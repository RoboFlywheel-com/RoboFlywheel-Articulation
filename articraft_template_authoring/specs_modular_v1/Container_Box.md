# Container box (cardboard / wooden storage / gift / shipping box with a closure mechanism) — Modular Spec

> 来源小类：`picture/Container/Box`（articraft_data 上游 Container/Box fork-variant pool）。
> Source map: `articraft_data/picture_expansion/template_source_maps/Container__Box.md`。
> 5★ 样本全读：4 parent（闭合 kraft 运输箱 / kraft 礼盒升降盖 / 胡桃木 keepsake 后铰箱 / 开口瓦楞四翻盖箱）+ 9 converged 变体（sliding_drawer / swing_double_door / front_drop_door[roll_top_tambour record] / liftout_tray / stacking_lip / n2_dividers / n4_dividers / slatted_walls / perforated_walls）= 13 records，逐一读取 `revisions/rev_000001/model.py`。
> 引用 `model.py:Lx-Ly` 来自各样本当前 `revisions/rev_000001/model.py`；以 part / joint / helper **名字** 为准（`_box_shell` / `_shell_solid` / `_box_base_solid` / `_box_shell_with_groove` / `_flap_slab` / `flap_defs` / `_drawer_tray` / `_door_panel` / `_lid_solid` / `_divider_solid` / `_inner_ledge_solid` / `_tray_*_solid` / `_inner_lip` / `_slat_board` / `_perforated_shell` / `box_to_{flap}` / `box_to_lid` / `base_to_lid` / `body_to_drawer` / `door_{i}_hinge` / `door_hinge` / `base_to_tray` / `base_to_divider_i` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_box` |
| template path | `agent/templates/Container_Box.py` |
| test path (optional) | `tests/agent/test_container_box_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: closure_mechanism + interior_structure + wall_surface 挂到共同 box_shell root，parallel_children；interior 槽内含一根 multiplicity 轴 `divider_count × N`）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 4 parent + 9 converged fork 变体 = 13 |
| read_count | 13（全读，逐一 `model.py`）|
| read_scope | all 5-star samples in this category（4 parent + 9 variant，无抽样）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14 |

冗余 / 分流说明：
- `rec_container_box_var_roll_top_tambour` record 内造的实为 **front_drop_door**（单前壁面板沿底边 REVOLUTE 下翻，part=`front_door` / joint=`door_hinge`），不是真卷帘——见源 map 排除项：真正 roll-top tambour 需 N 段链式铰接板条沿弯曲导轨，SDK 无曲线 rail prismatic，降级为单 `front_drop_door`。本 spec 即采纳该 record 的 `front_drop_door` 形态，记此。
- n2_dividers / n4_dividers 两 record 是同一 `compartment_dividers_N` 候选的 N={2,4} 两样本（`_divider_solid` 共享 helper + `for i in range(N)` 发射 + `base_to_divider_i` PRISMATIC），归并为单 multiplicity 候选，不另列 candidate。
- 三 walls 候选（solid / slatted / perforated）只换 box_shell 的发射 helper（`_shell_solid` ↔ `_corner_posts_solid`+`_slat_board` 循环 ↔ `_perforated_shell` 布尔挖孔），不改 closure / interior 接口，是真实结构差异。

## 核心身份

一只直立中空的**储物 / 礼盒 / 运输箱**（cardboard / 瓦楞纸 / 实木 keepsake / 板条 crate）：矩形或立方 box_shell 为 root，底坐地 z=0，居中于 (x=0,y=0)，由 CadQuery `box` + 内腔 `cut` 发射为四壁 + floor 的开口 / 闭口 shell。箱体的**主活动语义来自一只 closure 机构**，绕箱体某条边 / 面开合：四顶盖各绕顶边翻折（four_top_flaps，4× REVOLUTE）/ 分体望远镜升降盖（liftoff_telescoping_lid，PRISMATIC +Z）/ 后铰平盖（rear_hinged_flat_lid，REVOLUTE +X @ 后 rim）/ 内抽屉前抽（sliding_drawer，PRISMATIC -Y 火柴盒式）/ 前壁双开门（swing_double_door，2× REVOLUTE 立轴）/ 单前壁下翻门（front_drop_door，REVOLUTE +X @ 底边前装料桶式）。可选内部机构 / 内胆：空腔（plain）/ 浅升降内托盘（liftout_tray，PRISMATIC +Z 落内 ledge）/ 叠箱凸唇 + 底脚环（stacking_lip，固定 visual）/ N 块插槽隔板（compartment_dividers_N，N× PRISMATIC +Z 提出，multiplicity 轴）。壁面 / 表面结构：实壁（solid，瓦楞纸 / 实木 / 指接角）/ 横板条 crate 壁（slatted，`_slat_board` 循环 + 间隙）/ 规则圆孔通风壁（perforated，布尔挖孔）。默认成熟域：单箱 + 单 closure 机构 + 可选内部件 + 可选 N 隔板。

身份核心 = **带闭合机构（≥1 活动关节）的方角储物箱**。每个 closure 候选 ≥1 non-fixed joint（REVOLUTE / PRISMATIC）。

## 与相邻类别的边界

- 不该混入：**`bag_suitcase_box`（手提 bag-box / 行李箱体）**——理由：bag_suitcase_box 是带提把 / 拎手、可携带的箱包形态（carry handle + bail / strap），其身份在「可携带」；container_box 是**固定放置的储物 / 礼盒 / 运输箱**，无提把轴（source map §排除项明确：四 parent 均无独立提手机构，keepsake 黄铜铰仅装饰，Box 小类提手词汇稀薄，暂折入未来 hardware 槽，不强造空候选）。Box 的 closure 是箱盖 / 门 / 抽屉，bag_suitcase 的 closure 是拉链 / 搭扣 + 提携。两者不复用同一 closure 词汇表。
- 不该混入：**`container_shipping_container`（货柜 / 集装箱）**——理由：shipping container 是巨型钢制货柜（双开后门 + 波纹钢壁 + corner casting，米级尺度、车货运输身份）；container_box 是桌面 / 手持尺度（~0.1–0.3 m）的纸 / 木储物箱。虽然 swing_double_door 与货柜双门形态相近，但 container_box 是小尺度纸木盒（kraft / walnut / 瓦楞），不发射 corner casting / 集装箱 ISO 角件 / 波纹钢，材质 palette 是纸木而非工业钢。
- 不该混入：**`container_basket` / 收纳篮 / 购物篮（bail 提把 + 可嵌套堆叠 + 编织 / 网孔篮身）**——理由：basket 有 bail 提把轴 + 嵌套堆叠 multiplicity，身份在「可提编织篮」；container_box 是方盒带盖机构，无提把、网孔壁是 perforated 通风（非编织）。

reject 案例：用 boxy 占位体当篮 / 货柜；给箱补提把轴当 bag；造无任何活动关节的死盒（违反 §3，closure 必须 ≥1 non-fixed joint）。

