from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.mediacenter_profile_extension_content_status import (
    MediacenterProfileExtensionContentStatus,
)
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.catalog import Catalog


T = TypeVar("T", bound="MediacenterProfileExtension")


@_attrs_define
class MediacenterProfileExtension:
    """
    Attributes:
        id (str | Unset):
        location (str | Unset):
        district_abbreviation (str | Unset):
        main_url (str | Unset):
        catalogs (list[Catalog] | Unset):
        content_status (MediacenterProfileExtensionContentStatus | Unset):
    """

    id: str | Unset = UNSET
    location: str | Unset = UNSET
    district_abbreviation: str | Unset = UNSET
    main_url: str | Unset = UNSET
    catalogs: list[Catalog] | Unset = UNSET
    content_status: MediacenterProfileExtensionContentStatus | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        location = self.location

        district_abbreviation = self.district_abbreviation

        main_url = self.main_url

        catalogs: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.catalogs, Unset):
            catalogs = []
            for catalogs_item_data in self.catalogs:
                catalogs_item = catalogs_item_data.to_dict()
                catalogs.append(catalogs_item)

        content_status: str | Unset = UNSET
        if not isinstance(self.content_status, Unset):
            content_status = self.content_status.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if location is not UNSET:
            field_dict["location"] = location
        if district_abbreviation is not UNSET:
            field_dict["districtAbbreviation"] = district_abbreviation
        if main_url is not UNSET:
            field_dict["mainUrl"] = main_url
        if catalogs is not UNSET:
            field_dict["catalogs"] = catalogs
        if content_status is not UNSET:
            field_dict["contentStatus"] = content_status

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.catalog import Catalog

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        location = d.pop("location", UNSET)

        district_abbreviation = d.pop("districtAbbreviation", UNSET)

        main_url = d.pop("mainUrl", UNSET)

        _catalogs = d.pop("catalogs", UNSET)
        catalogs: list[Catalog] | Unset = UNSET
        if _catalogs is not UNSET:
            catalogs = []
            for catalogs_item_data in _catalogs:
                catalogs_item = Catalog.from_dict(catalogs_item_data)

                catalogs.append(catalogs_item)

        _content_status = d.pop("contentStatus", UNSET)
        content_status: MediacenterProfileExtensionContentStatus | Unset
        if isinstance(_content_status, Unset):
            content_status = UNSET
        else:
            content_status = MediacenterProfileExtensionContentStatus(_content_status)

        mediacenter_profile_extension = cls(
            id=id,
            location=location,
            district_abbreviation=district_abbreviation,
            main_url=main_url,
            catalogs=catalogs,
            content_status=content_status,
        )

        mediacenter_profile_extension.additional_properties = d
        return mediacenter_profile_extension

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
