# Differential Drive Wheel Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `differential_drive_wheel` |
| template path | `agent/templates/differential_drive_wheel.py` |
| test path (optional) | `tests/agent/test_differential_drive_wheel_template.py` |
| stage | `TEMPLATE_SWEEP_PASS` |
| status | `pass` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern=mixed`：本类别含两条离散 motion spine。(1) **bevel-differential 家族**——单一 `carrier` 根件，暴露/封闭的差速齿轮组 + 两轮全部以 CONTINUOUS mimic 齿轮链挂在 carrier 上（parallel children，无 chassis 板 / 无转向）。(2) **dual-drive 家族**——`mount_plate` 根件 →(转向关节)→ `drive_carriage` →(CONTINUOUS 或经 rocker 悬挂)→ 两轮（linear chain + parallel wheels）。两家族共享 “两同轴 CONTINUOUS 轮 + 底盘安装接口” 的核心身份。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this category (2 origins + 9 forks) |
| source_index_policy | only adopted module sources are indexed below; all 11 samples were adopted |

- 全部 11 个样本都被采纳为 module 来源（2 origin + 9 fork），无 read-but-unused。

## 核心身份

机器人驱动模块：两只同轴、共享横向轴线的轮子，各有一个真实的 CONTINUOUS 自转关节；由电机 + 减速/差速机构驱动或分配动力；通过一个底盘安装接口（顶板 / 侧法兰 / 差速器自身后桥）挂到机器人底盘，使左右轮速差产生前进与转向。必须保留：两同轴 CONTINUOUS 轮、一个驱动/减速或差速机构、一个底盘安装接口。

边界（不该混入）：
- 汽车整体后桥（钢板弹簧 / 刹车 / 乘用车桥）。
- 被动脚轮 / 家具万向轮（无动力）。
- 全向轮 / 麦克纳姆轮（轮缘上带滚子）。
- 裸电机 / 台架齿轮箱（无轮）。

## 采用源码索引（Adopted Source Index）
| id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| A | `rec_use-the-attached-reference-image-picture-robotic_20260707_084323_751535_ed8a6961` | L161-L323 | 开放式暴露 bevel 差速：carrier 根 + orange 环齿 + brass 侧齿 + 黄 pinion + 双半轴轮；mimic 齿轮链；`_toothed_bevel_mesh`/`_annular_cylinder_mesh`/`_make_tire_mesh`/`_make_rim_mesh` |
| B | `rec_robotics__differential_drive_wheel__002_png_2bafd7c2baa94629a23400f40574efad` | L108-L265 | AGV 双电机：mount_plate 根 + REVOLUTE swivel + drive_carriage 齿轮箱 + 两 CONTINUOUS 轮；cadquery 板/轴承环/吊环；`_make_tire_mesh` |
| belt | `rec_differential_drive_wheel_var_belt` | L221-L453 | 同步带减速 carriage：抬高电机 + 电机带轮 + 轮带轮 + 带环；`_toothed_pulley_mesh`/`_belt_loop_mesh` |
| worm | `rec_differential_drive_wheel_var_worm` | L106-L444 | 直角蜗杆减速：`Worm`/`SpurGear` 蜗杆+蜗轮盘 + 铸壳；`_carriage_body_mesh`/`_worm_housing_mesh` |
| hubdrive | `rec_differential_drive_wheel_var_hubdrive` | L118-L355 | 轮毂直驱：cross-bar carriage + 定子鼓（fixed）+ 轮=转子壳；`_stator_drum_cq`/`_rim_shell_cq`/`_cross_bar_cq` |
| caster | `rec_differential_drive_wheel_var_caster` | L66-L344 | 连续 360° slew-ring 转向：`_bearing_ring_mesh`(外齿 slew)/`_slew_ring_flange_mesh`；swivel=CONTINUOUS |
| sideflange | `rec_differential_drive_wheel_var_sideflange` | L34-L301 | 竖直 L 法兰底座：`_l_bracket_mesh`(法兰+座+肋)；swivel 落在座面 z≈0 |
| enclosed_housing | `rec_differential_drive_wheel_var_enclosed_housing` | L124-L493 | 封闭铸差速壳（pumpkin）+ 桥管 + pinion nose + 检视盖；`_make_diff_housing_shell` |
| spider_n2 | `rec_differential_drive_wheel_var_spider_n2` | L164-L424 | spider 十字 + 2 行星 pinion + 对称双侧齿；loop 复制 planet_pinion_i |
| spider_n4 | `rec_differential_drive_wheel_var_spider_n4` | 同结构 n=4 | spider 十字 + 4 行星 pinion（90° 布置） |

## 槽位 + 候选模块表

### Slot 1：drive_mechanism（② 关节/机构 + ③ 主体形态主槽）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `bevel_diff_single` | forked_anchor | A | L161-L323 | eligible if compatible | carrier 根；orange 环齿+单 brass 侧齿+黄 pinion；5 CONTINUOUS mimic 关节；无板无转向 |
| `bevel_diff_spider2` | forked_anchor | spider_n2 | L164-L424 | eligible if compatible | 同上 + spider 十字 + 对称双侧齿 + 2 行星 pinion（loop 复制，180°） |
| `bevel_diff_spider4` | forked_anchor | spider_n4 | 同 n=4 | eligible if compatible | 同 spider2，4 行星 pinion（90°）——multiplicity N∈{2,4} |
| `dual_motor_gearbox` | forked_anchor | B | L108-L265 | eligible if compatible | drive_carriage 齿轮箱块 + 单电机罐 + 轴桩；两轮 CONTINUOUS |
| `belt_reduction` | forked_anchor | belt | L221-L453 | eligible if compatible | 开放 carriage + 抬高电机 + 电机/轮带轮 + 同步带环 |
| `worm_reduction` | forked_anchor | worm | L106-L444 | eligible if compatible | 铸 carriage frame + 每侧蜗杆壳 + `Worm` 蜗杆 + `SpurGear` 蜗轮盘（键在轮上） |
| `hub_direct_drive` | forked_anchor | hubdrive | L118-L355 | eligible if compatible | cross-bar carriage + 定子鼓（fixed）+ 轮=转子壳绕定子 |

### Slot 2：chassis_mount（③ 主体形态 / 安装接口）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rear_bridge_carrier` | forked_anchor | A | L176-L214 | bevel 家族 only | 开放式 gunmetal 桥/颊板 carrier 本体（Planar/frame Boundary Form），carrier 即安装接口，rigid |
| `enclosed_diff_housing` | forked_anchor | enclosed_housing | L124-L383 | bevel 家族 only | 封闭铸球壳 + 桥管 + pinion nose + 检视盖（Volumetric Envelope Form） |
| `top_mount_plate` | forked_anchor | B | L36-L64,L124-L136 | dual-drive 家族 only | 圆角顶板 + 中央轴承环（Planar Boundary Form，水平） |
| `side_flange_bracket` | forked_anchor | sideflange | L34-L159 | dual-drive 家族 only | 竖直 L 法兰 + 水平座 + gusset 肋（转向关节落在座面） |

