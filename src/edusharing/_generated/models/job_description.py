from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.job_description_tags_item import JobDescriptionTagsItem
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.job_field_description import JobFieldDescription


T = TypeVar("T", bound="JobDescription")


@_attrs_define
class JobDescription:
    """
    Attributes:
        name (str | Unset):
        description (str | Unset):
        params (list[JobFieldDescription] | Unset):
        tags (list[JobDescriptionTagsItem] | Unset):
    """

    name: str | Unset = UNSET
    description: str | Unset = UNSET
    params: list[JobFieldDescription] | Unset = UNSET
    tags: list[JobDescriptionTagsItem] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        name = self.name

        description = self.description

        params: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.params, Unset):
            params = []
            for params_item_data in self.params:
                params_item = params_item_data.to_dict()
                params.append(params_item)

        tags: list[str] | Unset = UNSET
        if not isinstance(self.tags, Unset):
            tags = []
            for tags_item_data in self.tags:
                tags_item = tags_item_data.value
                tags.append(tags_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if name is not UNSET:
            field_dict["name"] = name
        if description is not UNSET:
            field_dict["description"] = description
        if params is not UNSET:
            field_dict["params"] = params
        if tags is not UNSET:
            field_dict["tags"] = tags

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.job_field_description import JobFieldDescription

        d = dict(src_dict)
        name = d.pop("name", UNSET)

        description = d.pop("description", UNSET)

        _params = d.pop("params", UNSET)
        params: list[JobFieldDescription] | Unset = UNSET
        if _params is not UNSET:
            params = []
            for params_item_data in _params:
                params_item = JobFieldDescription.from_dict(params_item_data)

                params.append(params_item)

        _tags = d.pop("tags", UNSET)
        tags: list[JobDescriptionTagsItem] | Unset = UNSET
        if _tags is not UNSET:
            tags = []
            for tags_item_data in _tags:
                tags_item = JobDescriptionTagsItem(tags_item_data)

                tags.append(tags_item)

        job_description = cls(
            name=name,
            description=description,
            params=params,
            tags=tags,
        )

        job_description.additional_properties = d
        return job_description

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
