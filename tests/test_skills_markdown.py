"""Was ein Skill-Dokument ueber sich sagt -- ohne I/O.

Die Redaktion schreibt Verweise als Bloecke in die Markdown-Datei und gliedert
eine Registry mit Ueberschriften. Das ist schon ein Manifest, es steht nur in
Prosa. Es HIER zu lesen statt einem Modell zu ueberlassen ist der Punkt: eine
Knoten-ID in einer URL in einem Markdown-Link in einem Block ist eine
Extraktionsaufgabe, und die hat eine Fehlerquote. Regeln wie im MCP
(``skill-references.ts``, ``markdown-sections.ts``, ``registry-contexts.ts``),
gegen Staging gemessen: ``skill_registry.md`` traegt 7 ``::: ki-skill``-Bloecke
und 3 Kontexte.
"""

from edusharing.skills_markdown import layout_contexts, parse_blocks, parse_sections

RENDER = "https://repo.test/edu-sharing/components/render/"
A = "12c04f9c-20b5-4461-804f-9c7b1a2d3e4f"
B = "ccdcae49-d4db-4e4a-9cae-49d4db1e4a11"
C = "aa11bb22-cc33-4d44-8e55-f66778899aab"
M = "0f0f0f0f-1111-4222-8333-444455556666"

REGISTRY = f"""# Skills für die Sammlung Optik

Für die Arbeit mit dieser Sammlung freigegeben. Bitte immer erst den Bestand
sichten, bevor etwas Neues entsteht.

::: ki-skill
[Lehrprofil auswerten]({RENDER}{A})
:::

## Unterricht vorbereiten

Für die Sekundarstufe I zuerst den Fragen-Skill.

::: wlo-material
![Titel](https://repo.test/edu-sharing/preview?nodeId={M})
[**Ein Arbeitsblatt**](https://example.org/quelle) — Lizenz: CC BY
:::

::: ki-skill
[**Fragen generieren**]({RENDER}{B})
:::

### Wochenplanung

Nur für ganze Unterrichtsreihen.

::: ki-skill
[Skill\\_Reihenplan\\_entwerfen]({RENDER}{C})
:::

## Material erschließen

Beim Beschreiben die Fachsystematik der Sammlung verwenden.

##

Ohne Titel: gehört zum allgemeinen Teil.
"""


# --- Bloecke ---------------------------------------------------------------

def test_bloecke_mit_art_titel_url_und_knoten_id():
    refs = parse_blocks(REGISTRY)
    assert [(r.kind, r.node_id) for r in refs] == [
        ("ki-skill", A), ("wlo-material", M), ("ki-skill", B), ("ki-skill", C)]
    assert refs[0].title == "Lehrprofil auswerten"
    assert refs[0].url == f"{RENDER}{A}"


def test_der_titel_ist_der_erste_link_der_kein_bild_ist():
    """Beim Material zeigt der Titellink auf die QUELLE; die Knoten-ID kommt aus
    dem Vorschaubild -- das erste Vorkommen im Block gewinnt."""
    material = parse_blocks(REGISTRY)[1]
    assert material.title == "Ein Arbeitsblatt"
    assert material.url == "https://example.org/quelle"
    assert material.node_id == M


def test_hervorhebung_und_backslash_escapes_verschwinden_aus_dem_titel():
    """Gemessen an der echten Optik-Registry: ``Skill\\_X`` -- der Unterstrich
    ist escaped, weil ``_so_`` kursiv waere -- und der Backslash kam mit."""
    refs = parse_blocks(REGISTRY)
    assert refs[2].title == "Fragen generieren"
    assert refs[3].title == "Skill_Reihenplan_entwerfen"


def test_ein_block_ohne_link_verweist_auf_nichts():
    assert parse_blocks("::: ki-skill\nnur Prosa\n:::\n") == []


def test_ein_offener_block_erfindet_nichts():
    assert parse_blocks("::: ki-skill\n[X](" + RENDER + A + ")\n") == []


def test_ein_block_ohne_repositoriumsadresse_hat_keine_id():
    refs = parse_blocks("::: ki-skill\n[Extern](https://example.org/x)\n:::\n")
    assert refs[0].title == "Extern" and refs[0].node_id == ""


def test_offsets_zeigen_auf_den_oeffnenden_zaun():
    refs = parse_blocks(REGISTRY)
    for r in refs:
        assert REGISTRY.startswith(":::", r.offset)


def test_nur_die_genannten_arten():
    assert [r.kind for r in parse_blocks(REGISTRY, kinds=("ki-skill",))] == ["ki-skill"] * 3


# --- Abschnitte ------------------------------------------------------------

def test_abschnitte_mit_ebene_titel_und_reichweite():
    secs = parse_sections(REGISTRY)
    assert [(s.level, s.title) for s in secs] == [
        (1, "Skills für die Sammlung Optik"), (2, "Unterricht vorbereiten"),
        (3, "Wochenplanung"), (2, "Material erschließen"), (2, "")]
    h2 = secs[1]
    assert REGISTRY[h2.heading_start:].startswith("## Unterricht")
    assert h2.end == secs[3].heading_start, "eine H2 schliesst erst die naechste H2"
    assert secs[2].end == secs[3].heading_start, "eine H3 endet auch an der naechsten H2"


def test_setext_und_zaeune_sind_keine_ueberschriften():
    text = "Titel\n=====\n\n```\n# kein Titel\n```\n\n#nicht\n\n## Echt\n"
    assert [s.title for s in parse_sections(text)] == ["Echt"]


# --- Kontexte --------------------------------------------------------------

def test_kontexte_aus_benannten_h2_und_h3():
    refs = parse_blocks(REGISTRY)
    layout = layout_contexts(REGISTRY, refs)
    assert [c.path for c in layout.contexts] == [
        "Unterricht vorbereiten", "Unterricht vorbereiten/Wochenplanung",
        "Material erschließen"]
    assert layout.contexts[0].skills == [B]
    assert layout.contexts[1].skills == [C]
    assert layout.contexts[2].skills == []
    assert layout.paths == [None, "Unterricht vorbereiten", "Unterricht vorbereiten",
                            "Unterricht vorbereiten/Wochenplanung"]


def test_allgemeiner_teil_sammelt_was_ausserhalb_liegt():
    layout = layout_contexts(REGISTRY, parse_blocks(REGISTRY))
    assert layout.general.skills == [A]
    assert "Bestand" in layout.general.instruction
    assert "Ohne Titel" in layout.general.instruction, "eine namenlose H2 ist transparent"


def test_die_anweisung_endet_am_ersten_block():
    layout = layout_contexts(REGISTRY, parse_blocks(REGISTRY))
    erste = layout.contexts[0].instruction
    assert "Fragen-Skill" in erste
    assert ":::" not in erste and "preview?nodeId" not in erste, \
        "ein Materialblock beendet die Anweisung ebenso"


def test_eine_h2_umfasst_ihre_h3():
    layout = layout_contexts(REGISTRY, parse_blocks(REGISTRY))
    eltern, kind = layout.contexts[0], layout.contexts[1]
    assert eltern.range[0] < kind.range[0] and kind.range[1] <= eltern.range[1]


def test_mehr_als_fuenfzig_kontexte_werden_gemeldet():
    text = "".join(f"## K{i}\n\n::: ki-skill\n[S]({RENDER}{A})\n:::\n\n" for i in range(55))
    layout = layout_contexts(text, parse_blocks(text))
    assert len(layout.contexts) == 50
    assert layout.truncated == (50, 55)
