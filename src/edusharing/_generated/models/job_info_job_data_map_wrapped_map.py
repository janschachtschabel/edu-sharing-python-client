from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.job_info_job_data_map_wrapped_map_additional_property import (
        JobInfoJobDataMapWrappedMapAdditionalProperty,
    )


T = TypeVar("T", bound="JobInfoJobDataMapWrappedMap")


@_attrs_define
class JobInfoJobDataMapWrappedMap:
    """ """

    additional_properties: dict[str, JobInfoJobDataMapWrappedMapAdditionalProperty] = _attrs_field(
        init=False, factory=dict
    )

    def to_dict(self) -> dict[str, Any]:

        field_dict: dict[str, Any] = {}
        for prop_name, prop in self.additional_properties.items():
            field_dict[prop_name] = prop.to_dict()

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.job_info_job_data_map_wrapped_map_additional_property import (
            JobInfoJobDataMapWrappedMapAdditionalProperty,
        )

        d = dict(src_dict)
        job_info_job_data_map_wrapped_map = cls()

        additional_properties = {}
        for prop_name, prop_dict in d.items():
            additional_property = JobInfoJobDataMapWrappedMapAdditionalProperty.from_dict(prop_dict)

            additional_properties[prop_name] = additional_property

        job_info_job_data_map_wrapped_map.additional_properties = additional_properties
        return job_info_job_data_map_wrapped_map

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> JobInfoJobDataMapWrappedMapAdditionalProperty:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: JobInfoJobDataMapWrappedMapAdditionalProperty) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
