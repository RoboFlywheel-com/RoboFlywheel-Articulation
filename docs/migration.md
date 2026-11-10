# Migration from the PVA workspaces

**Default policy:** prioritize usable output. Checks use a configurable 90%
sampled pass-rate threshold. Sampling exports passing assets and logs/skips failed
seeds; a mixed batch returns `partial` and succeeds if it produces any valid assets.
Legacy blueprint/source gaps and corner failures are diagnostics, not default
category-wide blockers. Add `--strict` to `check` or `release` only when you want
all-cases-pass and complete coverage/provenance. The stricter requirements described
below refer to that optional mode.


This codebase was assembled in a new branch of RoboFlywheel-Articulation. The
two original workspaces remain unchanged. The migration follows the current
RFW-A manuscript's generator-construction and procedural-sampling formulation.

## What was retained and why

`arti-template` supplies the SDK, reusable category generators, source-map and
blueprint schemas, mechanical checker, material exporter, source-record runtime,
viewer and existing regression tests. Its working-tree files were imported
selectively, with per-file hashes recorded in `migration_inventory.json`.
The source Git revision is recorded there, but working-tree hashes are the
authoritative identification of imported contents.

`articraft_data` supplies the source-asset/workbench side of the original workflow.
Inspection found extensive shared code with `arti-template`: 60 common agent
Python files, 64 SDK files, 22 storage files and 11 CLI files. Their working trees
have diverged. Replacing the generator workspace's SDK/compiler with the data
workspace versions would break its newer blueprint and material interfaces.
The unified release therefore uses one coherent runtime from `arti-template`,
retains source-generation/record management through `rfwa source`, and adds
`rfwa import-source` to ingest the data workspace's records without altering
ratings or revisions. Configurable generation defaults follow the data-side
convention, accepting `RFWA_MODEL`/`RFWA_THINKING_LEVEL` and the existing
`ARTICRAFT_*` aliases. Extra data-side provider adapters were not blindly overlaid;
this release retains OpenAI, Gemini, Anthropic and OpenRouter adapters.

`specific_editing` and `controlled_morphology` supply curated generator snapshots
and configuration-intervention experiments. They are retained separately from the
production generator inventory, and visual-only outputs are documented explicitly.
The `scripts/` directory retains offline material-preparation and research export
utilities needed by the existing regression suite. Some legacy research commands
require external material snapshots or Blender environments; they are not part of
the minimal sampling quickstart. The optional BlenderKit discovery downloader and
frozen-library builder were absent from both source workspaces and are not
fabricated in this repository. Tests for those external tools skip explicitly
when they are unavailable.

## Image-conditioned construction retained

The data workspace's picture bindings, category shard indexes, external image seed
creation, image inheritance on forks, Markdown image ingestion and picture doctor
are integrated with the template runtime. Provider-generated records also bind
canonical workspace images. Source import preserves bound reference images;
missing images are recorded without blocking legacy record import. See
[the full workflow](image_to_generator.md). Images and generated source records
remain data artifacts outside Git.

## What changed for RFW-A

- Added the `rfwa` distribution and CLI, with explicit construction, inspection,
  sampling, validation, release, source import and editing entry points.
- Aligned README and public documentation with source maps, category blueprints,
  reusable generators, procedural sampling and the paper's four authoring roles.
- Added a strict release adapter: all retained cases must pass, all declared
  choices need passing evidence, and source provenance must validate.
- Retained failed configurations across repair rounds; fixed random seeds alone
  are insufficient because a changed sampler can select a different configuration.
- Added seeded construction records, mechanical fingerprints, no-overwrite export
  checks and source-import file hashes.
- Preserved package import paths and old CLI for existing source programs, and
  preserved the original license/attribution rather than relabeling upstream work.

The historical authoring reference still describes the inherited development
checker, including tolerance-based statuses. `rfwa release --strict` provides optional formal certification; it does not accept those statuses as a substitute
for all-cases-pass evidence. Four-agent coordination is documented as an external
authoring workflow, not claimed as an implemented autonomous scheduler.

## Excluded artifacts

No source `.git` directory, virtualenv, `.env`, provider credentials, local logs,
material-library symlink, generated 400K asset tree, cache, or experiment render
directory is copied. Source-records and the frozen PBR library remain separate
data releases. The old Mars-rover presentation bundle, including generated images
and a zip archive, is not part of the generator runtime.

The original cross-simulator evaluation scripts and downstream training artifacts
are not present in these two codebases. Local mechanical validation and material
export must not be presented as reproduction of those paper experiments.

## Verification

Use `uv sync --locked --group dev`, `uv run pytest`, and `uv build` from this
checkout. The lockfile describes the new distribution, and fresh-environment
verification must not use an editable install of either original workspace.

`tests/known_failures.txt` is the inherited regression baseline; no new failures
are added to that list by migration. Some historical generator-specific tests
can expose existing geometry/SDK disagreements. The generator inventory is
therefore not pre-certified: inspect sampling success rates and per-asset results
when choosing a generator; use strict certification only when needed. Material-library integration tests skip
when the separately distributed library is absent; material-export unit tests use
small, complete frozen-library fixtures.
