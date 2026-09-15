from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UserStatsGroup")


@_attrs_define
class UserStatsGroup:
    """
    Attributes:
        node_count (int | Unset):
        node_count_oer (int | Unset):
        collection_count (int | Unset):
    """

    node_count: int | Unset = UNSET
    node_count_oer: int | Unset = UNSET
    collection_count: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        node_count = self.node_count

        node_count_oer = self.node_count_oer

        collection_count = self.collection_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if node_count is not UNSET:
            field_dict["nodeCount"] = node_count
        if node_count_oer is not UNSET:
            field_dict["nodeCountOER"] = node_count_oer
        if collection_count is not UNSET:
            field_dict["collectionCount"] = collection_count

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        node_count = d.pop("nodeCount", UNSET)

        node_count_oer = d.pop("nodeCountOER", UNSET)

        collection_count = d.pop("collectionCount", UNSET)

        user_stats_group = cls(
            node_count=node_count,
            node_count_oer=node_count_oer,
            collection_count=collection_count,
        )

        user_stats_group.additional_properties = d
        return user_stats_group

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
