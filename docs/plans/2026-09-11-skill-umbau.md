# Design: Der Skill wird ein Nutzungsleitfaden

## Ziel

Das LLM eines Nutzers kann **ohne Vorkenntnisse jede Option der Bibliothek**
nutzen — mit dem Skill allein, auch außerhalb dieses Repositoriums.

## Kontext

Gemessen am 11.09.2026 an `.claude/skills/edu-sharing-python/SKILL.md`:

| Befund | Wert |
|---|---|
| Länge | 940 Zeilen (Anthropic empfiehlt unter 500) |
| „Which call answers which question“ | 314 Zeilen, **kein** Codeblock |
| Oberfläche | 370 Namen, keine Signaturen, keine Rückgabeformen |
| Details | verwiesen auf `../../../docs/REFERENCE.md` — außerhalb des Repos tot |
| Fallen und Datenmodell | 434 Zeilen (46 %) |
| Python-Beispiele | 17, die meisten zu Fallen |

Das README nennt ihn selbst eine „Wegweisertabelle“. Ein LLM erfährt, *welcher*
Aufruf passt, aber nicht, *wie* man ihn aufruft — es rät Signaturen.

### Zweiter Durchgang: bildet der Skill alle Features ab, und vermittelt er sie?

Gemessen am 11.09.2026 gegen die 370 öffentlichen Namen (dieselbe Menge, die
`test_docs_complete` bewacht), je Name die beste Stufe im Skill:

| Stufe | SKILL.md | SKILL.de.md | heißt |
|---|---|---|---|
| in einem Python-Block | 48 (12 %) | 44 (11 %) | vorgemacht |
| als `name(…)` mit Argumenten | 108 (29 %) | 109 (29 %) | Aufruf gezeigt |
| nur als `.name()` ohne Argumente | 42 (11 %) | 45 (12 %) | Form offen |
| nur genannt, ohne Klammern | 172 (46 %) | 172 (46 %) | Existenz belegt |
| fehlt | 0 | 0 | — |

**Abbilden: ja.** Kein Name fehlt — das halten die Wächter.
**Vermitteln: zur Hälfte.** Von den 119 öffentlichen **Methoden** zeigt der
Skill bei 46 keinen Aufruf mit Argumenten. Bei 15 davon haben die Methoden
Pflichtparameter, die im Skill nirgends stehen — hier muss ein Modell raten:

| Klasse | Methoden ohne gezeigten Pflichtaufruf |
|---|---|
| `People` | `delete_group(name)`, `remove_member(group, authority)` |
| `BapiTemplates` | `images_limited(configs, context_node_id)`, `respond_limited(configs, context_node_id)` |
| `Transport` | `is_repository_url(url)`, `json(method, path)` |
| `Ace` | `allows(permission)` |
| `MetadataAgent` | `content_type_for(uri)` |
| `AsyncRepository` | `create_collection(title)` |
| `Comments` | `edit(comment_id, text)` |
| `SearchHit` | `from_node(repository_url)` |
| `Model` | `is_retired_on(day)` |
| `Relations` | `of(node_id)` |
| `Skills` | `pick(text)` |
| `Collections` | `remove(collection_id, node_id)` |
| `NodeContent` | `set_preview(data)` |
| `Node` | `set_property(prop, value)` |
| `Repository` | `update_collection(collection_id)` |

Die anderen 31 haben keine Pflichtparameter, aber der Skill sagt nicht, was
zurückkommt (`whoami`, `about`, `download`, `history`, `publish`, `load`, …).

Dieselbe Messung gegen `docs/REFERENCE.md`: **0** Methoden mit ungezeigten
Pflichtparametern, 19 ohne Argumente (alle ohne Pflichtparameter). Die Referenz
schließt die Lücke also vollständig — sie muss nur *mit dem Skill mitkommen*,
und der Skill muss die häufigen Aufrufe selbst zeigen. Beides ist der Ansatz
unten.

Wo die 172 nur genannten Namen hingehören: Konstanten (`SKILL_BUNDLE_MAX`,
`DEFAULT_MAX_TOKENS`, …) und Datenklassen (`Swimlane`, `Ace`, `Model`, …)
brauchen keinen Aufruf, aber ihre **Felder** — die stehen in der Referenz, im
Skill nur für einen Teil. Die elf Fehlerklassen stehen ohne Hierarchie da;
`error_class_for` und `error_from_response` ohne Zweck.

