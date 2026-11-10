# coffin (rustic wooden coffin / casket with a hinged plank lid) — Modular Spec

> 来源小类：`picture/Other/Coffin`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Other__Coffin.md`。
> **"Coffin" 在此 = 入殓木棺 / casket：一只长条中空 plank 木箱（toe-pincher 六面 / 矩形 casket / 锥形梯形），开顶坐地，上压一块（或两块 / 两叶 / 半身）平木盖，盖可沿一长边 rim REVOLUTE 翻起，或作为单一 PRISMATIC +Z 竖直上滑盖；盖面有三道深色 strap 板 + 头端拉丁十字；可选两长边 carry handles（固定导轨 / 摆动 drop-bar）。**
>
> **同步状态**：本 spec 引用的 **8 个真·棺木 5 星样本**（1 parent + 7 fork 槽位变体）已同步进本仓库 `data/records/`，rating=5，行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一核对）。
>
> **⚠ 数据污染剔除（重要）**：`data/records/` 下另有 4 个 `rec_variant-body-shape-rectangular-slab-…`、`rec_variant-body-shape-round-cylindrical-…`、`rec_variant-lid-mechanism-clamp-locking-…`、`rec_variant-lid-mechanism-hinged-flip-…` 记录，slug 片段与本类碰撞，但其 `model.py` 实为 **打火机（disposable_flint_pocket_lighter）与铸铁锅（cast_iron cauldron）** 变体（已逐一打开核对 `ArticulatedObject(name=...)`）。**这 4 个不是 coffin，未采纳、不进任何 slot/candidate。** 本 spec 的来源池 = source map 列出的 8 个、且 `name` 含 `coffin`/`casket` 的记录。

## 元信息
| 项 | 值 |
|---|---|
| slug | `coffin` |
| template path | `agent/templates/Other_Coffin.py` |
| test path (optional) | `tests/agent/test_coffin_template.py`（不写，sweep-pipeline 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: body_shape + lid_mechanism + carry_handles，**外加** `handle_count` 摆动把手多重性轴，仅 swing 候选下生效）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（真·棺木：1 parent + 7 fork 槽位变体；均 converged、compile success、≥1 非 fixed joint、workbench-only）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、run_tests / allow_overlap）+ 额外打开 4 个污染记录核对并剔除 |
| read_scope | all 5-star coffin samples in this category（剔除 4 个非棺木污染记录）|
| source_index_policy | 仅被采纳为 module source 的 8 个真·棺木样本进入下方 source 表与 §14；4 个污染记录不进任何表 |

阅读要点（用于槽位分解）：
- **共享基线拓扑**：所有 8 个样本共享同一参数化骨架——`LENGTH=1.90`、`BODY_H=0.33`、`LID_T=0.04`、`WALL_T=FLOOR_T=0.03`、`HINGE_Y=-(SHOULDER_HALF_W+LID_OVERHANG)`、`LID_OPEN_MAX=radians(110)`、相同 `_offset_polygon`/`_extrude_poly`/`_x_slab`/`_body_shell`/`_body_strap_band`/`_lid_panel`/`_lid_strap` helper 家族，相同 3 道 `STRAP_XS` 与头端拉丁十字（`cross_upright`+`cross_arm`）。**body 始终是 root，坐地**；活动语义集中在 lid_mechanism（必有）+ carry_handles（可选）。材质恒为 `plank_wood (0.44,0.31,0.20)` + `strap_wood (0.29,0.19,0.12)` + `cross_wood (0.22,0.14,0.09)`（swing 另加 `handle_iron (0.18,0.15,0.12)`，fixed_rails 另加 `rail_wood (0.38,0.26,0.16)`）。
- **body_shape 轴**（Slot A）：只改 `FOOTPRINT` 多边形（toe_pincher = 6 顶点收肩；rectangular = 4 顶点恒宽；tapered = 4 顶点单调收锥），`_body_shell`/`_lid_panel`/`strap`/`hinge` 全部由 `FOOTPRINT` 派生 → footprint 是 **mesh-profile 维度**，part 树 / joint 拓扑不变（body+lid+单 REVOLUTE）。
- **lid_mechanism 轴**（Slot B，**主机构槽**）：full_side_hinge（单 `lid` part，**1×REVOLUTE** `lid_hinge`，axis 沿真实侧边 rim 切线；矩形时才是 +X）/ split_two_panel（`lid_0`+`lid_1` 沿 X 切两段，**2×REVOLUTE**，每段沿对应侧边段 rim 独立）/ double_leaf_wings（`lid_leaf_0`+`lid_leaf_1` 沿中线切两叶，**2×REVOLUTE** 镜像沿左右真实侧边 rim 对开）/ half_couch_head_only（`head_lid` 一段 hinged + foot 半盖 **inline 进 body 不动**，**1×REVOLUTE** 沿头端侧边 rim）/ vertical_lift_lid（单 `lid` part，**1×PRISMATIC +Z** `lid_lift`，只竖直上滑不旋转）→ 真正的 part 数 / joint 拓扑变化（1 / 2 / 2 / 1 个 REVOLUTE，或 1 个 PRISMATIC，且互斥不叠加）。
- **carry_handles 轴**（Slot C）：none（无 handles，parent 基线）/ fixed_side_rails（两长边 `carry_rail_{0,1}` 固定导轨，**inline 进 body 的 visual，无 joint**，Rule 1）/ swing_drop_bar_handles（N 个 `handle_{i}` 摆动 U-bail，**每把手独立 REVOLUTE** `handle_{i}_pivot` axis=±X + body 上 `bracket_{i}_{±1}` 承座）→ 从无 / 不动 visual / N 个活动件，是 part 数 + joint 拓扑变化。
- **handle_count 轴**（Slot C 内多重性，仅 swing 下生效）：样本为每长边 3 个、共 6 个（`for side in (-1,1): for x_st in HANDLE_XS:` 双层循环，`handle_idx` 递增命名 `handle_{idx}` / `bracket_{idx}_{arm_s}`）。把手沿长边等距对称、每把手一个独立 REVOLUTE 上下摆（lower=0 hang / upper=radians(85) 外摆）。

## 核心身份

一只**入殓木棺 / casket**：长约 1.9 m、宽约 0.35–0.6 m、高约 0.4 m 的长条**中空开顶 plank 木箱**（`coffin_body`，root，坐地，~0.03 m 壁与底、外壁两道横向 plank seam 槽），footprint 为 toe-pincher 六面收肩 / 矩形恒宽 / 锥形梯形之一；上压一块**平木盖**（单整盖 / 头脚两段 / 双叶对开 / 仅头半身 / 竖直 lift-off 盖），盖沿一长边 top rim **REVOLUTE** 翻起 0..~110° 或以单一 **PRISMATIC +Z** 竖直上滑露出内腔；盖与体侧各横绕**三道深色 strap 木板**，盖头端有一道**拉丁十字**（`cross_upright`+`cross_arm`）。可选两长边**抬棺把手**：固定 carry rail（不动）或摆动 drop-bar bail（N 把，各自 REVOLUTE 上下摆）。默认成熟域 = body_shape(3) × lid_mechanism(5) × carry_handles(3，swing 含 handle_count N) 的木质棺木。

活动语义 = **盖的打开**（1×REVOLUTE 整盖 / 头半盖；2×REVOLUTE 两段 / 双叶；或 1×PRISMATIC +Z 竖直 lift-off 盖）+ 可选**摆动把手**（N×REVOLUTE）。fixed_side_rails 与 half_couch 的 foot 半盖是**不动结构**（inline body visual，Rule 1）。

不该混入：
- **treasure_chest / 珠宝箱 / 工具箱**——虽同为 hinged-lid 箱，但棺木身份在于长条棺形 footprint（toe-pincher 收肩 / casket 长宽比 ~3–6:1）+ 头端拉丁十字 + strap 板 + 入殓尺度（~1.9 m），缺这套即出类；treasure_chest 是近方小箱、常带拱顶盖 + 锁扣。
- **storage box / crate / 普通木箱**——无棺形收肩、无十字、非入殓比例。
- **cauldron / 打火机等"换盖 / 滑盖"小物**（本仓库恰有同 slug 片段的污染样本）——主体非长条棺箱、主运动 spine 与尺度完全不同。
- **棺架 / 灵车 / 墓碑**——棺木本体之外的承载 / 运输 / 标记物，非箱体本身。

## 槽位 + 候选模块表

> **建模注记**：`body_shape`（Slot A）是 `coffin_body` + `lid` + strap + hinge **同一组几何的 footprint 多边形**（六面 / 矩形 / 梯形），由 `FOOTPRINT` 常量一次决定、所有 helper 由它派生，不是独立串联 slot、不贡献额外 joint；列为候选轴以对齐 schema，与 lid_mechanism / carry_handles / N 的笛卡尔积共同撑开多样性（见 §9）。`lid_mechanism` 与 `carry_handles` 才是真正改 part 树 / joint 拓扑的轴。

### Slot A：body_shape（棺体足迹形状——body+lid+strap+hinge 共享的 footprint 多边形）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| toe_pincher_hex（基线） | rec_model-a-rustic-toe-pincher-…_3d5f4f7f (parent) | `FOOTPRINT` L55-62 / `_body_shell` L102-115 / `_lid_panel` L133-141 | eligible if compatible | 六顶点收肩 footprint（头窄 0.35 → 肩宽 0.60 → 脚窄 0.30，肩在 1/3 处）；经典 toe-pincher；part 树 = body+lid+1 REVOLUTE |
| rectangular_casket | rec_variant-body-shape-rectangular-casket-…_477ccc1d | `FOOTPRINT` L51-56（恒宽 4 顶点）/ `_body_shell` L96-109 / `_lid_panel` L127-135 | eligible if compatible | 四顶点恒宽矩形 casket（HALF_W=0.30 头到脚不变，直角），part 树 / joint 与 parent 同；仅 footprint 改 |
| tapered_trapezoid | rec_variant-body-shape-tapered-trapezoid-…_26a4798a | `FOOTPRINT` L56-61（HEAD_HALF_W=0.30→FOOT_HALF_W=0.15 单调收）/ `_body_shell`（同 helper） | eligible if compatible | 四顶点单调收锥梯形（头宽 0.60 → 脚窄 0.30，无肩折），part 树 / joint 与 parent 同；仅 footprint 改 |

### Slot B：lid_mechanism（盖开合机构 —— **主机构槽**，决定盖的 part 树与 REVOLUTE / PRISMATIC 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| full_side_hinge（基线） | rec_model-a-rustic-toe-pincher-…_3d5f4f7f (parent) | `lid` part L171-194 + `lid_hinge` REVOLUTE L199-207 | eligible if compatible | 单 `lid` child 整盖，**1×REVOLUTE** `lid_hinge` axis=该 body_shape 的 -Y 侧边 rim 切线（矩形为 +X；梯形/六边为斜向），origin 锚在真实 rim 点，lower=0 闭 / upper=radians(110) 开；十字 + 3 strap 全在此盖上 |
| split_two_panel | rec_variant-lid-mechanism-split-two-panel-…_1d8d2709 | `LID_PANEL_X_RANGES` L146-149 / `_lid_panel_half` L152-161 / 循环建 `lid_{i}` + `lid_hinge_{i}` L203-256 | eligible if compatible | 盖沿 X 切两段（`lid_0` 头半 / `lid_1` 脚半，中缝 LID_GAP=0.005），**2×REVOLUTE** 同在 -Y rim，但各段 axis 沿对应侧边段切线；两段独立翻起；十字在 lid_0 |
| double_leaf_wings | rec_variant-lid-mechanism-double-leaf-wings-…_de26f9e8 | `_compute_leaf_local_polygons` L165 / `NUM_LEAVES=2` L55 / `leaf_configs` L235-240 / 循环建 `lid_leaf_{i}` + `lid_leaf_{i}_hinge` L245-298 | eligible if compatible | 盖沿中线 y=0 切两叶（`lid_leaf_0` -Y 侧 / `lid_leaf_1` +Y 侧），**2×REVOLUTE 镜像对开**，axis 分别沿左右真实侧边 rim 切线（矩形退化为 ±X），strap 在中线 clip 不互穿；十字在 leaf_0 |
| half_couch_head_only | rec_variant-lid-mechanism-half-couch-head-only-…_0d84ee10 | `head_lid` part + `_foot_lid_panel` inline L191-206 + `_foot_lid_strap` L209-222 / body inline foot 盖 L253-267 / `head_lid_hinge` REVOLUTE L304-314 | eligible if compatible | 仅头半 `head_lid` hinged（**1×REVOLUTE** `head_lid_hinge` axis 沿头端侧边 rim 切线），脚半盖 `foot_lid_panel`+strap **inline 进 body 固定不动**（Rule 1，半身敞棺）；十字在 head_lid |
| vertical_lift_lid | procedural extension | `lid` part + `lid_lift` PRISMATIC | eligible if compatible | 单 `lid` child 整盖，**1×PRISMATIC +Z** `lid_lift`，origin 锚在头端 rim 真实点 `(HEAD_X,-HEAD_HALF_W,BODY_H)`，lower=0 闭 / upper≈0.42 m 开；只竖直上滑，不与任何 REVOLUTE 翻盖叠加 |

### Slot C：carry_handles（抬棺把手；swing 含 handle_count 多重性）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| none（基线） | rec_model-a-rustic-toe-pincher-…_3d5f4f7f (parent) | （body+lid 无任何 handle visual / joint）| eligible if compatible | 无把手（裸棺）；空机构，仅 lid_mechanism 提供活动件 |
| fixed_side_rails | rec_variant-carry-handles-fixed-side-rails-…_b642913b | `_carry_rail` L136-164 / 循环 `carry_rail_{i}` body visual L213-219 | eligible if compatible | 两长边各一根固定 carry rail（`carry_rail_0`/`carry_rail_1`，RAIL_LENGTH=1.50，含 3 个 inline bracket）**inline body visual，无 joint**（Rule 1）；rail 按当前 body_shape 的真实侧壁轮廓贴边，梯形为斜杆、六边收肩在肩部转折，不用最大肩宽做悬空直杆；rail 随 body 不动（盖开时 rail 静止，见 run_tests L438-440）|
| swing_drop_bar_handles | rec_variant-carry-handles-swing-drop-bar-handles-…_de2a3aba | `HANDLE_XS` L54 / `_bail_handle_cq` L173-186 / 双层循环 `handle_{idx}`+`bracket_{idx}_{arm_s}`+`handle_{idx}_pivot` REVOLUTE L253-294 / allow_overlap L470-477 | eligible if compatible | N 个摆动 U-bail（`handle_{i}` part），**每把手独立 REVOLUTE** `handle_{i}_pivot`（axis=±X 按侧、origin 在 pivot_y/HANDLE_PIVOT_Z）lower=0 hang / upper=radians(85) 外摆；body 上 `bracket_{i}_{±1}` 承座（captured，allow_overlap bracket↔bail）；样本 6 把（每侧 3）|

## 槽位图（slot graph）

pattern: mixed（固定 named slots: body_shape 决定 footprint；lid_mechanism + carry_handles 各自挂到共同 `coffin_body`（parallel children）；`handle_count` 在 body 上 N 次复制摆动把手 part+joint+bracket）

```
coffin_body (root, 坐地; 由 body_shape 决定 FOOTPRINT → shell/cavity/seam + strap band + rim 铰线 Z)
  │
  ├── [lid_mechanism slot]  (互斥五选一)
  │     ├─ full_side_hinge      : lid ───────[lid_hinge: REVOLUTE, real side-rim tangent]
  │     ├─ split_two_panel      : lid_0 ─────[lid_hinge_0: REVOLUTE, real side-rim segment tangent]
  │     │                         lid_1 ─────[lid_hinge_1: REVOLUTE, real side-rim segment tangent]
  │     ├─ double_leaf_wings    : lid_leaf_0 [lid_leaf_0_hinge: REVOLUTE, left/right rim tangent]
  │     │                         lid_leaf_1 [lid_leaf_1_hinge: REVOLUTE, mirrored rim tangent]
  │     ├─ half_couch_head_only : head_lid ──[head_lid_hinge: REVOLUTE, head-side rim tangent]
  │                               foot_lid_panel = body inline visual (不动)
  │     └─ vertical_lift_lid    : lid ───────[lid_lift: PRISMATIC axis=+Z, origin=(HEAD_X,-HEAD_HALF_W,BODY_H)]
  │
  └── [carry_handles slot]  (互斥三选一)
        ├─ none            : (无 handle)
        ├─ fixed_side_rails: carry_rail_0 / carry_rail_1 = body inline visual (不动, Rule 1)
        └─ swing_drop_bar  : [handle_count multiplicity 轴]  handle_{i} ──[handle_{i}_pivot: REVOLUTE axis=±X]
                              i∈range(N); body 上 bracket_{i}_{±1} 承座; 沿长边等距对称, 每侧 N/2
