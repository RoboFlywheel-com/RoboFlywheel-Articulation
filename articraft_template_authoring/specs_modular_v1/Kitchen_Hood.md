# hood (wall-mounted kitchen chimney range hood / extractor) — Modular Spec

> 来源小类：`picture/Kitchen/Hood`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Kitchen__Hood.md`。
> **"Hood" 在此 = 壁挂式厨房抽油烟机 / 烟罩（wall-mounted kitchen chimney range hood / cooker extractor hood），不是空调（air_conditioner 已有独立 slug）、也不是空气净化器 / 排气扇（vent 已有独立 slug）。**
> 结构家族 = 壁挂烟罩：一只 `canopy`（root，罩体壳 + 集成底板 + 凹腔 + 烟道接口）+ 头顶可伸缩烟囱 `chimney`（沿 +Z PRISMATIC 升降，套在固定 `lower_duct` 上）+ 罩下油网 `filter`（固定 / 翻盖 / 双百叶）+ 罩前面板控制 `control`（按键 / 旋钮 / 滑块）；**共享主运动 = 罩内鼓风机 `blower_fan` 绕竖直轴 CONTINUOUS 旋转（每个候选都有）**。
>
> **同步状态**：本 spec 引用的 8 个 5 星样本（1 个 parent + 7 个 fork 槽位变体）**已同步进本仓库 `data/records/<id>/`，rating=5**。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一逐行读完整文件核对）。引用以 part / joint / helper **名字** 为准（`canopy`/`chimney_sleeve`/`sleeve_{i}`/`blower_fan`/`grease_filter`/`filter_{i}`/`power_button`/`speed_knob`/`slider_tab` part；`canopy_to_chimney_sleeve`/`canopy_to_blower_fan`/`canopy_to_grease_filter`/`canopy_to_speed_knob`/`canopy_to_slider_tab` joint；`_canopy_shell`/`_pyramid_shell`/`_metal_body_shell`/`_glass_visor_geometry`/`_rect_tube`/`_build_sleeve_stage`/`_baffle_panel_cq` helper），行号仅作定位。
>
> **坐标约定（全样本统一，模板沿用）**：X = 宽（canopy ~0.90 m），Y = 深（~0.50 m，墙面在 y=−0.25），Z = 上（罩体底板下表面在 z=0）。烟囱沿 +Z 升降；油网在底板凹腔；控制在罩前 fascia（y=+0.25 附近，或 pyramid 的倾斜前面 / curved_glass 的 slim body 前面）。

## 元信息
| 项 | 值 |
|---|---|
| slug | `hood` |
| template path | `agent/templates/Kitchen_Hood.py` |
| test path (optional) | `tests/agent/test_hood_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: canopy_form + chimney + control，**外加** `filter_count` 油网多重性轴；四类层都以 parallel_children 直接挂在 `canopy` 根上）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 parent + 7 fork 槽位变体；均 converged、compile success、≥1 非 fixed joint、workbench-only，rating=5）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests + allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 8/8 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **共享基线拓扑（全部 8 个样本）**：`canopy`（root，罩壳 + 集成底板 + 凹腔 + 固定 `lower_duct` 烟道 + `motor_housing` + 双 `lamp_lens_{i}` + `brand_logo` + `indicator_lamp` inline visual）+ `chimney_sleeve`（或 dual 的 `sleeve_{i}`，PRISMATIC +Z 升降）+ `blower_fan`（FanRotorGeometry 转子 + `fan_shaft`，**`canopy_to_blower_fan` CONTINUOUS axis=(0,0,1)** 在油网后方旋转）+ 控制件。`canopy_to_blower_fan` CONTINUOUS 是**所有候选共享的主运动**（parent L300-308 / 每个变体都有），保证每个组合 ≥1 非 fixed joint。
- **Slot A canopy_form 轴**：是 canopy 壳 mesh 形态 + fascia 安装面法向变化（t_box / pyramid 不改 part/joint 拓扑，只改壳 mesh + control 安装面；curved_glass 额外多一个 `glass_visor` inline visual 且 body 变 slim、fan 半径缩小）。pyramid 把 fascia 改成**倾斜前面**，控制件安装轴改为斜面法向 → 与 Slot D 有真实接口耦合（见 §9）。
- **Slot B chimney 轴**：是 part 数 / joint 拓扑变化。single_telescope（parent）= 1 个 `chimney_sleeve` PRISMATIC；dual_telescope = 2 个 `sleeve_{i}` 串成 PRISMATIC linear_chain（`canopy_to_sleeve_0` → `sleeve_0_to_sleeve_1`），用 `_build_sleeve_stage` + `for i in range(2)` 发射 → +1 part +1 joint（链内）。
- **Slot C filter 轴**：是 part 数 / joint 拓扑变化。fixed_mesh（parent）= `filter_mesh_panel` 是 `canopy` 的 **inline visual，无独立 part/joint**（Rule 1）；hinged = `grease_filter` 独立 part，`canopy_to_grease_filter` **REVOLUTE axis=(1,0,0)** 0..π/2 翻下（+1 part +1 joint）；dual_baffle = `filter_{i}` 独立 part ×2，FIXED 到 canopy（`canopy_to_filter_{i}`），是 **filter_count multiplicity 轴**（见 §8）。
- **Slot D control 轴**：是 part 数 / joint 拓扑变化（但都 +1 part +1 joint，joint 类型不同）。push_button（parent）= `power_button` PRISMATIC axis=(0,−1,0) 0..4 mm 压入 + 4 个 inline `button_{i}` 静态假键；rotary_knob = `speed_knob`（KnobGeometry）REVOLUTE axis=(0,1,0) 0..270° + canopy 侧 `knob_escutcheon` 铒环；slider = `slider_tab`（`slider_cap`+`slider_stem`）PRISMATIC axis=(1,0,0) 0..60 mm + canopy 侧 `slider_track` + 3 个 `slider_tick_{i}`。

## 核心身份

一只**壁挂式厨房抽油烟机 / 烟罩**（wall-mounted kitchen chimney range hood）：一只钢 / 玻璃 **罩体 `canopy`**（root，坐挂于墙面 y=−0.25，底板下表面在 z=0；内有集成底板 + 凹腔 + 顶部排烟孔），罩内悬一只 **鼓风机转子 `blower_fan`**（在油网后方绕竖直轴 **CONTINUOUS** 旋转抽风——本类核心主运动），头顶有一截可伸缩 **烟囱 `chimney`**（套在固定 `lower_duct` 上，沿 +Z **PRISMATIC** 升降到天花板），罩底板凹腔内有 **油网 `filter`**（固定铝网 / 可翻下清洗的铰链网 / 并列百叶 baffle），罩前面板有 **控制 `control`**（按键 / 旋钮 / 滑块）。默认成熟域：canopy_form(3) × chimney(2) × filter(3) × control(3) 笛卡尔积 × 油网数 N∈[1,4] 的壁挂烟罩。活动语义 = **鼓风机 CONTINUOUS 旋转（全候选共享）** + **烟囱 PRISMATIC 升降（single / dual 串链）** + 可选 **油网 REVOLUTE 翻下**（hinged）+ **控制件 PRISMATIC 压 / REVOLUTE 旋 / PRISMATIC 滑**。

不该混入：
- **空调 / 分体壁挂空调（air_conditioner，已有独立 slug）**——虽同为壁挂矩形电器，但空调主体是出风口 + 摆叶（louver/vane swing），无烟囱、无油网、无罩下集风腔；source map 的 parent 同目录里有一条 mini-split AC 样本（不属本类）。本类身份在于「罩 + 烟囱 + 油网 + 鼓风机抽风」。
- **空气净化器 / 排气扇 / 通风口（vent / air purifier，vent 已有独立 slug）**——净化器是落地 / 桌面圆柱，排气扇是墙 / 窗格栅风叶；本类是厨房灶台上方的集烟罩，主运动是抽风 fan + 升降烟囱。
- **吊顶 / 嵌入式集成灶 / 内置烤箱（built_in_oven，已有独立 slug）**——嵌入橱柜的箱体门 + 拉篮；本类是壁挂悬空罩 + 烟囱。

