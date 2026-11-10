# toaster (pop-up bread toaster) — Modular Spec

> 来源小类：`picture/Kitchen/Toaster`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Kitchen__Toaster.md`。
> **"toaster" 在此 = 弹起式面包机（pop-up bread toaster），不是烤箱式多功能炉（toaster oven）、不是面包机（bread maker）、不是电烤盘 / 帕尼尼机（grill / panini press）。**
> 结构家族 = 一个融合的中空 `body` 碳壳（root，`shell` CadQuery 中空箱 + 内腔 cavity + 每槽顶部开口 + 凹陷 `slot_rim_plate` 镜板 + 前壁 lever 槽 / button 孔 / control 孔）+ 一只 `control_panel` brushed-silver 前面板 visual（+X 端面）+ 四个 `foot_{i}` 脚 + `dial_mark_{i+1}` / `brand_strip` 装饰。**定义运动 = `carriage_lever` PRISMATIC（轴 (0,0,-1)，0.070 m 向下，所有 bread 货架骑同一 carriage）+ browning 控制 REVOLUTE（旋钮）/ PRISMATIC（滑块 / 数字按钮）。**
> 坐标约定全 source 一致：+Z up，body 长轴沿 X，brushed-silver 控制面板在 +X 前端面；正视面板（沿 -X 看）时 +Y 是观者右、-Y 是观者左。
>
> **同步状态**：本 spec 引用的 8 个 5 星样本（1 个 parent + 7 个 fork 槽位 / multiplicity 变体）已同步进本仓库 `articraft_data/data/records/`，rating=5（按上游 curation）。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（逐一核对、全文读完）。引用以 part / joint / helper **名字** 为准（`body`/`shell`/`slot_rim_plate`/`control_panel`/`foot_{i}`、`carriage_lever`/`lever_knob`/`lever_stem`/`carriage_crossbar`/`bread_shelf_{i}`/`body_to_carriage_lever`、`browning_dial`/`dial_cap`/`dial_shaft`/`dial_pointer_nub`/`body_to_browning_dial`、`browning_slider`/`slider_tab`/`slider_stem`/`body_to_browning_slider`、`browning_button_{i}`/`browning_pad_{i}`/`body_to_browning_button_{i}`、`crumb_tray`/`tray_body`/`body_to_crumb_tray`、`lever_guide_plate`、`side_rail_{side_tag}`、`cancel_button`/`frozen_button`/`bagel_button` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `toaster` |
| template path | `agent/templates/Kitchen_Toaster.py` |
| test path (optional) | `tests/agent/test_toaster_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `multiplicity`（主可变 count 轴 = `slot_count` 面包槽 / 货架数 N 复制；外加固定 named slots: browning_control + lever_placement + crumb_tray + body_silhouette 各自挂到共同 root `body`，effectively mixed，但唯一模板级可变 count 轴是 slot_count → 归 `multiplicity`）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 parent + 7 fork 变体：2 browning_control 槽位 + 1 lever_placement 槽位 + 1 crumb_tray 槽位 + 1 body_silhouette 槽位 + 2 slot_count N 样本；均 converged，compile success、含 PRISMATIC carriage + 其槽机构非 fixed joint、workbench-only）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、run_tests 的 allow_overlap / check 段）|
| read_scope | all 5-star samples in this category（parent 母资产 001.png 覆盖 slot_count=2 × rotary_dial × front_lever × no-tray × square_box 基线；变体为 fork 子，各单轴变化）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 8/8 全部被采纳，无未采用样本（同名但不同小类的 `rec_toaster_oven_*` 是 toaster oven 类，与本类无关，已忽略）|

阅读要点（用于槽位分解，**关键拓扑发现**）：
- **8 个样本共享同一拓扑骨架**：root `body`（`shell` 中空 CadQuery 壳 + `slot_rim_plate` 凹镜板 + `control_panel` brushed-silver 前面板 + 4 个 `foot_{i}` + `dial_mark_{i+1}` / `brand_strip` 装饰，**全部 inline `body.visual(...)`，无 FIXED-joint 装饰 part**）+ `carriage_lever` PRISMATIC（轴 (0,0,-1)，0.070 m 向下，`bread_shelf_*` 货架透过顶槽可见）+ browning 控制机构 + 3 个功能按钮（cancel/frozen/bagel）PRISMATIC。`carriage_lever` PRISMATIC 在全 8 源中**完全一致**（`body_to_carriage_lever` 轴 (0,0,-1) `MotionLimits(effort=15, velocity=0.3, lower=0, upper=0.070)`）—— 这是身份的定义运动。
- **slot_count（multiplicity 主轴，3 个 N 样本逐一核对）**：所有 bread 货架骑**同一** carriage_lever（单 PRISMATIC joint），slot_count 改变的是顶槽开口 cut 数 + `bread_shelf_*` visual 数 + body 长，**不改 joint 数**（这是**视觉 / cut multiplicity**，非 per-N joint multiplicity）。
  - **N=2**（parent `…_d8fcb465`）：顶槽 cut 经 `for yc in (SLOT_YC, -SLOT_YC)`（shell L139-149），货架经 `for tag, yc in (("right", SLOT_YC), ("left", -SLOT_YC))`（carriage L316-322）→ `bread_shelf_right` / `bread_shelf_left`。
  - **N=4**（`rec_toaster_var_slot_4slice`）：`NUM_SLOTS=4`（L48），`SLOT_POSITIONS` 由嵌套 loop `SLOT_PAIR_XC × (±SLOT_YC)` 建（L73-76）；shell cut（L153-165）、rim cut（L202-214）、货架（L353-361）全经 `for i in range(NUM_SLOTS)` → `bread_shelf_{i}`；body 长 `BODY_L=0.396`（L50），加 X-spanning `side_rail_{side_tag}` 脊（L336-352）。
  - **N=1**（`rec_toaster_var_slot_long_single`）：单宽 baguette 长槽（L139-148 单语句），单 `bread_shelf`（无循环，L316-321），腔窄 `CAV_Y=0.040`（L58）。
- **Slot A browning_control**（挂 +X `control_panel`）：
  - **rotary_dial**（parent 基线）：`browning_dial` part（`dial_cap` KnobGeometry + `dial_shaft` + 离轴 `dial_pointer_nub`），`body_to_browning_dial` REVOLUTE axis (1,0,0) ~270°（parent L334-373）；面板 `dial_mark_{i+1}` 刻度 `for i, ang_deg in enumerate((235,180,125,70))`（parent L272-287）。
  - **slider**（`rec_toaster_var_browning_slider`）：`browning_slider` part（`slider_tab` + `slider_stem` + `slider_carriage_plate`），`body_to_browning_slider` PRISMATIC axis (0,0,1) travel 0.044（L359-391）；面板 / 壁竖 `track_slot` cut（shell L176-186 / panel L231-241）；`slider_mark_{i+1}` 刻度 `for i in range(4)`（L304-312）。
  - **digital**（`rec_toaster_var_browning_digital`）：`browning_button_{i}` parts（i∈{0,1}=UP/DOWN）含 `browning_pad_{i}` / `browning_stem_{i}` / `browning_indicator_{i}`，`body_to_browning_button_{i}` PRISMATIC axis (-1,0,0) travel 0.003（L350-388）；inline `digital_display` + `display_bezel` 面板 visual（L290-303）；loop `for i in range(2)`。
- **Slot B lever_placement**（定义运动 carriage PRISMATIC 的挂面）：
  - **front_lever**（parent 基线）：`carriage_lever`（`lever_knob` + `lever_stem` + `carriage_crossbar` + `bread_shelf_*`），`body_to_carriage_lever` PRISMATIC axis (0,0,-1)，lever 槽 cut 在前 `control_panel` + 前壁，knob 坐 `control_panel`（parent L296-332，前壁槽 shell L162-171 / panel L208-217）。
  - **side_lever**（`rec_toaster_var_lever_side`）：同 `carriage_lever` / `body_to_carriage_lever` PRISMATIC axis (0,0,-1) 不变，但槽 + knob 移到 +Y 侧壁；新 `lever_guide_plate` body visual（L296-301）+ `_side_guide_shape()` helper（L224-256）；knob 坐 `lever_guide_plate`；侧壁竖槽 cut（shell L169-179）；carriage L336-379。
- **Slot C crumb_tray**（挂壳底 pocket）：
  - **none**（parent 基线）：无 tray part，壳底密封。
  - **pullout**（`rec_toaster_var_crumb_tray_pullout`）：`crumb_tray` part / `tray_body` visual（`_crumb_tray_shape()` L260-300：base plate + 3 侧唇 + pull-handle tab），`body_to_crumb_tray` PRISMATIC axis (+1,0,0) travel 0.180（L446-471）；壳底 `tray_pocket` cut 必须贯穿外壳 X 端面，不能是被外壁封住的盲槽（shell L194-204）；extended 仍保留插入（run_tests L745-754）。
