---
name: edu-sharing-python
description: Using the edu-sharing-python-client library (import `edusharing`) — both levels (API objects and flow dicts), all 20 flows, the neighbouring services (b-api LLM gateway, text extraction, metadata agent), the measured traps, and the rules for putting it behind a model. Use when writing Python against an edu-sharing repository, building an MCP server or agent tool over WLO/OpenEduHub content, or when a call returned HTTP 200 and stored nothing. Trigger u.a. "edu-sharing Python", "edusharing library", "repo.flows", "SilentDropError", "Bibliothek nutzen", "Suche in Python", "Material anlegen Python", "MCP-Werkzeug edu-sharing", "b-api Python", "Textextraktion", "metadata agent schema", "welcher Aufruf für", "unresolved", "total_is_lower_bound".
---

# edu-sharing for Python — how to use it

*Deutsche Fassung: [SKILL.de.md](SKILL.de.md)*

The library at `github.com/…/edu-sharing-python-bib` (package
`edu-sharing-python-client`, import `edusharing`). It wraps edu-sharing's REST
API and three neighbouring services, and its central promise is that **a write
that did not happen is reported as a failure, not a success**.

**This skill covers the library.** For the raw REST API, WLO's own data model
(Quelldatensatz, Spider, replicationsource), licence keys or NGSearch body
fields, use `wlo-edu-sharing-api`. For instance addresses and environment
variable names, use `wlo-environments`. Those are the source of truth for
*deployment*; this one is the source of truth for *the Python surface*.

Written in English because the library's code and identifiers are English --
this is the version a model loads. [`SKILL.de.md`](SKILL.de.md) is the same
routing table for people who would rather read German; both are held to the
same tests, so neither can quietly omit a flow or invent a call.

---

## 1. Orientation in sixty seconds

```bash
uv pip install -e .        # not on PyPI yet
```

```python
from edusharing import Repository

with Repository("https://repository.staging.openeduhub.net") as repo:
    result = repo.search("Bruchrechnung", limit=5)
    for hit in result.hits:
        print(hit.title, hit.url)
```

Two levels, both permanent:

| | API level | Flow level |
|---|---|---|
| Reached as | `repo.search(...)`, `repo.node(...)` | `repo.flows.search(...)` |
| Returns | objects — `SearchResult`, `Node` | plain `dict`, ready for `json.dumps` |
| Good for | writing Python against edu-sharing | handing the answer on |
| Requests | one endpoint per call | one call, several endpoints |

**Rule of thumb:** if the result goes to a model, an MCP tool or an HTTP
response, use `repo.flows`. If you are writing the calling code yourself, use
the API level.

`Repository` is blocking. `AsyncRepository` is the same surface with `await`.
Use the async one inside an event loop, the blocking one everywhere else.

---

## 2. The instance is always a parameter

**Never hardwire an address.** The library has no default instance; every entry
point takes one, and no call below it takes an address of its own.

```python
repo = Repository(os.environ["EDU_SHARING_URL"], auth=(user, password))
repo = Repository.from_env()      # EDU_SHARING_URL / _USER / _PASSWORD
```

The three neighbouring services each take **their own** address and also have
no default — `from_env()` refuses without the variable rather than sending data
to a host nobody chose:

| Service | Class | Variable |
|---|---|---|
| LLM gateway (b-api) | `BildungsAPI` | `B_API_BASE_URL` + `B_API_KEY` |
| Text extraction | `TextExtraction` | `EDU_SHARING_TEXT_EXTRACTION_URL` |
| Metadata agent | `MetadataAgent` | `METADATA_AGENT_URL` |

Which concrete addresses belong to staging and production is **not** in this
skill and not in the library — see `wlo-environments`.

---

## 3. Which call answers which question

The complete list with input and output shapes is
[`docs/REFERENCE.md`](../../../docs/REFERENCE.md) /
[`docs/REFERENCE.de.md`](../../../docs/REFERENCE.de.md). This is the routing
table.

