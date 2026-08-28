# Design: kuratierte Seiten — und was bewusst draußen bleibt

## Ziel

Die letzten sieben Werkzeuge des `wlo-mcp-sc` abbilden, soweit sie von
edu-sharing handeln: den **Page Builder** (Themenseiten) lesen und die
gerenderte Variante umstellen. Für die drei, die nicht von edu-sharing handeln,
begründet festhalten, warum sie nicht in diese Bibliothek gehören — und für die
zwei, die schon heute mit vorhandenen Mitteln gehen, zeigen wie.

## Kontext

Nach `9ae40ec` sind 34 von 41 MCP-Werkzeugen und 25 von 25 Client-Methoden der
Ideendatenbank abgebildet. Die sieben offenen wurden bisher pauschal als
„WLO-spezifisch, bewusst draußen" geführt. Diese Begründung hält bei genauem
Hinsehen nur für drei von ihnen.

Alles Folgende ist am **28.08.2026 gegen Staging gemessen**, nicht aus der
OpenAPI abgeleitet.

## Die sieben, einzeln geprüft

| Werkzeug | Worauf es wirklich beruht | Gehört in eine generische Bibliothek? |
|---|---|---|
| `search_wlo_topic_pages` | `ccm:page_config_ref` auf einer Sammlung | **ja** — Page Builder ist edu-sharings eigene Funktion |
| `get_topic_page_content` | `ccm:page_variant_config` → Schwimmlinien | **ja** |
| `wlo_set_topic_page` | `POST …/property?property=ccm:page_config` | **ja** |
| `get_skill_registry` | Kinder einer Sammlung nach Inhaltstyp filtern, Text lesen | **geht schon** — nur dokumentieren |
| `search_skill` / `get_skill` | Suche auf `ccm:oeh_extendedType`, `node.content.text()` | **geht schon** — nur dokumentieren |
| `get_wikipedia_summary` | Wikipedia-REST-API | **nein** — kein edu-sharing |
| `get_url_text` | beliebige URL abrufen und Text extrahieren | **nein** — kein edu-sharing |

Die `ccm:`-Eigenschaften des Page Builders sind **keine WLO-Erfindung**. Sie
gehören zum Inhaltsmodell von edu-sharing; WLO benutzt sie nur. Eine
Themenseite ist damit dasselbe wie jede andere kuratierte Seite einer
edu-sharing-Instanz, und der generische Name dafür ist „die Seite, die eine
Sammlung rendert" — nicht „Themenseite".

## Was am 28.08.2026 gemessen wurde

Ausgangspunkt: die Sammlung **Deutsch** auf Staging und ihr Konfigurationsordner
`f2020460-d304-46b4-8204-60d304d6b4c5`.

1. **Eine Sammlung mit Seite trägt `ccm:page_config_ref`** — einen Store-Ref auf
   einen Ordner vom Typ `ccm:map`, benannt `PAGE_<uuid>`. Ohne diese Eigenschaft
   gibt es keine Seite; das ist das einzige verlässliche Kennzeichen.

2. **Der Ordner trägt `ccm:page_config`**, ein JSON-Dokument. Gemessen:
   `{"variants":["workspace://SpacesStore/a95029c1-…","workspace://SpacesStore/3e0daa41-…"]}`
   — **ohne** `default`. Ein Dokument ohne `default` rendert die **erste**
   Variante der Liste. „Keine festgelegte Variante" und „Variante 1 festgelegt"
   sehen für den Betrachter gleich aus, sind aber verschiedene Zustände, und ein
   Schreibvorgang muss sie auseinanderhalten.

3. **Die Varianten sind die Kinder des Ordners**, ebenfalls `ccm:map`, jede mit
   `ccm:page_variant_config` (3,5–4,1 kB JSON). Die Kinderliste der Bibliothek
   sendet bereits `propertyFilter=-all-`, also kommen die Dokumente **mit** —
   eine Seite kostet damit **zwei** Anfragen, nicht 1 + n.

