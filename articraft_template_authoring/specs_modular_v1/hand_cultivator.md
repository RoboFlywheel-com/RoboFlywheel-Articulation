# Modular Spec — Agricultural / Hand cultivator

## 元信息
| 项 | 值 |
|---|---|
| slug | `hand_cultivator` |
| template path | `agent/templates/hand_cultivator.py` |
| test path (optional) | `tests/agent/test_hand_cultivator_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children root `frame` + one CONTINUOUS wheel child + tine multiplicity) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in category `hand_cultivator` (1 origin + 9 slot-fork variants) |
| source_index_policy | only adopted module sources are indexed below |

阅读摘要：全部 10 个样本共享同一骨架 —— 单一 `frame` 部件（把手 + 钢叉/横杆/rake_neck/rake_crossbar +
工作头 + 轴销硬件 + 铆钉全部是 `frame` 上的 visual，均为 FIXED，按 Rule 1 内联为 parent.visual），
外加唯一一个独立部件 `tine_wheel`，由唯一活动关节 `wheel_axle`（CONTINUOUS, axis=(0,1,0),
origin=(0,0,0.33)）挂在 `frame` 上。所有 fork 只改**一个**结构层：working_head（5 形态）/
ground_wheel（3 形态）/ handle_config（2 形态），或 tine 复制数 N（3/5/7）。轴销 `axle_pin` 被
`tine_wheel` 的 hub 捕获（element-scoped allow_overlap），是全类唯一的非 FIXED 关节，每个 seed 必须保留。

关键几何原语（不得降级为 Box/Cylinder，Rule 3）：`tube_from_spline_points`（把手/钢叉/spring
爪/rigid 齿/frog 撑）、`_torus_y` mesh 铁圈、`_flat_plate` mesh（stirrup 刀片）、`_duckfoot_sweep`
mesh（V 型鸭掌板）、`_ridger_moldboard_surface` 14×12 曲面 mesh + `_ridger_share_edge` +
`_ridger_central_spine`、`WheelGeometry`/`TireGeometry` SDK 原语（pneumatic 轮）、`Cylinder`
（hub_shell / iron_disc / 轴销 / 螺母 / shaft_collar）、`Sphere`（铆钉头）。

## 核心身份

Hand cultivator（步行式 **wheel-hoe / 轮锄**）：一个可站立推行的单轮松土工具。恒定不变的读法 =
**大直径地轮**（`tine_wheel`，唯一转动件）在前，**可换工作头**（爪/齿/锄刀/鸭掌/培土犁）在后贴地，
上方伸出**长把手**（双直柄或单中柄）供操作者站立扶握。锈钢/涂装钢叉把三者连成一个刚性 `frame`。
成熟域 = 家用/园圃手推轮锄。

不该混入：带动力的 **rotary tiller / 微耕机**（有发动机与传动，非纯人力单轮）；**garden rake /
hand rake**（无轮、无长柄推行结构）；**wheelbarrow / garden cart**（载物斗，非松土头）；**plough
（畜/机引犁）**（无扶手轮组、非手推）。

## 槽位 + 候选模块表

### Slot A：working_head（③ 主体形态家族 / Primary Form Family —— 本类的“星”）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype | 结构特征 |
|---|---|---|---|---|---|---|
| spring_tine_claws | forked_anchor(origin) | rec_use-the-attached-reference-image-as-the-primary-_20260625_155418_882758_a6707f8e | L181-L197 | eligible if compatible | Volumetric Envelope Form | N 根 4-点弯簧齿 `spring_claw_{i}` + 亮尖 `worn_claw_tip_{i}`，`_straight_tube` 曲线扫掠，根植 `rake_crossbar`；带 N 复制 |
| rigid_tines | forked_anchor | rec_cultivator_var_rigid_tines | L179-L209 | eligible if compatible | Volumetric Envelope Form | N 根竖直直落 `rigid_tine_{i}` + `rigid_tine_tip_{i}`，`_straight_tube` 直线扫掠，根植 `rake_crossbar`；带 N 复制 |
| stirrup_hoe | forked_anchor | rec_cultivator_var_stirrup_hoe | L91-L118(`_flat_plate`), L209-L257 | eligible if compatible | Planar Boundary Form | U 形 stirrup 框（pivot_bolt + 2 arm + bottom_bar）+ 平刀片 `stirrup_blade`(`_flat_plate`) + 亮刃 `stirrup_cutting_edge`；单头无 N |
| sweep | forked_anchor | rec_cultivator_var_sweep | L91-L135(`_duckfoot_sweep`), L220-L251 | eligible if compatible | Planar Boundary Form | 竖 shank `sweep_shank` + collar + 宽 V 鸭掌板 `sweep_blade`(mesh) + 亮刃 `sweep_worn_edge`；单头无 N |
| ridger | forked_anchor | rec_cultivator_var_ridger | L91-L219(3 mesh helper), L304-L340 | eligible if compatible | Macro Surface Construction | frog 撑架 `moldboard_brace`+`frog_gusset_{s}` + 复合曲面翻土板 `ridger_moldboard`(14×12 grid mesh) + `ridger_share_edge` + `ridger_spine`；单头无 N |

- ③ 主体形态家族达标：5 candidate 覆盖 3 个 form_subtype（Volumetric Envelope ×2 / Planar Boundary ×2 / Macro Surface ×1），全部 source-backed。
- spring vs rigid 结构差异 = 齿母线离散不同（弯 vs 直），同 part tree / 同 `_straight_tube` primitive / 同 `rake_crossbar` interface → 合法的 Volumetric Envelope 区分（非只换尺寸）。

### Slot B：ground_wheel（唯一活动件所在层）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| spoked_iron | forked_anchor(origin) | rec_use-the-attached-reference-image-as-the-primary-_20260625_155418_882758_a6707f8e | L228-L264 | eligible if compatible | `outer_iron_rim`+`inner_iron_rim`(`_torus_y` mesh) + `hub_shell`(Cyl) + `wheel_spoke_{i}` ×N_spokes + `wheel_lug_{i}` ×10 + 亮尖 |
| solid_disc | forked_anchor | rec_cultivator_var_disc_wheel | L215-L254 | eligible if compatible | `outer_iron_rim`(torus) + `iron_disc`(Cyl r=0.29,len=0.008 实心盘) + `hub_shell` + lugs；无辐条 |
| pneumatic | forked_anchor | rec_cultivator_var_pneumatic_wheel | L5-L25(imports), L201-L275 | eligible if compatible | `steel_wheel`(`WheelGeometry`+hub+spokes) + `rubber_tire`(`TireGeometry` torus) + lugs；SDK 复合原语 |

### Slot C：handle_config

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| double_straight | forked_anchor(origin) | rec_use-the-attached-reference-image-as-the-primary-_20260625_155418_882758_a6707f8e | L111-L156 | eligible if compatible | 双长木柄 `wood_handle_{0,1}`+`rubber_grip_{0,1}` + 双 `upright_strap_{s}` 连叉 |
| single_central | forked_anchor | rec_cultivator_var_single_handle | L110-L171 | eligible if compatible | 单中柄 `central_handle`+`rubber_grip` + `shaft_collar` + 向心收拢的 `upright_strap_{s}` |

硬约束核对：Slot A=5、B=3、C=2（C 只有 2 个结构不同 candidate，样本池仅这两种真实形态；已达 ≥2，
degrade 理由：双柄/单柄是把手层仅有的两种真实拓扑，T/loop grip 属世界知识外推、本批不入采样，见排除项）。
无单-candidate slot。所有普通 candidate 均 forked_anchor + 真实 model.py 行号。

## 槽位图（slot graph）

pattern: mixed

```
                       [Slot C handle_config]
                              │ FIXED visuals on frame (upright_strap 端点落在 side_rail 与 handle 上)
                              ▼
