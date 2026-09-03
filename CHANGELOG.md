# Changelog

All notable changes to this project are recorded here, following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow
[Semantic Versioning](https://semver.org/).

Not on PyPI. `0.0.1` is the first tagged version: everything below was built
before it, and the number exists so that what comes next has something to be
compared against. The leading zeros are honest — the surface may still move.

Every entry that names a number was measured. Where a change came from a
measurement against a live instance, the date and the instance are in the code
and in [`docs/audits/`](docs/audits/).

## [Unreleased]

### Fixed

- **The transport no longer re-sends a write that may already have been
  carried out** (audit COR-1). After a timeout past the sending, or a 5xx,
  only reads and the writes that merely set a state — `update`,
  `set_property`, permissions, ratings, `collections.update`, the search and
  vocabulary queries — are retried; `request(idempotent=)` is the switch. A
  create or delete raises `TransportError` naming the doubt. A connection
  failure from before the sending is retried for every method, a `401` once,
  as before.
- **`add_material` names the limit of its duplicate check.** The address
  lookup goes through the search index, which trails the node store by a few
  seconds (measured on staging, 2026-09-02: findable after 5.3 s). The write
  proof that assumed an instant index now waits for it; the flow, the
  documentation and the skill say so.
- **`set_property(prop, None)` reads back that the property is gone.** Until
  now the read-back after a deletion was made and not looked at; an instance
  answering 200 and keeping the value passed as deleted. `SilentDropError`
  now, like every other lost write.
- **A renamed node is not a lost write.** `Nodes.create` compared `cm:name`
  too, so a collision that `rename_if_exists` resolved with a counter raised
  `SilentDropError` with a wrong diagnosis -- every re-run of `add_material`
  with the same title in the same folder failed. `node.name` carries the
  stored name.
- **A redirected write is disclosed even with `verify=False`.** The original
  is read (the check alone is skipped) and comes back stamped with
  `redirected_from`; an error raised at the original carries a note naming
  the reference the caller actually used.
- **`accept_suggestion` no longer wipes the keyword list.** A proposal for
  `cclom:general_keyword` was written with `set_property`, which replaces
  the whole list -- every other keyword went, silently. Keywords are now
  added; for other properties the displaced values come back as
  `replaced`. A failure while marking the proposal no longer loses the
  answer: `failed` carries a `mark` part and the value stays written.
- **An address the search cannot take is a check that did not run.**
  `find_by_url` never looked at `unresolved`; a scheme-less address was not
  sent, twenty unfiltered hits were compared, and "no duplicate" came back
  with empty `warnings`. It now raises `ValidationError`, which
  `add_material` turns into the documented warning or refusal. A
  misspelled `if_exists` is refused even when no `url` is given.
- **`update_material` discloses a redirection.** Its answer carried the
  original's `id` for a reference passed in and said nothing about it;
  `redirected_from` now names the id the caller used, like `describe`,
  `placement` and `delete` already did.
- **`placement` reports repository failures only.** A bug in the two halves
  was caught as a partial answer and hidden in `failed`; it raises now. The
  node read failing while both halves answer is pinned as the partial
  answer it was meant to be.
- **`text` reads JSON and XML uploads, and a repository failure is a
  reason.** `/textContent` is empty for `application/json` (measured), yet
  only `text/*` fell back to the file; and a 5xx while fetching the extract
  raised out of a flow whose contract is "no text is an answer" -- it is
  now `reason="repository_failed"` with `detail`.
- **Skills: the walk survives a refused sub-collection, and the block kind
  is a parameter.** One 403 among the sub-collections of a skills tree
  raised out of the whole search (the A10 precedent again); it is now
  counted in `SkillSearch.unreadable` and skipped, the root refusing stays
  an error. Sub-collections beyond one page set `truncated`. The kind that
  names a skill (`ki-skill`) was hard-wired in two places; it is
  `SkillConventions.skill_kind`. A registry naming one skill under two
  contexts reads its record once; transport and server errors raise
  instead of posing as `unresolved`; a skill's folder answering 404 is
  `files_reason="no_folder"`; `pick(..., include_files=False)` reaches `get`.
- **Skill Markdown: a block shown inside a code fence is not a reference,
  and an untitled sub-section lends its prose.** `parse_blocks` read a
  `::: ki-skill` example inside a fence as a real reference (and matched
  any `:::` pair when given no kinds); the prose under an untitled `###`
  inside a named `##`, and everything below an `####`, reached no
  `instruction`. Fences now mask blocks and headings alike; untitled
  sub-sections are transparent for their prose as for their skills; only
  `#` to `###` end a stretch of prose.
- **Skills: a search inside a collection matches, not merely ranks; the
  instruction is read as text only.** `search(text, collection_id=…)`
  returned every skill of the collection sorted by score, and `pick`
  named a zero-score "best"; a record no term touches is now left out.
  the instruction and the registry are decoded with `utf-8-sig` (a
  byte-order mark hid the H1 from the section parser, which runs on the
  registry) and refuses a binary upload with
  `content_reason="not_text"` instead of returning mojibake; `no_file`
  says the other reason. One `is_text_like` in `content` serves `text` and
  the skills alike.
- **`search` no longer caps the caller's `limit` at the refill cap.**
  `limit=250` silently became 200, and a page the refill could not fill
  after exclusions came back short with empty `warnings`. The cap now
  applies to the refill only; both shortfalls are named in `warnings`;
  under `rerank` the pool grows with the refill. A stored property that is
  not a list is wrapped under `fields`, not splatted into characters.
- **A read-side filter takes every URI a label carries.** `find_collections`
  and `Skills.search` resolved `subject="Physik"` to the first URI only,
  while `search` sends both (measured: 25 subject labels live in two
  vocabularies) -- so the same short name narrowed collections and skills
  differently from material, silently. `resolve_vocabulary(...,
  every_value=True)` is the reading rule; writing keeps the first.
- **`find_collections` judges its filter on candidates, not on the cut
  page.** A short name was applied after the server had cut the merge at
  `limit`, and `total` stayed the unfiltered figure -- ten candidates judged,
  48 claimed. Now five times `limit` (at most 100) are fetched, `total`
  counts the matches, and `warnings` names candidates beyond that. Below a
  `parent_id` the walk keeps each record, so a filter there no longer makes
  every hit `unjudged`; more sub-collections than one page lists set
  `truncated`; a query of stopwords only is matched as typed instead of
  matching everything; `query.filters` echoes the caller's words as `search`
  does; one `carries` serves collections and skills.
- **`search_all` keeps the material when the page search fails, and its
  empty collection bucket has the documented keys.** `find_pages` ran
  outside the outage handling built for audit A9, so with `include_pages`
  a 503 of the collection routes raised and lost the material hits; it now
  comes back as an empty `pages` bucket with `error` when that search
  fails. The empty collection bucket lacked `unjudged` and two `query`
  keys -- a `KeyError` in production only; both buckets are built through
  one path now. Short names reach the collection bucket (applied locally);
  `filters_ignored` names raw `filters` only.
- **Blocking `find_collections` takes no text, like the async one.** The
  mirror demanded a positional `text`; a guard now compares every facade
  method's defaults between the two, and the documentation guard checks
  `repo.flows.x(...)` calls against the real signatures -- 57 of them had
  escaped it.
- **Docs corrected where they had drifted from the code.** `placement` costs
  three requests (the node is read first to resolve a reference), not two;
  `add_material` three to six, with the address check; `accept_suggestion`
  six; the `search` example carries `preview_url`, `download_url`,
  `license` and `size`; `total_is_lower_bound` is true for a search and
  below a `parent_id` only when the walk was cut short; the block
  `search_all` shows calls `collections.find_collections`; a block that
  repeated `update_material` inside `add_material` is gone; the facade
  docstring no longer claims that nothing forwards `**kwargs`.
- **`include_pages` costs nothing more, and the registry is downloaded
  from the listing.** `search_all` read the pages off a second collection
  search; it now reads them off the collection hits it already has (one
  `pages_among` behind `find_pages` and `search_all`). `skill_registry`
  read the registry record again after the listing that already carried
  it; it downloads from the listing entry and reads the record only when
  the listing lacks the download address. Deleting a reference and
  accepting a proposal at a reference are pinned offline as well.
- **Second review round, skills.** The registry document is decoded with
  the same BOM-stripping rule as the instruction (the section parser runs
  there); a block shown unclosed inside a code fence no longer swallows the
  next real block; a registry candidate without a file is `unreadable`, not
  an error; the walk does not ask the last level for sub-collections it
  would never visit, and the root's sub-collection listing refusing is an
  error like its file listing; `application/octet-stream` counts as
  unknown and is decoded; a `SkillConventions` whose `skill_kind` is not
  among `block_kinds` is refused at construction; a query of stopwords
  only is matched as typed inside a collection.
- **Second review round, search.** The short-page warning under `rerank`
  recommends a larger pool, not an offset that does nothing there; below a
  `parent_id` a short-name filter judges every walked collection before
  the cut; the empty `pages` bucket is built through `pages_among` like
  the filled one; a stored `0`/`False` survives under `fields`; the facade
  docstrings and `EXCLUSION_MAX` wording say what the code does; the
  documentation guard now reads calls inside fenced code blocks and checks
  keywords against the function behind a `**kwargs` facade; the mirror
  guard looks both ways and at positional order; `carries`,
  `walk_collections` and `pages_among` are exported and documented.
- **Second review round, write path.** `accept_suggestion` names the
  original's values under `replaced` when called at a reference (the
  reference carries a copy); `find_by_url` refuses a scheme-less address
  before paying for a vocabulary lookup and an unfiltered search;
  `validate_if_exists` is public; the `placement` docstring counts three
  requests and names the `original` part; `set_property` and `update`
  docstrings say what the read-back does with a deletion and at a
  reference; the cost table counts `add_material` per step taken and
  publishing at four; the `add_material` example carries `existing`,
  `created` and `warnings`; "text/*" reads "text, JSON or XML" everywhere.

