# Modular Spec — Astronomy / Antenna dish

## 元信息
| 项 | 值 |
|---|---|
| slug | `Astronomy_Antenna_dish` |
| template path | `agent/templates/Astronomy_Antenna_dish.py` |
| test path (optional) | `tests/agent/test_Astronomy_Antenna_dish_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `linear_chain` (mount root -> azimuth turret -> elevation dish; plus within-dish ③/①/④ config sub-axes + 3 multiplicity axes) |
| function stem | `astronomy_antenna_dish` (exports `build_astronomy_antenna_dish`, `config_from_seed`, `run_astronomy_antenna_dish_tests`) |

`pattern = linear_chain`: a grounded `mount_base` root carries an `azimuth_turret`
(REVOLUTE about +Z) which carries the `dish_assembly` (elevation joint,
REVOLUTE about +Y or PRISMATIC along an inclined jack axis). Exactly 3 parts and
2 joints in every realization — this is a **form-dominated** category, so the
diversity lives in ③ Primary Form Family (mount body + reflector surface
construction), ② joint type (elevation), ①/③ feed-support construction, and ④
multiplicity, not in kinematic part count. All slot modules declare only a
`downstream` interface (re-export) and emit their own raw joints to the named
upstream part (Tipping_Barrow parallel-children idiom), so the
assembler emits no automatic chain joint.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 9 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 10 were read in full (origin full, 9 diffs vs origin) |

Samples (all `collections=["workbench"]`, `rating=5`):

- `rec_large-satellite-ground-station-antenna-white-par_20260708_082356_505435_4c5c4c05` — ORIGIN 母本 (conical pedestal building + azimuth turret w/ yoke + REVOLUTE elevation; solid paraboloid reflector, quad-strut prime-focus feed + subreflector + central horn, 8 radial backing ribs).
- `rec_antenna_dish_var_backing_rib_count` — multiplicity: `NUM_BACKING_RIBS` 8->12 radial ribs.
- `rec_antenna_dish_var_faceted_panel_reflector` — ③ Macro Surface: solid revolved shell -> flat trapezoidal gore panels in concentric rings (`MeshGeometry`).
- `rec_antenna_dish_var_feed_strut_count` — multiplicity: quad (4) prime-focus struts -> tripod (3) struts, uniform spacing.
- `rec_antenna_dish_var_louver_vent_count` — multiplicity: pedestal louver vents 3->4.
- `rec_antenna_dish_var_monopole_mast` — ③ mount form: conical pedestal building -> slender tubular steel monopole mast on a welded square base plate + gussets + top flange.
- `rec_antenna_dish_var_offset_feed_boom` — ① feed skeleton: prime-focus quad-strut + subreflector -> single curved cantilever offset boom from the rim carrying one feed horn at the focus (no subreflector).
- `rec_antenna_dish_var_open_truss_backing` — ③ Macro Surface (backing): radial rib chords -> open triangulated space-frame truss (spars + ring hoops + diagonal braces).
- `rec_antenna_dish_var_screwjack_elevation` — ② joint: elevation REVOLUTE trunnion -> PRISMATIC inclined screw-jack (cylinder on turret + extending ram on dish + slide rails).
- `rec_antenna_dish_var_tripod_mount` — ③/① mount form: conical pedestal -> 3 splayed tubular legs + hub + foot pads + gussets + cross-braces.

## 核心身份

A **ground-station / earth-terminal parabolic antenna dish**: a large concave
reflector aimed at the sky by an **azimuth-over-elevation (az-el) positioner**
planted on the earth. The whole object is the mount + positioner + reflector: a
grounded support body (conical pedestal building / tubular monopole mast /
splayed tripod), an **azimuth turret** that spins the head about the vertical,
and a **dish_assembly** that tilts in elevation between yoke cheeks (REVOLUTE
trunnion) or on a PRISMATIC screw-jack. The reflector carries its feed at the
prime focus on a strut spider (with a subreflector) or on an offset cantilever
boom, backed by radial ribs or an open truss. Default mature domain: 6-9 m class
reflector on a 5-6 m az-el mount, azimuth full-circle, elevation ~0-70 deg.

Not to be confused with the neighbouring picture subclass **Astronomy /
Satellite** — a free-flying spacecraft *bus* whose dishes are secondary deployed
appendages riding on solar-array-bearing appendages. Here the dish + earth mount
*is* the whole object; there is no bus, no solar wing, no MLI/radiator-tile
identity feature.

## 槽位 + 候选模块表

### Slot A：mount_base (root · ③ Primary Form Family + ①)

The grounded support body. One `mount_base` part in every candidate; only the
③ body envelope prototype (and the ① sub-member set for the tripod) changes. All
three expose the identical downstream contract: a level azimuth seat at derived
height `seat_z` with an azimuth REVOLUTE about +Z, so the turret + dish are
mount-form-independent (Contract 3c).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `conical_pedestal` | forked_anchor (origin) | `rec_large-...4c5c4c05` | L90-L177 | eligible | truncated-cone building (`LatheGeometry` cone) + top platform + blue access door + door surround + N louver vents + panel seam rings + side ladder (rails+rungs). **Volumetric Envelope Form** |
| `monopole_mast` | forked_anchor | `rec_antenna_dish_var_monopole_mast` | L38-L49, L96-L177 | eligible | square `Box` base plate + slender `CylinderGeometry` mast tube + top mounting flange + 4 radial gusset plates. **Volumetric Envelope Form** (slender vertical prism) |
| `tripod_mount` | forked_anchor | `rec_antenna_dish_var_tripod_mount` | L96-L211 | eligible | 3 splayed `CylinderGeometry` leg tubes + central hub + hub bearing plate + 3 foot pads + 3 junction gussets + 2 levels of cross-braces. **Macro Surface Construction** (open triangulated leg frame; adds ① sub-members) |

### Slot B：pointing (② elevation joint type · turret + elevation mechanism)

Builds the `azimuth_turret` part (drum + 2 yoke cheeks + 2 trunnion bearings +
elevation hardware) and the kinematic core of the `dish_assembly` part
(`backing_hub` + `trunnion_shaft`), and emits BOTH joints: `azimuth_drive`
REVOLUTE(+Z) parented to `mount_base`, and `elevation_drive` parented to the
turret. The captured azimuth seat and trunnion shaft are grandfathered raw
joints with element-scoped `allow_overlap` (Rule 2 captured-pivot exception,
exactly as every source declares).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `trunnion_revolute` | forked_anchor (origin) | `rec_large-...4c5c4c05` | L180-L216, L277-L285, L364-L372 | eligible | elevation `elevation_drive` **REVOLUTE** axis +Y between yoke cheeks; `elevation_drive_housing` box behind the yoke; trunnion shaft + backing hub. |
| `screwjack_prismatic` | forked_anchor | `rec_antenna_dish_var_screwjack_elevation` | L63-L78, L228-L265, L336-L350, L431-L438 | eligible | elevation `elevation_drive` **PRISMATIC** along inclined jack axis `(cos38.5,0,-sin38.5)`, travel [0, jack]; turret carries `screwjack_cylinder` + cross-bracket + 2 `elevation_bracket` slide rails, dish carries the extending `screwjack_ram` nested in the cylinder. |

Degrade-to-2 justification: the confirmed 5-star pool exposes exactly two
structurally distinct elevation mechanisms (bounded rotary trunnion; inclined
prismatic screw-jack). No third source-backed elevation topology exists; adding
one would violate Rule 3 (no invented joint candidate).

### Slot C：reflector (③ Primary Form Family — Macro Surface Construction · + ① feed + ③/④ backing)

The identity feature; adds all dish appearance to the existing `dish_assembly`
part: the reflector surface, rim stiffener, backing structure, counterweight,
and feed system. Two ③ reflector-surface candidates registered into
`slot_choices`; feed system (① skeleton) and backing (③/④) are source-backed
config sub-axes consumed inside the module (also reported into `slot_choices` for
coverage).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `solid_paraboloid` | forked_anchor (origin) | `rec_large-...4c5c4c05` | L233-L267 | eligible | smooth revolved thin-wall paraboloid shell (`LatheGeometry.from_shell_profiles`) + rim stiffening ring. **Macro Surface Construction** (continuous surface) |
| `faceted_panels` | forked_anchor | `rec_antenna_dish_var_faceted_panel_reflector` | L85-L156, L304-L317 | eligible | flat trapezoidal gore panels (`MeshGeometry`) in concentric contiguous rings following the paraboloid, + rim ring. **Macro Surface Construction** (faceted/paneled surface) |

Feed-system sub-axis (① skeleton, source-backed):
- `prime_focus_quad` (origin L319-L362): N converging feed struts + apex hub +
  subreflector dome + central feed horn tube + horn mouth. N = `feed_strut_count`.
- `offset_boom` (offset_feed_boom L305-L360): single curved cantilever boom
  (`tube_from_spline_points`) from the rim + mounting bracket + one offset feed
  horn tube + mouth at the focus; NO subreflector, NO central struts.

Backing sub-axis (③ Macro Surface / ④ decoration, source-backed):
- `radial_ribs` (origin L286-L310): N radial rib chords hugging the convex rear.
  N = `backing_rib_count`.
- `open_truss` (open_truss_backing L286-L356): triangulated space frame (radial
  spars + concentric ring hoops + diagonal braces) as tubular `CylinderGeometry`
  members.

硬约束满足：Slot A=3, Slot B=2 (justified), Slot C=2 candidates + 2 source-backed
sub-axes; every candidate/sub-axis has a `forked_anchor` + `model.py:Lx-Ly`. No
`world_knowledge_extrapolation` candidate is used (the pool supplies every form
directly). Every candidate is structurally distinct (different envelope /
surface construction / joint type / member set), not a re-skin.

## 槽位图（slot graph）

pattern: `linear_chain` (root -> turret -> dish; dish appearance added in place)

```
mount_base (root; conical_pedestal / monopole_mast / tripod_mount)
   --[azimuth_drive REVOLUTE +Z @ seat_z; drum seated on mount top (allow_overlap)]-->
