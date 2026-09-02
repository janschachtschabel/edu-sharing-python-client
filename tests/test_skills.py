"""Skills: Datensaetze mit einer Inhaltsart, deren Datei die Anleitung ist.

Alles hier folgt Konventionen EINER Instanz -- die URIs der Inhaltsarten, wie
ein Registry-Dokument sich zu erkennen gibt, die Blockarten. Sie sind
``SkillConventions`` und ein Parameter mit WLO-Vorgabe, keine feste
Verdrahtung: ein anderes Repositorium uebergibt seine eigenen.

Gemessen gegen Staging am 02.09.2026 (anonym, mds_oeh):

* 34 Skills ueber ``ccm:oeh_extendedType``; mit ``-default-`` weist die
  Instanz das Kriterium zurueck.
* Eine SKILL.md liest man mit ``download()`` -- ``text()`` ist fuer Markdown
  leer (14 493 Bytes gegen 0 Zeichen).
* ``virtual:primaryparent_nodeid`` kommt ueber ``/metadata``; der Ordner ist
  anonym gesperrt (403) -- Begleitdateien brauchen Rechte, das ist ein Grund,
  kein Fehler des Abrufs.
* Zwei Registry-Dokumente (``ai_prompt``): 7 ``::: ki-skill``-Bloecke, 3
  Kontexte.
"""

import json

import httpx
import pytest

from edusharing import AsyncRepository
from edusharing.errors import PermissionDeniedError, ServerError
from edusharing.skills import WLO_SKILLS, SkillConventions

REPO = "https://repo.test/edu-sharing"
SKILL = WLO_SKILLS.skill_type
REGISTRY = WLO_SKILLS.registry_type
RENDER = f"{REPO}/components/render/"
SA = "aaaaaaaa-0000-4000-8000-000000000001"
SB = "bbbbbbbb-0000-4000-8000-000000000002"
SC = "cccccccc-0000-4000-8000-000000000003"
SD = "dddddddd-0000-4000-8000-00000000000d"   # ein Skill in einer Untersammlung
REF_A = "ffffffff-0000-4000-8000-00000000000a"   # Referenz auf SA in einer Sammlung
FOLDER = "f0f0f0f0-0000-4000-8000-0000000000f0"
COLL = "c0c0c0c0-0000-4000-8000-0000000000c0"
REG = "e0e0e0e0-0000-4000-8000-0000000000e0"

REG_MD = f"""# Skills für die Sammlung Optik

Erst den Bestand sichten.

::: ki-skill
[Lehrprofil auswerten]({RENDER}{SA})
:::

## Unterricht vorbereiten

Zuerst den Fragen-Skill.

::: ki-skill
[Fragen generieren]({RENDER}{SB})
:::

::: ki-skill
[Verschollen]({RENDER}{SC})
:::
"""


def _skill(nid: str, title: str, *, keywords=(), description="", typ=SKILL,
           original: str | None = None, mimetype="text/x-web-markdown") -> dict:
    props = {"cclom:title": [title], "cclom:general_keyword": list(keywords),
             "cclom:general_description": [description], "cm:name": ["SKILL.md"],
             "ccm:oeh_extendedType": [typ], "virtual:primaryparent_nodeid": [FOLDER],
             "ccm:original": [original or nid]}
    data = {"ref": {"id": nid}, "title": title, "type": "ccm:io", "mimetype": mimetype,
            "mediatype": "file-markdown", "content": {"hash": "x"},
            "downloadUrl": f"{REPO}/rest/node/v1/nodes/-home-/{nid}/content",
            "properties": props}
    if original:
        data["originalId"] = original
        data["aspects"] = ["ccm:collection_io_reference"]
    return data


def _seite(total: int, count: int) -> dict[str, int]:
    return {"total": total, "from": 0, "count": count}


def _fehler(name: str) -> dict[str, str]:
    return {"error": name, "message": "abgelehnt"}


