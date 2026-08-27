from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.statistics_sub_group import StatisticsSubGroup


T = TypeVar("T", bound="StatisticsGroup")


@_attrs_define
class StatisticsGroup:
    """
    Attributes:
        count (int | Unset):
        sub_groups (list[StatisticsSubGroup] | Unset):
    """

    count: int | Unset = UNSET
    sub_groups: list[StatisticsSubGroup] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        count = self.count

        sub_groups: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.sub_groups, Unset):
            sub_groups = []
            for sub_groups_item_data in self.sub_groups:
                sub_groups_item = sub_groups_item_data.to_dict()
                sub_groups.append(sub_groups_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if count is not UNSET:
            field_dict["count"] = count
        if sub_groups is not UNSET:
            field_dict["subGroups"] = sub_groups

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.statistics_sub_group import StatisticsSubGroup

        d = dict(src_dict)
        count = d.pop("count", UNSET)

        _sub_groups = d.pop("subGroups", UNSET)
        sub_groups: list[StatisticsSubGroup] | Unset = UNSET
        if _sub_groups is not UNSET:
            sub_groups = []
            for sub_groups_item_data in _sub_groups:
                sub_groups_item = StatisticsSubGroup.from_dict(sub_groups_item_data)

                sub_groups.append(sub_groups_item)

        statistics_group = cls(
            count=count,
            sub_groups=sub_groups,
        )

        statistics_group.additional_properties = d
        return statistics_group

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
