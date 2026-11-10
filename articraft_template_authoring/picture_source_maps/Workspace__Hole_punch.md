# Source Map — Workspace / Hole punch

slug `hole_punch` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_chrome-plier-style-single-hole-punch-two-polishe_20260708_082409_296179_850c1c69` — picture/Workspace/Hole punch/001.png
- `rec_workspace__hole_punch__002_png_3283eefd8c2849d9b48921e4e76ad964` — picture/Workspace/Hole punch/002.png

## Variants generated this batch (6 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_hole_punch_var_mechanism_plunger` | mechanism_plunger | PASS | 1 | 1 |
| `rec_hole_punch_var_n3` | n3 | PASS | 1 | 0 |
| `rec_hole_punch_var_n4` | n4 | PASS | 1 | 0 |
| `rec_hole_punch_var_probe_adjustable` | probe_adjustable | PASS | 5 | 0 |
| `rec_hole_punch_var_skeleton_lever_carriage` | skeleton_lever_carriage | PASS | 2 | 1 |
| `rec_hole_punch_var_skeleton_sprung_loop` | skeleton_sprung_loop | PASS | 1 | 0 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Workspace / Hole punch (slug `hole_punch`)

pattern: **mixed** (two distinct origin skeletons: handheld plier-scissor vs desktop base+lever; multiplicity N over punch-pin/die pairs)
richness band: **simple** (target low end; see underfilled_reason)
counted candidate anchors: **7** (2 origins + 5 forks); +1 compatibility_probe (not counted)
fork jobs emitted: **6** (5 counted forks + 1 probe)

## subcategory_contract
```yaml
subcategory_contract:
  category: Workspace
  subcategory: Hole punch
  core_identity: A hand tool that perforates sheets of paper by driving one or more punch pins straight through the paper into matching dies, actuated by a single hand squeeze/press DOF, producing round holes and collecting the chads.
  must_keep:
    - one or more punch pins aligned to matching die bores/anvils
    - a single press/squeeze articulation (revolute or prismatic) that drives the pins into the dies
    - an open paper throat/slot gap at rest that closes on actuation
    - a chad/confetti path or waste window
  must_not_become:
    - eyelet / grommet setter
    - stapler
    - pliers / wire cutter
    - paper trimmer / guillotine
    - drill / hole saw / bench press-drill
    - comb / spiral binding machine
  image_evidence:
    - 001: two handheld metal punches — a plier/scissor crossed-arm punch (central rivet, jaws + single die/pin) and a spring loop-handle one-hand squeeze punch with a knurled grip and a row of chad-drain holes
    - 002: blue desktop punch — flat rubber-footed base, rear-hinged top pressing lever, punch head pressing down into die(s) in the base
  parent_evidence:
    - A (plier): parts `frame` (fixed arm) + `punch_lever` (moving arm) crossing at `rivet_shaft`; revolute `punch_stroke` (axis Y) drops `punch_pin` into `die_block` bore; single hole; `_bar`/`_boss`/`_grip_solid` helpers; knurled grips
    - B (desktop): `base` (rubber_pad, blue shell, die_ring/die_hole/die_boss ×2, paper_throat_gap, rear_hinge_block, hinge_barrel) + `pressing_lever` hinged by revolute `lever_pivot` at rear; two `punch_pin_{i}` FIXED to lever via `lever_to_pin_{i}`; loop-based pin/die emission (N=2)
```

