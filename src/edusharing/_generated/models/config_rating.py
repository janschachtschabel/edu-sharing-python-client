from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.config_rating_mode import ConfigRatingMode
from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigRating")


@_attrs_define
class ConfigRating:
    """Rating configuration

    Attributes:
        mode (ConfigRatingMode | Unset): Rating display mode: none (disabled), likes (like button), or stars (star
            rating)
    """

    mode: ConfigRatingMode | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        mode: str | Unset = UNSET
        if not isinstance(self.mode, Unset):
            mode = self.mode.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if mode is not UNSET:
            field_dict["mode"] = mode

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _mode = d.pop("mode", UNSET)
        mode: ConfigRatingMode | Unset
        if isinstance(_mode, Unset):
            mode = UNSET
        else:
            mode = ConfigRatingMode(_mode)

        config_rating = cls(
            mode=mode,
        )

        config_rating.additional_properties = d
        return config_rating

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