[axle hardware]──contact──[frame 钢叉 side_rail_{s}]──contact──[head_crossbar]──contact──[rake_neck]──contact──[rake_crossbar]
      │                                                                                                   │ FIXED visuals on frame
      │ CONTINUOUS wheel_axle (axis (0,1,0), origin (0,0,0.33))                                            ▼
      ▼                                                                                        [Slot A working_head]
[Slot B ground_wheel = tine_wheel 部件]                                                        (spring_claw_{i} ×N / rigid_tine_{i} ×N / stirrup / sweep / ridger)
   hub 捕获 axle_pin (element-scoped allow_overlap)
```

- **唯一跨部件关节**：`wheel_axle` CONTINUOUS，parent=`frame`，child=`tine_wheel`，axis=(0,1,0)，
  origin=(0,0,0.33)。接口点位 = 轴线中心（hub 对称中心 = 旋转 origin，落在 `axle_pin` 与 hub 硬件上）。
  该关节几何为 pin-through-hub（捕获销），**omit `MatingContract`**（grandfathered，Rule 2 允许），
  用 element-scoped `allow_overlap(frame.axle_pin, wheel.<hub>)` 守护。
- **Slot A / Slot C / 所有钢叉横杆 = `frame` 上的 FIXED visual**（Rule 1：不动件不建独立 part）。它们靠
  几何真实接触连成一个连通体（模板级 island 检查 tol=1µm，每个 tube 端点与相邻 member 端点重合以保证连通）。
- **互斥/条件**：tine 复制数 N 仅当 working_head ∈ {spring_tine_claws, rigid_tines} 时存在（`conditional`）；
  blade 头（stirrup/sweep/ridger）为单头，N 不适用。wheel spoke 数 `n_spokes` 仅当 ground_wheel=spoked_iron 存在。

## 每槽位 Module Emits / Interfaces

### Slot A / working_head（所有 candidate emit 到 `frame`，无内部关节）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；全部为 `frame` visual | origin L181-197 等 |
| internal joints | 无（FIXED 内联；Rule 1） | — |
| upstream interface | 头部根植在 `rake_crossbar`(tine 头 / stirrup)或 `rake_neck` 末端 shank（sweep/ridger），端点与横杆几何重合 | origin L173-177 |
| downstream interface | 无（末端工作面，落地） | — |

### Slot B / ground_wheel（emit `tine_wheel` 部件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tine_wheel`（rim/disc/steel_wheel + hub + spokes/tire + lugs + 亮尖） | origin L228-264 |
| internal joints | 无（轮内全部 visual） | — |
| upstream interface | hub 对称中心 = `wheel_axle` origin (0,0,0.33)，捕获 `axle_pin` | origin L266-274 |
| downstream interface | 无 | — |

