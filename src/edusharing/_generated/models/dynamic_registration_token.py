from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="DynamicRegistrationToken")


@_attrs_define
class DynamicRegistrationToken:
    """
    Attributes:
        token (str | Unset):
        url (str | Unset):
        registered_app_id (str | Unset):
        ts_created (int | Unset):
        ts_expiry (int | Unset):
        valid (bool | Unset):
    """

    token: str | Unset = UNSET
    url: str | Unset = UNSET
    registered_app_id: str | Unset = UNSET
    ts_created: int | Unset = UNSET
    ts_expiry: int | Unset = UNSET
    valid: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        token = self.token

        url = self.url

        registered_app_id = self.registered_app_id

        ts_created = self.ts_created

        ts_expiry = self.ts_expiry

        valid = self.valid

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if token is not UNSET:
            field_dict["token"] = token
        if url is not UNSET:
            field_dict["url"] = url
        if registered_app_id is not UNSET:
            field_dict["registeredAppId"] = registered_app_id
        if ts_created is not UNSET:
            field_dict["tsCreated"] = ts_created
        if ts_expiry is not UNSET:
            field_dict["tsExpiry"] = ts_expiry
        if valid is not UNSET:
            field_dict["valid"] = valid

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        token = d.pop("token", UNSET)

        url = d.pop("url", UNSET)

        registered_app_id = d.pop("registeredAppId", UNSET)

        ts_created = d.pop("tsCreated", UNSET)

        ts_expiry = d.pop("tsExpiry", UNSET)

        valid = d.pop("valid", UNSET)

        dynamic_registration_token = cls(
            token=token,
            url=url,
            registered_app_id=registered_app_id,
            ts_created=ts_created,
            ts_expiry=ts_expiry,
            valid=valid,
        )

        dynamic_registration_token.additional_properties = d
        return dynamic_registration_token

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
