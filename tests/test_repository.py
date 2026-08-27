"""Die oeffentliche Oberflaeche: verbinden, nachsehen, wer man ist.

Die Antwortformen stammen aus Messungen gegen edu-sharing 11.0 (Staging,
27.08.2026).
"""

import asyncio

import httpx
import pytest

from edusharing import AsyncRepository, Repository
from edusharing.errors import EduSharingError

REPO = "https://repository.staging.openeduhub.net/edu-sharing"

# Gemessene Antwort von GET /_about, auf das Wesentliche gekuerzt.
ABOUT = {
    "version": {"repository": "11.0", "renderservice": "11.0", "major": 1, "minor": 1},
    "services": [{"name": "IAM"}, {"name": "NODE"}],
    "plugins": [{"id": "mongo-plugin"}, {"id": "b-api"}],
    "features": [{"id": "handleService"}],
    "themesUrl": f"{REPO}/themes/default/",
}

# Gemessene Antwort von GET /iam/v1/people/-home-/-me- ohne Zugangsdaten.
ME_GUEST = {"person": {"authorityName": "esguest", "userName": "esguest",
                       "authorityType": "USER", "profile": {}}}
ME_ALICE = {"person": {"authorityName": "alice", "userName": "alice",
                       "authorityType": "USER",
                       "profile": {"firstName": "Alice", "lastName": "Beispiel"}}}


def _handler(routes: dict[str, dict]):
    def handle(request: httpx.Request) -> httpx.Response:
        for fragment, payload in routes.items():
            if fragment in str(request.url):
                return httpx.Response(200, json=payload)
        return httpx.Response(404, json={"error": "x", "message": "nicht gemockt"})
    return handle


def _repo(routes, **kwargs):
    return AsyncRepository(
        REPO,
        client=httpx.AsyncClient(transport=httpx.MockTransport(_handler(routes))),
        **kwargs,
    )


# --- about ----------------------------------------------------------------

async def test_about_liefert_die_version():
    async with _repo({"/_about": ABOUT}) as repo:
        about = await repo.about()
    assert about.repository_version == "11.0"
    assert about.renderservice_version == "11.0"


async def test_about_listet_dienste_und_plugins():
    """Womit eine Anwendung pruefen kann, was diese Instanz ueberhaupt kann --
    die Voraussetzung dafuer, nicht von einer bestimmten Instanz auszugehen."""
    async with _repo({"/_about": ABOUT}) as repo:
        about = await repo.about()
    assert "IAM" in about.services
    assert "b-api" in about.plugins
    assert "handleService" in about.features


async def test_about_vertraegt_fehlende_felder():
    """Aeltere oder anders konfigurierte Instanzen liefern nicht alles."""
    async with _repo({"/_about": {"version": {"repository": "9.1"}}}) as repo:
        about = await repo.about()
    assert about.repository_version == "9.1"
    assert about.services == []
    assert about.plugins == []


# --- whoami ---------------------------------------------------------------

async def test_whoami_erkennt_den_gast():
    """"Bin ich, wer ich denke?" -- ohne diese Probe merkt eine Anwendung
    nicht, mit welchen Rechten sie laeuft. edu-sharing nennt den anonymen
    Zugriff 'esguest'."""
    async with _repo({"-me-": ME_GUEST}) as repo:
        wer = await repo.whoami()
    assert wer.is_anonymous is True
    assert wer.authority == "esguest"


async def test_whoami_erkennt_den_angemeldeten_nutzer():
    async with _repo({"-me-": ME_ALICE}, auth=("alice", "geheim")) as repo:
        wer = await repo.whoami()
    assert wer.is_anonymous is False
    assert wer.authority == "alice"
    assert wer.display_name == "Alice Beispiel"


async def test_whoami_ohne_profil_faellt_auf_die_authority_zurueck():
    async with _repo({"-me-": ME_GUEST}) as repo:
        wer = await repo.whoami()
    assert wer.display_name == "esguest"


# --- Konfiguration --------------------------------------------------------

async def test_url_wird_normalisiert():
    async with AsyncRepository("repository.staging.openeduhub.net") as repo:
        assert repo.url == REPO


def test_from_env_braucht_eine_url(monkeypatch):
    monkeypatch.delenv("EDU_SHARING_URL", raising=False)
    with pytest.raises(EduSharingError, match="EDU_SHARING_URL"):
        AsyncRepository.from_env()


