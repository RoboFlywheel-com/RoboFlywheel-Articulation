# Modular Spec - Industrial / Hydraulic press

## 元信息
| 项 | 值 |
|---|---|
| slug | `Industrial_Hydraulic_press` |
| template path | `agent/templates/Industrial_Hydraulic_press.py` |
| test path (optional) | `tests/agent/test_Industrial_Hydraulic_press_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root frame + parallel-children ram/bed/control + 2 multiplicity axes) |
| function stem | `industrial_hydraulic_press` (exports `build_industrial_hydraulic_press`, `config_from_seed`, `run_industrial_hydraulic_press_tests`) |

`pattern = mixed`: a single root `frame` part (the fabricated steel press frame)
carries three parallel-children slots, each of which manually parents its own
articulations to the frame (no serial chain joint): the `ram` (the
category-defining vertical PRISMATIC descent), the `bed` (fixed or moving
work-support), and the `control` station (a detached console with articulated
buttons or a lever). Two multiplicity axes ride on top: `bed_pin_count`
(adjustable bed-height pins per column, frame surface decoration) and
`button_count` (push buttons on the console).

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 9 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 10 were read in full (origin full, each variant diffed against origin) |

Samples (all `collections=["workbench"]`, `rating=5`):

- `rec_industrial__hydraulic_press__001_png_...c62c5ca2` - ORIGIN 母本 (H-frame,
  box columns, fixed hydraulic cylinder + gland, FIXED bed, PRISMATIC ram with
  square platen, detached control pedestal with 3 PRISMATIC push buttons + gauge
  + hoses).
- `rec_hydraulic_press_var_c_frame` - ③/① frame form: H-frame -> single rear-spine
  C-frame with cantilever top arm + base arm + gussets (open front/sides).
- `rec_hydraulic_press_var_four_post_frame` - ③/① frame form: two box columns ->
  four cylindrical corner guide posts + collars + side ledges.
- `rec_hydraulic_press_var_tubular_columns` - ③ frame form: box columns -> round
  Cylinder columns (Volumetric Envelope Form).
- `rec_hydraulic_press_var_round_platen` - ③ tooling form: square platen plate ->
  round platen disc (Cylinder) on the ram.
- `rec_hydraulic_press_var_pin_adjustable_bed` - ② bed joint: FIXED bed ->
  vertical PRISMATIC height-adjustable bed (axis +Z, lower=-0.045 upper=0.135).
- `rec_hydraulic_press_var_sliding_bolster_bed` - ② bed joint / ①: FIXED bed ->
  horizontal PRISMATIC sliding bolster (axis -Y, 0..0.20) + bolster rails on
  frame + slide shoes on bed.
- `rec_hydraulic_press_var_lever_valve_control` - ①/② control: 3 PRISMATIC push
  buttons -> one REVOLUTE operating lever (axis X, +-0.55) + pivot boss.
- `rec_hydraulic_press_var_button_count` - ① multiplicity: 3 push buttons -> 5
  push buttons (uniform helper, each a PRISMATIC part).
- `rec_hydraulic_press_var_bed_pin_count` - ④ multiplicity: 3 adjustable bed-pin
  positions per column -> 5.

## 核心身份

An **industrial hydraulic press**: a heavy fabricated-steel **frame** (H-frame
with box or tubular columns, an open C-frame with a cantilever arm, or a
four-post guide-column frame) that carries, rigidly under its top crosshead /
cantilever, a **fixed hydraulic cylinder** (hollow steel shell + gland ring +
hose ports), and drives a vertical **ram** downward on a PRISMATIC stroke (axis
-Z, the category-defining joint) so a **platen** (square plate or round disc)
presses a workpiece against a **bed / bolster** below. The bed is either fixed,
vertically height-adjustable (pins/prismatic), or a horizontally sliding
bolster. Operation is by a detached **control station** (a floor-standing
console linked by flexible hydraulic hoses) carrying either a bank of push
buttons or a rotary operating lever. At least one real non-fixed joint is always
present (the ram PRISMATIC descent). Default mature domain: a ~2 m tall
single-station shop press.

Not to be confused with the neighbouring **Industrial / Drill press table** (a
rotating spindle over a work table - a drill, not a linear pressing ram), the
**Industrial / Ore crusher jaw** (a toggle-driven crushing jaw, not a vertical
ram), or a generic **Industrial vice** (a horizontal screw clamp with no frame
crosshead / hydraulic cylinder).

## 槽位 + 候选模块表

### Slot A: frame (root; ③ Primary Form Family + ① skeleton)

The root steel press frame. All candidates expose the SAME single-sourced
mounting datums (cylinder axis at x=y=0, `cyl_axis_z`; bed contact plane
`bed_contact_z`; hydraulic-port world positions; a floor `control_conduit` stub
toward the console) so the ram / bed / control slots are frame-form independent.
Non-moving detail (seams, bolts, warning labels, foot pads, gussets, wear
plates) is fused as `frame.visual(...)` (Rule 1). The fixed hydraulic cylinder
shell + gland ring are hollow revolved LatheGeometry tubes (faithful hollow
steel shell; the origin used a cadquery boolean cut - same hollow-shell
primitive family, revolved instead of boolean-cut to keep the compile budget
low and avoid a heavy cadquery dependency; NOT a Box/Cylinder downgrade).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `h_frame` | forked_anchor (origin) | `rec_industrial__hydraulic_press__001` | L52-L110 | eligible | two rectangular `Box` columns at +-col_x + massive top crosshead + lower sill + flared foot pads + inner wear plates + bed ledges. **Volumetric Envelope Form** |
| `h_frame_tubular` | forked_anchor | `rec_hydraulic_press_var_tubular_columns` | L52-L54, L99-L101 | eligible | identical H-frame part tree; columns are round `Cylinder` (r=0.15) instead of Box; port bracket bridges the round surface. **Volumetric Envelope Form** (round vs prismatic column) |
| `c_frame` | forked_anchor | `rec_hydraulic_press_var_c_frame` | L52-L112 | eligible | ①/③: single robust rear `rear_spine` Box + forward `top_cantilever` + `base_arm` + `base_foot` + spine/base gussets + `bed_support` riser + `bed_ledge_plate`; open front/left/right. **Macro Surface Construction** (open C vs closed portal) |
| `four_post` | forked_anchor | `rec_hydraulic_press_var_four_post_frame` | L52-L90 | eligible | ①/③: top crosshead + lower sill tied by four cylindrical corner guide `post_i` (r=0.06) + top/bottom collars + corner foot pads + side bed ledges. **Volumetric Envelope Form** (four slender posts vs two slab columns) |

### Slot B: ram (defining PRISMATIC descent; ③ tooling form)

The vertical ram + tooling. Same part tree across candidates (`ram_rod` polished
cylinder + `ram_collared_head` + `press_platen` bell + platen face), on the
category-defining `frame_to_ram` PRISMATIC joint (axis -Z, travel 0..ram_travel).
The rod is captured through the fixed cylinder + gland ring (element-scoped
`allow_overlap`, Rule 2 captured-pin exception). Only the platen face
prototype changes.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `square_platen` | forked_anchor (origin) | `rec_industrial__hydraulic_press__001` | L126-L139 | eligible | `square_platen_face` Box (0.23x0.23x0.035) tooling face. **Planar Boundary Form** (square plan) |
| `round_platen` | forked_anchor | `rec_hydraulic_press_var_round_platen` | L130, L318-L329 | eligible | `round_platen_disc` `Cylinder` (r=0.120) tooling face replaces the square plate. **Volumetric Envelope Form** (round disc) |

样本池仅提供两种压头孔径形态 (方板/圆盘); 该 slot 降到 2 candidate 已用尽 5 星池
的 tooling 形态词汇 (SPEC_TEMPLATE 硬约束: 池不足可降到 2 并说明理由), 两者都是
source-backed 且构成真实 ③ 形态原型差异, 非换尺寸/涂装。

### Slot C: bed (② bed joint / ①)

The work-support bed / bolster. Same bed part tree (`bed_block` + hazard-striped
front + `replaceable_bed_plate` + seam). Only the joint to the frame changes.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fixed_bed` | forked_anchor (origin) | `rec_industrial__hydraulic_press__001` | L112-L124 | eligible | `frame_to_bed` **FIXED** on the frame ledge (MatingContract, bed_block bottom on ledge top). Bed static; the non-fixed DOF is carried by the always-present ram. |
| `height_adjustable_bed` | forked_anchor | `rec_hydraulic_press_var_pin_adjustable_bed` | L124-L141, L341-L414 | eligible | ②: `frame_to_bed` **PRISMATIC** axis +Z, `[-bed_lower, +bed_raise]`; bed rides up/down the columns for daylight adjustment. |
| `sliding_bolster_bed` | forked_anchor | `rec_hydraulic_press_var_sliding_bolster_bed` | L67-L75, L133-L149 | eligible | ②/①: `frame_to_bed` **PRISMATIC** axis -Y, `[0, bolster_travel]`; adds `*_bolster_rail` visuals on the frame + `*_slide_shoe` on the bed; the bolster rolls out toward the operator for loading. |

