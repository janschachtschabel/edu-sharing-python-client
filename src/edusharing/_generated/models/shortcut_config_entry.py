from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.shortcut_config_entry_default_visibility import ShortcutConfigEntryDefaultVisibility
from ..types import UNSET, Unset

T = TypeVar("T", bound="ShortcutConfigEntry")


@_attrs_define
class ShortcutConfigEntry:
    """
    Attributes:
        id (str | Unset):
        icon (str | Unset):
        url (str | Unset):
        tool_permission (str | Unset):
        default_visibility (ShortcutConfigEntryDefaultVisibility | Unset):
    """

    id: str | Unset = UNSET
    icon: str | Unset = UNSET
    url: str | Unset = UNSET
    tool_permission: str | Unset = UNSET
    default_visibility: ShortcutConfigEntryDefaultVisibility | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        icon = self.icon

        url = self.url

        tool_permission = self.tool_permission

        default_visibility: str | Unset = UNSET
        if not isinstance(self.default_visibility, Unset):
            default_visibility = self.default_visibility.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if icon is not UNSET:
            field_dict["icon"] = icon
        if url is not UNSET:
            field_dict["url"] = url
        if tool_permission is not UNSET:
            field_dict["toolPermission"] = tool_permission
        if default_visibility is not UNSET:
            field_dict["defaultVisibility"] = default_visibility

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        icon = d.pop("icon", UNSET)

        url = d.pop("url", UNSET)

        tool_permission = d.pop("toolPermission", UNSET)

        _default_visibility = d.pop("defaultVisibility", UNSET)
        default_visibility: ShortcutConfigEntryDefaultVisibility | Unset
        if isinstance(_default_visibility, Unset):
            default_visibility = UNSET
        else:
            default_visibility = ShortcutConfigEntryDefaultVisibility(_default_visibility)

        shortcut_config_entry = cls(
            id=id,
            icon=icon,
            url=url,
            tool_permission=tool_permission,
            default_visibility=default_visibility,
        )

        shortcut_config_entry.additional_properties = d
        return shortcut_config_entry

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
