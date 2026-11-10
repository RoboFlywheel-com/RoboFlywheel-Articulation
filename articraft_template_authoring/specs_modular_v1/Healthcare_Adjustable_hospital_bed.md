# Healthcare / Adjustable hospital bed — modular template spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `Healthcare_Adjustable_hospital_bed` |
| template path | `agent/templates/Healthcare_Adjustable_hospital_bed.py` |
| test path (optional) | `tests/agent/test_Healthcare_Adjustable_hospital_bed_template.py` (skipped while batch-authoring) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root base -> deck carrier [PRISMATIC for hi-lo] + parallel-child hinged deck sections + optional revolute side-rail pair + multiplicity on deck sections) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 (2 parents + 5 converged forks) |
| read_count | 7 |
| read_scope | all 5-star samples in this 小类 (per source map) |
| source_index_policy | only adopted module sources are indexed below |

Source handle map:

| handle | record_id | 用途 |
|---|---|---|
| S1 | rec_a-single-section-adjustable-hospital-bed-a-recta_20260623_174436_818326_5bfade45 | caster bed frame; single backrest; tubular boards; cushions/casters idioms |
| S2 | rec_an-adjustable-examination-treatment-couch-medica_20260623_174436_819096_4031599a | 4-leg exam couch; open (no boards); backrest tilt |
| S3 | rec_hospbed_var_knee_gatch | 2-section deck (backrest + knee) |
| S4 | rec_hospbed_var_three_section | 3-section profiling deck (backrest + thigh + chained calf) |
| S5 | rec_hospbed_var_side_rails | drop-down REVOLUTE side rails |
| S6 | rec_hospbed_var_hilo_column | cruciform wheeled base + central PRISMATIC lift column |
| S7 | rec_hospbed_var_footboard_panel | solid molded end-panel boards |

All seven share one world convention (S1/S3/S4/S5/S6/S7 verbatim; S2 aligned to it):
bed long axis = X (head -X, foot +X), width = Y, deck top `deck_top_z = 0.62`,
`backrest_hinge_x = -bed_len/6 = -0.333`, side rails at `y = +-0.47`, mattress width 0.82.
Cushions are `superellipse_side_loft` meshes (`_rounded_cushion_mesh`, S1 L59-89); casters
are folded-in visual sub-assemblies (S1 L201-271); the backrest is one REVOLUTE about Y.

## 核心身份

一张**可调节医疗床 / 诊疗床**：一个轮式或腿式支撑底座托起一张多段软垫睡卧面，
至少有一段 **REVOLUTE 抬背** section（"可调节"的定义特征），可再叠加膝/腿段
（膝盖 gatch / 三段 profiling），可选中央 **PRISMATIC 升降柱**、可选 **REVOLUTE 落式护栏**、
以及管式 / 无 / 实心面板的头尾板。默认成熟域 = 家用/病房护理床与诊疗检查床。

不该混入：普通床/床头柜（无 articulating 段、无医疗底座）；纯担架/推车（无抬背铰接段）；
坐姿 surgical_chair（连续坐盘+环抱背）。邻类边界 = picture-小类 medical bed。

## 槽位 + 候选模块表

### Slot B：base / mobility（root 支撑 + 提供 deck 承载 part）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| caster_base | forked_anchor | S1 | L131-271 | eligible if compatible | root==deck part `base_frame`；四角腿柱 (x=+-0.95) + 折入式 swivel caster（tire/stem/swivel/fork/axle/hub 子件），可滚动 |
| four_leg_couch | forked_anchor | S2 | L140-151, L254-263 | eligible if compatible | root==deck part `base_frame`；4 条内收刚性方腿 (x=+-0.80) 到地 + 脚垫，无轮，静止诊疗床 |
| hi_lo_column | forked_anchor | S6 | L188-237, L244-260, L377-385 | eligible if compatible | root `base`=十字轮式底盘 + 外柱 + 4 caster；`lift_column` deck part 经 PRISMATIC(z) 抬升整床 |

