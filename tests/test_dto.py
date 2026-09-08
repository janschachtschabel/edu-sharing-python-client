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
)

QUELLE = Path(__file__).resolve().parent.parent / "src" / "edusharing"


# --- first -----------------------------------------------------------------


@pytest.mark.parametrize(("wert", "erwartet"), [
    (["a", "b"], "a"),
    ([], None),
    ("a", "a"),
    ("", None),
    (None, None),
    (0, None),
    ([42], "42"),
    ([0], "0"),
    ([""], ""),
])
def test_first_nimmt_den_ersten_wert(wert, erwartet):
    """edu-sharing liefert Eigenschaften immer als Liste, auch einzelne.

    Die beiden letzten Faelle sind die ueberraschenden und darum die
    wichtigsten: in einer Liste zaehlt, dass die Liste da ist, nicht ob ihr
    erster Wert etwas taugt. ``[""]`` ergibt ``""``, nicht ``None``. Ein
    blanker falscher Wert dagegen gilt als nicht gesetzt.
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
