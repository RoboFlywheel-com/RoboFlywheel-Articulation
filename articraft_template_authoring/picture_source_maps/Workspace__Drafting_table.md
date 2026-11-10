# Source Map — Workspace / Drafting table

slug `drafting_table` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_workspace__drafting_table__001_png_5a8e04ab8781490d928f4f521d03383a` — picture/Workspace/Drafting table/001.png
- `rec_workspace__drafting_table__003_png_fddcf4079562461d95f0ff535db2c6cf` — picture/Workspace/Drafting table/003.png
- `rec_workspace__drafting_table__002_png_21d3627a59614200863aeb0c4b91fa38` — picture/Workspace/Drafting table/002.png

## Variants generated this batch (5 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_drafting_table_var_base_column` | base_column | PASS | 3 | 2 |
| `rec_drafting_table_var_base_fourpost` | base_fourpost | PASS | 3 | 2 |
| `rec_drafting_table_var_grip_crank` | grip_crank | PASS | 3 | 2 |
| `rec_drafting_table_var_mech_height` | mech_height | PASS | 4 | 2 |
| `rec_drafting_table_var_n_drawers3` | n_drawers3 | PASS | 3 | 2 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Workspace / Drafting table (`drafting_table`)

Richness band: **normal** (target 12–18 candidate anchors). Coverage-first, no padding.
Pattern: **mixed** — single support root carries a hinged tilting board child (revolute) + side lock-knob children (revolute); homogeneous drawer/ratchet-tooth multiplicity.

## subcategory_contract
```yaml
subcategory_contract:
  category: Workspace
  subcategory: Drafting table
  core_identity: A wide flat drawing board that tilts on a hinge at its low (front) edge, carried by a floor-standing support, with a user-set angle lock.
  must_keep:
    - a wide planar drawing board (the work surface)
    - a real tilt articulation of the board (revolute hinge along the front/low edge)
    - a floor-grounded support that raises the board to standing/seated drafting height
    - an angle-hold control (lock knob / ratchet) that fixes the board angle
  must_not_become:
    - plain flat writing desk / office desk (non-tilting fixed top)
    - dining/bistro table or workbench
    - artist easel (no work surface / not floor-table height) or drafting stool
    - filing cabinet / dresser (drawer bank without the tilting board)
  image_evidence:
    - 001: pale-wood tilting board + black metal cantilever frame, two ring-pull drawers, front perforated mesh basket, left auxiliary shelf, right tool tray with pen holes/cup, side hand-crank winder visible on the frame
    - 002: reddish-wood board with black raised rim + paper channels, splayed X-braced black metal legs with a toothed ratchet angle plate, front supply tray with pale drawer faces, round side lock knobs
    - 003: vintage cherry-wood trestle (A-frame upright) base, black metal curved ratchet quadrant setting the board angle, large + small lobed hand knobs, no drawers
  parent_evidence:
    - all three: part `tabletop`/`support(frame)` split; `frame_to_tabletop` REVOLUTE tilt with lower<0<upper; side lock-knob REVOLUTE children on the frame
    - A: metal cantilever `frame` (front/rear splayed legs, foot bars, mesh `perforated_basket`, ring-pull drawers via loop over (-0.255,0.255)), tool_tray_rail w/ holes, side_shelf, tilt axis +X
    - B: metal `frame` with `side_brace`/`rear_kick_brace` X legs, `ratchet_tooth_{idx}_{tooth}` via `for tooth in range(6)`, `front_supply_tray` w/ `tray_divider`×3 + `drawer_face`×4 loops, tilt axis +X
    - C: wood `support_frame` trestle via `for suffix,y in (("near",-0.62),("far",0.62))`, `_annular_sector_geometry` curved `ratchet_arc_plate`, distinct `lock_knob`(large)+`angle_knob`(small), tilt axis −Y
```

## Slots & Candidate Grid

### Slot: support_base (① skeleton / structural topology)
| candidate | source_type | record/evidence | status |
|---|---|---|---|
| cantilever_metal_Zframe | origin_anchor | A `frame` splayed legs+foot bars+basket | converged |
| splayed_metal_Xbrace | origin_anchor | B `frame` side_brace/rear_kick_brace | converged |
| wood_trestle_Aframe | origin_anchor | C `support_frame` uprights+trestle feet | converged |
| central_pedestal_column | forked_anchor | fork@B → rec_drafting_table_var_base_column | planned |
| four_post_legs | forked_anchor | fork@B → rec_drafting_table_var_base_fourpost | planned |

