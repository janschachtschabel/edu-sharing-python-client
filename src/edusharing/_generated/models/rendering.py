from __future__ import annotations

from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Self, TypeVar

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

if TYPE_CHECKING:
    from ..models.rendering_gdpr import RenderingGdpr


T = TypeVar("T", bound="Rendering")


@_attrs_define
class Rendering:
    """Rendering settings (show preview, show download button, prerender content)

    Attributes:
        show_preview (bool | Unset): If true (default), show preview area with image on gray background
        show_download_button (bool | Unset): If true (default: false), show download button in preview area
        prerender (bool | Unset): If true (default), prerender files automatically after upload (DEPRECATED: configure
            in backend)
        gdpr (list[RenderingGdpr] | Unset): GDPR configuration for rendering privacy
    """

    show_preview: bool | Unset = UNSET
    show_download_button: bool | Unset = UNSET
    prerender: bool | Unset = UNSET
    gdpr: list[RenderingGdpr] | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)

    def to_dict(self) -> dict[str, Any]:
        show_preview = self.show_preview

        show_download_button = self.show_download_button

        prerender = self.prerender

        gdpr: list[dict[str, Any]] | Unset = UNSET
        if not isinstance(self.gdpr, Unset):
            gdpr = []
            for gdpr_item_data in self.gdpr:
                gdpr_item = gdpr_item_data.to_dict()
                gdpr.append(gdpr_item)

        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({})
        if show_preview is not UNSET:
            field_dict["showPreview"] = show_preview
        if show_download_button is not UNSET:
            field_dict["showDownloadButton"] = show_download_button
        if prerender is not UNSET:
            field_dict["prerender"] = prerender
        if gdpr is not UNSET:
            field_dict["gdpr"] = gdpr

        return field_dict

    @classmethod
    def from_dict(cls, src_dict: Mapping[str, Any]) -> Self:
        from ..models.rendering_gdpr import RenderingGdpr

        d = dict(src_dict)
        show_preview = d.pop("showPreview", UNSET)

        show_download_button = d.pop("showDownloadButton", UNSET)

        prerender = d.pop("prerender", UNSET)

        _gdpr = d.pop("gdpr", UNSET)
        gdpr: list[RenderingGdpr] | Unset = UNSET
        if _gdpr is not UNSET:
            gdpr = []
            for gdpr_item_data in _gdpr:
                gdpr_item = RenderingGdpr.from_dict(gdpr_item_data)

                gdpr.append(gdpr_item)

        rendering = cls(
            show_preview=show_preview,
            show_download_button=show_download_button,
            prerender=prerender,
            gdpr=gdpr,
        )

        rendering.additional_properties = d
        return rendering

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
