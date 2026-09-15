from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.node import Node


T = TypeVar("T", bound="RenderingDetailsEntry")


@_attrs_define
class RenderingDetailsEntry:
    """
    Attributes:
        details_snippet (str):
        mime_type (str):
        node (Node):
    """

    details_snippet: str
    mime_type: str
    node: Node
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        details_snippet = self.details_snippet

        mime_type = self.mime_type

        node = self.node.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "detailsSnippet": details_snippet,
                "mimeType": mime_type,
                "node": node,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node import Node

        d = dict(src_dict)
        details_snippet = d.pop("detailsSnippet")

        mime_type = d.pop("mimeType")

        node = Node.from_dict(d.pop("node"))

        rendering_details_entry = cls(
            details_snippet=details_snippet,
            mime_type=mime_type,
            node=node,
        )

        rendering_details_entry.additional_properties = d
        return rendering_details_entry

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
