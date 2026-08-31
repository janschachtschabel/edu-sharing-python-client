"""Der b-api-Client.

Die b-api ist das LLM-Gateway von OpenEduHub. Gemessen (Staging): Auth per
``X-API-KEY``, zwei Provider, keine Quoten-Header, kein ``retry-after`` bei
429 -- ein Client sieht sein Restkontingent also nicht und merkt das Limit
erst am Fehler.
"""

import asyncio
import json
from datetime import date

import httpx
import pytest

from edusharing.bapi import CACHE_FOREVER, BildungsAPI
from edusharing.errors import EduSharingError

#: Frei erfunden. Die Tests antworten ueber MockTransport; eine echte
#: Adresse hier waere eine Instanz im Code.
GATEWAY = "https://gateway.example.test"

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
    kwargs.setdefault("base_url", GATEWAY)
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
        BildungsAPI(api_key="", base_url=GATEWAY)


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


# --- Parametervalidierung -------------------------------------------------
#
# Audit-Befund F2/F3 vom 27.08.2026: der b-api-Client nahm jeden Parameter
# ungeprueft, waehrend der Transport vier davon prueft. max_retries=-1 liess die
# Retry-Schleife nie laufen und endete in einem "assert last is not None" --
# unter "python -O" wird daraus ein "raise None" und damit ein TypeError statt
# der eigentlichen Fehlermeldung.

@pytest.mark.parametrize("kwargs", [
    {"max_retries": -1},
    {"max_concurrency": 0},
    {"timeout": 0},
    {"backoff_base": -1},
    {"models_cache_seconds": -1},
])
def test_unsinnige_parameter_werden_sofort_abgelehnt(kwargs):
    """Frueh und laut statt spaet und raetselhaft -- dieselbe Regel, nach der
    sich der Transport richtet."""
    with pytest.raises(EduSharingError) as fehler:
        BildungsAPI(api_key="k", base_url=GATEWAY, **kwargs)
    # Die Meldung muss den Parameter benennen, sonst hilft sie nicht.
    assert next(iter(kwargs)) in str(fehler.value)


def test_gueltige_grenzwerte_bleiben_erlaubt():
    """Gegenprobe: 0 Wiederholungen und 0 Sekunden Cache sind sinnvoll."""
    api = BildungsAPI(api_key="k", base_url=GATEWAY, max_retries=0,
                      backoff_base=0,
                      models_cache_seconds=0, max_concurrency=1)
    assert api.max_retries == 0


async def test_modellwechsel_wird_gemeldet(caplog):
    """Audit-Befund F5: bei automatischer Wahl sagte nur last_model, wessen
    Antwort man liest -- warum die vorherigen Kandidaten ausfielen, stand
    nirgends. Genau das braucht man nach einem Zwischenfall.
    """
    import logging

    caplog.set_level(logging.INFO, logger="edusharing")

    def handler(request):
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json=MODELLE)
        if json.loads(request.content)["model"] == "qwen3.6-35b-a3b":
            return httpx.Response(503, json={"message": "Model pricing unavailable"})
        return httpx.Response(200, json=ANTWORT)

    async with _client(handler) as api:
        await api.chat("hallo")

    meldungen = [r.getMessage() for r in caplog.records]
    assert any("qwen3.6-35b-a3b" in m for m in meldungen), meldungen
    # Der Schluessel gehoert niemals hinein.
    assert "geheimer-schluessel" not in "\n".join(meldungen)


def test_ohne_adresse_wird_verweigert(monkeypatch):
    """Kein Vorgabewert fuer das Gateway -- wie beim Extraktionsdienst.

    Bis zum 28.08.2026 stand hier ``https://b-api.staging.openeduhub.net`` als
    Standard. Wer ``B_API_KEY`` setzte und sonst nichts, schickte seinen
    Schluessel damit an eine fremde **Staging**-Instanz, ohne sie gewaehlt zu
    haben. Das Schwestermodul ``extraction`` verweigert genau das seit jeher mit
    derselben Begruendung; die beiden Dienste widersprachen sich im selben
    Projekt.
    """
    monkeypatch.setenv("B_API_KEY", "irgendein-schluessel")
    monkeypatch.delenv("B_API_BASE_URL", raising=False)
    with pytest.raises(EduSharingError) as fehler:
        BildungsAPI.from_env()
    assert "B_API_BASE_URL" in str(fehler.value)


def test_mit_adresse_aus_der_umgebung_geht_es(monkeypatch):
    monkeypatch.setenv("B_API_KEY", "irgendein-schluessel")
    monkeypatch.setenv("B_API_BASE_URL", "https://gateway.example.test")
    llm = BildungsAPI.from_env()
    assert llm.base_url == "https://gateway.example.test"


# --- reasoning_effort und verbosity durchreichen ---------------------------

async def test_chat_setzt_die_vorgabe_low_bei_einem_reasoning_modell():
    aufrufe = []
    async with _client(_router, aufrufe) as api:
        await api.chat("x", model="gpt-5.6-luna", provider="openai")
    koerper = json.loads(aufrufe[-1].content)
    assert koerper["reasoning_effort"] == "low"
    assert koerper["verbosity"] == "low"