## [0.1.0] — 2026-09-02

### Added

- **Skills** — `repo.skills` and four flows (`find_skills`, `skill`,
  `skill_registry`, `pick_skill`): records whose content type says
  "instruction" and whose file is the `SKILL.md`, and the registry document a
  collection files to approve them, parsed into a catalogue with working
  contexts. Every convention — the content-type URIs, how a registry names
  itself, the block kinds — is `SkillConventions`, a parameter with WLO's
  `WLO_SKILLS` as the default. Measured on staging: 34 skills with `mds_oeh`
  and a refusal from `-default-`; the `SKILL.md` read with `download()`
  because `/textContent` is empty for Markdown; a skill's folder 403
  anonymously, reported as `files_reason`. The Markdown parsers
  (`edusharing.skills_markdown`) are pure and follow the MCP's rules.
- **`EDU_SHARING_METADATASET`** — `from_env()` reads the metadata set, because
  it decides what can be filtered on and a deployment has to say it once.
- **Search parity with the MCP.** `search(exclude_ids=…)` leaves out hits
  already shown and refills the page; `facet_limit` raises the 20 values per
  facet; `properties=[…]` carries any further property under `fields`, as
  stored — measured, a collection listing carries the content type and
  `fields` used to hide it. `find_collections` takes `subject=`/`level=`
  (applied locally: the collection endpoint accepts a search word and nothing
  else) and `parent_id=` (walks the subtree instead of searching), and reports
  `unjudged`. `search_all(include_pages=True)` adds the `pages` bucket. Every
  hit names `preview_url`, `download_url`, `license` and `size`.
  `flows/find.py` was split: collection search lives in `flows/collections.py`.
