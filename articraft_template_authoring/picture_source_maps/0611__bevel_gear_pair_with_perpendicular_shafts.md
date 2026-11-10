# 0611 / bevel_gear_pair_with_perpendicular_shafts — template source map
status: converged — GATE P1 machine-pass; human variant inspection confirmed 2026-07-12
pattern: parallel_children (support_frame root -> two CONTINUOUS shaft joints -> horizontal_drive + vertical_drive, mesh-coupled by mimic); multiplicity on the per-gear tooth loop
parents: rec_picturex_0611__bevel_gear_pair_with_perpendicular_shafts__001__png__airflex_batch_20260710_3880e38060ab47eabd6140ed98182b36 (picture/0611/bevel_gear_pair_with_perpendicular_shafts/001.png)
canonical_baselines: (none yet)
budget_note: 13 candidate anchors across 5 slots + 3 tooth-count N samples; within normal budget.

subcategory_contract:
  category: 0611
  subcategory: bevel_gear_pair_with_perpendicular_shafts
  core_identity: two conical (bevel) gears meshing at a 90 deg shaft angle, each mounted on its own rotating shaft, with the two rotations physically coupled by the gear mesh
  must_keep: [two bevel gears meshing at 90 deg, each shaft on its own CONTINUOUS rotation joint (>=2 continuous joints), the mesh coupling (vertical joint mimic of horizontal), teeth loop-emitted by BevelGear/BevelGearPair, a support that carries both shafts]
  must_not_become: [spur-gear pair (parallel shafts), worm-and-wheel drive, planetary/epicyclic gear set]
  image_evidence: [001.png curved/spiral-look bevel pair in a machined open-window cage with a top vertical shaft in a bearing and a horizontal through-shaft; 002.png straight-tooth bevel pair in a similar box frame with a bottom vertical shaft and horizontal shafts]
  parent_evidence: [parts support_frame + horizontal_drive + vertical_drive; joints support_to_horizontal (CONTINUOUS axis x) and support_to_vertical (CONTINUOUS axis z) with Mimic(joint=support_to_horizontal, multiplier=-20/16); BevelGearPair(module=2.1, gear_teeth=20, pinion_teeth=16, face_width=10, axis_angle=90, pressure_angle=20, backlash=0.15) with helix_angle=0 -> straight bevel; bore_d=10; visuals horizontal_bevel_gear/vertical_bevel_gear from gear_meshes[0]/[1]; keyed shafts (horizontal_key, vertical_key); spacers; three bearing races (side_bearing_0/1, top_bearing); helpers _make_support_frame, _annulus]

## Slot Candidates
| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| gear_tooth_form | straight bevel (parent) | ③ | origin_anchor | 002.png, parent helix_angle=0 | BevelGearPair, gear_meshes[0]/[1] | converged |
| gear_tooth_form | spiral bevel | ③ | forked_anchor | var_spiral_bevel | BevelGearPair helix_angle~35 | converged |
| gear_tooth_form | Zerol bevel | ③ | forked_anchor | var_zerol_bevel | BevelGearPair helix_angle~10 | converged |
| gear_tooth_form | hypoid offset | ① | forked_anchor | var_hypoid_offset | offset vertical joint origin + top bearing | converged |
| ratio_size | mild reduction 20/16 (parent) | ① | origin_anchor | parent gear_teeth/pinion_teeth, mimic -1.25 | support_to_vertical mimic | converged |
| ratio_size | miter 1:1 (equal teeth/dia) | ③ | forked_anchor | var_miter_1to1 | equal gear_teeth==pinion_teeth, mimic -1.0 | converged |
| ratio_size | high reduction ~3:1 | ① | forked_anchor | var_reduction_high | 33/11, large crown gear, mimic -3.0 | converged |
| teeth_count (N) | coarse low count 12/10 | N | forked_anchor | var_teeth_coarse | BevelGear tooth loop, module up | converged |
| teeth_count (N) | mid count 20/16 (parent) | N | origin_anchor | parent gear_teeth=20/pinion_teeth=16 | BevelGear tooth loop | converged |
| teeth_count (N) | fine high count 32/26 | N | forked_anchor | var_teeth_fine | BevelGear tooth loop, module down | converged |
| shaft_form | keyed shafts (parent) | ① | origin_anchor | parent horizontal_key/vertical_key | horizontal_key, vertical_key | converged |
| shaft_form | bare plain shafts | ① | forked_anchor | var_shaft_bare | keys removed | converged |
| shaft_form | hub + setscrew | ① | forked_anchor | var_shaft_hub_setscrew | hub collar + radial setscrew boss | converged |
| shaft_form | flanged coupling ends | ① | forked_anchor | var_shaft_flanged | flange disc + bolt-circle loop | converged |
| mounting_housing | machined open-frame cage (parent) | ① | origin_anchor | 001.png, parent _make_support_frame windowed box | support_frame, frame_body | converged |
| mounting_housing | bracketed pillow-block stand | ① | forked_anchor | var_housing_bracketed | rebuilt _make_support_frame, open brackets | converged |
| mounting_housing | closed gearbox housing | ① | forked_anchor | var_housing_gearbox | rebuilt _make_support_frame, enclosed case | converged |
| hub_boss | thin spacer (parent) | ③ | origin_anchor | parent horizontal_spacer/vertical_spacer | horizontal_spacer, vertical_spacer | converged |
| hub_boss | extended integral hub boss | ③ | forked_anchor | var_hub_boss | enlarged hub cylinders behind gears | converged |

