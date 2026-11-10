# fire_cabinet (street/utility upright metal cabinet, labeled "Fire cabinet") — Modular Spec

> 来源小类：`picture/Urban Environment/Fire cabinet`（articraft_data 上游 Urban Environment/Fire cabinet fork-variant pool）。
> 源 source map：`articraft_data/picture_expansion/template_source_maps/Urban_Environment__Fire_Other_Cabinet.md`。
> 1 母资产 + 9 个 converged fork 变体 = 10 个 5★ 样本，全部读 `model.py` 全文（见 §5）。
> 引用 `model.py:Lx-Ly` 来自各样本 `arti-template/data/records/<id>/revisions/rev_000001/model.py`，
> 以 part / joint / helper **名字** 为准（`cabinet` / `drawer_{i}` / `cabinet_to_drawer_{i}` / `door` /
> `door_{left,right}` / `cabinet_to_door` / `cabinet_to_door_{left,right}` / `shutter` / `cabinet_to_shutter` /
> `slat_{i}` / `lift_bar` / `shelf_{i}` / `face_rail_{i}` / `face_stile_{tag}` / `side_channel_{tag}` /
> `leg_{i}` / `caster_{i}` / `cabinet_to_caster_{i}` / `glass_pane` / `louver_slat_{i}` / `_add_shutter_slat` /
> `_add_caster_visuals` / `_louver_slat` 等），行号仅作定位（重排后以名字为准）。
> **身份歧义已上报，见 §3 与 §11 末尾的 REVIEWER FLAG。**

## 元信息
| 项 | 值 |
|---|---|
| slug | `fire_cabinet` |
| template path | `agent/templates/Urban_Environment_Fire_cabinet.py` |
| test path (optional) | `tests/agent/test_fire_cabinet_template.py`（不写，sweep-pipeline 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（共享 carcass 壳 `cabinet` 作为单一接地根 → closure 主机构 slot[N 复制] + front-face style + base/support 三个并行子层挂到 carcass）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 1 parent + 9 converged fork 变体 = 10 |
| read_count | 10（全部读 `model.py` 全文）|
| read_scope | all 5-star samples in this category（combinatorial fork pool：parent 全读 + 每个变体读其差异层：closure type / closure-N loop / front-face style / base support）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 slot 表与 §14 |

