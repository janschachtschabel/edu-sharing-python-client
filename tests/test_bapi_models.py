"""Welches Modell -- Wahl, Auslastung, Abkuendigung. Ohne Netz.

Alle Erwartungen stammen aus Messungen gegen die b-api (Staging). Die
Rumpfform steht in ``test_bapi_body.py``: zwei Fragen, die sich unabhaengig
voneinander bewegen.
"""

from datetime import date

import pytest

from edusharing.bapi.models import Model, pick_model
from edusharing.errors import ValidationError


def _m(mid, demand=0, status="ready", output=("text",)):
    return Model(id=mid, demand=demand, status=status,
                 input=("text",), output=tuple(output), owned_by="chat-ai", name=mid)


# --- Modellwahl ------------------------------------------------------------

def test_geringste_auslastung_gewinnt():
    """demand sagt die Wartezeit gut vorher: gemessen unter 0,6 s bei 0 und
    30 bis 41 s bei 5."""
    gewaehlt = pick_model([_m("a", demand=3), _m("b", demand=0), _m("c", demand=1)])
    assert gewaehlt.id == "b"


def test_nicht_bereite_modelle_werden_uebersprungen():
    gewaehlt = pick_model([_m("a", demand=0, status="loading"), _m("b", demand=4)])
    assert gewaehlt.id == "b"


def test_modelle_ohne_textausgabe_werden_uebersprungen():
    """Ein Embedding-Modell an /chat/completions antwortet mit
    '404 This is not a chat model'."""
    gewaehlt = pick_model([_m("embed", output=("embedding",)), _m("chat")])
    assert gewaehlt.id == "chat"


def test_bevorzugtes_modell_gewinnt_wenn_verfuegbar():
    gewaehlt = pick_model([_m("a", demand=0), _m("wunsch", demand=5)], prefer="wunsch")
    assert gewaehlt.id == "wunsch"


def test_bevorzugtes_modell_das_es_nicht_gibt_faellt_auf():
    """Modell-IDs aendern sich ohne Ankuendigung -- gemessen wurde aus
    deepseek-v4-flash binnen neun Tagen deepseek-v4-flash-0731, der alte Name
    antwortet seither mit 503. Ein stiller Wechsel auf ein anderes Modell
    waere schlimmer als ein Fehler."""
    with pytest.raises(ValidationError, match="wunsch"):
        pick_model([_m("a")], prefer="wunsch")


def test_ohne_brauchbares_modell_wird_das_gesagt():
    with pytest.raises(ValidationError):
        pick_model([_m("a", status="loading")])


def test_leere_liste():
    with pytest.raises(ValidationError):
        pick_model([])


# --- Abkuendigung ----------------------------------------------------------
#
# Gemessen am 31.08.2026: 57 von 132 OpenAI-Modellen tragen ein
# ``shutdown_date``, und acht verschiedene Termine kommen vor -- der frueheste
# (2026-07-23) lag zu dem Zeitpunkt bereits in der Vergangenheit, das Modell
# stand aber weiter in der Liste. Die AcademicCloud kennt das Feld nicht.

def test_shutdown_date_wird_gelesen():
    m = Model.from_response({"id": "gpt-4", "shutdown_date": "2026-10-23"})
    assert m.shutdown_date == "2026-10-23"


def test_ohne_shutdown_date_bleibt_es_leer():
    """Die AcademicCloud liefert das Feld nicht -- das ist keine Abkuendigung."""
    assert Model.from_response({"id": "glm-4.7"}).shutdown_date is None


@pytest.mark.parametrize("tag, erwartet", [
    (date(2026, 10, 22), False),   # davor
    (date(2026, 10, 23), True),    # am Tag selbst
    (date(2026, 10, 24), True),    # danach
])
def test_abgekuendigt_ab_dem_termin(tag, erwartet):
    m = Model.from_response({"id": "gpt-4", "shutdown_date": "2026-10-23"})
    assert m.is_retired_on(tag) is erwartet


def test_ohne_termin_nie_abgekuendigt():
    assert Model.from_response({"id": "x"}).is_retired_on(date(2099, 1, 1)) is False


def test_unlesbarer_termin_gilt_nicht_als_abgekuendigt():
    """Fremde Daten duerfen keine Ausnahme ausloesen.

    Ein unerwartetes Format ist ein Grund, nichts zu behaupten -- nicht ein
    Grund, das Modell fuer tot zu erklaeren.
    """
    m = Model.from_response({"id": "x", "shutdown_date": "demnaechst"})
    assert m.is_retired_on(date(2099, 1, 1)) is False


# --- Virtuelles Modell -----------------------------------------------------
#
# Mehrere Modelle unter einem Namen, und die Bibliothek nimmt daraus immer das
# am wenigsten ausgelastete. Nur die AcademicCloud meldet ``demand``; bei
# OpenAI ist das Feld nicht vorhanden, dort wird daraus eine Ausweichkette in
# der genannten Reihenfolge.

def test_die_wahl_faellt_innerhalb_der_genannten_modelle():
    """Ein niedriger ausgelastetes Modell ausserhalb der Auswahl gewinnt nicht."""
    modelle = [_m("a", demand=3), _m("b", demand=0), _m("c", demand=1)]
    assert pick_model(modelle, among=["a", "c"]).id == "c"


def test_ein_unbekannter_name_in_der_auswahl_faellt_auf():
    with pytest.raises(ValidationError) as info:
        pick_model([_m("a"), _m("b")], among=["a", "gibt-es-nicht"])
    assert "gibt-es-nicht" in str(info.value)


def test_auswahl_ohne_brauchbares_modell():
    modelle = [_m("a", status="loading"), _m("b", demand=0)]
    with pytest.raises(ValidationError) as info:
        pick_model(modelle, among=["a"])
    assert "a" in str(info.value)


def test_leere_auswahl_ist_ein_fehler():
    with pytest.raises(ValidationError):
        pick_model([_m("a")], among=[])


def test_ohne_auslastung_entscheidet_die_reihenfolge_der_auswahl():
    """OpenAI meldet kein ``demand`` -- dann ist die genannte Reihenfolge die
    Aussage des Aufrufers und wird respektiert."""
    modelle = [_m("zebra", demand=None), _m("alpha", demand=None)]
    assert pick_model(modelle, among=["zebra", "alpha"]).id == "zebra"


def test_prefer_und_among_zusammen_ist_ein_fehler():
    """Zwei Arten, dasselbe zu bestimmen -- da muss der Aufrufer sich festlegen."""
    with pytest.raises(ValidationError):
        pick_model([_m("a")], prefer="a", among=["a"])
