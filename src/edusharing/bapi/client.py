"""Zugang zur b-api, dem LLM-Gateway von OpenEduHub.

Gemessen gegen Staging:

* **Auth per ``X-API-KEY``**, nicht per Bearer -- die gespiegelte Falle zu
  edu-sharing, wo Basic gilt und ein Bearer ignoriert wird.
* **Zwei Provider**: ``academiccloud`` (mit Auslastungsangabe ``demand``) und
  ``openai`` (ohne). Ein dritter Name endet mit ``400 Provider ... not found``.
* **Keine Quoten-Header und kein ``retry-after``.** Ein Client sieht sein
  Restkontingent nicht und merkt ein Limit erst am Fehler; moeglich ist nur
  exponentielles Warten.
* **Kein OpenAPI-Dokument.** ``/openapi.json``, ``/docs`` und ``/health``
  liefern das Angular-Frontend. Die Endpunkte muss man kennen.

Eigener HTTP-Zugang statt des edu-sharing-``Transport``: dessen
Zugangsdaten-Grenze und Fehlerzuordnung sind auf ein Repositorium
zugeschnitten (Basic-Auth, ``DAO*``-Ausnahmen). Ihn dafuer zu
parametrisieren haette beide Seiten unklarer gemacht. Die Wiederholungslogik
aehnelt sich; kaeme ein dritter Nutzer dazu, waere sie es wert, herausgezogen
zu werden.
"""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any, Self

import httpx

from ..errors import EduSharingError, error_from_response
from .policy import Model, build_body, pick_model, rank_models, read_answer

__all__ = ["BildungsAPI"]

ENV_KEY = "B_API_KEY"
ENV_BASE_URL = "B_API_BASE_URL"

DEFAULT_BASE_URL = "https://b-api.staging.openeduhub.net"
DEFAULT_PROVIDER = "academiccloud"

#: Gemessen 21.08.2026: bis 26 gleichzeitige Anfragen fehlerfrei, ab 19
#: vereinzelt 502. Die Grenze ist NICHT stabil -- am 12.08. lag sie bei 2.
#: Vor einer Kapazitaetsplanung neu messen.
DEFAULT_MAX_CONCURRENCY = 6

#: Einzelne Anfragen hingen bis zu 94 s in der Warteschlange.
DEFAULT_TIMEOUT = 180.0
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE = 2.5

#: ``demand`` schwankt im Minutentakt -- ein langer Cache traefe die Modellwahl
#: auf veralteten Zahlen. Ganz ohne Cache kostet jeder Aufruf eine zusaetzliche
#: Anfrage.
DEFAULT_MODELS_CACHE_SECONDS = 30.0

#: Statuscodes, bei denen ein zweiter Versuch gelingen kann. 404 ist bewusst
#: nicht dabei: "This is not a chat model" wird beim vierten Mal nicht besser.
WIEDERHOLBAR = frozenset({429, 500, 502, 503, 504})

#: Wie viele Modelle bei automatischer Wahl nacheinander versucht werden.
#: Gemessen: ein Modell kann ``status: ready`` melden und trotzdem nicht
#: antworten (``503 Model pricing unavailable``). Bei fester Modell-ID wird
#: **nicht** ausgewichen -- das waere ein stiller Austausch.
DEFAULT_MODEL_ATTEMPTS = 3


