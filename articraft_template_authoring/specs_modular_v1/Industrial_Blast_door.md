# Modular Spec -- Industrial / Blast door

## 元信息
| 项 | 值 |
|---|---|
| slug | `Industrial_Blast_door` |
| template path | `agent/templates/Industrial_Blast_door.py` |
| test path (optional) | `tests/agent/test_Industrial_Blast_door_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root wall_frame + operation child leaf(es) + control child + leaf_form ③ axis + hinge_count multiplicity) |
| function stem | `industrial_blast_door` (exports `build_industrial_blast_door`, `config_from_seed`, `run_industrial_blast_door_tests`) |

`pattern = mixed`: a single grounded root `wall_frame` part (board-formed concrete
wall + proud steel door frame with a clear opening) carries an **operation**
module that (a) welds operation-specific STATIC mounting hardware (hinge tabs /
head rail / guide channels) onto `wall_frame` as named visuals, (b) creates the
moving door leaf part(s), and (c) emits the wall->leaf articulation(s). A
**control** module then mounts the latch actuator (lever / crash bar / handwheel)
on the active leaf. Two orthogonal axes ride on top: `leaf_form` (③ plate
envelope, a config-driven shared helper registered into `slot_choices`) and
`hinge_count` (multiplicity, swing operations only).

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 8 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 9 were read in full |

Samples (all `collections=["workbench"]`, `rating=5`, synced from `articraft_data`):

- `rec_heavy-industrial-blast-door-matte-black-steel-do_...afa2cf0b` -- ORIGIN 母本
  (concrete wall + steel frame root; single flat leaf on REVOLUTE(-Z) hinge with
  3 barrel hinges; lever handle on REVOLUTE spindle; window bezel + glass + blue
  button + keyed lock).
- `rec_blast_door_var_form_dished_leaf` -- ③ leaf form: flat plate -> convex
  barrel-vault dome (cadquery `threePointArc().extrude().union()`).
- `rec_blast_door_var_joint_crash_bar` -- ② control: lever -> PRISMATIC panic
  push bar (bar tube + 2 brackets, axis +Y inward).
- `rec_blast_door_var_joint_wheel` -- ② control: lever -> REVOLUTE handwheel valve
  (rim ring + 3 spokes + hub, axis -Y leaf normal, 0..pi).
- `rec_blast_door_var_mult_hinges_two` -- multiplicity: `HINGE_Z_LIST` len 2.
- `rec_blast_door_var_mult_hinges_five` -- multiplicity: `HINGE_Z_LIST` len 5.
- `rec_blast_door_var_skeleton_double_leaf` -- ① skeleton: single -> two mirrored
  biparting leaves, 2 REVOLUTE hinges (left/right jambs), centre astragal.
- `rec_blast_door_var_skeleton_sliding` -- ①/② skeleton+joint: swing -> slide;
  leaf rolls +X on a slotted head rail via trolley hangers (PRISMATIC X).
- `rec_blast_door_var_skeleton_vertical_lift` -- ①/② skeleton+joint: swing ->
  guillotine; leaf rises +Z in two C-channel guide rails (PRISMATIC Z).

## 核心身份

A **heavy industrial blast / security door set into a wall**: a grounded
board-formed **concrete wall** with a proud dark-steel **door frame** around a
rectangular clear opening, closed by one or more thick matte-steel **door
leaves** that operate on the category-defining motion (swing on barrel hinges,
bipart, slide on a head rail, or lift like a guillotine). Each leaf carries the
recognizable hardware -- a small rectangular viewing window with a raised black
bezel + glass, a round emergency button, a keyed lock cylinder, and a **latch
actuator** (lever handle, panic crash bar, or rotary handwheel). At least one
real non-fixed joint is always present (the leaf's operation joint). Default
mature domain: a ~1 m x 2 m clear opening, a single ~1 m leaf on 3 barrel hinges
with a lever handle.

Not to be confused with the neighbouring subclass **Industrial / Safety cage**
(a free-standing welded mesh enclosure whose door is a small sub-feature) or a
domestic cabinet/room door -- the blast door is a heavy weldment SET INTO A WALL,
frame + concrete are part of the object, and the leaf is a thick armoured slab.

## 槽位 + 候选模块表

### Slot A：wall_frame (root · grounded chassis)

The grounded root: board-formed concrete wall (lintel + 2 jambs + sill boxes
around the opening) + a proud rectangular steel frame (4 boxes). Same structure
across every seed; the clear-opening WIDTH is the only thing it reads from config
(single/slide/lift openings are ~0.96 m; the double-leaf opening widens to
~1.92 m). This is the ONLY single-candidate slot -- a **module-local fixed
structure** (SPEC_TEMPLATE §4 exception): the wall itself never varies
structurally in the pool; all topology variation lives in the operation/control
slots, and the operation slot adds its own STATIC wall hardware as `wall_frame`
visuals (Rule 1). Registered as root so downstream slots can parent to it.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `wall_frame` | forked_anchor (origin) | `rec_heavy-...afa2cf0b` | L91-L135 | eligible (always) | concrete wall (opening) + proud steel frame + operation-specific static hardware host. Volumetric Envelope Form (fixed). |

### Slot B：operation (child of wall_frame · ① skeleton + ② joint)

The identity axis. Emits the moving leaf part(s), their wall->leaf joint(s), and
the operation-specific STATIC wall hardware (as `wall_frame` visuals). Every leaf
plate is built by the shared `_build_leaf_visuals` helper (so `leaf_form` and
`hinge_count` compose orthogonally).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_swing` | forked_anchor (origin) | `rec_heavy-...afa2cf0b` | L129-L135, L218-L243 | eligible | 1 `door_leaf`; N `hinge_barrel_i`(door) + `hinge_strap_i` + `hinge_tab_i`(wall); `door_hinge` **REVOLUTE** axis (0,0,-1), lower=0. hinge_count multiplicity. |
| `double_swing` | forked_anchor | `rec_blast_door_var_skeleton_double_leaf` | L98-L135, L230-L245, L280-L300 | eligible | 2 mirrored leaves `door_leaf_left/right`, wider opening; `door_hinge_left`(axis(0,0,-1)) + `door_hinge_right`(axis(0,0,+1)) **REVOLUTE**; left-leaf `astragal` bridges centre. hinge_count multiplicity (per leaf). |
| `slide` | forked_anchor | `rec_blast_door_var_skeleton_sliding` | L98-L119, L160-L171, L260-L284 | eligible | ①/② change: 1 centred `door_leaf`; slotted `head_rail` + 2 `rail_bracket_i` (wall) + 2 `hanger_stem_i`/`trolley_i` (leaf top); `door_slide` **PRISMATIC** axis (1,0,0), 0..slide_travel. No hinges. |
| `vertical_lift` | forked_anchor | `rec_blast_door_var_skeleton_vertical_lift` | L61-L67, L98-L119, L170-L183, L267-L277 | eligible | ①/② change: 1 centred `door_leaf`; 2 `guide_channel_i` C-channels (wall) + `edge_runner_i` (leaf sides); `door_lift` **PRISMATIC** axis (0,0,1), 0..open_h. No hinges. |

