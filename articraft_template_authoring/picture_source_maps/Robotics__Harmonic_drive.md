# Source Map — Robotics / Harmonic drive

slug `harmonic_drive` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_use-the-attached-reference-image-picture-robotic_20260707_101020_765781_b50bce44` — picture/Robotics/Harmonic drive/002.png
- `rec_create-exactly-one-articulated-cad-style-harmoni_20260707_090158_102372_c263187d` — picture/Robotics/Harmonic drive/002.png
- `rec_robotics__harmonic_drive__001_png_d4091bdf8682414ba300de16b7984d0f` — picture/Robotics/Harmonic drive/001.png

## Variants generated this batch (6 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_harmonic_drive_var_bolt_n20` | bolt_n20 | PASS | 2 | 2 |
| `rec_harmonic_drive_var_bolt_n8` | bolt_n8 | PASS | 2 | 2 |
| `rec_harmonic_drive_var_form_tophat` | form_tophat | PASS | 2 | 1 |
| `rec_harmonic_drive_var_mechanism_continuous` | mechanism_continuous | PASS | 2 | 0 |
| `rec_harmonic_drive_var_probe_cup_rotary` | probe_cup_rotary | PASS | 2 | 1 |
| `rec_harmonic_drive_var_skeleton_3element` | skeleton_3element | PASS | 3 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Robotics / Harmonic drive (`harmonic_drive`)

pattern: **mixed** (coaxial concentric stack: fixed circular-spline/housing root; flexspline + wave-generator + output flange as coaxial children; bolt-hole / tooth / bearing-ball loop multiplicity). Some origins are ASSEMBLED (rotary reduction), some EXPLODED (prismatic assembly steps).

richness band: **normal (low end)** — target ~8–11 counted candidate anchors. Structural vocabulary is genuinely constrained: every real harmonic drive is a coaxial concentric strain-wave reducer, so ①/②/③ vocabulary is narrow. Coverage-first, no padding.

## 1. Subcategory Contract
```yaml
subcategory_contract:
  category: Robotics
  subcategory: Harmonic drive
  core_identity: A strain-wave (harmonic) gear reducer — an elliptical wave generator inside a flexible externally-toothed flexspline that meshes against a rigid internally-toothed circular spline, all coaxial, giving high single-stage speed reduction.
  must_keep:
    - three functional gear elements present or implied: wave generator (elliptical cam input), flexspline (flexible toothed member), circular spline (rigid toothed ring)
    - coaxial concentric assembly on one central axis (+Z), central bore / hollow-shaft capable
    - mounting bolt-hole pattern on the fixed flange/housing and an output interface
    - at least one real non-fixed joint (coaxial rotary reduction, or exploded assembly slide)
  must_not_become:
    - planetary / cycloidal (RV) reducer
    - plain ball / cross-roller bearing or slewing ring on its own
    - electric servo motor
    - plain flange shaft coupling
  image_evidence:
    - "001.png: assembled pancake unit, front face — outer bolted flange (~14 bolts), inner captured ball bearing ring, elliptical wave-generator cam visible through central aperture with keyway, dark spline-tooth ring"
    - "002.png: exploded three-piece set — circular-spline ring with external bolt holes + internal teeth (left), flexspline cup with fine external teeth + wave generator (middle), cross-roller output bearing ring with ball set (right)"
  parent_evidence:
    - "A (001): housing(14 bolts, 28 balls, 42 spline teeth) + output_flange(4 holes, keyway) + input_hub + lifting_wave_generator; housing_to_output/housing_to_input REVOLUTE + input_to_lift PRISMATIC"
    - "B (002): housing(24-bolt wide flange, ribbed shell, 60 outer ribs, 72 inner teeth, flexspline_tooth_band) + upper_cartridge(20-bolt cross-roller cartridge, 28 balls) + input_shaft(tall shaft + wave_cam); two PRISMATIC explode slides"
    - "C (002): flange(circular_spline_bore, 12 bolts) + flexspline(hollow_cup, 60 teeth) + wave_generator(elliptical_cam + center_hub); two PRISMATIC assembly-step slides"
```

