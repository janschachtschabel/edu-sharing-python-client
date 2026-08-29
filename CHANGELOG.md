# Changelog

All notable changes to this project are recorded here, following
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/). Versions follow
[Semantic Versioning](https://semver.org/).

Nothing has been released yet: the project sits at `0.0.0` and is not on PyPI.
Until a first release, breaking changes carry no migration burden — they are
recorded anyway, because the habit has to exist before it is needed.

Every entry that names a number was measured. Where a change came from a
measurement against a live instance, the date and the instance are in the code
and in [`docs/audits/`](docs/audits/).

## [Unreleased]

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
- **The 16 examples run as test cases** (`pytest -m live` / `-m write`). An
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
- **A skill for coding agents**, `.claude/skills/edu-sharing-python/`. A routing
  table from task to call across both levels, the neighbouring services and the
  measured traps, pointing at `wlo-edu-sharing-api` for the raw REST API and at
  `wlo-environments` for addresses rather than repeating either. Three tests
  keep it honest: it must name all 20 flows, invent no call, and use no
  environment variable the code does not read.
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

### Fixed

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
- Three examples were hard-wired to the staging instance and could not be
  pointed elsewhere — in a library whose headline claim is repository-agnostic.
- `15_full_text.py` no longer ends its run when the extraction service returns
  500 for one address, or when a node's content is refused; both are reported
  per row.
