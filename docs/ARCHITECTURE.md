# edu-sharing Python client — architecture & plan

Last updated: 2026-08-27 · Status: **all four stages complete**

A Python library that makes the REST API of an edu-sharing repository and the
surrounding services (b-api) accessible with little code — **without**
presupposing the metadata conventions of any particular instance.

---

## 1. Why at all

| What exists today | Why it is not enough |
|---|---|
| `oeh-search-etl/edu_sharing_openapi/` — generated client (openapi-generator 7.8.0) | vendored, not on PyPI, synchronous, 300+ models, and knows **none** of the measured pitfalls. Writing with it yields `200 OK` and nothing stored. |
| `wlo-mcp-sc` — MCP server (TypeScript, ~30,000 lines) | The de-facto reference implementation of the domain logic — but TypeScript, and its vocabularies are **hard-coded** for WLO (`vocabs.ts`). |
| Plain `requests`/`httpx` | Every application re-implements the 17 quirks — or walks into them. |

**No edu-sharing client exists on PyPI.** The namespace was free.

The value of this library is not the HTTP access — that is trivial. It is the
**measured behaviour**: which write route applies to which property, that a
`200` is no proof of persistence, that there are two collection searches and
neither is a superset of the other.

## 2. The central tension — and how it is resolved

Two requirements pull against each other:

* **generic** — other edu-sharing instances have different metadata sets,
  different properties, different vocabularies. Nothing may be hard-coded.
* **little code** — `repo.search("Photosynthese", subject="Biologie")` rather
  than loading the MDS, resolving URIs and assembling criteria first.

**Resolution:** vocabulary resolution happens **at runtime against the metadata
set of the instance at hand**, not against a built-in table.

```python
repo.vocab.resolve("ccm:taxonid", "Biologie")
# → POST /mds/v1/metadatasets/-home-/{mds}/values   {"pattern": ""}
# → "http://w3id.org/openeduhub/vocabs/discipline/080"
```

`subject="Biologie"` therefore works on **any** instance that carries a subject
vocabulary — without the library knowing WLO. A WLO profile stays a convenience
layer, not a prerequisite.

> Measured (staging, 2026-08-12): `pattern: ""` lists all values — the
> documented `"-all-"` returns **empty**. `pattern: "Ph"` is a working
> substring search, so the endpoint doubles as a typeahead. The header
> `locale: en_EN` yields English labels.

## 3. Layers

```
┌─ 4  Integrations ───── MCP server · tool schemas · framework adapters
│                        NOT part of v1 — but v1 must carry them
├─ 3  Agent blocks ───── formatting · budget · confirm · sanitize · safety
├─ 2  Resources ──────── repo.search() · node.update() · collection.add()
├─ 1  Profile & MDS ──── vocabulary resolution · property capabilities
├─ 0  Transport ──────── httpx · auth · retry · concurrency · read-back · errors
└─ _generated ────────── 389 operations · 378 models, from openapi.json
```

Layer 1 also answers the question third parties cannot: **which write route
applies.** Property in the MDS → `PUT /metadata`. Not in it → `POST /property`.
The library decides that itself.

## 4. Decisions taken

