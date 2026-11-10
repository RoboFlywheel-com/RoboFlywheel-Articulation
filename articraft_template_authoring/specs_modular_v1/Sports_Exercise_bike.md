# Modular Spec — exercise_bike (Sports / Exercise bike)

## 元信息
| 项 | 值 |
|---|---|
| slug | `exercise_bike` |
| template path | `agent/templates/Sports_Exercise_bike.py` |
| test path (optional) | `tests/agent/test_exercise_bike_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：parallel_children core（body root 同时挂 flywheel / crank / saddle/seat / handlebar 子件）+ linear_chain（crank → pedal 子链）+ multiplicity（stabilizer feet ×N，body 下统一 FIXED）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (parent + 8 variants) |
| source_index_policy | only adopted module sources are indexed below |

读到的 9 个 5★ 源（全部完整读过 model.py，已逐一解析 part tree / 非 fixed joint / multiplicity loop / primitive）：

| 别名 | record_id |
|---|---|
| S_parent | rec_white-upright-stationary-exercise-bike-with-red-_20260605_165843_884664_7f5ac918 |
| S_recumbent | rec_exercise_bike_var_recumbent |
| S_spin | rec_exercise_bike_var_spin |
| S_perf | rec_exercise_bike_var_perforated_flywheel |
| S_mag | rec_exercise_bike_var_magnetic_shroud |
| S_straight | rec_exercise_bike_var_straight_bar |
| S_aero | rec_exercise_bike_var_aero_grip |
| S_feet3 | rec_exercise_bike_var_feet3 |
| S_feet4 | rec_exercise_bike_var_feet4 |

## 核心身份

固定式（stationary）室内健身脚踏车：一个落地静止的车体（body root），前部有一个绕水平侧轴（Y）连续旋转的阻力飞轮 / 阻力源，body 下方一个曲柄（crank，绕 Y 连续旋转）带两条相隔 180° 的曲臂，每条曲臂末端各有一个绕自身踏轴（Y）连续旋转的踏板（pedal）。骑乘工位由坐垫（saddle on post 或 recumbent seat carriage）和把手 / 控制台（handlebar + console）提供，二者各自有一个升降 / 滑移自由度（PRISMATIC）。车体由若干根横向 chrome 稳定脚管（stabilizer feet ×N，FIXED）支撑在地面上，构成最宽的地面占地。+X = 车前（飞轮 / 阻力侧），−X = 车后，+Z = 上，+Y = 左侧。

成熟域：upright（立式塑壳）、recumbent（卧式长梁 + 靠背座）、spin（开放焊接钢管架）三种车体姿态；阻力源在裸露飞轮盘 / 镂空铸轮 / 全封闭磁阻罩之间变化；把手在 ram-horn 控制台 / 直把无控制台 / 多握位气动把之间变化。核心可动预算：flywheel（连续）+ crank（连续）+ 2×pedal（连续）+ saddle/seat（prismatic）+ handlebar（prismatic）[+ 可选 tension_knob（revolute）]，feet 全部固定。

## 槽位 + 候选模块表

### Slot A：frame_type（车体 / 骑乘工位姿态，body root）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| upright_shroud | S_parent | L77-L110（`_body_solid` 泪滴侧形 loft）+ L182-L203（body root + crank_boss + inertial） | eligible if compatible | 高耸竖立的塑料模塑壳体（teardrop 侧形 XZ extrude both=True + `edges("|Y").fillet`），坐垫在曲柄上方、把手在前桅杆；saddle/handlebar post 竖直 PRISMATIC 升起 |
| recumbent | S_recumbent | L66-L97（`_beam_solid` 长梁侧形）+ L201-L255（body root + flywheel_housing + flywheel_axle + crank_boss + seat_rail + inertial） | eligible if compatible (gates handlebar→side_grips, saddle→seat_carriage) | 长低水平梁（dx>0.8m, dx>4·dz），前端低飞轮，后部斜躺 bucket 座 + 直立靠背在 X 向 PRISMATIC 滑轨上；侧握把（side grips）取代前桅把手 |
| spin_tube_frame | S_spin | L77-L121（`_tube`+`_frame_mesh` 开放三角钢管架）+ L188-L194（body root tube mesh + inertial） | eligible if compatible (gates feet mount→tube ends, watch×magnetic) | 暴露的焊接圆管三角架（seat/down/top/head tube + fork legs + rear stays + BB shell/collars + 飞轮 axle），无塑壳；saddle/handlebar post 从 seat tube / head tube 顶端竖直 PRISMATIC 升起 |

### Slot B：resistance_form（飞轮 / 阻力源呈现）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| front_disc_red_ring | S_parent | L113-L129（`_flywheel_mesh` dished disc+hub / `_flywheel_ring_mesh` red torus）+ L258-L279（flywheel part: disc+ring+off-axis marker + `body_to_flywheel` CONTINUOUS Y） | eligible if compatible | 裸露实心灰色 dished 盘 + 红色 TorusGeometry accent ring + 偏轴 bolt marker；单一连续 Y 关节 |
| perforated_spoked | S_perf | L113-L160（`_flywheel_rim_mesh` annular rim / `_flywheel_hub_mesh` / `_spoke_arm_geometry` / `_flywheel_ring_mesh`）+ L289-L326（rim+hub+`for i in range(N_SPOKES)` spoke_{i} rpy 等角 + red ring + marker + `body_to_flywheel` CONTINUOUS Y） | eligible if compatible | 开放铸轮：厚外圈 rim + 中央 hub，二者由 for-i 等角辐条 spoke_{i}（N_SPOKES=8）连接，辐条间留空；红 accent ring 在 rim 带上；单连续 Y 关节 |
| magnetic_shroud_knob | S_mag | L132-L162（`_resistance_housing_mesh` 封闭罩 / `_flywheel_mass_mesh` 内部转子）+ L308-L376（flywheel mass `body_to_flywheel` CONTINUOUS Y + tension_knob part KnobGeometry + `body_to_tension_knob` REVOLUTE Z lower0 upper2.6） | eligible if compatible (gated off spin_tube_frame) | 无裸轮：body 上 fillet 圆罩 resistance_housing（visual on body）盖住内部 flywheel_mass（仍连续转 Y，藏在罩后）+ 顶部 tension_knob（第 2 真关节 REVOLUTE Z）含 pointer tab marker |

### Slot C：handlebar_form（把手 + 控制台座舱）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| ramhorn_console | S_parent | L145-L162（`_handlebar_mesh` ram-horn `tube_from_spline_points`）+ L373-L415（hbar_post: post tube + console_pad(tilted white) + handlebar_clamp + handlebar_tube + `body_to_handlebar_post` PRISMATIC Z） | eligible if compatible (gated off recumbent) | 弯曲红色 ram-horn 管（对称 U 形 spline）+ 倾斜白色显示控制台板；竖直 PRISMATIC 升降 |
| straight_bar_no_console | S_straight | L150-L153（`_grip_mesh`）+ L364-L408（hbar_post: post tube + handlebar_clamp + 直 `handlebar_bar` + `for i in range(2)` foam grip_{i} 端握 + `body_to_handlebar_post` PRISMATIC Z） | eligible if compatible (gated off recumbent) | 平直水平 dark 横把（在 Y 向展开）+ 两端泡棉 foam grips，无控制台板；竖直 PRISMATIC 升降 |
| aero_multigrip | S_aero | L146-L174（`_crossbar_mesh`/`_side_grip_mesh`/`_aero_extension_mesh` spline/`_forearm_pad_mesh`）+ L400-L476（hbar_post: post tube + console_pad + clamp + crossbar + `for i in range(2)` side_grip_{i} + `for i in range(2)` aero_extension_{i}（前伸 spline）+ forearm_pad_{i} + `body_to_handlebar_post` PRISMATIC Z） | eligible if compatible (gated off recumbent) | 多握位铁三座舱：基础 crossbar（红）+ 两侧 side grip 立握 + 两根前伸 aero extension（for-i ×2 镜像）+ 前臂 pad，保留白色控制台板；竖直 PRISMATIC 升降 |

注：所有 slot 均有 3 个结构互异 candidate（无降级到 2 的情况）。

## 槽位图（slot graph）

pattern: mixed

```
                         body (root: frame_type ∈ {upright_shroud / recumbent / spin_tube_frame})
                         │
   ┌──────────────┬──────┴──────────┬───────────────────────┬────────────────────────────┐
   │              │                 │                       │                            │
