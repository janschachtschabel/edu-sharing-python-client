"""Vokabularwerte -- Labels statt URIs, gefragt statt mitgeliefert.

Hier entscheidet sich, ob die Bibliothek an eine Instanz gebunden ist. Ein
eingebautes Faecher-Verzeichnis waere bequem und waere fuer jedes Repositorium
ausser einem falsch. Also wird gefragt::

    POST /mds/v1/metadatasets/{repo}/{mds}/values
    {"valueParameters": {"query": "ngsearch", "property": "ccm:taxonid",
                         "pattern": ""}, "criteria": []}

Zwei Eigenheiten, beide gemessen (edu-sharing 11.0, Staging, 27.08.2026):

* **``pattern: ""`` listet alles.** Das naheliegende ``"-all-"`` liefert eine
  leere Liste -- lautlos, also ohne dass etwas auf den Fehler hinweist.
* **Die Antwortform weicht von der OpenAPI-Spezifikation ab.** Die deklariert
  ``MdsValue {id, caption}``; geliefert wird ``{key, displayString}``. Wer sich
  hier auf die generierte Schicht verlaesst, liest leere Felder.

Aufgeloest wird **exakt**, nie unscharf. Im WLO-MCP ist nachgewiesen, wohin
unscharfes Raten fuehrt: ``bildungsinhalte`` loest dort auf **Bild** auf und
verwandelt eine Themensuche in eine Bildersuche. Ein ``None`` mit einem
Vorschlag aus ``suggest()`` ist ehrlicher.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from .transport import Transport

__all__ = ["VocabularyValue", "Vocabulary"]

DEFAULT_METADATASET = "-default-"
DEFAULT_QUERY = "ngsearch"

#: ``pattern`` fuer "alle Werte" -- siehe Modul-Docstring.
_ALLE = ""


@dataclass(frozen=True, slots=True)
class VocabularyValue:
    """Ein Wert aus einem kontrollierten Vokabular."""

    #: Der Wert, auf den das Repositorium filtert (meist eine SKOS-URI).
    uri: str
    #: Die menschenlesbare Form in der angefragten Sprache.
    label: str

    def __str__(self) -> str:
        return self.label


def _ist_uri(wert: str) -> bool:
    return wert.startswith(("http://", "https://"))


class Vocabulary:
    """Vokabularzugriff fuer einen Metadatensatz.

    Args:
        transport: die Verbindung zum Repositorium.
        metadataset: Metadatensatz, gegen den aufgeloest wird. ``-default-``
            ist der von der Instanz vorgegebene.
        query: Abfragekontext, in dem die Property definiert ist. ``ngsearch``
            ist die edu-sharing-Konvention; der Name steht **nicht** im MDS und
            laesst sich daher nicht ermitteln, nur setzen.
    """

    def __init__(
        self,
        transport: Transport,
        *,
        metadataset: str = DEFAULT_METADATASET,
        query: str = DEFAULT_QUERY,
    ) -> None:
        self._transport = transport
        self.metadataset = metadataset
        self.query = query
        self._cache: dict[tuple[str, str | None], list[VocabularyValue]] = {}
        self._locks: dict[tuple[str, str | None], asyncio.Lock] = {}

    # --- Werte ------------------------------------------------------------

    async def values(
        self, prop: str, *, locale: str | None = None
    ) -> list[VocabularyValue]:
        """Alle Werte, die diese Instanz fuer ``prop`` kennt.

        Das Ergebnis wird zwischengespeichert -- Vokabulare aendern sich selten,
        und dieselbe Property wird bei einem Fan-out vielfach gebraucht. Ein
        Fehlschlag landet nicht im Cache.

        Args:
            prop: Property-Name, etwa ``ccm:taxonid``.
            locale: Sprache der Labels, etwa ``en_EN``. Getrennt gecacht.

        Returns:
            Leere Liste, wenn die Property kein Vokabular hat.
        """
        schluessel = (prop, locale)
        if schluessel in self._cache:
            return self._cache[schluessel]

        # Ohne Sperre laedt bei gleichzeitigen Zugriffen jeder dasselbe
        # Vokabular einzeln -- bei einem Fan-out also vielfach.
        lock = self._locks.setdefault(schluessel, asyncio.Lock())
        async with lock:
            if schluessel in self._cache:
                return self._cache[schluessel]
            werte = await self._fetch(prop, _ALLE, locale)
            self._cache[schluessel] = werte
            return werte

    async def suggest(
        self, prop: str, text: str, *, locale: str | None = None
    ) -> list[VocabularyValue]:
        """Werte, deren Label ``text`` **enthaelt** -- serverseitige Suche.

        Teilstring, nicht Praefix: gemessen liefert ``"ysik"`` Physik,
        Atomphysik und Kernphysik. Wer ein Typeahead darauf baut, bekommt also
        auch Treffer, die nicht mit der Eingabe beginnen -- das ist meist
        erwuenscht, sollte aber bekannt sein.

        Nicht gecacht: jede Eingabe ist eine eigene Anfrage, ein Cache darueber
        wuerde nur Speicher fuellen.
        """
        return await self._fetch(prop, text, locale)

    async def resolve(
        self, prop: str, label_oder_uri: str, *, locale: str | None = None
    ) -> str | None:
        """Uebersetze ein Label in den Wert, auf den das Repositorium filtert.

        Args:
            label_oder_uri: ein Label (``"Physik"``) oder bereits eine URI --
                letztere wird unveraendert durchgereicht, ohne Anfrage.

        Returns:
            Den Filterwert, oder ``None``, wenn das Label unbekannt ist. Kein
            unscharfer Abgleich: ein falsch geratener Wert schraenkt die Suche
            auf etwas ein, das niemand angefragt hat. Fuer eine Rueckfrage
            liefert ``suggest()`` Vorschlaege.
        """
        wert = label_oder_uri.strip()
        if _ist_uri(wert):
            return wert
        gesucht = wert.casefold()
        for eintrag in await self.values(prop, locale=locale):
            if eintrag.label.strip().casefold() == gesucht:
                return eintrag.uri
        return None

    def clear_cache(self) -> None:
        """Verwirf die zwischengespeicherten Vokabulare."""
        self._cache.clear()

    # --- intern -----------------------------------------------------------

    async def _fetch(
        self, prop: str, pattern: str, locale: str | None
    ) -> list[VocabularyValue]:
        antwort = await self._transport.json(
            "POST",
            f"/mds/v1/metadatasets/-home-/{self.metadataset}/values",
            json={
                "valueParameters": {
                    "query": self.query,
                    "property": prop,
                    "pattern": pattern,
                },
                # Pflichtfeld, verengt aber nicht: gemessen liefert die Abfrage
                # mit und ohne Kriterien dieselben 416 Werte. Es ist eine
                # Vokabularliste, keine kontextabhaengige Vorschlagsliste.
                "criteria": [],
            },
            headers={"locale": locale} if locale else None,
        )
        return [
            VocabularyValue(uri=eintrag["key"], label=eintrag.get("displayString") or "")
            for eintrag in (antwort.get("values") or [])
            if eintrag.get("key")
        ]

    def __repr__(self) -> str:
        return f"Vocabulary(metadataset={self.metadataset!r}, query={self.query!r})"
