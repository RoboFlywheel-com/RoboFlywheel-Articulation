# pictureX_0611_Cabinet_with_drawers — modular spec (v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Cabinet_with_drawers` |
| template path | `agent/templates/pictureX_0611_Cabinet_with_drawers.py` |
| test path (optional) | `tests/agent/test_pictureX_0611_Cabinet_with_drawers_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `multiplicity` (primary) + `parallel_children` |

`pattern` 说明：一个刚性 carcass（root part）并联挂载 N 个独立抽屉（每个一条 PRISMATIC 滑轨），
抽屉数量/布局（drawer multiplicity）是**主多样性轴**；body_form（③）与 support_base（①）是结构 slot。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13 (5 origins + 8 variants) |
| read_count | 13 |
| read_scope | all 5-star samples in this category (5 origins fully; 8 forks) |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

一个 **drawers-only chest / dresser（纯抽屉柜）**：唯一的运动是一组可独立拉出的抽屉。刚性
carcass（顶/底/背/两侧 + 内部 runner）承载抽屉的负载路径；每个前脸开口都是一条独立的
PRISMATIC 抽屉滑轨，轴 (0,-1,0)（朝观察者 -Y 拉出），行程 ~0.27–0.30 m；每个抽屉是一个真实
的敞口盒（bottom + 两 side + 后壁）加一个 applied front 与 pull。默认成熟域是 2–6 个抽屉，
全宽竖叠 / 2 列网格 / 混合成对+全宽。

不该混入：
- **door cabinet（转门柜）**：门是 REVOLUTE 门扇 → 不是本类。
- **door+drawer sideboard（门+抽屉边柜）**：混合门与抽屉的 casework → 不是本类。
- **open shelving（开放搁架）**：暴露固定搁板、无抽屉 → 不是本类。

## 槽位 + 候选模块表

### Slot A：body_form（③ 主体形态家族 / Primary Form Family，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `rectilinear` | origin_anchor | 003 / 004 / 005 | 003 model.py:L266-L322；004 model.py:L202-L272；005 model.py:L237-L357 | Planar Boundary Form | eligible if compatible | 直箱 carcass（Box 侧板/背/顶/底），Box 抽屉前脸 |
| `bombe` | origin_anchor | 001 | 001 model.py:L31-L45（`_curved_front`）,L358-L387（bulged side posts） | Volumetric Envelope Form | eligible if compatible | 前脸 + 前侧柱外凸（抛物 bulge mesh，ExtrudeGeometry） |
| `oval_rounded` | origin_anchor | 002 | 002 model.py:L36-L50（`_rounded_prism`）,L53-L72（`_drawer_front` annulus）,L127-L147（`_carcass_shell`） | Volumetric Envelope Form | eligible if compatible | 圆端 carcass（前两角圆柱端帽）+ 凸弧前脸 mesh |
| `bow_front` | forked_anchor | var_bowfront ← 003 | var_bowfront model.py:L31-L74（`_bow_amount`/`_bow_front_mesh`）,L333-L364（bowed rails） | Planar Boundary Form | eligible if compatible | 仅前脸凸弧（front-only convex mesh），直侧板 |
| `tapered` | forked_anchor | var_tapered ← 005 | var_tapered model.py:L22-L56（`_taper_offset`/`_tapered_panel_mesh`） | Volumetric Envelope Form | eligible if compatible | 侧板上宽下窄斜切（LoftGeometry），直箱前脸 |

`bombe`/`oval_rounded`/`bow_front` 的曲面由真实曲面几何生成（ExtrudeGeometry 抛物 profile / 端帽
Cylinder / Loft），**禁止 Box 降级**（AUTHORING §A Rule 3）。共享一个 `_convex_front_mesh(width,
height, thickness, bulge)` helper，抛物母线，≤16 段；N 个同尺寸抽屉复用同一 Mesh。

### Slot B：support_base（① 骨架 / 支撑底座，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `cabriole_apron` | origin_anchor | 001 | 001 model.py:L358-L413（side_post + front_apron） | eligible if compatible | 4 短曲/锥腿 + 扇贝前 apron（apron 为 host visual） |
| `metal_legs` | origin_anchor | 002 | 002 model.py:L235-L249（leg_/foot_ cylinders） | eligible if compatible | 4 细黄铜圆柱腿 + 圆盘脚垫 |
| `plinth_block_feet` | origin_anchor | 003 | 003 model.py:L314-L321（base_plinth + leg/foot_block） | eligible if compatible | 阶梯 plinth Box + 4 方块脚 |
| `splayed_tapered_legs` | origin_anchor | 004 | 004 model.py:L50-L58,L249-L272（`_tapered_leg` + mount） | eligible if compatible | 4 外撇锥腿（Loft）+ 黄铜 mount |
| `tapered_apron_legs` | origin_anchor | 005 | 005 model.py:L40-L78,L360-L388（`_tapered_leg_mesh` + apron） | eligible if compatible | 4 锥腿（Loft）+ 扇贝 apron |
| `toe_kick` | forked_anchor | var_toekick ← 004 | var_toekick model.py:L23-L37,L25-L27（PLINTH + toe kick，无腿） | eligible if compatible | 内缩 plinth base + toe-kick，平贴地面无腿 |

所有 base 元素**不动**，作为 carcass part 的 visuals（Rule 1），随 carcass 底面接触/嵌入接地。

### Slot C：drawer_layout（N 主多样性轴，详见 §8；登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `full_width_stack` | origin_anchor | 001/002/003 (+forks n2/n4/n6) | 001 model.py:L421-L482；003 model.py:L371-L413；002 model.py:L251-L297 | eligible if compatible | N=2..6 全宽渐变竖叠，每屉一条 PRISMATIC；loop over `n_drawers` |
| `side_by_side_grid` | origin_anchor | 004 (+fork grid2x2) | 004 model.py:L226-L247,L291-L333（center_divider + `drawer_{row}_{col}`） | eligible if compatible | n_rows×2 列网格（2×2/2×3），中央 mullion；nested loop |
| `mixed_paired_full` | origin_anchor | 005 | 005 model.py:L303-L336,L411-L458（center_mullion + 上/中成对，下全宽） | eligible if compatible | 上两成对 + 中两成对 + 下一全宽（5 屉），center_mullion 只在成对行 |

### Slot D：pull_style（④ 表面装饰 / hardware，record_only，登记进 slot_choices，host-conformal）

| module_name | source_type | source evidence | model.py:Lx-Ly | 结构特征 |
|---|---|---|---|---|
| `brass_knob` | record_only | 001 model.py:L62-L88（`_add_brass_knob`） | rosette + stem + sphere，贴前脸曲面（y 随 bulge） |
| `handleless` | record_only | 002（无 pull 几何，push-to-open） | 无 pull |
| `turned_wood_knob` | record_only | 003 model.py:L65-L78（`_add_pull`） | stem + wooden sphere |
| `round_bronze` | record_only | 004 model.py:L116-L133 | stem + 小圆盘 |
| `bail_plate` | record_only + world_knowledge_extrapolation | 005 model.py:L81-L101（`_add_pull`/backplate） | backplate + 双 stem + bar |

pull 是 last geometry，按最终前脸面逐 x 采样 `bulge(x)` 贴合（Rule 4，③→⑤→④）。曲面前脸上
pull 的 y 由 `_convex_front_mesh` 的同一 `bulge()` 派生，随 ③/⑤ 共形。

硬约束满足：body_form 5 candidates（③，≥3 可识别形态原型）、support_base 6、drawer_layout 3、
pull_style 5。每个 ①/③/multiplicity candidate 有 forked/origin anchor + model.py:Lx-Ly。

## 槽位图（slot graph）

pattern: multiplicity (primary) + parallel_children

```
carcass(root, body_form ③ + support_base ①)
  ├─[PRISMATIC axis(0,-1,0), origin=(drawer_x, front_face_y, center_z), mating=front_panel⇄mate_rail]→ drawer_0
  ├─[PRISMATIC …]→ drawer_1
  └─[PRISMATIC …]→ drawer_{k}   (k = N-1, loop-emitted)
