"""Der Metadata Agent -- die Schemata je Inhaltsart.

``ccm:oeh_extendedType`` sagt, WAS eine Ressource ist; ``ccm:oeh_extendedData``
traegt einen freien JSON-Bereich. Welche Felder dort hineingehoeren, steht in
keinem Metadatensatz -- das weiss nur dieser Dienst, und nur zur Laufzeit.

Gemessen am 28.08.2026 gegen Staging und Produktiv, beide gleich. Der Dienst
gibt keine OpenAPI heraus (``/openapi.json`` und ``/docs`` antworten 404); die
Routen stammen aus seinem eigenen Widget-Bundle.
"""

import httpx
import pytest

from edusharing.errors import EduSharingError
from edusharing.metadata_agent import ContentType, MetadataAgent, SchemaInfo

AGENT = "https://agent.example.test"

LISTE = [
    {"file": "core.json", "profile_id": "core:descriptive",
     "label": {"de": "core.json", "en": "core.json"},
     "groups": ["description", "typification"], "field_count": 27},
    {"file": "organization.json", "profile_id": "oeh:organizationLocation",
     "label": {"de": "organization.json", "en": "organization.json"},
     "groups": ["base", "contact"], "field_count": 45},
]

CORE = {
    "profileId": "core:descriptive",
    "version": "2.0.0",
    "groups": ["description", "typification"],
    "fields": [
        {"id": "cclom:title", "group": "description",
         "label": {"de": "Titel", "en": "Title"}},
        {"id": "ccm:oeh_extendedType", "group": "typification",
         "label": {"de": "Inhaltsart(en)", "en": "Content Type(s)"},
         "system": {"vocabulary": {"type": "closed", "concepts": [
             {"label": {"de": "Organisation", "en": "Organization"},
              "icon": "business", "schema_file": "organization.json",
              "uri": "http://w3id.org/openeduhub/vocabs/contentTypes/organization"},
             {"label": {"de": "Person", "en": "Person"},
              "icon": "person", "schema_file": "person.json",
              "uri": "http://w3id.org/openeduhub/vocabs/contentTypes/person"},
         ]}}},
    ],
}


def _agent(handler, **kwargs):
    return MetadataAgent(
        AGENT,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        **kwargs)


def _router(request):
    pfad = request.url.path
    if pfad.endswith("/info/schemas/mds_oeh/latest"):
        return httpx.Response(200, json=LISTE)
    if pfad.endswith("/info/schema/mds_oeh/latest/core.json"):
        return httpx.Response(200, json=CORE)
    return httpx.Response(404, json={"detail": f"Schema not found: {pfad}"})


# --- Adresse ---------------------------------------------------------------

def test_ohne_adresse_wird_verweigert(monkeypatch):
    """Wie bei extraction und bapi: kein Vorgabewert. Eine falsche Adresse
    schickt Inhalte an einen Dienst, den niemand gewaehlt hat."""
    monkeypatch.delenv("METADATA_AGENT_URL", raising=False)
    with pytest.raises(EduSharingError, match="METADATA_AGENT_URL"):
        MetadataAgent.from_env()


def test_eine_adresse_ohne_schema_wird_abgelehnt():
    with pytest.raises(EduSharingError, match="scheme"):
        MetadataAgent("agent.example.test")


# --- Schemaliste -----------------------------------------------------------

async def test_die_liste_nennt_datei_profil_und_feldzahl():
    async with _agent(_router) as agent:
        schemata = await agent.schemas()
    assert [s.file for s in schemata] == ["core.json", "organization.json"]
    assert isinstance(schemata[0], SchemaInfo)
    assert schemata[1].field_count == 45
    assert schemata[1].groups == ("base", "contact")


async def test_kontext_und_version_landen_im_pfad():
    aufrufe = []

    def merken(request):
        aufrufe.append(request)
        return _router(request)

    async with _agent(merken) as agent:
        await agent.schemas(context="mds_oeh", version="latest")
    assert aufrufe[0].url.path == "/info/schemas/mds_oeh/latest"


async def test_eine_unbekannte_version_ist_ein_fehler():
    """Gemessen: der Dienst antwortet 404. Stillschweigend auf latest
    auszuweichen hiesse, Felder einer anderen Fassung zu liefern."""
    async with _agent(_router) as agent:
        with pytest.raises(EduSharingError):
            await agent.schemas(version="gibtsnicht")


# --- Ein Schema ------------------------------------------------------------

async def test_ein_schema_kommt_unveraendert_zurueck():
    """Rohform mit Absicht: ein Schema traegt je Feld Label, Beschreibung,
    Beispiele und einen Extraktions-Prompt in zwei Sprachen. Das in eigene
    Typen zu giessen hiesse, die Struktur eines fremden Dienstes zu erfinden."""
    async with _agent(_router) as agent:
        schema = await agent.schema("core.json")
    assert schema["profileId"] == "core:descriptive"
    assert len(schema["fields"]) == 2


# --- Die Zuordnung Inhaltsart -> Schema ------------------------------------

