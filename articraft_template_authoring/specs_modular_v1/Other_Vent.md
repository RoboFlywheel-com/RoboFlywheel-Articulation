# vent (air vent / exhaust ventilation fan with grille + backdraft shutter) — Modular Spec

> 来源小类：`picture/Other/Vent`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Other__Vent.md`。
> **"Vent" 在此 = 通风口 / 换气扇 / 排风口（air vent / exhaust ventilation fan / register）：一只壳体（壁挂/穿墙/管道/法兰）+ 出风面格栅（grille，网/百叶/冲孔）+ 内置轴流风叶（impeller，CONTINUOUS 旋转）+ 可选防回流挡板（backdraft shutter，REVOLUTE 重力/百叶翻板）。** 不是软体格栅装饰，也不是独立 louvered shutter（无风叶）。
>
> **同步状态**：本 spec 引用 8 个 5 星样本（4 个 parent 母资产 + 4 个 fork 槽位变体），均已同步进本仓库 `data/records/`，rating=5，逐一核对确为 vent（壳体+风叶+格栅，且至少 1 非 fixed joint）。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一精读核对）。引用以 part / joint / helper **名字**为准（`duct_sleeve` / `housing` / `duct_shell` / `front_guard` / `impeller` / `fan_impeller` / `mesh_grille` / `louver_frame` / `perforated_plate` / `ring_grille` / `backdraft_flap` / `shutter_blade_{i}` / `flap_hinge` / `impeller_spin` / `fan_spin` 等），行号仅作定位。
>
> **来源缺口说明（重要，见 §阅读摘要 + §8）**：source map 还命名了 3 根 multiplicity 轴的 fork 变体（`impeller-blade-count-3/7`、`shutter-flap-count-4`、`guard-ring-count-4`），但**这 4 个 multiplicity fork 记录未同步进本仓库** `data/records/`（已 `ls` 全量确认不存在）。本 spec 仍保留这三根 multiplicity 轴，但**把每根轴锚定到 parent / 已同步 fork 的真实复制循环代码**（FanRotorGeometry 的 `blade_count` 形参；multi_blade_louver_shutter 的 `for i in range(LOUVER_COUNT)` 独立 REVOLUTE 循环；P3 的 `for i, ring_r in enumerate(GUARD_RING_RADII)` 同心环循环），不锚定缺失记录。这满足 §2.4 "candidate 必须有真实 model.py:Lx-Ly 来源" 的硬约束（复制逻辑源真实存在），但缺失的具体 N 值快照样本需 reviewer 注意。

## 元信息
| 项 | 值 |
|---|---|
| slug | `vent` |
| template path | `agent/templates/Other_Vent.py` |
| test path (optional) | `tests/agent/test_vent_template.py`（不写，sweep-pipeline 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: housing_form + grille_style + backdraft_shutter（主机构），**外加** `impeller_blade_count` / `shutter_flap_count` / `guard_ring_count` 三根多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（4 parent 母资产 + 4 fork 槽位变体；均 converged，compile success、workbench-only、≥1 非 fixed joint）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、复制循环与 run_tests）|
| read_scope | all synced 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 8/8 全部被采纳 |
| 来源缺口 | source map 命名的 3 根 multiplicity 轴 fork（impeller-blade-count-3/7、shutter-flap-count-4、guard-ring-count-4 = 4 记录）**未同步**；multiplicity 轴改锚定 parent / 已同步 fork 的真实复制循环（见顶部说明 + §8）。其余 8 个样本全部齐备且全读。|

阅读要点（用于槽位分解）：
- **身份不变量**：每个样本都是 `壳体 part`（root）+ `impeller part`（child，**CONTINUOUS** 绕壳体轴旋转，press-fit 在固定 motor_shaft / bushing 上）+ `格栅`（出风面，网/百叶/冲孔/同心环）。这是 vent 的不变身份：壳 + 旋转风叶 + 出风格栅。可选第四件 = backdraft shutter（防回流挡板，**REVOLUTE**）。
- **壳体轴（Slot A，housing_form，4 母资产已占满）**：P1 round_through_wall（`duct_sleeve` 短穿墙套筒 + torus `bezel_ring`，duct 轴 = 世界 +X）/ P2 square_wall（`housing` 方壳 + 圆开口 frame plate，轴 = +Z）/ P3 inline_duct_cylinder（`duct_shell` 长 lathe 管 + 环形 front_guard，轴 = +X）/ P4 round_flange（`housing` 圆法兰 + collar + drum + 8 bolt，轴 = +Y）。**四种壳体在 part 数、mesh helper、轴向约定上有结构差异**（套筒 vs 方壳 vs 长管 vs 法兰鼓），是真正的拓扑/接口轴。
- **格栅轴（Slot B，grille_style）**：woven_mesh（P1 `mesh_grille`，独立 FIXED part，`for k in range(-3,4)` 交叉杆 8×8 网）/ ring_spoke_grille（P2 `ring_grille`，inline housing visual，`for k in range(RING_COUNT)` 同心环 + 6 spoke）/ wire_guard_cage（P3 `front_guard`，独立 FIXED part，4 环 + 8 dished spoke + hub plate）/ louvered_front_grille（louvered fork，inline 角度百叶 `for i in range(LOUVER_COUNT)` 固定斜板）/ perforated_plate（perforated fork，独立 FIXED part，冲孔 disc）。格栅是出风面 mesh/part 形态变化（part 数 0 或 1 + visual 复杂度），多数是非移动 FIXED 件。
- **backdraft_shutter 轴（Slot C，主机构槽）**：none（P1/P2/P3 无挡板，仅风叶 CONTINUOUS）/ spring_flap_pair（P4 `backdraft_flap` 单 REVOLUTE 圆盘挡板，top hinge captured-pin，axis -X）/ single_gravity_flap（gravity_flap fork `backdraft_flap` 单 REVOLUTE 圆盘，knuckle 绕 hinge_pin，axis +Y）/ multi_blade_louver_shutter（louver_shutter fork，**N 个独立 `shutter_blade_{i}` REVOLUTE** 百叶，axis +X，各独立 hinge `shutter_blade_{i}_hinge`）。这是真正的 joint 拓扑变化（0 / 1 REVOLUTE / N REVOLUTE）。
- **multiplicity 轴（三根，见 §8）**：`impeller_blade_count`（FanRotorGeometry/`_rotor_solid` 的 blade 数；P1=4 / P2=8 / P3=7 / P4=8，跨样本已变；随 impeller CONTINUOUS，无独立 joint）；`shutter_flap_count`（multi_blade_louver_shutter 的 `for i in range(LOUVER_COUNT)` 独立 REVOLUTE 百叶数，源 LOUVER_COUNT=5）；`guard_ring_count`（P3 `GUARD_RING_RADII` 同心环数 + P2 ring_grille 同心环数，随壳固定无关节）。

## 核心身份

一只**通风口 / 换气扇 / 排风口**（air vent / exhaust ventilation fan）：一只固定**壳体**（穿墙圆套筒 / 壁挂方壳 / 直列圆管 / 圆法兰鼓）支撑一只**轴流风叶 impeller**（`FanRotorGeometry` 或 polyline 叶片 pinwheel），impeller 绕壳体中心轴（duct axis）做 **CONTINUOUS 旋转**，hub bore press-fit 在壳体上固定的 motor_shaft / bushing / boss 上（captured shaft，非悬空）；壳体出风面有一层**格栅**（square wire mesh / 同心环+spoke / wire guard cage / 角度百叶 / 冲孔板），格栅多为非移动 FIXED 件，遮护风叶并定义出风面外观。可选**防回流挡板 backdraft shutter**（单重力圆盘翻板 / 单弹簧翻板 / N 叶独立百叶），通过壳体后/边缘的 hinge 硬件以 **REVOLUTE** 铰接，重力闭合（q=0）、气流推开（q>0），captured knuckle/pin 关系。

活动语义 = **风叶 CONTINUOUS 旋转（恒存在）** + 可选 **backdraft shutter REVOLUTE 翻开**（0 / 1 / N 个 REVOLUTE）。默认成熟域：housing_form × grille_style × backdraft_shutter × impeller 叶数 × shutter 翻板数 × guard 环数 的小型壁挂/管道通风口。

不该混入：
- **`vane_array_with_independent_pivots` / `louvered_shutter_assembly`（纯百叶阵列，无风叶）**——那是固定外框 + N 片独立/联动 vane，**没有旋转风叶 impeller**；vent 的不变身份必含旋转风叶。本类的 backdraft shutter 只是可选附件，主体是壳+风叶+格栅。
- **`ceiling_fan` / `box_fan_with_control_knob` / `desk_fan`（独立风扇）**——那是裸露大风扇（rotor 是主体，无穿墙/管道壳体出风格栅遮护、无 backdraft）；vent 的风叶藏在壳体内、被格栅遮护，是"建筑通风口"而非"桌面风扇"。
- **`range_hood` / `extractor_hood`（抽油烟机）**——大型橱柜式带控制面板，非小型通风口。
- **静态 `vent_grille` / `perforated_panel`（无风叶纯格栅）**——无 articulation；vent 必须有旋转风叶（≥1 CONTINUOUS）。

## 槽位 + 候选模块表

> **建模注记**：`housing_form`（Slot A）决定壳体 part 数、mesh helper、duct 轴向约定（+X/+Z/+Y）与所有下游接口点位（motor_shaft / bushing 位置、格栅安装面、backdraft hinge 硬件挂点），是真正的接口轴。`grille_style`（Slot B）是出风面格栅 part/visual 形态（多为 FIXED 非移动件，仅 part 数 0/1 与 mesh 复杂度变化）。`backdraft_shutter`（Slot C）是真正改 joint 拓扑的主机构轴（0 / 1 REVOLUTE / N REVOLUTE）。模板内部统一壳体轴向约定（推荐世界 +X = duct axis，参 P1/P3），各 housing helper 在内部完成 mesh 旋转使局部 +Z → 世界 duct axis。

### Slot A：housing_form（壳体形态 —— 决定 part 树 / 接口点位 / 轴向，4 母资产已占满）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_through_wall（基线 P1）| rec_model-a-small-round-through-wall-exhaust-vent-ab_…f4fe4250 | `_tube` L76-78 / `duct_sleeve` 装配 L92-118（含 motor strut/pod/shaft）/ torus `bezel_ring` L121-142 | eligible if compatible | 短穿墙圆套筒 `duct_sleeve`（root；hollow tube + motor_strut + motor_pod + 固定 motor_shaft）+ FIXED `bezel_ring`（torus 前缘 donut）；duct 轴 = 世界 +X；motor_shaft 在套筒内供 impeller press-fit |
| square_wall（基线 P2）| rec_model-a-square-wall-mounted-exhaust-ventilation-_…4c3504f2 | `_build_housing_shell` L80-105 / `_build_border_rim` L108-119 / `housing` 装配 L174-206（boss/shaft）| eligible if compatible | 壁挂方壳 `housing`（root；hollow rear box + 前 frame plate 含圆开口 + border_rim + motor_boss + 固定 motor_shaft）；duct 轴 = 世界 +Z（法向墙面）；方足迹 0.30×0.30 |
| inline_duct_cylinder（基线 P3）| rec_model-an-industrial-inline-duct-fan-a-hollow-ope_…4010e666 | `duct_shell` lathe L87-116 / `motor_mount`（motor_body+struts+shaft）L184-216 | eligible if compatible | 直列长圆管 `duct_shell`（root；LatheGeometry rolled-rim 管，卧地 z=0）+ FIXED `motor_mount`（独立 part：motor_body + 3 radial strut 焊入管壁 + 前 shaft 托 impeller）；duct 轴 = 世界 +X；两端开口 |
| round_flange（基线 P4）| rec_model-a-round-flange-mounted-wall-vent-fan-about_…6e21aa96 | `_tube` L85-86 / housing flange+collar+drum L127-145 / `_rotor_solid` impeller helper / motor_bushing+struts L167-185 / hinge 硬件 L189-201 | eligible if compatible | 圆法兰鼓 `housing`（root；flange_plate + collar_ring + drum_shell + 8 hex bolt + motor_bushing + 4 strut + 后置 hinge_bracket/hinge_pin）；duct 轴 = 世界 +Y；impeller shaft press-fit 在 motor_bushing 内；唯一自带 backdraft hinge 硬件的母资产 |

### Slot B：grille_style（出风面格栅 —— 多为 FIXED 非移动件，part 数 0/1 + mesh 形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键结构特征 |
|---|---|---|---|---|
| woven_square_mesh（基线 P1）| rec_model-…f4fe4250 | `mesh_grille` part L145-172（`for k in range(-3,4)` 交叉杆）+ FIXED `sleeve_to_grille` L173-179 | eligible if compatible | 独立 FIXED `mesh_grille` part：grille_rim 环 + 7 水平 + 7 垂直交叉 Box 杆 → ~8×8 方格网；recessed 在前缘内 |
| ring_spoke_grille（基线 P2）| rec_model-…4c3504f2 | `_build_ring_grille` L122-145（`for k in range(RING_COUNT)` 同心环 + `for i in range(SPOKE_COUNT)` spoke）| eligible if compatible | inline housing visual `ring_grille`：center cap disc + N 同心环 + 6 radial spoke，融合为一 solid，平贴开口面（与 guard_ring_count 联动）|
| wire_guard_cage（基线 P3）| rec_model-…4010e666 | `front_guard` part L124-166（`for i,ring_r in enumerate(GUARD_RING_RADII)` 4 环 + `for k in range(GUARD_SPOKE_COUNT)` 8 dished spoke + hub plate）+ FIXED `shell_to_guard` L168-177 | eligible if compatible | 独立 FIXED `front_guard` part：4 同心 torus 环 + 8 wire spoke 浅锥碟 + 中心 hub plate；工业 target/spider 罩（与 guard_ring_count 联动）|
| louvered_front_grille | rec_variant-grille-style-louvered-front-grille-repla_…2901e840 | `_louver_slat` L84-86 / louver_frame + `for i in range(LOUVER_COUNT)` 角度斜板 inline L152-177 | eligible if compatible | inline duct_sleeve visual：louver_frame 环 + N 片 `louver_{i}` 角度斜板（tilt 35°，**固定非移动**，sqrt 半span 适配圆口）；角度百叶面 |
| perforated_plate | rec_variant-grille-style-perforated-plate-replace-th_…67dfdf18 | `_perforated_disc` L85-117（pushPoints 圆孔阵）/ `perforated_plate` part L184-… + FIXED 接入 | eligible if compatible | 独立 FIXED `perforated_plate` part：plate_rim 环 + 冲孔 disc（cadquery 圆孔正方栅格 cut）；冲孔面板 |

### Slot C：backdraft_shutter（防回流挡板 —— **主机构槽**，决定 joint 拓扑：0 / 1 / N REVOLUTE）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| none（基线 P1/P2/P3）| rec_model-…f4fe4250 / …4c3504f2 / …4010e666（3 母资产无挡板）| 无 backdraft part（仅 impeller CONTINUOUS）| eligible if compatible | 无挡板：壳 + 风叶 CONTINUOUS + 格栅；最简（空机构）。多数穿墙/管道 vent 无防回流 |
| single_gravity_flap | rec_variant-backdraft-single-gravity-flap-add-a-sing_…bf2f8952 | hinge lugs+pin L141-160 / `backdraft_flap` disc+knuckle L253-272 / `flap_hinge` REVOLUTE axis +Y L275-285 | eligible if compatible | **单重力翻板** `backdraft_flap`（圆盘 `flap_disc` + `flap_knuckle` 绕 hinge_pin）child，**1×REVOLUTE** `flap_hinge` axis=(0,1,0)，origin 在套筒后缘 top（lower=0 重力闭合 / upper≈1.35 气流推开外翻）；壳体加 hinge_lug_{0,1}+hinge_pin captured |
| single_disc_flap_topring | rec_model-a-round-flange-mounted-wall-vent-fan-about_…6e21aa96（P4 自带）| hinge_bracket L189-195 / hinge_pin L196-201 / `backdraft_flap` disc+2 knuckle+tab L229-254 / `flap_hinge` REVOLUTE axis -X L256-266 | eligible if compatible | **单顶铰圆盘翻板** `backdraft_flap`（`flap_disc` + 2 `flap_knuckle_{i}` + 2 `flap_tab_{i}`）child，**1×REVOLUTE** `flap_hinge` axis=(-1,0,0)，origin 在 drum 内顶铰线（lower=0 闭合贴 drum 后 / upper≈1.40 后翻出 drum）；壳体加 hinge_bracket_{i}+hinge_pin captured-pin（2 knuckle 绕 pin）|
| multi_blade_louver_shutter | rec_variant-backdraft-multi-blade-louver-shutter-add_…d3db9306 | `_build_louver_frame` L183-214 / `_build_louver_blade` L217-223 / `for i in range(LOUVER_COUNT)` `shutter_blade_{i}` + `shutter_blade_{i}_hinge` REVOLUTE axis +X L303-332 | eligible if compatible | **N 叶独立百叶** child×N：每片 `shutter_blade_{i}` 平板 + 独立 **REVOLUTE** `shutter_blade_{i}_hinge` axis=(1,0,0)，origin 沿 frame 高度等距 pivot_y（lower=0 垂挂闭合 / upper≈1.22 同向翻开）；壳体 inline louver_frame + N-1 pivot rail；**与 shutter_flap_count 多重性轴联动**（N 个独立 REVOLUTE）|

> Slot C 候选差异是真实 joint 拓扑：none（0 REVOLUTE）/ single_gravity_flap 与 single_disc_flap_topring（各 1 REVOLUTE，但 axis（+Y vs -X）、hinge 硬件（lug+pin vs bracket+pin）、闭合姿态来源不同 → 结构不同 candidate）/ multi_blade_louver_shutter（N 个独立 REVOLUTE）。

## 槽位图（slot graph）

pattern: mixed（固定 named slots: housing_form + grille_style + backdraft_shutter 各自挂到共同 `壳体`（parallel children），外加 `impeller_blade_count` / `shutter_flap_count` / `guard_ring_count` 三根多重性轴在壳体 / impeller / shutter 上做 N 次复制）

```
壳体 housing/duct_sleeve/duct_shell (root; 由 housing_form 决定 part 树 + duct 轴 + motor_shaft/bushing + 格栅安装面 + backdraft hinge 挂点)
  │
  ├── impeller (恒存在 child) ──[impeller_spin/fan_spin: CONTINUOUS, axis=duct axis, origin=hub 中线]
  │        └ hub bore press-fit 在壳体固定 motor_shaft / bushing 上 (captured shaft, allow_overlap)
  │        └ [impeller_blade_count 多重性轴] FanRotorGeometry(blade_count=K) 或 _rotor_solid `for k in range(K)` 等角叶片
  │
  ├── [grille_style slot] (五选一; 出风面格栅)
  │     ├─ woven_square_mesh    : 独立 FIXED part `mesh_grille` ──[FIXED, origin=出风面]
  │     ├─ ring_spoke_grille    : inline housing visual `ring_grille` (无独立 part/joint)
  │     │                          └ [guard_ring_count 多重性轴] `for k in range(R)` 同心环
  │     ├─ wire_guard_cage      : 独立 FIXED part `front_guard` ──[FIXED, origin=前缘]
  │     │                          └ [guard_ring_count 多重性轴] `for i in range(R)` torus 环
  │     ├─ louvered_front_grille: inline 壳体 visual `louver_{i}` 角度斜板 (固定, 无独立 joint)
  │     └─ perforated_plate     : 独立 FIXED part `perforated_plate` ──[FIXED, origin=出风面]
  │
  └── [backdraft_shutter slot] (四选一; 主机构)
        ├─ none                      : (无挡板, 空机构)
        ├─ single_gravity_flap       : `backdraft_flap` ──[flap_hinge: REVOLUTE axis=+Y, origin=套筒后缘 top]
        ├─ single_disc_flap_topring  : `backdraft_flap` ──[flap_hinge: REVOLUTE axis=-X, origin=drum 内顶铰线]
        └─ multi_blade_louver_shutter: shutter_blade_{i} ──[shutter_blade_{i}_hinge: REVOLUTE axis=+X, origin=pivot_y_i] × N
              └ [shutter_flap_count 多重性轴] `for i in range(N)` 独立 REVOLUTE 百叶
