from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.admin_editor_type import AdminEditorType
from ..models.admin_wysiwyg_type import AdminWysiwygType
from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.statistics import Statistics


T = TypeVar("T", bound="Admin")


@_attrs_define
class Admin:
    """Admin panel configuration

    Attributes:
        statistics (Statistics | Unset):
        editor_type (AdminEditorType | Unset): Code editor type for config file editing: Textarea or Monaco
        wysiwyg_type (AdminWysiwygType | Unset): WYSIWYG editor type for message editing: Textarea or TinyMCE
    """

    statistics: Statistics | Unset = UNSET
    editor_type: AdminEditorType | Unset = UNSET
    wysiwyg_type: AdminWysiwygType | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        statistics: dict[str, Any] | Unset = UNSET
        if not isinstance(self.statistics, Unset):
            statistics = self.statistics.to_dict()

        editor_type: str | Unset = UNSET
        if not isinstance(self.editor_type, Unset):
            editor_type = self.editor_type.value

        wysiwyg_type: str | Unset = UNSET
        if not isinstance(self.wysiwyg_type, Unset):
            wysiwyg_type = self.wysiwyg_type.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if statistics is not UNSET:
            field_dict["statistics"] = statistics
        if editor_type is not UNSET:
            field_dict["editorType"] = editor_type
        if wysiwyg_type is not UNSET:
            field_dict["wysiwygType"] = wysiwyg_type

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.statistics import Statistics

        d = dict(src_dict)
        _statistics = d.pop("statistics", UNSET)
        statistics: Statistics | Unset
        if isinstance(_statistics, Unset):
            statistics = UNSET
        else:
            statistics = Statistics.from_dict(_statistics)

        _editor_type = d.pop("editorType", UNSET)
        editor_type: AdminEditorType | Unset
        if isinstance(_editor_type, Unset):
            editor_type = UNSET
        else:
            editor_type = AdminEditorType(_editor_type)

        _wysiwyg_type = d.pop("wysiwygType", UNSET)
        wysiwyg_type: AdminWysiwygType | Unset
        if isinstance(_wysiwyg_type, Unset):
            wysiwyg_type = UNSET
        else:
            wysiwyg_type = AdminWysiwygType(_wysiwyg_type)

        admin = cls(
            statistics=statistics,
            editor_type=editor_type,
            wysiwyg_type=wysiwyg_type,
        )

        admin.additional_properties = d
        return admin

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
