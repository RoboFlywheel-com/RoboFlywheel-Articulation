# Source Map — Workspace / Whiteboard easel

slug `whiteboard_easel` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_workspace__whiteboard_easel__001_png_d97e2e08aacc4cf4be89b7da5065b0cf` — picture/Workspace/Whiteboard easel/001.png
- `rec_workspace__whiteboard_easel__002_png_62adeead586e4395928bdaae3832ebf3` — picture/Workspace/Whiteboard easel/002.png

## Variants generated this batch (6 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_whiteboard_easel_var_base_fourpost` | base_fourpost | PASS | 2 | 0 |
| `rec_whiteboard_easel_var_base_tbase` | base_tbase | PASS | 6 | 1 |
| `rec_whiteboard_easel_var_board_revolve` | board_revolve | PASS | 11 | 1 |
| `rec_whiteboard_easel_var_board_slide` | board_slide | PASS | 9 | 1 |
| `rec_whiteboard_easel_var_board_tilt` | board_tilt | PASS | 12 | 1 |
| `rec_whiteboard_easel_var_n4_legs` | n4_legs | PASS | 10 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Workspace / Whiteboard easel (slug `whiteboard_easel`)

Richness band: **simple** (8–12). Target LOW end. Candidate anchors total = **8** (2 origins + 6 forks).
Structural vocabulary of this subcategory is concentrated in two layers only: the **support skeleton**
(how the board is held up) and the **board articulation** (how the panel itself moves). The writing
panel is always a planar rectangle, so axis ③ for the board body has no honest second value — see
`underfilled_reason`.

## subcategory_contract
```yaml
subcategory_contract:
  category: Workspace
  subcategory: Whiteboard easel
  core_identity: A free-standing floor easel whose primary element is a tall planar dry-erase writing
    board carried on its own portable leg/base stand, usually with a marker tray and some
    height/fold/tilt/reverse articulation.
  must_keep:
    - flat rectangular dry-erase writing panel framed by a perimeter rail
    - self-supporting floor stand (legs or wheeled/column base) that raises the board to writing height
    - a marker tray / ledge at the lower board edge
    - at least one real non-fixed joint (telescope, fold, tilt, revolve, caster, or board slide)
  must_not_become:
    - wall-mounted whiteboard (no floor stand)
    - tabletop / desktop flip easel (Workspace neighbor, no floor legs)
    - artist canvas painting easel with no dry-erase board
    - freestanding sign / menu / poster holder (display frame, not a writing board)
    - drafting table / desk (horizontal desk surface with drawers)
  image_evidence:
    - "001: blue powder-coated portrait board, perimeter frame, marker tray, two black side clamp knobs,
       H-shaped wheeled rolling base on 4 casters, telescoping vertical posts, rear brace."
    - "002: grey/aluminium portrait board, top flip-chart clamp bar, red magnet caps, marker tray with
       eraser, folding telescoping tripod (2 front + 1 rear splayed legs) with rubber feet, side knobs."
  parent_evidence:
    - "A(001): board_frame root + prismatic telescoping lower_leg_{0,1} in square sleeves, foot revolute,
       continuous casters ×4, rear_support kickstand revolute, board_to_clamp_{0,1} revolute knobs."
    - "B(002): board root + folding tripod front_leg_0/front_leg_1/rear_leg (revolute board_to_<leg>) each
       with prismatic <leg>_slide inner tube, FIXED brace, top_clamp_bar flip-chart holder, clamp knobs."
```

