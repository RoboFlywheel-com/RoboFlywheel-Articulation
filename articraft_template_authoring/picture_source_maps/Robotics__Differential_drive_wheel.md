# Source Map — Robotics / Differential drive wheel

slug `differential_drive_wheel` · variant-expansion batch 2026-07-09

## Origin parents
- `rec_use-the-attached-reference-image-picture-robotic_20260707_084323_751535_ed8a6961` — picture/Robotics/Differential drive wheel/001.png
- `rec_robotics__differential_drive_wheel__002_png_2bafd7c2baa94629a23400f40574efad` — picture/Robotics/Differential drive wheel/002.png

## Variants generated this batch (9 verified PASS)

| record_id | axis | verdict | non-fixed joints | compile warnings |
|---|---|---|---|---|
| `rec_differential_drive_wheel_var_belt` | belt | PASS | 3 | 1 |
| `rec_differential_drive_wheel_var_caster` | caster | PASS | 3 | 0 |
| `rec_differential_drive_wheel_var_enclosed_housing` | enclosed_housing | PASS | 5 | 1 |
| `rec_differential_drive_wheel_var_hubdrive` | hubdrive | PASS | 3 | 1 |
| `rec_differential_drive_wheel_var_sideflange` | sideflange | PASS | 3 | 1 |
| `rec_differential_drive_wheel_var_spider_n2` | spider_n2 | PASS | 8 | 1 |
| `rec_differential_drive_wheel_var_spider_n4` | spider_n4 | PASS | 10 | 1 |
| `rec_differential_drive_wheel_var_suspension` | suspension | PASS | 5 | 2 |
| `rec_differential_drive_wheel_var_worm` | worm | PASS | 3 | 1 |

---

## Plan / slots / 6-axis / multiplicity / blocked (planner)

# Variant Plan — Robotics / Differential drive wheel

slug: `differential_drive_wheel`
pattern: **mixed** (parallel children: two coaxial driven wheels + a drive/reduction mechanism hung on a chassis-mount carrier; one origin adds a top swivel link in the chain; gear-train and fastener multiplicity)
richness band: **simple** (8–12) — coverage-first; two genuinely distinct real archetypes but a moderate structural vocabulary
candidate anchors total: **11** (2 origins + 9 forks)
fork jobs emitted: **9**

## Origins (full reconciliation, 2/2 anchored)
| id | pic | built form | grid role |
|---|---|---|---|
| A `rec_use-the-attached-reference-image-picture-robotic_20260707_084323_751535_ed8a6961` | 001 | Educational exposed **bevel differential**: two wheels on a common axle line, open gunmetal carrier, exposed orange ring gear + brass side gear + yellow input pinion, blue motor, green/red half-shafts; single-motor differential split via mimic gear train; 5 continuous joints, rigid (no swivel) | mechanism=bevel_differential / carrier=open_exposed / mount=rear_bridge / steer=rigid |
| B `rec_robotics__differential_drive_wheel__002_png_2bafd7c2baa94629a23400f40574efad` | 002 | Industrial **AGV dual-drive wheel module**: two tan poly wheels, brushed-aluminum enclosed gearboxes, two independent motor cans, rounded top mounting plate + central swivel bearing (limited steering revolute), lift eyes, bolt patterns; 2 continuous wheel joints + 1 revolute swivel | mechanism=dual_independent_motor_gearbox / carrier=enclosed_plate / mount=top_plate / steer=limited_swivel |

## subcategory_contract
```yaml
subcategory_contract:
  category: Robotics
  subcategory: Differential drive wheel
  core_identity: A robot drive module with two wheels on a common transverse axle line, powered/split by a motor+gear mechanism, mounted to a robot chassis so wheel-speed difference produces motion and turning.
  must_keep:
    - two coaxial wheels each with a real continuous spin joint
    - a drive/reduction or differential mechanism (independent motors, or a bevel differential gearset)
    - a chassis-mounting carrier/plate/bracket interface
  must_not_become:
    - Automotive full rear axle (leaf springs, brakes, road car axle)
    - Caster wheel / passive furniture caster
    - Omni / mecanum wheel (rollers on the rim)
    - Bare electric motor or a benched gearbox with no wheels
  image_evidence:
    - 001: exposed orange bevel ring gear meshing a yellow pinion, brass side gear, green+red half-shafts to two treaded wheels, blue drive motor
    - 002: two tan wheels on a shared axle, aluminum gearbox carriage, top mounting plate with central swivel bearing, lift eyes and bolt circles
  parent_evidence:
    - A: parts carrier/left_wheel/right_wheel/orange_gear/brass_side_gear/input_pinion; joints *_spin CONTINUOUS with Mimic gear train; _toothed_bevel_mesh, _annular_cylinder_mesh helpers
    - B: parts mount_plate/drive_carriage/wheel_0/wheel_1; mount_to_carriage REVOLUTE swivel + carriage_to_wheel_i CONTINUOUS; loop-emitted screws/fins; CadQuery plate/bearing/eye-bolt helpers
```

