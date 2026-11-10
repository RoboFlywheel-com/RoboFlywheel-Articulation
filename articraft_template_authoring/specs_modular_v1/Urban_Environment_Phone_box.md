# phone_box — Modular Template Spec (SPEC_ONLY)

## 元信息
| 项 | 值 |
|---|---|
| slug | `phone_box` |
| template path | `agent/templates/Urban_Environment_Phone_box.py` |
| test path (optional) | `tests/agent/test_phone_box_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children: roof + door layered on a shared body root; multiplicity: glazing-pane grid loop) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (1 parent + 9 converged variant forks) |
| source_index_policy | only adopted module sources are indexed below |

所有 10 个样本共享一个 single-spine 结构：一个 root `kiosk_body`（plinth + 4 corner pilasters + lower kick panels + glazed window walls + TELEPHONE frieze band + crown roof）外加 **一个真实的 VERTICAL-hinge REVOLUTE 门/叶**。结构变化轴严格落在源 map 的 PHASE-0 四轴上：

- **Roof/crown form**：domed-K6（parent，stacked tapering boxes）vs flat slab（`roof_flat`，trim + overhang slab）vs triangular pediment（`roof_pediment` / `pediment_sparse_bifold`，手搓 6-vertex MeshGeometry 三棱柱 + raked trim + ridge + finials）。
- **Door mechanism**：single hinged leaf（parent，1 child + 1 joint）vs bi-fold（`door_bifold`，2 child + 2 joint，inner leaf 用 `Mimic(multiplier=-2.0)` 跟随）vs open-side（`door_openside`，front 改成永久敞开的 walk-in doorway，唯一活动件挪到 +Y 侧面的 access panel）。
- **Glazing grid N**：parent/baseline `COLS=3 ROWS=6`；`glazing_sparse` `2×4`；`glazing_dense` `4×8`。grid 全部由 `_glazed_grid(...)` helper loop-emit（`{prefix}_glass`、`{prefix}_vbar_{c}`(cols+1)、`{prefix}_hbar_{r}`(rows+1)），门玻璃同样 loop-emit（`door_vbar_{c}`、`door_hbar_{r}`，`d_cols=COLS`、`d_rows=ROWS-1`）。**N 是模板级 multiplicity，可由 COLS/ROWS 驱动。**
- **Footprint**：square one-person（`BOX_W=BOX_D=0.92`）vs wider two-person（`footprint_wide`，`BOX_D=1.29`≈1.4×，并把更宽面的列数提到 `BACK_COLS=5`、`DOOR_COLS=4`）。

手写 cosmetic repeats（4 frieze signs `sign_{fc}`/`signtext_{fc}`、4 crown emblems `crown_emblem_{fc}`、per-face kick panels）按源 map 审核结论，是 greebles，**不作为 multiplicity 轴，不过度 loop**。唯一需要保留的真实关节是 vertical-hinge REVOLUTE 门。

## 核心身份

phone_box = **英式 K6 红色电话亭 / 玻璃 kiosk**：一个落在低 plinth 上的、近方形、直立的封闭小室；四角 corner pilasters；三面（或两面 + 一面敞口）规则矩形玻璃格栅墙（mullion grid，行×列多重度）；顶部一圈 "TELEPHONE" frieze/sign 带；一个 crown roof（穹顶 / 平板 / 三角山墙）；**唯一的可动件是绕垂直轴（+Z）铰接的门 / 折叶 / 侧面 access panel——这是定义性关节**。默认成熟域是单人到双人占地、≈2.4–2.6 m 高、红/黑/银等少数 colorway。

不该混入：

- **utility_box / 配电箱 / 街边机柜**：那类是实心或单开维修门的矮箱体，没有人可进入的玻璃围合空间、没有 frieze sign 带、没有 corner-pilaster + multi-pane glazing 身份；phone_box 必须保持 glazed walk-in kiosk 比例（高 > 2 m，玻璃格栅墙）。
- **mailbox / 邮筒 pillar**：那类是实心圆柱/方柱投信筒，开口是小投递口而非全高门；phone_box 的开口是全高 mullioned 门并且人可进入。
- **window / sliding_window**：玻璃格栅本身不能让模板退化成纯窗扇；phone_box 的 grid 始终包在一个四角 pilaster + frieze + roof 的封闭 kiosk 壳里，关节是整扇门而不是滑动窗扇。

## 槽位 + 候选模块表

### Slot A：roof / crown form（root body 上层，固定 visual，不引入新关节）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `roof_domed_k6` | `rec_red-british-k6-telephone-booth-phone-box-a-cast-_20260612_113148_944128_c00c1818` | L220-L256 | eligible if compatible | cornice slab + 11-step `roof_step_{s}` 逐层 cosine-taper Box 堆叠成穹顶 + 4 `crown_emblem_{fc}` gold greeble；`ROOF_H≈0.36` |
| `roof_flat_slab` | `rec_phone_box_var_roof_flat` | L219-L236 | eligible if compatible | 薄 `roof_trim`(dark) + 单块四向 overhang `roof_slab`；`ROOF_H≈0.08`；BODY_TOP 抬高到 2.20 补偿矮顶 |
| `roof_pediment` | `rec_phone_box_var_roof_pediment` | L222-L318 | eligible if compatible | cornice + 手搓 6-vertex/8-face `MeshGeometry` 三棱柱 pediment（ridge 沿 Y）+ 4 raked `pediment_trim_*` + `ridge_cap` + 2 `gable_finial_*`；`mesh_from_geometry` |

二级 pediment 变体 `rec_phone_box_var_pediment_sparse_bifold` L? (CORNICE_H/GABLE_H 顶部块 + tympanum gold emblems, 同 family) 验证 pediment 可与 bi-fold/sparse 组合，不另算 candidate（同结构家族，只换 colorway/组合）。

### Slot B：door mechanism（root body 的可动子件，承载定义性 REVOLUTE 关节）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `door_single_hinge` | `rec_red-british-k6-telephone-booth-phone-box-a-cast-_...c00c1818` | L264-L350 | eligible if compatible | 1 个 `door` child（frame + kick + glass + loop mullion `door_vbar/hbar` + steel handle），1 个 REVOLUTE `body_to_door`，hinge 在 +Y 前角，axis (0,0,1)，lower=0/upper≈95° |
| `door_bifold` | `rec_phone_box_var_door_bifold` | L271-L399 | eligible if compatible | front 开口拆 2 窄叶（`outer_leaf` + `inner_leaf`，`_build_leaf` helper，`LEAF_COLS=2`）；2 个 REVOLUTE：`body_to_outer_leaf`(driver) + `outer_to_inner_leaf`(`Mimic(joint="body_to_outer_leaf", multiplier=-2.0)`)；track-guided V-fold |
| `door_open_side` | `rec_phone_box_var_door_openside` | L270-L362 | eligible if compatible | front (+X) 改成永久敞开 walk-in doorway（无 kick/无 glazed_grid，仅 jamb/frieze）；唯一活动件挪到 +Y 侧面 `access_panel`（hinge 在 -X 后边，leaf 沿 +X，axis (0,0,1)，开口朝 +Y） |

### Slot C：glazing grid multiplicity N（fixed walls + door glazing 的 mullion grid 行列数）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `glaze_medium_3x6` | `rec_red-british-k6-...c00c1818` | L49-L50 + L56-L113 | eligible if compatible | `COLS=3 ROWS=6`；`_glazed_grid` loop emit (cols+1) vbar + (rows+1) hbar；门 `d_cols=COLS d_rows=ROWS-1` |
| `glaze_sparse_2x4` | `rec_phone_box_var_glazing_sparse` | L49-L50 | eligible if compatible | `COLS=2 ROWS=4` 稀疏格；同 helper，少 bar |
| `glaze_dense_4x8` | `rec_phone_box_var_glazing_dense` | L49-L50 | eligible if compatible | `COLS=4 ROWS=8` 密 Georgian 格；同 helper，多 bar |

### Slot D：footprint（plan 尺寸 + 宽面列数派生，控制单人/双人占地）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `foot_square_1person` | `rec_red-british-k6-...c00c1818` | L32-L33 | eligible if compatible | `BOX_W=BOX_D=0.92` 近方形单人占地；door 列数 = COLS |
| `foot_wide_2person` | `rec_phone_box_var_footprint_wide` | L32-L33 + L50-L51 | eligible if compatible | `BOX_D=1.29`(≈1.4×) 双人占地；宽面列数派生提升（`BACK_COLS=5`、`DOOR_COLS=4`），即 cols 随 span 派生 |

硬约束满足：Slot A=3、B=3、C=3、D=2，均 ≥2（A/B/C ≥3），每个 candidate 都有真实 `model.py:Lx-Ly`，candidate 之间是真正的 part-tree / joint-count / mesh-type / N 差异（非纯尺寸/颜色）。

## 槽位图（slot graph）

pattern: `mixed`（root body 上挂 parallel children：roof 是固定 visual 层、door 是可动子件；glazing 是 body+door 内的 multiplicity loop）

```
              [Slot C glazing N]  ──drives mullion loop──┐
                                                         ▼
