# Traditional Windmill Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `traditional_windmill` |
| template path | `agent/templates/traditional_windmill.py` |
| test path | `tests/agent/test_traditional_windmill_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 32 |
| read_count | 32 |
| read_scope | all 5-star samples in this category; each record's `record.json`, active `revision.json`, `prompt.txt`, and `model.py` were scanned for part tree, joints, line ranges, and prompt intent |
| samples_adopted_as_module_sources | 10 |
| samples_read_but_not_adopted | 22 |
| source_index_policy | adopted sources cover the observed tower/cap/rotor/accessory families; non-adopted records are duplicate or lower-signal variants within those same families |

- adopted as module sources: `rec_traditional_windmill_0002`, `rec_traditional_windmill_00b3e45fa2e04aeaa5fb363f96b2115e`, `rec_traditional_windmill_018591ff916a428aa0d7b7fa8ad24d1d`, `rec_traditional_windmill_04d6d1109cf74ed194c5e7e9134c8272`, `rec_traditional_windmill_0c9ef136b78d4612a74250d77c632b08`, `rec_traditional_windmill_17c28308c5f04e3288c5cf19f9bee2c1`, `rec_traditional_windmill_72ad9025d8ee45aaa3843d5e6b549132`, `rec_traditional_windmill_973bf1df6bd245218dccfc8699935e81`, `rec_traditional_windmill_b7e9f597b4914a899df82c98be4f2429`, `rec_traditional_windmill_dba2ae8710824ba9bd7267c95d3b9d29`.
- read but not adopted: `rec_traditional_windmill_03046f8f45f042ddad4553b0a4b1affd`, `rec_traditional_windmill_0fe6a05d39514c23b54b50adbb9eed75`, `rec_traditional_windmill_12fdfc0e33ca467c990d366c5fed846e`, `rec_traditional_windmill_1711df240f3440f785592d515eadb319`, `rec_traditional_windmill_2dfcf4d95b944e95af4fe5529e7773b8`, `rec_traditional_windmill_2f4c1e1702224030bce58a486ea74096`, `rec_traditional_windmill_33c09c7fc0b440f38135862c6b66a7b2`, `rec_traditional_windmill_3c4537005b724f949f35ca037f9e52db`, `rec_traditional_windmill_4eb12f6fd6764f518b3fea75fa8519b0`, `rec_traditional_windmill_54e02a15827a4ecca2fabc0eedad9424`, `rec_traditional_windmill_6ce0d38ceb1a40d68d2b7c1b80021d09`, `rec_traditional_windmill_88136c6eea7a4705933de22a8f2620bf`, `rec_traditional_windmill_a9e17fe2dd4645b592965f921cac5aa3`, `rec_traditional_windmill_c201de4b67b247ddaa1aad9fa2568062`, `rec_traditional_windmill_c97fb13bb0814afd98392dc6e1da13fe`, `rec_traditional_windmill_cbc5a0e71e44403ba30636b7c288e97d`, `rec_traditional_windmill_d3de5d48efb0449eb1c8deb45e69bbf7`, `rec_traditional_windmill_d80bf1039a03475089fd9e6f9fd09bfd`, `rec_traditional_windmill_ddfdafb4e5e64b4da7686ba2024709d2`, `rec_traditional_windmill_e21c5d19214d45db88435230c23270e8`, `rec_traditional_windmill_eb484cb5048342fda5387c1a2ebeeafc`, `rec_traditional_windmill_f5ce086230c6402d9829bdf3e1147f83`; reason: redundant low-body, tapered-tower, continuous-yaw, lattice-rotor, or service-detail variants already represented above.

## 核心身份

Traditional windmill 是带建筑性塔身或磨坊体的历史风车：静态 tower/body 支撑可偏航的 cap/nacelle，cap 前方承载连续旋转的 sail hub / blade lattice。核心运动是 cap 绕竖直轴 yaw 加风叶绕水平风轴 continuous spin；可选运动包括 access door、brake lever、lockout lever 或 service hatch。模板不应退化成现代 wind turbine，也不应变成普通风扇。

边界：
- 不包括现代三叶 `wind_turbine` 的高塔机舱发电机语义。
- 不混入 waterwheel / clock tower：必须有前向风叶和 cap/yaw 或明确固定的传统风车头。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_traditional_windmill_00b3e45fa2e04aeaa5fb363f96b2115e` | `data/records/rec_traditional_windmill_00b3e45fa2e04aeaa5fb363f96b2115e/revisions/rev_000001/model.py:L59-L181` | low-body tower + simple cap + sail hub, clean 2-DOF chain |
| S2 | `rec_traditional_windmill_0002` | `data/records/rec_traditional_windmill_0002/revisions/rev_000001/model.py:L249-L639` | rugged tower, access door, roof cap, rotor, brake lever |
| S3 | `rec_traditional_windmill_018591ff916a428aa0d7b7fa8ad24d1d` | `data/records/rec_traditional_windmill_018591ff916a428aa0d7b7fa8ad24d1d/revisions/rev_000001/model.py:L222-L703` | industrial tower/cap with dense guard hardware |
| S4 | `rec_traditional_windmill_04d6d1109cf74ed194c5e7e9134c8272` | `data/records/rec_traditional_windmill_04d6d1109cf74ed194c5e7e9134c8272/revisions/rev_000001/model.py:L195-L301` | compact desktop tower and fold/stow-friendly rotor hints |
| S5 | `rec_traditional_windmill_0c9ef136b78d4612a74250d77c632b08` | `data/records/rec_traditional_windmill_0c9ef136b78d4612a74250d77c632b08/revisions/rev_000001/model.py:L264-L539` | split tower_base -> bearing_module -> cap_shell -> head_frame -> hub chain |
| S6 | `rec_traditional_windmill_17c28308c5f04e3288c5cf19f9bee2c1` | `data/records/rec_traditional_windmill_17c28308c5f04e3288c5cf19f9bee2c1/revisions/rev_000001/model.py:L234-L570` | weatherproof tower/cap/rotor shelling |
| S7 | `rec_traditional_windmill_72ad9025d8ee45aaa3843d5e6b549132` | `data/records/rec_traditional_windmill_72ad9025d8ee45aaa3843d5e6b549132/revisions/rev_000001/model.py:L102-L450` | bounded cap yaw and lockout lever |
| S8 | `rec_traditional_windmill_973bf1df6bd245218dccfc8699935e81` | `data/records/rec_traditional_windmill_973bf1df6bd245218dccfc8699935e81/revisions/rev_000001/model.py:L292-L691` | high-detail retrofit cap and rotor lattice |
| S9 | `rec_traditional_windmill_b7e9f597b4914a899df82c98be4f2429` | `data/records/rec_traditional_windmill_b7e9f597b4914a899df82c98be4f2429/revisions/rev_000001/model.py:L114-L429` | rugged cap with bounded yaw and rotor spin |
| S10 | `rec_traditional_windmill_dba2ae8710824ba9bd7267c95d3b9d29` | `data/records/rec_traditional_windmill_dba2ae8710824ba9bd7267c95d3b9d29/revisions/rev_000001/model.py:L50-L392` | field-service side hatch on cap |

