# built_in_oven — Modular Spec

> 来源小类：`picture/Other/Built-in oven`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Other__Built-in_oven.md`。
> **"Built-in oven" 在此 = 嵌入式箱体厨电（前开门的内嵌单/双腔电烤箱 + 紧凑微波炉家族）**：一只接地的中空箱体（fascia 面板 + shell + 控制条），前面开口，门绕一条铰线开合，腔内可装滑出烤架，前面板可有旋钮。
>
> **同步状态**：本 spec 引用的 9 个 5 星样本（2 个 parent + 7 个 fork 槽位/多重性变体）已同步进本仓库 `data/records/`，rating=5。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一核对，单 revision）。引用以 part / joint / helper **名字**为准（`oven_body` / `door` / `door_leaf_{i}` / `shelf_rack` / `rack_{i}` / `knob_{i}` / `body_to_door` / `body_to_door_leaf_{i}` / `body_to_rack_{i}` / `knob_{i}_spin` / `_body_shell` / `_front_fascia` / `_cavity_liner` / `_door_frame` / `_door_leaf_frame` / `_wire_rack` / `_add_door` / `_add_rack` / `KnobGeometry` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `built_in_oven` |
| template path | `agent/templates/Other_Built_in_oven.py` |
| test path (optional) | `tests/agent/test_built_in_oven_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slot: `door_mechanism`（主机构）+ **三根独立多重性轴** `door_count` / `rack_count` / `knob_count`）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（2 parent + 7 fork 变体；均 converged，compile success、≥1 非 fixed joint、workbench-only）|
| read_count | 9（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 9/9 全部被采纳，无未采用样本 |

阅读要点（用于槽位/多重性分解）：

- **两个 parent 是两套坐标系家族**，spec 必须统一到一个：
  - **P1 家族**（`rec_...363e4e6b` 单腔壁挂烤箱 + 全部 4 个 door/rack 变体）：**+Y 指向柜内、-Y 朝用户**；fascia 在 XZ 平面，宽度沿 **X**；接地于 z=0。门 = drop-down REVOLUTE **axis=+X**（底铰下翻 0..π/2）；rack = PRISMATIC **axis=(0,-1,0)** 向 -Y 拉出（travel 0.35）。
  - **P2 家族**（`rec_...6c671696` 紧凑微波炉 + 2 个 knob 变体）：**+X 指向用户前方**、宽度沿 **Y**；门 = REVOLUTE **axis=+Y**；旋钮 = CONTINUOUS **axis=+X**（前法向）。
  - 这两套是同一**结构家族**（箱体 + 前开门 + 控制面板），只是坐标轴标注不同。**本模板采用 P1 坐标系作为唯一约定**（多数门/rack 源 + door_count 工厂均建于此），knob 轴在 P1 系下改为**前法向 -Y**、旋钮沿 **X 等距**（语义不变：CONTINUOUS 绕前法向自转 + off-axis pointer 证旋转）。详见 §每槽位 emits 的 knob 注记。
- **door_mechanism（主机构槽，真正的 joint 拓扑轴）**：drop_down（1×REVOLUTE +X 底铰）/ side_hinge（1×REVOLUTE -Z 侧铰）/ french_double（2×REVOLUTE ±Z 镜像中线对开）→ joint **数量与轴向**不同，是真正的拓扑变化。
- **door_count（多重性轴 1）**：N 个炉腔沿 **+Z 叠层**，每腔各有完整的 cavity 切口 + liner + rail + 一扇门（+ 各自 rack）。N=2 变体已用 `_add_door`/`_add_rack` 工厂 + `OVEN_HINGE_Z = [0.058 + i*UNIT_PITCH]` 实现整腔复制，是 copy-logic 直接源。
- **rack_count（多重性轴 2）**：单腔内 N 层滑出烤架，沿 **+Z 等距**，每层各 PRISMATIC + 两侧 `shelf_rail_{ri}_{si}`。N=2/3 变体用 `RACK_Z` 偶分区 / 显式列表实现。
- **knob_count（多重性轴 3）**：前面板 N 个旋钮，**等距并排**，每钮各 CONTINUOUS 自转 + off-axis `knob_pointer`。N=2/4/6 变体用 `KNOB_YS` 列表 + `for i, ky in enumerate(...)` 实现。
- **非拓扑差异**（不另立 candidate）：fascia/shell 尺寸、控制条 display/icon 布局、handle 样式、material 配色——只换尺寸/装饰/颜色，归入连续 scale 或 `palette_style`。

## 核心身份

一只**嵌入式箱体厨电**（前开门内嵌烤箱 / 紧凑微波炉）：接地的中空 `oven_body`（root，由 outer shell + front fascia 开口 + cavity liner + 固定 control strip（dark touch glass + clock display + touch icons）组成），前面通过铰线连一扇或多扇 `door`（gray frame + frosted 窗 + 顶/侧 bar handle），腔内坐 0..N 层滑出 `rack`（chrome wire grid，靠两侧 `shelf_rail` 承托），前面板可有 0..N 个旋钮 `knob`（KnobGeometry cap + off-axis pointer）。活动语义 = **门的开合**（底铰下翻 REVOLUTE +X / 侧铰 REVOLUTE -Z / 法式双开 2×REVOLUTE ±Z）+ **烤架滑出**（PRISMATIC -Y）+ **旋钮自转**（CONTINUOUS 前法向）。默认成熟域：door_mechanism × door_count∈[1,3] × rack_count∈[0,5] × knob_count∈[0,8] 的内嵌单/双腔烤箱与微波炉，fascia ≈0.60 m 宽。

不该混入：
- **独立落地灶 / range / stove（带灶头 burner 的炉灶台）**——本类是**嵌入式无灶头箱体**（前开门 + 腔体），不含灶台燃烧器/锅架；灶台是另一 slug（`stove`）。
- **洗碗机 dishwasher**——虽同为前下翻门 + 滑出架箱体，但洗碗机身份在于喷淋臂/水路，且已有独立模板 `dishwasher_with_dropdown_door_and_sliding_racks`；本类是热腔烤箱/微波炉，无水路。
- **抽屉柜 / drawer cabinet**——纯 PRISMATIC 抽屉无旋转门、无烤腔身份。
- **普通对开门橱柜 cabinet**——无控制面板/旋钮/烤腔，非厨电。

