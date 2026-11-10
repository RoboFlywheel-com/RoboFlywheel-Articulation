# Source Map — Textiles_Fabric / Ironing board

slug `ironing_board` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_textiles_fabric__ironing_board__002_png_143983d17f334b44a8771c55083e9b98` — picture/Textiles_Fabric/Ironing board/002.png
- `rec_textiles_fabric__ironing_board__001_png_3d194111a13a4acd84617dd20115f652` — picture/Textiles_Fabric/Ironing board/001.png

## Variants generated this batch (4 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_ironing_board_var_form_rounded_oval` | form_rounded_oval | PASS | 3 | 2 |
| `rec_ironing_board_var_shelf_linen_rack` | shelf_linen_rack | PASS | 3 | 1 |
| `rec_ironing_board_var_shelf_rack_n10` | shelf_rack_n10 | PASS | 3 | 1 |
| `rec_ironing_board_var_skeleton_tabletop` | skeleton_tabletop | PASS | 2 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Textiles_Fabric / Ironing board — variant plan

slug `ironing_board` · pattern **mixed** (single `board` root carrying independent folding leg children + prismatic height latch; loop-emitted perforation dots/holes and notch teeth; optional under-shelf rung multiplicity).
Richness band: **simple (8–12 candidate anchors)** — ironing boards have thin honest structural vocabulary (elongated padded top + folding X-legs + height notch). Coverage first, no padding.

## subcategory_contract
```yaml
subcategory_contract:
  category: Textiles_Fabric
  subcategory: Ironing board
  core_identity: an elongated, tapered padded ironing surface on a folding leg stand
  must_keep:
    - flat elongated padded/fabric-covered ironing top (perforated deck under a cloth cover)
    - folding leg frame that raises the top and collapses (real non-fixed revolute leg joints)
    - height / fold articulation (leg revolutes + a prismatic height latch on a notched rail)
  must_not_become: [folding table / side table, drying / clothes rack, workbench, cutting board, sleeve board]
  image_evidence:
    - "002: sharp pointed nose + broad rounded tail; navy fabric cover with pale dot print; crossed (X) tubular legs; low wire storage shelf between legs; rear wire iron-holder loop; T-shaped feet; small companion mini board shown"
    - "001: pointed tapered board, warm-white palm-leaf print; black X legs with sliding rear pivot; rear tubular iron-rest rack + tray; T feet; height notch rail"
  parent_evidence:
    - "002: parts board / rear_leg_pair / front_leg_pair / height_latch; both leg pairs pivot directly on board (double-pivot X); board_to_rear_leg + board_to_front_leg revolute, board_to_height_latch prismatic; _notch_rail_mesh 6 V-notches; _wire_rest_mesh; loop-emitted cover_dot_/underside_hole_"
    - "001: parts board / height_slider / front_leg / rear_leg; front leg pivots on board, rear leg pivots on a translating slider (sliding-pivot X); board_to_height_slider prismatic + board_to_front_leg + slider_to_rear_leg revolute; ExtrudeWithHolesGeometry perforated deck; _perforation_holes loop; rear_iron_rest_rail tubular rack; 7 height_notch_ teeth"
```

## Slot / Candidate grid
| slot | candidate | axis | source_type | evidence | status |
|---|---|---|---|---|---|
| leg_skeleton | double_pivot_X (both legs pivot on board) | ① | origin_anchor | 002 | converged |
| leg_skeleton | sliding_pivot_X (rear leg on translating slider) | ① | origin_anchor | 001 | converged |
| leg_skeleton | tabletop fold-flat short legs | ① | forked_anchor | var_skeleton_tabletop | planned |
| board_planform | pointed-nose tapered board | ③ | origin_anchor | 001 & 002 | converged |
| board_planform | rounded-both-ends oval board | ③ | forked_anchor | var_form_rounded_oval | planned |
| iron_rest | rear wire-loop holder | accessory | origin_anchor | 002 (`_wire_rest_mesh`) | converged |
| iron_rest | rear tubular rack + tray | accessory | origin_anchor | 001 (`rear_iron_rest_rail`) | converged |
| under_shelf | none | ① | origin_anchor (default) | 001 | converged |
| under_shelf | lower linen/garment wire shelf | ① + N | forked_anchor | var_shelf_linen_rack / var_shelf_rack_n10 | planned |
| height_adjust | notched-rail + sliding latch | ② | origin_anchor | 001 & 002 | converged (only real mechanism; alternatives record_only) |

