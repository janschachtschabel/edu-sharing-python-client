# Design: die restlichen Endpunkte und Abläufe

## Ziel

Die acht edu-sharing-Endpunkte und fünf Abläufe schließen, die der Abgleich mit
`wlo-mcp-sc` und der Ideendatenbank am 28.08.2026 als Lücke ausgewiesen hat —
damit beide Fremdanwendungen ohne `repo.raw` auskommen.

## Kontext

Nach `ce63d23` sind 23 von 41 MCP-Werkzeugen und 16 von 25 Client-Methoden der
Ideendatenbank direkt abbildbar. Was fehlt, ist über `repo.raw.json(...)`
erreichbar, aber ohne getippte Hülle, ohne Rückleseprobe und ohne die
gemessenen Eigenheiten — und genau die sind bei diesen Endpunkten dicht gesät.

Alles Folgende wurde am **28.08.2026 gegen Staging** in einem eigens angelegten
Wegwerf-Ordner gemessen, nicht aus der OpenAPI abgeleitet.

## Umfang

**Drin** — acht Endpunktfamilien:

| Endpunkt | Wofür | Woher die Anforderung |
|---|---|---|
| `/rating/v1/ratings/-home-/{node}` | Bewertungen setzen, zurücknehmen, lesen | Ideendatenbank |
| `/comment/v1/comments/-home-/{node}` | Kommentare lesen, schreiben, ändern, löschen | Ideendatenbank |
| `/iam/v1/people/-home-/-me-/memberships`, `/iam/v1/groups/…` | Wer darf moderieren | Ideendatenbank |
| `/node/v1/nodes/-home-/{id}/preview` | Vorschaubild setzen und entfernen | Ideendatenbank |
| `/node/v1/nodes/-home-/{id}/children` mit Blättern/Sortieren | Ordnerinhalt durchgehen | beide |
| `/suggestions/v1/-home-/{node}` | Metadaten vorschlagen statt schreiben | MCP (3 Werkzeuge) |
| `/node/v1/nodes/-home-/{id}/workflow` | Zur Redaktion einreichen | MCP |
| `PUT /collection/v1/collections/-home-/{id}` | Sammlung umbenennen | MCP |

Und fünf Abläufe: `describe_many`, `related`, `browse_tree`,
`search_in_collection`, `collection_stats`.

**Draußen**, weiterhin und bewusst:

* Themenseiten (`ccm:page_variant`, `ccm:page_config`) und die Skills-Registry
  — Konventionen einer Instanz, nicht der API. Die Bibliothek bleibt generisch.
* `get_wikipedia_summary` und `get_url_text` — kein edu-sharing.
* Ein MCP-Server. Die Bausteine dafür liegen in `edusharing.agent`.

## Der gemessene Befund, auf den der Entwurf antwortet

### A. Bewertungen

* `PUT ?rating=4` mit dem Text als rohem Body → 200, **leerer Body**.
* **Die Knotenantwort trägt `rating` schon mit**: `{"overall": {"sum", "count",
  "rating"}, "affiliation": {…}, "user": 4.0}`. Eine Bewertung zu lesen kostet
  also **keine Anfrage** — dasselbe Muster wie `isPublic`.
* `GET …/history` antwortet **500 NotAnAdminException**. Die Einzelbewertungen
  sieht nur ein Administrator; die Zusammenfassung steht am Knoten.
* `rating=4.0` wird auf Staging **angenommen** (200). Die Ideendatenbank hat auf
  `redaktion.openeduhub.net` gemessen, dass ein Float verworfen wird und 500
  kommt. Der Unterschied ist instanzabhängig — die Bibliothek sendet
  Ganzzahlen als Ganzzahlen, das kostet nichts und deckt beide Fälle.
* `DELETE` → 200 auf Staging; die Ideendatenbank meldet 500 auf Produktion.

### B. Kommentare

* **Der Body wird 1:1 als Text gespeichert, ohne JSON-Auswertung.** Gemessen:
  ein gesendetes `"Erster"` kommt als `"Erster"` zurück — mit Anführungszeichen.
  Der Content-Type muss trotzdem `application/json` sein (sonst 415). Also:
  rohe UTF-8-Bytes senden, nicht `json=`.
* Anlegen ist `PUT …/{node}`, **Ändern ist `POST …/{comment}`**. Ein `PUT` auf
  die Kommentar-ID legt einen Kommentar *am Kommentar* an und endet in
  500 DAOValidationException.
