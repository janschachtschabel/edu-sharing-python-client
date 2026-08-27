from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.statistics_group import StatisticsGroup
    from ..models.statistics_key_group import StatisticsKeyGroup
    from ..models.statistics_user import StatisticsUser


T = TypeVar("T", bound="StatisticsGlobal")


@_attrs_define
class StatisticsGlobal:
    """
    Attributes:
        overall (StatisticsGroup | Unset):
        groups (list[StatisticsKeyGroup] | Unset):
        user (StatisticsUser | Unset):
    """

    overall: StatisticsGroup | Unset = UNSET
    groups: list[StatisticsKeyGroup] | Unset = UNSET
    user: StatisticsUser | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        overall: dict[str, Any] | Unset = UNSET
        if not isinstance(self.overall, Unset):
            overall = self.overall.to_dict()

        groups: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.groups, Unset):
            groups = []
            for groups_item_data in self.groups:
                groups_item = groups_item_data.to_dict()
                groups.append(groups_item)

        user: dict[str, Any] | Unset = UNSET
        if not isinstance(self.user, Unset):
            user = self.user.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if overall is not UNSET:
            field_dict["overall"] = overall
        if groups is not UNSET:
            field_dict["groups"] = groups
        if user is not UNSET:
            field_dict["user"] = user

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.statistics_group import StatisticsGroup
        from ..models.statistics_key_group import StatisticsKeyGroup
        from ..models.statistics_user import StatisticsUser

        d = dict(src_dict)
        _overall = d.pop("overall", UNSET)
        overall: StatisticsGroup | Unset
        if isinstance(_overall, Unset):
            overall = UNSET
        else:
            overall = StatisticsGroup.from_dict(_overall)

        _groups = d.pop("groups", UNSET)
        groups: list[StatisticsKeyGroup] | Unset = UNSET
        if _groups is not UNSET:
            groups = []
            for groups_item_data in _groups:
                groups_item = StatisticsKeyGroup.from_dict(groups_item_data)

                groups.append(groups_item)

        _user = d.pop("user", UNSET)
        user: StatisticsUser | Unset
        if isinstance(_user, Unset):
            user = UNSET
        else:
            user = StatisticsUser.from_dict(_user)

        statistics_global = cls(
            overall=overall,
            groups=groups,
            user=user,
        )

        statistics_global.additional_properties = d
        return statistics_global

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
