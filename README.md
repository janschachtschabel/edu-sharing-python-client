# edu-sharing for Python

Python client for [edu-sharing](https://edu-sharing.com) repositories and the
**b-api** (Bildungs-API, OpenEduHub) — **repository-agnostic** and
**async-first**.

> *Deutsche Fassung: [README.de.md](README.de.md).*

> **Status: work in progress.** Reading, searching and writing are in place and
> verified against edu-sharing 11.0 — including writes, against a live instance.
> The roadmap is in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
> ([German](docs/ARCHITECTURE.de.md)).

## Installing

Python 3.11 or newer. Not on PyPI yet, so install from a checkout:

```bash
uv pip install -e .
```

`pip install -e .` works the same way in an environment that has pip. Four
runtime dependencies come with it: `httpx` for the transport, and `attrs`,
`python-dateutil` and `typing-extensions` for the generated layer.

For the tests and the examples as well:

```bash
uv sync
```

Measured on 2026-08-28 into two empty environments: `uv pip install -e .` on
Python 3.13.5 and `pip install -e .` on 3.14.7. Both then answered
`repo.about().repository_version` with `11.0` against the staging instance.

## Contents

- [Installing](#installing)
- [Why](#why)
- [What works today](#what-works-today)
  - [Where a name comes from](#where-a-name-comes-from)
  - [Searching with labels instead of URIs](#searching-with-labels-instead-of-uris)
  - [Collections](#collections)
  - [Writing — with a read-back check](#writing--with-a-read-back-check)
  - [For AI applications](#for-ai-applications)
  - [The LLM gateway](#the-llm-gateway)
  - [The extraction service — text the repository does not have](#the-extraction-service--text-the-repository-does-not-have)
  - [The metadata agent — what belongs in a content type's JSON](#the-metadata-agent--what-belongs-in-a-content-types-json)
  - [Flows — a use case in one call](#flows--a-use-case-in-one-call)
- [Where this is going](#where-this-is-going)
- [What the library knows for you](#what-the-library-knows-for-you)
  - [Publishing — the step edu-sharing does not take](#publishing--the-step-edu-sharing-does-not-take)
  - [When a write half-succeeds](#when-a-write-half-succeeds)
  - [Ratings and comments](#ratings-and-comments)
  - [Proposing instead of writing, and handing on for review](#proposing-instead-of-writing-and-handing-on-for-review)
  - [Preview images, paging, renaming a collection](#preview-images-paging-renaming-a-collection)
  - [Groups — who may moderate](#groups--who-may-moderate)
  - [Where a node sits — and who curated it](#where-a-node-sits--and-who-curated-it)
  - [Child objects — documents that belong to one material](#child-objects--documents-that-belong-to-one-material)
  - [Relations — nodes that belong together](#relations--nodes-that-belong-together)
  - [Curated pages — what a collection renders](#curated-pages--what-a-collection-renders)
  - [What this library does not do](#what-this-library-does-not-do)
- [Fields and files the short names do not cover](#fields-and-files-the-short-names-do-not-cover)
- [Examples](#examples)
- [Structure](#structure)
- [Rebuilding the generated layer](#rebuilding-the-generated-layer)
- [Logging](#logging)
- [Tests](#tests)
- [Licence](#licence)

## Why

edu-sharing has 318 REST paths and behaviour you cannot guess: which write route
applies to which property, that a `200 OK` is **no** proof of persistence, that
there are two collection searches and neither is a superset of the other. This
library encapsulates the measured behaviour so that others need not rediscover
it.

**Repository-agnostic** means: vocabularies are resolved at runtime against *the
metadata set of the instance at hand*, not against a built-in table.
`subject="Biologie"` therefore also works on a repository that has nothing to do
with WirLernenOnline.

## What works today

```python
from edusharing import Repository

with Repository("https://repository.staging.openeduhub.net") as repo:
    about = repo.about()
    print(about.repository_version)   # 11.0
    print(about.plugins)              # ['mongo-plugin', 'b-api', ...]

    who = repo.whoami()               # who am I running as?
    print(who.authority)              # 'esguest' = anonymous
```

`AsyncRepository` is the same surface for asynchronous code; the synchronous one
also works inside a notebook, where an event loop is already running.

Credentials come from the environment (`EDU_SHARING_URL`, `EDU_SHARING_USER`,
`EDU_SHARING_PASSWORD`) or directly:

```python
repo = Repository(url, auth=("user", "password"))
```

Every one of the 389 operations is reachable, even without a method of its own:

```python
values = await repo.raw.json("GET", "/config/v1/values")
```

### Where a name comes from

Almost everything is a single import:

```python
from edusharing import Repository, Node, SearchResult, NotFoundError
```

| Import | What lives there |
|---|---|
| `from edusharing import …` | the repository, its results, its errors |
| `edusharing.agent` | building blocks for AI use: safety, sanitising, formatting |
| `edusharing.bapi` | the LLM gateway — a separate service |
| `edusharing.extraction` | the text-extraction service — likewise |
| `edusharing.metadata_agent` | the metadata agent — likewise |

The flows need no import of their own: they hang off a connection, as
`repo.flows.search(...)`. The two neighbouring services get a module of their
own because they have an address of their own — a connection to a repository
says nothing about whether they exist.

### Searching with labels instead of URIs

```python
with Repository(url, metadataset="mds_oeh") as repo:
    result = repo.search("Photosynthese", subject="Biologie", limit=5)

    for unresolved in result.unresolved:   # unresolvable filters — never silent
        print("!", unresolved)             # "ccm:taxonid='Bio' — did you mean: Biologie?"

    for hit in result.hits:
        print(hit.title, hit.labels("ccm:taxonid"), hit.url)
```

`subject="Biologie"` is resolved against **this** instance's metadata set, not
against a built-in table. `repo.metadatasets()` says which sets exist; the choice
changes what is filterable and what gets found.

Facets count server-side across the whole result set:

```python
result = repo.search("Photosynthese", facets=["ccm:educationalcontext"])
for value in result.facets[0].values:
    print(value.count, value.value)
```

**As a flow:** `repo.flows.search("Photosynthese", subject="Biologie")`
sends the same two requests and answers with a `dict`;
`repo.flows.vocabulary("subject")` lists what a field accepts.

### Collections

```python
repo.find_collections("Optik")
```

Queries **both** of edu-sharing's collection searches concurrently and merges
them — neither is a superset of the other. For "Deutsch" their overlap was
measured as **zero**.

Try it: `python docs/examples/01_connect.py` and `02_search.py`

**As a flow:** `repo.flows.find_collections("Optik")`, and
`repo.flows.collection_contents(id)` to open one.

### Writing — with a read-back check

```python
node = repo.node("abc-123")
node = node.update(title="New title")       # read back, raises on a silent drop
node = node.add_keywords("Weimar (Ort)")    # extends, does not replace
node = node.content.upload(data, filename="material.pdf", mimetype="application/pdf")
```

Why this is not trivial: **edu-sharing reports `200 OK` for writes that did not
happen.** A property the metadata set does not know is discarded silently —
status 200, value gone. `update()` therefore reads back:

```
SilentDropError: Not stored: ccm:oeh_collection_compendium_text
  (HTTP 200, absent or different after reading back). Two usual causes: the
  property is not provided for in this instance's metadata set, or the write
  permission is missing. node.set_property(...) bypasses the metadata set's
  filtering.
```

The library does **not** divert to `set_property` by itself: the filtering is a
decision of the repository, not a glitch. Bypassing it stays a deliberate step.

Collections:

```python
collection = repo.create_collection("My collection")   # private by default
repo.add_to_collection(collection.id, node.id)         # a reference, not a copy
```

Try it: `python docs/examples/03_write.py` — creates a throwaway folder of its
own and removes it afterwards.

**As a flow:** `repo.flows.add_material(…)` and
`repo.flows.update_material(…)` — the same requests, a `dict` back.
`10_two_levels.py` runs both versions side by side and counts them.

### For AI applications

`edusharing.agent` is framework-neutral — no MCP, no LangChain import:

```python
from edusharing.agent import as_result, as_untrusted, format_results, is_safe_url

result = await as_result(                        # errors as results, not exceptions
    repo.search("Photosynthese", subject="Biologie"),
    format=lambda r: format_results(r, max_chars=1500),
)
print(result.text)                               # id and url survive any budget

if is_safe_url(hit.source_url):                  # SSRF: URLs from foreign data
    ...
prompt = as_untrusted(hit.description,           # invisible control chars out,
                      label=f"Material {hit.id}")  # marked as foreign material
```

And before writing, show what would happen:

```python
from edusharing.agent import plan_update

plan = await plan_update(node, title="New title")
print(plan.describe())        # "cclom:title: 'Old'  ->  'New title'"
if plan.has_changes:
    node = await plan.apply()
```

### The LLM gateway

```python
from edusharing.bapi import BildungsAPI

async with BildungsAPI.from_env() as llm:        # B_API_KEY and B_API_BASE_URL
    answer = await llm.chat("Summarise: …")
    print(llm.last_model)                        # whose answer was that?
```

**Both variables, and there is no default address.** Until 2026-08-28 this
client fell back to a staging gateway, so setting only `B_API_KEY` sent your key
to a host you had not chosen. `TextExtraction` beside it had always refused
exactly that; the two services contradicted each other in the same library. The
key travels as `X-API-KEY`, not as a Bearer token.

Without a fixed model id the least loaded ready text model is chosen — and the
next one if needed: `status: ready` does not mean a model answers. The quirks of
the model families (`max_completion_tokens` for GPT-5/o, thinking switched off
for Qwen3 — but not for Mistral) live in `bapi.policy`.

**The gateway forwards the OpenAI surface**, not only chat:

```python
vectors = await llm.embeddings(["Photosynthese", "Zellatmung"],
                               model="text-embedding-3-small", provider="openai")
verdict = await llm.moderate(text, model="omni-moderation-latest",
                             provider="openai")   # .flagged, .categories, .scores
pictures = await llm.images("ein Baum", model="dall-e-3")   # .url or .b64
await llm.call("audio/speech", {...})             # anything else, as repo.raw
```

No model is guessed here — `chat()` may do that because a measured policy backs
it, and there is none for these. **The provider decides what is possible:**
measured 2026-08-28, `academiccloud` lists 16 models and none of them embed or
moderate, while `openai` lists 132 including both.

The endpoint list was measured, not read: `/v3/api-docs` describes only the
hand-written controllers and knows neither `/embeddings` nor `/chat/completions`.
Posting an empty body to each candidate separates them — `403` means the gateway
does not forward the route at all, anything else means it does. On that list:
`chat/completions`, `completions`, `embeddings`, `moderations`, `responses`,
`images/generations`, `images/edits`, `audio/*`, `files`, `batches`,
`fine_tuning/jobs`, `vector_stores`. **Not** on it: `rerank`.

Try it: `python docs/examples/04_agent_blocks.py`

### The extraction service — text the repository does not have

A repository stores the full text of the files it hosts. For material that only
*links* somewhere (`ccm:wwwurl`) it has nothing, because the page is not its
file. An edu-sharing installation normally runs a second service for that.

```python
from edusharing.extraction import TextExtraction

async with TextExtraction.from_env() as service:   # EDU_SHARING_TEXT_EXTRACTION_URL
    result = await service.text_of("https://example.org/article")
    print(result.lang, result.char_count, result.text[:200])
```

Full text of a node, from wherever it is available:

```python
node = await repo.node(node_id)
text = await node.content.text()                  # what the repository stored
if not text and node.get("ccm:wwwurl"):
    got = await service.text_of(node.get("ccm:wwwurl"), max_chars=20_000)
    text = got.text                                # got.reason says why, if empty
```

**No text is a normal outcome, not an error.** `reason` names the cause:
`not_http`, `private_host`, `dns_failed` or `no_text` — kept apart so "we would
not fetch that" never reads as "the page had no text".

Measured 2026-08-28 against the openeduhub service (FastAPI, `c766f2e5`):

* **An edu-sharing download URL gives 424.** The service cannot read what the
  repository itself hosts — `node.content.text()` stays responsible for that.
  Without knowing this you look for the fault in your own code.
* **`status` is the target page's**, not the service's: a 200 from the service
  can carry a 404 from the page.
* **`method="browser"` is not simply better.** On one page `simple` returned the
  article and `browser` returned the cookie banner. They are two attempts, not a
  ranking; if one yields nothing, try the other.

**There is no default address**, and that is deliberate: each installation runs
its own service, and a default pointing at a staging one used to send production
material URLs into a foreign environment. Unset means no client.

**The URL is yours, the fetching is someone else's.** Every check runs *before*
anything is sent: scheme, then the host as a literal address, then what it
resolves to — private, loopback and link-local ranges are refused, the cloud
metadata endpoint among them. One gap stays open and is named in the module: a
redirect happens inside the service's process, where this library cannot see it.

### The metadata agent — what belongs in a content type's JSON

`ccm:oeh_extendedType` says *what* a resource is; `ccm:oeh_extendedData` carries
a free-form JSON area beside it. Which fields belong in there is in no metadata
set — the repository stores that text and validates nothing. Only this service
knows, and only at runtime:

```python
from edusharing.metadata_agent import MetadataAgent   # METADATA_AGENT_URL

async with MetadataAgent.from_env() as agent:
    kind = await agent.content_type_for(node.get("ccm:oeh_extendedType"))
    schema = await agent.schema(kind.schema_file)     # 45 fields for an organisation
```

`content_types()` lists the eight it describes, with the vocabulary URI each one
answers to. **Do not derive the file name from the type** — measured 2026-08-28,
`profession` is `occupation.json` and `didactic_concepts` is
`didactic_planning_tools.json`. The authoritative mapping sits inside
`core.json` itself and is what this method reads.

**The repository knows more types than the agent.** Ten in `mds_oeh`, eight
here: `ai_prompt` and `ai_skill` have no schema, so `content_type_for` answers
`None` for them — not an error, just a node the agent has nothing to say about.

Schemas come back unshaped, and that is deliberate: every field carries a label,
a description, examples **and an extraction prompt** in two languages. Casting
that into types of our own would freeze a foreign service's structure into this
library.

### Flows — a use case in one call

Everything above is close to edu-sharing and returns objects. That is right for
Python, and wrong for anything that has to pass the result onwards. `repo.flows`
does the same work in one call and answers in JSON:

```python
result = repo.flows.search("Photosynthese", subject="Biologie")
json.dumps(result)                    # works -- that is the point

created = repo.flows.add_material(    # lands in your home folder
    "Photosynthese einfach erklärt",
    url="https://example.org/m",
    subject="Biologie",               # resolved while writing, too
)
if created["unresolved"]:             # values that did NOT stick
    ...
```

Twenty flows: `search`, `search_all`, `vocabulary`, `describe`,
`describe_many`, `related`, `placement`, `relations`, `child_objects`,
`browse_tree`, `search_in_collection`, `collection_stats`,
`find_collections`, `collection_contents`, `page`, `find_pages`,
`add_material`, `update_material`,
`build_collection`, `delete`. Full input and output for each in
**[docs/FLOWS.md](docs/FLOWS.md)**.

`search` also takes `rerank=True`. edu-sharing ANDs every query word, so a
naturally phrased question finds nothing: measured, *"Bruchrechnung"* has
1591 records and *"Ich suche ein Arbeitsblatt zur Bruchrechnung"* has
**zero**. Reranking asks several query variants and reorders by relevance --
it costs one request per variant and is off by default.

**Not everything has a flow, and that is deliberate.** Ratings, comments,
proposals, the editorial handover, groups, preview images and renaming a
collection each stay with one endpoint family. A flow earns its place by
composing several — `placement` asks two, `search_all` three. Wrapping a
single family would change the shape of the answer and save nothing. Those
use cases live at the API level, above.

Try it: `python docs/examples/05_flow_search.py`, `06_flow_create.py`,
`07_flow_collection.py`, `08_flow_rerank.py`, `09_flow_browse.py`

## Where this is going

An MCP server as a thin adapter over `edusharing.agent` — the building blocks
are in place, the server itself is deliberately not part of the library.

## What the library knows for you

A few behaviours of edu-sharing cannot be guessed. They are encoded here rather
than documented:

- **A bearer token is rejected, not sent.** edu-sharing knows only basic auth and
  session cookies — and *ignores* a bearer header instead of rejecting it. The
  request would run as a guest without anyone noticing.
- **HTTP 500 sometimes means "not signed in".** A guest hitting a protected
  endpoint gets 500 with "Not allowed for guest user". That becomes an
  `AuthenticationError` — and is not retried.
- **The password only goes to the configured repository.** Even when a URL from
  response data points elsewhere.
- **Having a vocabulary does not mean you can filter on it.** `ccm:taxonid`
  carries a vocabulary in both metadata sets checked, but is filterable only in
  `mds_oeh`. When the search hits that, the library adds the missing hint to the
  server message.
- **`pattern:""` lists all vocabulary values** — the obvious `"-all-"` silently
  returns an empty list.
- **Unresolvable filters are reported, not dropped.** A discarded constraint
  returns hits nobody asked for, and looks like an answer while doing so.
- **`200 OK` is no proof of persistence** when writing — see above.
- **`downloadUrl` does not prove a file exists.** It is always set; a node
  without content answers 200 with zero bytes. `content.has_content` checks the
  hash, which also tells a 0-byte file from *no* file.
- **Keywords are a shared list.** `add_keywords` extends; setting
  `cclom:general_keyword` directly deletes other people's entries.
- **Nothing an application creates is visible to anyone else.** Not after filing
  it into a public collection, not with `scope="PUBLIC"` — see below.
- **Setting one permission would delete the rest.** The repository's `POST`
  replaces the whole local access list; `grant()` merges into it.
- **A rating of `0` is a vote, not a reset.** It lowers the average; `unrate()`
  is what removes a vote.
- **A comment body is stored byte for byte.** Sending it as JSON stores the
  quotation marks with it.

### Publishing — the step edu-sharing does not take

Material an application creates is readable by its creator and by **nobody
else**. Filing it into a public collection does not change that, and neither
does `scope="PUBLIC"` on the collection — both measured on 2026-08-28, both
answering `200` along the way.

```python
node = repo.create_node(folder.id, name="material.txt", title="Photosynthese")
node.is_public                       # False — free, the response carries it
node.permissions.publish()           # True: published now
node.permissions.publish()           # False: it already was
```

`publish()` merges. The repository's own `POST` **replaces** the whole local
access list, so publishing without merging would quietly take away everyone
else's permissions — with a `200` in front of it.

```python
node.permissions.grant("GROUP_teachers", "Coordinator")
node.permissions.revoke("GROUP_teachers")
rights = node.permissions.get()
rights.is_public                     # inherited access counts too
rights.allows("alice", "Consumer")
```

A node in a public folder is public without an entry of its own. `unpublish()`
says so rather than reporting a privacy the node does not have:

```python
node.permissions.unpublish()         # ConflictError: public through its parent
```

The flows carry the same question. `public` is in every answer, and the switch
is off by default because reading cannot be taken back:

```python
repo.flows.add_material("Photosynthese", publish=True)["public"]   # True
```

### When a write half-succeeds

edu-sharing answers HTTP 200 to writes it does not fully store. The library
reads back after every write -- creating included -- and raises `SilentDropError`
naming the properties that did not arrive.

Three measured causes:

| Cause | Example | What to do |
|---|---|---|
| Not in the metadata set | `ccm:oeh_collection_compendium_text` | `set_property()` writes past it |
| Derived by the repository | `ccm:oeh_lrt_aggregated` from `ccm:oeh_lrt` | write the source field |
| A rule of the node type | `cm:title` on a new `cm:folder` | set it afterwards with `update()` |

`create(verify=False)` switches the check off for a field you know is derived.

**And one that arrives with the right status and the wrong meaning.** Measured
2026-08-28 with valid credentials: 20 nodes per round, 5 rounds — sent one
after another, `0 of 100` requests answered `401`; sent all at once, `9 of
100` did. Same nodes, same credentials. So the transport retries a `401`
**once** when the connection is signed in, and not at all when it is anonymous
(there it means "this needs a login" and will mean it again). Once, not
`max_retries` times — an extra request is a fair price for a measured hiccup,
three would be a penalty for a typo in a password.

And three errors that arrive wearing the wrong status, so that `except
NotFoundError` actually catches them — and so the transport does not retry
three times what can never succeed:

| Sent as | Really | Where |
|---|---|---|
| `500 Not allowed for guest user` | not signed in | any protected endpoint |
| `500 UsageException: Node does not exist` | `404` | `/usage/v1/…/collections` |
| `500 AccessDeniedException` | `403` | `…/parents` on foreign material |
| `500 NotAnAdminException` | `403` | `/rating/…/history`, group members |

### Ratings and comments

What a community leaves on a node. Reading a rating costs nothing — the node
response carries the summary, like `isPublic` does:

```python
node = repo.node("abc-123")
node.rating                          # Rating(4.0 aus 3) or None
node.rate(4, "Sehr brauchbar")       # writes, then reads the new average back
node.unrate()                        # takes this account's vote back
```

> **A rating of `0` is refused.** Measured on 2026-08-28: it does *not* take a
> rating back — the node then shows `count: 1, rating: 0.0`, so the zero counts
> as a vote and drags the average down. `unrate()` is what takes it back.

```python
node.comments.list()                 # [Comment('alice': 'Sehr brauchbar')]
c = node.comments.add("Erster")
node.comments.add("Antwort", reply_to=c.id)
node.comments.edit(c.id, "Nachgebessert")
node.comments.delete(c.id)
```

> **The comment body is stored verbatim.** edu-sharing does no JSON parsing
> here, so sending the text through `json=` would store `"Erster"` — quotation
> marks and all. The library sends raw UTF-8 bytes with an
> `application/json` content type, which is what the endpoint wants. Editing is
> `POST` on the comment; a `PUT` there creates a comment *on the comment* and
> answers 500.

### Proposing instead of writing, and handing on for review

Two steps a machine should take *instead* of writing: propose a value for a
person to weigh, and put a record into an editorial queue.

```python
node = repo.node("abc-123")
s = node.suggestions.propose("ccm:taxonid", uri, "The title names cells", confidence=0.9)
node.suggestions.list()              # [Suggestion('ccm:taxonid'='…', PENDING)]
node.suggestions.decide([s.id])      # ACCEPTED — see the warning
node.suggestions.decide([s.id], accept=False)
```

> **Accepting does not write the value.** Measured on 2026-08-28 and by
> `wlo-mcp-sc` before that: after `ACCEPTED` the node's keywords were still
> empty. `/suggestions/v1` is a staging area with a record — who proposed what,
> who decided what. Putting the value on the node stays a separate, deliberate
> write.
>
> The ids also go in the **query**, not the body. Sent as a body they are
> ignored and every suggestion stays `PENDING` — with a 200 in front of it, so
> `decide()` reads the statuses back.

```python
node.workflow.submit("GROUP_redaktion", "100_tocheck", "Bitte prüfen")
node.workflow.history()              # newest first
```

`status` has no default: the vocabulary belongs to the instance (WLO uses
`100_tocheck`), and guessing would file material into a queue that does not
exist.

### Preview images, paging, renaming a collection

```python
node.preview_url                     # None when it is only a type icon
node.content.set_preview(png_bytes)  # multipart field "image", not "file"
node.content.delete_preview()

page = repo.nodes.children(folder_id, limit=50, offset=0, only="files")
page.nodes, page.total, page.offset

repo.collections.update(collection_id, title="Neu", description="…")
```

> **A preview url is always there** — even for a node without one, and even
> after deleting one. The repository serves a type icon under it. `isIcon` is
> what tells them apart, which is why `preview_url` returns `None` rather than a
> url that shows a generic file symbol. Same trap as `downloadUrl`.

> **`repo.nodes.children()` is not `node.children`.** The first is the plain
> listing, paged and sorted; the second returns the *child objects* — the
> documents belonging to one piece of material. Paging has a default sort
> because paging over an unordered listing repeats some entries and misses
> others.

> **Renaming needs `ref.id` in the body**, although the id is in the path
> already — without it, `500 NullPointerException`. It also needs a `title`,
> so changing only the description reads the existing one first. And the
> description belongs *inside* the `collection` object: as
> `properties["cm:description"]` it is silently dropped. A new title changes
> `cm:name` too.

### Groups — who may moderate

```python
for group in repo.people.memberships():
    print(group.name, group.display_name, group.type)   # GROUP_ORG_… · AI-Compliance · EDITORIAL

repo.people.group("GROUP_ORG_AI-Skills")
repo.people.members("GROUP_ORG_AI-Skills")   # [Member('alice'), Member('GROUP_x', Gruppe)]
```

`Member.is_group` matters: a group can contain groups, and treating a nested
one as a person answers "who may moderate" wrongly.

> **Reading members needs management rights, not membership.** Measured:
> for a group one merely belongs to, the endpoint answers `500
> AccessDeniedException`. The library translates that to `PermissionDeniedError`
> — as a server error the transport would retry it three times.
>
> The endpoint also defaults `maxItems` to **10**, so a group of fifty would
> come back as a group of ten without saying so. The library asks for a hundred.

```python
repo.people.create_group("GROUP_projekt", display_name="Projekt")
repo.people.add_member("GROUP_projekt", "alice")
repo.people.remove_member("GROUP_projekt", "alice")
repo.people.delete_group("GROUP_projekt")
```

> **These four are not verified against a live instance.** The test account
> answers 403 on `POST /iam/v1/groups/…`, so only the request shape is proven —
> method, path, body, against the OpenAPI model. That a repository accepts them
> is unproven, and the docstrings repeat it.

### Where a node sits — and who curated it

Two questions that look alike and are not. A collection holds a *reference*: the
node it points at has its own parent somewhere else entirely. A node in ten
collections still has exactly one parent chain.

```python
node = repo.node("abc-123")
[f.title for f in node.parents()]      # nearest first — where it lives
[c.title for c in node.collections()]  # who curated it
```

Or both in one call, with the path turned around for printing:

```python
repo.flows.placement("abc-123")
# {"title": "…", "path": [top, …, nearest], "collections": [...], "scope": "MY_FILES"}
```

`scope` says how far the path reaches. It stops at the boundary of what the
account may read — asking for the complete path answers **403** for an ordinary
account, measured — so a truncated path is reported as such instead of passing
for a complete one.

### Child objects — documents that belong to one material

An answer sheet, a handout, a second file format: edu-sharing keeps those under
the main node, not beside it.

```python
node = await repo.node(node_id)
await node.children.add(pdf, filename="loesung.pdf", mimetype="application/pdf")
await repo.flows.child_objects(node_id)
```

The three parameters that create one cannot be guessed —
`ccm:io_childobject` is an aspect, not a type, and without
`assocType=ccm:childio` the repository answers HTTP 500. Details in
[docs/FLOWS.md](docs/FLOWS.md).

### Relations — nodes that belong together

A series and its episodes, a worksheet and the video it is based on: edu-sharing
keeps these as **relations** between nodes that stand side by side, separate
from collections.

```python
await repo.relations.create(part_id, "isPartOf", series_id)
await repo.flows.relations(series_id)     # the series reports "hasPart"
```

The opposite direction is kept automatically. The API also distinguishes
machine-proposed links from confirmed ones (`ai_generated`, `approve`), which
matters when a model does the proposing.

**The `metadata` argument does not survive.** edu-sharing 11.0 accepts it with
HTTP 200 and stores nothing — measured 2026-08-28 in three shapes, the last
straight at the endpoint, every time `metadata: {}` came back. `create()`
therefore reads it back and raises `SilentDropError`; the link itself is made.
Keep the reasoning on the nodes, or in your own store. Details in
[docs/FLOWS.md](docs/FLOWS.md#relations--what-a-node-is-linked-to).

### Curated pages — what a collection renders

edu-sharing's page builder: a collection may carry a landing page built from
*swimlanes*, each holding widgets, each widget pointing at a node.
WirLernenOnline calls these “Themenseiten”, but nothing about them is WLO's —
the properties belong to edu-sharing's content model, and any instance using
the page builder stores them the same way.

```python
node = await repo.node(collection_id)
page = await node.page.get()              # None when this collection has none
if page:
    print(page.rendered.title, len(page.rendered.swimlanes))
    await node.page.render(other_variant_id)   # immediately public
```

Or as a flow, JSON-ready:

```python
await repo.flows.find_pages("Deutsch")    # which collections carry one
await repo.flows.page(collection_id, resolve_widgets=True)
```

Three things worth knowing before you use it, all measured on 2026-08-28:

* A page document **without** a `default` renders the *first* variant of its
  list. `by_position` tells the two states apart — they look identical to a
  visitor and are not the same thing to a write.
* **Having a page is not having content.** One measured collection carries a
  page whose single variant configures zero swimlanes.
* **Nothing validates these documents.** The property route stores the literal
  string `"not json at all"` with a `200`. So reading never raises on a broken
  one (`readable` says so) and `render()` refuses everything it cannot prove,
  editing the stored document rather than composing a new one.

Details in [docs/FLOWS.md](docs/FLOWS.md#page--the-curated-page-a-collection-renders).

### What this library does not do

* **Summarise Wikipedia.** Not edu-sharing. Its full article text is reachable
  through the extraction service like any other page; a Wikipedia-shaped API
  client is somebody else's package.
* **Fetch a URL itself.** The extraction service does the fetching, in its own
  process. This library sends it an address and checks that address first.
* **Parse repository-specific document conventions.** Finding a document is
  generic and is shown under *Fields and files* below; what its Markdown means
  is the convention of the people who wrote it.
* **Create, delete or reorder page variants, or edit swimlanes.** Only which
  variant renders. A malformed page document does not fail on write — it fails
  later, in the page builder, on a page the public is reading.

## Fields and files the short names do not cover

The aliases (`subject`, `level`, …) are a convenience for the handful of
properties people filter by. Everything else is reachable too — the library does
not restrict what a node may carry.

**Any property, read and written:**

```python
node = await repo.node(node_id)
node.get("ccm:oeh_collection_compendium_text")       # read one
node.get_all("ccm:taxonid")                          # all values
node.properties                                      # everything at once

await node.update(properties={"ccm:custom": ["x"]})  # write, verified
await node.set_property("ccm:custom", "x")           # write, bypassing the mds
```

`update()` is checked against the metadata set and raises `SilentDropError` when
edu-sharing accepts a write and does not store it. A property the metadata set
does not provide for — the WLO compendium text is one — has to go through
`set_property()`, which writes directly. Measured 2026-08-27:
`ccm:oeh_collection_compendium_text` is dropped by `update()` on `mds_oeh` and
stored by `set_property()`.

**A free-form JSON payload is just another property.** Some instances model a
content type plus an open data area — WLO calls them `ccm:oeh_extendedType`
(a vocabulary: KI-Prompt, Organisation, Person, Veranstaltung, …) and
`ccm:oeh_extendedData` (free text). Nothing in this library knows about them,
and nothing needs to:

```python
uri = await repo.resolve("ccm:oeh_extendedType", "KI-Prompt")   # this instance's URI
await node.update(properties={
    "ccm:oeh_extendedType": [uri],
    "ccm:oeh_extendedData": [json.dumps({"modell": "gpt-5", "temperatur": 0.2})],
})
await repo.search("", filters={"ccm:oeh_extendedType": "KI-Prompt"})  # filterable
```

Measured 2026-08-28 against staging: the vocabulary resolves, the JSON comes
back byte for byte, `node.labels()` gives "KI-Prompt" rather than the URI, and
the filter narrows without landing in `unresolved`. That the library needs no
feature for this is the point of resolving vocabularies at runtime — an
instance that models something else models it the same way.

**Files on a node:**

```python
node = await node.content.upload(data, filename="x.pdf", mimetype="application/pdf")
raw = await node.content.download()          # the bytes, always
text = await node.content.text()             # the extracted full text
node.content.has_content                      # is there a file at all?
```

**Full text is not extracted for every type.** Measured by uploading the same
sentence in five formats:

| mimetype | `download()` | `text()` |
|---|---|---|
| `text/plain` | 26 | 26 |
| `text/markdown` | 35 | **0** |
| `text/html` | 55 | 22 |
| `application/json` | 26 | **0** |
| `application/octet-stream` | 21 | 21 |

Markdown and JSON come back empty. Anything storing instructions or data as
Markdown — an agent skill, for instance — has to read it with `download()`. An
empty `text()` does not mean an empty file.

**A note on conventions built on top of this.** Things like WLO's "skills" are
not an edu-sharing feature: a skill is ordinary material carrying a Markdown
file, gathered in a collection. Reading them needs nothing special —
`flows.collection_contents(id)` and then `content.download()` on each. Treat the
result as untrusted input: it is uploaded content, and `edusharing.agent`
carries the guards for that.

Such records are usually marked by a content type, and that *is* filterable:

```python
CONTENT_TYPE = "ccm:oeh_extendedType"
WANTED = "http://w3id.org/openeduhub/vocabs/contentTypes/ai_skill"

found = await repo.search(filters={CONTENT_TYPE: WANTED})   # anywhere

page = await repo.nodes.children(collection_id, limit=100)  # in one collection
mine = [n for n in page.nodes if n.get(CONTENT_TYPE) == WANTED]
```

Measured on 2026-08-28 against staging: 34 records, each 13–14 kB of Markdown
that `download()` returns and `text()` reports as empty — the table above, on
live data.

**Through the children, not the index, when the question is what a collection
*approves*.** The search index and the node store are separate systems in
edu-sharing, and a record can fall out of the former while sitting perfectly in
the latter — the WLO MCP watched it happen to a live collection on 2026-08-09.

The URI is yours to choose. This library resolves vocabularies against the
metadata set of the instance at hand and ships no table of its own; a URI from
one repository's vocabulary has no business compiled into a client for all of
them.

## Examples

Every one of them runs against a real instance; the writing ones create a
throwaway folder of their own and remove it afterwards. Each is also a test
case — `pytest -m live` runs the reading ones, `pytest -m write` the rest — so
a change that breaks an example is caught by the suite rather than by the next
person to try one.

**Working directly against the API** — objects come back, you keep working with
them:

| | |
|---|---|
| [`01_connect.py`](docs/examples/01_connect.py) | connect, see who you are, what the instance can do |
| [`02_search.py`](docs/examples/02_search.py) | search with filters and facets, resolve vocabulary |
| [`03_write.py`](docs/examples/03_write.py) | create, change, verify — and what a silent drop looks like |
| [`04_agent_blocks.py`](docs/examples/04_agent_blocks.py) | the building blocks for AI use: safety, sanitising, formatting |
| [`11_publish.py`](docs/examples/11_publish.py) | make material visible to others — the step nothing does for you |
| [`15_full_text.py`](docs/examples/15_full_text.py) | the full text of a material, from the repository or the extraction service |
| [`16_editorial.py`](docs/examples/16_editorial.py) | comment, rate, propose, hand over for review — the surfaces with no flow |

**Working through flows** — a `dict` comes back, ready to hand on:

| | |
|---|---|
| [`05_flow_search.py`](docs/examples/05_flow_search.py) | ask the vocabulary, search, describe one hit |
| [`06_flow_create.py`](docs/examples/06_flow_create.py) | create with vocabulary — and what an unknown value does |
| [`07_flow_collection.py`](docs/examples/07_flow_collection.py) | build a collection, fill it, watch a partial success |
| [`08_flow_rerank.py`](docs/examples/08_flow_rerank.py) | what a framing word costs, and what `rerank=True` recovers |
| [`09_flow_browse.py`](docs/examples/09_flow_browse.py) | find collections, open one, change what is inside |
| [`12_flow_place.py`](docs/examples/12_flow_place.py) | one query for material and collections, then where a hit sits |
| [`13_flow_tree.py`](docs/examples/13_flow_tree.py) | walk a collection, search inside it, count what is in it |
| [`14_flow_page.py`](docs/examples/14_flow_page.py) | read the curated page a collection renders, widgets and all — then the same page as objects |

**Both levels side by side:**

| | |
|---|---|
| [`10_two_levels.py`](docs/examples/10_two_levels.py) | the same use case written twice, counting the requests each sends |

Start with `10_two_levels.py` if you are deciding which level to write against.
It shows that `search` and `add_material` send exactly the same requests either
way — the flow changes the output shape, not the work — and where a flow does
save a round trip.

## Structure

| Layer | Content |
|---|---|
| `edusharing.agent` | Building blocks for AI use: formatting, token budget, preview-then-confirm, sanitising |
| `edusharing.flows` | Twenty flows: one use case, one call, a `dict` back |
| `edusharing` (resources) | `search()`, `node()`, `collection()` — objects back |
| Profile & MDS | Vocabulary resolution, property capabilities, choosing the write route |
| Transport | httpx, auth, retry, concurrency, read-back check |
| `_generated` | All 389 operations, generated from `openapi.json` |

Beside it, not inside it — two services with their own address, built on their
own because a connection to a repository says nothing about whether they exist:

| Module | Service |
|---|---|
| `edusharing.bapi` | The LLM gateway (`B_API_KEY`) |
| `edusharing.extraction` | The text-extraction service (`EDU_SHARING_TEXT_EXTRACTION_URL`) |
| `edusharing.metadata_agent` | The metadata agent: which fields a content type carries (`METADATA_AGENT_URL`) |

## Rebuilding the generated layer

```bash
python scripts/generate_client.py --from-instance https://repository.staging.openeduhub.net
```

The reference spec (edu-sharing 11.0) lives under `openapi/`. The script
normalises it first — without that step the generator emits invalid Python; the
reasoning is in the script's docstring.

## Logging

At `INFO` and `DEBUG` the library is silent by default, as a library should be.
A service switches those on where it needs them:

```python
import logging

logging.getLogger("edusharing").setLevel(logging.INFO)   # retries, model changes
logging.getLogger("edusharing").setLevel(logging.DEBUG)  # every request as well
```

`INFO` reports what you would otherwise puzzle over after the fact: a retry, and
which b-api model answered after an earlier candidate declined. `DEBUG` adds
method and URL of every request.

`WARNING` is the exception to the silence, in four places, and deliberately so:
Python prints those to stderr even with no logging configured. Three are the
extraction service refusing a host — a private address, one that would not
resolve, one that resolved into a private range. The fourth is a child object
that could be created but then neither filled nor removed; it stays behind
empty, and the error the caller gets is about the upload and does not know it
exists. Each names something a caller would otherwise never learn.

Headers are never logged. That is where the credentials live, and a log line is
aggregated, searched and kept.

## Tests

```bash
uv run pytest
```

Runs offline and deterministically. Tests against a live instance are separate:

```bash
EDU_SHARING_URL=https://repository.staging.openeduhub.net uv run pytest -m live
```

Write tests (`-m write`) need credentials and operate exclusively inside a
throwaway folder they create themselves.

The suites against the two neighbouring services skip themselves silently
without their own variable — `B_API_KEY` for the LLM gateway,
`EDU_SHARING_TEXT_EXTRACTION_URL` for the extraction service. A skip there means
"not configured", not "not covered".

## Licence

Apache-2.0
