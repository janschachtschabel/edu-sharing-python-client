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
| `text` | 1–3 | load node → stored text → (the file, for a text, JSON or XML upload) → (the linked page, with a service) |
| `search_all` | 3–4 (`include_pages` adds none) | material search (+1 to resolve a filter) + collection search (its two routes), in parallel |
| `placement` | 3 | load node (to resolve a reference) → way up + collections of the original, in parallel |
| `describe_many` | one per distinct id, in parallel | load each, report the ones that are gone |
| `related` | 2 (+1 per filter resolved) | describe the seed → search with its fields → drop the seed |
| `browse_tree` | one per collection opened | walk the sub-collections, de-duplicated and capped |
| `search_in_collection` | one per collection + two per collection for its material | walk → read material → compare locally |
| `collection_stats` | 2, parallel | material listing + sub-collection listing → tally locally |
| `page` | 3 (+1 per widget with `resolve_widgets`) | load collection → its page folder → the folder's variants |
| `find_pages` | 2, parallel | both collection routes → keep the hits carrying a page ref |
| `find_skills` | 1, or one per collection read (two with `include_subcollections`) | search with the content type → rank locally |
| `skill` | 2–3 | load record → download the file → list the original's folder |
| `skill_registry` | 2–3 + one per distinct entry | list the collection's files → download the registry → resolve each head |
| `pick_skill` | `find_skills` + `skill` | search → load the best |
| `relations` | 1 | read the node's links |
| `child_objects` | 2 | load parent → its children, filtered and sorted |
| `find_collections` | 2, parallel; with `parent_id` one per collection opened | both collection routes → merge on id → filter locally |
| `collection_contents` | 2, parallel | material listing + sub-collection listing |
| `add_material` | 1 + one per step taken (address 1, whoami 1, each vocabulary field 1, collection 1, publish 4) | check the address (`url`) → whoami (if no parent) → resolve vocabulary → create → add to collection (if asked) → publish (if asked) |
| `update_material` | 3–4 | resolve vocabulary → load → write → read back |
| `build_collection` | 1 + one per node (+4 to publish) | create → add each, catching failures → publish (if asked) |
| `delete` | 2 | load (to name it) → delete |
| `accept_suggestion` | 6–7 | load node → list proposals → write and read back → mark |

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

**Since 2026-09-02:** `exclude_ids` leaves out hits already shown — and the
page is refilled, so eight requested and three excluded still yields eight
(the refill capped at `EXCLUSION_MAX`, your `limit` never; `warnings` says
when a page still comes back short, and names the knob — offset, or the
pool under `rerank`); `facet_limit` raises the 20 values per facet;
`properties=["ccm:oeh_extendedType"]` carries any further property under
`fields` by its full name, as stored. Every hit also names `preview_url`,
`download_url`, `license` and `size`.

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
      "preview_url": "https://…/preview?nodeId=1f71f84a-…",
      "download_url": null,
      "license": "CC BY 4.0",
      "size": null,
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
from edusharing import LanguageProfile

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

## `search_all` — material *and* collections at once

**Since 2026-09-02:** `include_pages=True` adds a third bucket, `pages` — the
collection hits that carry a curated page (`find_pages`), read off the
collection hits already fetched — no further request. `properties=` reaches
both buckets.

Asking a repository about a topic usually means both questions: the individual
resources, and the collections in which somebody has already put together what
belongs to it. `wlo-mcp-sc` makes this its default entry point, and it is the
right default.

**Input**

```python
repo.flows.search_all("Zellteilung", subject="Biologie", limit=5)
```

**Output**

```json
{
  "query": {"text": "Zellteilung", "metadataset": "mds_oeh", "limit": 5},
  "materials": {
    "total": 42, "total_is_lower_bound": false, "returned": 5,
    "duplicates_removed": 0, "hits": [...], "facets": {}, "unresolved": []
  },
  "collections": {
    "total": 7, "total_is_lower_bound": true, "returned": 3,
    "hits": [...], "filters_ignored": [], "error": ""
  }
}
```

