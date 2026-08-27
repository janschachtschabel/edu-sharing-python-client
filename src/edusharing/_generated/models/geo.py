from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Geo")


@_attrs_define
class Geo:
    """
    Attributes:
        longitude (float | Unset):
        latitude (float | Unset):
        address_country (str | Unset):
    """

    longitude: float | Unset = UNSET
    latitude: float | Unset = UNSET
    address_country: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        longitude = self.longitude

        latitude = self.latitude

        address_country = self.address_country

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if longitude is not UNSET:
            field_dict["longitude"] = longitude
        if latitude is not UNSET:
            field_dict["latitude"] = latitude
        if address_country is not UNSET:
            field_dict["addressCountry"] = address_country

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        longitude = d.pop("longitude", UNSET)

        latitude = d.pop("latitude", UNSET)

        address_country = d.pop("addressCountry", UNSET)

        geo = cls(
            longitude=longitude,
            latitude=latitude,
            address_country=address_country,
        )

        geo.additional_properties = d
        return geo

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
