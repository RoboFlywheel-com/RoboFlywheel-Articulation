# PictureX_0611_kitchen_cabinet - Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_kitchen_cabinet` |
| template path | `agent/templates/pictureX_0611_kitchen_cabinet.py` |
| test path (optional) | none |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending_template` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all confirmed 5-star records in `0611 / kitchen_cabinet` |
| source_index_policy | only current confirmed 5-star pool; no blocked/excluded variants |

## 核心身份

Kitchen cabinet: a kitchen base or wall cabinet carcass with panel construction, doors and/or drawers, shelves, pulls, toe/leg support, hinges/slides/stay arms, and kitchen cabinetry proportions. Exclude wardrobe, hutch, bookcase, generic storage box, appliance shell, and full room-scale kitchen set.

## 槽位 + 候选模块表

### Slot A：cabinet_body
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| legged_base_carcass | origin_anchor | `rec_picturex_0611__kitchen_cabinet__001__png_5f29ccaadea944c09b6f9832561aa405`, `002`, `003`, `004`, `005` | `001:L50-L140`, `002:L61-L180`, `003:L189-L286`, `004:L55-L139`, `005:L178-L241` | eligible | white/wood panel carcass, countertop or top deck, recessed toe/legs, side/back/bottom panels |
| wall_carcass | forked_anchor | `rec_kitchen_cabinet_var_lift_up_wall_cabinet_refill` | `L95-L168` | eligible | shallow wall cabinet, top/bottom/side/back panels, shelves, wall cleats, piano hinge barrel |

### Slot B：access_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| single_shaker_door | origin_anchor | `rec_picturex_0611__kitchen_cabinet__001__png...`, `002`, `004` | `001:L142-L227`, `002:L182-L306`, `004:L140-L257` | eligible | one side-hinged full-height shaker/slab door, bar pull, hinge plates |
| double_door_sink_base | forked/origin_anchor | `rec_kitchen_cabinet_var_double_door_sink_base`, plus origin `003` and `005` double-door records | variant `L180-L310`, origin `003:L55-L152`, `005:L243-L293` | eligible | paired side-hinged doors, center reveal, two revolute joints, sink/countertop hint |
| drawer_stack_base | forked_anchor | `rec_kitchen_cabinet_var_drawer_stack` | `L126-L224` | eligible | 2-4 sampled drawer multiplicity, paired slide rails, one prismatic joint per drawer |
| lift_up_wall_cabinet | forked_anchor | `rec_kitchen_cabinet_var_lift_up_wall_cabinet_refill` | `L169-L320` | eligible | top-hinged lift door with bar pull and two mimic stay arms |

### Slot C：finish_and_detail
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| red_white | record_only | all five pictureX origins and three variants | material blocks across records | eligible | white carcass, red fronts, black pulls/legs |
| sage | world_knowledge_extrapolation(④/⑥) | same source geometry, reviewer palette extension | n/a | eligible | same topology; painted kitchen-cabinet finish |
| walnut | world_knowledge_extrapolation(④/⑥) | same source geometry, reviewer palette extension | n/a | eligible | same topology; wood cabinet finish |
| charcoal | world_knowledge_extrapolation(④/⑥) | same source geometry, reviewer palette extension | n/a | eligible | same topology; dark modern finish |

## 槽位图（slot graph）

pattern: mixed

`cabinet_body` is the grounded carcass. `access_module` attaches to its front/top opening using captured side hinges, prismatic drawer slides, or top lift hinge. `finish_and_detail` controls material palette and host-conformal pulls/reveals.

- `legged_base_carcass` supports `single_shaker_door`, `double_door_sink_base`, and `drawer_stack_base`.
- `wall_carcass` supports only `lift_up_wall_cabinet`.
- Hinged doors rotate around vertical front-edge axes; drawer stack travels along `-Y`; lift door rotates around the top-front `X` axis and drives two mimic stay arms.
- Pulls, rails, stiles, reveals, legs, cleats, and countertop/sink hints are visuals on their host part, not fixed child parts.

## 每槽位 Module Emits / Interfaces

### Slot A / module `legged_base_carcass`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `carcass` root with side panels, back panel, bottom/top decks, shelves, countertop, toe rail, legs | origins `001-L60-L140`, `002-L72-L180`, `005-L183-L241` |
| internal joints | none | source fixed cabinetry |
| upstream interface | grounded root | template root |
| downstream interface | front opening plane at `front_y`; side hinge axes; drawer side rail lanes | origins + drawer fork |

### Slot A / module `wall_carcass`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `carcass` root with shallow side/top/bottom/back panels, shelf, wall cleats, top hinge barrel | lift-up fork `L95-L168` |
| internal joints | none | source fixed cabinetry |
| upstream interface | grounded root | template root |
| downstream interface | top-front hinge line and side-wall stay-arm pivot points | lift-up fork |

### Slot B / module `single_shaker_door`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_0` with slab, raised stiles/rails, dark reveal strips, bar pull, hinge leaves | origins `001:L142-L207`, `002:L182-L306`, `004:L140-L257` |
| internal joints | `carcass_to_door_0` REVOLUTE, vertical hinge axis, outward swing | origins |
| upstream interface | captured concealed hinge at front side stile | origins |
| downstream interface | none | terminal access front |

