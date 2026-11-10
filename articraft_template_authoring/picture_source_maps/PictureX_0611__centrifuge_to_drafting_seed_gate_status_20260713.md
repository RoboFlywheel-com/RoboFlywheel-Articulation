# pictureX/0611 centrifuge-to-drafting seed gate status

Date: 2026-07-13

Pipeline reference:

- `<ARTI_SKILL_ROOT>/造模板管线总览.md`
- `<ARTI_SKILL_ROOT>/.agents/skills/build-template/SKILL.md`

## Scope

- `pictureX/0611/centrifuge_machine2`
- `pictureX/0611/Chain_separator`
- `pictureX/0611/compass`
- `pictureX/0611/crimping_tool`
- `pictureX/0611/Desk_with_drawers（no_door）`
- `pictureX/0611/drafting_table_with_adjustable_tilt_surface`

## Phase detection

All six subcategories already have valid reference images and explicitly bound original
workbench assets. No source map, converged variant pool, downstream modular spec, template,
or sweep-pass state exists for any of the six categories.

The batch is therefore at the first hard stop: **original asset review**. Variant generation,
5-star downstream sync, spec authoring, and template implementation must not start until the
user confirms the original assets after visual inspection.

## Mechanical gate

The 17 bound original records were checked with the thread-capped command shape:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 \
  uv run articraft compile --target full --validate --strict-geom-qc \
  data/records/<record_id>
```

Results:

| subcategory | originals | compile success | non-fixed joints per asset | binding | collection |
| --- | ---: | ---: | --- | --- | --- |
| `centrifuge_machine2` | 2 | 2/2 | 7, 8 | explicit / correct | workbench only |
| `Chain_separator` | 1 | 1/1 | 3 | explicit / correct | workbench only |
| `compass` | 1 | 1/1 | 4 | explicit / correct | workbench only |
| `crimping_tool` | 3 | 3/3 | 5, 4, 4 | explicit / correct | workbench only |
| `Desk_with_drawers（no_door）` | 5 | 5/5 | 15, 5, 4, 4, 4 | explicit / correct | workbench only |
| `drafting_table_with_adjustable_tilt_surface` | 5 | 5/5 | 6, 9, 8, 6, 7 | explicit / correct | workbench only |
| **total** | **17** | **17/17** | **all articulated** | **17/17** | **17/17** |

All 17 reference PNGs are readable. Every target record has a `picture.json` sidecar with
`source=explicit`, points to the requested `0611/<subcategory>` folder, appears in its
per-subcategory shard, and is present in `data/records_index.jsonl`.

The global read-only `picture_doctor` found no broken folder or image pointers. It did report
one unrelated pre-existing unbound workbench record, `rec_harvester_var_head_log_grapple`;
that record is outside this batch and does not affect the six target subcategories.

## Visual review risks

The following non-blocking compile evidence needs human judgment at this gate:

- Both `centrifuge_machine2` originals follow the pictures as exposed hand-crank laboratory
  centrifuges. Their own tests flag a possible mismatch with an enclosed powered-machine
  interpretation of the subcategory name.
- `Chain_separator/001.png` compiles, but strict geometry QC reports three isolated moving
  parts under explicit allowances: `driver_carriage`, `spindle_hub`, and `t_bar`. Inspect the
  screw/carriage capture and T-bar support carefully before accepting the parent.
- `Desk_with_drawers（no_door）/001.png` is modeled as the pictured antique roll-top writing
  desk with tambour hood rather than a generic open desk. Confirm that this form belongs in
  the intended template family.
- `drafting_table_with_adjustable_tilt_surface/001.png` is a portable tabletop drafting board
  with a folding tilt stand. Confirm that it should remain in the same family as the other
  adjustable drafting tables.
- The drafting-table sources include several source-declared captured-joint/contact overlaps.
  These passed strict geometry QC under justification, but their closed poses and motion paths
  still require visual inspection.

## Review filter and next action

In the upstream workbench, inspect these six exact subcategory filters under category `0611`.
Approve or reject individual originals, especially the four risk groups above.

After explicit original-asset confirmation, the next permitted segment is upstream variant
planning and forking: write one source map per subcategory, account for every original, fork
only missing structural anchors from original parents, reconcile/validate the variant pool,
and stop again at the variant-review gate before any downstream spec or template work.
