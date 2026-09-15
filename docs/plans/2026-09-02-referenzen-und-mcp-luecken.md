# Entwurf: Referenzen auflösen, und die Abläufe, die dem MCP noch fehlen

Stand: 02.09.2026 · Status: **freigegeben, sechs Pakete** · Prüfgegenstand:
die Bibliothek bei `36704e0`, Maßstab: `wlo-mcp-server-sc` (41 Werkzeuge, nur
gelesen).

**Entscheidungen vom 02.09.2026:** Schreiben an einer Referenz wird ans
Original **umgeleitet und ausgewiesen** (Ansatz C). `add_material(url=…)`
nennt einen vorhandenen Datensatz und legt keinen zweiten an
(`if_exists="return"`). Alle fünf Pakete — **und dazu die Skills**:
Skill-Suche, Skill-Abruf und die Skill-Registry einer Sammlung (Paket 6).
Draußen bleiben Wikipedia, das Fachportal nach Name (an ein Repositorium
gebunden) und die `search`/`fetch`-Konvention (OpenAI-spezifisch).

## Ziel

Jede Funktion des MCP-Servers, die edu-sharing betrifft, soll sich mit der
Bibliothek in wenigen Zeilen bauen lassen — und die Bibliothek darf dabei keine
Antwort geben, die der MCP als falsch gemessen hat. Der zweite Punkt ist der
dringende: **eine ID aus einem Sammlungs-Listing lässt die Bibliothek heute
„in keiner Sammlung" sagen und Schreibvorgänge ins Leere laufen.**

## Kontext

Der Abgleich vom 28.08.2026 (`2026-08-28-restliche-endpunkte-und-ablaeufe.md`)
zählte 23 von 41 MCP-Werkzeugen als abbildbar. Seither kamen vier Pakete dazu
(Bewertungen, Kommentare, Gruppen, Vorschläge, Redaktion, Blättern, Umbenennen,
fünf Abläufe, kuratierte Seiten). Der Abgleich vom 02.09.2026 gegen die
tatsächlichen Werkzeugverträge des MCP ergibt:

| Stand | Werkzeuge | Beispiele |
|---|---|---|
| direkt abbildbar (ein Aufruf) | 24 | `search_wlo_content`, `get_node_details`, `get_collection_stats`, `wlo_suggest_metadata`, `wlo_set_topic_page` |
| abbildbar, aber mehrere Aufrufe von Hand | 8 | `get_wlo_content_text` (Beispiel 15 braucht 215 Zeilen), `wlo_decide_suggestion` (annehmen ≠ anwenden), `wlo_create_content` (keine Dublettenprüfung) |
| bewusst draußen (Instanzkonvention, kein edu-sharing) | 9 | Wikipedia, Skills-Registry (3), Qualitäts-/Zugangs-Labels, Kompendium-Gliederung, Fachportal-Name, `search`/`fetch`-Konvention |

Das ist gut — und verdeckt den Befund, der zählt.

## Was am 02.09.2026 gemessen wurde

Alles gegen Staging, anonym, ohne zu schreiben.

### A. Die Referenz-Falle — die Bibliothek antwortet falsch

Eine Sammlung hält **Referenzen**, nicht die Datensätze. `collection_contents`
liefert deshalb Referenz-IDs — und das ist der gewöhnliche Weg, an eine ID zu
kommen, nicht ein Sonderfall.

```
Sammlung "Ungleichungen" (39f845f1-…), erstes Material:
  Listing-ID  e192b21c-…   Aspekt ccm:collection_io_reference: True
  DTO.originalId           c1af1dc9-…
  ccm:original             c1af1dc9-…   (zeigt auf dem Original auf sich selbst)

  collections_of(Listing-ID)               = 0 Sammlungen
  collections_of(Original)                 = 2 Sammlungen
  node.collections()  an der Listing-ID    = 0
  flows.placement(Listing-ID)["collections"] = 0
```

`/usage/v1/usages/node/{id}/collections` kennt nur das Original und antwortet
für eine Referenz mit `200` und einer leeren Liste. Die Bibliothek reicht das
als „dieser Knoten liegt in keiner Sammlung" durch — ohne Fehler, ohne Hinweis.
Kein Test deckt das ab; `README`, `FLOWS`, `REFERENCE` und der Skill kennen das
Wort „Referenz-ID" nicht.

Für Schreibvorgänge hat der MCP dasselbe am 17.08.2026 gemessen
(`services/write/nodes.ts`, F1/F2/F6/F10): ein `PUT /metadata` an eine Referenz
wird **auf der Referenz gespeichert**, erreicht das Original nie, und die
Referenz hört ab dann auf zu erben. Die Rückleseprobe der Bibliothek kann das
nicht bemerken — sie liest denselben Knoten und findet genau den Wert, den sie
geschrieben hat. Löschen dagegen entfernt an einer Referenz nur die Referenz
(F10): harmlos, und darum darf eine Löschung *nicht* umgeleitet werden.