### Slot: angle/height mechanism (② joint / mechanism)
| candidate | source_type | record/evidence | status |
|---|---|---|---|
| friction_knob_tilt_lock | origin_anchor | A tilt revolute held by side lock_knobs (no teeth) | converged |
| linear_toothed_ratchet | origin_anchor | B `ratchet_tooth` strip (6 teeth) | converged |
| curved_ratchet_quadrant | origin_anchor | C `ratchet_arc_plate` annular sector | converged |
| telescoping_prismatic_height | forked_anchor | fork@B → rec_drafting_table_var_mech_height (adds vertical prismatic DOF) | planned |

### Slot: user control / handle_or_grip (③ control form family)
| candidate | source_type | record/evidence | status |
|---|---|---|---|
| paired_symmetric_lock_knobs | origin_anchor | A/B `lock_knob_0/1` | converged |
| differentiated_large_small_knobs | origin_anchor | C `lock_knob`+`angle_knob` | converged |
| crank_winder_handle | forked_anchor | fork@A → rec_drafting_table_var_grip_crank (photo shows a side crank) | planned |

### Slot: under-board drawer bank (N multiplicity)
| candidate | source_type | record/evidence | status |
|---|---|---|---|
| n_drawers = 0 (open, no drawers) | origin_anchor (record) | C trestle, no storage | converged |
| n_drawers = 2 | origin_anchor | A ring-pull drawers loop | converged |
| n_drawers = 4 | origin_anchor | B `drawer_face` ×4 loop | converged |
| n_drawers = 3 | forked_anchor | fork@A → rec_drafting_table_var_n_drawers3 | planned |

### Accessory surface layer (record_only — ④, not candidate-anchor)
tool_tray_rail w/ pen holes + cup_socket (A), side auxiliary shelf (A), front perforated mesh basket (A), front supply cubby tray w/ dividers (B), paper_stop / paper_channel / raised board rim (all). Recorded, not forked.

## Mandatory 6-Axis Diversity Audit
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / structural topology | source-backed (candidate anchor) | cantilever-metal(A), splayed-X-metal(B), wood-trestle(C) + forks: central-pedestal-column, four-post-legs |
| ② joint / mechanism type | source-backed (candidate anchor) | tilt REVOLUTE (all, axis +X A/B, −Y C); angle-hold: friction-knob(A) / linear-ratchet(B) / curved-quadrant(C); + fork: prismatic height carriage. Knobs REVOLUTE spin-in-place. |
| ③ primary form family | source-backed (candidate anchor) | main body = single planar drawing board across all origins (no body-form family variety). Form variety lives in the control: round knob(A/B) / large+small knob(C) / + fork crank winder. |
| ④ surface decoration | record_only / world_knowledge_extrapolation | wood grain streak loops, pen/pencil holes in tool rail, perforated mesh basket, drawer ring-pulls, ratchet screw holes; extrapolate: parallel-rule bar, drawing-clip strip |
| ⑤ proportion / size / travel | record_only | board width ~1.08–1.26 m, depth ~0.76–0.82; tilt limits lower −0.20…−0.30, upper +0.45…+0.65 rad; knob spin ±π; fork height travel ~0.15 m |
| ⑥ material / palette / finish | record_only | pale wood(A) / warm-red wood(B) / cherry wood(C); black powder-coat vs blackened steel metal; steel/gunmetal/plastic hardware |

## Multiplicity / Copy Logic
- count_param: `n_drawers` (front under-board supply drawers)
- N samples (source-backed): 2 (origin A ring-pull loop), 4 (origin B drawer_face loop); + fork 3 → rec_drafting_table_var_n_drawers3. N=0 shown by trestle origin C.
- suggested N_range: [1,4]
- copied_object: drawer face + ring-pull hardware set; naming `drawer_{i}` / `pull_ring_{i}` with `drawer_divider_{i}` between cells
- placement_rule: even spacing across the `drawer_apron` X-width via for-i-in-range(N) loop, shared pull helper
- joint_policy: drawer faces are FIXED cosmetic panels (parents do not open drawers); multiplicity fork keeps FIXED policy. The real non-fixed joints (tilt + knobs) are unchanged.
- secondary N (record_only, not forked): ratchet teeth `for tooth in range(6)` (B); N_range ~[6,12] — copy logic already shown by B's loop, no fork.

## Budget Decision
Candidate anchors total = **15** (origins + forks): ① 5, ② 4, ③ 3, N 3 (N=0 recorded but not counted as a separate anchor line → count 3 of the 4 drawer rows). Fits **normal** band (12–18). Fork jobs emitted = **5**. Origins already cover 10 candidate anchors, so only 5 new candidates need forks. No probes needed (interface risks in the planned forks are low; the pedestal/four-post reuse the same hinge+knob head, the prismatic fork adds a single clean sliding sleeve).

