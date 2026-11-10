# Bag_Suitcase / Box — Modular Spec

> 来源小类：`picture/Bag_Suitcase/Box/001.png`（articraft_data 上游 rustic 木箱小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Bag_Suitcase__Box.md`。
> **同步前置**：本 spec 引用的 `model.py:Lx-Ly` 来自 1 个 parent + 20 个 workbench-only 五星变体（批次 `bag_suitcase_box_gpt55_20260611`，openai / gpt-5.5 / med，全部 compile rc=0、均有 URDF、非 fixed joint 1–4 个），目前都在 `articraft_data` 仓库，尚未同步进本仓库 `data/records/`。进入实现前需先把被采纳的 record 目录 + 物化缓存同步进本仓库 `data/records/` 并批量 `rating=5`（FORK_VARIANTS §7）。**下表行号按 articraft_data 当前 `revisions/rev_000001/model.py` 计；同步进 arti-template 后会 rebase**。

## 元信息
| 项 | 值 |
|---|---|
| slug | `bag_suitcase_box` |
| template path | `agent/templates/Bag_Suitcase_Box.py` |
| test path (optional) | `tests/agent/test_bag_suitcase_box_template.py`（不写，sweep 为唯一验收） |
| stage | `SPEC_ONLY`（pending review） |
| status | `spec_only` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots 挂到共同 box_body chassis；无 multiplicity） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 21（1 parent `1a9c91ba` + 20 fork 变体 v01–v20，全部 converged，workbench-only） |
| read_count | 12（parent 全文 + 提供独立结构 module 的 11 个变体：v02/v03/v04/v17/v19 lid，v05/v07/v12/v16 hardware，v13/v14/v18 interior；v06/v20 interior 基座与 v15/v08 chamfer/round-cap 经 grep 核对结构标记） |
| read_scope | 提供 module 来源的样本全部读；纯比例/装饰格子（v01 low_wide、v09 shallow_tray、v10 ribbed、v11 weathered）按 source map 判定为同 skeleton 比例/seam 样本，grep 核对结构标记后采纳为对应 slot 的轻量 candidate，不再全文重读 |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表（见 §14） |

冗余说明：
- v01（low_wide）、v09（shallow_tray，HB=0.085）、v15（beveled_corner_posts）等的 part tree 与 parent 全等（`box_body` + `box_lid` + `hasp`，REVOLUTE 后铰平盖），仅改 W/D/HB 比例或角件几何 → 归入 body_form / wall_style 的形态 candidate，不是新 lid_closure。
- v02/v03 的 "tall_upright / square_squat" 体形与其 lid 变体同体（source map line 34）：写 spec 时按 headline 轴（lid_closure）归 module，体形作 body_form 比例/形态样本，避免连续尺寸虚胖（FORK_VARIANTS §2）。

## 核心身份

一只**储物箱 / 木箱 / 小柜（storage box / chest）**：一个矩形（或切角 / 长窄 / 浅托盘 / 立式）单体箱壳，板条侧壁 + 金属角件，由**一个主开合机构（lid_closure）**封口。主机构是本类别身份：后铰平盖、前壁下翻 drop panel、顶盖双叶、侧槽滑出顶板、前面立轴开门、或拱顶后铰盖。箱体可带把手（绳把 / 可转提梁 / 可转环把）+ 闩扣（hasp / 旋转卡扣 / 旋转 hasp 板），内部可带附加机构（抬高脚 / 前抽屉 / 升降内托 / 滑动隔板 / 嵌套脚）。默认成熟域：边长 ~0.2–0.8 m 的单体箱，至少 1 个非 fixed joint（主机构）。

不该混入：带可伸缩拉杆 + 轮的拉杆箱（`rolling_toolbox_with_telescoping_handle`）、明确的钓具盒只有简单单铰盖（`tackle_box_with_simple_hinged_lid`，结构过窄、无 slot 多样性）、家电壳体（`chest_freezer_with_hinged_lid` 制冷柜、`box_fan_with_control_knob` 风扇）、行李箱 / 软包 suitcase（壳 + 拉链 + 万向轮，非本木箱形态）。

## 槽位 + 候选模块表

> **建模注记**：5 个 slot 不是串联链——`body_form`/`wall_style`/`hardware`/`interior_base` 都把自己的 part/visual 挂到**共同的 `box_body` 根**（parallel_children）。唯一真正的活动主轴是 `lid_closure`，它决定主 joint 的 type/axis/origin；其余 slot 各自贡献 0–N 个独立子件（把手 pivot、闩扣 hinge、内部 prismatic 机构）。slot 之间通过共享的 `box_body` mating face（顶 rim / 前面 / 侧面 / 底面）装配。

### Slot A：lid_closure（主机构槽——盒体的开合动作，决定主 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| hinged_flat_top（基线） | parent `1a9c91ba` | L84-127 | eligible if compatible | 后沿平盖 `box_lid` REVOLUTE ×1（axis −X，origin 顶后边 `(0,D/2,HB)`）+ 前 hasp 子铰 |
| front_drop_panel | v02 `0bad30bc` | L106-136 | eligible if compatible | 固定顶 rim/rail + 前壁 `drop_panel` 沿下前边 REVOLUTE 下翻（axis +X，origin `(0,-(D/2+T/2),RAIL)`），bottom_hinge_leaf captured 在 lower rail |
| split_double_leaf_top | v03 `052ac6c9` | L85-163 | eligible if compatible | 顶盖两叶 `front_lid_leaf`/`rear_lid_leaf`，沿前/后 rim 各一 REVOLUTE（axis ±X），中缝 4–8 mm seam |
| sliding_top_panel | v04 `f1d22421` | L66-133 | eligible if compatible | 侧槽 runner+lip+web + front_stop，`sliding_lid` 沿 +Y **PRISMATIC** 滑出（**唯一 PRISMATIC 主拓扑**） |
| hinged_front_door | v17 `f8e00598` | L108-149 | eligible if compatible | 固定顶板 + 前框 sill/header/jamb + 交错 hinge knuckle，`front_door` 立轴 REVOLUTE（axis −Z）侧开 + door 上 hasp 子铰 |
| arched_curved_top | v19 `0ee48866` | L28-58, L150-184 | eligible if compatible | helper `_arched_lid_mesh`（barrel-top MeshGeometry）+ 后铰板/barrel，拱顶 `box_lid` REVOLUTE（axis −X）+ 前 hasp 子铰 |

### Slot B：body_form（箱体形态/比例——挂到 box_body，不改主 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rectangular_standard（基线） | parent `1a9c91ba` | L31-43 | eligible if compatible | 标准矩形 floor+4 wall，W/D/HB≈0.50/0.34/0.24 |
| low_wide | v01 `53ef4fa4` | L34-124（grep 核对，part tree 同 parent） | eligible if compatible | 低矮加宽 W=0.72/HB=0.16，厚 plank 带 + 大角帽（比例 + seam 形态） |
| long_narrow_rounded_ends | v08 `e12ddd40` | L34-108（grep：`end_*_round` 圆端帽 cylinder/rim L48-65） | eligible if compatible | 长窄 W=0.82/D=0.24 + 金属圆端帽 rims/edge rolls |
| shallow_tray | v09 `0becfb46` | L33-85（grep：HB=0.085 + clear_acrylic 展示盖 L30/L86+） | eligible if compatible | 浅托盘式 HB=0.085，低侧壁 + 透明展示盖（acrylic material） |
| beveled_corner_posts | v15 `094c6b13` | L50-66（grep：`mesh_from_cadquery`+`.chamfer()` chamfer_post L53-58） | eligible if compatible | cadquery 切角角柱 `chamfer_post_i` 替方角铁 + beveled lid + round keeper 闩 |

### Slot C：wall_style（壁面/表面样式——挂到 box_body 外表面）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| plank_sides（基线） | parent `1a9c91ba` | L45-62 | eligible if compatible | 横/竖 plank seam + iron corner bracket ×4 + vertical batten |
| ribbed_vertical_slats | v10 `02fc6fb9` | L53-78（`front_slat_i`/`side_slat_*_i` 循环竖向板条 + 顶底 rail） | eligible if compatible | 竖向 slat 板条（循环发射 ~9/面）+ 上下加强 rail 捆绑 |
| weathered_crate_corner_blocks | v11 `4dcfee7f` | L38-78（dark 背板 + `corner_block_i` 凸角块 L78） | eligible if compatible | 风化板条箱：dark recessed backing 凸板 + 4 raised corner block |
| reinforced_metal_straps | v16 `433dd9d3` | L62-93 | eligible if compatible | 深色加固箱：环身 iron strap band（上/下 × 前/后/左/右）+ vertical strap，blackened palette |

### Slot D：hardware（把手 + 闩/扣 两个子轴——子件挂到 box_body 侧/前面）

> 子轴 D1=handle、D2=latch。两者各自独立选，挂在 box_body 不同面。下表合并列出。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| D1 rope_side_handles（基线） | parent `1a9c91ba` | L64-77 | eligible if compatible | 两端 staple + rope cylinder，**无 joint，parent visual** |
| D1 swing_bail_handle | v07 `b6be553b` | L63-81, L103-133 | eligible if compatible | side_bracket+pivot_boss + `bail_handle` REVOLUTE（axis +X，origin `(0,0,pivot_z)`）提梁，captured-pin allow_overlap |
| D1 rotating_side_rings | v16 `433dd9d3` | L95-116, L148-176 | eligible if compatible | TorusGeometry 环把 ×2，各 `ring_handle_i` REVOLUTE（axis +Y），8 条 captured-pin allow_overlap |
| D2 hasp_latch（基线） | parent `1a9c91ba` | L79-82, L109-127 | eligible if compatible | 前 hasp_keeper + `hasp` 子铰 REVOLUTE（axis +X，挂在 lid 上）抬起释放 |
| D2 rotating_clasp_latch ×2 | v05 `e1b5c35d` | L95-99, L127-146 | eligible if compatible | 两 clasp_keeper + `clasp_i` ×2 REVOLUTE（axis +X，挂在 lid）旋转释放 |
| D2 rotating_hasp_plate | v12 `9f64bd44` | L77-89, L114-134 | eligible if compatible | keeper 组 + `hasp` 板沿**前面平面立轴** REVOLUTE（axis +Y）旋转避让（lockbox 钢箱身份） |

### Slot E：interior_base（内部机构 / 底座附加——挂到 box_body 内/底）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| plain（基线） | parent `1a9c91ba` | —（无内部件） | eligible if compatible | 无内部机构 |
| raised_feet | v06 `7a4c1a2b` | L50-79 | eligible if compatible | jewelry-box 4 抬高脚 block + 浅内 tray lip 四边 ledge（无 joint，parent visual） |
| slide_out_front_drawer | v13 `427708e5` | L104-114, L161-194 | eligible if compatible | drawer runner + `front_drawer` 沿 −Y **PRISMATIC** 拉出；body 前面重建为 sill/stile/rail drawer 开口 |
| lift_out_inner_tray | v14 `01472062` | L71-87, L134-179 | eligible if compatible | inner cleat ×4 + `lift_tray` 沿 +Z **PRISMATIC** 垂直升降（double-depth 箱） |
| sliding_internal_divider | v18 `2825c67d` | L88-103, L150-187 | eligible if compatible | divider rail 前后 + `divider_panel` 沿 ±X **PRISMATIC** 左右滑动 |
| nesting_stackable_feet | v20 `aedc9476` | L41-68 | eligible if compatible | 4 nesting_foot block + 凹底 recess outline（可叠特征，无 joint，parent visual） |

硬约束记录：每个 slot 均 ≥3 candidate（D 拆 D1×3 + D2×3），无低于 2 的 slot；全部来自被采纳五星样本，无 1-candidate 槽。

## 槽位图（slot graph）

pattern: `parallel_children`（共同 root = `box_body`）

```
                       box_body  (root, 由 body_form × wall_style 参数化)
                          │
   ┌──────────────┬───────┴────────┬──────────────────┬─────────────────┐
   │ lid_closure  │ D1 handle      │ D2 latch         │ E interior      │ (wall_style 为 box_body 表面 visual)
   ▼              ▼                ▼                  ▼
 main lid/door  bail/ring        hasp/clasp/plate   drawer/tray/divider
 REVOLUTE 或     REVOLUTE         REVOLUTE           PRISMATIC（drawer/
 PRISMATIC      （或纯 visual）    （挂在 lid）         tray/divider）或纯 visual
 （挂在 body）                                         （挂在 body）
