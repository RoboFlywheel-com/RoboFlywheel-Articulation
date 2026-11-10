# makeup2 (articulated makeup compact / palette) — Modular Spec

> 来源小类：`picture/0611/Makeup2`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/0611__Makeup2.md`。
> **Category identity = articulated makeup compact / palette**：硬壳 base（含 recessed powder wells 或多格 pan grid）+ 后铰 mirror lid（≈100–105° 开）。
> 与相邻小类 `Accessories_Cushion`（cushion powder compact）区别：本类以 palette 多 pan / 多 well 为主，且强调 case_form ③ 家族（round / rectangular / clover）；cushion 主打 slide / clamshell / puff_tray 内部机构。
>
> **同步状态**：本 spec 引用的 11 个 5 星样本（2 个 parent + 9 个 fork 槽位变体）已同步进本仓库 `data/records/`，rating=5，均引自 `revisions/rev_000001/model.py`。

## 元信息
| 项 | 值 |
|---|---|
| slug | `makeup2` |
| template path | `agent/templates/makeup2.py` |
| test path (optional) | 无（sweep-pipeline 为唯一验收） |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: case_form + closure，外加 `powder_layout` well 多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11（2 parent + 9 fork 槽位变体；均 converged，rating=5）|
| read_count | 11（全部读整份 `model.py`）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 11/11 全部被采纳为 module source |

阅读要点（用于槽位分解）：
- **2 个 parent** 共享同一基线拓扑：`base`（root，含 pan wells + 后铰硬件）+ `mirror_lid`（child，含 mirror 面 + 铰链 barrel）+ **1 × REVOLUTE** `lid_hinge`（axis=(-1,0,0)，closed≈-1.75 rad，open≈0.14）。001 号额外多一个 `powder_tray` REVOLUTE child（tray topology），002 号是纯 palette（无独立 tray）。为了模板简化，采纳 002 拓扑作为公共基线（`base` + `mirror_lid`，powder wells 全部作为 base visual 内嵌，Rule 1）。
- **case_form 轴**（Slot A / ③ Primary Form Family）：rounded_rectangle（parents，`_rounded_box` L19-35）/ round（`rec_var_case_form_round`，圆盘 base）/ clover（`rec_var_case_form_clover`，四叶草足迹）。每个 candidate 保持同 part 树 / 同 lid_hinge，仅 base + lid 的**平面边界 mesh**（Planar Boundary Form）不同。
- **closure 轴**（Slot B / ② joint mechanism）：hinge_only（friction_hinge，仅 lid_hinge REVOLUTE，见 002 parent）/ push_latch（`rec_var_closure_push_latch`，新增 `latch_button` PRISMATIC 独立 part）/ over_center_latch（`rec_var_closure_over_center_latch`，仅几何 catch bar，无新 joint）。
- **powder_layout 轴**（Slot C，multiplicity）：pans 是 base visual inline，Rule 1；N∈{2,4,6,8}。source pool 覆盖 2/4/6/8。N 通过 `("powder_layout", f"n{N}")` 编进 slot_choice tuple。

## 核心身份

一只**化妆粉盒 / 眼影调色盘**：硬壳 `base`（rounded_rectangle / round / clover 三种平面轮廓）内嵌一组 recessed cosmetic pans（N 个 wells，通常 2–8 格）；`mirror_lid` 通过后铰（REVOLUTE，axis≈-X，closed≈-1.75 rad，开位≈0.14 rad）翻起，盖内为 `mirror` 面。可选闭合硬件：push_latch（前缘小 PRISMATIC 按钮 + 前 catch）或 over_center_latch（前缘 catch bar）。默认成熟域：手持粉盒尺寸（X≈0.08–0.10 m，Y≈0.06–0.08 m，Z≈0.02–0.03 m）。

**不该混入**：
- 首饰盒 / pill box：无 mirror + powder pans 就不是化妆粉盒。
- 空 cosmetic case：必须有可见的 pan wells 或 palette pans。
- Cushion 粉盒（`Accessories_Cushion`）：cushion 有 slide / clamshell / puff_tray 内部机构；本类只保留 hinge 家族 + case_form ③ 家族。

## 槽位 + 候选模块表

### Slot A：case_form（③ Primary Form Family — base + lid 平面轮廓形态）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 · form_subtype |
|---|---|---|---|---|---|
| rounded_rectangle（基线） | forked_anchor | `rec_picturex_0611__makeup2__002__png_e452c59a23e8409d9b7df37aa3754bfb`（parent）| `_rounded_box` L19-35, `_base_shell` L38-61, `_lid_shell` L68-95 | eligible if compatible | 圆角矩形足迹（`box.edges("|Z").fillet`），X 长于 Y。**form_subtype = Planar Boundary Form**（矩形 boundary） |
| round | forked_anchor | `rec_0611_makeup2_var_case_form_round` | `_build_base_shell` L45-75, `_build_lid_frame` L139-171 | eligible if compatible | 圆盘足迹（cylinder / circle-extrude），X≈Y 对称。**form_subtype = Planar Boundary Form**（circle boundary） |
| clover | forked_anchor | `rec_0611_makeup2_var_case_form_clover` | `_clover_body` L54-79, `_build_base_shell` L81-104, `_build_lid_frame` L168-206 | eligible if compatible | 四叶草足迹（4 个圆盘 union），非凸对称。**form_subtype = Planar Boundary Form**（4-lobe rosette boundary） |

### Slot B：closure（② joint / mechanism — 前缘闭合硬件）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|---|
| hinge_only（基线） | forked_anchor | `rec_picturex_0611__makeup2__002__png_e452c59a23e8409d9b7df37aa3754bfb`（parent）| `lid_hinge` L202-225 | eligible if compatible | 仅后铰 REVOLUTE，靠摩擦保持闭合；前缘光洁无额外硬件 |
| push_latch | forked_anchor | `rec_0611_makeup2_var_closure_push_latch` | `_latch_housing` L119-129, `_latch_button` L132-139, `_latch_hook` L142-151, `latch_button` part L292-311 | eligible if compatible | 新增 `latch_button` 独立 part，**PRISMATIC** axis=(0,+1,0) 前缘小按钮（travel ≈ 0.003 m）；base 前缘 `latch_housing`，lid 前缘 `latch_hook` |
| over_center_latch | forked_anchor | `rec_0611_makeup2_var_closure_over_center_latch` | `_lid_barrel_shape` L134-158, base+lid 装配 L161-... | eligible if compatible | 前缘增加 fixed `latch_bar` 几何（base + lid 侧几何 catch），无新 joint |

### Slot C：powder_layout（multiplicity — N 个 pan wells，Rule 1 base visual）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| n2 | forked_anchor | `rec_0611_makeup2_var_powder_layout_2_well` | `_build_well_pan`/`_build_well_powder` L126-155, base visual 装配 L219-... | eligible if compatible | 2 个 pan wells，1×2 或 2×1 排列 |
| n4（parent 基线） | forked_anchor | `rec_picturex_0611__makeup2__002__png_e452c59a23e8409d9b7df37aa3754bfb`（parent） | `pan_specs` L151-156 | eligible if compatible | 4 个 pans，2×2 网格 |
| n6 | forked_anchor | `rec_0611_makeup2_var_powder_layout_6_well` | `x_positions`/`y_positions` grid L162-177 | eligible if compatible | 6 pans，3×2 网格 |
| n8 | forked_anchor | `rec_0611_makeup2_var_powder_layout_8_well` | `_well_grid` L137-146 | eligible if compatible | 8 pans，4×2 网格 |

## 槽位图（slot graph）

pattern: mixed（固定 named slots: case_form + closure，parallel children 均挂到 root `base`；`powder_layout` 是 base 上的 N-well multiplicity）

```
base (root, 由 case_form 决定 mesh 平面边界; 内嵌 N 个 pan wells; 后缘 base_knuckle_{0,1} + hinge_pin)
  │
  ├── mirror_lid (REVOLUTE, axis=(-1,0,0), origin=后铰线 (0, y_hinge, z_hinge), closed≈-1.75 rad, open≈0.14 rad)
  │       (lid_shell + mirror + lid_barrel; 由 case_form 决定 lid mesh 平面边界)
  │
  └── [closure slot]  (三选一)
        ├── hinge_only:        无新 part / 无新 joint
        ├── push_latch:        latch_button (PRISMATIC, axis=(0,1,0), origin=前缘 latch_housing 位置, travel ≈ 0.003 m)
        └── over_center_latch: 无新 part / 无新 joint (仅 base + lid 前缘 fixed catch 几何)
