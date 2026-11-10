# Source Status — pictureX / 0611 requested batch

Date: 2026-07-12

Requested subcategories:

- `pictureX/0611/Ice_crream_machine`
- `pictureX/0611/industrial_crane_featuring_advanced_hydraulic`
- `pictureX/0611/Industrial_rolling_work_table`
- `pictureX/0611/ironing_board2`
- `pictureX/0611/juicer_press_with_handle`
- `pictureX/0611/kitchen_cabinet`

Reference pipeline: `<ARTI_SKILL_ROOT>/造模板管线总览.md`

## Verdict

These six subcategories have passed both manual gates. The original workbench
assets were confirmed by the user on 2026-07-12, the minimum variant fork queue
was generated, all generated variants mechanically validate, and the confirmed
source pool has been synced into this downstream template repo as 5-star
workbench records.

Next pipeline stage: write formal modular specs and implement templates.

## Mechanical Check Executed

Command shape:

```text
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
uv run python -m cli.main compile \
  --repo-root <ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711 \
  <record_id> --target full --validate
```

Result: all 18 target records compiled and validated successfully.

| subcategory | records checked | compile failures | records with no warnings | records with allowed-overlap warnings |
|---|---:|---:|---:|---:|
| `Ice_crream_machine` | 4 | 0 | 2 | 2 |
| `industrial_crane_featuring_advanced_hydraulic` | 2 | 0 | 0 | 2 |
| `Industrial_rolling_work_table` | 4 | 0 | 1 | 3 |
| `ironing_board2` | 2 | 0 | 0 | 2 |
| `juicer_press_with_handle` | 1 | 0 | 0 | 1 |
| `kitchen_cabinet` | 5 | 0 | 5 | 0 |
| **total** | **18** | **0** | **8** | **10** |

The allowed-overlap warnings came from source-declared justifications. They do
not block the mechanical compile gate, but they should still be visually checked
at the manual asset review gate.

## Variant Expansion Executed

Source map:

`<ARTI_SKILL_ROOT>/articraft_data/picture_expansion/template_source_maps/0611__requested_batch_variant_source_map.md`

Generated records:

| subcategory | generated variants | independent validation |
|---|---|---|
| `Ice_crream_machine` | `rec_ice_crream_machine_var_open_churner_stand` | pass |
| `industrial_crane_featuring_advanced_hydraulic` | `rec_hydraulic_crane_var_foldable_legs`, `rec_hydraulic_crane_var_double_stage_boom`, `rec_hydraulic_crane_var_wide_gantry_base` | pass |
| `Industrial_rolling_work_table` | `rec_rolling_work_table_var_lower_shelf_handle` | pass |
| `ironing_board2` | `rec_ironing_board2_var_x_leg_articulated`, `rec_ironing_board2_var_tabletop_short_legs`, `rec_ironing_board2_var_rear_iron_rest` | pass |
| `juicer_press_with_handle` | `rec_juicer_press_var_arch_frame`, `rec_juicer_press_var_dual_post_frame`, `rec_juicer_press_var_screw_assist_ram`, `rec_juicer_press_var_bowl_strainer_n` | pass |
| `kitchen_cabinet` | none; existing pool already has five source anchors | existing records pass |

After `data reconcile`, each requested subcategory has five indexed workbench
records. `data/records_index.jsonl` was rebuilt with 198 records.

## High-Quality Sample Sync

Second manual gate was confirmed by user on 2026-07-12.

Sync command:

```text
uv run python scripts/sync_from_source.py \
  --source-repo <ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711 \
  --records <30 confirmed record ids> \
  --rating 5 --execute
```

Result:

- 30/30 confirmed records copied into `arti-template/data/records`.
- 30/30 materialization caches copied into `arti-template/data/cache/record_materialization`.
- 30/30 destination records stamped `rating=5`.
- Search index rebuilt: `records=14720`, `workbench_entries=3900`.

Viewer startup was attempted with:

```text
uv run python -m cli.main viewer \
  --repo-root <ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711 \
  --host 127.0.0.1 --port 8765 --target /viewer
```

It did not start because this environment does not have `npm`, which is required
to build/serve `viewer/web`. The compiled URDFs were still written under
`data/cache/record_materialization/<record_id>/model.urdf` for all 18 target
records.

## Current State By Subcategory

