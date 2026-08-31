"""Die OpenAI-vertraeglichen Routen, die das Gateway durchreicht.

Gemessen am 28.08.2026 gegen b-api.staging.openeduhub.net. Die Spezifikation
unter ``/v3/api-docs`` taugt dafuer **nicht**: sie beschreibt nur die
handgeschriebenen Controller und kennt weder ``/embeddings`` noch
``/moderations`` -- auch nicht ``/chat/completions``, das dieser Client seit
jeher erfolgreich ruft. Ermittelt wurde die Liste stattdessen mit absichtlich
leeren Rumpfen, an denen jede Route vor der Arbeit scheitert:

    403  Spring Security -- die Route steht NICHT auf der Positivliste
    400  die Route greift und bemaengelt die Anfrage
    429  Kontingent -- greift ebenfalls

Ergebnis: chat/completions, completions, embeddings, moderations, responses,
images/generations, images/edits, audio/*, files, batches, fine_tuning/jobs und
vector_stores werden durchgereicht. **Nicht** durchgereicht wird ``rerank`` --
403, wie eine frei erfundene Route. ``images/variations`` antwortet 404 von
OpenAI selbst, der Endpunkt ist dort abgekuendigt.
"""

import httpx
import pytest

from edusharing.bapi import BildungsAPI, Moderation
from edusharing.errors import EduSharingError, ValidationError

GATEWAY = "https://gateway.example.test"

EINBETTUNG = {
    "object": "list",
    "model": "text-embedding-3-small",
    "data": [
        {"object": "embedding", "index": 0, "embedding": [0.1, 0.2, 0.3]},
        {"object": "embedding", "index": 1, "embedding": [0.4, 0.5, 0.6]},
    ],
    "usage": {"prompt_tokens": 4, "total_tokens": 4},
}

MODERATION = {
    "id": "modr-1",
    "model": "omni-moderation-latest",
    "results": [{
        "flagged": True,
        "categories": {"hate": False, "violence": True, "sexual": False},
        "category_scores": {"hate": 0.01, "violence": 0.98, "sexual": 0.0},
    }],
}

BILDER = {"created": 1, "data": [
    {"url": "https://beispiel.test/a.png", "revised_prompt": "ein Baum"},
    {"b64_json": "aGFsbG8="},
]}


def _client(handler, aufrufe=None, **kwargs):
    def wrapped(request):
        if aufrufe is not None:
            aufrufe.append(request)
        return handler(request)

    kwargs.setdefault("api_key", "geheimer-schluessel")
    kwargs.setdefault("base_url", GATEWAY)
    kwargs.setdefault("backoff_base", 0.0)
    return BildungsAPI(
        client=httpx.AsyncClient(transport=httpx.MockTransport(wrapped)), **kwargs)


def _antwortet(nutzlast, status=200):
    return lambda _request: httpx.Response(status, json=nutzlast)


# --- Einbettungen ----------------------------------------------------------

async def test_einbettungen_kommen_als_vektoren_zurueck():
    """Die Vektoren, nicht die Huelle -- der Aufrufer will rechnen."""
    async with _client(_antwortet(EINBETTUNG)) as api:
        vektoren = await api.embeddings(["a", "b"], model="text-embedding-3-small")
    assert vektoren == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]


async def test_ein_einzelner_text_ergibt_eine_liste_mit_einem_vektor():
    """Wie bei OpenAI selbst: input nimmt beides, data ist immer eine Liste.
    Ein wechselnder Rueckgabetyp zwaenge jeden Aufrufer zu einer Typpruefung."""
    einer = dict(EINBETTUNG, data=[EINBETTUNG["data"][0]])
    async with _client(_antwortet(einer)) as api:
        vektoren = await api.embeddings("nur einer", model="m")
    assert vektoren == [[0.1, 0.2, 0.3]]


async def test_einbettungen_gehen_an_die_richtige_route(aufrufe=None):
    aufrufe = []
    async with _client(_antwortet(EINBETTUNG), aufrufe) as api:
        await api.embeddings("x", model="m", provider="openai")
    assert aufrufe[0].url.path.endswith("/api/v1/llm/openai/embeddings")


