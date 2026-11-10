# pilers_linesman_pliers — Modular Spec

> Source subcategory: `pictureX/0611/Pilers_linesman_pliers` (母资产 001.png，标准 linesman 电工钳：两片对称锻钢半钳绕中央 rivet 交叉，颚身兼具钳口 + 内侧剪切刃 + 前部锯齿夹持面 + 内部 crimper 空间). Slug: `pilers_linesman_pliers`.
> Upstream source map: `picture_expansion/template_source_maps/0611__Pilers_linesman_pliers.md`.
> **同步状态**：9 fork + 1 origin 已入库到本仓库 `data/records/rec_0611_pilers_linesman_pliers_*/revisions/rev_000001/model.py`，rating=5。
> **建模基线**：3-part / 2-joint 骨架：`pivot_pin` (root) + `handle_0` + `handle_1`；`pivot_to_handle_0` REVOLUTE (pivot→handle_0, axis +Z, lower<0<upper) + `pivot_to_handle_1` REVOLUTE (pivot→handle_1, axis +Z, lower<0<upper)。仅 `leverage=compound_link` 变体改链拓扑，追加 `link_0` + `link_1` 中间 part 与两条 `link_i_to_handle_i` REVOLUTE → 5-part / 4-joint 链。

## 元信息
| 项 | 值 |
|---|---|
| slug | `pilers_linesman_pliers` |
| template path | `agent/templates/pilers_linesman_pliers.py` |
| test path | 无（sweep-pipeline 为唯一验收） |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（3-part pivot 链 + 可选 4-part 追加 link；jaw / handle 在两半上镜像 part-internal 几何层；spring 为 pivot_pin 上的可选 visual） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10（1 origin_anchor + 9 fork）|
| read_count | 10 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

样本与采纳分工：
- **P0 origin_anchor**（`rec_picturex_0611__pilers_linesman_pliers__001__png_6e9299cc363b4f9a93a12472b974811f`）：3-part 骨架基线 `pivot_pin` + `handle_0` + `handle_1`；`_make_forged_half` L44-116（tang+boss+jaw+八齿）+ `_make_grip` L119-138 + `_make_grip_collar` L141-153 + `_make_grip_highlight` L156-170 + `_make_jaw_bevel` L173-185 + `_make_cutting_edge` L188-198 + `_make_serrated_insert` L201-210 + `_make_pivot_pin` L213-232；`pivot_to_handle_0/1` L395-422。**Slot Base：tapered_serrated_jaw + straight_dipped_handle + fixed_rivet + no_spring 基线**。
- **V-JAW1 broad_square_jaw** (`rec_0611_pilers_linesman_pliers_var_jaw_module_broad_square_jaw`)：`_make_jaw_bevel` polyline L173-186（更宽方形 bevel，thickness 0.0012 vs 0.0008），断言 `jaw_bevel width >= 0.014`（L618-627）。**Slot A：broad_square_jaw 来源**。
- **V-JAW2 fish_tape_channel** (`rec_0611_pilers_linesman_pliers_var_jaw_module_fish_tape_channel`)：追加 `_make_fish_tape_channel` L200-215 vertical channel visual 贴颚内面。**Slot A：fish_tape_channel 来源**。
- **V-JAW3 crimper_cavity** (`rec_0611_pilers_linesman_pliers_var_jaw_module_crimper_cavity`)：追加 `_make_crimper_cavity` L195-218 半圆凹面 visual。**Slot A：crimper_cavity 来源**。
- **V-JAW4 cable_pulling_groove** (`rec_0611_pilers_linesman_pliers_var_jaw_module_cable_pulling_groove`)：追加 `_make_cable_groove` L190-212 V 形沟 visual。**Slot A：cable_pulling_groove 来源**。
- **V-L1 compound_link** (`rec_0611_pilers_linesman_pliers_var_leverage_compound_link`)：追加 `_make_link_bar` L239-291 + `link_0` / `link_1` parts + `pivot_to_link_{i}` + `link_{i}_to_handle_{i}` 四条 REVOLUTE (L513-577)；LINK_OFFSET_X=0.004, LINK_OFFSET_Y=-0.006；5-part / 4-joint。**Slot B：compound_link 来源**。
- **V-L2 offset_high_leverage_pivot** (`rec_0611_pilers_linesman_pliers_var_leverage_offset_high_leverage_pivot`)：`_make_pivot_pin` L218-243（加装 washer / larger caps）；part / joint 计数不变。**Slot B：offset_pivot 来源**。
- **V-R captured_spring** (`rec_0611_pilers_linesman_pliers_var_return_captured_spring`)：追加 `_make_captured_spring` helical torsion 线圈 visual 挂在 `pivot_pin` 上；追加 `_make_spring_anchor_slot` 每半矩形凹槽 visual；part / joint 计数不变。**Slot C：captured_spring 来源**。
- **V-H1 long_handle** (`rec_0611_pilers_linesman_pliers_var_handle_long_handle`)：`_make_grip` polyline L119-140 拉长（min_y 更负）；`_make_forged_half` tang polyline 同步拉长；part / joint 计数不变。**Slot D：long_handle 来源**。
- **V-H2 guarded_insulated_grip** (`rec_0611_pilers_linesman_pliers_var_handle_guarded_insulated_grip`)：`_make_grip` polyline 加护手指档 flare；part / joint 计数不变。**Slot D：guarded_insulated_grip 来源**。

