# pilers_needle_nose_pliers — Modular Spec

> 来源小类：`pictureX/0611/Pilers_needle_nose_pliers`（articraft_data 上游小类样本池；对象身份为一把长嘴钳/needle nose pliers —— 两片对称锻钢半钳绕一颗中央 rivet 交叉，前端为细长渐缩针嘴，后段延伸为绝缘长柄）。slug = `pilers_needle_nose_pliers`。
> 上游 source map：`picture_expansion/template_source_maps/0611__Pilers_needle_nose_pliers.md`。
> **同步状态**：本 spec 引用的 10 个 5★ 样本（1 origin_anchor + 9 单轴 fork 变体）已同步进本仓库 `data/records/rec_picturex_0611__pilers_needle_nose_pliers__001__png_a5f8e5dd1f0e454abefeb7f8583c6aca/` 和 `data/records/rec_0611_pilers_needle_nose_pliers_var_*`。行号按各样本本仓库 `revisions/rev_000001/model.py` 计。
> **建模基线（重要）**：origin 母资产共享 3-part / 2-joint 骨架：`pivot_pin` (root, captured rivet) + `plier_half_0` + `plier_half_1`；两条 REVOLUTE (`pivot_to_half_0` axis (0,0,-1)、`pivot_to_half_1` axis (0,0,+1)) 分别从 pivot 到两半，`range≈[-0.025, 0.28]`。全部 fork（除 leverage_compound_link 外）都保 3-part / 2-joint 骨架。

## 元信息
| 项 | 值 |
|---|---|
| slug | `pilers_needle_nose_pliers` |
| template path | `agent/templates/pilers_needle_nose_pliers.py` |
| test path (optional) | 无（sweep-pipeline 为唯一验收） |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（pivot_pin 为根，两 forged 半镜像挂 pivot；jaw_form / jaw_module / handle 是两半上镜像应用的 part-internal 几何层；return_spring 是可选 leaf 附件 visual） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

- **P0 origin_anchor** (`rec_picturex_0611__pilers_needle_nose_pliers__001__png_a5f8e5dd1f0e454abefeb7f8583c6aca` ← `pictureX/0611/Pilers_needle_nose_pliers/001.png`)：3-part 骨架基线 —— `pivot_pin` (root，`_build_rivet` L195-214) + `plier_half_0` (+x side) + `plier_half_1` (-x side)。锻钢半 = `_build_forged_head(side, z0)` L98-144 (jaw polyline + pivot disk + shoulder + 10 fine 内向 serration notches) + `_build_dark_tang(side, z0)` L147-162 (tapered path，黑化钢柄) + `_build_grip(side, z0)` L165-178 (安全黄绝缘柄) + `_build_jaw_tip(side, z0)` L181-192 (细长针嘴末段)。两条 REVOLUTE `pivot_to_half_0` axis (0,0,-1)、`pivot_to_half_1` axis (0,0,+1)，range `[-0.025, 0.28]`。**Slot Base：straight_needle + no_extra_module + standard_grip + no_return_spring**。
- **V-JF1 extra_fine** (`rec_0611_pilers_needle_nose_pliers_var_jaw_form_extra_fine`)：`_build_jaw_tip` L181-195 更细窄末段 (半宽从 0.00245 → 0.0020，尖端极细收锥)；part / joint 计数不变。**Slot A：extra_fine 来源**。
- **V-JF2 45_bent** (`rec_0611_pilers_needle_nose_pliers_var_jaw_form_45_bent`)：`_build_jaw_tip` L181-216 在 y=0.058 处向外 45° 折 (bend_length 0.015)；part / joint 不变。**Slot A：45_bent 来源**。
- **V-JF3 half_round** (`rec_0611_pilers_needle_nose_pliers_var_jaw_form_half_round`)：`_build_jaw_tip` L181-214 换成 D 断面 (沿 Y 轴半圆柱切平内侧)；part / joint 不变。**Slot A：half_round 来源**。
- **V-JM1 side_cutter** (`rec_0611_pilers_needle_nose_pliers_var_jaw_module_side_cutter`)：`_build_jaw_tip` L181-227 在 pivot 附近加宽平磨的 side cutter section (半宽 0.0042) + 三角切槽表达刃口。**Slot B：side_cutter 来源**。
- **V-JM2 wire_looping_groove** (`rec_0611_pilers_needle_nose_pliers_var_jaw_module_wire_looping_groove`)：`_build_jaw_tip` L181-210 在末端内侧刻半圆凹槽 (r=0.0007) 用于绕线。**Slot B：wire_looping_groove 来源**。
- **V-R1 leaf_spring** (`rec_0611_pilers_needle_nose_pliers_var_return_leaf_spring`)：在每半 tang 内侧加 `_build_leaf_spring(side, z0)` L195-213 弯细带（`spring_steel` 材质），作为可选返回弹簧 visual；part 计数不变（各半新增 visual），joint 计数不变。**Slot C：leaf_spring 来源**。
- **V-H1 long_reach** (`rec_0611_pilers_needle_nose_pliers_var_handle_long_reach`)：`_build_grip` 与 `_build_jaw_tip` 均沿 -y / +y 延长 (grip 到 y=-0.169，jaw tip 到 y=0.081)；part / joint 不变。**Slot D：long_reach 来源**。
- **V-H2 guarded_insulated_grip** (`rec_0611_pilers_needle_nose_pliers_var_handle_guarded_insulated_grip`)：`_build_grip` L165-193 加 guard flange (指档凸起) + 更粗绝缘体；红色替代黄色。**Slot D：guarded_insulated_grip 来源**。
- **V-L compound_link** (`rec_0611_pilers_needle_nose_pliers_var_leverage_compound_link`)：改链 7-part 6-joint，与其它样本骨架不同 —— **本 spec 不采纳该轴**（结构爆炸；主线保持 3-part / 2-joint）。列此说明不引入。

