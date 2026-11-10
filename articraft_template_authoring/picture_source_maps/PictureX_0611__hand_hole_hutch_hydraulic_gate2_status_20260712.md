# Source Status - pictureX / 0611 hand-hole-hutch-hydraulic gate 2

Date: 2026-07-12

## INVALIDATED 2026-07-13

This gate-2 status is void. The listed 19 records were local wrapper-generated
forks, not internal `articraft fork` variants, so they do not satisfy the
UPSTREAM variant-fork requirement in
`<ARTI_SKILL_ROOT>/.agents/skills/build-template/SKILL.md`,
`FORK_VARIANTS.md`, or `VARIANT_PIPELINE.md`.

The records have been quarantined out of `workbench` as `invalid_local_fork`,
and the source repo has been reconciled. Current valid workbench counts are:

| subcategory | valid current anchors | required minimum | missing internal-fork anchors |
|---|---:|---:|---:|
| `Hand-crank_clothes_wringer` | 1 | 8 | 7 |
| `Hole_punch` | 2 | 8 | 6 |
| `Hutch_Cabinet` | 1 | 8 | 7 |
| `hydraulic_jack` | 2 | 8 | 6 |
| `hydraulic_jack1` | 2 | 8 | 6 |
| `hydraulic_jack2` | 1 | 8 | 7 |

Current correction report:

`<ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711/picture_expansion/variant_count_correction_20260713.md`

Reference pipeline: `<ARTI_SKILL_ROOT>/造模板管线总览.md`

Input gate: user confirmed original assets after gate-1 report.

## Verdict

Stage two has been executed and this batch is now stopped at the second hard
gate: variant-pool human review.

No high-quality sample sync, modular spec finalization, or final template
acceptance should happen until this second gate is confirmed.

## Variant Generation

Created 19 local workbench fork records in the source repo:

- `Hand-crank_clothes_wringer`: 3 forks
- `Hole_punch`: 4 forks
- `Hutch_Cabinet`: 3 forks
- `hydraulic_jack`: 3 forks
- `hydraulic_jack1`: 3 forks
- `hydraulic_jack2`: 3 forks

Generation script:

`<ARTI_SKILL_ROOT>/arti-template/scripts/create_picturex_0611_gate2_variants.py`

Source map:

`<ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711/picture_expansion/template_source_maps/0611__hand_hole_hutch_hydraulic_requested.md`

## Mechanical Validation

Command shape:

```text
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
uv run articraft compile --repo-root <source_repo> <record_id> --target visual --validate
```

Result: 19/19 fork variants passed visual validation and then full validation
with `failures=0`, `warnings=0`.

## Reconcile

Executed:

```text
uv run python -m cli.main data reconcile \
  --repo-root <ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711 \
  --with-records-index
```

Indexed totals after reconcile:

| subcategory | indexed workbench records |
|---|---:|
| `Hand-crank_clothes_wringer` | 4 |
| `Hole_punch` | 6 |
| `Hutch_Cabinet` | 4 |
| `hydraulic_jack` | 5 |
| `hydraulic_jack1` | 5 |
| `hydraulic_jack2` | 4 |

## Gate Requirement

Human review should inspect the mixed original/fork pools for:

- class identity and no neighbor-category drift;
- one-axis-only intent for each fork;
- correct mechanisms and visible support paths;
- acceptable hydraulic-table compatibility probes;
- adequate structural vocabulary for downstream specs.

Only after this gate is confirmed should the pipeline proceed to high-quality
sample sync and modular specs.