The two stay in **separate buckets**. Merging them into one ranking would
compare things that do not compare, and their counts do not mean the same thing:
the collection figure is a lower bound (two routes are merged), the material one
is not. `limit` applies per bucket, so neither crowds out the other.

> **Read `collections.filters_ignored`.** The collection query accepts
> `ngsearchword` and nothing else — any further criterion ends in
> `400 DAOValidationException`. Short names (`subject=…`) still reach both
> buckets, because `find_collections` applies them locally; raw `filters`
> have no local counterpart there and are named here. Applying a filter to
> one side and silently not to the other would claim a narrowing that never
> happened.
>
> **And read `collections.error`.** If the collection search fails
> entirely, the bucket comes back empty with the failure named there, and
> the material hits still arrive. Losing them because the other endpoint
> was down would throw away an answer that existed — the same line
> `collections.find` already draws between its own two routes. A failing
> **material** search does raise: handing that bucket back empty would
> claim there is nothing.

**Behind it** — 3 requests, sent together (4 when a filter has to be resolved,
none more with `include_pages`, whose bucket is read off the collection hits
and comes back empty with `error` when that search fails):

```python
# what repo.flows.search_all("Zellteilung", subject="Biologie") does
materials, collections = await asyncio.gather(
    find.search(repo, "Zellteilung", subject="Biologie"),         # 1. ngsearch
    collections.find_collections(repo, "Zellteilung", subject="Biologie"),  # 2.+3.
)
```

Exactly what two separate calls would send — the flow saves the round trip only
in the sense that the three go out at once instead of in sequence.

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

Since 2026-09-02 the answer also carries `aspects` and `original_id` — a
listing id names a reference, and `original_id` is the record behind it,
the id a write goes to (`None` on an original).

**One request**, exactly like `repo.node(node_id)` at the API level. This flow saves
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
  "public": true,
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

**Behind it** — 1 request:

```python
# what repo.flows.describe("abc") does
node = await repo.node("abc")        # exactly the same single request
# then: resolve the vocabulary fields to labels, key them by short name,
#       and hand back a dict instead of a Node
```

This flow saves no round trip. What it changes is the shape of the answer —
which is the whole point when the answer has to travel onwards.

---

## `text` — the full text of one material, and why there is none

**One to three requests.** The repository's own text first (`/textContent`);
then the file itself, when the record carries a text, JSON or XML upload — measured on
2026-08-27, `/textContent` returns nothing for Markdown and JSON although the
file has text; then the linked page (`ccm:wwwurl`) through the text-extraction
service, and only when you pass one: the library knows no service address.

**Input**

```python
from edusharing.extraction import TextExtraction

service = TextExtraction.from_env()          # EDU_SHARING_TEXT_EXTRACTION_URL
repo.flows.text(node_id, extraction=service, max_chars=20_000)
```

**Output**

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

`source` is `repository`, `download`, `extraction` or `none`. **Read `reason`
when it is `none`**: `node_not_found`, `access_denied`, `no_text_no_url`,
`repository_failed` (the repository did not hand over what it has — worth a
retry, not "no text"), `no_extraction_service` or `extraction_failed` — and
`detail` carries the
service's or the error's own words. No text is a normal answer, not an error,
and a model told so can say so instead of inventing one. `source_url` names
the linked page whenever there is one, so a caller without a service can still
decide to fetch it. Example 15 did all of this by hand in 215 lines.

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

---

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

---

## `placement` — where a node sits, and who curated it

**A listing id is a reference.** Since 2026-09-02 the node is read first and
the collections are asked for the record behind it: measured against
staging, `/usage` answers a reference id with an empty list and the original
with the collections it sits in — this flow used to report "in no
collection" for material that is in two. The answer carries `original_id`
(`None` on an original). A node that cannot be read adds
`{part: "original"}` to `failed`, and the collections are then asked with
the id as given.

Two questions that look alike and are not. **Where it lives** is its folder, and
that folder's folder. **Who curated it** is which collections hold a reference —
and a collection references nodes whose own parent is somewhere else entirely. A
node in ten collections still has exactly one parent chain.