## 槽位 + 候选模块表

> **建模注记**：`box_shell` 是 root（坐地 z=0），其 mesh 由 `wall_surface` 槽决定（solid / slatted / perforated 三种发射 helper）。`closure_mechanism` 与 `interior_structure` 各自挂到 box_shell（parallel children / 固定 visual / multiplicity）。三轴笛卡尔积 + divider N 轴构成拓扑多样性（见 §9）。closure × interior × walls × N 的合法域近全正交（少量 gating 见 §9）。

### Slot A：closure_mechanism（主开合机构槽——箱体的开合动作，**每候选 ≥1 non-fixed joint**）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| four_top_flaps（基线）| rec_closed-kraft-cardboard-shipping-box-with-foldabl_..._0c476a9b | `_flap_slab` L51-L60 + `flap_defs` 列表 L100-L116 + `box_to_{flap}` REVOLUTE 循环 L118-L143 | eligible if compatible | 四顶盖 flap_{n,s,e,w}，各绕顶 rim 内边 REVOLUTE 翻折（N/S 长翻盖 axis±X、E/W 短翻盖 axis±Y），`_flap_slab` 共享 helper + `flap_defs` 干净循环；4 活动件 |
| four_top_flaps（开态变体）| rec_open-corrugated-cardboard-box-with-four-fold-out_..._ef4e9e5a | `_flap_solid` L74-L82 / `_short_solid` L185-L190 + `long_flap_0/1_hinge` L147-L182 + `short_flap_0/1_hinge` L204-L237（REVOLUTE）| 折入 four_top_flaps（同家族，开态命名变体）| 四 fold-out 顶盖手写 4 件 long_flap_0/1 + short_flap_0/1，REVOLUTE ~110°；与 0c476a9b 同 flap 家族，开态命名差异不另列 candidate |
| liftoff_telescoping_lid | rec_kraft-cardboard-gift-box-with-a-separate-lift-of_..._3386fca8 | `_box_base_solid` L39-L56 + `_lid_solid` L59-L83 + `box_to_lid` PRISMATIC +Z L164-L174 | eligible if compatible | 分体望远镜升降盖：`lid`(浅倒置盘 + skirt 罩 over 箱顶外壁) `box_to_lid` PRISMATIC +Z（q=0 坐下、正 q 直升脱离），单活动件 |
| rear_hinged_flat_lid | rec_wooden-keepsake-box-with-a-rear-hinged-lid-and-d_..._c87d6c10 | `_box_base_solid` L49-L91 + `_lid_solid` L123-L133 + `base_to_lid` REVOLUTE axis=(-1,0,0) origin=后 rim L225-L235 + `lid_knuckle_i`/`base_knuckle_i` 黄铜铰 | eligible if compatible | 后铰平盖绕后 rim 水平轴 REVOLUTE 上掀 ~100°，黄铜 knuckle 装饰铰；单活动件 |
| sliding_drawer | rec_container_box_var_sliding_drawer | `_shell_solid`（闭顶 + 前壁开口）L61-L90 + `_drawer_tray` L93-L119 + `body_to_drawer` PRISMATIC axis=(0,-1,0) L196-L209 | eligible if compatible | 火柴盒式内抽屉：箱顶固定面、前壁开口，`drawer`(tray floor+侧+背+前 face) `body_to_drawer` PRISMATIC 前抽 -Y（max 行程保留 ~40mm 插入）；单活动件 |
| swing_double_door | rec_container_box_var_swing_double_door | `_shell_solid`（开前壁）L61-L81 + `_door_panel(side)` L84-L115 + `door_{i}_hinge` REVOLUTE axis=(0,0,∓1) 立轴 ×2 L194-L204（`for i in range(NUM_DOORS)`）| eligible if compatible | 前壁双开门 door_0/door_1，各立轴 REVOLUTE 外摆 ~90°，door 集成圆柱 pull handle + 中缝 seam；2 活动件，`for` 循环发射 |
| front_drop_door | rec_container_box_var_roll_top_tambour | `_shell_solid`（闭顶 + 开前壁）L60-L84 + `_door_panel` L87-L95 + `door_hinge` REVOLUTE axis=(1,0,0) origin=底前 rim L173-L185 | eligible if compatible | 单前壁面板沿**底边** REVOLUTE 下翻 ~85°（前装料桶式），q 增大门顶前倾下落；单活动件 |

硬约束记录：closure_mechanism 6 distinct candidate（four_top_flaps / liftoff_telescoping_lid / rear_hinged_flat_lid / sliding_drawer / swing_double_door / front_drop_door，达 3-6 目标上限）。含 REVOLUTE（flaps ×4、rear_hinge ×1、swing ×2 立轴、drop ×1 底轴）+ PRISMATIC（liftoff +Z、drawer -Y）两种 joint 拓扑 + 不同 joint count（1 / 2 / 4 活动件）+ 不同轴向，是真实结构差异。four_top_flaps 收两 record（闭态 0c476a9b 干净循环 + 开态 ef4e9e5a 手写四件）为同家族，开态不另列。

### Slot B：interior_structure（内部机构 / 内胆——固定 visual / multiplicity / 无）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键结构特征 |
|---|---|---|---|---|
| plain（基线）| 全部 parent（如 0c476a9b `_box_shell` L38-L48）| `_box_shell` L38-L48（不发射内部件）| eligible if compatible | 空腔（仅箱壁；keepsake 有 lid_panel 装饰但非内部机构）；无内部 part / joint |
| liftout_tray | rec_container_box_var_liftout_tray | `_inner_ledge_solid` L179-L208（box visual）+ `_tray_floor_solid` L211-L219 / `_tray_walls_solid` L222-L249 / `_tray_rim_solid` L252-L274 + `base_to_tray` PRISMATIC +Z L398-L408 | eligible if compatible | 浅内托盘 `tray`(floor+walls+rim) 落于箱内 `inner_ledge`（固定 visual），rim 坐 ledge top，`base_to_tray` PRISMATIC +Z 垂直提出；1 活动件 + ledge 固定 visual |
| stacking_lip | rec_container_box_var_stacking_lip | `_rect_ring` L59-L72 + `_box_shell_with_groove` L76-L97 + `_inner_lip` L101-L108（均 box parent 固定 visual，无 joint）| eligible if compatible | 顶内缘凸唇 `inner_lip`（protrude above rim）+ 底凹脚环 groove（`_box_shell_with_groove`），可叠箱注册；**全固定 visual 无独立 joint**（closure 仍提供活动关节）|
| compartment_dividers_N（multiplicity）| rec_container_box_var_n2_dividers（N=2）/ rec_container_box_var_n4_dividers（N=4）| `_divider_solid` L163-L172 + `for i in range(N_DIVIDERS)` 发射 `divider_i` L270-L295 + `base_to_divider_i` PRISMATIC +Z origin=`(DIVIDER_XS[i],0,BASE_T)` L285-L295（n2）；n4 同结构 `DIVIDER_N=4` L54 | eligible if compatible | N 块竖隔板沿 +X 等距插槽，`_divider_solid` 共享 helper，`for` 循环发射，每块独立 `base_to_divider_i` PRISMATIC +Z 提出（统一上下限）；N 活动件（multiplicity 轴，见 §8）|

