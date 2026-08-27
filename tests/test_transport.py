"""Der eine Weg nach draussen.

Drei Dinge werden hier geprueft, weil sie sonst niemand prueft: dass das
Passwort nur an das konfigurierte Repositorium geht, dass eine Anfrage nur
dann wiederholt wird, wenn eine Wiederholung ueberhaupt gelingen kann, und
dass die Gleichzeitigkeit begrenzt bleibt.
"""

import asyncio

import httpx
import pytest

from edusharing.auth import ANONYMOUS, BasicCredential
from edusharing.errors import (
    AuthenticationError,
    EduSharingError,
    NotFoundError,
    ServerError,
    TransportError,
)
from edusharing.transport import Transport

REPO = "https://repository.staging.openeduhub.net/edu-sharing"
CRED = BasicCredential("alice", "geheim")


def _transport(handler, **kwargs):
    """Transport mit einem Handler statt echtem Netz. Backoff auf 0, damit die
    Tests nicht auf Wartezeiten warten."""
    kwargs.setdefault("credential", CRED)
    kwargs.setdefault("backoff_base", 0.0)
    return Transport(
        REPO,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)),
        **kwargs,
    )


def _ok(_request: httpx.Request) -> httpx.Response:
    return httpx.Response(200, json={"ok": True})


# --- Wohin das Passwort geht ----------------------------------------------

async def test_auth_geht_an_das_repositorium():
    gesehen = {}

    def handler(request):
        gesehen["auth"] = request.headers.get("authorization")
        return httpx.Response(200, json={})

    async with _transport(handler) as t:
        await t.request("GET", "/_about")
    assert gesehen["auth"] is not None
    assert gesehen["auth"].startswith("Basic ")


async def test_auth_geht_nicht_an_fremde_hosts():
    """Absolute URLs kommen auch aus Antwortdaten -- eine Vorschau-URL etwa.
    Wenn eine davon woanders hinzeigt, darf das Passwort nicht mitgehen."""
    gesehen = {}

    def handler(request):
        gesehen["auth"] = request.headers.get("authorization")
        return httpx.Response(200, content=b"")

    async with _transport(handler) as t:
        await t.request("GET", "https://fremder-host.test/etwas")
    assert gesehen["auth"] is None


async def test_auth_geht_nicht_an_aehnlich_aussehende_hosts():
    """Ein blosser Praefix-Vergleich wuerde hier zuschlagen: die fremde Adresse
    beginnt exakt mit der eigenen."""
    gesehen = {}

    def handler(request):
        gesehen["auth"] = request.headers.get("authorization")
        return httpx.Response(200, content=b"")

    async with _transport(handler) as t:
        await t.request("GET", f"{REPO}.angreifer.test/etwas")
    assert gesehen["auth"] is None


async def test_relative_pfade_gehen_an_die_rest_basis():
    gesehen = {}

    def handler(request):
        gesehen["url"] = str(request.url)
        return httpx.Response(200, json={})

    async with _transport(handler) as t:
        await t.request("GET", "/_about")
    assert gesehen["url"] == f"{REPO}/rest/_about"


async def test_zugangsdaten_pro_anfrage_ueberschreibbar():
    """Ein Dienst, der viele Nutzende bedient, braucht das pro Anfrage --
    ein globaler Zustand wuerde Anfragen vermischen."""
    gesehen = []

    def handler(request):
        gesehen.append(request.headers.get("authorization"))
        return httpx.Response(200, json={})

    async with _transport(handler) as t:
        await t.request("GET", "/_about")
        await t.request("GET", "/_about", credential=ANONYMOUS)
        await t.request("GET", "/_about", credential=BasicCredential("bob", "x"))
    assert gesehen[0] is not None
    assert gesehen[1] is None
    assert gesehen[2] is not None
    assert gesehen[0] != gesehen[2]


# --- Was wiederholt wird, und was nicht -----------------------------------

async def test_502_wird_wiederholt():
    """Cloudflare-Timeouts und Saettigung stromaufwaerts sind voruebergehend."""
    versuche = []

    def handler(request):
        versuche.append(1)
        return httpx.Response(502, content=b"<html>error code: 522</html>")

    async with _transport(handler, max_retries=2) as t:
        with pytest.raises(ServerError):
            await t.request("GET", "/_about")
    assert len(versuche) == 3          # ein Versuch + zwei Wiederholungen


