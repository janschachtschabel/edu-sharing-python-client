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
from edusharing.transport import DEFAULT_TIMEOUT, Transport

REPO = "https://repositorium.example.test/edu-sharing"
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


@pytest.mark.parametrize("status", [400, 403, 404, 409])
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


# --- Der eine 401, der doch wiederholt wird -------------------------------
#
# 401 stand bis zum 28.08.2026 in der Liste oben. Er steht dort nicht mehr,
# weil die Liste zwei Behauptungen in einer war. Gemessen gegen Staging mit
# gueltiger Anmeldung, 20 Knoten je Runde, 5 Runden:
#
#     nacheinander   0 von 100 Anfragen mit 401
#     gleichzeitig   9 von 100 Anfragen mit 401
#
# Dieselben Knoten, dieselben Zugangsdaten. Ein 401 unter Gleichzeitigkeit ist
# also keine Aussage ueber die Zugangsdaten, sondern ueber den Moment -- und er
# trifft jeden Stapel-Ablauf dieser Bibliothek.

async def test_401_mit_anmeldung_wird_einmal_wiederholt():
    versuche = []

    def handler(request):
        versuche.append(1)
        if len(versuche) == 1:
            return httpx.Response(401, json={"error": "x", "message": "nope"})
        return httpx.Response(200, json={"ok": True})

    async with _transport(handler, max_retries=3) as t:
        antwort = await t.request("GET", "/_about")
    assert antwort.status_code == 200
    assert len(versuche) == 2


async def test_401_wird_hoechstens_einmal_wiederholt():
    """Falsche Zugangsdaten duerfen nicht max_retries mal kosten -- ein
    zusaetzlicher Versuch ist der Preis fuer den gemessenen Ausrutscher, drei
    waeren eine Strafe fuer einen Tippfehler im Passwort."""
    versuche = []

    def handler(request):
        versuche.append(1)
        return httpx.Response(401, json={"error": "x", "message": "nope"})

    async with _transport(handler, max_retries=3) as t:
        with pytest.raises(AuthenticationError):
            await t.request("GET", "/_about")
    assert len(versuche) == 2


async def test_401_ohne_wiederholungsbudget_bleibt_bei_einem_versuch():
    versuche = []

    def handler(request):
        versuche.append(1)
        return httpx.Response(401, json={"error": "x", "message": "nope"})

    async with _transport(handler, max_retries=0) as t:
        with pytest.raises(AuthenticationError):
            await t.request("GET", "/_about")
    assert len(versuche) == 1


async def test_401_ohne_anmeldung_wird_nicht_wiederholt():
    """Anonym heisst 401 "hierfuer braucht es eine Anmeldung". Das wird beim
    zweiten Mal nicht anders."""
    versuche = []

    def handler(request):
        versuche.append(1)
        return httpx.Response(401, json={"error": "x", "message": "nope"})

    async with _transport(handler, credential=ANONYMOUS, max_retries=3) as t:
        with pytest.raises(AuthenticationError):
            await t.request("GET", "/_about")
    assert len(versuche) == 1


async def test_als_401_verkleideter_500_wird_nicht_wiederholt():
    """Der gemessene Ausrutscher ist ein echter 401-Status. Das "Not allowed
    for guest" im 500er ist eine Aussage ueber die Anmeldung und bleibt bei
    einem Versuch -- sonst waere der Sinn der Uebersetzung wieder dahin."""
    versuche = []

    def handler(request):
        versuche.append(1)
        return httpx.Response(500, json={
            "error": "java.lang.Exception",
            "message": "Not allowed for guest user",
        })

    async with _transport(handler, max_retries=3) as t:
        with pytest.raises(AuthenticationError):
            await t.request("GET", "/_about")
    assert len(versuche) == 1


# --- Umleitungen (Audit A8) -----------------------------------------------

async def test_eine_umleitung_ist_kein_erfolg():
    """``status_code < 400`` liess jede 3xx als Erfolg durch. Dieser Client
    folgt Umleitungen nicht -- ``follow_redirects`` bleibt bei der Vorgabe
    ``False`` --, also kam der leere Koerper der Umleitung zurueck. Bei
    ``Content.download`` sind das null Bytes statt der Datei, still.

    Gemessen am 28.08.2026 gegen Staging: acht Downloads, null Umleitungen --
    auf dieser Instanz also nicht ausgeloest. Hinter einem Proxy, der auf eine
    Anmeldeseite umlenkt, oder bei Inhalten von einem CDN schon.
    """
    def handler(_request):
        return httpx.Response(302, headers={"Location": "https://cdn.test/datei.pdf"})

    async with _transport(handler) as t:
        with pytest.raises(EduSharingError) as info:
            await t.request("GET", "/node/v1/nodes/-home-/abc/content")
    assert info.value.status == 302
    assert "cdn.test" in str(info.value), "die Umleitung gehoert in die Meldung"


async def test_eine_umleitung_wird_nicht_wiederholt():
    """Eine Umleitung ist eine Aussage, keine Stoerung."""
    versuche = []

    def handler(_request):
        versuche.append(1)
        return httpx.Response(301, headers={"Location": "https://anderswo.test/"})

    async with _transport(handler, max_retries=3) as t:
        with pytest.raises(EduSharingError):
            await t.request("GET", "/_about")
    assert len(versuche) == 1