**Input**

```python
repo.flows.placement("1f71f84a-a67d-4b93-b55f-3ba4f39571d8")
```

**Output**

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

`path` runs **top down**, ready to print as a breadcrumb — unlike
`node.parents()`, which mirrors the endpoint and gives the nearest first.
Measured live: `WLO > Biologie > Pflanzen: Form & Funktion`.

> **`failed` names the half that did not answer.** The two endpoints fail
> independently, and for foreign material one of them usually does: measured on
> 2026-08-28, `/parents` answers *500 AccessDeniedException* for material found
> by a search, while the very same endpoint gives a proper 403 for a node of
> one's own. Of 20 material hits, 18 hit exactly that — and the collections half
> answered every time.
>
> So a refused half is reported, not raised: `path` comes back empty with
> `{"part": "path", "reason": "PermissionDeniedError: …"}` in `failed`. Only
> when **both** halves fail does the flow raise — nothing to report is not a
> partial result, and an empty answer would claim the node sits nowhere.

> **Read `scope`.** It names the tree the path lives in — measured values are
> `COLLECTION` for the curated tree and `MY_FILES` for your own folders — and
> with it, where the path stops: at the boundary of what the account may read.
> Measured on 2026-08-28: asking for the complete
> path (`fullPath=true`) answers **HTTP 403** for an ordinary account, because
> it runs up through areas the account has no access to. The library therefore
> does not ask for it, and reports how far the answer reaches instead of
> letting a truncated path pass as a complete one.

**Behind it** — 3 requests: one read, then two sent together:

```python
# what repo.flows.placement("abc") does
node = await repo.nodes.get("abc")                    # 1. a listing id is a reference
ancestry, collections = await asyncio.gather(
    placement.ancestry_of(repo, "abc"),                # 2. GET …/parents
    placement.collections_of(repo, "abc", original_id=node.original_id),  # 3. /usage
)
```

The read comes first because `/usage` knows only originals: asked with a
reference id it answers an empty list, and "this node sits in no collection"
would be wrong. The parents answer carries the node itself as its first entry;
the library drops it from `path` — a node is not its own ancestor.

At the API level the same two, as objects:

```python
node = await repo.node("abc")
for folder in await node.parents():        # nearest first
    print(folder.title)
for collection in await node.collections():
    print(collection.title, collection.is_public)
```

---

## `find_collections` — search collections

**Since 2026-09-02 the search can be narrowed — locally.** The collection
endpoint takes a search word and nothing else (measured), so `subject=`,
`level=` and the other short names are resolved and matched against each hit's
own properties; a hit without properties cannot be judged and is counted in
`unjudged`. Collection hits carry the URIs but no `_DISPLAYNAME` labels
(measured), so `fields` stays empty for them — ask for the property itself with
`properties=["ccm:taxonid"]`. `parent_id` does not search: the sub-collections
below it are walked (two levels) and `text` is matched against their titles,
nearest level first; empty `text` lists them all.

Collections are how edu-sharing groups material for teaching, so finding them is
a different question from finding single resources — and a different endpoint.

**A short-name filter is judged here, on more candidates than `limit`.** The
collection routes take a search word and nothing else, so `subject="Biologie"`
is applied locally: up to five times `limit` (at most 100) candidates are
fetched and filtered, `total` then counts the matches among them, and
`warnings` says when the search knew more candidates than were judged.
`query.filters` echoes your words, as in `search`. Below a `parent_id` the
walk keeps each collection's record, so the same filter works there; a query
of stopwords only is matched as typed; more sub-collections than one page
lists make `total_is_lower_bound` true.

**Input**

```python
repo.flows.find_collections("Physik", limit=10)
```

**Output** — the same shape as `search`, with `query.kind` set to
`"collections"`.

