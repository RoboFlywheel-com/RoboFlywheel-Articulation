# well_lid — Modular Template Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `well_lid` |
| template path | `agent/templates/Urban_Environment_Well_lid.py` |
| test path (optional) | `tests/agent/test_well_lid_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel_children: frame→{hinge_pin, cover} + multiplicity: 盖面图案重复件 ring/spoke/stud/cell） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (1 parent + 8 single-axis converged variants from the source map) |
| source_index_policy | only adopted module sources are indexed below |

9 个 5★ 样本是 **同一拓扑等价类**（圆形铸铁井盖 = FIXED frame 环 + 圆形 cover + 真实开启关节）的不同 pattern/mechanism/frame/N 填充。它们共享一套不变的 `_build_frame_mesh()` + cover plate + pick-hole + 落座契约骨架。

- **S0 `well_lid` PARENT — waffle-grid hinged**
  (`rec_round-cast-iron-manhole-well-cover-with-a-dense-_20260608_172202_787515_e3176cb1`, model.py L1-L343)：圆铸铁井盖，方格 **waffle** 凸纹顶（凸 slab 切井字槽，L124-L151，**单 mesh 不发 cell visual**），pick-hole slot（L154-L161），后缘 **REVOLUTE** 铰（`cover_hinge` axis `(0,-1,0)` upper 1.75，L243-L253）+ FIXED `hinge_pin`（L209-L223）+ frame 环（L64-L105，凹 seat ledge + 圆 shaft void + 后缘 hinge lug）。落座契约 `allow_overlap`+`expect_contact(contact_tol=0.012)`（L306-L311），pin 被 knuckle 捕获 `expect_contact(0.006)`（L313-L319）。

- **S1 `pattern_rings`**（`rec_well_lid_var_pattern_rings`, model.py L1-L414）：同步骨架，顶面为 **同心环** 凸肋。`_build_annular_rib(inner_r,outer_r,height,name)` 共享 helper（L116-L131），`for i in range(N_RINGS=8)` loop-emit `ring_{i}` visuals（L238-L246）+ 中央 `center_hub`（L249-L261）。新增 ring 计数/同心/坐 plate 顶 asserts（L347-L390）。

- **S2 `pattern_spokes`**（`rec_well_lid_var_pattern_spokes`, model.py L1-L~330）：顶面为 **径向辐条**。`_build_radial_rib_mesh()` 梯形辐条 helper（L162-L179）+ `_build_hub_mesh()`（L182-L191）+ `_build_border_ring_mesh()`（L194-L207）；`for i in range(N_SPOKES=18)` 用 `rpy=(0,0,angle)` 角度复制 `spoke_{i}`（L285-L295），`SPOKE_ANGLE_OFFSET=pi/N` 避开 pick-hole（L56）。

- **S3 `pattern_medallion`**（`rec_well_lid_var_pattern_medallion`, model.py L1-L~340）：顶面为 **中央字母/纹章 medallion + 外圈 stud ring**。medallion boss + emblem ring + cross arms + tip dots 全部融进 cover mesh（L139-L197）；`_build_stud_mesh()` 圆顶 stud（L220-L229），`for i in range(NUM_STUDS=16)` 极坐标复制 `stud_{i}`（L289-L300）。

- **S4 `open_liftout`**（`rec_well_lid_var_open_liftout`, model.py L1-L300）：开启机构改 **+Z PRISMATIC 提起取出**。**无 hinge_pin part**（L222-L224 断言），cover 居中 `origin=(0,0,0)`（L181-L186），`cover_lift` PRISMATIC axis `(0,0,1)` lower 0 upper `LIFT_CLEARANCE`（L193-L206）；`LIFT_CLEARANCE=FRAME_H-COVER_BOTTOM_Z+COVER_T+0.020`（L58）。frame **无 hinge lug**（L61-L91）。提起后 cover 底 > frame 顶断言（L272-L294）。

- **S5 `open_pickbar`**（`rec_well_lid_var_open_pickbar`, model.py L1-L~420）：在 hinged cover 上 **再挂一个 REVOLUTE 折叠 pick-bar**（双关节链）。cover 上铸 recessed channel + 2 pivot lugs（L180-L192），`_build_pick_bar_mesh()` 撬杆（L215-L246），`cover_to_bar` REVOLUTE axis `(0,-1,0)` upper ~1.50 parent=cover（L333-L341）。cover 仍 REVOLUTE（L307-L315）。

- **S6 `cells_n`**（`rec_well_lid_var_cells_n`, model.py L1-L~390）：**waffle 多重性轴 — 更细网格**，loop-rewrite。`WAFFLE_PITCH=0.036`（比 parent 0.052 细），`Box((PAD,PAD,RELIEF))` 共享 pad helper（L161），嵌套 `for ix/for iy` 圆形裁剪发 `cell_{i}` visuals（L218-L241），`waffle_cell_count>=100` + 顺序命名 asserts（L345-L374）。

- **S7 `cells_coarse`**（`rec_well_lid_var_cells_coarse`, model.py L1-L~380）：**waffle 多重性轴 — 更粗网格**。`GRID_PITCH=0.090`（比 parent 粗），`_build_cell_pad_mesh()`（L177-L182）+ `_compute_grid_cells()` 圆裁剪四角全含（L189-L227）→ `GRID_CELLS`/`CELL_COUNT` 模块级常量（L229-L230），`for i,cx,cy in GRID_CELLS` 发 `cell_{i}`（L300-L305）。`cell_count_coarser_than_parent` 断言（L366-L369）。

- **S8 `frame_collar`**（`rec_well_lid_var_frame_collar`, model.py L1-L~340）：**frame 风格轴 — 凸起 collar 路缘**。`FRAME_H=0.280`（vs flush 0.110）+ 底 `FLANGE_OUTER_R=FRAME_OUTER_R+0.055`/`FLANGE_H=0.032` 稳定法兰（L55-L56），`_build_frame_mesh` 高 collar + flange union（L72-L120），`raised_collar_height` 断言 collar 高于普通 curb（L304-L321），cover mass 95（heavier，L219）。

共同骨架（identity 不变量）：固定圆 **frame 环**（base z≈0，footprint Ø≈0.74，含凹 seat ledge + 圆 shaft void + 黑 shaft_floor disk 读作 void）+ 一个 **圆 cover plate**（Ø≈0.61）落在 seat 上（`allow_overlap`+`expect_contact`）+ **真实开启关节**（REVOLUTE 后缘铰 / PRISMATIC +Z 提起）+ **pick-hole slot** + 盖面 **凸起（非贯穿）铸纹**。

## 核心身份

一块 **圆形铸铁井盖 / 检修盖（well / manhole cover），落座在圆形凹陷承座 frame 环里，盖下是圆形中空竖井 void**，盖面带 **致密凸起铸纹**（waffle 方格 / 同心环 / 径向辐条 / 中央 medallion+stud ring），整体齐平地面或带凸 collar 路缘，并带 **pick / pry hole** 供撬起。盖是被铰接的活动子件，**开启机构是真实非固定关节**：默认 **后缘 REVOLUTE 边缘翻转铰**（升起露出竖井），变体引入 **+Z PRISMATIC 整体提起取出**（lift-out，定义性关节），以及在 hinged cover 上 **再挂一个 REVOLUTE 折叠 pick-bar** 双关节链。frame 环与其下圆竖井保持 **FIXED**。盖面图案的重复件（环/辐条/stud/格子）是循环复制的 **multiplicity** 轴。

默认成熟域：圆形铸铁井盖，Ø≈0.55-0.70 m，落座 frame 内，REVOLUTE 后缘翻转 或 +Z PRISMATIC 提起，表面为凸起 waffle/ring/spoke/medallion 铸纹，齐平 curb 或凸 collar，带 pick-hole。

**关键 neighbor-boundary：ROUND well lid vs SQUARE Manhole_cover grate**（见 §与相邻类别的边界）。

## 槽位 + 候选模块表

四个 slot：A 表面图案 `surface_pattern`（决定 multiplicity 轴）、B 开启机构 `open_mechanism`（定义性关节）、C frame 风格 `frame_style`、D pick 取物特征 `pick_feature`。所有 candidate 共享不变的圆 cover plate + 圆 frame 环 + 圆 shaft void 骨架（来自 S0 `_build_frame_mesh` L64-L105 + cover plate L141-L177）。

### Slot A：surface_pattern（盖面凸起铸纹层；决定 multiplicity 轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `waffle_grid` | S0 / S6 / S7 | S6 L161 (`Box(PAD,PAD,RELIEF)` pad helper) + L218-L241 (嵌套 `for ix/for iy` 圆裁剪 emit `cell_{i}`) | eligible if compatible | 正方凸 pad 阵（loop-emit `cell_{i}`）；N = 圆内格子数，随 pitch 变（细 S6 / 粗 S7）；唯一 2D 嵌套复制 module |
| `concentric_rings` | S1 | S1 L116-L131 (`_build_annular_rib`) + L238-L246 (`for i in range(N_RINGS)` emit `ring_{i}`) + L249-L261 (center_hub) | eligible if compatible | 同心环肋（loop-emit `ring_{i}`）+ 中央 hub；N = 环数；1D 径向复制 |
| `radial_spokes` | S2 | S2 L162-L179 (`_build_radial_rib_mesh` 梯形辐条) + L285-L295 (`for i` `rpy=(0,0,angle)` emit `spoke_{i}`) + L182-L207 (hub+border_ring) | eligible if compatible | 径向辐条（loop-emit `spoke_{i}` 角度旋转）+ hub + border ring；N = 辐条数；1D 角向复制 |
| `medallion_studs` | S3 | S3 L139-L197 (medallion boss+emblem ring+cross arms 融进 cover mesh) + L220-L229 (`_build_stud_mesh`) + L289-L300 (`for i` 极坐标 emit `stud_{i}`) | eligible if compatible | 中央纹章 medallion + 外圈 stud ring（loop-emit `stud_{i}`）；N = stud 数；1D 角向复制 |

### Slot B：open_mechanism（开启机构 = 定义性非固定关节）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `edge_hinge` | S0 / S1 / S2 / S3 | S0 L243-L253 (`cover_hinge` REVOLUTE axis `(0,-1,0)` upper 1.75) + L209-L223 (FIXED `hinge_pin`) + L94-L103 (frame hinge lug) + L163-L179 (cover knuckles) | eligible if compatible | 后缘 REVOLUTE 翻转铰；额外 FIXED `hinge_pin` part + frame lug + cover knuckle 捕获 pin；cover plate origin = +COVER_R 前置 |
| `lift_out` | S4 | S4 L193-L206 (`cover_lift` PRISMATIC axis `(0,0,1)` upper `LIFT_CLEARANCE`) + L181-L186 (cover 居中 origin (0,0,0)) + L58 (LIFT_CLEARANCE) + L61-L91 (frame 无 lug) | eligible if compatible | +Z PRISMATIC 整体提起取出；**无 hinge_pin part**、frame **无 lug**；cover 居中坐 seat；提起后底 > frame 顶 |
| `hinge_plus_pickbar` | S5 | S5 L307-L315 (cover REVOLUTE) + L333-L341 (`cover_to_bar` REVOLUTE parent=cover axis `(0,-1,0)` upper ~1.50) + L180-L192 (channel+lugs) + L215-L246 (`_build_pick_bar_mesh`) | eligible if compatible | 双关节链：cover edge_hinge + 其上再挂一个折叠 REVOLUTE pick-bar（stowed 平躺 channel，竖起撬起）；保留 hinge_pin |

### Slot C：frame_style（frame 环外形；保持圆 seat + 圆 shaft void）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `flush_ground_ring` | S0 / S1 / S2 / S3 / S4 / S6 / S7 | S0 L64-L105 (`FRAME_H=0.110` 矮 curb 环 + 凹 seat + 圆 shaft + 顶缘 bevel) | eligible if compatible | 齐平地面矮 curb 环；base z≈0，圆 seat ledge `FRAME_INNER_R`，圆 shaft void `COLLAR_R` 下到 cast floor |
| `raised_collar` | S8 | S8 L50-L56 (`FRAME_H=0.280` 高 collar + `FLANGE_OUTER_R/FLANGE_H` 底法兰) + L72-L120 (高 collar + flange union) | eligible if compatible | 凸起 collar 路缘，远高于地面，带底稳定法兰；同样圆 seat + 圆 shaft void；cover mass 加大 |

### Slot D：pick_feature（取物 / 撬起特征；module-local，folded into cover）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `single_pick_slot` | S0 / S1 / S2 / S3 / S4 / S6 / S7 / S8 | S0 L154-L161 (`slot2D(0.060,0.024)` 前缘撬槽切入 cover) | eligible if compatible | 单条前缘 pick / pry slot 切口（cut into cover mesh）；所有 hinged/lift-out 默认 |
| `twin_pick_slots` | S4（pick-hole 复用→镜像） | S4 L94-L99 (cover mesh 头) + S0 L154-L161 (slot2D 复用，镜像 ±X 两条) | eligible if compatible | 对称两条撬槽（前后缘各一），适配 lift_out（两侧对称提起）；纯 cut，N 固定 2 |

**降级说明**：所有 slot 均有 ≥2 个结构不同 candidate，无单 candidate slot。Slot D 是 cover-local cut feature（不引入独立 part），但仍切换 part-tree 内 mesh 拓扑（撬槽数），故记为 slot；若审核认为应折入 cover module，可降为 cover-local fixed structure（`twin_pick_slots` 仅当 `lift_out` 时启用，见 compatibility matrix）。

## 槽位图（slot graph）

pattern: `mixed`（parallel_children + multiplicity）

```
frame (ROOT, FIXED, Slot C frame_style)
  │
  ├─[FIXED @ rear hinge axis (HINGE_X,0,HINGE_Z)]──> hinge_pin   (仅 edge_hinge / hinge_plus_pickbar)
  │
  └─[OPEN JOINT = Slot B 定义性关节]──> cover (圆盘 + Slot A surface_pattern multiplicity + Slot D pick_feature)
            │  edge_hinge:  REVOLUTE  axis(0,-1,0)  origin(HINGE_X,0,HINGE_Z)   upper≈1.75
            │  lift_out:    PRISMATIC axis(0,0,1)   origin(0,0,COVER_BOTTOM_Z)  upper=LIFT_CLEARANCE
            │  hinge_plus_pickbar: cover REVOLUTE(如上) 且
            │
            └─[REVOLUTE @ pivot lugs，仅 hinge_plus_pickbar]──> pick_bar  axis(0,-1,0) upper≈1.50
