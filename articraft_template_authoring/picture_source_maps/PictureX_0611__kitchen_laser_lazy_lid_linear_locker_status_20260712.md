# Source Status — pictureX / 0611 kitchen-laser-lazy-lid-linear-locker batch

Date: 2026-07-12

Requested subcategories:

- `pictureX/0611/Kitchen_set`
- `pictureX/0611/laser_level_tripod`
- `pictureX/0611/lazy_susan`
- `pictureX/0611/Lid_opener`
- `pictureX/0611/linear_bearing_slide_with_rail`
- `pictureX/0611/Locker_box`

Reference pipeline: `<ARTI_SKILL_ROOT>/造模板管线总览.md`

## Verdict

After user confirmation, the 10 original pictureX records were treated as
accepted parent/source assets and synced into `arti-template` as 5-star
workbench sources.

Variant expansion has also been executed in upstream `articraft_data`: 30 new
candidate records were generated and 30 / 30 passed full compile cleanly.
The user then confirmed the variant pool (`变体confirm`), so all 30 variant
records were synced into downstream `arti-template` as 5-star sources and the
search index was rebuilt.

Templates have been implemented for all 6 requested subcategories as
source-pool replay templates. Sweep-safe accepted sources were selected per
subcategory, non-fixed source joint limits are tightened to the authored rest
pose in the shared replay helper, and all 6 templates passed compile sweep on
seeds `0-5`.

## Executed Pipeline Step

Phase-zero state judgment and phase-one mechanical validation were executed on
2026-07-12.

Reference image validation: 10 / 10 PNG files opened successfully.

Command shape used for the compile pass:

```bash
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
uv run articraft compile <record_dir> \
  --repo-root <ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711 \
  --target full
```

Full compile result: 10 / 10 records passed cleanly (`status=success
failures=0 warnings=0 notes=0`). Materialized URDFs and compile reports were
written under:

`<ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711/data/cache/record_materialization/<record_id>/`

This completes the machine-checkable part of the current stage. Per the
pipeline, the batch now stops at the original-asset / variant human review gate:
compile success does not prove object identity, visual quality, or source-pool
coverage.

User confirmation received after this check. Follow-up actions executed:

- Synced the 10 confirmed parent/source records into downstream `arti-template`
  with `rating=5`.
- Rebuilt downstream search index:
  `data/cache/search_index.json` now reports `records=14668`, `categories=246`,
  `workbench_entries=3860`.
- Patched upstream generation compatibility for current CLI:
  `<ARTI_SKILL_ROOT>/articraft_data/scripts/run_picture_gpt55_batch.py`
  no longer passes removed `--collection`; `<ARTI_SKILL_ROOT>/articraft_data/agent/runner_cli.py`
  no longer passes removed `data_root`.
- Generated 30 additional candidate records in upstream `articraft_data`.
- Full compile rechecked every new candidate: 30 / 30 passed cleanly.
- User confirmed the variant pool (`变体confirm`).
- Synced the 30 confirmed variant records into downstream `arti-template` with
  `rating=5`.
- Rebuilt downstream search index:
  `data/cache/search_index.json` reports `records=14738`, `categories=246`,
  `workbench_entries=3930`.
- Authored source-replay modular specs under
  `articraft_template_authoring/specs_modular_v1/`.
- Implemented templates under `agent/templates/pictureX_0611_*.py`, registered
  them in `cli/template.py`, and added the shared helper
  `agent/templates/picturex_0611_source_replay.py`.
- Ran compile sweep for every requested template on seeds `0-5`; all passed.

Variant generation logs:

- `<ARTI_SKILL_ROOT>/articraft_data/logs/picturex_0611_confirmed_gap_variants_20260712/`
- `<ARTI_SKILL_ROOT>/articraft_data/logs/picturex_0611_confirmed_gap_variants_20260712_singletons/`
- `<ARTI_SKILL_ROOT>/articraft_data/logs/picturex_0611_confirmed_gap_variants_20260712_doubletons/`

## Current State By Subcategory

