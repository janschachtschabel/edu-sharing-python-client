from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LoginInitiationsBody")


@_attrs_define
class LoginInitiationsBody:
    """
    Attributes:
        iss (str): Issuer of the request, will be validated
        target_link_uri (str): target url of platform at the end of the flow
        client_id (str | Unset): Id of the issuer
        login_hint (str | Unset): context information of the platform
        lti_message_hint (str | Unset): additional context information of the platform
        lti_deployment_id (str | Unset): A can have multiple deployments in a platform
    """

    iss: str
    target_link_uri: str
    client_id: str | Unset = UNSET
    login_hint: str | Unset = UNSET
    lti_message_hint: str | Unset = UNSET
    lti_deployment_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        iss = self.iss

        target_link_uri = self.target_link_uri

        client_id = self.client_id

        login_hint = self.login_hint

        lti_message_hint = self.lti_message_hint

        lti_deployment_id = self.lti_deployment_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "iss": iss,
                "target_link_uri": target_link_uri,
            }
        )
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if login_hint is not UNSET:
            field_dict["login_hint"] = login_hint
        if lti_message_hint is not UNSET:
            field_dict["lti_message_hint"] = lti_message_hint
        if lti_deployment_id is not UNSET:
            field_dict["lti_deployment_id"] = lti_deployment_id

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        iss = d.pop("iss")

        target_link_uri = d.pop("target_link_uri")

        client_id = d.pop("client_id", UNSET)

        login_hint = d.pop("login_hint", UNSET)

        lti_message_hint = d.pop("lti_message_hint", UNSET)

        lti_deployment_id = d.pop("lti_deployment_id", UNSET)

        login_initiations_body = cls(
            iss=iss,
            target_link_uri=target_link_uri,
            client_id=client_id,
            login_hint=login_hint,
            lti_message_hint=lti_message_hint,
            lti_deployment_id=lti_deployment_id,
        )

        login_initiations_body.additional_properties = d
        return login_initiations_body

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
