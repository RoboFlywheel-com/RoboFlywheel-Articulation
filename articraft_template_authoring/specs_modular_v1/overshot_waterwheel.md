# Overshot Waterwheel Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `overshot_waterwheel` |
| template path | `agent/templates/overshot_waterwheel.py` |
| test path | `tests/agent/test_overshot_waterwheel_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 31 |
| read_count | 31 |
| read_scope | all 5-star samples in this category; each record's `record.json`, active `revision.json`, `prompt.txt`, and `model.py` were scanned |
| samples_adopted_as_module_sources | 12 |
| samples_read_but_not_adopted | 19 |
| source_index_policy | adopted sources cover support, wheel construction, water-control, brake, guard, and pulley families |

- adopted as module sources: `rec_overshot_waterwheel_0002`, `rec_overshot_waterwheel_0003`, `rec_overshot_waterwheel_11151adbd0fa4816ba1b013bf436c785`, `rec_overshot_waterwheel_2ecf1915ff74484ca50008589b1a1fa1`, `rec_overshot_waterwheel_33803fa1d6954b11a45337981e15ff29`, `rec_overshot_waterwheel_34ab721ae08a4072bcdd7ecbce39bf4b`, `rec_overshot_waterwheel_5193642d3d2e4879b1a8d9b8bea0b43c`, `rec_overshot_waterwheel_576296376a674c70817d8eb4e501f60f`, `rec_overshot_waterwheel_57e35e7515df48b2b25250de2d76e1e0`, `rec_overshot_waterwheel_a84a1a2e24f84a208e51e4185e570d7d`, `rec_overshot_waterwheel_b5756ab6877349ff9a562c42fad2c457`, `rec_overshot_waterwheel_c6788424bda249d185ba7f90358ac24a`.
- read but not adopted: `rec_overshot_waterwheel_015f02de5db54a838371646eb98019c7`, `rec_overshot_waterwheel_25feb1bc4340467691c420e045e1feee`, `rec_overshot_waterwheel_43ec6a2742b94234812eee111e4942b1`, `rec_overshot_waterwheel_4dfbdb8cad1d43a2810ffb914c7477c9`, `rec_overshot_waterwheel_5449c2e057a84faa98b71815994cbf12`, `rec_overshot_waterwheel_55732416dc324d5ca28574fa83350e82`, `rec_overshot_waterwheel_62564ffc326d4a928f3690354fe698f0`, `rec_overshot_waterwheel_6cbcd301bbe0465a85abff8a3f71a66a`, `rec_overshot_waterwheel_75f82bc8e84041f9b19e52664ad4e68a`, `rec_overshot_waterwheel_79b87320c8a241b2bcd418ddf19483da`, `rec_overshot_waterwheel_80effb5bdb534d0886b94d2a6f7c4b73`, `rec_overshot_waterwheel_8258f128327a418f9b3268ea44131460`, `rec_overshot_waterwheel_907a577673fc456ab815c2be6b0a2f30`, `rec_overshot_waterwheel_a1a1d74477494ffb94ee500bf79ae173`, `rec_overshot_waterwheel_a6462a283db84667a111562eb8bd7301`, `rec_overshot_waterwheel_a8b03a134ba144229e9d058f9ce7cc60`, `rec_overshot_waterwheel_dd9e49c4fd214cd9ad22b7c93f9b124e`, `rec_overshot_waterwheel_e087651dce4b4400a1cab8a5c949f538`, `rec_overshot_waterwheel_fb9f44936ab24713ab3dbff1c6349877`; reason: redundant timber/masonry frame, bucket wheel, chute gate, brake arm, or pulley variants already represented.

## 核心身份

Overshot waterwheel 是带上部进水槽/水闸语义的水平轴水轮。静态 timber/masonry support 或 millrace 支撑一只带桶/斗/桨叶的 wheel，wheel 围绕水平轴连续旋转；上方或侧上方必须有 chute/launder/flume/inlet box，常见附加运动包括 sliding sluice gate、pivoting shutoff flap、side brake arm、hinged guard 或 outboard pulley。

边界：
- 不包括 undershot/side-shot 水轮：本类必须读成从上方注水。
- 不混入 windmill：不能有 cap yaw 或 wind sail lattice。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_overshot_waterwheel_0002` | `data/records/rec_overshot_waterwheel_0002/revisions/rev_000001/model.py:L74-L376` | simple frame + chute + spoked bucket wheel |
| S2 | `rec_overshot_waterwheel_0003` | `data/records/rec_overshot_waterwheel_0003/revisions/rev_000001/model.py:L79-L258` | timber mill frame and deep bucket wheel |
| S3 | `rec_overshot_waterwheel_11151adbd0fa4816ba1b013bf436c785` | `data/records/rec_overshot_waterwheel_11151adbd0fa4816ba1b013bf436c785/revisions/rev_000001/model.py:L86-L320` | masonry support, drive pulley, feed chute, sliding gate |
| S4 | `rec_overshot_waterwheel_2ecf1915ff74484ca50008589b1a1fa1` | `data/records/rec_overshot_waterwheel_2ecf1915ff74484ca50008589b1a1fa1/revisions/rev_000001/model.py:L128-L451` | timber feed chute and prismatic sluice gate |
| S5 | `rec_overshot_waterwheel_33803fa1d6954b11a45337981e15ff29` | `data/records/rec_overshot_waterwheel_33803fa1d6954b11a45337981e15ff29/revisions/rev_000001/model.py:L129-L287` | hinged inspection flap at feed trough |
| S6 | `rec_overshot_waterwheel_34ab721ae08a4072bcdd7ecbce39bf4b` | `data/records/rec_overshot_waterwheel_34ab721ae08a4072bcdd7ecbce39bf4b/revisions/rev_000001/model.py:L33-L193` | side-mounted drive pinion on same axle |
| S7 | `rec_overshot_waterwheel_5193642d3d2e4879b1a8d9b8bea0b43c` | `data/records/rec_overshot_waterwheel_5193642d3d2e4879b1a8d9b8bea0b43c/revisions/rev_000001/model.py:L121-L398` | broad rim, buckets, side brake shoe lever |
| S8 | `rec_overshot_waterwheel_576296376a674c70817d8eb4e501f60f` | `data/records/rec_overshot_waterwheel_576296376a674c70817d8eb4e501f60f/revisions/rev_000001/model.py:L27-L168` | narrow launder and pivoting shutoff flap |
| S9 | `rec_overshot_waterwheel_57e35e7515df48b2b25250de2d76e1e0` | `data/records/rec_overshot_waterwheel_57e35e7515df48b2b25250de2d76e1e0/revisions/rev_000001/model.py:L32-L158` | compact demo wheel and hinged guard |
| S10 | `rec_overshot_waterwheel_a84a1a2e24f84a208e51e4185e570d7d` | `data/records/rec_overshot_waterwheel_a84a1a2e24f84a208e51e4185e570d7d/revisions/rev_000001/model.py:L101-L262` | cast-iron wheel, masonry flume, drop-in gate |
| S11 | `rec_overshot_waterwheel_b5756ab6877349ff9a562c42fad2c457` | `data/records/rec_overshot_waterwheel_b5756ab6877349ff9a562c42fad2c457/revisions/rev_000001/model.py:L60-L283` | separate launder part and flap parented to launder |
| S12 | `rec_overshot_waterwheel_c6788424bda249d185ba7f90358ac24a` | `data/records/rec_overshot_waterwheel_c6788424bda249d185ba7f90358ac24a/revisions/rev_000001/model.py:L81-L391` | suspended inlet box and regulator plate |

