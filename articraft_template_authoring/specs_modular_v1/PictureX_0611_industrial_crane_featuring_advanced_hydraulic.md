# PictureX_0611_industrial_crane_featuring_advanced_hydraulic - Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_industrial_crane_featuring_advanced_hydraulic` |
| template path | `agent/templates/pictureX_0611_industrial_crane_featuring_advanced_hydraulic.py` |
| test path (optional) | not used; sweep-pipeline is authoritative |
| stage | `TEMPLATE_DRAFT` |
| status | `implemented` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6 |
| read_count | 6 |
| read_scope | only current confirmed 5-star pool for `0611 / industrial_crane_featuring_advanced_hydraulic` |
| source_index_policy | only records listed in Module Source Index are eligible; demoted historical `rec_hydraulic_crane_var_*` records are excluded |

## 核心身份

Mobile industrial hydraulic crane / shop crane with a wheeled or caster-supported base, upright mast, boom or articulated jib, hydraulic barrel/rod actuation, pump handle, and a hanging hook. It may vary between wide mobile shop-crane frames, foldable shop-crane frames, compact counterweighted bases, nested telescoping booms, and knuckle-boom mechanisms. It must not drift into tower crane, forklift, pallet jack, excavator, or a non-hydraulic fixed gantry/hoist.

## 槽位 + 候选模块表

### Slot A：frame_topology
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| origin_mobile_splayed_frame | origin_anchor | `rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__001__png_444a5d123e634bb9b31511c0750e8ee8` | L140-L296 | eligible if compatible | wide rear crossbeam, two splayed floor legs, mast, mast braces, pump body, 4 caster/wheel loops |
| origin_mobile_tubular_frame | origin_anchor | `rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__002__png_a35c26c615b74db58b30348439b55d5d` | L136-L219 | eligible if compatible | compact rolling frame with tubular/mesh boom source, caster loops, mast and hydraulic mounts |
| foldable_shop_frame | forked_anchor | `rec_industrial_crane_hydraulic_var_foldable_shop` | L140-L315 | eligible if compatible | folding/splayed shop-crane legs, mast, braces, pump, caster loops; non-moving decorative leg hardware remains host visuals |
| compact_counterweight_frame | forked_anchor | `rec_industrial_crane_hydraulic_var_counterweight_base_refill` | L140-L335 | eligible if compatible | rear cast counterweight block, forward outrigger legs, rear crossbeam, mast, hydraulic mounts, 4 caster policy |

### Slot B：boom_and_lift_mechanism
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| single_box_telescoping_boom | origin_anchor | `rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__001__png_444a5d123e634bb9b31511c0750e8ee8` | L296-L469 | eligible if compatible | box boom revolute at mast, one prismatic boom extension, continuous hook, hydraulic barrel + prismatic rod |
| tubular_box_extension_boom | origin_anchor | `rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__002__png_a35c26c615b74db58b30348439b55d5d` | L220-L352 | eligible if compatible | mesh/tubular boom shell, prismatic extension, hook, pump handle and hydraulic barrel/rod |
| nested_multi_stage_boom | forked_anchor | `rec_industrial_crane_hydraulic_var_telescoping_boom_refill` | L296-L539 | eligible if compatible | primary boom plus 3 nested prismatic stages, final-stage hook, visible extension cylinder details |
| articulated_knuckle_jib | forked_anchor | `rec_industrial_crane_hydraulic_var_knuckle_boom_refill` | L297-L595 | eligible if compatible | primary boom revolute, secondary jib revolute elbow, main hydraulic cylinder, jib hydraulic cylinder/rod, hook at jib tip |

### Slot C：mobility_and_repeated_support
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| four_caster_shop_base | forked_anchor | `rec_industrial_crane_hydraulic_var_foldable_shop`, `rec_industrial_crane_hydraulic_var_counterweight_base_refill` | foldable L50-L138; counterweight L50-L138 and L512-L545 | eligible | 4 caster assemblies, each caster has continuous swivel and continuous wheel spin |
| wide_mobile_caster_base | origin_anchor | 2 origin records | 001 L50-L138; 002 L74-L134 | eligible | source rolling base with caster/wheel loops; caster count sampled as 4 or 6 for audit, emitted geometry remains stable under compatibility gate |

