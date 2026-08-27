from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="CreateUsage")


@_attrs_define
class CreateUsage:
    """
    Attributes:
        app_id (str | Unset):
        course_id (str | Unset):
        course_title (str | Unset):
        resource_id (str | Unset):
        node_id (str | Unset):
        node_version (str | Unset):
    """

    app_id: str | Unset = UNSET
    course_id: str | Unset = UNSET
    course_title: str | Unset = UNSET
    resource_id: str | Unset = UNSET
    node_id: str | Unset = UNSET
    node_version: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        app_id = self.app_id

        course_id = self.course_id

        course_title = self.course_title

        resource_id = self.resource_id

        node_id = self.node_id

        node_version = self.node_version

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if app_id is not UNSET:
            field_dict["appId"] = app_id
        if course_id is not UNSET:
            field_dict["courseId"] = course_id
        if course_title is not UNSET:
            field_dict["courseTitle"] = course_title
        if resource_id is not UNSET:
            field_dict["resourceId"] = resource_id
        if node_id is not UNSET:
            field_dict["nodeId"] = node_id
        if node_version is not UNSET:
            field_dict["nodeVersion"] = node_version

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        app_id = d.pop("appId", UNSET)

        course_id = d.pop("courseId", UNSET)

        course_title = d.pop("courseTitle", UNSET)

        resource_id = d.pop("resourceId", UNSET)

        node_id = d.pop("nodeId", UNSET)

        node_version = d.pop("nodeVersion", UNSET)

        create_usage = cls(
            app_id=app_id,
            course_id=course_id,
            course_title=course_title,
            resource_id=resource_id,
            node_id=node_id,
            node_version=node_version,
        )

        create_usage.additional_properties = d
        return create_usage

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