[Slot B]       [Slot crank]     [Slot C / cockpit]      [Slot saddle/seat]      [Multiplicity: feet ×N]
flywheel      crank             handlebar_post           saddle_post /          stabilizer_foot_{i}
   │              │             (or recumbent side_grips) seat_carriage              (i=0..N-1)
   │              │                                                                       │
body→flywheel  body→crank      body→handlebar_post       body→saddle_post        body→stabilizer_foot_{i}
CONTINUOUS Y   CONTINUOUS Y    PRISMATIC Z (0..0.1)       PRISMATIC Z (0..0.1)    FIXED (all)
[+ body→tension_knob            [recumbent: body→side_grip_{0,1}  [recumbent: body→seat_carriage
 REVOLUTE Z if magnetic]         FIXED, +Y/−Y beam sides]          PRISMATIC X (−0.06..0.06)]
   │
   └── crank → left_pedal / right_pedal (linear chain)
       crank→{l,r}_pedal CONTINUOUS Y（在曲臂尖 tip_y=±CRANK_ARM_Y, tip_z=±CRANK_ARM_LEN）
```

跨 slot 连接接口点位与 joint：

- **body → flywheel**：接口 = 车前侧轴中心 `(FLYWHEEL_X, FLYWHEEL_Y, FLYWHEEL_Z)`（mating = 飞轮盘贴 body 前壳 / spin 架 fork 间 axle）。CONTINUOUS，axis=(0,1,0)，无限程。S_parent L271-L279。
- **body → crank**：接口 = 曲柄轴中心 `(CRANK_X, 0, CRANK_Z)`，crank hub 穿过 body 坐在 dark crank_boss 上。CONTINUOUS，axis=(0,1,0)，无限程。S_parent L296-L304。
- **crank → {left,right}_pedal**：接口 = 曲臂尖 `(0, ±CRANK_ARM_Y, ±CRANK_ARM_LEN)`（pedal spindle captured 在臂尖）。CONTINUOUS，axis=(0,1,0)，无限程。S_parent L332-L340。
- **body → saddle_post**（upright/spin）：接口 = body 座管口 / seat tube 顶（如 S_parent `(0.06,0,SADDLE_BASE_Z)`，S_spin `ST_TOP`）。PRISMATIC，axis=(0,0,1)，range lower0 upper0.1。S_parent L362-L371。
- **body → seat_carriage**（recumbent only，互斥替换 saddle_post）：接口 = 后部 seat rail 顶 `(SEAT_X,0,SEAT_RAIL_Z_TOP)`。PRISMATIC，axis=(1,0,0)，range lower−0.06 upper0.06。S_recumbent L453-L461。
- **body → handlebar_post**（upright/spin）：接口 = body 前桅 / head tube 顶（S_parent `(-0.10,0,HBAR_BASE_Z)`，S_spin `HT_TOP`）。PRISMATIC，axis=(0,0,1)，range lower0 upper0.1。S_parent L407-L415。
- **body → side_grip_{0,1}**（recumbent only，替换 handlebar_post 前桅）：接口 = 座旁梁侧面 `(GRIP_X, ±BEAM_HALF_W, GRIP_Z)`。FIXED。S_recumbent L487-L493。
- **body → tension_knob**（仅 magnetic_shroud_knob）：接口 = 阻力罩顶 `(KNOB_X,0,KNOB_Z)`。REVOLUTE，axis=(0,0,1)，range lower0 upper2.6。S_mag L368-L376。
- **body → stabilizer_foot_{i}**：接口 = body root 原点（foot 内部 visuals 自带 fx 偏移）。全部 FIXED。S_feet3 L274-L280。

互斥 / 派生关系：

- Slot C（handlebar_form）的三个 candidate 仅在 upright_shroud / spin_tube_frame 车体上挂前桅 handlebar_post；**recumbent 车体把 cockpit 槽派生为座旁 side_grips + 后部 seat_carriage**（无前桅把手），故 Slot C 的三 candidate 与 recumbent 互斥（见 compatibility matrix）。
- saddle_post（upright/spin）与 seat_carriage（recumbent）互斥：同一坐姿槽两种实现，由 frame_type 派生。
- magnetic_shroud_knob 引入第 2 真关节 tension_knob，且其封闭罩贴 body 壳；spin_tube_frame 无壳可贴 → 二者 watch-gated。

## 每槽位 Module Emits / Interfaces

### Slot A / module upright_shroud
| emits | 描述 | 来源 |
|---|---|---|
| parts | body root：`body_shroud`（teardrop loft 壳）+ `crank_boss`（dark 轴座 visual） | S_parent / L182-L197 |
| internal joints | 无（root 内部全 visual） | S_parent / L77-L110 |
| upstream interface | root（无父）；inertial Box(0.62,0.18,0.40)@(0.16,0,0.30) | S_parent / L199-L203 |
| downstream interface | 提供 flywheel 轴座、crank_boss、saddle 座管口、前桅 head 列、feet 挂点 | S_parent / L182-L203 |

### Slot A / module recumbent
| emits | 描述 | 来源 |
|---|---|---|
| parts | body root：`body_beam`（长梁）+ `flywheel_housing`+`flywheel_axle`+`crank_boss`+`seat_rail`（visuals） | S_recumbent / L201-L249 |
| internal joints | 无 | S_recumbent / L66-L97 |
| upstream interface | root；inertial Box(beam)；姿态断言 dx>0.8 且 dx>4·dz | S_recumbent / L251-L255 |
| downstream interface | 前端低飞轮 axle、crank_boss、后部 seat_rail（X 滑轨）、座旁 side_grip 挂点、feet 挂点 | S_recumbent / L201-L255 |

### Slot A / module spin_tube_frame
| emits | 描述 | 来源 |
|---|---|---|
| parts | body root：`frame`（开放钢管三角架 merged mesh：seat/down/top/head tube + fork legs + rear stays + BB shell/collars + 飞轮 axle） | S_spin / L92-L121, L188-L189 |
| internal joints | 无 | S_spin / L77-L121 |
| upstream interface | root；inertial Box(0.50,0.46,0.55)@(0.10,0,0.30) | S_spin / L190-L194 |
| downstream interface | ST_TOP（saddle 入口）、HT_TOP（handlebar 入口）、BB（crank）、fork 间 axle（flywheel）、fork/stay 端点（feet 挂点） | S_spin / L42-L54 |

### Slot B / module front_disc_red_ring
| emits | 描述 | 来源 |
|---|---|---|
| parts | `flywheel`：`flywheel_disc`(gray) + `flywheel_red_ring`(red torus) + `flywheel_marker`(偏轴 dark bolt) | S_parent / L258-L265 |
| internal joints | 无（marker 是 visual） | S_parent / L113-L129 |
| upstream interface | body→flywheel CONTINUOUS Y @(FLYWHEEL_X,FLYWHEEL_Y,FLYWHEEL_Z) | S_parent / L271-L279 |
| downstream interface | 无（叶端件）；marker 提供旋转可检测性 | S_parent / L262-L265 |

### Slot B / module perforated_spoked
| emits | 描述 | 来源 |
|---|---|---|
| parts | `flywheel`：`flywheel_rim`+`flywheel_hub`+`spoke_{i}`(i=0..7) + `flywheel_red_ring` + `flywheel_marker` | S_perf / L289-L311 |
| internal joints | 无（spoke 是等角 rpy visual loop，固定于飞轮） | S_perf / L140-L151, L297-L304 |
| upstream interface | body→flywheel CONTINUOUS Y @(FLYWHEEL_X,FLYWHEEL_Y,FLYWHEEL_Z) | S_perf / L317-L326 |
| downstream interface | 无；spoke_0 上嵌 marker 提供旋转可检测性 | S_perf / L307-L311 |

### Slot B / module magnetic_shroud_knob
| emits | 描述 | 来源 |
|---|---|---|
| parts | body 上 `resistance_housing`(封闭罩 visual)；`flywheel`(`flywheel_mass`+`flywheel_marker`)；`tension_knob`(`tension_knob_cap`KnobGeometry+`knob_pointer_tab`+`knob_shaft`) | S_mag / L222(housing), L308-L364 |
| internal joints | tension_knob 内部无 | S_mag / L334-L367 |
| upstream interface | body→flywheel CONTINUOUS Y；body→tension_knob REVOLUTE Z lower0 upper2.6 @(KNOB_X,0,KNOB_Z) | S_mag / L321-L329, L368-L376 |
| downstream interface | 无；罩盖住飞轮，knob pointer tab 提供旋转可检测性 | S_mag / L349-L356 |

### Slot crank（固定核心，所有 frame 共用，非可替换 slot）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `crank`（hub + 2 臂 180° merged）；`left_pedal`/`right_pedal`（tread+spindle+ridge marker） | S_parent / L283-L327 |
| internal joints | body→crank CONTINUOUS Y；crank→{l,r}_pedal CONTINUOUS Y（linear chain） | S_parent / L296-L304, L332-L340 |
| upstream interface | body→crank @(CRANK_X,0,CRANK_Z) | S_parent / L296-L304 |
| downstream interface | 曲臂尖 (0,±CRANK_ARM_Y,±CRANK_ARM_LEN) 作 pedal 挂点 | S_parent / L306-L340 |

### Slot C / module ramhorn_console（+ saddle_post 同属上身工位）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handlebar_post`：post_tube + console_pad(白倾斜) + handlebar_clamp + handlebar_tube(ram-horn) | S_parent / L376-L403 |
| internal joints | 无 | S_parent / L145-L162 |
| upstream interface | body→handlebar_post PRISMATIC Z lower0 upper0.1 @(-0.10,0,HBAR_BASE_Z) | S_parent / L407-L415 |
| downstream interface | 无 | S_parent / L376-L403 |

