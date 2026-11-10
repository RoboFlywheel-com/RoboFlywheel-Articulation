# PictureX_0611_Ice_crream_machine - Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Ice_crream_machine` |
| template path | `agent/templates/pictureX_0611_Ice_crream_machine.py` |
| test path (optional) | n/a |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all current downstream `rating=5` records for `0611 / Ice_crream_machine` |
| source_index_policy | only the seven adopted 5-star samples below are indexed; `rec_ice_crream_machine_var_open_churner_stand` is excluded because its downstream rating is `0` |

Adopted 5-star records:

| source_id | sample_id | summary |
|---|---|---|
| S1 | `rec_picturex_0611__ice_crream_machine__001__png_f877360c62f94bcc849164b7930e8f80` | coopered wooden bucket freezer, inner canister, head frame, hinged gear cover, hand crank, grip, counter-rotating can/dasher |
| S2 | `rec_picturex_0611__ice_crream_machine__002__png_5ea881a7da9e4a00a7bf5d1390f2178c` | compact manual countertop maker, molded cylindrical housing with D-handle, removable bowl, twist lid, top crank, dasher |
| S3 | `rec_picturex_0611__ice_crream_machine__003__png_efc3f3416f3b42a9b21a9061d85e4469` | cream-painted pail churn, removable spun lid, arched support frame, vertical crank shaft, wood grip, dasher |
| S4 | `rec_picturex_0611__ice_crream_machine__004__png_ee7cae5d293b4afe8ff800e2b09be2f0` | blue/white shaved-ice or frozen-dessert machine, arched chassis, hinged lid, vertical feed press, handwheel, cutter rotor |
| S5 | `rec_ice_crream_machine_var_countertop_compressor` | rectangular electric compressor-style base, motor pod, removable bowl, twist lid, continuously rotating paddle |
| S6 | `rec_ice_crream_machine_var_bucket_churn_refill` | repaired wooden bucket churn with gusseted bearing, head bridge, hinged gear cover, crank, grip, canister and dasher coupling |
| S7 | `rec_ice_crream_machine_var_twin_bowl_refill` | twin-bowl countertop maker, loop-emitted bowl/lid/dasher pairs, side-by-side layout, front control knob |

## 核心身份

Small ice cream or frozen-dessert machine: it must have a supported tub, pail, bowl, canister, hopper, or appliance base; an access lid, bridge, head frame, or feed press; and a visible rotary dasher, paddle, cutter, handwheel, crank, or motor-driven churn mechanism. Adjacent categories excluded: blender/food processor blade jars, drink dispensers, generic storage buckets, coffee grinders, and standalone serving bowls without a moving churn/cutter/dasher.

## 槽位 + 候选模块表

### Slot A：body_family

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| wooden_bucket_canister | forked_anchor | S1 | `_frustum_shell:L22-L45`, body visuals L107-L226, head L228-L300 | eligible if compatible | tapered wood bucket, concentric metal canister, steel bands, bridge/head frame |
| compact_manual_bowl | forked_anchor | S2 | `_housing_shape:L27-L65`, `_bowl_shape:L68-L78`, parts L166-L233 | eligible if compatible | molded cylindrical countertop housing, side D-handle, removable bowl, clear lid hub |
| cream_pail_churn | forked_anchor | S3 | `_make_tub_shell:L60-L72`, `_make_lid:L75-L89`, `_make_support_frame:L92-L127`, parts L197-L231 | eligible if compatible | cream-painted tapered pail, spun lid, arched cast support frame |
| cutter_box_machine | forked_anchor | S4 | `_make_chassis:L55-L112`, `_make_housing:L115-L137`, parts L216-L249 | eligible if compatible | arched side cheeks, rectangular upper chamber, dispensing tray and cutter bay |
| compressor_countertop | forked_anchor | S5 | `_base_shape:L49-L108`, `_motor_pod_shape:L111-L146`, `_bowl_shape:L149-L173`, parts L246-L339 | eligible if compatible | rectangular appliance base, rear motor pod, bowl recess, transparent twist lid |
| bucket_churn_refill | forked_anchor | S6 | bucket/body L107-L226, repaired bearing L285-L308, dasher L379-L405 | eligible if compatible | slatted wooden churn with supported bearing housing and gear cover |
| twin_bowl_countertop | forked_anchor | S7 | `_make_base_housing:L50-L90`, loop bowls/lids/dashers L251-L316, knob L318-L349 | eligible if compatible | wide rectangular base with two repeated bowl/lid/dasher stations and front knob |