## 槽位 + 候选模块表

### Slot A：support_and_feed
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `simple_frame_chute` | `rec_overshot_waterwheel_0002` | L74-L287 | eligible if compatible | frame with overhead chute and side supports |
| `timber_mill_frame` | `rec_overshot_waterwheel_0003` | L79-L175 | eligible if compatible | timber frame, axle blocks, trough base |
| `masonry_flume_support` | `rec_overshot_waterwheel_11151adbd0fa4816ba1b013bf436c785` | L86-L215 | eligible if compatible | stone sidewalls plus feed chute |
| `suspended_inlet_box` | `rec_overshot_waterwheel_c6788424bda249d185ba7f90358ac24a` | L81-L337 | eligible if compatible | frame with separate inlet box above crown |

### Slot B：bucket_wheel
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `spoked_shallow_bucket_wheel` | `rec_overshot_waterwheel_0002` | L288-L376 | eligible if compatible | spoked wheel with shallow bucket ring |
| `deep_timber_bucket_wheel` | `rec_overshot_waterwheel_0003` | L176-L258 | eligible if compatible | deep bucket wheel and broad timber rim |
| `drive_pinion_rotor` | `rec_overshot_waterwheel_34ab721ae08a4072bcdd7ecbce39bf4b` | L110-L193 | eligible if compatible | wheel assembly includes outboard small gear/pinion |
| `cast_iron_bucket_wheel` | `rec_overshot_waterwheel_a84a1a2e24f84a208e51e4185e570d7d` | L211-L253 | eligible if compatible | cast-iron style rotor with masonry support |

