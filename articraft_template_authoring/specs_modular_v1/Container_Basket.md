# Container basket (lidded woven rattan storage basket) — Modular Spec

> 来源小类：`picture/Container/Basket`（articraft_data 上游 Container/Basket fork-variant pool）。
> 5 个 parent 覆盖 body_footprint 全轴（round / hexagonal / oval / rectangular / cylindrical），9 个 `rec_container_basket_var_*` 为 fork 变体覆盖 lid_closure / lid_grip / wall_weave / side-handle 轴。
> 引用 `model.py:Lx-Ly` 来自各样本 `articraft_data`（已镜像到 arti-template `data/records/`）当前 `revisions/rev_000001/model.py`；以 part/joint/helper **名字** 为准（`basket_body` / `basket_lid` / `body_to_lid` / `carry_bail` / `body_to_bail` / `turn_knob` / `lid_to_knob` / `_twill_strand_path` / `_checker_row_path` / `_body_wave_path` / `side_handle_loop_i` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_basket` |
| template path | `agent/templates/Container_Basket.py` |
| test path (optional) | `tests/agent/test_container_basket_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（linear_chain body→lid 串一条主闭合 joint；lid_grip 挂到 lid；side-grip 为唯一 multiplicity 轴，挂到 body）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 5 parent + 9 `rec_container_basket_var_*` fork 变体 = 14 |
| read_count | 14（全读 model.py 全文）：5 parent（round `66ae2d28` / hex `a27c9e51` / oval `003basket` / rect `99719568` / cyl `basket005`）+ 9 变体（hinged_flip_lid / bail_swing_handle / arched_carry_bail / twist_turn_knob_latch / open_lattice_weave / diagonal_twill_weave / dense_checker_weave / banded_wave_weave / side_carry_handles）|
| read_scope | all 5-star samples in this category（全读，未抽样）|
| source_index_policy | only adopted module sources are indexed below（§14）|

读取要点 / 分流说明：
- **统一命名契约**：每个样本 body 都是 `basket_body`，lid 都是 `basket_lid`，主闭合 joint 都是 `body_to_lid`。可读性契约（stakes / rows / floor / lid strips 全部经 for-i/for-j 循环 + 共享 tube helper 发射）在 14 个样本里**全部**遵守。
- **body_footprint 轴**：5 cell（round / hexagonal / oval / rectangular / cylindrical）已被 5 parent 占满，按源映射**不再作为变体轴重造**——它只是 body mesh 的 profile/helper 属性（圆 `_ring_path` / 棱 `_hex_path` + `_hex_vertices` / 超椭圆 `_super_point` / 矩形超椭圆 `_super_point(SUPER_N=5.2)`）。下游模板把它做成 `body_form` enum（root mesh 属性），与三个真 slot 笛卡尔积一起撑开多样性。
- **open_lattice_weave 实测**：record id 名为 `open_lattice`，但 `build_object_model` 实际发射的是**密集图案墙**（`woven_wall_wave_band_i` + `woven_wall_short_vertical_stitch_i` + `woven_wall_herringbone_{label}_i`），不是稀疏镂空菱形。采纳时按**实际几何**命名为 `patterned_wall_weave`（保留 source id），避免下游照名字写错结构。
- **纯色/材质/尺寸 diff**（FORK_VARIANTS §2 排除）不另列 candidate；material 归 `palette_style`（§7）。

## 核心身份

带盖的编织藤篮 / 收纳篮（lidded woven rattan basket）：一只直立中空篮体，底坐地 z≈0，居中于 (x=0,y=0)，由共享 tube helper（`tube_from_spline_points` 包裹 SDK `tube_from_spline_points` + `mesh_from_geometry`）把藤条逐根发射——**编织底**（crossed cane floor strips + braided foot ring）→ **垂直立柱 stakes**（`for j in range(STAKE_COUNT)`）→ **水平编织行 / 斜纹 / 棋盘 / 波浪带**（`for i in range(...)`）→ **辫状篮口 mouth rim**（`_braid_path` 双股反相）。篮口上方一只盖按某种机构开合（**主活动语义**）：友配抬升盖（纯 PRISMATIC +Z `body_to_lid`）/ 后铰翻盖（REVOLUTE 绕后 rim 水平 +X 轴）/ 固定盖 + 头顶提梁摆动（REVOLUTE +Y `body_to_bail`，提梁是 mover）。盖上可有一个抓握特征（`lid_grip`）：bare 平盖 / 低矮 oval 编织旋钮 / 小方盒提手 / 黑色直立环 / 高拱野餐提梁（固定）/ 中央 quarter-turn 旋锁旋钮（REVOLUTE +Z 活动）。篮壁可换不同编织拓扑（`wall_weave`）。篮体两侧可选一对藤编侧提握把（`side_handle_count`，唯一 multiplicity 轴）。默认成熟域：单篮单盖，footprint 由 5 parent 形态之一驱动。

不该混入：
- 金属丝购物筐 / 购物篮（wire shopping basket，钢丝网 + 推车，是 `shopping_bucket` / wire-basket 家族）——藤篮身份是逐根藤条编织 + 辫状口沿。
- 带盖玻璃 / 陶瓷罐（threaded screw-cap jar），是 `container_jar`——jar 是 revolve/shell 厚壁开口腔 + 螺纹 neck，basket 是镂空藤编 + 平/拱盖。
- 无盖收纳箱 / 行李箱（hinged-lid box / suitcase），是 `bag_suitcase_box`——box 是实心面板 shell，basket 是编织壁。
- 空气炸锅抽屉篮（air-fryer pull-out basket，PRISMATIC 抽拉 + 电器主体），是 appliance 家族——不是独立藤编容器。

## 槽位 + 候选模块表

> **建模注记**：`body_form`（round/hex/oval/rect/cyl）是 `basket_body`（root）的 mesh / profile 属性（一次性 floor+stakes+rows+rim 发射），**不是独立串联 slot**，但参与笛卡尔积（见 §9）。下面三个是真 slot：`lid_closure`（盖怎么连/开，linear_chain 主 joint）、`lid_grip`（盖上抓握特征，挂 lid）、`wall_weave`（篮壁编织拓扑，root mesh body 层）。

