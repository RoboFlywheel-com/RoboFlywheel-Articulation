# Modular Spec — handheld_game_console (Sports / game console)

## 元信息
| 项 | 值 |
|---|---|
| slug | `handheld_game_console` |
| template path | `agent/templates/Sports_game_console.py` |
| test path (optional) | `tests/agent/test_handheld_game_console_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel_children 控制簇挂在单一 body/lower_panel 上 + face-button multiplicity 复制轴；clamshell 候选额外引入一条 REVOLUTE hinge 链） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category（3 parents + 6 variants，全部逐行读完） |
| source_index_policy | only adopted module sources are indexed below |

源清单（全部已读，rev_000001/model.py）：
- S1 `rec_blue-psp-style-handheld-game-console-...f576a977`（PSP parent，487 行）
- S2 `rec_purple-wireless-game-controller-...a59b32a9`（controller parent，442 行）
- S3 `rec_red-handheld-brick-game-console-...2a2ee0bb`（brick parent，351 行）
- S4 `rec_handheld_game_console_var_clamshell`（clamshell，**重做** 608 行，fork from PSP；旧版结构错误已删除重 fork：chunky deck + slim screen lid，厚度有别，铰接掀盖立起）
- S5 `rec_handheld_game_console_var_numeric_keypad`（numeric keypad，419 行，fork from brick）
- S6 `rec_handheld_game_console_var_joypad_lever`（8-way joypad lever，580 行，fork from PSP）
- S7 `rec_handheld_game_console_var_n2`（N=2 face buttons，PSP-derived）
- S8 `rec_handheld_game_console_var_n3`（N=3 face buttons，PSP-derived）
- S9 `rec_handheld_game_console_var_clamshell_ds`（dual-screen DS clamshell，655 行，fork from PSP；上盖 + 下盖各一屏，下盖控件分列第二屏左右）

## 核心身份

便携式电子游戏机/手柄：一个手持的塑料外壳，正面（或上面）排布一组**可按压/可拨动的输入控件**（方向控制 + N 个圆形动作按钮 + 可选模拟摇杆/拨杆 + 可选肩键），通常带一块内嵌显示屏。物理含义 = 单手或双手握持的交互终端，所有控件都是**真实可活动件**（按钮 PRISMATIC 下压、摇杆/拨杆 REVOLUTE 倾摆、肩键 REVOLUTE 铰接、电源开关 PRISMATIC 滑动、翻盖 REVOLUTE 开合）。

默认成熟域：手掌尺度（长边 0.16–0.17 m，厚 0.012–0.022 m）。三大形态收敛于 parent：横置 PSP slab（屏在中央，左右分握）、纵向 brick 楔形板（屏在顶端）、人体工学双握 controller（无屏）。clamshell 候选把单块板拆成铰接上下两片。

不该混入：电视游戏主机/街机柜（大体量、非手持、无握把）；遥控器/计算器（用旋钮/拨盘代替圆形动作按钮就读作非游戏机）；智能手机/平板（纯触屏、无物理动作按钮簇）。

## 槽位 + 候选模块表

### Slot A：device_archetype / body form（外壳主形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| psp_slab | S1 rec_blue...f576a977 | L60-L92（`_slab_solid`）+ L112-L191（body 装配） | eligible if compatible | 单刚体横置 slab，中央矩形屏井 cut，两端 sculpted grip 凸起；控件挂前面 z=FRONT_Z |
| controller_ergo | S2 rec_purple...a59b32a9 | L52-L97（`_body_shell` loft + grip horns）+ L174-L218（body 装配） | eligible if compatible | 人体工学双握 lofted 壳，顶面 dome loft，两侧 grip horn 下沉；无屏；控件挂顶面 z=TOP_Z |
| brick_slab | S3 rec_red...2a2ee0bb | L42-L73（`_slab_solid` 楔形）+ L88-L149（body 装配） | eligible if compatible | 纵向楔形 slab（顶端薄、底端厚），长边 X，正面 +Z；屏在 +X 顶端的 recess |
| clamshell | S4 var_clamshell | L78-L120（`_deck_solid`/`_lid_solid`）+ L177-L272（deck+lid 装配 & knuckles & screen）+ L306-L308（hinge） | eligible if compatible（gated：见兼容矩阵） | **厚下盖 deck（T≈0.022）+ 薄屏盖 lid（T≈0.012）**，两半厚度有别（不再是两条同厚扁板）；后上缘 barrel-knuckle REVOLUTE hinge（deck 出 3 / lid 出 2 交错，0–120°）；deck=控件，lid=屏 |

### Slot B：primary input cluster（方向输入 + 摇杆形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| dpad_plus_round_buttons | S1 rec_blue...f576a977 | L196-L207（dpad PRISMATIC）+ L304-L315（`_dpad_solid`）；brick 变体 S3 L151-L180（dpad REVOLUTE rocker） | eligible if compatible | 十字 dpad 在屏左/下，右侧 N 个圆动作按钮；dpad 可 PRISMATIC 下压（PSP）或 REVOLUTE rocker（brick） |
| dual_thumbsticks | S2 rec_purple...a59b32a9 | L100-L124（`_stick_post_and_dish` + `_thumbstick_mesh`）+ L222-L261（双 stick REVOLUTE tilt + dpad rocker） | eligible if compatible | 两个模拟摇杆（短柱+凹帽，REVOLUTE tilt ±0.35rad），坐在固定 dish ring 里，外加 dpad + ABXY |
| numeric_keypad | S5 var_numeric_keypad | L103-L124（`_key_cap_solid` + grid 常量）+ L198-L233（KEY_COUNT 循环 PRISMATIC） | eligible if compatible | 手机式 3×4 小键 grid（rounded-rect cap，逐个 PRISMATIC 下压），与一个 dpad 共存 |
| single_8way_joypad_lever | S6 var_joypad_lever | L108-L148（`_joystick_collar_solid` + `_joystick_lever_mesh` lathe）+ L261-L282（lever REVOLUTE tilt ±20°） | eligible if compatible | 一根高摇杆（lathe 杆身+球顶）立在 raised collar 上，REVOLUTE 8-way 倾摆，替换十字 dpad |

### Slot C：screen form（屏幕形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| landscape_lcd | S1 rec_blue...f576a977 | L116-L137（screen Box + 4 silver bezel bars）+ L84-L91（`_slab_solid` well cut） | eligible if compatible | 大横屏，居中嵌入正面 well，四条 silver bezel 框 |
| square_lcd | S3 rec_red...2a2ee0bb | L76-L107（`_recess_box` + `_grid_mesh`）+ L124-L145（bezel + screen_face + pixel_grid） | eligible if compatible | 小近正方屏，gray bezel + dark screen_face + 绿色 pixel grid，在 +X 顶端 |
| no_screen | S2 rec_purple...a59b32a9 | L199-L205（logo disc，无 screen part） | eligible if compatible（gated：见兼容矩阵） | 无显示屏，仅中央 logo disc/menu pill 作 trim |
| dual_screen | S9 var_clamshell_ds | L115-L135（`_lid_shell_solid` 上屏 well）+ L197（lower_screen）+ L288（upper_screen）+ L329-L330（hinge） | eligible if compatible（gated：仅 clamshell；与 numeric_keypad 互斥） | DS 双屏翻盖：上盖一屏 + 下盖一屏，下盖 dpad/round 按钮分列第二屏左右 |

Slot C：landscape/square/no_screen 三档由三个 parent 覆盖；dual_screen 由 S9（DS 翻盖）覆盖，仅 clamshell 合法。不降级。

## 槽位图（slot graph）

pattern: mixed

```
Slot A (body / lower_panel = ROOT)
  ├─[fixed visual]──────────────────────────────► Slot C (screen)  [屏/bezel 为 body 上的 fixed visual；clamshell 时屏移到 upper_panel]
  ├─[parallel children, 都挂在 body 前控制面]────► Slot B (input cluster)
  │     • dpad / 摇杆 / 拨杆 / 键 → 各自独立 joint，origin 贴前控制面 (z≈FRONT_Z/TOP_Z)
  ├─[multiplicity loop]──────────────────────────► face_btn_{i}  (i=0..N-1)  每个 PRISMATIC press -Z
  └─[fixed top-edge hinge]───────────────────────► shoulder_l / shoulder_r  (REVOLUTE，可选)

