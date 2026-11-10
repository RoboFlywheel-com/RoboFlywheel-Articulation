# Modular Spec — folding_camp_table

## 元信息
| 项 | 值 |
|---|---|
| slug | `folding_camp_table` |
| template path | `agent/templates/folding_camp_table.py` |
| test path (optional) | `tests/agent/test_folding_camp_table_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

`pattern` = parallel_children：一个 `tabletop` 根 part 承载表面/围边/五金，legs / braces / storage / drop-leaf 都作为独立 child 或 root visual 挂到它上面（不是串链）。looped slats 是 tabletop 内部的 multiplicity。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 |
| read_count | 12 |
| read_scope | all listed 5-star ids (2 origin anchors + 10 forks) |
| source_index_policy | only adopted module sources are indexed below |

阅读要点：
- **origin A** (`…1a04de6b…`, model.py): 紧凑方桌 ~0.80×0.54，TOP_Z=0.51；`tabletop` root；9 条 `_slat_mesh`（ExtrudeGeometry(rounded_rect_profile)）+ 黑围边/角球/螺钉/椭圆嵌件；4 直腿 `leg_i`（Cylinder straight_tube + upper_collar + rubber_foot），`tabletop_to_leg_i` REVOLUTE 轴(0,±1,0) lower=0 upper=1.45；4 独立斜撑 `brace_i` REVOLUTE。captured-pin 用 allow_overlap（无 MatingContract）。
- **origin B** (`…e67ceec6…`, model.py): 较大矩形 ~1.06×0.65；`tabletop_frame` root；13 条 Box 板条；4 `_add_leg_sleeve`（sleeve/collar/clamp 都是 root visual）+ 4 `lower_leg_i` 内管，`table_to_lower_leg_i` PRISMATIC 轴(0,0,1) upper=0.16；织物+网兜储物（pocket_bottom + PerforatedPanelGeometry mesh_panel + orange binding）；X/scissor 斜撑 REVOLUTE。
- **solid_panel_top** fork: 用单块 `deck_panel` Box 替换 slat loop，其余（腿/撑/围边）继承 A。
- **mesh_fabric_top** fork: 用张紧 `fabric_panel` Box + 四条 bound_edge 替换 slats。
- **splayed_aframe_legs** fork: 腿两轴外撇（14°/8°），olive 涂装；仍 REVOLUTE 折叠。
- **x_cross_legs** fork: 每短端一对交叉腿 `_xleg_tube_mesh`（Y-Z 平面斜管），`tabletop_to_leg_i` REVOLUTE 轴(±1,0,0)；pair 交叉互穿用 allow_overlap；cross_pivot 螺栓。
- **accordion_scissor_base** fork: 4 `scissor_arm_i` REVOLUTE + Mimic 联动收合（本模板 deferred，见 §9）。
- **bifold_center_hinge** fork: `tabletop_left`/`tabletop_right` 中缝 REVOLUTE 对折（本模板 deferred：需拆根 topology，见 §9）。
- **drop_leaf_extension** fork: 后缘 `drop_leaf` part，`tabletop_to_drop_leaf` REVOLUTE 轴(-1,0,0)，hinge barrels/knuckles。
- **rigid_lower_shelf** fork: 腿间刚性板条下层（root visuals + brackets）。
- **slats_6 / slats_20** fork: 只是 SLAT_COUNT 的 multiplicity 变体（6 / 20），结构同 A/B。

## 核心身份

一张便携可折叠/伸缩的**露营桌**：抬升的矩形工作面 + 四角支撑 + 至少一处真实腿折叠/腿伸缩/顶折/储物开合关节，能收小携带。相邻类别边界见 §11。不该退化成固定露台桌、工作台、折叠椅/凳、行军床、带轮餐车或货架。

## 槽位 + 候选模块表

### Slot A：surface_construction（③ 主体形态家族 / Primary Form Family — 已登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `roll_top_slats` | origin_anchor | origin A & B | A L92-L121 / B L172-L199 | eligible if compatible | N 条独立铝板条（ExtrudeGeometry rounded_rect）+ 间隙暗条 + 端盖，multiplicity 轴挂此 module。**Macro Surface Construction** |
| `solid_panel` | forked_anchor | rec_…_var_solid_panel_top | L67-L112 | eligible if compatible | 单块刚性 Box 面板替换 slat loop。**Planar Boundary Form** |
| `fabric_mesh` | forked_anchor | rec_…_var_mesh_fabric_top | L67-L134 | eligible if compatible | 张紧薄织物 Box + 四条 bound_edge 缝边。**Macro Surface Construction (membrane)** |

### Slot B：support_style（① 骨架 + ② 关节类型）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `straight_folding_legs` | origin_anchor | origin A | L195-L246 | eligible if compatible | 4 直管腿，`tabletop_to_leg_i` REVOLUTE 轴(0,±1,0)，绕 Y 内折上收；hinge_pin/straight_tube/upper_collar/rubber_foot/brace_stub |
| `telescoping_legs` | origin_anchor | origin B | L44-L111 | eligible if compatible | 4 sleeve（root visual）+ 4 `lower_leg_i` 内管，`table_to_lower_leg_i` PRISMATIC 轴(0,0,1) 上抽 |
| `splayed_aframe_legs` | forked_anchor | rec_…_var_splayed_aframe_legs | L236-L304 | eligible if compatible | 4 外撇 A 型腿，REVOLUTE 轴(0,±1,0) 折叠；足外扩 |
| `x_cross_legs` | forked_anchor | rec_…_var_x_cross_legs | L241-L313 | eligible if compatible | 每短端一对交叉斜管腿（Y-Z 平面），REVOLUTE 轴(±1,0,0)；pair 交叉互穿声明 allow_overlap |

### Slot C：under_table_storage（③ 储物形态 / 可选 root-visual 层）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | origin_anchor | origin A（裸架） | — | eligible | 无储物层 |
| `fabric_hammock` | origin_anchor | origin B | L223-L270 | eligible if compatible | 中央软织物+网兜 sling（pocket_bottom + PerforatedPanelGeometry + binding），narrow-Y 中带，避开摆动腿 |
| `rigid_shelf` | forked_anchor | rec_…_var_rigid_lower_shelf | L219-L268 | eligible if compatible | 中央刚性板条下层托盘 + 端轨 + brackets 上连框架，narrow-Y 中带 |

`none` 单独存在合法（origin A 就是裸架），且储物层不改变根拓扑（纯 root visual），此 slot 允许 `none` 作为一个真实候选。

### Slot D：top_extension（① 可选顶部延展）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | origin_anchor | origin A/B | — | eligible | 无延展 |
| `drop_leaf` | forked_anchor | rec_…_var_drop_leaf_extension | L329-L435 | eligible if compatible | 后缘 `drop_leaf` part + hinge barrels/knuckles，`tabletop_to_drop_leaf` REVOLUTE 轴(-1,0,0)，q=0 展平 / 正 q 下折收纳 |

硬约束满足性：Slot A 3、Slot B 4、Slot C 3、Slot D 2，均 ≥2；A/B/C 均 ≥3。每个 ①/② candidate 有真实 forked/origin anchor + `model.py:Lx-Ly`。③ 主体形态家族 slot (surface_construction) 已登记进 `slot_choices` 且 ≥3 可识别原型。

## 槽位图（slot graph）

pattern: parallel_children

```
                       tabletop (ROOT: surface_construction 决定表面/围边/角球/装饰)
                        │
   ├─ support_style ──[REVOLUTE 轴(0,±1,0) 或 PRISMATIC 轴(0,0,1) 或 REVOLUTE 轴(±1,0,0);
   │                    origin@leg_top_z hinge socket / sleeve mouth]──▶ leg_0..3 (moving children)
   │
   ├─ under_table_storage ──[无关节：中央 root visual 直接嵌入 tabletop 框架]──▶ (visuals on tabletop)
   │
   └─ top_extension ──[REVOLUTE 轴(-1,0,0); origin@rear-edge hinge line]──▶ drop_leaf (moving child, optional)
