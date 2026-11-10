# microwave (countertop microwave oven) — Modular Spec

> 来源小类：`picture/Kitchen/Microwave`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Kitchen__Microwave.md`。
> **"Microwave" 在此 = 台面式微波炉（stylized countertop microwave oven，一只带门 + 转盘的台面加热腔体），不是烤面包炉（toaster oven）、不是嵌入式烤箱（built-in oven，已有独立 slug `built_in_oven`）。**
> 结构家族 = 台面微波炉：一只 chamfered `body`（root，坐地于四脚；前面左 3/4 切出中空 dark cooking cavity，右 1/4 嵌 control panel）+ 一只 `door`（前门机构 slot，铰链 REVOLUTE 或抽屉 PRISMATIC）+ 一只 `turntable`（腔内旋转 CONTINUOUS 玻璃盘，或退化为固定 flatbed）+ 可选内部 rack。
>
> **同步状态**：本 spec 引用的 8 个 5 星样本（1 个 parent + 7 个 fork 槽位变体）已同步进本仓库（articraft_data）`data/records/<id>/revisions/rev_000001/model.py`，rating=5。行号按各样本本仓库 `model.py` 实际行号计（已逐一逐行核对）。引用以 part / joint / helper **名字** 为准（`body` / `door` / `drawer` / `turntable` part；`door_hinge` / `drawer_slide` / `turntable_spin` / `{knob}_dial` / `body_to_rack` joint；`_shell_solid` / `_door_solid` / `_drawer_front_solid` / `_knob_mesh` / `_rack_wire` helper；`outer_shell` / `cavity_floor` / `control_panel` / `glass_plate` / `coupler_rib_{k}` / `flatbed_glass` / `touch_glass_panel` / `shelf_rack` / `cross_wire_{i}` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `microwave` |
| template path | `agent/templates/Kitchen_Microwave.py` |
| test path (optional) | `tests/agent/test_microwave_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 root `body` + 三个并行替换层：door_mechanism / turntable / control，挂同一 `body`；可选 interior rack 也挂 `body`。**door=drawer 时 turntable 改 reparent 到 drawer**——见 slot graph）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 parent + 7 fork 槽位变体；均 converged、compile success、≥1 非 fixed joint、workbench-only，rating=5）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、`for` 循环复制结构与 run_tests + allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 8/8 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **共享基线拓扑（全部 8 个样本）**：`body`（root，`_shell_solid()` chamfered shell `box.chamfer(0.012)` + cooking cavity `cut` + control-panel recess `cut`；body 上 inline 5 块 `cavity_{floor,ceiling,back_wall,left_wall,right_wall}` dark liner visual + `control_panel`/touch/dial 控件 + 4 个 `foot_{i}` 循环发射）+ `door`（或 `drawer`，前门机构）+ `turntable`（或 flatbed 退化）。`_shell_solid()`（parent L92-115）与 `_door_solid()`（parent L118-138）helper 在所有样本里**逐字复用**，仅 cavity cut 深度（drawer 把 cavity cut 加深 `box(CAV_W,0.40,CAV_H)` L114-118）与门 local frame 随机构调整。世界坐标统一：x=宽(0.52)、y=深(0.38，前面朝 −Y)、z=上(0.32)；`FRONT_Y=-0.19`。
- **door_mechanism 轴（Slot A，主机构）**：是 part 数 / joint 类型 / parent-child 拓扑变化。
  - side_hinge（parent）：`door` 独立 part，`door_hinge` **REVOLUTE** axis=(0,0,−1)（竖轴）origin 在左前缘（parent L237-245），0..100° 外摆。
  - drop_down（door_drop_down）：同 `door` parts，`door_hinge` **REVOLUTE** axis=(1,0,0)（横轴）origin 在底前缘（drop_down L244-255），0..90° 烤箱式下翻。
  - top_hinge（door_top_hinged）：同 `door` parts，`door_hinge` **REVOLUTE** axis=(−1,0,0)（横轴）origin 在顶前缘（top_hinge L254-264），0..100° 罩式上掀。
  - drawer_prismatic（door_drawer）：**改名 `drawer` part**（drawer_frame + window_glass + handle_bar + `drawer_tray` + `tray_lip_{i}`），`drawer_slide` **PRISMATIC** axis=(0,−1,0)（drawer L278-288）0..0.22 m 拉出；body 加 `guide_rail_{i}`（drawer L202-209）；**turntable 改 parent=drawer**（drawer L321-329）。这是唯一 part+joint-type swap（door_hinge REVOLUTE → drawer_slide PRISMATIC）+ turntable reparent 的轴。
- **turntable 轴（Slot B）**：是 part 数 / joint 拓扑变化。
  - rotating（parent）：`turntable` 独立 part（`drive_hub` + `coupler_rib_{0..2}` `for k in range(3)` 等角 + `glass_plate`，parent L248-274），`turntable_spin` **CONTINUOUS** axis=(0,0,1)（parent L276-284），off-axis 肋证明旋转。
  - flatbed（turntable_flatbed）：**无 `turntable` part、无 `turntable_spin` joint**；`flatbed_glass` 作 body inline visual（flatbed L183-188），固定玻璃地板；门 REVOLUTE 是唯一活动件。
- **control 轴（Slot C）**：membrane 是 body visual 无 joint；rotary_dials 加 2 个独立 part + 2 个 REVOLUTE；touch_glass 是 body visual 无 joint。
  - membrane（parent）：`control_panel` 单块 charcoal box 作 body visual（parent L187-192），无独立 part / joint。
  - rotary_dials（control_rotary_dials）：`power_knob`/`timer_knob` 2 个独立 part（`_knob_mesh` KnobGeometry skirted + off-center `{name}_pointer`，dials L337-359），各一 `{name}_dial` **REVOLUTE** axis=(0,−1,0)（前面法向）0..270°（dials L361-374），pointer 证明旋转。
  - touch_glass（control_touch_glass）：`touch_glass_panel` + `touch_panel_backing` + `touch_mark_{0..2}` 作 body inline visual（touch L193-217），无独立 part / joint。
- **interior rack 轴（Slot D，可选）**：none（parent，空腔）/ shelf。
  - shelf（rack_shelf）：`shelf_rack` 独立 part（`frame_{front,back,left,right}` + `cross_wire_{i}` ×10 `for i in range(N_CROSS_WIRES)` + `long_wire_{i}` ×4 `for i in range(N_LONG_WIRES)`，rack L335-384，丝用 `_rack_wire(length, along)` helper L160-167）；body 加 `rack_support_{left,right}` 壁挂 ledge（rack L240-251）；`body_to_rack` **FIXED**（rack L388-394）。rack 是 FIXED，门 + turntable 仍是活动件。

## 核心身份

