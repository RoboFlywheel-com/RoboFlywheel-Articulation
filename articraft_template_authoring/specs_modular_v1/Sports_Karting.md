# Modular Spec — `go_kart` (Sports / Karting)

## 元信息
| 项 | 值 |
|---|---|
| slug | `go_kart` |
| template path | `agent/templates/Sports_Karting.py` |
| test path (optional) | `tests/agent/test_go_kart_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children for chassis + seat + steering + 4 wheels/2 knuckles; multiplicity for the lateral cross-tube ladder) |

`pattern` 说明：chassis 是 root，seat / steering_wheel / 4 wheels(经 knuckle) / rear-drive 都是挂到 chassis 的 parallel children；横向 cross-tube ladder 是 chassis 内部的 N 复制 visual。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this category (parent + 10 variants) |
| source_index_policy | only adopted module sources are indexed below |

阅读清单（全部 rev_000001/model.py 已逐行读过，line range 均由源码解析得到）：
parent `rec_racing-go-kart-with-a-tubular-steel-frame-a-sing_20260605_165903_685895_dbb0d663` (687L)、
`rec_go_kart_var_bodywork` (642L)、`rec_go_kart_var_flatdeck` (728L)、`rec_go_kart_var_buggy` (754L)、
`rec_go_kart_var_flatsling` (717L)、`rec_go_kart_var_highback` (748L)、`rec_go_kart_var_butterfly` (729L)、
`rec_go_kart_var_qrhub` (829L)、`rec_go_kart_var_sideengine` (865L)、`rec_go_kart_var_chaindrive` (963L)、
`rec_go_kart_var_crosstubes6` (768L)。

## 核心身份

单座竞速/休闲 go-kart：低矮底盘（钢管框架或片材 deck），四个肥胖光头胎（前轮较小较窄、后轮较大较宽），
单人模塑桶椅，倾斜转向柱上的小方向盘，暴露的活后轴（live axle），可选发动机/链轮传动。坐标约定：
`+Y` = 前方、`-Y` = 后方、`+X` = 车左、`-X` = 车右、`+Z` = 上，地面 `z=0`，轮心 `z = tire_radius`。

**必须永远保留的核心 articulation（任何变体都不得改、不作为 slot 轴）：**
- 4 轮各自绕局部 X **CONTINUOUS** 滚动；前轮是各自 **REVOLUTE** 转向节（knuckle）的 child，后轮直接挂 chassis。
- 2 个前转向节绕竖直 Z **REVOLUTE** 转向（`front_left_steer` / `front_right_steer`，range ±0.52）。
- 方向盘绕倾斜柱轴 **CONTINUOUS** 自旋（`steering_spin`，axis = 柱轴 = local −Z，tilt `COLUMN_TILT`）。
- 座椅 FIXED 挂 chassis。

成熟域：竞速 kart / 出租休闲 kart / 越野 buggy-kart。不混入完整汽车（无封闭车身/车门/挡风/前后悬挂总成）、
不混入 ATV/四轮摩托（go-kart 是单座低坐姿、方向盘转向而非车把）、不混入卡丁车赛道护栏等场景物。

## 槽位 + 候选模块表

### Slot A：frame_chassis_form（整体框架/车身形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| open_tubular (parent) | rec_racing-go-kart-…_dbb0d663 | L145-L293 | eligible if compatible | 暴露焊接钢管：left/right_main_rail + center_spine + front/rear_cross_tube + 对角 brace（tube_from_spline_points）+ 粉色 superellipse side pods + 红色 front/rear fairing + floor_pan + seat_tray + column_lower_mount，低离地 `FRAME_Z=0.085` |
| bodywork_shroud | rec_go_kart_var_bodywork | L141-L195 | eligible if compatible | 单一连续 CIK 模塑外壳：nose+side pods+rear cowl 融成一条 `bodywork_shell`（superellipse_side_loft, segments=64），包住下底盘、隐藏钢管；decal 嵌在壳面；下方仍露 rear_axle_bar + floor_pan |
| flat_deck | rec_go_kart_var_flatdeck | L148-L286 | eligible if compatible | 平片材 `deck_pan`（宽薄 Box）+ 绕周一圈连续 `bumper_rail`（tube_from_spline_points 闭环 rounded-rect）+ 竖直 stanchions 连 deck↔rail + 后轴轴承座 + column_lower_mount；无 fore-aft 钢管 rail、无 side pod |
| offroad_buggy | rec_go_kart_var_buggy | L142-L357 | eligible if compatible | 抬高 `FRAME_Z=0.20` 的钢管框 + `roll_cage_hoop`（拱形 spline tube 跨座椅锚到 side rail）+ 前/后 down-bars(A/B 柱) + nerf bars + 前后 tube bumper；越野高离地 |

### Slot B：seat_form（座椅形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| molded_bucket (parent) | rec_racing-go-kart-…_dbb0d663 | L295-L336 | eligible if compatible | 深单桶椅：seat_pan + 中高 seat_back（两段 superellipse_side_loft）+ left/right_bolster（Box 侧翼）；seat_mount FIXED |
| flat_sling | rec_go_kart_var_flatsling | L296-L334 | eligible if compatible | 薄低 sling：浅 seat_pan + 低矮 seat_back，无高 bolster、无包裹翼，贴近地板 |
| high_back_shell | rec_go_kart_var_highback | L125-L160 + L326-L367 | eligible if compatible | 全包高背赛椅：单一连续 `seat_shell`（`section_loft` 8 段 oval 断面，`_seat_shell_section` 助手，wing 参数在肩高把侧断面前推成肩翼）升至头高 + 内背 padding 条 |

### Slot C：steering_wheel_form（方向盘 + 柱形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_3spoke (parent) | rec_racing-go-kart-…_dbb0d663 | L338-L397 | eligible if compatible | 圆环 rim（LatheGeometry torus，XY 平面）+ steering_hub + 3 根径向 `steering_spoke_*`（每隔 120°）+ off-axis `steering_marker`；倾斜柱 + `steering_column` shaft；`steering_spin` CONTINUOUS |
| butterfly_open | rec_go_kart_var_butterfly | L343-L419 | eligible if compatible | 开放 D-cut rim：上弧去掉，连续 U 形 spline rim（右 grip→平底 bar→左 grip）+ 2 根水平 spoke + hub，中心镂空；marker 在底 bar；`steering_spin` CONTINUOUS 保留 |
| quick_release_hub | rec_go_kart_var_qrhub | L345-L486 | eligible if compatible | 高 `qr_boss` 堆叠圆柱（base collar+splined body+top flange）夹在柱顶与轮之间 + 平底 rim（flat-bottom）+ 3 spoke；`steering_spin` 让轮+boss 一起转 |

### Slot D：rear_drive_form（后驱动/发动机形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| bare_axle (parent) | rec_racing-go-kart-…_dbb0d663 | L201-L207 | eligible if compatible | 仅暴露 live `rear_axle_bar`（Cylinder 跨后轮），无发动机块；chassis visual |
| side_engine_pod | rec_go_kart_var_sideengine | L522-L686 | eligible if compatible | 右后单缸 finned 发动机：engine_mount tubes + plate + engine_block + crankcase + 堆叠 lathed cooling-fin 缸头 + spark plug + 弯 `exhaust_header` tube + airbox/fuel + 曲轴 drive sprocket；全 chassis visual，无独立 joint |
| chain_sprocket_drive | rec_go_kart_var_chaindrive | L106-L168 + L314-L430 | eligible if compatible | 暴露链传动：engine_mount_plate + engine_block + 输出 shaft + `clutch_drum` + `engine_sprocket` + 键在活轴上的 `rear_sprocket`（`_sprocket_mesh` 助手）+ 包两轮的连续 `drive_chain` loop（`_chain_loop_points` tube）；全 chassis visual |

## 槽位图（slot graph）

pattern: mixed

```
chassis (root, Slot A)
 ├─[FIXED, seat_tray 上表面 mount @ (0,−0.06,frame_z+0.05); seat-local z=0=座底]──> seat (Slot B)
 ├─[CONTINUOUS steering_spin, axis=local −Z=柱轴, origin=col_top (0,0.12,0.49) rpy=(tilt,0,0);
 │   接口=column_lower_mount 套筒沿倾斜柱轴套住 steering_column, expect_overlap z≥0.02]──> steering_wheel (Slot C)
 ├─[REVOLUTE front_left_steer, axis=(0,0,1), range ±0.52, origin=(+FRONT_TRACK_X,FRONT_AXLE_Y,AXLE_Z_FRONT)]──> front_left_knuckle
 │        └─[CONTINUOUS front_left_roll, axis=(1,0,0), origin=(0,0,0)]──> front_left_wheel
 ├─[REVOLUTE front_right_steer, axis=(0,0,1), range ±0.52, origin=(−FRONT_TRACK_X,FRONT_AXLE_Y,AXLE_Z_FRONT)]──> front_right_knuckle
 │        └─[CONTINUOUS front_right_roll, axis=(1,0,0), origin=(0,0,0)]──> front_right_wheel
 ├─[CONTINUOUS rear_left_roll, axis=(1,0,0), origin=(+REAR_TRACK_X,REAR_AXLE_Y,AXLE_Z_REAR)]──> rear_left_wheel
 ├─[CONTINUOUS rear_right_roll, axis=(1,0,0), origin=(−REAR_TRACK_X,REAR_AXLE_Y,AXLE_Z_REAR)]──> rear_right_wheel
 └─[Slot D rear-drive: NO joint — pure chassis visuals 挂在 rear_cross_tube / rear_axle_bar 右侧真实面]
 └─[multiplicity: cross_tube_{i} ×N — chassis 内部 visual, NO joint, 随 chassis 动]
