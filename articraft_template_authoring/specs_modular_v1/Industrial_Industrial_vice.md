# Modular Spec - Industrial / Industrial vice

## 元信息
| 项 | 值 |
|---|---|
| slug | `Industrial_Industrial_vice` |
| template path | `agent/templates/Industrial_Industrial_vice.py` |
| test path (optional) | `tests/agent/test_Industrial_Industrial_vice_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (serial spine base->body->front_jaw->lead_screw + parallel side_lock child of base + 2 multiplicity axes) |
| function stem | `industrial_industrial_vice` (exports `build_industrial_industrial_vice`, `config_from_seed`, `run_industrial_industrial_vice_tests`) |

`pattern = mixed`: the vise is a fixed kinematic spine `base (root) -> body ->
front_jaw -> lead_screw`, plus a `side_lock` handle as a parallel child of the
base. All joints are emitted manually (parallel-children idiom, same as
`Urban_Environment_Tipping_Barrow`): every slot declares
only a `downstream` interface (re-export the base) so the assembler never emits
an auto chain joint. Five slots pick the module for each spine link; two
multiplicity axes (`lug_count` on the base, `plate_screw_count` on the jaw
plates) ride on top.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 9 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 10 were read in full (origin full + 9 diffs against origin) |

Samples (all `collections=["workbench"]`, `rating=5`, synced from `articraft_data`):

- `rec_industrial__industrial_vice__002_png_b597f2dc9a6d47d092782f8db39a1c94` - ORIGIN 母本: round cast swivel base (4 bolt lugs + turntable), cast arched blue body + rear anvil + fixed jaw plate, sliding front jaw (PRISMATIC), lead screw + T-handle (CONTINUOUS spin), side swivel-lock handle.
- `rec_industrial_vice_var_fixed_base` - ① skeleton + ② joint: `base_to_body` REVOLUTE swivel -> FIXED bolt-down; removes the `side_lock` part; flat base, no turntable.
- `rec_industrial_vice_var_rect_base` - ③ base form: round swivel disc -> rectangular flat plate + 4 square corner pads + central turntable boss.
- `rec_industrial_vice_var_continuous_swivel` - ② joint: `base_to_body` REVOLUTE (bounded) -> CONTINUOUS (unbounded 360 turntable).
- `rec_industrial_vice_var_lever_drive` - ② joint + ③ handle: T-handle CONTINUOUS spin -> single pivoting cam lever, `front_jaw_to_screw` CONTINUOUS -> REVOLUTE bounded arc (+/-1.20).
- `rec_industrial_vice_var_welded_box_body` - ③ body form: cast arched throat body -> fabricated welded steel box (flat L-plates, straight slide tunnel, no throat arch).
- `rec_industrial_vice_var_pipe_jaws` - ③/① jaw type: adds integral lower toothed **pipe V-jaws** (`fixed_v_jaw` on body + `moving_v_jaw` on front_jaw) below the flat plates (combination vise).
- `rec_industrial_vice_var_lugs_three` - multiplicity: base mounting lugs 4 -> 3 at regular 120deg spacing.
- `rec_industrial_vice_var_lugs_six` - multiplicity: base mounting lugs 4 -> 6 at regular 60deg spacing.
- `rec_industrial_vice_var_plate_screws` - multiplicity/④: jaw-plate retaining screws -> 4 indexed screws per plate at regular vertical spacing (helper `_add_plate_screws`).

## 核心身份

A **bench / machinist vise (工业台钳)**: a bolt-down **base** (round cast swivel
turntable or rectangular plate) carrying a heavy **body** casting whose rear
column mounts the fixed jaw + rear anvil, a **sliding front jaw** driven in/out
along a horizontal PRISMATIC slide, and a horizontal **lead screw + handle** that
spins/cranks the jaw closed. Both jaws carry replaceable steel plates (and, on a
combination vise, integral lower toothed pipe V-jaws). Optional features: a
rotating swivel turntable base (REVOLUTE bounded / CONTINUOUS 360) with a side
swivel-lock handle, or a rigid fixed-bolt-down base. The category-defining,
always-present non-fixed joint is the **jaw slide** (PRISMATIC) plus the **screw
drive** (CONTINUOUS spin or REVOLUTE cam arc); the swivel adds a third rotary DOF
when present. Default mature domain: 100-160 mm jaw-width class bench vise.

Not to be confused with the neighbouring **Industrial / Hydraulic press** or
**Industrial / Drill press table** (a large standing frame with a vertical ram /
column, not a hand-cranked horizontal jaw on a bolt-down base), or a plain
**Industrial / Industrial clamp / C-clamp** (a single-piece frame + screw, no
cast body, no swivel base, no rear anvil, no sliding boxed jaw).

## 槽位 + 候选模块表

### Slot A: base (root, ③ Primary Form Family + multiplicity `lug_count`)

The bolt-down root. Both candidates expose the identical top swivel-boss face at
`z = boss_top` (single-sourced), so the mount joint is base-form independent. The
`lug_count` multiplicity axis rides here (round base: N radial mounting lugs).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `round_base` | forked_anchor (origin, lugs_three, lugs_six) | `rec_industrial__...b597f2dc` L36-L49; `rec_industrial_vice_var_lugs_three` L36-L67; `rec_industrial_vice_var_lugs_six` L36-L59 | L36-L49 | eligible | round cadquery cast disc + N mounting lugs at regular angular spacing + raised turntable boss + lower ring; bolt-hole cuts. **Volumetric Envelope Form** |
| `rect_base` | forked_anchor | `rec_industrial_vice_var_rect_base` | L37-L60, L137 | eligible | rectangular flat plate + 4 square corner mounting pads + central circular turntable boss; bolt-hole cuts through pads. **Planar Boundary Form** |

### Slot B: body (③ body form)

Emits the `body` part (the heavy jaw column). Same part tree across candidates:
body casting + `rear_anvil` + `fixed_plate` (+ N `fixed_plate_screw_i`) + cast-on
`embossed_mark_i` / `rear_rib` / `front_rib` + `body_paint_chip`. Only the body
envelope prototype changes.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `cast_body` | forked_anchor (origin) | `rec_industrial__...b597f2dc` L52-L86 | L52-L86 | eligible | cadquery arched cast body: XZ side-profile extrude + bottom seat disc + boolean throat (rect + arch) cut + rectangular slide tunnel cut; filleted cast look. **Volumetric Envelope Form** |
| `welded_box_body` | forked_anchor | `rec_industrial_vice_var_welded_box_body` | L52-L84 | eligible | fabricated welded box: flat L-shaped XZ plate profile, straight rectangular slide tunnel, **no** curved throat arch, tighter weld-bead fillet. **Planar Boundary Form** |

### Slot C: mount (② swivel joint type + ① side_lock presence)

Emits the `base_to_body` articulation, and (for swivel mounts) the parallel
`side_lock` part + its `base_to_side_lock` REVOLUTE. This is the ②/① axis.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `revolute_swivel` | forked_anchor (origin) | `rec_industrial__...b597f2dc` L221-L229, L248-L256, L212-L219 | L221-L229 | eligible | `base_to_body` **REVOLUTE** axis Z bounded `[-swivel_range, +swivel_range]`; adds `side_lock` (lock boss + radial lever) + `base_to_side_lock` REVOLUTE(Z, +/-0.8). |
| `continuous_swivel` | forked_anchor | `rec_industrial_vice_var_continuous_swivel` | L223-L228 | eligible | `base_to_body` **CONTINUOUS** axis Z (unbounded 360 turntable); same `side_lock`. |
| `fixed_mount` | forked_anchor | `rec_industrial_vice_var_fixed_base` | L212-L234 | eligible | `base_to_body` **FIXED** (rigid bolt-down); **no** `side_lock` part (① skeleton -1 part). |

### Slot D: jaw_set (③/① jaw type + multiplicity `plate_screw_count`)

Emits the `front_jaw` part (front casting + `slide_bar` + `moving_plate` + N
`moving_plate_screw_i`) and the `body_to_front_jaw` PRISMATIC slide. The pipe
candidate additionally emits toothed V-groove pipe jaws (a body visual +
front_jaw visual). `plate_screw_count` multiplicity rides here (applies to both
the body `fixed_plate` and the front `moving_plate`, single-sourced).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `flat_jaws` | forked_anchor (origin) | `rec_industrial__...b597f2dc` L166-L187, L230-L238 | L166-L187 | eligible | front jaw casting + `slide_bar` + flat `moving_plate` + N retaining screws; `body_to_front_jaw` **PRISMATIC** axis X `[0, jaw_travel]`. |
| `pipe_combo_jaws` | forked_anchor | `rec_industrial_vice_var_pipe_jaws` | L120-L205, L252-L294 | eligible | same flat jaws PLUS integral lower toothed pipe V-jaws: `fixed_v_jaw` (body) + `moving_v_jaw` (front_jaw), cadquery toothed V-groove profile (combination vise). Same PRISMATIC slide. **Macro Surface Construction** (adds gripping V-groove surface). |

### Slot E: drive (② screw joint type + ③ handle form)

Emits the `lead_screw` part + the `front_jaw_to_screw` articulation.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `thandle_screw` | forked_anchor (origin) | `rec_industrial__...b597f2dc` L189-L210, L239-L247 | L189-L210 | eligible | lead screw + `screw_collar` + sliding cross `t_handle` + 2 `handle_knob_i` + `screw_end_cap`; `front_jaw_to_screw` **CONTINUOUS** axis X (spins freely). |
| `cam_lever` | forked_anchor | `rec_industrial_vice_var_lever_drive` | L201-L217, L248-L255 | eligible | lead screw + collar + single vertical `cam_lever` + `lever_grip`; `front_jaw_to_screw` **REVOLUTE** axis X bounded arc `[-screw_arc, +screw_arc]` (speed-vise quick clamp). |

硬约束满足: 每个 slot 有 >=2 结构不同 candidate (A=2, B=2, C=3, D=2, E=2); 每个
candidate 有 `forked_anchor` + `model.py:Lx-Ly`。四个 slot 只有 2 个 candidate ->
样本池诚实上界: 已确认变体池对每根轴恰好 fork 一个变体 (origin + 1 fork/轴), 无法
再拆出更多结构不同来源, 故按 SPEC_TEMPLATE 允许降到 2 并说明理由。无
`world_knowledge_extrapolation` candidate (全部 source-backed)。

## 槽位图（slot graph）

pattern: `mixed` (serial spine + parallel side_lock child + multiplicity)

```
base (root; round_base / rect_base; x N lugs)
  |-[base_to_body: REVOLUTE|CONTINUOUS|FIXED, axis Z @ (0,0,boss_top); mount slot]-> body (cast_body / welded_box_body)
  |     |-[body_to_front_jaw: PRISMATIC, axis X @ (0.205,0,0.066)*s; jaw_set slot]-> front_jaw (flat_jaws / pipe_combo_jaws; x N plate screws)
  |     |     |-[front_jaw_to_screw: CONTINUOUS|REVOLUTE, axis X @ (0.055,0,0)*s; drive slot]-> lead_screw (thandle_screw / cam_lever)
  |-[base_to_side_lock: REVOLUTE, axis Z @ (-0.035,-0.095,0.030)*s; only for swivel mounts]-> side_lock