## 槽位 + 候选模块表

> **建模注记**：唯一真正改 joint 拓扑的 named slot 是 `door_mechanism`（门的开合机构）。其余三根是**多重性轴**（door_count / rack_count / knob_count），它们改变 part 数与 joint 数（复制整腔 / 复制烤架 / 复制旋钮），编入 `slot_choices_for_seed` 作拓扑维度（见 §8/§9）。`oven_body`（箱体）是固定 root，不作独立候选 slot（单一形态，随 door_count 派生 N 腔 mesh）。

### Slot A：door_mechanism（**主机构槽**——炉门开合，决定门的 part 树与 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| drop_down_bottom_hinge（基线） | rec_...363e4e6b（P1）| `_door_frame` L94-101 / door part+visuals L186-219 / `body_to_door` REVOLUTE L221-229 | eligible if compatible | 单 `door` child，底铰下翻 **1×REVOLUTE** axis=(1,0,0)，origin=(0,HINGE_Y,HINGE_Z=底沿)，lower=0 闭合 / upper=π/2 平展；含 `hinge_arm_{i}` 销臂（captured into body slot，allow_overlap）|
| side_hinge_single | rec_variant-door-mechanism-side-hinge-single-...e2a585a2 | `_door_frame` L103-122 / door part+visuals L208-244 / `body_to_door` REVOLUTE L246-254 | eligible if compatible | 单 `door` child，左竖铰侧开 **1×REVOLUTE** axis=(0,0,-1)，origin=(-OPEN_W/2,HINGE_Y,Z_MID)，free（右）边向 -Y 摆出；`hinge_arm_{i}` 入左 jamb |
| french_double_door | rec_variant-door-mechanism-french-double-door-...4f000702 | `_door_leaf_frame` L125-141 / leaf 循环 L218-278 / 2×REVOLUTE ±Z L264-278 | eligible if compatible | **两片叶** child（`door_leaf_0` 左 / `door_leaf_1` 右，各覆盖半宽），**2×REVOLUTE** 镜像（left axis=(0,0,-1) origin=(-OPEN_W/2,..)，right axis=(0,0,1) origin=(+OPEN_W/2,..)），中线 LEAF_GAP 对开，各自独立开 |

> door_mechanism 第 4 候选（抽屉式 warming-drawer 烤箱，门=PRISMATIC 抽出）**source map 标注留待后续补格**，当前无 5 星源 → 不进 candidate 表（避免凭空发明）。3 候选满足 §2.3「目标 3-6，池不足可降到 2」（此处 3，达标），不构成单候选 slot。

## 槽位图（slot graph）

pattern: mixed（固定 named slot `door_mechanism` 挂到 root `oven_body`；三根多重性轴 `door_count` / `rack_count` / `knob_count` 各自在 body 上 N 次复制 cavity-unit / rack / knob）

```
oven_body (root, 坐地 z=0; outer shell + front fascia 开口 + cavity liner + control strip;
           door_count 决定沿 +Z 叠 N 腔，每腔各 cavity 切口/liner/rail)
  │
  ├── [door_mechanism slot]  (互斥三选一；当 door_count=N 时每腔各装一份此机构)
  │     ├─ drop_down_bottom_hinge : door ──[body_to_door: REVOLUTE axis=+X, origin=(0,HINGE_Y,腔底沿)]
  │     ├─ side_hinge_single      : door ──[body_to_door: REVOLUTE axis=-Z, origin=(-OPEN_W/2,HINGE_Y,Z_MID)]
  │     └─ french_double_door     : door_leaf_0 ─[body_to_door_leaf_0: REVOLUTE axis=-Z, origin=(-OPEN_W/2,..)]
  │                                 door_leaf_1 ─[body_to_door_leaf_1: REVOLUTE axis=+Z, origin=(+OPEN_W/2,..)]
  │
  ├── [door_count multiplicity 轴]  per-cavity unit i∈range(Nd), 沿 +Z 叠层 UNIT_PITCH
  │      复制对象 = cavity 切口 + cavity_liner_{i} + shelf_rail_{i}_* + door_{i}(机构) + rack_{i}(若有)
  │      命名 door_{i} / body_to_door_{i}（Nd=1 退化为单 door）
  │
  ├── [rack_count multiplicity 轴]  per-cavity 内 rack_{i} i∈range(Nr), 沿 +Z 等距
  │      复制对象 = 单层 wire rack ──[body_to_rack_{i}: PRISMATIC axis=(0,-1,0)] + 两侧 shelf_rail_{ri}_{si}
  │      命名 rack_{i} / body_to_rack_{i}（Nr=0 无烤架；Nr=1 退化单 rack）
  │
  └── [knob_count multiplicity 轴]  前面板 knob_{i} i∈range(Nk), 沿 X 等距并排
         复制对象 = KnobGeometry cap + off-axis knob_pointer ──[knob_{i}_spin: CONTINUOUS axis=前法向]
         命名 knob_{i} / knob_{i}_spin（Nk=0 无旋钮，纯触控面板=各 oven parent）
```

接口点位与 joint 语义：
- **door_mechanism 接口（互斥）**：所有门机构挂在 `oven_body` 的腔口铰线硬件上。
  - drop_down：底沿铰线，REVOLUTE axis=(1,0,0)，origin=(0,HINGE_Y,腔底 HINGE_Z)；`hinge_arm_{i}` 销臂 captured into body_shell/cavity_liner/front_fascia 底缘槽（element-scoped allow_overlap）。q=0 竖直闭合 / q=π/2 平展前伸 -Y。
  - side_hinge：左竖铰，REVOLUTE axis=(0,0,-1)，origin=(-OPEN_W/2,HINGE_Y,Z_MID)；`hinge_arm_{i}` 入左 jamb（allow_overlap）。q=0 闭合 / q=π/2 free 边摆向 -Y。
  - french_double：左/右竖铰各一，REVOLUTE axis=∓Z（origin 左/右 jamb），两叶中线 LEAF_GAP 对接、各自独立 0..π/2 开。