### Slot D: control (① control skeleton + ② control joint + multiplicity `button_count`)

A detached floor-standing control console (`control_pedestal` part: cabinet +
control head + sloped panel + gauge + indicator lights + hose fittings + feet,
all fused visuals, Rule 1) FIXED to the frame via a floor `control_conduit`
(the FIXED origin lands on the conduit end = real frame geometry AND on the
console base, satisfying FIXED origin-honesty on both sides; the conduit also
provides geometric connectivity for the otherwise-detached console and reads as
the hydraulic-line floor raceway). Two flexible hydraulic hoses (spline tubes)
route from the console fittings up to the frame's single-sourced ports
(element-scoped `allow_overlap` at the ports). Only the operator interface
changes.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `push_buttons` | forked_anchor (origin, button_count) | `rec_industrial__hydraulic_press__001` L194-L221; `rec_hydraulic_press_var_button_count` L43, L194-L230 | L194-L221 | eligible | N separate button parts (cap + stem), each on a `pedestal_to_button_i` **PRISMATIC** joint (axis +Y, tiny 0..0.008 travel). `button_count` multiplicity. |
| `operating_lever` | forked_anchor | `rec_hydraulic_press_var_lever_valve_control` | L194-L245 | eligible | ①/②: one `operating_lever` part (collar + shaft + grip ball) on a `pedestal_to_lever` **REVOLUTE** joint (axis X, +-lever_range) captured over a `lever_pivot_boss` on the panel; no push buttons. |