## 核心身份

一把手动长嘴钳（needle nose pliers）：**两片镜像锻钢半钳**，绕一颗**中央 rivet**（`pivot_pin`，作为 hierarchy 根）交叉；前端是**细长渐缩针嘴**（`jaw_tip` + `forged_head`），后段延伸为**黑化钢柄 + 绝缘长柄**（`handle_tang` + `grip`）。**主用户机构 = 两半分别绕 pivot_pin 独立开合**（两条 REVOLUTE 反向 axis (0,0,-1) 与 (0,0,+1)，正 pose 打开）。物体平躺 XY 平面（Z = 厚度/pivot 轴），嘴指 +Y，柄向 -Y，rivet 在世界原点。默认成熟域：真实手工具尺度（整长 ~0.19-0.20 m，jaw 长 ~0.07 m，绝缘柄长 ~0.05 m）。

**不该混入**：切断钳 pilers_cutting_pliers（本类核心是长嘴握持而非刃口对切）；scissors / tweezers / 扳手 / 剪线钳（本类是"中央 rivet + 两镜像锻钢针嘴"）。

## 槽位 + 候选模块表

> 4 个离散 slot + palette_style（仅 ⑥ 涂装，不进 slot_choice / 不改拓扑）。

### Slot A：jaw_form（针嘴末端形态；③ 主体形态家族 / Primary Form Family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype | 结构特征 |
|---|---|---|---|---|---|---|
| straight_needle（基线）| origin_anchor | P0 | `_build_jaw_tip` L181-192 (rec_picturex_...) | eligible if compatible | Planar Boundary Form | 标准直针嘴：`jaw_tip` 从 y=0.0675 走到 y=0.071，半宽 0.00230-0.00245 m，直线渐缩收锥 |
| extra_fine | forked_anchor | V-JF1 | `_build_jaw_tip` L181-195 (rec_0611_pilers_needle_nose_pliers_var_jaw_form_extra_fine) | eligible if compatible | Planar Boundary Form | 极细针嘴：多段 taper 收到 0.0010 m 半宽，末端更尖 |
| bent_45 | forked_anchor | V-JF2 | `_build_jaw_tip` L181-216 (rec_0611_pilers_needle_nose_pliers_var_jaw_form_45_bent) | eligible if compatible | Planar Boundary Form | 45° 弯嘴：在 y=0.058 处向外 45° 折约 0.015 m，可识别 bent-nose 家族 |
| half_round | forked_anchor | V-JF3 | `_build_jaw_tip` L181-214 (rec_0611_pilers_needle_nose_pliers_var_jaw_form_half_round) | eligible if compatible | Planar Boundary Form | 半圆断面嘴：D 形横断面 (沿 Y 轴半圆柱切平内侧)，外弧 + 内平 |

> 4 candidate (达 3-6 目标)。每个只改 `_build_jaw_tip` 平面 polyline (或半圆柱切平)，保 part tree、pivot origin、forged_head/tang/grip 不变。