- **door_count 接口**：每腔 i 是完整 cavity-unit（cavity 切口 cz=hinge_z+0.20、`cavity_liner_{i}`、`shelf_rail_{i}_*`、门 + rack），沿 +Z 以 `OVEN_HINGE_Z=[OPEN_Z0 + i·UNIT_PITCH]` 绝对式叠放；门机构由 door_mechanism 决定（每腔同一机构）。control strip 落在最顶腔上方 fascia。
- **rack_count 接口**：每层 rack 是 base 凹腔内独立 part，PRISMATIC axis=(0,-1,0) 向 -Y 拉出（travel 0.35），靠两侧 `shelf_rail_{ri}_{si}` 承托（`expect_gap` z 接触）；rack 在腔深方向保留 retained insertion（`expect_overlap` y≥0.04）。沿 +Z 在腔内 usable z 范围 `[_CAVITY_Z0,_CAVITY_Z1]` 偶分区。
- **knob_count 接口**：每钮挂 control strip 前面（`knob_cap` 0.5 mm 坐入 strip 面，captured allow_overlap），CONTINUOUS 绕前法向自转；off-axis `knob_pointer` 半转后移到对侧证旋转。沿 X 等距并排（P1 系；P2 源沿 Y，统一到 P1 时改 X）。
- **mating policy**：所有 hinge 是 `hinge_arm`/`hinge_lug` captured-pin（销臂入 body 槽）、rack 是 rail-on-rail 承托、knob 是 cap-on-strip captured —— 几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：所有门/叶 q=0 闭合（lower=0），rack q=0 坐腔内，knob q=0。
- **互斥 / 可选 / 派生**：door_mechanism 三候选互斥（一次只一种门机构，整机统一）；door_count / rack_count / knob_count 三根多重性轴**正交**（任意组合合法，受 §9 兼容矩阵的 N 上限与 french×多腔配额约束）。

## 每槽位 Module Emits / Interfaces

### Slot root / oven_body（固定 root；door_count 决定 N 腔 mesh）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `oven_body`（visual: `body_shell` 中空外壳 + `front_fascia` 开口面板 + `cavity_liner`(_{i}) 腔衬 + `shelf_rail_*` 承托轨 + control strip 组 `control_glass`/`clock_display`/`clock_digits`/`touch_icon_{n}`）| P1 `_body_shell` L72-75 / `_front_fascia` L78-85 / `_cavity_liner` L88-91 / control L154-183；多腔版 door_count `_body_shell` L82-98 / `_front_fascia` L101-117 / `_cavity_liner(hz)` L120-133 |
| internal joints | 无（body 是 root）| — |
| upstream interface | root（坐地 z=0，无父）| — |
| downstream interface | 腔口铰线硬件（供 door_mechanism）+ 凹腔 + `shelf_rail`（供 rack）+ control strip 前面（供 knob）| P1 L154-163 |

### Slot A / door_mechanism — drop_down_bottom_hinge
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door`（visual: `door_frame` 含 window 切口 + `window_glass` + `handle_bar` + `handle_post_{i}` + `hinge_arm_{i}`）| P1 `_door_frame` L94-101 / door L186-219 |
| internal joints | `body_to_door` REVOLUTE axis=(1,0,0)，origin=(0,HINGE_Y,HINGE_Z=腔底沿)，lower=0 / upper=π/2 | P1 L221-229 |
| upstream interface | `hinge_arm_{i}` 销臂 captured into body_shell/cavity_liner/front_fascia 底缘槽（allow_overlap）| P1 run_tests L260-282 |

### Slot A / door_mechanism — side_hinge_single
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door`（door-local origin 在左竖铰线；`door_frame`+window / `window_glass` / `handle_bar` / `handle_post_{i}` / `hinge_arm_{i}` 入左 jamb）| side_hinge `_door_frame` L103-122 / door L208-244 |
| internal joints | `body_to_door` REVOLUTE axis=(0,0,-1)，origin=(-OPEN_W/2,HINGE_Y,Z_MID)，lower=0 / upper=π/2 | side_hinge L246-254 |
| upstream interface | `hinge_arm_{i}` 入左 jamb（body_shell/cavity_liner/front_fascia，allow_overlap）+ door_frame 入 fascia 厚度坐深 | side_hinge run_tests L287-319 |

### Slot A / door_mechanism — french_double_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_leaf_0`（左，local origin 左竖铰）+ `door_leaf_1`（右，local origin 右竖铰）各 `leaf_frame`+window / `window_glass` / `handle_bar`（近中线竖把手）/ `handle_post_{j}` | french `_door_leaf_frame` L125-141 / leaf 循环 L218-278 |
| internal joints | `body_to_door_leaf_0` REVOLUTE axis=(0,0,-1) origin=(-OPEN_W/2,HINGE_Y,Z_MID) + `body_to_door_leaf_1` REVOLUTE axis=(0,0,1) origin=(+OPEN_W/2,..)，各 lower=0/upper=π/2 | french L264-278 |
| upstream interface | 两叶 free 边中线 LEAF_GAP 对接（`leaf_frame` 互不重叠）；门面坐 fascia 前 | french run_tests L367-409 |

### door_count multiplicity（炉腔/炉门复制；改 part+joint 拓扑）
| emits | 描述 | 来源 |
|---|---|---|
| parts | per-cavity 复制 `cavity_liner_{i}` + `shelf_rail_{i}_{j}` + `door_{i}`(机构) + `rack_{i}`(若有)；`_add_door(model,body,i,hz)` / `_add_rack(model,body,i,hz)` 工厂 | door_count `_add_door` L169-217 / `_add_rack` L220-243 / loop L328-330 |
| joints | 每腔 `body_to_door_{i}` REVOLUTE（door_mechanism 决定轴）+ `body_to_shelf_rack_{i}` PRISMATIC | door_count L206-216, L232-242 |
| placement | `OVEN_HINGE_Z = [OPEN_Z0 + i·UNIT_PITCH for i in range(Nd)]` 沿 +Z 绝对叠层（UNIT_PITCH=0.492）；body shell/fascia 各腔切一份 cavity/opening | door_count L65, L82-117 |

