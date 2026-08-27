from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.get_cache_entries_response_200_additional_property import (
        GetCacheEntriesResponse200AdditionalProperty,
    )


T = TypeVar("T", bound="GetCacheEntriesResponse200")


@_attrs_define
class GetCacheEntriesResponse200:
    """ """

    additional_properties: dict[str, GetCacheEntriesResponse200AdditionalProperty] = _attrs_field(
        init=False, factory=dict
    )

    def to_dict(self) -> dict[str, Any]:

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.get_cache_entries_response_200_additional_property import (
            GetCacheEntriesResponse200AdditionalProperty,
        )

        d = dict(src_dict)
        get_cache_entries_response_200 = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = GetCacheEntriesResponse200AdditionalProperty.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        get_cache_entries_response_200.additional_properties = additional_properties
        return get_cache_entries_response_200

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> GetCacheEntriesResponse200AdditionalProperty:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: GetCacheEntriesResponse200AdditionalProperty) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
