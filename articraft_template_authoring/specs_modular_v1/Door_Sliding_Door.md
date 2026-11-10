# sliding_door — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `sliding_door` |
| template path | `agent/templates/Door_Sliding_Door.py` |
| test path (optional) | `tests/agent/test_sliding_door_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `multiplicity` (主轴 = N glazed leaves on parallel PRISMATIC tracks) × `parallel_children` (named structural slots: kinematics / track / infill / handle / framing all hang off one static frame root) → 综合记为 `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 |
| read_count | 12 |
| read_scope | all 5-star samples in this category (5 converged parents + 7 converged variants) |
| source_index_policy | only adopted module sources are indexed below |

阅读要点（全部 12 个 model.py 已逐行读取）：

- **统一身份**：每个样本都是“静止外框 + 固定扇” 作为单一 root part，N−1（或 2）个 **glazed/panelled leaf** 各挂在一根 **PRISMATIC** joint 上沿水平 X 轨道平移。世界 +Z 向上，宽度沿 X、高度沿 Z、厚度沿 Y；门站在地面（z=0 起）。没有任何 REVOLUTE / hinge —— 这是与 hinged Door 的硬边界。
- **主变化轴 = 扇片数 N**：N=2 (`rec_door_slide_2panel`)、N=3 (`rec_door_slide_3panel_tele`)、N=4 (`rec_door_slide_4panel_tele` 与 `rec_door_slide_4panel_center`)、N=5 (`rec_door_slide_5panel_tele`)、N=6 (`rec_sliding_door_var_6panel_tele`)。distinct-N = 5。
- **三种 kinematics**：telescoping（逐扇行程递增、各扇独立 Y lane、后扇越走越远 nest 堆叠，见 3p/4p/5p/6p）、bypass（单滑扇在前 depth plane 越过固定扇，2panel）、center-biparting（两中扇用单标量 `Mimic` 反向对开，4panel_center，`door_1` mimic-couples `door_0`）。
- **loop-emission 标杆**：`rec_door_slide_5panel_tele` / `rec_sliding_door_var_6panel_tele` 用 `_lane_y(i)` + `_pane_center_x_closed(slot)` + `_add_leaf(part,...)` + `for i in range(N-1)` 造扇+造关节（行程 `slot*PANE_PITCH − i*NEST`），是模板化滑扇复制逻辑应当采纳的 helper 三件套；其余 parent 滑扇为手写，模板化须统一改为 loop。
- **Y-lane / depth 分离不变量**：所有扇片靠 Y 方向 lane 偏移彼此错开，才能在 X 投影上重叠却不穿模；run_tests 普遍 `expect_gap(... axis="y")` + 整组 `allow_overlap(... axis 隐含 X)` 声明 telescoping 重叠是预期。
- **捕获式轨道工程**：concealed-header 样本里 leaf top/bottom rail 故意伸进 head/sill 槽道（`head_track`/`sill_track` 或 `top_track`/`bottom_track`），用 element-scoped `allow_overlap` + `expect_contact`/`expect_overlap` 证明 captured engagement；barn_rail 则把外露 `rail_bar` + 滚轮 `roller_i` 接触 rail 底面作为捕获语义。
- **infill 是真实结构变化（非换色）**：full-glass（透明薄板）、muntin-grid（2×3 `lite_i` + 不透明 `vbar/hbar` 玻璃格条）、raised-panel（Shaker 凸边框 + 凹中心 `*_center` 实木面，不透明）、slatted-louver（`for i in range(n)` 统一 roll 倾角的百叶 blade）。
- **handle 是真实结构变化**：flush-bar（薄竖条 box）、curved-C-pull（弓形 Cylinder grip + 两斜 neck）、proud-D-loop（圆管 grip + 两 standoff neck cylinder，凸出 ≥15mm）、flush-finger-pull-pocket（CadQuery `cutBlind` 凹槽 mesh stile，无凸件）。
- **framing 两族**：slim-black-alu（细窄黑铝，FRAME_FACE≈0.042–0.070）、wide-white-vinyl（宽白 uPVC，FRAME_FACE≈0.060、LEAF_STILE≈0.055）。

## 核心身份

Sliding Door = 一组在固定外框/导轨内沿**水平直线 (PRISMATIC, axis≈±X)** 平移开合的玻璃/实心扇片，配合若干**永久固定扇**（telescoping 的 1 个、center-biparting 的 2 侧扇、bypass 的 1 个）。物理含义：靠平移腾出通行口，而不是绕铰链转动。默认成熟域是住宅/庭院/商铺的多扇推拉玻璃门，宽度 ~2.8–4.0 m、高度 ~2.0–2.4 m，站在地面上。

主要功能轴是**扇片数 N（multiplicity）**，叠加 5 个命名结构槽：kinematics（开合运动学）、track_style（顶轨/吊挂样式）、infill（扇芯样式）、handle（拉手样式）、framing（边框样式）。

**不该混入的相邻类别**见“与相邻类别的边界”节——核心红线：任何主开合运动若是 REVOLUTE/铰链转动，就不属于本类别（那是 hinged/French/folding/garage door）。