**Rahmen aus den Quellen** (abgerufen am 11.09.2026):

| Ziel | Ort / Regel | Quelle |
|---|---|---|
| Claude Code | `~/.claude/skills/<name>/SKILL.md` (persönlich), `<projekt>/.claude/skills/<name>/SKILL.md` | code.claude.com/docs/en/skills |
| OpenAI Codex | `~/.agents/skills/<name>/`, `<repo>/.agents/skills/<name>/`; Aufruf `$name` oder implizit | learn.chatgpt.com/docs/build-skills |
| claude.ai | ZIP, Skill-Ordner als Wurzel, `description` ≤ **200** Zeichen, `name` ≤ 64 | support.claude.com, Artikel 12512198 |
| Frontmatter allgemein | `name` ≤ 64, nur a–z, 0–9, `-`, nicht „anthropic“/„claude“; `description` ≤ 1024, keine XML-Tags | platform.claude.com, Agent Skills |
| Aufbau | SKILL.md < 500 Zeilen; Verweise **eine Ebene** tief; ab 100 Zeilen Inhaltsverzeichnis; konkrete Beispiele; mit Auswertungen entwickeln | platform.claude.com, Best practices |

## Entscheidungen (vom Nutzer, 11.09.2026)

1. **Einstieg + Nachschlagedateien** im Skill-Ordner.
2. **Alles zweisprachig** — Einstieg und Nachschlagedateien.
3. **Verteilung nur per Hinweis** in README und Doku: wohin bei Claude Code
   und bei OpenAI Codex, und eine ZIP-Fassung für Uploads.
4. **Abnahme mit einem frischen Agenten.**

## Ansatz für die Nachschlagedateien

| | Wie | Dafür | Dagegen |
|---|---|---|---|
| **A · Kopien der Doku, synchron gehalten** | ein Skript kopiert `docs/REFERENCE*.md`, `docs/FLOWS*.md`, `docs/examples/*.py` nach `reference/`; ein Test verlangt Gleichheit | eine Quelle; vollständig, weil REFERENCE schon bewacht ist (jeder Name, jedes Feld, Signaturen); Verweise bleiben gültig, weil die relative Struktur gleich bleibt | Dateien liegen doppelt im Repo |
| B · eigene Nachschlagedateien je Bereich | neu geschrieben | zugeschnitten | zweite Wahrheit, driftet; doppelter Schreibaufwand in zwei Sprachen |
| C · Verweise auf GitHub | URLs statt Dateien | nichts doppelt | tot ohne Netz — und die Sandbox von claude.ai/API hat oft keins |

**Gewählt: A.** Neu geschrieben werden nur der Einstieg (zwei Sprachen) und
ein Inhaltsverzeichnis für REFERENCE und FLOWS.

## Umfang

Drin:
- `SKILL.md` neu als Nutzungsleitfaden (< 500 Zeilen), `SKILL.de.md` als
  deutsche Fassung
- `reference/` im Skill-Ordner: Kopien von REFERENCE, FLOWS (je zwei
  Sprachen) und aller Beispiele; `TRAPS.md`/`TRAPS.de.md` mit Datenmodell und
  Fallen aus dem alten Skill (verschoben, nicht neu)
- Inhaltsverzeichnis in `docs/REFERENCE*.md` und `docs/FLOWS*.md`
- `scripts/sync_skill.py`, `scripts/build_skill_zip.py`
- eine Signaturwache für Aufrufe an `node`, `templates`, `api`, … in Codeblöcken
- README (beide Sprachen): Installation für Claude Code, Codex, claude.ai-ZIP;
  Hinweis in der Doku
- Abnahme: Auswertung mit einem frischen Agenten, vorher gegen den alten Skill

Nicht drin:
- Paketierung des Skills ins Wheel oder ein Installationsbefehl (Entscheidung 3)
- ein Upload nach claude.ai durch mich — die ZIP wird gebaut und geprüft, der
  Upload ist Sache des Nutzers
- Änderungen an der Bibliothek selbst

## Architektur

### Dateien