硬约束记录：interior_structure 4 candidate（plain / liftout_tray / stacking_lip / compartment_dividers_N，达 3-6 目标）。plain 为空机构；liftout_tray 引入 1 PRISMATIC 活动件 + ledge 固定 visual；stacking_lip 全固定 visual（lip+groove，无 joint，活动关节由 closure 槽保证）；compartment_dividers_N 引入 N× PRISMATIC multiplicity。结构差异真实（不同 part tree / joint count / multiplicity）。

### Slot C：wall_surface（壁面 / 表面结构——box_shell root 的 mesh 发射方式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键结构特征 |
|---|---|---|---|---|
| solid（基线）| parent 瓦楞 ef4e9e5a `_shell_solid` L56-L71 / 实木 c87d6c10 `_box_base_solid` L49-L91 / 升降盖箱 3386fca8 `_box_base_solid` L39-L56 | `_shell_solid` L56-L71（瓦楞）/ `_box_base_solid` L49-L91（指接木 + 角 notch）| eligible if compatible | 实心箱壁：四壁 + floor `box` 减内腔 `cut`；瓦楞纸 / 实木 / 指接角 notch（仅材质 / 装饰差异归一为 solid）|
| slatted_walls | rec_container_box_var_slatted_walls | `_slat_board` L58-L67 + `_corner_posts_solid` L82-L100 + `_floor_panel_solid` L74-L79 + 4 墙 ×N_SLATS `for` 循环发射 `{wall}_slat_{i}` L169-L180 | eligible if compatible | 开口板条 crate 壁：四角 maple 角柱 + 横木板条（`_slat_board`）间隙 SLAT_GAP，`for wall in (front,back,left,right): for i in range(N_SLATS)` 发射；全 box_shell 内 visual（无独立 joint）|
| perforated_walls | rec_container_box_var_perforated_walls | `_shell_solid` L64-L78 + `_grid_positions` L81-L91 + `_perforated_shell`（CadQuery boolean 钻孔阵）L94-L159 | eligible if compatible | 规则圆孔通风壁：solid shell 上 `pushPoints(grid).circle(HOLE_R).extrude` 布尔挖孔阵（四壁 X/Y-facing），floor 保实；单 box_shell visual |

硬约束记录：wall_surface 3 candidate（solid / slatted / perforated，达下限 3）。三者改 box_shell root 的 mesh 发射（实体 cut ↔ 角柱+板条循环 ↔ 布尔挖孔阵），真实改变 box_shell 的 part 内 visual 组 / 几何拓扑。slatted / perforated 无独立 joint（壁本身不活动），活动关节由 closure 槽保证。

> **walls 内 slat / hole 数量注记**：slatted 的 `N_SLATS`（每墙板条数）与 perforated 的孔阵密度 **随箱体高度 / 尺寸自适应派生**（`N_SLATS` ← INNER_H / slat_pitch；孔阵 ← `_grid_positions` 扫描范围），属 controlled local parameterization，**不作为独立 multiplicity 采样轴**（见 §8）。

## 槽位图（slot graph）

pattern: mixed（box_shell 为 root 坐地 z=0；closure / interior 挂到它 parallel children；interior=dividers 含一根 N multiplicity 轴）

```
box_shell(wall_surface, [interior 固定 visual])  [ROOT, 坐地 z=0; mesh 由 wall_surface 决定]
   │  (wall_surface ∈ {solid: _shell_solid/_box_base_solid | slatted: 角柱+_slat_board 循环 | perforated: _perforated_shell})
   │  (+ interior 固定 visual: stacking_lip 的 inner_lip+groove / liftout_tray 的 inner_ledge，挂 box_shell，无 joint)
   │
   ├── closure_mechanism = four_top_flaps:
   │     box_shell --[box_to_flap_{n,s,e,w}: REVOLUTE ±X/±Y @ 顶 rim 内边]--> flap_{n,s,e,w}  (×4)
   │
   ├── closure_mechanism = liftoff_telescoping_lid:
   │     box_shell --[box_to_lid: PRISMATIC +Z @ 箱顶 BOX_H]--> lid (skirt 罩 over 箱顶外壁)
   │
   ├── closure_mechanism = rear_hinged_flat_lid:
   │     box_shell --[base_to_lid: REVOLUTE -X @ 后 rim (0,HINGE_Y,HINGE_Z)]--> lid (+黄铜 knuckle 装饰)
   │
   ├── closure_mechanism = sliding_drawer:
   │     box_shell(闭顶+前壁开口) --[body_to_drawer: PRISMATIC -Y @ (0,-HY,joint_z)]--> drawer (tray)
   │
   ├── closure_mechanism = swing_double_door:
   │     box_shell(开前壁) --[door_0_hinge: REVOLUTE -Z @ (-IN_HX,-HY,HGT/2)]--> door_0
   │                       --[door_1_hinge: REVOLUTE +Z @ (+IN_HX,-HY,HGT/2)]--> door_1
   │
   └── closure_mechanism = front_drop_door:
         box_shell(闭顶+前壁开口) --[door_hinge: REVOLUTE +X @ 底前 rim (0,-HY,WALL)]--> front_door
   │
   ├── interior_structure = plain:        (无内部 part / joint)
   ├── interior_structure = liftout_tray:
   │     box_shell --[base_to_tray: PRISMATIC +Z @ TRAY_SEAT_Z]--> tray (rim 坐 inner_ledge)
   ├── interior_structure = stacking_lip:  (inner_lip + groove 固定 visual，无 joint)
   └── interior_structure = compartment_dividers_N (multiplicity, N ∈ [1,8]):
         for i in range(N):
           box_shell --[base_to_divider_i: PRISMATIC +Z @ (DIVIDER_XS[i],0,BASE_T)]--> divider_i
```

