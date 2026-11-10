# 0611 / Folding_table4 - template source map

status: P3 variant pool confirmed; 11 high-quality samples synced to downstream arti-template with rating=5
pattern: round dining table with a central rotating lazy-susan disk
parents:
- rec_picturex_0611__folding_table4__001__png_f4ee4e14e6ee4f2db24e0794cea1976e - pictureX/0611/Folding_table4/001.png
canonical_baselines: none
underfilled_reason: origin-only pool has 1 anchor; P2 now has 10 full-validated structural forks for 11 candidate anchors total.

## Slot Candidates
| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| tabletop_family | full circular dining tabletop | primary_form | origin_anchor | rec_picturex_0611__folding_table4__001__png_f4ee4e14e6ee4f2db24e0794cea1976e | `tabletop`, circular top radius | converged |
| rotating_insert | inset circular lazy-susan tray | mechanism | origin_anchor | same | `lazy_susan`, `tabletop_to_lazy_susan` REVOLUTE about Z | converged |
| support_topology | four slender radial legs | skeleton | origin_anchor | same | `leg_{i}` loop at 45/135/225/315 deg | converged |

## Multiplicity / Copy Logic
- count_param: `leg_count`.
- N samples: 4 legs.
- suggested N_range: keep leg_count=4 unless new sources show pedestal or 3-leg variants.
- copied object / naming / placement / joint policy: legs are fixed host visuals placed radially; lazy-susan is the only required non-fixed revolute part.

## Six-Axis Diversity Record
| axis | treatment | values / range / reason |
|---|---|---|
| skeleton / structural topology | underfilled | only four-leg round table is sourced |
| joint / mechanism type | source-backed | central bearing / turntable revolute joint |
| primary form family | source-backed | round dining table with inset tray |
| surface decoration | record_only | circular seam, underside apron, wood/metal finish |
| proportion / size / travel | record_only | tray radius smaller than tabletop; full continuous or broad limited rotation |
| material / palette / finish | record_only | wood tabletop, darker/metal legs, tray seam contrast |

## Compatibility Probes
| probe | record_id | combined axes | risk tested | result |
|---|---|---|---|---|
| none | - | - | one source only | n/a |

## Blocked / Excluded
- Drop-leaf or folding-leg table: not visible in this source; use Folding_table3/5 for those.
- Pure fixed dining table without rotating tray: excluded because it lacks the sourced articulation.
- Text/labels from the image prompt must not be reproduced.

## Stage Status
- Source map recorded; origin-only pool is underfilled until the planned P2 lazy-susan forks converge.
- First hard gate: original assets confirmed by user on 2026-07-12.
- Current phase: variant pool confirmed by user on 2026-07-13; high-quality samples synced to downstream `arti-template` with `rating=5` and `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`.
- Recommended next step: generate the single-axis lazy-susan forks before template authoring, then stop for variant-pool inspection.
## Downstream Sync - 2026-07-13
- Variant pool confirmed by user.
- Synced 11 records for this subcategory into `<ARTI_SKILL_ROOT>/arti-template`.
- Target metadata verified: `rating=5`, `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`, and `model.urdf` materialization present for every synced record.
