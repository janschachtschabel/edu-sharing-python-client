from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.childobjects_config import ChildobjectsConfig


T = TypeVar("T", bound="RepositoryConfigBackend")


@_attrs_define
class RepositoryConfigBackend:
    """
    Attributes:
        childobjects (ChildobjectsConfig | Unset):
    """

    childobjects: ChildobjectsConfig | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        childobjects: dict[str, Any] | Unset = UNSET
        if not isinstance(self.childobjects, Unset):
            childobjects = self.childobjects.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if childobjects is not UNSET:
            field_dict["childobjects"] = childobjects

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.childobjects_config import ChildobjectsConfig

        d = dict(src_dict)
        _childobjects = d.pop("childobjects", UNSET)
        childobjects: ChildobjectsConfig | Unset
        if isinstance(_childobjects, Unset):
            childobjects = UNSET
        else:
            childobjects = ChildobjectsConfig.from_dict(_childobjects)

        repository_config_backend = cls(
            childobjects=childobjects,
        )

        repository_config_backend.additional_properties = d
        return repository_config_backend

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
