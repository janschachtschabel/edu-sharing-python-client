"""Sammlungssuche ueber zwei Wege.

edu-sharing bietet zwei voneinander unabhaengige Sammlungs-Suchen, und keine
ist Obermenge der anderen. Gemessen (Staging, 27.08.2026, je 25 Treffer):

    Suchwort        A    B    gemeinsam  nur A  nur B
    Optik           5    4    4          1      0
    Deutsch        25   25    0          25     25     <- Schnittmenge NULL
    Grundschule     2    0    0          2      0
    Klimawandel    23   17   17          6      0
    Physik         25   25   20          5      5

Wer nur eines nimmt, verliert systematisch -- und welches versagt, haengt am
Suchwort, nicht an der Sammlung.
"""

import asyncio
import json

import httpx
import pytest

from edusharing.collections import Collections
from edusharing.errors import EduSharingError
from edusharing.transport import Transport

REPO = "https://repository.staging.openeduhub.net/edu-sharing"

# Leg A: POST /search/v1/queries/-home-/{mds}/collections -> nodes, mit pagination
LEG_A = {
    "nodes": [
        {"ref": {"id": "aaa-1"}, "title": "Wellenoptik", "properties": {}},
        {"ref": {"id": "gemeinsam"}, "title": "Optik", "properties": {}},
    ],
    "pagination": {"total": 23, "from": 0, "count": 2},
}

# Leg B: GET /collection/v1/collections/-home-/search -> collections, total NULL
LEG_B = {
    "collections": [
        {"ref": {"id": "gemeinsam"}, "title": "Optik", "properties": {}},
        {"ref": {"id": "bbb-1"}, "title": "Geometrische Optik", "properties": {}},
    ],
    "pagination": None,
}


def _router(a=LEG_A, b=LEG_B, aufrufe=None):
    def handler(request: httpx.Request) -> httpx.Response:
        url = str(request.url)
        if aufrufe is not None:
            aufrufe.append(url)
        if "/collection/v1/collections" in url:
            return httpx.Response(200, json=b) if not isinstance(b, int) \
                else httpx.Response(b, json={"error": "x", "message": "weg"})
        if "/collections" in url:
            return httpx.Response(200, json=a) if not isinstance(a, int) \
                else httpx.Response(a, json={"error": "x", "message": "weg"})
        return httpx.Response(404, json={"error": "x", "message": "nicht gemockt"})
    return handler


def _collections(handler, **kwargs):
    transport = Transport(
        REPO, client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        backoff_base=0.0,
    )
    return Collections(transport, metadataset="mds_oeh", **kwargs)


# --- Projektion -----------------------------------------------------------

async def test_weg_a_fordert_alle_eigenschaften_an():
    """Ohne propertyFilter liefert Weg A Treffer voellig ohne Eigenschaften.

    Gemessen (Staging, 28.08.2026): 0 Eigenschaften auf allen 25 Treffern zu
    "Deutsch". Mit ``-all-`` sind es 33 bis 57 -- und erst dann ist zu sehen,
    dass 2 der 25 Sammlungen eine kuratierte Seite tragen.
    """
    aufrufe = []
    await _collections(_router(aufrufe=aufrufe)).find("Optik")
    weg_a = [u for u in aufrufe if "/search/v1/queries/" in u]
    assert weg_a, "Weg A wurde gar nicht aufgerufen"
    assert "propertyFilter=-all-" in weg_a[0]


async def test_eigenschaften_erreichen_den_treffer():
    a = {
        "nodes": [{
            "ref": {"id": "aaa-1"},
            "title": "Wellenoptik",
            "properties": {"ccm:page_config_ref": ["workspace://SpacesStore/f2-0"]},
        }],
        "pagination": {"total": 1, "from": 0, "count": 1},
    }
    ergebnis = await _collections(_router(a=a, b={"collections": []})).find("Optik")
    treffer = next(h for h in ergebnis.hits if h.id == "aaa-1")
    assert treffer.properties()["ccm:page_config_ref"] == ["workspace://SpacesStore/f2-0"]


