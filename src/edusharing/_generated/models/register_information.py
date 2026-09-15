from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RegisterInformation")


@_attrs_define
class RegisterInformation:
    """
    Attributes:
        vcard (str | Unset):
        first_name (str | Unset):
        last_name (str | Unset):
        email (str | Unset):
        password (str | Unset):
        organization (str | Unset):
        allow_notifications (bool | Unset):
        authority_name (str | Unset):
    """

    vcard: str | Unset = UNSET
    first_name: str | Unset = UNSET
    last_name: str | Unset = UNSET
    email: str | Unset = UNSET
    password: str | Unset = UNSET
    organization: str | Unset = UNSET
    allow_notifications: bool | Unset = UNSET
    authority_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        vcard = self.vcard

        first_name = self.first_name

        last_name = self.last_name

        email = self.email

        password = self.password

        organization = self.organization

        allow_notifications = self.allow_notifications

        authority_name = self.authority_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if vcard is not UNSET:
            field_dict["vcard"] = vcard
        if first_name is not UNSET:
            field_dict["firstName"] = first_name
        if last_name is not UNSET:
            field_dict["lastName"] = last_name
        if email is not UNSET:
            field_dict["email"] = email
        if password is not UNSET:
            field_dict["password"] = password
        if organization is not UNSET:
            field_dict["organization"] = organization
        if allow_notifications is not UNSET:
            field_dict["allowNotifications"] = allow_notifications
        if authority_name is not UNSET:
            field_dict["authorityName"] = authority_name

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        vcard = d.pop("vcard", UNSET)

        first_name = d.pop("firstName", UNSET)

        last_name = d.pop("lastName", UNSET)

        email = d.pop("email", UNSET)

        password = d.pop("password", UNSET)

        organization = d.pop("organization", UNSET)

        allow_notifications = d.pop("allowNotifications", UNSET)

        authority_name = d.pop("authorityName", UNSET)

        register_information = cls(
            vcard=vcard,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            organization=organization,
            allow_notifications=allow_notifications,
            authority_name=authority_name,
        )

        register_information.additional_properties = d
        return register_information

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
