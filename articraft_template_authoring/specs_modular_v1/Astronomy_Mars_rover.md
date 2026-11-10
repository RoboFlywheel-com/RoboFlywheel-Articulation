# Modular Spec — Astronomy / Mars rover

## 元信息
| 项 | 值 |
|---|---|
| slug | `Astronomy_Mars_rover` |
| template path | `agent/templates/Astronomy_Mars_rover.py` |
| test path (optional) | `tests/agent/test_Astronomy_Mars_rover_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (one root `body` chassis; mobility / camera-mast / robotic-arm / high-gain-antenna slots all parent their joints directly to the body) |
| function stem | `astronomy_mars_rover` (exports `build_astronomy_mars_rover`, `build_seeded_astronomy_mars_rover`, `config_from_seed`, `resolve_config`, `slot_choices_for_seed`, `run_astronomy_mars_rover_tests`) |

`pattern = parallel_children`: a single root `body` (boxy chassis + equipment/solar
deck) carries four parallel-children subsystems, each of which manually parents its
own articulations to the `body` (no serial chain joint, no auto assembler joint):
mobility (rocker-bogie suspension + 6 wheels), camera mast (pan/tilt), robotic arm,
and steerable high-gain antenna dish. The `body`'s own ③ deck form is itself a
registered slot (equipment deck vs solar-array wings). There is always at least one
non-fixed joint (the 6 wheel CONTINUOUS spins are always present).

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 8 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 9 were read in full (origin full, each variant diffed against origin) |

Samples (all `collections=["workbench"]`, `rating=5`, synced from `articraft_data`):

- `rec_a-perseverance-style-mars-exploration-rover-a-wh_20260708_120003_784686_6a5aa1bc` — ORIGIN 母本 (boxy chassis + equipment deck; fused rocker-bogie tubes; 6 CONTINUOUS wheels; rigid pan/tilt mast; single rigid arm w/ fused turret; az-only HGA dish).
- `rec_mars_rover_var_rocker_bogie_linkage` — ① skeleton: fused suspension → articulated rocker + bogie parts on REVOLUTE(Y) pivots; wheels re-parent to rocker/bogie.
- `rec_mars_rover_var_steering_knuckles` — ①/② : 4 corner wheels gain steering-knuckle parts on REVOLUTE(Z) steer joints; corner wheels re-parent to knuckles.
- `rec_mars_rover_var_spoked_wheel_hub` — ③ form: solid domed wheel disc → open spring-spoke lattice disc (`_build_lattice_wheel_disc`, Torus/Cylinder/tube merge).
- `rec_mars_rover_var_folding_mast` — ①/② : rigid mast → two-segment deployable mast (lower_mast yaw → upper_mast deploy REVOLUTE(Y) → head tilt).
- `rec_mars_rover_var_multi_joint_arm` — ① skeleton: single rigid arm → upper_arm + forearm, adding an elbow REVOLUTE(Y).
- `rec_mars_rover_var_turret_rotation` — ①/② : fused turret → separate `instrument_turret` part on a wrist_roll CONTINUOUS(X) joint.
- `rec_mars_rover_var_hga_elevation_gimbal` — ①/② : az-only dish → az-el 2-DOF gimbal (stem azimuth → elevation yoke REVOLUTE(Y) carrying the dish).
- `rec_mars_rover_var_solar_deck` — ③ form: equipment-box deck → flat MER-style solar-array wings + cell-grid overlay.

> **Confirmed-pool note (reviewer):** the task brief's `variant_ids` for this subclass
> are exactly the 8 variants above (no wheel-count / body-shape / tool-handle variant
> — those belong to the sibling *Lunar rover* pool). Wheel count is therefore fixed at
> the canonical **6** (see §8). All 9 records compile clean and are adopted.

## 核心身份

A **planetary (Mars) exploration rover**: a boxy white spacecraft-derived **chassis
body** carried on a **six-wheel rocker-bogie mobility system**, topped by an
**equipment / solar-array deck** and three deployable science subsystems — a **pan/tilt
camera mast**, a **multi-segment robotic arm** ending in an instrument/drill turret,
and a **steerable high-gain antenna dish**. The category-defining motion is the six
independently-driven wheels (always CONTINUOUS-spun); the science appendages add
REVOLUTE pan/tilt/deploy/gimbal DOFs. Default mature domain: ~2.2 m body, 6 cleated
wheels of ~0.26 m radius, mast head ~2.2 m above ground.

Not to be confused with the neighbouring picture subclass **Astronomy / Lunar rover**
(a crewed open-frame buggy: seats, hand-controller, dish antenna on a mast, 4 wheels,
no boxy sealed instrument chassis / robotic arm), nor **Astronomy / Antenna dish**
(a ground-station az-el dish that IS the whole object rather than a small deployed
rover appendage).

## 槽位 + 候选模块表

### Slot A：chassis (root · ③ Primary Form Family: deck)

The root rover body. Same part tree across candidates: one `body` part with a chassis
`Box` + front hazcam pods + rear UHF antenna + HGA gimbal pedestal + arm shoulder
bracket + a mast mounting boss (all fused as `body` visuals, Rule 1). Only the **deck
form** prototype changes; both expose the identical deck-top datum (`DECK_TOP`) and
suspension/appendage mount stations so downstream slots are form-independent.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `equipment_deck` | forked_anchor (origin) | `rec_a-perseverance-...6a5aa1bc` | L82-L158 | eligible | flat deck plate + tiled equipment/electronics/instrument boxes + vent grille. **Macro Surface Construction** (boxy avionics deck) |
| `solar_wing_deck` | forked_anchor | `rec_mars_rover_var_solar_deck` | L44-L55, L82-L175 | eligible | MER-style: center deck + 2 flat solar wings straddling ±Y + revolved-cell `_solar_grid_mesh` overlay + wing brackets. **Planar Boundary Form** (broad flat wing planform) |

### Slot B：mobility (parallel children on body · ① skeleton + ② joint + ③ wheel-hub form)

Six cleated wheels (always present, always CONTINUOUS spin axis Y) plus the rocker-bogie
running gear. The suspension linkage topology is the primary ① axis. The `wheel_hub_form`
③ sub-parameter (solid disc vs spring-spoke lattice) is orthogonal and applies inside
every candidate (shared `_wheel_disc_mesh` helper). Axle stubs are captured pins inside
each wheel hub → element-scoped `allow_overlap`, joint grandfathered (Rule 2 exception).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fused_rocker_bogie` | forked_anchor (origin) | `rec_a-perseverance-...6a5aa1bc` | L160-L333 | eligible | rocker/bogie legs + pivot hubs + knuckle posts + axle stubs all fused as `body` visuals (static); 6 wheels CONTINUOUS spin parented to `body`. |
| `articulated_rocker_bogie` | forked_anchor | `rec_mars_rover_var_rocker_bogie_linkage` | L171-L390, L440-L465 | eligible | ① : per-side `{side}_rocker` (REVOLUTE Y `{side}_rocker_pivot`, parent body) + `{side}_bogie` (REVOLUTE Y `{side}_bogie_pivot`, parent rocker); front wheel→rocker, mid/rear wheels→bogie. |
| `steered_corners` | forked_anchor | `rec_mars_rover_var_steering_knuckles` | L270-L395 | eligible | ①/② : fused legs on body + 4 corner `{row}_{side}_knuckle` parts on REVOLUTE(Z) `{row}_{side}_steer`; corner wheels→knuckle, middle wheels→body. |

