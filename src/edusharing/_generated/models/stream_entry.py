from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node import Node
    from ..models.stream_entry_properties import StreamEntryProperties
    from ..models.user_simple import UserSimple


T = TypeVar("T", bound="StreamEntry")


@_attrs_define
class StreamEntry:
    """
    Attributes:
        id (str | Unset):
        description (str | Unset):
        nodes (list[Node] | Unset):
        properties (StreamEntryProperties | Unset):
        priority (int | Unset):
        author (UserSimple | Unset):
        created (int | Unset):
        modified (int | Unset):
    """

    id: str | Unset = UNSET
    description: str | Unset = UNSET
    nodes: list[Node] | Unset = UNSET
    properties: StreamEntryProperties | Unset = UNSET
    priority: int | Unset = UNSET
    author: UserSimple | Unset = UNSET
    created: int | Unset = UNSET
    modified: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        description = self.description

        nodes: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.nodes, Unset):
            nodes = []
            for nodes_item_data in self.nodes:
                nodes_item = nodes_item_data.to_dict()
                nodes.append(nodes_item)

        properties: dict[str, Any] | Unset = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        priority = self.priority

        author: dict[str, Any] | Unset = UNSET
        if not isinstance(self.author, Unset):
            author = self.author.to_dict()

        created = self.created

        modified = self.modified

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if description is not UNSET:
            field_dict["description"] = description
        if nodes is not UNSET:
            field_dict["nodes"] = nodes
        if properties is not UNSET:
            field_dict["properties"] = properties
        if priority is not UNSET:
            field_dict["priority"] = priority
        if author is not UNSET:
            field_dict["author"] = author
        if created is not UNSET:
            field_dict["created"] = created
        if modified is not UNSET:
            field_dict["modified"] = modified

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node import Node
        from ..models.stream_entry_properties import StreamEntryProperties
        from ..models.user_simple import UserSimple

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        description = d.pop("description", UNSET)

        _nodes = d.pop("nodes", UNSET)
        nodes: list[Node] | Unset = UNSET
        if _nodes is not UNSET:
            nodes = []
            for nodes_item_data in _nodes:
                nodes_item = Node.from_dict(nodes_item_data)

                nodes.append(nodes_item)

        _properties = d.pop("properties", UNSET)
        properties: StreamEntryProperties | Unset
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = StreamEntryProperties.from_dict(_properties)

        priority = d.pop("priority", UNSET)

        _author = d.pop("author", UNSET)
        author: UserSimple | Unset
        if isinstance(_author, Unset):
            author = UNSET
        else:
            author = UserSimple.from_dict(_author)

        created = d.pop("created", UNSET)

        modified = d.pop("modified", UNSET)

        stream_entry = cls(
            id=id,
            description=description,
            nodes=nodes,
            properties=properties,
            priority=priority,
            author=author,
            created=created,
            modified=modified,
        )

        stream_entry.additional_properties = d
        return stream_entry

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