### Slot C / module straight_bar_no_console
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handlebar_post`：post_tube + handlebar_clamp + handlebar_bar(直) + grip_{0,1}(foam) | S_straight / L367-L396 |
| internal joints | 无 | S_straight / L150-L153 |
| upstream interface | body→handlebar_post PRISMATIC Z lower0 upper0.1 | S_straight / L400-L408 |
| downstream interface | 无 | S_straight / L382-L396 |

### Slot C / module aero_multigrip
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handlebar_post`：post_tube + console_pad + clamp + crossbar + side_grip_{0,1} + aero_extension_{0,1} + forearm_pad_{0,1} | S_aero / L403-L463 |
| internal joints | 无（aero_extension / side_grip / forearm_pad 是 for-i 镜像 visual） | S_aero / L146-L174, L436-L463 |
| upstream interface | body→handlebar_post PRISMATIC Z lower0 upper0.1 | S_aero / L468-L476 |
| downstream interface | 无 | S_aero / L425-L463 |

### Slot saddle/seat（由 frame_type 派生）
| emits | 描述 | 来源 |
|---|---|---|
| parts (upright/spin) | `saddle_post`：post_tube + saddle_pad（teardrop） | S_parent / L344-L358 |
| parts (recumbent) | `seat_carriage`：carriage_plate + seat_post + bucket_seat + backrest_bracket + backrest_pad；+ `side_grip_{0,1}` | S_recumbent / L400-L451, L463-L493 |
| internal joints | 无 | S_recumbent / L116-L167 |
| upstream interface | upright/spin: body→saddle_post PRISMATIC Z；recumbent: body→seat_carriage PRISMATIC X (−0.06..0.06) + body→side_grip_{i} FIXED | S_parent L362-L371 / S_recumbent L453-L461, L487-L493 |
| downstream interface | 无 | — |

