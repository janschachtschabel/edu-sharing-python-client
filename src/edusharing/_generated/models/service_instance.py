from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.service_version import ServiceVersion


T = TypeVar("T", bound="ServiceInstance")


@_attrs_define
class ServiceInstance:
    """
    Attributes:
        version (ServiceVersion):
        endpoint (str):
    """

    version: ServiceVersion
    endpoint: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version = self.version.to_dict()

        endpoint = self.endpoint

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "version": version,
                "endpoint": endpoint,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.service_version import ServiceVersion

        d = dict(src_dict)
        version = ServiceVersion.from_dict(d.pop("version"))

        endpoint = d.pop("endpoint")

        service_instance = cls(
            version=version,
            endpoint=endpoint,
        )

        service_instance.additional_properties = d
        return service_instance

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
