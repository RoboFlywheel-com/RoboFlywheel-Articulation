# Source Map — Workspace / Adjustable monitor arm

slug `adjustable_monitor_arm` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_workspace__adjustable_monitor_arm__001_png_57e6935a2f524c8e825817b56262d035` — picture/Workspace/Adjustable monitor arm/001.png
- `rec_workspace__adjustable_monitor_arm__002_png_60e0835a36174ecda3d8a7130e870d31` — picture/Workspace/Adjustable monitor arm/002.png

## Variants generated this batch (8 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_adjustable_monitor_arm_var_base_freestanding` | base_freestanding | PASS | 4 | 1 |
| `rec_adjustable_monitor_arm_var_base_grommet` | base_grommet | PASS | 4 | 1 |
| `rec_adjustable_monitor_arm_var_base_wall` | base_wall | PASS | 4 | 1 |
| `rec_adjustable_monitor_arm_var_joint_pole_prismatic` | joint_pole_prismatic | PASS | 5 | 1 |
| `rec_adjustable_monitor_arm_var_n2` | n2 | PASS | 8 | 1 |
| `rec_adjustable_monitor_arm_var_n3` | n3 | PASS | 12 | 1 |
| `rec_adjustable_monitor_arm_var_skeleton_single_seg` | skeleton_single_seg | PASS | 3 | 1 |
| `rec_adjustable_monitor_arm_var_skeleton_three_seg` | skeleton_three_seg | PASS | 5 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Workspace / Adjustable monitor arm

slug: `adjustable_monitor_arm`
pattern: linear_chain + multiplicity (N arms branching off a shared pole)
richness band: **simple** (10 candidate anchors: 2 origins + 8 forks) — coverage-first, no padding

## Parents (origins, both single-arm in code)
- **A** `rec_workspace__adjustable_monitor_arm__001_png_57e6935a2f524c8e825817b56262d035` — pic `picture/Workspace/Adjustable monitor arm/001.png`. Gas-spring clamp arm WITH a monitor body head. Chain: `desk_clamp -> base_swivel -> lower_arm(FIXED) -> upper_arm(elbow Z) -> tilt_head(wrist_tilt Y) -> vesa_mount(vesa_rotation X)`. Elbow axis Z = horizontal folding swing. Includes full monitor (`monitor_body`, `screen_inset`, bezels).
- **B** `rec_workspace__adjustable_monitor_arm__002_png_60e0835a36174ecda3d8a7130e870d31` — pic `.../002.png`. Pole-clamp arm, bare VESA plate (no monitor). Chain: `clamp_base(+vertical_pole) -> lower_arm(base_swivel Z) -> upper_arm(elbow_pitch Y) -> wrist_head(wrist_tilt Y) -> vesa_plate(vesa_rotation X)`. Elbow axis Y = gas-spring vertical lift. CadQuery tube meshes, loop-emitted VESA fasteners. Cleanest template source → chosen fork parent for all 8 forks.

Note: reference image 002 depicts a **dual-arm** product (two arms on one central pole); the code origin is single-arm, so N=2/N=3 are genuine (source-suggested, fork-converged) multiplicity candidates.

## subcategory_contract
```yaml
subcategory_contract:
  category: Workspace
  subcategory: Adjustable monitor arm
  core_identity: A desk/wall-anchored articulated arm carrying a VESA monitor mount, with multiple real adjustment joints (swivel, lift/fold, tilt, screen rotation).
  must_keep:
    - VESA-style monitor mount terminal (plate or captured monitor head)
    - anchoring interface to desk/wall/surface (clamp, grommet, base, or wall plate)
    - at least one non-fixed arm articulation plus a tilt/rotation head
    - loop/helper-emitted repeated fasteners; supported (non-floating) segments
  must_not_become:
    - fixed TV wall bracket / static monitor stand (no articulation)
    - laptop stand / tablet holder / keyboard tray / desk lamp / microphone boom
    - camera tripod / shelf bracket
  image_evidence:
    - "001: single glossy-black gas-spring arm, C-clamp + thumb-screw at desk edge, vertical post, 2-segment arm, VESA head tilting a portrait monitor"
    - "002: DUAL silver arms on a shared central pole clamped to desk, each arm ends in a VESA head+monitor"
  parent_evidence:
    - "A: desk_clamp with KnobGeometry clamp_knob + clamp_screw + pressure_pad; base_swivel post; 2 gas-spring arm shells; tilt_head + vesa_mount with monitor_body"
    - "B: clamp_base with vertical_pole(0.5m) + C-clamp jaw/screw/pressure_pad; base_swivel_sleeve tube on pole; rounded arm shells; wrist_head + stamped vesa_plate w/ 75/100 fastener grid"
```

