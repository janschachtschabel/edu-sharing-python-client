from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.value import Value


T = TypeVar("T", bound="Facet")


@_attrs_define
class Facet:
    """
    Attributes:
        property_ (str):
        values (list[Value]):
        sum_other_doc_count (int | Unset):
    """

    property_: str
    values: list[Value]
    sum_other_doc_count: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        property_ = self.property_

        values = []
        for values_item_data in self.values:
            values_item = values_item_data.to_dict()
            values.append(values_item)

        sum_other_doc_count = self.sum_other_doc_count

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "property": property_,
                "values": values,
            }
        )
        if sum_other_doc_count is not UNSET:
            field_dict["sumOtherDocCount"] = sum_other_doc_count

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.value import Value

        d = dict(src_dict)
        property_ = d.pop("property")

        values = []
        _values = d.pop("values")
        for values_item_data in _values:
            values_item = Value.from_dict(values_item_data)

            values.append(values_item)

        sum_other_doc_count = d.pop("sumOtherDocCount", UNSET)

        facet = cls(
            property_=property_,
            values=values,
            sum_other_doc_count=sum_other_doc_count,
        )

        facet.additional_properties = d
        return facet

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