Each supported slot reaches ≥2 structurally distinct candidates (leg_skeleton 3, board_planform 2, iron_rest 2, under_shelf 2). height_adjust has a single genuine sourced mechanism; friction-clamp / fixed-height alternatives are not source-backed and are recorded only.

## Six-Axis Diversity Audit
| axis | candidate-anchor status | treatment | values |
|---|---|---|---|
| ① skeleton / topology | anchor | source-backed | double_pivot_X (002), sliding_pivot_X (001), tabletop fold-flat (fork), + under-shelf added structure (fork) |
| ② joint / mechanism | anchor | source-backed | leg revolutes (both), rear-leg-on-slider revolute (001), prismatic height slider/latch on notch rail (both) |
| ③ primary form family | anchor | source-backed | planar boundary: pointed-nose taper (origins) vs rounded oval (fork) |
| ④ surface decoration | record_only / companion | not standalone | cover print (navy dot 002, grey palm 001), perforation dots/holes, underside vent holes — host-conformal, no dedicated variant |
| ⑤ proportion / size / travel | record_only / companion | not standalone | board length ~1.4–1.6, height ~0.78–0.9 open; leg fold ~1.05–1.18 rad; height-latch travel ~0.11–0.12; tabletop shrinks proportion as companion only |
| ⑥ material / palette | record_only / companion | not standalone | fabric navy/white or warm-white; frame galvanized silver (002) or black powder-coat (001); rubber/plastic feet; zinc hardware |

## Multiplicity / Copy Logic
- **notch teeth** — count_param `n_notches`; source-backed samples 002=6 (`_notch_rail_mesh`), 001=7 (`height_notch_`); template N_range ~[4,12]; copied object = V-notch/tooth on a shared rail, indexed, evenly spaced, FIXED decoration on the height rail. Already covered by two origins → no separate fork.
- **under-shelf rungs** — count_param `n_shelf_rungs`; forked samples N=6 (var_shelf_linen_rack) and N=10 (var_shelf_rack_n10); template N_range ~[4,14]; copied object = longitudinal wire `rung_{i}`, loop-emitted, evenly spaced across shelf width, on a shared helper; joint policy: shelf is a fixed carried structure (no non-fixed joint of its own; board still articulates).
- perforation dots/holes (`cover_dot_`, `_perforation_holes`) — cosmetic ④ copy logic, record_only, not a candidate anchor.

## Budget decision
- Candidate anchors (origins + converged forks) = **10**: double_pivot_X, sliding_pivot_X, tabletop skeleton, pointed planform, oval planform, wire-loop rest, tubular-rack rest, no-shelf, linen-shelf N6, linen-shelf N10.
- Band = simple (8–12). Fork jobs emitted = **4**. No ④/⑤/⑥/scale/material padding.
- `underfilled_reason`: none — lands mid-simple band honestly. height_adjust kept at 1 real mechanism rather than inventing filler alternatives.