```

接口点位说明：
- **wheel ↔ knuckle/chassis**：轴线 mating（local X spin 轴）。前轮经 knuckle（vertical Z steer）间接挂 chassis；后轮直接挂 chassis。已声明 allow_overlap（hub/axle stub 穿 frame tube / 在 knuckle stub axle 上 captured）。
- **steering_wheel ↔ chassis**：`column_lower_mount`（Slot A 出的倾斜套筒，rpy=(COLUMN_TILT,0,0)）沿柱轴套住 `steering_column`，`expect_overlap(steering_column ↔ column_lower_mount, axes=z, min_overlap=0.02)`；`steering_spin` 轴 = 柱轴。
- **seat ↔ chassis**：Slot A 出的 `seat_tray`(或 deck/floor) 上表面 FIXED mount，seat 局部 z=0 = 座底；`expect_contact(seat, chassis)`。
- **Slot D ↔ chassis**：挂在 `rear_cross_tube` / `rear_axle_bar` 右后真实面，**无 joint**（parent visual，随 chassis 动）。
- 互斥/派生：Slot A 决定 `column_lower_mount` / 座椅 mount 面 / 离地高度（buggy 抬高），下游 Slot B/C/D 的 z 锚点随 Slot A 的 `FRAME_Z` 派生。

## 每槽位 Module Emits / Interfaces

### Slot A / open_tubular
| emits | 描述 | 来源 |
|---|---|---|
| parts | chassis visuals：left/right_main_rail、center_spine、front/rear_cross_tube、left/right_brace、rear_axle_bar、left/right_side_pod、front/rear_fairing、floor_pan、seat_tray、column_lower_mount、number_5 decals | S1 / L145-L293 |
| internal joints | 无（全是 chassis visual） | S1 |
| upstream interface | root（无 parent） | — |
| downstream interface | seat_tray 上表面（seat FIXED）、column_lower_mount 套筒（steering 套接）、front/rear 轴线（knuckle/wheel mount）、rear_cross_tube/rear_axle_bar 右后面（Slot D） | S1 / L276-L293,L184-L207 |

### Slot A / bodywork_shroud
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bodywork_shell`（单一连续 superellipse_side_loft）替换 pods+fairing；嵌面 decal；保留 rear_axle_bar + floor_pan + seat_tray + column_lower_mount | S2 / L141-L195 |
| internal joints | 无 | S2 |
| upstream interface | root | — |
| downstream interface | 同 open_tubular；seat 坐进 shell tub（XY containment, allow_overlap seat↔bodywork_shell） | S2 / L506-L561 |