azimuth_turret (drum + yoke cheeks + bearings + elevation hardware)
   --[elevation_drive REVOLUTE +Y (trunnion) | PRISMATIC jack-axis (screwjack) @ trunnion; shaft captured in bearings (allow_overlap)]-->
dish_assembly (reflector surface + rim + backing + feed + counterweight)
```

- **slot 顺序 / parent**：`mount_base` is the single root. `pointing` (Slot B)
  reads `mount_base` by name, creates `azimuth_turret` + `dish_assembly`, and
  emits both joints. `reflector` (Slot C) reads `dish_assembly` by name and adds
  its appearance visuals. All modules declare only `downstream` (re-export) →
  the assembler emits no auto chain joint; every joint is raw (parallel-children
  idiom).
- **接口点位**：azimuth seat = mount top center `(0,0,seat_z)`, axis +Z (drum
  symmetry centerline → origin-honesty passes). Elevation = trunnion axis
  `(0,0,seat_z+TRUNNION_Z)` in world; local `(0,0,TRUNNION_Z)` in turret frame;
  axis +Y (revolute) through the trunnion bearings/shaft, or jack-axis
  (prismatic, origin exempt).
- **跨 slot joint type/axis/range**：azimuth REVOLUTE(+Z, [-pi, pi]); elevation
  REVOLUTE(+Y, [0, elev_upper<=1.25], solver-clamped vs mount) or PRISMATIC(jack
  axis, [0, jack_travel<=2.6]).
- **互斥/派生**：`feed_strut_count` only for `prime_focus_quad`; `backing_rib_count`
  only for `radial_ribs`; `louver_vent_count` only for `conical_pedestal`.
  `screwjack_ram` dish visual only for `screwjack_prismatic`. Mount form is
  orthogonal to turret / dish (shared `seat_z` derivation).

## 每槽位 Module Emits / Interfaces

### Slot A / module conical_pedestal | monopole_mast | tripod_mount
| emits | 描述 | 来源 |
|---|---|---|
| parts | `mount_base` (root) | origin L90 |
| visuals | pedestal: `pedestal_cone_shell`+`top_platform`+`entrance_door`+`entrance_surround`+`louver_vent_i`+`panel_seam_ring_i`+`ladder_rail_*`+`ladder_rung_i`; mast: `base_plate`+`mast_tube`+`top_flange`+`gusset_i`; tripod: `leg_i`+`foot_pad_i`+`tripod_hub`+`hub_bearing_plate`+`gusset_i`+`cross_brace_l_i` | origin L98-L177; mast diff; tripod diff |
| internal joints | none (root) | — |
| downstream interface | `mount_base` re-export; `seat_z` carried in config | — |

### Slot B / module trunnion_revolute | screwjack_prismatic
| emits | 描述 | 来源 |
|---|---|---|
| parts | `azimuth_turret`, `dish_assembly` (kinematic core) | origin L180, L231 |
| visuals (turret) | `turntable_drum` + `yoke_cheek_{l,r}` + `trunnion_bearing_{l,r}` + (revolute) `elevation_drive_housing` OR (screwjack) `elev_cross_bracket`+`screwjack_cylinder`+`elevation_bracket_{l,r}` | origin L181-L216; screwjack L228-L265 |
| visuals (dish core) | `backing_hub` + `trunnion_shaft` + (screwjack) `screwjack_ram` | origin L269-L285; screwjack L336-L350 |
| internal joints | `azimuth_drive` REVOLUTE(+Z) mount->turret; `elevation_drive` REVOLUTE(+Y) or PRISMATIC(jack-axis) turret->dish | origin L218-L228, L364-L372; screwjack L431-L438 |
| downstream interface | `dish_assembly` re-export (passthrough) | — |

### Slot C / module solid_paraboloid | faceted_panels
| emits | 描述 | 来源 |
|---|---|---|
| parts | none new (adds visuals to `dish_assembly`) | — |
| visuals (reflector) | solid: `parabolic_reflector` shell + `rim_stiffener_ring`; faceted: `panel_ring_r_col_c` gore panels + `rim_stiffener_ring` | origin L233-L267; faceted L304-L317 |
| visuals (backing) | radial: `backing_rib_i` (xN); truss: `truss_member_i` (spars+rings+diagonals) | origin L286-L310; truss L286-L356 |
| visuals (feed) | prime_focus_quad: `feed_strut_i` (xN)+`apex_hub`+`subreflector`+`feed_horn_tube`+`feed_horn_mouth`; offset_boom: `feed_boom_arm`+`feed_boom_bracket`+`offset_feed_horn_tube`+`offset_feed_horn_mouth` | origin L319-L362; offset L305-L360 |
| visuals (other) | `counterweight_box` | origin L312-L317 |
| downstream interface | `dish_assembly` re-export (passthrough) | — |

活动件语义：azimuth 旋转整头；elevation 抬升/俯仰(revolute)或伸缩(prismatic)反射面。
不动细节(reflector shell / rim / ribs / truss / feed struts / subreflector / horn /
counterweight / mount cladding)全部写成宿主 part visual，非独立 part (Rule 1)。
captured azimuth seat + trunnion shaft 用 element-scoped allow_overlap (Rule 2 例外)。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `mount_form` | enum | conical_pedestal / monopole_mast / tripod_mount | conical_pedestal | choice | procedural sampler | Slot A |
| `elevation_module` | enum | trunnion_revolute / screwjack_prismatic | trunnion_revolute | choice | procedural sampler | Slot B |
| `reflector_form` | enum | solid_paraboloid / faceted_panels | solid_paraboloid | choice | procedural sampler | Slot C |
| `feed_system` | enum | prime_focus_quad / offset_boom | prime_focus_quad | choice | procedural sampler | Slot C sub-axis |
| `backing_style` | enum | radial_ribs / open_truss | radial_ribs | choice | procedural sampler | Slot C sub-axis |
| `backing_rib_count` | int | {6,8,10,12} (obs: 8 origin, 12 rib_count) | 8 | conditional | only for `radial_ribs`; else n/a | origin L296, rib_count L61 |
| `feed_strut_count` | int | {3,4} (obs: 4 origin, 3 strut_count) | 4 | conditional | only for `prime_focus_quad`; else n/a | origin L320, strut_count diff |
| `louver_vent_count` | int | {3,4,5} (obs: 3 origin, 4 louver_count) | 3 | conditional | only for `conical_pedestal`; else n/a | origin L130, louver_count diff |
| `mount_height_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform, clamp; scales `seat_z` (mount body height) | origin L40 |
| `dish_radius_scale` | float | [0.85, 1.12] | 1.0 | independent | uniform, clamp; reflector aperture radius + focal (equation) | origin L50 |
| `focal_len` | float | derived | — | equation | `= FOCAL_RATIO * dish_radius` (F/D locked, keeps paraboloid depth conformal) | origin L50-L51 |
| `elev_upper` | float | [0.90, 1.25] | 1.15 | independent | revolute elevation upper (rad); solver-clamped vs mount | origin L371 |
| `jack_travel` | float | [1.8, 2.6] | 2.4 | conditional | screwjack prismatic upper (m); else n/a | screwjack L70 |
| (—) | constraint | — | — | inequality | elevation revolute range solver-clamped by `clamp_joint_limits(keepout=[mount_base])` so the tilted/slewed dish never sweeps into the mount | clearance solver |