> **`total_is_lower_bound` is true for a search — and below a `parent_id`
> only when the walk was cut short.** The collection search asks two
> routes and merges them, so the figure counts at least this many, possibly more.
>
> **`limit` caps what comes back, and both routes get through it.** Each route
> is asked for `limit`, and the merged list is taken round-robin before it is
> cut — so `limit=10` gives roughly five from each rather than ten from the
> first. Cutting the concatenation instead would silence the second route for
> any broad query, and it measurably finds collections the first one does not.


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

**Since 2026-09-02:** `properties=["ccm:oeh_extendedType"]` carries further
properties of each entry under `fields`, as stored — measured, a listing carries
the content type and `fields` used to hide it.

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
# what repo.flows.collection_contents(collection_id=cid) does
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

## `describe_many` — several nodes at once

**Input**

```python
repo.flows.describe_many(["abc-…", "def-…", "ghi-…"])
```

**Output**

```json
{
  "requested": 3,
  "found": 2,
  "nodes": [{"id": "abc-…", "title": "…", "…": "…"}],
  "failed": [{"id": "ghi-…", "reason": "NotFoundError: HTTP 404 …"}]
}
```

`nodes` keeps the order of the request, so the answer lines up with what was
asked. Duplicates are fetched once.

> **A missing node is reported, not raised.** Measured on 2026-08-27: **4 of
> 25** search hits were no longer retrievable. An index that outlives its nodes
> is the ordinary case here, and losing the whole list because one entry is
> gone makes a search result unusable.

**Behind it** — one request per distinct id, sent together:

```python
# what repo.flows.describe_many(["a", "b"]) does
results = await asyncio.gather(*(describe(repo, i) for i in ["a", "b"]))
# each failure caught and reported instead of raised
```

---

## `related` — more material like this one

**Not a relation.** `flows.relations` gives the links somebody *asserted*
between two nodes. This computes a *resemblance*: the seed's own subject and
level become filters of an ordinary search, and the seed drops out of the
result. Both are called "related", and telling them apart matters.

**Input**

```python
repo.flows.related("abc-123", on=("subject", "level"), limit=10)
```

**Output**

```json
{
  "seed": {"id": "abc-123", "title": "Zellteilung"},
  "based_on": {"subject": ["Biologie"], "level": ["Sekundarstufe I"]},
  "hits": [{"id": "…", "title": "…", "…": "…"}],
  "unresolved": [],
  "reason": ""
}
```

> **Read `based_on`.** Without it nobody can judge the resemblance. And read
> `unresolved`: a value the instance could not resolve did **not** narrow the
> search, so the result is broader than it looks.

When the seed carries none of the fields, `hits` is empty and `reason` says so.
An unfiltered search would answer "more of this" with anything.

`on` is a default, not a fixture — which short names exist at all is decided by
the instance's metadata set.

**Behind it** — 2 requests plus vocabulary:

```python
# what repo.flows.related("abc") does
seed = await describe.describe(repo, "abc")           # 1. load it
found = await find.search(repo, None, **based_on)     # 2. its fields as filters
hits = [h for h in found["hits"] if h["id"] != "abc"] # drop the seed
```

---

## `browse_tree` — the collections under one collection

**Input**

```python
repo.flows.browse_tree("abc-123", depth=2, max_collections=50)
```

**Output**

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

> **Collections form a graph, not a tree.** A sub-collection can hang under
> several parents, and two can hang under each other. The walk de-duplicates by
> id — without that it runs in circles — and caps how many it opens. **Read
> `truncated`**: a shortened tree must not read as a complete one.

Only the collections. Their material is a second request per node —
`collection_stats` counts it, `collection_contents` lists it.

**Behind it** — one request per collection opened:

```python
# what repo.flows.browse_tree("abc", depth=2) does
GET /collection/v1/collections/-home-/abc/children/collections
# then the same for each child, to the given depth, skipping ids already seen
```

---

## `search_in_collection` — find something inside one collection

**Since 2026-09-02:** `properties=["ccm:oeh_extendedType"]` carries further
properties of each entry under `fields`, as stored — measured, a listing carries
the content type and `fields` used to hide it.

**Input**

