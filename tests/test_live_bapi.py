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

    Das Denken zahlt aus demselben Budget: gemessen am 31.08.2026 gingen 32
    Tokens vollstaendig in den Denkprozess, und ``truncated`` ist das einzige,
    was eine abgebrochene Antwort von einer fertigen unterscheidet.

    Das Modell wird aus der Liste des Anbieters genommen, nicht genannt. Hier
    stand ``qwen3.5-122b-a10b``; am 21.09.2026 fuehrt die AcademicCloud den
    Namen nicht mehr, und das Gateway antwortet auf ihn mit 503 ``Model
    pricing unavailable``. Von den 14 angebotenen Modellen melden 12 bei 32
    Tokens genau diesen Zustand, zwei sind aus eigenen Gruenden nicht
    bedienbar (``apertus-70b-instruct-2509`` ebenfalls 503 Pricing,
    ``qwen3-omni-30b-a3b-instruct`` 400 zu seinem Chat-Template). Darum wird
    der Reihe nach probiert: ein umbenanntes Modell ist kein Testergebnis,
    ein Anbieter, von dem keines antwortet, sehr wohl.
    """
    modelle = await llm.models("academiccloud")
    assert modelle, "der Anbieter meldet kein einziges Modell"

    abgewiesen = []
    for m in modelle:
        try:
            antwort = await llm.respond("Warum ist der Himmel blau?",
                                        model=m.id, provider="academiccloud",
                                        max_output_tokens=32)
        except EduSharingError as fehler:
            abgewiesen.append(f"{m.id}: {type(fehler).__name__}")
            continue
        assert antwort.truncated is True, (
            f"{m.id} beantwortete die Frage in 32 Tokens: {antwort.text!r}"
        )
        assert antwort.reason == "max_output_tokens", f"{m.id}: {antwort.reason}"
        return

    pytest.fail("kein Modell der AcademicCloud antwortete -- "
                + "; ".join(abgewiesen))


# --- Die GPT-5-Umstellung, gegen den Server --------------------------------
#
# ``build_body`` baut die Koerper, und ``test_bapi_body.py`` haelt fest, wie.
# Ob der Server sie noch verlangt, kann nur ein Lauf sagen: der Sprung von der
# gpt-4- auf die gpt-5-Familie hat hier dreimal die Regel geaendert, und eine
# zurueckgenommene Regel wuerde einem Test auf die eigene Koerperform nie
# auffallen -- der bliebe gruen, waehrend die Bibliothek Ballast mitschleppt.


@pytest.fixture
async def gpt5(llm):
    """Ein Modell der GPT-5-Familie beim Anbieter openai.

    ``gpt-5.6-luna``, solange es angeboten wird -- die Messungen dieser Datei
    stammen von ihm. Sonst das erste andere der Familie: die drei Regeln
    gelten der Familie, nicht dem einen Namen, und ein zurueckgezogener Name
    ist kein Testergebnis (siehe ``qwen3.5-122b-a10b``).
    """
    ids = [m.id for m in await llm.models("openai")]
    if "gpt-5.6-luna" in ids:
        return "gpt-5.6-luna"
    familie = [i for i in ids if i.startswith("gpt-5")]
    if not familie:
        pytest.skip("openai bietet kein Modell der GPT-5-Familie an")
    return familie[0]


@pytest.mark.live
async def test_gpt5_nimmt_den_koerper_der_bibliothek(llm, gpt5):
    """Die Gegenprobe zu den drei Abweisungen unten: was die Bibliothek baut,
    nimmt der Server an -- ueber beide Routen."""
    antwort = await llm.chat("Antworte mit genau einem Wort: Hallo.",
                             model=gpt5, provider="openai", max_tokens=50)
    assert antwort.strip(), "leere Antwort auf chat/completions"

    ueber_responses = await llm.respond(
        "Nenne die Hauptstadt von Frankreich, in drei Woertern.",
        model=gpt5, provider="openai", max_output_tokens=300)
    assert ueber_responses.status == "completed", ueber_responses.reason
    assert "aris" in ueber_responses.text, ueber_responses.text


@pytest.mark.live
@pytest.mark.parametrize("route, koerper, erwartet", [
    # Gemessen 21.09.2026: "Unsupported parameter: 'max_tokens' is not
    # supported with this model. Use 'max_completion_tokens' instead."
    ("chat/completions",
     {"messages": [{"role": "user", "content": "Hallo"}], "max_tokens": 50},
     "max_completion_tokens"),
    # "Unsupported value: 'temperature' does not support 0.0 with this model.
    # Only the default (1) value is supported."
    ("chat/completions",
     {"messages": [{"role": "user", "content": "Hallo"}],
      "max_completion_tokens": 50, "temperature": 0.0},
     "temperature"),
    # "Unsupported parameter: 'reasoning_effort'. In the Responses API, this
    # parameter has moved to 'reasoning.effort'."
    ("responses",
     {"input": "Hallo", "max_output_tokens": 300, "reasoning_effort": "low"},
     "reasoning.effort"),
])
async def test_gpt5_weist_die_vor_gpt5_schreibweise_ab(llm, gpt5, route, koerper,
                                                       erwartet):
    """Die drei Abweisungen, aus denen die Regeln in ``body`` bestehen.

    Wird eine davon eines Tages angenommen, ist dieser Test rot -- und dann
    traegt die Bibliothek eine Sonderbehandlung, die niemand mehr braucht.
    Das ist der einzige Weg, das zu bemerken.
    """
    with pytest.raises(EduSharingError) as fehler:
        await llm.call(route, {"model": gpt5, **koerper}, provider="openai")
    assert erwartet in str(fehler.value), str(fehler.value)[:200]


@pytest.mark.live
async def test_die_alte_completions_route_weist_die_gpt5_familie_ab(llm, gpt5):
    """Die alte Route gibt es noch -- die neue Familie gehoert nicht hinein.

    Gemessen am 21.09.2026: ``completions`` mit ``gpt-5.6-luna`` antwortet
    404 *"This is a chat model and not supported in the v1/completions
    endpoint"*. Die Bibliothek reicht ``completions`` durch, ohne einen
    Koerper je Familie zu bauen -- hier ist das richtig, denn es gibt keinen
    Koerper, der das heilen wuerde. Wer die Route fuer ein gpt-5-Modell nimmt,
    soll die Antwort des Servers lesen statt zu raten, und dass sie noch so
    lautet, sagt nur ein Lauf.
    """
    with pytest.raises(EduSharingError) as fehler:
        await llm.call("completions",
                       {"model": gpt5, "prompt": "hallo", "max_tokens": 5},
                       provider="openai")
    assert "chat model" in str(fehler.value), str(fehler.value)[:200]


@pytest.mark.live
async def test_respond_weicht_auf_den_naechsten_kandidaten_aus(llm, gpt5):
    """``respond`` hatte die Modellpolitik von ``chat`` nicht -- ohne Grund.

    Gemessen am 21.09.2026: ``tts-1`` steht in der Modellliste von openai und
    wird nicht bedient (503 ``Model pricing unavailable``). Vorher endete
    ``respond`` genau dort, denn es nahm die eine ID, die es bekam. Jetzt teilt
    es die Politik: naechster Kandidat, und die Antwort kommt.

    Der Fall ist mit Absicht ueber die echte Liste gewaehlt und nicht erfunden
    -- er ist der, der einem Aufrufer hier tatsaechlich begegnet.
    """
    antwort = await llm.respond(
        "Nenne die Hauptstadt von Frankreich, in drei Woertern.",
        model=["tts-1", gpt5], provider="openai", max_output_tokens=300)
    assert antwort.status == "completed", antwort.reason
    assert "aris" in antwort.text, antwort.text
    assert llm.last_model == gpt5, llm.last_model


# --- Die Routen mit einer Datei -------------------------------------------


def _uebersprungen_wenn_unbepreist(fehler: EduSharingError, modell: str) -> None:
    """Ein Modell, das das Gateway nicht abrechnen kann, ist kein Befund ueber
    diese Bibliothek. Gemessen am 21.09.2026 traf das ``tts-1``, ``whisper-1``
    und ``gpt-transcribe``; ``gpt-4o-mini-tts`` und ``gpt-4o-mini-transcribe``
    wurden bedient. Kippt das, soll der Test das sagen und nicht so tun, als
    waere der Dateiweg kaputt."""
    if "pricing unavailable" in str(fehler).lower():
        pytest.skip(f"{modell} wird vom Gateway nicht abgerechnet")
    raise fehler


@pytest.mark.live
async def test_eine_datei_geht_durch_die_bibliothek(llm):
    """Der Weg, den es vorher nicht gab.

    Vier weitergeleitete Routen nehmen eine Datei statt eines JSON-Koerpers,
    und ``call`` erreichte keine davon. Nicht, weil das Gateway sie
    verweigerte: gemessen am 21.09.2026 antwortet ``audio/transcriptions`` mit
    ``gpt-4o-mini-transcribe`` auf einen JSON-Koerper
    ``400 {'loc': ('body', 'file'), 'msg': 'Field required'}`` -- das Modell
    wird bedient, es fehlte allein die Datei.

    Die Probe erzeugt sich ihre Datei selbst: ``audio/speech`` spricht ein
    Wort, ``audio/transcriptions`` liest es zurueck. Damit liegt kein
    Testdatensatz im Repositorium, und beide Richtungen sind in einem Lauf
    belegt -- die eine ueber ``call_bytes``, fuer die es bisher ueberhaupt
    keinen Live-Test gab, die andere ueber ``call_multipart``.
    """
    try:
        gesprochen = await llm.call_bytes(
            "audio/speech",
            {"model": "gpt-4o-mini-tts", "voice": "alloy",
             "input": "Die Hauptstadt von Deutschland ist Berlin."},
            provider="openai")
    except EduSharingError as fehler:
        _uebersprungen_wenn_unbepreist(fehler, "gpt-4o-mini-tts")

    assert len(gesprochen) > 1000, f"nur {len(gesprochen)} Bytes"

    try:
        zurueck = await llm.call_multipart(
            "audio/transcriptions", {"model": "gpt-4o-mini-transcribe"},
            file=gesprochen, filename="probe.mp3", content_type="audio/mpeg",
            provider="openai")
    except EduSharingError as fehler:
        _uebersprungen_wenn_unbepreist(fehler, "gpt-4o-mini-transcribe")

    # Ein ganzer Satz mit Absicht. Gemessen am 21.09.2026 kam das einzelne
    # Wort "Berlin." als "柏林" zurueck -- richtig, aber auf
    # Chinesisch: ein Eigenname ohne Kontext ist mehrdeutig. Und ein
    # ``language``-Feld half nicht, weder mit "de" noch mit "zh"; beide
    # lieferten denselben deutschen Satz. Es steht darum nicht hier, damit
    # niemand es fuer wirksam haelt.
    assert "Berlin" in zurueck.get("text", ""), zurueck


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