## Slot / Candidate Grid
| slot | candidates (source) | axis |
|---|---|---|
| **drive_mechanism** | bevel_differential(A), dual_motor_gearbox(B), belt_reduction(fork belt), worm_reduction(fork worm), hub_direct_drive(fork hubdrive) | ② |
| **carrier / body form** | open_exposed(A), enclosed_plate_gearbox(B), enclosed_diff_housing(fork enclosed_housing), minimal_hub_bar(fork hubdrive) | ③ |
| **steering_swivel** | rigid_none(A), limited_swivel(B), continuous_caster_slew(fork caster) | ② |
| **mount_interface (support_or_base)** | rear_bridge_plate(A), top_mount_plate(B), vertical_side_flange(fork sideflange) | ③/interface |
| **suspension / skeleton** | rigid_axle(A,B), sprung_rocker_arm(fork suspension) | ① |
| **differential_multiplicity** | simplified_single_side_gear(A baseline), spider_2_pinion(fork spider_n2), spider_4_pinion(fork spider_n4) | N |

Every supported slot reaches ≥2 structurally distinct candidates.

## Mandatory 6-Axis Diversity Audit
| axis | treatment | values / reason |
|---|---|---|
| ① skeleton / topology | source-backed (origin + forked_anchor) | rigid_axle(A,B) vs sprung_rocker_arm (fork suspension adds rocker link + spring joints); B also adds the plate→swivel→carriage chain |
| ② joint / mechanism | source-backed (origin + forked_anchor) | bevel-diff mimic train(A); dual-motor + limited swivel(B); belt, worm, hub-direct reductions (forks); continuous caster slew swivel (fork) |
| ③ primary form family | source-backed (origin + forked_anchor) | open_exposed(A) / enclosed_plate(B) / enclosed cast diff housing (fork) / minimal hub bar (fork) / vertical side-flange mount (fork) |
| ④ surface decoration | record_only / companion | bolt circles, lift eyes, cooling fins, hub screws, gearbox side screws, tread patterns; host-conformal only — no standalone variant |
| ⑤ proportion / size / travel | record_only | wheel Ø ~0.26–0.27; swivel limited ±0.35 vs continuous; gear ratios (input→ring −0.42, side −1.0); tire width ~0.073–0.083; ride only as companion |
| ⑥ material / palette | record_only | tan polyurethane / black rubber tire; brushed-aluminum vs gunmetal carrier; blue motor; anodized colored gears (orange/brass/yellow); never a standalone variant |

## Multiplicity / Copy Logic
- **primary N axis — differential planet/spider pinions**: `count_param n_planet_pinions`; source-backed N samples {2, 4} (forks spider_n2, spider_n4); suggested N_range [2,4]; copied_object `planet_pinion_{i}` via shared `_toothed_bevel_mesh`, radial placement (180° / 90°), uniform mimic joint policy tied to `orange_gear_spin`. Baseline A carries a degenerate single side gear, so both N samples are forked.
- **wheels**: fixed at N=2 (definitional for differential drive — not swept). Each wheel is an independent continuous child; loop-emitted in B (`for i, pos in wheel_positions`).
- **fastener / fin copy logic (record_only, not candidate anchors)**: B loop-emits `plate_screw_i`(8), `bearing_screw_i`(10), `hub_screw_j`(10), `motor_fin_i`(3), `gearbox_screw_{side}_{j}`; A uses `BoltPattern(count=5)` on the rim + `cap_bolt` pairs. These expose copy logic for template sampling but are parametric, not forked.

## Budget Decision
Simple band, 11 candidate anchors (2 origins + 9 forks). Coverage-first: each real slot has ≥2 structurally distinct candidates; mechanism slot is deliberately the richest (5) because the subcategory spans both the mechanical-differential and independent-dual-motor interpretations of "differential drive". No ④/⑤/⑥-only, scale-only, or material-only variants were added. Not padded to the normal band; the honest structural vocabulary tops out around here.
`underfilled_reason` (N samples): the differential spider realistically supports only 2 or 4 planet pinions, so the N axis is covered with 2 samples rather than 3.

