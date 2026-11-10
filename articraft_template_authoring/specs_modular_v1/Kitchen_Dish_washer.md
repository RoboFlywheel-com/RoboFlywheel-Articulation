# dish_washer (freestanding dishwasher) — Modular Spec

> 来源小类：`picture/Kitchen/Dish washer`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Kitchen__Dish_washer.md`。
> **"dish_washer" 在此 = 独立式洗碗机（freestanding dishwasher）：中空 `cabinet` 柜体 + 开门 / 抽屉机构 + N 个滑出式碗篮 + 控制 / 把手条。不是冰箱 / 冷柜（freezer，无碗篮 / 无放下式门）、不是烤箱（oven，无碗篮 / 无滑轨）、不是普通橱柜 / 抽屉柜（cabinet / chest，无洗涤 tub liner / 无碗篮 / 无控制面板）。**
> 结构家族 = 一个中空 `cabinet`（root）—— 凹陷 `kick_plinth`、拉丝外壳（`side_wall_{0,1}` / `back_wall` / `cabinet_floor` / `cabinet_ceiling`）、抛光 tub liner（`tub_wall_{0,1}` / `tub_back_panel` / `tub_floor`）、侧 `rack_rail_{i}` 滑轨、悬挑 `top_slab`。开门机构（Slot A）、碗篮几何（Slot B）、控制 + 把手（Slot C）是三个独立结构槽；**滑出式碗篮栈是 multiplicity 主轴（rack_count）**。坐标约定全 source 一致：X = 宽，Y = 深（前 = +Y），Z = up；接地 z = 0。Helpers `_build_cabinet` / `_build_door` / `_populate_rack`（+ `_linspace`）在所有 door-based source 中复现；drawer 候选把同样部件重构成一个移动体。
>
> **同步状态**：本 spec 引用的 7 个 5 星样本（1 parent + 6 fork 单轴 / N 轴变体）已同步进本仓库 `articraft_data/data/records/`，rating=5（按上游 curation；本地同步副本 record.json 的 rating 字段为 null，不影响采纳）。行号按各样本 `revisions/rev_000001/model.py` 实际行号计（逐一全文读完）。引用以 part / joint / helper **名字**为准（`cabinet`/`kick_plinth`/`side_wall_{i}`/`back_wall`/`cabinet_floor`/`cabinet_ceiling`/`tub_wall_{i}`/`tub_back_panel`/`tub_floor`/`rack_rail_{i}`/`top_slab`、`front_door`/`door_panel`/`door_hinge`、`drawer`/`drawer_panel`/`drawer_slide`/`drawer_runner_{i}`/`cabinet_rail_{i}`/`lower_front_panel`、`rack_{i}`/`rack_slide_{i}`/`wheel_{idx}`/`side_runner_{k}`/`basket_body`、`control_strip`/`pocket_handle`/`display_lcd`/`button_{i}`/`control_panel`/`bar_handle`/`handle_standoff_{i}`），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `dish_washer` |
| template path | `agent/templates/Kitchen_Dish_washer.py` |
| test path (optional) | `tests/agent/test_dish_washer_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（defining motion = 开门机构 slot A：drop_down_door REVOLUTE / dish_drawer PRISMATIC；外加碗篮几何 slot B + 控制 / 把手 slot C 是固定 named slot；**唯一可变 count 轴 = rack_count 滑篮栈**，只在 drop_down_door 分支展开 → mixed）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7（1 parent + 6 fork 变体：1 dish_drawer 开门机构 + 1 fused_basket 碗篮几何 + 2 控制 / 把手槽（top_control / fascia_handle）+ 2 rack_count N 样本（racks_3_cutlery / handle_recessed_tall）；均 converged、compile success、含 REVOLUTE + PRISMATIC 非 fixed joint、workbench-only）|
| read_count | 7（**全部读完整 `model.py`**，不抽样；含每个样本 build helpers、part 树、articulation、run_tests 的 check / expect_contact / allow_overlap 段）|
| read_scope | all 5-star samples in this category（parent 母资产 001.png 覆盖 drop_down_door × wire_grid × front_fascia × rack_count=2 基线；6 变体为单轴 / N 轴 fork 子）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 7/7 全部被采纳，无未采用样本（下游 unverified 模板 `agent/templates/dishwasher_with_dropdown_door_and_sliding_racks.py` 与本 spec 无关，仅参考过其槽位思路，**不依赖**）|

阅读要点（用于槽位分解，**关键拓扑发现**）：
- **共享拓扑骨架**：root `cabinet`（拉丝外壳 + 抛光 tub liner + 侧滑轨 + 悬挑 top_slab，整体 ~0.60 W × 0.62 D × 0.85 H 接地 z=0）。door 家族（6/7）= `cabinet`(root) + `front_door`(REVOLUTE 底铰) + N 个独立 `rack_{i}`(PRISMATIC +Y)；drawer 家族（1/7）= `cabinet`(root) + 一个 `drawer`(PRISMATIC +Y) 整体拉出体（内含 tub liner + 单固定 rack + runners）。非 fixed joint 计数随机构变化：drop_down_door = 1 门铰 + rack_count 滑篮；dish_drawer = 1 抽屉滑（rack 固定在抽屉内，无独立 joint）。
- **rack_count 拷贝逻辑（multiplicity 主轴，2 个 N 样本逐一核对，这是 §8 copy-logic 源）**：
  - **N=2 loop 形式**（handle_recessed_tall）：`RACK_SPECS` = 2 个 dict 列表（L65-L84），`for i, spec in enumerate(RACK_SPECS)`（L375）emit `rack_0`（tall deep lower，wheels，z_origin=TUB_FLOOR_TOP+0.010）+ `rack_1`（removable upper half-rack，runners，z_origin=0.50），每个 `model.part(spec["name"])` + `_populate_rack(...)` + 一个 `{spec['name']}_slide` PRISMATIC（L385-L395）。**这是 N=2 的 loop-emit 参考。**
  - **N=3 loop 形式**（racks_3_cutlery）：`RACK_CONFIGS` = 3 个 dict + `NUM_RACKS=len(...)`（L68-L88），`for i in range(NUM_RACKS)`（L378）emit `rack_{i}`（rack_0 lower/wheels、rack_1 upper/runners、rack_2 shallow cutlery tray/runners）+ `rack_slide_{i}` PRISMATIC（L382-L392）；runner 滑轨也 loop-emit 成 `rack_rail_{rail_idx}`（L186-L198）。**这是 N=3 的 loop-emit 参考。**
  - **PARENT 本身 N=2 但是 HAND-WRITTEN**（两次 `model.part("upper_rack")` / `model.part("lower_rack")` + 两次 `_populate_rack` 调用，joint `upper_rack_slide` / `lower_rack_slide`，L329-L365）—— **NOT a loop**。**模板必须用 loop 形式**（racks_3_cutlery / handle_recessed_tall），不复制 parent 的两个手写命名 rack。fused_basket / top_control / fascia_handle 也都用 parent 的手写 N=2 形式（它们是单轴变体，不示范 loop）。
- **Slot A 开门机构（defining motion）**：
  - **drop_down_door**（parent + 4 个变体基线）：`front_door` part（`door_panel`）；`door_hinge` REVOLUTE parent=`cabinet` 底前缘 origin=(0, BODY_FRONT_Y, PLINTH_H) axis=(-1,0,0) lower=0 upper=π/2（L336-L344）；门下翻平放，tub 固定，碗篮在各自 PRISMATIC 上独立滑出（multiplicity 轴所在）。
  - **dish_drawer**（dishdrawer 变体）：`drawer` part（`drawer_panel` + `tub_wall_{i}` + `tub_floor` + `drawer_runner_{i}` + 单固定 rack wires）作为 ONE body 拉出；`drawer_slide` PRISMATIC parent=`cabinet` origin=(0, BODY_FRONT_Y, DRAWER_BOTTOM_Z=0.40) axis=(0,1,0) lower=0 upper=DRAWER_TRAVEL=0.42（L364-L374）；cabinet 加 `lower_front_panel`（L202-L209）+ `cabinet_rail_{i}` 通道（L224-L232）；runner-in-rail 望远镜 `allow_overlap`（L479-L489）。**无 REVOLUTE、无独立滑篮（rack 固定在 drawer 体内）→ rack_count 在 dish_drawer 上是 trivial 端点 N=1。**
- **Slot B 碗篮几何**：
  - **wire_grid**（parent + 5 个变体基线）：`_populate_rack(...)` 内 `floor_rod_y_{i}` / `floor_rod_x_{i}` / `top_rail_xy_{i}` / `top_rail_side_{i}` / `side_wire_{k}_{j}` / `face_wire_{k}_{j}`，全 Box 细杆（parent L231-L320）；支撑臂 = `wheel_{idx}`×4（lower，rolls on tub_floor）或 `side_runner_{k}`×2（upper，glide on rack_rail）。每根 wire 落在另一根 wire 上（无悬空）。
  - **fused_basket**（fused_basket 变体）：`_build_basket_mesh(w,d,h)` → 单个 CadQuery solid（tray floor + 4 周壁 + `rarray` 圆柱 tine 网格）经 `mesh_from_cadquery` 成 `basket_body` 单 visual（L230-L340）；同 `wheel_{idx}` / `side_runner_{k}` 支撑。**molded 塑料碗篮单 fused mesh + 整合 tine prongs，替代 wire 格栅（primitive 升级，import cadquery）。**