```
.claude/skills/edu-sharing-python/
├── SKILL.md              neu, englisch, < 500 Zeilen, mit Frontmatter
├── SKILL.de.md           neu, deutsch, ohne Frontmatter (Begleitdatei)
└── reference/
    ├── REFERENCE.md      Kopie von docs/REFERENCE.md
    ├── REFERENCE.de.md   Kopie von docs/REFERENCE.de.md
    ├── FLOWS.md          Kopie von docs/FLOWS.md
    ├── FLOWS.de.md       Kopie von docs/FLOWS.de.md
    ├── TRAPS.md          Datenmodell + Fallen (aus SKILL.md, Abschnitte 4–5)
    ├── TRAPS.de.md       dasselbe aus SKILL.de.md
    └── examples/         Kopie von docs/examples/*.py
scripts/sync_skill.py         kopiert; --check meldet Abweichungen (Exit 1)
scripts/build_skill_zip.py    baut dist/edu-sharing-python.zip
tests/test_skill_bundle.py    Kopien gleich, Länge, Verweise, Frontmatter, ZIP
```

Die Kopien behalten ihre relativen Namen: `FLOWS.md` verweist auf
`examples/05_flow_search.py`, und das liegt dann unter `reference/examples/`.

### Aufbau von SKILL.md

1. Installieren und verbinden (sync und async, Umgebung, Metadatenset)
2. Wie die Bibliothek gebaut ist (zwei Ebenen, Objekte, Fehler)
3. Rezepte je Aufgabe, jedes mit lauffähigem Code und der Rückgabeform:
   Suche · Knoten lesen · Anlegen und Ändern · Dateien · Sammlungen ·
   Veröffentlichen und Rechte · Redaktion (Kommentare, Bewertungen,
   Vorschläge, Workflow) · Beziehungen und Kindobjekte · Vokabular · Personen
   und Gruppen · kuratierte Seiten und Skills · roher Transport · LLM-Gateway
   Proxy · LLM-Gateway Template-Modus · Textextraktion und Metadata Agent ·
   Bausteine für KI-Werkzeuge
4. Die Oberfläche als Tabelle — **jede Methode als Aufruf mit ihren
   Parametern und der Rückgabe**, nicht als bloßer Name (ersetzt die heutige
   Tabelle „object by object“; die 15 Methoden aus der Messung stehen dann
   mit Pflichtparametern da)
5. Fehler: die Hierarchie unter `EduSharingError`, welche Klasse wann kommt,
   was man fängt, `error_type` in `ToolResult`
6. Die zehn Fallen, die Code brechen — je eine Zeile, Rest in `TRAPS.md`
7. Wo die Details stehen — jede Datei in `reference/` direkt verlinkt

### Wächter

| Test | prüft |
|---|---|
| `test_skill_bundle.py` (neu) | Kopien byte-gleich mit `docs/`; SKILL.md < 500 Zeilen; jede Datei in `reference/` aus SKILL.md direkt verlinkt; Frontmatter-Regeln; Inhaltsverzeichnis = Überschriften in REFERENCE/FLOWS; ZIP: Ordner als Wurzel, SKILL.md drin, `description` ≤ 200 |
| `test_skill_bundle.py`: **Vermittlungswache** (neu, aus der Messung oben) | jede öffentliche Methode mit Pflichtparametern steht in **SKILL.md** als `name(…)` mit genau diesen Parameternamen (aus `inspect.signature`, nicht gepflegt); jede Methode ohne Pflichtparameter steht im Bündel mit Rückgabeform (Tabellenzeile `\| … \| Ergebnis \|` oder Beispiel). Gegenprobe: eine Zeile mit `set_property(value)` statt `set_property(prop, value)` wird rot |
| `test_docs_complete.py` | bleibt für SKILL.md: jeder Ablauf, jede Tür, jeder Name der Beispiele; „jeder öffentliche Name“ gilt fortan für das Bündel (SKILL.md + `reference/`) |
| `test_docs_code.py` | + TRAPS-Dateien; neu: Aufrufe an bekannten Wurzeln binden an die echte Signatur |

## Nicht-funktional

- **Sprache:** Einstieg und Nachschlagedateien in zwei Sprachen (Entscheidung 2);
  das LLM liest SKILL.md (englisch), das deutsche Paar liegt daneben.