Der MCP löst mit `DTO.originalId` auf, nie über `ccm:original` — das zeigt auf
einem Original auf sich selbst, und eine darauf gebaute Regel meldet jeden
Datensatz als Referenz auf sich selbst, sobald der Selbstvergleich fehlt.

### B. Dokumentation gegen Signatur

`ancestry_of(nodes: Nodes, node_id)` und `collections_of(nodes: Nodes, node_id)`
nehmen ein `Nodes`-Objekt; `REFERENCE.md:257–258` dokumentiert
`ancestry_of(repo, node_id)`. Jede andere freie Funktion nimmt `repo`
(`search_reranked(repo, …)`, `sub_collections(repo, …)`, `rating_of(repo, …)`).
Der Signatur-Wächter prüft nur `repo.x(…)`-Zeilen, nicht freie Funktionen — so
kam es durch.

### C. Was der MCP als Abläufe hat und die Bibliothek als Bausteine

| MCP | Bibliothek heute | Was fehlt |
|---|---|---|
| `get_wlo_content_text` — Repositorium zuerst, dann die verlinkte Seite, `source`/`reason` | `node.content.text()` (kein Rückfall), `TextExtraction.text_of()` getrennt | ein Ablauf, der beides verbindet und *sagt, warum* kein Text da ist |
| `wlo_decide_suggestion` accept — Wert schreiben, zurücklesen, **dann** annehmen | `suggestions.decide()` markiert nur (gemessen: `ACCEPTED` schreibt nichts) | der zusammengesetzte Schritt |
| `wlo_create_content` mit `url` — vorher prüfen, ob es den Datensatz schon gibt | `add_material` legt an | die Dublettenprüfung über `ccm:wwwurl` |
| `search_wlo_*` mit `excludeNodeIds`, Facetten bis 100 | `flows.search` ohne `exclude`, `facet_limit` nur auf API-Ebene | zwei Parameter |
| `search_wlo_collections` mit Fach/Stufe und `parentNodeId` | `find_collections(text, limit)` | Filter und Elternbereich |
| Treffer mit `previewUrl`, `downloadUrl`, `license`, `mimeType`, `fileSize` | `hit_as_dict` ohne Vorschau, Download, Lizenz, Größe | vier Felder, die im DTO schon liegen |
| `search_wlo_all` mit Themenseiten-Topf | `search_all` = Material + Sammlungen; `find_pages` getrennt | der dritte Topf |

### D. Skills — was die Bibliothek heute davon kann, gemessen

Gegen Staging, anonym, `metadataset="mds_oeh"`:

```
repo.search(filters={"ccm:oeh_extendedType": <ai_skill-URI>})   → 34 Treffer
  mit dem Vorgabe-Metadatensatz "-default-"                     → ValidationError
      "Could not find parameter ccm:oeh_extendedType"  (der Fehlertext erklärt es)
Skill "Lehrkontext erfassen und halten":
  mimetype text/x-web-markdown · mediatype file-markdown
  content.download() = 14 493 Bytes · content.text() = 0 Zeichen   ← Markdown-Falle
  virtual:primaryparent_nodeid über /metadata vorhanden
  ccm:original zeigt auf dem Original auf sich selbst (F6 des MCP bestätigt)
  repo.nodes.children(<Arbeitsordner>)  → 403 anonym   ← Begleitdateien brauchen Rechte
Registry-Dokumente (ai_prompt): 2 anonym — skill_katalog.md, skill_registry.md
  skill_registry.md: 1 674 Zeichen, 7 ::: ki-skill-Blöcke, 3 Kontexte (H2/H3),
  7 eindeutige Knoten-IDs in den Blöcken; /usage nennt keine Sammlung
Sammlung "Geometrische Optik" (f35c17d1-…): 4 Materialien, eines ai_prompt
  /children/references mit propertyFilter=-all-: Typ sichtbar (1/4)
  flows.collection_contents: Typ sichtbar bei 0/4   ← hit_as_dict zeigt nur `fields`
```

Drei Folgerungen. **Erstens** entscheidet der Metadatensatz, ob man nach der
Inhaltsart filtern kann; `from_env()` kennt dafür keine Umgebungsvariable.
**Zweitens** liest man eine SKILL.md mit `download()`, nie mit `text()`.
**Drittens** verschweigt `collection_contents` jede Eigenschaft ohne Kurznamen —
eine Anwendung, die die Inhaltsart eines Listing-Eintrags braucht, muss den
Ablauf verlassen.

Der MCP maß am 08.08. noch, dass `-all-` die Inhaltsart auf `/children`
**nicht** liefert; heute liefert die Sammlungsroute sie mit `-all-`. Beide
Messungen stehen mit Datum, die Bibliothek verlässt sich auf keine davon: der
Skill-Code fordert die Eigenschaft ausdrücklich an.

### E. Werkzeuglauf

