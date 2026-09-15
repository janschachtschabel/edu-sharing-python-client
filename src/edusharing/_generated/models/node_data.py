from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_data_counts import NodeDataCounts


T = TypeVar("T", bound="NodeData")


@_attrs_define
class NodeData:
    """
    Attributes:
        timestamp (str | Unset):
        counts (NodeDataCounts | Unset):
    """

    timestamp: str | Unset = UNSET
    counts: NodeDataCounts | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        timestamp = self.timestamp

        counts: dict[str, Any] | Unset = UNSET
        if not isinstance(self.counts, Unset):
            counts = self.counts.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp
        if counts is not UNSET:
            field_dict["counts"] = counts

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node_data_counts import NodeDataCounts

        d = dict(src_dict)
        timestamp = d.pop("timestamp", UNSET)

        _counts = d.pop("counts", UNSET)
        counts: NodeDataCounts | Unset
        if isinstance(_counts, Unset):
            counts = UNSET
        else:
            counts = NodeDataCounts.from_dict(_counts)

        node_data = cls(
            timestamp=timestamp,
            counts=counts,
        )

        node_data.additional_properties = d
        return node_data

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
