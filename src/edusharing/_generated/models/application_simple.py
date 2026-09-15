from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ApplicationSimple")


@_attrs_define
class ApplicationSimple:
    """
    Attributes:
        id (str | Unset):
        title (str | Unset):
        type_ (str | Unset):
        subtype (str | Unset):
        host (str | Unset):
        domain (str | Unset):
        allowed_origins (list[str] | Unset):
    """

    id: str | Unset = UNSET
    title: str | Unset = UNSET
    type_: str | Unset = UNSET
    subtype: str | Unset = UNSET
    host: str | Unset = UNSET
    domain: str | Unset = UNSET
    allowed_origins: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        type_ = self.type_

        subtype = self.subtype

        host = self.host

        domain = self.domain

        allowed_origins: list[str] | Unset = UNSET
        if not isinstance(self.allowed_origins, Unset):
            allowed_origins = self.allowed_origins

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if title is not UNSET:
            field_dict["title"] = title
        if type_ is not UNSET:
            field_dict["type"] = type_
        if subtype is not UNSET:
            field_dict["subtype"] = subtype
        if host is not UNSET:
            field_dict["host"] = host
        if domain is not UNSET:
            field_dict["domain"] = domain
        if allowed_origins is not UNSET:
            field_dict["allowedOrigins"] = allowed_origins

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        title = d.pop("title", UNSET)

        type_ = d.pop("type", UNSET)

        subtype = d.pop("subtype", UNSET)

        host = d.pop("host", UNSET)

        domain = d.pop("domain", UNSET)

        allowed_origins = cast(list[str], d.pop("allowedOrigins", UNSET))

        application_simple = cls(
            id=id,
            title=title,
            type_=type_,
            subtype=subtype,
            host=host,
            domain=domain,
            allowed_origins=allowed_origins,
        )

        application_simple.additional_properties = d
        return application_simple

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
