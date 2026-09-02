# Review-Befunde vom 02.09.2026 — Arbeitsliste

Drei Prüfungen mit leerem Kontext, nur lesend, über die sechs Pakete des Tages
(Referenzen, `flows.text`, Schreibseite, Suchgleichstand, Konsistenz, Skills)
und die Teilung von `nodes.py`. Jeder Befund wurde vor der Umsetzung gegen den
Quelltext verifiziert; was sich nicht bestätigte oder bewusst bleibt, steht
mit Begründung hier. Reihenfolge: Korrektheit vor Tests vor Doku, ein Bereich
je Commit.

Status: `[ ]` offen · `[x]` erledigt · `[-]` bewusst nicht (Begründung).

## A — Skills (`skills.py`, `skills_registry.py`, `skills_markdown.py`, `flows/skills.py`)

- [x] A1 MAJOR — Blockart `ki-skill` steht wörtlich in `load_registry` und
  `layout_contexts`, obwohl `SkillConventions.block_kinds` der Parameter ist.
  → `SkillConventions.skill_kind` (Vorgabe `ki-skill`), `layout_contexts(..., skill_kind=)`.
- [x] A2 MAJOR — Kurznamen werden in `Skills.search` über `resolve_vocabulary`
  auf EINE URI aufgelöst; `repo.search` nimmt alle URIs eines Labels
  (`resolve_all`). Gleiches Muster in `find_collections` (C4). → ein
  Lese-Resolver mit allen Werten je Label.
- [x] A3 MAJOR — `_walk`: ein 403/404 einer Untersammlung wirft die ganze Suche
  (Präzedenz A10 in `flows/tree.py`). → je Untersammlung fangen, zählen
  (`SkillSearch.unreadable`), weiterlaufen; Fehler der Wurzel bleibt ein Fehler.
- [ ] A4 MAJOR — Der Sammlungszweig (`_walk`, `_is`, `_carries`, Tiefe, Besuchs-
  grenze, `truncated`) ist ungetestet; ebenso `resolve=False`, `REGISTRY_MAX`,
  `scan_truncated`, `reason="unreadable"`, Block ohne ID, `no_folder`, eigene
  `block_kinds`. → Tests.
- [x] A5 MINOR — Untersammlungen jenseits der Listenseite (50) fallen ohne
  `truncated` weg. → `pagination.total` prüfen.
- [x] A6 MINOR — `_bundle` fängt nur 403; ein 404 des Ordners wirft nach dem
  Download. → auch `NotFoundError` → `files_reason="no_folder"`.
- [x] A7 MINOR — `except EduSharingError` in `load_registry`/`_read_heads`
  macht Transport-/Serverfehler zu „unreadable"/„unresolved". → auf
  `NotFoundError | PermissionDeniedError` verengen, Rest wirft.
- [x] A8 MINOR — Ein zweimal genannter Skill wird zweimal gelesen. → IDs
  entdoppeln, zurück abbilden.
- [x] A9 MINOR — Im Sammlungszweig sortiert `text` nur, filtert nicht; die
  Docstrings von `search`/`pick` versprechen Treffer. → lokal ohne Treffer
  (Score 0) aussortieren, wenn Suchbegriffe vorliegen; Docstrings anpassen.
- [x] A10 MINOR — `parse_blocks` ignoriert Code-Zäune (ein gezeigtes Beispiel
  wird zum Verweis) und `kinds=()` fängt jedes `:::`-Paar. → Zaunspannen
  maskieren; leere `kinds` → `[]`.
- [x] A11 MINOR — `Skills.get` dekodiert ohne BOM-Behandlung und ohne
  Mimetype-Blick (Binärdatei → Zeichensalat). → `utf-8-sig`; Nicht-Text →
  `content=None` mit `content_reason`.
- [x] A12 MINOR — Prosa unter unbenanntem `###` in einem benannten `##`
  landet in keiner `instruction`; H4+ schneidet die Prosa ab. → Prosa
  unbenannter Unterabschnitte dem Besitzer anhängen; H4+ schneidet nicht.
- [x] A13 NIT — `_document` rechnet `asdict` doppelt; `range` wird stumm
  verworfen. → `asdict(doc)`; `range` mit Kommentar entfernen.
- [x] A14 NIT — `pick(text, include_files=False)` wirft. → `include_files`
  durchreichen.
- [x] A15 NIT (teils) — Kommentar an `registry_mark` falsch; `SKILL_DEPTH_MAX` fehlt
  in `__all__`; `SyncSkills` fehlt in `_sync.__all__`; Registry-Knoten wird
  nach dem Listing erneut gelesen; Fassaden-Docstring behauptet „kein
  `**kwargs`"; Beispiel 21 behauptet, `mds_oeh` sei für die Registry nötig.
  Bleibt: der zweite Lesezugriff auf den Registry-Knoten — `download()`
  braucht `downloadUrl` und `content` aus dem Datensatz, die ein Listing
  nicht auf jeder Instanz trägt; eine Anfrage ist der Preis der Sicherheit.
  Fassade, `_sync.__all__` und Beispiel 21 folgen im Doku-Commit.

