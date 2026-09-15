from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="OAuth2Consent")


@_attrs_define
class OAuth2Consent:
    """
    Attributes:
        client_id (str | Unset):
        state (str | Unset):
        scopes (list[str] | Unset):
    """

    client_id: str | Unset = UNSET
    state: str | Unset = UNSET
    scopes: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        client_id = self.client_id

        state = self.state

        scopes: list[str] | Unset = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = self.scopes

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if client_id is not UNSET:
            field_dict["clientId"] = client_id
        if state is not UNSET:
            field_dict["state"] = state
        if scopes is not UNSET:
            field_dict["scopes"] = scopes

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        client_id = d.pop("clientId", UNSET)

        state = d.pop("state", UNSET)

        scopes = cast(list[str], d.pop("scopes", UNSET))

        o_auth_2_consent = cls(
            client_id=client_id,
            state=state,
            scopes=scopes,
        )

        o_auth_2_consent.additional_properties = d
        return o_auth_2_consent

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