### Slot B：jaw_module（针嘴附加功能模块；④ 装饰 / part-internal 几何叠加）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| plain（基线）| origin_anchor | P0 | `_build_jaw_tip` L181-192 (rec_picturex_...) | eligible if compatible | 无附加模块，jaw_tip 光洁 |
| side_cutter | forked_anchor | V-JM1 | `_build_jaw_tip` L181-227 (rec_0611_pilers_needle_nose_pliers_var_jaw_module_side_cutter) | eligible if compatible | pivot 附近加宽平磨 (半宽 0.0042) + 三角内切槽 (刃口 bevel) |
| wire_looping_groove | forked_anchor | V-JM2 | `_build_jaw_tip` L181-210 (rec_0611_pilers_needle_nose_pliers_var_jaw_module_wire_looping_groove) | eligible if compatible | jaw_tip 末段内侧刻半圆凹槽 (r=0.0007) 表达绕线通道 |

> 3 candidate。三者仅改 `_build_jaw_tip` polyline 局部（加宽 / 刻槽），保 part / joint 不变。可与任一 jaw_form 正交叠加（叠加时以 module 为主）。

### Slot C：return_spring（复位弹簧附件；② 关节附属子件 visual）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| none（基线）| origin_anchor | P0 | (P0 无 leaf_spring visual) | eligible if compatible | 两半 tang 内侧无附件 |
| leaf_spring | forked_anchor | V-R1 | `_build_leaf_spring` L195-213 (rec_0611_pilers_needle_nose_pliers_var_return_leaf_spring) | eligible if compatible | 两半 tang 内侧各加一段弯细带 (`spring_steel`)，从 y≈-0.015 走到 y≈-0.066，模拟压合复位弹簧 |

> 2 candidate（达 ≥2 下限）。leaf_spring 只在每半 part 内追加 visual，不新增 part / joint。

### Slot D：handle_form（长柄形态与包覆；⑤ 尺寸/行程 + ⑥ 装饰共轴）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| standard（基线）| origin_anchor | P0 | `_build_grip` L165-178 (rec_picturex_...) | eligible if compatible | 直筒绝缘长柄 (min_y=-0.124 m) + 黑化钢内 tang |
| long_reach | forked_anchor | V-H1 | `_build_grip` L165-184 + `_build_jaw_tip` L187-199 (rec_0611_pilers_needle_nose_pliers_var_handle_long_reach) | eligible if compatible | grip 与 jaw_tip 双双拉长（grip 至 y=-0.169，jaw_tip 至 y=0.081）；整长 ~0.25 m |
| guarded_insulated_grip | forked_anchor | V-H2 | `_build_grip` L165-193 (rec_0611_pilers_needle_nose_pliers_var_handle_guarded_insulated_grip) | eligible if compatible | 加指档 flange (pivot 侧 flare) + 加粗红色绝缘体 (半宽 0.0075-0.0093 m) |

> 3 candidate。三者改 `_build_grip` polyline（含长度、指档），仅 long_reach 同步拉长 `_build_jaw_tip`；part / joint 计数不变。

## 槽位图（slot graph）

```
pattern: mixed（3-part pivot 链，pivot_pin 为根，两 forged 半镜像挂 pivot）

  pivot_pin (root; captured rivet visual)
      ├──[REVOLUTE pivot_to_half_0, axis (0,0,-1), origin (0,0,0)]──> plier_half_0
      │      承载: forged_head[A/B]·handle_tang·grip[D]·jaw_tip[A/B]·(leaf_spring[C])
      └──[REVOLUTE pivot_to_half_1, axis (0,0,+1), origin (0,0,0)]──> plier_half_1
             承载: forged_head[A/B 镜像]·handle_tang·grip[D 镜像]·jaw_tip[A/B 镜像]·(leaf_spring[C])
```

接口点位（每条连接）：
- **pivot_pin → plier_half_0 / pivot_pin → plier_half_1**：mating = 中央 rivet 轴（`origin=(0,0,0)`），axis 反向 `(0,0,-1)` / `(0,0,+1)`，range `[-0.025, 0.28] × open_angle_scale`；rivet 是 pivot_pin 的 inline visual (`Cylinder`)，两 forged head 的 z-lap 由 `expect_contact(pivot_pin, plier_half_i, elem_a="rivet", elem_b="forged_head")` 强制接触，配 broad `allow_overlap(pivot_pin, plier_half_i)` reason="captured rivet through hub"。**MatingContract 省略（captured pin grandfathered）**。
- **两半之间 z-lap 与嘴间隙**：`allow_overlap(plier_half_0, plier_half_1)` reason="two forged halves overlap at the pivot hub lap"；`expect_gap(plier_half_0, plier_half_1, axis="x", min_gap=0.0015, max_gap=0.0035, elem_a="jaw_tip", elem_b="jaw_tip")` 表达 rest pose 针嘴微开。
- **cutting_edge / groove / leaf_spring** 都是 part-internal visual（FIXED 语义）。

