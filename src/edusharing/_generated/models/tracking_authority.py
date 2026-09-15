from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.group import Group
    from ..models.organization import Organization


T = TypeVar("T", bound="TrackingAuthority")


@_attrs_define
class TrackingAuthority:
    """
    Attributes:
        hash_ (str | Unset):
        organization (list[Organization] | Unset):
        mediacenter (list[Group] | Unset):
    """

    hash_: str | Unset = UNSET
    organization: list[Organization] | Unset = UNSET
    mediacenter: list[Group] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        hash_ = self.hash_

        organization: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.organization, Unset):
            organization = []
            for organization_item_data in self.organization:
                organization_item = organization_item_data.to_dict()
                organization.append(organization_item)

        mediacenter: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.mediacenter, Unset):
            mediacenter = []
            for mediacenter_item_data in self.mediacenter:
                mediacenter_item = mediacenter_item_data.to_dict()
                mediacenter.append(mediacenter_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if hash_ is not UNSET:
            field_dict["hash"] = hash_
        if organization is not UNSET:
            field_dict["organization"] = organization
        if mediacenter is not UNSET:
            field_dict["mediacenter"] = mediacenter

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.group import Group
        from ..models.organization import Organization

        d = dict(src_dict)
        hash_ = d.pop("hash", UNSET)

        _organization = d.pop("organization", UNSET)
        organization: list[Organization] | Unset = UNSET
        if _organization is not UNSET:
            organization = []
            for organization_item_data in _organization:
                organization_item = Organization.from_dict(organization_item_data)

                organization.append(organization_item)

        _mediacenter = d.pop("mediacenter", UNSET)
        mediacenter: list[Group] | Unset = UNSET
        if _mediacenter is not UNSET:
            mediacenter = []
            for mediacenter_item_data in _mediacenter:
                mediacenter_item = Group.from_dict(mediacenter_item_data)

                mediacenter.append(mediacenter_item)

        tracking_authority = cls(
            hash_=hash_,
            organization=organization,
            mediacenter=mediacenter,
        )

        tracking_authority.additional_properties = d
        return tracking_authority

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