冗余说明：10 个样本核心骨架高度冗余（3-part + 2 REVOLUTE），diff 干净。仅 compound_link 改拓扑；其余仅调 jaw_bevel / 追加 jaw feature visual / 调 grip polyline / 追加 spring visual。

## 核心身份

一把手动 linesman 电工钳：**两片对称锻钢半钳** 绕中央 rivet **交叉**，颚身兼具钳口 + 内侧薄剪切刃 (`cutting_edge`) + 前部 `serrated_face` 锯齿夹持面 + 可选专用 jaw 特征 (fish tape / crimper / groove)；柄部为长橡胶浸塑手柄。主用户机构 = 两半绕中央 rivet 相对开合 (REVOLUTE，轴 +Z)；合柄 = 合刃 / 合齿。**pivot_pin 为独立 root part**（不是内嵌 rivet cylinder），两 handle 各有独立 REVOLUTE 挂到 pivot_pin。

物体平躺 XY 平面 (Z = 厚度)：颚指 +Y，手柄向 -Y 延伸；rivet 在世界原点 (0,0,0)。handle_0 为 -x 半（handle_sign=-1, jaw_sign=+1），handle_1 为 +x 半。**Slot B=compound_link 特例**：pivot 与 handle 之间夹一 `link_i` 中间 part（两 pivot 相距 LINK_OFFSET~7 mm），从 3-part / 2-joint 变 5-part / 4-joint。

默认成熟域：真实电工钳尺度（整长 ~0.22 m，颚长 ~0.055 m，柄长 ~0.13 m）。

不该混入：**cutting_pliers**（专切断，颚较窄短，无大 serrated_face），**needle_nose**（细长尖嘴），**locking / vise-grip**（有锁定机构），**scissors**（无中央锻钢咬颚 + 手柄剪指环），**扳手 / 镊子 / 订书机**。

## 槽位 + 候选模块表

> **建模注记**：Slot B (leverage_mechanism) 决定链拓扑（fixed_rivet / offset_pivot = 3-part 链；compound_link = 5-part 链）。Slot A (jaw_module) 是两半上镜像应用的 part-internal 几何层（追加 jaw feature visual 或改 jaw_bevel）。Slot C (return_spring) 是 pivot_pin 上可选 spring visual + 两半 spring_slot 凹槽 visual。Slot D (handle_form) 是 grip polyline 家族切换。

### Slot A：jaw_module（颚形态 / feature；③ 主体形态家族 / Primary Form Family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype | 结构特征 |
|---|---|---|---|---|---|---|
| tapered_serrated（基线）| origin_anchor | P0 | `_make_jaw_bevel` L173-185, `_make_cutting_edge` L188-198, `_make_serrated_insert` L201-210 | eligible if compatible | Planar Boundary Form | 锥形基线：窄 jaw_bevel + 前部 serrated_face 锯齿夹持面 + 内侧薄 cutting_edge |
| broad_square_jaw | forked_anchor | V-JAW1 | `_make_jaw_bevel` L173-186（更宽方形 polyline, thickness 0.0012）| eligible if compatible | Planar Boundary Form | 宽方形 jaw_bevel（半宽增至 ~0.02 m，断言 width ≥ 0.014）|
| fish_tape_channel | forked_anchor | V-JAW2 | `_make_fish_tape_channel` L200-215 | eligible if compatible | Planar Boundary Form | 追加垂直 fish_tape 拉线通道 visual 贴颚内侧 |
| crimper_cavity | forked_anchor | V-JAW3 | `_make_crimper_cavity` L195-218 | eligible if compatible | Planar Boundary Form | 追加半圆压接凹槽 visual 位于颚中段内侧 |
| cable_pulling_groove | forked_anchor | V-JAW4 | `_make_cable_groove` L190-212 | eligible if compatible | Planar Boundary Form | 追加 V 形拉线沟 visual 位于颚中段 |