| subcategory | reference images | generated records | confirmed 5-star records | current pipeline state | next action |
|---|---:|---:|---:|---|---|
| `Ice_crream_machine` | 4 | 4 | 0 | generated workbench assets exist; blocked before high-quality sample sync | manual asset/variant review; add at least 1 more accepted sample |
| `industrial_crane_featuring_advanced_hydraulic` | 2 | 2 | 0 | generated workbench assets exist; blocked before high-quality sample sync | manual asset/variant review; generate/accept at least 3 more samples |
| `Industrial_rolling_work_table` | 4 | 4 | 0 | generated workbench assets exist; blocked before high-quality sample sync | manual asset/variant review; add at least 1 more accepted sample |
| `ironing_board2` | 2 | 2 | 0 | generated workbench assets exist; blocked before high-quality sample sync | manual asset/variant review; generate/accept at least 3 more samples |
| `juicer_press_with_handle` | 1 | 1 | 0 | generated workbench asset exists; blocked before high-quality sample sync | manual asset review; generate/accept at least 4 more samples |
| `kitchen_cabinet` | 5 | 5 | 0 | sample count is sufficient, but confirmation/rating gate is not passed | manual review, then sync/stamp accepted records as 5-star |

## Source Pool Inventory

### `Ice_crream_machine`

| record_id | picture | rating | parts | articulations | visuals | observed helper surface |
|---|---|---:|---:|---:|---:|---|
| `rec_picturex_0611__ice_crream_machine__004__png_ee7cae5d293b4afe8ff800e2b09be2f0` | `pictureX/0611/Ice_crream_machine/004.png` | null | 9 | 8 | 15 | `_make_chassis`, `_make_housing`, `_make_lid`, `_make_handwheel`, `_make_cutter` |
| `rec_picturex_0611__ice_crream_machine__001__png_f877360c62f94bcc849164b7930e8f80` | `pictureX/0611/Ice_crream_machine/001.png` | null | 11 | 8 | 34 | `_frustum_shell`, `_ring`, `_rounded_bored_box` |
| `rec_picturex_0611__ice_crream_machine__002__png_5ea881a7da9e4a00a7bf5d1390f2178c` | `pictureX/0611/Ice_crream_machine/002.png` | null | 9 | 8 | 13 | `_housing_shape`, `_bowl_shape`, `_crank_shape`, `_dasher_shape` |
| `rec_picturex_0611__ice_crream_machine__003__png_efc3f3416f3b42a9b21a9061d85e4469` | `pictureX/0611/Ice_crream_machine/003.png` | null | 8 | 6 | 10 | `_make_tub_shell`, `_make_lid`, `_make_support_frame`, `_make_crank` |

Potential structure vocabulary after review: cabinet/chassis form, tub/bowl
form, lid/hopper access, handwheel/crank, internal dasher/cutter, support frame.

### `industrial_crane_featuring_advanced_hydraulic`

| record_id | picture | rating | parts | articulations | visuals | observed helper surface |
|---|---|---:|---:|---:|---:|---|
| `rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__001__png_444a5d123e634bb9b31511c0750e8ee8` | `pictureX/0611/industrial_crane_featuring_advanced_hydraulic/001.png` | null | 10 | 8 | 42 | `_box_between`, `_add_caster` |
| `rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__002__png_a35c26c615b74db58b30348439b55d5d` | `pictureX/0611/industrial_crane_featuring_advanced_hydraulic/002.png` | null | 11 | 8 | 29 | `_box_between`, `_cylinder_between`, `_boom_tube_mesh`, `_cylinder_tube_mesh`, `_add_caster` |

Potential structure vocabulary after review: wheeled base, upright mast,
telescoping / pivoting boom, hydraulic cylinder, hook/load point, casters.

### `Industrial_rolling_work_table`

| record_id | picture | rating | parts | articulations | visuals | observed helper surface |
|---|---|---:|---:|---:|---:|---|
| `rec_picturex_0611__industrial_rolling_work_table__002__png_734e7a01404e4b83b5986c0a30093445` | `pictureX/0611/Industrial_rolling_work_table/002.png` | null | 9 | 8 | 5 | `_box`, `_cylinder`, `_bar_between`, `_perforated_upright` |
| `rec_picturex_0611__industrial_rolling_work_table__003__png_8d72ded99b91405e97f6507d3115c6b9` | `pictureX/0611/Industrial_rolling_work_table/003.png` | null | 7 | 3 | 23 | `_beam_origin`, `_wood_top_shape` |
| `rec_picturex_0611__industrial_rolling_work_table__004__png_d11cca56695549bb9bda9bfd813476e2` | `pictureX/0611/Industrial_rolling_work_table/004.png` | null | 7 | 5 | 4 | `_box`, `_cylinder` |
| `rec_picturex_0611__industrial_rolling_work_table__001__png_f858cd8fba4c466aa560b397ff1bf275` | `pictureX/0611/Industrial_rolling_work_table/001.png` | null | 4 | 6 | 23 | `_add_frame_geometry`, `_add_yoke_geometry`, `_add_brake_geometry` |

Potential structure vocabulary after review: worktop, rolling base/casters,
upright peg/perforated panel, lower shelf, brake/yoke details, handle/side rail.

### `ironing_board2`