async def test_die_reihenfolge_der_vektoren_folgt_dem_index():
    """Die API darf umsortiert antworten; index ist die Zuordnung. Ohne
    Sortierung bekaeme der Aufrufer Vektoren zum falschen Text."""
    verdreht = dict(EINBETTUNG, data=list(reversed(EINBETTUNG["data"])))
    async with _client(_antwortet(verdreht)) as api:
        vektoren = await api.embeddings(["a", "b"], model="m")
    assert vektoren == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]


# --- Moderation ------------------------------------------------------------

async def test_moderation_verdichtet_auf_geflaggt_und_warum():
    """Die Rohantwort fuehrt gut ein Dutzend Kategorien plus Punktwerte. Was
    ein Aufrufer entscheidet, ist: durchlassen oder nicht, und woran es lag."""
    async with _client(_antwortet(MODERATION)) as api:
        urteil = await api.moderate("etwas", model="omni-moderation-latest")
    assert isinstance(urteil, Moderation)
    assert urteil.flagged is True
    assert urteil.categories == ("violence",)
    assert urteil.scores["violence"] == 0.98
    assert urteil.raw is not None


async def test_unbeanstandeter_text_hat_keine_kategorien():
    sauber = {"id": "m", "model": "m", "results": [{
        "flagged": False,
        "categories": {"hate": False, "violence": False},
        "category_scores": {"hate": 0.0, "violence": 0.0}}]}
    async with _client(_antwortet(sauber)) as api:
        urteil = await api.moderate("harmlos", model="m")
    assert urteil.flagged is False
    assert urteil.categories == ()


async def test_moderation_ohne_ergebnis_ist_ein_fehler():
    """Eine leere results-Liste als 'nicht beanstandet' zu lesen waere die
    gefaehrlichste Auslegung -- dann liesse ein Ausfall alles durch."""
    async with _client(_antwortet({"id": "m", "model": "m", "results": []})) as api:
        with pytest.raises(EduSharingError, match="no result"):
            await api.moderate("etwas", model="m")


# --- Bilder ----------------------------------------------------------------

async def test_bilder_kommen_mit_url_oder_base64():
    """response_format entscheidet, was zurueckkommt. Beides in einem Feld zu
    mischen zwaenge den Aufrufer zum Raten."""
    async with _client(_antwortet(BILDER)) as api:
        bilder = await api.images("ein Baum", model="dall-e-3")
    assert [b.url for b in bilder] == ["https://beispiel.test/a.png", None]
    assert [b.b64 for b in bilder] == [None, "aGFsbG8="]
    assert bilder[0].revised_prompt == "ein Baum"


# --- Der generische Weg ----------------------------------------------------

async def test_call_erreicht_jede_durchgereichte_route():
    """Wie repo.raw fuer edu-sharing: was keine eigene Methode hat, ist
    trotzdem erreichbar -- 14 Routen bekommen keine dreizehn Wrapper."""
    aufrufe = []
    async with _client(_antwortet({"ok": True}), aufrufe) as api:
        antwort = await api.call("audio/speech", {"model": "tts-1", "input": "hi"})
    assert antwort == {"ok": True}
    assert aufrufe[0].url.path.endswith("/api/v1/llm/academiccloud/audio/speech")


async def test_call_lehnt_einen_fuehrenden_schraegstrich_ab():
    """Sonst entstuende /api/v1/llm/anbieter//route, und der Fehler kaeme vom
    Server statt von hier."""
    async with _client(_antwortet({})) as api:
        with pytest.raises(ValidationError, match="without a leading"):
            await api.call("/audio/speech", {})


async def test_ein_fehler_der_route_wird_durchgereicht():
    async with _client(_antwortet({"message": "you must provide a model"}, 400)) as api:
        with pytest.raises(EduSharingError, match="model"):
            await api.embeddings("x", model="")


# --- Die Route ist eine Vertrauensgrenze -----------------------------------

@pytest.mark.parametrize("route", [
    "embeddings",
    "chat/completions",
    "images/generations",
    "fine_tuning/jobs",
    "vector_stores",
])
async def test_echte_routen_gehen_durch(route):
    aufrufe = []
    async with _client(_antwortet({"ok": True}), aufrufe) as api:
        await api.call(route, {})
    assert aufrufe[0].url.path.endswith(f"/api/v1/llm/academiccloud/{route}")


