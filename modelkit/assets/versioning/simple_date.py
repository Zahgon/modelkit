import datetime
import re
import typing

from modelkit.assets import errors
from modelkit.assets.versioning import versioning

DATE_RE = r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z$"


class SimpleDateAssetsVersioningSystem(versioning.AssetsVersioningSystem):
    @classmethod
    def get_initial_version(cls) -> str:
        pass

    @classmethod
    def check_version_valid(cls, version: str):
        if not re.fullmatch(DATE_RE, version):
            raise errors.InvalidVersionError(f"Invalid version `{version}`")

    @classmethod
    def sort_versions(cls, version_list: typing.Iterable[str]) -> typing.List[str]:
        return sorted(version_list, reverse=True)

    @classmethod
    def get_update_cli_params(cls, **kwargs) -> typing.Dict[str, typing.Any]:
        pass

    @classmethod
    def increment_version(
        cls,
        version_list: typing.Optional[typing.List[str]] = None,
        params: typing.Optional[typing.Dict[str, str]] = None,
    ) -> str:
        pass


def _utcnow() -> str:
    """string iso format in UTC"""
    pass