## Slot / Candidate Grid
| slot | candidate | axis | source_type | evidence | status |
|---|---|---|---|---|---|
| support_or_base | c_clamp | support | origin_anchor | A `desk_clamp`, B `clamp_base` | converged |
| support_or_base | grommet_mount | support | forked_anchor | fork@B | planned |
| support_or_base | freestanding_weighted_base | support | forked_anchor | fork@B | planned |
| support_or_base | wall_mount_plate | support | forked_anchor | fork@B | planned |
| arm_skeleton | two_segment_arm | ① | origin_anchor | A(lower+upper), B(lower+upper) | converged |
| arm_skeleton | single_segment_tilt | ① | forked_anchor | fork@B | planned |
| arm_skeleton | three_segment_arm | ① | forked_anchor | fork@B | planned |
| elbow_mechanism | horizontal_swing_revolute (Z) | ② | origin_anchor | A `elbow` axis Z | converged |
| elbow_mechanism | gas_spring_lift_revolute (Y) | ② | origin_anchor | B `elbow_pitch` axis Y | converged |
| height_mechanism | pole_prismatic_slider | ② | forked_anchor | fork@B (vertical_pole) | planned |
| head_terminal | captured_monitor_body | ③ | origin_anchor | A `vesa_mount/monitor_body` | converged |
| head_terminal | stamped_vesa_plate | ③ | origin_anchor | B `vesa_plate` | converged |
| multiplicity(N arms) | N=1 single | N | origin_anchor | A, B | converged |
| multiplicity(N arms) | N=2 dual | N | forked_anchor | fork@B (ref 002) | planned |
| multiplicity(N arms) | N=3 triple | N | forked_anchor | fork@B | planned |

Slot coverage: support_or_base 4, arm_skeleton 3, elbow/height mechanism 3, head_terminal 2, multiplicity 3 N-samples. Every supported slot reaches >=2 structurally distinct candidates.

## Six-Axis Diversity Audit
| axis | candidate-anchor? | treatment | values |
|---|---|---|---|
| ① skeleton/topology | yes | source-backed | two_segment(A,B) / single_segment(fork) / three_segment(fork) / N-arm branch(fork N2,N3) |
| ② joint/mechanism | yes | source-backed | swivel revolute(Z), elbow horizontal-swing(Z, A), elbow gas-spring pitch(Y, B), wrist_tilt(Y), vesa_rotation(X); + pole prismatic height slider(fork) |
| ③ primary form family | yes | source-backed | head terminal: volumetric monitor_body(A) vs planar stamped vesa_plate(B); base: C-clamp vs weighted-base volume vs grommet stud vs wall plate(planar) |
| ④ surface decoration | no | record_only / companion | cable clips, bolt/fastener heads, VESA 75/100 grid, thumb-screw knob (KnobGeometry), screen bezels/ribs, badge |
| ⑤ proportion/size/travel | no | record_only | arm shells ~0.33-0.38m; pole ~0.5m; swivel +-pi; elbow +-0.75..1.35; tilt +-0.7..0.85; rotation +-pi |
| ⑥ material/palette | no | record_only | glossy_black / satin_black / brushed_silver-aluminum / warm_gray_powdercoat / dark_hardware |

④/⑤/⑥ are recorded only; they are never standalone variants and are not counted toward the budget.

## Multiplicity / Copy Logic
- count_param: `n_arms`
- N samples: {1 (origins A,B), 2 (fork `var_n2`), 3 (fork `var_n3`)}; suggested N_range [1,4]
- copied_object: the full arm chain (`lower_arm -> upper_arm -> wrist_head -> vesa_plate`) with its 4-joint sub-graph
- placement_rule: radial fan around the shared `vertical_pole` at distinct yaw offsets (and/or stacked pole heights), loop-indexed `arm{idx}_*`
- joint_policy: each copied arm gets its OWN `base_swivel` revolute on the shared pole plus its own `elbow`/`wrist_tilt`/`vesa_rotation`; the pole/clamp stays a single shared root. Loop-emitted, shared helper, stable indexed names — no hand-written repeats.