```

接口点位与 joint 语义：
- **lid_mechanism 接口（互斥）**：所有盖机构以 `coffin_body` 为 parent，铰线落在 top rim（z=BODY_H）的长边上。
  - full_side_hinge / split_two_panel / half_couch：origin 锚在对应真实侧边 rim 点，axis 取该 rim 段切线；矩形是 (±)X，梯形/六边收肩为带 Y 分量的斜向轴。split 两段各自使用头段/脚段对应侧边切线；half_couch 仅头半 hinged。
  - double_leaf_wings：两条铰线对称在左右真实侧边 rim，leaf_0/leaf_1 用镜像侧边切线对开；矩形退化为 ±X。
  - vertical_lift_lid：origin=(HEAD_X,-HEAD_HALF_W,BODY_H) 锚在头端 rim 真实点，axis=(0,0,1)，单个 PRISMATIC 只沿 Z 竖直上滑；不生成任何 REVOLUTE 翻盖关节。
- **carry_handles 接口（互斥）**：
  - none：无 joint。
  - fixed_side_rails：`carry_rail_{i}` 为 body inline visual，bracket 与 body 长边壁重叠固定（Rule 1，无 joint）；rail 的 y 位置由各 x 处 `half_width_at(x)` 外推，贴随矩形 / 梯形 / 六边收肩侧壁；盖开时 rail 不动。
  - swing_drop_bar：`handle_{i}_pivot` REVOLUTE，origin=(x_st, pivot_y, HANDLE_PIVOT_Z)（pivot_y = side·(该 x 处壁半宽 + 余隙)，落在长边壁外侧），axis=(±1,0,0) 按侧；`bail` U 杆 top 坐入 body `bracket_{i}_{±1}` post（captured，bracket↔bail allow_overlap）。
- **mating policy**：所有 lid hinge / handle pivot 是 **铰线在 rim / pivot 硬件上的 REVOLUTE**，captured 重叠仅出现在 swing 的 bracket↔bail post（element-scoped `allow_overlap`，照搬 swing 样本 run_tests L470-477）。lid 闭合时盖坐 rim 上：`expect_gap`(lid,body,z,max_gap≈0.002) + `expect_contact` + `expect_within`（盖 outline 外挑 rim）。**几何非两轴对齐面对接 → 省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + allow_overlap 守 captured overlap。
- **rest pose**：所有盖 / 叶 q=0 闭合坐 rim；swing 把手 q=0 自然下垂（hang）；fixed rail / foot 半盖恒不动。
- **互斥 / 可选 / 派生**：lid_mechanism 五候选互斥（一次一种盖机构）；carry_handles 三候选互斥；none 无 handle 件（空机构）；handle_count N 仅在 swing 下编入 slot_choice（none / fixed_rails 时 N 不存在）。

## 每槽位 Module Emits / Interfaces

### Slot A / body_shape（以 toe_pincher_hex 为例；rectangular/tapered 仅换 FOOTPRINT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `coffin_body`（root；visual: `body_shell` 中空开顶 shell + 两道 seam 槽 + `body_{head/shoulder/foot}_strap` 三道 strap band）| parent `_body_shell` L102-115 / `_body_strap_band` L118-123 / 装配 L160-168 |
| internal joints | 无（body 是 root，无内部活动件）| — |
| upstream interface | root（坐地 z=0，无父）| — |
| downstream interface | -Y / ±Y 长边 top rim（z=BODY_H）铰线 + 内腔（供 lid_mechanism 接入）；长边壁外侧（供 carry_handles 接入）| parent L48, L204 |

### Slot B / lid_mechanism — full_side_hinge
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`（visual: `lid_panel` 平盖 + 2 道 seam 槽 + `lid_{head/shoulder/foot}_strap` + `cross_upright`+`cross_arm` 头端十字）| parent L171-194 |
| internal joints | `lid_hinge` REVOLUTE axis=(1,0,0)，origin=(0,HINGE_Y,BODY_H)，lower=0 / upper=radians(110) | parent L199-207 |
| upstream interface | lid 闭合坐 body rim（`expect_gap`+`expect_contact`+`expect_within`），铰线在 -Y 长边 rim | parent L268-278 |

