from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Relations")


@_attrs_define
class Relations:
    """
    Attributes:
        allowed_relations (list[str] | Unset):
    """

    allowed_relations: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        allowed_relations: list[str] | Unset = UNSET
        if not isinstance(self.allowed_relations, Unset):
            allowed_relations = self.allowed_relations

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if allowed_relations is not UNSET:
            field_dict["allowedRelations"] = allowed_relations

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        allowed_relations = cast(list[str], d.pop("allowedRelations", UNSET))

        relations = cls(
            allowed_relations=allowed_relations,
        )

        relations.additional_properties = d
        return relations

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