```python
repo.flows.search_in_collection("abc-123", "zelle", depth=2)
```

**Output**

```json
{
  "query": "zelle",
  "hits": [{"id": "…", "title": "Zellteilung", "…": "…"}],
  "searched": 4,
  "unreadable": 0,
  "failed": [],
  "truncated": false
}
```

> **`unreadable` counts the sub-collections that refused.** The walk finds
> them in their parents' answers, so the list includes collections this
> account has never opened and whose permissions it does not know. One 403
> among twenty-five used to turn a partial answer into no answer at all;
> now the rest is searched and the number stands next to `truncated`, for
> the same reason: cutting in silence reads like completeness.
> **`failed` names each of them** with its id and the reason
> (`"PermissionDeniedError: …"`). If not one collection could be read, the
> flow raises instead — a wrong password refuses all of them, and that is no
> partial answer. Only a refusal is part of the answer: any other error is
> raised, not counted (audit COR-2).

> **A search cannot be scoped to a collection.** Measured three times — by
> `wlo-mcp-sc` on 2026-07-17, here on 2026-08-27 and again on 2026-08-28 —
> `ngsearch` with `virtual:primaryparent_nodeid` answers HTTP 400. It would
> also be the wrong answer: a collection holds *references* to nodes whose own
> parent lives elsewhere, so a parent-scoped search would miss exactly the
> curated ones. So this flow walks and compares locally.

Compared are title, description and the resolved field labels — what a
serialised hit actually carries. For full text across the whole repository,
`flows.search` is the better tool.

> **Read `truncated`.** An empty result from a walk that stopped early is not
> "there is none".

**Behind it** — one request per collection for the walk, two more per
collection for its material:

```python
# what repo.flows.search_in_collection("abc", "zelle") does
tree = await browse_tree(repo, "abc", depth=2)        # the walk
pages = await asyncio.gather(*(collection_contents(repo, i) for i in ids))
hits = [h for page in pages for h in page["materials"] if matches(h)]
```

---

## `collection_stats` — how much is in there, and what of

**Input**

```python
repo.flows.collection_stats("abc-123", sample=100)
```

**Output**

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

The counts are exact — they come from the pagination totals. **The breakdown is
a sample**: `sampled` says how many records it was tallied over, `complete`
whether that was all of them. And **the counters do not partition it**: a field
is multi-valued, so measured live, 15 materials carried 25 level assignments
between them. Each counter says how many records mention a value. A breakdown over a hundred of three hundred is
useful; mistaking it for the whole is not.

> **Not from a facet query.** A collection curates *references* to nodes whose
> primary parent lives elsewhere, so a facet scoped by parent returns nothing
> for them. The children endpoint returns the referenced files with their
> `*_DISPLAYNAME` labels, so a local tally is both correct and readable.

**Behind it** — 2 requests:

```python
# what repo.flows.collection_stats("abc") does
page = await collection_contents(repo, "abc", limit=100)   # material + sub-collections
# then tally page["materials"] by their resolved field labels
```

---

## `page` — the curated page a collection renders

edu-sharing's page builder: a collection may carry a landing page made of
*swimlanes*, each holding widgets, each widget pointing at a node.
WirLernenOnline calls these “Themenseiten”; nothing about them is WLO's, so
this flow does not use the word.

**Input**

```python
repo.flows.page("abc-123")                       # the variant that renders
repo.flows.page("abc-123", variant="v-2")        # a specific one
repo.flows.page("abc-123", resolve_widgets=True) # + what each widget holds
```

**Output**

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

**`by_position` is not decoration.** A page document without a `default` renders
the *first* variant of its list. “Nothing chosen” and “the first one chosen”
look identical to a visitor and are different states — and switching away from
one is a different sentence than switching away from the other.

**A page can render nothing.** Measured 2026-08-28: the collection `Hexen`
carries a page, one variant, a readable document — whose swimlane list is
empty. *Has a page* and *has content* are separate questions.

