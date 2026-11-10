# pilers_slip_joint_pliers — Modular Spec

> 来源小类：`pictureX/0611/Pilers_slip_joint_pliers`（articraft_data 上游小类样本池；对象身份为一把家用滑动销钳/slip-joint pliers——两片锻钢半钳通过一个**可选位置的滑动 pivot 销**交叉，pivot 可在 slot_guide 上被切换到 2/3/5/7 个 detent 位置，头部为带齿的抓咬颚，柄部张合驱动开合）。slug 采本仓库规范 `pilers_slip_joint_pliers`。
> 上游 source map：`picture_expansion/template_source_maps/0611__Pilers_slip_joint_pliers.md`。
> **同步状态**：本 spec 引用的 8 个 5★ 样本（1 origin_anchor 的 fork 变体：3 pivot_positions / 2 jaw_form / 2 pivot_topology / 1 handle）+ 1 母资产（`slip_joint_pliers_001`，`rec_picturex_0611__pilers_slip_joint_pliers__001__png_730c921fd05840c19617cdf595353d1e`）均已同步 `data/records/rec_0611_pilers_slip_joint_pliers_*/revisions/rev_000001/model.py`（rating=5）。行号按各样本 rev_000001/model.py 计。
> **建模基线**：origin 母资产共享 **4-part / 3-joint 骨架**：`slot_guide` (root) + `pivot_slider` + `round_member` + `slotted_member`。`guide_to_slider` PRISMATIC (guide→slider, axis +X) 切换 pivot 位置；`slider_to_round_member` REVOLUTE (slider→round, axis +Z) + `slider_to_slotted_member` REVOLUTE (slider→slotted, axis +Z) 是钳子的开合双 hinge。push_button_selector 追加 `selector_button` part + `slider_to_button` PRISMATIC axis -Z（+1 part / +1 joint → 5-part / 4-joint）。

## 元信息
| 项 | 值 |
|---|---|
| slug | `pilers_slip_joint_pliers` |
| template path | `agent/templates/pilers_slip_joint_pliers.py` |
| test path (optional) | 无（sweep-pipeline 为唯一验收） |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel-children：两 forged member 都以 pivot_slider 为父的 REVOLUTE hinge；slot_guide→slider 的 PRISMATIC 是 pivot 选择器；push_button_selector 追加一个 slider→button PRISMATIC 子件；pivot_positions 是 slot_guide 上 detent 数量的 multiplicity 轴） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 origin_anchor 母资产 + 8 fork 变体，母资产本身不列入 8 但摘要中读过） |
| read_count | 9（母资产 + 8 变体全部 model.py 全文逐节读，diff 干净） |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