## 槽位 + 候选模块表

> **建模注记**：`canopy_form`（Slot A）主要是 `canopy` 壳的 mesh 足迹形态（box / pyramid / curved glass）+ control 安装面法向，由 canopy mesh helper 一次决定；t_box / pyramid 不改 part 树 / joint 拓扑（pyramid 仅把 control 安装轴改为斜面法向），curved_glass 额外多一个 `glass_visor` inline visual。`chimney` / `filter` / `control` 才是改 part 数 / joint 拓扑（或多重性）的轴。所有 4 个 slot 直接挂在 `canopy` 根上（parallel_children），dual_telescope 的两段内部是 PRISMATIC linear_chain，dual_baffle 是 filter_count multiplicity。

### Slot A：canopy_form（罩体壳 / 轮廓 —— canopy mesh 足迹 + fascia 安装面法向）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| t_box（基线）| rec_model-a-wall-mounted-t-style-box-linear-kitchen-_...e562777f（parent）| `_canopy_shell` L100-146（tapered skirt + fascia box loft + 凹腔 + filter/lamp/exhaust 切口）/ `canopy` 装配 L176-240 | eligible if compatible | 经典线性 box hood：tapered skirt（z 0..0.06）lofting 到 0.90×0.50×0.12 m fascia box + 集成底板；fascia 是**垂直前面**（y=+0.25），控制挂垂直面 |
| pyramid | rec_hood_var_form_pyramid | `_pyramid_shell` L124-172 / `_front_y_at_z` L62-64 / `FACE_TILT_FROM_Z`/`FRONT_NY`/`FRONT_NZ` 斜面法向数学 L51-59 / control 倾斜安装 L246-277, L350-364 | eligible if compatible | 截顶金字塔 loft（0.90×0.50 底 → 0.34×0.30 顶 @z=0.28，顶心 y=−0.10）；**倾斜前面**最戏剧化；控制件 rpy 用 `FACE_TILT_*`、power button 轴 = 斜面内法向 `(0,−FRONT_NY,−FRONT_NZ)`（A×D 接口耦合）|
| curved_glass | rec_hood_var_form_curved_glass | `_metal_body_shell` L123-155（slim box body）+ `_glass_visor_geometry` L170-208（`section_loft` over `LoftSection`/`SectionLoftSpec` 沿 `GLASS_CURVE`）/ 装配 L227-308 | eligible if compatible | slim stainless body（0.90×0.20×0.14 @z 0.30..0.44）+ 凹面 section-loft 钢化玻璃 visor（从 z≈0.30 下扫到 z≈0.04）；**body 更浅 + fan 半径缩到 0.050 + duct top 较低**（与 dual_telescope 叠加需复核插入余量，见 §9）|

### Slot B：chimney（可伸缩烟囱 —— `lower_duct` 固定 + 伸缩 sleeve；决定烟囱 part 数与 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| single_telescope（基线）| rec_..._e562777f（parent）| `chimney_sleeve` part + `sleeve_shell` + `guide_pad_{i}`×4 L243-267 / `canopy_to_chimney_sleeve` **PRISMATIC** axis=(0,0,1) 0..0.35 L268-276 / `_rect_tube` L149-158 | eligible if compatible | 一截上 sleeve（`_rect_tube` 0.336×0.296）套在固定 `lower_duct`（canopy inline visual L183-188）上沿 +Z 升降；4 个 friction `guide_pad_{i}` 贴 duct 壁（captured，`allow_overlap(guide_pad_{i}, lower_duct)`）；**1 part 1 PRISMATIC joint** |
| dual_telescope | rec_hood_var_chimney_telescope_dual | `_build_sleeve_stage` helper L164-219 + `for i in range(2)` → `sleeve_0`/`sleeve_1` part（`sleeve_shell_{i}` + `guide_pad_{i}_{j}`）；joint `canopy_to_sleeve_0`（origin 在 duct）→ `sleeve_0_to_sleeve_1`（origin (0,0,0)，parent=sleeve_0），均 **PRISMATIC +Z** 0..0.35 L303-342 | eligible if compatible | 两级嵌套伸缩（inner 0.336×0.296，outer 0.352×0.312）；stage1 parent=sleeve_0 → **PRISMATIC linear_chain**，全展开 = 2×travel；**2 part 2 PRISMATIC joint**（链）；stage0 pad 贴 duct、stage1 pad 贴 sleeve_shell_0 |

### Slot C：filter（罩下油网机构 —— 决定油网 part 数 / joint 拓扑 / multiplicity）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| fixed_mesh（基线）| rec_..._e562777f（parent）| `filter_mesh_panel`（`SlotPatternPanelGeometry`）inline visual on `canopy` L190-203 / 凹腔切口在 `_canopy_shell` L122-128 | eligible if compatible | 单块深色 slotted 铝网 panel，recessed 在底板上方；**`canopy` 的 inline visual，无独立 part/joint**（Rule 1）；fan 在其后方 `expect_gap` |
| hinged | rec_hood_var_filter_hinged | `grease_filter` part（`filter_mesh_panel` 前缘 + `hinge_knuckle_{i}`×3）L327-344 / `canopy_to_grease_filter` **REVOLUTE** axis=(1,0,0) 0..π/2 L347-355 | eligible if compatible | 单块网 panel 绕前缘 X 轴 hinge 翻下清洗（part 帧在 hinge 线，panel 向 −Y 延伸）；origin=(0, +FILTER_PANEL_D/2, PLATE_T+0.001) 落在前缘铰线；**+1 part +1 REVOLUTE joint**；`hinge_knuckle_{i}` captured 在 canopy_shell（`allow_overlap`）|
| dual_baffle | rec_hood_var_filter_dual_baffle | `_baffle_panel_cq` helper L176-224 + `for i in range(2)` → `filter_{i}` part（`baffle_panel_{i}`）L313-331；FIXED `canopy_to_filter_{i}`；canopy 侧 `filter_divider` L256-261 + `filter_rail_{fi}_{ri}` rails L265-274 | eligible if compatible | 两块并列可拆 baffle 滤网（框 + 平行百叶条 + 中央 cross-bar），坐 support rails 上；每块 **FIXED 到 canopy**（`canopy_to_filter_{i}`）；**MULTIPLICITY 轴**（filter_count，见 §8）；复制件本身不活动，活动关节靠共享 blower fan + 其余 slot |

