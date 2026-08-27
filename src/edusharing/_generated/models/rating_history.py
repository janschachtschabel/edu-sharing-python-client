from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rating_data import RatingData
    from ..models.rating_history_affiliation import RatingHistoryAffiliation


T = TypeVar("T", bound="RatingHistory")


@_attrs_define
class RatingHistory:
    """
    Attributes:
        overall (RatingData | Unset):
        affiliation (RatingHistoryAffiliation | Unset):
        timestamp (str | Unset):
    """

    overall: RatingData | Unset = UNSET
    affiliation: RatingHistoryAffiliation | Unset = UNSET
    timestamp: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        overall: dict[str, Any] | Unset = UNSET
        if not isinstance(self.overall, Unset):
            overall = self.overall.to_dict()

        affiliation: dict[str, Any] | Unset = UNSET
        if not isinstance(self.affiliation, Unset):
            affiliation = self.affiliation.to_dict()

        timestamp = self.timestamp

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if overall is not UNSET:
            field_dict["overall"] = overall
        if affiliation is not UNSET:
            field_dict["affiliation"] = affiliation
        if timestamp is not UNSET:
            field_dict["timestamp"] = timestamp

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.rating_data import RatingData
        from ..models.rating_history_affiliation import RatingHistoryAffiliation

        d = dict(src_dict)
        _overall = d.pop("overall", UNSET)
        overall: RatingData | Unset
        if isinstance(_overall, Unset):
            overall = UNSET
        else:
            overall = RatingData.from_dict(_overall)

        _affiliation = d.pop("affiliation", UNSET)
        affiliation: RatingHistoryAffiliation | Unset
        if isinstance(_affiliation, Unset):
            affiliation = UNSET
        else:
            affiliation = RatingHistoryAffiliation.from_dict(_affiliation)

        timestamp = d.pop("timestamp", UNSET)

        rating_history = cls(
            overall=overall,
            affiliation=affiliation,
            timestamp=timestamp,
        )

        rating_history.additional_properties = d
        return rating_history

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
