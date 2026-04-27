import glob
import os
import re
import sys
import tempfile

import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn
from rich.table import Table
from rich.tree import Tree

try:
    from modelkit.assets.drivers.gcs import GCSStorageDriver, GCSStorageDriverSettings

    has_gcs = True
except ModuleNotFoundError:
    has_gcs = False
try:
    from modelkit.assets.drivers.s3 import S3StorageDriver, S3StorageDriverSettings

    has_s3 = True
except ModuleNotFoundError:
    has_s3 = False
from modelkit.assets.errors import ObjectDoesNotExistError
from modelkit.assets.manager import AssetsManager
from modelkit.assets.remote import DriverNotInstalledError, StorageProvider
from modelkit.assets.settings import AssetSpec


@click.group("assets")
def assets_cli():
    """
    Assets management commands
    """
    pass


storage_url_re = (
    r"(?P<storage_prefix>[\w]*)://(?P<bucket_name>[\w\-]+)/(?P<object_name>.+)"
)


def parse_remote_url(path):
    pass


def _download_object_or_prefix(driver, object_name, destination_dir):
    pass


def _check_asset_file_number(asset_path):
    pass


@assets_cli.command("new")
@click.argument("asset_path")
@click.argument("asset_spec")
@click.option("--storage-prefix", envvar="MODELKIT_STORAGE_PREFIX")
@click.option("--dry-run", is_flag=True)
def new(asset_path, asset_spec, storage_prefix, dry_run):
    """
    Create a new asset.

    Create a new asset ASSET_SPEC with ASSET_PATH file.

    Will fail if asset exists (in this case use `update`).

    ASSET_PATH is the path to the file. The file can be local or on GCS
    (starting with gs://)

    ASSET_SPEC is and asset specification of the form
    [asset_name] (Major/minor version information is ignored)

    NB: [asset_name] can contain `/` too.
    """
    pass


def new_(asset_path, asset_spec, storage_prefix, dry_run):
    pass


@assets_cli.command("update")
@click.argument("asset_path")
@click.argument("asset_spec")
@click.option(
    "--bump-major",
    is_flag=True,
    help="[minor-major] Push a new major version (1.0, 2.0, etc.)",
)
@click.option("--storage-prefix", envvar="MODELKIT_STORAGE_PREFIX")
@click.option("--dry-run", is_flag=True)
def update(asset_path, asset_spec, storage_prefix, bump_major, dry_run):
    """
    Update an existing asset using versioning system
    set in MODELKIT_ASSETS_VERSIONING_SYSTEM (major/minor by default)

    Update an existing asset ASSET_SPEC with ASSET_PATH file.


    By default will upload a new minor version.

    ASSET_PATH is the path to the file. The file can be local remote (AWS or GCS)
    (starting with gs:// or s3://)

    ASSET_SPEC is and asset specification of the form
    [asset_name]:[version]

    Specific documentation depends on the choosen model
    """
    pass


def update_(asset_path, asset_spec, storage_prefix, bump_major, dry_run):
    pass


@assets_cli.command("list")
@click.option("--storage-prefix", envvar="MODELKIT_STORAGE_PREFIX")
def list(storage_prefix):
    """lists all available assets and their versions."""
    pass


@assets_cli.command("fetch")
@click.argument("asset")
@click.option("--download", is_flag=True)
def fetch_asset(asset, download):
    """Fetch an asset and download if necessary"""
    manager = AssetsManager()

    info = manager.fetch_asset(asset, return_info=True, force_download=download)

    console = Console()
    console.print(info)
