from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.mds_widget_condition_type import MdsWidgetConditionType
from ..types import UNSET, Unset

T = TypeVar("T", bound="MdsWidgetCondition")


@_attrs_define
class MdsWidgetCondition:
    """
    Attributes:
        type_ (MdsWidgetConditionType):
        value (str):
        negate (bool):
        dynamic (bool):
        pattern (str | Unset):
    """

    type_: MdsWidgetConditionType
    value: str
    negate: bool
    dynamic: bool
    pattern: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        value = self.value

        negate = self.negate

        dynamic = self.dynamic

        pattern = self.pattern

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "value": value,
                "negate": negate,
                "dynamic": dynamic,
            }
        )
        if pattern is not UNSET:
            field_dict["pattern"] = pattern

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        type_ = MdsWidgetConditionType(d.pop("type"))

        value = d.pop("value")

        negate = d.pop("negate")

        dynamic = d.pop("dynamic")

        pattern = d.pop("pattern", UNSET)

        mds_widget_condition = cls(
            type_=type_,
            value=value,
            negate=negate,
            dynamic=dynamic,
            pattern=pattern,
        )

        mds_widget_condition.additional_properties = d
        return mds_widget_condition

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
