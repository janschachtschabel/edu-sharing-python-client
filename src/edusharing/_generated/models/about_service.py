from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

if TYPE_CHECKING:
    from ..models.service_instance import ServiceInstance


T = TypeVar("T", bound="AboutService")


@_attrs_define
class AboutService:
    """
    Attributes:
        name (str):
        instances (list[ServiceInstance]):
    """

    name: str
    instances: list[ServiceInstance]
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        instances = []
        for instances_item_data in self.instances:
            instances_item = instances_item_data.to_dict()
            instances.append(instances_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "name": name,
                "instances": instances,
            }
        )

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.service_instance import ServiceInstance

        d = dict(src_dict)
        name = d.pop("name")

        instances = []
        _instances = d.pop("instances")
        for instances_item_data in _instances:
            instances_item = ServiceInstance.from_dict(instances_item_data)

            instances.append(instances_item)

        about_service = cls(
            name=name,
            instances=instances,
        )

        about_service.additional_properties = d
        return about_service

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
