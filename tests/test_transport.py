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
    ContentTooLargeError,
    EduSharingError,
    NotFoundError,
    RateLimitedError,
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


# --- Was nach dem Senden wiederholt werden darf ----------------------------
#
# Audit-Befund COR-1 (03.09.2026): ein Timeout nach dem Senden und ein 5xx
# lassen offen, ob der Server die Anfrage ausgefuehrt hat. Ein zweites POST
# legt dann ein zweites Kind an, haengt ein zweites Schlagwort an. Vor dem
# Senden ist dagegen nichts passiert -- da darf jede Methode nochmal.

WRITE = "/node/v1/nodes/-home-/abc/children"


def _erst_scheitern(fehler):
    """Handler, der beim ersten Aufruf scheitert -- mit einem Status (int)
    oder einer httpx-Ausnahme (Klasse) -- und danach 200 sagt."""
    versuche = []

    def handler(request):
        versuche.append(1)
        if len(versuche) < 2:
            if isinstance(fehler, int):
                return httpx.Response(fehler, text="")
            raise fehler("scheitert", request=request)
        return httpx.Response(200, json={})

    return handler, versuche


async def test_ein_post_wird_nach_lesetimeout_nicht_wiederholt():
    """Nach dem Senden weiss niemand, ob das Kind schon angelegt ist. Die
    Meldung sagt das, damit der Aufrufer nachsieht statt nochmal zu senden."""
    handler, versuche = _erst_scheitern(httpx.ReadTimeout)

    async with _transport(handler, max_retries=2) as t:
        with pytest.raises(TransportError, match="may already have been carried out"):
            await t.request("POST", WRITE)
    assert len(versuche) == 1


async def test_ein_post_wird_nach_5xx_nicht_wiederholt():
    handler, versuche = _erst_scheitern(502)

    async with _transport(handler, max_retries=2) as t:
        with pytest.raises(ServerError):
            await t.request("POST", WRITE)
    assert len(versuche) == 1


async def test_ein_delete_wird_nach_lesetimeout_nicht_wiederholt():
    """Ein zweites DELETE liefe in ein 404, das der Aufrufer fuer die Wahrheit
    hielte: "gab es nie" statt "ist gerade weg"."""
    handler, versuche = _erst_scheitern(httpx.ReadTimeout)

    async with _transport(handler, max_retries=2) as t:
        with pytest.raises(TransportError):
            await t.request("DELETE", "/node/v1/nodes/-home-/abc")
    assert len(versuche) == 1


async def test_ein_verbindungsfehler_wird_auch_bei_post_wiederholt():
    handler, versuche = _erst_scheitern(httpx.ConnectError)

    async with _transport(handler, max_retries=2) as t:
        antwort = await t.request("POST", WRITE)
    assert antwort.status_code == 200
    assert len(versuche) == 2


async def test_ein_get_wird_nach_lesetimeout_weiter_wiederholt():
    handler, versuche = _erst_scheitern(httpx.ReadTimeout)

    async with _transport(handler, max_retries=2) as t:
        antwort = await t.request("GET", "/_about")
    assert antwort.status_code == 200
    assert len(versuche) == 2


async def test_als_idempotent_markiert_wird_auch_ein_post_wiederholt():
    """Eine Eigenschaft setzen, eine ACL ersetzen: doppelt angekommen ist
    derselbe Zustand. Solche Aufrufe sagen es dem Transport selbst."""
    handler, versuche = _erst_scheitern(httpx.ReadTimeout)

    async with _transport(handler, max_retries=2) as t:
        antwort = await t.request(
            "POST", "/node/v1/nodes/-home-/abc/property", idempotent=True
        )
    assert antwort.status_code == 200
    assert len(versuche) == 2


async def test_ein_401_wird_auch_bei_post_einmal_wiederholt():
    """Abgelehnt, bevor etwas ausgefuehrt wurde -- die gemessene 401-Laune
    (README) trifft Schreibvorgaenge genauso, und die Wiederholung bleibt
    ungefaehrlich."""
    handler, versuche = _erst_scheitern(401)

    async with _transport(handler, max_retries=2) as t:
        antwort = await t.request("POST", WRITE)
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


# --- Streaming-Download mit Deckel (Audit SEC-2, 06.09.2026) ----------------
#
# request() liest jeden Koerper ganz in den Speicher, bevor jemand seine
# Groesse sehen kann. download() prueft die angekuendigte Groesse vor dem
# ersten Byte und zaehlt mit, waehrend sie ankommen.

async def _stueckweise(*teile: bytes):
    for teil in teile:
        yield teil


async def test_download_liest_den_koerper_stueckweise():
    def handler(request):
        return httpx.Response(200, content=_stueckweise(b"ab", b"cd", b"ef"))

    async with _transport(handler) as t:
        assert await t.download("/x") == b"abcdef"