clamshell only（deck=厚下盖 root，lid=薄屏盖 child）:
Slot A.deck(lower) --[REVOLUTE about ±X, barrel knuckle 交错 3+2, 0–120°]--> Slot A.lid(upper)(carries Slot C 屏)
  └─ dual_screen 时 deck 额外承一块 deck_screen（下盖中央，dpad/round 按钮分列其左右）
```

跨 slot 连接接口：
- **控制簇 ↔ body**：mating face = body 前控制面（PSP/brick z=FRONT_Z/TOP_Z；controller z=TOP_Z；clamshell lower z=FRONT_Z_L）。anchor = 各控件 (x,y) 中心。joint origin 贴前控制面 + 微正 z 偏移（FRONT_Z+0.001）。dpad/button = PRISMATIC axis (0,0,-1)；摇杆/拨杆/nub = REVOLUTE tilt axis (1,0,0) 或 (0,1,0)。
- **face_btn multiplicity ↔ body**：每个按钮独立 PRISMATIC，axis (0,0,-1)，origin = (FACE_CX+ox, FACE_CY+oy, FRONT_Z+0.001)。互不联动。
- **shoulder ↔ body**：hinge line 沿 X 在顶后缘，REVOLUTE axis (1,0,0)，range 0–18°。可选（controller 用 trigger paddle，range 0–0.35rad）。
- **clamshell hinge**：deck（厚下盖）后上缘 ↔ lid（薄屏盖）后下缘，mating face = 共享后边缘线，anchor = barrel knuckle 轴心，consumer joint = REVOLUTE，axis = (∓1,0,0)（共享 X 边；S4 用 -X、S9 用 +X，模板内统一一向），limits [0, ≈2.09rad =120°]。deck 出 3 knuckle、lid 出 2 knuckle，沿 X 交错共轴。deck 厚度 T_DECK≈0.022、lid 厚度 T_LID≈0.012（deck 必 ≥1.4×lid）。
- **joypad_lever / thumbstick ↔ body**：body 上 raised collar/dish ring（固定 visual）= 承托面，lever/stick 的 REVOLUTE 原点贴 collar 顶面（z = FRONT_Z + COLLAR_H）。

互斥/可选/派生：
- Slot A=clamshell 时 Slot C 屏移到 lid（upper），且 no_screen 不合法（翻盖却无屏读作空壳，gated→landscape）。
- Slot C=dual_screen 仅 Slot A=clamshell 合法（slab 双屏读错 → 非 clamshell 派生回 landscape）；dual_screen 时 deck 中央承第二屏，与 numeric_keypad（占 deck 中盘）互斥 → 派生回 dpad+round。
- Slot A=controller_ergo 与 Slot C∈{landscape_lcd, square_lcd, dual_screen}：加大屏会读成掌机而非手柄 → gated 排除，controller 强制 no_screen。
- Slot C=no_screen 仅 controller_ergo 合法。
- shoulder/trigger 为可选 moving child；缺失不破坏类别 identity（clamshell lid 掀盖故无 shoulder）。

## 每槽位 Module Emits / Interfaces

### Slot A / module psp_slab
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（shell mesh + 屏/bezel/speaker/start-select-home/logo/nub_collar/nub_post fixed visuals） | S1 / L112-L191 |
| internal joints | 无（body 是 root，内部全 fixed visual） | S1 / L112-L191 |
| upstream interface | root，无 parent | S1 / L99-L113 |
| downstream interface | 前控制面 z=FRONT_Z（+0.011），控件 anchor=(x,y) 中心；顶后缘 hinge line 供 shoulder | S1 / L52-L58, L266-L267 |

### Slot A / module controller_ergo
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（lofted shell + 双 stick dish ring + menu pill + logo glow + grip glow strip） | S2 / L174-L218 |
| internal joints | 无 | S2 / L174-L218 |
| upstream interface | root | S2 / L163-L176 |
| downstream interface | 顶控制面 z=TOP_Z(0.030)；dish ring 承托摇杆；顶前缘 z=0.018 供 trigger | S2 / L37-L50, L300-L313 |

### Slot A / module brick_slab
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（楔形 slab mesh + bezel/screen_face/pixel_grid fixed visuals） | S3 / L120-L149 |
| internal joints | 无 | S3 / L120-L149 |
| upstream interface | root | S3 / L110-L122 |
| downstream interface | 正控制面 z=TOP_Z（THK/2=0.009）；屏在 +X 顶端，控件在 -X 底端 | S3 / L31-L40 |

### Slot A / module clamshell
| emits | 描述 | 来源 |
|---|---|---|
| parts | `deck`(root, 厚 shell T≈0.022 + 控件 trim + 3 hinge knuckle)、`lid`(薄 shell T≈0.012 + screen + 2 hinge knuckle) | S4 / L78-L120, L177-L272（DS：S9 / L81-L135, L190-L313） |
| internal joints | `deck_to_lid` REVOLUTE axis(∓1,0,0) origin 共享后上缘 range[0,120°]；模板内统一掀向用户 | S4 / L306-L308（S9 / L329-L330） |
| upstream interface | deck = root | S4 / L177-L181 |
| downstream interface | deck 前面 z=FRONT_Z 挂控件 + dual_screen 第二屏；lid 内面承屏；后上缘 hinge line + 交错 barrel knuckle | S4 / L42-L72 |

### Slot B / module dpad_plus_round_buttons
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dpad`（十字 cross mesh） | S1 / L196-L198, L304-L315 |
| internal joints | `body_to_dpad` PRISMATIC axis(0,0,-1) range[0,0.0025]（PSP）；或 `dpad_rocker` REVOLUTE axis(0,1,0) range[-0.2,0.2]（brick） | S1 / L199-L207；S3 / L170-L180 |
| upstream interface | body 前控制面，anchor=(DPAD_CX, DPAD_CY) | S1 / L52-L53 |
| downstream interface | 右侧留 face-button 簇空间（multiplicity 轴） | S1 / L54-L55 |

