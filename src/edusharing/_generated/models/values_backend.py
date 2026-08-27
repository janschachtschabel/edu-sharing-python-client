from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.repository_config_backend import RepositoryConfigBackend
    from ..models.security_config import SecurityConfig


T = TypeVar("T", bound="ValuesBackend")


@_attrs_define
class ValuesBackend:
    """
    Attributes:
        security (SecurityConfig | Unset):
        repository (RepositoryConfigBackend | Unset):
    """

    security: SecurityConfig | Unset = UNSET
    repository: RepositoryConfigBackend | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        security: dict[str, Any] | Unset = UNSET
        if not isinstance(self.security, Unset):
            security = self.security.to_dict()

        repository: dict[str, Any] | Unset = UNSET
        if not isinstance(self.repository, Unset):
            repository = self.repository.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if security is not UNSET:
            field_dict["security"] = security
        if repository is not UNSET:
            field_dict["repository"] = repository

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.repository_config_backend import RepositoryConfigBackend
        from ..models.security_config import SecurityConfig

        d = dict(src_dict)
        _security = d.pop("security", UNSET)
        security: SecurityConfig | Unset
        if isinstance(_security, Unset):
            security = UNSET
        else:
            security = SecurityConfig.from_dict(_security)

        _repository = d.pop("repository", UNSET)
        repository: RepositoryConfigBackend | Unset
        if isinstance(_repository, Unset):
            repository = UNSET
        else:
            repository = RepositoryConfigBackend.from_dict(_repository)

        values_backend = cls(
            security=security,
            repository=repository,
        )

        values_backend.additional_properties = d
        return values_backend

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
