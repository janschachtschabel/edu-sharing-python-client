from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.property_suggestion_status import PropertySuggestionStatus
from ..models.property_suggestion_type import PropertySuggestionType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.property_suggestion_value import PropertySuggestionValue


T = TypeVar("T", bound="PropertySuggestion")


@_attrs_define
class PropertySuggestion:
    """
    Attributes:
        value (PropertySuggestionValue):
        id (str):
        type_ (PropertySuggestionType): Type of the suggestion
        version (str):
        description (str):
        node_id (str):
        status (PropertySuggestionStatus):
        property_id (str):
        confidence (float | Unset):
        modified (datetime.datetime | Unset):
        modified_by (str | Unset):
        created_by (str | Unset):
        created (datetime.datetime | Unset):
    """

    value: PropertySuggestionValue
    id: str
    type_: PropertySuggestionType
    version: str
    description: str
    node_id: str
    status: PropertySuggestionStatus
    property_id: str
    confidence: float | Unset = UNSET
    modified: datetime.datetime | Unset = UNSET
    modified_by: str | Unset = UNSET
    created_by: str | Unset = UNSET
    created: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        value = self.value.to_dict()

        id = self.id

        type_ = self.type_.value

        version = self.version

        description = self.description

        node_id = self.node_id

        status = self.status.value

        property_id = self.property_id

        confidence = self.confidence

        modified: str | Unset = UNSET
        if not isinstance(self.modified, Unset):
            modified = self.modified.isoformat()

        modified_by = self.modified_by

        created_by = self.created_by

        created: str | Unset = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "value": value,
                "id": id,
                "type": type_,
                "version": version,
                "description": description,
                "nodeId": node_id,
                "status": status,
                "propertyId": property_id,
            }
        )
        if confidence is not UNSET:
            field_dict["confidence"] = confidence
        if modified is not UNSET:
            field_dict["modified"] = modified
        if modified_by is not UNSET:
            field_dict["modifiedBy"] = modified_by
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if created is not UNSET:
            field_dict["created"] = created

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.property_suggestion_value import PropertySuggestionValue

        d = dict(src_dict)
        value = PropertySuggestionValue.from_dict(d.pop("value"))

        id = d.pop("id")

        type_ = PropertySuggestionType(d.pop("type"))

        version = d.pop("version")

        description = d.pop("description")

        node_id = d.pop("nodeId")

        status = PropertySuggestionStatus(d.pop("status"))

        property_id = d.pop("propertyId")

        confidence = d.pop("confidence", UNSET)

        _modified = d.pop("modified", UNSET)
        modified: datetime.datetime | Unset
        if isinstance(_modified, Unset):
            modified = UNSET
        else:
            modified = datetime.datetime.fromisoformat(_modified)

        modified_by = d.pop("modifiedBy", UNSET)

        created_by = d.pop("createdBy", UNSET)

        _created = d.pop("created", UNSET)
        created: datetime.datetime | Unset
        if isinstance(_created, Unset):
            created = UNSET
        else:
            created = datetime.datetime.fromisoformat(_created)

        property_suggestion = cls(
            value=value,
            id=id,
            type_=type_,
            version=version,
            description=description,
            node_id=node_id,
            status=status,
            property_id=property_id,
            confidence=confidence,
            modified=modified,
            modified_by=modified_by,
            created_by=created_by,
            created=created,
        )

        property_suggestion.additional_properties = d
        return property_suggestion

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
