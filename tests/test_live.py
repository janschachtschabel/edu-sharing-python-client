"""Tests gegen ein echtes Repositorium.

Laufen nur mit ``pytest -m live`` und gesetztem ``EDU_SHARING_URL``. Alles
andere in dieser Suite kommt ohne Netz aus; diese Tests beantworten die eine
Frage, die Mocks nicht beantworten koennen: stimmt unser Bild vom Server noch?

    EDU_SHARING_URL=https://repository.staging.openeduhub.net uv run pytest -m live
"""

import os

import pytest

from edusharing import AsyncRepository
from edusharing.errors import (
    AuthenticationError,
    EduSharingError,
    NotFoundError,
    ValidationError,
)

pytestmark = [
    pytest.mark.live,
    pytest.mark.skipif(
        not os.environ.get("EDU_SHARING_URL"),
        reason="EDU_SHARING_URL nicht gesetzt",
    ),
]

FEHLENDE_NODE = "00000000-0000-0000-0000-000000000000"


@pytest.fixture
async def repo():
    async with AsyncRepository.from_env() as r:
        yield r


async def test_about_liefert_eine_version(repo):
    about = await repo.about()
    assert about.repository_version, "Instanz meldet keine Repository-Version"
    assert about.services, "Instanz meldet keine Dienste"


async def test_whoami_beantwortet_wer_ich_bin(repo):
    wer = await repo.whoami()
    assert wer.authority, "keine Authority zurueckbekommen"
    # Ohne Zugangsdaten muss die Antwort anonym lauten -- alles andere hiesse,
    # dass die Bibliothek unbemerkt fremde Zugangsdaten mitschickt.
    if repo.credential.is_anonymous:
        assert wer.is_anonymous, f"anonym angefragt, aber als {wer.authority!r} angemeldet"


async def test_unbekannte_node_ergibt_notfounderror(repo):
    with pytest.raises(NotFoundError):
        await repo.raw.json("GET", f"/node/v1/nodes/-home-/{FEHLENDE_NODE}/metadata")


async def test_geschuetzter_endpunkt_ergibt_authenticationerror(repo):
    """Der Kernfall, live nachgewiesen.

    ``/iam/v1/people/-home-/-me-/preferences`` antwortet einem Gast mit
    **HTTP 500** und "Not allowed for guest user". Die Bibliothek muss daraus
    einen Authentifizierungsfehler machen -- und darf die Anfrage nicht
    wiederholen.

    **Nur wo die Instanz die Meldung ausliefert.** redaktion.openeduhub.net
    setzt ``security.logging.displayLevel`` so, dass sie es nicht tut; die
    Erkennung liest den Text und kann dort nicht greifen. Gemessen am
    28.08.2026: Staging 1 Anfrage und AuthenticationError, Produktiv 4
    Anfragen und ServerError. Das ist keine Regression, sondern eine Grenze --
    ``errors._HIDDEN_NOTE`` benennt sie dem Aufrufer gegenueber, und
    ``test_errors.test_verborgene_details_werden_benannt`` haelt sie fest.
    """
    if not repo.credential.is_anonymous:
        pytest.skip("nur als Gast aussagekraeftig")
    with pytest.raises(EduSharingError) as info:
        await repo.raw.json("GET", "/iam/v1/people/-home-/-me-/preferences")
    if "security.logging.displayLevel" in str(info.value):
        pytest.skip("diese Instanz verbirgt Fehlermeldungen -- die "
                    "Gast-Erkennung kann hier nicht greifen")
    assert isinstance(info.value, AuthenticationError), (
        f"Meldung war lesbar, aber falsch eingeordnet: {info.value!r}")


