from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.version import Version
    from ..models.version_build import VersionBuild
    from ..models.version_git import VersionGit


T = TypeVar("T", bound="RepositoryVersionInfo")


@_attrs_define
class RepositoryVersionInfo:
    """
    Attributes:
        repository (str | Unset):
        version (Version | Unset):
        git (VersionGit | Unset):
        build (VersionBuild | Unset):
    """

    repository: str | Unset = UNSET
    version: Version | Unset = UNSET
    git: VersionGit | Unset = UNSET
    build: VersionBuild | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository = self.repository

        version: dict[str, Any] | Unset = UNSET
        if not isinstance(self.version, Unset):
            version = self.version.to_dict()

        git: dict[str, Any] | Unset = UNSET
        if not isinstance(self.git, Unset):
            git = self.git.to_dict()

        build: dict[str, Any] | Unset = UNSET
        if not isinstance(self.build, Unset):
            build = self.build.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if repository is not UNSET:
            field_dict["repository"] = repository
        if version is not UNSET:
            field_dict["version"] = version
        if git is not UNSET:
            field_dict["git"] = git
        if build is not UNSET:
            field_dict["build"] = build

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.version import Version
        from ..models.version_build import VersionBuild
        from ..models.version_git import VersionGit

        d = dict(src_dict)
        repository = d.pop("repository", UNSET)

        _version = d.pop("version", UNSET)
        version: Version | Unset
        if isinstance(_version, Unset):
            version = UNSET
        else:
            version = Version.from_dict(_version)

        _git = d.pop("git", UNSET)
        git: VersionGit | Unset
        if isinstance(_git, Unset):
            git = UNSET
        else:
            git = VersionGit.from_dict(_git)

        _build = d.pop("build", UNSET)
        build: VersionBuild | Unset
        if isinstance(_build, Unset):
            build = UNSET
        else:
            build = VersionBuild.from_dict(_build)

        repository_version_info = cls(
            repository=repository,
            version=version,
            git=git,
            build=build,
        )

        repository_version_info.additional_properties = d
        return repository_version_info

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