```

接口点位与 joint 语义：
- **impeller 接口（恒存在）**：impeller hub bore press-fit 在壳体固定 motor_shaft（P1/P2）/ motor_bushing（P4）/ motor_mount shaft（P3）上；**CONTINUOUS** `impeller_spin`/`fan_spin`，axis = duct axis（P1/P3 +X、P2 +Z、P4 +Y），origin = hub 中线；motion_limits 无 lower/upper（连续旋转）。captured shaft 用 element-scoped `allow_overlap`（`fan_rotor/impeller_rotor` ↔ `motor_shaft/motor_bushing`，照搬各样本 run_tests）。
- **grille 接口（五选一）**：woven_square_mesh / wire_guard_cage / perforated_plate 为独立 FIXED child（origin 在出风面/前缘，rim press-fit 进壳口 → allow_overlap rim↔壳壁）；ring_spoke_grille / louvered_front_grille 为壳体 inline visual（无独立 joint，非移动）。所有格栅 recessed 在前缘/开口内，遮护风叶。
- **backdraft 接口（四选一，互斥）**：
  - none：无 joint。
  - single_gravity_flap：壳体后缘 top `hinge_lug_{i}` + `hinge_pin`（duct_sleeve）↔ flap `flap_knuckle` captured-pin；REVOLUTE axis=(0,1,0)，origin=(SLEEVE_BACK_X, 0, FLAP_HINGE_Z)；q=0 重力垂闭贴后缘 / q>0 外翻。
  - single_disc_flap_topring：drum 内顶 `hinge_bracket_{i}` + `hinge_pin`（housing）↔ flap `flap_knuckle_{i}`×2 captured-pin；REVOLUTE axis=(-1,0,0)，origin=(0,HINGE_Y,HINGE_Z)；q=0 闭合贴 drum 后 / q>0 后翻出 drum。
  - multi_blade_louver_shutter：壳体 inline louver_frame + N-1 pivot rail；每片 `shutter_blade_{i}` 独立 REVOLUTE `shutter_blade_{i}_hinge` axis=(1,0,0)，origin 沿 frame 高度等距 pivot_y_i（`LOUVER_OPENING_SIDE/2 − i·slot_h`）；q=0 全部垂闭 / q>0 同向翻开。
- **mating policy**：所有 hinge 是 pin-in-knuckle / pin-in-barrel captured-pin（销在 knuckle/barrel 内），impeller 是 shaft-in-bore captured-shaft，格栅 rim 是 ring-in-mouth press-fit —— 几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured/press-fit overlap（见各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：impeller q=0（任意，连续）；所有 backdraft flap/blade q=0 重力闭合（lower=0）。
- **互斥 / 可选 / 派生**：grille_style 五候选互斥；backdraft_shutter 四候选互斥（含 none 空机构）；impeller 恒存在。housing_form 决定哪些 grille / backdraft 兼容（见 §9 兼容矩阵：方壳 P2 配 louver_shutter 自然、圆套筒 P1 配 gravity_flap、法兰鼓 P4 配 disc_flap_topring）。

## 每槽位 Module Emits / Interfaces

### Slot A / housing_form — round_through_wall（P1，以此为壳体基线范式）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `duct_sleeve`（root；visual: `sleeve_tube` hollow tube + `motor_strut` + `motor_pod` + 固定 `motor_shaft`）+ FIXED `bezel_ring`（torus 前缘）| P1 `_tube` L76-78 / 装配 L92-142 |
| internal joints | `sleeve_to_bezel` FIXED（前缘 donut）| P1 L136-142 |
| upstream interface | root（无父）| — |
| downstream interface | `motor_shaft`（impeller press-fit 挂点）+ 套筒前缘 rim（grille 安装面）+ 后缘 top（backdraft hinge 挂点）| P1 L113-118 |

### Slot A / housing_form — square_wall（P2）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `housing`（root；visual: `housing_shell` 方壳+圆开口 + `border_rim` + `motor_boss` + 固定 `motor_shaft`）| P2 `_build_housing_shell` L80-105 / 装配 L174-201 |
| internal joints | 无（grille 多为 inline）| — |
| downstream interface | `motor_shaft`（impeller press-fit）+ 圆开口面（grille / louver_frame 安装）+ 后壁（louver_shutter pivot rail）| P2 L196-201 |

### Slot A / housing_form — inline_duct_cylinder（P3）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `duct_shell`（root；LatheGeometry rolled-rim 管，卧地）+ FIXED `motor_mount`（独立 part：`motor_body` + 3 `motor_strut_{k}` 焊入管壁 + `motor_shaft`）| P3 L87-116 / L184-216 |
| internal joints | `shell_to_motor_mount` FIXED / `shell_to_guard` FIXED | P3 L218-227 / L168-177 |
| downstream interface | motor_mount `motor_shaft`（impeller press-fit）+ 前 rim（guard 安装）| P3 L209-216 |

### Slot A / housing_form — round_flange（P4）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `housing`（root；`flange_plate` + `collar_ring` + `drum_shell` + 8 `flange_bolt_{i}` + `motor_bushing` + 4 `motor_strut_{i}` + 后置 `hinge_bracket_{i}` + `hinge_pin`）| P4 L127-201 |
| internal joints | 无（impeller/flap 是 child）| — |
| downstream interface | `motor_bushing`（impeller shaft press-fit）+ collar 开口（grille 面）+ drum 内顶 hinge_bracket/hinge_pin（backdraft 挂点）| P4 L167-201 |

### impeller（恒存在 child；以 P1 为例）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `fan_impeller`/`impeller`（`fan_rotor`/`impeller_rotor` = FanRotorGeometry 或 `_rotor_solid` 叶片 hub）| P1 L182-200 / P2 L213-218 / P3 L235-261 / P4 L204-216 |
| internal joints | `fan_spin`/`impeller_spin` CONTINUOUS，axis=duct axis，origin=hub 中线，无 lower/upper | P1 L201-209 / P2 L224-232 / P3 L263-271 / P4 L218-226 |
| upstream interface | hub bore press-fit 在壳体固定 motor_shaft/bushing（captured shaft，allow_overlap）| P1 L238-244 / P4 L281-287 |

### Slot B / grille_style — woven_square_mesh（P1）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 独立 FIXED `mesh_grille`（`grille_rim` + 7 `grille_bar_h_{i}` + 7 `grille_bar_v_{i}`）| P1 L145-172 |
| internal joints | `sleeve_to_grille` FIXED（出风面）| P1 L173-179 |
| upstream interface | grille_rim press-fit 进壳口（allow_overlap rim↔sleeve_tube）| P1 L231-237 |

### Slot B / grille_style — ring_spoke_grille（P2，含 guard_ring_count）
| emits | 描述 | 来源 |
|---|---|---|
| parts | inline housing visual `ring_grille`（cap + R 同心环 + 6 spoke，融合一 solid）| P2 `_build_ring_grille` L122-145 |
| internal joints | 无（inline visual）| — |
| guard_ring 复制 | `for k in range(RING_COUNT)` 同心环（R 与 guard_ring_count 联动）| P2 L125-133 |

### Slot B / grille_style — wire_guard_cage（P3，含 guard_ring_count）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 独立 FIXED `front_guard`（R `guard_ring_{i}` torus + 8 `guard_spokes` dished + `guard_hub_plate`）| P3 L124-166 |
| internal joints | `shell_to_guard` FIXED（前缘）| P3 L168-177 |
| guard_ring 复制 | `for i, ring_r in enumerate(GUARD_RING_RADII)` torus 环（R 与 guard_ring_count 联动）| P3 L126-138 |

### Slot B / grille_style — louvered_front_grille（fork）
| emits | 描述 | 来源 |
|---|---|---|
| parts | inline 壳体 visual `louver_frame` + N 片 `louver_{i}` 角度斜板（**固定非移动**）| louvered fork `_louver_slat` L84-86 / L152-177 |
| internal joints | 无（角度百叶固定，非 backdraft）| — |

### Slot B / grille_style — perforated_plate（fork）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 独立 FIXED `perforated_plate`（`plate_rim` + 冲孔 disc）| perforated fork `_perforated_disc` L85-117 / L184+ |
| internal joints | FIXED（出风面）| perforated fork |
| upstream interface | plate_rim press-fit 进壳口（allow_overlap）| perforated fork run_tests |

### Slot C / backdraft_shutter — single_gravity_flap（fork）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `backdraft_flap`（`flap_disc` + `flap_knuckle`）；壳体加 `hinge_lug_{i}`×2 + `hinge_pin` | gravity_flap fork L141-160 / L253-272 |
| internal joints | `flap_hinge` REVOLUTE axis=(0,1,0)，origin=(SLEEVE_BACK_X,0,FLAP_HINGE_Z)，lower=0 / upper≈1.35 | gravity_flap fork L275-285 |
| upstream interface | `flap_knuckle` 绕壳体 `hinge_pin` captured-pin（allow_overlap）| gravity_flap fork L332-338 |

### Slot C / backdraft_shutter — single_disc_flap_topring（P4 自带）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `backdraft_flap`（`flap_disc` + 2 `flap_knuckle_{i}` + 2 `flap_tab_{i}`）；壳体加 `hinge_bracket_{i}`×2 + `hinge_pin` | P4 L189-201 / L229-254 |
| internal joints | `flap_hinge` REVOLUTE axis=(-1,0,0)，origin=(0,HINGE_Y,HINGE_Z)，lower=0 / upper≈1.40 | P4 L256-266 |
| upstream interface | `flap_knuckle_{i}`×2 绕 `hinge_pin` captured-pin（allow_overlap）| P4 L288-295 |

### Slot C / backdraft_shutter — multi_blade_louver_shutter（fork；含 shutter_flap_count）
| emits | 描述 | 来源 |
|---|---|---|
| parts | N 片 `shutter_blade_{i}`（平板）；壳体 inline `louver_frame` + N-1 pivot rail | louver_shutter fork `_build_louver_frame` L183-214 / `_build_louver_blade` L217-223 / L303-311 |
| internal joints | N 个 `shutter_blade_{i}_hinge` REVOLUTE axis=(1,0,0)，origin=pivot_y_i，lower=0 / upper≈1.22（各独立）| louver_shutter fork L318-332 |
| placement | `for i in range(LOUVER_COUNT)` pivot_y = `LOUVER_OPENING_SIDE/2 − i·LOUVER_BLADE_SLOT_H`（等距）| louver_shutter fork L303-321 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| housing_form | enum | round_through_wall / square_wall / inline_duct_cylinder / round_flange | round_through_wall | choice | 由 deterministic procedural sampler 选；决定 part 树 + duct 轴 + 接口点位 | module table |
| grille_style | enum | woven_square_mesh / ring_spoke_grille / wire_guard_cage / louvered_front_grille / perforated_plate | woven_square_mesh | choice | sampler 选（受 housing_form gating）| module table |
| backdraft_shutter | enum | none / single_gravity_flap / single_disc_flap_topring / multi_blade_louver_shutter | none | choice | sampler 选；主机构（互斥，含空机构 none）| module table |
| impeller_blade_count (Kb) | int | 声明域 [3,9]；sweep 采样域 {3,5,7,8}（偏中加权）| 7 | conditional→slot_choice | 编入 slot_choice 为 `kb{Kb}`（FanRotor 叶数）；随 impeller CONTINUOUS，无独立 joint | P1=4/P2=8/P3=7/P4=8 |
| shutter_flap_count (Nf) | int | 声明域 [2,6]；sweep 采样域 [2,6]（偏小：2/3 高频、5/6 长尾）| 5 | conditional→slot_choice | **仅 backdraft_shutter=multi_blade_louver_shutter 有效**；编入 slot_choice `nf{Nf}`；N 个独立 REVOLUTE | louver_shutter fork LOUVER_COUNT=5 |
| guard_ring_count (Rg) | int | 声明域 [2,6]；sweep 采样域 [2,6]（偏中）| 4 | conditional→slot_choice | **仅 grille_style∈{ring_spoke_grille, wire_guard_cage} 有效**；编入 slot_choice `rg{Rg}`；同心环数，随壳固定无关节 | P3 GUARD_RING_RADII(4) / P2 RING_COUNT(13) |
| palette_style | enum | cream_plastic / white_grey_plastic / brushed_steel_industrial / pale_grey_painted / matte_black_register / warm_anodized_bronze | cream_plastic | palette | palette only，**不计入 slot_choice**（≥3，目标 4-6；本表 6 个）| 各样本材质 |
| housing_dia_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放壳体主直径/边长（bore/opening 同步），clamp | resolve clamp |
| housing_depth_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放壳体轴向深（duct length / drum depth），clamp | resolve clamp |
| impeller_dia_scale | float | derived | — | equation | `= housing_dia_scale`（叶尖随 bore 等比缩，保持 bore clearance）| 接口 |
| grille_recess_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放格栅 recess 深度（保格栅在前缘内），clamp | resolve clamp |
| flap_open_angle_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 backdraft_shutter≠none 有效；缩放 REVOLUTE flap/blade `upper`，clamp（保 ≤π·0.92）| resolve clamp |
| louver_pitch_scale | float | [0.90, 1.10] | 1.0 | conditional | 仅 multi_blade_louver_shutter 有效；缩放百叶等距 pitch | resolve clamp |
| guard_ring_pitch_scale | float | [0.90, 1.10] | 1.0 | conditional | 仅 ring_spoke_grille/wire_guard_cage 有效；缩放同心环 pitch | resolve clamp |
| (—) | constraint | — | — | inequality | impeller 叶尖不超 bore：`impeller_outer_R·impeller_dia_scale ≤ bore_inner_R − clearance`（违反按比例缩 impeller_outer 或拒采）| 接口 / clearance |
| (—) | constraint | — | — | inequality | 百叶排布不超 frame：`Nf·blade_slot_h ≤ frame_opening − 2·border`（违反缩 slot_h 或 clamp Nf）| 接口 / clearance |
| (—) | constraint | — | — | inequality | 同心环不超开口：`RING_R0 + (Rg−1)·ring_pitch·guard_ring_pitch_scale + ring_w/2 ≤ opening_R − margin`（违反缩 ring_pitch 或 clamp Rg）| 接口 / clearance |
| (—) | constraint | — | — | inequality | backdraft flap/blade 全开 range 内不撞壳壁/格栅（闭合 q=0 覆盖出风口，全开 q=upper 翻出 envelope）| 接口 / closed pose |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度 / pitch，**绝不改变 housing_form / grille_style / backdraft_shutter / Kb / Nf / Rg 的拓扑**。

## Multiplicity / Copy Logic

**3 根 multiplicity 轴**（各自独立加权采样、各自编进 slot_choice、各自 clamp、sweep 各自设上限）：

### 轴 1：`impeller_blade_count`（风叶数 Kb；恒存在轴）
- **count_param**：`impeller_blade_count`（FanRotorGeometry 的 `blade_count` 形参 / `_rotor_solid` 的 `for k in range(BLADE_COUNT)`）。
- **N_range**：声明产品域 **[3, 9]**（小型轴流风叶现实叶数 3-9；跨样本已见 4/7/8）。sweep 采样域 **{3,5,7,8}**（偏中加权：奇数风叶 5/7 常见、4/8 broad 叶常见、3 稀疏）。
- **sampling domain**：`config_from_seed` 用 `rng.choices((3,5,7,8), weights=偏中)`；`resolve_config` clamp 到 [3,9]。
- **copied object**：单片风叶（FanRotorGeometry 内部等角复制 K 片 broad/scimitar 叶 + hub；或 `_rotor_solid` 的 polyline 梯形叶 `for k in range(K)`）。N 片叶复用同一叶 profile。
- **naming**：FanRotorGeometry 内部叶片无独立 part 名（整 rotor = `fan_rotor`/`impeller_rotor` 单 mesh）；`_rotor_solid` 风格 union 叶到单 rotor。
- **placement**：等角 `k·360°/K`（FanRotorGeometry 内部 / `_rotor_solid` L113-114 `blade.rotate(...k·360/BLADE_COUNT)`）。
- **joint policy**：风叶是**非移动复制件 within impeller**（Rule 1）→ 整 rotor 是单 CONTINUOUS child，**不发射 per-blade 独立 joint**；唯一活动关节是 impeller_spin CONTINUOUS。
- **source/gating**：源取各 parent 的 blade_count（P1=4 L189 / P2=8 L74 / P3=7 L238 / P4=8 L57 + `_rotor_solid` L113-114）；与所有 housing/grille/backdraft 兼容。

### 轴 2：`shutter_flap_count`（百叶翻板数 Nf）
- **count_param**：`shutter_flap_count`（multi_blade_louver_shutter 的 `LOUVER_COUNT`）。
- **N_range**：声明产品域 **[2, 6]**。sweep 采样域 **[2, 6]**（偏小：2/3 高频、5/6 长尾）。
- **sampling domain**：`config_from_seed` 用 `rng.choices((2,3,4,5,6), weights=偏小)`；`resolve_config` clamp 到 [2,6]。
- **copied object**：单片百叶 `shutter_blade_{i}`（`_build_louver_blade` 平板）+ 其独立 `shutter_blade_{i}_hinge` REVOLUTE。
- **naming**：`shutter_blade_{i}` / joint `shutter_blade_{i}_hinge`，`for i in range(Nf)`（louver_shutter fork L303-332 已用此结构，直接作 copy-logic 源）。
- **placement**：沿 frame 高度 **绝对式**等距——`pivot_y = LOUVER_OPENING_SIDE/2 − i·LOUVER_BLADE_SLOT_H`（每 i 的 y 由 Nf 与 frame 解析，不累加漂移）。
- **joint policy**：每片百叶**独立 REVOLUTE**（axis +X，lower=0 / upper≈1.22）；N 个独立 hinge（非联动）。
- **source/gating**：源 louver_shutter fork L303-332（LOUVER_COUNT=5）；**仅当 backdraft_shutter=multi_blade_louver_shutter 时此轴活跃**（其余 backdraft 候选 Nf 不适用，slot_choice 不编 nf）。

### 轴 3：`guard_ring_count`（同心环数 Rg）
- **count_param**：`guard_ring_count`（P3 `GUARD_RING_RADII` 长度 / P2 `RING_COUNT`）。
- **N_range**：声明产品域 **[2, 6]**。sweep 采样域 **[2, 6]**（偏中）。
- **sampling domain**：`rng.choices((2,3,4,5,6), weights=偏中)`；clamp 到 [2,6]。
- **copied object**：单个同心环（P3 torus `guard_ring_{i}` / P2 ring solid），等径递增半径。
- **naming**：`guard_ring_{i}`（wire_guard_cage 风格，P3 L126-138 `for i, ring_r in enumerate(...)`）；ring_spoke_grille 风格 inline union（无独立 part 名）。
- **placement**：同心，半径 `RING_R0 + k·ring_pitch`（绝对式，P2 L142-143 / P3 GUARD_RING_RADII）。
- **joint policy**：同心环是**非移动复制件**（Rule 1）→ inline 为格栅 part/visual，**无独立 joint**；随壳固定。
- **source/gating**：源 P3 L126-138 + P2 L125-133；**仅当 grille_style∈{ring_spoke_grille, wire_guard_cage} 时此轴活跃**（其余 grille 候选 Rg 不适用，slot_choice 不编 rg）。

## 拓扑多样性审计

总组合数（合法化前）：housing_form(4) × grille_style(5) × backdraft_shutter(4) × Kb 采样数(4) × Nf 采样数(5, 仅 louver_shutter) × Rg 采样数(5, 仅 ring/guard grille)。

主拓扑笛卡尔积（不含 multiplicity）：4 × 5 × 4 = **80**（含 0 / 1 REVOLUTE(+Y) / 1 REVOLUTE(-X) / N REVOLUTE 的 backdraft joint 拓扑 × 5 grille 形态 × 4 壳体）。
叠 impeller_blade_count(4) → 320。
叠条件 multiplicity：backdraft=louver_shutter 时 × Nf(5)；grille∈{ring,guard} 时 × Rg(5)。粗合法组合估算（兼容矩阵裁剪后，见下）≈ **数百**，远超门控。

仅 backdraft_shutter(4：0/1+Y/1−X/N REVOLUTE) × grille_style(5) = 20 个 distinct joint+面形态组合 ≥ 10 已稳过；叠 housing(4) → 80，叠 Kb / Nf / Rg 后充裕。

理由：backdraft_shutter 提供真正的 joint 拓扑差异（0 / 1 REVOLUTE(+Y) / 1 REVOLUTE(-X) / N 独立 REVOLUTE），grille_style 提供 0/1 格栅 part + 5 种出风面 mesh，housing_form 提供 4 种 part 树/轴向，三轴笛卡尔积即 80 distinct slot tuple；叠三根 multiplicity（Kb 进 `kb{Kb}`、Nf 进 `nf{Nf}`、Rg 进 `rg{Rg}`）后远超。**Kb / Nf / Rg 必须编入 `slot_choices_for_seed` 的 tuple**（对齐 cushion/fence_cascade/shopping_bucket），否则损失三根拓扑维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` housing_form → 受兼容矩阵 gate 选 grille_style / backdraft_shutter → `rng.choices` 加权 Kb∈{3,5,7,8} → 条件采 Nf（仅 louver_shutter）/ Rg（仅 ring/guard grille）→ uniform 各连续 scale。compatibility matrix 排除/降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9 覆盖每个 housing×backdraft 家族 ≥1 例。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）。本类别合法 distinct slot tuple（80 主拓扑 × Kb(4) × 条件 Nf/Rg）按 ≥300 富类别口径观察，预期可达 ≥150。

