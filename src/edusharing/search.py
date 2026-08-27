"""Suche: Volltext, Filter in Labels, Facetten.

Der Aufruf, den diese Bibliothek moeglich machen soll::

    await repo.search("Photosynthese", fach="Biologie")

Damit das repository-unabhaengig bleibt, passiert dreierlei:

* **Filterwerte werden gegen den Metadatensatz DIESER Instanz aufgeloest**
  (siehe ``vocab``), nicht gegen eine mitgelieferte Tabelle.
* **Was sich nicht aufloesen laesst, wird gemeldet statt verworfen.** Eine
  stillschweigend fallengelassene Einschraenkung liefert Treffer, die niemand
  angefragt hat -- das ist schaedlicher als eine leere Ergebnisliste, weil es
  wie ein Ergebnis aussieht.
* **Die Feld-Aliase sind eine Konvention, keine Annahme.** ``fach`` zeigt auf
  ``ccm:taxonid``, weil das auf den geprueften Instanzen so heisst -- und ist
  ueberschreibbar, weil das anderswo anders sein kann.

Antwortform gemessen (edu-sharing 11.0, Staging, 27.08.2026): ``nodes``,
``pagination {total, from, count}``, ``facets``, ``suggests``, ``ignored``.
Eine **unbekannte** Property landet uebrigens nicht in ``ignored``, sondern
beendet die Anfrage mit ``400 DAOValidationException``.
"""

from __future__ import annotations

from typing import Any

from .errors import ValidationError
from .results import (
    Facet,
    FacetValue,
    SearchHit,
    SearchResult,
    UnresolvedFilter,
)
from .transport import Transport
from .vocab import DEFAULT_METADATASET, DEFAULT_QUERY, Vocabulary

__all__ = ["Search", "STANDARD_FIELD_ALIASES"]

#: Kurznamen fuer gebraeuchliche Filter-Properties.
#:
#: Ermittelt aus der Schnittmenge zweier Metadatensaetze (``mds`` und
#: ``mds_oeh``, Staging 27.08.2026) und **einzeln gegen ngsearch geprueft** --
#: denn ein Vokabular zu fuehren und filterbar zu sein sind zwei verschiedene
#: Dinge (siehe ``_UNBEKANNTES_KRITERIUM``). Nicht aufgenommen wurde deshalb
#: ``ccm:educationaltypicalagerangecluster``: es hat ein Vokabular, wird aber
#: von **keinem** der beiden Metadatensaetze als Kriterium angenommen.
#:
#: Das ist eine **Konvention**, kein Universal: welche Properties eine Instanz
#: fuehrt und welche davon filterbar sind, entscheidet ihr Metadatensatz.
#: ``field_aliases`` setzt eine eigene Zuordnung.
STANDARD_FIELD_ALIASES: dict[str, str] = {
    "fach": "ccm:taxonid",
    "stufe": "ccm:educationalcontext",
    "typ": "ccm:oeh_lrt_aggregated",
    "schwierigkeit": "ccm:educationaldifficulty",
    "lizenz": "license",
}

#: Woran die Antwort auf ein Kriterium zu erkennen ist, das dieser
#: Metadatensatz nicht kennt. Gemessen: ``ccm:taxonid`` ist in ``mds_oeh``
#: filterbar und in ``-default-`` nicht, obwohl es in beiden ein Vokabular hat.
_UNBEKANNTES_KRITERIUM = "could not find parameter"

DEFAULT_LIMIT = 10
DEFAULT_FACET_LIMIT = 20

#: Suchwort-Kriterium von ngsearch.
SEARCHWORD = "ngsearchword"


