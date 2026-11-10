# Source Map — Workspace / Laptop stand

slug `laptop_stand` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_foldable-adjustable-aluminum-laptop-stand-with-s_20260708_044924_835691_defb8533` — picture/Workspace/Laptop stand/002.png
- `rec_workspace__laptop_stand__001_png_bcafa993ed154935b4625385f533ddc9` — picture/Workspace/Laptop stand/001.png

## Variants generated this batch (6 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_laptop_stand_var_mechanism_prismatic_post` | mechanism_prismatic_post | PASS | 3 | 1 |
| `rec_laptop_stand_var_mechanism_prop_leg` | mechanism_prop_leg | PASS | 1 | 1 |
| `rec_laptop_stand_var_n9_vents` | n9_vents | PASS | 4 | 1 |
| `rec_laptop_stand_var_skeleton_center_column` | skeleton_center_column | PASS | 3 | 1 |
| `rec_laptop_stand_var_skeleton_scissor_lift` | skeleton_scissor_lift | PASS | 5 | 1 |
| `rec_laptop_stand_var_skeleton_wedge` | skeleton_wedge | PASS | 2 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Workspace / Laptop stand — variant plan

pattern: **parallel_children** (each origin = a base/support root carrying independent articulated risers/arms; ventilation-slot multiplicity on the support surface)
richness band: **simple** (target low end; laptop-stand structural vocabulary is modest)
candidate anchors: **8** (2 origins + 6 forks)
fork jobs emitted: **6**

## subcategory_contract
```yaml
subcategory_contract:
  category: Workspace
  subcategory: Laptop stand
  core_identity: A desk device that lifts a laptop off the desk to an ergonomic height/angle, with a laptop-scale support surface and a front retaining lip/hook.
  must_keep:
    - laptop-scale inclined or elevated support surface (rails/tray/plate)
    - front retaining lip or hook so the laptop cannot slide off
    - grounded, self-supporting footprint (feet or broad base)
    - at least one real height/tilt/rotation articulation (unless explicitly static_only)
  must_not_become:
    - Monitor stand / monitor arm / VESA pole mount
    - Tablet / phone easel or dock
    - Desk / table / lap desk
    - Book / document stand
    - Cooling pad / fan tray
  image_evidence:
    - "002.png: portable foldable X-frame aluminum stand; twin slotted rails with rubber feet; angled ratcheted uprights + crossing brace struts (X silhouette); upturned front hooks; folds flat into a pouch."
    - "001.png: sit-stand riser on a broad rotating (360deg) base; perforated side arms lift a tray; front clamp lips grip a MacBook; height + tilt + rotate."
  parent_evidence:
    - "A: base_rail_0/1 (lightening-slot bars, rubber feet, hinge lugs); upright_0/1 (ratchet slots, rubber pads); brace_strut_0/1; front_hook_0/1 (hook_bracket + rubber_saddle); 4 REVOLUTE fold joints (upright_pitch_*, strut_pitch_*); _lightening_slot_bar loop over cuts."
    - "B: base (rounded plate + grooves); turntable (disk/pedestal, CONTINUOUS turntable_yaw); link_arms (paired perforated side_arm segments, base/tray shafts, pivot washers, REVOLUTE arm_pitch); upper_tray (laptop_plate, front_lip, lip_foot, REVOLUTE tray_tilt)."
```

## Slot / candidate grid
| slot | candidate | axis | source_type | evidence | status |
|---|---|---|---|---|---|
| support_skeleton | foldable X-frame prop (crossed uprights+struts) | ① | origin_anchor | A | converged |
| support_skeleton | pedestal + inclined arm-linkage riser | ① | origin_anchor | B | converged |
| support_skeleton | scissor / pantograph vertical lift | ① | forked_anchor | fork scissor_lift (from B) | planned |
| support_skeleton | single central cantilever spine | ① | forked_anchor | fork center_column (from B) | planned |
| body_form | solid volumetric inclined wedge (closed shell) | ③ | forked_anchor | fork skeleton_wedge (from A), static_only | planned |
| adjust_mechanism | multi-position fold revolutes (tilt) | ② | origin_anchor | A (4 revolute) | converged |
| adjust_mechanism | continuous base yaw + arm/tray revolute | ② | origin_anchor | B (turntable_yaw + 2 revolute) | converged |
| adjust_mechanism | single rear prop-leg (kickstand) revolute | ② | forked_anchor | fork prop_leg (from A) | planned |
| adjust_mechanism | telescoping prismatic height post | ② | forked_anchor | fork prismatic_post (from B) | planned |
| support_or_base | twin slotted rails on rubber feet (open) | ①/base | origin_anchor | A | converged |
| support_or_base | broad rounded rotating base plate | ①/base | origin_anchor | B | converged |
| front_retainer | upturned front hook lip | retainer | origin_anchor | A (hook_bracket) | converged (2 cands, no fork) |
| front_retainer | front clamp lip + saddle | retainer | origin_anchor | B (front_lip/lip_foot) | converged |
| multiplicity | ventilation louver/slot count | N | origin_anchor + forked_anchor | A N=5; fork N=9 | planned |

