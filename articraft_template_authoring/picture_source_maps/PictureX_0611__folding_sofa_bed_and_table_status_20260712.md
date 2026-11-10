# Source Status — pictureX / 0611 folding sofa beds and folding tables

Date: 2026-07-12

Requested subcategories:

- `pictureX/0611/Folding_sofa_bed1`
- `pictureX/0611/Folding_sofa_bed2`
- `pictureX/0611/Folding_sofa_bed3`
- `pictureX/0611/Folding_table`
- `pictureX/0611/Folding_table1`
- `pictureX/0611/Folding_table2`

Reference pipeline: `<ARTI_SKILL_ROOT>/造模板管线总览.md`

## Verdict

These six subcategories have completed the upstream machine gate for the
current requested batch and are now at the variant inspection hard stop.

Execution update: the original 12 inspected generated records compiled
successfully with `uv run articraft compile --repo-root ... --target full
--validate`. After manual confirmation (`all confirm`), 18 single-axis variants
were forked from the confirmed origins. All 18 variant forks exited successfully,
the package indexes were reconciled with `--with-records-index`, and every new
variant passed full compile validation with at least one non-fixed joint while
remaining `collections: ['workbench']`.

They are still workbench-only records with `rating: null`. They have not yet
passed the manual variant-pool confirmation / 5-star source gate required before
high-quality sample sync.

Do not stamp these records as 5-star or sync them into the downstream template
source pool until manual review confirms the assets and any missing structural
variants are generated.

## Current State By Subcategory

| subcategory | generated records | confirmed 5-star records | current pipeline state | next action |
|---|---:|---:|---|---|
| `Folding_sofa_bed1` | 6 | 0 | source map written; all machine checks pass; blocked at variant inspection gate | inspect variant pool in viewer, then confirm accepted variants |
| `Folding_sofa_bed2` | 5 | 0 | source map written; all machine checks pass; blocked at variant inspection gate | inspect variant pool in viewer, then confirm accepted variants |
| `Folding_sofa_bed3` | 5 | 0 | source map written; all machine checks pass; blocked at variant inspection gate | inspect variant pool in viewer, then confirm accepted variants |
| `Folding_table` | 5 | 0 | source map written; all machine checks pass; blocked at variant inspection gate | inspect variant pool in viewer, then confirm accepted variants |
| `Folding_table1` | 5 | 0 | source map written; all machine checks pass; blocked at variant inspection gate | inspect variant pool in viewer, then confirm accepted variants |
| `Folding_table2` | 5 | 0 | source map written; all machine checks pass; blocked at variant inspection gate | inspect variant pool in viewer, then confirm accepted variants |

## Source Pool Inventory

### `Folding_sofa_bed1`

| record_id | picture | rating | collections | observed helper surface |
|---|---|---:|---|---|
| `rec_picturex_0611__folding_sofa_bed1__002__png_f3a7fcc7d38c4e7d8d79ea405442889c` | `pictureX/0611/Folding_sofa_bed1/002.png` | null | `['workbench']` | `_rounded_box`, `_side_panel_shape`, `build_object_model`, `_material_name` |
| `rec_picturex_0611__folding_sofa_bed1__003__png_rerun_ef2699b37030410e922caf5507d1190e` | `pictureX/0611/Folding_sofa_bed1/003.png` | null | `['workbench']` | `_rounded_box`, `_box`, `_union`, `_square_sleeve`, `_section_frame`, `_add_bed_section`, `_u_leg`, `build_object_model` |

Potential structure vocabulary after review: convertible sofa/bed panels, padded
seat and back sections, fold-out sleeping deck, side panels/arms, support legs,
hinge or sliding conversion hardware.

### `Folding_sofa_bed2`

| record_id | picture | rating | collections | observed helper surface |
|---|---|---:|---|---|
| `rec_picturex_0611__folding_sofa_bed2__001__png_bc9181ca88b34f609f35ca0b26987e36` | `pictureX/0611/Folding_sofa_bed2/001.png` | null | `['workbench']` | `_rounded_box`, `_add_rod_between`, `build_object_model` |