### Slot A：lid_closure（**主开合机构槽**——盖如何连接与开启）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| prismatic_liftoff（基线）| 5 parent 全部（round `66ae2d28`）| `body_to_lid` PRISMATIC axis(0,0,1) L358-366 + `basket_lid` part L301 | eligible if compatible | 友配抬升盖：单 `body_to_lid` PRISMATIC +Z（无旋转），q=0 盖坐 mouth rim、正 q 直抬离 LID_LIFT；最常见真实篮盖 |
| hinged_flip_lid | rec_container_basket_var_hinged_flip_lid | `body_to_lid` REVOLUTE axis(1,0,0) origin(0,-R_BODY,BODY_H) L478-486 + `hinge_barrel_i`(body) L460-474 + `lid_hinge_knuckle_i`(lid) L442-456 | eligible if compatible | 后铰翻盖：盖绕后 rim 水平 +X 轴 REVOLUTE，q=0 闭合盖座、正 q 上翻至 HINGE_UPPER=2.0rad；lid 几何整体 `_offset_y(..., R_BODY)` 平移使铰点在后 rim；body 侧 3 个 hinge_barrel + lid 侧 2 个 knuckle 交错 |
| bail_swing_handle | rec_container_basket_var_bail_swing_handle | `body_to_bail` REVOLUTE axis(0,1,0) origin(0,0,H_BODY) L527-537 + `carry_bail` part L461 + `bail_anchor_lug_i`(body) L385-398 | eligible if compatible | 固定友配盖（保留 `body_to_lid` PRISMATIC L513-521）+ 头顶 carry_bail 摆动：`carry_bail` 是 mover，绕两侧 lug 连线 +Y 轴 REVOLUTE，q=0 折下贴体、q=π 竖起提握；提梁 = 三股 `_bail_arch_path` 拱 + `_bail_braid_path` 缠绕 |

硬约束记录：lid_closure 3 candidate（达下限 3）。含 PRISMATIC（liftoff）/ REVOLUTE +X（flip）/ REVOLUTE +Y（bail，第二活动件）三种 joint 拓扑 + 不同 part 数（liftoff 2 part / flip 2 part + hinge 硬件 / bail 3 part：body+lid+carry_bail）。每个 candidate **≥1 non-fixed joint**。

### Slot B：lid_grip（盖上抓握特征——固定 visual 或活动旋钮）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键结构 / joint 特征 |
|---|---|---|---|---|
| bare（基线）| rec_hexagonal-...-lift-off-lid `a27c9e51`（也 round `66ae2d28`）| `basket_lid` 仅 lid_weave + 装饰，无独立 grip part（hex 用 `raised_leaf_woven_panel` 平贴装饰 L591-620；round 全平 L301-356）| eligible if compatible | 平盖 / 装饰盖，无凸起抓握件（lid 仅编织面 + braided rim）|
| raised_oval_knob | rec_oval-...-raised-lid-handle `003basket` | `raised_handle_base_braid_{strand}` L482-494 + `raised_handle_top_braid_{strand}` L495-506 + `raised_handle_vertical_weave_i` L508-521（`_handle_riser` helper L215）| eligible if compatible | 低矮藤编 oval 旋钮居中盖顶：双层 `_braid_path` 环（base+top）+ 12 根 vertical riser；固定 visual 挂 lid，无 joint |
| raised_rect_handle | rec_rectangular-...-fitted-lift `99719568` | `raised_rect_handle_rim_k`（base/top）L465-473 + `handle_vertical_stake_i` L474-483 + `handle_top_weave_x/y_i` L484-501（`_handle_chord` helper L201）| eligible if compatible | 小方盒提手：双层 rounded-rect 环 + 16 根竖 stake + 顶部 crossed weave；固定 visual 挂 lid，无 joint |
| black_ring_handle | rec_cylindrical-...-flat-lid `basket005` | `black_ring_handle_loop` L391-403（`_handle_loop_path` L143）+ `black_ring_handle_mount_i` L404-416（`_handle_post` L156）| eligible if compatible | 黑色直立环握把：单 upright loop（YZ 面）+ 2 根 mount 立柱，黑色材质；固定 visual 挂 lid，无 joint |
| arched_carry_bail | rec_container_basket_var_arched_carry_bail | `bail_post_i` L425-437（`_bail_post_path` L146）+ `bail_arch_main` L440-451（`_bail_arch_path` L161）+ `bail_arch_wrap_i` L454-466 | eligible if compatible | 高拱野餐提梁（**固定**，picnic-style）：两侧立柱 + 抛物拱 + 缠绕股，立在盖顶；固定 visual 挂 lid，无 joint（区别于 bail_swing_handle 的活动 carry_bail）|
| twist_turn_knob_latch | rec_container_basket_var_twist_turn_knob_latch | `turn_knob` part L499 + `lid_to_knob` REVOLUTE axis(0,0,1) origin(0,0,KNOB_BASE_Z) L642-650 + `lug_arm_i`/`lug_tip_i`/`lug_crossbar_i` L584-625 + `rim_lug_slot_i`(body) L424-436 | eligible if compatible | 中央 quarter-turn 旋锁旋钮（**活动** REVOLUTE +Z）：`turn_knob` 经 `lid_to_knob` 绕 +Z 旋 0→π/2 锁，4 根 lug 嵌入 body rim slot；旋钮转动 = 第二活动件，需 body rim slot 承载 |

硬约束记录：lid_grip 6 candidate（达 3-6 上限）。bare/oval/rect/ring/arched 为固定 visual（无独立 joint），twist_turn_knob_latch 引入第二活动 REVOLUTE +Z joint + 独立 `turn_knob` part。结构差异真实（不同 part / helper / joint 拓扑），非纯装饰换色。

