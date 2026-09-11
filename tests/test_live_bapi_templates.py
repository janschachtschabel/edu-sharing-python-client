"""Der Template-Modus gegen die echte b-api -- und gegen das Repositorium,
dessen Metadatenset die Konfigurationen traegt.

    uv run pytest -m live  tests/test_live_bapi_templates.py
    uv run pytest -m write tests/test_live_bapi_templates.py

``-m live`` braucht ``B_API_KEY``, ``B_API_BASE_URL`` und ``EDU_SHARING_URL``;
``-m write`` zusaetzlich ``EDU_SHARING_USER`` und ``EDU_SHARING_PASSWORD``.

Jede Pruefung hier steht als Zusage in REFERENCE oder im Docstring von
``BapiTemplates``, gemessen am 11.09.2026 gegen Staging. Die Kette wird aus
dem Metadatenset gelesen, nicht geraten: fehlt eine Konfiguration, springt der
Test ueber, statt an einer umbenannten ID zu scheitern.

**Schreibend** (``-m write``) wird nur in einem eigens angelegten Ordner im
Home-Verzeichnis gearbeitet, der am Ende endgueltig geloescht wird. Zwei Tests
muessen ihren Knoten dafuer oeffnen, weil das Gateway mit seinem **eigenen**
Konto liest (gemessen: privat -> 403): ``suggest`` veroeffentlicht ihn, ``qas``
gibt dem Konto des Gateways zusaetzlich Write. Beides nur am Wegwerf-Knoten.
Welches Konto das ist, sagt das Gateway selbst -- als ``createdBy`` eines
Vorschlags, den es gerade angelegt hat --, statt dass es hier geraten wird.
"""

import os
import uuid
import warnings

import pytest

from edusharing import AsyncRepository
from edusharing.bapi import BapiTemplates
from edusharing.errors import EduSharingError, PermissionDeniedError, ValidationError
from edusharing.nodes import Node

METADATENSET = os.environ.get("EDU_SHARING_METADATASET") or "mds_oeh"

ANBIETER = "topic_page_ai_default"
MODELL = "topic_page_ai_chat_completion"
#: Liest ``{{var(cm:name)|node(cm:name)|-}}`` -- der Platzhalter, an dem sich
#: "var vor node" und "limited setzt keinen freien Text ein" zeigen lassen.
TEXT = [ANBIETER, MODELL, "topic_page_ai_text_widget"]
#: Liest ``var(ccm:taxonid_DISPLAYNAME)`` -- das, was eine limited-Wahl nicht fuellt.
BESCHREIBUNG = [ANBIETER, MODELL, "topic_page_ai_topic_header_description"]

pytestmark = pytest.mark.skipif(
    not (os.environ.get("B_API_KEY") and os.environ.get("B_API_BASE_URL")
         and os.environ.get("EDU_SHARING_URL")),
    reason="B_API_KEY/B_API_BASE_URL/EDU_SHARING_URL nicht gesetzt",
)
_angemeldet = pytest.mark.skipif(
    not os.environ.get("EDU_SHARING_USER"), reason="EDU_SHARING_USER nicht gesetzt")


@pytest.fixture
async def repo():
    async with AsyncRepository.from_env(metadataset=METADATENSET) as r:
        yield r


@pytest.fixture
async def vorlagen():
    async with BapiTemplates.from_env(metadataset=METADATENSET) as t:
        yield t


@pytest.fixture
async def konfigurationen(repo):
    """Die KI-Konfigurationen des Metadatensets, je ID -- gelesen, nicht geraten."""
    mds = await repo.raw.json("GET", f"/mds/v1/metadatasets/-home-/{METADATENSET}")
    return {c["id"]: c for c in (mds.get("aiConfigs") or []) if c.get("id")}


@pytest.fixture
async def sammlung(repo):
    """Eine oeffentliche Sammlung als Kontext -- gemessen: ``MINT-Faecher``."""
    gefunden = await repo.flows.find_collections("Biologie", limit=3)
    if not gefunden["hits"]:
        pytest.skip("keine Sammlung als Kontext gefunden")
    return gefunden["hits"][0]["id"]


def _braucht(konfigurationen: dict, ids: list[str]) -> None:
    fehlend = [i for i in ids if i not in konfigurationen]
    if fehlend:
        pytest.skip(f"nicht im Metadatenset {METADATENSET}: {fehlend}")


def _merkt_sich(konfigurationen: dict) -> None:
    """Wortgleichheit belegt nur etwas, wenn die Kette ihre Antworten merkt."""
    if not konfigurationen[ANBIETER].get("useCaching"):
        pytest.skip(f"{ANBIETER} merkt sich keine Antworten mehr (useCaching)")


