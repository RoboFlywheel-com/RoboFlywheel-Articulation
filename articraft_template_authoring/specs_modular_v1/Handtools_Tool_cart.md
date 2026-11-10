# tool_cart (rolling tool cart / mobile tool chest) — Modular Spec

> 来源小类：`picture/Handtools/Tool cart`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Handtools__Tool_cart.md`。
> **"tool cart" 在此 = 带轮的滚动工具车 / 移动工具柜（rolling roller cabinet / mobile tool chest），不是固定书架 / 货架（shelf）、不是办公桌 / 工作台（desk / workbench）、不是手推平板车（flatbed platform cart）。**
> 结构家族 = 一个融合的 `cabinet_frame` 碳柜（root，`carcass_shell` + `side_pegboard` visuals）站在四个脚轮上，后部一个固定 `push_handle`（`handle_frame` + `handle_grip`，joint `frame_to_handle` FIXED）。前储物面 / 顶台面是 Slot A，脚轮类型是 Slot B；**抽屉栈是 multiplicity 轴**。共享运动学：抽屉沿 +Y PRISMATIC 拉出、脚轮绕 +Z CONTINUOUS 转向 + 轮绕 +X CONTINUOUS 滚动。坐标约定全 source 一致：+Z up，+Y 朝前（抽屉面 / 握把），+X 右；carcass 地板坐于 `FLOOR_Z = CASTER_GAP` 使轮落 z=0。
>
> **同步状态**：本 spec 引用的 9 个 5 星样本（1 个 parent + 8 个 fork 槽位 / multiplicity 变体）已同步进本仓库 `articraft_data/data/records/`，rating=5（按上游 curation；本地 record.json 的 rating 字段在同步副本里为 null，不影响采纳）。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（逐一核对、全文读完）。引用以 part / joint / helper **名字** 为准（`cabinet_frame`/`carcass_shell`/`side_pegboard`、`push_handle`/`handle_frame`/`handle_grip`/`frame_to_handle`、`drawer_{i}`/`drawer_face_{i}`/`frame_to_drawer_{i}`、`_drawer_mesh`/`_drawer_face_centers`/`_drawer_band_top`、`cabinet_door`/`door_panel`/`frame_to_door`、`shelf_{i}`/`bay_divider`/`_shelf_mesh`/`_shelf_z_positions`、`guard_rail`/`_guard_rail_mesh`、`caster_fork_{i}`/`caster_wheel_{i}`/`frame_to_caster_{i}`/`caster_to_wheel_{i}`、`swivel_fork_{i}`/`fixed_bracket_{i}`/`frame_to_bracket_{i}`/`bracket_to_wheel_{i}`、`brake_lever_{i}`/`fork_to_brake_{i}` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `tool_cart` |
| template path | `agent/templates/Handtools_Tool_cart.py` |
| test path (optional) | `tests/agent/test_tool_cart_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `multiplicity`（主轴 = `drawer_count` 抽屉栈 N 复制；外加固定 named slots: storage_module + caster 层在 `cabinet_frame` 上 parallel children；effectively mixed，但唯一可变 count 轴是 drawer_count → 归 `multiplicity`）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（1 parent + 8 fork 变体：3 storage_module 槽位 + 2 caster 槽位 + 1 cabinet_door + 2 drawer_count N 样本；均 converged，compile success、含 PRISMATIC + CONTINUOUS（+ 部分 REVOLUTE）非 fixed joint、workbench-only）|
| read_count | 9（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、run_tests 的 allow_overlap/allow_isolated_part/check 段）|
| read_scope | all 5-star samples in this category（parent 母资产 001.png 覆盖 drawer_stack × all_swivel 基线；变体为 fork 子，单轴变化）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 9/9 全部被采纳，无未采用样本（下游非 modular 文件 `rolling_toolbox_with_telescoping_handle.py` / `platform_cart.py` 与本类无关，已忽略）|

阅读要点（用于槽位分解，**关键拓扑发现**）：
- **9 个样本共享同一拓扑骨架**：root `cabinet_frame`（`carcass_shell` 黑钢柜 + `side_pegboard` 红洞洞板 fused visual）+ 固定 `push_handle`（`handle_frame` U-loop + `handle_grip` 红胶套，`frame_to_handle` FIXED origin=(0,0,0)）+ N 个 `drawer_{i}` PRISMATIC 抽屉 + 4 个脚轮（fork CONTINUOUS swivel + wheel CONTINUOUS roll）。joint 计数随 drawer_count 与 caster 类型变化（11-17 非 fixed joint）—— 抽屉栈是身份的主多重性轴。
- **抽屉拷贝逻辑（multiplicity 主轴，3 个 N 样本逐一核对）**：n3（`NUM_DRAWERS=3`、`DRAWER_HEIGHTS=(0.150,0.150,0.150)`、loop `for i in range(NUM_DRAWERS)` L480、`CAB_H=0.640`）/ parent（5：`DRAWER_HEIGHTS=(0.072,0.072,0.072,0.150,0.150)` 三浅二深、loop `for i, zc in enumerate(face_centers)` L480、`CAB_H=0.640`）/ n7（`N_DRAWERS=7`、`DRAWER_HEIGHTS=tuple([0.098]*N_DRAWERS)` L66、loop `for i, zc in enumerate(face_centers)` L481、`CAB_H=0.820` 升高以容纳更高栈）。每抽屉 = `drawer_{i}` part + `drawer_face_{i}` red 面板（凹指拉 + 黑中空盒身）+ `frame_to_drawer_{i}` PRISMATIC axis=(0,1,0) `MotionLimits(effort=60, velocity=0.30, lower=0, upper=DRAWER_TRAVEL=0.300)`。band 高度由 `_drawer_band_top()` / `_drawer_face_centers()` 自动适配（从 band top 向下走，每抽屉减 `DRAWER_HEIGHTS[i]+DRAWER_GAP`），共享 `_drawer_mesh(index)` helper。**这是 copy-logic 源**（见 §8）。
- **Slot A storage_module**（改前储物面 / 顶台面；drawer_stack 候选本身即 multiplicity 载体）：
  - **drawer_stack**（parent 基线）：满抽屉栈，是 multiplicity 轴本体（N∈[2,9]）。
  - **cabinet_door**（door 变体）：下柜 bay 加一扇侧铰柜门（`cabinet_door` part / `door_panel` visual / `frame_to_door` REVOLUTE axis=(0,0,1) 左缘竖铰、`lower=0 upper=DOOR_OPEN_ANGLE=1.50`），**仅保留上方 3 浅抽屉**（`DRAWER_HEIGHTS=(0.072,0.072,0.072)`），下方两深抽屉空间换成门后 bay。
  - **open_shelf**（openshelf 变体）：下 bay 开放，加 `bay_divider` inline visual + `SHELF_COUNT=2` 个 `shelf_{i}` inline 固定隔板（loop `for i in range(SHELF_COUNT)` via `_shelf_z_positions()`，**FIXED 非移动 visual，无独立 joint，Rule 1**），**仅保留上方 3 浅抽屉**；helpers `_shelf_mesh` / `_bay_divider_mesh`。
  - **worktop**（worktop 变体）：顶台面换成平实台面 + 薄周边唇（fused 进 `_carcass_mesh`，替代凹陷 tray basin，**无额外 part / joint**），**保留全 N 抽屉栈**。
  - **rail_shelf**（railshelf 变体）：顶 utility shelf 加管状周边 guard rail（`guard_rail` inline visual on `cabinet_frame`，helper `_guard_rail_mesh`：4 角柱 `for i in range(4)` + 横杆，**无独立 joint，Rule 1**），**保留全 N 抽屉栈** + 新 `STEEL` 材质。