### rack_count multiplicity（滑出烤架复制；改 part+joint 拓扑）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `rack_{i}`（`rack_grid` chrome wire）+ body 上 `shelf_rail_{ri}_{si}`（2 侧×Nr 高度）| rack_count(2) `_wire_rack` L114-124 / rail L156-163 / rack loop L245-263 |
| joints | 每层 `body_to_rack_{i}` PRISMATIC axis=(0,-1,0)，origin=(0,0.03,RACK_Z[i])，lower=0/upper=0.35 | rack_count(2) L254-262 |
| placement | `RACK_Z = [_CAVITY_Z0 + zone·(i+1)]` 偶分区（zone=(Z1-Z0)/(Nr+1)）沿 +Z 等距；N=3 用显式 `RACK_Z_POSITIONS=[0.13,0.27,0.41]` | rack_count(2) L65-70 / rack_count(3) L67-68 |

### knob_count multiplicity（前面板旋钮复制；改 part+joint 拓扑）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `knob_{i}`（`knob_cap` KnobGeometry mesh + off-axis `knob_pointer` box）| knob(2/6) `KnobGeometry` L306-312 / knob loop L313-328 |
| joints | 每钮 `knob_{i}_spin` CONTINUOUS，axis=前法向（P2 源 +X；P1 系统一为 -Y），origin 在 strip 前面 | knob(2/6) L329-337 |
| placement | `KNOB_YS` 等距列表（N=2:(-0.110,-0.050) / N=4:(-0.155..-0.005) / N=6:(-0.125..0.125)）`for i,ky in enumerate(KNOB_YS)`；P1 系沿 X 等距 | knob(2) L106 / knob(6) L106 / parent L106,313 |

> **knob 坐标系归一**：P2 源旋钮沿 fascia 宽度方向（其系为 Y）等距、自转轴=前法向（其系 +X）。本模板用 P1 系 → 旋钮沿 **X**（P1 宽度）等距、自转轴=**前法向 -Y**、`knob_cap` 由 +Z mesh 经 rpy pitch 朝前法向（照 P2 L318 的 pitch 思路改到 P1 前向）。语义（CONTINUOUS + off-axis pointer 半转移位）不变。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| door_mechanism | enum | drop_down_bottom_hinge / side_hinge_single / french_double_door | drop_down_bottom_hinge | choice | 由 deterministic procedural sampler 选；主机构（互斥，整机统一）| module table |
| door_count (Nd) | int | 声明域 [1,3]；sweep 采样域 [1,3]（偏小加权：1 高频、2 常见、3 长尾）| 1 | conditional→slot_choice | 编入 slot_choice 为 `("door_count", f"n{Nd}")`；沿 +Z 叠层；Nd 与 french/fascia 高联动（见不等式 + §8/§9）| door_count 变体 |
| rack_count (Nr) | int | 声明域 [0,5]；sweep 采样域 [0,4]（偏小加权：1-2 高频、0/3/4 较少、5 尾部）| 1 | conditional→slot_choice | 编入 slot_choice 为 `("rack_count", f"r{Nr}")`；每腔内沿 +Z 等距；Nr 受腔内净高 clamp（见不等式）| rack_count(2)/(3) |
| knob_count (Nk) | int | 声明域 [0,8]；sweep 采样域 [0,6]（偏小加权：0/2/4 高频、6 较少、8 尾部）| 0 | conditional→slot_choice | 编入 slot_choice 为 `("knob_count", f"k{Nk}")`；前面板沿 X 等距；Nk 受 fascia 宽 clamp（见不等式）| knob(2/4/6) |
| palette_style | enum | gray_steel / stainless_taupe / matte_black / cream_retro | gray_steel | palette | palette only，**不计入 slot_choice**；4 配色（见 §palette）| 各样本材质 |
| fascia_width_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 fascia/shell/door X 宽（保比例），clamp；影响 knob 沿 X 可用排距 | resolve clamp |
| cavity_height_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放单腔净高 → UNIT_PITCH / 腔内 usable z；影响 rack 可排层数与门高 | resolve clamp |
| body_depth_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 shell 深 BODY_D → rack travel 上限（≤ 腔深 − retained insertion）| resolve clamp |
| door_open_angle_scale | float | [0.88, 1.05] | 1.0 | independent | 缩放门/叶 REVOLUTE `upper`，clamp（保 ≤π/2·1.0，下翻门不超水平）| resolve clamp |
| rack_travel_scale | float | [0.85, 1.05] | 1.0 | conditional | 仅 Nr≥1 有效；缩放 PRISMATIC `upper`（≤ 腔深·body_depth_scale − 0.04 retained）| resolve clamp |
| knob_spacing_scale | float | [0.90, 1.10] | 1.0 | conditional | 仅 Nk≥2 有效；缩放前面板旋钮并排间距 | resolve clamp |
| (—) | constraint | — | — | inequality | **叠腔不超 fascia 高**：`OPEN_Z0 + Nd·UNIT_PITCH·cavity_height_scale ≤ FASCIA_H − ctrl_strip_h`；违反则减 Nd 或缩 UNIT_PITCH/腔高 | 接口 / clearance |
| (—) | constraint | — | — | inequality | **rack 不超腔内净高**：`Nr·rack_thickness + (Nr+1)·gap ≤ (_CAVITY_Z1−_CAVITY_Z0)·cavity_height_scale`；违反则按比例减 Nr 或缩 gap | 接口 / clearance（rack_count(3) L64-68 偶分区即此约束的实现）|
| (—) | constraint | — | — | inequality | **rack travel ≤ 腔深**：`RACK_TRAVEL·rack_travel_scale ≤ BODY_D·body_depth_scale − 0.04`（保 retained insertion ≥0.04）| 接口 / clearance |
| (—) | constraint | — | — | inequality | **knob 不超 fascia 宽**：`Nk·(KNOB_D) + (Nk-1)·gap·knob_spacing_scale ≤ FASCIA_W·fascia_width_scale − 2·margin`；违反则减 Nk 或缩 spacing | 接口 / clearance |
| (—) | constraint | — | — | conditional | **门面占满 fascia 开口**：每门/叶闭合 XZ 覆盖各自腔口（drop/side 单门全覆盖；french 两叶各覆盖半宽中线 LEAF_GAP 对接）| 接口 / closed pose |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 door_mechanism / Nd / Nr / Nk 的拓扑**。