@pytest.mark.parametrize("route", [
    "../../administration/account",   # verlaesst /api/v1/llm/ voellig
    "..",
    "a/../../b",
    "/embeddings",                    # fuehrender Schraegstrich
    "embeddings/",                    # leeres Segment am Ende
    "a//b",                           # leeres Segment in der Mitte
    "embeddings?admin=1",             # eingeschmuggelte Anfrageparameter
    "embeddings#x",
    "embeddings account",
    "",
])
async def test_eine_route_darf_ihren_pfad_nicht_verlassen(route):
    """Gemessen am 28.08.2026, bevor das hier stand:

        call("../../administration/account")
        -> https://…/api/v1/administration/account

    Die Anfrage verliess /api/v1/llm/{provider}/, erreichte die
    Administrations-API und nahm den X-API-KEY mit. ``path_segment`` wurde auf
    den Anbieter angewandt, auf die Route nicht -- in derselben Zeile.

    Das zaehlt hier besonders: diese Bibliothek ist fuer KI-Anwendungen gebaut,
    und ``call`` ist die Methode, deren Argument ein Modell waehlt. Genau der
    Fall, den der Docstring von ``path_segment`` als Grund seiner Existenz
    nennt.
    """
    versendet = []
    async with _client(_antwortet({"ok": True}), versendet) as api:
        with pytest.raises(ValidationError):
            await api.call(route, {})
    assert not versendet, (
        f"{route!r} wurde abgesetzt: {versendet[0].url if versendet else ''}")


# --- responses -------------------------------------------------------------
#
# Gemessen am 31.08.2026: **beide** Anbieter koennen den Endpunkt.
#
#   openai/gpt-5.6-luna     status=completed   'Hallo!'
#   academiccloud/gemma-4   status=completed   'Hallo! Wie kann ich dir...'
#   academiccloud/qwen3.5   status=incomplete  Budget ins Denken gelaufen
#
# Die Parameterform ist eine andere als bei chat/completions -- dort
# ``reasoning_effort``, hier ``reasoning={"effort": ...}``. Die chat-Form wird
# ausdruecklich abgelehnt: "Unsupported parameter: 'reasoning_effort'. In the
# Responses API, ...". ``model`` ist Pflicht, es gibt keine automatische Wahl.

ANTWORT_FERTIG = {
    "status": "completed",
    "model": "gpt-5.6-luna",
    "output": [{"content": [{"type": "output_text", "text": "Hallo!"}]}],
    "usage": {"output_tokens": 6},
}

ANTWORT_ABGESCHNITTEN = {
    "status": "incomplete",
    "model": "qwen3.5-122b-a10b",
    "incomplete_details": {"reason": "max_output_tokens"},
    "output": [{"content": [{"type": "output_text", "text": "Thinking Proce"}]}],
    "usage": {"output_tokens": 64},
}


async def test_responses_liefert_den_text():
    async with _client(lambda r: httpx.Response(200, json=ANTWORT_FERTIG)) as api:
        antwort = await api.respond("Sag hallo.", model="gpt-5.6-luna")
    assert antwort.text == "Hallo!"
    assert antwort.status == "completed"
    assert antwort.truncated is False
    assert antwort.model == "gpt-5.6-luna"


async def test_eine_abgeschnittene_antwort_sagt_dass_sie_es_ist():
    """Der Punkt der ganzen Klasse.

    ``incomplete`` heisst, das Budget ist ins Denken gelaufen und der Text ist
    abgeschnitten. Nur den Text zurueckzugeben saehe aus wie eine vollstaendige
    Antwort -- und genau davor schuetzt diese Bibliothek sonst ueberall.
    """
    async with _client(lambda r: httpx.Response(200, json=ANTWORT_ABGESCHNITTEN)) as api:
        antwort = await api.respond("x", model="qwen3.5-122b-a10b")
    assert antwort.truncated is True
    assert antwort.reason == "max_output_tokens"
    assert antwort.text == "Thinking Proce"


