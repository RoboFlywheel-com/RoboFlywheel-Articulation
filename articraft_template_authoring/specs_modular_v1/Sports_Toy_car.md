# Modular Spec — `toy_car` (Sports / Toy car)

## 元信息
| 项 | 值 |
|---|---|
| slug | `toy_car` |
| template path | `agent/templates/Sports_Toy_car.py` |
| test path (optional) | `tests/agent/test_toy_car_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children body + deck-mechanism, with a `multiplicity` axis over wheels) |

`pattern` 说明：一个 root `body` part 同时挂载 (a) 一个 deck-top play mechanism slot 和 (b) N 个独立 wheel 子件（multiplicity 轴）。body 是共同 chassis/parent，两类 child 都直接挂到它上面 → `parallel_children` 主干 + `multiplicity` 复制轴 = `mixed`。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (parent + 9 forked variants) |
| source_index_policy | only adopted module sources are indexed below |

读到的 10 个 5★ 源（全部读完 model.py，非仅 source map）：parent `rec_wooden-push-toy-car-…2a7a9bf4`、`rec_toy_car_var_{classic,pickup,racer,spinner,steering,knobby,spoked,wheels3,wheels6}`。

## 核心身份

`toy_car` 是一个 **chunky 木质推拉玩具车（push toy）**：沿 +X 为车长（车头/角色脸在 +X 前方），沿 Y 为车宽，+Z 向上；车身搁在一组红色车轮上滚动（地面 z=0）。它由三个结构层组成：

1. **车身 + 角色形态层**（Slot A）：一个 lofted/boolean 木块车身轮廓 + 一个 driver/character 形象（bug 头或 driver 头，带眼睛+笑脸等 parent visual）。
2. **甲板顶部可动玩法机构层**（Slot B）：固定在 body 上甲板（约 z=BODY_TOP_Z）的第二级铰接玩具特征——bead-maze 金属丝拱（拱 FIXED、3 颗珠子各自 CONTINUOUS 自旋）、屋顶 spinner 风车（单 CONTINUOUS 绕 +Z）、或方向盘转向柱（单 CONTINUOUS 绕倾斜柱轴）。
3. **车轮模块层**（Slot C，multiplicity）：单个 wheel 几何（圆盘/越野花纹胎/辐条轮），按 wheel_count 复制 N 次，每个都是绕 wheel-local Y 轴的独立 CONTINUOUS roll 关节。

成熟域：木质学步玩具车（push-along toddler toy），尺度约 0.15–0.17 m 长。核心可动语义 = 车轮滚动（恒在）+ 一个甲板玩法机构的二级铰接。

## 槽位 + 候选模块表

### Slot A：body_character_form（车身轮廓 + driver/character 形象）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| bug_face_beetle | rec_wooden-push-toy-car-…2a7a9bf4 | L67-L168 (`_body_solid` L67-88 + bug head/eyes/smile/nose/antennae/axle pegs/inertial L112-168) | eligible if compatible | 5 段 rect loft 圆甲板块（圆边 fillet），前部窄向车头；球形 bug 头 (head_r=0.026) 坐在甲板上，两眼+笑脸 torus+红鼻+两根天线；无 driver 坐舱 |
| classic_car_driver | rec_toy_car_var_classic | L74-L162 (`_body_solid` 含 7 段甲板 loft + `cabin` box union L74-106；driver head/眼/笑 + axle pegs/inertial L123-162) | eligible if compatible | 两厢经典车：甲板 loft（前部斜降的引擎盖）+ 后部 raised cabin box（CABIN_H=0.032）union；球形 driver 头 (R=0.015) 从开放座舱顶出，点眼+笑脸 |
| pickup_truck_bed | rec_toy_car_var_pickup | L65-L217 (`_truck_body` boolean L65-141：base slab + cab box + 货箱外墙 union，挖 cavity + cockpit well；driver stem/head/眼 + axle pegs/inertial L158-217) | eligible if compatible | 皮卡：前部高 cab block + 后部低开放货箱（侧墙+尾门，挖空 cavity，WALL_T=0.007）；cab 顶挖 cockpit well 露出 driver stem+小头 |
| open_racer_cockpit | rec_toy_car_var_racer | L76-L184 (`_racer_body_solid` 6 段 tapered loft + 挖 cockpit 圆柱 cut L76-114；driver head/眼/笑 + axle pegs/inertial L131-184) | eligible if compatible | 低矮锥形赛车壳，rear 宽 tail → 尖鼻（front Y 宽仅 0.014）；甲板上挖圆 cockpit pocket（R=0.020 深 0.018），driver 头坐在 pocket 里 |

Slot A = 4 candidates（≥3 ✓）。共享：车身永远是 root `body` part，永远暴露 `body_block`/`racer_hull`/`truck_body` named visual + 两/三根 `axle_{i}` peg parent visuals + driver/character 面部 parent visuals（不作独立 part）。

### Slot B：deck_top_play_mechanism（甲板顶二级铰接玩法）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| bead_maze_arch | rec_wooden-push-toy-car-…2a7a9bf4 | L170-L248 (wire arch `tube_from_spline_points` + `wire_arch` part + `body_to_arch` FIXED L170-200；3 颗 bead disc + `arch_to_bead_i` CONTINUOUS L202-248) | eligible if compatible | 弯曲金属丝拱（6 控制点 spline，apex≈z0.112，feet 嵌入甲板）FIXED 到 body；3 颗扁圆 bead 各 CONTINUOUS 绕本地丝段切向自旋。结构最深：1 FIXED + 3 CONTINUOUS（拱是独立 part，珠子挂在拱上） |
| rooftop_spinner | rec_toy_car_var_spinner | L107-L272 (`_spinner_disc_solid` hub+4 桨叶 L107-131；post_collar+spinner_post parent visuals L209-218；`spinner_disc` part + 4 彩点 + bore cap + `body_to_spinner` CONTINUOUS +Z L226-272) | eligible if compatible | 甲板上竖直 post+collar（parent visual）+ 风车圆盘（中心 hub+4 桨叶 boolean union，4 彩点 marker），单 CONTINUOUS 绕 +Z 轴，origin 在 post-top |
| steering_column | rec_toy_car_var_steering | L106-L252 (`_steering_wheel_mesh` rim torus+hub+4 spokes L106-134；column_boss+column_post parent visuals tilted L207-217；`steering_wheel` part + rim marker + `body_to_steering` CONTINUOUS 绕倾斜柱轴 L225-252) | eligible if compatible | 倾斜柱（TILT=30°，boss+post parent visual）+ 圆方向盘（rim torus+hub+4 辐条），单 CONTINUOUS 绕倾斜柱轴（joint origin 在柱顶 boss，rpy 把 local Z 对齐柱向） |

Slot B = 3 candidates（≥3 ✓）。注意：bead_maze_arch 自身是 *子-multiplicity*（3 颗珠子内部循环），spinner/steering 是单一 CONTINUOUS revolute 直接挂 body。

### Slot C：wheel_form（单个 wheel 几何）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_disc | rec_wooden-push-toy-car-…2a7a9bf4 | L250-L295 (`_wheel_mesh` `WheelGeometry`+rim/hub/face/bore L251-262；per-wheel hub_cap + spin_marker + `axle_{nm}` CONTINUOUS +Y L271-295) | eligible if compatible | 光滑红圆盘轮（`WheelGeometry` rim+recessed hub+dished face+round bore）+ 浅色 hub_cap + 黑 spin_marker |
| knobby_offroad | rec_toy_car_var_knobby | L40-L43 (常量 TIRE_BODY_R/KNOB_R/KNOB_N=8/KNOB_ROWS=2) + L255-L319 (`_build_knobby_tire`：cylinder 胎体+sidewall ridges+tread band+2 错列环 8 球 lug 共 16 lug L255-286；per-wheel hub_cap+marker+`axle_{nm}` CONTINUOUS L295-319) | eligible if compatible | 胖越野胎：圆柱胎体 + 两条错列环各 8 个圆 lug 球（merge），更大 hub_cap；轴关节同 round_disc |
| spoked_wheel | rec_toy_car_var_spoked | L46-L53 (常量 N_SPOKES=6/RIM_T/HUB_R/SPOKE_*) + L257-L323 (`_rim_mesh` LatheGeometry 环 + `_hub_mesh` + `_spoke_mesh(i)` BoxGeometry ×6 for-loop L257-287；per-wheel rim+hub+6 spoke+hub_cap+marker+`axle_{nm}` CONTINUOUS L296-323) | eligible if compatible | 开放辐条轮（cartwheel）：lathe 环 rim + 中心 hub + 6 根 chunky 径向 spoke（BoxGeometry，SPOKE_OVERLAP 连通）；轴关节同 round_disc |

Slot C = 3 candidates（≥3 ✓）。三者 emit 同一对外接口：one wheel part + 绕 wheel-local Y 的 CONTINUOUS roll 关节 + `spin_marker`（测试用）+ `hub_cap`，因此可与任意 wheel_count 复制逻辑解耦。

## 槽位图（slot graph）

pattern: `mixed`（parallel_children body 主干 + multiplicity wheels）

```
                 body (root, Slot A)
                 ├──[FIXED or CONTINUOUS @ deck top face z≈BODY_TOP_Z]── Slot B mechanism
                 │      • bead_maze_arch: body_to_arch FIXED (origin 0,0,0; feet 嵌甲板)
                 │            └──[CONTINUOUS axis=local wire tangent]── bead_i ×3 (子-multiplicity)
                 │      • rooftop_spinner: body_to_spinner CONTINUOUS axis=+Z @ post-top
                 │      • steering_column: body_to_steering CONTINUOUS axis=tilted col @ boss-top (rpy=-TILT about Y)
                 │
                 └──[CONTINUOUS axis=+Y @ axle peg z=AXLE_Z(=WHEEL_R), y=±AXLE_Y]── wheel_i ×N (Slot C, multiplicity)
