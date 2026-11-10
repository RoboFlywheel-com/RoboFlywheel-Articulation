# utility_box — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `utility_box` |
| template path | `agent/templates/Urban_Environment_utility_box.py` |
| test path (optional) | `tests/agent/test_utility_box_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (door / body / vent / base / roof children mount on a common shell; door & louver & leg three multiplicity axes) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 |
| read_count | 12 |
| read_scope | all 5-star samples in this category (4 parent forks + 8 converged variants) |
| source_index_policy | only adopted module sources are indexed below |

源码绝对路径（rev_000001/model.py）：
- S_tall = `data/records/rec_tall-narrow-street-electrical-utility-cabinet-we_20260608_164447_204319_864f73c7/revisions/rev_000001/model.py`
- S_grey = `data/records/rec_grey-galvanized-steel-street-electrical-distribu_20260608_164505_793099_7e9a7c89/revisions/rev_000001/model.py`
- S_wide = `data/records/rec_wide-double-door-street-electrical-cabinet-on-a-_20260608_164520_373943_20824ffb/revisions/rev_000001/model.py`
- S_small = `data/records/rec_small-ground-level-steel-utility-junction-box-st_20260608_164538_025408_6f7d1e9a/revisions/rev_000001/model.py`
- S_triple = `articraft_data/data/records/rec_utility_box_var_triple_door_bank/revisions/rev_000001/model.py`
- S_shutter = `data/records/rec_utility_box_var_roller_shutter/revisions/rev_000001/model.py`
- S_cube = `data/records/rec_utility_box_var_cube_footprint/revisions/rev_000001/model.py`
- S_louver = `data/records/rec_utility_box_var_louver_rows/revisions/rev_000001/model.py`
- S_mesh = `data/records/rec_utility_box_var_mesh_grille/revisions/rev_000001/model.py`
- S_dbllouver = `data/records/rec_utility_box_var_double_louver_doors/revisions/rev_000001/model.py`
- S_legs = `data/records/rec_utility_box_var_tall_legs/revisions/rev_000001/model.py`
- S_canopy = `data/records/rec_utility_box_var_canopy_roof/revisions/rev_000001/model.py`

阅读要点（共性结构家族）：所有 12 个样本都是 `support(ROOT) → FIXED → body(hollow shell, front -Y open) → REVOLUTE/PRISMATIC → door/lid/shutter` 的同一拓扑骨架。
- 共享 helper `_hollow_box(outer, wall, open_face)` 出现在全部样本，发射 5–6 片 wall `shell_{i}`（front 门型 open `-y`，顶翻盖型 open `+z`）。
- 门型样本（tall/grey/wide/cube/canopy/triple/louver/mesh/dbllouver）门 LOCAL ORIGIN = 铰边，门皮中心偏置 `skin_cx = ±DOOR_W/2`，joint origin 落在前面板平面 `door_face_y = FRONT_Y + DOOR_T/2 + DOOR_GAP`，铰轴竖直 `axis=(0,0,±1)`，`upper≈115–135°`。
- 顶翻盖样本 S_small：lid LOCAL ORIGIN = 后铰边，板沿 `-Y` 伸出，铰轴水平 `axis=(-1,0,0)`，`upper≈105°`；另带前 hasp clasp REVOLUTE（轴 `-X`，`upper≈110°`）。
- 卷帘样本 S_shutter：curtain `shutter_slat_{i}` loop（N≈22），PRISMATIC `axis=(0,0,1)`，`upper=SHUTTER_TRAVEL≈0.72`，retract 进 head_box。
- BarrelHinge 静态装饰统一 `hinge_{j}`（pin 轴 local Z = 竖直；S_small 顶铰用 rpy pitch +π/2 把 pin 转水平）。
- vent 样本用 `SlotPatternPanelGeometry`（louver slot）、`VentGrilleGeometry`（角度 slat）、或 `Cylinder` 阵列（mesh hole）。

## 核心身份

`utility_box` = 街边钢制电力/公用配电柜（street electrical cabinet / utility junction box）：一个落地或离地架空的箱形钢制 enclosure，前面（或顶面）有一扇或多扇可开合的铰链门 / 翻盖（REVOLUTE 为定义性 joint；少数为卷帘 PRISMATIC），柜身常带通风（百叶 louver 行 / 网孔 mesh grille）、坐落在裙座 plinth / 混凝土基座 / 短腿 / 高腿上，顶部带 drip cap 或斜坡雨棚。成熟域：W 0.36–0.84 m，D 0.30–0.58 m，body_H 0.18–0.85 m，离地腿 0–0.60 m。表面贴纸/涂鸦/警示牌/闪电符/conduit 桩为 parent visual 装饰，不立轴。

不该混入：
- **fire_cabinet（金属消防柜）**：同样是带门金属柜，但身份是红色消防柜+玻璃面板+卷管盘/灭火器内胆；utility_box 是灰/绿/米钢制电力柜、louver 通风、警示电符号、conduit 入线、户外落地。重叠最大处在「钢制带门柜」骨架，靠 palette（galv-grey/green/beige 非消防红）、户外 plinth/legs 基座、louver/mesh 通风（非玻璃面板）、conduit 入线区分。
- **phone_box（电话亭）**：人可进入的亭体、玻璃围壁、内部话机；utility_box 是不可进入的小型 enclosure，无玻璃围壁、无内部人用设备。
- **mailbox（邮箱）**：投递口 slot + 取件门 + 立杆；utility_box 无投递 slot，门覆盖整面而非小取件口，基座是宽 plinth/腿而非细立杆。

## 槽位 + 候选模块表

### Slot A：door / opening 主机构（柜体开合动作 = 定义性 joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_revolute_side | S_tall | L139-L206 | eligible if compatible | 单前门，LOCAL ORIGIN=铰边（skin_cx=-DOOR_W/2），REVOLUTE 竖直 `axis=(0,0,1)`，joint origin 在 +X jamb，`upper=115°`，门覆盖整面 |
| double_mimic | S_wide | L87-L148 (`_build_door`), L230-L267 (双调用+mimic) | eligible if compatible | 双门各 outer 铰，`_build_door(mirror)` X-镜像，door_1 `axis=(0,0,-1)` + `Mimic(body_to_door_0)` 联动；body 加 `center_mullion` |
| triple_door_bank(N) | S_triple | L93-L145 (`_build_door`), L228-L251 (range(N) loop) | eligible if compatible | N 门横排，`door_{i}` loop + 共享 `_build_door`，规则 X 间距 `_door_hinge_x(i)`，各独立 REVOLUTE `axis=(0,0,-1)`，N-1 个 `mullion_{i}` |
| top_revolute_lid + hasp | S_small | L251-L335 (lid+joint), L337-L399 (clasp+joint) | eligible if compatible | 顶翻盖，LOCAL ORIGIN=后铰边，板沿 -Y 伸出，REVOLUTE 水平 `axis=(-1,0,0)` `upper=105°`；+ 前 hasp clasp REVOLUTE `axis=(-1,0,0)` `upper=110°` |
| roller_shutter(N slats) | S_shutter | L228-L267 (shutter part + `shutter_slat_{i}` loop), L273-L283 (PRISMATIC) | eligible if compatible | 卷帘竖直 PRISMATIC `axis=(0,0,1)` `upper≈0.72`，curtain `shutter_slat_{i}` loop + bottom_rail + edge_rails，body 加 head_box+guide_rails |

降级说明：无单候选 slot；本 slot 5 个候选含 REVOLUTE-竖直立轴 / REVOLUTE-水平横轴 / PRISMATIC 三种 joint 拓扑。

### Slot B：body footprint（体形/比例 — 结构形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| tall_narrow | S_tall | L38-L43 (dims), L99-L137 (shell) | eligible if compatible | 高窄（W0.46 D0.30 H0.80），test 断言 `H > W + 0.25` |
| medium | S_grey | L42-L48 (dims), L107-L143 (shell) | eligible if compatible | 中等比例（W0.62 D0.40 H0.85） |
| wide_squat | S_wide | L47-L51 (dims), L182-L228 (shell) | eligible if compatible | 宽矮（W0.84 D0.55 H0.72），略宽于高 |
| cube | S_cube | L43-L50 (W=D=BODY_H=0.58), L109-L145 (shell) | eligible if compatible | 近立方体 squat，test 断言 `|W-D|<0.05 ∧ |W-H|<0.05` |
| low_ground_box | S_small | L39-L55 (dims, BOX_H0.18), L81-L249 (shell+rim) | conditional: top_revolute_lid 专用 | 低矮地面箱（W0.36 D0.30 H0.18），顶开口 open_face `+z`，test 断言 footprint > height |

### Slot C：ventilation（通风样式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| solid | S_small | （无 vent visual，门/盖实心） | eligible if compatible | 无通风开孔（顶翻盖箱常实心） |
| louver_slots | S_tall | L152-L170 (2 个 `door_grille_{k}` SlotPatternPanel) | eligible if compatible | 1–2 条水平百叶 slot 面板，`SlotPatternPanelGeometry`，rpy roll +π/2 朝前 |
| louver_rows(N) | S_louver | L57-L101 (`_louver_row_mesh` helper), L180-L193 (range(N) loop) | eligible if compatible | N 行水平百叶满门竖直堆叠，`louver_{i}` loop + 共享 grille helper，规则 pitch |
| mesh_grid | S_mesh | L58-L72 (params+helper), L171-L224 (frame + 行列 `mesh_hole_{i}` loop) | eligible if compatible | 网孔穿孔栅格，`mesh_hole_{i}` 行列 Cylinder loop + 4 条 frame bar |
| vent_grille_side | S_legs | L72-L74,L214-L249 (`VentGrilleGeometry` side wall vents) | eligible if compatible | 侧壁角度 slat 百叶（`VentGrilleGeometry`），装在 ±X 墙（door 占整面或离地箱时用） |

### Slot D：base / support（底座/支撑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| steel_plinth | S_tall | L84-L97 (plinth skirt, PLINTH_INSET 略窄于体) | eligible if compatible | 短钢裙 plinth，base z=0，略窄于体 |
| concrete_plinth | S_grey | L84-L105 (pedestal, PLINTH_OVER 宽于体 + conduit 桩) | eligible if compatible | 混凝土基座宽于体，test 断言 plinth_x > body_x + 0.05 |
| stepped_concrete | S_wide | L159-L180 (lower step + upper step 两级) | eligible if compatible | 两级阶梯混凝土（base_lower_step + base_upper_step） |
| four_short_legs | S_small | L126-L142 (`leg_{li}` + `foot_pad_{li}` 4 角 loop) | eligible if compatible | 四短腿 + foot pad（box 自带 leg loop，LEG_H≈0.06） |
| tall_legs(N) | S_legs | L76-L106 (`_leg_visuals` helper), L405-L432 (range(N) `leg_{i}` 独立 part + FIXED) | eligible if compatible | N 条高细钢腿离地架空（LEG_H≈0.60），`leg_{i}` 独立 part loop + 统一 FIXED + foot_pad + top_gusset |

### Slot E：roof（顶盖）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_drip_cap | S_grey | L117-L123 (drip_cap Box 略大于体) | eligible if compatible | 平顶 drip cap（Box 略大于体，drip lip） |
| pitched_canopy | S_canopy | L66-L121 (`_build_canopy` cadquery 三棱柱 gable + fascia), L182-L189 (mount) | eligible if compatible | 斜坡 gable 雨棚，真实 cadquery 角度几何（三棱柱 + 4 条 fascia drip edge），peak 高出体顶 |
| roof_cap_overhang | S_legs | L187-L212 (roof_cap + 3-side drip lip) | eligible if compatible | 平顶 cap + 三面 drip lip（前面开口），离地腿型常配 |

降级说明：roof slot 与 Slot A 的 top_revolute_lid 互斥（顶翻盖即顶面，无独立 roof；见 compatibility matrix）。

## 槽位图（slot graph）

pattern: `parallel_children`（door / vent / roof 挂到 body；base 是 body 的 parent 支撑；door 是 ROOT→base→body 链尾的定义性活动 child）

```
base[D] (ROOT, z=0)
  --[FIXED, origin=() 或 leg corner FIXED ×N]--> body[B] (hollow shell, front -Y open 或 top +z open)
        +-- vent[C]   (parent visual on body wall / door face, no joint)
        +-- roof[E]   (parent visual on body top, FIXED-as-visual)  [与 top_lid 互斥]
        +-- door[A]   --[REVOLUTE 竖直 axis=(0,0,±1) @ jamb plane]--> 单/双/N 门
                       --[REVOLUTE 水平 axis=(-1,0,0) @ 后铰边]----> 顶翻盖 lid (+ clasp REVOLUTE)
                       --[PRISMATIC 竖直 axis=(0,0,1) @ 前opening底]--> roller curtain