[ground z=0] ── plinth ── kiosk_body (root) ── frieze ── [Slot A roof: fixed visual cap on top of frieze]
   [Slot D footprint sets BOX_W/BOX_D + cols]   │
                                                 └──[Slot B door: REVOLUTE +Z hinge]──> door / leaves / side panel
```

接口点位与关节：

- **Slot D → 全体**：`BOX_W/BOX_D` 是 master，决定 plinth/pilaster/kick/window span、frieze、roof 平面、门宽（`door_w = inner_d - 2·gap`）、hinge 位置。footprint 改变时所有下游 anchor 用 `BOX_W/BOX_D` 重算（不是 hard-code）。宽面列数 `conditional` 派生（span 大→cols 多）。
- **Slot A → body top**：roof 坐在 `ROOF_BASE = BODY_TOP + FRIEZE_H`（frieze 顶面），固定 support，无关节。`roof_flat_slab` 选中时 `BODY_TOP` 抬到 2.20 补偿矮顶以保持 ~2.4–2.6 m 总高（`equation`）。
- **Slot B → front/side opening（定义性关节）**：
  - `door_single_hinge`：1 REVOLUTE `body_to_door`，origin `(BOX_W/2-0.03, BOX_D/2-POST-gap, 0)`，axis (0,0,1)，leaf 在 local frame 以 hinge 为原点沿 -Y 伸展，lower=0 / upper≈95°，正向开门时 free edge 外摆 +X。
  - `door_bifold`：driver REVOLUTE `body_to_outer_leaf`（同 origin/axis）+ follower REVOLUTE `outer_to_inner_leaf`（origin 在 outer leaf 自由边 `(0,-leaf_w,0)`，`Mimic(multiplier=-2.0)`，lower=-2·OPEN/upper=0）。
  - `door_open_side`：front +X 不放门（敞口，仅 jamb/frieze），REVOLUTE `body_to_panel` 挪到 +Y 侧面，origin `(-(BOX_W/2-POST-gap), BOX_D/2-GLASS_INSET, 0)`，axis (0,0,1)，leaf 沿 +X，开口朝 +Y。
- **Slot C → body & door**：`_glazed_grid(cols,rows)` 在每面 fixed wall loop emit glass+bars；door 玻璃 `d_cols=COLS, d_rows=ROWS-1`。C 不引入关节，只改 visual 多重度。

互斥/派生：Slot A/B/C/D 互相**正交**（任意组合均合法，源 map COMBO PRE-AUDIT 已验证 `pediment×sparse×bifold` 与 `flat×dense×wide` 两个 combo carrier 收敛）。`door_open_side` 与 footprint/roof/glazing 全兼容（panel 也用 `_glazed_grid`-风格 loop，受 Slot C 的 N 驱动）。

## 每槽位 Module Emits / Interfaces

### Slot A / module `roof_domed_k6`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `roof_cornice` + `roof_step_0..10` + `crown_emblem_{+x,-x,+y,-y}`（全为 body visual） | parent/model.py:L220-L256 |
| internal joints | 无 | — |
| upstream interface | 坐在 `ROOF_BASE = FRIEZE_TOP`，平面 = body plan 外扩 | parent/model.py:L222-L227 |
| downstream interface | roof 顶 = TOTAL_H；不接子件 | parent/model.py:L41 |

### Slot A / module `roof_flat_slab`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `roof_trim`(dark) + `roof_slab`(overhang) | roof_flat/model.py:L219-L236 |
| internal joints | 无 | — |
| upstream interface | 坐在 ROOF_BASE；`BODY_TOP` 抬至 2.20 保高 | roof_flat/model.py:L35,L219-L236 |
| downstream interface | TOTAL_H ≈ ROOF_BASE+0.08 | roof_flat/model.py:L40 |

### Slot A / module `roof_pediment`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `roof_cornice` + `pediment`(MeshGeometry 三棱柱) + `pediment_trim_*`×4 + `ridge_cap` + `gable_finial_{front,back}` | roof_pediment/model.py:L222-L318 |
| internal joints | 无 | — |
| upstream interface | cornice 坐在 ROOF_BASE；mesh base 平移到 `ped_z0=ROOF_BASE+cornice_h` | roof_pediment/model.py:L238-L271 |
| downstream interface | 顶 = ped_z0+ped_rise+finial；不接子件 | roof_pediment/model.py:L312-L318 |

### Slot B / module `door_single_hinge`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door` child：`door_frame`+`door_kick_panel`+`door_glass`+loop `door_vbar_{c}`/`door_hbar_{r}`+`door_handle` | parent/model.py:L264-L330 |
| internal joints | 无（child 内无关节） | — |
| upstream interface | hinge 轴在 body +Y 前角 `(BOX_W/2-0.03, BOX_D/2-POST-gap)` | parent/model.py:L276,L341 |
| downstream interface | REVOLUTE `body_to_door` axis(0,0,1) lower=0/upper≈95° | parent/model.py:L342-L350 |

