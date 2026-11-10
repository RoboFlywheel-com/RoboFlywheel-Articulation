# Source Map — Robotics / Rack-and-pinion slider

slug `rack_and_pinion_slider` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_robotics__rack_and_pinion_slider__002_png_74acaa0d7f234f268f9a71467cd6a0bb` — picture/Robotics/Rack-and-pinion slider/002.png
- `rec_robotics__rack_and_pinion_slider__001_png_181f53f1e2d249138d855513a68bcb4c` — picture/Robotics/Rack-and-pinion slider/001.png

## Variants generated this batch (8 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_rack_and_pinion_slider_var_carriage_linear_table` | carriage_linear_table | PASS | 2 | 1 |
| `rec_rack_and_pinion_slider_var_form_enclosed_tube` | form_enclosed_tube | PASS | 2 | 1 |
| `rec_rack_and_pinion_slider_var_form_round_rack` | form_round_rack | PASS | 2 | 1 |
| `rec_rack_and_pinion_slider_var_n16_short_rack` | n16_short_rack | PASS | 2 | 1 |
| `rec_rack_and_pinion_slider_var_n2_dual_pinion` | n2_dual_pinion | PASS | 3 | 1 |
| `rec_rack_and_pinion_slider_var_n44_long_rack` | n44_long_rack | PASS | 2 | 1 |
| `rec_rack_and_pinion_slider_var_skeleton_cantilever_pinion` | skeleton_cantilever_pinion | PASS | 2 | 1 |
| `rec_rack_and_pinion_slider_var_skeleton_traveling_pinion` | skeleton_traveling_pinion | PASS | 2 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Robotics / Rack-and-pinion slider (`rack_and_pinion_slider`)

pattern: **mixed** (single fixed guide-frame root carrying two coupled children: a REVOLUTE pinion and a PRISMATIC rack/carriage; rack-tooth and pinion-tooth loop multiplicity). Both origins are ASSEMBLED running mechanisms — pinion rotation ↔ rack linear translation coupled by pitch-radius metadata.

richness band: **simple (8–12)** — target ~10 counted candidate anchors. Structural vocabulary is genuinely narrow: every real rack-and-pinion slider is a toothed pinion meshing a toothed rack on a guide, so honest ①/②/③ vocabulary saturates near the low end. Coverage-first, no padding.

## 1. Subcategory Contract
```yaml
subcategory_contract:
  category: Robotics
  subcategory: Rack-and-pinion slider
  core_identity: A linear-motion transmission where a rotating toothed pinion (spur gear) meshes a toothed linear rack, converting rotation to straight-line travel (or the reverse), with the sliding member guided along one straight axis on a fixed frame/base.
  must_keep:
    - a toothed pinion (spur gear) that rotates on a fixed axis carried by the frame
    - a toothed straight rack whose teeth mesh the pinion at the pitch line
    - one REVOLUTE pinion joint + one PRISMATIC linear-slide joint, coupled by pitch-radius (rotation drives translation)
    - a fixed guide frame/base that carries the pinion axis and guides the sliding member
    - at least one real non-fixed joint (mesh-coupled spin + slide)
  must_not_become:
    - lead-screw / ball-screw linear actuator (helical screw drive, no rack teeth)
    - belt-driven / timing-belt linear slide (flexible belt, no gear mesh)
    - plain linear rail / LM guide / cross-roller stage (no gear drive at all)
    - rotary gear train / gearbox / worm drive (no linear rack member)
    - chain-and-sprocket linear drive
    - automotive steering rack with tie-rods (becomes a vehicle steering assembly)
  image_evidence:
    - "001.png (parent A/002): straight flat bar rack with cut trapezoidal teeth on top face + separate spur pinion (bore + counterbored hub) lying beside/above it; classic single-rack single-pinion pair, no housing"
    - "002.png (parent B/001): labelled diagram — spur 'pinion' with axle (C–D rotation) meshing a long straight 'rack' (A–B linear travel) resting on a rectangular guide bar; single pinion, single rack"
  parent_evidence:
    - "A (002): frame{base_plate, guide_rail_{0,1}, bearing_cheek_{0,1}, cheek_foot_{0,1}, bearing_boss_{0,1}, pinion_shaft, mount_screw_*} + rack_carriage{straight_rack(RackGear), carriage_block, carriage_bolt_{0,1}} + pinion{toothed_wheel(SpurGear 28T), hub}; pinion_spin REVOLUTE + rack_slide PRISMATIC, coupled by PINION_PITCH_RADIUS_M. Straddle cheek+shaft bearing support."
    - "B (001): guide_frame{base_plate, guide_rail, rail_stop_{0,1}, mount_bolt_{0..3}, bearing_web_{0,1}, bearing_saddle_{0,1}, bearing_collar_{0,1}(torus)} + rack_carriage{carriage_bridge, carriage_shoe_{0,1}, rack_bar, rack_end_cap_{0,1}, rack_tooth_00..29 (30-tooth loop)} + pinion{root_wheel, pinion_tooth_00..21 (22-tooth loop), raised_hub, axle, axle_cap_{0,1}(blue)}; pinion_spin REVOLUTE + rack_slide PRISMATIC, pitch_radius/tooth_pitch meta. Straddle torus-collar bearing support."
```

