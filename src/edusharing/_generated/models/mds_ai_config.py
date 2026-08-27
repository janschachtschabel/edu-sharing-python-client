from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="MdsAiConfig")


@_attrs_define
class MdsAiConfig:
    """
    Attributes:
        id (str | Unset):
        provider (str | Unset):
        use_caching (bool | Unset):
        clear_cache (bool | Unset):
        prompt (str | Unset):
    """

    id: str | Unset = UNSET
    provider: str | Unset = UNSET
    use_caching: bool | Unset = UNSET
    clear_cache: bool | Unset = UNSET
    prompt: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        provider = self.provider

        use_caching = self.use_caching

        clear_cache = self.clear_cache

        prompt = self.prompt

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if provider is not UNSET:
            field_dict["provider"] = provider
        if use_caching is not UNSET:
            field_dict["useCaching"] = use_caching
        if clear_cache is not UNSET:
            field_dict["clearCache"] = clear_cache
        if prompt is not UNSET:
            field_dict["prompt"] = prompt

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        provider = d.pop("provider", UNSET)

        use_caching = d.pop("useCaching", UNSET)

        clear_cache = d.pop("clearCache", UNSET)

        prompt = d.pop("prompt", UNSET)

        mds_ai_config = cls(
            id=id,
            provider=provider,
            use_caching=use_caching,
            clear_cache=clear_cache,
            prompt=prompt,
        )

        mds_ai_config.additional_properties = d
        return mds_ai_config

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