- **Slot D body_silhouette**（`shell` primitive 家族）：
  - **square_box**（parent 基线）：`_shell_shape()` = `cq.Workplane.box(...)` + 竖 / 顶 / 底圆角 fillet（parent L127-177）；`body_gray` matte 材质。
  - **retro_round**（`rec_toaster_var_body_retro_round`）：`_shell_shape()` = 3-section `slot2D`（base→barrel→dome）`.loft()`（L138-211，loft 截面 const L61-66）；`chrome_body` polished 材质；cavity / slots / recess / holes 从 loft 实体 boolean-cut；面板 / 腔 / recess Z 为 dome taper 下调（PANEL_Z1=0.152、CAV_Z1=0.160、RECESS_Z0=0.175）。
- **palette**：parent 同色族（`body_gray=(0.40,0.40,0.41)` 壳 / `brushed_silver=(0.78,0.79,0.81)` 面板 / `dark_plastic=(0.11,0.11,0.12)` 脚 & 旋钮轴 / `knob_gray` lever knob / `dial_dark_gray=(0.24,0.25,0.26)` 旋钮 / `button_silver=(0.72,0.73,0.75)` 按钮 / `rim_gray=(0.63,0.64,0.65)` 镜板 / `carriage_metal=(0.56,0.57,0.59)` 货架）；retro_round 用 `chrome_body=(0.78,0.80,0.85)`；slider 用 `slider_dark`；digital 用 `display_bg`。→ 4-6 套 colorway（见 §7 palette_style）。

## 核心身份

一台**弹起式面包机（pop-up bread toaster）**：一个融合的中空 `body` 碳壳（root，matte-gray 圆角方箱 或 retro chrome lofted dome），顶部有 N 个面包槽开口围以凹陷的 `slot_rim_plate` 镜板，内有隐藏的 toasting cavity，槽内坐着骑在**单一共享 carriage** 上的 N 个面包货架（`bread_shelf_*`）。前端 +X 是 brushed-silver `control_panel` 面板，上有 browning 控制（旋钮 / 滑块 / 数字按钮）、push-down carriage lever（前面板或侧壁）、3 个功能按钮（cancel/frozen/bagel）。底部 4 个 `foot_{i}` 脚，可选壳底 pull-out crumb_tray。活动语义恒为：**carriage 沿 -Z PRISMATIC 向下压（0.070 m，定义运动，所有货架一起下移）+ browning 控制（旋钮 REVOLUTE ~270° / 滑块 PRISMATIC +Z / 数字按钮 PRISMATIC -X）+ 3 个功能按钮 PRISMATIC -X 压入（0.003 m）+ 可选 crumb_tray PRISMATIC +X 抽出（0.180 m）**。默认成熟域：browning_control × lever_placement × crumb_tray × body_silhouette × 面包槽数 N∈[2,4] 笛卡尔积的单台台面弹起式面包机（典型尺寸 ~0.28×0.16×0.19 m，N=4 时 X 延长至 ~0.396 m）。

不该混入：
- **烤箱式多功能炉 / 小烤箱（toaster oven）**——侧开 / 下翻玻璃门 + 内部托盘 / 烤架 + 旋钮温控的箱式炉腔，是**横向门 + 内腔**的炉子（同名 `rec_toaster_oven_*` 即此），主运动是炉门铰链而非顶部弹起 carriage；本类核心是**顶插面包槽 + 向下压的弹起 carriage**，缺这套即出类。
- **面包机（bread maker / bread machine）**——高桶身 + 顶盖 + 内桶 + 揉面叶片，是发酵 / 烘焙整条面包的高箱机器，无面包槽 / 无弹起 carriage。
- **三明治机 / 帕尼尼机 / 电烤盘（sandwich press / panini grill / griddle）**——上下夹合 REVOLUTE 蛤壳热板，主运动是上盖翻合而非顶插弹起；本类无夹合热板。
- **电水壶 / 咖啡机等其他台面厨电**——主运动 spine 不同（倾倒 / 滴滤），非面包槽弹起形态。

## 槽位 + 候选模块表

> **建模注记**：toaster 是 **root `body`（dispatch body_silhouette 主壳几何 `shell` + `slot_rim_plate` + `control_panel` + 4 脚 + 装饰）+ 单一 `carriage_lever`（PRISMATIC，定义运动，承载 N 个 bread 货架）+ browning 控制机构（Slot A）+ 3 个功能按钮（固定结构，非 slot）+ 可选 crumb_tray（Slot C）parallel children**。
> - **Slot A（browning_control）改 +X 面板上的 browning 控制 part 树 + joint 拓扑**：rotary_dial（1 REVOLUTE 旋钮）/ slider（1 PRISMATIC 竖滑块）/ digital（2 PRISMATIC UP/DOWN 按钮 + display visual）。
> - **Slot B（lever_placement）改定义运动 carriage 的挂面**（joint 类型 / 轴 / 行程**不变**，只移槽 + knob 所在面 + guide hardware）：front_lever（前 `control_panel` 槽）/ side_lever（+Y 侧壁槽 + `lever_guide_plate`）。
> - **Slot C（crumb_tray）改壳底 part 树**：none（密封壳底，单候选 → 折为 pull-out 的 disabled/absent 状态）/ pullout（壳底 `tray_pocket` + `crumb_tray` PRISMATIC +X 抽出）。
> - **Slot D（body_silhouette）改 root 主壳 primitive 家族**：square_box（`box` + fillet）/ retro_round（3-section `slot2D.loft()` dome barrel）。
> - **slot_count（N）是 multiplicity 主轴**：顶槽 cut + `bread_shelf_{i}` visual + body 长随 N 展开 [2,4]（N=1 long-single 为退化的 baguette 形态）；**所有货架骑同一 carriage（1 joint 不随 N 变）**。

### Slot A：browning_control（+X 面板上的褐变 / 焦度控制 —— 改 part 树 + joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / joint 特征 |
|---|---|---|---|---|
| rotary_dial（基线） | parent rec_…_d8fcb465 | `browning_dial` part L334-373（`dial_cap` KnobGeometry L335-351 + `dial_shaft` L352-357 + 离轴 `dial_pointer_nub` L358-364）/ `body_to_browning_dial` REVOLUTE L365-373 / 面板 `dial_mark_{i+1}` 刻度 L272-287 / 面板 / 壁 dial 孔 shell L176 + panel L222 | eligible if compatible | dark-gray 旋钮绕水平 +X 面板法线旋转 ~270°（`body_to_browning_dial` REVOLUTE axis=(1,0,0) `MotionLimits(effort=2, velocity=2, lower=0, upper=radians(270))`）；离轴 nub 扫动证明连续旋转；`dial_mark_{i+1}` 4 刻度（固定 N inline visual，Rule 1）|
| slider | rec_toaster_var_browning_slider | `browning_slider` part L359-391（`slider_tab` `_slider_tab_shape` L251-260 + `slider_stem` L369-374 + `slider_carriage_plate` L376-381）/ `body_to_browning_slider` PRISMATIC L383-391 / 竖 `track_slot` cut shell L176-186 + panel L231-241 / `slider_mark_{i+1}` `for i in range(4)` L304-312 | eligible if compatible | dark tab 在竖轨上滑（上=高焦度）：`body_to_browning_slider` PRISMATIC axis=(0,0,1) `MotionLimits(effort=4, velocity=0.2, lower=0, upper=0.044)`；stem 穿 track 槽 + 内 carriage plate；`slider_mark_{i+1}` 4 刻度（固定 N inline，Rule 1）|
| digital | rec_toaster_var_browning_digital | `browning_button_{i}` parts（i∈{0,1}）L350-388（`browning_pad_{i}` `_rounded_pad` L130-139 + `browning_stem_{i}` L364-369 + `browning_indicator_{i}` L370-377）/ `body_to_browning_button_{i}` PRISMATIC L378-388 / inline `digital_display` + `display_bezel` L290-303 / 壁 digi 孔 shell L190-192 + panel L237-239 | eligible if compatible | dark LCD inset + UP/DOWN push pad（**2 个 PRISMATIC** 按钮，`for i in range(2)`）替代模拟控制：`body_to_browning_button_{i}` PRISMATIC axis=(-1,0,0) travel 0.003；`digital_display`/`display_bezel` 为 inline body visual（Rule 1）|

