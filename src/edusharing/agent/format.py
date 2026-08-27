"""Treffer fuer den Modellkontext aufbereiten.

Zwei Anforderungen, die sich widersprechen: der Kontext ist begrenzt, und
``id`` und ``url`` duerfen auf keinen Fall wegfallen. Genau die verliert ein
Sprachmodell beim Zusammenfassen als Erstes, und ohne sie kann niemand auf
einen Treffer zurueckkommen -- eine Antwort ohne Fundstelle ist fuer eine
Redaktion wertlos.

Deshalb ist die Reihenfolge beim Kuerzen festgelegt: **gekuerzt wird die
Beschreibung, nie die Rueckverweise.**

Budgetiert wird in **Zeichen**, nicht in Token. Zeichen sind exakt zaehlbar;
eine Token-Schaetzung ohne den Tokenizer des Zielmodells waere geraten und
haette die Genauigkeit nur vorgetaeuscht. Als grobe Umrechnung fuer deutsche
Texte: rund 3 bis 4 Zeichen je Token.

Ausserdem laeuft aller Fremdtext durch ``sanitize`` -- Titel und Beschreibungen
schreiben beliebige Personen.
"""

from __future__ import annotations

from ..results import SearchHit, SearchResult
from .sanitize import sanitize_text

__all__ = ["cap_text", "format_hit", "format_results", "DEFAULT_HIT_CHARS",
           "DEFAULT_RESULT_CHARS"]

#: Zeichenbudget je Treffer, wenn nichts anderes gesagt wird.
DEFAULT_HIT_CHARS = 400

#: Zeichenbudget einer ganzen Ergebnisliste.
DEFAULT_RESULT_CHARS = 4000

_KAPPUNGSZEICHEN = "…"


def cap_text(text: str | None, max_chars: int, *, marker: str = _KAPPUNGSZEICHEN) -> str:
    """Kuerze ``text`` auf hoechstens ``max_chars`` Zeichen.

    Gekuerzt wird an der letzten Wortgrenze davor -- ein mitten im Wort
    abgeschnittener Text liest sich wie ein Tippfehler. Die Kuerzung ist am
    Markierungszeichen erkennbar: ein stillschweigend abgeschnittener Text
    sieht aus wie ein vollstaendiger, und ein Modell zitiert ihn als solchen.

    Raises:
        ValueError: bei einem Budget kleiner als 1.
    """
    if max_chars < 1:
        raise ValueError(f"max_chars muss mindestens 1 sein, war {max_chars}.")
    if not text:
        return ""
    if len(text) <= max_chars:
        return text

    platz = max_chars - len(marker)
    if platz <= 0:
        return marker[:max_chars]

    rumpf = text[:platz]
    letzte_luecke = rumpf.rfind(" ")
    # Nur an der Wortgrenze schneiden, wenn dabei nicht fast alles wegfaellt.
    if letzte_luecke > platz // 2:
        rumpf = rumpf[:letzte_luecke]
    return rumpf.rstrip() + marker


def format_hit(hit: SearchHit, *, max_chars: int = DEFAULT_HIT_CHARS) -> str:
    """Ein Treffer als kompakter Text.

    Titel, Fundstelle und Fachlabels stehen immer; die Beschreibung fuellt den
    Rest des Budgets und faellt notfalls ganz weg.
    """
    titel = sanitize_text(hit.title) or "(ohne Titel)"
    # Der Rueckverweis wird nie gekuerzt -- er ist der Zweck der Ausgabe.
    kopf = f"{titel}\n  id: {hit.id}\n  url: {hit.url}"

    labels = [
        sanitize_text(w)
        for schluessel, werte in (hit.raw.get("properties") or {}).items()
        if schluessel.endswith("_DISPLAYNAME")
        for w in (werte if isinstance(werte, list) else [werte])
    ]
    if labels:
        zeile = f"\n  {', '.join(dict.fromkeys(labels))}"
        if len(kopf) + len(zeile) <= max_chars:
            kopf += zeile

    rest = max_chars - len(kopf) - len("\n  ")
    if hit.description and rest > 20:
        kopf += "\n  " + cap_text(sanitize_text(hit.description), rest)
    return kopf


def format_results(
    result: SearchResult,
    *,
    max_chars: int = DEFAULT_RESULT_CHARS,
    hit_chars: int = DEFAULT_HIT_CHARS,
) -> str:
    """Eine Ergebnisliste als Text fuer den Modellkontext.

    Enthaelt neben den Treffern auch das, was ein Modell sonst nicht wissen
    kann: wie viele Treffer es insgesamt gibt, wie viele davon hier stehen, ob
    ein Filter nicht aufgeloest werden konnte und ob eine Teilabfrage
    ausgefallen ist. All das aendert, wie belastbar eine Antwort ist.
    """
    zeilen: list[str] = []

    if result.total:
        vermerk = " (Untergrenze)" if result.total_is_lower_bound else ""
        zeilen.append(f"{result.total} Treffer{vermerk}.")
    else:
        zeilen.append("Keine Treffer.")

    for offen in result.unresolved:
        zeilen.append(f"! Filter nicht aufgeloest: {offen}")
    for warnung in result.warnings:
        zeilen.append(f"! {sanitize_text(warnung)}")
    if result.suggestions:
        zeilen.append(f"Meinten Sie: {', '.join(sanitize_text(s) for s in result.suggestions)}?")

    kopf = "\n".join(zeilen)
    verbleibend = max_chars - len(kopf)

    gezeigt = 0
    bloecke: list[str] = []
    for hit in result.hits:
        block = format_hit(hit, max_chars=hit_chars)
        # Platz fuer den Hinweis auf Weggelassenes freihalten, sonst faellt
        # ausgerechnet er dem Budget zum Opfer.
        if len(block) + 2 > verbleibend - 40:
            break
        bloecke.append(block)
        verbleibend -= len(block) + 2
        gezeigt += 1

    text = kopf
    if bloecke:
        text += "\n\n" + "\n\n".join(bloecke)
    if gezeigt < len(result.hits):
        weitere = len(result.hits) - gezeigt
        text += f"\n\n({weitere} weitere Treffer hier weggelassen, von {result.total} insgesamt.)"
    return text
