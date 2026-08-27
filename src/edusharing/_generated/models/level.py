from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Level")


@_attrs_define
class Level:
    """
    Attributes:
        syslog_equivalent (int | Unset):
        version_2_level (Level | Unset):
    """

    syslog_equivalent: int | Unset = UNSET
    version_2_level: Level | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        syslog_equivalent = self.syslog_equivalent

        version_2_level: dict[str, Any] | Unset = UNSET
        if not isinstance(self.version_2_level, Unset):
            version_2_level = self.version_2_level.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if syslog_equivalent is not UNSET:
            field_dict["syslogEquivalent"] = syslog_equivalent
        if version_2_level is not UNSET:
            field_dict["version2Level"] = version_2_level

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        syslog_equivalent = d.pop("syslogEquivalent", UNSET)

        _version_2_level = d.pop("version2Level", UNSET)
        version_2_level: Level | Unset
        if isinstance(_version_2_level, Unset):
            version_2_level = UNSET
        else:
            version_2_level = Level.from_dict(_version_2_level)

        level = cls(
            syslog_equivalent=syslog_equivalent,
            version_2_level=version_2_level,
        )

        level.additional_properties = d
        return level

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
