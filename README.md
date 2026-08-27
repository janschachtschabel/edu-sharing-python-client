# edu-sharing for Python

Python client for [edu-sharing](https://edu-sharing.com) repositories and the
**b-api** (Bildungs-API, OpenEduHub) — **repository-agnostic** and
**async-first**.

> *Deutsche Fassung: [README.de.md](README.de.md).*

> **Status: work in progress.** Reading, searching and writing are in place and
> verified against edu-sharing 11.0 — including writes, against a live instance.
> The roadmap is in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

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

### Collections

```python
repo.find_collections("Optik")
```

Queries **both** of edu-sharing's collection searches concurrently and merges
them — neither is a superset of the other. For "Deutsch" their overlap was
measured as **zero**.

Try it: `python docs/examples/01_connect.py` and `02_search.py`

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

async with BildungsAPI.from_env() as llm:        # B_API_KEY, X-API-KEY (no Bearer)
    answer = await llm.chat("Summarise: …")
    print(llm.last_model)                        # whose answer was that?
```

Without a fixed model id the least loaded ready text model is chosen — and the
next one if needed: `status: ready` does not mean a model answers. The quirks of
the model families (`max_completion_tokens` for GPT-5/o, thinking switched off
for Qwen3 — but not for Mistral) live in `bapi.policy`.

Try it: `python docs/examples/04_agent_blocks.py`

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

Ten flows: `search`, `vocabulary`, `describe`, `relations`, `find_collections`,
`collection_contents`, `add_material`, `update_material`,
`build_collection`, `delete`. Full input and output for each in
**[docs/FLOWS.md](docs/FLOWS.md)**.

`search` also takes `rerank=True`. edu-sharing ANDs every query word, so a
naturally phrased question finds nothing: measured, *"Bruchrechnung"* has
1591 records and *"Ich suche ein Arbeitsblatt zur Bruchrechnung"* has
**zero**. Reranking asks several query variants and reorders by relevance --
it costs one request per variant and is off by default.

Try it: `python docs/examples/05_flow_search.py`, `06_flow_create.py`,
`07_flow_collection.py`, `08_flow_rerank.py`, `09_flow_browse.py`

## ⏳ Where this is going

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
matters when a model does the proposing. Details in
[docs/FLOWS.md](docs/FLOWS.md#relations--what-a-node-is-linked-to).

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

## Examples

Every one of them runs against a real instance; the writing ones create a
throwaway folder of their own and remove it afterwards.

**Working directly against the API** — objects come back, you keep working with
them:

| | |
|---|---|
| [`01_connect.py`](docs/examples/01_connect.py) | connect, see who you are, what the instance can do |
| [`02_search.py`](docs/examples/02_search.py) | search with filters and facets, resolve vocabulary |
| [`03_write.py`](docs/examples/03_write.py) | create, change, verify — and what a silent drop looks like |
| [`04_agent_blocks.py`](docs/examples/04_agent_blocks.py) | the building blocks for AI use: safety, sanitising, formatting |

**Working through flows** — a `dict` comes back, ready to hand on:

| | |
|---|---|
| [`05_flow_search.py`](docs/examples/05_flow_search.py) | ask the vocabulary, search, describe one hit |
| [`06_flow_create.py`](docs/examples/06_flow_create.py) | create with vocabulary — and what an unknown value does |
| [`07_flow_collection.py`](docs/examples/07_flow_collection.py) | build a collection, fill it, watch a partial success |
| [`08_flow_rerank.py`](docs/examples/08_flow_rerank.py) | what a framing word costs, and what `rerank=True` recovers |
| [`09_flow_browse.py`](docs/examples/09_flow_browse.py) | find collections, open one, change what is inside |

**Both levels side by side:**

| | |
|---|---|
| [`10_two_levels.py`](docs/examples/10_two_levels.py) | the same use case written twice, counting the requests each sends |

Start with `10_two_levels.py` if you are deciding which level to write against.
It shows that `search` and `add_material` send exactly the same requests either
way — the flow changes the output shape, not the work — and where a flow does
save a round trip.

## Rebuilding the generated layer

```bash
python scripts/generate_client.py --from-instance https://repository.staging.openeduhub.net
```

The reference spec (edu-sharing 11.0) lives under `openapi/`. The script
normalises it first — without that step the generator emits invalid Python; the
reasoning is in the script's docstring.

## Logging

The library is silent by default, as a library should be. A service switches it
on where it needs it:

```python
import logging

logging.getLogger("edusharing").setLevel(logging.INFO)   # retries, model changes
logging.getLogger("edusharing").setLevel(logging.DEBUG)  # every request as well
```

`INFO` reports what you would otherwise puzzle over after the fact: a retry, and
which b-api model answered after an earlier candidate declined. `DEBUG` adds
method and URL of every request.

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

## Licence

Apache-2.0