def test_from_env_nimmt_url_und_zugangsdaten(monkeypatch):
    monkeypatch.setenv("EDU_SHARING_URL", REPO)
    monkeypatch.setenv("EDU_SHARING_USER", "alice")
    monkeypatch.setenv("EDU_SHARING_PASSWORD", "geheim")
    repo = AsyncRepository.from_env()
    assert repo.url == REPO
    assert repo.credential.is_anonymous is False


def test_from_env_ohne_zugangsdaten_ist_anonym(monkeypatch):
    monkeypatch.setenv("EDU_SHARING_URL", REPO)
    monkeypatch.delenv("EDU_SHARING_USER", raising=False)
    monkeypatch.delenv("EDU_SHARING_PASSWORD", raising=False)
    assert AsyncRepository.from_env().credential.is_anonymous is True


def test_from_env_gilt_auch_synchron(monkeypatch):
    """Beide Zugaenge lesen dieselbe Umgebung -- sonst haengt das Verhalten
    davon ab, welchen man erwischt."""
    monkeypatch.setenv("EDU_SHARING_URL", REPO)
    monkeypatch.delenv("EDU_SHARING_USER", raising=False)
    monkeypatch.delenv("EDU_SHARING_PASSWORD", raising=False)
    repo = Repository.from_env()
    try:
        assert repo.url == REPO
        assert repo.credential.is_anonymous is True
    finally:
        repo.close()


def test_from_env_synchron_braucht_ebenfalls_eine_url(monkeypatch):
    monkeypatch.delenv("EDU_SHARING_URL", raising=False)
    with pytest.raises(EduSharingError, match="EDU_SHARING_URL"):
        Repository.from_env()


def test_from_env_meldung_nennt_die_passende_klasse(monkeypatch):
    """Die Meldung schlaegt einen Aufruf vor -- der muss zu dem Zugang passen,
    den die aufrufende Person gerade benutzt."""
    monkeypatch.delenv("EDU_SHARING_URL", raising=False)
    with pytest.raises(EduSharingError, match="AsyncRepository"):
        AsyncRepository.from_env()
    with pytest.raises(EduSharingError, match=r"\bRepository\("):
        Repository.from_env()


# --- Parameter, die keinen Sinn ergeben -----------------------------------

@pytest.mark.parametrize("kwargs", [
    {"max_retries": -1},
    {"max_concurrency": 0},
    {"max_concurrency": -3},
    {"timeout": 0},
    {"backoff_base": -1.0},
])
def test_unsinnige_parameter_werden_beim_bauen_abgelehnt(kwargs):
    """Frueh und laut, statt spaeter und raetselhaft: max_retries=-1 wuerde
    die Wiederholungsschleife gar nicht erst betreten und einen Fehler ohne
    jede Ursache liefern."""
    with pytest.raises(EduSharingError):
        AsyncRepository(REPO, **kwargs)


def test_bearer_wird_beim_verbinden_abgelehnt():
    """Nicht erst beim ersten Aufruf, sondern sofort -- sonst laeuft die
    Anwendung unbemerkt als Gast weiter."""
    with pytest.raises(EduSharingError, match="Bearer"):
        AsyncRepository(REPO, auth="Bearer eyJhbGciOiJIUzI1NiJ9.abc")


# --- Der synchrone Zugang -------------------------------------------------

def test_synchron_ohne_asyncio():
    """Fuer Skripte und Notebooks: kein asyncio.run() noetig."""
    repo = Repository(
        REPO,
        client=httpx.AsyncClient(transport=httpx.MockTransport(_handler({"/_about": ABOUT}))),
    )
    try:
        assert repo.about().repository_version == "11.0"
    finally:
        repo.close()


def test_synchron_als_kontextmanager():
    with Repository(
        REPO,
        client=httpx.AsyncClient(transport=httpx.MockTransport(_handler({"-me-": ME_GUEST}))),
    ) as repo:
        assert repo.whoami().is_anonymous is True


async def test_synchron_funktioniert_auch_bei_laufendem_event_loop():
    """Der Jupyter-Fall. Ein Notebook betreibt bereits einen Event-Loop; ein
    Wrapper, der einfach asyncio.run() aufriefe, wuerde dort scheitern -- also
    genau bei der Zielgruppe, fuer die der synchrone Zugang gedacht ist."""
    assert asyncio.get_running_loop() is not None
    with Repository(
        REPO,
        client=httpx.AsyncClient(transport=httpx.MockTransport(_handler({"/_about": ABOUT}))),
    ) as repo:
        # Der Aufruf laeuft in einem eigenen Thread, nicht im laufenden Loop.
        antwort = await asyncio.to_thread(lambda: repo.about().repository_version)
    assert antwort == "11.0"