## C — Suche, Konfiguration, Sync (`flows/find.py`, `flows/collections.py`, `flows/serialize.py`, `_sync.py`, Wächter)

- [x] C1 MAJOR — `search`: `ask = min(limit + len(excluded), EXCLUSION_MAX)`
  kappt JEDE Anfrage auf 200 (auch `limit=250` ohne Ausschlüsse) und meldet
  einen nicht auffüllbaren Rest nicht. → `ask = limit + min(len(excluded), MAX)`;
  Warnungen bei Überschuss und bei kurzer Seite; unter `rerank` `pool` anheben.
- [x] C2 MAJOR — `search_all(include_pages=True)`: `find_pages` läuft außerhalb
  der Ausfallbehandlung — ein 503 der Sammlungsrouten wirft und verliert die
  Materialtreffer (Audit A9, wieder eingebaut). → in denselben `gather`.
- [x] C3 MAJOR — `find_collections`: Kurznamen-Filter werden NACH dem
  Server-Schnitt bei `limit` angewandt; `total` bleibt die ungefilterte Zahl.
  → mit Filter mehr holen (gekappt), `total=len(kept)` als Untergrenze,
  Warnung mit der Zahl der beurteilten Kandidaten.
- [x] C4 MAJOR — `resolve_vocabulary` löst nur die erste URI auf (siehe A2).
- [x] C5 MAJOR — Der Ausfall-Eimer von `search_all` hat andere Schlüssel als
  der Erfolgs-Eimer (`unjudged`, `query.filters`, `query.parent_id` fehlen).
  → eine `_empty`-Form für beide Wege; Test auf gleiche Schlüsselmenge.
- [ ] C6 MINOR — `SyncFlows.find_collections(text)` ohne Vorgabe, asynchron
  `text=""`. → Vorgabe; Reflexions-Wächter für Signaturen Async ↔ Sync.
- [x] C7 MINOR — `_below` baut `SearchHit` ohne `raw`; mit `parent_id` UND
  Kurzname ist jeder Treffer `unjudged`. → Rohdaten aus `browse_tree`
  mitführen, `SearchHit.from_node`.
- [x] C8 MINOR — `browse_tree` ignoriert `pagination.total` (>50
  Untersammlungen fallen stumm weg). → `truncated=True`.
- [x] C9 MINOR — `_below`: ein `text` nur aus Stoppwörtern ergibt `terms=[]`
  → alles passt. → Teilstring-Rückfall oder Warnung.
- [x] C10 MINOR — `hit_as_dict`: `list(values)` zerlegt einen String in
  Zeichen, ein `int` wirft. → Liste erzwingen.
- [x] C11 MINOR (teils) — `find_pages` läuft sequenziell nach dem `gather` und sendet
  dieselben zwei Sammlungsanfragen erneut. → in den `gather` (mit C2).
  Bleibt: die zwei Sammlungsanfragen werden weiterhin doppelt gesendet —
  parallel, nicht mehr nacheinander; sie aus dem Sammlungskorb abzuleiten
  hieße `find_pages` umzubauen, ein eigener Schritt.
- [x] C12 MINOR — (a) `search_all` reicht `**aliases` nicht an
  `find_collections` durch, meldet sie aber als `filters_ignored`; (b)
  `_carries` doppelt (`collections.py`, `skills.py`); (c) `query.filters` hat
  zwei Formen. → (a) prüfen und angleichen, (b) eine Fassung, (c) die Worte
  des Aufrufers in beiden.
- [ ] C13 MINOR — Test-Lücken: `Repository.from_env` mit `EDU_SHARING_METADATASET`,
  `SyncSkills` in `test_sync_surface.py`, tote Alternativen in
  `test_flows_search_more.py:80`, plus die Fälle aus C1/C2/C3/C7.
- [ ] C14 MINOR — Wächter-Lücken: `repo.flows.x(...)` (57 Aufrufe) entgeht dem
  Signatur-Wächter; Schlüssel-Wächter überspringt Abläufe, die einen Helfer
  zurückgeben; `_sync.__all__` nennt 7 von 14 Klassen.
- [ ] C15 MINOR — Falsche Aussagen: FLOWS „`find.find_collections`" (liegt in
  `flows.collections`); „`total_is_lower_bound` immer wahr" (mit `parent_id`
  nicht); Fassaden-Docstring zu `**kwargs`; Trefferbeispiel ohne die vier
  neuen Felder.

