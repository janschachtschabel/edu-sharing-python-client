from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.collections_type import CollectionsType


T = TypeVar("T", bound="Collections")


@_attrs_define
class Collections:
    """Collections configuration (allowed colors, special types like editorial)

    Attributes:
        types (CollectionsType | Unset): Special collection types configuration
        colors (list[str] | Unset): Array of allowed color values for collections
    """

    types: CollectionsType | Unset = UNSET
    colors: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        types: dict[str, Any] | Unset = UNSET
        if not isinstance(self.types, Unset):
            types = self.types.to_dict()

        colors: list[str] | Unset = UNSET
        if not isinstance(self.colors, Unset):
            colors = self.colors

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if types is not UNSET:
            field_dict["types"] = types
        if colors is not UNSET:
            field_dict["colors"] = colors

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.collections_type import CollectionsType

        d = dict(src_dict)
        _types = d.pop("types", UNSET)
        types: CollectionsType | Unset
        if isinstance(_types, Unset):
            types = UNSET
        else:
            types = CollectionsType.from_dict(_types)

        colors = cast(list[str], d.pop("colors", UNSET))

        collections = cls(
            types=types,
            colors=colors,
        )

        collections.additional_properties = d
        return collections

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
