# garage_shutter — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `garage_shutter` |
| template path | `agent/templates/Door_Garage_shutter.py` |
| test path (optional) | `tests/agent/test_garage_shutter_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (multiplicity panel-stack with parallel decoration/frame children + an exclusive single-pivot TYPE) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (1 parent + 8 variants) |
| source_index_policy | only adopted module sources are indexed below |

阅读要点：

- **统一骨架。** 全部 9 个样本共享一个 `frame` 固定 root（`jamb_0/1`、`header`、`threshold`、两条 `guide_track_0/1`，parent L101-155）和同一组尺寸常量（`DOOR_W=2.40`、`OPENING_W=2.28`、`SLAT_D=0.04`、`PANEL_BASE_Z=THRESHOLD_H`，parent L53-76）。所有 panel-stack 样本的 leaf 都按 `for i in range(N_SLATS)` 循环发射（parent L166-194），命名 `slat_{i}`，顶叶 `slat_0` 通过 `frame_to_slat_0` FIXED 锚到 frame、其余叶 `slat_{i-1}_to_slat_{i}` 统一 +Z PRISMATIC、行程一个 pitch（parent L227-244）。这是模板的 multiplicity 主轴，parent 已 loop-emit，扩 N 只重调 `N_SLATS`/`SLAT_PITCH`（n3 L59-60、n10 L59-60）。
- **真正的拓扑变化轴有四条**（不计颜色/材质）：
  1. **N（panel/slat 复制数）**：6 (parent)、3 (n3，pitch 0.71)、10 (n10，pitch 0.213)、1 (tiltup_slab 单叶)。同骨架、同 joint 策略，仅叶数 + pitch 变。
  2. **TYPE（curtain lift kinematics）**：sectional_telescoping（parent，N≥2 叶 PRISMATIC 链）vs single_tilt_up（tiltup_slab，单 `door_leaf` 一个 REVOLUTE 顶部 hinge，L217-225）。两者运动 spine 不同且互斥。
  3. **SURFACE（per-leaf 面层）**：flat_embossed_pillow（parent，单 `panel_pillow`）、vertical_ribbed（ribbed，每叶 `rib_{r}` 循环 5 条横向波纹 L183-198）、raised_panel_field（sectional_panels，`panel_body`+inset `raised_field` L161-197）、perforated_grille（grille，`ExtrudeWithHolesGeometry` 网格 + `edge_rail_0/1` L90-136/L209-241）。面层改变 leaf 内部 part/visual 构成。
  4. **FRAME（surround/guide 几何）**：slim_surround（parent，扁平黑盒框 L101-155）vs bold_square_tube_rails（box_rails，`ExtrudeWithHolesGeometry` 空心方管 `guide_rail_{i}` + `track_channel_{i}` L97-152）。
  5. 另有 **WINDOW（顶叶玻璃行）**：no_windows（parent，实心叶）vs divided_lite_top_row（window_row，顶叶 `slat_0` 改成 5 个 `window_glass_{j}`+`mullion_{j}`+top/bottom rail，inlaid 在顶叶里 L197-236，下叶保留 pillow L237-245）。
- **WINDOW 与 SURFACE 是顶叶 vs 下叶的正交装饰**：window_row 只动 `slat_0`，下叶仍是 SURFACE。两者均为 leaf 内 inlaid parent visual，没有独立 FIXED joint（无活动小件）。
- **次级 inner-loop counts**：`N_WINDOWS`(5)、`n_ribs`(5)、`N_ROWS`(6，tiltup 浮雕行)、grille 的 `n_cols`/`n_rows`（由 `GRILLE_PITCH` 推导）。这些都不是模板主 multiplicity 轴，是面层/装饰内部 helper 数量。
- **intentional overlaps**：panel-stack 样本对相邻叶 `allow_overlap`（望远镜 nesting，parent L373-381）；window_row 额外对 `panel_field`↔`window_glass/mullion/rail` 同叶 allow_overlap（recess 嵌入，L447-476）；grille 薄片无相邻叶 overlap（edge_rail 面对面接触代替实心 lap，L335-348）；tiltup_slab 单叶无 overlap。

## 核心身份

garage_shutter 是一扇**车库门帘**：一个固定的钢质 surround `frame`（双 jamb + header + 地面 sill + 两条侧向 guide track）围住开口，开口内是一叠**水平**钢板/卷帘片，沿 track 向上抬升打开。默认成熟域是住宅级 sectional/telescoping 车库门（近正方形开口 ~2.4 m 宽 × ~2.1 m 高，黑框灰板，底叶带 latch handle），但模板覆盖整个家族：

- **运动学身份（必须保留至少一个真实非 FIXED joint）**：要么是 sectional/telescoping —— N 个刚性叶沿 +Z PRISMATIC 链望远镜式嵌套到固定顶叶后面；要么是 single tilt-up —— 单块刚性 canopy 板绕顶部 header hinge 一个 REVOLUTE 向外/向上翻起。颜色/材质永远不算结构变化。
- **几何身份**：水平叶横跨开口全宽、纵向铺满开口全高；顶叶固定、底叶坐在 sill 上、底叶带把手；叶面是压花 pillow / 横向波纹 / 凸起 raised-panel / 穿孔安全格栅之一；可选顶叶玻璃采光行。

不该混入的相邻类别见“与相邻类别的边界”。关键区分：本类是**水平片帘沿竖直 track 抬升**（或单板上翻），不是竖直滑移门、不是侧开 hinged 门、不是百叶窗。

## 槽位 + 候选模块表

模板有 5 个 slot。Slot N（multiplicity）与 Slot TYPE（kinematics）是结构主轴；Slot SURFACE / WINDOW / FRAME 是在 panel-stack 骨架上叠加的可替换层。所有 candidate 均来自已收敛 5★ 样本。

### Slot N：panel/slat multiplicity（复制数轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| six_panels | rec_door_garage_shutter (parent) | L59-L68（N/pitch）, L166-L194（叶 loop）, L227-L244（joint 链） | eligible if compatible | 6 叶望远镜栈，pitch 0.355，parent 基准 |
| three_panels | rec_garage_shutter_var_n3 | L59-L60（N=3/pitch=0.71）, L166-L194, L227-L244 | eligible if compatible | 3 块更高叶填满同一开口（pitch 加倍），叶数减半、joint 链短一节 |
| ten_slats | rec_garage_shutter_var_n10 | L59-L61（N=10/pitch=0.213/lap=0.012）, L166-L194 | eligible if compatible | 10 片窄卷帘式 slat，pitch 收窄、lap/groove 随之缩放 |
| single_slab | rec_garage_shutter_var_tiltup_slab | L48-L49（N_ROWS=6）, L175-L211（单 door_leaf）, L83-L102（浮雕行 helper） | eligible if compatible（仅与 single_tilt_up TYPE 共生） | N 坍缩为 1 块整叶，原本的 N 行浮雕变成叶内 inlaid `panel_pillow_{i}`/`seam_groove_{i}`，无 PRISMATIC 链 |

### Slot TYPE：curtain lift kinematics（运动学轴，互斥）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| sectional_telescoping | rec_door_garage_shutter (parent) | L227-L244（FIXED 顶叶 + 每节 +Z PRISMATIC，行程一个 pitch） | eligible if compatible | 刚性叶沿 +Z 望远镜嵌套到固定顶叶后；N≥2；与所有 SURFACE/WINDOW/FRAME 共生 |
| single_tilt_up | rec_garage_shutter_var_tiltup_slab | L217-L225（frame_to_leaf REVOLUTE，axis=(-1,0,0)，hinge 在 header，limits 0–1.3 rad）, L64-L65（HINGE_Z） | eligible if compatible（强制 N=1 single_slab，SURFACE/WINDOW 改为 reframe 到单板面） | 单整叶绕顶部 hinge 一个 REVOLUTE 向外+向上翻；取代 PRISMATIC 链，保留自己的真实非 FIXED joint |

### Slot SURFACE：panel face treatment（叶面层）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_embossed_pillow | rec_door_garage_shutter (parent) | L181-L186（单 `panel_pillow` proud slab） | eligible if compatible | 每叶一块凸起平 pillow（band 内 inset），最简面层、parent 基准 |
| vertical_ribbed | rec_garage_shutter_var_ribbed | L183-L198（`for r in range(n_ribs=5)` 横向波纹 `rib_{r}`） | eligible if compatible | 每叶 5 条平行横向波纹凸条取代单 pillow，inner-loop count `n_ribs` |
| raised_panel_field | rec_garage_shutter_var_sectional_panels | L161-L197（`panel_body` 凹边 + inset `raised_field` proud center） | eligible if compatible | 经典 raised-panel：凹陷 stile/rail 边框包住凸起中心 field；part 名变 `section_{i}`/`panel_body` |
| perforated_grille | rec_garage_shutter_var_grille | L90-L136（`ExtrudeWithHolesGeometry` 方孔网格 helper + `mesh_from_geometry`）, L209-L241（`grille_panel` + 全深 `edge_rail_0/1`） | eligible if compatible | 每叶薄穿孔安全格栅片（方孔网格 + 实心边框）+ 两条全深结构 edge rail 作为面对面望远镜接触链，替代实心 lap |

### Slot WINDOW：top window row（顶叶玻璃采光行）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| no_windows | rec_door_garage_shutter (parent) | L166-L194（全部叶按 SURFACE 实心发射） | eligible if compatible | 所有叶都是实心 SURFACE 面，无玻璃，parent 基准 |
| divided_lite_top_row | rec_garage_shutter_var_window_row | L70-L93（窗参数 `N_WINDOWS=5`/recess 等）, L197-L236（顶叶 `slat_0` 改为 5 个 `window_glass_{j}` + `mullion_{j}` + top_rail/bottom_rail）, L237-L245（下叶仍 SURFACE pillow） | eligible if compatible | 仅顶叶玻璃化成 5 格 divided-lite 凹陷采光窗（玻璃 recess + 竖 mullion + 上下 rail）；下叶不变 |

### Slot FRAME：surround / guide-rail style（围框/导轨样式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| slim_surround | rec_door_garage_shutter (parent) | L101-L155（扁平黑盒 `jamb_0/1`、`header`、`threshold` + flush `guide_track_0/1`） | eligible if compatible | 纤细扁平黑框 + 内嵌 galvanized flush guide track，parent 基准 |
| bold_square_tube_rails | rec_garage_shutter_var_box_rails | L97-L103（空心方管截面 helper）, L125-L135（`guide_rail_{i}` 空心方管 mesh）, L142-L152（`track_channel_{i}`）, L155-L171（header beam + 深 sill） | eligible if compatible | 90 mm 实凸空心方管导轨（`ExtrudeWithHolesGeometry`+`mesh_from_geometry`）站在开口两侧，内面带可见 track channel，header beam + 深 sill |

硬约束自检：每个 slot ≥2 candidate（N=4、TYPE=2、SURFACE=4、WINDOW=2、FRAME=2），无单 candidate slot，全部 candidate 有真实 `model.py:Lx-Ly`，candidate 间均为结构差异（不同 part tree / joint / primitive）。

## 槽位图（slot graph）

pattern: mixed —— Slot N 在 panel-stack TYPE 下做 multiplicity（loop-emit `slat_{i}`），Slot SURFACE/WINDOW/FRAME 作为 parallel children/visual 层叠加；Slot TYPE 的 single_tilt_up 分支是互斥的 single-pivot 子图。

```
                           frame (fixed root: jambs/header/threshold/guide tracks)
                              │
      ┌───────────────────────┴───────────────────────────┐
      │ TYPE = sectional_telescoping (panel-stack 子图)      │ TYPE = single_tilt_up (互斥子图)
      │                                                     │
   slat_0 ──[FIXED  @ (0, leaf_center_y(0), band_center_z(0))]──┐    door_leaf ──[REVOLUTE axis(-1,0,0)
      │                                                     │      │   @ (0, leaf_center_y, HINGE_Z), 0–1.3 rad]
   slat_1 ──[PRISMATIC +Z @ (0, +SLAT_D, -SLAT_PITCH), 0..pitch]   │   (单整叶绕 header hinge 上翻)
      │                                                     │      │
   slat_2 ──[PRISMATIC +Z 同上]                              │   N 坍缩为 1，原 N 行浮雕 = 叶内 inlaid
      │   ...                                                │   panel_pillow_{i}/seam_groove_{i}
   slat_{N-1} (底叶: latch_handle + handle_boss_0/1)         │
