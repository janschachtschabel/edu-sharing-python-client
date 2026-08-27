"""Der b-api-Client.

Die b-api ist das LLM-Gateway von OpenEduHub. Gemessen (Staging): Auth per
``X-API-KEY``, zwei Provider, keine Quoten-Header, kein ``retry-after`` bei
429 -- ein Client sieht sein Restkontingent also nicht und merkt das Limit
erst am Fehler.
"""

import asyncio
import json

import httpx
import pytest

from edusharing.bapi import BildungsAPI
from edusharing.errors import EduSharingError

MODELLE = {"data": [
    {"id": "glm-4.7", "demand": 2, "status": "ready", "input": ["text"], "output": ["text"]},
    {"id": "qwen3.6-35b-a3b", "demand": 0, "status": "ready",
     "input": ["text"], "output": ["text"]},
    {"id": "embed-x", "demand": 0, "status": "ready",
     "input": ["text"], "output": ["embedding"]},
]}
ANTWORT = {"choices": [{"message": {"content": "Die Antwort"}}],
           "usage": {"total_tokens": 42}}


def _client(handler, aufrufe=None, **kwargs):
    def wrapped(request):
        if aufrufe is not None:
            aufrufe.append(request)
        return handler(request)

    kwargs.setdefault("api_key", "geheimer-schluessel")
    kwargs.setdefault("backoff_base", 0.0)
    kwargs.setdefault("models_cache_seconds", 0)
    return BildungsAPI(
        client=httpx.AsyncClient(transport=httpx.MockTransport(wrapped)), **kwargs)


def _router(request):
    if request.url.path.endswith("/models"):
        return httpx.Response(200, json=MODELLE)
    return httpx.Response(200, json=ANTWORT)


# --- Auth ------------------------------------------------------------------

async def test_schluessel_geht_als_x_api_key():
    """Gemessen: die b-api verlangt X-API-KEY. Ein Authorization-Bearer
    ergibt 401 -- dieselbe Falle wie bei edu-sharing, nur andersherum."""
    aufrufe = []
    async with _client(_router, aufrufe) as api:
        await api.models()
    assert aufrufe[0].headers.get("x-api-key") == "geheimer-schluessel"
    assert "authorization" not in aufrufe[0].headers


async def test_schluessel_steht_nicht_im_repr():
    async with _client(_router) as api:
        assert "geheimer-schluessel" not in repr(api)


def test_fehlender_schluessel_wird_beim_bauen_gemeldet():
    with pytest.raises(EduSharingError, match="B_API_KEY"):
        BildungsAPI(api_key="")


def test_from_env_ohne_schluessel(monkeypatch):
    monkeypatch.delenv("B_API_KEY", raising=False)
    with pytest.raises(EduSharingError, match="B_API_KEY"):
        BildungsAPI.from_env()


# --- Modelle ---------------------------------------------------------------

async def test_modelle_werden_gelesen():
    async with _client(_router) as api:
        modelle = await api.models()
    assert {m.id for m in modelle} == {"glm-4.7", "qwen3.6-35b-a3b", "embed-x"}
    assert next(m for m in modelle if m.id == "glm-4.7").demand == 2


async def test_modellliste_wird_kurz_zwischengespeichert():
    """demand schwankt im Minutentakt -- ein langer Cache wuerde die Wahl auf
    veralteten Zahlen treffen. Ganz ohne Cache kostet jeder Aufruf eine
    zusaetzliche Anfrage."""
    aufrufe = []
    async with _client(_router, aufrufe, models_cache_seconds=60) as api:
        await api.models()
        await api.models()
    assert len([r for r in aufrufe if r.url.path.endswith("/models")]) == 1


async def test_cache_laesst_sich_abschalten():
    aufrufe = []
    async with _client(_router, aufrufe, models_cache_seconds=0) as api:
        await api.models()
        await api.models()
    assert len([r for r in aufrufe if r.url.path.endswith("/models")]) == 2


# --- Chat ------------------------------------------------------------------

async def test_chat_mit_einfachem_text():
    aufrufe = []
    async with _client(_router, aufrufe) as api:
        antwort = await api.chat("Was ist Photosynthese?")
    assert antwort == "Die Antwort"
    body = json.loads(next(r for r in aufrufe if "completions" in r.url.path).content)
    assert body["messages"] == [{"role": "user", "content": "Was ist Photosynthese?"}]


async def test_chat_waehlt_das_am_wenigsten_ausgelastete_modell():
    aufrufe = []
    async with _client(_router, aufrufe) as api:
        await api.chat("hallo")
    body = json.loads(next(r for r in aufrufe if "completions" in r.url.path).content)
    assert body["model"] == "qwen3.6-35b-a3b"


async def test_festes_modell_spart_die_modellabfrage():
    aufrufe = []
    async with _client(_router, aufrufe) as api:
        await api.chat("hallo", model="glm-4.7")
    assert not any(r.url.path.endswith("/models") for r in aufrufe)