## Slots and Candidates
| slot | candidate | axis | source_type | record / evidence | status |
|---|---|---|---|---|---|
| body_form / skeleton | plier scissor crossed-arm (central rivet) | ① | origin_anchor | A (001 left) | converged |
| body_form / skeleton | desktop base + rear-hinged pressing lever | ① | origin_anchor | B (002) | converged |
| body_form / skeleton | sprung C-loop one-hand squeeze (front pivot, rear spring loop) | ① | forked_anchor | fork@A `rec_hole_punch_var_skeleton_sprung_loop` (001 right) | planned |
| body_form / skeleton | compound top lever + sliding plunger carriage | ① | forked_anchor | fork@B `rec_hole_punch_var_skeleton_lever_carriage` | planned |
| actuation mechanism | revolute press/squeeze pivot | ② | origin_anchor | A `punch_stroke`, B `lever_pivot` | converged |
| actuation mechanism | prismatic straight-down plunger (no lever) | ② | forked_anchor | fork@B `rec_hole_punch_var_mechanism_plunger` | planned |
| multiplicity (N holes) | N=1 | N | origin_anchor | A | converged |
| multiplicity (N holes) | N=2 | N | origin_anchor | B | converged |
| multiplicity (N holes) | N=3 | N | forked_anchor | fork@B `rec_hole_punch_var_n3` | planned |
| multiplicity (N holes) | N=4 | N | forked_anchor | fork@B `rec_hole_punch_var_n4` | planned |
| head positioning | adjustable sliding heads on Y rail | probe | compatibility_probe | fork@B `rec_hole_punch_var_probe_adjustable` | probe (not counted) |

Every supported slot reaches ≥2 structurally distinct candidates: skeleton ×4, mechanism ×2 (revolute/prismatic), N ×4 {1,2,3,4}.

## Six-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | candidate-anchor (source-backed) | plier-scissor (A), desktop base+rear-lever (B), sprung-loop (fork@A), compound lever+plunger-carriage (fork@B) |
| ② joint / mechanism | candidate-anchor (source-backed) | revolute pivot (A `punch_stroke`, B `lever_pivot`); prismatic plunger (fork@B); compound revolute+prismatic (lever-carriage fork) |
| ③ primary form family | source-backed via ①; not a separate fork | handheld frame vs desktop slab body are carried by the skeleton forks; no independent ③ vocabulary exists that isn't already a skeleton or ④/⑤ delta |
| ④ surface decoration | record_only / world_knowledge_extrapolation | die-hole shape (round vs shaped ticket-punch die), knurled grip pattern, chad-drain hole rows, blue highlight/shadow channels, screw heads — companion only |
| ⑤ proportion / size / travel | record_only | throat depth (short handheld ~26 mm reach vs long-reach), lever length, pin Ø ~2.8–3.6 mm, stroke ~0.14 rad / plunger travel; may ride as companion |
| ⑥ material / palette / finish | record_only | polished chrome / nickel (A, 001 right), blue painted metal (B), black rubber pad/foot, brushed steel dies — companion only |

## Multiplicity / Copy Logic
- count_param: number of punch-pin + matching die (`die_ring`/`die_hole`/`die_boss`) pairs, driven by the parent `for index, y in enumerate(...)` pin loop and paired die emission in `base`.
- N samples (source-backed): N=1 (A), N=2 (B origin), N=3 (fork@B), N=4 (fork@B).
- suggested N_range: [1, 4] (real office standards 1/2/3/4 hole; not beyond 4 for hand punches).
- copied object: `punch_pin_{i}` (pin + top cap + cutting tip) FIXED to lever via `lever_to_pin_{i}`, plus matching `die_ring_{i}`/`die_hole_{i}`/`die_boss_{i}` in base.
- placement: linear row along Y, equal spacing at realistic hole standards; N=4 widens base+lever along Y.
- joint policy: one FIXED `lever_to_pin_{i}` per pin under a single shared revolute `lever_pivot`; multiplicity forks change only count/spacing, not skeleton/mechanism.

## Budget decision
Simple band (8–12). Honest counted anchors = 7, just below the floor.
underfilled_reason: A hole punch is a single-DOF squeeze/press tool with limited structural vocabulary. The complete honest structural space is 4 skeletons (plier-scissor, desktop rear-lever, sprung-loop, compound lever+carriage), 2 mechanisms (revolute vs prismatic plunger), and an N-sweep {1,2,3,4}. Reaching 8+ would require padding with ④ die-shape / ⑤ throat-length / ⑥ palette variants, which the rules forbid as standalone anchors. One compatibility_probe (adjustable sliding heads on a rail) is added for the genuinely risky N-plus-rail interface but is not counted toward the budget.

