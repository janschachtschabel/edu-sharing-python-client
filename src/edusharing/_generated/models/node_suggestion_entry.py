from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node import Node
    from ..models.suggestion_node import SuggestionNode


T = TypeVar("T", bound="NodeSuggestionEntry")


@_attrs_define
class NodeSuggestionEntry:
    """
    Attributes:
        node (Node | Unset):
        suggestion_nodes (list[SuggestionNode] | Unset):
    """

    node: Node | Unset = UNSET
    suggestion_nodes: list[SuggestionNode] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node: dict[str, Any] | Unset = UNSET
        if not isinstance(self.node, Unset):
            node = self.node.to_dict()

        suggestion_nodes: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.suggestion_nodes, Unset):
            suggestion_nodes = []
            for suggestion_nodes_item_data in self.suggestion_nodes:
                suggestion_nodes_item = suggestion_nodes_item_data.to_dict()
                suggestion_nodes.append(suggestion_nodes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if node is not UNSET:
            field_dict["node"] = node
        if suggestion_nodes is not UNSET:
            field_dict["suggestionNodes"] = suggestion_nodes

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node import Node
        from ..models.suggestion_node import SuggestionNode

        d = dict(src_dict)
        _node = d.pop("node", UNSET)
        node: Node | Unset
        if isinstance(_node, Unset):
            node = UNSET
        else:
            node = Node.from_dict(_node)

        _suggestion_nodes = d.pop("suggestionNodes", UNSET)
        suggestion_nodes: list[SuggestionNode] | Unset = UNSET
        if _suggestion_nodes is not UNSET:
            suggestion_nodes = []
            for suggestion_nodes_item_data in _suggestion_nodes:
                suggestion_nodes_item = SuggestionNode.from_dict(suggestion_nodes_item_data)

                suggestion_nodes.append(suggestion_nodes_item)

        node_suggestion_entry = cls(
            node=node,
            suggestion_nodes=suggestion_nodes,
        )

        node_suggestion_entry.additional_properties = d
        return node_suggestion_entry

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