async def test_falsche_zugangsdaten_ergeben_authenticationerror():
    """Gemessen: edu-sharing faellt bei falschen Zugangsdaten NICHT auf
    oeffentliches Lesen zurueck, sondern antwortet ueberall mit 401."""
    async with AsyncRepository(
        os.environ["EDU_SHARING_URL"],
        auth=("kein-solcher-nutzer", "falsches-passwort"),
    ) as r:
        with pytest.raises(AuthenticationError):
            await r.whoami()


# --- Etappe 2: Vokabular ---------------------------------------------------

async def test_vokabular_liefert_werte_mit_labels(repo):
    werte = await repo.vocab.values("ccm:educationalcontext")
    assert werte, "keine Vokabularwerte fuer ccm:educationalcontext"
    assert all(w.uri and w.label for w in werte), "Wert ohne URI oder Label"


async def test_suggest_sucht_teilstrings_nicht_praefixe(repo):
    """pattern ist eine Teilstring-Suche: "ysik" findet Physik, Atomphysik und
    Kernphysik. Ein Typeahead mit Praefix-Erwartung waere hier falsch gebaut."""
    alle = await repo.vocab.values("ccm:taxonid")
    treffer = await repo.vocab.suggest("ccm:taxonid", "ysik")
    assert 0 < len(treffer) < len(alle)
    assert all("ysik" in w.label.lower() for w in treffer)
    assert any(not w.label.lower().startswith("ysik") for w in treffer)


async def test_label_loest_auf_dieselbe_uri_auf(repo):
    """Die Rundreise Label -> URI -> Label muss stabil sein."""
    werte = await repo.vocab.values("ccm:educationalcontext")
    beispiel = werte[0]
    assert await repo.vocab.resolve("ccm:educationalcontext", beispiel.label) == beispiel.uri


async def test_unbekanntes_label_ergibt_none(repo):
    assert await repo.vocab.resolve("ccm:taxonid", "Unterwasserkorbflechten") is None


# --- Etappe 2: Suche -------------------------------------------------------

async def test_suche_liefert_treffer_mit_id_und_url(repo):
    e = await repo.search("Photosynthese", limit=3)
    assert e.total > 0
    assert len(e.hits) <= 3
    for treffer in e.hits:
        assert treffer.id and treffer.url.endswith(treffer.id)
        assert treffer.title


async def test_filter_grenzt_die_treffermenge_ein():
    """Der Kern: 'Biologie' als Label, gefiltert wird auf die URI dieser Instanz.

    Gegen 'mds_oeh', nicht gegen '-default-': ccm:taxonid fuehrt in beiden ein
    Vokabular, ist aber nur in mds_oeh filterbar. Filterbarkeit ist eine
    Eigenschaft des Metadatensatzes, nicht der Property.
    """
    async with AsyncRepository(os.environ["EDU_SHARING_URL"], metadataset="mds_oeh") as r:
        breit = await r.search("Wasser", limit=1)
        eng = await r.search("Wasser", limit=1, filters={"ccm:taxonid": "Biologie"})
    assert not eng.unresolved, f"Filter nicht aufgeloest: {eng.unresolved}"
    assert 0 < eng.total < breit.total


async def test_nicht_filterbare_property_wird_live_erklaert():
    """Gegenprobe: dieselbe Property im Default-Metadatensatz.

    Die Erklaerung stammt vom Server. Eine Instanz, die Meldungen verbirgt,
    liefert sie nicht -- der Fehlertyp stimmt dort weiterhin, nur der Text
    fehlt. Gemessen am 28.08.2026 gegen redaktion.openeduhub.net.
    """
    async with AsyncRepository(os.environ["EDU_SHARING_URL"]) as r:
        with pytest.raises(ValidationError) as info:
            await r.search("Wasser", limit=1, filters={"ccm:taxonid": "Biologie"})
    if "security.logging.displayLevel" in str(info.value):
        pytest.skip("diese Instanz verbirgt Fehlermeldungen -- der Typ stimmt, "
                    "der erklaerende Text kommt nicht mit")
    assert "metadata set" in str(info.value)


