# Shopping bucket (hand-held shopping basket) — Modular Spec

> 来源小类：`picture/Bag_Suitcase/Shopping bucket`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Bag_Suitcase__Shopping_bucket.md`。
> **同步前置**：本 spec 引用的 `model.py:Lx-Ly` 来自该小类的 workbench-only 五星样本（3 个 parent + 16 个 fork 槽位变体 + 3 个 qwen 补造：solid-wall / N=3 / N=5 嵌套堆叠），目前仍在 `articraft_data` 仓库，**尚未同步进本仓库 `data/records/`**。进入 SPEC_ONLY 实现前需先把这些 record 目录 + 物化缓存同步进本仓库并批量 `rating=5`（FORK_VARIANTS §7）。本 spec 行号按各样本 `articraft_data` 当前 `revisions/rev_000001/model.py` 计；同步后按本仓库行号 rebase。引用以 part/joint/helper **名字** 为准（`_basket_mesh`/`_tub_mesh`/`_handle_mesh`/`basket_{i}`/`handle_{i}`/`tub_to_caddy` 等），行号仅作定位。
>
> **登记缺口**（继承自 source map）：这批样本未进 `picture_expansion/generated_assets.jsonl`（20 个手动 API fork + 3 个 qwen3.7-max 补造跑了 `--skip-search-index`）；后续可回填 generated_assets.jsonl，不影响本 spec 的来源完整性（record_id 已逐一列出）。

## 元信息
| 项 | 值 |
|---|---|
| slug | `shopping_bucket` |
| template path | `agent/templates/Bag_Suitcase_Shopping_bucket.py` |
| test path (optional) | `tests/agent/test_shopping_bucket_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `spec_only` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: body_form + wall_style + handle + lid_closure + interior，**外加** `basket_count` 嵌套堆叠 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 22（3 parent + 16 槽位 fork 变体 + 3 qwen 补造；均 converged，compile rc=0、均有 URDF，workbench-only）|
| read_count | 全部被采纳为 module source 的样本读其 `model.py`（3 parent 全文 + 每个槽位候选的 mesh helper / joint 装配段 + solid-wall 全文 + N=3 / N=5 嵌套链全文）|
| read_scope | all 5-star samples in this category（提供 module 来源的样本全部读；4 个出类 divergent 记入 §10/§11，不进核心槽位）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；未采用样本不列清单 |

冗余/分流说明：
- 3 个 parent（`c383d977` 红槽口拱把、`254643d5` 蓝槽口拱把、`b050efd5` 冲孔壁+双折叠提梁）同属基线格子 `body:rectangular × wall:slotted_perforated × handle:fixed/folding × lid:none × interior:plain`，提供共享 helper 与 bail-handle 基线；不重复登记同格子样本。
- `dual_independent_handles`（`08aedfc5`）与 parent `b050efd5` 的双折叠提梁同构，作 dual 变体对照样本，不提供新拓扑。
- 4 个 divergent（轮拖 / 折叠收平 / 双层 / 底抽屉）已飘出"手提购物篮"语义，按 §8.1 折出核心模板，记作 §10 compatibility-matrix 排除素材 + §11 边界。

## 核心身份

手持 / 可嵌套的购物篮（hand-held shopping basket / shopping bucket）：一只开口浅篮，长轴沿 X（X 宽于 Y），坐地于 z=0；薄壁中空 tub（loft 双圆角矩形 → `shell` 开口），厚卷边 rim，侧壁可为竖槽冲孔 / 钢丝网 / 全封闭光面；顶部一只或两只 bail 提把绕 X 轴 REVOLUTE 摆动；可选顶盖 / 蛤壳 / 前门 / 倒料板（lid_closure 主开合机构）与可选内部机构（固定隔断 / 可取 PRISMATIC 内托）。**多重性轴**：店门口那种 N 只强内收锥度篮**竖直嵌套堆叠**成一摞——每篮自带摆动 bail 把（REVOLUTE），篮体间 FIXED 嵌套链。默认成熟域：N∈[1,8] 的一摞嵌套篮（1-6 常见、7-8 长尾），单篮（N=1）即各 parent / 各单体槽位变体。活动语义是"每篮 bail 把绕短壁 pivot 线摆起 + 可选 lid/前门开合 + 可选内托提起"。

不该混入：带轮拖行的购物手推车 / 拉杆 trolley（升降拉杆 + 滚轮底盘，已飘出手提语义）、行李箱 suitcase（带轮拉杆硬壳）、通用容器 / 收纳箱（无提把 + 无开合机构，是单独的 `bag_suitcase_box` 模板）。

## 槽位 + 候选模块表

