# waffle_maker — Modular Spec

> 来源小类：`picture_expansion/0611/waffle_maker`。
> 上游 source map：`picture_expansion/template_source_maps/0611__waffle_maker.md`。
> 类别身份 = **翻盖式电/铸铁华夫饼铛**（clamshell waffle iron）：一只 `lower_housing` +
> 一只后铰翻起的 `lid`（±X 轴 REVOLUTE），上下面板夹着 waffle 烹烤格栅（凹/凸），
> 可选前 `latch` 组件（REVOLUTE 释锁）。默认成熟域 = 台式电器尺度（长边 0.20-0.35 m）。
>
> **同步状态**：本 spec 引用的 12 个 5 星样本（5 parent + 7 fork 槽位变体）已同步进本仓库
> `data/records/`，`rating=5`；`uv run articraft external examples --category-slug waffle_maker
> --rating-min 5 --limit 50` 返回 12。行号按各样本本仓库 `revisions/rev_000001/model.py`
> 实际行号计。引用以 part / joint / helper **名字**为准。

## 元信息
| 项 | 值 |
|---|---|
| slug | `waffle_maker` |
| template path | `agent/templates/waffle_maker.py` |
| test path (optional) | `tests/agent/test_waffle_maker_template.py`（不写；sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（fixed named slots + 兼容矩阵 gating；无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12（5 parent + 7 fork 变体；均 converged）|
| read_count | 12（全部读完整 `model.py`，不抽样；含每个样本 build helpers / part 树 / articulations / run_tests）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 slot 表；本批 12/12 全部被采纳 |

阅读要点：
- **5 个 parent** 共享同一 clamshell 拓扑：`lower_housing` (root) + `lid` (child) + 单
  REVOLUTE `lid_hinge`。其中 3/5 (003/004/005) 还带独立 `latch` part + REVOLUTE
  `latch_hinge`。所有 waffle 格栅由 rectangular Box **ribs** 或 cadquery
  intersect 的椭圆场组成，全部落在 Box/Cylinder 家族内，不涉及 Lathe/mesh 降级。
- **plate_form 轴**：parent 001 是椭圆 (ellipse_prism)；parent 002/003/004/005 是
  rectangular rounded_box；fork `plate_form_round` 把 001 改成圆形；fork
  `plate_form_square` 把 002 改成正方形 5x5 grid。
- **grid_topology 轴**：源里已有 dense_rectangular (002 6x5 / 003 10x8 / 005
  6-column dense) 与 diagonal_stripes (001 42° 双向 ribs)；fork
  `grid_topology_heart_cells` 把 003 grid 换成 4 心形；fork
  `grid_topology_4_belgian_cells` 把 004 换成 2x2 深胞。
- **closure 轴**：parents 002 无独立 latch (`latch_receiver` 只是 base visual)；
  003/004/005 有独立 latch；fork `closure_over_center_latch` 把 004 latch 换成大 U
  bail loop。→ closure slot 有 `no_latch` / `front_latch` 两个 candidate。
- **cooking_motion 变体**：fork `cooking_motion_flip_frame` 把 005 换成翻转架 +
  两独立铰链——但结构过于复杂且脱离主拓扑（旋转框架而非 clamshell），P0 决定**不采纳为
  独立 module**（拓扑差异过大会污染主 slot graph；见 §11 blocked）；改用
  `plate_form_round` 之外的三种 rectangular 变体，通过 `plate_form` × `grid_topology`
  × `closure` 组合覆盖 topology 空间。
- **plate_motion "removable plates"** 变体也不采纳为 slot 值——它只是把 base 的
  grid 拆成一个 FIXED 子 part，等价于装饰（Rule 1），不改主拓扑。

## 核心身份

一只 **clamshell waffle iron**：`lower_housing`（root，坐台面，含 waffle 下格栅、
后铰硬件、可选前控制件如 dial/button/foot 作 host-conformal visual）+ `lid`（唯一
必须的独立活动 part，绕 lower_housing 后铰 REVOLUTE 翻开，含上 waffle 格栅、前 handle
visual）+ 可选 `latch`（REVOLUTE 前锁扣）。**活动语义 = 盖开合**（0..≈1.7 rad，
q=0 闭合）+ 可选前锁 REVOLUTE。默认成熟域：{ 圆 / 正方 / 长方 } 三种 plate_form ×
{ 长方浅密 dense / 深 belgian 胞 / heart 胞 } 三种 grid_topology × { no_latch /
front_latch } 两种 closure。台面尺度长边 0.20-0.32 m。