### Slot D：control（罩前控制 —— 用户输入，决定控制件 part 树与 joint 类型）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| push_button（基线）| rec_..._e562777f（parent）| `power_button` part + `button_cap` L311-317 / `canopy_to_power_button` **PRISMATIC** axis=(0,−1,0) 0..0.004 L318-326；canopy 侧 4 个静态 `button_{i}` L220-226 | eligible if compatible | 最右键是活动 power button（4 mm 压入 fascia），左侧 4 个静态假键 inline；button axis = fascia 内法向（t_box 垂直 (0,−1,0)，pyramid 改斜面法向 `(0,−FRONT_NY,−FRONT_NZ)`，见 A×D 耦合）；**+1 part +1 PRISMATIC joint** |
| rotary_knob | rec_hood_var_control_rotary_knob | `speed_knob` part + `knob_body`（`KnobGeometry`+`KnobSkirt`/`KnobGrip`/`KnobIndicator`）L320-337 / `canopy_to_speed_knob` **REVOLUTE** axis=(0,1,0) 0..270° L338-350；canopy 侧 `knob_escutcheon` 铒环 L227-235 | eligible if compatible | 单只滚花旋钮绕 Y 轴 REVOLUTE 旋（穿 escutcheon 铒环伸出 +Y），替代按键行；KnobGeometry 对齐 Z，rpy=(π/2,0,0) 转轴向 +Y；**+1 part +1 REVOLUTE joint** |
| slider | rec_hood_var_control_slider | `slider_tab` part（`slider_cap` + `slider_stem`）L324-338 / `canopy_to_slider_tab` **PRISMATIC** axis=(1,0,0) 0..0.060 L339-347；canopy 侧 `slider_track` 槽 L226-231 + `slider_tick_{i}`×3 L233-239 | eligible if compatible | 横向 low/med/high 滑块 tab（cap 外凸 + stem 穿 track 槽）沿 +X 滑 60 mm；`slider_stem` captured 穿 canopy_shell（`allow_overlap`）；**+1 part +1 PRISMATIC joint** |

## 槽位图（slot graph）

pattern: mixed（固定 named slots: canopy_form + chimney + control 各自挂在共同 `canopy` 根上（parallel children），外加 `filter_count` 在 canopy 凹腔上 N 次复制 baffle 油网；blower_fan CONTINUOUS 也是 canopy 的 child，全候选共享）

```
canopy (root, 坐挂墙面 y=-0.25, 底板下表面 z=0; 由 canopy_form 决定罩壳 mesh + 凹腔 + 固定 lower_duct + 排烟孔 + motor_housing + lamps + logo inline)
  │
  ├── blower_fan ──[canopy_to_blower_fan: CONTINUOUS axis=(0,0,1), origin=(0,0,FAN_Z)]   ← 全候选共享主运动（在油网后方旋转抽风）
  │        （fan_shaft captured 进 motor_housing: allow_overlap(fan_shaft, motor_housing)）
  │
  ├── [chimney slot]  (二选一)
  │     ├─ single_telescope : chimney_sleeve ──[canopy_to_chimney_sleeve: PRISMATIC axis=(0,0,1), origin=(0,DUCT_Y,SLEEVE_Z0), 0..0.35]
  │     │                       （guide_pad_{i} captured 贴 lower_duct 壁）
  │     └─ dual_telescope   : sleeve_0 ──[canopy_to_sleeve_0:  PRISMATIC +Z, origin=(0,DUCT_Y,SLEEVE_Z0), 0..0.35]
  │                            sleeve_1 ─[sleeve_0_to_sleeve_1: PRISMATIC +Z, parent=sleeve_0, origin=(0,0,0), 0..0.35]  ← PRISMATIC linear_chain
  │
  ├── [filter slot]  (三选一; dual_baffle 含 filter_count 多重性)
  │     ├─ fixed_mesh  : (filter_mesh_panel = canopy inline visual, 无 joint, Rule 1)
  │     ├─ hinged      : grease_filter ──[canopy_to_grease_filter: REVOLUTE axis=(1,0,0), origin=(0,+FILTER_PANEL_D/2,PLATE_T+0.001), 0..π/2]
  │     └─ dual_baffle : filter_{i} ──[canopy_to_filter_{i}: FIXED, origin=(sign*BAFFLE_X_OFFSET,0,FILTER_Z)]  i∈range(N)  ← filter_count multiplicity
  │                       （canopy 侧 filter_divider + filter_rail_{fi}_{ri} 支撑轨; baffle_panel_{i} captured 接触 rail）
  │
  └── [control slot]  (三选一)
        ├─ push_button : power_button ──[canopy_to_power_button: PRISMATIC axis=fascia 内法向, origin 在 fascia 面, 0..0.004]
        │                 （t_box: axis=(0,-1,0); pyramid: axis=(0,-FRONT_NY,-FRONT_NZ) 斜面法向）+ 4 个静态 button_{i} inline
        ├─ rotary_knob : speed_knob ──[canopy_to_speed_knob: REVOLUTE axis=(0,1,0), origin=(KNOB_X,FASCIA_FRONT,KNOB_Z), 0..270°]
        │                 + canopy 侧 knob_escutcheon 铒环
        └─ slider      : slider_tab ──[canopy_to_slider_tab: PRISMATIC axis=(1,0,0), origin=(SLIDER_X0,FASCIA_FRONT+0.001,SLIDER_Z), 0..0.060]
                          + canopy 侧 slider_track + slider_tick_{i}×3
```

接口点位与 joint 语义：
- **blower_fan（全候选共享）**：mating = canopy 凹腔中心顶部 motor_housing。CONTINUOUS axis=(0,0,1)，origin=(0,0,FAN_Z)（curved_glass 为 (0,BODY_CY,FAN_Z)）；motion_limits 无 lower/upper（连续）；`fan_shaft` captured 进 `motor_housing`（`allow_overlap(fan_shaft, motor_housing)`，curved_glass 还 allow `fan_rotor↔motor_housing`）。fan 在油网正后方（`expect_gap(fan, filter, axis=z, min~0.005-0.015, max~0.06)`）。
- **chimney 接口（互斥二选一）**：所有 sleeve 挂 canopy 顶部 duct 区。
  - single_telescope：PRISMATIC +Z，origin=(0,DUCT_Y,SLEEVE_Z0)；`guide_pad_{i}` captured 贴 `lower_duct` 壁（`allow_overlap` + `expect_contact`）；闭合 sleeve 与 duct Z 向 `expect_overlap` ≥0.30（curved_glass 因 slim body 降到 0.25），全展开仍保 ≥0.05（curved_glass 0.02）。
  - dual_telescope：stage0 PRISMATIC origin 同 single；stage1 parent=sleeve_0、origin=(0,0,0)，PRISMATIC +Z；stage0 pad 贴 duct、stage1 pad 贴 sleeve_shell_0；两 sleeve 同 Z 段 concentric nesting（`allow_overlap(sleeve_shell_0, sleeve_shell_1)`）。
- **filter 接口（三选一）**：
  - fixed_mesh：无 joint（`filter_mesh_panel` canopy inline visual，坐凹腔上方，`expect_gap` 守 fan 间隙）。
  - hinged：前缘铰线 ↔ `grease_filter` part，REVOLUTE axis=(1,0,0)，origin=(0,+FILTER_PANEL_D/2,PLATE_T+0.001)，q=0 闭合平贴、q→π/2 后缘翻下；`hinge_knuckle_{i}` captured 在 canopy_shell（`allow_overlap`）。
  - dual_baffle：每块 `filter_{i}` FIXED 到 canopy，origin=(sign*BAFFLE_X_OFFSET,0,FILTER_Z)；坐 `filter_rail_{fi}_{ri}` 支撑轨（`expect_contact(baffle_panel_{i}, filter_rail_{i}_0)`），中间 `filter_divider` 分隔；并列沿 X（无 X 重叠）。
- **control 接口（三选一）**：所有控制件挂 canopy 前 fascia 面。
  - push_button：PRISMATIC，axis = fascia 内法向（t_box (0,−1,0)；**pyramid (0,−FRONT_NY,−FRONT_NZ) 斜面内法向**），origin 在 fascia 面（t_box (POWER_BTN_X,BTN_Y,BTN_Z)）；`button_cap` captured 穿 canopy_shell（`allow_overlap`）；q=0 凸出、q→0.004 压入。
  - rotary_knob：REVOLUTE axis=(0,1,0)，origin=(KNOB_X,FASCIA_FRONT,KNOB_Z)，穿 `knob_escutcheon` 伸 +Y；`knob_body` captured 穿 canopy_shell（`allow_overlap`）；旋转不漂移（origin 固定）。
  - slider：PRISMATIC axis=(1,0,0)，origin=(SLIDER_X0,FASCIA_FRONT+0.001,SLIDER_Z)；`slider_stem` captured 穿 canopy_shell / slider_track（`allow_overlap`）；q=0 low、q→0.060 high。