`wheel_hub_form` ③ (shared across all B candidates): `solid_disc` (origin `WheelGeometry`
domed disc, L288-L296) / `spoked_lattice` (`rec_mars_rover_var_spoked_wheel_hub`
`_build_lattice_wheel_disc`, Torus+Cylinder+tube merge). form_subtype = Macro Surface
Construction (open lattice vs closed disc face).

### Slot C：camera_mast (parallel child on body deck · ① skeleton + ② joint)

Pan/tilt remote-sensing mast. Always a `mast` part on a `mast_yaw` REVOLUTE(Z) plus a
`mast_camera_head` on a `head_tilt` REVOLUTE(Y). Only the number of column segments (and
the deploy joint) changes. 2 candidates (the 5-star pool contains exactly these two
mast skeletons).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rigid_mast` | forked_anchor (origin) | `rec_a-perseverance-...6a5aa1bc` | L338-L414 | eligible | one `camera_mast` (yaw Z) → `mast_camera_head` (tilt Y). 2 parts. |
| `folding_mast` | forked_anchor | `rec_mars_rover_var_folding_mast` | L57-L67, L346-L456 | eligible | ①/② : `lower_mast` (yaw Z) → `upper_mast` (`mast_deploy` REVOLUTE Y hinge, 0..1.57) → `mast_camera_head` (tilt Y). 3 parts, interleaving hinge knuckles/lug. |

### Slot D：robotic_arm (parallel child on body front-right bracket · ① skeleton + ② joint)

Front deployable science arm. Always a shoulder `arm_shoulder_yaw` REVOLUTE(Z). The
distal chain / turret articulation is the axis.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rigid_arm` | forked_anchor (origin) | `rec_a-perseverance-...6a5aa1bc` | L419-L490 | eligible | single `robotic_arm` part (upper link + forearm + wrist + turret + drill + sensor all fused); shoulder yaw Z only. |
| `elbow_arm` | forked_anchor | `rec_mars_rover_var_multi_joint_arm` | L419-L515 | eligible | ① : `upper_arm` (shoulder yaw Z) → `forearm` (`arm_elbow_pitch` REVOLUTE Y, -1.4..0.5) carrying wrist + turret. |
| `turret_roll_arm` | forked_anchor | `rec_mars_rover_var_turret_rotation` | L419-L510 | eligible | ①/② : `robotic_arm` (shoulder yaw Z) → `instrument_turret` part on `wrist_roll` CONTINUOUS(X). |

