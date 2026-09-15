from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.version_timestamp import VersionTimestamp


T = TypeVar("T", bound="VersionGitCommit")


@_attrs_define
class VersionGitCommit:
    """
    Attributes:
        id (str | Unset):
        timestamp (VersionTimestamp | Unset):
    """

    id: str | Unset = UNSET
    timestamp: VersionTimestamp | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        timestamp: dict[str, Any] | Unset = UNSET
        if not isinstance(self.timestamp, Unset):
            timestamp = self.timestamp.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.version_timestamp import VersionTimestamp

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _timestamp = d.pop("timestamp", UNSET)
        timestamp: VersionTimestamp | Unset
        if isinstance(_timestamp, Unset):
            timestamp = UNSET
        else:
            timestamp = VersionTimestamp.from_dict(_timestamp)

        version_git_commit = cls(
            id=id,
            timestamp=timestamp,
        )

        version_git_commit.additional_properties = d
        return version_git_commit

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
