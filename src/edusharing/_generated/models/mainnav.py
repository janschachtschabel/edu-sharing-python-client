from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.icon import Icon


T = TypeVar("T", bound="Mainnav")


@_attrs_define
class Mainnav:
    """Top navigation bar customization (icon, URL)

    Attributes:
        icon (Icon | Unset): Navigation icon configuration
        main_menu_style (str | Unset): Main menu style customization
    """

    icon: Icon | Unset = UNSET
    main_menu_style: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        icon: dict[str, Any] | Unset = UNSET
        if not isinstance(self.icon, Unset):
            icon = self.icon.to_dict()

        main_menu_style = self.main_menu_style

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if icon is not UNSET:
            field_dict["icon"] = icon
        if main_menu_style is not UNSET:
            field_dict["mainMenuStyle"] = main_menu_style

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.icon import Icon

        d = dict(src_dict)
        _icon = d.pop("icon", UNSET)
        icon: Icon | Unset
        if isinstance(_icon, Unset):
            icon = UNSET
        else:
            icon = Icon.from_dict(_icon)

        main_menu_style = d.pop("mainMenuStyle", UNSET)

        mainnav = cls(
            icon=icon,
            main_menu_style=main_menu_style,
        )

        mainnav.additional_properties = d
        return mainnav

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