| # | Decision | Rationale |
|---|---|---|
| E1 | **Full endpoint coverage** through a generated layer | 318 paths / 389 operations / 378 schemas; all with an `operationId` → deterministically generatable. No blind spot. |
| E2 | Generator: **`openapi-python-client`** (Python), not the Java `openapi-generator` | Produces **httpx**-based clients with async. The Java generator emits sync/urllib3 — incompatible with E3. Java is not installed on the target machine anyway. **Verified live, see §4.1.** |
| E3 | **Async-first, sync wrapper** | `AsyncRepository` is the truth, `Repository` a thin wrapper (models: httpx, openai). AI applications and batch curation need concurrency; notebooks still get the simple route. |
| E4 | **Profile-agnostic from the start** | WLO is one shipped profile among others. Stage 2 was to be verified against a second, foreign repository — otherwise WLO assumptions calcify (that is how `vocabs.ts` came about in the MCP). |
| E5 | **No MCP server in v1** — but every building block for one | See §6. The MCP is built *with* the library later, not *into* it. |
| E6 | Import `edusharing`, distribution `edu-sharing-python-client` | The bare name `edu-sharing` would have looked like an official client of metaVentis GmbH, from whom edu-sharing originates. |
| E7 | **Field aliases in English, values in German** | The rest of the API is English (`Repository`, `search`, `update`). The values are the repository's own labels and stay as they are. |
| E8 | **Identifiers are percent-encoded in exactly one place** (`urls.path_segment`) | Interpolating an id into a path with an f-string lets it escape the path: measured on 2026-08-27, a node id of `../../../admin/v1/applications` reached a different endpoint, and `abc?admin=1` swallowed the trailing `/metadata`. Encoding at each of the 16 call sites would mean 16 chances to forget; one helper plus an integration test that walks every call site makes a forgotten site fail loudly. Relevant because under an MCP the id comes from the model, i.e. from foreign data. See audit F1. |
| E9 | **Two levels: API-close objects and JSON flows** | The API level returns `SearchResult` and `Node` -- right for writing Python, wrong for anything that passes the result onwards. `repo.flows.*` chains the same calls and ends at `dict`. Flows add no capability; they remove steps. Kept separate rather than merged, because an object with methods and a JSON-serialisable structure are genuinely different things and picking one would have made the other awkward. Output keys are the configured aliases, so the shape is not tied to a profile (see E4). |
| E10 | **Reranking is opt-in, and its word lists are a parameter** | edu-sharing ANDs every query word, so a naturally phrased question finds nothing -- measured 2026-08-27: "Bruchrechnung" 1591 records, "Ich suche ein Arbeitsblatt zur Bruchrechnung" **0**. That is how a language model phrases things, so the fix matters for this library's main audience. Ported from `wlo-mcp-sc` (Apache-2.0) with two changes: the German word lists became a `LanguageProfile` parameter, and the metadata-quality signals read the configured aliases instead of fixed WLO properties -- a hard-wired German list would contradict E4. Opt-in because it costs one request per variant. The reciprocal rank fusion of the original was **removed**: it weighed a record's position in the repository's answer, and that order is measurably unstable (25 hits of which 15 differ between identical queries), which made the ranking depend on arrival order -- of 30 shuffles of one candidate set, only 14 gave the same result. What is left is order-independent: quality (0.8) plus which variants returned a record at all (0.2). Same candidates in, same ranking out; two runs still differ when the index does. |

### 4.1 Feasibility proof (carried out 2026-08-27 against staging)

E1 and E2 are **not assumed but measured** — with a finding that would otherwise
have wrecked the pipeline:

1. **The generator emits invalid Python from the unmodified spec.**
   244 path parameters carry a `schema.default` (`-home-`, `-default-`,
   `-userhome-`); when a parameter without a default follows, you get

   ```python
   def _get_kwargs(
       repository: str = '-home-',      # default from the spec
       metadataset: str = '-default-',  # default from the spec
       query: str,                      # ← SyntaxError
   ```

   **145 of 1131 files were broken** (12.8 %) — all under `api/`, the 701 models
   stayed clean. The generator reports this only as a warning and exits with
   **code 0**. Anyone not checking takes it for a successful run.

2. **A deterministic spec preprocessing fixes it completely.** After removing
   the 244 defaults: **1131 files, 0 syntax errors.** The default is not lost —
   it is a convenience of the web UI, and the convenience layer sets `-home-`
   itself anyway.

3. **All 389 operations have an `asyncio` variant.** Consistent with E3.

4. **Live call successful:** `GET /_about` through the generated async client →
   `200`, **edu-sharing 11.0**, 32 services.

Both the check and the repair live in `scripts/generate_client.py`. The script
exits with code 1 if even one file fails to parse; the syntax check is part of
generating, not optional.

> The only remaining warning: one `500` response is declared in the spec as
> `application/text` (not a valid MIME type) and is skipped. It affects the
> error case of a single endpoint.

### What E1 costs, and how it is contained

Full coverage means being tied to one edu-sharing version. Countermeasures:

1. Generation runs against a **reference spec** kept and versioned in the repo.
2. `scripts/generate_client.py` regenerates against **any** instance
   (`GET <repo>/rest/openapi.json`) — anyone on a different version builds their
   own layer.