### Slot E：high_gain_antenna (parallel child on deck pedestal · ① skeleton + ② joint)

Steerable comms dish. Always a `high_gain_antenna` stem on `hga_azimuth` REVOLUTE(Z).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `az_dish` | forked_anchor (origin) | `rec_a-perseverance-...6a5aa1bc` | L495-L532 | eligible | one `high_gain_antenna` part: gimbal stem + `LatheGeometry` dish + boss fused; azimuth Z only (1 DOF). |
| `azel_gimbal` | forked_anchor | `rec_mars_rover_var_hga_elevation_gimbal` | L495-L570 | eligible | ①/② : stem (azimuth Z) → `hga_elevation_yoke` (`hga_elevation` REVOLUTE Y, ±0.55) U-yoke carrying the dish. 2 DOF. |

硬约束满足：每个 slot 均有 source-backed candidate（A=2, B=3, C=2, D=3, E=2）；每个
candidate 有 `forked_anchor` + `model.py:Lx-Ly`。无 `world_knowledge_extrapolation`。
C/E 降到 2 个 candidate 的理由：本 5 星池对 mast / HGA 恰好各有 2 种结构骨架，无更多
source（SPEC_TEMPLATE §4 允许样本池不足时降到 2 并说明）。5 个 slot 全部是 body 的
parallel children、彼此无跨-slot mating seam（唯一共享 parent 是 body），因此 slot 数
虽多但装配风险低（AUTHORING §B parallel-children）。

## 槽位图（slot graph）

pattern: `parallel_children` (single root, all appendages parent to it)

```
chassis body (root; equipment_deck / solar_wing_deck)
   ├─[±Y running gear · wheel CONTINUOUS(Y) always; rocker/bogie REVOLUTE(Y) or steer REVOLUTE(Z) per module]→ mobility  (6 wheels + suspension)
   ├─[deck mast boss · mast_yaw REVOLUTE(Z), head_tilt REVOLUTE(Y), +deploy REVOLUTE(Y)]→ camera_mast
   ├─[front-right bracket · arm_shoulder_yaw REVOLUTE(Z) +elbow/ +wrist_roll]→ robotic_arm
   └─[deck pedestal · hga_azimuth REVOLUTE(Z) +elevation REVOLUTE(Y)]→ high_gain_antenna
```

- **slot 顺序 / parent**：`chassis` 是唯一 root。mobility / camera_mast / robotic_arm /
  high_gain_antenna 都只声明 `downstream` 接口（re-export body），不声明 `upstream`，故
  assembler 不发射自动 chain joint；每个 module 自行发原始 joint，`parent=body`（或
  articulated 时 parent=rocker/bogie，steered 时 parent=knuckle —— 都在同一 module 内建）。
- **接口点位**：wheels → `(WHEEL_ROW_X[row], ±WHEEL_TRACK_Y, wheel_radius)`；rocker pivot
  `(0.25, ±0.74, 0.95)`；bogie pivot `(-0.45, ±0.80, 0.60)`；steer `(row_x, ±0.72, wheel_radius)`；
  mast `MAST_BASE=(0.75,0.15,DECK_TOP)`；arm `ARM_SHOULDER=(1.32,-0.45,0.85)`；HGA
  `HGA_BASE=(0.10,0.45,DECK_TOP+0.10)`。
