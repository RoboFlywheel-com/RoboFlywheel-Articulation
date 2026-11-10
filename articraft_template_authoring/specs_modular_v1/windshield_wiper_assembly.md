# Modular Spec — windshield_wiper_assembly

## 元信息
| 项 | 值 |
|---|---|
| slug | `windshield_wiper_assembly` |
| template path | `agent/templates/windshield_wiper_assembly.py` |
| test path (optional) | `tests/agent/test_windshield_wiper_assembly_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：核心由 **architecture** slot 决定运动学拓扑（单 spindle 直驱 vs 双 spindle 外露 4-bar 联动 vs 双 spindle cowl 内 primary/cross-link 联动），其余 slot（motor_housing / arm_shape / blade_carrier）作为正交的几何/材质轴；arm_count（1 或 2）由 architecture 派生（multiplicity-by-architecture）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 28 |
| read_count | 28 |
| read_scope | all 5-star samples in this category (`model.py` 全量精读，分 3 批并行 Explore；`revision.json` / `record.json` / `prompt.txt` / category metadata 同步) |
| source_index_policy | only adopted module sources are indexed below |

全量阅读后的结构族分布（28 个样本）：

| 轴 | 观察到的真实结构变体 | 样本计数 |
|---|---|---|
| architecture | direct_drive_single_arm (motor↔spindle↔arm↔blade) / dual_arm_tandem_cross_car (motor crank→drag link→2 spindles+cross link) / dual_arm_cowl_primary_cross_link (motor crank→primary link/cross link→2 spindles) | 21 / 6 / 1 |
| motor_housing | cylindrical_can_motor (Cylinder body) / cast_box_motor_with_gearbox (Box housing + Cylinder can) / rectangular_turret_housing (flat box turret) / pedestal_motor (tall pedestal) | 12 / 11 / 3 / 2 |
| arm_shape | flat_strap_arm (Box bar) / tapered_lever_arm_with_extrude (ExtrudeGeometry profile) / tube_spine_composite_arm (Box shell + tube_from_spline_points spine) / lightened_lattice_arm (ExtrudeWithHolesGeometry) | 12 / 7 / 8 / 1 |
| blade_carrier | flat_squeegee_with_yoke (Box body + Cylinder pivot + rubber strip) / frame_with_multiple_pivots (bridge + harness + claws) / beam_style_aero (aero airfoil section_loft / sweep_profile_along_spline) | 13 / 12 / 3 |
| arm_count | 1 / 2 | 22 / 6 |
| pivot axis | spindle_sweep 全部沿 Z; blade_roll 多数沿 X，少数 (1) 沿 Y | — |
| joint range | sweep ±0.95 ~ ±1.35 主流；少数单向 0..1.35；blade_roll ±0.30 ~ ±0.65 | 全部 |
| 配件（不构成 slot） | tension_spine tube / claws / coil_spring LatheGeometry / rubber_strip ExtrudeGeometry / park-position offset | 散落 |

## 核心身份

`windshield_wiper_assembly` 的不变身份：**一个由 motor 驱动、通过 spindle (REVOLUTE 绕 Z 轴) 把 arm 在 windshield 平面内扫动 (sweep)，arm 末端经第二个 REVOLUTE (绕 X 或 Y 水平轴，blade_roll/pitch) 承载 blade carrier 与 rubber squeegee 的雨刮机构。** 最小合法体 = motor housing（含 mounting base）+ spindle + sweep arm + blade carrier；至少 2 个 REVOLUTE joint（sweep + roll）；sweep 轴必须竖直 Z，blade roll 轴必须水平。

默认成熟域：汽车前/后窗雨刮总成，包括单 arm 直驱、双 arm 跨车 4-bar 联动、双 arm cowl 内 primary/cross-link 联动；可视作摩托/船/工程车/巴士的小型化或加大版。无 squirter / washer fluid 系统、无 rain sensor、无 heated wiper — 这些不属于本类别 identity 范围。

不该混入：见“与相邻类别的边界”。

## 槽位 + 候选模块表

### Slot A：architecture（决定运动学拓扑、arm 数、是否含 linkage）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| direct_drive_single_arm | rec_windshield_wiper_assembly_06bc1be7674340859b60b037db3bee78 | L217-L234 | eligible if compatible | motor 直驱 spindle（无中间 linkage），1 arm + 1 blade；最简、最常见 |
| dual_arm_tandem_cross_car | rec_windshield_wiper_assembly_2f6e9a08fb3940d58acf2aa2e8ba9530 | L159-L396 | eligible if compatible | motor crank (CONTINUOUS) → drag_link → 左 spindle；cross_link → 右 spindle；2 arms + 2 blades；驾驶 + 乘客双臂联动 |
| dual_arm_cowl_primary_cross_link | rec_windshield_wiper_assembly_0003 | L209-L650 | eligible if compatible | motor_drive (CONTINUOUS) → drive_crank → primary_link + cross_link → left/right wiper modules；2 arms + 2 aero blades；cowl 内联动与外露 drag/cross 4-bar 来源不同 |

注：pantograph_dual_arm（rec_…_291e082 L417-L434，单 spindle + 2 yokes 平行联动）是 direct_drive_single_arm 的 module-local blade variant（在 blade slot 实现 dual_yoke pantograph blade），不单列。硬约束：每 slot ≥3 candidate（这里 3 个）；每个有真实 5 星 source；candidate 间是 motor / linkage / arm_count 拓扑差异，非装饰差异。

### Slot B：motor_housing（电机外壳 + 集成 mounting base，决定 spindle 接口姿态与 base 占地）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| cylindrical_can_motor | rec_windshield_wiper_assembly_0001 | L45-L50 | eligible if compatible | 单 Cylinder motor_can + 集成或独立 flat_plate base；最常见 |
| cast_box_motor_with_gearbox | rec_windshield_wiper_assembly_06bc1be7674340859b60b037db3bee78 | L38-L79 | eligible if compatible | Box gearbox_housing + Cylinder motor_can 复合；base 与 housing 一体；spindle 从 gearbox 顶面 / 侧面伸出 |
| rectangular_turret_housing | rec_windshield_wiper_assembly_2c145b57c5ed4b0c8d85be8eafda7707 | L15-L33 | eligible if compatible | 平 Box 转台外壳（无明显 motor_can），bracket 延伸到 spindle；薄、低 profile |
| pedestal_motor | rec_windshield_wiper_assembly_7f7c8dbfbedf45bfb12f58e840c84883 | L28-L63 | eligible if compatible | 高 pedestal 支撑 + 大半径 motor_can（radius ~0.045）；适合较高 sweep arm pivot |

### Slot C：arm_shape（spindle ↔ blade 之间的扫动臂形态，决定 chord 视觉与 arm primitive）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_strap_arm | rec_windshield_wiper_assembly_0001 | L58-L91 | eligible if compatible | 平 Box bar (chord × thickness × length) + 可选 hub；最简 |
| tapered_lever_arm_with_extrude | rec_windshield_wiper_assembly_257ea157639f455e841b3a5b2e7d9bbf | L129-L165 | eligible if compatible | ExtrudeGeometry 自定义 profile（lever 形 / leaf 形 / 锥形），含 raised_spine + tip_fork |
| tube_spine_composite_arm | rec_windshield_wiper_assembly_06bc1be7674340859b60b037db3bee78 | L82-L160 | eligible if compatible | Box shell + tube_from_spline_points spring spine（雨刮 hood 风格），含 sweep_profile_along_spline 弯曲外壳 |
| lightened_lattice_arm | rec_windshield_wiper_assembly_291e082ab0b34d1cb8d1d37d83a9fe5f | L157-L243 | eligible if compatible | ExtrudeWithHolesGeometry 镂空 arm + tapered_arm + spring_anchor + coil_spring LatheGeometry；高仿真 |

### Slot D：blade_carrier（雨刮 blade / squeegee 末端结构，承载 rubber strip）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_squeegee_with_yoke | rec_windshield_wiper_assembly_2c145b57c5ed4b0c8d85be8eafda7707 | L55-L68 | eligible if compatible | Box carrier_frame + Cylinder roll_barrel + 单 rubber_blade Box；最简 |
| frame_with_multiple_pivots | rec_windshield_wiper_assembly_06bc1be7674340859b60b037db3bee78 | L162-L215 | eligible if compatible | bridge + harness + 2-4 claws（claw_inner/outer_right/left）+ rubber_strip；复杂传统 frame blade |
| beam_style_aero | rec_windshield_wiper_assembly_0003 | L488-L535 | eligible if compatible | aero airfoil 截面（sweep_profile_along_spline 或 section_loft）+ spoiler + 隐藏 mounting；现代 beam 风格 |

硬约束：每 slot ≥3 candidate；A=3、B=4、C=4、D=3；均有真实 5 星 `model.py:Lx-Ly` 来源；candidate 间为真实 part tree / joint topology / primitive 差异。

## 槽位图（slot graph）

pattern: mixed

```
[Slot B motor_housing]（cylindrical_can / cast_box_gearbox / rectangular_turret / pedestal）
   │
   ├─ (mounting base, 由 motor_housing 内部派生 visual)
   │
   ▼
