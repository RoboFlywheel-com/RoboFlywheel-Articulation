# Modular Spec — Astronomy / Lunar rover

## 元信息
| 项 | 值 |
|---|---|
| slug | `Astronomy_Lunar_rover` |
| template path | `agent/templates/Astronomy_Lunar_rover.py` |
| test path (optional) | `tests/agent/test_Astronomy_Lunar_rover_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root chassis + parallel-children appendages + wheel/tool multiplicity + optional 2-hop steer/fold chains) |
| function stem | `astronomy_lunar_rover` (exports `build_astronomy_lunar_rover`, `build_seeded_astronomy_lunar_rover`, `config_from_seed`, `resolve_config`, `slot_choices_for_seed`, `run_astronomy_lunar_rover_tests`) |

`pattern = mixed`: a single root `chassis` part (open flat deck + all non-moving
deck furniture as fused visuals, Rule 1) carries several **parallel-children**
appendages — the running gear (N wheels, each on a CONTINUOUS roll joint; front
pair optionally on a REVOLUTE steer knuckle), the high-gain antenna (dish on a
REVOLUTE mount), the hand controller (REVOLUTE tilt or PRISMATIC throttle), and
the rear equipment rack (FIXED or REVOLUTE fold-down). One `chassis` candidate
splits the deck into `chassis`(forward) + `aft_deck` on a REVOLUTE tri-fold
hinge (a 2-hop chain for anything aft-mounted). Two multiplicity axes ride on
top: `wheel_count` (4/6) and `tool_handle_count` (3/4/5).

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 10 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 11 were read in full (origin full + 10 diffs vs origin) |

Samples (all `collections=["workbench"]`, `rating=5`, synced from `articraft_data`):

- `rec_apollo-lunar-roving-vehicle-lrv-as-seen-in-a-rea_20260708_115847_845699_410c71b1` — ORIGIN 母本 (rigid open flat-deck chassis, 4 SDK-tire wheels on CONTINUOUS Y spin, arch fenders, rear rack FIXED, umbrella HGA dish on REVOLUTE-Z azimuth swivel, hand controller REVOLUTE-Y tilt).
- `rec_lunar_rover_var_antenna_elevation` — ② joint: HGA mount REVOLUTE axis Z (azimuth) → axis Y (elevation), limits -0.7..1.0.
- `rec_lunar_rover_var_controller_throttle` — ② joint: hand controller REVOLUTE tilt (Y) → PRISMATIC throttle slide (X), limits -0.04..0.05.
- `rec_lunar_rover_var_dish_parabolic` — ③ form: HGA umbrella wire-mesh shell → solid deep parabolic bowl (`LatheGeometry(_parabolic_bowl_profile())`).
- `rec_lunar_rover_var_fender_flat_plate` — ③ form: fender arch (`ExtrudeGeometry` annular sector) → flat rectangular `Box` mudguard plate (Apollo-17 taped-map style).
- `rec_lunar_rover_var_fold_chassis` — ① skeleton: chassis split into `forward_deck` + `aft_deck` joined by a REVOLUTE tri-fold hinge (axis Y); rear wheel stations + seats + rack ride on `aft_deck`.
- `rec_lunar_rover_var_rack_folddown` — ② joint: rear rack FIXED → REVOLUTE fold-down hinge (axis Y, 0..pi/2).
- `rec_lunar_rover_var_steering_knuckle` — ①+② skeleton/joint: 2 `steering_knuckle_front_*` parts on REVOLUTE-Z steer joints; front wheels reparented knuckle→wheel (2-hop chain).
- `rec_lunar_rover_var_tire_solid` — ③ form: SDK `TireGeometry` chevron tire → smooth solid balloon tire (`LatheGeometry(_balloon_tire_profile())`, elliptical revolved section).
- `rec_lunar_rover_var_tool_handles_n` — multiplicity: rear tool pallet handles 3 → 5.
- `rec_lunar_rover_var_wheels_six` — ①+mult: 4 wheels → 6 (add `mid_left`/`mid_right` axle row at x=0), all CONTINUOUS Y spin.

## 核心身份

A **crewed lunar / planetary roving vehicle (Apollo-LRV class)**: an open
tubular/box **flat-deck chassis** rolling on **N wire-mesh or balloon wheels**
(each an always-on CONTINUOUS roll joint; the category-defining motion), with
**dust fenders** over the wheels, **two webbed astronaut seats**, a **center
control console**, blanketed **battery/LCRU boxes**, a **TV camera** and a
**low-gain antenna staff** (all fused deck furniture), plus the identity
appendages: a steerable/pointable **high-gain antenna dish** on a REVOLUTE mount
mast, a **hand controller** (T-handle tilt or throttle slide), and a **rear
equipment rack / tool pallet**. At least one non-fixed joint (the wheels' roll)
is always present; most builds add a steer / dish-point / controller / rack /
deck-fold DOF. Default mature domain: ~2.3 m wheelbase, 4 wheels, one HGA, one
rear rack.

Not to be confused with the neighbouring **Astronomy / Mars rover** (a boxy
warm-electronics-box rover body with a rocker-bogie suspension linkage, robotic
arm turret and mast camera — no open crew deck, no seats, no hand controller)
nor with **Astronomy / Antenna dish** (a ground-station parabolic dish on an
az-el pedestal; the LRV dish is a small secondary deck appendage, not the whole
object).

## 槽位 + 候选模块表

### Slot A：chassis (root · ① Skeleton family)

The root vehicle body. Emits the `chassis` part with the entire open flat deck
and every non-moving furniture item as fused named visuals (floor pan, side
rails, cross rails, per-wheel suspension arms + fenders, 2 seats+backrests,
center console, battery boxes, low-gain mast, TV camera — Rule 1). Both
candidates expose the same mounting datums (`DECK_TOP` face; wheel-station
positions from `r.wheel_positions`; the forward console top; the rear deck edge)
so downstream appendages are chassis-form-independent.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `rigid_deck` | forked_anchor (origin) | `rec_apollo-...410c71b1` | L102-L246 | eligible | single monolithic `chassis` part; one continuous flat deck. **Volumetric Envelope Form** (rigid frame) |
| `folding_deck` | forked_anchor | `rec_lunar_rover_var_fold_chassis` | L99-L149 (helper), L167-L307 (fwd/aft decks + `deck_fold_hinge`) | eligible | ① skeleton change: `chassis`(forward half) root + `aft_deck` child on a REVOLUTE tri-fold hinge (axis Y); rear wheels/seats/rack ride on `aft_deck` (2-hop for aft appendages). **Macro Surface Construction** (split-deck stowage break) |

### Slot B：running_gear (parallel children · ① skeleton + wheel `multiplicity` + ② steer joint)

The wheels (and optional front steering knuckles). Each wheel is a part on a
CONTINUOUS roll joint (axis Y); front wheels optionally sit on a REVOLUTE-Z
steer knuckle (a 2-hop `chassis→knuckle→wheel` chain). Wheel hub is a captured
axle-stub pivot → grandfathered joint + element-scoped `allow_overlap`.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `roll_four` | forked_anchor (origin) | `rec_apollo-...410c71b1` | L248-L301 | eligible | 4 wheels (front_l/r + rear_l/r), each CONTINUOUS Y spin, front axles fixed to chassis. `wheel_count`=4. |
| `roll_six` | forked_anchor | `rec_lunar_rover_var_wheels_six` | L57-L62, L505-L562 | eligible | 6 wheels — adds a mid-axle row (`mid_left`/`mid_right`) at x=0, all CONTINUOUS Y spin. `wheel_count`=6. |
| `steered_four` | forked_anchor | `rec_lunar_rover_var_steering_knuckle` | L64, L143-L150, L251-L292, L338-L358 | eligible | 4 wheels; 2 front `steering_knuckle_front_*` parts on REVOLUTE-Z steer joints, front wheels reparented knuckle→wheel CONTINUOUS. `wheel_count`=4. |

### Slot C：antenna (parallel child · ② mount joint; ③ dish form param)

The identity feature. Emits the `high_gain_antenna` part (mast + gimbal block +
dish + hub stub + feed rod + feed tip) on a REVOLUTE mount joint parented to the
chassis. Mast root is socketed into the deck → element-scoped `allow_overlap`.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `azimuth_dish` | forked_anchor (origin) | `rec_apollo-...410c71b1` | L368-L424 | eligible | HGA on REVOLUTE mount, **axis Z** (azimuth swivel), limits ±hga_az. |
| `elevation_dish` | forked_anchor | `rec_lunar_rover_var_antenna_elevation` | L422-L423 | eligible | ② joint axis change: identical part tree, REVOLUTE mount **axis Y** (elevation pitch), limits [-elev_lo, +elev_hi]. |

`dish_form` (③, threaded param on both candidates; registered as its own
slot_choices key): `umbrella` (`LatheGeometry.from_shell_profiles`, origin
L382-L389, Volumetric Envelope Form) / `parabolic` (solid deep bowl
`LatheGeometry(_parabolic_bowl_profile())`, dish_parabolic L91-L117 + L409-L411,
Volumetric Envelope Form). Both keep the same part tree / mount / feed — only
the reflecting-surface envelope prototype changes (Rule 3).

### Slot D：hand_controller (parallel child · ② joint type)

Emits the `hand_controller` part (stem + T-grip) on a joint parented to the
console top. Stem is a captured pivot/slide shaft in the console → element-scoped
`allow_overlap`.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `tilt_control` | forked_anchor (origin) | `rec_apollo-...410c71b1` | L427-L448 | eligible | REVOLUTE tilt, axis Y, limits ±ctrl_tilt (fore/aft driving tilt). |
| `throttle_control` | forked_anchor | `rec_lunar_rover_var_controller_throttle` | L442-L447 | eligible | ② joint type change: PRISMATIC throttle slide, axis X, limits [-0.04, +0.05] (fore/aft throttle travel). |

### Slot E：rear_rack (parallel child · ② joint type + `tool_handle_count` multiplicity)

Emits the `rear_equipment_rack` part (base rails, posts, top rail, tool pallet
plate, N tool handles, sample bag) at the rear deck edge. Base rails seat into
the deck pan → element-scoped `allow_overlap`.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fixed_rack` | forked_anchor (origin) | `rec_apollo-...410c71b1` | L304-L365 | eligible | rack FIXED to the deck (static equipment pallet). `tool_handle_count` multiplicity. |
| `folddown_rack` | forked_anchor | `rec_lunar_rover_var_rack_folddown` | L361-L366 | eligible | ② joint type change: rack on a REVOLUTE fold-down hinge, axis Y, limits [0, rack_fold_upper]. `tool_handle_count` multiplicity. |