- **filter_count 接口**：baffle 油网为**非移动复制件**（FIXED），沿 X 绝对式等距并排（中心 sign*BAFFLE_X_OFFSET），canopy 侧每块配 2 条 `filter_rail_{fi}_{ri}` + 中间 `filter_divider`。
- **mating policy**：所有 captured 接口（fan_shaft-in-housing、guide_pad-on-duct、hinge_knuckle-on-shell、button/knob/slider-stem-through-shell、baffle-on-rail）是 captured-fit / captured-slide / captured-pin，**非两轴对齐面对接 → 省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：blower_fan q=0（任意角，连续）；chimney sleeve q=0（闭合，顶 ~1.10 m）；hinged filter q=0（闭合平贴）；control q=0（按键凸出 / 旋钮 0° / 滑块 low）。
- **互斥 / 可选 / 派生**：chimney 二候选互斥；filter 三候选互斥；control 三候选互斥；fixed_mesh 无独立机构件（空机构，活动靠共享 fan）；filter_count 仅 dual_baffle 风格暴露（fixed_mesh/hinged 即 N=1，见 §8）。canopy_form 与 chimney/filter 正交，但 **canopy_form × control 有真实耦合**（pyramid 倾斜 fascia → control 安装轴 / placement 重算；curved_glass slim body × dual_telescope 插入余量复核，见 §9）。

## 每槽位 Module Emits / Interfaces

### Slot A / canopy_form（以 t_box 为例；pyramid/curved_glass 换 mesh helper + fascia 法向）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `canopy`（root，visual: `canopy_shell` 罩壳 + 固定 `lower_duct` 烟道 + `motor_housing` + `lamp_lens_{i}`×2 + `brand_logo` + `indicator_lamp` inline; curved_glass 多 `body_shell`+`glass_visor`）| t_box `_canopy_shell` L100-146 + 装配 L176-240 / pyramid `_pyramid_shell` L124-172 / curved_glass `_metal_body_shell` L123-155 + `_glass_visor_geometry` L170-208 |
| internal joints | 无（canopy 是 root）| — |
| upstream interface | root（坐挂墙面，无父）| — |
| downstream interface | 顶部 duct 区（供 chimney PRISMATIC）+ 底板凹腔（供 filter）+ 前 fascia 面（供 control）+ 凹腔中心顶（供 blower_fan CONTINUOUS）| t_box L139-145, L183-188 |

### Slot B / chimney — single_telescope
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chimney_sleeve`（visual: `sleeve_shell` + `guide_pad_{i}`×4）| parent L243-267 |
| internal joints | `canopy_to_chimney_sleeve` PRISMATIC axis=(0,0,1)，origin=(0,DUCT_Y,SLEEVE_Z0)，0..0.35 | parent L268-276 |
| upstream interface | `guide_pad_{i}` captured 贴 `lower_duct` 壁（`allow_overlap`+`expect_contact`）；sleeve 套 duct（`expect_within` xy + `expect_overlap` z ≥0.30）| parent L358-365, L399-414 |

### Slot B / chimney — dual_telescope
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sleeve_0`（`sleeve_shell_0`+`guide_pad_0_{j}`×4）+ `sleeve_1`（`sleeve_shell_1`+`guide_pad_1_{j}`×4），`_build_sleeve_stage` + `for i in range(2)` 发射 | dual L164-219, L303-342 |
| internal joints | `canopy_to_sleeve_0` PRISMATIC +Z origin=(0,DUCT_Y,SLEEVE_Z0) + `sleeve_0_to_sleeve_1` PRISMATIC +Z parent=sleeve_0 origin=(0,0,0)，各 0..0.35（PRISMATIC linear_chain，全展 2×travel）| dual L208-218, L318-342 |
| upstream interface | stage0 pad 贴 `lower_duct`、stage1 pad 贴 `sleeve_shell_0`（双组 captured `allow_overlap`）；concentric nesting `allow_overlap(sleeve_shell_0, sleeve_shell_1)` | dual L426-450 |

### Slot C / filter — fixed_mesh
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`filter_mesh_panel` 为 `canopy` inline visual）| parent L190-203 |
| internal joints | 无（Rule 1）| — |
| upstream interface | 坐底板凹腔上方（`expect_gap(fan, canopy, negative_elem=filter_mesh_panel)` 守 fan 间隙）| parent L468-476 |

### Slot C / filter — hinged
| emits | 描述 | 来源 |
|---|---|---|
| parts | `grease_filter`（`filter_mesh_panel` 在 part 帧 −Y 侧 + `hinge_knuckle_{i}`×3 前缘）| hinged L327-344 |
| internal joints | `canopy_to_grease_filter` REVOLUTE axis=(1,0,0)，origin=(0,+FILTER_PANEL_D/2,PLATE_T+0.001)，0..π/2 | hinged L347-355 |
| upstream interface | `hinge_knuckle_{i}` captured 在 canopy 底板边（`allow_overlap(hinge_knuckle_{i}, canopy_shell)`）；q=0 闭合平贴、π/2 翻下 | hinged L398-405, L573-581 |

### Slot C / filter — dual_baffle（含 filter_count multiplicity）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `filter_{i}`（`baffle_panel_{i}`，`_baffle_panel_cq` 框+百叶条+cross-bar）；canopy 侧 `filter_divider` + `filter_rail_{fi}_{ri}` rails | dual_baffle L176-224, L256-274, L313-331 |
| internal joints | `canopy_to_filter_{i}` FIXED，origin=(sign*BAFFLE_X_OFFSET,0,FILTER_Z)，i∈range(N) | dual_baffle L325-331 |
| upstream interface | `baffle_panel_{i}` 坐 `filter_rail_{i}_0` 支撑轨（`expect_contact`）；并列沿 X（无 X 重叠）| dual_baffle L615-639 |

### Slot D / control — push_button
| emits | 描述 | 来源 |
|---|---|---|
| parts | `power_button`（`button_cap`）；canopy 侧 4 个静态 `button_{i}` inline | parent L220-226, L311-317 |
| internal joints | `canopy_to_power_button` PRISMATIC axis=fascia 内法向（t_box (0,−1,0)；pyramid (0,−FRONT_NY,−FRONT_NZ)），origin 在 fascia 面，0..0.004 | parent L318-326 / pyramid L355-364 |
| upstream interface | `button_cap` captured 穿 canopy_shell（`allow_overlap`）；q=0 凸出、0.004 压入 | parent L351-357 |

### Slot D / control — rotary_knob
| emits | 描述 | 来源 |
|---|---|---|
| parts | `speed_knob`（`knob_body` via KnobGeometry+Skirt/Grip/Indicator）；canopy 侧 `knob_escutcheon` 铒环 | rotary_knob L227-235, L320-337 |
| internal joints | `canopy_to_speed_knob` REVOLUTE axis=(0,1,0)，origin=(KNOB_X,FASCIA_FRONT,KNOB_Z)，0..270° | rotary_knob L338-350 |
| upstream interface | `knob_body` captured 穿 canopy_shell（`allow_overlap`），穿 escutcheon 伸 +Y；旋转不漂移 | rotary_knob L375-381, L566-577 |