```

接口点位：

- **frame → cover（OPEN JOINT，定义性）**：
  - `edge_hinge` / `hinge_plus_pickbar`：mating = 后缘 barrel hinge；pivot 在 `Origin(xyz=(HINGE_X,0,HINGE_Z))`，`HINGE_X=-COVER_R-0.004`，`HINGE_Z=COVER_BOTTOM_Z+COVER_T*0.5`（S0 L60-L61）；axis `(0,-1,0)`；cover plate visual origin 前置 `(+COVER_R+0.004,0,-COVER_T/2)`（S0 L231-L236）使 plate 充满开口。
  - `lift_out`：mating = seat ledge contact plane；joint origin `Origin(xyz=(0,0,COVER_BOTTOM_Z))`，axis `(0,0,1)`，cover plate 居中 origin `(0,0,0)`（S4 L181-L206）。
- **cover seat 落座**：cover 底 z = `COVER_BOTTOM_Z = SEAT_Z = FRAME_H-SEAT_DROP`，落在 frame 凹 seat ledge（`FRAME_INNER_R = COVER_R+0.006`）；`allow_overlap`+`expect_contact(0.012)`（S0 L306-L311）。
- **frame → hinge_pin（FIXED）**：仅 hinge 机构存在；pin 在同一 hinge origin，被 cover knuckle 捕获（`allow_overlap`+`expect_contact(0.006)`，S0 L313-L319）。
- **cover → pick_bar（REVOLUTE，仅 hinge_plus_pickbar）**：pivot 在 cover-part 坐标 `(COVER_R+0.004+PIVOT_X_MESH,0,-COVER_T/2+PIVOT_Z_MESH)`（S5 L331-L341），axis `(0,-1,0)`，bar stowed 平躺 channel。
- **surface_pattern → cover plate（part-local visuals）**：所有 `ring_{i}`/`spoke_{i}`/`stud_{i}`/`cell_{i}` visual origin 坐 plate 顶面 `z = top_center_z`（S1 L237 / S2 L266-L267 / S3 L294 / S6 L236），无独立 joint（凸纹是 parent visual on the cover part）。

互斥 / 派生约束：

- `lift_out` 时 **无 hinge_pin part**、frame **无 hinge lug**，cover plate 居中（origin 切换）。
- `edge_hinge` / `hinge_plus_pickbar` 时 cover plate 前置（origin = +COVER_R），含 hinge_pin + lug + knuckle。
- `hinge_plus_pickbar` 仅在 cover 已是 REVOLUTE 时挂 pick_bar（不与 lift_out 组合）。
- `twin_pick_slots` 仅当 `lift_out`（对称两侧撬起合理）；hinged 机构用 `single_pick_slot`（前缘撬槽，pick_bar 占用前部 channel 时 pick slot 改为非冲突位）。

## 每槽位 Module Emits / Interfaces

### Slot A / module waffle_grid
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`cell_{i}` 凸 pad visuals 挂 cover part | S6 L218-L241 |
| internal joints | 无（凸纹是 cover parent visual） | — |
| upstream interface | pad 底坐 plate 顶 `z=COVER_T*0.5+RELIEF/2`，圆内裁剪（`math.hypot<grid_r`） | S6 L229-L239 |
| downstream interface | 决定 N（圆内格子数）；naming `cell_{i}` 顺序 | S6 L223-L241 |

### Slot A / module concentric_rings
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`ring_{i}` annular rib + `center_hub` visuals 挂 cover | S1 L238-L261 |
| internal joints | 无 | — |
| upstream interface | rib 坐 plate 顶 `ring_origin=(COVER_R+0.004,0,COVER_T*0.5)`；`inner_r=HUB_R+GROOVE+i*RING_STEP` | S1 L237-L246 |
| downstream interface | N=N_RINGS；最外环 within plate、hub within ring_0 asserts | S1 L362-L379 |

### Slot A / module radial_spokes
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`spoke_{i}` 梯形肋 + hub + border_ring visuals | S2 L270-L295 |
| internal joints | 无 | — |
| upstream interface | spoke 坐 `top_center`，`rpy=(0,0,SPOKE_ANGLE_OFFSET+i*step)` 角度复制 | S2 L285-L295 |
| downstream interface | N=N_SPOKES；ANGLE_OFFSET=pi/N 避开前缘 pick-hole | S2 L56,L288 |

### Slot A / module medallion_studs
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；medallion+emblem 融进 cover mesh，`stud_{i}` 圆顶 stud visuals | S3 L139-L197,L289-L300 |
| internal joints | 无 | — |
| upstream interface | stud 极坐标 `(COVER_R+0.004+R*cosθ, R*sinθ, COVER_T*0.5)` | S3 L291-L300 |
| downstream interface | N=NUM_STUDS（外圈）；medallion 固定 cosmetic | S3 L289-L300 |

### Slot B / module edge_hinge
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cover`（REVOLUTE child）+ `hinge_pin`（FIXED child） | S0 L209-L253 |
| internal joints | `cover_hinge` REVOLUTE axis(0,-1,0) lower 0 upper 1.75；`frame_to_pin` FIXED | S0 L217-L253 |
| upstream interface | frame 后缘 lug + hinge origin (HINGE_X,0,HINGE_Z) | S0 L94-L103,L222 |
| downstream interface | cover knuckle 捕获 pin（allow_overlap+contact 0.006） | S0 L163-L179,L313-L319 |