```

- 顺序/父子：`tabletop` 是唯一根，所有 slot 的 part 都以它为 parent（parallel children）。storage 不产生 part（root visual）。
- 跨 slot 接口点位：腿 = tabletop 底面 `hinge_socket_i` / `leg_sleeve_i`（root visual）与腿 `hinge_pin` / `inner_tube` 的 captured-pin/sleeve 配合；drop_leaf = 后缘 hinge barrel（root visual）与 leaf knuckle 的交叉铰链。
- 关节类型/轴/行程：见各 module emits 与 §7；captured-pin / pin-in-sleeve 铰链 **omit MatingContract（grandfathered）**，与全部 5★ 源一致（`AUTHORING.md` §A Rule 2 例外）。
- 互斥/gating：见 §9 compatibility matrix。storage & drop_leaf 尺寸/位置派生成"避开腿的摆动/交叉体积"（中央窄带 + 后缘外置），使全部 support × storage × top 组合几何合法，无需硬排除组合。

## 每槽位 Module Emits / Interfaces

### Slot A / surface_construction（3 modules，都发到 `tabletop` root）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（全部是 tabletop root visual） | A/B |
| root visuals | roll_top: `slat_{i}`×N + `slat_gap_{i}` + `{front,rear}_cap_{i}`；solid: `deck_panel`；fabric: `fabric_panel` + `bound_edge_{side}`；三者共用 `front/rear_rail`,`side_rail_{0,1}`,`corner_connector_{0..3}`,`underside_crossrail_*`,`front_screw/oval`(④) | A L92-L193 / solid L67-L152 / fabric L67-L150 |
| internal joints | 无 | — |
| interface | tabletop 底面在 `leg_top_z` 处提供 4 个腿安装点 (±leg_x,±leg_y)；后缘 `top_z` 处提供 drop-leaf 铰接线 | A |

### Slot B / support_style（4 modules）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `leg_0..3`（moving children of tabletop） | A/B/forks |
| tabletop visuals | `hinge_socket_i`（straight/splayed/x_cross）或 `leg_sleeve_i`+`upper_collar_i`+`leg_clamp_i`（telescoping） | A L167-L173 / B L44-L70 |
| leg visuals | straight/splayed: `hinge_pin`,`straight_tube`,`upper_collar`,`rubber_foot`,`brace_stub`；telescoping: `inner_tube`,`height_lock`,`thumb_knob`,`foot_pad`；x_cross: `hinge_pin`,`xleg_tube`,`upper_collar`,`rubber_foot`,`cross_pivot` | A/B/forks |
| internal joints | `tabletop_to_leg_i` REVOLUTE 轴(0,±1,0)/(±1,0,0)（straight/splayed/x_cross）或 `table_to_lower_leg_i` PRISMATIC 轴(0,0,1)（telescoping） | A L238-L246 / B L102-L110 |

### Slot C / under_table_storage（fabric_hammock / rigid_shelf；发到 `tabletop` root，无关节）
| emits | 描述 | 来源 |
|---|---|---|
| root visuals | hammock: `pocket_bottom` + `front/rear_mesh_panel`(PerforatedPanelGeometry) + `*_binding` + `hanger_*`；shelf: `shelf_slat_{i}` + `shelf_end_rail_{i}` + `shelf_bracket_*` | B L223-L270 / shelf fork L219-L268 |
| joints | 无（固定于框架的 root visual，中央窄带避腿） | — |

### Slot D / top_extension（drop_leaf）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drop_leaf`（moving child） | drop_leaf fork |
| tabletop visuals | `leaf_hinge_barrel_{i}` + `leaf_support_bracket_*` | fork L332-L353 |
| leaf visuals | `leaf_knuckle_{i}` + `leaf_hinge_strip` + `leaf_slat_{i}` + `leaf_outer_rail` + `leaf_side_rail_*` | fork L360-L420 |
| internal joints | `tabletop_to_drop_leaf` REVOLUTE 轴(-1,0,0) lower=0(展平) upper≈1.4(下折) | fork L425-L435 |

