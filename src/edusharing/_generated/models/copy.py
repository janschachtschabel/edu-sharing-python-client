from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.entry import Entry
    from ..models.node import Node


T = TypeVar("T", bound="Copy")


@_attrs_define
class Copy:
    """
    Attributes:
        root (Node | Unset):
        entries (list[Entry] | Unset):
    """

    root: Node | Unset = UNSET
    entries: list[Entry] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        root: dict[str, Any] | Unset = UNSET
        if not isinstance(self.root, Unset):
            root = self.root.to_dict()

        entries: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.entries, Unset):
            entries = []
            for entries_item_data in self.entries:
                entries_item = entries_item_data.to_dict()
                entries.append(entries_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if root is not UNSET:
            field_dict["root"] = root
        if entries is not UNSET:
            field_dict["entries"] = entries

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.entry import Entry
        from ..models.node import Node

        d = dict(src_dict)
        _root = d.pop("root", UNSET)
        root: Node | Unset
        if isinstance(_root, Unset):
            root = UNSET
        else:
            root = Node.from_dict(_root)

        _entries = d.pop("entries", UNSET)
        entries: list[Entry] | Unset = UNSET
        if _entries is not UNSET:
            entries = []
            for entries_item_data in _entries:
                entries_item = Entry.from_dict(entries_item_data)

                entries.append(entries_item)

        copy = cls(
            root=root,
            entries=entries,
        )

        copy.additional_properties = d
        return copy

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