```

跨 slot 连接说明：

- **Slot A ↔ Slot B**：接口 = body 上甲板 mating face（约 z=BODY_TOP_Z；pickup 在 cab roof/bed wall，racer 在 cockpit-后甲板）。单 mating face + 一个 anchor（拱的两脚 / spinner post-collar / steering boss）。consumer joint = 机构自身的 articulation：bead_maze_arch 先 FIXED（拱本身不动）再让珠子 CONTINUOUS；spinner/steering 直接一个 CONTINUOUS revolute 挂 body。axis：spinner=+Z；steering=倾斜柱轴（joint rpy 倾斜 local Z）；bead=local wire 切向（每颗珠子单算）。range：全部 CONTINUOUS（无限位）。
- **Slot A ↔ Slot C**：接口 = body 的 axle peg 圆柱侧面，anchor = axle origin `(ax_x, ±AXLE_Y, AXLE_Z)`，AXLE_Z=WHEEL_R 保证轮子落地。consumer joint = CONTINUOUS 绕 +Y。wheel_count multiplicity 决定 emit 多少 axle peg / wheel 对。
- 互斥/可选：Slot B 三选一（每 seed 恰好一个机构）。Slot A/B/C 之间无强制互斥，但有 gating（见兼容矩阵）：open_racer_cockpit × bead_maze_arch（拱脚可能浮空/穿 cockpit）、pickup_truck_bed × rooftop_spinner（货箱墙与 post 冲突）需 clearance gate / fallback。

## 每槽位 Module Emits / Interfaces

### Slot A / module bug_face_beetle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` (root)；named visuals: `body_block`, `bug_head`, `eye_0/1`, `smile`, `nose`, `antenna_0/1`, `axle_0/1` | parent / model.py:L105-168 |
| internal joints | 无（车身刚体；面部/天线/axle 都是 parent visual） | parent / model.py:L112-162 |
| upstream interface | root part（无 parent）；inertial Box origin z=(BODY_BOT_Z+BODY_TOP_Z)/2 | parent / model.py:L164-168 |
| downstream interface | 上甲板 face z≈BODY_TOP_Z 供 Slot B；axle pegs @ z=AXLE_Z, ±AXLE_Y 供 Slot C consumer CONTINUOUS | parent / model.py:L156-162 |

