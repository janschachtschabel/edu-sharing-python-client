"""Tests gegen die echte b-api.

    B_API_KEY=... uv run pytest -m live

Beantworten die Frage, die Mocks nicht beantworten koennen: stimmen die
Modell-IDs und die Request-Eigenheiten noch? Beide aendern sich ohne
Ankuendigung -- aus deepseek-v4-flash wurde binnen neun Tagen
deepseek-v4-flash-0731, der alte Name antwortet seither mit 503.
"""

import os
from datetime import date

import pytest

from edusharing.bapi import BildungsAPI
from edusharing.errors import EduSharingError

# Zwei Variablen, seit der Client keine Vorgabe-Adresse mehr hat (28.08.2026).
# Vorher genuegte B_API_KEY, weil die Adresse auf ein Staging-Gateway
# zurueckfiel -- genau der Grund, warum sie weg ist. Ohne diese Bedingung
# scheitert die Fixture mit einem EduSharingError, statt sich zu ueberspringen:
# gemessen 6 Fehler in einem Lauf, in dem nur der Schluessel gesetzt war.
pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not (os.environ.get("B_API_KEY") and os.environ.get("B_API_BASE_URL")),
        reason="B_API_KEY/B_API_BASE_URL nicht gesetzt",
    ),
]


@pytest.fixture
async def llm():
    async with BildungsAPI.from_env() as api:
        yield api


async def test_modelle_werden_gemeldet(llm):
    modelle = await llm.models()
    assert modelle, "keine Modelle gemeldet"
    assert all(m.id for m in modelle)


async def test_auslastung_wird_durchgereicht(llm):
    """demand ist die einzige Auslastungsinformation, die es gibt -- ohne sie
    waere die Modellwahl blind."""
    modelle = await llm.models()
    mit_angabe = [m for m in modelle if m.demand is not None]
    assert mit_angabe, "kein einziges Modell meldet demand"


async def test_automatische_modellwahl_liefert_eine_antwort(llm):
    antwort = await llm.chat("Antworte mit genau einem Wort: Hallo.", max_tokens=50)
    assert antwort.strip(), "leere Antwort"


async def test_qwen3_antwortet_mit_abgeschaltetem_denken(llm):
    """Der Fall, der Faktor 7 bis 9 ausmacht -- und bei dem ein leerer
    content zurueckkaeme, wenn das Budget fuers Denken draufginge."""
    modelle = await llm.models()
    qwen = next((m for m in modelle if m.id.startswith("qwen3") and m.is_ready), None)
    if qwen is None:
        pytest.skip("kein bereites qwen3-Modell")
    antwort = await llm.chat("Nenne die Hauptstadt von Frankreich.",
                             model=qwen.id, max_tokens=100)
    assert antwort.strip(), "leere Antwort trotz abgeschaltetem Denken"


async def test_unbekanntes_modell_wird_klar_gemeldet(llm):
    """Statt still auf ein anderes Modell auszuweichen."""
    with pytest.raises(EduSharingError):
        await llm.chat("hallo", model="gibt-es-nicht-2099", max_tokens=10)


async def test_fremder_provider_wird_abgelehnt(llm):
    """Gemessen: 400 'Provider ... not found'. Es gibt genau zwei."""
    with pytest.raises(EduSharingError):
        await llm.models(provider="gwdg")


# --- Die durchgereichten OpenAI-Routen -------------------------------------

async def test_einbettungen_kommen_vom_anbieter(llm):
    """Gemessen am 28.08.2026: academiccloud fuehrt kein Einbettungsmodell,
    openai schon. Deshalb hier ausdruecklich der Anbieter -- geraten wird
    nichts."""
    vektoren = await llm.embeddings(
        ["Photosynthese", "Zellatmung"],
        model="text-embedding-3-small", provider="openai")
    assert len(vektoren) == 2, f"zwei Texte, {len(vektoren)} Vektoren"
    assert all(len(v) > 100 for v in vektoren), "verdaechtig kurze Vektoren"
    assert vektoren[0] != vektoren[1], "zwei Texte, derselbe Vektor"


