"""Der Volltext eines Materials -- und warum es keinen gibt.

Drei Quellen, in dieser Reihenfolge:

1. ``/textContent`` des Repositoriums -- fuer die grosse Mehrheit vorhanden.
2. Die Datei selbst per ``download()``, wenn der Knoten eine ``text/*``-Datei
   traegt: gemessen am 27.08.2026 liefert ``/textContent`` fuer Markdown und
   JSON **nichts**, obwohl die Datei Text hat (siehe ``content.text``).
3. Die verlinkte Seite ueber den Extraktionsdienst -- nur fuer Material, das
   bloss verlinkt ist (``ccm:wwwurl``), und nur wenn ein Dienst uebergeben
   wurde: die Bibliothek kennt keine Adresse (E4).

Kein Text ist ein normales Ergebnis, kein Fehler: ``reason`` sagt, welches der
sechs Dinge es war. Beispiel 15 brauchte fuer dasselbe 215 Zeilen; der MCP
bietet es als ``get_wlo_content_text`` an.
"""

import json

import httpx

from edusharing import AsyncRepository
from edusharing.extraction import TextExtraction

REPO = "https://repo.test/edu-sharing"
DIENST = "https://text-extraction.test"
NID = "n-1"
SEITE = "https://example.org/arbeitsblatt"


def _knoten(*, url: str | None = None, datei: bool = False,
            mimetype: str | None = None, titel: str = "Mein Material") -> dict:
    data: dict = {
        "ref": {"id": NID}, "title": titel, "type": "ccm:io",
        "downloadUrl": f"{REPO}/rest/node/v1/nodes/-home-/{NID}/content",
        "content": {"hash": "abc" if datei else None},
        "mimetype": mimetype,
        "properties": {"cclom:title": [titel]},
    }
    if url:
        data["properties"]["ccm:wwwurl"] = [url]
    return data


class Instanz:
    """Repositorium und Extraktionsdienst in einem Handler, nach Host getrennt."""

    def __init__(self, knoten: dict | None = None, *, text: str = "",
                 datei: bytes = b"", status: int = 200,
                 extrahiert: str | None = "Von der Seite.",
                 dienst_status: int = 200) -> None:
        self.knoten = knoten if knoten is not None else _knoten()
        self.text, self.datei, self.status = text, datei, status
        self.extrahiert, self.dienst_status = extrahiert, dienst_status
        self.extraktionen: list[dict] = []
        self.pfade: list[str] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        pfad = request.url.path
        self.pfade.append(pfad)
        if request.url.host == "text-extraction.test":
            self.extraktionen.append(json.loads(request.content))
            if self.dienst_status != 200:
                return httpx.Response(self.dienst_status, json={"detail": "kaputt"})
            if self.extrahiert is None:
                return httpx.Response(200, json={"text": "", "lang": "", "status": 200})
            return httpx.Response(200, json={"text": self.extrahiert, "lang": "de",
                                             "status": 200})
        if pfad.endswith("/metadata"):
            if self.status != 200:
                return httpx.Response(self.status, json={"error": "DAOSecurityException",
                                                         "message": "nope"})
            return httpx.Response(200, json={"node": self.knoten})
        if pfad.endswith("/textContent"):
            return httpx.Response(200, json={"text": self.text})
        if pfad.endswith("/content"):
            return httpx.Response(200, content=self.datei)
        raise AssertionError(f"unerwartet: {request.method} {pfad}")

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))

    def dienst(self) -> TextExtraction:
        return TextExtraction(
            DIENST, backoff_base=0.0, resolve=lambda _host: ["93.184.216.34"],
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))


async def _text(instanz: Instanz, **kwargs):
    async with instanz.repo() as repo:
        return await repo.flows.text(NID, **kwargs)


# --- Die drei Quellen -------------------------------------------------------

async def test_text_aus_dem_repositorium():
    instanz = Instanz(text="Aus dem Repositorium.")
    got = await _text(instanz, extraction=instanz.dienst())
    assert got["source"] == "repository"
    assert got["text"] == "Aus dem Repositorium."
    assert got["reason"] == ""
    assert got["source_url"] is None
    assert got["char_count"] == len("Aus dem Repositorium.")
    assert got["truncated"] is False
    # Die Seite wird nicht gefragt, wenn das Repositorium Text hat.
    assert instanz.extraktionen == []