### Slot B / module lift_out
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cover`（PRISMATIC child）；**无 hinge_pin** | S4 L181-L206,L222-L224 |
| internal joints | `cover_lift` PRISMATIC axis(0,0,1) lower 0 upper LIFT_CLEARANCE | S4 L193-L206 |
| upstream interface | seat ledge 接触面；joint origin (0,0,COVER_BOTTOM_Z)，frame 无 lug | S4 L61-L91,L198 |
| downstream interface | 提起后 cover 底 z > FRAME_H（露竖井）；XY 不漂移 | S4 L272-L294 |

### Slot B / module hinge_plus_pickbar
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cover`(REVOLUTE) + `hinge_pin`(FIXED) + `pick_bar`(REVOLUTE child of cover) | S5 L294-L341 |
| internal joints | `cover_hinge` REVOLUTE + `cover_to_bar` REVOLUTE axis(0,-1,0) upper~1.50 | S5 L307-L341 |
| upstream interface | cover 上铸 channel + 2 pivot lugs；pivot 在 cover 坐标 | S5 L180-L192,L331 |
| downstream interface | bar stowed 平躺 channel，竖起姿态供撬起 | S5 L215-L246 |

### Slot C / module flush_ground_ring
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`(ROOT) + shaft_floor void disk visual | S0 L64-L105,L192-L201 |
| internal joints | 无（FIXED root） | — |
| upstream interface | base z≈0 坐地；圆 seat ledge FRAME_INNER_R；顶缘 bevel | S0 L67-L99 |
| downstream interface | seat ledge 承 cover；shaft void COLLAR_R 读作 void | S0 L84-L90 |

### Slot C / module raised_collar
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`(ROOT, 高 collar + 底法兰) + shaft_floor | S8 L72-L120 |
| internal joints | 无 | — |
| upstream interface | flange base z≈0；FRAME_H=0.280 高 collar；同圆 seat | S8 L50-L120 |
| downstream interface | seat ledge 承 cover（同 flush）；collar 高于地面断言 | S8 L304-L321 |