结构区分：caster=滚动四角、four_leg=静止内收腿、hi_lo=中央升降柱（多一条 PRISMATIC 轴 + 拆成两 part）。

### Slot A：deck articulation（可调节主机构；multiplicity N in {1,2,3}）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| single_backrest (N=1) | forked_anchor | S1 | L286-332 | eligible if compatible | 仅 backrest REVOLUTE(+Y) 抬头；其余是固定 hip deck |
| two_section_gatch (N=2) | forked_anchor | S3 | L326-425 | eligible if compatible | backrest + knee_section 各 REVOLUTE off deck；foot 端抬升 |
| three_section_profiling (N=3) | forked_anchor | S4 | L385-560 | eligible if compatible | backrest + thigh REVOLUTE off deck + calf REVOLUTE **chained off thigh**；raised-knee 轮廓 |

N 是 multiplicity 轴（1 fixed hip deck + N hinged sections，backrest 恒在，foot 侧 0/1/2 段），
编进 `slot_choices` 为 `("deck_sections","nN")`。N 不计入结构 distinct（VISUAL_DIVERSITY_MODEL 2），只买覆盖。

### Slot C：end boards（3 头尾板宏观表面）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| tubular_rail_boards | forked_anchor | S1 | L177-199 | eligible if compatible | 头尾各 2 立柱 + 3 横管栏（Planar Boundary Form：开放管框） |
| open_no_board | forked_anchor | S2 | couch has no end boards | eligible if compatible | 无头尾板（开放诊疗床） |
| solid_panel_boards | forked_anchor | S7 | L62-80, L213-226 | eligible if compatible | 头尾各 2 立柱 + 实心 molded rounded-rect 面板（ExtrudeGeometry+rounded_rect_profile） |

`open_no_board` 是"缺席该结构层"的合法候选（源 S2 就是无板诊疗床），非单件退化——三选一的宏观表面选择。

### Slot D：side safety rails（可选 REVOLUTE 子件对）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| none | forked_anchor | S1/S2 | parents have no side rails | eligible if compatible | 无护栏 |
| dropdown_side_rails | forked_anchor | S5 | L334-400 | eligible if compatible | 左右各一 REVOLUTE 落式全长护栏（guard/mid/pivot 三横管 + 立柱 + latch），绕床侧 x 轴落下 |

Slot D 仅 2 candidate：源池对侧护栏结构只有有/无两态（S5 是唯一护栏 fork，parents 均无）。
2 候选清 per-slot-key gate；不强凑第三种以免发明无源结构。

## 槽位图（slot graph）

pattern: mixed

```
[Slot B base] --root(floor)-->
   caster_base / four_leg_couch: root == deck_part == base_frame
   hi_lo_column: base --PRISMATIC z [0,0.30]--> lift_column == deck_part

deck_part --shared _deck_frame(underframe + hip deck + mattress + hinge barrels)-->
   [Slot A] backrest --REVOLUTE +Y @(-0.333,0,0.62)[0,1.15]--> child of deck_part
            (N>=2) knee/thigh --REVOLUTE -Y @(foot_hinge_x,0,0.62)[0,0.70]--> child of deck_part
            (N=3)  calf --REVOLUTE +Y @(thigh_len,0,0) local [-0.30,0.80]--> child of thigh
   [Slot C] head/foot boards --> deck_part VISUALS (Rule 1, 不动)
   [Slot D] side_rail_left/right --REVOLUTE +-X @(0,+-0.49,0.59)[0,1.57]--> child of deck_part
```

