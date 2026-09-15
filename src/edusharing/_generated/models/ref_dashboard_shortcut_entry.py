from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node import Node


T = TypeVar("T", bound="RefDashboardShortcutEntry")


@_attrs_define
class RefDashboardShortcutEntry:
    """
    Attributes:
        type_ (str):
        node (Node):
        title (str | Unset):
    """

    type_: str
    node: Node
    title: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        node = self.node.to_dict()

        title = self.title

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "node": node,
            }
        )
        if title is not UNSET:
            field_dict["title"] = title

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node import Node

        d = dict(src_dict)
        type_ = d.pop("type")

        node = Node.from_dict(d.pop("node"))

        title = d.pop("title", UNSET)

        ref_dashboard_shortcut_entry = cls(
            type_=type_,
            node=node,
            title=title,
        )

        ref_dashboard_shortcut_entry.additional_properties = d
        return ref_dashboard_shortcut_entry

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