## B — Referenzen und Schreibpfad (`nodes.py`, `nodes_write.py`, `flows/curate.py`, `flows/suggest.py`, `flows/duplicates.py`, `flows/text.py`, `flows/describe.py`)

Die Teilung selbst ist verhaltensgleich (Zeile für Zeile gegen `f8f8b0a~1`
geprüft); die Befunde betreffen Verhalten, das schon vorher so war.

- [x] B1 MAJOR — `Nodes.create` prüft `cm:name` mit nach; bei einer
  Namenskollision, die `renameIfExists` mit Zähler löst, fliegt
  `SilentDropError` mit falscher Diagnose. Jeder Wiederholungslauf von
  `add_material` mit gleichem Titel im selben Ordner scheitert. → `cm:name`
  aus der Probe nehmen; der gespeicherte Name ist `node.name`.
- [x] B2 MAJOR — `accept_suggestion` schreibt den Vorschlag mit
  `set_property`, das die GANZE Liste ersetzt: ein Schlagwort-Vorschlag
  löscht alle anderen Schlagwörter. → Schlagwörter zusammenführen
  (`add_keywords`); sonst ersetzen und die ersetzten Werte nennen
  (`replaced`).
- [x] B3 MAJOR — `set_property(None)` liest nach, prüft aber nicht: eine
  Instanz, die 200 sagt und die Eigenschaft behält, gilt als gelöscht. →
  `SilentDropError`, wenn die Eigenschaft noch da ist.
- [x] B4 MINOR — Mit `verify=False` geht ein Schreibvorgang über eine Referenz
  ans Original, zurück kommt aber die Referenz ohne `redirected_from`; ein
  Fehler des Originals nennt eine URL, die der Aufrufer nie hatte. → bei
  Umleitung trotzdem lesen (nur die Probe entfällt); Fehlern eine Notiz
  anhängen.
- [x] B5 MINOR — `find_by_url` sieht `result.unresolved` nicht an: eine Adresse
  ohne `http(s)://` wird nicht gesendet, 20 ungefilterte Treffer verglichen,
  „kein Duplikat" gemeldet. → `ValidationError`, damit `check_before_create`
  warnt bzw. verweigert.
- [x] B6 MINOR — `decide()` steht in `accept_suggestion` außerhalb des `try`:
  scheitert das Markieren nach dem Schreiben, geht das Ergebnis verloren.
  → fangen, `failed`-Teil `mark`, Antwort sagt, dass der Wert geschrieben ist.
- [x] B7 MINOR — `update_material` verschweigt die Umleitung (Antwort trägt die
  ID des Originals, nicht die übergebene). → `redirected_from` in Antwort
  und Doku.
- [x] B8 MINOR — `placement` fängt `BaseException`. → nur `EduSharingError`,
  alles andere wirft.
- [x] B9 MINOR — `flows.text`: JSON hat Text, fällt aber nicht auf `download`
  zurück; `text()`/`download()` ungeschützt (5xx wirft aus einem Ablauf,
  dessen Vertrag „kein Text ist eine Antwort" ist). → JSON in den Rückfall;
  fangen, Grund `repository_failed` mit `detail`.
- [ ] B10 MINOR — FLOWS: `placement` „2 Anfragen, nicht drei" (es sind drei),
  `accept_suggestion` „vier" (sechs), `add_material` „2–4" ohne
  Adressprüfung, doppelter „Behind it"-Block. Beide Sprachen.
- [ ] B11 MINOR — Tests: `set_property(None)` bei behaltener Eigenschaft;
  `verify=False` über Referenz; `create` mit Umbenennung; `placement` mit
  scheiterndem Knotenlesen; `flows.delete` an einer Referenz;
  `accept_suggestion` an Referenz und mit scheiterndem `decide`;
  `check_before_create` mit ungültigem `if_exists`.
- [x] B12 NIT — `if_exists` wird nur mit `url` geprüft. → immer prüfen.
- [x] B13 NIT — `describe`-Docstring ohne die vier Trefferfelder; „sechs
  Gründe" bei fünf Codes.
- [-] B14 NIT — Drei Anfragen in `placement` sind der richtige Kompromiss
  (`/parents` scheitert bei fremdem Material in 18 von 20 Fällen); keine
  Änderung.
- [x] B15 NIT — `update(node, properties, verify, aliases)` positional;
  `route` als freier String. → keyword-only, `Literal`. `__all__` bleibt
  (interne Helfer; das Modul sagt es).

## Verifikation je Commit

`pytest -q` grün (Zahl steigt um die neuen Tests), `ruff check .`,
`mypy --strict src`, die Doku-Wächter; wo ein Befund eine Messung braucht,
steht sie am Befund.
