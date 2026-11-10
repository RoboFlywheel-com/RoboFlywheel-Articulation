# Source Map — Textiles_Fabric / Needle case

slug `needle_case` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_an-open-tan-leather-knitting-needle-case-organiz_20260708_094902_572473_bc5bd0c0` — picture/Textiles_Fabric/Needle case/001.png
- `rec_a-saddle-brown-leather-knitting-needle-case-that_20260708_092645_846244_37039d39` — picture/Textiles_Fabric/Needle case/002.png

## Variants generated this batch (7 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_needle_case_var_channels_n6` | channels_n6 | PASS | 17 | 0 |
| `rec_needle_case_var_closure_zipper` | closure_zipper | PASS | 4 | 0 |
| `rec_needle_case_var_form_tube` | form_tube | PASS | 1 | 0 |
| `rec_needle_case_var_internal_loops` | internal_loops | PASS | 4 | 0 |
| `rec_needle_case_var_needles_n5` | needles_n5 | PASS | 4 | 0 |
| `rec_needle_case_var_skeleton_single_flat` | skeleton_single_flat | PASS | 2 | 0 |
| `rec_needle_case_var_skeleton_trifold_roll` | skeleton_trifold_roll | PASS | 18 | 0 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Textiles_Fabric / Needle case — variant plan

slug `needle_case` · pattern **mixed** (planar bifold leather case: one panel root carries
needle storage + hinged flaps/straps; second panel hangs on a central fold hinge; needle
copy-multiplicity and channel/divider multiplicity). Richness band: **normal** (target ~16-17
candidate anchors: 10 origin anchors + 7 forked anchors).

## Origins (full reconciliation, 2/2 usable)
| id | pic | built form | grid role |
|---|---|---|---|
| A `rec_an-open-tan-leather-knitting-needle-case-organiz_20260708_094902_572473_bc5bd0c0` | 001 | Open tan bifold organizer: `needle_panel` root with `channel_strip` (4 open-bottom tunnels, 8 bamboo double-pointed needles on **prismatic** slide-out), hinged `tip_flap`; `pocket_panel` on `fold_hinge` with `flat_pocket`, `cable_pocket` + coiled circular-needle `cable_coil`, `pocket_strap`/`cable_strap` snap straps; snap `cover_flap` on outer edge | skeleton=bifold / retention=channel_tunnels(prismatic) / storage=flat+coil_pocket / closure=snap_cover_flap / N: needles=8, tunnels=4 |
| B `rec_a-saddle-brown-leather-knitting-needle-case-that_20260708_092645_846244_37039d39` | 002 | Saddle-brown bifold: `base_panel`+`fold_panel` on `base_panel_to_fold_panel` spine; each panel a needle bed of 6 colorful `needle_{i}` threaded **under** a stitched `pocket_band` with `band_divider_{i}` dividers; `*_needle_flap` folds over tips; `closure_flap` with brass `snap_stud` wraps shut | skeleton=bifold / retention=stitched_band+dividers / closure=snap_cover_flap / N: needles=12 (6×2), dividers=7 |

## subcategory_contract
```yaml
subcategory_contract:
  category: Textiles_Fabric
  subcategory: Needle case
  core_identity: A dedicated case/organizer that stores and protects knitting/sewing needles (straight, double-pointed, or circular) in indexed positions, with a closure that keeps them contained.
  must_keep:
    - a needle bed / storage that holds an indexed row or bundle of needles
    - at least one real closure or retention articulation (fold hinge, cover flap, tie, cap, or zip)
    - needle-specific interior (channels/loops/band/pockets sized for needles, or an upright DPN bundle)
  must_not_become:
    - generic tool roll / brush roll / cosmetic roll (no needle-specific beds)
    - pen or pencil case / eyeglass case (no needle interior)
    - jewelry roll or soft cosmetic pouch/bag
  image_evidence:
    - 001: open leather bifold, row of bamboo DPN needles under raised channels, coiled steel circular-needle cables under a snap strap, snap cover flap
    - 002: leather bifold/trifold, rows of colorful interchangeable needle tips under stitched divider bands, fold-over tip flaps, brass snap closure
  parent_evidence:
    - A: needle_panel root, channel_strip tunnels, prismatic needle_{ci}_{si}_slide, tip_flap/cover_flap/pocket_strap/cable_strap revolutes, fold_hinge, flat_pocket + cable_pocket + cable_coil
    - B: base_panel/fold_panel spine revolute, _add_needle_bed helper, needle_{i} row, pocket_band + band_divider_{i}, flap_seam_ridge, *_needle_flap revolutes, closure_flap + snap_stud
```