- **Sicherheit:** Der Skill enthält keine Zugangsdaten; die Rezepte lesen sie aus
  der Umgebung. Hinweis für claude.ai/API: dort läuft der Skill in einer
  Sandbox, oft ohne Netz — er hilft Code zu schreiben, ausgeführt wird er dort,
  wo das Repositorium erreichbar ist.
- **Pflege:** eine Quelle je Inhalt; `sync_skill.py` plus Test verhindern Drift.

## Risiken

| Risiko | Gegenmittel |
|---|---|
| Rezepte rufen mit falschen Argumenten | neue Signaturwache; Auswertung mit frischem Agenten |
| Kopien veralten | Test verlangt Gleichheit; `sync_skill.py` behebt es |
| claude.ai lehnt die ZIP ab (Dateiname `skill.md`/`SKILL.md` ist in der Hilfe uneinheitlich) | Struktur und Beschreibung nach der Hilfe; der Upload selbst ist ungeprüft und wird so benannt |
| SKILL.md sprengt 500 Zeilen | Test; Rezepte knapp, Einzelheiten in REFERENCE |

## Abnahme (Entscheidung 4)

Zwölf Aufgaben, die ein Nutzer ohne Vorwissen stellt; ein frischer Agent
schreibt je Aufgabe eine Datei und liest dabei **nur** den Skill-Ordner:

| # | Aufgabe | Art |
|---|---|---|
| E1 | 5 Materialien zu „Bruchrechnung“ im Fach Mathematik: Titel und URL | lesend |
| E2 | Für einen Knoten Titel, Schlagworte, Fach als Label und seine Sammlungen | lesend |
| E3 | Sammlungen zu „Physik“ finden, die erste öffnen, ihre Materialien auflisten | lesend |
| E4 | Volltext eines Materials holen; wenn keiner da ist, sagen warum | lesend |
| E5 | Material mit Titel, Beschreibung, Fach und Bildungsstufe anlegen und prüfen, dass alles gespeichert ist | schreibend |
| E6 | Zwei Schlagworte ergänzen, ohne vorhandene zu verlieren, und veröffentlichen | schreibend |
| E7 | Ein Fach vorschlagen statt schreiben, und den Vorschlag so übernehmen, dass der Wert am Knoten steht | schreibend |
| E8 | Eine Textdatei hochladen und zurücklesen | schreibend |
| E9 | Das am wenigsten ausgelastete Modell der AcademicCloud zusammenfassen lassen und sagen, welches antwortete | lesend (b-api) |
| E10 | Mit der Kette der Themenseiten eine Kurzbeschreibung einer Sammlung erzeugen; Nutzereingaben nicht als freier Text | lesend (b-api) |
| E11 | Schlagworte vom Modell vorschlagen lassen und den besten übernehmen | schreibend (b-api) |
| E12 | Eine Funktion für ein MCP-Werkzeug: Suche, Erfolg und Fehler in derselben JSON-Form, Repositoriumstext als nicht vertrauenswürdig markiert | Code |

**Prüfung je Aufgabe:** parst; jeder Aufruf an bekannten Wurzeln existiert und
bindet an die Signatur; lesende Aufgaben laufen gegen Staging mit Exitcode 0.
Schreibende nur statisch — der Agent führt nichts aus.

**Grundlinie:** dieselben zwölf Aufgaben zuerst mit dem **alten** Skill. Die
Auswertung taugt nur, wenn sie dort Fehler findet.

**Bestanden:** mit dem neuen Skill alle zwölf statisch sauber und alle
lesenden live grün.

---

## Aufgaben

### Phase 0 — Auswertung zuerst

**Schritt 0: `/better-coding-workflow` laden.**

**A1 · Prüfskript** (Scratchpad, nicht im Repo): liest eine Ergebnisdatei,
parst sie, prüft Aufrufe an `repo`, `node`, `api`, `templates`, `extraction`,
`agent` gegen die echte Oberfläche — Existenz und `bind_partial` der Signatur.
Gegenprobe: eine Datei mit einem erfundenen Argument muss rot werden.

**A2 · Grundlinie:** frischer Agent, alter Skill (Kopie von HEAD), zwölf
Aufgaben. Ergebnis je Aufgabe festhalten.