### Slot D / control — slider
| emits | 描述 | 来源 |
|---|---|---|
| parts | `slider_tab`（`slider_cap` 外凸 + `slider_stem` 穿槽）；canopy 侧 `slider_track` + `slider_tick_{i}`×3 | slider L226-239, L324-338 |
| internal joints | `canopy_to_slider_tab` PRISMATIC axis=(1,0,0)，origin=(SLIDER_X0,FASCIA_FRONT+0.001,SLIDER_Z)，0..0.060 | slider L339-347 |
| upstream interface | `slider_stem` captured 穿 canopy_shell / slider_track（`allow_overlap`）；q=0 low、0.060 high | slider L372-378 |

### filter_count multiplicity（baffle 油网复制；non-moving FIXED 复制件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `filter_{i}` part（`baffle_panel_{i}` visual），`for i in range(N)`；canopy 侧 `filter_rail_{fi}_{ri}` + `filter_divider` | dual_baffle L313-331, L256-274 |
| joints | `canopy_to_filter_{i}` FIXED（复制件不活动；活动靠共享 blower fan + 其余 slot）| dual_baffle L325-331 |
| placement | `for i in range(N)`，沿 X 绝对式等距并排（中心 sign*BAFFLE_X_OFFSET；N>2 需把 offset 推广为 (i-(N-1)/2)·pitch）| dual_baffle L314-331 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| canopy_form | enum | t_box / pyramid / curved_glass | t_box | choice | 由 deterministic procedural sampler 选；决定 canopy mesh helper + fascia 安装面法向 | Slot A 表 |
| chimney | enum | single_telescope / dual_telescope | single_telescope | choice | sampler 选；dual 多一个 sleeve part + PRISMATIC 链关节 | Slot B 表 |
| filter | enum | fixed_mesh / hinged / dual_baffle | fixed_mesh | choice | sampler 选；含空机构 fixed_mesh；dual_baffle 触发 filter_count | Slot C 表 |
| control | enum | push_button / rotary_knob / slider | push_button | choice | sampler 选；joint 类型各异（PRISMATIC/REVOLUTE/PRISMATIC）| Slot D 表 |
| filter_count (N) | int | 声明域 [1,4]；sweep 采样域 [1,4]（偏小加权：1 高频、2 常见、3-4 长尾）| 1 | conditional→slot_choice | 编入 slot_choice 为 `n{N}`（拓扑维度）；仅 filter=dual_baffle 时 N 可>1（fixed_mesh/hinged 恒 N=1，见 §8）| dual_baffle L313-331 |
| palette_style | enum | brushed_stainless / glossy_black / black_glass / white_steel / inox_glass | brushed_stainless | palette | palette only，**不计入 slot_choice**；每 seed 采一套（见下表）| 各样本材质 |
| canopy_width_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 canopy X 主尺寸（CANOPY_W / BODY_W），clamp；联动 fascia 宽、油网排布上限 | parent L39 / curved_glass L42 |
| canopy_depth_scale | float | [0.88, 1.12] | 1.0 | independent | 缩放 canopy Y 深（CANOPY_D / BODY_D）→ 凹腔深、fascia front Y、duct Y，clamp | parent L40 / curved_glass L43 |
| canopy_height_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放罩壳高（CANOPY_BOX_H / CANOPY_H / BODY_H）→ HINGE/HOUSING Z，clamp | parent L41 / pyramid L42 / curved_glass L44 |
| chimney_travel_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 sleeve PRISMATIC upper（SLIDE_TRAVEL，每级行程），clamp（≤ 保留插入余量所需）| parent L74 |
| fan_radius_scale | float | [0.90, 1.10] | 1.0 | conditional | 缩放 FAN_R（curved_glass 基线最小 0.050，t_box/pyramid 0.085）；clamp 保 fan 在凹腔内、油网后 | parent L80 / curved_glass L102 |
| hinge_open_angle_scale | float | [0.85, 1.05] | 1.0 | conditional | 仅 filter=hinged 有效；缩放 `canopy_to_grease_filter` upper（保 ≤π·0.55）| hinged L354 |
| knob_open_angle_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 control=rotary_knob 有效；缩放 `canopy_to_speed_knob` upper（保 ≤π·1.6 即 ~288°）| rotary_knob L101, L348 |
| slider_travel_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 control=slider 有效；缩放 `canopy_to_slider_tab` upper（≤ fascia 可用宽度）| slider L99, L346 |
| button_travel_scale | float | [0.80, 1.20] | 1.0 | conditional | 仅 control=push_button 有效；缩放 BTN_TRAVEL（保 ≤ fascia 壁厚级，~0.003-0.006）| parent L96 |
| baffle_spacing_scale | float | [0.90, 1.10] | 1.0 | conditional | 仅 filter=dual_baffle 且 N≥2 有效；缩放并列 baffle pitch | dual_baffle L55 |
| (—) | constraint | — | — | inequality | 油网排布不超罩底：`N·BAFFLE_W + (N−1)·gap ≤ (CANOPY_W·canopy_width_scale) − 2·margin`；违反时缩 BAFFLE_W / spacing 或拒绝重采 | 接口 / clearance |
| (—) | constraint | — | — | inequality | 烟囱保留插入余量：闭合 sleeve 与 duct（或上级 sleeve）Z 向 overlap ≥ min_overlap（single/t_box 0.30、dual/curved_glass 0.25/0.02）；`chimney_travel_scale` 超出则回缩 | 接口 / clearance |
| (—) | constraint | — | — | inequality | fan 落凹腔且在油网后：`FAN_R·fan_radius_scale ≤ cavity_half − margin` 且 `expect_gap(fan, filter)` ∈[gap_min, 0.06]；curved_glass slim body 上限更紧 | 接口 / clearance |
| (—) | constraint | — | — | conditional | control 安装面随 canopy_form：t_box/curved_glass = 垂直前面 (0,−1,0)；pyramid = 斜面内法向 (0,−FRONT_NY,−FRONT_NZ) + rpy=FACE_TILT_* + Y/Z 用 `_front_y_at_z`；resolve_config 内按 canopy_form 解析 control origin/axis/rpy | pyramid L51-59, L246-277, L355-364 |

palette_style 候选（每 seed 采一套，**不计入 slot_choice**，跨 5★ 样本观察的真实材质 / 色集）：
| palette_style | canopy/shell | duct/sleeve | filter | glass visor | 来源样本 |
|---|---|---|---|---|---|
| brushed_stainless（默认）| 拉丝不锈钢 (0.74,0.75,0.77) | 钢 (0.70,0.71,0.73) | 深灰网 (0.20,0.21,0.23) | — | parent / pyramid / 多数变体 |
| glossy_black | 亮黑罩 (0.10,0.10,0.11) | 黑钢 | 黑网 | — | 不锈钢族暗化外推 |
| black_glass | 黑钢 body (0.18,0.18,0.20) | 钢 | 深灰网 | 钢化黑玻 (0.10,0.13,0.15) | curved_glass `tempered_glass` L217 |
| white_steel | 白烤漆罩 (0.92,0.92,0.93) | 钢 | 银网 (0.80,0.81,0.83) | — | dual_baffle `baffle_stainless` L233 外推 |
| inox_glass | 拉丝钢 body | 钢 | 银网 | 浅蓝灰玻 | curved_glass + 不锈钢混 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / 行程 / 角度 / clearance，**绝不改变 canopy_form / chimney / filter / control / N 的拓扑**。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（并列 baffle 油网数）：

