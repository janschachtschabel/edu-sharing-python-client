from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="SimpleEditGlobalGroups")


@_attrs_define
class SimpleEditGlobalGroups:
    """Global groups to offer in quick edit dialog

    Attributes:
        toolpermission (str | Unset): Tool permission required for this group entry (optional, applies to all if not
            set)
        groups (list[str] | Unset): Array of group IDs to offer in quick edit dialog
    """

    toolpermission: str | Unset = UNSET
    groups: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        toolpermission = self.toolpermission

        groups: list[str] | Unset = UNSET
        if not isinstance(self.groups, Unset):
            groups = self.groups

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if toolpermission is not UNSET:
            field_dict["toolpermission"] = toolpermission
        if groups is not UNSET:
            field_dict["groups"] = groups

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        toolpermission = d.pop("toolpermission", UNSET)

        groups = cast(list[str], d.pop("groups", UNSET))

        simple_edit_global_groups = cls(
            toolpermission=toolpermission,
            groups=groups,
        )

        simple_edit_global_groups.additional_properties = d
        return simple_edit_global_groups

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
