from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.collections_type_config_invitation_type import CollectionsTypeConfigInvitationType
from ..types import UNSET, Unset

T = TypeVar("T", bound="CollectionsTypeConfig")


@_attrs_define
class CollectionsTypeConfig:
    """Configuration for editorial collections

    Attributes:
        invitation_type (CollectionsTypeConfigInvitationType | Unset): Type of invitation dialog
        metadata_group (str | Unset): Metadata group ID to display (null = no metadata shown)
    """

    invitation_type: CollectionsTypeConfigInvitationType | Unset = UNSET
    metadata_group: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        invitation_type: str | Unset = UNSET
        if not isinstance(self.invitation_type, Unset):
            invitation_type = self.invitation_type.value

        metadata_group = self.metadata_group

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if invitation_type is not UNSET:
            field_dict["invitationType"] = invitation_type
        if metadata_group is not UNSET:
            field_dict["metadataGroup"] = metadata_group

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _invitation_type = d.pop("invitationType", UNSET)
        invitation_type: CollectionsTypeConfigInvitationType | Unset
        if isinstance(_invitation_type, Unset):
            invitation_type = UNSET
        else:
            invitation_type = CollectionsTypeConfigInvitationType(_invitation_type)

        metadata_group = d.pop("metadataGroup", UNSET)

        collections_type_config = cls(
            invitation_type=invitation_type,
            metadata_group=metadata_group,
        )

        collections_type_config.additional_properties = d
        return collections_type_config

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