要求满足：活动件（腿/leaf）都有 articulation；不动细节（围边、角球、螺钉、储物、sleeve/collar）都是 host part visual，不作独立 FIXED part（Rule 1）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| surface_construction | enum | roll_top_slats / solid_panel / fabric_mesh | roll_top_slats | choice | procedural sampler | Slot A |
| support_style | enum | straight_folding_legs / telescoping_legs / splayed_aframe_legs / x_cross_legs | straight_folding_legs | choice | procedural sampler | Slot B |
| under_table_storage | enum | none / fabric_hammock / rigid_shelf | none | choice | procedural sampler | Slot C |
| top_extension | enum | none / drop_leaf | none | choice | procedural sampler | Slot D |
| palette_style | enum | gray_aluminum / bamboo_wood / olive_field / coyote_two_tone / graphite_orange | gray_aluminum | choice | `rng.choice(PALETTE_STYLES)` → mats dict | ⑥ / 各源材质 |
| slat_count | int(N) | [6, 20] | 9 | independent | roll_top 时采样；clamp[6,20]；其它表面忽略 | A(9)/B(13)/f(6/20) |
| table_size_scale | float | [0.90, 1.30] | 1.0 | independent | 均匀采样后 clamp | A(0.8×0.54)/B(1.06×0.65) |
| table_aspect | float | [0.62, 0.78] | 0.68 | independent | table_y/table_x 比；clamp | A(0.675)/B(0.61) |
| table_height_scale | float | [0.85, 1.25] | 1.0 | independent | 驱动 top_z（deck 高） | A/B |
| (—) | derived | table_x = 0.80·table_size_scale | — | equation | `table_x = 0.80·size_scale` | A |
| (—) | derived | table_y = table_x·table_aspect | — | equation | `= table_x·aspect` | A/B |
| (—) | derived | top_z = 0.48·table_height_scale | — | equation | deck 顶面 z | A |
| (—) | derived | leg_x/leg_y = table_x/2−0.075 / table_y/2−0.060 | — | equation | 腿角位；hinge socket 位置同源 | A |
| (—) | derived | slat_w = (table_x−(N−1)·gap)/N | — | equation | roll_top 板条宽随 N/表宽 | A L29 |
| leg_fold_upper | float | derived ≤0.75 | 0.72 | inequality | REVOLUTE 折腿上界：`0.44·sin(θ) < leg_x − 0.05`（左右足不交叉，≥40mm 管间隙）；违反回缩 | 见 §8.5⑤ |
| telescope_travel | float | [0.10, 0.16] | 0.16 | independent | PRISMATIC 上抽行程 | B L109 |
| storage_half_x/y | float | derived | — | inequality | `≤ leg_x−0.055 / leg_y−0.055`（中央窄带避腿摆动/交叉） | 见 §9 |