### Slot B / module `double_door_sink_base`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_0`, `door_1`, paired red shaker fronts, center reveal, bar pulls, sink/countertop hint on carcass | double-door fork + origins `003`, `005` |
| internal joints | two REVOLUTE side hinges, mirrored axes, outward swing | variant `L289-L308`, origin `005:L262-L293` |
| upstream interface | left/right front side stiles | source-backed |
| downstream interface | none | terminal access front |

### Slot B / module `drawer_stack_base`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drawer_i` moving fronts/boxes; carcass bridge rails derived from side panels | drawer fork `L126-L224` |
| internal joints | `carcass_to_drawer_i` PRISMATIC, axis `(0,-1,0)`, one per drawer | drawer fork |
| upstream interface | side-mounted slide rails with real carcass contact | drawer fork |
| downstream interface | none | terminal access front |

### Slot B / module `lift_up_wall_cabinet`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lift_door`, `stay_arm_0`, `stay_arm_1`; door slab/frame/pull and gas-strut-like arms | lift-up fork `L169-L320` |
| internal joints | `carcass_to_lift_door` REVOLUTE top hinge; two mimic REVOLUTE stay arms | lift-up fork |
| upstream interface | top-front hinge barrel and side-wall pivot brackets | lift-up fork |
| downstream interface | none | terminal access front |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| access_module | enum | `single_shaker_door`, `double_door_sink_base`, `drawer_stack_base`, `lift_up_wall_cabinet` | `double_door_sink_base` | choice | deterministic procedural sampler | source table |
| palette_style | enum | `red_white`, `sage`, `walnut`, `charcoal` | `red_white` | choice | sampler | §6 / record palettes |
| width | float | base `[0.52,1.02]`, wall `[0.58,0.92]` | `0.78` | conditional | clamped by `access_module` | source proportions |
| depth | float | base `[0.40,0.60]`, wall `[0.28,0.40]` | `0.52` | conditional | wall cabinets are shallow | source proportions |
| height | float | base `[0.72,1.00]`, wall `[0.42,0.62]` | `0.86` | conditional | wall cabinets shorter | source proportions |
| drawer_count | int | `2,3,4` when drawer module; else `0` in slot choices | `3` | conditional | only sampled for `drawer_stack_base` | drawer fork |
| shelf_count | int | `0,1,2` | `1` | independent | carcass visual shelves only | origins + wall fork |
| door_swing | float | `[0.72,1.28]` rad | `1.12` | conditional | side-hinged only; sampled collision checked | door origins |
| drawer_travel | float | `[0.12, min(0.27, depth*0.48)]` | `0.20` | inequality | clamped in `resolve_config` to avoid slide overtravel | drawer fork |
| lift_angle | float | `[0.65,1.12]` rad | `0.95` | conditional | top-hinged only; sampled collision checked | lift-up fork |
| leg_height | float | derived | `height*0.17` | equation | base only, clamp `[0.12,0.16]`; wall `0` | origins |

## compile budget

Per-seed budget: 10-20s. Geometry is simple Box/Cylinder cabinetry with small moving part counts; sweep uses thread-capped workers and 120s watchdog.

## Multiplicity / Copy Logic

- `count_param`: `drawer_count`, `shelf_count`, pull count, stay-arm count.
- `N_range`: drawers `2-4` in template maturity sweep (source fork has 3, procedural extension covers adjacent common cabinet counts); shelves `0-2`; pulls match moving fronts; stay arms fixed `2`.
- copied object / naming / placement / joint policy: `drawer_i` repeats front/box/pull/slide geometry and emits one PRISMATIC joint per drawer; pulls are host visuals on each moving front; shelves are carcass visuals; stay arms are two mimic-driven side supports.

## 视觉多样性 6 轴考察
| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | one side-hinged door, two side-hinged doors, N prismatic drawers, top lift door + two stay arms; forked/origin anchors |
| └ multiplicity | 同构件 ×N | 有 | drawer_count `2-4`, shelf_count `0-2`, stay arms fixed 2; §8 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | REVOLUTE vertical side hinges, PRISMATIC drawer slides, REVOLUTE top lift hinge with mimic stay arms |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | 有 | legged base cabinet, double-door sink base, drawer bank base, shallow wall cabinet; source-backed |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | shaker stiles/rails, dark reveal strips, bar pulls, countertop/sink hint, wall cleats; all host visuals |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | width/depth/height, door_swing, drawer_travel, lift_angle. Motion test plan: sampled collision for all non-fixed joints plus targeted open-pose checks for side doors, drawer travel, and lift door rise |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | red/white source palette plus sage, walnut, charcoal procedural palettes |

## 采样与覆盖审计

