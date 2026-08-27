from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.repo import Repo


T = TypeVar("T", bound="Remote")


@_attrs_define
class Remote:
    """Remote node information (in case this node is from a remote/federated repository)

    Attributes:
        repository (Repo | Unset):
        id (str | Unset):
    """

    repository: Repo | Unset = UNSET
    id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository: dict[str, Any] | Unset = UNSET
        if not isinstance(self.repository, Unset):
            repository = self.repository.to_dict()

        id = self.id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if repository is not UNSET:
            field_dict["repository"] = repository
        if id is not UNSET:
            field_dict["id"] = id

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.repo import Repo

        d = dict(src_dict)
        _repository = d.pop("repository", UNSET)
        repository: Repo | Unset
        if isinstance(_repository, Unset):
            repository = UNSET
        else:
            repository = Repo.from_dict(_repository)

        id = d.pop("id", UNSET)

        remote = cls(
            repository=repository,
            id=id,
        )

        remote.additional_properties = d
        return remote

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