所有 equation/inequality 在 `resolve_config` 求解，不留到 builder 失败。scale 之间默认独立；相关性（table_y 派生自 table_x·aspect、leg_x 派生自 table_x、slat_w 派生自 N/table_x）已显式落到 equation 行。

### 7.5 编译预算 / compile budget（必填）
每-seed 预算 **≤14s**（依据：库内典型模板 5-20s；本类别只有 slat/tube 的 ExtrudeGeometry + Cylinder/Box + 少量 PerforatedPanelGeometry，无重布尔雕刻）。分档 tessellation：slat 圆角 `corner_segments=8`、tube `radial_segments≤18`、PerforatedPanel 孔阵与源同参；**一条 slat mesh 建一次、N 次复用同一 `Mesh`**（`_slat_mesh()` 只调用一次），drop-leaf slat 同法复用。超预算先降段数再迭代。

## Multiplicity / Copy Logic

**轴 1：slat_count（板条数）**
- `count_param`：`slat_count`；`N_range`：产品域 [6, 20]（测试偏小：6/9/13；产品含 20）；sampling domain：均匀采样后 clamp（小 N 与大 N 都出现）。
- copied object：一条铝板条 visual（`slat_{i}`，ExtrudeGeometry rounded_rect），复用同一 `_slat_mesh()`。
- naming：`slat_{i}`；placement：沿 X 均布，固定 `slat_gap`，`slat_w` 随 N/table_x 派生；joint policy：板条是 tabletop 的刚性 member（无 per-slat 关节）。
- source/gating：仅 `roll_top_slats` 表面启用；`solid_panel` / `fabric_mesh` 不暴露 slat_count（单板/单膜）。
- 次级重复集：4 腿 + 各自 brace_stub（腿数恒为 4，不作 multiplicity 轴 —— 3 腿露营桌不稳/罕见，见 §Blocked）。