- **`flows.accept_suggestion`** — apply a proposal, read it back, and only
  then mark it `ACCEPTED`. Measured 2026-08-28: marking alone writes nothing,
  so a proposal accepted by `decide()` was a record of something that never
  happened. When the value does not arrive, nothing is marked and `failed`
  says so.
- **`add_material(url=…)` checks for an existing record first.** A second
  record for the same address is a duplicate by definition; `if_exists`
  (`"return"` by default, `"raise"`, `"create"`) decides, and the answer
  carries `existing`, `created` and `warnings`. Measured 2026-09-02: `mds_oeh`
  accepts `ccm:wwwurl` as a criterion, `-default-` does not — then the
  default check is skipped and said so, while `"raise"` refuses to guess.
  `flows.duplicates.find_by_url` is the building block.
- **`flows.text`** — the full text of one material and why there is none:
  the repository's text first, then the file itself for a `text/*` upload
  (measured 2026-08-27: `/textContent` is empty for Markdown and JSON although
  the file has text), then the linked page through a `TextExtraction` the
  caller passes in. `source` and `reason` replace an empty string; no text is
  an answer, not an error. Example 15 did this by hand in 215 lines.
- **`Node.original_id`, `is_reference`, `aspects`, `redirected_from`; `SearchHit.original_id`.**
  A collection holds references, and a listing hands out their ids. The
  node now says which record it stands for, and a write through a reference
  returns the original with `redirected_from` set. `placement`, `describe`
  and `delete` carry `original_id`; `delete` also `is_reference`.