Each supported slot reaches >=2 structurally distinct candidates.

## Mandatory 6-axis diversity audit
| axis | candidate-anchor status | treatment | values |
|---|---|---|---|
| ① skeleton / topology | candidate-anchor | source-backed | fold-X prop (A) · arm-linkage riser (B) · scissor pantograph lift (fork) · single central spine (fork) |
| ② joint / mechanism | candidate-anchor | source-backed | 4 fold revolute (A) · continuous yaw+2 revolute (B) · single prop-leg revolute (fork) · prismatic height post (fork) |
| ③ primary form family | candidate-anchor | source-backed | open bar-linkage frame (A) · tray-on-arm (B) · closed volumetric inclined wedge/shell (fork, static_only) |
| ④ surface decoration | record_only / companion | not standalone | lightening/vent slots, rail grooves, rubber pads/saddles, ratchet buttons; world_knowledge_extrapolation: brand decal, mesh-vent field |
| ⑤ proportion / size / travel | record_only | not candidate anchor | tilt fold ~0..1.55 rad; arm_pitch ±0.45; tray_tilt -0.35..0.65; yaw continuous; riser height ~4-16 cm; laptop plate ~0.30x0.22 m |
| ⑥ material / palette / finish | record_only | not candidate anchor | brushed silver aluminum · matte/soft/groove black · satin pivot hardware · laptop silver; palette space: silver / space-grey / black / white |

①②③ and N are source-backed. ④⑤⑥ are record_only/companion — never standalone variants, never counted toward the budget.

## Multiplicity / copy-logic plan
- count_param: ventilation-slot count in the `base_cuts` tuple fed to `_lightening_slot_bar` (loop over `cuts`).
- N samples: **N=5** (origin A) and **N=9** (fork `n9_vents`). Two representative samples.
- suggested N_range: ~[3, 13].
- copied object: one through-slot cut (rounded/rect); naming: indexed slot cuts within the rail loop.
- placement: evenly spaced along rail long axis.
- joint policy: FIXED decorative through-cuts (no articulation change).

## Budget decision
- Richness = simple (8-12). Chosen total candidate anchors = **8** (low end), coverage-first, no padding.
- 2 origins + 6 forks: skeleton_wedge (③), prop_leg (②), prismatic_post (②), scissor_lift (①), center_column (①), n9_vents (N).
- `underfilled_reason`: none required (8 honest anchors reached). Deliberately not padded past 8 — additional laptop-stand forms would be ④/⑤/⑥ cosmetic (finish, vent pattern) or drift toward neighbor categories.
- Blocked / excluded: **vertical clamshell dock** — drifts toward a Laptop dock/holder neighbor (stores a closed laptop on edge rather than presenting it for use); excluded to protect subcategory identity. Pure cosmetic finish/color and vent-pattern-only variants excluded (⑥/④ only).