```

- carcass 是唯一 root；所有抽屉是它的并联 PRISMATIC 子件（不串链）。
- 跨 slot 接口点位：抽屉 `front_panel` 的 **positive_y（背）面** 与 carcass `mate_rail_{i}` 的
  **negative_y（前）面** 在 closed pose 于 reveal 平面 `front_face_y = -depth/2 + front_inset`
  处贴合（MatingContract，法向 Y，contact_tol 1mm；切向自由）。
- 抽屉盒底 `drawer_bottom` 由 carcass 内部 `runner_{i}` 从下方支撑（间隙 ≤1mm）。
- body_form / support_base 只改 carcass part 的 visuals（曲面/斜切/腿/plinth），不新增可动件、不改
  抽屉接口拓扑。

## 每槽位 Module Emits / Interfaces

### Slot A / body_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（全部 carcass visuals：side_panel_*/back_panel/top_slab/bottom_deck/front_stile_*/front_rail_* + 曲面 front mesh / 斜切 side loft / 圆端帽） | 003 L266-322 / 001 L302-419 / 002 L127-249 |
| internal joints | 无 | — |
| upstream interface | carcass 根 part frame（0,0,0 在 carcass 内） | — |
| downstream interface | reveal 平面 `front_face_y` + 每屉 `mate_rail_{i}` 的 negative_y 面 | 003 L291-306（front_rail_*） |

### Slot B / support_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（腿/脚/plinth/apron 均 carcass visuals） | 001 L358-413 / 002 L235-249 / 003 L314-321 / 004 L249-272 / 005 L360-388 / var_toekick L23-37 |
| internal joints | 无 | — |
| upstream interface | carcass 底面 z=base_h（bottom_deck） | — |
| downstream interface | 接地 z=0 | — |

### Slot C / drawer_layout（每屉 module，loop-emitted）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drawer_{i}`（stack）/ `drawer_{r}_{c}`（grid）/ 命名 upper/middle/lower（mixed）；各含 front_panel + drawer_bottom + drawer_side_0/1 + drawer_back + pull(s) | 001 L153-275 / 004 L61-165 / 005 L139-200 |
| internal joints | 无（抽屉本身刚性） | — |
| upstream interface | `front_panel` positive_y 面（贴 carcass mate_rail），local y=0 = joint origin | 005 L158-163 |
| downstream interface | 无（叶子件） | — |
| joint | `carcass_to_<drawer>` PRISMATIC parent=carcass child=drawer axis=(0,-1,0) lower=0 upper≈travel damping 3-7 friction 2-4 + MatingContract | 001 L257-275 / 004 L315-333 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | rectilinear/bombe/oval_rounded/bow_front/tapered | rectilinear | choice | procedural sampler | Slot A |
| support_base | enum | cabriole_apron/metal_legs/plinth_block_feet/splayed_tapered_legs/tapered_apron_legs/toe_kick | plinth_block_feet | choice | procedural sampler | Slot B |
| drawer_layout | enum | full_width_stack/side_by_side_grid/mixed_paired_full | full_width_stack | choice | procedural sampler | Slot C |
| n_drawers | int | [2,6]（stack）| 3 | conditional | 仅 full_width_stack 用；grid 用 n_rows | §8 |
| n_rows | int | [2,3]（grid）| 3 | conditional | 仅 side_by_side_grid 用；n_cols=2 固定 | §8 |
| pull_style | enum | brass_knob/handleless/turned_wood_knob/round_bronze/bail_plate | brass_knob | choice | procedural sampler | Slot D |
| palette_style | enum | mahogany/walnut/dark_walnut/oak/espresso/painted | walnut | choice | procedural sampler（≥3，目标 4-6） | §8.5 ⑥ |
| width | float | [0.90, 1.18] | 1.00 | independent | clamp | 002 L21/003 L240/005 L233 |
| depth | float | [0.42, 0.52] | 0.46 | independent | clamp | 002 L22/003 L240/005 L233 |
| case_height | float | derived | — | equation | `= 抽屉行数*pitch + rails`（按抽屉数派生 bay 高） | 003/005 |
| drawer_travel | float | [0.27, 0.30] | 0.28 | independent | clamp；`≤ box_depth-0.06`（保留插入） | 001 L522/005 L597 |
| (—) | constraint | — | — | inequality | `box_depth ≤ depth - front_inset - back_t - 0.03`；`travel ≤ box_depth-0.06` | 接口/clearance |
| (—) | constraint | — | — | inequality | 全宽屉 `front_w ≤ width - 2*stile - reveal`；网格屉 `col_w ≤ (width-2*stile-mullion)/2 - reveal` | 004 L26-31 |