### Slot B：access_and_drive

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| side_crank_bridge | forked_anchor | S1, S3, S6 | S1 crank/dasher joints L445-L504; S3 crank/dasher L277-L315; S6 crank/dasher L465-L524 | eligible for bucket/pail families | side or elevated hand crank, free grip, coupled dasher/canister motion |
| top_crank_twist_lid | forked_anchor | S2 | `_crank_shape:L81-L94`, `_dasher_shape:L124-L142`, joints L271-L325 | eligible for compact bowl family | top vertical crank, bayonet/twist lid, removable bowl, mimicked dasher |
| handwheel_press_cutter | forked_anchor | S4 | `_make_handwheel:L165-L177`, `_make_cutter:L180-L194`, feed/cutter joints L287-L357 | eligible for cutter-box family | handwheel and feed press driving lower cutter rotor |
| motor_pod_paddle | forked_anchor | S5 | motor pod L276-L288, paddle L330-L339, joints L343-L391 | eligible for compressor/twin appliance families | motor pod, removable bowl, transparent lid, continuous paddle |
| twin_independent_dashers | forked_anchor | S7 | loop-emitted joints L263-L316 and test assertions L401-L423 | eligible for twin-bowl family | repeated bowl/lid/dasher pairs with independent continuous dasher shafts |

### Slot C：surface_detail_and_palette

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| wood_steel_bands | record_only | S1, S6 | stave/band visuals L122-L172 | eligible | host-embedded staves, bands, side catches; no fixed decoration parts |
| white_clear_appliance | record_only | S2, S5 | materials/details S2 L158-L164, S5 L238-L244 and L260-L328 | eligible | white plastic, transparent lid, metal bowl, control/display details |
| cream_chrome_frame | record_only | S3, S4 | S3 materials L191-L195; S4 materials L210-L214 | eligible | cream/blue painted body with steel or chrome hardware |
| dark_twin_countertop | record_only | S7 | materials L222-L228 and front accent L237-L249 | eligible | dark base, twin stainless bowls, translucent lids, chrome/accent strip |

## 槽位图（slot graph）

pattern: `mixed`

`body_family` is the root chassis/tub/base. `access_and_drive` is emitted as a moving lid/head/drive/dasher mechanism mounted to the root's rim, top collar, side bearing, or front cutter bay. `surface_detail_and_palette` is module-local host visual decoration on the root or moving drive, never a standalone fixed decoration part.

跨 slot 连接与门控：

| body_family | legal access_and_drive | interface policy |
|---|---|---|
| `wooden_bucket_canister`, `cream_pail_churn`, `bucket_churn_refill` | `side_crank_bridge` | bridge or head frame seats on tub rim; side crank axis and vertical dasher shaft share a supported bearing |
| `compact_manual_bowl` | `top_crank_twist_lid` | lid covers bowl mouth; crank and dasher rotate around vertical bowl axis |
| `cutter_box_machine` | `handwheel_press_cutter` | hinged lid/feed press sits over chamber; handwheel/cutter axis is vertical through cutter bay |
| `compressor_countertop` | `motor_pod_paddle` | rear motor pod and lid bore align to central bowl paddle |
| `twin_bowl_countertop` | `motor_pod_paddle`, `twin_independent_dashers` | two bowl stations are symmetric along X; repeated dashers remain centered over each bowl |

## 每槽位 Module Emits / Interfaces

### Slot A / body_family
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `body` containing tub/base/bowls/chassis visuals and embedded details | S1 L107-L226, S2 L166-L233, S3 L197-L231, S4 L216-L249, S5 L246-L339, S7 L230-L260 |
| internal joints | none; static support and decoration fuse into root visuals | AUTHORING Rule 1; source details are host visuals |
| upstream interface | root support plane at base bottom | source bodies |
| downstream interface | top lid plane, side/top drive bearing, bowl centerline(s) | source body/head records |

