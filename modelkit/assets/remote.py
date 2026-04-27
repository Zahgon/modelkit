import datetime
import glob
import json
import os
import tempfile
import time
from typing import Any, Optional

import humanize
from dateutil import parser, tz
from structlog import get_logger

from modelkit.assets import errors
from modelkit.assets.drivers.abc import StorageDriver

try:
    from modelkit.assets.drivers.azure import (
        AzureStorageDriver,
        AzureStorageDriverSettings,
    )

    has_az = True
except ModuleNotFoundError:
    has_az = False
try:
    from modelkit.assets.drivers.gcs import GCSStorageDriver, GCSStorageDriverSettings

    has_gcs = True
except ModuleNotFoundError:
    has_gcs = False
from modelkit.assets.drivers.local import LocalStorageDriver, LocalStorageDriverSettings

try:
    from modelkit.assets.drivers.s3 import S3StorageDriver, S3StorageDriverSettings

    has_s3 = True
except ModuleNotFoundError:
    has_s3 = False
from modelkit.assets.settings import AssetSpec
from modelkit.utils.logging import ContextualizedLogging

logger = get_logger(__name__)


def get_size(dir_path):
    if os.path.isfile(dir_path):
        return os.stat(dir_path).st_size
    return sum(
        os.stat(f).st_size
        for f in glob.iglob(os.path.join(dir_path, "**/*"), recursive=True)
        if os.path.isfile(f)
    )


class UnknownDriverError(Exception):
    pass


class DriverNotInstalledError(Exception):
    pass


class NoConfiguredProviderError(Exception):
    pass


class StorageProvider:
    driver: StorageDriver
    force_download: bool
    prefix: str
    timeout: int

    def __init__(
        self,
        timeout_s: Optional[int] = None,
        prefix: Optional[str] = None,
        force_download: Optional[bool] = None,
        provider: Optional[str] = None,
        client: Optional[Any] = None,
        **driver_settings,
    ):
        self.timeout = timeout_s or int(
            os.environ.get("MODELKIT_STORAGE_TIMEOUT_S", 300)
        )
        self.prefix = (
            prefix or os.environ.get("MODELKIT_STORAGE_PREFIX") or "modelkit-assets"
        )
        self.force_download = force_download or bool(
            os.environ.get("MODELKIT_STORAGE_FORCE_DOWNLOAD")
        )

        provider = provider or os.environ.get("MODELKIT_STORAGE_PROVIDER")
        if not provider:
            raise NoConfiguredProviderError()

        if provider == "gcs":
            if not has_gcs:
                raise DriverNotInstalledError(
                    "GCS driver not installed, install modelkit[assets-gcs]"
                )
            gcs_driver_settings = GCSStorageDriverSettings(**driver_settings)
            self.driver = GCSStorageDriver(gcs_driver_settings, client)
        elif provider == "s3":
            if not has_s3:
                raise DriverNotInstalledError(
                    "S3 driver not installed, install modelkit[assets-s3]"
                )
            s3_driver_settings = S3StorageDriverSettings(**driver_settings)
            self.driver = S3StorageDriver(s3_driver_settings, client)
        elif provider == "local":
            local_driver_settings = LocalStorageDriverSettings(**driver_settings)
            self.driver = LocalStorageDriver(local_driver_settings)
        elif provider == "az":
            if not has_az:
                raise DriverNotInstalledError(
                    "Azure driver not installed, install modelkit[assets-az]"
                )
            az_driver_settings = AzureStorageDriverSettings(**driver_settings)
            self.driver = AzureStorageDriver(az_driver_settings, client)
        else:
            raise UnknownDriverError()

    def get_object_name(self, name, version):
        return "/".join((self.prefix, name, version))

    def get_meta_object_name(self, name, version):
        return self.get_object_name(name, version) + ".meta"

    def get_versions_object_name(self, name):
        return "/".join((self.prefix, name + ".versions"))

    def get_versions_info(self, name):
        """
        Retrieve asset versions information
        """
        versions_object_name = self.get_versions_object_name(name)
        with tempfile.TemporaryDirectory() as tmp_dir:
            versions_object_path = os.path.join(tmp_dir, name + ".version")
            os.makedirs(os.path.dirname(versions_object_path), exist_ok=True)
            self.driver.download_object(versions_object_name, versions_object_path)
            with open(versions_object_path) as f:
                versions_list = json.load(f)["versions"]
            return versions_list

    def get_asset_meta(self, name, version):
        """
        Retrieve asset metadata
        """
        meta_object_name = self.get_meta_object_name(name, version)
        with tempfile.TemporaryDirectory() as tempdir:
            fdst = os.path.join(tempdir, "meta.tmp")
            self.driver.download_object(meta_object_name, fdst)
            with open(fdst) as f:
                meta = json.load(f)
            meta["push_date"] = parser.isoparse(meta["push_date"])
        return meta

    def new(self, asset_path: str, name: str, version: str, dry_run=False):
        """
        Upload a new asset
        """
        pass

    def update(self, asset_path: str, name: str, version: str, dry_run=False):
        """
        Update an existing asset version
        """
        pass

    def push(self, asset_path, name, version, dry_run=False):
        """
        Push asset
        """
        pass

    def download(self, name, version, destination):
        """
        Retrieves the asset and returns a dictionary with meta information, asset
        origin (from cache) and local path
        """
        with ContextualizedLogging(name=name, version=version):
            destination_path = os.path.join(destination, *name.split("/"), version)
            object_name = self.get_object_name(name, version)
            meta = self.get_asset_meta(name, version)

            if meta.get("is_directory"):
                logger.info(
                    "Downloading remote multi-part asset",
                    n_parts=len(meta["contents"]),
                )
                t0 = time.monotonic()
                for part_no, part in enumerate(meta["contents"]):
                    current_destination_path = os.path.join(
                        destination_path, *part.split("/")
                    )
                    os.makedirs(
                        os.path.dirname(current_destination_path), exist_ok=True
                    )
                    remote_part_name = "/".join(
                        x for x in object_name.split("/") + part.split("/") if x
                    )
                    logger.debug(
                        "Downloading asset part",
                        part_no=part_no,
                        n_parts=len(meta["contents"]),
                    )
                    self.driver.download_object(
                        remote_part_name, current_destination_path
                    )
                    size = get_size(current_destination_path)
                    logger.debug(
                        "Downloaded asset part",
                        part_no=part_no,
                        n_parts=len(meta["contents"]),
                        size=humanize.naturalsize(size),
                        size_bytes=size,
                    )
                size = get_size(destination_path)
                logger.info(
                    "Downloaded remote multi-part asset",
                    size=humanize.naturalsize(size),
                    size_bytes=size,
                )
            else:
                logger.info("Downloading remote asset")
                t0 = time.monotonic()
                os.makedirs(os.path.dirname(destination_path), exist_ok=True)
                self.driver.download_object(object_name, destination_path)
                size = get_size(destination_path)
                download_time = time.monotonic() - t0
                logger.info(
                    "Downloaded asset",
                    size=humanize.naturalsize(size),
                    time=humanize.naturaldelta(
                        datetime.timedelta(seconds=download_time)
                    ),
                    time_seconds=download_time,
                    size_bytes=size,
                )
            # return
            return {"path": destination_path, "meta": meta}

    def iterate_assets(self):
        pass