async def test_chat_laesst_sie_weg_wo_das_modell_sie_nicht_kennt():
    aufrufe = []
    async with _client(_router, aufrufe) as api:
        await api.chat("x", model="gpt-4o-mini", provider="openai")
    koerper = json.loads(aufrufe[-1].content)
    assert "reasoning_effort" not in koerper
    assert "verbosity" not in koerper


async def test_chat_reicht_einen_ausdruecklichen_wert_durch():
    aufrufe = []
    async with _client(_router, aufrufe) as api:
        await api.chat("x", model="gpt-5.6-luna", provider="openai",
                       reasoning_effort="high")
    assert json.loads(aufrufe[-1].content)["reasoning_effort"] == "high"


async def test_chat_verwirft_einen_ausdruecklichen_wunsch_nicht_still():
    async with _client(_router) as api:
        with pytest.raises(ValueError) as info:
            await api.chat("x", model="gpt-4o-mini", provider="openai",
                           reasoning_effort="high")
    assert "gpt-4o-mini" in str(info.value)


# --- Virtuelles Modell -----------------------------------------------------
#
# Der Aufrufer nennt zwei oder drei Modelle, die alle taugen wuerden; die
# Bibliothek nimmt daraus das am wenigsten ausgelastete. In MODELLE oben hat
# qwen3.6-35b-a3b demand=0 und glm-4.7 demand=2.

async def test_liste_waehlt_das_am_wenigsten_ausgelastete():
    aufrufe = []
    async with _client(_router, aufrufe) as api:
        await api.chat("x", model=["glm-4.7", "qwen3.6-35b-a3b"])
    assert json.loads(aufrufe[-1].content)["model"] == "qwen3.6-35b-a3b"


async def test_benannter_verbund_wird_aufgeloest():
    aufrufe = []
    async with _client(_router, aufrufe,
                       virtual_models={"schnell": ["glm-4.7", "qwen3.6-35b-a3b"]}) as api:
        await api.chat("x", model="schnell")
    assert json.loads(aufrufe[-1].content)["model"] == "qwen3.6-35b-a3b"


async def test_ein_verbundname_der_wie_ein_echtes_modell_heisst_faellt_auf():
    """Sonst haengt es vom Nachschlagen ab, welches von beiden gemeint war."""
    async with _client(_router,
                       virtual_models={"glm-4.7": ["qwen3.6-35b-a3b"]}) as api:
        with pytest.raises(EduSharingError) as info:
            await api.chat("x", model="glm-4.7")
    assert "glm-4.7" in str(info.value)


async def test_faellt_das_erste_modell_aus_kommt_das_zweite_dran():
    """Genau dafuer nennt man mehrere."""
    aufrufe = []

    def handler(request):
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json=MODELLE)
        if b"qwen3.6-35b-a3b" in request.content:
            return httpx.Response(503, json={"error": "Model pricing unavailable"})
        return httpx.Response(200, json=ANTWORT)

    async with _client(handler, aufrufe) as api:
        antwort = await api.chat("x", model=["qwen3.6-35b-a3b", "glm-4.7"])
    assert antwort == "Die Antwort"

    # Der Reihe nach, ohne die Wiederholungen: ein 503 ist wiederholbar, also
    # versucht der Transport dasselbe Modell erst mehrfach. Fuer einen Verbund
    # ist das nicht ideal -- wechseln waere billiger als warten -- aber es ist
    # bestehendes Verhalten und gehoert nicht in diese Aenderung.
    gefragt = [json.loads(r.content)["model"] for r in aufrufe
               if not r.url.path.endswith("/models")]
    ohne_wiederholung = [m for i, m in enumerate(gefragt)
                         if i == 0 or m != gefragt[i - 1]]
    assert ohne_wiederholung == ["qwen3.6-35b-a3b", "glm-4.7"]


async def test_ein_unbekannter_name_im_verbund_wird_gemeldet():
    async with _client(_router) as api:
        with pytest.raises(EduSharingError) as info:
            await api.chat("x", model=["glm-4.7", "gibt-es-nicht"])
    assert "gibt-es-nicht" in str(info.value)


# --- Wann die Auslastung abgefragt wird ------------------------------------
#
# ``demand`` bewegt sich im Minutentakt, also ist die Vorgabe ein kurzer Cache
# (30 s). Wer ein kurzes Skript schreibt, will die Zahlen genau einmal holen;
# wer einen langlaufenden Dienst schreibt, will sie nicht veralten lassen. Das
# ist dieselbe Stellschraube, nur anders gestellt.

async def test_cache_forever_fragt_die_modelle_genau_einmal():
    aufrufe = []
    async with _client(_router, aufrufe,
                       models_cache_seconds=CACHE_FOREVER) as api:
        await api.models()
        await api.models()
        await api.models()
    assert sum(1 for r in aufrufe if r.url.path.endswith("/models")) == 1