### Slot D / module single_pick_slot
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（cover mesh cut） | S0 L154-L161 |
| internal joints | 无 | — |
| upstream interface | slot2D(0.060,0.024) 切前缘 cover plate | S0 L154-L161 |
| downstream interface | 视觉撬起锚点；不冲突 surface_pattern 中心 | S0 L154-L161 |

### Slot D / module twin_pick_slots
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（cover mesh cut ×2 镜像） | S0 L154-L161（镜像复用） |
| internal joints | 无 | — |
| upstream interface | 前后缘各一 slot2D（±X 镜像）；仅 lift_out 启用 | S4 L94-L99 + S0 L154-L161 |
| downstream interface | 对称提起锚点 | S0 L154-L161 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `surface_pattern` | enum | waffle_grid / concentric_rings / radial_spokes / medallion_studs | — | choice | deterministic procedural sampler | Slot A 表 |
| `open_mechanism` | enum | edge_hinge / lift_out / hinge_plus_pickbar | — | choice | sampler；hinge_plus_pickbar 仅与 hinged base | Slot B 表 |
| `frame_style` | enum | flush_ground_ring / raised_collar | — | choice | sampler | Slot C 表 |
| `pick_feature` | enum | single_pick_slot / twin_pick_slots | — | conditional | twin 仅当 lift_out；否则 single | Slot D 表 |
| `palette_style` | enum | cast_iron_black / weathered_rust / painted_green / municipal_grey / oxidized_bronze / fresh_charcoal | cast_iron_black | choice | sampler；仅改 material rgba 不改拓扑 | S0 L187-L190 (material 基线) |
| `cover_dia` | float | [0.55, 0.70] m | 0.610 | independent | 范围内均匀采样后 clamp；驱动所有派生半径 | S0 L40-L41 |
| `cover_t` | float | [0.034, 0.050] m | 0.042 | independent | clamp | S0 L43 |
| `frame_outer_r` | float | derived | 0.370 | equation | `= cover_r + 0.065`（curb 壁厚保形） | S0 L47 |
| `frame_inner_r` | float | derived | — | equation | `= cover_r + 0.006`（落座间隙） | S0 L46 |
| `collar_r` | float | derived | — | equation | `= cover_r - 0.030`（shaft 壁） | S0 L49 |
| `frame_h` | float | conditional | 0.110 / 0.280 | conditional | flush→[0.090,0.130]；raised_collar→[0.22,0.32] | S0 L48 / S8 L50 |
| `pattern_count` (N) | int | 见 §Multiplicity | per-module | conditional | N_range 按 surface_pattern 轴定；圆内裁剪 | §Multiplicity |
| `relief_height` | float | [0.007, 0.013] m | 0.010 | independent | clamp；凸纹高（非贯穿，远小于 cover_t） | S0 L44 |
| `hinge_upper` | float | [1.4, 1.9] rad | 1.75 | independent | clamp；REVOLUTE 开角 | S0 L252 |
| (—) | constraint | — | — | inequality | `relief_height ≤ cover_t*0.40`（凸纹不穿盖、非 through-hole）；违反则回缩 relief_height | identity（well_lid 非 grate） |
| (—) | constraint | — | — | inequality | `lift_clearance = frame_h - cover_bottom_z + cover_t + 0.020`（提起必须清 frame 顶）；lift_out 派生 | S4 L58 |
| (—) | constraint | — | — | inequality | pattern 最外 element radius `≤ cover_r - border_inset(≈0.018-0.028)`（凸纹不越盖缘） | S1 L69 / S2 L51 |
| (—) | constraint | — | — | inequality | pick_slot 不与 surface_pattern 中心 / pick_bar channel 冲突（前缘留空 border） | S2 L56 (ANGLE_OFFSET) |

