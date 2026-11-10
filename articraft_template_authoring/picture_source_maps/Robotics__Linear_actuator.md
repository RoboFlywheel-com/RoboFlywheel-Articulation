# Source Map — Robotics / Linear actuator

slug `linear_actuator` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_robotics__linear_actuator__002_png_d3d50297221542dda13617f4358bd6e3` — picture/Robotics/Linear actuator/002.png
- `rec_robotics__linear_actuator__001_png_9c02462c174f4f14bcda0a4340649b63` — picture/Robotics/Linear actuator/001.png

## Variants generated this batch (7 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_linear_actuator_var_form_rod_cylinder` | form_rod_cylinder | PASS | 2 | 1 |
| `rec_linear_actuator_var_mechanism_belt` | mechanism_belt | PASS | 2 | 1 |
| `rec_linear_actuator_var_n_carriage2` | n_carriage2 | PASS | 3 | 0 |
| `rec_linear_actuator_var_n_guiderod1` | n_guiderod1 | PASS | 2 | 1 |
| `rec_linear_actuator_var_probe_pneumatic` | probe_pneumatic | PASS | 1 | 1 |
| `rec_linear_actuator_var_skeleton_parallel_motor` | skeleton_parallel_motor | PASS | 2 | 1 |
| `rec_linear_actuator_var_skeleton_telescoping` | skeleton_telescoping | PASS | 3 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Robotics / Linear actuator (`linear_actuator`)

pattern: **mixed** (a fixed `frame` root carrying a linearly-guided `carriage` child on a PRISMATIC joint, plus a rotating `lead_screw` child on a REVOLUTE joint; guide-rod / belt-tooth / thread-crest / bolt-hole loop multiplicity). Both origins are the SAME structural cell: screw-driven extruded-rail slide.

richness band: **normal (low end)** — target ~8 counted candidate anchors. Structural vocabulary is real but converges: every linear actuator is a single-DOF linear-motion device, and the two origins occupy one identical cell (extruded rail + rotating lead screw + sliding carriage). Coverage-first, no padding.

## 1. Subcategory Contract
```yaml
subcategory_contract:
  category: Robotics
  subcategory: Linear actuator
  core_identity: A powered device that converts rotary (screw/belt/pulley) or direct (pneumatic/hydraulic) input into one controlled straight-line stroke — a carriage or rod that extends/retracts along a single linear axis, guided by a rail/tube and driven by an internal screw, belt, or piston.
  must_keep:
    - one primary translational output (a PRISMATIC carriage/rod stroke along one axis)
    - a fixed structural body (extruded rail / cylindrical barrel) that guides and supports the moving member
    - a drive element (rotating lead screw, driven belt/pulley, or direct piston) that produces the stroke
    - at least one real non-fixed joint (the carriage/rod prismatic, plus the screw/pulley revolute when present)
  must_not_become:
    - rack_and_pinion_slider (a pinion gear driving a toothed rack)
    - a passive linear rail / linear guide with no drive
    - a bare power/lead screw or ball screw on its own
    - a plain gearmotor / servo motor with no linear stage
    - a furniture desk/TV lift column (for the telescoping variant)
  image_evidence:
    - "002.png (A): exploded rail-stage set — extruded aluminum T-slot rail, a round guide rod, a black toothed drive strip/rack in front, black end plates, left motor block, right end plate with a large captured bearing bore"
    - "001.png (B): compact assembled rail actuator — black-anodized extrusion with dark T-slot grooves, black end caps + left motor housing, a central aluminum carriage with mounting holes riding mid-rail (rodless screw slide)"
  parent_evidence:
    - "A (002): frame(base_rail T-slots, 2 end_plate, motor_block, 2 guide_rod+rod_clamp, 2 bearing_ring, belt_backing+belt_tooth_{i}=58, rail_hole_{i}=6) + carriage(carriage_block, lead_nut_ring, carriage_bolt_{i}) + lead_screw(screw_core, screw_thread helix mesh, drive_coupler, shaft_extension, 2 bearing_journal); carriage_slide PRISMATIC + screw_spin REVOLUTE, both axis (1,0,0)"
    - "B (001): frame(rail_extrusion, bottom_foot, side_slot/top_slot, 2 end_plate, motor_block+motor_cap, 2 guide_rod, screw_yoke_*, face screws) + carriage(carriage_block, 2 bearing_shoe, side_skirt, raised_mount_boss, top_hole/front_hole) + lead_screw(screw_core, thread_crest_{i}=33, 2 coupler); frame_to_carriage PRISMATIC + frame_to_lead_screw REVOLUTE, both axis (1,0,0)"
```

