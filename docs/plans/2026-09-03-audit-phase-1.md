# Audit-Roadmap, Phase 1 — Arbeitsliste (03.09.2026)

Aus [`docs/audits/2026-09-03-audit.md`](../audits/2026-09-03-audit.md), §4 und §9:
die vier Bedingungen des Urteils „bedingt produktionsreif" plus der zweite
High-Korrektheitsbefund. Ein Befund je Commit, Tests zuerst, jeder Commit
hinter dem Gate (ruff, mypy --strict, Gesamtsuite).

Status: `[ ]` offen · `[x]` erledigt · `[-]` bewusst nicht (Begründung).

- [x] **COR-1** — Der Transport wiederholt nicht-idempotente Anfragen nach
  Timeout und 5xx. → `request(..., idempotent=)`: Verbindungsfehler vor dem
  Senden werden für jede Methode wiederholt; Lese-/Schreibfehler und 5xx nur
  für idempotente Anfragen (Vorgabe: GET/HEAD/OPTIONS; `update`,
  `set_property`, ACL- und Bewertungs-Schreibvorgänge markieren sich selbst).
  Docstring wahr machen; Doku, die „dreimal wiederholt" sagt, angleichen.
  Erledigt: 9 Tests (7 Transport, 2 Knoten), Docstrings, README (EN/DE),
  ARCHITECTURE (EN/DE), CHANGELOG. Der b-api-Client behält seine Schleife:
  Modellaufrufe sind zustandslos, eine Wiederholung kostet eine Anfrage,
  keinen doppelten Schreibzugriff (ARC-2, Phase 2).
- [x] **SEC-1** — `https://user:pw@host` wird angenommen und geloggt. →
  `normalize_repository_url` und die drei Geschwister-Prüfungen weisen eine
  Netloc mit `@` ab und nennen `auth=` / `EDU_SHARING_USER`.
  Erledigt: ein Helfer `refuse_userinfo` in `urls.py`, vier Aufrufer, die
  Meldung maskiert das Passwort; 7 Tests; README, Referenz, Skill (EN/DE),
  CHANGELOG.
- [ ] **DOC-1 / DOC-2** — Vier dokumentierte Aufrufe werfen `TypeError`
  (Referenz: `add_material(folder.id, title=…)`, `build_collection("…",
  [ids])`; Skill: `Repository(url, credential=…)`, `BildungsAPI(url, key)`).
  → berichtigen; der Signatur-Wächter bindet jeden dokumentierten Aufruf
  (`inspect.signature().bind`) und prüft Konstruktoren in den Tabellen.
- [ ] **SEC-2** — Downloads ungedeckelt, Markdown-Parser quadratisch. →
  `download(max_bytes=)` mit Größenprüfung vor dem Abruf und Streaming mit
  Kappung; `flows.text`, `skills.get`, Registry melden `too_large`;
  `parse_blocks`/`parse_sections` linear (Zeilenautomat).
- [ ] **COR-2** — `search_in_collection` verschluckt jeden Fehlertyp als
  „unreadable". → Programmfehler werfen; scheitern alle Listen, wirft der
  erste Fehler; sonst `failed: [{id, reason}]` neben `unreadable`.

Danach: Live-Nachlauf gegen Staging (lesend anonym, schreibend mit Login),
Audit-Bericht §4 um den Stand ergänzen.
