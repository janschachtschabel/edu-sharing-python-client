from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job_builder import JobBuilder
    from ..models.job_detail_job_data_map import JobDetailJobDataMap
    from ..models.job_key import JobKey


T = TypeVar("T", bound="JobDetail")


@_attrs_define
class JobDetail:
    """
    Attributes:
        key (JobKey | Unset):
        description (str | Unset):
        job_data_map (JobDetailJobDataMap | Unset):
        persist_job_data_after_execution (bool | Unset):
        durable (bool | Unset):
        concurrent_execution_disallowed (bool | Unset):
        job_builder (JobBuilder | Unset):
    """

    key: JobKey | Unset = UNSET
    description: str | Unset = UNSET
    job_data_map: JobDetailJobDataMap | Unset = UNSET
    persist_job_data_after_execution: bool | Unset = UNSET
    durable: bool | Unset = UNSET
    concurrent_execution_disallowed: bool | Unset = UNSET
    job_builder: JobBuilder | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        key: dict[str, Any] | Unset = UNSET
        if not isinstance(self.key, Unset):
            key = self.key.to_dict()

        description = self.description

        job_data_map: dict[str, Any] | Unset = UNSET
        if not isinstance(self.job_data_map, Unset):
            job_data_map = self.job_data_map.to_dict()

        persist_job_data_after_execution = self.persist_job_data_after_execution

        durable = self.durable

        concurrent_execution_disallowed = self.concurrent_execution_disallowed

        job_builder: dict[str, Any] | Unset = UNSET
        if not isinstance(self.job_builder, Unset):
            job_builder = self.job_builder.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if key is not UNSET:
            field_dict["key"] = key
        if description is not UNSET:
            field_dict["description"] = description
        if job_data_map is not UNSET:
            field_dict["jobDataMap"] = job_data_map
        if persist_job_data_after_execution is not UNSET:
            field_dict["persistJobDataAfterExecution"] = persist_job_data_after_execution
        if durable is not UNSET:
            field_dict["durable"] = durable
        if concurrent_execution_disallowed is not UNSET:
            field_dict["concurrentExecutionDisallowed"] = concurrent_execution_disallowed
        if job_builder is not UNSET:
            field_dict["jobBuilder"] = job_builder

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.job_builder import JobBuilder
        from ..models.job_detail_job_data_map import JobDetailJobDataMap
        from ..models.job_key import JobKey

        d = dict(src_dict)
        _key = d.pop("key", UNSET)
        key: JobKey | Unset
        if isinstance(_key, Unset):
            key = UNSET
        else:
            key = JobKey.from_dict(_key)

        description = d.pop("description", UNSET)

        _job_data_map = d.pop("jobDataMap", UNSET)
        job_data_map: JobDetailJobDataMap | Unset
        if isinstance(_job_data_map, Unset):
            job_data_map = UNSET
        else:
            job_data_map = JobDetailJobDataMap.from_dict(_job_data_map)

        persist_job_data_after_execution = d.pop("persistJobDataAfterExecution", UNSET)

        durable = d.pop("durable", UNSET)

        concurrent_execution_disallowed = d.pop("concurrentExecutionDisallowed", UNSET)

        _job_builder = d.pop("jobBuilder", UNSET)
        job_builder: JobBuilder | Unset
        if isinstance(_job_builder, Unset):
            job_builder = UNSET
        else:
            job_builder = JobBuilder.from_dict(_job_builder)

        job_detail = cls(
            key=key,
            description=description,
            job_data_map=job_data_map,
            persist_job_data_after_execution=persist_job_data_after_execution,
            durable=durable,
            concurrent_execution_disallowed=concurrent_execution_disallowed,
            job_builder=job_builder,
        )

        job_detail.additional_properties = d
        return job_detail

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
