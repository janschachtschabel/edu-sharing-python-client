from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.language import Language
    from ..models.values import Values
    from ..models.variables import Variables


T = TypeVar("T", bound="Context")


@_attrs_define
class Context:
    """
    Attributes:
        id (str | Unset):
        domain (list[str] | Unset):
        values (Values | Unset):
        language (list[Language] | Unset):
        variables (Variables | Unset):
    """

    id: str | Unset = UNSET
    domain: list[str] | Unset = UNSET
    values: Values | Unset = UNSET
    language: list[Language] | Unset = UNSET
    variables: Variables | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        domain: list[str] | Unset = UNSET
        if not isinstance(self.domain, Unset):
            domain = self.domain

        values: dict[str, Any] | Unset = UNSET
        if not isinstance(self.values, Unset):
            values = self.values.to_dict()

        language: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.language, Unset):
            language = []
            for language_item_data in self.language:
                language_item = language_item_data.to_dict()
                language.append(language_item)

        variables: dict[str, Any] | Unset = UNSET
        if not isinstance(self.variables, Unset):
            variables = self.variables.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if domain is not UNSET:
            field_dict["domain"] = domain
        if values is not UNSET:
            field_dict["values"] = values
        if language is not UNSET:
            field_dict["language"] = language
        if variables is not UNSET:
            field_dict["variables"] = variables

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.language import Language
        from ..models.values import Values
        from ..models.variables import Variables

        d = dict(src_dict)
        id = d.pop("id", UNSET)

        domain = cast(list[str], d.pop("domain", UNSET))

        _values = d.pop("values", UNSET)
        values: Values | Unset
        if isinstance(_values, Unset):
            values = UNSET
        else:
            values = Values.from_dict(_values)

        _language = d.pop("language", UNSET)
        language: list[Language] | Unset = UNSET
        if _language is not UNSET:
            language = []
            for language_item_data in _language:
                language_item = Language.from_dict(language_item_data)

                language.append(language_item)

        _variables = d.pop("variables", UNSET)
        variables: Variables | Unset
        if isinstance(_variables, Unset):
            variables = UNSET
        else:
            variables = Variables.from_dict(_variables)

        context = cls(
            id=id,
            domain=domain,
            values=values,
            language=language,
            variables=variables,
        )

        context.additional_properties = d
        return context

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
