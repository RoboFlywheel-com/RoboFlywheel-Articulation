# Source Status - pictureX / 0611 hand-hole-hutch-hydraulic batch

Date: 2026-07-12

Reference pipeline: `<ARTI_SKILL_ROOT>/造模板管线总览.md`

Requested subcategories:

- `pictureX/0611/Hand-crank_clothes_wringer`
- `pictureX/0611/Hole_punch`
- `pictureX/0611/Hutch_Cabinet`
- `pictureX/0611/hydraulic_jack`
- `pictureX/0611/hydraulic_jack1`
- `pictureX/0611/hydraulic_jack2`

## Verdict

Do not advance this batch to variant expansion, high-quality sync, modular spec,
or template acceptance yet.

The no-skip state machine places all six requested subcategories at the first
hard stop: original workbench assets exist, are bound to the requested picture
subcategory, and now compile with no blocking QC failures, but there is no
located human confirmation for the original-asset visual identity gate.

Existing downstream specs/templates/reports for these slugs are therefore
provisional only and must not be treated as final pipeline completion until both
manual gates and source organization are completed in order.

## Stage Zero - State Check

Reference records were located under:

`<ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711`

The target picture paths are indexed as workbench records in
`data/records_index.selected.jsonl`; all have `collections=["workbench"]`,
`run_status="success"`, and `has_compile_report=true`.

No batch-specific confirmation file was found for these six requested
subcategories. A legacy `Workspace / Hole punch` source map exists, but it is a
different category lineage and does not by itself confirm
`pictureX/0611/Hole_punch`.

## Stage One - Original Asset Mechanical Check

Command shape:

```text
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
uv run python -m cli.main compile \
  --repo-root <ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711 \
  <record_id> --target full --validate
```

Result: 9/9 original workbench records compile with `failures=0`.

| subcategory | record_id | result | notes |
|---|---|---|---|
| `Hand-crank_clothes_wringer` | `rec_picturex_0611__hand_crank_clothes_wringer__001__png_528e7f40341c4a72899b19b423e8248b` | pass | allowed overlap notes only |
| `Hole_punch` | `rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d` | pass with warning | fixed blocking joint-origin QC; remaining warning is disconnected datum geometry |
| `Hole_punch` | `rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff` | pass with warning | fixed blocking joint-origin QC; remaining warning is disconnected central bushing geometry |
| `Hutch_Cabinet` | `rec_picturex_0611__hutch_cabinet__001__png_06992399ece7490a91f934345df0f0ba` | pass | clean |
| `hydraulic_jack` | `rec_picturex_0611__hydraulic_jack__001__png_af55d19fd79043eeaaa91f76169ade14` | pass | allowed overlap notes only |
| `hydraulic_jack` | `rec_picturex_0611__hydraulic_jack__002__png_53523a539a204bcf896a11590eedafae` | pass | allowed overlap notes only |
| `hydraulic_jack1` | `rec_picturex_0611__hydraulic_jack1__001__png_fe4f01a5f14542c8ac8e1e3e53fb8613` | pass | allowed overlap notes only |
| `hydraulic_jack1` | `rec_picturex_0611__hydraulic_jack1__002__png_343b03cbe8414658969055f2ca9c7a13` | pass | allowed overlap notes only |
| `hydraulic_jack2` | `rec_picturex_0611__hydraulic_jack2__001__png_1e3d36c9f6f846b59e6a82e93b80e5e0` | pass with warning | fixed blocking cylinder-mount QC; remaining warning is disconnected datum geometry |

## Repairs Applied During Stage One

Three records initially had blocking QC failures despite the historical
`has_compile_report` flag:

- `Hole_punch/001`: fixed fixed-joint origin proximity for head, die, guide rail,
  and pivot axle by adding small assembly datum geometry without changing the
  authored object pose.
- `Hole_punch/002`: fixed pivot axle origin proximity by adding a central pivot
  bushing, then scoped the intentional axle/bushing capture overlap.
- `hydraulic_jack2/001`: fixed hydraulic cylinder fixed-mount origin proximity
  by adding a small cylinder mount datum, then scoped the intentional datum
  overlap.

Changed source files:

- `data/records/rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d/revisions/rev_000001/model.py`
- `data/records/rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff/revisions/rev_000001/model.py`
- `data/records/rec_picturex_0611__hydraulic_jack2__001__png_1e3d36c9f6f846b59e6a82e93b80e5e0/revisions/rev_000001/model.py`

## Hard Stop - Original Asset Review

Pipeline rule: all target original assets must stop here for human visual
review. Mechanical compile can confirm buildability and binding, but it cannot
confirm whether the model visually reads as the requested object.

Human review should check:

- target identity matches the picture subcategory;
- category binding is correct;
- no obvious floating parts, severe penetration, wrong support path, or wrong
  joint semantics;
- allowed overlap notes are visually acceptable;
- the three records with disconnected-datum warnings do not show visible
  artifacts from the small datum geometry.

## Next Action After Human Confirmation

Only after this first gate is explicitly confirmed:

1. write a variant plan per subcategory;
2. generate targeted variants from confirmed parents only;
3. rebuild indexes and validate variants;
4. stop again at the second human variant-pool gate;
5. sync only accepted high-quality samples downstream;
6. then write specs and accept templates.
