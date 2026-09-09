"""Die lesenden Ablaeufe -- was sie zurueckgeben, ist ihr eigentlicher Vertrag.

Ein Ablauf unterscheidet sich von der API-nahen Ebene in genau zwei Punkten:
er fasst mehrere Aufrufe zu einem zusammen, und er liefert etwas, das ohne
weitere Umwandlung durch json.dumps geht. Beides wird hier geprueft.

Antwortformen uebernommen aus test_search.py, gemessen gegen edu-sharing 11.0
(Staging, 27.08.2026).
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository

REPO = "https://repo.test/edu-sharing"

FAECHER = {"values": [
    {"key": "http://w3id.org/openeduhub/vocabs/discipline/080", "displayString": "Biologie"},
    {"key": "http://w3id.org/openeduhub/vocabs/discipline/460", "displayString": "Physik"},
]}

TREFFER = {
    "nodes": [{
        "ref": {"id": "1f71f84a-a67d-4b93-b55f-3ba4f39571d8", "repo": "local"},
        "title": "Feuerspuren im Satellitenbild",
        "mimetype": "text/html",
        "mediatype": "link",
        "properties": {
            "cclom:general_description": ["Ein Text ueber Oekosysteme"],
            "ccm:taxonid": ["http://w3id.org/openeduhub/vocabs/discipline/080"],
            "ccm:taxonid_DISPLAYNAME": ["Biologie"],
            "ccm:educationalcontext_DISPLAYNAME": ["Sekundarstufe I", "Sekundarstufe II"],
            "ccm:wwwurl": ["https://beispiel.test/material"],
        },
    }],
    "pagination": {"total": 211, "from": 0, "count": 1},
    "facets": [{
        "property": "ccm:taxonid",
        "values": [{"value": "http://w3id.org/openeduhub/vocabs/discipline/080", "count": 57}],
        "sumOtherDocCount": 30,
    }],
    "suggests": [],
    "ignored": [],
}


def _router(request: httpx.Request) -> httpx.Response:
    if "/values" in str(request.url):
        return httpx.Response(200, json=FAECHER)
    return httpx.Response(200, json=TREFFER)


def _repo(handler=_router, **kwargs) -> AsyncRepository:
    return AsyncRepository(
        REPO, metadataset="mds_oeh", backoff_base=0.0,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)), **kwargs)


# --- search ---------------------------------------------------------------

async def test_suche_liefert_serialisierbares_json():
    """Der Kern des Versprechens: das Ergebnis geht ohne Umweg durch
    json.dumps. Ein Ablauf, dessen Ausgabe erst konvertiert werden muss, hat
    seinen Zweck verfehlt."""
    async with _repo() as repo:
        ergebnis = await repo.flows.search("Feuer", subject="Biologie")
    text = json.dumps(ergebnis, ensure_ascii=False)
    assert "Feuerspuren" in text


async def test_suche_meldet_was_gesucht_wurde():
    """Ohne das kann ein Sprachmodell seine eigene Anfrage nicht referenzieren
    -- und behauptet im Zweifel, es habe etwas anderes gesucht."""
    async with _repo() as repo:
        ergebnis = await repo.flows.search("Feuer", subject="Biologie", limit=5)
    assert ergebnis["query"]["text"] == "Feuer"
    assert ergebnis["query"]["filters"] == {"subject": "Biologie"}
    assert ergebnis["query"]["metadataset"] == "mds_oeh"


async def test_treffer_tragen_id_und_url():
    async with _repo() as repo:
        ergebnis = await repo.flows.search("Feuer")
    treffer = ergebnis["hits"][0]
    assert treffer["id"] == "1f71f84a-a67d-4b93-b55f-3ba4f39571d8"
    assert treffer["url"].endswith("/components/render/1f71f84a-a67d-4b93-b55f-3ba4f39571d8")
    assert treffer["title"] == "Feuerspuren im Satellitenbild"


async def test_treffer_tragen_lesbare_werte_statt_uris():
    """Der Punkt der ganzen Uebung: ein Sprachmodell soll "Biologie" lesen,
    nicht "http://w3id.org/openeduhub/vocabs/discipline/080".

    Die Schluessel sind die konfigurierten Kurznamen, nicht die
    edu-sharing-Eigenschaften -- sonst waere die Ausgabe an ein Profil
    gebunden."""
    async with _repo() as repo:
        ergebnis = await repo.flows.search("Feuer")
    felder = ergebnis["hits"][0]["fields"]
    assert felder["subject"] == ["Biologie"]
    assert felder["level"] == ["Sekundarstufe I", "Sekundarstufe II"]
    assert not any(str(w).startswith("http://w3id") for w in felder.values())


async def test_eigene_aliase_bestimmen_die_ausgabefelder():
    """Gegenprobe zur Generizitaet: wer andere Kurznamen konfiguriert, bekommt
    andere Ausgabefelder. Nichts hier ist auf WLO festgelegt."""
    async with _repo(field_aliases={"fach": "ccm:taxonid"}) as repo:
        ergebnis = await repo.flows.search("Feuer")
    felder = ergebnis["hits"][0]["fields"]
    assert felder == {"fach": ["Biologie"]}


async def test_zaehlungen_sind_vollstaendig():
    async with _repo() as repo:
        ergebnis = await repo.flows.search("Feuer")
    assert ergebnis["total"] == 211
    assert ergebnis["returned"] == 1
    assert ergebnis["total_is_lower_bound"] is False


async def test_unaufloesbarer_filter_wird_gemeldet_statt_verschwiegen():
    """Ein stillschweigend fallengelassener Filter liefert ein breiteres
    Ergebnis, das vollstaendig aussieht. Das ist die gefaehrlichste Form von
    falsch."""
    async with _repo() as repo:
        ergebnis = await repo.flows.search("Feuer", subject="Gibtsnicht")
    assert ergebnis["unresolved"], "der Filter fiel weg, ohne dass es jemand erfaehrt"
    erster = ergebnis["unresolved"][0]
    assert erster["field"] == "subject"
    assert erster["value"] == "Gibtsnicht"
    assert "Biologie" in erster["suggestions"]


async def test_facetten_tragen_lesbare_namen():
    async with _repo() as repo:
        ergebnis = await repo.flows.search("Feuer", facets=["subject"])
    assert "subject" in ergebnis["facets"]
    assert ergebnis["facets"]["subject"][0]["count"] == 57


# --- vocabulary -----------------------------------------------------------

async def test_vokabular_listet_die_erlaubten_werte():
    """Damit ein Sprachmodell nicht raten muss, welche Werte ein Feld annimmt."""
    async with _repo() as repo:
        ergebnis = await repo.flows.vocabulary("subject")
    assert ergebnis["field"] == "subject"
    assert ergebnis["property"] == "ccm:taxonid"
    assert "Biologie" in ergebnis["values"]
    json.dumps(ergebnis)


async def test_vokabular_akzeptiert_auch_die_eigenschaft_direkt():
    async with _repo() as repo:
        ergebnis = await repo.flows.vocabulary("ccm:taxonid")
    assert ergebnis["property"] == "ccm:taxonid"


async def test_vokabular_eines_unbekannten_feldes_meldet_die_bekannten():
    """Sackgasse mit Wegweiser statt Sackgasse."""
    async with _repo() as repo:
        with pytest.raises(Exception) as fehler:
            await repo.flows.vocabulary("gibtsnicht")
    assert "subject" in str(fehler.value)


# --- describe -------------------------------------------------------------

KNOTEN = {"node": {
    "ref": {"id": "abc-123"},
    "name": "material.pdf",
    "title": "Feuerspuren",
    "type": "ccm:io",
    "access": ["Read", "Write"],
    "mimetype": "application/pdf",
    "content": {"hash": "-42"},
    "properties": {
        "cclom:general_description": ["Beschreibung"],
        "cclom:general_keyword": ["Feuer", "Satellit"],
        "ccm:taxonid_DISPLAYNAME": ["Biologie"],
        "ccm:wwwurl": ["https://beispiel.test/m"],
    },
}}


def _knoten_router(request: httpx.Request) -> httpx.Response:
    if "/values" in str(request.url):
        return httpx.Response(200, json=FAECHER)
    return httpx.Response(200, json=KNOTEN)


async def test_describe_fasst_einen_knoten_zusammen():
    """Auf API-Ebene braucht das mehrere Zugriffe: Knoten laden, Eigenschaften
    lesen, Schlagworte holen."""
    async with _repo(_knoten_router) as repo:
        ergebnis = await repo.flows.describe("abc-123")
    assert ergebnis["id"] == "abc-123"
    assert ergebnis["name"] == "material.pdf"
    assert ergebnis["type"] == "ccm:io"
    assert ergebnis["keywords"] == ["Feuer", "Satellit"]
    assert ergebnis["fields"]["subject"] == ["Biologie"]
    assert ergebnis["has_content"] is True
    assert ergebnis["access"] == ["Read", "Write"]
    json.dumps(ergebnis)


async def test_describe_reicht_die_rohen_eigenschaften_durch():
    """Fuer alles, was die Kurznamen nicht abdecken -- sonst waere der Ablauf
    eine Sackgasse, sobald ein Feld fehlt."""
    async with _repo(_knoten_router) as repo:
        ergebnis = await repo.flows.describe("abc-123")
    assert ergebnis["properties"]["ccm:wwwurl"] == ["https://beispiel.test/m"]


# --- R06 (Zweitpruefung 09.09.2026): die Facetten-Restanzahl --------------
#
# ``Facet`` traegt ``other_count`` und ``truncated`` -- die Suchschicht liest
# beides aus ``sumOtherDocCount``. ``_facet_values`` gab nur die Werteliste
# heraus. Gemessen am 09.09.2026: eine Facette mit einem Wert (70) und
# ``sumOtherDocCount=30`` kam im Flow als ``[{"value": ..., "count": 70}]`` an,
# ohne Restanzahl, ohne Abschneidung und mit leeren ``warnings``.
#
# Filterleisten, Statistiken und Agenten halten eine so gekuerzte Liste fuer
# vollstaendig. Die Bibliothek hatte die Information schon -- sie verlor sie
# beim Serialisieren.


def _mit_facette(rest: int) -> dict:
    antwort = json.loads(json.dumps(TREFFER))
    antwort["facets"] = [{
        "property": "ccm:taxonid",
        "values": [{"value": "Biologie", "count": 70}],
        "sumOtherDocCount": rest,
    }]
    return antwort


async def test_die_restanzahl_ueberlebt_die_serialisierung():
    def handler(request: httpx.Request) -> httpx.Response:
        if "/values" in str(request.url):
            return httpx.Response(200, json=FAECHER)
        return httpx.Response(200, json=_mit_facette(30))

    async with _repo(handler) as repo:
        antwort = await repo.flows.search("Zelle", facets=["subject"])

    assert antwort["facets"]["subject"] == [{"value": "Biologie", "count": 70}]
    assert antwort["facet_meta"]["subject"] == {"other_count": 30, "truncated": True}


async def test_eine_vollstaendige_facette_sagt_es_ausdruecklich():
    """Die Gegenprobe. ``other_count=0`` muss darstellbar bleiben -- sonst
    heisst "kein Schluessel" einmal vollstaendig und einmal nicht gefragt."""
    def handler(request: httpx.Request) -> httpx.Response:
        if "/values" in str(request.url):
            return httpx.Response(200, json=FAECHER)
        return httpx.Response(200, json=_mit_facette(0))

    async with _repo(handler) as repo:
        antwort = await repo.flows.search("Zelle", facets=["subject"])

    assert antwort["facet_meta"]["subject"] == {"other_count": 0, "truncated": False}


async def test_die_beiden_karten_tragen_dieselben_schluessel():
    """Die Invariante, nicht die Zahl: was unter ``facets`` steht, hat unter
    ``facet_meta`` einen Eintrag und umgekehrt.

    Der erste Anlauf dieses Tests behauptete, ohne gefragte Facetten bleibe
    die Karte leer. Falsch: die Antwort der Instanz traegt eine Facette, und
    ``facets`` fuehrt sie schon immer -- gefragt oder nicht.
    """
    async with _repo() as repo:
        antwort = await repo.flows.search("Zelle")
    assert set(antwort["facet_meta"]) == set(antwort["facets"])


async def test_ohne_facetten_in_der_antwort_bleiben_beide_leer():
    def handler(request: httpx.Request) -> httpx.Response:
        if "/values" in str(request.url):
            return httpx.Response(200, json=FAECHER)
        ohne = json.loads(json.dumps(TREFFER))
        ohne["facets"] = []
        return httpx.Response(200, json=ohne)

    async with _repo(handler) as repo:
        antwort = await repo.flows.search("Zelle")
    assert antwort["facets"] == {} and antwort["facet_meta"] == {}


async def test_die_suche_ueber_alles_traegt_es_mit():
    """Die Kette endet nicht bei ``search`` -- ``search_all`` reicht dieselbe
    Antwort weiter."""
    def handler(request: httpx.Request) -> httpx.Response:
        if "/values" in str(request.url):
            return httpx.Response(200, json=FAECHER)
        if "/collection/v1/collections/-home-/search" in str(request.url):
            return httpx.Response(200, json={"collections": []})
        return httpx.Response(200, json=_mit_facette(30))

    async with _repo(handler) as repo:
        antwort = await repo.flows.search_all("Zelle", facets=["subject"])

    assert antwort["materials"]["facet_meta"]["subject"]["other_count"] == 30
