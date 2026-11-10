# 0611 / Dressing_table — template source map
status: P3 confirmed; 7 HQ samples synced to downstream arti-template with rating=5
pattern: floor-supported vanity body + usable top + mirror + articulated storage
parents: 6 confirmed image-conditioned origins (`001.png`–`006.png`)
underfilled_reason: one planned tri-fold-mirror fork was stopped after the same mirror-wing overlap cluster repeated; 6 origins + 1 accepted fork = 7 honest anchors

## Subcategory Contract
```yaml
subcategory_contract:
  category: 0611
  subcategory: Dressing_table
  core_identity: floor-supported dressing vanity combining a usable tabletop, mirror, and accessible storage
  must_keep: [vanity work surface, mirror, storage articulation, floor support]
  must_not_become: [plain writing desk, bathroom sink vanity, loose wall mirror]
```

## Slot Candidates
| slot | candidate | axis | source/evidence | status |
|---|---|---|---|---|
| baseline assembly | six image-backed vanity layouts | mixed | confirmed origins `001`–`006` | confirmed |
| mirror mechanism | lift-top mirror beneath hinged centre tabletop lid | ② | `rec_dressing_table_var_lift_top_mirror` | fork pass |
| mirror topology | independently hinged tri-fold side wings | ① | `rec_dressing_table_var_trifold_mirror` | blocked |

## Multiplicity / Copy Logic
- Drawer/door counts vary among the six origins, but the current pool does not establish a controlled one-axis `N` series; counts remain source records rather than a template multiplicity claim.

## Six-Axis Diversity Record
| axis | treatment |
|---|---|
| ① skeleton / topology | six origin cabinet/leg/mirror layouts; tri-fold candidate blocked |
| ② joint / mechanism | origin drawers/doors plus accepted lift-top mirror lid |
| ③ primary form | source-backed arch, rectangular, pedestal, legged and cabinet vanity envelopes |
| ④ surface decoration | record-only: moulding, knobs, mirror trim |
| ⑤ proportion / travel | record-only: table width/height, drawer depth, lid angle |
| ⑥ material / finish | record-only: painted wood, stained wood, metal pulls, glass mirror |

## Compatibility / Blocked
- No compatibility probe is included.
- `rec_dressing_table_var_trifold_mirror`: stopped after six repeated compile cycles in the same mirror-wing overlap cluster; excluded from accepted anchors rather than force-passed.

## GATE P1 Verification (machine)
- accepted variants: 1; blocked variants: 1; total candidate anchors: 7 (6 origins + 1 fork)
- independent compile: 1/1 accepted fork success; `validation_level=full`; zero blocking signals
- articulation: accepted fork has 4 non-fixed joints
- binding/promotion: `workbench`; bound to `0611 / Dressing_table`; parent lineage present
- underfill is explicit and is not padded with a force-passed tri-fold candidate
- human variant-pool confirmation: 2026-07-14
- downstream sync: 7/7 records copied to `arti-template`, `rating=5`, `collections=[workbench]`, `rated_by=picturex_0611_compass_dressing_drum_elevator_clamps_variant_confirmed_20260714`