async def test_eine_umleitung_ohne_location_wird_trotzdem_gemeldet():
    def handler(_request):
        return httpx.Response(304)

    async with _transport(handler) as t:
        with pytest.raises(EduSharingError):
            await t.request("GET", "/_about")


async def test_zweihundert_bleibt_erfolg():
    """Gegenprobe: die neue Grenze darf den Normalfall nicht treffen."""
    async with _transport(_ok) as t:
        assert (await t.request("GET", "/_about")).status_code == 200


# --- Parameter, die nichts taten (Audit A11, A14) -------------------------

async def test_ein_eigener_client_bringt_sein_eigenes_zeitlimit_mit():
    """``timeout`` wurde geprueft und dann verworfen, sobald ein Client
    uebergeben wurde -- gemessen: ``timeout=0.5`` ergab ``Timeout(5.0)``, die
    httpx-Vorgabe. Wer fuer einen latenzkritischen Pfad kurz stellt, bekam
    still die Vorgabe. Das Zeitlimit gehoert dem Client, also sagt es die
    Bibliothek, statt es anzunehmen."""
    eigener = httpx.AsyncClient(timeout=1.5)
    with pytest.raises(EduSharingError, match="timeout"):
        Transport(REPO, timeout=0.5, client=eigener)
    await eigener.aclose()


async def test_ein_eigener_client_ohne_zeitlimitangabe_ist_erlaubt():
    """Gegenprobe: nur die *widerspruechliche* Angabe wird abgelehnt."""
    eigener = httpx.AsyncClient(timeout=1.5)
    t = Transport(REPO, client=eigener)
    assert t._client.timeout.read == 1.5
    await eigener.aclose()


@pytest.mark.parametrize("wert", ["schnell", float("nan"), [1]])
def test_unbrauchbare_zahlenwerte_werden_als_bibliotheksfehler_abgelehnt(wert):
    """``at_least`` verglich blind. Ein Nicht-Zahlenwert gab einen TypeError
    statt eines EduSharingError -- die Bibliothek deckte ihre eigene Eingabe
    nicht mit ihrem eigenen Fehlertyp ab. Und ``nan`` kam durch, weil jeder
    Vergleich mit nan falsch ist; httpx bekam dann ein Zeitlimit, das nie
    ablaeuft."""
    with pytest.raises(EduSharingError):
        Transport(REPO, timeout=wert)


@pytest.mark.parametrize("wert", [None, "drei", float("nan")])
def test_unbrauchbare_wiederholungszahlen_ebenso(wert):
    """Dieselbe Pruefung, ein anderer Parameter -- ``max_retries`` hat keinen
    None-Sonderfall, hier bleibt None ein Fehler."""
    with pytest.raises(EduSharingError):
        Transport(REPO, max_retries=wert)


def test_timeout_none_heisst_vorgabe():
    """Die Gegenprobe zum neuen Sonderfall: ``None`` ist die Art zu sagen
    "nimm die Vorgabe", nicht ein unbrauchbarer Wert."""
    t = Transport(REPO, timeout=None)
    assert t._client.timeout.read == DEFAULT_TIMEOUT


async def test_verborgene_details_werden_nur_einmal_wiederholt():
    """Gemessen am 28.08.2026 gegen redaktion.openeduhub.net.

    Eine Instanz kann ihre Fehlermeldungen zurueckhalten
    (``security.logging.displayLevel``). Die 5xx-Einordnung liest genau diesen
    Text, also bleibt ein verkleidetes "nicht angemeldet" ein ServerError --
    und der wird wiederholt. Gemessen an derselben Adresse: **4 Anfragen gegen
    Produktiv, 1 gegen Staging**.

    Einordnen laesst sich das nicht; was der Server verschweigt, kann die
    Bibliothek nicht erraten. Die Wiederholung deckeln schon, und zwar nach dem
    Muster, das dieser Transport fuer den 401 unter Nebenlaeufigkeit bereits
    gewaehlt hat: einmal, nicht ``max_retries``-mal. Eine zusaetzliche Anfrage
    ist ein fairer Preis fuer einen moeglicherweise voruebergehenden Fehler;
    drei sind eine Strafe dafuer, dass die Instanz schweigt.
    """
    versuche = []

    def handler(_request):
        versuche.append(1)
        return httpx.Response(500, json={
            "error": "java.lang.Exception",
            "message": "Details hidden: You can configure the output via "
                       "security.logging.displayLevel",
        })

    async with _transport(handler, max_retries=3) as t:
        with pytest.raises(ServerError):
            await t.request("GET", "/_about")
    assert len(versuche) == 2, (
        f"erwartet ein Versuch plus eine Wiederholung, waren {len(versuche)}")


async def test_ein_gewoehnlicher_500_wird_weiter_voll_wiederholt():
    """Der Deckel gilt nur dort, wo die Meldung fehlt -- sonst waere er eine
    stille Verschlechterung der Fehlertoleranz fuer alle anderen."""
    versuche = []

    def handler(_request):
        versuche.append(1)
        return httpx.Response(500, json={"error": "java.lang.Exception",
                                         "message": "Something genuinely broke"})

    async with _transport(handler, max_retries=3) as t:
        with pytest.raises(ServerError):
            await t.request("GET", "/_about")
    assert len(versuche) == 4
