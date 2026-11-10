# 0611 / kitchen_cabinet - template source map

pattern: kitchen base/wall cabinet with carcass, doors or drawers, pulls, shelves, and sliding/hinged access
parents: 5 origin records from `picture/0611/kitchen_cabinet`
canonical_baselines: none
underfilled_reason: none after refill 20260713; origin pool plus three passed access variants reaches 8 source-backed anchors for second-gate review

## Slot Candidates

| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| cabinet_body | original kitchen cabinet forms | ①/③ | origin_anchor | 5 origin records in `data/index/subcat/0611__kitchen_cabinet.jsonl` | carcass, doors/drawers, shelves, handles, hinges/slides | origin |
| access_module | three-drawer stack base cabinet | N / ③ | forked_anchor | `rec_kitchen_cabinet_var_drawer_stack` | drawer_i loop, slide rails, pulls; 3 non-fixed joints | PASS |
| access_module | double-door sink-base cabinet | ②/③ | forked_anchor | `rec_kitchen_cabinet_var_double_door_sink_base` | paired tall doors, hinge joints, center reveal; 2 non-fixed joints | PASS |

## Multiplicity / Copy Logic

- count_param: drawer count, door count, shelf count, pull count.
- N samples: 3-drawer stack fork; 2-door sink-base fork; origin-specific doors/drawers.
- suggested N_range: drawers 1-5; doors 1-2; shelves 0-3; pulls match access count.
- copied object / naming / placement / joint policy: drawer_i loops use uniform prismatic slides; door_i loops use mirrored revolute hinges and consistent center reveal.

| access_module | lift-up wall cabinet door with stay arms | ② / ③ | forked_anchor | `rec_kitchen_cabinet_var_lift_up_wall_cabinet_refill` | wall cabinet carcass, shelves, upward lift door, side stay arms; 3 non-fixed joints | PASS |

## Six-Axis Diversity Record

| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / structural topology | source-backed | original cabinet bodies plus sink-base/access variants |
| ② joint / mechanism type | source-backed | revolute hinged doors, prismatic sliding drawers |
| ③ primary form family | source-backed | drawer-stack cabinet, double-door sink-base, original cabinet forms |
| ④ surface decoration | record_only | pulls, rails, panel reveals, countertop/sink hints as host-conformal details |
| ⑤ proportion / size / travel | source-backed | drawer spacing, door reveal, slide travel, cabinet height/width |
| ⑥ material / palette / finish | record_only | painted wood/MDF, metal pulls, laminate/countertop surfaces |

## Compatibility Probes

None yet.

## Blocked / Excluded

- Freestanding wardrobe, hutch, bookcase, appliance enclosure: excluded as neighboring categories unless source image clearly belongs to kitchen cabinetry.
