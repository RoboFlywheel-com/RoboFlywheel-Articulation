# ac_outdoor_unit (air conditioner outdoor / condensing unit) — Modular Spec

> 大类/小类：`Facade Element / Air conditioner outdoor unit`（articraft_data 上游小类样本池；condenser units）。
> 上游 source map：`articraft_data/picture_expansion/template_source_maps/Facade_Element__Air_conditioner_outdoor_unit.md`。
> **本 slug = 室外冷凝机组（outdoor condensing unit）**：矩形钣金机箱 + 前/顶圆形轴流风机（带防护栅）+ 侧检修口 + 冷媒铜管阀 + 底座/支架。**与已存在的 `air_conditioner` slug（壁挂分体室内机）严格区分**，见 §11。
>
> **两个 parent 来自两张图、是两种结构家族**：
> - parent P1（**single-fan**，bracket-root 家族）：`rec_build-a-realistic-articulated-3d-model-of-a-air-_20260609_185849_813335_0710784e` ← `picture/Facade Element/Air conditioner outdoor unit/001.png`。
> - parent P2（**dual-fan**，housing-root 家族）：`rec_build-a-realistic-articulated-3d-model-of-a-air-_20260609_185900_637532_0ffac329` ← `picture/Facade Element/Air conditioner outdoor unit/003.png`。
> - 第三张图 `002.png` 的 build 记录 `rec_build-...-air-_20260609_185856_985635_d332e6ea` 存在但**没有 fork 出任何变体，不是本批 fork parent，不进 module source 表**（仅此处记录其存在）。
>
> **同步状态**：本 spec 引用的 7 个 5 星样本（2 parents + 5 槽位 fork 变体）已同步进本仓库 `data/records/`，rating=5。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一精读核对）。引用以 part / joint / helper **名字** 为准，行号作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `ac_outdoor_unit` |
| template path | `agent/templates/Facade_Element_Air_conditioner_outdoor_unit.py` |
| test path (optional) | `tests/agent/test_ac_outdoor_unit_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: fan_discharge_layout(A) + front_service_skin(B) + mounting_support(C) 各自挂到共同 `housing`（parallel children），**外加** `fan_count` 风机多重性轴，仅在 A=front_fan_row 时活跃）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7（2 parents + 5 槽位 fork 变体；均 converged、compile success、≥1 非 fixed joint）|
| read_count | 7（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、run_tests 的 allow_overlap/expect_contact 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 7/7 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：

- **两个 parent 是两条结构 spine，须在模板内统一到一个公共 `housing`-root 装配契约**：
  - **P1（single-fan, bracket-root）**：root = `mounting_bracket`（angle-iron 支架），`bracket_to_housing` FIXED 把 `housing` 抬到 `+BODY_H/2`。`housing` 是 CadQuery 盒体**从后面（-Y）掏空**、前面（+Y）开**单个圆形 fan 喉口**、右侧（+X）凹一个 service pocket。前面有 `fan_shroud_ring`（venturi 流环）+ `fan_motor_mount`（电机罐+轴+横撑，grounds rotor）。`fan_grille`（独立 part，concentric 钢丝栅 tori+spokes+boss+4 tabs）FIXED 挂前脸。`fan_rotor`（独立 part，`FanRotorGeometry` 绕 local+Z，origin rpy=(-π/2,0,0) 使轴对齐世界 **+Y**）`housing_to_fan` **CONTINUOUS axis=(0,1,0)**。`service_panel`（独立 part，薄板+finger-pull）`housing_to_service_panel` **REVOLUTE axis=(0,0,-1)** 竖直铰，lower0 upper1.9，外摆 +X。`service_valves`（铜管阀，FIXED，穿侧壁）。 (P1 model.py L396-L544)
  - **P2（dual-fan, housing-root）**：root = `housing`（无 bracket，无 service panel，无 valves）。`housing` 盒体掏空、前面开**两个**圆 bore（`LEFT_FAN_X`/`RIGHT_FAN_X`），grille guard（`_concentric_grille` 同心环+8 spokes+hub front/rear spigot）**作为 housing visual union 上去**（不是独立 part），另有 top lid lip + 2 mounting tabs + 左 control panel band（`panel_plate`+`rating_badge` visuals）+ **4 个 mount feet**（`_build_feet` 底座脚）。`left_fan`/`right_fan` 两个独立 part（`FanRotorGeometry` 绕 local+Z，origin rpy=(-π/2,0,0)→世界+Y），`housing_to_left_fan`/`housing_to_right_fan` **CONTINUOUS axis=(0,1,0)**。 (P2 model.py L260-L356)
  - **统一裁决**：模板以 **`housing`-root** 为公共 root（P2 风格），P1 的 `mounting_bracket` 降为 **Slot C 的一个候选**（mounting_support），通过 `bracket_to_housing` FIXED 反挂或等价地把 housing 抬到支架上方。fan 一律 **`fan_{i}` 独立 part + CONTINUOUS** 命名统一（P2 的 `left/right_fan` 在模板里改成 `fan_0/fan_1`，three_fans 已用此命名）。
- **Slot A = fan / discharge layout（主机构槽 + 多重性宿主）**：
  - `front_fan_row`（前脸横排 N 个圆风机，**携带 `fan_count` 多重性**；轴 **+Y**）—— 来自 P2(N=2) 与 `three_fans`(N=3，`fan_{i}` loop，`FAN_X_POSITIONS` 等距，每个独立 CONTINUOUS rotor)。
  - `top_discharge_fan`（顶面 +Z 单风机，轴 **+Z**，`_grille` 在 XY 面，rotor local+Z 直接对齐世界+Z 无需旋转）—— 来自 `top_discharge_fan`，**单风机、不携带多重性**（顶面只放一个）。
  - 两者真正改变 fan 轴向、bore 所在面、grille 朝向、以及 multiplicity 是否活跃 → 是结构槽不是装饰。
- **Slot B = front grille / service skin**：
  - `wire_ring_grille`（前脸 concentric 钢丝栅圈，独立 `fan_grille` part，tori+diametral spokes+center boss+4 mounting tabs）—— P1 `_grille` / side_door / wall_brackets 共用。
  - `louver_vent_panel`（矩形百叶通风板，`VentGrilleGeometry` framed vent + 水平 flat slats 35° + 短 rear sleeve 嵌 shroud；独立 `fan_grille` part，origin rpy=(-π/2,0,0)）—— `louvered_front`。
  - `side_service_door`（侧检修门 = 把 P1 的薄板 service_panel 升级成 `service_door` part：`_service_panel` slab + `_door_latch`（quarter-turn cam latch）+ housing 上 `_hinge_barrels`（2 个铰链 knuckle+leaf+cap，FIXED 在 housing），`housing_to_service_door` REVOLUTE axis=(0,0,-1)）—— `side_service_door`。
  - 注意：B 槽的 `side_service_door` 与 P1/wall_brackets 默认就有的 `service_panel`/REVOLUTE 检修盖**功能重叠**。模板里把"侧检修口"统一成一个由 B 选择细化的 skin：wire_ring/louver 两者仍保留默认 `service_panel`（薄板），`side_service_door` 则换成带 latch+可见 hinge barrels 的升级门。即 B 主要改的是**前栅形态**，side_service_door 额外升级侧门细节。
- **Slot C = mounting support**：
  - `angle_iron_bracket`（P1 `_bracket`：2 L 腿 + 前后横轨，root 或 FIXED 在 housing 下）。
  - `wall_brackets`（`wall_brackets`：`NUM_BRACKETS=2` 个重型挂墙托架，各含 shelf+wall plate+三角 gusset+front stop+bolt holes，`wall_bracket_0` 与 `wall_bracket_1` FIXED 相连，housing 坐其上）。
  - `base_feet`（P2 `_build_feet`：4 个深色底脚，作为 housing visual，落地式）。
  - 三者真正改变 root/support part 数、是否多支架、以及落地 vs 挂墙 → 结构槽。

## 核心身份

一台**空调室外冷凝机组（outdoor condensing unit）**：矩形钣金机箱（典型 W≈0.80–1.20m × D≈0.30m × H≈0.50–0.54m，白/米/灰外壳；多风机阵列可派生加宽），**从背面（-Y）掏空**的中空壳体，前面（或顶面）开一个或多个**圆形风机喉口**，每个喉口后是一台**轴流冷凝风机 rotor**（`FanRotorGeometry`，叶片数 `fan_blade_count` 随机 3–6）绕喉口法线 **CONTINUOUS 自转**（前排=+Y，顶排=+Z）。喉口外覆**防护栅**（同心钢丝圈 / 矩形百叶板）。机箱一侧有**检修口**（薄板 / 带 latch+铰链的检修门，REVOLUTE 竖直铰外摆），并伸出**冷媒铜管阀**（service valves，穿侧壁）。机箱由**支撑结构**承托：落地角铁支架 / 重型挂墙托架（×2，带三角 gusset） / 底脚。活动语义 = **轴流风机连续旋转（product 域前排 1–20 台，sweep 仅覆盖 1–5 台）+ 侧检修门开合（REVOLUTE）**。默认成熟域：fan_discharge_layout × front_service_skin × mounting_support × 前排风机数 N∈[1,20] 的室外冷凝机组；模板验收 sweep 只要求 N∈[1,5]。

不该混入：见 §11。

## 槽位 + 候选模块表

### Slot A：fan_discharge_layout（风机 / 排风布局；主机构 + multiplicity 宿主）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| front_fan_row | rec_build-...-air-_..._0ffac329 (P2) | L146-L213（housing+两 bore+grille union）, L305-L354（left/right_fan part + 两 CONTINUOUS +Y joint） | eligible if compatible | 前脸横排 N 个圆 bore，每 bore 后一台 axial rotor，joint **CONTINUOUS axis=(0,1,0)**；**`fan_count` 多重性宿主**。基线 N=2。 |
| front_fan_row (N=3 证据) | rec_ac_unit_var_three_fans | L141-L189（`FAN_X_POSITIONS` 等距 3 bore）, L289-L317（`fan_{i}` loop 发 3 个 part + `housing_to_fan_{i}` CONTINUOUS +Y） | eligible if compatible | 与上同 module，N=3 的循环复制证据：`for i in range(N_FANS)` 发 `fan_{i}` + `housing_to_fan_{i}`，等距排布。确立 `fan_{i}`/`housing_to_fan_{i}` 命名与 placement。 |
| top_discharge_fan | rec_ac_unit_var_top_discharge_fan | L69-L110（顶面 +Z bore）, L113-L206（顶面 shroud+grille XY）, L209-L296（顶挂 motor mount+rotor local+Z）, L466-L531（`housing_to_fan` CONTINUOUS **axis=(0,0,1)**） | eligible if compatible | 顶面 +Z 单风机：bore 切顶壁，grille 在 XY 面朝上，rotor local+Z 直对世界+Z（无 rpy），joint **CONTINUOUS axis=(0,0,1)**；**单风机、不携带多重性**（fan_count≡1）。 |

> A 槽 3 个 candidate（front_fan_row 单/多由 fan_count 表达，top_discharge_fan 独立结构）。前排 N=2/3 来自不同样本但是同一 module 的多重性实例，故 module 计 2 个结构家族（front_fan_row / top_discharge_fan）+ 一个 multiplicity 轴 → 槽位多样性主要由 **A×fan_count** 与 B、C 叉乘提供，见 §9。

### Slot B：front_service_skin（前栅 / 检修皮肤）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| wire_ring_grille | rec_build-...-air-_..._0710784e (P1) | L136-L211（`_grille` concentric tori+spokes+boss+4 tabs）, L447-L453（`fan_grille` part）, L497-L503（`housing_to_grille` FIXED 前脸） | eligible if compatible | 前脸**圆形钢丝同心栅**：4 tori（半径递增）+ 6 diametral spokes + center boss + 4 rim mounting tabs，fuse 成单连通岛，独立 `fan_grille` part，FIXED 挂前脸 venturi `fan_shroud_ring`。 |
| louver_vent_panel | rec_ac_unit_var_louvered_front | L148-L179（`_louver_grille_geometry` VentGrilleGeometry）, L415-L428（`fan_grille` part, origin rpy=(-π/2,0,0)）, L470-L477（`housing_to_grille` FIXED） | eligible if compatible | 前脸**矩形百叶通风板**：`VentGrilleGeometry` framed panel + 水平 flat slats（pitch0.022, angle35° down）+ divider + 短 rear sleeve（嵌 shroud）。近方形（W/H≈1），独立 `fan_grille` part。 |
| side_service_door | rec_ac_unit_var_side_service_door | L311-L353（`_hinge_barrels` 2 knuckle+leaf+cap, housing visual）, L356-L388（`_door_latch` quarter-turn cam）, L561-L575（`service_door` part w/ door_panel+door_latch）, L628-L636（`housing_to_service_door` REVOLUTE axis=(0,0,-1)） | eligible if compatible | **侧检修门升级**：保留前脸 wire_ring grille，但把侧 `service_panel` 升级为 `service_door`（薄板 + cam latch），并在 housing 上加 2 个**可见铰链 barrel**（knuckle+leaf+pin cap），REVOLUTE 竖直外摆。改变侧检修件 part 组成 + 增 housing 铰链 visual。 |

> B 槽 3 个 candidate，均结构不同（圆钢丝栅 / 矩形百叶板 / 侧门+可见铰链）。wire_ring_grille 与 louver_vent_panel 是**前栅形态**互斥替换；side_service_door 是**侧检修件**升级，默认与 wire_ring_grille 同时存在（前栅仍是钢丝圈）。详见 §9 兼容矩阵。

### Slot C：mounting_support（承托结构）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| angle_iron_bracket | rec_build-...-air-_..._0710784e (P1) | L303-L351（`_bracket` 2 L 腿+前后横轨）, L406-L416（`mounting_bracket` part）, L483-L489（`bracket_to_housing` FIXED 抬 housing） | eligible if compatible | **落地角铁支架**：2 条 L 形腿（沿 Y）+ bottom foot flange + top flange + 前后 cross rail。单 part `mounting_bracket`，FIXED 承托 housing（housing 抬 `+BODY_H/2`）。 |
| wall_brackets | rec_ac_unit_var_wall_brackets | L312-L414（`_wall_bracket` shelf+wall plate+三角 gusset+front stop+bolt holes）, L469-L493（`wall_bracket_{i}`×2, `bracket_to_bracket` FIXED）, L520-L526（`bracket_to_housing` FIXED, housing 居中两托架） | eligible if compatible | **重型挂墙托架×2**：每个含 shelf 平台 + 竖直 wall plate（带 2 bolt holes）+ 三角 gusset 斜撑 + front stop + 2 shelf bolt holes。两托架 FIXED 相连，housing 坐其上居中。**多 part 承托**。 |
| base_feet | rec_build-...-air-_..._0ffac329 (P2) | L231-L243（`_build_feet` 4 角底脚）, L298-L302（作为 `housing` visual `mount_feet`） | eligible if compatible | **落地底脚×4**：4 个深色矩形脚，作为 **housing visual**（非独立 part），落地式。无独立 support part / FIXED joint（housing 自身即 root）。 |

> C 槽 3 个 candidate：落地角铁支架 / 挂墙托架×2 / 落地底脚。结构差异在 root/support part 数（1 / 2 / 0 独立 support part）与落地 vs 挂墙。

## 槽位图（slot graph）

pattern: `mixed`（parallel children on a shared `housing` + 一根 `fan_count` multiplicity 轴）

```
                         [Slot C mounting_support]
                                  │ FIXED (support→housing 或 housing 直接为 root)
                                  ▼
                            ┌──────────┐
            ┌──────────────│  housing  │──────────────┐
            │ FIXED         └──────────┘  FIXED        │ FIXED
            ▼                   │  ×N CONTINUOUS        ▼
   [Slot B front_service_skin]  │  (fan_count 轴)   [service_valves]  (P1/侧门家族, 可选)
   wire_ring_grille (fan_grille │                       铜管阀, FIXED 穿侧壁
     part, FIXED 前脸)          ▼
   | louver_vent_panel          [Slot A fan_discharge_layout]
   | side_service_door          front_fan_row: fan_0..fan_{N-1} (CONTINUOUS +Y)
     (+ housing hinge barrels,  | top_discharge_fan: fan_0 (CONTINUOUS +Z)
      service_door REVOLUTE -Z)
