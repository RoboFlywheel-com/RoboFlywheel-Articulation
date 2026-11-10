# Verification snapshot

This records the two local migration audits. It does not certify every continuous
configuration of every historical generator.

## Public checkout review

The public-installation review replaces the internal package mirror in `uv.lock`
with HTTPS PyPI sources. All 121 locked dependency releases and 1,061 artifact
hashes were checked against PyPI release metadata. Package versions, dependency
edges, platform markers and hashes remain unchanged. `uv lock --check --offline`
passes with the public index selected.

The RFW-A CLI regressions pass (26 tests). The README hinge example exports all
three seeds successfully without provider credentials. Source and wheel builds
pass; the newly built wheel was installed separately and exported the same three
seeds while using the already tested dependency environment. Imports were checked
to come from that wheel installation rather than either legacy workspace.

A separate checkout and empty virtual environment also started a locked install
from public PyPI. That run was stopped during slow public artifact downloads; it
is **not** counted as a completed fresh public installation. PyPI metadata/hash
verification and the installed-wheel smoke test do not remove that limitation.

## Latest results

- The robotic-arm matrix completed: **146 passed**, comprising all 144 module
  combinations, the seed-zero anchor, and the gripper-subtype check. The previous
  single serial loop is now parametrized, preserving coverage while allowing
  independent scheduling and identifying the exact combination on failure.
- The rest of the full suite completed separately: **3,076 passed, 73 skipped,
  36 expected failures, one unexpected pass, and no new failures**. The recovered
  crane case was then removed from the historical failure list and passed again
  as a regular test. No failures were added to that list.
- The affected source-map, image-authoring, import, material-batch policy, storage
  and CLI regressions passed in a separate 56-case run. A final seven-case run
  verified import retry/hash receipts and the recovered crane case.
- Actual `rfwa sample robotic_arms` runs for seeds 0 and 9 (a dexterous hand)
  exported complete assets and passed sampled motion checks. Logs and outputs
  are under `/tmp/rfwa-second-audit-robot-*`.
- All 531 registered generators import, expose their expected build/test
  interfaces, and resolve configurations for seeds 0 and 1.
- The image seed → fork → source pool → SourceMap → blueprint filesystem workflow
  passes integration tests without provider calls. Source programs in these tests
  are fixtures, not live model-generated geometry.
- Python 3.12 isolated-environment dependency checks, focused Ruff checks,
  `git diff --check`, source distribution and wheel builds pass. Separate wheel
  installation and real mixed-result hinge sampling were verified during audit.

For repeatable audit timing, the latest two matrix runs constrained CPU affinity
to 16 CPUs **before** importing native CAD/numeric libraries, with eight pytest
workers. Ordinary CLI behavior and generator geometry were not altered by this
process setting. Normal CLI sampling of the two robotic-arm seeds also passed
without this audit affinity setting.

## Fixes from the continued audit

- SourceMap membership now comes from current records and picture sidecars. An
  outdated category index cannot hide newly imported or restored source assets.
- Material sampling publishes seeds independently. A seed's export failure is
  retained in `sampling.json`; successful exports survive and the batch continues.
  Counts/status describe actual exports, and reports do not reference deleted
  temporary validation directories.
- Source import copies the reference picture before committing the record. An I/O
  failure leaves the record ID available for retry instead of half-imported.
  Import receipts also retain the reference image SHA-256.

## Earlier audit fixes

- CLI checks and viewer source discovery default to this checkout's
  `data/records`, instead of the sibling legacy data repository. Viewer records
  can be overridden with `RFWA_RECORDS_ROOT` or `ARTICRAFT_RECORDS_ROOT`.
- The fixed louver leaf's socket spans its resolved frame clearance.
- The drop-down oven door has a physical hinge pin spanning its panel-to-pivot gap.
- Provider-preview tests isolate the host's configured base URL; invalid reference
  image paths are rejected before importing records.

The default practical policy remains a configurable 90% sampled pass rate, with
passing assets exported and failed seeds logged/skipped. Mechanical checks were
not relaxed to make regression tests pass.

## Limits and logs

The 36 historical expected failures remain documented in
`tests/known_failures.txt`. Optional external-library/tool tests skip explicitly;
they do not establish that the full released material dataset is present.
This audit did not exercise live provider calls, the complete frozen PBR library,
or simulator dynamics. Material-batch fault handling is tested with controlled
exporter failures; inherited exporter tests cover portable trees with fixtures.

Latest logs:

- `/tmp/rfwa-robotic-combinations.log` and its JUnit XML: 146-case robotic-arm run.
- `/tmp/rfwa-second-audit-full.log` and its JUnit XML: remaining full suite.
- `/tmp/rfwa-second-audit-final-core.log`: 56 affected regressions.
- `/tmp/rfwa-second-audit-final-regressions.log`: import/hash/retry and crane checks.
- `/tmp/rfwa-second-audit-robot-sample.log` and
  `/tmp/rfwa-second-audit-robot-hand.log`: real exports and motion diagnostics.

`/tmp/rfwa-audit-full.log` is the **earlier**, interrupted pre-fix run. Its five
failures were repaired and retested; it is not the latest test result.