## Slot / Candidate Grid
### Slot 1 — body_skeleton (① / ③)
| candidate | axis | source_type | record/evidence | status |
|---|---|---|---|---|
| bifold_planar | ① | origin_anchor | A, B | converged |
| trifold_rollup (chained panels + tie) | ① | forked_anchor | rec_needle_case_var_skeleton_trifold_roll (from A) | planned |
| single_flat_slip (one panel, no fold) | ① | forked_anchor | rec_needle_case_var_skeleton_single_flat (from B) | planned |
| rigid_tube (cylindrical DPN tube) | ③ | forked_anchor | rec_needle_case_var_form_tube (from B) | planned |

### Slot 2 — needle_retention_internal (internal_structure / ①)
| candidate | axis | source_type | record/evidence | status |
|---|---|---|---|---|
| channel_tunnels (prismatic slide) | ② internal | origin_anchor | A channel_strip + needle_{ci}_{si}_slide | converged |
| stitched_band + dividers (threaded under) | ① internal | origin_anchor | B pocket_band + band_divider_{i} | converged |
| leather_loop_row (one loop per needle) | ① internal | forked_anchor | rec_needle_case_var_internal_loops (from B) | planned |

### Slot 3 — accessory_storage (internal_structure)
| candidate | axis | source_type | record/evidence | status |
|---|---|---|---|---|
| flat_pocket | ① internal | origin_anchor | A flat_pocket | converged |
| coiled circular-needle cable_pocket | ① internal | origin_anchor | A cable_pocket + cable_coil | converged |

### Slot 4 — closure_motion (②)
| candidate | axis | source_type | record/evidence | status |
|---|---|---|---|---|
| snap_cover_flap (revolute + snap studs) | ② | origin_anchor | A cover_flap, B closure_flap + snap_stud | converged |
| zipper_slider (prismatic pull along rail) | ② | forked_anchor | rec_needle_case_var_closure_zipper (from B) | planned |
| wrap_tie (rides trifold_rollup) | ② | forked_anchor | in trifold_roll fork | companion |
| twist/pull cap (rides tube) | ② | forked_anchor | in form_tube fork | companion |

### Slot 5 — retaining_flap (②)
| candidate | axis | source_type | record/evidence | status |
|---|---|---|---|---|
| revolute tip/needle flap | ② | origin_anchor | A tip_flap_hinge, B *_needle_flap | converged |

### Slot 6 — multiplicity
| candidate | axis | source_type | record/evidence | status |
|---|---|---|---|---|
| needles N=8 | N | origin_anchor | A (4 channels × 2) | converged |
| needles N=12 | N | origin_anchor | B (6 × 2 panels) | converged |
| needles N=5/panel | N | forked_anchor | rec_needle_case_var_needles_n5 (from B) | planned |
| channel tunnels N=4 | N | origin_anchor | A CHANNEL_XS | converged |
| channel tunnels N=6 | N | forked_anchor | rec_needle_case_var_channels_n6 (from A) | planned |

## Six-Axis Diversity Audit
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / topology | source-backed | bifold(A,B) / trifold_rollup(fork) / single_flat(fork); retention topology band(B) vs channel(A) vs loops(fork) |
| ② joint / mechanism | source-backed | fold_hinge & spine revolute; flap/strap revolutes; prismatic needle slide(A); snap cover flap; +zipper prismatic(fork); +twist/pull cap(tube fork); +wrap tie(roll fork) |
| ③ primary form family | source-backed | planar leather panel(A,B) vs volumetric cylindrical tube(fork) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | cream saddle-stitch lines, stitched divider ridges, brass snap discs, embossed maker mark; extrapolate tooled/pyrography border |
| ⑤ proportion / size / travel | record_only | panel ~0.17-0.21 W × 0.22-0.24 H; needle Ø ~2-2.5 mm, len 0.115-0.17; needle slide travel ~0.095; flap open 0-2.7 rad |
| ⑥ material / palette / finish | record_only | leather tan / saddle brown / cognac; bamboo needles; brass studs; steel cables; colorful interchangeable tips (teal/purple/red/blue/green/orange) |

## Multiplicity / Copy Logic
- **needles**: count_param = len(NEEDLE_XS)/NEEDLE_OFFSETS; N samples {8 (A), 12 (B), 5 (fork)}; suggested N_range [4,16]; copied object `needle_{i}` / `needle_{ci}_{si}`; indexed naming; placement even-x row (B) or channel-pair (A); joint policy static-rest under band (B) or per-needle prismatic slide (A).
- **channel tunnels**: count_param = len(CHANNEL_XS); N samples {4 (A), 6 (fork)}; suggested N_range [3,8]; copied object channel slot in `channel_strip` with two prismatic-slide needles each; even-pitch placement; one prismatic joint per needle.
- **dividers**: count_param = len(DIVIDER_XS) (B, N=7); tracks needle count; FIXED decoration on `pocket_band`; recorded, not separately forked.

