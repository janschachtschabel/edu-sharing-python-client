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
from edusharing.flows.duplicates import check_before_create, find_by_url

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


async def test_eine_leere_adresse_ist_keine_adresse():
    """Gemessen am 10.09.2026: ``url=""`` schrieb ``ccm:wwwurl: ['']`` in den
    Datensatz.

    Ein leeres Formularfeld ist keine Quelladresse. Der Datensatz trug danach
    eine Quelle, die auf nichts zeigt -- und weil ``find_by_url`` einen leeren
    String vorne abweist, findet ihn auch keine Dublettenpruefung je wieder.
    ``url=""`` verhaelt sich jetzt wie ``url=None``.
    """
    instanz = Instanz([])
    async with instanz.repo() as repo:
        got = await repo.flows.add_material("Neu", url="")
    assert got["created"] is True
    assert "ccm:wwwurl" not in instanz.angelegt[-1], (
        "eine leere Adresse gehoert nicht in den Datensatz")
    assert not any("/search/v1" in r.url.path for r in instanz.anfragen)
    # Keine Warnung: es ist keine Pruefung ausgefallen, es gab nichts zu
    # pruefen. Das unterscheidet diesen Fall von einer unbrauchbaren Adresse.
    assert got["warnings"] == []


async def test_eine_adresse_aus_leerzeichen_ebenso():
    instanz = Instanz([])
    async with instanz.repo() as repo:
        got = await repo.flows.add_material("Neu", url="   ")
    assert got["created"] is True
    assert "ccm:wwwurl" not in instanz.angelegt[-1]


async def test_eine_leere_adresse_laesst_auch_raise_durch():
    """``if_exists="raise"`` hat ohne Adresse nichts, woran es sich stossen
    koennte -- und darf deshalb nicht stolpern."""
    instanz = Instanz([_treffer("alt-1", URL)])
    async with instanz.repo() as repo:
        got = await repo.flows.add_material("Neu", url="", if_exists="raise")
    assert got["created"] is True


async def test_eine_echte_adresse_wird_weiterhin_geschrieben():
    """Die Gegenprobe. Ohne sie waere die Aenderung gruen, indem sie jede
    Adresse verschluckt."""
    instanz = Instanz([])
    async with instanz.repo() as repo:
        got = await repo.flows.add_material("Neu", url=URL)
    assert got["created"] is True
    assert instanz.angelegt[-1]["ccm:wwwurl"] == [URL]
    assert any("/search/v1" in r.url.path for r in instanz.anfragen), (
        "eine echte Adresse wird weiterhin auf Dubletten geprueft")


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


# --- R09 (Zweitpruefung 09.09.2026): ein unlesbarer Kandidat ---------------
#
# Die komponentenweise Verarbeitung aus F10 ruft ``urlsplit`` -- ohne
# Behandlung. Eine fremde gespeicherte ``ccm:wwwurl`` muss aber nicht
# syntaktisch gueltig sein. Gemessen am 09.09.2026: ein Kandidat mit
# ``https://[broken`` beendete ``find_by_url`` mit ``ValueError: Invalid IPv6
# URL`` -- keine Bibliotheksausnahme, und ``add_material`` bricht davor ab.
#
# Die alte rohe Zeichenkettenpruefung war fuer Pfad-Gleichheit falsch, konnte
# an keinem Kandidaten aber scheitern. Ein Fix, der eine neue Fehlerart
# einfuehrt, gehoert zu Ende gebracht.

KAPUTT = "https://[broken"


async def test_ein_kaputter_kandidat_beendet_die_pruefung_nicht():
    """Er ist nicht dieselbe Adresse wie eine gueltige -- also wird er
    uebersprungen, nicht beklagt."""
    instanz = Instanz([_treffer("kaputt", KAPUTT), _treffer("gleich", URL)])
    async with instanz.repo() as repo:
        gefunden = await find_by_url(repo, URL)
    assert gefunden is not None and gefunden["id"] == "gleich"


async def test_ein_kaputter_kandidat_allein_heisst_keine_dublette():
    instanz = Instanz([_treffer("kaputt", KAPUTT)])
    async with instanz.repo() as repo:
        assert await find_by_url(repo, URL) is None


async def test_eine_kaputte_eigene_adresse_ist_ein_bibliotheksfehler():
    """Der andere Fall, und er ist ein anderer: die Adresse kommt vom
    Aufrufer, und er soll erfahren, dass sie unbrauchbar ist."""
    instanz = Instanz([])
    async with instanz.repo() as repo:
        with pytest.raises(ValidationError):
            await find_by_url(repo, KAPUTT)


async def test_add_material_bricht_an_einem_kaputten_nachbarn_nicht_ab():
    """Der Weg, auf dem es wirklich weh tut."""
    instanz = Instanz([_treffer("kaputt", KAPUTT)])
    async with instanz.repo() as repo:
        got = await repo.flows.add_material("Neu", url=URL)
    assert got["created"] is True


