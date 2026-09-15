# Audit follow-up: 22 confirmed findings

Baseline: `cb6ce5c488549cada7c8ee97f6db286dbb634ffa`, draft PR #1.
Workflow: Better Coding Workflow 2.12.0, with design, red/green regressions,
independent review and verification before publishing. Implementation of the
confirmed findings is authorised; speculative feature proposals are outside
this change. No live services or repository data are changed during tests.

## Design

Keep the async resources as the source of truth and the synchronous surface a
thin adapter. Share response-size enforcement below repository and b-api
clients, while keeping their authentication and request policies separate.
Validate service payloads at their typed boundaries. Preserve strict standalone
reads, but let aggregate flows return readable results with explicit warnings
and failures. Existing public calls and valid response shapes stay compatible.

For compressed downloads, checking decoded HTTPX chunks is too late. Rejecting
all compression would break valid downloads. Use incremental bounded decoding
of raw gzip/deflate bytes, with an explicit error for unsupported encodings and
separate bounded error-page handling. Test memory use with a real streamed bomb,
not an already decoded mock response. Any new helper stays private.

For Markdown, raising size limits or adding timeouts would retain quadratic
work. Parse link candidates in one pass and index section ownership and prose
boundaries. Construct only the allowed contexts, retaining all block paths and
the total context count. Resolve skill IDs from their title links; material
preview IDs remain supported.

For generic b-api writes, automatic model-request retries must not imply that
arbitrary routes are safe to repeat. Distinguish repeatable model operations
from generic writes, preserve connect-before-send retries, and surface uncertain
write outcomes. Parse each model candidate before marking it successful, and
respect a service Retry-After instead of switching models under the same key.

For documentation, count options by owning class and method, including Flows
and forwarded keyword options. A method with the same short name must not cover
another receiver. Add negative controls proving that missing documentation is
detected, including multi-line documented signatures as positive controls.

## Work packages

Each package starts by re-applying the workflow, writes regressions first,
records the failing command, makes the smallest coherent corrections and reruns
the targeted checks. Existing large modules are
split only where a separate responsibility warrants it; generated code is not
edited. Commits can be reverted individually, in reverse order if dependent.

| Package | Findings | Main files | Acceptance evidence |
| --- | --- | --- | --- |
| 1: cancellation, limits, Markdown | A01–A04, A12 | `_sync.py`, `_http.py`, private decoding/outline helpers as needed, `skills_markdown.py`, `extraction.py` | Interrupted queued write never sent; bounded decompression; linear malformed-link and capped-outline work; correct skill ID; secrets absent from logs |
| 2: service contracts and retries | A05–A07, A17 | `bapi/client.py`, `bapi/passthrough.py`, `bapi/models.py`, `metadata_agent.py` | Uncertain generic write sent once; connect retry control; malformed payloads raise library errors; fallback validates each candidate; long Retry-After preserved; unknown demand sorted last |
| 3: aggregate results and permissions | A08–A11, A13–A16 | `flows/tree.py`, `flows/text.py`, `flows/pages.py`, `flows/contents.py`, `flows/dedupe.py`, `skills.py`, `search.py`, permissions resource | Readable branches/files survive failed siblings; warnings survive aggregation; repository failure becomes flow result; aliases isolated; final ACL checked after no-op; per-record counts; ID-less hits never become duplicate anchors |
| 4: documentation and its guard | A18, U1–U4 | READMEs, both REFERENCE/FLOWS languages, docs option tests, generated skill copies | Binary example uses `call_bytes`; correct skill folder and all installation paths; explicit permanent-delete option; Flows and forwarded options covered; receiver collision negative controls |

## Verification and release

Run focused regressions red before production edits, then green with relevant
existing tests. Finish with the complete offline suite, Ruff, mypy, skill-copy
synchronisation, and relevant packaging checks. Read the final diff with the
review skill and an independent reviewer; verify with the verification skill.
Fetch remote state again, publish to the existing PR branch without force, and
check CI for the new commit. Do not merge the draft PR.

Risks: HTTPX's already-buffered responses differ from real raw streams; multiple
content encodings need bounded intermediate decoding; cancellation after a
server accepted a request cannot undo that write; tolerant aggregate reads must
not conceal root errors; documentation parsing must handle forwarding and
multi-line code without weakening coverage. Tests cover these boundaries.

## Evidence log

All four packages are implemented. Each was reviewed separately with
`better-coding-review`; the final source and documentation are published as one
coherent follow-up commit because the expanded option guard depends on the new
signatures and both references. This avoids publishing an intermediate commit
whose documented public contract is incomplete.

### Regression evidence