## Multiplicity / Copy Logic
- count_param: gear_teeth / pinion_teeth (number of teeth per gear, loop-emitted inside BevelGear via BevelGearPair)
- N samples: 12/10 (var_teeth_coarse, low), 20/16 (parent, mid), 32/26 (var_teeth_fine, high)
- suggested N_range: pinion 8..30, gear 10..40 (real bevel/miter stock), ratio typically 1:1 .. ~4:1
- copied object / naming / placement / joint policy: copied_object = single bevel tooth; naming = internal to BevelGear tooth loop (not per-tooth SDK parts, but count-driven); placement = radial around each pitch cone at equal angular pitch; joint_policy = teeth are fixed features of each rotating gear (no per-tooth joints). The vertical_joint mimic multiplier must equal -gear_teeth/pinion_teeth for every N sample.
- secondary multiplicity: flange bolt-hole ring on var_shaft_flanged (loop-emitted, count_param = flange_bolt_hole_count, default N=4; N_range 4/6/8) — exposes copy logic but the teeth loop is the primary N axis.

## Six-Axis Diversity Record
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / structural topology | source-backed | ratio topology (equal miter vs unequal reduction, changing teeth counts + cone diameters); hypoid shaft offset (non-intersecting 90 deg axes); shaft-to-gear interface (keyed / bare / hub+setscrew / flanged); support structure (open cage / pillow-block brackets / closed gearbox) |
| ② joint / mechanism type | source-backed (fixed identity, not a candidate anchor) | two CONTINUOUS shaft rotation joints (support_to_horizontal axis x, support_to_vertical axis z) with a Mimic mesh coupling are preserved across ALL variants; never reduced below 2 continuous joints; not used as a standalone fork |
| ③ primary form family | source-backed | tooth form (straight / spiral / Zerol bevel); gear body/hub construction (thin spacer vs extended hub boss); equal-vs-unequal cone-pair form |
| ④ surface decoration | record_only / world_knowledge_extrapolation | tooth-face chamfer/crowning, hex socket mark on setscrew boss, module/ratio stamps, cast ribs / cover-bolt pattern on gearbox case — host-conformal only, no dedicated variant |
| ⑤ proportion / size / travel | record_only | module ~2.1 (1.3 fine .. 3.5 coarse to hold pitch dia), face_width ~10, gear/pinion cone diameters, shaft lengths (~205 mm horizontal, ~122 mm vertical), hub/flange sizes; rotation travel is continuous/unlimited on both joints |
| ⑥ material / palette / finish | record_only | dark_gear_steel gears, machined_aluminum frame/case, polished_steel shafts/spacers, bearing_steel races, key_steel keys; alternates: brass/bronze gears, gray cast-iron case |

## Compatibility Probes
| probe | record_id | combined axes | risk tested | result |
|---|---|---|---|---|
| high crown gear vs open-frame clearance | rec_bevel_gear_pair_with_perpendicular_shafts_var_reduction_high | ① ratio + frame window proportion | enlarged 33T crown gear must clear frame_body window and side bearing housings | converged (probe noted in-variant) |
| enclosed case vs gear OD | rec_bevel_gear_pair_with_perpendicular_shafts_var_housing_gearbox | ① housing + internal clearance | closed cavity must clear gear outer diameter and align 3 shaft bores with bearings | converged (probe noted in-variant) |

## Blocked / Excluded
- P2 origin (rec_picturex_0611__bevel_gear_pair_with_perpendicular_shafts__002__png__airflex_batch_20260710_d5fbcd9190a44c679b47bd852085074b): blocked — origin fails to compile (>2min timeout); not usable as a fork parent. All forks are taken from P1 only. (002.png is still used as visual evidence for the straight-tooth / box-frame form.)
- non-90 shaft angle (skew / crossed-helical / angular bevel): blocked — leaves the "perpendicular shafts" identity; axis_angle stays 90 for all ordinary variants (hypoid keeps 90 with a lateral offset only).
- worm-and-wheel operator: blocked — a single-start worm driving a wheel is a neighbor category (worm gear), not a bevel pair; would violate must_not_become.
- planetary / epicyclic conversion: blocked — neighbor category; would add a carrier and multiple joints, breaking the two-shaft bevel identity.
- spur-gear pair (parallel shafts): blocked — neighbor category; loses the 90 deg conical mesh.
- adding a second gear pair / third shaft (differential): excluded — task scope keeps a single pair; a third collinear shaft reads as a differential, a different subcategory.
- material-only forks (brass gears / cast-iron case / alternate palettes): excluded from candidate count — ⑥ record_only, may ride along on structural forks.
- proportion-only forks (module/face-width/shaft-length tweaks): excluded from candidate count — ⑤ record_only, may ride along on structural forks.

## GATE P1 Verification (machine)
- normal variants forked & accepted: 13 (all exit 0)
- compatibility probes reuse normal variant records: 2 (`rec_bevel_gear_pair_with_perpendicular_shafts_var_reduction_high`, `rec_bevel_gear_pair_with_perpendicular_shafts_var_housing_gearbox`)
- compatibility probe-only variants: 0
- total synced source records after confirmation: 14 (1 usable origin + 13 normal variants; blocked P2 origin excluded)
- compile: ALL success
- articulation: every variant has >=1 non-fixed joint
- promotion: all workbench-only (dataset not in collections)
- binding: all bound to picture_category=0611 / picture_subcategory=bevel_gear_pair_with_perpendicular_shafts, parent_record_id set (verified in data/index/subcat/0611__bevel_gear_pair_with_perpendicular_shafts.jsonl)
- run_tests: every variant exports run_tests with axis-specific ctx.check/expect assertions (9-36 checks each)
- N-multiplicity axes verified to realize distinct counts (loop-emitted, stable indexed naming)
- human variant inspection: confirmed by user on 2026-07-12; downstream sync/spec/template stages may proceed.