硬约束满足: Slot A=4, Slot C=3 (>=3); Slot B=2, Slot D=2 (降到 2 已说明理由 - 池内
tooling 形态与操作机构各仅 2 种 source-backed 原型)。每个 candidate 有
`forked_anchor` + `model.py:Lx-Ly`; 无 `world_knowledge_extrapolation` candidate。

## 槽位图（slot graph）

pattern: `mixed` (root + 3 parallel children + 2 multiplicity)

```
frame (root; h_frame / h_frame_tubular / c_frame / four_post)
   |-[axis Z at cyl_axis_z; PRISMATIC descent; rod captured in cylinder+gland]-> ram   (square_platen / round_platen)
   |-[bed ledge at bed_contact_z; FIXED (mating) | PRISMATIC +Z | PRISMATIC -Y]-> bed   (fixed / height_adjustable / sliding_bolster)
   \-[floor control_conduit + FIXED at conduit end; hoses to frame ports]-> control     (push_buttons xN | operating_lever)
```

- **slot 顺序 / parent**: `frame` is the root and the only re-used parent. `ram`,
  `bed`, `control` each parent their own joint directly to `frame` (parallel
  children). All three declare only a `downstream` interface (re-export frame) and
  NO `upstream` -> the assembler emits no automatic chain joint; each module emits
  its own raw joint to the frame (same idiom as `Urban_Environment_Tipping_Barrow`).
- **接口点位**: ram -> cylinder axis `(0, 0, cyl_axis_z)`. bed -> bed ledge contact
  plane `(0, 0, bed_contact_z)`. control -> `control_conduit` end at
  `(pedestal_x, 0, conduit_top_z)`; hoses seat on frame ports `port_upper`,
  `port_lower`. buttons/lever parent to the `control_pedestal`.
- **跨 slot joint type/axis/range**: ram PRISMATIC axis (0,0,-1), `[0, ram_travel]`;
  bed FIXED | PRISMATIC(+Z, `[-bed_lower, bed_raise]`) | PRISMATIC(-Y, `[0, bolster_travel]`);
  control-pedestal FIXED; buttons PRISMATIC(+Y, `[0,0.008]`); lever REVOLUTE(X, `[-lever_range, lever_range]`).