### Slot B：lever_placement（push-down carriage lever 挂面 —— **定义运动槽**，joint 不变只移面）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / joint 特征 |
|---|---|---|---|---|
| front_lever（基线） | parent rec_…_d8fcb465 | `carriage_lever` part L296-332（`lever_knob` `_lever_knob_shape` L226-229 + `lever_stem` L304-309 + `carriage_crossbar` L310-315 + `bread_shelf_*` L316-322）/ `body_to_carriage_lever` PRISMATIC L324-332 / 前壁 lever 槽 cut shell L162-171 + panel L208-217 | eligible if compatible | push-down knob 骑前面板槽；`body_to_carriage_lever` PRISMATIC axis=(0,0,-1) origin=(0.132, LEVER_YC, 0.150) `MotionLimits(effort=15, velocity=0.3, lower=0, upper=0.070)`；knob 坐 `control_panel`（`expect_contact` lever_knob↔control_panel）|
| side_lever | rec_toaster_var_lever_side | 同 `carriage_lever` / `body_to_carriage_lever` PRISMATIC axis=(0,0,-1) 不变 L370-379 / 但 +Y 侧壁竖槽 cut shell L169-179 / 新 `lever_guide_plate` body visual L296-301 + `_side_guide_shape()` L224-256 / 侧式 knob `_lever_knob_shape` L259-263 / carriage L336-368 | eligible if compatible | lever 从前面移到 +Y 侧壁；面板失去 lever 槽（`_panel_shape` 不再 cut lever 槽 L208-221）；`carriage_crossbar` 沿 Y 跨接，joint origin=(LEVER_XC, BODY_W/2, 0.150)；knob 坐 `lever_guide_plate`（`expect_contact` lever_knob↔lever_guide_plate）；**joint 类型 / 轴 / 0.070 行程恒不变** |

> Slot B 是**定义运动槽**（carriage PRISMATIC）。只有挂面动（前面板槽 ↔ +Y 侧壁槽 + guide plate），joint 类型、轴 (0,0,-1)、0.070 m 行程在两候选间不变。

### Slot C：crumb_tray（壳底 crumb 托盘 —— 改壳底 part 树）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / joint 特征 |
|---|---|---|---|---|
| none（基线 / **disabled 状态**） | parent rec_…_d8fcb465 | （无 tray part；壳底无 `tray_pocket` cut，shell L127-177 无 pocket）| eligible if compatible | 基线——无可拆 tray，壳底密封；建模为 pullout module 的 **`tray_present=False` disabled 状态**（不发射 tray part / joint，壳底不开 pocket）|
| pullout | rec_toaster_var_crumb_tray_pullout | `crumb_tray` part / `tray_body` visual `_crumb_tray_shape()` L260-300（base plate + 3 侧唇 + pull-handle tab）/ `body_to_crumb_tray` PRISMATIC L463-471 / 壳底 `tray_pocket` cut shell L194-204 / extended 保留插入 run_tests L745-754 | eligible if compatible | flat crumb tray 从 +X 端壳底（cavity 下）滑出：`body_to_crumb_tray` PRISMATIC axis=(+1,0,0) `MotionLimits(effort=8, velocity=0.2, lower=0, upper=0.180)`；底部 pocket 必须挖穿到外壳端面形成真实开口，而不是外侧仍封口的盲槽；q=0 全插入、q=0.180 抽出但仍保留 ≥0.040 m 插入（box-in-pocket captured-slide，`allow_overlap` tray_body↔shell）|

> Slot C 是 1→2 候选轴（none vs pull-out）。本 spec 把 **`none` 折为 pull-out module 的 disabled/absent 状态**（布尔 feature flag `tray_present`）：`tray_present=True` 发射 `crumb_tray` part + PRISMATIC joint + 壳底 `tray_pocket` cut；`tray_present=False` 不发射任何 tray 几何且壳底不开 pocket。两状态都编入 `slot_choices_for_seed` 为 `("crumb_tray", "pullout")` / `("crumb_tray", "none")`，故 Slot C 在 slot_choice 维度上有 2 个 distinct 值（满足 ≥2 candidate 折叠要求，见 §9）。

### Slot D：body_silhouette（root 主壳 primitive 家族 —— 改 `shell` mesh helper）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / 结构特征 |
|---|---|---|---|---|
| square_box（基线） | parent rec_…_d8fcb465 | `_shell_shape()` L127-177 = `cq.Workplane.box(BODY_L,BODY_W,SHELL_H)` + 竖 `fillet(0.030)` / 顶 `fillet(0.016)` / 底 `fillet(0.005)` L132-134 + cavity/slots/recess/lever/button/dial cut | eligible if compatible | 经典现代圆角方箱；`body_gray` matte 材质；矩形足迹、内腔为 box cut |
| retro_round | rec_toaster_var_body_retro_round | `_shell_shape()` L138-211 = 3-section `slot2D`（base `slot2D(LOFT_BOTTOM_*)` → barrel `slot2D(LOFT_MIDDLE_*)` → dome `slot2D(LOFT_TOP_*)`，截面 const L61-66）`.loft()` L144-152 + cavity/slots/recess/lever/button/dial cut（lever 槽内延以容 dome taper L192-202）| eligible if compatible | 曲面 barrel-dome retro chrome 形态（真 loft primitive，非 box 占位）；`chrome_body=(0.78,0.80,0.85)` polished；dome taper 使顶 Y 收窄（`LOFT_TOP_W=BODY_W*0.78`），面板 / 腔 / recess Z 下调以适配 taper |

## 槽位图（slot graph）

pattern: multiplicity（root `body` 持有 body_silhouette 主壳 `shell` + `slot_rim_plate` + `control_panel` + 4 脚 + 装饰；单一 `carriage_lever`（PRISMATIC，**定义运动**，承载 N 个 bread 货架）+ browning 控制（Slot A）+ 3 个功能按钮 + 可选 crumb_tray（Slot C）挂到 root；slot_count multiplicity 只改顶槽 cut / 货架 visual / body 长，不加 joint）

```
body  (root；坐地于 z=0（FOOT_H 脚落地）。shell 中空壳（body_silhouette slot 决定 box / loft mesh）
        + slot_rim_plate 凹镜板 + control_panel brushed-silver +X 前面板 + 4×foot_{i} + dial_mark/brand_strip 装饰。
        BODY_L 随 slot_count 自适配（N=4→0.396；N≤2→0.280）)
  │
  ├── [carriage_lever]  (单一 PRISMATIC，**定义运动**；lever_knob + lever_stem + carriage_crossbar + N×bread_shelf_{i})
  │     ──[body_to_carriage_lever: PRISMATIC axis=(0,0,-1)(向下), origin=(carriage_x, LEVER_YC, 0.150),
  │        lower=0 upper=0.070, MotionLimits(effort=15, velocity=0.3)]
  │       挂面由 lever_placement slot 决定（front: control_panel 槽 / side: +Y 侧壁槽 + lever_guide_plate），
  │       但 joint 类型 / 轴 / 行程**不变**
  │
  ├── [slot_count multiplicity 轴]  bread_shelf_{i}  i∈range(N)（货架 = carriage 的 visual，非独立 part / joint）
  │     顶槽开口 cut（shell + slot_rim_plate）+ bread_shelf_{i} visual 各 N 份；N∈[2,4]（N=1 long-single 退化）；
  │     **所有 N 个货架骑同一 carriage_lever（1 joint，不随 N 变）→ 视觉 / cut multiplicity**
  │
  ├── [browning_control slot]  (互斥三选一；挂 +X control_panel)
  │     ├─ rotary_dial : browning_dial ──[body_to_browning_dial: REVOLUTE axis=(1,0,0), origin=(PANEL_X1, DIAL_Y, DIAL_Z), lower=0 upper=radians(270)]
  │     ├─ slider      : browning_slider ──[body_to_browning_slider: PRISMATIC axis=(0,0,1), origin=(PANEL_X1, SLIDER_Y, SLIDER_REST_Z), lower=0 upper=0.044]
  │     └─ digital     : browning_button_0/1 ──[body_to_browning_button_{i}: PRISMATIC axis=(-1,0,0), origin=(PANEL_X1, DIGI_Y, DIGI_BTN_Z[i]), lower=0 upper=0.003]  + digital_display/display_bezel inline visual
  │
  ├── [crumb_tray slot]  (二选一 / 布尔 tray_present；挂壳底 pocket)
  │     ├─ none    : (无 tray part / joint；壳底不开 pocket = pullout 的 disabled 状态)
  │     └─ pullout : crumb_tray ──[body_to_crumb_tray: PRISMATIC axis=(+1,0,0), origin=(0,0,tray_z), lower=0 upper=0.180]  + 壳底 tray_pocket cut
  │
  ├── [cancel_button / frozen_button / bagel_button]  (固定结构，非 slot；3×PRISMATIC)
  │     ──[body_to_{name}: PRISMATIC axis=(-1,0,0), origin=(PANEL_X1, BTN_Y, z), lower=0 upper=0.003]  (zip 名 + BTN_Z)
  │
  └── [body_silhouette slot]  (互斥二选一；决定 root shell mesh)
        ├─ square_box  : shell = box + fillet（body_gray matte）
        └─ retro_round : shell = 3-section slot2D.loft() dome barrel（chrome_body polished；面板 / 腔 / recess Z 下调适配 taper）
```