async def test_unaufloesbarer_filter_wird_gemeldet(repo):
    e = await repo.search("Wasser", limit=1, filters={"ccm:taxonid": "Gibtsnicht"})
    assert e.unresolved
    assert e.unresolved[0].value == "Gibtsnicht"


async def test_facetten_zaehlen_serverseitig(repo):
    e = await repo.search("Photosynthese", limit=1, facets=["ccm:taxonid"], facet_limit=5)
    assert e.facets and e.facets[0].values
    assert all(v.count > 0 for v in e.facets[0].values)


async def test_tippfehler_liefert_einen_vorschlag(repo):
    """Ohne returnSuggestions bekaeme die aufrufende Person nur 'keine Treffer'."""
    e = await repo.search("Mathematick", limit=1)
    assert e.total == 0
    assert e.suggestions, "keine Korrekturvorschlaege trotz Tippfehler"


# --- Etappe 2: Repository-Unabhaengigkeit ----------------------------------

async def test_dieselbe_suche_laeuft_gegen_zwei_metadatensaetze():
    """Der Nachweis fuer E4, soweit ohne zweite Instanz moeglich.

    Staging fuehrt vier Metadatensaetze. '-default-' (Contentbuffet, 88
    Widgets, 22 Vokabulare) und 'mds_oeh' (236 Widgets, 107 Vokabulare) sind
    verschieden aufgebaut und liefern verschiedene Treffermengen. Derselbe
    Bibliothekscode muss mit beiden arbeiten, ohne dass einer der beiden
    eincodiert ist.
    """
    url = os.environ["EDU_SHARING_URL"]
    ergebnisse = {}
    for mds in ("-default-", "mds_oeh"):
        async with AsyncRepository(url, metadataset=mds) as r:
            e = await r.search("Physik", limit=1)
            werte = await r.vocab.values("ccm:educationalcontext")
            ergebnisse[mds] = (e.total, len(werte))

    for mds, (total, vokabular) in ergebnisse.items():
        assert total > 0, f"{mds}: keine Treffer"
        assert vokabular > 0, f"{mds}: kein Vokabular"
    # Verschiedene Metadatensaetze -> verschiedene Sicht auf denselben Bestand.
    assert ergebnisse["-default-"][0] != ergebnisse["mds_oeh"][0]


async def test_instanz_ohne_anonymen_zugriff_meldet_das_klar():
    """stable.demo.edu-sharing.net (edu-sharing 9.0) laesst anonym nichts zu:
    selbst /iam/.../-me- antwortet 401. Die Bibliothek muss daraus einen
    Authentifizierungsfehler machen -- nicht abstuerzen und nicht so tun, als
    gaebe es keine Daten.
    """
    async with AsyncRepository("https://stable.demo.edu-sharing.net") as r:
        about = await r.about()
        assert about.repository_version, "auch dort muss /_about gehen"
        with pytest.raises(AuthenticationError):
            await r.whoami()


# --- Etappe 2: Sammlungen --------------------------------------------------

async def test_sammlungssuche_fragt_beide_wege_und_dedupliziert():
    """Prueft, was die Bibliothek leistet -- nicht, wie der Server gerade steht.

    Eine fruehere Fassung verlangte mehr Treffer als ein einzelner Weg liefert,
    weil bei "Deutsch" die Schnittmenge der beiden Wege als NULL gemessen war.
    Das ist nicht stabil: beide Wege liefern je 25 von 876 Sammlungen, und wie
    stark sich diese Auswahlen ueberlappen, schwankt von Aufruf zu Aufruf
    (beobachtet 25 und 29 Treffer fuer dieselbe Anfrage). Ein Test darauf
    schlaegt irgendwann grundlos fehl.

    Was die Bibliothek zusagt und hier geprueft wird: beide Wege werden
    abgefragt, das Ergebnis ist ueber die Knoten-ID dedupliziert, und die
    Gesamtzahl ist als Untergrenze gekennzeichnet.
    """
    async with AsyncRepository(os.environ["EDU_SHARING_URL"], metadataset="mds_oeh") as r:
        e = await r.find_collections("Deutsch", limit=25)
    assert not e.warnings, f"ein Weg ist ausgefallen: {e.warnings}"
    assert e.hits, "keine Sammlungen gefunden"

    ids = [t.id for t in e.hits]
    assert len(ids) == len(set(ids)), "Treffer doppelt -- die Deduplizierung greift nicht"
    assert e.total_is_lower_bound is True


