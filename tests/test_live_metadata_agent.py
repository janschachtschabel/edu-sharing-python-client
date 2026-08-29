"""Tests gegen einen echten Metadata Agent.

    METADATA_AGENT_URL=https://metadata-agent-canvas.staging.openeduhub.net \
        uv run pytest -m live

Beantworten die Frage, die Mocks nicht koennen: stimmt unser Bild vom Dienst
noch? Er gibt keine OpenAPI heraus, seine Routen sind aus dem Widget-Bundle
gelesen -- aendert er sie, faellt es nur hier auf.
"""

import os

import pytest

from edusharing.metadata_agent import MetadataAgent

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not os.environ.get("METADATA_AGENT_URL"),
        reason="METADATA_AGENT_URL nicht gesetzt",
    ),
]


@pytest.fixture
async def agent():
    async with MetadataAgent.from_env() as a:
        yield a


async def test_die_schemaliste_kommt(agent):
    schemata = await agent.schemas()
    assert schemata, "keine Schemata gemeldet"
    assert any(s.file == "core.json" for s in schemata), \
        f"core.json fehlt: {[s.file for s in schemata]}"
    assert all(s.field_count > 0 for s in schemata), "ein Schema ohne Felder"


async def test_beide_kontexte_antworten(agent):
    """default und mds_oeh -- die einzigen beiden, laut Widget-Doku."""
    for kontext in ("default", "mds_oeh"):
        assert await agent.schemas(context=kontext), f"{kontext} leer"


async def test_eine_unbekannte_version_wirft(agent):
    """Kein stilles Ausweichen auf latest -- sonst kaemen Felder einer
    anderen Fassung zurueck, ohne dass jemand es merkt."""
    from edusharing.errors import EduSharingError

    with pytest.raises(EduSharingError):
        await agent.schemas(version="gibtsnicht-9.9.9")


async def test_ein_schema_traegt_felder_mit_prompts(agent):
    """Der Grund, warum das hier roh zurueckkommt: jedes Feld fuehrt Label,
    Beschreibung, Beispiele UND einen Extraktions-Prompt, je zweisprachig."""
    schema = await agent.schema("core.json")
    felder = schema.get("fields") or []
    assert felder, "core.json ohne Felder"
    mit_prompt = [f for f in felder if f.get("prompt")]
    assert mit_prompt, "kein einziges Feld mit Extraktions-Prompt"
    erstes = mit_prompt[0]
    assert set(erstes["prompt"]) >= {"de", "en"}, erstes["prompt"].keys()


async def test_die_inhaltsarten_zeigen_auf_ihre_schemata(agent):
    arten = await agent.content_types()
    assert arten, "keine Inhaltsarten gemeldet"
    dateien = {s.file for s in await agent.schemas()}
    for art in arten:
        assert art.uri.startswith("http"), art
        assert art.schema_file in dateien, \
            f"{art.uri} zeigt auf {art.schema_file}, das es nicht gibt"


async def test_eine_umbenannte_inhaltsart_wird_richtig_zugeordnet(agent):
    """'profession' heisst beim Agent 'occupation.json'. Wer nach Dateinamen
    raet, findet nichts -- gemessen am 28.08.2026."""
    uri = "http://w3id.org/openeduhub/vocabs/contentTypes/profession"
    art = await agent.content_type_for(uri)
    if art is None:
        pytest.skip("dieser Agent fuehrt 'profession' nicht")
    assert art.schema_file == "occupation.json", art.schema_file


async def test_eine_unbekannte_uri_ergibt_none(agent):
    """Der Metadatensatz fuehrt mehr Inhaltsarten als der Agent Schemata hat --
    gemessen 10 gegen 8. Das ist kein Fehler, sondern der Normalfall."""
    assert await agent.content_type_for("http://beispiel.test/gibtsnicht") is None
