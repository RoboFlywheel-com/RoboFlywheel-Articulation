# Modular Spec — Industrial / Safety cage

## 元信息
| 项 | 值 |
|---|---|
| slug | `Industrial_Safety_cage` |
| template path | `agent/templates/Industrial_Safety_cage.py` |
| test path (optional) | `tests/agent/test_Industrial_Safety_cage_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root cage_frame + parallel-children wall_infill / interior / door_system + door-parented latch + 2 multiplicity axes) |
| function stem | `industrial_safety_cage` (exports `build_industrial_safety_cage`, `build_seeded_industrial_safety_cage`, `config_from_seed`, `resolve_config`, `slot_choices_for_seed`, `run_industrial_safety_cage_tests`) |

`pattern = mixed`: a single root `cage_frame` part (structural rails + corner
posts + base feet/casters + latch keeper, all fused visuals) carries three
parallel-children slots — `wall_infill` (visuals only, added to the cage part),
`interior` (payload / drawer / shelving), and `door_system` (1 or 2 access door
parts + their joints, all parented to the cage) — plus a `latch` slot parented to
the primary door leaf. Two multiplicity axes ride on top: `mesh_density` (wire
rod count) and door leaf count (folded into the door candidates: 1 vs 2).

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 9 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 10 were read in full (origin full + 9 diffed against origin) |

Samples (all `collections=["workbench"]`, `rating=5`):

- `rec_use-the-attached-reference-image-picture-industr_20260707_080119_804935_c0c2456f` — ORIGIN 母本 (box wire cage; wire mesh sides/rear/roof; leveling feet; FIXED red cabinet payload on bottom shelf; single yellow hinged access door REVOLUTE-z; rotating latch REVOLUTE-x).
- `rec_safety_cage_var_double_door` — ① skeleton + door leaf count: single door → 2 mirrored leaves, each REVOLUTE-z on an opposing front corner post.
- `rec_safety_cage_var_drawer_payload` — ①/② interior: FIXED cabinet → pull-out tray on PRISMATIC-y slide rails.
- `rec_safety_cage_var_mesh_density` — multiplicity: coarser wire-rod counts on side/rear/roof panels.
- `rec_safety_cage_var_mobile_caster_base` — ③/④ base: leveling feet → 4 swivel-caster assemblies (fused cage visuals).
- `rec_safety_cage_var_shelf_levels` — ① interior: single bottom shelf → N evenly-spaced internal shelf stack.
- `rec_safety_cage_var_sliding_bolt_latch` — ② latch: rotating drop-hasp REVOLUTE-x → sliding bolt PRISMATIC-y.
- `rec_safety_cage_var_sliding_door` — ② door: hinged REVOLUTE-z → sliding gate PRISMATIC-x on an overhead track.
- `rec_safety_cage_var_solid_perforated_panels` — ③ macro-surface: wire-rod lattice → thin solid perforated sheet-metal Box panels.
- `rec_safety_cage_var_top_hinge_awning` — ② door: side-hinged REVOLUTE-z → top-hinged awning REVOLUTE-x lifting outward.

## 核心身份

A **foreground industrial wire safety cage / guard enclosure**: a compact welded
rectangular steel **frame** (base rails + top rails + 4 upright corner posts,
standing on leveling feet or swivel casters) whose bays are filled with a
protective **wall surface** — crossed galvanized wire mesh, stout vertical bars,
or solid perforated sheet-metal panels — enclosing an interior payload (a
fixed equipment cabinet, a pull-out tray, or open shelving). Access is through
**at least one articulated access door** (side-hinged single or double leaf, a
side-sliding gate, or a top-hinged awning) secured by a **latch** (rotating
drop-hasp or sliding bolt). At least one real non-fixed joint (the door) is
always present. Default mature domain: ~0.5-0.7 m bench-scale guard cage.

Not to be confused with the neighbouring picture subclass **Industrial / Blast
door** (a single massive armored door leaf on a frame — the door IS the whole
object, not an enclosure) or **Industrial / Safety_cage**-adjacent shelving/racks
(no articulated access door, no protective mesh envelope).

## 槽位 + 候选模块表

### Slot A：wall_infill (parallel child; visuals added to cage root · ③ Macro Surface Construction + ④ + multiplicity `mesh_density`)

How the cage bays are enclosed. Emits ZERO parts — all rods/bars/panels are
fused as `cage_frame` visuals (Rule 1: non-moving decoration = `part.visual`).
Declares only `downstream` (re-export cage) so the assembler adds no chain joint.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `wire_mesh` | forked_anchor (origin) | `rec_use-...c0c2456f` | L94-L115 | eligible | crossed thin galvanized wire rods (`Cylinder` r=0.0038) on sides+rear+roof; verticals `_rod_z` + horizontals `_rod_y`/`_rod_x`. **Macro Surface Construction** (open lattice). `mesh_density` multiplicity. |
| `vertical_bar_grille` | forked_anchor | `rec_safety_cage_var_vertical_bar_grille` | L70, L95-L109, L180-L189 | eligible | stout vertical bars only (`Cylinder` r=0.008), NO horizontals on sides/rear/door; roof kept as thin wire. **Macro Surface Construction** (prison-bar grille). |
| `solid_perforated_panels` | forked_anchor | `rec_safety_cage_var_solid_perforated_panels` | L47-L49, L89-L110, L179-L191 | eligible | thin sheet-metal `Box` panels (t=0.003) filling each bay, edges embedded into frame channel; replaces the whole rod lattice. **Planar Boundary Form** (solid closed wall). |

### Slot B：door_system (parallel children on cage front -Y · ① skeleton + ② joint + door leaf count)

The category-defining access mechanism. Emits 1-2 door parts + their joints,
parented directly to the cage (parallel children; `downstream`-only). Latch mounts
onto the primary leaf (`access_door`, or `door_leaf_0` when double).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_hinged_door` | forked_anchor (origin) | `rec_use-...c0c2456f` | L134-L242 | eligible | one `access_door` leaf (yellow stile/rail frame + wire fill + hinge barrels); `cage_to_door` **REVOLUTE axis Z** `[0, pi/2]`, hinged on the front-left post, open outward at q=0. |
| `double_door` | forked_anchor | `rec_safety_cage_var_double_door` | L155-L233 | eligible | ① skeleton: 2 mirrored `door_leaf_{0,1}` on opposing front posts; each `cage_to_door_leaf_i` **REVOLUTE axis Z** `[0, pi/2]`, meeting at center when closed. Leaf count = 2. |
| `sliding_gate` | forked_anchor | `rec_safety_cage_var_sliding_door` | L120-L216 | eligible | ② joint: one `access_door` gate in the front plane + overhead `door_track` + hanger rollers (cage visuals); `cage_to_door` **PRISMATIC axis X** `[0, door_w]`, slides sideways to open. |
| `top_awning` | forked_anchor | `rec_safety_cage_var_top_hinge_awning` | L134-L240 | eligible | ② joint: `access_door` awning hinged along the top front rail; horizontal barrels axis X; `cage_to_door` **REVOLUTE axis X** `[0, pi/2]`, lifts outward/up at q=0. |

