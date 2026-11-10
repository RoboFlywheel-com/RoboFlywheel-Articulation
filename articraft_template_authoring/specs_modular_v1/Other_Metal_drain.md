# metal_drain (square/round/hex stainless-steel bathroom floor drain) — Modular Spec

> 来源小类：`picture/Other/Metal drain`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Other__Metal_drain.md`。
> **"Metal drain" 在此 = 浴室不锈钢地漏（bathroom floor drain）：扁平抛光外法兰 + 浅锥形排水杯 + 圆形开口内坐一只可拆穿孔篦子，篦子有动作机构。** 不是水槽下水器（sink strainer basket）、不是排水沟盖板（linear shower channel）、也不是排气格栅 / 风扇。
>
> **同步状态**：source map 命名的 parent（`rec_model-a-square-stainless-steel-bathroom-floor-dr_…`）**未同步进本仓库 `data/records/`**（见 §排除项）。本 spec 锚定的是 6 个已同步、rating=5、确属 metal drain 的 fork 槽位变体；行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号、已逐一 AST/人工核对。引用以 helper / part / joint **名字**为准（`_flange_solid` / `_cup_solid` / `_liner_solid` / `_rim_solid` / `_grate_solid` / `_slot_specs` / `_ring_specs` / `_grid_hole_positions` / `body_to_grate_rim` / `rim_to_grate` / `body_to_grate` / `grate_to_plug` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `metal_drain` |
| template path | `agent/templates/Other_Metal_drain.py` |
| test path (optional) | `tests/agent/test_metal_drain_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: flange_shape + grate_pattern + grate_mechanism，**外加** `perf_count` 篦子穿孔单元多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6（source map 命名 parent 未同步；6 个 fork 槽位变体已同步且均 rating=5、compile success、≥1 非 fixed joint、workbench-only）|
| read_count | 6（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests）|
| read_scope | all genuine 5-star metal-drain samples currently synced in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；2 个污染样本已排除（见 §排除项），不进 source 表 |

阅读要点（用于槽位分解）：
- **6 个变体共享同一基线身份与基线建模骨架**：root `drain_body`（`_flange_solid` 抛光外法兰 + `_cup_solid` 锥形开底排水杯 + `_liner_solid` 暗腔衬里），法兰中心圆开口（`HOLE_R≈0.0476`）坐一只圆篦盘（`_grate_solid`）。所有变体的 body/cup/liner helper 行结构相同，TOTAL_H=0.030、FLANGE_T=0.005、HOLE_R=0.0476、GRATE_R=0.0415、GRATE_T=0.004 等常量一致 → 基线骨架高度收敛。
- **flange_shape 轴（Slot A）**：法兰 / 杯 / 衬里**同一组 mesh 的足迹形态**（square / round / hex），由 footprint-aware mesh helper 一次决定。round 用 `cylinder`+`_tapered_round_tube`；hex 用 `polygon(6,…)`+`_tapered_hex_tube`；square 用 `box`+`_tapered_square_tube`。**part 树 / joint 拓扑完全不变**——footprint 是 mesh-helper 维度，不改拓扑、不贡献额外 joint。圆篦开口 / 篦盘 / 机构在三种足迹下一致。
- **grate_pattern 轴（Slot B）**：篦盘 `_grate_solid()` 内部的穿孔图样（pinwheel_slots / concentric_rings / square_grid_holes），通过不同 helper 循环（`_slot_specs` 四象限风车槽 / `_ring_specs`+`_bridge_bar` 同心环+辐条 / `_grid_hole_positions` 方格圆孔阵）切 `disc`。**篦盘是一个 part、无独立 joint**——pattern 只换 `_grate_solid` 内的 cut 循环，不改 part 树 / joint 拓扑。pattern 内含连续多重性（slots/rings/holes 数）→ 见 Slot D。
- **grate_mechanism 轴（Slot C，主机构槽）**：这是**唯一真正改 part 树 / joint 拓扑**的轴。
  - `twist_lock_lift_out`：`drain_body`→`grate_rim` **PRISMATIC**(+Z, 提起) + `grate_rim`→`grate` **REVOLUTE**(Z, 拧锁)。3 part，链深 2，2 个非 fixed joint。
  - `hinged_flip_grate`：seat ring 并入 `drain_body`（固定，`seat_ring` 改 body visual），单 `drain_body`→`grate` **REVOLUTE**(水平 X 轴，0..2.0 rad 翻起)，body 上加 `hinge_bracket` ear。2 part，链深 1，1 个非 fixed joint。
  - `popup_center_plug`：保留完整 twist+lift 基线（body→rim PRISMATIC + rim→grate REVOLUTE），**额外**加 `center_plug` part 与 `grate`→`center_plug` **PRISMATIC**(+Z, 8mm pop-up)；篦盘中心钻 `PLUG_BORE_R` 孔。4 part，链深 3，3 个非 fixed joint。
- **perf_count 轴（Slot D 多重性）**：篦盘穿孔单元的循环复制数——pinwheel 的 `N_GROUPS×SLOTS_PER_GROUP`、concentric 的 `N_RINGS`、grid 的 `_grid_hole_positions` 网格点数。穿孔是篦盘 **cut**（非移动件，无独立 joint，随篦盘动）。

## 核心身份

一只**浴室不锈钢地漏**（bathroom floor drain）：扁平抛光金属**外法兰**（square `box` / round `cylinder` / hex `polygon(6)`，~0.12 m 足迹、~0.005 m 厚、上缘倒角），坐在一只浅的**开底锥形排水杯**（`_cup_solid`，内有 inward seat plate + 圆 throat）上，杯内有暗色**腔衬里**（`cavity_liner`，从篦缝透出黑）。法兰中心圆开口（~0.095 m）内坐一只圆**篦盘**（`grate_disc`），盘面有**穿孔图样**（风车槽 / 同心环 / 方格圆孔阵）。活动语义 = **篦子机构动作**：twist-lock（PRISMATIC 提起 + REVOLUTE 拧锁，可整体取出清理）/ hinged-flip（单边 REVOLUTE 翻起）/ pop-up center plug（在 twist+lift 基础上加中心塞 PRISMATIC 升降启闭）。默认坐地于杯底（z=0），法兰顶在 z≈0.030。默认成熟域：flange_shape × grate_pattern × grate_mechanism × 穿孔单元数 N 的小型嵌入式地漏。