一只**台面式微波炉**（stylized countertop microwave oven）：一只 chamfered 浅蓝灰 `body`（root，坐地于四脚 `foot_{i}` 于 z=0；前面左 3/4 由 `_shell_solid()` 切出中空 dark cooking cavity（5 面 charcoal liner），右 1/4 嵌 control panel），前缘一只 `door`（铰链门）或 `drawer`（抽屉），腔内一只 `turntable`（旋转玻璃盘）或退化为固定 flatbed 玻璃地板，腔内可选一层 wire-grid `shelf_rack`。默认成熟域：door_mechanism(4) × turntable(2) × control(3) × interior_rack(2) 笛卡尔积的小型台面微波炉。活动语义 = **门的开合**（侧铰竖轴 REVOLUTE / 下翻横轴 REVOLUTE / 上掀横轴 REVOLUTE / 抽屉 PRISMATIC）+ **转盘旋转**（CONTINUOUS，flatbed 时无）+ 可选 **rotary dial REVOLUTE**（旋钮 0..270°）。**每个候选保≥1 非 fixed joint**：side/drop/top-hinge+任意 = 门 REVOLUTE 存活；drawer = drawer_slide PRISMATIC 存活；flatbed 也保门 REVOLUTE/drawer PRISMATIC；rotary_dials = 额外 2 REVOLUTE；rack FIXED 不算（门/转盘提供活动件）。

不该混入：
- **烤面包炉 / 小烤箱（toaster oven）**——前面玻璃门 + 内置加热管 + 烤架托盘，无旋转 turntable、无微波腔 control panel 右栏布局；本类核心身份是 cavity + 旋转玻璃盘 + 右侧控制栏。
- **嵌入式 / 壁挂烤箱（built-in oven）**——大型嵌墙、无四脚台面 footprint、门通常仅下翻 + 大握把横杆 + 内多层烤架；已有独立 slug `built_in_oven`（尺度与安装方式不同）。
- **空气炸锅 / 电饭煲 / 其他台面厨电**——非"前门 + 旋转盘 + 右控制栏"的箱体腔加热形态。

## 槽位 + 候选模块表

> **建模注记**：`door_mechanism`（Slot A）是真正的主机构槽——它既改 joint **类型**（REVOLUTE 三向 vs PRISMATIC），又在 drawer 时改 **part 名 + turntable 的 parent**（turntable 从 body reparent 到 drawer）。`turntable`（Slot B）改 part 数 + 是否有 CONTINUOUS joint。`control`（Slot C）改是否多 2 个 REVOLUTE 旋钮 part。`interior_rack`（Slot D，可选）改是否多 1 个 FIXED rack part。纯尺寸（更宽/更高/更扁的机身、cavity 尺寸、handle 长度）不作候选——属模板连续参数（见 §7）。

### Slot A：door_mechanism（前门机构 —— 主机构槽，决定门 part 名 / joint 类型 / turntable parent）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| side_hinge（基线）| rec_model-a-stylized-countertop-microwave-oven-appro_...b2de7afe（parent）| `door` part（`door_frame`=`_door_solid` L118-138 / `window_glass` / `handle_bar` 竖杆 / `handle_standoff_{top,bottom}`）L206-233；`door_hinge` **REVOLUTE** axis=(0,0,−1) origin=(DOOR_X0,DOOR_FRONT_Y,DOOR_CZ) 左前缘，lower=0/upper=rad(100) L237-245 | eligible if compatible | 竖轴侧开门：`door` 独立 part，绕左前竖缘外摆（toward −Y）0..100°；全高竖 `handle_bar`；`_door_solid` origin 在左铰缘 |
| drop_down | rec_microwave_var_door_drop_down | 同 `door` parts（`_door_solid` 改底心 origin L120-140）；`door_hinge` **REVOLUTE** axis=(1,0,0) origin=(DOOR_CX,DOOR_BACK_Y,DOOR_BOTTOM_Z) 底前缘，lower=0/upper=rad(90) L244-255；横 `handle_bar` 在顶 L221-240 | eligible if compatible | 横轴下翻门（烤箱式）：绕底前横缘下翻 0..90°；顶部横 `handle_bar`；`_door_solid` origin 在底心 |
| top_hinge | rec_microwave_var_door_top_hinged | 同 `door` parts（`_door_solid` 改顶心 origin L129-149）；`door_hinge` **REVOLUTE** axis=(−1,0,0) origin=(HINGE_X,HINGE_Y,HINGE_Z=DOOR_TOP_Z) 顶前缘，lower=0/upper=rad(100) L254-264；全高竖 `handle_bar` L233-249 | eligible if compatible | 横轴上掀门（罩式）：门从顶铰悬下，绕顶前横缘上掀 0..100°；`_door_solid` origin 在顶心 |
| drawer_prismatic | rec_microwave_var_door_drawer | **`drawer` part**（`drawer_frame`=`_drawer_front_solid` L130-152 / `window_glass` / `handle_bar` / `drawer_tray` L261-266 / `tray_lip_{i}` `for x_sign` L268-275）L231-275；`drawer_slide` **PRISMATIC** axis=(0,−1,0) origin=(CAV_X,FRONT_Y,PANEL_CZ)，lower=0/upper=0.22 L278-288；body 加 `guide_rail_{i}` `for x_sign` L202-209；**turntable parent=drawer** L321-329；allow_overlap(outer_shell↔drawer_tray / tray_lip) L438-450 | eligible if compatible | 拉出式抽屉微波炉：`drawer` 改名 part，带平托盘 `drawer_tray` 伸入腔，沿 −Y PRISMATIC 拉出 0..0.22 m；**turntable 重新 parent 到 drawer 上随抽屉平移**；body 上有 `guide_rail_{i}` 滑轨 visual |

### Slot B：turntable（腔内地面 —— 决定是否有旋转 part + CONTINUOUS joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| rotating（基线）| rec_model-a-...-b2de7afe（parent）| `turntable` part（`drive_hub` Cylinder L249-254 / `coupler_rib_{k}` `for k in range(3)` 等角 L256-267 / `glass_plate` Cylinder L269-274）；`turntable_spin` **CONTINUOUS** axis=(0,0,1) origin=(TT_X,TT_Y,TT_Z=floor) L276-284 | eligible if compatible | 旋转玻璃盘：driven hub 上的薄玻璃盘绕竖轴 CONTINUOUS 旋转；3 根 off-axis `coupler_rib` 证明旋转；rest parent=body（drawer 时 parent=drawer）|
| flatbed | rec_microwave_var_turntable_flatbed | `flatbed_glass` body inline visual（Box，坐 cavity floor liner 上）L183-188；**无 `turntable` part、无 `turntable_spin` joint** | eligible if compatible | 固定平玻璃地板：腔底一块固定玻璃，无旋转件；门 REVOLUTE / drawer PRISMATIC 是活动件。run_tests 显式只测 flatbed_glass 几何，不测 turntable（flatbed L355-383）|

> 降级理由（Slot B 仅 2 candidate）：微波炉腔底现实词汇表本身窄——旋转盘 vs 固定 flatbed 两种真实收敛形态，无第三种真实结构可加。Slot A(4) × Slot C(3) 已提供主拓扑多样性，Slot B ×2（含"是否有 CONTINUOUS joint"的拓扑差异）充裕（见 §9）。

