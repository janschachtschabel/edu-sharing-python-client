"""Die Ablaeufe gegen ein echtes Repositorium.

Die Mock-Tests halten das Format fest. Sie koennen aber nicht zeigen, dass die
Kette gegen eine laufende Instanz auch wirklich durchlaeuft -- und genau das ist
bei einem Ablauf das Versprechen.

**Sicherheitsregeln**, wie in ``test_live_write.py``:

* Geschrieben wird ausschliesslich in einem **eigens angelegten** Ordner.
* Der Ordner liegt im Home-Verzeichnis des angemeldeten Kontos.
* Geloescht wird nur, was diese Tests selbst angelegt haben.

Aufruf::

    uv run pytest -m "live and write" tests/test_live_flows.py
"""

import json
import os
import uuid

import pytest

from edusharing import AsyncRepository
from edusharing.errors import NotFoundError

_ANGEMELDET = os.environ.get("EDU_SHARING_URL") and os.environ.get("EDU_SHARING_USER")

pytestmark = pytest.mark.skipif(
    not _ANGEMELDET, reason="EDU_SHARING_URL/_USER nicht gesetzt"
)


@pytest.fixture
async def repo():
    async with AsyncRepository.from_env(metadataset="mds_oeh") as r:
        yield r


@pytest.fixture
async def ordner(repo):
    """Ein frischer Ordner je Testlauf, der am Ende wieder verschwindet."""
    wer = await repo.whoami()
    assert not wer.is_anonymous, "Schreibtests brauchen ein angemeldetes Konto"
    assert wer.home_folder, "kein Home-Verzeichnis -- hier wird nichts geschrieben"

    neu = await repo.create_node(
        wer.home_folder,
        name=f"pytest-flows-{uuid.uuid4().hex[:8]}",
        type="cm:folder",
        title="Wegwerf-Ordner der Ablauf-Tests",
    )
    try:
        yield neu
    finally:
        await neu.delete(recycle=False)


# --- lesend ---------------------------------------------------------------


@pytest.mark.live
async def test_suche_liefert_echtes_json(repo):
    ergebnis = await repo.flows.search("Physik", limit=3)
    json.dumps(ergebnis)
    assert ergebnis["total"] > 0
    assert 0 < ergebnis["returned"] <= 3
    erster = ergebnis["hits"][0]
    assert erster["id"] and erster["url"]


@pytest.mark.live
async def test_suche_mit_vokabular_filtert_wirklich(repo):
    """Gegenprobe zur Auflösung: mit Fachfilter darf nicht mehr herauskommen
    als ohne."""
    ohne = await repo.flows.search("Wald", limit=1)
    mit = await repo.flows.search("Wald", subject="Biologie", limit=1)
    assert not mit["unresolved"], f"Filter fiel weg: {mit['unresolved']}"
    assert mit["total"] <= ohne["total"]


@pytest.mark.live
async def test_vokabular_kommt_von_der_instanz(repo):
    ergebnis = await repo.flows.vocabulary("subject")
    assert ergebnis["property"] == "ccm:taxonid"
    assert ergebnis["count"] > 10
    assert "Biologie" in ergebnis["values"]


@pytest.mark.live
async def test_describe_beschreibt_einen_echten_treffer(repo):
    """Gemessen am 27.08.2026: **4 von 25** Suchtreffern sind nicht abrufbar --
    der Index enthaelt Knoten, die es nicht mehr gibt. Ein Test, der einfach den
    ersten Treffer nimmt, ist deshalb nicht deterministisch, und ein Ablauf, der
    Suche und Detailabruf verkettet, muss den Fall aushalten."""
    treffer = await repo.flows.search("Physik", limit=10)
    assert treffer["hits"], "keine Treffer -- der Test prueft nichts"

    for hit in treffer["hits"]:
        try:
            ergebnis = await repo.flows.describe(hit["id"])
        except NotFoundError:
            continue
        break
    else:
        pytest.skip("kein abrufbarer Treffer unter den ersten 10")

    assert ergebnis["id"]
    assert ergebnis["properties"], "keine Eigenschaften -- describe liefe leer"
    json.dumps(ergebnis)


# --- Neuordnung -----------------------------------------------------------