逐样本要点（采纳归属）：
- **P1 parent**（`rec_tall-four-drawer-metal-filing-cabinet-in-dark-ch_20260608_171125_602483_053b2c58`）：暗炭色钣金四抽屉立式柜。`cabinet` 为单根接地壳——`base_plinth`(凹底座) + `bottom_panel`/`top_panel`/`back_wall` + `side_wall_{left,right}` + 前框 `face_rail_{i}`(loop `range(n+1)` `L119-L126`) + `face_stile_{tag}` + 每抽屉两条 `runner_{i}_{side}`；唯一活动子件 = 4 只 `drawer_{i}` 开顶钣金托盘（`bottom_floor`+`side_wall_{l,r}`+`back_wall`+`drawer_face`+`handle_surround`+`pull_handle`+`label_holder`），经 `cabinet_to_drawer_{i}` **PRISMATIC** 沿 +X 前拉 0..travel（`L155-L247`，joint `L239-L247`）。**采纳为 closure=n_sliding_drawers 基线（N=4）+ carcass 壳共享件 + base=recessed_plinth 基线 + front=solid_steel 基线 + palette charcoal 基线**。drawer loop `L155-L247`。
- **drawers3**（`rec_fire_cabinet_var_drawers3`）：parent 结构，`n_drawers = 3`（`L46`），同一 face_rail/runner/drawer 循环按 N 自适应分层，`drawer_face_h=(stack_h - rail*(n+1))/n`（`L113`）。**采纳为 closure_multiplicity_N 下端点 N=3**。
- **drawers5**（`rec_fire_cabinet_var_drawers5`）：parent 结构，`n_drawers = 5`（`L46`），更密的抽屉栈。**采纳为 closure_multiplicity_N 上端点 N=5 + N 等距分层规范公式**。
- **hinged_door**（`rec_fire_cabinet_var_hinged_door`）：抽屉栈换为单扇全高 `door`，绑左前竖边 `cabinet_to_door` **REVOLUTE** +Z 0..2.3（`L253-L261`）；门面 `door_panel`+`door_emboss`+`handle_surround`+`pull_handle`+两只 `BarrelHingeGeometry` `hinge_{i}`（`mesh_from_geometry`，`L212-L239`）；carcass 前框改为周边 `face_rail_{top,bottom}`+`face_stile_{tag}`（`L104-L126`）+ 内部 2 块 FIXED `shelf_{i}`（loop `L133-L150`）+ `shelf_bracket_{i}_{side}`。**采纳为 closure=single_hinged_door + 周边门框 carcass 变体 + interior shelves N=2 复制契约 + barrel-hinge interface**。
- **double_doors**（`rec_fire_cabinet_var_double_doors`）：中缝对开两窄扇 `door_{left,right}`（`build` 循环按 `s=±1`、`axis_z=±1`，`L139-L194`），各自 `cabinet_to_door_{left,right}` **REVOLUTE**（left axis +Z / right axis -Z）从各自侧缘外摆 0..1.5；内部 3 块 FIXED `shelf_{i}`（loop `L119-L126`）；闭合时两扇中缝 `center_gap=0.003` 相接（test `doors_center_gap_small` `L271-L275`）。**采纳为 closure=double_doors + 双 REVOLUTE 对开接口 + interior shelves N=3**。
- **roller_shutter**（`rec_fire_cabinet_var_roller_shutter`）：前开口分上固定板 `fixed_front_panel`(45%) + 下卷帘区；`shutter` 部件 = `lift_bar` + N 片 `slat_{i}`（helper `_add_shutter_slat` `L27-L40`，loop `L235-L241`，相邻 slat 重叠 2mm 互锁），经 `cabinet_to_shutter` **PRISMATIC** 沿 +Z 上滑 0..0.50（`L258-L268`）；carcass 加 `side_channel_{tag}` 竖导轨（`L125-L133`）+ `meeting_rail`+`top_fascia`+`bottom_threshold`+`interior_back`。**采纳为 closure=roller_shutter + 竖向 PRISMATIC + slat 复制契约 + 侧导轨 carcass 变体**。注意 `n_slats=int(available/pitch)` 由几何派生（`L214`），非独立 N。
- **glazed_door**（`rec_fire_cabinet_var_glazed_door`）：单扇 REVOLUTE 门（同 hinged_door joint 拓扑 `L249-L257`），但门面 = 钢框 `frame_stile_{l,r}`+`frame_rail_{top,bottom}` 嵌透明 `glass_pane`（`glass_tint` rgba alpha=0.35，`L206-L218`）+ `edge_pull` + `fire_label`；carcass 用 `Cylinder` `hinge_barrel_{i}` 暴露铰桶（`L140-L149`）+ 2 块 `shelf_{i}`+`shelf_bracket`。**采纳为 front_face=glazed_window（door-central transparent pane in steel frame）+ exposed cylinder hinge-barrel 变体**。
- **louvered_door**（`rec_fire_cabinet_var_louvered_door`）：单扇 REVOLUTE 门（joint `L227-L237`，axis -Z），门面 = `door_panel` 背板 + 35 片角度叶片 `louver_slat_{i}`（helper `_louver_slat` `L34-L36`，loop `L188-L198`，`rpy=(0,35°,0)` 倾角）+ `edge_pull`；carcass 用连续 `Cylinder` `hinge_barrel`(piano hinge `L132-L142`) + 2 块 `shelf_{i}`。**采纳为 front_face=louvered（door face = regular stack of angled vent blades）+ louver 复制契约 + piano-hinge 变体**。
- **legs**（`rec_fire_cabinet_var_legs`）：parent 抽屉柜，但 `base_plinth` 换为 4 条 CadQuery 钢管腿 `leg_{i}`（`cq.Workplane` 圆管 + 圆脚板，`mesh_from_cadquery` `L63-L85`），`body_bottom_z=leg_h=0.120` 把壳抬离地面（`L87`）；其余 carcass+drawer 同 parent。**采纳为 base=steel_legs（4 角 FIXED 腿，body 抬升）+ leg mesh helper**。
- **casters**（`rec_fire_cabinet_var_casters`）：parent 抽屉柜，4 个万向脚轮 `caster_{i}`（helper `_add_caster_visuals`：`mounting_plate`+`swivel_ring`+`fork_stem`+`fork_bridge`+`fork_leg_{i}`+`wheel`+`hub_cap_{i}`，`L32-L117`），各自 `cabinet_to_caster_{i}` **CONTINUOUS** 绕 Z 旋转（`L261-L268`，`MotionLimits(effort=2,velocity=4)` 无 lower/upper）；`CASTER_H=0.080` 抬升壳；同时保留 4 抽屉 PRISMATIC。**采纳为 base=casters（4 角 CONTINUOUS 万向脚轮，body 抬升）+ caster part/joint 复制契约**。

## 核心身份

立式钣金街用/工具金属柜（标注 "Fire cabinet"，实为多抽屉/铰门金属箱体，filing-cabinet 形）：一只暗炭色前开口空腔壳 `cabinet`（`base_plinth`/`bottom_panel`/`top_panel`/`back_wall`/`side_wall_{l,r}` + 前框）作为**单一接地根**，正面由**真实非固定关节**封闭——这是定义性 joint：

- 抽屉 `drawer_{i}` 沿 +X **PRISMATIC** 前拉（baseline）；或
- 单扇/双扇 `door` 绕竖 Z 轴 **REVOLUTE** 外摆；或
- 卷帘 `shutter`（slat 栈 + lift_bar）沿 +Z **PRISMATIC** 上滑。

base/support 决定壳如何接地：凹底座 `base_plinth`（z=0）/ 4 条钢腿 `leg_{i}` / 4 个万向脚轮 `caster_{i}`（**CONTINUOUS** 绕 Z）。front-face style 决定封闭面外观：实心钢面 / 中央玻璃窗 / 角度百叶。

默认成熟域：立式自立柜（~0.38W(Y) × 0.60D(X) × 1.30H(Z) m，`height_z > width_y * 2.5` 立式比例），暗炭钢色。**核心运动身份 = `cabinet`(root) → 至少一个真实活动 closure（PRISMATIC 抽屉/卷帘 或 REVOLUTE 门）暴露内腔**。任何 seed 必须保留：① 单根接地 `cabinet` 壳，min-z≈0，立式高瘦比例；② ≥1 个非固定 closure joint（PRISMATIC 或 REVOLUTE）；③ 闭合姿态下 closure 面在壳前 x=D 处齐平。

不该混入（见 §11）：
- 把 `pull_handle` / `label_holder` / `top_badge` / `fire_label` / `door_emboss` 当作独立 slot——它们是 module-local 固定 visual / 装饰，不是 slot 也不是 candidate。
- 内部 `shelf_{i}` / 收纳分隔——非活动内部细节；它是 door-closure module 内的 FIXED 复制 fitment，不是独立 closure slot（但其 N 进 multiplicity 审计）。
- 单纯换色/换材质/换尺寸——禁止作为 candidate 或 slot。

## 槽位 + 候选模块表