| subcategory | reference images | generated records | confirmed 5-star records | current pipeline state | next action |
|---|---:|---:|---:|---|---|
| `Kitchen_set` | 3 | 3 | 6 synced | template implemented; sweep-safe source pool has 2 records; compile sweep 6/6 passed | complete |
| `laser_level_tripod` | 1 | 1 | 6 synced | template implemented; sweep-safe source pool has 2 records; compile sweep 6/6 passed | complete |
| `lazy_susan` | 2 | 2 | 8 synced | template implemented; sweep-safe source pool has 3 records; compile sweep 6/6 passed | complete |
| `Lid_opener` | 1 | 1 | 6 synced | template implemented; sweep-safe source pool has 4 records; compile sweep 6/6 passed | complete |
| `linear_bearing_slide_with_rail` | 2 | 2 | 8 synced | template implemented; sweep-safe source pool has 5 records; compile sweep 6/6 passed | complete |
| `Locker_box` | 1 | 1 | 6 synced | template implemented; sweep-safe source pool has 3 records; compile sweep 6/6 passed | complete |

## Variant Candidate Inventory

These candidates were machine-clean and then human-confirmed by
`变体confirm`; they have been synced as downstream 5-star sources.

### `Kitchen_set`

- `rec_use-the-attached-reference-image-as-the-primary-_20260712_091336_287900_df1e5b6c`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_092024_594506_750f090f`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_092024_589424_a073119f`

### `Lid_opener`

- `rec_use-the-attached-reference-image-as-the-primary-_20260712_092525_105360_45e44262`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_094150_036146_45e44262`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_094150_039038_45e44262`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_094513_583310_45e44262`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_094845_264861_45e44262`

### `Locker_box`

- `rec_use-the-attached-reference-image-as-the-primary-_20260712_092616_643603_0832e6dc`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_094918_538851_0832e6dc`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_095210_303286_0832e6dc`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_095217_763786_0832e6dc`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_095547_901965_0832e6dc`

### `laser_level_tripod`

- `rec_use-the-attached-reference-image-as-the-primary-_20260712_092909_380738_82e48964`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_095712_384185_82e48964`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_095851_476796_82e48964`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_100114_495054_82e48964`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_100144_545039_82e48964`

### `lazy_susan`