不该混入：
- **排水沟盖板 / 长条淋浴地漏（linear shower channel drain）**——长条形 + 长条篦，twist-lock 不适用，flange+grate 双轴耦合（见 §排除项，留作 compatibility matrix 素材，不纳单轴格子）。
- **水槽下水提篮 / 滤篮（sink strainer / basket waste）**——深篮 + 提篮提手 + 螺纹下水，不是扁平法兰地漏。
- **排气格栅 / 通风扇 / 风扇面板（wall vent / extractor fan）**——虽同为圆法兰穿孔盘，但有叶片 / 电机 / 进风导流，主功能是通风非排水（污染样本 `rec_model-a-round-flange-mounted-wall-vent-fan` 即此类，已排除）。

## 槽位 + 候选模块表

> **建模注记**：`flange_shape`（Slot A）是 body/cup/liner **同一组 mesh 的足迹形态**，由 footprint-aware mesh helper 一次决定，不是独立串联 slot、不贡献额外 joint。`grate_pattern`（Slot B）是篦盘 `_grate_solid` 内的 **cut 图样**，篦盘仍是一个 part、无独立 joint，pattern 不改 part 树 / joint 拓扑。两者列为候选轴以对齐 schema，与 grate_mechanism / N 的笛卡尔积共同撑开多样性（见 §9）。**`grate_mechanism`（Slot C）是唯一改 part 树 / joint 拓扑的主机构轴。**
>
> **基线归属注记**：source map 的 square parent 未同步，故本 spec 的 square footprint、pinwheel pattern、twist_lock 机构三条基线均**从已同步的 fork 变体回溯**：square footprint / pinwheel / twist_lock 由 `concentric_rings`、`hinged_flip`、`popup` 三个 square-body 变体共同携带（它们的 `_flange_solid` 用 `box(FLANGE_SIDE,…)`、`_slot_specs` 风车槽、twist+lift articulation 与 source map 描述的 parent 基线一致）；round / hex footprint 由对应 flange 变体携带。每条基线均有真实 `model.py:Lx-Ly`，无单一 anchor 依赖。

### Slot A：flange_shape（外法兰 / 杯 / 衬里共享的 mesh 足迹）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| square（基线） | rec_…concentric-rings…d68de668（square-body 变体携带 square 基线）| `_tapered_square_tube` L117-148 / `_flange_solid` `box` L151-167 / `_cup_solid` L170-185 / `_liner_solid` L188-197 | eligible if compatible | 方形法兰（`box(FLANGE_SIDE,FLANGE_SIDE,FLANGE_T)`）+ 锥形方杯（`rect` loft）+ 方腔衬里；X≈Y 方足迹基线 |
| round_circular | rec_…flange-shape-round-circular…b8d32e6f | `_tapered_round_tube` L99-130 / `_flange_solid` `cylinder` L133-149 / `_cup_solid` L152-167 / `_liner_solid` L170-179 | eligible if compatible | 圆形法兰（`cylinder(FLANGE_T,FLANGE_R)`）+ 锥形圆杯（`circle` loft）+ 圆腔衬里；圆对称足迹，part 树 / joint 与 square 一致 |
| hexagonal | rec_…flange-shape-hexagonal…4b1ebd24 | `_hex_circum_d` L103-105 / `_tapered_hex_tube` L108-139 / `_flange_solid` `polygon(6)` L142-159 / `_cup_solid` L162-178 / `_liner_solid` L181-190 | eligible if compatible | 六边形法兰（`polygon(6,HEX_CIRCUM_D).extrude`）+ 锥形六角杯（`polygon(6)` loft）+ 六角腔衬里；flat-to-flat 0.12 / point-to-point 0.139，part 树 / joint 不变 |

### Slot B：grate_pattern（篦盘穿孔图样——篦盘 `_grate_solid` 内的 cut 循环，无独立 joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| pinwheel_slots（基线） | rec_…hinged-flip…3cfbbefa / rec_…flange-shape-round…b8d32e6f（携带 pinwheel 基线）| `_slot_specs` L98-110（hinged）/ `_grate_solid` 四象限风车循环 L268-313（hinged）；round 变体同图样 `_slot_specs` L83-96 / `_grate_solid` L208-231 | eligible if compatible | 四象限风车槽：`for group in range(N_GROUPS): for y,x in _slot_specs()` 双层循环切平行矩形槽，每组旋转 90°（windmill motif）|
| concentric_rings | rec_…grate-pattern-concentric-rings…d68de668 | `_ring_specs` L89-96 / `_ring_slot` L99-114 / `_bridge_bar` L226-238 / `_grate_solid` 环槽+辐条 L241-265 | eligible if compatible | 同心环槽：`for i in range(N_RINGS)` 切环形 annular 缝（`_ring_slot` 外减内），外加 `N_BRIDGES=4` 根 `_bridge_bar` 辐条桥接结构连通 |
| square_grid_holes | rec_…grate-pattern-square-grid-holes…e214b2de | `_grid_hole_positions` L79-96 / `_grid_hole_cutter` L208-(disc) / `_grate_solid` 网格圆孔 L217-232 | eligible if compatible | 方格圆孔阵：`for row: for col:` 嵌套循环生成网格点，裁到圆形 field（`hypot(x,y)≤max_r`），每点切一圆孔 |