接口点位与 joint 语义：
- **carriage_lever 接口（定义运动）**：`carriage_lever` 是 `body` 的单一 PRISMATIC child，axis=(0,0,-1)，origin 在 lever rest 高度（front: (0.132, LEVER_YC, 0.150)；side: (LEVER_XC, BODY_W/2, 0.150)），`MotionLimits(effort=15, velocity=0.3, lower=0, upper=0.070)`。N 个 `bread_shelf_{i}` 都是该 carriage 的 visual（非独立 part / joint），rest pose q=0（货架在腔上部、透过顶槽可见，`shelf[0][2] > CAV_Z0 and shelf[1][2] < CAV_Z1`）；压下 q=0.070 货架仍在腔底上方（`shelf_dn[0][2] > CAV_Z0 + 0.005`）。lever_knob 坐挂面（front: `control_panel` / side: `lever_guide_plate`，`expect_contact` + 0.2-0.3 mm `allow_overlap`）。
- **slot_count 接口（multiplicity 主轴）**：顶槽开口（shell + slot_rim_plate 各 N 个 `_box` cut）+ N 个 `bread_shelf_{i}` carriage visual，**沿 X / Y 绝对式布局**（N=2: ±SLOT_YC 一对；N=4: 2 个 X-pair 各 ±SLOT_YC；N=1: 单宽中槽）。每货架中心由 N + 槽布局解析（不累加漂移）→ N-不变前提。**不发射额外 joint**——slot_count 改 cut / visual 数 + body 长，joint 数恒定。
- **browning_control 接口（root，互斥三选一，挂 +X control_panel）**：所有 browning 机构挂 `control_panel` 在 DIAL_Y/SLIDER_Y/DIGI_Y(=0.030) 区域（面板右下）。rotary_dial：REVOLUTE axis=(1,0,0)（面板法线），dial 孔在面板 / 壁；slider：PRISMATIC axis=(0,0,1)，竖 track 槽穿面板 / 壁；digital：2×PRISMATIC axis=(-1,0,0)，UP/DOWN pad 孔穿面板 / 壁 + `digital_display` inline。各机构 cap/tab/pad 0.2-0.3 mm 坐面板（`allow_overlap`）。
- **lever_placement 接口（root，互斥二选一）**：决定 carriage_lever 的挂面。front_lever：前壁 + control_panel 竖 lever 槽 cut，knob 在前面（+X）；side_lever：+Y 侧壁竖 lever 槽 cut + `lever_guide_plate` body visual，knob 在侧面（+Y）、面板不开 lever 槽。joint origin 落在对应挂面（`fail_if_articulation_origin_far_from_geometry` 守）。
- **crumb_tray 接口（root，二选一）**：none：无 joint（壳底密封）；pullout：壳底 `tray_pocket` cut（cavity 下方 flat pocket，X 向必须贯穿外壳端面形成可见外部开口）+ `crumb_tray` PRISMATIC axis=(+1,0,0)，origin=(0,0,tray_center_z)，q=0 全插入、q=0.180 抽出但 -X 端仍 overlap body ≥0.040 m（box-in-pocket captured-slide，`allow_overlap` tray_body↔shell）。
- **body_silhouette 接口（root）**：决定 `shell` mesh helper（square_box: box+fillet / retro_round: 3-section loft），其余接口（control_panel +X、顶槽、壳底 pocket、carriage 挂面）在两形态下相同语义；retro_round 需把面板 / 腔 / recess Z 与 lever 槽内延为 dome taper 适配（见 §9 兼容矩阵）。
- **mating policy**：carriage 是 shelf-on-carriage（货架是 carriage visual）+ knob-on-mount-face（坐面板 / guide plate）；browning dial 是 knob-on-panel-bearing、slider 是 tab-in-track captured-slide、digital pad 是 pad-on-panel；crumb_tray 是 box-in-floor-pocket captured-slide；功能按钮是 cap-on-panel-press。几何均非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 seat/captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：carriage q=0（货架在上、可见）；browning dial q=0（指 "1"）、slider q=0（低 / 弱焦度）、digital 按钮 q=0；功能按钮 q=0（未压）；crumb_tray q=0（全插入）。
- **互斥 / 可选 / 派生**：browning_control 三选一互斥；lever_placement 二选一互斥；crumb_tray 二选一（含 none disabled 状态）；body_silhouette 二选一互斥；slot_count N 是 multiplicity 主轴，与 body_silhouette（retro_round 的 dome taper 限 Y 向槽数）联动（见 §9 兼容矩阵）。

## 每槽位 Module Emits / Interfaces

### root `body`（body_silhouette = square_box 为例；retro_round 仅换 shell helper）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（root，visual: `shell` 中空壳 + `slot_rim_plate` 凹镜板 + `control_panel` brushed-silver 面板 + 4×`foot_{i}` + N×`dial_mark`/`slider_mark` 刻度 + `brand_strip`）| parent `_shell_shape` L127-177 / `_rim_plate_shape` L180-197 / `_panel_shape` L200-223 / 装配 L245-294 |
| internal joints | 无（body 是 root，自身无活动件；活动件为 carriage / browning / tray children）| — |
| upstream interface | root（坐地，4 脚落 z≈0；BODY_L 随 slot_count 自适配）| parent L48-54, L263-271 |
| downstream interface | +X control_panel（browning / front lever 接入）+ 顶槽 / 凹镜板（货架透出）+ +Y 侧壁（side lever 接入）+ 壳底 pocket（crumb_tray 接入）+ 内腔 cavity（货架居于其中）| parent L127-177 |

### 定义运动 `carriage_lever`（front_lever 为例；side_lever 仅换挂面 + guide plate）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `carriage_lever`（visual: `lever_knob` + `lever_stem` + `carriage_crossbar` + N×`bread_shelf_{i}`；N=4 额外 `side_rail_{side_tag}` 脊）| parent L296-322 / 4slice L316-361 |
| internal joints | `body_to_carriage_lever` PRISMATIC axis=(0,0,-1) origin=(carriage_x, LEVER_YC, 0.150) lower=0 upper=0.070 MotionLimits(effort=15, velocity=0.3) | parent L324-332 |
| upstream interface | lever_knob 坐挂面（front: control_panel / side: lever_guide_plate，0.2 mm seat `allow_overlap`）；stem 穿挂面竖槽 | parent L298-303, run_tests L417-423 |
| downstream interface | N×bread_shelf_{i} 透过顶槽可见（rest 在腔上部）| parent L316-322 |

### Slot A / browning_control — rotary_dial
| emits | 描述 | 来源 |
|---|---|---|
| parts | `browning_dial`（visual: `dial_cap` KnobGeometry + `dial_shaft` + 离轴 `dial_pointer_nub`）；body 上 inline `dial_mark_{i+1}`×4 刻度 | parent L334-364 / L272-287 |
| internal joints | `body_to_browning_dial` REVOLUTE axis=(1,0,0) origin=(PANEL_X1, DIAL_Y, DIAL_Z) lower=0 upper=radians(270) MotionLimits(effort=2, velocity=2) | parent L365-373 |
| upstream interface | dial_cap 坐 control_panel（0.3 mm seat `allow_overlap`）；shaft 穿面板 dial 孔 | parent L345-351, run_tests L424-430 |

### Slot A / browning_control — slider
| emits | 描述 | 来源 |
|---|---|---|
| parts | `browning_slider`（visual: `slider_tab` + `slider_stem` + `slider_carriage_plate`）；body 上 inline `slider_mark_{i+1}`×4 刻度 | slider L359-381 / L304-312 |
| internal joints | `body_to_browning_slider` PRISMATIC axis=(0,0,1) origin=(PANEL_X1, SLIDER_Y, SLIDER_REST_Z) lower=0 upper=0.044 MotionLimits(effort=4, velocity=0.2) | slider L383-391 |
| upstream interface | slider_tab 坐 control_panel（0.3 mm seat）；stem 穿竖 track 槽（面板 / 壁 cut） | slider L362-374, run_tests L442-448 |