- **`ancestry_of` and `collections_of` accept the connection**, as every
  other free function does; `collections_of` takes `original_id=` from a
  caller that already resolved it, saving the read.
- **`Repository.resolve_all(prop, label)`** — the blocking counterpart to
  `Vocabulary.resolve_all`. A label can belong to two vocabularies; `resolve`
  returns only the first. `search` resolved ambiguous labels internally either
  way, so blocking callers already got the right hits — but to see the set
  itself they needed `AsyncRepository`.
- **The skill names the whole surface.** It routed the twenty flows and named
  120 of 285 public names; an AI with only the skill loaded could not find
  `create_node` (used by eight examples) or `is_anonymous` (nine). It now names
  every public member of every object a caller holds, the free functions, the
  error tree and the named constants with their values — 285 of 285, in both
  languages.
- **How edu-sharing stores metadata** — a new section in both skill versions.
  Every value is a list; the `cm:` / `cclom:` / `ccm:` / `virtual:` namespaces;
  `cm:name` as a key against `cclom:title` (material) and `cm:title`
  (collection) as the title; vocabulary fields as URIs; the metadata set as a
  silent discarder; shared lists; aspects against types; `propertyFilter`.
- **Trap: four accessors on the blocking `Repository` are still asynchronous.**
  `repo.vocab`, `repo.searcher`, `repo.collections` and `repo.nodes` hand back
  the asynchronous objects unchanged, so a method call on them from blocking
  code produces a coroutine that never runs — no error, no effect. Documented
  with the table of blocking counterparts.
- **The fields of every object are in both references.** They were measured
  against `__all__`, which covers classes and functions but not the fields a
  class carries: `Swimlane.heading`, `Group.signup`, `Relation.created_by`,
  `PageVariant.target_group` and 35 more were absent from a reference that
  counted as complete.
- **Four guards, all derived rather than maintained**, so the measure grows
  with the library instead of ageing in a hand-kept list:
  `test_der_skill_nennt_jeden_oeffentlichen_namen` (everything in `__all__` is
  in both skill versions), `test_der_skill_nennt_was_die_beispiele_benutzen`
  (the lower bound: what a working example uses cannot be missing),
  `test_jedes_feld_jeder_klasse_steht_in_der_referenz` (every public field and
  property), and
  `test_jeder_dokumentierte_repository_aufruf_nennt_echte_parameter`, which
  checks every `repo.x(a, b=…)` in a file that asserts names against the real
  signature — positional arguments by name *and* order, keyword arguments
  against the parameter list unless the method takes `**kwargs`. The last one
  found all fourteen wrong places below.

### Changed

- **`nodes.py` split.** The write path -- field aliases, the read-back check,
  `update`, `set_property`, the keyword merge -- moved to `nodes_write.py`;
  `Node` keeps every method as a one-line delegation, so nothing in the public
  surface changed. 697 lines became 537 plus 200. The architecture note that
  had argued against a split (§8, "no second responsibility") is revised: the
  reference redirection gave the write discipline a reason to change of its
  own.

### Fixed