- **Slot B caster**（脚轮，挂在 `cabinet_frame` 地板下）：
  - **all_swivel**（parent 基线）：4 个相同后拖式转向脚轮，`caster_fork_{i}`/`caster_wheel_{i}`，`frame_to_caster_{i}` CONTINUOUS Z（转向）+ `caster_to_wheel_{i}` CONTINUOUS X（滚动）；helpers `_caster_fork_mesh` / `_caster_wheel_mesh`。每脚轮 2 joint → 8 caster joint。
  - **mixed_swivel_fixed**（mixedcaster 变体）：前 2 swivel（`swivel_fork_{i}`/`swivel_wheel_{i}`：`frame_to_swivel_{i}` CONTINUOUS Z + `swivel_to_wheel_{i}` CONTINUOUS X）+ 后 2 rigid（`fixed_bracket_{i}`/`fixed_wheel_{i}`：`frame_to_bracket_{i}` FIXED + `bracket_to_wheel_{i}` CONTINUOUS X，**无 trailing offset**）；两个 `for i in range(2)` loop；helper `_fixed_bracket_mesh`。这是常见车间布局（2 转向 + 2 定向）。
  - **brake_caster**（brakecaster 变体）：4 个 swivel 脚轮，每个加一个脚踏刹车杆（`brake_lever_{i}` part，`fork_to_brake_{i}` REVOLUTE axis=(1,0,0) **parent=fork** child=brake_lever、`lower=0 upper=BRAKE_ENGAGE_ANGLE=0.55`），**每脚轮 3 joint → 12 caster joint**；helpers `_brake_lever_mesh` / `_caster_wheel_meshes`（pneumatic tire + rim 双 visual）。
- **palette**：全样本同色族（`RED=(0.74,0.07,0.07)` 抽屉 / `BLACK=(0.10,0.10,0.11)` 柜壳 / `DARK=(0.16,0.16,0.18)` 把手 & fork / `RUBBER=(0.09,0.09,0.10)` 轮 / `GRIP_RED=(0.70,0.10,0.10)` 握把套；railshelf/door 另有 `STEEL=(0.55,0.56,0.58)`）。→ 4-6 套 colorway（见 §7 palette_style）。

## 核心身份

一台**带轮的滚动工具车 / 移动工具柜（rolling tool cart / mobile tool chest）**：一个融合的黑钢柜体 `cabinet_frame`（root，`carcass_shell` 中空箱 + 红色洞洞板 `side_pegboard` 侧挂板），站在四个黑色脚轮上，柜后 / 右上角固定一只暗色管状推手 `push_handle`（倒 U loop + 红胶握把）。柜体前面是储物面：**默认是一叠红色抽屉**（N 个 `drawer_{i}`，红面板 + 凹指拉 + 黑中空盒身，每个沿 +Y PRISMATIC 直拉出，行程 ~0.30 m），可替换为下柜带侧铰门（保留上方浅抽屉）、开放隔板 bay（保留上方浅抽屉）；柜顶可以是凹陷工具托 tray（默认）、平实台面（worktop）或带周边护栏的 utility shelf（rail_shelf）。底部四脚轮可全转向、两转向两定向、或带脚刹。活动语义恒为：**每个抽屉沿 +Y PRISMATIC 拉出**（主多重性轴）+ **脚轮绕 +Z CONTINUOUS 转向**（转向）+ **轮绕 +X CONTINUOUS 滚动**；可选 **柜门绕侧竖 +Z REVOLUTE 开合** / **脚刹绕 +X REVOLUTE 踩下**。`push_handle` 始终 FIXED。默认成熟域：storage_module × caster × 抽屉数 N∈[2,9] 笛卡尔积的单台手动滚动工具柜。

不该混入：
- **固定书架 / 货架（shelf / shelving unit）**——无轮、无柜体抽屉栈、无推手，是固定立架；本类核心身份是**带脚轮可推动 + 抽屉 / 柜门储物**，缺脚轮 + 推手 + 柜身抽屉即出类。
- **办公桌 / 工作台（desk / workbench）**——大平台面 + 桌腿，主体是工作平面而非储物柜，无 caster 转向 / 滚动机构（若有抽屉也是桌下吊柜形态，且无推手）；本类是工具**柜**车而非桌。
- **手推平板车 / 推车（flatbed / platform cart / trolley）**——纯平板 + 轮 + 推手，无柜体抽屉 / 柜门储物面（source map 明确忽略的 `platform_cart.py` 即此）；本类必须有柜身储物。
- **滚动工具箱 + 伸缩拉杆（rolling toolbox w/ telescoping handle）**——便携箱体 + 伸缩拉杆 + 2 轮拖行，不是 4-caster 推动的工具柜（source map 明确忽略的 `rolling_toolbox_with_telescoping_handle.py` 即此）。

## 槽位 + 候选模块表

> **建模注记**：tool_cart 是 **root `cabinet_frame`（dispatch storage_module 主壳 / 顶台面几何 + pegboard）+ 固定 `push_handle`（FIXED）+ N 个抽屉（PRISMATIC，multiplicity 主轴）+ 4 个脚轮（Slot B）parallel children**。
> - **Slot A（storage_module）改前储物面 + 顶台面**：drawer_stack（满抽屉栈，是 multiplicity 载体）/ cabinet_door（下 bay 加 REVOLUTE 门 + 仅 3 浅抽屉）/ open_shelf（下 bay 加 FIXED 隔板 + 仅 3 浅抽屉）/ worktop（顶台面平台化，保留全 N 栈）/ rail_shelf（顶台面加护栏，保留全 N 栈）。
> - **Slot B（caster）改脚轮 part 树 + joint 拓扑**：all_swivel（4×2 joint）/ mixed_swivel_fixed（前 2 swivel 4 joint + 后 2 fixed 2 joint）/ brake_caster（4×3 joint）。
> - **drawer_count（N）是 multiplicity 主轴**：drawer_stack / worktop / rail_shelf 候选随 N 展开全 [2,9]；cabinet_door / open_shelf 候选消耗下 bay → 只在 bay 上方保留 3 浅抽屉（与 drawer_count 联动，见 §8 / §9 兼容矩阵）。

### Slot A：storage_module（前储物面 + 顶台面 —— root 主壳几何 + 抽屉栈 / 门 / 隔板 / 台面）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| drawer_stack（基线 + multiplicity 载体） | parent rec_..._1e586d5a | `_drawer_mesh` L232-272 / `_drawer_face_centers` L108-117 / `_drawer_band_top` L102-105 / drawer loop L478-502（`for i, zc in enumerate(face_centers)`）/ `_carcass_mesh`(凹 tray) L123-202 | eligible if compatible | 满抽屉栈：N 个 `drawer_{i}` red 面板（凹指拉）+ 黑中空盒身，PRISMATIC +Y；顶 = 凹陷工具托 tray（basin + socket pockets）；**drawer_count multiplicity 轴本体**（n3 L480 `for i in range(NUM_DRAWERS)` / parent L480 enumerate / n7 L481 enumerate）|
| cabinet_door | rec_tool_cart_var_door | `cabinet_door` part L574-580 / `door_panel` visual L575 / `frame_to_door` REVOLUTE L584-597 / `_cabinet_door_mesh` L290-? / `_door_opening` L131-145 / drawer L543（`for i in range(N_DRAWERS=3)`）| eligible if compatible | 下柜 bay 加一扇侧铰柜门（左缘竖铰，REVOLUTE axis=(0,0,1) origin=(hinge_x=-(CAB_W/2−SIDE_REVEAL), hinge_y=CAB_D/2, door_cz)，`lower=0 upper=1.50≈86°`）；**仅保留上方 3 浅抽屉**（`DRAWER_HEIGHTS=(0.072,0.072,0.072)` L67），下两深抽屉换门后 bay；STEEL 材质加入 |
| open_shelf | rec_tool_cart_var_openshelf | `_shelf_mesh` L310-339 / `_bay_divider_mesh` L342-355 / `_shelf_z_positions` L142-152 / shelf loop L538-545（`for i in range(SHELF_COUNT=2)`）/ drawer L575（`for i in range(NUM_DRAWERS=3)`）| eligible if compatible | 下 bay 开放：`bay_divider` inline + `SHELF_COUNT=2` 个 `shelf_{i}` inline 固定隔板（**FIXED 非移动 visual，无独立 joint，Rule 1**，前缘小上翻唇）；**仅保留上方 3 浅抽屉**（`DRAWER_HEIGHTS=(0.072,0.072,0.072)` L69）|
| worktop | rec_tool_cart_var_worktop | `_carcass_mesh`（平台 slab + 周边唇 fused，替代凹 tray basin）L173-219 / drawer loop L498-521（5）| eligible if compatible | 顶台面 = 平实 solid 台面 + 薄周边唇（fused 进 carcass，**无额外 part / joint**）；**保留全 N 抽屉栈**（纯顶台面 swap）|
| rail_shelf | rec_tool_cart_var_railshelf | `_guard_rail_mesh` L223-332（4 角柱 `for i in range(4)` L281-294 + 横杆 loop L297-322 + 球帽）/ `guard_rail` inline visual L557 / drawer loop L586-608（5）| eligible if compatible | 顶 utility shelf 加管状周边 guard rail（4 角柱 + 上 / 中横杆，`guard_rail` inline visual on `cabinet_frame`，**无独立 joint，Rule 1**）；**保留全 N 抽屉栈** + `STEEL=(0.55,0.56,0.58)` 材质 |