> **建模注记（重要，对齐 fence_cascade 的处理）**：物理上 `body_form` / `wall_style` 是同一只 tub mesh 的属性（footprint 形态 + 壁面材质由 `_tub_mesh(...)` 一次发射，不是两个串联 slot，不共享 mating face）；`handle` / `lid_closure` / `interior` 各自挂到 tub（parallel children），不串成链。正确结构是 **一只参数化 basket 模块 `basket(body_form, wall_style, handle, lid_closure, interior)`，沿堆叠链复制 N 次**（variable-multiplicity stack）。下面把 5 个属性列为"模块轴"以对齐 schema 候选表；它们的笛卡尔积 × N 共同构成拓扑多样性（见 §9）。

### Slot A：body_form（体形 / 足迹——被复制的 tub 主体形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rectangular（基线） | rec_..._c383d977 / _254643d5 / _b050efd5（3 parent）| `_tub_mesh` L67-135（c383d977）| eligible if compatible | loft 双圆角矩形 tub（L_BOT→L_TOP 锥度），矩形足迹基线 |
| rounded_oval_deep | rec_..._2ec27abe | `_tapered_oval`/`_ellipse_at_z`/`_build_body` L76-167 | eligible if compatible | 椭圆截面深篮 tub（`_tapered_oval` 双椭圆 loft + 椭圆 rim/槽）|
| hexagonal_footprint | rec_..._50948264 | `_hex_verts`/`_hex_prism`/`_tapered_hex`/`_build_body` L76-289 | eligible if compatible | 六边形棱柱足迹 + 每面 lattice 壁 + 六边 rim |
| round_cylindrical_bucket | rec_..._e78fd94a | `_bucket_mesh` L65-152 | eligible if compatible | 圆筒 / 桶式 tub（圆截面，X≈Y，桶身锥度）|
| tapered_stackable | rec_..._6a8aa2c9 | `_tub_mesh` L73-179 | eligible if compatible | 强内收锥度矩形 tub（L_BOT≪L_TOP，可叠）——multiplicity 复制源的体形原型 |
| shallow_wide_tray | rec_..._b5cd2054 | `_tub_mesh` L68-138 | eligible if compatible | 浅宽托盘式 tub（H 矮、X 宽，浅足迹）|

### Slot B：wall_style（壁面 / 材质——同一 tub mesh 的壁面处理）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| slotted_perforated_plastic（基线） | rec_..._c383d977（红）/ _254643d5（蓝，`SlotPatternPanelGeometry`）| `_tub_mesh` 槽切段 L114-122（c383d977）/ `_slot_wall`+walls L25-70（254643d5/b050efd5）| eligible if compatible | 竖槽 / 冲孔塑料壁（`shell` 后 `cut` 竖槽 或 `SlotPatternPanelGeometry` 拼壁）|
| steel_wire_mesh | rec_..._1d416a15 | `_wire_segment`/`_wall_extent_*`/`_build_wire_basket` L77-330 | eligible if compatible | 不锈钢丝网篮：竖 / 横 wire 网格 + 粗 frame wire + 角柱（`_wire_segment` 焊接网）|
| solid_smooth_plastic | rec_..._77eca573 | `_tub_mesh` L59-120 | eligible if compatible | 全封闭光面 tub（`shell` 后**不切任何槽**；连续封闭壁；2026-06-16 补的硬空格）|

硬约束记录：wall_style 仅 3 candidate（达目标下限 3）。理由：真实购物篮壁面在样本中就是这三族（开槽塑料 / 钢丝网 / 实心光面）；多样性主要由 body_form × lid_closure × N 提供（见 §9）。

### Slot C：handle（提把类型——绕 X 轴 REVOLUTE 摆动 / 或 PRISMATIC 拉杆）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| fixed_central_arched（基线） | rec_..._c383d977 / _254643d5 | `_handle_mesh` L138-165 + `tub_to_handle` L198-211（c383d977）| eligible if compatible | 单中央拱把，绕短壁 pivot 线（X 轴）REVOLUTE，±95°，pin-in-boss 捕获 |
| single_swing_bail | rec_..._287b16ac | `_bail_handle_mesh` L214-255 + `bail_joint` REVOLUTE L281-298 | eligible if compatible | 单中央半圆摆动提梁，X 轴 REVOLUTE（folded↔upright）|
| dual_folding_bail | rec_..._35468439 | `_bail_handle_mesh` L243-282 + `handle_0`/`handle_1` REVOLUTE L309-339 | eligible if compatible | 两侧独立折叠提梁，2 个 X 轴 REVOLUTE（各折向自侧）|
| single_telescoping_pull_up | rec_..._09d0f958 | `_build_telescoping_handle` L247-344 + `tub_to_handle` **PRISMATIC** L375-388 | eligible if compatible | 中央 U 形伸缩拉杆，**Z 轴 PRISMATIC** 抬升（区别于其它 REVOLUTE 把）|