### Slot C：water_control_or_service
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `fixed_chute_only` | `rec_overshot_waterwheel_0002` | L209-L367 | eligible if compatible | chute is fixed to frame, no extra moving control |
| `sliding_sluice_gate` | `rec_overshot_waterwheel_2ecf1915ff74484ca50008589b1a1fa1` | L386-L451 | eligible if compatible | prismatic gate in feed path |
| `pivoting_shutoff_flap` | `rec_overshot_waterwheel_576296376a674c70817d8eb4e501f60f` | L131-L168 | eligible if compatible | hinged flap across launder outlet |
| `brake_arm` | `rec_overshot_waterwheel_5193642d3d2e4879b1a8d9b8bea0b43c` | L328-L398 | eligible if compatible | side brake lever presses shoe on rim |
| `hinged_guard_panel` | `rec_overshot_waterwheel_57e35e7515df48b2b25250de2d76e1e0` | L128-L158 | eligible if compatible | safety guard swings open beside feed point |

## 槽位图（slot graph）

pattern: `mixed`

```text
[Slot A support_and_feed] -- wheel_spin CONTINUOUS, horizontal axis --> [Slot B bucket_wheel]
[Slot A support_and_feed] -- optional FIXED/PRISMATIC/REVOLUTE --> [Slot C water_control_or_service]
```

## 部件（Parts）
| part | slot | visual_count | 描述 | 来源 |
|---|---|---:|---|---|
| `frame` / `support_frame` / `masonry` | A | ~7-20 | static support, side bearings, piers, trough or flume | S1-S4/S10 |
| `chute` / `launder` / `inlet_box` | A/C | ~1-12 | overhead feed element, sometimes separate fixed part | S1/S11/S12 |
| `wheel` / `waterwheel` / `rotor` | B | ~1-14 | bucketed rotating wheel on horizontal axle | S1-S3/S6/S10 |
| `gate` / `flap` / `brake_arm` / `guard` | C | ~1-7 | optional articulated control or service element | S4/S5/S7-S9 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 |
|---|---|---|---|---|---|---|
| `wheel_spin` | CONTINUOUS | A.frame | B.wheel | horizontal `(1,0,0)` or `(0,1,0)` | unbounded | main waterwheel axle |
| `chute_mount` | FIXED | A.frame | A.chute | n/a | fixed | only if chute is separate part |
| `gate_slide` | PRISMATIC | A.chute/frame | C.gate | `(0,0,1)` or local guide axis | short travel | sliding sluice/regulator |
| `flap_hinge` | REVOLUTE | A.launder/frame | C.flap | horizontal | bounded | shutoff or inspection flap |
| `brake_pivot` | REVOLUTE | A.frame | C.brake_arm | horizontal/vertical by source | bounded | side brake lever |

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
| `support_style` | enum | `simple_frame_chute` / `timber_mill_frame` / `masonry_flume_support` / `suspended_inlet_box` | `simple_frame_chute` | Slot A | S1-S4/S12 |
| `wheel_style` | enum | `spoked_shallow_bucket_wheel` / `deep_timber_bucket_wheel` / `drive_pinion_rotor` / `cast_iron_bucket_wheel` | `spoked_shallow_bucket_wheel` | Slot B | S1/S2/S6/S10 |
| `control_style` | enum | `fixed_chute_only` / `sliding_sluice_gate` / `pivoting_shutoff_flap` / `brake_arm` / `hinged_guard_panel` | `fixed_chute_only` | Slot C | S1/S4/S7-S9 |
| `bucket_count` | int | `12-32` | 18 | repeated bucket/paddle visuals on wheel | all wheel sources |
| `wheel_axis` | enum | `x` / `y` | `x` | determined by support orientation | all sources |