async def test_ohne_cache_wird_jedes_mal_gefragt():
    aufrufe = []
    async with _client(_router, aufrufe, models_cache_seconds=0) as api:
        await api.models()
        await api.models()
    assert sum(1 for r in aufrufe if r.url.path.endswith("/models")) == 2


# --- Der Auslastungsbericht ------------------------------------------------

async def test_load_meldet_die_modelle_am_wenigsten_ausgelastet_zuerst():
    async with _client(_router) as api:
        bericht = await api.load()
    assert [m.id for m in bericht.models] == ["qwen3.6-35b-a3b", "glm-4.7"]
    assert bericht.least_loaded is not None
    assert bericht.least_loaded.id == "qwen3.6-35b-a3b"
    assert bericht.reports_load is True


async def test_load_sagt_wenn_es_gar_keine_auslastung_gibt():
    """Bei OpenAI ist ``demand`` nicht vorhanden -- dann ist der ganze Bericht
    fuer die Lastfrage wertlos, und das muss dastehen."""
    ohne = {"data": [{"id": "gpt-5.6-luna"}, {"id": "gpt-4o-mini"}]}

    def handler(request):
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json=ohne)
        return httpx.Response(200, json=ANTWORT)

    async with _client(handler) as api:
        bericht = await api.load()
    assert bericht.reports_load is False
    assert "gpt-5.6-luna" in bericht.summary()


async def test_der_bericht_nennt_abgekuendigte_modelle():
    mit_datum = {"data": [{"id": "gpt-4", "shutdown_date": "2026-01-01"}]}

    def handler(request):
        return httpx.Response(200, json=mit_datum)

    async with _client(handler) as api:
        bericht = await api.load(on=date(2026, 6, 1))
    assert bericht.retired == ("gpt-4",)
    assert "gpt-4" in bericht.summary()


# --- Wiederholen oder wechseln ---------------------------------------------
#
# Ein 503 ist wiederholbar, also versuchte der Transport dasselbe ausgelastete
# Modell dreimal, bevor er wechselte -- bei backoff_base 2.5 rund 17 s, obwohl
# ein anderes Modell danebenstand. Wer mehrere Modelle nennt, will wechseln.

def _immer_503(aufrufe):
    def handler(request):
        aufrufe.append(request)
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json=MODELLE)
        return httpx.Response(503, json={"error": "Model pricing unavailable"})
    return handler


def _versuche_je_modell(aufrufe):
    from collections import Counter
    return Counter(json.loads(r.content)["model"] for r in aufrufe
                   if not r.url.path.endswith("/models"))


async def test_ein_kandidat_wird_einmal_wiederholt_dann_gewechselt():
    aufrufe = []
    async with _client(_immer_503(aufrufe), max_retries=3) as api:
        with pytest.raises(EduSharingError):
            await api.chat("x", model=["qwen3.6-35b-a3b", "glm-4.7"])
    zaehler = _versuche_je_modell(aufrufe)
    # Der erste: ein Versuch plus eine Wiederholung.
    assert zaehler["qwen3.6-35b-a3b"] == 2
    # Der letzte: das volle Budget, denn danach kommt nichts mehr.
    assert zaehler["glm-4.7"] == 4


async def test_das_budget_je_kandidat_ist_einstellbar():
    aufrufe = []
    async with _client(_immer_503(aufrufe), max_retries=3,
                       retries_before_switching=0) as api:
        with pytest.raises(EduSharingError):
            await api.chat("x", model=["qwen3.6-35b-a3b", "glm-4.7"])
    assert _versuche_je_modell(aufrufe)["qwen3.6-35b-a3b"] == 1


async def test_ein_einzelnes_modell_behaelt_das_volle_budget():
    """Ohne Alternative gibt es nichts zu wechseln -- warten ist alles."""
    aufrufe = []
    async with _client(_immer_503(aufrufe), max_retries=2) as api:
        with pytest.raises(EduSharingError):
            await api.chat("x", model="glm-4.7")
    assert _versuche_je_modell(aufrufe)["glm-4.7"] == 3


async def test_ein_verbund_probiert_alle_seine_mitglieder():
    """Wer fuenf nennt, meint fuenf -- die Obergrenze gilt der automatischen
    Wahl, nicht einer ausdruecklichen Aufzaehlung."""
    viele = {"data": [{"id": f"m{i}", "demand": i, "status": "ready",
                       "input": ["text"], "output": ["text"]} for i in range(5)]}
    aufrufe = []

    def handler(request):
        aufrufe.append(request)
        if request.url.path.endswith("/models"):
            return httpx.Response(200, json=viele)
        return httpx.Response(503, json={"error": "weg"})

    async with _client(handler, max_retries=0) as api:
        with pytest.raises(EduSharingError):
            await api.chat("x", model=["m0", "m1", "m2", "m3", "m4"])
    assert set(_versuche_je_modell(aufrufe)) == {"m0", "m1", "m2", "m3", "m4"}
