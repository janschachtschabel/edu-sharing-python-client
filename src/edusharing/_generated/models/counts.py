from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.element import Element


T = TypeVar("T", bound="Counts")


@_attrs_define
class Counts:
    """
    Attributes:
        elements (list[Element] | Unset):
    """

    elements: list[Element] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        elements: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.elements, Unset):
            elements = []
            for elements_item_data in self.elements:
                elements_item = elements_item_data.to_dict()
                elements.append(elements_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if elements is not UNSET:
            field_dict["elements"] = elements

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.element import Element

        d = dict(src_dict)
        _elements = d.pop("elements", UNSET)
        elements: list[Element] | Unset = UNSET
        if _elements is not UNSET:
            elements = []
            for elements_item_data in _elements:
                elements_item = Element.from_dict(elements_item_data)

                elements.append(elements_item)

        counts = cls(
            elements=elements,
        )

        counts.additional_properties = d
        return counts

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