async def test_moderation_urteilt(llm):
    urteil = await llm.moderate(
        "Ein voellig harmloser Satz ueber Blumen.",
        model="omni-moderation-latest", provider="openai")
    assert urteil.flagged is False, f"harmloser Satz geflaggt: {urteil.categories}"
    assert urteil.scores, "keine Punktwerte zurueckbekommen"


async def test_rerank_wird_nicht_durchgereicht(llm):
    """Die eine Route, die das Gateway ablehnt -- gemessen mit derselben
    Antwort wie fuer eine frei erfundene Route. Faellt das weg, ist die
    Positivliste gewachsen und passthrough.__doc__ veraltet."""
    from edusharing.errors import EduSharingError

    with pytest.raises(EduSharingError) as fehler:
        await llm.call("rerank", {"model": "x"}, provider="openai")
    assert "403" in str(fehler.value), str(fehler.value)[:120]


# --- responses -------------------------------------------------------------
#
# Beide Anbieter koennen den Endpunkt. Der Test prueft das gegen beide, weil
# genau diese Annahme falsch war, bevor sie gemessen wurde.

@pytest.mark.live
@pytest.mark.parametrize("provider, modell", [
    ("openai", "gpt-5.6-luna"),
    ("academiccloud", "gemma-4-31b-it"),
])
async def test_responses_antwortet_bei_beiden_anbietern(llm, provider, modell):
    antwort = await llm.respond(
        "Nenne die Hauptstadt von Frankreich, in drei Woertern.",
        model=modell, provider=provider, max_output_tokens=300)
    assert antwort.status == "completed", antwort.raw.get("incomplete_details")
    assert antwort.truncated is False
    assert "aris" in antwort.text, antwort.text
    assert antwort.model


@pytest.mark.live
async def test_ein_zu_kleines_budget_meldet_sich_als_abgeschnitten(llm):
    """Der Fall, den ein blosser Text verschweigen wuerde.

    qwen3.5 denkt, und das Denken zahlt aus demselben Budget: gemessen am
    31.08.2026 gingen 32 Tokens vollstaendig in den Denkprozess.
    """
    antwort = await llm.respond("Warum ist der Himmel blau?",
                                model="qwen3.5-122b-a10b",
                                provider="academiccloud", max_output_tokens=32)
    assert antwort.truncated is True
    assert antwort.reason == "max_output_tokens"


# --- Der Auslastungsbericht ------------------------------------------------

@pytest.mark.live
async def test_die_academiccloud_meldet_auslastung(llm):
    bericht = await llm.load("academiccloud")
    assert bericht.reports_load is True
    assert bericht.models, bericht.summary()
    # Am wenigsten ausgelastet zuerst -- monoton steigend.
    lasten = [m.demand for m in bericht.models if m.demand is not None]
    assert lasten == sorted(lasten), bericht.summary()


@pytest.mark.live
async def test_openai_meldet_keine_auslastung_und_sagt_das(llm):
    """Der Grund, warum ``reports_load`` existiert.

    Ohne das Feld waere die Rangfolge dort alphabetisch, und wer sie als
    Aussage ueber Warteschlangen liest, irrt.
    """
    bericht = await llm.load("openai")
    assert bericht.reports_load is False
    assert bericht.total > 100, bericht.total
    assert all(m.demand is None for m in bericht.models)


@pytest.mark.live
async def test_openai_meldet_abgekuendigte_modelle(llm):
    """Gemessen am 31.08.2026: 57 von 132 tragen ein shutdown_date."""
    bericht = await llm.load("openai", on=date(2026, 12, 31))
    assert bericht.retired, "kein einziges abgekuendigtes Modell gefunden"
