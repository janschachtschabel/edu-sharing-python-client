# Plan: die Befunde aus dem Skill-Review beheben

## Ziel

Die Befunde des Reviews vom 11.09.2026 (gegen `c6a796c`) beheben, die Wachen so
erweitern, dass dieselben Fehlerarten künftig rot werden, und das mit einem
zweiten Abnahmelauf messen. Auftrag des Nutzers: „ja bitte“ auf den Vorschlag
MAJOR zuerst, dann die Wachen, der Bibliotheksfix als eigener Commit, danach
ein zweiter Abnahmelauf mit einem frischen Agenten.

## Befunde

| # | Stufe | Befund | Beleg |
|---|---|---|---|
| 1 | MAJOR | Kurznamen an Eigenschaftspositionen: `facets=["subject"]` auf API-Ebene (SKILL:98, REFERENCE:202), `vocab.resolve_all("subject", …)` (TRAPS:98) | live: 400 *Widget subject was not found* |
| 2 | MAJOR | `workflow.submit(…, "TO_BE_CHECKED")` (SKILL:201, REFERENCE:591) | README:766, workflow.py:18 — WLO: `100_tocheck` |
| 3 | MAJOR | blockierend: `repo.nodes.wrap()` gibt den asynchronen `Node`, `repo.raw.is_repository_url` fehlt, `isinstance(repo.collections, Collections)` | offline geprüft |
| 4 | MAJOR | Metadatenset `-default-` ungenannt | live: 2826 statt 18006 Treffer |
| 5 | MAJOR | `text()` leer für Markdown/JSON, nicht im Einstieg | content.py:298 |
| 6 | MAJOR | `update_material(keywords=…)` ersetzt die gemeinsame Liste | curate.py:278 |
| 7 | MINOR | optionale Parameter ohne Doku; Legende „all in REFERENCE.md“ | Inventar: 26 nirgends |
| 8 | MINOR | `RELATION_TYPES` fehlt; Wache sieht `ast.AnnAssign` nicht | test_docs_complete.py:76 |
| 9 | MINOR | Verweise aufs README; Wissen nur dort (Logging, halbe Schreibvorgänge) | REFERENCE:146, :506 |
| 10 | MINOR | `SearchResult.ignored`/`.suggestions` fehlen | REFERENCE:193 |
| 11 | MINOR | Endmarke von `as_untrusted` falsch | REFERENCE:1456 |
| 12 | MINOR | `exc.dropped` als dict | TRAPS:159 |
| 13 | MINOR | Zusage SKILL:14 zu weit; Gruppen-Schreibaufrufe ungeprüft, Verwaltungsrecht | people.py:24 |
| 14 | MINOR | „members defaults to 10“ | people.py:49 |
| 15 | MINOR | `ValidationError` „before it is sent“ | live: 400 vom Server |
| 16 | MINOR | Kindobjekt „empty title“ | nodes.py:79 |
| 17 | MINOR | „0 gegen 43“ ohne Halbsatz | ranking.py:80 |
| 18 | MINOR | „takes the connection as its first argument“ | REFERENCE:744 |
| 19–22 | NIT | `redirected_from`; `SyncNodePage` doppelt; `**filters`; Fehlerattribute | — |
| 23 | NIT | Aufrufzeilen der Beispiele nennen `docs/examples/` | bleibt: im Repo richtig, die Kopien müssen byte-gleich bleiben |

## Pakete

Jedes Paket beginnt mit `/better-coding-workflow`; vor jedem Commit das Gate
(`ruff check .`, `mypy --strict src/edusharing`, `pytest -q`), dann Push und CI.
Doku-Änderungen gehen nach `docs/` und werden mit `scripts/sync_skill.py` in den
Skill kopiert; SKILL und TRAPS liegen nur im Skill. Immer beide Sprachen.

1. **Bibliothek** (eigener Commit). Test zuerst: der Wächter in
   `test_sync_surface.py` ruft auch die einfachen Methoden und prüft, ob ein
   Ergebnis asynchrone Methoden trägt; `repo.nodes`, `collections`, `searcher`,
   `vocab` kommen in seine Paare. Rot mit `Nodes.wrap` und
   `Transport.is_repository_url`. Dann `SyncNodes.wrap` → `SyncNode`,
   `SyncTransport.is_repository_url`. CHANGELOG.
