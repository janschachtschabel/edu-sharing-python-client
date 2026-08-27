from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.config_dashboard import ConfigDashboard


T = TypeVar("T", bound="ConfigFrontpage")


@_attrs_define
class ConfigFrontpage:
    """Front page configuration

    Attributes:
        enabled (bool | Unset):
        dashboard (ConfigDashboard | Unset):
    """

    enabled: bool | Unset = UNSET
    dashboard: ConfigDashboard | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        enabled = self.enabled

        dashboard: dict[str, Any] | Unset = UNSET
        if not isinstance(self.dashboard, Unset):
            dashboard = self.dashboard.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if enabled is not UNSET:
            field_dict["enabled"] = enabled
        if dashboard is not UNSET:
            field_dict["dashboard"] = dashboard

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.config_dashboard import ConfigDashboard

        d = dict(src_dict)
        enabled = d.pop("enabled", UNSET)

        _dashboard = d.pop("dashboard", UNSET)
        dashboard: ConfigDashboard | Unset
        if isinstance(_dashboard, Unset):
            dashboard = UNSET
        else:
            dashboard = ConfigDashboard.from_dict(_dashboard)

        config_frontpage = cls(
            enabled=enabled,
            dashboard=dashboard,
        )

        config_frontpage.additional_properties = d
        return config_frontpage

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