```

接口点位与 joint policy：

- **frame ↔ 顶叶（upstream interface）**：FIXED，origin `(0, _leaf_center_y(0), _band_center_z(0))`（parent L227-233）。顶叶前面 recess 在 frame front 后 0.02 m（`PANEL_FRONT_Y`，parent L74-75）；叶宽留 0.012 m 侧隙落在 guide track 内。single_tilt_up 时这条变为 frame↔door_leaf REVOLUTE（tiltup L217-225）。
- **叶 ↔ 叶（downstream interface / 望远镜链）**：每节 PRISMATIC，相对 origin `(0, +SLAT_D, -SLAT_PITCH)`，axis +Z，行程 `[0, SLAT_PITCH]`（parent L235-244）。下叶比上叶后退一个 `SLAT_D`、低一个 `SLAT_PITCH`，面对面接触；driving 全链到上限把所有叶嵌套到顶叶后、不超过 header。
- **叶内 SURFACE/WINDOW（同部件 visual）**：pillow/rib/raised_field/grille_panel 与 window_glass/mullion/rail 都挂在各自 `slat_{i}`（或 `section_{i}`）part 内，作为 parent visual，无独立 joint。grille 的 `edge_rail_0/1` 是结构 visual，承担相邻叶面对面接触（grille L335-348）。
- **FRAME（root visual 集合）**：slim_surround / bold_square_tube_rails 只替换 frame part 的 visual（jamb/rail/track/header/sill），不改 leaf 子图或 joint，与任何 panel-stack TYPE/SURFACE/WINDOW 正交共生。
- **互斥/可选**：TYPE=single_tilt_up 与 sectional_telescoping 互斥（不同 spine），且强制 N=1（single_slab），SURFACE/WINDOW 在该分支 reframe 到单板面；WINDOW=divided_lite_top_row 消费顶叶并叠加在 SURFACE 之上（顶叶玻璃化、下叶仍 SURFACE）。

## 每槽位 Module Emits / Interfaces

### Slot N / module six_panels（及 three_panels / ten_slats，同结构不同 N/pitch）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `slat_0..slat_{N-1}`（每叶含 `panel_field` + SURFACE visual + `seam_groove`），底叶 + `latch_handle`/`handle_boss_0/1` | parent L166-217 |
| internal joints | `frame_to_slat_0` FIXED；`slat_{i-1}_to_slat_{i}` PRISMATIC +Z（i=1..N-1） | parent L227-244 |
| upstream interface | 顶叶 FIXED 锚到 frame，origin `(0,_leaf_center_y(0),_band_center_z(0))` | parent L227-233 |
| downstream interface | 叶间 PRISMATIC，相对 origin `(0,+SLAT_D,-SLAT_PITCH)`，面对面 nesting + 相邻 allow_overlap | parent L235-244, L373-381 |

### Slot N / module single_slab（仅与 single_tilt_up 共生）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 单 `door_leaf`（`panel_field` 全高 + N_ROWS 行 inlaid `panel_pillow_{i}`/`seam_groove_{i}` + `latch_handle`/boss） | tiltup L175-211 |
| internal joints | 无叶间 joint（N=1）；浮雕行为同部件 visual | tiltup L186-187 |
| upstream interface | `door_leaf` 经 REVOLUTE 由 frame 驱动（见 TYPE） | tiltup L217-225 |
| downstream interface | 无（终端单叶） | tiltup L175 |

### Slot TYPE / module sectional_telescoping
| emits | 描述 | 来源 |
|---|---|---|
| internal joints | 顶叶 FIXED + 每节 +Z PRISMATIC，行程一个 pitch，effort 400/vel 0.30 | parent L234-244 |
| upstream interface | 消费 frame 顶部作为 FIXED 锚 | parent L227-233 |
| downstream interface | 望远镜链：全链开 → 叶嵌套到顶叶后、stack_top ≤ header | parent L347-367 |

### Slot TYPE / module single_tilt_up
| emits | 描述 | 来源 |
|---|---|---|
| internal joints | 单 `frame_to_leaf` REVOLUTE，axis (-1,0,0)，hinge 在 header line，limits 0–1.3 rad | tiltup L217-225 |
| upstream interface | hinge origin `(0, LEAF_CENTER_Y, HINGE_Z)`，HINGE_Z = 顶叶上沿/header | tiltup L61, L64-65, L222 |
| downstream interface | 翻开时 leaf 底沿向 -Y(前) 且 +Z(上) 摆出 | tiltup L301-330 |

### Slot SURFACE / 各 module
| emits | 描述 | 来源 |
|---|---|---|
| flat_embossed_pillow | 每叶单 `panel_pillow` proud slab | parent L181-186 |
| vertical_ribbed | 每叶 `rib_0..rib_{n_ribs-1}` 横向波纹凸条 | ribbed L183-198 |
| raised_panel_field | 每叶 `panel_body`(凹边) + `raised_field`(inset proud center)；part 名 `section_{i}` | sectional_panels L161-197 |
| perforated_grille | 每叶 `grille_panel`（ExtrudeWithHolesGeometry 方孔网格 mesh）+ `edge_rail_0/1`（全深结构接触条） | grille L90-136, L209-241 |
| interface | SURFACE visual 全部挂在各叶 part 内，proud/inset 相对 `panel_field`/`panel_body` 前面；grille 的 edge_rail 取代实心 lap 承担相邻接触 | grille L229-241, L335-348 |

### Slot WINDOW / 各 module
| emits | 描述 | 来源 |
|---|---|---|
| no_windows | 顶叶按 SURFACE 实心发射 | parent L166-194 |
| divided_lite_top_row | 顶叶 `slat_0`：`window_glass_0..4`（recess 玻璃）+ `mullion_0..3` + `top_rail`/`bottom_rail`；下叶仍 SURFACE | window_row L197-245 |
| interface | 玻璃 recess 在叶前面后 `WIN_RECESS`，mullion/rail 同 recess 内，需同叶 `panel_field`↔玻璃/mullion/rail allow_overlap | window_row L201-236, L447-476 |

### Slot FRAME / 各 module
| emits | 描述 | 来源 |
|---|---|---|
| slim_surround | frame visual：`jamb_0/1`、`header`、`threshold`、flush `guide_track_0/1` | parent L101-155 |
| bold_square_tube_rails | frame visual：`guide_rail_0/1`(空心方管 mesh)、`track_channel_0/1`、header beam、深 sill | box_rails L125-171 |
| upstream interface | frame 是 fixed root；提供顶部 FIXED/REVOLUTE 锚 + 两侧 guide + 底部 sill 承载 | parent L104-155 |
| downstream interface | sill 深度 `(STACK_BACK_Y+0.01)-FRAME_FRONT_Y` 覆盖全 depth-stagger 栈，底叶落钢 | parent L131-137 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `type_choice` | enum | `sectional_telescoping` / `single_tilt_up` | — | choice | deterministic procedural sampler 选；single_tilt_up 强制 `n_slats=1` 并切到 single_slab N module | TYPE 表 |
| `surface_choice` | enum | `flat_embossed_pillow` / `vertical_ribbed` / `raised_panel_field` / `perforated_grille` | — | choice | sampler 选；raised_panel_field 用 `section_{i}` 命名分支 | SURFACE 表 |
| `window_choice` | enum | `no_windows` / `divided_lite_top_row` | — | choice | sampler 选；conditional：仅 panel-stack TYPE 时作用于独立顶叶，single_tilt_up 时 reframe 到单板上带 | WINDOW 表 |
| `frame_choice` | enum | `slim_surround` / `bold_square_tube_rails` | — | choice | sampler 选；与 TYPE/SURFACE/WINDOW 正交 | FRAME 表 |
| `n_slats` | int | `[3, 14]`（panel-stack）；`=1`（single_tilt_up） | 6 | conditional | 上限随 TYPE：single_tilt_up→1；panel-stack 按加权抽 | parent L59, n3 L59, n10 L59 |
| `palette_style` | enum | `grey_steel` / `white` / `black_framed` / `dark_bronze` / `galvanized_silver` / `cream_almond` | `grey_steel` | choice | 仅改 material rgba，不改结构；≥3（目标 4-6 写实色板） | parent L94-99（材质表） |
| `opening_w_scale` | float | [0.85, 1.15] | 1.0 | independent | clamp；缩放 `OPENING_W`，叶宽/track 随之 | parent L58, L63 |
| `opening_h_scale` | float | [0.85, 1.20] | 1.0 | independent | clamp；缩放 `OPENING_H`（近正方形开口域） | parent L68 |
| `slat_pitch` | float | derived | — | equation | `= OPENING_H / n_slats`（panel-stack）；single_tilt_up 时 pitch=OPENING_H | parent L68, n3 L60, n10 L60 |
| `slat_lap` | float | [0.012, 0.025] | 0.020 | independent | clamp；窄 pitch 时偏小（n10=0.012） | parent L61, n10 L61, sectional_panels L58 |
| `slat_depth_scale` | float | [0.9, 1.2] | 1.0 | independent | clamp；缩放 `SLAT_D`（depth stagger），影响栈深 | parent L62 |
| `jamb_w_scale` | float | [0.8, 1.4] | 1.0 | independent | clamp；缩放 `JAMB_W`（slim_surround）/`RAIL_SIZE`（bold） | parent L54, box_rails L59 |
| `n_windows` | int | [3, 6] | 5 | conditional | 仅 window_choice=divided_lite_top_row 时有效；inner-loop count | window_row L73 |
| `n_ribs` | int | [3, 7] | 5 | conditional | 仅 surface_choice=vertical_ribbed 时有效；inner-loop count | ribbed L183 |
| `tilt_open_angle` | float | [1.0, 1.3] rad | 1.3 | conditional | 仅 single_tilt_up 时有效；REVOLUTE upper limit | tiltup L224 |
| (—) | constraint | — | — | inequality | `OPENING_H/n_slats ≥ slat_lap + 2·groove_h`（pitch 必须容得下 lap + seam，避免大 N 时叶高坍缩）；违反则下调 n_slats 或回缩 lap | parent L61, L166-194 |
| (—) | constraint | — | — | inequality | `STACK_BACK_Y = PANEL_FRONT_Y + n_slats·SLAT_D ≤ JAMB_D/2 缓冲内`（栈深不得穿出 frame 背面/guide track 深度）；违反则回缩 `slat_depth_scale` | parent L76, L141-142 |
| (—) | constraint | — | — | inequality | `n_windows·WIN_W + (n_windows-1)·MULLION_W ≤ SLAT_W`（窗行不得超叶宽）；违反则减 `n_windows` | window_row L82-83 |

采样契约（写进 `config_from_seed`/`resolve_config`）：先抽 enum（type→surface→window→frame，type 决定 N 域），再抽 `n_slats` 与 independent scale，按 `slat_pitch = OPENING_H/n_slats` 派生，最后用上面三条 inequality 投影/回缩；single_tilt_up 把 n_slats clamp 到 1 并解析 conditional（n_windows/n_ribs 仅在对应 choice 下生效）。

## Multiplicity / Copy Logic

本类有 **1 根模板主复制轴**（panel/slat 叶），外加若干面层 inner-loop count（不是独立 multiplicity 轴，随 SURFACE/WINDOW 内部 helper 数量走）。

**主轴：panel/slat 复制**

- `count_param`：`n_slats`（→ 常量 `N_SLATS`）。
- `N_range`：panel-stack 产品域 `[3, 14]`（近正方形开口，`pitch = OPENING_H / n_slats`；下限 3 来自 n3，上限 14 来自 pitch ≥ lap+seam 的下界与卷帘窄片家族）；single_tilt_up TYPE 把 N 坍缩为 `1`（single_slab，单整叶）。已覆盖 distinct N = {1, 3, 6, 10}。测试偏小（sweep 用小 N），产品全程到 14。
- sampling domain（权重档）：小 N 高频、大 N 稀有。建议 `3-6` 高频（住宅 sectional 主流，~60%）、`7-10` 中频（~30%，含卷帘式窄片）、`11-14` 低频尾部（~10%）；N=1 由 single_tilt_up TYPE 显式触发，不参与 panel-stack 加权抽样。
- copied object：每叶 `slat_{i}`（raised_panel_field SURFACE 下命名 `section_{i}`），含 `panel_field`/`panel_body` + SURFACE visual + `seam_groove`；底叶额外 `latch_handle`+`handle_boss_0/1`。
- naming：`slat_{i}`（i=0 顶叶/FIXED），`section_{i}`（raised_panel_field 分支）；joint `frame_to_slat_0`/`frame_to_section_0`、`slat_{i-1}_to_slat_{i}`/`section_{i-1}_to_section_{i}`。
- placement：竖直 band 堆叠，`_band_center_z(i)=PANEL_BASE_Z+OPENING_H-SLAT_PITCH·(i+0.5)`（顶叶 i=0 最高、底叶最低坐 sill）；depth stagger `_leaf_center_y(i)=PANEL_FRONT_Y+SLAT_D·i+SLAT_D/2`（每叶后退一个 SLAT_D，面对面）。下叶比 band 高出一个 lap（`field_h=SLAT_PITCH+SLAT_LAP`）塞到上叶背后，闭合无透光缝。
- joint policy：顶叶 `frame_to_slat_0` FIXED；其余 `slat_{i-1}_to_slat_{i}` PRISMATIC +Z、相对 origin `(0,+SLAT_D,-SLAT_PITCH)`、行程 `[0,SLAT_PITCH]`（telescoping）。single_tilt_up 分支换成单 REVOLUTE，无叶间链。相邻叶 `allow_overlap`（nesting 接触面），grille 改用 edge_rail 面对面接触。
- source/gating：parent 已 loop-emit（L166-194、L227-244），扩 N 只调 `N_SLATS`/`SLAT_PITCH`；single_tilt_up gate 强制 N=1。

**inner-loop counts（非主轴，conditional）**

- `n_windows`（divided_lite_top_row）：顶叶玻璃格数，`[3,6]` 默认 5，`window_glass_{j}`/`mullion_{j}`，受 `n_windows·WIN_W+(n_windows-1)·MULLION_W ≤ SLAT_W` 约束（window_row L73, L82-83, L205-236）。
- `n_ribs`（vertical_ribbed）：每叶横向波纹条数，`[3,7]` 默认 5，`rib_{r}`，band 内均布（ribbed L183-198）。
- grille 的 `n_cols`/`n_rows`：由 `GRILLE_PITCH` 从叶内尺寸推导，不直接暴露（grille L111-112）。
- `N_ROWS`（single_slab 浮雕行）：单叶上 inlaid 浮雕行数，跟 single_tilt_up 共生，默认 6（tiltup L48）。

## 拓扑多样性审计

总组合数：Slot N(panel-stack distinct 取 {3,6,10,14} 计 4，加 single_tilt_up 的 N=1) × Slot TYPE × Slot SURFACE × Slot WINDOW × Slot FRAME。
- panel-stack 主域（TYPE=sectional_telescoping）：N(4 distinct, 实际可到全程 [3,14]) × SURFACE(4) × WINDOW(2) × FRAME(2) = 64 distinct topology classes（按 distinct N 计；按全 N 范围更多）。
- single_tilt_up 分支：N=1 × SURFACE(4, reframe 到单板) × WINDOW(2) × FRAME(2) = 16。
- 合计 ≥ 80 distinct topology classes（不含连续 N 与 scale 带来的细分）。

理由：仅 SURFACE(4) × distinct-N(4) = 16 ≥ 10 已满足最低门槛（源 map GATE P1 已核），TYPE/WINDOW/FRAME 三轴再放大到 ≥80。所有组合均来自 on-disk 收敛样本或其正交叠加，无需 gap fork。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed` 对普通 seed 用 deterministic procedural sampling —— 先抽 `type_choice`（panel-stack 高频、tilt-up 低频），type 决定 N 域；panel-stack 时按权重档抽 `n_slats`，single_tilt_up 强制 N=1+single_slab；再抽 `surface_choice`/`window_choice`/`frame_choice`（各自均匀或轻加权），最后抽 independent scale 并按三条 inequality 回缩。compatibility matrix 阻止非法组合（见下）。`palette_style` 独立抽，仅改材质。少量 regression overrides 仅用于已知失败回归（首版无，留空）。random sweep：seeds 0-49 初轮（早停诊断），0-999 成熟度审计 + viewer 目检。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类 distinct N 全程 [3,14]（12 个）× 4 SURFACE × 2 WINDOW × 2 FRAME = 192（panel-stack）+ 16（tilt-up），低于 300 时记录类别离散空间上限；不设门。