- **count_param**：`filter_count`（模板内变量 N / FILTER_COUNT；罩底凹腔内并列 baffle 滤网数）。
- **N_range**：声明产品域 **[1, 4]**（真实抽油烟机常见 1–4 块并列百叶滤网；source map §Multiplicity 建议 [1,4]，采纳）。`config_from_seed` 的 sweep 采样域 **[1, 4]**（偏小加权：N=1 高频、N=2 常见、N=3/4 长尾）。N=1 即 fixed_mesh / hinged 的退化情形（单油网，不进 baffle 循环）。
- **sampling domain**：`config_from_seed` 用 `rng.choices((1,2,3,4), weights=偏小)`；`resolve_config` 把任意外部 config 的 N clamp 到 [1,4]。**N 仅在 filter=dual_baffle 时可>1**（见 joint policy / §9）。
- **copied object**：单块 baffle 滤网单元——`filter_{i}` part + `baffle_panel_{i}` visual（`_baffle_panel_cq` 共享 helper 发射：框 + 平行百叶条 + bottom plate + cross-bar）；canopy 侧每块配 2 条 `filter_rail_{fi}_{ri}` 支撑轨 + 块间 `filter_divider`。
- **naming**：`filter_{i}` part / `baffle_panel_{i}` visual / `canopy_to_filter_{i}` joint / `filter_rail_{fi}_{ri}` rails（dual_baffle L313-331 已用 `for i in range(2)` + `for fi in range(2)`，可直接作 copy-logic 源，N=2 推广到 N）。
- **placement**：沿 X **绝对式**等距并排——以罩底中心对称分布。N=2 源用 `sign*BAFFLE_X_OFFSET`（dual_baffle L55, L267, L315-316）；模板推广为 `x = (i − (N−1)/2)·BAFFLE_PITCH`（绝对式，每个 i 的 x 由 N 与中心解析，不累加漂移）→ N-不变前提。
- **joint policy**：baffle 油网是**非移动复制件**（FIXED）→ `canopy_to_filter_{i}` FIXED，**复制件本身不活动**；小类活动关节由共享 `blower_fan` CONTINUOUS spin + chimney PRISMATIC（+ 可选 control）提供（符合 §3：≥1 非 fixed joint 由 fan 保证）。
- **source/gating**：copy-logic 源取 dual_baffle L313-331（N=2）的 `for i in range(N)` 循环 + L265-274 的 rail 循环；**N=1 取 fixed_mesh 的单 inline `filter_mesh_panel` 或 hinged 的单 `grease_filter`**（未循环化，等价 range(1)）。**N>1 仅当 filter=dual_baffle**（fixed_mesh 单 inline 网 / hinged 单铰网无并列复制语义，强制 N=1，见 §9 兼容矩阵）。

## 拓扑多样性审计

总组合数：canopy_form(3) × chimney(2) × filter(3) × control(3) × filter_count 采样数（dual_baffle 时 {1,2,3,4}=4；fixed_mesh/hinged 恒 N=1）。

- 不计 N：3×2×3×3 = **54**（source map §组合数预审已确认 54 ≥ 10）。
- 计 N：filter 三候选中只有 dual_baffle 暴露 N>1，其余两候选恒 N=1 → filter×N 的拓扑等价类 = {fixed_mesh·n1, hinged·n1, dual_baffle·n1, dual_baffle·n2, dual_baffle·n3, dual_baffle·n4} = **6** → 总 canopy_form(3) × chimney(2) × 6 × control(3) = **108**。

仅 chimney(2) × filter(3) × control(3) = **18**（含 PRISMATIC / PRISMATIC-链 × 无joint / REVOLUTE / FIXED复制 × PRISMATIC / REVOLUTE / PRISMATIC 的 joint 拓扑组合）≥ 门控；叠 canopy_form(3) → 54、叠 N → 108，充裕。

理由：chimney × filter × control 提供真正的 joint 拓扑差异（chimney: 1 PRISMATIC vs 2 PRISMATIC 链；filter: 无 joint vs +REVOLUTE vs +N×FIXED；control: +PRISMATIC vs +REVOLUTE vs +PRISMATIC + part 树差异）= 单独 18 distinct joint-topology 类，叠 canopy_form(3) 与 filter_count(N) 后总 108 distinct。**N 必须编入 `slot_choices_for_seed` 的 tuple**（`("filter_count", f"n{N}")`，对齐 cushion/shopping_bucket/fence_cascade），否则单网与多网在 slot_choice 上无法区分，损失一整根拓扑维度。**`blower_fan` CONTINUOUS 是常驻 joint，不编 slot_choice（每候选都有，无区分力）。**

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 四个 named slot（canopy_form / chimney / filter / control），经兼容矩阵合法化（pyramid×control 解析斜面安装、curved_glass×dual_telescope 复核插入余量、N>1 仅 dual_baffle），再 `rng.choices` 加权 filter_count∈[1,4]（仅 dual_baffle 生效），再 uniform 各连续 scale + 采 palette_style。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（重点看 fan 旋转 + 烟囱升降 + hinged 翻网 + pyramid 斜面控制 + curved_glass visor）。


Controlled local parameterization：见 §参数表的 canopy_width/depth/height_scale + chimney_travel_scale（independent）+ fan_radius_scale（conditional@canopy_form）/ hinge_open_angle_scale（@hinged）/ knob_open_angle_scale（@rotary_knob）/ slider_travel_scale（@slider）/ button_travel_scale（@push_button）/ baffle_spacing_scale（@dual_baffle&N≥2）（conditional）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot + N（解析 conditional 范围：fan_radius 随 canopy_form、hinge/knob/slider/button 随 control、baffle_spacing 仅 dual_baffle&N≥2；control origin/axis/rpy 随 canopy_form 解析斜面 vs 垂直）→ 采 independent canopy width/depth/height + chimney_travel scale → 派生（fascia front Y 随 depth、HINGE/HOUSING Z 随 height、sleeve_len 随 travel）→ 用三条 clearance inequality（油网不超罩底、烟囱插入余量、fan 落腔且在网后）投影 / 回缩。跨部件依赖（油网排布 vs 罩宽、travel vs 插入、fan vs 凹腔）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 fan/sleeve/hinge/knob/slider joint origin、captured 接口、N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 四 named slot（经兼容矩阵），再 `rng.choices` 加权 N∈[1,4]（仅 dual_baffle），再解析 conditional scale + control 安装面，再 uniform independent scale，采 palette_style | slot_choices_for_seed 含 `("canopy_form",m)`/`("chimney",m)`/`("filter",m)`/`("control",m)`/`("filter_count",f"n{N}")` 且与 build 一致 |
| compatibility matrix | (1) **N>1 仅 filter=dual_baffle**：fixed_mesh（单 inline 网）/ hinged（单铰网）无并列复制语义 → N>1 时强制 filter=dual_baffle，否则 clamp N=1。 (2) **pyramid × control**：pyramid fascia 是斜面 → control（push_button/rotary_knob/slider）的 origin / axis / rpy 必须重算到斜面（push_button 用 (0,−FRONT_NY,−FRONT_NZ)；knob/slider 用 `_front_y_at_z` 定 Y + FACE_TILT rpy）；t_box/curved_glass 用垂直前面。这是 A×D 真实接口耦合，在 resolve_config 内按 canopy_form 解析。 (3) **curved_glass × dual_telescope**：curved_glass slim body（深 0.20）+ duct top 较低 + fan R 缩到 0.050 → dual_telescope 第二级插入余量紧（代码 min_overlap 已降 0.25/0.02）→ resolve 内对 chimney_travel_scale 收紧上限 + 复核 `expect_overlap` z；必要时降级 single_telescope。 (4) **fan_radius vs canopy_form**：curved_glass fan 基线 0.050（slim body），t_box/pyramid 0.085；fan_radius_scale clamp 后须落凹腔且在油网后（`expect_gap`）。 (5) canopy_form 与 chimney/filter 正交（除上述耦合外，任意组合合法）。 | 无 floating / collision / fan 撞壳 / 烟囱脱出 / 油网超罩 / pyramid 控制飞离斜面 / curved_glass 烟囱插入不足 |
| controlled local variation | 4 independent + 6 conditional clamped scale，每 build 统一；conditional 随 canopy_form/control/filter/N 解析 | 比例变化不破坏 fan/sleeve/hinge/knob/slider origin、captured 接口、油网覆盖、烟囱插入、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 slot 机构 QC（fan 旋转 / 烟囱升降 / hinged 翻网 / 旋钮转 / 滑块滑 / pyramid 斜面控制 / curved_glass visor）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| canopy_form | 3 | yes | yes | t_box / pyramid / curved_glass（mesh 足迹 + fascia 法向；pyramid 改 control 安装轴）|
| chimney | 2 | yes | no | single_telescope / dual_telescope（1 PRISMATIC vs 2 PRISMATIC 链；降级理由见下注）|
| filter | 3 | yes | yes | fixed_mesh（无 joint）/ hinged（REVOLUTE）/ dual_baffle（N×FIXED multiplicity）|
| control | 3 | yes | yes | push_button（PRISMATIC）/ rotary_knob（REVOLUTE）/ slider（PRISMATIC）|
| filter_count (N) | 4（采样域 {1,2,3,4}，1 高频 / 3-4 长尾）| yes | yes | 拓扑维度，编入 slot_choice；仅 dual_baffle 时 N>1 |