> 5 candidate（达 3-6 目标）。除 broad_square_jaw 改 jaw_bevel polyline 外，其他三 fork 是追加一个专用 feature visual 到每半 jaw 内侧。part/joint 计数不变。

### Slot B：leverage_mechanism（枢轴 / 杠杆机构；② 关节 / 骨架轴）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| fixed_rivet（基线）| origin_anchor | P0 | `_make_pivot_pin` L213-232 + `pivot_to_handle_0/1` L395-422 | eligible if compatible | 3-part 链 `pivot_pin` + `handle_0` + `handle_1`；单缩短 pivot_pin cylinder (shaft L 0.0136 m, 双 back/front cap r 0.0108 m) |
| offset_pivot | forked_anchor | V-L2 | `_make_pivot_pin` L218-243（加宽 caps 视觉）| eligible if compatible | 3-part 链不变；pivot_pin visual 用更长 shaft + 更大 caps（视觉 offset high-leverage） |
| compound_link | forked_anchor | V-L1 | `_make_link_bar` L239-291, `link_0/1` parts L447-475, 四 REVOLUTE L516-577 | eligible if compatible | 5-part 链 `pivot_pin` + `link_0` + `link_1` + `handle_0` + `handle_1`；追加 4 条 REVOLUTE 中的两条 (`pivot_to_link_i`) 替换基线两条 `pivot_to_handle_i`，再加两条 `link_i_to_handle_i` 在 secondary pivot 处 |

> 3 candidate。fixed_rivet / offset_pivot 保 3-part 链；compound_link 改拓扑。

### Slot C：return_spring（复位弹簧；④ / ② 追加 visual + 附属子件几何）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| no_spring（基线）| origin_anchor | P0 | — | eligible if compatible | 母图无可见弹簧，pivot_pin 仅 shaft + caps |
| captured_spring | forked_anchor | V-R | `_make_captured_spring` L237-282, `_make_spring_anchor_slot` L283-298 | eligible if compatible | pivot_pin 上追加螺旋 torsion 弹簧 visual + 每半 forged_body 内追加矩形 spring_anchor_slot visual；part / joint 计数不变 |

> 2 candidate（达 ≥2 门限）。captured_spring 完全为 visual 追加，不改 part / joint。

### Slot D：handle_form（手柄形态；① 骨架 + 装饰共轴）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| straight_dipped（基线）| origin_anchor | P0 | `_make_grip` L119-138 (min_y -0.159) | eligible if compatible | 标准直筒橡胶浸塑柄 + collar 环 + grip_highlight 沿棱 |
| long_handle | forked_anchor | V-H1 | `_make_grip` L119-140（min_y 更负 ≤ -0.170）| eligible if compatible | 拉长版直柄，grip min_y 更远 |
| guarded_insulated_grip | forked_anchor | V-H2 | `_make_grip` L119-140（中段 flare）| eligible if compatible | 中段加护手指档 flare（半宽 +0.003 m）|

> 3 candidate（达 3-6 目标）。三者改 grip polyline，保 part / joint 计数与 collar/highlight 层不变。

## 槽位图（slot graph）