接口点位与 joint 语义：
- **flaps 接口**：`box_to_flap_*` origin 落在顶 rim 内边（`(0,±HINGE_INSET,z)` / `(±HINGE_INSET,0,z)`），axis ±X / ±Y，REVOLUTE 闭合 q=0 平躺、正 q 翻起 ~90–110°；`_flap_slab` 共享 helper、`flap_defs` 循环。
- **liftoff 接口**：`box_to_lid` origin 在箱顶 `(0,0,BOX_H)`，axis +Z PRISMATIC（无旋转），q=0 skirt 罩下 / 正 q 直升脱离；盖 skirt 罩 over 箱顶外壁是 captured / 友配（element-scoped allow_overlap）。
- **rear_hinge 接口**：`base_to_lid` origin 在后 rim `(0,HINGE_Y,HINGE_Z)`，axis -X，REVOLUTE 闭合 q=0、上掀正 q；黄铜 knuckle 为装饰 visual（interleaved，allow_overlap 共享铰线）。
- **drawer 接口**：`body_to_drawer` origin 在前壁中心 `(0,-HY,joint_z)`，axis -Y PRISMATIC，q=0 前 face 平箱壁 / 正 q 前抽（max 行程保留 ~40mm 插入，drawer tray ↔ shell cavity 是 captured，allow_overlap）。
- **swing 接口**：`door_{i}_hinge` origin 在前壁侧边立柱 `(±IN_HX,-HY,HGT/2)`，axis ∓Z（立轴），REVOLUTE 闭合 q=0、外摆正 q ~90°；两门中缝 seam gap，`for` 循环发射。
- **drop_door 接口**：`door_hinge` origin 在底前 rim `(0,-HY,WALL)`，axis +X，REVOLUTE 闭合 q=0 竖立 / 正 q 门顶前倾下落 ~85°。
- **tray 接口**：`base_to_tray` origin 在 ledge 坐位 `(0,0,TRAY_SEAT_Z)`，axis +Z PRISMATIC，q=0 rim 坐 inner_ledge / 正 q 提出；`inner_ledge` 为 box_shell 固定 visual。
- **divider 接口**：`base_to_divider_i` origin 在 floor 插槽 `(DIVIDER_XS[i],0,BASE_T)`，axis +Z PRISMATIC，q=0 落底 / 正 q 提出；N 块等距，统一上下限。
- **seal / wall 固定 visual 接口**：stacking_lip 的 inner_lip+groove、slatted 角柱+板条、perforated 孔阵均为 box_shell 内固定 visual，无独立 joint。
- **mating policy**：盖罩 / drawer-in-cavity / 隔板插槽 / tray-on-ledge 均为 captured / 友配（故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（落在真实 rim / hinge / floor 插槽硬件）+ element-scoped `allow_overlap` 守 overlap（见各 record run_tests 的 `ctx.allow_overlap`）。
- **rest pose**：所有 closure q=0 闭合 / 坐下 / 插入；tray / divider q=0 落座；lip / groove / ledge / 板条 / 孔阵固定。closure 开合 + tray/divider 提出为 viewer 目检的活动语义。
- **互斥 / 可选**：`interior=plain` 是空机构；closure 各候选互斥（一次一种）；wall_surface 各候选互斥。divider N 仅在 interior=compartment_dividers_N 时存在。

## 每槽位 Module Emits / Interfaces

### Slot C / box_shell（wall_surface，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `box_shell` / `body` / `box` / `box_base`（visual: shell mesh，由 wall_surface 决定 solid/slatted/perforated）| ef4e9e5a `_shell_solid` L56-L71 / c87d6c10 `_box_base_solid` L49-L91 / slatted `_corner_posts_solid`+`_slat_board` L82-L180 / perforated `_perforated_shell` L94-L159 |
| internal joints | 无（root 箱壁本身不活动）| — |
| upstream interface | 坐地 z=0（root）| — |
| downstream interface | 顶 rim / 前壁开口 / 后 rim / floor 插槽 / ledge 坐位（closure / interior joint 的 parent 接口）| 各 record 的 origin |

### Slot A / closure_mechanism（每候选发射对应活动闭合件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `flap_{n,s,e,w}`(×4) / `lid`(liftoff) / `lid`+knuckle(rear_hinge) / `drawer` / `door_0`+`door_1` / `front_door` | 各 closure 源 |
| internal joints | `box_to_flap_*` REVOLUTE ±X/±Y(×4) / `box_to_lid` PRISMATIC +Z / `base_to_lid` REVOLUTE -X / `body_to_drawer` PRISMATIC -Y / `door_{i}_hinge` REVOLUTE ∓Z(×2) / `door_hinge` REVOLUTE +X | 0c476a9b L118-L143 / 3386fca8 L164-L174 / c87d6c10 L225-L235 / drawer L196-L209 / swing L194-L204 / drop L173-L185 |
| downstream interface | closure 闭合姿态 = q=0；箱顶 / 前壁 / 后 rim / 底前 rim mating face | 各 record |

### Slot B / interior_structure（≠plain 时，固定 visual / multiplicity 挂 box_shell）
| emits | 描述 | 来源 |
|---|---|---|
| parts | plain: 无 / liftout_tray: `tray`+`inner_ledge`(visual) / stacking_lip: `inner_lip`+groove(visual) / compartment_dividers_N: `divider_i`(×N) | liftout L211-L408 / stacking L101-L108 / dividers L163-L295 |
| internal joints | plain/stacking_lip: 无 / liftout_tray: `base_to_tray` PRISMATIC +Z / compartment_dividers_N: `base_to_divider_i` PRISMATIC +Z(×N) | liftout L398-L408 / n2 L285-L295 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| closure_mechanism | enum | four_top_flaps / liftoff_telescoping_lid / rear_hinged_flat_lid / sliding_drawer / swing_double_door / front_drop_door | four_top_flaps | choice | deterministic procedural sampler 选 | module table |
| interior_structure | enum | plain / liftout_tray / stacking_lip / compartment_dividers_N | plain | choice | sampler 选；含空机构 | module table |
| wall_surface | enum | solid / slatted / perforated | solid | choice | sampler 选 | module table |
| divider_count | int | [1, 8] | 2 | conditional | 仅 interior=compartment_dividers_N 时存在；加权采样（小 N 偏多）；上限随箱宽派生 clamp（见 §8）| n2/n4 records |
| palette_style | enum | kraft_corrugated / white_gift / white_gift_gloss / walnut_keepsake / natural_crate / gray_shipping / black_rigid_gift / red_gift / forest_gift / printed_kraft（10 colorway + finish 维度）| kraft_corrugated | palette | palette only，**不计入 slot_choice**；per-seed `rng.choice`；每 colorway 带显式 finish | 见下 palette 表 |
| box_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放箱高 HGT/BODY_H → closure mount 高度 + 板条 N_SLATS 派生，clamp | resolve clamp |
| box_footprint_scale | float | [0.88, 1.18] | 1.0 | independent | 缩放箱足迹 LEN_X/DEP_Y / 立方边 → 内腔 / 开口 / divider 跨度同比，clamp | resolve clamp |
| wall_thickness_scale | float | [0.80, 1.25] | 1.0 | independent | 缩放 WALL（壁厚 / 板条厚 / 翻盖厚），clamp（保 ≥ 内腔 clearance）| resolve clamp |
| closure_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 PRISMATIC 行程（lid lift / drawer / tray / divider lift）+ REVOLUTE open limit，clamp | resolve clamp |
| (—) | constraint | — | — | inequality | drawer / tray / divider 行程：`travel ≤ cavity_depth/height − retain_margin`（drawer 保 ~40mm 插入、tray/divider 不脱顶），违反按比例回缩 | 接口 / clearance |
| (—) | constraint | — | — | conditional | `divider_count` 上限：`N ≤ floor(inner_width / min_compartment)`（箱宽上限自然封顶），违反 clamp 到可行 N | n4 record L54-L60 |
| (—) | constraint | — | — | conditional | wall_surface=slatted 时 `N_SLATS = round(inner_h / slat_pitch)` 派生；=perforated 时孔阵由 `_grid_positions` 扫描派生（均非独立轴）| slatted L51 / perforated L81-L91 |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`divider_count` 上限 conditional 依箱宽；行程 inequality 在 resolve 投影 / 回缩，不留到 builder。scale 只动安全比例 / clearance / 细节尺寸，绝不改 closure / interior / walls 的拓扑。