- 跨 slot 连接点位：
  - base->deck（hi_lo）：PRISMATIC 轴 z，origin 世界原点，inner_column 嵌进 outer_column（captured slide，allow_overlap）。
  - deck->backrest/knee/thigh：REVOLUTE 铰，origin 在 deck hinge_barrel 硬件所在 hinge 线 `(hinge_x,0,deck_top_z)`，barrel(y=+-0.49) 与 child hinge_tube(y<=+-0.43) 侧向相邻不重叠（captured-pin，grandfather）。
  - thigh->calf：REVOLUTE，origin 在 thigh 远端 barrel 局部 `(thigh_len,0,0)`。
  - deck->side_rail：REVOLUTE 绕床侧 x 轴，pivot latch bracket 与 deck side_rail 局部搭接（captured pivot，allow_overlap）。
- Slot A backrest 恒存在；knee/thigh/calf 由 N 派生。Slot C boards 与 Slot D rails 可选。
- 所有非-root part 挂 deck_part（hi_lo 时 = lift_column，随升降柱一起抬升）。

## 每槽位 Module Emits / Interfaces

### Slot B / caster_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `base_frame`(==deck_part) | S1 L131 |
| visuals | 4 角腿柱(caster顶->deck) + 4 折入 swivel caster(tire/stem/swivel/fork_bridge/2 fork/axle/hub) | S1 L201-271 |
| internal joints | 无（casters 是 visual，Rule 1） | S1 |
| downstream interface | deck_part = base_frame | — |

### Slot B / four_leg_couch
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `base_frame`(==deck_part) | S2 L140 |
| visuals | 4 条内收方腿(x=+-0.80,y=+-0.47)->地 + 脚垫 box | S2 L150-151 |
| downstream interface | deck_part = base_frame | — |

### Slot B / hi_lo_column
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `base`(十字臂+hub_plate+outer_column+4 caster) + `lift_column`(==deck_part, inner_column+carriage_plate) | S6 L188-260 |
| internal joints | `column_to_deck` PRISMATIC z [0,0.30] base->lift_column | S6 L377-385 |
| downstream interface | deck_part = lift_column | — |

### shared `_deck_frame`（挂 deck_part，所有 base 共用）
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 上/下 side rail(y=+-0.47)、cross rails、固定 hip deck 板 + hip mattress（长度随 N 到 foot 侧 hinge）、backrest hinge barrel 对、(N>=2) foot 侧 hinge barrel 对 | S1 L133-199/L273-284, S3 L300-324 |

### Slot A / single_backrest · two_section_gatch · three_section_profiling
| emits | 描述 | 来源 |
|---|---|---|
| parts | `backrest`(恒)；N=2 加 `knee_section`；N=3 加 `thigh_section`+`calf_section` | S1 L286 / S3 L376 / S4 L426,L483 |
| visuals/段 | deck 板(Box) + mattress(mesh) + hinge tube/side tubes/leaves | S3 L327-363 |
| internal joints | `deck_to_backrest` REVOLUTE +Y [0,1.15]；`deck_to_knee`/`deck_to_thigh` REVOLUTE -Y [0,0.70]；`thigh_to_calf` REVOLUTE +Y [-0.30,0.80] | S3 L365-425, S4 L529-560 |
| upstream interface | 铰 origin 在 deck hinge 线 barrel 上；child hinge_tube 内含局部原点 | S3 |

### Slot C / boards（deck_part visuals）
| emits | 描述 | 来源 |
|---|---|---|
| tubular | 头尾各 2 立柱(x=+-0.95, deck->1.16) + 3 横管 | S1 L177-199 |
| panel | 头尾各 2 立柱 + molded rounded-rect 面板 | S7 L213-226 |
| open | 无 | S2 |