### Slot B：caster / wheel（脚轮，挂在 `cabinet_frame` 地板下，z=FLOOR_Z）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / joint 特征 |
|---|---|---|---|---|
| all_swivel（基线） | parent rec_..._1e586d5a | `_caster_fork_mesh` L346-402 / `_caster_wheel_mesh` L405-433 / caster loop L504-551（`for i, (cx,cy) in enumerate(caster_positions)`）| eligible if compatible | 4 个相同后拖式转向脚轮：`caster_fork_{i}`（CONTINUOUS Z 转向 `frame_to_caster_{i}` origin=(cx,cy,FLOOR_Z) axis=(0,0,1)）+ `caster_wheel_{i}`（CONTINUOUS X 滚动 `caster_to_wheel_{i}` origin=(0,−DROP,AXLE_Z) axis=(1,0,0)）；4×(swivel+roll)=8 joint；swivel post 咬入地板捕获 |
| mixed_swivel_fixed | rec_tool_cart_var_mixedcaster | `_fixed_bracket_mesh` L349-389 / swivel loop L559-597（`for i in range(2)`）/ fixed loop L601-635（`for i in range(2)`）| eligible if compatible | 前 2 swivel（`swivel_fork_{i}`/`swivel_wheel_{i}`：`frame_to_swivel_{i}` CONTINUOUS Z + `swivel_to_wheel_{i}` CONTINUOUS X，trailing offset）+ 后 2 rigid（`fixed_bracket_{i}`/`fixed_wheel_{i}`：`frame_to_bracket_{i}` FIXED + `bracket_to_wheel_{i}` CONTINUOUS X，origin=(0,0,AXLE_Z) **无 trailing offset**）；车间常见布局；4(swivel)+2(fixed)=6 joint |
| brake_caster | rec_tool_cart_var_brakecaster | `_caster_wheel_meshes`(tire+rim) L436-517 / `_brake_lever_mesh` L520-545 / caster loop L627-695（enumerate caster_positions）| eligible if compatible | 4 个 swivel 脚轮 + 每个脚刹杆：`frame_to_caster_{i}` CONTINUOUS Z + `caster_to_wheel_{i}` CONTINUOUS X + `fork_to_brake_{i}` REVOLUTE axis=(1,0,0) **parent=fork** child=`brake_lever_{i}` origin=(half_w+0.008,−DROP,boss_z) `lower=0 upper=0.55`；pneumatic tire + 辐条 rim 双 visual；4×3=12 joint |

## 槽位图（slot graph）

pattern: multiplicity（root `cabinet_frame` 持有 storage_module 主壳 / 顶台面几何 + pegboard；固定 `push_handle`（FIXED）+ N 个 `drawer_{i}`（PRISMATIC，**多重性主轴**）+ 4 个脚轮（Slot B）挂到 root；cabinet_door 加 1 REVOLUTE child，open_shelf/worktop/rail_shelf 加 inline FIXED visual）

```
cabinet_frame  (root；坐地于 FLOOR_Z=CASTER_GAP=0.150。carcass_shell 黑钢柜 + side_pegboard 红洞洞板。
                由 storage_module slot 决定前储物面 + 顶台面 mesh；CAB_H 随 drawer_count 自适配)
  │
  ├── [push_handle]  (FIXED；handle_frame U-loop + handle_grip 红胶套)
  │     ──[frame_to_handle: FIXED origin=(0,0,0)]
  │
  ├── [drawer_count multiplicity 轴]  drawer_{i} / drawer_face_{i}  i∈range(N)
  │     ──[frame_to_drawer_{i}: PRISMATIC axis=(0,1,0)(+Y 拉出), origin=(0,0,zc_i), lower=0 upper=DRAWER_TRAVEL≈0.300]
  │       zc_i = _drawer_face_centers()[i]（从 _drawer_band_top() 向下逐抽屉减 height+gap）
  │       N 范围 [2,9]；drawer_stack/worktop/rail_shelf → 全 N；cabinet_door/open_shelf → 上方 3 浅抽屉（下 bay 被门 / 隔板消耗）
  │
  ├── [storage_module slot]  (互斥五选一；决定前面 + 顶台面)
  │     ├─ drawer_stack : (满抽屉栈 = 上面 drawer_count 轴本体；顶 = 凹 tray basin)
  │     ├─ cabinet_door : cabinet_door(door_panel) ──[frame_to_door: REVOLUTE axis=(0,0,1)(左缘竖铰), origin=(hinge_x,hinge_y,door_cz), lower=0 upper=1.50]  + 上方 3 浅抽屉
  │     ├─ open_shelf   : bay_divider + shelf_{i}(i∈range(2)) = cabinet_frame inline FIXED visual(无 joint, Rule 1)  + 上方 3 浅抽屉
  │     ├─ worktop      : 平台 slab + 周边唇 fused 进 carcass_shell(无额外 part/joint)  + 全 N 抽屉栈
  │     └─ rail_shelf   : guard_rail(4 角柱+横杆) = cabinet_frame inline FIXED visual(无 joint, Rule 1)  + 全 N 抽屉栈
  │
  └── [caster slot]  (互斥三选一；挂 cabinet_frame 地板下 z=FLOOR_Z)
        ├─ all_swivel        : 4×(caster_fork_{i} ──[frame_to_caster_{i}: CONTINUOUS Z] + caster_wheel_{i} ──[caster_to_wheel_{i}: CONTINUOUS X])
        ├─ mixed_swivel_fixed: 前2(swivel_fork ──[frame_to_swivel_{i}: CONTINUOUS Z]+wheel ──[swivel_to_wheel_{i}: CONTINUOUS X]) + 后2(fixed_bracket ──[frame_to_bracket_{i}: FIXED]+wheel ──[bracket_to_wheel_{i}: CONTINUOUS X])
        └─ brake_caster      : 4×(caster_fork ──[frame_to_caster_{i}: CONTINUOUS Z] + caster_wheel ──[caster_to_wheel_{i}: CONTINUOUS X] + brake_lever_{i} ──[fork_to_brake_{i}: REVOLUTE X, parent=fork, lower=0 upper=0.55])
```