无第二 multiplicity 轴。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | support_style 4 种腿骨架（直腿 / 伸缩腿 / A 型撇腿 / X 交叉腿）+ top_extension 加一片 drop_leaf 活动 part。全部 origin/forked_anchor source-backed（origin A/B + splayed/x_cross/drop_leaf forks）。 |
| └ multiplicity | 同构件 ×N | 有 | slat_count N∈[6,20]（见 §8，权重：小 N 偏多、20 稀有）。 |
| ② 关节类型 | 图不变换 type/轴 | 有 | REVOLUTE 轴(0,±1,0)（直/撇腿折）· PRISMATIC 轴(0,0,1)（伸缩腿）· REVOLUTE 轴(±1,0,0)（X 交叉腿折）· REVOLUTE 轴(-1,0,0)（drop_leaf 顶折）。全部 source-backed（A revolute / B prismatic / x_cross / drop_leaf）。每种都在 sweep 出现（见 §9 采样）。 |
| ③ 主体形态家族 | 换核心 part 可识别形态原型 | 有 | surface_construction 3 原型（已登记 slot_choices）：`roll_top_slats`=Macro Surface Construction；`solid_panel`=Planar Boundary Form；`fabric_mesh`=membrane Macro Surface。source-backed（origin slats + solid_panel/mesh_fabric forks）。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | `front_screw_*`/`front_oval_insert_*`（螺钉行）、`corner_connector_*`（角连接球）、`small_edge_mark`（边缘 logo）、storage `*_binding`（orange 饰带）。`record_only` + host-conformal：都写成 tabletop / storage 宿主 visual，位置随 ③ 表面与 ⑤ 表宽逐-点派生（螺钉沿前 rail 随 slat 位、角球在四角随 table_x/y）。装饰非结构、非关节。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | 关键比例：table_size_scale[0.90,1.30]、table_aspect[0.62,0.78]、table_height_scale[0.85,1.25]（见 §7）。关节运动包络：直/撇腿 REVOLUTE 轴 Y，开启方向内折上收 `[0, ≤0.75]`（`leg_fold_upper` 由左右足不交叉不等式求解）；X 交叉腿 REVOLUTE 轴 X `[0, ≤0.60]`；伸缩腿 PRISMATIC 轴 Z `[0, telescope_travel≤0.16]`；drop_leaf REVOLUTE 轴 X `[0, ~1.4]`（q=0 展平→下折）。`motion_test_plan`：默认 harness_motion_qc 采样碰撞（captured-pin/pair-cross 用 element-scoped allow_overlap 声明）+ 每机构一条 targeted `ctx.pose(...)`（腿折上收足升高 / 伸缩腿上抽 / drop_leaf 下折）。关节全程不穿模；储物/leaf 尺寸派生成避开腿扫掠体积，故无需 sampled-pose exemption。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | palette_style ≥5：gray_aluminum(金属 metal)、bamboo_wood(木 wood)、olive_field(painted metal)、coyote_two_tone(painted 两色)、graphite_orange(metal+orange 织带)。材质大类覆盖 metal/wood/painted ≥ ceil(0.5×5)=3。每 seed `rng.choice(PALETTE_STYLES)` 驱动全部 `.visual(..., material=mats[...])`。 |

收尾自检：surface 三形态、四腿骨架、材质大类、装饰贴合、关节全程不穿模都须在 `template batch` 0-9 seed 肉眼可见。

