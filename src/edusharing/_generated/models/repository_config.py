from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.frontpage import Frontpage
    from ..models.repository_message import RepositoryMessage


T = TypeVar("T", bound="RepositoryConfig")


@_attrs_define
class RepositoryConfig:
    """
    Attributes:
        frontpage (Frontpage | Unset):
        messages (list[RepositoryMessage] | Unset):
    """

    frontpage: Frontpage | Unset = UNSET
    messages: list[RepositoryMessage] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        frontpage: dict[str, Any] | Unset = UNSET
        if not isinstance(self.frontpage, Unset):
            frontpage = self.frontpage.to_dict()

        messages: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.messages, Unset):
            messages = []
            for messages_item_data in self.messages:
                messages_item = messages_item_data.to_dict()
                messages.append(messages_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if frontpage is not UNSET:
            field_dict["frontpage"] = frontpage
        if messages is not UNSET:
            field_dict["messages"] = messages

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.frontpage import Frontpage
        from ..models.repository_message import RepositoryMessage

        d = dict(src_dict)
        _frontpage = d.pop("frontpage", UNSET)
        frontpage: Frontpage | Unset
        if isinstance(_frontpage, Unset):
            frontpage = UNSET
        else:
            frontpage = Frontpage.from_dict(_frontpage)

        _messages = d.pop("messages", UNSET)
        messages: list[RepositoryMessage] | Unset = UNSET
        if _messages is not UNSET:
            messages = []
            for messages_item_data in _messages:
                messages_item = RepositoryMessage.from_dict(messages_item_data)

                messages.append(messages_item)

        repository_config = cls(
            frontpage=frontpage,
            messages=messages,
        )

        repository_config.additional_properties = d
        return repository_config

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