- **Nine documented free-function signatures were wrong**, found by the new
  guard that checks `name(a, b=…)` rows against the real functions:
  `rating_of(repo, id)` takes a node, `resolve_vocabulary(repo, field, label)`
  takes the short names, `at_least` is a bounds check and not a way to read a
  partial result, and `cap_text`, `expand_query`, `query_terms`, `score_hit`,
  `normalize_repository_url` and `rest_base` named parameters they do not have.
- **`search_reranked` forwarded short names as keyword arguments into
  `Search.search`**, where a name matching one of its own parameters
  (`offset`, `content_type`) was taken as that parameter instead of refused.
  Short names become properties in the reranker and travel as filters.
- **`REFERENCE(.de).md` documented `add_material(parent_id, title=…)`** — the
  first positional argument is `title`; `parent_id` is a keyword. The
  signature guard checks `repo.x(…)` rows only, which is how this one slipped.
- **A listing id made the library answer "in no collection" — and write
  into the void.** Measured on staging, 2026-09-02: `/usage` answers a
  reference id with an empty list and the original with two collections;
  `node.collections()` and `flows.placement` passed the empty list on as a
  fact. And a `PUT` aimed at a reference is stored on the reference and never
  reaches the record (measured by the MCP, 2026-08-17) — a drop the read-back
  cannot see, because it re-reads the same node. Reads now ask for the
  original; `update()`, `set_property()` and `add_keywords()` write to it.
  Deleting is deliberately not redirected: on a reference it removes only the
  reference, and redirecting it would turn a harmless act into data loss.
- **`docs/REFERENCE(.de).md` documented a capability that never existed.**
  `repo.resolve(url_or_id)` promised "the node id behind a rendering URL". The
  method exists under that name but does something else — `resolve(prop, label)`
  translates a label. No URL-to-node-id resolution exists anywhere in the
  source; the line had been there since the reference was first written.
- **Twelve documented parameter names were wrong** across six files:
  `repo.node(id)` for `node_id`, `repo.update_collection(id, …)` and
  `repo.add_to_collection(coll_id, …)` for `collection_id`. Written as keyword
  arguments they raise `TypeError`.

## [0.0.1] — 2026-08-31

First numbered version. Reading, writing, twenty flows, three neighbouring
services; 1095 offline tests and 94 live ones against edu-sharing 11.0.

### Added

- **`edusharing.metadata_agent`** — the schemas behind `ccm:oeh_extendedData`.
  `ccm:oeh_extendedType` says what a resource is; which fields belong in its
  JSON area is in no metadata set, only in this service and only at runtime.
  `schemas()`, `schema()`, `content_types()` and `content_type_for()`. The
  authoritative mapping content type → schema file is read from `core.json`
  rather than guessed from file names: `profession` is `occupation.json`.
- **The b-api's forwarded OpenAI routes** — `embeddings()`, `moderate()`,
  `images()` on `BildungsAPI`, plus `call()` for everything else the gateway
  forwards (`responses`, `audio/*`, `batches`, `vector_stores`). Which routes
  are forwarded at all was measured, not read from the specification: see
  `bapi/passthrough.py`.
- **`Node.labels()`** — the readable values of a vocabulary property.
  `SearchHit` has always had it; a node did not, so the same question answered
  URI or label depending on what you held.
- **`LanguageProfile` and `GERMAN`** are importable from `edusharing` directly.
  `GERMAN` was bound but never declared in `flows.__all__`.
- **The 20 examples run as test cases** (`pytest -m live` / `-m write`). An
  example is executable documentation, and documentation nobody executes rots.
- **`docs/REFERENCE.md` and `docs/REFERENCE.de.md`** — every public name, the
  call that uses it, and the shape that comes back, with real outputs. 266
  names; `tests/test_docs_complete.py` fails when one is missing from either
  language, and a second test checks that the field names claimed in its tables
  exist on the classes. Writing it found eleven public names documented nowhere
  (`remove_from_collection`, `remove_keywords`, `collections.remove`,
  `vocab.suggest`, `models()`, `ping()`, `schemas()`, `ChangePlan`,
  `format_hit`, `check_url`) and six wrong field names in the first draft.
- **`docs/examples/19_collection_audit.py`** — audit a collection, and the
  section that matters: an empty `path` is not "sits nowhere". The obvious
  script printed exactly that wrong conclusion; `placement.failed` is what
  tells a refusal from an absence. Measured: signing in does not lift this
  particular refusal.