硬约束记录：dual_independent_handles（`08aedfc5`）与 dual_folding_bail 同构，不另列为 candidate。handle 4 candidate（达 3-6 目标）。

### Slot D：lid_closure（**主开合机构槽**——篮子的盖 / 门动作；含 `open_no_lid` 空机构）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| open_no_lid（基线） | rec_..._c383d977 / 各 parent | —（无 lid part，敞口）| eligible if compatible | 敞口无盖（不发射 lid part / lid joint）|
| hinged_top_lid | rec_..._ab5a00e2 | `_build_lid` L216-273 + `body_to_lid` REVOLUTE L306-319 | eligible if compatible | 单顶翻盖板，绕 +Y 长 rim 边 X 轴 REVOLUTE（闭合 q=0 盖座 rim，开 ~115°）|
| two_leaf_clamshell | rec_..._2822118b | `_lid_leaf_mesh` L173-215 + `tub_to_left_lid`/`tub_to_right_lid` REVOLUTE ×2 L287-318 | eligible if compatible | 双叶蛤壳盖，两片各绕 ±Y 长 rim 边镜像 REVOLUTE，中线对开 |
| drop_front_gate | rec_..._4598924c | `_build_gate_panel` L317-397 + `tub_to_gate` REVOLUTE L495-511 | eligible if compatible | 前壁掉头门板，绕前壁**底边**（z≈0）X 轴 REVOLUTE 下翻（取货）|
| tilt_down_front_panel | rec_..._85ab5e66 | `_front_panel_mesh` L155-193 + `tub_to_front_panel` REVOLUTE L255-268 | eligible if compatible | 前壁低位倒料板，绕前壁底边 X 轴 REVOLUTE 前倾倒料 |

### Slot E：interior（内部机构——固定 / 可取 PRISMATIC）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| plain（基线） | 各 parent | —（无内部机构）| eligible if compatible | 无内部件（不发射 divider / caddy）|
| two_compartment_divider | rec_..._31a4dbd5 | `_build_body` 内 divider 段 L168-186 | eligible if compatible | 固定中央隔断墙（Y=0），union 入 tub（无独立 joint，双格）|
| removable_inner_caddy | rec_..._5030ab7f | `_caddy_mesh`/`_caddy_grip_mesh` L194-292 + `tub_to_caddy` **PRISMATIC** L348-363 + `caddy_to_grip` REVOLUTE L377-390 | eligible if compatible | 可取内托盘：Z 轴 PRISMATIC 提起 + 托上折叠 REVOLUTE 小提梁 |

硬约束记录：interior 3 candidate（达下限 3）；样本只支持这三族（无内部 / 固定隔断 / 可取内托）。

### 共享 helper（非 slot，多 module 公用，主来源 parent `c383d977` + 嵌套样本 `27719f51`）

| helper | 5_star_source | model.py:Lx-Ly | 用途 |
|---|---|---|---|
| `_tub_mesh` / `_basket_mesh` | c383d977 / 27719f51 | c383d977 L67-135 / 27719f51 `_basket_mesh` L77-143 | loft 圆角矩形 tub + `shell` 开口 + 卷边 rim + 槽切 + 短壁 pivot boss |
| `_handle_mesh` | c383d977 / 27719f51 | c383d977 L138-165 / 27719f51 `_handle_mesh` L146-175 | 拱形 bail 把（XZ `threePointArc` sweep + 两端 pivot 膝节）|
| `Inertial.from_geometry`/`Box` | 各样本 | — | 每 part 的惯量盒 |

## 槽位图（slot graph）

pattern: mixed（参数化 basket 模块 + 变长嵌套堆叠 multiplicity 链；模块内 parallel children）

```
basket_0(body_form, wall_style, handle, lid_closure, interior)
   ├── [basket_0_to_handle_0:  REVOLUTE X, origin=short-wall pivot @ PIVOT_Z] ──> handle_0
   ├── [body_to_lid_0:         REVOLUTE X, origin=rim 长边 / 前壁底边]        ──> lid_0*   (lid_closure≠open_no_lid 时)
   ├── [tub_to_caddy_0:        PRISMATIC Z, origin=floor seat]              ──> caddy_0*  (interior=removable_inner_caddy 时)
   └── [basket_0_to_basket_1:  FIXED Z, origin=(0,0,NEST_STEP)]            ──> basket_1(同参数)
         ├── [basket_1_to_handle_1 REVOLUTE X] ──> handle_1
         └── [basket_1_to_basket_2 FIXED Z] ──> basket_2
               └── ... ──> basket_{N-1}   (每篮自带把 + 可选 lid/caddy；FIXED 嵌套链)
```