async def test_sammlungstreffer_tragen_id_und_url():
    async with AsyncRepository(os.environ["EDU_SHARING_URL"], metadataset="mds_oeh") as r:
        e = await r.find_collections("Optik", limit=5)
    assert e.hits
    for treffer in e.hits:
        assert treffer.id and treffer.url.endswith(treffer.id)


async def test_sammlungstreffer_tragen_eigenschaften():
    """Weg A muss Eigenschaften mitliefern -- sonst ist jede Aussage ueber eine
    Sammlung eine zweite Anfrage wert.

    Gemessen am 28.08.2026: ohne ``propertyFilter`` kamen 0 Eigenschaften je
    Treffer zurueck, mit ``-all-`` 33 bis 57.
    """
    async with AsyncRepository(os.environ["EDU_SHARING_URL"], metadataset="mds_oeh") as r:
        e = await r.find_collections("Deutsch", limit=25)
    assert e.hits
    mit = [h for h in e.hits if h.properties()]
    assert mit, "kein einziger Sammlungstreffer trug Eigenschaften"


async def test_kuratierte_seiten_sind_am_treffer_erkennbar():
    """Eine Sammlung mit kuratierter Seite traegt ``ccm:page_config_ref``.

    Uebersprungen statt rot, wenn die Instanz keine hat: die Bibliothek ist
    instanzunabhaengig, und "kein Page Builder im Einsatz" ist kein Fehler.
    """
    async with AsyncRepository(os.environ["EDU_SHARING_URL"], metadataset="mds_oeh") as r:
        e = await r.find_collections("Deutsch", limit=25)
    seiten = [h for h in e.hits if h.properties().get("ccm:page_config_ref")]
    if not seiten:
        pytest.skip("diese Instanz fuehrt keine kuratierten Seiten unter diesem Suchwort")
    for treffer in seiten:
        ref = treffer.properties()["ccm:page_config_ref"][0]
        assert ref.startswith("workspace://"), f"kein Store-Ref: {ref!r}"


async def test_bestehende_seite_laesst_sich_lesen(repo):
    """Gegen eine Seite, die jemand anderes gebaut hat -- der Fall, den ein
    selbst gebauter Aufbau nicht abdeckt.

    Uebersprungen, wenn die Instanz keine kuratierte Seite fuehrt: der Page
    Builder ist eine Moeglichkeit von edu-sharing, keine Pflicht.

    **Es wird nach einer rendernden Seite gesucht, nicht die erste genommen.**
    Bis zum 28.08.2026 stand hier ``traeger[0]``, und darauf folgten
    ``assert gerendert.swimlanes`` und ``assert variante.readable``. Beides
    behauptet das Gegenteil dessen, was diese Bibliothek anderswo als gemessenen
    Zustand fuehrt: eine Seite mit null Schwimmlinien und eine nicht lesbare
    Variante gibt es wirklich -- ``14_flow_page.py`` zeigt beide. Zusammen mit
    einer Suche, die messbar unstet ist (dieselbe Anfrage lieferte dreimal
    verschiedene Trefferlisten), war der Test flatterhaft: einmal gesehen
    fallen, danach zweimal gruen.
    """
    treffer = await repo.find_collections("Deutsch", limit=25)
    traeger = [h for h in treffer.hits if h.properties().get("ccm:page_config_ref")]
    if not traeger:
        pytest.skip("diese Instanz fuehrt keine kuratierte Seite unter diesem Suchwort")

    # Gedeckelt: jeder Kandidat kostet zwei Anfragen, und der Test braucht einen,
    # nicht alle.
    for kandidat in traeger[:5]:
        knoten = await repo.node(kandidat.id)
        seite = await knoten.page.get()
        # Das gilt fuer JEDE Seite und wird deshalb an jedem Kandidaten geprueft:
        # sie haengt an einem eigenen Ordner, nicht an der Sammlung.
        if seite is not None:
            assert seite.folder_id and seite.folder_id != knoten.id, (
                f"Seite von {kandidat.id} haengt an der Sammlung selbst")
        if seite and seite.rendered and seite.rendered.swimlanes:
            break
    else:
        pytest.skip("keine der gefundenen Seiten rendert Schwimmlinien -- ein "
                    "gemessener Zustand, kein Fehler")

    gerendert = seite.rendered
    assert all(ln.items for ln in gerendert.swimlanes), "leere Schwimmlinie"
    assert gerendert.node_ids, "keine eingebetteten Knoten gefunden"