### Slot C：latch (child of the primary door leaf · ② joint)

Small securing hardware on the door free edge. One `latch_handle` part parented
to the door part (not the cage), placed from `resolve_config` per door module.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rotating_latch` | forked_anchor (origin) | `rec_use-...c0c2456f` | L244-L262 | eligible | `pivot_pin` + `drop_hasp` + `pull_knob` sphere; `door_to_latch` **REVOLUTE axis X** `[-0.75, 0.75]`. |
| `sliding_bolt` | forked_anchor | `rec_safety_cage_var_sliding_bolt_latch` | L244-L262 | eligible | `bolt_body` rod + `pull_knob`; `door_to_latch` **PRISMATIC axis Y** `[0, 0.04]`, shoots into the keeper. |

### Slot D：interior (parallel child on cage · ① skeleton + ② joint)

The enclosed contents. Emits payload part(s) + supporting cage visuals (shelves /
slide rails). Parented to the cage.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fixed_cabinet` | forked_anchor (origin) | `rec_use-...c0c2456f` | L119-L132 | eligible | `bottom_shelf` (cage visual) + `red_payload` cabinet (`red_cabinet`+`top_cap`+`front_handle`) **FIXED** on the shelf. |
| `pull_out_drawer` | forked_anchor | `rec_safety_cage_var_drawer_payload` | L121-L160 | eligible | ② joint: L-channel `slide_rail_*` (cage visuals) + `red_payload` tray on `cage_to_payload` **PRISMATIC axis -Y** `[0, 0.28]`, pulls out the front. |
| `shelf_stack` | forked_anchor | `rec_safety_cage_var_shelf_levels` | L119-L132 | eligible | ① skeleton: N evenly-spaced `shelf_level_i` (cage visuals), NO payload part — open shelving. No interior joint. |

