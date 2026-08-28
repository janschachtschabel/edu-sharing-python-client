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
        ordner.id, name="material.txt", title="Ausgangstitel",
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
    aktualisiert = await knoten.update(title="Geaendert")
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
    node = await repo.create_node(ordner.id, name="datei.txt", title="Mit Datei")
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
    with pytest.raises(EduSharingError, match="carries no file"):
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
    io = await repo.create_node(ordner.id, name="fuer-sammlung.txt", title="Referenzziel")

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


async def test_volltext_gibt_es_nicht_fuer_jeden_dateityp(repo, ordner):
    """Gemessen am 27.08.2026: Markdown und JSON liefern ueber textContent
    einen LEEREN String, waehrend download() die Bytes liefert.

    Das zaehlt fuer alles, was Anweisungen oder Daten als Markdown im
    Repositorium ablegt -- ein leerer Volltext sieht aus wie eine leere Datei.
    Der Test haelt die Eigenschaft fest, damit eine Aenderung der Instanz
    auffaellt statt still die Doku zu widerlegen.
    """
    proben = [
        ("klar.txt", "text/plain", b"Photosynthese im Klartext.", True),
        ("doku.md", "text/markdown", b"# Titel\n\nPhotosynthese.", False),
    ]
    for name, mimetype, inhalt, erwartet_text in proben:
        node = await repo.create_node(ordner.id, name=name, title=name)
        node = await node.content.upload(inhalt, filename=name, mimetype=mimetype)

        assert await node.content.download() == inhalt, f"{name}: Bytes verloren"

        volltext = await node.content.text()
        if erwartet_text:
            assert volltext, f"{name}: kein Volltext, obwohl erwartet"
        else:
            assert not volltext, (
                f"{name}: liefert jetzt Volltext -- die Instanz hat sich "
                "geaendert, der Docstring von NodeContent.text stimmt nicht mehr")


# --- Rueckleseprobe beim Anlegen ------------------------------------------


async def test_ordner_uebernimmt_beim_anlegen_keinen_eigenen_titel(repo, ordner):
    """Gemessen am 28.08.2026: legt man einen cm:folder mit cm:title an, setzt
    edu-sharing cm:title auf cm:name -- der mitgegebene Titel ist weg.

    Bei einem ccm:io kommt derselbe Titel an. Es ist also keine allgemeine
    Regel, sondern eine des Ordnertyps, und ohne die Rueckleseprobe beim
    Anlegen faellt sie niemandem auf.

    Nachtraeglich laesst sich der Titel sehr wohl setzen -- auch das hier
    geprueft, damit die Doku nicht mehr behauptet als gemessen ist.
    """
    with pytest.raises(SilentDropError) as fehler:
        await repo.create_node(
            ordner.id, name="mit-titel", type="cm:folder",
            properties={"cm:title": ["Ein eigener Titel"]})
    assert "cm:title" in fehler.value.dropped

    # Ohne Pruefung entsteht der Ordner, und der Titel ist der Name.
    unter = await repo.create_node(
        ordner.id, name="ohne-pruefung", type="cm:folder", verify=False,
        properties={"cm:title": ["Ein eigener Titel"]})
    frisch = await repo.node(unter.id)
    assert frisch.get("cm:title") == "ohne-pruefung"

    # Nachtraeglich geht es.
    geaendert = await frisch.update(properties={"cm:title": ["Nachgereicht"]})
    assert geaendert.get("cm:title") == "Nachgereicht"


async def test_abgeleitetes_feld_wird_beim_anlegen_gemeldet(repo, ordner):
    """ccm:oeh_lrt_aggregated leitet das Repositorium aus ccm:oeh_lrt ab und
    nimmt es nicht entgegen. Gemessen am 28.08.2026: die POST-Antwort zeigt das
    Feld gar nicht, waehrend ccm:taxonid im selben Aufruf ankommt.

    Ein halb geglueckter Schreibvorgang, der wie ein ganzer aussieht -- genau
    der Fall, fuer den es die Probe gibt.
    """
    aggregiert = await repo.vocab.resolve("ccm:oeh_lrt_aggregated", "Video")
    assert aggregiert, "Vorbedingung: der Wert laesst sich aufloesen"

    with pytest.raises(SilentDropError) as fehler:
        await repo.create_node(
            ordner.id, name="abgeleitet.txt",
            properties={"ccm:oeh_lrt_aggregated": [aggregiert]})
    assert "ccm:oeh_lrt_aggregated" in fehler.value.dropped