## 槽位 + 候选模块表

### Slot A：multiplicity_N（主轴 —— 玻璃/面板扇总数；distinct N = 2/3/4/5/6）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| N2_bypass | rec_door_slide_2panel | L74-L153 (root frame+fixed pane), L161-L208 (single moving leaf), L232-L243 (joint) | eligible if compatible | 1 固定扇 + 1 滑扇；最简多重度，单 PRISMATIC；与 kinematics=bypass 强绑定 |
| N3_tele | rec_door_slide_3panel_tele | L88-L142 (`_add_panel_frame` shared helper), L161-L233 (root+fixed), L240-L286 (inner/outer panes), L300-L321 (2 joints) | eligible if compatible | 1 固定扇 + 2 滑扇逐个手写调用共享 helper；模板化须改 `for i in range(N-1)` |
| N4_tele | rec_door_slide_4panel_tele | L60-L112 (`_add_leaf` shared helper), L129-L204 (root+fixed+`track_rib` loop L161-L167), L211-L224 (3 leaves), L235-L261 (3 joints) | eligible if compatible | 1 固定扇 + 3 滑扇；唯一 enumerate loop 是 track_rib；滑扇手写，模板化改 loop |
| N5_tele | rec_door_slide_5panel_tele | L76-L78 (`_lane_y`), L81-L89 (`_pane_center_x_closed`), L92-L145 (`_add_leaf`), L159-L244 (root+fixed), L250-L281 (`for i in range(4)` 造扇+造关节) | eligible if compatible | **loop-emission 标杆**：helper 三件套 + 全循环造扇/造关节，行程 `slot*PANE_PITCH − i*NEST`；模板复制逻辑的采纳源 |
| N4_center | rec_door_slide_4panel_center | L96-L128 (`_add_leaf_frame`), L131-L184 (`_add_curved_handle`), L200-L284 (root+2 fixed+`mullion_i` loop L245-L251), L300-L310 (2 center leaves), L321-L343 (2 mimic-coupled joints) | eligible if compatible | 2 固定侧扇 + 2 中分滑扇，单标量 `Mimic` 反向对开；与 kinematics=center-biparting 强绑定 |
| N6_tele | rec_sliding_door_var_6panel_tele | L76-L145 (helper 三件套，复用), L159-L244 (root+fixed), L251-L281 (`for i in range(5)` → 5 滑扇 + 6 关节) | eligible if compatible | gold-standard loop 直接外推到 N=6（5 sliders + 1 fixed）；证明 loop 可任意扩 N |

### Slot B：kinematics（开合运动学；决定固定扇布局 + 行程公式 + joint 极性）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| telescoping | rec_door_slide_5panel_tele | L250-L281 (逐扇 PRISMATIC，axis=(-1,0,0)，行程 `slot*PANE_PITCH − i*NEST`，各扇 `_lane_y(slot)` 独立 Y lane) | eligible if compatible | 1 固定扇 + (N−1) 同向滑扇，后扇行程更远→nest 堆叠；N∈{3,4,5,6} 走此路线 |
| bypass | rec_door_slide_2panel | L232-L243 (单 PRISMATIC，axis=(-1,0,0)，`travel=BAY_W−FRAME_FACE`，单扇前置 depth plane `Y_LEAF` L51 越过固定扇) | eligible if compatible | 1 固定扇 + 1 滑扇，前后两 depth plane；专用于 N=2 |
| center-biparting | rec_door_slide_4panel_center | L321-L343 (`door_0_slide` axis=(-1,0,0) + `door_1_slide` axis=(1,0,0) `mimic=Mimic(door_0_slide, mult=1.0)`，`travel=BAY_W−0.010`) | eligible if compatible | 2 固定侧扇 + 2 中分滑扇反向对开，单标量耦合；专用于偶数 N（基线 N=4） |

### Slot C：track_style（顶轨 + 吊挂/捕获样式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| concealed-header | rec_door_slide_5panel_tele | L196-L207 (`bottom_track`/`top_track` 框内暗藏槽道), L326-L364 (rail↔track captured `allow_overlap`+`expect_contact`)；另见 rec_door_slide_2panel L120-L142 (`head_track`/`sill_track` lip) 与 rec_door_slide_4panel_tele L161-L167 (`track_rib_i`) | eligible if compatible | 周边框 + 框内 head/sill 暗藏槽道，扇 rail 伸入被捕获；适配全部 kinematics |
| exposed-barn-track-rollers | rec_sliding_door_var_barn_rail | L98-L103 (`_build_roller_mesh`), L122-L130 (外露 `rail_bar`/`barn_rail` root), L132-L160 (`for i in range(2)` 全高墙挂条 `bracket_plate_i`/`bracket_arm_i`), L162-L178 (`floor_guide_pin`/`floor_guide_base`), L242-L257 (`for i in range(2)` `hanger_i` + 曲面 `roller_i`), L262-L274 (单 PRISMATIC `leaf_slide`) | eligible if compatible | 无周边框/无暗藏槽道；外露横钢轨 + 顶吊滚轮吊架 + 底导向针；root 为 `barn_rail`；joint origin 落在 `RAIL_BOTTOM_Z` 接触线。当前仅 off-2panel-bypass 落盘（见兼容性矩阵限制） |

