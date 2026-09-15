# Design: generic metadata and composed application flows

## Goal and authority

Implement the functional audit of main `7d85186`: repository-specific metadata,
lossless vocabulary values, reusable metadata loading and three application flows.
The user authorizes implementation decisions, documentation changes and pushing
the result to GitHub. No live repository content writes are needed for development.

## Decisions

Keep the async-first, dependency-light architecture (Python >=3.11, httpx, attrs),
the synchronous adapters and JSON-returning flows. Generated endpoints remain
unchanged. Tests mock HTTP boundaries, not the public feature being verified.

Three approaches were considered for field independence:

1. Extend filter aliases into implicit write aliases: small but conflates label
   filters, one-to-many writes and raw property access.
2. Add one immutable MetadataProfile per connection: explicit read/write roles,
   search conventions and optional content fields, shared by existing consumers.
3. Generate all operations from a complete MDS: cannot infer query acceptance or
   semantic roles from widgets and would introduce unnecessary machinery.

Use approach 2. Preserve existing calls through a named compatibility profile;
an explicitly supplied empty/custom profile must never inherit its application
fields. Document the distinction prominently. No global mutable field overrides.
WLO-specific examples are allowed, and existing behavior must remain testable.

## Packages and acceptance criteria

### 1. Value identity and search

Step 0: invoke /better-coding-workflow.

Files: vocab.py, search.py, fields.py, flows/find.py, flows/rerank.py,
flows/serialize.py and the Flows facade; focused regression tests.

- Returned vocabulary collections cannot mutate the cache.
- Known stored keys (including URNs and codes) resolve by exact identity before
  labels; HTTP(S) passthrough remains compatible.
- Search gains explicit raw_filters, locale and strict handling of unresolved
  labels. Raw values are never inferred from a failed label lookup. Conflicting
  raw/label criteria for the same property fail before the search request.
- These options survive reranking and mixed-search forwarding.
- related() prefers stored values; only label-only legacy responses use label
  resolution. Equal labels must not expand a known stored identity.
- Vocabulary flows return entries with value and label beside legacy label lists;
  serialized hits expose stored values alongside their readable projection.

Verify failing then passing tests for mutation, two same-label keys, missing
DISPLAYNAME, locale, raw values and strict unresolved behavior. Existing flow
and reranking behavior remains covered.

### 2. Repository metadata profiles

Step 0: invoke /better-coding-workflow.

Files: new profile.py; repository.py, nodes.py, nodes_write.py, results.py,
ranking.py and direct consumers of title/description/URL/keywords.

- MetadataProfile owns immutable role-to-property mappings and filter aliases.
- Explicit profiles replace compatibility roles; empty mappings remain empty.
- Node.create/update and write flows use configured fields and node type.
- Node/SearchHit projections, URL duplicate checks and keyword ranking use the
  same profile. Technical cm:name stays the node name required by the protocol.
- Missing requested write roles raise a clear validation error before writing.
- Two repository objects with different profiles do not influence each other.

Verify custom fields for create, update, reading, URL matching and ranking,
neutral-profile writes, mutation resistance and default compatibility.

### 3. Metadata catalog and vocabulary reuse

Step 0: invoke /better-coding-workflow.

Files: new metadata.py; vocabulary loading/snapshot helpers; repository.py and
_sync.py adapters.

- repo.metadata loads full MDS definitions through the existing endpoint and
  caches independent copies with TTL and explicit refresh/clear.
- Expose definition and actual widget field information without claiming that
  presence proves searchability.
- Vocabularies can be preloaded for selected properties/locales with bounded
  concurrency and can export/import JSON-compatible snapshots.
- Snapshot context includes repository, MDS, query, locale and an explicit
  caller-supplied visibility scope. Reject incompatible/malformed snapshots;
  preserve original age rather than silently making stale data fresh.
- No filesystem writes, background threads or extra dependencies in the APIs.

Verify request coalescing, caller mutation, refresh, context/age validation,
round trips and synchronous access. Failures are not cached as empty catalogs.

### 4. Composed flows

Step 0: invoke /better-coding-workflow.

Files: new narrowly scoped flow modules and facade methods, collection placement
response adapter, selected existing helpers.

- place_material: use existing material, expose original/reference/collection
  identities, optional publication and explicit removal of an old placement.
  Use the mutation response, not immediate membership-index visibility. Never
  remove an old placement after a failed new placement; expose partial state.
- collection_context: combine description, one bounded contents read and derived
  statistics; optional configured compendium and registry, with errors and limits.
- prepare_material: read-only URL extraction/duplicate check/catalog and vocabulary
  normalization into a proposal. No implicit LLM and no writes. Unknown duplicates,
  unresolved values and required inputs must be distinguishable from success.

Verify HTTP method/path behavior, write count, IDs, partial failure, bounded reads,
configured metadata and JSON output. Keep pagination/indexing recipes in examples;
do not add a generic widget executor, learning-path engine or background cache.

### 5. Documentation, release and completion

Step 0: invoke /better-coding-workflow.

Update README EN/DE, REFERENCE and FLOWS EN/DE, ARCHITECTURE, examples,
the bundled skill and its synchronized references, changelog and package version.
Add the audit disposition and migration instructions. Use the repository's
existing synchronization commands and guards.

Run focused red/green tests during development, then the complete offline test
suite, Ruff, mypy, build and installed-package checks required by CI. Review the
final diff independently. Commit logical changes and push the feature branch;
use the existing authorized PR/merge workflow where possible and verify the
remote commit and CI results. No PyPI publication is requested.

## Risks and limits

MDS widgets do not establish query compatibility; full-text and collection query
conventions require explicit configuration. Metadata validation remains partly
server-side. Repository operations are not transactional across publication and
collection APIs, so partial states must be returned rather than hidden. Real
cross-instance acceptance remains unverified without suitable live endpoints.

## Progress

- [x] Audit and current main rechecked; workflow and design reviewed.
- [x] Value/search regressions fixed.
- [x] Profiles wired through read/write/ranking consumers.
- [x] Catalog and vocabulary reuse implemented.
- [x] Three composed flows implemented.
- [x] Documentation, examples, skill and version synchronized.
- [x] Independent review and local verification complete (2662 tests passed).

- [x] Remote push and [PR #2](https://github.com/janschachtschabel/edu-sharing-python-client/pull/2)
  merged into `main` at `24d973f` on 2026-09-15; all eight CI jobs passed before
  and after the merge. The remote tree matches the tested local tree.

The implementation is complete. Version 0.3.0 is the Git version; the release
tag awaits the live acceptance required by the repository release procedure.
[Audit disposition](../audits/2026-09-14-functional-implementation.md).

## Documentation closeout — 2026-09-15

The follow-up request is to finish the adjustment and update README/docs as
needed. Main already contains the functional work and has successful CI.

- README EN/DE: explicit upgrade to main, completion/report links and corrected
  instructions for the pending release rather than reusing the old 0.2.0 tag.
- ARCHITECTURE EN/DE: current implementation status and accurate requirements
  for custom metadata aliases, searchability and label locales.
- Audit/changelog: record the completed merge and the documentation corrections;
  preserve the distinction between offline/CI verification and live acceptance.
- Verification: run the existing documentation, skill-bundle and generic-example
  checks, check the diff, then use the authorized push/PR/merge workflow.

This closeout changes documentation only; no new library APIs or dependencies
are needed. The existing examples and bundled skill already describe the new APIs.
