# 0611 / Folding_table3 - template source map

status: P3 variant pool confirmed; 11 high-quality samples synced to downstream arti-template with rating=5
pattern: round or oval drop-leaf dining table with folding trestle/leg-frame supports
parents:
- rec_picturex_0611__folding_table3__001__png_27f22d79ac0b41399c93ce8a594e2746 - pictureX/0611/Folding_table3/001.png
- rec_picturex_0611__folding_table3__002__png_1d2b460cfb1f4c52b963597c7ee88e86 - pictureX/0611/Folding_table3/002.png
canonical_baselines: none
underfilled_reason: origin-only pool has 2 anchors; P2 now has 9 full-validated structural forks for 11 candidate anchors total.

## Slot Candidates
| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| tabletop_family | clipped circular center strip with two hinged round leaves | primary_form/mechanism | origin_anchor | rec_picturex_0611__folding_table3__001__png_27f22d79ac0b41399c93ce8a594e2746 | `center_table`, `leaf_{i}`, `center_to_leaf_{i}` REVOLUTE | converged |
| tabletop_family | oval/round dining table with narrow center section and two larger leaves | primary_form/mechanism | origin_anchor | rec_picturex_0611__folding_table3__002__png_1d2b460cfb1f4c52b963597c7ee88e86 | `center_section`, `leaf_{i}`, `center_to_leaf_{i}` REVOLUTE | converged |
| support_topology | independent folding legs under fixed center | skeleton/mechanism | origin_anchor | 001 | `leg_{i}`, `center_to_leg_{i}` REVOLUTE | converged |
| support_topology | folding leg frames carried by leaves | skeleton/mechanism | origin_anchor | 002 | `leg_frame_{i}`, `leaf_to_leg_frame_{i}` REVOLUTE | converged |
| brace_lock | no visible separate brace, center-supported legs | skeleton | origin_anchor | 001 | bounded leg pivots, hinge plates | converged |
| brace_lock | paired locking braces between frame and table | mechanism | origin_anchor | 002 | `locking_brace_{i}`, `frame_to_locking_brace_{i}` REVOLUTE | converged |

## Multiplicity / Copy Logic
- count_param: `leaf_count`, `leg_or_frame_count`, `brace_count`.
- N samples: 2 leaves in both origins; 2 or more leg assemblies; 2 locking braces in 002.
- suggested N_range: leaves fixed at 2 for this subcategory; leg/frame assemblies 2-4 depending on top span; brace count 0 or 2.
- copied object / naming / placement / joint policy: mirror `leaf_{i}` across the center strip; mirror leg frames and braces with revolute hinges at visible underside rails.

## Six-Axis Diversity Record
| axis | treatment | values / range / reason |
|---|---|---|
| skeleton / structural topology | source-backed | center-strip table with separate folding legs; leaf-carried folding leg frames with locking braces |
| joint / mechanism type | source-backed | leaf hinges, leg-frame hinges, brace hinges |
| primary form family | source-backed | round/clipped-circle drop-leaf table, oval dining table |
| surface decoration | record_only | wood grain grooves, seam gaps, hinge plates, rubber feet |
| proportion / size / travel | record_only | leaf open angle about 90 deg; leg deployment about 90 deg; radius/span from source models |
| material / palette / finish | record_only | warm wood top, black metal support frames, dark hinge hardware |

## Compatibility Probes
| probe | record_id | combined axes | risk tested | result |
|---|---|---|---|---|
| none yet | - | - | only origin anchors; cross-combining brace/no-brace with different leaf geometry needs template-time gating | pending |

## Blocked / Excluded
- Fixed round dining table with lazy susan: belongs to Folding_table4, not this drop-leaf class.
- Camp roll-top/slat table and workbench: neighboring folding-table families.
- More than two leaves: category drift unless a new image source shows that topology.

## Stage Status
- Source map complete from existing workbench origins.
- First hard gate: original assets confirmed by user on 2026-07-12.
- Current phase: variant pool confirmed by user on 2026-07-13; high-quality samples synced to downstream `arti-template` with `rating=5` and `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`.
- Next step: write or update the modular spec/template against the enlarged 11-sample high-quality pool, then run the template scan harness.
## Downstream Sync - 2026-07-13
- Variant pool confirmed by user.
- Synced 11 records for this subcategory into `<ARTI_SKILL_ROOT>/arti-template`.
- Target metadata verified: `rating=5`, `rated_by=picturex_0611_tables_turnstile_pruner_press_generator_variant_confirmed_20260713`, and `model.urdf` materialization present for every synced record.