```

- **slot 顺序 / parent**: `base` 是 root。slot 遍历顺序 base -> body -> mount ->
  jaw_set -> drive。`body`/`front_jaw`/`lead_screw` 串成主链; `side_lock` 是 base
  的并联子件 (仅 swivel mount)。所有 joint 手工发射 (parallel-children), 每个 slot
  只声明 `downstream` (re-export base) -> 无自动 chain joint。
- **接口点位**: base 顶部 boss 中心面 `(0,0,boss_top)` (body 座); body 前面 slide
  座 `(0.205,0,0.066)*s` (front_jaw); front_jaw 螺杆孔 `(0.055,0,0)*s` (lead_screw);
  base rim boss `(-0.035,-0.095,0.030)*s` (side_lock)。
- **跨 slot joint type/axis/range**: base_to_body REVOLUTE(Z, +/-swivel_range) /
  CONTINUOUS(Z) / FIXED; body_to_front_jaw PRISMATIC(X, [0, jaw_travel]);
  front_jaw_to_screw CONTINUOUS(X) / REVOLUTE(X, +/-screw_arc);
  base_to_side_lock REVOLUTE(Z, +/-0.8)。
- **互斥/派生**: `fixed_mount` -> 无 side_lock (① 跳过 base_to_side_lock);
  `rect_base` -> lug_count 固定为 4 个 corner pad (不采样 3/6); round_base ->
  lug_count {3,4,6}。base 形态 / body 形态 / mount / jaw / drive 完全正交自由组合
  (挂点用共享 half-extent 派生, 与形态无关)。

## 每槽位 Module Emits / Interfaces

### Slot A / module round_base | rect_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (single root part) | origin L128 |
| visuals | `base_with_bolt_holes` (cadquery cast/plate) + `base_paint_chip_0/1` | origin L129-L136 |
| internal joints | none (root) | - |
| downstream interface | `base` part, `base_with_bolt_holes` visual, face `positive_z`, anchor `(0,0,boss_top)` (informational; children wire manually) | - |

### Slot B / module cast_body | welded_box_body
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` | origin L138 |
| visuals | `body_casting` (cadquery) + `rear_anvil` + `fixed_plate` + N `fixed_plate_screw_i` + `embossed_mark_i` + `rear_rib` + `front_rib` + `body_paint_chip` | origin L139-L164 |
| internal joints | none (base_to_body emitted by mount slot) | - |
| downstream interface | re-export base (passthrough) | - |