async def test_erfolg_nach_wiederholung():
    versuche = []

    def handler(request):
        versuche.append(1)
        if len(versuche) < 3:
            return httpx.Response(503, content=b"")
        return httpx.Response(200, json={"ok": True})

    async with _transport(handler, max_retries=3) as t:
        antwort = await t.request("GET", "/_about")
    assert antwort.status_code == 200
    assert len(versuche) == 3


async def test_500_not_allowed_for_guest_wird_nicht_wiederholt():
    """Der Kernfall. Gemessen: fehlende Anmeldung kommt als HTTP 500 mit
    "Not allowed for guest user". Ein Retry darauf ist dreimal dieselbe
    Anfrage, die nie gelingen kann -- und dreimal Last auf einem
    Repositorium, das gar nichts falsch gemacht hat."""
    versuche = []

    def handler(request):
        versuche.append(1)
        return httpx.Response(500, json={
            "error": "java.lang.Exception",
            "message": "Not allowed for guest user",
        })

    async with _transport(handler, max_retries=3) as t:
        with pytest.raises(AuthenticationError):
            await t.request("GET", "/iam/v1/people/-home-/-me-/preferences")
    assert len(versuche) == 1


@pytest.mark.parametrize("status", [400, 401, 403, 404, 409])
async def test_fehler_der_anfrage_werden_nicht_wiederholt(status):
    versuche = []

    def handler(request):
        versuche.append(1)
        return httpx.Response(status, json={"error": "x", "message": "y"})

    async with _transport(handler, max_retries=3) as t:
        with pytest.raises(EduSharingError):
            await t.request("GET", "/_about")
    assert len(versuche) == 1


async def test_404_ergibt_notfounderror():
    def handler(request):
        return httpx.Response(404, json={
            "error": "org.edu_sharing.restservices.DAOMissingException",
            "message": "Node does not exist",
        })

    async with _transport(handler) as t:
        with pytest.raises(NotFoundError):
            await t.request("GET", "/node/v1/nodes/-home-/x/metadata")


# --- Netzwerkfehler -------------------------------------------------------

async def test_timeout_wird_transport_error():
    """Abgegrenzt von ServerError: bei einem Timeout ist unklar, ob etwas
    passiert ist. Fuer einen Schreibvorgang ist das ein Unterschied."""
    def handler(request):
        raise httpx.ReadTimeout("zu langsam", request=request)

    async with _transport(handler, max_retries=1) as t:
        with pytest.raises(TransportError):
            await t.request("GET", "/_about")


async def test_timeout_wird_wiederholt():
    versuche = []

    def handler(request):
        versuche.append(1)
        if len(versuche) < 2:
            raise httpx.ConnectError("weg", request=request)
        return httpx.Response(200, json={})

    async with _transport(handler, max_retries=2) as t:
        antwort = await t.request("GET", "/_about")
    assert antwort.status_code == 200
    assert len(versuche) == 2


# --- Gleichzeitigkeit -----------------------------------------------------

async def test_gleichzeitigkeit_ist_begrenzt():
    """Ohne Begrenzung erschlaegt ein Fan-out ueber viele Knoten das
    Repositorium -- gemessen liegt dessen Grenze niedriger, als eine
    unbegrenzte Schleife erzeugt."""
    laufend = 0
    hoechststand = 0

    async def handler(request):
        nonlocal laufend, hoechststand
        laufend += 1
        hoechststand = max(hoechststand, laufend)
        await asyncio.sleep(0.01)
        laufend -= 1
        return httpx.Response(200, json={})

    async with _transport(handler, max_concurrency=3) as t:
        await asyncio.gather(*(t.request("GET", "/_about") for _ in range(12)))
    assert hoechststand <= 3


# --- JSON-Bequemlichkeit --------------------------------------------------

async def test_json_gibt_den_geparsten_koerper():
    async with _transport(lambda r: httpx.Response(200, json={"a": 1})) as t:
        assert await t.json("GET", "/_about") == {"a": 1}
