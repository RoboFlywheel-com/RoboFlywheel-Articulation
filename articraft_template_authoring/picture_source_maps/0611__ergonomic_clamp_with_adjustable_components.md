# 0611 / ergonomic_clamp_with_adjustable_components — template source map
status: P3 confirmed; 8 HQ samples synced to downstream arti-template with rating=5
pattern: desk clamp -> multi-joint reach/lift arm -> tray yoke -> supported tilting laptop tray
parents: 2 confirmed image-conditioned origins (`001.png`, `002.png`)
underfilled_reason: none — 2 origins + 6 accepted forks = 8 candidate anchors

## Subcategory Contract
```yaml
subcategory_contract:
  category: 0611
  subcategory: ergonomic_clamp_with_adjustable_components
  core_identity: desk-clamped articulated laptop tray arm with height, reach, and tilt adjustment
  must_keep: [desk clamp, multi-joint arm, supported laptop tray, height or reach adjustment]
  must_not_become: [forearm support, monitor-only VESA arm, static laptop stand]
  classification_note: the authoritative images depict clamp-on articulated laptop tray arms; this image identity governs the source map despite the legacy picture label
```

## Slot Candidates
| slot | candidate | axis | source/evidence | status |
|---|---|---|---|---|
| baseline | two image-backed serial articulated tray arms | mixed | confirmed origins `001`, `002` | confirmed |
| lift mechanism | gas-spring counterbalanced parallelogram | ② | `rec_laptop_tray_arm_var_gas_spring` | fork pass |
| reach mechanism | two-stage telescoping boom | ② | `rec_laptop_tray_arm_var_telescoping_boom` | fork pass |
| reach topology | compact horizontal scissor linkage | ① | `rec_laptop_tray_arm_var_scissor_linkage` | fork pass |
| tray interface | quick-release dovetail + locking lever | ② | `rec_laptop_tray_arm_var_quick_release_yoke` | fork pass |
| clamp topology | wide dual-screw clamp base | ① | `rec_laptop_tray_arm_var_dual_screw_clamp` | fork pass |
| tray mechanism | fore-aft sliding rails + stop latch | ② | `rec_laptop_tray_arm_var_sliding_tray_rails` | fork pass |

## Multiplicity / Copy Logic
- The dual-screw base contains two semantic clamp spindles for load distribution, not a sampled arbitrary `N`; no multiplicity range is claimed.

## Six-Axis Diversity Record
| axis | treatment |
|---|---|
| ① skeleton / topology | two serial-arm origins, scissor reach, dual-screw base |
| ② joint / mechanism | serial pivots, gas spring, telescoping boom, quick release, sliding tray rails |
| ③ primary form | record-only: tray/yoke and arm-section envelopes |
| ④ surface decoration | record-only: vent slots, anti-slip pads, cable clips |
| ⑤ proportion / travel | record-only: reach, lift, tray slide and tilt ranges |
| ⑥ material / finish | record-only: aluminium arm, steel clamp, black tray, elastomer stops |

## Compatibility / Blocked
- No multi-axis probe is included.
- Monitor-only, forearm-support, and static-stand conversions are excluded as image/category drift.

## GATE P1 Verification (machine)
- accepted variants: 6; total candidate anchors: 8 (2 origins + 6 forks)
- independent compile: 6/6 success; `validation_level=full`; zero blocking signals
- articulation: 10–14 non-fixed joints per variant
- binding/promotion: all `workbench`; all bound to `0611 / ergonomic_clamp_with_adjustable_components`; parent lineage present
- classification warnings retain the image-faithful clamp-on articulated laptop-tray-arm interpretation
- human variant-pool confirmation: 2026-07-14
- downstream sync: 8/8 records copied to `arti-template`, `rating=5`, `collections=[workbench]`, `rated_by=picturex_0611_compass_dressing_drum_elevator_clamps_variant_confirmed_20260714`
