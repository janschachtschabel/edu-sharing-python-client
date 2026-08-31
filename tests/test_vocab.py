"""Vokabular: Labels statt URIs.

Der Kern der Repository-Unabhaengigkeit. Statt eine Tabelle mitzuliefern, die
nur fuer eine Instanz stimmt, wird gefragt, was *diese* Instanz anbietet.

Die Antwortform stammt aus einer Messung gegen edu-sharing 11.0 (Staging,
27.08.2026) -- sie weicht von der OpenAPI-Spezifikation ab: die deklariert
``MdsValue {id, caption}``, geliefert wird ``{key, displayString}``.
"""

import asyncio

import httpx
import pytest

from edusharing.errors import EduSharingError
from edusharing.transport import Transport
from edusharing.vocab import Vocabulary

REPO = "https://repositorium.example.test/edu-sharing"

# Gemessene Antwort von POST /mds/v1/metadatasets/-home-/mds_oeh/values
FAECHER = {"values": [
    {"key": "http://w3id.org/openeduhub/vocabs/discipline/460",
     "displayString": "Physik", "replacementString": None, "translation": None},
    {"key": "http://w3id.org/openeduhub/vocabs/discipline/080",
     "displayString": "Biologie", "replacementString": None, "translation": None},
    {"key": "http://w3id.org/openeduhub/vocabs/discipline/44007",
     "displayString": "Nachhaltigkeit", "replacementString": None, "translation": None},
]}


def _vocab(handler, **kwargs):
    transport = Transport(
        REPO, client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        backoff_base=0.0,
    )
    return Vocabulary(transport, **kwargs)


def _liefert(payload, aufrufe: list | None = None):
    def handler(request: httpx.Request) -> httpx.Response:
        if aufrufe is not None:
            aufrufe.append(request)
        return httpx.Response(200, json=payload)
    return handler


# --- Werte holen ----------------------------------------------------------

async def test_values_liefert_uri_und_label():
    v = _vocab(_liefert(FAECHER))
    werte = await v.values("ccm:taxonid")
    assert len(werte) == 3
    assert werte[0].uri == "http://w3id.org/openeduhub/vocabs/discipline/460"
    assert werte[0].label == "Physik"


async def test_leere_antwort_ergibt_leere_liste():
    """Eine Property ohne Vokabular ist kein Fehler."""
    v = _vocab(_liefert({"values": []}))
    assert await v.values("cclom:title") == []


async def test_antwort_ohne_values_schluessel_stuerzt_nicht_ab():
    v = _vocab(_liefert({}))
    assert await v.values("ccm:taxonid") == []


async def test_pattern_leer_statt_all():
    """Gemessen: pattern:"" listet alle Werte, das dokumentierte "-all-"
    liefert **null** zurueck. Die naheliegende Schreibweise ist die falsche."""
    aufrufe = []
    v = _vocab(_liefert(FAECHER, aufrufe))
    await v.values("ccm:taxonid")
    import json
    body = json.loads(aufrufe[0].content)
    assert body["valueParameters"]["pattern"] == ""


async def test_anfrage_nennt_property_und_query():
    aufrufe = []
    v = _vocab(_liefert(FAECHER, aufrufe), metadataset="mds_oeh")
    await v.values("ccm:taxonid")
    import json
    body = json.loads(aufrufe[0].content)
    assert body["valueParameters"]["property"] == "ccm:taxonid"
    assert body["valueParameters"]["query"] == "ngsearch"
    assert "mds_oeh/values" in str(aufrufe[0].url)


# --- Label -> URI ---------------------------------------------------------

async def test_resolve_findet_das_label():
    v = _vocab(_liefert(FAECHER))
    assert await v.resolve("ccm:taxonid", "Physik") == \
        "http://w3id.org/openeduhub/vocabs/discipline/460"


async def test_resolve_ignoriert_gross_klein_und_rand():
    v = _vocab(_liefert(FAECHER))
    assert await v.resolve("ccm:taxonid", "  physik ") is not None


async def test_resolve_gibt_none_bei_unbekanntem_label():
    """Wichtiger als es aussieht: eine stillschweigend verworfene Einschraenkung
    liefert Treffer, die niemand angefragt hat."""
    v = _vocab(_liefert(FAECHER))
    assert await v.resolve("ccm:taxonid", "Unterwasserkorbflechten") is None