## 槽位 + 候选模块表

### Slot A：support_tower
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `low_body_tower` | `rec_traditional_windmill_00b3e45fa2e04aeaa5fb363f96b2115e` | L59-L90 | eligible if compatible | low mill body with direct cap seat; compact and simple |
| `rugged_tower_with_door` | `rec_traditional_windmill_0002` | L249-L392 | eligible if compatible | tower body plus articulated access door source geometry |
| `industrial_guarded_tower` | `rec_traditional_windmill_018591ff916a428aa0d7b7fa8ad24d1d` | L222-L368 | eligible if compatible | heavy-duty tower with reinforced shell, hardware, guard language |
| `split_bearing_tower` | `rec_traditional_windmill_0c9ef136b78d4612a74250d77c632b08` | L264-L344 | eligible if compatible | tower_base and bearing_module are separate structural stages |

### Slot B：yaw_cap_head
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `continuous_roof_cap` | `rec_traditional_windmill_00b3e45fa2e04aeaa5fb363f96b2115e` | L91-L115, L164-L172 | eligible if compatible | simple cap part, continuous yaw about tower Z |
| `bounded_service_cap` | `rec_traditional_windmill_b7e9f597b4914a899df82c98be4f2429` | L223-L324, L412-L420 | eligible if compatible | heavier cap with REVOLUTE yaw limit |
| `split_head_frame` | `rec_traditional_windmill_0c9ef136b78d4612a74250d77c632b08` | L302-L377, L515-L530 | eligible if compatible | bearing_module -> cap_shell continuous, then fixed head_frame |
| `weatherproof_shell_cap` | `rec_traditional_windmill_17c28308c5f04e3288c5cf19f9bee2c1` | L285-L526, L553-L561 | eligible if compatible | sealed outdoor cap with dense roof/collar detailing |