所有 equation/inequality/conditional 在 `resolve_config` 内求解；builder 不失败。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: <= 30 s** (hang-guard `--compile-timeout 90`). The two
heavy modules are `faceted_panels` (~4 contiguous rings, ~50-64 gore `MeshGeometry`
panels of 8 vertices each — cheap tessellation, but many small meshes) and
`open_truss` (~12 spars + 3x12 ring chords + diagonals, all thin
`CylinderGeometry` at `radial_segments=8`). Tessellation tiers: hero reflector
lathe <=64 seg; cone/mast/flange lathe <=48 seg; small members (bearings, struts,
truss, hub) 12-24 seg; feed boom tube 16-20 radial. All N repeated ribs/struts/
truss members reuse per-call small geometries; no boolean sculpting. Expect
8-20 s/seed; if over, drop faceted rings to 3 and truss diagonals first.

## Multiplicity / Copy Logic

**三根独立 multiplicity 轴**（各自加权采样、各自编入 `slot_choices`、各自 clamp、
sweep 各自设上限）：

### 轴 1 — `backing_rib_count`（反射面背部径向肋数）
- `count_param`: `backing_rib_count`; `N_range` product `[6,12]`, test `{6,8,10,12}`;
  sampling domain 加权 `{8: 0.4, 6: 0.2, 10: 0.2, 12: 0.2}`（标称 8 偏多）。