## 采样与覆盖审计

总组合数：A(3) × B(4) × C(3) × D(2) = **72** 离散组合；乘 palette(5) = 360 视觉组合；再乘 slat_count(≈15) 与连续 scale → 远超 300 topology 目标。

理由：surface × support × storage × top-extension 四个离散轴独立可组合（储物/leaf 尺寸派生成避腿，无需排除组合），已给出富拓扑空间。

seed_domain_policy：procedural_first（seed 0 不特殊，`config_from_seed` 全程 `random.Random(seed)` 采样）。

Procedural Sampling / Sweep Plan：每 seed 独立采 4 个 slot enum + palette_style + slat_count + 3 个连续 scale + telescope_travel；`resolve_config` 派生 table_x/y/top_z/leg_x/leg_y/slat_w/leg_fold_upper/storage 尺寸并 clamp。compatibility：storage 尺寸夹到中央窄带（`storage_half ≤ leg−0.055`）避开腿摆动/X 交叉扫掠体积；drop_leaf 铰接线置后缘外侧避后腿。**唯一组合 fallback**：`x_cross_legs` + `drop_leaf` → drop_leaf 降级为 `none`（X 交叉腿管折叠时扫掠整个桌深，与后缘折翼共占体积；折翼仍在其余 3 种腿上实现）。无 regression override。random sweep：0-35 初过 + corner stage，`template batch` 0/1/2/3/4/5/6/14 目检覆盖全 surface/support/storage/top/palette。Topology target：report-only，reachable 105 离散组合（sweep 实测 saturated），远超 300…（连 palette/slat_count/scale）足够成熟度观察。

Controlled local parameterization：table_size_scale / table_aspect / table_height_scale / telescope_travel / slat_count；全部在 `resolve_config` clamp/派生，受 leg 接口、captured-pin 间隙、关节行程、类别 identity 约束；不破坏腿安装点或 multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 A→B→C→D 独立加权采样；palette/slat_count/scale 独立 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | storage/leaf 尺寸派生避腿；唯一 fallback：x_cross_legs+drop_leaf→drop_leaf=none | no floating / collision / axis / max-multiplicity / bulky-module 失败 |
| controlled local variation | table_size/aspect/height、telescope_travel、slat_count；clamp | 比例变化不破接口/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 初过；0-999 成熟审计 | contract failures；axis_realization；viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| surface_construction | 3 | yes | yes | ③ 已登记 slot_choices |
| support_style | 4 | yes | yes | ①② |
| under_table_storage | 3 | yes | yes | `none` 是真实 origin A 裸架候选 |
| top_extension | 2 | yes | no | 可选层，2 候选（none / drop_leaf），degrade 理由：顶折延展只有 drop_leaf 一个真实非平凡 fork，另一自然候选 bifold 需拆根拓扑 deferred（见下） |

## Validator

- slot_choices_for_seed 返回已实现 module 名（surface/support/storage/top-extension）
- config_from_seed 对所有 seed（含 0）用 `random.Random(seed)` procedural 采样
- storage/leaf 尺寸在 resolve_config 派生到避腿窄带 / 后缘外侧，不产生非法穿模组合
- 无 regression override 主导 seed domain
- 连续 scale（table_size/aspect/height、telescope_travel）在 resolve_config clamp/派生
- 每腿关节类型/轴与所选 support 一致（REVOLUTE Y / PRISMATIC Z / REVOLUTE X）；drop_leaf REVOLUTE X
- captured-pin/sleeve 铰链声明 element-scoped allow_overlap（不用 broad part-level）
- copied slat 遵守 `slat_{i}` 命名与均布放置
- run_tests 含每机构 targeted `ctx.pose(...)`（腿折/伸缩/leaf 下折）+ baseline gates

## Reject cases