```
pattern: mixed

  ── Slot B = fixed_rivet / offset_pivot（3-part 链，基线）──
    pivot_pin (root)
       承载: pivot_pin cylinder + caps + 可选 captured_spring[C]
       │
       ├──[REVOLUTE pivot_to_handle_0, axis +Z, origin (0,0,0)]──> handle_0
       │      承载: forged_body(jaw+tang+boss)·jaw_bevel[A]·cutting_edge·serrated_face·可选 jaw_feature[A]·grip_shell[D]·grip_collar·grip_ridge·可选 spring_anchor_slot[C]
       └──[REVOLUTE pivot_to_handle_1, axis +Z, origin (0,0,0)]──> handle_1
              (同上镜像)

  ── Slot B = compound_link（5-part 链）──
    pivot_pin (root)
       │
       ├──[REVOLUTE pivot_to_link_0]──> link_0 ──[REVOLUTE link_0_to_handle_0, origin (-LINK_OFFSET_X, LINK_OFFSET_Y, 0)]──> handle_0
       └──[REVOLUTE pivot_to_link_1]──> link_1 ──[REVOLUTE link_1_to_handle_1, origin (LINK_OFFSET_X, LINK_OFFSET_Y, 0)]──> handle_1
```

接口点位：
- **pivot_pin → handle_{0,1}（fixed_rivet / offset_pivot）**：origin=(0,0,0)，REVOLUTE axis (0,0,+1)，range handle_0 lower<0<upper, handle_1 lower<0<upper（symmetric）。**MatingContract 省略（grandfathered captured-pin）**：pivot_pin cylinder 与 forged_body 的 boss z-lap 由 `expect_contact` 强制接触，配 broad `allow_overlap(pivot_pin, handle_i)` reason。
- **pivot_pin → link_{0,1}（compound_link 分支）**：origin=(0,0,0)，REVOLUTE，同上 captured-pin 约定。
- **link_i → handle_i（compound_link 分支）**：origin=(∓LINK_OFFSET_X, LINK_OFFSET_Y, 0)，REVOLUTE captured。
- **captured_spring / jaw features / grip_collar / grip_highlight / cutting_edge / serrated_face / spring_anchor_slot**：均为父 part 内的 inline visual（FIXED 语义，不建独立装饰 part）。
- **互斥/可选/派生**：Slot B 决定 3-part vs 5-part 链（互斥）；Slot A/C/D 与 B 正交（任一 leverage 可叠任一 jaw / return / handle）；handle_0 = handle_1 `mirror("YZ")` 派生（两半用 handle_sign ±1 参数化）。

## 每槽位 Module Emits / Interfaces

### Slot A / module tapered_serrated
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `jaw_bevel` (窄 tapered), `cutting_edge`, `serrated_face` | P0 L173-210 |

### Slot A / module broad_square_jaw
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 宽方形 `jaw_bevel`（thickness 0.0012 m，width ≥ 0.014 m），其余同基线 | V-JAW1 L173-186 |

### Slot A / module fish_tape_channel
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 基线三 jaw visual + 追加 `fish_tape_channel` 竖直 slot visual | V-JAW2 L200-215 |

### Slot A / module crimper_cavity
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 基线 + 追加 `crimper_cavity` 半圆凹 visual | V-JAW3 L195-218 |

### Slot A / module cable_pulling_groove
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 基线 + 追加 `cable_groove` V 形沟 visual | V-JAW4 L190-212 |

### Slot B / module fixed_rivet
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pivot_pin` root part | P0 |
| joints | `pivot_to_handle_0/1` REVOLUTE axis +Z | P0 L395-422 |

### Slot B / module offset_pivot
| emits | 描述 | 来源 |
|---|---|---|
| parts | 同 fixed_rivet | V-L2 |
| visuals | `pivot_pin` 加长 shaft + 更大 caps | V-L2 L218-243 |
| joints | 同 fixed_rivet | 同 |

### Slot B / module compound_link
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pivot_pin` + `link_0` + `link_1` + `handle_0` + `handle_1` (5-part) | V-L1 |
| joints | `pivot_to_link_{0,1}` + `link_{0,1}_to_handle_{0,1}` (4 REVOLUTE) | V-L1 L516-577 |

### Slot C / module no_spring
| emits | 无 | — |

### Slot C / module captured_spring
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `captured_spring`（pivot_pin 上螺旋 tube visual）+ 每半追加 `spring_anchor_slot` 矩形凹 visual | V-R L237-298 |

### Slot D / module straight_dipped
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `grip_shell` + `grip_collar` + `grip_ridge` | P0 L119-170 |

### Slot D / module long_handle
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 拉长版 `grip_shell` (min_y 更负) | V-H1 L119-140 |

