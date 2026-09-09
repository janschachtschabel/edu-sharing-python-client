"""Gibt es zu dieser Adresse schon einen Datensatz?

``ccm:wwwurl`` benennt verlinktes Material eindeutig; ein zweiter Datensatz
fuer dieselbe Adresse ist per Definition eine Dublette. Gemessen am 02.09.2026
gegen Staging: mit ``mds_oeh`` ist die Eigenschaft ein Suchkriterium (1 Treffer,
exakt gleich); ``-default-`` weist es zurueck (``ValidationError``).

Zwei Dinge machen die Pruefung strenger als die Suche, auf der sie beruht --
beides vom MCP so gemessen (``services/write/duplicates.ts``): die Suche
antwortet auch mit Nachbarn, also wird die eigene ``ccm:wwwurl`` jedes Treffers
verglichen; und der Vergleich normalisiert **komponentenweise** -- Schema und
Host schreibungsblind, wie RFC 3986 es sagt, Pfad und Query nicht. Ein
Schraegstrich am Ende unterscheidet zwei echte Seiten, und ``/A`` von ``/a``
ebenso. Bis zum 09.09.2026 wurde die ganze Adresse kleingeschrieben (F10).
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import ConflictError, ValidationError
from edusharing.flows.duplicates import find_by_url

REPO = "https://repo.test/edu-sharing"
HOME = "home-folder-id"
URL = "https://example.org/Arbeitsblatt"


def _treffer(nid: str, url: str, titel: str = "Vorhanden") -> dict:
    return {"ref": {"id": nid}, "title": titel, "type": "ccm:io",
            "properties": {"cclom:title": [titel], "ccm:wwwurl": [url]}}


class Instanz:
    def __init__(self, treffer: list[dict] | None = None, *,
                 kriterium_unbekannt: bool = False) -> None:
        self.treffer = treffer or []
        self.kriterium_unbekannt = kriterium_unbekannt
        self.angelegt: list[dict] = []
        self.anfragen: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad, methode = request.url.path, request.method
        if "-me-" in pfad:
            return httpx.Response(200, json={"person": {
                "authorityName": "alice", "userName": "alice", "profile": {},
                "homeFolder": {"id": HOME}}})
        if "/values" in pfad:
            # Ein Wert ohne http(s):// geht durch die Vokabularsuche -- und
            # findet dort nichts.
            return httpx.Response(200, json={"values": []})
        if "/search/v1" in pfad:
            if self.kriterium_unbekannt:
                return httpx.Response(400, json={
                    "error": "DAOValidationException",
                    "message": "Could not find parameter ccm:wwwurl in the query ngsearch"})
            return httpx.Response(200, json={
                "nodes": self.treffer,
                "pagination": {"total": len(self.treffer), "from": 0,
                               "count": len(self.treffer)}})
        if methode == "POST" and pfad.endswith("/children"):
            gesendet = json.loads(request.content)
            self.angelegt.append(gesendet)
            node = {"ref": {"id": "neu-1"}, "type": "ccm:io", "isPublic": False,
                    "name": request.url.params.get("renameIfExists") or "x",
                    "title": (gesendet.get("cclom:title") or [""])[0],
                    "properties": gesendet}
            return httpx.Response(200, json={"node": node})
        if methode == "GET" and pfad.endswith("/metadata"):
            props = self.angelegt[-1] if self.angelegt else {}
            return httpx.Response(200, json={"node": {
                "ref": {"id": "neu-1"}, "type": "ccm:io", "isPublic": False,
                "name": "x", "title": (props.get("cclom:title") or [""])[0],
                "properties": props}})
        raise AssertionError(f"unerwartet: {methode} {pfad}")

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, metadataset="mds_oeh", backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))

    def kriterien(self) -> list[dict]:
        for r in self.anfragen:
            if "/search/v1" in r.url.path:
                return json.loads(r.content)["criteria"]
        raise AssertionError("keine Suchanfrage")


async def test_vorhandenes_wird_genannt_und_nichts_angelegt():
    instanz = Instanz([_treffer("alt-1", URL)])
    async with instanz.repo() as repo:
        got = await repo.flows.add_material("Neu", url=URL)
    assert got["created"] is False
    assert got["existing"] == {"id": "alt-1", "title": "Vorhanden", "url": URL}
    assert got["id"] == "alt-1"
    assert instanz.angelegt == []
    assert any(k["property"] == "ccm:wwwurl" for k in instanz.kriterien())


async def test_nur_die_gleiche_adresse_zaehlt():
    """Die Suche liefert Nachbarn mit -- ein Treffer ist noch keine Dublette.

    Das Beispiel fuer "dieselbe Adresse" war bis zum 09.09.2026 ``URL.upper()``
    -- also auch mit anderem **Pfad**. Seit F10 unterscheidet der Vergleich
    Pfade; gleich bleiben Schema und Host, und genau die sind hier anders
    geschrieben.
    """
    gleich = "HTTPS://EXAMPLE.ORG/Arbeitsblatt"
    instanz = Instanz([_treffer("nachbar", URL + "/2"), _treffer("gleich", gleich)])
    async with instanz.repo() as repo:
        got = await repo.flows.add_material("Neu", url=URL)
    assert got["existing"]["id"] == "gleich"


# --- F10 (Fremdpruefung 09.09.2026): der Pfad ist keine Nebensache ---------
#
# Verglichen wurde die **ganze** Adresse kleingeschrieben -- Pfad und Query
# eingeschlossen. Gemessen am 09.09.2026 galt ein Datensatz mit
# ``https://example.test/A`` als Dublette zu ``https://example.test/a``. Nach
# RFC 3986 ist ein Pfad zeichengenau; zwei Seiten koennen sich genau darin
# unterscheiden, und mit ``if_exists="return"`` bekommt der Aufrufer dann den
# falschen vorhandenen Datensatz statt des gewuenschten neuen.
#
# Das war eine **dokumentierte Entscheidung** ("der Vergleich ignoriert
# Gross-/Kleinschreibung, sonst nichts"), vom MCP so uebernommen, und dieser
# Test hielt sie fest. Sie wird hier geaendert, nicht repariert.


@pytest.mark.parametrize("gespeichert", [
    "https://example.org/ARBEITSBLATT",
    "https://example.org/arbeitsblatt",
    "https://example.org/Arbeitsblatt?v=A",
])
async def test_ein_anderer_pfad_ist_keine_dublette(gespeichert):
    instanz = Instanz([_treffer("anders", gespeichert)])
    async with instanz.repo() as repo:
        assert await find_by_url(repo, URL) is None


@pytest.mark.parametrize("gespeichert", [
    "HTTPS://example.org/Arbeitsblatt",
    "https://EXAMPLE.ORG/Arbeitsblatt",
    "https://Example.Org/Arbeitsblatt",
])
async def test_schema_und_host_bleiben_schreibungsblind(gespeichert):
    """Die Gegenprobe. Schema und Host sind nach RFC 3986 nicht
    schreibungsempfindlich -- eine Regel, die auch sie unterscheidet, meldete
    dieselbe Seite als neu und legte sie ein zweites Mal an."""
    instanz = Instanz([_treffer("gleich", gespeichert)])
    async with instanz.repo() as repo:
        gefunden = await find_by_url(repo, URL)
    assert gefunden is not None and gefunden["id"] == "gleich"


async def test_die_gespeicherte_adresse_kommt_unveraendert_zurueck():
    """Verglichen wird normalisiert, zurueckgegeben wird, was dasteht."""
    instanz = Instanz([_treffer("gleich", "HTTPS://EXAMPLE.ORG/Arbeitsblatt")])
    async with instanz.repo() as repo:
        gefunden = await find_by_url(repo, URL)
    assert gefunden is not None
    assert gefunden["url"] == "HTTPS://EXAMPLE.ORG/Arbeitsblatt"


async def test_ohne_dublette_wird_angelegt():
    instanz = Instanz([])
    async with instanz.repo() as repo:
        got = await repo.flows.add_material("Neu", url=URL)
    assert got["created"] is True
    assert got["existing"] is None
    assert got["warnings"] == []
    assert len(instanz.angelegt) == 1


async def test_eine_adresse_ohne_schema_kann_nicht_geprueft_werden():
    """Die Suche nimmt ccm:wwwurl nur als URI entgegen; "www.example.org/x"
    wandert in unresolved und wird NICHT gesendet. Bis heute verglich die
    Pruefung dann zwanzig ungefilterte Treffer und meldete "keine Dublette"
    -- genau das stille Ergebnis, das sie verhindern soll."""
    instanz = Instanz([_treffer("nachbar", "https://example.org/anderes")])
    async with instanz.repo() as repo:
        with pytest.raises(ValidationError):
            await find_by_url(repo, "www.example.org/x")
        got = await repo.flows.add_material("Neu", url="www.example.org/x")
        assert got["created"] is True
        assert got["warnings"] and "duplicate check skipped" in got["warnings"][0]
        with pytest.raises(ConflictError):
            await repo.flows.add_material("Neu", url="www.example.org/x", if_exists="raise")


async def test_ein_falsches_if_exists_wird_auch_ohne_adresse_abgelehnt():
    """Ein ausdruecklicher, aber verschriebener Wunsch darf nicht wortlos
    untergehen -- auch wenn ohne url gar keine Pruefung anstuende."""
    instanz = Instanz([])
    async with instanz.repo() as repo:
        with pytest.raises(ValidationError, match="if_exists"):
            await repo.flows.add_material("Neu", if_exists="retrun")
    assert instanz.angelegt == []


async def test_raise_wirft_bei_dublette():
    instanz = Instanz([_treffer("alt-1", URL)])
    async with instanz.repo() as repo:
        with pytest.raises(ConflictError):
            await repo.flows.add_material("Neu", url=URL, if_exists="raise")
    assert instanz.angelegt == []


async def test_create_prueft_nicht_und_legt_an():
    instanz = Instanz([_treffer("alt-1", URL)])
    async with instanz.repo() as repo:
        got = await repo.flows.add_material("Neu", url=URL, if_exists="create")
    assert got["created"] is True
    assert got["existing"] is None
    assert not any("/search/v1" in r.url.path for r in instanz.anfragen)


async def test_kann_die_instanz_nicht_pruefen_wird_das_gesagt():
    """``-default-`` kennt das Kriterium nicht. Eine Vorgabe darf fallen -- aber
    nicht stillschweigend: ``warnings`` nennt es, und angelegt wird trotzdem."""
    instanz = Instanz(kriterium_unbekannt=True)
    async with instanz.repo() as repo:
        got = await repo.flows.add_material("Neu", url=URL)
    assert got["created"] is True
    assert got["existing"] is None
    assert got["warnings"] and "ccm:wwwurl" in got["warnings"][0]


async def test_raise_ohne_pruefmoeglichkeit_ist_ein_fehler():
    """Ein ausdruecklicher Wunsch darf nicht fallen: wer ``raise`` verlangt und
    nicht bekommen kann, erfaehrt das als Fehler, nicht als Anlage."""
    instanz = Instanz(kriterium_unbekannt=True)
    async with instanz.repo() as repo:
        with pytest.raises(ConflictError):
            await repo.flows.add_material("Neu", url=URL, if_exists="raise")
    assert instanz.angelegt == []


async def test_ohne_adresse_gibt_es_nichts_zu_pruefen():
    instanz = Instanz([_treffer("alt-1", URL)])
    async with instanz.repo() as repo:
        got = await repo.flows.add_material("Neu")
    assert got["created"] is True
    assert not any("/search/v1" in r.url.path for r in instanz.anfragen)


async def test_eine_schemalose_adresse_kostet_keine_anfrage():
    """Die Suche nimmt nur http(s) -- das weiss die Pruefung selbst, statt erst
    Vokabular und eine ungefilterte Suche zu bezahlen."""
    instanz = Instanz([])
    async with instanz.repo() as repo:
        with pytest.raises(ValidationError):
            await find_by_url(repo, "www.example.org/x")
    assert instanz.anfragen == []


# --- TST-6: warum die zweite Verteidigungslinie nie anschlaegt -----------


async def test_eine_http_adresse_ist_nie_unaufloesbar():
    """``find_by_url`` prueft das Schema und wirft davor; danach reicht
    ``resolve_all`` jedes ``http(s)://`` unveraendert durch. Der
    ``unresolved``-Zweig darunter ist deshalb ueber diesen Weg **nicht
    erreichbar** -- er ist zweite Verteidigungslinie, so auch im Kommentar
    benannt.

    Dieser Test pinnt die Annahme, auf der das beruht. Wer ``_is_uri`` oder
    die Schemapruefung aendert, faellt hier auf und nicht erst im Betrieb
    (Audit TST-6)."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.search(
            filters={"ccm:wwwurl": "https://beispiel.test/seite"}, limit=5)
    assert ergebnis.unresolved == []