### Slot C：control（前面右栏控制 —— 决定是否多 2 个 REVOLUTE 旋钮 part）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| membrane（基线）| rec_model-a-...-b2de7afe（parent）| `control_panel` 单块 charcoal Box body inline visual，嵌右栏 recess L187-192 | eligible if compatible | 平膜键盘条：flat charcoal strip 坐 shell recess，无移动控件件 / 无 joint |
| rotary_dials | rec_microwave_var_control_rotary_dials | `power_knob`/`timer_knob` 2 独立 part（`_knob_mesh` KnobGeometry skirted L166-184 + off-center `{name}_pointer` Box L354-359）`for (knob_name,knob_z) in KNOB_SPECS` L337-374；各 `{name}_dial` **REVOLUTE** axis=(0,−1,0)（前面法向）origin=(PANEL_CX,KNOB_MOUNT_Y,knob_z)，lower=0/upper=rad(270) L361-374 | eligible if compatible | 两只 skirted 家电旋钮：各绕前面法向 REVOLUTE 0..270°；off-center `pointer` 证明旋转；knob mesh rpy=(π/2,0,0) 把 +Z 转到 −Y 外凸；**+2 part +2 joint** |
| touch_glass | rec_microwave_var_control_touch_glass | `touch_glass_panel` + `touch_panel_backing` + `touch_mark_{0..2}` `for dy` 3 个 body inline visual L193-217 | eligible if compatible | 单块凹入暗玻璃触控面 + 3 道 inline touch-zone 标记；无移动控件件 / 无 joint；run_tests 验玻璃薄(<5mm) + 标记存在（touch L386-410）|

### Slot D：interior_rack（腔内 turntable 上方内容 —— 可选 FIXED 层）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| none（基线）| rec_model-a-...-b2de7afe（parent）| （无 rack part）| eligible if compatible | turntable 上方空腔，无 rack |
| shelf | rec_microwave_var_rack_shelf | `shelf_rack` part（`frame_{front,back,left,right}` Box L339-364 + `cross_wire_{i}` `for i in range(10)` L367-374 + `long_wire_{i}` `for i in range(4)` L377-384，丝用 `_rack_wire(length,along)` helper L160-167）；body 加 `rack_support_{left,right}` ledge L240-251；`body_to_rack` **FIXED** origin=(CAV_X,RACK_YC,RACK_BOTTOM_Z−0.0005) L388-394；run_tests 验 rack 在 mid-level + 清 turntable ≥0.03（rack L553-617）| eligible if compatible | 中层可取 wire-grid 架：矩形 frame + 网格丝，坐 cavity 壁 `rack_support` ledge 上；`body_to_rack` **FIXED**（门 + turntable 仍是活动件）；丝网密度是 module-internal 固定阵列（见 §8）|

> Slot D 是 0/1 可选层（rack 个数 ∈ {0,1}），编入 slot_choice 为 `("interior_rack", none|shelf)` 提供拓扑差异（是否多 1 个 FIXED part + 2 个 support ledge visual）。

## 槽位图（slot graph）

pattern: parallel_children（固定 root `body`；door_mechanism / turntable / control / interior_rack 各自的活动件或 visual 按候选挂 `body`；**例外**：door=drawer 时 turntable reparent 到 drawer）

```
body (root, 坐地于 4 脚; _shell_solid: chamfered shell + cavity cut + control recess;
      inline visual: cavity_{floor,ceiling,back/left/right_wall} liner + foot_{i})
  │
  ├── [door_mechanism slot]  (四选一, 互斥主机构)
  │     ├─ side_hinge  : door ──[door_hinge: REVOLUTE axis=(0,0,−1), origin=左前竖缘 (DOOR_X0,DOOR_FRONT_Y,DOOR_CZ)] 0..100°
  │     ├─ drop_down   : door ──[door_hinge: REVOLUTE axis=(1,0,0),  origin=底前横缘 (DOOR_CX,DOOR_BACK_Y,DOOR_BOTTOM_Z)] 0..90°
  │     ├─ top_hinge   : door ──[door_hinge: REVOLUTE axis=(−1,0,0), origin=顶前横缘 (HINGE_X,HINGE_Y,DOOR_TOP_Z)] 0..100°
  │     └─ drawer      : drawer ─[drawer_slide: PRISMATIC axis=(0,−1,0), origin=(CAV_X,FRONT_Y,PANEL_CZ)] 0..0.22 m
  │                       (body 加 guide_rail_{i}; drawer 带 drawer_tray + tray_lip_{i})
  │
  ├── [turntable slot]  (二选一)
  │     ├─ rotating : turntable ──[turntable_spin: CONTINUOUS axis=(0,0,1), origin=cavity floor center (TT_X,TT_Y,TT_Z)]
  │     │              ★ 若 door=drawer → turntable_spin parent=DRAWER, origin=(0, TT_Y_LOCAL, tray_top_z)（随抽屉平移）
  │     └─ flatbed  : flatbed_glass = body inline visual (固定地板, 无 joint)
  │
  ├── [control slot]  (三选一)
  │     ├─ membrane     : control_panel = body inline visual (无 joint)
  │     ├─ rotary_dials : power_knob/timer_knob (2 part) ──[{name}_dial: REVOLUTE axis=(0,−1,0), origin=(PANEL_CX,KNOB_MOUNT_Y,knob_z)] 0..270°
  │     └─ touch_glass  : touch_glass_panel + touch_panel_backing + touch_mark_{i} = body inline visual (无 joint)
  │
  └── [interior_rack slot]  (可选, 二选一)
        ├─ none  : (无 rack part)
        └─ shelf : shelf_rack ──[body_to_rack: FIXED, origin=(CAV_X,RACK_YC,RACK_BOTTOM_Z−0.0005)]
                    (body 加 rack_support_{left,right} ledge; rack 网格丝 module-internal)
```

接口点位与 joint 语义：
- **body → door / drawer（door_mechanism 接口，互斥四选一）**：mating = body 前面开口（cavity opening）。所有门坐地于 `FRONT_Y=-0.19` 面：
  - side_hinge：REVOLUTE axis=(0,0,−1)，origin 落左前竖缘（真实门左缘硬件），q=0 闭合贴 body 前面（`expect_gap` y 0..0.004），q=upper 外摆 toward −Y。
  - drop_down：REVOLUTE axis=(1,0,0)，origin 落底前横缘，q=0 直立闭合，q=upper 下翻成近水平（顶缘掉到闭合高度以下）。
  - top_hinge：REVOLUTE axis=(−1,0,0)，origin 落顶前横缘，q=0 悬直闭合，q=upper 上掀过 body 顶。
  - drawer：PRISMATIC axis=(0,−1,0)，origin 落 cavity 前心，q=0 抽屉前板坐 body 前面（`drawer_frame` max_y≈FRONT_Y）、托盘插腔内（`expect_overlap` outer_shell↔drawer_tray ≥0.10），q=upper 拉出 0.22 m；body `guide_rail_{i}` 滑轨在腔壁。
- **body/drawer → turntable（turntable 接口）**：
  - rotating（door≠drawer）：CONTINUOUS axis=(0,0,1) parent=body，origin=cavity floor center，`drive_hub` 坐 cavity_floor liner（`expect_gap` z 0..0.002），off-axis `coupler_rib_0` 旋转后 y-center 位移 >0.015 证明旋转。
  - rotating（door=drawer）：CONTINUOUS axis=(0,0,1) **parent=drawer**，origin=(0,TT_Y_LOCAL,tray_top_z) 局部坐标，turntable 随抽屉平移（drawer L319-329；run_tests "turntable moves with the drawer" L485-492）。
  - flatbed：无 joint（`flatbed_glass` body inline visual 坐 cavity floor，`expect_gap`/`expect_within` 自洽于 body）。