### Slot A / browning_control — digital
| emits | 描述 | 来源 |
|---|---|---|
| parts | `browning_button_{i}`（i∈{0,1}，visual: `browning_pad_{i}` + `browning_stem_{i}` + `browning_indicator_{i}`）；body 上 inline `digital_display` + `display_bezel` | digital L350-377 / L290-303 |
| internal joints | 2×`body_to_browning_button_{i}` PRISMATIC axis=(-1,0,0) origin=(PANEL_X1, DIGI_Y, DIGI_BTN_Z[i]) lower=0 upper=0.003 | digital L378-388 |
| upstream interface | browning_pad_{i} 坐 control_panel（0.3 mm seat）；stem 穿面板 digi 孔；display/bezel 为 inline body visual（Rule 1）| digital L354-362, run_tests L440-448 |

### Slot B / lever_placement — front_lever
| emits | 描述 | 来源 |
|---|---|---|
| parts | （无独立 part；front_lever 决定 carriage_lever 挂面 = 前 control_panel + 前壁 lever 槽）| parent L162-171, L208-217 |
| internal joints | carriage_lever 的 `body_to_carriage_lever` PRISMATIC origin=(0.132, LEVER_YC, 0.150)（挂前面）| parent L324-332 |
| upstream interface | 前壁 + control_panel 竖 lever 槽 cut；knob 坐 control_panel（`expect_contact` lever_knob↔control_panel）| parent run_tests L473-480 |