# --- Lesend -----------------------------------------------------------------

@pytest.mark.live
async def test_die_kette_antwortet_aus_dem_kontextknoten(vorlagen, konfigurationen, sammlung):
    _braucht(konfigurationen, TEXT)
    antwort = await vorlagen.chat(TEXT, context_node_id=sammlung)
    assert antwort.strip()


@pytest.mark.live
async def test_ein_wert_gewinnt_vor_der_eigenschaft_des_knotens(
        vorlagen, konfigurationen, sammlung):
    _braucht(konfigurationen, TEXT)
    antwort = await vorlagen.chat(TEXT, context_node_id=sammlung,
                                  variables={"cm:name": "Vulkane"})
    assert "vulkan" in antwort.lower()


@pytest.mark.live
async def test_dieselbe_anfrage_kommt_wortgleich_zurueck(vorlagen, konfigurationen, sammlung):
    """REFERENCE: ``topic_page_ai_default`` setzt ``useCaching``."""
    _braucht(konfigurationen, TEXT)
    _merkt_sich(konfigurationen)
    erste = await vorlagen.chat(TEXT, context_node_id=sammlung)
    zweite = await vorlagen.chat(TEXT, context_node_id=sammlung)
    assert erste == zweite


@pytest.mark.live
async def test_limited_setzt_freien_text_nicht_ein(vorlagen, konfigurationen, sammlung):
    """``cm:name`` hat keinen Wertebereich, und der Prompt liest es als
    ``var(cm:name)`` -- kaeme freier Text durch, stuende hier "Vulkane"."""
    _braucht(konfigurationen, TEXT)
    antwort = await vorlagen.chat_limited(TEXT, context_node_id=sammlung,
                                          choices={"cm:name": "Vulkane"})
    assert "vulkan" not in antwort.lower()


@pytest.mark.live
async def test_eine_wahl_fuellt_displayname_nicht(repo, vorlagen, konfigurationen, sammlung):
    """Mit dem Merken ist die Antwort ohne Wahl der Vergleich: dieselbe, Wort
    fuer Wort, hiess am 11.09.2026 -- die Wahl kam im Prompt nicht an."""
    _braucht(konfigurationen, BESCHREIBUNG)
    _merkt_sich(konfigurationen)
    chemie = await repo.vocab.resolve("ccm:taxonid", "Chemie")
    if chemie is None:
        pytest.skip("kein Wert 'Chemie' in ccm:taxonid")
    ohne = await vorlagen.chat(BESCHREIBUNG, context_node_id=sammlung)
    mit = await vorlagen.chat_limited(BESCHREIBUNG, context_node_id=sammlung,
                                      choices={"ccm:taxonid": chemie})
    assert mit == ohne


@pytest.mark.live
async def test_respond_mit_einer_chat_konfiguration_sagt_warum_nicht(
        vorlagen, konfigurationen, sammlung):
    _braucht(konfigurationen, TEXT)
    with pytest.raises(ValidationError) as fehler:
        await vorlagen.respond(TEXT, context_node_id=sammlung)
    assert "Unsupported parameter" in str(fehler.value)
    assert "{'message'" not in str(fehler.value)


@pytest.mark.live
async def test_eine_unbekannte_konfiguration_ist_ein_validierungsfehler(vorlagen, sammlung):
    with pytest.raises(ValidationError, match="has no AI configuration"):
        await vorlagen.chat([f"gibt_es_nicht_{uuid.uuid4().hex[:8]}"],
                            context_node_id=sammlung)


# --- Schreibend: ein Wegwerf-Knoten je Test ----------------------------------

@pytest.fixture
async def ordner(repo):
    """Ein frischer Ordner im Home-Verzeichnis, der am Ende endgueltig geht."""
    wer = await repo.whoami()
    assert not wer.is_anonymous, "Schreibtests brauchen ein angemeldetes Konto"
    home = ((wer.raw.get("person") or {}).get("homeFolder") or {}).get("id")
    assert home, "kein Home-Verzeichnis -- ohne das wird hier nichts geschrieben"
    neu = await repo.create_node(
        home, name=f"pytest-edusharing-{uuid.uuid4().hex[:8]}", type="cm:folder")
    try:
        yield neu
    finally:
        await _wegwerfen(neu)


async def _wegwerfen(knoten: Node) -> None:
    """Endgueltig loeschen, und ein Scheitern melden statt den Testfehler zu
    ueberschreiben -- wie in ``test_live_write``."""
    try:
        await knoten.delete(recycle=False)
    except EduSharingError as exc:
        warnings.warn(f"Aufraeumen von {knoten.id!r} fehlgeschlagen: {exc}", stacklevel=2)