## Slots and Candidates
| slot | candidate | diversity_axis | source_type | evidence / record | status |
|---|---|---|---|---|---|
| support_base | rolling_h_base_casters | ① skeleton | origin_anchor | A (001): board_frame + sleeves + casters | converged |
| support_base | folding_tripod_3leg | ① skeleton | origin_anchor | B (002): 3 splayed folding+telescoping legs | converged |
| support_base | t_base_central_column_casters | ① skeleton | forked_anchor | fork@A → rec_..._var_base_tbase | planned |
| support_base | four_post_upright_frame | ① skeleton | forked_anchor | fork@A → rec_..._var_base_fourpost | planned |
| board_motion | static_framed_board | ② mechanism | origin_anchor | A & B fix panel to frame | converged |
| board_motion | revolving_double_sided | ② mechanism | forked_anchor | fork@A → rec_..._var_board_revolve | planned |
| board_motion | drafting_tilt_carriage | ② mechanism | forked_anchor | fork@A → rec_..._var_board_tilt | planned |
| board_motion | height_slide_carriage | ② mechanism | forked_anchor | fork@A → rec_..._var_board_slide | planned |
| leg_adjust | telescoping_prismatic | ② mechanism | origin_anchor | A lower_leg slide, B <leg>_slide | converged |
| leg_adjust | folding_revolute | ② mechanism | origin_anchor | B board_to_<leg>, A foot/rear hinges | converged |
| flip_chart_top | top_clamp_bar | ④/feature | origin_anchor | B top_clamp_bar + brackets | converged (no fork) |
| multiplicity_legs | n_legs {3,4} | N | origin_anchor + forked_anchor | B N=3; fork@B N=4 → rec_..._var_n4_legs | planned |

Every supported slot reaches ≥2 structurally distinct candidates: support_base(4), board_motion(4),
leg_adjust(2). Board body ③ (planar rectangle) has no second honest value → recorded, not forked.

## Six-Axis Diversity Audit
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / topology | source-backed (2 origin + 2 fork) | rolling_h_base(A) / folding_tripod(B) / t_base_column(fork) / four_post_frame(fork) |
| ② joint / mechanism | source-backed (origin + 3 fork) | telescope prismatic, fold revolute, caster continuous (origins); + board revolve, board drafting-tilt carriage, board vertical slide (forks) |
| ③ primary form family | record_only | writing panel is always a planar rectangular boundary; no honest 2nd body family → underfilled, not forked |
| ④ surface decoration | record_only / world_knowledge_extrapolation | marker tray + eraser rest, red magnet caps (B), top flip-chart clamp bar, brand decal, gridlines. Companion-only, never standalone. |
| ⑤ proportion / size / travel | record_only | board 0.68–0.82 W × 1.00–1.05 H portrait (H/W>1.3); leg telescope travel 0.08–0.18; fold 0.0–1.1 rad; tilt 0.0–1.4 rad; revolve ±π; caster continuous. |
| ⑥ material / palette / finish | record_only | powder-coated blue(A) / satin aluminium+grey(B) / white powder tube / black rubber / red magnet caps; extrapolate black, silver, coloured frames. |

## Multiplicity / Copy Logic
- count_param: `n_legs` (number of splayed folding+telescoping support legs on the tripod family).
- N samples: 3 (origin B) and 4 (fork `rec_whiteboard_easel_var_n4_legs`).
- suggested N_range: [3, 4] (portable folding easels are physically tripod or quad; higher counts are
  not real for this class).
- copied object: the origin-B leg subassembly — outer part `front_leg_i` (via `_add_outer_leg`) +
  `board_to_<leg>` REVOLUTE fold + child `<leg>_lower` (via `_add_inner_leg`) + `<leg>_slide` PRISMATIC.
- naming: `leg_{i}` / `leg_{i}_lower`, joints `board_to_leg_{i}`, `leg_{i}_slide`.
- placement_rule: radial splay from board underside on a regular ring/rectangle (2 front + 2 rear).
- joint_policy: each copied leg keeps its own revolute fold + prismatic telescope; no shared joint.

## Budget Decision
- Band: simple, chosen at low end (8 anchors). Coverage-first, no padding.
- Counted anchors: origins A, B + 6 forks (2 ① support, 3 ② board-motion, 1 N legs).
- Not counted: ④/⑤/⑥ records, flip_chart_top feature (already origin-shown), any probe.
- underfilled_reason: The board body (axis ③) is intrinsically a single planar-rectangle family, so it
  yields no second structural candidate; honest structural diversity lives only in support_base (①) and
  board_motion (②), which are fully covered. No compatibility probes are warranted — each fork changes a
  single interface with low clash risk against a rigid framed board, so the pool sits at the simple-band
  low end rather than being padded upward.