```

接口点位与 joint 语义：
- **lid_closure → box_body**：顶 rim（hinged_flat_top / split / arched 沿顶后/前边）、前面下边（front_drop_panel）、侧槽 runner（sliding_top_panel +Y PRISMATIC）、前面立柱（hinged_front_door −Z REVOLUTE）。joint origin 锚在真实铰链硬件 / 滑槽上，axis 见候选表。rest pose=closed（q=0 盖合在 body rim，留 0–6 mm gap）。
- **D2 latch → lid**（注意：hasp/clasp/plate 的 parent 是 `box_lid`，**不是 body**，所以 latch 子轴依赖 lid_closure 选了带 lid 的 module）。当 lid_closure=sliding_top_panel（无 hinged lid part）或 front_drop_panel / hinged_front_door（lid 形态不同）时，latch 需 gating（见 §10 compatibility matrix）。
- **D1 handle → box_body**：side_bracket/clevis pivot（bail +X、ring +Y）；rope 纯 visual。
- **E interior → box_body**：drawer −Y、tray +Z、divider ±X 各一 PRISMATIC，captured 在对应 runner/cleat/rail；raised_feet / nesting_feet 纯 visual 挂底面。
- **mating policy**：captured-pin（bail pivot pin↔boss、ring↔clevis、drop_panel hinge leaf↔rail、round hasp↔keeper）省略 MatingContract（grandfather），由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 overlap（来源样本已逐条声明，见 v07/v16/v05/v15 的 `ctx.allow_overlap`）。
- **互斥/派生**：见 §10。

## 每槽位 Module Emits / Interfaces

### Slot A / lid_closure（以 hinged_flat_top 为例）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `box_lid`（visuals: `lid_panel`/`lid_strap_*`/`hasp_mount`） | parent L84-97 |
| internal joints | `lid_hinge` REVOLUTE，axis(−1,0,0)，origin `(0,D/2,HB)`，range [0,2.1] | parent L99-107 |
| upstream interface | 顶后边 rim（消费 box_body 的 `wall_back` 顶面） | parent L99-107 |
| downstream interface | lid 前边 → 携带 D2 latch（`hasp_mount`，latch hinge 挂此处） | parent L94-97 |

（sliding_top_panel 改为 PRISMATIC `lid_slide` axis(0,1,0) + 侧 runner/lip 挂 body；hinged_front_door 改为 REVOLUTE `door_hinge` axis(0,0,-1) + 固定 top_panel；split 发 2 个 leaf part + 2 hinge；arched 用 `_arched_lid_mesh` helper。）

### Slot D1 / swing_bail_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bail_handle`（top_grip + side_arm + pivot_pin），body 上 side_bracket/lug/pivot_boss visual | v07 L63-81, L103-123 |
| internal joints | `bail_pivot` REVOLUTE，axis(1,0,0)，origin `(0,0,pivot_z)`，range [0,1.4] | v07 L125-133 |
| upstream interface | 两侧 box_body 侧面 pivot_boss（captured-pin） | v07 L76-81 |
| downstream interface | 无（终端把手） | — |

