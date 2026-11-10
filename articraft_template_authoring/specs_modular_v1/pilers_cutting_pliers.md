# pilers_cutting_pliers — Modular Spec

> 来源小类：`pictureX/0611/Pilers_cutting_pliers`（articraft_data 上游小类样本池；对象身份为一把对角/切断钳——两片锻钢半钳绕中央 rivet 交叉，头部为切断颚，柄部张合驱动切断动作）。slug 取本仓库规范 `pilers_cutting_pliers`。
> 上游 source map：`picture_expansion/template_source_maps/0611__Pilers_cutting_pliers.md`。
> **同步状态**：本 spec 引用的 10 个 5★ 样本（1 origin_anchor `diagonal_cutting_pliers_001` 母资产 + 9 单轴 fork 变体：3 cutting_head / 2 leverage / 2 return / 3 handle）已同步进本仓库 `data/records/rec_0611_pilers_cutting_pliers_*/revisions/rev_000001/model.py`，rating=5。行号按各样本本仓库 `revisions/rev_000001/model.py` 计。
> **建模基线（重要）**：origin 母资产共享 3-part / 2-joint 骨架：`root_half` (root) + `moving_half` + `spring_clip`；`plier_pivot` REVOLUTE (root→moving, axis +Z) + `clip_swing` REVOLUTE (moving→spring_clip, axis +Z)。仅 `leverage=compound_link` 轴改链拓扑（追加 `compound_link` part + `compound_to_moving` REVOLUTE mimic → 4-part / 3-joint 链）；其余 8 个 fork 均保 3-part / 2-joint。

## 元信息
| 项 | 值 |
|---|---|
| slug | `pilers_cutting_pliers` |
| template path | `agent/templates/pilers_cutting_pliers.py` |
| test path (optional) | 无（sweep-pipeline 为唯一验收） |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（两半镜像 pivot 链 + 可选 compound_link 追加 part / joint + spring_clip 端锚子件；cutting_head 与 handle 是两半上镜像应用的几何层） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10（1 origin_anchor 母资产 + 9 fork 变体）|
| read_count | 10（全部样本 `model.py` 全文逐行读，含 build_object_model + run_tests；结构冗余高，diff 干净） |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

样本与采纳分工：
- **P0 origin_anchor**（`rec_picturex_0611__pilers_cutting_pliers__001__png_3349bfedf500458989464141d14b0014` ← `pictureX/0611/Pilers_cutting_pliers/001.png`，对角切断钳）：3-part 骨架基线——`root_half`（左柄 + 跨 pivot 到右颚）为 root，`moving_half`（右柄 + 跨 pivot 到左颚镜像）为 moving child，`spring_clip`（可摆动铁丝夹）挂 moving_half 上。锻钢半 = `_forged_half(tang, jaw, thickness)` helper（tang polyline + jaw polyline + boss + pivot_hole）；两 grip 层（red rubber over-mold + blue rubber inlay）；`cutting_edge` 薄片贴颚内面（`cutting_steel`）。`plier_pivot` REVOLUTE (0,0,+1) `[-0.070, 0.34]` 主开合；`clip_swing` REVOLUTE (0,0,+1) `[-0.35, 0.60]` 铁丝夹绕手柄销摆。**Slot Base：diagonal_cutter + straight_dipped_handle + fixed_rivet_leaf 基线**。
- **V-CH1 flush_cutter**（`rec_0611_pilers_cutting_pliers_var_cutting_head_flush_cutter`，fork P0）：`jaw_profile` 改窄短 flush 形（tip 收更平），`cutting_edge_profile` 沿 jaw 内面延一条窄剪刃；part / joint 计数不变。**Slot A：flush_cutter 来源**。
- **V-CH2 end_cutter**（`rec_0611_pilers_cutting_pliers_var_cutting_head_end_cutter`）：`jaw_profile` 改宽圆弧末端 nipper，`cutting_edge_profile` 变宽横带切刃（`x-width > 0.015`）；part / joint 计数不变。**Slot A：end_cutter 来源**。
- **V-CH3 heavy_duty_bevel**（`rec_0611_pilers_cutting_pliers_var_cutting_head_heavy_duty_bevel`）：`jaw_profile` 加宽厚，`cutting_edge_profile` 为宽 bevel 切面；part / joint 计数不变。**Slot A：heavy_duty_bevel 来源**。
- **V-L1 compound_link**（`rec_0611_pilers_cutting_pliers_var_leverage_compound_link`）：`plier_pivot` 从单一 root→moving 拆成两级——`root_half → compound_link` (`plier_pivot`) + `compound_link → moving_half` (`compound_to_moving`, mimic=`plier_pivot`, mult 0.85)；引入 `_compound_link_bar` helper（bar polyline + 两 pivot boss）+ `PIVOT_OFFSET` (~0.006-0.008 m)；4 part / 3 joint。**Slot B：compound_link 来源**。
- **V-L2 high_leverage_offset_pivot**（`rec_0611_pilers_cutting_pliers_var_leverage_high_leverage_offset_pivot`）：pivot 附近加 `pivot_washer_front` / `pivot_washer_rear` 圆盘 + `pivot_pin`，视觉表达 offset high-leverage pivot；part / joint 计数不变。**Slot B：offset_pivot 来源**。
- **V-R1 leaf_spring**（`rec_0611_pilers_cutting_pliers_var_return_leaf_spring`）：`spring_clip` 的 `spring_wire` 从 P0 的 U 形铁丝换成扁 leaf spring polyline（tube_from_spline 直线 + 微弧），仍单 part 单 REVOLUTE `clip_swing`。**Slot C：leaf_spring 来源**。
- **V-R2 torsion_spring**（`rec_0611_pilers_cutting_pliers_var_return_torsion_spring`）：`spring_clip` 的 `spring_wire` 换成绕 pin 的 helical torsion 线圈（`_torsion_spring` helper 生成螺旋 tube），仍单 part 单 REVOLUTE。**Slot C：torsion_spring 来源**。
- **V-H1 long_handle**（`rec_0611_pilers_cutting_pliers_var_handle_long_handle`）：`left_grip_profile` / `left_blue_profile` 拉长（sink 到更负 y），整体尺度增；part / joint 计数不变。**Slot D：long_handle 来源**。
- **V-H2 guarded_insulated_grip**（`rec_0611_pilers_cutting_pliers_var_handle_guarded_insulated_grip`）：`left_grip_profile` 加护手指档凸起 flare；part / joint 计数不变。**Slot D：guarded_insulated_grip 来源**。
- **V-H3 two_material_comfort_grip**（`rec_0611_pilers_cutting_pliers_var_handle_two_material_comfort_grip`）：grip 分两截颜色（red rubber 外壳 + blue rubber comfort inlay 加长加宽）；part / joint 计数不变（仍用同两 grip visual）。**Slot D：two_material_comfort_grip 来源**。