### palette_style 配色（≥3，目标 4-6；从 5 星源材质提取，每 seed 采样一种）

| palette_style | 主壳/fascia | 门 frame | 控制条/display | 旋钮/把手 | 来源 |
|---|---|---|---|---|---|
| gray_steel（基线） | matte light-gray steel (0.80,0.80,0.81) | door_gray (0.62,0.62,0.64) | dark_glass (0.07,0.07,0.09)+pale digits | aluminum (0.78,0.79,0.82) / chrome_wire | P1 / 全 door·rack 变体 L120-130 |
| stainless_taupe | brushed stainless (0.78,0.79,0.80) | door_taupe (0.47,0.45,0.42) | strip_taupe (0.36,0.34,0.32)+display_glow 绿 | knob_metal (0.81,0.82,0.84) | P2 / knob 变体 L183-194 |
| matte_black | matte black (0.14,0.14,0.15) | gloss black (0.10,0.10,0.11) | dark_glass + cyan digits | brushed alloy 银 accents | 合成（厨电常见黑面板，从 dark_glass/display 系派生）|
| cream_retro | cream enamel (0.92,0.90,0.85) | cream frame + chrome trim | dark glass + amber digits | chrome bezel knobs | 合成（复古奶白珐琅烤箱，从 frosted/aluminum 系派生）|

> palette_style 是**纯材质映射**，不改任何 part/joint/尺寸/拓扑；4 配色覆盖灰钢/不锈钢-taupe/哑黑/奶白复古，前两者直接取自 5 星源，后两者为同色系合成现实配色。每 seed `rng.choice` 一种，写进 palette 不写进 slot_choice。

## Multiplicity / Copy Logic

**3 根独立 multiplicity 轴**（door_count / rack_count / knob_count）。每根各做一次加权采样、各自编进 `slot_choices`、各自 clamp、sweep 各自设上限。

### 轴 1：door_count（炉腔/炉门数，叠层多烤箱）
- **count_param**：`door_count`（模板变量 Nd / N_OVENS）。
- **N_range**：声明产品域 **[1,3]**（嵌入式叠层最多三腔；source map 建议 [1,3]）。`config_from_seed` sweep 采样域 **[1,3]**（偏小加权：1 高频、2 常见、3 长尾）。Nd=1 即单腔 parent（不进多腔循环）。
- **sampling domain**：`rng.choices((1,2,3), weights=(0.6,0.3,0.1))`；`resolve_config` clamp 任意外部 Nd 到 [1,3]，并按「叠腔不超 fascia 高」不等式回缩。
- **copied object**：整 cavity-unit——cavity 切口 + `cavity_liner_{i}` + `shelf_rail_{i}_*` + `door_{i}`(door_mechanism 机构) + `rack_{i}`(若 Nr≥1)。共享 `_add_door`/`_add_rack` 工厂。
- **naming**：`door_{i}` / `cavity_liner_{i}` / `body_to_door_{i}` / `body_to_shelf_rack_{i}`，`for i in range(Nd)`（door_count 变体 L328-330 已用此结构，直接作源）。
- **placement**：沿 +Z **绝对式**等距叠层 `OVEN_HINGE_Z=[OPEN_Z0 + i·UNIT_PITCH]`（UNIT_PITCH 随 cavity_height_scale 派生）；fascia/shell 各腔切一份。control strip 落顶腔上方。
- **joint policy**：每腔门各独立 REVOLUTE（轴由 door_mechanism 定），每腔 rack 各独立 PRISMATIC。
- **source/gating**：copy-logic 源取 door_count(N=2) 的 `_add_door`/`_add_rack` 工厂 + `OVEN_HINGE_Z`（L65,169-243,328-330）；Nd=1 取 parent 单 door（等价 range(1)）。Nd≥2 × french_double 见 §9 矩阵（多腔法式叶数翻倍，需配额限制或降级）。

### 轴 2：rack_count（单腔内滑出烤架数）
- **count_param**：`rack_count`（模板变量 Nr / RACK_COUNT）。
- **N_range**：声明产品域 **[0,5]**（含 Nr=0 无架的微波炉/纯热腔；现实烤箱 1-3 层多）。sweep 采样域 **[0,4]**（偏小加权：1-2 高频、0/3/4 较少、5 尾部）。
- **sampling domain**：`rng.choices((0,1,2,3,4), weights=(0.12,0.33,0.30,0.15,0.10))`；`resolve_config` clamp 到 [0,5] 并按「rack 不超腔内净高」不等式回缩。
- **copied object**：单层 `rack_{i}`（`rack_grid` chrome wire）+ 两侧 `shelf_rail_{ri}_{si}`，共享 `_wire_rack` 几何。
- **naming**：`rack_{i}` / `body_to_rack_{i}` / `shelf_rail_{ri}_{si}`，`for i in range(Nr)`（rack_count(2) L245-263 已用此结构）。
- **placement**：每腔内沿 +Z **绝对式**偶分区 `RACK_Z=[_CAVITY_Z0 + zone·(i+1)]`，zone=(_CAVITY_Z1−_CAVITY_Z0)/(Nr+1)（rack_count(2) L65-70）；与 door_count 联动时每腔各放一组 Nr 层。
- **joint policy**：每层独立 PRISMATIC axis=(0,-1,0) 向 -Y 拉出（travel=RACK_TRAVEL·rack_travel_scale），retained insertion ≥0.04。
- **source/gating**：源取 rack_count(2) 偶分区（L65-70,245-263）与 rack_count(3) 显式列表（L67-68）；Nr=0 时不发射任何 rack/rail（纯热腔，对应 P2 微波炉无架形态）；Nr=1 退化单 rack（parent 形态）。

