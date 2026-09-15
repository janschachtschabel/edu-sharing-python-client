from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.licenses_repository import LicensesRepository
    from ..models.licenses_services import LicensesServices


T = TypeVar("T", bound="Licenses")


@_attrs_define
class Licenses:
    """
    Attributes:
        repository (LicensesRepository | Unset):
        services (LicensesServices | Unset):
    """

    repository: LicensesRepository | Unset = UNSET
    services: LicensesServices | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        repository: dict[str, Any] | Unset = UNSET
        if not isinstance(self.repository, Unset):
            repository = self.repository.to_dict()

        services: dict[str, Any] | Unset = UNSET
        if not isinstance(self.services, Unset):
            services = self.services.to_dict()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if repository is not UNSET:
            field_dict["repository"] = repository
        if services is not UNSET:
            field_dict["services"] = services

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.licenses_repository import LicensesRepository
        from ..models.licenses_services import LicensesServices

        d = dict(src_dict)
        _repository = d.pop("repository", UNSET)
        repository: LicensesRepository | Unset
        if isinstance(_repository, Unset):
            repository = UNSET
        else:
            repository = LicensesRepository.from_dict(_repository)

        _services = d.pop("services", UNSET)
        services: LicensesServices | Unset
        if isinstance(_services, Unset):
            services = UNSET
        else:
            services = LicensesServices.from_dict(_services)

        licenses = cls(
            repository=repository,
            services=services,
        )

        licenses.additional_properties = d
        return licenses

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
