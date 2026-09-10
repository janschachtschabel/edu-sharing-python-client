"""Wer darf was mit einem Knoten -- und wer darf ihn ueberhaupt sehen.

Ohne diesen Teil legt die Bibliothek Material an, das ausser dem Anleger
niemand lesen kann, und meldet Erfolg. Die Ideendatenbank hat den Grund
aufgeschrieben: edu-sharing veroeffentlicht ein Original **nicht**, wenn es als
Referenz in eine oeffentliche Sammlung gehaengt wird.

Alles hier gemessen gegen Staging am 28.08.2026, in einem eigens angelegten
Wegwerf-Ordner:

* Der ``POST`` **ersetzt** die lokale ACL. Wer nur ein Recht ergaenzen will,
  muss selbst zusammenfuehren -- sonst loescht er die uebrigen Eintraege.
* Ein **GROUP_-Name ohne Gruppe dahinter** wird still verworfen: HTTP 200,
  und danach steht nichts da. Ein **Benutzername** wird dagegen gar nicht
  geprueft -- ein Eintrag fuer ein Konto, das es nicht gibt, wird gespeichert
  und berechtigt niemanden.
* Ein unbekannter **Rechtename** ist dagegen laut -- HTTP 500
  ``Can not find Quatschrecht``.
* Ein Knoten ist oeffentlich, wenn sein **Elternteil** es ist. Das Recht steht
  dann unter ``inheritedPermissions``, die lokale ACL bleibt leer.
* Die lokale ACL zu leeren nimmt das **nicht** zurueck. Nur ``inherited=false``
  tut das -- und schneidet dabei jedes geerbte Recht ab, nicht nur dieses.
* Der ``POST`` antwortet mit **leerem Body**. Es gibt nichts zu pruefen ausser
  einem zweiten Lesen.
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import ConflictError, SilentDropError
from edusharing.permissions import CONSUMER, EVERYONE, Ace, Permissions

REPO = "https://repo.test/edu-sharing"


def _ace(name: str, *rechte: str, typ: str = "USER") -> dict:
    return {"authority": {"authorityName": name, "authorityType": typ},
            "permissions": list(rechte), "editable": True}


def _antwort(*, inherits: bool = True, own: list[dict] | None = None,
             inherited: list[dict] | None = None) -> dict:
    """Die gemessene Form von GET /node/v1/nodes/-home-/{id}/permissions."""
    return {"permissions": {
        "localPermissions": {"inherited": inherits, "permissions": own or []},
        "inheritedPermissions": inherited if inherited is not None
        else [_ace("ROLE_OWNER", "All", typ="OWNER")],
    }}


class Instanz:
    """Ein Repositorium, dessen ACL sich merkt, was geschrieben wurde."""

    def __init__(self, *, inherits: bool = True, own: list[dict] | None = None,
                 inherited: list[dict] | None = None,
                 taub: bool = False) -> None:
        self.inherits = inherits
        self.own = list(own or [])
        self.inherited = inherited if inherited is not None else [
            _ace("ROLE_OWNER", "All", typ="OWNER")]
        # taub=True bildet den gemessenen stillen Verlust nach: 200, nichts
        # gespeichert.
        self.taub = taub
        self.geschrieben: list[dict] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/permissions"):
            if request.method == "GET":
                return httpx.Response(200, json=_antwort(
                    inherits=self.inherits, own=self.own, inherited=self.inherited))
            koerper = json.loads(request.content)
            self.geschrieben.append(koerper)
            if not self.taub:
                self.inherits = koerper["inherited"]
                self.own = list(koerper["permissions"])
            return httpx.Response(200, content=b"")
        return httpx.Response(
                200, json={"node": {"ref": {"id": "n1"}, "type": "ccm:io"}})

    def repo(self) -> AsyncRepository:
        return AsyncRepository(
            REPO, backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)))


# --- Lesen ----------------------------------------------------------------

async def test_liest_eigene_und_geerbte_rechte():
    instanz = Instanz(own=[_ace("alice", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        rechte = await knoten.permissions.get()
    assert [a.authority for a in rechte.own] == ["alice"]
    assert [a.authority for a in rechte.inherited] == ["ROLE_OWNER"]
    assert rechte.inherits is True


async def test_oeffentlich_durch_eigenes_recht():
    instanz = Instanz(own=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        rechte = await knoten.permissions.get()
    assert rechte.is_public


async def test_oeffentlich_durch_vererbung():
    """Gemessen: liegt der Knoten in einem oeffentlichen Ordner, bleibt seine
    lokale ACL leer und das Recht steht unter den geerbten. Wer nur die lokale
    ansieht, haelt einen fuer alle lesbaren Knoten fuer privat."""
    instanz = Instanz(own=[], inherited=[
        _ace("ROLE_OWNER", "All", typ="OWNER"),
        _ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        rechte = await knoten.permissions.get()
    assert rechte.own == ()
    assert rechte.is_public


async def test_nicht_oeffentlich():
    instanz = Instanz(own=[_ace("alice", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        rechte = await knoten.permissions.get()
    assert not rechte.is_public


async def test_geerbtes_recht_zaehlt_nicht_wenn_die_vererbung_aus_ist():
    """inherited=false schneidet die geerbte Liste ab -- gemessen kam sie danach
    leer zurueck. Bildet die Antwort sie trotzdem ab, darf sie nicht zaehlen."""
    instanz = Instanz(inherits=False, own=[], inherited=[
        _ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        rechte = await knoten.permissions.get()
    assert not rechte.is_public


async def test_allows_fragt_beide_listen():
    instanz = Instanz(own=[_ace("alice", "Coordinator")],
                      inherited=[_ace("bob", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        rechte = await knoten.permissions.get()
    assert rechte.allows("alice", "Coordinator")
    assert rechte.allows("bob", "Consumer")
    assert not rechte.allows("alice", "Consumer")
    assert not rechte.allows("carol", "Consumer")


# --- Schreiben ------------------------------------------------------------

async def test_grant_behaelt_die_uebrigen_eintraege():
    """Der wichtigste Test der Datei. Der POST ersetzt die lokale ACL -- wer
    nicht zusammenfuehrt, loescht beim Veroeffentlichen die Rechte anderer."""
    instanz = Instanz(own=[_ace("alice", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.grant("bob", CONSUMER)
    gesendet = {a["authority"]["authorityName"]
                for a in instanz.geschrieben[-1]["permissions"]}
    assert gesendet == {"alice", "bob"}


async def test_grant_behaelt_die_vererbung_bei():
    instanz = Instanz(inherits=True)
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.grant("bob", CONSUMER)
    assert instanz.geschrieben[-1]["inherited"] is True


async def test_grant_ergaenzt_ein_recht_bei_bestehender_autoritaet():
    instanz = Instanz(own=[_ace("alice", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.grant("alice", "Coordinator")
    eintrag = instanz.geschrieben[-1]["permissions"][0]
    assert sorted(eintrag["permissions"]) == ["Consumer", "Coordinator"]


async def test_grant_schreibt_nicht_wenn_das_recht_schon_steht():
    instanz = Instanz(own=[_ace("alice", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.grant("alice", CONSUMER)
    assert geaendert is False
    assert instanz.geschrieben == []


async def test_revoke_nimmt_nur_das_genannte_recht():
    instanz = Instanz(own=[_ace("alice", "Consumer", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.revoke("alice", "Coordinator")
    eintrag = instanz.geschrieben[-1]["permissions"][0]
    assert eintrag["permissions"] == ["Consumer"]


async def test_revoke_ohne_recht_entfernt_die_ganze_autoritaet():
    instanz = Instanz(own=[_ace("alice", "Consumer"), _ace("bob", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.revoke("alice")
    uebrig = [a["authority"]["authorityName"]
              for a in instanz.geschrieben[-1]["permissions"]]
    assert uebrig == ["bob"]


async def test_revoke_laesst_einen_leeren_eintrag_nicht_stehen():
    instanz = Instanz(own=[_ace("alice", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.revoke("alice", "Consumer")
    assert instanz.geschrieben[-1]["permissions"] == []


async def test_revoke_schreibt_nicht_wenn_nichts_zu_nehmen_ist():
    instanz = Instanz(own=[_ace("alice", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.revoke("bob", "Consumer")
    assert geaendert is False
    assert instanz.geschrieben == []


async def test_stiller_verlust_wird_gemeldet():
    """Gemessen: ein GROUP_-Name ohne Gruppe dahinter kommt mit HTTP 200 zurueck
    und steht danach nicht da. Genau der Fall, fuer den diese Bibliothek
    zurueckliest."""
    instanz = Instanz(taub=True)
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(SilentDropError) as fehler:
            await knoten.permissions.grant("GROUP_gibtesnicht", CONSUMER)
    assert "GROUP_gibtesnicht" in fehler.value.dropped


# --- Veroeffentlichen -----------------------------------------------------

async def test_publish_setzt_den_richtigen_autoritaetstyp():
    """GROUP_EVERYONE traegt den Typ EVERYONE, nicht GROUP -- der Name faengt
    mit GROUP_ an und verleitet zum falschen. Das Repositorium normalisiert den
    Typ zwar selbst (gemessen), aber was gesendet wird, soll stimmen."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.publish()
    eintrag = instanz.geschrieben[-1]["permissions"][-1]
    assert eintrag["authority"] == {"authorityName": EVERYONE,
                                    "authorityType": "EVERYONE"}
    assert eintrag["permissions"] == [CONSUMER]