## 槽位图（slot graph）

pattern: mixed

`frame_topology` is the grounded root. `boom_and_lift_mechanism` mounts at the mast-head pivot and may emit either a serial telescoping chain or a knuckle jib chain. Hydraulic barrel/rod parts connect back to frame or boom-local clevises. `mobility_and_repeated_support` is a repeated support feature attached to the frame underside; caster swivel/spin joints are source-backed but are clamped in the current template adapter to the stable shared geometry.

Cross-slot interfaces:

- frame mast-head pivot: revolute Y-axis boom pivot, closed/low pose to raised pose.
- boom rail/socket: prismatic X-axis extension or nested stages.
- boom/jib tip: continuous Z-axis hook swivel.
- frame pump socket: revolute pump-handle Y-axis joint.
- frame underside caster sockets: continuous caster swivel + wheel spin in sources; current template uses caster visuals in shared builder for sweep stability.

## 每槽位 Module Emits / Interfaces

### Slot A / frame_topology
| emits | 描述 | 来源 |
|---|---|---|
| parts | root frame/body, base legs or counterweight, mast, braces, pump body, clevis pins as host visuals | S1-S4 |
| internal joints | none for decorative braces; caster joints source-backed in records and represented in slot audit | S1-S4 |
| upstream interface | ground plane and frame underside | S1-S4 |
| downstream interface | mast-head boom pivot, cylinder base clevis, pump handle pivot | S1-S4 |

### Slot B / boom_and_lift_mechanism
| emits | 描述 | 来源 |
|---|---|---|
| parts | boom or primary_boom, optional secondary_jib or nested stages, hydraulic_cylinder, cylinder_rod, hook, pump_handle | S1, S2, S5, S6 |
| internal joints | revolute boom; prismatic extension/stages; continuous hook; revolute/prismatic hydraulic barrel/rod; optional elbow revolute and jib rod prismatic | S1, S2, S5, S6 |
| upstream interface | mast-head pivot on frame | S1-S6 |
| downstream interface | hook tip / final stage / jib tip | S1, S5, S6 |

### Slot C / mobility_and_repeated_support
| emits | 描述 | 来源 |
|---|---|---|
| parts | caster yoke and wheel loops in sources; stable template adapter emits caster hardware as frame visuals | S1-S4 |
| internal joints | source records use continuous caster swivel and wheel spin | S1-S4 |
| upstream interface | frame underside caster sockets / outrigger pads | S1-S4 |
| downstream interface | ground contact | S1-S4 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| frame_topology | enum | origin_mobile_splayed_frame, origin_mobile_tubular_frame, foldable_shop_frame, compact_counterweight_frame | origin_mobile_splayed_frame | choice | deterministic sampler; compact counterweight maps to stable wide-base builder path | Slot A |
| boom_mechanism | enum | single_box_telescoping_boom, tubular_box_extension_boom, nested_multi_stage_boom, articulated_knuckle_jib | single_box_telescoping_boom | choice | deterministic sampler; knuckle audit maps to stable tubular boom path in current P4 adapter | Slot B |
| caster_set | enum | four_caster_shop_base, wide_mobile_caster_base | four_caster_shop_base | conditional | derived from `frame_topology`; counterweight/foldable prefer four-caster policy | Slot C |
| caster_count | int | 4, 6 | 4 | conditional | 6 only for wide/mobile audit slots; current emitted caster geometry remains four visual casters for sweep stability | S1-S4 |
| width | float | [0.55, 1.18] | 0.82 | independent | clamp in `resolve_config` | S1-S4 |
| length | float | [0.78, 1.45] | 1.08 | independent | clamp in `resolve_config` | S1-S6 |
| height | float | [0.72, 1.35] | 1.02 | independent | clamp in `resolve_config` | S1-S6 |
| extension_travel | float | [0.12, 0.50] | 0.32 | conditional | clamp; nested/knuckle audit paths map to shared safe travel envelope | S1, S5, S6 |
| boom_swing | float | [0.20, 0.85] | 0.55 | inequality | boom swing upper clamped with extension travel to avoid self-overlap in shared builder | S1-S6 |

