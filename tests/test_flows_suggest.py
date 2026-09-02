"""Einen Vorschlag annehmen heisst: anwenden, zuruecklesen, DANN markieren.

Gemessen am 28.08.2026: ``PATCH ?status=ACCEPTED`` schreibt **nichts** in den
Knoten -- ein angenommener Vorschlag laesst die Eigenschaft leer. Wer nur
markiert, hat ein Protokoll, das etwas behauptet, was nie passiert ist. Der
MCP macht es in ``wlo_decide_suggestion`` in dieser Reihenfolge; hier ist es
ein Ablauf, damit die Reihenfolge nicht Sache jedes Aufrufers ist.

Bleibt der Wert aus (``SilentDropError``), bleibt der Vorschlag offen, und
``failed`` sagt es -- ein Vorschlag, der als angenommen gilt und nichts
bewirkt hat, ist genau der Zustand, den dieser Ablauf verhindert.
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import NotFoundError

REPO = "https://repo.test/edu-sharing"
NID = "k-1"


def _vorschlag(sid: str, prop: str, wert: str, *, status: str = "PENDING") -> dict:
    return {"id": sid, "nodeId": NID, "version": "v1", "propertyId": prop,
            "value": wert, "type": None, "status": status, "description": "Weil",
            "confidence": 0.9, "created": "2026-08-28T10:15:17.962Z",
            "createdBy": {"authorityName": "alice", "authorityType": "USER"}}


class Instanz:
    """Vorschlaege und ein Knoten mit Gedaechtnis; ``stumm`` wird nie gespeichert."""

    def __init__(self, vorschlaege: list[dict], *, stumm: tuple[str, ...] = (),
                 markieren_status: int = 200) -> None:
        self.vorschlaege = list(vorschlaege)
        self.markieren_status = markieren_status   # was PATCH antwortet
        self.props: dict[str, list[str]] = {"cclom:title": ["Probe"]}
        self.stumm = stumm
        self.anfragen: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad, methode = request.url.path, request.method
        if "/suggestions/v1" in pfad:
            if methode == "GET":
                nach_property: dict[str, list[dict]] = {}
                for v in self.vorschlaege:
                    nach_property.setdefault(v["propertyId"], []).append(v)
                return httpx.Response(200, json={"nodeId": NID, "suggestions": nach_property})
            if methode == "PATCH":
                if self.markieren_status != 200:
                    return httpx.Response(self.markieren_status,
                                          json={"error": "Kaputt", "message": "nein"})
                for sid in request.url.params.get_list("id"):
                    for v in self.vorschlaege:
                        if v["id"] == sid:
                            v["status"] = request.url.params.get("status")
                return httpx.Response(200, json=[])
        if methode == "POST" and pfad.endswith("/property"):
            prop = request.url.params["property"]
            if prop not in self.stumm:
                self.props[prop] = json.loads(request.content)
            return httpx.Response(200, content=b"")
        if methode == "PUT" and pfad.endswith("/metadata"):
            for k, v in json.loads(request.content).items():
                if k not in self.stumm:
                    self.props[k] = v
            return httpx.Response(200, json={"node": {
                "ref": {"id": NID}, "type": "ccm:io", "name": "k.txt",
                "properties": dict(self.props)}})
        if methode == "GET" and pfad.endswith("/metadata"):
            return httpx.Response(200, json={"node": {
                "ref": {"id": NID}, "type": "ccm:io", "name": "k.txt",
                "properties": dict(self.props)}})
        raise AssertionError(f"unerwartet: {methode} {pfad}")

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))

    def reihenfolge(self) -> list[str]:
        def art(pfad: str) -> str:
            if pfad.endswith("/property"):
                return "property"
            return "suggestions" if "/suggestions" in pfad else "metadata"
        return [f"{r.method} {art(r.url.path)}" for r in self.anfragen]


async def test_annehmen_schreibt_liest_zurueck_und_markiert_dann():
    instanz = Instanz([_vorschlag("s-1", "ccm:taxonid", "http://vocab.test/080")])
    async with instanz.repo() as repo:
        got = await repo.flows.accept_suggestion(NID, "s-1")
    assert got["applied"] is True
    assert got["status"] == "ACCEPTED"
    assert got["property"] == "ccm:taxonid"
    assert got["value"] == "http://vocab.test/080"
    assert got["failed"] == []
    assert instanz.props["ccm:taxonid"] == ["http://vocab.test/080"]
    schritte = instanz.reihenfolge()
    assert schritte.index("POST property") < schritte.index("PATCH suggestions"), schritte


async def test_kommt_der_wert_nicht_an_bleibt_der_vorschlag_offen():
    instanz = Instanz([_vorschlag("s-1", "ccm:taxonid", "x")], stumm=("ccm:taxonid",))
    async with instanz.repo() as repo:
        got = await repo.flows.accept_suggestion(NID, "s-1")
    assert got["applied"] is False
    assert got["status"] == "PENDING"
    assert [f["part"] for f in got["failed"]] == ["apply"]
    assert "SilentDropError" in got["failed"][0]["reason"]
    assert not any(r.method == "PATCH" for r in instanz.anfragen), "nichts markiert"


async def test_ein_schon_entschiedener_vorschlag_wird_nicht_erneut_angewandt():
    instanz = Instanz([_vorschlag("s-1", "ccm:taxonid", "x", status="DECLINED")])
    async with instanz.repo() as repo:
        got = await repo.flows.accept_suggestion(NID, "s-1")
    assert got["applied"] is False
    assert got["status"] == "DECLINED"
    assert [f["part"] for f in got["failed"]] == ["status"]
    assert not any(r.url.path.endswith("/property") for r in instanz.anfragen)


async def test_unbekannter_vorschlag():
    instanz = Instanz([_vorschlag("s-1", "ccm:taxonid", "x")])
    async with instanz.repo() as repo:
        with pytest.raises(NotFoundError):
            await repo.flows.accept_suggestion(NID, "s-99")


async def test_die_schluessel_sind_immer_dieselben():
    ok = Instanz([_vorschlag("s-1", "ccm:taxonid", "x")])
    stumm = Instanz([_vorschlag("s-1", "ccm:taxonid", "x")], stumm=("ccm:taxonid",))
    async with ok.repo() as a, stumm.repo() as b:
        eins = await a.flows.accept_suggestion(NID, "s-1")
        zwei = await b.flows.accept_suggestion(NID, "s-1")
    assert set(eins) == set(zwei) == {
        "id", "suggestion_id", "property", "value", "applied", "status", "failed",
        "replaced",
    }


async def test_ein_schlagwort_vorschlag_ergaenzt_die_liste_statt_sie_zu_ersetzen():
    """cclom:general_keyword ist eine geteilte Liste. Bis heute schrieb der
    Ablauf den Vorschlag mit set_property -- und loeschte damit jedes andere
    Schlagwort, ohne ein Wort."""
    instanz = Instanz([_vorschlag("s-1", "cclom:general_keyword", "neu")])
    instanz.props["cclom:general_keyword"] = ["bleibt", "auch"]
    async with instanz.repo() as repo:
        got = await repo.flows.accept_suggestion(NID, "s-1")
    assert got["applied"] is True
    assert instanz.props["cclom:general_keyword"] == ["bleibt", "auch", "neu"]
    assert got["replaced"] == []


async def test_ein_ersetzter_wert_wird_genannt():
    instanz = Instanz([_vorschlag("s-1", "ccm:taxonid", "http://vocab.test/neu")])
    instanz.props["ccm:taxonid"] = ["http://vocab.test/alt"]
    async with instanz.repo() as repo:
        got = await repo.flows.accept_suggestion(NID, "s-1")
    assert got["applied"] is True
    assert got["replaced"] == ["http://vocab.test/alt"]
    assert instanz.props["ccm:taxonid"] == ["http://vocab.test/neu"]


async def test_scheitert_das_markieren_bleibt_der_wert_und_die_antwort_sagt_es():
    """Der Wert ist geschrieben und zurueckgelesen; nur das Markieren ging
    schief. Ein Fehler an dieser Stelle darf das Ergebnis nicht verschlucken."""
    instanz = Instanz([_vorschlag("s-1", "ccm:taxonid", "x")], markieren_status=500)
    async with instanz.repo() as repo:
        got = await repo.flows.accept_suggestion(NID, "s-1")
    assert got["applied"] is False and got["status"] == "PENDING"
    assert [f["part"] for f in got["failed"]] == ["mark"]
    assert "written" in got["failed"][0]["reason"]
    assert instanz.props["ccm:taxonid"] == ["x"]


# --- Review B11: ein Vorschlag an einer Referenz, offline --------------------

class MitReferenz(Instanz):
    """ref-1 ist eine Referenz auf den Knoten NID."""

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and request.url.path.endswith("/ref-1/metadata"):
            self.anfragen.append(request)
            return httpx.Response(200, json={"node": {
                "ref": {"id": "ref-1"}, "type": "ccm:io", "name": "k.txt",
                "originalId": NID, "aspects": ["ccm:collection_io_reference"],
                "properties": dict(self.props)}})
        return super().handler(request)


async def test_annehmen_an_einer_referenz_schreibt_ans_original():
    """Ein Vorschlag an einer Listing-ID: der Wert geht ans Original, sonst
    erreicht er den Datensatz nie (gemessen vom MCP, 17.08.2026)."""
    instanz = MitReferenz([_vorschlag("s-1", "ccm:taxonid", "http://vocab.test/080")])
    async with instanz.repo() as repo:
        got = await repo.flows.accept_suggestion("ref-1", "s-1")
    assert got["applied"] is True and got["id"] == "ref-1"
    schreib = [r.url.path for r in instanz.anfragen if r.url.path.endswith("/property")]
    assert schreib and all(f"/{NID}/" in p for p in schreib), schreib