## Budget
Coverage-first. Candidate anchors = 10 origin + 7 forked = **17** (normal band 12-18). No padding: every fork is a distinct ①/②/③ or N structural candidate; ④/⑤/⑥ are record_only and never counted. No compatibility probes needed (skeleton and retention families are forked independently, not cross-combined).

## Variant Cards (forks)
```yaml
- variant_id: rec_needle_case_var_skeleton_trifold_roll
  source_type: forked_anchor
  parent_record_id: rec_an-open-tan-leather-knitting-needle-case-organiz_...
  primary_axis: {slot: body_skeleton, diversity_axis: ①, target_candidate: trifold_rollup}
  structural_delta: {change: [add middle_panel, second spine revolute, wrap_tie replaces cover_flap], keep_parts: [needle_panel, channel_strip, needle_*_slide, tip_flap, pocket_panel, fold_hinge, flat_pocket, cable_pocket], joint_policy: add one spine revolute, interface_policy: chained fold seams}
  multiplicity: {applies: true, target_n: 3 panels, copied_object: panel, placement_rule: chain}
- variant_id: rec_needle_case_var_skeleton_single_flat
  source_type: forked_anchor
  parent_record_id: rec_a-saddle-brown-...
  primary_axis: {slot: body_skeleton, diversity_axis: ①, target_candidate: single_flat_slip}
  structural_delta: {change: [remove fold_panel + spine hinge, re-parent closure_flap to base_panel], keep_parts: [base_panel, panel_shell, needle_i, pocket_band, band_divider_i, base_needle_flap], joint_policy: keep needle_flap revolute}
- variant_id: rec_needle_case_var_form_tube
  source_type: forked_anchor
  parent_record_id: rec_a-saddle-brown-...
  primary_axis: {slot: body_skeleton, diversity_axis: ③, target_candidate: rigid_cylindrical_tube}
  structural_delta: {change: [Cylinder tube_body replaces panel_shell, twist/pull cap joint, upright needle bundle], keep_parts: [needle_i, brass], joint_policy: add one cap joint (continuous or prismatic)}
- variant_id: rec_needle_case_var_internal_loops
  source_type: forked_anchor
  parent_record_id: rec_a-saddle-brown-...
  primary_axis: {slot: needle_retention_internal, diversity_axis: ①, target_candidate: leather_loop_row}
  structural_delta: {change: [remove pocket_band + band_divider_i, add loop_i arch per needle], keep_parts: [base_panel, panel_shell, needle_i, base_needle_flap, fold_panel], joint_policy: unchanged}
  multiplicity: {applies: true, target_n: loops == needle count, copied_object: loop_i, placement_rule: even-x row}
- variant_id: rec_needle_case_var_closure_zipper
  source_type: forked_anchor
  parent_record_id: rec_a-saddle-brown-...
  primary_axis: {slot: closure_motion, diversity_axis: ②, target_candidate: zipper_slider}
  structural_delta: {change: [zip_tape rail + prismatic zip_pull replace closure_flap + snap_stud], keep_parts: [base_panel, fold_panel, panel_shell, needle_i, pocket_band, base_panel_to_fold_panel, base_needle_flap], joint_policy: replace one revolute with one prismatic}
- variant_id: rec_needle_case_var_needles_n5
  source_type: forked_anchor
  parent_record_id: rec_a-saddle-brown-...
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: 5 needles/panel}
  multiplicity: {applies: true, target_n: 5, copied_object: needle_i, placement_rule: even-x spacing}
- variant_id: rec_needle_case_var_channels_n6
  source_type: forked_anchor
  parent_record_id: rec_an-open-tan-...
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: 6 channel tunnels}
  multiplicity: {applies: true, target_n: 6, copied_object: channel slot (2 prismatic needles each), placement_rule: even-x pitch}
```

## Blocked / Excluded
- individual deep sleeve pockets per needle — excluded to avoid padding (channel_tunnels + loops + band already give ≥3 distinct retention topologies).
- magnetic/tuck closure, elastic-band closure — record_only ② variants, not forked (snap + zip + tie + cap already cover the closure family).
- needles N=16 — excluded; {5,8,12} already exposes copy logic across the range.
