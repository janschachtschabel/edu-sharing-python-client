"""Dasselbe Material, mehrfach im Trefferbild.

edu-sharing legt bei wiederholten Importen derselben Webseite mehrere Knoten an.
Sie tragen dieselbe Quelladresse und unterscheiden sich nur im technischen Namen
(edu-sharing haengt bei Namenskollisionen " - 2", " - 3" an).

Gemessen gegen Staging am 27.08.2026: bei 50 Treffern zu "Photosynthese" und zu
"Bruchrechnung" jeweils **ein** Paar mit identischer Quelladresse. Der
wlo-mcp-sc mass am 09.08.2026 acht Knoten mit derselben Wikipedia-Adresse.

Die Rate ist niedrig, der Schaden pro Vorfall aber real: wer die Liste liest --
ein Mensch wie ein Sprachmodell -- haelt zwei Eintraege fuer zwei Materialien.

Deshalb wird zusammengefasst, aber nichts verschwiegen: der behaltene Treffer
traegt die IDs der zusammengefassten, und die Antwort nennt ihre Zahl.
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.flows.dedupe import deduplicate
from edusharing.results import SearchHit

REPO = "https://repo.test/edu-sharing"


def _hit(node_id: str, titel: str, quelle: str | None) -> SearchHit:
    return SearchHit(id=node_id, title=titel, url=f"{REPO}/components/render/{node_id}",
                     source_url=quelle, raw={"properties": {}})


# --- Die Regel ------------------------------------------------------------

def test_gleiche_quelladresse_wird_zusammengefasst():
    behalten, doppelt = deduplicate([
        _hit("a", "Optik", "https://de.wikipedia.org/wiki/Optik"),
        _hit("b", "Optik - 2", "https://de.wikipedia.org/wiki/Optik"),
    ])
    assert [h.id for h in behalten] == ["a"]
    assert doppelt == {"a": ["b"]}


def test_der_erste_treffer_gewinnt():
    """Die Reihenfolge ist zu diesem Zeitpunkt schon die endgueltige -- bei
    rerank die bestbewertete. Wer den spaeteren behielte, wuerfe die bessere
    Bewertung weg."""
    behalten, _ = deduplicate([
        _hit("besser", "Optik", "https://x/optik"),
        _hit("schlechter", "Optik - 2", "https://x/optik"),
    ])
    assert behalten[0].id == "besser"


def test_verschiedene_quellen_bleiben_getrennt():
    behalten, doppelt = deduplicate([
        _hit("a", "Optik", "https://x/optik"),
        _hit("b", "Akustik", "https://x/akustik"),
    ])
    assert len(behalten) == 2
    assert doppelt == {}


def test_treffer_ohne_quelladresse_fallen_nie_zusammen():
    """Sonst wuerden alle Materialien ohne Quelladresse zu einem einzigen --
    gemessen hat rund jeder fuenfzigste Treffer keine."""
    behalten, doppelt = deduplicate([
        _hit("a", "Eines", None),
        _hit("b", "Anderes", None),
        _hit("c", "Drittes", ""),
    ])
    assert len(behalten) == 3
    assert doppelt == {}


def test_gleicher_titel_allein_genuegt_nicht():
    """Zwei Materialien duerfen denselben Titel tragen und trotzdem
    verschieden sein -- gemessen kommt das vor. Nur die Quelladresse zaehlt."""
    behalten, _ = deduplicate([
        _hit("a", "Photosynthese", "https://x/eins"),
        _hit("b", "Photosynthese", "https://x/zwei"),
    ])
    assert len(behalten) == 2


def test_drei_gleiche_werden_zu_einem():
    behalten, doppelt = deduplicate([
        _hit("a", "Optik", "https://x/o"),
        _hit("b", "Optik - 2", "https://x/o"),
        _hit("c", "Optik - 3", "https://x/o"),
    ])
    assert [h.id for h in behalten] == ["a"]
    assert doppelt == {"a": ["b", "c"]}


def test_leere_liste():
    assert deduplicate([]) == ([], {})


def test_treffer_ohne_id_wird_durchgereicht():
    """Ohne ID ist ein Treffer nicht referenzierbar, aber auch kein Duplikat
    von etwas -- weglassen waere ein stiller Verlust."""
    behalten, _ = deduplicate([_hit("", "Ohne ID", "https://x/o")])
    assert len(behalten) == 1


def test_treffer_ohne_id_wird_auch_als_zweiter_behalten():
    """Zusammenfassen hiesse, ihn in duplicate_ids aufzufuehren -- mit einer
    leeren ID, unter der ihn niemand wiederfindet. Behalten ist ehrlicher."""
    behalten, doppelt = deduplicate([
        _hit("a", "Optik", "https://x/o"),
        _hit("", "Optik - 2", "https://x/o"),
    ])
    assert len(behalten) == 2
    assert doppelt == {}


# --- Im Ablauf ------------------------------------------------------------

FAECHER = {"values": [{"key": "http://x/080", "displayString": "Biologie"}]}


def _knoten(node_id: str, titel: str, quelle: str) -> dict:
    return {"ref": {"id": node_id}, "title": titel,
            "properties": {"cclom:title": [titel], "ccm:wwwurl": [quelle]}}


def _repo(knoten: list[dict]) -> AsyncRepository:
    def handler(request: httpx.Request) -> httpx.Response:
        if "/values" in request.url.path:
            return httpx.Response(200, json=FAECHER)
        return httpx.Response(200, json={
            "nodes": knoten,
            "pagination": {"total": 99, "from": 0, "count": len(knoten)}})

    return AsyncRepository(
        REPO, metadataset="mds_oeh", backoff_base=0.0,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)))


DOPPELT = [
    _knoten("a", "Optik", "https://de.wikipedia.org/wiki/Optik"),
    _knoten("b", "Optik - 2", "https://de.wikipedia.org/wiki/Optik"),
    _knoten("c", "Akustik", "https://de.wikipedia.org/wiki/Akustik"),
]


async def test_suche_fasst_doppelte_zusammen():
    async with _repo(DOPPELT) as repo:
        ergebnis = await repo.flows.search("Optik")
    assert [h["id"] for h in ergebnis["hits"]] == ["a", "c"]
    assert ergebnis["returned"] == 2


async def test_der_behaltene_treffer_nennt_die_zusammengefassten():
    """Nichts still weglassen: wer beide Datensaetze braucht -- zum Aufraeumen
    etwa -- kommt an den zweiten heran."""
    async with _repo(DOPPELT) as repo:
        ergebnis = await repo.flows.search("Optik")
    erster = ergebnis["hits"][0]
    assert erster["duplicate_ids"] == ["b"]
    assert ergebnis["hits"][1]["duplicate_ids"] == []
    assert ergebnis["duplicates_removed"] == 1
    json.dumps(ergebnis)


async def test_abschaltbar():
    """Wer die Rohsicht braucht, bekommt sie."""
    async with _repo(DOPPELT) as repo:
        ergebnis = await repo.flows.search("Optik", deduplicate=False)
    assert [h["id"] for h in ergebnis["hits"]] == ["a", "b", "c"]
    assert ergebnis["duplicates_removed"] == 0


async def test_das_limit_zaehlt_vor_dem_zusammenfassen():
    """Sonst muesste die Suche nachladen, um das Limit zu fuellen -- eine
    zweite Anfrage fuer einen Randfall. Was zurueckkommt, kann also weniger
    sein als limit, und returned sagt es."""
    async with _repo(DOPPELT) as repo:
        ergebnis = await repo.flows.search("Optik", limit=3)
    assert ergebnis["returned"] == 2
    assert ergebnis["duplicates_removed"] == 1


@pytest.mark.parametrize("feld", ["duplicate_ids"])
async def test_das_feld_steht_auch_ohne_duplikate(feld):
    """Ein fehlender Schluessel ist schwerer zu uebersehen als ein leerer."""
    async with _repo([_knoten("a", "Optik", "https://x/o")]) as repo:
        ergebnis = await repo.flows.search("Optik")
    assert feld in ergebnis["hits"][0]
