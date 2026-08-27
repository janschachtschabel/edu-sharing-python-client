from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar, cast

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.about_service import AboutService
    from ..models.feature_info import FeatureInfo
    from ..models.plugin_info import PluginInfo
    from ..models.rendering_service import RenderingService
    from ..models.service_version import ServiceVersion


T = TypeVar("T", bound="About")


@_attrs_define
class About:
    """
    Attributes:
        version (ServiceVersion):
        services (list[AboutService]):
        rendering_service_2 (RenderingService | Unset):
        plugins (list[PluginInfo] | Unset):
        features (list[FeatureInfo] | Unset):
        signature_algorithms (list[str] | Unset):
        default_signature_algorithm (str | Unset):
        themes_url (str | Unset):
        last_cache_update (int | Unset):
    """

    version: ServiceVersion
    services: list[AboutService]
    rendering_service_2: RenderingService | Unset = UNSET
    plugins: list[PluginInfo] | Unset = UNSET
    features: list[FeatureInfo] | Unset = UNSET
    signature_algorithms: list[str] | Unset = UNSET
    default_signature_algorithm: str | Unset = UNSET
    themes_url: str | Unset = UNSET
    last_cache_update: int | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        version = self.version.to_dict()

        services = []
        for services_item_data in self.services:
            services_item = services_item_data.to_dict()
            services.append(services_item)

        rendering_service_2: dict[str, Any] | Unset = UNSET
        if not isinstance(self.rendering_service_2, Unset):
            rendering_service_2 = self.rendering_service_2.to_dict()

        plugins: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.plugins, Unset):
            plugins = []
            for plugins_item_data in self.plugins:
                plugins_item = plugins_item_data.to_dict()
                plugins.append(plugins_item)

        features: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.features, Unset):
            features = []
            for features_item_data in self.features:
                features_item = features_item_data.to_dict()
                features.append(features_item)

        signature_algorithms: list[str] | Unset = UNSET
        if not isinstance(self.signature_algorithms, Unset):
            signature_algorithms = self.signature_algorithms

        default_signature_algorithm = self.default_signature_algorithm

        themes_url = self.themes_url

        last_cache_update = self.last_cache_update

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update(
            {
                "version": version,
                "services": services,
            }
        )
        if rendering_service_2 is not UNSET:
            field_dict["renderingService2"] = rendering_service_2
        if plugins is not UNSET:
            field_dict["plugins"] = plugins
        if features is not UNSET:
            field_dict["features"] = features
        if signature_algorithms is not UNSET:
            field_dict["signatureAlgorithms"] = signature_algorithms
        if default_signature_algorithm is not UNSET:
            field_dict["defaultSignatureAlgorithm"] = default_signature_algorithm
        if themes_url is not UNSET:
            field_dict["themesUrl"] = themes_url
        if last_cache_update is not UNSET:
            field_dict["lastCacheUpdate"] = last_cache_update

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.about_service import AboutService
        from ..models.feature_info import FeatureInfo
        from ..models.plugin_info import PluginInfo
        from ..models.rendering_service import RenderingService
        from ..models.service_version import ServiceVersion

        d = dict(src_dict)
        version = ServiceVersion.from_dict(d.pop("version"))

        services = []
        _services = d.pop("services")
        for services_item_data in _services:
            services_item = AboutService.from_dict(services_item_data)

            services.append(services_item)

        _rendering_service_2 = d.pop("renderingService2", UNSET)
        rendering_service_2: RenderingService | Unset
        if isinstance(_rendering_service_2, Unset):
            rendering_service_2 = UNSET
        else:
            rendering_service_2 = RenderingService.from_dict(_rendering_service_2)

        _plugins = d.pop("plugins", UNSET)
        plugins: list[PluginInfo] | Unset = UNSET
        if _plugins is not UNSET:
            plugins = []
            for plugins_item_data in _plugins:
                plugins_item = PluginInfo.from_dict(plugins_item_data)

                plugins.append(plugins_item)

        _features = d.pop("features", UNSET)
        features: list[FeatureInfo] | Unset = UNSET
        if _features is not UNSET:
            features = []
            for features_item_data in _features:
                features_item = FeatureInfo.from_dict(features_item_data)

                features.append(features_item)

        signature_algorithms = cast(list[str], d.pop("signatureAlgorithms", UNSET))

        default_signature_algorithm = d.pop("defaultSignatureAlgorithm", UNSET)

        themes_url = d.pop("themesUrl", UNSET)

        last_cache_update = d.pop("lastCacheUpdate", UNSET)

        about = cls(
            version=version,
            services=services,
            rendering_service_2=rendering_service_2,
            plugins=plugins,
            features=features,
            signature_algorithms=signature_algorithms,
            default_signature_algorithm=default_signature_algorithm,
            themes_url=themes_url,
            last_cache_update=last_cache_update,
        )

        about.additional_properties = d
        return about

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
