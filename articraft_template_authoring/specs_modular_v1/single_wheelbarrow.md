# single_wheelbarrow — Modular Spec

> 来源小类：`picture/Agricultural/Single-Wheelbarrow`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Agricultural__Single-Wheelbarrow.md`。
> **Single-Wheelbarrow = 单轮独轮车**：一只斗身（tub）+ 一副骨架（handles/legs/axle）+ **恰好一只**前轮；
> 两个活动关节始终并存 —— 车斗绕轴 REVOLUTE **倾倒**（body-tip，dump）+ 单轮绕轴 CONTINUOUS **旋转**（spin）。
>
> **同步状态**：本 spec 引用的 8 个 5 星样本（2 origin + 6 fork 变体）已同步进本仓库 `data/records/`，rating=5，
> workbench-only。行号 / 名字按各样本本仓库 `revisions/rev_000001/model.py` 实际内容核对；引用以 part / helper /
> joint **名字** 为准（`_wheelbarrow_tray_geometry` / `_poly_tub_geometry` / `_flat_deck_geometry` / `_solid_disc_wheel_geometry` /
> `side_{side}_slat_{row}` / `handle_rail_{i}` / `axle` / `axle_pivot_to_barrow` / `axle_pivot_to_wheel` 等），行号仅作定位。
>
> **坐标约定统一**：origin A 家族（钢斗）长轴沿 **+Y**、宽沿 X、前轮在 -Y；origin B 家族（木斗）长轴沿 X。
> 两家族坐标不同。本模板**统一采用 A 约定**（`AXLE_PIVOT=(0.0,-0.60,0.25)`，长轴 +Y，宽 X，前轮在 -Y，
> 两关节 axis=(1,0,0)），把 origin B 的 wood_slat_box / wood_runner / wood_spoked 三模块**重表达进 A 约定**
> （X↔Y 语义互换：板条沿 Y、侧墙在 ±X、把手伸向 +Y）。这样任意 tub × frame × wheel 组合坐标一致、可装配。

## 元信息
| 项 | 值 |
|---|---|
| slug | `single_wheelbarrow` |
| template path | `agent/templates/single_wheelbarrow.py` |
| test path (optional) | `tests/agent/test_single_wheelbarrow_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（root pivot `wheel_axle_pivot` 挂两 parallel child：`barrow` body-tip REVOLUTE + `wheel` spin CONTINUOUS；tub_body + frame_build 两轴都 inline 到同一 `barrow` part 的 visual，wheel_type 在 `wheel` part；外加 wood side-slat `side_slat_count` 多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（2 origin + 6 fork 变体；均 converged、compile success、含 body-tip REVOLUTE + wheel CONTINUOUS 两非-fixed joint、workbench-only）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、两 articulation、run_tests 的 allow_overlap / expect_* 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 8/8 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **共享基线拓扑（8/8 一致）**：`wheel_axle_pivot`（root，**无 visual 的纯运动学 pivot**）+ `barrow`/`barrow_body`（child，body-tip REVOLUTE）+ `wheel`/`front_wheel`（child，spin CONTINUOUS）。两 joint origin 同在轴心 `AXLE_PIVOT`；barrow 上的 `axle` 圆柱与 wheel 的 hub/rim 在轴心相交（captured-pin，`allow_overlap`）。tub 与 frame **同属 barrow part**（单刚体），二者靠 `tray_mount_*` pad ↔ frame 横梁互触连成一个几何岛。
- **tub_body 轴（Slot A，③ 主体形态）**：`_wheelbarrow_tray_geometry`（A，深压钢斗 superellipse loft）/ `_poly_tub_geometry`（plastic 变体，rotomolded 圆润厚壁 + 熔筋 flute）/ `_flat_deck_geometry`（flatbed 变体，平板 + kick-rail + 防滑条）/ wood_slat_box（B，板条箱：floor_plank + `side_{side}_slat_{row}` + upright_post + top_lip）—— 四种是核心 part 的**可识别几何形态原型**变化（体量包络 / 平面边界 / 宏观板条构成），非缩放 / 换色。
- **wheel_type 轴（Slot B，wheel part 的 ③）**：pneumatic_steel_rim（A：`TireGeometry`+`WheelGeometry` split_y 辐 + `valve_stem`）/ solid_disc（solid_wheel 变体：`_solid_disc_wheel_geometry` **LatheGeometry** 实心盘 + closed_hub + spin_marker）/ wood_spoked_cart（B：`TireGeometry`+`WheelGeometry` straight 辐 + wood 材质 + `dark_hub_shell` + `tread_marker`）。**辐条数 = `WheelSpokes(count=)` 参数，不是 slot**。
- **frame_build 轴（Slot C，① 骨架）**：tube_rail（A：`tube_from_spline_points` 弯管 handle_rail / front_guard / cross_tube / support_leg / front_strut + 三角板 axle_bracket）/ welded_flatbar（flatbar 变体：直 `Box` 梁 rail / front_guard bar / nose_bar / A-frame 腿 / flat-bar cross / flat axle_bracket / handle_stub）/ wood_runner（B：`Box` 木梁 `handle_{i}_runner` + 木腿 + 木撑 + `fork_{i}_axle_plate` 钢板 + 木 grip）—— 三种是把手 / 腿 / 轴座**骨架图（part-joint 运动学构成）**的真实差异。
- **side_slat_count 轴（Slot D 多重性）**：`rec_wheelbarrow_var_slats_n2`（N=2）/ origin B（N=3）/ `rec_wheelbarrow_var_slats_n5`（N=5）用 `for row in range(N)` 复制 `side_{side}_slat_{row}`（+ 同族 `{end}_slat_{row}` / upright_post 高度 / top_lip z 联动）。**仅 wood_slat_box tub 有板条**；其余 tub 无墙 → N 记 `n0`。