```

接口点位：
- **base→body（FIXED）**：plinth/concrete 型 `origin=Origin()`（body 中心 Z = support_top + BODY_H/2，坐在基座顶）；tall_legs/four_legs 型每条腿 `cabinet_to_leg_{i}` FIXED，origin=corner `(±(W/2-inset), ±(D/2-inset), BOX_BOTTOM)`，腿 LOCAL 顶在 body 底。
- **body→door（REVOLUTE 竖直）**：joint origin `(HINGE_X 或 ±OUTER_X 或 _door_hinge_x(i), door_face_y, support_top+BODY_H/2)`，门 LOCAL ORIGIN=铰边在此对齐，q=0 门平贴前面板；多门各自独立 origin（triple）或 mimic（double）。
- **body→lid（REVOLUTE 水平）**：joint origin `(0, REAR_Y+LID_OVER, RIM_Z+LID_T/2)`，lid LOCAL ORIGIN=后铰边，板沿 -Y 伸出，`axis=(-1,0,0)` 抬前缘上翻。
- **body→shutter（PRISMATIC 竖直）**：joint origin `(0, FRONT_Y, support_top)`，curtain 沿 +Z retract 进 head_box。
- **vent**：装在 body 墙或 door face 的 parent visual，无 joint（mesh/louver 阵列）。
- **roof**：装在 body 顶的 parent visual（drip_cap / canopy / roof_cap），无独立 joint。

互斥 / 派生：
- top_revolute_lid（Slot A）⟹ body 用 low_ground_box（Slot B，open_face `+z`）+ four_short_legs（Slot D）+ **no roof**（顶面即盖）；vent 限 solid / vent_grille_side。
- roller_shutter（Slot A）⟹ body 加 head_box + guide_rails（module-local），vent 强制走 vent_grille_side（侧壁，门面被 curtain 占满）。
- door_face louver/mesh（louver_slots/louver_rows/mesh_grid）只在 front-door 型（single/double/triple）合法；shutter / lid 型走 vent_grille_side / solid。

## 每槽位 Module Emits / Interfaces

### Slot A / module single_revolute_side
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door`(door_skin + handle_plate/pocket + handle_lever) | S_tall / L139-L188 |
| internal joints | 无（门内无 sub-joint） | — |
| upstream interface | door LOCAL ORIGIN = 铰边；joint origin 在 body 前面板 +X jamb | S_tall / L144-L150, L195-L201 |
| downstream interface | `body_to_door` REVOLUTE `axis=(0,0,1)` `upper=115°` | S_tall / L196-L206 |

