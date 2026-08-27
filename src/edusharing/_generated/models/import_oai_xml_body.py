from __future__ import annotations

from collections.abc import Mapping
from io import BytesIO
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, File, FileTypes, Unset

T = TypeVar("T", bound="ImportOaiXMLBody")


@_attrs_define
class ImportOaiXMLBody:
    """
    Attributes:
        xml (File | Unset):
    """

    xml: File | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        xml: FileTypes | Unset = UNSET
        if not isinstance(self.xml, Unset):
            xml = self.xml.to_tuple()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if xml is not UNSET:
            field_dict["xml"] = xml

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        if not isinstance(self.xml, Unset):
            files.append(("xml", self.xml.to_tuple()))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _xml = d.pop("xml", UNSET)
        xml: File | Unset
        if isinstance(_xml, Unset):
            xml = UNSET
        else:
            xml = File(payload=BytesIO(_xml))

        import_oai_xml_body = cls(
            xml=xml,
        )

        import_oai_xml_body.additional_properties = d
        return import_oai_xml_body

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