## 核心身份

一辆**单轮独轮车**（single-wheel wheelbarrow）：一只承载**斗身 tub**（深压钢斗 / 圆润聚乙烯塑料斗 / 平板砖斗 / 木板条箱四种形态之一），由一副**骨架 frame**（一对把手 + 后支撑腿 / 脚 + 前轴座 / 叉板 —— 弯钢管 / 焊接扁铁 / 木梁三种骨架之一）承托，前端**恰好一只轮**（充气钢圈胎 / 实心聚氨酯盘 / 木辐轮三种之一）。默认 Z-up，长轴沿 +Y，宽沿 X，前轮在 -Y 轴心，把手伸向 +Y、握把在约 (±0.31, 1.5, 0.96)，后腿脚落地 z≈0.03。活动语义 = **两关节始终并存**：① `barrow` 车斗绕轴心 X 轴 **REVOLUTE 倾倒**（body-tip / dump，lower=0 停放 → upper≈1.05 倾卸）；② `wheel` 单轮绕轴心 X 轴 **CONTINUOUS 旋转**（spin，无界）。默认成熟域：tub(4) × wheel(3) × frame(3) × 木斗板条数 N∈{2,3,5} 的手推独轮车。

不该混入：
- **双轮 / 多轮手推车（cart / trolley / hand-truck / wheelbarrow-with-2-wheels）**——本类**恰好一只前轮**且斗身能绕该轮轴倾倒；两轮车无单轮倾倒 spine。
- **Tipping barrow / 翻斗车（Urban_Environment_Tipping_Barrow）** 等大型翻斗设备——本类是人力小型独轮车，把手 + 单轮 + 后腿。
- **手推料车 / tool cart / 平板拖车**——无单前轮 + 后腿 + 把手倾倒这套独轮车身份。

## 槽位 + 候选模块表

> **建模注记**：`tub_body`（Slot A）与 `frame_build`（Slot C）两轴的 part 都发射为**同一个 `barrow` part 的 visual**
> （单刚体，二者靠 `tray_mount_*` pad ↔ frame 横梁互触连成一岛），因此二者之间**无跨-part MatingContract**，只需
> part-内几何岛连通（`warn_if_part_contains_disconnected_geometry_islands`，compile-sweep 升为硬 FAIL）。`wheel_type`
> （Slot B）发射到独立 `wheel` part。真正的活动关节只有两根：body-tip REVOLUTE（barrow）+ wheel spin CONTINUOUS（wheel），
> 两轴对所有 seed 恒为 axis=(1,0,0)、origin=AXLE_PIVOT（uniform joint frame，见 §5）。

### Slot A：tub_body（③ 主体形态家族 —— 斗身可识别几何形态，发射到 `barrow` part）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| steel_pressed_pan（基线） | forked_anchor | rec_use-...-155130_516298_cabe5db4（A）| `_wheelbarrow_tray_geometry` L75-110 / tray_shell L176-180 / side_rib+seam L183-201 | Volumetric Envelope Form | eligible if compatible | 深压钢斗：4-loop superellipse loft 中空斜壁 + 折边 rim（`MeshGeometry`），外挂 `side_rib_{i}`/`front_seam`/`rear_seam` reinforcing 肋（④）|
| plastic_molded_tub | forked_anchor | rec_wheelbarrow_var_plastic_tub | `_poly_tub_geometry` L74-114 / tray_shell(poly) L180-184 / `molded_flute_{i}` L189-218 | Volumetric Envelope Form | eligible if compatible | 一体成型聚乙烯圆润厚壁斗（exp=2.8 更圆角、厚 rim），外挂 `molded_flute_{i}` 结构熔筋（straddle 壁面，intentional overlap，④）|
| flatbed_deck | forked_anchor | rec_wheelbarrow_var_flatbed | `_flat_deck_geometry` L98-130 / flat_deck L211-215 / `tread_strip_{i}` L217-230 | Planar Boundary Form | eligible if compatible | 平板砖斗：低平板 + 四周浅 kick-rail（`_add_box_to_mesh` mesh），面上 `tread_strip_{i}` 防滑条（④）；**无深墙、无板条** |
| wood_slat_box | forked_anchor | rec_use-...-155130_520600_52ff17ad（B）| `floor_plank_{i}` L98-118 / `side_{side}_slat_{row}` L131-158 / `{end}_slat_{row}` L161-174 / `upright_post_{idx}` L178-192 / floor_grain/top_lip | Macro Surface Construction | eligible if compatible | 板条木箱：floor_plank 底 + 侧 / 端 `*_slat_{row}` 板条墙（**N 复制，见 §8**）+ 6 根 upright_post + top_lip；宏观由离散板条构成箱体 |

