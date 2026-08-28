"""Etwas zur Pruefung einreichen -- und nachsehen, was schon damit geschah.

Der Schritt, den weder Anlegen noch Aendern von allein tut, damit kein Entwurf
versehentlich in einer Redaktions-Warteschlange landet.

Gemessen gegen Staging am 28.08.2026:

* ``GET /node/v1/nodes/-home-/{id}/workflow`` antwortet mit einer **Liste**
  von Verlaufseintraegen, am Anfang leer -- nicht mit einem Objekt.
* Ein Eintrag traegt ``['comment', 'editor', 'receiver', 'status', 'time']``.
  ``time`` sind Millisekunden seit Epoche, ``receiver`` ist eine **Liste** von
  Autoritaeten.
* Der Verlauf kommt **neueste zuerst**. Gemessen durch zweimaliges Einreichen:
  der zweite Schritt stand vorn.
* Eingereicht wird mit **``PUT``**, Body
  ``{receiver: [{authorityName, authorityType}], status, comment}``. Die
  Antwort ist **leer** -- was gespeichert wurde, sagt erst der Verlauf.
* ``status`` ist eine Konvention der Instanz (auf WLO ``100_tocheck``), kein
  Wert der API. Er wird deshalb verlangt und nicht vorbelegt.
"""

import json
from datetime import UTC, datetime

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.workflow import WorkflowStep

REPO = "https://repo.test/edu-sharing"
NID = "k-1"


def _person(name: str) -> dict:
    return {"authorityName": name, "authorityType": "USER", "userName": name,
            "profile": {"firstName": "A", "lastName": "B"}}


def _eintrag(status: str, *, empfaenger: list[str] | None = None,
             comment: str = "Bitte pruefen",
             time: int = 1787913246139) -> dict:
    """Die gemessene Form eines Verlaufseintrags."""
    return {"time": time, "status": status, "comment": comment,
            "editor": _person("alice"),
            "receiver": [_person(e) for e in (empfaenger or ["bob"])]}


class Instanz:
    def __init__(self, verlauf: list[dict] | None = None) -> None:
        self.verlauf = list(verlauf or [])
        self.anfragen: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        if request.url.path.endswith("/workflow"):
            if request.method == "GET":
                return httpx.Response(200, json=self.verlauf)
            koerper = json.loads(request.content)
            # Wie die Instanz: neueste zuerst.
            self.verlauf.insert(0, _eintrag(
                koerper["status"], comment=koerper.get("comment", ""),
                empfaenger=[e["authorityName"] for e in koerper["receiver"]]))
            return httpx.Response(200, content=b"")
        return httpx.Response(200, json={"node": {
            "ref": {"id": NID}, "type": "ccm:io", "name": "k.txt",
            "properties": {"cclom:title": ["Probe"]}}})

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))

    def letzte(self, methode: str) -> httpx.Request:
        for r in reversed(self.anfragen):
            if r.method == methode and r.url.path.endswith("/workflow"):
                return r
        raise AssertionError(f"keine {methode}-Anfrage an /workflow")


# --- Lesen ----------------------------------------------------------------