### Slot A / module double_mimic
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_0` `door_1`（`_build_door(mirror)`）+ body `center_mullion` | S_wide / L87-L148, L195-L200 |
| internal joints | 无 | — |
| upstream interface | 各门 LOCAL ORIGIN=自身 outer 铰边；joint origin `±OUTER_X` | S_wide / L235-L246, L256-L261 |
| downstream interface | `body_to_door_0` `axis=(0,0,1)`；`body_to_door_1` `axis=(0,0,-1)` + `Mimic(door_0)` | S_wide / L241-L267 |

### Slot A / module triple_door_bank(N)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_{i}` ×N（loop + `_build_door`）+ body `mullion_{i}` ×(N-1) + `hinge_{i}_{j}` | S_triple / L190-L222, L228-L251 |
| internal joints | 各门独立 `body_to_door_{i}` REVOLUTE `axis=(0,0,-1)` | S_triple / L241-L251 |
| upstream interface | door LOCAL ORIGIN=左铰边；`_door_hinge_x(i)` 规则 X 间距 | S_triple / L69-L77, L240-L246 |
| downstream interface | N 个独立 REVOLUTE（非 mimic，独立开合） | S_triple / L241-L251 |

### Slot A / module top_revolute_lid + hasp
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`(lid_plate + lips + corner_tab + rivets) + `clasp`(hasp lever) | S_small / L251-L320, L340-L390 |
| internal joints | `box_to_lid` REVOLUTE `axis=(-1,0,0)`；`box_to_clasp` REVOLUTE `axis=(-1,0,0)` | S_small / L327-L335, L391-L399 |
| upstream interface | lid LOCAL ORIGIN=后铰边；body open_face `+z` | S_small / L84, L251-L261, L326-L332 |
| downstream interface | lid 抬前缘上翻 `upper=105°`；clasp 上翻释放 `upper=110°` | S_small / L334, L398 |

### Slot A / module roller_shutter(N slats)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `shutter`(bottom_rail + `shutter_slat_{i}` ×N + edge_rail) + body head_box/guide_rails | S_shutter / L228-L267, L152-L180 |
| internal joints | 无（slat 是 rib loop 非独立 joint） | S_shutter / L240-L247 |
| upstream interface | joint origin 前 opening 底中心 `(0, FRONT_Y, PLINTH_H)` | S_shutter / L273-L278 |
| downstream interface | `body_to_shutter` PRISMATIC `axis=(0,0,1)` `upper=0.72` retract 进 head_box | S_shutter / L273-L283 |

### Slot B / module（tall_narrow / medium / wide_squat / cube / low_ground_box）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`/`box`/`cabinet`：`shell_{i}` hollow box（5–6 wall）+ inertial | S_tall L99-L137 / S_cube L109-L145 / S_small L81-L249 |
| internal joints | 无 | — |
| upstream interface | body 坐在 support 顶：body_cz = support_top + BODY_H/2 | S_tall / L101 |
| downstream interface | 前面板 -Y open（门型）或顶面 +z open（lid 型）= 门挂载面 | `_hollow_box(open_face)` 全样本 |