样本与采纳分工：
- **P0 origin_anchor**（`rec_picturex_0611__pilers_slip_joint_pliers__001__png_730c921fd05840c19617cdf595353d1e` ← `pictureX/0611/Pilers_slip_joint_pliers/001.png`）：4-part 骨架基线——`slot_guide`（含 `_slot_track` 长条 + 1 个 `alternate_pivot` 圆盘 marker）为 root，`pivot_slider`（`pivot_shaft` Cylinder + `front_rivet_head` + `rear_rivet_head`）由 PRISMATIC `guide_to_slider` (axis +X, `[0, 0.012]`) 连；`round_member`（`_member_metal(mirrored=False, slotted=False)` + `_jaw_face` + `_grip`）经 REVOLUTE `slider_to_round_member` (axis +Z, `[-0.28, 0.04]`) 连 slider；`slotted_member`（`_member_metal(mirrored=True, slotted=True)` — 前板带 slot2D 长孔 + `_jaw_face` + `_grip`）经 REVOLUTE `slider_to_slotted_member` (axis +Z, `[-0.04, 0.28]`) 连 slider。**Slot Base：flat_serrated + sliding_rivet(2) + straight_dipped 基线**（母资产为 2 个 detent 位置）。
- **V-P1 pivot_positions=3**（`rec_0611_pilers_slip_joint_pliers_var_pivot_positions_3`，fork P0）：`PIVOT_POSITIONS=3` `PIVOT_SPACING=0.012`；`_slot_track` 长度 `(N-1)*spacing + 0.018`；for-loop 生成 N-1 个 `alternate_pivot_i` marker；PRISMATIC upper=`(N-1)*spacing`。**Slot C：3 detent 来源**。
- **V-P2 pivot_positions=5**（`rec_0611_pilers_slip_joint_pliers_var_pivot_positions_5`）：同 pattern，`N=5`。**Slot C：5 detent 来源**。
- **V-P3 pivot_positions=7**（`rec_0611_pilers_slip_joint_pliers_var_pivot_positions_7`）：同 pattern，`N=7`。**Slot C：7 detent 来源**。
- **V-J1 curved_pipe_jaw**（`rec_0611_pilers_slip_joint_pliers_var_jaw_form_curved_pipe_jaw`）：`_jaw_face` 换成 U 形 pipe-grip 凹槽（`box - cylinder cutter`）替代平面齿列，宽度更大。**Slot A：curved_pipe_jaw 来源**。
- **V-J2 broad_flat_jaw**（`rec_0611_pilers_slip_joint_pliers_var_jaw_form_broad_flat_jaw`）：`_jaw_face` polyline 加宽（back edge x 从 0.009→0.013，齿更浅），rivet head 稍大；grip 稍宽。**Slot A：broad_flat_jaw 来源**。
- **V-T1 captured_box_joint**（`rec_0611_pilers_slip_joint_pliers_var_pivot_topology_captured_box_joint`）：pivot_shaft 从 Cylinder 换成方截面 `_box_shaft` (rect 8.2×8.2)；alternate marker 也换 rect；两半 pivot hole 保持圆孔（略过盈）；part / joint 计数不变。**Slot B：captured_box_joint 来源**。
- **V-T2 push_button_selector**（`rec_0611_pilers_slip_joint_pliers_var_pivot_topology_push_button_selector`）：追加 `selector_button` part（红色 dome cap + 短 stem）+ `slider_to_button` PRISMATIC (axis -Z, `[0, 0.002]`)；pivot_slider 上追加 `button_bore` 沉孔 + `bore_bridge` 桥接。part=5 / joint=4。**Slot B：push_button_selector 来源**。
- **V-H1 flared_comfort_grip**（`rec_0611_pilers_slip_joint_pliers_var_handle_flared_comfort_grip`）：`_grip` polyline 中段外扩 flare（半宽 -0.045~-0.049），内侧加两条 finger-groove 凹凸；jaw teeth polyline 更深 V-notch。**Slot D：flared_comfort_grip 来源**。

冗余说明：8 个 fork 样本核心 4-part / 3-joint 骨架完全同构；每个 fork 只改 1 根结构轴，diff 干净。唯一改链拓扑的是 push_button_selector（+1 part +1 joint）；其余是 part-internal visual 几何 / joint 参数（PIVOT_POSITIONS=N 是同一 topology 的 multiplicity 参数化，marker 数量随 N 变但骨架不变）。

## 核心身份

一把家用手动 **slip-joint pliers**（滑动销钳）：**两片镜像锻钢半钳**，通过一个**位于 slot_guide 长孔上的可切换 pivot 销**交叉（这是本子类的关键身份——用户可将 pivot 在多个 detent 位置之间滑动/切换，从而改变颚的开合半径）。`slot_guide` 是一根薄的 dark 长条 root，承载 `slot_track` 与 N-1 个 `alternate_pivot_i` marker；`pivot_slider` 是承载 pivot 销（`pivot_shaft` + 两 rivet head）的可 PRISMATIC 滑动子件；两个 forged member（`round_member` 后板带圆 pivot 孔，`slotted_member` 前板带 elongated slot 孔）各自绕 `pivot_slider` 做 REVOLUTE 开合（相对方向相反）。

物体平躺 XY 平面（Z = 厚度方向）：颚指 +Y，手柄向 -Y 张开；rivet 在 slot_guide 上沿 +X 滑动。pivot_slider 中央（q=0）位于 `-(N-1)*spacing/2` 的世界 X，slider 移动到 `(N-1)*spacing` 到达最右 detent。

默认成熟域：真实手工具尺度（整长 y-span ~0.190-0.215 m，x-span ~0.070-0.100 m，厚 ~0.010-0.018 m）。jaw_form 形态可为 flat_serrated（六齿）/ curved_pipe_jaw（U 形 pipe-grip）/ broad_flat_jaw（宽平齿列）；pivot_topology 可为 sliding_rivet（圆柱 pin）/ captured_box_joint（方截面 pin）/ push_button_selector（追加按钮子件 +1 part / +1 joint）；pivot_positions 可为 2 / 3 / 5 / 7（marker 数与 slot 长度联动）；handle_form 可为 straight_dipped 或 flared_comfort_grip。

不该混入：**其他钳（Other_pliers 大类下的综合 / needle_nose / vise-grip / cutting）**——本类核心身份 = **可切换 pivot 位置的 slot_guide + PRISMATIC 滑动 pivot**（不允许 fixed rivet）；**剪刀 / scissors**（无 slip pivot）；**扳手 / spanner**；**镊子 / tweezers**（无 pivot）；**channel-lock / tongue-groove**（更多齿位但拓扑不同）。

