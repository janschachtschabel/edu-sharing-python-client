from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Suggest")


@_attrs_define
class Suggest:
    """
    Attributes:
        text (str): suggested text
        score (float): score of the suggestion
        highlighted (str | Unset): suggested text with corrected words highlighted
    """

    text: str
    score: float
    highlighted: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        text = self.text

        score = self.score

        highlighted = self.highlighted

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "text": text,
                "score": score,
            }
        )
        if highlighted is not UNSET:
            field_dict["highlighted"] = highlighted

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        text = d.pop("text")

        score = d.pop("score")

        highlighted = d.pop("highlighted", UNSET)

        suggest = cls(
            text=text,
            score=score,
            highlighted=highlighted,
        )

        suggest.additional_properties = d
        return suggest

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