- copied object: `backing_rib_i` box chord hugging the convex rear, even angular
  spacing `ang = 2*pi*i/N`. naming `backing_rib_{i}`. joint policy: none (dish visuals).
- source/gating: origin (N=8) L296, rib_count (N=12) L61; only for
  `backing_style==radial_ribs` (else axis `ribs_na`).

### 轴 2 — `feed_strut_count`（棱镜焦点馈源支撑撑杆数）
- `count_param`: `feed_strut_count`; `N_range` `[3,4]`, test `{3,4}`; sampling
  domain 加权 `{4: 0.6, 3: 0.4}`。
- copied object: `feed_strut_i` cylinder from dish surface to apex hub, even
  spacing. naming `feed_strut_{i}`. joint policy: none (dish visuals).
- source/gating: origin (N=4) L320, strut_count (N=3); only for
  `feed_system==prime_focus_quad` (else axis `strut_na`).

### 轴 3 — `louver_vent_count`（锥形基座百叶通风板数）
- `count_param`: `louver_vent_count`; `N_range` `[3,5]`, test `{3,4,5}`; sampling
  domain 加权 `{3: 0.4, 4: 0.4, 5: 0.2}`。
- copied object: `louver_vent_i` dark box conformal to the sloped cone wall,
  even angular spacing over a safe front arc. naming `louver_vent_{i}`. joint
  policy: none (mount visuals).
