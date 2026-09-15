from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.cache_info import CacheInfo
    from ..models.cache_member import CacheMember


T = TypeVar("T", bound="CacheCluster")


@_attrs_define
class CacheCluster:
    """
    Attributes:
        instances (list[CacheMember] | Unset):
        cache_infos (list[CacheInfo] | Unset):
        local_member (str | Unset):
        free_memory (int | Unset):
        total_memory (int | Unset):
        max_memory (int | Unset):
        available_processors (int | Unset):
        time_stamp (datetime.datetime | Unset):
        group_name (str | Unset):
    """

    instances: list[CacheMember] | Unset = UNSET
    cache_infos: list[CacheInfo] | Unset = UNSET
    local_member: str | Unset = UNSET
    free_memory: int | Unset = UNSET
    total_memory: int | Unset = UNSET
    max_memory: int | Unset = UNSET
    available_processors: int | Unset = UNSET
    time_stamp: datetime.datetime | Unset = UNSET
    group_name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        instances: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.instances, Unset):
            instances = []
            for instances_item_data in self.instances:
                instances_item = instances_item_data.to_dict()
                instances.append(instances_item)

        cache_infos: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.cache_infos, Unset):
            cache_infos = []
            for cache_infos_item_data in self.cache_infos:
                cache_infos_item = cache_infos_item_data.to_dict()
                cache_infos.append(cache_infos_item)

        local_member = self.local_member

        free_memory = self.free_memory

        total_memory = self.total_memory

        max_memory = self.max_memory

        available_processors = self.available_processors

        time_stamp: str | Unset = UNSET
        if not isinstance(self.time_stamp, Unset):
            time_stamp = self.time_stamp.isoformat()

        group_name = self.group_name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if instances is not UNSET:
            field_dict["instances"] = instances
        if cache_infos is not UNSET:
            field_dict["cacheInfos"] = cache_infos
        if local_member is not UNSET:
            field_dict["localMember"] = local_member
        if free_memory is not UNSET:
            field_dict["freeMemory"] = free_memory
        if total_memory is not UNSET:
            field_dict["totalMemory"] = total_memory
        if max_memory is not UNSET:
            field_dict["maxMemory"] = max_memory
        if available_processors is not UNSET:
            field_dict["availableProcessors"] = available_processors
        if time_stamp is not UNSET:
            field_dict["timeStamp"] = time_stamp
        if group_name is not UNSET:
            field_dict["groupName"] = group_name

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.cache_info import CacheInfo
        from ..models.cache_member import CacheMember

        d = dict(src_dict)
        _instances = d.pop("instances", UNSET)
        instances: list[CacheMember] | Unset = UNSET
        if _instances is not UNSET:
            instances = []
            for instances_item_data in _instances:
                instances_item = CacheMember.from_dict(instances_item_data)

                instances.append(instances_item)

        _cache_infos = d.pop("cacheInfos", UNSET)
        cache_infos: list[CacheInfo] | Unset = UNSET
        if _cache_infos is not UNSET:
            cache_infos = []
            for cache_infos_item_data in _cache_infos:
                cache_infos_item = CacheInfo.from_dict(cache_infos_item_data)

                cache_infos.append(cache_infos_item)

        local_member = d.pop("localMember", UNSET)

        free_memory = d.pop("freeMemory", UNSET)

        total_memory = d.pop("totalMemory", UNSET)

        max_memory = d.pop("maxMemory", UNSET)

        available_processors = d.pop("availableProcessors", UNSET)

        _time_stamp = d.pop("timeStamp", UNSET)
        time_stamp: datetime.datetime | Unset
        if isinstance(_time_stamp, Unset):
            time_stamp = UNSET
        else:
            time_stamp = datetime.datetime.fromisoformat(_time_stamp)

        group_name = d.pop("groupName", UNSET)

        cache_cluster = cls(
            instances=instances,
            cache_infos=cache_infos,
            local_member=local_member,
            free_memory=free_memory,
            total_memory=total_memory,
            max_memory=max_memory,
            available_processors=available_processors,
            time_stamp=time_stamp,
            group_name=group_name,
        )

        cache_cluster.additional_properties = d
        return cache_cluster

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