# --- Rechte und Veroeffentlichen ------------------------------------------
#
# Alles hier arbeitet ausschliesslich an selbst angelegten Knoten im eigenen
# Wegwerf-Ordner. Kein Test fasst fremde Rechte an.

async def test_frischer_knoten_ist_nicht_oeffentlich(knoten):
    """Die Vorbedingung fuer alles Weitere -- und der Grund, warum es diesen
    Teil gibt: was eine Anwendung anlegt, sieht zunaechst nur sie selbst."""
    assert not (await knoten.permissions.get()).is_public


async def test_veroeffentlichen_und_wieder_zuruecknehmen(knoten):
    assert await knoten.permissions.publish() is True
    assert (await knoten.permissions.get()).is_public

    assert await knoten.permissions.unpublish() is True
    assert not (await knoten.permissions.get()).is_public


async def test_veroeffentlichen_ist_wiederholbar(knoten):
    """Zweimal veroeffentlichen darf nicht zweimal schreiben -- ein zweiter
    Aufruf soll ein wiederholter Lauf sein duerfen, kein Fehler."""
    await knoten.permissions.publish()
    assert await knoten.permissions.publish() is False


async def test_zuruecknehmen_ist_wiederholbar(knoten):
    assert await knoten.permissions.unpublish() is False


async def test_veroeffentlichen_laesst_fremde_eintraege_stehen(repo, knoten):
    """Der POST ersetzt die lokale ACL. Wer nicht zusammenfuehrt, entzieht beim
    Veroeffentlichen anderen ihre Rechte -- unbemerkt, mit HTTP 200."""
    wer = await repo.whoami()
    await knoten.permissions.grant(wer.authority, "Coordinator")
    await knoten.permissions.publish()

    rechte = await knoten.permissions.get()
    assert rechte.allows(wer.authority, "Coordinator"), "eigener Eintrag verloren"
    assert rechte.is_public


async def test_recht_entziehen_laesst_die_uebrigen_stehen(repo, knoten):
    wer = await repo.whoami()
    await knoten.permissions.grant(wer.authority, "Coordinator")
    await knoten.permissions.publish()

    await knoten.permissions.revoke(wer.authority, "Coordinator")
    rechte = await knoten.permissions.get()
    assert not rechte.allows(wer.authority, "Coordinator")
    assert rechte.is_public, "das Veroeffentlichen ist mit weggeflogen"


async def test_unbekannte_gruppe_wird_still_verworfen(knoten):
    """Gemessen am 28.08.2026: HTTP 200, und danach steht nichts da. Dieselbe
    Klasse von Verlust wie bei den Properties, an einer anderen Stelle."""
    with pytest.raises(SilentDropError) as fehler:
        await knoten.permissions.grant("GROUP_gibtesnicht_xyz_9f3a", "Consumer")
    assert "GROUP_gibtesnicht_xyz_9f3a" in fehler.value.dropped


async def test_unbekannter_benutzer_wird_dagegen_gespeichert(knoten):
    """Die Kehrseite, und der Grund, warum der vorige Test eine Gruppe nimmt:
    Benutzernamen prueft das Repositorium nicht. Der Eintrag wird abgelegt und
    berechtigt niemanden -- die Rueckleseprobe kann einen Tippfehler im
    Benutzernamen also nicht auffangen. Das gehoert gesagt, statt es fuer
    abgedeckt zu halten."""
    assert await knoten.permissions.grant("gibtesnicht-xyz-9f3a", "Consumer") is True
    rechte = await knoten.permissions.get()
    assert rechte.allows("gibtesnicht-xyz-9f3a", "Consumer")


async def test_unbekanntes_recht_ist_dagegen_laut(repo, knoten):
    """Der Gegenbeweis zum vorigen Test: nicht alles an diesem Endpunkt ist
    still. Ein erfundener Rechtename kommt als 500 zurueck."""
    from edusharing.errors import ServerError
    wer = await repo.whoami()
    with pytest.raises(ServerError):
        await knoten.permissions.grant(wer.authority, "Quatschrecht")


# --- Vererbung -------------------------------------------------------------

