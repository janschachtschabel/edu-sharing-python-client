from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.shared_folder_options_cc_files import SharedFolderOptionsCcFiles
from ..models.shared_folder_options_folders import SharedFolderOptionsFolders
from ..models.shared_folder_options_private_files import SharedFolderOptionsPrivateFiles
from ..types import UNSET, Unset

T = TypeVar("T", bound="SharedFolderOptions")


@_attrs_define
class SharedFolderOptions:
    """
    Attributes:
        folders (SharedFolderOptionsFolders | Unset):
        private_files (SharedFolderOptionsPrivateFiles | Unset):
        cc_files (SharedFolderOptionsCcFiles | Unset):
        move (bool | Unset):
    """

    folders: SharedFolderOptionsFolders | Unset = UNSET
    private_files: SharedFolderOptionsPrivateFiles | Unset = UNSET
    cc_files: SharedFolderOptionsCcFiles | Unset = UNSET
    move: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        folders: str | Unset = UNSET
        if not isinstance(self.folders, Unset):
            folders = self.folders.value

        private_files: str | Unset = UNSET
        if not isinstance(self.private_files, Unset):
            private_files = self.private_files.value

        cc_files: str | Unset = UNSET
        if not isinstance(self.cc_files, Unset):
            cc_files = self.cc_files.value

        move = self.move

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if folders is not UNSET:
            field_dict["folders"] = folders
        if private_files is not UNSET:
            field_dict["privateFiles"] = private_files
        if cc_files is not UNSET:
            field_dict["ccFiles"] = cc_files
        if move is not UNSET:
            field_dict["move"] = move

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _folders = d.pop("folders", UNSET)
        folders: SharedFolderOptionsFolders | Unset
        if isinstance(_folders, Unset):
            folders = UNSET
        else:
            folders = SharedFolderOptionsFolders(_folders)

        _private_files = d.pop("privateFiles", UNSET)
        private_files: SharedFolderOptionsPrivateFiles | Unset
        if isinstance(_private_files, Unset):
            private_files = UNSET
        else:
            private_files = SharedFolderOptionsPrivateFiles(_private_files)

        _cc_files = d.pop("ccFiles", UNSET)
        cc_files: SharedFolderOptionsCcFiles | Unset
        if isinstance(_cc_files, Unset):
            cc_files = UNSET
        else:
            cc_files = SharedFolderOptionsCcFiles(_cc_files)

        move = d.pop("move", UNSET)

        shared_folder_options = cls(
            folders=folders,
            private_files=private_files,
            cc_files=cc_files,
            move=move,
        )

        shared_folder_options.additional_properties = d
        return shared_folder_options

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