### Slot B：wheel_type（wheel part 的 ③ 形态 —— **恒为独立 `wheel` part**）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 primitive / 结构特征 |
|---|---|---|---|---|---|
| pneumatic_steel_rim（基线） | forked_anchor | rec_...cabe5db4（A）| `TireGeometry` L314-328 / `WheelGeometry`(split_y 辐) L330-344 / `valve_stem` L347-352 | eligible if compatible | 充气橡胶胎（`TireGeometry` block tread + grooves + sidewall）+ 钢圈（`WheelGeometry` split_y 辐 + domed hub + bolt_pattern）+ `valve_stem` 旋转标记 |
| solid_disc | forked_anchor | rec_wheelbarrow_var_solid_wheel | `_solid_disc_wheel_geometry` **LatheGeometry** L125-144 / solid_disc L328-332 / closed_hub L335-340 / spin_marker L344-349 | eligible if compatible | 实心免充气聚氨酯盘（**`LatheGeometry` 旋转母线 + `rotate_y(π/2)` 对齐 X**，不得降 Box/Cylinder）+ closed_hub 圆柱 + 偏轴 `spin_marker` |
| wood_spoked_cart | forked_anchor | rec_...52ff17ad（B）| `TireGeometry` L321-333 / `WheelGeometry`(straight 辐, wood) L336-353 / `dark_hub_shell` L354-357 / `tread_marker` L361-366 | eligible if compatible | 木辐大车轮：`TireGeometry` + `WheelGeometry` straight 辐（`count=8`）wood 材质 + `dark_hub_shell` 黑轴套 + `tread_marker` 旋转标记 |

### Slot C：frame_build（① 骨架图 —— 把手 / 腿 / 轴座，发射到 `barrow` part）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 primitive / 骨架特征 |
|---|---|---|---|---|---|
| tube_rail（基线） | forked_anchor | rec_...cabe5db4（A）| `_barrow_tube_mesh`(spline tube) handle_rail L204-215 / front_guard L217-224 / cross_tube L226-232 / support_leg L234-249 / front_strut L307-309 / 三角板 axle_bracket L286-304 | eligible if compatible | 连续**弯钢管**骨架：`tube_from_spline_points` 弯管把手 + front_guard loop + 横管 + 弯管腿 + 弯管撑 + 三角板轴座 |
| welded_flatbar | forked_anchor | rec_wheelbarrow_var_flatbar_frame | 直 `Box` rail L180-186 / front_guard bar L190-195 / nose_bar L197-212 / flat cross L215-222 / **A-frame** leg L227-267 / flat axle_bracket L294-300 / handle_stub L328-345 | eligible if compatible | 焊接**直扁铁 / 角铁**骨架：矩形截面直梁 rail + 直 front_guard + A 字腿（front + rear leg 分叉 + gusset）+ 直轴板 + 螺栓 handle_stub |
| wood_runner | forked_anchor | rec_...52ff17ad（B）| `_body_beam_xz`(Box beam) `handle_{i}_runner` L196-217 / `leg_{i}_support_leg` L229-237 / `{i}_rear_brace` / fork_axle_plate L249-264 / axle_pin+stub L266-285 / front/side strut L288-290 | eligible if compatible | **木梁**骨架：粗方木 runner（承斗+把手一体）+ 木腿 / 脚 / 撑 + 黑钢 `fork_{i}_axle_plate` 叉板 + `axle_pin`/`axle_stub_{i}` |

## 槽位图（slot graph）

pattern: mixed（root pivot 挂两 parallel child；tub_body + frame_build inline 到 `barrow`；wheel_type 到 `wheel`；side_slat_count 在 `barrow` 上 N 次复制板条 visual）

```
wheel_axle_pivot (root, 无 visual 的纯运动学 pivot, 位于轴心 AXLE_PIVOT=(0,-0.60,0.25))
  │
  ├──[axle_pivot_to_barrow : REVOLUTE axis=(1,0,0), origin=AXLE_PIVOT, lower=0 upper≈1.05]──> barrow (body)
  │        └ visual 集合 = [frame_build slot 的 handles/legs/axle/brackets/cross-members]
  │                       + [tub_body slot 的 shell/deck/slat-box + tray_mount_* pad]
  │                       + [side_slat_count 多重性: side_{side}_slat_{row} i∈range(N) —— 仅 wood_slat_box]
  │        (tub 靠 tray_mount_* pad ↔ frame 横梁 z≈0.30 互触；frame 各件互触；全 barrow = 一个几何岛)
  │
  └──[axle_pivot_to_wheel : CONTINUOUS axis=(1,0,0), origin=AXLE_PIVOT]──> wheel
           └ visual 集合 = [wheel_type slot: tire + rim/disc + hub + spin marker], 轴对称母线沿 local X, 中心在 part 原点
```

