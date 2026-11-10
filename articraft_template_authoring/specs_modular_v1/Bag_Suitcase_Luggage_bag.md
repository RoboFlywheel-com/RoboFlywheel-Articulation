# Bag_Suitcase / Luggage bag — Modular Spec

> 来源小类：`picture/Bag_Suitcase/Luggage bag/001.png`（绿色硬壳拉杆箱）。
> 上游 source map：`picture_expansion/template_source_maps/Bag_Suitcase__Luggage_bag.md`。
> **同步状态**：本 spec 引用的 5 个 5 星样本（1 个 parent + 4 个 fork 槽位变体）已在本仓库 `data/records/` 下，rating=5（`category_slug=bag_suitcase`）。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一打开核对）。引用以 part / joint / helper **名字** 为准（`luggage_body` / `front_flap` / `door` / `pull_handle` / `wheel_{i}` / `_build_hollow_shell` / `_make_half_shell` / `_add_spinner_caster` / `_build_grab_handle_mesh` / `body_to_flap` / `body_to_door` / `handle_extend` / `wheel_{i}_spin`），行号仅作定位。
>
> **对 source map 的核对修正（任务要求"不盲信 map"）**：
> 1. source map 称 wheel_system 基线为 `inline_2`（2 直列轮）。**实测 parent 代码发射 4 个轮**（`WHEEL_POSITIONS` 四角 + `wheel_0..wheel_3`，CONTINUOUS spin axis=Y）。**没有任何留存样本真正发射 2 个轮**。因此本 spec 把 wheel_system 槽的两个**结构性 candidate** 定为 `yoke_wheels`（parent 简单 yoke + 圆柱胎，spin axis=Y）vs `swivel_caster`（spinner4 的 swivel raceway plate + fork + TireGeometry，spin axis=X）——这才是真正的 part-tree / joint-axis 拓扑差异；轮**数量** N 单列为 multiplicity 轴（§8），N=2 的"直列对"是 source map 意图的产品形态但**无样本**，作阻塞说明。
> 2. source map 的 body_opening 基线 `integrated_shell` 是**实心**单壳（parent `ExtrudeGeometry` cap=True，无 cut/shell）；`front_lid_flap` / `split_side` 是**空心薄壁**（`.cut()` / `.shell()`）。空心契约见 §核心身份 + §10。
> 3. `clamshell` / `split_flip` 已人工删除，不引用（source map line 38）。

