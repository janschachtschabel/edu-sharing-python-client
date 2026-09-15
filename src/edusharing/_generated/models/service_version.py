from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="ServiceVersion")


@_attrs_define
class ServiceVersion:
    """
    Attributes:
        major (int):
        minor (int):
        repository (str | Unset):
        renderservice (str | Unset):
    """

    major: int
    minor: int
    repository: str | Unset = UNSET
    renderservice: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        major = self.major

        minor = self.minor

        repository = self.repository

        renderservice = self.renderservice

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "major": major,
                "minor": minor,
            }
        )
        if repository is not UNSET:
            field_dict["repository"] = repository
        if renderservice is not UNSET:
            field_dict["renderservice"] = renderservice

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        major = d.pop("major")

        minor = d.pop("minor")

        repository = d.pop("repository", UNSET)

        renderservice = d.pop("renderservice", UNSET)

        service_version = cls(
            major=major,
            minor=minor,
            repository=repository,
            renderservice=renderservice,
        )

        service_version.additional_properties = d
        return service_version

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