### Slot A / flat_deck
| emits | 描述 | 来源 |
|---|---|---|
| parts | `deck_pan`(宽薄 Box) + 闭环 `bumper_rail`(tube) + stanchions + 后轴 bearing 座 + column_lower_mount + decal；无 fore-aft rail / 无 side pod | S3 / L148-L286 |
| internal joints | 无 | S3 |
| upstream interface | root | — |
| downstream interface | deck 上表面(seat mount)、column_lower_mount、轴线、rear 面 | S3 / L255-L286 |

### Slot A / offroad_buggy
| emits | 描述 | 来源 |
|---|---|---|
| parts | 抬高 rails + center_spine + `roll_cage_hoop` + 前后 down-bars + nerf bars + 前后 tube bumper + floor_pan/seat_tray/column_mount；FRAME_Z=0.20 | S4 / L142-L357 |
| internal joints | 无 | S4 |
| upstream interface | root | — |
| downstream interface | 同上，但 z 锚点抬高；roll_cage_hoop 必须落到 side rail 真实面（不可悬空） | S4 / L210-L357 |

### Slot B / molded_bucket
| emits | 描述 | 来源 |
|---|---|---|
| parts | seat_pan + seat_back + left/right_bolster（superellipse_side_loft + Box） | S1 / L305-L328 |
| internal joints | 无（seat 整体 FIXED） | S1 |
| upstream interface | seat_mount FIXED @ chassis seat_tray，seat-local z=0=座底 | S1 / L330-L336 |
| downstream interface | 无（终端） | — |