> 降级理由（Slot B chimney 仅 2 candidate）：fork 池烟囱形态只有 parent 的单级伸缩 + dual 变体的双级伸缩两个真实收敛形态；真实壁挂烟罩烟囱词汇表本身窄（单 / 双级伸缩为主，少数固定无伸缩或纯装饰罩）。审核如需扩容应回 fork 池补造（如三级伸缩、固定 box chimney、无烟囱 recirculating 罩），不在模板侧虚构。canopy_form(3) × filter(3+N) × control(3) 已提供主拓扑多样性，Slot B ×2 充裕。

## Validator
- `slot_choices_for_seed` 返回已实现的 module 名，含 `("canopy_form",m)`/`("chimney",m)`/`("filter",m)`/`("control",m)`/`("filter_count",f"n{N}")`；`blower_fan` CONTINUOUS 不编 slot_choice（常驻）
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊），N 采样域 ⊆ [1,4]
- `resolve_config` 把 filter_count clamp 到 [1,4]（N>1 强制 dual_baffle，否则 N=1），各 scale clamp 到声明范围；conditional scale 随 canopy_form/control/filter/N 解析；control origin/axis/rpy 随 canopy_form 解析（pyramid 斜面）；三条 clearance inequality（油网不超罩、烟囱插入余量、fan 落腔在网后）在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（N>1 仅 dual_baffle；pyramid 控制安装到斜面；curved_glass×dual_telescope 插入余量复核 / 降级）
- 连续 scale clamp 后不破坏 fan/sleeve/hinge/knob/slider joint origin / captured 接口 / 油网覆盖 / 烟囱插入 / N 复制 / 类别身份
- 关键 joint：`canopy_to_blower_fan` CONTINUOUS axis≈(0,0,1)（abs(axis[2])>0.99、无 lower/upper，全候选共享）；chimney `canopy_to_chimney_sleeve`/`canopy_to_sleeve_0` PRISMATIC axis≈(0,0,1)（dual 含 `sleeve_0_to_sleeve_1` parent=sleeve_0）；filter=hinged `canopy_to_grease_filter` REVOLUTE axis≈(1,0,0) 0..π/2；filter=dual_baffle `canopy_to_filter_{i}` FIXED；control=push_button `canopy_to_power_button` PRISMATIC axis=fascia 内法向（t_box (0,−1,0) / pyramid (0,−FRONT_NY,−FRONT_NZ)）；control=rotary_knob `canopy_to_speed_knob` REVOLUTE axis≈(0,1,0) 0..270°；control=slider `canopy_to_slider_tab` PRISMATIC axis≈(1,0,0)
- captured 接口：element-scoped `allow_overlap`（`fan_shaft`↔`motor_housing`；`guide_pad_{i}`/`guide_pad_{i}_{j}`↔`lower_duct`/`sleeve_shell_0`；`hinge_knuckle_{i}`↔`canopy_shell`；`button_cap`/`knob_body`/`slider_stem`↔`canopy_shell`；dual 的 `sleeve_shell_0`↔`sleeve_shell_1`），照搬各样本 run_tests 的 allow_overlap 段
- copied object 遵循 `filter_{i}`/`baffle_panel_{i}`/`canopy_to_filter_{i}`/`filter_rail_{fi}_{ri}` 命名 + 绝对式沿 X 等距 placement + FIXED 复制件（非移动）
- grandfather：所有 captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases
- 把 N 当普通 int 参数、不进 slot_choice → 单网与多网 slot_choice 同形，损失拓扑维度（违反 §8/§9 硬要求）。
- N>1 时仍用 fixed_mesh / hinged（单网无并列复制语义）→ 必须 gate（N>1 强制 dual_baffle，否则 clamp N=1）。
- pyramid canopy_form 配 control 时仍用垂直前面 (0,−1,0) 安装轴 / 不重算 origin → 控制件飞离斜面 fascia（pyramid run_tests 显式断言 button axis = `(0,−FRONT_NY,−FRONT_NZ)`，L604-608）。
- curved_glass × dual_telescope 不复核插入余量（slim body + 低 duct top）→ 第二级 sleeve 脱出 / `expect_overlap` z FAIL；须收紧 chimney_travel 或降级 single。
- 把 `blower_fan` 设成 REVOLUTE / 有限角或漏掉 → 违反共享主运动（每候选必有 CONTINUOUS spin，是 ≥1 非 fixed joint 的保证）。
- 把油网当独立活动 part 加 joint（dual_baffle 例外是 FIXED）→ fixed_mesh 应 inline（Rule 1）、dual_baffle 应 FIXED 复制；只有 hinged 才有 REVOLUTE。
- 烟囱 / 控制 / 油网 rest pose 设成展开 / 翻起 / 压入而非 q=0 闭合 → current-pose 与 viewer 目检不符（所有样本 q=0 闭合：sleeve 顶 ~1.10、hinged 平贴、button 凸出、slider low、knob 0°）。
- joint origin 放在凹腔中心或任意点而非真实硬件面（duct / 前缘铰线 / fascia / rail）→ `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- baffle 间距过大致油网超出罩底 → §7 第一条不等式 FAIL；须按比例缩 BAFFLE_W / spacing。
- 给 captured-fit / captured-slide 接口补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质（palette_style / canopy scale）当新 candidate 塞进 slot → 不是结构差异。
- 把空调 / 净化器 / 排气扇语义混入（摆叶出风 / 落地圆柱 / 窗格栅）→ 出类，本类是壁挂烟罩 + 烟囱 + 油网 + 抽风 fan。

## 与相邻类别的边界
- 不该混入：**空调 / 分体壁挂空调（air_conditioner，已有独立 slug）**——主体是出风口 + 摆叶 swing，无烟囱 / 油网 / 罩下集风腔；source map parent 同目录有一条 mini-split AC 样本（不属本类）。本类身份 = 罩 + 烟囱 + 油网 + 鼓风机抽风。
- 不该混入：**空气净化器 / 排气扇 / 通风口（vent，已有独立 slug）**——净化器落地 / 桌面圆柱，排气扇墙 / 窗格栅风叶；本类是灶台上方壁挂集烟罩，主运动是抽风 fan + 升降烟囱。
- 不该混入：**内置烤箱 / 嵌入式集成灶（built_in_oven，已有独立 slug）**——嵌橱柜箱体 + 门 + 拉篮；本类是壁挂悬空罩。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) canopy_form 建模为 mesh-helper + fascia-法向维度（t_box/pyramid 不改拓扑、curved_glass 多 glass_visor inline），其与 chimney/filter/control 的笛卡尔积撑开多样性是否接受；(2) filter_count N_range 取 [1,4]（采纳 source map 建议，N=3/4 无样本由模板侧放大，copy-logic 源仅 N=2）是否接受还是收窄到 [1,2]；(3) N>1 仅 dual_baffle 的 gate 策略；(4) **A×D 耦合**：pyramid 斜面 fascia 时 control 安装轴 / origin / rpy 重算（push_button 已有源 L355-364，knob/slider 需 resolve 内类比 `_front_y_at_z`+FACE_TILT 重算）是否接受；(5) **curved_glass × dual_telescope** 插入余量复核 / 降级 single 策略；(6) chimney 仅 2 candidate（降级理由见 Slot B 注）是否接受还是回 fork 池补造；(7) Topology target 108<300 的说明是否接受；(8) blower_fan CONTINUOUS 作常驻共享 joint 不编 slot_choice 是否符合 multiplicity / topology 审计期望。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）
- 共享 helper：`_canopy_shell`/`_pyramid_shell`/`_metal_body_shell`+`_glass_visor_geometry`（canopy mesh，按 canopy_form 切换）、`_rect_tube`（duct + sleeve，所有样本通用）、`_build_sleeve_stage`（dual_telescope 的 `for i in range(2)` 串链发射，single 用 N=1 退化）、`_baffle_panel_cq`（dual_baffle 油网，N 复制复用同一几何）、KnobGeometry（rotary_knob）、SlotPatternPanelGeometry（fixed_mesh/hinged 网）。
- captured 接口 allow_overlap：`run_hood_tests` 里逐 module 补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（parent L344-365、pyramid L382-403、curved_glass L415-443、dual L411-450、hinged L375-405、dual_baffle L436-457、rotary_knob L368-389、slider L365-386）。
- conditional 范围 / 安装面解析顺序：先采 canopy_form / chimney / filter / control / N → 解析 control origin/axis/rpy（随 canopy_form：t_box/curved_glass 垂直前面、pyramid 斜面 `_front_y_at_z`+FACE_TILT）/ fan_radius 基线（随 canopy_form：curved_glass 0.050）/ hinge/knob/slider/button scale（随 control）/ baffle_spacing（仅 dual_baffle&N≥2）→ 采 independent canopy width/depth/height + chimney_travel → 派生（fascia front Y 随 depth、HINGE/HOUSING Z 随 height、sleeve_len 随 travel）→ 投影三条 clearance inequality（油网不超罩、烟囱插入、fan 落腔在网后；curved_glass×dual 收紧 travel 上限）。
- N=1 退化：filter=fixed_mesh 用 inline `filter_mesh_panel`（不进循环）、filter=hinged 用单 `grease_filter`（REVOLUTE）；filter=dual_baffle 走 `for i in range(N)` 的 `filter_{i}`（N≥1，N=1 即单 baffle）。
- pyramid A×D 实现：power_button 源已把轴改斜面法向（pyramid L355-364），knob/slider 需在 resolve_config 内类比——用 `_front_y_at_z(KNOB_Z/SLIDER_Z)` 定 Y、rpy 用 `FACE_TILT_FROM_*`、joint axis 投影到斜面（knob 轴仍约 Y 但 origin 落斜面，slider 轴沿 X 不变但 Y/Z 落斜面）。这是 A×D 接口耦合的关键实现点。
- 参考模板：选运动拓扑相近的——root chassis + parallel children + 可选 REVOLUTE/PRISMATIC child + multiplicity count：`agent/templates/Accessories_Cushion.py`（mixed: 固定 named slots + `("pan_count",f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 mesh 复用 + 兼容矩阵 gating + captured allow_overlap）与 `shopping_bucket.py`（telescoping PRISMATIC + count multiplicity）最同构；hood 的 canopy→fan CONTINUOUS + chimney PRISMATIC(链) + filter(可选 REVOLUTE / N×FIXED) + control(PRISMATIC/REVOLUTE) 与之同构。hood 尺度中等（canopy ~0.90×0.50m、closed 顶 ~1.10m、fan R ~0.085m / curved_glass 0.050m），joint origin 须精确落真实硬件面（≤0.015m baseline）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D + shared fan（parent 基线）| t_box + single_telescope + fixed_mesh + push_button + blower_fan | rec_model-a-wall-mounted-t-style-box-linear-kitchen-_...e562777f | `_canopy_shell` L100-146 / `_rect_tube` L149-158 / `canopy` 装配 L176-240 / `chimney_sleeve`+PRISMATIC L243-276 / `blower_fan`+CONTINUOUS L278-308 / `power_button`+PRISMATIC L311-326 / allow_overlap L344-365 | 全基线坐标约定 + box canopy + 单级伸缩 + inline 网 + 压键 + 共享 fan CONTINUOUS 范式 + captured allow_overlap |
| S2 | A | pyramid canopy_form | rec_hood_var_form_pyramid | `_pyramid_shell` L124-172 / 斜面法向数学 `FACE_TILT_*`/`FRONT_NY/NZ`/`_front_y_at_z` L51-64 / 斜面 control 安装 L246-277, L350-364 / button axis 斜面法向断言 L604-608 | 截顶金字塔 canopy mesh + A×D 斜面安装耦合源 |
| S3 | A | curved_glass canopy_form | rec_hood_var_form_curved_glass | `_metal_body_shell` L123-155 / `_glass_visor_geometry`（section_loft）L170-208 / slim body + 缩 fan R 0.050 L102-119 / min_overlap 0.25/0.02 L515-550 | slim body + 凹面玻璃 visor mesh + curved_glass×dual 插入余量复核源 |
| S4 | B | dual_telescope | rec_hood_var_chimney_telescope_dual | `_build_sleeve_stage` L164-219 / `for i in range(2)` 串链 L303-342 / 双级 PRISMATIC linear_chain + 全展 2×travel 断言 L588-613 / 双组 pad + concentric allow_overlap L426-450 | 双级伸缩烟囱（PRISMATIC linear_chain，stage 循环发射）|
| S5 | C | hinged filter | rec_hood_var_filter_hinged | `grease_filter` part + `hinge_knuckle_{i}`×3 L327-344 / `canopy_to_grease_filter` REVOLUTE axis=(1,0,0) 0..π/2 L347-355 / 翻下断言 L549-592 / allow_overlap L398-405 | 翻下清洗油网（前缘 X 轴 REVOLUTE）|
| S6 | C（multiplicity）| dual_baffle filter（filter_count）| rec_hood_var_filter_dual_baffle | `_baffle_panel_cq` L176-224 / `for i in range(2)` `filter_{i}`/`baffle_panel_{i}` + FIXED L313-331 / `filter_rail_{fi}_{ri}` + `filter_divider` L256-274 / side-by-side + rail contact 断言 L594-656 | 并列 baffle 油网 copy-logic 源（filter_count multiplicity，FIXED 复制 + rail 支撑）|
| S7 | D | rotary_knob control | rec_hood_var_control_rotary_knob | `speed_knob`（KnobGeometry+Skirt/Grip/Indicator）L320-337 / `canopy_to_speed_knob` REVOLUTE axis=(0,1,0) 0..270° L338-350 / `knob_escutcheon` 铒环 L227-235 / 旋转不漂移断言 L552-577 | 旋钮控制（绕 Y REVOLUTE + escutcheon）|
| S8 | D | slider control | rec_hood_var_control_slider | `slider_tab`（`slider_cap`+`slider_stem`）L324-338 / `canopy_to_slider_tab` PRISMATIC axis=(1,0,0) 0..0.060 L339-347 / `slider_track`+`slider_tick_{i}`×3 L226-239 / 滑 60mm 断言 L546-577 | 滑块控制（横向 PRISMATIC + track + ticks）|