### palette_style 颜色板（≥3，本表 10 配色 + 显式 finish 维度，per-seed `rng.choice`，不计 slot_choice）

每个 colorway = **body（箱体 / box_shell）+ closure/lid（闭合件 / 盖 / 门 / 抽屉）+ interior（内件 / 内胆 / 隔板 / tray）+ label/accent（印刷 / 标签 / 丝带 / 铰链 accent）+ finish（材质表面处理维度）**。`finish` 是显式材质处理维度（非 rgba），realistic paper/wood/board 范围：`kraft_corrugated_matte`（瓦楞 kraft 哑光）/ `white_gift_matte`（白礼盒哑光层压）/ `white_gift_glossy`（白礼盒高光层压）/ `wood_grain_natural`（实木 / 胡桃 / 松木天然木纹）/ `shipping_board_matte`（灰运输板哑光）/ `rigid_gift_black_matte`（黑硬质礼盒哑光裱纸）/ `colored_gift_satin`（彩礼盒缎面）/ `printed_graphic`（满版印刷图形）。每个 colorway 显式标注一个 finish。

| palette_style | body rgba（box_shell）| closure/lid rgba | interior rgba（内件 / 隔板 / tray）| label/accent rgba | finish |
|---|---|---|---|---|---|
| kraft_corrugated（基线）| kraft `(0.78,0.62,0.40,1)` | kraft_flap `(0.80,0.69,0.49,1)` | kraft_inner `(0.72,0.56,0.36,1)` | print_ink `(0.20,0.20,0.22,1)` | kraft_corrugated_matte |
| white_gift | white_board `(0.93,0.92,0.90,1)` | white_lid `(0.95,0.94,0.92,1)` | label_paper `(0.90,0.86,0.78,1)` | ribbon_gray `(0.55,0.55,0.58,1)` | white_gift_matte |
| white_gift_gloss | white_board `(0.96,0.96,0.95,1)` | white_lid `(0.97,0.97,0.96,1)` | satin_liner `(0.88,0.88,0.90,1)` | silver_foil `(0.78,0.79,0.82,1)` | white_gift_glossy |
| walnut_keepsake | walnut `(0.36,0.22,0.13,1)` | walnut `(0.36,0.22,0.13,1)` | maple_accent `(0.82,0.66,0.42,1)` | brass `(0.74,0.58,0.26,1)` | wood_grain_natural |
| natural_crate | pine `(0.74,0.60,0.40,1)` | pine `(0.74,0.60,0.40,1)` | cedar_divider `(0.62,0.46,0.30,1)` | maple_accent `(0.82,0.66,0.42,1)` | wood_grain_natural |
| gray_shipping | gray_board `(0.62,0.60,0.58,1)` | gray_board `(0.62,0.60,0.58,1)` | gray_inner `(0.56,0.55,0.53,1)` | print_ink `(0.20,0.18,0.15,1)` + tape `(0.82,0.75,0.55,0.7)` | shipping_board_matte |
| black_rigid_gift | black_board `(0.13,0.13,0.14,1)` | black_board `(0.13,0.13,0.14,1)` | charcoal_liner `(0.22,0.22,0.24,1)` | gold_foil `(0.80,0.66,0.30,1)` | rigid_gift_black_matte |
| red_gift | crimson_board `(0.66,0.16,0.16,1)` | crimson_board `(0.66,0.16,0.16,1)` | label_paper `(0.90,0.86,0.78,1)` | gold_accent `(0.80,0.66,0.30,1)` | colored_gift_satin |
| forest_gift | forest_board `(0.18,0.34,0.24,1)` | forest_board `(0.18,0.34,0.24,1)` | kraft_inner `(0.72,0.56,0.36,1)` | gold_accent `(0.80,0.66,0.30,1)` | colored_gift_satin |
| printed_kraft | kraft `(0.78,0.62,0.40,1)` | kraft_flap `(0.80,0.69,0.49,1)` | kraft_inner `(0.72,0.56,0.36,1)` | brand_ink `(0.16,0.30,0.42,1)` + accent_ochre `(0.84,0.58,0.22,1)` | printed_graphic |

> finish 维度说明：`finish` 是显式材质处理标注（matte / glossy laminated / natural wood grain / satin / printed-graphic），与 rgba 正交——同一 body rgba 可配不同 finish（如 white_gift 哑光 vs white_gift_gloss 高光），故 finish 单列一维。realistic 锚定：kraft / white_gift / walnut / natural_crate / gray_shipping / red_gift 6 板直接来自 5★ 材质 rgba（见下灵感来源）；white_gift_gloss（白高光层压礼盒）/ black_rigid_gift（黑硬质裱纸礼盒）/ forest_gift（森绿缎面礼盒）/ printed_kraft（满版印刷瓦楞）4 板为 realistic 推演 colorway（纸 / 板范围内，非 metallic-neon）。本表 10 distinct colorway（kraft_corrugated 为基线，计入 10）。

| palette_style | 灵感来源（5★ 材质）|
|---|---|
| kraft_corrugated | ef4e9e5a / drawer / perforated 瓦楞 kraft `(0.78,0.62,0.40)` + kraft_inner `(0.72,0.56,0.36)` + print_ink；0c476a9b kraft_flap `(0.80,0.69,0.49)` |
| white_gift | 3386fca8 礼盒 label_paper `(0.90,0.86,0.78)`（白礼盒哑光层压变体）|
| white_gift_gloss | 3386fca8 白礼盒 → 高光层压推演（同纸礼盒族，finish 换 glossy）|
| walnut_keepsake | c87d6c10 胡桃木 `(0.36,0.22,0.13)` keepsake + maple `(0.82,0.66,0.42)` spline + brass `(0.74,0.58,0.26)` 黄铜铰 |
| natural_crate | slatted crate 松木板条 + maple `(0.82,0.66,0.42)` 角柱 + n2 cedar_divider `(0.62,0.46,0.30)` 隔板 |
| gray_shipping | 0c476a9b 运输箱 print_ink decal + roll_top packing_tape（灰板运输推演）|
| black_rigid_gift | 黑硬质裱纸礼盒 + gold_foil（realistic rigid gift colorway 推演，纸板范围）|
| red_gift | 3386fca8 礼盒 diamond label + gold accent（红金礼盒缎面，realistic gift colorway 推演）|
| forest_gift | 森绿缎面礼盒 + gold accent + kraft 内衬（realistic colored gift 推演）|
| printed_kraft | ef4e9e5a/0c476a9b 瓦楞 kraft 体 + 满版品牌印刷（realistic printed-graphic 推演）|

