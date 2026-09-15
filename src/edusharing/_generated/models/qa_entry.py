from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="QAEntry")


@_attrs_define
class QAEntry:
    """
    Attributes:
        id (str | Unset):
        node_id (str | Unset):
        question (str | Unset):
        answer (str | Unset):
        used_text (str | Unset):
        educational_level (str | Unset):
        created (datetime.datetime | Unset):
        created_by (str | Unset):
        last_reviewed (datetime.datetime | Unset):
        reviewed_by (str | Unset):
        edited (bool | Unset):
    """

    id: str | Unset = UNSET
    node_id: str | Unset = UNSET
    question: str | Unset = UNSET
    answer: str | Unset = UNSET
    used_text: str | Unset = UNSET
    educational_level: str | Unset = UNSET
    created: datetime.datetime | Unset = UNSET
    created_by: str | Unset = UNSET
    last_reviewed: datetime.datetime | Unset = UNSET
    reviewed_by: str | Unset = UNSET
    edited: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        node_id = self.node_id

        question = self.question

        answer = self.answer

        used_text = self.used_text

        educational_level = self.educational_level

        created: str | Unset = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        created_by = self.created_by

        last_reviewed: str | Unset = UNSET
        if not isinstance(self.last_reviewed, Unset):
            last_reviewed = self.last_reviewed.isoformat()

        reviewed_by = self.reviewed_by

        edited = self.edited

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if node_id is not UNSET:
            field_dict["nodeId"] = node_id
        if question is not UNSET:
            field_dict["question"] = question
        if answer is not UNSET:
            field_dict["answer"] = answer
        if used_text is not UNSET:
            field_dict["usedText"] = used_text
        if educational_level is not UNSET:
            field_dict["educationalLevel"] = educational_level
        if created is not UNSET:
            field_dict["created"] = created
        if created_by is not UNSET:
            field_dict["createdBy"] = created_by
        if last_reviewed is not UNSET:
            field_dict["lastReviewed"] = last_reviewed
        if reviewed_by is not UNSET:
            field_dict["reviewedBy"] = reviewed_by
        if edited is not UNSET:
            field_dict["edited"] = edited

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        node_id = d.pop("nodeId", UNSET)

        question = d.pop("question", UNSET)

        answer = d.pop("answer", UNSET)

        used_text = d.pop("usedText", UNSET)

        educational_level = d.pop("educationalLevel", UNSET)

        _created = d.pop("created", UNSET)
        created: datetime.datetime | Unset
        if isinstance(_created, Unset):
            created = UNSET
        else:
            created = datetime.datetime.fromisoformat(_created)

        created_by = d.pop("createdBy", UNSET)

        _last_reviewed = d.pop("lastReviewed", UNSET)
        last_reviewed: datetime.datetime | Unset
        if isinstance(_last_reviewed, Unset):
            last_reviewed = UNSET
        else:
            last_reviewed = datetime.datetime.fromisoformat(_last_reviewed)

        reviewed_by = d.pop("reviewedBy", UNSET)

        edited = d.pop("edited", UNSET)

        qa_entry = cls(
            id=id,
            node_id=node_id,
            question=question,
            answer=answer,
            used_text=used_text,
            educational_level=educational_level,
            created=created,
            created_by=created_by,
            last_reviewed=last_reviewed,
            reviewed_by=reviewed_by,
            edited=edited,
        )

        qa_entry.additional_properties = d
        return qa_entry

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