所有 equation/inequality/conditional 在 `resolve_config` 内求解。

## 7.5 编译预算 / compile budget（必填）

**每-seed 预算 ≤ 12s**（依据：库内直箱家具 5–10s；本类主体是 Box carcass + 少量 ExtrudeGeometry/
Loft 曲面前脸/斜侧）。分档 tessellation：曲面前脸抛物 profile ≤16 段、圆端帽 Cylinder ≤24 段、
锥腿 Loft 2 截面。N 个同尺寸抽屉前脸/腿复用同一 `Mesh`（按唯一 (front_w, front_h, bulge) 缓存）。
超预算先降精度再迭代。sweep `--compile-timeout 120`（看门狗 ≈10×）。

## 8. Multiplicity / Copy Logic

本小类有**一根主 multiplicity 轴：抽屉数量/布局**。

**Axis 1 — 抽屉数量 N（drawer count）**
- `count_param`: `n_drawers`（full_width_stack）/ `n_rows`×`n_cols`（side_by_side_grid，n_cols=2 固定）/
  固定 5（mixed_paired_full）。
- `N_range`（产品域）: full_width_stack `n_drawers∈[2,6]`；grid `n_rows∈[2,3]`（→ 4/6 屉）；mixed=5。
  组合 N 覆盖 = {2,3,4,5,6}（源支持：3→001/002/003，5→005，6-grid→004；forks→2/4/6-stack、4-grid）。
