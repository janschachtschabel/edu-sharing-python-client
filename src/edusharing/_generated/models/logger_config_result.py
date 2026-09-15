from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="LoggerConfigResult")


@_attrs_define
class LoggerConfigResult:
    """
    Attributes:
        name (str | Unset):
        level (str | Unset):
        appender (list[str] | Unset):
        config (bool | Unset):
    """

    name: str | Unset = UNSET
    level: str | Unset = UNSET
    appender: list[str] | Unset = UNSET
    config: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        level = self.level

        appender: list[str] | Unset = UNSET
        if not isinstance(self.appender, Unset):
            appender = self.appender

        config = self.config

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if level is not UNSET:
            field_dict["level"] = level
        if appender is not UNSET:
            field_dict["appender"] = appender
        if config is not UNSET:
            field_dict["config"] = config

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        level = d.pop("level", UNSET)

        appender = cast(list[str], d.pop("appender", UNSET))

        config = d.pop("config", UNSET)

        logger_config_result = cls(
            name=name,
            level=level,
            appender=appender,
            config=config,
        )

        logger_config_result.additional_properties = d
        return logger_config_result

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