- **Slot C 控制 + 把手**（门 / 前面板上沿条）：
  - **front_fascia**（parent + 基线）：`control_strip`（前凸条）+ 凹陷 `pocket_handle` + `display_lcd` + `button_{i}`（loop），全在门前面（parent L190-L227）；关门时控制可见、凹槽把手。
  - **top_hidden**（top_control 变体）：`control_panel` 凹进门 TOP 边（z≈DOOR_H face，L204-L209）+ `pocket_handle` + `display_lcd` + `button_{i}` 在 top face（L213-L238）；tests assert 关门时控制在 slab 下隐藏（L501-L506），开门时旋出前向（L567-L572）。
  - **proud_bar_handle**（fascia_handle 变体）：保留 `control_strip` + `display_lcd` + `button_{i}`；把 pocket 凹槽换成全宽 `bar_handle` Cylinder（bar_len=0.50 > 0.40 m span）立在两个 `handle_standoff_{i}` 支架上（standoff_depth=0.032 > 0.02 m standoff，L201-L228）；凸管把手 grab-bar 外观 + 支架。
- **palette**：全样本同色族材质（`BRUSHED_STEEL`(0.72,0.73,0.75) 外壳 / `STEEL_TOP`(0.66,0.67,0.69) 顶板 / `POLISHED_TUB`(0.82,0.83,0.85) tub / `PLINTH_GRAY`(0.28,0.29,0.30) plinth / `STRIP_GRAY`(0.20,0.21,0.23) 控制条 / `HANDLE_DARK`(0.10,0.10,0.11) 把手 / `LCD_BLUE`(0.25,0.50,0.92) / `BUTTON_GRAY`(0.55,0.56,0.58) / `CHROME_WIRE`(0.85,0.86,0.88) 碗篮；fused_basket 加 `BASKET_COATED`(0.78,0.78,0.76)）。→ 5 套 colorway（见 §7 palette_style：stainless / white / black 系）。

## 核心身份

一台**独立式洗碗机（freestanding dishwasher）**：一个中空拉丝钢柜 `cabinet`（root，凹陷 `kick_plinth` + 拉丝外壳 + 抛光 tub liner + 悬挑 `top_slab`，~0.60 W × 0.62 D × 0.85 H 接地 z=0）。前面是开门机构（Slot A）：**默认是一扇底铰放下式门 `front_door`**（`door_hinge` REVOLUTE 底前缘 axis=-X，0→π/2 前翻平放），可替换为整体拉出的**抽屉式 `drawer`**（`drawer_slide` PRISMATIC +Y）。tub 内是滑出式碗篮（Slot B）：**默认是 N 个 chrome wire-grid 碗篮**（每个 `rack_{i}` 沿 +Y PRISMATIC 拉出，行程 ~0.45 m），可替换为 molded fused-basket（CadQuery 单 mesh + tine 网格）。门 / 前面板上沿是控制 + 把手（Slot C）：默认 `front_fascia`（前凸控制条 + 凹陷 pocket handle + LCD + buttons），可替换为 `top_hidden`（控制凹进门顶边，关门时藏在 slab 下、开门时旋出）或 `proud_bar_handle`（凸管 grab-bar + 支架）。活动语义恒为：**drop_down_door 门绕底前缘 -X REVOLUTE 下翻** + **每个碗篮沿 +Y PRISMATIC 拉出**（rack_count 多重性主轴）；或 **dish_drawer 整体绕 +Y PRISMATIC 拉出**（内含单固定 rack）。默认成熟域：opening_mechanism × rack_geometry × control_handle × rack_count N∈[2,3]（仅 drop_down_door 分支）笛卡尔积的单台独立式洗碗机。

不该混入：
- **冰箱 / 冷柜（refrigerator / freezer）**——侧铰立式门（非底铰下翻）、内部是层架 / 抽屉储物（非洗涤 tub liner + 滑出碗篮 + 控制面板），无放下式门 + chrome 碗篮 + 底前缘门铰身份；本类核心是洗涤 tub + 滑出碗篮 + 前 / 顶控制条。
- **烤箱 / 微波炉（oven / microwave）**——同样底铰下翻门外观相似，但内部是空腔 + 烤架（无 chrome wire 碗篮 / 无侧滑轨 / 无 tub liner），且通常台面嵌入式 / 带玻璃门窗；本类必须有抛光 tub liner + 滑出式碗篮（wire_grid / fused_basket）。
- **普通橱柜 / 抽屉柜（cabinet / chest of drawers）**——纯储物，无洗涤 tub liner、无 chrome 碗篮、无控制面板 / LCD / buttons；本类是带洗涤腔 + 控制面板的电器，不是家具柜。（注意：dish_drawer 候选虽是抽屉形态，但抽屉体内含 tub liner + chrome rack + 控制面板 → 仍是洗碗机身份。）
- **洗衣机 / 烘干机（washing machine / dryer）**——前置圆形舱门 + 滚筒（非平面碗篮 + 矩形门），无 chrome wire 碗篮栈；本类是矩形碗篮 + 矩形门 / 抽屉。

## 槽位 + 候选模块表

> **建模注记**：dish_washer 是 **root `cabinet`（外壳 + tub liner + 侧滑轨 + top_slab）+ opening_mechanism(Slot A，门 REVOLUTE / 抽屉 PRISMATIC) + rack_geometry(Slot B，碗篮 visual 词汇) + control_handle(Slot C，门 / 面板上沿条) + N 个滑篮（PRISMATIC，rack_count multiplicity 主轴，仅 drop_down_door 分支）**。
> - **Slot A opening_mechanism**：drop_down_door（`front_door` REVOLUTE 底前缘 + N 个独立滑篮，**multiplicity 载体**）/ dish_drawer（整体 `drawer` PRISMATIC 拉出，内含单固定 rack，rack_count = trivial N=1）。
> - **Slot B rack_geometry**：wire_grid（Box 细杆 wire 格栅）/ fused_basket（CadQuery 单 mesh + tine）。drop_down_door 分支：决定每个 `rack_{i}` 的碗篮 visual；dish_drawer 分支：决定抽屉内单 rack 的碗篮 visual。
> - **Slot C control_handle**：front_fascia（前凸控制条 + 凹槽 pocket handle）/ top_hidden（控制凹进门顶边，关门藏 slab 下）/ proud_bar_handle（凸管 grab-bar + 支架）。
> - **rack_count（N）是 multiplicity 主轴**：仅 drop_down_door 分支展开 N∈[2,3]（每篮独立 PRISMATIC）；dish_drawer 分支 rack_count 解析为 trivial N=1（单 rack 固定在抽屉体内，无独立 joint），不随采样 N 展开（见 §8 / §9 兼容矩阵）。

### Slot A：opening_mechanism（defining motion —— 前开门 / 抽屉机构）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| drop_down_door（基线 + multiplicity 载体） | parent rec_model-a-freestanding-stainless-steel-dishwasher-_…_c2d628fd | `_build_door` L178-228 / `door_hinge` REVOLUTE L336-344 / `_build_cabinet` L83-175（含 `rack_rail_{i}` L160-166）/ rack PRISMATIC 见 Slot rack_count | eligible if compatible | `front_door` part（`door_panel` 立板 + Slot C 控制条），`door_hinge` REVOLUTE parent=`cabinet` 底前缘 origin=(0, BODY_FRONT_Y=0.27, PLINTH_H=0.07) axis=(-1,0,0) lower=0 upper=π/2；门下翻平放（open pose 水平、低、不入地）；tub 固定，**N 个独立 `rack_{i}` PRISMATIC 滑篮（rack_count multiplicity 轴本体）** |
| dish_drawer | rec_dish_washer_var_door_drawer_dishdrawer | `_build_drawer` L238-352 / `drawer_slide` PRISMATIC L364-374 / cabinet `lower_front_panel` L202-209 + `cabinet_rail_{i}` L224-232 / runner-in-rail allow_overlap L479-489 | eligible if compatible | `drawer` part 作为 ONE body（`drawer_panel` 前面板 + Slot C 控制 + `tub_wall_{i}` + `tub_back_panel` + `tub_floor` + `drawer_runner_{i}` + 单固定 rack wires），`drawer_slide` PRISMATIC parent=`cabinet` origin=(0, BODY_FRONT_Y, DRAWER_BOTTOM_Z=0.40) axis=(0,1,0) lower=0 upper=DRAWER_TRAVEL=0.42；整 tub 总成整体拉出；**无 REVOLUTE、无独立滑篮（rack 固定在抽屉内 → rack_count = trivial N=1）**；`cabinet_rail_{i}` ↔ `drawer_runner_{i}` 望远镜 allow_overlap |