接口点位与 joint 语义：
- **drawer_count 接口（multiplicity 主轴）**：每个 `drawer_{i}` 是 `cabinet_frame` 的 PRISMATIC child，axis=(0,1,0)，origin=(0,0,zc_i)，zc_i 由 `_drawer_face_centers()` 解析（从 `_drawer_band_top()=FLOOR_Z+CAB_H−WALL−TOP_MARGIN` 向下逐抽屉减 `DRAWER_HEIGHTS[i]+DRAWER_GAP`）。抽屉盒身 captured 在 carcass 开口内（小 sliding clearance，`allow_isolated_part`，照搬 parent L676-684）。rest pose q=0（闭合，面板与柜前齐平）。
- **storage_module 接口（root，互斥五选一）**：所有 storage_module 决定 root 前面 + 顶台面 mesh。drawer_stack/worktop/rail_shelf 用满 N 抽屉栈（worktop 改顶台面 fused、rail_shelf 加顶护栏 inline）；cabinet_door 加 1 个 `cabinet_door` REVOLUTE child（侧竖铰）并把抽屉减到上方 3 浅；open_shelf 加 `bay_divider`+`shelf_{i}` inline FIXED visual 并把抽屉减到上方 3 浅。门铰 origin 落在 `_door_opening()` 解析的下 bay 左缘竖线（`fail_if_articulation_origin_far_from_geometry` 守）。
- **caster 接口（root，互斥三选一，挂地板下 z=FLOOR_Z）**：脚轮 swivel/fixed bracket 挂 `cabinet_frame` 地板下四角 `caster_positions = [(±(CAB_W/2−INSET_X), ±(CAB_D/2−INSET_Y))]`。swivel post 咬入地板捕获（`allow_overlap` carcass↔fork）；wheel captured 在 fork trailing yoke（`allow_overlap` fork↔wheel）；brake_lever pivot 在 fork leg boss（`allow_overlap` fork↔lever）。all_swivel/brake = enumerate 四角 loop；mixed = 两个 `for i in range(2)`（前 swivel / 后 fixed）。
- **push_handle 接口（FIXED）**：`frame_to_handle` FIXED origin=(0,0,0)，handle 在 carcass frame 建模（顶后部 U-loop），upright bosses 咬入 top trim band（`allow_overlap` carcass↔handle，照搬 parent L712-720）。
- **mating policy**：所有抽屉是 box-in-cavity captured-slide（PRISMATIC）、脚轮 swivel 是 post-in-floor captured-bearing、wheel 是 pin-in-yoke captured-roll、门是 panel-on-side-hinge、brake 是 lever-on-fork-boss。几何均非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` / `allow_isolated_part` 守 captured overlap / sliding clearance（照搬各样本 run_tests 段）。
- **rest pose**：所有抽屉 q=0 闭合；门 q=0 关；brake q=0 松；脚轮 swivel/roll 静位 0。
- **互斥 / 可选 / 派生**：storage_module 五选一互斥（drawer_stack/worktop/rail_shelf 全 N；cabinet_door/open_shelf 派生减抽屉到 3 + 下 bay 机构）；caster 三选一互斥；drawer_count N 是 multiplicity 主轴，与 storage_module 联动（见 §9 兼容矩阵）。

## 每槽位 Module Emits / Interfaces

### Slot A / storage_module — drawer_stack（基线 + multiplicity 载体）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cabinet_frame`（root，visual: `carcass_shell` 黑柜含凹 tray basin + socket pockets + `side_pegboard` 红洞洞板）；N 个 `drawer_{i}`（visual `drawer_face_{i}` 红面板 + 凹指拉 + 黑中空盒身）| `_carcass_mesh` L123-202 / `_pegboard_mesh` L205-229 / `_drawer_mesh` L232-272 |
| internal joints | N 个 `frame_to_drawer_{i}` PRISMATIC axis=(0,1,0) origin=(0,0,zc_i) lower=0 upper=DRAWER_TRAVEL=0.300 | L489-502 |
| upstream interface | root（坐地，FLOOR_Z=CASTER_GAP=0.150 使轮落 z=0；CAB_H 随 N 自适配，n7 升至 0.820）| L52, L45 |
| downstream interface | 前开口（抽屉滑入）+ 顶 tray basin（工具托）+ 地板下四角（caster 接入）+ 顶后 trim（handle 接入）| L123-202 |

### Slot A / storage_module — cabinet_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cabinet_frame`（同基线但下 bay 留空给门）；3 个 `drawer_{i}`（上方浅抽屉）；`cabinet_door` part（visual `door_panel` red 面板 + 凹指拉）| `_cabinet_door_mesh` L290-? / `_door_opening` L131-145 |
| internal joints | 3 个 `frame_to_drawer_{i}` PRISMATIC（上栈）+ `frame_to_door` REVOLUTE axis=(0,0,1) origin=(hinge_x=−(CAB_W/2−SIDE_REVEAL), hinge_y=CAB_D/2, door_cz) lower=0 upper=DOOR_OPEN_ANGLE=1.50 | L543, L584-597 |
| upstream interface | 下 bay 左缘竖铰线（`_door_opening()` 解析门高 / 中心）| L131-145, L571-572 |
| downstream interface | 门后封闭 bay（柜内储物）；上方 3 浅抽屉栈 | L139-145 |

### Slot A / storage_module — open_shelf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cabinet_frame`（下 bay 开放 + `bay_divider` inline visual + `SHELF_COUNT=2` 个 `shelf_{i}` inline 固定隔板 visual）；3 个 `drawer_{i}`（上方浅抽屉）| `_shelf_mesh` L310-339 / `_bay_divider_mesh` L342-355 / `_shelf_z_positions` L142-152 |
| internal joints | 3 个 `frame_to_drawer_{i}` PRISMATIC（上栈）；**隔板无 joint**（FIXED 非移动 inline visual，Rule 1，loop L538-545 `for i in range(SHELF_COUNT)`）| L575-598 |
| upstream interface | 下 bay（`bay_divider` 分隔抽屉栈与开放 bay）| L342-355 |
| downstream interface | 开放隔板 bay（隔板嵌入侧壁 WALL_MOUNT，前缘小上翻唇）；上方 3 浅抽屉栈 | L310-339 |

### Slot A / storage_module — worktop
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cabinet_frame`（同基线但顶 = 平实 solid 台面 slab + 薄周边唇 fused，替代凹 tray basin，**无额外 part**）；全 N 抽屉栈 | `_carcass_mesh`(worktop) L173-219 |
| internal joints | N 个 `frame_to_drawer_{i}` PRISMATIC（全栈，loop L498-521）；**台面无 joint**（fused root visual）| L498-521 |
| downstream interface | 平台台面（无 basin，薄周边唇）；全 N 抽屉栈；其余接口同基线 | L173-219 |

### Slot A / storage_module — rail_shelf
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cabinet_frame`（顶 utility shelf + `guard_rail` inline visual：4 角柱 `for i in range(4)` + 上 / 中横杆 + 球帽）；全 N 抽屉栈 | `_guard_rail_mesh` L223-332 / `guard_rail` L557 |
| internal joints | N 个 `frame_to_drawer_{i}` PRISMATIC（全栈，loop L586-608）；**护栏无 joint**（FIXED 非移动 inline visual，Rule 1）| L586-608 |
| downstream interface | 顶护栏 utility shelf（管状周边）；全 N 抽屉栈；新 `STEEL` 材质 | L223-332, L550-551 |

### Slot B / caster — all_swivel（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 4 个 `caster_fork_{i}`（visual `fork_{i}` 暗色 U-yoke + swivel post）+ 4 个 `caster_wheel_{i}`（visual `wheel_{i}` 橡胶轮 + hub）| `_caster_fork_mesh` L346-402 / `_caster_wheel_mesh` L405-433 |
| internal joints | 4 个 `frame_to_caster_{i}` CONTINUOUS axis=(0,0,1) origin=(cx,cy,FLOOR_Z)（转向）+ 4 个 `caster_to_wheel_{i}` CONTINUOUS axis=(1,0,0) origin=(0,−DROP,AXLE_Z)（滚动）| L531-551 |
| upstream interface | swivel post 咬入 carcass 地板捕获（`allow_overlap` carcass↔fork）| L784-793 |
| downstream interface | wheel captured 在 fork trailing yoke（`allow_overlap` fork↔wheel）；轮落 z=0 | L774-783 |

### Slot B / caster — mixed_swivel_fixed
| emits | 描述 | 来源 |
|---|---|---|
| parts | 前 2 `swivel_fork_{i}`/`swivel_wheel_{i}` + 后 2 `fixed_bracket_{i}`/`fixed_wheel_{i}` | `_fixed_bracket_mesh` L349-389 |
| internal joints | 前: `frame_to_swivel_{i}` CONTINUOUS Z + `swivel_to_wheel_{i}` CONTINUOUS X（trailing offset）；后: `frame_to_bracket_{i}` FIXED + `bracket_to_wheel_{i}` CONTINUOUS X origin=(0,0,AXLE_Z)（无 trailing）；两个 `for i in range(2)` | L559-597 / L601-635 |
| upstream interface | swivel post 咬入地板（swivel）/ bracket FIXED 焊地板（fixed）| run_tests allow_overlap 段 |
| downstream interface | 前转向 + 后定向轮均落 z=0 | — |

