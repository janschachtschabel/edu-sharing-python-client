from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.update_contributor_request_kind import UpdateContributorRequestKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="UpdateContributorRequest")


@_attrs_define
class UpdateContributorRequest:
    """
    Attributes:
        kind (UpdateContributorRequestKind | Unset):
        title (str | Unset):
        givenname (str | Unset):
        surname (str | Unset):
        org (str | Unset):
        email (str | Unset):
        url (str | Unset):
        uid (str | Unset):
        orcid (str | Unset):
        gnduri (str | Unset):
        ror (str | Unset):
        wikidata (str | Unset):
        apply_to_existing (bool | Unset):
    """

    kind: UpdateContributorRequestKind | Unset = UNSET
    title: str | Unset = UNSET
    givenname: str | Unset = UNSET
    surname: str | Unset = UNSET
    org: str | Unset = UNSET
    email: str | Unset = UNSET
    url: str | Unset = UNSET
    uid: str | Unset = UNSET
    orcid: str | Unset = UNSET
    gnduri: str | Unset = UNSET
    ror: str | Unset = UNSET
    wikidata: str | Unset = UNSET
    apply_to_existing: bool | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        kind: str | Unset = UNSET
        if not isinstance(self.kind, Unset):
            kind = self.kind.value

        title = self.title

        givenname = self.givenname

        surname = self.surname

        org = self.org

        email = self.email

        url = self.url

        uid = self.uid

        orcid = self.orcid

        gnduri = self.gnduri

        ror = self.ror

        wikidata = self.wikidata

        apply_to_existing = self.apply_to_existing

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if kind is not UNSET:
            field_dict["kind"] = kind
        if title is not UNSET:
            field_dict["title"] = title
        if givenname is not UNSET:
            field_dict["givenname"] = givenname
        if surname is not UNSET:
            field_dict["surname"] = surname
        if org is not UNSET:
            field_dict["org"] = org
        if email is not UNSET:
            field_dict["email"] = email
        if url is not UNSET:
            field_dict["url"] = url
        if uid is not UNSET:
            field_dict["uid"] = uid
        if orcid is not UNSET:
            field_dict["orcid"] = orcid
        if gnduri is not UNSET:
            field_dict["gnduri"] = gnduri
        if ror is not UNSET:
            field_dict["ror"] = ror
        if wikidata is not UNSET:
            field_dict["wikidata"] = wikidata
        if apply_to_existing is not UNSET:
            field_dict["applyToExisting"] = apply_to_existing

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        _kind = d.pop("kind", UNSET)
        kind: UpdateContributorRequestKind | Unset
        if isinstance(_kind, Unset):
            kind = UNSET
        else:
            kind = UpdateContributorRequestKind(_kind)

        title = d.pop("title", UNSET)

        givenname = d.pop("givenname", UNSET)

        surname = d.pop("surname", UNSET)

        org = d.pop("org", UNSET)

        email = d.pop("email", UNSET)

        url = d.pop("url", UNSET)

        uid = d.pop("uid", UNSET)

        orcid = d.pop("orcid", UNSET)

        gnduri = d.pop("gnduri", UNSET)

        ror = d.pop("ror", UNSET)

        wikidata = d.pop("wikidata", UNSET)

        apply_to_existing = d.pop("applyToExisting", UNSET)

        update_contributor_request = cls(
            kind=kind,
            title=title,
            givenname=givenname,
            surname=surname,
            org=org,
            email=email,
            url=url,
            uid=uid,
            orcid=orcid,
            gnduri=gnduri,
            ror=ror,
            wikidata=wikidata,
            apply_to_existing=apply_to_existing,
        )

        update_contributor_request.additional_properties = d
        return update_contributor_request

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