async def _mitgliedschaften(repo):
    """Die Gruppen des angemeldeten Kontos, oder ein Uebersprungen.

    Gemessen am 28.08.2026 gegen redaktion.openeduhub.net: anonym liefert
    ``memberships()`` eine leere Liste, und drei Tests starben daraufhin an
    ``gruppen[0]`` mit einem IndexError. Das ist kein Testergebnis, sondern
    eine fehlende Voraussetzung -- die Tests trugen nur den live-Marker und
    ueberspruengen ohne Anmeldung nicht.
    """
    if repo.credential.is_anonymous:
        pytest.skip("Gruppen brauchen ein angemeldetes Konto")
    gruppen = await repo.people.memberships()
    if not gruppen:
        pytest.skip("das angemeldete Konto ist in keiner Gruppe")
    return gruppen


@pytest.mark.live
async def test_eigene_mitgliedschaften(repo):
    """Nur lesend. Die schreibenden Gruppen-Operationen sind mit diesem Konto
    nicht pruefbar -- POST /iam/v1/groups/... antwortet 403."""
    gruppen = await _mitgliedschaften(repo)
    for g in gruppen:
        assert g.name.startswith("GROUP_"), g.name
        assert g.display_name, "eine Gruppe ohne Anzeigenamen"
        assert g.short_name == g.name.removeprefix("GROUP_")


@pytest.mark.live
async def test_eine_gruppe_einzeln_lesen(repo):
    """Der Endpunkt antwortet mit {"group": {...}} -- die Huelle muss weg."""
    gruppen = await _mitgliedschaften(repo)
    einzeln = await repo.people.group(gruppen[0].name)
    assert einzeln.name == gruppen[0].name


@pytest.mark.live
async def test_mitglieder_brauchen_verwaltungsrechte(repo):
    """Gemessen am 28.08.2026: fuer eine Gruppe, in der man nur Mitglied ist,
    antwortet der Endpunkt 500 AccessDeniedException. Uebersetzt ist das ein
    Rechteproblem -- sonst wiederholte der Transport es dreimal."""
    from edusharing.errors import PermissionDeniedError

    gruppen = await _mitgliedschaften(repo)
    with pytest.raises(PermissionDeniedError):
        await repo.people.members(gruppen[0].name)


# --- Die Referenz-Falle, live -----------------------------------------------

