from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.config_theme_color import ConfigThemeColor


T = TypeVar("T", bound="ConfigThemeColors")


@_attrs_define
class ConfigThemeColors:
    """Theme color customization. An entry with no theme attribute (or theme="light") applies to light mode, theme="dark"
    to dark mode. A dark entry is used as-is instead of deriving dark variants from the light colors client-side

        Attributes:
            theme (str | Unset):
            color (list[ConfigThemeColor] | Unset):
            color_safe (list[ConfigThemeColor] | Unset):
    """

    theme: str | Unset = UNSET
    color: list[ConfigThemeColor] | Unset = UNSET
    color_safe: list[ConfigThemeColor] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        theme = self.theme

        color: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.color, Unset):
            color = []
            for color_item_data in self.color:
                color_item = color_item_data.to_dict()
                color.append(color_item)

        color_safe: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.color_safe, Unset):
            color_safe = []
            for color_safe_item_data in self.color_safe:
                color_safe_item = color_safe_item_data.to_dict()
                color_safe.append(color_safe_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if theme is not UNSET:
            field_dict["theme"] = theme
        if color is not UNSET:
            field_dict["color"] = color
        if color_safe is not UNSET:
            field_dict["colorSafe"] = color_safe

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.config_theme_color import ConfigThemeColor

        d = dict(src_dict)
        theme = d.pop("theme", UNSET)

        _color = d.pop("color", UNSET)
        color: list[ConfigThemeColor] | Unset = UNSET
        if _color is not UNSET:
            color = []
            for color_item_data in _color:
                color_item = ConfigThemeColor.from_dict(color_item_data)

                color.append(color_item)

        _color_safe = d.pop("colorSafe", UNSET)
        color_safe: list[ConfigThemeColor] | Unset = UNSET
        if _color_safe is not UNSET:
            color_safe = []
            for color_safe_item_data in _color_safe:
                color_safe_item = ConfigThemeColor.from_dict(color_safe_item_data)

                color_safe.append(color_safe_item)

        config_theme_colors = cls(
            theme=theme,
            color=color,
            color_safe=color_safe,
        )

        config_theme_colors.additional_properties = d
        return config_theme_colors

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