- **`docs/examples/20_provider_load.py`** — which model should answer, and on
  what basis. `load()`, a virtual model, and OpenAI's refusal side by side.
  Written to keep the `babbage-002` bug fixed.
- **`docs/examples/18_video_recommendation.py`** — the ten best videos on a
  topic, filtered by content type, reranked, as a table, then a model on the
  gateway recommends one. The titles go through `as_untrusted` before they
  reach the model context. Runs without a gateway key: the table is printed and
  the recommendation says it was skipped.
- **`docs/examples/17_flow_belonging.py`** — the three kinds of belonging side
  by side: collection, child object, relation. `child_objects` and `relations`
  were the only two flows without a runnable example.
- **`BildungsAPI.respond()`** — the `responses` route, on **both** providers.
  The assumption was that only OpenAI has it; measured 2026-08-31, the
  AcademicCloud answers it too. Returns an `Answer` rather than a string,
  because `status` can be `incomplete`: a reasoning model given 32 output
  tokens spends all of them thinking and returns the thinking.
- **`reasoning_effort` and `verbosity` on `chat()` and `respond()`**, defaulting
  to `low`. Measured: `gpt-5.6-luna` spent 14 reasoning tokens without the
  parameter and 0 with `low`. Applied only where the model takes them —
  `gpt-4o-mini` answers 400, and the AcademicCloud accepts and ignores them.
  A default is dropped silently; **an explicit value raises instead of being
  dropped**.
- **`BildungsAPI.load()`** — what the provider says about its models right now,
  ranked, with `summary()` for a start-up log. **`reports_load` first**: at
  OpenAI it is false, no load is reported at all, and the ranking is
  alphabetical rather than a statement about queues.
- **`CACHE_FOREVER`** as a model-cache lifetime — ask once and never again.
  Right for a script, wrong for a service, which would then choose models on
  figures from hours ago. The 30-second default stays.
- **A virtual model** — `chat(model=["a", "b", "c"])`, or a name from
  `BildungsAPI(virtual_models={...})`. The least loaded of the named models
  answers, and the next one is tried if it does not. Only the AcademicCloud
  reports load (`demand` 0 to 23 across its 15 models); at OpenAI a group is a
  fallback chain in the order given.
- **`Model.shutdown_date` and `Model.is_retired_on(day)`** — OpenAI reports a
  retirement date for 57 of its 132 models, the AcademicCloud for none.
- **The skill names every door into the library.** It listed all 20 flows and
  every `node.*` call, and three whole areas were still missing: the vocabulary
  API (only the flow was there, not `resolve_all` — this release's fix for
  ambiguous labels), the instance's own answers (`whoami`, `about`,
  `metadatasets`), and `repo.people.*` stood as a bare wildcard. A test now
  derives the accessors from the reference and requires each in both language
  versions.
- **A skill for coding agents**, `.claude/skills/edu-sharing-python/`. A routing
  table from task to call across both levels, the neighbouring services and the
  measured traps, pointing at `wlo-edu-sharing-api` for the raw REST API and at
  `wlo-environments` for addresses rather than repeating either. Three tests
  keep it honest: it must name all 20 flows, invent no call, and use no
  environment variable the code does not read. In English and German, both held
  to those same tests — a translation nobody checks is the first thing to rot.
- **A dependency CVE step in CI** (`pip-audit --skip-editable`).
- **CI has actually run.** The pipeline existed for days without a remote to
  run on; on 2026-08-31 the history was pushed to
  `janschachtschabel/edu-sharing-python-client` and it went green on the
  first attempt across Python 3.11, 3.12, 3.13 and 3.14.
- **A type check in CI** (`mypy`, configured in `pyproject.toml`). It found two
  places that were correct only by accident: a `json.loads` on a value that
  could be `None`, and an `int()` that relied on catching the resulting
  `TypeError`. Both guards are now written so a reader sees them too.

### Changed