## 槽位 + 候选模块表

> **建模注记**：pilers_slip_joint_pliers 的核心骨架是 4-part / 3-joint（slot_guide + slider + round + slotted），由 **Slot B (pivot_topology)** 决定链拓扑（sliding_rivet / captured_box_joint = 4-part；push_button_selector = 5-part + 1 追加 PRISMATIC）。**Slot A (jaw_form)** 是两 member 的 `_jaw_face` visual 几何切换；**Slot C (pivot_positions)** 是 slot_guide 上 alternate_pivot marker 数量的 multiplicity 参数（改 slot_track 长度 + PRISMATIC upper）；**Slot D (handle_form)** 是两 member 的 `_grip` polyline 切换。

### Slot A：jaw_form（颚形；③ 主体形态家族 / Primary Form Family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype | 结构特征 |
|---|---|---|---|---|---|---|
| flat_serrated（基线）| origin_anchor | P0 | `_jaw_face` L145-166（六齿锯齿 polyline，back edge x=0.009）| eligible if compatible | Planar Boundary Form | 六齿平锯齿颚：`_jaw_face` polyline 在 y=0.051-0.098 铺六个尖齿；宽度窄（x=0.009）|
| curved_pipe_jaw | forked_anchor | V-J1 | `_jaw_face` L146-183（box-cylinder U 槽 CSG）| eligible if compatible | Volumetric Envelope Form | U 形 pipe-grip：box 主体 - Y 轴向 cylinder cutter 形成凹槽；替代齿列，读作管夹 |
| broad_flat_jaw | forked_anchor | V-J2 | `_jaw_face` L148-166（back edge x=0.013，齿更浅）| eligible if compatible | Planar Boundary Form | 宽平齿列：`_jaw_face` polyline 加宽 back edge（0.013 vs 基线 0.009），齿浅但覆盖面广 |

> 3 candidate（达目标下限）。三者只改 `_jaw_face` 平面 polyline / CSG（flat_serrated / broad_flat_jaw 是 Planar Boundary Form 变体；curved_pipe_jaw 是 Volumetric Envelope Form），保 part tree / joint 计数一致。

### Slot B：pivot_topology（枢轴机构；② 关节 / 骨架轴，决定链拓扑）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| sliding_rivet（基线）| origin_anchor | P0 | pivot_shaft Cylinder L228-233；alternate_pivot Cylinder L218-222；guide_to_slider PRISMATIC L326-338 | eligible if compatible | 圆柱 pivot pin（`Cylinder(r=0.0052, l=0.012)`）；alternate marker 也为圆盘；4-part / 3-joint 骨架 |
| captured_box_joint | forked_anchor | V-T1 | `_box_shaft` L187-201; `_box_pivot_marker` L204-211; slider pivot_shaft L268 | eligible if compatible | 方截面 pivot shaft (`8.2×8.2 rect extrude`, 圆角 0.0008)；alternate marker 也 rect；4-part / 3-joint 骨架不变 |
| push_button_selector | forked_anchor | V-T2 | `_selector_button_cap` L187-198; button_bore L273-291; selector_button part L294-303; slider_to_button PRISMATIC L393-407 | eligible if compatible | 追加 `selector_button` part（红色 dome cap Cylinder + 短 stem）+ `slider_to_button` PRISMATIC axis -Z (`[0, 0.002]`)；slider 上追加 `button_bore` 沉孔 + `bore_bridge` 桥接 visual；5-part / 4-joint 链 |

> 3 candidate（达目标下限）。sliding_rivet / captured_box_joint 保 4-part 链、仅改 pivot_shaft 与 alternate marker 几何；push_button_selector 改链拓扑（+1 part +1 joint）。

### Slot C：pivot_positions（可选 pivot 位置数量；① multiplicity 轴）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| 2_position（基线）| origin_anchor | P0 | `_slot_track` L169-175（长 0.030）; alternate_pivot 单个 L217-222; PRISMATIC upper=0.012 L335 | eligible if compatible | slot_track 长 0.030；1 个 alternate marker；PRISMATIC upper=0.012 |
| 3_position | forked_anchor | V-P1 | `PIVOT_POSITIONS=3` L20; `_slot_track` L174-183（长 = 2*0.012+0.018=0.042）; for-loop L227-234 | eligible if compatible | slot_track 长 0.042；2 个 alternate marker；PRISMATIC upper=0.024 |
| 5_position | forked_anchor | V-P2 | 同 pattern `PIVOT_POSITIONS=5` | eligible if compatible | slot_track 长 0.066；4 个 alternate marker；PRISMATIC upper=0.048 |
| 7_position | forked_anchor | V-P3 | 同 pattern `PIVOT_POSITIONS=7` | eligible if compatible | slot_track 长 0.090；6 个 alternate marker；PRISMATIC upper=0.072 |

