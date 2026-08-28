"""Kommentare an einem Knoten.

Gemessen gegen Staging am 28.08.2026, und von der Ideendatenbank im Betrieb
bestaetigt:

* **Der Body wird 1:1 als Text gespeichert.** Es findet keine
  JSON-Auswertung statt -- ein gesendetes ``"Erster"`` kommt als ``"Erster"``
  zurueck, mit Anfuehrungszeichen. Der Content-Type muss trotzdem
  ``application/json`` sein, sonst 415. Also: rohe UTF-8-Bytes, kein ``json=``.
* Anlegen ist ``PUT .../{node}``, **Aendern ist ``POST .../{comment}``.** Ein
  ``PUT`` auf die Kommentar-ID legt einen Kommentar *am Kommentar* an und endet
  in ``500 DAOValidationException``.
* Antworten laufen ueber ``?commentReference={eltern-id}``; ``replyTo`` traegt
  danach die Referenz auf den Elternkommentar.
* Ein Kommentar traegt ``['comment', 'created', 'creator', 'ref', 'replyTo']``.
  ``created`` sind Millisekunden seit Epoche.
* Anlegen, Aendern und Loeschen antworten alle mit **leerem Body**.
"""

from datetime import UTC, datetime

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.comments import Comment

REPO = "https://repo.test/edu-sharing"
NID = "k-1"


def _eintrag(cid: str, text: str, *, autor: str = "alice",
             created: int = 1787912255934, reply_to: str | None = None) -> dict:
    """Die gemessene Form eines Kommentars."""
    return {
        "ref": {"repo": "local", "id": cid, "archived": False},
        "comment": text,
        "created": created,
        "creator": {"authorityName": autor, "authorityType": "USER"},
        "replyTo": None if reply_to is None else {"repo": "local", "id": reply_to},
    }


class Instanz:
    def __init__(self, eintraege: list[dict] | None = None) -> None:
        self.eintraege = list(eintraege or [])
        self.anfragen: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad = request.url.path
        if "/comment/v1" in pfad:
            if request.method == "GET":
                return httpx.Response(200, json={"comments": self.eintraege})
            if request.method == "PUT":
                eltern = request.url.params.get("commentReference") or None
                self.eintraege.append(_eintrag(
                    f"c-{len(self.eintraege) + 1}",
                    request.content.decode("utf-8"), reply_to=eltern))
            elif request.method == "POST":
                cid = pfad.rsplit("/", 1)[-1]
                for e in self.eintraege:
                    if e["ref"]["id"] == cid:
                        e["comment"] = request.content.decode("utf-8")
            elif request.method == "DELETE":
                cid = pfad.rsplit("/", 1)[-1]
                self.eintraege = [e for e in self.eintraege
                                  if e["ref"]["id"] != cid]
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
            if r.method == methode and "/comment/v1" in r.url.path:
                return r
        raise AssertionError(f"keine {methode}-Anfrage an /comment/v1")


# --- Lesen ----------------------------------------------------------------

async def test_ohne_kommentare_eine_leere_liste():
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        assert await knoten.comments.list() == []


async def test_ein_kommentar_wird_ausgelesen():
    instanz = Instanz([_eintrag("c-1", "Sehr brauchbar")])
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        (kommentar,) = await knoten.comments.list()
    assert kommentar.id == "c-1"
    assert kommentar.text == "Sehr brauchbar"
    assert kommentar.author == "alice"
    assert kommentar.reply_to is None


async def test_created_wird_zu_einem_zeitpunkt():
    """Der Endpunkt schickt Millisekunden seit Epoche. Als Zahl waere das
    unbrauchbar -- niemand vergleicht Kommentare nach 1787912255934."""
    instanz = Instanz([_eintrag("c-1", "x", created=1787912255934)])
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        (kommentar,) = await knoten.comments.list()
    assert kommentar.created == datetime.fromtimestamp(
        1787912255934 / 1000, tz=UTC)


async def test_eine_antwort_nennt_ihren_eltern():
    instanz = Instanz([_eintrag("c-1", "Frage"),
                       _eintrag("c-2", "Antwort", reply_to="c-1")])
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        eintraege = await knoten.comments.list()
    assert [e.reply_to for e in eintraege] == [None, "c-1"]


# --- Schreiben ------------------------------------------------------------

