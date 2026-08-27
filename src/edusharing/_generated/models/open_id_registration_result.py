from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.lti_tool_configuration import LTIToolConfiguration


T = TypeVar("T", bound="OpenIdRegistrationResult")


@_attrs_define
class OpenIdRegistrationResult:
    """
    Attributes:
        client_id (str | Unset):
        response_types (list[str] | Unset):
        jwks_uri (str | Unset):
        initiate_login_uri (str | Unset):
        grant_types (list[str] | Unset):
        redirect_uris (list[str] | Unset):
        application_type (str | Unset):
        token_endpoint_auth_method (str | Unset):
        client_name (str | Unset):
        logo_uri (str | Unset):
        scope (str | Unset):
        httpspurl_imsglobal_orgspeclti_tool_configuration (LTIToolConfiguration | Unset):
    """

    client_id: str | Unset = UNSET
    response_types: list[str] | Unset = UNSET
    jwks_uri: str | Unset = UNSET
    initiate_login_uri: str | Unset = UNSET
    grant_types: list[str] | Unset = UNSET
    redirect_uris: list[str] | Unset = UNSET
    application_type: str | Unset = UNSET
    token_endpoint_auth_method: str | Unset = UNSET
    client_name: str | Unset = UNSET
    logo_uri: str | Unset = UNSET
    scope: str | Unset = UNSET
    httpspurl_imsglobal_orgspeclti_tool_configuration: LTIToolConfiguration | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        client_id = self.client_id

        response_types: list[str] | Unset = UNSET
        if not isinstance(self.response_types, Unset):
            response_types = self.response_types

        jwks_uri = self.jwks_uri

        initiate_login_uri = self.initiate_login_uri

        grant_types: list[str] | Unset = UNSET
        if not isinstance(self.grant_types, Unset):
            grant_types = self.grant_types

        redirect_uris: list[str] | Unset = UNSET
        if not isinstance(self.redirect_uris, Unset):
            redirect_uris = self.redirect_uris

        application_type = self.application_type

        token_endpoint_auth_method = self.token_endpoint_auth_method

        client_name = self.client_name

        logo_uri = self.logo_uri

        scope = self.scope

        httpspurl_imsglobal_orgspeclti_tool_configuration: dict[str, Any] | Unset = UNSET
        if not isinstance(self.httpspurl_imsglobal_orgspeclti_tool_configuration, Unset):
            httpspurl_imsglobal_orgspeclti_tool_configuration = (
                self.httpspurl_imsglobal_orgspeclti_tool_configuration.to_dict()
            )

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if client_id is not UNSET:
            field_dict["client_id"] = client_id
        if response_types is not UNSET:
            field_dict["response_types"] = response_types
        if jwks_uri is not UNSET:
            field_dict["jwks_uri"] = jwks_uri
        if initiate_login_uri is not UNSET:
            field_dict["initiate_login_uri"] = initiate_login_uri
        if grant_types is not UNSET:
            field_dict["grant_types"] = grant_types
        if redirect_uris is not UNSET:
            field_dict["redirect_uris"] = redirect_uris
        if application_type is not UNSET:
            field_dict["application_type"] = application_type
        if token_endpoint_auth_method is not UNSET:
            field_dict["token_endpoint_auth_method"] = token_endpoint_auth_method
        if client_name is not UNSET:
            field_dict["client_name"] = client_name
        if logo_uri is not UNSET:
            field_dict["logo_uri"] = logo_uri
        if scope is not UNSET:
            field_dict["scope"] = scope
        if httpspurl_imsglobal_orgspeclti_tool_configuration is not UNSET:
            field_dict["https://purl.imsglobal.org/spec/lti-tool-configuration"] = (
                httpspurl_imsglobal_orgspeclti_tool_configuration
            )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.lti_tool_configuration import LTIToolConfiguration

        d = dict(src_dict)
        client_id = d.pop("client_id", UNSET)

        response_types = cast(list[str], d.pop("response_types", UNSET))

        jwks_uri = d.pop("jwks_uri", UNSET)

        initiate_login_uri = d.pop("initiate_login_uri", UNSET)

        grant_types = cast(list[str], d.pop("grant_types", UNSET))

        redirect_uris = cast(list[str], d.pop("redirect_uris", UNSET))

        application_type = d.pop("application_type", UNSET)

        token_endpoint_auth_method = d.pop("token_endpoint_auth_method", UNSET)

        client_name = d.pop("client_name", UNSET)

        logo_uri = d.pop("logo_uri", UNSET)

        scope = d.pop("scope", UNSET)

        _httpspurl_imsglobal_orgspeclti_tool_configuration = d.pop(
            "https://purl.imsglobal.org/spec/lti-tool-configuration", UNSET
        )
        httpspurl_imsglobal_orgspeclti_tool_configuration: LTIToolConfiguration | Unset
        if isinstance(_httpspurl_imsglobal_orgspeclti_tool_configuration, Unset):
            httpspurl_imsglobal_orgspeclti_tool_configuration = UNSET
        else:
            httpspurl_imsglobal_orgspeclti_tool_configuration = LTIToolConfiguration.from_dict(
                _httpspurl_imsglobal_orgspeclti_tool_configuration
            )

        open_id_registration_result = cls(
            client_id=client_id,
            response_types=response_types,
            jwks_uri=jwks_uri,
            initiate_login_uri=initiate_login_uri,
            grant_types=grant_types,
            redirect_uris=redirect_uris,
            application_type=application_type,
            token_endpoint_auth_method=token_endpoint_auth_method,
            client_name=client_name,
            logo_uri=logo_uri,
            scope=scope,
            httpspurl_imsglobal_orgspeclti_tool_configuration=httpspurl_imsglobal_orgspeclti_tool_configuration,
        )

        open_id_registration_result.additional_properties = d
        return open_id_registration_result

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