硬约束满足：Slot A=3, Slot B=4, Slot C=2, Slot D=3 candidates；每个 candidate
都有 `forked_anchor` + `model.py:Lx-Ly`（无 `world_knowledge_extrapolation`，全部
source-backed）。基座样式（feet / casters）不足以成为独立结构 slot（两者皆为不动
装饰、无关节），折入 cage root 的 `base_style` 参数（§8.5 ④ 记录），不虚构第 5 个 slot。

## 槽位图（slot graph）

pattern: `mixed` (root + parallel children + door-parented latch + multiplicity)

```
cage_frame (root; rails + 4 posts + base feet|casters + latch keeper)
   ├─[visuals only]                                    → wall_infill  (wire_mesh / bars / panels; ×mesh_density rods)
   ├─[cage front -Y · hinge REVOLUTE(Z)|REVOLUTE(X)|slide PRISMATIC(X); captured barrel/roller socket] → door_system (×1|2 leaves)
   │      └─[door free edge · REVOLUTE(X)|PRISMATIC(Y)] → latch
   └─[cage interior · FIXED|PRISMATIC(-Y)|visuals]      → interior    (cabinet / drawer / shelves)
```

- **slot 顺序 / parent**：`cage_frame` 是 root（唯一被复用的 parent）。`wall_infill`、
  `interior`、`door_system` 都把各自 joint 的 `parent=cage`（parallel children），只声明
  `downstream`（re-export cage）→ assembler 不发自动 chain joint。`latch` 在
  `door_system` 之后运行，`parent=` 主门 part（`access_door` 或 `door_leaf_0`，从
  model 查找），同样只声明 `downstream`。
- **接口点位**：door → cage 前面 (-Y) 门柱/顶轨面；latch → 门自由边（每个门模块由
  `resolve_config` 派生自由边坐标）；interior → cage 底部搁板/滑轨面。
- **跨 slot joint type/axis/range**：hinged door REVOLUTE(Z, [0,pi/2]) / awning
  REVOLUTE(X, [0,pi/2]) / sliding PRISMATIC(X, [0,door_w])；latch REVOLUTE(X,
  ±0.75) / PRISMATIC(Y, [0,0.04])；drawer PRISMATIC(-Y, [0,0.28])。
- **互斥/派生/sequenced**：`shelf_stack` 无 payload part、无 interior joint；
  `pull_out_drawer` 从前开口拉出，与关门（sliding/awning 的 q=0 或 hinged 的 q=pi/2）
  是**顺序机构**（先开门再拉抽屉）→ 声明 element/part-scoped `allow_overlap(payload,
  door)`，保留全行程（AUTHORING §C sequenced 例外）。

## 每槽位 Module Emits / Interfaces

### Slot root / module cage_frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cage_frame` (single root part) | origin L71 |
| visuals | `front_base_rail`/`rear_base_rail`/`side_base_rail_*`/`front_top_rail`/`rear_top_rail`/`side_top_rail_*` + `front_left_post`/`front_right_post`/`rear_left_post`/`rear_right_post` + `foot_*` OR `caster_*` + `latch_keeper` | origin L74-L118; caster L89-L141 |
| internal joints | none (root, static frame) | — |
| downstream interface | `cage_frame` part, `front_base_rail` visual, face `positive_z`, anchor `(0,0,bottom_z)` (informational; children wire manually) | — |

### Slot A / module wire_mesh | vertical_bar_grille | solid_perforated_panels
| emits | 描述 | 来源 |
|---|---|---|
| parts | none | — |
| visuals (added to cage) | wire: `{left,right}_side_vertical_i`/`_horizontal_i`, `rear_vertical_i`/`rear_horizontal_i`, `roof_*`; grille: `*_vertical_i` (stout, no horizontals); panels: `panel_{left_side,right_side,rear,roof}` | origin L94-L115; grille L95-L109; panels L89-L110 |
| downstream interface | re-export cage (passthrough) | — |

