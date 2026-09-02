# Abläufe — Anwendungsfälle in einem Aufruf

*[English version: FLOWS.md](FLOWS.md)*

Die Bibliothek hat zwei Ebenen. Sie beantworten verschiedene Fragen, und beide
bleiben.

| | API-Ebene | Ablauf-Ebene |
|---|---|---|
| Erreichbar als | `repo.search(...)`, `repo.node(...)` | `repo.flows.search(...)` |
| Liefert | Objekte — `SearchResult`, `Node` | schlichtes `dict`, fertig für `json.dumps` |
| Gut für | Python gegen edu-sharing schreiben | das Ergebnis weiterreichen |
| Aufrufe | ein Endpunkt je Aufruf | ein Aufruf, mehrere Endpunkte |

Abläufe fügen keine Fähigkeit hinzu. Alles, was sie tun, geht auch auf der
API-Ebene — mit mehr Code. Es gibt sie, weil ein MCP-Werkzeug, ein
HTTP-Endpunkt oder ein Sprachmodell kein `SearchResult` will, sondern JSON, und
weil niemand vier Endpunkte aufrufen möchte, um ein Material anzulegen.

```python
from edusharing import Repository

with Repository.from_env() as repo:
    ergebnis = repo.flows.search("Photosynthese", subject="Biologie")
    json.dumps(ergebnis)        # geht — genau darum geht es
```

Alles Folgende gibt es doppelt: `await repo.flows.…` auf `AsyncRepository` und
blockierend `repo.flows.…` auf `Repository`.

---

## Was jeder Ablauf kostet, auf einen Blick

Gemessen mit einem protokollierenden Transport am 27.08.2026. „Anfragen" ist
das, was der Ablauf an das Repositorium schickt; die API-Ebene schickt dieselben,
nur von Hand ausgeschrieben.

| Ablauf | Anfragen | Die Kette dahinter |
|---|---|---|
| `search` | 2 | Vokabular auflösen → suchen |
| `search(rerank=True)` | 1 je Variante (≤5), parallel | expandieren → je Variante suchen → im Speicher bewerten und mischen |
| `vocabulary` | 1 | Kurzname auflösen → Werte holen (zwischengespeichert) |
| `describe` | 1 | Knoten laden |
| `text` | 1–3 | Knoten laden → gespeicherter Text → (die Datei, bei `text/*`) → (die verlinkte Seite, mit Dienst) |
| `search_all` | 3–4 | Materialsuche (+1 zum Auflösen eines Filters) + Sammlungssuche (ihre zwei Wege), parallel |
| `placement` | 3 | Knoten laden (Referenz auflösen) → Weg nach oben + Sammlungen des Originals, parallel |
| `describe_many` | eine je verschiedener ID, parallel | jeden laden, die verschwundenen melden |
| `related` | 2 (+1 je aufgelöstem Filter) | Ausgang beschreiben → mit seinen Feldern suchen → Ausgang herausnehmen |
| `browse_tree` | eine je geöffneter Sammlung | Untersammlungen ablaufen, entdoppelt und gedeckelt |
| `search_in_collection` | eine je Sammlung + zwei je Sammlung für ihr Material | ablaufen → Material lesen → lokal vergleichen |
| `collection_stats` | 2, parallel | Materialliste + Untersammlungsliste → lokal auszählen |
| `page` | 3 (+1 je Widget mit `resolve_widgets`) | Sammlung laden → ihren Seiten-Ordner → dessen Varianten |
| `find_pages` | 2, parallel | beide Sammlungswege → die Treffer mit Seiten-Ref behalten |
| `find_skills` | 1, oder eine je gelesener Sammlung | Suche mit der Inhaltsart → lokal reihen |
| `skill` | 2–3 | Datensatz laden → Datei herunterladen → Ordner des Originals listen |
| `skill_registry` | 2 + eine je Eintrag | Dateien der Sammlung listen → Registry herunterladen → jeden Kopf auflösen |
| `pick_skill` | `find_skills` + `skill` | suchen → den besten laden |
| `relations` | 1 | die Verknüpfungen des Knotens lesen |
| `child_objects` | 2 | Hauptknoten laden → seine Kinder, gefiltert und sortiert |
| `find_collections` | 2, parallel; mit `parent_id` eine je geöffneter Sammlung | beide Sammlungswege → über die ID zusammenlegen → lokal filtern |
| `collection_contents` | 2, parallel | Materialliste + Untersammlungsliste |
| `add_material` | 3–6 | die Adresse (`url`) prüfen → whoami (ohne parent) → Vokabular auflösen → anlegen → einlegen (auf Wunsch) → veröffentlichen (auf Wunsch) |
| `update_material` | 3–4 | Vokabular auflösen → laden → schreiben → zurücklesen |
| `build_collection` | 1 + eine je Knoten (+2 zum Veröffentlichen) | anlegen → jeden einlegen, Fehlschläge auffangen → veröffentlichen (auf Wunsch) |
| `delete` | 2 | laden (um ihn zu benennen) → löschen |
| `accept_suggestion` | 4 | Knoten laden → Vorschläge auflisten → schreiben und zurücklesen → markieren |

Drei davon — `search`, `vocabulary`, `describe` — schicken exakt das, was die
API-Ebene schickt. Sie sparen keinen einzigen Umlauf: ihr Gewinn ist die
JSON-Form und die aufgelösten Bezeichnungen. Die übrigen verketten wirklich.

---

## Zwei Regeln, die durch jeden Ablauf gehen

**Lesbare Werte statt URIs.** In `ccm:taxonid` steht
`http://w3id.org/openeduhub/vocabs/discipline/080`. Ein Sprachmodell, das das
liest, weiß nichts. Abläufe liefern die Bezeichnungen, die das Repositorium
danebenstellt.

**Kurznamen statt Eigenschaften.** Die Ausgabeschlüssel sind die konfigurierten
Kurznamen (`subject`), nicht die edu-sharing-Eigenschaften (`ccm:taxonid`). Wer
andere Kurznamen konfiguriert, bekommt andere Schlüssel — nichts hier ist auf
ein Profil festgelegt:

```python
repo = Repository.from_env(field_aliases={"fach": "ccm:taxonid"})
repo.flows.search("Wald")["hits"][0]["fields"]     # {"fach": ["Biologie"]}
```

Voreingestellt sind `subject`, `level`, `type`, `difficulty`, `license`.

---

## `search` — Material finden

**Seit dem 02.09.2026:** `exclude_ids` lässt schon gezeigte Treffer aus — und
die Seite wird nachgefüllt, acht gewünschte und drei ausgeschlossene ergeben
also acht (bis `EXCLUSION_MAX` angefordert); `facet_limit` hebt die 20 Werte
je Facette an; `properties=["ccm:oeh_extendedType"]` trägt jede weitere
Eigenschaft unter `fields` mit ihrem vollen Namen, wie gespeichert. Jeder
Treffer nennt außerdem `preview_url`, `download_url`, `license` und `size`.

Vokabulare werden gegen den Metadatensatz dieser Instanz aufgelöst.
`subject="Biologie"` funktioniert also, ohne dass jemand den URI dahinter kennt.

**Eingabe**

```python
repo.flows.search(
    "Photosynthese",           # Volltext, entbehrlich wenn nur gefiltert wird
    subject="Biologie",        # konfigurierte Kurznamen, werden aufgelöst
    level="Sekundarstufe I",
    filters={"ccm:custom": "wert"},    # Eigenschaften ohne Kurznamen
    facets=["subject"],        # serverseitige Zählungen
    limit=10, offset=0,
)
```

**Ausgabe**

```json
{
  "query": {"text": "Photosynthese", "filters": {"subject": "Biologie"},
            "metadataset": "mds_oeh", "limit": 10, "offset": 0},
  "total": 115,
  "total_is_lower_bound": false,
  "returned": 3,
  "duplicates_removed": 1,
  "hits": [
    {
      "id": "1f71f84a-a67d-4b93-b55f-3ba4f39571d8",
      "title": "Feuerspuren im Satellitenbild",
      "url": "https://…/components/render/1f71f84a-…",
      "description": "Dynamik von Ökosystemen",
      "source_url": "https://beispiel.org/material",
      "mimetype": "text/html",
      "mediatype": "link",
      "fields": {"subject": ["Biologie"], "level": ["Sekundarstufe II"]},
      "original_id": null,
      "duplicate_ids": []
    }
  ],
  "facets": {"subject": [{"value": "…/discipline/080", "count": 57}]},
  "unresolved": [],
  "ignored": [], "warnings": [], "suggestions": []
}
```