- source/gating: origin (N=3) L130, louver_count (N=4); only for
  `mount_form==conical_pedestal` (else axis `louver_na`).

数量变化不改主体形态/机制（ribs 仍是 ribs, struts 仍会聚 apex, vents 仍贴壁）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 无（固定 3 part / 2 joint 运动学图） | 该地面站 az-el 天线运动学骨架恒为 mount->turret->dish（2 joint）。真正的"骨架级"差异（offset_boom vs prime-focus 馈源支撑, tripod 腿组）都不新增会动 part —— 全部熔进宿主刚体 part 的 visual (Rule 1)，故归 ③ Macro Surface Construction，不计 ①。source-backed: offset_feed_boom / tripod_mount。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：backing_rib_count {6,8,10,12}(origin/rib_count)、feed_strut_count {3,4}(origin/strut_count)、louver_vent_count {3,4,5}(origin/louver_count)。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | elevation joint：REVOLUTE(+Y, trunnion)（origin, forked_anchor）↔ PRISMATIC(jack-axis, screwjack)（screwjack_elevation, forked_anchor）。两种类型都在 sweep 出现。azimuth 恒 REVOLUTE(+Z)。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | **登记进 slot_choices 两处**：(A) mount 形态 slot — conical_pedestal(origin, Volumetric Envelope)/ monopole_mast(monopole_mast, Volumetric Envelope)/ tripod_mount(tripod_mount, Macro Surface Construction)。(C) reflector 表面构成 slot — solid_paraboloid(origin, Macro Surface: continuous)/ faceted_panels(faceted_panel_reflector, Macro Surface: faceted)。另加两 sub-axis：feed 支撑构成 prime_focus_quad↔offset_boom(offset_feed_boom, Macro Surface of feed frame)、backing 构成 radial_ribs↔open_truss(open_truss_backing, Macro Surface)。全部 forked_anchor。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | pedestal `panel_seam_ring`/`entrance_door`/`entrance_surround`/`ladder_rail`+`ladder_rung`；dish `rim_stiffener_ring`；mast `gusset`；tripod `gusset`/`cross_brace`。均为宿主 part visual，位置由宿主表面 (cone wall radius(z) / rim z / leg endpoints) 逐点派生，随 ③(mount 形态)/⑤(缩放) 共形。source_type=record_only (origin/mast/tripod)。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：mount_height_scale[0.85,1.15]、dish_radius_scale[0.85,1.12]（focal 由 F/D equation 派生）。关节运动包络：azimuth REVOLUTE +Z [-pi,pi]（整弧，双向）；elevation REVOLUTE +Y [0, elev_upper<=1.25]（solver-clamped vs mount，开启方向抬向 +X 地平）；elevation PRISMATIC jack-axis [0, jack_travel<=2.6]（伸出 +X/-Z）。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)`；targeted `ctx.pose` — azimuth 转 pi 镜像整头、revolute elevation 转 elev_upper 使 dish 质心前移+馈源下沉、prismatic 伸 jack_travel*0.8 使 ram/dish 沿轴前移。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted/metal（+ ceramic-white 反射面）；配色 >=5 colorway：`observatory_white`（白盘+灰包层+钢+蓝门）、`desert_tan`、`radio_gray`、`nato_green`、`red_white_bands`、`deep_space_charcoal`。材质大类覆盖 >= ceil(0.5×6)=3。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 pedestal/mast/tripod 三种 mount、solid/faceted
两种反射面、prime-focus vs offset-boom 两种馈源、revolute/prismatic 两种俯仰、
材质配色多样、azimuth/elevation 全程不穿模且 dish 不扫入 mount。

## 采样与覆盖审计

总组合数（distinct slot-choice tuple 上界）：
- mount 3 × elevation 2 × reflector 2 × feed 2 × backing 2 = **48** 离散拓扑；
  乘 multiplicity（rib 4 × strut 2 × louver 3，条件性）显著放大观测覆盖。

理由：48 离散拓扑 < 富类别建议 300，因为真实结构词汇在此收敛 —— 地面站 az-el 天线
恒为「mount + 方位转台 + 俯仰反射面」单 cell，可动轴仅 azimuth + elevation 两根，
其余多样性是宿主刚体的 ③/④ 形态与装饰。不硬凑组合空间（质量红线：不反推上游变体数量）。
report-only，不设 gate。

seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`
依次抽 mount_form、elevation_module、reflector_form、feed_system、backing_style、
palette，再按 compatibility 抽 backing_rib_count(radial_ribs 时)/ feed_strut_count
(prime_focus 时)/ louver_vent_count(pedestal 时)、连续 scale。seed 0 pinned 到
origin 母本组合（conical_pedestal + trunnion_revolute + solid_paraboloid +
prime_focus_quad(4) + radial_ribs(8) + louver(3), observatory_white）作为 documented
regression anchor（sparse override，其余 seed 全 procedural）。random sweep
`0-15`(fast)->`0-35`(final)->corner。

Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察；真实上界 48
离散拓扑（见上），低于 300 的原因为结构词汇收敛，已记录。report-only。