## 每槽位 Module Emits / Interfaces

### Slot A / straight_needle
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `jaw_tip`（brushed_steel，直针嘴 polyline，末端半宽 0.00245→0.00230 m）| P0 L181-192 |

### Slot A / extra_fine
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `jaw_tip`（brushed_steel，多段 taper 到 0.0010 m 半宽）| V-JF1 L181-195 |

### Slot A / bent_45
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `jaw_tip`（brushed_steel，y≥0.058 后向 +/-x 折 45° 长度 0.015 m）| V-JF2 L181-216 |
| downstream 断言 | jaw_tip world AABB x 范围较基线更宽（bent 外扩） | V-JF2 |

### Slot A / half_round
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `jaw_tip`（brushed_steel，D 断面：沿 Y 轴半圆柱切平内侧 x） | V-JF3 L181-214 |

### Slot B / plain
| emits | 无附加 | P0 |

### Slot B / side_cutter
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `jaw_tip` 包含 pivot 端加宽 side_cutter section + 三角刃槽 | V-JM1 L181-227 |
| downstream 断言 | jaw_tip AABB 在 y≈0.006-0.010 存在宽度 ≥ 0.003 m 的加宽区 | V-JM1 |

### Slot B / wire_looping_groove
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `jaw_tip` 末段内侧半圆凹槽 (r=0.0007 m) | V-JM2 L181-210 |

### Slot C / none
| emits | 无附加 | P0 |

### Slot C / leaf_spring
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 每半 part 追加 `leaf_spring` visual (`spring_steel`；tapered strip，y 从 -0.015 到 -0.066，半宽 0.0015-0.0022 m，厚度 0.0005 m) | V-R1 L195-213 |
| 配色 | 新增材质 `spring_steel` (rgba ≈ (0.82,0.83,0.82,1.0)) | V-R1 |

### Slot D / standard
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `grip`（safety_yellow, tapered path min_y=-0.124）| P0 L165-178 |

### Slot D / long_reach
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `grip`（safety_yellow, min_y=-0.169）+ `jaw_tip` 拉长到 y=0.081 | V-H1 L165-199 |
| downstream 断言 | grip min_y < -0.160；jaw_tip max_y > 0.078 | V-H1 |

### Slot D / guarded_insulated_grip
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `grip`（insulated_red，含 guard flange + 加粗身，min_y=-0.124） | V-H2 L165-193 |
| downstream 断言 | grip 中段 (y≈-0.038) 半宽 > 0.008 m（flange） | V-H2 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| jaw_form | enum | {straight_needle, extra_fine, bent_45, half_round} | straight_needle | choice | procedural sampler | Slot A |
| jaw_module | enum | {plain, side_cutter, wire_looping_groove} | plain | choice | sampler | Slot B |
| return_spring | enum | {none, leaf_spring} | none | choice | sampler | Slot C |
| handle_form | enum | {standard, long_reach, guarded_insulated_grip} | standard | choice | sampler | Slot D |
| palette_style | enum | {steel_yellow, matte_black_yellow, chrome_natural, gunmetal_orange, polished_red} | steel_yellow | palette | **palette only**；按 seed 采样，只换 material rgba | P0 + 世界知识扩展 |
| overall_len_scale | float | [0.92, 1.10] | 1.0 | independent | 等比 clamp | P0 整长 ~0.195 m |
| jaw_len_scale | float | [0.92, 1.08] | 1.0 | independent | 缩放 jaw_tip y 方向 | P0 |
| grip_girth_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 grip 半宽 | P0 |
| open_angle_scale | float | [0.80, 1.20] | 1.0 | independent | 缩放 pivot revolute upper (0.28) 与 lower (-0.025) | P0 L372-393 |
| (—) | constraint | — | — | inequality | pivot origin 落 (0,0,0)±0.001；两 forged head z-lap 恒接触；rivet 头部咬合两半 | 接口 |

## 视觉多样性 6 轴考察

