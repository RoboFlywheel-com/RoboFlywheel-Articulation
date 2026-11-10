# 0611 / ergonomic_clamp_with_adjustable — template source map
status: P3 confirmed; 8 HQ samples synced to downstream arti-template with rating=5
pattern: desk clamp -> repositionable support arm -> wrist interface -> padded forearm support
parents: 1 confirmed image-conditioned origin (`001.png`)
underfilled_reason: none — 1 origin + 7 accepted forks = 8 candidate anchors

## Subcategory Contract
```yaml
subcategory_contract:
  category: 0611
  subcategory: ergonomic_clamp_with_adjustable
  core_identity: desk-clamped adjustable forearm support with a padded support surface and repositionable arm
  must_keep: [desk clamp, adjustable support arm, forearm pad, real joints]
  must_not_become: [hand clamp, monitor arm, laptop tray]
  classification_note: the authoritative image depicts a desk-mounted forearm support; this image identity governs the source map despite the legacy picture label
```

## Slot Candidates
| slot | candidate | axis | source/evidence | status |
|---|---|---|---|---|
| baseline | single articulated arm + one forearm pad + desk C-clamp | mixed | confirmed origin `001` | confirmed |
| arm topology | two-bar parallel linkage | ① | `rec_forearm_support_var_parallel_linkage` | fork pass |
| reach mechanism | horizontal linear rail carriage | ② | `rec_forearm_support_var_linear_rail` | fork pass |
| height mechanism | gas-spring-assisted pivot arm | ② | `rec_forearm_support_var_gas_spring_arm` | fork pass |
| pad topology | separate forearm/wrist pads on articulated yoke | ① | `rec_forearm_support_var_split_pad` | fork pass |
| wrist mechanism | captured ball-and-socket pad joint | ② | `rec_forearm_support_var_ball_socket_wrist` | fork pass |
| base topology | height-adjustable rotary column + radial arm | ① | `rec_forearm_support_var_rotary_column` | fork pass |
| elevation mechanism | toothed ratchet elbow + release lever | ② | `rec_forearm_support_var_ratchet_elbow` | fork pass |

## Multiplicity / Copy Logic
- No arbitrary repeated-part multiplicity is category-defining. Split wrist/forearm pads are two semantic support zones, not an `N` family.

## Six-Axis Diversity Record
| axis | treatment |
|---|---|
| ① skeleton / topology | single arm, parallel linkage, split-pad yoke, rotary column |
| ② joint / mechanism | pivot, linear rail, gas spring, ball socket, planned ratchet elbow |
| ③ primary form | record-only: pad outline and clamp housing envelope |
| ④ surface decoration | record-only: upholstery seam, grip texture, scale marks |
| ⑤ proportion / travel | record-only: reach, column height, pad tilt and wrist sweep |
| ⑥ material / finish | record-only: polymer/foam pad, painted metal, plated spindle |

## Compatibility / Blocked
- No multi-axis probe is included.
- Monitor-arm and laptop-tray conversions are explicitly excluded; the padded forearm-support identity must remain visible.

## GATE P1 Verification (machine)
- accepted variants: 7; total candidate anchors: 8 (1 origin + 7 forks)
- independent compile: 7/7 success; `validation_level=full`; zero blocking signals
- articulation: 9–10 non-fixed joints per variant
- binding/promotion: all `workbench`; all bound to `0611 / ergonomic_clamp_with_adjustable`; parent lineage present
- classification warnings retain the image-faithful desk-mounted forearm-support interpretation
- human variant-pool confirmation: 2026-07-14
- downstream sync: 8/8 records copied to `arti-template`, `rating=5`, `collections=[workbench]`, `rated_by=picturex_0611_compass_dressing_drum_elevator_clamps_variant_confirmed_20260714`