### Slot C：control (child of active leaf · ② joint)

The latch actuator mounted on the active leaf's front face (near the closing
edge). All three combine with every operation.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `lever_handle` | forked_anchor (origin) | `rec_heavy-...afa2cf0b` | L245-L277 | eligible | `handle_rose`(leaf) + `lever_handle` part (`spindle_hub`+`lever_arm`+`lever_tip`); `handle_spindle` **REVOLUTE** axis (0,-1,0), 0..0.9; tip drops. |
| `crash_bar` | forked_anchor | `rec_blast_door_var_joint_crash_bar` | L79-L92, L250-L300 | eligible | ② change: `push_bar` part (`bar_tube` Cylinder + 2 `bracket_i` + door-face `bar_socket_i`); `push_bar` **PRISMATIC** axis (0,1,0) inward, 0..push_travel. |
| `handwheel` | forked_anchor | `rec_blast_door_var_joint_wheel` | L245-L330 | eligible | ② change: `lever_handle` part = rotary valve wheel (`spindle_hub` + `wheel_rim` TorusGeometry ring + 3 `wheel_spoke_i` Cylinders); `handle_spindle` **REVOLUTE** axis (0,-1,0), 0..handwheel_turn (~pi); rim rotates in leaf XZ plane. |

硬约束满足：operation slot 有 4 个结构不同 candidate，control slot 有 3 个；均为
`forked_anchor` + `model.py:Lx-Ly`。wall_frame 是唯一单-candidate slot（module-local
fixed structure 例外，已说明）。leaf_form（③）作为 config-driven 共享 helper 登记进
`slot_choices`（2 candidate，见 §8.5 ③ 行 + 降到 2 的理由）。无 `world_knowledge_extrapolation`。