class Instanz:
    def __init__(self, *, folder_status: int = 200, folder_total: int = 3,
                 registry_docs: list[dict] | None = None, coll_status: int = 200,
                 registry_text: str = REG_MD, unter: dict[str, int] | None = None,
                 unter_total: int | None = None,
                 kopf_status: dict[str, int] | None = None) -> None:
        self.nodes = {
            SA: _skill(SA, "Lehrprofil auswerten", keywords=("Lehrkontext",),
                       description="erfasst den Kontext"),
            SB: _skill(SB, "Fragen generieren", keywords=("Fragen", "Quiz"),
                       description="Fragen zu einem Text"),
            REF_A: _skill(REF_A, "Lehrprofil auswerten", original=SA),
            REG: _skill(REG, "Skill Registry", typ=REGISTRY),
        }
        self.texts = {
            SA: "# Lehrprofil\n\nAnleitung A.",
            SB: "# Fragen\n\n::: ki-skill\n[Lehrprofil auswerten](" + RENDER + SA + ")\n:::\n",
            REG: registry_text}
        self.folder_status, self.folder_total = folder_status, folder_total
        self.coll_status = coll_status
        self.registry_docs = registry_docs if registry_docs is not None else [self.nodes[REG]]
        # Untersammlungen von COLL: ID -> Status ihrer Dateiliste (200 = ein Skill SD).
        self.unter = unter or {}
        self.unter_total = unter_total          # pagination.total der Sammlungsliste
        self.kopf_status = kopf_status or {}    # /metadata-Status je Knoten
        if self.unter:
            self.nodes[SD] = _skill(SD, "Stunde planen", keywords=("Planung",))
            self.texts[SD] = "# Stunde\n\nAnleitung D."
        self.anfragen: list[httpx.Request] = []

    def handler(self, request: httpx.Request) -> httpx.Response:
        self.anfragen.append(request)
        pfad, params = request.url.path, dict(request.url.params)
        if "/values" in pfad:
            return httpx.Response(200, json={"values": [
                {"key": "http://x/460", "displayString": "Physik"}]})
        if "/search/v1" in pfad:
            body = json.loads(request.content)
            typen = [c["values"] for c in body["criteria"]
                     if c["property"] == "ccm:oeh_extendedType"]
            wanted = typen[0][0] if typen else None
            hits = [n for n in self.nodes.values()
                    if n["properties"]["ccm:oeh_extendedType"][0] == wanted]
            return httpx.Response(200, json={"nodes": hits, "facets": [],
                                             "pagination": _seite(len(hits), len(hits))})
        if pfad.endswith("/metadata"):
            nid = pfad.split("/-home-/")[1].split("/")[0]
            if nid in self.kopf_status:
                return httpx.Response(self.kopf_status[nid], json=_fehler("Kaputt"))
            if nid not in self.nodes:
                return httpx.Response(404, json={"error": "DAOMissingException", "message": nid})
            return httpx.Response(200, json={"node": self.nodes[nid]})
        if pfad.endswith("/textContent"):
            return httpx.Response(200, json={"text": ""})          # Markdown: leer, gemessen
        if pfad.endswith("/content"):
            nid = pfad.split("/-home-/")[1].split("/")[0]
            # Eine Referenz liefert den Inhalt ihres Originals.
            text = self.texts.get(nid) or self.texts[self.nodes[nid].get("originalId", nid)]
            return httpx.Response(200, content=text.encode("utf-8"))
        if pfad.endswith(f"/{FOLDER}/children"):
            if self.folder_status != 200:
                return httpx.Response(self.folder_status, json=_fehler("DAOSecurityException"))
            kinder = [self.nodes[SA], _skill("d0d0d0d0-0000-4000-8000-0000000000d0", "vorlage.docx",
                                              typ="x", mimetype="application/msword")]
            return httpx.Response(200, json={"nodes": kinder,
                                             "pagination": _seite(self.folder_total, len(kinder))})
        if pfad.endswith(f"/{COLL}/children"):
            if self.coll_status != 200:
                return httpx.Response(self.coll_status, json=_fehler("DAOMissingException"))
            docs = [*self.registry_docs, self.nodes[REF_A]]
            return httpx.Response(200, json={"nodes": docs,
                                             "pagination": _seite(len(docs), len(docs))})
        if pfad.endswith(f"/{COLL}/children/collections"):
            subs = [{"ref": {"id": s}, "title": f"Unter {s}"} for s in self.unter]
            total = self.unter_total if self.unter_total is not None else len(subs)
            return httpx.Response(200, json={"collections": subs,
                                             "pagination": {"total": total}})
        for sub, status in self.unter.items():
            if pfad.endswith(f"/{sub}/children"):
                if status != 200:
                    return httpx.Response(status, json=_fehler("DAOSecurityException"))
                return httpx.Response(200, json={"nodes": [self.nodes[SD]],
                                                 "pagination": _seite(1, 1)})
        if pfad.endswith("/children/collections"):
            return httpx.Response(200, json={"collections": [], "pagination": {"total": 0}})
        raise AssertionError(f"unerwartet: {request.method} {pfad} {params}")

    def repo(self, **kwargs) -> AsyncRepository:
        kwargs.setdefault("metadataset", "mds_oeh")
        return AsyncRepository(
            REPO, backoff_base=0.0,
            client=httpx.AsyncClient(transport=httpx.MockTransport(self.handler)), **kwargs)

    def suchkriterien(self) -> list[dict]:
        for r in self.anfragen:
            if "/search/v1" in r.url.path:
                return json.loads(r.content)["criteria"]
        raise AssertionError("keine Suche")