## 2. Slots and Candidates
| slot | candidate | axis | source | status |
|---|---|---|---|---|
| body_form / primary form family | extruded-rail slide (open carriage on aluminum extrusion) | ③ | A,B origin | origin_anchor |
| body_form / primary form family | cylindrical tube-and-rod barrel (electric cylinder) | ③ | fork form_rod_cylinder | forked_anchor |
| drive_mechanism | rotating lead-screw (REVOLUTE screw + PRISMATIC carriage) | ② | A,B origin | origin_anchor |
| drive_mechanism | toothed belt-and-pulley drive (REVOLUTE pulley + PRISMATIC carriage) | ② | fork mechanism_belt | forked_anchor |
| drive_mechanism | direct single-prismatic piston (no rotary screw) | ② | probe probe_pneumatic | compatibility_probe |
| skeleton / topology | single carriage on rail, inline coaxial motor | ① | A,B origin | origin_anchor |
| skeleton / topology | serial telescoping nested-tube prismatic chain | ① | fork skeleton_telescoping | forked_anchor |
| skeleton / topology | parallel/folded offset motor with reduction belt to screw | ① | fork skeleton_parallel_motor | forked_anchor |
| carriage_guidance / support | dual parallel guide rod | support | A,B origin | origin_anchor (record) |
| carriage_guidance / support | single central guide rod | N | fork n_guiderod1 | forked_anchor |
| multiplicity / carriage count | 1 carriage | N | A,B origin | origin_anchor |
| multiplicity / carriage count | 2 carriages on one rail | N | fork n_carriage2 | forked_anchor |

Each supported structural slot reaches ≥2 distinct candidates. body_form 2, drive_mechanism 2 (+1 probe), skeleton 3, guide-rod count 2, carriage count 2.

## 3. Six-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked_anchor) | single-carriage-on-rail inline-motor (A,B); serial telescoping nested-tube chain (fork); parallel/folded offset-motor drivetrain (fork) |
| ② joint / mechanism | source-backed (origin + forked_anchor + probe) | lead-screw REVOLUTE + carriage PRISMATIC (A,B); belt-and-pulley REVOLUTE + carriage PRISMATIC (fork); direct single-PRISMATIC piston, screw removed (probe) |
| ③ primary form family | source-backed (origin + forked_anchor) | planar extruded-rail profile (A,B); volumetric cylindrical tube-and-rod barrel (fork) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | T-slot grooves, belt_tooth_{i}/thread_crest_{i} strips, rail_hole_{i}, socket-head bolt/screw heads, cable, brand decal — host-conformal, no dedicated variant |
| ⑤ proportion / size / travel | record_only | rail length 0.70–0.83 m; stroke/travel 0.18–0.42 m; screw dia ~0.011–0.012; barrel/rod dia; ride-along companion only |
| ⑥ material / palette / finish | record_only | brushed vs polished aluminum, black-anodized, machined/polished steel screw, bronze lead nut, black timing-belt — companion only |

①②③ + N are the candidate-anchor axes and all source-backed. ④⑤⑥ are record_only / companion — never standalone, never counted toward budget.

## 4. Multiplicity / Copy Logic
- **count_param (primary): carriage count** `n_carriages` / `carriage_{i}` on the rail.
  - N samples: origin-shown {1 (A,B)}; forked sweep {2 (n_carriage2)}.
  - suggested N_range: [1, 3].
  - copied object: full carriage assembly (carriage_block + bearing shoes) + its own PRISMATIC joint `frame_to_carriage_{i}`; placement: distinct even X offsets along rail; joint policy: each an independent prismatic on axis (1,0,0), uniform limits.