async def test_der_text_geht_als_rohe_bytes():
    """Der wichtigste Test der Datei. Mit ``json=`` staenden Anfuehrungszeichen
    im gespeicherten Text -- gemessen, der Endpunkt wertet den Body nicht aus."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        await knoten.comments.add("Groesse und Uebung")
    put = instanz.letzte("PUT")
    assert put.content == b"Groesse und Uebung"
    assert put.headers["content-type"].startswith("application/json")


async def test_anlegen_liest_zurueck():
    """Die Antwort ist leer -- ohne zweites Lesen gibt es den neuen Kommentar
    gar nicht zurueckzugeben."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        neu = await knoten.comments.add("Erster")
    assert neu.text == "Erster"
    assert neu.id


async def test_antworten_setzt_die_referenz():
    instanz = Instanz([_eintrag("c-1", "Frage")])
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        antwort = await knoten.comments.add("Antwort", reply_to="c-1")
    assert instanz.letzte("PUT").url.params["commentReference"] == "c-1"
    assert antwort.reply_to == "c-1"


async def test_ohne_antwort_kein_leerer_parameter():
    """Ein leeres commentReference waere eine Referenz auf nichts."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        await knoten.comments.add("Erster")
    assert "commentReference" not in instanz.letzte("PUT").url.params


async def test_aendern_geht_per_post():
    """Ein PUT auf die Kommentar-ID legt einen Kommentar am Kommentar an und
    endet in 500 -- gemessen. Geaendert wird mit POST."""
    instanz = Instanz([_eintrag("c-1", "Alt")])
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        geaendert = await knoten.comments.edit("c-1", "Neu")
    post = instanz.letzte("POST")
    assert post.url.path.endswith("/c-1")
    assert post.content == b"Neu"
    assert geaendert.text == "Neu"


async def test_loeschen_entfernt_den_kommentar():
    instanz = Instanz([_eintrag("c-1", "Weg damit"), _eintrag("c-2", "Bleibt")])
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        await knoten.comments.delete("c-1")
        uebrig = await knoten.comments.list()
    assert [e.id for e in uebrig] == ["c-2"]


async def test_leerer_text_wird_abgelehnt():
    """Ein leerer Kommentar ist keiner. Der Endpunkt nimmt ihn an -- gemessen,
    200 fuer einen leeren Body -- und legt einen unsichtbaren Eintrag an."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        with pytest.raises(ValueError, match="without text"):
            await knoten.comments.add("   ")
    assert not [r for r in instanz.anfragen if "/comment/v1" in r.url.path]


async def test_aendern_auf_leer_ebenso():
    instanz = Instanz([_eintrag("c-1", "Alt")])
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        with pytest.raises(ValueError):
            await knoten.comments.edit("c-1", "")


async def test_ein_verschwundener_kommentar_wird_gemeldet():
    """Nach dem Aendern muss der Kommentar wieder auftauchen. Tut er es nicht,
    ist etwas anderes passiert als das Gewuenschte."""
    instanz = Instanz([_eintrag("c-1", "Alt")])
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        with pytest.raises(Exception, match="c-9"):
            await knoten.comments.edit("c-9", "Neu")


# --- Form -----------------------------------------------------------------

def test_comment_ist_unveraenderlich():
    k = Comment(id="c-1", text="x", author="alice",
                created=datetime.now(tz=UTC), reply_to=None)
    with pytest.raises(AttributeError):
        k.text = "y"  # type: ignore[misc]


def test_comment_repr_nennt_autor_und_anfang():
    k = Comment(id="c-1", text="Ein sehr langer Text, der gekuerzt gehoert",
                author="alice", created=datetime.now(tz=UTC), reply_to=None)
    assert "alice" in repr(k)
    assert len(repr(k)) < 80


async def test_ein_nicht_angekommener_kommentar_wird_gemeldet():
    """Die Instanz antwortet 200 und legt nichts an -- dieselbe Klasse von
    Verlust wie bei den Properties. Ohne Rueckleseprobe waere es ein Erfolg."""
    from edusharing.errors import SilentDropError

    class Taub(Instanz):
        def handler(self, request: httpx.Request) -> httpx.Response:
            if request.method == "PUT" and "/comment/v1" in request.url.path:
                self.anfragen.append(request)
                return httpx.Response(200, content=b"")
            return super().handler(request)

    instanz = Taub()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        with pytest.raises(SilentDropError):
            await knoten.comments.add("Verschwindet")


async def test_comments_repr_nennt_den_knoten():
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        assert NID in repr(knoten.comments)