> **`unresolved` prüfen.** Eine nicht leere Liste heißt: ein Filter ließ sich
> nicht auflösen und wurde deshalb **nicht gesendet**. Das Ergebnis ist breiter
> als angefragt und sieht trotzdem vollständig aus. Jeder Eintrag benennt das
> Feld so, wie *Sie* es genannt haben:
> `{"field": "subject", "value": "Raumschiffbau", "suggestions": ["Raumfahrt"]}`.

> **`total_is_lower_bound`** bedeutet „mindestens so viele". Wer diese Zahl als
> Tatsache weitergibt, behauptet etwas, das keine ist.

### Doppelte Treffer werden zusammengefasst

Das Repositorium legt bei jedem erneuten Import derselben Webseite einen eigenen
Knoten an. Die tragen dieselbe Quelladresse und unterscheiden sich nur im
technischen Namen — edu-sharing hängt bei Namenskollisionen „ - 2", „ - 3" an.
Wer die Liste liest, hält zwei Einträge für zwei Materialien.

Gemessen am 27.08.2026: unter 50 Treffern je ein solches Paar bei
„Photosynthese" und „Bruchrechnung", keines bei „Optik" oder „Wald". Eine
niedrige Rate — und jedes Mal ein echtes Problem.

`search` fasst sie deshalb zusammen, **standardmäßig an**, und verschweigt
nichts:

```json
{
  "returned": 49,
  "duplicates_removed": 1,
  "hits": [{"id": "a", "duplicate_ids": ["b"], "…": "…"}]
}
```

Der erste Treffer einer Gruppe gewinnt — bei `rerank` der bestbewertete. Es
zählt allein die **Quelladresse**: zwei Materialien dürfen denselben Titel
tragen und trotzdem verschieden sein, und ein Treffer ohne Quelladresse ist nie
das Duplikat von etwas.

`limit` zählt vor dem Zusammenfassen, es können also weniger als `limit` Treffer
zurückkommen; `returned` sagt wie viele. `deduplicate=False` liefert die
Rohsicht.


### `rerank=True` — die natuerlich formulierte Anfrage retten

edu-sharing UND-verknüpft jedes Wort einer Anfrage. Wörter, die nur die *Form*
einer Bitte beschreiben, stehen in fast keinem Datensatz — also leert ein
einziges davon die Trefferliste. Gemessen gegen Staging am 27.08.2026:

| Anfrage | Treffer |
|---|---|
| `Bruchrechnung` | 1591 |
| `Ich suche ein Arbeitsblatt zur Bruchrechnung` | **0** |
| `Französische Revolution` | 637 |
| `Unterrichtsstunde Französische Revolution` | **0** |

Ein Sprachmodell formuliert wie die zweite Zeile. Ohne Gegenmaßnahme meldet es
„nichts gefunden" über ein Thema mit fünfzehnhundert Datensätzen.

```python
repo.flows.search("Ich suche ein Arbeitsblatt zur Bruchrechnung", rerank=True)
# 0 Treffer -> 3 Treffer
```

Was dabei passiert: die Anfrage wird in Varianten zerlegt (die ursprüngliche,
eine ohne Rahmenwörter, eine ohne Stopwörter, eine je Synonym), parallel
gestellt, die Ranglisten werden verschmolzen und nach Text- und
Metadatenqualität neu geordnet.

**Es kostet eine Anfrage je Variante** (höchstens 5) und ist deshalb
standardmäßig aus. `offset` wird beim Neuordnen ignoriert — der Pool ist über
Varianten verschmolzen, ein Versatz hinein bedeutete nicht, was man erwartet.

Die Antwort trägt `query.reranked` und `query.variants`, damit die Reihenfolge
erklärbar bleibt.

Zwei ehrliche Grenzen:

* **Gleiche Kandidaten ergeben dieselbe Reihenfolge — nur schwanken die
  Kandidaten.** Die Bewertung ist eine reine Funktion aus Datensatz und Anfrage;
  die Position, die ein Datensatz in der Serverantwort hatte, geht bewusst
  **nicht** ein, und 15 Mischungen derselben Kandidatenmenge ergeben dieselbe
  Reihenfolge. Was schwankt, ist die Antwort des Repositoriums: gemessen liefert
  dieselbe Anfrage zweimal 25 Treffer, von denen sich **15 unterscheiden**. Zwei
  Läufe können also abweichen — dann hat sich der Index bewegt, nicht die
  Bewertung.
* **Die Wortlisten sind deutsch.** Sie sind ein Parameter, keine Konstante:

```python
from edusharing import LanguageProfile

englisch = LanguageProfile(stopwords=frozenset({"the", "of", "a"}),
                           framing=frozenset({"worksheet", "video"}),
                           synonyms={})
repo.flows.search("I need a worksheet about fractions",
                  rerank=True, language=englisch)
```

*Beispiele: [`examples/05_flow_search.py`](examples/05_flow_search.py), [`examples/08_flow_rerank.py`](examples/08_flow_rerank.py)*


**Was dahinter läuft** — eine Anfrage **je Variante**, parallel (höchstens 5):

```python
# was rerank=True ergänzt
varianten = expand_query(text, language)     # "full", "topic", "nostop", "syn"
ergebnisse = await asyncio.gather(*(         # alle auf einmal, nicht nacheinander
    repo.searcher.search(v.text, limit=pool) for v in varianten))
# danach im Speicher, ohne weitere Anfragen: gelöschte Platzhalter aussortieren,
# jeden Kandidaten nach Text- und Metadatenqualität bewerten, danach gewichten,
# welche Varianten ihn überhaupt fanden, sortieren, `limit` nehmen.
```


**Was dahinter läuft** — 2 Anfragen, dieselben zwei wie auf der API-Ebene:

```python
# was repo.flows.search("Photosynthese", subject="Biologie") tut
uri = await repo.vocab.resolve("ccm:taxonid", "Biologie")    # 1. Label -> URI
ergebnis = await repo.searcher.search("Photosynthese",       # 2. die Suche
                                      filters={"ccm:taxonid": uri})
# danach ohne weitere Anfragen: SearchResult -> dict, DISPLAYNAME-Werte statt
# URIs, Kurznamen als Schlüssel, unaufgelöste Filter in Ihren eigenen Worten
# benannt.
```

Hier wird kein Umlauf gespart. Der Gewinn ist die JSON-Form und dass ein
unauflösbarer Filter gemeldet statt stillschweigend fallengelassen wird.

---

## `search_all` — Material *und* Sammlungen auf einmal

**Seit dem 02.09.2026:** `include_pages=True` fügt einen dritten Topf hinzu,
`pages` — die Sammlungstreffer mit redaktioneller Seite (`find_pages`), um den
Preis einer zweiten Sammlungssuche. `properties=` wirkt auf beide Töpfe.

Wer ein Repositorium nach einem Thema fragt, meint meist beides: die einzelnen
Materialien und die Sammlungen, in denen jemand schon zusammengestellt hat, was
dazugehört. Der `wlo-mcp-sc` macht das zu seinem Standardeinstieg, und das ist
die richtige Vorgabe.

**Eingabe**

```python
repo.flows.search_all("Zellteilung", subject="Biologie", limit=5)
```

**Ausgabe**

```json
{
  "query": {"text": "Zellteilung", "metadataset": "mds_oeh", "limit": 5},
  "materials": {
    "total": 42, "total_is_lower_bound": false, "returned": 5,
    "duplicates_removed": 0, "hits": [...], "facets": {}, "unresolved": []
  },
  "collections": {
    "total": 7, "total_is_lower_bound": true, "returned": 3,
    "hits": [...], "filters_ignored": ["subject"], "error": ""
  }
}
```

Die beiden bleiben in **getrennten Körben**. Sie in eine Rangfolge zu mischen
hieße, Unvergleichbares zu vergleichen, und ihre Zählungen bedeuten nicht
dasselbe: die der Sammlungen ist eine Untergrenze (zwei Wege werden
zusammengeführt), die des Materials nicht. `limit` gilt je Korb, damit keiner
den anderen verdrängt.

> **`collections.filters_ignored` lesen.** Die Sammlungsabfrage akzeptiert
> `ngsearchword` und sonst nichts — jedes weitere Kriterium endet in
> `400 DAOValidationException`. Ein Filter verengt also den Material-Korb und
> **nicht** den anderen. Ihn auf die eine Seite anzuwenden und stillschweigend
> nicht auf die andere hieße, eine Einschränkung zu behaupten, die es nie gab —
> deshalb werden die Namen der nicht angewandten Filter gemeldet.
>
> **Und `collections.error` lesen.** Fällt die Sammlungssuche ganz aus,
> kommt der Korb leer zurück und nennt dort den Grund — die Materialtreffer
> kommen trotzdem an. Sie zu verlieren, weil der andere Endpunkt weg war,
> hieße eine Antwort wegzuwerfen, die es gab; dieselbe Grenze zieht
> `collections.find` schon zwischen seinen eigenen zwei Wegen. Fällt die
> **Materialsuche** aus, wirft der Ablauf sehr wohl: diesen Korb leer
> zurückzugeben behauptete, es gebe nichts.

