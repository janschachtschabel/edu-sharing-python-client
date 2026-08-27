from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NodeRef")


@_attrs_define
class NodeRef:
    """
    Attributes:
        repo (str):
        id (str):
        archived (bool):
        is_home_repo (bool | Unset):
    """

    repo: str
    id: str
    archived: bool
    is_home_repo: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repo = self.repo

        id = self.id

        archived = self.archived

        is_home_repo = self.is_home_repo

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "repo": repo,
                "id": id,
                "archived": archived,
            }
        )
        if is_home_repo is not UNSET:
            field_dict["isHomeRepo"] = is_home_repo

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        repo = d.pop("repo")

        id = d.pop("id")

        archived = d.pop("archived")

        is_home_repo = d.pop("isHomeRepo", UNSET)

        node_ref = cls(
            repo=repo,
            id=id,
            archived=archived,
            is_home_repo=is_home_repo,
        )

        node_ref.additional_properties = d
        return node_ref

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