### Slot B / lid_mechanism — split_two_panel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid_0`（头半 `lid_panel_0`+strap+十字）+ `lid_1`（脚半 `lid_panel_1`+strap），中缝 LID_GAP | split L203-237 |
| internal joints | `lid_hinge_0` + `lid_hinge_1` 2×REVOLUTE，均 axis=+X、origin=(0,HINGE_Y,BODY_H)，各 lower=0/upper=radians(110)，独立开 | split L242-253 |
| upstream interface | 两段共用 -Y rim 铰线；段间 `expect_gap`(lid_1,lid_0,x,max_gap≈0.02) 可见缝 | split L332 |

### Slot B / lid_mechanism — double_leaf_wings
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid_leaf_0`（-Y 叶 `lid_leaf_0_panel`+clip strap+十字）+ `lid_leaf_1`（+Y 叶 panel+clip strap）| double_leaf L245-286 |
| internal joints | `lid_leaf_0_hinge`(axis=+X,origin=(0,-HINGE_ABS,BODY_H)) + `lid_leaf_1_hinge`(axis=-X,origin=(0,+HINGE_ABS,BODY_H)) 2×REVOLUTE 镜像对开 | double_leaf L289-297 |
| upstream interface | 两叶各坐对侧 rim，中线相接（strap y-clip 防互穿）| double_leaf L200-209, L379-388 |

### Slot B / lid_mechanism — half_couch_head_only
| emits | 描述 | 来源 |
|---|---|---|
| parts | `head_lid`（头半 hinged，`head_lid_panel`+strap+十字）；`foot_lid_panel`+`foot_lid_strap_{i}` **inline 进 body**（不动）| half_couch head L270-300 / foot inline L253-267 |
| internal joints | `head_lid_hinge` REVOLUTE axis=(1,0,0)，origin=(0,HINGE_Y,BODY_H)，lower=0/upper=radians(110)；脚半无 joint | half_couch L304-314 |
| upstream interface | head_lid 坐头半 rim；foot 半盖固定坐脚半 rim（body visual，Rule 1）| half_couch L189-222 |

### Slot B / lid_mechanism — vertical_lift_lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`（整盖，`lid_panel`+3 strap+十字）| procedural extension |
| internal joints | `lid_lift` PRISMATIC axis=(0,0,1)，origin=(HEAD_X,-HEAD_HALF_W,BODY_H)，lower=0 / upper≈0.42m；无 REVOLUTE | procedural extension |
| upstream interface | lid 闭合坐 body rim；打开时整体沿 +Z 竖直平移，XY 不漂移 | procedural extension |