@pytest.mark.live
@pytest.mark.parametrize("natuerlich,thema", [
    ("Ich suche ein Arbeitsblatt zur Bruchrechnung", "Bruchrechnung"),
    ("Unterrichtsstunde Französische Revolution", "Französische Revolution"),
])
async def test_rerank_rettet_die_natuerlich_formulierte_anfrage(repo, natuerlich, thema):
    """Der Grund, warum es rerank gibt.

    edu-sharing UND-verknuepft jedes Wort. Woerter, die nur die Form der Bitte
    beschreiben, stehen in fast keinem Datensatz -- ein einziges leert die
    Liste. Gemessen am 27.08.2026: "Bruchrechnung" 1591 Treffer, "Ich suche ein
    Arbeitsblatt zur Bruchrechnung" null.

    Ein Sprachmodell formuliert genau so.
    """
    ohne = await repo.flows.search(natuerlich, limit=3)
    mit = await repo.flows.search(natuerlich, rerank=True, limit=3)
    blank = await repo.flows.search(thema, limit=1)

    assert blank["total"] > 100, "Vorbedingung: zum Thema gibt es reichlich"
    assert ohne["returned"] < mit["returned"], (
        f"rerank brachte keinen Gewinn: {ohne['returned']} -> {mit['returned']}")
    assert mit["total"] > 0, "eine Trefferzahl von 0 neben echten Treffern waere falsch"


@pytest.mark.live
async def test_rerank_meldet_die_gefahrenen_varianten(repo):
    ergebnis = await repo.flows.search(
        "Ich suche ein Video zur Photosynthese", rerank=True, limit=2)
    assert ergebnis["query"]["reranked"] is True
    assert "topic" in ergebnis["query"]["variants"]


@pytest.mark.live
async def test_die_suche_selbst_ist_nicht_reproduzierbar(repo):
    """Kein Fehler der Bibliothek, sondern eine Eigenschaft der Instanz -- und
    eine, die man kennen muss.

    Gemessen am 27.08.2026: dieselbe Anfrage zweimal gestellt lieferte 25
    Treffer, von denen sich **15 unterschieden**. Die Gesamtzahl blieb dabei
    konstant bei 317.

    Folge fuer rerank: es ordnet eine Kandidatenmenge deterministisch (dafuer
    ist der Tie-Break da, siehe test_flows_rerank.py), aber es kann die Suche
    nicht reproduzierbar machen, wenn die Quelle es nicht ist. Gemessen half
    auch ein groesserer Pool nicht nennenswert. Wer Ergebnisse zwischenspeichert
    oder zwei Laeufe vergleicht, muss damit rechnen.

    Der Test ist bewusst schwach formuliert: er verlangt nur, dass die
    Gesamtzahl stabil bleibt. Auf die Trefferreihenfolge zu pruefen hiesse, ihn
    an genau die Volatilitaet zu haengen, die er beschreibt.
    """
    laeufe = [await repo.searcher.search("Photosynthese", limit=25) for _ in range(2)]
    assert laeufe[0].total == laeufe[1].total, "die Gesamtzahl sollte stabil sein"

    ids = [{h.id for h in lauf.hits} for lauf in laeufe]
    gemeinsam = len(ids[0] & ids[1])
    # Keine Behauptung ueber die Hoehe -- nur festhalten, dass es passiert.
    if gemeinsam == len(ids[0]):
        pytest.skip("dieser Lauf war zufaellig stabil; die Instabilitaet ist "
                    "gemessen, aber nicht bei jedem Aufruf sichtbar")


# --- Sammlungen -----------------------------------------------------------


@pytest.mark.live
async def test_sammlungen_finden_und_oeffnen(repo):
    """Die Kette, die ein MCP faehrt: Sammlung suchen, dann hineinsehen."""
    gefunden = await repo.flows.find_collections("Physik", limit=3)
    assert gefunden["hits"], "keine Sammlung gefunden -- der Test prueft nichts"
    assert gefunden["total_is_lower_bound"] is True
    json.dumps(gefunden)

    inhalt = await repo.flows.collection_contents(gefunden["hits"][0]["id"], limit=5)
    assert inhalt["id"] == gefunden["hits"][0]["id"]
    assert inhalt["returned_materials"] == len(inhalt["materials"])
    assert inhalt["returned_materials"] <= 5
    json.dumps(inhalt)