```

跨 slot joint / interface：
- `lid_hinge` 后铰：origin 在 base 后缘 `hinge_pin` 中心；`hinge_pin` 与 `lid_barrel` element-scoped `allow_overlap`（captured-pin）。
- `latch_button_slide` 前铰：base 前缘 `latch_housing` 上的按钮；`latch_button` 与 `latch_housing` element-scoped `allow_overlap`（sliding fit）。

## 每槽位 Module Emits / Interfaces

### Slot A / case_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (root) 的 shell mesh + `mirror_lid` 的 lid_shell mesh | S(parents/case_form_round/clover) |
| internal joints | 无 | — |
| upstream interface | 无（root parallel） | — |
| downstream interface | base 后缘 hinge line (0, +y_hinge, z_hinge) 供 lid_hinge 挂钩，base 底面接地 | parents L202-225 |

### mirror_lid（常量，非 slot；由 case_form 决定 mesh 边界）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `mirror_lid`（lid_shell + mirror + lid_barrel） | parent 002 L181-200 |
| internal joints | — | — |
| upstream interface | lid_barrel 中心线（0,0,0）挂 lid_hinge | parent 002 L202-225 |

### Slot B / closure
| emits | 描述 | 来源 |
|---|---|---|
| parts | hinge_only: 无； push_latch: `latch_button`（PRISMATIC child）； over_center_latch: 无（几何 fixed） | rec_var_closure_push_latch L292-311 |
| internal joints | push_latch: `latch_button_slide` PRISMATIC axis=(0,1,0) travel ~0.003 | rec_var_closure_push_latch L304-315 |
| upstream interface | base 前缘 `latch_housing` | rec_var_closure_push_latch L119-129 |
| downstream interface | 无（叶端） | — |

### Slot C / powder_layout （multiplicity 轴，Rule 1 base.visual）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 0（Rule 1；powder pans 是 base.visual inline） | parent 002 L157-163 |
| internal joints | 0 | — |
| upstream interface | base pan_floor Z=0.006（parent 002）；由 case_form 决定 cavity 边界 | parent 002 |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| case_form | enum | `rounded_rectangle` / `round` / `clover` | rounded_rectangle | choice | deterministic procedural sampling | Slot A |
| closure | enum | `hinge_only` / `push_latch` / `over_center_latch` | hinge_only | choice | deterministic procedural sampling | Slot B |
| powder_layout_count | int | {2, 4, 6, 8} | 4 | choice | 直接采样 well 数 | Slot C |
| palette_style | enum | `champagne_gold` / `translucent_navy` / `matte_black` / `rose_gold` / `pastel_mint` | champagne_gold | choice | deterministic procedural sampling；驱动 `mats[...]` 所有材质 | parent 001+002 + world_knowledge_extrapolation |
| base_len_scale | float | [0.90, 1.15] | 1.0 | independent | uniform，clamp | parent 002 L38-61 |
| base_width_scale | float | [0.90, 1.15] | 1.0 | independent | uniform，clamp | parent 002 |
| base_height_scale | float | [0.90, 1.20] | 1.0 | independent | uniform，clamp | parent 002 |
| lid_open_angle | float | [0.10, 0.35] | 0.14 | independent | rad；REVOLUTE upper | parent 002 L218-219 |
| latch_travel | float | derived | 0.003 | equation | `= 0.003 * base_len_scale` | push_latch L304-315 |
| (—) | constraint | pan row must fit cavity | — | inequality | `(cols-1)*span_x + 2*pan_r ≤ 2*(rx - 1.5*wall)`；违反回缩 pan_span 后 pan_r | parents / powder_layout variants |

**说明**：
- `powder_layout_count` 直接采 well 数（不是间接的 rows×cols），resolve_config 中根据 N 派生 grid 排列（`(cols, rows)`：2→(2,1), 4→(2,2), 6→(3,2), 8→(4,2)）。
- `latch_travel` 只在 `closure == "push_latch"` 时生效。

### 7.5 编译预算 / compile budget

Per-seed 编译预算 ≈ **12–20 s**。依据：base + lid mesh 主要是 cadquery rounded_box + circle 组合，pans 用共享 `Cylinder`/rounded_box mesh 复用一份 `Mesh` 对象（N 份 visual 引用同一 mesh），tessellation 主体 ≤64 段（外框圆角），小 pan ≤32 段，clover 是 4 个圆盘 union（一次布尔）。若超出预算先降 tessellation 段数；不要跳到重布尔雕刻。

## Multiplicity / Copy Logic

**独立轴 = 1**：`powder_layout_count`。

- `count_param`：`powder_layout_count`
- `N_range`：{2, 4, 6, 8}（离散小集合，权重档：2:0.25 / 4:0.35 / 6:0.25 / 8:0.15；4 是 parent 基线所以最常见）
- copied object：pan visual（rounded_box `_pan_shape` mesh，共享一个 Mesh）
- naming：`pan_{i}` (i=0..N-1)
- placement：由 `resolve_config` 依 N 派生 grid `(cols, rows)`：2→(2,1)，4→(2,2)，6→(3,2)，8→(4,2)；X 上均匀 `x0 + i*pan_span_x`，Y 上 `y0 + j*pan_span_y`
- joint policy：pans 非移动件，作为 base.visual inline（Rule 1，无 joint）
- source/gating：所有 4 个 N 值 source-backed；无 compatibility gating（clover 时需缩小 pan_span 或减小 pan_r 以适配非凸 cavity，由 §7 inequality 处理）

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part | 有 | 2 种：base+mirror_lid（hinge_only / over_center_latch）；base+mirror_lid+latch_button（push_latch）。source_type=forked_anchor；来源：parents + rec_var_closure_push_latch |
| └ multiplicity | 同构件 ×N | 有 | 见 §8 — powder_layout N∈{2,4,6,8} |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | REVOLUTE(-X, lid_hinge, 一直存在) + PRISMATIC(+Y, latch_button_slide, 仅 push_latch 时) — 声明的每种类型都会在 sweep 中出现（sweep 会实现 push_latch）。source_type=forked_anchor |
| ③ 主体形态家族 | 换核心 part 的几何形态原型 | 有 | 3 个原型：rounded_rectangle / round / clover。每个 `form_subtype = Planar Boundary Form`（矩形边界 / 圆边界 / 四叶草边界）。source_type=forked_anchor（3 个 source-backed），登记进 slot_choices |
| ④ 表面装饰 | 叠加表面细节 | 无 | 本模板不加装饰 slot；base_shell 的 hinge_knuckle / mirror_bezel / pans 都是结构性 visual（不是纯装饰）。理由：source pool 无独立装饰 fork anchor。若后续需要，可加 `record_only` mirror_bezel 或 accent_ring 但不列 slot。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | base_len_scale [0.90, 1.15] / base_width_scale [0.90, 1.15] / base_height_scale [0.90, 1.20] / lid_open_angle [0.10, 0.35] rad。**运动包络**：`lid_hinge` REVOLUTE axis=(-1,0,0)，opening 方向 = 抬起 +Z，`[闭合=-1.75, 可行上界=+0.35]`（open 端上限，闭合端由源 `-1.745` 派生）；`latch_button_slide` PRISMATIC axis=(0,1,0)，`[0, 0.005]` m。**motion_test_plan**：调用 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)`；targeted `ctx.pose(...)` 覆盖 (a) lid 全开状态 lid AABB top > base AABB top + 0.030 (b) lid 闭合状态 lid overlaps base xy > 0.03 (c) push_latch 时 button 前移 y > 0.0015 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类：painted (champagne_gold / rose_gold / pastel_mint) + plastic (translucent_navy / matte_black)，共 5 个 palette_style（≥3 要求达标，涵盖 ≥2 material class）。source_type=record_only（parents） + world_knowledge_extrapolation（realistic cosmetic palettes） |