[Slot A architecture] determines linkage and joint chain:

  direct_drive_single_arm (arm_count=1):
    motor_housing ──spindle_sweep(REVOLUTE, Z, ±0.95..1.35)──> [arm part: Slot C arm_shape]
                                                                 │
                                                                 └─ blade_roll(REVOLUTE, X/Y, ±0.30..0.65) ──> [blade part: Slot D blade_carrier]

  dual_arm_cowl_primary_cross_link (arm_count=2):
    motor_housing/cowl ──motor_drive(CONTINUOUS, Z)──> [drive_crank part]
                                                         │
                                                         ├─ drive_to_primary_link(FIXED/captured crank pin) ──> [primary_link part]
                                                         │                                                   │
                                                         │                                                   └─ primary_link socket drives left_wiper_module
                                                         └─ left_wiper_module ──left_to_cross_link(FIXED/captured pin)──> [cross_link part]
                                                                                                                   │
                                                                                                                   └─ right_wiper_module receives paired sweep
    cowl ──left_wiper_sweep(REVOLUTE, Z)──> [arm_0: Slot C] ──blade_roll_0──> [blade_0: Slot D]
    cowl ──right_wiper_sweep(REVOLUTE, Z)──> [arm_1: Slot C] ──blade_roll_1──> [blade_1: Slot D]

  dual_arm_tandem_cross_car (arm_count=2):
    motor_housing ──motor_drive(CONTINUOUS, Z)──> [motor_crank part]
                                                    │
                                                    └─ crank_to_drag_link(REVOLUTE, Z) ──> [drag_link part]
                                                                                             │
                                                                                             └─ drag_link_to_spindle_0(REVOLUTE, Z) ──> [spindle_0]
                                                                                                                                         │
                                                                                                                                         └─ spindle_0_to_cross_link(REVOLUTE, Z) ──> [cross_link]
                                                                                                                                                                                    │
                                                                                                                                                                                    └─ cross_link_to_spindle_1(REVOLUTE, Z) ──> [spindle_1]
                                                                                             │
                                                                                             ├─ spindle_0_sweep(REVOLUTE, Z) ──> [arm_0: Slot C] ──> blade_roll_0 ──> [blade_0: Slot D]
                                                                                             └─ spindle_1_sweep(REVOLUTE, Z) ──> [arm_1: Slot C] ──> blade_roll_1 ──> [blade_1: Slot D]