Potential structure vocabulary after review: sofa frame, hinged back/seat,
folding mattress panel, visible support rods, side arm supports.

### `Folding_sofa_bed3`

| record_id | picture | rating | collections | observed helper surface |
|---|---|---:|---|---|
| `rec_picturex_0611__folding_sofa_bed3__001__png_681510f392e64b02aa2e69f4fa42da4b` | `pictureX/0611/Folding_sofa_bed3/001.png` | null | `['workbench']` | `_rounded_box_mesh`, `_add_x_cylinder`, `build_object_model` |

Potential structure vocabulary after review: padded sofa base, backrest-to-bed
folding motion, tubular X support, mattress panels, exposed folding linkage.

### `Folding_table`

| record_id | picture | rating | collections | observed helper surface |
|---|---|---:|---|---|
| `rec_picturex_0611__folding_table__001__png_4c4c814847524e32a28ec810e398ef86` | `pictureX/0611/Folding_table/001.png` | null | `['workbench']` | `_rounded_panel`, `_bar_pose`, `_add_leg_visuals`, `_add_brace_visuals`, `build_object_model` |
| `rec_picturex_0611__folding_table__002__png_f2f71083d3f24464854e6f048c746976` | `pictureX/0611/Folding_table/002.png` | null | `['workbench']` | `_leg_web_shape`, `build_object_model` |
| `rec_picturex_0611__folding_table__003__png_20026283e1e34d9cbb817acb4dbbd289` | `pictureX/0611/Folding_table/003.png` | null | `['workbench']` | `_rounded_panel`, `_beam_origin`, `build_object_model` |
| `rec_picturex_0611__folding_table__004__png_a30fb8a6461c4f59ae6ad0834120488b` | `pictureX/0611/Folding_table/004.png` | null | `['workbench']` | `_beam_xz`, `_beam_yz`, `_add_table_half`, `_add_leg_pair`, `_add_locking_brace`, `build_object_model` |

Potential structure vocabulary after review: single rigid tabletop, split/folding
tabletop halves, folding leg pairs, cross braces, locking braces, molded or
tubular leg webs.

### `Folding_table1`

| record_id | picture | rating | collections | observed helper surface |
|---|---|---:|---|---|
| `rec_picturex_0611__folding_table1__001__png_0b428e5ff1244f358d87b7bdb6280028` | `pictureX/0611/Folding_table1/001.png` | null | `['workbench']` | `_midpoint`, `_distance`, `_rpy_for_cylinder`, `_add_tube`, `build_object_model` |
| `rec_picturex_0611__folding_table1__002__png_d8a89d70dc0f47578894d5248ec122c6` | `pictureX/0611/Folding_table1/002.png` | null | `['workbench']` | `_rounded_plate`, `_tube`, `build_object_model` |
| `rec_picturex_0611__folding_table1__003__png_119980c9a7f043de91626799dd220807` | `pictureX/0611/Folding_table1/003.png` | null | `['workbench']` | `_tube_mesh`, `_hollow_x_tube_mesh`, `build_object_model` |

Potential structure vocabulary after review: tubular folding frame, rounded
tabletop plate, X-brace or cross-tube support, folding leg pivots, foot tubes.

### `Folding_table2`

| record_id | picture | rating | collections | observed helper surface |
|---|---|---:|---|---|
| `rec_picturex_0611__folding_table2__001__png_49f1fec0c3e148ed97f2cdfdb905c116` | `pictureX/0611/Folding_table2/001.png` | null | `['workbench']` | `_rounded_box`, `_tabletop_black_shell`, `_tabletop_insert`, `_outer_column_tube`, `_hinge_barrel`, `_add_caster_visuals`, `build_object_model` |

Potential structure vocabulary after review: folding tabletop shell/insert,
central column or pedestal, hinge barrel, wheeled/castered base, compact folding
support.