## Variant cards
```yaml
- variant_id: rec_laptop_stand_var_skeleton_wedge
  source_type: forked_anchor
  parent_record_id: rec_foldable-adjustable-aluminum-laptop-stand-with-s_...defb8533 (A)
  positioning: {product_archetype: fixed aluminum incline riser (mStand), why_same_subcategory: inclined laptop support surface + front lip + ventilation, elevated}
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: solid volumetric inclined wedge/shell}
  structural_delta:
    change: [replace fold linkage + 4 revolutes with one rigid ventilated wedge (top panel + solid side walls + footed base)]
    keep_parts: [front_hook/hook_bracket, rubber_saddle, rail_foot, _lightening_slot_bar ventilation, brushed_silver_aluminum]
    joint_policy: static_only (all fixed)
    interface_policy: front lip at low edge; rubber feet under base
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_456: [vent slot pattern, aluminum finish], forbidden: [fold/scissor/telescoping joints, category drift]}
  acceptance_focus: [static_only accepted, closed volumetric body, front lip present]

- variant_id: rec_laptop_stand_var_mechanism_prop_leg
  source_type: forked_anchor
  parent_record_id: A
  positioning: {product_archetype: thin folding kickstand laptop stand, why_same_subcategory: inclined ventilated surface + front lip, tilt-adjustable}
  primary_axis: {slot: adjust_mechanism, diversity_axis: ②, target_candidate: single rear prop-leg revolute}
  structural_delta:
    change: [one flat inclined tray + single width-spanning rear leg on ONE revolute setting tilt/height]
    keep_parts: [ventilated rails via _lightening_slot_bar, front_hook, rail_foot, hinge_boss/hinge_pin, materials]
    joint_policy: replace 4 fold revolutes with exactly one prop-leg revolute
    interface_policy: front edge on ground via hook lip; rear lifted by leg
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_456: [vent pattern, finish], forbidden: [scissor/telescoping/rotating joints, second leg pair]}
  acceptance_focus: [exactly one non-fixed joint, leg actually sets tilt]

- variant_id: rec_laptop_stand_var_mechanism_prismatic_post
  source_type: forked_anchor
  parent_record_id: rec_workspace__laptop_stand__001_png_...bcafa993 (B)
  positioning: {product_archetype: sit-stand telescoping riser, why_same_subcategory: base + tray holding laptop, height-adjustable}
  primary_axis: {slot: adjust_mechanism, diversity_axis: ②, target_candidate: prismatic vertical height post}
  structural_delta:
    change: [replace arm links + arm_pitch revolute with outer post + inner slider on ONE prismatic joint]
    keep_parts: [base/base_plate/grooves, upper_tray/front_lip/lip_foot/laptop_plate, turntable_yaw, tray_tilt, _rounded_plate_mesh]
    joint_policy: replace arm_pitch revolute with one prismatic; keep yaw + tray_tilt
    interface_policy: visible telescoping tube nesting; tray on inner slider
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_456: [base finish/proportion], forbidden: [monitor pole mount, fold flat, scissor bars]}
  acceptance_focus: [real prismatic travel raises tray, tube nesting reads captured]

- variant_id: rec_laptop_stand_var_skeleton_scissor_lift
  source_type: forked_anchor
  parent_record_id: B
  positioning: {product_archetype: scissor-lift sit-stand riser, why_same_subcategory: base + level tray holding laptop, height-adjustable}
  primary_axis: {slot: support_skeleton, diversity_axis: ①, target_candidate: double-X pantograph scissor lift}
  structural_delta:
    change: [two crossed link pairs (X pantograph) between base and tray, loop-emitted; driving revolute + top slider keep tray level]
    keep_parts: [base/base_plate, upper_tray/front_lip/lip_foot/laptop_plate, pivot washers/shafts, tray_tilt, materials]
    joint_policy: replace single arm linkage with coupled scissor revolutes (one driving) + leveling slider
    interface_policy: crossed links pinned at shared pivots; tray carried level
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: loop-emitted crossed links}
  companion_variations: {allowed_456: [finish/proportion], forbidden: [collapse into fold-flat X-prop, jack/cart/desk]}
  acceptance_focus: [vertical level lift, loop-emitted links, distinct from origin A fold-X]

- variant_id: rec_laptop_stand_var_skeleton_center_column
  source_type: forked_anchor
  parent_record_id: B
  positioning: {product_archetype: single-column cantilever riser, why_same_subcategory: base + tray holding laptop, height/tilt adjustable}
  primary_axis: {slot: support_skeleton, diversity_axis: ①, target_candidate: single central cantilever spine}
  structural_delta:
    change: [collapse twin side arms into one central column/shaft; single central base yoke + single central tray lug; tray cantilevered from centerline]
    keep_parts: [base/base_plate, turntable_yaw/short_pedestal, upper_tray/front_lip/lip_foot/laptop_plate, arm_pitch, tray_tilt, materials]
    joint_policy: keep arm_pitch + tray_tilt on the single spine; keep yaw
    interface_policy: single central load path, sides open
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_456: [finish/proportion], forbidden: [monitor arm/VESA, prismatic/scissor swap, desk]}
  acceptance_focus: [single central support carries tray, sides open, joints preserved]

- variant_id: rec_laptop_stand_var_n9_vents
  source_type: forked_anchor
  parent_record_id: A
  positioning: {product_archetype: same fold stand, denser cooling louvers, why_same_subcategory: identical laptop stand}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: 9 ventilation slots per rail}
  structural_delta:
    change: [regenerate base_cuts loop with N=9 evenly spaced through-slots (origin N=5)]
    keep_parts: [base_rail_0/1, upright_0/1, brace_strut_0/1, front_hook, all 4 fold joints, _lightening_slot_bar]
    joint_policy: preserve (no joint change)
    interface_policy: evenly spaced FIXED through-cuts along rail length
  multiplicity: {applies: true, target_n: 9, copied_object: rail through-slot, placement_rule: even spacing along rail long axis}
  companion_variations: {allowed_456: [], forbidden: [body/joint/feet/retainer change, hand-written slots]}
  acceptance_focus: [loop-emitted 9 slots, no other change vs parent]
```

## Fork jobs emitted (6)
See `/tmp/jobs/laptop_stand.jobs.txt` and axis files under `/tmp/axis/laptop_stand_var_*.txt`.
- rec_laptop_stand_var_skeleton_wedge (③, parent A)
- rec_laptop_stand_var_mechanism_prop_leg (②, parent A)
- rec_laptop_stand_var_mechanism_prismatic_post (②, parent B)
- rec_laptop_stand_var_skeleton_scissor_lift (①, parent B)
- rec_laptop_stand_var_skeleton_center_column (①, parent B)
- rec_laptop_stand_var_n9_vents (N, parent A)