冗余说明：10 个样本核心骨架（两片锻钢半 + 中央 REVOLUTE + spring_clip 端锚子件）完全同构；每个 fork 只改 1 根结构轴，diff 干净。仅 compound_link 改链拓扑（+1 part +1 joint），其余是 part-internal visual 几何 / 关节附属子件变体。

## 核心身份

一把手动切断钳（cutting pliers）：**两片镜像锻钢半钳**，**绕中央 rivet 交叉**，rivet 前方是**成对切断颚**（左右各带一薄 `cutting_edge` 剪刃片，闭合时对切金属丝 / 电线），后方延伸为**成对橡胶浸柄**（相对张合驱动切断）。**主用户机构 = 两半绕中央 rivet 的相对开合**（REVOLUTE，轴 = +Z）；合柄 = 合刃（切断）、张柄 = 分刃。**第二活动子件 = spring_clip**（挂 moving_half 手柄销上，绕 +Z 摆的铁丝/leaf/torsion 弹簧夹，视觉上是复位弹簧或线夹）。

物体平躺 XY 平面（Z = 厚度/枢轴方向）：颚指 +Y，手柄向 -Y 张开；rivet 在世界原点 (0,0,0)。root_half 承左柄 + 右颚（跨 pivot），moving_half 承右柄 + 左颚（跨 pivot 镜像）。cutting_edge 薄片贴颚内面，闭合时对合近触。**leverage=compound_link 特例**：追加 `compound_link` 中间 part（两 pivot boss 相隔 PIVOT_OFFSET~0.006-0.008 m）+ `compound_to_moving` REVOLUTE mimic（跟随 `plier_pivot`，multiplier 0.85），把单级 pivot 拆成两级 toggle。

默认成熟域：真实手工具尺度（整长 ~0.155-0.175 m，宽 ~0.070-0.095 m，jaw 长 ~0.05-0.06 m）。cutting_head 形态可为对角剪 / flush / end / heavy-duty bevel；leverage 可为 fixed_rivet（1 主 REVOLUTE）/ high_leverage_offset_pivot（视觉 washer/pin 增强，仍 1 主 REVOLUTE）/ compound_link（追加 compound_link part + 第二主 REVOLUTE mimic）；return spring 可为 U-wire / leaf / torsion（均单 part 单 clip_swing REVOLUTE，改 spring_wire 几何路径）；handle 可为 straight_dipped / long / guarded_insulated / two_material_comfort（改 grip polyline 与 inlay 分层）。

不该混入：**其他钳（Other_pliers 大类下的综合 / needle_nose / vise-grip / slip-joint / channel-lock）**——本类专职切断（cutting_edge 薄片剪刃 + jaw 尖端在中线对切），Other_pliers 的综合咬颚 / 长尖嘴 / 锁定 / 滑销机构不属本类；**剪刀 / scissors**（两薄刃 shear + finger-loop，本类是锻钢咬颚 + 单主 pivot）；**扳手 / spanner**；**镊子 / tweezers**（无中央 pivot）；**订书机 / 打孔器**（压合冲孔）。

## 槽位 + 候选模块表

> **建模注记（重要）**：pilers_cutting_pliers 的骨架由 **Slot B (leverage_mechanism)** 决定链拓扑（fixed_rivet / offset_pivot = 3-part 链 root→moving + spring_clip；compound_link = 4-part 链 root→compound_link→moving + spring_clip 挂 moving）。**Slot A (cutting_head)** 与 **Slot D (handle_form)** 是两半上镜像应用的 part-internal 几何层。**Slot C (return_spring)** 是 spring_clip 内部 `spring_wire` visual 的路径切换（不改 part / joint 计数）。
> 下面 4 个离散 slot + 1 个 palette 轴（palette_style，仅 ⑥ 涂装，不进 slot_choice / 不改拓扑）。

### Slot A：cutting_head（切断颚形；③ 主体形态家族 / Primary Form Family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype | 结构特征 |
|---|---|---|---|---|---|---|
| diagonal_cutter（基线）| origin_anchor | P0 | `_forged_half` L43-67, `jaw_profile` L107-124, `cutting_edge_profile` L162-174（P0 = end_cutter 变体的对角基线；对角类为 origin_anchor 的实际形态） | eligible if compatible | Planar Boundary Form | 锥形对角剪颚：`jaw_profile` 平面 polyline 从 pivot 向 +Y 收锥（tip x-width ~0.005 m），`cutting_edge` 沿内 edge 铺一条窄剪刃薄片（`cutting_steel` 材质）|
| flush_cutter | forked_anchor | V-CH1 `rec_0611_pilers_cutting_pliers_var_cutting_head_flush_cutter` | `jaw_profile` L107-124, `cutting_edge_profile` L157-168 | eligible if compatible | Planar Boundary Form | 平口 flush 剪：`jaw_profile` 更短窄的 taper (tip 平齐)，`cutting_edge_profile` 沿 tip 一条 flush 平线；对切时两 edge 完全贴合 |
| end_cutter | forked_anchor | V-CH2 `rec_0611_pilers_cutting_pliers_var_cutting_head_end_cutter` | `jaw_profile` L107-122, `cutting_edge_profile` L162-174 | eligible if compatible | Planar Boundary Form | 前端 nipper：`jaw_profile` 前端加宽成圆弧 head，`cutting_edge` 为宽横带切刃（`x-width > 0.015`）|
| heavy_duty_bevel | forked_anchor | V-CH3 `rec_0611_pilers_cutting_pliers_var_cutting_head_heavy_duty_bevel` | `jaw_profile` L107-124, `cutting_edge_profile` L157-168 | eligible if compatible | Planar Boundary Form | 重型 bevel：`jaw_profile` 更宽加厚 shoulder，`cutting_edge` 为宽 bevel 切面（thickness 0.001 m，比基线 0.0008 更厚）|