class BildungsAPI:
    """Client fuer die b-api.

    Args:
        api_key: der Schluessel. Pflicht.
        base_url: Gateway-Adresse.
        provider: ``academiccloud`` oder ``openai``.
        max_concurrency: gleichzeitige Anfragen.
        models_cache_seconds: wie lange die Modellliste gilt. ``0`` schaltet
            den Cache ab.
    """

    def __init__(
        self,
        api_key: str,
        *,
        base_url: str = DEFAULT_BASE_URL,
        provider: str = DEFAULT_PROVIDER,
        timeout: float = DEFAULT_TIMEOUT,
        max_retries: int = DEFAULT_MAX_RETRIES,
        max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        models_cache_seconds: float = DEFAULT_MODELS_CACHE_SECONDS,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        if not api_key:
            raise EduSharingError(
                f"Die b-api braucht einen Schluessel. Entweder {ENV_KEY} setzen "
                "oder BildungsAPI(api_key=...) uebergeben."
            )
        self._api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.provider = provider
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.models_cache_seconds = models_cache_seconds
        self._semaphore = asyncio.Semaphore(max_concurrency)
        self._client = client or httpx.AsyncClient(timeout=timeout)
        self._owns_client = client is None
        self._models_cache: tuple[float, list[Model]] | None = None
        self._models_lock = asyncio.Lock()
        #: Das Modell, von dem die letzte Antwort kam. Bei automatischer Wahl
        #: die einzige Stelle, an der ablesbar ist, wessen Antwort man liest.
        self.last_model: str | None = None

    @classmethod
    def from_env(cls, **kwargs: Any) -> BildungsAPI:
        """Baue einen Client aus ``B_API_KEY`` und optional ``B_API_BASE_URL``."""
        schluessel = os.environ.get(ENV_KEY, "")
        if not schluessel:
            raise EduSharingError(
                f"{ENV_KEY} ist nicht gesetzt. Entweder die Variable setzen oder "
                "den Schluessel uebergeben: BildungsAPI(api_key=...)."
            )
        kwargs.setdefault("base_url", os.environ.get(ENV_BASE_URL) or DEFAULT_BASE_URL)
        return cls(schluessel, **kwargs)

    # --- Lebenszyklus -----------------------------------------------------

    async def aclose(self) -> None:
        if self._owns_client:
            await self._client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()

    # --- Anfragen ---------------------------------------------------------

    async def models(self, provider: str | None = None) -> list[Model]:
        """Die Modelle dieses Providers, mit Auslastung sofern gemeldet."""
        anbieter = provider or self.provider
        jetzt = time.monotonic()

        if (
            self.models_cache_seconds > 0
            and self._models_cache
            and anbieter == self.provider
            and jetzt - self._models_cache[0] < self.models_cache_seconds
        ):
            return self._models_cache[1]

        async with self._models_lock:
            antwort = await self._request("GET", f"/api/v1/llm/{anbieter}/models")
            roh = antwort.get("data") if isinstance(antwort, dict) else antwort
            modelle = [Model.from_response(m) for m in (roh or [])]
            if anbieter == self.provider:
                self._models_cache = (jetzt, modelle)
            return modelle

    async def chat(
        self,
        prompt: str | list[dict[str, str]],
        *,
        model: str | None = None,
        provider: str | None = None,
        max_tokens: int = 1000,
        temperature: float = 0.0,
        thinking: bool = False,
        system: str | None = None,
    ) -> str:
        """Stelle eine Anfrage und gib den Antworttext zurueck.

        Args:
            prompt: ein Text oder eine fertige Nachrichtenliste.
            model: feste Modell-ID. Ohne Angabe wird die Modellliste geholt und
                das am wenigsten ausgelastete bereite Textmodell gewaehlt --
                das kostet eine zusaetzliche Anfrage, trifft die Wahl aber auf
                aktuellen Zahlen.
            system: Systemnachricht; nur wirksam, wenn ``prompt`` ein Text ist.
            thinking: Denken bei Qwen3 zulassen. Vorgabe ``False`` -- siehe
                ``policy``.

        Returns:
            Den Antworttext. Ist das Budget fuers Denken draufgegangen, kommt
            der Text aus ``reasoning`` statt aus ``content``.
        """
        if isinstance(prompt, str):
            nachrichten = [{"role": "user", "content": prompt}]
            if system:
                nachrichten.insert(0, {"role": "system", "content": system})
        else:
            nachrichten = prompt

        anbieter = provider or self.provider
        pfad = f"/api/v1/llm/{anbieter}/chat/completions"

        def bauen(mid: str) -> dict[str, Any]:
            return build_body(
                mid, nachrichten,
                max_tokens=max_tokens, temperature=temperature, thinking=thinking,
            )

        if model:
            self.last_model = model
            return read_answer(await self._request("POST", pfad, json=bauen(model)))

        kandidaten = rank_models(await self.models(anbieter))
        if not kandidaten:
            raise EduSharingError(
                f"Kein antwortbereites Textmodell beim Provider {anbieter!r}."
            )

        fehler: list[str] = []
        for kandidat in kandidaten[:DEFAULT_MODEL_ATTEMPTS]:
            try:
                antwort = await self._request("POST", pfad, json=bauen(kandidat.id))
            except EduSharingError as exc:
                # Ein "bereites" Modell kann trotzdem nicht antworten. Wer die
                # Wahl der Bibliothek ueberlassen hat, will eine Antwort --
                # nicht den Hinweis, dass ausgerechnet das erste gerade nicht
                # abrechenbar ist.
                fehler.append(f"{kandidat.id}: {exc}")
                continue
            self.last_model = kandidat.id
            return read_answer(antwort)

        raise EduSharingError(
            "Von den versuchten Modellen antwortete kein einziges. "
            + " | ".join(fehler)
        )

    async def _waehle(self, provider: str) -> Model:
        return pick_model(await self.models(provider))

    async def _request(self, method: str, pfad: str, **kwargs: Any) -> Any:
        url = f"{self.base_url}{pfad}"
        letzter: EduSharingError | None = None

        for versuch in range(self.max_retries + 1):
            if versuch:
                # Kein retry-after im 429 -- exponentiell ist alles, was geht.
                await asyncio.sleep(self.backoff_base * (2 ** (versuch - 1)))
            try:
                async with self._semaphore:
                    antwort = await self._client.request(
                        method, url,
                        headers={"X-API-KEY": self._api_key,
                                 "Accept": "application/json"},
                        **kwargs,
                    )
            except httpx.HTTPError as exc:
                letzter = EduSharingError(f"{type(exc).__name__}: {exc}", url=url)
                continue

            if antwort.status_code < 400:
                return antwort.json()

            letzter = self._fehler(antwort, url)
            if antwort.status_code not in WIEDERHOLBAR:
                raise letzter

        assert letzter is not None
        raise letzter

    def _fehler(self, antwort: httpx.Response, url: str) -> EduSharingError:
        """Baue einen Fehler aus der b-api-Antwort.

        Sie meldet im Feld ``message``, nicht in der edu-sharing-Form -- der
        Text wird deshalb hier uebernommen, statt ihn dort zu suchen.
        """
        try:
            daten = antwort.json()
            meldung = daten.get("message") or daten.get("error") or antwort.text
        except ValueError:
            meldung = antwort.text
        basis = error_from_response(antwort.status_code, url, "")
        return type(basis)(
            f"b-api HTTP {antwort.status_code}: {str(meldung)[:300]}",
            status=antwort.status_code, url=url,
        )

    def __repr__(self) -> str:
        return f"BildungsAPI(base_url={self.base_url!r}, provider={self.provider!r})"