### Slot C：wall_weave（篮壁编织拓扑——`basket_body` 的 side-wall 层）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 helper / 结构特征 |
|---|---|---|---|---|
| dense_over_under（基线）| 5 parent 全部（round `66ae2d28`）| `vertical_weave_stake_j` L243-256 + `horizontal_weave_band_i` L260-283（`_ring_path(weave_count=VERTICAL_STAKES)` 相位翻转 over-under）| eligible if compatible | 紧密平织 over-under：垂直 stakes + 水平带逐行 phase=（i%2）π 翻相，实墙 |
| patterned_wall_weave | rec_container_basket_var_open_lattice_weave（实测为图案墙，非镂空）| `woven_wall_wave_band_i` L446-456（`_wall_band_path` L173）+ `woven_wall_short_vertical_stitch_i` L458-470 + `woven_wall_herringbone_{label}_i` L472-484（`_herringbone_stitch_path` L206）| eligible if compatible | 图案壁：波浪水平带 + 短竖锁针 + 鱼骨斜插，三层叠出装饰面（无 `horizontal_rect_weave` 长行；dense_rows==0）|
| diagonal_twill_weave | rec_container_basket_var_diagonal_twill_weave | `twill_strand_right_i` L295-308 + `twill_strand_left_i` L310-323（`_twill_strand_path` L137：两族螺旋 over-2-under-2，TWILL_TURNS=1.5）+ `vertical_weave_stake_j` L275-288 | eligible if compatible | 斜纹 twill：两族斜向螺旋股绕 stakes 走 over-two/under-two 人字纹（无 horizontal_weave 带；test 断言 horizontal==0）|
| dense_checker_weave | rec_container_basket_var_dense_checker_weave | `checker_vertical_stake_j` L318-326（`_checker_vertical_path` L123）+ `checker_horizontal_band_i` L328-336（`_checker_row_path` L138：逐行 phase=row·π 棋盘相位）| eligible if compatible | 密棋盘：高密 vertical stakes(44) + horizontal bands(30) 逐行棋盘相位错开，紧凑方格 |
| banded_wave_weave | rec_container_basket_var_banded_wave_weave | `primary_horizontal_wave_band_i` L337-350（`_body_wave_path` L144：wave_count=WAVE_LOBES=8 正弦波带）+ `contrasting_reverse_wave_band_i` L351-362（`_secondary_wave_path` L160）+ `wide_contrast_girdle_wave_band_k` L364-377 | eligible if compatible | 横向波浪带：主波带 + 反相对比带 + 3 道宽 girdle 带，正弦起伏 wrap 全墙（区别 twill / lattice / checker）|

硬约束记录：wall_weave 5 candidate（达 3-6 上限）。全部为 `basket_body` 的 side-wall mesh 层替换，共享 stake + braided-rim + floor helper，**只换水平层的编织 helper 族**（平织带 / 图案墙 / 斜纹股 / 棋盘带 / 波浪带）。结构差异真实（不同 helper、不同 part 命名族、stakes 与 horizontal-row 的数量/拓扑差异），非换色。

## 槽位图（slot graph）

pattern: mixed（`basket_body` root 坐地；lid 经主闭合 joint 串接；grip 挂 lid；side-grip multiplicity 挂 body）

```
basket_body(body_form, wall_weave)  [ROOT, 坐地 z≈0]
   │  (+ wall_weave 决定 side-wall mesh helper 族；floor/stakes/braided-rim 共享)
   │  (+ side_handle_count × side_handle_loop_i 固定 visual 挂 body 侧面，无 joint —— multiplicity 轴)
   │
   ├── lid_closure = prismatic_liftoff:
   │     basket_body --[body_to_lid: PRISMATIC +Z @ mouth rim top (0,0,LID_SEAT_Z)]--> basket_lid
   │
   ├── lid_closure = hinged_flip_lid:
   │     basket_body --[body_to_lid: REVOLUTE +X @ 后 rim (0,-R_BODY,BODY_H)]--> basket_lid
   │        (+ hinge_barrel_i body visual / lid_hinge_knuckle_i lid visual @ 后 rim)
   │
   └── lid_closure = bail_swing_handle:
         basket_body --[body_to_lid: PRISMATIC +Z @ mouth rim]--> basket_lid (固定友配盖)
         basket_body --[body_to_bail: REVOLUTE +Y @ mouth rim (0,0,H_BODY)]--> carry_bail (mover)
            (+ bail_anchor_lug_i body visual @ 两侧 rim lug)

  basket_lid (上面任一 closure 的 child) 再挂 lid_grip:
   ├── bare: 无独立 grip part（lid 仅编织面）
   ├── raised_oval_knob / raised_rect_handle / black_ring_handle / arched_carry_bail:
   │     固定 visual 挂 basket_lid（无 joint）
   └── twist_turn_knob_latch:
         basket_lid --[lid_to_knob: REVOLUTE +Z @ lid 中心 (0,0,KNOB_BASE_Z)]--> turn_knob (mover)
            (+ rim_lug_slot_i body visual @ body mouth rim 承载 lug)
```

接口点位与 joint 语义：
- **liftoff 接口**：`body_to_lid` PRISMATIC origin 落在 mouth rim top 中心 `(0,0,LID_SEAT_Z)`（各样本 LID_SEAT_Z = H_BODY 或 H_BODY±小量），axis +Z，q=0 盖坐下、正 q 抬离 LID_LIF。
- **flip 接口**：`body_to_lid` REVOLUTE origin 在后 rim 边 `(0,-R_BODY,BODY_H)`，axis +X，闭合 q=0、上翻正 q（HINGE_UPPER=2.0）；lid 几何整体 `_offset_y(R_BODY)` 使 woven disc 在 q=0 时居中 body 上方；hinge_barrel/knuckle 为可见铰链硬件。
- **bail 接口**：`body_to_bail` REVOLUTE origin 在 mouth rim 中心 `(0,0,H_BODY)`，axis +Y（连两侧 lug），q=0 折下（AABB min_z < rim − 0.08）、q=π 竖起（AABB max_z > rim + 0.05）；同时 `body_to_lid` PRISMATIC 保留为固定友配盖机构。
- **twist-knob 接口**：`lid_to_knob` REVOLUTE origin 在 lid 局部帧 `(0,0,KNOB_BASE_Z)`，axis +Z，0→π/2 quarter-turn；lug_arm/lug_tip 嵌 body `rim_lug_slot_i`（需 body solid mouth rim 承载，见排除项）。
- **grip 固定接口**：oval_knob / rect_handle / black_ring / arched_bail 均为固定 visual 挂 basket_lid（无独立 joint），origin/位置在 lid 局部帧顶面中心。
- **side-grip 接口**：`side_handle_loop_i`（closed oval ring）+ `side_handle_anchor_i_j`（2 strap）+ `side_handle_weave_trim_i_k`（2 arc）固定 visual 挂 basket_body 侧面，N∈{0,2}（见 §8），handle top 必须 < LID_SEAT_Z 不挡盖。
- **mating policy**：盖编织 rim 罩 over mouth rim 是 captured / 友配（盖壁与 mouth 几何故意小重叠）→ **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `ctx.allow_overlap(lid, body, ...)` 守 overlap（见各样本 run_tests）；bail/knob 的 captured contact 同理 allow_overlap。
- **rest pose**：所有盖 q=0 闭合 / 坐下；bail q=0 折下贴体；turn_knob q=0 未锁；固定 grip / side-grip 不动。
- **互斥 / 可选**：lid_closure 三候选互斥（一次一种盖机构）；lid_grip 六候选互斥；arched_carry_bail（固定提梁 grip）与 bail_swing_handle（活动 carry_bail closure）语义不同但可共存——若同时选则两者都是头顶提梁会冗余，compatibility matrix 做软互斥（见 §9）。side_handle_count=0 是空机构。