## 2. Slots and Candidates
| slot | candidate | axis | source | status |
|---|---|---|---|---|
| body_form / flexspline family | cup type (deep hollow cup, closed diaphragm bottom) | ③ | C origin | origin_anchor |
| body_form / flexspline family | pancake / flat unit (thin coaxial disk) | ③ | A origin | origin_anchor |
| body_form / flexspline family | component tube / cartridge shell | ③ | B origin | origin_anchor |
| body_form / flexspline family | top-hat (silk-hat) flexspline, outward brim flange | ③ | fork F1 | forked_anchor |
| opening_or_motion / mechanism | coaxial bounded REVOLUTE rotary reduction (output+input) | ② | A origin | origin_anchor |
| opening_or_motion / mechanism | exploded PRISMATIC assembly-step stack | ② | B,C origin | origin_anchor |
| opening_or_motion / mechanism | CONTINUOUS unbounded rotary reduction (running reducer) | ② | fork F2 | forked_anchor |
| internal_structure / skeleton | single fused housing (spline baked into shell) | ① | A,B origin | origin_anchor |
| internal_structure / skeleton | separated 3-gear-element part tree (circular_spline + flexspline + wave + output) | ① | fork F3 | forked_anchor |
| internal_structure / bearing | integrated output bearing ball ring | internal | A,B origin | origin_anchor (record) |
| internal_structure / bearing | gear-elements-only, no integrated bearing | internal | C origin | origin_anchor (record) |
| multiplicity / mount bolts | flange bolt count {12(C),14(A),24(B)} | N | origins | origin_anchor |
| multiplicity / mount bolts | same-parent sweep N=8, N=20 (on C) | N | fork N1,N2 | forked_anchor |
| multiplicity / teeth | flexspline tooth count {42(A),60(C),72(B)} | N | origins | origin_anchor |

Each supported structural slot reaches ≥2 distinct candidates. Bearing-integration slot is recorded (internal-structure detail), not forked as a standalone anchor.

## 3. Six-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked_anchor) | fused-housing unit (A,B); exploded serial cup chain (C); separated 3-gear-element assembled tree (F3) |
| ② joint / mechanism | source-backed (origin + forked_anchor) | bounded coaxial REVOLUTE reduction (A); exploded PRISMATIC stack (B,C); CONTINUOUS unbounded reduction (F2). Input wave-generator revolute + prismatic lift observed. |
| ③ primary form family | source-backed (origin + forked_anchor) | cup (C), pancake/flat (A), component tube (B), top-hat brim (F1) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | broached keyway relief, machined groove lines, bearing-ball ring, spline-tooth hint ring, brand badge decal (host-conformal, no dedicated variant) |
| ⑤ proportion / size / travel | record_only | frame OD ~0.10–0.36 m; central bore small (A) to large hollow (top-hat); revolute ±π, continuous unbounded; explode travel 0.10–0.18 m; rides along only as companion |
| ⑥ material / palette / finish | record_only | brushed/satin aluminum, dark steel / black oxide, polished bearing steel, gray-green anodized, tan-gold flexspline; companion-only |

①②③ + N are the candidate-anchor axes and are all source-backed. ④⑤⑥ are record_only / companion — never standalone, never counted toward budget.

## 4. Multiplicity / Copy Logic
- **count_param (primary):** `bolt_count` / `bolt_{i}` mounting-bolt loop on the fixed flange/housing.
  - N samples: origin-shown {12 (C), 14 (A), 24 (B)}; same-parent forked sweep on C → {8 (N1), 20 (N2)} to expose clean copy logic on one geometry.
  - suggested N_range: [8, 30].
  - copied object: through-bolt / bolt visual, indexed `bolt_{i}`; placement: even radial on fixed bolt-circle radius; joint policy: FIXED decoration on the fixed flange (no articulation).
- **count_param (secondary, record_only):** flexspline external `tooth_{i}` count — origin-shown {42, 60, 72}; N_range ~[40, 80]; loop-placed radial teeth on flexspline/spline band; FIXED. Already 3 samples across origins → no fork.
- **other loops (record_only):** bearing balls {28 (A,B)}; housing outer ribs 60 / inner teeth 72 (B); output-flange bolt holes 4 (A) / cover sockets 20 (B). Loop-emitted, FIXED, indexed — recorded, not swept.

