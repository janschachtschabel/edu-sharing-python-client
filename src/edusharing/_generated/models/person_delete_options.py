from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.collection_options import CollectionOptions
    from ..models.delete_option import DeleteOption
    from ..models.home_folder_options import HomeFolderOptions
    from ..models.shared_folder_options import SharedFolderOptions


T = TypeVar("T", bound="PersonDeleteOptions")


@_attrs_define
class PersonDeleteOptions:
    """
    Attributes:
        cleanup_metadata (bool | Unset):
        home_folder (HomeFolderOptions | Unset):
        shared_folders (SharedFolderOptions | Unset):
        collections (CollectionOptions | Unset):
        ratings (DeleteOption | Unset):
        comments (DeleteOption | Unset):
        collection_feedback (DeleteOption | Unset):
        statistics (DeleteOption | Unset):
        stream (DeleteOption | Unset):
        receiver (str | Unset):
        receiver_group (str | Unset):
    """

    cleanup_metadata: bool | Unset = UNSET
    home_folder: HomeFolderOptions | Unset = UNSET
    shared_folders: SharedFolderOptions | Unset = UNSET
    collections: CollectionOptions | Unset = UNSET
    ratings: DeleteOption | Unset = UNSET
    comments: DeleteOption | Unset = UNSET
    collection_feedback: DeleteOption | Unset = UNSET
    statistics: DeleteOption | Unset = UNSET
    stream: DeleteOption | Unset = UNSET
    receiver: str | Unset = UNSET
    receiver_group: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        cleanup_metadata = self.cleanup_metadata

        home_folder: dict[str, Any] | Unset = UNSET
        if not isinstance(self.home_folder, Unset):
            home_folder = self.home_folder.to_dict()

        shared_folders: dict[str, Any] | Unset = UNSET
        if not isinstance(self.shared_folders, Unset):
            shared_folders = self.shared_folders.to_dict()

        collections: dict[str, Any] | Unset = UNSET
        if not isinstance(self.collections, Unset):
            collections = self.collections.to_dict()

        ratings: dict[str, Any] | Unset = UNSET
        if not isinstance(self.ratings, Unset):
            ratings = self.ratings.to_dict()

        comments: dict[str, Any] | Unset = UNSET
        if not isinstance(self.comments, Unset):
            comments = self.comments.to_dict()

        collection_feedback: dict[str, Any] | Unset = UNSET
        if not isinstance(self.collection_feedback, Unset):
            collection_feedback = self.collection_feedback.to_dict()

        statistics: dict[str, Any] | Unset = UNSET
        if not isinstance(self.statistics, Unset):
            statistics = self.statistics.to_dict()

        stream: dict[str, Any] | Unset = UNSET
        if not isinstance(self.stream, Unset):
            stream = self.stream.to_dict()

        receiver = self.receiver

        receiver_group = self.receiver_group

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if cleanup_metadata is not UNSET:
            field_dict["cleanupMetadata"] = cleanup_metadata
        if home_folder is not UNSET:
            field_dict["homeFolder"] = home_folder
        if shared_folders is not UNSET:
            field_dict["sharedFolders"] = shared_folders
        if collections is not UNSET:
            field_dict["collections"] = collections
        if ratings is not UNSET:
            field_dict["ratings"] = ratings
        if comments is not UNSET:
            field_dict["comments"] = comments
        if collection_feedback is not UNSET:
            field_dict["collectionFeedback"] = collection_feedback
        if statistics is not UNSET:
            field_dict["statistics"] = statistics
        if stream is not UNSET:
            field_dict["stream"] = stream
        if receiver is not UNSET:
            field_dict["receiver"] = receiver
        if receiver_group is not UNSET:
            field_dict["receiverGroup"] = receiver_group

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.collection_options import CollectionOptions
        from ..models.delete_option import DeleteOption
        from ..models.home_folder_options import HomeFolderOptions
        from ..models.shared_folder_options import SharedFolderOptions

        d = dict(src_dict)
        cleanup_metadata = d.pop("cleanupMetadata", UNSET)

        _home_folder = d.pop("homeFolder", UNSET)
        home_folder: HomeFolderOptions | Unset
        if isinstance(_home_folder, Unset):
            home_folder = UNSET
        else:
            home_folder = HomeFolderOptions.from_dict(_home_folder)

        _shared_folders = d.pop("sharedFolders", UNSET)
        shared_folders: SharedFolderOptions | Unset
        if isinstance(_shared_folders, Unset):
            shared_folders = UNSET
        else:
            shared_folders = SharedFolderOptions.from_dict(_shared_folders)

        _collections = d.pop("collections", UNSET)
        collections: CollectionOptions | Unset
        if isinstance(_collections, Unset):
            collections = UNSET
        else:
            collections = CollectionOptions.from_dict(_collections)

        _ratings = d.pop("ratings", UNSET)
        ratings: DeleteOption | Unset
        if isinstance(_ratings, Unset):
            ratings = UNSET
        else:
            ratings = DeleteOption.from_dict(_ratings)

        _comments = d.pop("comments", UNSET)
        comments: DeleteOption | Unset
        if isinstance(_comments, Unset):
            comments = UNSET
        else:
            comments = DeleteOption.from_dict(_comments)

        _collection_feedback = d.pop("collectionFeedback", UNSET)
        collection_feedback: DeleteOption | Unset
        if isinstance(_collection_feedback, Unset):
            collection_feedback = UNSET
        else:
            collection_feedback = DeleteOption.from_dict(_collection_feedback)

        _statistics = d.pop("statistics", UNSET)
        statistics: DeleteOption | Unset
        if isinstance(_statistics, Unset):
            statistics = UNSET
        else:
            statistics = DeleteOption.from_dict(_statistics)

        _stream = d.pop("stream", UNSET)
        stream: DeleteOption | Unset
        if isinstance(_stream, Unset):
            stream = UNSET
        else:
            stream = DeleteOption.from_dict(_stream)

        receiver = d.pop("receiver", UNSET)

        receiver_group = d.pop("receiverGroup", UNSET)

        person_delete_options = cls(
            cleanup_metadata=cleanup_metadata,
            home_folder=home_folder,
            shared_folders=shared_folders,
            collections=collections,
            ratings=ratings,
            comments=comments,
            collection_feedback=collection_feedback,
            statistics=statistics,
            stream=stream,
            receiver=receiver,
            receiver_group=receiver_group,
        )

        person_delete_options.additional_properties = d
        return person_delete_options

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