### Slot B / caster — brake_caster
| emits | 描述 | 来源 |
|---|---|---|
| parts | 4 个 `caster_fork_{i}` + 4 个 `caster_wheel_{i}`（pneumatic tire + 辐条 rim 双 visual）+ 4 个 `brake_lever_{i}`（脚刹钢片）| `_caster_wheel_meshes` L436-517 / `_brake_lever_mesh` L520-545 |
| internal joints | 4 个 `frame_to_caster_{i}` CONTINUOUS Z + 4 个 `caster_to_wheel_{i}` CONTINUOUS X + 4 个 `fork_to_brake_{i}` REVOLUTE axis=(1,0,0) **parent=fork** child=`brake_lever_{i}` origin=(half_w+0.008,−DROP,boss_z) lower=0 upper=BRAKE_ENGAGE_ANGLE=0.55 | L658-695 |
| upstream interface | brake_lever pivot 在 fork leg boss（`allow_overlap` fork↔lever，照搬 L977-1003）| L977-1003 |
| downstream interface | 脚刹踩下 REVOLUTE（每脚轮 3 joint，4 脚轮 12 joint）| L926-953 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| storage_module | enum | drawer_stack / cabinet_door / open_shelf / worktop / rail_shelf | drawer_stack | choice | deterministic procedural sampler 选；决定前储物面 + 顶台面 + 抽屉 band 占用（互斥）| Slot A 表 |
| caster | enum | all_swivel / mixed_swivel_fixed / brake_caster | all_swivel | choice | sampler 选；决定脚轮 part 树 + joint 拓扑（互斥）| Slot B 表 |
| drawer_count (N) | int | 声明产品域 **[2,9]**；sweep 采样域 [2,9]（偏小加权：N=3-5 高频、6-7 常见、8-9 长尾、2 下界）| 5 | conditional→slot_choice | **multiplicity 主轴**；编入 slot_choice 为 `("drawer_count", f"n{N}")`（拓扑维度）；cabinet_door/open_shelf 时 N 受下 bay 约束（见下 conditional + §8/§9）| parent / n3 / n7 |
| palette_style | enum | red_black_steel / blue_steel / safety_yellow / graphite_chrome / hi_vis_orange | red_black_steel | palette | palette only，**不计入 slot_choice**；见下方 colorway 说明 | 各样本材质 |
| cab_width_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 CAB_W（柜宽 X），clamp；连带抽屉面宽 / pegboard / caster 间距随之派生 | resolve clamp |
| cab_depth_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 CAB_D（柜深 Y），clamp；连带抽屉盒身深 / 门厚 / caster Y 间距派生 | resolve clamp |
| drawer_height_scale | float | [0.85, 1.15] | 1.0 | conditional | 缩放每抽屉 face 高（drawer_stack/worktop/rail_shelf 用均匀或浅 / 深档；door/openshelf 上 3 浅档）；clamp 使 `Σ(h_i)+gaps` ≤ 可用 band | parent DRAWER_HEIGHTS / n7 L66 |
| drawer_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 PRISMATIC upper（基 0.300）；clamp ≤ 0.95·盒身深（抽屉拉出不脱轨）| parent L501 |
| door_open_angle_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 cabinet_door 有效；缩放 REVOLUTE upper（基 1.50）；clamp ≤ 0.95·π/2·1.15（门不撞邻物 / 不过开）| door L595 |
| brake_angle_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 brake_caster 有效；缩放 brake REVOLUTE upper（基 0.55）；clamp 使脚刹踩下不穿轮 / 地 | brakecaster L693 |
| caster_gap_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 CASTER_GAP（轮高 / 离地间隙，基 0.150）；连带 AXLE_Z / wheel R 派生使轮仍落 z=0 | parent L51 |
| (—) | constraint | — | — | inequality | 抽屉栈占高：`Σ(DRAWER_HEIGHTS[i]·drawer_height_scale) + (N−1)·DRAWER_GAP ≤ 可用 band = CAB_H − WALL − TOP_MARGIN − BASE_BAND`；违反则升 CAB_H（如 n7 升 0.820）或回缩 drawer_height_scale / N | parent L102-117 / n7 L64-66 |
| (—) | constraint | — | — | inequality | 抽屉拉出不脱轨：`drawer_travel·drawer_travel_scale ≤ 0.95·box_depth`（box_depth=CAB_D−WALL−0.030）；违反回缩 travel | parent L242, L501 |
| (—) | constraint | — | — | inequality | cabinet_door 门高 + 上方 3 浅抽屉栈 ≤ 可用 band（`door_H + 3·shallow_h + gaps ≤ band`）；门 origin / 高由 `_door_opening()` 解析使两者不重叠 | door L131-145 |
| (—) | constraint | — | — | conditional | drawer_count 上限随 storage_module：drawer_stack/worktop/rail_shelf → N∈[2,9]（全栈）；cabinet_door/open_shelf → 上方栈固定 N=3 浅（下 bay 被门 / 隔板消耗），drawer_count 在这两候选下解析为 3（见 §8 / §9）| door / openshelf |
| (—) | constraint | — | — | inequality | 四脚轮落地共面：`AXLE_Z = −CASTER_GAP·caster_gap_scale + CASTER_WHEEL_R` 使轮 z_min≈0；caster_positions 在柜地板四角内（INSET）；违反回缩 caster_gap / INSET | parent L343, L507-511 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 storage_module / caster / drawer_count 的拓扑**。

**palette_style colorway（5 套，来自 9 个 5★ 源材质）**：
- `red_black_steel`（基线 / 默认）：red 抽屉 (0.74,0.07,0.07) + black 柜壳 (0.10,0.10,0.11) + dark 把手 & fork (0.16,0.16,0.18) + rubber 轮 (0.09,0.09,0.10) + grip_red 握把 (0.70,0.10,0.10)（全样本原色；railshelf/door 加 steel (0.55,0.56,0.58)）。
- `blue_steel`：抽屉 / 柜壳改深蓝钢 (0.13,0.24,0.42) + 银灰柜框 + chrome 把手 (0.72,0.74,0.78) + black 轮；专业蓝工具柜身份。
- `safety_yellow`：抽屉 / 柜框改安全黄 (0.86,0.72,0.10) + black 柜壳 + chrome 把手 + black 轮；工地高可见身份。
- `graphite_chrome`：石墨灰柜身 (0.22,0.23,0.25) + chrome 抽屉拉 / 把手 (0.72,0.74,0.78) + dark red accent + black 轮；高端工具柜身份。
- `hi_vis_orange`：橙红抽屉 (0.88,0.36,0.06) + black 柜壳 + steel 顶台面 / 护栏 + grip_black 握把；DIY / 消费级身份。

## Multiplicity / Copy Logic

**1 根小类级 multiplicity 主轴**（抽屉数 —— 本类的支配性多重性轴）：