### Slot A：closure_mechanism（封闭机构，主机构槽——壳前如何打开，定义性 joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| n_sliding_drawers | parent / drawers3 / drawers5 | parent L155-L247（drawer loop + `cabinet_to_drawer_{i}` PRISMATIC L239-L247）；drawers3 `n_drawers=3` L46；drawers5 `n_drawers=5` L46 | eligible if compatible | N 只开顶钣金托盘 `drawer_{i}`（`bottom_floor`+`side_wall_{l,r}`+`back_wall`+`drawer_face`+pull+label），各自 `cabinet_to_drawer_{i}` **PRISMATIC** +X 0..travel；carcass 前框 = `face_rail_{i}`(loop range(N+1)) + `face_stile_{tag}` + 每抽屉 `runner_{i}_{side}` |
| single_hinged_door | hinged_door | L162-L261（door part + `cabinet_to_door` REVOLUTE L253-L261）；shelves L133-L150；周边框 L104-L126 | eligible if compatible | 单扇全高 `door`（`door_panel`+`door_emboss`+pull+两只 `BarrelHingeGeometry` `hinge_{i}`），1 个 `cabinet_to_door` **REVOLUTE** 绕左前竖边 +Z 0..2.3；carcass = 周边 `face_rail_{top,bottom}`+`face_stile_{tag}` + 内部 FIXED `shelf_{i}`(N=2) + `shelf_bracket` |
| double_doors | double_doors | L128-L196（`door_{left,right}` 循环 + 双 `cabinet_to_door_{tag}` REVOLUTE L183-L194）；shelves L119-L126 | eligible if compatible | 中缝对开两窄扇 `door_{left,right}`（各 `door_panel`+pull），`cabinet_to_door_left` axis +Z / `cabinet_to_door_right` axis -Z 各自 **REVOLUTE** 从侧缘外摆 0..1.5；闭合 `center_gap=0.003` 相接；内部 FIXED `shelf_{i}`(N=3) |
| roller_shutter | roller_shutter | L196-L268（`shutter` part + `_add_shutter_slat` L27-L40 + slat loop L235-L241 + `cabinet_to_shutter` PRISMATIC L258-L268）；carcass 导轨 L109-L184 | eligible if compatible | `shutter` = `lift_bar` + N 片互锁 `slat_{i}`，经 `cabinet_to_shutter` **PRISMATIC** 沿 +Z 上滑 0..0.50；carcass = 上固定 `fixed_front_panel`(45%) + `side_channel_{tag}` 竖导轨 + `meeting_rail`/`top_fascia`/`bottom_threshold`/`interior_back`；`n_slats` 由几何派生非独立 N |

### Slot B：front_face_style（封闭面外观——仅对 hinged_door closure 生效；glazing/venting）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| solid_steel | parent / hinged_door / double_doors | hinged_door door_panel L176-L194；double_doors door_panel L145-L152；drawers drawer_face L204-L209 | eligible if compatible | 不透明钢面 / 实心门板 / 抽屉面（`door_panel` 或 `drawer_face` 实心 Box + 可选 `door_emboss` 加强筋）；默认 face style |
| glazed_window | glazed_door | L164-L238（钢框 `frame_stile_{l,r}`/`frame_rail_{top,bottom}` 嵌透明 `glass_pane` L206-L218，`glass_tint` alpha=0.35）；exposed `hinge_barrel_{i}` L140-L149 | eligible if compatible | 单扇 REVOLUTE 门中央 = 透明 `glass_pane`（半透明材质）框在钢框 `frame_stile`/`frame_rail` 内（玻璃座入 rebate）+ `edge_pull`+`fire_label`；carcass 用 `Cylinder` `hinge_barrel_{i}` 暴露铰桶 |
| louvered | louvered_door | L159-L237（`door_panel` 背板 + `_louver_slat` L34-L36 + 35 片 `louver_slat_{i}` loop L188-L198 `rpy=(0,35°,0)` + `cabinet_to_door` REVOLUTE L227-L237）；piano `hinge_barrel` L132-L142 | eligible if compatible | 单扇 REVOLUTE 门面 = `door_panel` 背板 + 规则角度叶片栈 `louver_slat_{i}`（倾斜 35° 通风百叶，loop 复制）+ `edge_pull`；carcass 用连续 `Cylinder` `hinge_barrel`(piano hinge) |

### Slot C：base_support（壳如何接地）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| recessed_plinth | parent（+ 全 door 变体默认）| parent `base_plinth` L54-L59；`body_bottom_z=plinth_h` L61 | eligible if compatible | 凹进踢脚底座 `base_plinth`（z=0 接地，inset 0.020），壳 `bottom_panel` 落在底座顶；默认 base |
| steel_legs | legs | L62-L85（`cq.Workplane` 圆管 + 圆脚板 `mesh_from_cadquery` `leg_{i}` 4 角）；`body_bottom_z=leg_h=0.120` L87 | eligible if compatible | 4 条直钢管腿 `leg_{i}`（圆管 + 圆脚板）FIXED 在壳 4 角底，把 `cabinet` 抬升 leg_h=0.120 离地；腿底 z=0 |
| casters | casters | L32-L117（`_add_caster_visuals` 整组 caster 几何）+ L235-L269（`caster_{i}` part + `cabinet_to_caster_{i}` CONTINUOUS L261-L268）；`CASTER_H=0.080` L125 | eligible if compatible | 4 个万向脚轮 `caster_{i}`（mounting_plate+swivel_ring+fork+wheel+hub_cap），各自 `cabinet_to_caster_{i}` **CONTINUOUS** 绕 Z 旋转（无 lower/upper）；壳抬升 CASTER_H=0.080，轮底 z=0 |

