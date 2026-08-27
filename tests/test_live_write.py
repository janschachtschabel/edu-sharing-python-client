"""Schreibtests gegen ein echtes Repositorium.

Laufen nur mit ``pytest -m write`` und gesetzten Zugangsdaten::

    uv run pytest -m write

**Sicherheitsregeln dieser Datei**, weil ein Schreibtest im falschen Ordner
fremde Bestaende beschaedigt:

* Es wird ausschliesslich in einem **eigens angelegten** Ordner gearbeitet.
* Der Ordner liegt im Home-Verzeichnis des angemeldeten Kontos; die Fixture
  prueft das, bevor sie irgendetwas schreibt.
* Geloescht wird nur, was diese Tests selbst angelegt haben.
* Kein Test fasst einen Knoten an, dessen ID er nicht selbst erzeugt hat.
"""

import os
import uuid

import pytest

from edusharing import AsyncRepository
from edusharing.errors import SilentDropError

pytestmark = [
    pytest.mark.write,
    pytest.mark.skipif(
        not (os.environ.get("EDU_SHARING_URL") and os.environ.get("EDU_SHARING_USER")),
        reason="EDU_SHARING_URL/_USER nicht gesetzt",
    ),
]

# Eine Property, die der Metadatensatz mds_oeh NICHT kennt -- geprueft gegen
# die Widget-Liste. Ueber sie laesst sich der stille Verlust ausloesen.
NICHT_IM_MDS = "ccm:oeh_collection_compendium_text"


@pytest.fixture
async def repo():
    async with AsyncRepository.from_env(metadataset="mds_oeh") as r:
        wer = await r.whoami()
        assert not wer.is_anonymous, "Schreibtests brauchen ein angemeldetes Konto"
        yield r


@pytest.fixture
async def ordner(repo):
    """Ein frischer Ordner je Testlauf, der am Ende wieder verschwindet."""
    wer = await repo.whoami()
    home = ((wer.raw.get("person") or {}).get("homeFolder") or {}).get("id")
    assert home, "kein Home-Verzeichnis -- ohne das wird hier nichts geschrieben"

    neu = await repo.create_node(
        home,
        name=f"pytest-edusharing-{uuid.uuid4().hex[:8]}",
        type="cm:folder",
        titel="Wegwerf-Ordner der Testsuite",
    )
    assert neu.id, "Ordner nicht angelegt"
    try:
        yield neu
    finally:
        await neu.delete()


@pytest.fixture
async def knoten(repo, ordner):
    """Ein Wegwerf-Knoten im Wegwerf-Ordner."""
    return await repo.create_node(
        ordner.id, name="material.txt", titel="Ausgangstitel",
    )


# --- Anlegen ---------------------------------------------------------------

async def test_knoten_wird_angelegt(knoten):
    assert knoten.id
    assert knoten.url.endswith(knoten.id)


async def test_titel_landet_in_beiden_namensraeumen(knoten):
    """Die Oberflaeche rendert cm:title und cclom:title an verschiedenen
    Stellen -- nur eines zu setzen zeigt der Nutzerin etwas anderes an, als
    die Anwendung geschrieben hat."""
    assert knoten.get("cm:title") == "Ausgangstitel"
    assert knoten.get("cclom:title") == "Ausgangstitel"


# --- Der Kernfall: stiller Verlust ----------------------------------------

async def test_property_im_metadatensatz_wird_gespeichert(knoten):
    aktualisiert = await knoten.update(titel="Geaendert")
    assert aktualisiert.get("cclom:title") == "Geaendert"


async def test_property_ausserhalb_des_metadatensatzes_wird_still_verworfen(knoten):
    """DER Grund fuer die Rueckleseprobe.

    edu-sharing antwortet auf diesen PUT mit **HTTP 200** und speichert
    nichts. Ohne die Probe meldete die Bibliothek hier Erfolg.
    """
    with pytest.raises(SilentDropError) as info:
        await knoten.update(properties={NICHT_IM_MDS: "Dieser Text geht verloren"})
    assert NICHT_IM_MDS in info.value.dropped


async def test_ohne_pruefung_bleibt_der_verlust_unbemerkt(knoten):
    """Die Gegenprobe: mit verify=False meldet derselbe Aufruf Erfolg -- und
    der Wert ist trotzdem weg. Das belegt, dass die Probe die Absicherung ist
    und nicht der Server."""
    await knoten.update(properties={NICHT_IM_MDS: "verloren"}, verify=False)
    frisch = await knoten._nodes.get(knoten.id)
    assert frisch.get(NICHT_IM_MDS) is None


async def test_direktweg_speichert_dieselbe_property(knoten):
    """set_property umgeht die Filterung des Metadatensatzes."""
    aktualisiert = await knoten.set_property(NICHT_IM_MDS, "Auf dem Direktweg")
    assert aktualisiert.get(NICHT_IM_MDS) == "Auf dem Direktweg"


async def test_direktweg_kann_loeschen(knoten):
    gesetzt = await knoten.set_property(NICHT_IM_MDS, "erst da")
    assert gesetzt.get(NICHT_IM_MDS) == "erst da"
    geleert = await gesetzt.set_property(NICHT_IM_MDS, None)
    assert geleert.get(NICHT_IM_MDS) is None


# --- Rechte und Loeschen ---------------------------------------------------

async def test_eigener_knoten_ist_beschreibbar(knoten):
    assert knoten.can_write is True


async def test_loeschen_entfernt_den_knoten(repo, ordner):
    eigener = await repo.create_node(ordner.id, name="wird-geloescht.txt")
    node_id = eigener.id
    await eigener.delete()
    from edusharing.errors import NotFoundError
    with pytest.raises(NotFoundError):
        await repo.node(node_id)


