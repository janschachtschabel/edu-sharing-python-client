from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ManualRegistrationData")


@_attrs_define
class ManualRegistrationData:
    """
    Attributes:
        target_link_uri (str): The default target link uri to use unless defined otherwise in the message or link
            definition
        client_name (str): Name of the Tool to be presented to the End-User. Localized representations may be included
            as described in Section 2.1 of the [OIDC-Reg] specification
        tool_name (str | Unset):
        tool_url (str | Unset):
        tool_description (str | Unset):
        keyset_url (str | Unset):
        login_initiation_url (str | Unset):
        redirection_urls (list[str] | Unset):
        custom_parameters (list[str] | Unset): JSON Oject where each value is a string. Custom parameters to be included
            in each launch to this tool. If a custom parameter is also defined at the message level, the message level value
            takes precedence. The value of the custom parameters may be substitution parameters as described in the LTI Core
            [LTI-13] specification
        logo_url (str | Unset):
        target_link_uri_deep_link (str | Unset): The target link uri to use for DeepLing Message
    """

    target_link_uri: str
    client_name: str
    tool_name: str | Unset = UNSET
    tool_url: str | Unset = UNSET
    tool_description: str | Unset = UNSET
    keyset_url: str | Unset = UNSET
    login_initiation_url: str | Unset = UNSET
    redirection_urls: list[str] | Unset = UNSET
    custom_parameters: list[str] | Unset = UNSET
    logo_url: str | Unset = UNSET
    target_link_uri_deep_link: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        target_link_uri = self.target_link_uri

        client_name = self.client_name

        tool_name = self.tool_name

        tool_url = self.tool_url

        tool_description = self.tool_description

        keyset_url = self.keyset_url

        login_initiation_url = self.login_initiation_url

        redirection_urls: list[str] | Unset = UNSET
        if not isinstance(self.redirection_urls, Unset):
            redirection_urls = self.redirection_urls

        custom_parameters: list[str] | Unset = UNSET
        if not isinstance(self.custom_parameters, Unset):
            custom_parameters = self.custom_parameters

        logo_url = self.logo_url

        target_link_uri_deep_link = self.target_link_uri_deep_link

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "targetLinkUri": target_link_uri,
                "clientName": client_name,
            }
        )
        if tool_name is not UNSET:
            field_dict["toolName"] = tool_name
        if tool_url is not UNSET:
            field_dict["toolUrl"] = tool_url
        if tool_description is not UNSET:
            field_dict["toolDescription"] = tool_description
        if keyset_url is not UNSET:
            field_dict["keysetUrl"] = keyset_url
        if login_initiation_url is not UNSET:
            field_dict["loginInitiationUrl"] = login_initiation_url
        if redirection_urls is not UNSET:
            field_dict["redirectionUrls"] = redirection_urls
        if custom_parameters is not UNSET:
            field_dict["customParameters"] = custom_parameters
        if logo_url is not UNSET:
            field_dict["logoUrl"] = logo_url
        if target_link_uri_deep_link is not UNSET:
            field_dict["targetLinkUriDeepLink"] = target_link_uri_deep_link

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        target_link_uri = d.pop("targetLinkUri")

        client_name = d.pop("clientName")

        tool_name = d.pop("toolName", UNSET)

        tool_url = d.pop("toolUrl", UNSET)

        tool_description = d.pop("toolDescription", UNSET)

        keyset_url = d.pop("keysetUrl", UNSET)

        login_initiation_url = d.pop("loginInitiationUrl", UNSET)

        redirection_urls = cast(list[str], d.pop("redirectionUrls", UNSET))

        custom_parameters = cast(list[str], d.pop("customParameters", UNSET))

        logo_url = d.pop("logoUrl", UNSET)

        target_link_uri_deep_link = d.pop("targetLinkUriDeepLink", UNSET)

        manual_registration_data = cls(
            target_link_uri=target_link_uri,
            client_name=client_name,
            tool_name=tool_name,
            tool_url=tool_url,
            tool_description=tool_description,
            keyset_url=keyset_url,
            login_initiation_url=login_initiation_url,
            redirection_urls=redirection_urls,
            custom_parameters=custom_parameters,
            logo_url=logo_url,
            target_link_uri_deep_link=target_link_uri_deep_link,
        )

        manual_registration_data.additional_properties = d
        return manual_registration_data

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