### Slot D：infill（扇芯/嵌板样式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| full-glass | rec_door_slide_5panel_tele | L103-L108 (`glass` 透明薄板 Box，inset within border)；另见 rec_door_slide_2panel L203-L208 (`leaf_pane`) | eligible if compatible | 整片透明低 alpha 玻璃；run_tests 断言 alpha<0.5 |
| muntin-grid-divided-lite | rec_sliding_door_var_muntin_grid | L66-L118 (`_add_muntin_grid` 嵌套 `for row/col` 造 2×3 `lite_i` + `for i` 造 `vbar_i`/`hbar_i`)，调用见 L157-L164 (leaf) 与 L263-L270 (fixed) | eligible if compatible | 透明玻璃格 + 不透明铝玻璃格条；6 lites + bars/扇；格条凸出玻璃 (MUNTIN_D>GLASS_D) |
| solid-opaque-raised-panel | rec_sliding_door_var_raised_panel | L63-L96 (`add_shaker_panel`：`for i in range(2)` 造 stile/rail 凸边框 + 凹中心 `*_center` 实心场) | eligible if compatible | 无玻璃；不透明木边框/中心；border 凸出 recessed center (PANEL_RECESS) |
| slatted-louver | rec_sliding_door_var_slatted_louver | L66-L101 (`_add_louver_slats`：`n=max(2,int(height/spacing))`，`for i in range(n)` 造统一 roll 倾角 `slat_*_i` blade) | eligible if compatible | 不透明百叶 blade，≥20 片/扇，非零 roll 倾角 (SLAT_ANGLE≈0.52 rad) |

### Slot E：handle / pull（拉手样式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flush-bar | rec_door_slide_2panel | L210-L222 (`handle_lever` 薄竖条 Box，proud≈0.008)；另见 rec_door_slide_4panel_tele L102-L112 (`_add_leaf(..., with_handle=True)` 竖条 `handle`) | eligible if compatible | 单个薄竖条 box 拉手，几乎齐平；最常见 |
| curved-C-pull | rec_door_slide_4panel_center | L131-L184 (`_add_curved_handle`：两斜 `*_neck_top/bottom` Cylinder + 弓形 `*_grip` Cylinder，proud bow 0.034) | eligible if compatible | 弓形 Cylinder C 形拉手，两 neck 锚回 stile；与 framing=wide-white 同源 |
| proud-D-loop | rec_sliding_door_var_d_loop_handle | L213-L231 (`handle_grip` 圆管竖 Cylinder), L233-L247 (`for i` 造两 standoff `handle_neck_i` Cylinder) | eligible if compatible | 凸出圆管 D 环，grip 站离 stile 面 ≥15mm；run_tests 证明 proud |
| flush-finger-pull-pocket | rec_sliding_door_var_flush_finger_pull | L64-L81 (`_build_pocket_stile_cq` CadQuery `cutBlind` 凹槽), L84-L105 (`_add_leaf` mesh-stile 分支：`stile_lead` 用 `mesh_from_cadquery`) | eligible if compatible | 凹槽 finger pull，mesh-backed stile，无任何凸拉手；run_tests 断言不存在凸 `handle` |

### Slot F：framing（stile/rail 边框样式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| slim-black-alu | rec_door_slide_5panel_tele | L30-L33 + L68-L71 (MEMBER/STILE/RAIL 细窄), L92-L137 (`_add_leaf` 细黑铝四边 + L152-L153 `black_aluminium` 材质)；另见 rec_door_slide_2panel L30-L36/L54 | eligible if compatible | 细窄黑铝边框 (face≈0.034–0.070)，深色低反；多数样本基线 |
| wide-white-vinyl | rec_door_slide_4panel_center | L46-L76 (FRAME_FACE=0.060, LEAF_STILE=0.055 宽白尺寸), L96-L128 (`_add_leaf_frame` 宽白四边), L190-L191 (`white_vinyl`/`white_trim` 材质) | eligible if compatible | 宽白 uPVC 边框 (face≈0.055–0.060)，亮白；与 curved-C-pull 同源 |

> 每个 slot 候选数：A=6(distinct-N 5)，B=3，C=2，D=4，E=4，F=2。全部 ≥2 ✓。track_style 仅 2 个但已满足下限（exposed-barn-track 是唯一第二候选，源充分，不降级）。

## 槽位图（slot graph）

pattern: mixed = multiplicity(主轴 N leaves on PRISMATIC) over parallel_children(structural slots on one frame root)

