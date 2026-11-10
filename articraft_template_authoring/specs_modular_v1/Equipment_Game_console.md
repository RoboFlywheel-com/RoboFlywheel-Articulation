# Arcade Cabinet Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `arcade_cabinet` |
| template path | `agent/templates/Equipment_Game_console.py` |
| test path | `tests/agent/test_arcade_cabinet_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | parent `a5689b50` + 8 planned fork variants (Slot A body ×3, Slot B control ×3, station N ×2) |
| samples_adopted_as_module_sources | 9 |
| samples_read_but_not_adopted | 0 |
| source_index_policy | all adopted; each candidate maps to exactly one fork record |

数据根来源说明（重要）：本类候选**不是** arti-template 10K 正式数据集成员。它们是 `articraft_data` 仓库内、由 `picture` 子类 `Equipment / Game console` 扩展产生的 **workbench-only fork 记录**（`collections=['workbench']`，未 promote）。全部 fork 自单一母资产 `a5689b50`，逐一 on-disk 验证过（last compile = success，≥1 非 fixed 关节）。引用一律写成 `data/records/<id>/revisions/rev_000001/model.py:Lx-Ly`，行号来自实读源码。

- adopted as module sources（record_id → 用途）：
  - `rec_build-a-realistic-articulated-3d-model-of-a-game_20260609_180045_745274_a5689b50`（parent）→ Slot A `wedge_cabinet` 基线 + Slot B `ball_top_joystick` 基线 + N=1 手写单站位
  - `rec_game_console_var_body_upright_box` → Slot A `upright_box`
  - `rec_game_console_var_body_cocktail` → Slot A `cocktail_flattop`
  - `rec_game_console_var_body_bartop_crown` → Slot A `bartop_crown`
  - `rec_game_console_var_ctrl_trackball` → Slot B `trackball`
  - `rec_game_console_var_ctrl_spinner` → Slot B `spinner_knob`
  - `rec_game_console_var_ctrl_slider` → Slot B `linear_slider`
  - `rec_game_console_var_stations_x2` → multiplicity copy-logic 源（N=2）
  - `rec_game_console_var_stations_x4` → multiplicity copy-logic 源（N=4，首选）

## 核心身份

Arcade cabinet 是**站立/台面式街机柜**整柜：一只静态柜体（root part `cabinet_body`）承载显示屏（`screen_glass` + bezel/marquee）和一块倾斜或水平的控制面，控制面上立起一个或多个可动主控制机构（球头摇杆 / 轨迹球 / 旋钮 / 滑块）。可动语义集中在控制机构上——典型 closed pose 是摇杆居中、球/旋钮静止、滑块归中。柜体本身不动，作为 parent visual 承托所有控制座（`joystick_collar` / `trackball_cup_liner` / `spinner_bearing` / `slider_slot_floor`）。

边界：
- 不是掌机（handheld game console / PSP / 手柄）：街机柜是落地或台面整柜，有屏脸、踏板/底座、独立控制面；掌机是握持式一体壳，无落地柜体。
- 不是 casino / slot machine：街机柜核心是玩家输入控制机构（摇杆/球/钮/滑块）+ 游戏屏，不应有拉杆+滚轮卷筒+投币赔付语义。

## 采用源码索引（Adopted Source Index）
| source_id | record_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_build-...745274_a5689b50` | `data/records/rec_build-a-realistic-articulated-3d-model-of-a-game_20260609_180045_745274_a5689b50/revisions/rev_000001/model.py:L88-L345` | wedge 楔形柜体 + 斜置控制带（Slot A 基线） |
| S1b | 同上 | `.../a5689b50/.../model.py:L298-L399` | 球头摇杆 + collar 座 + REVOLUTE 关节（Slot B 基线） |
| S2 | `rec_game_console_var_body_upright_box` | `data/records/rec_game_console_var_body_upright_box/revisions/rev_000001/model.py:L90-L243` | 直立矩形箱体 + 竖直平屏 + 水平挑出控制搁板 |
| S3 | `rec_game_console_var_body_cocktail` | `data/records/rec_game_console_var_body_cocktail/revisions/rev_000001/model.py:L80-L238` | 低宽台面式柜 + 顶台平嵌屏 + 四边轨 + 顶台控制簇 |
| S4 | `rec_game_console_var_body_bartop_crown` | `data/records/rec_game_console_var_body_bartop_crown/revisions/rev_000001/model.py:L93-L243` | bartop 紧凑柜 + 竖屏脸 + 上方弧形 marquee 顶冠 |
| S5 | `rec_game_console_var_ctrl_trackball` | `data/records/rec_game_console_var_ctrl_trackball/revisions/rev_000001/model.py:L296-L407` | 轨迹球嵌红板凹杯 + REVOLUTE 自旋 |
| S6 | `rec_game_console_var_ctrl_spinner` | `data/records/rec_game_console_var_ctrl_spinner/revisions/rev_000001/model.py:L178-L431` | 滚花旋钮立于轴承 + CONTINUOUS 连续旋转 |
| S7 | `rec_game_console_var_ctrl_slider` | `data/records/rec_game_console_var_ctrl_slider/revisions/rev_000001/model.py:L319-L411` | 拇指滑块沿红板通槽 + PRISMATIC |
| S8 | `rec_game_console_var_stations_x2` | `data/records/rec_game_console_var_stations_x2/revisions/rev_000001/model.py:L335-L468` | N=2 站位循环源（内联 `range(2)`） |
| S9 | `rec_game_console_var_stations_x4` | `data/records/rec_game_console_var_stations_x4/revisions/rev_000001/model.py:L205-L507` | N=4 站位循环源（`STATION_COUNT` + helper，首选 copy-logic 源） |