| 轴 | 判定 | 有/无 | 说明 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 无（本 spec 明确不采 compound_link 分支；核心骨架 3-part / 2-joint 固定） | leverage 变体不在本 spec 范围 |
| └ multiplicity | 同构件 ×N | 无 | source map 明示 no strong count axis |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有（Slot C leaf_spring 视为 part-internal，②弱化到装饰）；② 弱轴 | 主 pivot 两条 REVOLUTE 固定 |
| ③ 主体形态家族 | 换核心 part 形态原型 | 有 | Slot A jaw_form 4 candidate |
| ④ 表面装饰 | 叠加表面细节 | 有 | Slot B jaw_module 3 candidate (side_cutter/wire_looping_groove 是 host-conformal 装饰级几何叠加) + Slot C leaf_spring |
| ⑤ 尺寸/行程 | 只连续改尺寸 | 有 | Slot D handle_form (long_reach/guard) + overall_len_scale 等 4 个连续 scale |
| ⑥ 涂装 | 只改材质 | 有 | palette_style 5 档 |

## 采样与覆盖审计

总组合数（离散槽）：jaw_form(4) × jaw_module(3) × return_spring(2) × handle_form(3) = **72** distinct 拓扑等价类。此为 report-only；本类样本词汇表限制自然上限。

seed_domain_policy：procedural_first
Procedural Sampling：`config_from_seed(seed)` 加权选各 slot（基线偏多），采连续 scale，`resolve_config` clamp。

| slot | candidate_count | 是否 ≥2 |
|---|---:|---|
| A jaw_form | 4 | yes |
| B jaw_module | 3 | yes |
| C return_spring | 2 | yes |
| D handle_form | 3 | yes |

## Validator

- slot_choices_for_seed 返回 (jaw_form, jaw_module, return_spring, handle_form)
- config_from_seed deterministic
- pivot origin 恒钉 (0,0,0)；两 forged head 与 rivet 有 `expect_contact`；两半 z-lap broad `allow_overlap`
- 两条 REVOLUTE axis 反向 (`(0,0,-1)` 和 `(0,0,+1)`)，range 依 open_angle_scale
- pose 每条 pivot 到 upper 应使对应 half 的 `jaw_tip` 中心沿正/负 x 移动 ≥ 0.008 m，另一半不动
- palette_style 只换 material rgba
- 所有 `.visual(material=mats[...])` 用 `mats` dict 索引

## Reject cases

- 把中央 pivot 做成 FIXED 或省略
- pivot origin 漂浮 > 0.002 m
- 两条 REVOLUTE 未反向（长嘴钳两半应独立朝相反方向张开）
- jaw_form=bent_45 未真正 bent（jaw_tip AABB x 范围未加宽）
- jaw_module=side_cutter 未加宽（pivot 端半宽 ≤ 0.0025）
- handle_form=long_reach 未真正拉长（grip min_y > -0.150）
- palette_style 混进 slot_choice

## 与相邻类别的边界

- 不该混入：pilers_cutting_pliers（本类无 cutting_edge 剪刃薄片；本类核心是长嘴握持）
- 不该混入：scissors / tweezers / 扳手 / 剪线钳
- 0611 大类内：区别于其他 pilers 小类（各类核心颚形不同）

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 |
|---|---|---|---|---|
| P0 | A/B/C/D | straight_needle / plain / none / standard | rec_picturex_0611__pilers_needle_nose_pliers__001__png_a5f8e5dd1f0e454abefeb7f8583c6aca | `_build_forged_head` L98-144, `_build_dark_tang` L147-162, `_build_grip` L165-178, `_build_jaw_tip` L181-192, `_build_rivet` L195-214, pivot joints L365-394 |
| V-JF1 | A | extra_fine | rec_0611_pilers_needle_nose_pliers_var_jaw_form_extra_fine | `_build_jaw_tip` L181-195 |
| V-JF2 | A | bent_45 | rec_0611_pilers_needle_nose_pliers_var_jaw_form_45_bent | `_build_jaw_tip` L181-216 |
| V-JF3 | A | half_round | rec_0611_pilers_needle_nose_pliers_var_jaw_form_half_round | `_build_jaw_tip` L181-214 |
| V-JM1 | B | side_cutter | rec_0611_pilers_needle_nose_pliers_var_jaw_module_side_cutter | `_build_jaw_tip` L181-227 |
| V-JM2 | B | wire_looping_groove | rec_0611_pilers_needle_nose_pliers_var_jaw_module_wire_looping_groove | `_build_jaw_tip` L181-210 |
| V-R1 | C | leaf_spring | rec_0611_pilers_needle_nose_pliers_var_return_leaf_spring | `_build_leaf_spring` L195-213 |
| V-H1 | D | long_reach | rec_0611_pilers_needle_nose_pliers_var_handle_long_reach | `_build_grip` L169-184, `_build_jaw_tip` L187-199 |
| V-H2 | D | guarded_insulated_grip | rec_0611_pilers_needle_nose_pliers_var_handle_guarded_insulated_grip | `_build_grip` L165-193 |
