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
        with pytest.raises(Exception):
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
        with pytest.raises(Exception):
            await t.request("GET", "/_about")
        with pytest.raises(Exception):
            await t.request("POST", "/node/v1/nodes/-home-/x/metadata",
                            json={"cclom:title": ["Titel"]})

    alles = "\n".join(r.getMessage() for r in caplog.records)
    assert PASSWORT not in alles
    # Auch die kodierte Form nicht -- Basic-Auth ist base64, nicht verschluesselt.
    import base64
    kodiert = base64.b64encode(f"{NUTZER}:{PASSWORT}".encode()).decode()
    assert kodiert not in alles
    assert "Authorization" not in alles