## 槽位 + 候选模块表

### Slot A：body / cabinet form（柜体形态——承载屏与控制面的根 part）
| module_name | 5_star_source (record_id) | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `wedge_cabinet`（基线） | `rec_build-...745274_a5689b50` | L88-L345 | eligible if compatible | YZ `polyline` 楔形：竖后背 + 斜上前脸（屏）+ 竖下前脸检修板；斜置控制带（pitch≈`atan2`）；`_build_cabinet_shell` / `_sloped_face_geometry` / `cabinet_shell` / `base_pedestal` / `screen_bezel`+`screen_glass`+`game_over_text` |
| `upright_box` | `rec_game_console_var_body_upright_box` | L90-L243 | eligible if compatible | 直立矩形箱体（矩形 side）+ 竖直平前脸屏（`_front_screen_geometry`, roll=π/2）+ 从前脸水平挑出的 `control_shelf` + `shelf_front_lip` |
| `cocktail_flattop` | `rec_game_console_var_body_cocktail` | L80-L238 | eligible if compatible | 低矮宽台面（CAB_W≈0.78, CAB_H≈0.32），屏 `screen_glass` 平嵌 +Z 顶台（`deck_z`），四边 `top_rail_0..3` 黑边轨，控制簇置顶台屏前；`_rect_frame` / `_keypad_geometry` helper |
| `bartop_crown` | `rec_game_console_var_body_bartop_crown` | L93-L243 | eligible if compatible | bartop 紧凑柜：竖直屏脸（`_screen_face_geometry`, roll=-π/2）+ 上方 `threePointArc` 弧形 `curved_marquee_crown` 顶冠（取代楔形平顶）；`_build_curved_marquee_crown` helper |

### Slot B：primary control mechanism（主控制机构——挂在控制面上的可动件）
| module_name | 5_star_source (record_id) | model.py:Lx-Ly | sampling eligibility | 结构特征 + joint 策略 |
|---|---|---|---|---|
| `ball_top_joystick`（基线） | `rec_build-...745274_a5689b50` | L298-L399 | eligible if compatible | part `joystick`（`joystick_shaft`/`joystick_boot`/`joystick_ball`）经红板固定座 `joystick_collar` 立起；joint `panel_to_joystick` **REVOLUTE** axis=(-1,0,0) 前后摆 limits ±0.45 |
| `trackball` | `rec_game_console_var_ctrl_trackball` | L296-L407 | eligible if compatible | part `trackball`（`trackball_sphere`）嵌入红板 `cutThruAll` 凹杯 `trackball_cup_liner`+`trackball_bezel_cup`；joint `plate_to_trackball` **REVOLUTE** axis=(0,0,1) 原地自旋 limits ±π（无柄无倾） |
| `spinner_knob` | `rec_game_console_var_ctrl_spinner` | L178-L431 | eligible if compatible | part `spinner`（`spinner_stem`/`spinner_body` via `_build_knurled_spinner_body`）立于固定座 `spinner_bearing`；joint `panel_to_spinner` **CONTINUOUS** axis=(0,0,1) 无止挡连续旋转（注：是 continuous 非 revolute） |
| `linear_slider` | `rec_game_console_var_ctrl_slider` | L319-L411 | eligible if compatible | part `slider`（`slider_runner`/`slider_thumb`）沿红板 `cut` 通槽座 `slider_slot_floor` 左右滑；joint `panel_to_slider` **PRISMATIC** axis=(1,0,0) limits ±0.018 |

