from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.tool_permission_effective import ToolPermissionEffective
from ..models.tool_permission_explicit import ToolPermissionExplicit
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.group import Group


T = TypeVar("T", bound="ToolPermission")


@_attrs_define
class ToolPermission:
    """
    Attributes:
        explicit (ToolPermissionExplicit | Unset):
        effective (ToolPermissionEffective | Unset):
        effective_source (list[Group] | Unset):
        system_managed (bool | Unset):
    """

    explicit: ToolPermissionExplicit | Unset = UNSET
    effective: ToolPermissionEffective | Unset = UNSET
    effective_source: list[Group] | Unset = UNSET
    system_managed: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        explicit: str | Unset = UNSET
        if not isinstance(self.explicit, Unset):
            explicit = self.explicit.value

        effective: str | Unset = UNSET
        if not isinstance(self.effective, Unset):
            effective = self.effective.value

        effective_source: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.effective_source, Unset):
            effective_source = []
            for effective_source_item_data in self.effective_source:
                effective_source_item = effective_source_item_data.to_dict()
                effective_source.append(effective_source_item)

        system_managed = self.system_managed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if explicit is not UNSET:
            field_dict["explicit"] = explicit
        if effective is not UNSET:
            field_dict["effective"] = effective
        if effective_source is not UNSET:
            field_dict["effectiveSource"] = effective_source
        if system_managed is not UNSET:
            field_dict["systemManaged"] = system_managed

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.group import Group

        d = dict(src_dict)
        _explicit = d.pop("explicit", UNSET)
        explicit: ToolPermissionExplicit | Unset
        if isinstance(_explicit, Unset):
            explicit = UNSET
        else:
            explicit = ToolPermissionExplicit(_explicit)

        _effective = d.pop("effective", UNSET)
        effective: ToolPermissionEffective | Unset
        if isinstance(_effective, Unset):
            effective = UNSET
        else:
            effective = ToolPermissionEffective(_effective)

        _effective_source = d.pop("effectiveSource", UNSET)
        effective_source: list[Group] | Unset = UNSET
        if _effective_source is not UNSET:
            effective_source = []
            for effective_source_item_data in _effective_source:
                effective_source_item = Group.from_dict(effective_source_item_data)

                effective_source.append(effective_source_item)

        system_managed = d.pop("systemManaged", UNSET)

        tool_permission = cls(
            explicit=explicit,
            effective=effective,
            effective_source=effective_source,
            system_managed=system_managed,
        )

        tool_permission.additional_properties = d
        return tool_permission

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
