# Audit fixes, 14 September 2026

Base: `9541665f7f98a28586d926620f4ad585fc19feae`. The user requested implementation
of the fresh audit using `better-coding-workflow` 2.12.0. The already corrected
A01/A02/D01 remain regression controls. This plan covers B01–B04, D02 and R10;
the seven larger flow proposals and live repository writes are separate work.

## Contracts and decisions

- Python >=3.11, existing dependencies only; preserve the independent generated
  layer and the asynchronous core. Keep English and German public docs aligned.
- B01: retain the JSON return contract of `call()` and add the explicit
  `call_bytes(route, body, *, provider=None, max_bytes=None) -> bytes`. A mixed
  implicit return type would make every existing caller inspect its answer;
  merely removing the audio example would leave the requested flow unavailable.
  Reuse request retries, headers, route checks and concurrency. Extract the
  existing bounded HTTP response reader without changing its behavior, so audio
  and repository downloads share decoded-byte limits and gzip handling.
- B02/B03: validate required decisions and nested values before using them.
  Malformed data raises `EduSharingError` with a route/field, without echoing
  payload contents. Preserve documented absent/nullable text fields and the
  existing tolerated non-text output entries. Embedding results must contain
  exactly one uniquely indexed numeric vector per effective input, reordered
  by index. Do not add a general schema framework or a validation dependency.
- B04: normalize scheme and host, leaving user information, port, path, query
  and fragment intact. Preserve diagnostic masking and stored URL data.
- D02: distinguish the low-level searcher's property names from the search
  flow's facet aliases, in both skill entry points.
- R10: generate explicit `ValueError` guards for empty and whole-dot path
  parameters before URL construction. Use a small deterministic AST-guided
  postprocessing step in the existing generator. Keeping the documented gap
  would not fix it; vendoring a complete upstream Jinja template for one change
  would add avoidable maintenance. Never hand-edit generated endpoint files.
  Guard insertion must fail visibly if the generator's quote expression shape
  changes, and remain idempotent. Generated code does not import the handwritten
  library or its exception classes.

No public endpoint, credential source, model choice, retry policy or default
publication behavior changes. Binary size limits are optional as with existing
downloads. Real gateway/audio and private-file behavior remain unverified here.

## Package A — b-api boundaries

Step 0: invoke `/better-coding-workflow`.

1. Add `tests/test_bapi_response_validation.py` for B02/B03 using MockTransport:
   missing/null/non-boolean moderation decision; malformed chat message, response
   details, text and image entries; incomplete, duplicate and invalid embedding
   indices. Include valid empty/optional fields and reordered complete vectors.
   Run `pytest -q tests/test_bapi_response_validation.py` before implementation;
   the original cases must fail because they return approval/incomplete data or
   raise a built-in exception instead of the library error.
2. Add a small private `bapi/_response.py` for reusable field checks. Modify
   `bapi/body.py` and `bapi/passthrough.py` at the existing parser boundaries.
   Verify against the new tests and existing body, passthrough and template tests.
3. Add `tests/test_bapi_binary.py`: a binary HTTP 200 roundtrip; typed JSON error;
   unsafe route rejected before sending; decoded size limit and gzip control;
   failed response stream closed; supplied client remains owned by the caller.
   Run before adding `call_bytes` and observe the missing-method failure.
4. Extract the current bounded reader from `transport.py` to `_http.py`, retaining
   the existing download contract. Add the binary path to `bapi/client.py` and
   `bapi/passthrough.py`, sharing request and route handling. Run binary tests,
   existing transport/download tests, b-api tests and the configured mypy/Ruff checks.
5. Document `call_bytes` and parser errors in both references, update the JSON
   route example and changelog, then sync skill reference copies.

## Package B — URL equivalence and skill guidance

Step 0: invoke `/better-coding-workflow`.

1. Extend `tests/test_flows_duplicates.py` through `find_by_url()` with stored
   `https://alice:DummyPass@example.test/a`: identical/host-case variants match;
   username/password/path-case variants do not. Include bracketed IPv6 and ports.
   Run these tests before changing `_comparable()` and observe the false matches.
2. Fix the authority normalization in `flows/duplicates.py`; rerun the duplicate
   tests, including malformed URLs and masked diagnostic controls.
3. Correct `.claude/skills/edu-sharing-python/SKILL.md` and `SKILL.de.md` and
   update the changelog. This is a text correction; use the existing executable
   facet flow and documentation checks instead of another text-matching test.

## Package C — generated path guards

Step 0: invoke `/better-coding-workflow`.

1. Update the old R10 observation tests in `tests/test_generated_layer.py` to
   require rejection before a request can be built. Those tests intentionally
   pinned the known bug, so their expected behavior changes with this repair.
   Add valid dotted/escaped identifier controls and a generator idempotence test.
   Run first: old generated code must fail the rejection tests.
2. Add the generation pass in `scripts/generate_client.py`, regenerate in place
   with `python scripts/generate_client.py`, and run the generator/path tests.
   Confirm every generated path-parameter quote is preceded by a guard.
3. Replace the current documented gap in `urls.py` and both references; add the
   generator decision to architecture/provenance and this plan. Historical audit
   descriptions remain historical, with a link to the resolved state.

## Final evidence and integration

