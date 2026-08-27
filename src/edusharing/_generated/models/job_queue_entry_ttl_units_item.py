from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="JobQueueEntryTtlUnitsItem")


@_attrs_define
class JobQueueEntryTtlUnitsItem:
    """
    Attributes:
        duration_estimated (bool | Unset):
        time_based (bool | Unset):
        date_based (bool | Unset):
    """

    duration_estimated: bool | Unset = UNSET
    time_based: bool | Unset = UNSET
    date_based: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        duration_estimated = self.duration_estimated

        time_based = self.time_based

        date_based = self.date_based

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if duration_estimated is not UNSET:
            field_dict["durationEstimated"] = duration_estimated
        if time_based is not UNSET:
            field_dict["timeBased"] = time_based
        if date_based is not UNSET:
            field_dict["dateBased"] = date_based

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        duration_estimated = d.pop("durationEstimated", UNSET)

        time_based = d.pop("timeBased", UNSET)

        date_based = d.pop("dateBased", UNSET)

        job_queue_entry_ttl_units_item = cls(
            duration_estimated=duration_estimated,
            time_based=time_based,
            date_based=date_based,
        )

        job_queue_entry_ttl_units_item.additional_properties = d
        return job_queue_entry_ttl_units_item

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
