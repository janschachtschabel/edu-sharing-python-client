from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="FontIcon")


@_attrs_define
class FontIcon:
    """Array of icon identifier replacements (original identifier, replace with)

    Attributes:
        original (str | Unset): Original Material Design icon identifier to replace
        context (str | Unset): Context in which this replacement applies, as a regular expression matched against the
            whole context reported by the frontend (a plain string therefore acts as an exact match, e.g. 'mds', 'option',
            'collection-scope'; 'sidebar-.*' matches all sidebar contexts). Icons that report no context are matched against
            the empty string, so '.*' also covers them while '.+' requires a context; '(?!edge-toggle$|sidebar-navigate$).*'
            applies everywhere except those two contexts. Empty/null = applies to all contexts, but such an entry is only
            used if no entry with a matching context exists. If several entries match, the first one in the list wins
        replace (str | Unset): Replacement icon identifier or CSS class
        css_class (str | Unset): CSS class name
    """

    original: str | Unset = UNSET
    context: str | Unset = UNSET
    replace: str | Unset = UNSET
    css_class: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        original = self.original

        context = self.context

        replace = self.replace

        css_class = self.css_class

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if original is not UNSET:
            field_dict["original"] = original
        if context is not UNSET:
            field_dict["context"] = context
        if replace is not UNSET:
            field_dict["replace"] = replace
        if css_class is not UNSET:
            field_dict["cssClass"] = css_class

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        original = d.pop("original", UNSET)

        context = d.pop("context", UNSET)

        replace = d.pop("replace", UNSET)

        css_class = d.pop("cssClass", UNSET)

        font_icon = cls(
            original=original,
            context=context,
            replace=replace,
            css_class=css_class,
        )

        font_icon.additional_properties = d
        return font_icon

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
