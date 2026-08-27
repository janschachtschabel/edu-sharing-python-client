from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node import Node


T = TypeVar("T", bound="AdminStatistics")


@_attrs_define
class AdminStatistics:
    """
    Attributes:
        active_sessions (int | Unset):
        number_of_previews (int | Unset):
        max_memory (int | Unset):
        allocated_memory (int | Unset):
        preview_cache_size (int | Unset):
        active_locks (list[Node] | Unset):
    """

    active_sessions: int | Unset = UNSET
    number_of_previews: int | Unset = UNSET
    max_memory: int | Unset = UNSET
    allocated_memory: int | Unset = UNSET
    preview_cache_size: int | Unset = UNSET
    active_locks: list[Node] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        active_sessions = self.active_sessions

        number_of_previews = self.number_of_previews

        max_memory = self.max_memory

        allocated_memory = self.allocated_memory

        preview_cache_size = self.preview_cache_size

        active_locks: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.active_locks, Unset):
            active_locks = []
            for active_locks_item_data in self.active_locks:
                active_locks_item = active_locks_item_data.to_dict()
                active_locks.append(active_locks_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if active_sessions is not UNSET:
            field_dict["activeSessions"] = active_sessions
        if number_of_previews is not UNSET:
            field_dict["numberOfPreviews"] = number_of_previews
        if max_memory is not UNSET:
            field_dict["maxMemory"] = max_memory
        if allocated_memory is not UNSET:
            field_dict["allocatedMemory"] = allocated_memory
        if preview_cache_size is not UNSET:
            field_dict["previewCacheSize"] = preview_cache_size
        if active_locks is not UNSET:
            field_dict["activeLocks"] = active_locks

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node import Node

        d = dict(src_dict)
        active_sessions = d.pop("activeSessions", UNSET)

        number_of_previews = d.pop("numberOfPreviews", UNSET)

        max_memory = d.pop("maxMemory", UNSET)

        allocated_memory = d.pop("allocatedMemory", UNSET)

        preview_cache_size = d.pop("previewCacheSize", UNSET)

        _active_locks = d.pop("activeLocks", UNSET)
        active_locks: list[Node] | Unset = UNSET
        if _active_locks is not UNSET:
            active_locks = []
            for active_locks_item_data in _active_locks:
                active_locks_item = Node.from_dict(active_locks_item_data)

                active_locks.append(active_locks_item)

        admin_statistics = cls(
            active_sessions=active_sessions,
            number_of_previews=number_of_previews,
            max_memory=max_memory,
            allocated_memory=allocated_memory,
            preview_cache_size=preview_cache_size,
            active_locks=active_locks,
        )

        admin_statistics.additional_properties = d
        return admin_statistics

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