不该混入：
- **panini press / 三明治炉**：几乎完全一样的 clamshell 骨架，但格栅是**平滑或直纹条**，
  不是 waffle 深胞——本模板的 grid_topology 全走 waffle 深槽/深方胞/heart 深胞，
  已把身份钉在 waffle。
- **烤肉扁平 electric griddle**：单面无 lid、无 clamshell。
- **rice cooker / slow cooker**：圆桶盖+内胆，非 clamshell 两片 waffle plate。
- **烤面包机 (toaster)**：立式插槽，主运动 spine 不同。

## 槽位 + 候选模块表

> **建模注记**：`plate_form`（Slot A）决定 housing 的 footprint mesh（圆/正方/长方），
> 通过 mesh helper 切换 primitive，不改 part 数或 joint 拓扑，是共享 slot——
> **③ Primary Form Family 主体形态家族 slot**（Planar Boundary Form：核心 footprint
> 轮廓的离散原型变化）。`grid_topology`（Slot B）通过 rib helper 切换 waffle grid
> primitive，也不改 part 数，但改变宿主表面细节（Macro Surface Construction 边缘）——
> 与 plate_form 组合出真正的形态视觉差异。`closure`（Slot C）是**唯一真正改 part
> 数 / joint 拓扑的槽**：加不加一个 `latch` 独立 part + REVOLUTE `latch_hinge`。

### Slot A: `plate_form` — ③ Primary Form Family (Planar Boundary Form)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `oval` | forked_anchor (form_subtype=Planar Boundary Form) | rec_picturex_0611__waffle_maker__001 | L21-49 (`_ellipse_prism`/`_ellipse_ring`), L150-168 (`_lower_casting`), L189-204 (`_upper_casting`) | eligible if compatible | 椭圆足迹（rx≈0.128, ry≈0.087），椭圆 body + 椭圆 rim + 长 loop handle；grid 场为椭圆 clip |
| `round` | forked_anchor (form_subtype=Planar Boundary Form) | rec_0611_waffle_maker_var_plate_form_round | L24-51 (`_circle_prism`/`_circle_ring`), L156-174 (`_lower_casting`), L201-215 (`_upper_casting`) | eligible if compatible | 圆形足迹（r≈0.120），圆 body + 圆 rim；同 001 的部件树、只换 ellipse→circle profile |
| `square` | forked_anchor (form_subtype=Planar Boundary Form) | rec_0611_waffle_maker_var_plate_form_square | L166-176 (`_build_base_shell`), L283-296 (`_grid_plate_up` 5x5) | eligible if compatible | 正方 rounded_box footprint（sx≈sy≈0.224/0.184），5x5 方 pocket grid |
| `rectangular` | forked_anchor (form_subtype=Planar Boundary Form) | rec_picturex_0611__waffle_maker__002 / __003 / __004 / __005 | 002 L168-177, 003 L76-105, 004 L132-173, 005 L179-232 | eligible if compatible | 长方 rounded_box footprint（sx>sy，典型 0.255x0.148 或 0.284x0.220），dense rectangular grid |

### Slot B: `grid_topology` — ④ Surface Construction on host cooking face

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `dense_rectangular` | forked_anchor | rec_picturex_0611__waffle_maker__002 (6x5) / __003 (10x8) / __005 (dense ribs) | 002 L53-108 (`_grid_plate_up`), 003 L31-73 (`_waffle_plate`), 005 L88-158 (`_waffle_plate`) | eligible if compatible | 深浅方格 pockets 或密集直纹 rib 网（columns×rows≥6x5），rib 高度 0.005-0.008 |
| `diagonal_stripes` | forked_anchor | rec_picturex_0611__waffle_maker__001 | L96-147 (`_waffle_ribs`, 双 42° 组带) | eligible if compatible | 两组 ±42° 对角条纹，间距 0.016 m + 强化对角分割条 |
| `deep_belgian_cells` | forked_anchor | rec_0611_waffle_maker_var_grid_topology_4_belgian_cells | L59-100 (`_belgian_cell_border`) | eligible if compatible | 2x2 大深胞，每胞 raised rectangular wall border，胞深≈0.008-0.010 |
| `heart_cells` | forked_anchor | rec_0611_waffle_maker_var_grid_topology_heart_cells | L34-56 (`_heart_profile`), L59-131 (`_waffle_plate` 4 心) | eligible if compatible | 2x2 心形 rib walls + 中心十字连接 rib，可标注 `world_knowledge_extrapolation` 若形状太具象 |