硬约束满足：Slot A=2, B=3, C=2, D=2, E=2 candidate（B 达到 3；A/C/D/E 降到 2 —
本小类每个附件轴在 5 星池里恰好是 origin + 1 个 fork，无更多结构不同源，属
SPEC_TEMPLATE §4 "样本池不足时可降到 2 并说明理由"）。每个 candidate 均有
`forked_anchor` + `model.py:Lx-Ly`；无 `world_knowledge_extrapolation` skeleton/
joint candidate。③ 主体形态家族登记进 slot_choices 的三根：`dish_form`（umbrella/
parabolic）、`tire_form`（chevron/balloon）、`fender_form`（arch/flat_plate），
每根均 source-backed（origin + 对应 fork）。

## 槽位图（slot graph）

pattern: `mixed` (root chassis + parallel children + multiplicity + optional 2-hop chains)

```
chassis (root; rigid_deck | folding_deck[+aft_deck via deck_fold_hinge REVOLUTE Y])
   ├─[wheel station · CONTINUOUS(Y) roll; captured axle-stub | via REVOLUTE(Z) steer knuckle]→ running_gear (×N wheels, ±2 steer knuckles)
   ├─[console/deck face · REVOLUTE(Z|Y) mount; mast socketed]→ antenna     (high_gain_antenna, dish_form umbrella|parabolic)
   ├─[console top · REVOLUTE(Y) tilt | PRISMATIC(X) throttle; captured stem]→ hand_controller
   └─[rear deck edge · FIXED | REVOLUTE(Y) fold-down; rails seated]→ rear_rack (×M tool handles)
```

