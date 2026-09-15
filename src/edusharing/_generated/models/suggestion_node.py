from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.suggestion_node_status import SuggestionNodeStatus
from ..models.suggestion_node_type import SuggestionNodeType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_simple import UserSimple


T = TypeVar("T", bound="SuggestionNode")


@_attrs_define
class SuggestionNode:
    """
    Attributes:
        id (str | Unset):
        type_ (SuggestionNodeType | Unset): Type of the suggestion
        status (SuggestionNodeStatus | Unset):
        property_id (str | Unset):
        value (str | Unset):
        version (str | Unset):
        description (str | Unset):
        created_by (UserSimple | Unset):
        created (datetime.datetime | Unset):
    """

    id: str | Unset = UNSET
    type_: SuggestionNodeType | Unset = UNSET
    status: SuggestionNodeStatus | Unset = UNSET
    property_id: str | Unset = UNSET
    value: str | Unset = UNSET
    version: str | Unset = UNSET
    description: str | Unset = UNSET
    created_by: UserSimple | Unset = UNSET
    created: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        type_: str | Unset = UNSET
        if not isinstance(self.type_, Unset):
            type_ = self.type_.value

        status: str | Unset = UNSET
        if not isinstance(self.status, Unset):
            status = self.status.value

        property_id = self.property_id

        value = self.value

        version = self.version

        description = self.description

        created_by: dict[str, Any] | Unset = UNSET
        if not isinstance(self.created_by, Unset):
            created_by = self.created_by.to_dict()

        created: str | Unset = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if type_ is not UNSET:
            field_dict["type"] = type_
        if status is not UNSET:
            field_dict["status"] = status
        if property_id is not UNSET:
            field_dict["propertyId"] = property_id
        if value is not UNSET:
            field_dict["value"] = value
        if version is not UNSET:
            field_dict["version"] = version
        if description is not UNSET:
            field_dict["description"] = description
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if created is not UNSET:
            field_dict["created"] = created

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.user_simple import UserSimple

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        _type_ = d.pop("type", UNSET)
        type_: SuggestionNodeType | Unset
        if isinstance(_type_, Unset):
            type_ = UNSET
        else:
            type_ = SuggestionNodeType(_type_)

        _status = d.pop("status", UNSET)
        status: SuggestionNodeStatus | Unset
        if isinstance(_status, Unset):
            status = UNSET
        else:
            status = SuggestionNodeStatus(_status)

        property_id = d.pop("propertyId", UNSET)

        value = d.pop("value", UNSET)

        version = d.pop("version", UNSET)

        description = d.pop("description", UNSET)

        _created_by = d.pop("createdBy", UNSET)
        created_by: UserSimple | Unset
        if isinstance(_created_by, Unset):
            created_by = UNSET
        else:
            created_by = UserSimple.from_dict(_created_by)

        _created = d.pop("created", UNSET)
        created: datetime.datetime | Unset
        if isinstance(_created, Unset):
            created = UNSET
        else:
            created = datetime.datetime.fromisoformat(_created)

        suggestion_node = cls(
            id=id,
            type_=type_,
            status=status,
            property_id=property_id,
            value=value,
            version=version,
            description=description,
            created_by=created_by,
            created=created,
        )

        suggestion_node.additional_properties = d
        return suggestion_node

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