**收尾自检**：`template batch` 0-9 seed 渲染时验证：
- ③ Planar Boundary 拉得开（rounded_rectangle / round / clover 都出现）
- powder_layout N∈{2,4,6,8} 全部出现
- push_latch 时 button 前伸不穿模
- lid 全开状态 mirror 竖起
- 5 个 palette_style 至少 3 出现，材质大类 ≥ 2

## 采样与覆盖审计

总组合数：3 (case_form) × 3 (closure) × 4 (powder_layout) × 5 (palette_style) = **180**（palette 是外观通道，不计结构 distinct；结构 distinct = 3×3×4 = **36**）。

理由：sweep 0-35 (36 seeds) 恰好覆盖结构组合上界一个数量级。若单个 slot 覆盖不满，扩到 corner stage。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：deterministic procedural sampling per-seed (weighted for `powder_layout_count`, uniform for others)。compatibility matrix：clover 时若 N≥6，pan 网格需缩小 `pan_r` 至 0.008–0.010 m 以适配非凸 cavity（由 §7 inequality 回缩处理）。

Topology target：1000-seed slot choice tuple 覆盖 ~180 combos（远低于 300，因组合空间本身饱和 = 100% 实现率）；report-only。

Controlled local parameterization：`base_len_scale / base_width_scale / base_height_scale` 是主要连续 scale；`lid_open_angle` 是关节行程 scale；均在 `resolve_config` clamp。scale 之间独立采样；跨部件约束（pan grid 拟合 cavity）由 inequality 显式回缩。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted `powder_layout_count`, uniform case_form/closure/palette_style | slot_choices_for_seed matches build choices |
| compatibility matrix | clover + N≥6 → shrink pan_r 到 ≤ 0.010 m；无强制互斥 | clover cavity 内 pan 不越界 |
| controlled local variation | ±10-15% scale on base dims + open angle | proportions vary without breaking interfaces / hinge origin |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass, 0-999 maturity audit | axis_realization; corner failures |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| case_form | 3 | yes | yes | ③ Primary Form Family slot |
| closure | 3 | yes | yes | 涵盖 hinge_only / push_latch / over_center_latch |
| powder_layout | 4 | yes | yes | multiplicity 轴，N∈{2,4,6,8} |
| palette_style | 5 (外观) | yes | yes | ⑥ 涂装，不计结构 distinct |