## Variant Cards
```yaml
- variant_id: rec_hole_punch_var_skeleton_sprung_loop
  source_type: forked_anchor
  parent_record_id: rec_chrome-plier-style-single-hole-punch-two-polishe_20260708_082409_296179_850c1c69  # A
  positioning: {product_archetype: one-hand spring-return handheld loop-handle punch (001 right), why_same_subcategory: single pin into die via squeeze DOF, still perforates paper}
  primary_axis: {slot: body_form, diversity_axis: ①, target_candidate: sprung_C_loop_front_pivot}
  structural_delta:
    change: [move pivot to front working head, join rear grips with a continuous spring-steel loop bridge instead of a central crossing rivet]
    keep_parts: [frame, punch_lever, punch_stroke, die_block, punch_pin]
    joint_policy: preserve one revolute squeeze DOF at the head
    interface_policy: front pivot + elastic loop return; pin/die bore alignment kept
  multiplicity: {applies: true, target_n: 1, copied_object: punch_pin, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [chrome vs nickel palette], forbidden: [category drift, added holes, desktop base]}
  acceptance_focus: [pin enters die bore on squeeze, open paper slot at rest, loop frame reads as one connected part]

- variant_id: rec_hole_punch_var_skeleton_lever_carriage
  source_type: forked_anchor
  parent_record_id: rec_workspace__hole_punch__002_png_3283eefd8c2849d9b48921e4e76ad964  # B
  positioning: {product_archetype: heavy-duty office punch with long lever + spring-return plunger bar, why_same_subcategory: same base+dies, pins still driven into dies}
  primary_axis: {slot: body_form, diversity_axis: ①, target_candidate: compound_lever_plus_sliding_carriage}
  structural_delta:
    change: [insert plunger_carriage on a vertical prismatic guide, re-parent pins FIXED to carriage, lever pushes carriage via cam/contact]
    keep_parts: [base, pressing_lever, lever_pivot, punch_pin_{i}, die_ring_{i}, die_hole_{i}, rubber_pad, paper_throat_gap]
    joint_policy: preserve revolute lever_pivot; add exactly one carriage prismatic guide
    interface_policy: lever cam contacts carriage top; carriage slides straight down; pins straight into dies
  multiplicity: {applies: true, target_n: 2, copied_object: punch_pin, placement_rule: linear_row_Y}
  companion_variations: {allowed_④⑤⑥: [lever length, palette], forbidden: [hole-count change, handheld frame swap]}
  acceptance_focus: [pins travel straight down not on arc, carriage guided not floating, pin/die alignment through travel]

- variant_id: rec_hole_punch_var_mechanism_plunger
  source_type: forked_anchor
  parent_record_id: rec_workspace__hole_punch__002_png_3283eefd8c2849d9b48921e4e76ad964  # B
  positioning: {product_archetype: push-plunger / palm-press single-hole craft punch, why_same_subcategory: pin into die, single press DOF}
  primary_axis: {slot: actuation_mechanism, diversity_axis: ②, target_candidate: prismatic_vertical_plunger}
  structural_delta:
    change: [replace revolute lever_pivot with a prismatic plunger_head on +Z guide column, re-parent pin FIXED to plunger, spring-return travel]
    keep_parts: [base, punch_pin, die_ring, die_hole, rubber_pad, paper_throat_gap, side_waste_window]
    joint_policy: replace the single primary revolute with a single prismatic joint
    interface_policy: plunger slides in vertical guide column; pin descends into die bore
  multiplicity: {applies: true, target_n: 1, copied_object: punch_pin, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [button-cap knurl, palette], forbidden: [rotating lever, added holes, drill/press-drill drift]}
  acceptance_focus: [pin descends vertically into bore under prismatic travel, no rotating lever, guide column supports plunger]

- variant_id: rec_hole_punch_var_n3
  source_type: forked_anchor
  parent_record_id: rec_workspace__hole_punch__002_png_3283eefd8c2849d9b48921e4e76ad964  # B
  positioning: {product_archetype: US 3-hole office punch, why_same_subcategory: same skeleton/mechanism, more holes}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: 3}
  structural_delta:
    change: [set hole count to 3 via existing loops, three pin/die pairs in a linear Y row at 3-hole spacing]
    keep_parts: [base, pressing_lever, lever_pivot, punch_pin_{i}, lever_to_pin_{i}, die_ring_{i}, die_hole_{i}, die_boss_{i}]
    joint_policy: one FIXED lever_to_pin per pin under one shared revolute lever_pivot
    interface_policy: each pin aligned to its die bore
  multiplicity: {applies: true, target_n: 3, copied_object: punch_pin+die_triplet, placement_rule: linear_row_Y_equal_spacing}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [skeleton/mechanism change, hand-written repeats, binder-machine drift]}
  acceptance_focus: [3 pins loop-emitted, all aligned to dies, single lever drives all]

- variant_id: rec_hole_punch_var_n4
  source_type: forked_anchor
  parent_record_id: rec_workspace__hole_punch__002_png_3283eefd8c2849d9b48921e4e76ad964  # B
  positioning: {product_archetype: A4 4-hole binder punch, why_same_subcategory: same skeleton/mechanism, more holes}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: 4}
  structural_delta:
    change: [set hole count to 4 via existing loops, four pin/die pairs in a linear Y row, widen base+lever along Y]
    keep_parts: [base, pressing_lever, lever_pivot, punch_pin_{i}, lever_to_pin_{i}, die_ring_{i}, die_hole_{i}, die_boss_{i}]
    joint_policy: one FIXED lever_to_pin per pin under one shared revolute lever_pivot
    interface_policy: each pin aligned to its die bore
  multiplicity: {applies: true, target_n: 4, copied_object: punch_pin+die, placement_rule: linear_row_Y_equal_spacing}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [skeleton/mechanism change, hand-written repeats, comb/spiral binder drift]}
  acceptance_focus: [4 pins loop-emitted, base spans row, all aligned to dies]

- variant_id: rec_hole_punch_var_probe_adjustable
  source_type: compatibility_probe
  parent_record_id: rec_workspace__hole_punch__002_png_3283eefd8c2849d9b48921e4e76ad964  # B
  positioning: {product_archetype: adjustable-spacing desktop punch (repositionable heads), why_same_subcategory: heads still press pins into dies}
  primary_axis: {slot: head_positioning, diversity_axis: probe, target_candidate: sliding_heads_on_Y_rail}
  structural_delta:
    change: [add Y prismatic adjustment rail carrying each punch/die head module combined with the press DOF]
    keep_parts: [base, pressing_lever, lever_pivot, punch_pin_{i}, die_ring_{i}, die_hole_{i}, rubber_pad, paper_throat_gap]
    joint_policy: press revolute retained; add per-head Y prismatic adjustment
    interface_policy: sliding head stays aligned to its die across rail range, retains press clearance
  multiplicity: {applies: true, target_n: 2, copied_object: head_module, placement_rule: rail_Y}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [dropping press DOF, comb-binder drift, hand-written repeats]}
  acceptance_focus: [pin/die alignment at rail extremes, no neighbor/lever collision, press travel preserved]
```

## Blocked / Excluded
- screw-press / rotary-drive punch (② screw mechanism, scrapbook screw punch / paper drill): not cleanly representable as a single URDF joint (helical drive) and drifts toward the drill/press-drill neighbor — blocked/gated.
- ticket / shaped-hole conductor punch: die-hole shape is ④ surface decoration, not a structural anchor — record_only.
- long-reach / long-throat variants: ⑤ proportion only — record_only, not a standalone anchor.
- N>4 hand punches: not a real standard for hand punches; would be padding — excluded.
```