## 槽位图（slot graph）

pattern: `mixed` (root + children + ③ form axis + hinge multiplicity)

```
wall_frame (root; concrete wall + steel frame; opening width per operation)
   ├─[jamb hinge tabs / head-rail slot / guide-channel; captured] operation
   │      emits leaf part(s) + door<->wall joint:
   │        single_swing  -> REVOLUTE(0,0,-1) @ (HINGE_X,HINGE_Y,0)
   │        double_swing  -> 2x REVOLUTE(0,0,-/+1) @ (+-HINGE_X,HINGE_Y,0)
   │        slide         -> PRISMATIC(1,0,0)  @ (0,DOOR_Y,0)
   │        vertical_lift -> PRISMATIC(0,0,1)  @ (0,DOOR_Y,0)
   └─[active-leaf front face; captured spindle/bracket] control
          lever_handle -> REVOLUTE(0,-1,0); crash_bar -> PRISMATIC(0,1,0);
          handwheel    -> REVOLUTE(0,-1,0)
```

- **slot 顺序 / parent**：`wall_frame` 是 root（唯一被复用的 parent for operation）。
  `operation` 把 leaf 的 joint `parent=wall_frame`；`control` 把 handle 的 joint
  `parent=<active leaf>`。所有 module 只声明 `downstream`（re-export wall），不声明
  `upstream` -> assembler 不发自动 chain joint，各 module 发原始 joint（parallel-children，
  同 Tipping_Barrow 惯用）。
- **接口点位**：operation 静态硬件（hinge tabs / head_rail / guide channels）嵌入
  wall_frame 面（captured, element-scoped allow_overlap）。leaf 的 captured 接口：
  swing = barrel-on-axis wrapped by frame hinge tab；slide = hanger stem into rail
  slot；lift = edge runner in channel。control 的 captured 接口：spindle hub / bar
  bracket 穿过 rose / socket 进 leaf。
- **跨 slot joint type/axis/range**：见上图。swing REVOLUTE lower=0 upper=swing_upper；
  prismatic slide 0..slide_travel、lift 0..open_h；control lever/handwheel REVOLUTE
  (0,-1,0)、crash_bar PRISMATIC (0,1,0)。
- **互斥/派生**：`hinge_count` 仅 swing（single/double）有意义，slide/lift 记 `hinges_na`；
  double_swing 用宽 opening；operation 与 control / leaf_form 完全正交自由组合。

## 每槽位 Module Emits / Interfaces

