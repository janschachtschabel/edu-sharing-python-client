from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.config_upload_post_dialog import ConfigUploadPostDialog
from ..types import UNSET, Unset

T = TypeVar("T", bound="ConfigUpload")


@_attrs_define
class ConfigUpload:
    """File upload configuration

    Attributes:
        post_dialog (ConfigUploadPostDialog | Unset):
    """

    post_dialog: ConfigUploadPostDialog | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        post_dialog: str | Unset = UNSET
        if not isinstance(self.post_dialog, Unset):
            post_dialog = self.post_dialog.value

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if post_dialog is not UNSET:
            field_dict["postDialog"] = post_dialog

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _post_dialog = d.pop("postDialog", UNSET)
        post_dialog: ConfigUploadPostDialog | Unset
        if isinstance(_post_dialog, Unset):
            post_dialog = UNSET
        else:
            post_dialog = ConfigUploadPostDialog(_post_dialog)

        config_upload = cls(
            post_dialog=post_dialog,
        )

        config_upload.additional_properties = d
        return config_upload

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