## Variant cards
```yaml
variant_card:
  variant_id: rec_ironing_board_var_skeleton_tabletop
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__ironing_board__002...
  positioning: {product_archetype: tabletop/benchtop mini ironing board, why_same_subcategory: padded folding ironing top on folding legs, just short-stanced}
  primary_axis: {slot: leg_skeleton, diversity_axis: ①, target_candidate: tabletop fold-flat short legs}
  structural_delta:
    change: [shorten both leg pairs to a low stance, re-aim revolutes so legs fold flush/coplanar under board, drop height notch/latch as fixed-height consequence]
    keep_parts: [board, front_leg_pair, rear_leg_pair, board_to_front_leg, board_to_rear_leg]
    joint_policy: preserve both leg revolutes; remove the prismatic height latch (tabletop is fixed height)
    interface_policy: legs stow coplanar against board underside
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [compact board proportion], forbidden: [planform change, added board, rigid non-folding base]}
  acceptance_focus: [legs fold flat, real revolute joints remain, stays elongated padded top]
---
variant_card:
  variant_id: rec_ironing_board_var_form_rounded_oval
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__ironing_board__001...
  positioning: {product_archetype: oval / rounded-nose ironing board, why_same_subcategory: same padded top + folding X stand, only planform boundary differs}
  primary_axis: {slot: board_planform, diversity_axis: ③, target_candidate: rounded-both-ends oval}
  structural_delta:
    change: [rewrite _board_outline to rounded nose arc + near-parallel sides + rounded tail, update _half_width_at/_perforation_holes]
    keep_parts: [board, perforated_deck, fabric_cover, padded_edge_band, front_leg, rear_leg, height_slider, board_to_front_leg, slider_to_rear_leg, board_to_height_slider, rear_iron_rest_rail]
    joint_policy: preserve all joints unchanged
    interface_policy: leg pivot X-positions unchanged; deck/cover/edge extrusions track new outline
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [fabric print/palette], forbidden: [leg/joint/rest/mechanism change]}
  acceptance_focus: [rounded nose planform, cover/deck consistent, joints intact]
---
variant_card:
  variant_id: rec_ironing_board_var_shelf_linen_rack
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__ironing_board__002...
  positioning: {product_archetype: ironing board with lower linen storage shelf (ref 002), why_same_subcategory: ironing top + folding legs plus a carried under-shelf}
  primary_axis: {slot: under_shelf, diversity_axis: ① (added structure) + N, target_candidate: lower wire linen shelf}
  structural_delta:
    change: [add linen_shelf part = perimeter wire frame + N loop-emitted rungs, hung below on visible drop supports]
    keep_parts: [board, front_leg_pair, rear_leg_pair, height_latch, board_to_front_leg, board_to_rear_leg, board_to_height_latch, _leg_pair_mesh, _underframe_mesh]
    joint_policy: shelf fixed-jointed to board (carried static structure); existing leg/latch joints untouched
    interface_policy: shelf hangs on visible supports below board underframe, no float
  multiplicity: {applies: true, target_n: 6, copied_object: rung_{i}, placement_rule: even longitudinal spacing}
  companion_variations: {allowed_④⑤⑥: [wire gauge/finish], forbidden: [planform/leg/leg-joint change, shelf as primary object]}
  acceptance_focus: [shelf loop-emitted rungs, supported not floating, ironing surface still primary]
---
variant_card:
  variant_id: rec_ironing_board_var_shelf_rack_n10
  source_type: forked_anchor
  parent_record_id: rec_textiles_fabric__ironing_board__002...
  positioning: {product_archetype: ironing board with dense-rung lower linen shelf, why_same_subcategory: same as N6 shelf variant, denser rungs}
  primary_axis: {slot: under_shelf, diversity_axis: N multiplicity, target_candidate: shelf rungs N=10}
  structural_delta:
    change: [same linen_shelf, rung count 6 -> 10 via same for-loop, tighter spacing]
    keep_parts: [board, front_leg_pair, rear_leg_pair, height_latch, board_to_front_leg, board_to_rear_leg, board_to_height_latch, _leg_pair_mesh, _underframe_mesh]
    joint_policy: shelf fixed-jointed to board; existing joints untouched
    interface_policy: identical to N6 shelf except rung count/spacing
  multiplicity: {applies: true, target_n: 10, copied_object: rung_{i}, placement_rule: even longitudinal spacing}
  companion_variations: {allowed_④⑤⑥: [wire gauge/finish], forbidden: [any axis other than rung count]}
  acceptance_focus: [N=10 loop-emitted rungs, paired with N6 to expose copy logic]
```

## Blocked / Gated
- **wall-mounted / drop-down fold-out ironing board**: real product but no free-standing legs and high risk of drifting to cabinet/furniture; `blocked` (out of the free-standing folding-board archetype the origins establish).
- **iron_rest = none**: removal, not a structural candidate; not forked.
- **height_adjust alternatives (friction clamp / fixed-height)**: not source-backed; `record_only`, not forked.
- **notch-teeth N as a separate fork**: origins already show N=6 and N=7; copy logic covered without a dedicated fork.
