# pilers_wire_strippers — Modular Spec

> 来源小类：`pictureX/0611/Pilers_wire_strippers`。slug = `pilers_wire_strippers`。
> 上游 source map：`picture_expansion/template_source_maps/0611__Pilers_wire_strippers.md`。
> **同步状态**：本 spec 引用的 10 个 5★ 样本（1 origin_anchor `compact_wire_strippers_001` 母资产 + 9 单轴 fork 变体：3 gauge_count / 2 stripper_mechanism / 3 secondary_module / 2 return_lock）已同步进 `data/records/rec_0611_pilers_wire_strippers_*/revisions/rev_000001/model.py`，rating=5。行号按各样本本仓库 `revisions/rev_000001/model.py` 计。
> **建模基线（重要）**：origin 母资产共享 4-part / 3-joint 骨架：`pivot` (root) + `arm_0` + `arm_1` + `spring`；`pivot_to_arm_0` REVOLUTE (pivot→arm_0, axis (0,0,-1)) + `pivot_to_arm_1` REVOLUTE (pivot→arm_1, axis (0,0,+1)) + `arm_0_to_spring` REVOLUTE (arm_0→spring, axis +Z)。**双 REVOLUTE 由 shared `pivot` part 承担**——区别于 pilers_cutting_pliers 的 root→moving 单枢轴链。**关键几何身份 = 沿 jaw seam 的一列 calibrated stripping notches / gauge holes**（origin: 6 洞，行号 `L24-25` 的 `GAUGE_Y` / `GAUGE_R`；这是 wire strippers 与所有其他钳子的最重要视觉判据）。