# --- Schlagworte: die geteilte Liste --------------------------------------

async def test_schlagworte_ergaenzen_ohne_fremde_zu_verlieren(repo, ordner):
    """Der Fall, der eine eigene Methode rechtfertigt: cclom:general_keyword
    pflegen mehrere Beteiligte gemeinsam. Hier simuliert ein direkt gesetzter
    Bestand die Arbeit anderer -- er muss den eigenen Zusatz ueberleben."""
    node = await repo.create_node(ordner.id, name="schlagworte.txt")
    fremd = await node.update(
        properties={"cclom:general_keyword": ["Fremdes Schlagwort", "Noch eines"]})
    assert set(fremd.keywords) == {"Fremdes Schlagwort", "Noch eines"}

    ergaenzt = await fremd.add_keywords("Weimar (Ort)")
    assert set(ergaenzt.keywords) == {"Fremdes Schlagwort", "Noch eines", "Weimar (Ort)"}

    bereinigt = await ergaenzt.remove_keywords("Weimar (Ort)")
    assert set(bereinigt.keywords) == {"Fremdes Schlagwort", "Noch eines"}


async def test_doppeltes_schlagwort_wird_nicht_zweimal_abgelegt(repo, ordner):
    node = await repo.create_node(ordner.id, name="doppelt.txt")
    einmal = await node.add_keywords("Physik")
    zweimal = await einmal.add_keywords("Physik")
    assert zweimal.keywords.count("Physik") == 1


# --- Dateien ---------------------------------------------------------------

INHALT = "Hallo aus der Bibliothek.\nZweite Zeile mit Umlaut: Größe.\n".encode()


async def test_datei_hoch_und_wieder_herunterladen(repo, ordner):
    """Die Rundreise muss byte-identisch sein -- sonst geht bei Umlauten oder
    Zeilenenden unbemerkt etwas verloren."""
    node = await repo.create_node(ordner.id, name="datei.txt", titel="Mit Datei")
    mit_datei = await node.content.upload(
        INHALT, filename="datei.txt", mimetype="text/plain",
        version_comment="Testlauf")

    assert mit_datei.content.mimetype == "text/plain"
    assert mit_datei.content.size == len(INHALT)
    assert await mit_datei.content.download() == INHALT


async def test_volltext_wird_extrahiert(repo, ordner):
    node = await repo.create_node(ordner.id, name="volltext.txt")
    mit_datei = await node.content.upload(
        INHALT, filename="volltext.txt", mimetype="text/plain")
    text = await mit_datei.content.text()
    assert "Hallo aus der Bibliothek" in text


async def test_knoten_ohne_datei_meldet_das_klar(repo, ordner):
    """Ein frisch angelegter Knoten hat keinen Binaerinhalt.

    Gemessen und dabei eine Annahme widerlegt: ``downloadUrl`` ist auch dann
    gesetzt, und ein GET darauf liefert **200 mit null Bytes** -- klaglos, und
    nicht von einer leeren Datei zu unterscheiden. Das verlaessliche Signal
    ist ``content.hash``.
    """
    from edusharing.errors import EduSharingError
    node = await repo.create_node(ordner.id, name="ohne-datei.txt")
    assert node.content.download_url, "downloadUrl ist auch ohne Inhalt gesetzt"
    assert node.content.has_content is False
    with pytest.raises(EduSharingError, match="keine Datei"):
        await node.content.download()


async def test_leere_datei_gilt_als_inhalt(repo, ordner):
    """Der Fall, der cclom:size als Signal ausschliesst: eine 0-Byte-Datei hat
    dort ebenfalls None -- der Hash unterscheidet sie."""
    node = await repo.create_node(ordner.id, name="leer.txt")
    leer = await node.content.upload(b"", filename="leer.txt", mimetype="text/plain")
    assert leer.content.has_content is True
    assert leer.get("cclom:size") is None
    assert await leer.content.download() == b""


# --- Sammlungen ------------------------------------------------------------

@pytest.fixture
async def sammlung(repo):
    """Eine eigene, private Sammlung je Testlauf."""
    neu = await repo.create_collection(f"pytest-sammlung-{uuid.uuid4().hex[:8]}")
    assert neu.id
    try:
        yield neu
    finally:
        await neu.delete()


async def test_sammlung_ist_privat(sammlung):
    """Die Vorgabe muss die engste sein -- eine versehentlich oeffentliche
    Sammlung sieht die ganze Instanz."""
    assert (sammlung.raw.get("collection") or {}).get("scope") == "MY"


async def test_inhalt_in_sammlung_legen_und_wieder_herausnehmen(repo, sammlung, ordner):
    """Angelegt wird eine Referenz, keine Kopie: das Original ueberlebt das
    Herausnehmen."""
    io = await repo.create_node(ordner.id, name="fuer-sammlung.txt", titel="Referenzziel")

    assert await repo.add_to_collection(sammlung.id, io.id) is True
    await repo.remove_from_collection(sammlung.id, io.id)

    weiterhin_da = await repo.node(io.id)
    assert weiterhin_da.title == "Referenzziel"


async def test_doppeltes_einlegen_ist_kein_fehler(repo, sammlung, ordner):
    """409 heisst hier: liegt schon drin -- der gewuenschte Zustand. Ein Fehler
    daraus zu machen wuerde jeden Wiederholungslauf sprengen."""
    io = await repo.create_node(ordner.id, name="doppelt-eingelegt.txt")
    assert await repo.add_to_collection(sammlung.id, io.id) is True
    assert await repo.add_to_collection(sammlung.id, io.id) is False
    await repo.remove_from_collection(sammlung.id, io.id)