## 元信息
| 项 | 值 |
|---|---|
| slug | `luggage_bag` |
| template path | `agent/templates/Bag_Suitcase_Luggage_bag.py` |
| test path (optional) | `tests/agent/test_luggage_bag_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: body_opening + wheel_system + handle_system，**外加** `wheel_count` 脚轮多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 5（1 parent + 4 fork 槽位变体；均 converged、compile success、≥1 非 fixed joint、workbench-only、单轴 diff、绑定门禁通过；split_side 另经几何修复轮在箱外 + 框条对齐）|
| read_count | 5（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests / allow_overlap 段）|
| read_scope | all 5-star samples in this category（显式清单，非 category query）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 5/5 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **parent（baseline）** `rec_hard-shell-rolling-luggage-bag...110d261f`：实心 `ExtrudeGeometry` 单壳 `luggage_body`（root）+ 4 角 yoke + 4 轮 CONTINUOUS（axis=Y）+ `pull_handle` PRISMATIC 伸缩拉杆（axis=Z）。**整体壳 / yoke 4 轮 / 伸缩把 三轴基线同体**。
- **body_opening 轴**（Slot A）：`front_lid_flap`（frontlid）把 body 改为 cadquery **空心**壳（`_build_hollow_shell`，-Y 面全开）+ 独立 `front_flap` part 绕顶内边 **REVOLUTE**（axis=-X）翻盖；`split_side`（split_side）把 body 沿 Y=0 纵切两半空心半壳（`_make_half_shell` `.shell()`），`door` 半壳绕右竖边 **REVOLUTE**（axis=Z 立轴）侧甩开 —— 这是真正的 part 数 + joint 拓扑变化（多一个 child part + 一个 REVOLUTE，且壳由实心变空心）。
- **wheel_system 轴**（Slot B）：`swivel_caster`（spinner4）用 `_add_spinner_caster` for-loop 发射 swivel raceway plate + fork bridge + 2 fork arms + `TireGeometry` mesh 胎 + hub + axle，spin **axis=X**；与 parent 的简单 yoke box + 圆柱胎（spin **axis=Y**）是 part-tree（fork vs yoke）+ joint-axis（X vs Y）+ primitive（TireGeometry vs Cylinder）三重结构差异。
- **handle_system 轴**（Slot C）：`fixed_top_grab`（fixedgrab）删掉 `pull_handle` part 与 `handle_extend` PRISMATIC，改为 body inline 的 `grab_post_{i}` + 样条扫掠 `grab_grip`（`_build_grab_handle_mesh` tube）**纯 visual 无 joint**；与 parent 的 telescoping `pull_handle` PRISMATIC 是 part 数（有 / 无独立 handle part）+ joint 数（有 / 无 PRISMATIC）的拓扑变化。
- **wheel_count 轴**（Slot D 多重性）：spinner4 已是 `for i in range(4)` 发射脚轮；parent/frontlid/fixedgrab 用四元 `WHEEL_POSITIONS` 枚举（可 range 化）。脚轮是**独立活动件**（每只 `wheel_{i}` 一个 CONTINUOUS joint），与 cushion 的"粉盘 inline 无 joint"不同——此处 N 复制的是**带 joint 的活动子件**。

## 核心身份

一只**硬壳拉杆行李箱（hard-shell rolling luggage / spinner suitcase）**：一个直立的圆角矩形硬壳箱体（`luggage_body`，root，沿 Z 高、坐落于一组底部脚轮上），顶部 / 侧面带提拉机构（伸缩拉杆 / 固定提把），底部四角带脚轮，箱体可整体单壳（实心）或带一个开合舱口（正面翻盖 / 纵向侧门）露出内腔。活动语义 = **三类机构并存**：(1) body_opening 的盖 / 门（REVOLUTE，front_lid / split_side）或无（integrated 整壳）；(2) handle_system 的伸缩拉杆（PRISMATIC，telescoping）或固定提把（无 joint）；(3) wheel_system 的脚轮（每只 CONTINUOUS spin，N 个）。默认成熟域：W≈0.36 / D≈0.22 / H≈0.52 m 的直立硬壳箱，至少 1 个非 fixed joint（轮 spin 始终在）。

**空心契约（硬约束，见 source map line 18）**：会打开露内部的 body_opening candidate（`front_lid_flap` / `split_side`）的壳体用 cadquery `.cut()` / `.shell()` 做**空心薄壁舱**（WALL_T=0.003）；闭合 candidate（`integrated_shell`）保持**实心** `ExtrudeGeometry` 单壳。拉杆 / 脚轮捕获式 overlap 在两种壳上各有对应 allow_overlap（实心壳 → "retracts into the solid shell proxy"；空心壳 → "passes through the hollow shell top wall"）。

不该混入：
- **硬壳储物木箱 / chest（`bag_suitcase_box`）**——板条侧壁 + 金属角件的**静置单体箱**，无脚轮、无伸缩拉杆、卧式后铰平盖为主；本类是直立、带轮、带拉杆的拖行行李箱（核心身份是 wheel + telescoping handle）。
- **软包 suitcase / 旅行袋（拉链软壳 + 织物）**——本类是硬壳（rounded-rect 硬壳 mesh），无拉链 zipper 软体语义。
- **工具拉杆箱（`rolling_toolbox_with_telescoping_handle`）**——虽同有轮 + 拉杆，但工具箱以分层托盘 / 内格为身份；本类以硬壳箱身 + 万向轮行李形态为身份（如需可单独 slug）。
- **手提公文 / 化妆箱（无轮）**——缺脚轮 multiplicity，出本类。

## 槽位 + 候选模块表

> **建模注记**：3 个 named slot 不是串联链——`body_opening` / `wheel_system` / `handle_system` 都把自己的 part / visual / joint 挂到**共同的 `luggage_body` 根**（mixed / parallel children），外加 `wheel_count` 在底面 N 次复制脚轮活动件。`body_opening` 决定**是否多一个 REVOLUTE child + 壳实心 / 空心**；`wheel_system` 决定脚轮 part-tree 与 spin 轴；`handle_system` 决定**是否有 PRISMATIC handle part**。slot 之间通过共享的 `luggage_body` mating face（顶面 handle housing、底面脚轮座、前 / 侧面开口）装配。

### Slot A：body_opening（开合形式 —— **主结构轴**，决定壳实心 / 空心 + 是否多一个 REVOLUTE 舱门）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| integrated_shell（基线） | parent `...110d261f` | L48-104（实心 `ExtrudeGeometry` 单壳 + seam/handle_housing/side grab/yoke visuals；无独立开口 part）| eligible if compatible | **实心**单壳 `luggage_body`，无独立盖 / 门 part，无 body_opening REVOLUTE；闭合储物 |
| front_lid_flap | rec_luggage_var_frontlid | `_build_hollow_shell` L53-84 / `_build_flap_panel` L87-99 / `front_flap` part + `body_to_flap` REVOLUTE L185-209 | eligible if compatible | **空心**薄壁壳（cadquery `.cut()`，-Y 面全开 + `packing_floor` 内底）+ 独立 `front_flap` part 绕**顶内边** REVOLUTE（axis=-X，origin (0,HINGE_Y,HINGE_Z)=前面顶内边，range [0,1.4]）下翻露内腔 |
| split_side | rec_luggage_var_split_side | `_make_half_shell` L63-95 / `door` part + `body_to_door` REVOLUTE L218-283 | eligible if compatible | **空心**两半壳（cadquery `.shell(WALL_T)`），body=后半壳 / `door`=前半壳，绕**右竖边** REVOLUTE（axis=Z 立轴，origin (HINGE_X,0,HINGE_Z)，range [0,π·0.45]）侧门甩开；带 `hinge_barrel`↔`door_hinge_knuckle` captured 铰 + 自由边 latch；轮在箱外的 `base_chassis` skid plate |

### Slot B：wheel_system（轮系硬件 —— 脚轮 part-tree + spin 轴拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| yoke_wheels（基线） | parent `...110d261f` | yoke L106-115 / 轮 part + `wheel_{i}_spin` CONTINUOUS L154-187 | eligible if compatible | 简单 yoke box（body visual）+ 每轮 `tire`（Cylinder）+ `axle`（Cylinder）+ `tread_lug`，CONTINUOUS spin **axis=(0,1,0)**（绕 Y）；轮顶 recessed 进壳底 well（allow_overlap tire↔shell）|
| swivel_caster | rec_luggage_var_spinner4 | `_add_spinner_caster` L61-146（swivel_plate + fork_bridge + 2 fork arms = body visual；wheel part = TireGeometry tire + hub + axle + tread_marker；`wheel_{i}_spin` CONTINUOUS L138-146）| eligible if compatible | 万向脚轮硬件：`swivel_plate_{i}`（圆 raceway）+ `fork_bridge_{i}` + `fork_{i}_{0,1}` 双臂（body visual）+ 每轮 `TireGeometry` mesh 胎（block tread）+ `hub` + `axle`，CONTINUOUS spin **axis=(1,0,0)**（绕 X，垂直于 yoke 基线的 Y）；axle 被 fork 臂 captured |

> wheel_system 两 candidate 的真实结构差异：part-tree（yoke 单 box vs swivel_plate+bridge+双 fork 臂）、primitive（Cylinder 胎 vs TireGeometry mesh 胎）、joint axis（Y vs X）。**轮数量 N 不在此槽**，单列为 §8 multiplicity 轴。

### Slot C：handle_system（提拉机构 —— 是否有独立 PRISMATIC handle part）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| telescoping_pull（基线） | parent `...110d261f` | `pull_handle` part L117-142 / `handle_extend` PRISMATIC L144-152 | eligible if compatible | 独立 `pull_handle` part（2 tube + cross_grip + grip_pad）+ `handle_extend` **PRISMATIC**（axis=(0,0,1)，origin identity，range [0,HANDLE_TRAVEL=0.34]）向上伸缩；retracted 时 tube 插入壳内（allow_overlap tube↔shell）+ 顶 `handle_housing` / `handle_boss` 出口 |
| fixed_top_grab | rec_luggage_var_fixedgrab | `_build_grab_handle_mesh` L41-58 / grab posts + grip L95-111 | eligible if compatible | **无** `pull_handle` part、**无** PRISMATIC：顶面 inline `grab_post_{i}`（2 柱 Box）+ 样条扫掠 `grab_grip`（`tube_from_spline_points` 拱形 tube mesh）**纯 body visual 无 joint**；run_tests 显式断言 `"pull_handle" not in part_names`（活动语义由 wheel spin 提供）|

硬约束记录：3 个 named slot 各 ≥2 candidate（A=3、B=2、C=2），全部来自被采纳五星样本，无 1-candidate 槽。B / C 为 2 candidate（样本池仅 5，每轴仅 1 个 fork 对照基线）——符合 SPEC_TEMPLATE "样本池不足可降到 2，须说明理由"；理由：本小类 retained 五星样本=5（1 parent + 每轴 1 变体），无第 3 个结构变体可采（clamshell/split_flip 已删，wheel/handle 各仅 1 fork）。A=3 因 frontlid + split_side 两个 body_opening fork 都留存。

## 槽位图（slot graph）

pattern: mixed（固定 named slots: body_opening + wheel_system + handle_system 各自挂到共同 `luggage_body`（parallel children），外加 `wheel_count` 在底面 N 次复制脚轮活动件）

```
luggage_body (root, 直立硬壳; 由 body_opening 决定实心 / 空心 + mesh helper)
  │
  ├── [body_opening slot]  (互斥三选一)
  │     ├─ integrated_shell : (实心单壳, 无独立开口 part, 无 REVOLUTE)
  │     ├─ front_lid_flap   : front_flap ──[body_to_flap: REVOLUTE axis=-X, origin=前面顶内边 (0,HINGE_Y,HINGE_Z)]
  │     └─ split_side       : door ───────[body_to_door: REVOLUTE axis=+Z 立轴, origin=右竖边 (HINGE_X,0,HINGE_Z)]
  │                           + hinge_barrel(body)↔door_hinge_knuckle(door) captured-pin
  │
  ├── [handle_system slot]  (互斥二选一)
  │     ├─ telescoping_pull : pull_handle ─[handle_extend: PRISMATIC axis=+Z, origin=identity]
  │     └─ fixed_top_grab   : (grab_post_{i} + grab_grip = body visual, 无 joint)
  │
  └── [wheel_system slot × wheel_count multiplicity 轴]  wheel_{i}  i∈range(N)
        ├─ yoke_wheels   : 每轮 ─[wheel_{i}_spin: CONTINUOUS axis=(0,1,0)]  + yoke_{i}(body visual)
        └─ swivel_caster : 每轮 ─[wheel_{i}_spin: CONTINUOUS axis=(1,0,0)]  + swivel_plate/fork(body visual)
              placement: 底面四角对称（N=4）/ 侧向直列对（N=2，见 §8 阻塞）；x,y 由 N 解析