### Slot 3：steering（② 关节类型/轴）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rigid` | forked_anchor | A / B(FIXED variant) | A L275-L322 | 全家族 | mount→carriage FIXED（bevel 家族恒为 rigid：carrier 即根件无 mount 关节；dual-drive 亦可 rigid） |
| `limited_swivel` | forked_anchor | B | L242-L251 | dual-drive only | REVOLUTE 绕 Z，限位 ±swivel_limit（转向对齐） |
| `continuous_caster` | forked_anchor | caster | L66-L109,L321-L330 | dual-drive + top_mount_plate only | CONTINUOUS 绕 Z，全 360° slew-ring（外齿环 + 匹配法兰） |

### Slot 4：wheel_travel（① 骨架 / 悬挂）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rigid_axle` | forked_anchor | A / B | B L253-L263 | 全家族 | 轮直接 CONTINUOUS 挂在 carrier/carriage（无悬挂链） |
| `sprung_rocker` | forked_anchor | suspension | L347-L447 | dual_motor_gearbox only | 每侧插入 rocker_arm 连杆 + REVOLUTE rocker_pivot + 线圈弹簧/减振；轮改挂在 rocker 末端 |

硬约束满足：
- Slot 1 有 7 个结构不同 candidate；Slot 2 有 4；Slot 3 有 3；Slot 4 有 2。均无“只换尺寸/颜色/装饰”的伪 candidate。
- 无 1-candidate slot。Slot 3 `continuous_caster`、Slot 4 `sprung_rocker` 为条件可达（gating 见 §9），但每个 slot 至少 2 个可达 candidate。
- 行星 pinion N∈{2,4} 的 multiplicity 编码进 Slot1 的 `bevel_diff_spider2/4` candidate 名（AUTHORING 可变复制 radial 模式）。