- **count_param**：`drawer_count`（模板内变量 N；sources 用 `NUM_DRAWERS`(n3) / `N_DRAWERS`(n7)，parent 用 5-tuple `DRAWER_HEIGHTS`）。柜前栈的红抽屉数；每抽屉是一个独立 PRISMATIC joint，所以非 fixed joint 数随 N 变化（11-17 跨样本）。**这是支配性轴**（与 caulking_gun 的 rib_count module-local 轴不同：drawer_count 是小类级、改全模板 part/joint 拓扑、且是 drawer_stack/worktop/rail_shelf 候选的主结构）。
- **N_range**：声明产品域 **[2, 9]**（小型滚动 2-3 抽屉车 → 高大滚动工具柜 ~9；source map 建议 [2,9]，band 高度由 `CAB_H` / `_drawer_band_top()` / `_drawer_face_centers()` 自动适配，n7 已示范 `CAB_H` 升至 0.820 容纳 7 栈，N=8/9 由同一机制外推）。样本覆盖 {3,5,7} 仅示范 copy 逻辑，sampler 填满 [2,9] 其余值。`config_from_seed` 的 sweep 采样域 **[2, 9]**（偏小加权：N=3/4/5 高频、6/7 常见、8/9 长尾、2 下界）。
- **sampling domain**：`config_from_seed` 用 `rng.choices(range(2,10), weights=偏中小)`；`resolve_config` 把任意外部 config 的 N clamp 到 [2,9]，并在 cabinet_door/open_shelf 候选下解析为上方 3 浅栈（见 §9 兼容矩阵）。
- **copied object**：单个抽屉 = `drawer_{i}` part（red `drawer_face_{i}` 面板 + 凹指拉 + 黑中空盒身）由共享 `_drawer_mesh(index)` helper 建（parent L232-272）。
- **naming**：`drawer_{i}` part、`drawer_face_{i}` visual、`frame_to_drawer_{i}` joint（0-based i，top→bottom）；`for i in range(N)` 或 `for i, zc in enumerate(_drawer_face_centers())`（n3 L480 用 range、parent/n7 L480/L481 用 enumerate，**两者等价**，模板用 enumerate face_centers）。
- **placement**：栈式 top→bottom **绝对式**——`_drawer_face_centers()` 从 `_drawer_band_top()=FLOOR_Z+CAB_H−WALL−TOP_MARGIN` 向下走，每抽屉减 `DRAWER_GAP` 后取 `z − h/2`，再减 `DRAWER_HEIGHTS[i]`（parent L108-117）。joint origin z = 各抽屉静止中心 zc_i，x=y=0；每个 zc_i 由 N + band + 各 height 解析（不累加漂移）→ N-不变前提。
- **joint policy**：每抽屉是**独立 PRISMATIC joint**，parent=`cabinet_frame`，axis=(0,1,0)（+Y 拉出），`MotionLimits(lower=0.0, upper=DRAWER_TRAVEL≈0.300, effort=60, velocity=0.30)`。**不链式、不共享 hub**——每抽屉独立滑出柜体（parent L489-502）。
- **source/gating**：copy-logic 源取 parent L478-502 的 `for i, zc in enumerate(face_centers)` 循环 + L232-272 共享 `_drawer_mesh` helper + L102-117 band/centers helper；**N=5 即 parent 基线**（三浅二深），N=3 取 n3（uniform 0.150），N=7 取 n7（uniform 0.098 + CAB_H 升 0.820）。drawer_count 与 storage_module 的兼容见 §9（cabinet_door/open_shelf 消耗下 bay → 这两候选下 drawer_count 解析为上方 3 浅栈）。

**drawer_count 必须编入 `slot_choices_for_seed` 的 tuple**（`("drawer_count", f"n{N}")`），否则不同抽屉数的拓扑维度损失（对齐 cushion pan_count / caulking_gun rib_count / fence_cascade 范式）。

> 注：以下是**固定 N 的 module-local visual 复制**（非可变 count 轴、非移动件、按 Rule 1 inline 为 root visual，**不暴露为 multiplicity 轴**）：open_shelf 的 `SHELF_COUNT=2` 个 `shelf_{i}` inline 隔板（FIXED visual，loop `for i in range(SHELF_COUNT)` L538-545）；rail_shelf 的 `_guard_rail_mesh` 内 4 角柱 `for i in range(4)`；pegboard 洞孔 / wheel 辐条 inline 几何 loop；caster 四角 `for i, (cx,cy) in enumerate(caster_positions)`（固定 4）/ mixed 的两个 `for i in range(2)`（固定 2+2）。这些都不是模板级可变 count 轴。

## 拓扑多样性审计

总组合数（离散槽 + multiplicity 主轴，**受 §9 兼容矩阵约束**）：
- 朴素笛卡尔积 = storage_module(5) × caster(3) = **15** base topologies（source map combo 预审）。
- 叠 drawer_count：drawer_stack/worktop/rail_shelf（3 个全 N 候选）× N∈[2,9]（8 值）= 24 storage 状态；cabinet_door/open_shelf（2 个固定 3 浅栈候选）不随 N 展开 = 2 storage 状态 → storage 维度 = 24 + 2 = **26** distinct storage 拓扑。
- 总合法组合 = storage 拓扑(26) × caster(3) = **78**（远超 ≥10 门控）。

仅 storage_module(5) × caster(3) = **15** 已含 5 种前面 / 顶台面 × 3 种脚轮 joint 拓扑（all_swivel 8 joint / mixed 6 joint / brake 12 joint）的结构差异；叠 drawer_count 全 N → ~78 ≥ 10 稳过。