> 4 candidate（达目标 3-6）。N∈{2,3,5,7}，属 §8 multiplicity 轴（`count_param=pivot_positions_count`）。

### Slot D：handle_form（手柄形态；③ 骨架 + 装饰共轴）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| straight_dipped（基线）| origin_anchor | P0 | `_grip` L116-142（gentle bow, 半宽 ~0.043）| eligible if compatible | 温和外弓的浸塑柄，六段直筒 polyline |
| flared_comfort_grip | forked_anchor | V-H1 | `_grip` L117-146（中段 flare 到 0.049，内侧 finger-groove 凹凸）| eligible if compatible | 中段 flare（半宽 +0.006）+ 内侧两条 finger-groove 凹凸，读作 comfort grip |

> 2 candidate（降到 2；样本池只有 1 个 handle fork，按 SPEC_TEMPLATE 允许降到 2 说明理由）。straight_dipped / flared_comfort_grip 是 Planar Boundary Form 的两种平面轮廓；保 part / joint 计数不变。

## 槽位图（slot graph）

```
pattern: mixed（4-part parallel-children：slot_guide → PRISMATIC → pivot_slider；pivot_slider → REVOLUTE → round_member；pivot_slider → REVOLUTE → slotted_member；
                push_button_selector 追加：pivot_slider → PRISMATIC(-Z) → selector_button（5-part / 4-joint））

  ── Slot B = sliding_rivet / captured_box_joint（4-part / 3-joint 基线）──
    slot_guide (root)
      承载: slot_track（长 = (N-1)*spacing + 0.018）+ N-1 个 alternate_pivot marker（间距 spacing）
        │
        │ [PRISMATIC guide_to_slider, axis +X, origin (-(N-1)*spacing/2, 0, 0), range [0, (N-1)*spacing]]
        ↓
    pivot_slider
      承载: pivot_shaft (Cylinder r=0.0052 l=0.012 / captured_box_joint rect 8.2×8.2) + front_rivet_head + rear_rivet_head
        ├── [REVOLUTE slider_to_round_member, axis +Z, origin (0,0,0), range [-0.28, 0.04]]
        │     ↓
        │   round_member (承载: metal_body[基线，jaw+tang+pivot_plate 未 mirror]，jaw_teeth[Slot A]，blue_grip[Slot D])
        │
        └── [REVOLUTE slider_to_slotted_member, axis +Z, origin (0,0,0), range [-0.04, 0.28]]
              ↓
            slotted_member (承载: metal_body[mirrored=True + slot2D 长孔]，jaw_teeth[Slot A 镜像]，blue_grip[Slot D 镜像])

  ── Slot B = push_button_selector（5-part / 4-joint）──
    上述之外追加：
    pivot_slider  ── [PRISMATIC slider_to_button, axis -Z, origin (0, 0.012, 0.007), range [0, 0.002]] ──> selector_button
    pivot_slider 上追加 button_bore + bore_bridge visual
```

接口点位：
- **slot_guide → pivot_slider（guide_to_slider）**：mating = pivot_shaft 与 slot_track 长孔内部；joint = PRISMATIC, axis (1,0,0), origin (-(N-1)*spacing/2, 0, 0), range [0, (N-1)*spacing]。**MatingContract 省略**（captured-pin，pivot_shaft 长期贯穿 slot_track 是 captured 语义）：由 `allow_overlap(slot_guide, pivot_slider, elem_a="slot_track", elem_b="pivot_shaft", reason=...)` + `expect_within` / `expect_overlap` 表达（在 run_tests 中）。
- **pivot_slider → round_member（slider_to_round_member）**：mating = pivot_shaft 与 round_member 的圆 pivot hole；joint = REVOLUTE, axis (0,0,1), origin (0,0,0), range [-0.28, 0.04]。MatingContract 省略（captured-pin，rear_rivet_head 顶 round_member 后板 metal_body 通过 `expect_contact` 断言）。
- **pivot_slider → slotted_member（slider_to_slotted_member）**：mating = pivot_shaft 与 slotted_member 的 elongated slot 孔；joint = REVOLUTE, axis (0,0,1), origin (0,0,0), range [-0.04, 0.28]。MatingContract 省略（captured-pin，front_rivet_head 顶 slotted_member 前板通过 `expect_contact` 断言）。
- **pivot_slider → selector_button（Slot B = push_button_selector 时）**：mating = button stem 与 slider 的 button_bore；joint = PRISMATIC, axis (0,0,-1), origin (0, 0.012, 0.007), range [0, 0.002]。MatingContract 省略；由 `allow_overlap(pivot_slider, selector_button, ...)` 覆盖。
- **jaw_teeth、blue_grip、alternate_pivot、button_bore、bore_bridge**：各自宿主 part 的 inline visual（FIXED 语义，不建独立 part）。
- **互斥/可选/派生**：Slot B = push_button_selector 追加 1 part / 1 joint；其余 Slot A / C / D 与 B 正交；jaw 与 grip 在两半上通过 `mirrored=True/False` 派生。