* `mypy --strict`: 19 Befunde in 8 Dateien. Einer verdient Aufmerksamkeit:
  `flows/rerank.py:96` reicht `**aliases` in `Search.search` weiter, dessen
  positionelle Parameter (`facet_limit`, `limit`, `offset`, `content_type`)
  damit von einem gleichnamigen Kurznamen überschrieben werden könnten.
* `ruff --select B,PIE,SIM,RET,PL,RUF,ASYNC,PERF`: 70 Meldungen, davon
  `PLR0124 comparison-with-itself` in `errors.py:291` — der bewusste
  NaN-Vergleich, kommentiert; kein Fehler. Der Rest ist Stil.
* Live gegen Staging: der temporäre Login `sc25-14@…` wird seit heute mit
  `401` abgelehnt — alle 48 Fehlschläge des ersten Laufs waren
  `AuthenticationError`, nicht Bibliotheksfehler. Anonymer Lauf: siehe Bericht.

## Umfang

**Drin** — fünf Pakete, nach Dringlichkeit:

1. **Referenzen** — `original_id` am Knoten und am Treffer, Auflösung beim
   Lesen der Sammlungen, Umleitung mit Ausweis beim Schreiben, keine Umleitung
   beim Löschen, die Falle in allen vier Dokumenten.
2. **`flows.text`** — Volltext mit Rückfall und Grund.
3. **Schreibseite** — `accept_suggestion`, Dublettenprüfung in `add_material`.
4. **Suchgleichstand** — `exclude_ids`, `facet_limit`, Filter für
   `find_collections`, vier Trefferfelder, Themenseiten-Topf in `search_all`.
5. **Konsistenz** — freie Funktionen nehmen `repo`, Signatur-Wächter für freie
   Funktionen, der `rerank`-Befund.
6. **Skills** — Suche, Abruf mit Begleitdateien und Verweisen, die Registry
   einer Sammlung mit Kontexten; die Konventionen (Inhaltsart-URIs, Erkennung
   des Registry-Dokuments, Blockarten) als **Parameter mit WLO-Vorgabe**,
   nicht fest verdrahtet — wie `metadataset`.

**Draußen**, weiterhin und bewusst:

* Wikipedia, `search`/`fetch`-Konvention — kein edu-sharing.
* Qualitäts- und Zugangsbewertungen (`ccm:oeh_quality_*`,
  `ccm:conditionsOfAccess`), Kompendium-Gliederung, Fachportal nach Name,
  Lizenzbündel „OER" — Konventionen einer Instanz. Alle Eigenschaften sind über
  `node.properties` und `filters={…}` erreichbar; die Bibliothek benennt sie
  nicht.
* Die Aktivierungszeile, die ein Modell beim Anwenden eines Skills ausgeben
  soll — Sache des Werkzeugs, das dem Modell gegenübersteht. Die Bibliothek
  liefert das Dokument und sagt, dass es Daten ist (`as_untrusted`).
* Bestätigungsschlüssel (Vorschau → `confirmToken`) für jeden Schreibvorgang —
  das ist Sache des Werkzeugs, das die Bibliothek benutzt; `plan_update`
  liefert das Muster für Änderungen.

## Ansatz

Drei Wege für die Referenz-Falle wurden erwogen:

**A — nur dokumentieren.** Billig, aber die Bibliothek gäbe weiter eine falsche
Antwort auf die häufigste ID-Herkunft. Verworfen.

**B — beim Lesen auflösen, beim Schreiben verweigern.** Ehrlich, aber jede
Anwendung müsste vor jedem `update()` selbst auflösen; der MCP hat gezeigt, dass
das die Regel ist, nicht die Ausnahme. Verworfen.

**C — beim Lesen auflösen, beim Schreiben umleiten und ausweisen, beim Löschen
nicht umleiten.** Der Weg des MCP, gemessen. Der zurückgegebene Knoten trägt
`redirected_from`, damit niemand eine Umleitung übersieht, und `flows.delete`
sagt, ob eine Referenz oder ein Original ging. **Gewählt.**

Für die übrigen Pakete gilt die Regel des Hauses: ein Ablauf ist ein `dict`
mit den Schlüsseln, die er dokumentiert; das Fehlgeschlagene wird berichtet,
nicht verschwiegen; jede neue Eigenheit wird gemessen, nicht abgeleitet.

## Architektur

### Dateien