### Slot C / module revolute_swivel | continuous_swivel | fixed_mount
| emits | 描述 | 来源 |
|---|---|---|
| parts | `side_lock` (swivel mounts only) | origin L212 |
| visuals | `lock_boss` + `lock_lever` (side_lock) | origin L213-L219 |
| internal joints | `base_to_body` (REVOLUTE/CONTINUOUS/FIXED, Z) + `base_to_side_lock` (REVOLUTE, Z) | origin L221-L229, L248-L256 |
| downstream interface | re-export base (passthrough) | - |

### Slot D / module flat_jaws | pipe_combo_jaws
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_jaw` | origin L166 |
| visuals | `front_casting` (cadquery) + `slide_bar` + `moving_plate` + N `moving_plate_screw_i` + `jaw_paint_chip`; pipe: + `moving_v_jaw` (front_jaw) + `fixed_v_jaw` (added to body) | origin L167-L187; pipe L120-L205, L252-L294 |
| internal joints | `body_to_front_jaw` (PRISMATIC, X, [0, jaw_travel]) | origin L230-L238 |
| downstream interface | re-export base (passthrough) | - |

### Slot E / module thandle_screw | cam_lever
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lead_screw` | origin L189 |
| visuals | `lead_screw` + `screw_collar` + (`t_handle` + 2 `handle_knob_i` + `screw_end_cap`) OR (`cam_lever` + `lever_grip`) | origin L190-L210; lever L201-L217 |
| internal joints | `front_jaw_to_screw` (CONTINUOUS or REVOLUTE, X) | origin L239-L247; lever L248-L255 |
| downstream interface | re-export base (passthrough) | - |