- sampling domain（权重档）：小 N 高频（2,3,4），大 N（5,6）稀有；测试偏小、产品全程。
- copied object: 一个抽屉 = front（Box 或曲面 mesh）+ 敞口盒（drawer_bottom + drawer_side_0/1 +
  drawer_back）+ pull(s)，外加 carcass 上专属 `runner_{i}` 与 `mate_rail_{i}` 与一条 PRISMATIC。
- naming: stack `drawer_{i}`（i 从 0=底 到 N-1=顶，渐变高度按 i）；grid `drawer_{r}_{c}`；
  mixed `upper_drawer_{0,1}`/`middle_drawer_{0,1}`/`lower_drawer`；joint `carcass_to_<name>`。
- placement: stack 沿竖直均分 pitch，reveal rails 每屉重生；grid 规则 rows×cols + 固定 center_divider；
  渐变屉按 index 缩放前脸高度（底最深）。
- joint policy: 恰好一条 PRISMATIC/屉，parent=carcass，axis=(0,-1,0)，lower=0，upper≈0.27–0.30，
  damping 3–7 / friction 2–4，每屉保持侧向捕获 + 全行程保留插入 + MatingContract。
- source/gating: N 上限 6（stack）/ 6（grid 2×3）；不做 N=1（读作床头柜，非 chest）。

