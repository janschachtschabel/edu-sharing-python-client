from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OAuthEntry")


@_attrs_define
class OAuthEntry:
    """
    Attributes:
        name (str | Unset):
        registration_id (str | Unset):
        client_id (str | Unset):
        allow_third_party_login_plugin (bool | Unset):
    """

    name: str | Unset = UNSET
    registration_id: str | Unset = UNSET
    client_id: str | Unset = UNSET
    allow_third_party_login_plugin: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        registration_id = self.registration_id

        client_id = self.client_id

        allow_third_party_login_plugin = self.allow_third_party_login_plugin

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if registration_id is not UNSET:
            field_dict["registrationId"] = registration_id
        if client_id is not UNSET:
            field_dict["clientId"] = client_id
        if allow_third_party_login_plugin is not UNSET:
            field_dict["allowThirdPartyLoginPlugin"] = allow_third_party_login_plugin

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        registration_id = d.pop("registrationId", UNSET)

        client_id = d.pop("clientId", UNSET)

        allow_third_party_login_plugin = d.pop("allowThirdPartyLoginPlugin", UNSET)

        o_auth_entry = cls(
            name=name,
            registration_id=registration_id,
            client_id=client_id,
            allow_third_party_login_plugin=allow_third_party_login_plugin,
        )

        o_auth_entry.additional_properties = d
        return o_auth_entry

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