### Slot D / module guarded_insulated_grip
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 带指档 flare 的 `grip_shell` | V-H2 L119-140 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| jaw_module | enum | {tapered_serrated, broad_square_jaw, fish_tape_channel, crimper_cavity, cable_pulling_groove} | tapered_serrated | choice | procedural sampler | Slot A |
| leverage_mechanism | enum | {fixed_rivet, offset_pivot, compound_link} | fixed_rivet | choice | sampler；决定 3-part vs 5-part | Slot B |
| return_spring | enum | {no_spring, captured_spring} | no_spring | choice | sampler | Slot C |
| handle_form | enum | {straight_dipped, long_handle, guarded_insulated_grip} | straight_dipped | choice | sampler | Slot D |
| palette_style | enum | {steel_black_blue, gunmetal_red, chrome_natural, black_yellow, olive_orange, polished_silver} | steel_black_blue | palette | palette only；按 seed 采样；不进 slot_choice / 不改拓扑 | P0 配色 + 世界知识扩展 |
| overall_len_scale | float | [0.92, 1.10] | 1.0 | independent | 整体等比 y 方向缩放 | P0 |
| grip_girth_scale | float | [0.92, 1.08] | 1.0 | independent | grip 半宽缩放 | P0 |
| open_angle_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放主 pivot 关节 upper/lower | P0 |
| (—) | constraint | — | — | inequality | pivot origin 恒落 (0,0,0)±0.002 m | 接口 |
| (—) | constraint | — | — | inequality | jaw 半宽保守以免 rest 互穿 | 接口 |

palette_style 只换 material rgba，绝不进 slot_choice。

### 7.5 编译预算 / compile budget

自报 **~8-14 s / seed**（依据：3-5 part、6-9 visual per part、`_profile_solid` polyline extrude 是主 CQ 成本；无重布尔雕刻）。torsion spring tube 用 `tube_from_spline_points(samples_per_segment=14, radial_segments=14)`。

## Multiplicity / Copy Logic

- 无强复制轴（source map 声明 `count_param: no strong repeated-part axis planned`）。link 与 handle 各 2 份是镜像对称，不作 count 参数暴露。

## 视觉多样性 6 轴考察

| 轴 | 判断 | 有/无 | 值 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Slot B leverage_mechanism：fixed_rivet / offset_pivot (3-part) vs compound_link (5-part +2 link parts + 2 REVOLUTE)；source_type=forked_anchor (V-L1) |
| └ multiplicity | 同构件 ×N | 无 | 无强多重性轴 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | 全部 REVOLUTE 绕 +Z；compound_link 引入二级 REVOLUTE 依赖轴；source_type=forked_anchor (V-L1) |
| ③ 主体形态家族 | 换核心 part 可识别几何形态原型 | 有 | Slot A jaw_module 5 候选（tapered/broad/fish/crimper/groove），改 jaw_bevel polyline 或追加 jaw feature visual；source_type=forked_anchor (V-JAW1/2/3/4) + origin_anchor (P0) |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 | Slot C return_spring 的 captured torsion 弹簧 + 两半 spring_anchor_slot 凹槽；grip_collar/grip_ridge 层为 host-conformal；source_type=forked_anchor (V-R) + record_only |
| ⑤ 尺寸/行程 | 只连续改尺寸 | 有 | overall_len_scale [0.92,1.10]、grip_girth_scale [0.92,1.08]、open_angle_scale [0.85,1.15]；关节运动包络：pivot_to_handle_i 轴 +Z，range 依 open_angle_scale 缩放；无 continuous 关节 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | palette_style 6 档：steel_black_blue / gunmetal_red / chrome_natural / black_yellow / olive_orange / polished_silver；材质大类覆盖 metal (forged/edge/polished) + rubber (grip / collar) + accent (highlight) |

## 采样与覆盖审计

总组合数（离散槽）：jaw_module(5) × leverage_mechanism(3) × return_spring(2) × handle_form(3) = **90** distinct 拓扑等价类。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 加权 deterministic 采样 5 slot 值 + 3 scale + palette。`seed=0` 不特殊。

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| A jaw_module | 5 | yes | yes | tapered/broad/fish/crimper/groove |
| B leverage_mechanism | 3 | yes | yes | fixed/offset/compound |
| C return_spring | 2 | yes | no | no_spring/captured_spring；来源池仅两态 |
| D handle_form | 3 | yes | yes | straight/long/guarded |