### Slot A / module wall_frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wall_frame` (single root part) | origin L92 |
| visuals | `concrete_lintel`+`concrete_jamb_l/r`+`concrete_sill` (boxes around opening) + `steel_frame_top/bottom/left/right` (4 boxes) | origin L91-L124 (adapted box build; opening cut -> additive boxes, not a primitive downgrade) |
| internal joints | none (root, static) | -- |
| downstream interface | `wall_frame` part, `steel_frame_top` visual, face negative_y (front), anchor at opening centre (informational; children wire manually) | -- |

### Slot B / module single_swing | double_swing | slide | vertical_lift
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_leaf` (+`door_leaf_right` for double) | origin L138; double L106 |
| leaf visuals | `leaf_plate`(cadquery box+window cut, ③ form) + `window_bezel`(BezelGeometry) + `window_glass` + `blue_button` + `lock_escutcheon` + `lock_cylinder` + `handle_rose` + swing: N `hinge_barrel_i`/`hinge_strap_i`; slide: `hanger_stem_i`/`trolley_i`; lift: `edge_runner_i` | origin L140-L232; slide L260-L272; lift edge runners |
| wall hardware (wall_frame visuals) | swing: `hinge_tab_i`; slide: `head_rail`+`rail_bracket_i`; lift: `guide_channel_i` | origin L129-L135; slide L160-L171; lift L170-L183 |
| internal joints | `door_hinge`/`door_hinge_left`+`door_hinge_right` REVOLUTE, or `door_slide`/`door_lift` PRISMATIC | origin L234-L243; double L234-L245; slide L276-L284; lift L268-L277 |
| upstream interface | **none declared** (parallel-children; parents joint directly to `wall_frame`) | -- |
| downstream interface | re-export wall downstream (passthrough) | -- |

### Slot C / module lever_handle | crash_bar | handwheel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lever_handle` (lever/handwheel) or `push_bar` (crash bar) | origin L246; crash L245 |
| visuals | lever: `spindle_hub`+`lever_arm`+`lever_tip`; handwheel: `spindle_hub`+`wheel_rim`+3 `wheel_spoke_i`; crash: `bar_tube`+2 `bracket_i` (+ `bar_socket_i` on leaf) | origin L248-L266; wheel L250-L320; crash L250-L280 |
| internal joints | `handle_spindle` REVOLUTE(0,-1,0) or `push_bar` PRISMATIC(0,1,0) | origin L268-L277; wheel L305-L320; crash L285-L300 |
| upstream interface | **none declared** (parents joint directly to the active leaf) | -- |
| downstream interface | re-export wall downstream (passthrough) | -- |

活动件语义：operation joint 开关门（swing/slide/lift）；control joint 收放门闩
（lever 下压 / crash bar 内推 / handwheel 旋转）。不动细节（window/bezel/glass/button/
lock/rose/tabs/rail/channels/astragal）写成宿主 part visual，非独立 part（Rule 1）。
captured hinge/rail/channel/spindle socket 用 element-scoped allow_overlap（Rule 2
例外）；REVOLUTE 铰链原点落在门侧 barrel 轴几何（origin honesty），PRISMATIC 原点
gauge-free（豁免）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `operation` | enum | single_swing / double_swing / slide / vertical_lift | single_swing | choice | procedural sampler | Slot B |
| `control` | enum | lever_handle / crash_bar / handwheel | lever_handle | choice | procedural sampler | Slot C |
| `leaf_form` | enum | flat_plate / dished_leaf | flat_plate | choice | procedural sampler (③) | leaf helper |
| `palette_style` | enum | 6 colorways | matte_black | choice | procedural sampler | palette |
| `hinge_count` | int | {2,3,5} (obs: 3 origin, 2/5 mult variants) | 3 | conditional | only swing ops; slide/lift -> n/a | origin L58, mult L58 |
| `open_h_scale` | float | [0.94, 1.06] | 1.0 | independent | uniform, clamp; scales open_h/leaf_h/frame_out_h + feature z | origin L44 |
| `leaf_w_scale` | float | [0.96, 1.06] | 1.0 | independent | uniform, clamp; scales leaf/opening width | origin L43,L51 |
| `dome_rise_scale` | float | [0.7, 1.4] | 1.0 | conditional | dished_leaf only; scales DOME_RISE | dished L54 |
| `swing_upper` | float | [1.5, 2.1] | 2.0 | conditional | swing REVOLUTE upper (rad); slide/lift/prismatic n/a | origin L242 |
| `handwheel_turn` | float | [2.2, 3.14159] | 3.14159 | conditional | handwheel REVOLUTE upper; else n/a | wheel L315 |
| open_w / frame_out_w / leaf_w | float | derived | -- | equation | single/slide/lift base 0.96/1.12/1.04 * leaf_w_scale; double base 1.92/2.08/0.98 * leaf_w_scale | origin/double L43-L52 |
| open_h / leaf_h / frame_out_h / feature_z | float | derived | -- | equation | base * open_h_scale | origin L44-L53 |
| slide_travel | float | derived | -- | equation | `= open_w + 0.24` (leaf clears opening) | slide L91 |
| (—) | constraint | — | — | inequality | swing hinge upper capped by clearance solver against wall (`clamp_joint_limits`, keepout=wall_frame) | origin L242 |

