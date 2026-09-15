from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_stats_group import UserStatsGroup


T = TypeVar("T", bound="UserStats")


@_attrs_define
class UserStats:
    """
    Attributes:
        all_stats (UserStatsGroup | Unset):
        public_stats (UserStatsGroup | Unset):
    """

    all_stats: UserStatsGroup | Unset = UNSET
    public_stats: UserStatsGroup | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        all_stats: dict[str, Any] | Unset = UNSET
        if not isinstance(self.all_stats, Unset):
            all_stats = self.all_stats.to_dict()

        public_stats: dict[str, Any] | Unset = UNSET
        if not isinstance(self.public_stats, Unset):
            public_stats = self.public_stats.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if all_stats is not UNSET:
            field_dict["allStats"] = all_stats
        if public_stats is not UNSET:
            field_dict["publicStats"] = public_stats

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.user_stats_group import UserStatsGroup

        d = dict(src_dict)
        _all_stats = d.pop("allStats", UNSET)
        all_stats: UserStatsGroup | Unset
        if isinstance(_all_stats, Unset):
            all_stats = UNSET
        else:
            all_stats = UserStatsGroup.from_dict(_all_stats)

        _public_stats = d.pop("publicStats", UNSET)
        public_stats: UserStatsGroup | Unset
        if isinstance(_public_stats, Unset):
            public_stats = UNSET
        else:
            public_stats = UserStatsGroup.from_dict(_public_stats)

        user_stats = cls(
            all_stats=all_stats,
            public_stats=public_stats,
        )

        user_stats.additional_properties = d
        return user_stats

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