- **slot 顺序 / parent**：`chassis` 是 root（唯一被复用的 parent），随后
  running_gear / antenna / hand_controller / rear_rack 都直接把各自 joint 的
  `parent=chassis`（或 folding 时 aft appendages 的 `parent=aft_deck`），互不
  串联（parallel children）。所有非-root module 只声明 `downstream`（re-export
  chassis），不声明 `upstream`，因此 assembler 不发射自动 chain joint（各模块自己
  发原始 joint，与 5 星源一致，同 Tipping_Barrow 惯用）。
- **接口点位**：wheel 挂点 `(±half_wheelbase 或 0, ±half_track, AXLE_Z)`；steer
  knuckle pivot `(front_x, ±0.7375, AXLE_Z)` 轴 Z；HGA 挂点 `(1.05, 0.35,
  DECK_TOP)`；controller 挂点 console top `(0.40, 0.0, 0.78)`；rack 挂点 rear
  edge `(-half_wheelbase-0.16, 0.0, DECK_TOP)`；folding 时 aft 挂点在 `aft_deck`
  局部帧（世界 z 减 DECK_TOP）。
- **跨 slot joint type/axis/range**：wheel roll CONTINUOUS(Y)；steer REVOLUTE(Z,
  ±steer_range)；HGA REVOLUTE(Z, ±hga_az) 或 REVOLUTE(Y, elev)；controller
  REVOLUTE(Y, ±ctrl_tilt) 或 PRISMATIC(X, [-0.04,0.05])；rack FIXED 或 REVOLUTE(Y,
  [0, rack_fold_upper])；deck fold REVOLUTE(Y, [0, fold_upper]).