### Multiplicity / module stabilizer_foot
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stabilizer_foot_{i}`：stabilizer_tube(chrome 横管) + foot_leg(竖腿) + foot_cap_{l,r} + foot_pad_{l,r} | S_feet3 / L235-L268 |
| internal joints | 无 | S_feet3 / L165-L168 |
| upstream interface | body→stabilizer_foot_{i} FIXED @ root（visual 自带 fx 偏移），均匀前后分布 | S_feet3 / L274-L284 |
| downstream interface | 无（落地件，构成最宽地面占地） | S_feet3 / L282-L284 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| frame_type | enum | upright_shroud / recumbent / spin_tube_frame | — | choice | deterministic procedural sampler；派生 saddle/seat 与 cockpit 形式 | Slot A 表 |
| resistance_form | enum | front_disc_red_ring / perforated_spoked / magnetic_shroud_knob | — | choice | sampler；magnetic 与 spin watch-gated | Slot B 表 |
| handlebar_form | enum | ramhorn_console / straight_bar_no_console / aero_multigrip | — | choice | sampler；仅 upright/spin 适用（recumbent 派生 side_grips） | Slot C 表 |
| palette_style | enum | classic_white_red / matte_black_steel / chrome_silver_red / studio_gray_lime / clinical_white_blue | classic_white_red | choice | 每 seed 采样一组材质 RGBA 配色（见下） | 各源 material() |
| stabilizer_foot_count | int | [2, 6]（测试 {2,3,4}） | 2 | choice (weighted) | multiplicity 加权采样（小 N 偏多）；见 Multiplicity 节 | S_feet3/4 |
| flywheel_radius_scale | float | [0.85, 1.15] | 1.0 | independent | clamp；缩放 FLYWHEEL_R | S_parent L46 |
| body_height_scale | float | [0.9, 1.12] | 1.0 | independent | clamp；缩放车体高 / 桅杆高（upright/spin）；recumbent 锁 1.0 | S_parent L57-L58 |
| foot_span_scale | float | [0.92, 1.12] | 1.0 | independent | clamp；缩放 stabilizer 横管 FOOT_LENGTH_Y | S_feet3 L211 |
| crank_arm_len_scale | float | [0.9, 1.1] | 1.0 | independent | clamp；缩放 CRANK_ARM_LEN | S_parent L52 |
| post_travel | float | [0.06, 0.12] | 0.1 | independent | PRISMATIC saddle/handlebar 行程 upper（recumbent seat 用 ±0.06 X） | S_parent L370 |
| (—) | constraint | — | — | inequality | feet 地面 Y 跨度 = FOOT_LENGTH_Y·foot_span_scale ≥ body_span_y（feet 必须是最宽占地）；违反则放大 foot_span_scale | S_parent L553-L558 |
| (—) | constraint | — | — | inequality | post 全升时 post_tube 与 body 座管/head 列在 Z 重叠 ≥0.02（不脱出）；违反则缩 post_travel | S_parent L527-L531 |
| (—) | constraint | — | — | inequality | feet 最低 z ≤ flywheel 最低 z + 0.02 且 < 0.05（脚最低落地）；违反则下移 foot tube | S_parent L548-L552 |
| (—) | constraint | — | — | conditional | handlebar_form ∈ {3 candidates} 仅当 frame_type ∈ {upright_shroud, spin_tube_frame}；recumbent → cockpit 派生为 side_grips + seat_carriage | Slot C / recumbent |
| (—) | constraint | — | — | conditional | resistance_form == magnetic_shroud_knob 时 frame_type ≠ spin_tube_frame（无壳贴罩），或退化为 front_disc | watch matrix |
| (—) | constraint | — | — | conditional | recumbent 时 body_height_scale 锁 1.0（长梁姿态不缩高） | S_recumbent 姿态断言 |

palette_style 配色（取自 5★ 源实测 material set：body_white/accent_red/part_gray/dark_gray/chrome/cap_black、frame_steel、seat_pad）：

- **classic_white_red**：white 壳 (0.93,0.93,0.94) + accent_red (0.82,0.10,0.12) + chrome + gray（parent / perf / mag / straight / aero 基色）
- **matte_black_steel**：frame_steel (0.18,0.19,0.22) 车体 + dark_gray 件 + 暗红 accent + cap_black（spin 钢管基色）
- **chrome_silver_red**：chrome (0.78,0.80,0.83) 主体高光 + red accent + dark hub + black caps
- **studio_gray_lime**：part_gray (0.45,0.45,0.48) 壳 + lime 替换 red accent (≈0.55,0.80,0.15) + chrome + black
- **clinical_white_blue**：white 壳 + blue accent (≈0.12,0.35,0.78) 替换 red + gray + chrome + seat_pad gray

（目标 4–6，此处 5 个，全部仅改 material RGBA，不改拓扑。）

## Multiplicity / Copy Logic

**轴 1：stabilizer_foot_count（唯一 multiplicity 轴）**

- `count_param`：`stabilizer_foot_count`
- `N_range`：产品域 [2, 6]；测试偏小 {2, 3, 4}（已被 5★ 覆盖：parent N=2 / S_feet3 N=3 / S_feet4 N=4）。真实健身车 2 长横脚最常见，3–4 短脚见于重型底座，封顶 ~6。
- sampling domain（权重档）：N=2 高频（~55%）、N=3（~25%）、N=4（~12%）、N=5（~5%）、N=6（~3%）——小 N 偏多、尾部稀有。
- copied object：一根 chrome stabilizer 横管（共享 `_foot_mesh(flen)` helper）+ 竖向 `foot_leg` + 2 个 `foot_cap_{l,r}` + 2 个 `foot_pad_{l,r}`。
- naming：`stabilizer_foot_{i}`（i=0..N-1，i=0 最前）；元素名 `stabilizer_tube`/`foot_leg`/`foot_cap_{l,r}`/`foot_pad_{l,r}`。**parent 的 front_foot/rear_foot 手写 tuple 必须改写为 `for i in range(n)` 循环**（S_feet3/S_feet4 已是规范实现，模板采纳该 loop 形式）。
- placement：沿 X 在 body 占地内前后等距：`fx = FOOT_FRONT_X − i·(FOOT_FRONT_X − FOOT_REAR_X)/(N−1)`（S_feet3 L283 / S_feet4 L270-L278）；每根横管沿 Y 是地面最宽跨度；leg_top_z 由 body 底形按 fx 取值（upright/spin 用 `_body_bottom_z(fx)`，recumbent 用 BEAM_Z_BOT）。
- joint policy：统一 — 每只脚 FIXED 挂到 body root（`body_to_stabilizer_foot_{i}`，origin=(0,0,0)，visual 自带 fx 偏移）。车的 articulation 预算来自 flywheel/crank/pedals/posts，脚保持固定。
- source/gating：S_feet3（N=3）/ S_feet4（N=4）/ parent（N=2，待改 loop）。N=2 时 fx 退化为前后两点（FRONT/REAR），公式仍成立。

无其他 multiplicity 轴（spoke_{i}、aero_extension_{i}、side_grip_{i}、grip_{i} 均为 module-local 固定结构，不暴露模板级 `*_count`）。

## 拓扑多样性审计

总组合数：
- frame_type=upright_shroud / spin_tube_frame（2）× resistance_form（3，magnetic×spin gated 略减）× handlebar_form（3）= ~18 cockpit 组合 ×
- frame_type=recumbent（1）× resistance_form（3，magnetic 退化）× (cockpit 固定为 side_grips) = 3 组合
- 合计 frame×resistance×cockpit ≈ 18 + 3 = **~21 拓扑骨架** × stabilizer_foot_count {2..6} 的 N 采样（5 档） ⇒ 名义上 ~21×5 = **~105** distinct（含 N 维）。

理由：仅 frame×resistance×handlebar 的合法骨架已 ~21（远超 10）；加上 stabilizer_foot_count 的多 N 复制，1000-seed distinct 预期 按 ≥300 report-only 口径观察。即便保守只数 part-set 拓扑（不数连续 scale），骨架数仍 ≥18。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed` 先加权采 frame_type → 按 frame_type 解析 cockpit/seat 派生（recumbent 跳过 handlebar_form、改 side_grips+seat_carriage）→ 采 resistance_form（spin 时 magnetic 以兼容矩阵 fallback 到 front_disc 或 perforated）→ 采 handlebar_form（仅 upright/spin）→ 加权采 stabilizer_foot_count → 采 palette_style → 采连续 scale（先 independent 主尺度，再 inequality 投影回缩 feet 跨度 / post 行程 / feet 落地）。compatibility matrix 在采样阶段 gate 非法组合，避免 builder 失败。少量 regression overrides 仅用于已知失败回归。random sweep：seeds 0-49 初轮、0-999 成熟审计。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别骨架 ~21 × N 档 5 → 预期可达 ~100+。若实测低于 300，归因于 recumbent 分支 cockpit 被派生压缩（合理类别约束）。