## Budget Decision
Simple band, 10 candidate anchors (2 origins + 8 forks). Honest structural vocabulary for a monitor arm is moderate: base interface (4), arm-segment count (3), joint mechanism incl. prismatic height (3), N-arm branching (3 samples). No cosmetic/scale/material padding used. `underfilled_reason`: none — 10 anchors is a faithful, coverage-first pool for this class; adding more would require ④/⑤/⑥ padding or category drift (laptop tray / keyboard tray), which is forbidden.

## Blocked / Gated
- laptop_tray / tablet_clamp / keyboard_tray head terminal — **blocked**: drifts to neighbor category (laptop stand / tray), not a monitor arm.
- fixed (zero-articulation) wall bracket — **blocked**: violates must_keep articulation; wall variant retained ONLY as full-motion articulated wall arm.
- ball-joint head — **blocked** as separate ②: SDK models it as tilt(Y)+rotation(X) already present in origins; not structurally distinct.

## Variant Cards
```yaml
- variant_id: rec_adjustable_monitor_arm_var_base_grommet
  source_type: forked_anchor
  parent_record_id: B
  positioning: {product_archetype: through-desk grommet-mount monitor arm, why_same_subcategory: same articulated VESA arm, only the desk-anchoring interface changes}
  primary_axis: {slot: support_or_base, diversity_axis: ③/support, target_candidate: grommet_mount}
  structural_delta:
    change: [replace C-clamp jaw assembly with a top washer + downward threaded stud through desk + under-desk backing flange/nut]
    keep_parts: [vertical_pole, thrust_collar, base_swivel, lower_arm, upper_arm, wrist_head, vesa_plate]
    joint_policy: preserve all arm joints; add no new joint
    interface_policy: grommet stud/washer clamps the desktop from above and below instead of a C-jaw
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_456: [silver vs black finish], forbidden: [changing arm skeleton or joints]}
  acceptance_focus: [pole still stands upright above the mount; swivel still yaws arm]

- variant_id: rec_adjustable_monitor_arm_var_base_freestanding
  source_type: forked_anchor
  parent_record_id: B
  positioning: {product_archetype: freestanding weighted-base desk monitor stand-arm, why_same_subcategory: articulated VESA arm on a portable weighted base instead of a clamp}
  primary_axis: {slot: support_or_base, diversity_axis: ③/support, target_candidate: freestanding_weighted_base}
  structural_delta:
    change: [replace clamp jaw/screw/saddle with a flat weighted oval/disc base plate carrying the vertical_pole]
    keep_parts: [vertical_pole, base_swivel, lower_arm, upper_arm, wrist_head, vesa_plate]
    joint_policy: preserve all arm joints
    interface_policy: pole rises from a broad flat base footprint resting on the desk
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_456: [base disc vs oval outline], forbidden: [arm/joint changes]}
  acceptance_focus: [base footprint supports pole; no floating base]

- variant_id: rec_adjustable_monitor_arm_var_base_wall
  source_type: forked_anchor
  parent_record_id: B
  positioning: {product_archetype: full-motion wall-mounted monitor arm, why_same_subcategory: identical articulated VESA arm anchored to a wall plate rather than a desk clamp}
  primary_axis: {slot: support_or_base, diversity_axis: ③/support, target_candidate: wall_mount_plate}
  structural_delta:
    change: [replace clamp+pole with a flat vertical wall plate + short horizontal stub carrying the base_swivel]
    keep_parts: [base_swivel, lower_arm, upper_arm, wrist_head, vesa_plate]
    joint_policy: preserve all arm joints (must remain articulated, not a fixed bracket)
    interface_policy: wall plate with screw holes; swivel axis reoriented to remain a real arm swing
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_456: [plate hole pattern], forbidden: [removing articulation -> fixed bracket]}
  acceptance_focus: [arm still articulates; not a static wall bracket]

- variant_id: rec_adjustable_monitor_arm_var_skeleton_single_seg
  source_type: forked_anchor
  parent_record_id: B
  positioning: {product_archetype: compact single-segment tilt/rotate monitor mount, why_same_subcategory: minimal articulated VESA arm, one arm link + tilt head}
  primary_axis: {slot: arm_skeleton, diversity_axis: "① skeleton", target_candidate: single_segment_tilt}
  structural_delta:
    change: [collapse lower_arm+upper_arm into a single arm segment from the base_swivel to the wrist_head; remove the elbow joint]
    keep_parts: [clamp_base, vertical_pole, base_swivel, wrist_head, wrist_tilt, vesa_plate, vesa_rotation]
    joint_policy: remove elbow_pitch; keep base_swivel + wrist_tilt + vesa_rotation
    interface_policy: single arm shell mates swivel sleeve at root and wrist eye at tip
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_456: [shorter reach], forbidden: [changing base or head form]}
  acceptance_focus: [chain has one arm segment; swivel+tilt+rotation still move]

- variant_id: rec_adjustable_monitor_arm_var_skeleton_three_seg
  source_type: forked_anchor
  parent_record_id: B
  positioning: {product_archetype: long-reach three-segment folding monitor arm, why_same_subcategory: same VESA arm with an extra folding link for reach}
  primary_axis: {slot: arm_skeleton, diversity_axis: "① skeleton", target_candidate: three_segment_arm}
  structural_delta:
    change: [insert a third mid arm segment with its own revolute between lower_arm and upper_arm]
    keep_parts: [clamp_base, vertical_pole, base_swivel, lower_arm, upper_arm, wrist_head, vesa_plate]
    joint_policy: add exactly one mid-fold revolute; preserve base_swivel/elbow_pitch/wrist_tilt/vesa_rotation
    interface_policy: new segment mates via clevis+pin at both ends like the existing elbow
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_456: [longer overall reach], forbidden: [base or head swaps]}
  acceptance_focus: [three arm links present; each fold joint moves independently]

- variant_id: rec_adjustable_monitor_arm_var_joint_pole_prismatic
  source_type: forked_anchor
  parent_record_id: B
  positioning: {product_archetype: pole-mount monitor arm with sliding height collar, why_same_subcategory: same VESA arm; adds a real prismatic height-adjust mechanism on the post}
  primary_axis: {slot: height_mechanism, diversity_axis: "② joint/mechanism", target_candidate: pole_prismatic_slider}
  structural_delta:
    change: [add a height_slider collar part riding PRISMATIC along the vertical_pole; mount base_swivel+arm on the collar]
    keep_parts: [clamp_base, vertical_pole, base_swivel, lower_arm, upper_arm, wrist_head, vesa_plate]
    joint_policy: add one prismatic joint (pole Z); keep base_swivel revolute and downstream arm joints
    interface_policy: collar bore wraps the pole; travel bounded by pole length
  multiplicity: {applies: false, target_n: null, copied_object: null, placement_rule: none}
  companion_variations: {allowed_456: [collar clamp-lever detail], forbidden: [changing base type or arm skeleton]}
  acceptance_focus: [prismatic joint translates arm along pole; swivel still yaws]

- variant_id: rec_adjustable_monitor_arm_var_n2
  source_type: forked_anchor
  parent_record_id: B
  positioning: {product_archetype: dual-monitor arm on shared pole (matches reference 002), why_same_subcategory: two identical VESA arms on one shared clamp/pole}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: n_arms=2}
  structural_delta:
    change: [copy full arm chain twice; each arm gets its own base_swivel on the shared pole]
    keep_parts: [clamp_base, vertical_pole, lower_arm, upper_arm, wrist_head, vesa_plate]
    joint_policy: per-arm base_swivel + elbow_pitch + wrist_tilt + vesa_rotation; shared single root pole
    interface_policy: arms fan at distinct yaw offsets on the pole; loop-emitted arm{idx}_* names
  multiplicity: {applies: true, target_n: 2, copied_object: arm_chain, placement_rule: radial_fan_on_pole}
  companion_variations: {allowed_456: [], forbidden: [changing per-arm skeleton/joint/base type]}
  acceptance_focus: [two independent arms each swivel/fold/tilt; loop-based copy; no float/collide]

- variant_id: rec_adjustable_monitor_arm_var_n3
  source_type: forked_anchor
  parent_record_id: B
  positioning: {product_archetype: triple-monitor arm on shared pole, why_same_subcategory: three identical VESA arms on one shared clamp/pole}
  primary_axis: {slot: multiplicity, diversity_axis: N, target_candidate: n_arms=3}
  structural_delta:
    change: [copy full arm chain three times; each arm gets its own base_swivel on the shared pole]
    keep_parts: [clamp_base, vertical_pole, lower_arm, upper_arm, wrist_head, vesa_plate]
    joint_policy: per-arm base_swivel + elbow_pitch + wrist_tilt + vesa_rotation; shared single root pole
    interface_policy: three arms fan/stack on the pole; loop-emitted arm{idx}_* names
  multiplicity: {applies: true, target_n: 3, copied_object: arm_chain, placement_rule: radial_fan_on_pole}
  companion_variations: {allowed_456: [], forbidden: [changing per-arm skeleton/joint/base type]}
  acceptance_focus: [three independent arms; loop-based copy; no float/collide]
```