接口点位与 joint 语义：
- **两非-fixed joint（恒存，uniform）**：`axle_pivot_to_barrow` REVOLUTE + `axle_pivot_to_wheel` CONTINUOUS，**对所有 seed** axis=(1,0,0)、origin=AXLE_PIVOT（无 rpy）。barrow 侧真实硬件 = `axle` 圆柱（中心恰在 AXLE_PIVOT，沿 X）；wheel 侧真实硬件 = hub/rim（中心在 wheel-local 原点，即 AXLE_PIVOT）→ origin 检查两侧都落在硬件上。
- **captured-pin（grandfather）**：`axle`（barrow）穿过 wheel 的 hub/rim/disc bore —— 几何非两轴对齐面对接 → **省略 MatingContract**（Rule 2 captured-pin 豁免），由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap(barrow.axle ↔ wheel.hub/disc)` 守相交（照搬各样本 run_tests 段）。
- **tub ↔ frame 接口（part 内）**：tub 发射 `tray_mount_{i}` pad（Box，顶嵌入 tub 底、底伸到 frame 横梁 z≈0.30），frame **必提供**至少一根近-满宽横梁（tube: `front_cross_tube`/`rear_cross_tube`；flatbar: `front_cross_bar`/`rear_cross_bar`；wood: 加 `front_cross_tie`/`rear_cross_tie`）在 y∈{-0.22,0.28}, z≈0.30；pad ↔ 横梁 overlap 使 tub 与 frame 连成一岛。**同 part 内，无 joint**。
- **body-tip 运动包络**：REVOLUTE axis=(1,0,0)（宽向 X）、开启方向 = 前倾倒卸（+θ 使把手升、斗口朝前下），[闭合 0, 可行上界 ≈1.05]。倾倒时斗身绕轴心转，`axle`/brackets 因在轴心 X 轴上（同轴）几乎不动；斗中心 x 带的壳可能在倾倒中途扫近前轮胎面（真实倾卸就是把料倒过前轮）→ 若 sampled collision 触发 tub↔tire 中途相交，声明 element-scoped `allow_overlap(tub_shell ↔ tire, reason="dump tips the tub forward over the front wheel; load pours past the wheel — coupled dump motion")`。
- **wheel-spin 运动包络**：CONTINUOUS 整圈；胎轴对称，旋转不改碰撞（`valve_stem`/`spin_marker`/`tread_marker` 微小）→ 无新碰撞。
- **rest pose**：body-tip q=0（停放），wheel q=0；barrow 停放于后腿脚落地。
- **互斥 / 派生**：tub_body 四选一互斥、wheel_type 三选一互斥、frame_build 三选一互斥；side_slat_count **仅在 tub_body=wood_slat_box 时**为真实复制轴，其余 tub 记 `n0`（见 §8 / §9）。

## 每槽位 Module Emits / Interfaces

### Slot A / tub_body — steel_pressed_pan（其余 tub 仅换壳 mesh + 装饰 + tray_mount）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`tray_shell`（`_wheelbarrow_tray_geometry` mesh）+ `side_rib_{i}`/`front_seam`/`rear_seam`（④）+ `tray_mount_{i}` pad，全为 `barrow` visual | A L176-201, L253-261 |
| internal joints | 无（tub 是 barrow 的 visual，无 joint）| — |
| upstream interface | `tray_mount_{i}` pad 底面落在 frame 横梁 z≈0.30（part 内互触）| A L253-261 |
| downstream interface | 斗口向上开放（承载语义）| — |

### Slot A / tub_body — plastic_molded_tub
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tray_shell`（`_poly_tub_geometry` 圆润厚壁 mesh）+ `molded_flute_{i}`（结构熔筋，straddle 壁面 intentional overlap，④）+ `tray_mount_{i}` | plastic L180-218 |
| internal joints | 无 | — |
| upstream interface | `tray_mount_{i}` ↔ frame 横梁 | plastic L273-281 |

### Slot A / tub_body — flatbed_deck
| emits | 描述 | 来源 |
|---|---|---|
| parts | `flat_deck`（`_flat_deck_geometry` 平板+kick-rail mesh）+ `tread_strip_{i}`（防滑条，④）+ `tray_mount_{i}` | flatbed L211-230, L289-301 |
| internal joints | 无（**无板条 → side_slat_count = n0**）| — |
| upstream interface | `tray_mount_{i}`（前高后矮，桥接平板到 frame）| flatbed L289-301 |

### Slot A / tub_body — wood_slat_box（含 side_slat_count 多重性）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `floor_plank_{i}`(+floor_grain ④) + `side_{side}_slat_{row}`(+grain ④) + `{end}_slat_{row}` + `{side/end}_top_lip` + `upright_post_{idx}` + `*_floor_tie` + `tray_mount_{i}`，全 `barrow` visual | B L98-192 |
| internal joints | 无 | — |
| upstream interface | `*_floor_tie` / `tray_mount_{i}` ↔ frame 横梁 | B L120-135 |
| multiplicity | `side_{side}_slat_{row}` / `{end}_slat_{row}` `for row in range(N)`；`upright_post` 高度 + `top_lip` z 随 N 派生（见 §8）| slats_n2 L37-201 / slats_n5 |

### Slot B / wheel_type（pneumatic / solid_disc / wood_spoked —— 恒为独立 `wheel` part）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel` part：tire mesh + rim/disc mesh + hub + 偏轴 spin marker（轴对称母线沿 local X，中心在 part 原点）| A L313-352 / solid L323-349 / B L311-366 |
| internal joints | 无（wheel 内部无活动件）| — |
| upstream interface | hub/rim/disc bore 被 barrow 的 `axle` 穿过（captured-pin）；part 原点 (0,0,0) 落在 AABB 内 → chain 关节 origin 有几何 | A L314-344 |
| consumer joint | `axle_pivot_to_wheel` CONTINUOUS axis=(1,0,0)（root pivot 发射）| A L364-372 |

