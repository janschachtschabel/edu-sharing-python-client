from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.shortcut_config_entry import ShortcutConfigEntry


T = TypeVar("T", bound="ShortcutConfig")


@_attrs_define
class ShortcutConfig:
    """
    Attributes:
        enabled (bool | Unset):
        max_entries (int | Unset):
        entries (list[ShortcutConfigEntry] | Unset):
    """

    enabled: bool | Unset = UNSET
    max_entries: int | Unset = UNSET
    entries: list[ShortcutConfigEntry] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        max_entries = self.max_entries

        entries: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.entries, Unset):
            entries = []
            for entries_item_data in self.entries:
                entries_item = entries_item_data.to_dict()
                entries.append(entries_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if max_entries is not UNSET:
            field_dict["maxEntries"] = max_entries
        if entries is not UNSET:
            field_dict["entries"] = entries

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.shortcut_config_entry import ShortcutConfigEntry

        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        max_entries = d.pop("maxEntries", UNSET)

        _entries = d.pop("entries", UNSET)
        entries: list[ShortcutConfigEntry] | Unset = UNSET
        if _entries is not UNSET:
            entries = []
            for entries_item_data in _entries:
                entries_item = ShortcutConfigEntry.from_dict(entries_item_data)

                entries.append(entries_item)

        shortcut_config = cls(
            enabled=enabled,
            max_entries=max_entries,
            entries=entries,
        )

        shortcut_config.additional_properties = d
        return shortcut_config

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