### Slot B / flat_sling
| emits | 描述 | 来源 |
|---|---|---|
| parts | 浅 seat_pan + 低 seat_back（无 bolster/wing） | S5 / L306-L327 |
| internal joints | 无 | S5 |
| upstream interface | seat_mount FIXED @ chassis | S5 / L328-L334 |
| downstream interface | 无 | — |

### Slot B / high_back_shell
| emits | 描述 | 来源 |
|---|---|---|
| parts | 单一 `seat_shell`（section_loft 8 oval 断面 + shoulder wings）升至头高 + seat_padding 条 | S6 / L326-L359（断面助手 `_seat_shell_section` L125-L160） |
| internal joints | 无 | S6 |
| upstream interface | seat_mount FIXED @ chassis | S6 / L361-L367 |
| downstream interface | 无 | — |

### Slot C / round_3spoke
| emits | 描述 | 来源 |
|---|---|---|
| parts | steering_column shaft + steering_rim(torus) + steering_hub + 3×steering_spoke_* + steering_marker | S1 / L352-L382 |
| internal joints | 无（整体随 steering_spin 转） | S1 |
| upstream interface | steering_spin CONTINUOUS @ chassis col_top，axis=−Z=柱轴；steering_column 套进 column_lower_mount | S1 / L384-L397 |
| downstream interface | 无 | — |

### Slot C / butterfly_open
| emits | 描述 | 来源 |
|---|---|---|
| parts | steering_column + U 形 `butterfly_rim`(spline tube) + hub + 2 水平 spoke + steering_marker | S7 / L352-L404 |
| internal joints | 无 | S7 |
| upstream interface | steering_spin CONTINUOUS @ chassis col_top（同 parent） | S7 / L406-L419 |
| downstream interface | 无 | — |

### Slot C / quick_release_hub
| emits | 描述 | 来源 |
|---|---|---|
| parts | steering_column + 堆叠 qr_boss 圆柱 + 平底 rim + hub + 3 spoke + steering_marker（marker 远离柱轴, moved 阈值仍>0.05） | S8 / L354-L470 |
| internal joints | 无（boss+wheel 一起随 steering_spin 转） | S8 |
| upstream interface | steering_spin CONTINUOUS @ chassis col_top | S8 / L479-L486 |
| downstream interface | 无 | — |

### Slot D / bare_axle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `rear_axle_bar`(Cylinder)；无发动机 | S1 / L201-L207 |
| internal joints | 无 | S1 |
| upstream interface | 挂 chassis rear（chassis visual，无 joint，随后轮线） | S1 |
| downstream interface | 无 | — |

