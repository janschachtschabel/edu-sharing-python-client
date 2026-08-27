from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SimpleEditOrganization")


@_attrs_define
class SimpleEditOrganization:
    """Organization configuration for quick edit

    Attributes:
        group_types (list[str] | Unset): Group types to include
    """

    group_types: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        group_types: list[str] | Unset = UNSET
        if not isinstance(self.group_types, Unset):
            group_types = self.group_types

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if group_types is not UNSET:
            field_dict["groupTypes"] = group_types

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        group_types = cast(list[str], d.pop("groupTypes", UNSET))

        simple_edit_organization = cls(
            group_types=group_types,
        )

        simple_edit_organization.additional_properties = d
        return simple_edit_organization

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