### Slot C：sail_rotor
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `classic_lattice_sails` | `rec_traditional_windmill_00b3e45fa2e04aeaa5fb363f96b2115e` | L116-L163, L173-L181 | eligible if compatible | hub plus multiple lattice blades as rotor visuals; continuous shaft spin |
| `retrofit_dense_rotor` | `rec_traditional_windmill_973bf1df6bd245218dccfc8699935e81` | L594-L691 | eligible if compatible | denser retrofit rotor with reinforced hub and sail lattice |
| `compact_stow_rotor` | `rec_traditional_windmill_04d6d1109cf74ed194c5e7e9134c8272` | L238-L301 | eligible if compatible | compact rotor_hub with per-blade fold/stow hint plus spin |
| `weatherproof_rotor` | `rec_traditional_windmill_17c28308c5f04e3288c5cf19f9bee2c1` | L527-L570 | eligible if compatible | sealed rotor with outdoor hardware language |

### Slot D：service_accessory
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `access_door` | `rec_traditional_windmill_0002` | L346-L607 | eligible if compatible | tower door REVOLUTE hinged to tower |
| `brake_lever` | `rec_traditional_windmill_0002` | L558-L639 | eligible if compatible | cap-mounted brake lever REVOLUTE about local horizontal axis |
| `lockout_lever` | `rec_traditional_windmill_72ad9025d8ee45aaa3843d5e6b549132` | L426-L450 | eligible if compatible | industrial lockout lever on cap |
| `side_hatch` | `rec_traditional_windmill_dba2ae8710824ba9bd7267c95d3b9d29` | L262-L392 | eligible if compatible | side hatch REVOLUTE on cap for service access |

## 槽位图（slot graph）

pattern: `mixed`

```text
[Slot A support_tower]
  -- yaw: CONTINUOUS or REVOLUTE, axis Z -->
[Slot B yaw_cap_head]
  -- sail_spin: CONTINUOUS, axis horizontal X/Y -->
[Slot C sail_rotor]

[Slot A or B] -- optional parallel REVOLUTE --> [Slot D service_accessory]
```

## 部件（Parts）
| part | slot | visual_count | 描述 | 来源 |
|---|---|---:|---|---|
| `tower` / `tower_body` / `tower_base` | A | ~5-18 | masonry/timber/industrial tower, may include door frame or bearing pedestal | S1-S5 |
| `bearing_module` | A/B | ~2-5 | optional separate yaw bearing stage | S5 |
| `cap` / `cap_shell` / `head_frame` | B | ~4-39 | roofed nacelle/head carried by yaw joint | S1-S9 |
| `rotor` / `sail_hub` | C | ~3-12 | hub and sail lattice rotating as one part | S1/S4/S8 |
| `access_door` / `brake_lever` / `lockout_lever` / `side_hatch` | D | ~2-7 | articulated service accessory | S2/S7/S10 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 |
|---|---|---|---|---|---|---|
| `tower_to_cap` | CONTINUOUS / REVOLUTE | A.tower or A.bearing_module | B.cap | `(0,0,1)` | continuous or bounded yaw | wind-facing cap yaw |
| `cap_to_rotor` | CONTINUOUS | B.cap or B.head_frame | C.rotor | horizontal `(1,0,0)` or `(0,1,0)` | unbounded | sail hub spin |
| `tower_to_door` | REVOLUTE | A.tower | D.access_door | `(0,0,1)` | service swing | optional |
| `cap_to_brake_or_hatch` | REVOLUTE | B.cap | D.brake/hatch | horizontal or vertical by module | bounded | optional service control |

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
| `tower_style` | enum | `low_body_tower` / `rugged_tower_with_door` / `industrial_guarded_tower` / `split_bearing_tower` | `low_body_tower` | selects Slot A | S1-S5 |
| `yaw_style` | enum | `continuous_roof_cap` / `bounded_service_cap` / `split_head_frame` / `weatherproof_shell_cap` | `continuous_roof_cap` | selects Slot B and yaw joint type | S1/S5/S6/S9 |
| `rotor_style` | enum | `classic_lattice_sails` / `retrofit_dense_rotor` / `compact_stow_rotor` / `weatherproof_rotor` | `classic_lattice_sails` | selects Slot C geometry | S1/S4/S6/S8 |
| `sail_count` | int | `4-8` | 4 | radial lattice clone count; source majority is 4 | S1/S4/S8 |
| `service_accessory` | enum | `access_door` / `brake_lever` / `lockout_lever` / `side_hatch` / `none` | `access_door` | optional parallel child | S2/S7/S10 |
| `yaw_limited` | bool | derived from Slot B | false | bounded modules use REVOLUTE | S7/S9 |