All commands below used Python 3.12.14 and the existing development environment.
The test command was `python -m pytest -q -p no:cacheprovider --tb=short`, followed
by the named test files. Tests use local fake transports and never real writes.

| Findings | Regression files | Red observation and corrected behavior |
| --- | --- | --- |
| A01 | `tests/test_sync_cancellation.py` | Interrupting the waiting synchronous caller still allowed a POST. Both an already-started coroutine and a task queued before loop startup now cancel without sending the deferred write. |
| A02 | `tests/test_http_bounded.py` | A streamed 32 MiB expansion allocated 81,145,840 bytes despite a 1 KiB cap. Bounded decoding stays below the test's 2 MiB ceiling. Cases cover raw/zlib deflate, gzip, chained encodings, error pages and supported-encoding negotiation. |
| A03, A12 | `tests/test_skills_markdown.py` | Malformed link and heading-heavy inputs each took over 13 seconds; they now satisfy the 3 second ceiling. Skill IDs come from title links, including custom skill-kind conventions; material preview IDs remain supported. |
| A04 | `tests/test_extraction.py` | An unsafe URL leaked synthetic path/query secrets into the warning. They are absent after the fix, and the request is not sent. |
| A05–A07, A17 | `tests/test_bapi_boundaries.py`, `tests/test_metadata_agent.py` | The initial service-boundary run had 20 failures and 2 passing controls. Uncertain generic writes are sent once, connect failures still retry, explicit idempotency enables repeats, malformed objects raise library errors, chat validates each candidate, Retry-After survives selection, and unknown demand sorts last. |
| A08–A11, A13–A16 | `tests/test_flow_audit_boundaries.py`, `tests/test_flows_tree.py`, `tests/test_skills.py`, `tests/test_flows_dedupe.py` | The initial run had 10 failures and 1 passing control. Readable sibling results, files and warnings survive aggregation; root errors remain strict; metadata failure gets a flow reason; client aliases are isolated; no-op unpublish checks the latest ACL; labels count once per record; ID-less duplicates do not hide usable hits. |
| A18, U1–U4 | `tests/test_docs_options.py`, existing documentation tests | The old guard failed the Flows inventory, receiver-collision and multiline controls. Tightening it exposed 63 missing reference placements per language. Further red controls cover nested calls and removal of actual receiver-specific entries. Both references, installation instructions and binary examples are corrected. |

The focused runtime groups passed after the corrections: 74 synchronous tests,
229 service tests and 324 flow-related tests. These groups overlap and are not
added together as a total-suite count.

### Review corrections

The independent reviewer checked the four packages in separate sittings. Its
additional reproductions found and verified corrections for task-startup
cancellation, ambiguous raw-deflate headers, and bounded-request encoding
negotiation. It compared the Markdown outline against the baseline on 2,000
deterministic mixed-heading documents and checked nested compression limits.

The documentation review found one option consumed inside `**kwargs`:
`Skills.pick(include_files=...)`. Making it an explicit keyword-only parameter
preserves existing calls and makes its contract inspectable without adding a
special-case AST interpreter. Three inventory/removal controls failed before
this correction. Both `Skills.pick` and `Flows.pick_skill` now document it.
The measured inventory is **247 class/method/option tuples, including 81 on
Flows**. The review also removed an unsupported `sort` keyword from the search
table. Existing tests already verify the behavior of `pick(include_files=False)`.

The first complete offline run found the two new private modules missing from
the architecture inventories. Both language versions now name their distinct
responsibilities. The subsequent focused run passed **139 tests**, covering
options, module inventories, skills and b-api boundaries.

### Final verification

Fresh checks on the final source, 2026-09-14:

| Check | Result |
| --- | --- |
| `python -m pytest -q -p no:cacheprovider --tb=short --cov --cov-branch --cov-report=term --cov-report=json` | **2585 passed, 10 skipped, 194 deselected**, 107.32 seconds |
| Coverage, handwritten library only | **98.23% combined**; 5279/5347 statements and 1221/1270 branches covered |
| `ruff check .` | All checks passed |
| `mypy` | No issues in 69 source files |
| `python scripts/sync_skill.py --check` | Exit 0; reference copies match |
| `git diff --check` | Exit 0 |
| `uv build` | Wheel and source distribution built successfully |
| Wheel installation into a fresh environment outside the checkout, followed by importing every package module | **1199 modules imported, 0 errors** |
| Independent final documentation review and its focused checks | PASS in all review categories; **209 tests passed**, no remaining findings |

No generated endpoint or dependency declaration changed in this follow-up.
Publishing uses the existing draft PR branch, without a force update or merge.
CI must be checked against the new remote SHA; the prior branch's green run is
not evidence for this change. Live tests remain excluded because they require
real services and, in some cases, write to them.
