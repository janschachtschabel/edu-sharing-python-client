from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Register")


@_attrs_define
class Register:
    """Registration settings (local service, custom URLs, password recovery, required fields)

    Attributes:
        local (bool | Unset): Whether local registration service is active (default: true)
        recover_password (bool | Unset): Whether local password recovery function is active
        login_url (str | Unset): URL to custom registration page (used if local=false)
        recover_url (str | Unset): URL to custom password recovery page (used if local=false)
        recover_url_safe (str | Unset): Safe/alternative URL for password recovery
        required_fields (list[str] | Unset): Required registration fields: firstName, lastName, organization
    """

    local: bool | Unset = UNSET
    recover_password: bool | Unset = UNSET
    login_url: str | Unset = UNSET
    recover_url: str | Unset = UNSET
    recover_url_safe: str | Unset = UNSET
    required_fields: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        local = self.local

        recover_password = self.recover_password

        login_url = self.login_url

        recover_url = self.recover_url

        recover_url_safe = self.recover_url_safe

        required_fields: list[str] | Unset = UNSET
        if not isinstance(self.required_fields, Unset):
            required_fields = self.required_fields

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if local is not UNSET:
            field_dict["local"] = local
        if recover_password is not UNSET:
            field_dict["recoverPassword"] = recover_password
        if login_url is not UNSET:
            field_dict["loginUrl"] = login_url
        if recover_url is not UNSET:
            field_dict["recoverUrl"] = recover_url
        if recover_url_safe is not UNSET:
            field_dict["recoverUrlSafe"] = recover_url_safe
        if required_fields is not UNSET:
            field_dict["requiredFields"] = required_fields

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        local = d.pop("local", UNSET)

        recover_password = d.pop("recoverPassword", UNSET)

        login_url = d.pop("loginUrl", UNSET)

        recover_url = d.pop("recoverUrl", UNSET)

        recover_url_safe = d.pop("recoverUrlSafe", UNSET)

        required_fields = cast(list[str], d.pop("requiredFields", UNSET))

        register = cls(
            local=local,
            recover_password=recover_password,
            login_url=login_url,
            recover_url=recover_url,
            recover_url_safe=recover_url_safe,
            required_fields=required_fields,
        )

        register.additional_properties = d
        return register

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
