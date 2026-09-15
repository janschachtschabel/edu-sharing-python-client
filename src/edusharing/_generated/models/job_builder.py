from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="JobBuilder")


@_attrs_define
class JobBuilder:
    """
    Attributes:
        job_data (JobBuilder | Unset):
    """

    job_data: JobBuilder | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        job_data: dict[str, Any] | Unset = UNSET
        if not isinstance(self.job_data, Unset):
            job_data = self.job_data.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if job_data is not UNSET:
            field_dict["jobData"] = job_data

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _job_data = d.pop("jobData", UNSET)
        job_data: JobBuilder | Unset
        if isinstance(_job_data, Unset):
            job_data = UNSET
        else:
            job_data = JobBuilder.from_dict(_job_data)

        job_builder = cls(
            job_data=job_data,
        )

        job_builder.additional_properties = d
        return job_builder

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