## 每槽位 Module Emits / Interfaces

### Slot A / module flat_serrated
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 每 forged member 上一个 `jaw_teeth` mesh（`_jaw_face` 六齿锯齿 polyline extrude 0.00035）| P0 / L145-166 |
| 无独立 joint | jaw_teeth 是 member 的 inline visual | — |

### Slot A / module curved_pipe_jaw
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `jaw_teeth`：box 主体 - Y 轴向 cylinder cutter（U 槽 pipe-grip 语义）| V-J1 / L146-183 |
| 无独立 joint | — | — |

### Slot A / module broad_flat_jaw
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `jaw_teeth`：加宽 polyline（back edge x=0.013）；rivet head 略大 | V-J2 / L148-166 |
| 无独立 joint | — | — |

### Slot B / module sliding_rivet
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `pivot_slider.pivot_shaft` = Cylinder(r=0.0052, l=0.012)；`slot_guide.alternate_pivot_i` = Cylinder 圆盘 | P0 / L228-233, L217-222 |
| joints | `guide_to_slider` PRISMATIC；`slider_to_round_member` REVOLUTE；`slider_to_slotted_member` REVOLUTE | P0 / L326-365 |

### Slot B / module captured_box_joint
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `pivot_slider.pivot_shaft` = `_box_shaft` (rect 8.2×8.2 extrude, 圆角 0.0008)；`slot_guide.alternate_pivot_i` = rect marker | V-T1 / L187-211, L268 |
| joints | 同 sliding_rivet（part / joint 计数不变）| V-T1 |

### Slot B / module push_button_selector
| emits | 描述 | 来源 |
|---|---|---|
| parts | 追加 `selector_button`（`_selector_button_cap` dome cap + 短 stem，红色）| V-T2 / L186-198, L294-303 |
| visuals | `pivot_slider` 上追加 `button_bore` 沉孔 + `bore_bridge` 桥接 Cylinder（读作按钮座）| V-T2 / L273-291 |
| joints | 追加 `slider_to_button` PRISMATIC axis (0,0,-1) range [0, 0.002]（5-part / 4-joint 链）| V-T2 / L393-407 |

### Slot C / module 2_position / 3_position / 5_position / 7_position
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `slot_guide.slot_track` = `slot2D((N-1)*spacing+0.018, 0.0128, 0)`；`slot_guide.alternate_pivot_i` × (N-1) 个 | V-P1/2/3 / L174-183, L227-234 |
| joints | `guide_to_slider` PRISMATIC upper = `(N-1)*spacing`, origin.x = `-(N-1)*spacing/2` | V-P1/2/3 / L338-352 |

### Slot D / module straight_dipped
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 每 forged member 一个 `blue_grip` = `_polygon_prism(_grip_outline, 0.0076)` + edge fillet | P0 / L116-142 |

### Slot D / module flared_comfort_grip
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 中段外扩 flare + 内侧 finger-groove 凹凸 polyline extrude | V-H1 / L117-146 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| jaw_form | enum | {flat_serrated, curved_pipe_jaw, broad_flat_jaw} | flat_serrated | choice | procedural sampler | Slot A |
| pivot_topology | enum | {sliding_rivet, captured_box_joint, push_button_selector} | sliding_rivet | choice | procedural sampler；决定 4-part vs 5-part 链 | Slot B |
| pivot_positions | int (multiplicity) | {2, 3, 5, 7} | 2 | choice | procedural sampler；决定 slot_track 长度 + PRISMATIC upper | Slot C |
| handle_form | enum | {straight_dipped, flared_comfort_grip} | straight_dipped | choice | procedural sampler | Slot D |
| palette_style | enum | {steel_blue, gunmetal_red, chrome_dark_blue, black_yellow, industrial_green, brushed_steel_orange} | steel_blue | palette | **palette only，不进 slot_choice / 不改拓扑** | P0 配色 + 世界知识扩展 |
| overall_len_scale | float | [0.92, 1.10] | 1.0 | independent | 整体等比缩放；clamp 保 y-span ∈ [0.190, 0.215] | P0 整长 ~0.205 m |
| jaw_len_scale | float | [0.90, 1.08] | 1.0 | independent | 缩放 jaw_face 与 member 的 y 方向 | P0 `_scale_y factor=0.69` |
| grip_girth_scale | float | [0.92, 1.08] | 1.0 | independent | 缩放 grip 半宽 | P0 `_grip` |
| open_angle_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放两 REVOLUTE 的 upper/lower；clamp | P0 `[-0.28, 0.28]` |
| (—) | constraint | — | — | inequality | pivot_shaft 在 slot_track 内始终不越出（`(N-1)*spacing ≤ slot_track_length - 2*shaft_radius`）| captured-pin 内接 |
| (—) | constraint | — | — | inequality | jaw_form=curved_pipe_jaw 时 pipe channel z 不越出 member 厚度 | V-J1 |