### Slot C: `closure` — ② Joint Topology (adds/removes an independent latch REVOLUTE)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `no_latch` | forked_anchor | rec_picturex_0611__waffle_maker__001 / __002 | 002 L318-323 (`latch_receiver` 作 base visual, no joint) | eligible if compatible | 无独立 latch part，只在 lower_housing 前缘生成 `latch_receiver` visual；单一 REVOLUTE `lid_hinge` |
| `front_latch` | forked_anchor | rec_picturex_0611__waffle_maker__003 / __004 / __005 | 003 L297-330 (`latch` + `latch_hinge`), 004 L474-494, 005 L392-426 | eligible if compatible | 独立 `latch` part：`latch_pivot` 圆柱 + `latch_paddle` box + 可选 `latch_lip`；REVOLUTE `latch_hinge` axis 沿 X 或 -X，行程 0..≈0.5 rad 释锁 |

## Multiplicity / Copy Logic

- **无复制数量逻辑**：核心结构由固定 named slots（plate_form + grid_topology + closure）
  表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。plate 上 grid
  rib 数量由 grid_topology helper 内部确定（如 dense 6x5, belgian 2x2, heart
  2x2），是 module 内实现细节，不属于模板级 multiplicity 轴。

## 槽位图（slot graph）

pattern: `mixed`（固定 named slots；plate_form + grid_topology 是共享 host-mesh
维度，closure 决定是否新增 latch part）

```
lower_housing (root, 坐台面)
  │  plate_form 决定 housing/lid 的 outer footprint (oval/round/square/rectangular)
  │  grid_topology 决定 lower_housing 上表面 + lid 下表面的 waffle rib pattern
  │
  ├── lid ── [lid_hinge: REVOLUTE axis=-X or +Y, origin=后 rim 铰线, lower=0 闭合 / upper≈1.7]
  │            (盖的 upper waffle grid = plate_form × grid_topology 的镜像 mesh)
  │
  └── [closure = front_latch]:
        latch ── [latch_hinge: REVOLUTE axis=+X or -X, origin=前缘 latch_pivot 位置,
                  lower=0 闭合 / upper≈0.5 rad 释锁]
```

接口点位与 joint 语义：
- **lid_hinge**：后 rim 铰线上，`hinge_barrel_i` (lower_housing) ↔ `lid_hinge_barrel` /
  `lid_hinge_mount` (lid) 是 captured-pin 几何 → 省略 `MatingContract` (grandfathered)，
  由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped
  `allow_overlap` 守 pin↔barrel overlap。
- **latch_hinge**（closure=front_latch）：前缘上，`latch_pivot` cylinder 落在 lower_housing
  的 `latch_lugs` 之间，captured-pin → 同样 grandfathered + `allow_overlap`。
- **闭合姿态**：所有铰链 q=0 闭合；`lid` 与 `lower_housing` 的两块 waffle grid
  面对面留 0.3-2.5 mm clearance（不接触，也不穿模）。
- **rest pose**：可 `_LID_OPEN` 或 `0.0` 二选一——本模板取 **q=0 闭合**（更多 5 星样本
  用 closed rest 便于 clearance 校验），open 姿态通过 sampled-pose motion QC 覆盖。

## 每槽位 Module Emits / Interfaces

### Slot A / `plate_form=oval|round|square|rectangular`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无新独立 part（改 `lower_housing` + `lid` 的 outer footprint mesh 和 grid clip 场）| 001/002/003/004/005 主体 |
| internal joints | 无 | — |
| upstream interface | root（`lower_housing` 坐台面）| — |
| downstream interface | 上 rim + 后铰硬件（供 lid 接入）+ 前缘（供 closure 接入）| 001 L171-186 / 002 L168-177 |

