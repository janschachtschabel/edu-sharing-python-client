from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="GetByNodeIdsRequest")


@_attrs_define
class GetByNodeIdsRequest:
    """
    Attributes:
        node_ids (list[str] | Unset):
        properties (list[list[str]] | Unset):
    """

    node_ids: list[str] | Unset = UNSET
    properties: list[list[str]] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node_ids: list[str] | Unset = UNSET
        if not isinstance(self.node_ids, Unset):
            node_ids = self.node_ids

        properties: list[list[str]] | Unset = UNSET
        if not isinstance(self.properties, Unset):
            properties = []
            for properties_item_data in self.properties:
                properties_item = properties_item_data

                properties.append(properties_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if node_ids is not UNSET:
            field_dict["nodeIds"] = node_ids
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        node_ids = cast(list[str], d.pop("nodeIds", UNSET))

        _properties = d.pop("properties", UNSET)
        properties: list[list[str]] | Unset = UNSET
        if _properties is not UNSET:
            properties = []
            for properties_item_data in _properties:
                properties_item = cast(list[str], properties_item_data)

                properties.append(properties_item)

        get_by_node_ids_request = cls(
            node_ids=node_ids,
            properties=properties,
        )

        get_by_node_ids_request.additional_properties = d
        return get_by_node_ids_request

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