### Slot B：rack_geometry（碗篮 visual 词汇 —— 装进 `rack_{i}`（door）或 drawer 内单 rack）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| wire_grid（基线） | parent rec_model-a-freestanding-…_c2d628fd | `_populate_rack` L231-320（`floor_rod_y_{i}` L269-275 / `floor_rod_x_{i}` L276-283 / `top_rail_xy_{i}` L287-293 / `top_rail_side_{i}` L294-300 / `side_wire_{k}_{j}` L304-311 / `face_wire_{k}_{j}` L313-320）+ `wheel_{idx}`×4 L246-256（lower）/ `side_runner_{k}`×2 L260-266（upper）| eligible if compatible | 开放 chrome wire-frame 碗篮，多根 Box 细杆（WIRE=0.006）构成：纵 / 横地杆 + 顶周边 rail + 竖 wire（每根落在另一根上，无悬空）；支撑 = `wheel_{idx}`(lower，rolls on `tub_floor`) 或 `side_runner_{k}`(upper，glide on `rack_rail`)。drawer 候选用 `_add_rack_wires`（前缀化，L89-150）同款 wire 几何 |
| fused_basket | rec_dish_washer_var_rack_geom_fused_basket | `_build_basket_mesh(w,d,h)` L230-297（floor plate + 4 周壁 union + `rarray` tine 网格 extrude）/ `mesh_from_cadquery(...,"basket_body")` `_populate_rack` L334-340 / `import cadquery as cq` L25 / `BASKET_COATED` L78 | eligible if compatible | molded 塑料碗篮单个 CadQuery solid（tray floor + 4 perimeter walls + 圆柱 tine prong 网格）经 `mesh_from_cadquery` 成单 `basket_body` visual，替代 wire 格栅（**primitive 升级：真实 CadQuery 几何**）；同 `wheel_{idx}` / `side_runner_{k}` 支撑；`BASKET_COATED` 材质 |

### Slot C：control_handle（控制 + 把手 —— 门 / 前面板上沿条）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| front_fascia（基线） | parent rec_model-a-freestanding-…_c2d628fd | `control_strip` L193-198 / `pocket_handle` L202-207 / `display_lcd` L210-215 / `button_{i}` loop L218-227（`for i, bx in enumerate(...)`）| eligible if compatible | 门顶沿前凸 `control_strip`（STRIP_GRAY，proud of panel）+ 凹陷 `pocket_handle`（HANDLE_DARK inset bar）+ `display_lcd`（蓝）+ 4 个 `button_{i}`（off-axis 左侧，Cylinder along +Y）；关门时控制 head-on 可见，proud of panel front face |
| top_hidden | rec_dish_washer_var_door_top_control | `control_panel` 凹进门顶边 L204-209（z≈DOOR_H face）/ `pocket_handle` L215-220 / `display_lcd` L223-228 / `button_{i}` loop L232-238（沿 local Z，top face）/ tests: 关门藏 slab 下 L501-506、开门旋出 L567-572 | eligible if compatible | 隐藏式顶沿控制：`control_panel`(STRIP_GRAY) 凹进门 TOP 面（ctrl_zc=DOOR_H−ctrl_thick/2，front face 保持干净拉丝），`pocket_handle` / `display_lcd` / `button_{i}` 在 top face；关门时控制在 top_slab 下隐藏 / NOT proud of front，开门旋转到前向暴露 |
| proud_bar_handle | rec_dish_washer_var_control_body_fascia_handle | `control_strip` L193-198 / `handle_standoff_{i}` loop L211-219（两支架）/ `bar_handle` Cylinder L220-228（bar_len=0.50 span，standoff_depth=0.032）/ `display_lcd` L230-236 / `button_{i}` loop L238-248 | eligible if compatible | 保留 `control_strip` + `display_lcd` + `button_{i}`；把 pocket 凹槽换成全宽 `bar_handle` Cylinder（>0.40 m span，bar_y_center=DOOR_T+standoff_depth）立在两个 `handle_standoff_{i}` Box 支架上（>0.02 m standoff，sx=±0.20）；凸管 grab-bar 外观 + 支架 |

## 槽位图（slot graph）

pattern: mixed（root `cabinet` 持有 opening_mechanism(Slot A 门 / 抽屉) + control_handle(Slot C 在门 / 前面板上沿) + N 个滑篮(rack_count multiplicity 主轴，仅 drop_down_door 分支) parallel children；rack_geometry(Slot B) 是碗篮 visual 词汇 by-value 注入各 rack；defining motion = Slot A 的 REVOLUTE 门 或 PRISMATIC 抽屉）

```
cabinet  (root；接地 z=0。拉丝外壳 side_wall_{0,1}/back_wall/cabinet_floor/cabinet_ceiling +
          凹 kick_plinth + 抛光 tub liner tub_wall_{0,1}/tub_back_panel/tub_floor +
          侧 rack_rail_{i} 滑轨 + 悬挑 top_slab。~0.60 W × 0.62 D × 0.85 H)
  │
  ├── [opening_mechanism slot]  (互斥二选一；defining motion)
  │     ├─ drop_down_door : front_door(door_panel + Slot C 控制条)
  │     │      ──[door_hinge: REVOLUTE 底前缘 origin=(0, BODY_FRONT_Y=0.27, PLINTH_H=0.07), axis=(-1,0,0), lower=0 upper=π/2]
  │     │      + tub 固定 + N 个独立滑篮（rack_count 轴本体，见下）
  │     └─ dish_drawer    : drawer(drawer_panel + Slot C 控制 + tub liner + 单固定 rack + drawer_runner_{i})
  │            ──[drawer_slide: PRISMATIC origin=(0, BODY_FRONT_Y, DRAWER_BOTTOM_Z=0.40), axis=(0,1,0), lower=0 upper=DRAWER_TRAVEL=0.42]
  │            + cabinet 加 lower_front_panel + cabinet_rail_{i}（runner-in-rail 望远镜 allow_overlap）
  │            + rack_count = trivial N=1（单 rack 固定在 drawer 体内，无独立 joint）
  │
  ├── [rack_count multiplicity 轴]  (仅 drop_down_door 分支)  rack_{i} / wheel_{idx} or side_runner_{k}  i∈range(N)
  │     ──[rack_slide_{i}: PRISMATIC axis=(0,1,0)(+Y 拉出), origin=(0, rack_yc≈-0.01, z_i), lower=0 upper=RACK_TRAVEL≈0.45]
  │       z_i = 各 rack 静止高度（rack_0 lower 坐 tub_floor 上 wheels；上层 rack 在各自 rack_rail 上 runners，z 递增）
  │       N 范围 [2,3]；rack_0=lower(wheels)、rack_1=upper(runners)、rack_2=shallow cutlery tray(runners)
  │       碗篮 visual 由 rack_geometry(Slot B) 决定（wire_grid 细杆 / fused_basket CadQuery mesh）
  │
  └── [control_handle slot]  (互斥三选一；在 front_door / drawer 上沿)
        ├─ front_fascia     : control_strip(前凸) + pocket_handle(凹槽) + display_lcd + button_{i}（门前面，关门可见）
        ├─ top_hidden       : control_panel(凹进门顶边 z≈DOOR_H) + pocket_handle + display_lcd + button_{i}（top face，关门藏 slab 下、开门旋出）
        └─ proud_bar_handle : control_strip + bar_handle(Cylinder >0.40 span) on handle_standoff_{i}(>0.02 standoff) + display_lcd + button_{i}
```