## Related Existing Source

`Camping_Outdoor_Gear__Folding_camp_table.md` exists as a nearby but distinct
source map. Reuse only if a human decides these `pictureX/0611/Folding_table*`
subcategories should be merged into the camping/outdoor folding camp table
taxonomy. Otherwise it should remain reference-only and must not be treated as
source evidence for these requested subcategories.

## New Variant Records

### `Folding_sofa_bed1`

- `rec_picturex0611_folding_sofa_bed1_clickclack_back`
- `rec_picturex0611_folding_sofa_bed1_pullout_deck`
- `rec_picturex0611_folding_sofa_bed1_trifold_panels`

### `Folding_sofa_bed2`

- `rec_picturex0611_folding_sofa_bed2_metal_futon_frame`
- `rec_picturex0611_folding_sofa_bed2_storage_base`
- `rec_picturex0611_folding_sofa_bed2_chaise_extension`
- `rec_picturex0611_folding_sofa_bed2_slatted_deck`

### `Folding_sofa_bed3`

- `rec_picturex0611_folding_sofa_bed3_ratchet_back`
- `rec_picturex0611_folding_sofa_bed3_fold_down_arms`
- `rec_picturex0611_folding_sofa_bed3_rollout_legs`
- `rec_picturex0611_folding_sofa_bed3_ottoman_extension`

### `Folding_table`

- `rec_picturex0611_folding_table_scissor_base`

### `Folding_table1`

- `rec_picturex0611_folding_table1_rolltop_slats`
- `rec_picturex0611_folding_table1_telescoping_legs`

### `Folding_table2`

- `rec_picturex0611_folding_table2_x_trestle_base`
- `rec_picturex0611_folding_table2_four_corner_legs`
- `rec_picturex0611_folding_table2_bifold_top`
- `rec_picturex0611_folding_table2_drop_leaf_side`

## Source Maps Written

- `<ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711/picture_expansion/template_source_maps/0611__Folding_sofa_bed1.md`
- `<ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711/picture_expansion/template_source_maps/0611__Folding_sofa_bed2.md`
- `<ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711/picture_expansion/template_source_maps/0611__Folding_sofa_bed3.md`
- `<ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711/picture_expansion/template_source_maps/0611__Folding_table.md`
- `<ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711/picture_expansion/template_source_maps/0611__Folding_table1.md`
- `<ARTI_SKILL_ROOT>/pictureX_0611_selected_categories_records_no_urdf_mesh_20260711/picture_expansion/template_source_maps/0611__Folding_table2.md`

## Gate Checklist

- Generated workbench records exist for every requested subcategory.
- All generated records compile successfully with full validation.
- Compile reports exist under the source package materialization cache.
- 18 new single-axis variants were generated and validated.
- Source maps exist for all six requested subcategories.
- Records are not manually rated.
- Records are not confirmed as 5-star high-quality sources.
- No downstream sync should be run yet.
- No formal modular spec should be written yet.
- No template implementation should be generated yet.

## Hard Stop

The batch is now at the variant inspection gate. Machine checks prove that the
current origins and variants compile and remain workbench-only, but they do not
prove visual identity, mechanism correctness, or usable slot vocabulary. Per the
referenced pipeline, do not sync 5-star sources, write specs, or implement
templates until a human confirms which variant pools are accepted.

## Recommended Next Batch Actions

1. Preview the listed workbench records for each subcategory and mark accepted
   samples. Reject identity drift, floating parts, wrong joints, missing support,
   or bad category binding.
2. For subcategories with fewer than five accepted samples, generate targeted
   variants from accepted parents only. Keep each variant to one structural axis.
3. After acceptance, sync only accepted records into `arti-template` with rating
   5, then rebuild search.
4. Write one `specs_modular_v1/<slug>.md` per approved subcategory using the
   accepted record ids and exact source evidence.
5. Implement templates one at a time and run `template sweep-pipeline` before
   moving to the next category.
