# 0611 / Garden_pruner - template source map

status: P3 variant pool confirmed; 11 high-quality samples synced to downstream arti-template with rating=5
pattern: handheld garden pruner/shear with crossed handles, blade/anvil or bypass blades, spring, latch, and adjusters
parents:
- rec_picturex_0611__garden_pruner__001__png_1fb3fdfcc83c425f8d55bf2dec1bbb57 - pictureX/0611/Garden_pruner/001.png
- rec_picturex_0611__garden_pruner__002__png_a4fac9c0f0654977b6ccc47b55874c50 - pictureX/0611/Garden_pruner/002.png
- rec_picturex_0611__garden_pruner__003__png_6cb54782a7e4491aa10f109d158e4131 - pictureX/0611/Garden_pruner/003.png
- rec_picturex_0611__garden_pruner__004__png_6897c48ac959415388b3b05470fb9720 - pictureX/0611/Garden_pruner/004.png
canonical_baselines: none
underfilled_reason: origin-only pool has 4 anchors; P2 now has 7 full-validated structural forks for 11 candidate anchors total.

## Slot Candidates
| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| cutter_topology | anvil pruner with blade closing against anvil | skeleton/mechanism | origin_anchor | 001 | `anvil_half`, `blade_half`, single REVOLUTE cutting joint | converged |
| cutter_topology | bypass/crossing blade halves with pivot hub | skeleton/mechanism | origin_anchor | 002/003/004 | `cutting_half`, `anvil_half` or `hook_half`, pivot revolute joints | converged |
| return_mechanism | no separate spring part | primary_form | origin_anchor | 001 | pivot-only | converged |
| return_mechanism | visible return spring and spring seat | mechanism | origin_anchor | 002/003/004 | `return_spring`, `spring_seat`, prismatic/revolute spring-seat joints | converged |
| lock_adjust | latch and adjuster hardware | mechanism | origin_anchor | 002/003/004 | `latch`, `adjuster`, `pivot_nut`, `spring_adjuster` | converged |
| handle_finish | colored or textured grip sleeves | surface/material | origin_anchor | all origins | handle/grip geometry and material | record_only |

## Multiplicity / Copy Logic
- count_param: `handle_half_count`, `spring_coil_count`, `grip_rib_count`.
- N samples: two handle/blade halves; optional one latch; optional one adjuster; spring coil/rib counts encoded as visual loops in models.
- suggested N_range: handle halves fixed at 2; spring coil turns 5-9; grip ribs 4-12; latch optional 0/1; adjuster optional 0/1.
- copied object / naming / placement / joint policy: two halves share a physical pivot; spring coils and grip ribs are host visuals; latch/adjuster get separate constrained joints only when visible.

## Six-Axis Diversity Record
| axis | treatment | values / range / reason |
|---|---|---|
| skeleton / structural topology | source-backed | anvil pruner, bypass/crossing blade pruner, hook-half pruner |
| joint / mechanism type | source-backed | main pivot revolute, dual-half revolute, latch revolute, spring/adjuster prismatic |
| primary form family | source-backed | handheld garden shear/pruner with blade, handle, pivot |
| surface decoration | record_only | grip ribs, blade bevels, pivot screw/nut, latch tabs |
| proportion / size / travel | record_only | opening angle, blade length vs handle length, spring compression travel |
| material / palette / finish | record_only | forged steel blades, colored rubber/plastic grips, metal spring/nut |

## Compatibility Probes
| probe | record_id | combined axes | risk tested | result |
|---|---|---|---|---|
| bypass + latch + spring + adjuster | 002/003/004 | multi-joint accessory stack | several non-fixed children near one pivot | source-backed PASS |

## Blocked / Excluded
- Scissors, hedge shears, loppers with long two-hand handles: neighboring classes unless explicitly sourced.
- Pure static decorative pruner: excluded; must retain a real cutting pivot.
- Electric pruner or powered cutter: category drift.

## Stage Status
- Source map complete from four origins.
- First hard gate: original assets confirmed by user on 2026-07-12.
- Current phase: variant pool confirmed by user on 2026-07-13; high-quality samples synced to downstream `arti-template` with `rating=5` and `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`.
- Next gate: human variant-pool inspection, then high-quality sync/spec/template.
## Downstream Sync - 2026-07-13
- Variant pool confirmed by user.
- Synced 11 records for this subcategory into `<ARTI_SKILL_ROOT>/arti-template`.
- Target metadata verified: `rating=5`, `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`, and `model.urdf` materialization present for every synced record.