### Slot B / `grid_topology`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无新独立 part（改 `lower_grid` / `upper_grid` 的 rib pattern）| 002/003/004/005 |
| internal joints | 无 | — |
| upstream interface | 附着于 `lower_housing.upper_cooking_face`(z=rim_z) 和 `lid.lower_cooking_face` | 002 L280-295 / 005 L240-250 |
| downstream interface | — | — |

### Slot C / `closure=no_latch`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无新 part（`latch_receiver` 作 lower_housing 前缘 visual）| 002 L318-323 |
| internal joints | 无 | — |
| upstream interface | `lower_housing.front_face` | 002 L318-323 |

### Slot C / `closure=front_latch`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `latch`（visuals: `latch_pivot` + `latch_paddle` + 可选 `latch_lip`）| 003 L297-315, 005 L392-410 |
| internal joints | `latch_hinge` REVOLUTE axis=±X，origin 位于 `latch_pivot` 位置 y 前缘、z 在 rim 附近，lower=0 / upper≈0.5 rad | 003 L316-330, 005 L412-426 |
| upstream interface | `latch_pivot` cylinder 落入 lower_housing 的 `latch_lug_left` + `latch_lug_right` bosses（captured-pin）| 003 L98-103, 005 L392-398 |

### `lid`（永远存在，跨所有 slot 组合）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid` (visuals: `lid_shell` + `upper_grid` + `lid_handle` 或 `lid_edge_band`) | 001 L259-284 / 005 L281-368 |
| internal joints | 无（在 lower_housing 侧建 `lid_hinge`） | — |
| joint via lower_housing | `lid_hinge` REVOLUTE axis=(-1,0,0) 或 (0,-1,0)，origin=后 rim 铰线，lower=0 / upper≈1.6-1.9 rad | 001 L286-301 / 002 L402-419 / 005 L370-389 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| plate_form | enum | oval / round / square / rectangular | rectangular | choice | procedural sampler 选择 | slot A |
| grid_topology | enum | dense_rectangular / diagonal_stripes / deep_belgian_cells / heart_cells | dense_rectangular | choice | procedural sampler | slot B |
| closure | enum | no_latch / front_latch | front_latch | choice | procedural sampler | slot C |
| palette_style | enum | seasoned_cast_iron / black_appliance / brushed_steel / cream_retro / red_appliance | seasoned_cast_iron | palette | palette_only（不进 slot_choice；每 seed 采样一次；驱动全部 material=mats[…]）| 001/002/004 材质 |
| length_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 housing 长边 (rx)，clamp | 各 parent 尺寸 |
| width_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 housing 短边 (ry) | 各 parent 尺寸 |
| height_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 housing 总高（含 hinge_z / rim_z 派生）| 各 parent 尺寸 |
| lid_open_angle | float | [1.3, 1.95] | 1.65 | independent | REVOLUTE lid_hinge upper 极限（rad）| 001/002/005 motion_limits |
| latch_open_angle | float | [0.25, 0.6] | 0.45 | conditional | 仅 closure=front_latch；latch_hinge upper 极限 | 003/005 motion_limits |
| plate_gap | float | [0.0006, 0.0022] | 0.0012 | derived | closed pose 上下 grid 之间的 z 间隙 | 001 L376-384 / 005 L598-606 |
| (—) | constraint | — | — | equation | `rim_z = 0.34 · base_h · height_scale`；`hinge_z = 0.62 · base_h · height_scale` | 001/002/005 |
| (—) | constraint | — | — | inequality | grid rib 场必须落在 housing footprint 内（rib 场半宽 ≤ housing 半宽 − wall）| 003 L76-105 |
| (—) | constraint | — | — | inequality | closed pose：`lid_lower_grid.z_bottom − lower_grid.z_top ≥ plate_gap`；`lid` 到 `lower_housing` 的 xy overlap ≥ 0.6 · footprint | 001 L363-390 / 005 L588-606 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每 build 解析一次。scale 只动
安全比例 + 行程，绝不改变 plate_form / grid_topology / closure 的拓扑。

### 7.5 编译预算 / compile budget