活动件语义: 螺杆 spin/crank 驱动前钳 (screw drive); PRISMATIC slide 开合钳口;
swivel 转台转动钳身; side_lock 锁定转台。不动细节 (anvil / plates / screws /
embossing / ribs / paint chips / V-jaw teeth) 写成宿主 part visual, 非独立 part
(Rule 1)。captured 螺杆/滑杆/锁销/V钳 用 element-scoped allow_overlap (Rule 2
例外, 与全部 5 星源一致); joint 原点落在真实 face 几何 (PRISMATIC 免检)。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `base_module` | enum | round_base / rect_base | round_base | choice | procedural sampler | Slot A |
| `body_module` | enum | cast_body / welded_box_body | cast_body | choice | procedural sampler | Slot B |
| `mount_module` | enum | revolute_swivel / continuous_swivel / fixed_mount | revolute_swivel | choice | procedural sampler | Slot C |
| `jaw_module` | enum | flat_jaws / pipe_combo_jaws | flat_jaws | choice | procedural sampler | Slot D |
| `drive_module` | enum | thandle_screw / cam_lever | thandle_screw | choice | procedural sampler | Slot E |
| `lug_count` | int | {3,4,6} (obs: 4 origin, 3 lugs_three, 6 lugs_six) | 4 | conditional | round_base only; rect_base -> fixed 4 corner pads (axis reported `lugs_rect4`) | origin L38, lugs_three L47, lugs_six L43 |
| `plate_screw_count` | int | {2,3,4} (obs: 4 origin ~2x2, 4 plate_screws column; 2/3 interp within range) | 3 | independent | N retaining screws per jaw plate in a vertical column, both plates | plate_screws L120-L139 |
| `size_scale` | float | [0.90, 1.15] | 1.0 | independent | uniform; scales every cadquery solid (about part origin) + Box/Cyl/Sphere dims + joint origins | origin dims |
| `jaw_travel` | float | [0.060, 0.100] | 0.085 | independent | PRISMATIC upper (rest opening authored ~0.30) | origin L237 |
| `swivel_range` | float | [1.00, 1.45] | 1.35 | conditional | revolute_swivel +/- bound (rad); else n/a | origin L228 |
| `screw_arc` | float | [0.90, 1.30] | 1.20 | conditional | cam_lever REVOLUTE +/- arc (rad); else n/a (continuous) | lever_drive L255 |
| (-) | constraint | - | - | inequality | side_lock geometry capped at world z < boss_top so the swivelling body (z >= boss_top) never sweeps into the stationary lock (sampled-pose clearance) | this spec |

