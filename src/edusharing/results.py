"""Wertobjekte fuer Suchergebnisse.

Eigenes Modul, weil sie zwei Aufrufer haben: die Materialsuche und die
Sammlungssuche. Laegen sie in einem der beiden, muesste der andere dorthin
importieren -- und die Abhaengigkeit zeigte in die falsche Richtung.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

__all__ = ["SearchHit", "FacetValue", "Facet", "UnresolvedFilter", "SearchResult"]


@dataclass(frozen=True)
class SearchHit:
    """Ein Treffer.

    ``id`` und ``url`` sind die beiden Angaben, ohne die niemand auf den
    Treffer zurueckkommt -- und genau die, die ein Sprachmodell beim
    Zusammenfassen als Erstes wegparaphrasiert.
    """

    id: str
    title: str
    url: str
    description: str | None = None
    source_url: str | None = None
    mimetype: str | None = None
    mediatype: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    def properties(self) -> dict[str, Any]:
        return self.raw.get("properties") or {}

    def labels(self, prop: str) -> list[str]:
        """Die lesbaren Werte zu einer Vokabular-Property.

        edu-sharing liefert zu jedem Vokabularfeld ein ``<prop>_DISPLAYNAME``
        mit; das erspart eine zweite Anfrage, nur um eine URI lesbar zu machen.
        """
        return list(self.properties().get(f"{prop}_DISPLAYNAME") or [])

    @classmethod
    def from_node(cls, node: dict[str, Any], repository_url: str) -> SearchHit:
        node_id = (node.get("ref") or {}).get("id") or ""
        props = node.get("properties") or {}
        return cls(
            id=node_id,
            title=node.get("title") or _erster(props.get("cm:name")) or "",
            url=f"{repository_url}/components/render/{node_id}",
            description=_erster(props.get("cclom:general_description"))
            or _erster(props.get("cm:description")),
            source_url=_erster(props.get("ccm:wwwurl")),
            mimetype=node.get("mimetype"),
            mediatype=node.get("mediatype"),
            raw=node,
        )


@dataclass(frozen=True, slots=True)
class FacetValue:
    """Ein Facettenwert mit seiner Trefferzahl."""

    value: str
    count: int


@dataclass(frozen=True)
class Facet:
    """Serverseitige Aggregation ueber die ganze Ergebnismenge."""

    property: str
    values: list[FacetValue] = field(default_factory=list)
    #: Treffer, die in keinen der zurueckgegebenen Werte fielen.
    other_count: int = 0

    @property
    def truncated(self) -> bool:
        """Ob die Werteliste gekuerzt ist.

        Wichtig fuer alles, was Facettenzahlen summiert: eine gekuerzte Liste
        sieht autoritativ aus und ist zu klein.
        """
        return self.other_count > 0


@dataclass(frozen=True)
class UnresolvedFilter:
    """Ein Filterwert, den der Metadatensatz dieser Instanz nicht kennt."""

    field: str
    value: str
    suggestions: list[str] = field(default_factory=list)

    def __str__(self) -> str:
        text = f"{self.field}={self.value!r} ist unbekannt"
        if self.suggestions:
            text += f" -- gemeint: {', '.join(self.suggestions)}?"
        return text


@dataclass(frozen=True)
class SearchResult:
    """Das Ergebnis einer Suche."""

    hits: list[SearchHit] = field(default_factory=list)
    total: int = 0
    facets: list[Facet] = field(default_factory=list)
    #: "Meinten Sie ...?" aus dem Index -- gefuellt, wenn nichts gefunden wurde.
    suggestions: list[str] = field(default_factory=list)
    #: Filter, die nicht aufgeloest werden konnten und daher NICHT gesendet
    #: wurden. Nicht leer heisst: das Ergebnis ist breiter als angefragt.
    unresolved: list[UnresolvedFilter] = field(default_factory=list)
    #: Kriterien, die das Repositorium selbst verworfen hat.
    ignored: list[str] = field(default_factory=list)
    #: Was am Ergebnis unvollstaendig ist -- etwa eine Teilabfrage, die
    #: fehlgeschlagen ist. Nicht leer heisst: hier fehlt moeglicherweise etwas.
    warnings: list[str] = field(default_factory=list)
    #: Ob ``total`` nur eine Untergrenze ist. Trifft zu, wenn das Ergebnis aus
    #: mehreren Abfragen stammt und nicht alle eine Gesamtzahl liefern.
    total_is_lower_bound: bool = False
    raw: dict[str, Any] = field(default_factory=dict)

    def __len__(self) -> int:
        return len(self.hits)

    def __iter__(self):
        return iter(self.hits)


def _erster(wert: Any) -> str | None:
    """edu-sharing liefert Property-Werte immer als Liste, auch einzelne."""
    if isinstance(wert, list):
        return str(wert[0]) if wert else None
    return str(wert) if wert else None
