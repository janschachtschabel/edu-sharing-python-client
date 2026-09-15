from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.user_simple import UserSimple


T = TypeVar("T", bound="QAEntryResponseDTO")


@_attrs_define
class QAEntryResponseDTO:
    """
    Attributes:
        id (str):
        node_id (str):
        question (str):
        answer (str):
        created (datetime.datetime):
        created_by (UserSimple):
        modified (bool):
        used_text (str | Unset):
        educational_level (str | Unset):
        last_reviewed (datetime.datetime | Unset):
        reviewed_by (UserSimple | Unset):
    """

    id: str
    node_id: str
    question: str
    answer: str
    created: datetime.datetime
    created_by: UserSimple
    modified: bool
    used_text: str | Unset = UNSET
    educational_level: str | Unset = UNSET
    last_reviewed: datetime.datetime | Unset = UNSET
    reviewed_by: UserSimple | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        node_id = self.node_id

        question = self.question

        answer = self.answer

        created = self.created.isoformat()

        created_by = self.created_by.to_dict()

        modified = self.modified

        used_text = self.used_text

        educational_level = self.educational_level

        last_reviewed: str | Unset = UNSET
        if not isinstance(self.last_reviewed, Unset):
            last_reviewed = self.last_reviewed.isoformat()

        reviewed_by: dict[str, Any] | Unset = UNSET
        if not isinstance(self.reviewed_by, Unset):
            reviewed_by = self.reviewed_by.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "nodeId": node_id,
                "question": question,
                "answer": answer,
                "created": created,
                "createdBy": created_by,
                "modified": modified,
            }
        )
        if used_text is not UNSET:
            field_dict["usedText"] = used_text
        if educational_level is not UNSET:
            field_dict["educationalLevel"] = educational_level
        if last_reviewed is not UNSET:
            field_dict["lastReviewed"] = last_reviewed
        if reviewed_by is not UNSET:
            field_dict["reviewedBy"] = reviewed_by

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.user_simple import UserSimple

        d = dict(src_dict)
        id = d.pop("id")

        node_id = d.pop("nodeId")

        question = d.pop("question")

        answer = d.pop("answer")

        created = datetime.datetime.fromisoformat(d.pop("created"))

        created_by = UserSimple.from_dict(d.pop("createdBy"))

        modified = d.pop("modified")

        used_text = d.pop("usedText", UNSET)

        educational_level = d.pop("educationalLevel", UNSET)

        _last_reviewed = d.pop("lastReviewed", UNSET)
        last_reviewed: datetime.datetime | Unset
        if isinstance(_last_reviewed, Unset):
            last_reviewed = UNSET
        else:
            last_reviewed = datetime.datetime.fromisoformat(_last_reviewed)

        _reviewed_by = d.pop("reviewedBy", UNSET)
        reviewed_by: UserSimple | Unset
        if isinstance(_reviewed_by, Unset):
            reviewed_by = UNSET
        else:
            reviewed_by = UserSimple.from_dict(_reviewed_by)

        qa_entry_response_dto = cls(
            id=id,
            node_id=node_id,
            question=question,
            answer=answer,
            created=created,
            created_by=created_by,
            modified=modified,
            used_text=used_text,
            educational_level=educational_level,
            last_reviewed=last_reviewed,
            reviewed_by=reviewed_by,
        )

        qa_entry_response_dto.additional_properties = d
        return qa_entry_response_dto

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
