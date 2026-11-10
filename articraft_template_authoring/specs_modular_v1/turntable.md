# Turntable Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `turntable` |
| template path | `agent/templates/turntable.py` |
| test path | `tests/agent/test_turntable_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 43 |
| read_count | 43 |
| read_scope | all 5-star samples in this category; each record's `record.json`, active `revision.json`, `prompt.txt`, and `model.py` were scanned |
| samples_adopted_as_module_sources | 10 |
| samples_read_but_not_adopted | 33 |
| source_index_policy | adopted sources cover simple plinth, rugged spindle support, modular tonearm stages, two-axis tonearm, controls, hatches, guards, and compact variants |

- adopted as module sources: `rec_turntable_0001`, `rec_turntable_0002`, `rec_turntable_00e2f279f4804b9da8f633b755a26b21`, `rec_turntable_412ace408b7f48eeb54139da2940abae`, `rec_turntable_5c12632efc294508a166929c600d1c9e`, `rec_turntable_73ab50aef9f2479990d263a654c00a50`, `rec_turntable_8c6555a016894ba88c1263423a289a54`, `rec_turntable_be45c7260891449abda61c248181946d`, `rec_turntable_f39b633c366345ebb0eaa7867a4dc6b0`, `rec_turntable_751f57f2cace4f3d9752cd4960c0e846`.
- read but not adopted: `rec_turntable_05607d526a184dd7b359bf643b1b5688`, `rec_turntable_0b4a456ae7bf469e883f90e97154c11a`, `rec_turntable_13881127b7084bf3bd261937693bbbde`, `rec_turntable_17cf5a26eafe4f7f95efc139a639f4e9`, `rec_turntable_1fac4d85ea7f4d7f9eceb34ed909de2a`, `rec_turntable_20737bc8778f4f4eb2ea31edc64c9f46`, `rec_turntable_2fa09f477c3644ab87602680a0a1700b`, `rec_turntable_3e3a05ee4dbb40cb8bb14da5cc27a5fa`, `rec_turntable_41be000319d3408f93cbf63c7ae78313`, `rec_turntable_49d517720d5744cab7fce54307bcf54f`, `rec_turntable_532df32dbe7c446c9af5459f1e640368`, `rec_turntable_5ff9b56637a44ddab0a9914eff62627e`, `rec_turntable_6fad2496e77b485f869c17a8276c45d6`, `rec_turntable_816dc719d7c84bb99accd958f048d40d`, `rec_turntable_855df99810d54a7a93a3749a69fdfcb8`, `rec_turntable_8947851c068549e7b33b5c99eb7da58b`, `rec_turntable_9144377d19f34c63bff099a3097d832a`, `rec_turntable_a64b1547d6f849758f82506601025b54`, `rec_turntable_abe6ed1fe430422fbec6eeeebcb47b66`, `rec_turntable_adbb9c2ee821494e9d20d2a2c00404aa`, `rec_turntable_aef2ed0fef3b486b961f96bc58ad1210`, `rec_turntable_b07eb12343ed45fc91fccaddf9d614e9`, `rec_turntable_ba9271c72bdf48c7a0b760f0aaf775d7`, `rec_turntable_bd96a1d6cdc545cc80f121e6f93c37fa`, `rec_turntable_c466e101d1cd422d990b5c22f01aa264`, `rec_turntable_cb1bf01fbce94c6caf2ead91c5d3afd7`, `rec_turntable_d5f743dd6d9d43348048dafb898aabe2`, `rec_turntable_d60c0f60506940dbb3b2043e6c1d2585`, `rec_turntable_dac3506ccf3643a2ab16eba1b9e9a238`, `rec_turntable_dbbcb3bffb334a56ac9b007a97b6f012`, `rec_turntable_ddd9dec94e4e4c6da07b24b492e730a9`, `rec_turntable_ef1fedfefb0a46fb81b4b8c618bfecde`, `rec_turntable_f87247760408470eabdd5d57b45baf67`; reason: redundant plinth/platter/tonearm/control variants represented by adopted sources.

## 核心身份

Turntable is a record player deck: a plinth/base supports a circular platter spinning continuously about vertical Z and a tonearm stage pivoting about a side base. Secondary controls include speed dial/selector, start/power button, pitch slider, service hatches, guard ring, arm rest, or lockout hardware. The core is not generic rotary table; it must read as audio turntable with platter plus tonearm.

边界：
- 不包括 DJ controller/mixer without tonearm; those belong to `dj_equipment`.
- 不混入 generic rotary stage or lazy Susan: must have audio plinth and tonearm/cartridge semantics.

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_turntable_0001` | `data/records/rec_turntable_0001/revisions/rev_000001/model.py:L82-L215` | canonical plinth, platter, tonearm, platter spin and tonearm pivot |
| S2 | `rec_turntable_0002` | `data/records/rec_turntable_0002/revisions/rev_000001/model.py:L150-L552` | rugged plinth, spindle support, platter, two-axis tonearm carriage/tube, pitch slider |
| S3 | `rec_turntable_00e2f279f4804b9da8f633b755a26b21` | `data/records/rec_turntable_00e2f279f4804b9da8f633b755a26b21/revisions/rev_000001/model.py:L33-L225` | compact plinth and selector |
| S4 | `rec_turntable_412ace408b7f48eeb54139da2940abae` | `data/records/rec_turntable_412ace408b7f48eeb54139da2940abae/revisions/rev_000001/model.py:L67-L324` | speed dial and power button controls |
| S5 | `rec_turntable_5c12632efc294508a166929c600d1c9e` | `data/records/rec_turntable_5c12632efc294508a166929c600d1c9e/revisions/rev_000001/model.py:L56-L462` | industrial guard, spindle support, tonearm support, lockout/guard |
| S6 | `rec_turntable_73ab50aef9f2479990d263a654c00a50` | `data/records/rec_turntable_73ab50aef9f2479990d263a654c00a50/revisions/rev_000001/model.py:L115-L520` | retrofit bearing support, tonearm pedestal/stage, service hatches |
| S7 | `rec_turntable_8c6555a016894ba88c1263423a289a54` | `data/records/rec_turntable_8c6555a016894ba88c1263423a289a54/revisions/rev_000001/model.py:L34-L288` | modular tonearm base/bearing/head chain |
| S8 | `rec_turntable_be45c7260891449abda61c248181946d` | `data/records/rec_turntable_be45c7260891449abda61c248181946d/revisions/rev_000001/model.py:L31-L342` | rugged base with speed knob and start button |
| S9 | `rec_turntable_f39b633c366345ebb0eaa7867a4dc6b0` | `data/records/rec_turntable_f39b633c366345ebb0eaa7867a4dc6b0/revisions/rev_000001/model.py:L33-L238` | guard frame around platter/tonearm |
| S10 | `rec_turntable_751f57f2cace4f3d9752cd4960c0e846` | `data/records/rec_turntable_751f57f2cace4f3d9752cd4960c0e846/revisions/rev_000001/model.py:L19-L108` | explicit fixed platter_support and tonearm_base chain |