Controlled local parameterization：初版应含 `flywheel_radius_scale`[0.85,1.15] independent、`body_height_scale`[0.9,1.12] independent（recumbent 锁 1.0，conditional）、`foot_span_scale`[0.92,1.12] independent、`crank_arm_len_scale`[0.9,1.1] independent、`post_travel`[0.06,0.12] independent。依赖关系：feet 跨度 ≥ body_span_y（inequality，违反放大 foot_span_scale）；post 全升保留 ≥0.02 插入重叠（inequality，违反缩 post_travel）；feet 最低 z 落地（inequality）。全部在 `resolve_config` 内解算 clamp / 投影，不留到 builder。这些 scale 不破坏 InterfaceSpec（关节 origin 仍由参考坐标驱动）/ MatingContract / multiplicity（feet 间距公式按 N 自适应）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | frame→(派生 cockpit/seat)→resistance→handlebar(若 upright/spin)→foot_count(加权)→palette→continuous scales | slot_choices_for_seed matches build choices |
| compatibility matrix | recumbent ⊥ {3 handlebar candidates}（cockpit 派生 side_grips）；magnetic ⊥ spin（fallback front_disc/perforated）；saddle_post ⊥ seat_carriage（frame 派生）；watch: spin×magnetic 需小 housing bracket（暂不采样） | no floating, collision, axis, max multiplicity, bulky module, optional child failures |
| controlled local variation | flywheel_radius_scale / body_height_scale / foot_span_scale / crank_arm_len_scale / post_travel，全部 clamp + inequality 回缩 | proportions vary without breaking interfaces, clearance, support, joint origin, category identity |
| regression overrides | none（除非实现期发现具体失败 seed） | previously failed or reviewer-selected cases only |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | and contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A frame_type | 3 | yes | yes | upright / recumbent / spin |
| B resistance_form | 3 | yes | yes | disc / spoked / magnetic+knob |
| C handlebar_form | 3 | yes | yes | recumbent 派生不占此 slot |
| multiplicity foot_count | N{2..6} | yes | yes | 5★ 覆盖 {2,3,4} |