### Slot B / module `door_bifold`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `outer_leaf` + `inner_leaf`（各 `_build_leaf`：frame+kick+glass+loop mullion，inner 带 handle） | door_bifold/model.py:L298-L367 |
| internal joints | follower REVOLUTE `outer_to_inner_leaf` `Mimic(multiplier=-2.0)` | door_bifold/model.py:L387-L399 |
| upstream interface | driver hinge 同 single-door +Y 前角 | door_bifold/model.py:L287-L288,L372-L380 |
| downstream interface | driver REVOLUTE `body_to_outer_leaf`；fold 轴在 outer 自由边 `(0,-leaf_w,0)` | door_bifold/model.py:L372-L399 |

### Slot B / module `door_open_side`
| emits | 描述 | 来源 |
|---|---|---|
| parts | front +X 敞口（无门 part）；`access_panel` child：`panel_frame`+`panel_kick`+`panel_glass`+loop `panel_vbar/hbar`+`panel_handle` | door_openside/model.py:L158,L274-L340 |
| internal joints | 无 | — |
| upstream interface | hinge 在 +Y 面 -X 后边 `(-(BOX_W/2-POST-gap), BOX_D/2-GLASS_INSET)` | door_openside/model.py:L352-L353 |
| downstream interface | REVOLUTE `body_to_panel` axis(0,0,1) lower=0/upper≈95°，开口朝 +Y | door_openside/model.py:L354-L362 |