- **跨 slot joint type/axis/range**：wheel CONTINUOUS(Y)；rocker/bogie REVOLUTE(Y, ±0.20/±0.25)；
  steer REVOLUTE(Z, ±steer_range)；mast_yaw REVOLUTE(Z, ±2.8)；head_tilt REVOLUTE(Y, ±0.45)；
  mast_deploy REVOLUTE(Y, 0..mast_deploy_upper)；shoulder yaw REVOLUTE(Z, -0.35..0.50)；
  elbow REVOLUTE(Y, -1.4..0.5)；wrist_roll CONTINUOUS(X)；hga_azimuth REVOLUTE(Z, ±2.6)；
  hga_elevation REVOLUTE(Y, ±hga_elevation_range)。
- **互斥/派生**：所有 slot 与 body 的 deck 形态完全正交（挂点用共享常数 datum，与 deck 形态
  无关），可自由组合。无 slot 互斥。

## 每槽位 Module Emits / Interfaces

### Slot A / module equipment_deck | solar_wing_deck
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` (single root part) | origin L81 |
| visuals | `chassis_box` + deck (`deck_plate`+equipment boxes+`deck_vent_grille` \| `solar_center_deck`+`solar_wing_{side}`+`solar_grid_{side}`+brackets) + `front_hazcam_*` + `uhf_antenna_pole/can` + `hga_pedestal` + `arm_shoulder_bracket` + `mast_mount_boss` | origin L82-L158; solar L119-L175 |
| internal joints | none (root) | — |
| downstream interface | `body`, `chassis_box`, `positive_z` deck datum | — |

### Slot B / module fused_rocker_bogie | articulated_rocker_bogie | steered_corners
| emits | 描述 | 来源 |
|---|---|---|
| parts | 6× `{row}_{side}_wheel`; articulated adds `{side}_rocker`+`{side}_bogie`; steered adds 4× `{row}_{side}_knuckle` | origin L304; rocker L194,L289; steer L278 |
| visuals | wheel: `tire`+`wheel_disc`(solid/lattice)+`wheel_web`; suspension legs/hubs/knuckle posts/axle stubs (on body \| rocker/bogie \| knuckle) | origin L278-L324; lattice helper |
| internal joints | 6× `{row}_{side}_wheel_spin` CONTINUOUS(Y); articulated `{side}_rocker_pivot`/`{side}_bogie_pivot` REVOLUTE(Y); steered `{row}_{side}_steer` REVOLUTE(Z) | origin L325; rocker L278,L373; steer L309 |
| upstream interface | **none declared** (parallel children; parents to body/rocker/bogie/knuckle) | — |
| downstream interface | re-export body (passthrough) | — |

### Slot C / module rigid_mast | folding_mast
| emits | 描述 | 来源 |
|---|---|---|
| parts | `camera_mast`(\|`lower_mast`+`upper_mast`) + `mast_camera_head` | origin L338,L379; folding L349,L386 |
| visuals | flange + column(s) + cross handle + electronics pod + head stub + hinge knuckles/lug; head: neck collar + box + 2 lenses + accent bar | origin L339-L404; folding L349-L412 |
| internal joints | `mast_yaw` REVOLUTE(Z); `head_tilt` REVOLUTE(Y); folding adds `mast_deploy` REVOLUTE(Y) | origin L369,L405; folding L376,L413 |
| upstream interface | **none declared** (parallel child; parents to body) | — |
| downstream interface | re-export body (passthrough) | — |

### Slot D / module rigid_arm | elbow_arm | turret_roll_arm
| emits | 描述 | 来源 |
|---|---|---|
| parts | `robotic_arm`(\|`upper_arm`+`forearm`); turret_roll adds `instrument_turret` | origin L419; multi L421,L456; turret L479 |
| visuals | shoulder hub + upper link + elbow + forearm + wrist + turret cyl + drill bit + sensor block | origin L420-L481 |
| internal joints | `arm_shoulder_yaw` REVOLUTE(Z); elbow adds `arm_elbow_pitch` REVOLUTE(Y); turret_roll adds `wrist_roll` CONTINUOUS(X) | origin L482; multi L504; turret L498 |
| upstream interface | **none declared** (parallel child; parents to body) | — |
| downstream interface | re-export body (passthrough) | — |

### Slot E / module az_dish | azel_gimbal
| emits | 描述 | 来源 |
|---|---|---|
| parts | `high_gain_antenna`; azel adds `hga_elevation_yoke` | origin L495; hga L520 |
| visuals | gimbal stem + `LatheGeometry` dish + dish boss; azel adds elevation bearing + yoke axle + 2 yoke arms | origin L496-L523; hga L509-L558 |
| internal joints | `hga_azimuth` REVOLUTE(Z); azel adds `hga_elevation` REVOLUTE(Y) | origin L524; hga L559 |
| upstream interface | **none declared** (parallel child; parents to body) | — |
| downstream interface | re-export body (passthrough) | — |

活动件语义：wheel spin 驱动前进；rocker/bogie 铰接吸收地形；steer 转向；mast yaw/tilt 指向
相机；deploy 展开桅杆；shoulder/elbow/wrist_roll 操作机械臂；hga az/el 指向天线。不动细节
（deck 设备、hazcam、UHF、suspension 装饰腿、桅杆手柄）写成宿主 part visual（Rule 1）。
captured axle/flange/hub/stem socket 用 element-scoped allow_overlap（Rule 2 例外）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `deck_form` | enum | equipment_deck / solar_wing_deck | equipment_deck | choice | procedural sampler | Slot A |
| `mobility_module` | enum | fused_rocker_bogie / articulated_rocker_bogie / steered_corners | fused_rocker_bogie | choice | procedural sampler | Slot B |
| `wheel_hub_form` | enum | solid_disc / spoked_lattice | solid_disc | choice | procedural sampler | Slot B ③ |
| `mast_module` | enum | rigid_mast / folding_mast | rigid_mast | choice | procedural sampler | Slot C |
| `arm_module` | enum | rigid_arm / elbow_arm / turret_roll_arm | rigid_arm | choice | procedural sampler | Slot D |
| `antenna_module` | enum | az_dish / azel_gimbal | az_dish | choice | procedural sampler | Slot E |
| `wheel_radius_scale` | float | [0.92, 1.10] | 1.0 | independent | uniform, clamp; wheel_radius; axle_z co-derived | origin L43 |
| `mast_height_scale` | float | [0.85, 1.20] | 1.0 | independent | uniform, clamp; mast column length + head z | origin L57 |
| `arm_reach_scale` | float | [0.90, 1.15] | 1.0 | independent | uniform, clamp; arm link lengths | origin L429-L457 |
| `dish_radius_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform, clamp; HGA dish lathe radii | origin L502-L511 |
| `steer_range` | float | [0.35, 0.60] | 0.55 | conditional | steered_corners steer ± (rad); else n/a | steer L318 |
| `mast_deploy_upper` | float | [1.20, 1.57] | 1.45 | conditional | folding_mast deploy upper (rad); else n/a | folding L419 |
| `hga_elevation_range` | float | [0.40, 0.60] | 0.55 | conditional | azel_gimbal elevation ± (rad); else n/a | hga L568 |
| `wheel_radius` | float | derived | — | equation | `= 0.26 · wheel_radius_scale`; `axle_z = wheel_radius` (ground contact) | origin L43 |