# --- Suche -----------------------------------------------------------------

async def test_die_suche_sendet_die_inhaltsart_als_kriterium():
    instanz = Instanz()
    async with instanz.repo() as repo:
        got = await repo.skills.search("Fragen")
    assert any(k["property"] == "ccm:oeh_extendedType" and k["values"] == [SKILL]
               for k in instanz.suchkriterien())
    assert got.hits[0].id == SB, "Titel zaehlt 3, Schlagwort 2, Beschreibung 1"
    assert got.hits[0].title == "Fragen generieren"
    assert got.unresolved == []


async def test_referenz_und_original_sind_ein_skill_und_das_original_gewinnt():
    instanz = Instanz()
    async with instanz.repo() as repo:
        got = await repo.skills.search("")
    ids = [h.id for h in got.hits]
    assert SA in ids and REF_A not in ids
    assert len(ids) == len(set(h.original_id for h in got.hits))


async def test_ein_unaufloesbarer_kurzname_wird_gemeldet():
    instanz = Instanz()
    async with instanz.repo() as repo:
        got = await repo.skills.search("", subject="Phsyik")
    assert got.unresolved and got.unresolved[0]["value"] == "Phsyik"


async def test_eigene_konventionen_ersetzen_die_vorgabe():
    eigene = SkillConventions(skill_type="http://andere.test/skill")
    instanz = Instanz()
    instanz.nodes[SA]["properties"]["ccm:oeh_extendedType"] = ["http://andere.test/skill"]
    async with instanz.repo() as repo:
        got = await repo.skills.search("", conventions=eigene)
    assert [h.id for h in got.hits] == [SA]


# --- Der Sammlungszweig ----------------------------------------------------

async def test_der_sammlungszweig_findet_skills_in_untersammlungen():
    instanz = Instanz(unter={"u1": 200})
    async with instanz.repo() as repo:
        got = await repo.skills.search("", collection_id=COLL, include_subcollections=True)
    assert {h.original_id for h in got.hits} == {SA, SD}, (
        "die Referenz mit ihrem Original, dazu der Skill der Untersammlung")
    assert [h.id for h in got.hits if h.original_id == SA] == [REF_A], (
        "gelistet ist die Referenz -- das Original steht nicht in der Sammlung")
    assert got.unreadable == 0 and got.truncated is False
    assert not any("/search/v1" in r.url.path for r in instanz.anfragen), "nie ueber den Index"


async def test_ohne_untersammlungen_bleibt_es_bei_der_wurzel():
    instanz = Instanz(unter={"u1": 200})
    async with instanz.repo() as repo:
        got = await repo.skills.search("", collection_id=COLL)
    assert {h.original_id for h in got.hits} == {SA}


async def test_eine_gesperrte_untersammlung_zaehlt_und_stoppt_nicht():
    """Praezedenz A10 (flows/tree.py): ein 403 unter vielen darf aus einer
    Teilantwort keine Nicht-Antwort machen. Gezaehlt wird es trotzdem."""
    instanz = Instanz(unter={"u1": 200, "u2": 403})
    async with instanz.repo() as repo:
        got = await repo.skills.search("", collection_id=COLL, include_subcollections=True)
    assert {h.original_id for h in got.hits} == {SA, SD}
    assert got.unreadable == 1


async def test_eine_gesperrte_wurzel_ist_ein_fehler():
    """Die eigene ID des Aufrufers: eine Verweigerung ist die Antwort."""
    instanz = Instanz(coll_status=403)
    async with instanz.repo() as repo:
        with pytest.raises(PermissionDeniedError):
            await repo.skills.search("", collection_id=COLL)


async def test_mehr_untersammlungen_als_eine_seite_werden_gesagt():
    instanz = Instanz(unter={"u1": 200}, unter_total=120)
    async with instanz.repo() as repo:
        got = await repo.skills.search("", collection_id=COLL, include_subcollections=True)
    assert got.truncated is True