### Slot D / side_engine_pod
| emits | 描述 | 来源 |
|---|---|---|
| parts | engine_mount tubes+plate、engine_block、crankcase、finned cylinder head（堆叠 lathe disc）、spark plug、exhaust_header、airbox/fuel、drive sprocket | S9 / L522-L686 |
| internal joints | 无（全 chassis visual） | S9 |
| upstream interface | 挂 rear_cross_tube/rail 右后真实面（无 joint，allow_overlap 与 frame） | S9 / L534-L553 |
| downstream interface | 无 | — |

### Slot D / chain_sprocket_drive
| emits | 描述 | 来源 |
|---|---|---|
| parts | engine_mount_plate、engine_block、输出 shaft、clutch_drum、engine_sprocket、rear_sprocket(键在活轴)、drive_chain loop | S10 / L314-L430（助手 `_sprocket_mesh` L106-L131、`_chain_loop_points` L133-L168） |
| internal joints | 无（全 chassis visual；活轴本身由 rear wheel roll joint 表达） | S10 |
| upstream interface | engine_mount_plate 焊到 frame rails，rear_sprocket 键在 rear_axle 线上（无独立 joint） | S10 / L319-L416 |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| frame_chassis_form | enum | {open_tubular, bodywork_shroud, flat_deck, offroad_buggy} | open_tubular | choice | deterministic procedural sampler | Slot A 表 |
| seat_form | enum | {molded_bucket, flat_sling, high_back_shell} | molded_bucket | choice | sampler | Slot B 表 |
| steering_wheel_form | enum | {round_3spoke, butterfly_open, quick_release_hub} | round_3spoke | choice | sampler | Slot C 表 |
| rear_drive_form | enum | {bare_axle, side_engine_pod, chain_sprocket_drive} | bare_axle | choice | sampler | Slot D 表 |
| cross_tube_count | int | [2, 10]（测试小 N 偏多；产品全程） | 2 | choice/weighted | 等距 fore-aft 站位，见 Multiplicity | crosstubes6 / L228-L236 |
| palette_style | enum | {race_pink_red, rental_charcoal, offroad_green, bare_steel, brass_drive} | race_pink_red | choice | 每 seed 采样一个 colorway | 各源 material 汇总 |
| frame_z | float | conditional | 0.085 (非buggy) / 0.20 (buggy) | conditional | `= 0.20 if frame_chassis_form==offroad_buggy else 0.085`；下游 seat/steering/drive z 锚点全部从 frame_z 派生 | parent L49 / buggy L51 |
| ride_height_scale | float | [0.9, 1.15] | 1.0 | independent | 在范围内独立采样后 clamp；乘到 frame_z 与 cage 峰高 | buggy CAGE_PEAK_Z L55 |
| track_width_scale | float | [0.92, 1.08] | 1.0 | independent | 缩放 FRONT_TRACK_X/REAR_TRACK_X；保持 REAR_TRACK_X > FRONT_TRACK_X | parent L38-L39 |
| tire_radius_scale | float | [0.9, 1.12] | 1.0 | independent | 同比缩放 front/rear tire R | parent L41-L44 |
| rear_tire_bias | float | derived | — | equation | `REAR_TIRE_R = FRONT_TIRE_R * k_r (k_r≈1.22)`、`REAR_TIRE_W = FRONT_TIRE_W * k_w (k_w≈1.64)`；保后轮恒更大更宽（run_tests 硬约束） | parent L41-L44 |
| axle_z | float | derived | — | equation | `AXLE_Z_FRONT=FRONT_TIRE_R`、`AXLE_Z_REAR=REAR_TIRE_R`（轮心=胎半径，落地 z=0） | parent L46-L47 |
| column_tilt | float | [0.45, 0.62] | 0.55 | independent | 柱倾角；steering_spin 轴与 column_lower_mount rpy 同步取该值 | parent L50 |
| seat_back_height_scale | float | conditional | 1.0 | conditional | 范围依 seat_form：molded_bucket [0.9,1.1]、flat_sling [0.7,0.9]（短背）、high_back_shell [1.1,1.4]（头高）；clamp 后不得碰 steering/roll_cage | seat 各源 |
| qr_boss_height | float | conditional | — | conditional | 仅 steering_wheel_form==quick_release_hub 时有效 [0.04,0.09]；保证 steering_marker 离柱轴 spin moved>0.05 | qrhub L361-L399 |
| — | constraint | — | — | inequality | seat_back/high_back_shell 顶 + roll_cage_hoop 不得侵入 steering_wheel 扫掠域：`seat_top_z + clear ≤ col_top_z` 否则回缩 seat_back_height_scale | seat/steering 接口 |
| — | constraint | — | — | inequality | Slot D 引擎/链轮包络须落在 rear_cross_tube 右后真实面、贴合 frame（允许 overlap 与 frame，但不得悬空/不得撞后轮）：`engine_x_inner ≥ −(REAR_TRACK_X − rear_tire_w/2 − clr)` | sideengine/chaindrive 接口 |

