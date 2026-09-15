from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Sort")


@_attrs_define
class Sort:
    """
    Attributes:
        sorted_ (bool | Unset):
        empty (bool | Unset):
        unsorted (bool | Unset):
    """

    sorted_: bool | Unset = UNSET
    empty: bool | Unset = UNSET
    unsorted: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        sorted_ = self.sorted_

        empty = self.empty

        unsorted = self.unsorted

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if sorted_ is not UNSET:
            field_dict["sorted"] = sorted_
        if empty is not UNSET:
            field_dict["empty"] = empty
        if unsorted is not UNSET:
            field_dict["unsorted"] = unsorted

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        sorted_ = d.pop("sorted", UNSET)

        empty = d.pop("empty", UNSET)

        unsorted = d.pop("unsorted", UNSET)

        sort = cls(
            sorted_=sorted_,
            empty=empty,
            unsorted=unsorted,
        )

        sort.additional_properties = d
        return sort

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
