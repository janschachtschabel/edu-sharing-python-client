from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserQuota")


@_attrs_define
class UserQuota:
    """
    Attributes:
        enabled (bool | Unset):
        size_current (int | Unset):
        size_quota (int | Unset):
    """

    enabled: bool | Unset = UNSET
    size_current: int | Unset = UNSET
    size_quota: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        size_current = self.size_current

        size_quota = self.size_quota

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if size_current is not UNSET:
            field_dict["sizeCurrent"] = size_current
        if size_quota is not UNSET:
            field_dict["sizeQuota"] = size_quota

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        size_current = d.pop("sizeCurrent", UNSET)

        size_quota = d.pop("sizeQuota", UNSET)

        user_quota = cls(
            enabled=enabled,
            size_current=size_current,
            size_quota=size_quota,
        )

        user_quota.additional_properties = d
        return user_quota

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