### Slot C / handle_config（emit 到 `frame`）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`wood_handle_*`/`central_handle`+`rubber_grip*`+`upright_strap_{s}`(+`shaft_collar`) 均 frame visual | origin L111-156 / single L110-171 |
| internal joints | 无 | — |
| upstream interface | `upright_strap_{s}` 下端落在 `side_rail_{s}` 上、上端落在 handle 首点上（端点重合保证连通） | origin L141-147 |
| downstream interface | 无 | — |

### 骨架（frame 核心，非 slot，固定结构）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`（root）：`side_rail_{s}`、`head_crossbar`、`rake_neck`、`rake_crossbar`、`axle_pin`、`axle_nut_{0,1}`、`bolt_head_{i}` | origin L132-226 |
| internal joints | 无 | — |
| downstream interface | `axle_pin` @ (0,0,0.33) 供 `wheel_axle` | origin L200-205, L266-274 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| working_head | enum | spring_tine_claws / rigid_tines / stirrup_hoe / sweep / ridger | — | choice | deterministic sampler | Slot A 表 |
| ground_wheel | enum | spoked_iron / solid_disc / pneumatic | — | choice | deterministic sampler | Slot B 表 |
| handle_config | enum | double_straight / single_central | — | choice | deterministic sampler | Slot C 表 |
| palette_style | enum | rusted_iron / painted_green / painted_red / galvanized / blued_steel / planet_jr | rusted_iron | choice | `rng.choice(PALETTE_STYLES)` | §8.5 ⑥ |
| n_tines | int (multiplicity) | [3,9]，测试档 {3,5,7,9} | 5 | conditional | 仅 head∈{spring,rigid} 有效；否则不发射；clamp[3,9] | tines3/origin/tines7 §8 |
| n_spokes | int | [6,16] | 8 | conditional | 仅 wheel=spoked_iron 有效；clamp[6,16] | origin L237 |
| wheel_radius_scale | float | [0.82, 1.30] | 1.0 | independent | 轮外径 ±；clamp | §8.5 ⑤ (source map dia ±30%) |
| handle_len_scale | float | [0.88, 1.15] | 1.0 | independent | 柄长/操作者站距；clamp | origin L113-118 |
| handle_spread_scale | float | [0.85, 1.20] | 1.0 | independent | 双柄横向张开（single 无效）；clamp | origin L111 |
| head_depth_scale | float | [0.85, 1.20] | 1.0 | independent | 工作头下探深度；clamp | origin L181-197 |
| tine_spacing_scale | float | [0.85, 1.15] | 1.0 | independent | tine 横向间距；clamp | tines7 L182-184 |
| (—) | constraint | — | — | inequality | tine 排宽 `(N-1)*span ≤ crossbar_span-2*margin`：超出按比例回缩 span | rake_crossbar L174 |
| (—) | constraint | — | — | inequality | 轮上缘 `axle_z + wheel_r*scale` 不得顶到 single_central 柄下缘（single 柄首点 z ≥ 轮上缘+clearance）：违反抬高柄首点 | single L111-116 |
| (—) | constraint | — | — | inequality | lug 根半径 = `wheel_outer_r - lug_embed`（lug 必嵌入 rim/tread，避免轮内 island） | pneumatic 修正 |

