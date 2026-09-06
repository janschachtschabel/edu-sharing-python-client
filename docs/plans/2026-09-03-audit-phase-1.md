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
- [x] **DOC-1 / DOC-2** — Vier dokumentierte Aufrufe werfen `TypeError`
  (Referenz: `add_material(folder.id, title=…)`, `build_collection("…",
  [ids])`; Skill: `Repository(url, credential=…)`, `BildungsAPI(url, key)`).
  → berichtigen; der Signatur-Wächter bindet jeden dokumentierten Aufruf
  (`inspect.signature().bind`) und prüft Konstruktoren in den Tabellen.
  Erledigt: `_bindet_nicht` mit `bind_partial` und Platzhaltern in allen drei
  Wächtern (Repository-, freie, Konstruktor-Aufrufe), Selbsttest mit den vier
  Fällen; Referenz (EN/DE), Skill (EN/DE), CHANGELOG.
- [x] **SEC-2** — Downloads ungedeckelt, Markdown-Parser quadratisch. →
  `download(max_bytes=)` mit Größenprüfung vor dem Abruf und Streaming mit
  Kappung; `flows.text`, `skills.get`, Registry melden `too_large`;
  `parse_blocks`/`parse_sections` linear (Zeilenautomat).
  Erledigt in zwei Commits (06.09.2026): Parser als Zeilenautomaten mit
  Pin- und Leistungstest; `Transport.download` (Streaming, Content-Length
  vor dem ersten Byte, Zählung danach), `NodeContent.download(max_bytes=)`
  mit Größenprüfung vor dem Abruf, `ContentTooLargeError`, `MAX_TEXT_BYTES`,
  `too_large` in Textablauf, `skills.get` und Registry; 10 Tests; Referenz,
  FLOWS, Skill (EN/DE), CHANGELOG.
- [x] **COR-2** — `search_in_collection` verschluckt jeden Fehlertyp als
  „unreadable". → Programmfehler werfen; scheitern alle Listen, wirft der
  erste Fehler; sonst `failed: [{id, reason}]` neben `unreadable`.
  Erledigt: `_refused` in `flows/tree.py`, 3 Tests + Zusatzprüfung, Docstring,
  FLOWS (EN/DE), Referenz (EN/DE), CHANGELOG.

Danach: Live-Nachlauf gegen Staging (lesend anonym, schreibend mit Login),
Audit-Bericht §4 um den Stand ergänzen.

**Erledigt (06.09.2026).** Live-Nachlauf: lesend anonym 43 bestanden / 63
übersprungen; lesend angemeldet 72 bestanden / 34 übersprungen, nachdem ein
veralteter `search_all`-Test berichtigt war (Kurznamen erreichen seit dem
02.09. den Sammlungskorb, nur rohe `filters` werden als ignoriert genannt);
schreibend 79 bestanden in eigenen Wegwerf-Ordnern. CI grün auf jedem Commit.
Audit-Bericht §4 trägt den Stand. Weiter mit Phase 2 der Roadmap (§9).

## Review-Nachlese (06.09.2026)

Ein frischer Review-Durchgang über den Phase-1-Diff: 3 MAJOR, 5 MINOR,
9 NIT. Jeder Befund am Quelltext geprüft.

- [x] **F1 MAJOR** Schema-Tippfehler (`https:/user:pw@host`, `ftp://…`)
  umgingen SEC-1 → `refuse_userinfo` liest die Autorität selbst, nur http(s)
  wird ergänzt, `mask_userinfo` in jeder Meldung.
- [x] **F2 MAJOR** `download()` verlor alle Wiederholungen → läuft durch
  `request(max_bytes=)`; `_send` streamt und deckelt, Fehlerseiten bei 64 KiB.
- [x] **F3 MAJOR** Sync-Fläche ohne `download(max_bytes=)`/`raw.download` →
  beides durchgereicht, gepinnt.
- [x] **F4 MINOR** Vorenthaltener 5xx bei einem Schreibvorgang → Notiz am
  Fehler (nicht wiederholt, Verdacht Login-Ausrutscher, zurücklesen).
- [x] **F5 MINOR** Reine Zustands-Schreibvorgänge unmarkiert → `comments.edit`
  und `set_preview` markiert. Bewusst nicht: Vorschlags-Status (PATCH),
  Gruppenmitgliedschaft (PUT), Beziehung bestätigen (POST) — die Antwort
  des Repositoriums auf eine Wiederholung ist nicht gemessen.
- [x] **F6 MINOR** Markierte Stellen ohne Test → je ein Abbruch-Test.
- [x] **F7 MINOR** Vorabprüfung nicht bewiesen → Körper zählt, ob er gezogen
  wurde.
- [x] **F8 MINOR** Schemalose Form und Maskierung ungetestet → Tests.
- [x] **F9/F10/F11 NIT** ASCII-Ziffern, Fehlerseiten-Grenze, `credential=`.
- [-] **F12 NIT** Wandzeit-Assertion (< 3 s bei gemessenen 0,08 s): bleibt;
  ein Zählwerk brächte mehr Code als Sicherheit.
- [-] **F13 NIT** `_BEZEICHNER` nur Kleinbuchstaben: die Bibliothek hat keine
  camelCase-Parameter; bleibt.
- [x] **F14/F15/F16/F17 NIT** Docstring `splitlines`, CHANGELOG (BOM),
  Wortlaut „Verweigerung" → „Antwort des Repositoriums", `MAX_TEXT_BYTES`
  aus dem Paket exportiert.