Controlled local parameterization：见 §参数表的 housing_dia_scale / housing_depth_scale / impeller_dia_scale(equation=housing_dia_scale) / grille_recess_scale / flap_open_angle_scale(conditional@backdraft≠none) / louver_pitch_scale(conditional@louver_shutter) / guard_ring_pitch_scale(conditional@ring/guard grille)。全部 `resolve_config` clamp/派生 + 每 build 统一应用。采样契约：先采 named slot（housing/grille/backdraft）+ 三 multiplicity（解析 conditional 范围：Nf 仅 louver_shutter、Rg 仅 ring/guard、flap_angle/louver_pitch/guard_pitch 各自条件）→ 采 independent housing_dia/depth/recess scale → 派生 impeller_dia=housing_dia → 用四条 clearance/closed-pose inequality 投影/回缩。跨部件依赖（叶尖 vs bore、百叶排布 vs frame、同心环 vs 开口、flap range vs envelope）显式落 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 impeller_spin/flap_hinge origin、captured-shaft/pin 接口、三根 multiplicity 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` housing_form（经兼容矩阵）→ 选 grille_style / backdraft_shutter → `rng.choices` 加权 Kb → 条件采 Nf/Rg → uniform 各 scale | slot_choices_for_seed 含 `kb{Kb}` + 条件 `nf{Nf}`/`rg{Rg}` 且与 build 一致 |
| compatibility matrix | (1) **backdraft_shutter × housing_form**：multi_blade_louver_shutter 需方/矩形开口 frame → 优先方壳 P2 / 圆法兰 P4；圆套筒 P1 配 single_gravity_flap（后缘 top hinge）；P4 自带 single_disc_flap_topring；inline_duct P3（两端开口长管）默认 none 或 single_disc（drum-style 需加铰，弱兼容）。非法组合降级为 none。 (2) **grille_style × housing_form**：woven_square_mesh/perforated_plate 配圆口壳（P1/P4）；ring_spoke_grille 配方壳 P2；wire_guard_cage 配长管 P3；louvered_front_grille 配圆套筒 P1。跨配允许但优先匹配。 (3) **Nf 仅 louver_shutter 活跃**；**Rg 仅 ring/guard grille 活跃**；其余组合该轴退化为 1 / 不编 slot_choice。 (4) impeller 恒存在，Kb 全兼容。 (5) backdraft flap/blade 全开 range 内不撞壳壁/格栅。 | 无 floating / 风叶悬空 / 叶尖撞 bore / 百叶撞 frame / 同心环超开口 / flap 撞壳 / 格栅不遮风口 / 轴向错误 |
| controlled local variation | 7 个 clamped scale（housing_dia/depth、impeller_dia=equation、grille_recess、flap_angle@backdraft≠none、louver_pitch@louver_shutter、guard_ring_pitch@ring/guard）；conditional 按上游 enum 解析 | 比例变化不破坏 impeller_spin/flap_hinge origin、captured shaft/pin、格栅遮护、bore clearance、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 QC（CONTINUOUS spin + REVOLUTE flap 姿态）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| housing_form | 4 | yes | yes | 4 母资产已占满（套筒/方壳/长管/法兰）|
| grille_style | 5 | yes | yes | mesh/ring-spoke/wire-guard/louvered/perforated |
| backdraft_shutter | 4 | yes | yes | none / gravity_flap(+Y) / disc_flap_topring(−X) / multi_blade_louver(N×REVOLUTE)（主机构）|
| impeller_blade_count (Kb) | 4（采样域 {3,5,7,8}）| yes | yes | 恒存在多重性轴，编入 slot_choice |
| shutter_flap_count (Nf) | 5（采样域 [2,6]，仅 louver_shutter）| yes | yes | 条件多重性轴 |
| guard_ring_count (Rg) | 5（采样域 [2,6]，仅 ring/guard grille）| yes | yes | 条件多重性轴 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("impeller_blade_count", f"kb{Kb}")`，并在条件激活时含 `("shutter_flap_count", f"nf{Nf}")` / `("guard_ring_count", f"rg{Rg}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling；Kb 采样域 ⊆ [3,9]、Nf ⊆ [2,6]、Rg ⊆ [2,6]
- `resolve_config` clamp 三根 multiplicity 到声明范围，各 scale clamp；impeller_dia=housing_dia 派生；flap_angle/louver_pitch/guard_ring_pitch 为 conditional 随 backdraft/grille 解析；四条 clearance/closed-pose inequality 在 resolve 内投影/回缩
- compatibility matrix / gating 阻止非法组合（louver_shutter 需方/矩形 frame；Nf 仅 louver_shutter；Rg 仅 ring/guard grille；非法 backdraft 降级 none）
- 连续 scale clamp 后不破坏 impeller_spin/flap_hinge origin / captured-shaft/pin 接口 / 格栅遮护 / bore clearance / 三根 multiplicity 复制
- 关键 joint：impeller `impeller_spin`/`fan_spin` **CONTINUOUS** axis=duct axis（P1/P3 abs(axis[0])>0.99 / P2 abs(axis[2])>0.99 / P4 abs(axis[1])>0.99），无 lower/upper；backdraft single_gravity_flap `flap_hinge` REVOLUTE axis≈(0,1,0)；single_disc_flap_topring `flap_hinge` REVOLUTE axis≈(-1,0,0)；multi_blade_louver_shutter 每 `shutter_blade_{i}_hinge` REVOLUTE axis≈(1,0,0)，lower=0
- captured shaft/pin/press-fit：element-scoped `allow_overlap`（`fan_rotor/impeller_rotor`↔`motor_shaft/motor_bushing`；`flap_knuckle(_i)`↔`hinge_pin`；grille `*_rim`↔壳壁），照搬各样本 run_tests 的 allow_overlap 段（P1 L224-244 / P2 L345-355 / P3 L288-316 / P4 L281-295 / gravity_flap fork L324-338 / louver_shutter fork L440-450）
- copied object 遵循命名 + 绝对式等距 placement + Rule 1（impeller 叶 / 同心环无独立 joint；百叶每片独立 REVOLUTE）
- grandfather：所有 shaft/pin/press-fit captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把 vent 做成无旋转风叶的纯格栅 / 纯百叶阵列 → 出类（vent 不变身份必含 ≥1 CONTINUOUS impeller，藏在壳内被格栅遮护）。
- impeller 悬空、未 press-fit 在固定 motor_shaft/bushing 上 → floating；必须 captured shaft + allow_overlap。
- 把 Kb/Nf/Rg 当普通 int 参数、不进 slot_choice → 损失三根拓扑维度（违反 §8/§9 硬要求）。
- backdraft flap/blade rest pose 设成张开角而非 q=0 重力闭合 → current-pose 与目检不符（所有样本 lower=0 闭合）。
- multi_blade_louver_shutter 做成联动（tie-rod / 共享 joint）→ 样本是 N 个**独立** REVOLUTE；必须 per-blade 独立 hinge。
- 同心环 / impeller 叶当独立活动 part 加 joint → 违反 Rule 1（非移动复制件 inline）。
- impeller 叶尖超 bore / 百叶超 frame / 同心环超开口 → §7 inequality FAIL；须按比例缩或 clamp N。
- backdraft hinge origin 放在壳中心或任意点而非真实后缘/drum 顶铰线硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- impeller_spin 轴向错误（非 duct axis）→ 风叶盘转出 bore，axis 检查 FAIL。
- 给 captured shaft/pin/press-fit 补 MatingContract 硬对接 → 几何对不上 FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质（palette_style / scale）当新 candidate 塞进 slot → 不是结构差异。
- 把"裸露桌面/吊扇风扇"或"纯静态格栅"语义混入 → 出类（见边界）。

## 与相邻类别的边界

- 不该混入：**`vane_array_with_independent_pivots` / `louvered_shutter_assembly`（纯百叶阵列，无风叶）**——固定外框 + N 片 vane，**无旋转 impeller**；vent 必含旋转风叶，backdraft 只是可选附件。
- 不该混入：**`ceiling_fan` / `box_fan_with_control_knob` / `desk_fan`（裸露风扇）**——rotor 是裸主体、无穿墙/管道壳体出风格栅遮护、无 backdraft；vent 风叶藏在壳内被格栅遮护（建筑通风口）。
- 不该混入：**`range_hood` / 抽油烟机**——大型橱柜式带控制面板，非小型通风口。
- 不该混入：**静态 `vent_grille` / `perforated_panel`（无风叶纯格栅）**——无 articulation；vent 必须有 ≥1 CONTINUOUS 风叶。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **来源缺口** —— source map 命名的 3 根 multiplicity fork（impeller-blade-count-3/7、shutter-flap-count-4、guard-ring-count-4 = 4 记录）**未同步**进 data/records，本 spec 把三根轴改锚定 parent / 已同步 fork 的真实复制循环（FanRotor blade_count 形参；louver_shutter `for i in range(LOUVER_COUNT)` 独立 REVOLUTE；P3 `GUARD_RING_RADII` 同心环），是否接受 / 是否需补同步那 4 个 fork；(2) backdraft_shutter 把 P4 自带翻板（single_disc_flap_topring, axis −X）与 gravity_flap fork（axis +Y）列为两个 candidate 是否合理（joint 轴 / hinge 硬件 / 闭合姿态确有结构差异）；(3) Slot C 含 none（空机构）作为 candidate 是否符合 multiplicity/joint-topology 审计期望；(4) 三根 multiplicity 的 conditional 激活（Nf 仅 louver_shutter、Rg 仅 ring/guard grille）gating 策略；(5) statunified 壳体轴向（推荐世界 +X = duct axis，各 housing helper 内部旋转），还是保留各母资产原轴（+X/+Z/+Y）；(6) N_range 取值（Kb [3,9]、Nf [2,6]、Rg [2,6]）是否合理）|

## 模板实现备注（可选）

- 共享 helper：`_tube`（P1/P4 hollow cylinder）、`_build_housing_shell`/`_build_border_rim`（P2 方壳）、LatheGeometry shell（P3 长管）、flange/collar/drum（P4）—— 按 housing_form 切换；`_rotor_geometry`/`FanRotorGeometry`/`_rotor_solid`（impeller，blade_count=Kb）；`_build_ring_grille`/`front_guard`/`mesh_grille`/`_louver_slat`/`_perforated_disc`（grille，按 grille_style 切换，guard_ring_count=Rg）；`_build_louver_blade`/`_build_louver_frame`（louver_shutter，shutter_flap_count=Nf）；flap disc+knuckle（gravity_flap / disc_flap_topring）。
- captured 接口 allow_overlap：`run_vent_tests` 里逐机构补 element-scoped `allow_overlap`（rotor↔shaft/bushing；knuckle↔hinge_pin；grille rim↔壳壁），照搬各样本 run_tests 段（P1 L224-244、P2 L345-378、P3 L288-316、P4 L281-295、gravity_flap fork L301-338、louver_shutter fork L440-472）。
- conditional 范围解析顺序：先采 housing_form/grille_style/backdraft_shutter + Kb → 条件解析 Nf（仅 louver_shutter）/ Rg（仅 ring/guard grille）/ flap_angle（仅 backdraft≠none）/ louver_pitch（仅 louver_shutter）/ guard_ring_pitch（仅 ring/guard）→ 采 housing_dia/depth/recess independent scale → 派生 impeller_dia=housing_dia → 投影四条 clearance/closed-pose inequality。
- 壳体轴向：推荐模板内部统一世界 +X = duct axis，各 housing helper 在内部完成 mesh 旋转（P1/P3 已是 +X；P2 +Z、P4 +Y 需在 helper 内换算），impeller_spin/flap_hinge axis 随之统一；或保留各原轴并在 validator 按 housing_form 分支断言（见审核 notes (5)）。
- 参考模板：`agent/templates/Accessories_Cushion.py`（同为 mixed pattern：固定 named slots + multiplicity 轴进 slot_choice + 绝对式 placement + 共享 mesh 复用 + 兼容矩阵 gating + captured-pin allow_overlap 骨架）；`agent/templates/Bag_Suitcase_Shopping_bucket.py`（`("count", f"n{N}")` 进 slot_choice 范式）；vane_array 的 N×独立 REVOLUTE 百叶可参其 multiplicity 复制 + per-blade hinge 范式（用于 multi_blade_louver_shutter）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / impeller / B（P1 基线）| round_through_wall + impeller + woven_square_mesh | rec_model-…f4fe4250 | `_tube` L76-78 / `duct_sleeve` L92-118 / `bezel_ring` L121-142 / `mesh_grille` L145-179 / `fan_impeller`+CONTINUOUS L182-209 / allow_overlap L224-244 | 圆套筒壳基线 + CONTINUOUS impeller captured-shaft 范式 + 方网格栅 + 共享 _tube |
| S2 | A / B（含 guard_ring）| square_wall + ring_spoke_grille | rec_model-…4c3504f2 | `_build_housing_shell` L80-105 / `_build_ring_grille` L122-145 / `housing`+impeller L174-232 / boss/shaft allow_overlap L345-378 | 方壳基线 + 同心环+spoke 格栅（guard_ring_count 源）+ +Z 轴 impeller |
| S3 | A / B（含 guard_ring）| inline_duct_cylinder + wire_guard_cage | rec_model-…4010e666 | `duct_shell` lathe L87-116 / `front_guard` L124-177（`GUARD_RING_RADII` L126-138）/ `motor_mount`+impeller L184-271 / allow_overlap L288-316 | 长管壳基线 + wire guard cage（guard_ring_count 源）+ 独立 motor_mount FIXED |
| S4 | A / C（P4 自带）| round_flange + single_disc_flap_topring | rec_model-…6e21aa96 | flange/collar/drum L127-201 / `_rotor_solid` impeller L89-115/L204-226 / `backdraft_flap`+REVOLUTE −X L229-266 / allow_overlap L281-295 | 法兰鼓壳基线 + 单顶铰圆盘翻板（REVOLUTE −X）+ bolt flange + motor_bushing captured |
| S5 | B | louvered_front_grille | rec_variant-grille-style-louvered-front-grille-repla_…2901e840 | `_louver_slat` L84-86 / louver_frame + `for i in range(LOUVER_COUNT)` 角度斜板 L152-177 | 角度百叶面格栅（固定非移动）|
| S6 | B | perforated_plate | rec_variant-grille-style-perforated-plate-replace-th_…67dfdf18 | `_perforated_disc` L85-117 / `perforated_plate` part L184+ | 冲孔面板格栅（独立 FIXED part）|
| S7 | C（含 shutter_flap_count）| multi_blade_louver_shutter | rec_variant-backdraft-multi-blade-louver-shutter-add_…d3db9306 | `_build_louver_frame` L183-214 / `_build_louver_blade` L217-223 / `for i in range(LOUVER_COUNT)` `shutter_blade_{i}`+REVOLUTE +X L303-332 / allow_overlap L440-450 | N 叶独立 REVOLUTE 百叶（shutter_flap_count 源 + backdraft 主机构）|
| S8 | C | single_gravity_flap | rec_variant-backdraft-single-gravity-flap-add-a-sing_…bf2f8952 | hinge lug+pin L141-160 / `backdraft_flap` L253-272 / `flap_hinge` REVOLUTE +Y L275-285 / allow_overlap L324-338 | 单重力圆盘翻板（REVOLUTE +Y，套筒后缘 top hinge captured-pin）|