Controlled local parameterization：`mount_height_scale`(seat_z 派生)、
`dish_radius_scale`(focal 由 F/D equation 派生)、`elev_upper`、`jack_travel`
(conditional)。全部在 `resolve_config` clamp/派生；不破坏 captured-socket 接口、
azimuth/elevation 原点 honesty、multiplicity。连续尺寸契约：先采 independent
(mount_height/dish_radius/elev_upper)-> equation 派生 focal/seat_z-> conditional
解析 jack_travel/各 count。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 mount->elevation->reflector->feed->backing，加权 choice；multiplicity 各自加权 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | strut_count 仅 prime_focus；rib_count 仅 radial_ribs；louver_count 仅 pedestal；screwjack_ram 仅 screwjack；mount 与 head/dish 正交 | 无 floating / collision / 轴错误 / max-N / 可选子件失败 |
| controlled local variation | 4 个 clamp 连续 scale + solver-clamped elevation | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| mount_base | 3 | yes | yes | pedestal/mast/tripod |
| pointing (elevation) | 2 | yes | no | revolute/screwjack（池仅 2 种机制，已说明） |
| reflector | 2 | yes | no | solid/faceted（池仅 2 种表面构成，已说明） |
| feed_system (sub-axis) | 2 | yes | no | prime-focus/offset-boom |
| backing_style (sub-axis) | 2 | yes | no | ribs/truss |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ feed/backing/multiplicity axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented 母本 override only)
- compatibility gating prevents illegal combos (strut_count↔prime_focus; rib_count↔radial_ribs; louver_count↔pedestal; ram↔screwjack) in `resolve_config`
- controlled local scales clamped; cannot break captured-socket interfaces, azimuth/elevation origin honesty, or multiplicity
- cross-part scale dependencies (seat_z, focal_len) derived in `resolve_config`
- captured azimuth-seat / trunnion-shaft / screwjack ram overlaps are element-scoped `allow_overlap` (not broad part-level)
- key joints have expected type/axis/range: azimuth REVOLUTE(+Z); elevation REVOLUTE(+Y) or PRISMATIC(jack-axis)
- copied `backing_rib_i` / `feed_strut_i` / `louver_vent_i` follow naming + placement policy
- `run_astronomy_antenna_dish_tests` calls `fail_if_parts_overlap_in_sampled_poses` + >=1 targeted `ctx.pose` per mechanism (azimuth, elevation)