- **互斥/派生**: `button_count` only for `push_buttons` (`operating_lever` -> n/a);
  `bed_raise`/`bed_lower` only for `height_adjustable_bed`; `bolster_travel` only for
  `sliding_bolster_bed`; `lever_range` only for `operating_lever`. `ram_travel` is
  clamped by the rest-daylight inequality (see below), tightened further when the
  bed is height-adjustable. Frame form is orthogonal to ram/bed/control (shared
  datums), any combination legal.

## 每槽位 Module Emits / Interfaces

### Slot A / module h_frame | h_frame_tubular | c_frame | four_post
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame` (single root part) | origin L44 |
| visuals | columns/spine/posts + crosshead/cantilever + sill/base + feet/flares + wear plates + bed ledge(s) + `cylinder_flange` + `fixed_cylinder` (LatheGeometry hollow tube) + `gland_ring` (LatheGeometry) + `upper/lower_hose_port` (+brackets) + `*_bed_pin_i` (multiplicity) + `control_conduit` + seams/bolts/`warning_label_i`/`logo` (decoration) | origin L52-L110; c_frame L52-L112; four_post L52-L90; tubular L52-L54 |
| internal joints | none (root, static body) | - |
| downstream interface | `frame` part, `cylinder_flange` visual, face `positive_z`, anchor `(0,0,bed_contact_z)` (informational; children wire manually) | - |

### Slot B / module square_platen | round_platen
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ram` | origin L126 |
| visuals | `ram_rod` (polished Cylinder) + `ram_collared_head` + `press_platen` + (`square_platen_face` Box \| `round_platen_disc` Cylinder) | origin L127-L130; round L130 |
| internal joints | `frame_to_ram` PRISMATIC axis (0,0,-1) `[0, ram_travel]` | origin L131-L139 |
| upstream interface | **none declared** (parallel child; parents joint directly to `frame`) | - |
| downstream interface | re-export frame (passthrough) | - |

### Slot C / module fixed_bed | height_adjustable_bed | sliding_bolster_bed
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bed` | origin L112 |
| visuals | `bed_block` + `hazard_yellow` + `hazard_black_i` (stripes) + `replaceable_bed_plate` + `front_bed_seam`; sliding adds `*_slide_shoe` (bed) + `*_bolster_rail` (frame) | origin L113-L123; sliding L67-L75,L133-L142 |
| internal joints | `frame_to_bed` FIXED(mating) \| PRISMATIC(+Z) \| PRISMATIC(-Y) | origin L124; pin L124-L132; sliding L133-L149 |
| upstream interface | **none declared** (parallel child) | - |
| downstream interface | re-export frame (passthrough) | - |

### Slot D / module push_buttons | operating_lever
| emits | 描述 | 来源 |
|---|---|---|
| parts | `control_pedestal` + (`button_i` xN \| `operating_lever`) | origin L141,L200; lever L~215 |
| visuals | pedestal: `cabinet_body`+`control_head`+`sloped_panel`+`gauge_*`+`indicator_light_i`+`*_hose_fitting`+`pedestal_foot_i`+`upper/lower_hose` (spline tubes); button: `button_cap`+`button_stem`; lever: `lever_pivot_boss`(pedestal)+`lever_collar`+`lever_shaft`+`lever_grip` | origin L141-L212; lever diff |
| internal joints | `frame_to_pedestal` FIXED (at conduit end); `pedestal_to_button_i` PRISMATIC(+Y) \| `pedestal_to_lever` REVOLUTE(X) | origin L186-L221; lever diff |
| upstream interface | **none declared** (parallel child) | - |
| downstream interface | re-export frame (passthrough) | - |

活动件语义: ram PRISMATIC 压下; bed 升降/滑出 (可动 bed 型); button 按压; lever
旋转开阀。不动细节 (seams/bolts/labels/gauge/lights/feet/gussets/hoses) 写成宿主
part visual (Rule 1)。captured 过盈 (rod-in-cylinder, button stem-through-panel,
lever collar-over-boss, hose-over-port, slide shoe-on-rail) 用 element-scoped
`allow_overlap` (Rule 2 例外); FIXED bed 用 MatingContract; FIXED pedestal 原点落在
`control_conduit` 端 (frame 真实几何) + pedestal 基座 (origin honesty 两侧)。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `frame_form` | enum | h_frame / h_frame_tubular / c_frame / four_post | h_frame | choice | procedural sampler | Slot A |
| `platen_module` | enum | square_platen / round_platen | square_platen | choice | procedural sampler | Slot B |
| `bed_module` | enum | fixed_bed / height_adjustable_bed / sliding_bolster_bed | fixed_bed | choice | procedural sampler | Slot C |
| `control_module` | enum | push_buttons / operating_lever | push_buttons | choice | procedural sampler | Slot D |
| `bed_pin_count` | int | {2,3,5} per column (obs: 2 c_frame, 3 origin, 5 bed_pin_count) | 3 | independent | weighted sample; frame decoration | origin L108, c_frame L107, bed_pin L107 |
| `button_count` | int | {3,4,5} (obs: 3 origin, 5 button_count; 4 interp) | 3 | conditional | only for `push_buttons`; `operating_lever` -> n/a | origin L194, button_count L221 |
| `frame_height_scale` | float | [0.90, 1.15] | 1.0 | independent | uniform, clamp; scales all vertical datums together | origin L53-L57 |
| `frame_width_scale` | float | [0.90, 1.15] | 1.0 | independent | uniform, clamp; column spacing + crosshead/bed width | origin L53-L55 |
| `platen_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform, clamp; platen radius / plate size | origin L129-L130 |
| `ram_travel` | float | [0.10, 0.16] | 0.16 | inequality | `ram_travel <= daylight_rest - 0.045`; if height_adjustable also `- bed_raise` | origin L138 |
| `bed_raise` | float | [0.05, 0.09] | 0.08 | conditional | height_adjustable_bed up-range; else n/a | pin L131 |
| `bed_lower` | float | [0.03, 0.05] | 0.045 | conditional | height_adjustable_bed down-range; else n/a | pin L131 |
| `bolster_travel` | float | [0.14, 0.22] | 0.20 | conditional | sliding_bolster_bed travel; else n/a | sliding L148 |
| `lever_range` | float | [0.40, 0.60] | 0.55 | conditional | operating_lever revolute +-range; else n/a | lever diff |
| (-) | constraint | - | - | inequality | `daylight_rest = ram_rest_platen_z - bed_top_rest_z` computed from scaled datums; ram/bed travels clamped so no sampled (ram-down, bed-up) pose closes the platen-bed gap below 0.04 m | origin geometry |