### Slot A / module classic_car_driver
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`；visuals: `body_block`(deck loft ∪ cabin box), `driver_head`, `driver_eye_0/1`, `driver_smile`, `axle_0/1` | classic / model.py:L124-162 |
| internal joints | 无 | classic / model.py:L99-106 |
| upstream interface | root part；inertial origin z=0.055（含 cabin 高度） | classic / model.py:L158-162 |
| downstream interface | cabin/deck top（cabin_top=BODY_TOP_Z+CABIN_H=0.102）供 Slot B；axle pegs 供 Slot C | classic / model.py:L150-156 |

### Slot A / module pickup_truck_bed
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`；visuals: `truck_body`(base∪cab∪bed walls, cavity/well cut), `driver_stem`, `driver_head`, `driver_eye_0/1`, `axle_0/1` | pickup / model.py:L159-217 |
| internal joints | 无 | pickup / model.py:L65-141 |
| upstream interface | root part；inertial origin (0.01,0,0.055) | pickup / model.py:L213-217 |
| downstream interface | cab roof (CAB_TOP_Z=0.094) + bed wall top (BED_TOP_Z=0.070) 供 Slot B 双脚；axle pegs 供 Slot C | pickup / model.py:L201-211 |

### Slot A / module open_racer_cockpit
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`；visuals: `racer_hull`(tapered loft − cockpit cut), `driver_head`, `driver_eye_0/1`, `driver_smile`, `axle_0/1` | racer / model.py:L132-178 |
| internal joints | 无 | racer / model.py:L76-114 |
| upstream interface | root part；inertial origin z=(BODY_BOT_Z+BODY_TOP_Z)/2 | racer / model.py:L180-184 |
| downstream interface | 甲板 top z≈BODY_TOP_Z（cockpit pocket 在 COCKPIT_X 占用，机构脚须落在 pocket 外）供 Slot B；axle pegs 供 Slot C | racer / model.py:L172-178 |

### Slot B / module bead_maze_arch
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wire_arch`（part，含 `arch_wire` visual）+ `bead_0/1/2`（每颗一个 part，含 `bead_disc` visual） | parent / model.py:L189-236 |
| internal joints | `body_to_arch` FIXED(parent=body)；`arch_to_bead_i` CONTINUOUS×3 (parent=arch, axis=local wire tangent, effort0.2/vel10) | parent / model.py:L194-248 |
| upstream interface | 拱两脚嵌入 body 甲板（intentional embed, allow_overlap arch_wire↔body_block）；FIXED origin (0,0,0) | parent / model.py:L194-200 |
| downstream interface | beads 螺纹穿在 wire 上（allow_overlap bead_disc↔arch_wire, expect_contact） | parent / model.py:L225-248 |

