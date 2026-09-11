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