* Antworten über `?commentReference={eltern-id}`; `replyTo` trägt die Referenz.
* Ein Kommentar hat `['comment', 'created', 'creator', 'ref', 'replyTo']`.

### C. Gruppen und Mitgliedschaften

* `GET /iam/v1/people/-home-/-me-/memberships` → `{"groups": [...]}`, je Gruppe
  `authorityName`, `groupName`, `profile`, `signupMethod`, `organizations`.
* `GET /iam/v1/groups/-home-/{g}` → 200 für eine Gruppe, in der man ist.
* `GET /iam/v1/groups/-home-/{g}/members` → **500 AccessDeniedException**
  („User does not have permissions to manage this group"). Mitglieder sieht
  nur, wer die Gruppe verwaltet.
* **`POST /iam/v1/groups/-home-/{name}` → 403.** Das Testkonto darf keine
  Gruppen anlegen.

> **Offener Punkt, der bewusst so bleibt.** Die schreibenden
> Gruppen-Operationen sind auf Staging mit diesem Konto **nicht live
> prüfbar**. Sie werden gebaut, weil danach gefragt wurde, und offline gegen
> die gemessene Anfrageform getestet — Methode, Pfad, Body. Dass die Instanz
> sie annimmt, bleibt **unbelegt**, und die Docstrings sagen das. Das ist die
> schwächere Verifikation; sie wird als solche benannt, nicht verschwiegen.

### D. Vorschaubild

* `POST …/{id}/preview?mimetype=image/png`, multipart, Feldname **`image`** →
  200. Mit `file` statt `image`: **500 NullPointerException: inputStream**.
* Die Knotenantwort trägt `preview.url` — auch das kostenlos.
* `DELETE …/preview` → 200 mit JSON-Body.

### E. Kinder blättern und sortieren

* `sortProperties=cm:name&sortAscending=false` wirkt: gemessen
  `['s2.txt', 's1.txt', 's0.txt', 'k.txt']`.
* `skipCount=2` → `['s0.txt', 'k.txt']`. `pagination` trägt `{total, from, count}`.
* Ohne `propertyFilter=-all-` kommen die Kinder ohne Eigenschaften (bereits in
  `flows/discover.py` festgehalten).

### F. Vorschläge

* `GET /suggestions/v1/-home-/{node}` → `{"nodeId": …, "suggestions": {}}` — ein
  **Wörterbuch**, nach `propertyId` geschlüsselt, in einer Hülle.
* `POST` mit `?version=` und einer **Liste** von `{propertyId, value,
  description, confidence}` → antwortet mit einer **Liste** der angelegten
  Vorschläge, je mit `id`, `status: "PENDING"`, `created`, `createdBy`.
* `PATCH ?status=ACCEPTED` mit einer Liste von IDs → 200, Antwort `[]`.
* **Danach steht der Wert nicht am Knoten.** Gemessen: `keywords` blieb `[]`.
  Der Befund des MCP ist reproduziert. `/suggestions/v1` ist ein Ablagefach mit
  Protokoll, kein Mechanismus, der etwas anwendet.

### G. Redaktionelle Einreichung

* `GET …/{id}/workflow` → eine **Liste** von Verlaufseinträgen, leer am Anfang.
* `PUT` mit `{receiver: [{authorityName, authorityType}], status, comment}` →
  200, leerer Body. Danach steht der Eintrag im Verlauf, mit `time` und `editor`.

### H. Sammlung umbenennen

* `PUT /collection/v1/collections/-home-/{id}` **ohne `ref.id`** → 500
  NullPointerException (`NodeRef.getId()`). Die ID im Pfad genügt nicht; das
  DTO wird gelesen, nicht die URL. Bestätigt, was der MCP notiert hat.
* Mit `ref.id` → 200. Danach stehen `title`, `cm:title` **und `cm:name`** auf
  dem neuen Wert: Umbenennen benennt auch den Knoten um.

## Ansatz

Drei Alternativen für die Modulaufteilung wurden erwogen:

**A — ein Modul `extra.py` für alles.** Am wenigsten Dateien. Verworfen: sechs
unabhängige Endpunktfamilien mit je eigenen Eigenheiten in einer Datei, die
sofort über 800 Zeilen läge und sechs Gründe hätte, sich zu ändern.

**B — ein Modul je Endpunktfamilie, angehängt an `Node` bzw. `Repository`.**
Folgt dem, was `childobjects.py`, `relations.py`, `permissions.py` und
`placement.py` bereits tun: ein Modul trägt die gemessenen Eigenheiten *eines*
Endpunkts, `Node` reicht durch. **Gewählt.**

**C — alles in die generierte Schicht und nur dünn wrappen.** Verworfen: die
generierte Schicht bringt ihren eigenen Client mit — kein Retry, keine
Fehlerübersetzung, keine Rückleseprobe — und trägt gemessene Fallen weiter
(`rating: float`).

## Architektur

### Dateien

| Datei | Verantwortung | geschätzt |
|---|---|---|
| `src/edusharing/ratings.py` | **neu** — Bewertung setzen, nehmen, lesen | ~130 |
| `src/edusharing/comments.py` | **neu** — Kommentare, roher Body, POST zum Ändern | ~180 |
| `src/edusharing/people.py` | **neu** — Mitgliedschaften, Gruppen, Mitglieder | ~230 |
| `src/edusharing/suggestions.py` | **neu** — Vorschläge, mit dem Vorbehalt | ~180 |
| `src/edusharing/workflow.py` | **neu** — Einreichen und Verlauf | ~130 |
| `src/edusharing/flows/tree.py` | **neu** — Sammlungsbaum: browse, suchen, zählen | ~260 |
| `src/edusharing/content.py` | +Vorschaubild setzen/löschen | 182 → ~250 |
| `src/edusharing/nodes.py` | +`Nodes.children()`, +Durchreichen | 482 → ~560 |
| `src/edusharing/collections.py` | +`Collections.update()` | 258 → ~310 |
| `src/edusharing/flows/discover.py` | +`describe_many`, +`related` | 542 → ~650 |
| `src/edusharing/flows/__init__.py` | Fassade | +60 |
| `src/edusharing/repository.py` | `repo.people` | +15 |
| `src/edusharing/_sync.py` | synchroner Durchgriff für alles Neue | +120 |

`nodes.py` und `discover.py` wachsen über die 300-Zeilen-Marke hinaus — bei
beiden ist das Verhältnis Doku zu Code rund 2:1 (gemessen: 219 bzw. 201
Codezeilen), und beide haben genau **einen** Grund, sich zu ändern (wie ein
Knoten funktioniert, bzw. wie ein Lesevorgang zu JSON wird). Kein Aufteilen um
der Zahl willen; ausgelagert wird nur, was eine eigene Verantwortung hat —
darum `flows/tree.py` für den Sammlungsbaum.

### Öffentliche Schnittstellen

```python
# Bewertungen -- ratings.py
node.rating                       -> Rating | None     # kostenlos aus der Antwort
node.rate(4, "gut")               -> Rating            # PUT, dann zuruecklesen
node.unrate()                     -> bool              # True = es gab eine

@dataclass(frozen=True)
class Rating:
    average: float; count: int; own: float | None

# Kommentare -- comments.py
node.comments.list()              -> list[Comment]
node.comments.add(text, reply_to=None) -> Comment
node.comments.edit(comment_id, text)   -> Comment
node.comments.delete(comment_id)  -> None

@dataclass(frozen=True)
class Comment:
    id: str; text: str; author: str; created: datetime; reply_to: str | None

# Menschen -- people.py
repo.people.memberships()         -> list[Group]
repo.people.group(name)           -> Group
repo.people.members(name)         -> list[str]         # Autoritaetsnamen
repo.people.create_group(name, display_name=None) -> Group   # ungeprueft live
repo.people.delete_group(name)    -> None                    # ungeprueft live
repo.people.add_member(group, authority)    -> bool          # ungeprueft live
repo.people.remove_member(group, authority) -> bool          # ungeprueft live

@dataclass(frozen=True)
class Group:
    name: str; display_name: str; signup: str | None; raw: dict

# Vorschlaege -- suggestions.py
node.suggestions.list()           -> list[Suggestion]
node.suggestions.propose(prop, value, why, confidence=None) -> Suggestion
node.suggestions.decide(ids, accept=True) -> None

@dataclass(frozen=True)
class Suggestion:
    id: str; property: str; value: str; status: str
    why: str | None; confidence: float | None; author: str

# Einreichen -- workflow.py
node.workflow.history()           -> list[WorkflowStep]
node.workflow.submit(to, status, comment="") -> WorkflowStep

@dataclass(frozen=True)
class WorkflowStep:
    status: str; receivers: tuple[str, ...]; comment: str
    editor: str; at: datetime

# Ergaenzungen
node.content.set_preview(data, mimetype="image/png") -> Node
node.content.delete_preview()     -> Node
node.preview_url                  -> str | None        # kostenlos
repo.nodes.children(node_id, *, limit=50, offset=0,
                    sort="cm:name", ascending=True,
                    only="files"|"folders"|None) -> ChildPage
repo.collections.update(collection_id, title=None, description=None) -> Node

@dataclass(frozen=True)
class ChildPage:
    nodes: tuple[Node, ...]; total: int; offset: int

# Ablaeufe
repo.flows.describe_many(ids)                       -> dict
repo.flows.related(node_id, limit=10)               -> dict
repo.flows.browse_tree(collection_id, depth=2)      -> dict
repo.flows.search_in_collection(collection_id, text, depth=3) -> dict
repo.flows.collection_stats(collection_id, sample=100)        -> dict
```

### Datenfluss

Unverändert: `Transport` (Auth, Retry, Nebenläufigkeit, Fehlerübersetzung) →
Endpunktmodul (gemessene Eigenheiten, Rückleseprobe) → `Node`/`Repository`
(Durchreichen) → `flows/*` (mehrere Aufrufe, JSON heraus). Die Abhängigkeiten
zeigen nach innen; kein Endpunktmodul kennt die Ablaufschicht.

### Abhängigkeiten

**Keine neuen.** Alles mit `httpx` und der Standardbibliothek.

## Nichtfunktionales

* **Sicherheit.** Nichts Neues an der Angriffsfläche: jede ID geht durch
  `path_segment()`. Die schreibenden Gruppen-Operationen ändern fremde Rechte
  — ihre Docstrings sagen, was sie tun, und es gibt keine Bequemlichkeit, die
  das versehentlich auslöst.
* **Zurücklesen.** Jeder Schreibvorgang, dessen Antwort leer ist (Bewertung,
  Kommentar, Workflow, Sammlung umbenennen), liest zurück — genau der Grund,
  aus dem `permissions.py` es tut.
* **Anfragen.** Jeder neue Ablauf nennt seine Anfragezahl in der Kostentabelle
  von `FLOWS.md`, gedeckt durch einen Test. Die Baumabläufe deckeln ihre
  Verzweigung und **sagen im Ergebnis, was sie ausgelassen haben** — ein
  stilles Abschneiden liest sich wie Vollständigkeit.
* **Sprache.** Quelltext, Docstrings und Commits auf Englisch bzw. in der
  Hausform des Repos; Testnamen und Testdocstrings auf Deutsch, wie bisher.
  Beide READMEs und beide FLOWS-Dateien bleiben gleichauf.

## Risiken

| Risiko | Gegenmittel |
|---|---|
| Gruppen-Schreiben live ungeprüft | Offline gegen die gemessene Anfrageform; Docstring und Bericht sagen es. Kein Live-Test, der fremde Gruppen anfasst. |
| `/suggestions/v1` verleitet zum Irrtum, ACCEPTED schreibe etwas | Der Vorbehalt steht im Modul-Docstring, in der Methoden-Doku, in beiden READMEs und in einem Test, der ihn festhält. |
| Baumabläufe explodieren in Anfragen | Fester Fan-out-Deckel je Ebene, Entdopplung nach ID (Sammlungen bilden einen DAG, keinen Baum), und `truncated` im Ergebnis. |
| `nodes.py` und `discover.py` wachsen weiter | Nur Durchreichen bzw. zwei Abläufe hinein; alles mit eigener Verantwortung kommt in ein eigenes Modul. |
| Bewertungs-/Kommentar-Eigenheiten sind instanzabhängig | Was auf Staging gemessen wurde, steht als Staging-Messung da; was die Ideendatenbank auf Produktion gemessen hat, ist als deren Messung gekennzeichnet. Keine Vermischung. |

## Offene Punkte

Keine — bis auf den benannten: schreibende Gruppen-Operationen bleiben live
unverifiziert, weil das Testkonto sie nicht ausführen darf. Das ist im Bericht
zu nennen, nicht zu übergehen.

---

# Aufgaben

Fünf Pakete, jedes für sich lauffähig und getestet, jedes ein eigener Commit.

## Paket 1 — Bewertungen und Kommentare

Schritt 0: `/better-coding-workflow` aufrufen (Skills entladen sich).

**Aufgabe 1.1 — `Rating` lesen, kostenlos**
Neu: `src/edusharing/ratings.py`, `tests/test_ratings.py`.
Test zuerst: die Knotenantwort trägt `rating.overall.rating`, `.count` und
`rating.user`; `node.rating` gibt ein `Rating` oder `None`, wenn `count == 0`.
Prüfen: `uv run pytest tests/test_ratings.py -q` → rot, dann grün.

**Aufgabe 1.2 — bewerten und zurücknehmen**
`Ratings.set(value, text="")` sendet `PUT ?rating=<int>` mit rohem Body und
liest den Knoten zurück (die Antwort ist leer). Ganzzahlige Werte werden als
Ganzzahl formatiert. `Ratings.clear()` gibt `True`, wenn es eine eigene gab.
Test: der Query-Parameter enthält `4`, nicht `4.0`.

**Aufgabe 1.3 — `Comment` und Lesen**
Neu: `src/edusharing/comments.py`, `tests/test_comments.py`.
`Comment.from_response` liest `ref.id`, `comment`, `creator.authorityName`,
`created` (Millisekunden seit Epoche → `datetime`), `replyTo.id`.

**Aufgabe 1.4 — schreiben, ändern, löschen, antworten**
`add` = `PUT …/{node}` mit **rohen UTF-8-Bytes** und
`Content-Type: application/json`; `edit` = **`POST` …/{comment}**;
`delete` = `DELETE …/{comment}`; `reply_to` → `?commentReference=`.
Test hält fest, dass `add` **kein** `json=` benutzt — sonst stünden
Anführungszeichen im Text.

**Aufgabe 1.5 — Durchreichen, synchron, Live, Doku**
`Node.rating`, `Node.rate`, `Node.unrate`, `Node.comments`; `SyncNode`
entsprechend; Live-Tests im Wegwerf-Ordner; beide READMEs, ARCHITECTURE.
Prüfen: `uv run pytest -q`, `uv run --env-file .env pytest -m write -q`,
`uv run ruff check src tests`.

Commit: `feat(social): Bewertungen und Kommentare`

## Paket 2 — Menschen: Gruppen und Mitgliedschaften

Schritt 0: `/better-coding-workflow` aufrufen.

**Aufgabe 2.1 — `Group` und Lesen**
Neu: `src/edusharing/people.py`, `tests/test_people.py`.
`memberships()`, `group(name)`, `members(name)`. Test hält fest, dass
`members` bei fehlender Verwaltungsberechtigung `PermissionDeniedError` wirft
(gemessen: 500 AccessDeniedException, bereits übersetzt).

**Aufgabe 2.2 — schreibende Operationen**
`create_group`, `delete_group`, `add_member`, `remove_member`. Offline gegen
die gemessene Anfrageform. Jeder Docstring sagt: **live nicht verifiziert**,
weil das Testkonto 403 bekommt.

**Aufgabe 2.3 — `repo.people`, synchron, Live-Lesetest, Doku**
Live geprüft wird nur das Lesen. Beide READMEs.

Commit: `feat(people): Gruppen und Mitgliedschaften`

## Paket 3 — Redaktion: Vorschläge und Einreichung

Schritt 0: `/better-coding-workflow` aufrufen.

**Aufgabe 3.1 — `Suggestion` und Lesen**
Neu: `src/edusharing/suggestions.py`, `tests/test_suggestions.py`.
Die GET-Antwort ist ein Wörterbuch unter `suggestions`, nach `propertyId`
geschlüsselt; die Liste kommt flach heraus.

**Aufgabe 3.2 — vorschlagen und entscheiden**
`propose` sendet eine **Liste** an `POST ?version=`; `decide` sendet eine Liste
von IDs an `PATCH ?status=`. Ein Test hält den Vorbehalt fest: nach `decide`
steht der Wert **nicht** am Knoten.

**Aufgabe 3.3 — Workflow**
Neu: `src/edusharing/workflow.py`, `tests/test_workflow.py`.
`history()` liest die Liste, `submit()` sendet `PUT` und liest zurück.

**Aufgabe 3.4 — Durchreichen, synchron, Live, Doku**
Live-Test für beide im Wegwerf-Ordner, inklusive des reproduzierten
Vorbehalts. Beide READMEs, ARCHITECTURE.

Commit: `feat(editorial): Vorschlaege und redaktionelle Einreichung`

## Paket 4 — Vorschaubild, Blättern, Umbenennen

Schritt 0: `/better-coding-workflow` aufrufen.

**Aufgabe 4.1 — Vorschaubild**
`content.py`: `set_preview(data, mimetype)` — multipart, Feldname **`image`**
(mit `file` → 500) — und `delete_preview()`. `Node.preview_url` kostenlos aus
der Antwort.

**Aufgabe 4.2 — Kinder blättern und sortieren**
`nodes.py`: `Nodes.children(...)` mit `ChildPage`. Nicht zu verwechseln mit
`node.children` (Serienobjekte, nach Aspekt gefiltert) — der Docstring beider
sagt, was das andere tut.

**Aufgabe 4.3 — Sammlung ändern**
`collections.py`: `update(id, title=, description=)`. `ref.id` ist Pflicht
(ohne: 500), die Beschreibung geht über die Knotenroute, und es wird
zurückgelesen. Test hält fest, dass Umbenennen auch `cm:name` ändert.

**Aufgabe 4.4 — synchron, Live, Doku**

Commit: `feat(nodes): Vorschaubild, Blaettern, Sammlung umbenennen`

## Paket 5 — Die fünf Abläufe

Schritt 0: `/better-coding-workflow` aufrufen.

**Aufgabe 5.1 — `describe_many`**
`flows/discover.py`. Gepoolt über `asyncio.gather` mit einem Semaphor; ein
fehlender Knoten wird als `{"id": …, "error": …}` gemeldet, nicht geworfen —
sonst reißt ein toter Indexeintrag die ganze Liste mit.

**Aufgabe 5.2 — `related`**
`flows/discover.py`. `describe` → Fach und Stufe des Knotens → `search` mit
diesen Filtern, der Knoten selbst herausgefiltert. Ohne Fach und Stufe kommt
eine leere Liste mit `reason` zurück, keine willkürlichen Treffer.

**Aufgabe 5.3 — `browse_tree`**
Neu: `src/edusharing/flows/tree.py`, `tests/test_flows_tree.py`.
Rekursiv über `collection_contents`, entdoppelt nach ID (DAG), Fan-out je
Ebene gedeckelt. `truncated` nennt, was ausgelassen wurde.

**Aufgabe 5.4 — `search_in_collection`**
Traversal plus lokaler Textabgleich, weil `ngsearch` nicht auf eine Sammlung
einzugrenzen ist (gemessen, dreifach). Der Docstring sagt, warum.

**Aufgabe 5.5 — `collection_stats`**
Zählung aus `pagination` plus Auswertung über die tatsächlichen Kinder bis
`sample`. `sampled` nennt, worüber gezählt wurde.

**Aufgabe 5.6 — Fassade, synchron, Live, Doku, Beispiel**
Fünf Einträge in der Kostentabelle beider FLOWS-Dateien, je mit Ein- und
Ausgabe und „Was dahinter läuft". Ein Beispiel `13_flow_tree.py`.

Commit: `feat(flows): fuenf Ablaeufe fuer Baum, Verwandtes und Stapel`

## Verifikation

Für jedes Paket, mit Ausgabe belegt:

```
uv run pytest -q                                   # alle offline
uv run pytest tests/test_<neu>.py -q --cov=edusharing.<neu> --cov-report=term-missing
uv run --env-file .env pytest -m "live or write" tests/test_live_write.py -q
uv run ruff check src tests docs
```

Am Ende zusätzlich: alle Beispiele mit Exitcode 0, und Staging steht wieder auf
`['Dokumente', 'Bilder', 'Inbox']` ohne eigene Sammlungen.

**Regressionsrisiko.** `nodes.py`, `content.py`, `collections.py`,
`flows/discover.py` und `_sync.py` werden geändert — die bestehenden 635 Tests
decken sie ab und müssen grün bleiben. `tests/test_sync_surface.py` prüft, dass
kein neuer Durchgriff vergessen wurde; jede neue synchrone Methode braucht dort
einen Eintrag.
