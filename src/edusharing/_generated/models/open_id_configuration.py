from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.lti_platform_configuration import LTIPlatformConfiguration


T = TypeVar("T", bound="OpenIdConfiguration")


@_attrs_define
class OpenIdConfiguration:
    """
    Attributes:
        issuer (str | Unset):
        token_endpoint (str | Unset):
        token_endpoint_auth_methods_supported (list[str] | Unset):
        token_endpoint_auth_signing_alg_values_supported (list[str] | Unset):
        jwks_uri (str | Unset):
        authorization_endpoint (str | Unset):
        registration_endpoint (str | Unset):
        scopes_supported (list[str] | Unset):
        response_types_supported (list[str] | Unset):
        subject_types_supported (list[str] | Unset):
        id_token_signing_alg_values_supported (list[str] | Unset):
        claims_supported (list[str] | Unset):
        httpspurl_imsglobal_orgspeclti_platform_configuration (LTIPlatformConfiguration | Unset):
    """

    issuer: str | Unset = UNSET
    token_endpoint: str | Unset = UNSET
    token_endpoint_auth_methods_supported: list[str] | Unset = UNSET
    token_endpoint_auth_signing_alg_values_supported: list[str] | Unset = UNSET
    jwks_uri: str | Unset = UNSET
    authorization_endpoint: str | Unset = UNSET
    registration_endpoint: str | Unset = UNSET
    scopes_supported: list[str] | Unset = UNSET
    response_types_supported: list[str] | Unset = UNSET
    subject_types_supported: list[str] | Unset = UNSET
    id_token_signing_alg_values_supported: list[str] | Unset = UNSET
    claims_supported: list[str] | Unset = UNSET
    httpspurl_imsglobal_orgspeclti_platform_configuration: LTIPlatformConfiguration | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        issuer = self.issuer

        token_endpoint = self.token_endpoint

        token_endpoint_auth_methods_supported: list[str] | Unset = UNSET
        if not isinstance(self.token_endpoint_auth_methods_supported, Unset):
            token_endpoint_auth_methods_supported = self.token_endpoint_auth_methods_supported

        token_endpoint_auth_signing_alg_values_supported: list[str] | Unset = UNSET
        if not isinstance(self.token_endpoint_auth_signing_alg_values_supported, Unset):
            token_endpoint_auth_signing_alg_values_supported = (
                self.token_endpoint_auth_signing_alg_values_supported
            )

        jwks_uri = self.jwks_uri

        authorization_endpoint = self.authorization_endpoint

        registration_endpoint = self.registration_endpoint

        scopes_supported: list[str] | Unset = UNSET
        if not isinstance(self.scopes_supported, Unset):
            scopes_supported = self.scopes_supported

        response_types_supported: list[str] | Unset = UNSET
        if not isinstance(self.response_types_supported, Unset):
            response_types_supported = self.response_types_supported

        subject_types_supported: list[str] | Unset = UNSET
        if not isinstance(self.subject_types_supported, Unset):
            subject_types_supported = self.subject_types_supported

        id_token_signing_alg_values_supported: list[str] | Unset = UNSET
        if not isinstance(self.id_token_signing_alg_values_supported, Unset):
            id_token_signing_alg_values_supported = self.id_token_signing_alg_values_supported

        claims_supported: list[str] | Unset = UNSET
        if not isinstance(self.claims_supported, Unset):
            claims_supported = self.claims_supported

        httpspurl_imsglobal_orgspeclti_platform_configuration: dict[str, Any] | Unset = UNSET
        if not isinstance(self.httpspurl_imsglobal_orgspeclti_platform_configuration, Unset):
            httpspurl_imsglobal_orgspeclti_platform_configuration = (
                self.httpspurl_imsglobal_orgspeclti_platform_configuration.to_dict()
            )

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if issuer is not UNSET:
            field_dict["issuer"] = issuer
        if token_endpoint is not UNSET:
            field_dict["token_endpoint"] = token_endpoint
        if token_endpoint_auth_methods_supported is not UNSET:
            field_dict["token_endpoint_auth_methods_supported"] = (
                token_endpoint_auth_methods_supported
            )
        if token_endpoint_auth_signing_alg_values_supported is not UNSET:
            field_dict["token_endpoint_auth_signing_alg_values_supported"] = (
                token_endpoint_auth_signing_alg_values_supported
            )
        if jwks_uri is not UNSET:
            field_dict["jwks_uri"] = jwks_uri
        if authorization_endpoint is not UNSET:
            field_dict["authorization_endpoint"] = authorization_endpoint
        if registration_endpoint is not UNSET:
            field_dict["registration_endpoint"] = registration_endpoint
        if scopes_supported is not UNSET:
            field_dict["scopes_supported"] = scopes_supported
        if response_types_supported is not UNSET:
            field_dict["response_types_supported"] = response_types_supported
        if subject_types_supported is not UNSET:
            field_dict["subject_types_supported"] = subject_types_supported
        if id_token_signing_alg_values_supported is not UNSET:
            field_dict["id_token_signing_alg_values_supported"] = (
                id_token_signing_alg_values_supported
            )
        if claims_supported is not UNSET:
            field_dict["claims_supported"] = claims_supported
        if httpspurl_imsglobal_orgspeclti_platform_configuration is not UNSET:
            field_dict["https://purl.imsglobal.org/spec/lti-platform-configuration"] = (
                httpspurl_imsglobal_orgspeclti_platform_configuration
            )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.lti_platform_configuration import LTIPlatformConfiguration

        d = dict(src_dict)
        issuer = d.pop("issuer", UNSET)

        token_endpoint = d.pop("token_endpoint", UNSET)

        token_endpoint_auth_methods_supported = cast(
            list[str], d.pop("token_endpoint_auth_methods_supported", UNSET)
        )

        token_endpoint_auth_signing_alg_values_supported = cast(
            list[str], d.pop("token_endpoint_auth_signing_alg_values_supported", UNSET)
        )

        jwks_uri = d.pop("jwks_uri", UNSET)

        authorization_endpoint = d.pop("authorization_endpoint", UNSET)

        registration_endpoint = d.pop("registration_endpoint", UNSET)

        scopes_supported = cast(list[str], d.pop("scopes_supported", UNSET))

        response_types_supported = cast(list[str], d.pop("response_types_supported", UNSET))

        subject_types_supported = cast(list[str], d.pop("subject_types_supported", UNSET))

        id_token_signing_alg_values_supported = cast(
            list[str], d.pop("id_token_signing_alg_values_supported", UNSET)
        )

        claims_supported = cast(list[str], d.pop("claims_supported", UNSET))

        _httpspurl_imsglobal_orgspeclti_platform_configuration = d.pop(
            "https://purl.imsglobal.org/spec/lti-platform-configuration", UNSET
        )
        httpspurl_imsglobal_orgspeclti_platform_configuration: LTIPlatformConfiguration | Unset
        if isinstance(_httpspurl_imsglobal_orgspeclti_platform_configuration, Unset):
            httpspurl_imsglobal_orgspeclti_platform_configuration = UNSET
        else:
            httpspurl_imsglobal_orgspeclti_platform_configuration = (
                LTIPlatformConfiguration.from_dict(
                    _httpspurl_imsglobal_orgspeclti_platform_configuration
                )
            )

        open_id_configuration = cls(
            issuer=issuer,
            token_endpoint=token_endpoint,
            token_endpoint_auth_methods_supported=token_endpoint_auth_methods_supported,
            token_endpoint_auth_signing_alg_values_supported=token_endpoint_auth_signing_alg_values_supported,
            jwks_uri=jwks_uri,
            authorization_endpoint=authorization_endpoint,
            registration_endpoint=registration_endpoint,
            scopes_supported=scopes_supported,
            response_types_supported=response_types_supported,
            subject_types_supported=subject_types_supported,
            id_token_signing_alg_values_supported=id_token_signing_alg_values_supported,
            claims_supported=claims_supported,
            httpspurl_imsglobal_orgspeclti_platform_configuration=httpspurl_imsglobal_orgspeclti_platform_configuration,
        )

        open_id_configuration.additional_properties = d
        return open_id_configuration

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