- **BREAKING — `BildungsAPI` requires an address.** `base_url` is now a required
  keyword argument, and `from_env()` requires `B_API_BASE_URL` alongside
  `B_API_KEY`. Until now the client fell back to a staging gateway, so setting
  only the key sent it to a host the caller had not chosen. `TextExtraction`
  had always refused exactly that.
  *Migration:* set `B_API_BASE_URL`, or pass `base_url=`.
- **BREAKING — `BildungsAPI.call()` validates its route.** Each segment must
  match `[A-Za-z0-9_-]+`. Previously an unvalidated route could leave
  `/api/v1/llm/{provider}/` entirely: `call("../../administration/account")`
  reached the administration API with the API key attached.
  *Migration:* routes look like `embeddings` or `images/generations`; nothing
  legitimate is affected.
- **BREAKING — the top-level import surface is smaller.** Removed from
  `edusharing`: `Nodes`, `Search`, `Collections` (the accessor classes behind
  `repo.node` / `repo.search`), `credential_from`, `rest_base` and
  `normalize_repository_url` (layer-0 factories). All remain importable from
  their own modules.
  *Migration:* `from edusharing.urls import normalize_repository_url`, etc.
- `relations.create(metadata=...)` now reads back and raises `SilentDropError`
  when the metadata did not arrive. edu-sharing 11.0 accepts it with HTTP 200
  and stores nothing — measured three ways, the last straight at the endpoint.
- A `500` whose body says the instance withholds error details is retried
  **once**, not `max_retries` times. Measured: 4 requests against production
  where staging needs 1, to an address that can never answer.
- Every example configures its instance once, at the top, and no call below
  takes an address of its own. Reading examples run against another repository
  by setting `EDU_SHARING_URL` alone — verified against production.

### Security

- **A real staging password was committed** — in `tests/test_auth.py`, in the
  very test that proves a password does not belong in an error message, and in
  an audit document quoting that message. It is out of the working tree; the
  test now uses an invented value and proves the same thing.
  `tests/test_no_secrets.py` fails if any credential set in the environment
  turns up in a tracked file, and reports the variable name only, never the
  value.

  **It is out of the history as well.** On 2026-08-30 the repository was
  rewritten with `git filter-repo`, replacing the value with
  `PASSWORT-ENTFERNT` in every commit that carried it. Nothing had ever been
  pushed — there is no remote — so the rewrite cost nothing but new hashes.
  Verified: `git log --all -S` finds it in no commit, and a scan of *every*
  object in the repository, reachable or not, returns zero. Only `.env` still
  holds it, and `.env` is git-ignored.

  Every commit hash from that point on changed. The hashes quoted in
  `docs/audits/2026-08-29-audit.md` were re-stamped; hashes quoted inside
  older *commit messages* were not, and now name commits that no longer
  exist.
- The account name used for the measurements is no longer an example value in
  the reference or a docstring. Not a secret, but a live account does not
  belong in published examples.

### Fixed

- The documentation guard mis-read a code span that wraps across a line: it
  paired the closing backtick of one span with the opening backtick of the next
  and treated the prose between them as code. Both error directions — a
  documented name counted as missing, and a prose mention counted as
  documented. Fences are removed first now, and an inline span may wrap.

- **An automatically chosen model that the provider has retired is now logged.**
  19 of OpenAI's 132 were already past their date on 2026-08-31. They are not
  excluded — they still answer, and a caller who names one means it — but when
  the *library* chooses, nobody else is in a position to notice.
- The documentation guard read only top-level assignments and so could not see
  `__version__`, which is assigned inside a `try` for the not-installed case.
  It now reads `try` bodies too.

- **Automatic model selection at OpenAI picked `babbage-002`.** OpenAI reports
  neither load nor output types for any of its 132 models, so every one counted
  as chat-capable and the ranking fell back to the id — alphabetical order
  wearing a ranking's clothes. `chat()` without a model now refuses there with
  a message that names the way out, instead of failing after three wasted
  requests. `is_rankable()` is the check.
- **A search on an ambiguous label found only half the material.** Measured
  2026-08-31, 25 subject labels sit in two vocabularies at once — `Biologie`,
  `Chemie`, `Physik` among them, once under `discipline` and once under
  `hochschulfaechersystematik`. `resolve()` took the first and said nothing.
  `resolve_all()` returns all of them and the search filters on all of them;
  whoever wants the halves apart adds an educational-level filter.
