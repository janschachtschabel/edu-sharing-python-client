"""Tests gegen ein echtes Repositorium.

Laufen nur mit ``pytest -m live`` und gesetztem ``EDU_SHARING_URL``. Alles
andere in dieser Suite kommt ohne Netz aus; diese Tests beantworten die eine
Frage, die Mocks nicht beantworten koennen: stimmt unser Bild vom Server noch?

    EDU_SHARING_URL=https://repository.staging.openeduhub.net uv run pytest -m live
"""

import os

import pytest

from edusharing import AsyncRepository
from edusharing.errors import AuthenticationError, NotFoundError

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not os.environ.get("EDU_SHARING_URL"),
        reason="EDU_SHARING_URL nicht gesetzt",
    ),
]

FEHLENDE_NODE = "00000000-0000-0000-0000-000000000000"


@pytest.fixture
async def repo():
    async with AsyncRepository.from_env() as r:
        yield r


async def test_about_liefert_eine_version(repo):
    about = await repo.about()
    assert about.repository_version, "Instanz meldet keine Repository-Version"
    assert about.services, "Instanz meldet keine Dienste"


async def test_whoami_beantwortet_wer_ich_bin(repo):
    wer = await repo.whoami()
    assert wer.authority, "keine Authority zurueckbekommen"
    # Ohne Zugangsdaten muss die Antwort anonym lauten -- alles andere hiesse,
    # dass die Bibliothek unbemerkt fremde Zugangsdaten mitschickt.
    if repo.credential.is_anonymous:
        assert wer.is_anonymous, f"anonym angefragt, aber als {wer.authority!r} angemeldet"


async def test_unbekannte_node_ergibt_notfounderror(repo):
    with pytest.raises(NotFoundError):
        await repo.raw.json("GET", f"/node/v1/nodes/-home-/{FEHLENDE_NODE}/metadata")


async def test_geschuetzter_endpunkt_ergibt_authenticationerror(repo):
    """Der Kernfall, live nachgewiesen.

    ``/iam/v1/people/-home-/-me-/preferences`` antwortet einem Gast mit
    **HTTP 500** und "Not allowed for guest user". Die Bibliothek muss daraus
    einen Authentifizierungsfehler machen -- und darf die Anfrage nicht
    wiederholen.
    """
    if not repo.credential.is_anonymous:
        pytest.skip("nur als Gast aussagekraeftig")
    with pytest.raises(AuthenticationError):
        await repo.raw.json("GET", "/iam/v1/people/-home-/-me-/preferences")


async def test_falsche_zugangsdaten_ergeben_authenticationerror():
    """Gemessen: edu-sharing faellt bei falschen Zugangsdaten NICHT auf
    oeffentliches Lesen zurueck, sondern antwortet ueberall mit 401."""
    async with AsyncRepository(
        os.environ["EDU_SHARING_URL"],
        auth=("kein-solcher-nutzer", "falsches-passwort"),
    ) as r:
        with pytest.raises(AuthenticationError):
            await r.whoami()
