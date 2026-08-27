from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

T = TypeVar("T", bound="ValueParameters")


@_attrs_define
class ValueParameters:
    """
    Attributes:
        query (str):
        property_ (str):
        pattern (str): prefix of the value (or "-all-" for all values)
    """

    query: str
    property_: str
    pattern: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        query = self.query

        property_ = self.property_

        pattern = self.pattern

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "query": query,
                "property": property_,
                "pattern": pattern,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        query = d.pop("query")

        property_ = d.pop("property")

        pattern = d.pop("pattern")

        value_parameters = cls(
            query=query,
            property_=property_,
            pattern=pattern,
        )

        value_parameters.additional_properties = d
        return value_parameters

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