### Slot C / frame_build（tube_rail / welded_flatbar / wood_runner —— 发射到 `barrow` part）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；handle_rail/runner + grip(+ring/band ④) + support_leg + foot_pad + front_strut + **cross-member**（横梁，供 tub 骑座）+ `axle` 圆柱 + axle_bracket/fork_plate(+bolt ④)，全 `barrow` visual | A L204-309 / flatbar L164-372 / B L196-290 |
| internal joints | 无（frame 是 barrow 的 visual）| — |
| upstream interface | cross-member(y∈{-0.22,0.28},z≈0.30) 供 tub `tray_mount` 骑座；`axle` 中心=AXLE_PIVOT 供 body-tip + wheel-spin joint | A L226-232, L280-285 |
| downstream interface | grips 在 +Y（人手）；后腿脚落地 | A L264-277, L234-249 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| tub_body | enum | steel_pressed_pan / plastic_molded_tub / flatbed_deck / wood_slat_box | steel_pressed_pan | choice | deterministic procedural sampler 选；决定 tub 壳 mesh + 装饰 + 承载 part | module table |
| wheel_type | enum | pneumatic_steel_rim / solid_disc / wood_spoked_cart | pneumatic_steel_rim | choice | sampler 选（互斥）| module table |
| frame_build | enum | tube_rail / welded_flatbar / wood_runner | tube_rail | choice | sampler 选（互斥）| module table |
| side_slat_count (N) | int | 声明产品域 [2,8]；sweep 采样域 {2,3,5}（偏小加权：2 高频、3 常见、5 长尾）| 3 | conditional→slot_choice | **仅 tub_body=wood_slat_box 生效**；编入 slot_choice 为 `n{N}`（拓扑维度），其余 tub 记 `n0`（见 §8）| slats_n2 / B / slats_n5 |
| palette_style | enum | galvanized_green / natural_wood_black / red_painted / blue_orange_contractor / green_poly / yellow_builder | galvanized_green | palette | palette only，**不计入 slot_choice**；驱动全部 `.visual(material=mats[...])` | 各样本材质 + ⑥ |
| tub_width_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 tub X（宽）主尺寸，clamp | resolve clamp |
| tub_length_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 tub Y（长）主尺寸，clamp | resolve clamp |
| tub_depth_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 tub Z 高度（斗深）+ tray_mount pad 高派生，clamp | resolve clamp |
| handle_reach_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放把手 +Y 伸展 + 握把 y，clamp | resolve clamp |
| wheel_size_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放轮 OD（tire/rim/disc 等比），clamp | resolve clamp |
| body_tip_upper | float | [1.00, 1.15] | 1.05 | independent | body-tip REVOLUTE upper（run_tests 要求 ≥1.0）| A L361 |
| (—) | constraint | — | — | equation | `tray_mount_pad_height = tub_underside_z(tub_body, tub_depth_scale) − CROSS_MEMBER_Z(≈0.30)`；pad 顶嵌 tub 底、底触横梁（保 tub↔frame 连通）| 接口 / 连通 |
| (—) | constraint | — | — | inequality | 轮不撞斗前壁：`tire_top_z(wheel_size_scale) ≤ tub_front_underside_z − clearance`；wheel_size 过大时回缩 wheel_size_scale | 接口 / clearance |
| (—) | constraint | — | — | conditional | N（side_slat_count）合法域随 tub_body：wood_slat_box→{2,3,5} 采样、[2,8] clamp；其余 tub→N 恒 0（`n0`），不发射板条 | §8 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 tub_body / wheel_type / frame_build / N 的离散拓扑**。

### 7.5 编译预算 / compile budget（必填）

**自报预算：≤ 18 s/seed**（依据：origin 记录级编译均落在库内典型模板 5-20s 区间；本类无重布尔雕刻，最贵的是 tub loft mesh + 3 段 tube spline mesh + Tire/Wheel geometry）。分档 tessellation：tub loft `segments≤64`；tube `radial_segments=16, samples_per_segment=12`；Tire/Wheel 用样本默认（已是中等）；LatheGeometry disc `segments=48`；N 个板条 = 复用同一 `Box` 语义、循环发射（非 N 份 mesh）。sweep `--compile-timeout 120`（≈6.7× 自报，watchdog）。超预算先降 loft/tube 段数再迭代。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（wood 斗侧 / 端板条数），**conditional 于 tub_body=wood_slat_box**：

