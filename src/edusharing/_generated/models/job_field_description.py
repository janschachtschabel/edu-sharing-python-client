from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="JobFieldDescription")


@_attrs_define
class JobFieldDescription:
    """
    Attributes:
        name (str | Unset):
        description (str | Unset):
        file (bool | Unset):
        sample_value (str | Unset):
        is_array (bool | Unset):
        array (bool | Unset):
    """

    name: str | Unset = UNSET
    description: str | Unset = UNSET
    file: bool | Unset = UNSET
    sample_value: str | Unset = UNSET
    is_array: bool | Unset = UNSET
    array: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        file = self.file

        sample_value = self.sample_value

        is_array = self.is_array

        array = self.array

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if file is not UNSET:
            field_dict["file"] = file
        if sample_value is not UNSET:
            field_dict["sampleValue"] = sample_value
        if is_array is not UNSET:
            field_dict["isArray"] = is_array
        if array is not UNSET:
            field_dict["array"] = array

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        file = d.pop("file", UNSET)

        sample_value = d.pop("sampleValue", UNSET)

        is_array = d.pop("isArray", UNSET)

        array = d.pop("array", UNSET)

        job_field_description = cls(
            name=name,
            description=description,
            file=file,
            sample_value=sample_value,
            is_array=is_array,
            array=array,
        )

        job_field_description.additional_properties = d
        return job_field_description

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
