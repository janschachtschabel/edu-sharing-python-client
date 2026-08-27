from __future__ import annotations

from collections.abc import Mapping
from typing import Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

T = TypeVar("T", bound="Application")


@_attrs_define
class Application:
    """
    Attributes:
        id (str | Unset):
        title (str | Unset):
        type_ (str | Unset):
        subtype (str | Unset):
        host (str | Unset):
        domain (str | Unset):
        allowed_origins (list[str] | Unset):
        webserver_url (str | Unset):
        client_base_url (str | Unset):
        repository_type (str | Unset):
        xml (str | Unset):
        file (str | Unset):
        content_url (str | Unset):
        config_url (str | Unset):
    """

    id: str | Unset = UNSET
    title: str | Unset = UNSET
    type_: str | Unset = UNSET
    subtype: str | Unset = UNSET
    host: str | Unset = UNSET
    domain: str | Unset = UNSET
    allowed_origins: list[str] | Unset = UNSET
    webserver_url: str | Unset = UNSET
    client_base_url: str | Unset = UNSET
    repository_type: str | Unset = UNSET
    xml: str | Unset = UNSET
    file: str | Unset = UNSET
    content_url: str | Unset = UNSET
    config_url: str | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        id = self.id

        title = self.title

        type_ = self.type_

        subtype = self.subtype

        host = self.host

        domain = self.domain

        allowed_origins: list[str] | Unset = UNSET
        if not isinstance(self.allowed_origins, Unset):
            allowed_origins = self.allowed_origins

        webserver_url = self.webserver_url

        client_base_url = self.client_base_url

        repository_type = self.repository_type

        xml = self.xml

        file = self.file

        content_url = self.content_url

        config_url = self.config_url

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if id is not UNSET:
            field_dict["id"] = id
        if title is not UNSET:
            field_dict["title"] = title
        if type_ is not UNSET:
            field_dict["type"] = type_
        if subtype is not UNSET:
            field_dict["subtype"] = subtype
        if host is not UNSET:
            field_dict["host"] = host
        if domain is not UNSET:
            field_dict["domain"] = domain
        if allowed_origins is not UNSET:
            field_dict["allowedOrigins"] = allowed_origins
        if webserver_url is not UNSET:
            field_dict["webserverUrl"] = webserver_url
        if client_base_url is not UNSET:
            field_dict["clientBaseUrl"] = client_base_url
        if repository_type is not UNSET:
            field_dict["repositoryType"] = repository_type
        if xml is not UNSET:
            field_dict["xml"] = xml
        if file is not UNSET:
            field_dict["file"] = file
        if content_url is not UNSET:
            field_dict["contentUrl"] = content_url
        if config_url is not UNSET:
            field_dict["configUrl"] = config_url

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        d = dict(src_dict)
        id = d.pop("id", UNSET)

        title = d.pop("title", UNSET)

        type_ = d.pop("type", UNSET)

        subtype = d.pop("subtype", UNSET)

        host = d.pop("host", UNSET)

        domain = d.pop("domain", UNSET)

        allowed_origins = cast(list[str], d.pop("allowedOrigins", UNSET))

        webserver_url = d.pop("webserverUrl", UNSET)

        client_base_url = d.pop("clientBaseUrl", UNSET)

        repository_type = d.pop("repositoryType", UNSET)

        xml = d.pop("xml", UNSET)

        file = d.pop("file", UNSET)

        content_url = d.pop("contentUrl", UNSET)

        config_url = d.pop("configUrl", UNSET)

        application = cls(
            id=id,
            title=title,
            type_=type_,
            subtype=subtype,
            host=host,
            domain=domain,
            allowed_origins=allowed_origins,
            webserver_url=webserver_url,
            client_base_url=client_base_url,
            repository_type=repository_type,
            xml=xml,
            file=file,
            content_url=content_url,
            config_url=config_url,
        )

        application.additional_properties = d
        return application

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
