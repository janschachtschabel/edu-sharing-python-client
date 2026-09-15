from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.audience import Audience
    from ..models.interface import Interface
    from ..models.provider import Provider


T = TypeVar("T", bound="Service")


@_attrs_define
class Service:
    """
    Attributes:
        name (str | Unset):
        url (str | Unset):
        icon (str | Unset):
        logo (str | Unset):
        in_language (str | Unset):
        type_ (str | Unset):
        description (str | Unset):
        audience (list[Audience] | Unset):
        provider (Provider | Unset):
        start_date (str | Unset):
        interfaces (list[Interface] | Unset):
        about (list[str] | Unset):
        is_accessible_for_free (bool | Unset):
    """

    name: str | Unset = UNSET
    url: str | Unset = UNSET
    icon: str | Unset = UNSET
    logo: str | Unset = UNSET
    in_language: str | Unset = UNSET
    type_: str | Unset = UNSET
    description: str | Unset = UNSET
    audience: list[Audience] | Unset = UNSET
    provider: Provider | Unset = UNSET
    start_date: str | Unset = UNSET
    interfaces: list[Interface] | Unset = UNSET
    about: list[str] | Unset = UNSET
    is_accessible_for_free: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        url = self.url

        icon = self.icon

        logo = self.logo

        in_language = self.in_language

        type_ = self.type_

        description = self.description

        audience: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.audience, Unset):
            audience = []
            for audience_item_data in self.audience:
                audience_item = audience_item_data.to_dict()
                audience.append(audience_item)

        provider: dict[str, Any] | Unset = UNSET
        if not isinstance(self.provider, Unset):
            provider = self.provider.to_dict()

        start_date = self.start_date

        interfaces: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.interfaces, Unset):
            interfaces = []
            for interfaces_item_data in self.interfaces:
                interfaces_item = interfaces_item_data.to_dict()
                interfaces.append(interfaces_item)

        about: list[str] | Unset = UNSET
        if not isinstance(self.about, Unset):
            about = self.about

        is_accessible_for_free = self.is_accessible_for_free

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if url is not UNSET:
            field_dict["url"] = url
        if icon is not UNSET:
            field_dict["icon"] = icon
        if logo is not UNSET:
            field_dict["logo"] = logo
        if in_language is not UNSET:
            field_dict["inLanguage"] = in_language
        if type_ is not UNSET:
            field_dict["type"] = type_
        if description is not UNSET:
            field_dict["description"] = description
        if audience is not UNSET:
            field_dict["audience"] = audience
        if provider is not UNSET:
            field_dict["provider"] = provider
        if start_date is not UNSET:
            field_dict["startDate"] = start_date
        if interfaces is not UNSET:
            field_dict["interfaces"] = interfaces
        if about is not UNSET:
            field_dict["about"] = about
        if is_accessible_for_free is not UNSET:
            field_dict["isAccessibleForFree"] = is_accessible_for_free

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.audience import Audience
        from ..models.interface import Interface
        from ..models.provider import Provider

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        url = d.pop("url", UNSET)

        icon = d.pop("icon", UNSET)

        logo = d.pop("logo", UNSET)

        in_language = d.pop("inLanguage", UNSET)

        type_ = d.pop("type", UNSET)

        description = d.pop("description", UNSET)

        _audience = d.pop("audience", UNSET)
        audience: list[Audience] | Unset = UNSET
        if _audience is not UNSET:
            audience = []
            for audience_item_data in _audience:
                audience_item = Audience.from_dict(audience_item_data)

                audience.append(audience_item)

        _provider = d.pop("provider", UNSET)
        provider: Provider | Unset
        if isinstance(_provider, Unset):
            provider = UNSET
        else:
            provider = Provider.from_dict(_provider)

        start_date = d.pop("startDate", UNSET)

        _interfaces = d.pop("interfaces", UNSET)
        interfaces: list[Interface] | Unset = UNSET
        if _interfaces is not UNSET:
            interfaces = []
            for interfaces_item_data in _interfaces:
                interfaces_item = Interface.from_dict(interfaces_item_data)

                interfaces.append(interfaces_item)

        about = cast(list[str], d.pop("about", UNSET))

        is_accessible_for_free = d.pop("isAccessibleForFree", UNSET)

        service = cls(
            name=name,
            url=url,
            icon=icon,
            logo=logo,
            in_language=in_language,
            type_=type_,
            description=description,
            audience=audience,
            provider=provider,
            start_date=start_date,
            interfaces=interfaces,
            about=about,
            is_accessible_for_free=is_accessible_for_free,
        )

        service.additional_properties = d
        return service

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