所有 equation/conditional 在 `resolve_config` 内求解；builder 不失败。连续 scale 不影响 body
的共享 mount datum（挂点用固定常数），故不破坏任何 slot 接口。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: ≤ 20 s** (hang-guard `--compile-timeout 60`). Heavy meshes:
6 wheels share ONE `tire_mesh` + ONE `wheel_disc_mesh` (solid `WheelGeometry` or the
`_build_lattice_wheel_disc` Torus/tube merge — the lattice is the single most expensive
mesh, ≤16 spokes × radial 8, rings tubular ≤48); suspension tubes `tube_from_spline_points`
(radial 16); dish `LatheGeometry` (48 seg); solar-grid revolve mesh. All 6 wheels reuse the
shared meshes, both sides reuse suspension leg splines. Tessellation tiers: dish/solar ≤48
seg, tubes radial 16, small cylinders default. No boolean sculpting. Expect 6-14 s/seed;
downgrade spoke count / tube radial segments first if over.

## Multiplicity / Copy Logic

- **本类别的唯一固定复制是 6 个轮子**：`for i in range(6)` 复制同构 `{row}_{side}_wheel`
  （3 行 × 2 侧），全部共享 `tire_mesh`/`wheel_disc_mesh`，spin joint 沿 Y。这是**类别身份的
  固定结构**，不是可采样的 `*_count` multiplicity 轴 —— 本 5 星池没有任何 wheel-count 变体
  （wheel-count 变化属于 sibling *Lunar rover* 池），故轮数固定 6，不暴露 `wheel_count`，
  也不做加权采样。naming `{front,middle,rear}_{left,right}_wheel`；placement `WHEEL_ROW_X ×
  ±WHEEL_TRACK_Y`；joint CONTINUOUS(Y)；source origin L298-L333。