- Run the complete configured offline suite: `pytest -q --tb=short`.
- Run `ruff check .`, `mypy`, `python scripts/sync_skill.py --check`, matching CI.
- Regenerate twice and verify byte-identical output; build a wheel/sdist and
  check installation/imports because generated and new internal modules changed.
- Review handwritten changes in small passes using `better-coding-review`:
  contract compliance, correctness/security, edge cases and unnecessary code.
- Apply `better-coding-verify` before completion. Record actual red/green and
  final outputs below. Commit logical packages on `fix/audit-2026-09-14`, push
  that branch and open a draft PR; do not merge to main or run live write tests.
- Rollback is a revert of the relevant logical commit. The generated guard
  commit includes its generator change, generated output and documentation.

## Evidence log

Verified locally on Python 3.12.14 with the locked development dependencies.
The commands below used that environment's interpreter and executables.

### Regression evidence

- B02/B03, before implementation: `test_bapi_response_validation.py` reported
  **29 failed, 4 passed**. Failures were silent acceptance or built-in exceptions.
  Three later vector-shape cases were also run red before adding their guard:
  **3 failed, 33 passed**. All 36 now pass.
- B01, before implementation: all **9 binary tests failed** because `call_bytes`
  did not exist. All 9 now pass, including gzip, stream cleanup and typed errors.
- B04: before the normalization fix, the new comparison cases reported
  **3 failed, 4 passed**; all 7 now pass.
- R10: the updated rejection tests failed against the old generated layer.
  A separate comparison using the original function from Git confirmed that
  `.` built `/edu-sharing/rest/node/v1/nodes/-home-` and `..` built
  `/edu-sharing/rest/node/v1/nodes`. The corrected function rejects both before
  request construction. All **24 generated-layer tests** now pass.
- The existing embeddings route fixture returned two vectors for one input.
  It now returns one; the routing assertion is unchanged. The proxy API surface
  inventory explicitly includes the intentional new `call_bytes` method.

### Final verification

| Check | Observed result |
|---|---|
| `python -m pytest -q -p no:cacheprovider --tb=short` | **2525 passed, 10 skipped, 194 deselected**, 75.99 s |
| `ruff check --no-cache .` | **All checks passed** |
| `mypy` with an external cache directory | **No issues in 67 source files** |
| `python scripts/sync_skill.py --check` | **Exit 0**; English/German reference copies match |
| Repeated `python scripts/generate_client.py` | **1132 files byte-identical**, including provenance; 1131 Python files parse |
| Exhaustive generated path check | **278 endpoints, 499 parameters, 1497 invalid values rejected** before request construction |
| Generated diff check | Removing only the new guards yields the original AST in every affected endpoint |
| `uv build` | Wheel and source distribution built successfully |
| Fresh wheel installation outside the checkout | **1197 package modules imported, 0 errors**; binary API and generated guards present |
| `git diff --check` | **Exit 0** |

The first full run found two missing architecture inventory entries for the new
internal modules, with 2523 other tests passing. Both language versions were
corrected and the complete suite rerun to the result above. The final build was
made after removing temporary generation output; wheel and sdist were checked
to exclude that intermediate specification.

### Requirements and review

- [x] B01: explicit binary response API, bounded decoded bytes and shared HTTP
  error/retry behavior — `tests/test_bapi_binary.py` and transport regressions.
- [x] B02/B03: explicit moderation decisions and validated nested responses /
  complete vectors — `tests/test_bapi_response_validation.py`, existing proxy
  and template suites.
- [x] B04: credential case preserved in URL equivalence —
  `tests/test_flows_duplicates.py`.
- [x] D02: skill guidance distinguishes low-level properties from flow facet
  aliases — paired docs and existing `test_flows_search_more.py` facet behavior.
- [x] R10: repeatable independent generated guards, valid escaping retained —
  `tests/test_generated_layer.py`, regeneration and exhaustive path checks.
- [x] Public references, skill copies, architecture and changelog updated.

Review used `better-coding-review` 2.12.0 against the plan and the base commit,
in small handwritten-code passes. Generated output was checked mechanically.
The two documentation omissions found during verification are resolved.

```text
Spec compliance: PASS
Security: PASS   Correctness: PASS   Performance: PASS
Maintainability: PASS   Testing: PASS   Docs: PASS
Automated tooling: linter=pass, types=pass, tests=pass, build=pass
Security scanner/dependency audit: not run locally; existing CI retains its audit.
All findings verified against source.
Verdict: no remaining findings in the reviewed change.
```

### Limits and integration

No live gateway generation or repository writes were exercised. Binary provider
support is verified at the HTTP client boundary using synthetic responses;
availability of a specific model/route remains a gateway concern. The existing
CI supplies Python 3.11–3.14, Windows and minimum-dependency coverage after push.
No new dependency or package version was introduced. The seven larger flow
proposals remain separate from this repair.

Integration target: draft PR from `fix/audit-2026-09-14` to `main`. The final
review and verification apply to the complete branch; main is not merged here.

Publication history: automatic approval review initially rejected the push because it
requires explicit permission for the external GitHub mutation and destination.
A read-only GitHub branch listing confirmed that the branch was not created.
The user subsequently explicitly authorized pushing the changes to
`https://github.com/janschachtschabel/edu-sharing-python-client` on 2026-09-14.
The branch is published under that authorization; main remains a separate merge.
