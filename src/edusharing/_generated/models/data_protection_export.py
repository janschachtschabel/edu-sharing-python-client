from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_entry import NodeEntry


T = TypeVar("T", bound="DataProtectionExport")


@_attrs_define
class DataProtectionExport:
    """
    Attributes:
        node_entry (NodeEntry | Unset):
    """

    node_entry: NodeEntry | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node_entry: dict[str, Any] | Unset = UNSET
        if not isinstance(self.node_entry, Unset):
            node_entry = self.node_entry.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if node_entry is not UNSET:
            field_dict["nodeEntry"] = node_entry

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node_entry import NodeEntry

        d = dict(src_dict)
        _node_entry = d.pop("nodeEntry", UNSET)
        node_entry: NodeEntry | Unset
        if isinstance(_node_entry, Unset):
            node_entry = UNSET
        else:
            node_entry = NodeEntry.from_dict(_node_entry)

        data_protection_export = cls(
            node_entry=node_entry,
        )

        data_protection_export.additional_properties = d
        return data_protection_export

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