### Slot C / carry_handles — none
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（无把手件）| parent |
| internal joints | 无 | — |

### Slot C / carry_handles — fixed_side_rails
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`carry_rail_0`/`carry_rail_1`（含 3 inline bracket）为 **body visual** | fixed_rails `_carry_rail` L136-164 / 装配 L213-219 |
| internal joints | 无（Rule 1，rail 固定）| — |
| upstream interface | rail bracket 嵌入两长边壁外侧（RAIL_Z_CENTER=0.18 中高），rail / bracket 均由当前 x 处壁半宽外推，非矩形时沿侧壁斜边或肩部折线贴合；盖开时不动 | fixed_rails L154-162, L438-440 |

### Slot C / carry_handles — swing_drop_bar_handles（multiplicity）
| emits | 描述 | 来源 |
|---|---|---|
| parts | N 个 `handle_{i}`（visual `bail` U 杆）；body 上 `bracket_{i}_{-1}`/`bracket_{i}_{+1}` 承座 | swing L270-279 |
| internal joints | 每把手 `handle_{i}_pivot` REVOLUTE，axis=(±1,0,0) 按侧，origin=(x_st,pivot_y,HANDLE_PIVOT_Z)，lower=0/upper=radians(85) | swing L283-293 |
| upstream interface | `bail` arm top 坐入 `bracket_{i}_{arm_s}` post（captured，bracket↔bail allow_overlap）；pivot_y 由该 x 处壁半宽派生（`_half_width_at`）保证清壁 | swing L256-275, L470-477 |

