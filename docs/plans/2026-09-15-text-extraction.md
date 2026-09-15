# Text extraction: repository address convenience

## Existing capability and scope

Baseline: main `8ace0759c93b51716124cb890610bad99f37fdc1`.
The supplied API examples are already supported by `TextExtraction.text_of`:
`simple`/`browser`, `txt`/`markdown`, language, target-page status and truncation.
`browser_location=null` and `preference="none"` match the service defaults.
The client already works with any explicitly configured service address.

The missing convenience is choosing the sibling service for installations that
use `repository.<domain>` and `text-extraction.<domain>`. Implement one explicit
factory, `TextExtraction.from_repository(repository_url, **kwargs)`, reusing URL
normalization and the existing client. `repo.url` works for both repository
facades. Preserve scheme and non-default port; remove repository path prefixes.
Reject other hostname conventions and malformed addresses with an actionable,
credential-free error. Construction performs no DNS, HTTP or availability probe.

Keep `from_env` explicit and unchanged: it still needs
`EDU_SHARING_TEXT_EXTRACTION_URL`. Do not silently enable page extraction in
flows or assume that every repository runs a service. Other deployment layouts
continue to use `TextExtraction(base_url=...)`.

## Implementation and verification

1. Add HTTP-boundary tests for host derivation, paths/ports, no implicit probes,
   invalid configuration, client ownership and both supplied output modes.
   Run red, add the factory, run green.
2. Add a small URL-to-text/Markdown file example with its offline exercise.
   Document the factory, configuration choice and existing extraction/flow use
   in README and reference EN/DE; synchronize the bundled skill and examples.
3. Run focused tests, the complete offline suite and relevant existing quality
   gates. Review the diff independently, then use the already authorized
   push/PR/merge workflow and verify the remote tree and CI.

No new service, browser runtime, crawling scheduler, dependency or automatic
repository write is needed. The supplied samples are the API evidence; live
service verification is reported separately if reachable.

## Verification outcome

- Regression tests first reproduced the missing factory and example. The fresh
  review also reproduced malformed DNS labels accepted by HTTPX; the factory now
  checks ASCII/IDNA labels and the derived hostname length before construction.
  International names remain supported, and invalid configuration errors contain
  no credentials or query values.
- The complete offline suite passes: **2697 passed, 13 skipped, 197 deselected**
  (117.07 seconds). The first full run caught the example inventory and missing
  required-parameter notation in both skill entry points; both are corrected.
- Ruff passes; mypy reports no issues in 76 source files. Skill validation,
  reference/example synchronization, CLI help and `git diff --check` pass.
- `uv build` creates the wheel and source distribution successfully.
- Independent follow-up review: spec compliance, security, correctness,
  performance, maintainability, tests and docs pass; no remaining findings.
- The new HTTP-boundary tests cover both supplied service modes. No live
  extraction request was performed during this change; the supplied API samples
  and existing service contract tests are the evidence for the request format.
  The GitHub PR records the CI results for the committed revision.