## 槽位图（slot graph）

pattern: `mixed`

```text
# bevel-differential 家族（carrier 根，parallel children，rigid）
[Slot2 rear_bridge_carrier | enclosed_diff_housing] == carrier(root)
   ├─ left_wheel_spin   CONTINUOUS axis X  --> left_wheel   (mimic side gear)
   ├─ right_wheel_spin  CONTINUOUS axis X  --> right_wheel  (mimic side gear)
   ├─ orange_gear_spin  CONTINUOUS axis X  --> orange_gear  (mimic input_pinion ×-0.42)
   ├─ (single) brass_gear_spin  或  (spiderN) left/right_side_gear_spin + planet_pinion_i_spin
   └─ input_pinion_spin CONTINUOUS axis Y  --> input_pinion (driver)
   # Slot3=rigid（carrier 即底盘接口），Slot4=rigid_axle

# dual-drive 家族（linear chain + parallel wheels）
[Slot2 top_mount_plate | side_flange_bracket] == mount_plate(root)
   └─[mount_to_carriage : Slot3 rigid=FIXED / limited_swivel=REVOLUTE / caster=CONTINUOUS ; axis Z ; origin 板/座中心]--> drive_carriage(Slot1: dual_motor/belt/worm/hub)
        ├─ rigid_axle:  carriage_to_wheel_i CONTINUOUS axis X --> wheel_i
        └─ sprung_rocker: rocker_pivot_i REVOLUTE axis Y --> rocker_arm_i ；carriage_to_wheel_i CONTINUOUS axis X --> wheel_i（挂 rocker 末端）
```

跨 slot 接口点位：
- bevel 家族：所有 CONTINUOUS 关节 origin 在轴线上（轮 z=0.130 world，X 轴对称中心线），符合 origin-proximity 旋转对称中心线豁免；齿轮/半轴过盈用 element-scoped allow_overlap。
- dual-drive 家族：mount→carriage 关节 origin 在板/座中心 Z 轴（swivel_post/bearing_ring 对称中心线）；轮关节 origin 在轴线 X。sprung_rocker 的 rocker_pivot origin 在 carriage 侧齿轮箱面上的 pivot boss。
- 所有 moving child 关节都是 captured-pin / bearing / shaft-in-hub 几何（非两平面贴合），按 AUTHORING Rule 2 语义 **omit MatingContract**（grandfathered），靠 element-scoped allow_overlap 表达真实过盈——与全部 11 个通过样本一致。

## 每槽位 Module Emits / Interfaces

### Slot1 / bevel_diff_single|spider2|spider4
| emits | 描述 | 来源 |
|---|---|---|
| parts | left_wheel, right_wheel（tire+rim+half_shaft+collar）；orange_gear；input_pinion；(single) brass_side_gear / (spiderN) left_side_gear,right_side_gear,planet_pinion_i | A / spider_n2 |
| internal joints | *_spin CONTINUOUS：input_pinion(driver, axis Y)、orange(mimic pinion ×-0.42)、side gear(mimic orange ×-1)、wheel(mimic side gear)、planet_i(mimic orange) | A/spider L275-L423 |
| upstream interface | 无（carrier 根，见 Slot2）；齿轮/轮 parent=carrier | A |
| downstream interface | 齿轮啮合/半轴过盈（element allow_overlap） | A |