## 元信息
| 项 | 值 |
|---|---|
| slug | `pilers_wire_strippers` |
| template path | `agent/templates/pilers_wire_strippers.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（双 arm 镜像绕 shared pivot part 交叉 + spring 端锚子件 + 沿 jaw 均布 gauge holes 阵列） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10（1 origin_anchor + 9 fork 变体）|
| read_count | 10 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

样本与采纳分工：
- **P0 origin_anchor**（`rec_picturex_0611__pilers_wire_strippers__001__png_e3e85c27d08747acb9386fa8293dcd70` ← `picture/0611/Pilers_wire_strippers/001.png`）：4-part 骨架基线——`pivot`（承 rivet_shaft + 两 rivet_head）为 root，`arm_0` / `arm_1` 各为 stamped 钢片半 (带 handle + jaw + 6 gauge holes 阵列 + 2 crimp nests + insulated grip + yellow insert)，`spring`（compression coil, `_spring_geometry` L156-180，9 圈螺旋）挂 `arm_0`。`pivot_to_arm_0` REVOLUTE axis (0,0,-1) range `[-2°, +18°]`; `pivot_to_arm_1` REVOLUTE axis (0,0,+1) range `[-2°, +18°]`; `arm_0_to_spring` REVOLUTE axis +Z range `[-7°, +7°]`。**Slot Base：baseline_pivot + wire_clip_coil + 6_gauge + no_secondary**。Gauge holes 中心线沿 jaw seam (x≈0)，Y ∈ [0.037, 0.086]，radius 递减 0.00245→0.00130（origin `L24-25`）。
- **V-G5 gauge_count_5**：`GAUGE_Y = (0.040, 0.051, 0.062, 0.073, 0.084)` `GAUGE_R = (0.00245, 0.00215, 0.00185, 0.00155, 0.00130)`（L24-25 5 洞 5 半径）；part / joint 计数不变。**Slot D 5-hole 来源**。
- **V-G7 gauge_count_7**：`GAUGE_Y` 7 元、`GAUGE_R` 7 元（L24-25）；part / joint 计数不变。**Slot D 7-hole 来源**。
- **V-G9 gauge_count_9**：`GAUGE_Y = (0.034, ..., 0.094)` 9 元、`GAUGE_R = (0.00260, ..., 0.00125)` 9 元（L24-25）；part / joint 计数不变。**Slot D 9-hole 来源**。
- **V-M1 stripper_mechanism_compound_automatic**（`rec_0611_pilers_wire_strippers_var_stripper_mechanism_compound_automatic`）：`_metal_arm` L48-108 中 jaw 段替换为带 offset toggle boss + 更厚 compound-linkage 断面；part / joint 计数不变。**Slot B compound_automatic 来源**。
- **V-M2 stripper_mechanism_self_adjusting_para**（`rec_0611_pilers_wire_strippers_var_stripper_mechanism_self_adjusting_para`）：`_metal_arm` L48-108 改为 parallel jaw carrier（jaw 与 handle 通过 offset 连接、jaw plate 沿轨道走）；part / joint 计数不变。**Slot B self_adjusting_parallel 来源**。
- **V-S1 secondary_module_terminal_crimper**：追加 die-cavity 阵列 (4 die sizes)，`DIE_Y=(0.038,0.053,0.068,0.083)` `DIE_R=(0.0038,0.0032,0.0026,0.0020)` (L24-26)；沿 jaw 内边挖 crimp nest；part / joint 计数不变。**Slot A terminal_crimper 来源**。
- **V-S2 secondary_module_bolt_shear**（`rec_0611_pilers_wire_strippers_var_secondary_module_bolt_shear`）：`_bolt_shear_notch` helper L183-215（两半刃对合形成 shear hole，两 shear 半径 0.0016/0.0020，Y=0.012/0.016）；part / joint 计数不变。**Slot A bolt_shear 来源**。
- **V-S3 secondary_module_cable_cutter**（`rec_0611_pilers_wire_strippers_var_secondary_module_cable_cutter`）：`_cutter_plate` 变体 (更宽、带 cable-cut V 槽) L134-155；part / joint 计数不变。**Slot A cable_cutter 来源**。
- **V-R1 return_lock_torsion_return**（`rec_0611_pilers_wire_strippers_var_return_lock_torsion_return`）：`_spring_geometry` L156-180 换成绕 pivot mandrel 的 helical torsion coil；`arm_0_to_spring` 保 REVOLUTE。**Slot C torsion_return 来源**。
- **V-R2 return_lock_handle_lock**（`rec_0611_pilers_wire_strippers_var_return_lock_handle_lock`）：追加 `handle_lock` 单 part（lever 几何 `_handle_lock_lever` L183-213）挂 arm_0，新增 `arm_0_to_handle_lock` REVOLUTE axis +Z；保 spring + coil。**Slot C handle_lock 来源**（追加 1 part + 1 joint）。

冗余说明：10 个样本核心骨架（`pivot` root + 两 arm 镜像 + spring）同构；gauge_count / secondary_module 是 part-internal 几何切换（改 cut 循环 + 追加 cutter/crimp/notch 层），stripper_mechanism 是 jaw polyline 家族切换（`_metal_arm` polyline 换），return_lock=handle_lock 是唯一改链拓扑（+1 part +1 joint）的 fork。

## 核心身份

一把手动 wire strippers（剥线钳）：**两片镜像 stamped 钢半钳，绕 shared central `pivot` part 交叉**，jaw 段 = **成对的 stamped 钢颚 + 沿 jaw seam 一列 6-9 个 calibrated stripping notches / gauge holes**（这是 wire strippers 的**核心视觉判据**——每洞对应一个 AWG / mm² 规格，两半 jaw 各含相同布局的孔洞，合刃时两半孔对合形成完整剥皮孔），近 pivot 处有 **2 个较大的 insulated-terminal crimp nests**。**主用户机构 = 两 arm 各自绕 shared pivot 的相对开合**（**双 REVOLUTE**：pivot→arm_0 轴 (0,0,-1) + pivot→arm_1 轴 (0,0,+1)）；合柄 = 合刃剥皮 + 挤压 crimp。**第二活动子件 = spring**（挂 arm_0 手柄销上，绕 +Z 摆的 compression coil / torsion coil，视觉上是复位弹簧）。

物体平躺 XY 平面（Z = 厚度/枢轴方向）：jaw 指 +Y，handle 向 -Y 张开；rivet / shared pivot 在世界原点 (0,0,0)。`arm_0` 承 -x handle + +x jaw；`arm_1` 承 +x handle + -x jaw（镜像）。cutter_plate 薄片贴 arm_1 前颚面（`bright_tool_steel`）。**return_lock=handle_lock 特例**：追加 `handle_lock` 中间 part（lever 几何）+ `arm_0_to_handle_lock` REVOLUTE axis +Z；把 5-part 链拓扑变成 5-part（4 + lock）。

默认成熟域：真实手工具尺度（整长 ~0.24-0.26 m，宽 ~0.07-0.09 m，jaw 长 ~0.09-0.10 m）。secondary_module 可为 none (baseline cutter_plate) / terminal_crimper / bolt_shear / cable_cutter；stripper_mechanism 可为 standard_plier / compound_automatic (jaw polyline 换) / self_adjusting_parallel (jaw polyline 换)；gauge_count 可为 5 / 6 / 7 / 9（Y 均布 + radius 递减 taper）；return_lock 可为 spring_coil / torsion_return / handle_lock。

不该混入：**其他钳（Other_pliers 大类下的综合 / cutting / needle_nose / linesman / slip_joint / tongue_groove / fencing）**——本类专职剥线（沿 jaw seam 阵列的 calibrated gauge holes 是唯一形态判据）；**剪刀 / scissors**；**扳手 / spanner**；**镊子 / tweezers**。

## 槽位 + 候选模块表

> **建模注记**：pilers_wire_strippers 的骨架由 **Slot C (return_lock)** 决定链拓扑（spring_coil / torsion_return = 4-part 链 pivot+arm_0+arm_1+spring；handle_lock = 5-part 链 追加 handle_lock）。**Slot A / B / D** 是 part-internal 几何层（arm 内 polyline / cut 循环 / 追加 visual）。
> 下面 4 个离散 slot + 1 个 palette 轴。

### Slot A：secondary_module（辅助功能模块；③ 主体形态家族 / Primary Form Family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype | 结构特征 |
|---|---|---|---|---|---|---|
| baseline_cutter_plate（基线）| origin_anchor | P0 | `_cutter_plate` L134-153（arm_1 前颚 bright_tool_steel 薄片）| eligible if compatible | Planar Boundary Form | 基线：仅 arm_1 承 bright_tool_steel cutter_plate 薄片（含 2 crimp nests 剪切孔），无第二功能层 |
| terminal_crimper | forked_anchor | V-S1 `rec_0611_pilers_wire_strippers_var_secondary_module_terminal_crimper` | `DIE_Y=(0.038,0.053,0.068,0.083)` L24, `DIE_R=(0.0038,0.0032,0.0026,0.0020)` L25 | eligible if compatible | Planar Boundary Form | 4 die-cavity 阵列（远 jaw 段挖 4 个 crimp die 孔，radius 递减）；追加 die-cavity cut 循环 |
| bolt_shear | forked_anchor | V-S2 `rec_0611_pilers_wire_strippers_var_secondary_module_bolt_shear` | `_bolt_shear_notch` L183-215 (2 shear holes: r=0.0016/0.0020 Y=0.012/0.016) | eligible if compatible | Planar Boundary Form | jaw 内边追加 2 shear notches (半径 0.0016/0.0020)，两半对合形成 shear 圆孔 |
| cable_cutter | forked_anchor | V-S3 `rec_0611_pilers_wire_strippers_var_secondary_module_cable_cutter` | `_cutter_plate` 变体 L134-155（宽 V 槽刃口）| eligible if compatible | Planar Boundary Form | cutter_plate 加宽并挖 cable-cut V 槽（cutter_plate x-width > 0.020） |

> 4 candidate（达 3-6 目标）。每个只改 arm 内 cut 循环 / 追加薄片 visual，保 part tree / interface / primitive 家族一致。

### Slot B：stripper_mechanism（jaw 与机构形态；② 关节 / 骨架轴 —— 保拓扑但改 jaw polyline 家族）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| standard_plier（基线）| origin_anchor | P0 | `_metal_arm` L48-97（handle + jaw + boss + gauge cut）| eligible if compatible | 基线 stamped 钢片双 arm，jaw polyline 从 pivot 直线向 +Y taper；`pivot_to_arm_{0,1}` REVOLUTE range `[-2°, +18°]` |
| compound_automatic | forked_anchor | V-M1 `rec_0611_pilers_wire_strippers_var_stripper_mechanism_compound_automatic` | `_metal_arm` L48-108 变体（jaw 段 offset toggle boss + 更厚断面）| eligible if compatible | jaw 段加宽（half-width +0.003 m）并附加一个 offset boss（+x 侧凸起 0.004 m）表达 compound-linkage jaw；`pivot_to_arm_{0,1}` 保 REVOLUTE，range 不变 |
| self_adjusting_parallel | forked_anchor | V-M2 `rec_0611_pilers_wire_strippers_var_stripper_mechanism_self_adjusting_para` | `_metal_arm` L48-108 变体（parallel jaw carrier 更宽平面）| eligible if compatible | jaw 段前端切平（tip 拉平至矩形）并加宽 (+0.004 m)，表达 parallel jaw 端面；`pivot_to_arm_{0,1}` 保 REVOLUTE，range 不变 |

> 3 candidate（达目标下限）。三者均改 `_metal_arm` 的 jaw polyline 家族形态（可识别），保 part / joint 计数与轴族一致。

### Slot C：return_lock（复位/锁定；② 关节附属子件 —— handle_lock 追加 part+joint）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| spring_coil（基线）| origin_anchor | P0 | `_spring_geometry` L156-180（9 圈 compression coil）| eligible if compatible | 4-part 链 baseline：`spring` part 单 REVOLUTE `arm_0_to_spring` axis +Z range `[-7°, +7°]`；coil 沿 -y 方向绕 x 轴的螺旋 tube |
| torsion_return | forked_anchor | V-R1 `rec_0611_pilers_wire_strippers_var_return_lock_torsion_return` | `_spring_geometry` L156-180（绕 pivot mandrel 的 helical torsion coil）| eligible if compatible | 4-part 链：`spring` part 单 REVOLUTE 保留；coil 换成 helical torsion（绕 x 轴 3-4 圈，紧螺距）表达 torsion return |
| handle_lock | forked_anchor | V-R2 `rec_0611_pilers_wire_strippers_var_return_lock_handle_lock` | `_handle_lock_lever` L183-213, handle_lock part L424-436, arm_0_to_handle_lock REVOLUTE L438-455 | eligible if compatible | 5-part 链：保留 spring + coil + `arm_0_to_spring`；追加 `handle_lock` part（lever polyline + boss）+ `arm_0_to_handle_lock` REVOLUTE axis +Z range `[-0.35, 0.60]` |

> 3 candidate（达目标下限）。spring_coil / torsion_return 保 4-part 链、改 coil 几何；handle_lock 追加 part + joint。

### Slot D：gauge_count（gauge hole 数量；④ 表面装饰 + ⑤ 尺寸阵列共轴）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| 6_gauge（基线）| origin_anchor | P0 | `GAUGE_Y = (0.037, 0.047, 0.057, 0.067, 0.077, 0.086)` L24, `GAUGE_R = (0.00245, 0.00220, 0.00195, 0.00172, 0.00150, 0.00130)` L25 | eligible if compatible | 6 gauge holes 沿 jaw seam 均布，radius 从 0.00245 taper 到 0.00130 |
| 5_gauge | forked_anchor | V-G5 `rec_0611_pilers_wire_strippers_var_gauge_count_5` | `GAUGE_Y = (0.040, 0.051, 0.062, 0.073, 0.084)` L24, `GAUGE_R = (0.00245, 0.00215, 0.00185, 0.00155, 0.00130)` L25 | eligible if compatible | 5 洞、间距更宽 |
| 7_gauge | forked_anchor | V-G7 `rec_0611_pilers_wire_strippers_var_gauge_count_7` | L24-25 7 元 tuple | eligible if compatible | 7 洞、间距更密 |
| 9_gauge | forked_anchor | V-G9 `rec_0611_pilers_wire_strippers_var_gauge_count_9` | `GAUGE_Y = (0.034, 0.041, 0.049, 0.056, 0.064, 0.071, 0.079, 0.086, 0.094)` L24, `GAUGE_R = (0.00260, 0.00238, 0.00218, 0.00198, 0.00180, 0.00164, 0.00150, 0.00137, 0.00125)` L25 | eligible if compatible | 9 洞、jaw 更长以容纳 |

> 4 candidate（达 3-6 目标）。四者只改 `GAUGE_Y` / `GAUGE_R` tuple 长度与元素（procedural 均布 taper），part / joint 计数不变，杂而不改拓扑。

## palette

`palette_style` (6): `black_yellow_pro`（origin 基线）/ `red_black`（industrial red overmold）/ `blue_yellow`（Klein 风格 blue）/ `all_black`（工程款）/ `orange_black`（Fluke 风格 orange）/ `chrome_natural`（chrome plated frame + gray grip）。每档 5 mat：`metal_frame`（stamped 钢，深灰-深黑）+ `pivot_metal`（亮银 pivot）+ `bright_metal`（前刃亮银）+ `grip_shell`（黑/红/蓝/橙外层）+ `grip_insert`（黄/黑/黄 insert）。metal 大类覆盖 4 档 + rubber/polymer 大类覆盖 6 档。

## 槽位图（slot graph）

```
pattern: mixed（4-part chain: pivot root + arm_0 + arm_1 (镜像) + spring；return_lock=handle_lock 追加 handle_lock part +1 REVOLUTE 变成 5-part）

  ── Slot C = spring_coil / torsion_return（4-part 链，基线）──
    pivot (root)  ──[REVOLUTE pivot_to_arm_0, axis (0,0,-1), origin (0,0,0)]──>  arm_0
      承载: rivet_shaft + 两 rivet_head + rivet_button                              承载: metal_frame[B,D]·grip_shell[palette]·grip_insert[palette]·spring_seat·gauge_mark×N
                  │                                                                   │
                  └[REVOLUTE pivot_to_arm_1, axis (0,0,+1), origin (0,0,0)]──> arm_1
                                                                                  承载: metal_frame[B,D 镜像]·grip_shell[palette]·grip_insert[palette]·cutter_plate[A]·spring_seat
                                                                                      │
                                                                       [REVOLUTE arm_0_to_spring, axis +Z, origin (-0.018,-0.028,0.0084)]
                                                                                      ↓
                                                                                  spring (coil[C])

  ── Slot C = handle_lock（5-part 链）──
    上同，追加：
    arm_0 ──[REVOLUTE arm_0_to_handle_lock, axis +Z, origin (-0.020,-0.055,0.008)]──> handle_lock (lock_lever)
