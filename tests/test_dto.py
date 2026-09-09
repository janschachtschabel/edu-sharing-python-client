"""Ein Knotensatz, einmal gelesen.

Derselbe Datensatz wurde an fuenf Stellen verschieden gelesen: ``_first``
dreimal definiert (einmal mit ``""`` statt ``None`` als Ergebnis), ``_bare``
zweimal, die Ansichts-URL an fuenf Stellen gebaut, ``(raw["ref"])["id"]`` an
zwoelf, ``pagination.total`` an acht. Wer ein Feld umbenennt, muss es dann in
einem Dutzend Dateien jagen (Audit MNT-1).

Hier steht, was die eine Lesart leistet -- und eine Wache, die eine neue
Kopie beim naechsten Mal auffallen laesst.
"""

import ast
from pathlib import Path

import pytest

from edusharing.dto import (
    bare_id,
    first,
    node_id_of,
    page_total,
    render_url,
    stored_title_of,
    title_of,
)
from edusharing.nodes import Node
from edusharing.results import SearchHit
from edusharing.skills_registry import _title as registry_title

QUELLE = Path(__file__).resolve().parent.parent / "src" / "edusharing"


# --- first -----------------------------------------------------------------


@pytest.mark.parametrize(("wert", "erwartet"), [
    (["a", "b"], "a"),
    ([], None),
    ("a", "a"),
    ("", ""),
    (None, None),
    (0, "0"),
    (False, "False"),
    ([42], "42"),
    ([0], "0"),
    ([""], ""),
])
def test_first_nimmt_den_ersten_wert(wert, erwartet):
    """edu-sharing liefert Eigenschaften immer als Liste, auch einzelne.

    Eine Regel fuer beide Formen: **nur Abwesenheit und die leere Liste sind
    keine Werte.** ``[""]`` ergibt ``""``, und ein blankes ``0`` ergibt
    ``"0"``.

    Der blanke Fall galt bis zum 08.09.2026 als nicht gesetzt, mit einem
    eigenen Testfall (Audit COR-9). Ein gemessener Schaden stand nicht
    dahinter: jeder Aufruf von ``first`` liest ``properties.get(...)``, und
    edu-sharing schickt Listen -- der Skalarzweig ist ein Sicherheitsnetz,
    das in der Praxis nie ein blankes ``0`` trug.

    Falsch war, dass dieses Netz eine **andere** Regel hatte als die, die
    ``flows/serialize.py`` fuer dieselbe Frage aufschreibt: "``0`` und
    ``False`` sind Werte; nur Abwesenheit und die leere Liste sind es nicht."
    Ein Sicherheitsnetz, das der Regel widerspricht, die es absichert, hat
    die falsche Form fuer den Tag, an dem es doch etwas faengt. Jetzt gilt
    eine Regel an beiden Stellen.
    """
    assert first(wert) == erwartet


def test_first_gibt_none_und_nicht_leerstring():
    """Die Registry gab bisher ``""`` zurueck, die beiden anderen ``None``.
    Ein Aufrufer, der auf ``is None`` prueft, sah je nach Herkunft etwas
    anderes (Audit MNT-1)."""
    assert first([]) is None
    assert first(None) is None


# --- node_id_of ------------------------------------------------------------


def test_node_id_of_liest_die_referenz():
    assert node_id_of({"ref": {"id": "9f2c"}}) == "9f2c"


@pytest.mark.parametrize("roh", [{}, {"ref": None}, {"ref": {}}, {"ref": {"id": None}}])
def test_node_id_of_ist_leer_wenn_es_keine_gibt(roh):
    """Nie ``None``: der Wert geht in URLs und Routen, und ein ``None`` dort
    faellt erst weit weg auf."""
    assert node_id_of(roh) == ""


# --- bare_id ---------------------------------------------------------------


@pytest.mark.parametrize(("ref", "erwartet"), [
    ("workspace://SpacesStore/9f2c", "9f2c"),
    ("9f2c", "9f2c"),
    ("", ""),
])
def test_bare_id_streift_das_praefix_ab(ref, erwartet):
    """Der Seitenbauer schreibt volle Store-Referenzen; jede REST-Route dieser
    Bibliothek nimmt die blanke id."""
    assert bare_id(ref) == erwartet


# --- render_url ------------------------------------------------------------


def test_render_url_baut_die_ansichts_adresse():
    assert render_url("https://repo.test/edu-sharing", "9f2c") == (
        "https://repo.test/edu-sharing/components/render/9f2c")


def test_render_url_ohne_id_ist_leer():
    """Eine Adresse auf nichts ist keine Adresse -- fuenf Baustellen, drei
    Antworten darauf (Audit MNT-1)."""
    assert render_url("https://repo.test/edu-sharing", "") == ""


# --- page_total ------------------------------------------------------------


def test_page_total_liest_die_gesamtzahl():
    assert page_total({"pagination": {"total": 128, "from": 0}}) == 128


@pytest.mark.parametrize("antwort", [{}, {"pagination": None}, {"pagination": {}},
                                     {"pagination": {"total": None}}])
def test_page_total_faellt_auf_die_vorgabe(antwort):
    """``ngsearch`` liefert ``pagination: null`` -- dort gibt es keine
    Gesamtzahl, und der Aufrufer sagt, was dann gelten soll."""
    assert page_total(antwort) == 0
    assert page_total(antwort, default=7) == 7