**Was dahinter läuft** — 3 Anfragen, gemeinsam gesendet (4, wenn ein Filter
aufgelöst werden muss):

```python
# was repo.flows.search_all("Zellteilung") tut
materials, collections = await asyncio.gather(
    find.search(repo, "Zellteilung"),            # 1. ngsearch
    find.find_collections(repo, "Zellteilung"),  # 2.+3. ihre beiden Wege
)
```

Genau das, was zwei getrennte Aufrufe senden — der Ablauf spart die Runde nur
insofern, als die drei gemeinsam hinausgehen statt nacheinander.

---

## `vocabulary` — welche Werte ein Feld annimmt

Damit niemand raten muss. Ein Sprachmodell, das nach Fach filtern soll, erfindet
sonst einen plausiblen Wert, und die Suche liefert stillschweigend alles.

**Eingabe**

```python
repo.flows.vocabulary("subject")            # Kurzname
repo.flows.vocabulary("ccm:taxonid")        # oder die Eigenschaft direkt
repo.flows.vocabulary("subject", locale="en")
```

**Ausgabe**

```json
{
  "field": "subject",
  "property": "ccm:taxonid",
  "values": ["Schulfächer", "Allgemein", "Alt-Griechisch", "…"],
  "count": 416
}
```

Wirft `ValidationError` bei unbekanntem Kurznamen — die Meldung nennt die
bekannten.


**Was dahinter läuft** — 1 Anfrage:

```python
# was repo.flows.vocabulary("subject") tut
prop = repo.searcher.field_aliases["subject"]      # Kurzname -> ccm:taxonid
werte = await repo.vocab.values(prop)              # die Anfrage
```

Zwischengespeichert: dasselbe Feld ein zweites Mal zu erfragen kostet nichts.

---

## `describe` — alles über einen Knoten

Seit dem 02.09.2026 trägt die Antwort auch `aspects` und `original_id` —
eine Listing-ID benennt eine Referenz, und `original_id` ist der Datensatz
dahinter, die ID, an die ein Schreibvorgang geht (`None` auf einem Original).

**Ein Zugriff**, genau wie `repo.node(node_id)` auf der API-Ebene. Dieser Ablauf
spart keinen Umlauf; er liefert ein `dict` mit bereits aufgelösten
Vokabularwerten statt eines `Node`-Objekts.

**Eingabe**

```python
repo.flows.describe("1f71f84a-a67d-4b93-b55f-3ba4f39571d8")
```

**Ausgabe** — die Form eines `search`-Treffers, dazu:

```json
{
  "id": "…", "title": "…", "url": "…", "fields": {"subject": ["Biologie"]},
  "name": "material.pdf",
  "type": "ccm:io",
  "access": ["Read", "Write", "Delete"],
  "public": true,
  "has_content": true,
  "keywords": ["Photosynthese", "Zelle"],
  "properties": {"ccm:wwwurl": ["…"], "…": "…"}
}
```

In `properties` stehen die rohen edu-sharing-Eigenschaften. Der Ablauf ist also
keine Sackgasse, sobald ein Feld keinen Kurznamen hat.

> **Der Suchindex kann Knoten enthalten, die es nicht mehr gibt.** Gemessen am
> 27.08.2026 gegen Staging: **4 von 25** Treffern waren nicht abrufbar. Wer
> `search` und `describe` verkettet, muss mit `NotFoundError` rechnen.

---

---

**Was dahinter läuft** — 1 Anfrage:

```python
# was repo.flows.describe("abc") tut
node = await repo.node("abc")        # genau dieselbe eine Anfrage
# dann: die Vokabularfelder zu Labels auflösen, unter den Kurznamen ablegen
#       und ein dict statt eines Node zurückgeben
```

Dieser Ablauf spart keine Anfrage. Er ändert die Form der Antwort — und genau
darum geht es, wenn die Antwort weiterreisen soll.

---

## `text` — der Volltext eines Materials, und warum es keinen gibt

**Eine bis drei Anfragen.** Zuerst der eigene Text des Repositoriums
(`/textContent`); dann die Datei selbst, wenn der Datensatz eine
`text/*`-Datei trägt — gemessen am 27.08.2026 liefert `/textContent` für
Markdown und JSON nichts, obwohl die Datei Text hat; dann die verlinkte Seite
(`ccm:wwwurl`) über den Extraktionsdienst, und nur, wenn man einen übergibt:
die Bibliothek kennt keine Dienstadresse.

**Eingabe**

```python
from edusharing.extraction import TextExtraction

service = TextExtraction.from_env()          # EDU_SHARING_TEXT_EXTRACTION_URL
repo.flows.text(node_id, extraction=service, max_chars=20_000)
```

**Ausgabe**

```json
{
  "id": "1f71f84a-…",
  "title": "Bruchrechnung — Arbeitsblatt",
  "text": "Brüche addieren …",
  "source": "repository",
  "source_url": null,
  "char_count": 4312,
  "truncated": false,
  "reason": "",
  "detail": ""
}
```

`source` ist `repository`, `download`, `extraction` oder `none`. **Bei `none`
`reason` lesen**: `node_not_found`, `access_denied`, `no_text_no_url`,
`no_extraction_service` oder `extraction_failed` — und `detail` trägt die
Worte des Dienstes oder des Fehlers. Kein Text ist eine normale Antwort, kein
Fehler, und ein Modell, dem man das sagt, kann es weitersagen, statt einen zu
erfinden. `source_url` nennt die verlinkte Seite, wann immer es eine gibt,
damit ein Aufrufer ohne Dienst selbst entscheiden kann. Beispiel 15 hat das
von Hand in 215 Zeilen gemacht.

---

## `child_objects` — weitere Dokumente eines Knotens

Das Lösungsblatt zu einem Arbeitsblatt, die Handouts zu einem Unterrichtsplan.
Sie gehören **zum** Hauptdokument und stehen nicht für sich — das unterscheidet
sie vom Inhalt einer Sammlung und von einer Relation zwischen zwei
eigenständigen Knoten.

**Eingabe**

```python
repo.flows.child_objects("haupt-1")
```

**Ausgabe**

```json
{
  "id": "haupt-1",
  "count": 2,
  "children": [
    {"id": "…", "name": "loesungsblatt.pdf", "title": "Lösungen",
     "url": "https://…", "mimetype": "application/pdf",
     "has_content": true, "order": 0},
    {"id": "…", "name": "handout.pdf", "…": "…", "order": 1}
  ]
}
```

Sortiert nach `ccm:childobject_order`, dann nach Erstellungszeit. Zurückgegeben
werden nur Knoten mit dem Aspekt `ccm:io_childobject` — ein Knoten hat auch
andere Kinder, Versionen etwa, und die als Anhänge auszugeben wäre auf eine
Weise falsch, die erst auffällt, wenn eine Version in einer Download-Liste
auftaucht.

**Was dahinter läuft** — 2 Anfragen:

```python
# was repo.flows.child_objects("haupt-1") tut
node = await repo.nodes.get("haupt-1")      # 1. den Hauptknoten laden
kinder = await node.children.list()          # 2. seine Kinder, gefiltert + sortiert
```

### Serienobjekte schreiben

```python
node = await repo.node("haupt-1")
kind = await node.children.add(pdf_bytes, filename="loesung.pdf",
                               mimetype="application/pdf")
await kind.delete()                           # ab hier ein gewöhnlicher Knoten
```

`add()` sind **zwei Anfragen**: das Kind anlegen, dann die Bytes hochladen.
Schlägt der Upload fehl, wird das Kind wieder entfernt — ein Knoten ohne Inhalt
steht in jeder Liste und lädt nichts herunter.

> **Die nötige Kombination ist nicht zu erraten.** Gemessen am 27.08.2026:
> `type=ccm:io_childobject` antwortet mit HTTP 500 (den Typ gibt es nicht),
> `type=ccm:io` ohne `assocType` antwortet mit HTTP 500 (Integritätsverletzung).
> Es funktioniert `type=ccm:io` **plus** `assocType=ccm:childio` **plus**
> `aspects=ccm:io_childobject` — denn `ccm:io_childobject` ist ein *Aspekt*,
> kein Typ. Die Bibliothek setzt alle drei.

---

## `relations` — womit ein Knoten verknüpft ist

Relationen verbinden Knoten, die **nebeneinander** stehen — die Teile einer
Reihe, ein Material und das, worauf es aufbaut. Nicht zu verwechseln mit einer
Sammlung, die ein Behälter ist.

**Eingabe**

```python
repo.flows.relations("teil-1")
```

**Ausgabe**