## 8.5 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | support_base 6 种拓扑（cabriole/metal legs/plinth+feet/splayed legs/tapered legs+apron/toe-kick），source-backed（001/002/003/004/005/var_toekick）。carcass 恒为刚性箱 + 内部 runner 负载路径。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：抽屉数 N∈{2,3,4,5,6}，权重档小 N 高频；full_width_stack / grid / mixed 三布局。 |
| ② 关节类型 | 图不变，换 type/轴 | **无（saturated）** | 唯一合法机构 = PRISMATIC 抽屉滑轨 axis(0,-1,0) travel 0.27–0.30。**underfilled_reason（源自 source map）**：本小类 joint/mechanism 轴只有单一合法值，已记录不 fork；第二种机构（REVOLUTE 门扇）会使其变成 door cabinet（跨类）。所有 origins 均只暴露 prismatic 滑轨（001 L257/002 L279/003 L203/004 L315/005 L441）。 |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | body_form 5 candidates（rectilinear=Planar Boundary；bombe/oval_rounded/tapered=Volumetric Envelope；bow_front=Planar Boundary）；曲面用真实 ExtrudeGeometry/Loft/端帽，登记进 slot_choices。source：001/002/003/004/005 + var_bowfront/var_tapered。 |
| ④ 表面装饰 | 叠加表面细节/改装饰数 | 有 | pull_style 5（brass_knob/handleless/turned_wood_knob/round_bronze/bail_plate，record_only）+ 前脸 field/trim；host-conformal（曲面前脸 pull 的 y 随 bulge(x) 派生，③→⑤→④）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | width[0.90,1.18]/depth[0.42,0.52]/case_height 派生/drawer_travel[0.27,0.30]；渐变前脸高（顶浅底深）。每条 PRISMATIC 运动包络：轴(0,-1,0)、开启方向 -Y、[0, travel]；motion_test_plan：跑 `fail_if_parts_overlap_in_sampled_poses`（max_pose_samples=48，抽屉多时降），每屉一条 targeted `ctx.pose({joint:upper})` 验证 -Y 位移 ≥0.24 且保留插入 ≥0.045。抽屉朝外滑离本体，全程不新增穿模。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted-wood/metal(brass,bronze)；配色 6：mahogany/walnut/dark_walnut/oak/espresso/painted。每 palette wood+wood_dark+interior+hardware(brass/bronze)+accent。 |

**收尾自检**：body_form 5 种形态在 batch 0-9 拉得开；6 palette 出现；pull 贴合前脸不悬空；抽屉全行程不穿模。

## 拓扑审计（topology audit）

- root parts: 恰好 1（carcass）。
- 每个抽屉是 carcass 的直接子 part，恰好一条 PRISMATIC，无二级链。
- 无 FIXED 关节（腿/apron/plinth/装饰都是 carcass visuals，不是独立 part）。
- 无独立浮空 part：抽屉经 front_panel⇄mate_rail 接触 + 侧向 stile/mullion 邻接进入连通树。
- 曲面 body_form 仅改 carcass visuals，不改抽屉接口拓扑；抽屉盒始终矩形。
- N 变化只改抽屉 part 数与对应 runner/mate_rail/joint 数，拓扑保持"1 carcass + N 并联 prismatic 子件"。

## 采样与覆盖审计

总组合数（离散）：body_form(5) × support_base(6) × drawer_layout(3) × pull_style(5) × palette(6)
= 2700，再乘 N 采样（stack 5 + grid 2 + mixed 1 = 8）≈ 21600 拓扑元组组合 → 远超富类别 300 门槛。

理由：主多样性来自离散 slot（③ body_form + ① support_base + N/layout）+ ④ pull + ⑥ palette，
连续 scale（width/depth/travel）只做局部微调。

seed_domain_policy：procedural_first（seed 0 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 加权采样每个 slot、
N/layout、pull、palette，再采连续 scale；`resolve_config` clamp + 派生 case_height/box_depth +
投影 travel 可行域 + 解析 conditional N。compatibility：曲面 body_form 与任何 layout/base 兼容
（曲面只在前脸+侧envelope，抽屉盒保持矩形）；无非法组合。无 regression overrides（主 seed domain 全程序化）。
Topology target：1000-seed slot 元组覆盖 report-only。
Controlled local parameterization：width/depth/drawer_travel/leg_length（base 内），均在
`resolve_config` clamp/派生，不破坏 MatingContract / runner 支撑 / joint 轴。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 加权 + N 小值偏多；layout↔N 条件解析 | slot_choices_for_seed == build choices |
| compatibility matrix | 全兼容；N clamp [2,6]，grid n_cols=2；travel≤box_depth-0.06 | 无 floating/collision/axis/超 N 失败 |
| controlled local variation | width/depth/travel/leg_length clamp | 比例变化不破坏接口/支撑/joint 轴/类别身份 |
| regression overrides | none | — |
| random sweep | 0-35 初过，0-999 成熟审计 | axis_realization；viewer 目检 0-9 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form ③ | 5 | yes | yes | 形态主导 slot |
| support_base ① | 6 | yes | yes | |
| drawer_layout (N) | 3 布局 × N | yes | yes | 主 multiplicity 轴 |
| pull_style ④ | 5 | yes | yes | record_only |
| palette ⑥ | 6 | yes | yes | |