- **count_param (secondary): guide-rod count** `n_guide_rods` / `guide_rod_{i}`.
  - N samples: origin-shown {2 (A,B)}; forked sweep {1 (n_guiderod1)}.
  - suggested N_range: [1, 2].
  - copied object: guide_rod cylinder (+ bushing/rod_clamp); placement: symmetric about screw axis for 2, centered on axis for 1; joint policy: FIXED to frame.
- **record_only loops (not swept):** belt_tooth_{i} {58 (A)}, thread_crest_{i} {33 (B)}, rail_hole_{i} {6 (A)}, mounting bolt/screw patterns, telescoping stage_{i}. Loop-emitted, indexed, FIXED decoration or internal — recorded, not padded into anchors.

## 5. Budget Decision
- Counted candidate anchors (origin_anchor + forked_anchor): **2 origins + 6 forks = 8**.
  - origins: A (rich CadQuery rail-stage), B (compact box rail-stage) — same structural cell.
  - forks: form_rod_cylinder (③), mechanism_belt (②), skeleton_telescoping (①), skeleton_parallel_motor (①), n_carriage2 (N), n_guiderod1 (N).
- Not counted: 1 compatibility_probe (probe_pneumatic — cylinder form + direct single-prismatic).
- `underfilled_reason`: The two origins occupy one identical structural cell (extruded rail + rotating lead screw + sliding carriage), so honest ①/②/③ vocabulary for the whole subcategory saturates near the low end of the normal band (~8). The remaining diversity is proportion/travel, palette, and decoration (④⑤⑥) plus belt/thread/hole N, which are recorded rather than padded into filler anchors. Rack-and-pinion drive is deliberately excluded (it is the neighbor subcategory rack_and_pinion_slider).