@pytest.mark.write
@_angemeldet
async def test_ein_privater_knoten_ist_fuer_das_gateway_zu(
        repo, vorlagen, konfigurationen, ordner):
    """Auch mit dem eigenen Konto in ``user`` -- das Gateway liest mit seinem."""
    _braucht(konfigurationen, TEXT)
    knoten = await repo.create_node(ordner.id, name="privat.txt", title="Privat")
    ich = (await repo.whoami()).username
    for wer in ("guest", ich):
        with pytest.raises(PermissionDeniedError, match="own account"):
            await vorlagen.chat(TEXT, context_node_id=knoten.id, user=wer)


@pytest.mark.write
@_angemeldet
async def test_suggest_legt_an_was_accept_suggestion_uebernimmt(
        repo, vorlagen, konfigurationen, ordner):
    """Die ganze Kette, die README, REFERENCE und SKILL versprechen: die b-api
    schlaegt vor, ``node.suggestions`` liest es, ``flows.accept_suggestion``
    uebernimmt es. Gemessen am 11.09.2026: das Schlagwort landet am Knoten,
    die uebrigen Vorschlaege bleiben offen."""
    _braucht(konfigurationen, ["suggestion_ai"])
    knoten = await repo.create_node(ordner.id, name="photosynthese.txt",
                                    title="Photosynthese bei Pflanzen")
    await knoten.permissions.publish()
    vorschlaege = await vorlagen.suggest(
        ["suggestion_ai"], {"cclom:general_keyword": "default"},
        context_node_id=knoten.id,
        variables={"cclom:title": "Photosynthese bei Pflanzen",
                   "cclom:general_description":
                       "Wie Pflanzen aus Licht, Wasser und Kohlenstoffdioxid "
                       "Zucker und Sauerstoff bilden."})
    assert vorschlaege, "keine Vorschlaege angelegt"
    assert all(v.id and v.value and v.status == "PENDING" for v in vorschlaege)
    assert {v.property for v in vorschlaege} == {"cclom:general_keyword"}
    gelesen = await (await repo.node(knoten.id)).suggestions.list()
    assert {v.id for v in vorschlaege} <= {g.id for g in gelesen}

    bester = max(vorschlaege, key=lambda v: v.confidence or 0)
    angenommen = await repo.flows.accept_suggestion(knoten.id, bester.id)
    assert angenommen["applied"] is True, angenommen
    assert angenommen["status"] == "ACCEPTED", angenommen
    frisch = await repo.node(knoten.id)
    assert bester.value in frisch.keywords
    assert {s.status for s in await frisch.suggestions.list()
            if s.id != bester.id} <= {"PENDING"}


@pytest.mark.write
@_angemeldet
async def test_qas_braucht_write_und_liefert_fragen_mit_antworten(
        repo, vorlagen, konfigurationen, ordner):
    """Veroeffentlicht genuegte nicht (403 *requires permission(s): Write*);
    mit Write fuer das Konto des Gateways kamen die Paare -- nach rund 50 s.

    Das Konto steht nicht hier im Test (Review 11.09.2026): ein fest
    eingetragenes ``admin@B-API`` bekaeme an einem anderen Gateway ein Recht,
    das dort niemandem gehoert -- ``grant`` legt auch einen unbekannten Namen
    ohne Widerspruch an --, und der Test schluege fehl, statt es zu sagen."""
    _braucht(konfigurationen, ["suggestion_ai"])
    knoten = await repo.create_node(ordner.id, name="photosynthese.txt",
                                    title="Photosynthese")
    await knoten.content.upload(
        b"Photosynthese ist der Vorgang, bei dem Pflanzen mit Hilfe von "
        b"Lichtenergie aus Wasser und Kohlenstoffdioxid Traubenzucker und "
        b"Sauerstoff bilden.", filename="photosynthese.txt", mimetype="text/plain")
    await knoten.permissions.publish()
    with pytest.raises(PermissionDeniedError, match="Write"):
        await vorlagen.qas([knoten.id])

    [vorschlag, *_] = await vorlagen.suggest(
        ["suggestion_ai"], {"cclom:general_keyword": "default"},
        context_node_id=knoten.id, variables={"cclom:title": "Photosynthese"})
    assert vorschlag.author, "das Gateway nennt sein Konto nicht"
    await knoten.permissions.grant(vorschlag.author, "Write")
    paare = await vorlagen.qas([knoten.id])
    assert paare, "keine Frage-Antwort-Paare"
    assert all(p.get("question") and p.get("answer") for p in paare)
    assert {p.get("nodeId") for p in paare} == {knoten.id}
