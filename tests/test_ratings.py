"""Bewertungen.

Gemessen gegen Staging am 28.08.2026 in einem eigens angelegten Ordner:

* **Die Knotenantwort traegt die Bewertung schon mit** -- unter ``rating``
  stehen ``overall.rating``, ``overall.count`` und ``user``. Sie zu lesen
  kostet keine Anfrage, dasselbe Muster wie bei ``isPublic``.
* ``PUT ?rating=4`` antwortet mit **leerem Body**. Was gespeichert wurde, sagt
  erst der zweite Blick auf den Knoten.
* ``GET .../history`` -- die Einzelbewertungen -- antwortet **500
  NotAnAdminException**. Die sieht nur ein Administrator.
* **``rating=0`` ist kein Zuruecksetzen.** Gemessen: danach steht
  ``count: 1, rating: 0.0`` -- die Null zaehlt mit und zieht den Schnitt
  herunter. Zurueckgenommen wird mit ``DELETE``. Die Ideendatenbank
  dokumentiert die Null als Reset; auf Staging ist sie das nicht.
* ``DELETE`` ohne vorhandene Bewertung antwortet ebenfalls 200.
* Der Body ist gleichgueltig -- leer, Leerzeichen und roher Text ergeben alle
  200. Der Content-Type muss ``application/json`` sein.
"""

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.ratings import Rating

REPO = "https://repo.test/edu-sharing"
NID = "k-1"


def _bewertung(*, sum_: float = 0.0, count: int = 0, own: float = 0.0) -> dict:
    """Die gemessene Form des rating-Blocks einer Knotenantwort."""
    schnitt = (sum_ / count) if count else 0.0
    return {"overall": {"sum": sum_, "count": count, "rating": schnitt},
            "affiliation": {} if not count else {"null": {"sum": sum_,
                                                          "count": count,
                                                          "rating": schnitt}},
            "user": own}


class Instanz:
    def __init__(self, rating: dict | None = None) -> None:
        self.rating = _bewertung() if rating is None else rating
        self.anfragen: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad = request.url.path
        if "/rating/v1" in pfad:
            if request.method == "PUT":
                wert = float(request.url.params.get("rating"))
                self.rating = _bewertung(sum_=wert, count=1, own=wert)
            elif request.method == "DELETE":
                self.rating = _bewertung()
            return httpx.Response(200, content=b"")
        return httpx.Response(200, json={"node": {
            "ref": {"id": NID}, "type": "ccm:io", "name": "k.txt",
            "rating": self.rating, "properties": {"cclom:title": ["Probe"]}}})

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))

    def params(self, methode: str) -> dict:
        for r in self.anfragen:
            if r.method == methode and "/rating/v1" in r.url.path:
                return dict(r.url.params)
        raise AssertionError(f"keine {methode}-Anfrage an /rating/v1")


# --- Lesen, ohne Anfrage --------------------------------------------------

async def test_ohne_bewertung_kommt_nichts():
    """count == 0 ist das Kennzeichen. Ein Schnitt von 0.0 waere als Zahl
    irrefuehrend -- niemand hat 0 vergeben, es hat niemand vergeben."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
    assert knoten.rating is None


async def test_bewertung_kommt_aus_der_knotenantwort():
    instanz = Instanz(_bewertung(sum_=9.0, count=3, own=4.0))
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        bewertung = knoten.rating
    assert bewertung == Rating(average=3.0, count=3, own=4.0)


async def test_lesen_kostet_keine_anfrage():
    instanz = Instanz(_bewertung(sum_=4.0, count=1, own=4.0))
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        vorher = len(instanz.anfragen)
        assert knoten.rating is not None
    assert len(instanz.anfragen) == vorher


async def test_ohne_eigene_bewertung_ist_own_leer():
    """user kommt als 0.0, wenn das Konto nicht bewertet hat -- gemessen. Das
    ist von einer echten Null nicht zu unterscheiden, weshalb die Bibliothek
    eine Null gar nicht erst schreiben laesst."""
    instanz = Instanz(_bewertung(sum_=8.0, count=2, own=0.0))
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
    assert knoten.rating.own is None
    assert knoten.rating.count == 2


# --- Schreiben ------------------------------------------------------------

async def test_bewerten_liest_zurueck():
    """Die Antwort auf den PUT ist leer -- es gibt nichts zu pruefen ausser
    einem zweiten Blick auf den Knoten."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        neu = await knoten.rate(4)
    assert neu == Rating(average=4.0, count=1, own=4.0)


async def test_ganze_zahlen_gehen_als_ganze_zahlen():
    """Die Ideendatenbank hat auf Produktion gemessen, dass httpx einen float
    als ``rating=4.0`` schreibt und edu-sharing das verwirft. Auf Staging
    nimmt es beides an -- die Ganzzahl kostet nichts und deckt beide Faelle."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        await knoten.rate(4)
    assert instanz.params("PUT")["rating"] == "4"


async def test_halbe_zahlen_bleiben_halbe_zahlen():
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        await knoten.rate(3.5)
    assert instanz.params("PUT")["rating"] == "3.5"


async def test_null_wird_abgelehnt():
    """Gemessen: rating=0 setzt nichts zurueck, sondern zaehlt als abgegebene
    Null und zieht den Schnitt herunter. Wer sie schreibt, meint fast immer
    zuruecknehmen."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        with pytest.raises(ValueError, match="unrate"):
            await knoten.rate(0)
    assert not [r for r in instanz.anfragen if "/rating/v1" in r.url.path]


async def test_negative_werte_ebenso():
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        with pytest.raises(ValueError):
            await knoten.rate(-1)


async def test_der_text_geht_als_rohe_bytes():
    """Wie beim Kommentar: der Endpunkt liest den Body, nicht ein JSON-Feld."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        await knoten.rate(4, "Sehr brauchbar")
    put = next(r for r in instanz.anfragen if r.method == "PUT")
    assert put.content == b"Sehr brauchbar"
    assert put.headers["content-type"].startswith("application/json")


async def test_zuruecknehmen_liest_ebenfalls_zurueck():
    instanz = Instanz(_bewertung(sum_=4.0, count=1, own=4.0))
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        danach = await knoten.unrate()
    assert danach is None, "ohne Bewertungen gibt es keine Zahl"


async def test_zuruecknehmen_ohne_bewertung_ist_kein_fehler():
    """Gemessen: DELETE antwortet auch dann 200. Ein wiederholter Lauf soll
    nicht scheitern."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node(NID)
        assert await knoten.unrate() is None


# --- Form -----------------------------------------------------------------

def test_rating_ist_unveraenderlich():
    bewertung = Rating(average=4.0, count=1, own=4.0)
    with pytest.raises(AttributeError):
        bewertung.average = 5.0  # type: ignore[misc]


def test_rating_repr_nennt_schnitt_und_zahl():
    assert repr(Rating(average=4.0, count=3, own=None)) == "Rating(4.0 aus 3)"
