from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigReportProblem")


@_attrs_define
class ConfigReportProblem:
    """Problem reporting configuration

    Attributes:
        tool_permissions (list[str] | Unset):
    """

    tool_permissions: list[str] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        tool_permissions: list[str] | Unset = UNSET
        if not isinstance(self.tool_permissions, Unset):
            tool_permissions = self.tool_permissions

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if tool_permissions is not UNSET:
            field_dict["toolPermissions"] = tool_permissions

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        tool_permissions = cast(list[str], d.pop("toolPermissions", UNSET))

        config_report_problem = cls(
            tool_permissions=tool_permissions,
        )

        config_report_problem.additional_properties = d
        return config_report_problem

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