*(File links here are relative to the library's checkout. Copied into
`~/.claude/skills/` they name paths in that repository, not on disk.)*

### Finding things

| The task | The call |
|---|---|
| search material | `repo.flows.search(text, subject=…, limit=…)` |
| search material *and* collections at once | `repo.flows.search_all(text)` |
| find collections only | `repo.flows.find_collections(text)` |
| more like this node | `repo.flows.related(node_id, on=["subject", "level"])` |
| which values does a field allow | `repo.flows.vocabulary("subject")` |
| a poorly phrased query ("something about fractions") | `repo.flows.search(text, rerank=True)` |
| search *inside* one collection | `repo.flows.search_in_collection(id, text)` |
| find collections that render a curated page | `repo.flows.find_pages(text)` |

### Reading one thing

| The task | The call |
|---|---|
| everything about a node, as JSON | `repo.flows.describe(node_id)` |
| several nodes at once | `repo.flows.describe_many(ids)` |
| where does it sit (breadcrumb) | `repo.flows.placement(node_id)` |
| what is in this collection | `repo.flows.collection_contents(id)` |
| what hangs *under* this material | `repo.flows.child_objects(node_id)` |
| what stands *beside* it | `repo.flows.relations(node_id)` |
| what is underneath, recursively | `repo.flows.browse_tree(id, depth=2)` |
| how much is in there | `repo.flows.collection_stats(id)` |
| the curated landing page | `repo.flows.page(collection_id)` |
| the file itself | `node.content.download()` / `node.content.text()` |
| text of a page the repository does *not* hold | `TextExtraction.text_of(url)` |

### Changing things

| The task | The call |
|---|---|
| create material with vocabulary | `repo.flows.add_material(title, url=…, subject=…)` |
| change material | `repo.flows.update_material(node_id, title=…)` |
| build a collection and fill it | `repo.flows.build_collection(title, node_ids)` |
| put existing material into a collection | `repo.add_to_collection(coll_id, node_id)` |
| take it out again (material stays) | `repo.remove_from_collection(coll_id, node_id)` |
| delete | `repo.flows.delete(node_id)` |
| upload a file | `node.content.upload(data, filename=…, mimetype=…)` |
| attach an answer sheet | `node.children.add(data, filename=…, mimetype=…)` |
| link two materials | `repo.relations.create(a, "isPartOf", b)` |
| make it publicly readable | `node.permissions.publish()` |
| keywords | `node.add_keywords([...])` / `node.remove_keywords([...])` |

### Editorial surfaces (no flow — API level only)

| The task | The call |
|---|---|
| comment | `node.comments.add(text)` / `.list()` / `.edit()` / `.delete()` |
| rate | `node.rate(4)` / `node.unrate()` |
| **propose** a value instead of writing it | `node.suggestions.propose(prop, value, reason)` |
| accept or reject a proposal | `node.suggestions.decide(ids, accept=True)` |
| hand on for review | `node.workflow.submit("GROUP_redaktion", "TO_BE_CHECKED")` |
| grant or revoke rights | `node.permissions.grant(who, "Read")` / `.revoke(...)` |
| groups and members | `repo.people.*` |

### The neighbouring services

| The task | The call |
|---|---|
| ask a model | `BildungsAPI.chat(prompt)` |
| which models are there | `.models()` |
| embeddings | `.embeddings(texts)` |
| moderation | `.moderate(texts)` |
| image generation | `.images(prompt)` |
| any other forwarded OpenAI route | `.call("responses", body)` |
| text behind a URL | `TextExtraction.text_of(url, method="simple")` |
| what belongs in a content type's JSON | `MetadataAgent.content_types()` / `.schema(file)` |

### Building blocks for AI use

| The task | The call |
|---|---|
| one shape for success and failure | `as_result(awaitable, format=format_results)` |
| a hit as compact text | `format_hit(hit)` / `format_results(result)` |
| mark foreign text as data | `as_untrusted(text, label="description")` |
| clean control characters out | `sanitize_text(text)` / `one_line(text)` |
| refuse an internal address | `check_url(url)` / `is_safe_url(url)` |
| plan a change, let a person confirm | `plan_update(node, title=…)` → `.describe()` → `.apply()` |