async def test_publish_ist_wiederholbar():
    instanz = Instanz(own=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.publish()
    assert geaendert is False
    assert instanz.geschrieben == []


async def test_publish_schreibt_nicht_wenn_schon_geerbt_oeffentlich():
    """Ein zweites Recht neben dem geerbten waere Rauschen -- und es spaeter zu
    entfernen wuerde nichts bewirken."""
    instanz = Instanz(inherited=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.publish()
    assert geaendert is False
    assert instanz.geschrieben == []


async def test_unpublish_nimmt_das_eigene_recht_zurueck():
    instanz = Instanz(own=[_ace("alice", "Coordinator"),
                           _ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.unpublish()
    assert geaendert is True
    uebrig = [a["authority"]["authorityName"]
              for a in instanz.geschrieben[-1]["permissions"]]
    assert uebrig == ["alice"]


async def test_unpublish_ist_wiederholbar():
    instanz = Instanz(own=[])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.unpublish()
    assert geaendert is False


async def test_unpublish_meldet_wenn_die_vererbung_oeffentlich_haelt():
    """Gemessen: die lokale ACL zu leeren nimmt nichts zurueck, solange das
    Elternteil oeffentlich ist. ``False`` zurueckzugeben hiesse behaupten, der
    Knoten sei jetzt privat -- er ist es nicht."""
    instanz = Instanz(own=[], inherited=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(ConflictError) as fehler:
            await knoten.permissions.unpublish()
    assert "geerbt" in str(fehler.value).lower() or "inherit" in str(fehler.value).lower()


# --- F03/F04 (Fremdpruefung 09.09.2026) ------------------------------------

async def test_unpublish_meldet_auch_wenn_es_beides_gibt():
    """Der Fall, durch den der Konfliktschutz fiel: **eigenes und geerbtes**
    Recht zugleich.

    Geprueft wurde, ob es einen eigenen Eintrag gibt -- den gibt es hier, also
    griff der Schutz nicht, das eigene Recht wurde entfernt und ``unpublish()``
    meldete ``True``. Gemessen war der Knoten danach weiter oeffentlich. Die
    Frage ist nicht, woher das Recht kommt, sondern ob der Knoten es hinterher
    noch hat.
    """
    instanz = Instanz(
        own=[_ace("alice", "Coordinator"), _ace(EVERYONE, CONSUMER, typ="EVERYONE")],
        inherited=[_ace("ROLE_OWNER", "All", typ="OWNER"),
                   _ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(ConflictError):
            await knoten.permissions.unpublish()
        assert (await knoten.permissions.get()).is_public is True
    assert instanz.geschrieben == [], (
        "ein Konflikt schreibt nicht halb -- sonst waere das eigene Recht weg "
        "und der Knoten trotzdem oeffentlich")


async def test_unpublish_ohne_vererbung_bleibt_moeglich():
    """Die Gegenprobe: schneidet der Knoten die Vererbung ab, zaehlt das
    geerbte Recht nicht mehr -- und der Rueckzug gelingt.

    Ohne diesen Test waere die Wache gruen, wenn ``unpublish()`` jeden Knoten
    mit einem geerbten Eintrag ablehnt.
    """
    instanz = Instanz(
        inherits=False,
        own=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")],
        inherited=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        assert await knoten.permissions.unpublish() is True
        assert (await knoten.permissions.get()).is_public is False


async def test_revoke_glaubt_seinem_eigenen_ruecklesen_nicht_blind():
    """F04: der Server bestaetigt mit 200 und speichert nichts.

    ``_write()`` liest bereits zurueck -- eine zweite Anfrage, bezahlt und
    weggeworfen. ``grant()`` vergleicht dieses Ergebnis seit jeher und meldet
    ``SilentDropError``; ``revoke()`` gab ``True`` zurueck, ohne hinzusehen.
    """
    instanz = Instanz(own=[_ace("alice", "Coordinator")], taub=True)
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(SilentDropError):
            await knoten.permissions.revoke("alice", "Coordinator")


async def test_revoke_bemerkt_auch_eine_halb_uebernommene_aenderung():
    """Der interessantere Fall: der Server nimmt einen Teil und laesst den
    Rest fallen. Ein Vergleich, der nur das entzogene Recht ansieht, waere
    hier gruen."""
    class Halb(Instanz):
        def handler(self, request: httpx.Request) -> httpx.Response:
            if request.url.path.endswith("/permissions") and request.method == "POST":
                koerper = json.loads(request.content)
                self.geschrieben.append(koerper)
                # Das entzogene Recht geht -- und bob geht gleich mit.
                self.own = [a for a in koerper["permissions"]
                            if a["authority"]["authorityName"] != "bob"]
                return httpx.Response(200, content=b"")
            return super().handler(request)

    instanz = Halb(own=[_ace("alice", "Coordinator"), _ace("bob", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(SilentDropError) as fehler:
            await knoten.permissions.revoke("alice", "Coordinator")
    assert "bob" in str(fehler.value)


async def test_revoke_meldet_wenn_die_vererbung_umgeworfen_wird():
    """Und der dritte Teil des Zustands: ob der Knoten noch erbt."""
    class Kippt(Instanz):
        def handler(self, request: httpx.Request) -> httpx.Response:
            if request.url.path.endswith("/permissions") and request.method == "POST":
                koerper = json.loads(request.content)
                self.geschrieben.append(koerper)
                self.own = list(koerper["permissions"])
                self.inherits = not koerper["inherited"]
                return httpx.Response(200, content=b"")
            return super().handler(request)

    instanz = Kippt(own=[_ace("alice", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(SilentDropError):
            await knoten.permissions.revoke("alice", "Coordinator")


async def test_ein_gelungener_entzug_meldet_weiterhin_true():
    """Die Gegenprobe zu allen dreien: ein Server, der tut was er sagt."""
    instanz = Instanz(own=[_ace("alice", "Coordinator"), _ace("bob", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        assert await knoten.permissions.revoke("alice", "Coordinator") is True
        danach = await knoten.permissions.get()
    assert [a.authority for a in danach.own] == ["bob"]


# --- R02/R03 (Zweitpruefung 09.09.2026) ------------------------------------

class WaehrendDesSchreibens(Instanz):
    """Ein Repositorium, dessen Elternteil waehrend des POST oeffentlich wird.

    Der Fall ist nicht konstruiert: zwischen Vorpruefung und Schreiben liegt
    eine Anfrage, und eine Redaktionsoberflaeche veroeffentlicht Ordner.
    """

    def __init__(self, *args, danach: list[dict] | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.danach = danach or []

    def handler(self, request: httpx.Request) -> httpx.Response:
        antwort = super().handler(request)
        if request.url.path.endswith("/permissions") and request.method == "POST":
            self.inherited = self.danach
        return antwort


async def test_unpublish_meldet_auch_neu_hinzugekommene_vererbung():
    """R02: die Pruefung lief nur **vor** dem Schreiben.

    Gemessen: der Knoten traegt zunaechst nur das eigene Recht, der Elternteil
    wird waehrend des POST oeffentlich, und die Rueckleseantwort zeigt das
    bereits -- ``unpublish()`` lieferte trotzdem ``True``.
    """
    instanz = WaehrendDesSchreibens(
        own=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")],
        danach=[_ace("ROLE_OWNER", "All", typ="OWNER"),
                _ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(ConflictError) as fehler:
            await knoten.permissions.unpublish()
        assert (await knoten.permissions.get()).is_public is True
    # Der lokale Eintrag ist weg -- das muss in der Meldung stehen, sonst
    # weiss der Aufrufer den Zustand nicht.
    assert instanz.geschrieben, "geschrieben wurde bereits"
    assert "removed" in str(fehler.value) or "entfernt" in str(fehler.value)


async def test_ein_gelungener_rueckzug_meldet_weiterhin_true():
    """Die Gegenprobe. Ohne sie waere die Nachpruefung gruen, wenn sie jeden
    Rueckzug ablehnt."""
    instanz = Instanz(own=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        assert await knoten.permissions.unpublish() is True
        assert (await knoten.permissions.get()).is_public is False


class NimmtNurDenNeuen(Instanz):
    """Ein Repositorium, das nur die zuletzt genannte Autoritaet speichert und
    dabei die Vererbung abschaltet -- die gemessene Form einer teilweise
    uebernommenen ACL."""

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/permissions") and request.method == "POST":
            koerper = json.loads(request.content)
            self.geschrieben.append(koerper)
            self.own = koerper["permissions"][-1:]
            self.inherits = False
            return httpx.Response(200, content=b"")
        return super().handler(request)


async def test_revoke_bemerkt_wenn_die_autoritaet_mehr_verliert_als_gefragt():
    """Der Fall, den ein ``skip`` verdecken wuerde: entzogen wird ``Consumer``,
    der Server nimmt auch ``Coordinator``."""
    class NimmtMehr(Instanz):
        def handler(self, request: httpx.Request) -> httpx.Response:
            if (request.url.path.endswith("/permissions")
                    and request.method == "POST"):
                koerper = json.loads(request.content)
                self.geschrieben.append(koerper)
                self.own = []
                return httpx.Response(200, content=b"")
            return super().handler(request)

    instanz = NimmtMehr(own=[_ace("alice", "Consumer", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(SilentDropError) as fehler:
            await knoten.permissions.revoke("alice", "Consumer")
    assert "Coordinator" in str(fehler.value)


async def test_grant_bemerkt_den_verlust_fremder_eintraege():
    """R03: der POST ersetzt die ganze lokale Liste, also verliert ``grant``
    genauso wie ``revoke``.

    Ich hatte ``_not_stored`` bewusst nur an ``revoke`` gehaengt und "kleinster
    Eingriff" dazu gesagt. Gemessen: ``grant=True``, Alice weg,
    ``inherits=False`` trotz gesendetem ``True``.
    """
    instanz = NimmtNurDenNeuen(own=[_ace("alice", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(SilentDropError) as fehler:
            await knoten.permissions.grant("bob", "Consumer")
    assert "alice" in str(fehler.value)
    assert "inherit" in str(fehler.value).lower()


async def test_grant_meldet_einen_unbekannten_gruppennamen_weiterhin_eigens():
    """Die Gegenprobe: die gemessene stille Verwerfung eines ``GROUP_``-Namens
    ohne Gruppe dahinter behaelt ihre eigene Erklaerung -- sie sagt dem
    Aufrufer, wonach er suchen soll."""
    instanz = Instanz(taub=True)
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(SilentDropError) as fehler:
            await knoten.permissions.grant("GROUP_gibtsnicht", "Consumer")
    assert "group" in str(fehler.value).lower()
    assert "spelling" in str(fehler.value).lower()


async def test_ein_gelungener_grant_meldet_weiterhin_true():
    """Und die zweite Gegenprobe: ein Server, der tut was er sagt."""
    instanz = Instanz(own=[_ace("alice", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        assert await knoten.permissions.grant("bob", "Consumer") is True
        danach = await knoten.permissions.get()
    assert sorted(a.authority for a in danach.own) == ["alice", "bob"]
    assert danach.inherits is True


# --- A01 (Drittpruefung 10.09.2026) ----------------------------------------

class NimmtNurDasNeueRecht(Instanz):
    """Speichert fuer die bearbeitete Autoritaet **nur** das zuletzt genannte
    Recht und wirft ihren Altbestand weg. Fremde Eintraege und die Vererbung
    bleiben unangetastet.

    Genau der Randfall, den ``skip=authority`` durchlaesst: die Pruefung fuer
    fremde Eintraege sieht nichts, weil fremd nichts fehlt, und die Pruefung
    fuer die eigene sah nur die **neu** angefragten Rechte.
    """

    def handler(self, request: httpx.Request) -> httpx.Response:
        if request.url.path.endswith("/permissions") and request.method == "POST":
            koerper = json.loads(request.content)
            self.geschrieben.append(koerper)
            self.inherits = koerper["inherited"]
            self.own = [
                _ace("alice", "Write")
                if e["authority"]["authorityName"] == "alice" else e
                for e in koerper["permissions"]]
            return httpx.Response(200, content=b"")
        return super().handler(request)


async def test_grant_bemerkt_den_verlust_alter_rechte_derselben_autoritaet():
    """A01: ``grant`` sagt zu, vorhandene Rechte derselben Autoritaet zu
    erhalten -- geprueft hat es das nie.

    Gemessen am 10.09.2026: lokale ACL ``alice:[Read]``, ``bob:[Consumer]``,
    Vererbung an. ``grant("alice", "Write")`` sendet ``['Read', 'Write']``,
    der Server speichert ``['Write']`` -- und ``grant`` meldete ``True``.
    """
    instanz = NimmtNurDasNeueRecht(
        own=[_ace("alice", "Read"), _ace("bob", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(SilentDropError) as fehler:
            await knoten.permissions.grant("alice", "Write")
    # Das verlorene Recht muss dastehen, sonst sucht der Aufrufer im Dunkeln.
    assert "Read" in str(fehler.value)
    assert "alice" in str(fehler.value)


async def test_ein_grant_der_alte_und_neue_rechte_behaelt_meldet_true():
    """Die Gegenprobe. Ohne sie waere die neue Wache gruen, indem sie jede
    Ergaenzung ablehnt."""
    instanz = Instanz(own=[_ace("alice", "Read"), _ace("bob", "Consumer")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        assert await knoten.permissions.grant("alice", "Write") is True
        danach = await knoten.permissions.get()
    assert sorted(danach.find("alice").permissions) == ["Read", "Write"]
    assert list(danach.find("bob").permissions) == ["Consumer"]


async def test_ein_grant_an_eine_neue_autoritaet_bleibt_unberuehrt():
    """Die zweite Gegenprobe: ohne Alteintrag gibt es nichts zu verlieren --
    der Fall darf nicht plotzlich am leeren Altbestand haengenbleiben."""
    instanz = Instanz(own=[_ace("alice", "Read")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        assert await knoten.permissions.grant("bob", "Consumer") is True


async def test_der_unbekannte_gruppenname_behaelt_seinen_eigenen_text():
    """Die dritte: zwei Gruende, zwei Texte. Ein Gruppenname ohne Gruppe
    dahinter soll weiter nach der Schreibweise fragen lassen -- nicht nach
    einem verlorenen Altbestand, den es nicht gibt."""
    instanz = Instanz(taub=True, own=[_ace("GROUP_x", "Read")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(SilentDropError) as fehler:
            await knoten.permissions.grant("GROUP_x", "Consumer")
    assert "spelling" in str(fehler.value).lower()


# --- Formen ---------------------------------------------------------------

def test_ace_leitet_den_typ_aus_dem_namen_ab():
    assert Ace.for_authority(EVERYONE, CONSUMER).authority_type == "EVERYONE"
    assert Ace.for_authority("GROUP_lehrer", CONSUMER).authority_type == "GROUP"
    assert Ace.for_authority("ROLE_OWNER", "All").authority_type == "OWNER"
    assert Ace.for_authority("alice", CONSUMER).authority_type == "USER"


def test_ace_typ_laesst_sich_ueberschreiben():
    gesetzt = Ace.for_authority("x", CONSUMER, authority_type="GROUP")
    assert gesetzt.authority_type == "GROUP"


def test_permissions_ist_unveraenderlich():
    rechte = Permissions.from_response(_antwort())
    with pytest.raises(AttributeError):
        rechte.inherits = False  # type: ignore[misc]


async def test_revoke_schreibt_nicht_wenn_die_autoritaet_das_recht_nicht_hat():
    """Sie steht in der Liste, aber mit anderen Rechten. Ein Schreibvorgang
    waere ein Leerlauf, der wie eine Aenderung aussieht."""
    instanz = Instanz(own=[_ace("alice", "Coordinator")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        geaendert = await knoten.permissions.revoke("alice", CONSUMER)
    assert geaendert is False
    assert instanz.geschrieben == []


async def test_grant_ohne_recht_ist_ein_fehler():
    """Ein Aufruf ohne Recht kann nichts bewirken. Still nichts zu tun hiesse,
    einen Tippfehler als Erfolg zu melden."""
    instanz = Instanz()
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        with pytest.raises(ValueError, match="at least one permission"):
            await knoten.permissions.grant("alice")
    assert instanz.geschrieben == []


async def test_reprs_nennen_das_wesentliche():
    instanz = Instanz(own=[_ace(EVERYONE, CONSUMER, typ="EVERYONE")])
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        assert "n1" in repr(knoten.permissions)
        rechte = await knoten.permissions.get()
    assert "public=True" in repr(rechte)
    assert repr(rechte.own[0]) == f"Ace('{EVERYONE}', {CONSUMER})"


# --- COR-1: die ACL-Stelle sagt idempotent=True (Review 06.09.2026, F6) ------

async def test_die_acl_wird_nach_abbruch_erneut_gesendet():
    """Ein ganzes ACL zu ersetzen ist zweimal derselbe Zustand. Ohne diesen
    Test hielte ein verlorenes Flag die Suite gruen."""
    instanz = Instanz()
    abgebrochen = []
    echt = instanz.handler

    def handler(request):
        if request.method == "POST" and not abgebrochen:
            abgebrochen.append(1)
            raise httpx.ReadTimeout("abgebrochen", request=request)
        return echt(request)

    instanz.handler = handler
    async with instanz.repo() as repo:
        knoten = await repo.node("n1")
        await knoten.permissions.grant("bob", "Consumer")
    assert abgebrochen == [1]
    assert len(instanz.geschrieben) == 1