## Validator

- slot_choices_for_seed 返回已实现 module 名（body_form/support_base/drawer_layout/n/pull_style/palette）
- config_from_seed 对所有普通 seed 用程序化采样（含 seed 0）
- compatibility gating 阻止非法组合（N clamp、travel 可行域）
- 无 regression overrides
- 连续 scale 依赖（equation/inequality/conditional）在 resolve_config 求解
- 每屉存在 MatingContract（front_panel positive_y ⇄ mate_rail_{i} negative_y）
- 每条 joint 是 PRISMATIC，axis=(0,-1,0)，lower=0，upper∈[0.27,0.30]
- copied drawers 遵循命名/放置策略；渐变高度顶浅底深
- 曲面 body_form 用真实曲面几何（无 Box 降级）

## Reject cases

- 出现 REVOLUTE 门扇 / 门+抽屉混合 / 无抽屉开放搁架（跨类）
- 任一抽屉缺 front_panel / drawer_bottom / drawer_side_0/1 / drawer_back（不是真实敞口盒）
- 抽屉 joint 非 PRISMATIC 或轴不是 (0,-1,0) 或 lower≠0
- 曲面 body_form 用 Box 降级冒充曲面
- 抽屉盒不由 runner 支撑 / 全行程失去插入（脱轨）
- pull 在曲面前脸上悬空（未随 bulge 共形）
- MatingContract 缺失或前脸背面与 mate_rail 前面间隙 >1mm
- closed pose 抽屉间/抽屉-carcass 穿模；全行程新增穿模

## 与相邻类别的边界

- 不该混入：door cabinet（转门柜）——门是 REVOLUTE 门扇，本类只有 prismatic 抽屉。
- 不该混入：door+drawer sideboard（门+抽屉边柜）——混合门与抽屉，本类纯抽屉。
- 不该混入：open shelving（开放搁架）——暴露固定搁板无抽屉。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | ② 轴 saturated（单一 prismatic 机构），按 source map underfilled_reason 记录不 fork。 |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | rectilinear | 003/004/005 | 003 L266-322 | Box carcass + Box 前脸 |
| S2 | A | bombe | 001 | L31-45,L358-387 | 曲面前脸 + 外凸侧柱 |
| S3 | A | oval_rounded | 002 | L36-72,L127-147 | 圆端帽 + 凸弧前脸 |
| S4 | A | bow_front | var_bowfront | L31-74 | 前脸凸弧 mesh |
| S5 | A | tapered | var_tapered | L22-56 | 斜切侧板 loft |
| S6 | B | cabriole_apron | 001 | L358-413 | 曲/锥腿 + apron |
| S7 | B | metal_legs | 002 | L235-249 | 细黄铜腿 |
| S8 | B | plinth_block_feet | 003 | L314-321 | plinth + 方块脚 |
| S9 | B | splayed_tapered_legs | 004 | L50-58,L249-272 | 外撇锥腿 |
| S10 | B | tapered_apron_legs | 005 | L40-78 | 锥腿 + apron |
| S11 | B | toe_kick | var_toekick | L23-37 | plinth + toe kick |
| S12 | C | full_width_stack | 001/002/003 | 003 L371-413 | 全宽渐变竖叠 loop |
| S13 | C | side_by_side_grid | 004 | L226-247,L291-333 | 网格 + divider |
| S14 | C | mixed_paired_full | 005 | L303-336,L411-458 | 成对 + 全宽 |
| S15 | D | pulls | 001/003/004/005 | 001 L62-88 | pull 家族 |