所有 equation/inequality/conditional 在 `resolve_config` 内求解; builder 不失败。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: <= 15 s** (hang-guard `--compile-timeout 60`).
Geometry is mostly `Box`/`Cylinder` primitives. The only meshes are: 2 revolved
LatheGeometry hollow tubes (`fixed_cylinder` <=48 seg, `gland_ring` <=32 seg,
built ONCE per frame) and 2 `tube_from_spline_points` hydraulic hoses (<=16
radial). Round columns/posts/platen are SDK `Cylinder`. No cadquery, no boolean
sculpting. Expect 4-9 s/seed; downgrade lathe/tube seg counts first if over.

## Multiplicity / Copy Logic

**两根独立 multiplicity 轴** (各自加权采样、各自编入 `slot_choices`、各自 clamp、
sweep 各自设上限):

### 轴 1 - `bed_pin_count` (每列可调压床定位销数)
- `count_param`: `bed_pin_count`; `N_range` product `[2,5]`, test `{2,3,5}`;
  sampling domain 加权 `{2:0.2, 3:0.5, 5:0.3}` (小 N 偏多).
- copied object: `left_bed_pin_i` / `right_bed_pin_i` small dark cylinders on the
  column front faces (H-frame / four_post); c_frame uses centered `bed_pin_i`.
- naming: `{side}_bed_pin_{i}`; placement: uniform z pitch from `bed_pin_z0`.
  joint policy: none - pure frame surface decoration (④), fused as `frame.visual`.
- source/gating: origin (3) L108, c_frame (2) L107, bed_pin_count (5) L107-L112.
  Present for every frame form.

### 轴 2 - `button_count` (控制台按钮数)
- `count_param`: `button_count`; `N_range` `[3,5]`, test `{3,4,5}`; sampling domain
  加权 `{3:0.5, 4:0.2, 5:0.3}`.
- copied object: `button_i` part (cap + stem) + its `pedestal_to_button_i`
  PRISMATIC joint; uniform x spacing along the sloped panel; colors cycle
  green/red/amber/blue/white.