## Multiplicity / Copy Logic

- `bucket_count` controls the repeated bucket/paddle visuals on Slot B `bucket_wheel`. Seed-0 uses `N=18`.
- The copied object is bucket/paddle geometry baked into the single rotating wheel part. Buckets are not independent child parts and have no per-bucket joints.
- Naming should use `bucket_i` / `paddle_i` for named visuals when exposed for tests or inspection.
- Placement is radial around the wheel rim: bucket `i` is placed at phase `i * 360° / N` about the horizontal wheel axis, with all bucket openings oriented consistently for overshot flow.
- Changing `N` changes only the wheel visual density. The articulation graph stays one `wheel_spin` CONTINUOUS joint plus any optional Slot C control/service joints.

## 拓扑多样性审计


| slot | candidate_count | 是否 >=3 | 备注 |
|---|---:|---|---|
| support_and_feed | 4 | yes | |
| bucket_wheel | 4 | yes | |
| water_control_or_service | 5 | yes | |

### Procedural Sampling / Sweep Plan

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊，不作为 anchor 或 reference seed。Sampling 先选择上游结构槽，再从 compatible 下游 candidate 集合中选择 module / multiplicity / module-local variant。

Compatibility matrix / gating：以「槽位图」「每槽位 Module Emits / Interfaces」「Validator」中定义的接口、joint 轴、支撑面、range 和互斥关系为准；不兼容组合必须在 sampler 或 `resolve_config` 中降级、重采样或拒绝，不能让 builder 后期失败。

Regression overrides：默认无。若未来 sweep 发现稳定失败组合，或 reviewer 指定固定回归样本，可以添加少量显式 regression seed，但必须写明 seed、组合和原因；不得用小型 curated / modulo 表作为主 seed domain。

Random sweep / viewer plan：首次模板验收跑 `uv run articraft template sweep-pipeline <slug>`，依赖 0、0-4、0-19、0-49 的 cumulative random seeds 检查 build、MatingContract、joint origin / axis / range、support、collision 和 。机械通过后 viewer 目检一小批随机 seed，重点看类别身份、比例、closed pose、bulky module、optional moving child、max multiplicity、captured-pin / bearing / hinge / rail 接口。


## Validator（author_run_tests 必须覆盖的点）
- 必须有支持架/石墩、水平轴 bucket wheel、上部 chute/launder/inlet 语义。
- wheel spin axis 必须水平，wheel must be centered between bearing supports.
- bucket/paddle count 与参数一致，围绕 rim 等角分布。
- sliding gate/flap/brake/guard 若启用，必须接触真实 frame/chute，并有正确轴向。
- chute 出口必须位于 wheel 上方或上前方，不能读成 undershot。

## Reject cases（必须能识别并拒绝）
- wheel 轴竖直，或没有 continuous wheel spin。
- 没有上方进水构件，导致像普通 flywheel。
- gate、flap、brake、guard 悬空或用不可见接口盘连接。
- 将 bucket/paddle 做成未连接的独立 FIXED child parts。

## 与相邻类别的边界
- `traditional_windmill`：有风帆和 cap yaw；waterwheel 是水槽驱动水平轮。
- `ferris_wheel`：Ferris wheel 有座舱/乘客吊舱，不应有 feed chute/gate。
- `gear_train` / `pulley`：本类必须有 overshot bucket rim 和水力语义。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核 |