### handle_count multiplicity（摆动把手复制；仅 swing 候选）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle_{i}`（part，bail visual）+ `bracket_{i}_{±1}`（body visual 承座）| swing L253-294 |
| joints | 每把手一个独立 `handle_{i}_pivot` REVOLUTE（不是单 joint 多 visual）| swing L283-293 |
| placement | 双层循环 `for side in (-1,1): for x_st in HANDLE_XS:`，`handle_idx` 递增；每侧 N/2 沿长边 X 等距对称，pivot_y 按侧壁外推 | swing L254-294 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_shape | enum | toe_pincher_hex / rectangular_casket / tapered_trapezoid | toe_pincher_hex | choice | deterministic sampler 选；决定 `FOOTPRINT` 多边形（所有 mesh/hinge 派生）| module table |
| lid_mechanism | enum | full_side_hinge / split_two_panel / double_leaf_wings / half_couch_head_only / vertical_lift_lid | full_side_hinge | choice | sampler 选；主机构（互斥），决定盖 part 数 + REVOLUTE / PRISMATIC 拓扑 | module table |
| carry_handles | enum | none / fixed_side_rails / swing_drop_bar_handles | none | choice | sampler 选；含空机构 none | module table |
| handle_count (N) | int | 声明域 [2,8]（每侧 1–4）；sweep 采样域 [2,8]（偏小加权：4 高频、2/6 常见、8 长尾）；**仅 swing 下生效** | 6 | conditional→slot_choice | 编入 slot_choice 为 `n{N}`（拓扑维度）；仅 `carry_handles=swing_drop_bar`；N 取偶数（每侧 N/2）| swing |
| palette_style | enum | weathered_oak / dark_walnut / ebony_black / pale_pine / mahogany_red | weathered_oak | palette | palette only，**不计入 slot_choice**；改 plank/strap/cross/rail/handle 材质 rgba | 各样本材质（见下）|
| coffin_length_scale | float | [0.92, 1.08] | 1.0 | independent | 缩放 `LENGTH`（保 ~1.9 m 主尺度），clamp；strap/handle x 站位等比 | resolve clamp |
| body_width_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 footprint 半宽（HEAD/SHOULDER/FOOT_HALF_W 同因子），clamp；hinge_y / pivot_y 随之 | resolve clamp |
| body_height_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 `BODY_H`（rim 高 / 腔深），clamp；hinge origin z / handle pivot z 随之派生 | resolve clamp |
| lid_open_angle_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放盖 / 叶 REVOLUTE `upper`（保 ≤ radians(170)），clamp | resolve clamp |
| handle_swing_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 swing 有效；缩放 `HANDLE_PIVOT_MAX`（≤ radians(110)）| resolve clamp |
| handle_spacing_scale | float | [0.90, 1.10] | 1.0 | conditional | 仅 swing 且 N≥4 有效；缩放每侧把手 X 间距 | resolve clamp |
| (—) | constraint | — | — | inequality | 把手沿长边不越界：每侧 `(N/2)·HANDLE_SPAN + ((N/2)-1)·gap ≤ LENGTH·scale − 2·end_margin`；违反时缩 gap 或拒绝重采 | 接口 / clearance |
| (—) | constraint | — | — | inequality | 盖闭合覆盖 rim：closed lid/leaf XY outline 外挑 rim（`expect_within` margin≈0.001）；split/double 各段覆盖各自半区 | 接口 / clearance |
| (—) | constraint | — | — | conditional | handle_count / handle_swing / handle_spacing 仅 `carry_handles=swing_drop_bar` 时解析；其余取标称且不进 slot_choice | 接口 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 body_shape / lid_mechanism / carry_handles / N 的拓扑**。

**palette_style colorway（4–6，从 5★ 样本材质与现实棺木采）**：
- `weathered_oak`（默认）：plank `(0.44,0.31,0.20)` + strap `(0.29,0.19,0.12)` + cross `(0.22,0.14,0.09)` ——直接采自全部 8 样本基线材质（风化橡木）。
- `dark_walnut`：plank `(0.30,0.20,0.12)` + strap `(0.18,0.12,0.07)` + cross `(0.12,0.08,0.05)` ——深胡桃。
- `ebony_black`：plank `(0.10,0.09,0.08)` + strap `(0.05,0.05,0.05)` + cross `(0.16,0.14,0.10)`（哑金十字对比）——黑檀礼棺。
- `pale_pine`：plank `(0.70,0.58,0.40)` + strap `(0.52,0.40,0.26)` + cross `(0.40,0.30,0.18)` ——浅松木素棺。
- `mahogany_red`：plank `(0.40,0.18,0.12)` + strap `(0.28,0.12,0.08)` + cross `(0.18,0.08,0.05)` ——红木抛光。
（swing handle 用 `handle_iron (0.18,0.15,0.12)`、fixed rail 用比 plank 略深的 `rail_wood`，随 palette 同步偏移；palette 不改任何 mesh / joint，仅 rgba。）

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（摆动把手数，**仅 `carry_handles=swing_drop_bar_handles` 下生效**；none / fixed_rails 无此轴）：