**Saved searches are named, not run.** A widget holds either a fixed list
(`sortedNodeIds`, resolved) or a saved search (`searchText` + `propertyFilters`,
reported under `search` and left alone). Those filters carry `virtual:` fields
the metadata set does not know; running them would be guessing. Use
`flows.search` with filters you chose.

**Behind it** — 3 requests:

```python
# what repo.flows.page("abc") does
node = await repo.node("abc")            # for ccm:page_config_ref
page = await node.page.get()             # folder + its children, 2 requests
```

**Writing.** Which variant renders is a write, and it is immediately public:

```python
node = await repo.node("abc-123")
page = await node.page.render("v-2")     # reads, edits, writes, reads back
```

It **edits** the stored document — every key the page builder owns travels
through untouched — and refuses everything it cannot prove: no document, not
JSON, not an object, no variant list, variant not listed. Nothing upstream
validates it; measured, the property route stores the literal string
`"not json at all"` with a `200`.

---

## `find_pages` — which collections carry one

**Input**

```python
repo.flows.find_pages("Deutsch", limit=25)
```

**Output**

```json
{"query": "Deutsch", "checked": 50, "total": 876, "total_is_lower_bound": true,
 "hits": [{"id": "69f9ff64-…", "title": "Deutsch", "url": "https://…",
           "folder_id": "f2020460-…"}],
 "reason": ""}
```

One search — two routes in parallel, exactly what `find_collections` sends.
A subset of it, too: every curated page is a collection, few collections have
one.

`total` counts the collections that matched, not the ones carrying a page —
and it is a **lower bound**, because the collection search asks two routes and
one of them reports no total at all.

**`checked` says how many hits could be judged at all.** One leg of the
collection search has a fixed projection and returns no properties; a page
cannot be recognised on those hits. Without that number, an empty `hits` reads
as a statement about the repository when it was one about the projection.

**One run is a sample, not the catalogue.** Measured six times on 2026-08-28
with the same term: three different hit sets, `checked` swinging between 50
and 100. Both collection routes are involved and neither is a superset of the
other.

> **Why not a filter?** Because there is none. `ccm:page_config_ref` as a search
> criterion answers `400 DAOValidationException: Widget ccm:page_config_ref was
> not found in the mds`. A page is recognised from the answer.

**Behind it** — 2 requests, in parallel:

```python
# what repo.flows.find_pages("Deutsch") does
found = await repo.find_collections("Deutsch", limit=25)   # both routes at once
# then: keep the hits whose properties carry ccm:page_config_ref,
#       and count how many hits carried properties at all
```

At the API level the same recognition is one line:
`hit.properties().get("ccm:page_config_ref")`. Reading the page behind it is
`node.page.get()`.

---

## `find_skills` — which skills fit a task