### Slot C / module（vent 各候选）
| emits | 描述 | 来源 |
|---|---|---|
| parts | door face: `door_grille_{k}` / `louver_{i}` / `mesh_hole_{i}`+frame；side: `side_vent_{s}` | S_tall L152-L170 / S_louver L180-L193 / S_mesh L171-L224 / S_legs L214-L249 |
| internal joints | 无（通风为 parent visual） | — |
| upstream interface | 贴 door face front (-Y, rpy roll +π/2) 或 ±X 墙（rpy pitch ±π/2） | S_tall L167 / S_legs L231-L248 |
| downstream interface | 无（不承载下游） | — |

### Slot D / module（base 各候选）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `plinth`/`base`：skirt / pedestal+conduit / 两级 step / `leg_{i}`+foot_pad | S_tall L84-L97 / S_grey L84-L105 / S_wide L159-L180 / S_legs L405-L432 |
| internal joints | tall_legs/four_legs：`cabinet_to_leg_{i}` FIXED ×N | S_legs / L426-L432 |
| upstream interface | base bottom = z=0（落地）；conduit/foot_pad 触地或入体 | 全 base 样本 |
| downstream interface | base→body FIXED（plinth `origin=()`；legs corner origin） | S_tall L209-L215 / S_legs L426-L432 |