| record_id | picture | rating | parts | articulations | visuals | observed helper surface |
|---|---|---:|---:|---:|---:|---|
| `rec_picturex_0611__ironing_board2__001__png_20c3543235f84c8c9cdc02c21fc7b567` | `pictureX/0611/ironing_board2/001.png` | null | 3 | 3 | 15 | `_capsule`, `_perforated_tray`, `_cover_pattern`, `_add_leg_frame`, `_add_lock_brace` |
| `rec_picturex_0611__ironing_board2__002__png_a42c994617f44685ada679afd555e0ef` | `pictureX/0611/ironing_board2/002.png` | null | 4 | 2 | 9 | `_slot_solid`, `_perforated_pan`, `_cylinder_between`, `_add_hinge_mount` |

Potential structure vocabulary after review: tapered ironing deck, perforated
pan/tray, fabric cover decoration, folding leg frame, hinge hardware, lock brace.

Note: an older confirmed `ironing_board` source map already exists for
`Textiles_Fabric / Ironing board`; reuse it only if this `ironing_board2`
subcategory is intentionally merged with that category.

### `juicer_press_with_handle`

| record_id | picture | rating | parts | articulations | visuals | observed helper surface |
|---|---|---:|---:|---:|---:|---|
| `rec_picturex_0611__juicer_press_with_handle__001__png_4f95d74d2d3847cd8bdb9c4751cc97b7` | `pictureX/0611/juicer_press_with_handle/001.png` | null | 7 | 6 | 15 | `_base_shell`, `_upper_crosshead`, `_cup_geometry`, `_strainer_shell_geometry`, `_perforated_strainer_plate`, `_ram_geometry`, `_lever_arm_geometry`, `_linkage_geometry` |

Potential structure vocabulary after review: base shell, uprights/crosshead,
cup/strainer, perforated plate, ram/plunger, long handle, linkage.

### `kitchen_cabinet`

| record_id | picture | rating | parts | articulations | visuals | observed helper surface |
|---|---|---:|---:|---:|---:|---|
| `rec_picturex_0611__kitchen_cabinet__003__png_bd4b17b1bb1d45059fc34b510868a618` | `pictureX/0611/kitchen_cabinet/003.png` | null | 6 | 5 | 2 | `_add_box`, `_add_cylinder`, `_add_shaker_door` |
| `rec_picturex_0611__kitchen_cabinet__002__png_241b2c4fbfaa407c837bd61a7fb1b21f` | `pictureX/0611/kitchen_cabinet/002.png` | null | 3 | 3 | 23 | `build_object_model` |
| `rec_picturex_0611__kitchen_cabinet__005__png_32d18ad6c4bc42d1850e18a6ce8fa5cb` | `pictureX/0611/kitchen_cabinet/005.png` | null | 4 | 4 | 17 | `_add_leg`, `_add_shaker_door` |
| `rec_picturex_0611__kitchen_cabinet__004__png_5a44a3fb595d482486a4d5792aac684a` | `pictureX/0611/kitchen_cabinet/004.png` | null | 3 | 2 | 21 | `build_object_model` |
| `rec_picturex_0611__kitchen_cabinet__001__png_5f29ccaadea944c09b6f9832561aa405` | `pictureX/0611/kitchen_cabinet/001.png` | null | 4 | 3 | 19 | `build_object_model` |

Potential structure vocabulary after review: cabinet carcass, shaker/flat doors,
hinged door leaves, drawers or panel fronts where source-backed, legs/toe-kick,
countertop/sink-like upper surface if present in accepted samples.

## Gate Checklist

- Reference images exist for every requested subcategory.
- Generated workbench records exist for every requested subcategory.
- All 18 requested records compile with `--target full --validate`.
- First manual gate was confirmed by user on 2026-07-12.
- Minimum variant fork queue was generated for underfilled classes.
- All 12 generated variants compile with `--target full --validate`.
- Each requested subcategory now has five indexed workbench records.
- Second manual gate was confirmed by user on 2026-07-12.
- Confirmed high-quality samples were synced downstream and stamped `rating=5`.
- Local viewer launch attempted, but blocked by missing `npm`.
- Formal modular specs are not written yet.
- Template implementations are not generated yet.

## Recommended Next Batch Actions

1. Preview the listed workbench records for each subcategory and mark accepted
   samples. Reject any asset with identity drift, floating parts, wrong joints,
   missing support, or bad category binding.
2. For subcategories with fewer than five accepted samples, generate targeted
   variants from accepted parents only. Keep each variant to one structural axis.
3. After acceptance, sync only accepted records into `arti-template` with rating
   5, then rebuild search.
4. Write one `specs_modular_v1/<slug>.md` per approved subcategory, using these
   record ids and exact `model.py` line spans.
5. Implement templates one at a time and run `template sweep-pipeline` before
   moving to the next category.