```
                         [Slot F framing]  (装饰/尺寸调制：作用于 root frame 与每个 leaf 的 stile/rail)
                                │ (材质+边框尺寸，不改拓扑)
                                ▼
[Slot C track_style] ── root part ──(static frame / 或 barn_rail)
   (concealed: 周边框+暗藏 head/sill 槽道; 或 exposed: rail_bar+墙挂条+底导向)
        │
        │  PRISMATIC joint(s)  ── axis=±X, origin=closed-leaf-center (telescoping/bypass)
        │                          或 RAIL_BOTTOM_Z 接触线 (barn)
        ▼
[Slot A multiplicity_N] ── N−1 (tele) / 1 (bypass) / 2 (center) 个 leaf child part
        │   每 leaf 占一根独立 Y lane（_lane_y(i)）以在 X 投影重叠却不穿模
        │
        ├── [Slot D infill]  per-leaf 扇芯（full-glass / muntin / raised-panel / louver）
        │       + 同样 infill 应用到固定扇（保持视觉一致）
        │
        └── [Slot E handle]  per-(leading) leaf 拉手（flush-bar / curved-C / D-loop / finger-pocket）

[Slot B kinematics] = 横切约束：决定固定扇数量与布局、行程公式、joint 极性/Mimic 耦合
   telescoping: 1 fixed + (N−1) 同向 (-X)，travel 递增 nest
   bypass:      1 fixed + 1 (-X)，单扇 (N=2 专属)
   center:      2 fixed 侧扇 + 2 中分反向 (±X)，door_1 mimic door_0 (偶数 N)
```

接口点位说明：

- **root → leaf 接口**：每根 PRISMATIC joint 的 `origin` = 该扇 **closed-pose 中心**（telescoping/bypass）或 **rail 底面接触线 RAIL_BOTTOM_Z**（barn）。leaf 在自身 part-local frame 居中（x=0,z=0），joint origin 把它放到 closed 位。axis = `(-1,0,0)`（telescoping/bypass，正 q 向 −X 开）；center-biparting `door_0` axis `(-1,0,0)`、`door_1` axis `(1,0,0)` 且 `Mimic(joint=door_0_slide, multiplier=1.0)`。
- **leaf ↔ track captured engagement**：concealed 下 leaf top/bottom rail 伸入 `head/sill track` 或 `top/bottom track`，用 element-scoped `allow_overlap` + `expect_contact`/`expect_overlap` 证明；barn 下 `roller_i` 接触 `rail_bar` 底面。
- **leaf ↔ leaf depth 分离**：相邻扇靠 Y lane（`LANE_GAP`/`PLANE_PITCH`/`TRACK_Y[i]`）错开，`expect_gap(axis="y", positive_elem="glass", negative_elem="glass")`。
- **互斥 / 派生关系**：B=bypass ⟺ A=N2；B=center-biparting ⟺ A∈偶数（基线 N4）；C=exposed-barn 当前仅与 A=N2/B=bypass 兼容（见兼容性矩阵）。framing(F) 仅调制材质+边框尺寸，不改拓扑，自由组合。

## 每槽位 Module Emits / Interfaces

### Slot A / module N5_tele（loop-emission 标杆，作为 multiplicity 复制基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`(root, 含 fixed 扇) + `pane_0..pane_{N-2}` leaf parts | rec_door_slide_5panel_tele/model.py:L159-L255 |
| internal joints | `pane_i_slide` × (N−1)，PRISMATIC，axis=(-1,0,0)，`upper=slot*PANE_PITCH − i*NEST` | model.py:L271-L281 |
| upstream interface | leaf 在 part-local 居中；joint origin=(`_pane_center_x_closed(slot)`, `_lane_y(slot)`, OPEN_ZC) | model.py:L81-L89, L265-L277 |
| downstream interface | leaf top/bottom rail 进 head/sill track（captured），相邻扇 Y lane 分离 | model.py:L111-L122, L326-L399 |