```json
{
  "id": "teil-1",
  "count": 2,
  "relations": [
    {"type": "isPartOf", "id": "reihe", "title": "Die Reihe",
     "url": "https://…", "ai_generated": false, "approved": false},
    {"type": "references", "id": "teil-2", "title": "Folge 2",
     "url": "https://…", "ai_generated": true, "approved": false}
  ]
}
```

Jeder Eintrag benennt den Knoten am *anderen* Ende, aus Sicht des angefragten.

> **`ai_generated` und `approved` gehören zusammen gelesen.** Eine Verknüpfung,
> die eine Maschine vorschlug und niemand bestätigte, ist ein Vorschlag, keine
> Tatsache. Die API ist ausdrücklich dafür gebaut: ein Modell darf vorschlagen,
> ein Mensch gibt frei.

**Was dahinter läuft** — 1 Anfrage:

```python
# was repo.flows.relations("teil-1") tut
relationen = await repo.relations.of("teil-1")   # GET /relation/v1/-home-/{id}
```

### Relationen schreiben

Dafür gibt es keinen Ablauf — es ist je ein Aufruf auf der API-Ebene:

```python
await repo.relations.create("teil-1", "isPartOf", "reihe")
await repo.relations.create("teil-1", "references", "teil-2", ai_generated=True)
await repo.relations.approve("teil-1", "references", "teil-2")   # ein Mensch bestätigt
await repo.relations.delete("teil-1", "references", "teil-2")
```

**Die Gegenrichtung wird für Sie geführt.** Wer `isPartOf` von Teil zu Reihe
anlegt, sieht an der Reihe `hasPart` — gemessen, ohne sie zweimal zu setzen.
Sieben Typen lassen sich anlegen:

`isPartOf` · `isBasedOn` · `references` · `isDuplicateOf` · `requires` ·
`replaces` · `hasFormat`

Die übrigen fünf (`hasPart`, `isBasisFor`, `isRequiredBy`, `isReplacedBy`,
`isFormatOf`) entstehen als deren Gegenrichtung und sind nur lesbar. Wer einen
davon direkt setzen will, bekommt einen HTTP 400 ohne erkennbaren Grund — die
Bibliothek lehnt vorher ab und nennt den passenden.

---

## `placement` — wo ein Knoten liegt, und wer ihn kuratiert hat

**Eine Listing-ID ist eine Referenz.** Seit dem 02.09.2026 wird der Knoten
zuerst gelesen und die Sammlungen werden für den Datensatz dahinter
erfragt: gegen Staging gemessen antwortet `/usage` einer Referenz-ID mit
leerer Liste und dem Original mit den Sammlungen, in denen es liegt — dieser
Ablauf meldete „in keiner Sammlung" für Material, das in zweien liegt. Die
Antwort trägt `original_id` (`None` auf einem Original). Ein Knoten, der
sich nicht lesen lässt, fügt `{part: "original"}` zu `failed` hinzu; die
Sammlungen werden dann mit der ID wie übergeben erfragt.

Zwei Fragen, die sich ähneln und es nicht sind. **Wo er liegt** ist sein Ordner,
und dessen Ordner. **Wer ihn kuratiert hat** sind die Sammlungen, die eine
Referenz halten — und eine Sammlung verweist auf Knoten, deren eigenes
Elternteil ganz woanders liegt. Ein Knoten in zehn Sammlungen hat trotzdem genau
eine Elternkette.

**Eingabe**

```python
repo.flows.placement("1f71f84a-a67d-4b93-b55f-3ba4f39571d8")
```

**Ausgabe**

```json
{
  "id": "1f71f84a-…",
  "title": "Feuerspuren im Satellitenbild",
  "path": [
    {"id": "…", "title": "Fachportale", "type": "ccm:map"},
    {"id": "…", "title": "Biologie", "type": "ccm:map"}
  ],
  "collections": [
    {"id": "…", "title": "Ökosysteme", "type": "ccm:map"}
  ],
  "scope": "COLLECTION",
  "failed": []
}
```

`path` läuft **von oben nach unten**, fertig zum Anzeigen — anders als
`node.parents()`, das die Antwort des Endpunkts spiegelt und den nächsten zuerst
gibt. Live gemessen: `WLO > Biologie > Pflanzen: Form & Funktion`.

> **`failed` benennt die Hälfte, die nicht geantwortet hat.** Die beiden
> Endpunkte fallen unabhängig voneinander aus, und bei fremdem Material tut es
> meistens einer: gemessen am 28.08.2026 antwortet `/parents` für Material aus
> einer Suche mit *500 AccessDeniedException*, während derselbe Endpunkt bei
> einem eigenen Knoten ein sauberes 403 liefert. Von 20 Materialtreffern traf
> das 18 — und die Sammlungshälfte antwortete jedes Mal.
>
> Eine verweigerte Hälfte wird deshalb gemeldet, nicht geworfen: `path` kommt
> leer zurück, und in `failed` steht
> `{"part": "path", "reason": "PermissionDeniedError: …"}`. Erst wenn **beide**
> Hälften ausfallen, wirft der Ablauf — nichts zu berichten ist kein
> Teilergebnis, und eine leere Antwort behauptete, der Knoten liege nirgends.

> **`scope` lesen.** Es benennt den Baum, in dem der Pfad liegt — gemessene
> Werte sind `COLLECTION` für den kuratierten Baum und `MY_FILES` für die
> eigenen Ordner — und damit auch, wo der Pfad endet: an der Grenze dessen, was
> das Konto lesen darf. Gemessen am 28.08.2026: den vollständigen Pfad
> zu verlangen (`fullPath=true`) endet für ein gewöhnliches Konto mit **HTTP
> 403**, weil er durch Bereiche führt, auf die es keinen Zugriff hat. Die
> Bibliothek verlangt ihn deshalb nicht und meldet stattdessen, wie weit die
> Antwort reicht — statt einen abgeschnittenen Pfad als vollständigen
> durchgehen zu lassen.

**Was dahinter läuft** — 2 Anfragen, gemeinsam gesendet:

```python
# was repo.flows.placement("abc") tut
ancestry, collections = await asyncio.gather(
    placement.ancestry_of(repo.nodes, "abc"),     # 1. GET …/parents
    placement.collections_of(repo.nodes, "abc"),  # 2. GET /usage/v1/…/collections
)
```

Nicht drei: die parents-Antwort trägt den Knoten selbst als ersten Eintrag, der
Titel kommt also mit. Die Bibliothek nimmt diesen Eintrag aus `path` heraus — ein
Knoten ist nicht sein eigener Vorfahre.

Auf der API-Ebene dieselben zwei, als Objekte:

```python
node = await repo.node("abc")
for ordner in await node.parents():        # der nächste zuerst
    print(ordner.title)
for sammlung in await node.collections():
    print(sammlung.title, sammlung.is_public)
```

---

## `find_collections` — Sammlungen suchen

**Seit dem 02.09.2026 lässt sich die Suche eingrenzen — lokal.** Der
Sammlungsendpunkt nimmt ein Suchwort und sonst nichts (gemessen); `subject=`,
`level=` und die anderen Kurznamen werden aufgelöst und gegen die
Eigenschaften jedes Treffers geprüft; ein Treffer ohne Eigenschaften lässt
sich nicht beurteilen und zählt in `unjudged`. Sammlungstreffer tragen die
URIs, aber keine `_DISPLAYNAME`-Labels (gemessen), `fields` bleibt bei ihnen
also leer — die Eigenschaft selbst holt `properties=["ccm:taxonid"]`.
`parent_id` sucht nicht: die Untersammlungen darunter werden gegangen (zwei
Ebenen) und `text` gegen ihre Titel geprüft, die nähere Ebene zuerst; leeres
`text` listet alle.

Sammlungen sind die Art, wie edu-sharing Material für den Unterricht bündelt.
Sie zu finden ist eine andere Frage als einzelne Materialien zu finden — und ein
anderer Endpunkt.

**Eingabe**

```python
repo.flows.find_collections("Physik", limit=10)
```

**Ausgabe** — dieselbe Form wie `search`, mit `query.kind` auf `"collections"`.

> **`total_is_lower_bound` ist hier immer wahr.** Die Sammlungssuche fragt zwei
> Wege ab und legt sie zusammen; die Zahl zählt mindestens so viele, womöglich
> mehr.
>
> **`limit` deckelt, was zurückkommt, und beide Wege kommen durch den Deckel.**
> Jeder Weg wird nach `limit` gefragt, und die zusammengeführte Liste wird im
> Wechsel genommen, bevor sie geschnitten wird — `limit=10` gibt also etwa fünf
> aus jedem statt zehn aus dem ersten. Die Aneinanderreihung zu schneiden würde
> den zweiten Weg bei jeder breiten Anfrage verstummen lassen, und er findet
> nachweislich Sammlungen, die der erste nicht findet.