| Datei | Änderung | Paket |
|---|---|---|
| `src/edusharing/nodes.py` (640 Z.) | `Node.original_id`, `Node.is_reference`, `Node.aspects`, `Node.redirected_from`; `update()`/`set_property()` schreiben ans Original | 1 |
| `src/edusharing/results.py` | `SearchHit.original_id` | 1 |
| `src/edusharing/placement.py` | `collections_of` nimmt `repo | Nodes`, löst über den gelesenen Knoten auf; `ancestry_of` ebenso | 1, 5 |
| `src/edusharing/flows/describe.py` | `describe`: `original_id`, `aspects`; `placement`: liest den Knoten einmal, gibt `original_id` zurück | 1 |
| `src/edusharing/flows/curate.py` | `delete`: `is_reference`, `original_id` im Ergebnis; `add_material`: `if_exists` | 1, 3 |
| `src/edusharing/flows/text.py` (neu, ~120 Z.) | `text(repo, node_id, *, extraction=None, max_chars=…)` | 2 |
| `src/edusharing/flows/suggest.py` (neu, ~90 Z.) | `accept_suggestion(repo, node_id, suggestion_id)` | 3 |
| `src/edusharing/flows/find.py` (399 Z. → **teilen**: `collections.py` für `find_collections`/`search_all`) | `exclude_ids`, `facet_limit`; Filter + `parent_id` für `find_collections`; `include_pages` | 4 |
| `src/edusharing/flows/serialize.py` | `hit_as_dict`: `preview_url`, `download_url`, `license`, `size`, `original_id` | 1, 4 |
| `src/edusharing/flows/rerank.py` | `**aliases` nur noch als `filters` weiterreichen | 5 |
| `src/edusharing/flows/__init__.py` | zwei neue Methoden: `text`, `accept_suggestion` | 2, 3 |
| `src/edusharing/_sync.py` | die zwei Methoden spiegeln | 2, 3 |
| `tests/test_docs_complete.py` | Signatur-Wächter auch für `name(repo, …)`-Zeilen | 5 |
| `src/edusharing/skills_markdown.py` (neu, ~160 Z., rein) | `parse_blocks`, `parse_sections`, `layout_contexts` — kein I/O | 6 |
| `src/edusharing/skills.py` (neu, ~260 Z.) | `SkillConventions`, `Skills` (`search`, `get`, `registry`, `pick`), die Wertobjekte | 6 |
| `src/edusharing/flows/skills.py` (neu, ~120 Z.) | `find_skills`, `skill`, `skill_registry`, `pick_skill` als `dict` | 6 |
| `src/edusharing/repository.py` | `repo.skills`; `from_env` liest `EDU_SHARING_METADATASET` | 6 |
| `docs/FLOWS(.de).md`, `docs/REFERENCE(.de).md`, Skill-Paar, `CHANGELOG.md` | die Falle, die sechs Abläufe, die neuen Parameter | alle |

`find.py` steht mit 399 Zeilen über der Schwelle und bekäme durch Paket 4 eine
zweite Verantwortung (Sammlungssuche mit Filtern). Erst teilen, dann erweitern.

### Datenfluss — Referenz beim Lesen

```
collection_contents(S)  →  Treffer mit id = Referenz-ID, original_id = O
repo.node(Referenz-ID)  →  Node.id = Referenz-ID, .original_id = O, .is_reference
node.collections()      →  GET /usage/…/node/O/collections   (nicht Referenz-ID)
flows.placement(R)      →  liest R einmal, fragt Weg-nach-oben mit R,
                           Sammlungen mit O; gibt {id: R, original_id: O, …}
```

### Datenfluss — Referenz beim Schreiben

```
node.update(title=…) an einer Referenz
  → PUT /node/…/O/metadata          (Umleitung ans Original)
  → GET O, Rückleseprobe wie bisher
  → Node(O) mit redirected_from = R
node.delete()  an einer Referenz
  → DELETE R                         (KEINE Umleitung; entfernt die Referenz)
flows.delete(R) → {…, "is_reference": True, "original_id": O, "recycled": …}
```

### Öffentliche Schnittstellen