- **count_param**：`side_slat_count`（模板变量 N；wood_slat_box 每面墙的板条行数）。
- **N_range**：声明产品域 **[2, 8]**（现实木斗侧墙 2-8 行板条已覆盖浅箱→深箱；source map 建议 {2,3,5} 有样本、模板域 [2,8]）。`config_from_seed` sweep 采样域 **{2,3,5}**（偏小加权：N=2 高频、N=3 常见、N=5 长尾），对齐三样本实测点。`resolve_config` 把任意外部 N clamp 到 [2,8]。
- **sampling domain**：`config_from_seed` 用 `rng.choices((2,3,5), weights=偏小)`；**非 wood 斗时 N 记为 0**（`n0`，不发射板条）。
- **copied object**：单块板条 `side_{side}_slat_{row}`（+ 端墙 `{end}_slat_{row}` + `{side}_grain_{row}` ④），共享 `Box` 几何 helper；N 行复用同一截面。upright_post 高度、top_lip z 随 N **派生**（`top_lip_z = floor_z + N·row_pitch + margin`；`post_height = N·row_pitch`）。
- **naming**：`side_{side}_slat_{row}` side∈{0,1}, row∈range(N)；`{end}_slat_{row}` end∈{front,rear}。`for row in range(N)`（slats_n2 L139 / B L131-138 / slats_n5 已用此结构，直接作 copy-logic 源）。
- **placement**：沿 Z **绝对式**等距堆叠（`z_row = FLOOR_Z + SLAT_PITCH·(row + 0.5)`，每 row 的 z 由 row 与 floor 解析、不累加漂移）→ N-不变前提。侧墙沿 Y 满长、端墙沿 X 满宽。
- **joint policy**：板条是**非移动件**（Rule 1）→ inline 为 `barrow` 的 visual，**不发射独立 joint**；活动关节只有 body-tip + wheel-spin。
- **source/gating**：copy-logic 源 = slats_n2（N=2）/ origin B（N=3）/ slats_n5（N=5）的 `for row in range(N)`。N 与 tub_body 的 conditional 见 §9。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | **有** | frame_build 三候选换把手/腿/轴座**骨架构成**：tube_rail（弯管，forked_anchor A）/ welded_flatbar（直扁铁+A腿，forked_anchor flatbar 变体）/ wood_runner（木梁+叉板，forked_anchor B）。part-joint 图恒定（root+barrow+wheel，两 joint），骨架 visual 构成变。 |
| └ multiplicity | 同构件 ×N | **有** | 见 §8：wood_slat_box 侧/端板条 `side_{side}_slat_{row}` N∈{2,3,5} 采样 / [2,8] 域；非 wood 斗记 n0。forked_anchor（slats_n2/B/slats_n5）。 |
| ② 关节类型 | 图不变，某边换 type/轴 | **有（恒并存两型）** | `axle_pivot_to_barrow` **REVOLUTE**（axis=(1,0,0), [0,1.05] 倾倒）+ `axle_pivot_to_wheel` **CONTINUOUS**（axis=(1,0,0) 整圈旋转）。两型对**每个 seed 都出现**（非跨-seed 切换，是同图并存两关节）。forked_anchor（8/8 样本）。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | **有（登记 slot A + 附 wheel 形态 slot B）** | **tub_body slot A（主 ③，登记进 slot_choices）**：steel_pressed_pan（Volumetric Envelope，forked A）/ plastic_molded_tub（Volumetric Envelope 圆润，forked plastic 变体）/ flatbed_deck（Planar Boundary，forked flatbed 变体）/ wood_slat_box（Macro Surface，forked B）—— 4 个可识别斗形原型。**wheel_type slot B（wheel part 的 ③）**：pneumatic / solid_disc（Lathe 实心盘）/ wood_spoked 三种轮形。全 source-backed，非缩放/换色。 |
| ④ 表面装饰 | 原型不变，叠表面细节 / 改装饰数 | **有** | steel: `side_rib`/`front_seam`/`rear_seam`（record_only, A）；poly: `molded_flute_{i}` 熔筋（record_only, plastic 变体）；flatbed: `tread_strip_{i}` 防滑条（record_only, flatbed 变体）；wood: `floor_grain`/`side_grain`/`bolt_*` 木纹螺栓（record_only, B）；wheel: `valve_stem`/`spin_marker`/`tread_marker`。装饰均由宿主壳面 / 板面**逐面派生嵌入**（随 ③⑤ 共形，Rule 4；如 flute straddle 壁、seam 贴 rim、mount pad 随 depth_scale）。 |
| ⑤ 尺寸/行程 | 离散不变，只连续改尺寸/行程 | **有** | tub_width/length/depth_scale[0.9,1.12/1.15]、handle_reach_scale[0.92,1.10]、wheel_size_scale[0.9,1.12]（§7）；**body-tip REVOLUTE 运动包络**：axis=(1,0,0)，开启=前倾倒卸，[闭合 0, 可行上界 body_tip_upper∈[1.0,1.15]]；`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`（两 joint 组合，tub↔tire dump 相交声明 coupled `allow_overlap`）+ targeted `ctx.pose({body_tip:0.65})`（斗前倾+把手升）与 `ctx.pose({wheel_spin:1.25})`（marker 绕轴移动）；wheel CONTINUOUS 轴对称整圈无穿模。 |
| ⑥ 涂装 | 几何不变，只改材质/色 | **有** | `palette_style` 6 档（galvanized_green / natural_wood_black / red_painted / blue_orange_contractor / green_poly / yellow_builder），驱动全部 `.visual(material=mats[...])`。材质大类覆盖 metal(镀锌/漆钢)+plastic(聚乙烯)+wood(木)+rubber(胎/握把)+painted，≥ ceil(0.5×6)=3。tub 材质大类还随 tub_body（钢/塑/木/漆）拉开。 |

**收尾自检**：`template batch` 0-9 seed 渲染须肉眼见：4 种斗形拉得开（深钢斗 / 圆润塑斗 / 平板 / 木箱）、3 种轮（充气 / 实心盘 / 木辐）、3 种骨架（弯管 / 扁铁 A 腿 / 木梁）、板条 N 变化、6 涂装出现、body-tip 倾倒 + wheel 旋转全程不穿模。

## 拓扑多样性审计

总组合数：tub_body(4) × wheel_type(3) × frame_build(3) × side_slat_count 有效档 = 非 wood 斗(3 tub)×3×3×{n0}=27 + wood 斗(1)×3×3×{n2,n3,n5}=27 = **54 distinct slot-choice tuple**。

理由：tub_body 4、wheel_type 3、frame_build 3、side_slat_count {n0,n2,n3,n5} 4 —— 每 slot key ≥2 distinct 稳过。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三 named slot（tub_body / wheel_type / frame_build）→ 若 tub=wood_slat_box 则 `rng.choices((2,3,5),weights=偏小)` 采 N，否则 N=0 → uniform 各连续 scale → `resolve_config` clamp + 派生 tray_mount pad 高（equation）+ 投影 wheel-clear inequality。compatibility matrix 见下表（本类组合几乎全合法，仅 N conditional 于 wood 斗）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-35 初轮（fast 0-15 + final 16-35）+ corner stage；成熟审计 0-999；viewer 目检 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近组合上限 **54**（**低于富类别建议 ≥300（report-only）**）。原因说明：单轮独轮车是结构高度收敛的小类——真实形态就是 斗形(4) × 轮形(3) × 骨架(3) × 木斗板条数(≈3 有效) 这 54 组拓扑等价类，无更多真实结构可加；进一步"细分"靠 §7 连续 scale（tub/handle/wheel 尺寸、tip 行程）+ palette(6) 实现而非新拓扑。54 distinct 远超 ≥10 机械可见项，符合本小类真实结构上限。