### Slot1 / dual_motor_gearbox|belt_reduction|worm_reduction|hub_direct_drive
| emits | 描述 | 来源 |
|---|---|---|
| parts | drive_carriage（机构相关 visuals）；wheel_0, wheel_1 | B/belt/worm/hubdrive |
| internal joints | carriage_to_wheel_i CONTINUOUS axis X | B L253-L263 |
| upstream interface | drive_carriage 顶 swivel_post/bearing_flange，接 Slot3 转向关节 | B |
| downstream interface | 轮轴 X 线（rigid_axle 直挂 / sprung_rocker 经 rocker） | B/suspension |

### Slot2 / chassis_mount
| emits | 描述 | 来源 |
|---|---|---|
| parts | rear_bridge_carrier/enclosed_diff_housing → `carrier`（含电机）；top_mount_plate/side_flange_bracket → `mount_plate` | A/enclosed/B/sideflange |
| internal joints | 无（根件） | — |
| downstream interface | bevel：carrier 上齿轮/轮的 CONTINUOUS 关节 origin；dual：板/座中心的转向关节座 | A/B |

### Slot4 / sprung_rocker
| emits | 描述 | 来源 |
|---|---|---|
| parts | rocker_arm_i（arm_body mesh + spring_coil + shock_shaft）；carriage 上 shock_body_i/spring_mount_i visuals | suspension L300-L379 |
| internal joints | rocker_pivot_i REVOLUTE axis Y（±），carriage_to_wheel_i 改 parent=rocker_arm_i | suspension L407-L447 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `drive_mechanism` | enum | 7 module 名 | `dual_motor_gearbox` | choice | deterministic sampler | Slot1 |
| `chassis_mount` | enum | 4 module 名 | `top_mount_plate` | conditional | 由 family gating（§9）选 | Slot2 |
| `steering` | enum | rigid/limited_swivel/continuous_caster | `limited_swivel` | conditional | family + mount gating | Slot3 |
| `wheel_travel` | enum | rigid_axle/sprung_rocker | `rigid_axle` | conditional | 仅 dual_motor_gearbox 可 sprung | Slot4 |
| `planet_pinions` | int | {2,4} | 2 | conditional | 仅 spider* candidate；N 编进 candidate 名 | spider |
| `track_scale` | float | [0.94, 1.06] | 1.0 | independent | 轮外置位置 = base·scale 后 clamp | ⑤ |
| `swivel_limit` | float | [0.25, 0.5] | 0.35 | independent | limited_swivel 的 ±上下限 | B ⑤ |
| `palette_theme` | enum | 3 themes | `industrial_steel` | choice | 仅改材质大类/配色（⑥），几何不变 | ⑥ |
| (—) | constraint | — | — | inequality | 轮内侧面 − carriage/gearbox 外侧面 ∈ [0.001, 0.06]；track_scale 收缩到满足 | 接口 clearance |

连续尺寸采样契约：先采 `track_scale`/`swivel_limit`（independent，均匀），无 equation 从属尺度，`inequality`（轮-机构间隙）在 `resolve_config` 内 clamp track_scale。`conditional`（chassis_mount/steering/wheel_travel/planet_pinions 的合法域）在采样前按 drive_mechanism family 解析。

### 7.5 编译预算 / compile budget（必填）
自报 **每-seed ≤ 45s**（依据：dual/caster/sideflange 走 cadquery 板+轴承环+吊环 meshes；worm 走 `Worm`/`SpurGear`；belt 走 pulley+belt loop——均为库内“重布尔/放样”档，实测参考 30-60s；bevel 家族走轻量 `_toothed_bevel_mesh`/tire mesh ≈ 10-20s）。每 seed 只构建被选中的一套机构+一个 mount，cadquery tolerance 保持源值 0.0008/0.0006/0.0004；tire/rim/gear mesh 分档段数沿用源。sweep `--compile-timeout 150`（≈3×）作 watchdog。

## Multiplicity / Copy Logic