## 5. Budget Decision
- Counted candidate anchors (origin_anchor + forked_anchor): **3 origins + 5 forks = 8**.
  - origins: A (pancake/flat rotary), B (component tube exploded), C (cup exploded)
  - forks: F1 top-hat (③), F2 continuous (②), F3 3-element skeleton (①), N1 bolt=8, N2 bolt=20
- Not counted: 1 compatibility_probe (cup + rotary output).
- `underfilled_reason`: harmonic drives are structurally narrow — all variants are coaxial concentric strain-wave reducers, so honest ①/②/③ vocabulary saturates near the low end of the normal band (8). Remaining diversity is proportion/palette/decoration (④⑤⑥) and tooth/bolt N, which are recorded rather than padded into filler anchors.

## 6. Variant Cards
```yaml
- variant_id: rec_harmonic_drive_var_form_tophat
  source_type: forked_anchor
  parent_record_id: rec_create-exactly-one-articulated-cad-style-harmoni_20260707_090158_102372_c263187d  # C (cup)
  positioning: {product_archetype: top-hat/silk-hat HD component set (SHG/CSG), why_same_subcategory: keeps wave generator + flexible toothed spline + circular spline coaxial}
  primary_axis: {slot: flexspline_form, diversity_axis: ③, target_candidate: top_hat_outward_brim}
  structural_delta:
    change: [replace closed cup+diaphragm with short open barrel ending in outward radial mounting-flange brim carrying its own bolt circle; keep external tooth band loop near rim]
    keep_parts: [flange, circular_spline_bore, flexspline, tooth_{i}, wave_generator, elliptical_cam, center_hub, step_01_flange_to_flexspline, step_02_flexspline_to_wave_generator]
    joint_policy: preserve two coaxial +Z prismatic joints
    interface_policy: elliptical cam nests in open bore; brim concentric with flange
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [barrel wall proportion, anodized palette], forbidden: [joint change, part add/remove, category drift]}
  acceptance_focus: [brim reads as outward flange not closed cup, compiles, prismatic slides work]

- variant_id: rec_harmonic_drive_var_mechanism_continuous
  source_type: forked_anchor
  parent_record_id: rec_robotics__harmonic_drive__001_png_d4091bdf8682414ba300de16b7984d0f  # A (assembled rotary)
  positioning: {product_archetype: installed HD gearbox on robot joint, running reduction, why_same_subcategory: coaxial wave/flexspline/spline reduction preserved}
  primary_axis: {slot: mechanism, diversity_axis: ②, target_candidate: continuous_unbounded_rotary}
  structural_delta:
    change: [retype housing_to_output and housing_to_input REVOLUTE -> CONTINUOUS about (0,0,1); drop input_to_lift prismatic + lift post; seat wave_generator directly in input_hub]
    keep_parts: [housing, housing_shell, output_flange, input_hub, wave_generator, bearing_ball_{i}, spline_tooth_{i}, housing_to_output, housing_to_input]
    joint_policy: replace exactly one primary-axis mechanism (bounded->continuous), remove secondary lift
    interface_policy: keep concentric bearing races and ball ring
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [form-family change, bolt/tooth N change]}
  acceptance_focus: [continuous joints, output rotates unbounded, at least one non-fixed joint, compiles]

- variant_id: rec_harmonic_drive_var_skeleton_3element
  source_type: forked_anchor
  parent_record_id: rec_robotics__harmonic_drive__001_png_d4091bdf8682414ba300de16b7984d0f  # A
  positioning: {product_archetype: HD component set assembled with separate circular-spline ring + flexspline + wave + output, why_same_subcategory: same three strain-wave elements engage coaxially}
  primary_axis: {slot: skeleton, diversity_axis: ①, target_candidate: separated_3_element_part_tree}
  structural_delta:
    change: [promote circular-spline tooth ring into its own fixed circular_spline part bolted to housing; add distinct thin-wall flexspline ring part; keep output_flange rotating and input_hub+wave as input]
    keep_parts: [housing, output_flange, input_hub, wave_generator, spline_tooth_{i}, bearing_ball_{i}, housing_to_output, housing_to_input]
    joint_policy: add fixed mount(circular_spline->housing); preserve moving output/input revolute types
    interface_policy: all parts concentric with visible mating faces; circular spline fixed to housing
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [prismatic explode conversion, form-family change, N change]}
  acceptance_focus: [distinct circular_spline + flexspline parts, no floating parts, rotary output preserved, compiles]

- variant_id: rec_harmonic_drive_var_bolt_n8
  source_type: forked_anchor
  parent_record_id: rec_create-exactly-one-articulated-cad-style-harmoni_20260707_090158_102372_c263187d  # C
  positioning: {product_archetype: compact small-frame HD with sparse mount bolts, why_same_subcategory: only mount-bolt count changes}
  primary_axis: {slot: multiplicity_mount_bolts, diversity_axis: N, target_candidate: 8}
  structural_delta:
    change: [change bolt_{i} loop count 12 -> 8 on same bolt-circle radius]
    keep_parts: [flange, flange_ring, circular_spline_bore, bolt_{i}, flexspline, tooth_{i}, wave_generator]
    joint_policy: preserve all joints
    interface_policy: unchanged
  multiplicity: {applies: true, target_n: 8, copied_object: bolt visual, placement_rule: radial even on flange bolt circle}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [any non-count change]}
  acceptance_focus: [8 evenly-spaced bolts, indexed names, compiles]

- variant_id: rec_harmonic_drive_var_bolt_n20
  source_type: forked_anchor
  parent_record_id: rec_create-exactly-one-articulated-cad-style-harmoni_20260707_090158_102372_c263187d  # C
  positioning: {product_archetype: large high-torque HD with dense mount bolts, why_same_subcategory: only mount-bolt count changes}
  primary_axis: {slot: multiplicity_mount_bolts, diversity_axis: N, target_candidate: 20}
  structural_delta:
    change: [change bolt_{i} loop count 12 -> 20 on same bolt-circle radius]
    keep_parts: [flange, flange_ring, circular_spline_bore, bolt_{i}, flexspline, tooth_{i}, wave_generator]
    joint_policy: preserve all joints
    interface_policy: unchanged
  multiplicity: {applies: true, target_n: 20, copied_object: bolt visual, placement_rule: radial even on flange bolt circle}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [any non-count change]}
  acceptance_focus: [20 evenly-spaced bolts, indexed names, compiles]

- variant_id: rec_harmonic_drive_var_probe_cup_rotary
  source_type: compatibility_probe
  parent_record_id: rec_create-exactly-one-articulated-cad-style-harmoni_20260707_090158_102372_c263187d  # C
  positioning: {product_archetype: assembled CSF cup-type HD gearbox with rotating output flange, why_same_subcategory: cup strain-wave reducer with integrated rotary output}
  primary_axis: {slot: probe, diversity_axis: probe, target_candidate: cup_form + rotary_output}
  structural_delta:
    change: [add rotating output_flange disk on cup mouth; replace two prismatic explode joints with REVOLUTE flange_to_output + REVOLUTE wave input]
    keep_parts: [flange, circular_spline_bore, bolt_{i}, flexspline, flexspline_cup, tooth_{i}, wave_generator, elliptical_cam, center_hub]
    joint_policy: replace explode prismatics with coaxial revolute output/input
    interface_policy: bearing land / mating face between output flange and fixed flange (supported, not floating)
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [category drift]}
  acceptance_focus: [output flange supported not floating, cup form retained, revolute output turns, compiles]
```

## 7. Blocked / Excluded
- Extra bolt-N samples beyond {8,12,20} (same parent) and beyond origin {14,24}: excluded — copy logic already exposed.
- Tooth-count N fork: excluded — origins already show {42,60,72}.
- Bearing-integration as standalone anchor: recorded as internal-structure detail (origins A/B have it, C omits it); not forked to avoid ④/internal padding.
- Roller vs cam wave-generator internal detail, hollow-bore size sweep: record_only (⑤), not forked.

## 8. Emitted Jobs
6 jobs in `/tmp/jobs/harmonic_drive.jobs.txt`: F1 form_tophat, F2 mechanism_continuous, F3 skeleton_3element, N1 bolt_n8, N2 bolt_n20 (5 counted forked_anchors) + 1 compatibility_probe (probe_cup_rotary, not counted).
