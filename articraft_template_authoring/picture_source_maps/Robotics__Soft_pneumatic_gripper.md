# Source Map — Robotics / Soft pneumatic gripper

slug `soft_pneumatic_gripper` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_robotics__soft_pneumatic_gripper__002_png_16a0541b69674c8f87875546ee294d6b` — picture/Robotics/Soft pneumatic gripper/002.png
- `rec_robotics__soft_pneumatic_gripper__001_png_220a1418d3af41bba9fac002123e7ea5` — picture/Robotics/Soft pneumatic gripper/001.png

## Variants generated this batch (7 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_soft_pneumatic_gripper_var_base_wrist_flange` | base_wrist_flange | PASS | 8 | 0 |
| `rec_soft_pneumatic_gripper_var_form_fiber_cylinder` | form_fiber_cylinder | PASS | 8 | 0 |
| `rec_soft_pneumatic_gripper_var_mechanism_multisegment` | mechanism_multisegment | PASS | 5 | 0 |
| `rec_soft_pneumatic_gripper_var_mechanism_span_prismatic` | mechanism_span_prismatic | PASS | 5 | 1 |
| `rec_soft_pneumatic_gripper_var_n3` | n3 | PASS | 6 | 1 |
| `rec_soft_pneumatic_gripper_var_n6` | n6 | PASS | 12 | 1 |
| `rec_soft_pneumatic_gripper_var_skeleton_inline` | skeleton_inline | PASS | 8 | 0 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Robotics / Soft pneumatic gripper (`soft_pneumatic_gripper`)

pattern: **multiplicity + mixed** (rigid pneumatic manifold/mounting root carries N radial or opposing soft bellows fingers as independent REVOLUTE-bend children; per-finger hose-swivel sub-joint; finger/hose/yoke/air-tube loop multiplicity). Origins differ in finger count (2 vs 4), arrangement (opposing linear vs radial cross-rail), and bellow form family.

richness band: **simple (upper end)** — target ~8–10 counted candidate anchors. Honest structural vocabulary is moderate: a soft pneumatic gripper is always a rigid manifold + compliant pressurized bellows fingers that bend inward, so ①/②/③ vocabulary is real but bounded. Coverage-first, no padding.

## 1. Subcategory Contract
```yaml
subcategory_contract:
  category: Robotics
  subcategory: Soft pneumatic gripper
  core_identity: An end-effector whose grasping members are soft, compliant, air-pressurized silicone bellows/actuator fingers mounted to a rigid pneumatic manifold/mounting plate; the fingers bend inward under pneumatic pressure to enclose and grasp fragile or irregular objects.
  must_keep:
    - two or more compliant soft bellows/silicone actuator fingers (not rigid links)
    - a rigid central pneumatic manifold / mounting plate carrying the fingers and routing air
    - visible air routing (hoses, barbed fittings, elbows) feeding the fingers
    - at least one real non-fixed inward-bending articulation per finger (REVOLUTE bend approximating soft curl)
  must_not_become:
    - rigid parallel-jaw / two-finger pneumatic gripper (rigid jaws)
    - vacuum / suction-cup gripper
    - rigid multi-link tendon-driven robot hand
    - granular jamming (universal) gripper
  image_evidence:
    - "001.png: 4 cyan corrugated silicone bellows fingers hanging radially from a drilled round top plate over crossed slotted aluminum rails; central boss; pale pneumatic elbows and hoses beside each finger; fingers point down and curl inward"
    - "002.png: 2 opposing matte-black ribbed-fin silicone bellows jaws under a cross-shaped drilled aluminum plate + machined actuator blocks with clevis cheeks; central barbed fitting + air tube; laser-etched load labels (e.g. Max 1700g); two-jaw opposing grasp"
  parent_evidence:
    - "A (001, radial): manifold(mounting_plate perforated, central_boss, air_manifold_block, rail_x/rail_y crossed slotted rails, standoff_{i}/cap_screw_{i}, per-station yoke_cheek/yoke_bridge/hinge_pin/fixed_elbow/air_tube) + 4x finger_{idx}(actuator_base, soft_neck, bellow=_finger_bellow_geometry stacked oval fins + tip pad, grip_valley_{j}) + 4x hose_connector_{idx}; joints manifold_to_finger_{idx} REVOLUTE bend (independent) + finger_to_connector_{idx} REVOLUTE swivel; radial loop yaw=2*pi*idx/4"
    - "B (002, opposing): manifold(_metal_manifold_shape aluminum frame: top plate, standoffs, actuator blocks, clevis cheeks; screw/hex/port/barb fittings, fixed_air_tube spline, swivel_socket) + finger_0/finger_1(bellows=_finger_shape external ribbed fins) + hose_swivel(elbow_tube); joints finger_0_bend REVOLUTE + finger_1_bend REVOLUTE (mimic of finger_0) + hose_swivel REVOLUTE"
```