连续 scale 默认独立采样 → inequality 由 `resolve_config` clamp 求解。**palette_style 只换 material rgba。**

### 7.5 编译预算 / compile budget

自报每-seed 编译预算 **~15-22 s**（依据：4-5 part、`_member_metal` 是主 CQ 成本——slot2D + polyline extrude + fillet + cut；jaw / grip 是较轻的 polyline extrude；无 loft、无 groove 循环、无重雕刻）。分档 tessellation：pivot_shaft 用 SDK `Cylinder`；polyline 部件用 CQ extrude（默认 tolerance 0.00035-0.0004）。超预算先降 tolerance 再迭代。

## Multiplicity / Copy Logic

- `count_param`: `pivot_positions_count`（Slot C）
- `N_range`: {2, 3, 5, 7}（本 4 个 candidate 是显式枚举，5★ 源支撑 3/5/7；2 由 origin 母资产支撑）
- sampling domain：权重 `[3, 3, 2, 2]`（小 N 稍频繁；weighted per §8 multiplicity 契约）
- copied object：`alternate_pivot_i` marker（Cylinder 圆盘 for sliding_rivet / sliding_rivet；rect for captured_box_joint）
- naming：`alternate_pivot_1`, `alternate_pivot_2`, ..., `alternate_pivot_{N-1}`
- placement：`x = -(N-1)*spacing/2 + i*spacing`（在 slot_guide 局部帧内，从最左 detent 起沿 +X 均匀分布）
- joint policy：无独立 joint（marker 是 slot_guide inline visual）
- source / gating：{2,3,5,7} 均已由 origin + V-P1/2/3 覆盖

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Slot B pivot_topology：sliding_rivet / captured_box_joint（4-part 链）vs push_button_selector（5-part 链 +1 PRISMATIC）；source_type=forked_anchor (V-T2) |
| └ multiplicity | 同构件 ×N | 有 | Slot C pivot_positions: N ∈ {2, 3, 5, 7}，`alternate_pivot_i` marker ×(N-1)；权重 `[3, 3, 2, 2]`；source_type=origin_anchor + forked_anchor (V-P1/2/3) |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | 基线 = 1 PRISMATIC + 2 REVOLUTE；push_button_selector 追加 1 PRISMATIC（axis -Z），关节 type 生态涵盖 PRISMATIC + REVOLUTE 两大类；source_type=forked_anchor (V-T2) |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | 有 | Slot A jaw_form：flat_serrated (Planar Boundary Form) / broad_flat_jaw (Planar Boundary Form) / curved_pipe_jaw (Volumetric Envelope Form)；Slot D handle_form：straight_dipped / flared_comfort_grip 两种 Planar Boundary Form；source_type=forked_anchor (V-J1/2, V-H1) + origin_anchor (P0) |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | Slot C alternate_pivot marker 数量与 Slot B captured_box_joint 的方形 vs 圆形 marker 差异；push_button_selector 的红色 dome cap 装饰；均为 host-conformal 且非独立 module；source_type=record_only |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | overall_len_scale [0.92,1.10]、jaw_len_scale [0.90,1.08]、grip_girth_scale [0.92,1.08]、open_angle_scale [0.85,1.15]；关节运动包络：guide_to_slider PRISMATIC axis +X open direction=upper `[0, (N-1)*0.012]`；slider_to_round REVOLUTE axis +Z `[-0.28, 0.04] × scale`；slider_to_slotted REVOLUTE axis +Z `[-0.04, 0.28] × scale`；slider_to_button PRISMATIC axis -Z `[0, 0.002]`（push_button 分支）；motion_test_plan：跑 sampled collision + targeted `ctx.pose(...)` 覆盖 open/rest/end-slide 三态 |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | palette_style 6 档：steel_blue / gunmetal_red / chrome_dark_blue / black_yellow / industrial_green / brushed_steel_orange；材质大类覆盖 metal (3 档) + rubber/vinyl (3 档) ≥ ceil(0.5×6)=3 |

