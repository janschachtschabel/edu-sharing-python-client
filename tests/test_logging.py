"""Was die Bibliothek nach aussen meldet -- und was niemals.

Audit-Befund F5 vom 27.08.2026: die Bibliothek schwieg vollstaendig. Ein Dienst,
der sie einsetzt, konnte nach einem Zwischenfall nicht rekonstruieren, welche
Anfragen liefen, was wiederholt wurde und welches Modell geantwortet hat.

Die zweite Haelfte des Themas ist die wichtigere: Protokolle werden aggregiert,
durchsucht und aufbewahrt. Ein Passwort, das einmal darin steht, steht dort
dauerhaft. Die Tests hier pruefen deshalb beides -- dass etwas gemeldet wird,
und dass die Zugangsdaten es nicht sind.
"""

import logging

import httpx
import pytest

from edusharing.errors import ServerError
from edusharing.transport import Transport

REPO = "https://repo.test/edu-sharing"
PASSWORT = "Streng-Geheim-2026"
NUTZER = "testnutzer"


def _transport(handler, **kwargs) -> Transport:
    return Transport(
        REPO, credential=(NUTZER, PASSWORT), backoff_base=0.0,
        client=httpx.AsyncClient(transport=httpx.MockTransport(handler)), **kwargs)


async def test_anfrage_wird_gemeldet(caplog):
    caplog.set_level(logging.DEBUG, logger="edusharing")
    async with _transport(lambda r: httpx.Response(200, json={})) as t:
        await t.request("GET", "/_about")
    meldungen = [r.getMessage() for r in caplog.records]
    assert any("GET" in m and "/_about" in m for m in meldungen), meldungen


async def test_wiederholung_wird_gemeldet(caplog):
    """Ein stiller Retry ist bei der Fehlersuche das Schlimmste: die Anfrage
    dauerte dreimal so lang, und nichts sagt warum."""
    caplog.set_level(logging.DEBUG, logger="edusharing")
    versuche: list = []

    def handler(request):
        versuche.append(request)
        return httpx.Response(503, text="kurz nicht da")

    async with _transport(handler, max_retries=2) as t:
        with pytest.raises(ServerError):
            await t.request("GET", "/_about")

    assert len(versuche) == 3, "Vorbedingung: es wurde wirklich wiederholt"
    hinweise = [r.getMessage() for r in caplog.records if r.levelno >= logging.INFO]
    assert hinweise, "die Wiederholung blieb unerwaehnt"


@pytest.mark.parametrize("stufe", [logging.DEBUG, logging.INFO])
async def test_zugangsdaten_stehen_nie_im_protokoll(caplog, stufe):
    """Der eigentliche Punkt. Protokolle werden aggregiert und aufbewahrt --
    was einmal darin steht, steht dauerhaft darin."""
    caplog.set_level(stufe, logger="edusharing")

    def handler(request):
        return httpx.Response(503, text="weg")

    async with _transport(handler, max_retries=1) as t:
        with pytest.raises(ServerError):
            await t.request("GET", "/_about")
        with pytest.raises(ServerError):
            await t.request("POST", "/node/v1/nodes/-home-/x/metadata",
                            json={"cclom:title": ["Titel"]})

    alles = "\n".join(r.getMessage() for r in caplog.records)
    assert PASSWORT not in alles
    # Auch die kodierte Form nicht -- Basic-Auth ist base64, nicht verschluesselt.
    import base64
    kodiert = base64.b64encode(f"{NUTZER}:{PASSWORT}".encode()).decode()
    assert kodiert not in alles
    assert "Authorization" not in alles


# --- Was in einer Adresse stecken kann ------------------------------------
#
# ``extraction.py`` meldet seit jeher nur den Host, weil eine vom Aufrufer
# uebergebene Adresse ein Token im Query tragen kann. ``transport`` meldete
# die Adresse vollstaendig und nahm ueber ``_resolve`` auch absolute URLs an
# -- dieselbe Luecke, gegen die der Nachbardienst schon schuetzt (Audit F7).

TICKET = "TICKET_ec4f1a90"


async def test_ein_query_steht_nie_im_protokoll(caplog):
    """Der Query gehoert dem Aufrufer, der Pfad der Bibliothek.

    edu-sharing selbst kennt ``?ticket=``; wer es ueber ``repo.raw`` anhaengt,
    darf es nicht im Protokoll wiederfinden.
    """
    caplog.set_level(logging.DEBUG, logger="edusharing")
    async with _transport(lambda r: httpx.Response(200, json={})) as t:
        await t.request("GET", f"/_about?ticket={TICKET}")
    alles = "\n".join(r.getMessage() for r in caplog.records)
    assert TICKET not in alles, alles
    assert "/_about" in alles, "der Pfad selbst bleibt -- sonst nuetzt es nichts"


async def test_von_einer_fremden_adresse_steht_nur_der_host_im_protokoll(caplog):
    """Bei einer fremden Adresse gehoert auch der Pfad dem Aufrufer.

    ``request`` nimmt absolute URLs an. Ein signierter Link traegt sein
    Geheimnis im Pfad, nicht im Query.
    """
    caplog.set_level(logging.DEBUG, logger="edusharing")
    async with _transport(lambda r: httpx.Response(200, json={})) as t:
        await t.request("GET", f"https://fremd.test/download/{TICKET}/datei.pdf")
    alles = "\n".join(r.getMessage() for r in caplog.records)
    assert TICKET not in alles, alles
    assert "fremd.test" in alles, "der Host bleibt -- sonst ist die Zeile wertlos"

