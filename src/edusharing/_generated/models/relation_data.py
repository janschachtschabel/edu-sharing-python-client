from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.relation_data_reverse_type import RelationDataReverseType
from ..models.relation_data_type import RelationDataType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.evaluation import Evaluation
    from ..models.relation_data_metadata import RelationDataMetadata


T = TypeVar("T", bound="RelationData")


@_attrs_define
class RelationData:
    """
    Attributes:
        type_ (RelationDataType):
        created_by (str):
        to_node (str):
        ai_generated (bool):
        from_node (str):
        reverse_type (RelationDataReverseType):
        created_at (datetime.datetime):
        modified_at (datetime.datetime | Unset):
        evaluation (Evaluation | Unset):
        modified_by (str | Unset):
        metadata (RelationDataMetadata | Unset):
    """

    type_: RelationDataType
    created_by: str
    to_node: str
    ai_generated: bool
    from_node: str
    reverse_type: RelationDataReverseType
    created_at: datetime.datetime
    modified_at: datetime.datetime | Unset = UNSET
    evaluation: Evaluation | Unset = UNSET
    modified_by: str | Unset = UNSET
    metadata: RelationDataMetadata | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_.value

        created_by = self.created_by

        to_node = self.to_node

        ai_generated = self.ai_generated

        from_node = self.from_node

        reverse_type = self.reverse_type.value

        created_at = self.created_at.isoformat()

        modified_at: str | Unset = UNSET
        if not isinstance(self.modified_at, Unset):
            modified_at = self.modified_at.isoformat()

        evaluation: dict[str, Any] | Unset = UNSET
        if not isinstance(self.evaluation, Unset):
            evaluation = self.evaluation.to_dict()

        modified_by = self.modified_by

        metadata: dict[str, Any] | Unset = UNSET
        if not isinstance(self.metadata, Unset):
            metadata = self.metadata.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "type": type_,
                "createdBy": created_by,
                "toNode": to_node,
                "aiGenerated": ai_generated,
                "fromNode": from_node,
                "reverseType": reverse_type,
                "createdAt": created_at,
            }
        )
        if modified_at is not UNSET:
            field_dict["modifiedAt"] = modified_at
        if evaluation is not UNSET:
            field_dict["evaluation"] = evaluation
        if modified_by is not UNSET:
            field_dict["modifiedBy"] = modified_by
        if metadata is not UNSET:
            field_dict["metadata"] = metadata

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.evaluation import Evaluation
        from ..models.relation_data_metadata import RelationDataMetadata

        d = dict(src_dict)
        type_ = RelationDataType(d.pop("type"))

        created_by = d.pop("createdBy")

        to_node = d.pop("toNode")

        ai_generated = d.pop("aiGenerated")

        from_node = d.pop("fromNode")

        reverse_type = RelationDataReverseType(d.pop("reverseType"))

        created_at = datetime.datetime.fromisoformat(d.pop("createdAt"))

        _modified_at = d.pop("modifiedAt", UNSET)
        modified_at: datetime.datetime | Unset
        if isinstance(_modified_at, Unset):
            modified_at = UNSET
        else:
            modified_at = datetime.datetime.fromisoformat(_modified_at)

        _evaluation = d.pop("evaluation", UNSET)
        evaluation: Evaluation | Unset
        if isinstance(_evaluation, Unset):
            evaluation = UNSET
        else:
            evaluation = Evaluation.from_dict(_evaluation)

        modified_by = d.pop("modifiedBy", UNSET)

        _metadata = d.pop("metadata", UNSET)
        metadata: RelationDataMetadata | Unset
        if isinstance(_metadata, Unset):
            metadata = UNSET
        else:
            metadata = RelationDataMetadata.from_dict(_metadata)

        relation_data = cls(
            type_=type_,
            created_by=created_by,
            to_node=to_node,
            ai_generated=ai_generated,
            from_node=from_node,
            reverse_type=reverse_type,
            created_at=created_at,
            modified_at=modified_at,
            evaluation=evaluation,
            modified_by=modified_by,
            metadata=metadata,
        )

        relation_data.additional_properties = d
        return relation_data

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