4. **Die Schwimmlinien liegen unter `structure.swimlanes`**, je mit `heading`,
   `type` und `grid`; jedes Grid-Element hat `item` (den Widget-Namen) und
   optional `nodeId` als Store-Ref. Gemessen an der Variante
   `3e0daa41-…`: 9 Linien, 10 Grid-Elemente, eine davon (`wlo-editorial-members`)
   ganz ohne `nodeId`. Ein Item ohne Knoten ist also der Normalfall, kein Fehler.

5. **`ccm:page_variant_is_template` ist ein String**, `"false"`, nicht `false`.

6. **Die Zielgruppenfelder sind meist leer.** Bei beiden gemessenen Varianten
   sind `ccm:page_variant_profiling_target_group` und `ccm:educationalcontext`
   unbesetzt, während der `variables`-Block des Konfigurationsdokuments sehr wohl
   eine Voreinstellung trägt (`virtual:profiling_widget_intention: "teach"`,
   `virtual:profiling_widget_education_level: "…/sekundarstufe_1"`). Die beiden
   Quellen sind verschiedene Aussagen; das MCP hat 2026-08-11 nachgewiesen, dass
   sie sich sogar widersprechen. Diese Bibliothek gibt daher **beide** aus und
   führt keine auf die andere zurück.

7. **Die Sammlungssuche liefert ohne `propertyFilter=-all-` gar keine
   Eigenschaften** — gemessen: 0 auf allen 25 Treffern. Mit dem Parameter kommen
   33–57 Eigenschaften je Treffer, und `ccm:page_config_ref` ist dabei: 2 von 25
   Treffern zu „Deutsch" tragen eine Seite. **Damit kostet das Finden kuratierter
   Seiten eine Anfrage, nicht 1 + n.** Das MCP liest hier je Kandidat nach.

8. **Auf `ccm:page_config_ref` lässt sich nicht filtern**:
   `400 DAOValidationException: Widget ccm:page_config_ref was not found in the
   mds oeh`. Die Seite muss also aus der Antwort erkannt werden, nicht aus der
   Anfrage.

9. **Der Testzugang darf die fremde Seite nicht schreiben** (`can_write == False`
   auf dem Ordner der Sammlung Deutsch). Der Schreibpfad wird deshalb an einer
   **selbst angelegten** Seite geprüft, nicht an einer bestehenden.

## Umfang

**Drin:**

- `pages.py` — der Page Builder auf API-Ebene: `CuratedPage`, `PageVariant`,
  `Swimlane`, `SwimlaneItem`, `NodePage` (Zugriffsobjekt an `Node.page`).
- `flows/pages.py` — zwei Abläufe: `page()` (JSON-fertige Seitenstruktur,
  wahlweise mit aufgelösten Widgets) und `find_pages()` (welche Sammlungen eine
  Seite tragen).
- Eine Korrektur an `collections.find`: `propertyFilter=-all-` mitsenden, damit
  Treffer überhaupt Eigenschaften haben.
- Synchrone Durchgriffe, beide READMEs, `docs/FLOWS.md` + `.de.md`, ein Beispiel.
- Ein Kochbuch-Abschnitt für den Skills-Fall (bestehende Mittel, kein neuer Code).

**Draußen, mit Begründung:**

- **Wikipedia und URL-Text.** Kein edu-sharing. Eine
  edu-sharing-Client-Bibliothek, die beliebige URLs abruft, ist eine
  SSRF-Oberfläche in einem Paket, in dem niemand danach sucht. Wer beides
  braucht, nimmt `httpx` direkt — dieselbe Abhängigkeit, die diese Bibliothek
  ohnehin schon mitbringt.
- **Das `:::`-Blockformat der WLO-Skill-Registry.** Eine Dokumentkonvention von
  WLO, keine Eigenschaft von edu-sharing. Der Weg zum Dokument ist generisch und
  wird dokumentiert; das Parsen bleibt beim Aufrufer.
- **Varianten anlegen, löschen, umsortieren; Schwimmlinien bearbeiten.** Das MCP
  tut es auch nicht, und aus gutem Grund: Am Dokument validiert nichts. Gemessen
  am 09.08.2026 nahm die Eigenschaft die Zeichenkette `"not json at all"` mit
  200 an. Ein kaputtes Dokument fällt nicht hier auf, sondern später, im Page
  Builder, auf einer öffentlichen Seite.