```

接口点位与 joint 语义：
- **body_opening 接口（互斥）**：
  - integrated_shell：无活动开口 part（实心壳本身就是 root visual）。
  - front_lid_flap：壳前面（-Y）全开，`front_flap` 绕**顶内边铰线** REVOLUTE axis=(-1,0,0)，origin=(0, -D/2, SHELL_TOP-WALL_T)；q=0 闭合贴 -Y 开口，q=1.4 下翻露内腔；`flap_latch` 底缘卡扣 protrude 出 -Y 面。
  - split_side：body=后半壳 / door=前半壳沿 Y=0 split；door 绕**右竖边** REVOLUTE axis=(0,0,1)，origin=(HINGE_X=W/2, 0, HINGE_Z=壳中高)；`door_hinge_knuckle`（door）落入 `hinge_barrel`（body）captured-pin；q=0 闭合两半在 Y=0 对接（expect_gap ≤0.015），q≈1.0 侧甩；自由边 `latch_body`↔`latch_door`。**轮在 `base_chassis` skid plate（fixed body）上，门下脚轮仍接地于 body**。
- **handle_system 接口（互斥）**：
  - telescoping_pull：`pull_handle` PRISMATIC axis=(0,0,1)，origin=identity（authored 在 retracted pose，正 q 整体上滑）；tube 穿 `handle_housing` / `handle_boss` 出口 + 插入壳内（captured，allow_overlap tube↔shell/housing/boss）。
  - fixed_top_grab：grab_post + grab_grip 纯 body visual，无接口 joint（grab_post 接触壳顶 expect_contact，grab_grip 在壳顶之上 expect_gap）。
- **wheel_system / wheel_count 接口**：每只 `wheel_{i}` 一个 CONTINUOUS `wheel_{i}_spin`，origin=(sx, sy, WHEEL_CZ=WHEEL_R)（轮触地 z=0）；axis 由 wheel_system 决定（yoke=Y / swivel=X）；axle captured 进 yoke / fork（allow_overlap axle↔yoke / fork）；tire 顶 recessed 进壳底 well（allow_overlap tire↔shell，split_side 例外：轮在箱外 base_chassis 下，tire_top ≤ shell_base_z）。
- **mating policy**：所有铰 / 捕获是 pin-in-barrel（split door knuckle↔barrel）、axle-in-yoke/fork captured、tube-in-shell captured —— 几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：body_opening 盖 / 门 q=0 闭合（front_flap 贴 -Y 开口 / door 在 Y=0 对接）；telescoping handle q=0 retracted 插入壳内；轮 spin q=0。
- **互斥 / 可选 / 派生**：body_opening 三选一互斥；handle_system 二选一互斥；wheel_system 二选一互斥；wheel_count N 与 wheel_system 联动（见 §8 / §9）。

## 每槽位 Module Emits / Interfaces

### Slot A / body_opening — integrated_shell（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `luggage_body`（visual: 实心 `shell` ExtrudeGeometry + `seam_*` + `handle_housing` + `side_post/side_grip`）；无独立开口 part | parent L48-104 |
| internal joints | 无 body_opening joint（实心整壳）| parent（无）|
| upstream interface | root（坐地，无父）| — |
| downstream interface | 顶 handle_housing（供 handle_system）+ 底脚轮座（供 wheel_system）；无内腔露出 | parent L73-86 |

### Slot A / body_opening — front_lid_flap
| emits | 描述 | 来源 |
|---|---|---|
| parts | `luggage_body`（**空心** cadquery `shell` + `packing_floor` 内底）+ `front_flap`（`flap_panel` mesh + `flap_latch`）| frontlid `_build_hollow_shell` L53-84 / flap L185-199 |
| internal joints | `body_to_flap` REVOLUTE axis=(-1,0,0)，origin=(0, -D/2, SHELL_TOP-WALL_T)，range [0,1.4] | frontlid L201-209 |
| upstream interface | 壳前面 -Y 全开，flap 闭合贴开口（expect_within flap_panel⊂shell width）| frontlid L351-359 |
| downstream interface | 无（flap 是终端 child）| — |

### Slot A / body_opening — split_side
| emits | 描述 | 来源 |
|---|---|---|
| parts | `luggage_body`=后半空心壳（`body_shell` + `base_chassis` skid + `hinge_barrel` + `latch_body`）+ `door`=前半空心壳（`door_shell` + `door_hinge_knuckle` + `latch_door`）| split_side `_make_half_shell` L63-95 / body L114-216 / door L218-268 |
| internal joints | `body_to_door` REVOLUTE axis=(0,0,1)，origin=(W/2, 0, SHELL_Z0+SHELL_H/2)，range [0,π·0.45] | split_side L271-283 |
| upstream interface | `door_hinge_knuckle`↔`hinge_barrel` captured-pin（右竖边铰线）；q=0 两半在 Y=0 对接 expect_gap | split_side L396-419, L449-467 |
| downstream interface | 无（door 是终端 child）| — |

### Slot B / wheel_system — swivel_caster（以单脚轮为例；yoke_wheels 同构但 yoke box + Cylinder 胎 + axis=Y）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel_{i}`（`tire` TireGeometry mesh + `hub` + `axle` + `tread_marker`）；body 上 `swivel_plate_{i}` + `fork_bridge_{i}` + `fork_{i}_{0,1}` visual | spinner4 L96-135 / hardware L69-93 |
| internal joints | `wheel_{i}_spin` CONTINUOUS axis=(1,0,0)，origin=(sx,sy,WHEEL_CZ=WHEEL_R)，无 limit | spinner4 L138-146 |
| upstream interface | `axle` captured 进 `fork_{i}_{0,1}`（allow_overlap）；tire 顶进 swivel/bridge recess | spinner4 L307-331 |
| downstream interface | 无（脚轮终端）；接地点 z=0 | — |