所有 conditional/inequality 在 `resolve_config` 内求解; builder 不失败。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: <= 35 s** (hang-guard `--compile-timeout 90`).
Geometry is dominated by 3-4 cadquery castings per seed: `base` (disc/plate +
N lug unions + 1-2 boss unions + N bolt-hole cuts), `body` (profile extrude +
seat disc + up to 3 boolean cuts), `front_jaw` (profile extrude + 2 cuts), and
(pipe only) 2x `_pipe_v_jaw` (toothed polyline extrude + 1 shaped cut). All
tessellation at `tolerance=0.0008, angular_tolerance=0.09` (cast) / `0.10`
(fabricated). Both pipe V-jaws share ONE cached cadquery solid; screws/plates/
handle/anvil are cheap Box/Cylinder/Sphere. size_scale applied by scaling the
tessellated solid about the part origin (no re-boolean). No lathe/heavy sweep.
Expect 8-20 s/seed; if over, drop angular_tolerance first, then quantize
size_scale for cadquery cache reuse.

## Multiplicity / Copy Logic

**两根独立 multiplicity 轴** (各自加权采样、各自编入 `slot_choices`、各自 clamp、
sweep 各自设上限):

### 轴 1 - `lug_count`（round base 安装耳数）
- `count_param`: `lug_count`; `N_range` product `[3,6]`, test `{3,4,6}`; sampling
  domain 加权: `{4: 0.5, 3: 0.25, 6: 0.25}` (标称 4 高频)。
- copied object: 一个圆形 mounting lug disc + 同位 bolt-hole cut, `for i in
  range(lug_count)` at `angle = i*2*pi/lug_count`, radius `lug_R`。
- naming: 单一 `base_with_bolt_holes` cadquery visual (lugs 融合进铸件, Rule 1)。
  placement: 绕 base rim 等角。joint policy: 无 (静态铸件细节)。
- source/gating: origin N=4 L38, lugs_three N=3 L47-L59, lugs_six N=6 L43-L59。
  `rect_base` 不参与 (固定 4 corner pad), 采样时该轴报 `lugs_rect4`。

### 轴 2 - `plate_screw_count`（每块钳口板固定螺钉数）
- `count_param`: `plate_screw_count`; `N_range` `[2,4]`, test `{2,3,4}`; sampling
  domain 加权: `{2: 0.35, 3: 0.30, 4: 0.35}`。
- copied object: 一枚 `Cylinder(r=0.007,len=0.005)` 埋头螺钉, `for i in
  range(N)` 垂直等距排布于板面 (helper `_add_plate_screws`, source plate_screws)。