async def test_eigene_nachrichtenliste():
    aufrufe = []
    nachrichten = [{"role": "system", "content": "Du bist knapp."},
                   {"role": "user", "content": "hallo"}]
    async with _client(_router, aufrufe) as api:
        await api.chat(nachrichten, model="glm-4.7")
    body = json.loads(next(r for r in aufrufe if "completions" in r.url.path).content)
    assert body["messages"] == nachrichten


async def test_provider_ist_waehlbar():
    aufrufe = []
    async with _client(_router, aufrufe, provider="openai") as api:
        await api.models()
    assert "/llm/openai/models" in str(aufrufe[0].url)


# --- Fehler und Wiederholung ----------------------------------------------

@pytest.mark.parametrize("status", [429, 502, 503, 504])
async def test_voruebergehende_fehler_werden_wiederholt(status):
    """429 kommt ohne retry-after -- moeglich ist nur exponentielles Warten."""
    versuche = []

    def handler(request):
        versuche.append(request)
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json=MODELLE)
        if len([r for r in versuche if "completions" in r.url.path]) < 3:
            return httpx.Response(status, json={"message": "gerade nicht"})
        return httpx.Response(200, json=ANTWORT)

    async with _client(handler, max_retries=3) as api:
        assert await api.chat("hallo", model="glm-4.7") == "Die Antwort"


async def test_dauerhafte_fehler_werden_nicht_wiederholt():
    """400 'not a chat model' wird beim vierten Versuch nicht besser."""
    versuche = []

    def handler(request):
        versuche.append(request)
        return httpx.Response(404, json={"message": "This is not a chat model"})

    async with _client(handler, max_retries=3) as api:
        with pytest.raises(EduSharingError):
            await api.chat("hallo", model="embed-x")
    assert len(versuche) == 1


async def test_fehlermeldung_nennt_die_ursache():
    def handler(request):
        return httpx.Response(400, json={"message": "use max_completion_tokens instead"})

    async with _client(handler) as api:
        with pytest.raises(EduSharingError, match="max_completion_tokens"):
            await api.chat("hallo", model="gpt-5.6-luna")


# --- Gleichzeitigkeit ------------------------------------------------------

async def test_gleichzeitigkeit_ist_begrenzt():
    """Gemessen: ab etwa 19 gleichzeitigen Anfragen kommen 502er, bei 28 bricht
    es ab. Die Grenze ist nicht stabil und gehoert nachgemessen -- aber
    unbegrenzt ist sicher falsch."""
    laufend = 0
    hoechststand = 0

    async def handler(request):
        nonlocal laufend, hoechststand
        laufend += 1
        hoechststand = max(hoechststand, laufend)
        await asyncio.sleep(0.01)
        laufend -= 1
        return httpx.Response(200, json=ANTWORT)

    async with _client(handler, max_concurrency=3) as api:
        await asyncio.gather(*(api.chat("x", model="glm-4.7") for _ in range(12)))
    assert hoechststand <= 3


# --- Wenn ein "bereites" Modell doch nicht antwortet ----------------------

async def test_automatische_wahl_weicht_auf_das_naechste_modell_aus():
    """Gemessen: apertus-70b-instruct-2509 meldet status 'ready' und demand 0,
    antwortet aber mit 503 'Model pricing unavailable ... cannot enforce cost
    quota'. status allein taugt also nicht als Auswahlkriterium, und die
    Untauglichkeit steht in keiner Modellliste.

    Wer die Wahl der Bibliothek ueberlassen hat, will eine Antwort -- nicht
    den Hinweis, dass ausgerechnet das erste Modell gerade nicht abrechenbar
    ist.
    """
    versuche = []

    def handler(request):
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json=MODELLE)
        body = json.loads(request.content)
        versuche.append(body["model"])
        if body["model"] == "qwen3.6-35b-a3b":     # das am wenigsten ausgelastete
            return httpx.Response(503, json={"message": "Model pricing unavailable"})
        return httpx.Response(200, json=ANTWORT)

    async with _client(handler, max_retries=0) as api:
        assert await api.chat("hallo") == "Die Antwort"
    assert versuche == ["qwen3.6-35b-a3b", "glm-4.7"], versuche


async def test_festes_modell_weicht_nicht_aus():
    """Wer ein Modell nennt, will dessen Antwort -- eine vom Nachbarmodell
    waere ein stiller Austausch."""
    versuche = []

    def handler(request):
        versuche.append(json.loads(request.content)["model"])
        return httpx.Response(503, json={"message": "Model pricing unavailable"})

    async with _client(handler, max_retries=0) as api:
        with pytest.raises(EduSharingError):
            await api.chat("hallo", model="glm-4.7")
    assert versuche == ["glm-4.7"]


async def test_wenn_alle_modelle_scheitern_wird_das_gesagt():
    def handler(request):
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json=MODELLE)
        return httpx.Response(503, json={"message": "Model pricing unavailable"})

    async with _client(handler, max_retries=0) as api:
        with pytest.raises(EduSharingError, match="None of the models"):
            await api.chat("hallo")


async def test_gewaehltes_modell_ist_ablesbar():
    """Sonst weiss der Aufrufer nicht, wessen Antwort er gerade liest."""
    async with _client(_router) as api:
        await api.chat("hallo")
        assert api.last_model == "qwen3.6-35b-a3b"
