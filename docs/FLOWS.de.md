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

*Beispiel: [`examples/05_flow_search.py`](examples/05_flow_search.py)*

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

---

## `describe` — alles über einen Knoten

Auf API-Ebene sind das drei Zugriffe: Knoten laden, Eigenschaften lesen, Inhalt
ansehen.

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