- 自报预算：**≤ 20 s / seed**（现实为 5-12s），依据：库内简单 clamshell 类模板（tackle
  box, wheelie_bin）平均 3-8s；waffle grid 用 SDK 原语 `Box` (Grid ribs) + `Cylinder`
  （pivot / hinge pin）而非 cadquery 布尔雕刻，因此不用 mesh_from_cadquery 昂贵路径。
- Tessellation 档：所有 Cylinder 段数使用 SDK 默认（≥16），小半径 (pin/pivot ≤3mm)
  自动 32 段；grid rib 组数每面 ≤50 个 Box visual（dense 6x5 = 60，但每个 rib 是
  primitive Box 而非 mesh）。
- 单 seed 内所有 rib visuals 都是 `sdk.Box` 原语（不走 mesh），因此不必复用 Mesh
  对象。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | **有** | 2 种：{lower_housing + lid}（closure=no_latch, 1×REVOLUTE） / {lower_housing + lid + latch}（closure=front_latch, 2×REVOLUTE）。均 forked_anchor，见 slot C 表 |
| └ multiplicity | 同构件 ×N | 无 | 类别不带同构 N 复制（grid rib 数是 module-local 实现细节，不是模板级 multiplicity 轴，spec §8 已声明）|
| ② 关节类型 | 图不变，某条边换 type/轴 | **有** | 全部 REVOLUTE（lid_hinge + 可选 latch_hinge）；轴族：lid_hinge ∈ {(-1,0,0), (0,-1,0)}，latch_hinge ∈ {(1,0,0), (-1,0,0)}。source-backed：001/003 lid 沿 -Y / 002/005 lid 沿 -X / 003 latch 沿 -X / 005 latch 沿 +X |
| ③ 主体形态家族 / Primary Form Family | 换核心 part 的可识别几何形态原型 | **有** | 4 candidate：oval / round / square / rectangular（`plate_form` slot A，全部 form_subtype=**Planar Boundary Form**——核心 footprint 轮廓离散变化）。已登记进 slot_choices |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | **有** | grid_topology slot B 的 4 candidate（dense_rectangular / diagonal_stripes / deep_belgian_cells / heart_cells）是 host-conformal surface pattern；此外 host visuals：feet (Box×4)、hinge_barrel、handle (Box)、可选 indicator lens (Cylinder)。派生顺序 ③→⑤→④，rib 场按 plate_form footprint clip |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | **有** | length_scale/width_scale/height_scale [0.85,1.15]；lid_open_angle [1.3,1.95] rad；latch_open_angle [0.25,0.6] rad。运动包络：`lid_hinge` 轴=-X 或 -Y，开启方向 +Z，[0, lid_open_angle]；`latch_hinge`（front_latch 时）轴 =±X，开启方向 上，[0, latch_open_angle]。`motion_test_plan`：run_tests 用 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)`；targeted `ctx.pose({lid_hinge: lid_open_angle})` 检 lid 抬起；`ctx.pose({latch_hinge: latch_open_angle})` 检 latch 释锁 |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | **有** | `palette_style` 5 档（seasoned_cast_iron / black_appliance / brushed_steel / cream_retro / red_appliance）；材质大类：cast_iron(metal) / painted / stainless(metal) / plastic-painted / red-plastic → ≥3 材质大类；每 seed 采样一次，全部 mats[key] 读该 palette |

**收尾自检**：本表每个"有"里列的取值，必须在 `template batch` 0-9 seed 渲染里
肉眼可见地出现——4 种 footprint 拉得开、4 种 grid pattern 都出现、closure 两种
拓扑都出现、5 种 palette 都出现、lid 全程不穿模。

## 采样与覆盖审计

总组合数：plate_form(4) × grid_topology(4) × closure(2) = **32**。palette_style(5)
+ 连续 scale 使多样性远超。0-35 sweep 应命中 32 组合中的 ~24+（每个 slot 值出现
≥1 次）。

理由：Slot A/B 都提供真正的视觉/形态差异，Slot C 提供 joint 拓扑差异。32 是 report-only
目标；低于 300 因为类别 clamshell 结构真实空间就是有限的（单 REVOLUTE lid + 可选
latch）。

seed_domain_policy：`procedural_first`。`config_from_seed(seed)` 用
`random.Random(seed)`；seed=0 不特殊。

Procedural Sampling / Sweep Plan：sampler 依次 `rng.choice` 三个 named slot；
`resolve_config` 走一次兼容矩阵合法化 + clamp 连续 scale；无 regression overrides。
random sweep seeds 0-35（初轮）+ 0-999 成熟审计；viewer 目检 seeds 0-9。

Controlled local parameterization：见 §7 参数表。length_scale/width_scale/height_scale/
lid_open_angle 独立采样，latch_open_angle conditional 于 closure=front_latch，
plate_gap 派生自 height_scale。跨部件约束通过两条 inequality（rib 场 ≤ housing
footprint；closed pose 上下 grid clearance ≥ plate_gap）在 `resolve_config` 内投影。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` A/B/C，`rng.uniform` scales, `rng.choice` palette | slot_choices_for_seed 与 build 一致；含 (plate_form, ), (grid_topology, ), (closure, ) |
| compatibility matrix | (1) 所有 (plate_form × grid_topology × closure) 32 组合合法（无互斥）；(2) `heart_cells` 与 `round` 组合时把 heart 单元尺寸 clamp 到不超出 0.85·rx；(3) `deep_belgian_cells` 与 `round` 时同上；(4) 无回退降级——所有 32 组合都可 build | 无 floating / collision / axis / 未覆盖 slot |
| controlled local variation | 4 个 clamped scale + 1 conditional (latch_open_angle) + 1 derived (plate_gap) | 比例变化不破坏 hinge origin、captured 接口、closed pose clearance、类别身份 |
| regression overrides | none | — |
| random sweep | seeds 0-35 初轮；0-999 成熟审计 | 每 slot 值 ≥1 次 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| plate_form | 4 | yes | yes | oval/round/square/rectangular（③ Primary Form Family）|
| grid_topology | 4 | yes | yes | dense/diagonal/belgian/heart |
| closure | 2 | yes | no | 只 2 candidate——源池只有 {no latch, one front latch} 两种拓扑（`over_center_latch` 与 `front_latch` 拓扑相同，只是 loop shape 不同 → 折入 front_latch 的 sub-variant；`cooking_motion=flip_frame` 拓扑差异过大不采纳）；文档化 |

