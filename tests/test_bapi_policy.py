"""Modellwahl und Request-Bau der b-api -- ohne Netz.

Alle Erwartungen stammen aus Messungen gegen die b-api (Staging). Die
Eigenheiten sind nicht optional: wer sie ignoriert, bekommt HTTP 400 oder
wartet das Sieben- bis Neunfache.
"""

from datetime import date

import pytest

from edusharing.bapi.policy import Model, build_body, pick_model, read_answer


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
    with pytest.raises(ValueError, match="wunsch"):
        pick_model([_m("a")], prefer="wunsch")


def test_ohne_brauchbares_modell_wird_das_gesagt():
    with pytest.raises(ValueError):
        pick_model([_m("a", status="loading")])


def test_leere_liste():
    with pytest.raises(ValueError):
        pick_model([])


# --- Request-Bau -----------------------------------------------------------

def test_normales_modell_bekommt_max_tokens():
    body = build_body("glm-4.7", [{"role": "user", "content": "hi"}], max_tokens=100)
    assert body["max_tokens"] == 100
    assert "temperature" in body
    assert "max_completion_tokens" not in body


@pytest.mark.parametrize("mid", ["gpt-5.6-luna", "gpt-5-mini", "o1-preview", "o3", "o4-mini"])
def test_gpt5_und_o_serie_brauchen_max_completion_tokens(mid):
    """Gemessen: sonst HTTP 400. Und temperature lehnen sie ebenfalls ab."""
    body = build_body(mid, [{"role": "user", "content": "hi"}], max_tokens=100)
    assert body["max_completion_tokens"] == 100
    assert "max_tokens" not in body
    assert "temperature" not in body


def test_qwen3_bekommt_das_denken_abgeschaltet():
    """Gemessen Faktor 7 bis 9: qwen3.6-35b-a3b brauchte 17,33 s mit Denken
    und 1,96 s ohne. '/no_think' im Prompt wirkt nicht -- das ist Qwen2.5."""
    body = build_body("qwen3.6-35b-a3b", [{"role": "user", "content": "hi"}])
    assert body["chat_template_kwargs"] == {"enable_thinking": False}


def test_mistral_bekommt_das_flag_nicht():
    """Gemessen: 400 'chat_template is not supported for Mistral tokenizers'."""
    body = build_body("mistral-medium-3.5-128b", [{"role": "user", "content": "hi"}])
    assert "chat_template_kwargs" not in body


def test_denken_laesst_sich_erzwingen():
    body = build_body("qwen3.6-35b-a3b", [{"role": "user", "content": "hi"}], thinking=True)
    assert "chat_template_kwargs" not in body


def test_streaming_verlangt_die_verbrauchsangabe():
    body = build_body("glm-4.7", [{"role": "user", "content": "hi"}], stream=True)
    assert body["stream"] is True
    assert body["stream_options"] == {"include_usage": True}


# --- Antwort auslesen ------------------------------------------------------

def test_antworttext_wird_gelesen():
    antwort = {"choices": [{"message": {"content": "Die Antwort"}}]}
    assert read_answer(antwort) == "Die Antwort"


def test_reasoning_faengt_ein_aufgebrauchtes_budget_auf():
    """Gemessen: Reasoning-Modelle zaehlen ihr Denken mit. Ist das Budget
    aufgebraucht, kommt content: null und der Text steht in reasoning --
    qwen3.6-35b-a3b produzierte einmal 1.500 Tokens reines Reasoning ohne ein
    Zeichen Antwort."""
    antwort = {"choices": [{"message": {"content": None, "reasoning": "Gedanken"},
                            "finish_reason": "length"}]}
    assert read_answer(antwort) == "Gedanken"


def test_leere_antwort_ergibt_leeren_text():
    assert read_answer({"choices": []}) == ""
    assert read_answer({}) == ""


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


# --- reasoning_effort und verbosity ----------------------------------------
#
# Gemessen am 31.08.2026 gegen die b-api (Staging):
#
#   gpt-5.6-luna    ohne Parameter   completion=32  reasoning=14
#   gpt-5.6-luna    effort=low       completion=11  reasoning=0     <- wirkt
#   gpt-5.6-luna    effort=high      completion=35  reasoning=17
#   gpt-5-nano      effort=low       200
#   gpt-4o-mini     effort=low       400 Unrecognized request argument
#   gpt-3.5-turbo   effort=low       400 Unrecognized request argument
#   gpt-4o-mini     verbosity=low    400 does not support 'low' ... only 'medium'
#   qwen3.5-122b    effort=low/high  200, aber completion identisch -> ignoriert
#
# Daraus die Regel: low ist die Vorgabe, weil sie messbar Denk-Tokens spart.
# Wo das Modell sie nicht kennt, entfaellt sie stillschweigend -- eine Vorgabe
# darf das. Ein ausdruecklich uebergebener Wert darf es nicht: still verworfen
# saehe eine Antwort mit hohem Aufwand genauso aus wie eine mit niedrigem.

def test_vorgabe_low_landet_im_rumpf_wo_das_modell_sie_kennt():
    body = build_body("gpt-5.6-luna", [{"role": "user", "content": "x"}])
    assert body["reasoning_effort"] == "low"
    assert body["verbosity"] == "low"


def test_vorgabe_entfaellt_still_wo_das_modell_sie_nicht_kennt():
    """gpt-4o-mini antwortet sonst mit 400."""
    body = build_body("gpt-4o-mini", [{"role": "user", "content": "x"}])
    assert "reasoning_effort" not in body
    assert "verbosity" not in body


def test_vorgabe_entfaellt_auch_bei_der_academiccloud():
    """Dort wird der Parameter angenommen und ignoriert -- also nicht senden."""
    body = build_body("qwen3.5-122b-a10b", [{"role": "user", "content": "x"}])
    assert "reasoning_effort" not in body


@pytest.mark.parametrize("feld", ["reasoning_effort", "verbosity"])
def test_ausdruecklicher_wunsch_wird_nicht_still_verworfen(feld):
    """Der Kern der Regel."""
    with pytest.raises(ValueError) as info:
        build_body("gpt-4o-mini", [{"role": "user", "content": "x"}], **{feld: "high"})
    assert "gpt-4o-mini" in str(info.value)
    assert feld in str(info.value)


def test_ausdruecklicher_wunsch_wird_uebernommen_wo_er_geht():
    body = build_body("gpt-5.6-luna", [{"role": "user", "content": "x"}],
                      reasoning_effort="high", verbosity="medium")
    assert body["reasoning_effort"] == "high"
    assert body["verbosity"] == "medium"


@pytest.mark.parametrize("modell", ["gpt-5.6-luna", "gpt-4o-mini"])
def test_none_heisst_gar_nicht_senden(modell):
    body = build_body(modell, [{"role": "user", "content": "x"}],
                      reasoning_effort=None, verbosity=None)
    assert "reasoning_effort" not in body
    assert "verbosity" not in body