- **body → control（control 接口）**：
  - membrane / touch_glass：无 joint（body inline visual 嵌右栏 recess）。
  - rotary_dials：2 个 `{name}_dial` REVOLUTE axis=(0,−1,0)，origin=(PANEL_CX, KNOB_MOUNT_Y=panel front, knob_z)，knob 外凸过 panel 前面 0.005，旋转后 `{name}_pointer` x-center 位移 >0.010 证明旋转；两旋钮竖向分离（`expect_gap` z ≥0.01）。
- **body → rack（interior_rack 接口，可选）**：shelf 时 `body_to_rack` FIXED，origin 落 cavity 壁 `rack_support` ledge 接触面（mid-level RACK_BOTTOM_Z）；rack 清 turntable 下方 ≥0.03（`expect_gap` z）；rack 在 body footprint 内。
- **mating policy**：door/drawer 是 hinge-on-edge / slide-in-cavity 捕获式装配（门铰落真实缘硬件、抽屉托盘嵌 cavity）；turntable hub 坐 floor liner；knob 嵌 panel 面；rack 坐 support ledge——**几何非两轴对齐面对接 → 省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（drawer 的 outer_shell↔drawer_tray/tray_lip overlap 见 drawer L438-450，照搬）。
- **rest pose**：所有门 q=0 闭合（侧/上掀悬直、下翻直立、抽屉收回贴前面）；turntable 任意（CONTINUOUS 无 lower）；旋钮 q=0；rack FIXED。
- **互斥 / 可选 / 派生**：door_mechanism 四候选互斥；turntable 二候选互斥；control 三候选互斥；interior_rack 二候选（含 none）。**派生**：turntable 的 parent 由 door_mechanism 派生（drawer→parent=drawer，其余→parent=body）；door=drawer × turntable=flatbed 时固定 flatbed 玻璃归属需裁决（见 §9 兼容矩阵）。

## 每槽位 Module Emits / Interfaces

### root / body（所有候选共享；door_mechanism / control / rack 的 body 侧 visual 按候选追加）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（root，visual：`outer_shell`=`_shell_solid` mesh + `cavity_{floor,ceiling,back_wall,left_wall,right_wall}` liner + `control_panel`/touch/dial 控件 + `foot_{i}`×4 + drawer 时 `guide_rail_{i}` + shelf 时 `rack_support_{left,right}`）| parent `_shell_solid` L92-115 + body 装配 L145-203 |
| internal joints | 无（body 是 root）| — |
| upstream interface | root（坐地于 z=0 四脚，无父）| parent L195-203 |
| downstream interface | cavity opening 前面（供 door/drawer）+ cavity floor（供 turntable/flatbed）+ 右栏 recess（供 control）+ cavity 壁 ledge（供 rack）| parent L102-114 |

### Slot A / door_mechanism — side_hinge（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door`（visual：`door_frame`=`_door_solid` mesh + `window_glass` + 竖 `handle_bar` + `handle_standoff_{top,bottom}`）| parent L206-233 |
| internal joints | `door_hinge` REVOLUTE axis=(0,0,−1)，origin=(DOOR_X0,DOOR_FRONT_Y,DOOR_CZ)，lower=0/upper=rad(100) | parent L237-245 |
| upstream interface | `door` 左前竖缘落 body 前面左缘（captured hinge edge）| parent L237-245 |

### Slot A / door_mechanism — drop_down
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door`（同 side_hinge parts，`_door_solid` 底心 origin；横 `handle_bar` 在顶）| drop_down L120-140, L221-240 |
| internal joints | `door_hinge` REVOLUTE axis=(1,0,0)，origin=(DOOR_CX,DOOR_BACK_Y,DOOR_BOTTOM_Z)，lower=0/upper=rad(90) | drop_down L244-255 |
| upstream interface | `door` 底前横缘落 body 前面底缘 | drop_down L244-255 |

### Slot A / door_mechanism — top_hinge
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door`（同 side_hinge parts，`_door_solid` 顶心 origin；全高竖 `handle_bar`）| top_hinge L129-149, L233-249 |
| internal joints | `door_hinge` REVOLUTE axis=(−1,0,0)，origin=(HINGE_X,HINGE_Y,DOOR_TOP_Z)，lower=0/upper=rad(100) | top_hinge L254-264 |
| upstream interface | `door` 顶前横缘落 body 前面顶缘 | top_hinge L254-264 |

