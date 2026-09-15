from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.media_type_parameters import MediaTypeParameters


T = TypeVar("T", bound="MediaType")


@_attrs_define
class MediaType:
    """
    Attributes:
        type_ (str | Unset):
        subtype (str | Unset):
        parameters (MediaTypeParameters | Unset):
        wildcard_type (bool | Unset):
        wildcard_subtype (bool | Unset):
    """

    type_: str | Unset = UNSET
    subtype: str | Unset = UNSET
    parameters: MediaTypeParameters | Unset = UNSET
    wildcard_type: bool | Unset = UNSET
    wildcard_subtype: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        subtype = self.subtype

        parameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()

        wildcard_type = self.wildcard_type

        wildcard_subtype = self.wildcard_subtype

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if subtype is not UNSET:
            field_dict["subtype"] = subtype
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if wildcard_type is not UNSET:
            field_dict["wildcardType"] = wildcard_type
        if wildcard_subtype is not UNSET:
            field_dict["wildcardSubtype"] = wildcard_subtype

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.media_type_parameters import MediaTypeParameters

        d = dict(src_dict)
        type_ = d.pop("type", UNSET)

        subtype = d.pop("subtype", UNSET)

        _parameters = d.pop("parameters", UNSET)
        parameters: MediaTypeParameters | Unset
        if isinstance(_parameters, Unset):
            parameters = UNSET
        else:
            parameters = MediaTypeParameters.from_dict(_parameters)

        wildcard_type = d.pop("wildcardType", UNSET)

        wildcard_subtype = d.pop("wildcardSubtype", UNSET)

        media_type = cls(
            type_=type_,
            subtype=subtype,
            parameters=parameters,
            wildcard_type=wildcard_type,
            wildcard_subtype=wildcard_subtype,
        )

        media_type.additional_properties = d
        return media_type

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