### 轴 3：knob_count（前面板旋钮数）
- **count_param**：`knob_count`（模板变量 Nk）。
- **N_range**：声明产品域 **[0,8]**（含 Nk=0 纯触控面板=各烤箱 parent；旋钮式微波炉/灶控 2-6 常见）。sweep 采样域 **[0,6]**（偏小加权：0/2/4 高频、6 较少、8 尾部）。
- **sampling domain**：`rng.choices((0,2,3,4,6), weights=(0.30,0.22,0.13,0.22,0.13))`（含 0 与偶数常见档）；`resolve_config` clamp 到 [0,8] 并按「knob 不超 fascia 宽」不等式回缩。
- **copied object**：单旋钮 `knob_{i}`（KnobGeometry `knob_cap` + off-axis `knob_pointer`），共享同一 `knob_geo`（KnobGeometry 对象复用）。
- **naming**：`knob_{i}` / `knob_{i}_spin`，`for i,ky in enumerate(KNOB_YS)`（knob 变体 L313-337；P1 系改沿 X 等距）。
- **placement**：前面板沿 **X 绝对式**等距并排（以中心对称分布；间距随 knob_spacing_scale）。
- **joint policy**：每钮独立 CONTINUOUS，axis=前法向（P1 系 -Y），`knob_cap` 0.5 mm 坐入 control strip 面（captured allow_overlap）。
- **source/gating**：源取 knob(2)/(4 parent)/(6) 的 `KNOB_YS` + knob loop（L106,306-337）；Nk=0 时不发射旋钮（纯触控烤箱面板）；Nk≥2 走等距循环。

## 拓扑多样性审计

总组合数：door_mechanism(3) × door_count 采样数(3，{1,2,3}) × rack_count 采样数(5，{0,1,2,3,4}) × knob_count 采样数(5，{0,2,3,4,6}) = **3 × 3 × 5 × 5 = 225**。
（含 1×REVOLUTE / 1×REVOLUTE / 2×REVOLUTE 门拓扑 × 多腔×多 PRISMATIC × 多 CONTINUOUS 的 joint 数/类拓扑差异）

仅 door_mechanism(3) × door_count(3) × rack_count(5) = **45**，再叠 knob(5) → 225，**远超 ≥10 机械门控**。即便只看 door_mechanism × (Nr∈{0,1,2}) × (Nk∈{0,2,4}) = 3×3×3=27 也已稳过。