async def test_im_sammlungszweig_filtert_der_text_und_reiht_nicht_nur():
    """Das Listing nimmt keine Kriterien; lokal ist ein Datensatz, den kein
    Begriff trifft, kein Treffer -- sonst waere jede Suche in einer Sammlung
    "alles, sortiert", und pick nennt einen Besten mit Punktzahl null."""
    instanz = Instanz(unter={"u1": 200})
    async with instanz.repo() as repo:
        planung = await repo.skills.search(
            "Planung", collection_id=COLL, include_subcollections=True)
        nichts = await repo.skills.search(
            "Quantenphysik", collection_id=COLL, include_subcollections=True)
        keiner = await repo.skills.pick("Quantenphysik", collection_id=COLL)
    assert [h.id for h in planung.hits] == [SD]
    assert nichts.hits == [] and keiner is None


# --- Abruf -----------------------------------------------------------------

async def test_get_liest_die_datei_nicht_den_textauszug():
    instanz = Instanz()
    async with instanz.repo() as repo:
        doc = await repo.skills.get(SA)
    assert doc.content == "# Lehrprofil\n\nAnleitung A."
    assert any(r.url.path.endswith("/content") for r in instanz.anfragen)


async def test_get_nennt_verweise_und_begleitdateien():
    instanz = Instanz()
    async with instanz.repo() as repo:
        mit_verweis = await repo.skills.get(SB)
        doc = await repo.skills.get(SA)
    assert [r.node_id for r in mit_verweis.references] == [SA]
    assert [f.title for f in doc.files] == ["vorlage.docx"], (
        "der Skill selbst ist keine Begleitdatei")
    assert doc.files[0].mimetype == "application/msword"
    assert doc.files_reason == ""


async def test_begleitdateien_ueber_das_original_einer_referenz():
    instanz = Instanz()
    async with instanz.repo() as repo:
        doc = await repo.skills.get(REF_A)
    assert doc.original_id == SA
    assert [f.title for f in doc.files] == ["vorlage.docx"]


async def test_ein_gesperrter_ordner_ist_ein_grund_kein_fehler():
    """Gemessen: der Arbeitsordner eines Skills ist anonym 403."""
    instanz = Instanz(folder_status=403)
    async with instanz.repo() as repo:
        doc = await repo.skills.get(SA)
    assert doc.content and doc.files == [] and doc.files_reason == "folder_unreadable"


async def test_eine_bom_verschwindet_aus_dem_inhalt():
    """Windows-Editoren schreiben eine BOM; mit ihr im Text verliert der
    Abschnittsparser die H1."""
    instanz = Instanz()
    instanz.texts[SA] = "\ufeff# Lehrprofil\n\nAnleitung A."
    async with instanz.repo() as repo:
        doc = await repo.skills.get(SA)
    assert doc.content == "# Lehrprofil\n\nAnleitung A." and doc.content_reason == ""


async def test_eine_binaerdatei_ist_kein_inhalt_und_sagt_es():
    """Ein PDF als Text dekodiert ist Zeichensalat, keine Anleitung."""
    instanz = Instanz()
    instanz.nodes[SA]["mimetype"] = "application/pdf"
    async with instanz.repo() as repo:
        doc = await repo.skills.get(SA)
    assert doc.content is None and doc.content_reason == "not_text"
    assert not any(r.url.path.endswith("/content") for r in instanz.anfragen)


async def test_ohne_datei_sagt_content_reason_warum():
    instanz = Instanz()
    instanz.nodes[SA]["content"] = {"hash": None}
    async with instanz.repo() as repo:
        doc = await repo.skills.get(SA)
    assert doc.content is None and doc.content_reason == "no_file"


async def test_ein_verschwundener_ordner_ist_ein_grund():
    """Ein 404 des Ordners flog bisher nach dem Download -- als haette es den
    Skill nie gegeben."""
    instanz = Instanz(folder_status=404)
    async with instanz.repo() as repo:
        doc = await repo.skills.get(SA)
    assert doc.content and doc.files == [] and doc.files_reason == "no_folder"


async def test_ein_riesiger_ordner_wird_gezaehlt_nicht_gelistet():
    instanz = Instanz(folder_total=484)
    async with instanz.repo() as repo:
        doc = await repo.skills.get(SA)
    assert doc.files == [] and doc.files_reason == "too_many" and doc.folder_file_count == 484


