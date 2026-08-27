from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.notification_config_config_mode import NotificationConfigConfigMode
from ..models.notification_config_default_interval import NotificationConfigDefaultInterval
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.notification_intervals import NotificationIntervals


T = TypeVar("T", bound="NotificationConfig")


@_attrs_define
class NotificationConfig:
    """
    Attributes:
        config_mode (NotificationConfigConfigMode | Unset):
        default_interval (NotificationConfigDefaultInterval | Unset):
        intervals (NotificationIntervals | Unset):
    """

    config_mode: NotificationConfigConfigMode | Unset = UNSET
    default_interval: NotificationConfigDefaultInterval | Unset = UNSET
    intervals: NotificationIntervals | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        config_mode: str | Unset = UNSET
        if not isinstance(self.config_mode, Unset):
            config_mode = self.config_mode.value

        default_interval: str | Unset = UNSET
        if not isinstance(self.default_interval, Unset):
            default_interval = self.default_interval.value

        intervals: dict[str, Any] | Unset = UNSET
        if not isinstance(self.intervals, Unset):
            intervals = self.intervals.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if config_mode is not UNSET:
            field_dict["configMode"] = config_mode
        if default_interval is not UNSET:
            field_dict["defaultInterval"] = default_interval
        if intervals is not UNSET:
            field_dict["intervals"] = intervals

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.notification_intervals import NotificationIntervals

        d = dict(src_dict)
        _config_mode = d.pop("configMode", UNSET)
        config_mode: NotificationConfigConfigMode | Unset
        if isinstance(_config_mode, Unset):
            config_mode = UNSET
        else:
            config_mode = NotificationConfigConfigMode(_config_mode)

        _default_interval = d.pop("defaultInterval", UNSET)
        default_interval: NotificationConfigDefaultInterval | Unset
        if isinstance(_default_interval, Unset):
            default_interval = UNSET
        else:
            default_interval = NotificationConfigDefaultInterval(_default_interval)

        _intervals = d.pop("intervals", UNSET)
        intervals: NotificationIntervals | Unset
        if isinstance(_intervals, Unset):
            intervals = UNSET
        else:
            intervals = NotificationIntervals.from_dict(_intervals)

        notification_config = cls(
            config_mode=config_mode,
            default_interval=default_interval,
            intervals=intervals,
        )

        notification_config.additional_properties = d
        return notification_config

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