> 4 candidate（达 3-6 目标）。每个只改 `jaw_profile` 与 `cutting_edge_profile` 平面 polyline 的可识别形态原型（Planar Boundary Form），保 part tree / interface / primitive 家族一致，改 run_tests 几何断言（如 end_cutter 的 `ce_width > 0.015`）。

### Slot B：leverage_mechanism（枢轴 / 杠杆机构；② 关节 / 骨架轴，决定链拓扑）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| fixed_rivet（基线）| origin_anchor | P0 | `plier_pivot` L282-299（P0）| eligible if compatible | 单一中央 `plier_pivot` REVOLUTE，axis (0,0,+1)，range `[-0.070, 0.34]`；3-part 链 root→moving；rivet 为 root_half 内 inline visual（`pivot_pin` cylinder） |
| offset_pivot | forked_anchor | V-L2 `rec_0611_pilers_cutting_pliers_var_leverage_high_leverage_offset_pivot` | pivot_washer visuals L216-233（P0 already carries `pivot_washer_front/rear` + `pivot_pin` cylinders in root_half）| eligible if compatible | 视觉 high-leverage：在 root_half pivot 处追加 `pivot_washer_front` + `pivot_washer_rear` 圆盘（0.0075 m 半径 × 0.0015 m 厚，`polished_steel`），保单一 REVOLUTE 与 3-part 链；改 run_tests 断言 `pivot_washer_front` 存在 |
| compound_link | forked_anchor | V-L1 `rec_0611_pilers_cutting_pliers_var_leverage_compound_link` | `_compound_link_bar` L70-118, `compound_link` part L287-303, `plier_pivot` L361-378, `compound_to_moving` (mimic) L381-398 | eligible if compatible | 追加 `compound_link` part（`_compound_link_bar` helper：两 pivot boss 相隔 PIVOT_OFFSET~0.007 m 的锻钢 toggle bar）+ 第二 REVOLUTE `compound_to_moving` mimic (`plier_pivot`, mult 0.85, offset 0)；4-part 链 root→compound_link→moving |

> 3 candidate（达目标下限）。fixed_rivet / offset_pivot 保 3-part 链、改 root_half 内 visual；compound_link 改链拓扑（+1 part +1 joint）——结构差异显著。

### Slot C：return_spring（复位弹簧形态；② 关节附属子件几何）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| wire_clip（基线）| origin_anchor | P0 | `spring_wire = tube_from_spline_points` L305-321（U 形铁丝）| eligible if compatible | U 形 wire clip：`tube_from_spline_points` 铺一段闭合 U（长度 ~0.022 m，半径 0.00115 m），仍 spring_clip 单 part 单 `clip_swing` REVOLUTE |
| leaf_spring | forked_anchor | V-R1 `rec_0611_pilers_cutting_pliers_var_return_leaf_spring` | `spring_wire` at L280-320（tube_from_spline_points 的更直、更长 polyline，含微弧）| eligible if compatible | 扁 leaf spring 长带：spline 走近直线略弧（长 ~0.030 m）; 半径微加大成 leaf 断面感（0.0014）；仍单 part 单 REVOLUTE |
| torsion_spring | forked_anchor | V-R2 `rec_0611_pilers_cutting_pliers_var_return_torsion_spring` | `_torsion_spring` helper L65-... + spring_wire mesh; part L356-364| eligible if compatible | 绕 pin 的 helical torsion 线圈：helper 生成螺旋 `tube_from_spline_points`（多圈螺旋 + 两臂延伸），仍单 part 单 REVOLUTE |

> 3 candidate（达目标下限）。三者改 `spring_clip` 内部 `spring_wire` visual 的 spline 路径（U / leaf / helical），保 spring_clip 单 part 单 `clip_swing` REVOLUTE、interface 到 moving_half 的 `clip_pin` 不变，结构差异成立（U vs leaf vs 螺旋是可识别几何家族）。

### Slot D：handle_form（手柄形态；① 骨架 + 装饰共轴，实为 grip polyline 家族切换）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| straight_dipped（基线）| origin_anchor | P0 | `left_grip_profile` L123-138, `left_blue_profile` L139-149（P0） | eligible if compatible | 直筒橡胶浸塑柄：`left_grip_profile` 长 ~0.104 m 半宽 ~0.017 m，`left_blue_profile` inlay 沿外侧，`cornerRadius` 0.0022 |
| long_handle | forked_anchor | V-H1 `rec_0611_pilers_cutting_pliers_var_handle_long_handle` | `left_grip_profile` L131-160（拉长版；min_y 更负）| eligible if compatible | 加长直柄：grip polyline min_y 到 -0.125 m（vs 基线 -0.109 m），整体拉长；`left_blue_profile` 随之延展 |
| guarded_insulated_grip | forked_anchor | V-H2 `rec_0611_pilers_cutting_pliers_var_handle_guarded_insulated_grip` | `left_grip_profile` L120-153（含指档 flare）| eligible if compatible | 护手指档柄：`left_grip_profile` 在中段 -0.06...-0.08 m 处加宽 flare（半宽 +0.005 m）形成指挡；`left_blue_profile` 局部内凹 |
| two_material_comfort_grip | forked_anchor | V-H3 `rec_0611_pilers_cutting_pliers_var_handle_two_material_comfort_grip` | `left_grip_profile` L123-140, `left_blue_profile` L141-160（加宽加长 comfort inlay）| eligible if compatible | 双材质舒适柄：`left_blue_profile` 加宽 comfort inlay（半宽 +0.003 m）并加长（min_y -0.115），`left_grip_profile` 局部覆盖 |

> 4 candidate（达目标 3-6）。四者改 `left_grip_profile` / `left_blue_profile` 平面 polyline（拉长 / 护手 flare / 加大 inlay），保 part / joint 计数与 red+blue 两 grip visual 结构不变，结构差异成立（形态原型不同）。