class Search:
    """Suche gegen einen Metadatensatz.

    Args:
        transport: die Verbindung zum Repositorium.
        vocab: loest Filter-Labels gegen dieselbe Instanz auf.
        metadataset: Metadatensatz, gegen den gesucht wird.
        query: Abfragename, per Konvention ``ngsearch``.
        field_aliases: Kurznamen fuer Properties. ``None`` nimmt
            ``STANDARD_FIELD_ALIASES``.
    """

    def __init__(
        self,
        transport: Transport,
        vocab: Vocabulary,
        *,
        metadataset: str = DEFAULT_METADATASET,
        query: str = DEFAULT_QUERY,
        field_aliases: dict[str, str] | None = None,
    ) -> None:
        self._transport = transport
        self._vocab = vocab
        self.metadataset = metadataset
        self.query = query
        self.field_aliases = (
            STANDARD_FIELD_ALIASES if field_aliases is None else field_aliases
        )

    async def search(
        self,
        text: str | None = None,
        *,
        filters: dict[str, str | list[str]] | None = None,
        facets: list[str] | None = None,
        facet_limit: int = DEFAULT_FACET_LIMIT,
        limit: int = DEFAULT_LIMIT,
        offset: int = 0,
        content_type: str = "FILES",
        **aliases: str | list[str],
    ) -> SearchResult:
        """Suche Material.

        Args:
            text: Volltext-Suchwort. Weglassbar, wenn nur gefiltert wird.
            filters: ``{property: label}`` -- Labels werden aufgeloest, URIs
                unveraendert uebernommen.
            facets: Properties, ueber die serverseitig gezaehlt werden soll.
            facet_limit: wie viele Werte je Facette.
            limit, offset: Seitengroesse und Startpunkt.
            content_type: ``FILES`` (Vorgabe) oder ``FILES_AND_FOLDERS``.
                Sammlungen liefert diese Abfrage **nicht** -- dafuer gibt es
                eine eigene.
            **aliases: Kurznamen aus ``field_aliases``, etwa ``fach="Biologie"``.

        Returns:
            Ein ``SearchResult``. Dessen ``unresolved`` ist zu pruefen: ist es
            nicht leer, wurde weniger eingeschraenkt als angefragt.

        Raises:
            ValidationError: bei einem Kurznamen, den ``field_aliases`` nicht
                kennt -- ein Tippfehler darf nicht als "keine Einschraenkung"
                durchgehen.
        """
        kriterien, unresolved = await self._kriterien(
            self._felder(filters, aliases)
        )
        if text:
            kriterien.insert(0, {"property": SEARCHWORD, "values": [text]})

        body: dict[str, Any] = {
            "criteria": kriterien,
            # Ohne dieses Flag bekommt ein Tippfehler "keine Treffer" und nichts,
            # womit sich ein zweiter Versuch bauen liesse.
            "returnSuggestions": True,
        }
        if facets:
            body["facets"] = [{"property": p} for p in facets]
            body["facetLimit"] = facet_limit
            body["facetMinCount"] = 1

        try:
            antwort = await self._transport.json(
                "POST",
                f"/search/v1/queries/-home-/{self.metadataset}/{self.query}",
                params={
                    "contentType": content_type,
                    "maxItems": limit,
                    "skipCount": offset,
                    "propertyFilter": "-all-",
                },
                json=body,
            )
        except ValidationError as exc:
            raise self._erklaeren(exc) from exc
        return self._ergebnis(antwort, unresolved)

    # --- intern -----------------------------------------------------------

    def _felder(
        self,
        filters: dict[str, str | list[str]] | None,
        aliases: dict[str, str | list[str]],
    ) -> dict[str, str | list[str]]:
        """Fuehre explizit genannte Properties und Kurznamen zusammen.

        Raises:
            ValidationError: bei einem unbekannten Kurznamen. Ihn stumm zu
                ignorieren hiesse, ohne die gemeinte Einschraenkung zu suchen
                und das Ergebnis trotzdem als Treffer auszugeben.
        """
        felder = dict(filters or {})
        for name, wert in aliases.items():
            prop = self.field_aliases.get(name)
            if prop is None:
                bekannt = ", ".join(sorted(self.field_aliases)) or "(keine)"
                raise ValidationError(
                    f"Unbekanntes Suchfeld {name!r}. Bekannt sind: {bekannt}. "
                    "Eine Property laesst sich auch direkt angeben: "
                    "filters={'ccm:...': 'Wert'}."
                )
            felder[prop] = wert
        return felder

    def _erklaeren(self, exc: ValidationError) -> ValidationError:
        """Ergaenze die Servermeldung um das, was sie offen laesst.

        "Could not find parameter X in the query ngsearch" sagt nicht, dass die
        Ursache der gewaehlte Metadatensatz ist -- und genau daran scheitert
        man sonst lange, weil die Property ja nachweislich existiert und sogar
        ein Vokabular fuehrt.

        Andere Validierungsfehler bleiben unveraendert.
        """
        if _UNBEKANNTES_KRITERIUM not in str(exc).lower():
            return exc
        return ValidationError(
            f"{exc}\n"
            f"Der Metadatensatz {self.metadataset!r} nimmt dieses Kriterium in der "
            f"Abfrage {self.query!r} nicht an. Dass die Property existiert und sogar "
            f"ein Vokabular fuehrt, sagt darueber nichts -- Filterbarkeit ist eine "
            f"Eigenschaft des Metadatensatzes. Welche die Instanz fuehrt, zeigt "
            f"GET /mds/v1/metadatasets/-home-; gewaehlt wird ueber "
            f"AsyncRepository(url, metadataset=...).",
            status=exc.status,
            url=exc.url,
            error_class=exc.error_class,
            stacktrace=exc.stacktrace,
        )

    async def _kriterien(
        self, filters: dict[str, str | list[str]]
    ) -> tuple[list[dict[str, Any]], list[UnresolvedFilter]]:
        """Loese Filter-Labels auf. Unaufloesbares wird gemeldet, nicht gesendet."""
        kriterien: list[dict[str, Any]] = []
        unresolved: list[UnresolvedFilter] = []

        for prop, roh in filters.items():
            werte = [roh] if isinstance(roh, str) else list(roh)
            aufgeloest: list[str] = []
            for wert in werte:
                uri = await self._vocab.resolve(prop, wert)
                if uri:
                    aufgeloest.append(uri)
                else:
                    unresolved.append(
                        UnresolvedFilter(
                            field=prop,
                            value=wert,
                            suggestions=[
                                v.label for v in await self._vocab.suggest(prop, wert)
                            ][:5],
                        )
                    )
            if aufgeloest:
                kriterien.append({"property": prop, "values": aufgeloest})

        return kriterien, unresolved

    def _ergebnis(
        self, antwort: dict[str, Any], unresolved: list[UnresolvedFilter]
    ) -> SearchResult:
        basis = self._transport.repository_url
        seite = antwort.get("pagination") or {}
        return SearchResult(
            hits=[
                SearchHit.from_node(n, basis) for n in (antwort.get("nodes") or [])
            ],
            total=int(seite.get("total") or 0),
            facets=[
                Facet(
                    property=f.get("property") or "",
                    values=[
                        FacetValue(value=v.get("value") or "", count=int(v.get("count") or 0))
                        for v in (f.get("values") or [])
                    ],
                    other_count=int(f.get("sumOtherDocCount") or 0),
                )
                for f in (antwort.get("facets") or [])
            ],
            suggestions=[
                s.get("text") for s in (antwort.get("suggests") or []) if s.get("text")
            ],
            unresolved=unresolved,
            ignored=list(antwort.get("ignored") or []),
            raw=antwort,
        )

    def __repr__(self) -> str:
        return f"Search(metadataset={self.metadataset!r}, query={self.query!r})"