## 2. Slots and Candidates
| slot | candidate | axis | source | status |
|---|---|---|---|---|
| finger_multiplicity | N=2 opposing | N | B origin | origin_anchor |
| finger_multiplicity | N=4 radial | N | A origin | origin_anchor |
| finger_multiplicity | N=3 tripod radial | N | fork n3 | forked_anchor |
| finger_multiplicity | N=6 dense radial | N | fork n6 | forked_anchor |
| arrangement_skeleton | opposing linear two-jaw frame | ① | B origin | origin_anchor |
| arrangement_skeleton | radial crossed-rail | ① | A origin | origin_anchor |
| arrangement_skeleton | inline single-rail bank | ① | fork skeleton_inline | forked_anchor |
| bellow_form_family | stacked oval corrugated bellows | ③ | A origin | origin_anchor |
| bellow_form_family | external ribbed-fin (PneuNet) bellows | ③ | B origin | origin_anchor |
| bellow_form_family | smooth fiber-reinforced cylinder | ③ | fork form_fiber_cylinder | forked_anchor |
| actuation_mechanism | single inward REVOLUTE bend (+ hose swivel) | ② | A,B origin | origin_anchor |
| actuation_mechanism | PRISMATIC span-adjust carriage + bend | ② | fork mechanism_span_prismatic | forked_anchor |
| actuation_mechanism | serial multi-segment (2-knuckle) progressive curl | ② | fork mechanism_multisegment | forked_anchor |
| base_mount / support | drilled plate + crossed slotted rails | support | A origin | origin_anchor (record) |
| base_mount / support | machined clevis frame block | support | B origin | origin_anchor (record) |
| base_mount / support | round ISO-9409 wrist flange + bolt circle | ①/support | fork base_wrist_flange | forked_anchor |

Each supported structural slot reaches ≥2 distinct candidates. The base_mount slot is anchored by both origins (plate+rail vs clevis frame) and extended once (wrist flange) because it is a real topology change of the load-carrying root; mimic-coupled vs independent finger bend is recorded (B mimics, A independent), not forked.