### Slot E / module（roof 各候选）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drip_cap` / `rain_canopy`(cadquery) / `roof_cap`+lips | S_grey L117-L123 / S_canopy L182-L189 / S_legs L187-L212 |
| internal joints | 无 | — |
| upstream interface | 装在 body 顶 z = support_top + BODY_H（parent visual） | S_canopy / L186 |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| door_module | enum | single_revolute_side / double_mimic / triple_door_bank / top_revolute_lid / roller_shutter | — | choice | deterministic procedural sampler | Slot A |
| body_module | enum | tall_narrow / medium / wide_squat / cube / low_ground_box | — | choice | sampler；low_ground_box conditional on top_lid | Slot B |
| vent_module | enum | solid / louver_slots / louver_rows / mesh_grid / vent_grille_side | — | choice | sampler；door-face vent gated by front-door door_module | Slot C |
| base_module | enum | steel_plinth / concrete_plinth / stepped_concrete / four_short_legs / tall_legs | — | choice | sampler；four_short_legs conditional on top_lid | Slot D |
| roof_module | enum | none / flat_drip_cap / pitched_canopy / roof_cap_overhang | — | choice | sampler；none required when top_lid | Slot E |
| door_count_N | int | [1,4] | 1 | conditional | 仅 triple_door_bank 轴；N=1→single, N=2→可 double, N≥2 横排 | S_triple L58-L63 |
| louver_row_N | int | [3,12] | 8 | conditional | 仅 louver_rows / dbllouver 轴；竖直 pitch = span/(N-1) | S_louver L58, L184 / S_dbllouver L75-L78 |
| leg_N | int | {4,6} | 4 | conditional | 仅 tall_legs 轴（4 角，6=长体加中腿） | S_legs L42, L408 |
| shutter_slat_N | int | derived | 22 | equation | `= round(CURTAIN_H / SLAT_PITCH)`；随 curtain 高度，非独立轴 | S_shutter L52-L59 |
| width_scale | float | [0.90, 1.10] | 1.0 | independent | W 缩放后 clamp；门皮/铰/vent 随 W | 全 dims |
| depth_scale | float | [0.90, 1.10] | 1.0 | independent | D 缩放 | 全 dims |
| height_scale | float | [0.90, 1.10] | 1.0 | independent | BODY_H 缩放 | 全 dims |
| leg_height_scale | float | [0.85, 1.15] | 1.0 | conditional | 仅 leg 型；LEG_H 缩放；body_cz 随之抬升 | S_legs L46 |
| palette_style | enum | galvanized_grey / utility_green / beige_tan / weathered_white / dark_graphite / municipal_blue | galvanized_grey | choice | 仅改 material rgba，不改拓扑 | 派生（见下） |
| (—) | constraint | — | — | inequality | `DOOR_W = W - 2*DOOR_GAP - (N-1)*SEAM_GAP > 0.10`（门宽下限，违反则降 N 或回缩） | S_triple L63 |
| (—) | constraint | — | — | inequality | `louver_span = DOOR_H - 2*MARGIN ≥ louver_row_N * LOUVER_ROW_H`（行不超门高，违反则降 N） | S_louver L183-L184 |
| (—) | constraint | — | — | inequality | `support_top + BODY_H/2`：body 坐基座顶，base z=0（落地不漂浮） | 全 base 样本 |