- **Gespeicherte Suchen der Widgets ausführen.** `resolve_widgets` gibt die
  Suchparameter aus und führt sie nicht aus. Sie enthalten `virtual:`-Felder,
  die die MDS nicht kennt, und `flows.search` ist mit ausdrücklichen Filtern das
  bessere Werkzeug. Was ausgeführt werden kann, ohne zu raten, ist die feste
  Liste `sortedNodeIds` — die wird aufgelöst.

## Ansatz

Drei Wege wurden erwogen:

**A — alles als Ablauf.** Nur `flows.page()` und `flows.find_pages()`, kein
API-Objekt; das Parsen lebt im Ablauf.
*Für:* am wenigsten Code. *Gegen:* der Schreibvorgang (`render`) hat keinen
sinnvollen Platz in einem Ablaufmodul, und die Bibliothek hätte zum ersten Mal
eine Datenstruktur, die es nur als `dict` gibt. Bricht die Zweischichtigkeit,
die überall sonst gilt.

**B — Eigenschaften roh durchreichen.** Kein eigenes Modul; die Dokumentation
zeigt, wie man `ccm:page_config` selbst parst.
*Für:* null neuer Code. *Gegen:* verschiebt genau die neun gemessenen
Eigenheiten oben zurück zum Aufrufer. Das ist der Zustand vor dieser
Bibliothek.

**C — eigenes Modul, wie `permissions.py`.** Wertobjekte plus ein
Zugriffsobjekt an `Node`, dazu zwei Abläufe für die JSON-Ebene.
*Für:* folgt dem Muster, das für Rechte, Kommentare, Vorschläge und Workflow
schon steht; der Schreibvorgang hat einen Ort; die Abläufe bleiben dünn.
*Gegen:* ein Modul mehr.

**Gewählt: C.** Der Page Builder ist eine eigene Verantwortung mit eigenem
Dokumentformat — dasselbe Argument, mit dem `flows/tree.py` ein eigenes Modul
wurde.

## Architektur

### Dateien

| Datei | Verantwortung | ± Zeilen |
|---|---|---|
| `src/edusharing/pages.py` | neu — Page-Builder-Dokument: lesen, prüfen, `default` setzen | +270 |
| `src/edusharing/flows/pages.py` | neu — `page()`, `find_pages()` | +215 |
| `src/edusharing/nodes.py` | `Node.page` (Zugriffsobjekt) | +14 |
| `src/edusharing/collections.py` | `propertyFilter=-all-` in Leg A | +9 |
| `src/edusharing/flows/__init__.py` | Fassade: `page`, `find_pages` | +26 |
| `src/edusharing/_sync.py` | `SyncNodePage` + zwei Ablauf-Durchgriffe | +48 |
| `src/edusharing/__init__.py` | Ausfuhr der vier Wertobjekte | +6 |
| `tests/test_pages.py` | neu | +240 |
| `tests/test_flows_pages.py` | neu | +150 |
| `docs/examples/14_flow_page.py` | neu | +80 |

`pages.py` bleibt damit unter 300 Zeilen. Sollte es beim Schreiben darüber
hinausgehen, ist die Naht das Dokumentformat gegen den Zugriff: `pages.py`
behält Parsen und Prüfen, `NodePage` zieht nach `nodes.py`. Nicht vorab
aufteilen — die beiden ändern sich zusammen.

### Datenfluss

```
Node (Sammlung)
  └─ ccm:page_config_ref ──▶ Ordner (ccm:map)
                               ├─ ccm:page_config  {"variants":[…], "default": …}
                               └─ children ──▶ Varianten (ccm:map)
                                                 └─ ccm:page_variant_config
                                                      └─ structure.swimlanes[]
                                                           └─ grid[] {item, nodeId}
                                                                        └─▶ Widget-Knoten
                                                                             └─ ccm:widget_config
```