## Validator

- slot_choices_for_seed returns implemented module names（frame_type / resistance_form / handlebar_form / stabilizer_foot_count / palette_style）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating prevents illegal combos（recumbent×handlebar、magnetic×spin、saddle_post×seat_carriage）
- optional regression overrides are sparse and justified（none by default）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params clamped；feet 跨度 / post 行程 / feet 落地 inequality 在 resolve_config 解算
- cross-part scale dependencies resolved in `resolve_config`, not builder
- critical InterfaceSpec / MatingContract exist：body→flywheel(Y)、body→crank(Y)、crank→pedal(Y)、body→saddle/seat、body→handlebar/side_grips、body→foot_{i}、[body→tension_knob]
- key joints have expected type/axis/range：flywheel/crank/pedal CONTINUOUS Y；saddle/handlebar PRISMATIC Z (0..~0.1)；seat_carriage PRISMATIC X (±0.06)；tension_knob REVOLUTE Z (0..2.6)；feet FIXED
- copied objects follow naming/placement：stabilizer_foot_{i} 前后等距，i=0 最前，FIXED，feet 为最宽占地

## Reject cases

1. flywheel / crank / pedal 任一不是绕 Y 的 CONTINUOUS（被建成 FIXED 或装饰盘），失去核心踩踏 articulation。
2. saddle/handlebar post 升到顶后脱出 body 座管 / head 列（post_tube 与 body Z 重叠 < 0.02），读作断裂。
3. stabilizer feet 不是地面最宽占地（foot Y 跨度 < body_span_y），或脚不落地（foot 最低 z 不是最低件 / ≥0.05），整车悬空 / 不稳。
4. recumbent 车体却挂前桅 ram-horn/aero handlebar_post（未派生为 side_grips + seat_carriage），姿态自相矛盾。
5. magnetic_shroud_knob 装到 spin_tube_frame 上但无壳贴罩 / 无 housing bracket，封闭罩悬空穿模。
6. perforated_spoked 的 spoke_{i} 未用 for-i 等角 loop（手写少数辐条或辐条间无空），失去镂空铸轮识别度；或 marker 缺失致旋转不可检测。
7. stabilizer_foot_count 仍是 parent 的 front_foot/rear_foot 手写 tuple（未改 `for i in range(n)` 循环），N>2 时无法复制 / 命名 `stabilizer_foot_{i}`。
8. seat_carriage（recumbent）滑轨方向错误（沿 Z 而非 X）或脱离 seat_rail，或 saddle_post 与 seat_carriage 同时出现（互斥违例）。