### Slot B / module single_hinged_door | double_door | sliding_gate | top_awning
| emits | 描述 | 来源 |
|---|---|---|
| parts | `access_door` (single/sliding/awning) or `door_leaf_0`,`door_leaf_1` (double) | origin L136; double L157 |
| visuals | `hinge_stile`+`free_stile`+`top_rail`+`bottom_rail`+`middle_rail` + wire/bar/panel fill + `upper/lower_hinge_barrel`+`*_hinge_leaf` (or `hanger_bracket/roller` for sliding) + `latch_plate` | origin L148-L227; sliding L186-L204; awning L147-L218 |
| internal joints | `cage_to_door` / `cage_to_door_leaf_{0,1}` REVOLUTE(Z) \| REVOLUTE(X) \| PRISMATIC(X) | origin L234-L242; double L212-L221; sliding L210-L217; awning L233-L241 |
| upstream interface | **none declared** (parallel-children; parents to cage) | — |
| downstream interface | re-export cage (passthrough) | — |

### Slot C / module rotating_latch | sliding_bolt
| emits | 描述 | 来源 |
|---|---|---|
| parts | `latch_handle` | origin L245 |
| visuals | rotating: `pivot_pin`+`drop_hasp`+`pull_knob`; sliding: `bolt_body`+`pull_knob` | origin L246-L253; bolt L246-L251 |
| internal joints | `door_to_latch` REVOLUTE(X, ±0.75) \| PRISMATIC(Y, [0,0.04]) | origin L254-L262; bolt L256-L262 |
| upstream interface | **none declared**; parents to the primary door part | — |
| downstream interface | re-export cage (passthrough) | — |

### Slot D / module fixed_cabinet | pull_out_drawer | shelf_stack
| emits | 描述 | 来源 |
|---|---|---|
| parts | `red_payload` (cabinet/tray) or none (shelf_stack) | origin L122; drawer L148; shelf none |
| visuals | cage: `bottom_shelf` / `slide_rail_*` / `shelf_level_i`; payload: `red_cabinet`+`top_cap`+`front_handle` | origin L119-L125; drawer L121-L152; shelf L119-L132 |
| internal joints | `cage_to_payload` FIXED \| PRISMATIC(-Y, [0,0.28]) \| none | origin L126-L132; drawer L153-L159 |
| upstream interface | **none declared**; parents to cage | — |
| downstream interface | re-export cage (passthrough) | — |

活动件语义：door 开合、latch 锁闭、drawer 拉出。不动细节（rails/posts/feet/casters/
mesh/bars/panels/shelves/keeper/hinge barrels）写成宿主 part visual，非独立 part
（Rule 1）。captured hinge barrel / roller / caster socket 用 element-scoped
`allow_overlap`（Rule 2 例外），joint 原点落在真实 post/rail 几何（origin honesty）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `wall_infill_module` | enum | wire_mesh / vertical_bar_grille / solid_perforated_panels | wire_mesh | choice | procedural sampler | Slot A |
| `door_module` | enum | single_hinged_door / double_door / sliding_gate / top_awning | single_hinged_door | choice | procedural sampler | Slot B |
| `latch_module` | enum | rotating_latch / sliding_bolt | rotating_latch | choice | procedural sampler | Slot C |
| `interior_module` | enum | fixed_cabinet / pull_out_drawer / shelf_stack | fixed_cabinet | choice | procedural sampler | Slot D |
| `base_style` | enum | leveling_feet / casters | leveling_feet | choice | procedural sampler (cage root visual) | origin L89; caster L89-L141 |
| `palette_style` | enum | 6 colorways | industrial_gray | choice | procedural sampler | §8.5 ⑥ |
| `mesh_density` | int | {5,6,7} verts/side (obs origin 7 fine, mesh_density 5 coarse) | 7 | conditional | only wire_mesh; else n/a | origin L96, mesh_density L96 |
| `width_scale` | float | [0.85, 1.20] | 1.0 | independent | uniform, clamp; cage X | origin L60 |
| `depth_scale` | float | [0.85, 1.20] | 1.0 | independent | uniform, clamp; cage Y | origin L61 |
| `height_scale` | float | [0.85, 1.20] | 1.0 | independent | uniform, clamp; cage Z | origin L62 |
| `door_w` | float | derived | — | equation | `= width - post - 0.02` (single/sliding) / `(width - post)/2 - 0.012` (double leaf) | origin L138 |
| `door_h` | float | derived | — | equation | `= height - 0.06` | origin L137 |
| `door_open` | float | [1.30, 1.57] | 1.57 | independent | revolute door upper (rad); clamp ≤ pi/2 | origin L241 |
| `latch_throw` | float | [0.03, 0.05] | 0.04 | conditional | sliding_bolt only; else revolute ±0.75 | bolt L262 |
| `drawer_travel` | float | derived | 0.28 | equation | `= depth - 0.22` (tray stays partly captured) | drawer L159 |
| (—) | constraint | — | — | inequality | `pull_out_drawer` + closed door → sequenced `allow_overlap(payload,door)`; keep full travel | drawer/door |

