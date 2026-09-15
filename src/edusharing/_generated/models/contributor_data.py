from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..models.contributor_data_kind import ContributorDataKind
from ..types import UNSET, Unset

T = TypeVar("T", bound="ContributorData")


@_attrs_define
class ContributorData:
    """
    Attributes:
        id (int):
        kind (ContributorDataKind):
        vcard (str):
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
        created (datetime.datetime | Unset):
        last_updated (datetime.datetime | Unset):
    """

    id: int
    kind: ContributorDataKind
    vcard: str
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
    created: datetime.datetime | Unset = UNSET
    last_updated: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        kind = self.kind.value

        vcard = self.vcard

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

        created: str | Unset = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        last_updated: str | Unset = UNSET
        if not isinstance(self.last_updated, Unset):
            last_updated = self.last_updated.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "id": id,
                "kind": kind,
                "vcard": vcard,
            }
        )
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
        if created is not UNSET:
            field_dict["created"] = created
        if last_updated is not UNSET:
            field_dict["lastUpdated"] = last_updated

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id")

        kind = ContributorDataKind(d.pop("kind"))

        vcard = d.pop("vcard")

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

        _created = d.pop("created", UNSET)
        created: datetime.datetime | Unset
        if isinstance(_created, Unset):
            created = UNSET
        else:
            created = datetime.datetime.fromisoformat(_created)

        _last_updated = d.pop("lastUpdated", UNSET)
        last_updated: datetime.datetime | Unset
        if isinstance(_last_updated, Unset):
            last_updated = UNSET
        else:
            last_updated = datetime.datetime.fromisoformat(_last_updated)

        contributor_data = cls(
            id=id,
            kind=kind,
            vcard=vcard,
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
            created=created,
            last_updated=last_updated,
        )

        contributor_data.additional_properties = d
        return contributor_data

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