async def test_ohne_modell_gibt_es_keine_anfrage():
    """Der Endpunkt verlangt es, und raten waere eine stille Modellwahl."""
    async with _client(lambda r: httpx.Response(200, json=ANTWORT_FERTIG)) as api:
        with pytest.raises(EduSharingError):
            await api.respond("x", model="")


async def test_die_vorgabe_kommt_in_der_responses_form():
    aufrufe = []

    def handler(request):
        aufrufe.append(request)
        return httpx.Response(200, json=ANTWORT_FERTIG)

    async with _client(handler) as api:
        await api.respond("x", model="gpt-5.6-luna")
    import json as _json
    koerper = _json.loads(aufrufe[-1].content)
    assert koerper["reasoning"] == {"effort": "low"}
    assert koerper["text"] == {"verbosity": "low"}
    assert "reasoning_effort" not in koerper


async def test_ohne_faehiges_modell_entfaellt_die_vorgabe():
    aufrufe = []

    def handler(request):
        aufrufe.append(request)
        return httpx.Response(200, json=ANTWORT_FERTIG)

    async with _client(handler) as api:
        await api.respond("x", model="gemma-4-31b-it")
    import json as _json
    koerper = _json.loads(aufrufe[-1].content)
    assert "reasoning" not in koerper
    assert "text" not in koerper


async def test_ausdruecklicher_wunsch_wird_auch_hier_nicht_verworfen():
    async with _client(lambda r: httpx.Response(200, json=ANTWORT_FERTIG)) as api:
        with pytest.raises(ValidationError) as info:
            await api.respond("x", model="gemma-4-31b-it", reasoning_effort="high")
    assert "gemma-4-31b-it" in str(info.value)


# --- Fremddaten am Rand ----------------------------------------------------

@pytest.mark.parametrize("rumpf, erwartet", [
    ({"output": [{"content": [{"text": "ok"}]}]}, "ok"),
    ({"output": ["Text statt eines Eintrags"]}, ""),
    ({"output": [{"content": "kein dict"}]}, ""),
    ({"output": [{}]}, ""),
    ({"output": None}, ""),
    ({}, ""),
])
def test_der_text_wird_auch_aus_unerwarteten_ruempfen_gelesen(rumpf, erwartet):
    """Der Rumpf kommt vom Gateway, nicht von uns.

    Ein ``AttributeError`` waere hier weder aussagekraeftig noch als
    ``EduSharingError`` fangbar -- die Bibliothek ist an genau solchen Raendern
    sonst vorsichtig (``Model.is_retired_on`` faengt das unlesbare Datum,
    ``read_answer`` prueft auf leere ``choices``).
    """
    from edusharing.bapi.passthrough import _text_of
    assert _text_of(rumpf) == erwartet


async def test_zwei_wege_denselben_wert_zu_setzen_sind_ein_fehler():
    """``extra`` ist die Notluke -- aber nicht, um denselben Wert zweimal zu setzen.

    Frueher gewann ``extra`` stillschweigend, weil es zuletzt ausgebreitet
    wurde: ``reasoning_effort="high"`` verschwand neben einem eigenen
    ``reasoning``. Das ist genau die stille Verwerfung, gegen die diese
    Parameter ueberhaupt so behandelt werden.
    """
    async with _client(lambda r: httpx.Response(200, json=ANTWORT_FERTIG)) as api:
        with pytest.raises(ValidationError) as info:
            await api.respond("x", model="gpt-5.6-luna", reasoning_effort="high",
                              reasoning={"effort": "minimal"})
    assert "reasoning" in str(info.value)


async def test_wer_nur_extra_setzt_bekommt_es_und_nicht_die_vorgabe():
    """Umgekehrt darf die Vorgabe einen eigenen Wert nicht ueberschreiben."""
    aufrufe = []

    def handler(request):
        aufrufe.append(request)
        return httpx.Response(200, json=ANTWORT_FERTIG)

    async with _client(handler) as api:
        await api.respond("x", model="gpt-5.6-luna",
                          reasoning={"effort": "minimal"})
    import json as _json
    koerper = _json.loads(aufrufe[-1].content)
    assert koerper["reasoning"] == {"effort": "minimal"}
    # Die Vorgabe fuer verbosity bleibt, die kollidiert ja nicht.
    assert koerper["text"] == {"verbosity": "low"}