所有 equation/inequality/conditional 在 `resolve_config` 内求解；builder 不失败。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: ≤ 12 s** (hang-guard `--compile-timeout 60`).
Geometry is entirely primitives — `Box`, `Cylinder`, `Sphere` (no meshes, no
LatheGeometry, no boolean sculpting). The heaviest seed is a fine `wire_mesh`
(~2×(7 verts+8 horiz) side rods + rear + roof ≈ 60 thin cylinders) plus a door
lattice — all default tessellation (≤32 seg). Expect 3-8 s/seed. If over, cut
`mesh_density` upper first. Small cylinders (rods/barrels/casters) use default
segment counts; no hero surface needs >32.

## Multiplicity / Copy Logic

**两根 multiplicity 轴**：

### 轴 1 — `mesh_density`（wire_mesh 每面钢丝根数）
- `count_param`: `mesh_density`; `N_range` product `[5,7]`, test `[5,7]`; sampling
  domain 加权：`{7: 0.5, 6: 0.2, 5: 0.3}`（细密偏多，与 origin 一致）。
- copied object: side/rear vertical `_rod_z` + horizontal `_rod_y`/`_rod_x` 钢丝，
  数量由 `mesh_density` 派生（verticals = mesh_density, horizontals ≈ mesh_density+1）。
- naming: `{left,right}_side_vertical_{i}` / `_horizontal_{i}` / `rear_vertical_{i}` /
  `rear_horizontal_{i}` / `roof_*`. placement: 沿面均匀分布。joint policy: 无（全为
  cage 装饰 visual）。
- source/gating: origin (fine 7) L96, mesh_density (coarse 5) L96；仅 `wire_mesh`
  参与，`vertical_bar_grille`/`solid_perforated_panels` 该轴写 `n/a`。
- 数量变化不改主体形态（仍是 open wire 面）。