## 槽位 + 候选模块表

### Slot A：plinth_base
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `simple_rect_plinth` | `rec_turntable_0001` | L82-L121 | eligible if compatible | low rectangular plinth with platter and tonearm mount areas |
| `rugged_spindle_plinth` | `rec_turntable_0002` | L150-L328 | eligible if compatible | reinforced plinth with separate spindle support |
| `modular_bearing_plinth` | `rec_turntable_8c6555a016894ba88c1263423a289a54` | L34-L218 | eligible if compatible | base plus tonearm modules and bearing chain |
| `industrial_guarded_plinth` | `rec_turntable_5c12632efc294508a166929c600d1c9e` | L56-L270 | eligible if compatible | plinth with guard and support modules |

### Slot B：platter_spindle
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `direct_platter` | `rec_turntable_0001` | L122-L144, L198-L206 | eligible if compatible | platter directly continuous to plinth |
| `spindle_supported_platter` | `rec_turntable_0002` | L310-L365, L495-L510 | eligible if compatible | fixed spindle part plus continuous platter |
| `guarded_platter` | `rec_turntable_5c12632efc294508a166929c600d1c9e` | L75-L151, L403-L418 | eligible if compatible | platter carried by spindle_support with guard context |
| `raised_support_platter` | `rec_turntable_751f57f2cace4f3d9752cd4960c0e846` | L27-L56 | eligible if compatible | explicit platter_support fixed to plinth |

