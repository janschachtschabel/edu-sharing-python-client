from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Tool")


@_attrs_define
class Tool:
    """
    Attributes:
        domain (str | Unset):
        description (str | Unset):
        app_id (str | Unset):
        name (str | Unset):
        logo (str | Unset):
        custom_content_option (bool | Unset):
        resource_type (str | Unset):
    """

    domain: str | Unset = UNSET
    description: str | Unset = UNSET
    app_id: str | Unset = UNSET
    name: str | Unset = UNSET
    logo: str | Unset = UNSET
    custom_content_option: bool | Unset = UNSET
    resource_type: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        domain = self.domain

        description = self.description

        app_id = self.app_id

        name = self.name

        logo = self.logo

        custom_content_option = self.custom_content_option

        resource_type = self.resource_type

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if domain is not UNSET:
            field_dict["domain"] = domain
        if description is not UNSET:
            field_dict["description"] = description
        if app_id is not UNSET:
            field_dict["appId"] = app_id
        if name is not UNSET:
            field_dict["name"] = name
        if logo is not UNSET:
            field_dict["logo"] = logo
        if custom_content_option is not UNSET:
            field_dict["customContentOption"] = custom_content_option
        if resource_type is not UNSET:
            field_dict["resourceType"] = resource_type

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        domain = d.pop("domain", UNSET)

        description = d.pop("description", UNSET)

        app_id = d.pop("appId", UNSET)

        name = d.pop("name", UNSET)

        logo = d.pop("logo", UNSET)

        custom_content_option = d.pop("customContentOption", UNSET)

        resource_type = d.pop("resourceType", UNSET)

        tool = cls(
            domain=domain,
            description=description,
            app_id=app_id,
            name=name,
            logo=logo,
            custom_content_option=custom_content_option,
            resource_type=resource_type,
        )

        tool.additional_properties = d
        return tool

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