**One request** repository-wide (the content type travels as a criterion, the
short names with it), or **one per collection read** with `collection_id`
(the listing takes no criteria; type and short names are checked locally).
Ranked: a term in the title counts 3, in the keywords 2, in the description 1.
A skill that is both an original and a reference into a collection comes back
once, as the original — the id a write may target.

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
  "truncated": false,
  "unreadable": 0
}
```

The conventions — which content type marks a skill, how a registry names
itself — are `SkillConventions`, a parameter with WLO's values as the default.
**Measured (2026-09-02): `mds_oeh` accepts the content type as a criterion,
`-default-` refuses it** — set `EDU_SHARING_METADATASET` or pass
`metadataset=`, or no skill is found at all.

---

## `skill` — one skill's instruction, and what belongs to it

**Two to three requests.** The record, its file with `download()` — measured,
`/textContent` is empty for Markdown — and, with `include_files`, the folder
beside it: the ORIGINAL's folder, read through one extra request when the id
was a reference. **Read `files_reason`**: `folder_unreadable` (403 anonymously,
measured), `no_folder`, or `too_many` with `folder_file_count` — an empty
`files` is not "the skill travels alone".

```python
repo.flows.skill(node_id)
```

```json
{
  "id": "…", "original_id": "…", "title": "Fragen generieren", "…": "…",
  "content": "# Fragen generieren\n\n…",
  "content_reason": "",
  "references": [{"kind": "ki-skill", "title": "Lehrprofil auswerten",
                  "url": "…/components/render/…", "node_id": "…", "offset": 412}],
  "files": [{"id": "…", "title": "vorlage.docx", "mimetype": "application/msword",
             "size": 18342, "download_url": "…"}],
  "files_reason": "",
  "folder_file_count": null
}
```

`content_reason` says why `content` is `null`: `no_file` for a record without
an upload, `not_text` for a binary one — a PDF decoded as text is mojibake,
not an instruction. A byte-order mark is stripped.

`content` is uploaded content — data for a model to weigh, never an
instruction this library follows. Wrap it with `as_untrusted` before it
reaches a prompt.

---

## `skill_registry` — which skills one collection approved

**Two requests plus one per distinct entry — three when the listing lacks
the download address.** The collection's file listing (never the
search index — a record can fall out of the index while sitting in the store,
measured by the MCP on 2026-08-09), the registry document with `download()`
straight from the listing entry (its record is read separately only when the
listing lacks the download address), then each named skill's record for description and keywords (`resolve=False`
skips those). The document's `::: ki-skill` blocks are the catalogue, its
`##`/`###` headings the working contexts; `context="Unterricht vorbereiten"`
narrows to that group plus the general part, and **a name that does not match
narrows nothing** — `context_match` says `missing` and `contexts` lists what
exists.

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

**Read `reason` before `entries`**: `collection_not_found`, `no_registry` or
`unreadable`. `no_registry` with a `scan_truncated` is not a finding of
absence — the listing was cut at 50 files. Two candidate documents in one
collection are told apart by their name or title (`skill_registry.md`,
"Skillkatalog …"); when that does not decide, the smallest id wins and
`ambiguous` says how many there were.

---

## `pick_skill` — search, rank, load

**`find_skills` plus one `skill`.** The best match with its instruction, the
runners-up by title and id — so a wrong pick stays visible to the caller.

```json
{"best": {"id": "…", "title": "…", "content": "…", "…": "…"},
 "alternatives": [{"id": "…", "title": "…", "…": "…"}],
 "reason": ""}
```

`reason` is `no_match` when nothing fitted; then `best` is `null`.

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
 "name": "material.pdf", "unresolved": [], "redirected_from": null}
```

**`redirected_from`** names the id you passed when the write went to its
original — a listing id is a reference, and a write stored on a reference
never reaches the record — and `id` is then the original's. `null` otherwise.

Only what you pass is written; everything else stays. The write is verified by
reading it back, so a value edu-sharing silently drops raises `SilentDropError`
rather than passing as success.

> **A change where *nothing* could be resolved raises** instead of returning
> `unresolved`. Nothing happened, and a result that looks like a partial success
> would suggest the rest went through. There is no rest.
**Behind it** — 3 to 4 requests:

```python
# what repo.flows.update_material("abc", title="New", subject="Biologie") does
await repo.vocab.resolve("ccm:taxonid", "Biologie")   # cached after the first
node = await repo.node("abc")
await node.update(title="New", properties={...})      # writes, then reads back
```

The read-back is not the flow's doing — `node.update()` carries it either way.

---


## `accept_suggestion` — apply a proposal, read it back, then mark it

**Six requests, seven for a keyword.** Load the node, list its proposals,
write the proposed value and read it back — a keyword through
`add_keywords`, everything else with `set_property` — and only then mark
the proposal `ACCEPTED` and read its status back. Measured on 2026-08-28: marking alone writes **nothing** into the
node — a proposal accepted by `decide()` leaves the property as it was, so
"accepted" on its own is a record of something that never happened.

**Input**

```python
repo.flows.accept_suggestion(node_id, suggestion_id)
```

**Output**

```json
{
  "id": "1f71f84a-…",
  "suggestion_id": "s-4410…",
  "property": "ccm:taxonid",
  "value": "http://w3id.org/openeduhub/vocabs/discipline/080",
  "applied": true,
  "status": "ACCEPTED",
  "failed": [],
  "replaced": []
}
```

**Read `applied`.** When the value does not arrive (`SilentDropError`), nothing
is marked, `status` stays `PENDING` and `failed` carries `{part: "apply"}`;
a proposal already decided comes back with `{part: "status"}` and is not
applied again. Declining needs no flow — `node.suggestions.decide(ids,
accept=False)` touches nothing but the proposal, which is what declining means.

**A keyword proposal is added, not written over.** `cclom:general_keyword`
is a shared list; the value goes in through `add_keywords`, and the other
keywords stay. For any other property the values the proposal displaced
come back as `replaced`. And when the value is on the node but marking the
proposal fails, `failed` carries a `mark` part that says so — the value is
not lost with the error.

---

## `add_material` — create with proper metadata

**Since 2026-09-02, `url` is checked first.** A second record for the same
address is a duplicate by definition, so with `if_exists="return"` (the
default) an existing record is named — `created` is `False`, `existing` carries
`{id, title, url}`, and nothing is created. `"raise"` raises `ConflictError`;
`"create"` skips the check. Whether the check can run is a property of the
metadata set — measured, `mds_oeh` accepts `ccm:wwwurl` as a criterion and
`-default-` does not — and when it cannot, the default check is skipped and
`warnings` says so, while `"raise"` refuses to guess. The same applies to an
address the search cannot take as a criterion — it passes only `http(s)://`
addresses through — and to a misspelled `if_exists`, which is refused even
when no `url` is given.

