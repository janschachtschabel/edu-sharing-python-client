from __future__ import annotations

import json
from collections.abc import Mapping
from io import BytesIO
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from .. import types
from ..types import UNSET, File, FileTypes, Unset

if TYPE_CHECKING:
    from ..models.children_metadata import ChildrenMetadata


T = TypeVar("T", bound="ChildrenFileContentUpload")


@_attrs_define
class ChildrenFileContentUpload:
    """Multipart upload for node content

    Attributes:
        properties (ChildrenMetadata | Unset): JSON-Metadaten
        file (File | Unset): File content
    """

    properties: ChildrenMetadata | Unset = UNSET
    file: File | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        properties: dict[str, Any] | Unset = UNSET
        if not isinstance(self.properties, Unset):
            properties = self.properties.to_dict()

        file: FileTypes | Unset = UNSET
        if not isinstance(self.file, Unset):
            file = self.file.to_tuple()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if properties is not UNSET:
            field_dict["properties"] = properties
        if file is not UNSET:
            field_dict["file"] = file

        return field_dict

    def to_multipart(self) -> types.RequestFiles:
        files: types.RequestFiles = []

        if not isinstance(self.properties, Unset):
            files.append(
                (
                    "properties",
                    (None, json.dumps(self.properties.to_dict()).encode(), "application/json"),
                )
            )

        if not isinstance(self.file, Unset):
            files.append(("file", self.file.to_tuple()))

        for prop_name, prop in self.additional_properties.items():
            files.append((prop_name, (None, str(prop).encode(), "text/plain")))

        return files

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.children_metadata import ChildrenMetadata

        d = dict(src_dict)
        _properties = d.pop("properties", UNSET)
        properties: ChildrenMetadata | Unset
        if isinstance(_properties, Unset):
            properties = UNSET
        else:
            properties = ChildrenMetadata.from_dict(_properties)

        _file = d.pop("file", UNSET)
        file: File | Unset
        if isinstance(_file, Unset):
            file = UNSET
        else:
            file = File(payload=BytesIO(_file))

        children_file_content_upload = cls(
            properties=properties,
            file=file,
        )

        children_file_content_upload.additional_properties = d
        return children_file_content_upload

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