## 每槽位 Module Emits / Interfaces

### Slot root / basket_body（body_form + wall_weave，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `basket_body`（floor cross-weave + braided foot ring + vertical stakes + 选定 wall_weave 水平层 + braided mouth rim[ + side_handle_* 固定 visual]）| round `66ae2d28` L178-299 / wall_weave 各 source |
| internal joints | 无（root 篮体本身无活动件）| — |
| upstream interface | 坐地 z≈0（root）| — |
| downstream interface | mouth rim top 中心（lid joint parent 接口）+ 后 rim 边（flip hinge）+ 两侧 rim lug（bail/side-grip）| round L363 / flip L483 / bail L532 |

### Slot A / lid_closure（每候选发射对应活动盖）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `basket_lid`(liftoff/flip) / `basket_lid`+`carry_bail`(bail) | 各 closure 源 |
| internal joints | `body_to_lid` PRISMATIC +Z（liftoff）/ `body_to_lid` REVOLUTE +X（flip）/ `body_to_lid` PRISMATIC +Z + `body_to_bail` REVOLUTE +Y（bail）| round L358 / flip L478 / bail L513,L527 |
| downstream interface | basket_lid（lid_grip 的 parent）| — |

### Slot B / lid_grip（≠bare/twist 时固定 visual 挂 basket_lid；twist 发射活动旋钮）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（oval_knob/rect_handle/black_ring/arched_bail 为 basket_lid 固定 visual）/ `turn_knob`(twist) | oval L482 / rect L465 / ring L391 / arched L425 / twist L499 |
| internal joints | 无（固定 grip）/ `lid_to_knob` REVOLUTE +Z 0→π/2（twist）| twist L642 |

### Slot D / side-grip multiplicity（固定 visual 挂 basket_body）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`side_handle_loop_i` + `side_handle_anchor_i_j` + `side_handle_weave_trim_i_k` 为 basket_body 固定 visual）| side_carry_handles L553-621 |
| internal joints | 无（非活动编织握把）| — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | round / hexagonal / oval / rectangular / cylindrical | round | choice | deterministic procedural sampler 选（root mesh 属性）| 5 parent |
| lid_closure | enum | prismatic_liftoff / hinged_flip_lid / bail_swing_handle | prismatic_liftoff | choice | sampler 选 | Slot A 表 |
| lid_grip | enum | bare / raised_oval_knob / raised_rect_handle / black_ring_handle / arched_carry_bail / twist_turn_knob_latch | bare | choice | sampler 选；含空机构 bare | Slot B 表 |
| wall_weave | enum | dense_over_under / patterned_wall_weave / diagonal_twill_weave / dense_checker_weave / banded_wave_weave | dense_over_under | choice | sampler 选 | Slot C 表 |
| side_handle_count | int (multiplicity) | {0, 2} | 0 | conditional | N∈{0,2}（见 §8）；N=2 时仅当 body_form 有近垂直平侧面（hex/rect/cyl/oval）才放置，round 强弧腹回退 N=0 | side_carry_handles L545 |
| palette_style | enum | natural_tan / honey_rattan / dark_walnut_reed / teal_red_accent / two_tone_wheat_umber / black_handle_natural / lacquered_chestnut / sage_powdercoat_wire / seagrass_natural / charcoal_painted（**10 配色**，每个含 body·lid·grip·trim 颜色 + 显式 finish 维度）| natural_tan | palette | palette only，**不计入 slot_choice**；per-seed `rng.choice(PALETTE_STYLES)` | 各样本 material()（§7 配色表）|
| body_height_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放篮体高 H_BODY → mouth rim Z → lid mount 高度 → side-grip Z 中心，clamp | resolve clamp |
| body_radius_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放篮体半径 / 半宽（profile 同比）→ mouth R，clamp（保盖罩配合）| resolve clamp |
| lid_overhang_scale | float | [0.95, 1.10] | 1.0 | equation | `lid_outer_R = body_mouth_R · lid_overhang_scale`；盖罩半径派生跟随 body 口径（保罩配合）| resolve clamp |
| grip_size_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放所选 lid_grip 的尺寸（knob/handle/ring/bail/turn-knob），clamp | resolve clamp |
| joint_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 lid_slide LID_LIFT / hinge upper / bail upper / knob quarter-turn 行程，clamp（hinge/bail/knob 角度上限单独 clamp 防过转）| resolve clamp |
| (—) | constraint | — | — | inequality | 盖罩配合：`lid_outer_R ≥ body_mouth_R + seat_clearance` 且 `lid_outer_R ≤ body_max_R + proud`，违反按比例回缩 lid_overhang/radius scale | 接口 / clearance |
| (—) | constraint | — | — | inequality | side-grip 不挡盖：`handle_top_z = side_grip_z_center + 0.5·grip_h + tube_r < LID_SEAT_Z − 0.01`，违反下移 side_grip_z_center | side_carry_handles L849-854 |
| (—) | constraint | — | — | conditional | twist_turn_knob_latch 需 body solid mouth rim 承载 lug → 与 patterned_wall_weave / diagonal_twill / banded_wave（镂空感强）软降级（见 §9）；其余 grip × 任意 wall_weave 正交 | 排除项 / §9 |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`lid_overhang_scale` 为 equation（盖罩半径跟随 body 口径，保盖罩 mouth 配合不破）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 body_form / lid_closure / lid_grip / wall_weave / side_handle_count 的拓扑。

## §7 配色表（palette_style — palette-only，10 配色 × 显式 finish 维度）

