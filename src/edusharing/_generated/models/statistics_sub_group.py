from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.sub_group_item import SubGroupItem


T = TypeVar("T", bound="StatisticsSubGroup")


@_attrs_define
class StatisticsSubGroup:
    """
    Attributes:
        id (str | Unset):
        count (list[SubGroupItem] | Unset):
    """

    id: str | Unset = UNSET
    count: list[SubGroupItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        count: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.count, Unset):
            count = []
            for count_item_data in self.count:
                count_item = count_item_data.to_dict()
                count.append(count_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if count is not UNSET:
            field_dict["count"] = count

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.sub_group_item import SubGroupItem

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _count = d.pop("count", UNSET)
        count: list[SubGroupItem] | Unset = UNSET
        if _count is not UNSET:
            count = []
            for count_item_data in _count:
                count_item = SubGroupItem.from_dict(count_item_data)

                count.append(count_item)

        statistics_sub_group = cls(
            id=id,
            count=count,
        )

        statistics_sub_group.additional_properties = d
        return statistics_sub_group

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
