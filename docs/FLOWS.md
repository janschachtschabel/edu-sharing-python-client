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

## What each flow costs, at a glance

Measured with a request-logging transport on 2026-08-27. "Requests" is what the
flow sends to the repository; the API level sends the same ones, just written
out by hand.

| Flow | Requests | The chain behind it |
|---|---|---|
| `search` | 2 | resolve vocabulary → query |
| `search(rerank=True)` | 1 per variant (≤5), parallel | expand → query each → score and merge in memory |
| `vocabulary` | 1 | resolve short name → fetch values (cached) |
| `describe` | 1 | load node |
| `relations` | 1 | read the node's links |
| `child_objects` | 2 | load parent → its children, filtered and sorted |
| `find_collections` | 2, parallel | both collection routes → merge on id |
| `collection_contents` | 2, parallel | material listing + sub-collection listing |
| `add_material` | 2–4 | whoami (if no parent) → resolve vocabulary → create → add to collection (if asked) |
| `update_material` | 3–4 | resolve vocabulary → load → write → read back |
| `build_collection` | 1 + one per node | create → add each, catching failures |
| `delete` | 2 | load (to name it) → delete |

Three of them — `search`, `vocabulary`, `describe` — send exactly what the API
level sends. They save no round trip at all: their gain is the JSON shape and
the resolved labels. The rest genuinely chain calls.

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
  "duplicates_removed": 1,
  "hits": [
    {
      "id": "1f71f84a-a67d-4b93-b55f-3ba4f39571d8",
      "title": "Feuerspuren im Satellitenbild",
      "url": "https://…/components/render/1f71f84a-…",
      "description": "Dynamik von Ökosystemen",
      "source_url": "https://example.org/material",
      "mimetype": "text/html",
      "mediatype": "link",
      "fields": {"subject": ["Biologie"], "level": ["Sekundarstufe II"]},
      "duplicate_ids": []
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

### Duplicate hits are folded together

The repository creates a separate node each time the same web page is imported.
Those nodes share a source address and differ only in the technical name —
edu-sharing appends " - 2", " - 3" on a name collision. Whoever reads the list
takes two entries for two pieces of material.

Measured on 2026-08-27: among 50 hits, one such pair for "Photosynthese" and one
for "Bruchrechnung", none for "Optik" or "Wald". A low rate, and a real problem
each time it occurs.

`search` therefore folds them, **on by default**, and hides nothing:

```json
{
  "returned": 49,
  "duplicates_removed": 1,
  "hits": [{"id": "a", "duplicate_ids": ["b"], "…": "…"}]
}
```

The first hit of a group wins — under `rerank` that is the best-scored one. Only
the **source address** counts: two materials may share a title and genuinely
differ, and a hit without a source address is never a duplicate of anything.

`limit` counts before folding, so fewer than `limit` hits can come back;
`returned` says how many. `deduplicate=False` gives the raw view.


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


**Behind it** — one request **per variant**, run in parallel (at most 5):

```python
# what rerank=True adds
variants = expand_query(text, language)      # "full", "topic", "nostop", "syn"
results = await asyncio.gather(*(            # all at once, not one after another
    repo.searcher.search(v.text, limit=pool) for v in variants))
# then, in memory and without further requests: drop deleted placeholders,
# score every candidate for text and metadata quality, weight by which variants
# found it at all, sort, take `limit`.
```


**Behind it** — 2 requests, the same two the API level makes:

```python
# what repo.flows.search("Photosynthese", subject="Biologie") does
uri = await repo.vocab.resolve("ccm:taxonid", "Biologie")    # 1. label -> URI
result = await repo.searcher.search("Photosynthese",         # 2. the query
                                    filters={"ccm:taxonid": uri})
# then, without further requests: SearchResult -> dict, DISPLAYNAME values
# instead of URIs, short names as keys, unresolved filters named back in your
# own words.
```

No round trip is saved here. The gain is the JSON shape, and that an
unresolvable filter is reported rather than silently dropped.

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


**Behind it** — 1 request:

```python
# what repo.flows.vocabulary("subject") does
prop = repo.searcher.field_aliases["subject"]      # short name -> ccm:taxonid
values = await repo.vocab.values(prop)             # the request
```

Cached: asking a second time for the same field costs nothing.

---

## `describe` — everything about one node

**One request**, exactly like `repo.node(id)` at the API level. This flow saves
no round trip; it hands back a `dict` with vocabulary fields already resolved to
labels, instead of a `Node` object.

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

---

---

## `child_objects` — further documents of one node

A worksheet's answer sheet, a lesson plan's handouts. These belong **to** the
parent rather than standing on their own — which is what separates them from a
collection's contents and from a relation between two independent nodes.

**Input**

```python
repo.flows.child_objects("haupt-1")
```

**Output**

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

Ordered by `ccm:childobject_order`, then by creation time. Only nodes carrying
the `ccm:io_childobject` aspect are returned — a node has other children,
versions among them, and returning those as attachments would be wrong in a way
nobody notices until a version appears in a download list.

**Behind it** — 2 requests:

```python
# what repo.flows.child_objects("haupt-1") does
node = await repo.nodes.get("haupt-1")      # 1. load the parent
children = await node.children.list()        # 2. its children, filtered + sorted
```

### Writing child objects

```python
node = await repo.node("haupt-1")
child = await node.children.add(pdf_bytes, filename="loesung.pdf",
                                mimetype="application/pdf")
await child.delete()                          # an ordinary node from here on
```

`add()` is **two requests**: create the child, then upload the bytes. If the
upload fails the child is removed again — a node without content shows up in
every listing and downloads as nothing.

> **The combination that creates one cannot be guessed.** Measured on
> 2026-08-27: `type=ccm:io_childobject` answers HTTP 500 (no such type),
> `type=ccm:io` without `assocType` answers HTTP 500 (integrity violation). What
> works is `type=ccm:io` **plus** `assocType=ccm:childio` **plus**
> `aspects=ccm:io_childobject` — because `ccm:io_childobject` is an *aspect*,
> not a type. The library sets all three.

## `relations` — what a node is linked to

Relations join nodes that stand **side by side** — the parts of a series, a
resource and what it is based on. Not to be confused with a collection, which is
a container.

**Input**

```python
repo.flows.relations("teil-1")
```

**Output**

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

Each entry names the node at the *other* end, seen from the node you asked
about.

> **Read `ai_generated` and `approved` together.** A link a machine proposed and
> nobody confirmed is a suggestion, not a fact. The API is explicitly built for
> this: a model may propose, a person approves.

**Behind it** — 1 request:

```python
# what repo.flows.relations("teil-1") does
relations = await repo.relations.of("teil-1")     # GET /relation/v1/-home-/{id}
```

### Writing relations

There is no flow for this — it is a single call at the API level:

```python
await repo.relations.create("teil-1", "isPartOf", "reihe")
await repo.relations.create("teil-1", "references", "teil-2", ai_generated=True)
await repo.relations.approve("teil-1", "references", "teil-2")   # a person confirms
await repo.relations.delete("teil-1", "references", "teil-2")
```

**The opposite direction is kept for you.** Create `isPartOf` from part to
series, and the series reports `hasPart` — measured, without setting it twice.
Seven types can be created:

`isPartOf` · `isBasedOn` · `references` · `isDuplicateOf` · `requires` ·
`replaces` · `hasFormat`

The other five (`hasPart`, `isBasisFor`, `isRequiredBy`, `isReplacedBy`,
`isFormatOf`) arise as those opposites and are read-only. Asking for one
directly answers HTTP 400 with nothing that says why, so the library rejects it
first with a message naming the one to use instead.

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


**Behind it** — 2 requests, run in parallel:

```python
# what repo.flows.find_collections("Physik") does
result = await repo.collections.find("Physik")
#   which internally asks both routes at once and merges them on node id:
#     POST /search/v1/queries/-home-/{mds}/collections
#     GET  /collection/v1/collections/-home-/search
```

Two routes because neither alone is complete — which is also why `total` is only
a lower bound.

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


**Behind it** — 2 requests, run in parallel:

```python
# what repo.flows.collection_contents(cid) does
materials, children = await asyncio.gather(
    repo.raw.json("GET", f"/node/v1/nodes/-home-/{cid}/children",
                  params={"filter": "files", "maxItems": limit}),
    repo.raw.json("GET", f"/collection/v1/collections/-home-/{cid}"
                         "/children/collections", params={"maxItems": limit}),
)
```

Written out at the API level this is two waits instead of one — and the second
endpoint is easy to forget entirely.

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


**Behind it** — 2 to 4 requests:

```python
# what repo.flows.add_material("T", subject="Biologie") does
who = await repo.whoami()                        # 1. only when parent_id is None
uri = await repo.vocab.resolve("ccm:taxonid", "Biologie")   # 2. per vocab field
node = await repo.nodes.create(                  # 3. the creation itself
    who.home_folder, name=name_from_title("T"), title="T",
    properties={"ccm:taxonid": [uri]})
await repo.collections.add(collection_id, node.id)          # 4. only if asked
```

The name is derived from the title; a collision appends a counter instead of
failing.


**Behind it** — 3 to 4 requests:

```python
# what repo.flows.update_material("n1", subject="Biologie") does
uri = await repo.vocab.resolve("ccm:taxonid", "Biologie")   # 1. per vocab field
node = await repo.nodes.get("n1")                            # 2. load
await node.update(properties={"ccm:taxonid": [uri]})         # 3. PUT
#     which reads the node back itself (4.) and raises SilentDropError when
#     edu-sharing accepted the write and did not store it.
```

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


**Behind it** — 1 request plus one per node:

```python
# what repo.flows.build_collection("C", node_ids=["a", "b"]) does
collection = await repo.collections.create("C")     # 1. create
for node_id in ["a", "b"]:                          # 2..n, sequential on purpose
    try:
        await repo.collections.add(collection.id, node_id)
    except EduSharingError as exc:
        failed.append({"id": node_id, "reason": str(exc)})
```

Each failure is caught rather than raised: the collection already exists by
then, so aborting would leave one nobody asked for.

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


**Behind it** — 2 requests:

```python
# what repo.flows.delete("n1") does
node = await repo.nodes.get("n1")     # 1. read, so the answer can name it
await node.delete(recycle=True)       # 2. delete
```

That extra read is the whole point: it turns "done" into "deleted 'Photosynthese
einfach erklärt' (ccm:io)".

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