```python
class Node:
    original_id: str | None        # DTO.originalId; None auf einem Original
    is_reference: bool             # original_id is not None
    aspects: tuple[str, ...]       # DTO.aspects
    redirected_from: str | None    # gesetzt auf dem Knoten, den update() zurückgibt

class SearchHit:
    original_id: str | None

async def collections_of(repo_or_nodes, node_id, *, original_id=None) -> list[Node]
async def ancestry_of(repo_or_nodes, node_id) -> Ancestry

# flows
async def text(repo, node_id, *, extraction: TextExtraction | None = None,
               max_chars: int = 200_000) -> dict
# → {id, title, text, source: "repository"|"extraction"|"none",
#    source_url, char_count, truncated, reason: ""|"node_not_found"|
#    "no_text_no_url"|"no_extraction_service"|"extraction_failed"|"access_denied"}

async def accept_suggestion(repo, node_id, suggestion_id) -> dict
# → {id, suggestion_id, property, value, applied: bool, status, failed: [...]}

async def add_material(..., if_exists: Literal["create","return","raise"] = "return")
# → zusätzlich {"existing": {"id": ..., "url": ...} | None}

async def search(..., exclude_ids: Sequence[str] = (), facet_limit: int = 20)
async def find_collections(text, *, limit=10, parent_id: str | None = None, **aliases)
async def search_all(text, *, include_pages: bool = False, ...)   # dritter Topf "pages"

async def delete(repo, node_id, *, recycle=True)
# → zusätzlich {"is_reference": bool, "original_id": str | None}

# Skills (Paket 6) — API-Ebene
@dataclass(frozen=True)
class SkillConventions:
    type_property: str = "ccm:oeh_extendedType"
    skill_type: str = "http://w3id.org/openeduhub/vocabs/contentTypes/ai_skill"
    registry_type: str = "http://w3id.org/openeduhub/vocabs/contentTypes/ai_prompt"
    registry_mark: str = r"skill[\s_-]*(registry|catalogue|catalog|katalog)"
    markdown_mimetypes: frozenset[str] = frozenset({"text/x-web-markdown", "text/markdown", "text/x-markdown"})
    block_kinds: tuple[str, ...] = ("ki-skill", "wlo-material")
WLO_SKILLS = SkillConventions()            # die Vorgabe, wie mds_oeh eine Vorgabe ist

class Skills:                              # repo.skills
    async def search(self, text="", *, collection_id=None, include_subcollections=False,
                     limit=10, conventions=WLO_SKILLS, **aliases) -> SkillSearch
    #   repositoriumsweit: Search mit {type_property: skill_type} + aliases (subject=, level=)
    #   in einer Sammlung: begrenzter Gang (Tiefe ≤ 2, ≤ 30 Sammlungen, Seite 50),
    #   Typ lokal geprüft; Dublette Referenz/Original → Original gewinnt;
    #   Rang: Titel 3 · Schlagwörter 2 · Beschreibung 1 (flows.ranking.term_matches)
    async def get(self, node_id, *, include_files=True, conventions=WLO_SKILLS) -> SkillDocument
    #   Text über download() (text() ist für Markdown leer, gemessen);
    #   Begleitdateien: Ordner des ORIGINALS (virtual:primaryparent_nodeid),
    #   ≤ 50 Einträge sonst nur Zählung; 403 → files_reason="folder_unreadable"
    async def registry(self, collection_id, *, context=None, resolve=True,
                       conventions=WLO_SKILLS) -> SkillRegistry | RegistryMiss
    #   über die Kinder der Sammlung, nie über den Index; Kandidat = registry_type
    #   + Markdown; markiert nach Name/Titel; Gleichstand → kleinste ID + ambiguous;
    #   ::: ki-skill-Blöcke, Kontexte aus H2/H3, Köpfe mit Pool 10 aufgelöst, ≤ 100
    async def pick(self, text, **same_as_search) -> tuple[SkillDocument, list[SkillSummary]] | None

@dataclass(frozen=True)
class SkillSummary:   id, original_id, title, description, keywords, url, download_url
class SkillDocument(SkillSummary): content: str | None, references: tuple[SkillReference, ...],
                                   files: tuple[SkillFile, ...], files_reason: str, folder_file_count: int | None
class SkillReference: kind, title, url, node_id, offset
class SkillFile:      id, title, mimetype, size, download_url
class RegistryEntry:  node_id, title, description, keywords, context
class RegistryContext: title, level, path, instruction, skills, range
class SkillRegistry:  collection_id, registry_id, registry_title, markdown, entries,
                      unresolved, contexts, general, ambiguous, truncated, contexts_truncated
RegistryMiss = Literal["collection_not_found", "no_registry", "unreadable"]

# Skills — Ablaufebene (dict, Regeln des Hauses: failed/unresolved/truncated benannt)
async def find_skills(repo, text="", **kwargs) -> dict      # {query, hits, unresolved, truncated}
async def skill(repo, node_id, **kwargs) -> dict            # {…SkillDocument…, files_reason}
async def skill_registry(repo, collection_id, *, context=None) -> dict
#   {collection_id, registry, entries, contexts, general, context_resolution, reason, …}
async def pick_skill(repo, text, **kwargs) -> dict          # {best, alternatives, reason}
```

### Abhängigkeiten

Keine neuen. `flows.text` nimmt den `TextExtraction`-Client als Parameter
entgegen statt ihn zu bauen — die Bibliothek darf keine Adresse kennen (E4).

## Nichtfunktionales

* **Kosten:** `placement` kostet drei Anfragen statt zwei (der Knoten wird
  einmal gelesen). `node.collections()` bleibt bei einer — der Knoten liegt
  schon vor. `update()` an einer Referenz kostet eine Anfrage mehr (das
  Original wird vor dem Schreiben gelesen, weil die Änderungsmenge gegen *sein*
  Ist zu bilden ist, nicht gegen das der Referenz).
* **Sicherheit:** `flows.text` ruft die Extraktion nur für `http(s)`-Adressen
  und lehnt interne Adressen über `agent.safety.check_url` ab — derselbe Schutz,
  den `TextExtraction` schon hat.
* **Rückwärtskompatibilität:** `collections_of(nodes, id)` bleibt gültig;
  `repo` kommt als zweite erlaubte Form dazu. Kein Schlüssel eines Ablaufs
  entfällt.

## Risiken