### Slot B / module rooftop_spinner
| emits | 描述 | 来源 |
|---|---|---|
| parts | body parent visuals: `post_collar`, `spinner_post`；`spinner_disc`（part，含 `disc_body`+`blade_dot_0..3`+`hub_bore_cap`） | spinner / model.py:L209-256 |
| internal joints | `body_to_spinner` CONTINUOUS(parent=body, axis=+Z, origin=POST_TOP, effort0.3/vel15) | spinner / model.py:L264-272 |
| upstream interface | post/collar 立在甲板 z=BODY_TOP_Z（parent visual） | spinner / model.py:L209-218 |
| downstream interface | disc hub 套在 post 顶（allow_overlap disc_body↔spinner_post, expect_contact） | spinner / model.py:L369-382 |

### Slot B / module steering_column
| emits | 描述 | 来源 |
|---|---|---|
| parts | body parent visuals: `column_boss`, `column_post`(tilted)；`steering_wheel`（part，含 `steering_wheel_body`+`steer_marker`） | steering / model.py:L207-235 |
| internal joints | `body_to_steering` CONTINUOUS(parent=body, axis=local +Z, origin=(COL_TOP_X,0,COL_TOP_Z) rpy=(0,-TILT,0), effort0.3/vel10) | steering / model.py:L244-252 |
| upstream interface | boss/post 立在甲板 COL_BASE_X，柱倾斜 TILT=30° | steering / model.py:L207-217 |
| downstream interface | 方向盘绕倾斜柱轴旋转（rim marker 用于 spin 检测） | steering / model.py:L232-252 |