### Slot E / slide_out_front_drawer
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_drawer`（face+floor+sides+back+pull），body 上 drawer_runner_l/r + 前面 sill/stile/rail 开口 | v13 L104-114, L161-184 |
| internal joints | `drawer_slide` PRISMATIC，axis(0,-1,0)，range [0,0.145] | v13 L186-194 |
| upstream interface | body 前面 drawer 开口（重建 front_sill/stile/rail）+ 内 runner | v13 L40-56, L104-114 |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| lid_closure | enum | hinged_flat_top / front_drop_panel / split_double_leaf_top / sliding_top_panel / hinged_front_door / arched_curved_top | — | choice | deterministic sampler；编入 slot_choice（joint-type 区分拓扑） | module table |
| body_form | enum | rectangular_standard / low_wide / long_narrow_rounded_ends / shallow_tray / beveled_corner_posts | — | choice | sampler 选 | module table |
| wall_style | enum | plank_sides / ribbed_vertical_slats / weathered_crate_corner_blocks / reinforced_metal_straps | — | choice | sampler 选 | module table |
| handle_style (D1) | enum | rope_side_handles / swing_bail_handle / rotating_side_rings | — | choice | sampler 选 | module table |
| latch_style (D2) | enum | none / hasp_latch / rotating_clasp_latch / rotating_hasp_plate | — | conditional | 仅当 lid 有 hinged top/door 时可选非 none；见 §10 gating | module table |
| material_style | enum | rustic_wood / blackened_travel / weathered / painted_steel | — | palette | palette only，**不计入 slot_choice** | palette（v11/v16/v12） |
| box_w / box_d / box_h_scale | float | W∈[0.30,0.82]、D∈[0.20,0.40]、HB∈[0.085,0.58] | parent 名义 | independent | 在范围内独立采样后 clamp；按 body_form conditional 收窄（见下） | parent L15-17 |
| wall_thickness T | float | derived | 0.018 | equation | `= clamp(0.012, 0.018)`，随 body_form（lockbox/小箱用 0.010–0.012） | 各样本 L18-19 |
| lid_thickness LID_T | float | derived | 0.040 | equation | `= f(box_h)`，浅托盘/小箱按比例缩 | 各样本 |
| joint_range_scale | float | [0.85, 1.05] | 1.0 | independent | 每主 joint `motion_limits` clamp（基线 lid 2.1 / drawer 0.145 / tray 0.140 / divider 0.155） | 各样本 |
| (—) | constraint | — | — | conditional | `box_h ∈ body_form 的合法带`（shallow_tray HB≤0.10、low_wide HB≤0.18、立式 ≤0.58）；先解析 body_form 再采 box_h | body_form |
| (—) | constraint | — | — | inequality | drawer/tray/divider 行程 ≤ 内腔可用尺寸（`travel ≤ inner_dim − part_dim − clearance`）；违反则回缩行程 | v13/v14/v18 |

连续尺寸采样契约：先解析 body_form（conditional 收窄 box_h 带）→ 采 independent 主尺度（box_w/d/h、joint_range_scale）→ 派生 T/LID_T（equation）→ 用 inequality 把 interior 行程投影回内腔可行域。所有 scale 在 `resolve_config` clamp/派生，绝不改 slot enum 选择或 joint type。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（box_body / lid / handle / latch / interior）表达，box 是单体，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。
- 说明：v20 的"嵌套脚 + 凹底 recess"只是可叠特征（4 个固定脚），v05 的双 clasp / v16 的双 ring / v10 的 ~9 条 slat 都是 module 内部固定数量的局部循环，**不是模板级 N-复制轴**（数量不进 slot_choice，不加权采样）。source map line 64-67 同此判定。

## 拓扑多样性审计

总组合数（不含 palette、不含连续 scale）：
lid_closure(6) × body_form(5) × wall_style(4) × handle_style(3) × latch_style(≈3 有效，受 gating) × interior(6)
= 6 × 5 × 4 × 3 × 3 × 6 = **6480**（gating 后仍 ≫ 10）。


理由：`slot_choices_for_seed` 返回 `(lid_closure, body_form, wall_style, handle_style, latch_style, interior_base)` 六元组；6480 个合法 distinct 组合远超 10。sliding_top_panel 的 PRISMATIC 主 joint 与 5 个 REVOLUTE module 是不同拓扑等价类（joint type 不同），不会被 distinct 折叠。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 加权采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 顺序 = 先 `rng.choice` lid_closure → 据 lid_closure gating 决定 latch_style 合法子集（见下）→ `rng.choice` body_form / wall_style / handle_style / interior_base → 解析 body_form 的 box_h conditional 带 → 采 independent 主尺度 → 派生 T/LID_T → inequality 投影 interior 行程。compatibility matrix 排除非法 latch/lid 组合与 body_form/interior 干涉（见 §10）。无 regression override（首版）。random sweep：seeds 0-49 初轮、0-999 成熟审计。

Topology target：1000-seed slot choice tuple distinct 预计按 ≥300 富类别口径观察（理论上限 6480；真实采样 1000 seed 应见数百个 distinct 六元组）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：关键 scale = box_w / box_d / box_h（受 body_form conditional 带约束）、wall_thickness T（equation 派生）、lid_thickness LID_T（equation）、joint_range_scale（independent，每主 joint clamp）、interior travel（inequality 投影内腔）。全部 `resolve_config` clamp/派生，不破坏 lid mating face、latch 挂载点、interior captured 接口或类别身份。按 §7 约束类型声明依赖；遵循采样契约（conditional→independent→equation→inequality）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | lid_closure 先选 → gating latch → 选 body/wall/handle/interior → 解析 box_h 带 → 采尺度 → 派生 → 投影行程 | slot_choices_for_seed 六元组与 build 一致、含 PRISMATIC 维度 |
| compatibility matrix | latch 依赖 lid 有 hinged top/door；sliding_top_panel→latch=none；front_drop_panel/hinged_front_door→latch∈{none, 各自原生 hasp}；shallow_tray 不配深 interior（drawer/tray）；rotating_hasp_plate 偏 lockbox/painted_steel | 无 floating latch、无 lid 缺失时挂 hasp、无浅箱塞深抽屉穿模 |
| controlled local variation | box_w/d/h + T/LID_T + joint_range + interior travel，全 clamp/派生 | 比例变化不破坏 lid seat gap、latch 对位、interior captured、脚贴地、类别身份 |
| regression overrides | none | — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 module captured-pin allow_overlap + closed-pose seat |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| lid_closure | 6 | yes | yes | 含 1 PRISMATIC + 5 REVOLUTE，joint-type 多样 |
| body_form | 5 | yes | yes | 比例/角件形态 |
| wall_style | 4 | yes | yes | 表面 visual 族 |
| handle_style (D1) | 3 | yes | yes | rope(纯visual)/bail/ring |
| latch_style (D2) | 4（含 none） | yes | yes | conditional gating by lid |
| interior_base | 6 | yes | yes | 3 PRISMATIC + 3 纯 visual |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名的六元组 `(lid_closure, body_form, wall_style, handle_style, latch_style, interior_base)`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` clamp box_w/d/h 到 body_form 合法带，派生 T/LID_T，投影 interior travel 到内腔，clamp joint_range_scale
- compatibility matrix / gating 阻止非法 lid×latch、shallow×深 interior 组合
- controlled local scale clamp 后不破坏 lid seat gap、latch 对位、interior captured 接口、joint origin、类别身份
- cross-part scale 依赖（box_h conditional、interior travel inequality、T/LID_T equation）在 `resolve_config` 解析，不留到 builder
- 关键 joint type/axis/range：lid_closure 主 joint（REVOLUTE 或 PRISMATIC 按 module）、latch 子铰 REVOLUTE、interior PRISMATIC
- captured-pin（bail pivot↔boss、ring↔clevis、drop_panel leaf↔rail、round hasp↔keeper）逐元素 element-scoped `allow_overlap`（来源样本已声明）
- closed pose：lid/door/panel 在 q=0 seat 在 body rim（0–6 mm gap）、覆盖开口