### Slot C / module `glaze_*`（medium/sparse/dense）
| emits | 描述 | 来源 |
|---|---|---|
| parts | per fixed face `{prefix}_glass` + `{prefix}_vbar_{0..cols}` + `{prefix}_hbar_{0..rows}`；door 同构 | parent/model.py:L56-L113,L304-L322 |
| internal joints | 无（纯 visual multiplicity） | — |
| upstream interface | span = inner_w/inner_d（由 footprint），z0=WINDOW_BOTTOM z1=BODY_TOP | parent/model.py:L175-L180 |
| downstream interface | bar 数 = (cols+1)+(rows+1)/面；门玻璃 d_rows=ROWS-1 | parent/model.py:L304-L305 |

### Slot D / module `foot_*`（square/wide）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；设 `BOX_W/BOX_D` master 尺寸，下游全部派生 | parent/model.py:L32-L33 |
| internal joints | 无 | — |
| upstream interface | 决定 plinth/pilaster/kick/window/frieze/roof plane、door_w、hinge xyz | parent/model.py 全文用 BOX_W/BOX_D |
| downstream interface | wide 时宽面 cols 派生提升（BACK_COLS/DOOR_COLS） | footprint_wide/model.py:L50-L51 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `roof_choice` | enum | `roof_domed_k6` / `roof_flat_slab` / `roof_pediment` | — | choice | procedural sampler 选 | Slot A table |
| `door_choice` | enum | `door_single_hinge` / `door_bifold` / `door_open_side` | — | choice | procedural sampler 选 | Slot B table |
| `glaze_choice` | enum | `glaze_sparse_2x4` / `glaze_medium_3x6` / `glaze_dense_4x8` | `glaze_medium_3x6` | choice | 决定 (COLS,ROWS) | Slot C table |
| `foot_choice` | enum | `foot_square_1person` / `foot_wide_2person` | `foot_square_1person` | choice | 决定 BOX_D 档 | Slot D table |
| `glaze_cols` | int | {2,3,4} | 3 | conditional | = glaze_choice 映射；宽面 +X/-X/door 列数随 span 派生（wide 时 +1~+2） | parent L49 / footprint_wide L50-51 |
| `glaze_rows` | int | {4,6,8} | 6 | conditional | = glaze_choice 映射；door rows = rows-1 | parent L50,L305 |
| `box_w` | float | [0.86, 0.98] | 0.92 | independent | plan width，范围内均匀采样后 clamp | parent L32 |
| `box_d` | float | square:[0.86,0.98] / wide:[1.20,1.40] | 0.92 | conditional | 区间随 foot_choice；wide≈1.4× | footprint_wide L33 |
| `body_top` | float | [1.95, 2.25] | 2.00 | independent | 玻璃体高度；clamp 保 ~2.0–2.3 | parent L36 |
| `body_top_roof_comp` | float | derived | — | equation | flat_slab 选中时 body_top += ~0.20 补矮顶保总高 | roof_flat L35,L39 |
| `roof_h` | float | derived | — | equation | = f(roof_choice)：domed 0.36 / flat 0.08 / pediment 0.36 | parent L40 / flat L39 |
| `window_bottom` | float | [0.55, 0.68] | 0.62 | independent | kick 高度；clamp < body_top-0.8 | parent L44 |
| `open_angle` | float | [85°, 105°] | 95° | independent | door REVOLUTE upper；clamp 入区间 | parent L53 |
| `palette_style` | enum | `classic_red` / `air_force_blue` / `municipal_green` / `noir_black` / `polished_silver` / `royal_post_red` | `classic_red` | choice | 见 Multiplicity/palette 表；只换 material rgba | parent L119-L128 |
| (—) | constraint | — | — | inequality | `door_w = inner_d - 2·DOOR_GAP > 0` 且 hinge_y 落在 pilaster 内侧（door/panel 不穿 pilaster）；违反则按 box_d 回缩 | parent L269,L341 |
| (—) | constraint | — | — | inequality | `WINDOW_BOTTOM + 0.8 ≤ BODY_TOP`（保证玻璃带有足够高度）；违反则下调 window_bottom | parent L44,L36 |
| (—) | constraint | — | — | inequality | bi-fold：`outer_to_inner` mimic 行程 `[-2·open, 0]` 与 driver `[0, open]` 必须一致符号，使闭合 q=0 两叶 flush | door_bifold L394-L399 |