# --- Die Wache -------------------------------------------------------------


def _definierte(name: str) -> list[str]:
    """Jede Datei, die eine Funktion dieses Namens selbst definiert."""
    gefunden = []
    for pfad in sorted(QUELLE.rglob("*.py")):
        if "_generated" in pfad.parts or pfad.name == "dto.py":
            continue
        baum = ast.parse(pfad.read_text(encoding="utf-8"), filename=str(pfad))
        for knoten in ast.walk(baum):
            if isinstance(knoten, ast.FunctionDef) and knoten.name == name:
                gefunden.append(pfad.relative_to(QUELLE).as_posix())
    return gefunden


@pytest.mark.parametrize("name", ["_first", "_bare", "first", "bare_id", "node_id_of"])
def test_niemand_definiert_die_leser_ein_zweites_mal(name):
    """Die Doppelung entstand nicht auf einmal, sondern eine Kopie nach der
    anderen. Diese Wache faellt beim naechsten Mal auf, statt beim naechsten
    Audit."""
    assert _definierte(name) == []


# --- title_of --------------------------------------------------------------


@pytest.mark.parametrize(("roh", "erwartet"), [
    ({"title": "Angezeigt", "properties": {"cclom:title": ["LOM"],
                                           "cm:title": ["Alfresco"],
                                           "cm:name": ["datei.pdf"]}}, "Angezeigt"),
    ({"properties": {"cclom:title": ["LOM"], "cm:title": ["Alfresco"],
                     "cm:name": ["datei.pdf"]}}, "LOM"),
    ({"properties": {"cm:title": ["Alfresco"], "cm:name": ["datei.pdf"]}}, "Alfresco"),
    ({"properties": {"cm:name": ["datei.pdf"]}}, "datei.pdf"),
    ({"properties": {}}, ""),
    ({}, ""),
    ({"title": "", "properties": {"cm:name": ["datei.pdf"]}}, "datei.pdf"),
])
def test_title_of_folgt_einer_kette(roh, erwartet):
    """Was die Schnittstelle selbst anzeigt, dann der LOM-Titel, dann der von
    Alfresco, zuletzt der Dateiname. Ein Name ist besser als nichts, und die
    ausdruecklichen Titel stehen vor ihm."""
    assert title_of(roh) == erwartet


def test_alle_objekte_lesen_denselben_titel():
    """Der Kern des Befunds: derselbe Datensatz zeigte je nach Objekt einen
    anderen Titel. Ein Datensatz mit LOM-Titel und abweichendem Dateinamen kam
    als Treffer als 'arbeitsblatt.pdf' an, als Knoten als 'Bruchrechnung'
    (Audit MNT-1)."""
    roh = {"ref": {"id": "n1"},
           "properties": {"cclom:title": ["Bruchrechnung"],
                          "cm:name": ["arbeitsblatt.pdf"]}}
    assert Node(roh, None).title == "Bruchrechnung"
    assert SearchHit.from_node(roh, "https://repo.test").title == "Bruchrechnung"
    assert registry_title(roh) == "Bruchrechnung"


@pytest.mark.parametrize(("roh", "erwartet"), [
    ({"title": "Angezeigt", "properties": {"cm:name": ["datei.pdf"]}}, "Angezeigt"),
    ({"properties": {"cclom:title": ["LOM"], "cm:name": ["datei.pdf"]}}, "LOM"),
    ({"properties": {"cm:title": ["Alfresco"], "cm:name": ["datei.pdf"]}}, "Alfresco"),
    ({"properties": {"cm:name": ["datei.pdf"]}}, ""),
    ({}, ""),
])
def test_stored_title_of_faellt_nicht_auf_den_namen_zurueck(roh, erwartet):
    """Das Gegenstueck zu ``title_of``: was ein Schreibvorgang erhaelt.

    Der Anzeigetitel faellt auf den Dateinamen zurueck. Diesen beim Erhalten
    eines Titels zu schreiben, legt Metadaten an, die niemand verlangt hat --
    gemessen an einer Sammlung ohne Titel, deren Beschreibung geaendert wurde
    (Review 08.09.2026)."""
    assert stored_title_of(roh) == erwartet


def test_die_beiden_titelfragen_unterscheiden_sich_genau_dort():
    roh = {"properties": {"cm:name": ["arbeitsblatt.pdf"]}}
    assert title_of(roh) == "arbeitsblatt.pdf"
    assert stored_title_of(roh) == ""


@pytest.mark.parametrize("wert", [None, ""])
def test_page_total_nimmt_die_vorgabe_wenn_nichts_gesagt_ist(wert):
    """``None`` und ``""`` heissen beide "nicht gesagt". Ein leeres Feld darf
    die Auflistung nicht mit einem ValueError beenden."""
    assert page_total({"pagination": {"total": wert}}, default=7) == 7


def test_eine_genannte_null_ist_eine_antwort():
    """Der Befund, um den es ging: acht Aufrufstellen schrieben ``or``, und
    ein Aufrufer mit einer Vorgabe ungleich 0 bekam sie bei einer leeren
    Auflistung zurueck (Review 08.09.2026)."""
    assert page_total({"pagination": {"total": 0}}, default=7) == 0
