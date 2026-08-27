"""Sammlungen suchen -- ueber beide Wege, die edu-sharing dafuer hat.

Es gibt zwei voneinander unabhaengige Sammlungs-Suchen, und **keine ist
Obermenge der anderen**. Gemessen (Staging, 27.08.2026, je 25 Treffer):

===========  ===  ===  =========  =====  =====
Suchwort       A    B  gemeinsam  nur A  nur B
===========  ===  ===  =========  =====  =====
Optik          5    4          4      1      0
Deutsch       25   25          **0**   25     25
Grundschule    2    0          0      2      0
Klimawandel   23   17         17      6      0
Physik        25   25         20      5      5
===========  ===  ===  =========  =====  =====

Bei "Deutsch" ist die Schnittmenge **null**: 25 gegen 25 voellig verschiedene
Sammlungen. Wer nur einen Weg nimmt, verliert also systematisch -- und welcher
versagt, haengt am Suchwort, nicht an der Sammlung.

Die beiden Wege:

* **A** ``POST /search/v1/queries/-home-/{mds}/collections?contentType=COLLECTIONS``
  -- liefert ``nodes`` und eine echte ``pagination.total``. ``ngsearch`` selbst
  taugt dafuer nicht: es gibt ueberhaupt keine Sammlungen zurueck.
* **B** ``GET /collection/v1/collections/-home-/search`` -- liefert
  ``collections``, und ``pagination`` ist **null**. Es gibt hier also keine
  Gesamtzahl.

Deshalb ist ``total`` am Ergebnis eine **Untergrenze**: die Summe waere wegen
der Ueberlappung zu hoch, die Zahl aus A allein zu niedrig.
"""

from __future__ import annotations

import asyncio

from .errors import EduSharingError
from .results import SearchHit, SearchResult
from .transport import Transport
from .vocab import DEFAULT_METADATASET

__all__ = ["Collections"]

DEFAULT_LIMIT = 10

#: Abfragename fuer Leg A. Wie ``ngsearch`` eine Konvention des Metadatensatzes.
COLLECTION_QUERY = "collections"


class Collections:
    """Sammlungssuche ueber beide Wege.

    Args:
        transport: die Verbindung zum Repositorium.
        metadataset: Metadatensatz fuer Leg A.
    """

    def __init__(
        self,
        transport: Transport,
        *,
        metadataset: str = DEFAULT_METADATASET,
    ) -> None:
        self._transport = transport
        self.metadataset = metadataset

    async def find(self, text: str, *, limit: int = DEFAULT_LIMIT) -> SearchResult:
        """Suche Sammlungen nach einem Stichwort.

        Beide Wege laufen gleichzeitig; die Ergebnisse werden ueber die
        Knoten-ID zusammengefuehrt.

        Faellt einer der beiden aus -- auf einer fremden Instanz kann ein
        Endpunkt fehlen --, kommt das Ergebnis des anderen zurueck, und der
        Ausfall steht in ``warnings``. Erst wenn **beide** ausfallen, wird der
        Fehler durchgereicht: ein halbes Ergebnis ist brauchbar, ein
        vorgetaeuschtes leeres nicht.

        Returns:
            Ein ``SearchResult`` mit ``total_is_lower_bound=True``.
        """
        leg_a, leg_b = await asyncio.gather(
            self._mds_leg(text, limit),
            self._rest_leg(text, limit),
            return_exceptions=True,
        )

        warnungen: list[str] = []
        treffer: list[SearchHit] = []
        gesehen: set[str] = set()
        total = 0

        if isinstance(leg_a, BaseException):
            warnungen.append(
                f"Die Sammlungsabfrage des Metadatensatzes ({COLLECTION_QUERY}) "
                f"ist fehlgeschlagen: {leg_a}"
            )
        else:
            knoten, total = leg_a
            treffer.extend(self._als_treffer(knoten, gesehen))

        if isinstance(leg_b, BaseException):
            warnungen.append(
                f"Die REST-Sammlungssuche (collection/v1) ist fehlgeschlagen: {leg_b}"
            )
        else:
            treffer.extend(self._als_treffer(leg_b, gesehen))

        if isinstance(leg_a, BaseException) and isinstance(leg_b, BaseException):
            raise EduSharingError(
                "Beide Sammlungs-Suchen sind fehlgeschlagen. "
                f"Metadatensatz-Abfrage: {leg_a} | REST-Suche: {leg_b}"
            )

        return SearchResult(
            hits=treffer,
            total=max(total, len(treffer)),
            total_is_lower_bound=True,
            warnings=warnungen,
        )

    # --- intern -----------------------------------------------------------

    def _als_treffer(
        self, knoten: list[dict], gesehen: set[str]
    ) -> list[SearchHit]:
        """Wandle Knoten in Treffer, ohne bereits gesehene IDs erneut."""
        neu = []
        basis = self._transport.repository_url
        for k in knoten:
            node_id = (k.get("ref") or {}).get("id")
            if not node_id or node_id in gesehen:
                continue
            gesehen.add(node_id)
            neu.append(SearchHit.from_node(k, basis))
        return neu

    async def _mds_leg(self, text: str, limit: int) -> tuple[list[dict], int]:
        """Leg A -- liefert Knoten und eine echte Gesamtzahl."""
        antwort = await self._transport.json(
            "POST",
            f"/search/v1/queries/-home-/{self.metadataset}/{COLLECTION_QUERY}",
            params={
                "contentType": "COLLECTIONS",
                "maxItems": limit,
                "skipCount": 0,
            },
            # Diese Abfrage nimmt ausschliesslich ngsearchword an; jedes andere
            # Kriterium endet mit 400 DAOValidationException.
            json={"criteria": [{"property": "ngsearchword", "values": [text]}]},
        )
        seite = antwort.get("pagination") or {}
        return list(antwort.get("nodes") or []), int(seite.get("total") or 0)

    async def _rest_leg(self, text: str, limit: int) -> list[dict]:
        """Leg B -- eigene Projektion, ohne Gesamtzahl."""
        antwort = await self._transport.json(
            "GET",
            "/collection/v1/collections/-home-/search",
            # propertyFilter wird von diesem Endpunkt ignoriert; er hat eine
            # feste Projektion. Wer mehr Properties braucht, liest die Knoten
            # ueber ihre ID nach.
            params={"query": text, "maxItems": limit, "skipCount": 0},
        )
        return list(antwort.get("collections") or [])

    def __repr__(self) -> str:
        return f"Collections(metadataset={self.metadataset!r})"
