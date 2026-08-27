from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_stats_total import NodeStatsTotal


T = TypeVar("T", bound="NodeStats")


@_attrs_define
class NodeStats:
    """
    Attributes:
        total (NodeStatsTotal | Unset):
    """

    total: NodeStatsTotal | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        total: dict[str, Any] | Unset = UNSET
        if not isinstance(self.total, Unset):
            total = self.total.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if total is not UNSET:
            field_dict["total"] = total

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node_stats_total import NodeStatsTotal

        d = dict(src_dict)
        _total = d.pop("total", UNSET)
        total: NodeStatsTotal | Unset
        if isinstance(_total, Unset):
            total = UNSET
        else:
            total = NodeStatsTotal.from_dict(_total)

        node_stats = cls(
            total=total,
        )

        node_stats.additional_properties = d
        return node_stats

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