约束说明：每个 candidate 结构差异显著（楔形 vs 直箱 vs 台面 vs 弧冠；REVOLUTE 摆 vs REVOLUTE 自旋 vs CONTINUOUS vs PRISMATIC），非纯尺寸/颜色变体。Slot A、Slot B 各 4 个候选，满足 3-6 目标。

## 槽位图（slot graph）

pattern: `mixed`（body 形态槽 + control 机构槽 + 玩家站位 multiplicity）

```text
[Slot A body/cabinet]  --static FIXED, 控制座 visual on control face-->  控制面(band / control_shelf / deck)
        |                                                                       |
        | (multiplicity axis: station_count N, copy 整站位)                      |
        v                                                                       v
   每站位红板/collar 沿 X 等距投点  --consumer joint per station-->  [Slot B control mechanism × N]
```

跨 slot 连接：
- **控制座 = 承托面**：`joystick_collar` / `trackball_cup_liner`+bezel / `spinner_bearing` / `slider_slot_floor` 是 Slot A body 上的固定 visual；Slot B 子可动件原点贴座顶面。captured fit（boot/shaft 入 collar、ball 入 cup、stem 入 bearing、runner 入 slot）需局部 `allow_overlap` 声明。
- **控制面定义**：wedge/bartop = 倾斜控制带（`band_y`/`band_z`，法向含 `band_face_pitch≈-0.18`，joint origin rpy=(band_face_pitch,0,0)）；upright_box = 水平 `control_shelf` 顶面；cocktail = `deck_z` 水平顶台。
- **跨 slot joint**：mating face = 控制面，anchor = 红板(x,y)中心，joint origin 贴面法向。joint type 随 Slot B 变（REVOLUTE / CONTINUOUS / PRISMATIC），不可强行统一。
- **互斥/可选**：N（station multiplicity）是独立轴；每站位是一份完整 Slot B 拷贝。Slot A 与 Slot B 正交，组合留给 compatibility matrix。

## 每槽位 Module Emits / Interfaces

### Slot A / body（以 wedge_cabinet 为例，其余 body candidate 同构）
| emits | 描述 | 来源 |
|---|---|---|
| parts | root part `cabinet_body`：`cabinet_shell` + `base_pedestal` + `screen_bezel`/`screen_glass` + marquee/`game_over_text` + 控制带 keypad/`control_red_plate` + 控制座 visual | S1 / model.py:L88-L345 |
| internal joints | 无（柜体全静态，控制座为 parent visual，不是独立 part） | S1 / model.py:L183-L345 |
| upstream interface | 落地：`base_pedestal` 触地面，root part 无 parent | S1 / model.py:L196-L198 |
| downstream interface | 控制面（band/shelf/deck）法向 + 控制座顶面，供 Slot B mate；anchor = 红板中心 | S1 / model.py:L253-L345 |

### Slot B / control（以 ball_top_joystick 为例）
| emits | 描述 | 来源 |
|---|---|---|
| parts | movable part `joystick`（shaft/boot/ball）；固定座 `joystick_collar` 归属 parent body | S1 / model.py:L298-L386 |
| internal joints | 无（机构是单刚体 + 一个 consumer joint） | S1 / model.py:L347-L386 |
| upstream interface | 子件原点贴控制座顶面，captured fit 入 collar bore（`allow_overlap`） | S1 / model.py:L347-L386 |
| downstream interface | consumer joint `panel_to_joystick` REVOLUTE axis=-X limits ±0.45，origin rpy=band_face_pitch | S1 / model.py:L387-L399 |