## Reject cases

- Tilted/slewed dish sweeps into the mount body (wide pedestal cone) → solver-clamp
  the elevation revolute range with `clamp_joint_limits(keepout=["mount_base"])`, never widen past feasibility.
- Faceted gore panels leave circumferential/radial gaps → disconnected geometry
  islands (FAIL in compile-sweep). Make ring radii contiguous and adjacent panels
  abut (zero/small negative angular gap) so the surface is one connected mesh.
- Screwjack ram at full extension drives the dish below ground / into the mount →
  cap `jack_travel`, keep the jack axis forward+down (+X/-Z), sampled-pose check.
- Louver vents / seam rings built at a constant radius float off the tapered cone
  wall → derive their radius from the cone `radius(z)` profile (Rule 4).
- Downgrading `LatheGeometry` reflector shell / `MeshGeometry` gore panels /
  `tube_from_spline_points` offset boom to crude Box/Cylinder (Rule 3 violation).
- Emitting the feed struts / subreflector / ribs / mount cladding as separate
  FIXED-joint parts instead of host `dish/mount` visuals (Rule 1 violation).

## 与相邻类别的边界

- 不该混入：**Astronomy / Satellite**（自由飞行 spacecraft bus + 太阳翼 + MLI/tile
  身份；dish 只是次级可动附件。本类别无 bus、无太阳翼、整体planted on ground）。