## Reject cases

- 让 latch（hasp/clasp）挂在 sliding_top_panel（无 hinged lid part）→ latch 浮空 / 挂载点缺失 FAIL；须 gating latch=none。
- shallow_tray（HB=0.085）配 lift_out_inner_tray / 深 drawer → 内腔不足穿模 / 行程越界 FAIL；compatibility 排除。
- 给 captured-pin（bail/ring/drop_panel/round-hasp）补 MatingContract 硬对接 → 几何对不上 mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸（box_w/h）或材质 palette 当新 candidate 塞进 slot → 不是结构差异，违反 §2.4。
- 把 v05 双 clasp / v16 双 ring / v10 多 slat 的局部固定数量当成模板级 multiplicity 轴并加权采样 N → 误造 count 参数，违反 §8 单体判定。
- body 前面用 drawer 开口（v13 重建 sill/stile/rail）却仍发完整 `wall_front` plank → 前面双层穿模。
- lid rest pose 默认设成开启角而非 closed → closed-pose seat 检查 FAIL、不符合箱类身份。

## 与相邻类别的边界

- 不该混入：`rolling_toolbox_with_telescoping_handle`（有可伸缩拉杆 + 滚轮的拖行机构，本类是静置单体箱、无 telescoping prismatic 拉杆 + 轮轴）。
- 不该混入：`tackle_box_with_simple_hinged_lid`（仅单一简单铰盖、无 6×5×4×… 的 slot 多样性；本类的核心价值是 lid_closure 6 机构 + interior 多 prismatic 机构）。
- 不该混入：`chest_freezer_with_hinged_lid`（家电制冷柜壳体，含压缩机/温控语义；本类是无源储物木箱）。
- 不该混入：`box_fan_with_control_knob`（旋钮控制的风扇家电，主活动是叶轮旋转；本类主活动是箱盖开合）。
- 不该混入：行李箱 / 软包 suitcase（壳体 + 拉链 + 万向轮 + 伸缩柄；本类是板条木箱形态，无拉链/轮）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 D 槽拆 D1 handle × D2 latch 双子轴 + latch conditional gating by lid 的方案；确认 sliding_top_panel 的 PRISMATIC 作为独立拓扑等价类编入 slot_choice；确认 body_form/wall_style 的比例/seam 样本归 module 而非连续尺寸虚胖；确认 interior 3 个 PRISMATIC 机构与浅箱 body_form 的 compatibility 排除带） |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | base | box_body 骨架 + lid_hinge + hasp 基线 | rec_...`1a9c91ba`(parent) | L23-129 | root chassis + hinged_flat_top + rope handle + hasp latch + plank wall |
| S2 | lid_closure | front_drop_panel | rec_...`0bad30bc`(v02) | L106-136 | 前壁下翻 REVOLUTE + 固定 rim |
| S3 | lid_closure | split_double_leaf_top | rec_...`052ac6c9`(v03) | L85-163 | 双叶顶盖 2× REVOLUTE |
| S4 | lid_closure | sliding_top_panel | rec_...`f1d22421`(v04) | L66-133 | 侧槽 PRISMATIC 滑盖（唯一 PRISMATIC 主拓扑） |
| S17 | lid_closure | hinged_front_door | rec_...`f8e00598`(v17) | L108-149 | 立轴前门 REVOLUTE + 固定顶板 |
| S19 | lid_closure | arched_curved_top | rec_...`0ee48866`(v19) | L28-58, L150-184 | `_arched_lid_mesh` barrel 顶盖 REVOLUTE |
| S1 | body_form | low_wide | rec_...`53ef4fa4`(v01) | L34-124 | 低矮加宽比例 |
| S8 | body_form | long_narrow_rounded_ends | rec_...`e12ddd40`(v08) | L34-108 | 长窄 + 圆端帽 |
| S9 | body_form | shallow_tray | rec_...`0becfb46`(v09) | L33-86 | 浅托盘 + 透明盖 |
| S15 | body_form | beveled_corner_posts | rec_...`094c6b13`(v15) | L50-66, L118-127 | cadquery chamfer 角柱 + beveled lid |
| S10 | wall_style | ribbed_vertical_slats | rec_...`02fc6fb9`(v10) | L53-78 | 竖向 slat 循环 + 加强 rail |
| S11 | wall_style | weathered_crate_corner_blocks | rec_...`4dcfee7f`(v11) | L38-78 | 风化板条 + 凸角块 |
| S16 | wall_style + D1 | reinforced_metal_straps + rotating_side_rings | rec_...`433dd9d3`(v16) | L62-93 / L95-176 | 环身 strap 带 + TorusGeometry 转环把 |
| S7 | handle (D1) | swing_bail_handle | rec_...`b6be553b`(v07) | L63-81, L103-133 | 可转提梁 REVOLUTE + captured-pin |
| S5 | latch (D2) | rotating_clasp_latch | rec_...`e1b5c35d`(v05) | L95-99, L127-146 | 双旋转卡扣 REVOLUTE |
| S12 | latch (D2) | rotating_hasp_plate | rec_...`9f64bd44`(v12) | L77-89, L114-134 | 立轴旋转 hasp 板（lockbox） |
| S6 | interior | raised_feet | rec_...`7a4c1a2b`(v06) | L50-79 | 抬高脚 + 内 tray lip |
| S13 | interior | slide_out_front_drawer | rec_...`427708e5`(v13) | L104-114, L161-194 | 前抽屉 PRISMATIC −Y |
| S14 | interior | lift_out_inner_tray | rec_...`01472062`(v14) | L71-87, L134-179 | 升降内托 PRISMATIC +Z |
| S18 | interior | sliding_internal_divider | rec_...`2825c67d`(v18) | L88-103, L150-187 | 滑动隔板 PRISMATIC ±X |
| S20 | interior | nesting_stackable_feet | rec_...`aedc9476`(v20) | L41-68 | 嵌套脚 + 凹底 recess |