- **互斥/派生（compatibility）**：`folding_deck` × `roll_six` 禁止（mid 轴排恰落在
  折叠铰线 x=0 上，物理不成立）→ folding 时 gear 仅取 {roll_four, steered_four}。
  其余 chassis × gear × antenna × controller × rack × forms 正交自由组合。

## 每槽位 Module Emits / Interfaces

### Slot A / module rigid_deck | folding_deck
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chassis` (root); folding 追加 `aft_deck` | origin L102; fold L167,L266 |
| visuals | `floor_pan`(+`_aft`) + `side_rail_*` + `cross_rail_*` + per-wheel `suspension_arm_*`/`fender_*`/(`axle_*` non-steered) + `seat_pan_*`/`seat_back_*`/`seat_leg_*` + `console_body`/`console_panel` + `battery_box_*` + `lowgain_mast`/`lowgain_head` + `camera_post`/`camera_body`/`camera_lens` | origin L105-L246 |
| internal joints | none (rigid); `deck_fold_hinge` REVOLUTE axis Y (folding) | fold L296-L307 |
| downstream interface | `chassis` part, `floor_pan` visual, face `positive_z`, anchor `(0,0,DECK_TOP)` (informational; children wire manually) | — |

### Slot B / module roll_four | roll_six | steered_four
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel_{station}` ×N; steered adds `steering_knuckle_front_{l,r}` | origin L279; steer L255 |
| visuals | per-wheel `tire`(SDK chevron mesh \| balloon lathe) + `wheel_disc`; knuckle `knuckle_pivot`+`knuckle_arm`+`axle_front_*` | origin L281-L292; steer L258-L281 |
| internal joints | `chassis_to_wheel_{s}` / `knuckle_to_wheel_{s}` CONTINUOUS(Y); `chassis_to_steer_{s}` REVOLUTE(Z) | origin L293-L301; steer L282-L358 |
| upstream interface | **none declared** (parallel children; parents joints to `chassis`/`aft_deck`) | — |
| downstream interface | re-export chassis downstream (passthrough) | — |

### Slot C / module azimuth_dish | elevation_dish
| emits | 描述 | 来源 |
|---|---|---|
| parts | `high_gain_antenna` | origin L368 |
| visuals | `hga_mast` + `hga_gimbal` + `hga_dish`(umbrella lathe \| parabolic bowl lathe) + `hga_hub_stub` + `hga_feed_rod` + `hga_feed_tip` | origin L369-L415; parabolic L409-L411 |
| internal joints | `chassis_to_high_gain_antenna` REVOLUTE axis Z (azimuth) \| axis Y (elevation) | origin L416-L424; elev L422-L423 |
| upstream interface | **none declared** | — |
| downstream interface | re-export chassis (passthrough) | — |

