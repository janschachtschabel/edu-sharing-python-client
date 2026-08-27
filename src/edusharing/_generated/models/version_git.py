from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.version_git_commit import VersionGitCommit


T = TypeVar("T", bound="VersionGit")


@_attrs_define
class VersionGit:
    """
    Attributes:
        branch (str | Unset):
        commit (VersionGitCommit | Unset):
    """

    branch: str | Unset = UNSET
    commit: VersionGitCommit | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        branch = self.branch

        commit: dict[str, Any] | Unset = UNSET
        if not isinstance(self.commit, Unset):
            commit = self.commit.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if branch is not UNSET:
            field_dict["branch"] = branch
        if commit is not UNSET:
            field_dict["commit"] = commit

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.version_git_commit import VersionGitCommit

        d = dict(src_dict)
        branch = d.pop("branch", UNSET)

        _commit = d.pop("commit", UNSET)
        commit: VersionGitCommit | Unset
        if isinstance(_commit, Unset):
            commit = UNSET
        else:
            commit = VersionGitCommit.from_dict(_commit)

        version_git = cls(
            branch=branch,
            commit=commit,
        )

        version_git.additional_properties = d
        return version_git

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
