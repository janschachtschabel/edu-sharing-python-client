from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node import Node


T = TypeVar("T", bound="WebsiteInformation")


@_attrs_define
class WebsiteInformation:
    """
    Attributes:
        title (str | Unset):
        page (str | Unset):
        description (str | Unset):
        license_ (str | Unset):
        keywords (list[str] | Unset):
        duplicate_nodes (list[Node] | Unset):
    """

    title: str | Unset = UNSET
    page: str | Unset = UNSET
    description: str | Unset = UNSET
    license_: str | Unset = UNSET
    keywords: list[str] | Unset = UNSET
    duplicate_nodes: list[Node] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        title = self.title

        page = self.page

        description = self.description

        license_ = self.license_

        keywords: list[str] | Unset = UNSET
        if not isinstance(self.keywords, Unset):
            keywords = self.keywords

        duplicate_nodes: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.duplicate_nodes, Unset):
            duplicate_nodes = []
            for duplicate_nodes_item_data in self.duplicate_nodes:
                duplicate_nodes_item = duplicate_nodes_item_data.to_dict()
                duplicate_nodes.append(duplicate_nodes_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if title is not UNSET:
            field_dict["title"] = title
        if page is not UNSET:
            field_dict["page"] = page
        if description is not UNSET:
            field_dict["description"] = description
        if license_ is not UNSET:
            field_dict["license"] = license_
        if keywords is not UNSET:
            field_dict["keywords"] = keywords
        if duplicate_nodes is not UNSET:
            field_dict["duplicateNodes"] = duplicate_nodes

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node import Node

        d = dict(src_dict)
        title = d.pop("title", UNSET)

        page = d.pop("page", UNSET)

        description = d.pop("description", UNSET)

        license_ = d.pop("license", UNSET)

        keywords = cast(list[str], d.pop("keywords", UNSET))

        _duplicate_nodes = d.pop("duplicateNodes", UNSET)
        duplicate_nodes: list[Node] | Unset = UNSET
        if _duplicate_nodes is not UNSET:
            duplicate_nodes = []
            for duplicate_nodes_item_data in _duplicate_nodes:
                duplicate_nodes_item = Node.from_dict(duplicate_nodes_item_data)

                duplicate_nodes.append(duplicate_nodes_item)

        website_information = cls(
            title=title,
            page=page,
            description=description,
            license_=license_,
            keywords=keywords,
            duplicate_nodes=duplicate_nodes,
        )

        website_information.additional_properties = d
        return website_information

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
