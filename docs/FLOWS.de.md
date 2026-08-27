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
| `find_collections` | 2, parallel | beide Sammlungswege → über die ID zusammenlegen |
| `collection_contents` | 2, parallel | Materialliste + Untersammlungsliste |
| `add_material` | 2–4 | whoami (ohne parent) → Vokabular auflösen → anlegen → einlegen (auf Wunsch) |
| `update_material` | 3–4 | Vokabular auflösen → laden → schreiben → zurücklesen |
| `build_collection` | 1 + eine je Knoten | anlegen → jeden einlegen, Fehlschläge auffangen |
| `delete` | 2 | laden (um ihn zu benennen) → löschen |

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
  "hits": [
    {
      "id": "1f71f84a-a67d-4b93-b55f-3ba4f39571d8",
      "title": "Feuerspuren im Satellitenbild",
      "url": "https://…/components/render/1f71f84a-…",
      "description": "Dynamik von Ökosystemen",
      "source_url": "https://beispiel.org/material",
      "mimetype": "text/html",
      "mediatype": "link",
      "fields": {"subject": ["Biologie"], "level": ["Sekundarstufe II"]}
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
from edusharing.flows import LanguageProfile

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

**Ein Zugriff**, genau wie `repo.node(id)` auf der API-Ebene. Dieser Ablauf
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

## `find_collections` — Sammlungen suchen

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

## `add_material` — anlegen, mit sauberen Metadaten

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
  "unresolved": []
}
```

Zwei Dinge nimmt der Ablauf ab:

**Wohin es kommt.** Ohne `parent_id` landet es im Home-Verzeichnis — dessen ID
vier Ebenen tief in der Antwort von `whoami()` steckt.

**Vokabular beim Schreiben.** Lesend löste die Suche „Biologie" längst selbst
auf; schreibend musste man den URI kennen. Genau dort wiegt ein fehlender Wert
schwerer:

> **`unresolved` prüfen.** Diese Werte wurden **nicht geschrieben**. Das
> Material existiert ohne sie und sieht vollständig aus. Deshalb werden sie
> gemeldet statt fallengelassen.

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
)
```

**Ausgabe**

```json
{
  "id": "c32b0498-0c0e-488e-ab04-980c0ea88e7f",
  "title": "Meine Sammlung",
  "url": "https://…/components/render/c32b0498-…",
  "added": ["abc-…", "def-…"],
  "failed": [{"id": "ghi-…", "reason": "HTTP 404 … Node does not exist"}]
}
```

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