总组合数：`4 access_module × 4 palette_style × 3 shelf_count × drawer_count variants where applicable = 72 reachable topology/color/count tuples`。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` uses deterministic `random.Random(seed)` sampling for all ordinary seeds including seed 0. `resolve_config` clamps dimensions and motion by module. `slot_choices_for_seed(seed)` returns `cabinet_body`, `access_module`, `door_family`, `drawer_count`, `shelf_count`, and `palette_style`.

Compatibility matrix: `wall_carcass` only pairs with `lift_up_wall_cabinet`; base carcass pairs with single, double, and drawer modules. Drawer travel is clamped by depth; wall cabinet height/depth are clamped separately.

Controlled local parameterization: width/depth/height vary inside source-like kitchen-cabinet proportions; door/drawer/lift motion stays within sampled collision envelope; slide rails are derived from side-panel and drawer-side geometry to preserve support contact.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | deterministic RNG choices with resolve-time compatibility clamps | slot choices match build choices |
| compatibility matrix | wall access isolated to lift module; base access excludes lift module | no floating fronts; correct body/access pairing |
| controlled local variation | dimensions and travel clamped in `resolve_config` | no side-panel/rail gaps, no drawer overtravel |
| regression overrides | none | ordinary seeds only |
| random sweep | 0-35 plus corner stage via `sweep-pipeline` | pass_rate, axis realization, failed corners |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| cabinet_body | 2 | yes | no | source pool has base vs wall body only |
| access_module | 4 | yes | yes | covers single, double, drawer, lift-up |
| finish_and_detail | 4 | yes | yes | palette/material axis |

## Validator

- `slot_choices_for_seed` returns implemented module names.
- `config_from_seed` uses deterministic procedural sampling for ordinary seeds.
- `resolve_config` clamps module-compatible dimensions, drawer travel, and lift/door angles.
- Critical front/top hinge and slide support points exist as real visuals on carcass and moving parts.
- Side doors have REVOLUTE joints and targeted open-pose outward checks.
- Drawer stack has PRISMATIC joints and targeted drawer travel checks.
- Lift-up wall cabinet has top REVOLUTE hinge, two mimic stay arms, and targeted lift-door rise check.
- `run_picturex_0611_kitchen_cabinet_tests` calls `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)`.

## Reject cases

- zero moving access joints
- generic box/bookcase without kitchen cabinet front hardware
- drawer or door part floating away from carcass
- part-internal visual islands in legs, pulls, rails, cleats, or stiles
- side door opening into the cabinet instead of outward
- drawer travel not along `-Y`
- lift-up door not rising from top hinge
- wall cabinet sampled with base-only access module

## 与相邻类别的边界

- 不该混入：wardrobe / hutch / bookcase（non-kitchen storage furniture; lacks countertop/toe/hinge-drawer kitchen-cabinet cues）
- 不该混入：appliance enclosure（not cabinetry access hardware）
- 不该混入：full kitchen set（room/run-scale assembly rather than one cabinet object）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Variant pool confirmed by user; implementation uses only current 8 confirmed 5-star records as structural sources. |

## 模板实现备注（可选）

- Captured hinges/slides/stay-arm pivots omit `MatingContract` and are guarded by sampled-pose tests.
- Drawer rail x-span is derived from side panel and drawer-side geometry to satisfy support/contact gates.
- Pulls, reveal strips, stiles, cleats, countertop, sink hint, and legs are host visuals.

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | cabinet_body/access | single_shaker_door | `rec_picturex_0611__kitchen_cabinet__001__png_5f29ccaadea944c09b6f9832561aa405` | `L50-L227` | legged carcass, single right-hinged door, pull/legs |
| S2 | cabinet_body/access | single_shaker_door | `rec_picturex_0611__kitchen_cabinet__002__png_241b2c4fbfaa407c837bd61a7fb1b21f` | `L61-L306` | proportions, shelves, concealed hinge and shaker details |
| S3 | cabinet_body/access | double_door_sink_base | `rec_picturex_0611__kitchen_cabinet__003__png_bd4b17b1bb1d45059fc34b510868a618` | `L55-L286` | paired doors, center divider, countertop |
| S4 | cabinet_body/access | single_shaker_door | `rec_picturex_0611__kitchen_cabinet__004__png_5a44a3fb595d482486a4d5792aac684a` | `L55-L257` | single left-hinged door, toe/leg details |
| S5 | cabinet_body/access | double_door_sink_base | `rec_picturex_0611__kitchen_cabinet__005__png_32d18ad6c4bc42d1850e18a6ce8fa5cb` | `L178-L293` | two-door base cabinet, hinge cups/pulls |
| S6 | access_module | drawer_stack_base | `rec_kitchen_cabinet_var_drawer_stack` | `L126-L224` | drawer multiplicity, slide rails, prismatic travel |
| S7 | access_module | double_door_sink_base | `rec_kitchen_cabinet_var_double_door_sink_base` | `L180-L310` | paired sink-base doors and mirrored hinges |
| S8 | cabinet_body/access | lift_up_wall_cabinet | `rec_kitchen_cabinet_var_lift_up_wall_cabinet_refill` | `L95-L320` | wall carcass, lift door, mimic stay arms |
