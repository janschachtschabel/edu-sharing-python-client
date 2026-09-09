"""Serienobjekte -- weitere Dokumente an einem Hauptdokument.

Ein Material kann zusaetzliche Dateien tragen: das Arbeitsblatt und sein
Loesungsblatt, ein Hauptdokument und seine Anhaenge. edu-sharing fuehrt die als
**Kindobjekte** unter dem Hauptknoten, und die Kombination, die das erzeugt, ist
nicht zu erraten.

Gemessen gegen Staging am 27.08.2026, nachdem der erste Versuch scheiterte:

    type=ccm:io_childobject              -> HTTP 500, der Typ existiert nicht
    type=ccm:io (ohne assocType)         -> HTTP 500, Integritaetsverletzung
    type=ccm:io + assocType=ccm:childio
        + aspects=ccm:io_childobject     -> angelegt

``ccm:io_childobject`` ist ein **Aspekt**, kein Typ -- daran scheiterte der
erste Anlauf. Der Weg stammt aus der Ideendatenbank, die ihn produktiv nutzt.
"""

import json
import logging

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.childobjects import LIST_MAX
from edusharing.errors import EduSharingError, ValidationError

REPO = "https://repo.test/edu-sharing"
HAUPT = "haupt-1"

CHILD_ASPECT = "ccm:io_childobject"


def _kind(node_id: str, name: str, order: str | None, *, serie: bool = True) -> dict:
    props = {"cm:name": [name]}
    if order is not None:
        props["ccm:childobject_order"] = [order]
    return {
        "ref": {"id": node_id}, "name": name, "title": name, "type": "ccm:io",
        "aspects": [CHILD_ASPECT] if serie else ["cm:versionable"],
        "createdAt": f"2026-08-27T10:0{order or 9}:00Z",
        "content": {"hash": "-1"}, "properties": props,
    }