接口点位与 joint 语义：
- **opening_mechanism 接口（互斥二选一，defining motion）**：drop_down_door = `front_door` 是 `cabinet` 的 REVOLUTE child，`door_hinge` origin 落在 cabinet 底前缘 (0, BODY_FRONT_Y, PLINTH_H)，axis=(-1,0,0)，rest q=0 立板 flush against cabinet front（`expect_contact` door_panel↔side_wall_0），open q=π/2 水平前翻（oz1<0.12、oy1>0.95、oz0>0 不入地）。dish_drawer = `drawer` 是 `cabinet` 的 PRISMATIC child，`drawer_slide` origin=(0, BODY_FRONT_Y, DRAWER_BOTTOM_Z)，axis=(0,1,0)，rest q=0 前面板 flush at opening，open q=DRAWER_TRAVEL 整体前拉（仍部分 retained，`expect_overlap` axis=y ≥0.02）；drawer 体内 tub liner + 单 rack 跟随拉出。
- **rack_count 接口（multiplicity 主轴，仅 drop_down_door 分支）**：每个 `rack_{i}` 是 `cabinet` 的 PRISMATIC child，axis=(0,1,0)（+Y 拉出），origin=(0, rack_yc≈-0.01, z_i)；z_i 由各 rack 静止高度解析（rack_0 lower 在 tub_floor 上方、上层 rack 在递增 z 的 rack_rail 上）。rest pose q=0（闭合，碗篮 nest 在 tub 内，`expect_within` axes=xy + `expect_gap` door↔rack axis=y ≥0.005）；open q=RACK_TRAVEL 滑出柜前（`expect_overlap` axis=y ≥0.02 部分 retained + r_aabb[1][1] > BODY_FRONT_Y+0.30 凸出 + `expect_gap` rack↔door axis=z ≥0 越过翻平的门）。rack_0 wheels `expect_contact` wheel_0↔tub_floor；上层 rack runners `expect_contact` side_runner_0↔rack_rail_0。
- **rack_geometry 接口（碗篮 visual 词汇，by-value 注入）**：wire_grid = `_populate_rack` 内多 Box 细杆（每根落在另一根上）；fused_basket = `_build_basket_mesh` 单 CadQuery solid → `basket_body` 单 visual。两者共用同款 `wheel_{idx}`(lower) / `side_runner_{k}`(upper) 支撑与同款 PRISMATIC 滑动接口；fused_basket 不改 joint 拓扑，只换碗篮主体 primitive（import cadquery）。
- **control_handle 接口（门 / 前面板上沿，互斥三选一）**：所有 control_handle visual 挂在 Slot A 的活动件（`front_door` 或 `drawer`）上沿（随门 / 抽屉一起动），不是独立 part。front_fascia = `control_strip` + `pocket_handle` + LCD + buttons 在门前面（proud of panel front, y > BODY_FRONT_Y+DOOR_T）；top_hidden = `control_panel` + handle + LCD + buttons 在门 TOP 面（z≈DOOR_H，关门时藏 top_slab 下、NOT proud of front，开门旋出前向）；proud_bar_handle = `control_strip` + `bar_handle` Cylinder on `handle_standoff_{i}` 支架（凸出 door front）+ LCD + buttons。
- **mating policy**：门是 panel-on-bottom-front-hinge（REVOLUTE）、抽屉 / 碗篮是 box-in-cavity captured-slide（PRISMATIC）、控制条是 strip-on-moving-panel（visual on Slot A part）。drawer 的 runner-in-rail 是望远镜 captured-slide（`allow_overlap` cabinet_rail_{i}↔drawer_runner_{i}）。几何均非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap + `expect_contact`/`expect_gap`/`expect_within`/`expect_overlap` 守静止 / 行程姿态（照搬各样本 run_tests 段）。
- **rest pose**：门 q=0 立板关闭 flush；抽屉 q=0 闭合 flush；所有碗篮 q=0 nest 在 tub 内闭合。
- **互斥 / 可选 / 派生**：opening_mechanism 二选一互斥（drop_down_door 带 rack_count 全 N / dish_drawer 派生 rack_count 为 trivial N=1）；rack_geometry 二选一互斥（决定碗篮 visual）；control_handle 三选一互斥（top_hidden 在 drop_down_door 上语义最完整：依赖门旋转暴露控制，dish_drawer 上 top_hidden 需重锚到前面板 → 见 §9 兼容矩阵）；rack_count N 是 multiplicity 主轴，仅 drop_down_door 展开。

## 每槽位 Module Emits / Interfaces

### Slot A / opening_mechanism — drop_down_door（基线 + multiplicity 载体）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cabinet`（root，visual：`kick_plinth` + `side_wall_{0,1}`/`back_wall`/`cabinet_floor`/`cabinet_ceiling` 拉丝壳 + `tub_wall_{0,1}`/`tub_back_panel`/`tub_floor` 抛光 liner + `rack_rail_{i}` 滑轨 + `top_slab`）；`front_door`(visual `door_panel` + Slot C 控制条) | parent `_build_cabinet` L83-175 / `_build_door` L178-228 |
| internal joints | `door_hinge` REVOLUTE parent=`cabinet` child=`front_door` origin=(0, BODY_FRONT_Y=0.27, PLINTH_H=0.07) axis=(-1,0,0) lower=0 upper=π/2；+ N 个 `rack_slide_{i}` PRISMATIC（见 rack_count） | parent L336-344 |
| upstream interface | root（接地 z=0，~0.60×0.62×0.85 envelope）| parent L382-396 |
| downstream interface | 前开口（门铰 + 碗篮滑入）+ tub liner（碗篮 nest）+ 侧 rack_rail（runner 篮支撑）+ 顶 top_slab（top_hidden 控制藏其下）| parent L83-175 |

