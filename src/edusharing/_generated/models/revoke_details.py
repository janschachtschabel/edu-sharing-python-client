from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="RevokeDetails")


@_attrs_define
class RevokeDetails:
    """
    Attributes:
        reason (str | Unset):
        cleanup_collections (bool | Unset):
        cleanup_usages (bool | Unset):
        unpublish (bool | Unset):
        remove_content (bool | Unset):
    """

    reason: str | Unset = UNSET
    cleanup_collections: bool | Unset = UNSET
    cleanup_usages: bool | Unset = UNSET
    unpublish: bool | Unset = UNSET
    remove_content: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        reason = self.reason

        cleanup_collections = self.cleanup_collections

        cleanup_usages = self.cleanup_usages

        unpublish = self.unpublish

        remove_content = self.remove_content

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if reason is not UNSET:
            field_dict["reason"] = reason
        if cleanup_collections is not UNSET:
            field_dict["cleanupCollections"] = cleanup_collections
        if cleanup_usages is not UNSET:
            field_dict["cleanupUsages"] = cleanup_usages
        if unpublish is not UNSET:
            field_dict["unpublish"] = unpublish
        if remove_content is not UNSET:
            field_dict["removeContent"] = remove_content

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        reason = d.pop("reason", UNSET)

        cleanup_collections = d.pop("cleanupCollections", UNSET)

        cleanup_usages = d.pop("cleanupUsages", UNSET)

        unpublish = d.pop("unpublish", UNSET)

        remove_content = d.pop("removeContent", UNSET)

        revoke_details = cls(
            reason=reason,
            cleanup_collections=cleanup_collections,
            cleanup_usages=cleanup_usages,
            unpublish=unpublish,
            remove_content=remove_content,
        )

        revoke_details.additional_properties = d
        return revoke_details

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