理由：door_mechanism 提供真正的 joint 拓扑差异（1 REVOLUTE 下翻 / 1 REVOLUTE 侧铰 / 2 REVOLUTE 法式双叶），三根多重性轴各改 part 数与 joint 数（叠腔→多门多 PRISMATIC、多 rack→多 PRISMATIC、多 knob→多 CONTINUOUS）。**Nd / Nr / Nk 必须各自编入 `slot_choices_for_seed`**（`("door_count",f"n{Nd}")` / `("rack_count",f"r{Nr}")` / `("knob_count",f"k{Nk}")`，对齐 cushion/shopping_bucket/fence_cascade），否则同机构不同 N 在 slot_choice 上无法区分，损失三整根拓扑维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` door_mechanism（经兼容矩阵），再各 `rng.choices` 加权 Nd∈[1,3] / Nr∈[0,4] / Nk∈[0,6]，再 uniform 各连续 scale。compatibility matrix 排除/降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：225 组合的采样空间下，1000-seed slot choice tuple distinct 预计接近组合上限（225，受真实结构词汇表约束，**超过建议的 ≥300**）。本小类多重性极强（三根独立 N 轴），拓扑空间充裕，连续 scale 与 palette 再细分外观。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 fascia_width_scale / cavity_height_scale / body_depth_scale / door_open_angle_scale（independent）+ rack_travel_scale（conditional@Nr≥1）/ knob_spacing_scale（conditional@Nk≥2）。全部 `resolve_config` clamp。采样契约：先采 door_mechanism + Nd/Nr/Nk（解析 conditional 范围：rack_travel 仅 Nr≥1、knob_spacing 仅 Nk≥2）→ 采 independent fascia/cavity/depth/angle scale → 派生（UNIT_PITCH 随 cavity_height_scale、门高随腔高）→ 用四条 clearance inequality（叠腔不超高、rack 不超净高、travel 不超深、knob 不超宽）投影/回缩。跨部件依赖（叠腔 vs fascia 高、rack 排布 vs 腔净高、travel vs 腔深、knob 排布 vs fascia 宽）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 hinge/rail origin、captured-pin/cap 接口、N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` door_mechanism（经兼容矩阵），再各 `rng.choices` 加权 Nd/Nr/Nk，再 uniform 各 scale | slot_choices_for_seed 含 `("door_count",f"n{Nd}")`/`("rack_count",f"r{Nr}")`/`("knob_count",f"k{Nk}")` 且与 build 一致 |
| compatibility matrix | (1) **french_double_door × door_count(Nd≥2)**：每腔双叶 → 叶数=2·Nd，几何与铰线密度高；gate 为 Nd≤2 配 french（Nd=3 时 french 降级为 drop_down 或 side_hinge）。 (2) **door_count(Nd≥2) × rack_count(Nr)**：多腔时每腔各放 Nr 层，total rack = Nd·Nr，受单腔净高约束（与单腔同 clamp，不额外 gate）；Nr 上限随 cavity_height_scale。 (3) **knob_count × fascia_width**：Nk 上限随 fascia 可用前面宽 clamp（Nk·KNOB_D+gap ≤ 宽−margin）；Nk=0 合法（纯触控）。 (4) **rack_count Nr=0** 合法（微波炉无架）；**knob_count Nk=0** 合法（纯触控烤箱）；但 Nr=0 且 Nk=0 且 door 闭合仍是合法纯箱体（至少 1 门保证 ≥1 非 fixed joint）。 (5) door_mechanism 与三根 N 轴正交（除 french×Nd≥3 降级外）。 | 无 floating / collision / 叠腔超高 / rack 超净高 / travel 超深 / knob 超宽 / french 多腔铰线撞 / 门不覆盖腔口 |
| controlled local variation | 6 个 clamped scale（fascia_width/cavity_height/body_depth/door_open_angle independent + rack_travel@Nr≥1/knob_spacing@Nk≥2 conditional），每 build 统一 | 比例变化不破坏 hinge/rail origin、captured 接口、门覆盖、rack 承托、retained insertion、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构/逐轴 QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| door_mechanism | 3 | yes | yes | 1 REVOLUTE 下翻 / 1 REVOLUTE 侧铰 / 2 REVOLUTE 法式（互斥主机构）|
| door_count (Nd) | 3（采样域 {1,2,3}，1 高频 / 3 长尾）| yes | yes | 多重性轴，编入 slot_choice |
| rack_count (Nr) | 5（采样域 {0,1,2,3,4}，含 0）| yes | yes | 多重性轴，编入 slot_choice |
| knob_count (Nk) | 5（采样域 {0,2,3,4,6}，含 0）| yes | yes | 多重性轴，编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("door_count",f"n{Nd}")` / `("rack_count",f"r{Nr}")` / `("knob_count",f"k{Nk}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，Nd⊆[1,3] / Nr⊆[0,5] / Nk⊆[0,8]
- `resolve_config` clamp Nd/Nr/Nk 到声明域、各 scale clamp 到声明范围；rack_travel/knob_spacing 为 conditional 随 Nr/Nk 解析；四条 clearance inequality（叠腔不超高、rack 不超净高、travel 不超深、knob 不超宽）在 resolve 内投影/回缩
- compatibility matrix / gating 阻止非法组合（french×Nd≥3 降级；Nk 超宽减数；门必覆盖腔口；至少 1 门保 ≥1 非 fixed joint）
- 连续 scale clamp 后不破坏 hinge/rail/cap origin、captured-pin/cap 接口、门覆盖、rack 承托/retained insertion、N 复制
- 关键 joint：drop_down `body_to_door` REVOLUTE axis≈(1,0,0)；side_hinge `body_to_door` REVOLUTE axis≈(0,0,-1)；french `body_to_door_leaf_0/1` 2×REVOLUTE 镜像 ∓Z/±Z；rack `body_to_rack_{i}` PRISMATIC axis≈(0,-1,0) upper≈0.35；knob `knob_{i}_spin` CONTINUOUS axis=前法向
- captured-pin / cap / rail：element-scoped `allow_overlap`（`hinge_arm_{i}`↔body_shell/cavity_liner/front_fascia；`knob_cap`↔control_strip；多腔 `hinge_arm_{i}`↔`cavity_liner_{i}`），照搬各样本 run_tests 的 allow_overlap 段（P1 L260-282、side_hinge L287-319、knob L358-375、door_count L347-360）
- copied object 遵循 `door_{i}` / `rack_{i}` / `knob_{i}` 命名 + 绝对式等距 placement（door +Z 叠层 / rack +Z 等距 / knob X 等距）+ 每复制件独立 joint
- grandfather：所有 hinge/rail/cap captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守
- 坐标系统一：整模板用 P1 系（+Y 柜内 / -Y 用户前 / 宽沿 X），knob 轴归一到前法向 -Y、沿 X 等距

## Reject cases

- 把 Nd/Nr/Nk 当普通 int 参数、不进 slot_choice → 同机构不同 N 的 slot_choice 同形，损失三根拓扑维度（违反 §8/§9 硬要求）。
- 混用 P1/P2 两套坐标系（门 axis +X 但 knob axis 还按 P2 +X 沿 Y 排）→ 旋钮自转轴与门坐标系不一致、几何错位；必须全程 P1 系（knob 轴=前法向 -Y、沿 X 排）。
- french_double_door 在 Nd=3（六叶）不降级 → 铰线密度/几何过载；必须 gate（french 限 Nd≤2，否则降级 drop/side）。
- rack 行程超过腔深、retained insertion <0.04 → rack 脱出腔体；travel 必须 ≤ 腔深−0.04（§7 不等式）。
- 把门/叶/rack/knob rest pose 设成张开/拉出/转角而非 q=0 闭合坐位 → current-pose 与 viewer 目检不符（所有样本闭合 lower=0）。
- hinge/rail/cap origin 放在腔中心或任意点而非真实铰线/导轨/strip 面 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 给 captured `hinge_arm`/`knob_cap` 补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- knob/rack 间距过大致超 fascia 宽/腔净高 → §7 不等式 FAIL；须按比例缩间距或减 N。
- 把连续尺寸/颜色/材质（palette_style / fascia scale）当新 candidate 塞进 door_mechanism slot → 不是结构差异。
- 把灶头 burner / 锅架（落地灶 stove）或喷淋臂（dishwasher）混入 → 出类，本类是无灶头无水路的嵌入式热腔箱体。
- Nd=0（无门无腔）→ 无 ≥1 非 fixed joint 且失类；至少保 1 门 1 腔。

## 与相邻类别的边界

- 不该混入：**落地灶 / range / 灶台 stove（带灶头 burner + 锅架）**——本类是嵌入式无灶头箱体（前开门 + 热腔），灶台燃烧器是另一结构家族（独立 slug `stove`）。
- 不该混入：**洗碗机 dishwasher**——虽同为前下翻门 + 滑出架，但身份在喷淋臂/水路；已有独立模板 `dishwasher_with_dropdown_door_and_sliding_racks`，本类是热腔烤箱/微波炉无水路。
- 不该混入：**抽屉柜 / drawer cabinet**——纯 PRISMATIC 抽屉、无旋转门/控制面板/烤腔。
- 不该混入：**普通橱柜 cabinet**——无控制条/旋钮/烤腔，非厨电箱体。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **坐标系统一到 P1**（+Y 柜内 / 宽沿 X），knob 轴归一为前法向 -Y、沿 X 等距——是否接受这一归一（vs 拆成 P1 单腔系 与 P2 微波炉系 两个 slug）；(2) 三根多重性轴 N_range：door_count [1,3] / rack_count [0,5] / knob_count [0,8]（含 Nr=0 微波炉、Nk=0 纯触控）是否合理；(3) french_double × Nd≥3 的降级策略（限 french≤2 腔）是否接受；(4) door_count×rack_count 时 total rack=Nd·Nr 是否需额外配额 gate；(5) palette_style 4 配色（gray_steel/stainless_taupe 取自源 + matte_black/cream_retro 合成）是否够现实；(6) door_mechanism 第 4 候选 warming-drawer 留待补格是否 OK）|

## 模板实现备注（可选）

- 共享 helper：`_body_shell`/`_front_fascia`/`_cavity_liner`（多腔版接受 hinge_z 列表，从 door_count L82-133 改编）、`_door_frame`（drop/side 复用，side 改 door-local origin 到左竖铰）、`_door_leaf_frame`（french）、`_wire_rack`（rack 复用，N 层共享几何）、`KnobGeometry`+`knob_geo`（knob 复用）、`_add_door`/`_add_rack`（door_count 工厂，作多腔/多架统一入口）。
- captured 接口 allow_overlap：`run_built_in_oven_tests` 里逐机构/逐轴补 element-scoped `allow_overlap`（hinge_arm↔body_shell/cavity_liner/front_fascia / knob_cap↔control_strip），照搬各样本 run_tests 段（P1 L260-282、side_hinge L287-319、french（无 hinge_arm overlap，门坐 fascia 前）、door_count L347-360、knob L358-375）。
- conditional 范围解析顺序：先采 door_mechanism / Nd / Nr / Nk → 解析 rack_travel（仅 Nr≥1）/ knob_spacing（仅 Nk≥2）/ french×Nd 降级 → 采 fascia/cavity/depth/angle independent scale → 派生 UNIT_PITCH/门高 → 投影四条 clearance inequality。
- N 退化：Nd=1 用单 door（不进多腔循环，等价 range(1)）；Nr=0 不发射 rack/rail；Nk=0 不发射旋钮；Nr=1/Nk≥2 走 `for i in range(N)`。
- 参考模板：`agent/templates/Accessories_Cushion.py`（同 mixed pattern：固定 named slot + 多重性轴进 slot_choice + 绝对式 placement + 共享 mesh 复用 + 兼容矩阵 gating + captured-pin allow_overlap）；`agent/templates/dishwasher_with_dropdown_door_and_sliding_racks.py`（同为前下翻门 + 滑出架箱体，door REVOLUTE + rack PRISMATIC 的 origin/承托/retained insertion 范式可直接借）；`agent/templates/Bag_Suitcase_Shopping_bucket.py`（`("count",f"n{N}")` 进 slot_choice + 绝对式 N 复制骨架）。

## Module Source Index

| source_id | slot/轴 | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | root + door_mechanism（基线）| oven_body + drop_down + single rack | rec_...363e4e6b（P1）| `_body_shell` L72-91 / `_front_fascia` L78-85 / `_cavity_liner` L88-91 / `_door_frame` L94-101 / door+REVOLUTE L186-229 / `_wire_rack`+PRISMATIC L104-114,239-247 / allow_overlap L260-282 | 箱体 root + 下翻门基线 + 单架 + captured-pin 范式 + control strip |
| S2 | root + 坐标系 + knob 轴 | cabinet_body + drop_down(P2) + 4 knob | rec_...6c671696（P2）| `_cabinet_shell_shape`/`_trim_frame_shape`/`_door_panel_shape` L115-172 / door REVOLUTE L295-303 / KnobGeometry+knob loop L306-337 / allow_overlap L358-375 | knob CONTINUOUS+pointer 范式 + KnobGeometry 用法（坐标归一到 P1）+ stainless_taupe 配色 |
| S3 | door_mechanism | side_hinge_single | rec_variant-door-mechanism-side-hinge-single-...e2a585a2 | `_door_frame` L103-122 / door L208-244 / `body_to_door` REVOLUTE -Z L246-254 / allow_overlap L287-319 | 侧铰单门（REVOLUTE -Z + door-local 左竖铰 origin）|
| S4 | door_mechanism | french_double_door | rec_variant-door-mechanism-french-double-door-...4f000702 | `_door_leaf_frame` L125-141 / leaf 循环 L218-278 / 2×REVOLUTE ±Z L264-278 | 法式双叶（2×REVOLUTE 镜像 + 中线对接）|
| S5 | door_count（multiplicity）| Nd=2 整腔复制 | rec_variant-door-count-2-make-it-a-double-...3d0a0f67 | 多腔 `_body_shell` L82-98 / `_front_fascia` L101-117 / `_cavity_liner(hz)` L120-133 / `OVEN_HINGE_Z` L65 / `_add_door` L169-217 / `_add_rack` L220-243 / loop L328-330 | door_count copy-logic 源（整 cavity-unit 工厂 + +Z 叠层）|
| S6 | rack_count（multiplicity）| Nr=2 偶分区 | rec_variant-rack-count-2-fit-...303083cb | `RACK_Z` 偶分区 L65-70 / `shelf_rail_{ri}_{si}` L156-163 / rack loop L245-263 / allow_overlap L278-299 | rack_count copy-logic 源（偶分区 + 每层 PRISMATIC + 承托轨）|
| S7 | rack_count（multiplicity）| Nr=3 显式列表 | rec_variant-rack-count-3-fit-...541d21da | `RACK_Z_POSITIONS=[0.13,0.27,0.41]` L67-68 | rack_count N=3 placement 源（三层等距）|
| S8 | knob_count（multiplicity）| Nk=2 | rec_variant-knob-count-2-reduce-...47d387a5 | `KNOB_YS=(-0.110,-0.050)` L106 / knob loop+pointer L313-337 | knob_count N=2 copy-logic 源 |
| S9 | knob_count（multiplicity）| Nk=6 | rec_variant-knob-count-6-increase-...16d89608 | `KNOB_YS=(-0.125..0.125)` L106 / knob loop L313-337 | knob_count N=6 copy-logic 源（等距 6 钮）|