Controlled local parameterization：初版模板包含关键连续 scale —— `opening_w_scale [0.85,1.15]`、`opening_h_scale [0.85,1.20]`、`slat_lap [0.012,0.025]`、`slat_depth_scale [0.9,1.2]`、`jamb_w_scale [0.8,1.4]`，全部在 `resolve_config` clamp；`slat_pitch = OPENING_H/n_slats` 为 equation 派生（不独立抽）；跨部件依赖（pitch≥lap+seam、栈深≤frame 背、窗行≤叶宽）为 inequality 在 resolve 投影。这些 scale 只改安全比例，不破坏 FIXED/PRISMATIC/REVOLUTE 接口、guide track 承载或类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | type→N(域随 type)→surface→window→frame→scale；权重档：小 N/panel-stack 高频 | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | single_tilt_up ⇒ N=1+single_slab（互斥 PRISMATIC 链）；divided_lite_top_row 消费顶叶（panel-stack）或 reframe 单板（tilt-up）；perforated_grille 用 edge_rail 接触链替代实心 lap；FRAME 与 TYPE/SURFACE/WINDOW 正交 | 无 floating/穿模/joint 轴错/closed-pose 超 header/大 N 叶高坍缩/可选顶叶玻璃失败 |
| controlled local variation | 5 个 clamp scale + equation pitch + 3 条 inequality | 比例变化不破坏接口、clearance、sill 承载、joint origin、类别 identity |
| regression overrides | none（首版） | 仅已知失败回归或审核指定样本 |
| random sweep | seeds 0-49 初轮、0-999 成熟度 | 与 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| N | 4 | yes | yes | {1, 3, 6, 10} distinct，产品域 [3,14]+tilt N=1 |
| TYPE | 2 | yes | no | sectional_telescoping / single_tilt_up；运动学互斥，2 个已足 |
| SURFACE | 4 | yes | yes | pillow / ribbed / raised_panel / grille |
| WINDOW | 2 | yes | no | no_windows / divided_lite_top_row；正交装饰，2 个已足 |
| FRAME | 2 | yes | no | slim_surround / bold_square_tube_rails；正交围框，2 个已足 |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名 `(slot, module)`（N/TYPE/SURFACE/WINDOW/FRAME）。
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling；seed=0 不特殊。
- compatibility matrix / gating 阻止非法组合：single_tilt_up 必须 N=1+single_slab；divided_lite_top_row 在 panel-stack 作用顶叶、在 tilt-up reframe 单板；grille 用 edge_rail 接触链。
- optional regression overrides 稀少且有理由（首版 none）。
- 不把小型 curated/modulo 表当主 seed domain。
- 受控 scale（opening_w/h、lap、depth、jamb）均 clamp，pitch 由 equation 派生，三条 inequality 在 `resolve_config` 求解，不留到 builder 才失败。
- 关键 InterfaceSpec/MatingContract 存在：顶叶 FIXED 锚、叶间 PRISMATIC 链面对面、底叶坐 sill、guide track 覆盖全 depth-stagger、tilt-up REVOLUTE hinge 在 header。
- 关键 joint type/axis/range：PRISMATIC axis +Z 行程 `[0,SLAT_PITCH]`；REVOLUTE axis (-1,0,0) 行程 `[0,~1.3]`；顶叶/单叶上锚 FIXED/REVOLUTE。
- copied object 遵循命名/placement：`slat_{i}`/`section_{i}` band 堆叠 + depth stagger，底叶带 handle。