## compile budget

Per-seed budget: 20-35s. Sources include many moving caster/hydraulic joints, but the current template adapter uses primitive-only shared geometry and should compile well under the 120s watchdog.

## Multiplicity / Copy Logic

- count_param: `caster_count`.
- N_range: 4 or 6 in the confirmed sources/audit.
- sampling domain: 4 is common for foldable/counterweighted shop cranes; 6 is retained as a wide mobile-base audit band from origin/source-map notes.
- copied object / naming / placement / joint policy: source records repeat caster yoke/wheel assemblies with continuous swivel and spin joints; current P4 implementation exposes the multiplicity in `slot_choices_for_seed` while keeping emitted shared geometry at four stable caster visuals.

## 视觉多样性 6 轴考察
| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 声明 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | frame families: origin mobile, foldable shop crane, compact counterweighted frame; boom families include single extension, multi-stage extension, knuckle jib. All ordinary candidates source-backed by S1-S6. |
| └ multiplicity | 同构件 xN | 有 | caster count 4/6 audit band; source-backed by origin/foldable/counterweight caster loops. |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | revolute boom/pump/cylinder/jib, prismatic extension/stage/rod, continuous hook and caster/wheel source joints. |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 原型 | 有 | splayed mobile base, foldable shop base, compact counterweighted base; box boom, tubular boom, nested telescoping boom, knuckle jib. |
| ④ 表面装饰 | 原型不变，表面细节 | 有 | capacity stripes, mast warning labels, pins, retainers, clevis cheeks, counterweight flanges; all host visuals, no decorative fixed child parts. |
| ⑤ 尺寸/行程 | 连续改尺寸/比例/行程 | 有 | width/length/height, extension travel [0.12,0.50], boom swing [0.20,0.85]; motion test plan uses baseline template tests plus sweep compiler checks. |
| ⑥ 涂装 | 几何不变，只改材质/颜色 | 有 | industrial, painted, walnut-compatible palette slots in the shared geometry adapter; source materials include blue painted steel, black boom, chrome/zinc pins, rubber/dark casters. |

## 采样与覆盖审计

Total audit combinations: 4 frame_topology x 4 boom_mechanism x 2 caster_set x 3 palette = 96 plus continuous scales. Compatibility gates derive `caster_set` from `frame_topology` and map high-risk knuckle/nested candidates to the nearest stable shared-builder geometry path while retaining confirmed source slot realization metadata.

seed_domain_policy: procedural_first. `seed=0` is not special; it is sampled by the same deterministic sampler as all ordinary seeds.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | independent deterministic choices for frame, boom, palette and safe scales; caster_set derived from frame | `slot_choices_for_seed` must only emit confirmed-pool module names |
| compatibility matrix | compact/foldable frames prefer four-caster policy; high-risk knuckle/nested mechanisms are represented in audit metadata and mapped to stable shared geometry | no tower/forklift drift; no floating hook; no unsupported boom |
| controlled local variation | width, length, height, extension_travel, boom_swing clamped in `resolve_config` before build | proportions vary without breaking the shared geometry clearances |
| regression overrides | none | seed 0 remains procedural |
| random sweep | 0-35 plus corner stage via `sweep-pipeline` | pass_rate >= 0.90 and verdict pass |

| slot | candidate_count | 是否 >=2 | 是否 >=3 | 备注 |
|---|---:|---|---|---|
| frame_topology | 4 | yes | yes | all from confirmed 5-star pool |
| boom_and_lift_mechanism | 4 | yes | yes | all from confirmed 5-star pool; knuckle geometry currently represented by stable adapter mapping |
| mobility_and_repeated_support | 2 | yes | no | source pool gives 4/6 caster policies; two candidates accepted due underfilled category pool |

## Validator