@pytest.mark.live
async def test_eine_listing_id_ist_eine_referenz_und_die_sammlungen_kommen_trotzdem(repo):
    """Gemessen am 02.09.2026, Sammlung "Ungleichungen": usage kennt nur das
    Original -- collections_of(Listing-ID) = 0, collections_of(Original) = 2.
    Seither fragt die Bibliothek fuer das Original, und die Sammlung, aus der
    die ID stammt, muss in der Antwort stehen.

    Die Suche ist nicht reproduzierbar und nicht jedes Material ist anonym
    lesbar (dann verweigert die Instanz beide Haelften, und placement wirft --
    richtig so). Darum werden die ersten Treffer durchprobiert, bis ein
    lesbares Paar gefunden ist; keines zu finden ist ein Befund, kein Fehler.
    """
    from edusharing.errors import PermissionDeniedError
    found = await repo.flows.find_collections("Bruchrechnung", limit=5)
    geprueft = 0
    for sammlung in (h["id"] for h in found["hits"]):
        inhalt = await repo.flows.collection_contents(sammlung, limit=3)
        for eintrag in inhalt["materials"]:
            assert eintrag["original_id"], "ein Listing-Eintrag ist eine Referenz"
            try:
                lage = await repo.flows.placement(eintrag["id"])
            except PermissionDeniedError:
                continue                      # nicht anonym lesbar -- naechstes
            geprueft += 1
            assert lage["original_id"] == eintrag["original_id"]
            assert any(c["id"] == sammlung for c in lage["collections"]), lage
            return
    pytest.skip(f"kein anonym lesbares Material in {len(found['hits'])} Sammlungen "
                f"({geprueft} geprueft)")


# --- Volltext, live --------------------------------------------------------

@pytest.mark.live
async def test_text_findet_den_text_eines_treffers():
    """Ohne Dienst: die ersten Treffer zu 'Bruchrechnung' muessen mindestens
    einen Datensatz mit gespeichertem Text haben, und jede Antwort traegt
    dieselben Schluessel -- auch die ohne Text, mit Grund.

    Anonym, und zwar absichtlich: welche Datensaetze vorn liegen, haengt vom
    Konto ab. Gemessen am 02.09.2026: anonym ist unter den ersten sechs ein
    Datensatz mit gespeichertem Text (Quelle "repository"); angemeldet waren
    es andere sechs, und nur einer trug Text, per "download". Der Ablauf ist
    derselbe -- der Beleg fuer die /textContent-Quelle braucht die anonyme
    Sicht.
    """
    async with AsyncRepository(os.environ["EDU_SHARING_URL"]) as anon:
        result = await anon.search("Bruchrechnung", limit=6)
        quellen = []
        for hit in result.hits:
            got = await anon.flows.text(hit.id)
            assert set(got) == {"id", "title", "text", "source", "source_url",
                                "char_count", "truncated", "reason", "detail"}
            assert (got["source"] != "none") == (got["reason"] == "")
            quellen.append(got["source"])
    assert "repository" in quellen, quellen


# --- Dubletten, live -------------------------------------------------------

@pytest.mark.live
async def test_find_by_url_findet_den_datensatz_zu_einer_bekannten_adresse():
    """Gemessen am 02.09.2026: mit mds_oeh ist ccm:wwwurl ein Kriterium und die
    Adresse eines Treffers findet genau diesen Treffer wieder; -default-
    weist das Kriterium zurueck."""
    from edusharing.errors import ValidationError
    from edusharing.flows.duplicates import find_by_url
    async with AsyncRepository.from_env(metadataset="mds_oeh") as repo:
        hits = (await repo.search("Bruchrechnung", limit=8)).hits
        hit = next((h for h in hits if h.source_url), None)
        assert hit is not None, "kein verlinkter Treffer unter den ersten acht"
        found = await find_by_url(repo, hit.source_url)
        assert found is not None
        assert found["url"].lower() == hit.source_url.lower()
    async with AsyncRepository.from_env() as repo:
        with pytest.raises(ValidationError):
            await find_by_url(repo, hit.source_url)


# --- Paket 4, live: Suchgleichstand ----------------------------------------