### Slot D / module tilt_control | throttle_control
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hand_controller` | origin L427 |
| visuals | `controller_stem` + `controller_grip` | origin L428-L439 |
| internal joints | `chassis_to_hand_controller` REVOLUTE axis Y (tilt) \| PRISMATIC axis X (throttle) | origin L440-L448; throttle L442-L447 |
| upstream / downstream interface | none / passthrough chassis | — |

### Slot E / module fixed_rack | folddown_rack
| emits | 描述 | 来源 |
|---|---|---|
| parts | `rear_equipment_rack` | origin L304 |
| visuals | `rack_base_rail_*` + `rack_post_*` + `rack_pallet_stub_*` + `rack_top_rail` + `tool_pallet_plate` + `tool_handle_{i}` ×M + `sample_bag` | origin L306-L358 |
| internal joints | `chassis_to_rear_rack` FIXED \| REVOLUTE axis Y (fold-down) | origin L359-L365; folddown L361-L366 |
| upstream / downstream interface | none / passthrough chassis | — |

活动件语义：wheel roll 使车行驶；steer 转向前轮；HGA mount 指向天线；controller
tilt/throttle 驾驶输入；rack fold-down 装卸；deck fold 收纳。不动细节（座椅/控制台/
电池/相机/低增益杆/fender/suspension）写成宿主 part visual，非独立 part（Rule 1）。
captured axle/knuckle/mast/stem/rail socket 用 element-scoped `allow_overlap`
（Rule 2 例外）；所有 REVOLUTE 原点落在真实 face/hardware 几何（origin honesty）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `chassis_module` | enum | rigid_deck / folding_deck | rigid_deck | choice | procedural sampler | Slot A |
| `gear_module` | enum | roll_four / roll_six / steered_four | roll_four | conditional | folding→{roll_four,steered_four} only | Slot B |
| `antenna_module` | enum | azimuth_dish / elevation_dish | azimuth_dish | choice | procedural sampler | Slot C |
| `controller_module` | enum | tilt_control / throttle_control | tilt_control | choice | procedural sampler | Slot D |
| `rack_module` | enum | fixed_rack / folddown_rack | fixed_rack | choice | procedural sampler | Slot E |
| `dish_form` | enum | umbrella / parabolic | umbrella | choice | procedural sampler | dish_parabolic |
| `tire_form` | enum | chevron / balloon | chevron | choice | procedural sampler | tire_solid |
| `fender_form` | enum | arch / flat_plate | arch | choice | procedural sampler | fender_flat_plate |
| `wheel_count` | int | {4,6} (obs: 4 origin, 6 wheels_six) | 4 | conditional | 6 only for `roll_six`; steered/folding→4 | wheels_six L57-L62 |
| `tool_handle_count` | int | {3,4,5} (obs: 3 origin, 5 tool_handles_n) | 3 | independent | weighted {3:0.5,4:0.2,5:0.3}; placed uniformly along rack Y | origin L345, handles L345 |
| `deck_len_scale` | float | [0.90, 1.15] | 1.0 | independent | uniform, clamp; scales half_wheelbase + deck length (wheel X, fender X co-derive) | origin L48 |
| `track_scale` | float | [0.90, 1.15] | 1.0 | independent | uniform, clamp; scales half_track + deck width + side-rail Y (wheel Y, fender Y co-derive) | origin L49 |
| `dish_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform, clamp; HGA dish footprint | origin L382-L389 |
| `half_wheelbase` | float | derived | — | equation | `= 1.145·deck_len_scale` | origin L48 |
| `half_track` | float | derived | — | equation | `= 0.915·track_scale` | origin L49 |
| `steer_range` | float | [0.05, 0.08] | 0.07 | conditional | steered_four only; REVOLUTE steer ±range. Clearance-capped small (Rule 5): the deck is as wide as the track, so a wider yaw sweeps the wide tire through the fixed fender/deck edge. The ② steer JOINT (REVOLUTE-Z) is the structural feature; magnitude is clearance-limited | steer L291 |
| `hga_az` | float | [1.8, 2.8] | 2.6 | conditional | azimuth_dish only; REVOLUTE ±range (Z) | origin L423 |
| `elev_hi` | float | [0.0, 1.0] | 1.0 | conditional | elevation_dish only; REVOLUTE (Y) limits [0, 1.0]. lower=0 (Rule 5): the dish rests at DISH_TILT=-0.5 leaning back; a further-back elevation lays it flat over the deck/crew, so the actuator only pitches up toward zenith | antenna_elevation L423 |
| `ctrl_tilt` | float | [0.25, 0.40] | 0.35 | conditional | tilt_control only; REVOLUTE ±range (Y) | origin L447 |
| `fold_upper` | float | [1.2, 1.6] | 1.5 | conditional | folding_deck only; REVOLUTE fold upper (rad), capped so aft deck stands clear of forward deck (never folds onto it) | fold L307 |
| `rack_fold_upper` | float | [1.3, 1.6] | 1.5708 | conditional | folddown_rack only; REVOLUTE fold-down upper (rad) | folddown L366 |
| (—) | constraint | — | — | inequality | `wheel_count==4` unless `gear_module==roll_six`; `folding_deck ⇒ gear ∈ {roll_four,steered_four}` (mid axle can't sit on the fold hinge) | wheels_six / fold_chassis |

所有 equation/inequality/conditional 在 `resolve_config` 内求解；builder 不失败。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: ≤ 20 s** (hang-guard `--compile-timeout 60`).
Geometry dominated by shared meshes: ONE `tire_mesh` (SDK TireGeometry chevron,
~24 tread blocks, OR balloon `LatheGeometry` 48 seg) + ONE `disc_mesh`
(WheelGeometry, 8 spokes) reused across all N wheels; ONE `fender_mesh`
(ExtrudeGeometry annular ~28 seg, arch form only) reused across all stations;
ONE `dish_mesh` (LatheGeometry ≤48 seg). No boolean sculpting. Tessellation
tiers: dish/balloon lathe ≤48 seg (hero), fender arch 28 seg, small cylinders
default. Expect 5-12 s/seed; downgrade seg counts first if over.

## Multiplicity / Copy Logic

**两根独立 multiplicity 轴**（各自加权采样、各自编入 `slot_choices`、各自 clamp、
sweep 各自设上限）：

### 轴 1 — `wheel_count`（车轮数）
- `count_param`: `wheel_count`; `N_range` product/test `{4,6}`; sampling domain：
  只有 `roll_six` module 给 6，其余 4；`roll_six` 采样权重 0.30（大 N 稀有）。
- copied object: `wheel_{station}` 整个轮（tire + disc + CONTINUOUS Y spin joint）。
  4 轮 = front_l/r + rear_l/r；6 轮追加 mid_l/r（x=0 轴排）。
- naming: `wheel_{front,mid,rear}_{left,right}` / `chassis_to_wheel_{station}`。
  placement: 沿 X 的 1-3 个规则轴排，每排 ±half_track。joint policy: 每轮独立
  CONTINUOUS Y roll（steered 前轮经 knuckle）。
- source/gating: origin (N=4) L57-L61, wheels_six (N=6) L57-L62。`roll_six` 与
  `folding_deck` 互斥（见 §4 compatibility）。数量变化不改主体形态/机制。

### 轴 2 — `tool_handle_count`（后架工具手柄数）
- `count_param`: `tool_handle_count`; `N_range`/test `{3,4,5}`; sampling domain
  加权 `{3:0.5,4:0.2,5:0.3}`（小 N 偏多）。
- copied object: `tool_handle_{i}` Cylinder，沿 rack Y 均匀排布于 tool pallet。
- naming: `tool_handle_{i}`。placement: `ty = linspace(-span, span, N)`。joint
  policy: 无关节（宿主 rack part visual，随 rack fold-down 一起动）。
- source/gating: origin (N=3) L345, tool_handles_n (N=5) L345。所有 rack module
  都带该轴（fixed / folddown 皆可）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 结构 candidate：rigid vs folding deck（origin / fold_chassis，追加 `aft_deck` part + REVOLUTE fold 边）；running_gear roll_four / roll_six（+2 wheel part）/ steered_four（+2 knuckle part + REVOLUTE steer 边，前轮改挂 knuckle）。全部 forked_anchor。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：wheel_count {4,6}（origin/wheels_six），tool_handle_count {3,4,5}（origin/tool_handles_n）。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | HGA mount REVOLUTE 轴 Z（origin）↔ 轴 Y（antenna_elevation）；controller REVOLUTE tilt-Y（origin）↔ PRISMATIC throttle-X（controller_throttle）；rack FIXED（origin）↔ REVOLUTE fold-down（rack_folddown）；steer REVOLUTE-Z（steering_knuckle）。全部 forked_anchor；每种在 sweep 出现。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | **三处登记进 slot_choices**：(C) `dish_form` — umbrella wire-mesh shell（origin, Volumetric Envelope）/ solid parabolic bowl（dish_parabolic, Volumetric Envelope）；(B) `tire_form` — SDK chevron tire（origin）/ smooth balloon lathe tire（tire_solid）（Volumetric Envelope）；(chassis) `fender_form` — annular arch（origin, Macro Surface）/ flat rectangular plate（fender_flat_plate, Planar Boundary Form）。全部 source-backed。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | chevron tread pattern、wheel-disc spokes、console panel、seat webbing、MLI-tan battery blankets、`sample_bag`、tool handles — 均为宿主 part visual，随 ③（fender/tire 形态）/⑤（deck/track 缩放，wheel-station 位置）派生位置。source_type=record_only（origin/tire_solid/tool_handles_n）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：deck_len_scale[0.90,1.15]（half_wheelbase 派生）、track_scale[0.90,1.15]（half_track 派生）、dish_scale[0.85,1.15]。关节运动包络（每个非-continuous joint）：steer REVOLUTE axis Z，双向，[闭合 0, ±steer_range≤0.70]；HGA azimuth REVOLUTE Z 双向 ±hga_az≤2.8，或 elevation REVOLUTE Y [-0.7, 1.0]；controller REVOLUTE Y ±ctrl_tilt≤0.40 或 PRISMATIC X [-0.04, 0.05]；rack fold-down REVOLUTE Y [0, ≤1.6]；deck fold REVOLUTE Y [0, ≤1.6]（capped 使 aft deck 立起不压 forward deck）。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)`；continuous wheel 采 {0,±90°,180°}；targeted `ctx.pose` — 车轮 spin、steer 转前轮出侧向、HGA mount 位移 dish、controller tilt/slide 位移 grip、rack fold 降 pallet、deck fold 抬 aft deck。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal/painted；配色 ≥5 colorway：`apollo_lrv`（铝框 + 银网轮 + 暗胎 + 金褐 fender/座椅）、`bare_alloy`、`dust_tan`、`charcoal_service`、`white_thermal`、`gunmetal`。材质大类覆盖 ≥ ceil(0.5×6)=3。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 rigid/folding 两种底盘、4/6 轮、有/无转向节、
umbrella/parabolic 两种碟、chevron/balloon 两种胎、arch/flat 两种挡泥板、tilt/throttle
控制、fixed/folddown 后架、多配色，且 fold/steer/gimbal/rack 全程不穿模。

## 采样与覆盖审计

总组合数（distinct slot-choice tuple 上界，含 form 轴，不含连续 scale）：
- chassis 2 × gear(rigid 下 3，folding 下 2) × antenna 2 × controller 2 × rack 2
  × dish_form 2 × tire_form 2 × fender_form 2 × tool 3 ≈
  rigid: `1×3×2×2×2×2×2×2×3 = 576`；folding: `1×2×2×2×2×2×2×2×3 = 384`（roll_six 排除）
  → **≈ 960 distinct topology tuples**（>300 富类别阈值）。

理由：本类别附件轴多（5 slots + 3 form + 2 mult），组合空间宽；每根轴 source-backed，
不硬凑。report-only，不设 gate。

seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`
先抽 chassis_module，按 compatibility 抽 gear_module（folding 时限 4 轮集），再抽
antenna/controller/rack module、dish/tire/fender form、tool_handle_count、palette、
连续 scale + 关节行程。seed 0 pinned 到 origin 母本组合（rigid_deck + roll_four +
azimuth_dish + tilt_control + fixed_rack + umbrella + chevron + arch + 3 handles,
apollo_lrv）作为 documented regression anchor（sparse override，其余 seed 全
procedural）。random sweep `0-15`（fast）→ `0-35`（final）→ corner。

Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察；真实上界 ≈960
（见上）。report-only。