async def test_kind_eines_oeffentlichen_ordners_ist_oeffentlich(repo, ordner):
    """Ohne eigenen Eintrag. Wer nur die lokale ACL liest, haelt einen fuer
    alle lesbaren Knoten fuer privat."""
    kind = await repo.create_node(ordner.id, name="geerbt.txt", title="Geerbt")
    await ordner.permissions.publish()

    rechte = await kind.permissions.get()
    assert rechte.own == (), "das Kind hat keinen eigenen Eintrag"
    assert rechte.is_public


async def test_zuruecknehmen_meldet_die_vererbung(repo, ordner):
    """Lokal gibt es nichts zu entfernen, und der Knoten bleibt oeffentlich.
    ``False`` zurueckzugeben hiesse behaupten, er sei jetzt privat."""
    from edusharing.errors import ConflictError
    kind = await repo.create_node(ordner.id, name="geerbt2.txt", title="Geerbt")
    await ordner.permissions.publish()

    with pytest.raises(ConflictError):
        await kind.permissions.unpublish()


# --- Wo ein Knoten liegt, und wer ihn kuratiert hat ------------------------

async def test_der_weg_nach_oben(repo, ordner):
    """Der Endpunkt liefert den Knoten selbst als ersten Eintrag -- gemessen.
    Die Bibliothek zieht ihn ab, sonst waere er sein eigener Vorfahre."""
    unter = await repo.create_node(ordner.id, name="unterordner", type="cm:folder")
    knoten = await repo.create_node(unter.id, name="tief.txt", title="Tief")

    eltern = await knoten.parents()
    assert [n.id for n in eltern] == [unter.id, ordner.id], "naechster zuerst"
    assert knoten.id not in [n.id for n in eltern]


async def test_die_vorfahren_tragen_ihre_namen(repo, ordner):
    """Ohne propertyFilter kommen sie mit leeren properties zurueck. Ein Pfad
    ohne Beschriftung ist als Brotkrume wertlos."""
    knoten = await repo.create_node(ordner.id, name="k.txt", title="K")
    eltern = await knoten.parents()
    assert eltern and eltern[0].name == ordner.name


async def test_sammlungen_eines_knotens(repo, ordner, sammlung):
    """Die andere Frage: nicht wo der Knoten liegt, sondern wer ihn eingelegt
    hat. Eine Sammlung haelt eine Referenz -- das Original bleibt, wo es ist."""
    knoten = await repo.create_node(ordner.id, name="kuratiert.txt", title="K")
    assert await knoten.collections() == []

    await repo.add_to_collection(sammlung.id, knoten.id)
    drin = await knoten.collections()
    assert [s.id for s in drin] == [sammlung.id]
    assert drin[0].title == sammlung.title, "der Eintrag traegt den ganzen Knoten"

    # Und das Elternteil ist davon unberuehrt.
    assert [n.id for n in await knoten.parents()] == [ordner.id]


async def test_placement_beantwortet_beides(repo, ordner, sammlung):
    knoten = await repo.create_node(ordner.id, name="verortet.txt", title="Verortet")
    await repo.add_to_collection(sammlung.id, knoten.id)

    ergebnis = await repo.flows.placement(knoten.id)
    assert ergebnis["title"] == "Verortet"
    assert [s["id"] for s in ergebnis["collections"]] == [sammlung.id]
    assert ergebnis["path"][-1]["id"] == ordner.id, "von oben nach unten"
    assert ergebnis["scope"], "der Endpunkt nennt, wie weit er reicht"


# --- Bewertungen und Kommentare -------------------------------------------
#
# Wieder nur an selbst angelegten Knoten im eigenen Wegwerf-Ordner.

async def test_frischer_knoten_ist_unbewertet(knoten):
    assert knoten.rating is None


async def test_bewerten_und_zuruecknehmen(knoten):
    bewertet = await knoten.rate(4, "Sehr brauchbar")
    assert bewertet is not None
    assert bewertet.average == 4.0
    assert bewertet.count == 1
    assert bewertet.own == 4.0

    assert await knoten.unrate() is None


async def test_die_null_wird_nicht_geschrieben(repo, knoten):
    """Gemessen: rating=0 zaehlt als abgegebene Null und zieht den Schnitt
    herunter, statt zurueckzunehmen. Die Bibliothek laesst sie nicht durch."""
    with pytest.raises(ValueError, match="unrate"):
        await knoten.rate(0)
    assert (await repo.node(knoten.id)).rating is None


async def test_bewerten_ist_wiederholbar(knoten):
    await knoten.rate(3)
    zweite = await knoten.rate(5)
    assert zweite.count == 1, "dieselbe Stimme, nicht eine zweite"
    assert zweite.own == 5.0


