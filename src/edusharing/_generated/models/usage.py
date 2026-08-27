from __future__ import annotations

import datetime
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.parameters import Parameters
    from ..models.usage_application import UsageApplication


T = TypeVar("T", bound="Usage")


@_attrs_define
class Usage:
    """
    Attributes:
        app_user (str):
        app_user_mail (str):
        course_id (str):
        app_id (str):
        node_id (str):
        parent_node_id (str):
        usage_version (str):
        resource_id (str):
        course_title (str | Unset):
        distinct_persons (int | Unset):
        from_used (datetime.datetime | Unset):
        to_used (datetime.datetime | Unset):
        usage_counter (int | Unset):
        usage_xml_params (Parameters | Unset):
        usage_xml_params_raw (str | Unset):
        guid (str | Unset):
        app_subtype (str | Unset):
        app_type (str | Unset):
        application (UsageApplication | Unset):
        type_ (str | Unset):
        created (datetime.datetime | Unset):
        modified (datetime.datetime | Unset):
    """

    app_user: str
    app_user_mail: str
    course_id: str
    app_id: str
    node_id: str
    parent_node_id: str
    usage_version: str
    resource_id: str
    course_title: str | Unset = UNSET
    distinct_persons: int | Unset = UNSET
    from_used: datetime.datetime | Unset = UNSET
    to_used: datetime.datetime | Unset = UNSET
    usage_counter: int | Unset = UNSET
    usage_xml_params: Parameters | Unset = UNSET
    usage_xml_params_raw: str | Unset = UNSET
    guid: str | Unset = UNSET
    app_subtype: str | Unset = UNSET
    app_type: str | Unset = UNSET
    application: UsageApplication | Unset = UNSET
    type_: str | Unset = UNSET
    created: datetime.datetime | Unset = UNSET
    modified: datetime.datetime | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        app_user = self.app_user

        app_user_mail = self.app_user_mail

        course_id = self.course_id

        app_id = self.app_id

        node_id = self.node_id

        parent_node_id = self.parent_node_id

        usage_version = self.usage_version

        resource_id = self.resource_id

        course_title = self.course_title

        distinct_persons = self.distinct_persons

        from_used: str | Unset = UNSET
        if not isinstance(self.from_used, Unset):
            from_used = self.from_used.isoformat()

        to_used: str | Unset = UNSET
        if not isinstance(self.to_used, Unset):
            to_used = self.to_used.isoformat()

        usage_counter = self.usage_counter

        usage_xml_params: dict[str, Any] | Unset = UNSET
        if not isinstance(self.usage_xml_params, Unset):
            usage_xml_params = self.usage_xml_params.to_dict()

        usage_xml_params_raw = self.usage_xml_params_raw

        guid = self.guid

        app_subtype = self.app_subtype

        app_type = self.app_type

        application: dict[str, Any] | Unset = UNSET
        if not isinstance(self.application, Unset):
            application = self.application.to_dict()

        type_ = self.type_

        created: str | Unset = UNSET
        if not isinstance(self.created, Unset):
            created = self.created.isoformat()

        modified: str | Unset = UNSET
        if not isinstance(self.modified, Unset):
            modified = self.modified.isoformat()

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "appUser": app_user,
                "appUserMail": app_user_mail,
                "courseId": course_id,
                "appId": app_id,
                "nodeId": node_id,
                "parentNodeId": parent_node_id,
                "usageVersion": usage_version,
                "resourceId": resource_id,
            }
        )
        if course_title is not UNSET:
            field_dict["courseTitle"] = course_title
        if distinct_persons is not UNSET:
            field_dict["distinctPersons"] = distinct_persons
        if from_used is not UNSET:
            field_dict["fromUsed"] = from_used
        if to_used is not UNSET:
            field_dict["toUsed"] = to_used
        if usage_counter is not UNSET:
            field_dict["usageCounter"] = usage_counter
        if usage_xml_params is not UNSET:
            field_dict["usageXmlParams"] = usage_xml_params
        if usage_xml_params_raw is not UNSET:
            field_dict["usageXmlParamsRaw"] = usage_xml_params_raw
        if guid is not UNSET:
            field_dict["guid"] = guid
        if app_subtype is not UNSET:
            field_dict["appSubtype"] = app_subtype
        if app_type is not UNSET:
            field_dict["appType"] = app_type
        if application is not UNSET:
            field_dict["application"] = application
        if type_ is not UNSET:
            field_dict["type"] = type_
        if created is not UNSET:
            field_dict["created"] = created
        if modified is not UNSET:
            field_dict["modified"] = modified

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.parameters import Parameters
        from ..models.usage_application import UsageApplication

        d = dict(src_dict)
        app_user = d.pop("appUser")

        app_user_mail = d.pop("appUserMail")

        course_id = d.pop("courseId")

        app_id = d.pop("appId")

        node_id = d.pop("nodeId")

        parent_node_id = d.pop("parentNodeId")

        usage_version = d.pop("usageVersion")

        resource_id = d.pop("resourceId")

        course_title = d.pop("courseTitle", UNSET)

        distinct_persons = d.pop("distinctPersons", UNSET)

        _from_used = d.pop("fromUsed", UNSET)
        from_used: datetime.datetime | Unset
        if isinstance(_from_used, Unset):
            from_used = UNSET
        else:
            from_used = datetime.datetime.fromisoformat(_from_used)

        _to_used = d.pop("toUsed", UNSET)
        to_used: datetime.datetime | Unset
        if isinstance(_to_used, Unset):
            to_used = UNSET
        else:
            to_used = datetime.datetime.fromisoformat(_to_used)

        usage_counter = d.pop("usageCounter", UNSET)

        _usage_xml_params = d.pop("usageXmlParams", UNSET)
        usage_xml_params: Parameters | Unset
        if isinstance(_usage_xml_params, Unset):
            usage_xml_params = UNSET
        else:
            usage_xml_params = Parameters.from_dict(_usage_xml_params)

        usage_xml_params_raw = d.pop("usageXmlParamsRaw", UNSET)

        guid = d.pop("guid", UNSET)

        app_subtype = d.pop("appSubtype", UNSET)

        app_type = d.pop("appType", UNSET)

        _application = d.pop("application", UNSET)
        application: UsageApplication | Unset
        if isinstance(_application, Unset):
            application = UNSET
        else:
            application = UsageApplication.from_dict(_application)

        type_ = d.pop("type", UNSET)

        _created = d.pop("created", UNSET)
        created: datetime.datetime | Unset
        if isinstance(_created, Unset):
            created = UNSET
        else:
            created = datetime.datetime.fromisoformat(_created)

        _modified = d.pop("modified", UNSET)
        modified: datetime.datetime | Unset
        if isinstance(_modified, Unset):
            modified = UNSET
        else:
            modified = datetime.datetime.fromisoformat(_modified)

        usage = cls(
            app_user=app_user,
            app_user_mail=app_user_mail,
            course_id=course_id,
            app_id=app_id,
            node_id=node_id,
            parent_node_id=parent_node_id,
            usage_version=usage_version,
            resource_id=resource_id,
            course_title=course_title,
            distinct_persons=distinct_persons,
            from_used=from_used,
            to_used=to_used,
            usage_counter=usage_counter,
            usage_xml_params=usage_xml_params,
            usage_xml_params_raw=usage_xml_params_raw,
            guid=guid,
            app_subtype=app_subtype,
            app_type=app_type,
            application=application,
            type_=type_,
            created=created,
            modified=modified,
        )

        usage.additional_properties = d
        return usage

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
