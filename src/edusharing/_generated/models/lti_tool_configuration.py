from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LTIToolConfiguration")


@_attrs_define
class LTIToolConfiguration:
    """
    Attributes:
        version (str | Unset):
        deployment_id (str | Unset):
        target_link_uri (str | Unset):
        domain (str | Unset):
        description (str | Unset):
        claims (list[str] | Unset):
    """

    version: str | Unset = UNSET
    deployment_id: str | Unset = UNSET
    target_link_uri: str | Unset = UNSET
    domain: str | Unset = UNSET
    description: str | Unset = UNSET
    claims: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version = self.version

        deployment_id = self.deployment_id

        target_link_uri = self.target_link_uri

        domain = self.domain

        description = self.description

        claims: list[str] | Unset = UNSET
        if not isinstance(self.claims, Unset):
            claims = self.claims

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if version is not UNSET:
            field_dict["version"] = version
        if deployment_id is not UNSET:
            field_dict["deployment_id"] = deployment_id
        if target_link_uri is not UNSET:
            field_dict["target_link_uri"] = target_link_uri
        if domain is not UNSET:
            field_dict["domain"] = domain
        if description is not UNSET:
            field_dict["description"] = description
        if claims is not UNSET:
            field_dict["claims"] = claims

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        version = d.pop("version", UNSET)

        deployment_id = d.pop("deployment_id", UNSET)

        target_link_uri = d.pop("target_link_uri", UNSET)

        domain = d.pop("domain", UNSET)

        description = d.pop("description", UNSET)

        claims = cast(list[str], d.pop("claims", UNSET))

        lti_tool_configuration = cls(
            version=version,
            deployment_id=deployment_id,
            target_link_uri=target_link_uri,
            domain=domain,
            description=description,
            claims=claims,
        )

        lti_tool_configuration.additional_properties = d
        return lti_tool_configuration

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