### Slot C：grate_mechanism（**主机构槽**——决定篦子动作的 part 树与 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| twist_lock_lift_out（基线） | rec_…flange-shape-round…b8d32e6f / rec_…concentric-rings…d68de668（携带 twist+lift 基线）| round: `body_to_grate_rim` PRISMATIC L273-281 + `rim_to_grate` REVOLUTE L285-295；concentric: 同机构 L307-329 | eligible if compatible | 3 part（`drain_body`/`grate_rim`/`grate`），链深 2：`body→grate_rim` **PRISMATIC** axis=(0,0,1) 提起（0..0.03）+ `grate_rim→grate` **REVOLUTE** axis=(0,0,1) 拧锁（±90°）；篦盘坐 `grate_rim` 内 lip |
| hinged_flip_grate | rec_…grate-mechanism-hinged-flip…3cfbbefa | `_hinge_bracket_solid` L219-(end) / `body_to_grate` REVOLUTE L359-369 / seat ring 并入 body L338-347 | eligible if compatible | 2 part（`drain_body`/`grate`），链深 1：seat ring 固定为 body visual（`seat_ring`），body 加 `hinge_bracket` ear；单 `body→grate` **REVOLUTE** axis=(1,0,0) 水平翻起（0..2.0 rad），q=0 闭合盖住开口 |
| popup_center_plug | rec_…grate-mechanism-popup-center-plug…a0a6918d | `_plug_solid` L249-(end) / `body_to_grate_rim` PRISMATIC L306-313 + `rim_to_grate` REVOLUTE L318-329 + `grate_to_plug` PRISMATIC L339-349 / 篦盘钻 bore L243 | eligible if compatible | 4 part（+`center_plug`），链深 3：保留完整 twist+lift 基线 + `grate→center_plug` **PRISMATIC** axis=(0,0,1) 中心塞升降（0..0.008）；篦盘中心 `PLUG_BORE_R` 孔供塞杆穿过 |

## 槽位图（slot graph）

pattern: mixed（固定 named slots: flange_shape（mesh 维度）+ grate_pattern（篦盘 cut 维度）+ grate_mechanism（主机构，决定 part 树）；外加 `perf_count` 在篦盘内 N 次复制穿孔单元 cut）

```
drain_body (root, 坐地 z=0; 由 flange_shape 决定 flange/cup/liner mesh 足迹 + 法兰圆开口 + seat plate)
  │  └─ visual: flange_plate / drain_cup / cavity_liner（暗腔）
  │
  └── [grate_mechanism slot]  (互斥三选一，决定篦子机构 part 树)
        │
        ├─ twist_lock_lift_out :
        │     grate_rim ──[body_to_grate_rim: PRISMATIC axis=+Z, origin=(0,0,RIM_REST_Z) seat 面] (提起 0..0.03)
        │       └─ grate ──[rim_to_grate: REVOLUTE axis=+Z, origin=(0,0,DISC_LOCAL_Z) 盘心] (拧锁 ±90°)
        │            └─ grate_disc visual 由 [grate_pattern slot] 切孔 ×[perf_count N]
        │
        ├─ hinged_flip_grate :
        │     (seat_ring 固定并入 drain_body visual; body 加 hinge_bracket ear)
        │     grate ──[body_to_grate: REVOLUTE axis=+X(水平), origin=(0,HINGE_Y,HINGE_Z) -Y 缝缘] (翻起 0..2.0 rad)
        │            └─ grate_disc visual 由 [grate_pattern slot] 切孔 ×[perf_count N]
        │
        └─ popup_center_plug :
              grate_rim ──[body_to_grate_rim: PRISMATIC +Z] (基线提起)
                └─ grate ──[rim_to_grate: REVOLUTE +Z] (基线拧锁)
                     │  └─ grate_disc visual 由 [grate_pattern slot] 切孔 ×[perf_count N] + 中心 PLUG_BORE 孔
                     └─ center_plug ──[grate_to_plug: PRISMATIC +Z, origin=(0,0,GRATE_T) 盘心] (塞升降 0..0.008)
```

接口点位与 joint 语义：
- **flange_shape 接口（mesh 维度，无 joint）**：决定 `_flange_solid`/`_cup_solid`/`_liner_solid` 的足迹 primitive（box / cylinder / polygon6）；法兰中心圆开口 `HOLE_R` 与篦盘 / 机构在三种足迹下**统一不变**（开口恒为圆，故机构正交于 footprint）。
- **grate_pattern 接口（篦盘 cut 维度，无 joint）**：决定 `_grate_solid` 内的 cut 循环（`_slot_specs` / `_ring_specs`+`_bridge_bar` / `_grid_hole_positions`）；篦盘外形 / 厚 / 半径（GRATE_R/GRATE_T）不变，pattern 只改盘面穿孔，**篦盘仍是单一 `grate` part**。
- **grate_mechanism 接口（互斥三选一，主 joint 拓扑）**：
  - twist_lock_lift_out：`grate_rim` 坐 `drain_body` seat plate（`body_to_grate_rim` PRISMATIC origin=(0,0,RIM_REST_Z)，提起出 seat）；`grate` 坐 `grate_rim` 内 lip（`rim_to_grate` REVOLUTE origin=(0,0,DISC_LOCAL_Z) 盘心轴）。两 captured-seat overlap（rim↔body seat plate、grate↔rim lip）。
  - hinged_flip_grate：seat ring 固定并入 body；`grate` 经 `hinge_bracket`（-Y 缝缘 barrel）绕水平 X 轴翻起（`body_to_grate` REVOLUTE origin=(0,HINGE_Y,HINGE_Z)）；q=0 篦盘闭合盖住法兰圆开口（覆盖 plan）。
  - popup_center_plug：在 twist+lift 基线上加 `center_plug`，经篦盘中心 bore 孔由 `grate_to_plug` PRISMATIC origin=(0,0,GRATE_T) 升降；plug cap q=0 贴篦盘面、升到 +0.008 露排水。plug 是 `grate` 的子（随 twist/lift 一起动）。