### Slot A / door_mechanism — drawer_prismatic
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drawer`（visual：`drawer_frame`=`_drawer_front_solid` mesh + `window_glass` + 竖 `handle_bar` + `handle_standoff_{i}` + `drawer_tray` + `tray_lip_{i}`×2）；body 加 `guide_rail_{i}`×2 | drawer L202-209, L231-275 |
| internal joints | `drawer_slide` PRISMATIC axis=(0,−1,0)，origin=(CAV_X,FRONT_Y,PANEL_CZ)，lower=0/upper=0.22 | drawer L278-288 |
| upstream interface | `drawer_tray` 插 cavity（`allow_overlap(outer_shell, drawer_tray/tray_lip)` + `expect_overlap` ≥0.10）；turntable reparent 到 drawer | drawer L321-329, L438-465 |

### Slot B / turntable — rotating（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `turntable`（visual：`drive_hub` Cylinder + `coupler_rib_{k}`×3 + `glass_plate` Cylinder）| parent L248-274 |
| internal joints | `turntable_spin` CONTINUOUS axis=(0,0,1)，parent=body（drawer 时=drawer），origin=cavity floor center（drawer 时=tray top 局部） | parent L276-284 / drawer L321-329 |
| upstream interface | `drive_hub` 坐 cavity_floor liner（`expect_gap` z 0..0.002）/ drawer tray 顶 | parent L416-425 |

### Slot B / turntable — flatbed
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`flatbed_glass` 为 body inline visual）| flatbed L183-188 |
| internal joints | 无 | — |
| upstream interface | `flatbed_glass` 坐 cavity_floor，居腔 footprint 内（`expect_gap`/`expect_within` body↔body）| flatbed L365-383 |

### Slot C / control — membrane（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`control_panel` 为 body inline visual）| parent L187-192 |
| internal joints | 无 | — |
| upstream interface | `control_panel` 嵌右栏 recess，居 door 右侧 | parent L352-360 |

### Slot C / control — rotary_dials
| emits | 描述 | 来源 |
|---|---|---|
| parts | `power_knob` + `timer_knob`（各 visual：`{name}_cap`=`_knob_mesh` KnobGeometry skirted + off-center `{name}_pointer`）| dials L337-359 |
| internal joints | 2 个 `{name}_dial` REVOLUTE axis=(0,−1,0)，origin=(PANEL_CX,KNOB_MOUNT_Y,knob_z)，lower=0/upper=rad(270) | dials L361-374 |
| upstream interface | knob 嵌 panel 面、外凸 −Y >0.005，cap 居 panel X 内（`expect_within`）| dials L561-580 |

### Slot C / control — touch_glass
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`touch_glass_panel` + `touch_panel_backing` + `touch_mark_{0..2}` 为 body inline visual）| touch L193-217 |
| internal joints | 无 | — |
| upstream interface | 玻璃面嵌右栏 recess（薄 <5mm），居 door 右侧；backing 连玻璃到 recess 后壁 | touch L376-410 |

### Slot D / interior_rack — shelf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `shelf_rack`（visual：`frame_{front,back,left,right}` + `cross_wire_{i}`×N_CROSS + `long_wire_{i}`×N_LONG）；body 加 `rack_support_{left,right}` ledge | rack L240-251, L335-384 |
| internal joints | `body_to_rack` FIXED，origin=(CAV_X,RACK_YC,RACK_BOTTOM_Z−0.0005) | rack L388-394 |
| upstream interface | rack frame 侧轨坐 `rack_support` ledge（mid-level），清 turntable 下方 ≥0.03 | rack L237-251, L603-609 |

### interior_rack 内部 wire-grid（module-local 固定阵列；non-moving visual）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`cross_wire_{i}`/`long_wire_{i}` 作 `shelf_rack` 的 visual | rack L367-384 |
| joints | 无（Rule 1，丝是非移动 inline visual）| — |
| placement | `for i in range(N_CROSS_WIRES)` 沿 Y 等距 + `for i in range(N_LONG_WIRES)` 沿 X 等距，绝对式 `_rack_wire(length,along)` 复用 | rack L160-167, L367-384 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| door_mechanism | enum | side_hinge / drop_down / top_hinge / drawer_prismatic | side_hinge | choice | 由 deterministic procedural sampler 选；drawer 改 part 名 + joint 类型 + turntable parent | Slot A 表 |
| turntable | enum | rotating / flatbed | rotating | choice | sampler 选；rotating 独带 `turntable_spin` CONTINUOUS | Slot B 表 |
| control | enum | membrane / rotary_dials / touch_glass | membrane | choice | sampler 选；rotary_dials 独带 2 个 `{name}_dial` REVOLUTE | Slot C 表 |
| interior_rack | enum | none / shelf | none | choice | sampler 选；shelf 独带 `body_to_rack` FIXED + rack part | Slot D 表 |
| palette_style | enum | white_appliance / black_appliance / stainless_steel / pale_blue_gray(基线) / cream_retro | pale_blue_gray | palette | palette only，**不计入 slot_choice**；每 seed 采一套（材质/色，见下表）| 各样本材质 |
| body_width_scale | float | [0.90, 1.15] | 1.0 | independent | 缩放 BODY_W → 联动 cavity / door / panel X，clamp | parent L36 |
| body_depth_scale | float | [0.90, 1.15] | 1.0 | independent | 缩放 BODY_D → 联动 cavity 深 / drawer travel 上限 / FRONT_Y，clamp | parent L37 |
| body_height_scale | float | [0.88, 1.18] | 1.0 | independent | 缩放 TOTAL_H → 联动 cavity 高 / door 高 / panel 高，clamp | parent L38 |
| cavity_inset_scale | float | [0.92, 1.08] | 1.0 | derived | cavity 内壁 inset / liner，随 body scale 等比派生（保 cavity 在 footprint 内）| parent L46-53 |
| door_open_angle_scale | float | [0.85, 1.08] | 1.0 | conditional | 仅 REVOLUTE 门（side/drop/top）有效；缩放 `door_hinge` upper（保 ≤π·0.95）| parent L244 |
| drawer_travel_scale | float | [0.80, 1.10] | 1.0 | conditional | 仅 door=drawer 有效；缩放 `drawer_slide` upper（≤ 暴露托盘所需 & ≤ rail 长）| drawer L70 |
| knob_size_scale | float | [0.85, 1.20] | 1.0 | conditional | 仅 control=rotary_dials 有效；缩放 KNOB_DIAMETER/SKIRT（保两旋钮竖向不重叠）| dials L93-95 |
| rack_wire_density | (见 §8) | cross [6,14] / long [3,6] | 10 / 4 | conditional | 仅 interior_rack=shelf 有效；module-internal 丝数，**不进 slot_choice** | rack L91-92 |
| (—) | constraint | — | — | inequality | cavity 在 body footprint 内：`CAV_W·scale ≤ BODY_W·scale − 2·wall_margin`、`CAV_H·scale ≤ shell 内净高`；违反按比例缩 cavity | parent L47-51 |
| (—) | constraint | — | — | inequality | drawer 行程不超 rail：`drawer_travel·scale ≤ RAIL_DEPTH − margin` 且 ≤ tray 仍留腔内 `expect_overlap ≥0.10`；违反缩 travel | drawer L75, L463 |
| (—) | constraint | — | — | inequality | 闭合门覆盖 cavity opening：door W/H ≥ cavity opening + 边距（门 footprint 全覆腔口）；违反放大门或缩 cavity | parent L55-59 |
| (—) | constraint | — | — | inequality | rack 清 turntable：`RACK_BOTTOM_Z − (TT_Z + plate_top) ≥ 0.03`；违反抬高 rack 或拒绝（rack×rotating 组合）| rack L603-609 |
| (—) | constraint | — | — | conditional | door=drawer 时 turntable.parent=drawer & turntable.origin=tray-local；door≠drawer 时 parent=body & origin=cavity floor center（在 resolve 内解析 parent/origin）| drawer L321-329 |
| (—) | constraint | — | — | conditional | door=drawer × turntable=flatbed 时固定 flatbed 玻璃改挂 drawer tray（随抽屉平移）而非 body cavity floor（见 §9 矩阵）| drawer / flatbed 接口推断 |

palette_style 候选（每 seed 采一套，**不计入 slot_choice**；基线取 parent 材质，其余为家电真实配色外推）：
| palette_style | 机身 shell | 门 / 控件 | cavity / 旋钮 | 来源 |
|---|---|---|---|---|
| pale_blue_gray（基线，默认）| 浅蓝灰 (0.70,0.76,0.80) | 炭黑门 (0.17,0.18,0.20) + 蓝灰握把 | 暗腔 (0.09,0.09,0.10) + 玻璃盘 (0.60,0.64,0.66) | parent 全套材质 |
| white_appliance | 白机身 | 黑门框 + 银握把 | 暗腔 + 灰玻璃 | 家电白外推 |
| black_appliance | 黑机身 | 黑门 + 银握把 | 暗腔 + 暗玻璃 | parent CHARCOAL/NEAR_BLACK 外推 |
| stainless_steel | 不锈钢灰机身 + 黑门玻璃 | 钢握把 + 黑控件 | 暗腔 + 钢转盘 | parent FOOT/HUB gray 外推 |
| cream_retro | 米白复古机身 | 铬握把 + 米色控件 | 暗腔 + 玻璃盘 | 复古配色外推 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / 行程 / 角度 / clearance，**绝不改变 door_mechanism / turntable / control / interior_rack 的拓扑**。

## Multiplicity / Copy Logic

- **无小类级可变 multiplicity 轴**：核心结构由固定 named slots（door_mechanism / turntable / control / interior_rack）表达，不暴露 `*_count` 形成小类级功能复制轴（整机只有 0/1 个 rack，none vs 1 shelf 已由 Slot D enum 表达；只有 1 个门、1 个 turntable）。
- **存在 module-local 固定 / 半参数化阵列 visual（非小类级 multiplicity 轴，**不进 slot_choice**）**：
  - turntable 的 `coupler_rib_{k}`：源用 `for k in range(3)` 等角发射 3 根肋（parent L256-267），固定 N=3（rotation 证明用，随 rotating module 固定）。
  - body 的 `foot_{i}`：源用 `for i,(fx,fy)` 发射 4 个脚（parent L195-203），固定 N=4。
  - drawer 的 `guide_rail_{i}` / `tray_lip_{i}`：源用 `for x_sign in [-1,1]` 发射 2 个（drawer L202-209, L268-275），固定 N=2。
  - rotary_dials 的 knob：源用 `for (name,z) in KNOB_SPECS` 发射 2 个旋钮（dials L337，KNOB_SPECS 固定 2 项），随 rotary_dials module 固定 N=2。
  - touch_glass 的 `touch_mark_{i}`：源用 `for dy` 发射 3 道标记（touch L211-217），固定 N=3。
  - **interior_rack=shelf 的 wire-grid `cross_wire_{i}` / `long_wire_{i}`**：源用 `for i in range(N_CROSS_WIRES=10)` / `for i in range(N_LONG_WIRES=4)` + 共享 `_rack_wire(length,along)` helper + 等距 placement 发射（rack L367-384）。这是 **rack 模块的内部填充密度**（controlled local parameterization 范畴：cross ∈ ~[6,14]、long ∈ ~[3,6]），**不是小类级功能复制轴**——它不改变拓扑等价类（仍是"1 个 shelf_rack part + 1 个 FIXED joint"），仅改丝数装饰密度，故**不编入 slot_choice**，作为 conditional@shelf 的 module-internal 参数随 rack 一起 clamp。
- 这些都是 module-local 固定 / 半参数化多份 visual（肋 / 脚 / 滑轨 / 旋钮 / 标记 / 网格丝），按 module 而非 multiplicity 轴声明——clamp 不存在"任意 N 个门 / N 个 turntable"的真实产品域。copied object 用共享 helper / 循环发射、绝对式等距 / 等角 placement，无独立 joint（FIXED 装饰 inline visual，Rule 1；rotary_dials 的 2 旋钮例外是真有 2 个 REVOLUTE，但 N=2 固定属 module 定义不属可变轴）。

## 拓扑多样性审计

总组合数：door_mechanism(4) × turntable(2) × control(3) × interior_rack(2) = **48**（含若干兼容 gating，见 §9；gate 后合法组合 ≈42-48）。

仅 door_mechanism(4) × control(3) = **12 ≥ 10**（已达机械门控），其中 joint 拓扑差异来自：door 的 {竖轴 REVOLUTE / 横轴 REVOLUTE×2 / PRISMATIC} × control 的 {无 joint / +2 REVOLUTE / 无 joint}；叠 turntable(2)（是否有 CONTINUOUS joint）→ 24；叠 interior_rack(2)（是否有 FIXED part）→ 48。

理由：door_mechanism 提供 4 类真正的 joint 拓扑差异（竖轴 REVOLUTE / 底横 REVOLUTE / 顶横 REVOLUTE / PRISMATIC + part 改名 + turntable reparent），turntable 提供"是否有 CONTINUOUS joint + 是否有 turntable part"差异，control 提供"是否有 2 个 REVOLUTE 旋钮 part"差异，interior_rack 提供"是否有 FIXED rack part"差异。**四轴都进 `slot_choices_for_seed` 的 tuple**（`("door_mechanism",m)`、`("turntable",m)`、`("control",m)`、`("interior_rack",m)`），drawer 的 part 改名 + turntable reparent 与 hinge 三向天然区分。door×control 单独即 12 distinct，叠 turntable×rack 后 48，远超 ≥10。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 四个 named slot（door_mechanism / turntable / control / interior_rack），经兼容矩阵合法化（drawer×flatbed 玻璃归属、rack×drawer 干涉、rack×rotating 清隙），再 uniform 各连续 scale（解析 conditional：door_open_angle 仅 REVOLUTE 门、drawer_travel 仅 drawer、knob_size 仅 rotary_dials、rack_wire_density 仅 shelf），采 palette_style。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（重点看：drawer 拉出 turntable 随动 / 三向门开合姿态 / 旋钮旋转 / rack 清 turntable / flatbed 固定地板）。


Controlled local parameterization：见 §参数表的 body_width/depth/height_scale（independent）+ cavity_inset_scale（derived）+ door_open_angle_scale（@REVOLUTE 门）/ drawer_travel_scale（@drawer）/ knob_size_scale（@rotary_dials）/ rack_wire_density（@shelf）（conditional）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采四 named slot（解析 conditional 范围 + turntable parent/origin 派生 + drawer×flatbed 玻璃归属）→ 采 independent body scale → 派生 cavity_inset（随 body scale）+ door/panel 尺寸 → 用四条 inequality（cavity 在 footprint 内、drawer 不超 rail、闭合门覆腔口、rack 清 turntable）投影 / 回缩。跨部件依赖（cavity vs body、drawer travel vs rail、门 vs 腔口、rack vs turntable）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 door/drawer 铰链 origin、turntable reparent、knob/rack 接口或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 四 named slot（door/turntable/control/rack），经兼容矩阵，再解析 conditional scale + turntable parent，再 uniform 各 scale，采 palette_style | slot_choices_for_seed 含 `("door_mechanism",m)`/`("turntable",m)`/`("control",m)`/`("interior_rack",m)` 且与 build 一致 |
| compatibility matrix | (1) **drawer × flatbed**：drawer 把活动地板归到抽屉——flatbed 固定玻璃地板须改挂 drawer tray（随抽屉平移）而非 body cavity floor（否则抽屉拉出后玻璃地板留在 body 内、与抽屉脱节）；rotating 已有此 reparent 范式（drawer L321-329），flatbed 沿用：door=drawer → flatbed_glass 挂 drawer。 (2) **rack(shelf) × drawer**：rack 的 `rack_support_{l,r}` 与 `body_to_rack` FIXED 锚在 body 固定 cavity 壁；drawer 拉出时托盘/turntable 平移，rack 仍固定在 body 腔内——须验 rack 不与拉出的 drawer tray/turntable 干涉（rack 在 mid-level RACK_BOTTOM_Z，drawer tray 在腔底，竖向有隙）；若冲突则 door=drawer 时 gate interior_rack=none。初版**保守 gate：door=drawer 时 interior_rack=none**（rack×drawer 未抽检，避免悬空/干涉）。 (3) **rack(shelf) × rotating**：rack 须清 turntable 下方 ≥0.03（rack L603-609）；body scale 把 cavity 压扁时若 rack 清隙不足 → 抬高 rack 或 gate rack=none（conditional@body_height）。 (4) **rotary_dials × 各 door**：旋钮锚在 body 右栏 panel 面，与 door 在不同面，组合风险低（正交，全合法）。 (5) door_mechanism × turntable parent 派生：drawer→turntable.parent=drawer，其余→parent=body（resolve 内解析，非 gate 而是派生）。 | 无 floating / collision / drawer 拉出玻璃地板脱节 / rack 撞 drawer / rack 撞 turntable / 门不覆腔口 / 旋钮重叠 |
| controlled local variation | 3 independent body scale + 1 derived cavity + 4 conditional（door_angle/drawer_travel/knob_size/rack_density），每 build 统一；conditional 随 slot 解析 | 比例变化不破坏门/抽屉铰链 origin、turntable reparent、knob/rack 接口、闭合姿态、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 QC（三向门开合 / drawer 拉出 turntable 随动 / 旋钮旋转 / flatbed 固定 / rack 清隙）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| door_mechanism | 4 | yes | yes | side/drop/top REVOLUTE 三向 + drawer PRISMATIC（part 改名 + turntable reparent）|
| turntable | 2 | yes | no | rotating(+CONTINUOUS part) / flatbed(body visual 无 joint)；降级理由见 Slot B 注 |
| control | 3 | yes | yes | membrane / touch_glass（visual 无 joint）+ rotary_dials(+2 REVOLUTE part)|
| interior_rack | 2 | yes | no | none / shelf(+FIXED part)；0/1 可选层，编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 `("door_mechanism",m)`/`("turntable",m)`/`("control",m)`/`("interior_rack",m)`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 把各 scale clamp 到声明范围；door_open_angle/drawer_travel/knob_size/rack_wire_density 为 conditional 随 door/control/rack 解析；四条 inequality（cavity 在 footprint 内、drawer 不超 rail、门覆腔口、rack 清 turntable）在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（drawer×flatbed 玻璃改挂 drawer；保守 gate door=drawer×interior_rack=none；rack×rotating 清隙不足时抬 rack 或 gate none）
- door=drawer 时 `turntable_spin.parent=drawer`、origin=tray-local；door≠drawer 时 parent=body、origin=cavity floor center（resolve 内派生，build 一致）
- 连续 scale clamp 后不破坏 door/drawer 铰链 origin / turntable reparent / knob / rack 接口 / 闭合姿态 / module-local 阵列
- 关键 joint：
  - side_hinge `door_hinge` REVOLUTE axis≈(0,0,−1)（abs(axis[2])>0.99）
  - drop_down `door_hinge` REVOLUTE axis≈(1,0,0)（abs(axis[0])>0.99、y/z≈0）
  - top_hinge `door_hinge` REVOLUTE axis≈(−1,0,0)（abs(axis[0])>0.99、y/z≈0）
  - drawer `drawer_slide` PRISMATIC axis≈(0,−1,0)（abs(axis[1])>0.99）
  - rotating `turntable_spin` CONTINUOUS axis≈(0,0,1)、无 lower
  - rotary_dials `{name}_dial` REVOLUTE axis≈(0,−1,0)、0..rad(270)
  - shelf `body_to_rack` FIXED
- flatbed 时断言无 `turntable` part、无 `turntable_spin` joint（照搬 flatbed run_tests 只测 flatbed_glass，不取 turntable）
- membrane/touch_glass 时断言无 `{name}_dial` joint、无 knob part
- captured overlap：element-scoped `allow_overlap`（drawer 的 `outer_shell`↔`drawer_tray` / `outer_shell`↔`tray_lip_{i}`，照搬 drawer L438-450）
- copied object 遵循 `coupler_rib_{k}` / `foot_{i}` / `guide_rail_{i}` / `tray_lip_{i}` / `touch_mark_{i}` / `cross_wire_{i}` / `long_wire_{i}` 命名 + 绝对式等距/等角 placement + Rule 1（无独立 joint；rotary 2 旋钮例外有 joint）
- grandfather：所有 hinge/slide/seat captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守
- 旋转/平移证明：rotating off-axis `coupler_rib_0` 旋转后 y-center 位移 >0.015；rotary `{name}_pointer` 旋转后 x-center 位移 >0.010；drawer 拉出后 drawer y-center 位移 >0.10 且 turntable 随动

## Reject cases

- 把 door 当普通 hinge 但 drawer 仍用 REVOLUTE / 不改 part 名 / 不 reparent turntable → 违反 drawer 候选的"PRISMATIC + part 改名 `drawer` + turntable parent=drawer"拓扑（drawer run_tests 显式测 PRISMATIC + turntable 随动）。
- door=drawer × turntable=flatbed 时把固定玻璃地板留在 body cavity floor → 抽屉拉出后地板与抽屉脱节、悬空；须随 drawer reparent（见 §9 矩阵）。
- door=drawer × interior_rack=shelf 未 gate 直接组合 → rack support 锚 body 固定壁、与拉出的抽屉托盘/turntable 干涉风险（未抽检）；初版保守 gate door=drawer→rack=none。
- turntable=flatbed 仍发射 `turntable` part / `turntable_spin` joint → 违反 flatbed 候选的"固定 body visual 无 joint"拓扑（flatbed run_tests 不取 turntable）。
- control=membrane/touch_glass 仍发射 `{name}_dial` REVOLUTE 或 knob part → 违反这两候选的"控件是 body visual 无 joint"拓扑。
- 门 rest pose 设成开角 / 抽屉设成拉出而非 q=0 闭合 → current-pose 与 viewer 目检不符（所有样本闭合姿态 lower=0、抽屉收回贴前面）。
- door_hinge / drawer_slide / turntable_spin origin 放在腔中心或任意点而非真实铰缘 / 滑轨 / floor center 硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- cavity scale 过大致 cavity 超出 body footprint / 门不覆腔口 → §7 inequality FAIL；须按比例缩 cavity 或放大门。
- drawer_travel 过大超 rail 或托盘全脱腔（`expect_overlap` <0.10）→ §7 inequality FAIL；缩 travel。
- rack 清 turntable 不足（<0.03，body 压扁时）→ §7 inequality FAIL；抬 rack 或 gate rack=none。
- 给 drawer tray↔shell captured overlap 补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap（照搬 drawer）。
- 把连续尺寸 / 颜色 / 材质（palette_style / body scale / wire 密度）当新 candidate 塞进 slot → 不是结构差异。
- 把 toaster-oven / built-in-oven / 空气炸锅语义混入（无旋转盘 / 嵌墙 / 无右控制栏）→ 出类，本类是台面带门带转盘微波炉。

## 与相邻类别的边界

- 不该混入：**烤面包炉 / 小烤箱（toaster oven）**——前玻璃门 + 加热管 + 烤架托盘，无旋转 turntable、无微波右控制栏布局；本类核心身份是 cooking cavity + 旋转玻璃盘 + 右侧 control panel。
- 不该混入：**嵌入式 / 壁挂烤箱（built-in oven）**——嵌墙大型、无四脚台面 footprint、门多为单一下翻 + 内多层烤架；已有独立 slug `built_in_oven`（安装方式 / 尺度不同）。
- 不该混入：**空气炸锅 / 电饭煲 / 其他台面厨电**——非"前门 + 旋转盘 + 右控制栏"的箱体腔加热形态（开盖 / 旋钮锅 / 不同主运动 spine）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **slot 抽象容纳 door↔drawer part+joint-type swap**：door_mechanism 槽同时换 part 名（door/drawer）、joint 类型（door_hinge REVOLUTE / drawer_slide PRISMATIC）与 turntable parent（drawer 时 reparent）——是否接受把"part 改名 + joint 类型变 + 下游 reparent"作为单一 slot 的三候选 + 一抽屉候选；(2) **turntable parent 由 door_mechanism 派生**（drawer→parent=drawer）作为 resolve 内派生而非 gate；(3) **drawer × flatbed**：固定玻璃地板改挂 drawer tray（随抽屉平移）的兼容裁决是否接受；(4) **保守 gate door=drawer × interior_rack=none**（rack×drawer 未抽检）是否接受还是要求抽检后放开；(5) turntable 仅 2 candidate、interior_rack 仅 2 candidate（含 none）的降级理由是否接受；(6) Topology target 48<300 的说明是否接受（本小类真实结构上限）；(7) rack 内部 wire-grid 丝数作 module-internal conditional 参数（不进 slot_choice）是否符合 multiplicity 审计期望；(8) palette_style 5 套（基线 pale_blue_gray + white/black/stainless/cream 外推）是否合适。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- **共享 helper**：`_shell_solid()`（chamfered shell + cavity cut + control recess，drawer 时 cavity cut 加深；按 body scale 参数化）、`_door_solid()`（门 mesh，按 door_mechanism 切 origin：side=左前缘 / drop=底心 / top=顶心）、`_drawer_front_solid()`（drawer 前板 mesh）、`_knob_mesh()`（KnobGeometry skirted，rotary_dials 用；注意 KnobGeometry +Z base、center=False，visual rpy=(π/2,0,0) 转 −Y 外凸）、`_rack_wire(length,along)`（shelf 网格丝，N 复用同一 helper）。
- **door_mechanism = 单 slot 多形态**：四候选共享门 part（side/drop/top 用同 `door` part + `_door_solid` 仅换 origin + hinge axis；drawer 用 `drawer` part + `_drawer_front_solid` + PRISMATIC）。模板按 door_mechanism 选 part 名 / mesh helper / joint 类型 / hinge origin / axis。
- **turntable reparent 派生**：`resolve_config` 内根据 door_mechanism 决定 `turntable_spin.parent`（drawer→drawer、其余→body）与 origin（drawer→tray-local (0,TT_Y_LOCAL,tray_top_z)、其余→cavity floor center (TT_X,TT_Y,TT_Z)）；flatbed 时不发 turntable，drawer×flatbed 时 flatbed_glass 改挂 drawer tray。
- **captured 接口 allow_overlap**：`run_microwave_tests` 里 drawer 候选补 element-scoped `allow_overlap(outer_shell, drawer_tray)` + `allow_overlap(outer_shell, tray_lip_{i})`，照搬 drawer L438-450。其余候选（hinge 门 / turntable hub / knob / rack）多为 `expect_gap`/`expect_within`/`expect_overlap` 自洽，按各样本 run_tests 段补。
- **conditional 范围解析顺序**：先采 door_mechanism / turntable / control / interior_rack → 经兼容矩阵（drawer×flatbed reparent、door=drawer→rack=none、rack×rotating 清隙）→ 解析 turntable parent/origin + door_open_angle（仅 REVOLUTE 门）/ drawer_travel（仅 drawer）/ knob_size（仅 rotary）/ rack_wire_density（仅 shelf）→ 采 independent body scale → 派生 cavity_inset + 门/panel 尺寸 → 投影四条 inequality。
- **参考模板**：选运动拓扑相近的——root chassis + parallel children + 可选 REVOLUTE/PRISMATIC child + 互斥 slot（`cushion` 的 base + lid REVOLUTE/PRISMATIC + interior 互斥 + multiplicity / `clamp` 的 frame root + screw PRISMATIC + 可选 REVOLUTE pad/lever + 三轴正交）。microwave 的 body→door REVOLUTE/PRISMATIC + body→turntable CONTINUOUS（drawer 时 reparent）+ body→knob REVOLUTE + body→rack FIXED 与之同构；尺度中等（body ~0.52×0.38×0.32m），joint origin 须精确落真实缘 / 滑轨 / floor 硬件（≤0.015m baseline）。
- **part 改名 + reparent 注记**：drawer 候选是本模板唯一既改 part 名（door→drawer）又改下游 joint parent（turntable→drawer）的轴，模板侧务必在 build 时按 door_mechanism 分支处理 part 名与 turntable parent，并在 run_tests 按候选断言对应 joint 类型 / part 存在性。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | root + A/B/C/D 基线 | body + side_hinge + rotating + membrane + none | rec_model-a-stylized-countertop-microwave-oven-appro_...b2de7afe（parent）| `_shell_solid` L92-115 / `_door_solid` L118-138 / body 装配 L145-203 / `door` part L206-233 / `door_hinge` REVOLUTE −Z L237-245 / `turntable` part + `coupler_rib` 循环 L248-274 / `turntable_spin` CONTINUOUS L276-284 / `control_panel` L187-192 / `foot_{i}` 循环 L195-203 | 共享 body/door/shell helper + side_hinge 基线 + rotating turntable + membrane control + 旋转证明范式 |
| S2 | A | drop_down | rec_microwave_var_door_drop_down | `_door_solid` 底心 L120-140 / `door_hinge` REVOLUTE +X 底前缘 L244-255 / 顶横 handle L221-240 | 横轴下翻门（底铰 REVOLUTE +X）|
| S3 | A | top_hinge | rec_microwave_var_door_top_hinged | `_door_solid` 顶心 L129-149 / `door_hinge` REVOLUTE −X 顶前缘 L254-264 | 横轴上掀门（顶铰 REVOLUTE −X）|
| S4 | A | drawer_prismatic | rec_microwave_var_door_drawer | `_drawer_front_solid` L130-152 / `drawer` part + tray + `tray_lip_{i}` L231-275 / `guide_rail_{i}` L202-209 / `drawer_slide` PRISMATIC −Y L278-288 / turntable parent=drawer L321-329 / allow_overlap L438-450 | 抽屉门（PRISMATIC + part 改名 + turntable reparent + captured overlap 范式）|
| S5 | B | flatbed | rec_microwave_var_turntable_flatbed | `flatbed_glass` body visual L183-188 / run_tests 不取 turntable L355-383 | 固定玻璃地板（body visual 无 joint，退化 turntable）|
| S6 | C | rotary_dials | rec_microwave_var_control_rotary_dials | `_knob_mesh` KnobGeometry L166-184 / `power_knob`/`timer_knob` part + `{name}_pointer` L337-359 / `{name}_dial` REVOLUTE −Y 0..270° L361-374 | 旋钮控制（2 独立 part + 2 REVOLUTE，pointer 旋转证明）|
| S7 | C | touch_glass | rec_microwave_var_control_touch_glass | `touch_glass_panel` + `touch_panel_backing` + `touch_mark_{i}` body visual L193-217 / 薄玻璃断言 L386-410 | 触控玻璃面（body visual 无 joint）|
| S8 | D | shelf | rec_microwave_var_rack_shelf | `_rack_wire` helper L160-167 / `shelf_rack` part + frame + `cross_wire_{i}`×10 + `long_wire_{i}`×4 L335-384 / `rack_support_{l,r}` L240-251 / `body_to_rack` FIXED L388-394 / rack 清 turntable 断言 L603-609 | 中层 wire-grid 架（FIXED part + 壁挂 ledge + module-internal 网格丝循环）|
