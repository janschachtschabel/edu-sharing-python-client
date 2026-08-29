"""Tests gegen die echte b-api.

    B_API_KEY=... uv run pytest -m live

Beantworten die Frage, die Mocks nicht beantworten koennen: stimmen die
Modell-IDs und die Request-Eigenheiten noch? Beide aendern sich ohne
Ankuendigung -- aus deepseek-v4-flash wurde binnen neun Tagen
deepseek-v4-flash-0731, der alte Name antwortet seither mit 503.
"""

import os

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