## Variant Cards (one per fork)
```yaml
- variant_id: rec_drafting_table_var_base_column
  source_type: forked_anchor
  parent_record_id: rec_workspace__drafting_table__002_...
  primary_axis: {slot: support_base, diversity_axis: ①, target_candidate: central_pedestal_column}
  structural_delta: {change: [splayed legs+runners -> single central mast on cruciform/tripod foot; hinge rail+ratchet+knob sockets moved to column head], keep_parts: [tabletop, wood_drawing_board, tilt_barrel, front_hinge_rail, ratchet_backbone, knob_socket, lock_knob_{idx}, frame_to_tabletop, frame_to_lock_knob_{idx}], joint_policy: preserve tilt+knob revolutes, interface_policy: hinge/knob anchored to new column head plate}
  multiplicity: {applies: false}
  acceptance_focus: [tilt revolute unchanged, board carried by single column, no floating head]
- variant_id: rec_drafting_table_var_base_fourpost
  source_type: forked_anchor
  primary_axis: {slot: support_base, diversity_axis: ①, target_candidate: four_post_legs}
  structural_delta: {change: [splayed braced legs -> 4 straight corner legs via loop + box apron], keep_parts: [tabletop..., front_hinge_rail, ratchet_backbone, knob_socket, lock_knob_{idx}, frame_to_tabletop, frame_to_lock_knob_{idx}], joint_policy: preserve tilt+knob revolutes, interface_policy: hinge on front apron, knobs on side apron}
  multiplicity: {applies: true, target_n: 4, copied_object: leg, placement_rule: grid/corner}
  acceptance_focus: [4 looped legs, retains tilt+lock, does not read as flat desk]
- variant_id: rec_drafting_table_var_mech_height
  source_type: forked_anchor
  primary_axis: {slot: angle_height_mechanism, diversity_axis: ②, target_candidate: telescoping_prismatic_height}
  structural_delta: {change: [split base into grounded outer sleeves + movable inner carriage; add ONE prismatic base_to_carriage vertical joint ~0.15 m], keep_parts: [tabletop..., frame_to_tabletop, lock_knob_{idx}, frame_to_lock_knob_{idx}], joint_policy: add exactly one prismatic height DOF, interface_policy: inner tube slides inside outer sleeve}
  multiplicity: {applies: false}
  acceptance_focus: [prismatic joint raises whole board assembly, tilt+knob preserved, tubes visibly telescope]
- variant_id: rec_drafting_table_var_grip_crank
  source_type: forked_anchor
  parent_record_id: rec_workspace__drafting_table__001_...
  primary_axis: {slot: handle_or_grip, diversity_axis: ③, target_candidate: crank_winder_handle}
  structural_delta: {change: [lobed knob disk -> radial crank arm + revolving grip on same spindle], keep_parts: [frame, tabletop, hinge_*, tool_tray_rail, side_shelf, drawer/pull_ring, frame_to_tabletop], joint_policy: keep revolute (crank sweeps circle in place), interface_policy: threaded_stem seated in hinge cheek}
  multiplicity: {applies: false}
  acceptance_focus: [crank is a real non-fixed revolute (not a fixed handle), spins in place, base/tilt/drawers unchanged]
- variant_id: rec_drafting_table_var_n_drawers3
  source_type: forked_anchor
  parent_record_id: rec_workspace__drafting_table__001_...
  primary_axis: {slot: drawer_bank, diversity_axis: N, target_candidate: n_drawers=3}
  structural_delta: {change: [2 ring-pull drawers -> 3 via for-i-in-range(3) loop + drawer_divider_{i}], keep_parts: [frame, tabletop, tilt/knob joints], joint_policy: drawer faces FIXED (as parent), interface_policy: shared pull helper on apron face}
  multiplicity: {applies: true, target_n: 3, copied_object: drawer face + ring pull, placement_rule: even X spacing}
  acceptance_focus: [3 looped drawers, no hand-copied blocks, still a drafting-table apron]
```

## Blocked / Excluded
- parallelogram / gas-spring counterbalance arm (②): drift + high mechanical risk, not clearly shown in refs — blocked to avoid over-engineering.
- ratchet-tooth N-sweep (e.g. N=10) as its own fork: excluded — copy logic already exposed by B's `for tooth in range(6)`; recorded as record_only N_range.
- ④/⑤/⑥-only variants (material/palette/scale, alternate wood tones, tool-tray decor): excluded per rules; recorded in the 6-axis audit only.

underfilled_reason: none — drafting tables have moderate structural vocabulary; 15 honest candidate anchors sit comfortably in the normal band without padding.