Lesen: 2 Anfragen (Ordner + Kinderliste). Mit `resolve_widgets`: +1 je
Stapel von Widget-Knoten, gebündelt über `nodes.get` je Knoten — begrenzt durch
`max_widgets` (Vorgabe 24).

Schreiben: 1 Leseanfrage (aktuelles Dokument), 1 Schreibanfrage, 1 Rücklesung.

### Öffentliche Schnittstellen

```python
# pages.py
@dataclass(frozen=True)
class SwimlaneItem:
    widget: str                 # "wlo-content-teaser"
    node_id: str | None         # Store-Ref entfernt; None ist normal

@dataclass(frozen=True)
class Swimlane:
    heading: str
    type: str                   # "container", "accordion", …
    items: tuple[SwimlaneItem, ...]

@dataclass(frozen=True)
class PageVariant:
    id: str
    title: str
    is_template: bool
    target_group: str | None
    educational_contexts: tuple[str, ...]
    intention: str | None       # aus variables: "teach" | "learn"
    education_levels: tuple[str, ...]
    swimlanes: tuple[Swimlane, ...]
    readable: bool              # False: Dokument da, aber kein JSON
    @property
    def node_ids(self) -> tuple[str, ...]

@dataclass(frozen=True)
class CuratedPage:
    collection_id: str
    folder_id: str
    variants: tuple[PageVariant, ...]   # default zuerst, dann Dokumentreihenfolge
    rendered_id: str                    # "" wenn keine festgelegt
    @property
    def rendered(self) -> PageVariant | None
    @property
    def by_position(self) -> bool       # True: keine festgelegt, es rendert variants[0]
    def variant(self, variant_id: str) -> PageVariant | None

class NodePage:
    async def get(self) -> CuratedPage | None          # None: keine Seite
    async def render(self, variant_id: str) -> CuratedPage

# nodes.py
class Node:
    @property
    def page(self) -> NodePage

# flows/pages.py
async def page(repo, collection_id: str, *, variant: str | None = None,
               resolve_widgets: bool = False, max_widgets: int = 24) -> dict
async def find_pages(repo, text: str = "", *, limit: int = 25) -> dict
```

Antwortform `flows.page`:

```python
{"collection": {"id": …, "title": …}, "folder_id": …,
 "rendered": {"id": …, "title": …, "by_position": bool},
 "variants": [{"id", "title", "is_template", "target_group",
               "educational_contexts", "intention", "education_levels",
               "readable"}],
 "swimlanes": [{"heading", "type",
                "items": [{"widget", "node_id",
                           "description"?, "node_ids"?, "search"?}]}],
 "node_ids": [...],           # flach, entdoppelt
 "resolved": bool, "truncated": bool, "reason": str}
```

Antwortform `flows.find_pages`:

```python
{"query": …, "checked": int, "hits": [{"id", "title", "url", "folder_id"}],
 "total": int, "reason": str}
```

### Abhängigkeiten

Keine neuen. `json` aus der Standardbibliothek.

## Nichtfunktionales

- **Leistung.** Lesen 2 Anfragen; Finden 1. `resolve_widgets` ist ausdrücklich
  abzuschalten und gedeckelt.
- **Sicherheit.** Der einzige Schreibvorgang ist `ccm:page_config` auf dem
  Ordner. Er wird **redigiert, nicht komponiert**: unbekannte Schlüssel bleiben
  erhalten. Er verweigert, wenn das Dokument fehlt, kein JSON ist, kein Objekt
  ist, keine `variants`-Liste hat oder die gewünschte Variante nicht darin steht
  — denn ein `default` außerhalb von `variants[]` rendert nichts, und die
  Instanz prüft davon nichts.
- **Vertrauensgrenze.** Sowohl `ccm:page_config` als auch
  `ccm:page_variant_config` sind vom Page Builder geschriebene Dokumente, die
  niemand validiert. Jeder Zugriff beim Parsen ist gegen fehlende und
  falsch getypte Schlüssel abgesichert; ein unlesbares Dokument ergibt
  `readable=False`, nie eine Ausnahme im Lesepfad.