Controlled local parameterization：`deck_len_scale`（half_wheelbase 派生）、
`track_scale`（half_track 派生）、`dish_scale`、joint 行程（steer/hga/ctrl/fold/
rack_fold）。全部在 `resolve_config` clamp / 派生 / 按 conditional 解析；不破坏
captured-socket 接口、joint 原点、multiplicity。连续尺寸契约：先采 independent
（deck_len/track/dish scale + 各行程）→ equation 派生 half_wheelbase/half_track →
conditional 解析行程（仅当对应 module 选中）+ wheel_count/gear gating。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 chassis→gear→antenna→controller→rack + form + mult，加权 choice | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | folding_deck→gear∈{roll_four,steered_four}；roll_six→wheel_count=6 else 4；正交其余 | 无 floating / collision / 轴错误 / max-N / bulky / 可选子件失败 |
| controlled local variation | 3 个 clamp scale + 6 个 clamp joint 行程 | 比例/行程变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| chassis | 2 | yes | no | rigid/folding（池内唯一 2 结构源） |
| running_gear | 3 | yes | yes | roll_four/roll_six/steered_four |
| antenna | 2 | yes | no | azimuth/elevation（+dish_form ③） |
| hand_controller | 2 | yes | no | tilt/throttle |
| rear_rack | 2 | yes | no | fixed/folddown（+tool mult） |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ dish/tire/fender form + wheel_count/tool_handle_count axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented 母本 override only)
- compatibility gating prevents illegal combos (folding→no roll_six; roll_six⇒6 wheels else 4) in `resolve_config`
- controlled local scales/ranges clamped; cannot break captured-socket interfaces, joint origin honesty, or multiplicity
- cross-part scale dependencies (half_wheelbase/half_track; wheel-station positions shared by chassis fenders + running_gear wheels) derived in `resolve_config`
- captured axle/knuckle/mast/stem/rail overlaps are element-scoped `allow_overlap` (not broad part-level)
- key joints have expected type/axis/range: wheel CONTINUOUS(Y); steer REVOLUTE(Z); HGA REVOLUTE(Z|Y); controller REVOLUTE(Y)|PRISMATIC(X); rack FIXED|REVOLUTE(Y); deck fold REVOLUTE(Y)
- copied `wheel_{station}` / `tool_handle_i` follow naming + placement policy
- `run_astronomy_lunar_rover_tests` calls `fail_if_parts_overlap_in_sampled_poses` + ≥1 targeted `ctx.pose` per mechanism