---

## 4. The traps — what to watch for

Each of these was measured against a real instance. They are the reason the
library exists.

### 4.1 HTTP 200 does not mean it was stored

edu-sharing accepts writes it then discards. Every write in this library reads
back and raises `SilentDropError` instead of reporting success.

```python
try:
    await node.update(title="Neu")
except SilentDropError as exc:
    exc.dropped        # {"cclom:title": ["Neu"]}
```

**If you write through `repo.raw`, you lose this.** Read back yourself.

Known droppers: `relations.create(metadata=...)` (accepted, stored nowhere),
and metadata-set fields the instance does not know.

### 4.2 `unresolved` is not decoration

A filter value the instance does not know is **not applied**, and the search
answers a wider question than you asked.

```python
answer = await repo.flows.search("Zellen", subject="Bio")
answer["unresolved"]   # [{"field": "subject", "value": "Bio",
                       #   "suggestions": ["Biologie"]}]
```

Same for writing: `add_material` and `update_material` return `unresolved` for
values that were **not** written. The material exists without them.

**Never report a result to a user or a model without checking this.**

### 4.3 `total_is_lower_bound`, `truncated`, `complete`

- `total_is_lower_bound=True` → `total` counts *at least* that many. Reporting
  it as an exact figure states a number that is not one.
- `browse_tree`/`search_in_collection`: `truncated=True` → the walk stopped
  early. An empty result then does **not** mean "there is none".
- `collection_stats`: `complete=False` → the breakdown is a sample.

`find_collections` always sets `total_is_lower_bound`: it merges two routes.

### 4.4 A collection is not a folder, and a search cannot be scoped to it

- Create collections through `repo.create_collection`, never as a `ccm:map`
  node. A node created the other way is not a collection to the rest of the
  system.
- Collections form a **graph**, not a tree — a collection can have several
  parents. `browse_tree` guards against cycles and says so via `truncated`.
- There is no search scoped to a collection. `virtual:primaryparent_nodeid`
  returns HTTP 400, and it would be the wrong answer anyway: a curated
  collection holds *references* to nodes whose primary parent lives elsewhere.
  `search_in_collection` walks and filters locally.
- `collection_contents` asks **two** routes. Material alone reports a
  collection of sub-collections as empty.

### 4.5 Three different kinds of belonging

| | Holds | Read with |
|---|---|---|
| Collection | references to material that also lives elsewhere | `collection_contents` |
| Child object | a document *under* one material, no life of its own | `child_objects` |
| Relation | two materials standing *side by side* | `relations` |

A child object carries its filename in `name` and an **empty** `title`. Every
other flow displays `title`, so reaching for it here shows nothing.

Relations keep the opposite direction automatically: create `isPartOf` from the
episode and the series reports `hasPart`. A fresh relation is
`approved=False` — `relations.approve(...)` sets it.

### 4.6 Labels versus URIs

`node.get("ccm:taxonid")` gives the URI. `node.labels("ccm:taxonid")` gives
"Mathematik". `SearchHit.labels` does the same. The flow level resolves labels
for you in `fields`.

Facet *values* are URIs and carry no label — `FacetValue` has `value` and
`count` only.

Which short names (`subject`, `level`, …) exist is **read from the instance**,
not fixed in the library: `repo.searcher.field_aliases`.

### 4.7 Paging, limits and defaults that truncate

- `repo.people.members(group)` defaults to 10 and truncates silently. Pass
  `limit`.
- `collection_contents` needs `propertyFilter=-all-` to get properties at all;
  the library sets it. Through `repo.raw` you must set it yourself.
- The extraction service's two methods are **not** ranked: measured, `simple`
  returned an article where `browser` returned a cookie banner. If one yields
  nothing, try the other.

### 4.8 A framing word ruins a query