接口点位与 joint 语义：
- **嵌套链接口**：上游 `basket_{i}` 的内腔（强内收锥度）↔ 下游 `basket_{i+1}` 的底外形；FIXED，`origin=(0,0,NEST_STEP)` 沿 +Z 等距递增（嵌套深度 NEST_STEP≈0.065-0.08m）。`basket_0` 为根（坐地 z=0）。
- **handle 接口**：每篮 tub 短壁 pivot boss（X 轴 pin-in-boss 捕获）↔ handle 端 pivot 膝节；REVOLUTE +X 轴，`origin=(0,0,PIVOT_Z)`（origin 落在真实 pivot 线硬件上，满足 baseline `fail_if_articulation_origin_far_from_geometry` 0.015）。multiplicity 下**每篮一把**（`basket_{i}_to_handle_{i}`）。
- **lid 接口**（lid_closure≠open_no_lid）：顶翻盖 origin 在 +Y 长 rim 外边（z=rim 高）；蛤壳两片 origin 在 ±Y 长 rim；drop_front / tilt_down origin 在前壁**底边**（z≈0）。全部 REVOLUTE ±X 轴。
- **caddy 接口**（interior=removable_inner_caddy）：tub 内腔底中心；PRISMATIC +Z 轴 `origin=(0,0,CADDY_FLOOR_SEAT)`，q=0 内托坐底，提起到 bail 顶。caddy 上还有 `caddy_to_grip` REVOLUTE 折叠小提梁。
- **mating policy**：bail pin-in-boss 是 captured-pin（销在膝节/boss 内），几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + 逐篮 element-scoped `allow_overlap(basket_i↔handle_i)` 守 overlap；嵌套链篮间 / 折叠把间在堆叠姿态相互穿插，逐对 `allow_overlap`（见 N=5 样本 L360-405）。lid 闭合姿态盖座 rim crest 用 element-scoped `allow_overlap`（见蛤壳样本 L597-612）。
- **rest pose**：所有 handle = upright（或 N>1 时 folded-down 嵌套姿态）、所有 lid q=0 闭合、caddy q=0 坐底。嵌套链平移不变（每篮 +NEST_STEP），强锥度保证篮壁不互相穿模（taper clearance 见 N=5 L312-318）→ 小 N 通过即任意 N 通过。
- **互斥 / 可选**：`lid_closure=open_no_lid` 与 `interior=plain` 是空机构（不发射对应 part/joint）；其余为可选 moving child。lid_closure 各候选互斥（一次只一种盖机构）。

## 每槽位 Module Emits / Interfaces

### basket 模块（body_form=tapered_stackable + handle=single_swing_bail 为例，其余属性仅换对应子件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `basket_{i}`（visual: `tub_shell`[ + 钢丝网 wire visuals / + 固定 divider]）| 27719f51 `_basket_mesh` L77-143 / 各 body_form / wall_style 源 |
| internal joints | 无（单篮 tub 内部无活动件；rim / 槽 / boss / 固定 divider 均为同一 part 的 visual / union）| divider: 31a4dbd5 L168-186 |
| upstream interface | 底外形（嵌套链 FIXED 的 child 接口；落在 part 原点附近）| 27719f51 嵌套链 L233-240 |
| downstream interface | 内腔锥面（嵌套链 FIXED 的 parent 接口，`origin=(0,0,NEST_STEP)`）| 27719f51 L233-240 |

### handle 子模块（每篮发射，REVOLUTE；telescoping 为 PRISMATIC）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle_{i}`（visual: `bail_bar`）；dual: `handle_{i}_front`/`_back` 各一 | 27719f51 `_handle_mesh` L146-175 |
| internal joints | `basket_{i}_to_handle_{i}` REVOLUTE +X，origin=(0,0,PIVOT_Z)，0..π / ±95° | 27719f51 L215-230 |

### lid_closure 子模块（lid_closure≠open_no_lid 时，挂 basket_{i}）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid_{i}`（顶翻盖）/ `left_lid_{i}`+`right_lid_{i}`（蛤壳）/ `gate_{i}`（前门）/ `front_panel_{i}`（倒料板）| ab5a00e2 / 2822118b / 4598924c / 85ab5e66 |
| internal joints | `body_to_lid_{i}` REVOLUTE ±X（顶翻盖 / 蛤壳 ×2 / 前门底边 / 倒料板底边）| ab5a00e2 L306-319 等 |

### interior 子模块（interior≠plain 时）
| emits | 描述 | 来源 |
|---|---|---|
| parts（divider）| 无独立 part（divider 墙 union 入 `basket_{i}` tub）| 31a4dbd5 L168-186 |
| parts（caddy）| `caddy_{i}`（+ `caddy_grip_{i}`）| 5030ab7f L340-390 |
| internal joints（caddy）| `tub_to_caddy_{i}` PRISMATIC +Z + `caddy_to_grip_{i}` REVOLUTE +X | 5030ab7f L348-390 |

