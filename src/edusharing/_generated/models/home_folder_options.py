from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.home_folder_options_cc_files import HomeFolderOptionsCcFiles
from ..models.home_folder_options_folders import HomeFolderOptionsFolders
from ..models.home_folder_options_private_files import HomeFolderOptionsPrivateFiles
from ..types import UNSET, Unset

T = TypeVar("T", bound="HomeFolderOptions")


@_attrs_define
class HomeFolderOptions:
    """
    Attributes:
        folders (HomeFolderOptionsFolders | Unset):
        private_files (HomeFolderOptionsPrivateFiles | Unset):
        cc_files (HomeFolderOptionsCcFiles | Unset):
        keep_folder_structure (bool | Unset):
    """

    folders: HomeFolderOptionsFolders | Unset = UNSET
    private_files: HomeFolderOptionsPrivateFiles | Unset = UNSET
    cc_files: HomeFolderOptionsCcFiles | Unset = UNSET
    keep_folder_structure: bool | Unset = UNSET
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

        keep_folder_structure = self.keep_folder_structure

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if folders is not UNSET:
            field_dict["folders"] = folders
        if private_files is not UNSET:
            field_dict["privateFiles"] = private_files
        if cc_files is not UNSET:
            field_dict["ccFiles"] = cc_files
        if keep_folder_structure is not UNSET:
            field_dict["keepFolderStructure"] = keep_folder_structure

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _folders = d.pop("folders", UNSET)
        folders: HomeFolderOptionsFolders | Unset
        if isinstance(_folders, Unset):
            folders = UNSET
        else:
            folders = HomeFolderOptionsFolders(_folders)

        _private_files = d.pop("privateFiles", UNSET)
        private_files: HomeFolderOptionsPrivateFiles | Unset
        if isinstance(_private_files, Unset):
            private_files = UNSET
        else:
            private_files = HomeFolderOptionsPrivateFiles(_private_files)

        _cc_files = d.pop("ccFiles", UNSET)
        cc_files: HomeFolderOptionsCcFiles | Unset
        if isinstance(_cc_files, Unset):
            cc_files = UNSET
        else:
            cc_files = HomeFolderOptionsCcFiles(_cc_files)

        keep_folder_structure = d.pop("keepFolderStructure", UNSET)

        home_folder_options = cls(
            folders=folders,
            private_files=private_files,
            cc_files=cc_files,
            keep_folder_structure=keep_folder_structure,
        )

        home_folder_options.additional_properties = d
        return home_folder_options

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