async def test_resolve_raet_nicht():
    """Kein unscharfer Abgleich. Gemessen im WLO-MCP: 'bildungsinhalte' wuerde
    unscharf auf **Bild** aufloesen und eine Themensuche in eine Bildersuche
    verwandeln. Lieber None und eine Rueckfrage."""
    v = _vocab(_liefert(FAECHER))
    assert await v.resolve("ccm:taxonid", "Phys") is None
    assert await v.resolve("ccm:taxonid", "Physikunterricht") is None


async def test_ein_uri_wird_unveraendert_durchgereicht():
    """Wer die URI schon hat, soll sie uebergeben duerfen -- ohne dass dafuer
    ein Vokabular geladen wird."""
    aufrufe = []
    v = _vocab(_liefert(FAECHER, aufrufe))
    uri = "http://w3id.org/openeduhub/vocabs/discipline/460"
    assert await v.resolve("ccm:taxonid", uri) == uri
    assert aufrufe == []


# --- Vorschlaege ----------------------------------------------------------

async def test_suggest_reicht_die_eingabe_als_pattern_durch():
    """Gemessen: pattern ist eine TEILSTRING-Suche, keine Praefixsuche --
    "ysik" liefert Physik, Atomphysik und Kernphysik. Der Endpunkt taugt als
    Typeahead-Quelle, aber nicht mit Praefix-Erwartung."""
    aufrufe = []
    v = _vocab(_liefert(FAECHER, aufrufe))
    await v.suggest("ccm:taxonid", "Ph")
    import json
    assert json.loads(aufrufe[0].content)["valueParameters"]["pattern"] == "Ph"


async def test_suggest_wird_nicht_gecacht():
    """Jedes Praefix ist eine andere Anfrage -- ein Cache darueber wuerde nur
    Speicher fuellen."""
    aufrufe = []
    v = _vocab(_liefert(FAECHER, aufrufe))
    await v.suggest("ccm:taxonid", "Ph")
    await v.suggest("ccm:taxonid", "Ph")
    assert len(aufrufe) == 2


# --- Cache ----------------------------------------------------------------

async def test_zweiter_zugriff_fragt_nicht_erneut():
    aufrufe = []
    v = _vocab(_liefert(FAECHER, aufrufe))
    await v.values("ccm:taxonid")
    await v.values("ccm:taxonid")
    await v.resolve("ccm:taxonid", "Physik")
    assert len(aufrufe) == 1


async def test_cache_trennt_nach_property():
    aufrufe = []
    v = _vocab(_liefert(FAECHER, aufrufe))
    await v.values("ccm:taxonid")
    await v.values("ccm:educationalcontext")
    assert len(aufrufe) == 2


async def test_cache_trennt_nach_sprache():
    """Gemessen: der Header locale=en_EN liefert englische Labels. Ein
    gemeinsamer Cache wuerde sie vermischen."""
    aufrufe = []
    v = _vocab(_liefert(FAECHER, aufrufe))
    await v.values("ccm:taxonid")
    await v.values("ccm:taxonid", locale="en_EN")
    assert len(aufrufe) == 2
    assert aufrufe[1].headers.get("locale") == "en_EN"


async def test_gleichzeitige_zugriffe_fragen_nur_einmal():
    """Ein Fan-out ueber viele Knoten fragt dasselbe Vokabular gleichzeitig an.
    Ohne Sperre laedt jeder Aufruf es einzeln."""
    aufrufe = []

    async def handler(request):
        aufrufe.append(request)
        await asyncio.sleep(0.01)
        return httpx.Response(200, json=FAECHER)

    v = _vocab(handler)
    await asyncio.gather(*(v.values("ccm:taxonid") for _ in range(8)))
    assert len(aufrufe) == 1


async def test_clear_cache_erzwingt_neuladen():
    aufrufe = []
    v = _vocab(_liefert(FAECHER, aufrufe))
    await v.values("ccm:taxonid")
    v.clear_cache()
    await v.values("ccm:taxonid")
    assert len(aufrufe) == 2


async def test_fehler_wird_nicht_gecacht():
    """Sonst haengt ein voruebergehender Ausfall dem Prozess dauerhaft an."""
    zustand = {"fehler": True}

    def handler(request):
        if zustand["fehler"]:
            return httpx.Response(500, json={"error": "x", "message": "kaputt"})
        return httpx.Response(200, json=FAECHER)

    v = _vocab(handler)
    with pytest.raises(EduSharingError):
        await v.values("ccm:taxonid")
    zustand["fehler"] = False
    assert len(await v.values("ccm:taxonid")) == 3


