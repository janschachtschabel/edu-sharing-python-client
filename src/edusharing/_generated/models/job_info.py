from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.job_info_status import JobInfoStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job_detail import JobDetail
    from ..models.job_info_job_data_map import JobInfoJobDataMap
    from ..models.level import Level
    from ..models.log_entry import LogEntry


T = TypeVar("T", bound="JobInfo")


@_attrs_define
class JobInfo:
    """
    Attributes:
        unique_id (str | Unset):
        job_data_map (JobInfoJobDataMap | Unset):
        job_name (str | Unset):
        job_group (str | Unset):
        thread_id (int | Unset):
        start_time (int | Unset):
        finish_time (int | Unset):
        status (JobInfoStatus | Unset):
        worst_level (Level | Unset):
        log (list[LogEntry] | Unset):
        job_detail (JobDetail | Unset):
    """

    unique_id: str | Unset = UNSET
    job_data_map: JobInfoJobDataMap | Unset = UNSET
    job_name: str | Unset = UNSET
    job_group: str | Unset = UNSET
    thread_id: int | Unset = UNSET
    start_time: int | Unset = UNSET
    finish_time: int | Unset = UNSET
    status: JobInfoStatus | Unset = UNSET
    worst_level: Level | Unset = UNSET
    log: list[LogEntry] | Unset = UNSET
    job_detail: JobDetail | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        unique_id = self.unique_id

        job_data_map: dict[str, Any] | Unset = UNSET
        if not isinstance(self.job_data_map, Unset):
            job_data_map = self.job_data_map.to_dict()

        job_name = self.job_name

        job_group = self.job_group

        thread_id = self.thread_id

        start_time = self.start_time

        finish_time = self.finish_time

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        worst_level: dict[str, Any] | Unset = UNSET
        if not isinstance(self.worst_level, Unset):
            worst_level = self.worst_level.to_dict()

        log: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.log, Unset):
            log = []
            for log_item_data in self.log:
                log_item = log_item_data.to_dict()
                log.append(log_item)

        job_detail: dict[str, Any] | Unset = UNSET
        if not isinstance(self.job_detail, Unset):
            job_detail = self.job_detail.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if unique_id is not UNSET:
            field_dict["uniqueId"] = unique_id
        if job_data_map is not UNSET:
            field_dict["jobDataMap"] = job_data_map
        if job_name is not UNSET:
            field_dict["jobName"] = job_name
        if job_group is not UNSET:
            field_dict["jobGroup"] = job_group
        if thread_id is not UNSET:
            field_dict["threadId"] = thread_id
        if start_time is not UNSET:
            field_dict["startTime"] = start_time
        if finish_time is not UNSET:
            field_dict["finishTime"] = finish_time
        if status is not UNSET:
            field_dict["status"] = status
        if worst_level is not UNSET:
            field_dict["worstLevel"] = worst_level
        if log is not UNSET:
            field_dict["log"] = log
        if job_detail is not UNSET:
            field_dict["jobDetail"] = job_detail

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.job_detail import JobDetail
        from ..models.job_info_job_data_map import JobInfoJobDataMap
        from ..models.level import Level
        from ..models.log_entry import LogEntry

        d = dict(src_dict)
        unique_id = d.pop("uniqueId", UNSET)

        _job_data_map = d.pop("jobDataMap", UNSET)
        job_data_map: JobInfoJobDataMap | Unset
        if isinstance(_job_data_map, Unset):
            job_data_map = UNSET
        else:
            job_data_map = JobInfoJobDataMap.from_dict(_job_data_map)

        job_name = d.pop("jobName", UNSET)

        job_group = d.pop("jobGroup", UNSET)

        thread_id = d.pop("threadId", UNSET)

        start_time = d.pop("startTime", UNSET)

        finish_time = d.pop("finishTime", UNSET)

        _status = d.pop("status", UNSET)
        status: JobInfoStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = JobInfoStatus(_status)

        _worst_level = d.pop("worstLevel", UNSET)
        worst_level: Level | Unset
        if isinstance(_worst_level, Unset):
            worst_level = UNSET
        else:
            worst_level = Level.from_dict(_worst_level)

        _log = d.pop("log", UNSET)
        log: list[LogEntry] | Unset = UNSET
        if _log is not UNSET:
            log = []
            for log_item_data in _log:
                log_item = LogEntry.from_dict(log_item_data)

                log.append(log_item)

        _job_detail = d.pop("jobDetail", UNSET)
        job_detail: JobDetail | Unset
        if isinstance(_job_detail, Unset):
            job_detail = UNSET
        else:
            job_detail = JobDetail.from_dict(_job_detail)

        job_info = cls(
            unique_id=unique_id,
            job_data_map=job_data_map,
            job_name=job_name,
            job_group=job_group,
            thread_id=thread_id,
            start_time=start_time,
            finish_time=finish_time,
            status=status,
            worst_level=worst_level,
            log=log,
            job_detail=job_detail,
        )

        job_info.additional_properties = d
        return job_info

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
