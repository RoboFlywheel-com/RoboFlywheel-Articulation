# 0611 / drawing_compass_with_adjustable_legs — template source map
status: P3 confirmed; 8 HQ samples synced to downstream arti-template with rating=5
pattern: two-leg head pivot with marking tip + centre tip; optional radius-control submechanism
parents: 4 confirmed image-conditioned origins (`001.png`–`004.png`)
underfilled_reason: none — 4 origins + 4 accepted forks = 8 candidate anchors

## Subcategory Contract
```yaml
subcategory_contract:
  category: 0611
  subcategory: drawing_compass_with_adjustable_legs
  core_identity: two-legged drawing compass with a shared head pivot, one marking/lead end, one centre point, and adjustable radius
  must_keep: [two supported adjustable legs, head pivot, aligned working tips, real non-fixed adjustment]
  must_not_become: [divider-only caliper, protractor, single-arm beam trammel]
```

## Slot Candidates
| slot | candidate | axis | source/evidence | status |
|---|---|---|---|---|
| baseline assembly | four image-backed compass constructions | mixed | confirmed origins `001`–`004` | confirmed |
| radius control | bow-spring head + threaded spreader | ② | `rec_drawing_compass_var_bow_spring_head` | fork pass |
| radius control | quick-set centre wheel + release arms | ② | `rec_drawing_compass_var_quick_set_center_wheel` | fork pass |
| reach structure | telescoping pencil-leg extension bar | ① | `rec_drawing_compass_var_extension_bar_radius` | fork pass |
| marking end | integrated lead cartridge + collet | ③ | `rec_drawing_compass_var_lead_cartridge` | fork pass |

## Multiplicity / Copy Logic
- No category-defining repeated-part multiplicity is sampled. The two main legs are semantic roles (centre and marking), not an arbitrary `N` array.

## Six-Axis Diversity Record
| axis | treatment |
|---|---|
| ① skeleton / topology | four origin constructions plus telescoping radius extension |
| ② joint / mechanism | origin head adjustments, bow-spring spreader, quick-set centre wheel |
| ③ primary form | pencil clamp versus integrated lead cartridge |
| ④ surface decoration | record-only: knurling, graduation marks, grip texture |
| ⑤ proportion / travel | record-only: leg length, maximum radius, fine-adjust range |
| ⑥ material / finish | record-only: plated steel, brass, blackened hardware, plastic grip |

## Compatibility / Blocked
- No multi-axis compatibility probe is needed for this eight-anchor pool.
- Divider-only, protractor, and single-arm beam-compass conversions are excluded as category drift.

## GATE P1 Verification (machine)
- accepted variants: 4; total candidate anchors: 8 (4 origins + 4 forks)
- independent compile: 4/4 success; `validation_level=full`; zero blocking signals
- articulation: 4–8 non-fixed joints per variant
- binding/promotion: all `workbench`; all bound to `0611 / drawing_compass_with_adjustable_legs`; parent lineage present
- human variant-pool confirmation: 2026-07-14
- downstream sync: 8/8 records copied to `arti-template`, `rating=5`, `collections=[workbench]`, `rated_by=picturex_0611_compass_dressing_drum_elevator_clamps_variant_confirmed_20260714`