async def test_markdown_kommt_per_download():
    """Gemessen: /textContent ist fuer text/markdown leer, die Datei nicht."""
    instanz = Instanz(_knoten(datei=True, mimetype="text/markdown"),
                      datei=b"# Titel\n\nDer Text.")
    got = await _text(instanz)
    assert got["source"] == "download"
    assert got["text"] == "# Titel\n\nDer Text."
    assert got["reason"] == ""


async def test_eine_binaerdatei_wird_nicht_heruntergeladen():
    """Ein PDF ohne extrahierten Text ist kein Textrueckfall -- Bytes sind kein Text."""
    instanz = Instanz(_knoten(datei=True, mimetype="application/pdf"), datei=b"%PDF")
    got = await _text(instanz)
    assert got["source"] == "none"
    assert got["reason"] == "no_text_no_url"
    assert not any(p.endswith("/content") for p in instanz.pfade)


async def test_verlinktes_material_kommt_von_der_seite():
    instanz = Instanz(_knoten(url=SEITE))
    got = await _text(instanz, extraction=instanz.dienst())
    assert got["source"] == "extraction"
    assert got["text"] == "Von der Seite."
    assert got["source_url"] == SEITE
    assert instanz.extraktionen[0]["url"] == SEITE


# --- Die sechs Gruende, warum keiner da ist --------------------------------

async def test_ohne_text_und_ohne_adresse():
    instanz = Instanz(_knoten())
    got = await _text(instanz, extraction=instanz.dienst())
    assert got["source"] == "none"
    assert got["reason"] == "no_text_no_url"
    assert got["text"] == ""


async def test_ohne_dienst_bleibt_die_adresse_ungelesen():
    """Die Bibliothek kennt keine Adresse eines Dienstes. Ohne uebergebenen
    Dienst wird die Seite nicht geholt -- und die Antwort nennt die Adresse,
    damit der Aufrufer selbst entscheiden kann."""
    instanz = Instanz(_knoten(url=SEITE))
    got = await _text(instanz)
    assert got["reason"] == "no_extraction_service"
    assert got["source_url"] == SEITE


async def test_die_seite_hat_keinen_text():
    instanz = Instanz(_knoten(url=SEITE), extrahiert=None)
    got = await _text(instanz, extraction=instanz.dienst())
    assert got["reason"] == "extraction_failed"
    assert "no_text" in got["detail"]


async def test_der_dienst_selbst_scheitert():
    """Ein kaputter Dienst ist etwas anderes als eine Seite ohne Text -- aber
    beides ist fuer den Aufrufer 'kein Text, und zwar deshalb'."""
    instanz = Instanz(_knoten(url=SEITE), dienst_status=500)
    got = await _text(instanz, extraction=instanz.dienst())
    assert got["reason"] == "extraction_failed"
    assert "500" in got["detail"]


async def test_unbekannter_knoten():
    instanz = Instanz(status=404)
    got = await _text(instanz)
    assert got["reason"] == "node_not_found"
    assert got["id"] == NID
    assert got["title"] is None
    assert got["text"] == ""


async def test_verweigerter_knoten():
    instanz = Instanz(status=403)
    got = await _text(instanz)
    assert got["reason"] == "access_denied"


# --- Kuerzen ---------------------------------------------------------------

async def test_gekuerzt_an_der_wortgrenze():
    instanz = Instanz(text="Wort " * 100)
    got = await _text(instanz, max_chars=23)
    assert got["truncated"] is True
    assert got["char_count"] == 500
    assert len(got["text"]) <= 23
    assert not got["text"].endswith("Wor"), "nicht mitten im Wort"


async def test_die_schluessel_sind_immer_dieselben():
    """Auch ohne Text: jeder Schluessel da, damit ein Aufrufer nicht raten muss."""
    ohne = await _text(Instanz(_knoten()))
    mit = await _text(Instanz(text="x"))
    assert set(ohne) == set(mit) == {
        "id", "title", "text", "source", "source_url", "char_count",
        "truncated", "reason", "detail",
    }