> `palette_style` 仅换 `model.material(...)` 的 rgba / 名义 finish，**不动任何 slot / candidate / multiplicity / joint / dimension / topology**。10 个 coordinated colorways，per-seed `rng.choice(PALETTE_STYLES)` 抽一个 colorway；其下 `body/weave`（篮体编织三档 light/mid/shadow-dark）、`lid`（盖编织 lid_light/lid_shadow）、`grip/handle`（lid_grip 的 oval_knob/rect_handle/black_ring/arched_bail/turn_knob，或 bail_swing 的 carry_bail，按所选 grip/closure 实际存在的 part 上色）、`trim/accent`（hex 色带 / 波浪对比带 / side-handle weave-trim / braided-rim accent 等装饰股，仅当该 colorway 有装饰族时发射）四组颜色随 colorway 一起取定。grip/trim 若当前组合无对应 part，则该列颜色不发射（palette 不新增 part）。
>
> **finish 维度**（显式材质处理，名义属性，挂在 colorway 上；当前 SDK 用 rgba + 名义 finish note 表达，不改几何）：`matte_natural`（天然藤/柳，哑光）· `lacquered`（清漆/亮漆柳条，高光暖调）· `powder_coated`（线材/金属丝喷塑，缎面均色）· `painted`（实色油漆，缎面）· `woven_plastic_satin`（编织塑料/树脂藤，缎面）· `natural_fiber`（海草/剑麻天然纤维，哑光偏灰绿）· `two_tone_stained`（双色染色，哑光-半光）。
>
> 锚定：前 6 个 colorway 直接取 5★ 源 rgba（round/oval/rect/cyl parent + hex 色带 + banded_wave 双色变体）；后 3 个为同类真实推断配色（柳编/线材/海草/油漆篮在真实世界常见），rgba 选在源 family 的合理邻域，finish 与几何不冲突（编织壁不变，仅名义材质处理）。

| colorway | finish（材质处理）| body/weave (light · mid · shadow/dark) | lid (lid_light · lid_shadow) | grip/handle | trim/accent（装饰股，可空）| 锚定来源 |
|---|---|---|---|---|---|---|
| natural_tan（基线）| `matte_natural` 天然藤哑光 | (0.91,0.72,0.40) · (0.80,0.58,0.28) · (0.56,0.35,0.14) | (0.88,0.67,0.35) · (0.68,0.45,0.20) | 同 lid 藤色（bare 无 grip part）| —（无装饰带）| round parent `66ae2d28` L172-176 |
| honey_rattan | `lacquered` 清漆亮柳（暖高光）| (0.91,0.70,0.38) · (0.76,0.50,0.21) · (0.49,0.30,0.11) / dark (0.34,0.20,0.07) | (0.91,0.70,0.38) · (0.49,0.30,0.11) | rect_handle / oval_knob 同 lid 暖藤；clear-coat 高光 | braided-rim accent (0.34,0.20,0.07) | rect parent `99719568` L272-275 |
| dark_walnut_reed | `lacquered` 深胡桃染色亮漆 | (0.78,0.53,0.28) · (0.62,0.39,0.18) · (0.36,0.22,0.10) | (0.76,0.51,0.25) · (0.52,0.31,0.13) | grip 同 lid 深藤；black_ring 时 (0.015,0.012,0.010) | dark reed accent (0.36,0.22,0.10) | cyl parent `basket005` L178-182 |
| teal_red_accent | `two_tone_stained` 染色藤 + 彩色编织带 | (0.90,0.68,0.36) · (0.76,0.50,0.22) · (0.50,0.31,0.12) / dark (0.36,0.21,0.08) | (0.90,0.68,0.36) · (0.50,0.31,0.12) | grip 同 lid 藤色 | woven_teal (0.02,0.48,0.41) · woven_red (0.78,0.06,0.13) · woven_coral (0.88,0.28,0.18) 色带/side-trim | hex parent `a27c9e51` L341-343 + side_carry_handles L380-382 |
| two_tone_wheat_umber | `two_tone_stained` 双色染色（麦+乌木）| honey (0.88,0.66,0.34) · wheat (0.96,0.80,0.48) · dark_reed (0.40,0.24,0.10) | lid_light (0.90,0.69,0.38) · lid_dark (0.48,0.28,0.12) | grip 同 lid 麦色藤 | umber_band (0.56,0.31,0.13) 对比波浪带 · deep_shadow (0.07,0.045,0.025) | banded_wave var L266-272 |
| black_handle_natural | `matte_natural` 天然藤 + 黑环握把 | (0.78,0.53,0.28) · (0.62,0.39,0.18) · (0.36,0.22,0.10) | (0.76,0.51,0.25) · (0.52,0.31,0.13) | black_ring / turn_knob 黑 (0.015,0.012,0.010) | dark reed accent (0.36,0.22,0.10) | cyl parent `basket005` L183 black_ring_handle |
| lacquered_chestnut | `lacquered` 栗色清漆柳条（深暖高光）| (0.70,0.42,0.16) · (0.55,0.31,0.13) · (0.43,0.24,0.09) | (0.66,0.40,0.16) · (0.40,0.22,0.09) | grip 同 lid 栗藤；clear-coat 高光 | rim accent (0.28,0.16,0.06) | 推断：oval parent `003basket` L236-240 深暖邻域 + 清漆 |
| sage_powdercoat_wire | `powder_coated` 鼠尾草绿喷塑（线材篮，缎面均色）| (0.52,0.58,0.46) · (0.42,0.48,0.37) · (0.30,0.35,0.26) | (0.50,0.56,0.44) · (0.34,0.39,0.29) | grip 同体喷塑绿；black_ring 时哑黑 (0.05,0.05,0.05) | 同色无对比带（喷塑均色）| 推断：现实粉末喷塑收纳篮常见鼠尾草绿，缎面均色（非藤色 family，finish 显式区分）|
| seagrass_natural | `natural_fiber` 海草/剑麻天然纤维（哑光偏灰绿米）| (0.80,0.74,0.55) · (0.68,0.61,0.43) · (0.50,0.44,0.30) | (0.78,0.72,0.53) · (0.54,0.48,0.33) | grip 同 lid 海草色 | 浅灰米 rim (0.62,0.56,0.40) | 推断：海草编篮（greige 天然纤维），rattan family 去饱和偏冷邻域 |
| charcoal_painted | `painted` 炭灰实色油漆（缎面，现代深色篮）| (0.22,0.22,0.24) · (0.16,0.16,0.18) · (0.10,0.10,0.12) | (0.20,0.20,0.22) · (0.12,0.12,0.14) | grip 同体炭灰漆；金属环时 (0.55,0.55,0.58) 缎面金属 | rim 高光 (0.30,0.30,0.33) | 推断：实色喷漆装饰篮（炭灰），painted satin，几何不变仅名义实色 |