### Slot B / module dual_thumbsticks
| emits | 描述 | 来源 |
|---|---|---|
| parts | `left_thumbstick`、`right_thumbstick`（post+cap+rim）；body 上 dish ring 为 fixed | S2 / L100-L124, L222-L245 |
| internal joints | `body_to_left/right_thumbstick` REVOLUTE axis(0,1,0) range[-0.35,0.35]；外加 `body_to_dpad` rocker | S2 / L235-L261 |
| upstream interface | dish ring 承托面 z=TOP_Z，anchor=L_STICK/R_STICK | S2 / L40-L41 |
| downstream interface | 右上 ABXY 簇（multiplicity 轴）共存 | S2 / L44-L46 |

### Slot B / module numeric_keypad
| emits | 描述 | 来源 |
|---|---|---|
| parts | `key_{i}` i=0..KEY_COUNT-1（默认 4×3=12，rounded-rect cap）+ 一个 `dpad` | S5 / L198-L233 |
| internal joints | `key_{i}_press` PRISMATIC axis(0,0,-1) range[0,0.002]；`dpad_rocker` REVOLUTE | S5 / L222-L233 |
| upstream interface | body 控制面，grid center=(KEY_GRID_CX,KEY_GRID_CY)，行列等距 pitch | S5 / L115-L124 |
| downstream interface | keypad 与 dpad 沿 Y 分置（互不重叠） | S5 / L209-L210 |