```

接口点位与 joint 契约：
- **mounting_support → housing**（Slot C 上游）：
  - `angle_iron_bracket` / `wall_brackets`：support 为 root，`bracket_to_housing` **FIXED**，origin 把 housing 抬到 `+BODY_H/2`（支架 shelf 顶 = housing 底，contact plane = z=0 shelf top）。wall_brackets 另有 `bracket_to_bracket` FIXED（两托架沿 X 间距 `BODY_W-2*INSET`）。
  - `base_feet`：无独立 support，**housing 自身为 root**，feet 是 housing visual（落地 contact plane = housing 底 -H/2）。
  - → 模板需统一 root 策略：C 选 bracket 类时 support 为 root + FIXED；C 选 base_feet 时 housing 为 root。`slot_choices_for_seed` 记录 C 选择即决定 root 拓扑。
- **housing → fan_{i}**（Slot A，主机构）：每个 fan rotor part 经 `housing_to_fan_{i}` **CONTINUOUS** 挂 housing。
  - front_fan_row：axis=(0,1,0)（前脸法线 +Y），origin=(`FAN_X_POSITIONS[i]`, `FRONT_Y-0.015`, `FAN_CTR_Z`)，rotor visual origin rpy=(-π/2,0,0)。fan 在 bore 内、栅后（recessed），hub 由 grille rear spigot 或 motor mount 承（captured embed）。
  - top_discharge_fan：axis=(0,0,1)（顶面法线 +Z），origin=(0,0,`BODY_H/2-0.018`)，rotor local+Z 直对世界+Z（无 rpy）。
- **housing → fan_grille / front skin**（Slot B）：
  - wire_ring_grille / louver_vent_panel：独立 `fan_grille` part，`housing_to_grille` **FIXED** 挂前脸（origin=(`fan_x`, `BODY_D/2`, `fan_z`)），grille rear 嵌 `fan_shroud_ring`（captured，allow_overlap）。
  - side_service_door：前栅仍 wire_ring；额外 `service_door` part `housing_to_service_door` **REVOLUTE axis=(0,0,-1)**（竖直铰，lower0 upper1.9，free edge 外摆 +X），hinge barrels 是 housing visual（FIXED in housing）。
- **housing → service_panel / service_valves**（P1/侧门家族默认侧检修件）：`housing_to_service_panel` **REVOLUTE axis=(0,0,-1)**；`housing_to_service_valves` **FIXED**（铜管穿侧壁，allow_overlap）。base_feet+top_discharge / P2 家族可无 service_panel/valves（P2 本身没有）→ 见 §9 兼容矩阵。

互斥 / 可选 / 派生：
- top_discharge_fan **与 fan_count 多重性互斥**（顶面只放 1 台 → fan_count≡1）。
- side_service_door 是侧检修件升级；与前栅 module（wire/louver）正交并存。
- service_valves / service_panel 是 P1-bracket 家族标配，base_feet（P2 落地）家族可省略（P2 无 valves/panel）。

## 每槽位 Module Emits / Interfaces

### Slot A / module front_fan_row
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fan_0`..`fan_{N-1}`（每个 = 一个 `FanRotorGeometry` rotor visual `fan_{i}_rotor`，origin rpy=(-π/2,0,0)，叶片数由 `fan_blade_count`=3–6 控制） | S5 three_fans/L289-L305；S2 P2/L305-L333 |
| internal joints | `housing_to_fan_{i}`：CONTINUOUS，axis=(0,1,0)，origin=(`FAN_X_POSITIONS[i]`,`FRONT_Y-0.015`,`FAN_CTR_Z`)，MotionLimits(effort2, velocity20) | S5/L308-L317；S2/L337-L354 |
| upstream interface | housing 前脸 N 个圆 bore（`_build_housing` 循环 cut，`FAN_X_POSITIONS` 等距）+ 每 bore 一个 `_concentric_grille` rear hub spigot 承 rotor hub | S5/L152-L158；S2/L159-L164,L130-L142 |
| downstream interface | rotor hub captured 在 grille rear spigot（`expect_contact`，allow_overlap `grille_i`↔`fan_i_rotor`）；rotor 在 cabinet footprint 内（`expect_within` xz） | S5/L437-L453；S2/L468-L522 |