## Validator

- `slot_choices_for_seed` 返回 `(("plate_form", …), ("grid_topology", …), ("closure", …))`，与 build 一致
- `config_from_seed(0)` 与所有 seed 用 deterministic procedural sampling
- compatibility matrix / gating 阻止不合法尺寸（heart/belgian 单元不超 footprint）
- 每 build 一次 `resolve_config`，clamp 连续 scale + 派生 plate_gap/rim_z/hinge_z
- key joints：`lid_hinge` REVOLUTE axis ∈ {(-1,0,0), (0,-1,0)}，upper ∈ [1.3, 1.95]；
  `latch_hinge`（front_latch 时）REVOLUTE axis ∈ {(1,0,0), (-1,0,0)}，upper ∈ [0.25, 0.6]
- captured-pin allow_overlap：lid_hinge (pin ↔ barrel)，latch_hinge (pivot ↔ lug)
- Rule 5：`run_tests` 调 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64,
  ignore_fixed=True)` + targeted `ctx.pose(...)` for lid_open / latch_open
- palette_style 驱动所有 material 参考；无裸 RGB

## Reject cases

- 把 grid rib 场半宽超出 housing footprint → §7 inequality FAIL / 悬空 rib
- lid_hinge origin 放在 housing 中心而非后 rim → `fail_if_articulation_origin_far_from_geometry` FAIL
- 把 latch 当 FIXED joint 或作为 lower_housing visual（closure=front_latch 语义要求它是独立活动 part）
- closed pose 让上下 grid 相撞（plate_gap < 0）或悬浮距过大 → §7 inequality 或 sampled-pose FAIL
- 把 flip_frame 拓扑塞进主 slot graph（旋转框架和 clamshell 骨架不兼容 → §11 blocked）
- 把 grid rib 数当 multiplicity 轴 → 违反 §8 声明（rib 数是 module 实现细节）
- 走 mesh_from_cadquery 布尔雕刻做 waffle 场（超 20s 预算，超 §7.5 编译预算）

## 与相邻类别的边界

- 不该混入：**panini press / 三明治炉**——同 clamshell 骨架但格栅是平/直纹，非
  waffle 深胞；本模板 grid_topology 全走 waffle 深槽/深方胞/heart 深胞。
- 不该混入：**平面 electric griddle**——单面无 lid、无 clamshell。
- 不该混入：**rice cooker / slow cooker**——圆桶盖+内胆，非 clamshell 两片 plate。
- 不该混入：**toaster**——立式插槽，主运动 spine 不同。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | (P0 决定) (1) `cooking_motion=flip_frame` 变体因拓扑差异过大（旋转框架 vs clamshell）不作为独立 module；(2) `plate_motion=removable_plates` 因等价于装饰（Rule 1）不作为独立 module；(3) `closure_over_center_latch` 视为 `front_latch` 的 sub-variant（loop shape 差异）而非新 slot 值；(4) closure 只有 2 candidate（degrade 到 2）—— 源池只有 {no latch, front latch} 两种真实拓扑；(5) 32 组合 < 300 是类别真实结构上限（report-only）|

## 模板实现备注

- 共享 helper：`_footprint_solid(form, sx, sy, rz)` 切换 Box/Cylinder/ellipse-mesh；
  `_grid_ribs(topology, sx, sy, z0, height, form)` 切换 grid rib helper。
- captured 接口 allow_overlap：`run_waffle_maker_tests` 里两组：
  `lid_hinge_pin`↔`lower_housing.hinge_barrel`, `latch_pivot`↔`lower_housing.latch_lug_left/right`。
- palette：`PALETTE_STYLES` 5 档全数据表，`resolve_config` 输出 palette dict，
  `build_*` 里 `mats = {name: model.material(...)}`，全部 visual 用 `material=mats[...]`。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C parent 基线 | oval + diagonal_stripes + no_latch | rec_picturex_0611__waffle_maker__001 | L21-49, L96-147, L150-215, L286-301 | oval footprint + 对角 rib helper + rear hinge |
| S2 | A/B/C parent 基线 | rectangular + dense_rectangular + no_latch | rec_picturex_0611__waffle_maker__002 | L53-108, L166-177, L402-419 | rectangular dense pockets |
| S3 | A/B/C parent 基线 | rectangular + dense_rectangular + front_latch | rec_picturex_0611__waffle_maker__003 | L31-73, L76-105, L107-146, L276-330 | 独立 latch REVOLUTE 前锁基线 |
| S4 | A/B/C parent 基线 | rectangular + dense_rectangular + front_latch | rec_picturex_0611__waffle_maker__004 | L63-100, L132-173, L459-494 | latch 沿 -Y 轴、bail loop 变体 |
| S5 | A/B/C parent 基线 | rectangular + dense_rectangular + front_latch | rec_picturex_0611__waffle_maker__005 | L88-158, L179-232, L370-426 | rectangular dense + front latch paddle |
| S6 | A | plate_form=round | rec_0611_waffle_maker_var_plate_form_round | L24-51, L156-215 | round footprint fork |
| S7 | A | plate_form=square | rec_0611_waffle_maker_var_plate_form_square | L166-177, L283-296 | square footprint fork（5x5 pockets）|
| S8 | B | grid_topology=heart_cells | rec_0611_waffle_maker_var_grid_topology_heart_cells | L34-56, L59-131 | 心形 rib pattern fork |
| S9 | B | grid_topology=deep_belgian_cells | rec_0611_waffle_maker_var_grid_topology_4_belgian_cells | L59-100 | 深 belgian 2x2 fork |
| S10 | C | closure=front_latch (bail loop sub-variant) | rec_0611_waffle_maker_var_closure_over_center_latch | latch 相关 helper | 折入 front_latch |
| S11 | blocked | cooking_motion=flip_frame（拓扑差异过大）| rec_0611_waffle_maker_var_cooking_motion_flip_frame | — | 不采纳，见 §11 |
| S12 | blocked | plate_motion=removable_plates（Rule 1 等价装饰）| rec_0611_waffle_maker_var_plate_motion_removable_plates | — | 不采纳，见 §11 |
