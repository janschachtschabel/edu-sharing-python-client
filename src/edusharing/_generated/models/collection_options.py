from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.collection_options_private_collections import CollectionOptionsPrivateCollections
from ..models.collection_options_public_collections import CollectionOptionsPublicCollections
from ..types import UNSET, Unset

T = TypeVar("T", bound="CollectionOptions")


@_attrs_define
class CollectionOptions:
    """
    Attributes:
        private_collections (CollectionOptionsPrivateCollections | Unset):
        public_collections (CollectionOptionsPublicCollections | Unset):
    """

    private_collections: CollectionOptionsPrivateCollections | Unset = UNSET
    public_collections: CollectionOptionsPublicCollections | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        private_collections: str | Unset = UNSET
        if not isinstance(self.private_collections, Unset):
            private_collections = self.private_collections.value

        public_collections: str | Unset = UNSET
        if not isinstance(self.public_collections, Unset):
            public_collections = self.public_collections.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if private_collections is not UNSET:
            field_dict["privateCollections"] = private_collections
        if public_collections is not UNSET:
            field_dict["publicCollections"] = public_collections

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _private_collections = d.pop("privateCollections", UNSET)
        private_collections: CollectionOptionsPrivateCollections | Unset
        if isinstance(_private_collections, Unset):
            private_collections = UNSET
        else:
            private_collections = CollectionOptionsPrivateCollections(_private_collections)

        _public_collections = d.pop("publicCollections", UNSET)
        public_collections: CollectionOptionsPublicCollections | Unset
        if isinstance(_public_collections, Unset):
            public_collections = UNSET
        else:
            public_collections = CollectionOptionsPublicCollections(_public_collections)

        collection_options = cls(
            private_collections=private_collections,
            public_collections=public_collections,
        )

        collection_options.additional_properties = d
        return collection_options

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