### Slot A / module top_discharge_fan
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fan_0`（`fan_rotor` rotor，local+Z 直对世界+Z，无 rpy，叶片数由 `fan_blade_count`=3–6 控制）；顶面 `fan_grille`（独立 part，XY 面 `_grille`） | S6 top_discharge/L457-L475 |
| internal joints | `housing_to_fan` CONTINUOUS axis=(0,0,1)，origin=(0,0,`BODY_H/2-0.018`)；`housing_to_grille` FIXED 顶面 | S6/L504-L531 |
| upstream interface | housing 顶壁 +Z 圆 bore（`top_cut` cut 顶壁）+ 顶面 `fan_shroud_ring`（venturi）+ 十字 `fan_motor_mount`（悬挂电机罐+轴，grounds rotor） | S6/L89-L97,L113-L131,L209-L276 |
| downstream interface | rotor hub captured 在 motor shaft（`expect_contact` `fan_rotor`↔`fan_motor_mount`）；grille 在 fan 上方（`grille_above_fan`）；rotor 在 grille footprint xy 内 | S6/L672-L723 |

### Slot B / module wire_ring_grille
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fan_grille`（visual `grille_rings`：concentric tori + diametral spokes + center boss + 4 rim tabs，fuse 单岛） | S1 P1/L447-L453,L136-L211 |
| internal joints | 无活动（FIXED 静栅） | — |
| upstream interface | `housing_to_grille` FIXED，origin=(`fan_x`,`BODY_D/2`,`fan_z`)，前脸 venturi `fan_shroud_ring` 对中 | S1/L497-L503 |
| downstream interface | grille rim tabs 嵌 `fan_shroud_ring`（`expect_contact` `grille_rings`↔`fan_shroud_ring`，allow_overlap）；grille 在 fan 前方 +Y（`grille_in_front_of_fan`） | S1/L676-L703 |