所有 equation/inequality/conditional 在 `resolve_config` 内求解；builder 不失败。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: <= 25 s** (hang-guard `--compile-timeout 90`). The ONLY
cadquery boolean work is the leaf plate: flat = 1 box minus 1 window box; dished =
box + barrel-vault arc-extrude union + 1 window cut (~3 booleans). double_swing =
2 leaves (~2-6 booleans). Everything else is primitives / mesh geometries:
wall+frame from boxes (no boolean), guide channels / head rail from boxes,
handwheel rim = one `TorusGeometry` (radial 16 / tubular 24), spokes = Cylinders,
bezel = `BezelGeometry`. Both double leaves share one window-box helper. Expect
6-15 s/seed; if over, drop the arc-extrude segments / torus tubular_segments
first. No mesh reused >2x needs a shared instance here (leaves differ by side).

## Multiplicity / Copy Logic

**一根 multiplicity 轴：**

### 轴 1 — `hinge_count`（每摆门叶的桶铰数）
- `count_param`: `hinge_count`; `N_range` product `{2,3,5}`, test `{2,3,5}`; sampling
  domain 加权：`{3: 0.5, 2: 0.3, 5: 0.2}`（标称 3 偏多，5 稀有）。
- copied object: `hinge_barrel_i` (door, Cylinder on the pivot axis) + `hinge_strap_i`
  (door weld strap) + `hinge_tab_i` (wall jamb lug). placement: evenly spaced along
  the leaf height `z_i = LEAF_H * (i+1)/(N+1)` (matches origin 3-list 0.35/1.05/1.75).
- naming: `hinge_barrel_{i}` / `hinge_strap_{i}` / `hinge_tab_{i}` (per leaf for double).
- joint policy: hinges are STATIC weld hardware (visuals), NOT joints; the single
  `door_hinge` REVOLUTE carries the DOF. N changes visual count only, not the joint
  count or the mechanism.
- source/gating: origin N=3 L58, mult_hinges_two N=2, mult_hinges_five N=5.
  `slide`/`vertical_lift` have no hinges -> axis records `hinges_na`.
- 数量变化不改主体形态/机制（仍是同一 swing REVOLUTE）。