### Slot C / handle_system — telescoping_pull（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pull_handle`（`tube_left/tube_right` Cylinder + `cross_grip` + `grip_pad`）；body 上 `handle_housing` + `handle_boss_{l,r}` 出口 visual | parent L120-142 / housing L73-86 |
| internal joints | `handle_extend` PRISMATIC axis=(0,0,1)，origin=identity，range [0,0.34] | parent L144-152 |
| upstream interface | tube 穿 `handle_housing`/`handle_boss`、retracted 插入壳内（allow_overlap tube↔shell/housing/boss）| parent L204-245 |
| downstream interface | 无（拉杆终端）| — |

### Slot C / handle_system — fixed_top_grab
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`grab_post_{i}`（Box ×2）+ `grab_grip`（spline tube mesh）作 `luggage_body` visual | fixedgrab L95-111 |
| internal joints | 无（固定提把，纯 visual）| fixedgrab run_tests L234-240 断言无 pull_handle |
| upstream interface | grab_post 接触壳顶（expect_contact）、grab_grip 在壳顶之上（expect_gap）| fixedgrab L191-232 |
| downstream interface | 无 | — |

### wheel_count multiplicity（脚轮复制；**带 joint 的活动件**）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel_{i}`（i∈range(N)），每只一个独立活动 part + CONTINUOUS `wheel_{i}_spin` | spinner4 `for i in range(4)` L216-221 |
| joints | 每轮 CONTINUOUS（与 cushion 粉盘 Rule 1 inline 不同：脚轮**有**独立 joint）| spinner4 L138-146 |
| placement | `for i in range(N)`，底面对称（N=4 四角 `WHEEL_POSITIONS`；N=2 侧向直列对，x 固定、±WHEEL_Y）| parent/spinner4 `WHEEL_POSITIONS` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_opening | enum | integrated_shell / front_lid_flap / split_side | integrated_shell | choice | 由 deterministic procedural sampler 选；决定壳实心 / 空心 + 是否加 REVOLUTE child（编入 slot_choice）| module table |
| wheel_system | enum | yoke_wheels / swivel_caster | yoke_wheels | choice | sampler 选；决定脚轮 part-tree + spin 轴（编入 slot_choice）| module table |
| handle_system | enum | telescoping_pull / fixed_top_grab | telescoping_pull | choice | sampler 选；决定是否有 PRISMATIC handle part（编入 slot_choice）| module table |
| wheel_count (N) | int | 声明域 [2,4]；sweep 采样域 {2,3,4}（偏小加权：4 高频真实形态、2/3 长尾）| 4 | conditional→slot_choice | 编入 slot_choice 为 `n{N}`（拓扑维度）；N 与 wheel_system 联动（见 §8 + 不等式）| spinner4 for-loop（N=4 well-sourced；N=2/3 无样本，见 §8 阻塞）|
| palette_style | enum | hardshell_green / graphite_black / silver_aluminum / navy_business / burgundy_leather_trim | hardshell_green | palette | palette only，**不计入 slot_choice**（见 §PALETTE_STYLES）| 各样本材质 |
| box_w / box_d / box_h | float | W∈[0.30,0.42]、D∈[0.18,0.26]、H∈[0.44,0.60] | 0.36/0.22/0.52 | independent | 范围内独立采样后 clamp | 各样本 L20-30 |
| wall_thickness WALL_T | float | derived | 0.003 | equation | `= clamp(0.0025, 0.0040)`，仅 hollow body_opening（front_lid/split）用；integrated 实心不用 | frontlid L29 / split L32 |
| handle_travel_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 telescoping_pull 有效；缩放 `handle_extend` upper（≤ 壳高暴露所需行程）| parent L31 |
| lid_open_angle_scale | float | [0.85, 1.05] | 1.0 | conditional | 仅 front_lid/split 有效；缩放 REVOLUTE upper（front≤1.4 / door≤π·0.45）| frontlid L208 / split L281 |
| wheel_r_scale | float | [0.88, 1.12] | 1.0 | independent | 缩放 WHEEL_R → WHEEL_CZ（轮心 z）+ 离地 clearance，clamp | 各样本 L33-37 |
| wheel_span_scale | float | [0.90, 1.10] | 1.0 | conditional | 仅 N≥2 有效；缩放脚轮 X/Y 跨距 | WHEEL_X/Y |
| (—) | constraint | — | — | inequality | 脚轮跨距不超底面：`N 个轮中心 ± WHEEL_R + margin ⊆ box 底面 footprint`；违反按比例缩 span/wheel_r 或拒绝重采 | 接口 / clearance |
| (—) | constraint | — | — | inequality | telescoping retracted tube 深插壳内（split_side 要求 min_overlap≥0.06 along z）；handle_travel 不得使 retracted 时 tube 出壳 | parent L297-305 / split L509-516 |
| (—) | constraint | — | — | conditional | body_opening=split_side 时轮在箱外 `base_chassis` 下（SHELL_Z0 抬高，`tire_top ≤ shell_base_z`）；其余壳轮 recessed 进壳底 well | split L552-564 |