### 链（multiplicity）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `basket_0..basket_{N-1}`（+ 每篮 handle / 可选 lid / caddy），共享 mesh helper，N 个 part 复用同一 mesh | 27719f51 L181-213 |
| joints | `basket_{i}_to_basket_{i+1}` FIXED +Z，i=0..N-2，origin=(0,0,NEST_STEP) | 27719f51 L232-240 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | rectangular / rounded_oval_deep / hexagonal_footprint / round_cylindrical_bucket / tapered_stackable / shallow_wide_tray | rectangular | choice | 由 deterministic procedural sampler 选 | module table |
| wall_style | enum | slotted_perforated_plastic / steel_wire_mesh / solid_smooth_plastic | slotted_perforated_plastic | choice | sampler 选 | module table |
| handle | enum | fixed_central_arched / single_swing_bail / dual_folding_bail / single_telescoping_pull_up | fixed_central_arched | choice | sampler 选 | module table |
| lid_closure | enum | open_no_lid / hinged_top_lid / two_leaf_clamshell / drop_front_gate / tilt_down_front_panel | open_no_lid | choice | sampler 选；含空机构 | module table |
| interior | enum | plain / two_compartment_divider / removable_inner_caddy | plain | choice | sampler 选；含空机构 | module table |
| basket_count (N) | int | 声明域 [1, 8]；**sweep 采样域 [1, 8]**（偏小加权：1-6 高频、7-8 稀疏长尾）| 1 | conditional→slot_choice | 编入 slot_choice 为 `n{N}`（拓扑维度）；见 §8 | 27719f51 N=5 / 465484ba N=3 multiplicity |
| material_style | enum | red_plastic / blue_plastic / galvanized_steel / charcoal | red_plastic | palette | palette only，**不计入 slot_choice** | palette |
| body_len_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 L_TOP/D_TOP→L_BOT/D_BOT（保锥度比），clamp | resolve clamp |
| body_height_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 H→PIVOT_Z→rim/handle 高度，clamp | resolve clamp |
| taper_scale | float | [0.85, 1.15] | 1.0 | conditional | 锥度强度（L_BOT/L_TOP 比）；N>1 时下限抬高保证嵌套 clearance | resolve clamp（见下不等式）|
| nest_step_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 NEST_STEP（嵌套垂直步距），clamp | resolve clamp |
| handle_arch_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 ARCH_RISE（提把弧高），clamp | resolve clamp |
| joint_limit_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 handle / lid `motion_limits`，clamp | resolve clamp |
| (—) | constraint | — | — | inequality | 嵌套 clearance：`L_BOT + (L_TOP-L_BOT)·NEST_STEP/H − 2·WALL > L_BOT + 0.005`（N>1 时必满足，否则按比例增 taper 或回缩 nest_step；见 N=5 L312-318）| 接口 / clearance |
| (—) | constraint | — | — | inequality | lid 闭合不穿 handle：bail upright 顶 z > lid 平面 + 余隙，否则降 ARCH_RISE 或 grandfather 该对 overlap | 接口 / clearance |

所有连续 scale 在 `resolve_config` 中 clamp；**每个 build 解析一次，全部 basket 统一使用**（保证嵌套链上 basket 全等 → N-不变）。scale 只动安全比例 / clearance / 细节尺寸，绝不改变 body_form / wall_style / handle / lid_closure / interior / N 的拓扑。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（嵌套堆叠）：

- **count_param**：`basket_count`（模板内变量 N_BASKETS / N）。
- **N_range**：声明产品域 **[1, 8]**（一摞嵌套购物篮的现实上限较小，店门口堆叠通常 1-8 只）；`config_from_seed` 的 **sweep 采样域 [1, 8]**（偏小加权，1-6 高频、7-8 稀疏长尾）。N=1 即单篮（各 parent / 各单体槽位变体的退化情形：不发射嵌套 FIXED 链）。
- **sampling domain**：`config_from_seed` 用 `rng.choices((1..8), weights=偏小)`（1-6 权重高、7-8 稀有长尾）；`resolve_config` 把任意外部 config 的 N clamp 到 [1, 8]。
- **copied object**：整只 basket 模块——tub（body_form + wall_style）+ 自带 bail handle（+ 可选 lid + 可选 caddy），由共享 helper（`_basket_mesh` / `_handle_mesh`）发射，N 个 part 复用同一 tessellated mesh（大 N 仍便宜）。
- **naming**：`basket_{i}` / `handle_{i}`（+ `lid_{i}` / `caddy_{i}`），`for i in range(N)`（N=3 / N=5 变体已用此结构，可直接作 module 源码）。
- **placement**：沿 +Z **绝对式**等距递增——`basket_0` 坐地 z=0，`basket_{i+1}` 经 FIXED `origin=(0,0,NEST_STEP·nest_step_scale)` 落在 `basket_i` 上方（嵌套深度）。绝对式（每对 origin 恒定）是 N-不变前提。
- **joint policy**：每个复制件**独立活动**——`basket_{i}_to_handle_{i}` REVOLUTE +X（每篮一把，0..π）；篮体间 `basket_{i}_to_basket_{i+1}` FIXED +Z 嵌套链；可选 lid / caddy joint 随每篮发射。
- **source/gating**：copy-logic 源取 N=5 `27719f51` L181-240（`for i in range(N)`: `basket_{i}` + `handle_{i}` + 各 REVOLUTE + N−1 个 FIXED 嵌套）与 N=3 `465484ba` L187-240（同构）；**不取 parent**（parent 是 N=1 单篮，未循环化）。

