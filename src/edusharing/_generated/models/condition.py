from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.condition_type import ConditionType
from ..types import UNSET, Unset

T = TypeVar("T", bound="Condition")


@_attrs_define
class Condition:
    """
    Attributes:
        type_ (ConditionType | Unset):
        negate (bool | Unset):
        value (str | Unset):
    """

    type_: ConditionType | Unset = UNSET
    negate: bool | Unset = UNSET
    value: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        negate = self.negate

        value = self.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if negate is not UNSET:
            field_dict["negate"] = negate
        if value is not UNSET:
            field_dict["value"] = value

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _type_ = d.pop("type", UNSET)
        type_: ConditionType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = ConditionType(_type_)

        negate = d.pop("negate", UNSET)

        value = d.pop("value", UNSET)

        condition = cls(
            type_=type_,
            negate=negate,
            value=value,
        )

        condition.additional_properties = d
        return condition

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