连续尺寸采样契约：先采所有 independent scale（均匀）→ 无 equation 从属 → 用 3 条 inequality
在 `resolve_config` 内投影/回缩（tine 排宽、single 柄避轮、lug 嵌入）→ conditional（N、n_spokes、
handle_spread 仅特定 enum 有效）在采样后按上游 choice 解析。所有约束在 `resolve_config` 求解，不留到 builder。

## 7.5 编译预算 / compile budget

自报预算：**≤15s/seed**（§7.5 上限 20s）。依据：最重组合 = ridger 复合曲面（14×12 grid ≈ 360 面）
+ pneumatic `TireGeometry`（tread count 降到 ≤14）同一 seed 不会同现（head 与 wheel 独立采），单件
mesh 面数受控。分档 tessellation：`_torus_y` major 72 / tube 12；spoke/tube radial 10-12；tire tread
count ≤14、tube/major 段数走 SDK 默认但半径特征小。N 个 tine 复用同一 `_straight_tube` 几何函数。
超预算先降 torus/tire 段数再迭代。

## 8. Multiplicity / Copy Logic

**轴 1（主）：n_tines —— cultivator 齿数**
- `count_param`：`n_tines`；`N_range`：产品域 [3,9]，测试档 {3,5,7,9}（源覆盖 3/5/7）。
- sampling domain（权重档）：小 N 偏多 —— 3:0.30, 5:0.40, 7:0.20, 9:0.10（5 最典型）。
- copied object：弯簧齿 `spring_claw_{i}`+`worn_claw_tip_{i}`（spring 头）或 `rigid_tine_{i}`+`rigid_tine_tip_{i}`（rigid 头），共用同一 `_straight_tube` helper。
- naming：`spring_claw_{i}` / `rigid_tine_{i}`（i=0..N-1）。
- placement：沿 `rake_crossbar` 在 y∈[-half,+half] 等距，`y_i = y_min + (y_max-y_min)*i/(N-1)`（tines7 L184），每根根点 (-crossbar_x, y_i, crossbar_z) 落在 rake_crossbar 上。
- joint policy：FIXED 视觉（Rule 1，不单独铰接）。
- source/gating：**conditional** —— 仅 head∈{spring_tine_claws, rigid_tines} 发射；blade 头（stirrup/sweep/ridger）为单头，此轴不存在（slot_choice 记 `("n_tines","n0")` 表示不适用）。

