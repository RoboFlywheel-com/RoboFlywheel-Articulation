# 0611 / Ice_crream_machine — template source map

pattern: mixed (bowl/tub body + lid + rotary dasher/cutter)
parents: 4 origin records from `picture/0611/Ice_crream_machine`
canonical_baselines: none
underfilled_reason: refill 20260713 added bucket churn and twin-bowl anchors; still short of the normal 8-anchor budget by 1 source-backed anchor (soft-serve retry blocked by provider timeout)

## Slot Candidates

| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| body_form | image-specific original ice cream / frozen dessert machines | ③ | origin_anchor | 4 origin records in `data/index/subcat/0611__Ice_crream_machine.jsonl` | source-specific housings, lids, crank/dasher/cutter parts | origin |
| body_form | compact countertop compressor-style maker | ③ | forked_anchor | `rec_ice_crream_machine_var_countertop_compressor` | rectangular base, bowl, lid, paddle/dasher; 3 non-fixed joints | PASS |
| body_form | wooden bucket hand-crank churn | ③ | blocked/retry_needed | `rec_ice_crream_machine_var_bucket_churn` planned from origin 001 | bucket, inner canister, bridge, crank, dasher | no persisted record |

## Multiplicity / Copy Logic

- count_param: optional slats/bands around bucket body, paddle blades.
- N samples: origin-specific only so far.
- suggested N_range: slats 8-16 if bucket churn retry converges; paddle blades 2-4.
- copied object / naming / placement / joint policy: bucket slats should be looped as static host visuals; paddle blades looped or helper-emitted on a single rotating paddle part.

| body_form | wooden bucket hand-crank churn | ③ | forked_anchor | `rec_ice_crream_machine_var_bucket_churn_refill` | slatted bucket, inner canister, bridge/yoke, crank, gear cover, dasher; 6 non-fixed joints | PASS |
| bowl_count | twin-bowl countertop maker | N | forked_anchor | `rec_ice_crream_machine_var_twin_bowl_refill` | loop-emitted bowl_0/1 + dasher_0/1 modules, lids, shared base; 7 non-fixed joints | PASS |
| body_form | soft-serve lever dispenser/freezer | ③ | blocked/retry_needed | `rec_ice_crream_machine_var_soft_serve_lever_refill` | upright cabinet, freezing barrel, dispensing lever, dasher | provider timeout before persisted record |

## Six-Axis Diversity Record

| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / structural topology | partial source-backed | origin machines plus countertop appliance fork; bucket-on-stand topology still retry_needed |
| ② joint / mechanism type | source-backed | continuous paddle/dasher/cutter rotation; lid revolute/twist or removable access; removable bowl/press where present |
| ③ primary form family | partial source-backed | original forms + countertop compressor maker PASS; bucket churn planned but not converged |
| ④ surface decoration | record_only | control panel, transparent lid, bands/slats, small labels, host-conformal only |
| ⑤ proportion / size / travel | record_only | compact countertop appliance proportions; original image proportions retained per source |
| ⑥ material / palette / finish | record_only | plastic/steel/transparent lid; wood/galvanized bucket palette planned but not sourced by a passed fork |

## Compatibility Probes

None yet.

## Blocked / Excluded

- `rec_ice_crream_machine_var_bucket_churn`: stopped due unresponsive fork; retry from origin 001 or 003.
- Blender / food processor / drink dispenser forms: excluded as category drift.