连续尺寸采样契约：先采 `cover_dia`/`cover_t`/`relief_height`/`hinge_upper`（independent）→ 派生 `frame_outer_r`/`frame_inner_r`/`collar_r`/`lift_clearance`（equation）→ `frame_h` 按 frame_style conditional 解析 → inequality 把 relief、pattern radius、pick clearance 投影/回缩到可行域。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（`pattern_count` N），其语义/范围/placement **随所选 `surface_pattern` module 切换**（conditional N_range，按轴按 module 定）：

- `count_param`：`pattern_count`（下游编进 `slot_choices`，因为它改变拓扑等价类 = 不同重复件数）。
- `copied object` / `naming` / `placement` / `joint policy`（统一：无 joint，凸纹是 cover parent visual）：

| surface_pattern | copied object | naming | placement | N_range (product domain) | sampling domain (权重) |
|---|---|---|---|---|---|
| waffle_grid | 方 pad `Box(PAD,PAD,RELIEF)` | `cell_{i}` | 2D 正方网格，圆内裁剪（4 角全含） | N∈[~12, ~180]（pitch 0.090→粗~12 / 0.036→细~180） | 小 N（粗格 pitch 大）偏多，细格尾部稀有 |
| concentric_rings | annular rib | `ring_{i}` | 1D 径向 `inner_r=HUB_R+GROOVE+i*RING_STEP` | N∈[4, 14] | 中 N（6-9）偏多 |
| radial_spokes | 梯形辐条肋 | `spoke_{i}` | 1D 角向 `angle=OFFSET+i*2π/N` | N∈[8, 36] | 中 N（12-20）偏多 |
| medallion_studs | 圆顶 stud | `stud_{i}` | 1D 角向极坐标外圈 | N∈[8, 32] | 中 N（12-20）偏多 |