### Slot C / module round_disc（per-copy emit；wheels3/wheels6 共享同一 wheel 几何）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel_{i}`（或 N=4 时 `wheel_front_left` 等语义名）；visuals: `wheel_body`, `hub_cap`, `spin_marker` | parent / model.py:L271-282 |
| internal joints | 无内部关节（wheel 刚体） | parent / model.py:L251-262 |
| upstream interface | 套在 body axle peg 上（allow_overlap wheel_body↔axle_{peg}） | parent / model.py:L359-367 |
| downstream interface | `axle_{nm}` CONTINUOUS(parent=body, axis=(0,1,0), origin=(ax_x, ysign·AXLE_Y, AXLE_Z), effort0.5/vel20) | parent / model.py:L287-295 |

### Slot C / module knobby_offroad
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel_{i}`；visuals: `tire_tread`(胎体+16 lug), `hub_cap`, `spin_marker` | knobby / model.py:L296-306 |
| internal joints | 无 | knobby / model.py:L255-286 |
| upstream interface | 同 round_disc（套 axle peg） | knobby / model.py:L295-302 |
| downstream interface | `axle_{nm}` CONTINUOUS axis=+Y（同 round_disc，effort0.5/vel20） | knobby / model.py:L311-319 |

### Slot C / module spoked_wheel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel_{i}`；visuals: `rim`, `hub`, `spoke_0..5`, `hub_cap`, `spin_marker` | spoked / model.py:L297-310 |
| internal joints | 无（spoke 是 visual，SPOKE_OVERLAP 保连通） | spoked / model.py:L257-287 |
| upstream interface | 同 round_disc（套 axle peg） | spoked / model.py:L296-306 |
| downstream interface | `axle_{nm}` CONTINUOUS axis=+Y（同 round_disc，effort0.5/vel20） | spoked / model.py:L315-323 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | {bug_face_beetle, classic_car_driver, pickup_truck_bed, open_racer_cockpit} | — | choice | deterministic procedural sampler | Slot A table |
| deck_mechanism | enum | {bead_maze_arch, rooftop_spinner, steering_column} | — | choice | sampler；受兼容矩阵 gating | Slot B table |
| wheel_form | enum | {round_disc, knobby_offroad, spoked_wheel} | — | choice | sampler | Slot C table |
| wheel_count | int | [3, 8]（test 偏小 {3,4,6}） | 4 | conditional | 见 Multiplicity；奇数=1 centerline 前轮+成对后轮，偶数=每轴 L/R 对 | wheels3/wheels6 |
| palette_style | enum | {natural_wood_red, painted_primary, candy_pastel, monochrome_black_white, retro_teal_orange, bright_rainbow} | natural_wood_red | choice | 每 seed 抽一个 colorway，统一映射 body/wheel/bead/blade 材质 | 见下 palette 说明 |
| body_length_scale | float | [0.92, 1.18] | 1.0 | conditional | 上限随 wheel_count 提高：wheel_count≥6 时车身须拉长以容纳第 3 轴（wheels6 BODY_LEN=0.168 vs 0.150）；BODY_LEN·scale ≥ 覆盖 axle X 跨度 | parent L45 / wheels6 L47 |
| body_width_scale | float | [0.92, 1.10] | 1.0 | independent | 在范围内独立采样后 clamp | _body_solid Y 段 |
| deck_height_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 BODY_TOP_Z；clamp 保证机构脚/post 仍坐甲板 | parent L47-48 |
| wheel_radius_scale | float | [0.88, 1.12] | 1.0 | equation | `AXLE_Z = WHEEL_R·scale`（轴高=轮半径，保证落地 min_z≤0.004）；hub_cap/marker 随比例 | parent L38-40 |
| axle_track_scale | float | [0.90, 1.12] | 1.0 | inequality | `AXLE_Y·scale ≥ body_half_width + WHEEL_W/2 + clearance`（轮不穿车身侧壁），否则回缩 | parent L43 |
| mechanism_scale | float | [0.85, 1.15] | 1.0 | inequality | 缩放机构（拱高/post 高/柱长/盘径）；`mechanism footprint ⊂ deck top face` 且不与相邻 Slot A 特征穿模，违反回缩 | spinner/steering/arch |
| (—) | constraint | — | — | inequality | 落地约束：所有 wheel `min_z ≤ 0.004`（AXLE_Z=WHEEL_R·wheel_radius_scale 强制满足） | 接口 / 落地 |
| (—) | constraint | — | — | conditional | racer×arch / pickup×spinner 组合的机构 anchor 须落在合法甲板区（cockpit pocket 外 / 货箱墙外），否则 fallback 换机构 | 兼容矩阵 |