## Reject cases

- 大 N 时 `pitch = OPENING_H/n_slats` 小于 `slat_lap + 2·groove_h`，叶高坍缩/lap 透光缝（必须用 inequality 回缩 n_slats 或 lap）。
- single_tilt_up 仍发射 N≥2 叶或叶间 PRISMATIC 链（运动学混叠，必须 gate 成 N=1 单 REVOLUTE）。
- depth-stagger 栈深 `n_slats·SLAT_D` 穿出 frame 背面/超 guide track 深度，导致后叶悬空或穿模。
- divided_lite_top_row 窗行宽 `n_windows·WIN_W+(n_windows-1)·MULLION_W` 超过 `SLAT_W`，mullion/玻璃溢出叶边。
- 望远镜全开后 stack_top 超过 header line（叶探出框顶），或下叶未清空开口下半。
- perforated_grille 丢失 `edge_rail_0/1` 接触链 → 相邻薄片无面对面承载、telescoping 链断（不能照搬实心 lap 检查）。
- 把 palette/材质当独立 slot 或当结构变化（颜色不算 candidate）。
- 顶叶/单叶 FIXED/REVOLUTE 锚 origin 错位（顶叶不在 band_center、hinge 不在 header），导致闭合姿态叶不铺满开口或翻转方向反。

