from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MenuEntry")


@_attrs_define
class MenuEntry:
    """Additional custom menu entries in left sidebar (position, icon, name, URL/path, scope, etc.)

    Attributes:
        position (int | Unset): Position in menu (negative = count from end)
        icon (str | Unset): Material Design icon identifier
        name (str | Unset): Display name (can include language translation strings)
        url (str | Unset): URL to open on click
        is_disabled (bool | Unset): If true, display grayed out with no function
        open_in_new (bool | Unset): If true (default), open link in new tab
        is_separate (bool | Unset): If true, separate with line above
        is_separate_bottom (bool | Unset): If true, separate with line below
        only_desktop (bool | Unset): If true, only visible on desktop
        only_web (bool | Unset): If true (default: false), hide in Cordova apps
        path (str | Unset): Internal path (e.g. 'workspace', 'collections?scope=EDU_ALL'). Used instead of url for
            internal navigation
        scope (str | Unset): Scope for highlighting (e.g. 'workspace')
    """

    position: int | Unset = UNSET
    icon: str | Unset = UNSET
    name: str | Unset = UNSET
    url: str | Unset = UNSET
    is_disabled: bool | Unset = UNSET
    open_in_new: bool | Unset = UNSET
    is_separate: bool | Unset = UNSET
    is_separate_bottom: bool | Unset = UNSET
    only_desktop: bool | Unset = UNSET
    only_web: bool | Unset = UNSET
    path: str | Unset = UNSET
    scope: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        position = self.position

        icon = self.icon

        name = self.name

        url = self.url

        is_disabled = self.is_disabled

        open_in_new = self.open_in_new

        is_separate = self.is_separate

        is_separate_bottom = self.is_separate_bottom

        only_desktop = self.only_desktop

        only_web = self.only_web

        path = self.path

        scope = self.scope

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if position is not UNSET:
            field_dict["position"] = position
        if icon is not UNSET:
            field_dict["icon"] = icon
        if name is not UNSET:
            field_dict["name"] = name
        if url is not UNSET:
            field_dict["url"] = url
        if is_disabled is not UNSET:
            field_dict["isDisabled"] = is_disabled
        if open_in_new is not UNSET:
            field_dict["openInNew"] = open_in_new
        if is_separate is not UNSET:
            field_dict["isSeparate"] = is_separate
        if is_separate_bottom is not UNSET:
            field_dict["isSeparateBottom"] = is_separate_bottom
        if only_desktop is not UNSET:
            field_dict["onlyDesktop"] = only_desktop
        if only_web is not UNSET:
            field_dict["onlyWeb"] = only_web
        if path is not UNSET:
            field_dict["path"] = path
        if scope is not UNSET:
            field_dict["scope"] = scope

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        position = d.pop("position", UNSET)

        icon = d.pop("icon", UNSET)

        name = d.pop("name", UNSET)

        url = d.pop("url", UNSET)

        is_disabled = d.pop("isDisabled", UNSET)

        open_in_new = d.pop("openInNew", UNSET)

        is_separate = d.pop("isSeparate", UNSET)

        is_separate_bottom = d.pop("isSeparateBottom", UNSET)

        only_desktop = d.pop("onlyDesktop", UNSET)

        only_web = d.pop("onlyWeb", UNSET)

        path = d.pop("path", UNSET)

        scope = d.pop("scope", UNSET)

        menu_entry = cls(
            position=position,
            icon=icon,
            name=name,
            url=url,
            is_disabled=is_disabled,
            open_in_new=open_in_new,
            is_separate=is_separate,
            is_separate_bottom=is_separate_bottom,
            only_desktop=only_desktop,
            only_web=only_web,
            path=path,
            scope=scope,
        )

        menu_entry.additional_properties = d
        return menu_entry

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