- **Five flows returned keys their own docstrings did not mention**, and the
  unmentioned ones were the ones that matter: `placement.failed` (the way up
  was refused, so an empty `path` is not "sits nowhere"),
  `search_in_collection.unreadable` (collections the walk could not open),
  `add_material.public`, `build_collection.public`, `describe.duplicate_ids`.
  A test now compares each flow's promised shape against the dict it actually
  returns.

- **A cold model cache is filled once, not once per concurrent caller.** The
  cache was checked before the lock and not again inside it, so the lock only
  queued the callers up: six concurrent calls made six requests to `/models` —
  against a gateway that rate-limits the key. `CACHE_FOREVER` now keeps the
  promise its name makes.
- **`ValidationError` instead of a bare `ValueError`** for a reasoning
  parameter a model cannot take, a route `call()` refuses, and an unknown model
  in a group. The reference says every failure is an `EduSharingError`; a
  `ValueError` escaped that, and inconsistently — the same `chat()` call
  converted one of the three and not the other two.
- **A truncated `responses` body no longer raises `AttributeError`.** `_text_of`
  now checks every level, because every level comes from the gateway.
- **`respond()` refuses two ways of setting the same value.** `reasoning` in the
  extra arguments used to win over `reasoning_effort=` silently, because it was
  spread last. Passing only the extra still works — a default steps aside, an
  explicit value does not.
- `load()` judges retirement against the UTC day, not the local one.
- **A busy model no longer consumes the full retry budget while another model
  is available.** A 503 is retryable, so the transport spent all
  `max_retries` on it — roughly 17 s at the default backoff — with a second
  candidate standing right next to it, which defeats the point of naming
  several. A candidate now gets `retries_before_switching` retries (default 1)
  while another remains; the last keeps the full budget, because there is
  nothing left to switch to. The knob only lowers: `max_retries=0` still means
  one attempt each. A 429 is the case it cannot help — the AcademicCloud
  limits the key, not the model.
- **A virtual model tries all its members.** The cap of three belongs to the
  automatic choice, where the library is guessing; naming five means five.

- A child object that could be created but then neither filled nor removed is
  now logged with its id. The caller receives the upload error, which does not
  know the child exists; without the line an empty node stayed behind that
  nobody could attribute.
- An error message from an instance that withholds details now says so, and
  names the setting (`security.logging.displayLevel`). Without it the same
  library returns different error types against two instances for no visible
  reason.
- `TextExtraction.from_env()` reads `EDU_SHARING_TEXT_EXTRACTION_URL`; the
  reference named it `TEXT_EXTRACTION_URL`, and `Repository`'s credential
  argument is `auth=`, not `login=`. Both are now checked by a test.
- The `search` flow's docstring omitted `duplicates_removed` from its return
  shape — a key it has always returned.
- `metadata_agent.content_types()` remembers its answer per `(context,
  version)` instead of refetching a 110 kB `core.json` on every call.
- `metadata_agent` raises instead of returning an empty list when `core.json`
  carries no `ccm:oeh_extendedType` field, or when the schema list is not a
  list. An empty list would read as "this agent describes nothing", which is a
  different statement.
- A query string is no longer logged, and of a foreign address only the host
  is. `Transport.request` accepts absolute URLs and a path handed to
  `repo.raw` can carry `?ticket=`, so the debug line could keep a secret that
  `TextExtraction` had always withheld. Both now follow one rule: log what the
  library built, never what a caller handed over verbatim.
- The README described "two services with their own address" beside a table
  listing three, and named only `B_API_KEY` for the gateway although
  `B_API_BASE_URL` became mandatory in this release. `ARCHITECTURE` still
  listed production testing as deferred, three sections after recording that
  stage 9 was measured against it.
- Three examples were hard-wired to the staging instance and could not be
  pointed elsewhere — in a library whose headline claim is repository-agnostic.
- `15_full_text.py` no longer ends its run when the extraction service returns
  500 for one address, or when a node's content is refused; both are reported
  per row.