- naming: `button_{i}` / `pedestal_to_button_{i}`. joint policy: one PRISMATIC per
  button (axis +Y, 0..0.008).
- source/gating: origin (3) L194, button_count (5) L194-L230. Only for
  `push_buttons` (`operating_lever` -> n/a, writes `buttons_na`).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | frame skeleton: two-column portal (origin) / four-post guide frame (four_post, +2 parts-worth of guide posts) / single-spine C-frame (c_frame); control skeleton: N push-button parts (origin/button_count) vs one lever part (lever_valve_control, part/joint 计数变). 全部 forked_anchor. |
| └ multiplicity | 同构件 xN | 有 | 见 §8: `bed_pin_count` {2,3,5} (c_frame/origin/bed_pin_count), `button_count` {3,4,5} (origin/button_count). |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | bed joint FIXED (origin) <-> PRISMATIC +Z (pin_adjustable_bed) <-> PRISMATIC -Y (sliding_bolster_bed); control joint PRISMATIC +Y buttons (origin) <-> REVOLUTE X lever (lever_valve_control). 全部 forked_anchor; 每种在 sweep 出现. |
| ③ 主体形态家族 | 图&关节不变，换核心 part 形态原型 | 有 | **两处登记进 slot_choices**: (A) frame column form - rectangular box columns (origin, Volumetric Envelope) / round tubular columns (tubular_columns, Volumetric Envelope) / open C-frame construction (c_frame, Macro Surface Construction) / four slender posts (four_post, Volumetric Envelope). (B) ram platen form - square plate (origin, Planar Boundary Form) / round disc (round_platen, Volumetric Envelope Form). |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | frame: bolted seams, foot/crosshead `*_bolt_i`, `warning_label_i`+mark, `top_logo_plate`, inner wear plates, gussets; bed: hazard yellow/black stripe band; pedestal: gauge face+needle, indicator lights. `bed_pin_count` is the decoration-count axis (see §8). All host `frame.visual`/`bed.visual`/`pedestal.visual`, positions derived from the realized (scaled) faces. source_type=record_only (origin/variants). |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale: frame_height_scale[0.90,1.15], frame_width_scale[0.90,1.15], platen_scale[0.85,1.15]. 关节运动包络 (每个非-continuous joint): ram PRISMATIC axis -Z, opens downward, `[0, ram_travel<=0.16]`; height_adjustable bed PRISMATIC axis +Z, `[-bed_lower, +bed_raise]`; sliding bolster PRISMATIC axis -Y, `[0, bolster_travel<=0.22]`; button PRISMATIC axis +Y `[0,0.008]`; lever REVOLUTE axis X `[-lever_range, +lever_range]`. `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)`; targeted `ctx.pose` - ram descends >=0.13 without closing bed gap below 0.04; adjustable bed rises visibly and still clears ram; sliding bolster moves >=0.15 in -Y; lever grip swings; one button depresses. No continuous joints -> no full-circle sampling. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted/metal; >=6 colorway: `warm_gray_press` (origin), `machine_blue`, `safety_orange`, `hammertone_green`, `graphite_dark`, `bare_steel`. Button/label/indicator colors stay semantic (green/red/amber start-stop-reset, safety yellow). 材质大类覆盖 >= ceil(0.5x6)=3. |

**收尾自检**: 0-9 seed 渲染须肉眼见到 4 种 frame (box/tubular/C/four-post)、方/圆
两种 platen、fixed/升降/滑出三种 bed、按钮组与操作杆、材质配色多样, ram 下压与
可动 bed 全程不穿模。

## 采样与覆盖审计

总组合数 (distinct slot-choice tuple 上界):
- frame 4 x platen 2 x bed 3 x control(push_buttons x button_count 3 = 3, +
  operating_lever 1 = 4) x bed_pin_count 3 = **4 x 2 x 3 x 4 x 3 = 288**.

理由: 288 < 富类别建议 300, 因为真实结构词汇在此收敛 - 所有样本共享同一
「frame + 固定油缸 + 垂直 ram + bed + 控制台」cell, 可动轴为 ram (恒定) + bed 关节 +
控制机构 + 两根小 multiplicity。不硬凑组合空间 (质量红线: 不反推上游变体数量)。
report-only, 不设 gate。

seed_domain_policy: `procedural_first`.

