from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateQAEntryDTO")


@_attrs_define
class UpdateQAEntryDTO:
    """
    Attributes:
        id (str):
        question (str):
        answer (str):
        used_text (str | Unset):
        educational_level (str | Unset):
        reviewed (bool | Unset):
    """

    id: str
    question: str
    answer: str
    used_text: str | Unset = UNSET
    educational_level: str | Unset = UNSET
    reviewed: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        question = self.question

        answer = self.answer

        used_text = self.used_text

        educational_level = self.educational_level

        reviewed = self.reviewed

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "question": question,
                "answer": answer,
            }
        )
        if used_text is not UNSET:
            field_dict["usedText"] = used_text
        if educational_level is not UNSET:
            field_dict["educationalLevel"] = educational_level
        if reviewed is not UNSET:
            field_dict["reviewed"] = reviewed

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        question = d.pop("question")

        answer = d.pop("answer")

        used_text = d.pop("usedText", UNSET)

        educational_level = d.pop("educationalLevel", UNSET)

        reviewed = d.pop("reviewed", UNSET)

        update_qa_entry_dto = cls(
            id=id,
            question=question,
            answer=answer,
            used_text=used_text,
            educational_level=educational_level,
            reviewed=reviewed,
        )

        update_qa_entry_dto.additional_properties = d
        return update_qa_entry_dto

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