- **count_param**：`handle_count`（模板内变量 N / HANDLE_COUNT；两长边摆动 drop-bar 把手总数）。
- **N_range**：声明产品域 **[2, 8]**（每侧 1–4，取偶数对称；source map 建议 [2,8]）。样本为 N=6（每侧 3）。`config_from_seed` 的 sweep 采样域 **[2,8] 偶数**（偏小加权：4 高频、2/6 常见、8 长尾）。仅在选中 swing 候选时采样；其余候选 N 不存在。
- **sampling domain**：`config_from_seed` 在 `carry_handles==swing_drop_bar` 时 `rng.choices((2,4,6,8), weights=偏小)`；`resolve_config` 把任意外部 N clamp 到偶数 ∈[2,8]。
- **copied object**：单只 drop-bar 把手单元——`handle_{i}` part（`bail` U 杆 visual，`_bail_handle_cq` 共享几何对象 N 次复用）+ body 上 `bracket_{i}_{-1}`/`bracket_{i}_{+1}` 承座 visual。
- **naming**：`handle_{i}`（part）/ `handle_{i}_pivot`（joint）/ `bracket_{i}_{arm_s}`（body visual，arm_s∈{-1,+1}）；`handle_idx` 在 `for side in (-1,1): for x_st in HANDLE_XS:` 双层循环里递增（swing L253-294 已用此结构，直接作 copy-logic 源）。
- **placement**：每侧 N/2 个沿长边 **X 绝对式**等距对称分布（x 站位由 N 与中心解析，不累加漂移）；pivot_y = side·(该 x 处壁半宽 `_half_width_at(x)` + 余隙)，使每把手清越棺壁、贴该侧。绝对式是 N-不变前提。
- **joint policy**：**每把手一个独立 REVOLUTE** `handle_{i}_pivot`（axis=(±1,0,0) 按侧，lower=0 hang / upper=HANDLE_PIVOT_MAX 外摆）——非单 joint 多 visual。
- **source/gating**：copy-logic 源取 swing L253-294 的双层循环（样本 N=6）；N=2 即每侧 1 把（仍走循环，range 退化）。N 仅在 swing 下编 `slot_choice`（见 §9）。

**lid_mechanism 的 split / double 是固定 2 段 / 2 叶**（`NUM_LEAVES=2`、`LID_PANEL_X_RANGES` 长 2），**不是可变 multiplicity 轴**——它们是 named 双件结构，N 恒为 2，不暴露 `*_count`。仅 handle_count 是真·可变复制轴。

## 拓扑多样性审计

总组合数：body_shape(3) × lid_mechanism(5) × carry_handles(3，其中 swing 展开 handle_count {2,4,6,8}=4 档) 。
- carry_handles 非 swing 分支：none + fixed_rails = 2 种（无 N）。
- carry_handles swing 分支：swing × N∈{2,4,6,8} = 4 种。
- ⇒ carry_handles 维度有效拓扑数 = 2 + 4 = **6**。
- 总组合 = body_shape(3) × lid_mechanism(5) × carry_handles_eff(6) = **90**。

仅 lid_mechanism(5) × carry_handles_eff(6) = **30**（含 1/2/2/1 REVOLUTE 盖或 1 PRISMATIC +Z 盖 × 无 / 不动 rail / N×REVOLUTE 把手的 joint 拓扑组合）≫ 门控；叠 body_shape(3) → 90 充裕。