### Phase 1 — Werkzeug und Wächter

**Schritt 0: `/better-coding-workflow` neu laden.**

**T1 · `scripts/sync_skill.py`** — Test zuerst (`test_skill_bundle.py`: Kopien
gleich; rot, weil `reference/` fehlt), dann Skript, dann Lauf.

**T2 · Inhaltsverzeichnis** in `docs/REFERENCE*.md` und `docs/FLOWS*.md` — Test
zuerst (Liste = `##`-Überschriften), dann die Listen; danach neu synchronisieren.

**T3 · Signaturwache** in `test_docs_code.py` für Aufrufe an `node`,
`templates`, `api` — Test zuerst mit einem erfundenen Argument, dann die Wache.

**T3b · Vermittlungswache** in `test_skill_bundle.py`: für jede öffentliche
Methode mit Pflichtparametern muss SKILL.md `name(` gefolgt von genau diesen
Parameternamen enthalten. „Pflicht“ heißt, wie in der Messung vom 11.09.2026:
per `inspect.signature`, Parameter ohne Vorgabe, ohne `self`, ohne `*args`
und `**kwargs`; die Methoden sind die von `oeffentliche_namen()` in
`test_docs_complete.py` mit Herkunft `Datei:Klasse`, ohne Properties. Läuft gegen den **alten** Skill zuerst rot mit
den 15 Methoden aus der Messung — das ist die Gegenprobe. Sie wird grün, wenn
T5 die Tabelle schreibt.

### Phase 2 — Inhalt

**Schritt 0: `/better-coding-workflow` neu laden.**

**T4 · TRAPS verschieben:** Abschnitte 4–5 aus SKILL.md nach
`reference/TRAPS.md`, aus SKILL.de.md nach `reference/TRAPS.de.md`; Verweise
anpassen; beide in die Listen der Doku-Tests.

**T5 · SKILL.md neu** (englisch), Aufbau wie oben, < 500 Zeilen.

**T6 · SKILL.de.md neu** (deutsch), dieselben Rezepte.

**T7 · Doku-Tests anpassen:** „jeder öffentliche Name“ gegen das Bündel;
`test_skill_bundle.py` um Länge, Verweise eine Ebene tief, Frontmatter.

### Phase 3 — Verteilung

**Schritt 0: `/better-coding-workflow` neu laden.**

**T8 · `scripts/build_skill_zip.py`** — Test zuerst (Ordner als Wurzel,
SKILL.md drin, `description` ≤ 200), dann Skript; `dist/` ist ignoriert.

**T9 · README (beide Sprachen):** Abschnitt „Den Skill im eigenen Werkzeug
nutzen“ — Claude Code, Codex, claude.ai-ZIP; Hinweis in REFERENCE.

**T10 · CHANGELOG.**

### Phase 4 — Abnahme

**Schritt 0: `/better-coding-workflow` neu laden.**

**T11 · Auswertung mit dem neuen Skill**, gleiche zwölf Aufgaben, frischer
Agent; lesende live gegen Staging. Lücken, die er zeigt, im Skill schließen und
erneut auswerten.

**T12 · Gate, Commit, Push, CI.**

## Verifikation

| Anforderung | Beleg | Fehlerbild |
|---|---|---|
| ohne Vorkenntnisse nutzbar | Abnahme: 12/12 statisch sauber, lesende live grün; Grundlinie schlechter | Aufgabe scheitert |
| jede Option erreichbar | Bündel nennt jeden öffentlichen Namen; SKILL.md nennt jeden Ablauf, jede Tür, jeden Namen der Beispiele | Wache rot |
| jede Option **vermittelt** | Vermittlungswache: 0 Methoden mit ungezeigten Pflichtparametern in SKILL.md (heute 15); Rückgabeform je Methode im Bündel | Wache rot |
| außerhalb des Repos nutzbar | keine Verweise aus dem Skill-Ordner hinaus; Kopien gleich | Wache rot |
| Regeln der Anbieter | < 500 Zeilen, eine Ebene, Frontmatter, ZIP-Beschreibung ≤ 200 | Wache rot |
| zwei Sprachen | beide Einstiege unter denselben Wächtern, Kopien beider Sprachen | Wache rot |

Regression: die ganze Suite, `ruff`, `mypy --strict`.