- **Sprache.** Code, Bezeichner und Docstrings englisch; Planungsdokument und
  `*.de.md` deutsch — wie im Rest des Projekts.

## Risiken

| Risiko | Gegenmaßnahme |
|---|---|
| Schreibfenster zwischen Lesen und Schreiben — eine gleichzeitig angelegte Variante geht verloren | Nicht lösbar: die Property-Route bietet kein ETag. Im Docstring benannt, wie es das MCP tut. |
| `propertyFilter=-all-` vergrößert jede Sammlungssuche | Gemessen 33–57 Eigenschaften je Treffer. Die Knotensuche sendet ihn längst; die Asymmetrie war der Fehler, nicht der Parameter. |
| Leg B von `collections.find` hat eine feste Projektion und bleibt eigenschaftslos | Im Docstring festgehalten; `find_pages` wertet nur Treffer mit Eigenschaften und meldet `checked`. |
| Der Testzugang darf fremde Seiten nicht schreiben | Der Schreibtest baut seine eigene Seite und räumt sie ab. |

## Offene Fragen

Keine.

---

# Aufgaben

## Paket 1 — die Sammlungssuche liefert Eigenschaften

**Schritt 0: `/better-coding-workflow` aufrufen** (Skills entladen sich).

### Aufgabe 1.1 — Test: Leg A sendet `propertyFilter`

- **Dateien:** `tests/test_collections.py` (ändern)
- **Was:** Ein Mock-Test hält fest, dass `collections.find` beim
  MDS-Aufruf `propertyFilter=-all-` mitschickt und die Eigenschaften des
  Treffers bei `hit.properties()` ankommen.
- **Rot:** Der Test scheitert, weil der Parameter fehlt und `properties()` `{}` gibt.

### Aufgabe 1.2 — Parameter setzen

- **Dateien:** `src/edusharing/collections.py:145-160`
- **Was:** `"propertyFilter": "-all-"` in die Parameter von `_mds_leg`. Der
  Docstring hält fest, dass Leg B eine feste Projektion hat und deshalb
  eigenschaftslos bleibt — die Asymmetrie ist messbar und überrascht sonst.
- **Grün:** `uv run pytest tests/test_collections.py`

### Aufgabe 1.3 — Live-Beleg

- **Dateien:** `tests/test_live.py`
- **Was:** Ein lesender Live-Test sucht `Deutsch` und behauptet: mindestens ein
  Treffer trägt Eigenschaften, und mindestens einer trägt
  `ccm:page_config_ref`. Übersprungen mit klarer Begründung, wenn die Instanz
  keine kuratierte Seite hat — die Bibliothek ist instanzunabhängig, der Test
  darf es nicht vergessen.
- **Prüfen:** `uv run --env-file .env pytest tests/test_live.py -m live -k page`
- **Commit:** `fix(collections): Sammlungssuche liefert wieder Eigenschaften`

## Paket 2 — der Page Builder auf API-Ebene

**Schritt 0: `/better-coding-workflow` aufrufen.**

### Aufgabe 2.1 — Wertobjekte und Parser

- **Dateien:** `src/edusharing/pages.py` (neu), `tests/test_pages.py` (neu)
- **Was:** `SwimlaneItem`, `Swimlane`, `PageVariant` samt
  `variant_from_node(node)`. Tests zuerst, und zwar für die gemessenen
  Eigenheiten: `is_template` kommt als String; ein Grid-Element ohne `nodeId`
  bleibt erhalten; Store-Refs werden abgeschnitten; kaputtes JSON ergibt
  `readable=False` statt einer Ausnahme; `variables` liefert `intention` und
  `education_levels`, eine komma-getrennte Zeichenkette wird zerlegt.
- **Grün:** `uv run pytest tests/test_pages.py`

### Aufgabe 2.2 — `CuratedPage` und `NodePage.get`

- **Dateien:** `src/edusharing/pages.py`, `src/edusharing/nodes.py`,
  `tests/test_pages.py`