# --- Zusammenfuehrung -----------------------------------------------------

async def test_beide_wege_werden_abgefragt():
    aufrufe = []
    await _collections(_router(aufrufe=aufrufe)).find("Optik")
    assert any("/search/v1/queries" in u for u in aufrufe), "Leg A fehlt"
    assert any("/collection/v1/collections/-home-/search" in u for u in aufrufe), "Leg B fehlt"


async def test_treffer_beider_wege_erscheinen():
    e = await _collections(_router()).find("Optik")
    ids = {t.id for t in e.hits}
    assert "aaa-1" in ids, "Treffer aus Leg A fehlt"
    assert "bbb-1" in ids, "Treffer aus Leg B fehlt"


async def test_gemeinsame_treffer_erscheinen_einmal():
    e = await _collections(_router()).find("Optik")
    ids = [t.id for t in e.hits]
    assert ids.count("gemeinsam") == 1
    assert len(ids) == 3


async def test_die_beiden_wege_laufen_gleichzeitig():
    """Nacheinander waere die Sammlungssuche doppelt so langsam wie noetig."""
    laufend = 0
    hoechststand = 0

    async def handler(request):
        nonlocal laufend, hoechststand
        laufend += 1
        hoechststand = max(hoechststand, laufend)
        await asyncio.sleep(0.02)
        laufend -= 1
        url = str(request.url)
        return httpx.Response(
            200, json=LEG_B if "/collection/v1/" in url else LEG_A)

    await _collections(handler).find("Optik")
    assert hoechststand == 2


# --- Ehrlichkeit ueber die Gesamtzahl -------------------------------------

async def test_gesamtzahl_ist_als_untergrenze_gekennzeichnet():
    """Nur Leg A liefert eine Zahl; Leg B gibt pagination null zurueck. Die
    Summe waere wegen der Ueberlappung falsch, die Zahl von A allein zu klein.
    Sie ist also eine Untergrenze -- und das muss ablesbar sein."""
    e = await _collections(_router()).find("Optik")
    assert e.total >= 23
    assert e.total_is_lower_bound is True


# --- Ein Weg faellt aus ---------------------------------------------------

async def test_ausfall_eines_weges_liefert_trotzdem_ergebnisse():
    """Auf einer fremden Instanz kann einer der beiden Endpunkte fehlen. Dann
    ist ein halbes Ergebnis besser als gar keines -- aber es muss als halb
    erkennbar sein."""
    e = await _collections(_router(b=404)).find("Optik")
    assert {t.id for t in e.hits} == {"aaa-1", "gemeinsam"}
    assert e.warnings, "der Ausfall muss vermerkt sein"


async def test_ausfall_wird_benannt():
    e = await _collections(_router(b=404)).find("Optik")
    assert any("collection/v1" in w or "Sammlungssuche" in w for w in e.warnings)


async def test_ausfall_beider_wege_wirft():
    """Kein Ergebnis vorzutaeuschen, wenn gar nichts abgefragt werden konnte."""
    with pytest.raises(EduSharingError):
        await _collections(_router(a=500, b=500)).find("Optik")


# --- Sonstiges ------------------------------------------------------------

async def test_limit_gilt_fuer_beide_wege():
    aufrufe = []
    await _collections(_router(aufrufe=aufrufe)).find("Optik", limit=7)
    assert all("maxItems=7" in u for u in aufrufe)


async def test_treffer_tragen_die_render_url():
    e = await _collections(_router()).find("Optik")
    treffer = next(t for t in e.hits if t.id == "aaa-1")
    assert treffer.url == f"{REPO}/components/render/aaa-1"


# --- Schreiben: Sammlungen und Referenzen ---------------------------------

