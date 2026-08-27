from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.job_queue_entry_status import JobQueueEntryStatus
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job_queue_entry_ttl import JobQueueEntryTtl


T = TypeVar("T", bound="JobQueueEntry")


@_attrs_define
class JobQueueEntry:
    """
    Attributes:
        id (int | Unset):
        unique (bool | Unset):
        group (str | Unset):
        requested (datetime.datetime | Unset):
        last_updated (datetime.datetime | Unset):
        status (JobQueueEntryStatus | Unset):
        ttl (JobQueueEntryTtl | Unset):
        job_hash (int | Unset):
        method (str | Unset):
        params (list[str] | Unset):
        user (str | Unset):
    """

    id: int | Unset = UNSET
    unique: bool | Unset = UNSET
    group: str | Unset = UNSET
    requested: datetime.datetime | Unset = UNSET
    last_updated: datetime.datetime | Unset = UNSET
    status: JobQueueEntryStatus | Unset = UNSET
    ttl: JobQueueEntryTtl | Unset = UNSET
    job_hash: int | Unset = UNSET
    method: str | Unset = UNSET
    params: list[str] | Unset = UNSET
    user: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        unique = self.unique

        group = self.group

        requested: str | Unset = UNSET
        if not isinstance(self.requested, Unset):
            requested = self.requested.isoformat()

        last_updated: str | Unset = UNSET
        if not isinstance(self.last_updated, Unset):
            last_updated = self.last_updated.isoformat()

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        ttl: dict[str, Any] | Unset = UNSET
        if not isinstance(self.ttl, Unset):
            ttl = self.ttl.to_dict()

        job_hash = self.job_hash

        method = self.method

        params: list[str] | Unset = UNSET
        if not isinstance(self.params, Unset):
            params = self.params

        user = self.user

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if unique is not UNSET:
            field_dict["unique"] = unique
        if group is not UNSET:
            field_dict["group"] = group
        if requested is not UNSET:
            field_dict["requested"] = requested
        if last_updated is not UNSET:
            field_dict["lastUpdated"] = last_updated
        if status is not UNSET:
            field_dict["status"] = status
        if ttl is not UNSET:
            field_dict["ttl"] = ttl
        if job_hash is not UNSET:
            field_dict["jobHash"] = job_hash
        if method is not UNSET:
            field_dict["method"] = method
        if params is not UNSET:
            field_dict["params"] = params
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.job_queue_entry_ttl import JobQueueEntryTtl

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        unique = d.pop("unique", UNSET)

        group = d.pop("group", UNSET)

        _requested = d.pop("requested", UNSET)
        requested: datetime.datetime | Unset
        if isinstance(_requested, Unset):
            requested = UNSET
        else:
            requested = datetime.datetime.fromisoformat(_requested)

        _last_updated = d.pop("lastUpdated", UNSET)
        last_updated: datetime.datetime | Unset
        if isinstance(_last_updated, Unset):
            last_updated = UNSET
        else:
            last_updated = datetime.datetime.fromisoformat(_last_updated)

        _status = d.pop("status", UNSET)
        status: JobQueueEntryStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = JobQueueEntryStatus(_status)

        _ttl = d.pop("ttl", UNSET)
        ttl: JobQueueEntryTtl | Unset
        if isinstance(_ttl, Unset):
            ttl = UNSET
        else:
            ttl = JobQueueEntryTtl.from_dict(_ttl)

        job_hash = d.pop("jobHash", UNSET)

        method = d.pop("method", UNSET)

        params = cast(list[str], d.pop("params", UNSET))

        user = d.pop("user", UNSET)

        job_queue_entry = cls(
            id=id,
            unique=unique,
            group=group,
            requested=requested,
            last_updated=last_updated,
            status=status,
            ttl=ttl,
            job_hash=job_hash,
            method=method,
            params=params,
            user=user,
        )

        job_queue_entry.additional_properties = d
        return job_queue_entry

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