## 3. Six-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked_anchor) | opposing linear two-jaw (B); radial crossed-rail (A); inline single-rail bank (skeleton_inline); round wrist-flange root (base_wrist_flange); serial 2-segment finger internal topology (mechanism_multisegment) |
| ② joint / mechanism | source-backed (origin + forked_anchor) | independent inward REVOLUTE bend (A); mimic-coupled REVOLUTE bend (B); per-finger REVOLUTE hose swivel (A,B); PRISMATIC span-adjust slide + bend (span_prismatic); serial REVOLUTE knuckle progressive curl (multisegment) |
| ③ primary form family | source-backed (origin + forked_anchor) | stacked oval corrugated bellows (A); external ribbed-fin PneuNet bellows (B); smooth fiber-reinforced cylinder (form_fiber_cylinder) |
| ④ surface decoration | record_only / world_knowledge_extrapolation | grip_valley insets, dark slot channels, drilled port holes / hex sockets, barbed fittings, laser-etched load labels ("Max 1700g" on B); rib-density and fiber-wrap pattern are host-conformal extrapolations, no dedicated variant |
| ⑤ proportion / size / travel | record_only | finger length ~0.09–0.14 m; bend upper 0.55–0.62 rad; hose swivel ±0.30–0.35 rad; span slide ~0–0.03 m; finger_radius ~0.10 m; rides along only as companion |
| ⑥ material / palette / finish | record_only | cyan/blue silicone (A), matte-black silicone (B); satin/brushed aluminum manifold, off-white nylon fittings, black air tube; extrapolate food-grade white / orange silicone; companion-only |

①②③ + N are the candidate-anchor axes and are all source-backed. ④⑤⑥ are record_only / companion — never standalone, never counted toward budget.

## 4. Multiplicity / Copy Logic
- **count_param (primary):** `n_fingers` — the radial/inline finger-station loop `for idx, yaw in enumerate(...)`.
  - N samples: origin-shown {2 (B, opposing), 4 (A, radial)}; forked radial sweep {3 (n3), 6 (n6)}.
  - suggested N_range: [2, 6].
  - copied object: the whole finger station — `finger_{idx}` (+ `actuator_base`, `soft_neck`, `bellow`, `grip_valley_{j}`), its `hose_connector_{idx}`, and its manifold-side `yoke_cheek_{idx}_{n}` / `yoke_bridge_{idx}` / `hinge_pin_{idx}` / `fixed_elbow_{idx}` / `air_tube_{idx}`.
  - placement: radial even at yaw = 2*pi*idx/N on a fixed finger-circle radius (A family); linear opposing/inline for the two-jaw and bank families.
  - joint policy: one independent REVOLUTE `manifold_to_finger_{idx}` bend per finger about its tangential axis (optionally mimic-coupled to a master, as B does for finger_1).
- **other loops (record_only):** plate screws/standoffs/port holes, wrist-flange bolt circle (`flange_bolt_{i}`, FIXED), grip_valley insets per finger — loop-emitted, indexed, FIXED decoration; recorded, not swept.

## 5. Budget Decision
- Counted candidate anchors (origin_anchor + forked_anchor): **2 origins + 7 forks = 9**.
  - origins: A (N=4 radial, corrugated-oval, crossed-rail), B (N=2 opposing, ribbed-fin, clevis frame)
  - forks: n3, n6 (multiplicity N); skeleton_inline (①); form_fiber_cylinder (③); mechanism_span_prismatic, mechanism_multisegment (②); base_wrist_flange (①/support)
- Not counted: no compatibility probes needed (no genuinely risky cross-slot interface this pool requires).
- `underfilled_reason`: not underfilled — 9 counted anchors sit in the simple band. Structural vocabulary saturates here: a soft pneumatic gripper is always a rigid manifold + compliant pressurized bellows fingers, so beyond finger count, arrangement, actuator form family, actuation mechanism, and base mount the remaining diversity is proportion/palette/decoration (④⑤⑥), which is recorded rather than padded into filler anchors.