### Slot B / access_and_drive
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hinged_lid`, `rotary_drive`, `dasher` and optional module-local repeated dasher visuals | S1 L303-L434, S2 L235-L269, S4 L258-L380, S5 L330-L339, S7 L251-L349 |
| internal joints | `body_to_hinged_lid`, `body_to_rotary_drive`, `body_to_dasher`; continuous/revolute/prismatic semantics reduced to safe sampled template axes | S1 L445-L504, S2 L271-L325, S4 L264-L357, S5 L343-L391, S7 L263-L349 |
| upstream interface | rim/hinge/bearing/shaft origin on root `body` | per family gate |
| downstream interface | no serial downstream; moving parts are parallel children of `body` | mixed/parallel pattern |

### Slot C / surface_detail_and_palette
| emits | 描述 | 来源 |
|---|---|---|
| parts | no new parts | AUTHORING Rule 1 |
| internal joints | none | n/a |
| upstream interface | host final body surface, body_family-specific radius/face | S1/S6 bands; S2/S5 controls; S7 front accent |
| downstream interface | none | n/a |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_family` | enum | 7 candidates above | `wooden_bucket_canister` | choice | `config_from_seed` chooses, `resolve_config` gates drive | Slot A |
| `access_and_drive` | enum | 5 candidates above | `side_crank_bridge` | conditional | illegal pair maps to family-compatible mechanism | Slot B |
| `palette_style` | enum | `wood_steel`, `white_clear`, `cream_chrome`, `dark_twin` | `wood_steel` | conditional | family-preferred palette may be overridden by seed | Slot C |
| `body_scale` | float | [0.86, 1.18] | 1.0 | independent | clamp before geometry | source proportions |
| `width_scale` | float | [0.88, 1.20] | 1.0 | independent | clamp before station spacing | S4/S5/S7 wide bases |
| `bowl_count` | int | 1 or 2 | 1 | conditional | `2` only when `body_family=twin_bowl_countertop` | S7 |
| `dasher_blade_count` | int | 2, 3, 4 | 3 | conditional | 4 only for bowl/twin appliance families; otherwise 2-3 | S1/S2/S5/S7 |
| `lid_motion` | float | [0.32, 1.10] rad | 0.75 | independent | revolute lid upper limit; prismatic source semantics represented by safe visible opening | S1/S2/S3/S4/S5/S7 |
| `drive_radius` | float | [0.065, 0.155] | 0.105 | independent | drive visuals remain inside bearing support envelope | S1/S2/S3/S4 |
| `body_height` | float | derived | 0.42 | equation | derived from `body_family`, `body_scale`, and source proportions | source body dimensions |
| `station_spacing` | float | derived | 0.19 | conditional | twin stations use `max(0.17, 0.19*width_scale)`; single uses 0 | S7 L22-L33 |

## 编译预算 / compile budget

Per-seed budget: 12-20s. The implemented template uses primitive boxes/cylinders only, no high-resolution CadQuery booleans; `--compile-timeout 120` is a watchdog, not the target runtime.

## Multiplicity / Copy Logic

- `count_param`: `bowl_count`, `dasher_blade_count`.
- `N_range`: `bowl_count in {1,2}`; `dasher_blade_count in {2,3,4}`.
- copied object / naming / placement / joint policy: twin bowl stations are looped as host visuals on `body` with symmetric `bowl_station_0/1` naming; dasher blades are host visuals on one moving `dasher` part, arranged radially around the shaft. The template does not emit static decoration as fixed child parts.
- source/gating: `bowl_count=2` only for S7-derived `twin_bowl_countertop`; blade counts derive from S1/S2/S5/S7 dasher/cutter repeated blade evidence.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | bucket/pail/apppliance/cutter/twin topologies from S1-S7; moving graph always includes root body + lid/access + rotary drive + dasher/cutter |
| └ multiplicity | 同构件 ×N | 有 | `bowl_count=2` from S7; `dasher_blade_count=2/3/4` from S1/S2/S5/S7 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | continuous/revolute rotary drive and dasher; lid/access represented by revolute safe opening; sources include prismatic bowl/lid/feed in S2/S3/S4/S5/S7 |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | 有 | wooden bucket, compact manual bowl, cream pail, cutter box, compressor rectangle, repaired bucket churn, twin-bowl countertop; all forked_anchor/source-backed |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | bands/staves/control panels/accent strips/transparent lids; all emitted as host visuals derived from body dimensions |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | `body_scale`, `width_scale`, `drive_radius`, `lid_motion`; motion tests cover open lid and rotary drive/dasher quarter-turn; sampled collision check enabled |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | wood+steel, white+clear appliance, cream+chrome/blue, dark twin countertop; material families include wood, plastic, metal, transparent lid |

## 采样与覆盖审计