理由：storage_module(5 种前面 + 顶台面几何，含 1 REVOLUTE 门 / FIXED 隔板 / FIXED 护栏 / fused 台面 / 满抽屉栈) × caster(3 种脚轮 joint 拓扑) × drawer_count(全 N 候选 [2,9]) 提供充裕真实结构差异。**drawer_count 必须编入 slot_choices_for_seed**（`("drawer_count", f"n{N}")`），否则不同抽屉数在 slot_choice 上不可区分，损失主多重性维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` storage_module，再 `rng.choice` caster，再（drawer_stack/worktop/rail_shelf 时）`rng.choices` 加权 N∈[2,9]（cabinet_door/open_shelf 时 drawer_count 解析为 3 浅栈），再 uniform 各连续 scale（解析 conditional：door_open_angle 仅 cabinet_door、brake_angle 仅 brake_caster、drawer_height 随 storage_module 档）。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（含一个 small-N drawer_stack、一个 large-N drawer_stack、一个 cabinet_door、一个 open_shelf、一个 brake_caster、一个 worktop+mixed）。


Controlled local parameterization：见 §参数表的 cab_width_scale / cab_depth_scale / drawer_height_scale(conditional@storage) / drawer_travel_scale / door_open_angle_scale(conditional@cabinet_door) / brake_angle_scale(conditional@brake_caster) / caster_gap_scale。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（storage_module→caster）→ 采 drawer_count N（drawer_stack/worktop/rail_shelf 加权 [2,9]；cabinet_door/open_shelf 解析为 3）→ 采 independent cab_width/depth/travel/caster_gap scale → 派生（抽屉面宽随 cab_width、盒身深随 cab_depth、caster 间距随 W/D、AXLE_Z 随 caster_gap、CAB_H 随 N×drawer_height）→ 解析 conditional（drawer_height 档、door_open_angle、brake_angle）→ 用 inequality 投影 / 回缩（抽屉栈占高 ≤ band 否则升 CAB_H、抽屉行程 ≤ 0.95·盒身深、门高+上栈 ≤ band、四轮共面落地）。跨部件依赖显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 drawer/caster/door 的 joint origin、captured 接口、抽屉复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` storage_module + caster，再 `rng.choices` 加权 N∈[2,9]（drawer_stack/worktop/rail_shelf）/ 解析 N=3（cabinet_door/open_shelf），再 uniform 各 scale | slot_choices_for_seed 含 `("storage_module",..),("caster",..),("drawer_count",f"n{N}")` 且与 build 一致 |
| compatibility matrix | (1) **drawer_count × storage_module**：drawer_stack/worktop/rail_shelf → drawer_count∈[2,9] 全栈（worktop/rail_shelf 是纯顶台面 swap，与全 N 正交）；cabinet_door/open_shelf 消耗下 bay → drawer_count 解析为上方 **N=3 浅栈**（样本基线，下 bay 被门 / 隔板占用），不随采样 N 展开（避免门 / 隔板与多抽屉争 band）。 (2) **storage_module × caster 正交**：5 种 storage × 3 种 caster 均可（脚轮挂地板下、storage 在柜体内 / 顶，互不干涉）。 (3) **抽屉栈占高**：`Σ(h_i·scale)+gaps ≤ band`，违反先升 CAB_H（n7 范式）再回缩 drawer_height / N，保证抽屉不互撞 / 不顶天。 (4) **门 / 刹角**：door_open_angle clamp ≤ 0.95·π/2·1.15（门不过开）、brake_angle clamp 使脚刹不穿轮 / 地。 (5) **四轮共面**：AXLE_Z 随 caster_gap 派生使轮落 z=0（mixed 的 fixed 轮无 trailing offset，origin=(0,0,AXLE_Z)）。 | 无 floating / collision / 抽屉互撞或顶天 / 门过开 / 脚刹穿轮 / 轮不落地 / cabinet_door 与多抽屉争 band |
| controlled local variation | 8 个 clamped scale（cab_width/depth、drawer_height@storage、drawer_travel、door_open_angle@cabinet_door、brake_angle@brake_caster、caster_gap），每 build 统一；drawer_height/door_open_angle/brake_angle 为 conditional | 比例变化不破坏 drawer/caster/door joint origin、captured 接口、抽屉行程、四轮落地、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 storage_module/caster/drawer_count QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| storage_module | 5 | yes | yes | drawer_stack(满栈) / cabinet_door(REVOLUTE 门+3 浅) / open_shelf(FIXED 隔板+3 浅) / worktop(fused 台面) / rail_shelf(FIXED 护栏)，5 种前面+顶台面 |
| caster | 3 | yes | yes | all_swivel(8 joint) / mixed_swivel_fixed(6 joint) / brake_caster(12 joint)，3 种脚轮 joint 拓扑 |
| drawer_count (N) | 8（采样域 [2,9]，仅 drawer_stack/worktop/rail_shelf 全展开；cabinet_door/open_shelf 固定 3）| yes | yes | **multiplicity 主轴**，编入 slot_choice `("drawer_count",f"n{N}")` |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名（storage_module / caster），且含 `("drawer_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，drawer_count 采样域 ⊆ [2,9]（drawer_stack/worktop/rail_shelf 全展开；cabinet_door/open_shelf 解析为 3）
- `resolve_config` 把 drawer_count clamp 到 [2,9]、各 scale clamp 到声明范围；drawer_height/door_open_angle/brake_angle 为 conditional 随 storage_module / caster 解析；四条 clearance inequality（抽屉栈占高 / 抽屉行程 / 门高+上栈 / 四轮共面）在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（cabinet_door/open_shelf 固定 3 浅栈；door_open_angle / brake_angle clamp；四轮落地共面；抽屉不顶天）
- 连续 scale clamp 后不破坏 drawer/caster/door joint origin / captured 接口 / 抽屉行程 / 四轮落地 / 类别身份
- 关键 joint：抽屉 `frame_to_drawer_{i}` PRISMATIC axis≈(0,1,0) lower=0 upper≈0.300；脚轮 swivel `frame_to_caster_{i}`/`frame_to_swivel_{i}` CONTINUOUS axis≈(0,0,1)；wheel `caster_to_wheel_{i}`/`swivel_to_wheel_{i}`/`bracket_to_wheel_{i}` CONTINUOUS axis≈(1,0,0)；handle `frame_to_handle` FIXED；门 `frame_to_door` REVOLUTE axis≈(0,0,1) upper≈1.50；刹 `fork_to_brake_{i}` REVOLUTE axis≈(1,0,0) parent=fork upper≈0.55；mixed 的 `frame_to_bracket_{i}` FIXED
- captured-slide / bearing / pin：element-scoped `allow_overlap`（carcass↔fork swivel post；fork↔wheel yoke；fork↔brake_lever boss；carcass↔handle bosses）+ `allow_isolated_part`（drawer 滑动间隙），照搬各样本 run_tests 段（parent L676-684、L712-720、L774-793；door allow_overlap L850-858；brake L977-1003）
- copied object 遵循 `drawer_{i}` 命名 + 绝对式 top→bottom placement（`_drawer_face_centers`）+ 独立 PRISMATIC joint policy
- 固定 N inline 复制（shelf_{i} / guard_rail 角柱 / caster 四角）遵循 Rule 1（无独立 joint，shelf/guard 为 root FIXED visual）
- grandfather：所有 captured-slide/bearing/pin/seated 接口省略 MatingContract，由 origin 检查 + allow_overlap/allow_isolated_part 守

## Reject cases

- 把 drawer_count 当普通 int 参数、不进 slot_choice → 不同抽屉数 slot_choice 同形，损失主多重性维度（违反 §8/§9 硬要求）。
- 把抽屉做成链式 / 共享 hub 而非每抽屉独立 PRISMATIC parent=`cabinet_frame` → 违反 joint policy；所有样本是每抽屉独立滑出。
- 在 cabinet_door / open_shelf 候选下仍按采样 N 塞满抽屉、不解析为上方 3 浅栈 → 门 / 隔板与多抽屉争 band，下 bay 重叠 / 抽屉顶天；必须 gate（这两候选固定 3 浅栈，下 bay 给门 / 隔板）。
- 抽屉栈总高超 band 不升 CAB_H 也不回缩 → 抽屉互撞 / 顶天，§7 第一条不等式 FAIL；须升 CAB_H（n7 范式）或回缩 drawer_height / N。
- 把 shelf_{i} / guard_rail 角柱 / worktop 台面 / pegboard / push_handle 当独立活动 part 加 joint → 违反 Rule 1（隔板 / 护栏 / 台面 / 洞洞板是 FIXED 非移动 visual，handle 是 FIXED part）。
- 抽屉 / 门 / 刹 rest pose 设成拉出 / 开 / 踩下而非 q=0 → current-pose 与 viewer 目检不符（所有样本 lower=0 闭合 / 关 / 松）。
- 抽屉满行程后盒身脱出柜体开口 → §7 第二条不等式 FAIL；须回缩 drawer_travel（≤0.95·盒身深）。
- 脚轮轮不落地（z_min≠0）或四轮不共面 → §7 第四条不等式 FAIL；须按 caster_gap 派生 AXLE_Z；mixed 的 fixed 轮 origin 用 (0,0,AXLE_Z) 无 trailing offset。
- 门过开（door_open_angle 超 ~π/2·1.15）穿邻物 / 脚刹踩下穿轮或地 → conditional clamp FAIL；须回缩 door_open_angle / brake_angle。
- 给 captured-slide / bearing / pin 接口补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap/allow_isolated_part。
- 把连续尺寸 / 颜色 / 材质（palette_style / cab scale）当新 candidate 塞进 slot → 不是结构差异。
- 把**固定书架 / 货架**（无轮 / 无柜抽屉 / 无推手）或**手推平板车**（无柜储物）或**滚动工具箱+伸缩拉杆**（2 轮拖行非 4-caster 推车）语义混入 → 出类，本类是 4-caster 推动 + 柜储物的滚动工具车。

## 与相邻类别的边界

- 不该混入：**固定书架 / 货架（shelf / shelving unit）**——无脚轮 / 无柜体抽屉 / 无推手，是固定立架；本类核心是带 caster 可推 + 抽屉 / 柜门储物。
- 不该混入：**办公桌 / 工作台（desk / workbench）**——主体是工作平面 + 桌腿，无 caster 转向 / 滚动，无推手；本类是工具**柜**车。
- 不该混入：**手推平板车 / 推车（flatbed / platform cart / trolley）**——纯平板 + 轮 + 推手，无柜身储物面（source map 忽略的 `platform_cart.py` 即此）；本类必须有柜身抽屉 / 柜门。
- 不该混入：**滚动工具箱 + 伸缩拉杆（rolling toolbox w/ telescoping handle）**——便携箱 + 伸缩拉杆 + 2 轮拖行，非 4-caster 推动的工具柜（source map 忽略的 `rolling_toolbox_with_telescoping_handle.py` 即此）。
- Handtools 大类内：区别于无"4-caster 推动 + 柜身抽屉 / 柜门储物 + 固定推手"身份的其它手动工具（钳 / 锤 / 螺丝刀 / 扳手 / caulking gun）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) drawer_count N_range 取 [2,9]（样本覆盖 {3,5,7}，N=2/4/6/8/9 由 `_drawer_band_top`/`_drawer_face_centers`/CAB_H 自适配外推，n7 已示范升 CAB_H）是否接受；(2) cabinet_door / open_shelf 候选下 drawer_count **固定为上方 3 浅栈**（不随采样 N 展开，下 bay 被门 / 隔板消耗）的兼容策略是否接受，还是要求把上方浅抽屉数也做成可变档（2-3）以再拉一个拓扑维度（首版保守取样本基线 3）；(3) shelf_{i}（open_shelf）与 guard_rail 角柱（rail_shelf）与 worktop 台面按 Rule 1 inline 为 root FIXED visual（无独立 joint）是否符合 multiplicity 审计期望；(4) Topology target ~70-78 <300 的说明（兼容矩阵收窄 + 真实结构上限）是否接受，或要求开放上方浅抽屉可变档拉到 ≥300；(5) palette_style 5 套 colorway 是否覆盖足够；(6) brake_caster 的 pneumatic tire + 辐条 rim 双 visual（与 all_swivel/mixed 的简轮 visual 不同）是否要统一轮 visual 还是保留各候选原 visual。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：carcass mesh 按 storage_module 分（drawer_stack=`_carcass_mesh`(凹 tray)、worktop=`_carcass_mesh`(平台 slab+唇)、rail_shelf=`_carcass_mesh`+`_guard_rail_mesh`(inline)、open_shelf=`_carcass_mesh`+`_bay_divider_mesh`+`_shelf_mesh`(inline)、cabinet_door=`_carcass_mesh`(下 bay 留空)）；抽屉 N 复制复用同一 `_drawer_mesh(index)` + `_drawer_face_centers()`/`_drawer_band_top()`；门 = `_cabinet_door_mesh`+`_door_opening`；caster 按候选分（`_caster_fork_mesh`/`_caster_wheel_mesh`(all_swivel)、`_fixed_bracket_mesh`(mixed)、`_caster_wheel_meshes`(tire+rim)/`_brake_lever_mesh`(brake)）；`push_handle` = `_handle_mesh`（全候选共享）。
- captured 接口 allow_overlap / allow_isolated_part：`run_tool_cart_tests` 里逐组合补 element-scoped（carcass↔fork swivel post；fork↔wheel yoke；fork↔brake_lever boss；carcass↔handle bosses；drawer 滑动 `allow_isolated_part`），照搬各样本 run_tests 段（parent L676-684 / L712-720 / L774-793；door allow_overlap L850-858；mixed/brake 对应段 L977-1003）。
- **drawer_count band 自适配（最关键实现点）**：`CAB_H` 随 N×drawer_height 派生（参 n7 把 CAB_H 升到 0.820 容纳 7 栈）；`_drawer_band_top()` / `_drawer_face_centers()` 解析每抽屉 zc_i 使栈不顶天 / 不互撞；inequality `Σ(h_i)+gaps ≤ band` 在 resolve 内投影（升 CAB_H 或回缩）。cabinet_door/open_shelf 候选把 N 解析为上方 3 浅栈、下 bay 给门 / 隔板。
- conditional 范围解析顺序：先采 storage_module → caster → drawer_count（drawer_stack/worktop/rail_shelf 加权 [2,9]；cabinet_door/open_shelf 解析 3）→ 解析 drawer_height 档（满栈均匀 / 三浅二深 / 全浅 vs 上 3 浅）/ door_open_angle（仅 cabinet_door）/ brake_angle（仅 brake_caster）→ 采 cab_width/depth/travel/caster_gap independent → 派生（抽屉面宽 / 盒身深 / caster 间距 / AXLE_Z / CAB_H）→ 投影四条 clearance inequality。
- 参考模板：`agent/templates/Accessories_Cushion.py`（mixed pattern：固定 named slots + `("count",f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 mesh 复用 + 兼容矩阵 gating + captured allow_overlap 骨架，本类 drawer_count multiplicity 可同构改编 pan_count）；`agent/templates/Handtools_caulking_gun.py`（同 Handtools 小类的 multiplicity 范式：count 轴编 slot_choice + Rule 1 inline 复制 + conditional scale 解析）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B（parent 基线 + multiplicity 载体）| drawer_stack + all_swivel + push_handle | rec_..._1e586d5a | `_drawer_mesh` L232-272 / `_drawer_face_centers` L108-117 / drawer loop L478-502 / `_carcass_mesh`(凹 tray) L123-202 / `_caster_fork_mesh` L346-402 / `_caster_wheel_mesh` L405-433 / caster loop L504-551 / `_handle_mesh` L285-340 / `frame_to_handle` L470-476 / allow_overlap L712-793 | 满抽屉栈 + drawer_count copy-logic 源（共享 helper + band/centers + 独立 PRISMATIC）+ all_swivel 脚轮 + FIXED handle + captured 范式 |
| S2 | drawer_count（N=3）| drawer_stack n3 | rec_tool_cart_var_n3 | `NUM_DRAWERS=3` L63 / `DRAWER_HEIGHTS=(0.150,0.150,0.150)` L65 / loop `for i in range(NUM_DRAWERS)` L480 / CAB_H=0.640 L45 | drawer_count N=3 copy-logic 源（range 循环 + uniform 高）|
| S3 | drawer_count（N=7）| drawer_stack n7 | rec_tool_cart_var_n7 | `N_DRAWERS=7` L63 / `DRAWER_HEIGHTS=tuple([0.098]*N_DRAWERS)` L66 / loop `for i, zc in enumerate(face_centers)` L481 / CAB_H=0.820 L45（升高容纳 7 栈）| drawer_count N=7 copy-logic 源（enumerate + band 自适配 + CAB_H 升高范式）|
| S4 | A | cabinet_door | rec_tool_cart_var_door | `cabinet_door` part L574-580 / `door_panel` L575 / `frame_to_door` REVOLUTE axis(0,0,1) L584-597 / `_door_opening` L131-145 / `DRAWER_HEIGHTS=(0.072,0.072,0.072)` L67 / drawer loop L543 | 下 bay 侧铰柜门（REVOLUTE 竖铰）+ 上方 3 浅抽屉（drawer_count 派生）|
| S5 | A | open_shelf | rec_tool_cart_var_openshelf | `_shelf_mesh` L310-339 / `_bay_divider_mesh` L342-355 / `_shelf_z_positions` L142-152 / `SHELF_COUNT=2` L77 / shelf loop L538-545 / drawer L575 | 开放隔板 bay（FIXED inline 隔板 Rule 1）+ 上方 3 浅抽屉 |
| S6 | A | worktop | rec_tool_cart_var_worktop | `_carcass_mesh`(平台 slab+周边唇 fused) L173-219 / drawer loop L498-521（全 5）| 平台顶台面（fused root visual，无额外 part/joint）+ 全 N 栈 |
| S7 | A | rail_shelf | rec_tool_cart_var_railshelf | `_guard_rail_mesh`(4 角柱 `for i in range(4)`+横杆) L223-332 / `guard_rail` L557 / `STEEL` L550-551 / drawer loop L586-608（全 5）| 顶护栏 utility shelf（FIXED inline 护栏 Rule 1）+ 全 N 栈 + STEEL 材质 |
| S8 | B | mixed_swivel_fixed | rec_tool_cart_var_mixedcaster | `_fixed_bracket_mesh` L349-389 / swivel loop L559-597 / fixed loop L601-635 / `frame_to_bracket_{i}` FIXED + `bracket_to_wheel_{i}` CONTINUOUS X | 前 2 swivel + 后 2 rigid 脚轮（车间布局）|
| S9 | B | brake_caster | rec_tool_cart_var_brakecaster | `_caster_wheel_meshes`(tire+rim) L436-517 / `_brake_lever_mesh` L520-545 / `fork_to_brake_{i}` REVOLUTE axis(1,0,0) parent=fork L683-695 / `BRAKE_ENGAGE_ANGLE=0.55` L110 / caster loop L627-695 | 脚刹脚轮（每脚轮 3 joint，brake REVOLUTE on fork）|
