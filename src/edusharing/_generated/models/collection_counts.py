from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.element import Element


T = TypeVar("T", bound="CollectionCounts")


@_attrs_define
class CollectionCounts:
    """
    Attributes:
        refs (list[Element] | Unset):
        collections (list[Element] | Unset):
    """

    refs: list[Element] | Unset = UNSET
    collections: list[Element] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        refs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.refs, Unset):
            refs = []
            for refs_item_data in self.refs:
                refs_item = refs_item_data.to_dict()
                refs.append(refs_item)

        collections: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.collections, Unset):
            collections = []
            for collections_item_data in self.collections:
                collections_item = collections_item_data.to_dict()
                collections.append(collections_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if refs is not UNSET:
            field_dict["refs"] = refs
        if collections is not UNSET:
            field_dict["collections"] = collections

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.element import Element

        d = dict(src_dict)
        _refs = d.pop("refs", UNSET)
        refs: list[Element] | Unset = UNSET
        if _refs is not UNSET:
            refs = []
            for refs_item_data in _refs:
                refs_item = Element.from_dict(refs_item_data)

                refs.append(refs_item)

        _collections = d.pop("collections", UNSET)
        collections: list[Element] | Unset = UNSET
        if _collections is not UNSET:
            collections = []
            for collections_item_data in _collections:
                collections_item = Element.from_dict(collections_item_data)

                collections.append(collections_item)

        collection_counts = cls(
            refs=refs,
            collections=collections,
        )

        collection_counts.additional_properties = d
        return collection_counts

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