- source/gating：每个 module 圆内/盖缘裁剪（inequality：pattern radius ≤ cover_r - border）。N 上限受 cover_r 与 pad/rib pitch 几何约束；sweep 对每 module 各设 N 上限（waffle 网格防 mesh 爆量：sweep 上限 ~120 cell，product 域可到 ~180 但稀有采样）。
- 测试偏小 N（粗格 / 少环辐），产品全程；下游对此轴做一次加权采样、clamp、sweep 设上限。

（注：跨 module N 共享采样 helper 待第二个 multiplicity 模板出现再抽，不提前抽象。）

## 拓扑多样性审计

总组合数（不含连续 scale，含 N 采样数量）：

```
surface_pattern(4) × open_mechanism(3) × frame_style(2) × pick_feature(conditional≈1.x)
  基础 = 4 × 3 × 2 = 24
  × distinct-N（每 module 至少 3 档可分辨 N，跨 4 module ≈ 8-12 distinct N 拓扑）
  ⇒ 按 ≥300 富类别口径观察 slot choice tuple distinct
```

理由：仅 surface_pattern × open_mechanism × frame_style = 24 已 > 10；叠加每 module N 复制使 1000-seed slot choice tuple distinct 轻松 按 ≥300 report-only 口径观察。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed` 用 deterministic procedural sampling 依序选 surface_pattern → open_mechanism → frame_style → pick_feature（conditional gate）→ pattern_count（按所选 module 加权采样）→ palette_style → 连续 scale（按采样契约 independent→equation→conditional→inequality）。compatibility matrix 排除非法组合（见下）。无需 curated/modulo 主表；少量 regression overrides 仅用于已知失败 seed。Random sweep：seeds 0-49 初轮，0-999 成熟审计；viewer 目检圆形身份、落座、开启语义、凸纹（非贯穿）。Topology target：1000-seed distinct ≥ 100（24 module 组合 × 多 N 档，远超）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：`cover_dia`[0.55,0.70]、`cover_t`[0.034,0.050]、`relief_height`[0.007,0.013]、`hinge_upper`[1.4,1.9]、`frame_h`(conditional)、`pattern_count`(conditional N)。`frame_outer_r/inner_r/collar_r/lift_clearance` 为 equation 派生。所有 scale 在 `resolve_config` clamp/派生/投影，不破坏 seat 落座、shaft 比例、joint origin、圆形 identity。inequality（relief≤0.40·cover_t、pattern radius≤cover_r-border、lift_clearance 清 frame 顶）显式声明，不当独立自由变量。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 A→B→C→D→N→palette→scale；加权 choices；conditional gate | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | lift_out ⇒ 无 hinge_pin/lug + cover 居中 + 允许 twin_pick；hinge_plus_pickbar ⇒ 必须 hinged base；raised_collar 与任意机构兼容；pattern radius ≤ cover_r-border | 无漂浮 / 穿模 / 错轴 / 提起不清竖井 / N 爆量 / pick 冲突 |
| controlled local variation | 上述 6 个 scale + clamp/derive；relief 非贯穿 | 比例变化不破坏 seat 接触、shaft、joint origin、圆 identity |
| regression overrides | none（除非 sweep 暴露具体失败 seed） | 仅已知失败回归 |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | 与 contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A surface_pattern | 4 | yes | yes | 决定 multiplicity 轴 |
| B open_mechanism | 3 | yes | yes | 定义性关节（REVOLUTE / PRISMATIC / 双关节） |
| C frame_style | 2 | yes | no | flush vs raised collar；样本仅 2 风格 |
| D pick_feature | 2 | yes | no | cover-local cut；conditional gate |

## Validator

- slot_choices_for_seed 返回已实现 module 名（surface_pattern / open_mechanism / frame_style / pick_feature + pattern_count）
- config_from_seed 对普通 seed 用 deterministic procedural sampling；seed=0 不特殊
- compatibility matrix 阻止非法组合：lift_out+hinge_pin、hinge_plus_pickbar+lift_out base、pattern radius 越缘、N 超几何上限
- regression overrides 稀少且有据
- 不无限轮换小型 curated 表
- 受控 scale clamp/派生，不破坏 seat 接触 / shaft 比例 / joint origin / 圆 identity / multiplicity
- 跨部件 scale 依赖（equation/inequality/conditional）在 resolve_config 求解
- 关键 InterfaceSpec/MatingContract：cover 落座 seat ledge（allow_overlap+expect_contact）、hinge_pin 被 knuckle 捕获、lift_out 提起清 frame 顶
- 关键 joint 类型/轴/range：edge_hinge REVOLUTE axis(0,-1,0) upper≈1.75；lift_out PRISMATIC axis(0,0,1) upper=lift_clearance；pick_bar REVOLUTE axis(0,-1,0)
- 复制件 `ring_{i}`/`spoke_{i}`/`stud_{i}`/`cell_{i}` 顺序命名 + 圆内 placement

## Reject cases

- 圆 cover 变方形 / 矩形 grate 或盖面切 **贯穿 through-slot**（侵入 Manhole_cover 身份）。
- open_mechanism 退化为 FIXED（无真实非固定关节）。
- lift_out 仍保留 hinge_pin/lug，或提起后 cover 底未清 frame 顶（未露竖井）。
- 凸纹高 `relief_height > 0.40·cover_t` 穿透盖板，或 pattern 越过盖缘悬空。
- cover 未落座 seat ledge（无 contact / 漂浮 / 穿入 shaft）。
- 仅改 palette/material/纯尺寸冒充新拓扑（无 slot/N 变化）。
- N 超几何上限致 mesh 爆量 SIGKILL（waffle 细格未设 sweep 上限）。
- hinge_plus_pickbar 与 lift_out base 组合（pick_bar 无 hinged cover 可挂）。

## 与相邻类别的边界

- **不该混入：Manhole_cover（方形排水栅 / 检修盖）**（理由：那是 **SQUARE / rectangular** outline、盖面 **贯穿 through-slot 栅条 / 防滑菱形 stud 网格**、默认 **+Z PRISMATIC 提起**。well_lid 是 **ROUND** 盖 + 圆 frame 环、盖面 **凸起非贯穿铸纹**（waffle/ring/spoke/medallion）、默认 **后缘 REVOLUTE 翻转铰**。圆 vs 方 + 凸纹 vs 贯穿 + REVOLUTE-default vs PRISMATIC-default 是硬边界）。
- **不该混入：墙面/地面 grille / register / floor drain channel**（理由：那些是无 frame+shaft 骨架的薄栅板或长条 trench；well_lid 必须有圆 frame 承座 + 圆竖井 void + 落座契约）。
- **不该混入：井盖以外的 round hatch / porthole / 罐口盖**（理由：well_lid 是地面齐平市政井盖，base z≈0 坐地、整体齐平，非容器/船体上的开口盖）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 共享 helper：所有 module 共用 `_build_frame_mesh`（按 frame_style 切 flush/collar）+ cover plate（按 open_mechanism 切 origin 前置/居中）+ `single/twin_pick_slot` cut。
- surface_pattern 各自 helper：`_build_annular_rib`(rings) / `_build_radial_rib_mesh`+hub+border(spokes) / `_build_stud_mesh`+medallion(studs) / pad `Box`(waffle)。
- 关键 captured-pin overlap 需 element-scoped allow_overlap：cover↔hinge_pin（knuckle 捕获）、cover↔frame（seat 落座）。
- 关键 InterfaceSpec/MatingContract：hinge origin (HINGE_X,0,HINGE_Z) 与 cover plate 前置 origin 必须一致（hinged）；lift_out 时 cover 居中 + frame 无 lug 同步切换。
- 暂不进入 seed domain 的组合：hinge_plus_pickbar × lift_out（互斥，gate 排除）。
- mesh 性能：waffle 细格 N 大时 cell visual 量大，sweep N 上限 ~120，pad 用简单 Box（非 loft）控顶点。
