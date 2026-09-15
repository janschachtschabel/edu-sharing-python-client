from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CacheInfo")


@_attrs_define
class CacheInfo:
    """
    Attributes:
        size (int | Unset):
        statistic_hits (int | Unset):
        name (str | Unset):
        backup_count (int | Unset):
        backup_entry_count (int | Unset):
        backup_entry_memory_cost (int | Unset):
        heap_cost (int | Unset):
        owned_entry_count (int | Unset):
        get_owned_entry_memory_cost (int | Unset):
        size_in_memory (int | Unset):
        member (str | Unset):
        group_name (str | Unset):
        max_size (int | Unset):
    """

    size: int | Unset = UNSET
    statistic_hits: int | Unset = UNSET
    name: str | Unset = UNSET
    backup_count: int | Unset = UNSET
    backup_entry_count: int | Unset = UNSET
    backup_entry_memory_cost: int | Unset = UNSET
    heap_cost: int | Unset = UNSET
    owned_entry_count: int | Unset = UNSET
    get_owned_entry_memory_cost: int | Unset = UNSET
    size_in_memory: int | Unset = UNSET
    member: str | Unset = UNSET
    group_name: str | Unset = UNSET
    max_size: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        size = self.size

        statistic_hits = self.statistic_hits

        name = self.name

        backup_count = self.backup_count

        backup_entry_count = self.backup_entry_count

        backup_entry_memory_cost = self.backup_entry_memory_cost

        heap_cost = self.heap_cost

        owned_entry_count = self.owned_entry_count

        get_owned_entry_memory_cost = self.get_owned_entry_memory_cost

        size_in_memory = self.size_in_memory

        member = self.member

        group_name = self.group_name

        max_size = self.max_size

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if size is not UNSET:
            field_dict["size"] = size
        if statistic_hits is not UNSET:
            field_dict["statisticHits"] = statistic_hits
        if name is not UNSET:
            field_dict["name"] = name
        if backup_count is not UNSET:
            field_dict["backupCount"] = backup_count
        if backup_entry_count is not UNSET:
            field_dict["backupEntryCount"] = backup_entry_count
        if backup_entry_memory_cost is not UNSET:
            field_dict["backupEntryMemoryCost"] = backup_entry_memory_cost
        if heap_cost is not UNSET:
            field_dict["heapCost"] = heap_cost
        if owned_entry_count is not UNSET:
            field_dict["ownedEntryCount"] = owned_entry_count
        if get_owned_entry_memory_cost is not UNSET:
            field_dict["getOwnedEntryMemoryCost"] = get_owned_entry_memory_cost
        if size_in_memory is not UNSET:
            field_dict["sizeInMemory"] = size_in_memory
        if member is not UNSET:
            field_dict["member"] = member
        if group_name is not UNSET:
            field_dict["groupName"] = group_name
        if max_size is not UNSET:
            field_dict["maxSize"] = max_size

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        size = d.pop("size", UNSET)

        statistic_hits = d.pop("statisticHits", UNSET)

        name = d.pop("name", UNSET)

        backup_count = d.pop("backupCount", UNSET)

        backup_entry_count = d.pop("backupEntryCount", UNSET)

        backup_entry_memory_cost = d.pop("backupEntryMemoryCost", UNSET)

        heap_cost = d.pop("heapCost", UNSET)

        owned_entry_count = d.pop("ownedEntryCount", UNSET)

        get_owned_entry_memory_cost = d.pop("getOwnedEntryMemoryCost", UNSET)

        size_in_memory = d.pop("sizeInMemory", UNSET)

        member = d.pop("member", UNSET)

        group_name = d.pop("groupName", UNSET)

        max_size = d.pop("maxSize", UNSET)

        cache_info = cls(
            size=size,
            statistic_hits=statistic_hits,
            name=name,
            backup_count=backup_count,
            backup_entry_count=backup_entry_count,
            backup_entry_memory_cost=backup_entry_memory_cost,
            heap_cost=heap_cost,
            owned_entry_count=owned_entry_count,
            get_owned_entry_memory_cost=get_owned_entry_memory_cost,
            size_in_memory=size_in_memory,
            member=member,
            group_name=group_name,
            max_size=max_size,
        )

        cache_info.additional_properties = d
        return cache_info

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