Controlled local parameterization：tub_width_scale / tub_length_scale / tub_depth_scale / handle_reach_scale / wheel_size_scale / body_tip_upper（§7），全 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot + N（conditional：N 仅 wood 斗）→ 采 independent 各 scale → 派生 tray_mount pad 高（equation，随 tub_depth）→ 用 wheel-clear inequality 回缩 wheel_size。跨部件依赖（pad 高 vs tub 底 & 横梁 z、tire top vs 斗前壁）显式落 §7 equation/inequality，在 `resolve_config` 内求解，不留到 builder。这些 scale 不破坏两 joint origin/axis、captured-pin 接口、N 复制或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot，再（wood 斗）`rng.choices` 加权 N∈{2,3,5}，再 uniform 各 scale | slot_choices_for_seed 含 `("side_slat_count", f"n{N}")` 且与 build 一致 |
| compatibility matrix | (1) **side_slat_count conditional**：仅 tub_body=wood_slat_box 发射板条并采 N∈{2,3,5}；其余 tub N=0（`n0`）。 (2) **tub × frame 正交**：4 tub × 3 frame 均可（A 约定统一坐标，tub 靠 tray_mount 骑 frame 横梁；frame 必供 y∈{-0.22,0.28},z≈0.30 横梁）。 (3) **tub × wheel 正交**：材质混搭（木斗+钢轮等）为 ⑥/③ 合法，不 gate。 (4) **wheel-clear**：wheel_size_scale 过大回缩以保胎顶不撞斗前壁下沿。 | 无 floating / island / tub-frame 断连 / tub-tire 静态穿模 / 两 joint origin 偏离 |
| controlled local variation | 6 个 clamped scale（tub_w/l/d、handle_reach、wheel_size、body_tip_upper），每 build 统一 | 比例变化不破坏 joint origin/axis、captured 接口、tub-frame 连通、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-35 初轮 + corner stage；0-999 成熟审计 | axis_realization（逐 slot 值计数）+ 逐机构 QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| tub_body | 4 | yes | yes | 主 ③；Volumetric×2 / Planar / Macro 四形态原型 |
| wheel_type | 3 | yes | yes | 充气 / 实心 Lathe 盘 / 木辐 |
| frame_build | 3 | yes | yes | 弯管 / 焊接扁铁 A 腿 / 木梁（① 骨架）|
| side_slat_count (N) | 4 有效档（n0/n2/n3/n5）| yes | yes | 多重性；conditional 于 wood 斗，编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名，含 `("side_slat_count", f"n{N}")`（wood 斗 n2/n3/n5，其余 n0）。
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）；N 采样域 ⊆ {2,3,5} 且仅 wood 斗生效。
- `resolve_config` 把 N clamp 到 [2,8]、各 scale clamp 到声明范围；tray_mount pad 高（equation 随 tub_depth）+ wheel-clear（inequality）在 resolve 内求解。
- compatibility matrix / gating：N conditional 于 wood_slat_box；非 wood 斗不发射板条。
- 连续 scale clamp 后不破坏两 joint origin=AXLE_PIVOT / axis=(1,0,0)、captured-pin 接口、tub-frame part-内连通、N 复制。
- 关键 joint：`axle_pivot_to_barrow` REVOLUTE axis≈(1,0,0)（abs(axis[0])>0.99）lower=0 upper≥1.0；`axle_pivot_to_wheel` CONTINUOUS axis≈(1,0,0)。
- captured-pin：element-scoped `allow_overlap(barrow.axle ↔ wheel.hub/rim/disc)`；dump 中途若 tub↔tire 相交，coupled `allow_overlap(tub_shell ↔ tire)`（照搬样本 + dump 语义）。
- 恰好 3 part（wheel_axle_pivot + barrow + wheel）、恰好一只 wheel、两 joint 均挂 wheel_axle_pivot。
- copied object 遵循 `*_slat_{row}` 命名 + 绝对式沿 Z 等距 placement + Rule 1（无独立 joint）。
- grandfather：两非-fixed joint 是 captured-pin，省略 MatingContract，由 origin 检查 + allow_overlap 守。
- Rule 5：`run_tests` 调 `fail_if_parts_overlap_in_sampled_poses` + targeted `ctx.pose(body_tip)` / `ctx.pose(wheel_spin)`。

## Reject cases

- 把 A 家族与 B 家族坐标混用（长轴一半 +Y 一半 +X）→ tub/frame/wheel 错位、断连；必须统一 A 约定重表达 wood 模块。
- 把 tub_body 或 frame_build 发射成独立 FIXED part → 违反 Rule 1（tub/frame 是 barrow 的非移动 visual，应 inline 到同一刚体）。
- 把板条当独立活动 part 加 joint → 违反 Rule 1；板条是 `barrow` visual，无 joint。
- 非 wood 斗仍发射板条 / 采 N>0 → 违反 §8/§9 conditional（板条只属 wood_slat_box）。
- tub 与 frame 之间无 `tray_mount` pad ↔ 横梁互触 → tub 成孤岛（`warn_if_part_contains_disconnected_geometry_islands` 在 compile-sweep 升 FAIL）。
- 两 joint origin 放在轴心以外或 axis 非 (1,0,0) → `fail_if_articulation_origin_far_from_geometry`(0.015) FAIL / body-tip 倾倒 & wheel spin 方向错。
- 给 captured-pin（axle↔hub）补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把 solid_disc 的 `LatheGeometry` 降成 `Box`/`Cylinder`，或把 Tire/Wheel geometry 降成裸圆柱 → 违反 Rule 3（禁降级 Lathe/mesh/Tire/Wheel）。
- body-tip rest pose 设成张开角而非 q=0 → current-pose / viewer 目检不符（8/8 样本 lower=0 停放）。
- wheel_size_scale 过大致胎顶撞斗前壁下沿 → §7 inequality FAIL；须回缩 wheel_size。
- 把连续尺寸 / palette / 装饰数当新 candidate 塞进 slot → 不是结构差异。