- **rest pose**：所有机构 q=0 闭合 / 坐入——twist_lock 篦子坐 seat（lift=0, twist=0，顶面与法兰齐平）；hinged_flip 篦子闭合盖开口（q=0）；popup plug cap 贴篦面（q=0）。
- **mating policy**：所有接触是 captured-seat（rim 坐 seat plate / grate 坐 lip）/ captured-bore（plug stem 穿 bore）/ hinge-bracket pin —— 几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 `ctx.allow_overlap` 段：twist_lock L309-318 / popup 同段 / hinged 的 allow_overlap）。
- **互斥 / 可选 / 派生**：grate_mechanism 三候选互斥（一次只一种篦子机构）；flange_shape 与 grate_pattern 与 grate_mechanism 正交（任意法兰 × 任意图样 × 任意机构均合法，开口恒圆、篦盘恒圆）；perf_count 为篦盘内 cut 多重性，随 grate_pattern 解析（pinwheel→slot 总数、concentric→ring 数、grid→网格点数）。

## 每槽位 Module Emits / Interfaces

### Slot A / flange_shape（以 square 为例；round/hex 仅换足迹 helper，part 树不变）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drain_body`（visual: `flange_plate` 抛光法兰 + `drain_cup` 锥杯 + `cavity_liner` 暗腔衬里）| concentric(square) `_flange_solid` L151-167 / `_cup_solid` L170-185 / `_liner_solid` L188-197；round b8d32e6f L133-179；hex 4b1ebd24 L142-190 |
| internal joints | 无（drain_body 是 root，足迹层无活动件）| — |
| upstream interface | root（坐地 z=0，无父）| — |
| downstream interface | 法兰中心圆开口 `HOLE_R` + seat plate（供 grate_mechanism 接入；开口恒圆，独立于足迹）| concentric `_flange_solid` hole cut L159-164 |

### Slot B / grate_pattern（篦盘 cut；以 pinwheel 为例）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`grate_disc` 是 `grate` part 的 visual，pattern 仅改其 cut 循环 | hinged `_grate_solid` L268-313 |
| internal joints | 无（pattern 不引入 joint）| — |
| interface | 篦盘 `disc`（`cylinder(GRATE_T,GRATE_R)`）被 pattern helper 切孔；穿孔单元数 = perf_count（见 §8）| hinged `_slot_specs` L98-110 / concentric `_ring_specs` L89-96 / grid `_grid_hole_positions` L79-96 |

### Slot C / grate_mechanism — twist_lock_lift_out
| emits | 描述 | 来源 |
|---|---|---|
| parts | `grate_rim`（`_rim_solid` L 形 seat ring）+ `grate`（`grate_disc` 穿孔盘）| round b8d32e6f rim L257-262 / grate L264-269 |
| internal joints | `body_to_grate_rim` PRISMATIC axis=(0,0,1)，origin=(0,0,RIM_REST_Z)，lower=0 / upper=0.030；`rim_to_grate` REVOLUTE axis=(0,0,1)，origin=(0,0,DISC_LOCAL_Z)，lower=-π/2 / upper=+π/2 | round L273-295 |
| upstream interface | rim 坐 body seat plate（captured-seat，`allow_overlap(rim,body)`）；grate 坐 rim 内 lip（captured-seat，`allow_overlap(grate,rim)`）| round run_tests L309-318 |

### Slot C / grate_mechanism — hinged_flip_grate
| emits | 描述 | 来源 |
|---|---|---|
| parts | `grate`（`grate_disc` + hinge knuckle）；body 加 `seat_ring`（固定）+ `hinge_bracket` ear | hinged seat_ring/bracket L338-347 / grate L350-355 |
| internal joints | `body_to_grate` REVOLUTE axis=(1,0,0)，origin=(0,HINGE_Y,HINGE_Z)，lower=0 / upper=2.0（翻起）| hinged L359-369 |
| upstream interface | grate knuckle 落入 body `hinge_bracket`（-Y 缝缘 captured-pin）；q=0 篦盘闭合盖法兰开口 | hinged `_hinge_bracket_solid` L219+ / origin L364 |

### Slot C / grate_mechanism — popup_center_plug
| emits | 描述 | 来源 |
|---|---|---|
| parts | `grate_rim` + `grate`（中心 bore）+ `center_plug`（cap + stem）| popup rim L290-294 / grate L297-301 / plug L331-336 |
| internal joints | `body_to_grate_rim` PRISMATIC +Z（基线）+ `rim_to_grate` REVOLUTE +Z（基线）+ `grate_to_plug` PRISMATIC axis=(0,0,1)，origin=(0,0,GRATE_T)，lower=0 / upper=0.008 | popup L306-349 |
| upstream interface | rim/grate 同 twist_lock captured-seat；plug stem 穿篦盘中心 `PLUG_BORE_R` 孔（captured-bore，`allow_overlap(plug,grate)`）；plug cap q=0 贴篦面 | popup L243 bore / run_tests allow_overlap |