- **Was:** `CuratedPage` mit `rendered`, `by_position`, `variant()`; `NodePage.get()`
  liest Ordner und Kinder (2 Anfragen) und ordnet die Varianten: erst
  `default`, dann Dokumentreihenfolge, dann was das Dokument nie nannte.
  `Node.page` als Eigenschaft nach dem Muster von `Node.permissions`.
  `get()` gibt `None`, wenn kein `ccm:page_config_ref` da ist.
- **Grün:** `uv run pytest tests/test_pages.py`

### Aufgabe 2.3 — `NodePage.render`

- **Dateien:** `src/edusharing/pages.py`, `tests/test_pages.py`
- **Was:** Der Schreibvorgang. Liest das aktuelle Dokument frisch, redigiert nur
  `default`, schreibt über
  `POST /node/v1/nodes/-home-/{folder}/property?property=ccm:page_config`, liest
  zurück und wirft `SilentDropError`, wenn die Instanz 200 sagt und nichts
  speichert. Fünf Verweigerungen als eigene Tests: Dokument fehlt, kein JSON,
  kein Objekt, keine `variants`, Variante nicht gelistet.
- **Grün:** `uv run pytest tests/test_pages.py`

### Aufgabe 2.4 — synchrone Hülle

- **Dateien:** `src/edusharing/_sync.py`, `src/edusharing/__init__.py`,
  `tests/test_sync_surface.py`
- **Was:** `SyncNodePage` mit `get` und `render`; die vier Wertobjekte
  ausführen. Ohne diesen Schritt bekommt der synchrone Aufrufer eine Koroutine
  und keine Fehlermeldung.
- **Grün:** `uv run pytest tests/test_sync_surface.py`

### Aufgabe 2.5 — Live gegen Staging

- **Dateien:** `tests/test_live.py` (lesend), `tests/test_live_write.py` (schreibend)
- **Was:** Lesend gegen die vorhandene Seite der Sammlung Deutsch: zwei
  Varianten, neun Schwimmlinien, `by_position is True`. Schreibend gegen eine
  **selbst gebaute** Seite: Sammlung anlegen, Unterordner als
  Konfigurationsordner, zwei Varianten, `ccm:page_config` setzen, `render()` auf
  Variante 2, zurücklesen, alles wieder abräumen.
- **Prüfen:** `uv run --env-file .env pytest -m "live or write" -k page`
- **Commit:** `feat(pages): kuratierte Seiten lesen und die gerenderte Variante setzen`

## Paket 3 — Abläufe und Dokumentation

**Schritt 0: `/better-coding-workflow` aufrufen.**

### Aufgabe 3.1 — `flows.page`

- **Dateien:** `src/edusharing/flows/pages.py` (neu), `tests/test_flows_pages.py` (neu)
- **Was:** JSON-fertige Seitenstruktur. `variant=` wählt eine bestimmte, sonst
  die gerenderte. `resolve_widgets=True` liest die Widget-Knoten (gedeckelt
  durch `max_widgets`) und hängt je Item `description`, `node_ids` aus
  `sortedNodeIds` und — **unausgeführt** — `search` aus `searchText` und
  `propertyFilters`. `truncated` sagt, wenn der Deckel gegriffen hat.
- **Grün:** `uv run pytest tests/test_flows_pages.py`

### Aufgabe 3.2 — `flows.find_pages`

- **Dateien:** `src/edusharing/flows/pages.py`, `tests/test_flows_pages.py`
- **Was:** Eine Sammlungssuche, aus deren Treffern die mit
  `ccm:page_config_ref` gemeldet werden. `checked` sagt, wie viele Treffer
  überhaupt Eigenschaften trugen — sonst liest sich „keine Seite gefunden" wie
  eine Aussage über die Instanz, obwohl es eine über die Projektion war.
- **Grün:** `uv run pytest tests/test_flows_pages.py`

### Aufgabe 3.3 — Fassade und Durchgriff

- **Dateien:** `src/edusharing/flows/__init__.py`, `src/edusharing/_sync.py`,
  `tests/test_sync_surface.py`
- **Grün:** `uv run pytest`

### Aufgabe 3.4 — Dokumentation und Beispiel