## Variant Cards
```yaml
- variant_id: rec_whiteboard_easel_var_base_tbase
  source_type: forked_anchor
  parent_record_id: A (rec_workspace__whiteboard_easel__001...)
  positioning: {product_archetype: mobile single-column flip/whiteboard easel on a star caster base,
    why_same_subcategory: same framed dry-erase board + marker tray raised to writing height on a rolling floor stand}
  primary_axis: {slot: support_base, diversity_axis: ①, target_candidate: t_base_central_column_casters}
  structural_delta:
    change: [replace the two telescoping side sleeves/legs and H-runner base with ONE central vertical
             mast column standing on a 3-or-4-arm star/cross floor base; casters at each arm end]
    keep_parts: [board_frame, white_surface, top_rail, bottom_rail, marker_tray_shelf, tray_back_lip,
                 board_to_clamp_i, caster_i_j (rubber_wheel/hub_cap/axle_pin), foot_to_caster continuous]
    joint_policy: keep continuous casters; column-to-board height stays a single prismatic on the mast
    interface_policy: board hangs off the mast via a rigid bracket; star arms are fixed to the column foot
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: radial}
  companion_variations: {allowed_④⑤⑥: [palette, mast/base proportion], forbidden: [add tripod legs, sign holder drift]}
  acceptance_focus: [casters continuous-spin, board reads centred over single column, marker tray at lower edge]

- variant_id: rec_whiteboard_easel_var_base_fourpost
  source_type: forked_anchor
  parent_record_id: A
  positioning: {product_archetype: classroom reversible whiteboard on a rigid four-post upright floor frame,
    why_same_subcategory: framed dry-erase board + tray on a self-supporting floor stand}
  primary_axis: {slot: support_base, diversity_axis: ①, target_candidate: four_post_upright_frame}
  structural_delta:
    change: [replace wheeled H-base + telescoping sleeves with four straight vertical tubular posts arranged
             in a rectangle, tied by lower and upper crossbars into a closed ladder frame with floor glides/feet]
    keep_parts: [board_frame, white_surface, top_rail, bottom_rail, side_0_rail, side_1_rail, lower_crossbar,
                 crossbar_mount_i, marker_tray_shelf, tray_back_lip, board_to_clamp_i]
    joint_policy: rigid frame; keep the two clamp knob revolutes; legs are fixed (static support), casters optional
    interface_policy: board frame bolts between the two front posts; crossbars fix rear posts
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: rectangular}
  companion_variations: {allowed_④⑤⑥: [palette, post gauge], forbidden: [folding tripod splay, wheel-only base]}
  acceptance_focus: [four posts reach floor, frame rigid & non-floating, board framed across width]

- variant_id: rec_whiteboard_easel_var_board_revolve
  source_type: forked_anchor
  parent_record_id: A
  positioning: {product_archetype: revolving double-sided mobile whiteboard easel,
    why_same_subcategory: same rolling stand + framed board, board now reversible instead of fixed}
  primary_axis: {slot: board_motion, diversity_axis: ②, target_candidate: revolving_double_sided}
  structural_delta:
    change: [make the panel double-sided (writing surface on both faces) and mount it on a horizontal
             trunnion pivot between the two upright side posts so it revolves/flips; clamp knobs become pivot locks]
    keep_parts: [board_frame, white_surface, top_rail, bottom_rail, side_0_rail, side_1_rail, marker_tray_shelf,
                 lower_leg_i, board_to_lower_leg_i prismatic, foot_i, caster_i_j, foot_to_caster continuous]
    joint_policy: ADD one horizontal-axis revolute base_to_board pivot (±pi); keep clamp revolutes as detents
    interface_policy: trunnion stubs on both side rails ride in yoke bearings on the two posts
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [tilt-only limit change, remove marker tray]}
  acceptance_focus: [board revolves ~pi about horizontal axis, both faces are writable, pivot on both posts]

- variant_id: rec_whiteboard_easel_var_board_tilt
  source_type: forked_anchor
  parent_record_id: A
  positioning: {product_archetype: adjustable drafting-tilt easel (vertical writing to near-flat drawing),
    why_same_subcategory: same framed dry-erase board + tray + floor stand, board on a tilt carriage}
  primary_axis: {slot: board_motion, diversity_axis: ②, target_candidate: drafting_tilt_carriage}
  structural_delta:
    change: [insert a NEW tilt_carriage bracket part between the mast/frame and the board; board pivots on it
             from upright toward horizontal (0 to ~1.4 rad) with a detent strut/arc so it locks at drafting angles]
    keep_parts: [board_frame, white_surface, top_rail, bottom_rail, marker_tray_shelf, tray_back_lip,
                 lower_leg_i, board_to_lower_leg_i prismatic, caster_i_j, board_to_clamp_i]
    joint_policy: ADD one revolute board_to_carriage (0..~1.4 rad) with a support arc/strut; NOT merely wider clamp limits
    interface_policy: tilt carriage is a real bracket fixed to the mast tops; board hinges at its top edge onto the carriage
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [double-sided flip, replacing base skeleton]}
  acceptance_focus: [distinct tilt carriage part exists, board tilts forward and is supported by strut, not floating]

- variant_id: rec_whiteboard_easel_var_board_slide
  source_type: forked_anchor
  parent_record_id: A
  positioning: {product_archetype: height-adjustable board that slides up/down on fixed masts,
    why_same_subcategory: same framed board + tray, adjustment moves the board rather than the legs}
  primary_axis: {slot: board_motion, diversity_axis: ②, target_candidate: height_slide_carriage}
  structural_delta:
    change: [make the two side masts fixed-height and mount the board frame on a prismatic vertical carriage
             that slides along the masts; reuse the square sleeve/collar rail vocabulary as the board rail]
    keep_parts: [_add_square_sleeve sleeves, upper_collar/lower_collar bands, clamp_shoe, board_frame,
                 white_surface, marker_tray_shelf, board_to_clamp_i, lower_crossbar, caster_i_j]
    joint_policy: ADD one prismatic board_to_carriage vertical slide; legs no longer telescope (masts fixed)
    interface_policy: board carriage captured by the two mast rails; clamp knobs act as height locks
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [palette, travel within record range], forbidden: [tilt, revolve, tripod base]}
  acceptance_focus: [board translates vertically on masts, stays captured on rails at both extremes]

- variant_id: rec_whiteboard_easel_var_n4_legs
  source_type: forked_anchor
  parent_record_id: B (rec_workspace__whiteboard_easel__002...)
  positioning: {product_archetype: heavy-duty four-leg folding flip-chart / whiteboard easel,
    why_same_subcategory: identical tripod easel with one extra support leg for stability}
  primary_axis: {slot: multiplicity_legs, diversity_axis: N, target_candidate: n_legs=4}
  structural_delta:
    change: [change leg count from 3 to 4 by extending the hinge_points/foot_targets loop; keep the exact
             folding+telescoping leg subassembly and copy logic; place legs as 2 front + 2 rear splay]
    keep_parts: [board, brace, _add_outer_leg, _add_inner_leg, board_to_<leg> revolute, <leg>_slide prismatic,
                 clamp_i, top_clamp_bar, marker_tray_base]
    joint_policy: each of the 4 legs keeps its own revolute fold + prismatic telescope (loop-emitted)
    interface_policy: hinge blocks/pins regenerated per leg on a regular rectangular footprint
  multiplicity: {applies: true, target_n: 4, copied_object: leg subassembly (outer+lower+fold+slide),
    placement_rule: radial/rectangular splay 2 front + 2 rear}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [change board motion, change leg geometry/type]}
  acceptance_focus: [4 loop-emitted legs each fold+telescope, regular indexed names, all feet reach floor]
```

## Blocked / Excluded
- board body ③ second form family — blocked: whiteboard panel is intrinsically a planar rectangle; no
  honest volumetric/alternate boundary exists in-category (a curved/round board drifts toward sign/decor).
- board_tilt reframed as pure limit widening — excluded: a bare wider-range clamp revolute would be a ⑤
  travel change only; the accepted `board_tilt` fork must add a real tilt_carriage part + support strut.
- caster-count N-sweep — excluded: caster count does not expose new copy logic beyond the leg-count N axis.
- wall-mount / tabletop / sign-holder / drafting-desk forms — blocked: out-of-subcategory neighbors.