### Slot B / lever_placement — side_lever
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lever_guide_plate`（body visual，`_side_guide_shape()`：proud 侧板 + lever 槽穿透）| side_lever L296-301, L224-256 |
| internal joints | carriage_lever 的 `body_to_carriage_lever` PRISMATIC origin=(LEVER_XC, BODY_W/2, 0.150)（挂 +Y 侧）；轴 / 行程不变 | side_lever L370-379 |
| upstream interface | +Y 侧壁竖 lever 槽 cut（shell）+ lever_guide_plate；knob 坐 lever_guide_plate（`expect_contact` lever_knob↔lever_guide_plate）；面板不开 lever 槽 | side_lever L169-179, run_tests L464-470, L544-550 |

### Slot C / crumb_tray — none（disabled 状态）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（tray_present=False：不发射 tray part，壳底不开 pocket）| parent（无 tray）|
| internal joints | 无 | — |
| upstream interface | 壳底密封 | parent L127-177 |

### Slot C / crumb_tray — pullout
| emits | 描述 | 来源 |
|---|---|---|
| parts | `crumb_tray`（visual: `tray_body` = base plate + 3 侧唇 + pull-handle tab）；body shell 加壳底 `tray_pocket` cut | pullout L446-471, `_crumb_tray_shape` L260-300 / pocket cut L194-204 |
| internal joints | `body_to_crumb_tray` PRISMATIC axis=(+1,0,0) origin=(0,0,tray_center_z) lower=0 upper=0.180 MotionLimits(effort=8, velocity=0.2) | pullout L463-471 |
| upstream interface | tray 坐壳底 pocket（box-in-pocket captured-slide，`allow_overlap` tray_body↔shell）；extended 仍保留插入 ≥0.040 m | pullout run_tests L696-754 |

### slot_count multiplicity（bread 货架复制；carriage visual，非移动件 / 非独立 joint）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；N×`bread_shelf_{i}`（carriage 的 visual）+ shell / rim 各 N 个顶槽 cut | 4slice 货架 L353-361 + 槽 cut L153-165, L202-214 / parent N=2 半循环 L316-322 / long-single N=1 单语句 L316-321 |
| joints | 无（Rule 1，所有货架骑 carriage 单 PRISMATIC，slot_count 不加 joint）| — |
| placement | `for i in range(N)`，沿 X / Y 绝对式布局（N=2: ±SLOT_YC；N=4: SLOT_PAIR_XC × ±SLOT_YC；N=1: 单宽中槽）；货架中心由 N + 槽布局解析 | 4slice L73-76, L354-361 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| browning_control | enum | rotary_dial / slider / digital | rotary_dial | choice | deterministic procedural sampler 选；决定 +X 面板 browning part 树 + joint 拓扑（互斥）| Slot A 表 |
| lever_placement | enum | front_lever / side_lever | front_lever | choice | sampler 选；决定 carriage_lever 挂面（joint 不变，互斥）| Slot B 表 |
| crumb_tray | enum | none / pullout | none | choice | sampler 选；pullout 发射 tray part + PRISMATIC + pocket，none = disabled（无 tray 几何）；编入 slot_choice | Slot C 表 |
| body_silhouette | enum | square_box / retro_round | square_box | choice | sampler 选；决定 root shell primitive（box / loft，互斥）| Slot D 表 |
| slot_count (N) | int | 声明产品域 **[2,4]**（模板域；N=1 long-single 为退化 baguette 形态，单独 form flag 见 §8）；sweep 采样域 [2,4]（偏小加权：N=2 高频、N=4 常见、N=3 偶尔）| 2 | conditional→slot_choice | **multiplicity 主轴**；编入 slot_choice 为 `("slot_count", f"n{N}")`（拓扑维度）；retro_round 时 N 受 dome taper Y 约束（见下 conditional + §8/§9）；**所有货架骑同一 carriage（1 joint 不随 N 变）** | parent / 4slice / long_single |
| palette_style | enum | chrome_silver / matte_black / pastel_cream / brushed_steel / retro_red | chrome_silver | palette | palette only，**不计入 slot_choice**；见下方 colorway 说明 | 各样本材质 |
| body_len_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 BODY_L（壳长 X），clamp；连带腔长 / 槽布局 X / 面板 X 锚 / 脚 X 派生 | parent L48 / resolve clamp |
| body_width_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 BODY_W（壳宽 Y），clamp；连带腔半宽 / 槽 Y / 侧 lever 挂面 / 脚 Y 派生 | parent L49 / resolve clamp |
| body_height_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 BODY_H（壳高 Z），clamp；连带腔高 / 面板 Z 范围 / lever rest Z / browning Z 锚派生（保 SLOT_CUT_Z0 在腔顶上方）| parent L50 / resolve clamp |
| lever_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 carriage PRISMATIC upper（基 0.070）；clamp 使压下货架仍在腔底上方（`shelf_dn[0][2] > CAV_Z0+0.005`）| parent L84, L331 |
| browning_range_scale | float | [0.85, 1.10] | 1.0 | conditional | rotary_dial：缩放 REVOLUTE upper（基 radians(270)，clamp ≤ radians(300)）；slider：缩放 PRISMATIC upper（基 0.044，clamp ≤ track 长）；digital：无效（按钮固定 0.003）| dial L106 / slider L98 |
| tray_travel_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 crumb_tray=pullout 有效；缩放 tray PRISMATIC upper（基 0.180）；clamp ≤ 0.95·(tray 长 − 保留插入 0.040) 使抽出不脱出 | pullout L119, L470 |
| slot_pitch_scale | float | [0.90, 1.10] | 1.0 | conditional | 仅 N≥2 有效；缩放面包槽并排 / 串排间距（SLOT_YC / SLOT_PAIR_XC），clamp 使 §下不等式满足 | parent L65 / 4slice L70 |
| (—) | constraint | — | — | inequality | 顶槽布局不超顶面：`N_y·(SLOT_W) + (N_y−1)·gap ≤ body_W − 2·margin`（Y 向并排数 N_y）且 `N_x·(SLOT_L) + (N_x−1)·gap ≤ body_L − 2·margin`（X 向串排数 N_x，N=4 时 N_x=2）；违反则升 body_L（如 N=4 升 0.396）或回缩 slot_pitch / SLOT_L | 4slice L50, L59, L70 |
| (—) | constraint | — | — | inequality | 压下货架不撞腔底：`carriage_rest_z − lever_travel·lever_travel_scale − shelf_half_h > CAV_Z0 + 0.005`；违反回缩 lever_travel | parent run_tests L504-508 |
| (—) | constraint | — | — | inequality | crumb_tray 抽出不脱出：`tray_travel·tray_travel_scale ≤ 0.95·(tray_L − 0.040)`（保留 ≥0.040 m 插入）；违反回缩 tray_travel | pullout run_tests L745-754 |
| (—) | constraint | — | — | conditional | slot_count 上限随 body_silhouette：square_box → N∈[2,4]；retro_round → N∈[2,2]（dome taper 收窄顶 Y `LOFT_TOP_W=BODY_W*0.78`，Y 向并排限单对；N=4 / N>2 需重比例 loft → 首版 gate retro_round 仅 N=2，见 §9）| retro_round L65-66 |

**palette_style colorway（5 套，来自 8 个 5★ 源材质 + 真实弹起式面包机色族）**：
- `chrome_silver`（基线 / 默认）：`body_gray=(0.40,0.40,0.41)` 壳 + `brushed_silver=(0.78,0.79,0.81)` 面板 + `dark_plastic=(0.11,0.11,0.12)` 脚 & 旋钮轴 + `dial_dark_gray=(0.24,0.25,0.26)` 旋钮 + `button_silver=(0.72,0.73,0.75)` 按钮 + `rim_gray=(0.63,0.64,0.65)` 镜板 + `carriage_metal=(0.56,0.57,0.59)` 货架（parent 原色）。
- `matte_black`：壳改深 matte 黑 (0.10,0.10,0.11) + 黑面板 + chrome 旋钮 / 拉杆 (0.72,0.74,0.78) + 黑脚；现代黑钢面包机身份。
- `pastel_cream`：壳改奶油 pastel (0.92,0.88,0.78) / 薄荷 (0.78,0.90,0.84) / 粉 (0.94,0.82,0.84) 三档之一 + chrome lever / 旋钮 + cream 面板；复古 pastel 厨房身份。
- `brushed_steel`：全身刷钢 (0.74,0.75,0.77) + dark 面板嵌条 + 黑按钮 + 黑脚；专业不锈钢面包机身份。
- `retro_red`：retro_round 配 chrome_body=(0.78,0.80,0.85) loft 壳 + 红面板 / 红嵌条 (0.74,0.10,0.10) + chrome lever；retro 红 chrome 身份（对应 body_silhouette=retro_round）。

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 browning_control / lever_placement / crumb_tray / body_silhouette / slot_count 的拓扑**。

## Multiplicity / Copy Logic

**1 根小类级 multiplicity 主轴**（面包槽 / 货架数 —— 本类的支配性多重性轴，**视觉 / cut multiplicity，非 joint multiplicity**）：

- **count_param**：`slot_count`（模板内变量 N；sources 用 `NUM_SLOTS`(4slice) / parent 的 2-tuple `("right","left")` 半循环 / long_single 的单 `bread_shelf`）。顶部面包槽数 = 槽内骑同一 carriage 的货架数。**关键**：每个货架是**单一共享 `carriage_lever` 的一个 visual**，所以 carriage 始终是**一个 PRISMATIC joint，不随 N 变化**（货架是它的 visual，不是额外 joint）。slot_count 改变的是 (1) shell 顶槽开口 cut 数、(2) `slot_rim_plate` 槽 cut 数、(3) `bread_shelf_{i}` carriage visual 数、(4) body_L（N=4 延长至 0.396）—— 全是**视觉 / cut multiplicity**。这与 cushion `pan_count`（粉盘 inline visual，Rule 1，亦无独立 joint）同型，但与 tool_cart `drawer_count`（每抽屉一个独立 PRISMATIC，joint 随 N 变）**相反**——务必在模板中明确：**slot_count ↑ ⇒ visual/cut ↑，joint 数恒定（始终 1 个 carriage PRISMATIC）**。
- **N_range**：声明产品域 **[2, 4]**（2-slice 最常见、4-slice 常见；source map 建议 [2,4]，body_L 由 slot_count 自适配，N=4 已示范延长至 0.396 + 加 `side_rail_{side_tag}` carriage 脊，N=3 由同一机制在 N=2/N=4 间内插）。样本覆盖 {2,4}（+ N=1 long-single 退化形态）仅示范 copy 逻辑，sampler 填满 [2,4]。`config_from_seed` 的 sweep 采样域 **[2, 4]**（偏小加权：N=2 高频、N=4 常见、N=3 偶尔）。
- **N=1 long-single（退化 baguette 形态）**：source `rec_toaster_var_slot_long_single` 是单宽长槽 baguette 形态（窄腔 `CAV_Y=0.040`、宽槽 `SLOT_W=0.045`、单 `bread_shelf` 无循环）。它是真实产品但读作**独立 silhouette**。首版**不进 [2,4] 主采样域**，作为可选 `long_slot_form` 布尔 form flag（默认 False）：当 `long_slot_form=True` 时强制 N=1 + 单宽中槽 + 窄腔（编入 slot_choice 为 `("slot_count", "n1_long")`）。reviewer 可决定是否把 long_slot_form 纳入主采样（小概率档）；首版保守留为 form flag，主域 N∈[2,4]。
- **sampling domain**：`config_from_seed` 用 `rng.choices((2,3,4), weights=偏小)`；`resolve_config` 把任意外部 config 的 N clamp 到 [2,4]（或 long_slot_form 时锁 1）；retro_round 时 N gate 到 2（见 §9 兼容矩阵）。
- **copied object**：单个面包槽单元 = 一个顶 shell/rim 开口 cut + 一个 `bread_shelf_{i}` carriage visual（共享 `Box(...)` 几何 / 共享 `_box(...)` cut helper），**无额外 joint**。
- **naming**：`bread_shelf_{i}` carriage visual（0-based i），顶槽 cut 经 `for i in range(N)` over `SLOT_POSITIONS`；**模板标准化为 `for i in range(slot_count)` + `bread_shelf_{i}`**（折叠 parent 的 `("right"/"left")` 半循环 tuple 与 long_single 的裸 `bread_shelf` 为统一 range 形式，4slice L153-165 + L353-361 已是此结构，可直接作 copy-logic 源）。
- **placement**：沿 X / Y **绝对式**布局——N=2: 单 X 中心 × ±SLOT_YC 一对；N=4: 2 个 X-pair（`SLOT_PAIR_XC=(-0.060,0.060)`）× ±SLOT_YC；N=3: 在 N=2/N=4 间解析（如 1 对 + 1 单，或 3 槽等距，按 reviewer 定，首版用 4slice 的 `SLOT_POSITIONS` 列表机制取前 3）。每槽 (xc,yc) 由 N + 中心解析（不累加漂移）→ N-不变前提。`bread_shelf_{i}` 中心位于其槽下、carriage rest 高度、腔内。
- **joint policy**：**所有货架骑唯一共享 `carriage_lever`**（单 `body_to_carriage_lever` PRISMATIC，axis=(0,0,-1)，travel 0.070，`MotionLimits(effort=15, velocity=0.3, lower=0, upper=0.070)`）。carriage **不链式、不 per-slot-jointed**——每个货架随单一向下压 carriage 一起动。**slot_count 改 visual / cut 数，不改 joint 数（恒 1 个 carriage PRISMATIC）。**
- **source/gating**：copy-logic 源取 4slice L153-165（shell 槽 cut loop）+ L202-214（rim 槽 cut loop）+ L353-361（货架 loop）+ L73-76（`SLOT_POSITIONS` 嵌套布局）；**N=2 取 parent**（`("right","left")` 半循环 → 折为 range(2)）、N=4 取 4slice（body_L 延长 + side_rail 脊）、N=1 取 long_single（form flag）。slot_count 与 body_silhouette 的兼容见 §9（retro_round dome taper 限 N=2）。

**slot_count 必须编入 `slot_choices_for_seed` 的 tuple**（`("slot_count", f"n{N}")`），否则不同槽数的拓扑维度损失（对齐 cushion pan_count / tool_cart drawer_count / fence_cascade 范式）。

> 注：以下是**固定 N 的 module-local visual 复制**（非可变 count 轴、非移动件、按 Rule 1 inline 为 body visual，**不暴露为 multiplicity 轴**）：4 个 `foot_{i}`（`for i, (fx,fy) in enumerate([...4 角...])`，parent L263-271）；4 个 `dial_mark_{i+1}`（`for i, ang_deg in enumerate((235,180,125,70))`，parent L272-287）/ slider 的 4 个 `slider_mark_{i+1}`（`for i in range(4)`，slider L304-312）；3 个功能按钮（`for name, z in zip(("cancel_button","frozen_button","bagel_button"), BTN_Z)`，3 个独立 PRISMATIC，parent L375-398 —— 固定 3，非可变 count 轴）；digital 的 2 个 `browning_button_{i}`（`for i in range(2)`，固定 2，属 Slot A digital module-local）。这些都不是模板级可变 count 轴。

## 拓扑多样性审计

总组合数（离散槽 + multiplicity 主轴，**受 §9 兼容矩阵约束**）：
- 朴素笛卡尔积 = browning_control(3) × lever_placement(2) × crumb_tray(2) × body_silhouette(2) = **24** base topologies（source map combo 预审）。
- 叠 slot_count：square_box（N∈[2,4]，3 值）× 上述其余槽 = 24/2(square)×3 = 36 …… 更精确：browning(3)×lever(2)×tray(2) = 12 组非-silhouette 组合；× square_box × N∈{2,3,4}(3) = 36；× retro_round × N=2(gate，1 值) = 12 → 总合法组合 = 36 + 12 = **48**（远超 ≥10 门控）。
- 仅 browning_control(3) × lever_placement(2) = **6**；× body_silhouette(2) = **12**；× crumb_tray(2) = **24**（含 REVOLUTE / PRISMATIC↑ / 2×PRISMATIC × front/side carriage 挂面 × box/loft 壳 × tray 有 / 无 的拓扑组合）已远超门控。

理由：browning_control（3 种 joint 拓扑：1 REVOLUTE 旋钮 / 1 PRISMATIC 滑块 / 2 PRISMATIC 数字按钮 + display）× lever_placement（2 种 carriage 挂面）× crumb_tray（tray PRISMATIC 有 / 无）× body_silhouette（box / loft 壳 primitive）= 24 base，叠 slot_count（square 全 N [2,4]）→ ~48 distinct。**slot_count 必须编入 slot_choices_for_seed**（`("slot_count", f"n{N}")`），否则不同槽数在 slot_choice 上不可区分，损失主多重性维度。注意：slot_count 是视觉 / cut 多重性（joint 数恒定），但仍是真实拓扑等价类维度（part visual 数 + body 比例 + 槽布局不同）。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` body_silhouette（决定 shell + N 上限），再 `rng.choice` browning_control，再 `rng.choice` lever_placement，再 `rng.choice` crumb_tray，再 `rng.choices` 加权 N（square: [2,4]；retro_round: gate 到 2），再 uniform 各连续 scale（解析 conditional：browning_range 仅 dial/slider、tray_travel 仅 pullout、slot_pitch 仅 N≥2）。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（含一个 N=2 dial+front+box、一个 N=4 slider+front+box、一个 N=2 digital+side+box、一个 N=2 dial+front+pullout、一个 retro_round N=2、一个 N=3 中间档）。