| Risiko | Gegenmaßnahme |
|---|---|
| `originalId` fehlt auf manchen Referenzen (ältere Instanzen) | Rückfall auf `ccm:original`, **nur** wenn es vom eigenen `id` abweicht; Live-Test hält beide Fälle fest |
| Umleitung beim Schreiben überrascht einen Aufrufer | `redirected_from` am Ergebnis; Falle 5.13 im Skill; `plan_update.describe()` nennt die Umleitung |
| `find.py` teilen bricht Importe | reine Verschiebung, `flows/__init__` und `__all__` zeigen weiter dorthin; Wächter `test_docs_complete` prüft die Namen |
| Dublettenprüfung findet „ähnliche" URLs statt gleiche | exakter Vergleich `ccm:wwwurl == url.strip()` je Treffer, wie im MCP (`duplicates.ts`) |

## Offene Fragen

Entschieden am 02.09.2026 (siehe Kopf): Umleiten mit Ausweis;
`if_exists="return"`; `include_pages=False` als Vorgabe bleibt die Empfehlung
und wird so umgesetzt. Keine offene Frage mehr.

Eine Abweichung, benannt: `WLO_SKILLS` trägt die URIs einer Instanz als
Vorgabe. Das steht neben E4 wie `metadataset="-default-"` — ein Wert, den
jeder Aufrufer ersetzen kann, kein Wert, den die Bibliothek voraussetzt. Ein
anderes Repositorium übergibt seine eigenen `SkillConventions`.

---

## Paket 1 — Referenzen

Schritt 0: `/better-coding-workflow` laden.

### Aufgabe 1.1 — Test: der Knoten kennt sein Original

`tests/test_nodes.py`: ein DTO mit `originalId`, `aspects` und
`ccm:original` → `original_id`, `is_reference`, `aspects`; ein DTO ohne
`originalId`, dessen `ccm:original` auf sich selbst zeigt → `original_id is
None`, `is_reference is False`. Rot: Attribute fehlen.

### Aufgabe 1.2 — `Node.original_id`, `is_reference`, `aspects`

`nodes.py`, drei Properties nach `preview_url`. `original_id` liest
`DTO.originalId`; fehlt es, `ccm:original` nur wenn ≠ `self.id`. Grün.

### Aufgabe 1.3 — Test: `collections_of` fragt das Original

`tests/test_placement.py`: `collections_of(nodes, R)` mit einem gemockten
`GET /node/…/R/metadata` (originalId = O) sendet `GET /usage/…/node/O/…`.
Und: mit `original_id=O` übergeben, **kein** Knotenabruf. Rot.

### Aufgabe 1.4 — Auflösung in `collections_of`, `Node.collections()`, `placement`

`placement.py`: Signatur `(repo_or_nodes, node_id, *, original_id=None)`;
ohne `original_id` wird der Knoten gelesen. `Node.collections()` übergibt
`self.original_id`. `flows.placement` liest den Knoten einmal und gibt
`original_id` mit. Grün; `describe` bekommt `original_id` und `aspects`.

### Aufgabe 1.5 — Test: `update()` an einer Referenz schreibt ans Original

`tests/test_nodes.py`: DTO R mit `originalId=O`; `update(title=…)` sendet
`PUT /node/…/O/metadata`, liest O zurück, das Ergebnis trägt
`redirected_from == R`. Ein Original: keine Umleitung, `redirected_from is
None`. Rot.

### Aufgabe 1.6 — Umleitung in `update()` und `set_property()`

`nodes.py`: Zielkennung `self.original_id or self.id`; vor dem Schreiben das
Original lesen (Änderungsmenge gegen sein Ist); `redirected_from` setzen. Grün.
`delete()` bleibt unverändert; `flows.delete` liefert `is_reference`,
`original_id`.

### Aufgabe 1.7 — `SearchHit.original_id`, `hit_as_dict`

`results.py`, `serialize.py`, ein Test je Datei. Grün.

### Aufgabe 1.8 — Live-Beleg, lesend und schreibend

`tests/test_live_flows.py`: `find_collections` → `collection_contents` → erster
Treffer hat `original_id`; `flows.placement(Listing-ID)["collections"]` ist
nicht leer. `tests/test_live_write.py` (Fixture `ordner`): Knoten und Sammlung
anlegen, hinzufügen, Listing-ID aus `collection_contents`, `update(title=)` an
der Listing-ID → `repo.node(O).title` trägt den Wert, `redirected_from == R`;
`delete()` an R lässt O bestehen.

### Aufgabe 1.9 — Dokumentation

Skill-Paar: Falle 5.13 „Eine ID aus einem Sammlungs-Listing ist eine Referenz".
`FLOWS`-Paar: `placement`, `describe`, `delete`. `REFERENCE`-Paar: die vier
Felder, die zwei Signaturen. `CHANGELOG`: unter `Fixed`.

## Paket 2 — `flows.text`

Schritt 0: `/better-coding-workflow` laden.

### Aufgabe 2.1 — Test: die drei Quellen und die sechs Gründe