3. The hand-written layers 0–3 depend **only** on the ~30 operations actually
   used. If the generated layer breaks, the library does not.
4. `repo.raw.get/post(...)` stays open as an escape hatch.

## 5. How it should feel

```python
from edusharing import Repository

repo = Repository.from_env()          # EDU_SHARING_URL / _USER / _PASSWORD
repo = Repository("https://repository.staging.openeduhub.net")   # anonymous, read-only

# --- Reading: labels, not URIs. Resolved against THIS instance's MDS.
for hit in repo.search("Photosynthese", subject="Biologie", level="Sekundarstufe I"):
    print(hit.title, hit.url)

# --- Writing: merged, read back, raises on a silent drop
node = repo.node("abc-123")
node = node.update(title="New title", description="…")
node = node.add_keywords("Weimar (Ort)")     # merge, not overwrite

# --- Collections: both search legs, because neither is a superset
repo.find_collections("Optik")
repo.add_to_collection(collection_id, node.id)

# --- Escape hatch: any of the 389 operations
repo.raw.json("GET", "/config/v1/values")
```

The failure case that justifies the library:

```
SilentDropError: Not stored: ccm:oeh_collection_compendium_text
  (HTTP 200, absent or different after reading back). …
  node.set_property(...) bypasses the metadata set's filtering.
```

## 6. What a complex MCP will need — and why it is in v1

The MCP server is not part of v1. The blocks without which it could not later be
built are. Derived from `wlo-mcp-sc`:

| Block | Why an MCP needs it | Status |
|---|---|---|
| **Per-request credentials** | One server serves many users — global auth state is a leak. | ✅ `auth`, `transport` |
| **Preview-then-confirm** | The agent must be able to show *what* it would change before doing it. | ✅ `agent/confirm` |
| **LLM formatting + budget** | Node → compact text, capped, keeping url and nodeId (which a model otherwise paraphrases away). | ✅ `agent/format` |
| **Prompt-injection defusing** | Foreign repository content lands in the model context. | ✅ `agent/sanitize` |
| **SSRF / private-host guard** | URLs from foreign content get fetched. | ✅ `agent/safety` |
| **Structured results, not exceptions** | A tool returns errors as *text*; an exception ends the turn. | ✅ `agent/result` |
| **Concurrency + rate limiting** | Fan-out across many nodes without overwhelming the repository. | ✅ `transport`, `bapi/client` |
| **Resolution feedback** | "subject 'Bio' unresolvable — did you mean Biologie?" instead of silent emptiness. | ✅ `search`, `results` |
| **Dedupe** | Merge the two collection legs on the node id. | ✅ `collections` |
| **Cache with TTL** | Vocabulary and model lists are costly and change rarely. | ✅ `vocab`, `bapi/client` |

That is layer 3 (`edusharing.agent`). It is **framework-neutral** — no MCP, no
LangChain import. The MCP server is then a thin adapter project.

Deliberately **not** built: a reranker. Without a concrete use case it would be
guesswork, and the two collection legs are already merged on the node id.

## 7. Measured foundations the design rests on

Not assumed but checked (staging, 2026-08-27, unless noted otherwise):

**edu-sharing**

* The reference instance reports **edu-sharing 11.0** (`GET /_about`), 32 services.
* `GET /rest/openapi.json` → 1.34 MB, OpenAPI 3.0.1, 318 paths / 389 operations /
  378 schemas, 36 families, **all with an `operationId`**. `swagger.json` does
  not exist. Largest families: ADMIN v1 (61), NODE v1 (53), IAM v1 (47),
  Assignment v1 (18), COLLECTION v1 (16), SEARCH v1 (13), MDS v1 (5).
* `securitySchemes` = `basicAuth` + `cookieAuth`. **No bearer.** A bearer header
  is *ignored, not rejected* — the request looks authenticated and is not. The
  most dangerous mistake a client can make.
* Wrong credentials give **401 everywhere** — no fallback to "public only". A
  typo in the password paralyses every call instead of degrading access.
* The MDS is **17.2 MB** — never in the request path. Vocabulary comes from
  `POST /mds/v1/metadatasets/-home-/{mds}/values`.