finish 维度落地说明：当前 SDK 以 `model.material(name, rgba=...)` 表达，每个 colorway 的 finish 作为**名义 material-finish 属性**（colorway 表第 2 列），下游模板按 colorway 选 rgba 并把 finish 记入 material 命名 / note（如 `lacquered_*` / `powdercoat_*` / `painted_*` 前缀），**不改任何几何**（编织壁、stake、braided-rim、lid、grip part 拓扑全部保持）。grip/trim 颜色仅在该 colorway 当前组合实际有对应 part（所选 lid_grip / closure carry_bail / 装饰带族）时才上色发射；无对应 part 时该列不发射，palette 绝不新增 part / 改 slot。

## Multiplicity / Copy Logic

本小类有 **1 根 multiplicity 轴**（side 侧提握把）。核心 body→lid→grip 结构由固定 named slots 表达，不暴露其它 `*_count`。

**轴 1：side_handle_count（侧提握把对）**
- `count_param`：`side_handle_count`
- `N_range`：`{0, 2}`（本小类本轴的产品域）。源映射明确：真实带盖篮要么 0 侧握把，要么一对对置 = 2；奇数不真实。测试与产品都只采 {0,2}，**不**做 [2,100] 之类的大 N 扫描（与栅栏/桨叶类不同）。
- sampling domain（权重档）：加权采样 `{0: 0.6, 2: 0.4}`（多数带盖篮无侧握把，少数有一对）；小 N（0）偏多，2 为有限尾部。
- copied object：一个 `side_handle_loop`（closed oval ring，`_side_handle_loop_path`）+ 2 根 `side_handle_anchor`（wall→ring strap）+ 2 道 `side_handle_weave_trim`（上下加固 arc），来自共享 handle-loop helper。
- naming：`side_handle_loop_{i}` / `side_handle_anchor_{i}_{j}` / `side_handle_weave_trim_{i}_{k}`，i ∈ [0, N)。
- placement：N=2 时一对置于对置侧面中点（`handle_face_specs` = perimeter_s 0.25/0.75 即 ±Y face）+ 固定 grip 高度 HANDLE_Z_CENTER；N=0 不发射。
- joint policy：inlined 为 body 固定 visual（非活动编织握把，无 per-grip articulation），与 parent 的 inline-decoration 规则一致。
- source/gating：rec_container_basket_var_side_carry_handles `model.py` L57(SIDE_HANDLE_COUNT)/L344-370(`_side_handle_loop_path`)/L545-621(发射循环)/L817-854(test)。**gating**：N=2 仅当 body_form 有近垂直平侧面（hex/rect/cyl/oval）才放置；round（强弧腹）会让 recessed grip 浮在曲面外 → 按排除项强制回退 N=0（resolve 解析）。

## 拓扑多样性审计

总组合数：body_form(5) × lid_closure(3) × lid_grip(6) × wall_weave(5) = **450**。
（叠 side_handle_count multiplicity {0,2}，且 N=2 仅 4/5 body_form 合法 → 组合再放大，>>450。）

仅 lid_closure × lid_grip × wall_weave = 3 × 6 × 5 = **90 ≥ 10** 已远超门控；叠 body_form(5) 后 450，充裕。