Measured over a 60-node pool: `"Bruchrechnung"` matched 0 nodes and
`"die Bruchrechnung"` matched 43. `rerank=True` expands and re-scores the
query; it costs several requests, so use it when the query comes from a human
or a model, not for a machine-built filter query.

`rerank=True` and `offset` do not combine — the pool is merged across variants,
so an offset into it would not mean what a caller expects.

### 4.9 Dead index entries

Measured: 4 of 25 search hits were no longer retrievable. `describe_many`
reports them in `failed` instead of raising, so a shorter list than requested
is distinguishable from "these do not exist".

---

## 5. Putting it behind a model

### Never let repository text act as an instruction

Descriptions, titles and comments are written by strangers. Wrap them before
they enter a model context:

```python
from edusharing.agent import as_untrusted, sanitize_text

as_untrusted(hit.description, label="description")
```

### Propose, do not write

For anything a model decided, the route is `suggestions.propose(...)` and a
person decides — not `node.update(...)`. When a write really is intended, plan
it and show the plan:

```python
plan = await plan_update(node, title=proposed)
print(plan.describe())        # old -> new, for a human
await plan.apply()            # only after confirmation
```

### One shape for success and failure

```python
outcome = await as_result(repo.flows.search(text))
outcome.ok, outcome.error_type      # False, "NotFoundError"
```

`error_type` lets a tool distinguish "rephrasing might help" from "credentials
are missing" without parsing the message. Errors carry no Java stack trace.

### Addresses from a model are untrusted

`check_url` refuses loopback, link-local and private ranges. `BildungsAPI.call`
validates its route segment by segment — `"../../administration/account"` is
refused rather than sent with the API key.

### What never reaches a log

Headers, credentials, query strings, and the path of any address the caller
supplied. The library logs only what it built itself.

---

## 6. Where to look things up

| Question | File |
|---|---|
| what does this call return, exactly | [`docs/REFERENCE.md`](../../../docs/REFERENCE.md) · [de](../../../docs/REFERENCE.de.md) |
| why does this flow do what it does | [`docs/FLOWS.md`](../../../docs/FLOWS.md) · [de](../../../docs/FLOWS.de.md) |
| how is the library built | [`docs/ARCHITECTURE.md`](../../../docs/ARCHITECTURE.md) · [de](../../../docs/ARCHITECTURE.de.md) |
| a runnable example | `docs/examples/01…17` — see the README table |
| what changed | `CHANGELOG.md` |

Start with `docs/examples/10_two_levels.py` when deciding which level to write
against: it writes the same use case twice and counts the requests each sends.

---

## 7. Checklist before shipping a tool built on this

```
[ ] Instance comes from configuration, not from a literal in the code
[ ] Credentials from env or a vault, never in source, never logged
[ ] Every search result: `unresolved` checked and surfaced
[ ] Every count reported: `total_is_lower_bound` respected
[ ] Every walk: `truncated` / `complete` surfaced
[ ] Every write: SilentDropError handled, not swallowed
[ ] Repository text wrapped with `as_untrusted` before a model sees it
[ ] URLs from a model passed through `check_url`
[ ] Model-decided changes go through `suggestions.propose`, not `update`
[ ] Errors caught as `EduSharingError`, reported with `error_type`
```

---

## 8. Related skills

| Skill | For |
|---|---|
| `wlo-edu-sharing-api` | the raw REST API, WLO's data model, licence keys, NGSearch |
| `wlo-environments` | which address is staging, which is production; variable names |
| `wlo-metadata-agent-api` | the metadata agent's own endpoints |
| `wlo-bapi-llm` / `wlo-b-api-llm` | the gateway's model list and provider behaviour |
| `wlo-suggestions-curation` | the editorial workflow this library's `suggestions` feeds |
| `wlo-mcp-search` / `wlo-mcp-python-client` | building an MCP server over this |

When those skills and this one disagree about a *Python* call, this one and
`docs/REFERENCE.md` win. When they disagree about an *address*, a *raw
endpoint* or WLO's data model, they win.