### 轴 2 — 门扇数（door leaf count，折入 door 候选，N 不计数只覆盖）
- 1 扇（single_hinged/sliding/awning）vs 2 扇（double_door）。每扇独立 REVOLUTE-z
  hinge，命名 `door_leaf_{0,1}`。source: origin (1) / double_door (2)。作为 ①
  skeleton candidate 直接体现，非独立采样轴。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | door skeleton：单扇（origin, forked_anchor）／双扇（double_door，2 门 part+2 joint）／sliding gate（sliding_door）／awning（top_hinge_awning）；interior：fixed cabinet part（origin）／pull-out tray part（drawer_payload）／无 payload 的 shelf stack（shelf_levels，删掉 payload part）。全部 source-backed。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：`mesh_density`{5,6,7}（origin/mesh_density），门扇 1↔2（origin/double_door）。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | door：REVOLUTE(Z)（origin）↔ PRISMATIC(X)（sliding_door）↔ REVOLUTE(X)（top_hinge_awning）；latch：REVOLUTE(X)（origin）↔ PRISMATIC(Y)（sliding_bolt_latch）；interior：FIXED（origin）↔ PRISMATIC(-Y)（drawer_payload）。全部 forked_anchor；每种类型都在 sweep 中出现。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | **登记进 slot_choices 的 wall_infill slot**：open crossed wire mesh（origin，Macro Surface Construction）／stout vertical-bar grille（vertical_bar_grille，Macro Surface Construction）／solid perforated sheet panel（solid_perforated_panels，Planar Boundary Form）。三种可识别的墙面构成原型。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | `latch_keeper` 挂扣、hinge barrels/leaves、`front_handle`、base_style（leveling feet vs swivel casters，均为宿主 cage visual，随 ⑤ 缩放派生位置）、middle_rail。source_type=record_only（origin/mobile_caster_base）。装饰随 cage 面/⑤ 尺寸派生。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：width/depth/height_scale ∈[0.85,1.20]；door_open ∈[1.30,1.57]，latch_throw ∈[0.03,0.05]。关节运动包络（每个非-continuous joint）：hinged door REVOLUTE-Z，open 外向，[0, door_open≤pi/2]；sliding door PRISMATIC-X，[0, door_w]；awning REVOLUTE-X，[0, pi/2]；latch REVOLUTE-X [−0.75,0.75] 或 PRISMATIC-Y [0,0.04]；drawer PRISMATIC-(-Y) [0, drawer_travel]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)`；targeted `ctx.pose` — 门开→关位移、latch 锁闭位移、drawer 拉出位移。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted/metal；配色 ≥6 colorway：`industrial_gray`、`safety_yellow_black`、`galvanized_zinc`、`municipal_blue`、`workshop_green`、`powder_black`。材质大类覆盖 ≥ ceil(0.5×6)=3。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 mesh/bar/panel 三种墙面、single/double/sliding/
awning 四种门、cabinet/drawer/shelf 三种内部、feet/caster 两种基座、材质配色多样、
门/latch/drawer 全程不穿模。

## 采样与覆盖审计

总组合数（distinct slot-choice tuple 上界）：
- wall_infill 3 (× mesh_density 3 for wire = 5) × door 4 × latch 2 × interior 3 × base 2 = 5×4×2×3×2 = **240**。

理由：240 < 富类别建议 300，因为真实结构词汇收敛——所有样本共享同一「box 钢框 +
可动门 + 内部载荷 + 墙面填充」cell，可动轴离散槽有限。不硬凑组合空间（红线：不反推
上游变体数量）。report-only，不设 gate。

seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`
依次抽 wall_infill、door、latch、interior、base_style、palette，再按 compatibility
抽 mesh_density（wire_mesh 时）、连续 scale。seed 0 pinned 到 origin 母本组合
（wire_mesh×7 + single_hinged + rotating_latch + fixed_cabinet + feet, industrial_gray）
作为 documented regression anchor（sparse override，其余 seed 全 procedural）。
random sweep `0-15`（fast）→ `0-35`（final）→ corner。

Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察；真实上界 240，
低于 300 的原因为结构词汇收敛，已记录。report-only。

Controlled local parameterization：`width_scale`/`depth_scale`/`height_scale`（cage
包络，door_w/door_h/drawer_travel 由其 equation 派生）、`door_open`、`latch_throw`
（conditional）。全部在 `resolve_config` clamp / 派生；不破坏 captured-socket 接口、
hinge 原点、multiplicity。连续尺寸契约：先采 independent（3 scale + door_open）→
equation 派生 door_w/door_h/drawer_travel → conditional 解析 latch_throw/mesh_density。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 wall_infill→door→latch→interior→base→palette，加权 choice；multiplicity 各自加权 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | mesh_density 仅 wire_mesh；shelf_stack 无 payload joint；drawer+closed door → sequenced allow_overlap；其余正交自由组合 | 无 floating / collision / 轴错误 / max-N / bulky / 可选子件失败 |
| controlled local variation | 5 个 clamp 连续 scale + door_open + latch_throw | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| wall_infill | 3 | yes | yes | wire/bars/panels |
| door_system | 4 | yes | yes | single/double/sliding/awning |
| latch | 2 | yes | no | rotating/sliding — 源池只支持 2 种 latch，降到 2 并说明 |
| interior | 3 | yes | yes | cabinet/drawer/shelf |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ mesh_density / base axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented 母本 override only)
- compatibility gating prevents illegal combos (mesh_density only wire_mesh; shelf_stack no payload joint) in `resolve_config`
- controlled local scales clamped; cannot break captured-socket interfaces, hinge/prismatic origin honesty, or multiplicity
- cross-part scale dependencies (door_w/door_h/drawer_travel) derived in `resolve_config`
- captured hinge-barrel / roller / caster overlaps are element-scoped `allow_overlap` (not broad part-level); drawer+door sequence is a documented part-scoped allowance
- key joints have expected type/axis/range: door REVOLUTE(Z)/REVOLUTE(X)/PRISMATIC(X); latch REVOLUTE(X)/PRISMATIC(Y); drawer PRISMATIC(-Y); cabinet FIXED
- copied `*_vertical_i` / `door_leaf_i` / `shelf_level_i` follow naming + placement policy
- `run_industrial_safety_cage_tests` calls `fail_if_parts_overlap_in_sampled_poses` + >=1 targeted `ctx.pose` per mechanism (door, latch, drawer)