**The check sees what the index sees.** The address lookup goes through the
search index, which trails the node store: measured on staging (2026-09-02),
a record created a moment ago was findable by its address after 5.3 seconds,
not before. Two calls for the same address within that window both create;
an import that carries the same address twice must de-duplicate its own
input.

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
    publish=False,                     # True → readable by everyone
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
  "public": false,
  "unresolved": [],
  "existing": null,
  "created": true,
  "warnings": []
}
```

Three things the flow takes off your hands:

**Where it goes.** Omit `parent_id` and it lands in your home folder — an id
that sits four levels deep in the `whoami()` response.

**Vocabulary while writing.** Reading, the search resolved `"Biologie"` on its
own; writing, the URI had to be known. This is where a missing value hurts more:

> **Check `unresolved`.** Those values were **not written**. The material exists
> without them and looks complete. That is why they are reported rather than
> dropped.

**Visibility.** What is created here is readable by its creator and by nobody
else, and filing it into a public collection does not change that — measured.

> **Check `public`.** `false` means the material exists and only you can see it.
> `publish=True` grants everyone read access. It is off by default because
> reading cannot be taken back.

`cm:name` is derived from the title unless `name` says otherwise; a collision
appends a counter rather than failing.

*Example: [`examples/06_flow_create.py`](examples/06_flow_create.py)*


**Behind it** — one request per step taken (publishing counts four: two reads,
the grant and its read-back):

```python
# what repo.flows.add_material("T", url=url, subject="Biologie") does
await duplicates.find_by_url(repo, url)          # 0. only with url: the address check
who = await repo.whoami()                        # 1. only when parent_id is None
uri = await repo.vocab.resolve("ccm:taxonid", "Biologie")   # 2. per vocab field
node = await repo.nodes.create(                  # 3. the creation itself
    who.home_folder, name=name_from_title("T"), title="T",
    properties={"ccm:taxonid": [uri]})
await repo.collections.add(collection_id, node.id)          # 4. only if asked
```

The name is derived from the title; a collision appends a counter instead of
failing.


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
    publish=False,           # True → readable by everyone
)
```

**Output**

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

> **`scope="PUBLIC"` is not read access.** Measured: it decides where the
> collection is listed, not who may open it — a collection created that way
> still comes back unreadable to others. `publish=True` is what grants it.

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

Since 2026-09-02 the answer also says `is_reference` and `original_id`.
Deleting a reference removes only the reference (measured by the MCP,
2026-08-17); the record behind it survives, and this is where a caller
learns which of the two just went.

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
