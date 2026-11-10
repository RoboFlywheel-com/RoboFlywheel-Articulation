# 0611 / garlic_press - template source map

status: P3 variant pool confirmed; 11 high-quality samples synced to downstream arti-template with rating=5
pattern: handheld hinged garlic press with cup/basket, plunger, handles, pivot pin, and optional cleaner or insert
parents:
- rec_picturex_0611__garlic_press__001__png_3421a0ddb8c34efba208bce9cae4e306 - pictureX/0611/garlic_press/001.png
- rec_picturex_0611__garlic_press__002__png_c325dc0d44734cf991faad455b7ceee5 - pictureX/0611/garlic_press/002.png
- rec_picturex_0611__garlic_press__003__png_49e1ec7b931140fbbd37cda9296bcafe - pictureX/0611/garlic_press/003.png
- rec_picturex_0611__garlic_press__004__png_b0766f37d84548ec90c8ef55abf0bac0 - pictureX/0611/garlic_press/004.png
- rec_picturex_0611__garlic_press__005__png_4adee0e4c7d2464784e7e05bd7894aa0 - pictureX/0611/garlic_press/005.png
- rec_picturex_0611__garlic_press__006__png_3062a3533457437a8611707aaf3e09f6 - pictureX/0611/garlic_press/006.png
canonical_baselines: none
underfilled_reason: none; 6 origin/external anchors plus 5 full-validated structural forks give 11 candidate anchors total.

## Slot Candidates
| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| body_topology | cup/basket handle plus plunger handle | skeleton/mechanism | origin_anchor | 002/003/005 | `cup_handle`/`basket_handle`, `plunger_handle`/`plunger_arm`, REVOLUTE hinge | converged |
| body_topology | cast press body with upper plunger arm | skeleton/mechanism | origin_anchor | 004 | `press_body`, `plunger_arm`, pivot REVOLUTE | compile-confirmed |
| body_topology | lower body, upper handle, separate plunger link | skeleton/mechanism | origin_anchor | 006 | `lower_body`, `upper_handle`, `plunger`, two REVOLUTE joints | converged |
| cleaner_insert | hinged/removable cleaning insert | mechanism | origin_anchor | 001 | `cleaning_insert`, `basket_arm_to_cleaning_insert` REVOLUTE | converged |
| cleaner_insert | no cleaner insert | primary_form | origin_anchor | 002/003/004/005/006 | cup/perforation only | converged |
| plunger_mechanism | direct plunger carried by upper handle | mechanism | origin_anchor | 001-005 | main hinge drives plunger toward cup | converged |
| plunger_mechanism | self-leveling separate plunger | mechanism | origin_anchor | 006 | main handle hinge plus `plunger_pin` REVOLUTE | converged |

## Multiplicity / Copy Logic
- count_param: `perforation_count`, `tooth_count`, `handle_count`.
- N samples: handle_count=2; perforated cup grid varies by source; cleaner teeth only in 001; plunger link count 1 or 2.
- suggested N_range: perforation rows 3-6, columns 4-8; cleaner teeth 0 or matching perforation columns; handle count fixed at 2.
- copied object / naming / placement / joint policy: cup holes and cleaner teeth are host-conformal repeated details; handles/plunger are articulated by supported pivot pins.

## Six-Axis Diversity Record
| axis | treatment | values / range / reason |
|---|---|---|
| skeleton / structural topology | source-backed | cast body press, cup-handle press, separate lower/upper/plunger press |
| joint / mechanism type | source-backed | main revolute hinge, optional cleaner hinge, optional self-leveling plunger hinge |
| primary form family | source-backed | handheld garlic press with basket/cup and mating plunger |
| surface decoration | record_only | perforation grid, cleaning teeth, cast ribs, handle end holes |
| proportion / size / travel | record_only | open/closed handle angle, cup depth, handle length |
| material / palette / finish | record_only | cast aluminum, stainless steel, plastic/rubber grip accents |

## Compatibility Probes
| probe | record_id | combined axes | risk tested | result |
|---|---|---|---|---|
| cleaner insert + dual handle | 001 | cleaner hinge near pressing cup | extra moving insert without category drift | source-backed PASS |
| self-leveling plunger | 006 | main hinge + secondary plunger hinge | two-joint squeeze mechanism | source-backed PASS |

## Blocked / Excluded
- Nutcracker, citrus press, potato ricer: neighboring press tools but not garlic press.
- Static perforated scoop with no hinge: excluded.
- Motorized/electric mincer: category drift.

## Stage Status
- Source map complete from six origins for structural planning.
- First hard gate: original assets confirmed by user on 2026-07-12.
- Mechanical follow-up: external records 003/004/005 compile-confirmed with `--target full --validate` on 2026-07-12; 003 and 004 have one justified allowed overlap each.
- Current phase: variant pool confirmed by user on 2026-07-13; high-quality samples synced to downstream `arti-template` with `rating=5` and `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`.
- Next gate: human variant-pool inspection, then high-quality sync/spec/template.
## Downstream Sync - 2026-07-13
- Variant pool confirmed by user.
- Synced 11 records for this subcategory into `<ARTI_SKILL_ROOT>/arti-template`.
- Target metadata verified: `rating=5`, `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`, and `model.urdf` materialization present for every synced record.
