# Modular Spec — Badge / ID Holder Clip

## 元信息
| 项 | 值 |
|---|---|
| slug | `badge_id_holder_clip` |
| template path | `agent/templates/badge_id_holder_clip.py` |
| test path (optional) | `tests/agent/test_badge_id_holder_clip_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

`pattern`：根 `clip_body`（由 attachment 槽发出，同时内含一个随夹口一起动的抓取子件）作为
chassis；`badge_connector` 槽把徽章连接件挂到 `clip_body` 上的旋转钮座（swivel boss），用一个
grandfathered continuous swivel joint（captured-button 枢轴，无 MatingContract）。夹口子件
（spring_jaw / magnet_backer）是 attachment 模块内部发出的 revolute / prismatic 子件。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all readable 5-star samples in this category (2 origins + 6 forked variants) |
| source_index_policy | only adopted module sources are indexed below |

> 说明：源图规划里提到的 `rec_badge_id_holder_clip_var_reelbody`（retractable reel body）在磁盘上
> 不存在（`data/records/` 无该记录），因此 **不实现 reel 候选**——无 source 支撑。其余 8 个样本全部读取。

## 核心身份

一个佩戴在衣物上、用来固定 ID/姓名徽章的小器件：一端是**衣物抓取机构**（弹簧夹口 /
磁吸夹 / ——reel 无源不做），另一端是**徽章连接件**（透明打孔胶片带 / 硬质卡框 / 环扣），
两端通常由一个**旋转钮枢轴**连接，使连接件能相对夹子转动。默认成熟域 = 冲压金属鳄鱼夹 +
透明胶片带 + 旋钮。

不该混入：普通鳄鱼/电工/线夹（没有徽章连接件）、挂绳及其五金（裸钩 / 弹簧钩 / 分体钥匙圈作
整体）、装订/长尾夹/薯片袋夹/相框、冰箱贴 / 首饰扣。

## 槽位 + 候选模块表

### Slot A：attachment_mechanism（根 chassis + 抓取子件；① 骨架 / ② 关节 / ③ 夹体形态）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `alligator_pinch` | forked_anchor | rec_workspace__…__002 | L154-L329 | eligible if compatible | clip_body(冲压长下颚板+锯齿+折边侧颊+hinge_pin+torsion_spring+swivel_post/boss) + spring_jaw(hinge_barrel+锥形上簧板+上前齿) ；body_to_jaw REVOLUTE 轴 y |
| `bulldog_leaf` | forked_anchor | rec_badge_id_holder_clip_var_bulldog | L180-L434 | eligible if compatible | 同 part tree，但下/上板改成短宽 bulldog 叶片 + 两片上翘 `_bent_lever` 指扳 (mesh)；REVOLUTE 轴 y（③ 夹体形态变体） |
| `magnetic_clamp` | forked_anchor | rec_badge_id_holder_clip_var_magnetic_clamp | L85-L246 | eligible if compatible | clip_body = 扁平 front_plate + alignment_dimple + swivel_post/boss（无颊/无 hinge/无齿）；magnet_backer(backer_plate+2 magnet_pole) 以 body_to_backer PRISMATIC 轴 -z 夹合（② 关节变体，无锯齿） |

### Slot B：badge_connector（挂到 swivel boss 的徽章连接件；③ 连接件形态）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `clear_strap` | forked_anchor | rec_workspace__…__002 | L278-L310 | eligible if compatible | Planar Boundary Form：透明打孔胶片带（rounded plate + grommet 圆孔 + 徽章长槽 + grid 矩形孔）+ swivel_button_ring + button_window |
| `card_frame` | forked_anchor | rec_badge_id_holder_clip_var_card_frame | L118-L339 | eligible if compatible | Volumetric Envelope Form：硬质开口卡框（cadquery back panel + 三面凸边 + 顶部开口 CR80 卡槽）+ button_ring + window |
| `ring_loop` | forked_anchor | rec_badge_id_holder_clip_var_ring_loop | L278-L308 | eligible if compatible | Macro Surface Construction：短颈 `neck_shank` + 立在 XZ 面的 torus `ring_loop` + button_ring + window |

硬约束满足：Slot A 3 候选、Slot B 3 候选，均 ≥2 且各来自结构不同的样本；全部 `forked_anchor` 且引真实
`model.py:Lx-Ly`。swivel（旋钮）只有一个真实候选（origin 的 snap-button continuous），按 §B 折成 A→B 的
**接口**而非独立槽。jaw 锯齿数是 §8 的 multiplicity 轴（同构齿 ×N），不是独立槽。

## 槽位图（slot graph）

```
pattern: parallel_children