- **Dateien:** `README.md`, `README.de.md`, `docs/FLOWS.md`, `docs/FLOWS.de.md`,
  `docs/ARCHITECTURE.md`, `docs/examples/14_flow_page.py` (neu)
- **Was:** 20 Abläufe statt 18, Kostentabelle ergänzt. Das Beispiel liest nur.

### Aufgabe 3.5 — Kochbuch und Abgrenzung

- **Dateien:** `README.md`, `README.de.md`
- **Was:** Zwei kurze Abschnitte. Erstens: wie man Dokumente eines Inhaltstyps
  in einer Sammlung findet und ihren Text liest — der Skills-Fall, in acht
  Zeilen mit vorhandenen Mitteln, mit dem gemessenen Hinweis, dass die
  Kinderliste dem Suchindex vorzuziehen ist (Index und Knotenspeicher sind in
  edu-sharing getrennte Systeme). Zweitens: was diese Bibliothek nicht tut und
  warum — Wikipedia, beliebige URLs, WLO-Dokumentkonventionen.
- **Prüfen:** `uv run --env-file .env python docs/examples/14_flow_page.py`
- **Commit:** `feat(flows): kuratierte Seiten finden und ausgeben`

## Abweichungen vom Entwurf (waehrend der Umsetzung)

1. **`render` sitzt am Zugriffsobjekt, nicht am Wertobjekt.** Geplant war
   `CuratedPage.render()`. Beim Bauen der synchronen Huelle fiel auf, dass
   `CuratedPage` damit das erste Wertobjekt dieser Bibliothek mit einer
   asynchronen Methode gewesen waere — und `SyncNodePage.get()` haette ein
   Objekt zurueckgegeben, dessen `render()` eine nicht abgewartete Coroutine
   ist. Genau die Falle, gegen die es die synchrone Flaeche gibt. `render` sitzt
   jetzt an `NodePage`, `CuratedPage` ist trage. Nebeneffekt: das Fenster
   zwischen Lesen und Schreiben ist auf einen Aufruf verkuerzt, weil eine
   gehaltene Seite gar nicht mehr schreiben kann.
2. **Keine Ausfuhr in `__init__.py`.** Der Entwurf sah die vier Wertobjekte im
   Paket-Namensraum vor. `Permissions`, `Ace`, `Rating` und `Comment` stehen
   dort auch nicht — sie kommen aus ihrem Modul. Symmetrie waere hier ein Bruch
   der bestehenden Konvention gewesen.
3. **`CuratedPage.document`** kam dazu: das rohe Dokument, wie gespeichert. Die
   Bibliothek modelliert zwei seiner Schluessel; die uebrigen gehoeren dem Page
   Builder, und ein Schreibvorgang muss sie durchreichen. Es offenzulegen
   kostet nichts und erspart dem Aufrufer eine zweite Anfrage.

## Verifikationsplan

| Kriterium | Befehl | Erfolg |
|---|---|---|
| Sammlungstreffer tragen Eigenschaften | `pytest tests/test_collections.py` | grün |
| Dokumentparser hält den gemessenen Eigenheiten stand | `pytest tests/test_pages.py` | grün, `pages.py` 100 % |
| Schreibvorgang verweigert fünf ungültige Fälle | `pytest tests/test_pages.py -k refuse` | grün |
| Abläufe geben JSON-fertige Werte | `pytest tests/test_flows_pages.py` | grün |
| Synchron kein Koroutinen-Leck | `pytest tests/test_sync_surface.py` | grün |
| Keine Rückschritte | `uv run pytest` | ≥ 786 grün |
| Live lesend | `pytest -m live -k page` | grün |
| Live schreibend, eigene Seite | `pytest -m write -k page` | grün, Staging danach aufgeräumt |
| Stil | `uv run ruff check src tests` | sauber |
| Beispiele | alle 14 nacheinander | Exitcode 0 |

**Rückschrittsrisiko:** Paket 1 ändert eine Anfrage, die jede
Sammlungssuche stellt. Es müssen weiterhin grün sein: `test_collections.py`,
`test_flows_discover.py`, `test_flows_tree.py`, `test_live_flows.py`.
