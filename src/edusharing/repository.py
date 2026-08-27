"""Der Einstieg: eine Verbindung zu einem edu-sharing-Repositorium.

``AsyncRepository`` ist die eigentliche Umsetzung, ``Repository`` reicht sie
synchron durch. Beide bieten in dieser Etappe zwei Auskuenfte:

* ``about()`` -- was ist das fuer eine Instanz, und was kann sie?
* ``whoami()`` -- als wer laufe ich hier eigentlich?

Die zweite ist wichtiger, als sie klingt. Ohne sie merkt eine Anwendung nicht,
dass sie als Gast arbeitet, und stolpert stattdessen irgendwann ueber ein
HTTP 500 an einer Stelle, die mit der Ursache nichts zu tun hat.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any, Self

import httpx

from ._sync import LoopThread
from .auth import ANONYMOUS, BasicCredential, Credential, credential_from
from .collections import Collections
from .errors import EduSharingError
from .search import Search, SearchResult
from .transport import (
    DEFAULT_BACKOFF_BASE,
    DEFAULT_MAX_CONCURRENCY,
    DEFAULT_MAX_RETRIES,
    DEFAULT_TIMEOUT,
    Transport,
)
from .vocab import DEFAULT_METADATASET, DEFAULT_QUERY, Vocabulary

__all__ = ["AsyncRepository", "Repository", "About", "Identity", "MetadataSet"]

ENV_URL = "EDU_SHARING_URL"

#: Wie edu-sharing den nicht angemeldeten Zugriff nennt. Der Wert ist
#: instanzseitig konfigurierbar (``repository.guest.username``); ``esguest`` ist
#: die Vorgabe und das, was auf den geprueften Instanzen zurueckkommt.
GUEST_AUTHORITY = "esguest"


def _url_aus_umgebung(cls: type) -> str:
    """Lies ``EDU_SHARING_URL``. Gemeinsam fuer beide Zugaenge, damit ihr
    Verhalten nicht auseinanderlaeuft.

    Raises:
        EduSharingError: wenn die Variable fehlt. Die Meldung nennt den Aufruf
            der Klasse, die gerade verwendet wird.
    """
    url = os.environ.get(ENV_URL)
    if not url:
        raise EduSharingError(
            f"{ENV_URL} ist nicht gesetzt. Entweder die Variable setzen oder "
            f"die Adresse direkt uebergeben: {cls.__name__}('https://...')."
        )
    return url


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


class AsyncRepository:
    """Verbindung zu einem edu-sharing-Repositorium.

    Args:
        url: Adresse in beliebiger der ueblichen Schreibweisen.
        auth: ``None`` (anonym), ein ``(benutzer, passwort)``-Paar oder ein
            fertiges ``Credential``. Ein Bearer-Token wird abgelehnt.
        metadataset: Metadatensatz fuer Vokabular und Suche. ``-default-`` ist
            der von der Instanz vorgegebene; eine Instanz kann mehrere fuehren,
            und die Wahl aendert, was gefunden wird (gemessen auf Staging:
            ``-default-`` findet 2825 Treffer fuer "Physik", ``mds_oeh`` 17994).
        query: Abfragekontext fuer Vokabular und Suche, per Konvention
            ``ngsearch``.
        field_aliases: Kurznamen fuer Filter-Properties (``fach`` ->
            ``ccm:taxonid``). ``None`` nimmt die Vorgabe.
        timeout: Sekunden bis zum Abbruch einer Anfrage.
        max_retries: Wiederholungen zusaetzlich zum ersten Versuch.
        max_concurrency: gleichzeitig laufende Anfragen.
        backoff_base: Grundwert der Wartezeit zwischen Wiederholungen.
        client: eigener httpx-Client, etwa fuer Tests.
    """

    def __init__(
        self,
        url: str,
        *,
        auth: object = None,
        metadataset: str = DEFAULT_METADATASET,
        query: str = DEFAULT_QUERY,
        field_aliases: dict[str, str] | None = None,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._transport = Transport(
            url,
            credential=credential_from(auth) if auth is not None else ANONYMOUS,
            timeout=timeout,
            max_retries=max_retries,
            max_concurrency=max_concurrency,
            backoff_base=backoff_base,
            client=client,
        )
        self.metadataset = metadataset
        self.query = query
        # Einmal angelegt und behalten: der Vokabular-Cache lebt darin, und ein
        # frisches Objekt je Zugriff wuerde ihn bei jedem Aufruf verwerfen.
        self._vocab = Vocabulary(self._transport, metadataset=metadataset, query=query)
        self._search = Search(
            self._transport, self._vocab,
            metadataset=metadataset, query=query, field_aliases=field_aliases,
        )
        self._collections = Collections(self._transport, metadataset=metadataset)

    @classmethod
    def from_env(cls, **kwargs: Any) -> AsyncRepository:
        """Baue eine Verbindung aus ``EDU_SHARING_URL`` und den Zugangsdaten.

        Raises:
            EduSharingError: wenn ``EDU_SHARING_URL`` fehlt, oder wenn von
                Benutzername und Passwort nur eines gesetzt ist.
        """
        return cls(_url_aus_umgebung(cls), auth=BasicCredential.from_env(), **kwargs)

    # --- Zustand ----------------------------------------------------------

    @property
    def url(self) -> str:
        """Die normalisierte Repository-URL."""
        return self._transport.repository_url

    @property
    def credential(self) -> Credential:
        """Die Zugangsdaten, die ohne anderslautende Angabe verwendet werden."""
        return self._transport.credential

    @property
    def raw(self) -> Transport:
        """Der Transport, fuer Endpunkte ohne eigene Methode.

        ``await repo.raw.json("GET", "/config/v1/values")``
        """
        return self._transport

    @property
    def vocab(self) -> Vocabulary:
        """Vokabularwerte dieser Instanz -- Labels statt URIs.

        ``await repo.vocab.resolve("ccm:taxonid", "Physik")``
        """
        return self._vocab

    @property
    def searcher(self) -> Search:
        """Die Suchschicht, fuer Zugriff auf ihre Einstellungen."""
        return self._search

    @property
    def collections(self) -> Collections:
        """Die Sammlungssuche, fuer Zugriff auf ihre Einstellungen."""
        return self._collections

    # --- Suchen -----------------------------------------------------------

    async def search(self, text: str | None = None, **kwargs: Any) -> SearchResult:
        """Suche Material. Siehe ``Search.search`` fuer alle Parameter.

        ``await repo.search("Photosynthese", fach="Biologie")``

        Das Ergebnis traegt ``unresolved``: ist es nicht leer, konnte ein Filter
        nicht aufgeloest werden und das Ergebnis ist breiter als angefragt.
        """
        return await self._search.search(text, **kwargs)

    async def find_collections(self, text: str, **kwargs: Any) -> SearchResult:
        """Suche Sammlungen ueber beide Wege, die edu-sharing dafuer hat.

        ``total`` ist eine Untergrenze -- siehe ``collections``.
        """
        return await self._collections.find(text, **kwargs)

    # --- Auskuenfte -------------------------------------------------------

    async def about(self) -> About:
        """Version, Dienste, Plugins und Merkmale dieser Instanz."""
        return About.from_response(await self._transport.json("GET", "/_about"))

    async def metadatasets(self) -> list[MetadataSet]:
        """Welche Metadatensaetze diese Instanz fuehrt.

        Billig (wenige hundert Byte) -- im Gegensatz zum Metadatensatz selbst,
        der bei ``mds_oeh`` 17 MB umfasst.
        """
        antwort = await self._transport.json("GET", "/mds/v1/metadatasets/-home-")
        return [
            MetadataSet(id=m.get("id") or "", name=m.get("name") or "")
            for m in (antwort.get("metadatasets") or [])
            if m.get("id")
        ]

    async def whoami(self) -> Identity:
        """Als wer diese Verbindung arbeitet.

        Anonym ist kein Fehler, sondern ein gueltiger Betriebsfall -- aber die
        Anwendung sollte es wissen, statt es zu vermuten.
        """
        data = await self._transport.json("GET", "/iam/v1/people/-home-/-me-")
        return Identity.from_response(data)

    # --- Lebenszyklus -----------------------------------------------------

    async def aclose(self) -> None:
        await self._transport.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    def __repr__(self) -> str:
        return f"AsyncRepository({self.url!r})"


class Repository:
    """Synchroner Zugang -- fuer Skripte und Notebooks.

    Gleiche Signatur wie ``AsyncRepository``. Die Aufrufe laufen in einem
    eigenen Hintergrund-Loop, damit sie auch dort funktionieren, wo bereits ein
    Event-Loop laeuft.
    """

    def __init__(self, url: str, **kwargs: Any) -> None:
        self._loop = LoopThread()
        self._async = AsyncRepository(url, **kwargs)

    @classmethod
    def from_env(cls, **kwargs: Any) -> Repository:
        """Wie ``AsyncRepository.from_env``."""
        return cls(_url_aus_umgebung(cls), auth=BasicCredential.from_env(), **kwargs)

    @property
    def url(self) -> str:
        return self._async.url

    @property
    def credential(self) -> Credential:
        return self._async.credential

    @property
    def metadataset(self) -> str:
        return self._async.metadataset

    @property
    def vocab(self) -> Vocabulary:
        """Vokabularwerte dieser Instanz. Die Methoden sind asynchron --
        fuer den synchronen Weg siehe ``resolve()``."""
        return self._async.vocab

    @property
    def searcher(self) -> Search:
        """Die Suchschicht, fuer Zugriff auf ihre Einstellungen."""
        return self._async.searcher

    def search(self, text: str | None = None, **kwargs: Any) -> SearchResult:
        """Suche Material. Siehe ``Search.search`` fuer alle Parameter."""
        return self._loop.run(self._async.search(text, **kwargs))

    @property
    def collections(self) -> Collections:
        """Die Sammlungssuche, fuer Zugriff auf ihre Einstellungen."""
        return self._async.collections

    def find_collections(self, text: str, **kwargs: Any) -> SearchResult:
        """Suche Sammlungen ueber beide Wege. ``total`` ist eine Untergrenze."""
        return self._loop.run(self._async.find_collections(text, **kwargs))

    def resolve(self, prop: str, label: str, *, locale: str | None = None) -> str | None:
        """Uebersetze ein Label in den Wert, auf den das Repositorium filtert."""
        return self._loop.run(self._async.vocab.resolve(prop, label, locale=locale))

    def about(self) -> About:
        """Version, Dienste, Plugins und Merkmale dieser Instanz."""
        return self._loop.run(self._async.about())

    def whoami(self) -> Identity:
        """Als wer diese Verbindung arbeitet."""
        return self._loop.run(self._async.whoami())

    def metadatasets(self) -> list[MetadataSet]:
        """Welche Metadatensaetze diese Instanz fuehrt."""
        return self._loop.run(self._async.metadatasets())

    def close(self) -> None:
        try:
            self._loop.run(self._async.aclose())
        finally:
            self._loop.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, *exc_info: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"Repository({self.url!r})"