### Slot A / opening_mechanism — dish_drawer
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cabinet`（root，同基线 + `lower_front_panel` + `cabinet_rail_{i}` 通道，无门铰）；`drawer` part（visual `drawer_panel` + Slot C 控制 + `tub_wall_{i}`/`tub_back_panel`/`tub_floor` liner + `drawer_runner_{i}` + 单固定 rack wires，整体一个移动体）| `_build_cabinet` L154-234 / `_build_drawer` L238-352 |
| internal joints | `drawer_slide` PRISMATIC parent=`cabinet` child=`drawer` origin=(0, BODY_FRONT_Y, DRAWER_BOTTOM_Z=0.40) axis=(0,1,0) lower=0 upper=DRAWER_TRAVEL=0.42；**无独立滑篮 joint**（rack 固定在 drawer 体内）| L364-374 |
| upstream interface | root（同基线 envelope）；drawer 前面板 flush at opening | L387-402 |
| downstream interface | 整 tub 总成拉出（前面板 + liner + 单 rack + runners 跟随）；`cabinet_rail_{i}` ↔ `drawer_runner_{i}` 望远镜 allow_overlap | L479-499 |

### Slot rack_count — 滑篮（multiplicity 主轴，仅 drop_down_door 分支）
| emits | 描述 | 来源 |
|---|---|---|
| parts | N 个 `rack_{i}`（碗篮 visual 由 Slot B 决定 + 支撑 `wheel_{idx}`×4(rack_0 lower) / `side_runner_{k}`×2(上层 runners)）；runner 滑轨 loop-emit `rack_rail_{rail_idx}` | racks_3 `for i in range(NUM_RACKS)` L378-392 / handle_recessed_tall `for i, spec in enumerate(RACK_SPECS)` L375-395 |
| internal joints | N 个 `rack_slide_{i}` PRISMATIC parent=`cabinet` axis=(0,1,0) origin=(0, rack_yc≈-0.01, z_i) lower=0 upper=RACK_TRAVEL=0.45 | racks_3 L382-392 / handle_recessed_tall L385-395 |
| upstream interface | 挂 `cabinet`（tub 内）；rack_0 wheels 坐 tub_floor、上层 rack runners 坐 rack_rail（z 递增）| racks_3 L186-198, L549-575 |
| downstream interface | 碗篮 nest 闭合（q=0）/ 滑出柜前（q=RACK_TRAVEL，越过翻平门）| racks_3 L530-652 |

### Slot B / rack_geometry — wire_grid（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts（visual 注入各 rack）| 多 Box 细杆 wire 格栅：`floor_rod_y_{i}` / `floor_rod_x_{i}` / `top_rail_xy_{i}` / `top_rail_side_{i}` / `side_wire_{k}_{j}` / `face_wire_{k}_{j}`（每根落在另一根上）；支撑 `wheel_{idx}`×4 或 `side_runner_{k}`×2 | parent `_populate_rack` L231-320 |
| internal joints | 无（碗篮 visual 词汇，滑动 joint 属 rack_count）| — |
| downstream interface | nest 在 tub 内 / 滑出；wheels↔tub_floor 或 runners↔rack_rail 接触 | parent L246-266 |

### Slot B / rack_geometry — fused_basket
| emits | 描述 | 来源 |
|---|---|---|
| parts（visual 注入各 rack）| 单 `basket_body`（CadQuery solid：tray floor + 4 周壁 + `rarray` 圆柱 tine 网格，`mesh_from_cadquery`）；支撑 `wheel_{idx}`×4 或 `side_runner_{k}`×2；`import cadquery as cq` + `BASKET_COATED` | `_build_basket_mesh` L230-297 / `_populate_rack` L334-340 |
| internal joints | 无（碗篮 visual 词汇）| — |
| downstream interface | 同 wire_grid 滑动 / 接触接口（只换碗篮主体 primitive，不改 joint 拓扑）| L309-340 |

### Slot C / control_handle — front_fascia（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts（visual on Slot A part）| `control_strip`(前凸条) + `pocket_handle`(凹槽 inset bar) + `display_lcd`(蓝) + 4 个 `button_{i}`(off-axis 左) | parent L193-227 |
| internal joints | 无（visual on 门 / 抽屉前面，随之动）| — |
| downstream interface | 关门时控制 head-on 可见，proud of panel front（y > BODY_FRONT_Y+DOOR_T）| parent L460-481 |

### Slot C / control_handle — top_hidden
| emits | 描述 | 来源 |
|---|---|---|
| parts（visual on `front_door` top edge）| `control_panel`(凹进门顶边 z≈DOOR_H) + `pocket_handle` + `display_lcd` + `button_{i}`(top face) | top_control L204-238 |
| internal joints | 无（visual on 门顶，随门旋转）| — |
| downstream interface | 关门时控制藏 top_slab 下 / NOT proud of front；开门旋出前向暴露 | top_control L501-506, L567-572 |

### Slot C / control_handle — proud_bar_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts（visual on Slot A part）| `control_strip` + 2 个 `handle_standoff_{i}`(支架) + `bar_handle`(Cylinder >0.40 span) + `display_lcd` + `button_{i}` | fascia_handle L193-248 |
| internal joints | 无（visual on 门 / 抽屉前面）| — |
| downstream interface | 凸管 grab-bar 凸出 door front（bar_y_center=DOOR_T+standoff_depth，>0.02 m standoff）| fascia_handle L211-228 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| opening_mechanism | enum | drop_down_door / dish_drawer | drop_down_door | choice | deterministic procedural sampler 选；决定 defining motion（REVOLUTE 门 / PRISMATIC 抽屉）+ 是否展开 rack_count（互斥）| Slot A 表 |
| rack_geometry | enum | wire_grid / fused_basket | wire_grid | choice | sampler 选；决定碗篮 visual 词汇（细杆 / CadQuery mesh，互斥）| Slot B 表 |
| control_handle | enum | front_fascia / top_hidden / proud_bar_handle | front_fascia | choice | sampler 选；决定门 / 面板上沿控制 + 把手形态（互斥）；top_hidden conditional@drop_down_door（见下）| Slot C 表 |
| rack_count (N) | int | 声明产品域 **[2,3]**；sweep 采样域 [2,3]（N=2 高频基线、N=3 含 cutlery tray 常见）| 2 | conditional→slot_choice | **multiplicity 主轴**，编入 slot_choice 为 `("rack_count", f"n{N}")`（拓扑维度）；**仅 drop_down_door 展开 [2,3]**；dish_drawer 解析为 trivial N=1（单固定 rack，见 §8/§9）| parent(N=2 hand-written) / handle_recessed_tall(N=2 loop) / racks_3_cutlery(N=3 loop) |
| palette_style | enum | stainless_brushed / glossy_white / matte_black / steel_blue / graphite_chrome | stainless_brushed | palette | palette only，**不计入 slot_choice**；见下方 colorway 说明 | 各样本材质 |
| cabinet_width_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 BODY_W / TOP_W（柜宽 X），clamp；连带门宽 / 抽屉面宽 / 碗篮宽 / tub liner 宽派生 | resolve clamp |
| cabinet_depth_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 BODY 深（Y），clamp；连带碗篮深 / 抽屉 tub 深 / rack_travel 上限派生 | resolve clamp |
| cabinet_height_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 TOTAL_H / BODY_TOP_Z（高 Z），clamp；连带门高 DOOR_H / 碗篮 z 间距 / tub liner 高派生 | resolve clamp |
| rack_travel_scale | float | [0.85, 1.05] | 1.0 | independent | 缩放碗篮 PRISMATIC upper（基 RACK_TRAVEL=0.45）；clamp ≤ 0.95·(tub 深) 使碗篮滑出仍部分 retained（不脱轨）| parent L355 |
| drawer_travel_scale | float | [0.85, 1.05] | 1.0 | conditional | 仅 dish_drawer 有效；缩放 `drawer_slide` upper（基 DRAWER_TRAVEL=0.42）；clamp ≤ 0.95·tub 深（抽屉仍部分 retained）| dishdrawer L372 |
| door_open_angle | float | 固定 π/2（不缩放）| π/2 | conditional | 仅 drop_down_door；门 REVOLUTE upper 恒 π/2（水平翻平，所有样本固定值，不暴露为 scale）| parent L343 |
| rack_height_scale | float | [0.85, 1.15] | 1.0 | conditional | 缩放各碗篮 basket height（lower 深 / upper 浅 / cutlery 更浅）；clamp 使 Σ(碗篮高+gap) ≤ tub 可用高，碗篮不互撞 / 不顶 tub 顶 | handle_recessed_tall L65-84 / racks_3 L68-87 |
| (—) | constraint | — | — | inequality | 碗篮栈占高：`Σ(rack_height[i]·rack_height_scale) + (N−1)·rack_gap ≤ tub 可用高 = liner_h − margin`；违反则回缩 rack_height_scale 或 N（仅 drop_down_door；N≤3 时样本基线已满足，cabinet_height_scale 放大时进一步保险）| racks_3 z 布局 L70-86 |
| (—) | constraint | — | — | inequality | 碗篮 / 抽屉拉出不脱轨：`travel·travel_scale ≤ 0.95·tub_depth`（碗篮 RACK_TRAVEL / 抽屉 DRAWER_TRAVEL 各自）；违反回缩 travel（保证 `expect_overlap` axis=y ≥0.02 部分 retained）| parent L355 / dishdrawer L372 |
| (—) | constraint | — | — | inequality | 门翻平不入地：drop_down_door open pose（q=π/2）门 oz0 > 0（hinge 在 PLINTH_H 高、门高 DOOR_H < hinge_z + 前伸不触地）；由 hinge origin=(0,BODY_FRONT_Y,PLINTH_H) + DOOR_H 几何保证；cabinet_height_scale 放大门高时校验 oz0>0 | parent L524-538 |
| (—) | constraint | — | — | conditional | rack_count 上限随 opening_mechanism：drop_down_door → N∈[2,3] 全展开（每篮独立 PRISMATIC）；dish_drawer → 解析为 trivial N=1（单 rack 固定在抽屉体内，无独立 joint），rack_count slot_choice 记为 `n1`（见 §8/§9）| dishdrawer / racks_3 |
| (—) | constraint | — | — | conditional | control_handle × opening_mechanism：top_hidden 依赖门旋转暴露控制（tests assert 关门藏 slab 下 / 开门旋出）→ 在 drop_down_door 上语义完整；dish_drawer 上 top_hidden 需把控制重锚到前面板（不依赖旋转）→ 首版 gate（dish_drawer 仅 front_fascia / proud_bar_handle，见 §9）| top_control L501-572 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程，**绝不改变 opening_mechanism / rack_geometry / control_handle / rack_count 的拓扑**。

**palette_style colorway（5 套，来自 7 个 5★ 源材质 + 真实洗碗机外观族）**：
- `stainless_brushed`（基线 / 默认）：BRUSHED_STEEL 拉丝外壳 (0.72,0.73,0.75) + STEEL_TOP 顶板 (0.66,0.67,0.69) + POLISHED_TUB (0.82,0.83,0.85) + PLINTH_GRAY (0.28,0.29,0.30) + STRIP_GRAY 控制条 (0.20,0.21,0.23) + HANDLE_DARK 把手 (0.10,0.10,0.11) + LCD_BLUE (0.25,0.50,0.92) + CHROME_WIRE 碗篮 (0.85,0.86,0.88)（全样本原色；fused_basket 加 BASKET_COATED (0.78,0.78,0.76)）。
- `glossy_white`：外壳 / 门改亮白 (0.93,0.93,0.94) + 浅灰顶板 + chrome 把手 (0.80,0.81,0.83) + dark 控制条；家用白色洗碗机身份。
- `matte_black`：外壳 / 门改哑黑 (0.13,0.13,0.15) + 黑顶板 + steel 把手 + LCD_BLUE accent + chrome 碗篮；现代黑色厨电身份。
- `steel_blue`：拉丝外壳带冷蓝调 (0.55,0.62,0.70) + steel 顶板 + chrome 把手 + dark 控制条；专业不锈钢蓝身份。
- `graphite_chrome`：石墨灰外壳 (0.30,0.31,0.33) + chrome 控制条 / bar_handle (0.80,0.81,0.83) + LCD_BLUE + chrome 碗篮；高端厨电身份。

## Multiplicity / Copy Logic

**1 根小类级 multiplicity 主轴**（碗篮数 —— 仅在 drop_down_door 分支展开）：

- **count_param**：`rack_count`（模板内变量 N；sources 用 `NUM_RACKS`(racks_3) / `len(RACK_SPECS)`(handle_recessed_tall)；parent 用 hand-written `upper_rack` + `lower_rack`）。tub 内的滑出式碗篮数；每个碗篮是一个独立 PRISMATIC joint，所以 drop_down_door 的非 fixed joint 数 = 1 门铰 + rack_count。**这是 drop_down_door 分支的支配性多重性轴**；dish_drawer 分支 rack_count 是 trivial 端点（单 rack 固定在抽屉体内）。
- **N_range**：声明产品域 **[2, 3]**（真实独立式洗碗机 = 下篮 + 上篮，可选第三层浅 cutlery tray；>3 层堆叠滑篮不是真实配置，所以本轴刻意窄——source map 明确建议 [2,3]）。样本覆盖 {2,3} 已**完整覆盖**整个建议域。`config_from_seed` 的 sweep 采样域 **[2, 3]**（N=2 高频基线、N=3 含 cutlery tray 常见）。
- **sampling domain**：`config_from_seed` 在 drop_down_door 分支用 `rng.choices([2,3], weights=[偏 2])`；`resolve_config` 把任意外部 config 的 N clamp 到 [2,3]，并在 dish_drawer 分支解析为 trivial N=1（slot_choice 记 `n1`，见 §9 兼容矩阵）。
- **copied object**：单个碗篮 = `rack_{i}` part（碗篮 visual 由 Slot B 决定：wire_grid 细杆 / fused_basket CadQuery `basket_body`）+ 支撑（`wheel_{idx}`×4 for rack_0 wheeled lower、`side_runner_{k}`×2 for 上层 runner racks）由共享 `_populate_rack` helper 建（parent L231-320 / handle_recessed_tall L254-352）。
- **naming**：标准化为 **`rack_{i}` part + `rack_slide_{i}` joint**（0-based i，bottom→top）。两个 loop 源：racks_3_cutlery 用 `for i in range(NUM_RACKS)` 命名 `rack_{i}` / `rack_slide_{i}`（L378-392）；handle_recessed_tall 用 `for i, spec in enumerate(RACK_SPECS)` 命名 `rack_{i}` / `{spec['name']}_slide`（L375-395，即 `rack_0_slide` 等）。**两者等价；模板用 `rack_{i}` / `rack_slide_{i}`**（racks_3 形式，joint 名更规整）；runner 滑轨 loop-emit `rack_rail_{rail_idx}`（racks_3 L186-198）。
- **placement**：栈式 bottom→top **绝对式**——rack_0 sits on tub_floor（wheels，z_origin=TUB_FLOOR_TOP+0.010），每个更高的 rack 在自己一对 side rail 上 z 递增（rack_1 upper z≈0.45-0.50、rack_2 cutlery z≈0.62）；PRISMATIC origin z = 各 rack 静止高度 z_i，x=0，y = 小固定 inset（rack_yc≈-0.01）。每个 z_i 由 N + tub 高 + 各 rack height 解析（不累加漂移）→ N-不变前提。
- **joint policy**：每个碗篮是**独立 PRISMATIC joint**，parent=`cabinet`，axis=(0,1,0)（+Y 拉出），`MotionLimits(lower=0.0, upper=RACK_TRAVEL≈0.45, effort=20, velocity=0.5)`。**不链式、不共享 hub**——每个碗篮独立滑出 tub（racks_3 L382-392）。rack_0 rolls on `wheel_{idx}`；上层 rack glide on `side_runner_{k}` over `rack_rail_*`。
- **source/gating**：copy-logic 源取 handle_recessed_tall 的 `for i, spec in enumerate(RACK_SPECS)`（N=2 loop，L375-395）+ racks_3_cutlery 的 `for i in range(NUM_RACKS)`（N=3 loop，L378-392）+ 共享 `_populate_rack` helper。**N=2 即基线**（lower + upper），N=3 取 racks_3（+ shallow cutlery tray）。rack_count 与 opening_mechanism 的兼容见 §9（dish_drawer 把 rack_count 解析为 trivial N=1，单 rack 固定在抽屉体内）。

**rack_count 必须编入 `slot_choices_for_seed` 的 tuple**（`("rack_count", f"n{N}")`），否则不同碗篮数的拓扑维度损失（对齐 tool_cart drawer_count / cushion pan_count 范式）。

> 注：以下是**固定 N 的 module-local visual 复制**（非可变 count 轴、按 Rule 1 inline）：control_handle 的 `button_{i}`（4 个，`for i, bx in enumerate(...)`，all Slot C 变体）；side wall / rail / runner 对称对（`side_wall_{0,1}` / `tub_wall_{0,1}` / `rack_rail_{0,1}` / `handle_standoff_{i}` / `drawer_runner_{i}` / `cabinet_rail_{i}`，固定 2）；wire 格栅 / tine 网格 / runner 滑轨内的 inline loop（`_populate_rack` / `_build_basket_mesh` / `_build_cabinet` 内）；`wheel_{idx}`（固定 4 per wheeled rack）。这些都不是模板级可变 count 轴。

## 拓扑多样性审计

总组合数（离散槽 + multiplicity 主轴，**受 §9 兼容矩阵约束**）：
- 朴素笛卡尔积 = opening_mechanism(2) × rack_geometry(2) × control_handle(3) = **12** base topologies（source map combo 预审，≥10 ✓）。
- 叠 rack_count：drop_down_door 分支随 N∈{2,3}（2 值）展开 → drop_down_door 状态 = rack_geometry(2) × control_handle(3) × N(2) = 12；dish_drawer 分支 rack_count = trivial N=1（不展开）+ control_handle 受 gate（仅 front_fascia / proud_bar_handle，见 §9）→ dish_drawer 状态 = rack_geometry(2) × control_handle(2) × N1(1) = 4 → 合法状态 = 12 + 4 = **16** distinct（≥10 稳过）。

仅 opening_mechanism(2) × rack_geometry(2) × control_handle(3) = **12** 已含 2 种 defining motion（REVOLUTE 门 / PRISMATIC 抽屉）× 2 种碗篮 primitive（细杆 / CadQuery mesh）× 3 种控制 / 把手的结构差异；叠 rack_count + 兼容 gate → **16** ≥ 10 稳过。

理由：opening_mechanism(2 种 defining motion joint 拓扑：REVOLUTE 门 + N 个 PRISMATIC 篮 vs 单 PRISMATIC 抽屉) × rack_geometry(2 种碗篮 primitive) × control_handle(3 种控制 / 把手) × rack_count(drop_down_door 展开 [2,3]) 提供充裕真实结构差异。**rack_count 必须编入 slot_choices_for_seed**（`("rack_count", f"n{N}")`），否则 N=2 / N=3 在 slot_choice 上不可区分，损失主多重性维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` opening_mechanism，再 `rng.choice` rack_geometry，再 `rng.choice` control_handle（dish_drawer 时从 {front_fascia, proud_bar_handle} 选，gate 掉 top_hidden），再（drop_down_door 时）`rng.choices` 加权 N∈[2,3]（dish_drawer 时 rack_count 解析为 1），再 uniform 各连续 scale（解析 conditional：drawer_travel 仅 dish_drawer、rack_height/rack_travel 随碗篮档）。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（含一个 drop_down_door×wire_grid×front_fascia×N2 基线、一个 drop_down_door×N3 cutlery、一个 drop_down_door×top_hidden、一个 drop_down_door×proud_bar_handle、一个 dish_drawer×wire_grid、一个 fused_basket）。