### Slot C：tonearm_stage
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `simple_pivot_tonearm` | `rec_turntable_0001` | L145-L215 | eligible if compatible | single tonearm part pivots on plinth |
| `two_axis_carriage_arm` | `rec_turntable_0002` | L366-L538 | eligible if compatible | carriage swings about Z, tube has second pitch REVOLUTE |
| `modular_tonearm_head` | `rec_turntable_8c6555a016894ba88c1263423a289a54` | L114-L288 | eligible if compatible | tonearm_base -> bearing_module -> head_module chain |
| `retrofit_tonearm_stage` | `rec_turntable_73ab50aef9f2479990d263a654c00a50` | L246-L506 | eligible if compatible | pedestal and stage for robust retrofit assembly |

### Slot D：controls_accessories
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `none` | `rec_turntable_0001` | L82-L215 | eligible if compatible | no extra controls beyond platter/tonearm |
| `pitch_slider` | `rec_turntable_0002` | L470-L552 | eligible if compatible | PRISMATIC pitch slider on plinth |
| `speed_dial_power_button` | `rec_turntable_412ace408b7f48eeb54139da2940abae` | L245-L324 | eligible if compatible | speed dial REVOLUTE plus power button PRISMATIC |
| `service_hatches` | `rec_turntable_73ab50aef9f2479990d263a654c00a50` | L394-L520 | eligible if compatible | motor/signal hatches as service features |
| `guard_frame` | `rec_turntable_f39b633c366345ebb0eaa7867a4dc6b0` | L203-L238 | eligible if compatible | fixed guard frame around deck |

## 槽位图（slot graph）

pattern: `mixed`

```text
[Slot A plinth_base]
  ├── platter_spin CONTINUOUS, axis Z --> [Slot B platter_spindle]
  ├── tonearm_pivot REVOLUTE, axis Z --> [Slot C tonearm_stage]
  └── optional parallel controls/accessories --> [Slot D controls_accessories]
```

## 部件（Parts）
| part | slot | visual_count | 描述 | 来源 |
|---|---|---:|---|---|
| `plinth` / `base` | A | ~5-24 | rectangular audio deck and support details | S1-S8 |
| `spindle_support` / `platter_support` | B | ~1-4 | optional fixed support part under platter | S2/S5/S10 |
| `platter` | B | ~3-8 | circular record platter and mat/spindle details | S1-S10 |
| `tonearm` / `tonearm_stage` / `tonearm_carriage` | C | ~5-10 | pivoting arm, cartridge, counterweight, bearing | S1/S2/S6/S7 |
| `speed_dial` / `button` / `pitch_slider` / `guard_frame` / `hatch` | D | ~1-8 | secondary controls and service features | S2/S4-S9 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 |
|---|---|---|---|---|---|---|
| `platter_spin` | CONTINUOUS | A.plinth or B.spindle_support | B.platter | `(0,0,1)` | unbounded | rotating platter |
| `tonearm_pivot` | REVOLUTE | A.plinth or C.tonearm_base | C.tonearm | `(0,0,1)` | bounded sweep | tonearm sweeps across platter |
| `tonearm_pitch` | REVOLUTE | C.carriage | C.tonearm_tube | `(0,1,0)` | bounded | optional two-axis tonearm |
| `pitch_slider` | PRISMATIC | A.plinth | D.pitch_slider | `(1,0,0)` | short travel | optional pitch control |
| `control_spin` / `button_press` | REVOLUTE / PRISMATIC | A.plinth | D.control | local Z | bounded/short | speed dial and button |

## 每槽位 Module Emits / Interfaces

本 spec 是 modular v1 早期写法；每个 slot/module 的 emitted parts、internal joints、upstream/downstream interface 已在「槽位 + 候选模块表」「槽位图」「部件（Parts）」「关节（Joints）」和 adopted source index 中给出。模板实现阶段必须把这些信息逐 module 显式落成 `ModuleBuild`、`InterfaceSpec` 和 `MatingContract`，不能只按全局部件清单拼装。

| emits | 描述 | 来源 |
|---|---|---|
| parts / visuals | 以各 slot candidate 的结构特征和「部件（Parts）」表为准；不动装饰优先作为 parent visual | adopted source index + slot table |
| internal joints | 以「关节（Joints）」表和 slot graph 中的 joint type / axis / range 为准 | adopted source index + joints table |
| upstream interface | 来自 slot graph 中的 parent face、hinge line、socket、rail、axis、contact plane 或 support policy | slot graph + source snippets |
| downstream interface | 消费相邻 slot 的 mating point / axis / face；必须在实现中转成真实 `InterfaceSpec` | slot graph + source snippets |
| mating contracts | 每个 separate moving child 和跨 slot 连接必须有可见支撑路径；captured pin / shaft / bearing overlap 需要局部 allow-overlap 理由 | validator + reject cases |