总组合数：7 `body_family` x gated `access_and_drive` x 4 palettes x 2 bowl count bands x 3 blade counts, with gates reducing illegal body/mechanism pairs.

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` uses `random.Random(seed)` for every seed including `0`; `resolve_config` clamps numeric fields and maps incompatible `access_and_drive` choices to the body-family legal mechanism. `slot_choices_for_seed(seed)` reports `body_family`, `access_and_drive`, `palette_style`, `bowl_count`, and `dasher_blade_count`.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | choose body, compatible mechanism, palette, dimensions, multiplicity | slot choices match resolved config |
| compatibility matrix | body-family gates above | no blender/drink-dispenser drift; drive remains supported by bearing/head |
| controlled local variation | body scale, width scale, drive radius, lid motion | proportions vary without losing bowl/tub/canister identity |
| regression overrides | none | seed 0 not special-cased |
| random sweep | required command: `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1 uv run articraft template sweep-pipeline pictureX_0611_Ice_crream_machine --max-workers 16 --compile-timeout 120` | verdict/pass_rate, axis realization, motion audit, disconnected islands |

| slot | candidate_count | 是否 >=2 | 是否 >=3 | 备注 |
|---|---:|---|---|---|
| body_family | 7 | yes | yes | current 7 rating=5 sources |
| access_and_drive | 5 | yes | yes | gated by body family |
| surface_detail_and_palette | 4 | yes | yes | host visual only |

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names and multiplicity fields.
- `config_from_seed(seed)` is deterministic and handles seed 0 procedurally.
- `resolve_config` gates illegal body/mechanism pairs before build.
- `build_picturex_0611_ice_crream_machine` emits root body, moving lid/access, rotary drive, and dasher/cutter semantics.
- Static decoration remains host visuals, not fixed child parts.
- Moving parts have visible body supports/bearings and targeted `ctx.pose(...)` checks.
- `run_picturex_0611_ice_crream_machine_tests` calls `fail_if_parts_overlap_in_sampled_poses(...)`.
- Bowl/tub/canister identity remains visible for all body families.

## Reject cases

- Uses `rec_ice_crream_machine_var_open_churner_stand` or any other non-5-star source as an adopted module.
- Reads as blender, food processor, drink dispenser, coffee grinder, or generic bucket.
- Has no moving rotary dasher/paddle/cutter/drive mechanism.
- Emits decorative bands, labels, controls, or staves as independent fixed child parts.
- Lid, bridge, drive shaft, or dasher floats without a visible support path.
- Twin-bowl choice fails to show two side-by-side bowl stations.
- Seed sampling silently cycles a small curated table or treats seed 0 as a hand-authored special case.

## 与相邻类别的边界

- 不该混入：blender / food processor - those center on blade jar and motor-base blending, not a churn/freezing bowl/cutter press.
- 不该混入：drink dispenser - no dispensing tap-only appliance without dasher, churn, paddle, or cutter.
- 不该混入：generic storage bucket - bucket-only shapes without head frame, lid, canister, dasher, or crank are outside the category.
- 不该混入：coffee grinder - grinder hoppers and burr mechanisms lack ice-cream/freezing bowl semantics.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Variant pool confirmed by user; spec uses only the seven current downstream 5-star Ice_crream_machine records. |

## 模板实现备注（可选）

- The implementation intentionally keeps the repeated bowl and decoration layers as host visuals to avoid fixed-decoration parts.
- Source prismatic access semantics are represented by safe visible lid/access opening in the first slug template; body-family slot choices preserve the source identity and sweep coverage.
- Broad part-pair overlap allowances in tests are limited to supported bearings, shafts, nested lids, and internal dasher/canister relationships.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | body_family/access | `wooden_bucket_canister`, `side_crank_bridge` | `rec_picturex_0611__ice_crream_machine__001__png_f877360c62f94bcc849164b7930e8f80` | L22-L45, L107-L226, L228-L300, L371-L504 | coopered bucket, bands, canister, bridge, crank/dasher coupling |
| S2 | body_family/access | `compact_manual_bowl`, `top_crank_twist_lid` | `rec_picturex_0611__ice_crream_machine__002__png_5ea881a7da9e4a00a7bf5d1390f2178c` | L27-L78, L166-L233, L235-L325 | compact bowl, twist lid, top crank, removable bowl/dasher |
| S3 | body_family/access | `cream_pail_churn`, `side_crank_bridge` | `rec_picturex_0611__ice_crream_machine__003__png_efc3f3416f3b42a9b21a9061d85e4469` | L60-L127, L197-L231, L247-L315 | cream pail, spun lid, arched frame, vertical crank/dasher |
| S4 | body_family/access | `cutter_box_machine`, `handwheel_press_cutter` | `rec_picturex_0611__ice_crream_machine__004__png_ee7cae5d293b4afe8ff800e2b09be2f0` | L55-L194, L216-L249, L258-L380 | arched cutter chassis, feed press, handwheel, cutter rotor |
| S5 | body_family/access | `compressor_countertop`, `motor_pod_paddle` | `rec_ice_crream_machine_var_countertop_compressor` | L49-L217, L246-L391 | rectangular base, motor pod, removable bowl, transparent lid, paddle |
| S6 | body_family/access | `bucket_churn_refill`, `side_crank_bridge` | `rec_ice_crream_machine_var_bucket_churn_refill` | L107-L226, L285-L308, L379-L524 | repaired bearing/gussets, bucket churn, hinged cover, crank/dasher |
| S7 | body_family/access/multiplicity | `twin_bowl_countertop`, `twin_independent_dashers` | `rec_ice_crream_machine_var_twin_bowl_refill` | L50-L90, L93-L207, L251-L349 | twin bowl station loop, independent dashers, front knob |
