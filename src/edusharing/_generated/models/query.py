from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.condition import Condition


T = TypeVar("T", bound="Query")


@_attrs_define
class Query:
    """
    Attributes:
        condition (Condition | Unset):
        query (str | Unset):
    """

    condition: Condition | Unset = UNSET
    query: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        condition: dict[str, Any] | Unset = UNSET
        if not isinstance(self.condition, Unset):
            condition = self.condition.to_dict()

        query = self.query

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if condition is not UNSET:
            field_dict["condition"] = condition
        if query is not UNSET:
            field_dict["query"] = query

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.condition import Condition

        d = dict(src_dict)
        _condition = d.pop("condition", UNSET)
        condition: Condition | Unset
        if isinstance(_condition, Unset):
            condition = UNSET
        else:
            condition = Condition.from_dict(_condition)

        query = d.pop("query", UNSET)

        query = cls(
            condition=condition,
            query=query,
        )

        query.additional_properties = d
        return query

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