## Variant Cards
```yaml
- variant_id: rec_differential_drive_wheel_var_belt
  source_type: forked_anchor
  parent_record_id: B
  primary_axis: {slot: drive_mechanism, diversity_axis: ②, target_candidate: timing_belt_reduction}
  structural_delta: {change: [replace side spur-gearbox blocks with motor pulley + wheel pulley + belt loop per side], keep_parts: [mount_plate, swivel post/bearing, wheel_0, wheel_1, mount_to_carriage, carriage_to_wheel_i], joint_policy: preserve wheel spins + swivel, interface_policy: belt spans pulleys on real motor/axle faces}
  multiplicity: {applies: false}
- variant_id: rec_differential_drive_wheel_var_worm
  source_type: forked_anchor
  parent_record_id: B
  primary_axis: {slot: drive_mechanism, diversity_axis: ②, target_candidate: right_angle_worm_reduction}
  structural_delta: {change: [worm on fore-aft motor shaft meshing a worm wheel on each axle], keep_parts: [mount_plate, wheels, swivel, carriage_to_wheel_i], joint_policy: preserve wheel spins + swivel, interface_policy: worm/worm-wheel right-angle mesh}
  multiplicity: {applies: false}
- variant_id: rec_differential_drive_wheel_var_hubdrive
  source_type: forked_anchor
  parent_record_id: B
  primary_axis: {slot: drive_mechanism, diversity_axis: ②, target_candidate: in_hub_direct_drive}
  structural_delta: {change: [remove external motor/gearbox/axle-stub; slim carrier bar; wheel rim = rotor around fixed stator drum], keep_parts: [mount_plate, swivel, wheel tires/rims, carriage_to_wheel_i], joint_policy: stator fixed to carriage, rim rotates on wheel spins, interface_policy: rim/stator air gap on stub axle}
  multiplicity: {applies: false}
- variant_id: rec_differential_drive_wheel_var_caster
  source_type: forked_anchor
  parent_record_id: B
  primary_axis: {slot: steering_swivel, diversity_axis: ②, target_candidate: continuous_360_caster_slew}
  structural_delta: {change: [mount_to_carriage REVOLUTE→CONTINUOUS; full slew-ring interface], keep_parts: [mount_plate, drive_carriage, wheels, carriage_to_wheel_i], joint_policy: replace exactly the swivel mechanism, interface_policy: large slew ring between plate and carriage}
  multiplicity: {applies: false}
- variant_id: rec_differential_drive_wheel_var_suspension
  source_type: forked_anchor
  parent_record_id: B
  primary_axis: {slot: suspension_skeleton, diversity_axis: ①, target_candidate: sprung_rocker_arm_per_wheel}
  structural_delta: {change: [insert rocker_arm_i link + rocker_pivot_i revolute + spring between arm and carriage; re-parent wheel spin to arm end], keep_parts: [mount_plate, carriage body, wheels, mount_to_carriage], joint_policy: add rocker pivot + preserve wheel spins, interface_policy: spring ends on real faces}
  multiplicity: {applies: false}
- variant_id: rec_differential_drive_wheel_var_sideflange
  source_type: forked_anchor
  parent_record_id: B
  primary_axis: {slot: mount_interface, diversity_axis: ③, target_candidate: vertical_side_flange_bracket}
  structural_delta: {change: [horizontal top plate + central bearing → vertical flange plate + L gusset bracket carrying carriage], keep_parts: [drive_carriage, wheels, carriage_to_wheel_i, swivel post], joint_policy: reorient swivel onto bracket seat, interface_policy: vertical bolt flange + horizontal bracket seat}
  multiplicity: {applies: false}
- variant_id: rec_differential_drive_wheel_var_enclosed_housing
  source_type: forked_anchor
  parent_record_id: A
  primary_axis: {slot: carrier_form, diversity_axis: ③, target_candidate: enclosed_cast_diff_housing}
  structural_delta: {change: [open bridge/cheek carrier → rounded cast housing + two axle tubes + pinion nose + inspection cover], keep_parts: [wheels, orange_gear, brass_side_gear, input_pinion, all *_spin mimic joints], joint_policy: preserve all continuous joints + mimic ratios, interface_policy: axle tubes enclose half-shafts to hubs}
  multiplicity: {applies: false}
- variant_id: rec_differential_drive_wheel_var_spider_n2
  source_type: forked_anchor
  parent_record_id: A
  primary_axis: {slot: differential_multiplicity, diversity_axis: N, target_candidate: spider_2_pinion}
  structural_delta: {change: [single side gear → symmetric side-gear pair + spider cross with 2 loop-emitted planet pinions], keep_parts: [carrier, wheels, orange_gear ring, input_pinion, *_spin], joint_policy: each planet continuous mimic of orange_gear_spin, interface_policy: planets mesh both side gears}
  multiplicity: {applies: true, target_n: 2, copied_object: planet_pinion_{i}, placement_rule: radial 180°}
- variant_id: rec_differential_drive_wheel_var_spider_n4
  source_type: forked_anchor
  parent_record_id: A
  primary_axis: {slot: differential_multiplicity, diversity_axis: N, target_candidate: spider_4_pinion}
  structural_delta: {change: [single side gear → symmetric side-gear pair + spider cross with 4 loop-emitted planet pinions], keep_parts: [carrier, wheels, orange_gear ring, input_pinion, *_spin], joint_policy: each planet continuous mimic of orange_gear_spin, interface_policy: planets mesh both side gears}
  multiplicity: {applies: true, target_n: 4, copied_object: planet_pinion_{i}, placement_rule: radial 90°}
```

## Blocked / Excluded
- wheel-count N-sweep (3/4 wheels): blocked — differential drive is definitionally 2 coaxial wheels; more wheels drift toward a full chassis/rover (out of subcategory).
- chain_drive: excluded — redundant mechanism family with belt_reduction; belt already exposes the flexible-drive template.
- tread/color/tire-material only variants: excluded — ④/⑥ record_only, never standalone anchors.
- compatibility probes: none emitted — no genuinely risky interface combination beyond the single-axis forks above.
