# Sampling, material grounding and directed editing

**Default policy:** prioritize usable output. Checks use a configurable 90%
sampled pass-rate threshold. Sampling exports passing assets and logs/skips failed
seeds; a mixed batch returns `partial` and succeeds if it produces any valid assets.
Legacy blueprint/source gaps and corner failures are diagnostics, not default
category-wide blockers. Add `--strict` to `check` or `release` only when you want
all-cases-pass and complete coverage/provenance. The stricter requirements described
below refer to that optional mode.


Run commands from an installed source checkout (`uv sync --group dev`). Python
3.11 and 3.12 are supported. `uv run rfwa --help` lists the RFW-A commands;
`uv run articraft --help` exposes inherited source-record tools.

## Deterministic sampling

```bash
uv run rfwa generators
uv run rfwa inspect single_revolute_hinge
uv run rfwa config single_revolute_hinge --seed 0
uv run rfwa sample single_revolute_hinge --seeds 0-2,10 --out /tmp/rfwa-samples
```

The basic sample path runs author tests, SDK validation and sampled joint-motion
checks. Passing artifacts are under `seed_<n>/` with `model.urdf`, `model.py`,
mesh assets and `artifact.json`; `sampling.json` records resolved configurations,
mechanical-code fingerprint and per-seed diagnostics. Failed seeds are reported and skipped. A batch returns a nonzero exit status
when it produces no passing assets. Do not reuse an output directory containing a
previous run. No API key is needed.

The generator inventory includes legacy categories and source-derived names.
Use the exact listed ID; readable category labels do not replace stable IDs in
reproduction records. A seed is reproducible with the same generator, SDK and
dependency versions. Preserve the environment lockfile with exported datasets.

## Frozen materials and physical annotations

```bash
uv run rfwa sample <generator> --seeds 0-2 --out /tmp/rfwa-grounded \
  --library-pointer /path/to/pbr_library/unified/latest.json
```

Supply the library snapshot referenced by the pointer, including its pool index,
catalog, material metadata and textures. Mechanical checks precede export.
The material path selects a pool by each surface's `material_class_id`, draws a
member with a local seeded RNG, and binds that member's appearance and six
physical-property fields together. `--material-seed` controls the draw independently
of geometry; by default it follows the asset seed.

This export uses `<generator>/seed_<n>/` containing `model.urdf`, portable meshes,
textures, `appearance.json` and `physics.json`. The metadata retains library and
generator hashes. It preserves authored link mass/inertia; it does not compute
new inertias from the estimated density. A generator needs complete surface
annotations. Missing libraries, pool members or class assignments are reported per
seed in `sampling.json`. Passing exports are retained; a material-export failure
does not discard other valid assets in the batch.

## Directed editing

```bash
uv run rfwa edit --list-generators
uv run rfwa edit --describe-generator cabinet
uv run rfwa edit --spec specific_editing/specs/single_variable/cabinet_paper_showcase.json --dry-run
```

Use a spec from `specific_editing/specs/single_variable/`, then pass
`--out /tmp/rfwa-edits` to build and render. Inspect its `generator` and render
settings before execution. Available IDs and actual spec filenames can be listed
with the commands above and `ls specific_editing/specs/single_variable`.

Component, count, material and dimensional edits rebuild from configuration and
resolve dependent construction parameters. The curated editing snapshots are
separate from production generators. The editing renderer exports **visual-only**
URDF/GLB comparisons; those are not physics-ready sample exports. It writes this
boundary explicitly in `exports.json`. Material themes require the separate
material library. Blender can be selected through `SPECIFIC_EDITING_BLENDER`;
the software backend is a lightweight preview.

See [the inherited editing reference](../specific_editing/README.md) for the full
spec contract, target selectors and output layout. `controlled_morphology/`
provides additional cabinet parameter-intervention experiments.