**轴 2（次，非模板级复制多样性，仅覆盖）：n_spokes —— 铁辐轮辐条数**
- 仅 ground_wheel=spoked_iron 有效；[6,16]，测试档 {6,8,12,16}；copied object=`wheel_spoke_{i}`（`_wheel_spoke`），FIXED 视觉，均匀角分布。非 spoked 轮不发射。
- 注：wheel spokes 是 param 非 slot；N 不计入结构 distinct，只覆盖。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 骨架恒为 `frame` + `tine_wheel`（1 CONTINUOUS）。结构变化经 3 个 slot 的 FIXED-visual 形态实现（head 5 / wheel 3 / handle 2），无“增删活动 part”。全部 forked_anchor。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：n_tines∈[3,9] 权重档（conditional on tine 头）；次级 n_spokes∈[6,16]（conditional on spoked 轮）。 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 无（单一） | 全类唯一活动关节恒为 `wheel_axle` CONTINUOUS(axis (0,1,0))；源无第二活动轴（depth-pivot 属外推、本批不做）。理由：类别本征只有地轮一处转动。该 CONTINUOUS 每 seed 都出现。 |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 可识别几何形态原型 | 有 | working_head 5 原型，覆盖 3 form_subtype：spring_tine_claws / rigid_tines = **Volumetric Envelope Form**（弯 vs 直扫掠母线）；stirrup_hoe / sweep = **Planar Boundary Form**（U-loop+平刀片 / 宽 V 鸭掌平板）；ridger = **Macro Surface Construction**（14×12 复合翻土曲面壳）。全部 forked_anchor，登记进 `slot_choices`。 |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | `bolt_head_{i}` 铆钉头（Sphere，嵌在 member 上，随头/柄选择重定位）+ 各头亮 `worn_*` 刃/尖（host-conformal，落在其宿主刀片/齿面）。source_type=record_only（origin L215-226 铆钉 + 各头亮刃）。装饰数随 head/wheel 派生（③→⑤→④ 顺序）。 |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | wheel_radius_scale[0.82,1.30]、handle_len_scale[0.88,1.15]、handle_spread_scale[0.85,1.20]、head_depth_scale[0.85,1.20]、tine_spacing_scale[0.85,1.15]。唯一非-continuous 关节？无 —— `wheel_axle` 是 continuous，运动包络 = 整圈旋转，sampled-pose 全圈不穿模（motion_test_plan：`fail_if_parts_overlap_in_sampled_poses` + targeted `ctx.pose({axle: 1.1})` 验证轮上亮尖可见位移）。 |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | 6 palette：rusted_iron / painted_green / painted_red / galvanized / blued_steel / planet_jr(green frame + yellow wheel)，每个含木柄色 + 橡胶握把 + 钢件主色 + 铆钉暗色 + 亮刃色 + 轮胎黑。材质大类：metal(painted/rusted/galvanized/blued) + wood + rubber，≥ceil(0.5×6)=3。source_type=record_only。 |

**收尾自检**：batch 0-9 需肉眼看到 5 种 head 形态、3 种轮、双/单柄、N 覆盖、6 涂装、铆钉贴合、轮旋转全程不穿模。

## 拓扑多样性审计

总组合数：A(5) × B(3) × C(2) = 30 个纯离散 slot 组合；乘 n_tines 测试档（tine 头 4 档，blade 头 1 档）
与 n_spokes（spoked 轮 4 档，其余 1 档）后覆盖面充分（按 ≥300 report-only 口径观察 slot choice tuple distinct on 1000 seeds：head×wheel×handle×N×spokes）。

理由：3 个 slot 每个 ≥2 candidate，deterministic sampler 均匀覆盖；N/spokes 只覆盖不计数。

seed_domain_policy：procedural_first。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 独立采样 3 个 slot enum
+ palette + N + n_spokes + 5 个连续 scale（seed=0 不特殊）。compatibility gating 在 `resolve_config`：
(a) N 仅 tine 头有效，(b) n_spokes 仅 spoked 轮有效，(c) handle_spread 仅 double 柄有效，
(d) 3 条 inequality 回缩（tine 排宽 / single 柄避轮 / lug 嵌入）。无 regression override（首版即 procedural）。
Topology target：1000-seed distinct 期望 按 ≥300 report-only 口径观察（head 5 × wheel 3 × handle 2 × N 覆盖 × spokes 覆盖）。
Controlled local parameterization：wheel_radius_scale / handle_len_scale / handle_spread_scale /
head_depth_scale / tine_spacing_scale —— 全在 `resolve_config` clamp/回缩，不破坏 `wheel_axle` origin、
frame 连通、tine 排宽、single 柄净空。按第 7 节约束类型声明（全 independent + 3 inequality + 若干 conditional）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 head→wheel→handle→palette→N→spokes→scales，均匀 choice + N/spokes 权重档 | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | N gated on tine 头；spokes gated on spoked 轮；handle_spread gated on double 柄；3 inequality 回缩 | 无 floating/island、轮旋转不穿模、single 柄避轮、tine 不越 crossbar |
| controlled local variation | 5 连续 scale + clamp/回缩 | 比例变化不破接口/连通/关节 origin/身份 |
| regression overrides | none | — |
| random sweep | seeds 0-35 首过，0-999 成熟审计 | contract failures；axis_realization 报告 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A working_head | 5 | yes | yes | ③ 主体形态家族，3 form_subtype |
| B ground_wheel | 3 | yes | yes | 唯一活动件所在层 |
| C handle_config | 2 | yes | no | 把手层仅 2 真实拓扑；T/loop 外推留后续（排除项） |