attachment_mechanism (Slot A, root = clip_body)
   ├─[internal REVOLUTE axis y  | 捕获 hinge_pin↔hinge_barrel]  spring_jaw      (alligator/bulldog)
   ├─[internal PRISMATIC axis -z| magnet_pole↔front_plate 贴合] magnet_backer   (magnetic)
   └─[downstream: swivel_boss +z 面, anchor=(swivel_x,0,boss_top_z)]
          └─[CONTINUOUS axis z | captured-button, 无 MatingContract(grandfathered)]
                 badge_connector (Slot B)  ← 读取 ctx.upstream_interface.part_name="clip_body"，自发 swivel joint
```

- 连接点：`clip_body.swivel_boss` 顶面（+z）为 downstream anchor；`badge_connector` 的 part frame 原点
  即 swivel joint 原点，`swivel_button_ring` 含 (0,0,0)。
- 跨 slot joint：CONTINUOUS 轴 (0,0,1)，captured-button 枢轴，**omit MatingContract**（pin/crimp 几何无法
  两轴对齐面），origin 落在 boss 对称中心线（过 `fail_if_articulation_origin_far_from_geometry` 的旋转对称豁免）。
- attachment 的内部子件（jaw/backer）由 attachment 工厂**手动**发关节；badge_connector **不声明 upstream 接口**，
  故 assembler 不自动 chain（parallel_children，与 usb_drive_with_swivel_cover 同型）。

## 每槽位 Module Emits / Interfaces

### Slot A / module alligator_pinch（root）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `clip_body`, `spring_jaw` | 002 / L154-L276 |
| internal joints | `body_to_jaw` REVOLUTE 轴 y range [0, jaw_open_upper] | 002 / L312-L320 |
| upstream interface | 无（root） | — |
| downstream interface | `swivel_boss` +z, anchor=(0.045,0,boss_top_z) | 002 / L212-L223 |

### Slot A / module bulldog_leaf（root）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `clip_body`, `spring_jaw`(含 2×`finger_lever` mesh) | var_bulldog / L199-L371 |
| internal joints | `body_to_jaw` REVOLUTE 轴 y range [0, jaw_open_upper] | var_bulldog / L413-L421 |
| downstream interface | `swivel_boss` +z | var_bulldog / L276-L287 |

### Slot A / module magnetic_clamp（root）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `clip_body`(front_plate), `magnet_backer` | var_magnetic_clamp / L105-L175 |
| internal joints | `body_to_backer` PRISMATIC 轴 -z range [0, clamp_travel] | var_magnetic_clamp / L224-L232 |
| downstream interface | `swivel_boss` +z, anchor=(0.030,0,boss_top_z) | var_magnetic_clamp / L130-L142 |

### Slot B / module clear_strap
| emits | 描述 | 来源 |
|---|---|---|
| parts | `badge_connector`(perforated_clear_strap+swivel_button_ring+button_window) | 002 / L278-L310 |
| internal joints | `body_to_connector` CONTINUOUS 轴 z（工厂自发，parent=clip_body） | 002 / L321-L329 |
| upstream interface | 不声明（parallel child，读 ctx.upstream_interface） | — |

（card_frame / ring_loop 同型，只换 badge_connector 的形态 part，见 Slot B 表。）

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `attachment_module` | enum | alligator_pinch / bulldog_leaf / magnetic_clamp | — | choice | deterministic sampler | Slot A |
| `connector_module` | enum | clear_strap / card_frame / ring_loop | — | choice | deterministic sampler | Slot B |
| `tooth_count` | int | [3, 12] | 6 | conditional | 仅 pinch/bulldog 有效；magnetic 忽略（=0）；pitch/tooth_width 由总跨 ~0.019 派生 | 002 / var_teeth_n3 / var_teeth_n10 |
| `jaw_open_upper` | float | [0.38, 0.52] | 0.45 | independent | REVOLUTE 上界；仅 pinch/bulldog | 002 / L319 |
| `clamp_travel` | float | [0.010, 0.014] | 0.012 | independent | PRISMATIC 上界；仅 magnetic | var_magnetic_clamp / L231 |
| `connector_len_scale` | float | [0.9, 1.15] | 1.0 | independent | 只缩放连接件延伸长度（strap 长 / card 高 / ring 颈），不改 button 座 | 连接件源 |
| `palette_theme` | enum | polished_chrome / brushed_nickel / brass_black | polished_chrome | choice | 涂装 ride-along | 全样本 |
| (—) | constraint | — | — | conditional | tooth_count 与 jaw_open_upper 只在 pinch/bulldog 解析；clamp_travel 只在 magnetic 解析 | 接口 |

连续尺寸采样契约：先独立采 `jaw_open_upper` / `clamp_travel` / `connector_len_scale`，无 equation 从属，无跨部件
inequality（连接件与夹体的扫掠重叠由 captured-swivel allow_overlap 处理，不靠尺寸回缩）。`tooth_count` 按 §8 加权采样。

## 7.5 编译预算 / compile budget
自报 **每-seed ≤ 12s**（实测 origin/variant 记录 `external check` ~4s；含 1-2 个 cadquery 布尔件 + 1 torus）。
分档 tessellation：cadquery mesh tolerance 0.00025-0.0003；torus radial ≤28 / tubular ≤36；N 齿复用同一 `_tooth_bar`。
超预算先降 mesh tolerance / torus 段数再迭代。

## Multiplicity / Copy Logic
- 有 1 根 multiplicity 轴：**jaw_serrations N**（锯齿数）。
- `count_param`：`tooth_count`（喂给 `_tooth_bar(count,…)`，同时用于 lower_jaw_teeth 与 upper_front_teeth 两排）。
- `N_range`：产品域 [3, 12]；sampling domain 加权（小 N 高频：3-6 常见，7-12 稀有）。sweep 上限 12。
- copied object：单个矩形锯齿，在一条薄背条上按等 pitch 复制；naming：`_tooth_bar` 内 loop-indexed（源 helper，template-clean）。
- placement：等 pitch 跨 bar；总跨固定 ~0.019，`pitch=(0.019 - tooth_width)/(N-1)`，`tooth_width=clamp(0.019/N*0.7,…)`。
- joint policy：锯齿是 FIXED 融进各自颚板的 host visual（随该板的 revolute 一起动），不是独立 part。
- gating：magnetic_clamp 无锯齿 → tooth 轴记 `none`，不发齿。

## 视觉多样性 6 轴考察
| 轴 | 怎么判断 | 有/无 | 取值/来源 或 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | pinch/bulldog：clip_body+spring_jaw（2 part，revolute 子件）；magnetic：clip_body+magnet_backer（prismatic 子件）。均 forked_anchor（002 / var_bulldog / var_magnetic_clamp）。connector 恒为第 3 个挂件 part。 |
| └ multiplicity | 同构件 ×N | 有 | jaw 锯齿 N∈[3,12]，见 §8（002=6 / var_teeth_n3=3 / var_teeth_n10=10）。 |
| ② 关节类型 | 换 type/轴 | 有 | REVOLUTE 轴 y（弹簧夹口）· CONTINUOUS 轴 z（旋钮）· PRISMATIC 轴 -z（磁夹）。均 source-backed；每种都在 sweep 出现。 |
| ③ 主体形态家族 | 换核心 part 的可识别几何原型 | 有 | 夹体：alligator 长颚 vs bulldog 短宽叶+指扳（③）。连接件：clear_strap=Planar Boundary Form / card_frame=Volumetric Envelope Form / ring_loop=Macro Surface Construction。均登记进 `slot_choices` 的 connector 槽，source-backed。 |
| ④ 表面装饰 | 叠表面细节 | 有(record_only) | strap 打孔 grid + 徽章长槽 + grommet 圆孔、锯齿、cheek 圆孔、pressed_rivet——均写成宿主 part 的 visual，由宿主面派生，不作独立 part / joint；不设专门装饰候选。 |
| ⑤ 尺寸/行程 | 只改连续尺寸/行程 | 有 | jaw REVOLUTE 轴 y [0, 0.38-0.52]（开=teeth +z 抬升）；clamp PRISMATIC 轴 -z [0, 0.010-0.014]（开=backer 远离 front_plate）；swivel CONTINUOUS 整圈。connector_len_scale [0.9,1.15]。motion_test_plan：跑 `fail_if_parts_overlap_in_sampled_poses`（captured 枢轴 element/broad allow）+ targeted `ctx.pose`：jaw 开抬齿、clamp 开离板、swivel 90° 换向。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | polished_chrome / brushed_nickel / brass_black（≥3 主题；金属大类 + 透明 vinyl / 黑磁 / 硬塑）。ride-along。 |

## 采样与覆盖审计

总组合数：attachment(3) × connector(3) × tooth_count(pinch/bulldog≈10 档，magnetic 无) × palette(3)。
离散拓扑元组（attachment×connector）= 9；含 tooth N 与 palette 后 seed 覆盖充分。

理由：类别属 **simple** richness band；主多样性来自 3×3 离散 module 网格 + N 齿 multiplicity + 3 关节类型，
连续 scale 仅作 ride-along。

seed_domain_policy：procedural_first（seed 0 不特殊，走同一采样器）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次采
attachment / connector / palette / tooth_count（加权）/ jaw_open_upper / clamp_travel / connector_len_scale；
compatibility：无非法 module 对（3×3 全合法）；tooth/jaw 参数仅在 pinch/bulldog 解析，clamp_travel 仅在 magnetic
解析（conditional gating in `resolve_config`）。无 regression override。random sweep 0-35 初测，viewer 目检 0-2。
Topology target：真实离散拓扑空间仅 9（3×3），远小于 300——**类别本身 simple**、源锚点上限即此；report-only 不作 gate。
Controlled local parameterization：`jaw_open_upper` / `clamp_travel` / `connector_len_scale`（见 §7，均 independent，
resolve_config 内 clamp）；不破坏 InterfaceSpec（swivel boss 座固定）/ swivel captured 枢轴 / N 复制。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 attachment→connector，加权 tooth N，palette/scale 独立采样后 clamp | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 3×3 全合法；tooth/jaw 仅 pinch/bulldog、clamp 仅 magnetic（conditional 解析） | 无锯齿出现在 magnetic；无 clamp 参数用于 pinch |
| controlled local variation | jaw/clamp 行程 + 连接件长度 scale，clamp 在 resolve | 比例变化不破坏接口 / 枢轴 / 类别 identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 初测，0-999 成熟度 | contract failures；axis_realization；viewer 0-2 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| attachment_mechanism | 3 | yes | yes | |
| badge_connector | 3 | yes | yes | |

## Validator
- slot_choices_for_seed 返回已实现的 module 名（attachment / connector / tooth_count / palette）
- config_from_seed 对所有普通 seed（含 0）用 deterministic procedural sampling
- compatibility：tooth/jaw 仅 pinch/bulldog，clamp 仅 magnetic（resolve_config 解析，不留到 builder）
- 关键接口：swivel_boss +z downstream；badge_connector part frame 含原点；captured swivel 无 MatingContract
- 关节：body_to_jaw REVOLUTE 轴 y / body_to_backer PRISMATIC 轴 -z / body_to_connector CONTINUOUS 轴 z
- N 齿 loop-emit（`_tooth_bar`），FIXED 融进颚板，不作独立 part
- 连续 scale 在 resolve_config clamp，不破坏枢轴 / 接口

## Reject cases
- 把不动的锯齿 / grommet / pressed_rivet / cheek 圆孔做成 FIXED-joint 独立 part（违反 Rule 1）
- swivel 连接件飘在 boss 上方有缝（未落 captured 枢轴 seating / origin 离几何过远）
- magnetic 变体仍保留弹簧颚 / 锯齿（应无颚无齿）
- 连接件在 180° 旋转扫过夹体时穿模且未声明 captured-swivel allow_overlap
- 用连续 scale / 涂装冒充离散多样性；或新增无源支撑的 reel/pin-back skeleton
- 下颚与上颚闭合无间隙（应保留 realistic closed clearance）

## 与相邻类别的边界
- 不该混入：普通鳄鱼/电工夹（无徽章连接件——本类必须保留 swivel 连接件）
- 不该混入：挂绳五金 / carabiner / 分体钥匙圈（ring_loop 是**旋钮上的**连接件，不是整体挂绳）
- 不该混入：长尾/装订夹、相框、冰箱贴（bulldog 候选是弹簧夹口的形态变体，必须保留 revolute 夹口 + swivel）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 8 个可读 5 星样本（reelbody 无源，不实现）；parallel_children，swivel captured 枢轴 grandfathered，同 usb_drive_with_swivel_cover 型 |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | alligator_pinch | rec_workspace__…__002 | L154-L329 | clip_body+spring_jaw part tree + revolute + swivel downstream |
| S2 | A | bulldog_leaf | rec_badge_id_holder_clip_var_bulldog | L199-L434 | bulldog 叶片 + `_bent_lever` 指扳 |
| S3 | A | magnetic_clamp | rec_badge_id_holder_clip_var_magnetic_clamp | L105-L246 | front_plate + magnet_backer + prismatic |
| S4 | B | clear_strap | rec_workspace__…__002 | L278-L310 | 透明打孔胶片带 (Planar) |
| S5 | B | card_frame | rec_badge_id_holder_clip_var_card_frame | L118-L339 | 硬质卡框 (Volumetric) |
| S6 | B | ring_loop | rec_badge_id_holder_clip_var_ring_loop | L278-L308 | 环扣 (Macro Surface) |
| S7 | A(mult) | tooth_count | rec_badge_id_holder_clip_var_teeth_n3 / _n10 | L177,L272 | N 齿采样域 3 / 10 |
```