* `GET /search/v1/metadata?nodeIds=a&nodeIds=b` **is not a batch** — two ids
  yield exactly one result. Using it as one silently loses nodes.

**b-api** *(Spring Boot, not FastAPI — the 404 trace gives it away)*

* Exactly two providers: `academiccloud`, `openai`. Others → `400 Provider … not found`.
* `/embeddings`, `/completions` → **403** from Spring Security. Not enabled.
* Without a key → 401. Auth is `X-API-KEY`, **not** bearer.
* `openapi.json`, `/docs`, `/health` serve HTML (SPA fallback) — any endpoint
  discovery is guesswork. Documented as a known limit.
* → "driving the b-api" means **policy**, not breadth: model choice by
  `demand`/`status`, per-family request quirks (`max_completion_tokens` for
  GPT-5/o, `enable_thinking:false` for Qwen3 — but **not** for Mistral, which
  answers 400), retry on 429/502/503/504, semaphore, `content or reasoning` when
  reading.

**The search index holds nodes that no longer exist.** Measured on 2026-08-27 against staging: of 25 hits for "Physik", **4 were not retrievable** -- `NotFoundError` from `/node/v1/nodes/-home-/{id}/metadata`, although the hit carried a title and full metadata in the search response. Anything chaining search to a detail lookup -- which is exactly what an MCP does -- has to survive that. Recorded because it looks like a library bug and is not.

## 8. Stages

| # | Content | Done when |
|---|---|---|
| **0** | ~~Generator pipeline~~ | ✅ **done** — `scripts/generate_client.py`, verified (§4.1) |
| **1** | ~~Transport, auth (incl. the bearer trap), error types, `_about` health, identity probe~~ | ✅ **done** — 93 tests offline, 5 live against 11.0 (§8.1) |
| **2** | ~~Vocabulary cache, label↔URI, search with facets, both collection legs~~ | ✅ **done** — 160 offline, 21 live (§8.2) |
| **3** | ~~Nodes, properties (both routes), read-back verify, keyword merge, collections, files~~ | ✅ **done** — 206 offline, 19 live reading, 18 live **writing** (§8.3) |
| **4** | ~~`edusharing.agent` (§6) + b-api client with policy~~ | ✅ **done** — 342 offline, 25 live (§8.4) |

Documentation runs alongside, not afterwards: **every example under
`docs/examples/` is an executable test against staging.** What does not run there
does not go into the README.

### 8.1 Stage 1 — what came out of it

| Module | Responsibility |
|---|---|
| `errors.py` | Error types; mapping from status **and** Java class name |
| `urls.py` | Normalise repository URL, reject deep links |
| `auth.py` | Credentials as values; bearer rejected; passwords never in `repr` |
| `transport.py` | httpx, timeout, retry, concurrency, credential boundary |
| `_sync.py` | Event loop in a background thread for the synchronous surface |
| `repository.py` | `AsyncRepository` / `Repository`, `about()`, `whoami()`, `raw` |

Three decisions made while building, each justified in the code:

1. **Retries follow the error *type*, not the status code.** Otherwise a "Not
   allowed for guest user" would be retried three times — the same request that
   can never succeed, against a repository that did nothing wrong.
2. **The synchronous surface runs its own loop in its own thread** rather than
   `asyncio.run()`. Otherwise it fails inside Jupyter — precisely the audience
   it exists for.
3. **Credentials go only to the configured repository URL**, checked with prefix
   *and* boundary. A plain `startswith` would let
   `https://repo.example.test.attacker.test` through.

The three critical behaviours are covered by mutation tests: disable the
semaphore, switch retries to the status code, replace the boundary check with a
plain `startswith` — each mutation turns exactly its own test red.

### 8.2 Stage 2 — what came out of it

| Module | Responsibility |
|---|---|
| `vocab.py` | Label↔URI against `/values`, cached with a per-property lock |
| `search.py` | ngsearch with filters, facets, field aliases |
| `results.py` | Value objects, shared by material and collection search |
| `collections.py` | Both collection searches, concurrent, merged |

**On genericity (E4).** A second *instance* could not be brought in:
`stable.demo.edu-sharing.net` (edu-sharing 9.0) permits **nothing** anonymously
— even `/iam/…/-me-` answers 401. That is captured as a live test (the library
must turn it into an `AuthenticationError`, not crash).