- 不该混入：**Astronomy / Space shuttle / Return capsule**（有翼/钝头再入体，非
  az-el 反射面拓扑）。
- 不该混入：纯装饰卫星天线小碟（无 az-el 地面positioner、无 pedestal/mast/tripod
  mount）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Slot B/C degrade to 2 candidates each — justified by the confirmed 5-star pool (exactly 2 elevation mechanisms; 2 reflector-surface constructions). Form-dominated category: ① kinematic skeleton is fixed (3 parts/2 joints); diversity carried by ③ mount + reflector Primary Form Family, ② elevation joint type, ①/③ feed construction, ④ multiplicity. All source-backed; no world_knowledge_extrapolation candidate. |

## 模板实现备注（可选）

- `seat_z` (mount top / azimuth seat height) 与 `focal_len` (F/D locked) single-sourced
  in `ResolvedConfig`（Contract 3c）；turret/dish 挂点全部从 `seat_z` 派生，mount 形态正交。
- captured azimuth seat + trunnion shaft + screwjack ram-in-cylinder → 原始 joint
  (no MatingContract, grandfathered) + element-scoped `allow_overlap`，与全部 5 星源一致（Rule 2 例外）。
- Slot B 创建 `azimuth_turret` + `dish_assembly` 两 part 并发两 joint；Slot C 只向
  已存在的 `dish_assembly` 追加 reflector/backing/feed appearance visuals（parallel
  visual authoring on one rigid part — Rule 1 熔合不动细节）。
- elevation revolute 转角用 `clamp_joint_limits(keepout=["mount_base"], allowed_pairs=captured)`
  求解，替代手调上限，跨 mount 形态自适应。prismatic travel 手 cap + sampled-pose 验证。
- faceted panels: 环半径连续 + 相邻 panel 抵接（保连通，防 island FAIL）。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`：每 slot 单候选（已 resolve），
  只声明 downstream → 无自动 chain joint，各模块发原始 joint（同 Tipping_Barrow）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | conical_pedestal + trunnion_revolute + solid_paraboloid + prime_focus_quad + radial_ribs | `rec_large-...4c5c4c05` (origin 母本) | L38-L469 | mount cone part tree, turret+yoke+REVOLUTE elevation, solid paraboloid + rim, quad prime-focus feed + subreflector + horn, radial ribs, counterweight, azimuth/elevation test semantics |
| S2 | C mult | backing_rib_count=12 | `rec_antenna_dish_var_backing_rib_count` | L61-L63, L296-L300 | rib multiplicity upper |
| S3 | C ③ | faceted_panels | `rec_antenna_dish_var_faceted_panel_reflector` | L85-L156, L304-L317 | faceted gore-panel reflector surface (MeshGeometry) |
| S4 | C mult | feed_strut_count=3 | `rec_antenna_dish_var_feed_strut_count` | L319-L322 | tripod feed-strut multiplicity |
| S5 | A mult | louver_vent_count=4 | `rec_antenna_dish_var_louver_vent_count` | L130-L134 | pedestal louver multiplicity |
| S6 | A ③ | monopole_mast | `rec_antenna_dish_var_monopole_mast` | L38-L49, L96-L177 | tubular mast + base plate + flange + gussets mount |
| S7 | C ① | offset_boom feed | `rec_antenna_dish_var_offset_feed_boom` | L305-L360 | offset cantilever feed boom + rim bracket + focal horn |
| S8 | C ③ | open_truss backing | `rec_antenna_dish_var_open_truss_backing` | L286-L356 | triangulated space-frame backing (spars+rings+diagonals) |
| S9 | B ② | screwjack_prismatic | `rec_antenna_dish_var_screwjack_elevation` | L63-L78, L228-L265, L336-L350, L431-L438 | PRISMATIC inclined screw-jack elevation (cylinder+rails+ram) |
| S10 | A ③/① | tripod_mount | `rec_antenna_dish_var_tripod_mount` | L96-L211 | splayed-leg tripod frame + hub + braces mount |