### Slot D / dropdown_side_rails
| emits | 描述 | 来源 |
|---|---|---|
| parts | `side_rail_left` / `side_rail_right` | S5 L348 |
| visuals | guard_bar/mid_bar/pivot_tube 三横管 + 立柱 + pivot latch bracket | S5 L351-390 |
| internal joints | `deck_to_side_rail_{side}` REVOLUTE 绕 +-X [0,1.57] | S5 L392-400 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| base | enum | caster_base / four_leg_couch / hi_lo_column | — | choice | rng.choice；无 gating（全互容） | Slot B |
| deck_sections (N) | enum(mult) | n1 / n2 / n3 | — | choice | rng.choices weights (0.45,0.30,0.25) | Slot A |
| boards | enum | tubular_rail_boards / open_no_board / solid_panel_boards | — | choice | rng.choice | Slot C |
| side_rails | enum | none / dropdown_side_rails | — | choice | rng.choice weights (0.5,0.5) | Slot D |
| palette_style | enum | white_blue / grey_green / beige_cream / chrome_teal / white_burgundy | white_blue | choice | rng.choice(PALETTE_STYLES)；仅涂装，不进 slot_choices | 8.5 6 |
| mattress_thickness_scale | float | [0.90, 1.15] | 1.0 | independent | 仅缩放 cushion z 厚度（顶面）；不改接口 | S1 cushions |
| backrest_range_scale | float | [0.80, 1.00] | 1.0 | independent | 乘 backrest/section upper 上界（只减不增，<= 已验证安全上界） | S1 L331 |
| (—) | constraint | — | — | inequality | 段抬升上界 x scale <= 已验证 clearance 安全值（1.15/0.70/0.80）；护栏在 Y 外侧恒 clear | clearance 分析 |

连续尺寸采样契约：先采两个 independent scale（均匀），无 equation/conditional 依赖；inequality 由 scale<=1 且标称上界已 clearance-safe 静态满足，无需回缩。

### 7.5 编译预算 / compile budget
每-seed 预算 **<= 18s**（依据：源 S1/S3/S4 单记录编译均 <10s；本模板每 seed 至多 ~5 个
`superellipse_side_loft` cushion mesh（segments=64）+ 1-2 个 molded panel Extrude + 若干
Cylinder/Box 原语 caster 子件）。分档：cushion loft 64 段，caster 小圆柱用 Cylinder 原语，
molded panel corner_segments=8。N 段复用同一 `_rounded_cushion_mesh` helper。超预算先降
loft segments 至 48 再迭代。sweep `--compile-timeout 120`（约 3x 预算 watchdog）。

## Multiplicity / Copy Logic

两根复制轴：

- **deck_sections (Slot A 的 N)**
  - count_param `section_count` / N_range 产品域 {1,2,3}（离散）；sampling domain 权重档 (n1 0.45, n2 0.30, n3 0.25)，小 N 偏多。
  - copied object：hinged deck section（deck Box + mattress mesh + hinge tube/leaves）。naming：`backrest`(恒) / `knee_section`(N=2) / `thigh_section`+`calf_section`(N=3)。
  - placement：backrest 在 head 侧 hinge(-0.333)；foot 侧段在 foot_hinge_x（N=2:0.30；N=3:thigh 0.10 + calf 链于 thigh 远端）。
  - joint policy：backrest/knee/thigh 各 REVOLUTE off deck_part；calf REVOLUTE chained off thigh。
  - source/gating：S1(N=1)/S3(N=2)/S4(N=3)；N 与任何 base/boards/rails 全互容。

- **casters (=4)**
  - count_param 固定 4（四角）。N_range {4}，非采样轴。copied object：swivel caster 子装配。naming `caster_{i}` / `caster_{i}_*`。placement：caster_base 四角(+-0.95,+-0.47)；hi_lo 十字臂端。joint policy：折入 root part 的 visual（Rule 1）。source S1 L201-271 / S6 L92-141。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| 1 骨架图 | 加/减会动的 part/边 | 有 | Slot A backrest(1)/+knee(2)/+thigh+calf(3) part-joint 图变化；Slot B hi_lo 多一条 PRISMATIC 轴 + lift_column part；Slot D 加/减一对 revolute 护栏 part。forked_anchor S1/S2/S3/S4/S5/S6 |