class Instanz:
    """Merkt sich, was angelegt wurde, und antwortet danach."""

    def __init__(self, kinder=None, upload_fehler: bool = False) -> None:
        self.anfragen: list[httpx.Request] = []
        self.kinder = list(kinder or [])
        self.upload_fehler = upload_fehler
        self.geloescht: list[str] = []

    def __call__(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad, methode = request.url.path, request.method

        if methode == "POST" and pfad.rstrip("/").endswith("/children"):
            koerper = json.loads(request.content)
            name = (koerper.get("cm:name") or ["?"])[0]
            order = (koerper.get("ccm:childobject_order") or [None])[0]
            neu = _kind(f"kind-{len(self.kinder)}", name, order)
            self.kinder.append(neu)
            return httpx.Response(200, json={"node": neu})
        if methode == "POST" and "/content" in pfad:
            if self.upload_fehler:
                return httpx.Response(403, json={"error": "kein Zugriff"})
            return httpx.Response(200, json={"node": self.kinder[-1]})
        if methode == "GET" and pfad.endswith("/children"):
            return httpx.Response(200, json={
                "nodes": self.kinder,
                "pagination": {"total": len(self.kinder), "from": 0,
                               "count": len(self.kinder)}})
        if methode == "DELETE":
            self.geloescht.append(pfad.rstrip("/").split("/")[-1])
            return httpx.Response(200, content=b"")
        knoten_id = pfad.split("/-home-/")[1].split("/")[0] if "/-home-/" in pfad else HAUPT
        passend = next((k for k in self.kinder
                        if (k.get("ref") or {}).get("id") == knoten_id), None)
        return httpx.Response(200, json={"node": passend or _kind(HAUPT, "haupt.txt",
                                                                  None, serie=False)})


class OhneLoeschen(Instanz):
    """Wie ``Instanz``, verweigert aber auch das Aufraeumen."""

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.method == "DELETE":
            self.anfragen.append(request)
            return httpx.Response(403, json={"error": "auch das nicht"})
        return super().__call__(request)


class OhneZaehlung(Instanz):
    """Wie ``Instanz``, schickt aber kein ``pagination`` mit.

    ``list()`` traegt so einer Antwort ausdruecklich Rechnung. Gemessen ist
    sie nicht -- am 09.09.2026 nannte jeder Endpunkt, den diese Bibliothek
    auflistet, eine Zahl. Geprueft wird sie trotzdem, denn keine Antwort
    dieses Moduls darf daran haengen, dass jemand eine nennt.
    Drei Tests brauchen sie und trugen sie dreimal (Pruefung 09.09.2026).
    """

    def __call__(self, request: httpx.Request) -> httpx.Response:
        if request.method == "GET" and request.url.path.endswith("/children"):
            self.anfragen.append(request)
            return httpx.Response(200, json={"nodes": self.kinder})
        return super().__call__(request)


def _repo(instanz) -> AsyncRepository:
    return AsyncRepository(
        REPO, backoff_base=0.0,
        client=httpx.AsyncClient(transport=httpx.MockTransport(instanz)))


# --- Lesen ----------------------------------------------------------------

async def test_nur_serienobjekte_werden_gelistet():
    """Unter einem Hauptknoten haengen auch andere Kinder -- Versionen etwa.
    Ohne die Filterung auf den Aspekt kaemen die als Anhaenge zurueck."""
    instanz = Instanz(kinder=[
        _kind("a", "anhang.txt", "0"),
        _kind("version", "alte-fassung.txt", None, serie=False),
    ])
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        kinder = await node.children.list()
    assert [k.name for k in kinder] == ["anhang.txt"]


async def test_reihenfolge_folgt_dem_ordnungsfeld():
    instanz = Instanz(kinder=[
        _kind("c", "drittens.txt", "2"),
        _kind("a", "erstens.txt", "0"),
        _kind("b", "zweitens.txt", "1"),
    ])
    async with _repo(instanz) as repo:
        kinder = await (await repo.node(HAUPT)).children.list()
    assert [k.name for k in kinder] == ["erstens.txt", "zweitens.txt", "drittens.txt"]


async def test_ohne_ordnungsfeld_ans_ende_und_dann_nach_alter():
    """Ein Kind ohne Ordnungsangabe darf nicht zufaellig vorn landen."""
    instanz = Instanz(kinder=[
        _kind("ohne", "ohne-order.txt", None),
        _kind("mit", "mit-order.txt", "0"),
    ])
    async with _repo(instanz) as repo:
        kinder = await (await repo.node(HAUPT)).children.list()
    assert [k.name for k in kinder] == ["mit-order.txt", "ohne-order.txt"]


async def test_keine_kinder_ist_kein_fehler():
    async with _repo(Instanz()) as repo:
        assert await (await repo.node(HAUPT)).children.list() == []


# --- Anlegen --------------------------------------------------------------

async def test_anlegen_setzt_aspekt_und_assoziation():
    """Die Kombination ist der ganze Punkt: ccm:io_childobject ist ein ASPEKT,
    kein Typ. Als Typ gesetzt antwortet die Instanz mit HTTP 500."""
    instanz = Instanz()
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        await node.children.add(b"Inhalt", filename="anhang.txt",
                                mimetype="text/plain")

    angelegt = next(r for r in instanz.anfragen
                    if r.method == "POST" and r.url.path.rstrip("/").endswith("/children"))
    assert angelegt.url.params.get("type") == "ccm:io"
    assert angelegt.url.params.get("assocType") == "ccm:childio"
    assert angelegt.url.params.get("aspects") == CHILD_ASPECT


async def test_anlegen_haengt_hinten_an():
    """Ohne eigene Angabe bekommt das neue Kind die naechste freie Nummer --
    sonst konkurrieren zwei Anhaenge um dieselbe Position."""
    instanz = Instanz(kinder=[_kind("a", "erstens.txt", "0"),
                              _kind("b", "zweitens.txt", "1")])
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        await node.children.add(b"x", filename="drittens.txt", mimetype="text/plain")

    angelegt = next(r for r in instanz.anfragen
                    if r.method == "POST" and r.url.path.rstrip("/").endswith("/children"))
    assert json.loads(angelegt.content)["ccm:childobject_order"] == ["2"]


async def test_eigene_reihenfolge_wird_uebernommen():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        await node.children.add(b"x", filename="a.txt", mimetype="text/plain", order=7)
    angelegt = next(r for r in instanz.anfragen
                    if r.method == "POST" and r.url.path.rstrip("/").endswith("/children"))
    assert json.loads(angelegt.content)["ccm:childobject_order"] == ["7"]


async def test_die_datei_wird_hochgeladen():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        kind = await node.children.add(b"Der Inhalt", filename="a.txt",
                                       mimetype="text/plain")
    assert kind.id
    assert any("/content" in r.url.path for r in instanz.anfragen), \
        "ohne Datei ist das Kind ein leerer Rumpf"


async def test_scheiternder_upload_hinterlaesst_keinen_rumpf():
    """Aus der Ideendatenbank uebernommen: ein Kindknoten ohne Inhalt ist
    Datenmuell. Anlegen und Hochladen sind zwei Aufrufe, und der zweite kann
    fuer sich scheitern."""
    instanz = Instanz(upload_fehler=True)
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        with pytest.raises(EduSharingError):
            await node.children.add(b"x", filename="a.txt", mimetype="text/plain")
    assert instanz.geloescht, "der Rumpf blieb stehen"


async def test_ein_fehlschlagendes_aufraeumen_verdeckt_nicht_den_grund():
    """Wenn schon der Upload scheitert und danach auch das Aufraeumen, ist die
    Upload-Meldung die, die der Aufrufer braucht. Der Rumpf bleibt dann stehen
    -- unschoen, aber besser als eine Fehlermeldung ueber das Aufraeumen."""
    instanz = OhneLoeschen(upload_fehler=True)
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        with pytest.raises(EduSharingError) as fehler:
            await node.children.add(b"x", filename="a.txt", mimetype="text/plain")
    assert "403" in str(fehler.value)
    assert any(r.method == "DELETE" for r in instanz.anfragen), (
        "das Aufraeumen wurde gar nicht erst versucht")


async def test_ein_stehengebliebener_rumpf_wird_gemeldet(caplog):
    """Bleibt der Rumpf stehen, muss wenigstens seine ID im Log stehen.

    Der Aufrufer bekommt die Upload-Meldung, und die kennt den Kindknoten
    nicht. Ohne Logzeile liegt also Datenmuell im Repositorium, den niemand mehr
    zuordnen kann -- die Ausnahme zu schlucken ist richtig, sie zu verschweigen
    nicht. Andere Module der Bibliothek melden solche Faelle ebenso
    (``transport``, ``extraction``).
    """
    instanz = OhneLoeschen(upload_fehler=True)
    with caplog.at_level(logging.WARNING, logger="edusharing.childobjects"):
        async with _repo(instanz) as repo:
            node = await repo.node(HAUPT)
            with pytest.raises(EduSharingError):
                await node.children.add(b"x", filename="a.txt",
                                        mimetype="text/plain")

    meldungen = [r.getMessage() for r in caplog.records]
    assert any("kind-0" in m for m in meldungen), (
        f"die ID des stehengebliebenen Rumpfes fehlt im Log: {meldungen}")


async def test_ein_kind_ohne_id_ist_ein_fehler():
    """Ohne ID laesst sich nichts hochladen und nichts wieder aufraeumen."""
    class OhneId(Instanz):
        def __call__(self, request):
            pfad = request.url.path.rstrip("/")
            if request.method == "POST" and pfad.endswith("/children"):
                self.anfragen.append(request)
                return httpx.Response(200, json={"node": {"ref": {}}})
            return super().__call__(request)

    instanz = OhneId()
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        with pytest.raises(EduSharingError):
            await node.children.add(b"x", filename="a.txt", mimetype="text/plain")


async def test_lesbare_darstellung():
    """repr taucht in Fehlermeldungen und Protokollen auf."""
    async with _repo(Instanz()) as repo:
        node = await repo.node(HAUPT)
        assert HAUPT in repr(node.children)


async def test_leerer_dateiname_wird_abgelehnt():
    instanz = Instanz()
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        with pytest.raises(ValidationError):
            await node.children.add(b"x", filename="  ", mimetype="text/plain")
    assert not instanz.anfragen or all(r.method == "GET" for r in instanz.anfragen)


# --- Ablauf-Ebene ---------------------------------------------------------

async def test_flow_liefert_die_serienobjekte_als_json():
    instanz = Instanz(kinder=[_kind("a", "loesung.pdf", "0")])
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.child_objects(HAUPT)
    assert ergebnis["id"] == HAUPT
    assert ergebnis["count"] == 1
    assert ergebnis["children"][0]["name"] == "loesung.pdf"
    assert ergebnis["children"][0]["order"] == 0
    json.dumps(ergebnis)


async def test_flow_meldet_none_wenn_ein_kind_keine_position_traegt():
    """Ein Kind ohne Position bekommt ``None``, nicht 0.

    0 ist eine gueltige Position -- die erste. Wer sie fuer "hat keine"
    haelt, sortiert ein unpositioniertes Kind vor alle anderen. Ebenso
    ``"zwei"``: eine Position, die keine Zahl ist, ist keine.
    """
    instanz = Instanz(kinder=[
        _kind("ohne", "ohne.pdf", None),
        _kind("krumm", "krumm.pdf", "zwei"),
    ])
    async with _repo(instanz) as repo:
        ergebnis = await repo.flows.child_objects(HAUPT)
    assert [k["order"] for k in ergebnis["children"]] == [None, None]
    json.dumps(ergebnis)


# --- Der Deckel (Audit MNT-4) ---------------------------------------------
#
# Die Auflistung nahm hart 200 und sagte nichts. Sie ist die einzige in dieser
# Bibliothek, die kuerzt, ohne es auszuweisen -- jede andere nimmt ein
# ``limit`` und gibt ein ``total`` zurueck. Wer ``len(node.children.list())``
# liest, liest die Zahl der Anhaenge; bei 250 bekam er 200 und nichts sonst.

class MitVielen(Instanz):
    """Meldet mehr Kinder, als sie ausliefert -- wie eine Instanz mit einem
    Bestand ueber der Seitengroesse."""

    def __init__(self, gesamt: int, geliefert: int) -> None:
        super().__init__(kinder=[_kind(f"k{i}", f"{i}.txt", str(i))
                                 for i in range(geliefert)])
        self.gesamt = gesamt

    def __call__(self, request):
        if request.method == "GET" and request.url.path.endswith("/children"):
            self.anfragen.append(request)
            return httpx.Response(200, json={
                "nodes": self.kinder,
                "pagination": {"total": self.gesamt, "from": 0,
                               "count": len(self.kinder)}})
        return super().__call__(request)


async def test_eine_gekuerzte_liste_wird_gemeldet_statt_ausgeliefert():
    """Es gibt keine Verwendung, fuer die die ersten 200 richtig waeren: man
    laedt sie herunter, zeigt sie an oder zaehlt sie. Die Rueckgabe ist eine
    Liste und hat keinen Platz fuer "unvollstaendig", also muss es der Fehler
    sagen."""
    async with _repo(MitVielen(gesamt=250, geliefert=200)) as repo:
        node = await repo.node(HAUPT)
        with pytest.raises(EduSharingError, match="250"):
            await node.children.list()


async def test_genau_am_deckel_ist_kein_fehler():
    """Gegenprobe: die Grenze selbst ist noch vollstaendig."""
    async with _repo(MitVielen(gesamt=200, geliefert=200)) as repo:
        node = await repo.node(HAUPT)
        assert len(await node.children.list()) == 200


# --- Die Zaehlung beim Anhaengen ------------------------------------------

async def test_anlegen_liest_die_kinder_genau_einmal():
    """Was MNT-4 wirklich beanstandete: "attaching N files costs 3N
    requests" -- also die **Zahl** der Anfragen.

    Die Abkuerzung, mit der das behoben wurde (eine Seite mit einem
    Datensatz, gelesen wird nur ihre Gesamtzahl), ist am 09.09.2026
    zurueckgenommen worden: sie beantwortete die falsche Frage. Die Zahl
    der Kinder ist nur dann die naechste freie Stelle, wenn die Nummern
    lueckenlos bei 0 beginnen -- siehe
    ``test_die_position_folgt_der_hoechsten_vergebenen``.

    Was bleibt, ist die Ersparnis, um die es ging: **eine** Lesung, nicht
    eine je angehaengter Datei.
    """
    instanz = Instanz(kinder=[_kind("a", "a.txt", "0")])
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        await node.children.add(b"x", filename="b.txt", mimetype="text/plain")

    gelesen = [r for r in instanz.anfragen
               if r.method == "GET" and r.url.path.endswith("/children")]
    assert len(gelesen) == 1, [str(r.url) for r in gelesen]


async def test_ohne_gesamtzahl_zaehlt_das_anlegen_trotzdem_richtig():
    """Der Rueckfall von ``_count``, und der teure Fall dieser Aenderung.

    ``page_total`` liefert ohne ``pagination`` die Vorgabe -- das war 0, also
    bekam **jeder** Anhang die Position 0 und alle konkurrierten um dieselbe
    Stelle (Pruefung 08.09.2026). ``list()`` toleriert so eine Antwort
    ausdruecklich; gemessen ist sie nicht (siehe ``OhneZaehlung``).

    Zaehlt niemand, wird gezaehlt wie vorher -- eine volle Auflistung ist
    teurer als eine Seite, aber eine falsche Position kostet die Reihenfolge.
    """
    instanz = OhneZaehlung(kinder=[_kind("a", "a.txt", "0"),
                                   _kind("b", "b.txt", "1")])
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        await node.children.add(b"x", filename="c.txt", mimetype="text/plain")

    angelegt = next(r for r in instanz.anfragen
                    if r.method == "POST" and r.url.path.rstrip("/").endswith("/children"))
    assert json.loads(angelegt.content)["ccm:childobject_order"] == ["2"]


async def test_genau_am_deckel_ohne_gesamtzahl_ist_vollstaendig():
    """Genau ``LIST_MAX`` Kinder und keine genannte Zahl -- und trotzdem
    kein Fehler.

    Bis zum 09.09.2026 wurde das faelschlich abgelehnt: eine volle Seite war
    das Bild einer Kappung, und ohne ``pagination`` liess sich das nicht
    unterscheiden. Die falsche Ablehnung stand als bewusster Preis dabei.

    Sie war nicht noetig. Gefragt wird nach **einem Datensatz mehr** als der
    Deckel: kommen 200, sind es 200; kaemen 201, waeren es mehr. Gemessen
    gegen edu-sharing 11.0 mit 205 Kindern -- ``maxItems=201`` liefert 201,
    die Instanz deckelt nicht bei 200.
    """
    voll = OhneZaehlung(kinder=[_kind(f"k{i}", f"{i}.txt", str(i))
                                for i in range(200)])
    async with _repo(voll) as repo:
        node = await repo.node(HAUPT)
        assert len(await node.children.list()) == 200


async def test_einer_ueber_dem_deckel_ohne_gesamtzahl_wird_gemeldet():
    """Die Gegenprobe, und der Grund fuer den einen Datensatz mehr: bei 201
    ist die Seite nicht mehr alles, und das sagt sie selbst -- ohne dass
    irgendwer eine Gesamtzahl nennen muesste."""
    zuviel = OhneZaehlung(kinder=[_kind(f"k{i}", f"{i}.txt", str(i))
                                  for i in range(201)])
    async with _repo(zuviel) as repo:
        node = await repo.node(HAUPT)
        with pytest.raises(EduSharingError, match="200"):
            await node.children.list()


async def test_die_auflistung_fragt_einen_datensatz_mehr_als_den_deckel():
    """Woran alles darueber haengt. Ohne den einen zusaetzlichen Datensatz
    waere eine volle Seite wieder mehrdeutig, und die Kappungsfrage haenge
    erneut daran, dass der Server eine Gesamtzahl nennt -- und dass sie
    stimmt."""
    instanz = Instanz(kinder=[_kind("a", "a.txt", "0")])
    async with _repo(instanz) as repo:
        await (await repo.node(HAUPT)).children.list()
    gelesen = [r for r in instanz.anfragen
               if r.method == "GET" and r.url.path.endswith("/children")]
    assert [r.url.params.get("maxItems") for r in gelesen] == ["201"], (
        [str(r.url) for r in gelesen])


async def test_eine_halbe_seite_ohne_gesamtzahl_ist_unverdaechtig():
    """Gegenprobe: weniger als der Deckel *kann* nicht gekuerzt sein.

    ``pagination`` fehlt bei manchen Antworten ganz, und eine Auflistung an
    einer nicht gemachten Angabe scheitern zu lassen waere schlechter, als
    sie auszuliefern -- die Wache gilt dem, was der Server *sagt*.
    """
    async with _repo(OhneZaehlung(kinder=[_kind("a", "a.txt", "0")])) as repo:
        node = await repo.node(HAUPT)
        assert len(await node.children.list()) == 1


async def test_der_rueckfall_zaehlt_dasselbe_wie_die_gesamtzahl():
    """Beide Wege von ``_count`` muessen dieselbe Zahl liefern.

    ``pagination.total`` zaehlt **jedes** Kind, Versionen eingeschlossen; der
    Rueckfall zaehlte ueber ``list()`` und damit nur die mit dem Aspekt. Fuer
    denselben Knoten kamen so verschiedene Zahlen heraus -- und die kleinere
    traf eine belegte Position (Pruefung 09.09.2026).

    Nachgestellt mit einem Anhang auf Position **1** und einer Version ohne
    Aspekt: mit Gesamtzahl wird 2 vergeben, ohne sie war es 1 -- genau die
    Kollision, gegen die diese Zaehlung existiert.
    """
    bestand = [_kind("a", "a.txt", "1"), _kind("v", "alt.txt", None, serie=False)]
    positionen = []
    for klasse in (Instanz, OhneZaehlung):
        instanz = klasse(kinder=list(bestand))
        async with _repo(instanz) as repo:
            node = await repo.node(HAUPT)
            await node.children.add(b"x", filename="neu.txt", mimetype="text/plain")
        angelegt = next(r for r in instanz.anfragen if r.method == "POST"
                        and r.url.path.rstrip("/").endswith("/children"))
        positionen.append(json.loads(angelegt.content)["ccm:childobject_order"])

    mit, ohne = positionen
    assert mit == ohne == ["2"], f"mit Gesamtzahl {mit}, ohne {ohne}"


async def test_ohne_gesamtzahl_und_voll_wird_das_anlegen_erklaert_verweigert():
    """Sind es so viele wie der Deckel und nennt niemand eine Zahl, ist die
    naechste Position nicht bestimmbar.

    Verweigert wird mit dem Ausweg, der hier hilft -- ``order=`` mitgeben --,
    nicht mit dem Rat zum *Lesen*, den die Auflistung gibt. Vorher kam genau
    dieser durch, weil ``_count`` auf ``list()`` zurueckfiel (Pruefung
    09.09.2026).
    """
    voll = OhneZaehlung(kinder=[_kind(f"k{i}", f"{i}.txt", str(i))
                                for i in range(201)])
    async with _repo(voll) as repo:
        node = await repo.node(HAUPT)
        with pytest.raises(EduSharingError, match="order"):
            await node.children.add(b"x", filename="neu.txt", mimetype="text/plain")


async def test_mit_eigener_position_wird_gar_nicht_gezaehlt():
    """Und der genannte Ausweg funktioniert auch dort, wo sonst verweigert
    wuerde -- sonst waere die Meldung ein leeres Versprechen."""
    voll = OhneZaehlung(kinder=[_kind(f"k{i}", f"{i}.txt", str(i))
                                for i in range(200)])
    async with _repo(voll) as repo:
        node = await repo.node(HAUPT)
        await node.children.add(b"x", filename="neu.txt", mimetype="text/plain",
                                order=500)
    gezaehlt = [r for r in voll.anfragen
                if r.method == "GET" and r.url.path.endswith("/children")]
    assert not gezaehlt, "mit eigener Position gibt es nichts zu zaehlen"


async def test_die_position_folgt_der_hoechsten_vergebenen():
    """Die Zusage ist *hinter den bestehenden* -- und die haelt nur, wenn die
    hoechste vergebene Nummer sie bestimmt, nicht die Anzahl der Kinder.

    Gemessen am 09.09.2026: zwei Anhaenge, mit ``order=`` ausdruecklich auf 5
    und 6 gesetzt -- dem Parameter, den ``add()`` selbst dafuer anbietet.
    Danach ``add()`` ohne ``order``: die Anzahl ist 2, also bekam der neue die
    Position 2 und stand in ``list()`` **an erster Stelle**. Der Audit hat
    diese Bauform in MNT-4 woertlich vorgeschrieben ("order from a
    ``limit=1`` page's total"); sie traegt die Zusage nicht.
    """
    instanz = Instanz(kinder=[_kind("a", "a.txt", "5"), _kind("b", "b.txt", "6")])
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        await node.children.add(b"x", filename="neu.txt", mimetype="text/plain")
        kinder = await node.children.list()

    angelegt = next(r for r in instanz.anfragen if r.method == "POST"
                    and r.url.path.rstrip("/").endswith("/children"))
    assert json.loads(angelegt.content)["ccm:childobject_order"] == ["7"]
    assert [k.name for k in kinder][-1] == "neu.txt", [k.name for k in kinder]


async def test_eine_luecke_wird_nicht_wiederverwendet():
    """Ein geloeschter Anhang laesst eine Luecke, und die uebrigen behalten
    ihre Nummern. Die Anzahl faellt dabei unter die hoechste vergebene.

    Anhaenge auf 1 und 2 (der auf 0 ist fort): die Anzahl ist 2, und 2 ist
    belegt. ``list()`` bricht den Gleichstand zwar nach ``createdAt``, sodass
    nichts verschwindet -- aber jeder andere Leser der Eigenschaft, die
    Redaktionsoberflaeche voran, sieht zwei Anhaenge auf derselben Stelle.
    """
    instanz = Instanz(kinder=[_kind("b", "b.txt", "1"), _kind("c", "c.txt", "2")])
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        await node.children.add(b"x", filename="neu.txt", mimetype="text/plain")

    angelegt = next(r for r in instanz.anfragen if r.method == "POST"
                    and r.url.path.rstrip("/").endswith("/children"))
    assert json.loads(angelegt.content)["ccm:childobject_order"] == ["3"]


async def test_andere_kinder_verschieben_die_position_nicht():
    """Versionen und was sonst unter dem Knoten haengt, tragen keine Ordnung
    und gehoeren nicht in die Rechnung.

    Vorher zaehlte ``pagination.total`` **jedes** Kind, sodass ein Anhang auf
    0 neben einer Version die Position 2 bekam -- eine uebersprungene Nummer,
    die als richtig verteidigt wurde ("zugesagt ist hinter den bestehenden,
    nicht lueckenlos"). Der Sprung war nie noetig: die Zusage gilt den
    **Anhaengen**, und deren hoechste Nummer ist 0.
    """
    instanz = Instanz(kinder=[_kind("a", "a.txt", "0"),
                              _kind("v", "alt.txt", None, serie=False)])
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        await node.children.add(b"x", filename="neu.txt", mimetype="text/plain")

    angelegt = next(r for r in instanz.anfragen if r.method == "POST"
                    and r.url.path.rstrip("/").endswith("/children"))
    assert json.loads(angelegt.content)["ccm:childobject_order"] == ["1"]


async def test_ein_anhang_ohne_ordnung_bestimmt_nichts():
    """``_NO_ORDER`` sortiert ein Kind ohne Nummer ans Ende -- als Wert
    genommen ergaebe es die Position 1000001. Er zaehlt nicht mit."""
    instanz = Instanz(kinder=[_kind("a", "a.txt", "0"),
                              _kind("ohne", "ohne.txt", None)])
    async with _repo(instanz) as repo:
        node = await repo.node(HAUPT)
        await node.children.add(b"x", filename="neu.txt", mimetype="text/plain")

    angelegt = next(r for r in instanz.anfragen if r.method == "POST"
                    and r.url.path.rstrip("/").endswith("/children"))
    assert json.loads(angelegt.content)["ccm:childobject_order"] == ["1"]


class MeldetDieSeite(Instanz):
    """Nennt als ``total`` die **Seitengroesse** und beachtet ``maxItems``.

    Es gibt keinen Weg, so eine Antwort von einer wahren zu unterscheiden --
    ein Knoten mit genau so vielen Kindern sendet dasselbe.
    """

    def __call__(self, request):
        if request.method == "GET" and request.url.path.endswith("/children"):
            self.anfragen.append(request)
            grenze = int(request.url.params.get("maxItems") or LIST_MAX)
            seite = self.kinder[:grenze]
            return httpx.Response(200, json={
                "nodes": seite,
                "pagination": {"total": len(seite), "from": 0,
                               "count": len(seite)}})
        return super().__call__(request)


async def test_eine_gemeldete_seitengroesse_taeuscht_keine_vollstaendigkeit_vor():
    """Der Grund fuer den einen Datensatz ueber dem Deckel.

    Solange genau ``LIST_MAX`` geholt wurden, war eine so gemeldete Gesamtzahl
    ``LIST_MAX`` -- und die Kappungsfrage lautete "ist ``total`` groesser als
    der Deckel?", also nein. Ein Knoten mit 250 Kindern lieferte damit still
    die ersten 200 (gemessen 09.09.2026).

    Jetzt kommen 201 Datensaetze an, und schon die Zahl der Datensaetze sagt
    es -- unabhaengig davon, was der Server ueber die Gesamtheit behauptet.
    """
    viele = MeldetDieSeite(kinder=[_kind(f"k{i}", f"{i}.txt", str(i))
                                   for i in range(250)])
    async with _repo(viele) as repo:
        node = await repo.node(HAUPT)
        with pytest.raises(EduSharingError, match="at least 201"):
            await node.children.list()


async def test_eine_gemeldete_seitengroesse_unter_dem_deckel_ist_kein_fehler():
    """Gegenprobe: dieselbe Antwortform mit wenigen Kindern ist vollstaendig,
    und die Wache darf sie nicht ablehnen."""
    wenige = MeldetDieSeite(kinder=[_kind(f"k{i}", f"{i}.txt", str(i))
                                    for i in range(3)])
    async with _repo(wenige) as repo:
        node = await repo.node(HAUPT)
        assert len(await node.children.list()) == 3
