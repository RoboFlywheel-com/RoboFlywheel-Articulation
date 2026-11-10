# 0611 / Folding_table5 - template source map

status: P3 variant pool confirmed; 11 high-quality samples synced to downstream arti-template with rating=5
pattern: mobile half-round drop-leaf table with swing-out gate supports and optional casters
parents:
- rec_picturex_0611__folding_table5__001__png_1ac9d775a5de4deaa6918c2b8db999a4 - pictureX/0611/Folding_table5/001.png
- rec_picturex_0611__folding_table5__002__png_2402f0a0895c48cfa6267157874c2050 - pictureX/0611/Folding_table5/002.png
- rec_picturex_0611__folding_table5__003__png_ef8fdc887f014728a345a684122913c2 - pictureX/0611/Folding_table5/003.png
canonical_baselines: none
underfilled_reason: origin-only pool has 3 anchors; P2 now has 8 full-validated structural forks for 11 candidate anchors total.

## Slot Candidates
| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| tabletop_family | round drop-leaf top with narrow central spine | primary_form/mechanism | origin_anchor | 001 | `center`, `front_leaf`, `rear_leaf`, leaf hinges REVOLUTE | converged |
| tabletop_family | one horizontal and one upright half-round leaf | primary_form/mechanism | origin_anchor | 002 | `horizontal_leaf`, `upright_leaf`, bounded leaf hinges | converged |
| tabletop_family | rectangular fixed depth with two semicircular leaves | primary_form/mechanism | origin_anchor | 003 | `front_leaf`, `rear_leaf`, `_semicircle_panel` | converged |
| support_topology | swing gate supports under each leaf | skeleton/mechanism | origin_anchor | 001/002/003 | `front_gate`/`rear_gate` or `gate_{i}`, gate pivots REVOLUTE | converged |
| mobility | stationary gate-supported table | skeleton | origin_anchor | 001/002 | no wheel parts | converged |
| mobility | caster forks and wheels on mobile base | skeleton/mechanism | origin_anchor | 003 | `caster_fork_{i}`, `caster_wheel_{i}`, CONTINUOUS wheel joints | converged |

## Multiplicity / Copy Logic
- count_param: `leaf_count`, `gate_count`, `caster_count`.
- N samples: 2 leaves; 2 gates; 0 or 2 casters.
- suggested N_range: leaf_count fixed at 2; gate_count 2; caster_count 0, 2, or 4 if a future source supports four casters.
- copied object / naming / placement / joint policy: mirror leaves and gate supports front/rear; caster wheel joints are continuous, fork may be fixed or swivel only if sourced.

## Six-Axis Diversity Record
| axis | treatment | values / range / reason |
|---|---|---|
| skeleton / structural topology | source-backed | central spine, swing gate supports, optional caster base |
| joint / mechanism type | source-backed | leaf hinges, gate support pivots, caster wheel continuous rotation |
| primary form family | source-backed | circular/half-round leaves, rectangular fixed bay plus semicircular leaves |
| surface decoration | record_only | wood grain grooves, seam lines, hinge knuckles, small caster brackets |
| proportion / size / travel | record_only | leaf raise/drop range, gate swing around 90 deg, top length 0.88-1.20m in sources |
| material / palette / finish | record_only | wood veneer top, dark metal supports, rubber/plastic caster wheels |

## Compatibility Probes
| probe | record_id | combined axes | risk tested | result |
|---|---|---|---|---|
| caster + two swing gates | rec_picturex_0611__folding_table5__003__png_ef8fdc887f014728a345a684122913c2 | mobility + gate support + dual leaves | moving supports with mobile base | source-backed PASS |

## Blocked / Excluded
- Lazy-susan round table: different mechanism, see Folding_table4.
- Camp slat table or fixed workbench: category drift.
- More than two drop leaves and unsourced caster swivel forks: hold until new source/fork.

## Stage Status
- Source map complete from reworked origins.
- First hard gate: original assets confirmed by user on 2026-07-12.
- Current phase: variant pool confirmed by user on 2026-07-13; high-quality samples synced to downstream `arti-template` with `rating=5` and `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`.
- Next gate: human variant-pool inspection, then high-quality sync and modular spec/template.
## Downstream Sync - 2026-07-13
- Variant pool confirmed by user.
- Synced 11 records for this subcategory into `<ARTI_SKILL_ROOT>/arti-template`.
- Target metadata verified: `rating=5`, `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`, and `model.urdf` materialization present for every synced record.