async def test_download_bricht_ueber_max_bytes_ab():
    """Ohne Content-Length zaehlt der Transport mit und bricht ab, statt alles
    zu halten und dann zu messen."""
    def handler(request):
        return httpx.Response(200, content=_stueckweise(b"x" * 60, b"x" * 60))

    async with _transport(handler) as t:
        with pytest.raises(ContentTooLargeError):
            await t.download("/x", max_bytes=100)


async def test_download_lehnt_eine_angekuendigte_groesse_vor_dem_lesen_ab():
    """Review 06.09.2026 (F7): MockTransport reicht einen bytes-Koerper als ein
    Stueck durch, also bewies der Test nicht, dass vor dem ersten Byte
    abgelehnt wird. Jetzt merkt sich der Koerper, ob er gezogen wurde."""
    gezogen = []

    async def koerper():
        gezogen.append(1)
        yield b"x" * 1000

    def handler(request):
        return httpx.Response(200, content=koerper(), headers={"Content-Length": "1000"})

    async with _transport(handler) as t:
        with pytest.raises(ContentTooLargeError, match="1000"):
            await t.download("/x", max_bytes=100)
        assert gezogen == [], "kein Byte gelesen"
        assert len(await t.download("/x", max_bytes=1000)) == 1000
        assert len(await t.download("/x")) == 1000


async def test_download_wird_wie_ein_get_wiederholt():
    """Review 06.09.2026 (F2): die erste Fassung lief am Transport vorbei und
    verlor alle Wiederholungen -- ein 502, ein Verbindungsfehler oder der
    gemessene 401-Ausrutscher liessen jeden Datei-Fan-out scheitern, der
    zuvor durchkam. Ein Download ist ein GET und wird wie eines wiederholt."""
    versuche = []

    def handler(request):
        versuche.append(1)
        if len(versuche) == 1:
            return httpx.Response(502, text="")
        if len(versuche) == 2:
            raise httpx.ConnectError("weg", request=request)
        return httpx.Response(200, content=b"Dateiinhalt")

    async with _transport(handler, max_retries=3) as t:
        assert await t.download("/x", max_bytes=100) == b"Dateiinhalt"
    assert len(versuche) == 3


async def test_zu_gross_wird_nicht_wiederholt():
    versuche = []

    def handler(request):
        versuche.append(1)
        return httpx.Response(200, content=b"x" * 200)

    async with _transport(handler, max_retries=3) as t:
        with pytest.raises(ContentTooLargeError):
            await t.download("/x", max_bytes=100)
    assert len(versuche) == 1


async def test_eine_fehlerseite_wird_begrenzt_gelesen():
    """Review 06.09.2026 (F10): max_bytes galt nicht fuer den Koerper eines
    5xx. Eine Fehlerseite wird bei 64 KiB abgeschnitten, nicht abgelehnt --
    der Fehler bleibt ein ServerError."""
    def handler(request):
        return httpx.Response(500, content=b"e" * 200_000)

    async with _transport(handler, max_retries=0) as t:
        with pytest.raises(ServerError) as fehler:
            await t.download("/x", max_bytes=10)
    assert len(str(fehler.value)) < 70_000


async def test_download_mit_eigener_anmeldung():
    """Review 06.09.2026 (F11): download() kennt credential= wie request()."""
    gesehen = []

    def handler(request):
        gesehen.append(request.headers.get("authorization"))
        return httpx.Response(200, content=b"x")

    async with _transport(handler) as t:
        await t.download("/x", credential=ANONYMOUS)
    assert gesehen == [None]


async def test_download_meldet_umleitung_status_und_netzfehler():
    """Dieselben Regeln wie request(): eine Umleitung ist kein Erfolg (Audit
    A8), ein Status ab 400 wird zum passenden Fehler, ein Netzfehler zum
    TransportError."""
    def handler(request):
        pfad = request.url.path
        if pfad.endswith("/kaputt"):
            raise httpx.ReadTimeout("zu langsam", request=request)
        if pfad.endswith("/weg"):
            return httpx.Response(302, headers={"location": "https://anderswo.test/"})
        return httpx.Response(404, json={"error": "DAOMissingException", "message": "nein"})

    async with _transport(handler) as t:
        with pytest.raises(EduSharingError, match="redirected"):
            await t.download("/weg")
        with pytest.raises(NotFoundError):
            await t.download("/fehlt")
        with pytest.raises(TransportError):
            await t.download("/kaputt")


