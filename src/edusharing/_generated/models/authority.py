from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.authority_authority_type import AuthorityAuthorityType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.authority_properties import AuthorityProperties


T = TypeVar("T", bound="Authority")


@_attrs_define
class Authority:
    """
    Attributes:
        authority_name (str):
        authority_type (AuthorityAuthorityType | Unset):
        properties (AuthorityProperties | Unset):
        editable (bool | Unset):
    """

    authority_name: str
    authority_type: AuthorityAuthorityType | Unset = UNSET
    properties: AuthorityProperties | Unset = UNSET
    editable: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        authority_name = self.authority_name

        authority_type: str | Unset = UNSET
        if not isinstance(self.authority_type, Unset):
            authority_type = self.authority_type.value

        properties: dict[str, Any] | Unset = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        editable = self.editable

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "authorityName": authority_name,
            }
        )
        if authority_type is not UNSET:
            field_dict["authorityType"] = authority_type
        if properties is not UNSET:
            field_dict["properties"] = properties
        if editable is not UNSET:
            field_dict["editable"] = editable

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.authority_properties import AuthorityProperties

        d = dict(src_dict)
        authority_name = d.pop("authorityName")

        _authority_type = d.pop("authorityType", UNSET)
        authority_type: AuthorityAuthorityType | Unset
        if isinstance(_authority_type, Unset):
            authority_type = UNSET
        else:
            authority_type = AuthorityAuthorityType(_authority_type)

        _properties = d.pop("properties", UNSET)
        properties: AuthorityProperties | Unset
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = AuthorityProperties.from_dict(_properties)

        editable = d.pop("editable", UNSET)

        authority = cls(
            authority_name=authority_name,
            authority_type=authority_type,
            properties=properties,
            editable=editable,
        )

        authority.additional_properties = d
        return authority

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
