"""Tests gegen ein echtes Repositorium.

Laufen nur mit ``pytest -m live`` und gesetztem ``EDU_SHARING_URL``. Alles
andere in dieser Suite kommt ohne Netz aus; diese Tests beantworten die eine
Frage, die Mocks nicht beantworten koennen: stimmt unser Bild vom Server noch?

    EDU_SHARING_URL=https://repository.staging.openeduhub.net uv run pytest -m live
"""

import os

import pytest

from edusharing import AsyncRepository
from edusharing.errors import AuthenticationError, NotFoundError, ValidationError

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
    """
    if not repo.credential.is_anonymous:
        pytest.skip("nur als Gast aussagekraeftig")
    with pytest.raises(AuthenticationError):
        await repo.raw.json("GET", "/iam/v1/people/-home-/-me-/preferences")


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
    """Gegenprobe: dieselbe Property im Default-Metadatensatz."""
    async with AsyncRepository(os.environ["EDU_SHARING_URL"]) as r:
        with pytest.raises(ValidationError) as info:
            await r.search("Wasser", limit=1, filters={"ccm:taxonid": "Biologie"})
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


@pytest.mark.live
async def test_eigene_mitgliedschaften(repo):
    """Nur lesend. Die schreibenden Gruppen-Operationen sind mit diesem Konto
    nicht pruefbar -- POST /iam/v1/groups/... antwortet 403."""
    gruppen = await repo.people.memberships()
    assert gruppen, "das angemeldete Konto ist in keiner Gruppe"
    for g in gruppen:
        assert g.name.startswith("GROUP_"), g.name
        assert g.display_name, "eine Gruppe ohne Anzeigenamen"
        assert g.short_name == g.name.removeprefix("GROUP_")


@pytest.mark.live
async def test_eine_gruppe_einzeln_lesen(repo):
    """Der Endpunkt antwortet mit {"group": {...}} -- die Huelle muss weg."""
    gruppen = await repo.people.memberships()
    einzeln = await repo.people.group(gruppen[0].name)
    assert einzeln.name == gruppen[0].name


@pytest.mark.live
async def test_mitglieder_brauchen_verwaltungsrechte(repo):
    """Gemessen am 28.08.2026: fuer eine Gruppe, in der man nur Mitglied ist,
    antwortet der Endpunkt 500 AccessDeniedException. Uebersetzt ist das ein
    Rechteproblem -- sonst wiederholte der Transport es dreimal."""
    from edusharing.errors import PermissionDeniedError

    gruppen = await repo.people.memberships()
    with pytest.raises(PermissionDeniedError):
        await repo.people.members(gruppen[0].name)