**palette_style colorways（≥3，目标 4–6，取 6）** —— 取自 5★ 源实际出现的材质/颜色集合（natural_wood + wood_dark + toy_red + hub_light + face_black + bead_red/orange/green + blade_red/blue/yellow/green + driver_skin）：
- `natural_wood_red`（baseline：木色车身 + 红轮 + 红/橙/绿珠 + 黑面，parent 原配）
- `painted_primary`（红蓝黄三原色车身/轮，对应 spinner blade_red/blue/yellow）
- `candy_pastel`（柔和粉彩 body+wheel，珠子淡化）
- `monochrome_black_white`（黑白木 + 浅 hub_light 点缀）
- `retro_teal_orange`（蓝绿金属丝 wire_metal + 橙红 accent，呼应 metal+bead_orange）
- `bright_rainbow`（多彩珠/桨叶满配，body 木色）

## Multiplicity / Copy Logic

**唯一 multiplicity 轴：wheel_count**（其余结构由固定 named slots 表达）。

- `count_param`：`wheel_count`
- `N_range`：产品域 `[3, 8]`（3 轮 trike / 4 轮标准 / 6 轮 / 8 轮 hauler）；测试偏小，已覆盖样本 `{4(parent), 3(wheels3), 6(wheels6)}`
- sampling domain（权重档）：小 N 高频——`N=4` 权重最高（标准玩具车），`N=3` 次之，`N≥6` 稀有尾部（仅 hauler 形态）。建议加权 ~ {4:0.5, 3:0.25, 6:0.15, 8:0.10} 之类，downstream 人工审核后定。
- copied object：单个 wheel part（按 wheel_form 选 `WheelGeometry`/knobby tire/spoked rim）+ 其 `hub_cap` + `spin_marker`；每个一条 CONTINUOUS roll 关节（parent=body, axis=+Y）。配套 emit body 上 `axle_{j}` peg parent visual（每根轴一个）。
- naming：`wheel_{i}`（语义 N=4 可用 `wheel_front_left` 等，但模板首版统一用 `wheel_{i}` 更稳）；axle pegs `axle_{j}`。
- placement：成对 L/R 在 ±AXLE_Y，轴沿 X 在 `AXLE_RX..AXLE_FX` 间规则分布；**奇数 N** 在最前（或后）放一个 centerline 轮 `y=0`（wheels3：1 前 centerline + 2 后；需在车身底挖 front-wheel 通道，见 wheels3 L90-105）。**偶数 N** 每轴 L/R 对（wheels6：3 轴×2）。axle X 数 = ceil(N/2)（奇数含 1 centerline 轴）。
- joint policy：每个 wheel 一条独立 CONTINUOUS 关节绕 wheel-local Y（parent=body），uniform effort0.5/velocity20；**无链式**，各轮独立滚动。
- source/gating：`wheel_radius_scale` 不随 N 变；`body_length_scale` 上限随 N 提高（conditional，见参数表）以容纳更多轴。