## 槽位图（slot graph）

```
pattern: mixed（3-part pivot 链 + 端锚 spring_clip；leverage=compound_link 追加 1 part + 1 joint 变成 4-part 链；
                cutting_head / handle 为两半镜像 part-internal 几何层；return_spring 为 spring_clip 内 spring_wire 几何切换）

  ── Slot B = fixed_rivet / offset_pivot（3-part 链，基线）──
    root_half (root)  ──[REVOLUTE plier_pivot, axis +Z, origin (0,0,0)]──>  moving_half
       承载: jaw[A]·cutting_edge·hub·pivot_pin·red_grip[D]·blue_inlay·                   承载: jaw[A 镜像]·cutting_edge·red_grip[D 镜像]·blue_inlay·
       (offset_pivot 追加 pivot_washer_front/rear)                                         clip_pin (spring_clip 附着点)
                                                                                          │
                                                                    [REVOLUTE clip_swing, axis +Z, origin (0.030, -0.086, 0.013)]
                                                                                          ↓
                                                                              spring_clip (承载 spring_wire[C])

  ── Slot B = compound_link（4-part 链）──
    root_half (root)  ──[REVOLUTE plier_pivot, axis +Z, origin (0, PIVOT_OFFSET, 0)]──>  compound_link
       承载: jaw[A]·cutting_edge·red_grip[D]·pivot_washer                              承载: compound_bar (bar polyline + 两 pivot boss)
                                                                                          │
                                                        [REVOLUTE compound_to_moving, axis +Z, origin (0, -2*PIVOT_OFFSET, 0), mimic=plier_pivot × 0.85]
                                                                                          ↓
                                                                                  moving_half
                                                                                    承载: jaw[A 镜像]·cutting_edge·red_grip[D 镜像]·clip_pin
                                                                                          │
                                                                       [REVOLUTE clip_swing, axis +Z]
                                                                                          ↓
                                                                                    spring_clip
```

接口点位（每条连接）：
- **root_half → moving_half（fixed_rivet / offset_pivot，plier_pivot）**：mating = 中央 rivet 轴线（`origin=(0,0,0)`，两 hub 半-lap 共轴），joint = REVOLUTE，axis `(0,0,+1)`，range `[-0.070, 0.34]`（scale by `open_angle_scale`）。**MatingContract 省略（grandfathered）**：rivet pin cylinder 是 root_half 的 inline visual (`pivot_pin`)，两 forged 半的 z-lap 由 `expect_gap axis=z` 强制接触，配 broad `allow_overlap(root_half, moving_half)` reason。origin 落 pivot cylinder 真实几何 (≤0.002 m)。
- **root_half → compound_link（compound_link 分支，plier_pivot）**：mating = root_half 的 pivot boss（`origin=(0, PIVOT_OFFSET, 0)` 落 compound_link 上端 pivot boss），joint = REVOLUTE，axis `(0,0,+1)`，range `[-0.050, 0.24]`。MatingContract 省略（captured toggle bar，grandfathered）。
- **compound_link → moving_half（compound_link 分支，compound_to_moving，mimic）**：mating = compound_link 下端 pivot boss（`origin=(0, -2*PIVOT_OFFSET, 0)`），joint = REVOLUTE，axis `(0,0,+1)`，range `[-0.060, 0.24]`，`mimic=Mimic(joint="plier_pivot", multiplier=0.85, offset=0.0)`。MatingContract 省略。
- **moving_half → spring_clip（clip_swing，所有分支）**：mating = moving_half 的 `clip_pin` cylinder（`origin=(0.030, -0.086, 0.013)`，clip_pin 半径 0.0023 m），joint = REVOLUTE，axis `(0,0,+1)`，range `[-0.35, 0.60]`；spring_wire 铺围绕 pin 的路径，captured-pin overlap 由 `allow_overlap(moving_half, spring_clip, elem_a="clip_pin", elem_b="spring_wire", reason="visible spring clip is intentionally captured around its handle pin")` 声明（不设 MatingContract）。
- **cutting_edge、pivot_washer、pivot_pin、blue_inlay 等**：root_half 或 moving_half 内的 inline visual（FIXED 语义，不建独立装饰 part）。
- **互斥/可选/派生**：Slot B 决定 3-part vs 4-part 链（互斥）；Slot A / C / D 与 Slot B 正交（任一 leverage 均可叠任一 cutting_head / return_spring / handle）；jaw 与 grip 在两半上镜像派生（moving_half = root_half `mirror("YZ")` + `_mirror_x` on grip / inlay / cutting_edge profiles）。

## 每槽位 Module Emits / Interfaces

### Slot A / module diagonal_cutter
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `forged_steel` (jaw profile 内含), `cutting_edge`（对角剪刃薄片，cutting_steel）| P0 / `jaw_profile` L107-124、`cutting_edge_profile` L162-174 |
| internal joints | 无（刃是 part visual）| — |
| downstream interface | 刃口在 pivot 前方对合近触（`expect_gap axis=x` positive_elem=cutting_edge）| P0 / L458-467 |

### Slot A / module flush_cutter
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `forged_steel` (窄短 flush jaw), `cutting_edge`（flush 平线剪刃）| V-CH1 / `jaw_profile` L107-124、`cutting_edge` L157-168 |
| downstream interface | 两 flush edge tip 闭合 gap ≈ 0（`expect_gap max_gap=0.0005`）| V-CH1 / L508-514 |

### Slot A / module end_cutter
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `forged_steel`（宽圆弧 nipper 前端）, `cutting_edge`（宽横带切刃，`x-width > 0.015`）| V-CH2 / L107-124, L162-174 |
| downstream interface | 前端 nipper 横带在中线对合；断言 cutting_edge x-width > 0.015 | V-CH2 / L449-456 |

### Slot A / module heavy_duty_bevel
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `forged_steel`（宽厚 shoulder jaw）, `cutting_edge`（宽 bevel 切面 thickness 0.001）| V-CH3 / L107-124, L157-168 |
| downstream interface | bevel 面在中线对合；断言 cutting_edge 面积/宽度加大 | V-CH3 / L450-460 |

