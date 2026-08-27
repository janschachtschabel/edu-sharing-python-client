from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.form_data_content_disposition_parameters import (
        FormDataContentDispositionParameters,
    )


T = TypeVar("T", bound="FormDataContentDisposition")


@_attrs_define
class FormDataContentDisposition:
    """
    Attributes:
        type_ (str | Unset):
        parameters (FormDataContentDispositionParameters | Unset):
        file_name (str | Unset):
        creation_date (datetime.datetime | Unset):
        modification_date (datetime.datetime | Unset):
        read_date (datetime.datetime | Unset):
        size (int | Unset):
        name (str | Unset):
    """

    type_: str | Unset = UNSET
    parameters: FormDataContentDispositionParameters | Unset = UNSET
    file_name: str | Unset = UNSET
    creation_date: datetime.datetime | Unset = UNSET
    modification_date: datetime.datetime | Unset = UNSET
    read_date: datetime.datetime | Unset = UNSET
    size: int | Unset = UNSET
    name: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        type_ = self.type_

        parameters: dict[str, Any] | Unset = UNSET
        if not isinstance(self.parameters, Unset):
            parameters = self.parameters.to_dict()

        file_name = self.file_name

        creation_date: str | Unset = UNSET
        if not isinstance(self.creation_date, Unset):
            creation_date = self.creation_date.isoformat()

        modification_date: str | Unset = UNSET
        if not isinstance(self.modification_date, Unset):
            modification_date = self.modification_date.isoformat()

        read_date: str | Unset = UNSET
        if not isinstance(self.read_date, Unset):
            read_date = self.read_date.isoformat()

        size = self.size

        name = self.name

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if type_ is not UNSET:
            field_dict["type"] = type_
        if parameters is not UNSET:
            field_dict["parameters"] = parameters
        if file_name is not UNSET:
            field_dict["fileName"] = file_name
        if creation_date is not UNSET:
            field_dict["creationDate"] = creation_date
        if modification_date is not UNSET:
            field_dict["modificationDate"] = modification_date
        if read_date is not UNSET:
            field_dict["readDate"] = read_date
        if size is not UNSET:
            field_dict["size"] = size
        if name is not UNSET:
            field_dict["name"] = name

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.form_data_content_disposition_parameters import (
            FormDataContentDispositionParameters,
        )

        d = dict(src_dict)
        type_ = d.pop("type", UNSET)

        _parameters = d.pop("parameters", UNSET)
        parameters: FormDataContentDispositionParameters | Unset
        if isinstance(_parameters, Unset):
            parameters = UNSET
        else:
            parameters = FormDataContentDispositionParameters.from_dict(_parameters)

        file_name = d.pop("fileName", UNSET)

        _creation_date = d.pop("creationDate", UNSET)
        creation_date: datetime.datetime | Unset
        if isinstance(_creation_date, Unset):
            creation_date = UNSET
        else:
            creation_date = datetime.datetime.fromisoformat(_creation_date)

        _modification_date = d.pop("modificationDate", UNSET)
        modification_date: datetime.datetime | Unset
        if isinstance(_modification_date, Unset):
            modification_date = UNSET
        else:
            modification_date = datetime.datetime.fromisoformat(_modification_date)

        _read_date = d.pop("readDate", UNSET)
        read_date: datetime.datetime | Unset
        if isinstance(_read_date, Unset):
            read_date = UNSET
        else:
            read_date = datetime.datetime.fromisoformat(_read_date)

        size = d.pop("size", UNSET)

        name = d.pop("name", UNSET)

        form_data_content_disposition = cls(
            type_=type_,
            parameters=parameters,
            file_name=file_name,
            creation_date=creation_date,
            modification_date=modification_date,
            read_date=read_date,
            size=size,
            name=name,
        )

        form_data_content_disposition.additional_properties = d
        return form_data_content_disposition

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