- `rec_use-the-attached-reference-image-as-the-primary-_20260712_093026_380093_a4b69753`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_093216_489164_9abfe7cb`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_100645_100347_a4b69753`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_100645_100756_a4b69753`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_100932_868786_9abfe7cb`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_100941_355392_9abfe7cb`

### `linear_bearing_slide_with_rail`

- `rec_use-the-attached-reference-image-as-the-primary-_20260712_093250_195206_83d08292`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_093549_584407_4387eb47`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_101211_883498_83d08292`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_101220_741681_83d08292`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_101504_669150_4387eb47`
- `rec_use-the-attached-reference-image-as-the-primary-_20260712_101508_609061_4387eb47`

## Source Pool Inventory

### `Kitchen_set`

| record_id | picture | rating | parts | articulations | visuals | observed helper surface |
|---|---|---:|---:|---:|---:|---|
| `rec_picturex_0611__kitchen_set__001__png_c1970d9ce2634508b40ad70a6dbcea9d` | `pictureX/0611/Kitchen_set/001.png` | null | 8 | 6 | 5 | `_box`, `_make_hinged_panel`, `_make_oven_door` |
| `rec_picturex_0611__kitchen_set__002__png_f3297107e4784723b3e657e0f26ed27f` | `pictureX/0611/Kitchen_set/002.png` | null | 6 | 4 | 17 | `_countertop_mesh`, `_sink_basin_mesh`, `_sink_rim_mesh` |
| `rec_picturex_0611__kitchen_set__003__png_13615c53ca2c41eca2c6416dfaa3996d` | `pictureX/0611/Kitchen_set/003.png` | null | 6 | 4 | 13 | `_add_island_drawer`, `_add_slab_door`, `_box`, `_countertop_shape` |

Potential structure vocabulary after review: cabinet carcass or island body,
countertop, sink basin/rim, hinged lower panels, oven door, drawers, slab or
shaker fronts.

### `laser_level_tripod`

| record_id | picture | rating | parts | articulations | visuals | observed helper surface |
|---|---|---:|---:|---:|---:|---|
| `rec_picturex_0611__laser_level_tripod__001__png_42c26bf6cf4f4e838a5d8a4cdf4b502d` | `pictureX/0611/laser_level_tripod/001.png` | null | 12 | 10 | 34 | `_aabb_center`, `_add_member`, `_distance`, `_leg_frame_point`, `_midpoint`, `_rectangular_ring`, `_rectangular_tube`, `_rpy_for_z_member` |

Potential structure vocabulary after review: three folding tripod legs,
telescoping or braced members, central mast, laser level head, mounting ring,
leg pivots and spreader braces.

### `lazy_susan`

| record_id | picture | rating | parts | articulations | visuals | observed helper surface |
|---|---|---:|---:|---:|---:|---|
| `rec_picturex_0611__lazy_susan__001__png_84d342859ad6436ebbd9b2e40cd55644` | `pictureX/0611/lazy_susan/001.png` | null | 4 | 2 | 8 | `_add_surface_line` |
| `rec_picturex_0611__lazy_susan__002__png_34d73e1312d84c3a872e9ce87f698a3a` | `pictureX/0611/lazy_susan/002.png` | null | 4 | 2 | 9 | `_marble_disk_shape`, `_pedestal_shape`, `_tabletop_shape`, `_vein_shape` |

Potential structure vocabulary after review: fixed base or pedestal, rotating
top disk/tabletop, bearing seam, rim or surface line detail, marble/wood visual
treatment. Note: this is a pictureX-specific source pool; existing generic
`lazy_susan` dataset records in `data/records` should not be treated as
confirmed pictureX sources unless the categories are intentionally merged.

### `Lid_opener`

| record_id | picture | rating | parts | articulations | visuals | observed helper surface |
|---|---|---:|---:|---:|---:|---|
| `rec_picturex_0611__lid_opener__001__png_3629ffb09bed420e8847dce28465922d` | `pictureX/0611/Lid_opener/001.png` | null | 10 | 8 | 16 | `_annular_eye`, `_curvature`, `_handle_loft`, `_mesh`, `_plate` |

Potential structure vocabulary after review: curved handle, annular gripping
eye, toothed or serrated contact pads, squeeze/lever arms, hinge or pivot
hardware, jar-lid capture geometry.

### `linear_bearing_slide_with_rail`

| record_id | picture | rating | parts | articulations | visuals | observed helper surface |
|---|---|---:|---:|---:|---:|---|
| `rec_picturex_0611__linear_bearing_slide_with_rail__001__png_9c9598a488404d7a805a4da0e5dd43ff` | `pictureX/0611/linear_bearing_slide_with_rail/001.png` | null | 4 | 2 | 6 | `_carriage_body_shape`, `_end_seal_shape`, `_rail_shape` |
| `rec_picturex_0611__linear_bearing_slide_with_rail__002__png_190bfa58cf1f4780a07ddd430375802b` | `pictureX/0611/linear_bearing_slide_with_rail/002.png` | null | 4 | 2 | 6 | `_add_carriage_visuals`, `_carriage_body_shape`, `_seal_shape`, `_support_frame_shape` |

Potential structure vocabulary after review: straight rail, sliding carriage,
end seals, mounting holes or screw blocks, support frame, single prismatic
travel axis with retained carriage overlap.

### `Locker_box`

| record_id | picture | rating | parts | articulations | visuals | observed helper surface |
|---|---|---:|---:|---:|---:|---|
| `rec_picturex_0611__locker_box__001__png_530198ce33344903b0ba8c8e5a959124` | `pictureX/0611/Locker_box/001.png` | null | 8 | 6 | 21 | `_cylinder_along_y` |

Potential structure vocabulary after review: box carcass, hinged lid or door,
hasp/lock plate, handle or latch cylinder, internal tray/panel if present,
capture/hinge support details.

## Gate Checklist

- Reference images exist for every requested subcategory.
- Reference images are readable PNG files.
- Generated workbench/export records exist for every requested subcategory.
- Full compile passed cleanly for every generated record.
- Original 10 records are manually confirmed by user and synced as rating-5
  downstream sources.
- Each subcategory now has at least six machine-clean candidates including the
  confirmed parents.
- Variant pool confirmed by user and synced as rating-5 downstream sources.
- Sweep-safe source pools selected for all 6 source-replay templates.
- Modular specs written for all 6 requested subcategories.
- Template registry entries added for all 6 requested subcategories.
- Compile sweep passed for all 6 templates on seeds `0-5`.

## Recommended Next Batch Actions

1. If these source-replay templates are later upgraded to hand-authored
   parametric CAD, use the synced 5-star records and the current specs as the
   approved source pool.
2. For release validation beyond this execution pass, run broader sweeps such
   as `--seeds 0-31` per slug.
3. Keep records excluded from the template source pool out of sweep sampling
   unless their stricter articulation-origin or motion-QC issues are repaired.
