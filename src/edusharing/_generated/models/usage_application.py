from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UsageApplication")


@_attrs_define
class UsageApplication:
    """
    Attributes:
        app_id (str | Unset):
        app_caption (str | Unset):
        domain (str | Unset):
    """

    app_id: str | Unset = UNSET
    app_caption: str | Unset = UNSET
    domain: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        app_id = self.app_id

        app_caption = self.app_caption

        domain = self.domain

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if app_id is not UNSET:
            field_dict["appId"] = app_id
        if app_caption is not UNSET:
            field_dict["appCaption"] = app_caption
        if domain is not UNSET:
            field_dict["domain"] = domain

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        app_id = d.pop("appId", UNSET)

        app_caption = d.pop("appCaption", UNSET)

        domain = d.pop("domain", UNSET)

        usage_application = cls(
            app_id=app_id,
            app_caption=app_caption,
            domain=domain,
        )

        usage_application.additional_properties = d
        return usage_application

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