2. **Wachen für 1 und 2, dann die Doku.** Neue Wache: Eigenschaftspositionen
   (`facets=`, `filters=`-Schlüssel, `properties=`-Schlüssel, erstes Argument
   von `vocab.*`/`resolve*`/`labels`/`get_all`/`set_property`/`propose`) tragen
   den vollen Namen — außer unter `flows`; in Codeblöcken und in parsebarem
   Inline-Code; mit Gegenprobe. Workflow-Status in der Doku = der gemessene.
3. **MAJOR 3–6** in der Doku. 5 vorher live nachmessen, im eigenen
   Wegwerf-Ordner (danach `delete(recycle=False)`); dabei auch `cm:title` an
   einem neuen Ordner und `rename_if_exists` für Paket 5 und 4.
4. **Wache „jede Option steht bei ihrer Methode“** (REFERENCE oder FLOWS) und
   `ast.AnnAssign` in der Vollständigkeitswache; die Doku ergänzen (7, 8).
5. **MINOR 9–18, NIT 19–22.**
6. **CHANGELOG, Nachtrag hier; zweiter Abnahmelauf** mit einem frischen Agenten
   und Aufgaben aus den Befund-Bereichen (Facetten, Vokabular, Workflow,
   private Markdown-Datei, Schlagworte über den Flow, blockierendes `wrap`).

---

## Umsetzung (11./12.09.2026)

Sechs Commits, jeder nach dem Gate und direkt gepusht, CI je grün:
`1530191` Bibliothek · `81e4c58` Plan · `4662ba2` Kurznamen und Status ·
`5ce12b3` Metadatenset, Markdown, Schlagworte · `8d5f538` Optionen und
`RELATION_TYPES` · `eab9340` die kleineren Befunde.

### Abweichungen vom Plan, mit Grund

| Plan | Umgesetzt | Grund |
|---|---|---|
| Befund 3 in der Doku als „nur async" kennzeichnen | in der Bibliothek behoben: `SyncNodes.wrap` → `SyncNode`, `SyncTransport.is_repository_url` reicht durch | der Wrapper macht die Doku wahr, statt eine Ausnahme zu erklären; `is_repository_url` antwortet ohne I/O, der Docstring „deliberately narrow" ist entsprechend ergänzt |
| Wache für Eigenschaftspositionen in `test_docs_code.py` | eigene Datei `tests/test_docs_values.py` | die bestehende Datei fragt nach Signaturen, diese nach Werten — und sie war schon an der Größenschwelle |
| Wache „jede Option" als Teil derselben | eigene Datei `tests/test_docs_options.py` | dieselbe Trennung; dazu eine kleine Tabelle `AUCH_ALS` für Fassaden (`create_node` für `Nodes.create`) |
| Befund 23 beheben | bleibt | die Aufrufzeilen der Beispiele stimmen im Repo, und die Kopien müssen byte-gleich bleiben |

### Zweiter Abnahmelauf

Frischer Agent, Modell sonnet, eingefrorene Kopie des Skills außerhalb des
Repos, acht Aufgaben aus genau den Befund-Bereichen; gelesen nur der
Skill-Ordner, nichts ausgeführt.

| | Ergebnis |
|---|---|
| statisch (Bindung, Attribute, `await`) | **8 von 8** sauber — 48 Aufrufe gebunden, 147 Attribute geprüft |
| Werte-Wache (Kurzname an Eigenschaftsposition, Status) | **8 von 8** sauber |
| live gegen Staging, lesend | **3 von 3** mit Exitcode 0 (Facetten 838 Treffer zu „Optik", beide `Biologie`-URIs, 18006 zu „Physik") |
| Sicherheit | 5/5 für r3, r5, r6; 4/5 für r1, r4, r7, r8; 3/5 für r2 |

Jede berichtigte Stelle wurde benutzt: Facetten über den Flow mit Kurznamen,
`resolve_all` mit `ccm:taxonid`, `metadataset="mds_oeh"` samt Prüfung gegen
`-default-`, der Markdown-Weg (leerer `text()`, 403 privat, veröffentlichen),
die Vereinigung der Schlagworte vor `update_material`, `100_tocheck`,
`repo.nodes.wrap` blockierend, `only="folders"` mit `sort`.

Was der Agent noch raten musste, ist Deutung der Aufgabe statt Lücke im Skill —
mit einer Ausnahme: der Mimetype für Markdown stand nirgends. Gemessen und
nachgetragen (`text/markdown`, `application/json`).

### Offen

- Befund 23 (siehe oben).
- Die schreibenden Aufgaben des zweiten Laufs (r4–r8) sind nur statisch
  geprüft, wie im ersten Lauf.