## 6. Variant Cards
```yaml
- variant_id: rec_linear_actuator_var_form_rod_cylinder
  source_type: forked_anchor
  parent_record_id: rec_robotics__linear_actuator__002_png_d3d50297221542dda13617f4358bd6e3  # A
  positioning: {product_archetype: electric rod-style cylinder linear actuator (enclosed round barrel + protruding thrust rod), why_same_subcategory: an internal rotating lead screw still drives one prismatic linear stroke}
  primary_axis: {slot: body_form, diversity_axis: ③, target_candidate: cylindrical_tube_and_rod_barrel}
  structural_delta:
    change: [replace extruded base_rail with a round barrel tube frame via lathe/tube geometry; repurpose the carriage prismatic child as a coaxial extending rod exiting one end cap; house lead_screw and guide rod inside the barrel; add end caps/gland]
    keep_parts: [frame, carriage, lead_screw, screw_core, screw_thread, drive_coupler, motor_block, carriage_slide, screw_spin]
    joint_policy: preserve carriage_slide PRISMATIC and screw_spin REVOLUTE about (1,0,0)
    interface_policy: rod exits a bored end cap; screw is captive inside the barrel and drives the rod nut
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [barrel/rod proportion, anodized palette], forbidden: [joint-type change, drive-mechanism change, category drift]}
  acceptance_focus: [barrel+rod reads as a cylinder actuator, rod extends on prismatic, screw revolute retained, compiles]

- variant_id: rec_linear_actuator_var_mechanism_belt
  source_type: forked_anchor
  parent_record_id: rec_robotics__linear_actuator__002_png_d3d50297221542dda13617f4358bd6e3  # A
  positioning: {product_archetype: toothed-belt-driven linear slide/actuator (high-speed belt carriage), why_same_subcategory: a driven pulley converts rotation into one prismatic carriage stroke}
  primary_axis: {slot: drive_mechanism, diversity_axis: ②, target_candidate: belt_and_pulley_drive}
  structural_delta:
    change: [remove lead_screw/lead_nut_ring/screw_thread; add a closed timing-belt loop over two coaxial end pulleys (drive_pulley + idler_pulley); clamp the upper belt span to the carriage via belt_clamp; retype the rotary joint as drive_pulley REVOLUTE about the pulley axis]
    keep_parts: [frame, base_rail, end_plate_0, end_plate_1, guide_rod_0, guide_rod_1, carriage, carriage_block, carriage_slide]
    joint_policy: preserve carriage_slide PRISMATIC; replace exactly one primary-axis mechanism (screw revolute -> driven pulley revolute)
    interface_policy: belt seated in pulley grooves, clamped to carriage (no floating belt); pulleys journalled in end plates
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [belt-tooth pitch, palette], forbidden: [form-family change, rack-and-pinion drift, carriage-count change]}
  acceptance_focus: [belt runs over two pulleys and clamps to carriage, pulley revolute drives carriage prismatic, compiles]

- variant_id: rec_linear_actuator_var_skeleton_telescoping
  source_type: forked_anchor
  parent_record_id: rec_robotics__linear_actuator__001_png_9c02462c174f4f14bcda0a4340649b63  # B
  positioning: {product_archetype: telescopic rod / multi-stage column linear actuator (nested tubes extend along one axis), why_same_subcategory: single-axis powered extension with a visible drive, not a passive furniture column}
  primary_axis: {slot: skeleton, diversity_axis: ①, target_candidate: serial_telescoping_nested_prismatic_chain}
  structural_delta:
    change: [replace single flat rail + carriage with 3 nested tubes stage_{i} emitted by a for-i loop with a shared helper; each inner stage_{i} is a PRISMATIC child of the next-outer stage along +X (serial chain); keep the central screw as the drivetrain]
    keep_parts: [frame, rail_extrusion, motor_block, lead_screw, screw_core, frame_to_lead_screw]
    joint_policy: single prismatic -> serial nested prismatic chain stage_slide_{i}, one primary translational axis retained; screw revolute kept
    interface_policy: each stage nests inside its parent tube with a sliding fit; outermost stage is the moving rod
  multiplicity: {applies: true, target_n: 3, copied_object: nested tube stage, placement_rule: serial coaxial chain along +X}
  companion_variations: {allowed_④⑤⑥: [tube proportion, palette], forbidden: [furniture-column drift, drive-mechanism change]}
  acceptance_focus: [nested tubes telescope on serial prismatic chain, loop-emitted stage_{i}, no floating parts, compiles]

- variant_id: rec_linear_actuator_var_skeleton_parallel_motor
  source_type: forked_anchor
  parent_record_id: rec_robotics__linear_actuator__002_png_d3d50297221542dda13617f4358bd6e3  # A
  positioning: {product_archetype: parallel-drive / folded-motor rail actuator (space-saving side-mounted motor coupled to the screw by a reduction belt), why_same_subcategory: same screw-driven prismatic carriage output, only the drivetrain layout changes}
  primary_axis: {slot: skeleton, diversity_axis: ①, target_candidate: parallel_folded_offset_motor_drivetrain}
  structural_delta:
    change: [relocate motor_block onto a bracket offset in -Y beside the rail with its axis parallel to the screw; add motor_pulley + screw_pulley + reduction_belt spanning motor-to-screw at the drive end; drive end plate gains the reduction cover]
    keep_parts: [frame, base_rail, carriage, carriage_block, lead_screw, screw_core, screw_thread, guide_rod_0, guide_rod_1, carriage_slide, screw_spin]
    joint_policy: preserve carriage_slide PRISMATIC and screw_spin REVOLUTE; motor is fixed housing, reduction belt is FIXED coupling decoration
    interface_policy: motor bracket bolted to frame; reduction belt seated on both pulleys (no floating), screw still drives carriage
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [motor size, palette], forbidden: [belt-driven-carriage conversion, joint-type change, gearmotor-only]}
  acceptance_focus: [motor offset parallel beside rail with reduction belt to screw, carriage still screw-driven prismatic, compiles]

- variant_id: rec_linear_actuator_var_n_carriage2
  source_type: forked_anchor
  parent_record_id: rec_robotics__linear_actuator__001_png_9c02462c174f4f14bcda0a4340649b63  # B
  positioning: {product_archetype: dual-carriage / multi-slide linear actuator (two independently positioned carriages on one rail), why_same_subcategory: still one rail with prismatic carriage strokes}
  primary_axis: {slot: multiplicity_carriage, diversity_axis: N, target_candidate: 2}
  structural_delta:
    change: [emit carriages via for-i-in-range(2) loop with a shared carriage helper -> carriage_{i}; place at distinct X offsets; each carriage_{i} an independent PRISMATIC child of frame via frame_to_carriage_{i}]
    keep_parts: [frame, rail_extrusion, guide_rod_0, guide_rod_1, lead_screw, screw_core, frame_to_lead_screw]
    joint_policy: preserve screw revolute; carriage prismatic copied per carriage on axis (1,0,0), uniform limits
    interface_policy: both carriages ride the same rail/guide rods; no overlap at rest
  multiplicity: {applies: true, target_n: 2, copied_object: carriage assembly + its prismatic joint, placement_rule: even X offsets along rail}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [any non-count structural change]}
  acceptance_focus: [two loop-emitted carriages, two independent prismatic joints, indexed names, compiles]

- variant_id: rec_linear_actuator_var_n_guiderod1
  source_type: forked_anchor
  parent_record_id: rec_robotics__linear_actuator__001_png_9c02462c174f4f14bcda0a4340649b63  # B
  positioning: {product_archetype: single-guide-rod linear actuator (one central round guide rod, extrusion body provides anti-rotation), why_same_subcategory: same screw-driven prismatic carriage on a rail}
  primary_axis: {slot: multiplicity_guide_rod, diversity_axis: N, target_candidate: 1}
  structural_delta:
    change: [change guide_rod_{i} loop from 2 rods (y=±0.032) to 1 rod on the rail centerline (y=0); update the carriage bearing shoe to ride the single central rod]
    keep_parts: [frame, rail_extrusion, carriage, carriage_block, bearing_shoe_0, lead_screw, screw_core, frame_to_carriage, frame_to_lead_screw]
    joint_policy: preserve carriage prismatic and screw revolute; guide_rod_{i} loop range(1), FIXED to frame
    interface_policy: single rod centered on screw axis, carriage bushing concentric on it
  multiplicity: {applies: true, target_n: 1, copied_object: guide_rod cylinder + bushing, placement_rule: centered on rail axis}
  companion_variations: {allowed_④⑤⑥: [rod diameter, palette], forbidden: [any non-count structural change]}
  acceptance_focus: [single central guide rod, carriage rides it, loop-emitted, compiles]

- variant_id: rec_linear_actuator_var_probe_pneumatic
  source_type: compatibility_probe
  parent_record_id: rec_robotics__linear_actuator__002_png_d3d50297221542dda13617f4358bd6e3  # A
  positioning: {product_archetype: pneumatic/hydraulic cylinder linear actuator (rod extends/retracts directly), why_same_subcategory: single prismatic thrust output despite removing the rotary drivetrain}
  primary_axis: {slot: probe, diversity_axis: probe, target_candidate: cylinder_form + direct_single_prismatic}
  structural_delta:
    change: [enclose actuator in a round barrel tube frame (lathe/tube); repurpose carriage as a coaxial piston rod exiting one cap; remove lead_screw and screw_spin entirely; keep carriage_slide as the sole direct prismatic; add port bosses/end caps]
    keep_parts: [frame, carriage, carriage_slide]
    joint_policy: single direct PRISMATIC only (no revolute); at least one non-fixed joint retained
    interface_policy: rod supported by bored end cap and barrel bore (not floating); barrel is the fixed body
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [barrel/rod proportion, palette], forbidden: [gas-spring/damper drift, rack_and_pinion_slider]}
  acceptance_focus: [rod-cylinder body with pure prismatic reads as a supported linear actuator, rod not floating, compiles]
```

## 7. Blocked / Excluded
- rack-and-pinion drive: excluded — it is the neighbor subcategory `rack_and_pinion_slider`, listed in must_not_become.
- bare lead-screw / passive linear-guide / gearmotor-only: excluded — not linear actuators (drop a required functional layer).
- extra carriage-N beyond {1,2} and guide-rod-N beyond {1,2}: excluded — copy logic already exposed at the low end.
- belt-tooth / thread-crest / rail-hole N sweeps: record_only (④ decoration), not forked.
- screw REVOLUTE -> CONTINUOUS unbounded: record_only (② joint-limit detail, too close to origins), not forked.

## 8. Emitted Jobs
7 jobs in `/tmp/jobs/linear_actuator.jobs.txt`: form_rod_cylinder (③), mechanism_belt (②), skeleton_telescoping (①), skeleton_parallel_motor (①), n_carriage2 (N), n_guiderod1 (N) = 6 counted forked_anchors, + probe_pneumatic (compatibility_probe, not counted).