## Reject cases

- Door swings/slides into the cage frame or wall infill at its motion extreme → shrink `door_open` / size door slightly under the opening / offset the hinge plane just outside the front face.
- double_door leaves collide at center when both closed → leave a small center gap (leaf_w < half-opening).
- Latch on the door free edge collides with the keeper or door mesh through its travel → place the bolt/hasp clear; keeper is a thin standoff.
- pull_out_drawer collides with a closed door but is NOT declared sequenced → declare part-scoped `allow_overlap(payload, door)` with a sequence reason; never strangle drawer travel.
- Wall infill rods/panels float off the frame (not embedded into rails/posts) → penetrate rods into rail/post channel (contact) so no disconnected islands.
- Caster/hinge-barrel hardware floats or over-broad part-level allow → element-scoped captured-socket allow_overlap only.
- Downgrading distinct wall constructions (mesh vs bars vs solid) to identical geometry (Rule 3 form-family violation).

## 与相邻类别的边界

- 不该混入：**Industrial / Blast door**（单块装甲门扇本身即整体对象，无 enclosure、无墙面填充、无内部载荷）。
- 不该混入：普通货架 / 层架（无可动防护门、无 mesh/bar/panel 防护墙面身份特征）。
- 不该混入：**Industrial / Safety_cage** 之外的宠物笼/动物笼（家用装饰域，非工业防护网罩成熟域）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | latch slot 仅 2 candidate（源池只含 rotating + sliding_bolt 两种 latch），符合"样本池不足降到 2 并说明"。base_style（feet/casters）折入 root 参数而非第 5 slot，避免 slot 爆炸。 |

## 模板实现备注（可选）
- cage 包络（width/depth/height）single-sourced in `ResolvedConfig`（Contract 3c），door/interior/infill 挂点全部从中派生。
- captured hinge barrel / hanger roller / caster socket → 原始 joint（no MatingContract, grandfathered）+ element-scoped `allow_overlap`，与全部 5 星源一致（Rule 2 例外）。
- wire_mesh 的 side/rear/roof 钢丝与门 lattice 共享 `_rod_*` helper；door 模块共享 door-frame helper。
- pull_out_drawer + 任意门 → part-scoped `allow_overlap(red_payload, <door part>)`（sequenced：先开门再拉抽屉），保留全 drawer_travel。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`：cage root 声明 downstream；wall_infill/interior/door_system/latch 只声明 downstream（re-export cage）→ 无自动 chain joint，各模块发原始 joint（parallel-children，同 Tipping_Barrow 惯用）；latch parent = 主门 part。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | root/A/B/C/D | cage + wire_mesh + single_hinged + rotating_latch + fixed_cabinet | `rec_use-...c0c2456f` (origin 母本) | L56-L343 | cage part tree, 钢丝墙面, 单扇 REVOLUTE-z 门, 旋转 latch, FIXED 载荷, 全部 test 语义 |
| S2 | B ① | double_door | `rec_safety_cage_var_double_door` | L155-L233 | 双扇镜像 REVOLUTE-z 门 |
| S3 | D ② | pull_out_drawer | `rec_safety_cage_var_drawer_payload` | L121-L160 | PRISMATIC-y 抽屉滑轨 |
| S4 | A mult | mesh_density | `rec_safety_cage_var_mesh_density` | L96-L116 | wire 钢丝根数 multiplicity 下界 |
| S5 | root ④ | casters | `rec_safety_cage_var_mobile_caster_base` | L89-L141 | swivel caster 基座装饰 |
| S6 | D ① | shelf_stack | `rec_safety_cage_var_shelf_levels` | L119-L132 | N 层内部搁板栈 |
| S7 | C ② | sliding_bolt | `rec_safety_cage_var_sliding_bolt_latch` | L244-L262 | PRISMATIC-y 插销 latch |
| S8 | B ② | sliding_gate | `rec_safety_cage_var_sliding_door` | L120-L216 | PRISMATIC-x 推拉门 + 顶轨 |
| S9 | A ③ | solid_perforated_panels | `rec_safety_cage_var_solid_perforated_panels` | L89-L110 | 实心穿孔板墙面（Planar Boundary Form） |
| S10 | B ② | top_awning | `rec_safety_cage_var_top_hinge_awning` | L134-L240 | 顶铰上翻 awning REVOLUTE-x 门 |
</content>
</invoke>