## 参数范围汇总
| 参数 | 类型 | 取值范围 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `plinth_style` | enum | `simple_rect_plinth` / `rugged_spindle_plinth` / `modular_bearing_plinth` / `industrial_guarded_plinth` | `simple_rect_plinth` | Slot A | S1/S2/S5/S7 |
| `platter_style` | enum | `direct_platter` / `spindle_supported_platter` / `guarded_platter` / `raised_support_platter` | `direct_platter` | Slot B | S1/S2/S5/S10 |
| `tonearm_style` | enum | `simple_pivot_tonearm` / `two_axis_carriage_arm` / `modular_tonearm_head` / `retrofit_tonearm_stage` | `simple_pivot_tonearm` | Slot C | S1/S2/S6/S7 |
| `accessory_style` | enum | `none` / `pitch_slider` / `speed_dial_power_button` / `service_hatches` / `guard_frame` | `none` | Slot D | S2/S4/S6/S9 |
| `platter_radius` | float | category scale sampled | sampled | must fit plinth footprint | all |
| `tonearm_length` | float | reaches platter radius | sampled | pivot outside platter rim | all |

## Multiplicity / Copy Logic

- 无复制数量逻辑：本类别的核心 moving set is one platter, one tonearm/tonearm stage, and optional named controls/access doors. The template should not expose `platter_count`, `tonearm_count`, or a random control-count loop.
- Buttons, hatches, guard bars, screws, and deck marks inside a selected module are source-local fixed structure or baked visuals. They may be emitted by that module, but they are not template-level sampled multiplicity.
- Topology diversity comes from slot module choices and joint types, not from cloning an arbitrary number of parallel parts.

## 拓扑多样性审计


| slot | candidate_count | 是否 >=3 | 备注 |
|---|---:|---|---|
| plinth_base | 4 | yes | |
| platter_spindle | 4 | yes | |
| tonearm_stage | 4 | yes | |
| controls_accessories | 5 | yes | includes `none` |

### Procedural Sampling / Sweep Plan

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊，不作为 anchor 或 reference seed。Sampling 先选择上游结构槽，再从 compatible 下游 candidate 集合中选择 module / multiplicity / module-local variant。

Compatibility matrix / gating：以「槽位图」「每槽位 Module Emits / Interfaces」「Validator」中定义的接口、joint 轴、支撑面、range 和互斥关系为准；不兼容组合必须在 sampler 或 `resolve_config` 中降级、重采样或拒绝，不能让 builder 后期失败。

Regression overrides：默认无。若未来 sweep 发现稳定失败组合，或 reviewer 指定固定回归样本，可以添加少量显式 regression seed，但必须写明 seed、组合和原因；不得用小型 curated / modulo 表作为主 seed domain。

Random sweep / viewer plan：首次模板验收跑 `uv run articraft template sweep-pipeline <slug>`，依赖 0、0-4、0-19、0-49 的 cumulative random seeds 检查 build、MatingContract、joint origin / axis / range、support、collision 和 。机械通过后 viewer 目检一小批随机 seed，重点看类别身份、比例、closed pose、bulky module、optional moving child、max multiplicity、captured-pin / bearing / hinge / rail 接口。


## Validator（author_run_tests 必须覆盖的点）
- Must include platter continuous spin about vertical Z.
- Must include a tonearm/stage pivoting about a side base; pivot must lie outside platter radius.
- Platter must sit on plinth/spindle support with visible contact.
- Tonearm cartridge/head must point toward platter area and clear platter at rest.
- Controls/accessories must be anchored to real plinth geometry.

## Reject cases（必须能识别并拒绝）
- No tonearm or no platter spin.
- Tonearm pivot at platter center or tonearm floating over deck.
- Platter not circular or not on vertical axis.
- Controls as disconnected/fixed decorative parts.
- Generic rotary table without audio device identity.

## 与相邻类别的边界
- `dj_equipment`：DJ controller/mixer can have jog wheels but may lack tonearm; turntable requires record platter + tonearm.
- `coaxial_rotary_stack`：generic mechanical stack has no audio plinth/tonearm.
- `globe`：rotating sphere and meridian, not flat platter/audio controls.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核 |