（无其它 multiplicity 轴：window/button/lock/rose 各恰好 1 个，spokes 固定 3 根，
brackets 固定 2 个 -- 都不暴露 `*_count`。）

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | operation skeleton candidates：single swing leaf（origin, forked_anchor）／double biparting 2 leaves + 2 hinges（skeleton_double_leaf）／sliding 1 leaf on rail（skeleton_sliding）／vertical guillotine lift（skeleton_vertical_lift）。part/joint 计数随之变（1 leaf/1 joint -> 2 leaves/2 joints；hinge hardware <-> rail <-> channel）。全部 forked_anchor。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：hinge_count {2,3,5}（origin/mult_hinges_two/mult_hinges_five）。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | operation joint：REVOLUTE(-Z) swing（origin）↔ PRISMATIC(X) slide（sliding）↔ PRISMATIC(Z) lift（vertical_lift）。control joint：REVOLUTE(-Y) lever（origin）↔ PRISMATIC(+Y) crash bar（crash_bar）↔ REVOLUTE(-Y, full-turn) handwheel（wheel）。全部 forked_anchor；每种类型都在 sweep 出现。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | leaf plate 形态（登记进 slot_choices 的 `leaf_form` 轴）：flat armoured slab（origin, form_subtype = Volumetric Envelope Form）/ convex barrel-vault dished leaf（form_dished_leaf, threePointArc arc-extrude union, form_subtype = Volumetric Envelope Form）。**降到 2 candidate 的理由**：确认池里只有这两种主体形态原型（其余 8 样本共享 flat slab）；门这一类是 **机制主导**（identity 在 operation/control joint，非 leaf 形态），③ 用 2 个 source-backed 原型合规（SPEC_TEMPLATE §4 允许样本不足降 2 + 说明），不用世界知识硬造第三种。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | `window_bezel`（BezelGeometry raised rect bezel）、`window_glass`、`blue_button`、`lock_escutcheon`+`lock_cylinder`、`handle_rose`、`astragal`（double）、hinge `strap`/`tab` -- 均为宿主 part visual，位置随 ③（leaf 面/中心）与 ⑤（open_h_scale/leaf_w_scale）派生（feature 以 leaf 中心为基准 + 缩放）。source_type=record_only（origin/double）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：open_h_scale[0.94,1.06]、leaf_w_scale[0.96,1.06]、dome_rise_scale[0.7,1.4]（dished）。关节运动包络：swing REVOLUTE axis(0,0,-/+1)，开向 -Y，[闭合 0, 可行上界 swing_upper<=2.1（clamp_joint_limits vs wall）]；slide PRISMATIC axis(1,0,0)，[0, slide_travel=open_w+0.24]；lift PRISMATIC axis(0,0,1)，[0, open_h]；lever REVOLUTE axis(0,-1,0)，[0,0.9]；crash_bar PRISMATIC axis(0,1,0)，[0,push_travel]；handwheel REVOLUTE axis(0,-1,0)，[0,handwheel_turn]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)`；targeted `ctx.pose` -- operation 开门（swing 摆出 -Y / slide 平移 +X / lift 升 +Z）位移 leaf，control 动作（lever tip 下降 / bar 内推 / wheel 旋转）位移 actuator。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal/painted/glass；配色 >=6 colorway：`matte_black`（默认，黑叶+暗钢框）、`safety_hazard`（黄黑警示）、`galvanized`（镀锌银）、`navy_bulkhead`（海军灰蓝）、`rust_oxide`（红锈）、`olive_military`（军橄榄）。材质大类覆盖 >= ceil(0.5×3)=2（metal + painted 必现，glass window 恒有）。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 swing/double/slide/lift 四种 operation、flat 与
dished 两种叶形、lever/crash/wheel 三种 control、hinge 数变化、材质配色多样、门开合全程不穿模。

## 采样与覆盖审计

总组合数（distinct slot-choice tuple 上界）：
- operation(single_swing × hinge 3 = 3, double_swing × hinge 3 = 3, slide 1, lift 1 = 8)
  × control 3 × leaf_form 2 = **8 × 3 × 2 = 48**。

理由：48 < 富类别建议 300，因为真实结构词汇在此收敛 -- 所有样本共享同一「wall+frame
+ 可动 leaf + latch actuator」cell，可动轴只有 operation(4) + control(3) 两根离散槽 +
leaf_form(2) + 一根小 multiplicity(hinge 3 档)。不硬凑组合空间（质量红线：不反推上游
变体数量）。report-only，不设 gate。

seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`
依次抽 operation、control、leaf_form、palette，再按 compatibility 抽 hinge_count（swing
时 {2,3,5} 加权，否则 n/a）、连续 scale。seed 0 pinned 到 origin 母本组合
（single_swing + hinge 3 + lever_handle + flat_plate, matte_black）作为 documented
regression anchor（sparse override，其余 seed 全 procedural）。random sweep `0-15`
（fast）→ `0-35`（final）→ corner。

Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察；真实上界 48（见上），
低于 300 的原因为结构词汇收敛，已记录。report-only。