```

接口点位：
- **pivot → arm_0（pivot_to_arm_0）**：mating = 中央 rivet shaft (Cylinder r=0.0040, l=0.0090) 落 (0,0,0)，joint REVOLUTE axis (0,0,-1) range `[-2°, +18°] × open_angle_scale`；MatingContract 省略；broad `allow_overlap(pivot, arm_0, reason="rivet shaft captured through hub bore")`
- **pivot → arm_1（pivot_to_arm_1）**：mating 同上，axis (0,0,+1) range 同上；broad `allow_overlap(pivot, arm_1, reason=...)`
- **arm_0 → spring（arm_0_to_spring）**：mating = arm_0 的 spring_seat (Cylinder r=0.0022) origin (-0.018,-0.028,0.0084) axis +Z range `[-7°,+7°]`；elem-scoped `allow_overlap(spring, arm_0, elem_a="coil", elem_b="spring_seat", reason="spring tang captured in seat")` + `allow_overlap(spring, arm_1, elem_a="coil", elem_b="spring_seat", reason=...)`（对合 seat 上）
- **arm_0 → handle_lock（return_lock=handle_lock 分支）**：mating = arm_0 handle 面 lock_pin，REVOLUTE axis +Z range `[-0.35, +0.60]`；broad `allow_overlap(arm_0, handle_lock, reason="lock lever pin captured")`
- **互斥/可选/派生**：Slot C 决定 4- vs 5-part 链；A/B/D 与 C 正交；jaw / handle 在两 arm 上镜像派生（side=±1）；gauge holes 阵列在两 arm 相同 Y/R 参数生成。

## 每槽位 Module Emits / Interfaces

### Slot A / baseline_cutter_plate
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `cutter_plate`（arm_1 上 bright_tool_steel 薄片，_cutter_plate polyline extrude 0.0008 m）| P0 / L134-153 |
| downstream interface | 无独立 interface；`expect_contact(pivot, arm_1, ...)` 保 rivet 与 arm_1 接触 | P0 / L484-501 |

### Slot A / terminal_crimper
| emits | `cutter_plate` (baseline) + 4 die-cavity cut on arm_0/arm_1 jaw | V-S1 / L24-26 |
| downstream | jaw 断言 die_hole 数 = 4 | V-S1 |

### Slot A / bolt_shear
| emits | `cutter_plate` + `bolt_shear_notch` inline visual (2 semicircle plates with cut holes at Y=0.012/0.016) | V-S2 / L183-215 |
| downstream | jaw 内边可视 shear holes | V-S2 |

### Slot A / cable_cutter
| emits | 加宽 cutter_plate（x-width > 0.020）带 V 槽 cable cut | V-S3 / L134-155 |
| downstream | cutter_plate x-width 断言 > 0.018 | V-S3 |

### Slot B / standard_plier
| emits | 基线 `_metal_arm` jaw polyline | P0 / L48-97 |
### Slot B / compound_automatic
| emits | jaw polyline 变体（half-width +0.003, 追加 offset boss） | V-M1 / L48-108 |
### Slot B / self_adjusting_parallel
| emits | jaw polyline 变体（tip 拉平、加宽 +0.004） | V-M2 / L48-108 |

### Slot C / spring_coil
| emits | `spring` part 承 `_spring_geometry` (9 圈 compression coil sink) | P0 / L156-180 |
### Slot C / torsion_return
| emits | `spring` part 承 helical torsion tube (3-4 圈紧螺距) | V-R1 / L156-180 |
### Slot C / handle_lock
| emits | 保 `spring` part + coil；追加 `handle_lock` part (`_handle_lock_lever` polyline + boss) + `arm_0_to_handle_lock` REVOLUTE | V-R2 / L183-213, L424-455 |

### Slot D / 5_gauge / 6_gauge / 7_gauge / 9_gauge
| emits | 沿 jaw seam 均布 N 个 gauge hole cut（`GAUGE_Y`/`GAUGE_R` tuple 长度 = N，radius 从 0.00245 taper 到 0.00130）；每洞对应 1 `gauge_mark_i` Box visual（外贴 marker）| P0 / V-G5 / V-G7 / V-G9 / L24-25, L282-288 |
| downstream | arm.meta['gauge_hole_count'] == N；沿 y 严格单调 | P0 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| secondary_module | enum | {baseline_cutter_plate, terminal_crimper, bolt_shear, cable_cutter} | baseline_cutter_plate | choice | sampler 选择 | Slot A |
| stripper_mechanism | enum | {standard_plier, compound_automatic, self_adjusting_parallel} | standard_plier | choice | sampler 选择；不改拓扑 | Slot B |
| return_lock | enum | {spring_coil, torsion_return, handle_lock} | spring_coil | choice | sampler 选择；handle_lock 追加 part + joint | Slot C |
| gauge_count | enum | {5, 6, 7, 9} | 6 | choice | sampler 选择；每档产生对应长度的 GAUGE_Y/GAUGE_R | Slot D |
| palette_style | enum | {black_yellow_pro, red_black, blue_yellow, all_black, orange_black, chrome_natural} | black_yellow_pro | palette | seed 采样；不进 slot_choice | P0 + 世界知识 |
| overall_len_scale | float | [0.90, 1.15] | 1.0 | independent | 整体等比缩放 | P0 |
| jaw_len_scale | float | [0.90, 1.10] | 1.0 | independent | jaw polyline y-scale；gauge Y 同步缩放 | P0 |
| grip_girth_scale | float | [0.90, 1.10] | 1.0 | independent | grip half-width；两 arm rest 不互穿 | P0 |
| open_angle_scale | float | [0.80, 1.20] | 1.0 | independent | pivot_to_arm_{0,1} upper (18°) 与 lower (-2°) scale | P0 |
| (—) | constraint | — | — | inequality | rivet origin (0,0,0)±0.002；两 arm z-lap 接触 | 接口 |
| (—) | constraint | — | — | inequality | gauge_Y max × jaw_len_scale ≤ 0.10；相邻 gauge_Y 严格递增 gap ≥ 0.006 m | 阵列 |

### 7.5 编译预算

自报本类别每-seed 编译预算 **~15-25 s**（4 part、多 gauge cut + polyline extrude 是主 CQ 成本；无重布尔雕刻；参考 P0 类比）。所有 `mesh_from_cadquery(..., tolerance=0.0003)`；spring tube 用 `tube_from_spline_points(samples_per_segment=2, radial_segments=10)`（P0 参数）。gauge_count=9 是 90 分位；预算不足时降 samples_per_segment。

## Multiplicity / Copy Logic

- gauge holes 数 N = gauge_count (∈ {5,6,7,9})；每 arm 各含 N holes，两 arm 对合形成 N 个 stripping stations
- Y 均布：`Y_i = Y0 + i × (Yn - Y0) / (N-1)`；R taper：`R_i = R_max - i × (R_max - R_min) / (N-1)`；`Y0 = 0.037`, `Yn = 0.086`, `R_max = 0.00245`, `R_min = 0.00130`（gauge_count=9 时 Y0=0.034 Yn=0.094）
- copied object / naming: `gauge_mark_{i}` box + inline cut；同 arm 上循环生成；joint policy 与 part policy 不变

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type |
|---|---|---|---|
| ① 骨架图 | 加/减 part/边 | 有 | Slot C return_lock：spring_coil/torsion_return (4-part) vs handle_lock (5-part +1 REVOLUTE)；forked_anchor V-R2 |
| └ multiplicity | 同构件 ×N | 有 | Slot D gauge_count = 5/6/7/9 (每 arm 各 N holes)；forked_anchor V-G5/V-G7/V-G9 |
| ② 关节类型 | 图不变换 type/轴 | 有 | 全 REVOLUTE 绕 +Z 或 -Z 但 pivot_to_arm_0 轴向 (0,0,-1) 与 pivot_to_arm_1 (0,0,+1) 对称构成对称对；handle_lock 追加 REVOLUTE；source: P0 |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | Slot A secondary_module (baseline/crimper/shear/cutter，4 candidate) + Slot B stripper_mechanism jaw polyline family (standard/compound_automatic/self_adjusting_parallel，3 candidate)；forked_anchor |
| ④ 表面装饰 | 装饰细节 | 有 | gauge_mark 外贴 marker Box + grip_insert 分层；host-conformal，非独立 module |
| ⑤ 尺寸/行程 | 连续尺度 | 有 | overall/jaw/grip/open_angle scale，全 clamp；joint range pivot_to_arm ∈ [-2°,18°] × scale；spring [-7°,7°] 固定；无 continuous 关节 |
| ⑥ 涂装 | 材质/颜色 | 有 | palette_style 6 档 (black_yellow_pro/red_black/blue_yellow/all_black/orange_black/chrome_natural)；material 大类覆盖 metal (4 档：pivot_metal + bright_metal + metal_frame 亮/暗) + polymer (grip 黑/红/蓝/橙) |

## 采样与覆盖审计

总组合：secondary_module(4) × stripper_mechanism(3) × return_lock(3) × gauge_count(4) = **144** distinct 拓扑等价类。

seed_domain_policy：procedural_first。`config_from_seed(seed)` deterministic：加权选 slot（baseline 偏多）+ 连续 scale + palette。`seed=0` 不特殊。

| slot | count | ≥2 | ≥3 | 备注 |
|---|--:|---|---|---|
| A secondary_module | 4 | yes | yes | baseline/crimper/shear/cutter |
| B stripper_mechanism | 3 | yes | yes | standard/compound_auto/parallel |
| C return_lock | 3 | yes | yes | spring_coil/torsion/handle_lock |
| D gauge_count | 4 | yes | yes | 5/6/7/9 |

## Validator

- slot_choices_for_seed returns implemented module names (secondary_module / stripper_mechanism / return_lock / gauge_count)
- config_from_seed procedural for all seeds；seed=0 不特殊
- pivot origin 恒 (0,0,0)±0.002；两 arm z-lap 接触；rivet captured 由 broad allow_overlap 覆盖
- gauge_Y 严格 y 递增；gauge_count=N 时数量断言
- spring captured：elem-scoped allow_overlap(spring, arm_0/1, elem_a=coil, elem_b=spring_seat)
- handle_lock 分支：追加 handle_lock part + arm_0_to_handle_lock REVOLUTE；broad allow_overlap
- 开合：pose pivot_to_arm_{0,1} 到 upper 使 arm_0 grip_shell x-min 减小、arm_1 grip_shell x-max 增大 (≥0.008)
- palette_style 只换 material rgba
- 所有 `.visual(material=mats[...])` 用 mats dict 索引

## Reject cases

- 缺 gauge holes 阵列（wire strippers 判据缺失）
- pivot 不作独立 part 或不作 root
- 单 REVOLUTE 代替双 REVOLUTE (pivot_to_arm_0 + pivot_to_arm_1)
- gauge_count=N 但实际不到 N 洞或 Y 非单调
- return_lock=handle_lock 但缺 handle_lock part 或 arm_0_to_handle_lock REVOLUTE
- secondary_module=cable_cutter 但 cutter_plate x-width ≤ 0.018
- palette_style 塞进 slot_choice

## 与相邻类别的边界

- 不该混入：pilers_cutting_pliers、pilers_needle_nose_pliers、pilers_linesman_pliers、pilers_slip_joint_pliers、pilers_tongue_groove_pliers、pilers_locking_pliers、pilers_fencing_pliers（各自独立小类，wire_strippers 判据 = gauge holes 阵列）
- 不该混入：scissors / wrench / tweezers / stapler

## 模板实现备注

- 共享 helper：`_poly_solid(points, thickness, z_center)`, `_circle_solid(r, thickness, z_center, x, y)`, `_metal_arm(side, z_center, r)`, `_grip_shapes(side, z_center, r)`, `_cutter_plate_baseline(side, z_center)`, `_spring_coil()`, `_torsion_coil()`, `_handle_lock_lever()`
- 关键 allow_overlap：broad `allow_overlap(pivot, arm_0/1, reason=...)` (rivet captured)；elem-scoped `allow_overlap(spring, arm_0/1, elem_a=coil, elem_b=spring_seat, reason=...)`；handle_lock 分支 broad `allow_overlap(arm_0, handle_lock, reason=...)`
- 主 REVOLUTE 均省略 MatingContract（captured-pin grandfathered）
- gauge_count → GAUGE_Y/GAUGE_R 由 `_gauge_layout(N)` 派生（Y 均布 + R taper）
- 开合测试：pose pivot_to_arm_{0,1} 到 upper 使 arm_0/arm_1 grip_shell x 分离；spring x 摆动

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| P0 | A/B/C/D | baseline_cutter_plate/standard_plier/spring_coil/6_gauge | rec_picturex_0611__pilers_wire_strippers__001__png_e3e85c27d08747acb9386fa8293dcd70 | _metal_arm L48-97, _grip_shapes L100-131, _cutter_plate L134-153, _spring_geometry L156-180, pivot_to_arm_0 L312-326, pivot_to_arm_1 L327-341, arm_0_to_spring L356-370, GAUGE_Y/R L24-25 | 4-part 骨架基线 |
| V-S1 | A | terminal_crimper | rec_0611_pilers_wire_strippers_var_secondary_module_terminal_crimper | DIE_Y/DIE_R L24-26 | 4 die-cavity 阵列 |
| V-S2 | A | bolt_shear | rec_0611_pilers_wire_strippers_var_secondary_module_bolt_shear | _bolt_shear_notch L183-215 | jaw 内 2 shear notches |
| V-S3 | A | cable_cutter | rec_0611_pilers_wire_strippers_var_secondary_module_cable_cutter | _cutter_plate L134-155 (加宽) | 宽 cutter with V 槽 |
| V-M1 | B | compound_automatic | rec_0611_pilers_wire_strippers_var_stripper_mechanism_compound_automatic | _metal_arm L48-108 (compound jaw) | 复合 jaw polyline 家族 |
| V-M2 | B | self_adjusting_parallel | rec_0611_pilers_wire_strippers_var_stripper_mechanism_self_adjusting_para | _metal_arm L48-108 (parallel jaw) | parallel jaw polyline 家族 |
| V-R1 | C | torsion_return | rec_0611_pilers_wire_strippers_var_return_lock_torsion_return | _spring_geometry L156-180 (torsion) | 绕 mandrel torsion coil |
| V-R2 | C | handle_lock | rec_0611_pilers_wire_strippers_var_return_lock_handle_lock | _handle_lock_lever L183-213, handle_lock part L424-436, arm_0_to_handle_lock L438-455 | 追加 lock lever part+joint |
| V-G5 | D | 5_gauge | rec_0611_pilers_wire_strippers_var_gauge_count_5 | GAUGE_Y/R L24-25 (5 元) | 5 洞 |
| V-G7 | D | 7_gauge | rec_0611_pilers_wire_strippers_var_gauge_count_7 | GAUGE_Y/R L24-25 (7 元) | 7 洞 |
| V-G9 | D | 9_gauge | rec_0611_pilers_wire_strippers_var_gauge_count_9 | GAUGE_Y/R L24-25 (9 元) | 9 洞 |
