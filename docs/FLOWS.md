# Flows — use cases in one call

*[Deutsche Fassung: FLOWS.de.md](FLOWS.de.md)*

The library has two levels. They answer different questions, and both stay.

| | API level | Flow level |
|---|---|---|
| Reached as | `repo.search(...)`, `repo.node(...)` | `repo.flows.search(...)` |
| Returns | objects — `SearchResult`, `Node` | plain `dict`, ready for `json.dumps` |
| Good for | writing Python against edu-sharing | passing the result onwards |
| Calls | one endpoint per call | one call, several endpoints |

Flows add no capability. Everything they do can be done at the API level — with
more code. They exist because an MCP tool, an HTTP endpoint or a language model
does not want a `SearchResult`; it wants JSON, and it does not want to call four
endpoints to publish one piece of material.

```python
from edusharing import Repository

with Repository.from_env() as repo:
    result = repo.flows.search("Photosynthese", subject="Biologie")
    json.dumps(result)          # works — that is the point
```

Everything below exists twice: `await repo.flows.…` on `AsyncRepository`, and
blocking `repo.flows.…` on `Repository`.

---

## Two rules that run through every flow

**Readable values, not URIs.** `ccm:taxonid` holds
`http://w3id.org/openeduhub/vocabs/discipline/080`. A language model reading
that learns nothing. Flows return the labels the repository ships alongside.

**Short names, not properties.** Output keys are the configured aliases
(`subject`), not the edu-sharing properties (`ccm:taxonid`). Configure different
aliases and you get different keys — nothing here is tied to one profile:

```python
repo = Repository.from_env(field_aliases={"fach": "ccm:taxonid"})
repo.flows.search("Wald")["hits"][0]["fields"]     # {"fach": ["Biologie"]}
```

The defaults are `subject`, `level`, `type`, `difficulty`, `license`.

---

## `search` — find material

Vocabularies are resolved against this instance's own metadata set, so
`subject="Biologie"` works without anyone knowing the URI behind it.

**Input**

```python
repo.flows.search(
    "Photosynthese",           # full-text, optional when only filtering
    subject="Biologie",        # configured short names, resolved for you
    level="Sekundarstufe I",
    filters={"ccm:custom": "value"},   # properties without a short name
    facets=["subject"],        # server-side counts
    limit=10, offset=0,
)
```

**Output**

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
      "source_url": "https://example.org/material",
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

> **Check `unresolved`.** A non-empty list means a filter could not be resolved
> and was therefore **not sent**. The result is broader than you asked for and
> looks complete regardless. Each entry names the field in *your* words:
> `{"field": "subject", "value": "Raumschiffbau", "suggestions": ["Raumfahrt"]}`.

> **`total_is_lower_bound`** being true means "at least this many". Reporting
> that number as a fact states something that is not one.

### `rerank=True` — rescue a naturally phrased query

edu-sharing ANDs every word of a query. Words that describe the *shape* of a
request rather than its subject appear in almost no record, so one of them
empties the result set. Measured against staging on 2026-08-27:

| query | hits |
|---|---|
| `Bruchrechnung` | 1591 |
| `Ich suche ein Arbeitsblatt zur Bruchrechnung` | **0** |
| `Französische Revolution` | 637 |
| `Unterrichtsstunde Französische Revolution` | **0** |

A language model phrases like the second line. Left alone it reports "no
material found" about a subject with fifteen hundred records.

```python
repo.flows.search("Ich suche ein Arbeitsblatt zur Bruchrechnung", rerank=True)
# 0 hits -> 3 hits
```

What it does: expands the query into variants (the original, one without
framing words, one without stopwords, one per synonym), asks them in parallel,
fuses the rankings, and reorders by text and metadata quality.

**It costs one request per variant** (at most 5), so it is off by default.
`offset` is ignored while reranking — the pool is merged across variants, so an
offset into it would not mean what you expect.

The answer carries `query.reranked` and `query.variants` so the order is
explicable.

Two honest limits:

* **Same candidates in, same ranking out — but the candidates vary.** The
  scoring is a pure function of each record and the query; the position a record
  held in the repository's answer deliberately does not enter into it, and 15
  shuffles of one candidate set produce one identical ranking. What varies is
  what the repository returns: measured, the same query asked twice gives 25
  hits of which **15 differ**. So two runs may differ, and when they do it is
  the index that moved, not the ranking.
* **The word lists are German.** They are a parameter, not a constant:

```python
from edusharing.flows import LanguageProfile

english = LanguageProfile(stopwords=frozenset({"the", "of", "a"}),
                          framing=frozenset({"worksheet", "video"}),
                          synonyms={})
repo.flows.search("I need a worksheet about fractions",
                  rerank=True, language=english)
```

*Examples: [`examples/05_flow_search.py`](examples/05_flow_search.py), [`examples/08_flow_rerank.py`](examples/08_flow_rerank.py)*

---

## `vocabulary` — what values a field accepts

So that nothing has to guess. A language model asked to filter by subject will
otherwise invent a plausible value, and the search silently returns everything.

**Input**

```python
repo.flows.vocabulary("subject")            # short name
repo.flows.vocabulary("ccm:taxonid")        # or the property directly
repo.flows.vocabulary("subject", locale="en")
```

**Output**

```json
{
  "field": "subject",
  "property": "ccm:taxonid",
  "values": ["Schulfächer", "Allgemein", "Alt-Griechisch", "…"],
  "count": 416
}
```

Raises `ValidationError` for an unknown short name — the message lists the known
ones.

---