Controlled local parameterization：见 §参数表的 body_len_scale / body_width_scale / body_height_scale / lever_travel_scale / browning_range_scale(conditional@dial/slider) / tray_travel_scale(conditional@pullout) / slot_pitch_scale(conditional@N≥2)。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（body_silhouette→browning_control→lever_placement→crumb_tray）→ 采 slot_count N（square 加权 [2,4]；retro_round gate 2）→ 采 independent body_len/width/height/lever_travel scale → 派生（腔 / 槽布局 / 面板锚 / 脚位随 body scale；retro_round loft 截面随 body scale 等比）→ 解析 conditional（browning_range、tray_travel、slot_pitch 范围）→ 用 inequality 投影 / 回缩（顶槽布局 ≤ 顶面、压下货架 ≤ 腔底上方、tray 抽出 ≤ 0.95·(tray_L−0.040)）。跨部件依赖显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 carriage / browning / tray 的 joint origin、captured 接口、货架复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` body_silhouette → browning_control → lever_placement → crumb_tray（经兼容矩阵），再 `rng.choices` 加权 N（square [2,4] / retro_round gate 2），再 uniform 各 scale | slot_choices_for_seed 含 `("slot_count", f"n{N}")` 且与 build 一致 |
| compatibility matrix | (1) **retro_round × slot_count**：retro_round 的 dome taper 收窄顶 Y（`LOFT_TOP_W=BODY_W*0.78`）+ loft 为 2-slice body 调过（腔 / recess / 面板 Z 下调）→ N=4（长 body）/ N>2（Y 多对）需重比例 loft → **首版 gate retro_round 仅 N=2**；square_box 配全 N∈[2,4]。 (2) **side_lever × body_silhouette**：side_lever 假设平侧壁（square_box）；side_lever × retro_round 需把侧槽 / guide 投影到曲 barrel 面 → 首版 gate side_lever 仅 square_box（或 retro_round 配 front_lever）。 (3) **crumb_tray=pullout × body_silhouette**：pullout 壳底 pocket 在 box / loft 均可（floor flat），允许。 (4) **browning_control 与其余正交**（dial/slider/digital 均可配任意 lever / tray / silhouette / N）。 (5) **long_slot_form(N=1) × slot_count**：long_slot_form=True 强制 N=1（互斥于 N∈[2,4]），首版默认 False。 | 无 floating / collision / dome 收窄撞多槽 / 侧 lever 撞曲壁 / 压下货架撞腔底 / tray 脱出 |
| controlled local variation | 7 个 clamped scale（body_len/width/height、lever_travel、browning_range@dial/slider、tray_travel@pullout、slot_pitch@N≥2），每 build 统一；browning_range / tray_travel / slot_pitch 为 conditional | 比例变化不破坏 carriage/browning/tray origin、captured 接口、货架可见 / 不撞底、tray 保留插入、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 QC（carriage 压下、browning 动、tray 抽出）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| browning_control | 3 | yes | yes | 1 REVOLUTE 旋钮 / 1 PRISMATIC 滑块 / 2 PRISMATIC 数字按钮（互斥）|
| lever_placement | 2 | yes | no | front / side carriage 挂面（joint 不变，2 候选；定义运动槽，源池仅此 2 真实挂面）|
| crumb_tray | 2 | yes | no | none(disabled) / pullout（tray PRISMATIC 有 / 无；none 折为 pullout disabled 状态，编入 slot_choice 2 值）|
| body_silhouette | 2 | yes | no | square_box / retro_round（box / loft 壳 primitive，互斥）|
| slot_count (N) | 3（采样域 {2,3,4}，N=2 高频 / N=4 常见 / N=3 偶尔）| yes | yes | 视觉 / cut 多重性维度，编入 slot_choice；N=1 long-single 为 form flag |


## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("slot_count", f"n{N}")`（及 `("browning_control", ...)`/`("lever_placement", ...)`/`("crumb_tray", ...)`/`("body_silhouette", ...)`）
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，N 采样域 ⊆ [2,4]（retro_round 时 gate 2）
- `resolve_config` 把 slot_count clamp 到 [2,4]（或 long_slot_form 锁 1），各 scale clamp 到声明范围；browning_range / tray_travel / slot_pitch 为 conditional 随 browning_control / crumb_tray / N 解析；三条 clearance inequality 在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（retro_round gate N=2；side_lever gate square_box；crumb_tray=none 不发射 tray 几何 + 壳底不开 pocket）
- 连续 scale clamp 后不破坏 carriage/browning/tray joint origin、captured 接口、货架可见 / 不撞腔底、tray 保留插入、N 复制
- **定义运动**：`body_to_carriage_lever` PRISMATIC axis≈(0,0,-1)（axis[2]<0，abs≈1）upper≈0.070（全 silhouette / lever_placement / N 不变）；**carriage 始终是单一 PRISMATIC joint，joint 数不随 slot_count 变化**（slot_count 只改 bread_shelf visual / 顶槽 cut 数）
- 关键 joint（browning）：rotary_dial `body_to_browning_dial` REVOLUTE axis≈(1,0,0)（abs(axis[0])>0.99）upper≈radians(270)；slider `body_to_browning_slider` PRISMATIC axis≈(0,0,1) upper≈0.044；digital 2×`body_to_browning_button_{i}` PRISMATIC axis≈(-1,0,0) upper≈0.003
- 关键 joint（可选）：crumb_tray=pullout 时 `body_to_crumb_tray` PRISMATIC axis≈(+1,0,0) upper≈0.180 + extended 保留插入 ≥0.040；3 个功能按钮 `body_to_{name}` PRISMATIC axis≈(-1,0,0) upper≈0.003
- captured / seat overlap：element-scoped `allow_overlap`（lever_knob↔control_panel 或 lever_knob↔lever_guide_plate；dial_cap↔control_panel；slider_tab↔control_panel；browning_pad_{i}↔control_panel；{name}_cap↔control_panel；tray_body↔shell），照搬各样本 run_tests 的 allow_overlap 段
- copied object 遵循 `bread_shelf_{i}` 命名 + 绝对式沿 X/Y 布局 + Rule 1（货架 = carriage visual，无独立 joint；顶槽 cut 同步 N）
- grandfather：所有 carriage / browning / tray captured / seat 接口省略 MatingContract，由 `fail_if_articulation_origin_far_from_geometry` + allow_overlap 守

## Reject cases