Verification instead ran against **two metadata sets of the same instance**:
`-default-` (Contentbuffet, 88 widgets, 22 vocabularies) and `mds_oeh`
(236 widgets, 107 vocabularies). They return different result sets for the same
query (2825 vs 17994 for "Physik"), and the same library code works with both.
That is weaker than a foreign instance, but it is a real separation: had the
library carried WLO assumptions, `-default-` would fail.

Five findings that shaped the design — all measured, three of them correcting
previously assumed knowledge:

1. **Carrying a vocabulary and being filterable are different things.**
   `ccm:taxonid` has a vocabulary in both metadata sets but is filterable only in
   `mds_oeh`; `ccm:educationaltypicalagerangecluster` in neither. A live test
   tripped over exactly this. The library now adds the missing hint to the
   server message.
2. **The OpenAPI spec describes the vocabulary response incorrectly.** It
   declares `MdsValue {id, caption}`; what arrives is `{key, displayString}`.
   Anyone trusting the generated layer reads empty fields — the justification for
   the hand-written layer, in one sentence.
3. **`pattern` is a substring search, not a prefix search.** `"ysik"` finds
   Physik, Atomphysik, Kernphysik. The original prefix assumption was refuted by
   a live test.
4. **The two collection searches genuinely diverge** — for "Deutsch" the overlap
   was **zero** (25 against 25 different collections), for "Physik" each
   contributes five of its own. Both are needed. (Note: the *degree* of overlap
   fluctuates between calls, since each leg returns 25 of 876 — see §8.5.)
5. **Query names are not introspectable.** `ngsearch` appears in no API
   response; the `lists` in the MDS all carry `queries: []`. The name is a
   convention and therefore a parameter, not a discovered value.

### 8.3 Stage 3 — what came out of it

| Module | Responsibility |
|---|---|
| `nodes.py` | Read/create/change/delete nodes, read-back check, keyword merge |
| `content.py` | Upload/download files, full text |
| `info.py` | Value objects for instance information (split out of `repository.py`) |
| `collections.py` | additionally: create collection, set/remove references |
| `_sync.py` | additionally: `SyncTransport`, `SyncNode`, `SyncNodeContent` |

**The central measurement**, taken on a throwaway node:

| Operation | HTTP | stored |
|---|---|---|
| `PUT /metadata`, property in the MDS | 200 | yes |
| `PUT /metadata`, property **not** in the MDS | **200** | **no** |
| `POST /property`, same property | 200 | yes |
| `PUT /metadata`, invented field | **200** | **no** |

Twice a success code for something that did not happen. The live test proves
both sides: with the read-back check the operation fails, with `verify=False`
the same call reports success and the value is gone.

Four further findings, three of which refuted assumptions:

1. **`downloadUrl` does not prove content exists.** It is always set, and a node
   without a file answers 200 with zero bytes — without complaint. Reliable is
   `content.hash`: `None` without content, set for a 0-byte file. `cclom:size`
   is `None` in both cases and is therefore no good.
2. **A `ccm:map` from the node API is not a collection.** It lacks the
   `collection` aspect; every reference attempt ends in `400 … is not a
   collection`. Collections need the collection endpoint — and there
   `-collectionhome-` is **not** resolved (404), unlike at the node API. The
   collection root is called `-root-` there.
3. **After `addReference` the reference is not immediately visible.**
   `/children/references` returns an empty list although the reference exists —
   the second attempt answers 409. A read-back would therefore be wrong and
   raise a false alarm; `add()` skips it and reports through its return value
   whether something was newly created.
4. **Deleting a property works with a `null` body *and* with no body at all.**
   The explicit `null` is sent — the documented route; an omission is something
   another version may read differently.

**Two gaps of my own**, both noticed while using the library and closed: the
synchronous `Repository` had no `raw`, and `SyncNode.content` returned an object
with asynchronous methods whose calls went nowhere. Every new asynchronous
surface needs its synchronous pass-through — that is the maintenance cost of
decision E3 and belongs on the checklist for every extension.