### Slot B / module center-biparting
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`(2 fixed 侧扇 `outer_pane_0/1`) + `door_0`/`door_1` 中扇 | rec_door_slide_4panel_center/model.py:L200-L310 |
| internal joints | `door_0_slide`(axis -X) + `door_1_slide`(axis +X, mimic door_0) | model.py:L321-L343 |
| upstream interface | joint origin=closed 中扇中心 ±meet_reveal；单标量驱动两扇 | model.py:L319-L342 |
| downstream interface | 中扇 rail 进 head/sill track；开时各扇 tuck 到对应固定侧扇前 (Y 分离) | model.py:L357-L373, L475-L492 |

### Slot C / module exposed-barn-track-rollers
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `barn_rail`(外露 `rail_bar` + `bracket_plate_i`/`bracket_arm_i` + `floor_guide_pin/base`) | rec_sliding_door_var_barn_rail/model.py:L122-L178 |
| internal joints | 单 `leaf_slide` PRISMATIC，origin 落 `RAIL_BOTTOM_Z` | model.py:L262-L274 |
| upstream interface | leaf 顶 `hanger_i` + `roller_i` 接触 rail 底面（captured-by-roller） | model.py:L242-L257, L355-L363 |
| downstream interface | `floor_guide_pin` 在 leaf 底下方 (expect_gap)；hanger 始终在 rail 宽内 | model.py:L379-L416 |

### Slot D / module muntin-grid-divided-lite
| emits | 描述 | 来源 |
|---|---|---|
| parts (visual) | `*_lite_{0..5}` 透明玻璃格 + `*_vbar_i`/`*_hbar_i` 不透明格条（per leaf + per fixed pane） | rec_sliding_door_var_muntin_grid/model.py:L66-L118 |
| internal joints | 无（infill 为 leaf-local visual） | — |
| upstream interface | 由 `_add_leaf`/fixed-pane builder 在扇中心调用，glass_w/glass_h 来自边框内净空 | model.py:L154-L164, L263-L270 |
| downstream interface | 格条凸出玻璃面 (MUNTIN_D>GLASS_D)；不影响 track/joint | model.py:L100-L118 |

### Slot E / module proud-D-loop
| emits | 描述 | 来源 |
|---|---|---|
| parts (visual) | `handle_grip` 圆管竖 Cylinder + `handle_neck_{0,1}` standoff Cylinder | rec_sliding_door_var_d_loop_handle/model.py:L226-L247 |
| internal joints | 无（拉手为 leaf-local visual） | — |
| upstream interface | 锚在 leading stile 室内面 (+Y)，handle_x=leading stile 中心 | model.py:L216-L223 |
| downstream interface | grip 凸出 stile 面 ≥15mm（proud 断言）；不进入相邻 lane | model.py:L218-L231 |

### Slot F / module wide-white-vinyl
| emits | 描述 | 来源 |
|---|---|---|
| parts (visual) | root frame + 每 leaf 的宽白 stile/rail（face/depth 加宽，材质 white_vinyl/white_trim） | rec_door_slide_4panel_center/model.py:L96-L128, L200-L251 |
| internal joints | 无（framing 是尺寸+材质调制） | — |
| upstream interface | 调大 FRAME_FACE / LEAF_STILE 并切换材质；其余拓扑不变 | model.py:L48-L76, L190-L195 |
| downstream interface | 不改 joint origin / track / multiplicity；仅占用更多边框净空 | model.py:L62-L67 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `kinematics` | enum | telescoping / bypass / center_biparting | — | choice | deterministic sampler；受 compatibility matrix 与 N 约束（bypass⟺N2；center⟺偶数 N） | Slot B 表 |
| `panel_count` (N) | int | [2, 12]（测试偏小；产品全程见 §Multiplicity） | — | conditional | 合法 N 依赖 kinematics（见 N_range/兼容矩阵）；加权采样后 clamp | rec_*_tele/center |
| `track_style` | enum | concealed_header / exposed_barn | concealed_header | choice | exposed_barn 当前仅 N2+bypass 合法（gating） | Slot C 表 |
| `infill` | enum | full_glass / muntin_grid / raised_panel / slatted_louver | full_glass | choice | 自由组合，应用到固定扇与全部 leaf | Slot D 表 |
| `handle` | enum | flush_bar / curved_C_pull / proud_D_loop / finger_pocket | flush_bar | choice | finger_pocket 与 raised_panel/louver 不冲突；finger_pocket 改 stile 为 mesh | Slot E 表 |
| `framing` | enum | slim_black_alu / wide_white_vinyl | slim_black_alu | choice | 仅改材质+边框尺寸，自由组合 | Slot F 表 |
| `palette_style` | enum | charcoal_black_alu / anodized_dark_bronze / warm_white_vinyl / clear_glass_neutral / tinted_grey_glass / oak_warm_wood | charcoal_black_alu | choice | 调色板（边框+玻璃 tint+木色）；详见下方 palette 说明 | 全样本材质 |
| `opening_width_scale` | float | [0.85, 1.20] | 1.0 | independent | 缩放 UNIT_W/OPENING_W；采样后 clamp | rec_*_tele L28-L33 |
| `opening_height_scale` | float | [0.90, 1.15] | 1.0 | independent | 缩放 UNIT_H/FRAME_H | rec_*_tele L29-L31 |
| `frame_face_scale` | float | [0.85, 1.25] | 1.0 | independent | 缩放 FRAME_FACE/MEMBER（受 framing enum 标称值约束） | rec_door_slide_2panel L31-L36 |
| `lane_gap_scale` | float | [0.9, 1.3] | 1.0 | independent | 缩放 LANE_GAP/PLANE_PITCH（扇 depth 分离） | rec_door_slide_5panel_tele L38 |
| `leaf_pitch` (derived) | float | derived | — | equation | `= clear_opening_W / panes_across`（telescoping=N、center=4、bypass=2） | rec_door_slide_5panel_tele L59 |
| `meeting_overlap` (derived) | float | derived | 0.030 | equation | `= k · STILE`（保持 closed 互锁，随 frame_face_scale 派生） | rec_door_slide_5panel_tele L60-L61 |
| `travel_i` (derived) | float | derived | — | equation | telescoping `slot·leaf_pitch − i·NEST`；center `BAY_W − 0.010`；bypass `BAY_W − FRAME_FACE` | rec_*_tele L270 / center L317 |
| (—) | constraint | — | — | inequality | `frame_depth ≥ N·lane_pitch + 2·MEMBER`（lane 堆叠必须装进框深）；违反则回缩 lane_gap_scale 或拒绝重采 | rec_door_slide_5panel_tele L38-L40 |
| (—) | constraint | — | — | inequality | `Σ leaf_widths − (N−1)·meeting_overlap ≤ clear_opening_W`（闭合扇片必须铺满不溢出）；违反按比例回缩 leaf_pitch | rec_door_slide_3panel_tele L66-L80 |
| (—) | constraint | — | — | inequality | `travel_{N-2} ≤ clear_opening_W − leaf_width + NEST`（最远扇行程不出框）；违反 clamp travel | rec_door_slide_4panel_tele L226-L232 |

**palette_style 说明（≥3，目标 4–6 realistic colorways）：** 取 6 个：
1. `charcoal_black_alu`（边框 (0.09,0.09,0.10) 黑铝 + clear glass tint，来源 2panel/3p/4p/5p parents）。
2. `anodized_dark_bronze`（深古铜暗色铝，源自 5panel `anodized_black` (0.05,..) + 暖偏移，商用深色门）。
3. `warm_white_vinyl`（白 uPVC (0.93,0.94,0.94) + 偏冷 clear glass，来源 4panel_center）。
4. `clear_glass_neutral`（中性高透 glass (0.78,0.82,0.84,0.12) + 黑铝框，来源 3panel/4p）。
5. `tinted_grey_glass`（灰染玻璃 (0.62,0.70,0.72,0.22)/(0.62,0.72,0.78,0.28) + 黑铝框，来源 5panel/center）。
6. `oak_warm_wood`（仅当 infill∈{raised_panel, slatted_louver} 时可选；木色 (0.40,0.26,0.14)/(0.52,0.36,0.22) 边框/中心，来源 raised_panel/louver）。

palette 是材质层枚举（边框 RGBA + 玻璃 tint/alpha + 木色），不改拓扑；oak_warm_wood 受 infill enum 条件约束（conditional），其余对全 infill 合法。

## Multiplicity / Copy Logic

本模板有 **1 根 multiplicity 轴**：玻璃/面板扇总数 N。

- **count_param**：`panel_count` (= N，玻璃/面板扇总数)。
  - telescoping：1 fixed + (N−1) sliders。
  - center-biparting：2 fixed 侧扇 + 2 中分 sliders（基线 N=4；高 N 为对称 per-side 加倍，下游可扩但当前主域取 N=4）。
  - bypass：1 fixed + 1 slider（N=2 专属）。
- **N_range（本小类本轴的产品域）**：`[2, 12]`。测试主域偏小：sweep 与 viewer 目检集中在 N∈{2,3,4,5,6}（parents+converged 已覆盖证明），N∈{7..12} 由 loop-emission 构造安全（gold-standard `for i in range(N-1)` 已对 N=6 外推证明），稀疏采样。
- **sampling domain（权重档）**：小 N 高频、大 N 稀有。建议加权：N2≈0.22, N3≈0.20, N4≈0.22, N5≈0.16, N6≈0.10, N∈{7..9}≈0.08(合计), N∈{10..12}≈0.02(合计)。下游对该轴做一次加权采样、编进 `slot_choices`、clamp 到 kinematics 允许集、sweep 上限设 N=12。
- **copied object**：单个 glazed/panelled leaf（含 Slot D infill + Slot E handle，由 `_add_leaf` 类 helper 产出）。
- **naming**：滑扇 part `pane_i`（i=0..N-2，telescoping）/ `door_0`,`door_1`（center）/ `sliding_leaf`（bypass 单扇）；关节 `pane_i_slide` / `door_{0,1}_slide` / `leaf_slide`。模板统一采用 telescoping 路线的 `pane_i` / `pane_i_slide` 作为规范命名（其余 kinematics 为特例分支）。
- **placement**：每扇 closed 中心 `_pane_center_x_closed(slot)`，各扇独立 Y lane `_lane_y(slot)`（telescoping 单调前移；center 两中扇对称）。
- **joint policy**：统一 PRISMATIC。telescoping 同向 (−X) 且行程递增 (`slot·pitch − i·NEST`) 形成 nest；center-biparting 反向 (±X) 且 `door_1` 用 `Mimic(door_0_slide, multiplier=1.0)` 单标量耦合；bypass 单 joint。所有 captured-engagement / telescoping nest 重叠用 element- 或 part-scoped `allow_overlap` 声明。

## 拓扑多样性审计

总组合数（结构槽，未计连续 scale 与 palette）：

```
distinct-N(主采样域取 5 个代表档 N∈{2,3,4,5,6}，实际域 [2,12])
× kinematics(3) × track_style(2) × infill(4) × handle(4) × framing(2)