async def test_download_traegt_die_anmeldung_nur_zum_repositorium():
    gesehen = {}

    def handler(request):
        gesehen[request.url.host] = request.headers.get("authorization")
        return httpx.Response(200, content=b"x")

    async with _transport(handler) as t:
        await t.download("/x")
        await t.download("https://fremd.example.test/datei")
    assert gesehen["repositorium.example.test"] is not None
    assert gesehen["fremd.example.test"] is None


async def test_vorenthaltener_5xx_bei_einem_post_nennt_den_verdacht():
    """Review 06.09.2026 (F4): auf der Produktivinstanz (Meldungen versteckt)
    kommt der gemessene 401-Ausrutscher als 500 "details hidden" an. Fuer ein
    POST wird er nicht wiederholt -- ob es lief, weiss niemand -- aber der
    Fehler sagt das, statt wie ein Serverfehler auszusehen."""
    versuche = []

    def handler(request):
        versuche.append(1)
        return httpx.Response(500, json={"error": "java.lang.Exception",
                                         "message": "details hidden"})

    async with _transport(handler, max_retries=2) as t:
        with pytest.raises(ServerError) as fehler:
            await t.request("POST", WRITE)
    assert len(versuche) == 1
    assert any("read back" in n for n in fehler.value.__notes__)


# --- ARC-2/API-2: der 429 ist eine Absage, kein Ergebnis --------------------


def _gewartet(monkeypatch) -> list[float]:
    """Zeichnet auf, was geschlafen worden waere, statt zu schlafen."""
    dauern: list[float] = []

    async def statt_schlaf(dauer):
        dauern.append(dauer)

    monkeypatch.setattr(asyncio, "sleep", statt_schlaf)
    return dauern


async def test_ein_429_kommt_als_rate_limited_error_mit_der_wartezeit():
    """Bisher fiel der 429 auf die Basisklasse: nicht zu unterscheiden, und
    die Zahl im Header las niemand (Audit API-2)."""
    def handler(request):
        return httpx.Response(429, headers={"Retry-After": "7"},
                              json={"message": "rate limit"})

    async with _transport(handler, max_retries=0) as t:
        with pytest.raises(RateLimitedError) as fehler:
            await t.request("GET", "/x")
    assert fehler.value.status == 429
    assert fehler.value.retry_after == 7.0


async def test_ein_429_auf_ein_post_wird_wiederholt():
    """Anders als ein 5xx sagt der 429, dass die Anfrage *nicht* ausgefuehrt
    wurde -- der Server hat sie abgewiesen. Also darf auch ein Schreibvorgang
    erneut gesendet werden, ohne dass er zweimal ankommt."""
    versuche = []

    def handler(request):
        versuche.append(1)
        if len(versuche) == 1:
            return httpx.Response(429, headers={"Retry-After": "0"})
        return httpx.Response(200, json={"ok": True})

    async with _transport(handler, max_retries=2) as t:
        antwort = await t.request("POST", WRITE)
    assert len(versuche) == 2
    assert antwort.json() == {"ok": True}


async def test_die_genannte_wartezeit_wird_eingehalten(monkeypatch):
    """Frueher wiederzukommen, als der Dienst gesagt hat, ist genau das, was
    der 429 verhindern soll."""
    dauern = _gewartet(monkeypatch)
    versuche = []

    def handler(request):
        versuche.append(1)
        if len(versuche) == 1:
            return httpx.Response(429, headers={"Retry-After": "12"})
        return httpx.Response(200, json={"ok": True})

    async with _transport(handler, max_retries=2, backoff_base=0.0) as t:
        await t.request("GET", "/x")
    assert dauern == [12.0]


async def test_eine_zu_lange_wartezeit_wird_dem_aufrufer_gegeben(monkeypatch):
    """Eine Stunde in einem Bibliotheksaufruf zu schlafen waere ein
    Aufhaenger. Der Fehler traegt die Zahl, der Aufrufer kann einplanen."""
    dauern = _gewartet(monkeypatch)

    def handler(request):
        return httpx.Response(429, headers={"Retry-After": "3600"})

    async with _transport(handler, max_retries=3) as t:
        with pytest.raises(RateLimitedError) as fehler:
            await t.request("GET", "/x")
    assert dauern == []
    assert fehler.value.retry_after == 3600.0


async def test_der_backoff_streut(monkeypatch):
    """Ohne Jitter kaeme eine Fan-out-Welle geschlossen zurueck. Gestreut
    liegt die Wartezeit zwischen halbem und vollem Schritt (Audit ARC-2)."""
    dauern = _gewartet(monkeypatch)

    def handler(request):
        return httpx.Response(503)

    async with _transport(handler, max_retries=2, backoff_base=1.0) as t:
        with pytest.raises(ServerError):
            await t.request("GET", "/x")
    assert len(dauern) == 2
    assert 0.5 <= dauern[0] <= 1.0
    assert 1.0 <= dauern[1] <= 2.0