## 2. Slots and Candidates
| slot | candidate | axis | source | status |
|---|---|---|---|---|
| rack_form (③ primary form family) | straight flat bar rack (rectangular back + top teeth) | ③ | A,B origin | origin_anchor |
| rack_form (③ primary form family) | round / cylindrical rack shaft (teeth cut into a round bar) | ③ | fork form_round_rack | forked_anchor |
| body_envelope (③ macro construction) | open bare mechanism (rack/pinion exposed) | ③ | A,B origin | origin_anchor |
| body_envelope (③ macro construction) | enclosed tubular actuator housing (rack extends from a tube) | ③ | fork form_enclosed_tube | forked_anchor |
| output_carriage (③ carriage body form) | plain carriage block / bridge under the rack | ③ | A,B origin | origin_anchor (record) |
| output_carriage (③ carriage body form) | broad rack-driven linear stage table (T-slot platform) | ③ | fork carriage_linear_table | forked_anchor |
| drive_skeleton (① topology) | moving rack, fixed pinion (rack translates) | ① | A,B origin | origin_anchor |
| drive_skeleton (① topology) | fixed rack, traveling pinion carriage (pinion+carriage climbs the rack) | ① | fork skeleton_traveling_pinion | forked_anchor |
| pinion_support (① support topology) | straddle two-side bearing (cheeks A / torus collars B) | ① | A,B origin | origin_anchor |
| pinion_support (① support topology) | cantilever / overhung one-side pinion support (motor-mounted) | ① | fork skeleton_cantilever_pinion | forked_anchor |
| pinion_multiplicity (N pinions) | single pinion on the rack | N | A,B origin | origin_anchor |
| pinion_multiplicity (N pinions) | dual anti-backlash pinions on one rack (2 REVOLUTE) | N | fork n2_dual_pinion | forked_anchor |
| rack_multiplicity (N rack teeth / length) | rack tooth count 30 (mid) | N | B origin | origin_anchor |
| rack_multiplicity (N rack teeth / length) | long rack ~44 teeth (long-stroke) | N | fork n44_long_rack | forked_anchor |
| rack_multiplicity (N rack teeth / length) | short rack ~16 teeth (short-stroke) | N | fork n16_short_rack | forked_anchor |

Each supported structural slot reaches ≥2 distinct candidates. `output_carriage` plain-block value is recorded (both origins show it); only its distinct linear-table candidate is forked. `pinion_teeth` count is recorded (⑤/N record_only: 22T@B, 28T@A) — not swept, to avoid over-forking; rack-length is the primary multiplicity.

## 3. Six-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked_anchor) | moving-rack/fixed-pinion (A,B); fixed-rack/traveling-pinion carriage (fork); straddle two-side pinion support (A,B) vs cantilever overhung support (fork); single vs dual pinion |
| ② joint / mechanism | source-backed (origin) | REVOLUTE pinion_spin + PRISMATIC rack_slide coupled by pitch radius (A,B). Dual-pinion fork adds a second synchronized REVOLUTE; traveling-pinion fork moves the PRISMATIC onto the carriage. No new joint *type* is honestly available — the pair is the mechanism's identity. |
| ③ primary form family | source-backed (origin + forked_anchor) | rack: flat bar (A,B) vs round cylindrical shaft (fork); envelope: open bare (A,B) vs enclosed tube housing (fork); carriage: plain block/bridge (A,B) vs broad linear-stage table (fork) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | trapezoidal tooth flanks, machined hub counterbore, bearing-collar rings, blue axle end-caps, rail-stop blocks, mount-bolt/screw heads, brand decal (host-conformal; no dedicated variant) |
| ⑤ proportion / size / travel | record_only | base length ~0.32–0.86 m; rack travel ~0.045–0.055 m; pinion 22–28 teeth, module ~2 mm; pinion pitch radius ~0.028–0.067 m; revolute ±1 rad; rides along only as companion |
| ⑥ material / palette / finish | record_only | brushed/satin steel & aluminum, dark oxide / bearing steel, zinc hardware, warm machined gear, blue anodized cap; companion-only |