async def test_get_ohne_dateien_kostet_keinen_ordnerabruf():
    instanz = Instanz()
    async with instanz.repo() as repo:
        await repo.skills.get(SA, include_files=False)
    assert not any(r.url.path.endswith("/children") for r in instanz.anfragen)


# --- Registry --------------------------------------------------------------

async def test_registry_findet_das_dokument_und_loest_die_koepfe_auf():
    instanz = Instanz()
    async with instanz.repo() as repo:
        reg = await repo.skills.registry(COLL)
    assert reg.reason == ""
    assert reg.registry_id == REG and reg.registry_title == "Skill Registry"
    assert [e.node_id for e in reg.entries] == [SA, SB]
    assert reg.entries[1].description == "Fragen zu einem Text", (
        "der Datensatz gewinnt ueber den Block")
    assert reg.unresolved == [{"title": "Verschollen", "node_id": SC}]
    assert [c.path for c in reg.contexts] == ["Unterricht vorbereiten"]
    assert reg.general.skills == [SA]
    assert reg.contexts[0].skills == [SB, SC]
    assert not any("/search/v1" in r.url.path for r in instanz.anfragen), "nie ueber den Index"


async def test_ein_kontext_verengt_und_ein_fehlgriff_nie():
    instanz = Instanz()
    async with instanz.repo() as repo:
        eng = await repo.skills.registry(COLL, context="Unterricht vorbereiten")
        daneben = await repo.skills.registry(COLL, context="Gibtsnicht")
    assert [e.node_id for e in eng.entries] == [SA, SB], "der Kontext PLUS das Allgemeine"
    assert eng.context_match == "exact"
    assert [e.node_id for e in daneben.entries] == [SA, SB]
    assert daneben.context_match == "missing"


async def test_ohne_registry_dokument_sagt_es_die_antwort():
    instanz = Instanz(registry_docs=[])
    async with instanz.repo() as repo:
        reg = await repo.skills.registry(COLL)
    assert reg.reason == "no_registry" and reg.entries == []


async def test_eine_fehlende_sammlung_ist_ein_grund():
    instanz = Instanz(coll_status=404)
    async with instanz.repo() as repo:
        reg = await repo.skills.registry(COLL)
    assert reg.reason == "collection_not_found"


async def test_mehrere_kandidaten_die_kleinste_id_gewinnt_und_es_wird_gesagt():
    zweites = _skill("00000000-0000-4000-8000-000000000000", "Skill Registry alt", typ=REGISTRY)
    instanz = Instanz(registry_docs=[_skill(REG, "Skill Registry", typ=REGISTRY), zweites])
    instanz.nodes[zweites["ref"]["id"]] = zweites
    instanz.texts[zweites["ref"]["id"]] = "keine Bloecke"
    async with instanz.repo() as repo:
        reg = await repo.skills.registry(COLL)
    assert reg.registry_id == "00000000-0000-4000-8000-000000000000"
    assert reg.ambiguous == 2


async def test_ohne_markierung_zaehlt_jedes_ai_prompt_markdown():
    """Alle Dateien heissen SKILL.md (gemessen) -- die Markierung im Namen oder
    Titel ist der Tie-Break, nicht die Bedingung."""
    unmarkiert = _skill(REG, "Irgendein Prompt", typ=REGISTRY)
    instanz = Instanz(registry_docs=[unmarkiert])
    async with instanz.repo() as repo:
        reg = await repo.skills.registry(COLL)
    assert reg.registry_id == REG and reg.reason == ""


async def test_eigene_blockart_fuer_skills():
    """Die Blockart, die einen Skill nennt, ist Konvention -- also Parameter."""
    eigene = SkillConventions(block_kinds=("ai-skill",), skill_kind="ai-skill")
    instanz = Instanz(registry_text=REG_MD.replace("::: ki-skill", "::: ai-skill"))
    async with instanz.repo() as repo:
        reg = await repo.skills.registry(COLL, conventions=eigene)
    assert [e.node_id for e in reg.entries] == [SA, SB]
    assert reg.contexts[0].skills == [SB, SC]