连续尺寸采样契约：先采 named slot（body_opening / wheel_system / handle_system）+ N（解析 conditional：handle_travel 仅 telescoping、lid_open_angle 仅 front/split、wheel_span 仅 N≥2、SHELL_Z0 抬高仅 split）→ 采 independent 主尺度（box_w/d/h、wheel_r）→ 派生 WALL_T（equation，仅 hollow）→ 用两条 inequality 投影（脚轮跨距 ⊆ 底面、retracted tube 深插）。所有 scale 在 `resolve_config` clamp / 派生，**绝不改 slot enum 选择或 joint type / N**。

## PALETTE_STYLES（colorway，per-seed 采样；不计入 slot_choice）

> 跟随 Accessories_Cushion.md PALETTE_STYLES 范式。下列材质 / 颜色集**锚定 5 星样本实际观测**：parent/frontlid/spinner4 全用 `shell_green=(0.20,0.40,0.16)` + `trim_black=(0.08,0.08,0.09)` + `metal_chrome=(0.60,0.60,0.63)` + `wheel_black=(0.12,0.12,0.13)`；frontlid 另加 `interior_gray=(0.38,0.36,0.34)`；split_side 另加 `door_graphite=(0.22,0.22,0.24)`；fixedgrab 另加 `grip_rubber=(0.15,0.15,0.16)`。`hardshell_green` / `graphite_black` 直接复刻样本；`silver_aluminum` / `navy_business` / `burgundy_leather_trim` 在同 trim/chrome/wheel 骨架上换 shell 主色（现实硬壳行李箱常见配色），保持 trim_black + metal_chrome + wheel_black 不变。

| palette_style | shell (主壳) | trim (seam/housing) | metal (chrome/拉杆/铰) | wheel (胎) | accent (interior/grip/door) | 来源 |
|---|---|---|---|---|---|---|
| hardshell_green（基线） | (0.20,0.40,0.16) | (0.08,0.08,0.09) | (0.60,0.60,0.63) | (0.12,0.12,0.13) | interior_gray (0.38,0.36,0.34) | parent/frontlid/spinner4 实测 |
| graphite_black | (0.22,0.22,0.24) | (0.08,0.08,0.09) | (0.60,0.60,0.63) | (0.12,0.12,0.13) | grip_rubber (0.15,0.15,0.16) | split_side door_graphite + fixedgrab grip_rubber |
| silver_aluminum | (0.72,0.73,0.75) | (0.30,0.30,0.32) | (0.78,0.78,0.80) | (0.12,0.12,0.13) | interior_gray (0.38,0.36,0.34) | metal_chrome 提亮（铝壳行李箱）|
| navy_business | (0.10,0.14,0.30) | (0.07,0.07,0.09) | (0.55,0.55,0.58) | (0.12,0.12,0.13) | interior_gray (0.40,0.40,0.44) | shell 换深蓝（商务硬壳）|
| burgundy_leather_trim | (0.34,0.10,0.13) | (0.18,0.10,0.06) | (0.62,0.55,0.40) | (0.12,0.12,0.13) | grip_rubber (0.20,0.12,0.08) | shell 酒红 + 棕皮 trim + 古铜 metal（皮饰硬壳）|

palette_style 只换命名材质 rgba，不改任何 part / joint / 尺寸 / N；per-seed `rng.choice` 采样，**不进 `slot_choices_for_seed` tuple**。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（底面脚轮数）：