Controlled local parameterization：`open_h_scale`、`leaf_w_scale`（derive open/frame/
leaf 尺寸）、`dome_rise_scale`（conditional dished）、`swing_upper`/`handwheel_turn`
（conditional）。全部在 `resolve_config` clamp / 派生；不破坏 captured-socket 接口、
hinge 轴几何、multiplicity。连续尺寸契约：先采 independent（open_h_scale/leaf_w_scale）
→ equation 派生 open/frame/leaf 尺寸 + slide_travel → conditional 解析 dome_rise/
swing_upper/handwheel_turn/hinge_count。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 operation→control→leaf_form→palette，均匀 choice；hinge_count 加权 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | hinge_count 仅 swing；double_swing 用宽 opening；operation×control×leaf_form 正交自由组合 | 无 floating / collision / 轴错误 / 门穿墙 |
| controlled local variation | 4 个 clamp 连续 scale | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| wall_frame | 1 | no | no | 单-candidate root（module-local fixed structure 例外，已说明） |
| operation | 4 | yes | yes | single/double/slide/lift |
| control | 3 | yes | yes | lever/crash/wheel |
| leaf_form (③, slot_choices 轴) | 2 | yes | no | flat/dished（样本池仅此两原型，已说明） |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ leaf_form/hinge_count axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented 母本 override only)
- compatibility gating: hinge_count only for swing; double uses wide opening (in `resolve_config`)
- controlled local scales clamped; cannot break captured-socket interfaces, hinge axis geometry, or multiplicity
- cross-part scale dependencies (opening/frame/leaf dims, slide_travel) derived in `resolve_config`
- captured hinge-tab/barrel, rail/hanger, channel/runner, spindle/socket overlaps are element-scoped `allow_overlap` (not broad part-level where avoidable)
- key joints have expected type/axis/range: operation REVOLUTE(-Z)/PRISMATIC(X)/PRISMATIC(Z); control REVOLUTE(-Y)/PRISMATIC(+Y)
- copied `hinge_*_i` follow naming + even-spacing placement policy
- `run_industrial_blast_door_tests` calls `fail_if_parts_overlap_in_sampled_poses` + >=1 targeted `ctx.pose` per mechanism

## Reject cases

- Swing leaf steered past the wall at hinge upper collides with the concrete jamb -> `clamp_joint_limits` vs `wall_frame` (keepout), never a hand-tuned magic upper.
- Sliding / lifting leaf drifts INTO the wall plane (wrong Y) -> leaf front always proud of the frame front face (single-sourced `door_y`); prismatic axis strictly X or Z.
- Double-leaf pair overlaps at the centre with no astragal, or the two leaves interpenetrate -> gap at centre + left-leaf astragal bridging it (element-scoped allow_overlap astragal<->right leaf only).
- Hinge barrels / tabs float off the pivot axis (constant list not scaled with leaf height) -> even-spacing `z_i = LEAF_H*(i+1)/(N+1)`, barrels on the axis, tabs wrapping them (Rule 4 / origin honesty).
- Handwheel rim downgraded from `TorusGeometry` to a flat Box/Cylinder disc, or dished leaf downgraded from arc-extrude to a plain Box (Rule 3 violation).
- Control actuator mounted where it detaches from the leaf (rose/socket not overlapping the spindle/bracket) -> captured spindle/socket overlap declared.
- A fully static model (no non-fixed joint) -> every operation carries a real swing/slide/lift joint.