async def test_ein_doppelt_genannter_skill_wird_einmal_gelesen():
    """Ein Skill unter zwei Kontexten ist redaktioneller Alltag -- zwei Eintraege,
    ein Kopf."""
    block = "::: ki-skill\n[Lehrprofil auswerten](" + RENDER + SA + ")\n:::\n"
    doppelt = REG_MD + "\n## Nachbereiten\n\n" + block
    instanz = Instanz(registry_text=doppelt)
    async with instanz.repo() as repo:
        reg = await repo.skills.registry(COLL)
    assert [e.node_id for e in reg.entries] == [SA, SB, SA]
    assert [e.context for e in reg.entries] == [None, "Unterricht vorbereiten", "Nachbereiten"]
    koepfe = [r for r in instanz.anfragen if r.url.path.endswith(f"/{SA}/metadata")]
    assert len(koepfe) == 1


async def test_ein_serverfehler_beim_kopf_ist_kein_unresolved():
    """unresolved heisst: der Block nennt keinen lesbaren Datensatz. Ein 500
    sagt nichts ueber den Datensatz -- er wirft."""
    instanz = Instanz(kopf_status={SB: 500})
    async with instanz.repo() as repo:
        with pytest.raises(ServerError):
            await repo.skills.registry(COLL)


# --- Auswahl ---------------------------------------------------------------

async def test_pick_liefert_den_besten_mit_anleitung_und_die_anderen():
    instanz = Instanz()
    async with instanz.repo() as repo:
        picked = await repo.skills.pick("Fragen zu einem Text")
    assert picked is not None
    best, others = picked
    assert best.id == SB and best.content.startswith("# Fragen")
    assert [o.id for o in others] == [SA]


async def test_pick_reicht_include_files_durch():
    instanz = Instanz()
    async with instanz.repo() as repo:
        picked = await repo.skills.pick("Fragen", include_files=False)
    assert picked is not None
    assert not any(r.url.path.endswith("/children") for r in instanz.anfragen)


async def test_pick_ohne_treffer_ist_none():
    instanz = Instanz()
    async with instanz.repo(metadataset="mds_oeh") as repo:
        leer = SkillConventions(skill_type="http://leer")
        assert await repo.skills.pick("", conventions=leer) is None


# --- Die synchrone Huelle ---------------------------------------------------

def test_blockierend_ohne_koroutine():
    from edusharing import Repository
    instanz = Instanz()
    repo = Repository(REPO, metadataset="mds_oeh", backoff_base=0.0,
                      client=httpx.AsyncClient(transport=httpx.MockTransport(instanz.handler)))
    try:
        got = repo.skills.search("Fragen")
        assert got.hits[0].id == SB
        assert repo.skills.get(SA).content.startswith("# Lehrprofil")
        assert repo.skills.registry(COLL).registry_id == REG
    finally:
        repo.close()


@pytest.mark.parametrize("attr", ["skill_type", "registry_type", "type_property", "registry_mark"])
def test_die_vorgabe_traegt_die_wlo_werte(attr):
    assert getattr(WLO_SKILLS, attr)


# --- Die vier Ablaeufe -----------------------------------------------------

async def test_find_skills_als_dict():
    instanz = Instanz()
    async with instanz.repo() as repo:
        got = await repo.flows.find_skills("Fragen")
    assert set(got) == {"query", "hits", "unreadable", "unresolved", "truncated"}
    assert got["hits"][0]["id"] == SB and got["hits"][0]["keywords"] == ["Fragen", "Quiz"]


async def test_skill_als_dict():
    instanz = Instanz()
    async with instanz.repo() as repo:
        got = await repo.flows.skill(SB)
    assert got["content"].startswith("# Fragen")
    assert got["references"][0]["node_id"] == SA
    assert got["files_reason"] == ""


async def test_skill_registry_als_dict():
    instanz = Instanz()
    async with instanz.repo() as repo:
        got = await repo.flows.skill_registry(COLL, context="Unterricht vorbereiten")
    assert got["reason"] == "" and got["context_match"] == "exact"
    assert [e["node_id"] for e in got["entries"]] == [SA, SB]
    assert got["contexts"][0]["path"] == "Unterricht vorbereiten"
    assert got["general"]["skills"] == [SA]


async def test_pick_skill_als_dict():
    instanz = Instanz()
    async with instanz.repo() as repo:
        got = await repo.flows.pick_skill("Fragen zu einem Text")
        leer = await repo.flows.pick_skill("", conventions=SkillConventions(skill_type="http://leer"))
    assert got["best"]["id"] == SB and got["reason"] == ""
    assert [a["id"] for a in got["alternatives"]] == [SA]
    assert leer == {"best": None, "alternatives": [], "reason": "no_match"}
