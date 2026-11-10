# 0611 / drum_pedal_with_beater_and_spring_return — template source map
status: P3 confirmed; 6 HQ samples synced to downstream arti-template with rating=5
pattern: hoop-clamped frame -> hinged footboard -> drive transmission -> beater shaft, with automatic return
parents: 1 confirmed image-conditioned origin (`001.png`)
underfilled_reason: two return-spring candidates reached stationary failure clusters and were stopped; 1 origin + 5 accepted forks = 6 honest anchors

## Subcategory Contract
```yaml
subcategory_contract:
  category: 0611
  subcategory: drum_pedal_with_beater_and_spring_return
  core_identity: foot-operated bass-drum pedal transmitting footboard travel to a beater shaft with automatic spring return
  must_keep: [hinged footboard, drive transmission, beater, return spring, drum hoop interface]
  must_not_become: [hi-hat pedal, electronic trigger pad, loose mallet]
```

## Slot Candidates
| slot | candidate | axis | source/evidence | status |
|---|---|---|---|---|
| baseline | single-chain, split heel/footboard, side extension spring | mixed | confirmed origin `001` | confirmed |
| drive transmission | rigid direct-drive link | ② | `rec_drum_pedal_var_direct_drive_link` | fork pass |
| drive transmission | flexible strap around cam | ② | `rec_drum_pedal_var_strap_drive` | fork pass |
| drive form | twin roller-chain rows + wide sprocket | ③ | `rec_drum_pedal_var_double_chain_drive` | fork pass |
| foot platform | continuous longboard | ③ | `rec_drum_pedal_var_longboard` | fork pass |
| foot platform | separately hinged heel plate + short toe board | ① | `rec_drum_pedal_var_split_heel_plate` | fork pass |
| return mechanism | coaxial beater-shaft torsion spring | ② | `rec_drum_pedal_var_torsion_spring_return` | blocked |
| return mechanism | under-board compression spring + plunger | ② | `rec_drum_pedal_var_underboard_compression_return` | blocked |

## Multiplicity / Copy Logic
- The double-chain candidate uses two semantic parallel chain rows, but the pool does not infer an arbitrary chain-row `N`; no multiplicity axis is claimed.

## Six-Axis Diversity Record
| axis | treatment |
|---|---|
| ① skeleton / topology | origin platform plus split hinged heel/toe construction |
| ② joint / mechanism | chain, direct link, strap drive; alternative return mechanisms blocked |
| ③ primary form | single/double chain transmission width and split/longboard platform family |
| ④ surface decoration | record-only: traction perforations, logo plate, knurling |
| ⑤ proportion / travel | record-only: footboard length, cam radius, beater throw |
| ⑥ material / finish | record-only: cast aluminium, steel chain/shaft, felt beater, black coating |

## Compatibility / Blocked
- No compatibility probe is included.
- `rec_drum_pedal_var_torsion_spring_return`: stopped after eight repeated connection-overlap compile cycles.
- `rec_drum_pedal_var_underboard_compression_return`: stopped after seven repeated collision/travel failures.

## GATE P1 Verification (machine)
- accepted variants: 5; blocked variants: 2; total candidate anchors: 6 (1 origin + 5 forks)
- independent compile: 5/5 accepted forks success; `validation_level=full`; zero blocking signals
- articulation: 7–8 non-fixed joints per accepted variant
- binding/promotion: all `workbench`; all bound to `0611 / drum_pedal_with_beater_and_spring_return`; parent lineage present
- underfill is explicit and is not padded with force-passed return-spring candidates
- human variant-pool confirmation: 2026-07-14
- downstream sync: 6/6 records copied to `arti-template`, `rating=5`, `collections=[workbench]`, `rated_by=picturex_0611_compass_dressing_drum_elevator_clamps_variant_confirmed_20260714`