## 与相邻类别的边界

- 不该混入：**Bicycle / 真实自行车**（理由：exercise_bike 是落地静止器械，靠 stabilizer feet 站立、无可滚动落地车轮、飞轮是阻力源不是承载轮；不得出现两个可滚动地面轮 + 转向前叉骑行链）。
- 不该混入：**Treadmill / 跑步机、Elliptical / 椭圆机**（理由：本类核心是 crank+pedal 旋转踩踏 + 前飞轮，不含跑带 / 椭圆踏轨 / 上肢摆臂连杆；阻力呈现限于飞轮盘 / 镂空轮 / 磁阻罩）。
- 不该混入：**Office chair / 普通座椅**（理由：recumbent 座虽有靠背，但必须挂在带飞轮 + 曲柄 + 踏板的器械车体上，不是独立可旋转升降办公椅）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核。开放问题见下方。 |

## 模板实现备注（可选）

- 共享 helper：`_foot_mesh` / `_build_stabilizer_foot`（feet loop，采 S_feet4 的函数式签名）；`_flywheel_ring_mesh`（红环，三 resistance 变体复用）；crank+pedal 核心块（三 frame 共用，参考坐标 CRANK_X/Z、CRANK_ARM_*）。
- captured-pin / 座入式 allow_overlap（element-scoped）需逐组合复制：saddle/handlebar post_tube↔body 壳（z 轴 expect_overlap ≥0.02）、crank↔body boss、flywheel↔body、pedal↔crank 臂尖、foot_leg↔body 壳、seat carriage_plate↔seat_rail（recumbent，x 轴 ≥0.04）、resistance_housing↔flywheel_mass（magnetic）。
- magnetic_shroud_knob 引入第 2 真关节（tension_knob REVOLUTE Z），需 KnobGeometry（diameter/height 是直径参数）+ pointer tab marker（破对称）+ knob_shaft 连罩顶。
- 暂不进入 seed domain 的组合：spin_tube_frame × magnetic_shroud_knob（需独立 housing bracket，compatibility-matrix 候选，本批不采样）。

## 开放问题（供审核）

- spin_tube_frame × magnetic_shroud_knob：是 fallback 到 front_disc/perforated（推荐，简单），还是实现一个挂在钢管 BB 附近的小 housing bracket？本 spec 默认 fallback。
- recumbent 的 cockpit 派生：side_grips 是否应进一步暴露一个小 enum（side_grips vs forward_recumbent_bar）？当前仅 1 种，归为 frame 派生固定结构，不计入 Slot C。
- N=2 时是否保留 parent 的非循环 fx（FRONT/REAR 两点），还是统一走 `for i in range(2)` 公式（两点退化）？推荐统一走公式以消除 parent 手写 tuple 分支。
