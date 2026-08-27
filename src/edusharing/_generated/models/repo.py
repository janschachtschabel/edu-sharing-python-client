from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Repo")


@_attrs_define
class Repo:
    """
    Attributes:
        id (str | Unset):
        is_home_repo (bool | Unset):
        title (str | Unset):
        repository_type (str | Unset):
        icon (str | Unset):
        logo (str | Unset):
        rendering_supported (bool | Unset):
    """

    id: str | Unset = UNSET
    is_home_repo: bool | Unset = UNSET
    title: str | Unset = UNSET
    repository_type: str | Unset = UNSET
    icon: str | Unset = UNSET
    logo: str | Unset = UNSET
    rendering_supported: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        is_home_repo = self.is_home_repo

        title = self.title

        repository_type = self.repository_type

        icon = self.icon

        logo = self.logo

        rendering_supported = self.rendering_supported

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if is_home_repo is not UNSET:
            field_dict["isHomeRepo"] = is_home_repo
        if title is not UNSET:
            field_dict["title"] = title
        if repository_type is not UNSET:
            field_dict["repositoryType"] = repository_type
        if icon is not UNSET:
            field_dict["icon"] = icon
        if logo is not UNSET:
            field_dict["logo"] = logo
        if rendering_supported is not UNSET:
            field_dict["renderingSupported"] = rendering_supported

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        is_home_repo = d.pop("isHomeRepo", UNSET)

        title = d.pop("title", UNSET)

        repository_type = d.pop("repositoryType", UNSET)

        icon = d.pop("icon", UNSET)

        logo = d.pop("logo", UNSET)

        rendering_supported = d.pop("renderingSupported", UNSET)

        repo = cls(
            id=id,
            is_home_repo=is_home_repo,
            title=title,
            repository_type=repository_type,
            icon=icon,
            logo=logo,
            rendering_supported=rendering_supported,
        )

        repo.additional_properties = d
        return repo

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