> Slot B 兼容性注记：`front_face_style` 仅对 `single_hinged_door` closure 有意义（glazed/louvered 是「门面变体」）。`n_sliding_drawers`/`double_doors`/`roller_shutter` closure 强制 `front_face_style=solid_steel`（见 §9 compatibility matrix）。glazed/louvered 各自带自己的 carcass 铰桶变体（exposed cylinder / piano hinge），由 face module 携带，不另开 slot。

## 槽位图（slot graph）

pattern: `parallel_children`（共享 carcass 壳 `cabinet` = 单一接地根）

```
                         [base_support C]                      接地：plinth z=0 / leg 底 z=0 / wheel 底 z=0
                              |  FIXED(plinth/legs) 或 CONTINUOUS(casters, axis +Z)
                              |  接口：壳 bottom_panel 底面 @ body_bottom_z（plinth_h / leg_h / CASTER_H）
                              v
   cabinet (root carcass shell)  ──────────────────────────────►  front face plane @ x=D
     base_plinth/bottom/top/back/side_walls + 前框 face_rail/stile      |
                              |                                          |  闭合时 closure 面齐平 x=D
            closure 主机构 [Slot A, multiplicity N 复制]                  |
                              |                                          v
        ┌── n_sliding_drawers: cabinet_to_drawer_{i} PRISMATIC axis=+X, origin=(D,0,cz_i), 0..travel  [N 复制]
        ├── single_hinged_door: cabinet_to_door REVOLUTE axis=+Z, origin=(D, hinge_y=W/2-wall, z_mid), 0..~2.3
        │        └── front_face_style [Slot B]：solid_steel / glazed_window(glass_pane) / louvered(louver_slat_{i})
        ├── double_doors: cabinet_to_door_{left,right} REVOLUTE axis=±Z, origin=(D, ±(W/2-wall), open_bot_z), 0..1.5  [2 扇对开]
        └── roller_shutter: cabinet_to_shutter PRISMATIC axis=+Z, origin=(slat_x≈D, 0, joint_z), 0..0.50  [slat 栈派生 N]
                              |
                interior fitment（FIXED `shelf_{i}` 复制，仅 door closure 携带，N=2/3）
```

接口点位：
- **base→carcass**：base module 把壳 `bottom_panel` 底面定位到 `body_bottom_z`（plinth_h=0.060 / leg_h=0.120 / CASTER_H=0.080），caster 用 `cabinet_to_caster_{i}` CONTINUOUS（origin 在壳底角 z=body_bottom_z，axis +Z），plinth/legs 为 FIXED carcass visual（不出关节）。base module **不改变** carcass 上方几何与 closure 接口。
- **closure→carcass**：所有 closure joint origin 锚在壳前平面 x=D。PRISMATIC 抽屉 axis=+X、origin=(D,0,cz_i)；REVOLUTE 门 axis=±Z、origin=(D, ±(W/2-wall), z)；PRISMATIC 卷帘 axis=+Z、origin≈(D,0,joint_z)。闭合姿态（q=0）closure 面 max-x 在壳前 x=D 处齐平（test `*_flush_closed`）。
- **front_face→door**：face style 是 single_hinged_door module 内部的门面构造选择（solid 门板 / glass_pane in steel frame / louver_slat 栈），不跨 part；它决定 door part 的 visual 集合与 carcass 铰桶形态（barrel mesh / exposed cylinder / piano cylinder）。
- 互斥/派生：Slot B 仅在 Slot A=single_hinged_door 时激活；其它 closure 强制 solid_steel。Slot A=roller_shutter 时 N 由几何派生（不暴露 count param）。base Slot C 与 closure Slot A 完全正交（任意组合合法）。

## 每槽位 Module Emits / Interfaces

### Slot A / module n_sliding_drawers
| emits | 描述 | 来源 |
|---|---|---|
| parts | N × `drawer_{i}`（每只：`bottom_floor`/`side_wall_{l,r}`/`back_wall`/`drawer_face`/`handle_surround`/`pull_handle`/`label_holder`）| parent L155-L229 |
| internal joints | N × `cabinet_to_drawer_{i}` **PRISMATIC** axis=(1,0,0) origin=(D,0,cz_i) lower=0 upper=travel(=drawer_depth*0.72) | parent L239-L247 |
| carcass visuals (parent-owned) | `face_rail_{i}`(loop range(N+1)) + `face_stile_{tag}` + `runner_{i}_{side}` | parent L119-L169 |
| upstream interface | 挂到 root `cabinet`；每抽屉竖向中心 `cz_i=open_bot_z+rail+drawer_face_h/2+i*(drawer_face_h+rail)` | parent L159 |
| downstream interface | closure 面 = `drawer_face` 在 x=D 齐平（闭合），开启沿 +X 前拉并保留后插（`retains_insertion`）| parent L279-L353 |

### Slot A / module single_hinged_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door`（`door_panel`+`door_emboss`+`handle_surround`+`pull_handle`+`hinge_{0,1}`）；front_face style 决定门面 visual 集合 | hinged_door L162-L239 |
| internal joints | 1 × `cabinet_to_door` **REVOLUTE** axis=(0,0,1) origin=(D, hinge_y=W/2-wall, z_mid) lower=0 upper≈2.3 | hinged_door L253-L261 |
| carcass visuals | 周边 `face_rail_{top,bottom}`+`face_stile_{tag}` + FIXED `shelf_{i}`(N=2)+`shelf_bracket_{i}_{side}` | hinged_door L104-L150 |
| upstream interface | 铰线在壳左前竖边 y=W/2-wall，门 part frame 在铰线 | hinged_door L246-L251 |
| downstream interface | 闭合门面在 x=D 齐平、laps over right stile（`expect_contact`/`expect_overlap` + element-scoped `allow_overlap` 铰桶/stile）| hinged_door L354-L388 |

