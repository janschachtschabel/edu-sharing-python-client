from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.simple_edit_global_groups import SimpleEditGlobalGroups
    from ..models.simple_edit_organization import SimpleEditOrganization


T = TypeVar("T", bound="SimpleEdit")


@_attrs_define
class SimpleEdit:
    """Quick edit dialog configuration

    Attributes:
        global_groups (list[SimpleEditGlobalGroups] | Unset): Global groups to offer in quick edit dialog
        organization (SimpleEditOrganization | Unset): Organization configuration for quick edit
        organization_filter (str | Unset): Organization filter pattern
        licenses (list[str] | Unset): Array of allowed license IDs for quick edit
    """

    global_groups: list[SimpleEditGlobalGroups] | Unset = UNSET
    organization: SimpleEditOrganization | Unset = UNSET
    organization_filter: str | Unset = UNSET
    licenses: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        global_groups: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.global_groups, Unset):
            global_groups = []
            for global_groups_item_data in self.global_groups:
                global_groups_item = global_groups_item_data.to_dict()
                global_groups.append(global_groups_item)

        organization: dict[str, Any] | Unset = UNSET
        if not isinstance(self.organization, Unset):
            organization = self.organization.to_dict()

        organization_filter = self.organization_filter

        licenses: list[str] | Unset = UNSET
        if not isinstance(self.licenses, Unset):
            licenses = self.licenses

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if global_groups is not UNSET:
            field_dict["globalGroups"] = global_groups
        if organization is not UNSET:
            field_dict["organization"] = organization
        if organization_filter is not UNSET:
            field_dict["organizationFilter"] = organization_filter
        if licenses is not UNSET:
            field_dict["licenses"] = licenses

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.simple_edit_global_groups import SimpleEditGlobalGroups
        from ..models.simple_edit_organization import SimpleEditOrganization

        d = dict(src_dict)
        _global_groups = d.pop("globalGroups", UNSET)
        global_groups: list[SimpleEditGlobalGroups] | Unset = UNSET
        if _global_groups is not UNSET:
            global_groups = []
            for global_groups_item_data in _global_groups:
                global_groups_item = SimpleEditGlobalGroups.from_dict(global_groups_item_data)

                global_groups.append(global_groups_item)

        _organization = d.pop("organization", UNSET)
        organization: SimpleEditOrganization | Unset
        if isinstance(_organization, Unset):
            organization = UNSET
        else:
            organization = SimpleEditOrganization.from_dict(_organization)

        organization_filter = d.pop("organizationFilter", UNSET)

        licenses = cast(list[str], d.pop("licenses", UNSET))

        simple_edit = cls(
            global_groups=global_groups,
            organization=organization,
            organization_filter=organization_filter,
            licenses=licenses,
        )

        simple_edit.additional_properties = d
        return simple_edit

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