## 6. Variant Cards
```yaml
- variant_id: rec_soft_pneumatic_gripper_var_n3
  source_type: forked_anchor
  parent_record_id: rec_robotics__soft_pneumatic_gripper__001_png_220a1418d3af41bba9fac002123e7ea5  # A radial
  positioning: {product_archetype: three-finger tripod soft bellows gripper for round/fragile parts, why_same_subcategory: keeps compliant corrugated silicone bellows fingers bending inward on a pneumatic manifold}
  primary_axis: {slot: finger_multiplicity, diversity_axis: N, target_candidate: 3}
  structural_delta:
    change: [set yaw list to 3 even angles 2*pi*idx/3 reused by every per-finger loop; 3 identical radial finger stations copy-generated]
    keep_parts: [manifold, mounting_plate, central_boss, rail_x, rail_y, yoke_cheek_{idx}_{n}, yoke_bridge_{idx}, hinge_pin_{idx}, fixed_elbow_{idx}, air_tube_{idx}, finger_{idx}, actuator_base, soft_neck, bellow, hose_connector_{idx}, manifold_to_finger_{idx}, finger_to_connector_{idx}]
    joint_policy: preserve one independent REVOLUTE bend per finger + hose swivel
    interface_policy: fingers on fixed finger-circle radius; hinge pins captured in actuator bores
  multiplicity: {applies: true, target_n: 3, copied_object: finger station (finger + hose_connector + yokes/hinge/elbow/air_tube), placement_rule: radial even 2*pi*idx/3}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [form-family/skeleton/joint change, category drift]}
  acceptance_focus: [3 evenly-spaced fingers, indexed names, all bend inward, compiles]

- variant_id: rec_soft_pneumatic_gripper_var_n6
  source_type: forked_anchor
  parent_record_id: rec_robotics__soft_pneumatic_gripper__001_png_220a1418d3af41bba9fac002123e7ea5  # A radial
  positioning: {product_archetype: six-finger dense radial soft bellows gripper for large/heavy irregular items, why_same_subcategory: keeps compliant silicone bellows fingers bending inward on a pneumatic manifold}
  primary_axis: {slot: finger_multiplicity, diversity_axis: N, target_candidate: 6}
  structural_delta:
    change: [set yaw list to 6 even angles 2*pi*idx/6 reused by every per-finger loop; 6 identical radial finger stations copy-generated]
    keep_parts: [manifold, mounting_plate, central_boss, rail_x, rail_y, yoke_cheek_{idx}_{n}, yoke_bridge_{idx}, hinge_pin_{idx}, fixed_elbow_{idx}, air_tube_{idx}, finger_{idx}, actuator_base, soft_neck, bellow, hose_connector_{idx}, manifold_to_finger_{idx}, finger_to_connector_{idx}]
    joint_policy: preserve one independent REVOLUTE bend per finger + hose swivel
    interface_policy: fingers on fixed finger-circle radius; no self-collision at 6 stations
  multiplicity: {applies: true, target_n: 6, copied_object: finger station, placement_rule: radial even 2*pi*idx/6}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [form-family/skeleton/joint change, category drift]}
  acceptance_focus: [6 evenly-spaced fingers, indexed names, all bend inward, compiles]

- variant_id: rec_soft_pneumatic_gripper_var_skeleton_inline
  source_type: forked_anchor
  parent_record_id: rec_robotics__soft_pneumatic_gripper__001_png_220a1418d3af41bba9fac002123e7ea5  # A radial
  positioning: {product_archetype: inline soft-finger gripper bar picking a row above a conveyor, why_same_subcategory: soft bellows fingers still bend under air pressure off a shared manifold beam}
  primary_axis: {slot: arrangement_skeleton, diversity_axis: ①, target_candidate: inline_single_rail_bank}
  structural_delta:
    change: [replace crossed rail_x/rail_y with one long manifold beam along +X; place 4 finger stations at even x = x0 + idx*pitch, yaw=0, all curling same direction]
    keep_parts: [manifold, mounting_plate, central_boss, air_manifold_block, yoke_cheek_{idx}_{n}, yoke_bridge_{idx}, hinge_pin_{idx}, fixed_elbow_{idx}, air_tube_{idx}, finger_{idx}, actuator_base, soft_neck, bellow, hose_connector_{idx}, manifold_to_finger_{idx}, finger_to_connector_{idx}]
    joint_policy: preserve REVOLUTE bend per finger, axis perpendicular to beam
    interface_policy: fingers evenly pitched along one supported beam, not radial
  multiplicity: {applies: false, target_n: 4, copied_object: finger station, placement_rule: linear pitch along beam}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [finger-count change, form-family change, joint change, category drift]}
  acceptance_focus: [fingers in a straight evenly-pitched row on one beam, all bend, compiles]

- variant_id: rec_soft_pneumatic_gripper_var_form_fiber_cylinder
  source_type: forked_anchor
  parent_record_id: rec_robotics__soft_pneumatic_gripper__001_png_220a1418d3af41bba9fac002123e7ea5  # A radial
  positioning: {product_archetype: fiber-reinforced (McKibben/PneuFlex) smooth soft finger gripper, why_same_subcategory: fingers remain compliant air-pressurized bending actuators on the same manifold}
  primary_axis: {slot: bellow_form_family, diversity_axis: ③, target_candidate: smooth_fiber_reinforced_cylinder}
  structural_delta:
    change: [rewrite _finger_bellow_geometry to a smooth slightly-tapered cylinder + rounded distal pad + shallow helical fiber-wrap rib instead of stacked oval chambers; bellow element keeps name bellow]
    keep_parts: [manifold, rail_x, rail_y, central_boss, yoke_bridge_{idx}, hinge_pin_{idx}, fixed_elbow_{idx}, air_tube_{idx}, finger_{idx}, actuator_base, soft_neck, hose_connector_{idx}, manifold_to_finger_{idx}, finger_to_connector_{idx}]
    joint_policy: preserve REVOLUTE inward bend per finger
    interface_policy: smooth actuator seats on actuator_base at soft_neck as before
  multiplicity: {applies: false, target_n: 4, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [silicone palette], forbidden: [finger-count/skeleton/joint change, rigid or vacuum drift]}
  acceptance_focus: [finger reads as smooth fiber-reinforced tube not accordion bellows, bends inward, compiles]

- variant_id: rec_soft_pneumatic_gripper_var_mechanism_span_prismatic
  source_type: forked_anchor
  parent_record_id: rec_robotics__soft_pneumatic_gripper__002_png_16a0541b69674c8f87875546ee294d6b  # B opposing
  positioning: {product_archetype: adjustable-span opposing soft gripper that widens/narrows jaw gap for different object sizes, why_same_subcategory: two jaws stay compliant pressurized silicone bellows bending inward}
  primary_axis: {slot: actuation_mechanism, diversity_axis: ②, target_candidate: prismatic_span_adjust_plus_bend}
  structural_delta:
    change: [insert finger_carriage_{idx} slide part per jaw on the manifold width axis; add PRISMATIC manifold_to_carriage_{idx} (~0-0.03 m); re-parent finger bend joints onto carriages; add visible rail/dovetail + mating block]
    keep_parts: [manifold, machined_manifold, barb_fitting_{idx}, fixed_air_tube, swivel_socket, finger_0, finger_1, bellows, hose_swivel, elbow_tube, finger_0_bend, finger_1_bend, hose_swivel]
    joint_policy: add exactly one PRISMATIC span slide per jaw; preserve REVOLUTE bends (finger_1 mimic kept)
    interface_policy: carriage slides on supported manifold rail, not floating
  multiplicity: {applies: false, target_n: 2, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [finger-count change, form-family change, extra unrelated joints, rigid-jaw drift]}
  acceptance_focus: [prismatic span slide works and is supported, bends preserved, non-fixed joints, compiles]

- variant_id: rec_soft_pneumatic_gripper_var_mechanism_multisegment
  source_type: forked_anchor
  parent_record_id: rec_robotics__soft_pneumatic_gripper__002_png_16a0541b69674c8f87875546ee294d6b  # B opposing
  positioning: {product_archetype: progressive-curl multi-segment soft finger gripper that wraps around objects, why_same_subcategory: both segments are compliant pressurized silicone bellows bending inward on the manifold}
  primary_axis: {slot: actuation_mechanism, diversity_axis: ②, target_candidate: serial_multi_segment_curl}
  structural_delta:
    change: [split each finger bellows into proximal (finger_{idx}) + distal (finger_{idx}_tip) segment parts; add serial REVOLUTE finger_{idx}_knuckle between them; keep proximal manifold bend]
    keep_parts: [manifold, machined_manifold, barb_fitting_{idx}, fixed_air_tube, swivel_socket, finger_0, finger_1, bellows, hose_swivel, elbow_tube, finger_0_bend, finger_1_bend, hose_swivel]
    joint_policy: add exactly one serial REVOLUTE knuckle per finger, parallel bend axis, same inward direction
    interface_policy: distal segment seats on proximal segment tip, supported, no floating
  multiplicity: {applies: false, target_n: 2, copied_object: null, placement_rule: none}
  companion_variations: {allowed_④⑤⑥: [], forbidden: [finger-count change, form-family change, rigid multi-link hand drift]}
  acceptance_focus: [two serial soft segments curl progressively inward, both joints non-fixed, compiles]

- variant_id: rec_soft_pneumatic_gripper_var_base_wrist_flange
  source_type: forked_anchor
  parent_record_id: rec_robotics__soft_pneumatic_gripper__001_png_220a1418d3af41bba9fac002123e7ea5  # A radial
  positioning: {product_archetype: cobot-mounted soft gripper on a round ISO-9409 quick-change wrist flange, why_same_subcategory: same radial soft bellows fingers + pneumatic manifold hang below the round flange}
  primary_axis: {slot: base_mount, diversity_axis: ①, target_candidate: round_iso9409_wrist_flange}
  structural_delta:
    change: [replace rectangular mounting_plate + crossed rail_x/rail_y/slot_x/slot_y with round wrist_flange disk + loop-generated flange_bolt_{i} bolt circle + central pilot bore, concentric above central_boss]
    keep_parts: [manifold, central_boss, air_manifold_block, yoke_cheek_{idx}_{n}, yoke_bridge_{idx}, hinge_pin_{idx}, fixed_elbow_{idx}, air_tube_{idx}, finger_{idx}, actuator_base, soft_neck, bellow, hose_connector_{idx}, manifold_to_finger_{idx}, finger_to_connector_{idx}]
    joint_policy: preserve 4 REVOLUTE finger bends; flange bolts FIXED
    interface_policy: flange concentric on central_boss; fingers still radial under flange
  multiplicity: {applies: false, target_n: 4, copied_object: flange_bolt_{i}, placement_rule: radial even on bolt circle (FIXED)}
  companion_variations: {allowed_④⑤⑥: [flange diameter proportion, aluminum finish], forbidden: [finger/joint/form change, bare-flange or vacuum drift]}
  acceptance_focus: [round flange with even bolt circle replaces rails, fingers still bend, no floating parts, compiles]
```

## 7. Blocked / Excluded
- Granular jamming / universal pouch gripper form: excluded — different subcategory (jamming gripper), category drift.
- Vacuum / suction-cup end-effector: excluded — not a soft pneumatic bellows gripper.
- Extra N samples beyond {2,3,4,6}: excluded — copy logic already exposed across four counts.
- Mimic-coupled vs independent finger bend: recorded (B mimics finger_1→finger_0, A independent), not a standalone fork.
- Tip pad shape, grip-valley density, load-label decals, silicone color: record_only (④/⑤/⑥), not forked.

## 8. Emitted Jobs
7 jobs in `/tmp/jobs/soft_pneumatic_gripper.jobs.txt` (all counted forked_anchors): n3, n6 (N multiplicity), skeleton_inline (①), form_fiber_cylinder (③), mechanism_span_prismatic, mechanism_multisegment (②), base_wrist_flange (①/support). No compatibility probes. Total counted candidate anchors = 2 origins + 7 forks = 9.
