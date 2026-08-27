from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.collection_dto_properties import CollectionDTOProperties


T = TypeVar("T", bound="CollectionDTO")


@_attrs_define
class CollectionDTO:
    """
    Attributes:
        type_ (str | Unset):
        aspects (list[str] | Unset):
        properties (CollectionDTOProperties | Unset):
    """

    type_: str | Unset = UNSET
    aspects: list[str] | Unset = UNSET
    properties: CollectionDTOProperties | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        aspects: list[str] | Unset = UNSET
        if not isinstance(self.aspects, Unset):
            aspects = self.aspects

        properties: dict[str, Any] | Unset = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if aspects is not UNSET:
            field_dict["aspects"] = aspects
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.collection_dto_properties import CollectionDTOProperties

        d = dict(src_dict)
        type_ = d.pop("type", UNSET)

        aspects = cast(list[str], d.pop("aspects", UNSET))

        _properties = d.pop("properties", UNSET)
        properties: CollectionDTOProperties | Unset
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = CollectionDTOProperties.from_dict(_properties)

        collection_dto = cls(
            type_=type_,
            aspects=aspects,
            properties=properties,
        )

        collection_dto.additional_properties = d
        return collection_dto

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
