from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.provider_area_served import ProviderAreaServed
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.location import Location


T = TypeVar("T", bound="Provider")


@_attrs_define
class Provider:
    """
    Attributes:
        legal_name (str | Unset):
        url (str | Unset):
        email (str | Unset):
        area_served (ProviderAreaServed | Unset):
        location (Location | Unset):
    """

    legal_name: str | Unset = UNSET
    url: str | Unset = UNSET
    email: str | Unset = UNSET
    area_served: ProviderAreaServed | Unset = UNSET
    location: Location | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        legal_name = self.legal_name

        url = self.url

        email = self.email

        area_served: str | Unset = UNSET
        if not isinstance(self.area_served, Unset):
            area_served = self.area_served.value

        location: dict[str, Any] | Unset = UNSET
        if not isinstance(self.location, Unset):
            location = self.location.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if legal_name is not UNSET:
            field_dict["legalName"] = legal_name
        if url is not UNSET:
            field_dict["url"] = url
        if email is not UNSET:
            field_dict["email"] = email
        if area_served is not UNSET:
            field_dict["areaServed"] = area_served
        if location is not UNSET:
            field_dict["location"] = location

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.location import Location

        d = dict(src_dict)
        legal_name = d.pop("legalName", UNSET)

        url = d.pop("url", UNSET)

        email = d.pop("email", UNSET)

        _area_served = d.pop("areaServed", UNSET)
        area_served: ProviderAreaServed | Unset
        if isinstance(_area_served, Unset):
            area_served = UNSET
        else:
            area_served = ProviderAreaServed(_area_served)

        _location = d.pop("location", UNSET)
        location: Location | Unset
        if isinstance(_location, Unset):
            location = UNSET
        else:
            location = Location.from_dict(_location)

        provider = cls(
            legal_name=legal_name,
            url=url,
            email=email,
            area_served=area_served,
            location=location,
        )

        provider.additional_properties = d
        return provider

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