async def test_kommentar_schreiben_lesen_aendern_loeschen(knoten):
    assert await knoten.comments.list() == []

    neu = await knoten.comments.add("Ein Kommentar mit Umlauten: Groesse, Ubung")
    assert neu.text == "Ein Kommentar mit Umlauten: Groesse, Ubung"
    assert neu.author

    geaendert = await knoten.comments.edit(neu.id, "Nachgebessert")
    assert geaendert.text == "Nachgebessert"

    await knoten.comments.delete(neu.id)
    assert await knoten.comments.list() == []


async def test_der_text_kommt_ohne_anfuehrungszeichen_zurueck(knoten):
    """Der Kernfall: edu-sharing speichert den Body 1:1. Mit ``json=`` staende
    hier '"Erster"' statt 'Erster'."""
    neu = await knoten.comments.add("Erster")
    assert neu.text == "Erster"
    assert '"' not in neu.text


async def test_auf_einen_kommentar_antworten(knoten):
    frage = await knoten.comments.add("Eine Frage")
    antwort = await knoten.comments.add("Eine Antwort", reply_to=frage.id)
    assert antwort.reply_to == frage.id

    alle = await knoten.comments.list()
    assert {k.id for k in alle} == {frage.id, antwort.id}


# --- Vorschlaege und redaktionelle Einreichung -----------------------------

async def test_vorschlagen_und_entscheiden(repo, knoten):
    assert await knoten.suggestions.list() == []

    vorschlag = await knoten.suggestions.propose(
        "cclom:general_keyword", "Photosynthese",
        "Der Titel nennt das Thema", confidence=0.9)
    assert vorschlag.status == "PENDING"
    assert vorschlag.value == "Photosynthese"

    (gelesen,) = await knoten.suggestions.list()
    assert gelesen.id == vorschlag.id
    assert gelesen.why == "Der Titel nennt das Thema"


async def test_annehmen_traegt_den_wert_nicht_ein(repo, knoten):
    """Der Vorbehalt, live reproduziert. Der wlo-mcp-sc hat ihn am 01.08.2026
    gemessen, hier ist er noch einmal: nach ACCEPTED steht das Schlagwort
    nicht am Knoten. Wer glaubt, es stuende dort, hat einen Datensatz, der
    aussieht wie gepflegt und keiner ist."""
    vorschlag = await knoten.suggestions.propose(
        "cclom:general_keyword", "Photosynthese", "Weil")
    await knoten.suggestions.decide([vorschlag.id])

    frisch = await repo.node(knoten.id)
    assert frisch.keywords == [], "der Endpunkt wendet nichts an"

    (danach,) = await knoten.suggestions.list()
    assert danach.status == "ACCEPTED", "nur der Stand wandert"


async def test_ablehnen_setzt_den_anderen_stand(repo, knoten):
    vorschlag = await knoten.suggestions.propose("ccm:taxonid", "Biologie", "Weil")
    await knoten.suggestions.decide([vorschlag.id], accept=False)
    (danach,) = await knoten.suggestions.list()
    assert danach.status == "DECLINED"


async def test_einreichen_und_verlauf(repo, knoten):
    assert await knoten.workflow.history() == []

    wer = await repo.whoami()
    schritt = await knoten.workflow.submit(wer.authority, "100_tocheck",
                                           "Bitte pruefen")
    assert schritt.status == "100_tocheck"
    assert schritt.receivers == (wer.authority,)
    assert schritt.comment == "Bitte pruefen"
    assert schritt.editor == wer.authority

    verlauf = await knoten.workflow.history()
    assert len(verlauf) == 1


async def test_der_verlauf_kommt_neueste_zuerst(repo, knoten):
    """Der Verlauf ist ein Protokoll, kein Zustand -- jeder Schritt bleibt.
    Und er kommt in umgekehrter Reihenfolge zurueck: gemessen am 28.08.2026
    stand der zweite Schritt vorn. Darauf beruht die Rueckleseprobe von
    submit(), die den ersten Treffer nimmt."""
    wer = await repo.whoami()
    await knoten.workflow.submit(wer.authority, "100_tocheck", "Erst")
    await knoten.workflow.submit(wer.authority, "200_tosave", "Dann")
    verlauf = await knoten.workflow.history()
    assert [s.status for s in verlauf] == ["200_tosave", "100_tocheck"]
    assert verlauf[0].at >= verlauf[1].at