async def test_ein_frischer_knoten_hat_keinen_verlauf():
    """Der Endpunkt antwortet mit einer leeren Liste, nicht mit einem Objekt --
    wer ein Woerterbuch erwartet, bekommt hier einen Typfehler."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        assert await knoten.workflow.history() == []


async def test_ein_eintrag_wird_ausgelesen():
    instanz = Instanz([_eintrag("100_tocheck", empfaenger=["bob", "carol"])])
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        (schritt,) = await knoten.workflow.history()
    assert schritt.status == "100_tocheck"
    assert schritt.receivers == ("bob", "carol")
    assert schritt.editor == "alice"
    assert schritt.comment == "Bitte pruefen"


async def test_die_zeit_wird_zu_einem_zeitpunkt():
    instanz = Instanz([_eintrag("100_tocheck", time=1787913246139)])
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        (schritt,) = await knoten.workflow.history()
    assert schritt.at == datetime.fromtimestamp(1787913246139 / 1000, tz=UTC)


# --- Einreichen -----------------------------------------------------------

async def test_einreichen_schickt_empfaenger_status_und_kommentar():
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        await knoten.workflow.submit("bob", "100_tocheck", "Bitte pruefen")
    koerper = json.loads(instanz.letzte("PUT").content)
    assert koerper == {"receiver": [{"authorityName": "bob",
                                     "authorityType": "USER"}],
                       "status": "100_tocheck", "comment": "Bitte pruefen"}


async def test_eine_gruppe_als_empfaenger_bekommt_den_richtigen_typ():
    """GROUP_-Namen sind Gruppen. Denselben Ableitungsweg nutzt permissions.py."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        await knoten.workflow.submit("GROUP_redaktion", "100_tocheck")
    koerper = json.loads(instanz.letzte("PUT").content)
    assert koerper["receiver"][0]["authorityType"] == "GROUP"


async def test_mehrere_empfaenger_sind_erlaubt():
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        await knoten.workflow.submit(["bob", "carol"], "100_tocheck")
    koerper = json.loads(instanz.letzte("PUT").content)
    assert [e["authorityName"] for e in koerper["receiver"]] == ["bob", "carol"]


async def test_einreichen_liest_den_verlauf_zurueck():
    """Die Antwort ist leer. Ohne zweiten Blick gibt es nichts zurueckzugeben
    und nichts zu pruefen."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        schritt = await knoten.workflow.submit("bob", "100_tocheck", "Los")
    assert schritt.status == "100_tocheck"
    assert schritt.receivers == ("bob",)


async def test_ohne_empfaenger_wird_nicht_geschickt():
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        with pytest.raises(ValueError, match="receiver"):
            await knoten.workflow.submit([], "100_tocheck")
    assert not [r for r in instanz.anfragen if r.url.path.endswith("/workflow")]


async def test_ohne_status_ebenso():
    """status ist eine Konvention der Instanz, keine der API -- er wird
    verlangt, nicht geraten."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        with pytest.raises(ValueError, match="status"):
            await knoten.workflow.submit("bob", "")


async def test_ein_nicht_angekommener_schritt_wird_gemeldet():
    from edusharing.errors import SilentDropError

    class Taub(Instanz):
        def handler(self, request: httpx.Request) -> httpx.Response:
            if request.method == "PUT" and request.url.path.endswith("/workflow"):
                self.anfragen.append(request)
                return httpx.Response(200, content=b"")
            return super().handler(request)

    instanz = Taub()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        with pytest.raises(SilentDropError):
            await knoten.workflow.submit("bob", "100_tocheck")


# --- Form -----------------------------------------------------------------

def test_workflowstep_ist_unveraenderlich():
    s = WorkflowStep(status="x", receivers=("bob",), comment="",
                     editor="alice", at=datetime.now(tz=UTC))
    with pytest.raises(AttributeError):
        s.status = "y"  # type: ignore[misc]


def test_workflowstep_repr_nennt_stand_und_empfaenger():
    s = WorkflowStep(status="100_tocheck", receivers=("bob", "carol"),
                     comment="", editor="alice", at=datetime.now(tz=UTC))
    assert repr(s) == "WorkflowStep('100_tocheck' an bob, carol)"


async def test_der_verlauf_kommt_neueste_zuerst():
    """Darauf beruht die Rueckleseprobe von submit(): sie nimmt den ersten
    Treffer und damit den eben gemachten Schritt, nicht einen aelteren, der
    genauso aussah."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        await knoten.workflow.submit("bob", "100_tocheck")
        zweiter = await knoten.workflow.submit("bob", "200_tosave")
        verlauf = await knoten.workflow.history()
    assert [s.status for s in verlauf] == ["200_tosave", "100_tocheck"]
    assert zweiter.status == "200_tosave"