## 与相邻类别的边界

- 不该混入：**双轮 / 多轮手推车（two-wheel cart / trolley / hand-truck）**——本类恰好一只前轮 + 斗身绕该轮轴倾倒；两轮车无单轮倾倒 spine。
- 不该混入：**Tipping_Barrow / 大型翻斗设备**——本类是人力小型独轮车（把手 + 单轮 + 后腿），非机动翻斗。
- 不该混入：**tool cart / 平板拖车 / 料车**——无"单前轮 + 后腿 + 把手倾倒"独轮车身份。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) 统一 A 约定、把 wood 模块重表达进 +Y 长轴是否接受（vs 拆 slug）；(2) side_slat_count 采样域 {2,3,5}、产品域 [2,8]、非 wood 斗记 n0；(3) tub × frame × wheel 全正交（材质混搭不 gate）；(4) Topology target 54<300 的结构上限说明是否接受；(5) tub/frame 同属 `barrow` 单刚体、靠 tray_mount pad 连通是否符合审计期望）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 参考模板：`agent/templates/Accessories_Cushion.py`（mixed pattern：固定 named slots + `("count", f"n{N}")` 进 slot_choice + 兼容 gating + captured 接口 element-scoped `allow_overlap` + PALETTES 字典驱动全 visual material 的骨架，本类同构改编）；`agent/templates/wheelbarrow.py`（**不同的旧模板，仅参考单轮 + wheel-spin + 大轮 QC 思路，不改写/覆盖它**）。
- 坐标 helper：沿用 origin A 的 `_barrow_origin(x,y,z,rpy)`（xyz 减 AXLE_PIVOT）/ `_barrow_mesh(geom)`（translate 减 AXLE_PIVOT）/ `_barrow_tube_mesh`（每点减 AXLE_PIVOT）；wheel visual 在 wheel-local 原点（中心=AXLE_PIVOT，轴对称沿 X，无 joint rpy）。
- 共享 helper：`_wheelbarrow_tray_geometry` / `_poly_tub_geometry` / `_flat_deck_geometry`（tub 壳，按 tub_body 切换）；`_solid_disc_wheel_geometry`（**保 LatheGeometry**）；`_barrow_tube_mesh` / `_beam_xz`（frame 梁）；板条 `Box` 循环复用。
- captured 接口 allow_overlap：`run_single_wheelbarrow_tests` 里补 element-scoped `allow_overlap(barrow.axle ↔ wheel.<hub/rim/disc>)`（照搬 A L412-421 / B L429-435 / solid L409-428）；dump 中途 tub↔tire 若相交补 coupled `allow_overlap`。
- 派生顺序（Rule 4 装饰共形）：③ tub 壳 mesh → ⑤ scale → tray_mount pad 高（随 depth）→ ④ 装饰（rib/flute/tread/grain 由最终壳面派生嵌入）。
- N=非 wood 斗退化：不进 range 循环、slot_choice 记 `n0`；wood 斗走 `for row in range(N)`（slats_n2/B/slats_n5 结构）。
- frame 必供 cross-member：三 frame 都要在 y∈{-0.22,0.28},z≈0.30 发射近-满宽横梁供 tub tray_mount 骑座（wood_runner 需补 `front_cross_tie`/`rear_cross_tie`）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C（origin 基线）| steel_pressed_pan + pneumatic + tube_rail | rec_use-...-155130_516298_cabe5db4 | `_wheelbarrow_tray_geometry` L75-110 / Tire+Wheel L314-344 / tube frame L204-309 / 两 joint L354-372 / allow_overlap L412-421 | A 约定基线 + 深钢斗 + 充气轮 + 弯管骨架 + captured-pin 范式 |
| S2 | A/B/C（origin 基线）| wood_slat_box + wood_spoked + wood_runner | rec_use-...-155130_520600_52ff17ad | 板条 L98-192 / Tire+Wheel(wood 辐) L321-357 / 木梁+叉板 L196-290 / 两 joint L359-379 | 木斗（板条多重性）+ 木辐轮 + 木梁骨架（重表达进 A 约定）|
| S3 | A | plastic_molded_tub | rec_wheelbarrow_var_plastic_tub | `_poly_tub_geometry` L74-114 / molded_flute L189-218 | 圆润聚乙烯塑料斗（Volumetric Envelope）+ 熔筋装饰 |
| S4 | A | flatbed_deck | rec_wheelbarrow_var_flatbed | `_flat_deck_geometry` L98-130 / tread_strip L217-230 | 平板砖斗（Planar Boundary）+ 防滑条 |
| S5 | B | solid_disc | rec_wheelbarrow_var_solid_wheel | `_solid_disc_wheel_geometry` **LatheGeometry** L125-144 / closed_hub L335-340 / spin_marker L344-349 | 实心免充气盘轮（Lathe，不得降级）|
| S6 | C | welded_flatbar | rec_wheelbarrow_var_flatbar_frame | 直 Box rail L180-186 / A-frame leg L227-267 / handle_stub L328-345 / flat bracket L294-300 | 焊接直扁铁 + A 字腿骨架 |
| S7 | D（multiplicity）| side_slat_count N=2 | rec_wheelbarrow_var_slats_n2 | `SLAT_Z_POSITIONS` L37 / `for row in range(N)` `side_{side}_slat_{row}` L139-158 / post/lip 派生 L37-201 | 浅箱 N=2 copy-logic 源 |
| S8 | D（multiplicity）| side_slat_count N=5 | rec_wheelbarrow_var_slats_n5 | `side_{side}_slat_{row}` N=5 + post/lip z 缩放 | 深箱 N=5 copy-logic 源 |