## Multiplicity / Copy Logic

**唯一一根 multiplicity 轴：`cross_tube_count`（底盘横向桥接管 ladder）。**

- `count_param`: `cross_tube_count`
- `N_range`: 产品域 **[2, 10]**；测试偏小 **{2, 3, 4, 6}**（5★ 样本覆盖 {2(parent 手写未循环), 6(crosstubes6 循环化)}；采样域大于样本覆盖属正常）。
- sampling domain（权重档）：小 N 高频（2–4 最常见，真实 kart 多为少数横管），大 N（7–10）稀有尾部下采样。
- copied object：一根贯穿左右 side rail 的 spline 横管，共享 helper `_lateral_cross_tube(y_pos, frame_z, radius)`（crosstubes6 L91-L102，端点用 `_rail_xz_at_y(y_pos)` 取该 Y 站位的 rail x/z，含轻微上拱 crown）。
- naming：`cross_tube_{i}`，`i = 0..N−1`。
- placement：在 `FRONT_AXLE_Y` 与 `REAR_AXLE_Y` 之间等距 fore-aft 站位，`t = i/(N−1)`，`cross_tube_0` 近前轴、`cross_tube_{N−1}` 近后轴（crosstubes6 L228-L236）。
- joint policy：全部是 chassis 的 visual，**无独立 joint**（随 chassis 动）；属 parent-visual 复制，不是 jointed multiplicity。
- source/gating：所有 Slot A 形态都可承载 ladder；但 **flat_deck** 没有 fore-aft 钢管 rail——在 flat_deck 下 ladder gated（横管要么改锚到 deck/bumper_rail 周边面，要么该形态把 cross_tube_count 钳到 0 并以 deck pan 自身承担横向刚度，spec 取后者：`cross_tube_count` 仅对有 fore-aft rail 的 {open_tubular, bodywork_shroud, offroad_buggy} 有效，flat_deck 下不发射）。

## 拓扑多样性审计

总组合数：A(4) × B(3) × C(3) × D(3) × cross_tube N 样本(测试 4 档) = 4×3×3×3×4 = **432**（仅结构 + 多重度，未计连续 scale）。
即便只看最小独立子集 A(4) × C(3) = 12 ≥ 10。

理由：单结构轴最大 4 候选已 >1；A×C=12 就已超 10；加上 B、D 与 cross_tube N，distinct 拓扑远超 10。1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）：结构 combos 上界 4×3×3×3=108（A 在 flat_deck 时禁 ladder 略减计数，但 ladder N 在其余三形态上再乘开），叠加 N∈[2,10] 与连续 scale 足以 按 ≥300 report-only 口径观察。