### Slot A / module double_doors
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door_{left,right}`（各 `door_panel`+`handle_surround`+`pull_handle`）| double_doors L139-L170 |
| internal joints | `cabinet_to_door_left` REVOLUTE axis=(0,0,+1)；`cabinet_to_door_right` axis=(0,0,-1)；origin=(D, s*(W/2-wall), open_bot_z) lower=0 upper=1.5 | double_doors L183-L194 |
| carcass visuals | FIXED `shelf_{i}`(N=3) | double_doors L119-L126 |
| upstream interface | 两铰线在壳左右前竖边，门向中缝延伸 | double_doors L131-L152 |
| downstream interface | 闭合两扇在 x=D 齐平、中缝 `center_gap=0.003` 相接（`doors_center_gap_small`）；外摆 panel max-x +X | double_doors L239-L275 |

### Slot A / module roller_shutter
| emits | 描述 | 来源 |
|---|---|---|
| parts | `shutter`（`lift_bar` + N 片 `slat_{i}`，helper `_add_shutter_slat`）| roller_shutter L27-L40, L224-L241 |
| internal joints | 1 × `cabinet_to_shutter` **PRISMATIC** axis=(0,0,1) origin≈(D,0,joint_z) lower=0 upper=0.50 | roller_shutter L258-L268 |
| carcass visuals | `fixed_front_panel`(上 45%) + `side_channel_{tag}` 竖导轨 + `meeting_rail`/`top_fascia`/`bottom_threshold`/`interior_back` | roller_shutter L122-L184 |
| upstream interface | 卷帘下区在壳前开口下部，slat 在 x≈D-0.012 略后于固定板（升起 slat 藏于固定板后）| roller_shutter L216-L222 |
| downstream interface | 闭合卷帘盖下开口，开启沿 +Z 上滑露开口（`shutter_slides_upward`/`shutter_reveals_opening`）；`expect_within` footprint | roller_shutter L348-L375 |

### Slot B / module solid_steel
| emits | 描述 | 来源 |
|---|---|---|
| parts(visuals on door) | 实心 `door_panel`(+可选 `door_emboss`) 或 `drawer_face`；无玻璃/无叶片 | hinged_door L176-L194 |
| interface | 门面 module-local；不改 closure joint | hinged_door L176 |

### Slot B / module glazed_window
| emits | 描述 | 来源 |
|---|---|---|
| parts(visuals on door) | 钢框 `frame_stile_{l,r}`/`frame_rail_{top,bottom}` + 透明 `glass_pane`(`glass_tint` alpha=0.35) + `edge_pull` + `fire_label` | glazed_door L177-L238 |
| carcass visuals | exposed `Cylinder` `hinge_barrel_{i}`（2 段铰桶）| glazed_door L140-L149 |
| interface | 玻璃座入门框 rebate（`expect_overlap` glass vs rails/stile，door-local）| glazed_door L310-L319 |

### Slot B / module louvered
| emits | 描述 | 来源 |
|---|---|---|
| parts(visuals on door) | `door_panel` 背板 + N 片角度 `louver_slat_{i}`(`rpy=(0,35°,0)`, helper `_louver_slat`) + `edge_pull` | louvered_door L169-L210 |
| carcass visuals | 连续 `Cylinder` `hinge_barrel`(piano hinge) | louvered_door L132-L142 |
| interface | 百叶为门面装饰栈，门仍单轴 REVOLUTE；piano-hinge element-scoped `allow_overlap` | louvered_door L375-L390 |

### Slot C / module recessed_plinth
| emits | 描述 | 来源 |
|---|---|---|
| carcass visual | `base_plinth`（凹底座 Box，z=0 接地）；`body_bottom_z=plinth_h=0.060` | parent L54-L61 |
| interface | 壳 `bottom_panel` 底面落在底座顶；无关节 | parent L64-L70 |

### Slot C / module steel_legs
| emits | 描述 | 来源 |
|---|---|---|
| carcass visuals | 4 × `leg_{i}`（CadQuery 圆管+圆脚板 mesh，4 角）；`body_bottom_z=leg_h=0.120` | legs L62-L87 |
| interface | 腿底 z=0，壳抬升 leg_h；FIXED（无关节）| legs L78-L87 |

### Slot C / module casters
| emits | 描述 | 来源 |
|---|---|---|
| parts | 4 × `caster_{i}`（`_add_caster_visuals`：plate/ring/stem/bridge/fork_leg/wheel/hub_cap）| casters L32-L117, L245-L257 |
| internal joints | 4 × `cabinet_to_caster_{i}` **CONTINUOUS** axis=(0,0,1) origin=(corner, body_bottom_z) 无 lower/upper | casters L261-L268 |
| interface | 轮底 z=0，壳抬升 CASTER_H=0.080；caster part frame 在壳底角 | casters L155, L259-L266 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| closure_mechanism | enum | {n_sliding_drawers, single_hinged_door, double_doors, roller_shutter} | n_sliding_drawers | choice | deterministic procedural sampler 选 | Slot A 表 |
| front_face_style | enum | {solid_steel, glazed_window, louvered} | solid_steel | conditional | 仅 closure==single_hinged_door 时可取 glazed/louvered；否则强制 solid_steel | Slot B 表 |
| base_support | enum | {recessed_plinth, steel_legs, casters} | recessed_plinth | choice | 与 closure 正交；任意组合合法 | Slot C 表 |
| n_drawers | int | [3,5]（产品域；测试偏小）| 4 | conditional | 仅 closure==n_sliding_drawers 时有效；逐 N 加权采样 | parent/drawers3/drawers5 L46 |
| n_shelves | int | door closure 内部 FIXED 层数：single→{2}, double→{3} | — | conditional | 由 closure 选择派生（非独立采样）| hinged L133 / double L45,L119 |
| cabinet_width_scale | float | [0.90, 1.12] | 1.0 | independent | W=0.380*scale；clamp；不破坏 `upright`(h>w*2.5) 与 footprint | parent L38 |
| cabinet_height_scale | float | [0.92, 1.10] | 1.0 | independent | H=1.300*scale；clamp 保证 top>1.2 且 h>w*2.5 | parent L40 |
| cabinet_depth_scale | float | [0.92, 1.08] | 1.0 | independent | D=0.600*scale；闭合 closure 面随 D 重锚到 x=D | parent L39 |
| drawer_travel_ratio | float | [0.60, 0.78] | 0.72 | equation | `travel = drawer_depth * ratio`；drawer_depth=D-wall-0.030 随 depth_scale | parent L151 |
| shutter_travel | float | [0.40, 0.55] | 0.50 | inequality | 升起 slat 顶 ≤ open_top_z（不穿顶板）；越界回缩 | roller_shutter L256 |
| door_open_upper | float | [1.5, 2.35] rad | 2.3(single)/1.5(double) | independent | REVOLUTE upper；不影响闭合拓扑 | hinged L260 / double L192 |
| base_lift | float | derived | plinth_h/leg_h/CASTER_H | equation | `body_bottom_z = {0.060, 0.120, 0.080}[base_support]`；上方几何不变 | parent L61 / legs L87 / casters L155 |
| palette_style | enum | {charcoal_oem, fire_red_alarm, municipal_grey, hi_vis_yellow, weathered_green, stainless_brushed} | charcoal_oem | choice | 仅改 material rgba（壳/面/底/把手/badge 协调配色）；不改拓扑 | parent L30-L35 |
| (—) | constraint | — | — | inequality | closure 面闭合 max-x ≈ D（齐平容差 <0.025）；违反回缩门/抽屉/卷帘锚点 | 各 `*_flush_closed` test |
| (—) | constraint | — | — | inequality | drawer/shelf/louver/slat 栈在 cavity 高度内等距，不越 top/bottom panel | parent L113 / hinged L134 |

palette_style 6 个 colorway（≥3 目标，落在 4-6）：
- **charcoal_oem**：暗炭钢 `charcoal=(0.15,0.16,0.18)` + `charcoal_dark` 底座/把手 + `badge_red`（baseline，parent）。
- **fire_red_alarm**：消防红壳 `(0.62,0.12,0.10)` + 暗红底座 + 白/不锈门框 + 黄 badge（呼应 "Fire cabinet" 标签语义）。
- **municipal_grey**：市政浅灰 `(0.55,0.57,0.60)` 壳 + 深灰底座 + 黑把手 + 红 badge。
- **hi_vis_yellow**：工业警示黄 `(0.82,0.72,0.12)` 壳 + 黑底座/导轨 + 黑把手（街用工具柜）。
- **weathered_green**：橄榄/做旧绿 `(0.28,0.34,0.26)` 壳 + 暗绿底座 + 黄铜 label + 红 badge。
- **stainless_brushed**：拉丝不锈 `(0.70,0.72,0.74)` 壳 + 深灰底座 + 黑把手 + 蓝 badge。

## Multiplicity / Copy Logic

本模板有 **2 根条件 multiplicity 轴**（各按 closure 选择激活；非全程并存）。

### 轴 1：drawer_count（仅 closure==n_sliding_drawers）
- `count_param`：`n_drawers`
- `N_range`：`[3,5]`（本小类抽屉柜产品域；测试偏小、产品全程；source 给出 N=3/4/5 三档）
- sampling domain：逐 N 加权（N=4 baseline 高频；N=3/5 次之；不外推 >5，因高瘦壳超过 ~6 抽屉面高过薄、不符 source 比例）
- copied object：`drawer_{i}` 开顶钣金托盘（含 face/pull/label）+ carcass 侧 `face_rail_{i}`(range(N+1)) + `runner_{i}_{side}`
- naming：`drawer_{i}` / `cabinet_to_drawer_{i}` / `face_rail_{i}` / `runner_{i}_{left,right}`
- placement：`cz_i=open_bot_z+rail+drawer_face_h/2+i*(drawer_face_h+rail)`，`drawer_face_h=(stack_h-rail*(N+1))/N`（等距分层）
- joint policy：每只 `cabinet_to_drawer_{i}` PRISMATIC axis=+X origin=(D,0,cz_i) lower=0 upper=travel
- source/gating：parent(N=4)/drawers3(N=3)/drawers5(N=5)；仅当 closure=n_sliding_drawers 激活

### 轴 2：shelf_count（仅 closure∈{single_hinged_door, double_doors}，FIXED 内部 fitment）
- `count_param`：`n_shelves`
- `N_range`：`{2,3}`（single_door→2、double_doors→3；由 closure 派生，不独立采样）
- sampling domain：由 closure enum 决定（single=2 / double=3）；非加权独立轴
- copied object：FIXED `shelf_{i}`(+`shelf_bracket_{i}_{side}` for hinged_door) 横隔板
- naming：`shelf_{i}` / `shelf_bracket_{i}_{side}`
- placement：`sz_i=open_bot_z+(i+1)*cavity_h/(N+1)`（N+1 等距）
- joint policy：无关节（FIXED carcass visual，非活动件）
- source/gating：hinged_door(N=2)/double_doors(N=3)

> roller_shutter 的 `slat_{i}` 与 louvered 的 `louver_slat_{i}` 是 **module-local 派生复制**（`n_slats=int(available/pitch)`、`n_slats=35` 由几何/常量决定），**不是暴露的 multiplicity count param**——它们随 closure/face module 内部尺寸自适应，不进 `slot_choices` 也不加权采样（仅作 viewer 目检的连接性检查）。caster/leg 固定为 4（结构常量，非 multiplicity 轴）。

## 拓扑多样性审计

总组合数（含 multiplicity）：
- closure=n_sliding_drawers × N∈{3,4,5} = **3**（front 强制 solid，base × 3）
- closure=single_hinged_door × front∈{solid,glazed,louvered} = **3**
- closure=double_doors = **1**（front=solid）
- closure=roller_shutter = **1**（front=solid）
- closure×front×N 子合计 = 3+3+1+1 = **8** distinct closure/face/N 拓扑类
- × base_support {plinth, legs, casters} = **8 × 3 = 24** distinct 拓扑组合
- （palette_style 6 与连续 scale 不计入拓扑等价类，但 sweep 多样性远超此数）

理由：24 distinct module/N/base 组合 ≥ 10；closure×N 单独即 3+3+1+1=8，× base 3 = 24，clear 机械门槛。casters 引入 CONTINUOUS joint、roller_shutter 引入第二 PRISMATIC 轴、door 引入 REVOLUTE，三类 joint topology 并存进一步拉开 distinct。

seed_domain_policy：`procedural_first`

Procedural Sampling / Sweep Plan：
`config_from_seed(seed)` 用 deterministic procedural sampling：① 加权选 `closure_mechanism`（drawers baseline 偏高，door/shutter 次之）；② 若 closure=n_sliding_drawers，逐 N 加权选 `n_drawers∈{3,4,5}`（N=4 高频）；③ 若 closure=single_hinged_door，选 `front_face_style∈{solid,glazed,louvered}`，否则强制 solid_steel；④ 独立选 `base_support∈{plinth,legs,casters}`；⑤ 选 `palette_style`；⑥ 采 independent 连续 scale（width/height/depth/travel/door_open）→ 派生 base_lift/drawer_travel → inequality 投影（flush 容差、栈高、shutter 不穿顶）。compatibility matrix gating（见下表）排除非法 front×closure。少量 regression overrides：仅在 sweep 暴露已知失败组合时加（首版无）。random sweep / viewer 目检：seeds 0-49 初轮，0-999 成熟审计。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）——本类 closure/face/N/base distinct 仅 24（受 closure 兼容约束 + door 内部 shelf-N 由 closure 派生 + base 仅 3 档），低于 300 属类别固有约束（街用立式柜的封闭机构与接地方式枚举有限）；多样性主要来自 24 拓扑 × 6 palette × 连续比例的视觉展开，sweep 仍以 24 拓扑等价类为主轴。

Controlled local parameterization：初版应含 `cabinet_width_scale`/`cabinet_height_scale`/`cabinet_depth_scale`（independent，clamp 保 `upright` h>w*2.5 与 footprint）、`drawer_travel_ratio`（equation，随 depth）、`shutter_travel`（inequality，不穿顶板）、`door_open_upper`（independent，仅 joint range）、`base_lift`（equation，由 base_support 派生 body_bottom_z）。全部在 `resolve_config` clamp/派生/投影，不破坏 closure flush 接口、base 接地不变量、multiplicity 等距分层。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | closure(加权)→[N or front 条件]→base→palette→连续 scale；`slot_choices_for_seed` 返回 (closure, front, base) + N | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | front∈{glazed,louvered} ⇒ closure==single_hinged_door（否则 fallback solid_steel）；N 仅 drawers；shelf-N 由 door 派生；shutter slat-N 几何派生；base 与 closure 正交 | 非法 front×closure 被 gate；无 floating door/drawer/shutter；caster CONTINUOUS 轴正确；leg/plinth 接地 z≈0 |
| controlled local variation | width/height/depth/travel/door_open/base_lift scale + clamp | 比例变化不破 upright 比例、flush 闭合、栈等距、接地不变量、joint origin |
| regression overrides | none（首版）| 仅 sweep 暴露失败组合时补，记录 seed+原因 |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | 各 closure flush/open + base 接地 + contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A closure_mechanism | 4 | yes | yes | drawers/single_door/double_doors/roller_shutter |
| B front_face_style | 3 | yes | yes | solid/glazed/louvered（条件激活于 single_hinged_door）|
| C base_support | 3 | yes | yes | plinth/legs/casters |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名（closure/front/base + N）
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling；seed=0 不特殊
- compatibility matrix gating 阻止非法组合（glazed/louvered 仅配 single_hinged_door；N 仅 drawers；front 非门 closure 强制 solid）
- optional regression overrides 稀疏且有据（首版 none）
- 不无限轮换小型 curated / modulo 表作为主 seed domain
- 受控局部 scale 被 clamp，不破坏 closure flush 接口、base 接地不变量、closure joint origin、multiplicity 等距
- 跨部件 scale 依赖（base_lift equation、drawer_travel equation、flush/栈高/shutter inequality）在 `resolve_config` 解析，不留到 builder 失败
- 关键 InterfaceSpec / MatingContract：closure 面闭合齐平 x=D；base 接地 min-z≈0；REVOLUTE 门绕竖 Z；PRISMATIC 抽屉 +X / 卷帘 +Z；CONTINUOUS caster +Z
- 关键 joint type/axis/range 符合：drawer PRISMATIC +X 0..travel；door REVOLUTE +Z；double_doors 两扇 axis ±Z；shutter PRISMATIC +Z 0..0.50；caster CONTINUOUS +Z 无 lower/upper
- 复制对象遵循命名/placement：`drawer_{i}`/`shelf_{i}`/`slat_{i}`/`louver_slat_{i}`/`leg_{i}`/`caster_{i}` 等距/角阵 placement

## Reject cases

- closure 闭合姿态下 closure 面（drawer_face / door_panel / shutter / glass-frame）未在壳前 x=D 齐平（`*_flush_closed` fail）。
- 任一 closure joint 缺失或退化为 FIXED——必须 ≥1 个真实 PRISMATIC 或 REVOLUTE closure 暴露内腔。
- door 绕非竖轴（`abs(axis[2])<0.99`）或 double_doors 两扇同向（应 axis ±Z 对开）。
- 抽屉/卷帘/百叶/slat 栈越过 top/bottom panel 或彼此非等距、出现孤岛（slat 间未 2mm 互锁致断开）。
- base 接地失败：plinth/leg 底或 wheel 底 min-z 不≈0；或 caster 轴非 +Z CONTINUOUS。
- front∈{glazed,louvered} 配到非 single_hinged_door closure（compatibility 未 gate）。
- 立式比例破坏：`height_z ≤ width_y*2.5` 或 top_z ≤ 1.2（width/height scale clamp 失效）。
- 把 `pull_handle`/`label_holder`/`top_badge`/`fire_label`/`door_emboss` 提升为独立 part/slot，或为凑 slot 发明无 source 结构。
- 用纯 color/material/scale 差异冒充新 candidate。

## 与相邻类别的边界

- 不该混入 **utility_box（街道电气箱 / pad-mounted street electrical cabinet）**：**重叠提醒**——两者都是街用直立钣金箱体，外观可混淆。区分点：fire_cabinet 是 filing-cabinet 形**高瘦立式柜**（h>w*2.5），其 closure 是**多种真实关节家族**（PRISMATIC 抽屉栈 / REVOLUTE 单双门 / PRISMATIC 卷帘）且内部有 drawer/shelf fitment；utility_box 通常是**矮胖电气机柜**、closure 多为单/双前铰门遮蔽内部接线端子/断路器，无抽屉栈、无卷帘、无 filing-cabinet 比例，且常带散热百叶/电缆入口为身份核心。若 closure=single_hinged_door 且配 louvered front，二者最易混——靠**高瘦立式比例 + 抽屉/卷帘候选存在性 + 内部 shelf 非端子盘**锚定 fire_cabinet 身份。
- 不该混入 **drawer_cabinet_with_sliding_drawers（木质多抽屉柜/斗柜）**：那是室内木作家具，材质木色、无街用钢壳/凹底座/卷帘/铰门混合 closure 家族；fire_cabinet 是钣金街用柜且 closure 是**多机构枚举**（抽屉只是其一）。
- 不该混入 **first_aid_cabinet（壁挂急救柜）**：那是**壁挂**小尺度药柜（贴墙、不落地、无腿/脚轮/底座支腿，门玻璃+红十字身份），fire_cabinet 是**自立落地**街用大柜（plinth/legs/casters 接地 + 抽屉/卷帘/双门多 closure）。
- 不该混入 **cabinet / arcade_cabinet / container_box**：通用机柜/街机/集装箱拓扑与接口点位不同（无街用立式钢柜 + 多 closure 关节家族 + 接地枚举身份）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | **IDENTITY-AMBIGUITY FLAG（需 reviewer 裁决）**：上游标签为 "Fire cabinet"，但 PICDIR `001.png` 与全部 10 个 5★ 样本实际是一只**暗炭色四抽屉金属 filing/utility 立式柜**，**不是**玻璃消防水带箱。本 spec 已按 source map 的既定身份处理为「街用钢制立式柜，closure 为定义性关节（抽屉 PRISMATIC / 门 REVOLUTE / 卷帘 PRISMATIC），base = plinth/legs/casters」。请确认：(a) 是否保留 slug `fire_cabinet` 但身份取「street/utility metal cabinet」；(b) 与 **utility_box**（街道电气箱）的边界重叠（见 §11，louvered+single_door 组合最易混）是否需进一步收窄或合并；(c) palette_style 中 `fire_red_alarm` colorway 是否足以呼应 "Fire" 语义而无需引入消防水带箱拓扑。|

## 模板实现备注（可选）

- closure modules 共享 carcass 壳 helper（`base_plinth`/`bottom_panel`/`top_panel`/`back_wall`/`side_wall_{tag}`），但**前框/导轨随 closure 不同**：drawers→`face_rail_{i}`(range N+1)+`runner`；single/double door→周边 `face_rail_{top,bottom}`+`face_stile`；shutter→`side_channel`+`fixed_front_panel`+rails。前框生成应按 closure 分支，不强行统一。
- base modules 共享 `body_bottom_z` 抽象（plinth_h/leg_h/CASTER_H）；上方 carcass+closure 几何对 base 完全无感（base 仅决定 z 抬升 + 是否出 caster CONTINUOUS 关节）。
- element-scoped `allow_overlap` 必须随 closure/face 复制：hinged_door 的 door_panel-vs-face_stile + 铰桶-vs-stile（hinged L355-L372）；glazed 的 hinge_barrel-vs-frame_stile（glazed L271-L276）；louvered 的 piano hinge_barrel-vs-door_panel（louvered L375-L384）；shutter slat 互锁重叠（element-local）。
- roller_shutter slat-N 与 louvered louver-N 为几何派生，**不进 seed domain count param**；caster/leg 固定 4。
- shutter `cabinet_to_shutter` 升程 inequality（升起 slat 顶 ≤ open_top_z）与 door REVOLUTE upper 必须在 `resolve_config` 求解，避免 builder 期穿模/穿顶。