其余 Slot B 模块的 consumer joint：trackball = REVOLUTE axis=Z ±π（L398-L407）；spinner = **CONTINUOUS** axis=Z 无止挡（L416-L423）；slider = PRISMATIC axis=X ±0.018（L402-L410）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_style` | enum | `wedge_cabinet` / `upright_box` / `cocktail_flattop` / `bartop_crown` | — | choice | deterministic procedural sampler 选择 | Slot A 表 |
| `control_style` | enum | `ball_top_joystick` / `trackball` / `spinner_knob` / `linear_slider` | — | choice | deterministic procedural sampler 选择 | Slot B 表 |
| `station_count` | int | `[1, 6]` | 1 | independent | 加权采样（小 N 高频，≥5 稀有）；每站位一份 Slot B 拷贝 | S1/S8/S9 |
| `cab_width_scale` | float | [0.85, 1.25] | 1.0 | conditional | `CAB_W` 下限随 `station_count` 升高：`CAB_W ≥ station_count·station_spacing + 2·deck_margin`（参 x4 `CAB_W=0.900`） | S9 / model.py:L37,L211-L215 |
| `station_spacing_scale` | float | [0.85, 1.15] | 1.0 | independent | 在范围内独立采样后 clamp（基线 spacing≈0.190） | S8 / model.py:L336,L351 |
| `control_travel_scale` | float | [0.8, 1.2] | 1.0 | independent | 缩放 joystick ±0.45 / slider ±0.018 行程；trackball/spinner 不受限 | S1/S7 |
| (—) | constraint | — | — | inequality | 站位投点须落在控制面内且互不穿模：`Σ station 占宽 ≤ 控制面可用宽`，违反时回缩 `station_spacing_scale` 或拒绝重采 | S8/S9 接口 |

## Multiplicity / Copy Logic

本类有 **1 根** multiplicity 轴（站位数）。

- `count_param`：`station_count`（亦即 `joystick_count`）。x4 变体用常量 `STATION_COUNT=4`（S9/L205）；x2 变体内联 `range(2)`（S8/L350）。
- `N_range`：`[1, 6]`。真实街机柜常见 1-4 玩家，留余量到 6；sweep 小 N 高频、尾部稀有。
- sampling domain：加权采样，N=1/2 高频，N=3/4 中频，N=5/6 稀有。
- copied object：**一个完整玩家站位** = 红控制板 + 金按钮簇 + gimbal collar + 该站位自己的主控制机构（默认球头摇杆）+ 四角螺栓，由共享 helper 发射。
- naming：`station_{i}`（板）/ `station_{i}_buttons`（x2）或 `station_buttons_{i}`（x4）/ `joystick_collar_{i}` / 子 part `joystick_{i}` / 关节 `panel_to_joystick_{i}`（x2）或 `deck_to_joystick_{i}`（x4），`for i in range(n)` 循环发射。
- placement：沿 X 左右等距一排。x2 用 `station_x = (i-0.5)*station_spacing`（spacing≈0.190，S8/L351）；x4 用 `_station_x_positions()` 对称 pitch 排布且 `CAB_W` 加宽到 0.900（S9/L211-L215）。站位面偏移经 `band_point()` / `_panel_point()` 投到倾斜控制带法向。
- joint policy：每站位独立 **REVOLUTE** axis=(-1,0,0) 前后摆 limits ±0.45 effort/velocity=4.0，互不联动。
- 源码选择：**parent 的 N=1 是手写单体** `joystick` / `panel_to_joystick`，**未循环化**，不作为 copy-logic 源；stations_x2/x4 已重写为 `station_{i}`/`joystick_{i}` 循环链。**首选 x4（S9）作为 copy-logic 源码**——其 count 已参数化为单一常量 `STATION_COUNT` + `_add_joystick_station()` helper + `_station_x_positions()`；x2 用 `_build_control_station_geometry()` dict + 内联 `range(2)`，作为次选参照。
- N 样本已覆盖：N=1（parent，手写）、N=2（S8）、N=4（S9）。

## 拓扑多样性审计

总组合数：`4 body × 4 control × N(采样域 [1,6], 取保守 3 档) = 48`。仅 body×control 基础拓扑已 `4 × 4 = 16`，叠加 station N 轴进一步放大。


seed_domain_policy：procedural_first。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对普通 seed 用 deterministic procedural sampling：先选 `body_style`，再从 compatible Slot B 集合选 `control_style`，再对 `station_count` 加权采样，最后采 independent scale 并按 inequality 投影。`seed=0` 不特殊。compatibility matrix 排除非法组合（见下）。少量 regression overrides 仅用于已知失败回归。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类 16 基础拓扑 × N 档，低于 300 时记录离散空间上限；scale 只补视觉/比例多样性。

Controlled local parameterization：`cab_width_scale`（conditional，随 N）、`station_spacing_scale`（independent）、`control_travel_scale`（independent，缩放行程）。均在 `resolve_config` 内 clamp / 解析，不破坏控制座 captured fit、joint origin/axis、控制面 mating 或类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body → compatible control → weighted station_count → scales | slot_choices_for_seed matches build choices |
| compatibility matrix | body×control 正交（默认全合法）；N>1 时需 body 控制面足够宽（gating `CAB_W`）；spinner joint 须 CONTINUOUS 不可改 revolute | no floating control, collar/cup/bearing captured fit, joint axis/type, station 不穿模 |
| controlled local variation | cab_width_scale / station_spacing_scale / control_travel_scale + clamp | proportions vary without breaking control seat, joint origin, clearance, identity |
| regression overrides | none（首版） | previously failed or reviewer-selected only |
| random sweep | seeds 0-49 initial, 0-999 maturity | and contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body / cabinet form | 4 | yes | yes | |
| primary control mechanism | 4 | yes | yes | |
| station multiplicity (轴) | N∈[1,6] | yes | yes | N=1/2/4 有实读源 |

## Validator
- slot_choices_for_seed returns implemented module names（4 body × 4 control）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating prevents illegal combos（N>1 需控制面够宽；spinner 保持 CONTINUOUS）
- optional regression overrides are sparse and justified
- controlled local scale params（cab_width / station_spacing / control_travel）clamped；cross-part 依赖（cab_width conditional on N、station 不穿模 inequality）resolved in `resolve_config`
- 必须有静态 `cabinet_body` root、屏（`screen_glass`/bezel/marquee）、控制面、≥1 控制座 visual
- 每个可动控制机构有正确 consumer joint：joystick REVOLUTE axis=-X ±0.45；trackball REVOLUTE axis=Z ±π；**spinner CONTINUOUS axis=Z 无止挡**；slider PRISMATIC axis=X ±0.018
- captured fit（boot/shaft 入 collar、ball 入 cup、stem 入 bearing、runner 入 slot）有 element-scoped allow_overlap
- station multiplicity：N 份站位沿 X 等距、各有独立 REVOLUTE 关节、命名 `joystick_{i}` / `panel_to_joystick_{i}` 或 `deck_to_joystick_{i}`

## Reject cases
- 控制机构悬空，或经不可见接口盘连接（未贴控制座顶面）。
- 把 spinner 写成 REVOLUTE 带止挡——它必须是 CONTINUOUS 无止挡。
- 柜体被做成可动 part（应为静态 root parent visual）。
- 没有屏 / 没有控制面：退化成纯方块或纯掌机壳。
- station N>1 时未循环化（沿用 parent 手写单体），或站位互相穿模 / 落在控制面外。
- captured fit 无 allow_overlap 导致 collision 误报，或子件原点未贴座面导致漂浮。
- 把 keypad / 螺栓 / marquee 做成独立 FIXED child part（应为 parent visual）。

## 与相邻类别的边界
- 不该混入：**handheld game console（掌机 / PSP / 手柄）**——掌机是握持式一体壳、无落地柜体、无独立控制面与控制座；街机柜是落地/台面整柜，有屏脸 + 底座/踏板 + 倾斜或水平控制面 + 立起的主控制机构。二者只共享 picture 文件格式，不共享内容。
- 不该混入：**casino_machine（老虎机 / slot machine）**——casino 机核心是侧拉杆 + 旋转卷筒（reels）+ 投币/赔付线语义；街机柜核心是玩家输入控制机构（摇杆/球/钮/滑块）+ 游戏屏，无卷筒卷轴与赔付结构。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；workbench-only fork 源（非 10K 正式集）；等待人工审核，审核通过前不进入模板实现 |
