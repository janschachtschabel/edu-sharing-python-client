<!--
Begleitdatei, kein eigener Skill: absichtlich ohne Frontmatter. Frontmatter ist
das, was eine Datei zu einem Skill macht -- zwei Skills mit fast denselben
Ausloesern wuerden einander in die Quere kommen, und die englische Fassung
traegt die deutschen Ausloeser bereits in ihrer description. Wer daraus doch
einen eigenen Skill machen will, legt ein eigenes Verzeichnis an und setzt
dort Frontmatter.

Beide Fassungen stehen unter denselben Tests: tests/test_docs_complete.py.
-->

# edu-sharing für Python — wie man sie benutzt

*[English version: SKILL.md](SKILL.md)*

Die Bibliothek unter `github.com/…/edu-sharing-python-bib` (Paket
`edu-sharing-python-client`, Import `edusharing`). Sie umhüllt die REST-API von
edu-sharing und drei Dienste daneben, und ihr zentrales Versprechen lautet:
**ein Schreibvorgang, der nicht stattgefunden hat, wird als Fehlschlag gemeldet,
nicht als Erfolg.**

**Dieser Skill behandelt die Bibliothek.** Für die rohe REST-API, das
WLO-Datenmodell (Quelldatensatz, Spider, replicationsource), Lizenzschlüssel
oder NGSearch-Rumpffelder ist `wlo-edu-sharing-api` zuständig. Für
Instanzadressen und Variablennamen `wlo-environments`. Die sind die Wahrheit
über den *Betrieb*, dieser hier über die *Python-Oberfläche*.

**Zwei Fassungen, eine Quelle.** Die Bezeichner, um die es geht, sind englisch,
und `SKILL.md` ist die Fassung, die ein Modell lädt — sie trägt die deutschen
Auslöser schon in ihrer Beschreibung, eine deutsche Anfrage aktiviert sie also
ohnehin. Diese hier ist dieselbe Wegweisertabelle für Menschen, die lieber
deutsch lesen. Beide stehen unter denselben Tests: `tests/test_docs_complete.py`
lässt keine der beiden einen Ablauf auslassen, einen Aufruf erfinden, eine
Umgebungsvariable nennen, die der Code nicht liest, oder ins Leere verweisen.

---

## 1. Orientierung in sechzig Sekunden

```bash
uv pip install -e .        # noch nicht auf PyPI
```

```python
from edusharing import Repository

with Repository("https://repository.staging.openeduhub.net") as repo:
    result = repo.search("Bruchrechnung", limit=5)
    for hit in result.hits:
        print(hit.title, hit.url)
```

Zwei Ebenen, beide bleiben:

| | API-Ebene | Ablauf-Ebene |
|---|---|---|
| Erreichbar als | `repo.search(...)`, `repo.node(...)` | `repo.flows.search(...)` |
| Liefert | Objekte — `SearchResult`, `Node` | schlichtes `dict`, fertig für `json.dumps` |
| Gut für | Python gegen edu-sharing schreiben | die Antwort weiterreichen |
| Anfragen | ein Endpunkt je Aufruf | ein Aufruf, mehrere Endpunkte |

**Faustregel:** geht das Ergebnis an ein Modell, ein MCP-Werkzeug oder eine
HTTP-Antwort, dann `repo.flows`. Schreiben Sie den aufrufenden Code selbst,
dann die API-Ebene.

`Repository` ist blockierend, `AsyncRepository` dieselbe Oberfläche mit `await`.
Innerhalb einer Ereignisschleife die asynchrone, sonst die blockierende.

---

## 2. Die Instanz ist immer ein Parameter

**Nie eine Adresse fest verdrahten.** Die Bibliothek hat keine voreingestellte
Instanz; jeder Einstiegspunkt nimmt eine entgegen, und kein Aufruf darunter
nimmt eine eigene.

```python
repo = Repository(os.environ["EDU_SHARING_URL"], auth=(user, password))
repo = Repository.from_env()      # EDU_SHARING_URL / _USER / _PASSWORD
```

Die drei Nachbardienste bekommen jeder **seine eigene** Adresse und haben
ebenfalls keine Voreinstellung — `from_env()` verweigert ohne die Variable,
statt Daten an einen Host zu schicken, den niemand gewählt hat:

| Dienst | Klasse | Variable |
|---|---|---|
| LLM-Gateway (b-api) | `BildungsAPI` | `B_API_BASE_URL` + `B_API_KEY` |
| Textextraktion | `TextExtraction` | `EDU_SHARING_TEXT_EXTRACTION_URL` |
| Metadata Agent | `MetadataAgent` | `METADATA_AGENT_URL` |

Welche konkreten Adressen zu Staging und Produktiv gehören, steht **nicht** in
diesem Skill und nicht in der Bibliothek — siehe `wlo-environments`.

---

## 3. Welcher Aufruf beantwortet welche Frage

Die vollständige Liste mit Ein- und Ausgabeformen ist
[`docs/REFERENCE.de.md`](../../../docs/REFERENCE.de.md) /
[`docs/REFERENCE.md`](../../../docs/REFERENCE.md). Dies ist die Wegweisertabelle.

*(Die Dateiverweise hier gelten relativ zum Checkout der Bibliothek. Nach
`~/.claude/skills/` kopiert benennen sie Pfade in jenem Repositorium, nicht auf
der Platte.)*

### Finden

| Die Aufgabe | Der Aufruf |
|---|---|
| Material suchen | `repo.flows.search(text, subject=…, limit=…)` |
| Material *und* Sammlungen auf einmal | `repo.flows.search_all(text)` |
| nur Sammlungen finden | `repo.flows.find_collections(text)` |
| mehr wie dieser Knoten | `repo.flows.related(node_id, on=["subject", "level"])` |
| welche Werte lässt ein Feld zu | `repo.flows.vocabulary("subject")` |
| eine schlecht formulierte Anfrage („irgendwas mit Brüchen") | `repo.flows.search(text, rerank=True)` |
| *innerhalb* einer Sammlung suchen | `repo.flows.search_in_collection(id, text)` |
| Sammlungen mit kuratierter Seite finden | `repo.flows.find_pages(text)` |

### Eines lesen

| Die Aufgabe | Der Aufruf |
|---|---|
| alles über einen Knoten, als JSON | `repo.flows.describe(node_id)` |
| mehrere Knoten auf einmal | `repo.flows.describe_many(ids)` |
| wo liegt er (Brotkrumenpfad) | `repo.flows.placement(node_id)` |
| was ist in dieser Sammlung | `repo.flows.collection_contents(id)` |
| was hängt *unter* diesem Material | `repo.flows.child_objects(node_id)` |
| was steht *daneben* | `repo.flows.relations(node_id)` |
| was liegt darunter, rekursiv | `repo.flows.browse_tree(id, depth=2)` |
| wie viel ist darin | `repo.flows.collection_stats(id)` |
| die kuratierte Landeseite | `repo.flows.page(collection_id)` |
| die Datei selbst | `node.content.download()` / `node.content.text()` |
| Text einer Seite, die das Repositorium *nicht* hat | `TextExtraction.text_of(url)` |

### Ändern

| Die Aufgabe | Der Aufruf |
|---|---|
| Material mit Vokabular anlegen | `repo.flows.add_material(title, url=…, subject=…)` |
| Material ändern | `repo.flows.update_material(node_id, title=…)` |
| Sammlung bauen und füllen | `repo.flows.build_collection(title, node_ids)` |
| vorhandenes Material in eine Sammlung legen | `repo.add_to_collection(coll_id, node_id)` |
| wieder herausnehmen (Material bleibt) | `repo.remove_from_collection(coll_id, node_id)` |
| löschen | `repo.flows.delete(node_id)` |
| Datei hochladen | `node.content.upload(data, filename=…, mimetype=…)` |
| Lösungsblatt anhängen | `node.children.add(data, filename=…, mimetype=…)` |
| zwei Materialien verknüpfen | `repo.relations.create(a, "isPartOf", b)` |
| öffentlich lesbar machen | `node.permissions.publish()` |
| Schlagwörter | `node.add_keywords([...])` / `node.remove_keywords([...])` |

### Redaktionelle Flächen (kein Ablauf — nur API-Ebene)

| Die Aufgabe | Der Aufruf |
|---|---|
| kommentieren | `node.comments.add(text)` / `.list()` / `.edit()` / `.delete()` |
| bewerten | `node.rate(4)` / `node.unrate()` |
| einen Wert **vorschlagen** statt ihn zu schreiben | `node.suggestions.propose(prop, value, reason)` |
| einen Vorschlag annehmen oder ablehnen | `node.suggestions.decide(ids, accept=True)` |
| zur Prüfung weiterreichen | `node.workflow.submit("GROUP_redaktion", "TO_BE_CHECKED")` |
| Rechte geben oder nehmen | `node.permissions.grant(who, "Read")` / `.revoke(...)` |
| Gruppen und Mitglieder | `repo.people.*` |

### Die Nachbardienste

| Die Aufgabe | Der Aufruf |
|---|---|
| ein Modell fragen | `BildungsAPI.chat(prompt)` |
| über die responses-Route fragen | `.respond(prompt, model=…)` → `.truncated` prüfen |
| das am wenigsten ausgelastete von mehreren | `.chat(prompt, model=["a", "b", "c"])` |
| wie die Modelle gerade dastehen | `.load()` → `.summary()` |
| welche Modelle gibt es | `.models()` |
| billiger denken (Vorgabe) | nichts — `reasoning_effort` steht schon auf `low` |
| mehr denken | `.chat(prompt, reasoning_effort="high")` |
| Einbettungen *(nur OpenAI)* | `.embeddings(texts)` |
| Moderation *(nur OpenAI)* | `.moderate(texts)` |
| Bildgenerierung *(nur OpenAI)* | `.images(prompt)` |
| jede andere durchgereichte OpenAI-Route | `.call("batches", body)` |
| Text hinter einer URL | `TextExtraction.text_of(url, method="simple")` |
| was in den JSON-Bereich einer Inhaltsart gehört | `MetadataAgent.content_types()` / `.schema(file)` |

### Bausteine für KI-Anwendungen

| Die Aufgabe | Der Aufruf |
|---|---|
| eine Form für Erfolg und Fehlschlag | `as_result(awaitable, format=format_results)` |
| ein Treffer als knapper Text | `format_hit(hit)` / `format_results(result)` |
| fremden Text als Daten markieren | `as_untrusted(text, label="description")` |
| Steuerzeichen entfernen | `sanitize_text(text)` / `one_line(text)` |
| eine interne Adresse ablehnen | `check_url(url)` / `is_safe_url(url)` |
| eine Änderung planen, ein Mensch bestätigt | `plan_update(node, title=…)` → `.describe()` → `.apply()` |

---

## 4. Die Fallen — worauf zu achten ist

Jede davon wurde gegen eine echte Instanz gemessen. Sie sind der Grund, warum
es diese Bibliothek gibt.

### 4.1 HTTP 200 heißt nicht, dass etwas gespeichert wurde

edu-sharing nimmt Schreibvorgänge an, die es dann verwirft. Jeder
Schreibvorgang dieser Bibliothek liest zurück und wirft `SilentDropError`,
statt Erfolg zu melden.

```python
try:
    await node.update(title="Neu")
except SilentDropError as exc:
    exc.dropped        # {"cclom:title": ["Neu"]}
```

**Wer über `repo.raw` schreibt, verliert das.** Dann selbst zurücklesen.

Bekannte Verwerfer: `relations.create(metadata=...)` (angenommen, nirgends
gespeichert) und Metadatensatz-Felder, die die Instanz nicht kennt.

### 4.2 `unresolved` ist keine Zierde

Ein Filterwert, den die Instanz nicht kennt, wird **nicht angewendet** — und
die Suche beantwortet eine weitere Frage als die gestellte.

```python
answer = await repo.flows.search("Zellen", subject="Bio")
answer["unresolved"]   # [{"field": "subject", "value": "Bio",
                       #   "suggestions": ["Biologie"]}]
```

Beim Schreiben genauso: `add_material` und `update_material` liefern
`unresolved` für Werte, die **nicht** geschrieben wurden. Das Material gibt es
dann ohne sie.

**Nie ein Ergebnis an einen Menschen oder ein Modell melden, ohne das geprüft
zu haben.**

### 4.3 `total_is_lower_bound`, `truncated`, `complete`

- `total_is_lower_bound=True` → `total` zählt *mindestens* so viele. Wer das
  als genaue Zahl meldet, behauptet eine Zahl, die keine ist.
- `browse_tree`/`search_in_collection`: `truncated=True` → der Gang hat früh
  abgebrochen. Ein leeres Ergebnis heißt dann **nicht** „es gibt keins".
- `collection_stats`: `complete=False` → die Aufschlüsselung ist eine
  Stichprobe.

`find_collections` setzt `total_is_lower_bound` immer: es führt zwei Routen
zusammen.

### 4.4 Eine Sammlung ist kein Ordner, und eine Suche lässt sich nicht darauf einschränken

- Sammlungen über `repo.create_collection` anlegen, nie als `ccm:map`-Knoten.
  Ein anders angelegter Knoten ist für den Rest des Systems keine Sammlung.
- Sammlungen bilden einen **Graphen**, keinen Baum — eine Sammlung kann
  mehrere Eltern haben. `browse_tree` sichert gegen Zyklen und sagt es über
  `truncated`.
- Es gibt keine auf eine Sammlung eingeschränkte Suche.
  `virtual:primaryparent_nodeid` antwortet mit HTTP 400, und es wäre ohnehin
  die falsche Antwort: eine kuratierte Sammlung hält *Referenzen* auf Knoten,
  deren primärer Elternteil woanders liegt. `search_in_collection` läuft ab und
  filtert lokal.
- `collection_contents` fragt **zwei** Routen. Nur das Material zu holen ließe
  eine Sammlung aus Untersammlungen leer aussehen.

### 4.5 Drei verschiedene Arten von Zugehörigkeit

| | Hält | Gelesen mit |
|---|---|---|
| Sammlung | Referenzen auf Material, das auch anderswo liegt | `collection_contents` |
| Serienobjekt | ein Dokument *unter* einem Material, ohne eigenes Leben | `child_objects` |
| Beziehung | zwei Materialien, die *nebeneinander* stehen | `relations` |

Ein Serienobjekt trägt seinen Dateinamen in `name` und ein **leeres** `title`.
Jeder andere Ablauf zeigt `title` an, wer hier danach greift, sieht nichts.

Beziehungen pflegen die Gegenrichtung automatisch: `isPartOf` von der Folge
angelegt, und die Reihe meldet `hasPart`. Eine frische Beziehung ist
`approved=False` — `relations.approve(...)` setzt es.

### 4.6 Labels gegen URIs

`node.get("ccm:taxonid")` gibt die URI. `node.labels("ccm:taxonid")` gibt
„Mathematik". `SearchHit.labels` tut dasselbe. Die Ablauf-Ebene löst die Labels
in `fields` für Sie auf.

Facetten*werte* sind URIs und tragen kein Label — `FacetValue` hat nur `value`
und `count`.

Welche Kurznamen (`subject`, `level`, …) es gibt, wird **von der Instanz
gelesen**, nicht in der Bibliothek festgelegt: `repo.searcher.field_aliases`.

### 4.7 Blättern, Grenzen und Vorgaben, die stillschweigend kürzen

- `repo.people.members(group)` hat die Vorgabe 10 und kürzt, ohne es zu sagen.
  `limit` mitgeben.
- `collection_contents` braucht `propertyFilter=-all-`, um überhaupt
  Eigenschaften zu bekommen; die Bibliothek setzt es. Über `repo.raw` müssen
  Sie es selbst setzen.
- Die zwei Methoden des Extraktionsdienstes sind **nicht** gereiht: gemessen
  lieferte `simple` einen Artikel, wo `browser` ein Cookie-Banner lieferte.
  Bringt eine nichts, ist die andere der zweite Versuch.

### 4.8 Ein Rahmenwort ruiniert eine Anfrage

Über einen Pool von 60 Knoten gemessen: `"Bruchrechnung"` traf 0 Knoten,
`"die Bruchrechnung"` traf 43. `rerank=True` weitet die Anfrage auf und bewertet
neu; das kostet mehrere Anfragen, also dafür, wenn die Anfrage von einem
Menschen oder einem Modell kommt, nicht für eine maschinell gebaute
Filteranfrage.

`rerank=True` und `offset` vertragen sich nicht — der Pool wird über die
Varianten zusammengeführt, ein Versatz darin bedeutete also nicht, was ein
Aufrufer erwartet.

### 4.9 Tote Indexeinträge

Gemessen: 4 von 25 Suchtreffern waren nicht mehr abrufbar. `describe_many`
meldet sie in `failed`, statt zu werfen — eine kürzere Liste als angefragt ist
so davon zu unterscheiden, dass es diese Knoten nicht gibt.

### 4.10 Die zwei Anbieter sind nicht austauschbar

Gemessen am 31.08.2026. `openai` bietet 132 Modelle und meldet keine
Auslastung; `academiccloud` bietet 15 und meldet `demand` 0 bis 23, was sich im
Minutentakt ändert. Beide haben `chat/completions` und `responses`. Nur OpenAI
hat `embeddings`, `moderations` und `images/generations` — die AcademicCloud
antwortet 404, und ihre Modelle erzeugen `text` und `thought`, sonst nichts.

`reasoning_effort` und `verbosity` wirken bei der gpt-5- und o-Serie und werden
von älteren OpenAI-Modellen mit 400 abgelehnt. Die AcademicCloud nimmt sie an
und ignoriert sie: gleicher Tokenverbrauch bei `low` und `high`. Ihr Hebel ist
`chat_template_kwargs`, das die Bibliothek für Qwen3 setzt.

Die Bibliothek stellt beide auf `low` und wendet sie nur an, wo sie wirken.
**Ein ausdrücklicher Wert wird nie für Sie verworfen** — er löst stattdessen
einen Fehler aus, denn eine Antwort ohne den gewünschten Aufwand sieht genauso
aus wie eine mit ihm.

Ein virtuelles Modell (`model=["a","b","c"]` oder ein Name aus
`virtual_models`) nimmt das am wenigsten ausgelastete davon. Das lohnt bei der
AcademicCloud; bei OpenAI wird daraus eine Ausweichkette in Ihrer Reihenfolge.

### 4.11 Auslastung abfragen, und wechseln statt warten

`demand` ändert sich im Minutentakt, deshalb wird die Modellliste 30 Sekunden
gemerkt. Stellen Sie das darauf ein, wie lange Ihr Prozess lebt:

```python
# Ein Skript, das eine Minute läuft: einmal fragen.
api = BildungsAPI.from_env(models_cache_seconds=CACHE_FOREVER)
print((await api.load()).summary())      # ins Startprotokoll

# Ein Dienst, der einen Tag läuft: die 30 Sekunden stehen lassen. CACHE_FOREVER
# ließe ihn nach Zahlen von vor Stunden entscheiden.
```

`load()` liefert einen `LoadReport`. **Zuerst `reports_load` lesen** — bei
OpenAI steht dort `false`, es wird gar keine Auslastung gemeldet, und die
Rangfolge ist alphabetisch statt eine Aussage über Warteschlangen.

**Wechseln schlägt Warten, solange es wohin zu wechseln gibt.** Ein 503 ist
wiederholbar, also verbrauchte ein ausgelastetes Modell bisher das volle
`max_retries` — rund 17 s bei voreingestellter Wartezeit — während ein anderes
danebenstand. Ein Kandidat bekommt jetzt `retries_before_switching`
Wiederholungen (Vorgabe 1), solange ein weiterer da ist; der letzte behält das
volle Budget. `max_retries=0` heißt weiterhin genau ein Versuch je Modell: die
Stellschraube senkt nur.

Ein 429 ist der Fall, dem das nicht hilft — die AcademicCloud begrenzt den
Schlüssel, nicht das Modell, der nächste Kandidat scheitert also genauso
schnell.

---

## 5. Hinter ein Modell stellen

### Text aus dem Repositorium darf nie als Anweisung wirken

Beschreibungen, Titel und Kommentare schreiben Fremde. Vor dem Modellkontext
umschließen:

```python
from edusharing.agent import as_untrusted, sanitize_text

as_untrusted(hit.description, label="description")
```

### Vorschlagen, nicht schreiben

Für alles, was ein Modell entschieden hat, führt der Weg über
`suggestions.propose(...)` und einen Menschen — nicht über `node.update(...)`.
Wo wirklich geschrieben werden soll: planen und den Plan zeigen.

```python
plan = await plan_update(node, title=proposed)
print(plan.describe())        # alt -> neu, für einen Menschen
await plan.apply()            # erst nach der Bestätigung
```

### Eine Form für Erfolg und Fehlschlag

```python
outcome = await as_result(repo.flows.search(text))
outcome.ok, outcome.error_type      # False, "NotFoundError"
```

`error_type` lässt ein Werkzeug „anders formulieren hilft vielleicht" von
„Zugangsdaten fehlen" unterscheiden, ohne die Meldung zu zerlegen. Fehler
tragen keinen Java-Stacktrace.

### Adressen von einem Modell sind ungeprüft

`check_url` lehnt Loopback, Link-Local und private Bereiche ab.
`BildungsAPI.call` prüft seine Route Segment für Segment —
`"../../administration/account"` wird abgelehnt statt mit dem API-Schlüssel
gesendet.

### Was nie in ein Protokoll gerät

Header, Zugangsdaten, Query-Zeichenketten und der Pfad jeder Adresse, die der
Aufrufer übergeben hat. Protokolliert wird nur, was die Bibliothek selbst
gebaut hat.

---

## 6. Wo man nachschlägt

| Frage | Datei |
|---|---|
| was genau liefert dieser Aufruf | [`docs/REFERENCE.de.md`](../../../docs/REFERENCE.de.md) · [en](../../../docs/REFERENCE.md) |
| warum tut dieser Ablauf, was er tut | [`docs/FLOWS.de.md`](../../../docs/FLOWS.de.md) · [en](../../../docs/FLOWS.md) |
| wie ist die Bibliothek gebaut | [`docs/ARCHITECTURE.de.md`](../../../docs/ARCHITECTURE.de.md) · [en](../../../docs/ARCHITECTURE.md) |
| ein lauffähiges Beispiel | `docs/examples/01…17` — siehe die README-Tabelle |
| was sich geändert hat | `CHANGELOG.md` |

Fangen Sie mit `docs/examples/10_two_levels.py` an, wenn Sie sich für eine
Ebene entscheiden: es schreibt denselben Anwendungsfall zweimal und zählt die
Anfragen, die jede Fassung sendet.

---

## 7. Prüfliste, bevor ein Werkzeug damit ausgeliefert wird

```
[ ] Instanz kommt aus der Konfiguration, nicht aus einem Literal im Code
[ ] Zugangsdaten aus Umgebung oder Vault, nie im Quelltext, nie im Protokoll
[ ] Jedes Suchergebnis: `unresolved` geprüft und weitergereicht
[ ] Jede gemeldete Zahl: `total_is_lower_bound` beachtet
[ ] Jeder Gang: `truncated` / `complete` weitergereicht
[ ] Jeder Schreibvorgang: SilentDropError behandelt, nicht verschluckt
[ ] Text aus dem Repositorium mit `as_untrusted` umschlossen
[ ] URLs von einem Modell durch `check_url` geschickt
[ ] Vom Modell entschiedene Änderungen über `suggestions.propose`, nicht `update`
[ ] Fehler als `EduSharingError` gefangen, mit `error_type` gemeldet
```

---

## 8. Verwandte Skills

| Skill | Wofür |
|---|---|
| `wlo-edu-sharing-api` | die rohe REST-API, WLO-Datenmodell, Lizenzschlüssel, NGSearch |
| `wlo-environments` | welche Adresse Staging ist, welche Produktiv; Variablennamen |
| `wlo-metadata-agent-api` | die eigenen Endpunkte des Metadata Agent |
| `wlo-bapi-llm` / `wlo-b-api-llm` | Modellliste und Anbieterverhalten des Gateways |
| `wlo-suggestions-curation` | der redaktionelle Ablauf, den `suggestions` hier speist |
| `wlo-mcp-search` / `wlo-mcp-python-client` | einen MCP-Server darüber bauen |

Widersprechen jene Skills und dieser sich über einen *Python*-Aufruf, gewinnen
dieser und `docs/REFERENCE.de.md`. Widersprechen sie sich über eine *Adresse*,
einen *rohen Endpunkt* oder das WLO-Datenmodell, gewinnen jene.