理由：本类拓扑多样性来源充裕——
- lid_closure 引入 PRISMATIC +Z / REVOLUTE +X / REVOLUTE +Y(+ 第二活动件 carry_bail) 三种 joint 拓扑 + 不同 part count；
- lid_grip 含固定 visual(5) + 活动 REVOLUTE +Z 旋锁(turn_knob 独立 part) 的真实差异；
- wall_weave 在 5 个不同 helper 族（平织/图案墙/斜纹/棋盘/波浪）间改 body side-wall part 命名与拓扑；
- body_form 在 5 个 mesh profile/helper 族（圆 ring / 棱 hex / 超椭圆 oval / 矩形超椭圆 / 圆柱）间换 root mesh。
slot_choices 编入四轴 +（side_handle_count）一根 multiplicity。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choices` body_form + lid_closure + lid_grip + wall_weave（加权，近全正交，少量 gating 见下），再加权采 side_handle_count∈{0,2}，再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除/降级易坏组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 450 的可达子集（受 side-grip gating 与 turn-knob×镂空软降级影响，实际 distinct 估 ≥150；按 ≥300 富类别口径观察 建议线）。低于 450 的原因是部分组合被 compatibility 降级合并（如 round+side-grip 回退 N=0、turn-knob×强镂空墙降级到 solid-rim 适配），而非词汇不足。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 5 个 scale（body_height / body_radius / lid_overhang(equation) / grip_size / joint_travel）。全部 `resolve_config` clamp + 每 build 统一应用。`lid_overhang_scale` 为 equation（盖罩半径派生跟随 body 口径）。盖罩配合不等式 + side-grip 不挡盖不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏 lid joint origin（mouth rim / 后 rim hinge / bail 轴 / knob 中心）、盖罩 mouth 配合、side-grip 位置或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choices` 四 named slot（加权，近全正交）+ 加权 side_handle_count{0,2}，再 uniform 各 scale + palette_style | slot_choices_for_seed 含四轴 + multiplicity 且与 build 一致 |
| compatibility matrix | (1) **side_handle_count=2 × body_form=round** → recessed grip 浮在强弧腹外，**强制回退 N=0**（排除项 §3）。(2) **twist_turn_knob_latch × {patterned_wall_weave, diagonal_twill_weave, banded_wave_weave}** → 旋锁 lug 需 solid mouth rim 承载，强镂空感墙降低承载可信度 → **软降级**：仍发射，但 rim 处保留 solid braided mouth rim 段供 lug 嵌入（不 gate-out，保多样性；排除项 §3）。(3) **arched_carry_bail(固定提梁 grip) × bail_swing_handle(活动 carry_bail closure)** → 两者都是头顶提梁，冗余 → **软互斥**：若同抽，优先保留 closure 的活动 carry_bail，grip 降级为 bare（避免双提梁穿插）。(4) lid_closure 三候选互斥、lid_grip 六候选互斥。(5) 其余组合正交，resolve 内按 body 口径派生盖/grip 尺寸适配 | 无 floating / collision / lid 穿篮壁 / joint 轴或 origin 错位 / 双提梁穿插 |
| controlled local variation | 5 个 clamped scale，每 build 统一；lid_overhang equation 驱动盖罩半径；scale 仅动安全比例 | 比例变化不破坏 lid joint origin / 盖罩配合 / 坐地 / side-grip 不挡盖 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | lid 动作 / bail 摆动 / knob 旋锁 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 5 | yes | yes | round / hex / oval / rect / cyl（root mesh，5 parent）|
| lid_closure | 3 | yes | yes | liftoff(PRIS+Z) / flip(REV+X) / bail(PRIS+Z & REV+Y 双活动件)|
| lid_grip | 6 | yes | yes | bare / oval_knob / rect_handle / black_ring / arched_bail(固定) / twist_knob(REV+Z 活动)|
| wall_weave | 5 | yes | yes | over-under / patterned_wall / twill / checker / banded_wave |
| side_handle_count | {0,2} | yes (N 轴) | — | multiplicity 轴，加权 {0,2}|

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_form, lid_closure, lid_grip, wall_weave) 四轴 + side_handle_count
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（`random.Random(seed)`），seed=0 不特殊
- `resolve_config` 各 scale clamp 到声明范围；lid_overhang equation 驱动盖罩半径；盖罩配合不等式 + side-grip 不挡盖不等式在 resolve 内投影 / 回缩；side-grip×round 回退 N=0、turn-knob×镂空墙软降级、双提梁软互斥均在 resolve 解析
- compatibility matrix / gating：450 组合主体合法（仅少量软降级/回退，无大面积 gate-out）
- 连续 scale clamp 后不破坏 lid joint origin / 盖罩配合 / 坐地 / side-grip 位置 / 类别身份
- 关键 joint：liftoff `body_to_lid` PRISMATIC +Z (tuple(axis)==(0,0,1))；flip `body_to_lid` REVOLUTE +X (abs(axis[0])>0.9) origin 在后 rim；bail `body_to_bail` REVOLUTE +Y (abs(axis[1])>0.9) origin 在 mouth rim 中心 + 保留 `body_to_lid` PRISMATIC；twist `lid_to_knob` REVOLUTE +Z 0→π/2 + 独立 `turn_knob` part
- captured-fit：element-scoped `ctx.allow_overlap(basket_lid, basket_body, reason=...)`（盖编织 rim 罩 mouth rim）；bail/turn_knob captured contact 同理 allow_overlap
- grandfather：盖罩 captured-fit 省略 MatingContract，由 `fail_if_articulation_origin_far_from_geometry` + allow_overlap 守
- copied object：side_handle 按 `side_handle_loop_{i}` / `side_handle_anchor_{i}_{j}` / `side_handle_weave_trim_{i}_{k}` 命名与对置侧面 placement，N∈{0,2}

## Reject cases

- 用纯 Box/Cylinder 实体当篮体而非逐根藤条编织 → 失类别身份；body 必须由 floor cross-weave + vertical stakes(for-j) + horizontal/twill/checker/wave 层(for-i) + braided rim 发射，墙体读为镂空藤编。
- lid joint origin 放在篮底 / 任意点而非 mouth rim top / 后 rim hinge / bail 轴 / knob 中心真实硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- lid_closure rest pose 设成张开 / 抬起 / bail 竖起而非 q=0 闭合坐下 → current-pose 与 viewer 目检不符（盖必须 q=0 闭、bail q=0 折下、knob q=0 未锁）。
- bail_swing_handle 把 carry_bail 做成固定 visual（无 `body_to_bail` REVOLUTE）→ 失活动语义（提梁必须是 mover，绕 +Y 摆 0→π）。
- twist_turn_knob_latch 把 turn_knob 做成固定旋钮（无 `lid_to_knob` REVOLUTE +Z）→ 退化为 raised_oval_knob，不是旋锁。
- side_handle_count 采奇数 / >2 / round body 上放 recessed grip → 不真实 / 浮在弧腹外；只采 {0,2}，round 回退 0。
- 给盖罩 captured-fit 补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质 / 装饰密度当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice；body_footprint 已被 5 parent 占满不重造）。
- 同时发射固定 arched_carry_bail（grip）与活动 carry_bail（bail closure）导致双提梁穿插 → 软互斥未生效；应 grip 降级 bare。

## 与相邻类别的边界

- 不该混入：**container_jar 带盖玻璃/陶瓷罐**（threaded screw-cap，revolve/shell 厚壁腔 + neck）——理由：jar 是实壁旋升盖罐，basket 是镂空藤编 + 平/拱盖。
- 不该混入：**shopping_bucket / wire shopping basket 金属丝购物筐**（钢丝网 + 推车 + 嵌套）——理由：藤篮是逐根藤条编织 + 辫状口沿，不是丝网。
- 不该混入：**bag_suitcase_box 无盖收纳箱 / 行李箱**（实心面板 shell，铰链翻盖箱体）——理由：basket 类别身份是编织壁 + 带盖篮口。
- 不该混入：**air-fryer pull-out basket（电器抽屉篮）**——理由：那是 appliance 主体 + PRISMATIC 抽拉子件，不是独立藤编容器。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | palette_style 扩到 **10 配色**（§7 配色表）× 显式 **material-finish 维度**（matte_natural / lacquered / powder_coated / painted / woven_plastic_satin / natural_fiber / two_tone_stained），每配色含 body·lid·grip·trim 四组颜色：natural_tan · honey_rattan · dark_walnut_reed · teal_red_accent · two_tone_wheat_umber · black_handle_natural · lacquered_chestnut · sage_powdercoat_wire · seagrass_natural · charcoal_painted。前 6 锚 5★ 源 rgba，后 3 为同类真实推断。palette-only，未改任何 slot / candidate / multiplicity / joint / dimension / topology。其余待审。 |