理由：lid_mechanism 提供 5 类真正的 joint 拓扑（1 REVOLUTE 整盖 / 2 REVOLUTE 段 / 2 REVOLUTE 镜像叶 / 1 REVOLUTE 头半+固定脚半 / 1 PRISMATIC +Z 竖直 lift-off 盖），carry_handles 提供 无 joint / 不动 visual / N×REVOLUTE 三类，二者笛卡尔积已 ≥30 distinct joint-topology 类；叠 footprint(3) 与 N(4 档) 后总 90 distinct。**N 必须编入 `slot_choices_for_seed` 的 tuple**（swing 时 `("handle_count", f"n{N}")`，对齐 cushion/shopping_bucket/fence_cascade），否则不同把手数在 slot_choice 上无法区分，损失一根拓扑维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（body_shape / lid_mechanism / carry_handles），经兼容矩阵合法化；若 carry_handles==swing 再 `rng.choices` 加权偶数 N∈[2,8]（否则 N 不存在）；再 uniform 各连续 scale（handle_swing / handle_spacing 仅 swing、handle_spacing 仅 N≥4 解析）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：见 §参数表的 coffin_length_scale / body_width_scale / body_height_scale / lid_open_angle_scale / handle_swing_scale（conditional@swing）/ handle_spacing_scale（conditional@swing & N≥4）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（解析 conditional：handle_count/handle_swing/handle_spacing 仅 swing）→ 采 independent length/width/height/angle scale → 派生（hinge origin z 随 body_height、pivot_y 随 body_width、strap/handle x 站位随 length 等比）→ 用两条 inequality（把手沿长边不越界、盖闭合覆盖 rim）投影 / 回缩。跨部件依赖（把手排布 vs 棺长、盖覆盖 vs footprint、pivot_y vs 壁半宽）显式落在 §7 inequality / equation，在 `resolve_config` 内求解。这些 scale 不破坏 hinge/pivot origin、captured bracket↔bail 接口、N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（经兼容矩阵）；swing 时再 `rng.choices` 偶数 N∈[2,8]；再 uniform 各 scale | slot_choices_for_seed 含 `("handle_count", f"n{N}")`（仅 swing）且与 build 一致 |
| compatibility matrix | (1) **handle_count 仅 swing**：none / fixed_rails 不采样 N、不进 slot_choice。 (2) **handle_count 偶数 & 每侧清壁**：N 取偶数（每侧 N/2），pivot_y 由 `_half_width_at` 派生保证清越棺壁；N 过大致把手沿长边越界 → §7 inequality 回缩 / gate 上限。 (3) **swing × lid_mechanism 正交**：把手在棺壁外侧、盖在 rim 顶，互不冲突 → 任意盖机构均可配 swing/fixed/none。 (4) **fixed_rails × double_leaf**：双叶对开占两长边 rim 顶，rail 在壁中高(0.18)外侧，不冲突 → 允许；rail RAIL_LENGTH=1.50 按 length_scale 缩。 (5) body_shape 与机构正交（三 footprint 均可配任意盖 / 把手）。 | 无 floating / 把手穿壁 / 把手越界 / 盖不覆盖 rim / rail 随盖误动 |
| controlled local variation | 6 个 clamped scale（length/width/height、lid_open_angle、handle_swing@swing、handle_spacing@swing&N≥4），每 build 统一；后两者 conditional | 比例变化不破坏 hinge/pivot origin、captured 接口、盖覆盖、坐地、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_shape | 3 | yes | yes | toe_pincher 为 parent 基线，rectangular/tapered 为 fork；仅 FOOTPRINT 改 |
| lid_mechanism | 5 | yes | yes | 1 / 2 / 2 / 1 REVOLUTE + 1 PRISMATIC（互斥主机构），切分轴向不同 |
| carry_handles | 3 | yes | yes | 无 joint / 不动 visual / N×REVOLUTE |
| handle_count (N) | 4 档（采样域 {2,4,6,8}，4 高频 / 8 长尾，仅 swing）| yes | yes | 拓扑维度，swing 时编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名；`carry_handles=swing_drop_bar` 时含 `("handle_count", f"n{N}")`，none/fixed 时不含
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling；N 仅在 swing 下采样、采样域 ⊆ 偶数[2,8]
- `resolve_config` 把 handle_count clamp 到偶数[2,8]，各 scale clamp 到声明范围；handle_swing / handle_spacing 为 conditional 随 carry_handles / N 解析；两条 inequality（把手不越界、盖覆盖 rim）在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（N 仅 swing；N 偶数且每侧清壁；盖闭合必覆盖 rim；fixed rail / foot 半盖不随盖动）
- 连续 scale clamp 后不破坏 hinge/pivot origin / captured bracket↔bail 接口 / 盖覆盖 / 坐地 / N 复制
- 关键 joint：full_side `lid_hinge` REVOLUTE axis≈(1,0,0)（abs(axis[0])>0.99）；split `lid_hinge_0`/`lid_hinge_1` 2×REVOLUTE 同侧 +X；double_leaf `lid_leaf_0_hinge`/`lid_leaf_1_hinge` 2×REVOLUTE 镜像 ±X；half_couch `head_lid_hinge` REVOLUTE +X（foot 半盖无 joint）；swing 每 `handle_{i}_pivot` REVOLUTE axis≈(±1,0,0)、lower=0/upper≈radians(85)
- captured-pin overlap：swing 的 `bracket_{i}_{arm_s}`↔`bail` element-scoped `allow_overlap`，照搬 swing 样本 run_tests L470-477
- copied object 遵循 `handle_{i}` / `bracket_{i}_{arm_s}` 命名 + 绝对式沿 X 等距对称 placement + 每把手独立 REVOLUTE
- grandfather：所有 lid hinge / handle pivot / captured bracket 接口省略 MatingContract，由 origin 检查 + allow_overlap 守
- 闭合姿态：所有盖 / 叶 q=0 闭合坐 rim（lower=0）；swing 把手 q=0 下垂

## Reject cases

- 把 4 个污染记录（rectangular_slab=打火机 / round_cylindrical=打火机 / clamp_locking=铸铁锅 / hinged_flip=铸铁锅）当 coffin candidate 采纳 → 不是棺木（已剔除，见顶部注记 + §5）。
- 把 N 当普通 int 参数、不进 slot_choice → 不同把手数 slot_choice 同形，损失拓扑维度（违反 §8/§9 硬要求）。
- 在 none / fixed_side_rails 下仍采样 / 编入 handle_count → N 仅 swing 生效；必须 gate。
- 把 fixed_side_rails 的 `carry_rail` 或 half_couch 的 `foot_lid_panel` 当独立活动 part 加 joint → 违反 Rule 1（不动结构应 inline 为 body visual）。
- handle_count 取奇数或不按每侧 N/2 对称 → 棺木把手现实上左右对称成对；须偶数。
- 把手 / fixed rail 的外侧 y 设成常量而非 `_half_width_at(x)` 派生 → toe-pincher / tapered 收锥处把手穿壁或悬空；须按该 x 壁半宽外推，fixed rail 还要按侧壁斜边 / 肩部折线分段。
- 盖 / 叶 rest pose 设成张开角而非 q=0 闭合坐 rim → current-pose 与 viewer 目检不符（所有样本 lower=0 闭合）。
- lid hinge / handle pivot origin 放在腔中心或任意点而非真实 rim 铰线 / pivot 硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 给 swing bracket↔bail captured overlap 补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- handle_spacing 过大致把手沿长边越界 → §7 第一条不等式 FAIL；须缩 gap / 拒绝重采。
- 把连续尺寸 / 颜色 / 材质（palette_style / footprint scale）当新 candidate 塞进 slot → 不是结构差异。
- 把 treasure_chest / 普通木箱语义混入（近方小箱 / 拱顶 / 无十字 / 无棺形 footprint）→ 出类。

## 与相邻类别的边界