**Was dahinter läuft** — 2 Anfragen, parallel:

```python
# was repo.flows.find_collections("Physik") tut
ergebnis = await repo.collections.find("Physik")
#   was intern beide Wege gleichzeitig abfragt und über die Knoten-ID zusammenlegt:
#     POST /search/v1/queries/-home-/{mds}/collections
#     GET  /collection/v1/collections/-home-/search
```

Zwei Wege, weil keiner allein vollständig ist — deshalb ist `total` auch nur
eine untere Schranke.

---

## `collection_contents` — eine Sammlung öffnen

**Seit dem 02.09.2026:** `properties=["ccm:oeh_extendedType"]` trägt weitere
Eigenschaften jedes Eintrags unter `fields`, wie gespeichert — gemessen trägt
ein Listing die Inhaltsart, und `fields` verschwieg sie.

**Eingabe**

```python
repo.flows.collection_contents("c32b0498-…", limit=20, offset=0)
```

**Ausgabe**

```json
{
  "id": "c32b0498-…",
  "materials": [{"id": "…", "title": "…", "url": "…", "fields": {…}}],
  "collections": [{"id": "…", "title": "Untersammlung", "url": "…", "fields": {}}],
  "total_materials": 26,
  "returned_materials": 20
}
```

Material und Untersammlungen, weil eine Sammlung beides enthält. Gemessen am
27.08.2026 an einer Sammlung mit zwei Untersammlungen: fragt man nur das
Material ab (`filter=files`), kommen **null** Knoten zurück — die Sammlung sieht
leer aus.

Materialien tragen dieselbe Form wie Suchtreffer; niemand muss zwei
Trefferformate auseinanderhalten.


**Was dahinter läuft** — 2 Anfragen, parallel:

```python
# was repo.flows.collection_contents(cid) tut
material, kinder = await asyncio.gather(
    repo.raw.json("GET", f"/node/v1/nodes/-home-/{cid}/children",
                  params={"filter": "files", "maxItems": limit}),
    repo.raw.json("GET", f"/collection/v1/collections/-home-/{cid}"
                         "/children/collections", params={"maxItems": limit}),
)
```

Von Hand geschrieben sind das zwei Wartezeiten statt einer — und der zweite
Endpunkt wird leicht ganz vergessen.

---

## `describe_many` — mehrere Knoten auf einmal

**Eingabe**

```python
repo.flows.describe_many(["abc-…", "def-…", "ghi-…"])
```

**Ausgabe**

```json
{
  "requested": 3,
  "found": 2,
  "nodes": [{"id": "abc-…", "title": "…", "…": "…"}],
  "failed": [{"id": "ghi-…", "reason": "NotFoundError: HTTP 404 …"}]
}
```

`nodes` behält die Reihenfolge der Anfrage, damit sich die Antwort mit der
Eingabe zusammenbringen lässt. Doppelte IDs werden einmal geholt.

> **Ein fehlender Knoten wird gemeldet, nicht geworfen.** Gemessen am
> 27.08.2026: **4 von 25** Treffern des Suchindex waren nicht mehr abrufbar.
> Ein Index, der seine Knoten überlebt, ist hier der Normalfall — und wer die
> ganze Liste verliert, weil einer fehlt, kann ein Suchergebnis nicht
> weiterverarbeiten.

**Was dahinter läuft** — eine Anfrage je verschiedener ID, gemeinsam gesendet:

```python
# was repo.flows.describe_many(["a", "b"]) tut
results = await asyncio.gather(*(describe(repo, i) for i in ["a", "b"]))
# jeder Fehlschlag wird gefangen und gemeldet, nicht geworfen
```

---

## `related` — mehr Material wie dieses

**Keine Relation.** `flows.relations` gibt die Verknüpfungen, die jemand
*behauptet* hat. Dieser Ablauf errechnet eine *Ähnlichkeit*: Fach und Stufe des
Ausgangsknotens werden zu Filtern einer gewöhnlichen Suche, und der Knoten
selbst fällt aus dem Ergebnis. Beides heißt „verwandt", und der Unterschied
zählt.

**Eingabe**

```python
repo.flows.related("abc-123", on=("subject", "level"), limit=10)
```

**Ausgabe**

```json
{
  "seed": {"id": "abc-123", "title": "Zellteilung"},
  "based_on": {"subject": ["Biologie"], "level": ["Sekundarstufe I"]},
  "hits": [{"id": "…", "title": "…", "…": "…"}],
  "unresolved": [],
  "reason": ""
}
```

> **`based_on` lesen.** Ohne diese Angabe lässt sich die Ähnlichkeit nicht
> beurteilen. Und `unresolved`: ein Wert, den die Instanz nicht auflösen
> konnte, hat die Suche **nicht** verengt — das Ergebnis ist breiter, als es
> aussieht.

Trägt der Ausgangsknoten keines der Felder, ist `hits` leer und `reason` sagt
es. Eine ungefilterte Suche beantwortete „mehr davon" mit irgendetwas.

`on` ist eine Vorgabe, keine Festlegung — welche Kurznamen es überhaupt gibt,
entscheidet der Metadatensatz der Instanz.

**Was dahinter läuft** — 2 Anfragen plus Vokabular:

```python
# was repo.flows.related("abc") tut
seed = await describe.describe(repo, "abc")           # 1. laden
found = await find.search(repo, None, **based_on)     # 2. seine Felder als Filter
hits = [h for h in found["hits"] if h["id"] != "abc"] # den Ausgang herausnehmen
```

---

## `browse_tree` — die Sammlungen unter einer Sammlung

**Eingabe**

```python
repo.flows.browse_tree("abc-123", depth=2, max_collections=50)
```

**Ausgabe**

```json
{
  "id": "abc-123",
  "collections": [
    {"id": "…", "title": "Biologie", "collections": [
      {"id": "…", "title": "Zellbiologie", "collections": []}
    ]}
  ],
  "opened": 3,
  "truncated": false
}
```

> **Sammlungen bilden einen Graphen, keinen Baum.** Eine Untersammlung kann
> unter mehreren Elternteilen hängen, und zwei können untereinander hängen. Der
> Lauf entdoppelt nach ID — ohne das läuft er im Kreis — und deckelt, wie viele
> er öffnet. **`truncated` lesen**: ein abgeschnittener Baum darf sich nicht
> wie ein vollständiger lesen.

Nur die Sammlungen. Ihr Material ist eine zweite Anfrage je Knoten —
`collection_stats` zählt es, `collection_contents` listet es.

**Was dahinter läuft** — eine Anfrage je geöffneter Sammlung:

```python
# was repo.flows.browse_tree("abc", depth=2) tut
GET /collection/v1/collections/-home-/abc/children/collections
# dann dasselbe je Kind, bis zur Tiefe, unter Auslassung schon gesehener IDs
```

---

## `search_in_collection` — etwas in einer Sammlung finden

**Seit dem 02.09.2026:** `properties=["ccm:oeh_extendedType"]` trägt weitere
Eigenschaften jedes Eintrags unter `fields`, wie gespeichert — gemessen trägt
ein Listing die Inhaltsart, und `fields` verschwieg sie.

**Eingabe**

```python
repo.flows.search_in_collection("abc-123", "zelle", depth=2)
```

**Ausgabe**

```json
{
  "query": "zelle",
  "hits": [{"id": "…", "title": "Zellteilung", "…": "…"}],
  "searched": 4,
  "unreadable": 0,
  "truncated": false
}
```

> **`unreadable` zählt die Untersammlungen, die sich verweigert haben.**
> Der Gang findet sie in den Antworten ihrer Eltern, die Liste enthält also
> auch Sammlungen, die dieses Konto nie geöffnet hat und deren Rechte es
> nicht kennt. Ein 403 unter fünfundzwanzig machte aus einer Teilantwort
> früher gar keine; jetzt wird der Rest durchsucht und die Zahl steht neben
> `truncated` — aus demselben Grund: stilles Abschneiden liest sich wie
> Vollständigkeit.

> **Eine Suche lässt sich nicht auf eine Sammlung eingrenzen.** Drei Mal
> gemessen — vom `wlo-mcp-sc` am 17.07.2026, hier am 27. und 28.08.2026 —
> antwortet `ngsearch` mit `virtual:primaryparent_nodeid` mit HTTP 400. Es wäre
> auch die falsche Antwort: eine Sammlung hält *Referenzen* auf Knoten, deren
> eigenes Elternteil woanders liegt — eine nach Elternteil eingegrenzte Suche
> verfehlte genau die kuratierten. Also wird gelaufen und lokal verglichen.