palette_style 仅换材质 rgba + finish 标注，不改结构 / 拓扑（材质 / 表面处理差异不是 candidate，§2.4）。closure / interior / walls 的 closure-piece / 内件 / accent 材质 + finish 统一由 palette_style 派生。

## Multiplicity / Copy Logic

本 spec 有 **1 根 multiplicity 轴**（divider_count），仅在 interior_structure=compartment_dividers_N 时激活。

- `count_param`：`divider_count`（interior 槽内的竖隔板复制数）。
- `N_range`：`divider_count ∈ [1, 8]`（本小类本轴的产品域；测试偏小 N={1,2,3,4}，产品全程到 8；箱宽上限处自然封顶）。已覆盖样本 N={2, 4}（n2_dividers / n4_dividers）。
- sampling domain（权重档）：小 N 高频、大 N 稀有 —— 建议权重 N=1:0.10 / N=2:0.30 / N=3:0.22 / N=4:0.18 / N=5:0.10 / N=6:0.06 / N=7:0.025 / N=8:0.015（小 N 偏多，尾部稀有）。每 build 对该轴做一次加权采样，编进 `slot_choices`，clamp 到箱宽派生上限。
- copied object：单块竖隔板（`_divider_solid` 共享 helper，DIV_T 薄板 × cavity 深 × cavity 高）。
- naming：`divider_i`（i=0..N-1）+ joint `base_to_divider_i`。
- placement：沿 +X 等距插槽 `DIVIDER_XS = [-IW/2 + (i+1)·IW/(N+1) for i in range(N)]`，落在底面 floor（z=BASE_T），把内腔分成 N+1 等宽 compartment。
- joint policy：每块独立 `base_to_divider_i` PRISMATIC +Z 提出，统一 motion_limits（lower=0, upper≈0.10·closure_travel_scale clamp），origin 在各自插槽 floor。
- source / gating：n2 record L270-L295（`for i in range(N_DIVIDERS)` + `_divider_solid` + `base_to_divider_i`）；n4 record `DIVIDER_N=4` L54。**gating**：仅 interior=compartment_dividers_N 暴露；N 上限 `floor(inner_width / min_compartment_width)`，超限 clamp。

> walls 内 slat / hole 数量是 box_shell 局部 controlled parameterization（随尺寸派生），**不是** 独立 multiplicity 采样轴（不暴露 `slat_count` / `hole_count` 给 sampler）。仅 divider_count 是模板级 multiplicity 轴。

## 拓扑多样性审计

总组合数：closure_mechanism(6) × interior_structure(4) × wall_surface(3) = **72** 基础结构组合。
含 divider N 轴：interior=compartment_dividers_N 时再乘 N 采样档（[1,8] 取 ~4 个有效拓扑等价类样本 {1,2,4,8}）→ 远超门槛。

仅 closure_mechanism × interior_structure = **24 ≥ 10** 已可过门控；叠 wall_surface(72) + divider N 后充裕。

理由：本类拓扑多样性来源充裕——closure(6) × interior(4) 的笛卡尔积即 24 distinct，远超 10；closure 引入 REVOLUTE ±X/±Y(flaps ×4) / PRISMATIC +Z(liftoff) / REVOLUTE -X(rear_hinge) / PRISMATIC -Y(drawer) / REVOLUTE ∓Z(swing ×2 立轴) / REVOLUTE +X(drop ×1 底轴) 等不同 joint 拓扑 + 不同 part / joint count（1/2/4 活动件），是真实结构差异。interior 在 plain↔tray(+1 PRISMATIC)↔stacking(固定 visual)↔dividers(+N PRISMATIC) 间改 part tree。wall_surface 改 box_shell mesh 发射（实体 / 板条循环 / 布尔挖孔）。slot_choices 编入三轴 + divider N。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 加权 `rng.choice` 三个 named slot（笛卡尔积近全合法，少量 gating 见下），若 interior=compartment_dividers_N 再对 divider_count 做加权采样（小 N 偏多），再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除 / 适配少量组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计 ~72 基础 +（dividers 分支的 N 等价类）→ 接近 100。低于 300 的部分原因：本小类真实结构词汇就是 6 closure × 4 interior × 3 walls = 72 基础组合 + 1 根 divider N 轴，是该类目的合理上限，不强行注水。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 4 个 scale（box_height / box_footprint / wall_thickness / closure_travel）+ divider_count（conditional multiplicity）。全部 `resolve_config` clamp + 每 build 统一应用。`divider_count` 上限 conditional 依箱宽；行程 inequality（drawer/tray/divider travel ≤ cavity − retain_margin）在 resolve 内投影 / 回缩，不留到 builder。slatted `N_SLATS` / perforated 孔阵由箱高 / 尺寸派生（conditional，非独立轴）。这些 scale 不破坏 closure joint origin（顶 rim / 后 rim / 前壁 / 底前 rim / floor 插槽 / ledge）、盖罩 / drawer-in-cavity / 隔板插槽配合、interior 位置或类别身份。按 §7 约束类型声明：4 scale 为 independent，divider 上限 + slat/hole 数 + 行程为 conditional/inequality，遵循连续尺寸采样契约（先采 independent → 派生 → 投影回缩 → 解析 conditional）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 加权 `rng.choice` 三 named slot（近全正交），dividers 分支再加权采 N，再 uniform 各 scale + palette_style | slot_choices_for_seed 含三轴 + divider N 且与 build 一致 |
| compatibility matrix | (1) `sliding_drawer` / `swing_double_door` / `front_drop_door` 需要相应箱壁开口（前壁开口 / 闭顶），与 wall_surface=perforated/slatted 组合时：drawer/door 占据前壁，板条 / 孔阵在其余三壁发射（resolve 解析前壁让位，不 gate 掉）。(2) `liftoff_telescoping_lid` 盖 skirt 罩 over 箱顶外壁 → captured 友配，element-scoped allow_overlap（不发独立长 neck）。(3) closure × interior 近全正交，但 `liftoff_telescoping_lid` + `compartment_dividers_N`：盖直升、隔板独立提出，二者不冲突（divider 提出行程 ≤ 盖内净高）；`rear_hinged_flat_lid` / `four_top_flaps` + dividers 同理可共存。(4) `interior=liftout_tray` 占内腔上层、`compartment_dividers_N` 占下层——二者互斥（同一 interior 槽，一次一种）。(5) wall_surface 各候选互斥；closure 各候选互斥。(6) divider_count 上限随箱宽 clamp。无硬 gate-out（72 基础组合全合法，只在 resolve 派生尺寸 / 前壁让位适配）| 无 floating / collision / closure 穿箱 / drawer 脱出 / divider 脱顶 / joint 轴或 origin 错位 |
| controlled local variation | 4 个 clamped scale + divider_count conditional + slat/hole 派生，每 build 统一 | 比例变化不破坏 closure joint origin / 盖罩 / drawer-in-cavity / 隔板插槽配合 / 坐地 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | closure 动作 / 坐地 / overlap / divider N QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| closure_mechanism | 6 | yes | yes | flaps(REV ±X/±Y ×4) / liftoff(PRIS +Z) / rear_hinge(REV -X) / drawer(PRIS -Y) / swing(REV ∓Z ×2) / drop(REV +X) |
| interior_structure | 4 | yes | yes | plain 空 + liftout_tray(+1 PRIS) + stacking_lip(固定 visual) + compartment_dividers_N(+N PRIS, multiplicity) |
| wall_surface | 3 | yes | yes | solid 实体 + slatted 板条循环 + perforated 布尔挖孔 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (closure_mechanism, interior_structure, wall_surface) 三轴 + interior=dividers 时的 divider_count
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（加权 slot + 加权 divider N + uniform scale + rng palette_style）
- `resolve_config` 各 scale clamp 到声明范围；divider_count 上限按箱宽 conditional 派生；行程 inequality（drawer/tray/divider ≤ cavity − retain_margin）在 resolve 投影 / 回缩；slat/hole 数随尺寸派生
- compatibility matrix / gating：72 基础组合全合法（无硬 gate-out），drawer/door + slatted/perforated 时前壁让位在 resolve 派生
- 连续 scale clamp 后不破坏 closure joint origin / 盖罩 / drawer-in-cavity / 隔板插槽 / 坐地 / 类别身份
- 关键 joint：four_top_flaps `box_to_flap_*` REVOLUTE ±X/±Y(×4) (abs 主轴分量>0.99)；liftoff `box_to_lid` PRISMATIC +Z；rear_hinge `base_to_lid` REVOLUTE -X (abs(axis[0])>0.99)；drawer `body_to_drawer` PRISMATIC -Y；swing `door_{i}_hinge` REVOLUTE ∓Z(×2) (abs(axis[2])>0.99)；drop `door_hinge` REVOLUTE +X；tray `base_to_tray` PRISMATIC +Z；divider `base_to_divider_i` PRISMATIC +Z(×N)
- captured-fit：element-scoped `allow_overlap`（lid skirt ↔ box_shell 罩配 / drawer tray ↔ shell cavity / divider ↔ shell floor / tray ↔ inner_ledge / 翻盖相邻角 ↔ 角 / knuckle ↔ knuckle 共享铰线）
- grandfather：盖罩 / drawer / 插槽 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守
- copied objects：divider_i 遵循 `_divider_solid` 共享 helper + `DIVIDER_XS` 等距 placement + 统一 `base_to_divider_i` PRISMATIC joint policy
- palette_style 仅换材质 rgba + finish 标注（10 colorway），不计 slot_choice，不改拓扑

