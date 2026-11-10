# 0611 / full_height_turnstile - template source map

status: P3 variant pool confirmed; 11 high-quality samples synced to downstream arti-template with rating=5
pattern: full-height security turnstile with fixed guard cage and vertical rotating rotor
parents:
- rec_picturex_0611__full_height_turnstile__001__png_6b7e15d6e87242ac98409635abccc39b - pictureX/0611/full_height_turnstile/001.png
- rec_picturex_0611__full_height_turnstile__002__png_da54abc7e8844e8599f629d58357b56e - pictureX/0611/full_height_turnstile/002.png
- rec_picturex_0611__full_height_turnstile__003__png_1ffe2f2c8ebd43499f4e65e482fe1601 - pictureX/0611/full_height_turnstile/003.png
- rec_picturex_0611__full_height_turnstile__004__png_104746ac4b87457a9090aff843d68651 - pictureX/0611/full_height_turnstile/004.png
canonical_baselines: none
underfilled_reason: origin-only pool has 4 anchors; P2 now has 7 full-validated structural forks for 11 candidate anchors total.

## Slot Candidates
| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| guard_frame | full fixed outer cage with top/bottom bearings | skeleton | origin_anchor | all four origins | `frame` / `guard_frame`, floor and overhead pivots | converged |
| rotor_family | three-wing rotor with repeated horizontal bars | mechanism/multiplicity | origin_anchor | 001 | `rotor` meta `wing_count: 3`, `arm_tiers: 11`, `rotor_spin` REVOLUTE | converged |
| rotor_family | vertical spindle rotor in fixed cage | mechanism | origin_anchor | 002/003/004 | `rotor`, `rotor_bearing` or `rotor_spin` REVOLUTE about Z | converged |
| auxiliary_gate | hinged guard/access leaf | mechanism | origin_anchor | 001 | `guard_leaf`, `guard_hinge` REVOLUTE | converged |
| auxiliary_gate | no separate guard leaf | primary_form | origin_anchor | 002/003/004 | fixed frame only | converged |

## Multiplicity / Copy Logic
- count_param: `wing_count`, `arm_tier_count`, `guard_upright_count`.
- N samples: wing_count=3; arm_tiers roughly 8-11; guard upright count around 5 in 001.
- suggested N_range: wing_count 3-4; arm_tier_count 6-12; guard upright count 4-8.
- copied object / naming / placement / joint policy: loop horizontal bars along Z tiers and angular rotor wings around the vertical spindle; all rotor bars are rigid children of one rotating rotor part.

## Six-Axis Diversity Record
| axis | treatment | values / range / reason |
|---|---|---|
| skeleton / structural topology | source-backed | cage frame with overhead/floor bearing, optional side guard leaf |
| joint / mechanism type | source-backed | vertical rotor revolute/indexing joint; optional guard leaf hinge |
| primary form family | source-backed | galvanized full-height security rotor/cage |
| surface decoration | record_only | bearing caps, access control box, welded collars, galvanized tube finish |
| proportion / size / travel | record_only | full human-height frame, lane width, rotor tier count; rotation may be continuous or indexed |
| material / palette / finish | record_only | galvanized steel, dark bearing housings, small access-control panels |

## Compatibility Probes
| probe | record_id | combined axes | risk tested | result |
|---|---|---|---|---|
| rotor + hinged guard leaf | 001 | full cage + rotor + auxiliary gate | two independent moving assemblies in tall frame | source-backed PASS |

## Blocked / Excluded
- Waist-high tripod turnstile: separate class; not a full-height cage.
- Revolving door with panels/glass: category drift.
- Multiple lanes: not sourced here; use only if a new image shows a paired full-height unit.

## Stage Status
- Source map complete from four origins.
- First hard gate: original assets confirmed by user on 2026-07-12.
- Current phase: variant pool confirmed by user on 2026-07-13; high-quality samples synced to downstream `arti-template` with `rating=5` and `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`.
- Next gate: human variant-pool inspection, then spec/template.
## Downstream Sync - 2026-07-13
- Variant pool confirmed by user.
- Synced 11 records for this subcategory into `<ARTI_SKILL_ROOT>/arti-template`.
- Target metadata verified: `rating=5`, `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`, and `model.urdf` materialization present for every synced record.