Verglichen werden Titel, Beschreibung und die aufgelösten Feldwerte — was ein
serialisierter Treffer wirklich trägt. Für Volltext über den ganzen Bestand ist
`flows.search` das bessere Werkzeug.

> **`truncated` lesen.** Ein leeres Ergebnis aus einem Lauf, der früh
> aufgehört hat, ist kein „gibt es nicht".

**Was dahinter läuft** — eine Anfrage je Sammlung für den Lauf, zwei weitere je
Sammlung für ihr Material:

```python
# was repo.flows.search_in_collection("abc", "zelle") tut
tree = await browse_tree(repo, "abc", depth=2)        # der Lauf
pages = await asyncio.gather(*(collection_contents(repo, i) for i in ids))
hits = [h for page in pages for h in page["materials"] if passt(h)]
```

---

## `collection_stats` — wie viel darin liegt, und wovon

**Eingabe**

```python
repo.flows.collection_stats("abc-123", sample=100)
```

**Ausgabe**

```json
{
  "id": "abc-123",
  "materials": 342,
  "collections": 7,
  "sampled": 100,
  "complete": false,
  "by": {"subject": {"Biologie": 61, "Chemie": 22}, "level": {"Sekundarstufe I": 74}}
}
```

Die Zahlen sind genau — sie kommen aus der Paginierung. **Die Aufschlüsselung
ist eine Stichprobe**: `sampled` sagt, über wie viele Datensätze ausgezählt
wurde, `complete`, ob das alle waren. Und **die Zähler teilen sie nicht auf**:
ein Feld ist mehrwertig, live gemessen trugen 15 Materialien zusammen 25
Stufenangaben. Jeder Zähler sagt, wie viele Datensätze einen Wert nennen. Eine Aufschlüsselung über hundert von
dreihundert ist nützlich; sie für das Ganze zu halten nicht.

> **Nicht über eine Facettenabfrage.** Eine Sammlung kuratiert *Referenzen* auf
> Knoten, deren primäres Elternteil woanders liegt — eine nach Elternteil
> eingegrenzte Facette liefert für sie nichts. Der Kinder-Endpunkt gibt die
> referenzierten Dateien mit ihren `*_DISPLAYNAME`-Labels zurück, also ist das
> lokale Auszählen richtig und lesbar zugleich.

**Was dahinter läuft** — 2 Anfragen:

```python
# was repo.flows.collection_stats("abc") tut
page = await collection_contents(repo, "abc", limit=100)   # Material + Untersammlungen
# dann page["materials"] nach ihren aufgeloesten Feldwerten auszaehlen
```

---

## `page` — die kuratierte Seite, die eine Sammlung rendert

Der Page Builder von edu-sharing: eine Sammlung kann eine Startseite tragen,
aufgebaut aus *Schwimmlinien*, jede mit Widgets, jedes Widget auf einen Knoten
zeigend. WirLernenOnline nennt das „Themenseite“; daran ist nichts von WLO, und
darum benutzt dieser Ablauf das Wort nicht.

**Eingabe**

```python
repo.flows.page("abc-123")                       # die Variante, die rendert
repo.flows.page("abc-123", variant="v-2")        # eine bestimmte
repo.flows.page("abc-123", resolve_widgets=True) # + was jedes Widget hält
```

**Ausgabe**

```json
{
  "collection": {"id": "abc-123", "title": "Deutsch", "url": "https://…"},
  "folder_id": "f2020460-…",
  "rendered": {"id": "a95029c1-…", "title": "Fachportal Startseite",
               "by_position": true},
  "variants": [{"id": "a95029c1-…", "title": "Fachportal Startseite",
                "is_template": false, "target_group": null,
                "educational_contexts": [], "intention": "teach",
                "education_levels": ["…/sekundarstufe_1"], "readable": true}],
  "swimlanes": [
    {"heading": "Themenübersicht", "type": "container",
     "items": [{"widget": "wlo-collection-chips", "node_id": "4d39f9a1-…",
                "description": "Die folgenden Sammlungen …",
                "node_ids": ["69756a85-…", "cffaadfb-…"]}]}
  ],
  "node_ids": ["4d39f9a1-…"],
  "resolved": true, "truncated": false, "reason": ""
}
```

**`by_position` ist keine Zierde.** Ein Seitendokument ohne `default` rendert
die *erste* Variante seiner Liste. „Nichts festgelegt“ und „die erste
festgelegt“ sehen für den Besucher gleich aus und sind verschiedene Zustände —
und davon wegzuschalten ist zweimal ein anderer Satz.

**Eine Seite kann nichts rendern.** Gemessen am 28.08.2026: die Sammlung
`Hexen` trägt eine Seite, eine Variante, ein lesbares Dokument — mit leerer
Schwimmlinienliste. *Hat eine Seite* und *hat Inhalt* sind zwei Fragen.

**Gespeicherte Suchen werden genannt, nicht ausgeführt.** Ein Widget hält
entweder eine feste Liste (`sortedNodeIds`, wird aufgelöst) oder eine
gespeicherte Suche (`searchText` + `propertyFilters`, steht unter `search` und
bleibt liegen). Deren Filter tragen `virtual:`-Felder, die der Metadatensatz
nicht kennt; sie auszuführen hieße raten. Nimm `flows.search` mit Filtern, die
du selbst gewählt hast.

**Was dahinter läuft** — 3 Anfragen:

```python
# was repo.flows.page("abc") tut
node = await repo.node("abc")            # wegen ccm:page_config_ref
page = await node.page.get()             # Ordner + seine Kinder, 2 Anfragen
```

**Schreiben.** Welche Variante rendert, ist ein Schreibvorgang — und sofort
öffentlich sichtbar:

```python
node = await repo.node("abc-123")
page = await node.page.render("v-2")     # liest, redigiert, schreibt, liest zurück
```

Er **redigiert** das gespeicherte Dokument — jeder Schlüssel, der dem Page
Builder gehört, reist unverändert mit — und verweigert alles, was er nicht
belegen kann: kein Dokument, kein JSON, kein Objekt, keine Variantenliste,
Variante nicht gelistet. Nichts davor prüft es; gemessen speichert die
Property-Route die Zeichenkette `"not json at all"` mit einer `200`.

---

## `find_pages` — welche Sammlungen eine tragen

**Eingabe**

```python
repo.flows.find_pages("Deutsch", limit=25)
```

**Ausgabe**

```json
{"query": "Deutsch", "checked": 50, "total": 876, "total_is_lower_bound": true,
 "hits": [{"id": "69f9ff64-…", "title": "Deutsch", "url": "https://…",
           "folder_id": "f2020460-…"}],
 "reason": ""}
```

Eine Suche — zwei Wege parallel, genau das, was `find_collections` sendet.
Und eine Teilmenge davon: jede kuratierte Seite ist eine Sammlung, aber wenige
Sammlungen haben eine.

`total` zählt die Sammlungen, die getroffen haben, nicht die mit Seite — und
es ist eine **Untergrenze**, weil die Sammlungssuche zwei Routen fragt und eine
davon gar keine Gesamtzahl meldet.

**`checked` sagt, wie viele Treffer überhaupt beurteilbar waren.** Ein Weg der
Sammlungssuche hat eine feste Projektion und liefert keine Eigenschaften; an
diesen Treffern ist eine Seite nicht zu erkennen. Ohne die Zahl liest sich ein
leeres `hits` wie eine Aussage über die Instanz, obwohl es eine über die
Projektion war.

**Ein Lauf ist eine Stichprobe, kein Katalog.** Am 28.08.2026 sechsmal mit
demselben Suchwort gemessen: drei verschiedene Treffermengen, `checked`
zwischen 50 und 100. Beide Sammlungsrouten sind beteiligt, und keine ist
Obermenge der anderen.

> **Warum kein Filter?** Weil es keinen gibt. `ccm:page_config_ref` als
> Suchkriterium antwortet mit `400 DAOValidationException: Widget
> ccm:page_config_ref was not found in the mds`. Eine Seite wird aus der
> Antwort erkannt.

**Was dahinter läuft** — 2 Anfragen, parallel:

```python
# was repo.flows.find_pages("Deutsch") tut
treffer = await repo.find_collections("Deutsch", limit=25)   # beide Wege zugleich
# dann: die Treffer behalten, deren Eigenschaften ccm:page_config_ref tragen,
#       und zählen, wie viele überhaupt Eigenschaften trugen
```

Auf der API-Ebene ist dasselbe Erkennen eine Zeile:
`hit.properties().get("ccm:page_config_ref")`. Die Seite dahinter liest
`node.page.get()`.

---

## `find_skills` — welche Skills zu einer Aufgabe passen

