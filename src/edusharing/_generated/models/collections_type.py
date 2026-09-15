from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.collections_type_config import CollectionsTypeConfig


T = TypeVar("T", bound="CollectionsType")


@_attrs_define
class CollectionsType:
    """Special collection types configuration

    Attributes:
        editorial (CollectionsTypeConfig | Unset): Configuration for editorial collections
    """

    editorial: CollectionsTypeConfig | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        editorial: dict[str, Any] | Unset = UNSET
        if not isinstance(self.editorial, Unset):
            editorial = self.editorial.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if editorial is not UNSET:
            field_dict["editorial"] = editorial

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.collections_type_config import CollectionsTypeConfig

        d = dict(src_dict)
        _editorial = d.pop("editorial", UNSET)
        editorial: CollectionsTypeConfig | Unset
        if isinstance(_editorial, Unset):
            editorial = UNSET
        else:
            editorial = CollectionsTypeConfig.from_dict(_editorial)

        collections_type = cls(
            editorial=editorial,
        )

        collections_type.additional_properties = d
        return collections_type

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