## Reject cases

- Deck fold upper too large → aft deck folds onto forward deck/console (parts interpenetrate) → cap `fold_upper` ≤1.6 so the aft section only stands up; never `allow_overlap` a true deck-on-deck collision.
- Steer range too wide → front wheel swings into the fender / side rail at ±range → clamp `steer_range`; knuckle pivot nested in suspension arm is the ONLY allowed steer overlap.
- HGA dish steered into the deck / camera at azimuth or elevation extremes → keep the mast tall so the dish clears the deck; clamp ranges.
- Fender form swap leaves the flat plate floating above the wheel with no strut → keep the fender post/stay under both forms (host-derived support).
- `roll_six` mid wheels detached (no fender/suspension station) → chassis emits a fender+suspension station per wheel position, mid included.
- Downgrading `hga_dish` / balloon tire `LatheGeometry` or fender arch `ExtrudeGeometry` to crude Box/Cylinder (Rule 3 violation).
- Rear rack parented to `chassis`(forward) under folding_deck → joint origin far from geometry; aft appendages MUST parent to `aft_deck`.

## 与相邻类别的边界

- 不该混入：**Astronomy / Mars rover**（暖电子箱 + rocker-bogie 悬挂连杆 + 机械臂
  turret + mast 相机的自主探测车；无敞开乘员甲板、无座椅、无手柄控制器）。