- **count_param**：`wheel_count`（模板内变量 N / WHEEL_COUNT；底面脚轮数）。
- **N_range**：声明产品域 **[2, 4]**（拉杆行李箱底轮现实区间：2 直列轮的卧式拉杆款 / 4 万向轮 spinner 款；source map line 33-35 建议 [2,4]）。`config_from_seed` 的 sweep 采样域 **{2,3,4}**（偏小加权：**N=4 高频**——所有 5 星样本都是 4 轮、是真实主流 spinner 形态；N=2/3 长尾）。
- **sampling domain**：`config_from_seed` 用 `rng.choices((2,3,4), weights=(偏 4))`；`resolve_config` 把任意外部 config 的 N clamp 到 [2,4]。
- **copied object**：单只脚轮活动件——`wheel_{i}`（`tire` + `axle` + (`hub`/`tread_marker` 视 wheel_system)）+ 对应 body 侧硬件（yoke_{i} 或 swivel_plate/fork_{i}），共享 helper 发射（`_add_spinner_caster` 已是单脚轮工厂，可直接作 copy-logic 源）。
- **naming**：`wheel_{i}`（part）+ `wheel_{i}_spin`（joint）+ 硬件 `yoke_{i}` / `swivel_plate_{i}` / `fork_{i}_{0,1}` / `fork_bridge_{i}`，`for i in range(N)`（spinner4 L216 已用此结构）。
- **placement**：底面**绝对式**对称分布——N=4 四角 `(±WHEEL_X, ±WHEEL_Y)`；N=2 侧向直列对 `(0, ±WHEEL_Y)` 或前后对（每个 i 的 (x,y) 由 N 与中心解析，不累加漂移）；N=3 不对称，需 gating（见 §9）。绝对式是 N-不变前提。
- **joint policy**：脚轮是**独立活动件**（与 cushion 粉盘 Rule 1 不同）→ 每只发射独立 CONTINUOUS `wheel_{i}_spin`；axis 由 wheel_system 决定（yoke=Y / swivel=X）。
- **source/gating**：copy-logic 源取 spinner4 `for i in range(4)` + `_add_spinner_caster`（N=4 well-sourced）。**阻塞说明**：N=2 / N=3 **无任何留存五星样本**（5 个样本全是 4 轮）；N=2 是 source map 意图的"inline_2 直列对"产品形态但需在实现期由 N=4 的脚轮工厂参数化降到 2（去掉一对角轮 + 重排 placement），N=3 几何不对称风险高。**首版实现把 sweep 采样域收窄为主要 N=4，并对 N=2 走"直列对" placement 子路径**；若 N=2/3 在 sweep 出现 floating/footprint 问题，gate 回 N=4（见 §9 compatibility）。reviewer 须确认 N=2/3 是否进首版 seed domain，还是仅声明域、采样域先锁 {4}（或 {2,4}）。

## 拓扑多样性审计

总组合数（不含 palette、不含连续 scale）：
body_opening(3) × wheel_system(2) × handle_system(2) × wheel_count 采样数(3，即 {2,3,4}) = **36**（≫ 10）。

source map 预审（不含 multiplicity）：body_opening(3) × wheel_system(2) × handle_system(2) = **12 ≥ 10 ✓**。叠 wheel_count(3) → 36 充裕。

仅 body_opening(3) × handle_system(2) 已含 joint 拓扑差异：integrated（无开口 joint）/ front_lid（+1 REVOLUTE -X）/ split（+1 REVOLUTE +Z）× telescoping（+1 PRISMATIC）/ fixed_grab（无 handle joint）= 6 种 joint-topology 类，叠 wheel_system 的 spin 轴（Y/X）与 N 后远超门控。

理由：`slot_choices_for_seed` 返回 `(body_opening, wheel_system, handle_system, ("wheel_count", f"n{N}"))` 四元组；12（named slot 组合）× 3（N）= 36 个合法 distinct 组合远超 10。body_opening 的 0 / REVOLUTE-X / REVOLUTE-Z 与 handle 的 PRISMATIC / 无 是不同 joint 拓扑等价类，不被 distinct 折叠。**N 必须编入 slot_choice tuple**（`("wheel_count", f"n{N}")`，对齐 cushion/shopping_bucket），否则 2/3/4 轮在 slot_choice 上无法区分，损失一整根拓扑维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三 named slot（body_opening / wheel_system / handle_system），经兼容矩阵合法化，再 `rng.choices` 加权 N∈{2,3,4}，再 `rng.choice` palette_style，再 uniform 各连续 scale。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：关键 scale = box_w/box_d/box_h（independent）、wheel_r_scale（independent）、WALL_T（equation，仅 hollow）、handle_travel_scale（conditional@telescoping）、lid_open_angle_scale（conditional@front/split）、wheel_span_scale（conditional@N≥2）。全部 `resolve_config` clamp / 派生 + 每 build 统一应用。采样契约：先采 named slot + N（解析 conditional 范围：handle_travel/lid_angle/wheel_span/SHELL_Z0 抬高随 slot/N）→ 采 independent box/wheel scale → 派生 WALL_T（hollow）→ 用两条 inequality 投影（脚轮跨距 ⊆ 底面、retracted tube 深插）。跨部件依赖（脚轮跨距 vs 底面、tube 行程 vs 壳高）显式落 §参数表 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 hinge/slide origin、captured-pin/axle 接口、N 复制逻辑、空心契约或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（经兼容矩阵）→ `rng.choices` 加权 N∈{2,3,4} → `rng.choice` palette → uniform 各 scale | slot_choices_for_seed 含 `("wheel_count", f"n{N}")` 且与 build 一致；palette 不进 tuple |
| compatibility matrix | (1) **body_opening × wheel_system / handle_system 正交**（三 named slot 互相兼容，任意组合合法）。 (2) **wheel_count × wheel_system**：N=2 走"直列对" placement（`(0,±WHEEL_Y)` 或前后对）、N=4 走四角、N=3 不对称 → 若 N=3 出 floating/footprint 风险则 gate 回 N=4（或 N=2）。N=2/3 无样本 → 首版可先锁采样域 {2,4} 或 {4}（reviewer 定，见 §8）。 (3) **split_side × wheel placement**：split 的轮在箱外 `base_chassis` 下（SHELL_Z0 抬高），脚轮跨距须 ⊆ chassis footprint；front 脚轮跨距同壳底。 (4) palette_style 与全部机构正交。 | 无 floating wheel / 跨距超底面 / retracted tube 出壳 / 盖门不闭合 / 空心壳实心化错配 |
| controlled local variation | box_w/d/h + wheel_r（independent）、WALL_T（equation@hollow）、handle_travel（conditional@telescoping）、lid_open_angle（conditional@front/split）、wheel_span（conditional@N≥2），每 build 统一 clamp | 比例变化不破坏 hinge/PRISMATIC origin、captured axle/tube 接口、轮接地、盖门闭合、空心契约、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 captured-pin/axle allow_overlap + closed-pose seat |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_opening | 3 | yes | yes | integrated(实心,无 joint) / front_lid(REVOLUTE -X,空心) / split(REVOLUTE +Z,空心) |
| wheel_system | 2 | yes | no | yoke(spin Y) / swivel_caster(spin X)；样本池仅 1 fork 对照，降到 2 已说明 |
| handle_system | 2 | yes | no | telescoping(PRISMATIC) / fixed_grab(无 joint)；样本池仅 1 fork 对照，降到 2 已说明 |
| wheel_count (N) | 3（采样域 {2,3,4}，4 高频 / 2,3 长尾）| yes | yes | 拓扑维度，编入 slot_choice；N=2/3 无样本（§8 阻塞）|