- **primary N 轴——差速行星 pinion**：`count_param planet_pinions`，source-backed N∈{2,4}（spider_n2/spider_n4）。N 编入 Slot1 candidate 名 `bevel_diff_spider2/4`。copied_object `planet_pinion_{i}`（共享 `_toothed_bevel_mesh` helper），radial 布置（i·2π/N，实际 180°/90°），uniform mimic 关节全部 mimic `orange_gear_spin`。N_range=[2,4]（真实 spider 只支持 2 或 4，故 2 个 N 样本；`underfilled_reason` 同源 planner）。
- **轮**：固定 N=2（差速驱动定义性，不 sweep）；每轮独立 CONTINUOUS 子件，loop 发射。
- **紧固件/散热片/螺丝（record_only，非 candidate）**：plate_screw_i(8)、bearing_screw_i(10/12)、hub_screw_j(10)、motor_fin_i、gearbox_screw、cover_bolt_i、flange_screw_i、rotor_bolt_j、cap_bolt——均 loop 发射、宿主面派生、稳定索引名，是参数化复制而非拓扑 candidate。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 两条离散骨架：bevel(carrier 根，5-10 齿轮/轮 CONTINUOUS mimic 图) vs dual-drive(plate→carriage→2 轮链)；`sprung_rocker` 再插 rocker_arm 连杆 + rocker_pivot REVOLUTE（① 增件增边）。全 forked_anchor（A/B/spider/suspension） |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：planet_pinion N∈{2,4}（spider_n2/n4） |
| ② 关节类型 | 换 type/轴 | 有 | wheel spin CONTINUOUS(X)；bevel 齿轮链 CONTINUOUS(X/Y) mimic；转向 rigid=FIXED / limited=REVOLUTE(Z) / caster=CONTINUOUS(Z)；rocker_pivot REVOLUTE(Y)。每种类型都在 sweep 出现（gating 保证）。全 source-backed |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | Slot1/Slot2 承载：rear_bridge_carrier=开放框架(Planar/frame Boundary Form) / enclosed_diff_housing=封闭铸球壳(Volumetric Envelope Form) / top_mount_plate=水平圆角板(Planar Boundary Form) / side_flange_bracket=竖直 L 法兰(Planar Boundary Form, 竖直) / hub_direct_drive=cross-bar+转子壳(Volumetric)。每个 candidate 标 form_subtype；全 forked_anchor |
| ④ 表面装饰 | 叠加表面细节/改装饰数 | 有(record_only, host-conformal) | 螺栓圈/吊环/散热片/轮毂螺丝/胎面花纹/齿轮齿/检视盖螺栓/法兰螺栓——全部作为宿主 part 的 visual、由宿主面派生，非独立 candidate、非新 joint |
| ⑤ 尺寸/行程 | 只改尺寸/行程 | 有 | `track_scale`[0.94,1.06]、`swivel_limit`[0.25,0.5]。运动包络：wheel spin CONTINUOUS 整圈不穿模；limited_swivel REVOLUTE(Z) [−lim,+lim]；caster CONTINUOUS(Z) 整圈；rocker_pivot REVOLUTE(Y) [−0.12,+0.18]（正向抬轮）。motion_test_plan：靠 harness_motion_qc sampled collision（honor element allow_overlap）+ 每机构 targeted `ctx.pose`（轮自转心不动 / swivel 座下贴合 / caster 360° 回位 / rocker 抬轮） |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 3 palette theme（industrial_steel / gunmetal_orange / anodized_black）覆盖 metal/painted/rubber 材质大类；功能性齿轮色（orange/brass/yellow）与胎面在 bevel 家族固定语义。材质大类 ≥ ceil(0.5×3)=2 覆盖 |

## 采样与覆盖审计

总组合数（合法域）：
- bevel 家族：drive(3: single/spider2/spider4) × mount(2) × steer(1 rigid) × travel(1) = 6
- dual-drive 家族：drive(4) × mount(2) × steer(≤3) × travel(≤2)，经 gating（caster 仅 top_plate；sprung 仅 gearbox）≈ 4×2×3×2 − 非法 ≈ 30+
- 合计合法离散组合 ≈ 36+，叠加 track_scale/swivel_limit/palette 连续+离散足以覆盖 36 seed。