## 拓扑多样性审计

总组合数：body_form(6) × wall_style(3) × handle(4) × lid_closure(5) × interior(3) × N采样数(8，即 {1..8}) = **8640**。

仅 body_form × lid_closure = **30 ≥ 10** 已可过门控；叠 N 与其余轴后充裕。


seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 五个 named slot（笛卡尔积近全合法，仅少量 gating 见下），再 `rng.choices` 加权 N∈[1,8]（1-6 高频、7-8 长尾），再 uniform 各连续 scale。compatibility matrix 排除非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计按 ≥300 富类别口径观察（8640 组合的采样空间足够；受真实结构词汇表约束的轴是 wall_style(3) / interior(3)，但 body_form(6) × lid_closure(5) × handle(4) × N(8) 已撑开）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 6 个 scale（body_len / body_height / taper / nest_step / handle_arch / joint_limit）。全部 `resolve_config` clamp + 每 build 统一应用。其中 `taper_scale` 为 **conditional**：N>1 时其下限按嵌套 clearance 不等式抬高（先采 N → 解析 taper 范围 → 采 independent scale → 派生 L_BOT → 用 clearance 不等式投影 / 回缩）。其余 scale independent。跨部件依赖（嵌套 clearance、lid-handle 不穿）显式落在 §7 的两条 inequality，在 `resolve_config` 内求解，不留到 builder。这些 scale 不破坏 嵌套链 origin、handle pivot 接口、lid hinge origin、N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 五 named slot（近全正交），再 `rng.choices` 加权 N∈[1,8]（1-6 高频、7-8 长尾），再 uniform 各 scale | slot_choices_for_seed 含 `("basket_count", f"n{N}")` 且与 build 一致 |
| compatibility matrix | (1) N>1（多篮嵌套堆叠）时强制 `body_form ∈ {rectangular, tapered_stackable, round_cylindrical_bucket, shallow_wide_tray}` 且抬高 taper（需强内收锥度才能嵌套；oval/hex 嵌套穿模风险高，降级为 tapered_stackable）；(2) N>1 时 `lid_closure=open_no_lid` 且 `interior=plain`（堆叠的篮不带盖 / 不带内托，避免堆叠姿态盖 / 托互穿——堆叠摞只复制 tub+bail）；(3) N=1 时五槽全正交无 gate。排除 §11 的 4 个 divergent（轮拖 / 折叠 / 双层 / 抽屉）出 enum | 无 floating / collision / 嵌套穿模 / 出类目 / max N |
| controlled local variation | 6 个 clamped scale，每 build 统一；taper conditional 随 N | 比例变化不破坏 嵌套链 origin / handle pivot / lid hinge / 坐地 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐对 / 逐篮 QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 6 | yes | yes | |
| wall_style | 3 | yes | yes | 真实壁面三族（开槽 / 钢丝网 / 实心）|
| handle | 4 | yes | yes | 含 REVOLUTE×{1,1,2} + PRISMATIC 拉杆 |
| lid_closure | 5 | yes | yes | 主开合机构（含 open_no_lid 空机构 + 4 种 REVOLUTE 盖 / 门）|
| interior | 3 | yes | yes | 含 plain 空 + 固定 divider + PRISMATIC caddy |
| basket_count (N) | 8（采样域 {1..8}，1-6 高频 / 7-8 长尾）| yes | yes | 拓扑维度，编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("basket_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，N 采样域 ⊆ [1,8]
- `resolve_config` 把 basket_count clamp 到 [1,8]，各 scale clamp 到声明范围；taper conditional 随 N 解析；两条 clearance inequality 在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（N>1 强制可嵌套 body_form + 抬 taper + open_no_lid + plain；排除 §11 divergent）
- 连续 scale clamp 后不破坏 嵌套链 origin / handle pivot 接口 / lid hinge origin / 坐地 / N 复制
- 关键 joint：每篮 `basket_{i}_to_handle_{i}` REVOLUTE +X 轴（abs(axis[0])>0.99）；N−1 个 `basket_{i}_to_basket_{i+1}` FIXED +Z；可选 lid REVOLUTE ±X / caddy PRISMATIC +Z；telescoping handle PRISMATIC +Z
- captured-pin：逐篮 element-scoped `allow_overlap(basket_i, handle_i)`（pin-in-boss）；N>1 嵌套姿态逐对 `allow_overlap`（篮间 / 折叠把间 / 把穿篮壁，见 27719f51 L360-405、465484ba L361-416）；lid 闭合盖座 rim element-scoped allow_overlap
- copied object 遵循 `basket_{i}` / `handle_{i}` 命名 + 绝对式 +Z 等距 placement + 统一 joint policy
- grandfather：bail pin-in-boss / 嵌套捕获省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把 N 当普通 int 参数、不进 slot_choice → 单篮与多篮堆叠 slot_choice 同形，损失拓扑维度（即便 body×lid=30 仍过门控，但 N 维度丢失，违反 §8/§9 硬要求）。
- N>1 时允许 oval / hexagonal body_form 或弱锥度 → 嵌套篮壁互穿（taper clearance 不等式失败）；必须 gate 到强锥度可嵌套 body_form。
- N>1 时仍发射 lid / caddy → 堆叠姿态盖 / 托互穿、part 数爆炸；堆叠摞只复制 tub+bail。
- placement 写成累加（`prev_z + step`）而非绝对式每对恒定 origin → 大 N 浮点漂移破坏 N-不变。
- 给 bail pin-in-boss / 嵌套捕获补 MatingContract 硬对接 → captured-pin 几何对不上，mating-gap FAIL；应 grandfather。
- handle pivot / lid hinge origin 放在地面或任意点而非真实 pivot 线硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异（material_style 是 palette，不计 slot_choice）。
- 把 4 个 divergent（轮拖 / 折叠收平 / 双层 / 抽屉）塞回核心 enum → 出"手提购物篮"语义、引入轮 / 拉杆 / 多体框等未建模拓扑。
- lid 闭合 rest pose 设成张开角而非 q=0 闭合 → current-pose 与 viewer 目检不符。

## 与相邻类别的边界

- 不该混入：**wheeled shopping cart / trolley 购物手推车 / 拉杆车**（带轮底盘 + 升降拉杆，已飘出手提语义；divergent `43ad0ea4` 即此，移出核心模板）——理由：滚轮 + 拉杆是另一套 spine / root coordinate，非手提篮。
- 不该混入：**luggage suitcase 行李箱**（带轮拉杆硬壳箱体，开合是拉链 / 蛤壳但形态是行李，非购物篮）。
- 不该混入：**generic container / storage box 通用容器 / 收纳箱**（无提把 + 无开合机构，是单独的 `bag_suitcase_box` 模板）——理由：购物篮的类别身份是 bail 提把 + 开口浅篮 + 可嵌套堆叠，纯箱体不属本类。
- 排除项备注（divergent，§8.1 折出，记作 compatibility-matrix 素材）：`collapsible_four_hinged_walls`（四壁折叠收平 `651978c4`）、`two_tier_stacked`（双层叠放共享框 `332f5cbc`）、`under_basket_slide_drawer`（底部抽屉 `52ba7599`）。如后续想纳入，可各作一条薄可选轴并各补第二候选；当前出核心槽位。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 5 属性建模为单 basket 模块属性 + N 进 slot_choice 的方案；确认 N>1 的 compatibility gating——多篮堆叠强制可嵌套 body_form + open_no_lid + plain；确认 sweep N 上限 6 与声明域 6 一致的取舍；确认 wall_style / interior 仅 3 candidate 可接受）|

## 模板实现备注（可选）

- 共享 helper：`_basket_mesh` / `_handle_mesh`（来自 27719f51 L77-175）全 module 公用；N 个 basket part 复用同一 tessellated mesh（mesh 对象跨 part 复用安全）。body_form / wall_style 各换对应 mesh helper（`_tapered_oval` / `_hex_*` / `_bucket_mesh` / `_wire_segment` / 实心 `_tub_mesh`）。
- captured-pin / 嵌套 overlap：`run_shopping_bucket_tests` 里 `for i in range(N): ctx.allow_overlap(basket_i, handle_i, reason="pin-in-boss pivot")`；N>1 时再逐对 `allow_overlap`（篮间 / 折叠把穿篮壁 / 相邻把交错），照搬 27719f51 L360-405 与 465484ba L361-416 的循环结构。
- lid / caddy 仅在 N=1 发射（compatibility gating）；lid 闭合盖座 rim crest 用 element-scoped `allow_overlap`（蛤壳 2822118b L597-612）。
- 嵌套 clearance：`resolve_config` 必须先采 N → 若 N>1 抬 taper 下限并验 §7 第一条不等式（27719f51 L312-318 的 taper_clearance 公式），不满足则增 taper 或回缩 nest_step。
- chain joint 契约：嵌套 FIXED 与 fence_cascade 的 REVOLUTE 链类似，绝对式每对 origin 恒定（`(0,0,NEST_STEP)`），勿写累加。
- 参考模板：`agent/templates/Fence_Cascade_fences_MORE_THAN_1.py`（变长 N multiplicity-as-module-name + `("count", f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 mesh 复用 + 循环 allow_overlap 骨架，本类直接同构改编）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | (parent/helper) | rectangular + slotted + fixed bail | rec_..._c383d977 | `_tub_mesh` L67-135 / `_handle_mesh` L138-165 / `tub_to_handle` L198-211 | 共享 tub/handle helper + 基线 |
| S2 | (parent) | rectangular + SlotPattern wall + bail | rec_..._254643d5 | `_slot_wall` L25-37 / walls L47-84 / handles L86-115 | `SlotPatternPanelGeometry` 壁 + 双把对照 |
| S3 | (parent) | perforated + dual folding | rec_..._b050efd5 | `_slot_wall` + handles L86-115 | 双折叠提梁基线 |
| S4 | A | rounded_oval_deep | rec_..._2ec27abe | `_tapered_oval` L76-167 | 椭圆 body_form |
| S5 | A | hexagonal_footprint | rec_..._50948264 | `_hex_*` / `_build_body` L76-289 | 六边 body_form |
| S6 | A | round_cylindrical_bucket | rec_..._e78fd94a | `_bucket_mesh` L65-152 | 圆筒 body_form |
| S7 | A | tapered_stackable | rec_..._6a8aa2c9 | `_tub_mesh` L73-179 | 强锥度可叠 body_form（multiplicity 体形原型）|
| S8 | A | shallow_wide_tray | rec_..._b5cd2054 | `_tub_mesh` L68-138 | 浅宽托盘 body_form |
| S9 | B | steel_wire_mesh | rec_..._1d416a15 | `_wire_segment`/`_build_wire_basket` L77-330 | 钢丝网壁 |
| S10 | B | solid_smooth_plastic | rec_..._77eca573 | `_tub_mesh` L59-120 | 全封闭光面壁 |
| S11 | C | single_swing_bail | rec_..._287b16ac | `_bail_handle_mesh` L214-255 + joint L281-298 | 单摆动提梁 |
| S12 | C | dual_folding_bail | rec_..._35468439 | `_bail_handle_mesh` L243-282 + joints L309-339 | 双折叠提梁 |
| S13 | C | single_telescoping_pull_up | rec_..._09d0f958 | `_build_telescoping_handle` L247-344 + PRISMATIC L375-388 | 伸缩拉杆（PRISMATIC）|
| S14 | D | hinged_top_lid | rec_..._ab5a00e2 | `_build_lid` L216-273 + `body_to_lid` L306-319 | 顶翻盖 |
| S15 | D | two_leaf_clamshell | rec_..._2822118b | `_lid_leaf_mesh` L173-215 + joints ×2 L287-318 | 蛤壳双叶 |
| S16 | D | drop_front_gate | rec_..._4598924c | `_build_gate_panel` L317-397 + `tub_to_gate` L495-511 | 前壁掉头门 |
| S17 | D | tilt_down_front_panel | rec_..._85ab5e66 | `_front_panel_mesh` L155-193 + joint L255-268 | 前壁倒料板 |
| S18 | E | two_compartment_divider | rec_..._31a4dbd5 | `_build_body` divider 段 L168-186 | 固定中央隔断 |
| S19 | E | removable_inner_caddy | rec_..._5030ab7f | `_caddy_mesh` L194-292 + `tub_to_caddy` PRISMATIC L348-363 + grip L377-390 | 可取内托（PRISMATIC + REVOLUTE 小把）|
| S20 | multiplicity | basket_count N=5 | rec_..._27719f51 | `_basket_mesh`/`_handle_mesh` L77-175 + `for i in range(N)` L181-240 + allow_overlaps L360-405 | 嵌套堆叠 copy-logic 主源 |
| S21 | multiplicity | basket_count N=3 | rec_..._465484ba | `for i in range(N_BASKETS)` L187-240 + allow_overlaps L361-416 | 嵌套堆叠 copy-logic 对照（同构）|