## Validator

- `slot_choices_for_seed` 返回已实现 module 名的四元组 `(body_opening, wheel_system, handle_system, ("wheel_count", f"n{N}"))`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊），N 采样域 ⊆ [2,4]
- `resolve_config` 把 N clamp 到 [2,4]、各 scale clamp 到声明范围；WALL_T 仅 hollow body_opening 派生；handle_travel/lid_open_angle/wheel_span 为 conditional 随 slot/N 解析；两条 inequality（脚轮跨距 ⊆ 底面、retracted tube 深插）在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（N=3 不对称→gate；N=2/3 无样本→首版锁采样域；split 轮在箱外跨距 ⊆ chassis）
- 连续 scale clamp 后不破坏 hinge/PRISMATIC origin、captured axle/tube 接口、轮接地、盖门闭合、空心契约、N 复制
- cross-part scale 依赖（脚轮跨距 inequality、tube 行程 inequality、WALL_T equation、SHELL_Z0 conditional@split）在 `resolve_config` 解析，不留到 builder
- 关键 joint type/axis/range：front_lid `body_to_flap` REVOLUTE axis≈(-1,0,0)（abs(axis[0])>0.99）；split `body_to_door` REVOLUTE axis≈(0,0,1)（abs(axis[2])>0.99）立轴；telescoping `handle_extend` PRISMATIC axis≈(0,0,1)；每轮 `wheel_{i}_spin` CONTINUOUS（yoke axis≈(0,1,0) / swivel axis≈(1,0,0)）
- 空心契约：front_lid/split body 是 cadquery `.cut()`/`.shell()` 空心薄壁（mesh-backed），integrated 是实心 ExtrudeGeometry；allow_overlap reason 随实心 / 空心匹配（"solid shell proxy" vs "hollow shell wall"）
- captured-pin / axle / tube：element-scoped `allow_overlap`（split `door_hinge_knuckle`↔`hinge_barrel`；轮 `axle`↔`yoke_{i}`/`fork_{i}_{0,1}`；`tire`↔shell/swivel/bridge；`tube_left/right`↔shell/housing/boss），照搬各样本 run_tests 的 allow_overlap 段
- copied object 遵循 `wheel_{i}` / `wheel_{i}_spin` 命名 + 绝对式底面对称 placement + 每轮独立 CONTINUOUS joint（非 inline）
- closed pose：body_opening 盖 / 门 q=0 seat（front_flap 贴 -Y 开口 / door 在 Y=0 对接 expect_gap）、telescoping handle q=0 retracted 深插壳内
- grandfather：所有 hinge/axle/tube captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把 N（wheel_count）当普通 int 参数、不进 slot_choice → 2/3/4 轮 slot_choice 同形，损失拓扑维度（违反 §8/§9 硬要求）。
- 把 wheel_system 的"轮数量"当槽（B 槽塞 inline_2 vs spinner_4）→ 误把数量当结构 candidate；数量是 multiplicity 轴，B 槽只放 part-tree/spin-轴 拓扑差异（yoke vs swivel）。
- front_lid / split_side 的 body 仍发实心 `ExtrudeGeometry` 壳（不 `.cut()`/`.shell()`）→ 违反空心契约、开盖露不出内腔、flap/door 与实心壳穿模 FAIL。
- integrated_shell 误做成空心壳 → 闭合款无需空心、徒增 mesh 成本 + 内壁穿模风险；integrated 保持实心。
- 给 captured-pin（split knuckle↔barrel）/ axle↔yoke / tube↔shell 补 MatingContract 硬对接 → 几何对不上 mating-gap FAIL；应 grandfather + allow_overlap。
- 脚轮 rest pose 设成离地浮空 / 跨距超底面 footprint → floating / footprint FAIL；须 inequality 投影跨距 ⊆ 底面、WHEEL_CZ=WHEEL_R 接地。
- body_opening 盖 / 门 rest pose 设成张开角而非 q=0 闭合 → closed-pose seat 检查 FAIL、不符合行李箱身份。
- split_side 的脚轮塞进箱体内（recessed 进壳）而非箱外 `base_chassis` 下 → 违反 split 的"轮在箱外"修复（tire_top ≤ shell_base_z），门下脚轮穿模。
- fixed_top_grab 仍发 `pull_handle` part / PRISMATIC → 与样本 run_tests 的 `"pull_handle" not in part_names` 断言冲突；fixed_grab 是纯 visual 无 joint。
- 把连续尺寸 / 颜色 / palette_style 当新 candidate 塞进 named slot → 不是结构差异，违反 §2.4。
- 把 source map 的 `inline_2` 当真发 2 轮的独立 wheel_system module（无样本支持）→ 应作 N=2 multiplicity 子路径处理 + 阻塞说明。

