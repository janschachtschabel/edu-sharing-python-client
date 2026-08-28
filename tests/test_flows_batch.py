"""Viele Knoten auf einmal, und „mehr davon".

Zwei Abläufe, die der MCP als ``get_nodes_details`` und ``get_related_content``
anbietet.

``related`` ist **keine** Relation im Sinne von ``/relation/v1``. Es ist
„mehr davon": die Fächer und Stufen des Ausgangsknotens werden zu Filtern einer
gewöhnlichen Suche, der Knoten selbst fällt aus dem Ergebnis. Der MCP macht es
genauso, und der Unterschied gehört benannt, weil beide Dinge gleich heißen.

``describe_many`` muss einen fehlenden Knoten überleben: gemessen am
27.08.2026 waren **4 von 25** Treffern des Suchindex nicht mehr abrufbar. Ein
einzelner 404 darf die ganze Liste nicht mitreißen.
"""

import json

import httpx

from edusharing import AsyncRepository

REPO = "https://repo.test/edu-sharing"

# Je Property ein eigenes Vokabular -- eine gemeinsame Liste liesse jeden
# zweiten Filter als unaufloesbar herausfallen.
VOKABULAR = {
    "ccm:taxonid": [{"key": "http://vocab.test/080", "displayString": "Biologie"}],
    "ccm:educationalcontext": [{"key": "http://vocab.test/sek1",
                                "displayString": "Sekundarstufe I"}],
}


def _knoten(nid: str, titel: str, *, fach: str | None = "http://vocab.test/080",
            stufe: str | None = "http://vocab.test/sek1") -> dict:
    eigenschaften: dict[str, list[str]] = {"cclom:title": [titel]}
    if fach:
        eigenschaften["ccm:taxonid"] = [fach]
        eigenschaften["ccm:taxonid_DISPLAYNAME"] = ["Biologie"]
    if stufe:
        eigenschaften["ccm:educationalcontext"] = [stufe]
        eigenschaften["ccm:educationalcontext_DISPLAYNAME"] = ["Sekundarstufe I"]
    return {"ref": {"id": nid}, "title": titel, "type": "ccm:io",
            "properties": eigenschaften}


class Instanz:
    def __init__(self, *, knoten: dict[str, dict] | None = None,
                 treffer: list[dict] | None = None) -> None:
        self.knoten = knoten if knoten is not None else {
            "a": _knoten("a", "Zellteilung")}
        self.treffer = treffer if treffer is not None else [
            _knoten("a", "Zellteilung"), _knoten("b", "Photosynthese")]
        self.anfragen: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad = request.url.path
        if "/values" in pfad:
            # Die Property steht im Body, nicht im Pfad.
            prop = json.loads(request.content)["valueParameters"]["property"]
            return httpx.Response(200, json={"values": VOKABULAR.get(prop, [])})
        if "/search/v1" in pfad:
            return httpx.Response(200, json={
                "nodes": self.treffer,
                "pagination": {"total": len(self.treffer), "from": 0,
                               "count": len(self.treffer)}})
        nid = pfad.rsplit("/metadata", 1)[0].rsplit("/", 1)[-1]
        if nid not in self.knoten:
            return httpx.Response(404, json={
                "error": "org.edu_sharing.restservices.DAOMissingException",
                "message": f"Node does not exist: {nid}"})
        return httpx.Response(200, json={"node": self.knoten[nid]})

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, metadataset="mds_oeh", backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))

    def kriterien(self) -> list[dict]:
        for r in reversed(self.anfragen):
            if "/search/v1" in r.url.path:
                return json.loads(r.content)["criteria"]
        raise AssertionError("keine Suchanfrage")


# --- describe_many --------------------------------------------------------

async def test_mehrere_knoten_auf_einmal():
    instanz = Instanz(knoten={"a": _knoten("a", "Eins"), "b": _knoten("b", "Zwei")})
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.describe_many(["a", "b"])
    assert [n["id"] for n in ergebnis["nodes"]] == ["a", "b"]
    assert ergebnis["requested"] == 2
    assert ergebnis["found"] == 2
    assert ergebnis["failed"] == []


async def test_ein_fehlender_knoten_reisst_die_liste_nicht_mit():
    """Gemessen waren 4 von 25 Treffern des Suchindex nicht mehr abrufbar. Wer
    die ganze Liste verliert, weil einer fehlt, kann die Suche nicht
    weiterverarbeiten."""
    instanz = Instanz(knoten={"a": _knoten("a", "Eins")})
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.describe_many(["a", "weg", "auch-weg"])
    assert [n["id"] for n in ergebnis["nodes"]] == ["a"]
    assert [f["id"] for f in ergebnis["failed"]] == ["weg", "auch-weg"]
    assert "NotFoundError" in ergebnis["failed"][0]["reason"]
    assert ergebnis["requested"] == 3
    assert ergebnis["found"] == 1