连续尺寸采样契约：先采 independent（box_w, body_top, window_bottom, open_angle）→ equation 派生（roof_h, body_top_roof_comp）→ inequality 投影/回缩（door_w>0、玻璃带高度、hinge 不穿 pilaster）→ conditional 解析（box_d 区间、glaze_cols/rows、wide 宽面列数）。所有约束在 `resolve_config` 内求解。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴：glazing-pane grid（rows × cols）。**

- `count_param`：`(glaze_cols, glaze_rows)`（一对，驱动每面 mullion grid；列方向轴与行方向轴共享同一 `_glazed_grid` helper，按小类视为单一 grid 轴的二维档）。
- `N_range`：`cols ∈ [2, 6]`、`rows ∈ [3, 10]`（产品域）。测试偏小（2×4、3×6），大格（4×8、6×10）按构造安全、稀疏抽样。本小类 grid 是 cosmetic-but-identity multiplicity，不接关节，N 大不会自碰撞。
- sampling domain（权重档）：小 N 高频——`3×6` 与 `2×4` 合计 ~70%、`4×8` ~20%、`>4×8`（含 5×9、6×10）尾部稀有 ~10%；`glaze_choice` enum 给三个标称档，连续 N 在档附近 ±1 抖动派生（wide footprint 把宽面 cols +1~+2）。
- copied object：每面 `{prefix}_glass`（1）+ `{prefix}_vbar_{c}`（cols+1）+ `{prefix}_hbar_{r}`（rows+1）；door/leaf/panel 玻璃同构（door rows = rows-1）。
- naming：`win_left_*` / `win_right_*` / `win_back_*` / `door_*` / `outer_*` / `inner_*` / `panel_*` 前缀 + `_vbar_{c}` / `_hbar_{r}` 索引（沿用源 helper 命名）。
- placement：vbar 沿 span 等分 `c/cols`，hbar 沿高度等分 `r/rows`；bar 在 glass 平面外侧 `MULLION_D` 处（避免 z-fight）。
- joint policy：**无关节**——glazing 是纯 visual multiplicity；唯一关节是 Slot B 的门 REVOLUTE。
- source/gating：`_glazed_grid` helper 复用于所有 fixed walls + door；`door_open_side` 的 access_panel 同样用 grid loop。N 上限 sweep 设 cols≤6/rows≤10。