palette_style 候选 rgba（target 6 colorways，源自样本 material 调）：
- galvanized_grey: body (0.66,0.67,0.69) door (0.72,0.73,0.75) — S_grey L76-L77
- weathered_white: body (0.82,0.81,0.78) door (0.74,0.73,0.70) — S_tall L79-L80
- utility_green: body (0.40,0.50,0.42) door (0.45,0.55,0.46) — S_legs door_paint (0.58,0.62,0.60) 系
- beige_tan: body (0.80,0.76,0.66) door (0.84,0.80,0.70)
- dark_graphite: body (0.34,0.36,0.38) door (0.40,0.42,0.44) — S_legs dark_metal 系
- municipal_blue: body (0.40,0.46,0.58) door (0.46,0.52,0.64)

## Multiplicity / Copy Logic

本类别有 **3 根独立 multiplicity 轴** + 1 根派生（卷帘 slat）：

### 轴 1：door-count N（triple_door_bank）
- `count_param`: `door_count_N`
- `N_range`: 产品域 [2,4]（N=1 退化为 single_revolute_side 单门；本轴覆盖 2/3/4 横排门）；测试偏 N=2,3
- sampling domain: 加权 — N2 高频、N3 中频、N4 稀有
- copied object: `door_{i}` part（`_build_door` helper）+ body `mullion_{i}` ×(N-1) + `hinge_{i}_{j}`
- naming: `door_{i}` / `body_to_door_{i}` / `mullion_{i}`
- placement: 规则 X 间距 `_door_hinge_x(i) = -W/2 + DOOR_GAP + i*(DOOR_W+SEAM_GAP)`，等宽
- joint policy: 各门独立 REVOLUTE 竖直 `axis=(0,0,-1)` `upper=115°`（独立开合，非 mimic）
- source/gating: S_triple L228-L251；gate `DOOR_W > 0.10`

### 轴 2：louver-row N（louver_rows / double_louver_doors）
- `count_param`: `louver_row_N`
- `N_range`: 产品域 [3,12]；测试偏 [3,8]
- sampling domain: 加权 — N4-6 高频、N8-12 稀有
- copied object: `louver_{i}`（单门）或 `{name}_louver_{i}`（每门，dbllouver）面板
- naming: `louver_{i}` / `door_{i}_louver_{j}`
- placement: 竖直规则 pitch = `(DOOR_H - 2*MARGIN)/(N-1)`，门面满堆
- joint policy: 无 joint（通风为 parent visual）
- source/gating: S_louver L180-L193 / S_dbllouver L143-L155；gate `louver_span ≥ N*LOUVER_ROW_H`