## Validator

- slot_choices_for_seed returns implemented module names（head/wheel/handle + `n_tines`/`n_spokes` 编码）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos（N 仅 tine 头、spokes 仅 spoked 轮、spread 仅 double 柄）
- optional regression overrides：none
- controlled local scale params clamped，不破 `wheel_axle` origin / frame 连通 / tine 排宽 / single 柄净空
- cross-part scale dependencies（inequality）在 `resolve_config` 求解，不留到 builder
- `wheel_axle` = CONTINUOUS, axis≈(0,1,0), origin≈(0,0,0.33)，每 seed 存在（唯一非-FIXED 关节）
- 捕获销 element-scoped `allow_overlap(frame.axle_pin, wheel.<hub>)` 存在
- N 个 tine visual 命名/等距/FIXED policy 正确；tine 头有 N 根，blade 头 0 根
- Rule 5：`fail_if_parts_overlap_in_sampled_poses` + targeted `ctx.pose({axle})` 断言轮可见旋转

## Reject cases

- `frame` 部件内出现 island（某 tube/铆钉/头件未与相邻 member 在 1µm 内接触）→ 模板级 island 硬失败。
- lug 根半径 ≥ 轮外接触半径（lug 悬空于 rim/tread 外）→ 轮部件 island。
- single_central 柄首点低于轮上缘 → 柄与旋转轮穿模（sampled-pose fail）。
- tine 排宽越过 `rake_crossbar` 端点 → tine 悬空/越界。
- 把 `wheel_axle` 降成 FIXED 或删除 → 零活动关节（拒绝）。
- 把 pneumatic `WheelGeometry`/`TireGeometry` 或 mesh 头降级为 Box/Cylinder → 违反 Rule 3。
- blade 头仍循环发射 N 根 tine，或 tine 头 N<3 → 形态错误。
- 单一涂装/材质大类不足 3 → ⑥ 不达标。

## 与相邻类别的边界

- 不该混入：**Rotary tiller / 微耕机**（有发动机+传动链，非纯人力单轮松土；本类无动力 part）。
- 不该混入：**Garden rake / hand rake**（无地轮、无长推柄骨架；本类恒有 `tine_wheel` + 长柄）。
- 不该混入：**Wheelbarrow / garden cart**（有载物斗，轮为承载非松土前导；本类无斗、头为工作刃）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 首版 spec；连续执行进入模板实现。关键风险：frame 单部件 1µm 连通（端点重合设计）+ pneumatic lug 嵌入修正。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | 骨架/A/B/C | origin | rec_use-the-attached-reference-image-as-the-primary-_20260625_155418_882758_a6707f8e | L21-274 | frame 骨架 + spring_tine_claws + spoked_iron + double_straight + wheel_axle |
| S2 | A | rigid_tines | rec_cultivator_var_rigid_tines | L179-209 | 直齿头 |
| S3 | A | stirrup_hoe | rec_cultivator_var_stirrup_hoe | L91-118,209-257 | stirrup U 刀头 |
| S4 | A | sweep | rec_cultivator_var_sweep | L91-135,220-251 | 鸭掌 sweep 头 |
| S5 | A | ridger | rec_cultivator_var_ridger | L91-219,304-340 | 培土犁翻土板 |
| S6 | B | solid_disc | rec_cultivator_var_disc_wheel | L215-254 | 实心盘轮 |
| S7 | B | pneumatic | rec_cultivator_var_pneumatic_wheel | L5-25,201-275 | 充气胎轮 |
| S8 | C | single_central | rec_cultivator_var_single_handle | L110-171 | 单中柄 |
| S9 | N | tines3 | rec_cultivator_var_tines3 | L181 | N=3 覆盖 |
| S10 | N | tines7 | rec_cultivator_var_tines7 | L181-199 | N=7 覆盖 + 通用间距公式 |