①②③ + N are the candidate-anchor axes and are all source-backed. ④⑤⑥ are record_only / companion — never standalone, never counted toward budget.

## 4. Multiplicity / Copy Logic
- **count_param (primary):** rack tooth count / rack length — `rack_tooth_{idx}` loop (source-backed by B's `for idx, i in range(-15,15)` 30-tooth loop; A uses parametric RackGear as the length driver).
  - N samples: origin-shown {30 (B)}; same-parent forked sweep on B → {44 (n44, long-stroke rack), 16 (n16, short-stroke rack)}.
  - suggested N_range: [12, 56].
  - copied object: single `rack_tooth` trapezoid mesh via shared `_trapezoid_prism` helper; placement: even half-pitch spacing along +X on the rack bar; joint policy: teeth ride the moving `rack_carriage` (PRISMATIC), no per-tooth joint.
- **count_param (secondary, N/record_only):** pinion tooth count — `pinion_tooth_{idx}` radial loop, origin-shown {22 (B), 28 (A)}; N_range ~[14, 40]; already 2 samples across origins → recorded, not swept.
- **count_param (structural, forked):** number of pinions on the rack — origins show N=1; `n2_dual_pinion` fork copies the pinion sub-assembly to N=2 (anti-backlash, each with its own REVOLUTE) via a pinion-instance loop with even X spacing on the shared shaft line.
- **other loops (record_only):** mount screws/bolts {4 (A), 4 (B)}, guide rails {1–2}, bearing supports {2}. Loop-emitted, FIXED, indexed — recorded, not swept.

## 5. Budget Decision
- Counted candidate anchors (origin_anchor + forked_anchor): **2 origins + 8 forks = 10** (simple band 8–12).
  - origins: A (002, flat rack, straddle-cheek support, RackGear/SpurGear parametric), B (001, flat rack, straddle-torus support, looped teeth)
  - forks: form_round_rack (③), form_enclosed_tube (③), carriage_linear_table (③), skeleton_traveling_pinion (①), skeleton_cantilever_pinion (①), n2_dual_pinion (N/①), n44_long_rack (N), n16_short_rack (N)
- Not counted: none (no compatibility_probe needed — no genuinely risky interface combination; all forks change one clean axis).
- `underfilled_reason`: not underfilled, but deliberately held to the simple band. Rack-and-pinion sliders are a structurally narrow mechanism — the REVOLUTE-pinion + PRISMATIC-rack pair *is* the subcategory identity, so ② offers no new joint type and ①③ vocabulary is limited to rack cross-section, drive topology, support topology, and envelope. Remaining diversity is proportion / palette / decoration (④⑤⑥) and tooth-count N, which are recorded rather than padded into filler anchors.

## 6. Variant Cards
```yaml
- variant_id: rec_rack_and_pinion_slider_var_form_round_rack
  source_type: forked_anchor
  parent_record_id: rec_robotics__rack_and_pinion_slider__001_png_181f53f1e2d249138d855513a68bcb4c  # B
  positioning: {product_archetype: cylindrical rack-shaft slider (round rack bar with a toothed strip along the top), why_same_subcategory: a spur pinion still meshes a straight linear rack and drives it in a line}
  primary_axis: {slot: rack_form, diversity_axis: ③, target_candidate: round_cylindrical_rack_shaft}
  structural_delta:
    change: [replace the rectangular rack_bar box with a round cylindrical rack shaft (Cylinder along +X); keep the rack_tooth_{idx} loop but seat the trapezoidal teeth on the top of the round shaft along the pitch line; carriage rides the round shaft]
    keep_parts: [guide_frame, base_plate, guide_rail, bearing_collar_{idx}, rack_carriage, carriage_bridge, rack_tooth_{idx}, pinion, root_wheel, pinion_tooth_{idx}, axle, pinion_spin, rack_slide]
    joint_policy: preserve REVOLUTE pinion_spin + PRISMATIC rack_slide, pitch coupling unchanged
    interface_policy: pinion teeth mesh the top-of-shaft tooth strip; round shaft slides through saddle/guide bore
  multiplicity: {applies: false, target_n: null, copied_object: rack_tooth, placement_rule: even half-pitch along +X}
  companion_variations: {allowed_④⑤⑥: [shaft diameter proportion, palette], forbidden: [joint change, add/remove pinion, envelope change]}
  acceptance_focus: [rack_bar is round not boxy, teeth still mesh, prismatic slide + pinion spin work, compiles]

- variant_id: rec_rack_and_pinion_slider_var_form_enclosed_tube
  source_type: forked_anchor
  parent_record_id: rec_robotics__rack_and_pinion_slider__002_png_74acaa0d7f234f268f9a71467cd6a0bb  # A
  positioning: {product_archetype: enclosed rack-and-pinion linear actuator (mechanism inside a tubular housing, rack rod extends from one end), why_same_subcategory: pinion still meshes a straight rack and drives it linearly, just shrouded}
  primary_axis: {slot: body_envelope, diversity_axis: ③, target_candidate: enclosed_tubular_actuator_housing}
  structural_delta:
    change: [add a tubular/box housing shell on the frame that encloses the pinion and the retracted rack; the straight_rack extrudes out through an end aperture as the sliding rod; pinion shaft crosses the housing wall on its bearings]
    keep_parts: [frame, base_plate, pinion_shaft, bearing_boss_{0,1}, rack_carriage, straight_rack, carriage_block, pinion, toothed_wheel, hub, pinion_spin, rack_slide]
    joint_policy: preserve REVOLUTE pinion_spin + PRISMATIC rack_slide (rack slides through housing end aperture)
    interface_policy: housing is FIXED to frame; rack passes through a clearance aperture in the end wall (no collision with shell)
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [housing proportion, palette], forbidden: [joint change, rack cross-section change, add pinion]}
  acceptance_focus: [housing shell encloses pinion, rack still exits and slides freely, at least one non-fixed joint, compiles]

- variant_id: rec_rack_and_pinion_slider_var_carriage_linear_table
  source_type: forked_anchor
  parent_record_id: rec_robotics__rack_and_pinion_slider__001_png_181f53f1e2d249138d855513a68bcb4c  # B
  positioning: {product_archetype: rack-driven linear stage — a broad flat T-slot table carriage driven along the guide by the rack, why_same_subcategory: the pinion drives a straight rack that translates the carriage in a line}
  primary_axis: {slot: output_carriage, diversity_axis: ③, target_candidate: broad_linear_stage_table}
  structural_delta:
    change: [replace the slim carriage_bridge with a broad flat rectangular stage table (platform) rigidly tied to the rack_bar; add a shallow T-slot / rib pattern loop on the table top; carriage_shoes become the table's guide runners]
    keep_parts: [guide_frame, base_plate, guide_rail, rack_carriage, rack_bar, rack_tooth_{idx}, carriage_shoe_{idx}, pinion, root_wheel, pinion_tooth_{idx}, pinion_spin, rack_slide]
    joint_policy: preserve REVOLUTE pinion_spin + PRISMATIC rack_slide (table is part of the sliding rack_carriage)
    interface_policy: table sits above/on guide rail, rigidly bolted to rack bar; rides the fixed guide without penetration
  multiplicity: {applies: true, target_n: null, copied_object: table_slot_rib, placement_rule: even across table top}
  companion_variations: {allowed_④⑤⑥: [table proportion, palette], forbidden: [joint change, rack cross-section change, drive-topology change]}
  acceptance_focus: [broad table carriage reads as a stage, rides guide without floating, slide+spin work, compiles]

- variant_id: rec_rack_and_pinion_slider_var_skeleton_traveling_pinion
  source_type: forked_anchor
  parent_record_id: rec_robotics__rack_and_pinion_slider__002_png_74acaa0d7f234f268f9a71467cd6a0bb  # A
  positioning: {product_archetype: rack-and-pinion hoist / gantry-axis drive — a fixed rack bolted to the frame while a pinion carriage climbs along it, why_same_subcategory: still a pinion meshing a straight rack producing relative linear travel}
  primary_axis: {slot: drive_skeleton, diversity_axis: ①, target_candidate: fixed_rack_traveling_pinion_carriage}
  structural_delta:
    change: [make straight_rack FIXED to the frame (bolted the full length); introduce a moving pinion_carriage part that carries the pinion + its bearings; move the PRISMATIC joint onto the carriage (frame->carriage) and mount the REVOLUTE pinion on the carriage]
    keep_parts: [frame, base_plate, guide_rail_{0,1}, straight_rack, pinion, toothed_wheel, hub, pinion_shaft, pinion_spin, rack_slide]
    joint_policy: relocate the single PRISMATIC to the pinion carriage; keep exactly one REVOLUTE pinion; rack becomes fixed
    interface_policy: carriage rides the guide rails; pinion overhangs and meshes the fixed rack; no floating
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [carriage proportion, palette], forbidden: [add second pinion, rack cross-section change, envelope change]}
  acceptance_focus: [rack fixed to frame, carriage+pinion translates along fixed rack, mesh maintained, compiles]

- variant_id: rec_rack_and_pinion_slider_var_skeleton_cantilever_pinion
  source_type: forked_anchor
  parent_record_id: rec_robotics__rack_and_pinion_slider__002_png_74acaa0d7f234f268f9a71467cd6a0bb  # A
  positioning: {product_archetype: motor-mounted overhung pinion — pinion supported on one side only by a single bearing block / gearmotor face, why_same_subcategory: a cantilevered spur pinion still meshes and drives the straight rack}
  primary_axis: {slot: pinion_support, diversity_axis: ①, target_candidate: cantilever_overhung_one_side_support}
  structural_delta:
    change: [remove one bearing_cheek/boss pair so the pinion is carried by a single-side support block (add a stub gearmotor/bearing housing on one cheek); pinion_shaft becomes a cantilever stub bolted into that one block]
    keep_parts: [frame, base_plate, guide_rail_{0,1}, bearing_cheek_0, pinion_shaft, rack_carriage, straight_rack, carriage_block, pinion, toothed_wheel, hub, pinion_spin, rack_slide]
    joint_policy: preserve REVOLUTE pinion_spin (now one-side supported) + PRISMATIC rack_slide
    interface_policy: single-side support block carries the shaft cantilever; pinion face still meshes rack
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [motor-block proportion, palette], forbidden: [add second pinion, rack cross-section change, envelope change]}
  acceptance_focus: [pinion supported from one side only (no floating), mesh preserved, spin+slide work, compiles]

- variant_id: rec_rack_and_pinion_slider_var_n2_dual_pinion
  source_type: forked_anchor
  parent_record_id: rec_robotics__rack_and_pinion_slider__001_png_181f53f1e2d249138d855513a68bcb4c  # B
  positioning: {product_archetype: dual-pinion anti-backlash rack drive — two pinions meshing one rack for stiffness/preload, why_same_subcategory: still pinion(s) meshing a straight rack driving linear travel}
  primary_axis: {slot: pinion_multiplicity, diversity_axis: N, target_candidate: 2_pinions}
  structural_delta:
    change: [emit the pinion as a pinion_{k} instance loop (k in range(2)) sharing the tooth-loop helper; place the two pinions at even +X offsets along the shaft line, both meshing the same rack; each gets its own REVOLUTE pinion_spin_{k}]
    keep_parts: [guide_frame, base_plate, guide_rail, bearing_web_{idx}, bearing_collar_{idx}, rack_carriage, rack_bar, rack_tooth_{idx}, root_wheel, pinion_tooth_{idx}, rack_slide]
    joint_policy: copy the primary REVOLUTE to N=2 synchronized pinion joints; preserve the single PRISMATIC rack_slide
    interface_policy: both pinions mesh the shared rack at the pitch line; supports duplicated per pinion
  multiplicity: {applies: true, target_n: 2, copied_object: pinion sub-assembly (root_wheel + pinion_tooth loop + hub), placement_rule: even X spacing on shared shaft axis}
  companion_variations: {allowed_④⑤⑥: [palette], forbidden: [rack cross-section change, envelope change, drive-topology change]}
  acceptance_focus: [two loop-emitted pinions both mesh the rack, two REVOLUTE joints, indexed names, compiles]

- variant_id: rec_rack_and_pinion_slider_var_n44_long_rack
  source_type: forked_anchor
  parent_record_id: rec_robotics__rack_and_pinion_slider__001_png_181f53f1e2d249138d855513a68bcb4c  # B
  positioning: {product_archetype: long-stroke rack-and-pinion slider (extended rack for long linear travel), why_same_subcategory: only rack tooth count / length changes}
  primary_axis: {slot: rack_multiplicity, diversity_axis: N, target_candidate: 44}
  structural_delta:
    change: [change rack_tooth_{idx} loop count 30 -> 44 (range extended) at the same tooth_pitch; lengthen rack_bar and base to carry the longer rack; extend prismatic travel accordingly]
    keep_parts: [guide_frame, base_plate, guide_rail, rack_carriage, rack_bar, rack_tooth_{idx}, rack_end_cap_{idx}, pinion, root_wheel, pinion_tooth_{idx}, pinion_spin, rack_slide]
    joint_policy: preserve REVOLUTE pinion_spin + PRISMATIC rack_slide (longer travel range)
    interface_policy: unchanged mesh; longer rack still carried on base over full length
  multiplicity: {applies: true, target_n: 44, copied_object: rack_tooth trapezoid, placement_rule: even half-pitch along +X}
  companion_variations: {allowed_④⑤⑥: [base length proportion, palette], forbidden: [rack cross-section change, add pinion, envelope change]}
  acceptance_focus: [44 evenly-spaced rack teeth, longer travel, indexed names, mesh preserved, compiles]

- variant_id: rec_rack_and_pinion_slider_var_n16_short_rack
  source_type: forked_anchor
  parent_record_id: rec_robotics__rack_and_pinion_slider__001_png_181f53f1e2d249138d855513a68bcb4c  # B
  positioning: {product_archetype: short-stroke compact rack-and-pinion slider (short rack for a small linear stroke), why_same_subcategory: only rack tooth count / length changes}
  primary_axis: {slot: rack_multiplicity, diversity_axis: N, target_candidate: 16}
  structural_delta:
    change: [change rack_tooth_{idx} loop count 30 -> 16 at the same tooth_pitch; shorten rack_bar and base; reduce prismatic travel accordingly]
    keep_parts: [guide_frame, base_plate, guide_rail, rack_carriage, rack_bar, rack_tooth_{idx}, rack_end_cap_{idx}, pinion, root_wheel, pinion_tooth_{idx}, pinion_spin, rack_slide]
    joint_policy: preserve REVOLUTE pinion_spin + PRISMATIC rack_slide (shorter travel range)
    interface_policy: unchanged mesh; shorter rack still carried on base over full length
  multiplicity: {applies: true, target_n: 16, copied_object: rack_tooth trapezoid, placement_rule: even half-pitch along +X}
  companion_variations: {allowed_④⑤⑥: [base length proportion, palette], forbidden: [rack cross-section change, add pinion, envelope change]}
  acceptance_focus: [16 evenly-spaced rack teeth, shorter travel, indexed names, mesh preserved, compiles]
```

## 7. Blocked / Excluded
- Pinion-tooth-count N fork: excluded — origins already show {22 (B), 28 (A)}; recorded as ⑤/N record_only, not swept.
- Extra rack-length N samples beyond {16, 30, 44}: excluded — copy logic already exposed by three samples.
- Bearing-support style as a standalone anchor (cheek vs torus collar): recorded (both origins show a straddle style); only the distinct cantilever/overhung support is forked (skeleton_cantilever_pinion).
- Handwheel / knob / gearmotor input as a standalone variant: excluded — it is an added ④-level input decoration on the same REVOLUTE, not a new joint type; recorded only.
- Curved / sector / helical rack: excluded — drifts toward gear-sector / worm-drive neighbors, not honestly a straight-rack slider.
- Belt / lead-screw / plain-rail alternatives: excluded as neighbor categories (see must_not_become).

## 8. Emitted Jobs
8 jobs in `/tmp/jobs/rack_and_pinion_slider.jobs.txt`, all counted forked_anchors: form_round_rack (③), form_enclosed_tube (③), carriage_linear_table (③), skeleton_traveling_pinion (①), skeleton_cantilever_pinion (①), n2_dual_pinion (N/①), n44_long_rack (N), n16_short_rack (N). No compatibility_probe. Total candidate anchors = 2 origins + 8 forks = 10 (simple band).