## Validator

- slot_choices_for_seed returns implemented module names
- config_from_seed deterministic procedural
- pivot origin 恒钉 (0,0,0)；两 handle REVOLUTE 各有 lower<0<upper
- compound_link 分支：5 parts + 4 REVOLUTE，link_i 挂在 pivot_pin，handle_i 挂在 link_i；secondary pivot origin=(∓LINK_OFFSET_X, LINK_OFFSET_Y, 0)
- broad_square_jaw 断言 `jaw_bevel` width ≥ 0.014
- long_handle 断言 grip min_y ≤ -0.165 (scale 后)
- palette_style 只换 material rgba
- 所有 `.visual(material=mats[...])` 用 mats dict

## Reject cases

- pivot origin 不落 (0,0,0) 真实几何 → 漂浮
- REVOLUTE 用 FIXED 或缺 lower<0<upper
- compound_link 分支缺 link_i part 或缺 link_i_to_handle_i 二级 REVOLUTE
- broad_square_jaw 未真正加宽 jaw_bevel
- palette_style 混进 slot_choice

## 与相邻类别的边界

- 不该混入：cutting_pliers / needle_nose / locking / vise-grip / slip-joint / channel-lock / wire_strippers / scissors / 扳手 / 镊子。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工确认；本类无 clip spring 端锚子件，captured_spring 为 pivot_pin 上 visual + 两半 anchor_slot 视觉共同表达。 |

## 模板实现备注

- 共享 helper: `_mirror_points`, `_profile_solid`, `_make_forged_half`, `_make_grip`, `_make_grip_collar`, `_make_grip_highlight`, `_make_jaw_bevel_*`, `_make_cutting_edge`, `_make_serrated_insert`, `_make_pivot_pin_*`, `_make_link_bar`, `_make_captured_spring`.
- 关键 captured-pin overlap: broad `allow_overlap(pivot_pin, handle_i)` 与 (compound 分支) `allow_overlap(pivot_pin, link_i)` + `allow_overlap(link_i, handle_i)`.
- 主 REVOLUTE 均省略 MatingContract（captured-pin grandfathered）；origin 落真实 pivot 几何。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 |
|---|---|---|---|---|
| P0 | A/B/C/D | tapered_serrated / fixed_rivet / no_spring / straight_dipped | rec_picturex_0611__pilers_linesman_pliers__001__png_6e9299cc363b4f9a93a12472b974811f | `_make_forged_half` L44-116, `_make_grip` L119-138, `_make_jaw_bevel` L173-185, `_make_cutting_edge` L188-198, `_make_serrated_insert` L201-210, `_make_pivot_pin` L213-232, joints L395-422 |
| V-JAW1 | A | broad_square_jaw | rec_0611_pilers_linesman_pliers_var_jaw_module_broad_square_jaw | `_make_jaw_bevel` L173-186, run_tests assert L618-627 |
| V-JAW2 | A | fish_tape_channel | rec_0611_pilers_linesman_pliers_var_jaw_module_fish_tape_channel | `_make_fish_tape_channel` L200-215 |
| V-JAW3 | A | crimper_cavity | rec_0611_pilers_linesman_pliers_var_jaw_module_crimper_cavity | `_make_crimper_cavity` L195-218 |
| V-JAW4 | A | cable_pulling_groove | rec_0611_pilers_linesman_pliers_var_jaw_module_cable_pulling_groove | `_make_cable_groove` L190-212 |
| V-L1 | B | compound_link | rec_0611_pilers_linesman_pliers_var_leverage_compound_link | `_make_link_bar` L239-291, parts L447-475, joints L516-577 |
| V-L2 | B | offset_pivot | rec_0611_pilers_linesman_pliers_var_leverage_offset_high_leverage_pivot | `_make_pivot_pin` L218-243 |
| V-R | C | captured_spring | rec_0611_pilers_linesman_pliers_var_return_captured_spring | `_make_captured_spring` L237-282, `_make_spring_anchor_slot` L283-298 |
| V-H1 | D | long_handle | rec_0611_pilers_linesman_pliers_var_handle_long_handle | `_make_grip` L119-140 |
| V-H2 | D | guarded_insulated_grip | rec_0611_pilers_linesman_pliers_var_handle_guarded_insulated_grip | `_make_grip` L119-140 |