def _schreib_router(aufrufe: list, konflikt: bool = False):
    def handler(request: httpx.Request) -> httpx.Response:
        aufrufe.append(request)
        pfad, methode = request.url.path, request.method
        if methode == "POST" and pfad.endswith("/children"):
            return httpx.Response(200, json={
                "collection": {"ref": {"id": "neue-sammlung"}, "title": "Neu",
                               "collection": {"scope": "MY"}}})
        if methode == "PUT" and "/references/" in pfad:
            if konflikt:
                return httpx.Response(409, json={
                    "error": "org.edu_sharing.restservices.DAODuplicateNodeNameException",
                    "message": "already in collection"})
            return httpx.Response(200, content=b"")
        if methode == "DELETE" and "/references/" in pfad:
            return httpx.Response(200, content=b"")
        return httpx.Response(404, json={"error": "x", "message": pfad})
    return handler


async def test_sammlung_anlegen_sendet_das_noetige_dto():
    """Ein ueber die Node-API angelegtes ccm:map ist KEINE Sammlung -- gemessen
    fehlt ihm der Aspekt 'collection', und jede Referenz darauf endet mit 400.
    Sammlungen brauchen diesen Endpunkt und ein Body mit title und collection."""
    aufrufe = []
    coll = await _collections(_schreib_router(aufrufe)).create("Neue Sammlung")
    assert coll.id == "neue-sammlung"
    import json as _json
    body = _json.loads(aufrufe[0].content)
    assert body["title"] == "Neue Sammlung"
    assert body["collection"]["scope"] == "MY"


async def test_sammlung_wird_per_vorgabe_privat_angelegt():
    """Eine versehentlich oeffentliche Sammlung sieht die ganze Instanz."""
    aufrufe = []
    await _collections(_schreib_router(aufrufe)).create("X")
    import json as _json
    assert _json.loads(aufrufe[0].content)["collection"]["scope"] == "MY"


async def test_referenz_hinzufuegen():
    aufrufe = []
    await _collections(_schreib_router(aufrufe)).add("coll-1", "node-1")
    put = next(r for r in aufrufe if r.method == "PUT")
    assert put.url.path.endswith("/collections/-home-/coll-1/references/node-1")


async def test_referenz_wird_nicht_zurueckgelesen():
    """Anders als beim Schreiben von Properties ist hier keine Rueckleseprobe
    moeglich: gemessen liefert /children/references direkt nach dem Anlegen
    eine LEERE Liste, obwohl die Referenz existiert -- der zweite Versuch
    antwortet mit 409. Eine Probe wuerde also faelschlich Alarm schlagen."""
    aufrufe = []
    await _collections(_schreib_router(aufrufe)).add("coll-1", "node-1")
    assert not any(r.method == "GET" for r in aufrufe)


async def test_doppelte_referenz_ist_kein_fehler():
    """409 heisst hier "liegt schon drin" -- das ist der gewuenschte Zustand.
    Ein Fehler daraus zu machen wuerde jeden Wiederholungslauf sprengen."""
    aufrufe = []
    ergebnis = await _collections(_schreib_router(aufrufe, konflikt=True)).add("c", "n")
    assert ergebnis is False          # nichts hinzugefuegt, aber kein Fehler


async def test_neue_referenz_meldet_true():
    ergebnis = await _collections(_schreib_router([])).add("c", "n")
    assert ergebnis is True


async def test_referenz_entfernen():
    aufrufe = []
    await _collections(_schreib_router(aufrufe)).remove("coll-1", "node-1")
    delete = next(r for r in aufrufe if r.method == "DELETE")
    assert delete.url.path.endswith("/collections/-home-/coll-1/references/node-1")


async def test_beschreibung_gehoert_in_das_collection_objekt():
    """Gemessen am 27.08.2026 gegen Staging: auf oberster Ebene lehnt die API
    sie ab (UnrecognizedPropertyException, Node kennt kein "description"), und
    als properties["cm:description"] wird sie stillschweigend verworfen. Nur
    collection.description kommt an.

    Der Parameter war vorher ungetestet und schlug bei jedem Aufruf fehl.
    """
    aufrufe: list = []
    await _collections(_schreib_router(aufrufe)).create("Titel", description="Text")
    post = next(r for r in aufrufe if r.method == "POST")
    body = json.loads(post.content)
    assert body["collection"]["description"] == "Text"
    assert "description" not in body, "auf oberster Ebene lehnt die API sie ab"