seed_domain_policy：procedural_first。
Procedural Sampling / Sweep Plan：`config_from_seed` 先对每个结构 slot 做加权 choice（A/B/C/D 各一），再对 `cross_tube_count` 做加权采样（小 N 偏多），再采 independent 连续 scale（ride_height/track_width/tire_radius/column_tilt），按 equation 派生（rear_tire_bias、axle_z），按 conditional 解析 frame_z / seat_back_height_scale / qr_boss_height，最后用 inequality 投影/回缩（seat↔steering 间隙、Slot D 包络）。compatibility matrix 处理非法组合（见下）。少量 regression overrides 仅用于已知失败回归。random sweep 初版 seeds 0-49，成熟审计 0-999。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；结构 108 上界 × N 档，低于 300 时记录离散空间或采样权重原因；scale 只补比例多样性。
Controlled local parameterization：`ride_height_scale`、`track_width_scale`、`tire_radius_scale`、`column_tilt`、`seat_back_height_scale`、`qr_boss_height`（详见参数表）。全部在 `resolve_config` 内 clamp/派生/投影；scale 之间依赖按第 7 节约束类型显式声明（rear_tire_bias=equation、axle_z=equation、frame_z/seat_back/qr_boss=conditional、两条 clearance=inequality），不当作互相独立的自由变量各抽各的。它们不会破坏核心 joint 轴/range、座椅 mount、steering 套接、Slot D 锚面、cross_tube ladder 站位。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | A→B→C→D enum 加权 choice，再 cross_tube_count 加权，再连续 scale | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | flat_deck → cross_tube_count 不发射(deck pan 承横向刚度)；offroad_buggy → roll_cage_hoop 必落 side rail 真实面(防悬空)；quick_release_hub → marker 离柱轴需 spin moved>0.05；high_back_shell/seat_back 顶须低于 steering 扫掠域 | no floating(roll cage/engine)、collision(seat↔steering、shroud↔seat)、axis、max multiplicity、bulky module |
| controlled local variation | 上列 6 个 scale，全部 clamp/派生/投影 | 比例变化不破坏 InterfaceSpec/MatingContract/multiplicity/clearance/joint origin/category identity（后轮恒大恒宽、四轮落地、转向±0.52） |
| regression overrides | none（如后续 fork 暴露失败再补 seed+理由） | previously failed / reviewer-selected only |
| random sweep | seeds 0-49 初版；0-999 成熟审计 | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A frame_chassis_form | 4 | yes | yes | |
| B seat_form | 3 | yes | yes | |
| C steering_wheel_form | 3 | yes | yes | |
| D rear_drive_form | 3 | yes | yes | |
| cross_tube_count (mult) | 测试4档/产品[2,10] | yes | yes | flat_deck 下 gated 不发射 |

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C/D + cross_tube_count）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating prevents illegal combos（flat_deck 禁 ladder；buggy roll_cage 锚 rail；qrhub marker spin；high_back 不撞 steering）
- optional regression overrides are sparse and justified（当前 none）
- final template does not endlessly cycle a small curated table as main seed domain
- controlled local scales clamped；rear_tire_bias/axle_z(equation)、frame_z/seat_back/qr_boss(conditional)、两条 clearance(inequality) 全在 `resolve_config` 求解
- critical InterfaceSpec/MatingContract 存在：column_lower_mount↔steering_column 套接、seat_tray↔seat FIXED、4 轴线 wheel mount、Slot D 锚面
- key joints 类型/轴/range 正确：4×CONTINUOUS roll(axis X)、2×REVOLUTE steer(axis Z, ±0.52)、1×CONTINUOUS steering_spin(柱轴)、1×FIXED seat_mount
- copied objects(cross_tube_{i}) 遵守 naming + 等距 placement，无独立 joint

## Reject cases

1. 任一核心 joint 缺失/改型（4 轮 roll、2 前转向、steering_spin、seat FIXED）——核心 articulation 不得作为 slot 轴。
2. 后轮不比前轮更大或更宽（违反 parent run_tests 的 rear>front 直径/宽度断言）。
3. 任一轮底未落到 ~z≤0.02 地面（轮心≠胎半径，导致悬空或埋地）。
4. steering_column 未套进 column_lower_mount（expect_overlap z<0.02），方向盘漂浮。
5. seat 不在车体中心或未接触 chassis（seat origin |x|≥0.05 或未 expect_contact）。
6. flat_deck 仍发射 fore-aft rail/side_pod 或仍发射 cross_tube ladder（与 deck 穿插/冗余）。
7. offroad_buggy 的 roll_cage_hoop 悬空未锚到 side rail 真实面（disconnected island）。
8. quick_release_hub 的高 boss 使 steering_marker spin moved ≤0.05（旋转不可检测）或 boss 穿柱；或 high_back_shell/seat_back 顶侵入 steering 扫掠域造成 collision。
9. Slot D 引擎/链轮悬空、撞后轮、或未贴 frame 真实面（应为 chassis visual + allow_overlap 与 frame，绝不漂浮）。
10. cross_tube_count 超出 [2,10] 或站位非等距/命名非 `cross_tube_{i}`。