## 模板实现备注（可选）
- 共享 helper：`tube_from_spline_points`(包裹 SDK + `mesh_from_geometry` 命名)、`_braid_path`(双股辫 rim)、stake/floor helper、各 body_form 的 profile helper（圆 `_base_radius`/`_ring_path` · 棱 `_hex_vertices`/`_hex_path` · 超椭圆 `_super_point`/`_axes_at_z` · 矩形 `_super_point(SUPER_N=5.2)` · 圆柱 `_radius_at_z`）全 module 公用；wall_weave 各族用自己的 horizontal helper（`_ring_path` over-under / `_wall_band_path`+`_herringbone_stitch_path` / `_twill_strand_path` / `_checker_row_path` / `_body_wave_path`+`_secondary_wave_path`）。
- closure：flip 必须把 lid 几何整体 `_offset_y(R_BODY)` 让铰点落后 rim；bail 的 carry_bail 是独立 part，`body_to_bail` REVOLUTE +Y origin 在 mouth rim 中心，且保留 `body_to_lid` PRISMATIC 友配盖。
- grip：twist 必须独立 `turn_knob` part + `lid_to_knob` REVOLUTE +Z 0→π/2 + body `rim_lug_slot_i`；arched_carry_bail 是**固定** lid visual（无 joint），勿与 bail closure 混淆。
- captured-fit overlap：`run_container_basket_tests` 里 `ctx.allow_overlap(basket_lid, basket_body, reason="盖编织 rim 罩 mouth rim")`；bail↔body / bail↔lid / turn_knob↔lid / turn_knob↔body / side_handle↔body 的 captured contact 同理 allow_overlap（见各样本 run_tests）。
- lid_overhang equation：`resolve_config` 派生 `lid_outer_R = body_mouth_R · lid_overhang_scale`，盖罩配合不等式在 resolve 投影；side-grip 不挡盖不等式 `handle_top_z < LID_SEAT_Z − 0.01` 在 resolve 投影。
- 参考模板：`agent/templates/Container_Jar.py`（同 Container 大类的 parallel_children/mixed 骨架：Config/ResolvedConfig + `config_from_seed` + `resolve_config` clamp + `slot_choices_for_config` + captured-fit allow_overlap + element-scoped grandfather）；`agent/templates/Bag_Suitcase_Shopping_bucket.py`（multiplicity + 多 lid 机构分支 + captured-pin allow_overlap）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | body_form/A/B/C | round + prismatic_liftoff + bare + dense_over_under | rec_woven-rattan...`66ae2d28` | `basket_body` L178 / `_ring_path` L81 / `vertical_weave_stake` L243 / `horizontal_weave_band` L260 / `body_to_lid` PRISMATIC L358-366 | 圆 body 基线 + 抬升盖 + 平织墙 + bare 盖 |
| S2 | body_form/B | hexagonal + bare(leaf-decorated) | rec_hexagonal...`a27c9e51` | `_hex_vertices` L103 / `_hex_path` L130 / `raised_leaf_woven_panel` L596 / `body_to_lid` PRISMATIC L622 | 棱 body + 平贴装饰盖（bare 代表）|
| S3 | body_form/B | oval + raised_oval_knob | rec_oval...`003basket` | `_super_point` L64 / `_axes_at_z` L71 / `raised_handle_base/top_braid` L482-506 / `_handle_riser` L215 | 超椭圆 oval body + 低 oval 旋钮 grip |
| S4 | body_form/B | rectangular + raised_rect_handle | rec_rectangular...`99719568` | `_super_point(SUPER_N=5.2)` L71 / `raised_rect_handle_rim` L465 / `handle_vertical_stake` L474 / `handle_top_weave` L484 | 矩形 body + 方盒提手 grip |
| S5 | body_form/B/A | cylindrical + black_ring_handle + prismatic_liftoff | rec_cylindrical...`basket005` | `_radius_at_z` L49 / `vertical_rattan_stake` L254 / `black_ring_handle_loop` L391 / `_handle_loop_path` L143 / `body_to_lid` PRISMATIC L418 | 圆柱 body + 黑环握把 grip |
| S6 | A | hinged_flip_lid | rec_container_basket_var_hinged_flip_lid | `body_to_lid` REVOLUTE +X L478-486 / `hinge_barrel` L460 / `lid_hinge_knuckle` L442 / `_offset_y` L163 | 后铰翻盖 closure |
| S7 | A | bail_swing_handle | rec_container_basket_var_bail_swing_handle | `carry_bail` L461 / `body_to_bail` REVOLUTE +Y L527-537 / `bail_anchor_lug` L385 / `_bail_arch_path` L179 | 活动头顶提梁 closure（第二活动件）|
| S8 | B | arched_carry_bail | rec_container_basket_var_arched_carry_bail | `bail_post` L425 / `bail_arch_main` L440 / `_bail_post_path` L146 / `_bail_arch_path` L161 | 固定野餐提梁 grip |
| S9 | B | twist_turn_knob_latch | rec_container_basket_var_twist_turn_knob_latch | `turn_knob` L499 / `lid_to_knob` REVOLUTE +Z L642-650 / `lug_arm`/`lug_tip` L584-625 / `rim_lug_slot` L424 | 旋锁旋钮 grip（活动 REVOLUTE +Z）|
| S10 | C | patterned_wall_weave | rec_container_basket_var_open_lattice_weave | `_wall_band_path` L173 / `woven_wall_wave_band` L446 / `woven_wall_short_vertical_stitch` L458 / `_herringbone_stitch_path` L206 / `woven_wall_herringbone` L472 | 图案壁编织（实测非镂空）|
| S11 | C | diagonal_twill_weave | rec_container_basket_var_diagonal_twill_weave | `_twill_strand_path` L137 / `twill_strand_right`/`left` L295-323 | 斜纹 twill 墙 |
| S12 | C | dense_checker_weave | rec_container_basket_var_dense_checker_weave | `_checker_vertical_path` L123 / `_checker_row_path` L138 / `checker_vertical_stake`/`checker_horizontal_band` L318-336 | 密棋盘墙 |
| S13 | C | banded_wave_weave | rec_container_basket_var_banded_wave_weave | `_body_wave_path` L144 / `_secondary_wave_path` L160 / `primary_horizontal_wave_band` L337 / `contrasting_reverse_wave_band` L351 | 横向波浪带墙 |
| S14 | multiplicity | side_carry_handles | rec_container_basket_var_side_carry_handles | `SIDE_HANDLE_COUNT` L57 / `_side_handle_loop_path` L344 / `side_handle_loop`/`anchor`/`weave_trim` L553-621 / test L817-854 | 侧提握把对（N∈{0,2}）|