## 与相邻类别的边界

- 不该混入：**Industrial / Safety cage**（自立焊接网栏，门只是子特征；blast door 是 SET INTO A WALL 的重型 weldment，concrete + frame 属于对象本体）。
- 不该混入：家用橱柜门 / 房间门（薄板、无 concrete 墙 + proud steel frame + 装甲 slab + 工业 latch）。
- 不该混入：**Industrial / Blast door** 与一个纯 mesh 洞（洞是 ③ 的一部分，不是独立类别）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | leaf_form ③ 轴降到 2 candidate（样本池仅 flat + dished 两原型），已在 §8.5 说明；门为机制主导类，identity 在 operation/control joint。wall_frame 单-candidate root（module-local fixed structure 例外）。待人工背书。 |

## 模板实现备注（可选）

- opening/frame/leaf 尺寸 + slide_travel + active_leaf/active_sign single-sourced in `ResolvedConfig`（Contract 3c），operation/control/leaf 派生自其中，operation 与 form 正交。
- captured hinge-tab/barrel、rail/hanger、channel/runner、spindle/bracket-socket -> 原始 joint + element-scoped `allow_overlap`（Rule 2 例外），与 5 星源一致。
- 唯一 cadquery boolean = leaf plate（flat: box+window cut；dished: box+arc-extrude union+window cut）；wall/frame/channels/rail 全 boxes；handwheel rim = TorusGeometry；保编译预算。
- swing REVOLUTE upper 用 `clamp_joint_limits`（clearance solver，keepout=["wall_frame"]，豁免 captured hinge overlap）求解，替代手调角度，跨 leaf 尺寸自适应。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`：wall_frame root 声明 downstream；operation/control 只声明 downstream（re-export wall）→ 无自动 chain joint，各 module 发原始 joint（parallel-children，同 Tipping_Barrow 惯用）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | wall_frame + single_swing + lever_handle + flat_plate | `rec_heavy-...afa2cf0b` (origin 母本) | L37-L389 | wall+frame part tree, swing leaf + REVOLUTE hinge + N barrels, lever handle + REVOLUTE spindle, flat leaf, window/lock/button hardware, all test semantics |
| S2 | ③ | dished_leaf | `rec_blast_door_var_form_dished_leaf` | L54-L75, L137-L180 | barrel-vault dome leaf (arc-extrude union), Volumetric Envelope Form |
| S3 | C ② | crash_bar | `rec_blast_door_var_joint_crash_bar` | L79-L92, L250-L300 | PRISMATIC panic push bar + brackets/sockets |
| S4 | C ② | handwheel | `rec_blast_door_var_joint_wheel` | L245-L330 | REVOLUTE handwheel valve (rim + spokes + hub) |
| S5 | B mult | hinge_count=2 | `rec_blast_door_var_mult_hinges_two` | L58 | hinge_count multiplicity low |
| S6 | B mult | hinge_count=5 | `rec_blast_door_var_mult_hinges_five` | L58 | hinge_count multiplicity high |
| S7 | B ① | double_swing | `rec_blast_door_var_skeleton_double_leaf` | L98-L135, L214-L245, L280-L300 | biparting 2-leaf skeleton + astragal + 2 REVOLUTE |
| S8 | B ①/② | slide | `rec_blast_door_var_skeleton_sliding` | L78-L119, L160-L171, L260-L284 | sliding leaf + slotted head rail + trolley hangers + PRISMATIC X |
| S9 | B ①/② | vertical_lift | `rec_blast_door_var_skeleton_vertical_lift` | L61-L67, L98-L119, L170-L183, L267-L277 | guillotine lift + C-channel guides + PRISMATIC Z |