## 与相邻类别的边界

- 不该混入：完整 **汽车/赛车**（go-kart 无封闭车身、无车门、无挡风、无独立前后悬挂总成；底盘低、live 后轴、单座露天）。
- 不该混入：**ATV / 四轮摩托**（go-kart 是低坐姿座椅 + 方向盘转向，不是跨骑座 + 车把转向）。
- 不该混入：**赛道场景物**（护栏、围墙、计时门）——本类别只建 kart 本体。

## Multiplicity 多样性补充（palette_style 详表）

观察自 5★ 源的真实 material 集，组成 5 个 colorway（per seed 采样其一）：

| palette_style | 车身/外壳 | 框架金属 | 座椅 | 传动/点缀 | 出处 |
|---|---|---|---|---|---|
| race_pink_red | body_pink (0.92,0.28,0.42) + body_red (0.80,0.14,0.16) | frame_steel (0.72,0.73,0.76) + dark_steel (0.26,0.27,0.29) | seat_gray (0.82,0.82,0.84) | rim_silver / marker_yellow / decal_white | parent / bodywork / sideengine / chaindrive |
| rental_charcoal | deck_charcoal (0.16,0.17,0.19) | frame_steel + dark_steel | seat_gray | rim_silver / marker_yellow | flatdeck |
| offroad_green | cage_green (0.22,0.52,0.28) | frame_steel + bumper_black (0.12,0.12,0.13) | seat_gray | rim_silver / marker_yellow | buggy |
| bare_steel | (无 body) 暴露钢管 | frame_steel + dark_steel | seat_gray | rim_silver / tire_rubber | parent open_tubular / bare_axle |
| brass_drive | body_pink/red | dark_steel + engine_aluminum (0.62,0.63,0.66) | seat_gray | sprocket_brass (0.72,0.56,0.22) / chain_oiled_steel (0.22,0.22,0.24) | chaindrive / sideengine |

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核。Open questions：(1) flat_deck 下 cross_tube_count gated 为 0（deck 承横向刚度）是否如期望，或应改为锚到 bumper_rail 周边发射横肋；(2) 是否要把 buggy 的 roll_cage 作为 Slot A 内固定子结构（当前如此）还是单列轴——保持折入 Slot A，避免出现单候选轴。 |

## 模板实现备注（可选）

- 共享 helper：`_tire_mesh` / `_wheel_visuals` / `_knuckle`（4 轮 + 2 knuckle 通用，所有变体一致）；`_lateral_cross_tube` + `_rail_xz_at_y`（cross_tube ladder）；`_sprocket_mesh` + `_chain_loop_points`（chain_sprocket_drive）；`_seat_shell_section` + `section_loft`（high_back_shell）。
- InterfaceSpec 重点：column_lower_mount↔steering_column 沿倾斜柱轴 `expect_overlap(axes=z, min_overlap=0.02)`，柱倾角 = `column_tilt`，steering_spin 轴必须与柱轴一致（local −Z + rpy=(tilt,0,0)）。
- captured-pin/element-scoped allow_overlap：前轮 hub/axle ↔ knuckle stub（element pair）、4 轮 ↔ chassis 轴线/frame tube、knuckle ↔ front_cross_tube kingpin、steering_column ↔ column_lower_mount、（bodywork_shroud）seat ↔ bodywork_shell、（Slot D）engine/sprocket/chain ↔ frame——均须按形态分别声明。
- 暂不进入 seed domain 的组合：无强制排除（flat_deck×ladder 已由 gating 处理，不是排除而是该轴不发射）。
