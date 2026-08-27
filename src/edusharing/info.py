"""Wertobjekte fuer die Auskuenfte einer Instanz.

Getrennt von ``repository``, weil sie eine eigene Frage beantworten -- *was ist
das fuer ein Repositorium und als wer arbeite ich darin* -- und weil
``repository`` sonst zum Sammelbecken wird, sobald die Node-Operationen
dazukommen.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ["About", "Identity", "MetadataSet", "GUEST_AUTHORITY"]

#: Wie edu-sharing den nicht angemeldeten Zugriff nennt. Der Wert ist
#: instanzseitig konfigurierbar (``repository.guest.username``); ``esguest`` ist
#: die Vorgabe und das, was auf den geprueften Instanzen zurueckkommt.
GUEST_AUTHORITY = "esguest"


@dataclass(frozen=True)
class About:
    """Auskunft ueber die Instanz, aus ``GET /_about``.

    ``services``, ``plugins`` und ``features`` sind der Weg, Faehigkeiten zu
    pruefen, statt sie vorauszusetzen -- etwa ob diese Instanz die b-api
    mitbringt.
    """

    repository_version: str | None = None
    renderservice_version: str | None = None
    api_version: str | None = None
    services: list[str] = field(default_factory=list)
    plugins: list[str] = field(default_factory=list)
    features: list[str] = field(default_factory=list)
    themes_url: str | None = None
    #: Die vollstaendige Antwort, fuer alles hier nicht Abgebildete.
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> About:
        version = data.get("version") or {}
        major, minor = version.get("major"), version.get("minor")
        return cls(
            repository_version=version.get("repository"),
            renderservice_version=version.get("renderservice"),
            api_version=f"{major}.{minor}" if major is not None else None,
            services=[s.get("name") for s in (data.get("services") or []) if s.get("name")],
            plugins=[p.get("id") for p in (data.get("plugins") or []) if p.get("id")],
            features=[f.get("id") for f in (data.get("features") or []) if f.get("id")],
            themes_url=data.get("themesUrl"),
            raw=data,
        )


@dataclass(frozen=True, slots=True)
class MetadataSet:
    """Ein Metadatensatz, den diese Instanz fuehrt.

    Welcher der richtige ist, entscheidet die Anwendung: die Wahl aendert,
    welche Properties filterbar sind und was gefunden wird.
    """

    id: str
    name: str


@dataclass(frozen=True)
class Identity:
    """Als wer die Anwendung gerade arbeitet, aus ``GET /iam/v1/people/-home-/-me-``."""

    authority: str
    username: str
    display_name: str
    is_anonymous: bool
    raw: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> Identity:
        person = data.get("person") or {}
        authority = person.get("authorityName") or ""
        profile = person.get("profile") or {}
        name = " ".join(
            teil for teil in (profile.get("firstName"), profile.get("lastName")) if teil
        )
        return cls(
            authority=authority,
            username=person.get("userName") or authority,
            display_name=name or authority,
            is_anonymous=authority == GUEST_AUTHORITY,
            raw=data,
        )
