from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.tracking_authority import TrackingAuthority
    from ..models.tracking_counts import TrackingCounts
    from ..models.tracking_fields import TrackingFields
    from ..models.tracking_groups import TrackingGroups


T = TypeVar("T", bound="Tracking")


@_attrs_define
class Tracking:
    """
    Attributes:
        counts (TrackingCounts | Unset):
        date (str | Unset):
        fields (TrackingFields | Unset):
        groups (TrackingGroups | Unset):
        authority (TrackingAuthority | Unset):
    """

    counts: TrackingCounts | Unset = UNSET
    date: str | Unset = UNSET
    fields: TrackingFields | Unset = UNSET
    groups: TrackingGroups | Unset = UNSET
    authority: TrackingAuthority | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        counts: dict[str, Any] | Unset = UNSET
        if not isinstance(self.counts, Unset):
            counts = self.counts.to_dict()

        date = self.date

        fields: dict[str, Any] | Unset = UNSET
        if not isinstance(self.fields, Unset):
            fields = self.fields.to_dict()

        groups: dict[str, Any] | Unset = UNSET
        if not isinstance(self.groups, Unset):
            groups = self.groups.to_dict()

        authority: dict[str, Any] | Unset = UNSET
        if not isinstance(self.authority, Unset):
            authority = self.authority.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if counts is not UNSET:
            field_dict["counts"] = counts
        if date is not UNSET:
            field_dict["date"] = date
        if fields is not UNSET:
            field_dict["fields"] = fields
        if groups is not UNSET:
            field_dict["groups"] = groups
        if authority is not UNSET:
            field_dict["authority"] = authority

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.tracking_authority import TrackingAuthority
        from ..models.tracking_counts import TrackingCounts
        from ..models.tracking_fields import TrackingFields
        from ..models.tracking_groups import TrackingGroups

        d = dict(src_dict)
        _counts = d.pop("counts", UNSET)
        counts: TrackingCounts | Unset
        if isinstance(_counts, Unset):
            counts = UNSET
        else:
            counts = TrackingCounts.from_dict(_counts)

        date = d.pop("date", UNSET)

        _fields = d.pop("fields", UNSET)
        fields: TrackingFields | Unset
        if isinstance(_fields, Unset):
            fields = UNSET
        else:
            fields = TrackingFields.from_dict(_fields)

        _groups = d.pop("groups", UNSET)
        groups: TrackingGroups | Unset
        if isinstance(_groups, Unset):
            groups = UNSET
        else:
            groups = TrackingGroups.from_dict(_groups)

        _authority = d.pop("authority", UNSET)
        authority: TrackingAuthority | Unset
        if isinstance(_authority, Unset):
            authority = UNSET
        else:
            authority = TrackingAuthority.from_dict(_authority)

        tracking = cls(
            counts=counts,
            date=date,
            fields=fields,
            groups=groups,
            authority=authority,
        )

        tracking.additional_properties = d
        return tracking

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