## Multiplicity / Copy Logic

- `sail_count` controls the repeated sail/lattice visuals in Slot C. Seed-0 uses `N=4`.
- The copied object is the sail visual cluster around the hub, not a separate child part and not a separate joint per sail. The whole rotor remains one Slot C part driven by the single `cap_to_rotor` CONTINUOUS joint.
- Naming should follow `sail_i` / `lattice_sail_i` for internal named visuals when the implementation needs per-sail inspection.
- Placement is radial: each sail root attaches to the hub and uses phase `i * 360° / N` in the rotor plane.
- Source majority is four-sail traditional windmill geometry. `N=5-8` is a low-priority reviewer-gated extrapolation by clone count and phase only; it must not change the joint graph.

## 拓扑多样性审计


| slot | candidate_count | 是否 >=3 | 备注 |
|---|---:|---|---|
| support_tower | 4 | yes | |
| yaw_cap_head | 4 | yes | |
| sail_rotor | 4 | yes | |
| service_accessory | 5 | yes | includes `none` |

### Procedural Sampling / Sweep Plan

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊，不作为 anchor 或 reference seed。Sampling 先选择上游结构槽，再从 compatible 下游 candidate 集合中选择 module / multiplicity / module-local variant。

Compatibility matrix / gating：以「槽位图」「每槽位 Module Emits / Interfaces」「Validator」中定义的接口、joint 轴、支撑面、range 和互斥关系为准；不兼容组合必须在 sampler 或 `resolve_config` 中降级、重采样或拒绝，不能让 builder 后期失败。

Regression overrides：默认无。若未来 sweep 发现稳定失败组合，或 reviewer 指定固定回归样本，可以添加少量显式 regression seed，但必须写明 seed、组合和原因；不得用小型 curated / modulo 表作为主 seed domain。

Random sweep / viewer plan：首次模板验收跑 `uv run articraft template sweep-pipeline <slug>`，依赖 0、0-4、0-19、0-49 的 cumulative random seeds 检查 build、MatingContract、joint origin / axis / range、support、collision 和 。机械通过后 viewer 目检一小批随机 seed，重点看类别身份、比例、closed pose、bulky module、optional moving child、max multiplicity、captured-pin / bearing / hinge / rail 接口。


## Validator（author_run_tests 必须覆盖的点）
- 必须有 tower/body、cap/head、rotor/sail 三个核心语义。
- `tower_to_cap` 轴必须竖直；`cap_to_rotor` 轴必须水平且穿过 hub。
- sail count 与 rotor visuals/parts 一致，围绕 hub 等角分布。
- cap/head 必须坐在 tower 或 bearing_module 上，rotor 必须由 cap/head 正面实体支撑。
- service accessory 若为独立 part，必须有真实 hinge/socket geometry 和 MatingContract。

## Reject cases（必须能识别并拒绝）
- 没有 windmill sail rotor，或 rotor 不连续旋转。
- cap 悬空、rotor 离 cap 有明显空隙、sail root 不接触 hub。
- 做成现代三叶风电机、桌面风扇、水轮或纯静态塔楼。
- 把不动的 roof trim / braces 做成 FIXED child parts，违反 Rule 1。

## 与相邻类别的边界
- `wind_turbine`：现代 HAWT 是 tower+nacelle+三叶发电机；本类是传统塔身/cap/多片 lattice sail。
- `overshot_waterwheel`：水轮水平轴但由水槽驱动，无 cap yaw、无风帆。
- `ceiling_fan` / `box_fan`：风扇无建筑性 tower/cap。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核 |