理由：机构 slot 故意最富（7），因为本小类横跨“机械差速”与“独立双电机”两种解释。每个可达 slot ≥2 candidate。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对所有普通 seed（含 seed 0，不特殊）用 `random.Random(seed)` 采样：先选 drive_mechanism → 解析 family → 条件采 chassis_mount/steering/wheel_travel/planet_pinions → 采连续 track_scale/swivel_limit/palette。无 curated/modulo 主表。
Topology target：report-only；真实合法组合空间 ≈36（受两家族 disjoint 骨架 + gating + 源锚点上限约束，<300 已说明）。
无 regression overrides。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | drive→family→conditional mount/steer/travel/N→continuous | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | bevel⇒{rear_bridge/enclosed}+rigid+rigid_axle；dual⇒{top_plate/side_flange}+{rigid/limited/caster}+{rigid/sprung}；caster⇒top_plate only；sprung⇒dual_motor_gearbox only | 无 floating/collision/轴/max-N/bulky/optional-child 失败 |
| controlled local variation | track_scale/swivel_limit（clamp+inequality），palette（仅色） | 比例变化不破接口/间隙/支撑/joint origin/类别身份 |
| regression overrides | none | — |
| random sweep | seeds 0-35 首验，0-999 成熟度 | 契约失败；axis_realization；viewer |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| drive_mechanism | 7 | yes | yes | |
| chassis_mount | 4 | yes | yes | family-gated |
| steering | 3 | yes | yes | caster 条件可达 |
| wheel_travel | 2 | yes | no | sprung 仅 gearbox（source 上限） |

## Validator
- slot_choices_for_seed 返回已实现 module 名。
- config_from_seed 对所有普通 seed 用 deterministic procedural sampling（seed 0 不特殊）。
- compatibility gating 阻止非法组合（bevel+swivel、caster+side_flange、sprung+非gearbox）。
- 无 curated/modulo 主 seed 表；track_scale/swivel_limit 在 resolve_config clamp。
- 每个 wheel spin 是 CONTINUOUS(axis X)；至少一个底盘安装接口 part 存在。
- bevel 家族：input_pinion 驱动 orange（mimic<0）；侧齿反转；轮 mimic 侧齿/orange。
- dual 家族：limited_swivel=REVOLUTE 有限位；caster=CONTINUOUS 无硬限位；sprung=rocker_pivot REVOLUTE 有限位且正向抬轮。
- 关键过盈用 element-scoped allow_overlap（齿轮啮合/半轴/轴承/rocker 捕获），非 broad part 级。

## Reject cases
- 缺 wheel spin 或非 CONTINUOUS 或轴非 X。
- bevel 家族缺齿轮链 / mimic 断裂 / 输入不驱动 orange。
- dual 家族轮直接漂浮无 carriage 支撑 / 转向关节 origin 不在板座中心。
- caster 声明连续却带硬限位；limited_swivel 无限位。
- 把不动装饰（螺栓/散热片/胎面）做成 FIXED part（应为宿主 visual）。
- 用 broad part 级 allow_overlap 掩盖真实穿模；用尺寸缩放硬凑过 sweep。
- 轮数 ≠ 2（差速定义性）。

## 与相邻类别的边界
- 汽车整体后桥（`rear_axle`）：有钢板弹簧/刹车鼓/整车桥壳；本类别是机器人驱动模块，两独立轮速。
- 脚轮 / caster wheel：被动无动力；本类别每轮必有驱动 CONTINUOUS 自转 + 减速/差速机构。
- 全向/麦克纳姆轮：轮缘带滚子；本类别为普通胎面轮。
- 裸电机 / 台架齿轮箱：无轮；本类别必含两同轴轮。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核 |

## 模板实现备注（可选）
- 共享 helper：`_toothed_bevel_mesh`/`_annular_cylinder_mesh`（bevel 齿轮，来自 A/spider）；`_make_tire_mesh`/`_make_rim_mesh`（A 轮）；`_make_tire_mesh_b`（B 轮）；`_mounting_plate_mesh`/`_bearing_ring_mesh`/`_eye_bolt_mesh`（B 板）。
- captured-pin element allow_overlap：bevel 半轴↔齿轮 hub、input_shaft↔motor、spider arm↔shaft、planet↔side gear；dual swivel_post↔bearing_ring、worm/worm_wheel↔housing、hub_bearing↔rotor、rocker arm↔wheel/gearbox。逐机构从对应源 run_tests 移植。
- 暂不进入 seed domain 的组合：bevel+任何 swivel/side_flange/sprung；caster+side_flange；sprung+非gearbox（gating 排除）。
</content>
</invoke>