### Slot B / module fixed_rivet
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `pivot_pin`（Cylinder r=0.004, l=0.015），root_half inline | P0 / L216-221 |
| internal joints | `plier_pivot` REVOLUTE，axis (0,0,+1)，range `[-0.070, 0.34]`（root_half→moving_half）| P0 / L282-299 |
| upstream/downstream interface | 两 forged 半 z-lap 接触 (`expect_gap axis=z max_gap=0.0001`) + broad `allow_overlap(root_half, moving_half)` | P0 / L468-477 |

### Slot B / module offset_pivot
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `pivot_pin` + `pivot_washer_front` (Cylinder r=0.0075, l=0.0015, z=+0.00675) + `pivot_washer_rear` (z=-0.00675), root_half inline | P0/V-L2 / L216-233 |
| internal joints | `plier_pivot` REVOLUTE 同 fixed_rivet | 同上 |
| upstream interface | `expect_contact(root_half, moving_half, elem_a="pivot_washer_front", elem_b="forged_steel")` 断言 washer 顶靠 moving_half | P0 / L478-484 |

### Slot B / module compound_link
| emits | 描述 | 来源 |
|---|---|---|
| parts | `compound_link`（`_compound_link_bar(0.0045)` = 锻钢 toggle bar polyline + 两 pivot boss @ y=0 和 y=-2*PIVOT_OFFSET）| V-L1 / L70-118, L287-303 |
| internal joints | `plier_pivot` REVOLUTE (root→compound_link, axis +Z, origin (0, PIVOT_OFFSET, 0), range `[-0.050, 0.24]`) + `compound_to_moving` REVOLUTE mimic (compound_link→moving, origin (0, -2*PIVOT_OFFSET, 0), axis +Z, mimic plier_pivot × 0.85, range `[-0.060, 0.24]`) | V-L1 / L361-398 |
| upstream/downstream interface | 上端 boss captured 于 root_half pivot；下端 boss captured 于 moving_half hub；两处 broad `allow_overlap` | V-L1 / L360-398 |

### Slot C / module wire_clip
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `spring_wire`（`tube_from_spline_points` U 形铁丝：8 点闭合 U，长 0.022 m，半径 0.00115 m）| P0 / L305-325 |
| upstream interface | spring_wire 围绕 moving_half 的 `clip_pin` (r=0.0023, l=0.005) 缠绕；expect_contact + allow_overlap | P0 / L489-511 |

### Slot C / module leaf_spring
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `spring_wire`（`tube_from_spline_points` 近直 leaf spline：起自 clip_pin 沿 -y 方向直走，末端微弧，长 ~0.030 m，tube 半径 ~0.0014 m）| V-R1 / L280-320 |
| upstream interface | 起点与 clip_pin 重叠；spring_clip 单 part 单 REVOLUTE 不变 | V-R1 |

### Slot C / module torsion_spring
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `spring_wire`（helper `_torsion_spring(coils, radius, ...)` 生成螺旋 tube：2-3 圈绕 pin 螺旋 + 两臂延伸）| V-R2 / L65-... |
| upstream interface | 螺旋中轴与 clip_pin 共轴；spring_clip 单 part 单 REVOLUTE 不变；elem_a="clip_pin" elem_b="spring_wire" 的 allow_overlap 覆盖螺旋圈 | V-R2 |

### Slot D / module straight_dipped
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `red_grip`（`_profile_solid(left_grip_profile, 0.016, corner_radius=0.0022)`），`blue_inlay`（`_profile_solid(left_blue_profile, 0.0164, corner_radius=0.0014)`）| P0 / L123-149, L189-206 |
| upstream interface | grip 接 tang 末端向 -y 延伸；两半镜像 (`_mirror_x`) | P0 / L248-265 |

### Slot D / module long_handle
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 拉长版 `left_grip_profile`（min_y -0.125）+ 拉长 `left_blue_profile` | V-H1 / L131-160 |
| upstream interface | 同基线，整体沿 -y 方向拉长 ~15%；影响整长断言（放宽 length upper bound） | V-H1 |

### Slot D / module guarded_insulated_grip
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 带指档 flare 的 `left_grip_profile`（中段半宽 +0.005 m）+ `left_blue_profile` 局部内凹 | V-H2 / L120-153 |
| upstream interface | 同基线；断言 grip 中段宽度加大 | V-H2 |

### Slot D / module two_material_comfort_grip
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `left_grip_profile`（red）+ 加宽加长 `left_blue_profile`（comfort inlay，半宽 +0.003 m，min_y -0.115）| V-H3 / L123-160 |
| upstream interface | 同基线；两 grip visual 结构不变 | V-H3 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| cutting_head | enum | {diagonal_cutter, flush_cutter, end_cutter, heavy_duty_bevel} | diagonal_cutter | choice | deterministic procedural sampler 选择 | Slot A |
| leverage_mechanism | enum | {fixed_rivet, offset_pivot, compound_link} | fixed_rivet | choice | sampler 选择；决定 3-part vs 4-part 链 | Slot B |
| return_spring | enum | {wire_clip, leaf_spring, torsion_spring} | wire_clip | choice | sampler 选择 | Slot C |
| handle_form | enum | {straight_dipped, long_handle, guarded_insulated_grip, two_material_comfort_grip} | straight_dipped | choice | sampler 选择 | Slot D |
| palette_style | enum | {steel_red_blue, black_orange, chrome_natural, gunmetal_yellow, polished_silver, industrial_green} | steel_red_blue | palette | **palette only，不进 slot_choice / 不改拓扑**；按 seed 采样 | P0 配色 + 世界知识扩展 |
| overall_len_scale | float | [0.90, 1.15] | 1.0 | independent | 整体等比缩放；clamp 保真实手工具尺度（整长 ∈ [0.140, 0.185]）| P0 整长 ~0.16 m |
| jaw_len_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 jaw_profile 与 cutting_edge_profile 的 y 方向 taper；clamp 保闭合接触 | P0 `jaw_profile` L107-124 |
| grip_girth_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 grip half-width；clamp 保两 grip 在 rest pose 不互穿 | P0 `left_grip_profile` |
| open_angle_scale | float | [0.80, 1.20] | 1.0 | independent | 缩放主 `plier_pivot` upper (0.34) 与 lower (-0.070)；clamp 到 upper ∈ [0.20, 0.42], lower ∈ [-0.10, -0.03] | P0 L288-294 |
| (—) | constraint | — | — | inequality | 中央 pivot origin 必须落 (0,0,0)±0.002 m；scale 不改 pivot 几何位置；两 forged 半 z-lap 接触 (gap ≤ 0.0001) 恒立 | 接口 / captured-pin |
| (—) | constraint | — | — | inequality | jaw_len × jaw_profile max_y 必须 ≤ 0.06 m（真实 jaw 长上限），且合刃 gap ∈ [0.0, 0.006] | 接口 / cutting_edge |

