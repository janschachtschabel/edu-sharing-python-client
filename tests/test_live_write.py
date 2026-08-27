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
