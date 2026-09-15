from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.language_current import LanguageCurrent
    from ..models.language_global import LanguageGlobal


T = TypeVar("T", bound="Language")


@_attrs_define
class Language:
    """
    Attributes:
        global_ (LanguageGlobal | Unset):
        current (LanguageCurrent | Unset):
        current_language (str | Unset):
    """

    global_: LanguageGlobal | Unset = UNSET
    current: LanguageCurrent | Unset = UNSET
    current_language: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        global_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.global_, Unset):
            global_ = self.global_.to_dict()

        current: dict[str, Any] | Unset = UNSET
        if not isinstance(self.current, Unset):
            current = self.current.to_dict()

        current_language = self.current_language

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if global_ is not UNSET:
            field_dict["global"] = global_
        if current is not UNSET:
            field_dict["current"] = current
        if current_language is not UNSET:
            field_dict["currentLanguage"] = current_language

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.language_current import LanguageCurrent
        from ..models.language_global import LanguageGlobal

        d = dict(src_dict)
        _global_ = d.pop("global", UNSET)
        global_: LanguageGlobal | Unset
        if isinstance(_global_, Unset):
            global_ = UNSET
        else:
            global_ = LanguageGlobal.from_dict(_global_)

        _current = d.pop("current", UNSET)
        current: LanguageCurrent | Unset
        if isinstance(_current, Unset):
            current = UNSET
        else:
            current = LanguageCurrent.from_dict(_current)

        current_language = d.pop("currentLanguage", UNSET)

        language = cls(
            global_=global_,
            current=current,
            current_language=current_language,
        )

        language.additional_properties = d
        return language

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
