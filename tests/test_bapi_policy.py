"""Modellwahl und Request-Bau der b-api -- ohne Netz.

Alle Erwartungen stammen aus Messungen gegen die b-api (Staging). Die
Eigenheiten sind nicht optional: wer sie ignoriert, bekommt HTTP 400 oder
wartet das Sieben- bis Neunfache.
"""

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