### perf_count multiplicity（篦盘穿孔单元复制；non-moving cut）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；穿孔单元是 `grate_disc` 的 cut（slots/rings/holes），随篦盘动 | hinged `_grate_solid` L268-313 |
| joints | 无（穿孔非移动件，cut 进篦盘）| — |
| placement | pinwheel: `for group in range(N_GROUPS): for i in range(SLOTS_PER_GROUP)`，等角四象限 + 组内等距；concentric: `for i in range(N_RINGS)` 等径环；grid: `for row: for col:` 等距网格裁圆 field | hinged L268-313 / concentric L241-265 / grid L217-232 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| flange_shape | enum | square / round_circular / hexagonal | square | choice | 由 deterministic procedural sampler 选；决定 flange/cup/liner mesh helper（不改拓扑）| module table |
| grate_pattern | enum | pinwheel_slots / concentric_rings / square_grid_holes | pinwheel_slots | choice | sampler 选；决定 `_grate_solid` cut 循环（无 joint）| module table |
| grate_mechanism | enum | twist_lock_lift_out / hinged_flip_grate / popup_center_plug | twist_lock_lift_out | choice | sampler 选；**主机构（互斥），决定 part 树 / joint 拓扑** | module table |
| perf_count (N) | int | 声明域随 pattern（见 §8 conditional）；sweep 采样域偏小加权 | pattern 各自基线 | conditional→slot_choice | 编入 slot_choice 为 `("perf", f"n{bucket}")`（拓扑维度）；N 域随 grate_pattern 解析 | §8 |
| palette_style | enum | brushed_stainless / polished_chrome / matte_black / antique_brass / oil_rubbed_bronze | brushed_stainless | palette | palette only，**不计入 slot_choice**；改 body/rim/grate/plug 的 metal rgba | 各样本 material 段 |
| flange_size_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放 FLANGE_SIDE/FLANGE_R/HEX_FLAT_TO_FLAT（法兰足迹主尺寸）+ 派生 cup/liner，clamp | 各样本 FLANGE 常量 |
| cup_depth_scale | float | [0.85, 1.25] | 1.0 | independent | 缩放 TOTAL_H/CUP_H（杯深 → FLANGE_BOT_Z/RIM_REST_Z/HINGE_Z 派生），clamp | 各样本 TOTAL_H |
| grate_open_ratio | float | [0.70, 0.86] | 0.79 | independent | HOLE_R / (flange 半足迹)：圆开口占法兰比例；派生 GRATE_R/RIM_OUT_R，clamp | HOLE_R/FLANGE_R 比 |
| flip_angle_scale | float | [0.80, 1.10] | 1.0 | conditional | 仅 hinged_flip 有效；缩放 `body_to_grate` upper（≤2.2 rad，保不过翻）| hinged FLIP_UPPER L93 |
| twist_range_scale | float | [0.80, 1.05] | 1.0 | conditional | 仅 twist_lock/popup 有效；缩放 REVOLUTE twist `±TWIST_LIMIT`（≤π/2·1.05）| twist 样本 TWIST_LIMIT |
| plug_travel_scale | float | [0.80, 1.20] | 1.0 | conditional | 仅 popup 有效；缩放 `grate_to_plug` upper（≤ stem 保持咬合行程）| popup PLUG_TRAVEL L82 |
| perf_density_scale | float | [0.80, 1.20] | 1.0 | independent | 缩放穿孔 pitch（SLOT_PITCH/RING_PITCH/GRID_PITCH）→ 间接改 N，clamp | 各 pattern PITCH 常量 |
| (—) | constraint | — | — | inequality | 穿孔不超 field：pinwheel `FIELD_R<GRATE_R`、concentric `max ring outer_r<GRATE_R`、grid `hypot≤GRID_FIELD_R-GRID_HOLE_R`；违反时按比例缩 pitch / 减 N 或拒绝重采 | 各样本 `_grate_solid` field 约束 |
| (—) | constraint | — | — | inequality | 圆开口 ≤ 法兰内可容：`HOLE_R + margin ≤ flange 半足迹`（square: FLANGE_SIDE/2；round: FLANGE_R；hex: 内切半径）| `_flange_solid` hole cut |
| (—) | constraint | — | — | inequality | 篦盘 / rim 留开口径向间隙：`RIM_OUT_R < HOLE_R`、`GRATE_R < RIM_IN_R`（捕获坐入，非穿模）| 各样本 RIM/GRATE 常量 |
| (—) | constraint | — | — | conditional | grate_mechanism=hinged_flip 时 seat ring 改 body visual（非独立 rim part）、且无 twist/plug joint；mechanism=popup 时篦盘加中心 bore（pinwheel/grid 须中心留 web 容 bore）| 各机构样本 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度 / 穿孔密度，**绝不改变 flange_shape / grate_pattern / grate_mechanism / N-bucket 的拓扑等价类**。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（篦盘穿孔单元数）：

- **count_param**：`perf_count`（模板内变量 N；随 grate_pattern 解析为 pinwheel 的 `N_GROUPS×SLOTS_PER_GROUP`、concentric 的 `N_RINGS`、grid 的 `_grid_hole_positions` 网格点数）。
- **N_range**：source map 建议 [4,60]（视盘径连续缩放）。本 spec 按 pattern 分别声明产品域（conditional），并将连续 N **分桶**为拓扑维度（避免每个整数 N 都算一个 distinct 拓扑类）：
  - pinwheel：`N_GROUPS=4` 固定（风车四象限是身份），`SLOTS_PER_GROUP∈[3,8]`（基线 5）→ 总 slots ∈ [12,32]。
  - concentric：`N_RINGS∈[3,8]`（基线 5），`N_BRIDGES=4` 固定（辐条结构）。
  - grid：网格点数随 `GRID_PITCH` 与 field 派生 ∈ [9,49]（基线 ~13–21，pitch 0.009）。
  - **拓扑分桶**：把 N 映射到 `bucket∈{sparse, medium, dense}`（按各 pattern 三档），`("perf", f"n{bucket}")` 进 slot_choice；连续 N 由 `perf_density_scale` 在桶内微调（非拓扑）。