### 轴 3：leg-count N（tall_legs）
- `count_param`: `leg_N`
- `N_range`: {4,6}（4 角为主，6=长体加中腿）；测试偏 4
- sampling domain: 加权 — N4 高频、N6 稀有
- copied object: `leg_{i}` 独立 part（`_leg_visuals` helper：post + foot_pad + top_gusset）
- naming: `leg_{i}` / `cabinet_to_leg_{i}`
- placement: 角点 `(±(W/2-inset), ±(D/2-inset))`，N6 时长边加中腿
- joint policy: 各腿 FIXED，origin=corner，腿 LOCAL 顶在 body 底
- source/gating: S_legs L405-L432；four_short_legs（S_small）是同轴 LEG_H 短版（N=4 固定）

### 派生：shutter_slat_N
- `count_param`: `shutter_slat_N`（equation 派生，非独立轴）
- 函数: `= round(CURTAIN_H / SLAT_PITCH)`，随 curtain 高度
- copied object: `shutter_slat_{i}` rib loop（装饰，PRISMATIC 整体平移，slat 不独立动）
- source: S_shutter L52-L59, L240-L247

三处独立 multiplicity 各 ≥2 个 distinct N（door 2/3/4、louver 3..12、leg 4/6），满足 multiplicity 2–3 N 要求。

## 拓扑多样性审计

总组合数（受 compatibility gating 后的合法组合，非裸笛卡尔积）：

裸笛卡尔积：door(5) × body(5) × vent(5) × base(5) × roof(4) = 2500；distinct-N 三轴另乘 door-N(3) + louver-N(~10) + leg-N(2)。
仅独立两轴下限：door(5) × body(5) = 25 ≥ 10 已单独过线。

