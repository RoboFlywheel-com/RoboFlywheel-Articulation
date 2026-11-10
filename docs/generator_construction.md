# Constructing a category-level generator

**Default policy:** prioritize usable output. Checks use a configurable 90%
sampled pass-rate threshold. Sampling exports passing assets and logs/skips failed
seeds; a mixed batch returns `partial` and succeeds if it produces any valid assets.
Legacy blueprint/source gaps and corner failures are diagnostics, not default
category-wide blockers. Add `--strict` to `check` or `release` only when you want
all-cases-pass and complete coverage/provenance. The stricter requirements described
below refer to that optional mode.


Read the [paper-to-code mapping](architecture.md) first. The primary RFW-A
workflow is source components → category blueprint → executable generator →
validation/repair → procedural sampling.

从图片持续扩展新类别，参阅 [完整图像到 generator 流程](image_to_generator.md)。

## 1. Prepare source programs

Existing Articraft-format records can be imported without rewriting their ratings
or revision history:

```bash
uv run rfwa import-source --from-repo /path/to/source-checkout rec_example
```

This copies the record and its assets into `data/records/`, retains metadata,
and writes file hashes under `data/source_imports/`. It refuses existing targets
and symlinks. It does not copy caches, private environment files or dataset-wide
indexes. The original source checkout is unchanged. Source records and generated
artifacts are excluded from Git; distribute data separately.

For source-asset synthesis, configure the desired provider in `.env` (start from
`.env.example`) and use `uv run rfwa source generate --help`. The inherited source
workflow is per-asset synthesis; it is an input to RFW-A generator construction.
If an external agent is creating source records, follow
[`EXTERNAL_AGENT_DATA.md`](../EXTERNAL_AGENT_DATA.md) through
`rfwa source external ...`.

## 2. Source Agent: identify reusable components

```bash
uv run rfwa author source-map-init my_category \
  --records-root data/records \
  --picture-category '<source category>' \
  --picture-subcategory '<source subcategory>'
uv run rfwa author source-map-check \
  --source-map articraft_template_authoring/source_maps/my_category.md \
  --records-root data/records
```

Initialization creates a scaffold, not an approved map. Review every discovered
source and fill in useful candidates with exact code spans and structural/motion
evidence. [Source role](roles/source.md).

## 3. Architect Agent: specify the category blueprint

```bash
uv run rfwa author design-init my_category \
  --source-map articraft_template_authoring/source_maps/my_category.md \
  --records-root data/records
```

Fill in `articraft_template_authoring/designs/my_category.json`: component
alternatives, free and derived parameters, interfaces, repetition, attachment and
joint rules. Keep source paths relative to the checkout when sharing a blueprint.
The source collection must be present to validate provenance.
[Architect role](roles/architect.md).

## 4. Code Agent: implement a self-contained generator

Create `agent/templates/my_category.py` and register its function stem in
`agent/template_registry.py`. Expose `config_from_seed(seed)`,
`build_<stem>(config, assets=...)`, `run_<stem>_tests(model, config)`, and
`TEMPLATE_DOMAIN`; provide `resolve_config` for dependent parameters and
`TEMPLATE_CORNERS` for boundaries and coupled risks. Construction uses the SDK
and the extracted component logic, without importing source-record programs at
sampling time. [Code role](roles/code.md).

Detailed schema and mechanical conventions remain in the inherited
[`AUTHORING.md`](../articraft_template_authoring/AUTHORING.md). Its legacy
tolerance-based completion terminology applies to development tools; the
RFW-A release requirements below take precedence for a release decision.

## 5. Revision Module and Repair Agent

```bash
uv run rfwa check my_category --stage random-16
uv run rfwa check my_category --stage random-36
uv run rfwa release my_category
```

Inspect `.artifacts/rfwa/my_category/` for stage reports, failing configurations,
responsible functions, parts/joints and measurements. Repair the blueprint when
the construction rule is wrong; otherwise repair the generator. Rerun using the
same state directory. [Repair role](roles/repair.md).

Optional `release --strict` requires passing preflight and source provenance, all 36 fixed random
seeds, every corner/regression case, motion coverage, and passing evidence for
every declared domain choice. Missing source records, uncovered choices and
legacy `strict_ready_with_tolerance` are not accepted. Bundled historical designs
and programs are migration inputs, not pre-issued release certificates.

For ordinary generation, a practical readiness report is enough. For optional
formal certification add `--strict`. Then use `rfwa sample my_category --seeds 100-199 --out /tmp/my_category`.