## `describe` — everything about one node

At the API level this is three calls: load the node, read its properties, look
at its content.

**Input**

```python
repo.flows.describe("1f71f84a-a67d-4b93-b55f-3ba4f39571d8")
```

**Output** — the `search` hit shape, plus:

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

`properties` holds the raw edu-sharing properties, so the flow is not a dead end
when a field has no short name.

> **The search index can hold nodes that no longer exist.** Measured against
> staging on 2026-08-27: **4 of 25** hits were not retrievable. Anything
> chaining `search` → `describe` has to expect `NotFoundError`.

---

## `find_collections` — search collections

Collections are how edu-sharing groups material for teaching, so finding them is
a different question from finding single resources — and a different endpoint.

**Input**

```python
repo.flows.find_collections("Physik", limit=10)
```

**Output** — the same shape as `search`, with `query.kind` set to
`"collections"`.

> **`total_is_lower_bound` is always true here.** The collection search asks two
> routes and merges them, so the figure counts at least this many, possibly more.

---

## `collection_contents` — open a collection

**Input**

```python
repo.flows.collection_contents("c32b0498-…", limit=20, offset=0)
```

**Output**

```json
{
  "id": "c32b0498-…",
  "materials": [{"id": "…", "title": "…", "url": "…", "fields": {…}}],
  "collections": [{"id": "…", "title": "Untersammlung", "url": "…", "fields": {}}],
  "total_materials": 26,
  "returned_materials": 20
}
```

Material and sub-collections, because a collection holds both. Measured on
2026-08-27 against a collection with two sub-collections: asking only for
material (`filter=files`) returns **zero** nodes — that collection looks empty.

Materials carry the same shape as search hits, so nothing has to tell two hit
formats apart.

---

## `update_material` — change what is already there

**Input**

```python
repo.flows.update_material(
    "b1a7555d-…",
    title="Neuer Titel",
    keywords=["Photosynthese"],
    subject="Physik",          # resolved, same as when creating
)
```

**Output**

```json
{"id": "b1a7555d-…", "title": "Neuer Titel", "url": "…",
 "name": "material.pdf", "unresolved": []}
```

Only what you pass is written; everything else stays. The write is verified by
reading it back, so a value edu-sharing silently drops raises `SilentDropError`
rather than passing as success.

> **A change where *nothing* could be resolved raises** instead of returning
> `unresolved`. Nothing happened, and a result that looks like a partial success
> would suggest the rest went through. There is no rest.

## `add_material` — create with proper metadata

**Input**

```python
repo.flows.add_material(
    "Photosynthese einfach erklärt",   # required
    url="https://example.org/material",
    parent_id=None,                    # None → your home folder
    description="…",
    keywords=["Photosynthese"],
    collection_id="…",                 # place a reference right away
    properties={"ccm:custom": ["…"]},  # raw properties
    subject="Biologie",                # resolved while writing
    level="Sekundarstufe I",
)
```

**Output**

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

Two things the flow takes off your hands:

**Where it goes.** Omit `parent_id` and it lands in your home folder — an id
that sits four levels deep in the `whoami()` response.

**Vocabulary while writing.** Reading, the search resolved `"Biologie"` on its
own; writing, the URI had to be known. This is where a missing value hurts more:

> **Check `unresolved`.** Those values were **not written**. The material exists
> without them and looks complete. That is why they are reported rather than
> dropped.

`cm:name` is derived from the title unless `name` says otherwise; a collision
appends a counter rather than failing.

*Example: [`examples/06_flow_create.py`](examples/06_flow_create.py)*

---

## `build_collection` — create a collection and fill it

**Input**

```python
repo.flows.build_collection(
    "Meine Sammlung",
    description="…",
    parent_id=None,          # None → your collection root
    node_ids=["abc-…", "def-…"],
    scope="MY",              # MY (default) | ORGANIZATION | PUBLIC
)
```

**Output**

```json
{
  "id": "c32b0498-0c0e-488e-ab04-980c0ea88e7f",
  "title": "Meine Sammlung",
  "url": "https://…/components/render/c32b0498-…",
  "added": ["abc-…", "def-…"],
  "failed": [{"id": "ghi-…", "reason": "HTTP 404 … Node does not exist"}]
}
```

> **The collection exists even when `failed` is non-empty.** Placing material is
> one call per node and each can fail on its own. Aborting halfway would leave a
> collection nobody asked for — so partial success is reported, not raised.

*Example: [`examples/07_flow_collection.py`](examples/07_flow_collection.py)*

---

## `delete` — remove and say what went

**Input**

```python
repo.flows.delete("abc-123")                   # into the bin
repo.flows.delete("abc-123", recycle=False)    # permanently
```

**Output**

```json
{"id": "abc-123", "title": "Photosynthese einfach erklärt",
 "name": "material.pdf", "type": "ccm:io", "recycled": true}
```

The node is read before it is deleted, so the answer can name it. A bare "done"
leaves the caller unsure whether the right thing was hit — and a language model
then confirms something to a person without knowing what.

The default is the reversible one. Permanent deletion has to be spelled out.

---

## When to use which level

Use **flows** when the result leaves your process: an MCP tool, an HTTP
response, a prompt. Use the **API level** when you keep working with the result
in Python — `Node` has `update()`, `add_keywords()`, `content.upload()`, and a
`dict` has none of that.

Mixing is normal:

```python
found = await repo.flows.search("Wald", subject="Biologie")   # JSON out
node = await repo.node(found["hits"][0]["id"])                # object back
await node.add_keywords("geprüft")
```