door 叶数不作为独立 multiplicity 轴：single=1、bi-fold=2 是 Slot B 的离散 candidate（part-tree + joint-count 差异），不是 count_param 复制。

## 拓扑多样性审计

总组合数：A × B × C × D = 3 × 3 × 3 × 2 = **54**；把 distinct glazing N（≥3：2×4, 3×6, 4×8，加尾部 5×9/6×10）独立计入，topology-distinct 上限远超 54。

理由：仅 Slot A×B 就有 9 个 part-tree/joint-count 不同的 topology（domed/flat/pediment × single/bifold/openside，其中 bifold 多 1 child+1 mimic joint、openside 把关节挪到侧面 panel + front 敞口去掉 door part），再叠 C 的 distinct N 与 D 的 footprint，distinct topology ≥ 9×3 = 27 ≫ 10。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `ctx.rng` 对 A/B/C/D 各做加权采样（A/B 均匀；C 小 N 偏多；D square ~70% / wide ~30%），再采连续 scale（box_w/body_top/window_bottom/open_angle），`resolve_config` 解 equation/inequality/conditional。`slot_choices_for_seed(seed)` 返回 `[(roof, …),(door, …),(glaze, …),(foot, …)]` 离散四元组（连续 scale 不进 slot_choices，除非改拓扑等价类）。compatibility matrix 全 legal（四轴正交，两 combo carrier 已收敛验证）。无需 curated/modulo 主域；regression overrides 仅在出现已知失败 seed 时按需加，初版 none。random sweep：seeds 0-49 初轮、0-999 maturity（含尾部大 N）。Topology target：1000-seed distinct 富类别建议 ≥300（report-only）（54 离散组合 × 连续 N 抖动 + footprint scale 足以覆盖）。
Controlled local parameterization：关键连续 scale = `box_w`(plan)、`box_d`(footprint 派生区间)、`body_top`(body height)、`window_bottom`(kick height)、`open_angle`(door travel)；范围/ clamp 见第 7 节，全部在 `resolve_config` clamp/派生，不破坏 InterfaceSpec（hinge 仍落 pilaster 内侧、roof 仍坐 frieze 顶、grid span 跟 inner_w/d）/ MatingContract（门闭合 seat into opening）/ multiplicity（grid N 独立）。跨部件依赖（roof_h↔body_top 补偿、box_d↔宽面 cols、door_w↔box_d）显式声明为 equation/conditional/inequality，不当独立自由变量。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | A/B 均匀，C 小 N 偏多，D 70/30；连续 scale 区间内均匀后 clamp | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | 四轴全正交、全 legal；无互斥；两 combo carrier 已收敛 | 无 floating / collision / 错轴 / 闭合姿态错 / door 穿 pilaster |
| controlled local variation | box_w/box_d/body_top/window_bottom/open_angle clamp+派生 | 比例变化不破接口、clearance、hinge origin、kiosk identity |
| regression overrides | none（初版）；仅已知失败 seed 时按需加并注明 | 仅失败回归 |
| random sweep | seeds 0-49 初轮，0-999 maturity（含尾部大 N glazing） | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A roof | 3 | yes | yes | |
| B door | 3 | yes | yes | 含定义性 REVOLUTE 关节 |
| C glazing N | 3 | yes | yes | multiplicity 轴 |
| D footprint | 2 | yes | no | 2 档；wide 派生宽面 cols |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名（roof/door/glaze/foot 四元组）。
- `config_from_seed` 对普通 seed 用 deterministic procedural sampling；seed=0 不特殊。
- compatibility matrix / gating 阻止非法组合（本类四轴正交，无非法组合；但 inequality 保证 door_w>0、hinge 不穿 pilaster、玻璃带高度足）。
- regression overrides 稀疏且有理由（初版 none）。
- 不以小型 curated/modulo 表作为主 seed domain。
- 受控 scale（box_w/box_d/body_top/window_bottom/open_angle）clamp，不破接口/clearance/joint origin/glazing 多重度。
- 跨部件 scale 依赖（roof_h↔body_top、box_d↔cols、door_w↔box_d）在 `resolve_config` 解，不留到 builder。
- 关键关节存在且 type/axis/range 正确：门 REVOLUTE，axis (0,0,1)，lower≈0 / upper∈[85°,105°]；bi-fold follower 是 `Mimic(joint=driver, multiplier=-2)`；open_side 的关节挪到 +Y panel。
- copied glazing objects 遵循命名/placement（`{prefix}_vbar_{c}` cols+1、`{prefix}_hbar_{r}` rows+1，door rows=ROWS-1）。
- InterfaceSpec / MatingContract：kiosk base 落 z=0；roof 坐 frieze 顶；闭合门 seat into opening（element-scoped `allow_overlap` 于 jamb embed）；总高 ∈ ~2.4–2.8 m。

