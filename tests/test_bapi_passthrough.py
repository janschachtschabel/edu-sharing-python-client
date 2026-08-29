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
from edusharing.errors import EduSharingError

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
        with pytest.raises(ValueError, match="without a leading"):
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
        with pytest.raises(ValueError):
            await api.call(route, {})
    assert not versendet, (
        f"{route!r} wurde abgesetzt: {versendet[0].url if versendet else ''}")