### Slot B / module louver_vent_panel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fan_grille`（visual `louver_panel`：`VentGrilleGeometry` framed + 水平 slats + sleeve，origin rpy=(-π/2,0,0)） | S3 louvered/L415-L428,L148-L179 |
| internal joints | 无活动（FIXED 静板） | — |
| upstream interface | `housing_to_grille` FIXED 前脸；rear sleeve 嵌 `fan_shroud_ring`（allow_overlap `louver_panel`↔`fan_shroud_ring` + `louver_panel`↔`housing_shell`，矩形框角超出圆 bore） | S3/L470-L477,L555-L568 |
| downstream interface | 近方形面板覆盖圆 bore（`louver_panel_rectangular` dx,dz>0.35; aspect≈1）；薄沿 Y（`louver_panel_thin_depth`<0.08）；在 fan 前方 | S3/L700-L731 |

### Slot B / module side_service_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | `service_door`（visual `door_panel` slab + `door_latch` cam）；housing visual `hinge_barrels`（2 knuckle+leaf+cap）；前栅仍 `fan_grille`(wire_ring) | S4 side_door/L561-L575,L522-L526 |
| internal joints | `housing_to_service_door` REVOLUTE axis=(0,0,-1)，origin=(`HINGE_X`,`HINGE_Y`,0)，lower0 upper1.9（外摆 +X） | S4/L628-L636 |
| upstream interface | hinge barrels FIXED 在 housing 侧壁 hinge line（`hinge_stays_on_frame`）；door 铰于 housing service pocket 后沿 | S4/L818-L832,L874-L882 |
| downstream interface | latch 在 door free edge（`latch_on_free_edge`）；closed door 贴侧壁（`door_seated_on_side`）；hinge barrel 嵌 door edge（allow_overlap `hinge_barrels`↔`door_panel`） | S4/L683-L689,L834-L872 |

### Slot C / module angle_iron_bracket
| emits | 描述 | 来源 |
|---|---|---|
| parts | `mounting_bracket`（visual `bracket_frame`：2 L 腿 + foot/top flange + 前后 cross rail） | S1 P1/L406-L416,L303-L351 |
| internal joints | 无活动；作为 root | — |
| upstream interface | root（无上游） | S1/L599-L605 |
| downstream interface | `bracket_to_housing` FIXED，origin=(0,0,`BODY_H/2`)，shelf top = housing 底（`bracket_below_housing`） | S1/L483-L489,L640-L647 |