# --- Aufraeumen -----------------------------------------------------------

async def test_clear_cache_raeumt_auch_die_sperren():
    """Audit-Befund F6 vom 27.08.2026: clear_cache() leerte den Cache, liess die
    Sperren aber stehen.

    Zwei Gruende, warum das zaehlt: der Name verspricht mehr, als die Methode
    hielt, und in einem langlaufenden Dienst -- einem MCP-Server etwa -- waechst
    das Sperren-Verzeichnis mit jeder Kombination aus Feld und Sprache, ohne
    dass es je wieder kleiner wird.
    """
    v = _vocab(_liefert(FAECHER))
    await v.values("ccm:taxonid")
    await v.values("ccm:educationalcontext", locale="de")
    assert v._cache and v._locks, "Vorbedingung: beide Verzeichnisse gefuellt"

    v.clear_cache()

    assert not v._cache
    assert not v._locks, "die Sperren bleiben stehen -- das Verzeichnis waechst"


async def test_nach_clear_cache_wird_neu_geladen():
    """Gegenprobe: das Aufraeumen darf die Funktion nicht beschaedigen."""
    aufrufe: list = []
    v = _vocab(_liefert(FAECHER, aufrufe))
    await v.values("ccm:taxonid")
    v.clear_cache()
    assert len(await v.values("ccm:taxonid")) == 3
    assert len(aufrufe) == 2, "nach dem Leeren muss erneut geladen werden"


# --- Ein Label, zwei Vokabulare -------------------------------------------
#
# Gemessen am 31.08.2026 gegen die Staging: 25 Fachlabels stehen doppelt --
# einmal in ``discipline`` (Schulfach), einmal in ``hochschulfaechersystematik``.
# ``Biologie``, ``Chemie``, ``Ethik``, ``Physik`` und 21 weitere.
#
# ``resolve`` nahm den ersten Treffer, ohne zu sagen, dass es einen zweiten
# gibt. Eine Suche nach ``subject="Biologie"`` fand damit nur die eine Haelfte,
# und niemand konnte das sehen. Wer die Haelften trennen will, filtert
# zusaetzlich nach Bildungsstufe.

DOPPELT = {"values": [
    {"key": "http://w3id.org/openeduhub/vocabs/discipline/080",
     "displayString": "Biologie", "replacementString": None, "translation": None},
    {"key": "http://w3id.org/openeduhub/vocabs/hochschulfaechersystematik/n026",
     "displayString": "Biologie", "replacementString": None, "translation": None},
    {"key": "http://w3id.org/openeduhub/vocabs/discipline/460",
     "displayString": "Physik", "replacementString": None, "translation": None},
]}


async def test_resolve_all_liefert_beide_vokabulare():
    vocab = _vocab(lambda r: httpx.Response(200, json=DOPPELT))
    uris = await vocab.resolve_all("ccm:taxonid", "Biologie")
    assert len(uris) == 2
    assert any("discipline" in u for u in uris)
    assert any("hochschulfaechersystematik" in u for u in uris)


async def test_resolve_all_bei_eindeutigem_label():
    vocab = _vocab(lambda r: httpx.Response(200, json=DOPPELT))
    assert len(await vocab.resolve_all("ccm:taxonid", "Physik")) == 1


async def test_resolve_all_bei_unbekanntem_label():
    vocab = _vocab(lambda r: httpx.Response(200, json=DOPPELT))
    assert await vocab.resolve_all("ccm:taxonid", "Gibtsnicht") == []


async def test_eine_uri_geht_unveraendert_durch():
    """Wie bei ``resolve``: eine URI ist schon, was das Repositorium will."""
    vocab = _vocab(lambda r: httpx.Response(200, json=DOPPELT))
    uri = "http://w3id.org/openeduhub/vocabs/discipline/080"
    assert await vocab.resolve_all("ccm:taxonid", uri) == [uri]


async def test_resolve_bleibt_die_einzahl():
    """Der alte Aufruf aendert sich nicht -- er hat weiterhin seinen Zweck."""
    vocab = _vocab(lambda r: httpx.Response(200, json=DOPPELT))
    einer = await vocab.resolve("ccm:taxonid", "Biologie")
    assert einer in await vocab.resolve_all("ccm:taxonid", "Biologie")
