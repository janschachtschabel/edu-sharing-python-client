"""Der eine Weg nach draussen.

Jede Anfrage an ein Repositorium laeuft hier durch. Das ist kein Selbstzweck:
drei Entscheidungen muessen an genau einer Stelle getroffen werden, sonst
driften ihre Kopien auseinander.

**Wer das Passwort bekommt.** Zugangsdaten gehen ausschliesslich an die
konfigurierte Repository-URL. Absolute URLs stammen teils aus Antwortdaten
(Vorschaubilder, Downloads), und eine davon kann woanders hinzeigen.

**Was wiederholt wird.** Nur, was bei einer Wiederholung gelingen kann. Die
Entscheidung faellt ueber den Fehlertyp aus ``errors``, nicht ueber den
Statuscode -- weil bei edu-sharing ein HTTP 500 auch schlicht "nicht
angemeldet" heissen kann.

**Wie viel gleichzeitig laeuft.** Ein Fan-out ueber viele Knoten erzeugt sonst
mehr Last, als das Repositorium vertraegt.
"""

from __future__ import annotations

import asyncio
from typing import Any, Self

import httpx

from .auth import ANONYMOUS, Credential, credential_from
from .errors import EduSharingError, ServerError, TransportError, error_from_response
from .urls import normalize_repository_url, rest_base

__all__ = ["Transport"]

DEFAULT_TIMEOUT = 30.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_MAX_CONCURRENCY = 8
DEFAULT_BACKOFF_BASE = 0.5


def _mindestens(name: str, wert: float, grenze: float) -> None:
    """Weise einen Parameter ab, der keinen sinnvollen Betrieb ergibt.

    Frueh und laut, statt spaeter und raetselhaft: ``max_retries=-1`` etwa
    wuerde die Wiederholungsschleife gar nicht erst betreten, und der Aufrufer
    saehe einen Fehler ohne jede Ursache.
    """
    if wert < grenze:
        raise EduSharingError(
            f"{name}={wert!r} ist nicht zulaessig -- erwartet wird mindestens {grenze}."
        )


class Transport:
    """HTTP-Zugang zu einem edu-sharing-Repositorium.

    Args:
        repository_url: Adresse des Repositoriums in beliebiger der ueblichen
            Schreibweisen; wird normalisiert.
        credential: Vorgabe fuer alle Anfragen. Pro Anfrage ueberschreibbar.
        timeout: Sekunden bis zum Abbruch einer einzelnen Anfrage.
        max_retries: Wiederholungen zusaetzlich zum ersten Versuch.
        max_concurrency: gleichzeitig laufende Anfragen.
        backoff_base: Grundwert der Wartezeit; verdoppelt sich je Versuch.
        client: eigener httpx-Client, etwa fuer Tests.
    """

    def __init__(
        self,
        repository_url: str,
        *,
        credential: object = ANONYMOUS,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        _mindestens("timeout", timeout, 0.001)
        _mindestens("max_retries", max_retries, 0)
        _mindestens("max_concurrency", max_concurrency, 1)
        _mindestens("backoff_base", backoff_base, 0)

        self.repository_url = normalize_repository_url(repository_url)
        self.rest_url = rest_base(self.repository_url)
        self.credential = credential_from(credential)
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._client = client or httpx.AsyncClient(timeout=timeout)
        self._owns_client = client is None

    # --- Lebenszyklus -----------------------------------------------------

    async def aclose(self) -> None:
        """Schliesse den Client, sofern er hier angelegt wurde."""
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    # --- Grenze: wer bekommt die Zugangsdaten -----------------------------

    def is_repository_url(self, url: str) -> bool:
        """Ob ``url`` das konfigurierte Repositorium anspricht.

        Praefix UND Grenze, damit ein aehnlich benannter Host
        (``https://repo.example.test.angreifer.test``) nicht durchrutscht.
        """
        base = self.repository_url
        return url == base or url.startswith((f"{base}/", f"{base}?"))

    def _resolve(self, path: str) -> str:
        """Relative Pfade an die REST-Wurzel haengen, absolute unveraendert lassen."""
        if path.startswith(("http://", "https://")):
            return path
        return f"{self.rest_url}{path if path.startswith('/') else '/' + path}"

    def _headers(
        self, url: str, credential: Credential, extra: dict[str, str] | None
    ) -> dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.is_repository_url(url):
            headers.update(credential.headers())
        if extra:
            headers.update(extra)
        return headers

    # --- Anfragen ---------------------------------------------------------

    async def request(
        self,
        method: str,
        path: str,
        *,
        credential: object | None = None,
        params: dict[str, Any] | None = None,
        json: Any = None,
        content: bytes | str | None = None,
        files: Any = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        """Stelle eine Anfrage und gib die Antwort zurueck.

        Args:
            path: Pfad relativ zur REST-Wurzel (``/_about``) oder absolute URL.
            credential: Zugangsdaten nur fuer diese Anfrage.

        Raises:
            EduSharingError: bei jedem Status ab 400, als passender Untertyp.
            TransportError: wenn die Anfrage den Server nicht erreicht hat.
        """
        url = self._resolve(path)
        cred = self.credential if credential is None else credential_from(credential)
        request_headers = self._headers(url, cred, headers)

        letzter: EduSharingError | None = None
        for versuch in range(self.max_retries + 1):
            if versuch:
                await asyncio.sleep(self.backoff_base * (2 ** (versuch - 1)))
            try:
                async with self._semaphore:
                    response = await self._client.request(
                        method, url,
                        params=params, json=json, content=content,
                        files=files, headers=request_headers,
                    )
            except httpx.HTTPError as exc:
                # Netzwerkebene: Timeout, DNS, TLS, Verbindungsabbruch.
                letzter = TransportError(
                    f"{type(exc).__name__}: {exc}", url=url,
                )
                continue

            if response.status_code < 400:
                return response

            letzter = error_from_response(response.status_code, url, response.text)
            # Wiederholt wird nur, was der Server voruebergehend nicht
            # leisten konnte. Ein 500, das in Wahrheit "nicht angemeldet"
            # heisst, ist bereits als AuthenticationError klassifiziert und
            # faellt hier nicht mehr unter ServerError.
            if not isinstance(letzter, ServerError):
                raise letzter

        # ``max_retries >= 0`` ist im Konstruktor geprueft, die Schleife laeuft
        # also mindestens einmal und hat ``letzter`` in jedem Zweig gesetzt, der
        # nicht selbst zurueckkehrt oder wirft.
        raise letzter

    async def json(self, method: str, path: str, **kwargs: Any) -> Any:
        """Wie ``request``, gibt aber den geparsten JSON-Koerper zurueck."""
        response = await self.request(method, path, **kwargs)
        return response.json()

    def __repr__(self) -> str:
        return f"Transport({self.repository_url!r})"