连续 scale 默认独立采样 → inequality 把 pivot origin 钉真实几何 + jaw 长上限守门。全部在 `resolve_config` 内求解。**palette_style 只换 material rgba，绝不进 slot_choice / 不改拓扑。**

### 7.5 编译预算 / compile budget

自报本类别每-seed 编译预算 **~12-18 s**（依据：3-4 part、5-9 visual per part、`_profile_solid` polyline extrude + `_forged_half` union 是主 CQ 成本；无重布尔雕刻、无 loft、无 groove 循环；参考类比 Other_pliers 无 slip 分支的 fixed_rivet 分支）。分档 tessellation：pivot_pin / washer / clip_pin 用 SDK `Cylinder`（不设自定义段数）；polyline 剪刃 / grip 通过 CQ extrude（内部默认 tolerance 0.0002）。所有 forged_steel mesh 用 `mesh_from_cadquery(..., tolerance=0.0002)`；spring wire tube 用 `tube_from_spline_points(samples_per_segment=16, radial_segments=18)`（P0 参数，torsion_spring 保持相同）。超出预算先降 spring_wire 的 samples_per_segment / radial_segments，再迭代（§C）。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots 表达（cutting_head / leverage / return_spring / handle），不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。source map 无多重性轴（`count_param: no strong repeated-part axis planned`）；本类无 groove / 齿列 / 叶片阵列可参数化。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Slot B leverage_mechanism：fixed_rivet / offset_pivot（3-part 链）vs compound_link（4-part 链 +1 REVOLUTE mimic）；source_type=forked_anchor (V-L1) |
| └ multiplicity | 同构件 ×N | 无 | 本类无强多重性轴（无 groove / 齿列 / 阵列子件）——source map 明示 `count_param: no strong repeated-part axis planned`；核心机构由 3-4 命名 part 组成，无需复制 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | 全部 REVOLUTE 绕 +Z（主 pivot + clip_swing + 可选 compound_to_moving mimic）；轴族一致，通过 Slot B 引入 mimic 依赖轴（compound_to_moving mimic plier_pivot × 0.85）改关节生态；source_type=forked_anchor (V-L1) |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | 有 | Slot A cutting_head：diagonal_cutter / flush_cutter / end_cutter / heavy_duty_bevel 四种可识别 jaw 平面轮廓 + cutting_edge 形态（4 个 candidate，均 form_subtype=Planar Boundary Form）；source_type=forked_anchor (V-CH1/2/3) + origin_anchor (P0) |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | Slot D handle_form 的 blue_inlay 分层（straight_dipped 单 inlay、two_material 加大 inlay）+ Slot B offset_pivot 的 washer 装饰环；host-conformal，非独立 module；source_type=record_only |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | overall_len_scale [0.90,1.15]、jaw_len_scale [0.90,1.10]、grip_girth_scale [0.90,1.10]、open_angle_scale [0.80,1.20]；关节运动包络：plier_pivot 轴 +Z open direction=upper，`[-0.070, 0.34]` × scale ∈ [-0.10, -0.03] × [0.20, 0.42]；clip_swing 轴 +Z `[-0.35, 0.60]`（固定不 scale）；compound_to_moving 轴 +Z mimic；motion_test_plan：跑 sampled collision、sampled pose 覆盖 open (upper) / closed (lower) / rest (0) 三态；无 continuous 关节；无需 exemption |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | palette_style 6 档：steel_red_blue / black_orange / chrome_natural / gunmetal_yellow / polished_silver / industrial_green；材质大类覆盖 metal (forged/polished/cutting steel) + rubber (red/blue over-mold)；档数 ≥ 3-6 目标；material 大类覆盖 = 2（metal + rubber）达 ceil(0.5 × 6) = 3 未达标 → 加 chrome_natural 全 metal 档、polished_silver 全 metal 档（rubber 换 dark_metal 涂装占位）→ metal 涵盖 3 档，rubber 涵盖 3 档；见 §palette |

**收尾自检**：本表每个"有"里列的取值，必须在 `template batch` 的 0-9 seed 渲染里肉眼可见地出现——4 个 cutting_head 拉得开、3 个 leverage 机构 (含 compound_link 4-part 链) 出现、3 个 return_spring (U / leaf / torsion) 可辨、4 个 handle_form 长短/护手/comfort 各现、6 个 palette 覆盖 metal / rubber 大类。做不到 = 本节未达标。

## 采样与覆盖审计

总组合数（离散槽）：cutting_head(4) × leverage_mechanism(3) × return_spring(3) × handle_form(4) = **144** distinct 拓扑等价类。