理由：Slot A 自身含 REVOLUTE-竖直立轴 / REVOLUTE-水平横轴 / PRISMATIC 三种 joint 拓扑；外加 base 的 plinth-vs-legs（FIXED-origin() vs N×FIXED-corner 子件复制）改变 part/joint 计数；triple-door 与 tall-legs 的 distinct-N 各产生不同 part 树规模。distinct topology equiv class 远超 10。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed` 对每个 seed：(1) 先按加权选 door_module；(2) 按 door_module gate 选 body_module（top_lid⟹low_ground_box）、base_module（top_lid⟹four_short_legs）、roof_module（top_lid⟹none）；(3) 选 vent_module（front-door⟹door-face vents 合法，shutter/lid⟹side/solid）；(4) 三 multiplicity 轴各做一次加权 N 抽样（小 N 偏多），各 clamp，各编入 `slot_choices`；(5) 采 width/depth/height/leg_height scale（independent，clamp [0.9,1.1]），派生 shutter_slat_N，投影 inequality（DOOR_W/louver_span 下限），违反则降 N 或回缩；(6) 选 palette_style。无小型 curated/modulo 表作主域。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别 door(5)×body(5)×base(5) 已 125 拓扑骨架，加 multiplicity N 与 roof 按 ≥300 富类别口径观察。

Controlled local parameterization：width_scale / depth_scale / height_scale / leg_height_scale（见参数表，独立 clamp [0.85–1.15]），louver pitch 与 door_W 由 N 派生。所有 scale 在 `resolve_config` clamp/派生：body 缩放后门皮/铰/vent/base footprint 随之重算（door_face_y、joint origin、support_top），不破坏 InterfaceSpec（铰边对齐）/ MatingContract（门贴前面板）/ multiplicity（间距按缩放后 W 重算）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | door 先选 → gate body/base/roof/vent → 三 N 加权 → scale clamp → palette | slot_choices_for_seed matches build choices |
| compatibility matrix | top_lid↔low_ground_box+four_legs+no_roof+(solid/side_vent)；shutter↔side_vent+head_box；door-face vent↔front-door；roof 与 top_lid 互斥 | no floating, no collision, axis correct, closed-pose seals, max N, optional child |
| controlled local variation | W/D/H/leg_height scale clamp [0.85–1.15]，门/铰/vent/base 随缩放重算 | proportions vary without breaking jamb-align, conduit overlap, joint origin, identity |
| regression overrides | none（首版无） | — |
| random sweep | seeds 0-4 → 0-19 → 0-49 初轮；0-999 成熟审计 | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A door | 5 | yes | yes | 3 种 joint 拓扑 |
| B body | 5 | yes | yes | low_ground_box conditional |
| C vent | 5 | yes | yes | door-face vs side gating |
| D base | 5 | yes | yes | plinth vs legs(N) |
| E roof | 4 (incl none) | yes | yes | none 与 top_lid 绑定 |

## Validator
- slot_choices_for_seed returns implemented module names
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos（top_lid+roof、front-door-vent on shutter、low_ground_box without top_lid 等被 gate 掉）
- optional regression overrides 为空
- controlled local scale params clamped；body 缩放不破坏铰边对齐 / conduit overlap / joint origin / multiplicity
- cross-part scale deps（DOOR_W/louver_span/support_top inequalities）resolved in `resolve_config`
- critical InterfaceSpec / MatingContract：door LOCAL ORIGIN=铰边对齐 joint origin（q=0 平贴）；base z=0；legs corner FIXED
- key joints：door REVOLUTE 竖直 `axis=(0,0,±1)` `upper≈115°`；lid REVOLUTE 水平 `axis=(-1,0,0)` `upper≈105°`；shutter PRISMATIC `axis=(0,0,1)`
- copied objects follow naming/placement：`door_{i}` / `louver_{i}` / `leg_{i}` / `shutter_slat_{i}` loop，规则间距
- final template 不循环小 curated 表

## Reject cases
- 门在 q=0 不平贴前面板（铰边 LOCAL ORIGIN 未对齐 joint origin）→ 门漂浮或穿模
- base 底不在 z=0（漂浮）或 plinth 不宽于体却断言 wider
- door REVOLUTE 轴非竖直（door 型）或 lid 轴非水平（lid 型）；shutter 用 REVOLUTE
- top_revolute_lid 同时挂 roof module（顶面冲突）或用 front-door-face louver
- triple_door_bank N 过大致 `DOOR_W ≤ 0.10`（门过窄/负宽）
- louver_row_N 过大致 louver 行溢出门高 / 行间穿模
- roller_shutter 缺 head_box/guide_rails 致 curtain retract 无处可去 / 侧面无 vent 却门面被占
- tall_legs 腿底不触地（FIXED origin 错）或腿与 body 不接（漂浮 island）
- palette_style 改了拓扑而非仅 material（应只换 rgba）
- 把 conduit 桩 / 警示牌 / 闪电符 / hasp 装饰做成独立 FIXED 轴（应为 parent visual）

## 与相邻类别的边界
- 不该混入：**fire_cabinet**（消防柜）— 重叠在「钢制带门金属柜」骨架；utility_box 靠 galv-grey/green/beige palette（非消防红）、louver/mesh 通风（非玻璃面板+卷管盘）、户外 plinth/legs + conduit 入线区分，不暴露消防内胆。
- 不该混入：**phone_box**（电话亭）— 电话亭可进入、玻璃围壁、内部话机；utility_box 不可进入、无玻璃围壁、门覆盖整面 enclosure。
- 不该混入：**mailbox**（邮箱）— 邮箱有投递 slot + 细立杆；utility_box 无投递口、门为整面服务门、基座为宽 plinth/腿。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）
- 共享 helper：`_hollow_box(open_face)` 全 module 复用（门型 `-y`，lid 型 `+z`）；`_build_door` 由 single/double/triple 共用（mirror 参数 + loop）；`_leg_visuals` 由 four_legs/tall_legs 共用。
- InterfaceSpec 重点：门 LOCAL ORIGIN=铰边须随 width_scale 后的 jamb 重算 joint origin；body_cz = support_top + BODY_H/2 随 base 与 height_scale 派生。
- allow_overlap 须按 module 局部声明：closed door/lid/shutter nests in opening（door↔body）；conduit↔shell_4（plinth↔body，cable entry，含 expect_overlap）；shutter↔body（guide channel + head_box）；多门型每门各一条 allow_overlap。
- 暂不进入 seed domain 的组合：top_revolute_lid + tall_legs（顶翻盖低地箱配高腿不符身份，gate 掉）；roller_shutter + door-face louver（互斥）。
</content>
</invoke>