- 除此之外无模板级复制数量逻辑：核心多样性由 5 个 named slot（+ wheel_hub_form ③）表达，
  不通过循环复制模板级 part/joint 数量。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | mobility：fused（wheels on body）/ articulated rocker+bogie parts（+4 REVOLUTE pivots）/ steered corners（+4 knuckle parts, +4 REVOLUTE steer）—— forked_anchor（rocker_bogie_linkage / steering_knuckles）。mast：2-part rigid / 3-part folding（+deploy edge）—— forked_anchor（folding_mast）。arm：1-part rigid / 2-part elbow（+elbow）/ arm+turret（+wrist_roll）—— forked_anchor（multi_joint_arm / turret_rotation）。HGA：1-part az / 2-part az-el（+elevation）—— forked_anchor（hga_elevation_gimbal）。全部 source-backed。 |
| └ multiplicity | 同构件 ×N | 无(固定) | 见 §8：轮数固定 6（类别身份；池内无 wheel-count 变体）。声明"无可采样 multiplicity 轴 + 理由"。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | CONTINUOUS(Y wheel spin, X wrist_roll) ↔ REVOLUTE(Z mast_yaw/steer/shoulder/hga_az, Y head_tilt/deploy/elbow/rocker/bogie/hga_el)。wrist_roll CONTINUOUS(X)（turret_rotation）与 steer/rocker/bogie/elbow/deploy REVOLUTE 全部 forked_anchor；声明的每种类型都在 sweep 出现。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | **两处登记进 slot_choices**：(A) deck 形态 slot — equipment box deck（origin, Macro Surface Construction）/ solar-array wings（solar_deck, Planar Boundary Form）。(B) wheel_hub_form — solid domed disc（origin, closed）/ spring-spoke lattice（spoked_wheel_hub, Macro Surface Construction 开放晶格）。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | deck 设备箱阵列、`front_hazcam_*`、`uhf_antenna_can`、solar `_solar_grid_mesh` 电池格线、tire block tread、head `head_accent_bar` 橙条 —— 均为宿主 part visual，随 ③（deck 面）/⑤（缩放）派生位置。source_type=record_only（origin/solar_deck）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：wheel_radius_scale[0.92,1.10]、mast_height_scale[0.85,1.20]、arm_reach_scale[0.90,1.15]、dish_radius_scale[0.85,1.15]。运动包络（每个非-continuous joint）：mast_yaw Z 双向 ±2.8；head_tilt Y ±0.45；mast_deploy Y [0, mast_deploy_upper≤1.57]；shoulder_yaw Z [-0.35,0.50]；elbow Y [-1.4,0.5]；steer Z ±steer_range≤0.60；hga_azimuth Z ±2.6；hga_elevation Y ±hga_elevation_range≤0.60；rocker Y ±0.20；bogie Y ±0.25。continuous（wheel spin / wrist_roll）采整圈 {0,±90°,180°}。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32)`（自由度多，取 32）；targeted `ctx.pose` — wheel spin 转 90° 保持接地、mast yaw 转 π/2、head tilt、shoulder yaw 侧摆、elbow 折叠、hga slew 离桅杆、（如有）steer 转向、deploy 展开、elevation 抬升。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted/metal；≥5 colorway：`nasa_white`（白板+橙件）、`mer_gold`（金箔+深板）、`dusty_tan`（火星尘调）、`dark_ops`（暗色）、`bare_metal`（银）、`science_blue`。材质大类覆盖 ≥ ceil(0.5×6)=3。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 equipment/solar 两种 deck、solid/lattice 两种轮盘、
fused/articulated/steered 三种底盘、rigid/folding 桅杆、rigid/elbow/turret 三种臂、az/azel
两种天线、材质配色多样、所有关节全程不穿模。

## 采样与覆盖审计

总组合数（distinct slot-choice tuple 上界）：
- deck 2 × mobility 3 × wheel_hub 2 × mast 2 × arm 3 × antenna 2 = **144**。

理由：144 < 富类别建议 300，因为真实结构词汇在此收敛 —— 所有样本共享同一
「boxy chassis + 6-wheel rocker-bogie + pan/tilt mast + arm + HGA」cell，可变轴是 6 根
离散槽（含 wheel_hub ③）。不硬凑组合空间（质量红线：不反推上游变体数量）。report-only，
不设 gate。

seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次抽
deck_form、mobility_module、wheel_hub_form、mast_module、arm_module、antenna_module、palette，
再抽连续 scale + conditional 关节 range。seed 0 pinned 到 origin 母本组合（equipment_deck +
fused_rocker_bogie + solid_disc + rigid_mast + rigid_arm + az_dish, nasa_white）作为 documented
regression anchor（sparse override，其余 seed 全 procedural）。random sweep `0-15`（fast）→
`0-35`（final）→ corner。

Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察；真实上界 144（见上），低于
300 的原因为结构词汇收敛，已记录。report-only。

Controlled local parameterization：`wheel_radius_scale`（axle_z 派生）、`mast_height_scale`、
`arm_reach_scale`、`dish_radius_scale`、conditional `steer_range`/`mast_deploy_upper`/
`hga_elevation_range`。全部在 `resolve_config` clamp / 派生；不破坏共享 body mount datum、
captured-socket 接口、joint 原点、类别身份。连续尺寸契约：先采 independent（4 个 scale）→
conditional 关节 range 按上游 module 解析。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 deck→mobility→wheel_hub→mast→arm→antenna，等权 choice | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 全 6 轴正交自由组合；无互斥；conditional joint range 仅当对应 module 选中才生效 | 无 floating / collision / 轴错误 / 可选子件失败 |
| controlled local variation | 4 个 clamp 连续 scale + 3 个 conditional joint range | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| chassis (deck) | 2 | yes | no | 池内 deck 形态恰 2 种 |
| mobility | 3 | yes | yes | fused/articulated/steered |
| wheel_hub (③) | 2 | yes | no | solid/lattice |
| camera_mast | 2 | yes | no | 池内 mast 骨架恰 2 种 |
| robotic_arm | 3 | yes | yes | rigid/elbow/turret_roll |
| high_gain_antenna | 2 | yes | no | 池内 HGA 骨架恰 2 种 |

## Validator

- `slot_choices_for_seed` returns implemented module names (deck/mobility/wheel_hub/mast/arm/antenna)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented 母本 override only)
- conditional joint ranges resolved in `resolve_config` (steer_range/mast_deploy_upper/hga_elevation_range only bound when their module is selected)
- controlled local scales clamped; cannot break shared body mount datum, captured-socket interfaces, joint-origin honesty
- captured axle/flange/hub/stem/pivot overlaps are element-scoped `allow_overlap` (not broad part-level)
- key joints have expected type/axis: wheel CONTINUOUS(Y); rocker/bogie REVOLUTE(Y); steer REVOLUTE(Z); mast_yaw REVOLUTE(Z)/head_tilt REVOLUTE(Y)/deploy REVOLUTE(Y); shoulder REVOLUTE(Z)/elbow REVOLUTE(Y)/wrist_roll CONTINUOUS(X); hga_azimuth REVOLUTE(Z)/hga_elevation REVOLUTE(Y)
- 6 wheels always present; copied `{row}_{side}_wheel` follow naming + placement policy
- `run_astronomy_mars_rover_tests` calls `fail_if_parts_overlap_in_sampled_poses` + ≥1 targeted `ctx.pose` per mechanism

## Reject cases

- Wheel not grounded (aabb bottom |z| > ~0.03 after scaling) → keep spin origin z = wheel_radius.
- Articulated rocker/bogie swings a wheel into the chassis at pivot min/max → cap rocker ±0.20 / bogie ±0.25 (source values); never widen to pass.
- Steering knuckle steers the corner wheel into the fused suspension leg → cap steer_range ≤0.60; element-scoped allow_overlap only on knuckle post ↔ leg terminus.
- Folding upper mast folds back and the head clips the deck / lower column → cap mast_deploy_upper ≤1.57; targeted deploy pose test.
- HGA dish slewed in azimuth clips the camera mast → keep dish outboard on the deck; targeted az pose gap test (origin L611-L620).
- Solar wing deck leaves the wing floating off the chassis (bracket gap) → wing brackets tie the wing to the chassis side wall (Rule 4 / connectivity).
- Downgrading the `LatheGeometry` dish / `tube_from_spline_points` suspension legs / lattice wheel `Torus` merge to crude Box/Cylinder (Rule 3 violation).

## 与相邻类别的边界

- 不该混入：**Astronomy / Lunar rover**（载人开放式月球车：座椅、手柄、无密封仪器舱与机械臂；本类别是无人火星车，有 boxy 密封舱 + 机械臂 + 桅杆）。
- 不该混入：**Astronomy / Antenna dish**（地面站 az-el 天线整体即对象；本类别的 HGA 只是车上小型可动附件）。
- 不该混入：一般 wheeled robot / 推车（无 rocker-bogie 六轮 + 桅杆 + 机械臂 + HGA 的火星车身份组合）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 轮数固定 6（池内无 wheel-count 变体，wheel-count 属 sibling Lunar rover）；5 个 parallel-children slot（deck③ + mobility + mast + arm + HGA）+ wheel_hub③ 子参数，全 source-backed，无 world_knowledge_extrapolation。待人工 viewer 目检类别忠实。 |

## 模板实现备注（可选）

- body mount datums（DECK_TOP / MAST_BASE / ARM_SHOULDER / HGA_BASE / WHEEL_ROW_X / pivots）single-sourced 为模块级常数（Contract 3c），所有 slot 挂点从中派生，deck 形态正交。
- 6 wheels 共享一个 `tire_mesh` + 一个 `wheel_disc_mesh`（solid 或 lattice）；两侧 suspension leg 共享 spline helper —— 保编译预算。
- captured pin overlaps（axle-in-hub / mast-flange-in-deck / head-collar-on-stub / shoulder-hub-in-bracket / gimbal-stem-in-pedestal / hinge lug / pivot hub）全部 element-scoped `allow_overlap`，与 origin run_tests 一致（Rule 2 例外）。
- 组装走 `_modular.assemble(..., selection_mode="anchor_choices")`：chassis root 声明 downstream；其余 4 slot 只声明 downstream（re-export body）→ 无自动 chain joint，各模块发原始 joint 到 body（parallel-children，同 Tipping_Barrow 惯用）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D/E | equipment_deck + fused_rocker_bogie + solid_disc + rigid_mast + rigid_arm + az_dish | `rec_a-perseverance-...6a5aa1bc` (origin 母本) | L34-L653 | body part tree + deck + fused suspension + 6 wheels + rigid mast/arm/HGA + 全部 test 语义 |
| S2 | B ① | articulated_rocker_bogie | `rec_mars_rover_var_rocker_bogie_linkage` | L171-L390, L440-L465 | rocker+bogie parts + REVOLUTE(Y) pivots + wheel re-parenting |
| S3 | B ①/② | steered_corners | `rec_mars_rover_var_steering_knuckles` | L270-L395 | 4 corner knuckle parts + REVOLUTE(Z) steer + corner wheel re-parenting |
| S4 | B ③ | spoked_lattice wheel disc | `rec_mars_rover_var_spoked_wheel_hub` | `_build_lattice_wheel_disc` (~L40-L110) | 开放弹簧辐条晶格轮盘 mesh |
| S5 | C ①/② | folding_mast | `rec_mars_rover_var_folding_mast` | L57-L67, L346-L456 | 两段可展开桅杆 + mast_deploy REVOLUTE(Y) |
| S6 | D ① | elbow_arm | `rec_mars_rover_var_multi_joint_arm` | L419-L515 | upper_arm + forearm + elbow REVOLUTE(Y) |
| S7 | D ①/② | turret_roll_arm | `rec_mars_rover_var_turret_rotation` | L419-L510 | instrument_turret part + wrist_roll CONTINUOUS(X) |
| S8 | E ①/② | azel_gimbal | `rec_mars_rover_var_hga_elevation_gimbal` | L495-L570 | elevation yoke + hga_elevation REVOLUTE(Y) |
| S9 | A ③ | solar_wing_deck | `rec_mars_rover_var_solar_deck` | L44-L55, L82-L175 | MER 太阳翼 deck + `_solar_grid_mesh` 电池格 |