理由：仅离散槽即 144 > 100，覆盖成熟度足；本类无 multiplicity 乘子（source map 声明无强多重性轴），不再叠加乘子。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed 做 deterministic procedural sampling——加权选 cutting_head / leverage_mechanism / return_spring / handle_form（diagonal_cutter / fixed_rivet / wire_clip / straight_dipped 偏多），采连续 scale，经 `resolve_config` 解析 inequality（pivot origin 钉几何、jaw 长上限）。`seed=0` 不特殊。无 regression overrides（如 sweep 暴露特定 seed 失败，再稀疏加）。
Topology target：1000-seed slot choice tuple distinct 目标 = 144（本类离散组合上界）。若实测偏低，多因权重偏向基线，可微调 leverage=compound_link / cutting_head 非基线权重。（统一口径：富类别建议 ≥300；本类 144 因样本词汇表限制，report-only。）
Controlled local parameterization：初版即含 `overall_len_scale` / `jaw_len_scale` / `grip_girth_scale` / `open_angle_scale`，全部 clamp/inequality，受 pivot origin、jaw 上限、grip 互穿、真实开度约束，不改变拓扑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 顺序：cutting_head → leverage_mechanism → return_spring → handle_form → scales → palette；加权（cutting_head 偏 diagonal、leverage 偏 fixed_rivet、return 偏 wire_clip、handle 偏 straight_dipped）| slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | (1) 所有 slot 正交（任一 leverage 均可叠任一 cutting_head / return_spring / handle）。(2) pivot origin 恒钉 (0,0,0) 真实几何（compound_link 分支时 origin 落 compound_link boss 真实几何 (0, PIVOT_OFFSET, 0)）；rivet pin captured 配 broad allow_overlap。(3) jaw_len_scale × max_y ≤ 0.06 m；grip_girth_scale × max_half_w 保两半 grip rest 不互穿。(4) clip_pin 与 spring_wire captured-pin 恒有 allow_overlap + expect_overlap。| 无 floating / collision / captured-pin origin 漂移 / cutting_edge 不合刃 / grip 互穿 |
| controlled local variation | 4 个 clamped scale（overall_len / jaw_len / grip_girth / open_angle），每 build 统一 | 比例变化不破坏 pivot origin、jaw 上限、grip 互穿、joint range、类别身份 |
| regression overrides | none（首版纯 procedural） | 仅 sweep 暴露的具体失败 seed 才稀疏添加并注明 |
| random sweep | 初轮 seeds 0-49，成熟审计 0-999 | captured-pin overlap / cutting_edge 合刃 / grip 互穿 / compound_link 4-part 链装配 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A cutting_head | 4 | yes | yes | diagonal / flush / end / heavy_duty_bevel |
| B leverage_mechanism | 3 | yes | yes | fixed_rivet(1 主 REVOLUTE) / offset_pivot(+washer 装饰) / compound_link(+1 part +1 mimic joint) |
| C return_spring | 3 | yes | yes | wire_clip / leaf_spring / torsion_spring |
| D handle_form | 4 | yes | yes | straight_dipped / long / guarded_insulated / two_material_comfort |

## Validator

- slot_choices_for_seed returns implemented module names（cutting_head / leverage_mechanism / return_spring / handle_form）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating：所有 slot 正交；pivot origin 恒钉 (0,0,0)（fixed/offset）或 (0, PIVOT_OFFSET, 0)（compound_link）真实几何；jaw_len × max_y ≤ 0.06；grip 互穿守门
- optional regression overrides 初版为空
- controlled local scale params 全部 clamp，不破坏 pivot origin / jaw 上限 / grip 互穿 / joint range / 类别身份
- cross-part scale dependencies 在 `resolve_config` 求解，不留到 builder 失败
- critical captured-pin overlap：rivet pin captured 于两半 z-lap（broad `allow_overlap(root_half, moving_half)`, reason="rivet pin captured through hub lap"）；clip_pin captured 于 spring_wire（elem-scoped `allow_overlap(moving_half, spring_clip, elem_a="clip_pin", elem_b="spring_wire", reason=…)`）；compound_link 分支两 boss captured 于 root/moving hub（broad `allow_overlap`）
- key joints：`plier_pivot` REVOLUTE axis (0,0,+1) range 依 leverage 分支；`clip_swing` REVOLUTE axis (0,0,+1) range `[-0.35, 0.60]`；compound_link 分支 `compound_to_moving` REVOLUTE mimic (`plier_pivot` × 0.85)
- 开合测试：pose `plier_pivot` 到 upper 使两 cutting_edge x 分离（`open_edge[0][0] < rest_edge[0][0] - 0.008`）、两 grip x 张开（`open_grip[1][0] > rest_grip[1][0] + 0.015`）；pose 到 lower（closed）使 cutting_edge gap 收至 ≤ 0.0005；pose `clip_swing` 到 0.35 使 spring_clip x 摆动
- palette_style 只换 material rgba，不进 slot_choice、不改拓扑
- 所有 `.visual(material=mats[...])` 用 `mats` dict 索引，禁止 fixed material name

## Reject cases

- 把中央 pivot 做成 FIXED 或省略（切断钳必须有两半相对开合的 REVOLUTE）
- pivot origin 不落 (0,0,0)（fixed/offset）或 (0, PIVOT_OFFSET, 0)（compound_link）真实几何（漂浮 >0.002 m），或缺 broad allow_overlap 两半 → captured-pin 判失败
- 两 cutting_edge 不在 pivot 前方对合近触（gap 越过 0.006），或开合 pose 不分离 cutting_edge（pivot pose 变化 cutting_edge 不动）
- leverage_mechanism=compound_link 但缺 `compound_link` part 或缺第二 REVOLUTE `compound_to_moving`（compound_link 要求追加真实中间 part + mimic 关节）
- return_spring=torsion_spring 但 spring_wire 不成螺旋（退化成直线）或 helix 中轴不与 clip_pin 共轴（漂浮）
- handle_form=guarded_insulated_grip 未在 grip 中段加 flare 指档（退化成 straight）；或 long_handle 未真正拉长（min_y 未越过 -0.115）
- cutting_head=end_cutter 但 cutting_edge x-width 未 > 0.015（退化成 diagonal）
- 用 boxy 占位代替真实 jaw / grip / cutting_edge polyline
- 连续 scale 把钳放到非真实尺度（overall_len_scale 越界使整长 < 0.14 或 > 0.185 m）
- config_from_seed 采到非法组合（本类所有 slot 正交，无非法组合）；如 palette_style 混进 slot_choice 则拓扑污染
- 把 palette_style / 连续尺寸当新 candidate 塞进 slot（非结构差异）

## 与相邻类别的边界

