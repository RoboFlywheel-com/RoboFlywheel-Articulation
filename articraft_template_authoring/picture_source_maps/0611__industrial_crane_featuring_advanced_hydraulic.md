# 0611 / industrial_crane_featuring_advanced_hydraulic — template source map

pattern: mixed (mobile frame + boom/hoist + hydraulic actuator + hook)
parents: 2 origin records from `picture/0611/industrial_crane_featuring_advanced_hydraulic`
canonical_baselines: none
underfilled_reason: refill 20260713 added telescoping-boom, counterweighted-base, and knuckle-boom anchors; still short of the normal 8-anchor budget by 2 source-backed anchors (gantry/wall-jib retries did not converge in this run)

## Slot Candidates

| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| frame_topology | original mobile hydraulic crane frames | ① | origin_anchor | 2 origin records in `data/index/subcat/0611__industrial_crane_featuring_advanced_hydraulic.jsonl` | frame, boom, boom_extension, hook, hydraulic cylinder/rod, caster/wheel loops | origin |
| frame_topology | foldable hydraulic shop crane | ① | forked_anchor | `rec_industrial_crane_hydraulic_var_foldable_shop` | splayed legs, mast, boom, extension, hook, jack/cylinder, pump handle; 14 non-fixed joints | PASS |
| frame_topology | portable gantry with trolley/hoist | ① | blocked/retry_needed | `rec_industrial_crane_hydraulic_var_gantry_trolley` planned from origin 002 | A-frame supports, overhead beam, trolley prismatic, hook lift | no persisted record |

## Multiplicity / Copy Logic

- count_param: caster count, brace count, optional A-frame side supports.
- N samples: 6 caster origin; 4 caster foldable shop crane fork.
- suggested N_range: casters 4-6; braces 2-8 depending topology.
- copied object / naming / placement / joint policy: caster_i and wheel_i loops with continuous swivel/spin joints; braces static host visuals unless part of a moving support.

| boom_mechanism | multi-stage telescoping hydraulic boom | ② / N | forked_anchor | `rec_industrial_crane_hydraulic_var_telescoping_boom_refill` | nested boom stages, extension cylinder, hook at final stage; 20 non-fixed joints | PASS |
| frame_topology | compact counterweighted shop crane base | ① | forked_anchor | `rec_industrial_crane_hydraulic_var_counterweight_base_refill` | rear counterweight block, outrigger legs, mast, hydraulic boom, hook; 14 non-fixed joints | PASS |
| frame_topology | portable gantry with trolley/hoist | ① | blocked/retry_needed | `rec_industrial_crane_hydraulic_var_gantry_trolley_refill` | A-frame supports, overhead beam, trolley prismatic, hook lift | provider timeout/no persisted record |
| boom_mechanism | articulated knuckle-boom crane | ② | forked_anchor | `rec_industrial_crane_hydraulic_var_knuckle_boom_refill` | primary boom, secondary jib, hydraulic cylinders, hook; 20 non-fixed joints | PASS |
| frame_topology | pedestal/wall jib crane | ① | blocked/retry_needed | `rec_industrial_crane_hydraulic_var_wall_jib_refill` | mast, yawing jib, trolley/hook, hydraulic assist | interrupted before persisted record |

## Six-Axis Diversity Record

| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / structural topology | partial source-backed | origin mobile crane + foldable shop crane PASS; gantry trolley retry_needed |
| ② joint / mechanism type | source-backed | boom revolute, boom extension prismatic, hydraulic rod prismatic, hook continuous, caster swivel/spin, pump handle revolute |
| ③ primary form family | partial source-backed | mobile wheeled hydraulic crane, foldable shop crane; gantry not yet converged |
| ④ surface decoration | record_only | hazard labels, painted steel gussets, chain texture, host-conformal only |
| ⑤ proportion / size / travel | record_only | boom pitch and extension travel inherited from origins/fork; caster count changes 6 to 4 |
| ⑥ material / palette / finish | record_only | painted steel, rubber wheels, zinc/chrome pins, black hydraulic body |

## Compatibility Probes

None yet.

## Blocked / Excluded

- `rec_industrial_crane_hydraulic_var_gantry_trolley`: stopped due unresponsive fork; retry or replace with a simpler A-frame hoist candidate.
- Tower crane, forklift, pallet jack, excavator: excluded as neighboring categories.
