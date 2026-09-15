from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.context_menu_entry_change_strategy import ContextMenuEntryChangeStrategy
from ..models.context_menu_entry_scopes_item import ContextMenuEntryScopesItem
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContextMenuEntry")


@_attrs_define
class ContextMenuEntry:
    """Custom options for the user menu (shown on username click in navigation bar)

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
        mode (str | Unset): When to show: 'nodes' (selected nodes), 'noNodes' (nothing selected), 'noNodesNotEmpty'
            (nothing selected but items available), 'always'
        scopes (list[ContextMenuEntryScopesItem] | Unset): Scopes where option appears (e.g. 'Render', 'Search',
            'WorkspaceList'). Empty = all scopes
        ajax (bool | Unset): If true, call URL via AJAX; if false, open in current window
        group (str | Unset): Option grouping (e.g. 'Create', 'View', 'Edit')
        permission (str | Unset): Only show if node has this permission (e.g. 'Write', 'CCPublish')
        toolpermission (str | Unset): Only show if user has this tool permission
        is_directory (bool | Unset): true = only for folders, false = only for files, null = both
        show_as_action (bool | Unset): If true, show as action in toolbar
        multiple (bool | Unset): If true, action works on multiple selected nodes
        change_strategy (ContextMenuEntryChangeStrategy | Unset): For modifications: 'update' to modify existing option,
            'remove' to delete
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
    mode: str | Unset = UNSET
    scopes: list[ContextMenuEntryScopesItem] | Unset = UNSET
    ajax: bool | Unset = UNSET
    group: str | Unset = UNSET
    permission: str | Unset = UNSET
    toolpermission: str | Unset = UNSET
    is_directory: bool | Unset = UNSET
    show_as_action: bool | Unset = UNSET
    multiple: bool | Unset = UNSET
    change_strategy: ContextMenuEntryChangeStrategy | Unset = UNSET
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

        mode = self.mode

        scopes: list[str] | Unset = UNSET
        if not isinstance(self.scopes, Unset):
            scopes = []
            for scopes_item_data in self.scopes:
                scopes_item = scopes_item_data.value
                scopes.append(scopes_item)

        ajax = self.ajax

        group = self.group

        permission = self.permission

        toolpermission = self.toolpermission

        is_directory = self.is_directory

        show_as_action = self.show_as_action

        multiple = self.multiple

        change_strategy: str | Unset = UNSET
        if not isinstance(self.change_strategy, Unset):
            change_strategy = self.change_strategy.value

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
        if mode is not UNSET:
            field_dict["mode"] = mode
        if scopes is not UNSET:
            field_dict["scopes"] = scopes
        if ajax is not UNSET:
            field_dict["ajax"] = ajax
        if group is not UNSET:
            field_dict["group"] = group
        if permission is not UNSET:
            field_dict["permission"] = permission
        if toolpermission is not UNSET:
            field_dict["toolpermission"] = toolpermission
        if is_directory is not UNSET:
            field_dict["isDirectory"] = is_directory
        if show_as_action is not UNSET:
            field_dict["showAsAction"] = show_as_action
        if multiple is not UNSET:
            field_dict["multiple"] = multiple
        if change_strategy is not UNSET:
            field_dict["changeStrategy"] = change_strategy

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

        mode = d.pop("mode", UNSET)

        _scopes = d.pop("scopes", UNSET)
        scopes: list[ContextMenuEntryScopesItem] | Unset = UNSET
        if _scopes is not UNSET:
            scopes = []
            for scopes_item_data in _scopes:
                scopes_item = ContextMenuEntryScopesItem(scopes_item_data)

                scopes.append(scopes_item)

        ajax = d.pop("ajax", UNSET)

        group = d.pop("group", UNSET)

        permission = d.pop("permission", UNSET)

        toolpermission = d.pop("toolpermission", UNSET)

        is_directory = d.pop("isDirectory", UNSET)

        show_as_action = d.pop("showAsAction", UNSET)

        multiple = d.pop("multiple", UNSET)

        _change_strategy = d.pop("changeStrategy", UNSET)
        change_strategy: ContextMenuEntryChangeStrategy | Unset
        if isinstance(_change_strategy, Unset):
            change_strategy = UNSET
        else:
            change_strategy = ContextMenuEntryChangeStrategy(_change_strategy)

        context_menu_entry = cls(
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
            mode=mode,
            scopes=scopes,
            ajax=ajax,
            group=group,
            permission=permission,
            toolpermission=toolpermission,
            is_directory=is_directory,
            show_as_action=show_as_action,
            multiple=multiple,
            change_strategy=change_strategy,
        )

        context_menu_entry.additional_properties = d
        return context_menu_entry

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