async def test_inhaltsarten_kommen_aus_core_json():
    """Die maszgebliche Zuordnung steht im Schema selbst, unter
    ccm:oeh_extendedType. Sie nach Dateinamen zu raten ginge schief:
    'profession' heisst 'occupation.json'."""
    async with _agent(_router) as agent:
        arten = await agent.content_types()
    assert all(isinstance(a, ContentType) for a in arten)
    assert [a.schema_file for a in arten] == ["organization.json", "person.json"]
    assert arten[0].label == "Organisation"
    assert arten[0].uri.endswith("/organization")


async def test_schema_zu_einer_uri_finden():
    """Der Weg, den ein Aufrufer wirklich geht: er hat den Wert von
    ccm:oeh_extendedType an einem Knoten und will die Felder dazu."""
    uri = "http://w3id.org/openeduhub/vocabs/contentTypes/person"
    async with _agent(_router) as agent:
        art = await agent.content_type_for(uri)
    assert art is not None
    assert art.schema_file == "person.json"


async def test_eine_unbekannte_uri_ergibt_none():
    """None, kein Fehler: der Metadatensatz fuehrt mehr Inhaltsarten als der
    Agent Schemata hat -- gemessen 10 gegen 8, ohne ai_prompt und ai_skill."""
    async with _agent(_router) as agent:
        assert await agent.content_type_for("http://beispiel.test/gibtsnicht") is None


# --- Die Zuordnung wird nicht bei jedem Aufruf neu geholt -------------------

async def test_die_inhaltsarten_werden_gemerkt():
    """core.json sind 110 kB. Der wahrscheinlichste Aufruf ist eine Schleife
    ueber Knoten -- zwanzig Knoten waeren zwanzigmal 110 kB fuer eine
    Zuordnung, die sich je Version nie aendert."""
    aufrufe = []

    def merken(request):
        aufrufe.append(request.url.path)
        return _router(request)

    async with _agent(merken) as agent:
        for _ in range(3):
            await agent.content_type_for(
                "http://w3id.org/openeduhub/vocabs/contentTypes/person")
    geholt = [p for p in aufrufe if p.endswith("core.json")]
    assert len(geholt) == 1, f"core.json {len(geholt)}x geholt: {aufrufe}"


async def test_verschiedene_versionen_werden_getrennt_gemerkt():
    """Sonst bekaeme die zweite Version die Zuordnung der ersten."""
    aufrufe = []

    def merken(request):
        aufrufe.append(request.url.path)
        return httpx.Response(200, json=CORE)

    async with _agent(merken) as agent:
        await agent.content_types(version="latest")
        await agent.content_types(version="2.0.0")
    assert len(aufrufe) == 2, aufrufe


async def test_clear_cache_erzwingt_ein_neues_holen():
    """Ein lang laufender Prozess auf 'latest' behaelt sonst, was er zuerst
    sah -- wie repo.vocab.clear_cache() gibt es einen Weg heraus."""
    aufrufe = []

    def merken(request):
        aufrufe.append(request.url.path)
        return _router(request)

    async with _agent(merken) as agent:
        await agent.content_types()
        agent.clear_cache()
        await agent.content_types()
    assert len(aufrufe) == 2, aufrufe


# --- Eine strukturelle Ueberraschung bleibt nicht stumm --------------------

async def test_ein_fehlendes_typfeld_ist_ein_fehler():
    """Frueher kam hier eine leere Liste zurueck -- ununterscheidbar von
    'dieser Agent fuehrt keine Inhaltsarten'. Benennt der Dienst das Feld um,
    muss die Bibliothek das sagen, nicht schweigen."""
    ohne = {"profileId": "core:descriptive", "version": "2.0.0",
            "fields": [{"id": "cclom:title", "group": "description"}]}

    async with _agent(lambda r: httpx.Response(200, json=ohne)) as agent:
        with pytest.raises(EduSharingError, match="ccm:oeh_extendedType"):
            await agent.content_types()


async def test_eine_antwort_die_keine_liste_ist_ist_ein_fehler():
    """Dasselbe fuer die Schemaliste: aus einer unerwarteten Form darf keine
    leere werden."""
    async with _agent(lambda r: httpx.Response(200, json={"nanu": 1})) as agent:
        with pytest.raises(EduSharingError, match="list"):
            await agent.schemas()


# --- Was die Durchsicht als ungetestet ausgewiesen hat ---------------------

def test_from_env_nimmt_die_adresse_aus_der_umgebung(monkeypatch):
    monkeypatch.setenv("METADATA_AGENT_URL", "https://agent.example.test/")
    agent = MetadataAgent.from_env()
    assert agent.base_url == "https://agent.example.test"


def test_lesbare_darstellung():
    """repr taucht in Fehlermeldungen und Protokollen auf."""
    assert repr(MetadataAgent(AGENT)) == f"MetadataAgent({AGENT!r})"


async def test_ein_netzfehler_wird_zu_einem_edusharingerror():
    """Sonst schlaegt httpx bis zum Aufrufer durch, und der muss zwei
    Fehlerfamilien kennen."""
    def kaputt(_request):
        raise httpx.ConnectError("kein Netz")

    async with _agent(kaputt) as agent:
        with pytest.raises(EduSharingError, match="ConnectError"):
            await agent.schemas()