async def test_die_reihenfolge_bleibt_die_der_anfrage():
    """Sonst laesst sich das Ergebnis nicht mit der Eingabe zusammenbringen."""
    instanz = Instanz(knoten={n: _knoten(n, n.upper()) for n in "abc"})
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.describe_many(["c", "a", "b"])
    assert [n["id"] for n in ergebnis["nodes"]] == ["c", "a", "b"]


async def test_eine_leere_liste_ist_kein_fehler():
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.describe_many([])
    assert ergebnis == {"requested": 0, "found": 0, "nodes": [], "failed": []}
    assert instanz.anfragen == []


async def test_doppelte_ids_werden_einmal_geholt():
    """Zwei Anfragen fuer denselben Knoten kosten zweimal und liefern
    dasselbe."""
    instanz = Instanz(knoten={"a": _knoten("a", "Eins")})
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.describe_many(["a", "a", "a"])
    assert len(instanz.anfragen) == 1
    assert [n["id"] for n in ergebnis["nodes"]] == ["a"]
    assert ergebnis["requested"] == 1


async def test_die_antwort_ist_json():
    instanz = Instanz()
    async with instanz.repo() as repo:
        json.dumps(await repo.flows.describe_many(["a", "weg"]))


# --- related --------------------------------------------------------------

async def test_mehr_davon_filtert_nach_fach_und_stufe():
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.flows.related("a")
    felder = {k["property"] for k in instanz.kriterien()}
    assert "ccm:taxonid" in felder
    assert "ccm:educationalcontext" in felder


async def test_der_ausgangsknoten_faellt_heraus():
    """Sonst steht das Material, von dem man ausging, als sein eigener
    Verwandter in der Liste."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.related("a")
    assert [h["id"] for h in ergebnis["hits"]] == ["b"]


async def test_die_grundlage_wird_genannt():
    """Wer nicht weiss, worauf die Aehnlichkeit beruht, kann sie nicht
    beurteilen."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.related("a")
    assert ergebnis["based_on"] == {"subject": ["Biologie"],
                                    "level": ["Sekundarstufe I"]}
    assert ergebnis["seed"]["title"] == "Zellteilung"


async def test_ohne_fach_und_stufe_kommen_keine_willkuerlichen_treffer():
    """Eine ungefilterte Suche waere keine Antwort auf 'mehr davon' -- sie
    waere irgendetwas."""
    instanz = Instanz(knoten={"a": _knoten("a", "Ohne", fach=None, stufe=None)})
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.related("a")
    assert ergebnis["hits"] == []
    assert "subject" in ergebnis["reason"] or "level" in ergebnis["reason"]
    assert not [r for r in instanz.anfragen if "/search/v1" in r.url.path]


async def test_die_felder_lassen_sich_waehlen():
    """subject und level sind eine Vorgabe, keine Festlegung -- welche
    Kurznamen es gibt, entscheidet der Metadatensatz der Instanz."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.flows.related("a", on=("subject",))
    felder = {k["property"] for k in instanz.kriterien()}
    assert "ccm:taxonid" in felder
    assert "ccm:educationalcontext" not in felder


async def test_ein_unbekannter_kurzname_wird_gemeldet():
    from edusharing.errors import ValidationError
    instanz = Instanz()
    async with instanz.repo() as repo:
        try:
            await repo.flows.related("a", on=("gibtesnicht",))
        except ValidationError as fehler:
            assert "gibtesnicht" in str(fehler)
        else:
            raise AssertionError("ein Tippfehler darf nicht als 'kein Filter' durchgehen")


async def test_ein_unaufloesbarer_wert_wird_gemeldet():
    """Der Filter waere sonst stillschweigend weggefallen und die Aehnlichkeit
    breiter, als sie aussieht. Hier traegt der Knoten ein Fach, dessen Label
    das Vokabular der Instanz nicht kennt -- gemessen kommt das vor, wenn
    Bestand aelter ist als der Metadatensatz."""
    fremd = _knoten("a", "Mit fremdem Fach")
    fremd["properties"]["ccm:taxonid_DISPLAYNAME"] = ["Gibtesnicht"]
    instanz = Instanz(knoten={"a": fremd})
    async with instanz.repo() as repo:
        ergebnis = await repo.flows.related("a")
    assert ergebnis["unresolved"], "der nicht angewandte Filter wird genannt"