- 把 slot_count 当普通 int 参数、不进 slot_choice → 不同槽数 slot_choice 同形，损失主多重性维度（违反 §8/§9 硬要求）。
- 给每个面包槽 / 货架发独立 joint（per-slot PRISMATIC）→ 违反核心拓扑：所有货架骑**同一**共享 carriage（1 PRISMATIC joint 不随 N 变）；slot_count 是视觉 / cut 多重性，不是 joint 多重性。
- retro_round × N=4（或 N>2）不重比例 loft → dome taper 收窄顶 Y 撞多槽 / 长 body 撑破 loft；必须 gate retro_round 仅 N=2（或重调 loft，首版 gate）。
- side_lever × retro_round 不投影侧槽到曲壁 → 侧 lever 槽 / guide plate 悬在曲 barrel 面外；首版 gate side_lever 仅 square_box。
- crumb_tray=none 仍发射 tray part / joint 或壳底开 pocket → none 应是 pullout 的 disabled 状态（无任何 tray 几何 + 壳底密封）。
- carriage / browning / tray rest pose 设成展开 / 压下 / 抽出而非 q=0 → current-pose 与 viewer 目检不符（所有样本 q=0：货架在上可见、旋钮指 1、tray 全插入）。
- carriage / browning / tray joint origin 放在腔中心或任意点而非真实挂面 / 槽硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL（carriage origin 在 lever rest 高度、dial/slider/digital 在面板对应区、tray 在壳底 pocket）。
- lever_travel / browning_range / tray_travel 过大致货架撞腔底 / 旋钮过开 / tray 脱出 → §7 三条不等式 FAIL；须按比例回缩。
- 给 captured / seat 接口补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质（palette_style / body scale）当新 candidate 塞进 slot → 不是结构差异。
- 把"toaster oven（小烤箱）"语义混入（侧 / 下翻玻璃门 + 内腔托盘）→ 出类，本类是顶插面包槽弹起式面包机（同名 `rec_toaster_oven_*` 是另一小类）。

## 与相邻类别的边界

- 不该混入：**烤箱式多功能炉 / 小烤箱（toaster oven）**——侧开 / 下翻玻璃门 + 内部烤盘 / 烤架 + 旋钮温控的箱式炉，主运动是炉门铰链 REVOLUTE 与内腔托盘，而非顶部弹起 carriage；同名但是完全不同的结构家族（同步副本里的 `rec_toaster_oven_*` 即此，已排除）。如需可作单独 slug `toaster_oven`。
- 不该混入：**面包机（bread maker / bread machine）**——高桶身 + 顶盖 + 内桶 + 揉面叶片，发酵 / 烘焙整条面包，无面包槽 / 无弹起 carriage。
- 不该混入：**三明治机 / 帕尼尼机 / 电烤盘（sandwich press / panini grill / griddle）**——上下夹合 REVOLUTE 蛤壳热板，主运动是上盖翻合而非顶插弹起；本类无夹合热板。
- 不该混入：**电水壶 / 咖啡机等其他台面厨电**——主运动 spine 不同（倾倒 / 滴滤），非面包槽弹起形态。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) slot_count 作为**视觉 / cut multiplicity**（所有货架骑同一 carriage，1 PRISMATIC joint 不随 N 变）的建模是否符合 multiplicity 审计期望（与 tool_cart drawer_count 的 per-N joint 相反）；(2) N_range 取 [2,4]（主域）+ N=1 long-single 作 form flag（默认 False）是否合适，还是把 long_slot_form 纳入主采样小概率档；(3) crumb_tray=none 折为 pullout 的 disabled/tray_present=False 状态（编入 slot_choice 2 值）是否接受；(4) retro_round gate N=2 + side_lever gate square_box 的兼容降级策略；(5) lever_placement / crumb_tray / body_silhouette 各 2 candidate（未达 3，源池真实上限）是否接受；(6) Topology target ~48<300 的说明是否接受（本小类真实结构上限 + slot_count 是视觉多重性））|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：`_box`/`_xcyl`（全样本 CadQuery 原语，照搬）、`_shell_shape`（body_silhouette 切换：square_box=box+fillet / retro_round=3-section slot2D.loft）、`_rim_plate_shape`/`_panel_shape`（随 lever_placement 决定是否 cut 前 lever 槽 + 随 browning_control 决定 dial/track/digi 孔）、`_lever_knob_shape`（front / side 两形）、`_side_guide_shape`（仅 side_lever）、`_crumb_tray_shape`（仅 pullout）、`_rounded_pad`（仅 digital）、`_slider_tab_shape`（仅 slider）。
- captured / seat 接口 allow_overlap：`run_toaster_tests` 里逐机构补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（parent L417-438 lever_knob/dial_cap/button caps↔control_panel；slider L435-456；digital L433-456；side_lever L464-485 lever_knob↔lever_guide_plate；pullout L696-702 tray_body↔shell）。
- conditional 范围解析顺序：先采 body_silhouette / browning_control / lever_placement / crumb_tray / N → 解析 retro_round gate N=2 / side_lever gate square_box / browning_range（仅 dial/slider）/ tray_travel（仅 pullout）/ slot_pitch（仅 N≥2）→ 采 body_len/width/height/lever_travel independent scale → 派生（腔 / 槽布局 / 面板锚 / 脚位 / loft 截面随 body scale）→ 投影三条 clearance inequality。
- slot_count copy 折叠：把 parent 的 `("right","left")` 半循环 + long_single 的裸 `bread_shelf` 折为统一 `for i in range(slot_count)` over `SLOT_POSITIONS`（照 4slice L73-76 + L153-165 + L353-361 机制）；**carriage 始终单一 PRISMATIC，货架仅是其 visual**；body_L 随 N 派生（N=4→0.396 + side_rail 脊；N=3 内插；N=2→0.280）。
- 参考模板：`agent/templates/Handtools_Tool_cart.py`（同为 multiplicity pattern：root carcass + 固定 named slots + `(count, f"n{N}")` 进 slot_choice + 绝对式 placement + 兼容矩阵 gating + captured allow_overlap 骨架——但注意 tool_cart 是 per-N joint，本类 slot_count 是 per-N visual/cut（joint 恒 1），更接近 `cushion.py` 的 pan_count Rule 1 inline 复制；二者结合改编）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | root + A/B/C/D + N（parent 基线）| square_box + rotary_dial + front_lever + none + N=2 | rec_…_d8fcb465 | `_shell_shape` L127-177 / `_rim_plate_shape` L180-197 / `_panel_shape` L200-223 / carriage+PRISMATIC L296-332 / `browning_dial`+REVOLUTE L334-373 / 功能按钮 L375-398 / allow_overlap L417-438 | square_box + rotary_dial + front_lever + 定义运动 carriage + N=2 货架基线 + 共享 shell/panel helper + captured/seat 范式 |
| S2 | A | slider | rec_toaster_var_browning_slider | `_slider_tab_shape` L251-260 / `browning_slider` L359-381 / PRISMATIC +Z L383-391 / 竖 track cut shell L176-186 + panel L231-241 / `slider_mark` L304-312 / allow_overlap L442-448 | 竖滑块 browning（PRISMATIC +Z + track captured-slide）|
| S3 | A | digital | rec_toaster_var_browning_digital | `_rounded_pad` L130-139 / `browning_button_{i}` L350-388 / 2×PRISMATIC -X / `digital_display`+`display_bezel` L290-303 / allow_overlap L433-456 | 数字 browning（2 PRISMATIC UP/DOWN + display inline）|
| S4 | B | side_lever | rec_toaster_var_lever_side | `_side_guide_shape` L224-256 / `lever_guide_plate` L296-301 / 侧式 `_lever_knob_shape` L259-263 / 侧壁竖槽 cut L169-179 / carriage L336-379（joint axis/行程不变）/ allow_overlap L464-470 | carriage lever 移 +Y 侧壁（挂面变、joint 不变）|
| S5 | C | pullout | rec_toaster_var_crumb_tray_pullout | `_crumb_tray_shape` L260-300 / `crumb_tray` L446-471 / PRISMATIC +X L463-471 / 壳底 `tray_pocket` cut L194-204 / 保留插入 run_tests L745-754 / allow_overlap L696-702 | 壳底抽出 crumb tray（PRISMATIC +X + box-in-pocket captured-slide）|
| S6 | D | retro_round | rec_toaster_var_body_retro_round | `_shell_shape` 3-section slot2D.loft L138-211 / loft 截面 const L61-66 / `chrome_body` L270 / 面板 / 腔 / recess Z 适配 L91, L71, L83 | 曲面 barrel-dome retro chrome 壳（真 loft primitive）|
| S7 | N（multiplicity）| slot_count N=4 | rec_toaster_var_slot_4slice | `NUM_SLOTS=4` L48 / `SLOT_POSITIONS` 嵌套 loop L73-76 / shell cut loop L153-165 / rim cut loop L202-214 / 货架 loop `bread_shelf_{i}` L353-361 / `side_rail_{side_tag}` L336-352 / body_L=0.396 L50 | 4-slice copy-logic 源（range loop + body 延长 + carriage 脊，**单 carriage joint 不变**）|
| S8 | N（multiplicity）| slot_count N=1 long-single | rec_toaster_var_slot_long_single | 单宽长槽 cut L139-148 / 单 `bread_shelf` L316-321 / 窄腔 `CAV_Y=0.040` L58 / 宽槽 `SLOT_W=0.045` L64 | N=1 baguette 退化形态 copy-logic 源（form flag，单货架仍骑同 carriage）|