## 模板实现备注（可选）

- 共享 helper：`box_body` floor+4 wall + corner_bracket 循环为所有 module 公用骨架；`_arched_lid_mesh`（v19 L28-58）仅 arched module 用；`mesh_from_cadquery`+`.chamfer()`（v15）仅 beveled body_form 用。
- captured-pin allow_overlap 来源样本已逐条声明：v07 L151-192（bail pin↔boss/bracket）、v16 L285-340（ring↔pin/saddle/clevis ×8）、v05 隐式（clasp captured 由 origin 守）、v15 L191-195（round hasp↔keeper）、v02 L149-155（drop_panel leaf↔rail）。实现时按 module 复制对应 element-scoped allow_overlap。
- latch parent = `box_lid`（不是 body）：latch 子轴必须在 lid module 发出 lid part 后才挂；gating 须保证 sliding_top_panel 时 latch=none。
- 不调 `fail_if_parts_overlap_in_sampled_poses`（多 module 多姿态积大、成本不值）；保留自动 baseline 的 `fail_if_parts_overlap_in_current_pose`（closed rest pose 干净）。
- body_form=shallow_tray 与 interior∈{drawer, tray} 互斥（内腔不足）；body_form=long_narrow 与 split_double_leaf 体形偏窄需复核 seam。
- 参考实现模板（review 通过后选读）：`drawer_cabinet_with_sliding_drawers.py`（prismatic 抽屉 + runner captured）、`dishwasher_with_dropdown_door_and_sliding_racks.py`（dropdown REVOLUTE door + 内 prismatic rack，与 front_drop_panel + interior 同构）。
