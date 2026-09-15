from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.node_suggestion_response_dto_suggestions import (
        NodeSuggestionResponseDTOSuggestions,
    )


T = TypeVar("T", bound="NodeSuggestionResponseDTO")


@_attrs_define
class NodeSuggestionResponseDTO:
    """
    Attributes:
        node_id (str):
        suggestions (NodeSuggestionResponseDTOSuggestions):
    """

    node_id: str
    suggestions: NodeSuggestionResponseDTOSuggestions
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node_id = self.node_id

        suggestions = self.suggestions.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "nodeId": node_id,
                "suggestions": suggestions,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node_suggestion_response_dto_suggestions import (
            NodeSuggestionResponseDTOSuggestions,
        )

        d = dict(src_dict)
        node_id = d.pop("nodeId")

        suggestions = NodeSuggestionResponseDTOSuggestions.from_dict(d.pop("suggestions"))

        node_suggestion_response_dto = cls(
            node_id=node_id,
            suggestions=suggestions,
        )

        node_suggestion_response_dto.additional_properties = d
        return node_suggestion_response_dto

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