**收尾自检**：本表每个"有"里列的取值，必须在 `template batch` 0-9 seed 渲染肉眼可见——3 个 jaw_form 拉得开、3 个 pivot_topology 出现（含 push_button 5-part 链）、4 个 pivot_positions 出现（2/3/5/7 detent 数）、2 个 handle_form 出现、6 个 palette 覆盖 metal / vinyl。

## 采样与覆盖审计

总组合数（离散槽）：jaw_form(3) × pivot_topology(3) × pivot_positions(4) × handle_form(2) = **72** 拓扑等价类。

理由：仅离散槽 72，覆盖成熟度足；本类 §8 有 multiplicity 轴（Slot C），已算入。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有 seed 做 deterministic procedural sampling——加权选 jaw_form / pivot_topology / pivot_positions / handle_form（flat_serrated / sliding_rivet / 2_position / straight_dipped 偏多），采连续 scale，`resolve_config` clamp。`seed=0` 不特殊。无 regression overrides（sweep 暴露特定 seed 失败再稀疏加）。
Topology target：1000-seed slot choice tuple distinct 目标 = 72（本类离散组合上界，report-only）。
Controlled local parameterization：`overall_len_scale` / `jaw_len_scale` / `grip_girth_scale` / `open_angle_scale`，全 clamp。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 顺序：jaw_form → pivot_topology → pivot_positions → handle_form → scales → palette；加权 | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | (1) 所有 slot 正交。(2) pivot_shaft 在 slot_track 内始终 captured；`(N-1)*spacing ≤ slot_track_length - 2*shaft_radius` 恒立。(3) push_button_selector 分支追加 selector_button 与 slider_to_button，其他 slot 不受影响。(4) captured-pin overlap 由 allow_overlap 覆盖。| 无 floating / collision / captured-pin origin 漂移 / member 互穿 |
| controlled local variation | 4 个 clamped scale | 不破坏 pivot origin / joint range / 类别 identity |
| regression overrides | none | 仅 sweep 暴露的失败 seed 稀疏添加 |
| random sweep | 初轮 0-35，成熟审计 0-999 | captured-pin overlap / jaw 合刃 / grip 互穿 / push_button 5-part 链装配 / N=7 detent slot 长度不越 member |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A jaw_form | 3 | yes | yes | flat_serrated / curved_pipe_jaw / broad_flat_jaw |
| B pivot_topology | 3 | yes | yes | sliding_rivet(1 PRISMATIC + 2 REVOLUTE) / captured_box_joint(rect shaft) / push_button_selector(+1 part +1 PRISMATIC) |
| C pivot_positions | 4 | yes | yes | 2 / 3 / 5 / 7 detent |
| D handle_form | 2 | yes | no | straight_dipped / flared_comfort_grip（样本池限制，降到 2）|

## Validator

- slot_choices_for_seed returns implemented module names
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating：所有 slot 正交；pivot_shaft 在 slot_track 内 captured
- optional regression overrides 初版为空
- controlled local scale 全部 clamp
- critical captured-pin overlap：`allow_overlap(slot_guide, pivot_slider, elem_a="slot_track", elem_b="pivot_shaft", reason=...)` + `allow_overlap(pivot_slider, round_member, elem_a="pivot_shaft", elem_b="metal_body", reason=...)` + `allow_overlap(pivot_slider, slotted_member, elem_a="pivot_shaft", elem_b="metal_body", reason=...)`；两个 forged member 之间存在 pivot_plate 交叉重叠（z-lap），需 `allow_overlap(round_member, slotted_member, elem_a="metal_body", elem_b="metal_body", reason="crossed pivot plates z-lap")`
- key joints：`guide_to_slider` PRISMATIC axis (1,0,0), range `[0, (N-1)*0.012]`；`slider_to_round_member` / `slider_to_slotted_member` REVOLUTE axis (0,0,1), ranges `[-0.28,0.04]` / `[-0.04,0.28]`（× open_angle_scale, clamp）；`slider_to_button` PRISMATIC axis (0,0,-1), range `[0, 0.002]`（push_button 分支）
- 开合测试：`pose slider_to_round=-0.20, slider_to_slotted=+0.20` 使 jaw 分离；`pose guide_to_slider=upper` 使 pivot_slider x 增大；push_button 分支 pose `slider_to_button=0.002` 使 button z 下降
- palette_style 只换 rgba
- 所有 `.visual(material=mats[...])` 用 `mats` dict 索引