```

接口点位与跨 slot joint：

- **motor_housing → spindle**：恒水平外壳顶/侧 bearing seat；spindle_sweep 关节 origin 落 housing bearing seat 中心，axis = (0,0,1)。
- **spindle → arm**：spindle hub + arm hub captured 关系（element-scoped `allow_overlap`）；arm length 沿水平方向延伸。
- **arm → blade_carrier**：arm tip 上的 yoke / fork 抱住 blade carrier 的 trunnion / pivot；blade_roll 关节 origin 落 arm tip pivot；axis 水平（默认 X，少数 Y；不允许 Z）。
- **dual_arm_tandem_cross_car 内部 linkage**：motor_crank → drag_link → spindle_0；spindle_0 → cross_link → spindle_1；linkage 关节/捕获 pin 的 axis 都是 (0,0,1)（windshield 平面 4-bar），origin 落各 pivot pin。
- **dual_arm_cowl_primary_cross_link 内部 linkage**：drive_crank 与 primary_link/cross_link 保留来源中的 fixed/captured 接触语义，同时 left/right wiper modules 各自以 Z 轴 REVOLUTE sweep。

互斥/可选/派生：

- `direct_drive_single_arm` → arm_count = 1，无 linkage parts，无 motor_drive joint（spindle_sweep 自己是被驱动 joint）。
- `dual_arm_cowl_primary_cross_link` → arm_count = 2，含 drive_crank + primary_link + cross_link parts；motor_drive 为 CONTINUOUS，left/right wiper sweep 为两个 REVOLUTE，primary/cross link 接口按来源保留 captured/fixed contact 语义。
- `dual_arm_tandem_cross_car` → arm_count = 2，含 motor_crank + drag_link + cross_link parts；4 个 linkage REVOLUTE + 2 个 spindle_sweep + 2 个 blade_roll = 8 个 joint。
- `pedestal_motor` ⇒ spindle 较高，配 tube_spine_composite_arm 或 lightened_lattice_arm 视觉更协调（soft prefer）。
- `rectangular_turret_housing` 偏紧凑 → 优先配 flat_strap_arm（soft prefer）。
- `cast_box_motor_with_gearbox` 兼容所有 architecture（最通用）。
- blade_roll 轴可为 X 或 Y（spec 默认 X，rec_…_8377 / rec_…_91f4 用 Y，少数）；template 实现 X 为主、Y 作 module-local variant。

## 每槽位 Module Emits / Interfaces

### Slot B / module cylindrical_can_motor
| emits | 描述 | 来源 |
|---|---|---|
| parts | motor_housing（Cylinder motor_can + flat_plate mounting base + optional bearing collar） | rec_…_0001 / L45-L50；rec_…_7be21 L37-L79 |
| downstream interface | top bearing seat（供 spindle / motor_crank）；axis = Z | rec_…_0001 / L45-L50 |

### Slot B / module cast_box_motor_with_gearbox
| emits | 描述 | 来源 |
|---|---|---|
| parts | gearbox_housing(Box) + motor_can(Cylinder) + integrated mounting flange + bearing tower | rec_…_06bc1be / L38-L79；rec_…_257ea L79-L127；rec_…_2fff L31-L66 |
| downstream interface | spindle bearing on top of gearbox（spindle_sweep origin） | rec_…_06bc1be / L74-L79 |

### Slot B / module rectangular_turret_housing
| emits | 描述 | 来源 |
|---|---|---|
| parts | 平 Box turret housing + bracket arm 延伸到 spindle | rec_…_2c145b5 / L15-L33；rec_…_f175 L29-L64 |
| downstream interface | spindle bearing 在 bracket 末端，向 +y/+x offset | rec_…_2c145b5 / L25-L33 |

### Slot B / module pedestal_motor
| emits | 描述 | 来源 |
|---|---|---|
| parts | tall pedestal Box + 大 motor_can Cylinder + flat base | rec_…_7f7c8 / L28-L63 |
| downstream interface | spindle 在高 pedestal 顶 | rec_…_7f7c8 / L55-L63 |

### Slot C / module flat_strap_arm
| emits | 描述 | 来源 |
|---|---|---|
| parts | arm part（Box bar + Cylinder hub at spindle end + Cylinder pivot at tip） | rec_…_0001 / L58-L91；rec_…_dc72 L66-L108 |
| internal helpers | 无（纯 primitive） | 同上 |

### Slot C / module tapered_lever_arm_with_extrude
| emits | 描述 | 来源 |
|---|---|---|
| parts | ExtrudeGeometry profile arm + tip_fork + spindle hub | rec_…_257ea / L129-L165；rec_…_7be21 L81-L134；rec_…_d5a7a L74-L96；rec_…_eaf5e L93-L139 |
| internal helpers | ExtrudeGeometry / mesh_from_geometry / rounded_rect_profile | 同上 |

### Slot C / module tube_spine_composite_arm
| emits | 描述 | 来源 |
|---|---|---|
| parts | Box shell + tube_from_spline_points spring spine + sweep_profile_along_spline curved hood + tip fork | rec_…_06bc1be / L82-L160；rec_…_2fff L68-L131；rec_…_8377 L104-L137；rec_…_73998 L86-L126 |
| internal helpers | tube_from_spline_points / sweep_profile_along_spline / rounded_rect_profile | 同上 |

### Slot C / module lightened_lattice_arm
| emits | 描述 | 来源 |
|---|---|---|
| parts | ExtrudeWithHolesGeometry 镂空 arm + tapered_arm + spring_anchor + coil_spring LatheGeometry | rec_…_291e082 / L157-L243 |
| internal helpers | ExtrudeWithHolesGeometry / LatheGeometry / tube_from_spline_points | 同上 |

### Slot D / module flat_squeegee_with_yoke
| emits | 描述 | 来源 |
|---|---|---|
| parts | blade carrier part（Box carrier_frame + Cylinder roll_barrel + 1 rubber_blade Box / ExtrudeGeometry） | rec_…_2c145b5 / L55-L68；rec_…_7be21 L136-L196；rec_…_dc72 L109-L144；rec_…_eaf5e L141-L184 |
| upstream interface | roll_barrel ↔ arm tip yoke captured | rec_…_2c145b5 / L60-L68 |

### Slot D / module frame_with_multiple_pivots
| emits | 描述 | 来源 |
|---|---|---|
| parts | bridge + harness + 2-4 claws + rubber_strip；含 hinge_barrel；可选 spoiler | rec_…_06bc1be / L162-L215；rec_…_0ee53 L129-L175；rec_…_2fff L133-L186；rec_…_0001 L94-L114 |
| internal | claws 数 2 或 4（端点 + 中间） | 同上 |
| upstream interface | bridge center hinge_barrel ↔ arm tip fork | 同上 |

### Slot D / module beam_style_aero
| emits | 描述 | 来源 |
|---|---|---|
| parts | aero blade body via section_loft / sweep_profile_along_spline + airfoil spoiler + rubber strip + hidden mounting; mesh-based | rec_…_0003 / L488-L535；rec_…_75aee L286-L340；rec_…_76d79 L387-L410 |
| internal helpers | section_loft / sweep_profile_along_spline / rounded_rect_profile / aero airfoil profile | 同上 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| architecture (A) | enum | direct_drive_single_arm / dual_arm_cowl_primary_cross_link / dual_arm_tandem_cross_car | sampled | deterministic procedural sampler | Slot A |
| motor_housing (B) | enum | cylindrical_can_motor / cast_box_motor_with_gearbox / rectangular_turret_housing / pedestal_motor | sampled | architecture 不强 gating（dual_arm 偏 cast_box / cylindrical_can） | Slot B |
| arm_shape (C) | enum | flat_strap_arm / tapered_lever_arm_with_extrude / tube_spine_composite_arm / lightened_lattice_arm | sampled | motor_housing 弱 soft prefer | Slot C |
| blade_carrier (D) | enum | flat_squeegee_with_yoke / frame_with_multiple_pivots / beam_style_aero | sampled | 无强 gating | Slot D |
| arm_count | int (derived) | {1, 2} | 由 architecture 派生 | direct_drive → 1; dual_arm_cowl_primary_cross_link / dual_arm_tandem → 2 | A |
| blade_roll_axis | enum | x_horizontal / y_horizontal | x_horizontal | 大多数 X；Y 作 module-local variant | rec_…_8377 / rec_…_91f4 |
| spindle_sweep_range | float pair | (lower, upper) ∈ ([-1.40,-0.00], [0.40, 1.50]) | (-1.10, 1.10) | dual_arm 左/右镜像；direct_drive 多对称 | 全样本 |
| blade_roll_range | float pair | (lower, upper) ∈ ([-0.65,-0.05], [0.05, 0.65]) | (-0.35, 0.35) | 静态时 0；roll 跟 windshield 曲率 | 全样本 |
| motor_drive_park_offset | float | [-2.65, 2.65] | 0.0 | 仅 cranked architecture；park 位置 | rec_…_0002 / rec_…_2f6e |
| arm_length | float | [0.18, 0.50] | 0.32 | sweep 半径 | 全样本 |
| arm_chord | float | [0.014, 0.040] | 0.022 | arm 横截面宽 | 全样本 |
| arm_thickness | float | [0.006, 0.016] | 0.010 | arm 厚度 | 全样本 |
| blade_length | float | [0.20, 0.60] | 0.36 | blade carrier 长 | 全样本 |
| blade_chord | float | [0.015, 0.030] | 0.020 | blade 厚 (横截面) | 全样本 |
| spindle_radius | float | [0.006, 0.014] | 0.009 | spindle pin radius | 全样本 |
| motor_radius | float | [0.018, 0.048] | 0.030 | motor_can radius | 全样本 |
| motor_length | float | [0.050, 0.140] | 0.090 | motor_can length | 全样本 |
| linkage_drag_length | float | [0.10, 0.30] | 0.18 | drag_link length（仅 cranked） | rec_…_0002 / rec_…_2f6e |
| linkage_cross_length | float | [0.35, 0.90] | 0.55 | cross_link length（仅 dual_arm） | rec_…_2f6e |
| spindle_separation | float | [0.42, 0.94] | 0.58 | 双 spindle 间距（仅 dual_arm） | rec_…_2f6e |
| arm_length_scale | float | [0.92, 1.10] | 1.0 | 安全缩放 | resolve_config clamp |
| arm_chord_scale | float | [0.90, 1.15] | 1.0 | 安全缩放 | resolve_config clamp |
| blade_length_scale | float | [0.92, 1.10] | 1.0 | 安全缩放 | resolve_config clamp |
| linkage_clearance_scale | float | [0.95, 1.12] | 1.0 | linkage pivot clearance | resolve_config clamp |
| material_style | enum | factory_black / weathered_chrome / safety_orange_service / premium_satin / utility_yellow | sampled | 调色板 | 全样本 |

参数只表达语义选择、尺寸、行程、角度、multiplicity 数量、palette 与 module-local variant；未实现拓扑（rear-wiper 单 arm 但 motor + spindle 在车顶 vs cowl 安装 / 三 arm 巴士雨刮 / heated wiper / squirter / rain sensor）不进 enum。

## Multiplicity / Copy Logic

本类别含 architecture-derived multiplicity（不是显式 N 采样，而是 architecture 直接决定 arm_count）：

**(1) arm_count（由 architecture 派生）**
- count_param：`arm_count`（不暴露，derived from architecture）
- N_range：{1, 2}
- sampling domain：direct_drive_single_arm → 1；dual_arm_cowl_primary_cross_link → 2；dual_arm_tandem_cross_car → 2
- copied object：每 arm 一组 `(arm_i, blade_carrier_i, spindle_sweep_i, blade_roll_i)`；arm_0 / arm_1，blade_carrier_0 / blade_carrier_1
- naming：`arm_{i}` / `blade_carrier_{i}` / `spindle_sweep_{i}` / `blade_roll_{i}`（i ∈ {0} 或 {0,1}）
- placement：dual_arm 时两 spindle 沿 ±spindle_separation/2（驾驶侧 + 乘客侧）；arm_0 = 驾驶侧、arm_1 = 乘客侧
- joint policy：每 spindle 一个 REVOLUTE spindle_sweep_i（Z 轴）；每 arm tip 一个 REVOLUTE blade_roll_i（水平轴）
- source/gating：rec_…_06bc1be (N=1) / rec_…_2f6e (N=2) / rec_…_0003 (N=2) / rec_…_8c2d (N=2) / rec_…_76d79 (N=2)

**(2) linkage_part_count（由 architecture 派生）**
- direct_drive_single_arm：0 个 linkage part（无 motor_crank / drag_link / cross_link）
- dual_arm_cowl_primary_cross_link：3 个 linkage parts（drive_crank + primary_link + cross_link）+ motor_drive CONTINUOUS + 2 个 wiper_sweep REVOLUTE + 2 个 blade_roll REVOLUTE；primary/cross link 连接按来源为 captured/fixed support 语义
- dual_arm_tandem_cross_car：3 个 linkage parts（motor_crank + drag_link + cross_link）+ 4 个 linkage REVOLUTE（motor_drive + crank_to_drag + drag_to_spindle_0 + spindle_0_to_cross + cross_to_spindle_1）

**(3) blade_claw_count（module-local，固定，不暴露）**
- frame_with_multiple_pivots 内部固定 2 或 4 claws（end_left/end_right 或 inner/outer pairs）；module-local helper 循环，不暴露 template-level N

**(4) rubber_strip / spoiler / accessory**
- 每 blade carrier 含 1 rubber_strip；module-local 固定，不暴露
- beam_style_aero 含 1 spoiler；module-local 固定

## 拓扑多样性审计

总组合数（合法化前）：A(3) × B(4) × C(4) × D(3) = 144。compatibility matrix 裁剪后估算合法组合 ≈ 130（仅去掉极少数 soft mismatched 组合，例如 pedestal_motor + flat_strap_arm 视觉差但仍合法）。

每个 architecture 内部带来 distinct joint topology：
- direct_drive_single_arm: 2 joint (spindle_sweep + blade_roll)
- dual_arm_cowl_primary_cross_link: 5 moving joints (motor_drive + left/right wiper_sweep + left/right blade_roll) plus primary/cross link captured/fixed contacts
- dual_arm_tandem_cross_car: 8 joint (motor_drive + crank_to_drag + drag_to_spindle_0 + spindle_0_to_cross + cross_to_spindle_1 + 2 × spindle_sweep + 2 × blade_roll)

所以 A 维度本身就贡献 3 个 distinct topology family（part tree + joint count 完全不同）。

理由：A × B × C × D ≈ 144 enum 组合；A 维度本身保证 3 个 distinct part tree 家族；1000-seed 内能稳定看到 ≥40 distinct slot_choice tuple。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed deterministic procedural sampling —— rng 顺序选 architecture (A) → motor_housing (B) → arm_shape (C) → blade_carrier (D) → blade_roll_axis → 连续 scale + sweep/roll range → palette；arm_count 由 A 派生。`seed=0` 不特殊。所有非法组合由 compatibility matrix + `resolve_config` clamp 拦截。random sweep：seeds 0-49 初判，0-999 成熟审计；viewer 目检覆盖每个 A 家族（3）× B × D 至少 1 例。重点：

- spindle_sweep 轴竖直 Z
- blade_roll 轴水平（X 主，Y 少）
- dual_arm linkage 几何闭合（drag_link / cross_link 长度匹配 spindle_separation 与 crank 半径）
- arm tip yoke 抱住 blade carrier roll_barrel（captured-pin overlap 必须 element-scoped 声明）
- spindle hub 抱住 arm hub（captured pin）
- park-pose（rest pose）下 arm 不撞 motor_housing 或相邻 arm（dual_arm 时）
- blade 不漂浮：blade carrier 必须 child 于 arm
- arm 长度 + sweep 全 range 内不超 windshield 横向范围（合理性）

Topology target：1000-seed slot choice tuple distinct 建议 ≥40；本类别合法组合 ~130，预期可达。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
regression overrides：初版默认 none；若 sweep 暴露 dual_arm cross_car 4-bar 闭合失败的特定 spindle_separation × cross_link_length 组合，再以稀疏、显式 + 失败回归理由加入；不得用小型 curated/modulo 表当主 seed domain。
Controlled local parameterization：初版即纳入 `arm_length [0.18, 0.50]`、`arm_chord [0.014, 0.040]`、`arm_thickness [0.006, 0.016]`、`blade_length [0.20, 0.60]`、`blade_chord [0.015, 0.030]`、`spindle_radius`、`motor_radius`、`motor_length`、`spindle_separation [0.42, 0.94]` (dual_arm only)、`linkage_drag_length [0.10, 0.30]` (cranked only)、`linkage_cross_length [0.35, 0.90]` (dual_arm only)、`spindle_sweep_range`、`blade_roll_range`、`motor_drive_park_offset`，加各 scale。全部在 `resolve_config` clamp / 派生，受 motor housing → spindle 几何对齐、arm tip yoke 捕获 blade roll_barrel、dual_arm 4-bar 闭合性、park-pose envelope、joint origin 约束；不改变 architecture / motor_housing / arm_shape / blade_carrier / arm_count 等拓扑量。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | A→B→C→D 顺序选择 + 各步连续参数采样；A 决定 part count；weighted（direct_drive 高、dual_arm_tandem 中、dual_arm_cowl_primary_cross_link 低，反映样本分布 21:6:1，但权重提到 0.45:0.35:0.20 增加 cowl-link 曝光） | slot_choices_for_seed matches build choices |
| compatibility matrix | dual_arm_tandem_cross_car ⇒ arm_count=2 必须；linkage 长度由 spindle_separation 与 crank 半径派生；pedestal_motor / cast_box_motor 兼容所有 architecture；blade_roll_axis ∈ {X, Y} 与 arm tip yoke 方向一致 | no floating（arm/blade/linkage 不漂浮）、collision（park pose 下 dual_arm 相邻 arm 不互穿）、axis（sweep Z、blade_roll horizontal）、max multiplicity（arm_count ≤ 2）、closed pose（park 不撞 motor housing）、optional gating（cranked 时 linkage 必须 closed） |
| controlled local variation | arm_length / arm_chord / arm_thickness / blade_length / blade_chord / spindle_radius / motor_radius / motor_length / linkage 各长度 / sweep/roll range / motor_drive_park_offset / 各 scale，全 clamp | 比例变化不破坏 spindle 捕获、arm tip yoke 捕获 blade、linkage 4-bar 闭合、park pose envelope、joint origin、类别 identity |
| regression overrides | none（初版） | 仅失败回归或审核指定时显式加入 |
| random sweep | seeds 0-49 初判，0-999 成熟审计 | 与 contract failures（floating/overlap/captured-pin/axis/closed pose/linkage closure） |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A architecture | 3 | yes | yes | direct_drive / motor_crank / cross_car |
| B motor_housing | 4 | yes | yes | can / cast_box / turret / pedestal |
| C arm_shape | 4 | yes | yes | flat / tapered_extrude / tube_spine / lattice |
| D blade_carrier | 3 | yes | yes | flat_squeegee / multi_pivot_frame / aero_beam |

兼容矩阵（合法 / 互斥 / fallback）：

- `dual_arm_tandem_cross_car` ⇒ arm_count = 2（必须 ≥ spindle_separation 0.42m & ≤ 0.94m）；其他 architecture ⇒ arm_count = 1。
- `dual_arm_cowl_primary_cross_link` ⇒ 必须含 drive_crank + primary_link + cross_link parts；arm_count = 2；left/right wiper sweep 必须可见且 blade pitch 轴水平。
- `direct_drive_single_arm` ⇒ 无 linkage parts；arm_count = 1。
- `rectangular_turret_housing` × `lightened_lattice_arm`：视觉上 turret 平 + lattice 精细比例不太协调，但仍合法（soft warn only，不 gating）。
- `pedestal_motor` × `flat_strap_arm`：pedestal 高、flat_strap 矮显得过小，soft prefer `tube_spine_composite_arm` 或 `tapered_lever_arm_with_extrude`，但仍合法。
- `beam_style_aero` blade × `lightened_lattice_arm` arm：典型现代 aero wiper 组合，soft prefer。
- blade_roll_axis Y 仅在 module-local variant 启用（默认 X）；template 实现 X 主。
- linkage 4-bar 闭合：`linkage_drag_length` + `linkage_cross_length` 必须几何允许 `spindle_separation` 范围内闭合；`resolve_config` 派生而非自由采样。

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C/D 四元组 + arm_count + blade_roll_axis 派生 + material_style 可选）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal module combinations（dual_arm ↔ linkage parts 必须；cowl-link ↔ motor_drive + primary/cross link parts 必须；arm_count 由 A 派生）
- optional regression overrides are sparse and justified（初版 none）
- controlled local scale params (arm/blade/motor/linkage sizes, sweep/roll ranges, park offset, 各 scale) clamped；不破坏 spindle 捕获、arm tip yoke 捕获 blade、linkage 4-bar 闭合、park pose envelope、joint origin、类别 identity
- critical InterfaceSpec / MatingContract points exist：motor_housing top bearing seat ↔ spindle hub；spindle hub ↔ arm hub captured pin（element-scoped allow_overlap）；arm tip fork/yoke ↔ blade carrier roll_barrel captured pin；dual_arm linkage 各 pivot pin captured（motor_crank pin / drag_link pin / cross_link pin）
- key joints have expected type/axis/range：每个 `spindle_sweep_i` REVOLUTE axis=(0,0,1) range≈[-1.4, 1.4]；每个 `blade_roll_i` REVOLUTE axis 水平 range≈[-0.65, 0.65]；`motor_drive`（仅 cranked）CONTINUOUS or REVOLUTE axis=(0,0,1)；linkage 各 hinge REVOLUTE axis=(0,0,1)；origin 落各 pivot pin 中心
- arm/blade primitives：tube_spine_composite_arm 必须含 tube_from_spline_points 或 sweep_profile_along_spline；tapered_lever_arm_with_extrude 必须含 ExtrudeGeometry profile；lightened_lattice_arm 必须含 ExtrudeWithHolesGeometry；beam_style_aero blade 必须含 sweep_profile_along_spline 或 section_loft；不可降级
- arm_count multiplicity 一致：dual_arm 时必须有 arm_0/arm_1 + blade_carrier_0/blade_carrier_1 + spindle_sweep_0/spindle_sweep_1 + blade_roll_0/blade_roll_1 + cross_link & drag_link
- pivot origin 落 spindle / arm / linkage 实际几何，非空中（参 [[project_sweep_only_rest_pose]]）
- park pose（rest pose）下相邻 arm 不互穿、不撞 motor_housing

## Reject cases

- 缺少 spindle_sweep 或 blade_roll 任一关节（不构成 wiper）。
- spindle_sweep 轴非 Z 或 blade_roll 轴非水平（轴向错误）。
- dual_arm 但 linkage parts 缺失或 linkage 不闭合（4-bar 长度不匹配）。
- dual_arm_cowl_primary_cross_link 但缺 drive_crank/primary_link/cross_link parts，或 left/right sweep 未成对出现。
- arm 漂浮于 spindle（spindle hub 未捕获 arm hub）。
- blade 漂浮于 arm（arm tip yoke 未捕获 blade roll_barrel）。
- dual_arm 时 arm_0/arm_1 几何对称失败（左右镜像错）。
- park pose 下 arm 撞 motor housing 或相邻 arm 互穿（dual_arm）。
- arm 长 + sweep 全 range 超出合理范围（arm tip 在 windshield 外）。
- arm_shape 退化（tube_spine 不含 tube_from_spline_points / tapered 不含 ExtrudeGeometry / lattice 不含 ExtrudeWithHolesGeometry / aero blade 不含 sweep_profile / section_loft —— 违反 [[feedback_mesh_profile_origin_pitfall]] 与 Rule 3）。
- 只 rest pose 验 sweep / roll → 必须 pose 到 upper/lower 实测 AABB（[[project_sweep_only_rest_pose]]）。
- 隐藏机构（把 motor housing 完全藏起或 arm 完全在 housing 内部）违反 [[feedback_enclosed_mechanism_open_front]]。
- 把 module-local 件（claws / rubber_strip / spoiler）当成 slot 拓扑差异（[[feedback_multiplicity_includes_jointless]]）。
- 用尺寸/材质/颜色变化冒充 architecture / motor_housing / arm_shape / blade_carrier 候选差异。

## 与相邻类别的边界

- 不该混入：`box_fan_with_control_knob` / `ceiling_fan` / 旋翼机螺旋桨类 —— 那些是 **rotor + radial blade** 周向旋转；本类别是 **spindle + 单/双 arm linear-sweep**，运动语义不同。
- 不该混入：`articulated_task_lamp` / `cantilever_articulated_arm` / `serial_elbow_arm` —— 多关节臂用于位姿控制；本类别只有 sweep + roll 2-3 关节，arm 是单段或带 1 个 elbow。
- 不该混入：`vane_array_with_independent_pivots` / `louvered_shutter_assembly` —— 那是 N 片独立 / 联动 vane；本类别是单 / 双 spindle 驱动 1-2 arm。
- 不该混入：`paper_cutter_guillotine` / `barrier_gate_boom` —— 单 leaf 翻转门 / 道闸；motor 直驱无 sweep 平面运动。
- 不该混入：`monitor_mount` / `desktop_monitor_with_tilt_swivel_stand` —— 末端是 panel，不是 squeegee blade；无 motor 驱动。
- 不该混入：`gear_assemblies` —— 只有传动件，不是完整 wiper assembly。
- 不该混入：rear-window 单 arm 雨刮（cowl 顶置）—— 几何上同 direct_drive_single_arm 但 spindle 朝下，本 spec 默认 spindle 朝上的 cowl 安装；rear 变体作为 module-local viewer note 暂不进入主采样。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S-A1 | A | direct_drive_single_arm | rec_windshield_wiper_assembly_06bc1be7674340859b60b037db3bee78 | L217-L234 | motor 直驱 spindle + 2 joint (sweep + roll) |
| S-A2 | A | dual_arm_tandem_cross_car | rec_windshield_wiper_assembly_2f6e9a08fb3940d58acf2aa2e8ba9530 | L159-L396 | motor crank + drag_link + cross_link + 2 spindle + 2 arm 完整 4-bar |
| S-A3 | A | dual_arm_cowl_primary_cross_link | rec_windshield_wiper_assembly_0003 | L209-L650 | motor (CONTINUOUS) + drive_crank + primary_link + cross_link + left/right wiper modules |
| S-B1 | B | cylindrical_can_motor | rec_windshield_wiper_assembly_0001 | L45-L50 | Cylinder motor_can + flat_plate base |
| S-B2 | B | cast_box_motor_with_gearbox | rec_windshield_wiper_assembly_06bc1be7674340859b60b037db3bee78 | L38-L79 | Box gearbox_housing + Cylinder motor_can 集成 |
| S-B3 | B | rectangular_turret_housing | rec_windshield_wiper_assembly_2c145b57c5ed4b0c8d85be8eafda7707 | L15-L33 | 平 Box turret + bracket 到 spindle |
| S-B4 | B | pedestal_motor | rec_windshield_wiper_assembly_7f7c8dbfbedf45bfb12f58e840c84883 | L28-L63 | tall pedestal + 大 motor_can |
| S-C1 | C | flat_strap_arm | rec_windshield_wiper_assembly_0001 | L58-L91 | Box bar arm 最简 |
| S-C2 | C | tapered_lever_arm_with_extrude | rec_windshield_wiper_assembly_257ea157639f455e841b3a5b2e7d9bbf | L129-L165 | ExtrudeGeometry profile + tip_fork |
| S-C3 | C | tube_spine_composite_arm | rec_windshield_wiper_assembly_06bc1be7674340859b60b037db3bee78 | L82-L160 | Box shell + tube_from_spline_points + sweep_profile_along_spline |
| S-C4 | C | lightened_lattice_arm | rec_windshield_wiper_assembly_291e082ab0b34d1cb8d1d37d83a9fe5f | L157-L243 | ExtrudeWithHolesGeometry + LatheGeometry coil_spring |
| S-D1 | D | flat_squeegee_with_yoke | rec_windshield_wiper_assembly_2c145b57c5ed4b0c8d85be8eafda7707 | L55-L68 | Box + Cylinder + rubber Box 最简 |
| S-D2 | D | frame_with_multiple_pivots | rec_windshield_wiper_assembly_06bc1be7674340859b60b037db3bee78 | L162-L215 | bridge + harness + 2-4 claws + rubber_strip |
| S-D3 | D | beam_style_aero | rec_windshield_wiper_assembly_0003 | L488-L535 | section_loft / sweep_profile_along_spline + airfoil spoiler |

## 模板实现备注（可选）

- 共享 helper：`_motor_housing(style, r)` 4-branch primitive 分支；`_arm_shape(style, r)` 4-branch；`_blade_carrier(style, r)` 3-branch；`_linkage_4bar(r)` dual_arm 内置；`_arm_factory(i, shape, r)` 与 `_blade_factory(i, carrier, r)` 同形复用。
- 重点 InterfaceSpec / MatingContract：motor_housing top bearing seat ↔ spindle hub（轴向贴合 expect_gap≈0.0015）；spindle hub ↔ arm hub captured pin（element-scoped allow_overlap）；arm tip yoke ↔ blade carrier roll_barrel captured pin（element-scoped allow_overlap）；dual_arm linkage 各 pivot pin captured（motor_crank pin、drag_link pin、cross_link pin）。
- captured-pin overlap：spindle in motor bearing、arm hub on spindle、blade roll_barrel in arm tip yoke、linkage pin in linkage hole 处需 element-scoped `allow_overlap`，仅对真实意图穿插声明。
- 暂不进入 seed domain（待审核或后续启用）：rear-window 倒装单 arm 变体（rec 内无 5 星 rear 样本）；motor with embedded park-sensor；heated wiper element；squirter / washer fluid hose；3-arm bus wiper。
- dual_arm linkage 4-bar 闭合性：建议 resolve_config 根据 spindle_separation 与 crank_radius 派生 drag_link_length 与 cross_link_length，保证闭合（reference: rec_…_2f6e cross_link = spindle_separation × 0.77 ~ 0.80m for 1.55m cowl）。
- park pose（rest pose）：`motor_drive_park_offset` ∈ [-2.65, 2.65]（仅 cranked）；默认 0 以避免相邻 arm 互穿；resolve_config 根据 architecture clamp 到安全值。
- 单 arm 与 dual arm 的 spindle 位置：单 arm 时 spindle 在 motor housing 顶（origin x=0）；dual_arm 时 spindle_0 在 x=-spindle_separation/2、spindle_1 在 x=+spindle_separation/2，motor_crank 在 spindle_0 附近（驾驶侧）。
- blade_roll_axis 默认 X（垂直于 windshield 横向 = 沿 sweep arm 长方向）；若选 Y 则 blade 沿 windshield 上下翻转（罕见）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 全 28 个 5 星样本（rec_windshield_wiper_assembly_*）逐文件读取 model.py / revision.json / record.json / prompt / category metadata，分 3 批并行 Explore；candidate module 都锚定 `model.py:Lx-Ly`。结构家族：3 architecture × 4 motor_housing × 4 arm_shape × 3 blade_carrier，加 arm_count 派生 multiplicity 与 linkage_part_count 派生。等待人工审核。 |