- **sampling domain**：`config_from_seed` 先按 grate_pattern 解析该 pattern 的 N 合法域，再 `rng.choices(三档桶, weights=偏小)`（sparse 高频、dense 长尾），桶内 N 由 pitch uniform 采。`resolve_config` 把任意外部 N clamp 到 pattern 合法域。
- **copied object**：单只穿孔单元——pinwheel 单矩形槽（`box` cut）/ concentric 单环（`_ring_slot` annular cut）/ grid 单圆孔（`_grid_hole_cutter` cylinder cut）；共享 helper 发射，N 个 cut 复用同一 cutter 几何对象循环 union 后一次 `disc.cut`。
- **naming**：穿孔是 cut（非命名 part）；循环 index 隐式（`for group/for i/for row,col`），不暴露 `*_{i}` part 名。
- **placement**：pinwheel 等角四象限 + 组内等距（`_slot_specs` y 递增 + 90° 旋转）；concentric 等径环（`RING_R0 + i·RING_PITCH`）；grid 等距网格裁圆 field（`hypot(x,y)≤max_r`）。三者均**绝对式**（每单元位置由 index 与 pitch 解析，不累加漂移）→ N-不变前提。
- **joint policy**：穿孔是**非移动件 cut**（Rule 1）→ 切进 `grate_disc` visual，**不发射独立 joint**；活动关节由 grate_mechanism 提供。
- **source/gating**：copy-logic 源取 hinged/round 的 `for group: for i` 风车循环 L268-313、concentric 的 `for i in range(N_RINGS)` 环循环 L241-265、grid 的 `for row: for col` 网格循环 L217-232。N 与 grate_pattern 联动见 §9 矩阵。

## 拓扑多样性审计

总组合数：flange_shape(3) × grate_pattern(3) × grate_mechanism(3) × perf_count 桶(3，{sparse,medium,dense}) = **81**。

仅 grate_mechanism(3) = 真正的 joint 拓扑类（2 joint depth-2 twist+lift / 1 joint depth-1 hinge / 3 joint depth-3 twist+lift+plug）；叠 grate_pattern(3) × flange_shape(3) = **27 ≥ 10** 已稳过；叠 N 桶(3) → 81 充裕。

