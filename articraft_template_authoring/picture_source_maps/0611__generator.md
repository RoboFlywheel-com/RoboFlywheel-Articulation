# 0611 / generator - template source map

status: P3 variant pool confirmed; 11 high-quality samples synced to downstream arti-template with rating=5
pattern: small hand-cranked generator / electromagnetic demo with frame, crank, transmission, rotor/armature, coil/magnet details, and terminals
parents:
- rec_picturex_0611__generator__001__png_350ef02be9dc4cdc8a58c6842bafc709 - pictureX/0611/generator/001.png
- rec_picturex_0611__generator__002__png_39eb2ba17a7d498c86c917d6ce57b54e - pictureX/0611/generator/002.png
- rec_picturex_0611__generator__003__png_7e039f67b7a1456d8c640d8c6af56be1 - pictureX/0611/generator/003.png
- rec_picturex_0611__generator__004__png_11d3985262e14371b76e27c16f948615 - pictureX/0611/generator/004.png
canonical_baselines: none
underfilled_reason: origin-only pool has 4 anchors; P2 now has 7 full-validated structural forks for 11 candidate anchors total.

## Slot Candidates
| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| drive_input | single hand crank and grip | mechanism | origin_anchor | 001/003/004 | `crank`, `handle_grip`, CONTINUOUS crank joint, grip REVOLUTE/CONTINUOUS | converged |
| drive_input | dual crank handles | mechanism/multiplicity | origin_anchor | 002 | `crank_0`, `crank_1`, `grip_0`, `grip_1` | converged |
| transmission | direct shaft / pulley drive | mechanism | origin_anchor | 001 | `shaft`, `pulley`, mimic-linked rotor | converged |
| transmission | meshed gear pair / gearbox | mechanism | origin_anchor | 002/004 | `drive_gear`, `driven_gear`, `transfer_crank`, mimic ratios | converged |
| transmission | belt and two pulleys | mechanism | origin_anchor | 003 | `drive_belt`, `drive_pulley`, `generator_pulley`, mimic ratios | converged |
| generator_core | rotor/coil armature in frame | skeleton/mechanism | origin_anchor | all origins | `rotor`, `armature`, `armature_coil`, `armature_rotation` | converged |
| generator_core / frame | U-shaped slotted stator bridge around rotor | skeleton/topology | forked_anchor | `rec_picturex0611_generator_var_slotted_stator_bridge` | `stator_bridge`, `pole_pad_left`, `pole_pad_right`, preserved crank/belt/rotor mimic chain | full-validated |
| electrical_details | terminals/caps/magnets/stator | surface/primary_form | origin_anchor | 001/002/003/004 | `terminal_cap_{i}`, housing/stator details | record_only |

## Multiplicity / Copy Logic
- count_param: `crank_count`, `terminal_count`, `coil_count`, `gear_tooth_count`/visual spoke count.
- N samples: crank_count 1 or 2; terminal caps in 001; coil_count 1 in 004; gear/pulley pairs 2.
- suggested N_range: crank_count 1-2; terminals 2-4; coils 1-3; gear teeth/spokes as visual loops only unless a mesh helper already defines them.
- copied object / naming / placement / joint policy: hand cranks rotate continuously; grips spin on crank pins; gears/pulleys/rotor use mimic-linked continuous joints with physically plausible ratios.

## Six-Axis Diversity Record
| axis | treatment | values / range / reason |
|---|---|---|
| skeleton / structural topology | source-backed | open frame, housing/base, belt-frame demo, geared demo |
| joint / mechanism type | source-backed | continuous crank, shaft, grip, gear/pulley, and rotor joints with mimic coupling |
| primary form family | source-backed | small hand-cranked educational generator/electromagnetic machine |
| surface decoration | record_only | copper coil windings, terminal caps, magnets, fasteners, frame brackets |
| proportion / size / travel | record_only | crank radius, pulley/gear ratio, frame height, rotor clearance |
| material / palette / finish | record_only | painted metal/plastic frame, copper coils, dark belts, metallic shafts |

## Compatibility Probes
| probe | record_id | combined axes | risk tested | result |
|---|---|---|---|---|
| crank + gear train + armature | 002/004 | input + geared transfer + rotor | mimic-coupled rotating chain | source-backed PASS |
| crank + belt drive + rotor | 003 | input + belt/pulley + generator core | belt/pulley layout and ratio | source-backed PASS |

## Blocked / Excluded
- Gasoline generator set, wind turbine, motor-only rotor: neighboring generator categories unless the source shows a small hand-cranked demo.
- Static electrical box with terminals only: excluded; must retain real rotating input/output.
- Unsourced complex commutator/brush animation: keep as visual details unless future model/source supports separate articulation.

## Stage Status
- Source map complete from four origins.
- First hard gate: original assets confirmed by user on 2026-07-12.
- Current phase: variant pool confirmed by user on 2026-07-13; high-quality samples synced to downstream `arti-template` with `rating=5` and `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`.
- Note: planned `rec_picturex0611_generator_var_horseshoe_magnet_frame` stalled on repeated DashScope timeout before materialization; it was replaced by `rec_picturex0611_generator_var_slotted_stator_bridge` on the same origin and one-axis generator-core/frame target.
- Next gate: human variant-pool inspection, then high-quality sync/spec/template.
## Downstream Sync - 2026-07-13
- Variant pool confirmed by user.
- Synced 11 records for this subcategory into `<ARTI_SKILL_ROOT>/arti-template`.
- Target metadata verified: `rating=5`, `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`, and `model.urdf` materialization present for every synced record.