（注：bead_maze_arch 内部的 3 颗珠子是 *module-local 固定 multiplicity*，不是模板级 `*_count` 轴——首版固定 3 颗，不暴露 bead_count。）

## 拓扑多样性审计

总组合数：Slot A(4) × Slot B(3) × Slot C(3) × wheel_count N-samples(≥3：{3,4,6}，产品域 [3,8] 可达 6 个离散值) = **4×3×3×6 = 216** 拓扑组合（即使只数测试 N {3,4,6} 也有 4×3×3×3 = 108）。

理由：仅 Slot A×B×C 已 36 distinct 拓扑（part/joint 拓扑各不同），叠加 wheel_count 改变 part 数与 axle 布局 → 108–216，远超 10。

seed_domain_policy：`procedural_first`
Procedural Sampling / Sweep Plan：`config_from_seed` 用 deterministic procedural sampling 依次抽 body_form → deck_mechanism → wheel_form → wheel_count（加权，小 N 偏多）→ palette_style → 连续 scale（先 independent：body_width/deck_height；再 equation：wheel_radius→AXLE_Z；再 inequality 投影：axle_track、mechanism footprint；最后 conditional：body_length 上限按 N、机构 anchor 区按 body_form 解析）。compatibility matrix gating 在选机构前/后剔除非法组合或 fallback。无需小型 curated 表；首版可保留 ≤2 个 regression override（仅记录已知失败回归）。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别 4×3×3×(≤6 N) 上界 216，目标 distinct ≈ 100–180（受加权 N 与 gating 影响）。低于 300 时记录该类别离散结构空间上限；不设门。
Controlled local parameterization：`body_length_scale`(conditional by N)、`body_width_scale`(independent)、`deck_height_scale`(independent)、`wheel_radius_scale`(equation→AXLE_Z)、`axle_track_scale`(inequality 不穿车身)、`mechanism_scale`(inequality footprint⊂deck)。全部在 `resolve_config` 内 clamp/派生/投影，不破坏 InterfaceSpec（甲板 mating face、axle peg 接口）、MatingContract（机构脚 embed、bead 螺纹、wheel-peg capture）、multiplicity（落地约束）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 A→B→C→N→palette→scales；加权 N（小偏多）；choices 决定 part/joint 拓扑 | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | open_racer_cockpit × bead_maze_arch → 拱脚须落 cockpit pocket 外（否则 fallback spinner/steering）；pickup_truck_bed × rooftop_spinner → post 须避开货箱墙（否则 fallback steering/arch）；其余自由 | no floating arch feet, no collision post↔bed wall, axis/ground 约束, max N=8, optional mechanism child |
| controlled local variation | 6 个连续 scale + clamp/派生/投影（见上） | proportions 变化不破坏 deck mating、axle 接口、落地、joint origin、类别 identity |
| regression overrides | none（首版）/ 仅记录已知失败回归 | previously failed / reviewer-selected only |
| random sweep | seeds 0–49 初轮，0–999 成熟审计 | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_character_form | 4 | yes | yes | |
| B deck_top_play_mechanism | 3 | yes | yes | |
| C wheel_form | 3 | yes | yes | |
| (轴) wheel_count | — | — | — | multiplicity 轴 N∈[3,8]，样本 {3,4,6} |