理由：grate_mechanism 提供真正的 part 树 / joint 拓扑差异（3 part/2 joint、2 part/1 joint、4 part/3 joint，链深 2/1/3）；grate_pattern × flange_shape 是 mesh/cut 维度但仍产生不同 build choice tuple；N 桶编入 `slot_choices_for_seed`（`("perf", f"n{bucket}")`）。**flange_shape / grate_pattern / perf 桶必须各自编入 slot_choice tuple**，否则 mesh/cut 维度损失。flange × pattern × mechanism × N桶 = 81 distinct slot_choice 组合。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（flange_shape / grate_pattern / grate_mechanism），经兼容矩阵合法化（本类三轴近乎正交，gate 极少），再按 grate_pattern 解析 perf N 合法域并 `rng.choices` 加权三桶，再 uniform 各连续 scale（flange_size/cup_depth/open_ratio/perf_density + conditional flip/twist/plug 行程）。compatibility matrix 仅处理少数耦合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：见 §参数表的 flange_size_scale / cup_depth_scale / grate_open_ratio / perf_density_scale（independent）+ flip_angle_scale@hinged / twist_range_scale@twist+popup / plug_travel_scale@popup（conditional）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot + 解析 grate_pattern 的 perf 桶 / N（解析 conditional 范围：flip 仅 hinged、twist 仅 twist_lock/popup、plug 仅 popup）→ 采 independent flange_size/cup_depth/open_ratio/perf_density → 派生（cup/liner 随 flange_size 等比；GRATE_R/RIM 随 open_ratio）→ 用三条 clearance inequality（穿孔不超 field、开口 ≤ 法兰内容、篦盘/rim 径向间隙）投影 / 回缩。跨部件依赖（穿孔 vs field、开口 vs 法兰、篦盘 vs 开口）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏机构 origin、captured-seat/bore 接口、N cut 逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（经兼容矩阵），按 grate_pattern 解析 perf N 域并 `rng.choices` 加权三桶，再 uniform 各 scale | slot_choices_for_seed 含 `("flange",…)`/`("pattern",…)`/`("mechanism",…)`/`("perf", f"n{bucket}")` 且与 build 一致 |
| compatibility matrix | (1) **三主轴近乎正交**：flange_shape × grate_pattern × grate_mechanism 任意组合合法（开口恒圆、篦盘恒圆、机构不依赖足迹 / 图样）→ 无互斥 gate。 (2) **popup × grate_pattern**：popup 需篦盘中心留 web 容 `PLUG_BORE_R` 孔；concentric_rings 的内环 `RING_R0=0.007` 与 grid 中心若占满中心，须 gate "popup 时 pattern 中心留 bore margin"（pinwheel 中心已有 CENTER_GAP web；concentric 把 RING_R0 抬到 ≥PLUG_BORE_R+margin；grid 跳过中心格点）。 (3) **hinged_flip × perf 桶**：翻盖篦盘无 rim/twist，dense 穿孔不影响 hinge，但 dense 穿孔削弱 hinge 缘强度 → dense 桶在 hinged 下降级 medium（可选）。 (4) **N 上限随 field 与 pitch**：dense 桶 clamp 到 pattern 的 field 容量上限（pinwheel ≤8 slots/group、concentric ≤8 rings、grid ≤49 holes）。 | 无穿模 / 开口篦盘不卡 / bore 不撞穿孔 / 翻盖闭合覆盖开口 / 穿孔不超 field |
| controlled local variation | 7 个 clamped scale（flange_size/cup_depth/open_ratio/perf_density independent + flip@hinged/twist@twist+popup/plug@popup conditional），每 build 统一 | 比例变化不破坏机构 origin、captured-seat/bore、开口覆盖、坐入、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| flange_shape | 3 | yes | yes | square 基线（从 square-body 变体回溯）/ round / hex；mesh 维度，正交 |
| grate_pattern | 3 | yes | yes | pinwheel / concentric / grid；篦盘 cut 维度，无 joint |
| grate_mechanism | 3 | yes | yes | twist+lift(2 joint) / hinged(1 joint) / popup(3 joint)（互斥主机构）|
| perf_count (N) | 3（采样桶 {sparse,medium,dense}，sparse 高频 / dense 长尾）| yes | yes | 拓扑维度，编入 slot_choice；N 域随 pattern conditional |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("flange",…)`/`("pattern",…)`/`("mechanism",…)`/`("perf", f"n{bucket}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling；perf N 采样域随 grate_pattern 解析
- `resolve_config` 把 perf N clamp 到 pattern 合法域、各 scale clamp 到声明范围；flip/twist/plug 行程为 conditional 随 mechanism 解析；三条 clearance inequality（穿孔不超 field、开口≤法兰内容、篦盘/rim 径向间隙）在 resolve 内投影 / 回缩
- compatibility matrix / gating：popup 时 pattern 中心留 bore margin；dense 桶 clamp 到 field 容量上限；三主轴正交无非法互斥
- 连续 scale clamp 后不破坏机构 origin / captured-seat/bore 接口 / 开口覆盖 / 坐入 / N cut
- 关键 joint：twist_lock `body_to_grate_rim` PRISMATIC axis≈(0,0,1) + `rim_to_grate` REVOLUTE axis≈(0,0,1)；hinged `body_to_grate` REVOLUTE axis≈(1,0,0)（水平，abs(axis[0])>0.99）；popup 三 joint（PRISMATIC+REVOLUTE+PRISMATIC），`grate_to_plug` PRISMATIC axis≈(0,0,1)
- captured-seat / bore / hinge-pin：element-scoped `allow_overlap`（twist_lock `grate_rim`↔`drain_body` seat plate、`grate`↔`grate_rim` lip；popup `center_plug`↔`grate` bore；hinged grate knuckle↔`hinge_bracket`），照搬各样本 run_tests 的 allow_overlap 段（twist_lock L309-318）
- copied object（穿孔）遵循 cut-into-disc + 绝对式 placement（等角 / 等径 / 网格）+ Rule 1（无独立 joint）
- grandfather：所有 captured-seat / bore / hinge 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把 grate_pattern 或 flange_shape 当独立 joint 槽（加 articulation）→ 二者是 mesh/cut 维度，无活动语义（违反槽定义）。
- 把 perf_count 当普通 int 参数、不进 slot_choice → 稀疏与密集穿孔 slot_choice 同形，损失拓扑维度（违反 §8/§9 硬要求）。
- popup_center_plug 配 concentric_rings/grid 但篦盘中心被穿孔占满 → plug bore 无 web 容身、撞穿孔；必须 gate（popup 时 pattern 中心留 bore margin）。
- 把穿孔当独立活动 part 加 joint → 违反 Rule 1（穿孔是篦盘 cut，应切进 `grate_disc` visual）。
- 机构 rest pose 设成张开 / 提起 / 翻起而非 q=0 闭合坐入 → current-pose 与 viewer 目检不符（所有样本闭合姿态 lower=0 / 坐 seat）。
- 机构 joint origin 放在腔中心或任意点而非真实 seat 面 / 盘心 / 缝缘铰线 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 给 captured-seat / bore / hinge-pin 补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- perf_density / pitch 致穿孔超出 field（FIELD_R/ring outer_r/grid field）→ §7 第一条不等式 FAIL；须按比例缩 pitch / 减 N。
- 把 hinged_flip 的 seat ring 当独立 rim part 还加 twist joint → hinged 变体 seat ring 是固定 body visual、单 REVOLUTE，不可混入 twist_lock 的 rim part。
- 把连续尺寸 / 颜色 / 材质（palette_style / flange_size scale）当新 candidate 塞进 slot → 不是结构差异。
- 把长条淋浴沟地漏 / 水槽提篮 / 通风扇语义混入 → 出类（见 §排除项 / §边界）。

## 与相邻类别的边界

- 不该混入：**长条淋浴沟地漏 / linear shower channel drain**——长条形 flange + 长条篦，twist-lock 圆机构不适用，需 flange+grate 双轴耦合改型（见 §排除项，留作 compatibility matrix 素材，不纳单轴格子）。
- 不该混入：**水槽下水提篮 / sink strainer basket**——深篮 + 提篮提手 + 螺纹下水管，主形态是篮非扁平法兰地漏。
- 不该混入：**通风扇 / 排气格栅 / wall vent fan**——虽同为圆法兰穿孔盘，但有叶片 / 电机 / 进风导流，主功能通风非排水（污染样本 `rec_model-a-round-flange-mounted-wall-vent-fan` 即此类，已排除，见 §排除项）。

## 排除项（contamination）

records-root 下有 2 个挂着相邻 slug 片段但**非 metal drain** 的 5★ 记录，已排除、不进 source 表：

| record_id | rating | 实际内容 | 排除理由 |
|---|---|---|---|
| `rec_model-a-round-flange-mounted-wall-vent-fan-about_20260610_084754_275335_6e21aa96` | 5 | **圆法兰墙壁通风扇**（"round flange-mounted wall vent fan, 0.26 m dia, pale grey painted metal, annular mounting…"）| 是通风扇非地漏：有叶片 / 进风面、尺寸 0.26 m（地漏 0.12 m）、功能通风非排水。source map 命名的 drain parent（`…square-stainless-steel-bathroom-floor-dr_…`）**未同步**，此 vent fan 不能替代之 |
| `rec_variant-base-support-hairpin-metal-legs-replace-_20260617_091347_462104_dcdcb159` | 5 | **带腿橱柜 / 边几**（"hairpin metal legs… two prismatic drawers, gallery-lip shell, chrome bar handles, runner rails…"）| 是抽屉柜变体（cabinet/console），与地漏无任何结构关系，仅 slug 含 "metal"；属其他小类污染 |

source map 的 `rectangular_linear`（长条淋浴沟地漏）已在 source map §排除项中标注为 compatibility-matrix 素材、未纳单轴格子，本 spec 沿用（无对应样本，不列 candidate）。

**5★ 计数说明**：source map 声称 6 变体 + 1 parent = 7；本仓库实际同步 6 个 genuine drain 变体，parent 未同步。6 ≥ 5（§2.1 门槛），且每个 named slot 候选均 ≥2、有真实 `model.py:Lx-Ly`，故继续 author（square/pinwheel/twist_lock 基线从 square-body 变体回溯，见槽位表注记）。如审核认为缺 parent 须先同步，可阻塞。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) source map 的 square parent 未同步、基线从 fork 变体回溯是否接受，还是须先同步 parent；(2) flange_shape / grate_pattern 建模为 mesh/cut 维度（非串联 joint slot）是否认可；(3) perf_count 分桶 {sparse,medium,dense} 进 slot_choice 的拓扑维度处理；(4) popup × concentric/grid 的中心 bore-margin gate 策略；(5) Topology target 81<300 的说明是否接受（本小类真实结构上限），或要求扩到 4 档/108；(6) 2 个污染样本（vent fan + cabinet drawer）排除是否确认）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：`_flange_solid`/`_cup_solid`/`_liner_solid` + `_tapered_{square,round,hex}_tube`（footprint mesh，按 flange_shape 切换）；`_grate_solid` + `_slot_specs`/`_ring_specs`+`_ring_slot`+`_bridge_bar`/`_grid_hole_positions`+`_grid_hole_cutter`（pattern cut，按 grate_pattern 切换）；`_rim_solid`（twist_lock/popup 用 rim part，hinged 用 body visual）；`_hinge_bracket_solid`（hinged）；`_plug_solid`（popup）。穿孔 cutter N 复制复用同一几何对象循环 union。
- captured 接口 allow_overlap：`run_metal_drain_tests` 里逐机构补 element-scoped `allow_overlap`（twist_lock：rim↔body seat plate + grate↔rim lip，照搬 round/concentric run_tests L309-318；popup：+ plug↔grate bore；hinged：grate knuckle↔hinge_bracket），照搬各样本 run_tests 段。
- conditional 范围解析顺序：先采 flange_shape / grate_pattern / grate_mechanism + 解析 perf 桶 N → 解析 flip_angle（仅 hinged）/ twist_range（仅 twist_lock/popup）/ plug_travel（仅 popup）/ popup 时 pattern 中心 bore margin → 采 flange_size/cup_depth/open_ratio/perf_density independent scale → 派生 cup/liner/GRATE_R/RIM → 投影三条 clearance inequality。
- 机构 part 树差异：twist_lock=3 part(body/rim/grate)；hinged=2 part(body+seat_ring visual/grate)，rim 并入 body；popup=4 part(+center_plug)。slot_choice 的 mechanism 维度即决定 builder 走哪条 part-tree 分支。
- 参考模板：`agent/templates/Bag_Suitcase_Shopping_bucket.py`（同为 mixed pattern：固定 named slots + `("count", f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 mesh 复用 + 兼容矩阵 gating + captured allow_overlap 骨架，本类可同构改编）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A（square 基线）+ B（pinwheel 基线携带）| square footprint | rec_…concentric-rings…d68de668 | `_tapered_square_tube` L117-148 / `_flange_solid` box L151-167 / `_cup_solid` L170-185 / `_liner_solid` L188-197 | square 足迹 mesh helper 基线（其 pattern 字段另取 concentric）|
| S2 | A | round_circular footprint | rec_…flange-shape-round-circular…b8d32e6f | `_tapered_round_tube` L99-130 / `_flange_solid` cylinder L133-149 / `_cup_solid` L152-167 / `_liner_solid` L170-179 | 圆形足迹 mesh helper（part 树不变）+ pinwheel 基线 `_slot_specs` L83-96 / `_grate_solid` L208-231 + twist_lock 基线 articulation L273-295 |
| S3 | A | hexagonal footprint | rec_…flange-shape-hexagonal…4b1ebd24 | `_hex_circum_d` L103-105 / `_tapered_hex_tube` L108-139 / `_flange_solid` polygon6 L142-159 / `_cup_solid` L162-178 / `_liner_solid` L181-190 | 六边形足迹 mesh helper（part 树不变）|
| S4 | B | concentric_rings pattern | rec_…grate-pattern-concentric-rings…d68de668 | `_ring_specs` L89-96 / `_ring_slot` L99-114 / `_bridge_bar` L226-238 / `_grate_solid` L241-265 | 同心环槽 cut + 辐条 + ring 多重性源 |
| S5 | B | square_grid_holes pattern | rec_…grate-pattern-square-grid-holes…e214b2de | `_grid_hole_positions` L79-96 / `_grid_hole_cutter` L208+ / `_grate_solid` L217-232 | 方格圆孔阵 cut + grid 多重性源 |
| S6 | B（pinwheel）+ C（twist_lock 基线）| pinwheel + twist_lock | rec_…flange-shape-round…b8d32e6f | `_slot_specs` L83-96 / `_grate_solid` L208-231 / `body_to_grate_rim` PRISMATIC L273-281 / `rim_to_grate` REVOLUTE L285-295 / allow_overlap L309-318 | pinwheel 风车 pattern + twist_lock_lift_out 机构（2 joint）+ captured-seat 范式 |
| S7 | C | hinged_flip_grate | rec_…grate-mechanism-hinged-flip…3cfbbefa | `_hinge_bracket_solid` L219+ / seat ring→body L338-347 / `body_to_grate` REVOLUTE L359-369 | 单边翻盖（1 REVOLUTE 水平 X，seat ring 固定）|
| S8 | C | popup_center_plug | rec_…grate-mechanism-popup-center-plug…a0a6918d | `_plug_solid` L249+ / 篦盘 bore L243 / twist+lift 基线 L306-329 / `grate_to_plug` PRISMATIC L339-349 | 中心 pop-up 塞（twist+lift + 第三 PRISMATIC，4 part 链深 3）|