## Reject cases

- closure_mechanism 造成无任何活动关节的死盒（0 non-fixed joint）→ 违反类别身份（Box 必须 ≥1 closure 活动机构）；magnetic_clasp / friction_press_fit 等无关节闭合不立候选（source map §排除项）。
- closure joint origin 放在箱底 / 任意点而非顶 rim / 后 rim / 前壁 / 底前 rim / floor 插槽真实硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- closure rest pose 设成张开 / 抬起而非 q=0 闭合（盖翻起 / 门外摆 / 抽屉拉出）→ current-pose 与 viewer 目检不符。
- drawer 行程超内腔深（脱出无插入）/ tray / divider 提出脱顶 → 行程 inequality 未在 resolve 回缩，FAIL。
- divider_count 超箱宽上限（compartment 过窄 / 隔板互穿）→ conditional clamp 缺失，collision FAIL。
- 给 captured-fit（盖罩 / drawer-in-cavity / 插槽 / tray-on-ledge）补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + element-scoped allow_overlap。
- 把 roll_top_tambour 当真卷帘（N 段链式曲线 rail）造 → SDK 无曲线 prismatic，不收敛；本 spec 只采该 record 的 front_drop_door 单铰形态。
- 把 palette_style / 尺寸 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice；slat/hole 数是局部派生非 multiplicity）。
- 给箱补提把轴当 bag_suitcase / 造米级钢货柜当 shipping_container → 出 Box 类目身份（无提把、桌面尺度纸木材质）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。6 closure × 4 interior × 3 walls = 72 基础组合；closure×interior=24；+ 1 根 divider_count multiplicity 轴 [1,8]（样本 N={2,4}）。closure 含 REVOLUTE(flaps×4 / rear_hinge / swing×2 立轴 / drop 底轴) + PRISMATIC(liftoff +Z / drawer -Y) 两种 joint 拓扑。palette_style 10 colorway + 显式 finish 维度（kraft_corrugated/white_gift/white_gift_gloss/walnut_keepsake/natural_crate/gray_shipping/black_rigid_gift/red_gift/forest_gift/printed_kraft；finish ∈ matte/glossy laminated/natural wood grain/satin/printed-graphic；6 板锚 5★ rgba + 4 板 realistic 推演）。13 records 全读。与 bag_suitcase_box（提把可携带）/ container_shipping_container（米级钢货柜）边界已划。开放问题见下。|

## 与相邻类别的边界

- 不该混入：**bag_suitcase_box（手提 bag-box / 行李箱体）**——理由：有提把 / 可携带，closure 是拉链 / 搭扣 + 提携；container_box 是固定放置储物箱，无提把轴，closure 是盖 / 门 / 抽屉。
- 不该混入：**container_shipping_container（米级钢货柜 / 集装箱）**——理由：巨型钢制货柜（ISO 角件 + 波纹钢 + 双开后门，米级、车货运输）；container_box 是桌面 / 手持尺度（~0.1–0.3 m）纸 / 木储物箱，材质 palette 纸木非工业钢。
- 不该混入：**container_basket / 收纳篮 / 购物篮**——理由：有 bail 提把 + 嵌套堆叠 multiplicity + 编织 / 网孔篮身；container_box 方盒带盖机构，perforated 是通风圆孔（非编织），无提把无嵌套。

## 模板实现备注（可选）

