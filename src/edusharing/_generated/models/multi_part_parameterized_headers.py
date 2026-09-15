from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.parameterized_header import ParameterizedHeader


T = TypeVar("T", bound="MultiPartParameterizedHeaders")


@_attrs_define
class MultiPartParameterizedHeaders:
    """
    Attributes:
        empty (bool | Unset):
    """

    empty: bool | Unset = UNSET
    additional_properties: dict[str, list[ParameterizedHeader]] = _attrs_field(
        init=False, factory=dict
    )

    def to_dict(self) -> dict[str, Any]:
        empty = self.empty

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = []
            for additional_property_item_data in prop:
                additional_property_item = additional_property_item_data.to_dict()
                field_dict[prop_name].append(additional_property_item)

        field_dict.update({})
        if empty is not UNSET:
            field_dict["empty"] = empty

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.parameterized_header import ParameterizedHeader

        d = dict(src_dict)
        empty = d.pop("empty", UNSET)

        multi_part_parameterized_headers = cls(
            empty=empty,
        )

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = []
            _additional_property = prop_dict
            for additional_property_item_data in _additional_property:
                additional_property_item = ParameterizedHeader.from_dict(
                    additional_property_item_data
                )

                additional_property.append(additional_property_item)

            additional_properties[prop_name] = additional_property

        multi_part_parameterized_headers.additional_properties = additional_properties
        return multi_part_parameterized_headers

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> list[ParameterizedHeader]:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: list[ParameterizedHeader]) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