### Slot B / module single_8way_joypad_lever
| emits | 描述 | 来源 |
|---|---|---|
| parts | `joystick`（lathe 杆身+球顶）；body 上 `joystick_collar` 为 fixed | S6 / L108-L148, L261-L266 |
| internal joints | `body_to_joystick` REVOLUTE axis(1,0,0) range[-20°,20°]（8-way tilt） | S6 / L270-L282 |
| upstream interface | collar 顶面承托，pivot 在 z=FRONT_Z+COLLAR_H | S6 / L275-L276 |
| downstream interface | 替换十字 dpad；右侧 face-button 簇照常 | S6 / L54-L57 |

### Slot C / module landscape_lcd
| emits | 描述 | 来源 |
|---|---|---|
| parts | `screen`(Box) + bezel_top/bot/left/right（silver bars），均为 body fixed visual | S1 / L116-L137 |
| internal joints | 无 | — |
| upstream interface | body 正面中央 well（_slab_solid cut），anchor=(SCREEN_CX,SCREEN_CY) | S1 / L84-L91 |
| downstream interface | screen 顶 z ≤ FRONT_Z（recessed） | S1 / L116-L121 |

### Slot C / module square_lcd
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bezel`、`screen_face`、`pixel_grid`（body fixed visual） | S3 / L124-L145 |
| internal joints | 无 | — |
| upstream interface | body 顶端 recess（_recess_box cut），anchor=(0.045,0.0) | S3 / L76-L85 |
| downstream interface | screen_face 顶 < bezel 顶，且 screen 落在 bezel footprint 内 | S3 / L132-L138 |

### Slot C / module no_screen
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无 screen part；中央 logo disc / menu pill 作 trim（body fixed visual） | S2 / L190-L205 |
| internal joints | 无 | — |
| upstream interface | body 顶面中央，仅 trim | S2 / L199-L205 |
| downstream interface | 无屏接口；控件占满控制面 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| device_archetype (Slot A) | enum | {psp_slab, controller_ergo, brick_slab, clamshell} | psp_slab | choice | deterministic procedural sampler；门控见兼容矩阵 | Slot A table |
| input_cluster (Slot B) | enum | {dpad_plus_round_buttons, dual_thumbsticks, numeric_keypad, single_8way_joypad_lever} | dpad_plus_round_buttons | choice | sampler；与 Slot A 兼容门控 | Slot B table |
| screen_form (Slot C) | enum | {landscape_lcd, square_lcd, no_screen, dual_screen} | landscape_lcd | conditional | no_screen 仅当 Slot A=controller_ergo；dual_screen 仅当 Slot A=clamshell；clamshell 强制有屏 | Slot C table |
| face_button_count (N) | int (multiplicity) | {2,3,4,6}，采样域 [2,8] | 4 | conditional | placement 表随 N 切换；见 Multiplicity 节 | S1/S3/S7/S8 |
| palette_style | enum | {glossy_blue_psp, brick_red_yellow, charcoal_pro, retro_cream, mint_translucent, neon_arcade} | glossy_blue_psp | choice | 每 seed 抽一档，决定 shell/button/accent/screen 材质 RGBA | S1-S6 materials |
| body_width_scale | float | [0.90, 1.12] | 1.0 | independent | 范围内独立采样后 clamp（slab 宽/controller span） | S1 L42；S2 L62 |
| body_thickness_scale | float | [0.85, 1.15] | 1.0 | independent | 独立采样 clamp（slab 厚 T/THK） | S1 L44；S3 L35 |
| screen_size_scale | float | derived | 1.0 | equation | `= 0.92·body_width_scale`（屏宽随壳宽，保持 bezel 余量） | S1 L47-L48 |
| (—) | constraint | — | — | inequality | `screen_well_half_w + bezel_margin ≤ (W·body_width_scale)/2 − grip_clearance`；违反则回缩 screen_size_scale | S1 L84-L91, L124 |
| (—) | constraint | — | — | inequality | face cluster 半径 `R_cluster(N) + BTN_R ≤ grip_half_w − edge_margin`（右握把不溢出）；违反回缩 cluster pitch | S1 L213-L218；S8 L214 |
| (—) | constraint | — | — | inequality | clamshell 闭合（q=0）：lid 折平贴 deck 顶面，控件凸起/第二屏被掀盖捕获（allow_overlap）；开到 120° 时 lid AABB 顶升 ≥0.01（屏立起朝用户） | S4 deck_to_lid hinge |
| face_cluster_pitch_scale | float | [0.85, 1.20] | 1.0 | conditional | 上限随 N 收紧（N=6 时上限 1.05，避免 2×2+下排溢出 grip） | S1 L213-L218；S3 L192-L202 |
| dpad_arm_scale | float | [0.85, 1.15] | 1.0 | independent | 独立采样 clamp（十字臂长） | S1 L307-L308 |
| hinge_open_limit | float | [110°, 135°] | 120° | conditional | 仅 clamshell；REVOLUTE upper limit (default 120°) | S4 hinge emit |
| deck_thickness vs lid_thickness | float | deck ≈0.023·st / lid ≈0.011·st（lid clamp [0.009,0.014]） | — | conditional | 仅 clamshell；deck 必须 ≥1.4×lid（厚下盖+薄屏盖，读作翻盖而非两条同厚板） | S4 deck/lid |

连续尺寸采样契约：先采 independent（body_width/thickness、dpad_arm）→ equation 派生 screen_size → inequality 投影回缩（屏/簇/闭合）→ conditional 解析（screen_form、face_cluster_pitch 上限、hinge_open_limit）。

## Multiplicity / Copy Logic

**单轴 multiplicity：face_button_count（右侧圆形动作按钮数）**

- `count_param`：`face_button_count`（N）
- `N_range`：产品域 `[2, 8]`（真实手柄圆按钮常 2–6，留余量到 8）；测试偏小，sweep 上限 8
- sampling domain（权重档）：小 N 高频、大 N 稀有。建议 N=2 偏多、N=3/4 常见、N=6 中等、N=7/8 稀有。N=4（diamond）、N=6（2×2+下排）为最典型 → 给较高权重；N=2（横排对）、N=3（三角）次之；N=5/7/8 由通用环形/网格 placement 兜底但低频。
- copied object：单个圆形动作按钮 = 共享 dome+stem helper（PSP 风 `_face_button_geometry`，S7 L290+）或 cylinder cap（brick 风，S3 L206-L214）。
- naming：`face_btn_{i}` for i in range(N)（PSP/clamshell/n2/n3 命名）；brick 系内部 `btn_{i}`，模板统一对外 `face_btn_{i}`。
- placement（随 N 切换的 placement 表 / 函数）：
  - N=2：横排一对，`ox=(i-0.5)·spacing`（S7 L213-L215）
  - N=3：等边三角 120° 环形，`angle=90°+i·120°`（S8 L213-L218）
  - N=4：diamond（上/右/下/左），offsets 表（S1 L213-L218）
  - N=6：2×2 + 下排两小键（big_specs+small_specs，S3 L192-L202）；模板化为 2 列 ×3 行 或 diamond+2
  - N=5/7/8：通用环形等角 / 半 diamond 兜底
- joint policy：每个按钮独立 PRISMATIC，axis(0,0,-1)，统一 lower=0、upper≈0.0015–0.002，effort/velocity 一致；互不联动。
- source/gating：N 复制对所有 Slot A 合法（PSP/controller/brick/clamshell 都有右侧动作按钮簇）。建议 fork 自 PSP 的纯 `for i in range(N)` 循环（干净，N 变体只改循环上界 + placement 表）；brick parent 用手写 big/small_specs（非纯循环），不作为复制 helper 主源。

dpad/摇杆/拨杆/键盘 keys 属 Slot B 模块内部结构，不暴露为模板级 `*_count`（numeric_keypad 的 KEY_COUNT 是模块内部固定 4×3，非主 multiplicity 轴；如需可作 Slot B 内 sub-variant，本批不暴露）。

## 拓扑多样性审计

总组合数（粗算，扣除非法组合前）：
- Slot A × Slot B × Slot C × N-samples = 4 × 4 × 4 × |{2,3,4,6,(5,7,8)}≈6| = 384（Slot C 增 dual_screen）。
- 扣除兼容矩阵非法组合（clamshell×no_screen、controller×有屏、controller×numeric_keypad、dual_screen×非clamshell、dual_screen×numeric_keypad 等）后合法组合仍 ≈180+。

理由：仅 Slot A(4)×Slot B(4)=16 个 archetype×input 组合（即便全忽略 Slot C 与 N）就远超 10；叠加 Slot C(3) 与 N 复制后 distinct topology 充裕。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 用 deterministic 加权采样依次定 Slot A → Slot B → Slot C（受 conditional 门控）→ N（加权小 N 偏多）→ palette_style → 连续 scale（按采样契约）。兼容矩阵在采样后 gate/回退非法组合（如抽到 controller_ergo 则 Slot C 强制 no_screen；抽到 clamshell 则 Slot C 落 landscape/square/dual_screen，且 clamshell 群体内对 dual_screen 加权重采样以保证 DS 形态出现在 pool 中；dual_screen 仅 clamshell 合法，dual_screen 时若 input=numeric_keypad 改用 dpad+round；no_screen 仅 controller）。少量 regression overrides 仅用于已知失败 seed。random sweep：seeds 0–49 初轮、0–999 成熟审计。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；合法组合空间 ≈150，低于 300 时记录该类别离散结构空间上限；不设门。
Controlled local parameterization：body_width_scale [0.90,1.12] independent、body_thickness_scale [0.85,1.15] independent、dpad_arm_scale [0.85,1.15] independent、screen_size_scale = 0.92·body_width_scale (equation)、face_cluster_pitch_scale [0.85,1.20] conditional（N=6 上限 1.05）、hinge_open_limit [110°,135°] conditional（仅 clamshell）。inequality：屏 well 不溢出壳、face cluster 不溢出右握把、clamshell 闭合贴合。全在 `resolve_config` 求解；不破坏 InterfaceSpec（控制面 anchor、collar/dish 承托、hinge 轴）/ multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | A→B→C(conditional)→N(加权小 N 偏多)→palette→scales；deterministic | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | clamshell×no_screen 非法→landscape；controller×{landscape,square,dual}_lcd 非法→强制 no_screen；no_screen 仅 controller；dual_screen 仅 clamshell（非 clamshell→landscape）；dual_screen×numeric_keypad→dpad+round（让出 deck 中央给第二屏）；其余合法 | no floating screen、屏穿模、闭合碰撞、簇溢出 grip、deck 双控件不挤第二屏、可选 shoulder 缺失 |
| controlled local variation | body/screen/dpad/cluster scale 全 clamp/derived，受不等式回缩 | proportions 变化不破 bezel 余量、握把不溢出、hinge 闭合、joint origin 贴面 |
| regression overrides | none（首版）/ 仅记录已知失败 seed | previously failed cases only |
| random sweep | seeds 0–49 初轮，0–999 成熟审计 | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A device_archetype | 4 | yes | yes | psp/controller/brick/clamshell |
| B input_cluster | 4 | yes | yes | dpad+buttons / sticks / keypad / joypad_lever |
| C screen_form | 3 | yes | yes | landscape / square / no_screen |

## Validator
- slot_choices_for_seed returns implemented module names（Slot A/B/C + N + palette）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating prevents illegal combos（clamshell×no_screen、controller×有屏、no_screen 非 controller）
- optional regression overrides are sparse and justified（首版 none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params clamped；屏/簇/闭合不等式在 resolve_config 求解
- cross-part scale deps（screen_size equation、cluster/well/闭合 inequality、screen_form/pitch/hinge conditional）resolved in resolve_config
- critical InterfaceSpec/MatingContract 点存在：控制面 anchor、collar/dish 承托面、clamshell hinge knuckle 轴
- key joints type/axis/range：face_btn PRISMATIC (0,0,-1) [0,~0.0015-0.002]；摇杆/拨杆/nub REVOLUTE tilt；shoulder REVOLUTE [0,18°]；clamshell hinge REVOLUTE [0,120°]；brick dpad rocker REVOLUTE
- copied face_btn_{i} follow naming（i in range(N)）+ placement（N→layout 表）policy

## Reject cases
1. face_btn 数与 N 不符（缺循环上界 / 漏 face_btn_{N-1}），或两个按钮共用一条 joint（应各自独立 PRISMATIC）。
2. clamshell 闭合时 upper_panel 与 lower_panel 不贴合或穿透（违反闭合不等式），或开到 120° 屏不朝用户。
3. screen well/bezel 溢出 shell 边缘或穿到 grip（违反屏不等式），square_lcd 的 screen_face 跑出 bezel footprint。
4. controller_ergo 配了大 landscape/square 屏（出类目，读成掌机），或 clamshell 选了 no_screen（空壳）。
5. 摇杆/拨杆 REVOLUTE 原点不在 collar/dish 顶面（pivot 悬空），或 lever 球顶没高出 collar ≥0.02（读不出摇杆）。
6. face cluster 半径随 N 增大溢出右握把（N=6 未收紧 pitch 上限），按钮叠到 dpad/屏上。
7. 把圆形动作按钮整体换成单旋钮/拨盘（读作收音机/计算器，出类目）。
8. shoulder/trigger 铰链轴方向错（应沿顶缘 X），或正向 q 不把触发件压下/拉起。

## 与相邻类别的边界
- 不该混入：电视游戏主机 / 街机柜（大体量、非手持、无握把与手持控件簇）。
- 不该混入：遥控器 / 计算器（用旋钮/拨盘或纯数字键代替圆形动作按钮簇 → 失去游戏机 identity；numeric_keypad 候选必须与 dpad 共存以保留方向输入）。
- 不该混入：智能手机 / 平板（纯触屏、无物理 dpad/动作按钮/摇杆活动件）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核。开放问题见下。 |

## 模板实现备注（可选）
- 共享 helper：face button dome+stem（PSP 风，跨 N 复用）；rounded slab/panel（`_deck_solid`/`_lid_solid`(S4)、`_rounded_slab`(模板) 供 clamshell deck+lid；psp slab 另一 helper）；dpad cross；shoulder bar。
- InterfaceSpec 重点：clamshell barrel knuckle（lower 3 / upper 2 交错，captured-pin 风格 overlap，需 element-scoped allow_overlap 逐对声明，见 S4 L430-L453）；摇杆/拨杆 collar/dish 承托面（allow_overlap stem↔collar）。
- captured-pin overlap：clamshell hinge knuckle 互嵌、闭合时 upper shell 盖住 lower 控件凸起（S4 大量 allow_overlap，复制到模板每个 clamshell+控件组合）。
- 暂不进入 seed domain 的组合：controller_ergo×有屏、clamshell×no_screen（兼容矩阵 gate）。

## 开放问题（for review）
1. N=5/7/8 的通用兜底 placement（环形等角 vs 网格）是否需要在首版实现，还是先只产 {2,3,4,6} 四档采样、把 [5,7,8] 留作低频兜底？
2. brick dpad 用 REVOLUTE rocker、PSP 用 PRISMATIC press —— dpad 动作语义是否随 Slot A 绑定（建议绑定：slab/brick→press/rocker，clamshell→press），还是作为 Slot B 内独立 sub-choice？
3. numeric_keypad 的 KEY_COUNT（4×3）是否要暴露为第二条 multiplicity 轴（3×3/3×4），还是固定为模块内部常量（本批建议固定）。