**Eine Anfrage** repositoriumsweit (die Inhaltsart reist als Kriterium, die
Kurznamen mit ihr) oder **eine je gelesener Sammlung** mit `collection_id`
(das Listing nimmt keine Kriterien; Inhaltsart und Kurznamen werden lokal
geprüft). Gereiht: ein Begriff im Titel zählt 3, in den Schlagwörtern 2, in
der Beschreibung 1. Ein Skill, der Original und zugleich Referenz in einer
Sammlung ist, kommt einmal — als Original, die ID, an die geschrieben wird.

```python
repo.flows.find_skills("Fragen generieren", subject="Physik")
```

```json
{
  "query": {"text": "Fragen generieren", "collection_id": null, "metadataset": "mds_oeh"},
  "hits": [{"id": "…", "original_id": "…", "title": "Fragen generieren",
            "description": "…", "keywords": ["Fragen", "Quiz"], "url": "…",
            "download_url": "…"}],
  "unresolved": [],
  "truncated": false
}
```

Die Konventionen — welche Inhaltsart einen Skill kennzeichnet, wie eine
Registry sich nennt — sind `SkillConventions`, ein Parameter mit WLOs Werten
als Vorgabe. **Gemessen (02.09.2026): `mds_oeh` nimmt die Inhaltsart als
Kriterium, `-default-` weist sie zurück** — `EDU_SHARING_METADATASET` setzen
oder `metadataset=` übergeben, sonst wird kein Skill gefunden.

---

## `skill` — die Anleitung eines Skills, und was dazugehört

**Zwei bis drei Anfragen.** Der Datensatz, seine Datei per `download()` —
gemessen ist `/textContent` für Markdown leer — und mit `include_files` der
Ordner daneben: der Ordner des ORIGINALS, über eine Anfrage mehr gelesen, wenn
die ID eine Referenz war. **`files_reason` lesen**: `folder_unreadable` (403
anonym, gemessen), `no_folder` oder `too_many` mit `folder_file_count` — ein
leeres `files` heißt nicht „der Skill reist allein".

```python
repo.flows.skill(node_id)
```

```json
{
  "id": "…", "original_id": "…", "title": "Fragen generieren", "…": "…",
  "content": "# Fragen generieren\n\n…",
  "references": [{"kind": "ki-skill", "title": "Lehrprofil auswerten",
                  "url": "…/components/render/…", "node_id": "…", "offset": 412}],
  "files": [{"id": "…", "title": "vorlage.docx", "mimetype": "application/msword",
             "size": 18342, "download_url": "…"}],
  "files_reason": "",
  "folder_file_count": null
}
```

`content` ist hochgeladener Inhalt — Daten, die ein Modell abwägt, nie eine
Anweisung, der diese Bibliothek folgt. Vor dem Prompt mit `as_untrusted`
rahmen.

---

## `skill_registry` — welche Skills eine Sammlung freigegeben hat

**Zwei Anfragen plus eine je Eintrag.** Das Dateilisting der Sammlung (nie
der Suchindex — ein Datensatz kann aus dem Index fallen und im Speicher
liegen, vom MCP am 09.08.2026 gemessen), das Registry-Dokument per
`download()`, dann je genanntem Skill der Datensatz für Beschreibung und
Schlagwörter (`resolve=False` lässt das aus). Die `::: ki-skill`-Blöcke des
Dokuments sind der Katalog, seine `##`/`###`-Überschriften die
Arbeitszusammenhänge; `context="Unterricht vorbereiten"` verengt auf diese
Gruppe plus das Allgemeine, und **ein Name, der nicht passt, verengt nichts**
— `context_match` sagt `missing`, und `contexts` nennt, was es gibt.

```python
repo.flows.skill_registry(collection_id, context="Unterricht vorbereiten")
```

```json
{
  "collection_id": "…", "registry_id": "…", "registry_title": "Skill Registry",
  "markdown": "# Skills für die Sammlung Optik\n\n…",
  "entries": [{"node_id": "…", "title": "Fragen generieren", "description": "…",
               "keywords": ["Fragen"], "context": "Unterricht vorbereiten"}],
  "unresolved": [],
  "contexts": [{"title": "Unterricht vorbereiten", "level": 2,
                "path": "Unterricht vorbereiten", "instruction": "…", "skills": ["…"]}],
  "general": {"instruction": "Erst den Bestand sichten.", "skills": ["…"]},
  "ambiguous": 0, "truncated": null, "contexts_truncated": null,
  "reason": "", "context_match": "exact", "scan_truncated": null
}
```