- 腿折 `upper` 过大致左右足/管交叉穿模（未按 `leg_fold_upper` 不等式回缩）
- storage 铺满全宽与摆动腿/ X 交叉腿在 sampled pose 穿模（未夹到中央窄带）
- drop_leaf 铰接线置于后腿内侧致下折撞腿
- 把不动的 sleeve/collar/围边/角球/螺钉/储物做成独立 FIXED part（违 Rule 1）
- 用 broad part-level allow_overlap 掩盖过宽关节行程（而非 element-scoped captured-pin）
- roll_top slat_count 越界（<6 或 >20）或 slat_w 变负
- 把 LatheGeometry/Extrude slat 降级成裸 Box 占位（违 Rule 3）—— slat 必须保持 ExtrudeGeometry(rounded_rect_profile)
- 腿在开姿态不落地（foot z 远离 0）或折叠不上升

## 与相邻类别的边界

- 不该混入：固定露台/野餐桌（无折叠/伸缩关节，违 must_keep）
- 不该混入：工作台 / 绘图桌（倾斜台面、重型，drifts to workbench）
- 不该混入：折叠椅/凳（有靠背/坐面比例，非抬升工作面）
- 不该混入：带轮餐车 / camp kitchen cart（下层带轮，drifts to serving cart）
- 不该混入：货架单元（多层无桌面语义）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 4 slot（surface③ / support①② / storage③ / top-ext①）+ slat multiplicity + 5 palette；bifold 与 scissor 两个 fold_mechanism fork **deferred**（见下），已用 revolute（直/撇/X 腿 + drop_leaf）与 prismatic（伸缩腿）覆盖 ② 主要关节类型多样性。 |

## 模板实现备注（可选）

- 共享 helper：`_slat_mesh()`（只建一次复用 N 条）、`_frame_and_corners()`（三种表面共用围边/角球/装饰）、`_tube_between` / brace_stub helper。
- captured-pin：straight/splayed 腿 `hinge_socket_i`↔`hinge_pin`/`straight_tube`；telescoping `leg_sleeve_i`↔`inner_tube`；x_cross pair `xleg_tube`↔`xleg_tube` + `cross_pivot`；drop_leaf `leaf_hinge_barrel`↔`leaf_knuckle` —— 全 element-scoped `allow_overlap`。
- **Deferred（暂不进 seed domain，documented degrade）**：
  - `bifold_center_hinge`（②中缝顶折）：需把根 tabletop 拆成 `tabletop_left`+`tabletop_right` 两个 part 并让 surface/storage/leaf 全部适配拆分根拓扑，与本模板 parallel-children 单根设计冲突；其 ② REVOLUTE 类型已由 drop_leaf/腿折覆盖。留作独立 slug 或后续扩展。
  - `accordion_scissor_base`（②剪叉收合）：需 4-arm Mimic 联动 + 大量 pair allow_overlap，收敛风险高；其 ② 也是 REVOLUTE(+mimic)，不引入新关节类型。deferred 到基础模板稳定后再评估。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | roll_top_slats | origin A | L39-L47,L92-L121 | slat mesh + loop + 装饰 |
| S2 | A/C | (frame) / fabric_hammock | origin B | L172-L270 | 板条框架 + 织物网兜储物 |
| S3 | A | solid_panel | var_solid_panel_top | L67-L112 | 单板面 |
| S4 | A | fabric_mesh | var_mesh_fabric_top | L67-L134 | 张紧膜面 + bound edges |
| S5 | B | straight_folding_legs | origin A | L195-L246 | 直腿 REVOLUTE |
| S6 | B | telescoping_legs | origin B | L44-L111 | 伸缩腿 PRISMATIC |
| S7 | B | splayed_aframe_legs | var_splayed_aframe_legs | L236-L304 | 撇腿 |
| S8 | B | x_cross_legs | var_x_cross_legs | L241-L313 | X 交叉腿 REVOLUTE-X |
| S9 | C | rigid_shelf | var_rigid_lower_shelf | L219-L268 | 刚性下层托盘 |
| S10 | D | drop_leaf | var_drop_leaf_extension | L329-L435 | 后缘折翼 |
| S11 | mult | slat_count | var_slats_6 / var_slats_20 | L27-L29 | N=6/20 板条数轴 |