## 与相邻类别的边界

- 不该混入：**硬壳储物木箱 / chest（`bag_suitcase_box`）**——板条侧壁 + 金属角件的静置卧式单体箱，无脚轮 / 无伸缩拉杆 / 后铰平盖为主；本类是直立、带万向轮、带拉杆的拖行硬壳行李箱（核心身份 = wheel multiplicity + telescoping/grab handle）。
- 不该混入：**软包 suitcase / 旅行袋**——拉链软壳 + 织物，本类是 rounded-rect 硬壳 mesh，无 zipper 软体语义。
- 不该混入：**工具拉杆箱（`rolling_toolbox_with_telescoping_handle`）**——同有轮 + 拉杆但以分层托盘 / 内格为身份；本类以硬壳箱身 + 行李形态为身份（如需可单独 slug）。
- 不该混入：**手提公文 / 化妆箱（无轮）**——缺脚轮 multiplicity，出本类。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) wheel_system 槽定为 yoke vs swivel **结构** candidate、轮**数量**单列 multiplicity 轴（修正 source map 的 inline_2 误标，实测 parent 4 轮）；(2) **N=2/3 无样本** → wheel_count 首版 sweep 采样域是锁 {4}、{2,4} 还是全 {2,3,4} + N=3 gating；(3) 空心契约（front_lid/split `.cut()`/`.shell()` 空心、integrated 实心）+ allow_overlap reason 随实心 / 空心匹配；(4) B/C 槽降到 2 candidate（样本池仅 5、每轴 1 fork）是否接受；(5) Topology target 36<300 的说明是否接受（本小类真实结构上限）；(6) PALETTE_STYLES 5 colorway 中 3 个锚定样本实测、2 个换 shell 主色是否符合"observed across sources"要求）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：`_build_hollow_shell`（frontlid cadquery `.cut()`，front_lid 用）、`_make_half_shell`（split cadquery `.shell()`，split_side 用）、`ExtrudeGeometry.from_z0`（实心壳，integrated 用）；`_add_spinner_caster`（swivel 单脚轮工厂，可直接作 wheel_count copy-logic 源，yoke 基线另写简单 yoke 工厂）；`_build_grab_handle_mesh`（spline tube，fixed_grab 用）；`_build_flap_panel`（front_flap mesh）。
- captured 接口 allow_overlap：`run_luggage_bag_tests` 里逐机构补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（parent L204-270、frontlid L294-333、split L378-444、spinner4 L273-331、fixedgrab L246-266）。**注意 reason 字符串随壳实心 / 空心切换**（"solid shell proxy" / "hollow shell top wall"）。
- conditional 范围解析顺序：先采 body_opening / wheel_system / handle_system / N → 解析 handle_travel（仅 telescoping）/ lid_open_angle（仅 front/split）/ wheel_span（仅 N≥2）/ SHELL_Z0 抬高（仅 split，轮在箱外）→ 采 box/wheel independent scale → 派生 WALL_T（hollow）→ 投影两条 inequality。
- N 复制：脚轮**带独立 CONTINUOUS joint**（与 cushion 粉盘 inline 无 joint 不同）；`for i in range(N)` 发射 `wheel_{i}` + `wheel_{i}_spin` + 硬件 `{yoke|swivel_plate|fork}_{i}`；placement 绝对式（N=4 四角 / N=2 直列对）。
- split_side 的轮在箱外 `base_chassis` skid plate 下（SHELL_Z0 抬高至 2·WHEEL_R+clearance），与其余壳的"轮 recessed 进壳底 well"是不同接地策略 → wheel_count placement 须按 body_opening=split 切换抬高。
- 参考模板（review 通过后选读）：`agent/templates/Accessories_Cushion.py`（同 mixed pattern：固定 named slots + `("count", f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 helper + 兼容矩阵 gating + captured-pin allow_overlap + PALETTE_STYLES 范式，本类可同构改编）；`drawer_cabinet_with_sliding_drawers.py`（PRISMATIC + captured，对 telescoping handle）；`single_revolute_hinge` / `wheelie_bin_with_hinged_lid`（REVOLUTE 盖 closed-pose，对 front_lid/split）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A/B/C（parent 基线）| integrated_shell + yoke_wheels + telescoping_pull | rec_hard-shell-rolling...110d261f | 实心壳 L48-104 / yoke+轮 CONTINUOUS L106-187 / pull_handle PRISMATIC L117-152 | root 实心壳 + yoke 4 轮 spin-Y 基线 + 伸缩拉杆基线 + N 复制 placement 源 |
| S1 | A | front_lid_flap | rec_luggage_var_frontlid | `_build_hollow_shell` L53-84 / `front_flap` + `body_to_flap` REVOLUTE L185-209 | 空心薄壁壳（`.cut()`）+ 正面翻盖 REVOLUTE -X |
| S2 | A | split_side | rec_luggage_var_split_side | `_make_half_shell` L63-95 / `door` + `body_to_door` REVOLUTE L218-283 | 空心两半壳（`.shell()`）+ 纵向侧门 REVOLUTE +Z 立轴 + 轮在箱外 chassis |
| S3 | B | swivel_caster | rec_luggage_var_spinner4 | `_add_spinner_caster` L61-146 / for-loop L216-221 | 万向脚轮硬件（swivel plate + fork + TireGeometry）spin-X + 单脚轮工厂（wheel_count copy 源）|
| S4 | C | fixed_top_grab | rec_luggage_var_fixedgrab | `_build_grab_handle_mesh` L41-58 / grab L95-111 | 固定顶提把（spline tube 纯 visual 无 joint）|
</content>
</invoke>
