from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.gdpr_entry import GdprEntry


T = TypeVar("T", bound="Gdpr")


@_attrs_define
class Gdpr:
    """GDPR configuration

    Attributes:
        enabled (bool | Unset): If true, enable GDPR-related features
        entry (list[GdprEntry] | Unset): GDPR entry definitions
    """

    enabled: bool | Unset = UNSET
    entry: list[GdprEntry] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        entry: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.entry, Unset):
            entry = []
            for entry_item_data in self.entry:
                entry_item = entry_item_data.to_dict()
                entry.append(entry_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if entry is not UNSET:
            field_dict["entry"] = entry

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.gdpr_entry import GdprEntry

        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        _entry = d.pop("entry", UNSET)
        entry: list[GdprEntry] | Unset = UNSET
        if _entry is not UNSET:
            entry = []
            for entry_item_data in _entry:
                entry_item = GdprEntry.from_dict(entry_item_data)

                entry.append(entry_item)

        gdpr = cls(
            enabled=enabled,
            entry=entry,
        )

        gdpr.additional_properties = d
        return gdpr

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
