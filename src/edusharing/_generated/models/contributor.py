from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Contributor")


@_attrs_define
class Contributor:
    """Contributors (authors, publishers) for the node

    Attributes:
        property_ (str | Unset):
        firstname (str | Unset):
        lastname (str | Unset):
        email (str | Unset):
        vcard (str | Unset):
        org (str | Unset):
    """

    property_: str | Unset = UNSET
    firstname: str | Unset = UNSET
    lastname: str | Unset = UNSET
    email: str | Unset = UNSET
    vcard: str | Unset = UNSET
    org: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        property_ = self.property_

        firstname = self.firstname

        lastname = self.lastname

        email = self.email

        vcard = self.vcard

        org = self.org

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if property_ is not UNSET:
            field_dict["property"] = property_
        if firstname is not UNSET:
            field_dict["firstname"] = firstname
        if lastname is not UNSET:
            field_dict["lastname"] = lastname
        if email is not UNSET:
            field_dict["email"] = email
        if vcard is not UNSET:
            field_dict["vcard"] = vcard
        if org is not UNSET:
            field_dict["org"] = org

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        property_ = d.pop("property", UNSET)

        firstname = d.pop("firstname", UNSET)

        lastname = d.pop("lastname", UNSET)

        email = d.pop("email", UNSET)

        vcard = d.pop("vcard", UNSET)

        org = d.pop("org", UNSET)

        contributor = cls(
            property_=property_,
            firstname=firstname,
            lastname=lastname,
            email=email,
            vcard=vcard,
            org=org,
        )

        contributor.additional_properties = d
        return contributor

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