## Validator
- slot_choices_for_seed returns implemented module names（body_form / deck_mechanism / wheel_form）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（含加权 wheel_count）
- compatibility matrix / gating prevents illegal combos（racer×arch 浮脚、pickup×spinner 穿墙 → fallback）
- optional regression overrides are sparse and justified（首版 none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params clamped；wheel_radius→AXLE_Z equation、axle_track/mechanism_scale inequality 投影、body_length conditional by N 全在 resolve_config 解
- cross-part scale dependencies resolved in resolve_config（落地 AXLE_Z=WHEEL_R·scale、不穿车身、机构 footprint⊂deck）
- critical InterfaceSpec / MatingContract points exist：deck top mating face、axle peg 接口、机构脚 embed、bead 螺纹、wheel-peg capture
- key joints have expected type/axis/range：wheels=CONTINUOUS axis=+Y；spinner=CONTINUOUS +Z；steering=CONTINUOUS 倾斜柱轴；bead=CONTINUOUS local wire 切向；body_to_arch=FIXED
- copied objects follow naming/placement：`wheel_{i}` + `axle_{j}`，±AXLE_Y 成对，奇数加 centerline，每轮独立 CONTINUOUS

## Reject cases
- 任一 wheel `min_z > 0.004`（车轮不落地 / 悬空）——违反落地约束。
- wheel_count 为偶数却出现 centerline (y≈0) 轮，或奇数却无 centerline 轮（multiplicity 布局错误）。
- deck mechanism 脚/post 浮空于甲板之上或穿透车身（机构 anchor 未坐甲板 mating face）——尤其 racer×arch 拱脚悬在 cockpit 上、pickup×spinner post 插进货箱墙。
- 机构应有的 CONTINUOUS 关节缺失或被建成 FIXED（spinner/steering 不转、bead 不旋），或 body_to_arch 被错建成非 FIXED。
- wheel 与 body 间除「hub bore↔axle peg」「机构脚 embed」「bead↔wire」「disc↔post」之外出现未声明 overlap（穿模）。
- axle_track 过窄导致 wheel 穿入车身侧壁（axle_track inequality 未投影）。
- body_length 未随 wheel_count≥6 拉长，第 3 轴轮重叠 / 轴距塌缩。
- palette_style 未统一映射（部分 part 落到默认材质，colorway 不一致）。

## 与相邻类别的边界
- 不该混入：**Vehicle / Sports car（写实跑车，如 Diablo/Pagani fork）**——那是写实比例硬壳跑车（hollow cabin、steer-knuckle、悬挂、车门铰接），无木质 push-toy 身份、无 bead-maze/spinner/steering 玩具机构、无 character 面孔；toy_car 是 chunky 学步木玩具。
- 不该混入：**Others / 一般 wheeled container 或 trolley/cart**——它们以载物/拖拽为功能，无 driver/character 形象、无甲板顶玩法机构，且车轮非「玩具滚动 + 二级铰接玩法」语义。
- 不该混入：**Toy（非车类，如积木/拼插玩具）**——toy_car 必须保留「车身 + N 轮滚动 + 甲板机构」三层，缺车轮滚动语义即越界。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核。开放问题见下方 Return summary。 |

## 模板实现备注（可选）
- Slot C 三个 wheel module 共享同一 axle-joint helper（CONTINUOUS +Y，effort0.5/vel20）和 hub_cap/spin_marker emit；只换 wheel 几何 mesh。
- wheel_count 复制需 axle-peg helper：axle X 数 = ceil(N/2)，奇数最前轴放 centerline 轮 + 车身底挖 front-wheel 通道（参考 wheels3 L90-105）。
- captured-pin overlaps 需 element-scoped allow_overlap：每轮 `wheel_body`(或 tire_tread/rim)↔对应 `axle_{peg}`；机构脚 `arch_wire`↔`body_block`；`bead_disc`↔`arch_wire`；`disc_body`↔`spinner_post`。
- 暂不进 seed domain 的组合：无（仅 racer×arch、pickup×spinner 走 fallback gating，不硬排除）。
- bead 切向轴向量需用 spline 局部切向规范化（参考 parent `_rot_to_axis` + yaw/pitch 旋转）；首版固定 3 颗珠子。