## 与相邻类别的边界

- 不该混入：**Door / 普通竖直滑移门 或 侧开 hinged 门**（理由：本类是水平片帘沿竖直 track 抬升或单板顶 hinge 上翻；竖直滑移/侧开是不同 spine 与接口，guide track 与 telescoping 链语义不适用）。
- 不该混入：**Window / 百叶窗 (blinds/shutter slats)**（理由：百叶是可旋转倾角的细条窗饰、绕各自水平轴 REVOLUTE，本类叶是 +Z PRISMATIC 抬升的承重门板，运动轴与承载语义不同）。
- 不该混入：**Roller / 卷帘门连续帘片绕顶鼓卷收（roller_coiling）**（理由：连续帘片绕顶部 barrel drum 单 REVOLUTE 卷收是另一种 TYPE，未在 on-disk 收敛集中，暂排除在 candidate 之外，仅记为未来 compatibility 素材）。
- 不该混入：**Fence / 栅栏 cascade 等其它水平多叶复制类**（理由：虽同为 multiplicity 多叶，但栅栏无 frame 开口/telescoping 抬升/sill 承载，根坐标与接口完全不同）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- N module（six/three/ten panels）共享一个 leaf-loop helper（`_band_center_z`/`_leaf_center_y` + `for i in range(N_SLATS)`），parent 已 loop-emit；扩 N 只调 `N_SLATS`/`SLAT_PITCH`。raised_panel_field 用 `section_{i}` 命名分支（与 `slat_{i}` 等价拓扑，仅命名 + part 内 visual 不同）。
- SURFACE 改的是叶内 visual 块，可做 `_emit_surface(slat, surface_choice, ...)` 分发；grille 需 `ExtrudeWithHolesGeometry`+`mesh_from_geometry` 并 `rotate_x(pi/2)` 旋到 XZ 面（grille L130-136），其 `edge_rail_0/1` 取代实心 lap 作为相邻接触链——测试 depth-stagger 时对 grille 用 `edge_rail` 而非 `panel_field`。
- FRAME 改的是 frame part 的 visual 集合，bold_square_tube_rails 需空心方管 helper（box_rails L97-103）+ `track_channel`，header/sill 几何随之调整；与 leaf 子图正交。
- allow_overlap 须 element-scoped：panel-stack 相邻叶 nesting（parent L373-381）、window_row 同叶 `panel_field`↔玻璃/mullion/rail（window_row L447-476）；grille 与 tilt-up 不发相邻叶 overlap。
- single_tilt_up 与 sectional_telescoping 互斥子图：可暂只在已实现且测试覆盖的稳定子域采样；若 single_tilt_up × 复杂 SURFACE/WINDOW 组合不稳，先收窄该分支组合再逐步放开。