Procedural Sampling / Sweep Plan: `config_from_seed(seed)` 用 `random.Random(seed)`
依次抽 frame_form、platen_module、bed_module、control_module, 再按 compatibility 抽
bed_pin_count / button_count (control 为 push_buttons 时)、palette、连续 scale。
seed 0 pinned 到 origin 母本组合 (h_frame + square_platen + fixed_bed +
push_buttons x3, warm_gray_press) 作为 documented regression anchor (sparse
override, 其余 seed 全 procedural)。random sweep `0-15` (fast) -> `0-35` (final) -> corner。

Topology target: 1000-seed slot-choice tuple 覆盖用于成熟度观察; 真实上界 288
(见上), 低于 300 因结构词汇收敛, 已记录。report-only。

Controlled local parameterization: `frame_height_scale`、`frame_width_scale`、
`platen_scale`、`ram_travel`、`bed_raise`/`bed_lower` (conditional)、`bolster_travel`
(conditional)、`lever_range` (conditional)。全部在 `resolve_config` clamp / 求解;
不破坏 mount 数据面、captured 过盈接口、joint 原点、multiplicity。连续尺寸契约:
先采 independent (height/width/platen scale) -> 计算 daylight_rest -> 用 inequality
把 ram_travel (+height_adjustable 时减 bed_raise) 投影回可行域 -> conditional 解析
bed_raise/bolster_travel/lever_range。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 frame->platen->bed->control, 加权 choice; multiplicity 各自加权 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | button_count only push_buttons; bed_raise/bolster/lever conditional per module; ram_travel clamped by daylight; frame x ram x bed x control 正交自由组合 | 无 floating / collision / 轴错误 / max-N / bulky / 可选子件失败 |
| controlled local variation | 3 独立 scale + 4 conditional 行程 | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本 (documented anchor); 无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 >=2 | 是否 >=3 | 备注 |
|---|---:|---|---|---|
| frame | 4 | yes | yes | box/tubular/C/four-post |
| ram | 2 | yes | no | 池内 tooling 形态仅方板/圆盘两种 source-backed |
| bed | 3 | yes | yes | fixed/height-adjustable/sliding-bolster |
| control | 2 | yes | no | 池内操作机构仅按钮/操作杆两种 source-backed |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ bed_pin_count/button_count axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented 母本 override only)
- compatibility gating prevents illegal combos (button_count only push_buttons; conditional ranges per module) in `resolve_config`
- controlled local scales clamped; ram/bed travels solved against `daylight_rest`; cannot close the platen-bed gap below 0.04 m in any sampled pose
- cross-part scale dependencies (vertical datums, daylight) derived in `resolve_config`
- captured overlaps are element-scoped `allow_overlap` (rod-in-cylinder, button stem-in-panel, lever collar-on-boss, hose-on-port, shoe-on-rail); FIXED bed uses a MatingContract; FIXED pedestal origin sits on the control_conduit end + pedestal base
- key joints have expected type/axis/range: ram PRISMATIC(-Z); bed FIXED | PRISMATIC(+Z) | PRISMATIC(-Y); buttons PRISMATIC(+Y); lever REVOLUTE(X)
- copied `*_bed_pin_i` / `button_i` follow naming + placement policy
- `run_industrial_hydraulic_press_tests` calls `fail_if_parts_overlap_in_sampled_poses` + >=1 targeted `ctx.pose` per mechanism (ram, moving bed, control)

## Reject cases

- Ram descends far enough to drive the platen into (through) the bed at max travel -> clamp `ram_travel` by the rest-daylight inequality.
- Height-adjustable bed raised while the ram is down closes the gap and interpenetrates -> tighten `ram_travel` by `bed_raise` (both extremes must still clear 0.04 m); never mask a real platen-into-bed 穿模 with `allow_overlap`.
- Detached control pedestal FIXED with the joint origin in mid-air (far from both frame and console) -> route the FIXED origin through the `control_conduit` end so it sits on real frame geometry AND the console base.
- Frame form swap leaves the hydraulic cylinder / hose ports / bed ledge floating off the new structure -> single-source `cyl_axis_z` / `bed_contact_z` / port world positions and have every frame candidate emit ledge + ports + cylinder there.
- Bed pins / warning labels drawn at a constant offset that floats off round columns or the C-spine -> derive their front-face offset from the realized column form (Rule 4).
- Sliding bolster whose slide shoes float above the bolster rails -> seat the shoes on the rails with element-scoped `allow_overlap`.
- Downgrading the hollow `fixed_cylinder` / `gland_ring` revolved shell to a solid `Cylinder`, or the round platen/columns to a Box (Rule 3 violation).

