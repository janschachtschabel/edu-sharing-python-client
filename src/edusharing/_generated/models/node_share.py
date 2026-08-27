from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="NodeShare")


@_attrs_define
class NodeShare:
    """
    Attributes:
        password (bool | Unset):
        token (str | Unset):
        email (str | Unset):
        expiry_date (int | Unset):
        invited_at (int | Unset):
        download_count (int | Unset):
        url (str | Unset):
        share_id (str | Unset):
    """

    password: bool | Unset = UNSET
    token: str | Unset = UNSET
    email: str | Unset = UNSET
    expiry_date: int | Unset = UNSET
    invited_at: int | Unset = UNSET
    download_count: int | Unset = UNSET
    url: str | Unset = UNSET
    share_id: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        password = self.password

        token = self.token

        email = self.email

        expiry_date = self.expiry_date

        invited_at = self.invited_at

        download_count = self.download_count

        url = self.url

        share_id = self.share_id

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if password is not UNSET:
            field_dict["password"] = password
        if token is not UNSET:
            field_dict["token"] = token
        if email is not UNSET:
            field_dict["email"] = email
        if expiry_date is not UNSET:
            field_dict["expiryDate"] = expiry_date
        if invited_at is not UNSET:
            field_dict["invitedAt"] = invited_at
        if download_count is not UNSET:
            field_dict["downloadCount"] = download_count
        if url is not UNSET:
            field_dict["url"] = url
        if share_id is not UNSET:
            field_dict["shareId"] = share_id

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        password = d.pop("password", UNSET)

        token = d.pop("token", UNSET)

        email = d.pop("email", UNSET)

        expiry_date = d.pop("expiryDate", UNSET)

        invited_at = d.pop("invitedAt", UNSET)

        download_count = d.pop("downloadCount", UNSET)

        url = d.pop("url", UNSET)

        share_id = d.pop("shareId", UNSET)

        node_share = cls(
            password=password,
            token=token,
            email=email,
            expiry_date=expiry_date,
            invited_at=invited_at,
            download_count=download_count,
            url=url,
            share_id=share_id,
        )

        node_share.additional_properties = d
        return node_share

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