- 不该混入：**Other_pliers 综合 / vise-grip / slip-joint / channel-lock**（本类专切断：cutting_edge 薄片剪刃 + jaw 尖端在中线对切；综合咬颚 / 锁定 / 滑销机构不属本类）
- 不该混入：**needle_nose pilers**（细长尖嘴钳，属 pilers_needle_nose_pliers 独立小类）
- 不该混入：**scissors / shears**（两薄刃 shear + finger-loop，本类是锻钢咬颚 + 单主 pivot + 橡胶浸柄）
- 不该混入：**扳手 / wrench**（无枢轴开合的固定/活络开口）
- 不该混入：**镊子 / tweezers**（无中央 rivet 枢轴，弹性夹臂）
- 不该混入：**订书机 / 打孔器 / 冲子**（压合/冲孔机构，不出双臂中央枢轴）
- 0611 大类内：区别于 pilers_linesman / fencing / locking / needle_nose / slip_joint / tongue_groove / wire_strippers 各自独立小类（各类核心颚形与机构不同）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工确认：(1) 6 档 palette 是否达标（metal 3 + rubber 3 覆盖 ceil(0.5×6)=3）；(2) leverage_mechanism=compound_link 的 mimic 关节视作 ② 骨架轴 vs 单独轴的分类；(3) return_spring 三档中 leaf_spring / torsion_spring 的 spring_wire spline 参数化范围是否足够真实；(4) handle_form 4 档中 two_material_comfort_grip 是否与 straight_dipped 差异足够（inlay 加大）；(5) 本类无 multiplicity 是否符合审计期望（source map 明示无）。 |

## 模板实现备注（可选）

- 共享 helper：`_profile_solid(points, thickness, corner_radius)`（P0 已用；polyline→extrude→fillet 单件）、`_forged_half(tang, jaw, thickness)`（tang + boss + jaw + pivot_hole）、`_mirror_x(points)`、`_compound_link_bar(thickness)`（compound_link 分支）、`_torsion_spring_wire(coils, r)` (torsion 分支)。
- 关键 captured-pin overlap：**broad** `allow_overlap(root_half, moving_half, reason="rivet pin captured through hub lap")`（fixed_rivet / offset_pivot / compound_link 均声明）；**elem-scoped** `allow_overlap(moving_half, spring_clip, elem_a="clip_pin", elem_b="spring_wire", reason=...)`；compound_link 分支加 `allow_overlap(root_half, compound_link)` + `allow_overlap(compound_link, moving_half)`。
- 主 `plier_pivot` / `clip_swing` / `compound_to_moving` joint 均**省略 MatingContract**（captured-pin grandfathered）；origin 落真实 pivot cylinder / boss / clip_pin 几何 (≤0.002 m)。
- 派生与门控集中在 `resolve_config`：无条件门控（所有 slot 正交）；scale clamp；jaw_len 上限守门。
- 链拓扑由 leverage_mechanism 派生：fixed_rivet / offset_pivot=3-part（root→moving + spring_clip 挂 moving）；compound_link=4-part（root→compound_link→moving + spring_clip 挂 moving）。builder 按所选 leverage 选择 part / joint 装配路径。
- 开合测试：pose `plier_pivot` 到 upper 使 cutting_edge min_x 减小、grip max_x 增大；pose 到 lower 使 cutting_edge gap ≤ 0.0005；pose `clip_swing` 到 0.35 使 spring_clip max_x 增大 > 0.005；compound_link 分支 mimic 自动 pose `compound_to_moving`。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| P0 | A/B/C/D | diagonal_cutter / fixed_rivet / wire_clip / straight_dipped | rec_picturex_0611__pilers_cutting_pliers__001__png_3349bfedf500458989464141d14b0014 | `_forged_half` L43-67, jaw_profile L107-124, cutting_edge_profile L162-174, left_grip_profile L123-138, left_blue_profile L139-149, plier_pivot L282-299, clip_swing L326-340, spring_wire L305-321 | 3-part / 2-joint 骨架基线；diagonal_cutter + straight_dipped + fixed_rivet + wire_clip 各 slot 基线 |
| V-CH1 | A | flush_cutter | rec_0611_pilers_cutting_pliers_var_cutting_head_flush_cutter | jaw_profile L107-124, cutting_edge_profile L157-168 | 平口 flush 剪颚 |
| V-CH2 | A | end_cutter | rec_0611_pilers_cutting_pliers_var_cutting_head_end_cutter | jaw_profile L107-122, cutting_edge_profile L162-174, run_tests 断言 x-width>0.015 L449-456 | 前端 nipper 宽横带切刃 |
| V-CH3 | A | heavy_duty_bevel | rec_0611_pilers_cutting_pliers_var_cutting_head_heavy_duty_bevel | jaw_profile L107-124, cutting_edge_profile L157-168 | 重型 bevel 切面 |
| V-L1 | B | compound_link | rec_0611_pilers_cutting_pliers_var_leverage_compound_link | `_compound_link_bar` L70-118, compound_link part L287-303, plier_pivot L361-378, compound_to_moving (mimic) L381-398 | 4-part 链 + toggle bar + mimic 关节 |
| V-L2 | B | offset_pivot | rec_0611_pilers_cutting_pliers_var_leverage_high_leverage_offset_pivot | pivot_washer_front/rear + pivot_pin visuals L216-233 | 视觉 offset high-leverage washer/pin |
| V-R1 | C | leaf_spring | rec_0611_pilers_cutting_pliers_var_return_leaf_spring | spring_wire tube_from_spline_points L280-320 | 扁 leaf spring |
| V-R2 | C | torsion_spring | rec_0611_pilers_cutting_pliers_var_return_torsion_spring | `_torsion_spring` helper L65-...、spring_wire mesh + spring_clip part L356-364 | helical torsion 螺旋 |
| V-H1 | D | long_handle | rec_0611_pilers_cutting_pliers_var_handle_long_handle | left_grip_profile L131-160 | 加长直柄 |
| V-H2 | D | guarded_insulated_grip | rec_0611_pilers_cutting_pliers_var_handle_guarded_insulated_grip | left_grip_profile L120-153 | 护手指档 flare |
| V-H3 | D | two_material_comfort_grip | rec_0611_pilers_cutting_pliers_var_handle_two_material_comfort_grip | left_grip_profile L123-140, left_blue_profile L141-160 | 加宽加长 comfort inlay |
