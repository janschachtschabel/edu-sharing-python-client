from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="StatisticsTemplate")


@_attrs_define
class StatisticsTemplate:
    """
    Attributes:
        name (str | Unset):
        group (str | Unset):
        unfold (str | Unset):
        type_ (str | Unset):
    """

    name: str | Unset = UNSET
    group: str | Unset = UNSET
    unfold: str | Unset = UNSET
    type_: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        group = self.group

        unfold = self.unfold

        type_ = self.type_

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if group is not UNSET:
            field_dict["group"] = group
        if unfold is not UNSET:
            field_dict["unfold"] = unfold
        if type_ is not UNSET:
            field_dict["type"] = type_

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        group = d.pop("group", UNSET)

        unfold = d.pop("unfold", UNSET)

        type_ = d.pop("type", UNSET)

        statistics_template = cls(
            name=name,
            group=group,
            unfold=unfold,
            type_=type_,
        )

        statistics_template.additional_properties = d
        return statistics_template

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