## 与相邻类别的边界

- 不该混入: **Industrial / Drill press table** (旋转主轴 + 工作台的钻床, 是 CONTINUOUS 旋转主轴不是垂直线性压下的 ram)。
- 不该混入: **Industrial / Ore crusher jaw** (肘板驱动的破碎颚, 摆动颚板而非垂直 ram + 固定油缸)。
- 不该混入: **Industrial / Industrial vice** (水平螺杆夹钳, 无 frame 横梁/油缸/垂直 ram)。
- 不该混入: 纯 C-clamp / arbor press (手动杠杆丝杠, 无液压缸 + 控制台身份特征)。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Slot B (ram tooling) 与 Slot D (control) 各降到 2 candidate: 5 星池内 tooling 形态仅方板/圆盘、操作机构仅按钮/操作杆两种 source-backed 原型, 已按 SPEC_TEMPLATE 硬约束说明理由。`control_conduit` 为使脱离式控制台成为合法连通子装配 + FIXED 原点两侧落地而引入的地面线槽 (真实液压/电缆走线), 非结构性 crude 占位, 待人工确认忠实度。 |

## 模板实现备注（可选）

- 竖向 datums (`crosshead_z`/`cyl_axis_z`/`bed_contact_z`/`sill_z`) 与 `daylight_rest`
  single-sourced in `ResolvedConfig` (Contract 3c); ram/bed/control 挂点与行程全部
  从中派生, frame 形态正交。
- 固定油缸 shell + gland 用 LatheGeometry 旋转空心管 (built once, shared);
  hoses 用 `tube_from_spline_points`。所有 K 个 bed_pin / button 复用同一几何。
- captured 过盈全部 element-scoped `allow_overlap`; FIXED bed 用 MatingContract;
  FIXED pedestal 走 `control_conduit` + `mount_fixed` 单源锚定。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`: frame root 声明
  downstream; ram/bed/control 只声明 downstream (re-export frame) -> 无自动 chain
  joint, 各模块发原始 joint 到 frame (parallel-children, 同 Tipping_Barrow 惯用)。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D | h_frame + square_platen + fixed_bed + push_buttons | `rec_industrial__hydraulic_press__001` (origin 母本) | L29-L428 | frame part tree + fixed cylinder/gland/ports, ram + PRISMATIC descent, FIXED bed + hazard bed, detached pedestal + hoses + PRISMATIC buttons, 全部 test 语义 |
| S2 | A ③/① | c_frame | `rec_hydraulic_press_var_c_frame` | L52-L112 | 单脊 C-frame 悬臂结构 |
| S3 | A ③/① | four_post | `rec_hydraulic_press_var_four_post_frame` | L52-L90 | 四立柱导向框架 |
| S4 | A ③ | h_frame_tubular | `rec_hydraulic_press_var_tubular_columns` | L52-L54, L99-L101 | 圆管立柱 (Cylinder) + 桥接托架 |
| S5 | B ③ | round_platen | `rec_hydraulic_press_var_round_platen` | L130, L318-L329 | 圆盘压头 |
| S6 | C ② | height_adjustable_bed | `rec_hydraulic_press_var_pin_adjustable_bed` | L124-L141, L341-L414 | 垂直 PRISMATIC 升降床 |
| S7 | C ②/① | sliding_bolster_bed | `rec_hydraulic_press_var_sliding_bolster_bed` | L67-L75, L133-L149 | 水平 PRISMATIC 滑出床 + 导轨/滑靴 |
| S8 | D ①/② | operating_lever | `rec_hydraulic_press_var_lever_valve_control` | L194-L245 | REVOLUTE 操作杆 + 枢轴凸台 |
| S9 | D mult | button_count=5 | `rec_hydraulic_press_var_button_count` | L43, L194-L230 | button_count multiplicity 上界 + 统一 helper |
| S10 | A mult | bed_pin_count=5 | `rec_hydraulic_press_var_bed_pin_count` | L107-L112, L295-L308 | bed_pin_count multiplicity 上界 |