`tests/test_flows_text.py`: Repositorium liefert Text → `source="repository"`;
leer + `ccm:wwwurl` + Extraktion → `source="extraction"`, `source_url`; leer,
keine URL → `reason="no_text_no_url"`; leer, URL, `extraction=None` →
`"no_extraction_service"`; Extraktion ohne Text → `"extraction_failed"`;
`404` → `"node_not_found"`; `403`/`500 AccessDenied` → `"access_denied"`.
`max_chars` kürzt an einer Wortgrenze und setzt `truncated`. Rot.

### Aufgabe 2.2 — `flows/text.py`

Reihenfolge wie im MCP: `/textContent` zuerst, Extraktion nur für verlinktes
Material. `check_url` vor dem Extrahieren. Grün.

### Aufgabe 2.3 — Verdrahtung, Sync, Doku, Beispiel 15 verkürzen

`Flows.text`, `SyncFlows.text`; `FLOWS`-Paar Abschnitt `text`; `REFERENCE`;
Skill-Tabelle „Reading one thing"; Beispiel 15 nutzt den Ablauf.

### Aufgabe 2.4 — Live-Beleg

Ein Material mit Repositoriumstext, eines nur verlinkt (Staging, anonym).

## Paket 3 — Schreibseite

Schritt 0: `/better-coding-workflow` laden.

### Aufgabe 3.1 — Test + Ablauf `accept_suggestion`

Vorschlag lesen → `node.set_property(property, value)` → Rückleseprobe → erst
dann `decide([id], accept=True)`; bleibt der Wert aus, bleibt der Vorschlag
offen und `failed` sagt es. Unit-Test mit gemockter Reihenfolge; Live-Test im
Wegwerf-Ordner.

### Aufgabe 3.2 — Test + Dublettenprüfung in `add_material`

Vor dem Anlegen mit `url`: `repo.search(filters={"ccm:wwwurl": url})`,
je Treffer exakter Vergleich der eigenen `ccm:wwwurl`. `if_exists`:
`"return"` (Vorgabe, offene Frage 2), `"raise"` → `ConflictError`, `"create"`.
Ergebnis trägt `existing`.

### Aufgabe 3.3 — Doku und Changelog

## Paket 4 — Suchgleichstand

Schritt 0: `/better-coding-workflow` laden.

### Aufgabe 4.1 — `find.py` teilen

`flows/collections.py` erhält `find_collections`, `search_all`; reine
Verschiebung, Tests grün vor und nach.

### Aufgabe 4.2 — `exclude_ids`, `facet_limit` in `search`

Ausschluss nach der Suche, mit Nachladen bis `limit` voll ist oder der Pool
leer; `facet_limit` durchgereicht. Tests: Ausschluss verringert nie die
Trefferzahl unter `limit`, solange der Pool reicht.

### Aufgabe 4.3 — Filter und `parent_id` für `find_collections`

`**aliases` wie in `search`; `parent_id` als `ccm:parent`-Kriterium? **Zu
messen**: welches Kriterium schränkt die Sammlungssuche auf einen Teilbaum ein
(Aufgabe beginnt mit einer Messung gegen Staging, wie am 28.08.).

### Aufgabe 4.4 — vier Trefferfelder, und jede gewünschte Eigenschaft

`hit_as_dict`, `describe`: `preview_url`, `download_url`, `license`
(`ccm:commonlicense_key`), `size`. Alle liegen im DTO. Dazu `properties=`
an `search`, `search_all`, `collection_contents`, `search_in_collection`: die
genannten Eigenschaften erscheinen unter `fields` mit ihrem vollen Namen —
gemessen verschweigt `collection_contents` heute die Inhaltsart, obwohl das
Listing sie trägt.

### Aufgabe 4.5 — `include_pages` in `search_all`

Dritter Topf über `find_pages`, gleiche `limit`-Regel je Topf.

### Aufgabe 4.6 — Doku, Changelog, Wächter

## Paket 5 — Konsistenz

### Aufgabe 5.1 — Signatur-Wächter für freie Funktionen

`test_docs_complete.py`: Zeilen `` `name(a, b=…)` `` gegen `inspect.signature`
der Funktion aus `__all__` — findet `ancestry_of(repo, …)` sofort. Dann die
Signatur ändern (Aufgabe 1.4) statt die Doku.

### Aufgabe 5.2 — `rerank.py`: `**aliases` nur noch als `filters`

Test: ein Kurzname `limit=` in `search_reranked` überschreibt den Pool nicht.

### Aufgabe 5.3 — die übrigen mypy-Befunde

`repository.py:38` Re-Export, `collections.py` Typargumente,
`contents.py`/`_sync.py` `Any`-Rückgaben. Kein Verhalten ändert sich.

## Paket 6 — Skills

Schritt 0: `/better-coding-workflow` laden.

### Aufgabe 6.1 — `EDU_SHARING_METADATASET`

`from_env()` liest die Variable, wenn kein `metadataset=` übergeben wird;
Vorgabe bleibt `-default-`. Test: gesetzt/ungesetzt/übergeben. Doku: README-
Paar, Skill §2, REFERENCE. Ohne sie findet `from_env()` auf WLO keinen Skill.

