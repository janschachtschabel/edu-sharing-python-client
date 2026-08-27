from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.language import Language
    from ..models.values import Values
    from ..models.values_backend import ValuesBackend


T = TypeVar("T", bound="Config")


@_attrs_define
class Config:
    """
    Attributes:
        context_id (str | Unset):
        current_backend (ValuesBackend | Unset):
        current (Values | Unset):
        global_ (Values | Unset):
        language (Language | Unset):
    """

    context_id: str | Unset = UNSET
    current_backend: ValuesBackend | Unset = UNSET
    current: Values | Unset = UNSET
    global_: Values | Unset = UNSET
    language: Language | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        context_id = self.context_id

        current_backend: dict[str, Any] | Unset = UNSET
        if not isinstance(self.current_backend, Unset):
            current_backend = self.current_backend.to_dict()

        current: dict[str, Any] | Unset = UNSET
        if not isinstance(self.current, Unset):
            current = self.current.to_dict()

        global_: dict[str, Any] | Unset = UNSET
        if not isinstance(self.global_, Unset):
            global_ = self.global_.to_dict()

        language: dict[str, Any] | Unset = UNSET
        if not isinstance(self.language, Unset):
            language = self.language.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if context_id is not UNSET:
            field_dict["contextId"] = context_id
        if current_backend is not UNSET:
            field_dict["currentBackend"] = current_backend
        if current is not UNSET:
            field_dict["current"] = current
        if global_ is not UNSET:
            field_dict["global"] = global_
        if language is not UNSET:
            field_dict["language"] = language

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.language import Language
        from ..models.values import Values
        from ..models.values_backend import ValuesBackend

        d = dict(src_dict)
        context_id = d.pop("contextId", UNSET)

        _current_backend = d.pop("currentBackend", UNSET)
        current_backend: ValuesBackend | Unset
        if isinstance(_current_backend, Unset):
            current_backend = UNSET
        else:
            current_backend = ValuesBackend.from_dict(_current_backend)

        _current = d.pop("current", UNSET)
        current: Values | Unset
        if isinstance(_current, Unset):
            current = UNSET
        else:
            current = Values.from_dict(_current)

        _global_ = d.pop("global", UNSET)
        global_: Values | Unset
        if isinstance(_global_, Unset):
            global_ = UNSET
        else:
            global_ = Values.from_dict(_global_)

        _language = d.pop("language", UNSET)
        language: Language | Unset
        if isinstance(_language, Unset):
            language = UNSET
        else:
            language = Language.from_dict(_language)

        config = cls(
            context_id=context_id,
            current_backend=current_backend,
            current=current,
            global_=global_,
            language=language,
        )

        config.additional_properties = d
        return config

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