- 不该混入：**treasure_chest / 珠宝箱 / 工具箱**——同为 hinged-lid 箱但近方比例、常带拱顶盖 + 锁扣；棺木身份在长条棺形 footprint + 头端拉丁十字 + strap 板 + 入殓尺度（~1.9 m），缺即出类。如需 treasure_chest 单独 slug（已存在 `Bag_Suitcase_Treasure_chest.md`）。
- 不该混入：**storage box / crate / 普通木箱**——无棺形收肩 / 无十字 / 非入殓比例。
- 不该混入：**cauldron / 打火机等换盖小物**（本仓库恰有同 slug 片段污染样本）——主体非长条棺箱、尺度与主运动 spine 完全不同；已在来源剔除。
- 不该混入：**棺架 / 灵车 / 墓碑**——棺木本体之外的承载 / 运输 / 标记物。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) 已剔除 4 个污染记录（打火机×2 + 铸铁锅×2），来源池 = 8 个真·棺木；(2) body_shape 建模为 FOOTPRINT mesh 维度（非串联 slot）；(3) handle_count N_range=[2,8] 偶数、仅 swing 生效、编入 slot_choice；(4) lid split/double 为固定 2 段 / 2 叶（非可变 multiplicity）；(5) vertical_lift_lid 为单一 PRISMATIC +Z，不与旋转重合；(6) Topology target 90<300 的说明是否接受（本小类真实结构上限）；(7) 5 个 palette_style colorway 是否合理；(8) fixed_rails / foot 半盖 Rule 1 inline 无 joint 是否符合期望）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：`_offset_polygon`/`_extrude_poly`/`_x_slab`/`_body_shell`/`_body_strap_band`/`_lid_panel`/`_lid_strap`（全 8 样本同源，按 `FOOTPRINT` 切换 footprint）；split 加 `_lid_panel_half`+`_x_clip_box`；double_leaf 加 `_compute_leaf_local_polygons`+`_clip_polygon_*`；half_couch 加 `_foot_lid_panel`/`_foot_lid_strap`（inline body）；fixed_rails 加 `_carry_rail`；swing 加 `_bail_handle_cq`+`_half_width_at`（pivot_y 派生）。
- captured 接口 allow_overlap：仅 swing 需要——`run_coffin_tests` 里逐把手补 element-scoped `allow_overlap(body, handle_{i}, elem_a=f"bracket_{i}_{arm_s}", elem_b="bail")`，照搬 swing 样本 run_tests L470-477。其余机构无 captured overlap。
- conditional 范围解析顺序：先采 body_shape / lid_mechanism / carry_handles → 若 swing 解析 handle_count(偶数[2,8]) / handle_swing / handle_spacing(N≥4) → 采 length/width/height/angle independent scale → 派生（hinge z 随 height、pivot_y 随 width 与 `_half_width_at`、strap/handle x 随 length）→ 投影两条 inequality（把手不越界、盖覆盖 rim）。
- N 退化：N=2 即每侧 1 把（仍走 `for side in (-1,1): for x_st in HANDLE_XS[:1]` 等价；HANDLE_XS 长度 = N/2）。
- foot 半盖 / carry rail 是 body inline visual（Rule 1），盖开 pose 下必须静止（half_couch run_tests / fixed_rails L438-440 已验）。
- 参考模板：`articraft_template_authoring/specs_modular_v1/Accessories_Cushion.md`（**最近拓扑**：同为 mixed = 固定 named slots(footprint × lid_mechanism × interior) + 1 根 multiplicity 轴编入 `("count", f"n{N}")` + 绝对式 placement + 共享 mesh 复用 + 兼容矩阵 gating + captured-pin allow_overlap；本类直接同构改编，把 interior 轴换成 carry_handles、pan_count 换成 handle_count）；`Bag_Suitcase_Treasure_chest.md`（同为 hinged-lid 箱，盖坐 rim + REVOLUTE 范式）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C（parent 基线）| toe_pincher_hex + full_side_hinge + none | rec_model-a-rustic-toe-pincher-…_3d5f4f7f | `FOOTPRINT` L55-62 / `_body_shell` L102-115 / `lid`+`lid_hinge` L171-207 / 闭合检查 L268-278 | toe-pincher footprint + full_side_hinge 基线 + 共享 body/lid helper 范式 |
| S2 | A | rectangular_casket footprint | rec_variant-body-shape-rectangular-casket-…_477ccc1d | `FOOTPRINT` L51-56（恒宽）/ `_body_shell` L96-109 | 矩形 casket footprint（part 树不变）|
| S3 | A | tapered_trapezoid footprint | rec_variant-body-shape-tapered-trapezoid-…_26a4798a | `FOOTPRINT` L56-61（单调收锥）| 锥形梯形 footprint（part 树不变）|
| S4 | B | split_two_panel | rec_variant-lid-mechanism-split-two-panel-…_1d8d2709 | `LID_PANEL_X_RANGES` L146-149 / `_lid_panel_half` L152-161 / `lid_{i}`+`lid_hinge_{i}` L203-256 | 两段盖（2×REVOLUTE 同侧 rim）|
| S5 | B | double_leaf_wings | rec_variant-lid-mechanism-double-leaf-wings-…_de26f9e8 | `_compute_leaf_local_polygons` L165 / `leaf_configs` L235-240 / `lid_leaf_{i}`+`lid_leaf_{i}_hinge` L245-298 | 双叶对开（2×REVOLUTE 镜像 ±X）|
| S6 | B | half_couch_head_only | rec_variant-lid-mechanism-half-couch-head-only-…_0d84ee10 | `head_lid` L270-300 / foot inline L253-267 / `head_lid_hinge` L304-314 | 头半 hinged + 脚半固定（1×REVOLUTE + inline 不动盖）|
| S7 | C | fixed_side_rails | rec_variant-carry-handles-fixed-side-rails-…_b642913b | `_carry_rail` L136-164 / `carry_rail_{i}` L213-219 / 不动检查 L438-440 | 固定 carry rail（inline body visual，Rule 1）|
| S8 | C（multiplicity）| swing_drop_bar_handles | rec_variant-carry-handles-swing-drop-bar-handles-…_de2a3aba | `HANDLE_XS` L54 / `_bail_handle_cq` L173-186 / `handle_{i}`+`bracket_{i}_{arm_s}`+`handle_{i}_pivot` L253-294 / allow_overlap L470-477 | N×摆动把手 copy-logic 源（独立 REVOLUTE + captured bracket）|
</content>
</invoke>
