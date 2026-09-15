from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.node_version_properties import NodeVersionProperties
    from ..models.node_version_ref import NodeVersionRef
    from ..models.person import Person


T = TypeVar("T", bound="NodeVersion")


@_attrs_define
class NodeVersion:
    """
    Attributes:
        version (NodeVersionRef):
        comment (str):
        modified_at (str):
        modified_by (Person): Owner of the node
        content_url (str | Unset):
        properties (NodeVersionProperties | Unset):
    """

    version: NodeVersionRef
    comment: str
    modified_at: str
    modified_by: Person
    content_url: str | Unset = UNSET
    properties: NodeVersionProperties | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version = self.version.to_dict()

        comment = self.comment

        modified_at = self.modified_at

        modified_by = self.modified_by.to_dict()

        content_url = self.content_url

        properties: dict[str, Any] | Unset = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "version": version,
                "comment": comment,
                "modifiedAt": modified_at,
                "modifiedBy": modified_by,
            }
        )
        if content_url is not UNSET:
            field_dict["contentUrl"] = content_url
        if properties is not UNSET:
            field_dict["properties"] = properties

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.node_version_properties import NodeVersionProperties
        from ..models.node_version_ref import NodeVersionRef
        from ..models.person import Person

        d = dict(src_dict)
        version = NodeVersionRef.from_dict(d.pop("version"))

        comment = d.pop("comment")

        modified_at = d.pop("modifiedAt")

        modified_by = Person.from_dict(d.pop("modifiedBy"))

        content_url = d.pop("contentUrl", UNSET)

        _properties = d.pop("properties", UNSET)
        properties: NodeVersionProperties | Unset
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = NodeVersionProperties.from_dict(_properties)

        node_version = cls(
            version=version,
            comment=comment,
            modified_at=modified_at,
            modified_by=modified_by,
            content_url=content_url,
            properties=properties,
        )

        node_version.additional_properties = d
        return node_version

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
