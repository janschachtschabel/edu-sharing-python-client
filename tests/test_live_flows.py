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