## Reject cases

- 门关节缺失、变成 fixed、或轴非垂直 (0,0,1)（失去定义性 REVOLUTE 身份）。
- 门 / 叶 / panel 漂浮：hinge origin 不在 pilaster 内侧或与 body 不接触（`expect_contact` 失败）。
- bi-fold inner leaf 没有 mimic（或 multiplier≠-2），导致两叶不协调或穿模。
- glazing grid 退化（cols<2 或 rows<2，不再是 multi-pane kiosk 身份），或把 cosmetic frieze/emblem 误当 multiplicity 大量复制。
- footprint 缩放后 door_w≤0 或门穿 pilaster / 玻璃带高度 < 0.8（未解 inequality）。
- roof 选 flat_slab 但未补 body_top，导致总高 < 2.4 m（违反 kiosk 比例）。
- open_side 变体保留 front +X 门又同时挪 +Y panel（双关节冗余）或 front 仍 glazed 死面（不再是 walk-in）。
- 模板把 palette 之外的颜色/材质变体当独立 slot，或用 curated seed 表充当主 domain。

## 与相邻类别的边界

- 不该混入：**utility_box / 街边配电柜**（矮实心箱 + 单维修门，无 walk-in 玻璃围合、无 frieze sign、无 corner-pilaster multi-pane glazing；phone_box 必须高 >2 m 且玻璃格栅墙人可进入）。
- 不该混入：**mailbox / 邮筒 pillar**（实心投信柱 + 小投递口；phone_box 开口是全高 mullioned 门，人可进入）。
- 不该混入：**window / sliding_window**（孤立窗扇；phone_box 的 grid 必须包在四角 pilaster + frieze + roof 的封闭 kiosk 壳内，关节是整扇门而非滑动窗扇）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY 草稿；4 轴（roof×3 / door×3 / glazing-N×3 / footprint×2）= 54 离散组合，distinct topology ≥27，glazing 为唯一 multiplicity 轴，门 REVOLUTE(+Z) 为定义性关节。待人工审核后再进入模板实现。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | roof_domed_k6 | rec_red-british-k6-...c00c1818 | L220-L256 | 穹顶 step 堆叠 + emblem |
| S2 | A | roof_flat_slab | rec_phone_box_var_roof_flat | L219-L236 | trim+overhang slab + body_top 补偿 |
| S3 | A | roof_pediment | rec_phone_box_var_roof_pediment | L222-L318 | MeshGeometry 三棱柱 + raked trim/ridge/finial |
| S4 | B | door_single_hinge | rec_red-british-k6-...c00c1818 | L264-L350 | 单叶 child + REVOLUTE hinge |
| S5 | B | door_bifold | rec_phone_box_var_door_bifold | L271-L399 | 2 叶 + Mimic(-2) bi-fold |
| S6 | B | door_open_side | rec_phone_box_var_door_openside | L270-L362 | 敞口 front + +Y access panel REVOLUTE |
| S7 | C | glaze_medium_3x6 | rec_red-british-k6-...c00c1818 | L49-L113 | `_glazed_grid` loop helper（基准 N） |
| S8 | C | glaze_sparse_2x4 | rec_phone_box_var_glazing_sparse | L49-L50 | 稀疏 N |
| S9 | C | glaze_dense_4x8 | rec_phone_box_var_glazing_dense | L49-L50 | 密 N |
| S10 | D | foot_square_1person | rec_red-british-k6-...c00c1818 | L32-L33 | 方形单人 master 尺寸 |
| S11 | D | foot_wide_2person | rec_phone_box_var_footprint_wide | L32-L33,L50-L51 | 1.4× 双人 + 宽面 cols 派生 |
| S12 | A+B+C | pediment_sparse_bifold (carrier) | rec_phone_box_var_pediment_sparse_bifold | L29,L46-L58 | 验证 pediment×sparse×bifold combo 收敛 |
| S13 | A+C+D | flat_dense_wide (carrier) | rec_phone_box_var_flat_dense_wide | — | 验证 flat×dense×wide combo 收敛 |

## 模板实现备注（可选）

- `_glazed_grid` helper 在 fixed walls / door / leaf / panel 间共享；palette 只换 material rgba，不改结构。
- 关键 MatingContract：门闭合 seat into opening 需 element-scoped `allow_overlap(body, door/leaf/panel, reason=jamb embed)`（源已声明，见 parent L425-L429、bifold L505-L514、openside L437-L441）。
- bi-fold 的 `outer_to_inner_leaf` 必须保留 `Mimic(joint="body_to_outer_leaf", multiplier=-2.0)`，否则两叶 closed 不 flush / open 穿模。
- `roof_pediment` 用 `MeshGeometry`+`mesh_from_geometry`（6 vertex / 8 face），实现时注意 outward winding 与 base 平移到 `ROOF_BASE+cornice_h`。
- palette_style 目标 ≥4 colorway：classic_red / air_force_blue（澳式深蓝）/ municipal_green / noir_black / polished_silver / royal_post_red，每个只改 `kiosk_red`(+dark)、`plinth_black`、`crown_gold` 等 material rgba，glass 保持半透。