## Validator

- `slot_choices_for_seed(seed)` 返回实现的 (case_form, closure, powder_layout, palette_style) tuple
- `config_from_seed(seed)` 对所有普通 seed 使用 deterministic procedural sampling；seed=0 不特殊
- compatibility：clover + 大 N 通过 pan_r/pan_span 回缩解决，不用互斥 gate
- 无 regression overrides
- 所有 continuous scale 在 `resolve_config` clamp
- `lid_hinge` REVOLUTE axis=(-1,0,0)，origin 落在 hinge_pin 中心
- push_latch 时 `latch_button_slide` PRISMATIC axis=(0,+1,0)，travel ≤ 0.005 m
- `hinge_pin`↔`lid_barrel` element-scoped `allow_overlap`（captured-pin）
- `run_makeup2_tests` 调用 `fail_if_parts_overlap_in_sampled_poses` + 至少 3 个 targeted `ctx.pose(...)`

## Reject cases

- 无 mirror 或无 mirror 面 material（→ 不是化妆粉盒）
- lid 全开状态 mirror 不高于 base（说明 hinge_pin origin 错）
- lid 闭合状态 lid 未覆盖 base pan wells（→ hinge closed 端有误）
- push_latch 时 button 与 latch_housing 不共线（→ prismatic axis 错）
- 任何 pan 越出 base 外轮廓（→ pan_r/pan_span/cavity fit 不对）
- palette_style 未真正驱动 material（→ 只换 name 不换 rgba）