### Slot C / module wall_brackets
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wall_bracket_0`(root) + `wall_bracket_1`（各 visual `bracket_body_{i}`：shelf+wall plate+gusset+stop+holes） | S7 wall_brackets/L469-L484 |
| internal joints | `bracket_to_bracket` FIXED（沿 X 间距 `BODY_W-2*INSET`） | S7/L487-L493 |
| upstream interface | `wall_bracket_0` 为 root | S7/L688-L694 |
| downstream interface | `bracket_to_housing` FIXED，housing 居中两托架（`housing_centered_between_brackets`），坐 shelf 顶（`housing_seated_on_bracket_{i}` expect_contact, allow_overlap）；gusset 深度（`bracket_gusset_depth`） | S7/L519-L526,L773-L795 |

### Slot C / module base_feet
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`mount_feet` 是 **housing visual**（4 角底脚） | S2 P2/L298-L302,L231-L243 |
| internal joints | 无；**housing 自身为 root** | S2 |
| upstream interface | housing root（无独立 support） | S2/L260-L356 |
| downstream interface | feet 落地 contact plane = housing 底 -H/2（视觉脚，无 joint） | S2/L231-L243 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| fan_discharge_layout | enum | {front_fan_row, top_discharge_fan} | front_fan_row | choice | 由 deterministic procedural sampler 选 | A 表 |
| front_service_skin | enum | {wire_ring_grille, louver_vent_panel, side_service_door} | wire_ring_grille | choice | sampler 选；top_discharge 时 louver/side 兼容性见 §9 | B 表 |
| mounting_support | enum | {angle_iron_bracket, wall_brackets, base_feet} | angle_iron_bracket | choice | sampler 选；决定 root 拓扑 | C 表 |
| fan_count | int | product 域 [1,20]；sweep/test 覆盖 [1,5] | 2 | conditional | front_fan_row 普通 seed 在 [1,20] 加权抽；sweep overrides 只覆盖 [1,5]；top_discharge_fan 时 ≡1（gating） | S5 three_fans/L50,L66-68,L294-305；产品扩展策略 |
| fan_blade_count | int | [3,6] | 4 | independent | 每 seed 随机抽 3/4/5/6；同一实例内所有 fan rotor 使用同一叶片数（需要时可二期改 per-fan jitter） | `FanRotorGeometry` 参数化 |
| body_w | float | [0.78, 1.25]（N≤5 sweep）；product 域可随 N 派生加宽到 fit | 0.80 | conditional | 随 fan_count 派生下限：`body_w ≥ PANEL_W + N*(2*FAN_BORE_R+gap) + margin`；N>5 时优先缩小 `fan_bore_r`/gap，再派生加宽；resolve_config 内 clamp/fit | S5/L51,L63-68；产品扩展策略 |
| body_h | float | [0.48, 0.56] | 0.52 | independent | 在范围内采样后 clamp（保持 housing_proportions 0.45–0.62） | P1/L636-L638; S2/L380 |
| body_d | float | [0.27, 0.34] | 0.30 | independent | clamp（cabinet_depth 0.26–0.36） | S2/L379 |
| fan_bore_r | float | [0.125, 0.165]（front N≤5）/ product N>5 可缩到 fit / derived（top） | 0.150 | conditional | top_discharge 时 `≤ min(body_w,body_d)/2 - margin`；front 时 `≤ 0.5*usable_x_span/N - gap`，N>5 允许生成更小阵列风机以容纳 6–20 台 | S2/L60; S6/L45；产品扩展策略 |
| grille_ring_count | int | [3,5] | 4 | independent | 仅 wire_ring_grille；不改拓扑等价类（装饰密度），不进 slot_choices | P1/L54 |
| louver_slat_pitch | float | [0.018, 0.028] | 0.022 | independent | 仅 louver_vent_panel；装饰密度，不进 slot_choices | S3/L66 |
| fan_velocity | float | [15, 120] | 20 | independent | CONTINUOUS MotionLimits velocity；不改拓扑 | S2/L344; P1/L523 |
| palette_style | enum | 见 §palette（≥4 colorway） | white_steel | choice | 每 seed 抽一组材质 | 各样本材质段 |
| (—) | constraint | — | — | inequality | `usable_x_span = body_w - panel_w - 2*edge ≥ N*(2*fan_bore_r + fan_gap)`；违反则缩 fan_bore_r 或加 body_w，再不行拒绝重采 | S2/L63-68; S5/L63-68 |
| (—) | constraint | — | — | inequality | top_discharge_fan：`fan_bore_r + shroud ≤ min(body_w,body_d)/2 - 0.02`（顶面装得下） | S6/L45,L91-97 |
| (—) | constraint | — | — | conditional | mounting_support=base_feet → housing 为 root；={angle_iron_bracket,wall_brackets} → support 为 root + bracket_to_housing FIXED | C 表; S1/L483; S7/L520 |

### palette_style（≥4 colorway，取自样本实际材质）
> 每 seed 抽一组，喂 module factory；保证输出色彩多样而非单色。RGBA 取自所读样本。

| colorway | housing / cabinet | grille / skin | fan blades | support / feet / steel | copper valves | 来源 |
|---|---|---|---|---|---|---|
| `white_steel`（P1，weathered white）| `(0.86,0.85,0.82,1)` casing | `(0.18,0.18,0.19,1)` dark grille | `(0.10,0.10,0.11,1)` | `(0.35,0.35,0.37,1)` steel | `(0.62,0.40,0.22,1)` | P1/L399-404 |
| `cream_white`（P2，warm cream）| `(0.880,0.870,0.815,1)` cabinet | `(0.930,0.925,0.905,1)` off-white plastic | `(0.855,0.845,0.800,1)` pale | `(0.300,0.300,0.310,1)` dark feet | — | P2/L73-78 |
| `beige_panel`（米色调）| `(0.86,0.85,0.82,1)` | `(0.20,0.20,0.21,1)` | `(0.10,0.10,0.11,1)` | `(0.32,0.33,0.36,1)` steel（wall bracket 调）| `(0.62,0.40,0.22,1)` | top_discharge/L409-414; wall_brackets/L462-467 |
| `cool_grey`（冷灰壳，深栅）| `(0.72,0.73,0.75,1)` grey cabinet | `(0.16,0.16,0.18,1)` charcoal grille | `(0.12,0.12,0.13,1)` | `(0.40,0.40,0.42,1)` brushed | `(0.60,0.42,0.26,1)` | 派生自 P1/P2 灰阶（合理工业灰）|
| `panel_face_two_tone`（壳体白 + 控制面板深）| `(0.880,0.870,0.815,1)` | `(0.815,0.805,0.755,1)` panel band + `(0.620,0.640,0.660,1)` badge | `(0.855,0.845,0.800,1)` | `(0.300,0.300,0.310,1)` | — | P2/L76-78 |

## Multiplicity / Copy Logic

**一根多重性轴：`fan_count`（前排轴流风机数）。**

- `count_param`：`fan_count`。
- `N_range`：本小类本轴 **product 域 [1, 20]**；本批证据覆盖 P1 N=1、P2 N=2、three_fans N=3，模板实现需写成通用循环而不是 curated 表。**sweep/test 域只覆盖 [1, 5]**：若 N=1..5 的复制、命名、joint、placement、allow_overlap 都通过，则 N=6..20 属同一循环外推，普通 seed 可生成但不作为 sweep 必测范围。
- sampling domain（权重档）：front_fan_row 普通 seed 在 **1..20** 抽样，建议小 N 高频、长尾覆盖大 N（例如 1/2/3/4/5 权重较高，6..20 合计长尾）；sweep overrides 固定覆盖 `fan_count∈{1,2,3,4,5}`。top_discharge_fan 时 `fan_count≡1`（gating 强制，不抽）。
- copied object：fan rotor part `fan_{i}`（`FanRotorGeometry` rotor visual `fan_{i}_rotor`，`blade_count=fan_blade_count`）+ 对应前脸圆 bore + 对应 `_concentric_grille(FAN_X_POSITIONS[i])`（或 louver 时 per-fan 面板 / fallback，见兼容矩阵）。
- naming：part `fan_{i}`（i=0..N-1）；visual `fan_{i}_rotor`；joint `housing_to_fan_{i}`；grille visual `grille_{i}`（three_fans 已定此命名）。
- placement：沿 X 等距：`FAN_X_POSITIONS[i] = USABLE_X0 + GRILLE_SPAN*(i+0.5)/N`，`USABLE_X0 = -W/2 + PANEL_W`，`USABLE_X1 = W/2 - 0.020`（three_fans/L63-68）。所有 fan 同高 `FAN_CTR_Z`，同 recess `FRONT_Y-0.015`。
- joint policy：每个 `housing_to_fan_{i}` 一律 **CONTINUOUS axis=(0,1,0)**，相同 MotionLimits(effort2, velocity≈20)。各 rotor 独立旋转（无耦合）。
- source/gating：front_fan_row 专属；top_discharge_fan gating 到 N≡1。`body_w` 与 `fan_bore_r` 随 N 派生 fit（见 §7 inequality）；N>5 不进入 sweep 必测，但必须走同一 build loop。

## 拓扑多样性审计

总组合数（拓扑等价类，不含连续 scale）：

- A=front_fan_row × fan_count∈{1..20} = 20 个产品拓扑；sweep 验收覆盖 fan_count∈{1..5} = 5 个拓扑（part/joint 数随 N 变）
- A=top_discharge_fan（fan_count≡1）= 1 个拓扑
- → A×fan_count 维度 = **21** 个产品 part-tree；sweep 验收维度 = **6** 个不同 part-tree。
- × B{wire_ring_grille, louver_vent_panel, side_service_door} = 3
- × C{angle_iron_bracket, wall_brackets, base_feet} = 3

**产品原始叉乘 = 21 × 3 × 3 = 189**；sweep 原始叉乘 = 6 × 3 × 3 = 54。扣除 §兼容矩阵非法格（见下）后，sweep 合法拓扑组合仍 ≥10 ✓。

理由：仅 sweep 覆盖的 A×fan_count 就给 6 个 part-tree（front fan part/joint 数 1/2/3/4/5 + top 单风机异轴）；B 改 fan_grille part 组成 / 增 service_door part / 增 housing hinge barrels；C 改 root/support part 数（0/1/2 个独立 support part）。三槽 + multiplicity 正交（除少数 gating），sweep 合法组合数远超 10；product 域 6..20 是同一复制循环的长尾外推。

seed_domain_policy：`procedural_first`。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 deterministic procedural sampling：① 按权重抽 A（front_fan_row 0.7 / top_discharge_fan 0.3）；② A=front_fan_row 时普通 seed 抽 `fan_count∈[1,20]`（小 N 高频、6..20 长尾），sweep/regression overrides 只枚举 `fan_count∈{1,2,3,4,5}`，A=top_discharge_fan 时 `fan_count=1`；③ 抽 `fan_blade_count∈{3,4,5,6}`；④ 抽 B、C（各 1/3 均匀，受兼容矩阵 gating）；⑤ 抽 palette_style；⑥ 采 independent 连续 scale（body_h, body_d, fan_velocity, grille_ring_count/louver_slat_pitch）；⑦ 派生 conditional/inequality（body_w 随 N、fan_bore_r 随面/ N、root 策略随 C）并在 `resolve_config` clamp/投影/拒绝重采。`slot_choices_for_seed` 记录 (A, fan_count, fan_blade_count, B, C, palette) — 连续 scale 不进（不改拓扑等价类）。
Topology target：1000-seed slot choice tuple distinct 目标 ≥50（sweep 域约 50+ 合法组合；product 域 6..20 提供更多长尾拓扑，但不强制 sweep 全覆盖）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
若使用 regression overrides：**none**（无已知回归；首次实现）。
Controlled local parameterization：关键连续 scale = `body_w`(派生于 fan_count 下限)、`body_h`/`body_d`(independent clamp)、`fan_bore_r`(conditional 随面/N)、`fan_blade_count`(3–6 independent discrete)、`fan_velocity`(independent)、`grille_ring_count`/`louver_slat_pitch`(module-local density)。全部在 `resolve_config` clamp/派生，受 housing_proportions(0.45–0.62 H)、cabinet_width/depth、usable_x_span 不等式、top 顶面装得下不等式约束，**不破坏** InterfaceSpec（grille FIXED 对中 / fan CONTINUOUS 轴 / support FIXED 抬高）/ MatingContract（rotor hub captured / grille 嵌 shroud / housing 坐 shelf）/ multiplicity（product `fan_count` clamp [1,20]；sweep overrides [1,5]）。按 §7 约束类型声明依赖（body_w=conditional(fan_count)、fan_bore_r=conditional(face,N)、其余 independent），遵循采样契约（先 independent → 派生 conditional → 投影 inequality → 拒绝重采）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 抽序 A→fan_count→fan_blade_count→B→C→palette→连续 scale；fan_count 普通域 1..20、小 N 偏多；sweep 只测 1..5；compatibility gates 见下 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | top_discharge_fan ⇒ fan_count≡1（互斥多重性）；louver_vent_panel 默认对应单大面板覆盖（与 fan_count>1 需 per-fan louver，见 fallback）；base_feet ⇒ housing 为 root（无 bracket_to_housing）；side_service_door 不改 fan/grille 前栅拓扑（与 wire_ring 并存）| 无悬空、无 fan 轴错、无 grille 漂浮、root 唯一、普通域 N≤20、sweep N≤5 |
| controlled local variation | body_w/h/d、fan_bore_r、fan_blade_count、fan_velocity、ring/slat density 在 resolve_config clamp/派生 | 比例变化不破接口 / clearance / joint origin / 类别 identity |
| regression overrides | none | — |
| random sweep | 初版 seeds 0-49；成熟审计 0-999 |与 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A fan_discharge_layout | 2 module + fan_count(product 1-20; sweep 1-5) 多重性 → product 21 / sweep 6 拓扑 | yes | yes（含多重性）| front_fan_row(单/多) + top_discharge_fan |
| B front_service_skin | 3 | yes | yes | wire_ring / louver / side_door |
| C mounting_support | 3 | yes | yes | angle_iron / wall_brackets / base_feet |

兼容矩阵（互斥 / fallback）：
- **top_discharge_fan × fan_count>1**：非法 → gating 强制 `fan_count=1`（顶面单风机）。
- **top_discharge_fan × louver_vent_panel**：louver 是前脸矩形板，与顶排风口不对位 → fallback 到 wire_ring（顶面圆栅，top_discharge 本就用 `_grille` 圆栅）。即 top_discharge 时 B 限 {wire_ring_grille, side_service_door}。
- **louver_vent_panel × fan_count>1**：单大百叶板默认只覆盖一个 bore；N>1 时 fallback 为**逐 fan per-fan louver panel**（复用 `_louver_grille_geometry` × N）或退回 wire_ring（更安全）。初版安全策略：louver 仅在 fan_count=1 时启用，N>1 时 B 抽到 louver 则 fallback wire_ring；若二期开 per-fan louver，必须按 N 复制到每个 bore，N=1..5 sweep 验证即可外推到 N=20。
- **base_feet × wall_brackets**：互斥（同为 C 槽，单选）。
- **side_service_door** 与任何 A、C 正交并存（仅升级侧检修件）。

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C + fan_count + fan_blade_count + palette）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos（top_discharge⇒N=1；louver⇒N=1 否则 fallback wire；base_feet⇒housing root）
- optional regression overrides are sparse and justified（none）
- final template 不无限轮换 curated/modulo 表作为主 seed domain
- controlled local scale params（body_w/h/d, fan_bore_r, fan_blade_count, fan_velocity, density）clamped，不破接口 / clearance / joint origin / multiplicity
- cross-part scale deps（body_w=conditional(fan_count)、fan_bore_r=conditional(face,N)、usable_x_span inequality、top 顶面 inequality）在 resolve_config 求解
- critical InterfaceSpec/MatingContract 存在：grille `housing_to_grille` FIXED 对中 fan 轴；rotor hub captured（grille rear spigot 或 motor mount，expect_contact + allow_overlap）；support `bracket_to_housing` FIXED 抬高 / housing 坐 shelf（expect_contact）；side_door hinge barrels 在 housing
- key joints 类型/轴/range：`housing_to_fan_{i}` CONTINUOUS axis=(0,1,0)（front）或 (0,0,1)（top）；`housing_to_service_door`/`housing_to_service_panel` REVOLUTE axis=(0,0,-1) lower0 upper1.9；support joints FIXED
- copied objects 遵循命名/placement：`fan_{i}` + `housing_to_fan_{i}` + `grille_{i}`，沿 X 等距 `FAN_X_POSITIONS`；sweep 覆盖 i=0..4，product 域同循环外推到 i=19

## Reject cases

- fan rotor 不绕喉口法线 CONTINUOUS（错成 REVOLUTE 或固定盘）→ 失去冷凝风机身份。
- fan 轴向与所在面不符：front 用 +Z 或 top 用 +Y（rotor 朝向 / joint axis 错配）。
- grille 漂浮在 fan 前方不嵌 `fan_shroud_ring`（无 expect_contact，悬空 island）。
- rotor hub 不被任何件 captured（grille rear spigot / motor mount 缺失）→ rotor 悬空、缺承托。
- `fan_count>20`、`fan_count<1`、sweep 误把 N=6..20 当必测失败项，或 top_discharge 配 N>1（多重性越界 / gating 失效）。
- `fan_blade_count` 不在 3..6，或同一 rotor 叶片数与配置不一致。
- housing 非中空（实心盒）或前脸不开 bore（fan 被实壁挡住 / 无喉口）。
- multiple roots：support 与 housing 都被当 root（base_feet 时还另建 bracket，或 bracket 家族 housing 不挂在 support 下）。
- side_service_door 的 hinge barrels 随门飞走（不留在 housing frame 侧 → hinge 拓扑错）。
- louver_vent_panel 配 fan_count>1 时单板只盖一个 bore，其余 bore 裸露无栅（未 fallback）。
- 比例越界：housing H 超出 0.45–0.62 或 W 装不下 N 个风机（usable_x_span 不等式违反未回缩）。

## 与相邻类别的边界

- **不该混入：`air_conditioner`（壁挂分体式空调室内机 / mini-split indoor unit，已存在 slug）**——这是**最关键的区分**。`air_conditioner` 是**室内机**：横长玻璃白塑壳**背面贴墙（y=0）、底坐 z=0**，下前缘出风区是一组**摆动导风叶（louver vanes，REVOLUTE 绕 X 或 Z 摆动 ±45°）**，大前脸是**铰接检修盖**（上掀/蛤壳/底翻），内部是 cross-flow 风道 + 滤网腔，**没有可见旋转 rotor、没有铜管阀、没有落地/挂墙金属支架**，活动语义是**导风叶摆动 + 检修盖开合**。本 `ac_outdoor_unit` 是**室外机**：矩形钣金机箱 + **可见轴流风机 rotor 连续自转（CONTINUOUS，不是摆动叶）** + 防护栅圈/百叶 + 侧检修门 + **冷媒铜管阀** + **金属支架/底脚承托**，活动语义是**风机旋转 + 检修门开合**。判据：有无连续自转的 axial fan rotor + 铜管阀 + 支架 = 室外；摆动导风叶 + 贴墙壳 + 检修盖 = 室内。
- **不该混入：排气扇 / 换气扇 / 工业轴流风机（exhaust fan / box fan）**——它们也有旋转 rotor + 栅，但**无冷凝机箱、无铜管阀、无侧检修门、无机组级机箱身份**，多为薄框风扇。本类必须是带**中空机箱 + 冷媒接口 + 承托支架**的整台机组。
- **不该混入：通风百叶 / facade vent grille（无活动件的纯百叶）**——louver_vent_panel 只是本类的一个**前栅 skin**，本体仍须有旋转风机 + 机箱；纯静态百叶面板不是空调室外机。
- **不该混入：热泵热水器 / 立式柜机（standing AC / heat-pump cylinder）**——立筒或落地柜形态、出风结构不同，非矩形横置冷凝箱 + 前/顶圆风机身份。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核。开放问题：(1) Slot B 的 side_service_door 与默认 service_panel 功能重叠——是否把"侧检修件"独立成第 4 槽，还是按现案折入 B（前栅正交、侧门升级）？(2) louver_vent_panel × fan_count>1 初版采"仅 N=1 启用、否则 fallback wire_ring"的安全策略，是否接受（更激进的 per-fan louver 留待模板期）？(3) C=base_feet 时无 service_valves/service_panel（P2 本无），是否保留这一"落地家族省略侧检修件"的派生，或统一所有家族都带侧检修件？(4) top_discharge_fan 单候选携带 fan_count≡1，已说明降级理由（顶面单风机），不再拆 slot。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | parent P1 / A,B,C | front single fan + wire_ring_grille + angle_iron_bracket + service_panel/valves | rec_build-...-air-_..._0710784e | L396-L544（assembly）, L69-L351（helpers） | bracket-root 家族基线；wire grille（B）；angle_iron_bracket（C）；service_panel REVOLUTE + 铜管阀 |
| S2 | parent P2 / A,C | front dual fan + concentric grille(housing visual) + base_feet | rec_build-...-air-_..._0ffac329 | L260-L356（assembly）, L81-L243（helpers） | housing-root 家族基线；front_fan_row N=2；base_feet（C）；palette cream_white |
| S5 | A multiplicity | front_fan_row N=3（`fan_{i}` loop） | rec_ac_unit_var_three_fans | L141-L189, L289-L317 | fan_count 多重性证据 + `fan_{i}`/`housing_to_fan_{i}`/`grille_{i}` 命名与等距 placement |
| S6 | A | top_discharge_fan | rec_ac_unit_var_top_discharge_fan | L69-L296, L457-L531 | 顶面 +Z 单风机 module（异轴、单风机 gating） |
| S3 | B | louver_vent_panel | rec_ac_unit_var_louvered_front | L148-L179, L415-L428 | 矩形百叶前栅 module（VentGrilleGeometry） |
| S4 | B | side_service_door | rec_ac_unit_var_side_service_door | L311-L388, L561-L575, L628-L636 | 侧检修门升级（hinge barrels + cam latch + REVOLUTE 门） |
| S7 | C | wall_brackets | rec_ac_unit_var_wall_brackets | L312-L414, L469-L526 | 挂墙托架×2（shelf+gusset，多 support part） |

## 模板实现备注（可选）

- **公共 root 裁决**：模板以 `housing`-root 为默认（P2 风格）；C 选 angle_iron_bracket/wall_brackets 时改 support 为 root + `bracket_to_housing` FIXED（origin 抬 housing `+BODY_H/2`），C 选 base_feet 时 housing 即 root + feet 作 housing visual。`slot_choices_for_seed` 记 C 即定 root 拓扑。
- **fan 命名统一**：P2 的 `left_fan`/`right_fan` 在模板里一律 `fan_0`/`fan_1`（three_fans 已用 `fan_{i}`），joint `housing_to_fan_{i}`，grille visual `grille_{i}`。
- **captured-pin / embed allow_overlap（element-scoped）**：每 fan 需声明 (a) rotor hub ↔ grille rear spigot 或 motor_mount（rotor 承托）；(b) rotor ↔ housing_shell（recessed in hollow cabinet，P2 风格）；grille rim/sleeve ↔ `fan_shroud_ring`（grille 嵌 venturi）；louver_panel 另需 ↔ housing_shell（矩形框角超圆 bore）；side_door hinge_barrels ↔ door_panel；service_valves ↔ housing_shell（穿侧壁）；wall_brackets：housing_shell ↔ bracket_body_{i}（坐 shelf）。**每个 A×B×C×N 组合都要复制相应 allow_overlap**（参考 overlap QC 一次性声明所有接口对的经验）。
- **helper 共享**：`_concentric_grille`（B=wire 前脸 / top_discharge 顶面圆栅）、`_fan_rotor_mesh`、`_housing_shell`（front bore 循环 vs top bore）、`_fan_shroud_ring`、`_fan_motor_mount`（front +Y 横撑 vs top 十字悬挂）按 A/面切换；`VentGrilleGeometry`（louver）单独。
- **MATURE_TEMPLATE_METHOD 参考候选**（模板期再选 1–3 深读）：选 multiplicity + parallel-children + CONTINUOUS rotor 拓扑相近者（如已有的风机/旋转 rotor 多重性模板），不按类别名相似选。