| └ multiplicity | 同构件 xN | 有 | 见 8：deck_sections N{1,2,3} 权重 (0.45,0.30,0.25)；casters x4 固定 |
| 2 关节类型 | 换 type/轴 | 有 | REVOLUTE（backrest +Y、knee/thigh -Y、calf +Y、side rail +-X）+ PRISMATIC（hi_lo 升降 z）+ FIXED（无：不动件均 visual）。每种在 sweep 中随组合出现。forked_anchor S1/S4/S5/S6 |
| 3 主体形态家族 | 换核心 part 可识别几何原型 | 有 | Slot C 头尾板 = 3 主形态 slot：tubular_rail_boards(form_subtype=Planar Boundary Form,开放管框) / open_no_board(无板开放面) / solid_panel_boards(form_subtype=Planar Boundary Form,实心 molded 面板)；Slot B 底座形态（滚轮四角/内收刚腿/中央升降柱）亦为可识别宏观形态。全部 source-backed（S1/S2/S7 + S1/S2/S6），登记进 slot_choices（boards、base）。 |
| 4 表面装饰 | 叠加表面细节 | 有(轻) | mattress 顶面 crowned（`_rounded_cushion_mesh` softness/edge_taper 由宿主逐-z 派生）、pivot latch 小板、caster hub 亮环。record_only（S1/S5）。无自由装饰计数轴——医疗床表面本征素净。 |
| 5 尺寸/行程 | 只改连续尺寸/行程 | 有 | deck ~1.9x0.86 m、mattress_thickness_scale[0.90,1.15]、backrest_range_scale[0.80,1.00]。运动包络：backrest +Y[0,1.15]（抬头，head 端上抬内摆离头板）；knee/thigh -Y[0,0.70]（foot 端上抬）；calf +Y local[-0.30,0.80]（foot 端相对下垂）；side rail +-X[0,1.57]（护栏落至床侧下方，Y 恒在垫外侧）；hi_lo PRISMATIC z[0,0.30]（整床抬升，保留柱插入深度）。motion_test_plan：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)`；per-机构 targeted `ctx.pose`：backrest 抬 pillow 上、knee/thigh 抬 foot 上、calf 落 foot 下、prismatic 抬 deck 上、side rail guard 下。全程不穿模。 |
| 6 涂装 | 只改材质/颜色 | 有 | 5 colorway（white_blue/grey_green/beige_cream/chrome_teal/white_burgundy），材质大类 painted-steel + fabric(mattress) + rubber(tire) + metal(caster/hub) + plastic(panel)；覆盖 >= ceil(0.5x5)=3。record_only(S1/S6/S7) + 世界知识配色。 |

收尾自检：`template batch` 0-9 seed 需肉眼可见 3 种 board 形态 + 3 种 base + N 段抬升 + 护栏有无 + palette 变化，且抬升/落栏全程不穿模。

## 拓扑多样性审计

总组合数：base(3) x N(3) x boards(3) x side_rails(2) = **54** 纯 slot 拓扑（>= 多样性地板 10）。

理由：4 个 slot key 每个 >=2（base3/deck_sections3/boards3/side_rails2）且全互容，36-seed 采样几乎必然逐 key 覆盖 >=2。

seed_domain_policy：procedural_first（config_from_seed 对每 seed 用 random.Random(seed) 独立采样 4 slot enum + palette + 2 scale；seed=0 不特殊）。
Procedural Sampling / Sweep Plan：4 slot 各自加权 rng 抽取；无非法组合，无 gating/override。初版即以此为主 seed domain；无 curated/modulo 表。random sweep 0-35 初验 + corner stage 探未实现极值/组合；viewer 目检 ~10 seed。
Topology target：1000-seed slot choice tuple distinct 预计连同 palette/scale 按 ≥300 富类别口径观察。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
Controlled local parameterization：mattress_thickness_scale[0.90,1.15]、backrest_range_scale[0.80,1.00]，均 independent 且在 resolve_config clamp；不触 InterfaceSpec/接触面/multiplicity/joint origin/identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 4 slot 加权 rng.choice + 2 clamp scale；顺序 base->N->boards->rails | slot_choices_for_seed == build 选择 |
| compatibility matrix | 全互容，无互斥/fallback | 无 floating/穿模/轴/max-mult/bulky/optional-child 失败 |
| controlled local variation | 2 个 independent scale，clamp | 比例微变不破接口/clearance/support/joint origin/identity |
| regression overrides | none | — |
| random sweep | 0-15 -> 0-35 -> corner；1000 用于成熟审计 | 契约失败；axis_realization / report |

| slot | candidate_count | 是否 >=2 | 是否 >=3 | 备注 |
|---|---:|---|---|---|
| B base | 3 | yes | yes | |
| A deck_sections | 3 | yes | yes | multiplicity N |
| C boards | 3 | yes | yes | 3 主形态 |
| D side_rails | 2 | yes | no | 源池仅有/无两态 |

## Validator

- slot_choices_for_seed returns implemented module names (base / nN / boards / side_rails)
- config_from_seed uses deterministic procedural sampling for all ordinary seeds (incl. seed 0)
- compatibility matrix：全互容，无非法组合
- optional regression overrides：none
- controlled scales clamped in resolve_config；不破接口/clearance/joint origin/multiplicity
- key joints have expected type/axis/range：deck_to_backrest REVOLUTE axis Y；hi_lo column_to_deck PRISMATIC axis Z；side rails REVOLUTE +-X
- casters：每 base 4 个 caster 子装配，folded visuals（Rule 1）
- copied objects follow naming/placement policy（caster_{i}、section 命名、side_rail_{side}）
- Rule 5：`fail_if_parts_overlap_in_sampled_poses` + per-机构 targeted `ctx.pose`

## Reject cases

- 抬背/抬膝在 upper 上界撞头/尾板（-> 上界已 clearance-safe，段向内上摆离板；scale 只减）
- 落式护栏在某角度撞睡卧面/段（-> 护栏 pivot 在 y=+-0.49，全程在 mattress(+-0.41) 外侧）
- hi_lo 抬升后 inner_column 脱出 outer_column（-> 保留插入深度 >=0.10，源 S6 已验证）
- board 立柱悬空（-> 立柱底嵌进 deck side_rail，deck_part 内连通）
- caster 子件互相断开成 island（-> 同一 root part 内共 hub/axle 接触）
- 段 mattress 在 rest 位互穿（-> mattress 从 hinge 线内缩 length-0.04，rest 留小缝）

## 与相邻类别的边界

- 不该混入：普通床 / 床头柜（无 REVOLUTE articulating 段、无医疗底座/护栏/升降）。
- 不该混入：担架 / 推车（纯平板可滚动，无抬背铰接段）。
- 不该混入：surgical_chair（坐姿连续坐盘 + 环抱背）；surgical_bed（OR 台有 trendelenburg 整台倾斜 DOF + 柱式基座，本类以护理/诊疗床为主，无整台倾斜）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | spec 直接进入模板实现（连续，无停点）。所有候选均有真实 model.py:Lx-Ly；无单候选 slot（Slot D 2 候选已说明源池限制）。 |

## 模板实现备注（可选）

- 共享 helper：`_rounded_cushion_mesh`(S1 L59)、`_cylinder_x/y/z`(S1 L32-56)、`_add_caster`、`_deck_frame`、`_molded_panel_mesh`(S7 L62)。
- 铰接均为 captured-pin（barrel+tube 侧向相邻）-> 省略 mating= 依 AUTHORING Rule 2 grandfather（与 primary 参考 Science_Surgical_bed 一致），origin 落在 deck hinge_barrel 硬件上，element-scoped allow_overlap 处理局部搭接。
- PRISMATIC lift：origin 为 gauge freedom（exempt）；allow_overlap(inner_column, outer_column) captured slide。
- palette 经 mats[...] dict 驱动每个 .visual(material=...)，key：frame/deck/fabric/rubber/metal/hub/column/panel。
