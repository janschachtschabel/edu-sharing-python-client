from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.organization import Organization
    from ..models.pagination import Pagination


T = TypeVar("T", bound="OrganizationEntries")


@_attrs_define
class OrganizationEntries:
    """
    Attributes:
        organizations (list[Organization]):
        pagination (Pagination):
        can_create (bool | Unset):
    """

    organizations: list[Organization]
    pagination: Pagination
    can_create: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        organizations = []
        for organizations_item_data in self.organizations:
            organizations_item = organizations_item_data.to_dict()
            organizations.append(organizations_item)

        pagination = self.pagination.to_dict()

        can_create = self.can_create

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "organizations": organizations,
                "pagination": pagination,
            }
        )
        if can_create is not UNSET:
            field_dict["canCreate"] = can_create

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.organization import Organization
        from ..models.pagination import Pagination

        d = dict(src_dict)
        organizations = []
        _organizations = d.pop("organizations")
        for organizations_item_data in _organizations:
            organizations_item = Organization.from_dict(organizations_item_data)

            organizations.append(organizations_item)

        pagination = Pagination.from_dict(d.pop("pagination"))

        can_create = d.pop("canCreate", UNSET)

        organization_entries = cls(
            organizations=organizations,
            pagination=pagination,
            can_create=can_create,
        )

        organization_entries.additional_properties = d
        return organization_entries

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
