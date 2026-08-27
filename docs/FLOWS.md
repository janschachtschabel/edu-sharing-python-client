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

*Example: [`examples/05_flow_search.py`](examples/05_flow_search.py)*

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