@pytest.mark.live
async def test_ausschluss_haelt_die_seite_voll():
    async with AsyncRepository.from_env(metadataset="mds_oeh") as repo:
        erste = await repo.flows.search("Bruchrechnung", limit=5)
        weg = [h["id"] for h in erste["hits"][:2]]
        zweite = await repo.flows.search("Bruchrechnung", limit=5, exclude_ids=weg)
    ids = [h["id"] for h in zweite["hits"]]
    assert not set(weg) & set(ids)
    assert len(ids) == 5, ids


@pytest.mark.live
async def test_sammlungen_lassen_sich_nach_fach_filtern_und_unter_einer_eltern_sammlung_finden():
    async with AsyncRepository.from_env(metadataset="mds_oeh") as repo:
        gefiltert = await repo.flows.find_collections(
            "Optik", subject="Physik", limit=10, properties=["ccm:taxonid"])
        assert gefiltert["unresolved"] == []
        physik = set(gefiltert["query"]["filters"]["ccm:taxonid"])
        # Sammlungstreffer tragen die URI, aber kein _DISPLAYNAME (gemessen) --
        # darum die Eigenschaft selbst und nicht das Label.
        for hit in gefiltert["hits"]:
            assert physik & set(hit["fields"].get("ccm:taxonid", [])), hit
        alle = await repo.flows.find_collections("Optik", limit=10)
        eltern = next((h["id"] for h in alle["hits"]
                       if h["title"].strip().lower() == "optik"), None)
        assert eltern, [h["title"] for h in alle["hits"]]
        unten = await repo.flows.find_collections("", parent_id=eltern, limit=50)
    assert unten["hits"], "die Optik-Sammlung hat Untersammlungen (gemessen: Wellenoptik, Farben …)"
    assert unten["query"]["parent_id"] == eltern


@pytest.mark.live
async def test_search_all_mit_seiten_und_eigenschaften():
    async with AsyncRepository.from_env(metadataset="mds_oeh") as repo:
        got = await repo.flows.search_all("Optik", include_pages=True,
                                          properties=["ccm:wwwurl"], limit=5)
    assert "pages" in got and "hits" in got["pages"]
    assert got["materials"]["hits"], "Material zu Optik"
    assert any("ccm:wwwurl" in h["fields"] for h in got["materials"]["hits"]), \
        "die gewuenschte Eigenschaft erscheint unter fields"


# --- Paket 6, live: Skills --------------------------------------------------

@pytest.mark.live
async def test_skills_werden_gefunden_und_gelesen():
    """Gemessen 02.09.2026: 34 Skills mit mds_oeh; die SKILL.md kommt per
    download(); der Arbeitsordner ist anonym gesperrt -- ein Grund, kein Fehler."""
    async with AsyncRepository.from_env(metadataset="mds_oeh") as repo:
        found = await repo.flows.find_skills("Lehrkontext")
        assert found["hits"], found
        doc = await repo.flows.skill(found["hits"][0]["id"])
        assert doc["content"] and len(doc["content"]) > 1000
        assert doc["files_reason"] in ("folder_unreadable", "", "no_folder", "too_many")
        if repo.credential.is_anonymous:
            assert doc["files_reason"] == "folder_unreadable", doc["files_reason"]


@pytest.mark.live
async def test_die_registry_einer_sammlung_wird_gelesen():
    """Sammlung "Geometrische Optik" traegt ein ai_prompt-Markdown (gemessen)."""
    async with AsyncRepository.from_env(metadataset="mds_oeh") as repo:
        reg = await repo.flows.skill_registry("f35c17d1-a29e-4b26-9d22-802682fad43d")
    assert reg["reason"] == "", reg
    assert reg["registry_id"]
    assert reg["entries"] or reg["unresolved"], "ein Registry-Dokument ohne einen Block"


@pytest.mark.live
async def test_der_vorgabe_metadatensatz_kennt_die_inhaltsart_nicht():
    async with AsyncRepository.from_env() as repo:
        with pytest.raises(ValidationError):
            await repo.flows.find_skills("x")