# --- A02 (Drittpruefung 10.09.2026) ----------------------------------------
#
# Der Fehlerpfad fuer die **eigene** Adresse interpolierte sie roh. Steht ein
# Passwort darin, steht es in der Meldung -- und ueber ``check_before_create``
# in den Warnungen und im ConflictError. Gemessen am 10.09.2026 an sechs
# Stellen des Moduls; kein Netzwerkaufruf noetig, die Offenlegung passiert
# beim Bauen des Textes.
#
# ``mask_userinfo`` liegt seit F06 in ``urls`` und wurde hier nicht benutzt.

GEHEIM = "DUMMY_AUDIT_PASSWORD"
MIT_GEHEIMNIS = f"https://alice:{GEHEIM}@example.org/Arbeitsblatt"
KAPUTT_MIT_GEHEIMNIS = f"https://alice:{GEHEIM}@[broken"
FTP_MIT_GEHEIMNIS = f"ftp://alice:{GEHEIM}@example.org/x"


async def test_eine_unlesbare_eigene_adresse_zeigt_kein_passwort():
    instanz = Instanz([])
    async with instanz.repo() as repo:
        with pytest.raises(ValidationError) as fehler:
            await find_by_url(repo, KAPUTT_MIT_GEHEIMNIS)
    assert GEHEIM not in str(fehler.value)
    # Aber die Adresse bleibt erkennbar -- sonst weiss der Aufrufer nicht,
    # welche gemeint ist.
    assert "***@" in str(fehler.value)


async def test_eine_adresse_ohne_http_schema_zeigt_kein_passwort():
    """Der zweite Fehlerpfad. Der Bericht nennt ihn nicht eigens; gemessen
    leckt er genauso."""
    instanz = Instanz([])
    async with instanz.repo() as repo:
        with pytest.raises(ValidationError) as fehler:
            await find_by_url(repo, FTP_MIT_GEHEIMNIS)
    assert GEHEIM not in str(fehler.value)


async def test_die_uebersprungene_pruefung_warnt_ohne_passwort():
    """``if_exists='return'``: die Pruefung faellt aus, das wird gesagt --
    und die Warnung landet oft in einem Protokoll."""
    instanz = Instanz([])
    async with instanz.repo() as repo:
        _, warnungen = await check_before_create(
            repo, KAPUTT_MIT_GEHEIMNIS, "return")
    assert warnungen, "die ausgefallene Pruefung wird gesagt, nicht verschwiegen"
    assert not any(GEHEIM in w for w in warnungen)


async def test_die_ausgefallene_pruefung_wirft_ohne_passwort():
    """``if_exists='raise'``: der aeussere ConflictError baut seinen eigenen
    Text -- die Maskierung an der Quelle allein reicht dort nicht."""
    instanz = Instanz([])
    async with instanz.repo() as repo:
        with pytest.raises(ConflictError) as fehler:
            await check_before_create(repo, KAPUTT_MIT_GEHEIMNIS, "raise")
    assert GEHEIM not in str(fehler.value)


async def test_die_gefundene_dublette_meldet_ohne_passwort():
    """Die sechste Stelle: eine gueltige Adresse **mit** Zugangsdaten findet
    ihre Dublette -- und der ConflictError gab sie woertlich wieder."""
    instanz = Instanz([_treffer("alt-1", MIT_GEHEIMNIS)])
    async with instanz.repo() as repo:
        with pytest.raises(ConflictError) as fehler:
            await check_before_create(repo, MIT_GEHEIMNIS, "raise")
    assert GEHEIM not in str(fehler.value)
    assert "alt-1" in str(fehler.value)


async def test_eine_gewoehnliche_adresse_steht_weiter_woertlich_da():
    """Die Gegenprobe. Eine Maskierung, die jede Adresse unkenntlich macht,
    waere gruen und nutzlos -- die Meldung soll sagen, um welche es geht."""
    instanz = Instanz([])
    async with instanz.repo() as repo:
        with pytest.raises(ValidationError) as fehler:
            await find_by_url(repo, KAPUTT)
    assert KAPUTT in str(fehler.value)


async def test_ein_at_im_pfad_wird_mitmaskiert_und_das_ist_gewollt():
    """Der gemessene Preis der Maskierung, hier festgehalten statt spaeter
    entdeckt.

    ``mask_userinfo`` kann eine Adresse nicht zergliedern, die **gerade
    deshalb** in der Meldung steht, weil sie kaputt ist -- also nimmt es jedes
    ``...@``. Ein ``@`` im Pfad faellt mit. Eine Meldung, die ein
    Pfadstueck weniger zeigt, ist die billige Seite dieses Tauschs; eine, die
    ein Passwort zeigt, nicht.
    """
    instanz = Instanz([])
    async with instanz.repo() as repo:
        with pytest.raises(ValidationError) as fehler:
            await find_by_url(repo, "https://[a@b")
    assert "***@b" in str(fehler.value)


async def test_die_suche_bekommt_die_adresse_unveraendert():
    """Die zweite Gegenprobe: maskiert wird die **Meldung**, nicht die
    Abfrage. Sonst faende die Pruefung ihre Dublette nicht mehr."""
    instanz = Instanz([_treffer("alt-1", MIT_GEHEIMNIS)])
    async with instanz.repo() as repo:
        gefunden = await find_by_url(repo, MIT_GEHEIMNIS)
    assert gefunden is not None and gefunden["id"] == "alt-1"
    assert instanz.kriterien()[0]["values"] == [MIT_GEHEIMNIS]