- 共享 helper：`_box_shell(wall_surface, footprint, height)` 统一发射 root（solid: `box`+内腔`cut`；slatted: `_floor_panel`+`_corner_posts`+`_slat_board` 循环；perforated: solid + `_grid_positions`+`pushPoints.circle.extrude` 布尔挖孔）。closure helper 各自：`_flap_slab` + `flap_defs` 循环 / `_lid_solid`(liftoff skirt) / `_lid_solid`+knuckle(rear_hinge) / `_drawer_tray` / `_door_panel(side)` / `_door_panel`(drop)。interior：`_inner_ledge_solid`+`_tray_*_solid` / `_inner_lip`+`_box_shell_with_groove`(`_rect_ring`) / `_divider_solid` 循环。
- captured-fit overlap：`run_container_box_tests` 里 element-scoped `ctx.allow_overlap`：lid skirt↔box_shell（liftoff 罩配）/ drawer tray↔shell cavity / divider_i↔box_shell floor / tray↔inner_ledge / 翻盖相邻角↔角 / knuckle↔knuckle 共享铰线（复制各 record 的 allow_overlap）。
- divider_count multiplicity：`for i in range(N)` 发射 `divider_i` + `base_to_divider_i`，`DIVIDER_XS` 等距，N 上限 resolve clamp；仅 interior=compartment_dividers_N 激活。
- 行程 inequality：`resolve_config` 派生 drawer/tray/divider travel ≤ cavity_depth/height − retain_margin（drawer 保 ~40mm 插入），在 resolve 投影回缩。
- drawer/door + slatted/perforated 组合：前壁开口让位，板条 / 孔阵在其余三壁发射（resolve 解析）。
- 参考模板（实现阶段深读，按 slot graph / 运动拓扑选，非类名）：`agent/templates/Chair_Folding_chair.py`（Config/ResolvedConfig + `config_from_seed` + `resolve_config` clamp + `slot_choices_for_config` + allow_overlap 骨架）；`agent/templates/Container_Jar.py`（parallel_children 多 closure 机构分支 + captured-fit grandfather）；含 multiplicity 轴的 fence/divider 类模板（divider N 加权采样 + `for i in range(N)` 复制 helper）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/C | four_top_flaps + solid（瓦楞）| rec_open-corrugated-..._ef4e9e5a | `_shell_solid` L56-L71 / `_flap_solid` L74-L82 / `long_flap_*_hinge`+`short_flap_*_hinge` L147-L237 | 瓦楞 solid 壁基线 + 四 fold-out 翻盖（REVOLUTE ~110°）|
| S2 | A | four_top_flaps（闭态干净循环）| rec_closed-kraft-..._0c476a9b | `_box_shell` L38-L48 / `_flap_slab` L51-L60 / `flap_defs` L100-L116 / `box_to_{flap}` L118-L143 | 四顶盖闭态 + `flap_defs` 最干净复制循环 |
| S3 | A/C | liftoff_telescoping_lid + solid | rec_kraft-..._3386fca8 | `_box_base_solid` L39-L56 / `_lid_solid` L59-L83 / `box_to_lid` PRISMATIC +Z L164-L174 | 望远镜升降盖（PRISMATIC +Z lift-off skirt 罩配）|
| S4 | A/C | rear_hinged_flat_lid + solid（指接木）| rec_wooden-keepsake-..._c87d6c10 | `_box_base_solid` L49-L91 / `_lid_solid` L123-L133 / `base_to_lid` REVOLUTE -X L225-L235 / knuckle L170-L215 | 后铰平盖（REVOLUTE -X @ 后 rim）+ 黄铜铰 + 指接角 solid 壁 |
| S5 | A | sliding_drawer | rec_container_box_var_sliding_drawer | `_shell_solid`(闭顶+前开口) L61-L90 / `_drawer_tray` L93-L119 / `body_to_drawer` PRISMATIC -Y L196-L209 | 火柴盒抽屉（PRISMATIC -Y 前抽，captured in cavity）|
| S6 | A | swing_double_door | rec_container_box_var_swing_double_door | `_shell_solid`(开前壁) L61-L81 / `_door_panel(side)` L84-L115 / `door_{i}_hinge` REVOLUTE ∓Z L194-L204 | 前壁双开门（2× REVOLUTE 立轴，`for` 循环 + 集成 handle）|
| S7 | A | front_drop_door | rec_container_box_var_roll_top_tambour | `_shell_solid`(闭顶+前开口) L60-L84 / `_door_panel` L87-L95 / `door_hinge` REVOLUTE +X 底前 rim L173-L185 | 单前壁下翻门（REVOLUTE +X @ 底边，roll_top record 降级形态）|
| S8 | B | liftout_tray | rec_container_box_var_liftout_tray | `_inner_ledge_solid` L179-L208 / `_tray_floor/_walls/_rim_solid` L211-L274 / `base_to_tray` PRISMATIC +Z L398-L408 | 浅升降内托盘（PRISMATIC +Z 落 ledge）|
| S9 | B | stacking_lip | rec_container_box_var_stacking_lip | `_rect_ring` L59-L72 / `_box_shell_with_groove` L76-L97 / `_inner_lip` L101-L108 | 叠箱凸唇 + 底脚环（固定 visual，无 joint）|
| S10 | B | compartment_dividers_N | rec_container_box_var_n2_dividers（N=2）/ rec_container_box_var_n4_dividers（N=4）| `_divider_solid` L163-L172 / `for i in range(N)` `divider_i` L270-L295 / `base_to_divider_i` PRISMATIC +Z L285-L295 | N 块竖隔板 multiplicity 轴（PRISMATIC +Z 提出，N={2,4} 样本）|
| S11 | C | slatted_walls | rec_container_box_var_slatted_walls | `_slat_board` L58-L67 / `_corner_posts_solid` L82-L100 / 4 墙 ×N_SLATS `for` 循环 L169-L180 | 板条 crate 壁（角柱 + 横板条循环 + 间隙）|
| S12 | C | perforated_walls | rec_container_box_var_perforated_walls | `_grid_positions` L81-L91 / `_perforated_shell` L94-L159（布尔挖孔阵）| 圆孔通风壁（CadQuery boolean 钻孔阵）|

## 开放问题（reviewer 注意）

1. **handle / hardware 轴未立**：四 parent 均无独立提手机构（keepsake 黄铜铰仅装饰），Box 提手词汇稀薄。暂不立 handle 槽（折入未来 hardware 扩展），与 bag_suitcase_box（提把身份）划清边界。reviewer 确认是否同意不强造空 handle 候选。
2. **closure × wall_surface 前壁让位**：drawer / swing / drop 占前壁开口，与 slatted / perforated 组合需在 resolve 让前壁，其余三壁发板条 / 孔阵。reviewer 确认该派生策略（不 gate-out）可接受，还是收窄为 drawer/door 仅配 solid。
3. **palette_style 10 colorway + finish 维度，含 4 板 realistic 推演**：6 板（kraft_corrugated/white_gift/walnut_keepsake/natural_crate/gray_shipping/red_gift）锚定 5★ rgba（red_gift 主体由 3386fca8 礼盒 label_paper + gold 推演），4 板（white_gift_gloss/black_rigid_gift/forest_gift/printed_kraft）为 realistic 纸/板范围内推演 colorway（非 metallic-neon），各带显式 finish（matte / glossy laminated / natural wood grain / satin / printed-graphic）。reviewer 确认是否保留全部 10 板或收窄到仅 5★-锚定的 6 板。