- naming: `fixed_plate_screw_{i}` (body) / `moving_plate_screw_{i}` (front_jaw)。
  placement: 板 z 范围内等距列。joint policy: 无 (④ 表面装饰细节, host visual)。
- source/gating: origin (2x2=4) L146-L158, plate_screws (column N=4) L120-L139。
  两块板共用 `plate_screw_count` (resolve_config single-source), body slot 发
  fixed 螺钉、jaw_set slot 发 moving 螺钉。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | side_lock part 存在 (revolute_swivel/continuous_swivel, origin) vs 不存在 (fixed_mount, fixed_base fork) -> part+joint 计数 +/-1; 全部 forked_anchor。 |
| └ multiplicity | 同构件 xN | 有 | 见 §8: lug_count {3,4,6} (origin/lugs_three/lugs_six), plate_screw_count {2,3,4} (origin/plate_screws)。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | base_to_body REVOLUTE(Z, origin) <-> CONTINUOUS(Z, continuous_swivel) <-> FIXED(fixed_base); front_jaw_to_screw CONTINUOUS(X, origin) <-> REVOLUTE(X, lever_drive)。始终存在 PRISMATIC(X, body_to_front_jaw) 与 REVOLUTE(Z, side_lock)。全部 forked_anchor; 每种类型都在 sweep 出现。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | **多处登记进 slot_choices**: base 圆盘转台 (round_base, Volumetric Envelope) / 矩形板 (rect_base, Planar Boundary); body 铸造拱喉 (cast_body, Volumetric Envelope) / 焊接方箱 (welded_box_body, Planar Boundary); jaw 平板 (flat_jaws) / 组合管钳 V 槽 (pipe_combo_jaws, Macro Surface Construction); handle T 型横杆 (thandle) / 单摆凸轮杆 (cam_lever)。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | `embossed_mark_i` (铸字, 4x) / `rear_rib` / `front_rib` (铸筋) / `base_paint_chip`/`body_paint_chip`/`jaw_paint_chip` (掉漆 bare-metal 斑) / 埋头螺钉 (plate_screw_count 档)。source_type=record_only (origin/plate_screws)。装饰几何贴附宿主铸件面 (side face y=-0.083, 随 size_scale 缩放共形)。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale: size_scale[0.90,1.15] (整机等比), jaw_travel[0.060,0.100]。关节运动包络 (每个非-continuous joint): base_to_body REVOLUTE axis Z 双向 [闭合 0, +/-swivel_range<=1.45]; body_to_front_jaw PRISMATIC axis X, open +X, [0, jaw_travel<=0.10]; front_jaw_to_screw REVOLUTE (cam) axis X 双向 [0, +/-screw_arc<=1.30]; base_to_side_lock REVOLUTE axis Z [+/-0.8]。`motion_test_plan`: 跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)`; targeted `ctx.pose` - 前钳 PRISMATIC 平移张开钳口 (opening 增大)、swivel 转钳身、cam lever 摆动、continuous 螺杆采 {0,+/-90,180}。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted (铸件主色) / metal (steel plates+screw+anvil+bare chips+dark caps); 配色 >=6 colorway: `classic_blue`、`machinist_gray`、`safety_red`、`cast_black`、`galv_silver`、`hammertone_green`。材质大类覆盖 (painted+metal 均出现) >= ceil(0.5x2)=1。 |

**收尾自检**: 0-9 seed 渲染须肉眼见到 round/rect 两种 base、cast/welded 两种 body、
flat/pipe 两种钳口、T-handle/cam-lever 两种手柄、swivel/fixed 两种底座、材质配色
多样、PRISMATIC 开合与 swivel 转动全程不穿模。

## 采样与覆盖审计

总组合数 (distinct slot-choice tuple 上界):
- base(round x lug{3,4,6}=3, + rect 1 = 4) x body 2 x mount 3 x jaw 2 x drive 2 x
  plate_screw{2,3,4}=3 = **4 x 2 x 3 x 2 x 2 x 3 = 288**。

理由: 288 < 富类别建议 300, 因为真实结构词汇在此收敛 - 所有样本共享同一
「bolt-down base + 铸身 + 滑动前钳 + 螺杆」cell, 可动轴只有 5 根离散槽 + 2 根小
multiplicity。不硬凑组合空间 (质量红线: 不反推上游变体数量)。report-only, 不设 gate。

seed_domain_policy: `procedural_first`。

Procedural Sampling / Sweep Plan: `config_from_seed(seed)` 用 `random.Random(seed)`
依次抽 base/body/mount/jaw/drive 模块, 再按 compatibility 抽 lug_count (round base
时, 否则报 rect4)、plate_screw_count、palette、连续 scale。seed 0 pinned 到 origin
母本组合 (round_base x4 lugs + cast_body + revolute_swivel + flat_jaws x3 screws +
thandle_screw, classic_blue) 作为 documented regression anchor (sparse override;
其余 seed 全 procedural)。random sweep `0-15` (fast) -> `0-35` (final) -> corner。

Topology target: 1000-seed slot-choice tuple 覆盖用于成熟度观察; 真实上界 288 (见上),
低于 300 的原因为结构词汇收敛, 已记录。report-only。

Controlled local parameterization: `size_scale` (整机等比, 保 mounting 一致)、
`jaw_travel`、`swivel_range` (conditional)、`screw_arc` (conditional)。全部在
`resolve_config` clamp / 解析; 不破坏 captured-socket 接口、joint 原点、multiplicity。
连续尺寸契约: 先采 independent (size_scale/jaw_travel) -> conditional 解析
swivel_range/screw_arc/lug_count/plate_screw_count。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 base->body->mount->jaw->drive, 均匀 choice; multiplicity 各自加权 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | fixed_mount -> 无 side_lock (跳过 base_to_side_lock); rect_base -> lug_count 报 rect4 (不采 3/6); 5 slot x mult 正交自由组合 | 无 floating / collision / 轴错误 / max-N / bulky / 可选子件失败 |
| controlled local variation | 4 个 clamp 连续 scale | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本 (documented anchor); 无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 >=2 | 是否 >=3 | 备注 |
|---|---:|---|---|---|
| base | 2 | yes | no | 池仅 origin(round)+rect_base fork; 降到 2 说明理由 |
| body | 2 | yes | no | 池仅 origin(cast)+welded fork |
| mount | 3 | yes | yes | revolute/continuous/fixed |
| jaw_set | 2 | yes | no | 池仅 origin(flat)+pipe fork |
| drive | 2 | yes | no | 池仅 origin(thandle)+lever fork |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ lug_count/plate_screw_count axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented 母本 override only)
- compatibility gating prevents illegal combos (fixed_mount -> no side_lock; rect_base -> no 3/6 lug sampling) in `resolve_config`
- controlled local scales clamped; cannot break captured-socket interfaces, joint origin honesty, or multiplicity
- captured screw/slide/lock/V-jaw overlaps are element-scoped `allow_overlap` (not broad part-level)
- key joints have expected type/axis/range: base_to_body REVOLUTE/CONTINUOUS(Z) or FIXED; body_to_front_jaw PRISMATIC(X); front_jaw_to_screw CONTINUOUS(X)/REVOLUTE(X); base_to_side_lock REVOLUTE(Z)
- copied `*_lug` / `*_plate_screw_i` follow naming + placement policy
- `run_industrial_industrial_vice_tests` calls `fail_if_parts_overlap_in_sampled_poses` + >=1 targeted `ctx.pose` per mechanism

## Reject cases

- Swivelling body sweeps into the stationary `side_lock` at some swivel angle -> keep side_lock geometry entirely below `boss_top` (body z >= boss_top), never mask with a part-level allow_overlap.
- Sliding jaw closes INTO the fixed jaw/body at prismatic q=0 or over-travel -> author rest opening ~0.30 and PRISMATIC opens +X only (jaw moves away); cap `jaw_travel`.
- Lead screw / slide bar shown floating instead of captured in the jaw/body bore -> element-scoped allow_overlap on the exact captured elements (screw_collar/lead_screw/slide_bar), grandfather the joint.
- Base form swap leaves the body seat / mount joint origin off the new boss face -> single-source `boss_top` in ResolvedConfig; both bases expose it.
- Downgrading the cadquery cast/welded body / arched throat / toothed pipe V-jaw to a crude Box/Cylinder (Rule 3 violation) -> keep `mesh_from_cadquery` profiles.
- Cast-on embossing / ribs / paint chips built at constant size laid over the scaled body face (Rule 4) -> derive positions from `size_scale` so they hug the body across ⑤.
- cam_lever/screw REVOLUTE arc so wide the lever sweeps into the body/jaw -> clamp `screw_arc`.

## 与相邻类别的边界

- 不该混入: **Industrial / Hydraulic press** / **Drill press table** (大型立式框架 + 竖直油缸/立柱行程, 非手摇水平钳口 + bolt-down 底座)。
- 不该混入: **Industrial / Industrial clamp / C-clamp** (单体框架 + 螺杆, 无铸身、无转台、无后砧、无箱式滑钳)。
- 不该混入: 纯装饰台钳模型 (无任何 non-fixed joint) - 本类别至少 PRISMATIC 滑钳 + 螺杆驱动始终存在。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 全部 10 样本 source-backed, 无 world_knowledge_extrapolation。base/body/jaw/drive 四轴各仅 1 fork -> candidate 降到 2 (池上限), mount 有 3。side_lock 抬升到 boss_top 之下以过 sampled-pose swivel clearance (origin 未测 swivel 姿态碰撞)。 |

## 模板实现备注（可选）
- `boss_top` / mounting envelope single-sourced in `ResolvedConfig` (Contract 3c); base 形态正交。
- captured screw/slide/lock/V-jaw socket -> 原始 joint (no MatingContract, grandfathered) + element-scoped `allow_overlap`, 与全部 5 星源一致 (Rule 2 例外)。
- 两块 V-jaw 共享一个缓存 cadquery solid; size_scale 通过对 tessellated solid 绕 part origin `.scale()` 施加 (no re-boolean), 避免重编译。
- side_lock 抬升低于 boss_top 保证 swivel 全程 body 不扫入锁; 若 sampled-pose 仍穿模, 降 swivel_range 或下移 side_lock, 不用 part-level allow_overlap 掩盖。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`: base root 声明 downstream; 其余 slot 只声明 downstream (re-export base) -> 无自动 chain joint, 各模块手工发 joint (parallel-children, 同 Tipping_Barrow 惯用)。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D/E | round_base + cast_body + revolute_swivel + flat_jaws + thandle_screw | `rec_industrial__...b597f2dc` (origin 母本) | L36-L347 | 全 part tree, 铸件几何, PRISMATIC 滑钳 + CONTINUOUS 螺杆 + REVOLUTE 转台 + side_lock, 全部 test/allow_overlap 语义 |
| S2 | A mult | lug_count=3 | `rec_industrial_vice_var_lugs_three` | L36-L67 | 3 耳等角复制 helper |
| S3 | A mult | lug_count=6 | `rec_industrial_vice_var_lugs_six` | L36-L59 | 6 耳等角复制 helper |
| S4 | A ③ | rect_base | `rec_industrial_vice_var_rect_base` | L37-L60 | 矩形板 + corner pad + boss |
| S5 | B ③ | welded_box_body | `rec_industrial_vice_var_welded_box_body` | L52-L84 | 焊接方箱 L-profile + 直滑槽 |
| S6 | C ② | continuous_swivel | `rec_industrial_vice_var_continuous_swivel` | L223-L228 | CONTINUOUS 360 转台 |
| S7 | C ①/② | fixed_mount | `rec_industrial_vice_var_fixed_base` | L212-L234 | FIXED 底座 + 移除 side_lock |
| S8 | D ③/① | pipe_combo_jaws | `rec_industrial_vice_var_pipe_jaws` | L120-L205, L252-L294 | 组合管钳 toothed V-groove |
| S9 | D/B mult | plate_screw_count=4 | `rec_industrial_vice_var_plate_screws` | L120-L139 | N 螺钉等距列 helper |
| S10 | E ②/③ | cam_lever | `rec_industrial_vice_var_lever_drive` | L201-L217, L248-L255 | 凸轮摆杆 REVOLUTE 弧 |