@pytest.mark.live
async def test_wer_nur_material_abfragt_haelt_die_sammlung_fuer_leer(repo):
    """Der Grund, warum collection_contents zwei Wege abfragt.

    Gemessen am 27.08.2026 an einer Sammlung mit zwei Untersammlungen:
    filter=files liefert **null** Knoten. Die Untersammlungen tauchen unter
    filter=folders durchaus auf (als ccm:map) -- eine erste Messung an einer
    Sammlung ohne Untersammlungen hatte das Gegenteil nahegelegt, was ein
    Fehlschluss war.

    Genommen wird trotzdem der Sammlungs-Endpunkt: er ist der dafuer
    vorgesehene und liefert Sammlungs-Metadaten (scope), waehrend der
    Ordnerfilter ein Umweg ist, der zufaellig funktioniert.
    """
    wurzel = await repo.raw.json(
        "GET", "/collection/v1/collections/-home-/-root-/children/collections",
        params={"scope": "TYPE_EDITORIAL", "maxItems": 5})
    eltern = [c for c in (wurzel.get("collections") or [])]
    if not eltern:
        pytest.skip("keine redaktionellen Wurzelsammlungen auf dieser Instanz")

    for kandidat in eltern:
        cid = (kandidat.get("ref") or {}).get("id")
        inhalt = await repo.flows.collection_contents(cid)
        if inhalt["collections"]:
            nur_material = await repo.raw.json(
                "GET", f"/node/v1/nodes/-home-/{cid}/children",
                params={"filter": "files", "maxItems": 20})
            assert not (nur_material.get("nodes") or []), (
                "diese Sammlung enthaelt auch Material -- fuer den Nachweis "
                "wird eine gebraucht, die nur Untersammlungen hat")
            assert inhalt["collections"], (
                "collection_contents muss die Untersammlungen zeigen, die der "
                "Materialfilter verschweigt")
            return
    pytest.skip("keine Sammlung mit Untersammlungen gefunden")


# --- schreibend -----------------------------------------------------------


@pytest.mark.live
@pytest.mark.write
async def test_material_anlegen_mit_vokabular(repo, ordner):
    """Der Kern des schreibenden Ablaufs: "Biologie" statt des URI."""
    ergebnis = await repo.flows.add_material(
        "Ablauf-Test Material",
        parent_id=ordner.id,
        url="https://beispiel.test/ablauf",
        description="Von der Testsuite angelegt",
        keywords=["Test", "Ablauf"],
        subject="Biologie",
    )
    assert not ergebnis["unresolved"], f"nicht aufgeloest: {ergebnis['unresolved']}"

    # Gegenprobe am Server, nicht an der Rueckgabe.
    geschrieben = await repo.flows.describe(ergebnis["id"])
    assert geschrieben["fields"]["subject"] == ["Biologie"]
    assert geschrieben["keywords"] == ["Test", "Ablauf"]


@pytest.mark.live
@pytest.mark.write
async def test_unbekannter_wert_wird_gemeldet_und_material_entsteht(repo, ordner):
    """Gemessen statt vermutet: was macht die Instanz mit einem Wert, den ihr
    Metadatensatz nicht kennt?"""
    ergebnis = await repo.flows.add_material(
        "Ablauf-Test Unbekannt", parent_id=ordner.id, subject="Gibtsnichtwirklich"
    )
    assert ergebnis["unresolved"], "der Wert fiel weg, ohne dass es jemand erfaehrt"
    assert ergebnis["id"], "das Material sollte trotzdem entstehen"


@pytest.mark.live
@pytest.mark.write
async def test_sammlung_anlegen_fuellen_und_wieder_loeschen(repo, ordner):
    material = await repo.flows.add_material("Ablauf-Test Sammelgut", parent_id=ordner.id)

    sammlung = await repo.flows.build_collection(
        f"Ablauf-Test Sammlung {uuid.uuid4().hex[:6]}",
        description="Von der Testsuite angelegt",
        node_ids=[material["id"]],
    )
    try:
        assert sammlung["added"] == [material["id"]], sammlung["failed"]
        assert not sammlung["failed"]
    finally:
        geloescht = await repo.flows.delete(sammlung["id"], recycle=False)
        assert geloescht["id"] == sammlung["id"]


@pytest.mark.live
@pytest.mark.write
async def test_loeschen_benennt_was_verschwand(repo, ordner):
    material = await repo.flows.add_material(
        "Ablauf-Test Wegwerf", parent_id=ordner.id)
    ergebnis = await repo.flows.delete(material["id"], recycle=False)
    assert ergebnis["title"] == "Ablauf-Test Wegwerf"
    assert ergebnis["recycled"] is False


@pytest.mark.live
@pytest.mark.write
async def test_material_aendern_mit_vokabular(repo, ordner):
    """Der Kreis schliesst sich: anlegen, aendern, loeschen."""
    angelegt = await repo.flows.add_material(
        "Ablauf-Test Aenderung", parent_id=ordner.id, subject="Biologie")

    geaendert = await repo.flows.update_material(
        angelegt["id"], title="Ablauf-Test Geaendert", subject="Physik",
        keywords=["geaendert"])
    assert not geaendert["unresolved"], f"nicht aufgeloest: {geaendert['unresolved']}"
    assert geaendert["title"] == "Ablauf-Test Geaendert"

    # Gegenprobe am Server, nicht an der Rueckgabe.
    stand = await repo.flows.describe(angelegt["id"])
    assert stand["fields"]["subject"] == ["Physik"]
    assert stand["keywords"] == ["geaendert"]