仅两个 headline 非-N 结构槽 × distinct-N（保守门控）：
   infill(4) × track_style(2) × distinct-N(5) = 40 ≥ 10 ✓
计入全部轴（受兼容性 gating 后仍）：
   N(5) × kin(3) × track(2) × infill(4) × handle(4) × framing(2) ≫ 100
```

理由：仅 infill×track×distinct-N 就有 40 个合法拓扑等价类，远超 10；handle/kinematics/framing 进一步放大。即便 exposed-barn 受 N2 gating 限制，concealed×全 N×全 infill 仍 ≥40。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 deterministic procedural sampling：(1) 先按权重抽 `panel_count` N（小 N 偏多）；(2) 抽 `kinematics`，并用兼容矩阵把 N 投影到合法集（bypass→强制 N2；center→强制偶数，否则回退 telescoping）；(3) 独立抽 track_style（exposed_barn 仅当 (N2,bypass) 时合法，否则回退 concealed_header）；(4) 独立抽 infill / handle / framing / palette_style（palette 的 oak 仅当 infill∈{raised,louver}）；(5) 采 independent 连续 scale → 派生 leaf_pitch/meeting_overlap/travel → 用 3 条 inequality 把组合投影/回缩到可行域，不满足则拒绝重采。`slot_choices_for_seed(seed)` 返回稳定 `(slot,module)` 列表（含 `panel_count` 因其改变拓扑等价类，但不含连续 scale）。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别因 N(实域 11 档)×kin(3)×track(2)×infill(4)×handle(4)×framing(2) 组合空间足够大，预期可达 ≥300（兼容 gating 后仍宽裕）。

Controlled local parameterization：初版模板包含的关键连续 scale = `opening_width_scale [0.85,1.20]`、`opening_height_scale [0.90,1.15]`、`frame_face_scale [0.85,1.25]`、`lane_gap_scale [0.9,1.3]`；派生 `leaf_pitch`(=clear_W/panes_across)、`meeting_overlap`(=k·STILE)、`travel_i`。全部在 `resolve_config` 中 clamp/派生/投影，受 3 条 inequality（frame_depth≥lane 堆叠、闭合不溢出、行程不出框）约束，不破坏 InterfaceSpec(joint origin)、MatingContract(rail↔track / roller↔rail captured)、multiplicity(N)。跨部件依赖（lane 堆叠 vs 框深、行程 vs 净空）显式落在 inequality 行，不当独立自由变量。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先加权抽 N → 抽 kinematics(投影 N) → 抽 track(gating) → 独立抽 infill/handle/framing/palette；各 clamp | `slot_choices_for_seed` 与 build choices 一致；N 与 kinematics 互洽 |
| compatibility matrix | bypass⟺N2；center⟺偶数 N(基线4)；exposed_barn⟺(N2,bypass)；oak palette⟺infill∈{raised,louver}；其余自由；非法→回退默认 | 无悬空扇、无 closed 漏光、无穿模(Y lane 分离)、joint 轴/极性正确、最大 N≤12、telescoping nest 不脱开 |
| controlled local variation | 4 个 scale + clamp + 3 inequality 投影/回缩 | 比例变化不破坏 captured engagement、clearance、joint origin、闭合互锁、类别 identity |
| regression overrides | none（如后续出现 sweep 失败再按 seed+理由稀疏添加） | 仅已知失败回归 / 审核指定样本 |
| random sweep | seeds 0-49 初轮；0-999 成熟度审计（含 N≤12、各 kinematics、exposed_barn gating、各 infill/handle） | 与 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A multiplicity_N | 6 (distinct-N 5, 实域 [2,12]) | yes | yes | 主轴 |
| B kinematics | 3 | yes | yes | |
| C track_style | 2 | yes | no | exposed_barn 源充分但受 N2 gating；不降级 |
| D infill | 4 | yes | yes | |
| E handle | 4 | yes | yes | |
| F framing | 2 | yes | no | 仅材质+尺寸调制，下限达标 |

## Validator

- `slot_choices_for_seed` returns implemented module names（kinematics/track/infill/handle/framing + `panel_count`）
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos（bypass⟺N2、center⟺偶数、exposed_barn⟺N2+bypass、oak⟺raised/louver）
- optional regression overrides are sparse and justified（初版 none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params clamped；3 条 inequality（lane 堆叠≤框深、闭合不溢出、行程不出框）在 `resolve_config` 求解，不留到 builder 失败
- critical InterfaceSpec / MatingContract points exist：每根 PRISMATIC joint origin=closed-leaf-center 或 RAIL_BOTTOM_Z；rail↔track / roller↔rail captured engagement 用 element-scoped allow_overlap
- key joints have expected type/axis/range：全 PRISMATIC；telescoping/bypass axis=(-1,0,0)；center door_1 axis=(1,0,0)+Mimic(door_0)；upper>0
- copied objects follow naming/placement：`pane_i`/`pane_i_slide`，各扇独立 Y lane，closed 互锁，open telescoping nest 保持 overlap

## Reject cases

1. 主开合用 REVOLUTE/铰链转动（变成 hinged/French/folding door）—— 非本类别。
2. 采到 bypass 但 N≠2，或采到 center-biparting 但 N 为奇数（固定扇/中扇布局不自洽）。
3. exposed_barn 与 telescoping/center 或 N>2 组合（当前无该接口源：barn root 仅证明单扇 leaf_slide）。
4. 扇片缺独立 Y lane 导致相邻扇在 closed/open 真实穿模（非 element-scoped 声明的 overlap）。
5. closed 姿态扇间漏光（meeting_overlap 不足，扇片未铺满净空）或扇片溢出框外（行程/净空 inequality 未投影）。
6. telescoping 开到 upper 时相邻扇脱开（nest overlap 丢失，joint upper 取过大）。
7. captured engagement 缺失：leaf rail 不进 head/sill track 或 roller 不接触 rail，扇读作悬空 floating part。
8. lane 堆叠总深超过框深（frame_depth inequality 未约束），扇前后穿出框面。
9. 把 palette/材质/纯尺寸当作独立 slot 或独立 candidate（违反“仅换色/尺寸不是新候选”）。

## 与相邻类别的边界

- 不该混入：**Hinged / French / 平开 Door**（主运动是 REVOLUTE 绕竖直铰链转动；本类别主运动恒为水平 PRISMATIC 平移，无 hinge）。
- 不该混入：**Folding / Bi-fold / Accordion Door**（扇片间有铰链折叠 + 沿轨平移的复合运动；本类别扇片是刚性平移、扇间无 REVOLUTE 折叠）。
- 不该混入：**Garage / Roller / Sectional Door**（垂直升降或卷绕、绕过弯轨的多段链式运动；本类别是单一水平直线轨道、扇片不变形不卷绕）。
- 不该混入：**Pocket Door 墙袋（cassette）**（滑扇缩进墙内空腔，需墙体 cassette 几何；已 dropped 留作未来 kinematics 素材，当前不采样）。
- 不该混入：**Window / 推拉窗**（虽同为 PRISMATIC，但尺度/落地与门不同：sliding door 落地站地面 z=0、人可通行高度 ~2.0–2.4m；窗不落地）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 采纳 `rec_door_slide_5panel_tele` 的 helper 三件套（`_lane_y`/`_pane_center_x_closed`/`_add_leaf`）作为 multiplicity 复制基线；3p/4p parent 的手写滑扇统一改 `for i in range(N-1)` loop-emission。
- `_add_leaf` 应参数化 infill（注入 full-glass / `_add_muntin_grid` / `add_shaker_panel` / `_add_louver_slats`）与 handle（flush-bar / `_add_curved_handle` / D-loop / finger-pocket mesh）；finger-pocket 需 CadQuery（`_build_pocket_stile_cq` + `mesh_from_cadquery`），实现时确认 SDK CadQuery 可用，否则该 handle 候选 gating 关闭并记录。
- InterfaceSpec/MatingContract 重点：joint origin 落 closed-leaf-center（telescoping/bypass）或 `RAIL_BOTTOM_Z`（barn）；MatingContract = rail↔track（concealed）或 roller↔rail（barn）captured engagement。
- captured-pin overlap 用 element-scoped allow_overlap：concealed 的 `rail_top↔top_track`/`rail_bottom↔bottom_track`（或 `head/sill_track`）；telescoping nest 的 `pane_i↔pane_j` part-scoped allow_overlap（各扇 Y lane 分离）；barn 的 `roller_i↔rail_bar` contact。
- 暂不进入 seed domain 的组合：exposed_barn × (N>2 或 telescoping/center)、center-biparting × 奇数 N、center-biparting × 高 N（>4，需对称 per-side 扩展，留待后续）；这些由兼容矩阵 gating 回退默认。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B | N2_bypass / bypass | rec_door_slide_2panel | L74-L153, L161-L208, L210-L243 | bypass 运动学 + flush-bar handle 基线 |
| S2 | A | N3_tele | rec_door_slide_3panel_tele | L88-L142, L300-L321 | telescoping 共享 panel helper（手写扇→改 loop） |
| S3 | A | N4_tele | rec_door_slide_4panel_tele | L60-L112, L161-L167, L235-L261 | `_add_leaf` + track_rib loop + 3 telescoping joints |
| S4 | A/C/D/F | N5_tele (loop 标杆) | rec_door_slide_5panel_tele | L76-L145, L196-L207, L250-L281 | multiplicity 复制基线 + concealed track + full-glass + slim-black |
| S5 | A/B/E/F | N4_center / center-biparting | rec_door_slide_4panel_center | L96-L128, L131-L184, L321-L343 | bi-parting mimic + curved-C-pull + wide-white framing |
| S6 | A | N6_tele | rec_sliding_door_var_6panel_tele | L251-L281 | loop 外推到 N=6（证明任意 N） |
| S7 | C | exposed-barn-track-rollers | rec_sliding_door_var_barn_rail | L98-L103, L122-L178, L242-L257, L262-L274 | 外露 barn 轨 + 滚轮吊架 + 底导向 |
| S8 | D | muntin-grid-divided-lite | rec_sliding_door_var_muntin_grid | L66-L118 | 2×3 muntin 格 infill helper |
| S9 | D | solid-opaque-raised-panel | rec_sliding_door_var_raised_panel | L63-L96 | Shaker 实心面板 infill helper |
| S10 | D | slatted-louver | rec_sliding_door_var_slatted_louver | L66-L101 | 百叶 slat infill helper（for-i） |
| S11 | E | proud-D-loop | rec_sliding_door_var_d_loop_handle | L213-L247 | 凸圆管 D 环拉手 |
| S12 | E | flush-finger-pull-pocket | rec_sliding_door_var_flush_finger_pull | L64-L81, L84-L105 | CadQuery cutBlind 凹槽 mesh stile 拉手 |
</content>
</invoke>