### Aufgabe 6.2 — Test + `skills_markdown.py`

Reine Funktionen. `parse_blocks(text, kinds)` → `SkillReference` mit `offset`;
Titel aus dem ersten Nicht-Bild-Link, `**…**` und Backslash-Escapes entfernt
(`Skill\_X` → `Skill_X`); Knoten-ID aus `?nodeId=` oder `/components/render/`;
ein Block ohne Link verweist auf nichts; ein offener Block verschluckt den
Rest, erfindet aber nichts. `parse_sections(text)` → ATX-Überschriften mit
`start`, `body_start`, `end` (gleiche oder höhere Ebene schließt). `layout_
contexts(text, blocks)` → benannte H2/H3 als Kontexte, namenlose transparent,
Anweisung = Prosa bis zum ersten Block, ≤ 50 Kontexte mit `truncated`. Tests
mit dem gemessenen `skill_registry.md`-Aufbau (7 Blöcke, 3 Kontexte) und den
Randfällen aus `registry-contexts.ts`.

### Aufgabe 6.3 — Test + `SkillConventions`, `SkillSummary`, `Skills.search`

Repositoriumsweit: `Search.search(filters={type_property: skill_type},
limit=50, **aliases)` und lokal ranken; Kurznamen, die nicht auflösen, kommen
als `unresolved` zurück (nicht verschluckt). In einer Sammlung: Gang über
`collections.py` mit ausdrücklichem `propertyFilter` für `type_property`, Tiefe
und Breite gedeckelt, `truncated` benannt. Dublette Referenz/Original.

### Aufgabe 6.4 — Test + `Skills.get`

`download()` statt `text()`; Verweise geparst; Begleitdateien über das
Original; `files_reason` ∈ `{"", "no_folder", "folder_unreadable",
"too_many"}`; `PermissionDeniedError` beim Ordner wird zum Grund, nie zum
Fehler des Abrufs.

### Aufgabe 6.5 — Test + `Skills.registry`

Kinder der Sammlung (nie der Index), Kandidat = `registry_type` und Markdown,
Markierung nach `cm:name` oder Titel, Gleichstand → kleinste ID, `ambiguous`;
Blöcke → Einträge, Köpfe mit Pool 10 auflösen (`asyncio.Semaphore`), nicht
lesbare Köpfe → `unresolved`; ≤ 100 mit `truncated`; `context=` liefert den
Kontext **plus** `general`, ein Fehlgriff verengt nie und nennt die
vorhandenen Kontexte. `RegistryMiss` für 404 / kein Kandidat / unlesbar.

### Aufgabe 6.6 — `Skills.pick`, `repo.skills`, synchrone Hülle

### Aufgabe 6.7 — die vier Abläufe

`find_skills`, `skill`, `skill_registry`, `pick_skill` in `flows/skills.py`,
verdrahtet in `Flows` und `SyncFlows`; Ergebnisse als `dict` mit `failed` /
`unresolved` / `truncated`, Markdown unverändert (der Aufrufer rahmt es mit
`as_untrusted`).

### Aufgabe 6.8 — Live-Belege, anonym gegen Staging

`find_skills("Lehrkontext")` ≥ 1 Treffer mit `mds_oeh`; `skill(<id>)` mit
`content` ≥ 1 000 Zeichen und `files_reason == "folder_unreadable"`;
`skill_registry("f35c17d1-a29e-4b26-9d22-802682fad43d")` mit ≥ 1 Eintrag und
≥ 1 Kontext; `-default-` → `ValidationError` mit erklärendem Text.

### Aufgabe 6.9 — Dokumentation und Beispiel

FLOWS-Paar (vier Abschnitte), REFERENCE-Paar (Objekte und Felder — der
Feld-Wächter verlangt sie), Skill-Paar: Zeilen in „Finding things" / „Reading
one thing", Falle 5.14 „Die Inhaltsart ist filterbar, wenn der Metadatensatz
es erlaubt — `-default-` erlaubt es nicht", Beispiel `21_skills.py`:
Registry einer Sammlung lesen, Skill wählen, laden, Begleitdateien nennen.
`CHANGELOG`.

## Verifikation

* `pytest -q` grün, Zahl steigt um die neuen Tests; `ruff`, `mypy` sauber.
* `pytest -m "live and not write"` anonym gegen Staging: der Referenz-Lesetest
  und `flows.text` grün.
* `pytest -m "live and write"` gegen Staging im Wegwerf-Ordner: die Umleitung
  und `accept_suggestion` belegt.
* `test_docs_complete.py`: alle Wächter grün, der neue meldet keine Zeile.
* Abgleichstabelle oben: „mehrere Aufrufe von Hand" von 8 auf 2
  (`get_subject_portals`, `get_related_content` mit Geschwistern — je zwei
  Aufrufe, das ist in Ordnung).