**Write tests** run only with `-m write`, exclusively inside a folder created
for the purpose in the test account's home, and clear it away afterwards. The
holdings were compared against their initial state after every run.

### 8.4 Stage 4 — what came out of it

| Module | Responsibility |
|---|---|
| `agent/safety.py` | May this URL be fetched? (SSRF) |
| `agent/sanitize.py` | Foreign content for a model context |
| `agent/format.py` | Hits, compact, budgeted, without losing the citation |
| `agent/result.py` | Errors as results rather than exceptions |
| `agent/confirm.py` | Show what would happen, then do it |
| `bapi/policy.py` | Model choice and request shape — pure functions |
| `bapi/client.py` | HTTP to the b-api, retry, concurrency, TTL cache |

Three decisions that need explaining:

1. **`sanitize` detects no attack phrasings.** A pattern list against "ignore all
   previous instructions" can be reworded — and a teaching text *about* prompt
   injection is a legitimate resource it would mangle. What remains is false
   confidence. Instead: strip invisible control characters (zero-width, bidi,
   Unicode tag block) and mark the content so it cannot break out.
2. **`safety` does not resolve names.** `internal-service.example.com` may point
   at `10.0.0.5` and still pass. Resolving here would be security theatre anyway
   because of DNS rebinding; anyone who must rule it out needs an outbound proxy.
   The limit is stated in the docstring rather than in a security promise.
3. **`format` budgets in characters, not tokens.** A token estimate without the
   target model's tokenizer would be a guess. And: if not even the header fits
   the budget, the citation wins and the budget is exceeded — a hit without `id`
   and `url` is worthless.

**Two findings from the live tests:**

* **`status: ready` does not mean a model answers.**
  `apertus-70b-instruct-2509` reports `ready` and `demand: 0` and answers
  `503 Model pricing unavailable — cannot enforce cost quota`. That appears in no
  model list. Under **automatic** selection the client therefore falls through to
  the next model (`last_model` says which it became); with an **explicit** model
  id it does not — that would be a silent substitution.
* **Noise in the model context:** some records carry the string `null` as a
  `_DISPLAYNAME`, and the server returns "did you mean …?" even alongside 57
  hits. Both are filtered now; which vocabulary fields belong in the context at
  all is decided by the caller through `label_properties`.

**A mutation test failed to bite at first.** The original test for "`id` and
`url` survive the budget" stayed green although the guarantee had been disabled —
the budget was chosen too generously. It has been sharpened; the mutation now
turns it red. A mutation test that catches nothing is the more dangerous case: it
certifies safety that is not there.

**On the noted split of `repository.py`:** not carried out. The file has one
responsibility — the entry point, in two flavours — and stage 4 barely touched it
because `agent` and `bapi` are sub-packages of their own. Cutting at the line
limit without a second responsibility having appeared would only have increased
the file count.

### 8.5 Language changeover and a test-design correction

After stage 4 the code, documentation and field names were switched to English
(decision E7); values stay German, since they are the repository's own labels.
Error messages went with them: they reach end users and model contexts, and
German messages beneath English docstrings would be the same split the field
aliases had just left behind.

In the course of that, a **test-design error of mine** surfaced. The live test
for the collection search demanded more hits than a single leg returns, because
the overlap for "Deutsch" had been measured as zero. That is not stable: each
leg returns 25 of 876 collections, and how strongly those two selections overlap
fluctuates from call to call — 25 and 29 hits were both observed for the same
query. The test now checks what the library guarantees (both legs queried, result
deduplicated on the node id, total marked as a lower bound). The measurement of
the overlap remains in the documentation, where it belongs.

## 9. Open points

1. **Second test instance** — still open. `stable.demo.edu-sharing.net`
   (edu-sharing 9.0) is reachable but permits **nothing** anonymously beyond
   `/_about` and `/config/v1/values`; without credentials it is no good for
   verification. Production is deliberately deferred until the library runs
   stably. Until then, genericity is evidenced only against two metadata sets of
   one instance (§8.2).
2. **Test docstrings are still German.** They are the measurement record of this
   project, are not shipped, and have no external audience; translating them
   would be an opportunity to blur a measured finding. A deliberate exception to
   E7.
3. **`nodes.py` (409 lines)** remains above the size threshold.
