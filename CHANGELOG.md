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

Nothing yet.

## [0.0.1] — 2026-08-31

First numbered version. Reading, writing, twenty flows, three neighbouring
services; 1093 offline tests and 93 live ones against edu-sharing 11.0.

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
- **The 17 examples run as test cases** (`pytest -m live` / `-m write`). An
  example is executable documentation, and documentation nobody executes rots.
- **`docs/REFERENCE.md` and `docs/REFERENCE.de.md`** — every public name, the
  call that uses it, and the shape that comes back, with real outputs. 266
  names; `tests/test_docs_complete.py` fails when one is missing from either
  language, and a second test checks that the field names claimed in its tables
  exist on the classes. Writing it found eleven public names documented nowhere
  (`remove_from_collection`, `remove_keywords`, `collections.remove`,
  `vocab.suggest`, `models()`, `ping()`, `schemas()`, `ChangePlan`,
  `format_hit`, `check_url`) and six wrong field names in the first draft.
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
- **A skill for coding agents**, `.claude/skills/edu-sharing-python/`. A routing
  table from task to call across both levels, the neighbouring services and the
  measured traps, pointing at `wlo-edu-sharing-api` for the raw REST API and at
  `wlo-environments` for addresses rather than repeating either. Three tests
  keep it honest: it must name all 20 flows, invent no call, and use no
  environment variable the code does not read. In English and German, both held
  to those same tests — a translation nobody checks is the first thing to rot.
- **A dependency CVE step in CI** (`pip-audit --skip-editable`).
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