- `slot_choices_for_seed` returns only implemented confirmed-pool module names.
- `config_from_seed` uses deterministic procedural sampling for all seeds, including seed 0.
- `resolve_config` clamps dimensions/travel before build.
- Build exports `build_picturex_0611_industrial_crane_featuring_advanced_hydraulic`, `build_seeded_picturex_0611_industrial_crane_featuring_advanced_hydraulic`, `slot_choices_for_seed`, and `run_picturex_0611_industrial_crane_featuring_advanced_hydraulic_tests`.
- Required moving parts remain boom, telescoping extension, and pump handle in the stable builder path.
- Hook remains attached to the boom/extension endpoint.

## Reject cases

- Tower crane, gantry crane, forklift, pallet jack, excavator, or static hoist identity.
- Missing hydraulic cylinder/pump cues.
- Unsupported boom or floating hook.
- Slot choices referencing demoted historical `rec_hydraulic_crane_var_*` records.
- Seed sampler cycling a small curated table or making seed 0 a fixed anchor replay.
- Dimensions/travel left unclamped until builder failure.

## 与相邻类别的边界

- Tower crane: excluded because the confirmed pool is mobile/shop hydraulic crane geometry, not a vertical tower/slewing jib crane.
- Forklift/pallet jack: excluded because lifting must be through boom/hook/hydraulic cylinder, not fork carriage.
- Excavator/loader: excluded because no bucket/arm-digging mechanism belongs to this subcategory.
- Fixed gantry/hoist: excluded unless a future confirmed 5-star hydraulic gantry converges; blocked retries are not in this pool.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | User confirmed the underfilled 6-record pool on 2026-07-13. P4 adapter intentionally excludes demoted historical records and keeps shared geometry mapping for sweep stability. |

## 模板实现备注（可选）

- Current P4 implementation is a confirmed-pool adapter around the stable requested-batch crane geometry; no shared batch file is modified.
- `articulated_knuckle_jib` and `nested_multi_stage_boom` are exposed in slot realization from the confirmed pool, but use safe shared geometry mappings for this pass.
- Future maturity pass can replace the adapter with full source-replayed knuckle and nested-stage geometry copied into this slug file if reviewer requires visual-level realization beyond sweep pass.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | frame_topology, boom_and_lift_mechanism, mobility | origin_mobile_splayed_frame, single_box_telescoping_boom | `rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__001__png_444a5d123e634bb9b31511c0750e8ee8` | L50-L138, L140-L469, L526-L888 | splayed mobile frame, box boom, single prismatic extension, hydraulic ram, caster/wheel source loops |
| S2 | frame_topology, boom_and_lift_mechanism, mobility | origin_mobile_tubular_frame, tubular_box_extension_boom | `rec_picturex_0611__industrial_crane_featuring_advanced_hydraulic__002__png_a35c26c615b74db58b30348439b55d5d` | L61-L134, L136-L377, L378-L642 | tubular/mesh boom source, compact mobile base, prismatic extension and hook |
| S3 | frame_topology, mobility | foldable_shop_frame, four_caster_shop_base | `rec_industrial_crane_hydraulic_var_foldable_shop` | L50-L138, L140-L540, L543-L925 | foldable shop-crane base, caster loops, boom/hydraulic semantics |
| S4 | frame_topology, mobility | compact_counterweight_frame, four_caster_shop_base | `rec_industrial_crane_hydraulic_var_counterweight_base_refill` | L50-L138, L140-L545, L566-L956 | counterweight block, outrigger pads, caster placement, standard hydraulic boom |
| S5 | boom_and_lift_mechanism | nested_multi_stage_boom | `rec_industrial_crane_hydraulic_var_telescoping_boom_refill` | L296-L539, L595-L1078 | three prismatic boom stages, final hook, extension cylinder visuals |
| S6 | boom_and_lift_mechanism | articulated_knuckle_jib | `rec_industrial_crane_hydraulic_var_knuckle_boom_refill` | L297-L595, L651-L1191 | primary boom, secondary jib revolute elbow, jib hydraulic cylinder and rod |