**`reason` vor `entries` lesen**: `collection_not_found`, `no_registry` oder
`unreadable`. `no_registry` mit `scan_truncated` ist kein Befund der
Abwesenheit — das Listing wurde bei 50 Dateien abgeschnitten. Zwei
Kandidaten in einer Sammlung unterscheidet der Name oder Titel
(`skill_registry.md`, „Skillkatalog …"); entscheidet das nicht, gewinnt die
kleinste ID, und `ambiguous` sagt, wie viele es waren.

---

## `pick_skill` — suchen, reihen, laden

**`find_skills` plus ein `skill`.** Der beste Treffer mit Anleitung, die
Übrigen nach Titel und ID — damit ein Fehlgriff sichtbar bleibt.

```json
{"best": {"id": "…", "title": "…", "content": "…", "…": "…"},
 "alternatives": [{"id": "…", "title": "…", "…": "…"}],
 "reason": ""}
```

`reason` ist `no_match`, wenn nichts passte; dann ist `best` `null`.

---

## `update_material` — ändern, was schon da ist

**Eingabe**

```python
repo.flows.update_material(
    "b1a7555d-…",
    title="Neuer Titel",
    keywords=["Photosynthese"],
    subject="Physik",          # wird aufgelöst, wie beim Anlegen
)
```

**Ausgabe**

```json
{"id": "b1a7555d-…", "title": "Neuer Titel", "url": "…",
 "name": "material.pdf", "unresolved": []}
```

Geschrieben wird nur, was übergeben wurde; alles andere bleibt. Der Schreibvorgang
wird durch erneutes Lesen geprüft, sodass ein Wert, den edu-sharing stillschweigend
verwirft, einen `SilentDropError` auslöst statt als Erfolg durchzugehen.

> **Eine Änderung, bei der sich *nichts* auflösen ließ, wirft** statt
> `unresolved` zurückzugeben. Es ist nichts passiert, und ein Ergebnis, das wie
> ein Teilerfolg aussieht, legte nahe, der Rest sei angekommen. Es gibt keinen
> Rest.
**Was dahinter läuft** — 3 bis 4 Anfragen:

```python
# was repo.flows.update_material("abc", title="Neu", subject="Biologie") tut
await repo.vocab.resolve("ccm:taxonid", "Biologie")   # danach aus dem Cache
node = await repo.node("abc")
await node.update(title="Neu", properties={...})      # schreibt, liest zurück
```

Die Rückleseprobe ist nicht das Verdienst des Ablaufs — `node.update()` bringt
sie ohnehin mit.

---


## `accept_suggestion` — einen Vorschlag anwenden, zurücklesen, dann markieren

**Vier Anfragen.** Den Knoten laden, seine Vorschläge auflisten, den
vorgeschlagenen Wert mit `set_property` schreiben und zurücklesen, und erst
dann den Vorschlag als `ACCEPTED` markieren. Gemessen am 28.08.2026: Markieren
allein schreibt **nichts** in den Knoten — ein mit `decide()` angenommener
Vorschlag lässt die Eigenschaft, wie sie war; „angenommen" allein ist damit
das Protokoll von etwas, das nie passiert ist.

**Eingabe**

```python
repo.flows.accept_suggestion(node_id, suggestion_id)
```

**Ausgabe**

```json
{
  "id": "1f71f84a-…",
  "suggestion_id": "s-4410…",
  "property": "ccm:taxonid",
  "value": "http://w3id.org/openeduhub/vocabs/discipline/080",
  "applied": true,
  "status": "ACCEPTED",
  "failed": []
}
```

**`applied` lesen.** Kommt der Wert nicht an (`SilentDropError`), wird nichts
markiert, `status` bleibt `PENDING` und `failed` trägt `{part: "apply"}`; ein
schon entschiedener Vorschlag kommt mit `{part: "status"}` zurück und wird
nicht erneut angewandt. Ablehnen braucht keinen Ablauf —
`node.suggestions.decide(ids, accept=False)` rührt nur den Vorschlag an, und
genau das heißt Ablehnen.

---

## `add_material` — anlegen, mit sauberen Metadaten

**Seit dem 02.09.2026 wird `url` zuerst geprüft.** Ein zweiter Datensatz für
dieselbe Adresse ist per Definition eine Dublette; mit `if_exists="return"`
(Vorgabe) wird ein vorhandener genannt — `created` ist `False`, `existing`
trägt `{id, title, url}`, und nichts wird angelegt. `"raise"` wirft
`ConflictError`; `"create"` lässt die Prüfung aus. Ob sie laufen kann, ist
Sache des Metadatensatzes — gemessen nimmt `mds_oeh` `ccm:wwwurl` als
Kriterium an, `-default-` nicht — und wenn nicht, fällt die Vorgabe aus und
`warnings` sagt es, während `"raise"` sich weigert zu raten.

**Die Prüfung sieht, was der Index sieht.** Die Adresssuche läuft über den
Suchindex, und der hinkt dem Knotenspeicher nach: gemessen auf Staging
(02.09.2026) war ein eben angelegter Datensatz nach 5,3 Sekunden über seine
Adresse auffindbar, vorher nicht. Zwei Aufrufe zur selben Adresse innerhalb
dieser Spanne legen beide an; ein Import, der dieselbe Adresse zweimal
enthält, muss seine Eingabe selbst entdoppeln.

**Eingabe**

```python
repo.flows.add_material(
    "Photosynthese einfach erklärt",   # erforderlich
    url="https://beispiel.org/material",
    parent_id=None,                    # None → Ihr Home-Verzeichnis
    description="…",
    keywords=["Photosynthese"],
    collection_id="…",                 # gleich als Referenz einlegen
    properties={"ccm:custom": ["…"]},  # rohe Eigenschaften
    subject="Biologie",                # wird beim Schreiben aufgelöst
    level="Sekundarstufe I",
    publish=False,                     # True → für alle lesbar
)
```

**Ausgabe**

```json
{
  "id": "b1a7555d-95bc-4de7-a755-5d95bcede724",
  "title": "Photosynthese einfach erklärt",
  "url": "https://…/components/render/b1a7555d-…",
  "parent_id": "21b1ca3d-…",
  "name": "Photosynthese einfach erklärt",
  "collection": {"id": "…", "added": true},
  "public": false,
  "unresolved": []
}
```

Drei Dinge nimmt der Ablauf ab:

**Wohin es kommt.** Ohne `parent_id` landet es im Home-Verzeichnis — dessen ID
vier Ebenen tief in der Antwort von `whoami()` steckt.

**Vokabular beim Schreiben.** Lesend löste die Suche „Biologie" längst selbst
auf; schreibend musste man den URI kennen. Genau dort wiegt ein fehlender Wert
schwerer:

> **`unresolved` prüfen.** Diese Werte wurden **nicht geschrieben**. Das
> Material existiert ohne sie und sieht vollständig aus. Deshalb werden sie
> gemeldet statt fallengelassen.

**Sichtbarkeit.** Was hier entsteht, kann sein Urheber lesen und sonst niemand —
auch das Einhängen in eine öffentliche Sammlung ändert daran nichts, gemessen.

> **`public` prüfen.** `false` heißt: das Material existiert und nur du siehst
> es. `publish=True` gibt allen Leserecht. Der Schalter ist aus, weil sich
> Gelesenes nicht zurücknehmen lässt.

`cm:name` wird aus dem Titel abgeleitet, sofern `name` nichts anderes sagt; bei
einer Namenskollision wird ein Zähler angehängt statt abzubrechen.

*Beispiel: [`examples/06_flow_create.py`](examples/06_flow_create.py)*


**Was dahinter läuft** — 2 bis 4 Anfragen:

```python
# was repo.flows.add_material("T", subject="Biologie") tut
wer = await repo.whoami()                        # 1. nur wenn parent_id fehlt
uri = await repo.vocab.resolve("ccm:taxonid", "Biologie")   # 2. je Vokabularfeld
node = await repo.nodes.create(                  # 3. das Anlegen selbst
    wer.home_folder, name=name_from_title("T"), title="T",
    properties={"ccm:taxonid": [uri]})
await repo.collections.add(collection_id, node.id)          # 4. nur auf Wunsch
```

Der Name wird aus dem Titel abgeleitet; bei einer Namenskollision wird ein
Zähler angehängt statt abzubrechen.


**Was dahinter läuft** — 3 bis 4 Anfragen:

```python
# was repo.flows.update_material("n1", subject="Biologie") tut
uri = await repo.vocab.resolve("ccm:taxonid", "Biologie")   # 1. je Vokabularfeld
node = await repo.nodes.get("n1")                            # 2. laden
await node.update(properties={"ccm:taxonid": [uri]})         # 3. PUT
#     was selbst noch einmal zurückliest (4.) und einen SilentDropError wirft,
#     wenn edu-sharing den Schreibvorgang annahm und nicht speicherte.
```

---

## `build_collection` — Sammlung anlegen und füllen

**Eingabe**

```python
repo.flows.build_collection(
    "Meine Sammlung",
    description="…",
    parent_id=None,          # None → Ihre Sammlungswurzel
    node_ids=["abc-…", "def-…"],
    scope="MY",              # MY (Vorgabe) | ORGANIZATION | PUBLIC
    publish=False,           # True → für alle lesbar
)
```

**Ausgabe**

```json
{
  "id": "c32b0498-0c0e-488e-ab04-980c0ea88e7f",
  "title": "Meine Sammlung",
  "url": "https://…/components/render/c32b0498-…",
  "added": ["abc-…", "def-…"],
  "failed": [{"id": "ghi-…", "reason": "HTTP 404 … Node does not exist"}],
  "public": false
}
```

> **`scope="PUBLIC"` ist kein Leserecht.** Gemessen: der Scope entscheidet,
> wo die Sammlung gelistet wird, nicht wer sie öffnen darf — so angelegt kommt
> sie für andere trotzdem unlesbar zurück. `publish=True` erteilt das Recht.

> **Die Sammlung existiert auch dann, wenn `failed` nicht leer ist.** Material
> einzulegen ist ein Aufruf je Knoten, und jeder kann für sich scheitern. Ein
> Abbruch auf halber Strecke hinterließe eine Sammlung, die niemand bestellt
> hat — deshalb wird der Teilerfolg gemeldet, nicht geworfen.

*Beispiel: [`examples/07_flow_collection.py`](examples/07_flow_collection.py)*


**Was dahinter läuft** — 1 Anfrage plus eine je Knoten:

```python
# was repo.flows.build_collection("C", node_ids=["a", "b"]) tut
sammlung = await repo.collections.create("C")       # 1. anlegen
for node_id in ["a", "b"]:                          # 2..n, bewusst nacheinander
    try:
        await repo.collections.add(sammlung.id, node_id)
    except EduSharingError as exc:
        failed.append({"id": node_id, "reason": str(exc)})
```

Jeder Fehlschlag wird aufgefangen statt geworfen: die Sammlung existiert zu dem
Zeitpunkt schon, ein Abbruch hinterließe eine, die niemand bestellt hat.

---

## `delete` — löschen und benennen, was verschwand

Seit dem 02.09.2026 sagt die Antwort auch `is_reference` und `original_id`.
An einer Referenz verschwindet nur die Referenz (vom MCP am 17.08.2026
gemessen); der Datensatz dahinter bleibt, und hier erfährt ein Aufrufer,
welches von beiden gerade ging.

**Eingabe**

```python
repo.flows.delete("abc-123")                   # in den Papierkorb
repo.flows.delete("abc-123", recycle=False)    # endgültig
```

**Ausgabe**

```json
{"id": "abc-123", "title": "Photosynthese einfach erklärt",
 "name": "material.pdf", "type": "ccm:io", "recycled": true}
```

Der Knoten wird vor dem Löschen gelesen, damit die Antwort ihn benennen kann.
Ein bloßes „erledigt" lässt den Aufrufer im Ungewissen, ob er das Richtige
erwischt hat — und ein Sprachmodell bestätigt dann einem Menschen irgendetwas.

Die Vorgabe ist die umkehrbare Variante. Endgültiges Löschen muss hingeschrieben
werden.


**Was dahinter läuft** — 2 Anfragen:

```python
# was repo.flows.delete("n1") tut
node = await repo.nodes.get("n1")     # 1. lesen, damit die Antwort ihn benennt
await node.delete(recycle=True)       # 2. löschen
```

Der zusätzliche Lesezugriff ist der ganze Zweck: er macht aus „erledigt" ein
„gelöscht: 'Photosynthese einfach erklärt' (ccm:io)".

---

## Wann welche Ebene

**Abläufe**, wenn das Ergebnis den Prozess verlässt: ein MCP-Werkzeug, eine
HTTP-Antwort, ein Prompt. Die **API-Ebene**, wenn Sie in Python damit
weiterarbeiten — `Node` hat `update()`, `add_keywords()`, `content.upload()`,
ein `dict` hat davon nichts.

Beides zu mischen ist normal:

```python
gefunden = await repo.flows.search("Wald", subject="Biologie")   # JSON heraus
node = await repo.node(gefunden["hits"][0]["id"])                # Objekt zurück
await node.add_keywords("geprüft")
```