Controlled local parameterization：见 §参数表的 cabinet_width_scale / cabinet_depth_scale / cabinet_height_scale / rack_travel_scale / drawer_travel_scale(conditional@dish_drawer) / rack_height_scale(conditional@drop_down_door)。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（opening_mechanism→rack_geometry→control_handle）→ 采 rack_count N（drop_down_door 加权 [2,3]；dish_drawer 解析为 1）→ 采 independent cabinet_width/depth/height/rack_travel scale → 派生（门宽 / 抽屉面宽 / 碗篮宽随 cabinet_width，碗篮深 / 抽屉 tub 深随 cabinet_depth，门高 DOOR_H / 碗篮 z 间距随 cabinet_height，rack_travel/drawer_travel 上限随 tub 深）→ 解析 conditional（rack_height 档、drawer_travel）→ 用 inequality 投影 / 回缩（碗篮栈占高 ≤ tub 可用高、碗篮 / 抽屉行程 ≤ 0.95·tub 深、门翻平不入地 oz0>0）。跨部件依赖显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 door/drawer/rack 的 joint origin、captured 接口、碗篮复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` opening_mechanism + rack_geometry + control_handle（dish_drawer 时 control_handle 从 {front_fascia, proud_bar_handle} 选），再 `rng.choices` 加权 N∈[2,3]（drop_down_door）/ 解析 N=1（dish_drawer），再 uniform 各 scale | slot_choices_for_seed 含 `("opening_mechanism",..),("rack_geometry",..),("control_handle",..),("rack_count",f"n{N}")` 且与 build 一致 |
| compatibility matrix | (1) **rack_count × opening_mechanism**：drop_down_door → rack_count∈[2,3] 全展开（每篮独立 PRISMATIC，rack_0 lower wheels + 上层 runners）；dish_drawer → rack_count 解析为 **trivial N=1**（单 rack 固定在 drawer 体内，无独立 joint），slot_choice 记 `n1`，不随采样 N 展开（避免给抽屉体加多个独立滑篮 joint，与单体拉出语义冲突）。 (2) **control_handle × opening_mechanism**：front_fascia / proud_bar_handle × 任意 opening_mechanism 均可（控制 visual 挂前面板）；**top_hidden × dish_drawer gate 掉**（top_hidden tests assert 关门控制藏 slab 下 / 开门旋出，依赖门 REVOLUTE 旋转；抽屉无旋转 → 首版仅 top_hidden × drop_down_door）。 (3) **rack_geometry × 任意正交**：wire_grid / fused_basket 均可装进 drop_down_door 的 N 个 rack 或 dish_drawer 的单 rack（只换碗篮 visual primitive，不改 joint）。 (4) **碗篮栈占高**：`Σ(rack_height[i]·scale)+gaps ≤ tub 可用高`，违反回缩 rack_height_scale / N（N≤3 样本基线已满足）。 (5) **行程 / 门翻平**：rack_travel/drawer_travel clamp ≤ 0.95·tub 深（不脱轨、仍部分 retained）；门 q=π/2 翻平 oz0>0 不入地。 | 无 floating / collision / 碗篮互撞或顶 tub / 门翻平入地 / 行程脱轨 / top_hidden×dish_drawer 语义错配 |
| controlled local variation | 6 个 clamped scale（cabinet_width/depth/height、rack_travel、drawer_travel@dish_drawer、rack_height@drop_down_door），每 build 统一；drawer_travel/rack_height 为 conditional；door_open_angle 固定 π/2 不缩放 | 比例变化不破坏 door/drawer/rack joint origin、captured 接口、碗篮行程、门翻平、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 opening_mechanism/rack_geometry/control_handle/rack_count QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| opening_mechanism | 2 | yes | no | drop_down_door(REVOLUTE 门 + N PRISMATIC 篮，multiplicity 载体) / dish_drawer(单 PRISMATIC 抽屉体)；**降到 2 的理由**：真实独立式洗碗机的开门 defining motion 只有放下式门 + 整体抽屉两种结构类（无第三种真实机构；侧铰立式门属冰箱、上掀门属洗衣机），样本池已覆盖这两类，符合 SPEC_TEMPLATE §4「样本不足可降到 2 但须说明理由」|
| rack_geometry | 2 | yes | no | wire_grid(Box 细杆格栅) / fused_basket(CadQuery 单 mesh + tine)；**降到 2 的理由**：碗篮几何真实结构家族只有开放钢丝格栅 + molded 塑料 fused-basket 两类（其余只是尺寸 / tine 密度差异，非结构差异），样本池覆盖这两类 |
| control_handle | 3 | yes | yes | front_fascia(前凸控制条+凹槽) / top_hidden(顶边凹控制，drop_down_door only) / proud_bar_handle(凸管 bar+支架)，3 种控制 / 把手形态 |
| rack_count (N) | 2（采样域 [2,3]，仅 drop_down_door 展开；dish_drawer 固定 n1）| yes | no | **multiplicity 主轴**，编入 slot_choice `("rack_count",f"n{N}")`；**N_range 窄到 [2,3] 的理由**：真实洗碗机 = 下篮+上篮(+可选第三层浅 cutlery tray)，>3 层堆叠滑篮不是真实配置（source map 明确）|

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名（opening_mechanism / rack_geometry / control_handle），且含 `("rack_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，rack_count 采样域 ⊆ [2,3]（drop_down_door 全展开；dish_drawer 解析为 1）
- `resolve_config` 把 rack_count clamp 到 [2,3]（drop_down_door）/ 1（dish_drawer）、各 scale clamp 到声明范围；rack_height/drawer_travel 为 conditional 随 opening_mechanism 解析；三条 clearance inequality（碗篮栈占高 / 碗篮 / 抽屉行程 / 门翻平不入地）在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（dish_drawer 固定 trivial 单 rack；top_hidden × dish_drawer gate 掉；行程不脱轨；碗篮不顶 tub；门翻平不入地）
- 连续 scale clamp 后不破坏 door/drawer/rack joint origin / captured 接口 / 碗篮 / 抽屉行程 / 门翻平 / 类别身份
- 关键 joint：门 `door_hinge` REVOLUTE axis≈(-1,0,0) origin=(0,BODY_FRONT_Y,PLINTH_H) lower=0 upper≈π/2（drop_down_door）；抽屉 `drawer_slide` PRISMATIC axis≈(0,1,0) origin=(0,BODY_FRONT_Y,DRAWER_BOTTOM_Z) lower=0 upper≈0.42（dish_drawer）；碗篮 `rack_slide_{i}` PRISMATIC axis≈(0,1,0) lower=0 upper≈0.45（drop_down_door，每篮独立 parent=cabinet）
- captured-slide：element-scoped `allow_overlap`（dish_drawer 的 cabinet_rail_{i}↔drawer_runner_{i} 望远镜，照搬 dishdrawer L479-489）；碗篮 nest / 滑出由 expect_within/expect_overlap/expect_gap 守（照搬 parent/racks_3 run_tests 段）
- copied object 遵循 `rack_{i}` 命名 + 绝对式 bottom→top placement（各 rack 静止 z_i）+ 独立 PRISMATIC joint policy；**必须用 loop 形式**（handle_recessed_tall enumerate RACK_SPECS / racks_3 range NUM_RACKS），NOT parent 的两个手写 upper_rack/lower_rack
- 固定 N inline 复制（button_{i} / side_wall_{0,1} / wheel_{idx}×4）遵循 Rule 1（visual on parent 或随 part 动，无独立 multiplicity 轴）
- grandfather：所有 hinge/slide/captured 接口省略 MatingContract，由 origin 检查 + allow_overlap + expect_* 守

## Reject cases

- 把 rack_count 当普通 int 参数、不进 slot_choice → 不同碗篮数 slot_choice 同形，损失主多重性维度（违反 §8/§9 硬要求）。
- **照搬 parent 的两个手写 `upper_rack` / `lower_rack`（两次 `model.part` + 两次 `_populate_rack`）而非 loop** → 无法随 rack_count 展开 N；**必须用 loop 形式**（`for i, spec in enumerate(RACK_SPECS)`（handle_recessed_tall）或 `for i in range(NUM_RACKS)`（racks_3）），emit `rack_{i}` + `rack_slide_{i}`。
- 把碗篮做成链式 / 共享 hub 而非每篮独立 PRISMATIC parent=`cabinet` → 违反 joint policy；所有 door 样本是每篮独立滑出。
- 在 dish_drawer 候选下仍按采样 N 给抽屉体加多个独立滑篮 joint、不解析为 trivial 单固定 rack → 与「整 tub 总成单体拉出」语义冲突；必须 gate（dish_drawer rack_count=1，单 rack 固定在 drawer 体内随抽屉拉出）。
- 在 dish_drawer 上用 top_hidden（控制凹门顶、依赖门旋转暴露）→ 抽屉无 REVOLUTE 旋转，控制无法旋出；首版必须 gate（top_hidden 仅 drop_down_door）。
- 把 control_strip / pocket_handle / control_panel / bar_handle / button_{i} 做成独立活动 part 加 joint → 违反 Rule 1（控制 / 把手是 visual on Slot A 活动件 front_door / drawer，随门 / 抽屉动，无独立 joint）。
- 门 / 抽屉 / 碗篮 rest pose 设成开 / 拉出而非 q=0 → current-pose 与 viewer 目检不符（所有样本 lower=0 关闭 / nest）。
- 碗篮 / 抽屉满行程后脱出 tub（不再部分 retained）→ §7 行程不等式 FAIL；须回缩 travel（≤0.95·tub 深，保证 expect_overlap axis=y ≥0.02）。
- 门翻平（q=π/2）入地（oz0<0）→ §7 门翻平不等式 FAIL；须保 hinge 在 PLINTH_H 高 + 门高 DOOR_H 几何使翻平后离地。
- 碗篮栈总高超 tub 可用高 / 碗篮互撞 → §7 碗篮栈占高不等式 FAIL；须回缩 rack_height_scale 或 N（N≤3 样本基线已满足）。
- 给 hinge/slide/captured-slide 接口补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap + expect_*。
- 把连续尺寸 / 颜色 / 材质（palette_style / cabinet scale / tine 密度）当新 candidate 塞进 slot → 不是结构差异。
- 把**冰箱 / 冷柜**（侧铰立门 + 层架储物）或**烤箱**（空腔 + 烤架无碗篮）或**普通柜 / 抽屉柜**（无 tub liner / 无碗篮 / 无控制面板）或**洗衣机**（圆舱门 + 滚筒）语义混入 → 出类，本类是洗涤 tub + 滑出碗篮 + 控制面板的洗碗机。

## 与相邻类别的边界

- 不该混入：**冰箱 / 冷柜（refrigerator / freezer）**——侧铰立式门 + 内部层架 / 抽屉储物，无底铰放下式门、无洗涤 tub liner、无 chrome wire 滑出碗篮；本类核心是放下式门 / 抽屉 + tub + 滑出碗篮 + 控制面板。
- 不该混入：**烤箱 / 微波炉（oven / microwave）**——同样底铰下翻门但内部是空腔 + 烤架（无 chrome wire 碗篮 / 无侧滑轨 / 无抛光 tub liner）；本类必须有滑出式碗篮（wire_grid / fused_basket）+ tub。
- 不该混入：**普通橱柜 / 抽屉柜（cabinet / chest of drawers）**——纯储物家具，无 tub liner / 无碗篮 / 无控制面板 / LCD / buttons；本类是带洗涤腔 + 控制面板的电器（dish_drawer 候选虽抽屉形态但内含 tub + chrome rack + 控制 → 仍是洗碗机）。
- 不该混入：**洗衣机 / 烘干机（washing machine / dryer）**——前置圆舱门 + 滚筒（非矩形门 / 抽屉 + 矩形碗篮栈）；本类是矩形门 / 抽屉 + 矩形滑出碗篮。
- Kitchen 大类内：区别于无「放下式门 / 整体抽屉 + 洗涤 tub liner + 滑出 chrome 碗篮 + 前 / 顶控制面板」身份的其它厨电（灶具 range / 油烟机 / 水槽）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) rack_count N_range 取 **[2,3]**（样本完整覆盖 {2,3}，与 source map 一致；真实洗碗机不超 3 层滑篮）是否接受；(2) **rack_count multiplicity 仅 drop_down_door 分支展开，dish_drawer 解析为 trivial N=1**（单 rack 固定在抽屉体内，slot_choice 记 `n1`）的兼容策略是否接受；(3) **top_hidden × dish_drawer 首版 gate 掉**（top_hidden 依赖门 REVOLUTE 旋转暴露控制，抽屉无旋转）是否接受，还是要求把 dish_drawer 的 top_hidden 重锚到前面板再纳入采样；(4) opening_mechanism / rack_geometry 各 **降到 2 个 candidate**（真实结构家族只有门 / 抽屉、wire / fused 两类）的降级理由是否充分；(5) Topology target ~16 <300 的说明（本小类结构高度收敛 + rack_count 仅 [2,3] 两档，与 cushion/tool_cart 同类情形）是否接受，或要求把 rack_height 离散档也进 slot_choice 再拉一维；(6) palette_style 5 套 colorway（stainless/white/black/blue/graphite）是否覆盖足够；(7) 模板**必须用 loop 形式 emit 碗篮**（handle_recessed_tall enumerate RACK_SPECS / racks_3 range NUM_RACKS），NOT parent 的手写 upper_rack/lower_rack —— 这一硬约束是否在 spec 中表达清楚。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：cabinet mesh 按 opening_mechanism 分（drop_down_door=`_build_cabinet`(含 rack_rail + 开门 front)、dish_drawer=`_build_cabinet`(加 lower_front_panel + cabinet_rail，无门铰)）；碗篮 N 复制复用同一 `_populate_rack(rack, height, support, ...)` helper + 按 rack_geometry 分支（wire_grid 多 Box 细杆 / fused_basket `_build_basket_mesh` CadQuery）；门 = `_build_door`(随 control_handle 分支 front_fascia/top_hidden/proud_bar_handle 改控制 visual)；drawer = `_build_drawer`(含 `_add_rack_wires` 前缀化 wire 或 fused basket)。
- **碗篮 loop emission（最关键实现点）**：drop_down_door 分支用 `RACK_SPECS`/`RACK_CONFIGS` 列表 + `for i, spec in enumerate(...)` 或 `for i in range(N)` emit `rack_{i}` + `rack_slide_{i}`（参 handle_recessed_tall L375-395 N=2 / racks_3 L378-392 N=3）；rack_0=lower(wheels, z=TUB_FLOOR_TOP+0.010)、rack_1=upper(runners, z≈0.45-0.50)、rack_2=shallow cutlery(runners, z≈0.62, height≈0.04)；runner 滑轨 loop-emit `rack_rail_{rail_idx}`（racks_3 L186-198，只为 runner-supported rack 建）。dish_drawer 分支把单 rack 固定在 `drawer` 体内（`_add_rack_wires` / fused basket，无独立 joint）。
- captured 接口 allow_overlap / expect_*：dish_drawer 的 `cabinet_rail_{i}` ↔ `drawer_runner_{i}` 望远镜 `allow_overlap`（照搬 dishdrawer L479-489）；门 panel↔side_wall `expect_contact`、碗篮 nest `expect_within`(xy) + 门↔篮 `expect_gap`(y)、wheels↔tub_floor / runners↔rack_rail `expect_contact`、滑出 `expect_overlap`(y) + `expect_gap`(z over folded door)（照搬 parent/racks_3 run_tests 段）。
- conditional 范围解析顺序：先采 opening_mechanism → rack_geometry → control_handle（dish_drawer gate top_hidden）→ rack_count（drop_down_door 加权 [2,3]；dish_drawer 解析 1）→ 解析 rack_height 档（lower 深 / upper 浅 / cutlery 更浅）/ drawer_travel（仅 dish_drawer）→ 采 cabinet_width/depth/height/rack_travel independent → 派生（门 / 抽屉面宽 / 碗篮宽 / 深 / 门高 DOOR_H / 碗篮 z 间距 / travel 上限）→ 投影三条 clearance inequality（碗篮栈占高 ≤ tub 可用高、行程 ≤ 0.95·tub 深、门翻平 oz0>0）。
- fused_basket 需 `import cadquery as cq` + `mesh_from_cadquery`（参 fused_basket L25, L37, L230-340）；wire_grid 纯 Box 不需 cadquery。
- 参考模板：`agent/templates/Handtools_Tool_cart.py`（multiplicity 范式：count 轴(drawer_count↔rack_count) 编 slot_choice + 绝对式 placement + 共享 `_populate`/mesh helper 复用 + 兼容矩阵 gating（cabinet_door 固定浅栈 ↔ dish_drawer 固定单 rack 同构）+ captured allow_overlap 骨架）；`agent/templates/Accessories_Cushion.py`（mixed pattern：固定 named slots + `("count",f"n{N}")` 进 slot_choice + 兼容矩阵 + palette_style 不计入 slot_choice 范式）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/rack_count（parent 基线）| drop_down_door + wire_grid + front_fascia（+ hand-written N=2 racks）| rec_model-a-freestanding-stainless-steel-dishwasher-_…_c2d628fd | `_build_cabinet` L83-175 / `_build_door`(front_fascia: control_strip L193-198 / pocket_handle L202-207 / display_lcd L210-215 / button_{i} L218-227) / `_populate_rack`(wire_grid) L231-320 / `door_hinge` REVOLUTE L336-344 / rack PRISMATIC L348-365 / run_tests envelope/door/rack expect_* L370-572 | root cabinet + tub liner + rack_rail + drop_down_door REVOLUTE + wire_grid 碗篮 + front_fascia 控制 + door 家族 captured 范式（**注：racks 手写，模板改用 loop**）|
| S2 | rack_count（N=2 loop）| drop_down_door + N=2 loop racks | rec_dish_washer_var_door_handle_recessed_tall | `RACK_SPECS`(2 dict) L65-84 / `for i, spec in enumerate(RACK_SPECS)` L375 / `model.part(spec["name"])` + `_populate_rack` L376-384 / `{spec['name']}_slide` PRISMATIC L385-395 / rail upper_z L182-189 | **rack_count N=2 loop-emit 源**（enumerate RACK_SPECS → rack_0 lower wheels + rack_1 upper half-rack runners + 各自 PRISMATIC slide）|
| S3 | rack_count（N=3 loop）| drop_down_door + N=3 loop racks + cutlery tray | rec_dish_washer_var_racks_3_cutlery | `RACK_CONFIGS`(3 dict) + `NUM_RACKS` L68-88 / `for i in range(NUM_RACKS)` L378 / `model.part(f"rack_{i}")` + `_populate_rack` L380-381 / `rack_slide_{i}` PRISMATIC L382-392 / runner 滑轨 loop `rack_rail_{rail_idx}` L186-198 | **rack_count N=3 loop-emit 源**（range NUM_RACKS → rack_0/rack_1/rack_2 cutlery tray + rack_slide_{i} + loop-emit rail；规整 `rack_{i}`/`rack_slide_{i}` 命名范式）|
| S4 | A | dish_drawer | rec_dish_washer_var_door_drawer_dishdrawer | `_build_drawer`(drawer_panel + tub liner + drawer_runner_{i} + 单 rack `_add_rack_wires`) L238-352 / `drawer_slide` PRISMATIC L364-374 / cabinet `lower_front_panel` L202-209 + `cabinet_rail_{i}` L224-232 / runner-in-rail allow_overlap L479-489 / `_add_rack_wires` 前缀化 wire L89-150 | 整体抽屉拉出机构（单 PRISMATIC，单固定 rack 在 drawer 体内 → rack_count trivial N=1）+ 望远镜 runner-in-rail captured allow_overlap 范式 |
| S5 | B | fused_basket | rec_dish_washer_var_rack_geom_fused_basket | `import cadquery as cq` L25 / `_build_basket_mesh(w,d,h)`(floor + 4 walls union + rarray tine) L230-297 / `mesh_from_cadquery(...,"basket_body")` `_populate_rack` L334-340 / `BASKET_COATED` L78 | molded fused-basket 碗篮 primitive 升级（CadQuery 单 mesh + tine 网格 → 单 basket_body visual，替代 wire 格栅）|
| S6 | C | top_hidden | rec_dish_washer_var_door_top_control | `_build_door`(control_panel 凹门顶边 L204-209 / pocket_handle L215-220 / display_lcd L223-228 / button_{i} top face L232-238) / tests 关门藏 slab 下 L501-506 / 开门旋出前向 L567-572 | 顶边隐藏控制（依赖门 REVOLUTE 旋转暴露 → conditional@drop_down_door）|
| S7 | C | proud_bar_handle | rec_dish_washer_var_control_body_fascia_handle | `_build_door`(control_strip L193-198 / handle_standoff_{i} L211-219 / bar_handle Cylinder bar_len=0.50 L220-228 / display_lcd L230-236 / button_{i} L238-248) | 凸管 grab-bar 把手（全宽 Cylinder >0.40 span on 两 standoff 支架 >0.02 standoff，替代凹槽 pocket）|