- 不该混入：**Astronomy / Antenna dish**（地面站 az-el 抛物面天线整体对象；LRV 的
  HGA 只是甲板上的次级小附件）。
- 不该混入：普通 **Urban / 手推车 / 拖车**（无月面轮网胎、无 HGA、无座椅+控制台
  乘员甲板身份特征）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Slot A/C/D/E 降到 2 candidate（每附件轴 5 星池只有 origin + 1 fork）；③ 主体形态多样性由 dish_form/tire_form/fender_form 三根 form 轴承载并登记进 slot_choices。folding_deck×roll_six 设计期物理 gate（mid 轴落折叠铰线）。 |

## 模板实现备注（可选）

- half_wheelbase/half_track single-sourced in `ResolvedConfig`（Contract 3c）；
  `wheel_positions`（含 front/mid/rear + 挂点 part）由其派生，chassis fenders 与
  running_gear wheels 共读，保 fender 对齐轮位。
- captured axle/knuckle/mast/stem/rail socket → 原始 joint（no MatingContract,
  grandfathered）+ element-scoped `allow_overlap`（Rule 2 例外）。
- 所有 N 个轮共享一个 `tire_mesh` / `disc_mesh`；所有 arch fender 共享一个
  `fender_mesh`；dish 单一 mesh —— 保编译预算。
- folding_deck：`aft_deck` 局部帧原点 = 世界 `(0,0,DECK_TOP)`，aft 视觉 z 减
  DECK_TOP；rear wheels / rack / seats 挂到 `aft_deck`（`r.aft_part_name`）。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`：chassis root
  声明 downstream；其余 slot 只声明 downstream（re-export chassis）→ 无自动 chain
  joint，各模块发原始 joint（parallel-children，同 Tipping_Barrow 惯用）。
- fold / rack fold 优先手写 REVOLUTE + capped upper + targeted pose test；若
  sampled-pose 穿模再切 `clamp_joint_limits`。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D/E | rigid_deck + roll_four + azimuth_dish + tilt_control + fixed_rack + umbrella + chevron + arch | `rec_apollo-...410c71b1` (origin 母本) | L44-L612 | chassis 全 furniture, 轮 part tree + CONTINUOUS spin, HGA + REVOLUTE azimuth, controller REVOLUTE tilt, rack FIXED, umbrella dish + chevron tire + arch fender, 全部 test 语义 |
| S2 | C ② | elevation_dish | `rec_lunar_rover_var_antenna_elevation` | L422-L423 | HGA REVOLUTE 轴 Z→Y elevation |
| S3 | D ② | throttle_control | `rec_lunar_rover_var_controller_throttle` | L442-L447 | controller REVOLUTE→PRISMATIC throttle |
| S4 | C ③ | parabolic dish_form | `rec_lunar_rover_var_dish_parabolic` | L91-L117, L409-L411 | solid parabolic bowl LatheGeometry |
| S5 | chassis ③ | flat_plate fender_form | `rec_lunar_rover_var_fender_flat_plate` | L52-L56, L130-L138 | flat Box mudguard plate |
| S6 | A ① | folding_deck | `rec_lunar_rover_var_fold_chassis` | L99-L149, L167-L307 | 分体甲板 + REVOLUTE tri-fold hinge |
| S7 | E ② | folddown_rack | `rec_lunar_rover_var_rack_folddown` | L361-L366 | rack FIXED→REVOLUTE fold-down |
| S8 | B ①/② | steered_four | `rec_lunar_rover_var_steering_knuckle` | L64, L251-L292, L338-L358 | steering knuckle REVOLUTE-Z + 前轮 2-hop |
| S9 | B ③ | balloon tire_form | `rec_lunar_rover_var_tire_solid` | L85-L103, L264-L290 | balloon LatheGeometry tire |
| S10 | E mult | tool_handle_count=5 | `rec_lunar_rover_var_tool_handles_n` | L345 | tool handle multiplicity 上界 |
| S11 | B mult | roll_six | `rec_lunar_rover_var_wheels_six` | L57-L62, L505-L562 | 6 轮 mid 轴排 |