## Reject cases

- 中央 pivot 做成 FIXED 或省略 PRISMATIC guide_to_slider（slip-joint 必须有可切换的 pivot 位置）
- pivot_shaft 未 captured 在 slot_track 内（导致 island / 漂浮）
- captured-pin allow_overlap 缺失 → 两 forged member 之间 z-lap 判 collision fail
- Slot B=push_button_selector 缺 selector_button part 或 slider_to_button PRISMATIC
- Slot C 的 alternate_pivot marker 数量 ≠ (N-1)
- Slot A=curved_pipe_jaw 的 pipe 凹槽穿透 member 厚度或 z 越界
- open pose 两 member 不真正张开
- 用 boxy 占位代替真实 jaw / grip / member polyline

## 与相邻类别的边界

- 不该混入：**Other_pliers / vise-grip / needle_nose / cutting_pliers**（本类专职 slip-joint = 可切换 pivot 位置的 PRISMATIC + 2 REVOLUTE 拓扑）
- 不该混入：**channel-lock / tongue-groove**（更多齿位 / 不同的 detent 拓扑）
- 不该混入：**scissors / shears**（无 slip pivot）
- 不该混入：**扳手 / wrench**
- 不该混入：**镊子 / tweezers**

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 首次实现；待验证 sweep-pipeline `verdict=pass` 与 corner clean |

## 模板实现备注

- 共享 helper：`_polygon_prism`（P0 已用）、`_mirror_points`、`_scale_y factor=0.69`、`_member_metal(mirrored, slotted)`、`_grip`、`_jaw_face`（Slot A 分派）、`_slot_track(length)`、`_front_rivet_head`、`_box_shaft`（B=captured_box_joint）、`_selector_button_cap`（B=push_button）
- 关键 captured-pin：所有 pivot pin captured；采 element-scoped `allow_overlap` 与 broad member↔member overlap（z-lap crossed plates）
- 主 joints 省略 MatingContract（captured-pin grandfathered）；origin 落 pivot shaft 中心真实几何
- pivot_positions=N 参数化 slot_track 长度与 PRISMATIC upper；`alternate_pivot_i` marker 循环 for i in 1..N-1

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| P0 | A/B/C/D | flat_serrated / sliding_rivet / 2_position / straight_dipped | rec_picturex_0611__pilers_slip_joint_pliers__001__png_730c921fd05840c19617cdf595353d1e | `_member_metal` L32-113, `_grip` L116-142, `_jaw_face` L145-166, `_slot_track` L169-175, `_front_rivet_head` L178-184, 3 joints L326-365 | 4-part / 3-joint 骨架 + 各 slot 基线 |
| V-P1 | C | 3_position | rec_0611_pilers_slip_joint_pliers_var_pivot_positions_3 | `PIVOT_POSITIONS`/`PIVOT_SPACING` L20-21, `_slot_track` L174-183, marker loop L227-234, PRISMATIC upper L347-352 | multiplicity 参数化模式 |
| V-P2 | C | 5_position | rec_0611_pilers_slip_joint_pliers_var_pivot_positions_5 | 同 pattern N=5 | 5 detent |
| V-P3 | C | 7_position | rec_0611_pilers_slip_joint_pliers_var_pivot_positions_7 | 同 pattern N=7 | 7 detent |
| V-J1 | A | curved_pipe_jaw | rec_0611_pilers_slip_joint_pliers_var_jaw_form_curved_pipe_jaw | `_jaw_face` L146-183（box - cylinder cutter）| pipe-grip 凹槽 |
| V-J2 | A | broad_flat_jaw | rec_0611_pilers_slip_joint_pliers_var_jaw_form_broad_flat_jaw | `_jaw_face` L148-166 加宽 back edge; grip 稍宽 | 宽平齿列 |
| V-T1 | B | captured_box_joint | rec_0611_pilers_slip_joint_pliers_var_pivot_topology_captured_box_joint | `_box_shaft` L187-201, `_box_pivot_marker` L204-211, pivot_shaft L268 | 方截面 pivot |
| V-T2 | B | push_button_selector | rec_0611_pilers_slip_joint_pliers_var_pivot_topology_push_button_selector | `_selector_button_cap` L187-198, button_bore L273-291, selector_button part L294-303, `slider_to_button` PRISMATIC L393-407 | +1 part +1 joint 按钮子件 |
| V-H1 | D | flared_comfort_grip | rec_0611_pilers_slip_joint_pliers_var_handle_flared_comfort_grip | `_grip` L117-146（flare + finger-groove）| comfort grip |