## 与相邻类别的边界

- 不该混入 **`Accessories_Cushion`（cushion 粉盒）**：cushion 强调 slide / clamshell / puff_tray 内部机构；本类无 clamshell 无 slide，主打 case_form ③ 家族 + pans 阵列。
- 不该混入 **首饰盒 / pill box**：这些无 mirror + powder pans。
- 不该混入 **口红管 / 香水瓶**：非翻盖粉盒形态。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Author draft; spec+template continuous authoring per README.md workflow. |

## 模板实现备注

- 共享 helper：`_rounded_shape(case_form, sx, sy, sz, r)` 一次派发出 3 种 planar boundary。
- pan mesh 用 `mesh_from_geometry(Box(...))` 共享一份 Mesh 供 N 个 pan visual 引用。
- captured-pin overlap：`hinge_pin`↔`lid_barrel` element-scoped allow_overlap。
- push_latch 时 latch_button 与 latch_housing 之间需 element-scoped allow_overlap（sliding capture）。
- palette_style 通过 `PALETTES[style]` dict 表驱动 `mats["shell"|"mirror"|"metal"|"pan_i"|"accent"]`；每个 `.visual(...)` 都从 `mats` 取 material，不硬编 rgba。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | case_form | rounded_rectangle | rec_picturex_0611__makeup2__002__png_e452c59a23e8409d9b7df37aa3754bfb | L19-95 | base+lid mesh baseline |
| S2 | case_form | round | rec_0611_makeup2_var_case_form_round | L45-171 | round base+lid mesh |
| S3 | case_form | clover | rec_0611_makeup2_var_case_form_clover | L54-206 | clover base+lid mesh (4-lobe union) |
| S4 | closure | hinge_only | rec_picturex_0611__makeup2__002__png_e452c59a23e8409d9b7df37aa3754bfb | L202-225 | REVOLUTE lid_hinge baseline |
| S5 | closure | push_latch | rec_0611_makeup2_var_closure_push_latch | L119-311 | latch_button PRISMATIC + housing + hook |
| S6 | closure | over_center_latch | rec_0611_makeup2_var_closure_over_center_latch | L134-... | fixed catch bar 几何 |
| S7 | powder_layout | n2 | rec_0611_makeup2_var_powder_layout_2_well | L126-155 | 2-well grid |
| S8 | powder_layout | n4 | rec_picturex_0611__makeup2__002__png_e452c59a23e8409d9b7df37aa3754bfb | L151-163 | 2×2 grid |
| S9 | powder_layout | n6 | rec_0611_makeup2_var_powder_layout_6_well | L162-177 | 3×2 grid |
| S10 | powder_layout | n8 | rec_0611_makeup2_var_powder_layout_8_well | L137-146 | 4×2 grid |
| S11 | palette_style | translucent_navy | rec_picturex_0611__makeup2__001__png_88723ca63e414320b8fa80969891b63a | L209-215 | source palette 001 |
