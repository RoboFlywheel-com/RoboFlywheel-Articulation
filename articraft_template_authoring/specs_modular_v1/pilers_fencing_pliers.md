# pilers_fencing_pliers — Modular Spec

> 来源小类：`picture/0611/Pilers_fencing_pliers`（articraft_data 上游小类样本池；对象身份为一把手动 fencing pliers ——两片锻钢半钳绕中央 rivet 交叉；一半是宽 hammer head + 侧 jaw + wire slot，另一半是弯 claw hook + 侧 jaw + fork_slot；柄部张合驱动 jaw 侧切并把 claw 用作 nail puller）。slug `pilers_fencing_pliers`。
> 上游 source map：`picture_expansion/template_source_maps/0611__Pilers_fencing_pliers.md`。
> **同步状态**：9 个 5★ fork 变体（3 hammer_claw / 2 jaw_cutter / 1 leverage / 1 return / 2 handle）已同步进本仓库 `data/records/rec_0611_pilers_fencing_pliers_*/revisions/rev_000001/model.py`，rating=5。origin_anchor 母资产的 P0 直接观察未同步为 5★ 独立 record，但共享同一 `_ribbon`/`_profile`/`_soften_vertical_edges` helper 家族与 3-part 骨架（pivot + hammer_handle + claw_handle）——见 `_var_return_captured_spring` 作为"最接近 origin"的 canonical 参照（source map 标其为 converged）。行号按各样本本仓库 `revisions/rev_000001/model.py` 计。
> **建模基线（重要）**：origin/baseline 共享 3-part / 2-joint 骨架：**`pivot`（root，承载 pivot_pin + pivot_cap + pivot_back + 可选 captured_spring）** + `hammer_handle`（承宽 hammer head + jaw + grip）+ `claw_handle`（承弯 claw hook + jaw + grip）。`pivot_to_hammer_half` REVOLUTE (pivot→hammer, axis +Z, lower=-0.24 upper=0.12) + `pivot_to_claw_half` REVOLUTE (pivot→claw, axis +Z, lower=-0.12 upper=0.24)。**每半各绕 pivot 独立旋转**（与 cutting pliers 的"root_half→moving_half"不同——fencing pliers 用中央 pin 作为 root 承载 return spring）。仅 `leverage=compound_link` 追加两条 link bars（`hammer_link` + `claw_link`）+ 两条 REVOLUTE（`hammer_compound_link` + `claw_compound_link`），5-part / 4-joint。

## 元信息
| 项 | 值 |
|---|---|
| slug | `pilers_fencing_pliers` |
| template path | `agent/templates/pilers_fencing_pliers.py` |
| test path (optional) | 无（sweep-pipeline 为唯一验收） |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（pivot 为 root，两半各绕 pivot REVOLUTE；hammer_claw / jaw_cutter / handle 是两半上的 part-internal 几何层；leverage=compound_link 追加两条 link parts + 两条 REVOLUTE；return=captured_spring 是 pivot 上 spring 视觉层） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9（全部样本 `model.py` 全文逐行读，含 build_object_model + run_tests；结构冗余高，diff 干净） |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted module sources are indexed below |

样本与采纳分工：
- **V-R1 captured_spring (baseline)**（`rec_0611_pilers_fencing_pliers_var_return_captured_spring`）：3-part 骨架基线——`pivot`（承 pivot_pin r=0.011 l=0.011、pivot_cap r=0.014 l=0.0015、pivot_back r=0.013 l=0.0015、`captured_spring` mesh 从 `_captured_return_spring` helper 生成——扁螺旋 spring wire 跨两柄内侧）为 root，`hammer_handle` + `claw_handle` 各承 `hammer_forging`（`_ribbon` handle 中线 + `_profile` 宽 head + 圆 boss + `wire_slot` triangular cut + `keyhole` cut）/ `claw_forging`（`_ribbon` + `_profile` 弯 hook + `throat` circle cut + `fork_slot` V cut）+ `striking_face`（hammer 端 polished）+ `hammer_jaw`/`claw_jaw`（hardened side pad）+ `hammer_cutter`/`claw_cutter`（hardened cutter shim）+ `hammer_transition`/`claw_transition`（black rubber）+ `hammer_grip`/`claw_grip`（red rubber sleeve）。`pivot_to_hammer_half` axis +Z lower=-0.24 upper=0.12，`pivot_to_claw_half` axis +Z lower=-0.12 upper=0.24。**Slot Base：baseline_hammer_and_claw + jaw_with_cutter + fixed_rivet + captured_spring + straight_dipped_handle**。source: L20-86 helper, L100-127 materials, L130-159 pivot, L162-343 hammer_handle, L345-497 claw_handle, L499-536 joints。
- **V-HC1 round_hammer_face**（`rec_0611_pilers_fencing_pliers_var_hammer_claw_round_hammer_face`）：hammer_head polyline 加宽成圆弧（`_profile` 顶部多点铺圆）；`striking_face` 从 `_profile` 改为 `circle(14.5).extrude(5.0)` 圆盘（真圆盘）。claw_head 与 baseline 同。part / joint 计数不变。source: L145-232（hammer_head + striking_face）。**Slot A：round_hammer_face 来源**。
- **V-HC2 deep_staple_claw**（`rec_0611_pilers_fencing_pliers_var_hammer_claw_deep_staple_claw`）：claw_head polyline 加长到 -88mm（vs baseline -75mm）；`throat` 圆心 (-52,64) r=10（vs baseline (-39,43) r=13）；`fork_slot` 从 (-90,48)-(-70,54)-(-90,60)（vs (-78,55)-(-56,58.5)-(-78,62)）。hammer_head 与 baseline 同。part / joint 计数不变。source: L328-395（claw_head + throat + fork_slot）。**Slot A：deep_staple_claw 来源**。
- **V-HC3 offset_claw**（`rec_0611_pilers_fencing_pliers_var_hammer_claw_offset_claw`）：claw_head polyline 沿 -y 偏移锚点；hammer_head 加宽以平衡；claw jaw / cutter 微调。part / joint 计数不变。source: L145-235 hammer_head + L331-410 claw_head。**Slot A：offset_claw 来源**。
- **V-JC1 broad_serrated_jaw**（`rec_0611_pilers_fencing_pliers_var_jaw_cutter_broad_serrated_jaw`）：hammer_jaw / claw_jaw 用 `_serrated_jaw_pad` helper 铺宽 pad（含平行 groove），**移除 hammer_cutter / claw_cutter 两个 visual**（jaw 兼作 crimp/gripping 面）。hammer_forging / claw_forging / striking_face 与 baseline 同。part / joint 计数不变。source: L277-295 hammer_jaw + L430-448 claw_jaw + L565-575 test assertion no cutter。**Slot B：broad_serrated_jaw 来源**。
- **V-JC2 twin_side_cutters**（`rec_0611_pilers_fencing_pliers_var_jaw_cutter_twin_side_cutters`）：两半 head 从"hammer/claw asymmetric"改为**对称 tapered side-cutter head**（`_base_head` 单形态镜像应用两侧），**移除 striking_face**（对称 side-cutter 无 hammer 端）；part 名从 `hammer_handle/claw_handle` 变为 `left_half/right_half`（对称）。part / joint 计数仍为 3 / 2。source: L125-183（head/jaw/cutter geometry）+ L273-315（visuals per half）+ L505-508 test no striking face。**Slot B：twin_side_cutters 来源**（注：本模板保持 `hammer_handle/claw_handle` 命名，只在 twin_side_cutters 模式下省略 striking_face 且两半 head 使用对称几何——保 part 名一致以简化 kinematics 断言）。
- **V-L1 compound_link**（`rec_0611_pilers_fencing_pliers_var_leverage_compound_link`）：baseline 3-part + 追加 `hammer_link` + `claw_link` 两个 link bar parts（`_compound_link_bar(length=28, width=8, thickness=3, boss_radius=5.5)` helper），两条追加 REVOLUTE：`hammer_compound_link`（parent=hammer_handle, child=hammer_link, origin=(-0.015, 0.012, 0), axis +Z, lower=-0.35 upper=0.35）+ `claw_compound_link`（parent=claw_handle, child=claw_link, origin=(0.015, 0.012, 0)）。part / joint 计数：5 / 4。source: L91-176 `_compound_link_bar` + L574-615 link parts + L647-672 link joints。**Slot C：compound_link 来源**。
- **V-H1 long_fencing_handle**（`rec_0611_pilers_fencing_pliers_var_handle_long_fencing_handle`）：`hammer_grip` / `claw_grip` centerline 拉长到 -290/-260mm（vs baseline -220），width 数组扩展 [18,19,19,18.5,18,17.5,16.5,15]；`hammer_transition` / `claw_transition` 与 baseline 同。part / joint 计数不变。source: L271-288 hammer_grip + L427-444 claw_grip。**Slot D：long_fencing_handle 来源**。
- **V-H2 flared_comfort_grip**（`rec_0611_pilers_fencing_pliers_var_handle_flared_comfort_grip`）：`hammer_grip` / `claw_grip` width 数组加大 [19,22,25,27,28,26]（vs baseline [18,19,19,18.5,18,16]），thickness 从 11 → 13；`hammer_transition` / `claw_transition` width 数组 [15,17,20,23]（vs [14,15,16,17]）；material 从 `red_grip` 改为 `comfort_grip`。part / joint 计数不变。source: L268-291 flare grip + L426-449 claw side。**Slot D：flared_comfort_grip 来源**。

冗余说明：9 个样本核心骨架（pivot + hammer_handle + claw_handle + 两 REVOLUTE from pivot）完全同构；每个 fork 只改 1 根结构轴，diff 干净。仅 compound_link 改链拓扑（+2 part +2 joint），jaw_cutter=twin_side_cutters 改 head 形态并省略 striking_face（无 part / joint 变更），其余是 part-internal visual 几何变体。

## 核心身份

一把 **手动 fencing pliers**（fence-work pliers/staple pliers）：**pivot pin 承起两片锻钢半钳**——一半是 **宽 hammer head**（带 wire_slot 三角切口 + keyhole）+ striking_face + 侧 jaw + 弯下 grip；另一半是 **弯 claw hook**（nail puller，带 throat 圆切口 + fork_slot V 切口）+ 侧 jaw + 弯下 grip。**主用户机构 = 两半各绕中央 pivot REVOLUTE**（两个独立 REVOLUTE，axis +Z）；合柄 = 合 jaw + 拉起 claw（nail 拔出方向）、张柄 = 分 jaw + 松 claw。**pivot 是 root**（承载 pin/cap/back + 可选 captured 返回弹簧）。

物体平躺 XY 平面（Z = 厚度方向）：hammer head 指 +X，claw hook 指 -X，柄向 -Y 张开；pivot 在世界原点 (0,0,0)。hammer_handle 承左柄 + 右宽 head，claw_handle 承右柄 + 左弯 hook。**leverage=compound_link 特例**：hammer_handle / claw_handle 各追加一条 link bar（`hammer_link` / `claw_link`），link bars 各挂在对应 handle 的第二 pivot 上（origin ~(±0.015, 0.012, 0)）作为 toggle 增力元件——追加 2 REVOLUTE，共 4 joint / 5 part。

默认成熟域：真实 fencing pliers 尺度（整长 ~0.22-0.30 m，宽 ~0.15-0.19 m，hammer head ~0.08 m 直径，claw hook ~0.075-0.088 m 弧长）。hammer_claw 形态可为 default_asymmetric / round_hammer_face / deep_staple_claw / offset_claw；jaw_cutter 可为 jaw_with_cutter（baseline）/ broad_serrated_jaw（jaw pad 无 cutter shim）/ twin_side_cutters（两半 head 对称，无 striking_face）；leverage 可为 fixed_rivet（2 REVOLUTE from pivot）/ compound_link（追加两 link parts + 两 REVOLUTE，共 5 part / 4 joint）；return 可为 captured_spring（pivot 上视觉 spring）/ no_spring（omit spring visual）；handle 可为 straight_dipped / long_fencing_handle / flared_comfort_grip。

不该混入：**其他钳（cutting/needle_nose/vise-grip/slip-joint/channel-lock/linesman）**——本类专职 fencing（宽 hammer + 弯 claw 组合 + 侧 jaw + wire slot），其他 plier 无此不对称 head 组合；**锤子/羊角锤**（无 pivot 双柄）；**扳手/spanner**；**剪刀/scissors**。

## 槽位 + 候选模块表

> **建模注记（重要）**：pilers_fencing_pliers 的骨架由 **Slot C (leverage_mechanism)** 决定链拓扑（fixed_rivet = 3-part / 2-joint；compound_link = 5-part / 4-joint）。**Slot A (hammer_claw_form)** 与 **Slot D (handle_form)** 是两半上的 part-internal 几何层。**Slot B (jaw_cutter)** 影响 hammer_jaw/claw_jaw 形态与是否发出 cutter shim / striking_face visual。**Slot E (return_spring)** 是 pivot 上 spring visual 层（不改 part / joint 计数）。
> 下面 5 个离散 slot + 1 个 palette 轴（palette_style，仅 ⑥ 涂装，不进 slot_choice / 不改拓扑）。

### Slot A：hammer_claw_form（宽 hammer + 弯 claw 组合形；③ 主体形态家族 / Primary Form Family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype | 结构特征 |
|---|---|---|---|---|---|---|
| default_asymmetric（基线）| origin_anchor | V-R1 baseline | `hammer_head` L182-204, `claw_head` L365-389, `striking_face` L247-262（`_var_return_captured_spring`）| eligible if compatible | Planar Boundary Form | 基线不对称 head：hammer_head `_profile` 长 polyline 铺宽 head（tip 到 x≈77），striking_face `_profile` 三角块；claw_head `_profile` 弯 hook（tip 到 x≈-75，弧顶 y≈57）+ throat 圆切 + fork_slot V 切 |
| round_hammer_face | forked_anchor | V-HC1 | `hammer_head` L145-169, `striking_face` L211-221（`circle(14.5).extrude(5.0)`）| eligible if compatible | Planar Boundary Form | 圆盘 hammer face：hammer_head 顶部加宽成圆弧，striking_face 用真圆盘（Cylinder-like 14.5mm r × 5mm 厚）代替三角块 |
| deep_staple_claw | forked_anchor | V-HC2 | `claw_head` L328-353, `throat` L364-375, `fork_slot` L376-380 | eligible if compatible | Planar Boundary Form | 加深 staple claw：claw_head tip 到 -88mm（vs -75），弧顶前移；throat 圆心 (-52,64) r=10；fork_slot V 加长 |
| offset_claw | forked_anchor | V-HC3 | `claw_head` L331-410 | eligible if compatible | Planar Boundary Form | 偏移 claw：claw_head 锚点沿 -y 偏；hammer_head 加宽以平衡 |

> 4 candidate（达 3-6 目标）。四者改 `hammer_head` / `claw_head` / `striking_face` 平面 polyline 与形态（Planar Boundary Form），保 part tree / interface / primitive 家族一致。

### Slot B：jaw_cutter（jaw 与 cutter 的组合层；① 骨架轴，可省略 visual）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| jaw_with_cutter（基线）| origin_anchor | V-R1 baseline | `hammer_jaw` L275-289, `hammer_cutter` L280-294, `claw_jaw` L430-443, `claw_cutter` L435-448（`_var_return_captured_spring`）| eligible if compatible | 两半各带 hardened `jaw` (`_profile` 侧 pad) + `cutter` (`_profile` 薄剪刃 shim)，striking_face 保留 |
| broad_serrated_jaw | forked_anchor | V-JC1 | `_serrated_jaw_pad` helper + hammer_jaw L275-295, claw_jaw L430-450, test "no cutter" L570-573 | eligible if compatible | 宽 serrated pad：`hammer_jaw` / `claw_jaw` 用 groove pad 代替窄 jaw；**不发出 hammer_cutter / claw_cutter**（省略 2 visual，保 part / joint 计数）；striking_face 保留 |
| twin_side_cutters | forked_anchor | V-JC2 | `_base_head` L128-142, `_base_jaw` L158-169, `_base_cutter` L172-182, per-half emit L273-313, test "no striking face" L505-508 | eligible if compatible | 对称 side-cutter head：两半 head 使用同 `_base_head` polyline（镜像应用），**省略 striking_face visual**；jaw + cutter 均以对称 taper 形态发出 |

> 3 candidate（达目标下限）。三者的差异全在 visual 组合（发出/省略 hammer_cutter/claw_cutter/striking_face 与 jaw 几何族），保 3-part 骨架、2 REVOLUTE 不变。

### Slot C：leverage_mechanism（枢轴 / 杠杆机构；② 关节 / 骨架轴，决定链拓扑）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| fixed_rivet（基线）| origin_anchor | V-R1 baseline | `pivot_to_hammer_half` L499-517, `pivot_to_claw_half` L518-536（`_var_return_captured_spring`）| eligible if compatible | 单 pivot，两条 REVOLUTE from pivot；3-part 链 pivot + hammer + claw；`pivot_pin` cylinder r=0.011 l=0.011 在 pivot 上 |
| compound_link | forked_anchor | V-L1 | `_compound_link_bar` L91-176, `hammer_link` part L574-593, `claw_link` part L596-615, `hammer_compound_link` L647-659, `claw_compound_link` L660-672 | eligible if compatible | 追加 `hammer_link` + `claw_link` 两 toggle bar parts（`_compound_link_bar` helper：length=28mm, width=8mm, thickness=3mm, boss_radius=5.5mm）+ 两条 REVOLUTE（origin ~(±0.015, 0.012, 0), axis +Z, range [-0.35, 0.35]）；5-part / 4-joint |

> 2 candidate（<3 但拓扑差异显著且 source 支持；source map 仅列 compound_link 一个 leverage fork，故 2 达标下限 by axis policy——source 覆盖已尽）。

### Slot D：handle_form（手柄形态；③ 骨架 grip polyline 家族切换）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| straight_dipped（基线）| origin_anchor | V-R1 baseline | `hammer_grip` L305-320, `claw_grip` L460-475, `hammer_transition` L296-304（`_var_return_captured_spring`）| eligible if compatible | 直筒 red rubber sleeve：`_ribbon` centerline 到 -220mm, widths [18,19,19,18.5,18,16]，thickness 11mm；`transition` black rubber 段 widths [14,15,16,17] |
| long_fencing_handle | forked_anchor | V-H1 | `hammer_grip` L271-288, `claw_grip` L427-444 | eligible if compatible | 加长柄：centerline 到 -290mm（extra points at -225/-260/-290），widths [18,19,19,18.5,18,17.5,16.5,15]；transition 同 baseline |
| flared_comfort_grip | forked_anchor | V-H2 | `hammer_grip` L277-291, `hammer_transition` L268-275, `claw_grip` L435-449 | eligible if compatible | 加宽 flare grip：widths [19,22,25,27,28,26]，thickness 13mm；transition widths [15,17,20,23]，thickness 9.5mm；material 名可切至 `comfort_grip` (但本模板保留 `red_grip` 材质 slot，仅换 palette) |

> 3 candidate（达目标下限）。三者改 `_ribbon` centerline 长度与 widths 数组（形态原型不同：短/长/flare），保 part / joint 与 transition + grip 两 visual 结构不变。

### Slot E：return_spring（pivot 上返回弹簧 visual；② 关节附属 visual，可选）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| captured_spring（基线）| origin_anchor | V-R1 | `_captured_return_spring` L69-86, pivot visual `captured_spring` L149-159 | eligible if compatible | 扁螺旋 return spring（`_captured_return_spring` = spiral centerline + `_ribbon` 铺 1.9mm 宽 tube）作为 pivot 的 visual，视觉表达"pivot 上捕获返回弹簧" |
| no_spring | axis_variant | 世界知识扩展；许多 fencing pliers 无外部返回弹簧（依赖用户手动打开）| — | eligible if compatible | 省略 pivot 上 `captured_spring` visual；保 pivot_pin / pivot_cap / pivot_back 三视觉 |

> 2 candidate（<3 但 source 已尽，且 ② 视觉附属层典型只在"有"/"无"两态；符合 by axis policy）。

## 槽位图（slot graph）

```
pattern: mixed（pivot 为 root 承两条 REVOLUTE 到 hammer + claw；jaw_cutter 决定 head 上是否有 cutter shim 与 striking_face；
                leverage=compound_link 追加 2 link parts + 2 REVOLUTE 变成 5-part / 4-joint 链；
                return=captured_spring 追加 pivot 上 spring visual；handle 改 grip _ribbon centerline / widths）

  ── Slot C = fixed_rivet（3-part / 2-joint，基线）──
    pivot (root)  ──[REVOLUTE pivot_to_hammer_half, axis +Z, origin (0,0,0)]──>  hammer_handle
      承载: pivot_pin, pivot_cap, pivot_back                                        承载: hammer_forging (hammer_head[A])
             + (return=captured_spring: captured_spring visual[E])                          + striking_face[A/B]
                     │                                                                       + hammer_jaw[B] + hammer_cutter[B?]
                     └[REVOLUTE pivot_to_claw_half, axis +Z, origin (0,0,0)]──> claw_handle    + hammer_transition + hammer_grip[D]
                                                                                     承载: claw_forging (claw_head[A])
                                                                                            + claw_jaw[B] + claw_cutter[B?]
                                                                                            + claw_transition + claw_grip[D]

  ── Slot C = compound_link（5-part / 4-joint）──
    pivot ─┬─(pivot_to_hammer_half)─> hammer_handle ─(hammer_compound_link, origin (-0.015, 0.012, 0))─> hammer_link
           └─(pivot_to_claw_half)  ─> claw_handle  ─(claw_compound_link,   origin ( 0.015, 0.012, 0))─> claw_link
```

接口点位（每条连接）：
- **pivot → hammer_handle (`pivot_to_hammer_half`)**：mating = 中央 pivot pin 轴线（`origin=(0,0,0)`），joint = REVOLUTE，axis `(0,0,+1)`，range `[-0.24, 0.12]`（scale by `open_angle_scale`）。**MatingContract 省略（grandfathered）**：pivot_pin 是 pivot 的 inline visual (`Cylinder r=0.011 l=0.011`)，pivot pin 穿过 hammer_handle 的 forging 中央 hub；broad `allow_overlap(pivot, hammer_handle, elem_a="pivot_pin", elem_b="hammer_forging", reason="pivot pin captured through hammer half hub")`。origin 落 pivot pin 真实几何 (0,0,0)。
- **pivot → claw_handle (`pivot_to_claw_half`)**：同 hammer 对称，range `[-0.12, 0.24]`；broad `allow_overlap(pivot, claw_handle, elem_a="pivot_pin", elem_b="claw_forging", reason=...)`。
- **hammer_handle → hammer_link (`hammer_compound_link`，compound_link 分支)**：mating = hammer_handle 上的第二 pivot 点（`origin=(-0.015, 0.012, 0)`，落 hammer_link 上端 boss），joint = REVOLUTE，axis `(0,0,+1)`，range `[-0.35, 0.35]`。MatingContract 省略。broad `allow_overlap(hammer_handle, hammer_link)`。
- **claw_handle → claw_link (`claw_compound_link`，compound_link 分支)**：镜像，`origin=(0.015, 0.012, 0)`，同 range。
- **captured_spring, striking_face, hammer_jaw, hammer_cutter, claw_jaw, claw_cutter, pivot_pin/cap/back**：pivot / hammer_handle / claw_handle 内的 inline visual（FIXED 语义，不建独立装饰 part）。
- **互斥/可选/派生**：Slot C 决定 3-part vs 5-part 链（互斥）；Slot A / B / D / E 与 Slot C 正交；Slot B 决定是否发出 hammer_cutter/claw_cutter + 是否保留 striking_face；Slot E 决定是否发出 pivot 上 captured_spring visual。

## 每槽位 Module Emits / Interfaces

### Slot A / module default_asymmetric（baseline）
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `hammer_forging`（`_ribbon` 中线 + `_profile` 宽 head + boss + wire_slot + keyhole cuts）, `claw_forging`（`_ribbon` + `_profile` 弯 hook + boss + throat + fork_slot cuts）| V-R1 / L162-243（hammer）L345-428（claw）|
| downstream interface | hammer_head 到 x≈+77 mm; claw_head tip 到 x≈-75 mm | V-R1 |

### Slot A / module round_hammer_face
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 圆弧 hammer_head + 圆盘 `striking_face` (`circle(14.5).extrude(5.0)`)；claw_head 与 baseline 同 | V-HC1 / L145-232 |
| downstream interface | striking_face x_max > 65 mm、圆形 aabb 检测 | V-HC1 |

### Slot A / module deep_staple_claw
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 加深 claw_head 到 tip x=-88 mm; throat 圆心 (-52,64) r=10; fork_slot V 加长 | V-HC2 / L328-380 |
| downstream interface | 断言 claw_forging min_x < -0.085 | V-HC2 |

### Slot A / module offset_claw
| emits | 描述 | 来源 |
|---|---|---|
| visuals | claw_head 锚点沿 -y 偏；hammer_head 加宽以平衡；jaw / cutter 微调 | V-HC3 / L145-235, L331-410 |
| downstream interface | claw_forging 质心 y_min 显著负偏 | V-HC3 |

### Slot B / module jaw_with_cutter（baseline）
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `hammer_jaw` (`_profile` 5点 pad) + `hammer_cutter` (`_profile` 4点 shim), `claw_jaw` + `claw_cutter` | V-R1 / L275-294, L430-449 |
| downstream interface | 4 hardened 视觉均存在 | V-R1 / L582-599 test |

### Slot B / module broad_serrated_jaw
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `hammer_jaw` 宽 pad (7点 polyline)、`claw_jaw` 宽 pad；**不发出 hammer_cutter / claw_cutter** | V-JC1 / L277-295, L430-450 |
| downstream interface | 断言 hammer_jaw x-width > 0.016 且 y-length > 0.020；断言无 cutter 视觉 | V-JC1 / L570-599 |

### Slot B / module twin_side_cutters
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 两半共享 `_base_head` 对称 taper head；`hammer_jaw` / `claw_jaw` 用 `_base_jaw` 对称形；`hammer_cutter` / `claw_cutter` 用 `_base_cutter` 对称薄片；**不发出 striking_face** | V-JC2 / L125-183, L273-315 |
| downstream interface | 断言无 striking_face 视觉；断言两半 head 形态对称（min_x 与 max_x 绝对值差 < 0.005） | V-JC2 / L505-508 |

### Slot C / module fixed_rivet
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `pivot_pin` (Cylinder r=0.011 l=0.011), `pivot_cap` (r=0.014 l=0.0015), `pivot_back` (r=0.013 l=0.0015)，pivot inline | V-R1 / L131-148 |
| internal joints | `pivot_to_hammer_half` REVOLUTE axis +Z range [-0.24, 0.12]，`pivot_to_claw_half` REVOLUTE axis +Z range [-0.12, 0.24] | V-R1 / L499-536 |
| upstream/downstream interface | broad `allow_overlap(pivot, hammer_handle, elem_a="pivot_pin", elem_b="hammer_forging")` + 同 claw | V-R1 / 隐式（captured-pin） |

### Slot C / module compound_link
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hammer_link` + `claw_link`（各 `_compound_link_bar(length=28, width=8, thickness=3, boss_radius=5.5)`）| V-L1 / L91-176, L574-615 |
| internal joints | 加 `hammer_compound_link` REVOLUTE (hammer→hammer_link, origin (-0.015, 0.012, 0), axis +Z, range [-0.35, 0.35]) + `claw_compound_link` REVOLUTE (claw→claw_link, origin (0.015, 0.012, 0)) | V-L1 / L647-672 |
| upstream/downstream interface | link bar 上端 boss captured 于 hammer/claw handle 的第二 pivot；broad `allow_overlap` on both link pairs | V-L1 |

### Slot D / module straight_dipped（baseline）
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `hammer_grip` (`_ribbon` widths [18,19,19,18.5,18,16] thickness 11), `claw_grip` (镜像), `hammer_transition` (widths [14,15,16,17] thickness 9), `claw_transition` | V-R1 / L296-342, L451-497 |
| downstream interface | grip aabb min_y < -0.210；transition 存在 | V-R1 / L709-716 |

### Slot D / module long_fencing_handle
| emits | 描述 | 来源 |
|---|---|---|
| visuals | grip centerline 加长到 -290mm，8 点 widths [18,19,19,18.5,18,17.5,16.5,15] | V-H1 / L271-288 |
| downstream interface | 断言 grip min_y < -0.260 | V-H1 |

### Slot D / module flared_comfort_grip
| emits | 描述 | 来源 |
|---|---|---|
| visuals | grip widths [19,22,25,27,28,26] thickness 13；transition widths [15,17,20,23] thickness 9.5 | V-H2 / L268-291 |
| downstream interface | 断言 grip x-width > 0.024（比 baseline 加宽显著）| V-H2 |

### Slot E / module captured_spring（baseline）
| emits | 描述 | 来源 |
|---|---|---|
| visuals | `captured_spring` mesh 从 `_captured_return_spring` helper（spiral + straight tails, `_ribbon` 1.9mm 宽）作为 pivot 的第 4 个视觉 | V-R1 / L69-86, L149-159 |
| downstream interface | 断言 pivot has_visual("captured_spring") | V-R1 |

### Slot E / module no_spring
| emits | 描述 | 来源 |
|---|---|---|
| visuals | 省略 `captured_spring` visual；保留 pivot_pin / pivot_cap / pivot_back 三视觉 | 世界知识扩展 |
| downstream interface | 断言 pivot 无 captured_spring | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| hammer_claw_form | enum | {default_asymmetric, round_hammer_face, deep_staple_claw, offset_claw} | default_asymmetric | choice | deterministic procedural sampler 选择 | Slot A |
| jaw_cutter | enum | {jaw_with_cutter, broad_serrated_jaw, twin_side_cutters} | jaw_with_cutter | choice | sampler 选择 | Slot B |
| leverage_mechanism | enum | {fixed_rivet, compound_link} | fixed_rivet | choice | sampler 选择；决定 3-part vs 5-part 链 | Slot C |
| handle_form | enum | {straight_dipped, long_fencing_handle, flared_comfort_grip} | straight_dipped | choice | sampler 选择 | Slot D |
| return_spring | enum | {captured_spring, no_spring} | captured_spring | choice | sampler 选择 | Slot E |
| palette_style | enum | {steel_red_black, black_orange, chrome_natural, gunmetal_yellow, polished_silver, industrial_green} | steel_red_black | palette | **palette only，不进 slot_choice / 不改拓扑**；按 seed 采样 | V-R1 配色 + 世界知识扩展 |
| overall_len_scale | float | [0.90, 1.15] | 1.0 | independent | 整体等比缩放；clamp 保真实 fencing pliers 尺度（整长 ∈ [0.22, 0.32]）| V-R1 整长 ~0.24 m |
| head_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 hammer_head / claw_head 的 xy；clamp 保 head_max 尺度 | V-R1 head 尺度 |
| grip_girth_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 grip _ribbon widths；clamp 保两半 grip 在 rest pose 不互穿 | V-R1 grip |
| open_angle_scale | float | [0.80, 1.20] | 1.0 | independent | 缩放 pivot_to_hammer / pivot_to_claw 的 upper / lower；clamp | V-R1 joint L506-511, L525-530 |
| (—) | constraint | — | — | inequality | 中央 pivot origin 必须落 (0,0,0)±0.002 m；两 REVOLUTE 从 pivot 出发 | 接口 / captured-pin |
| (—) | constraint | — | — | inequality | hammer_head max_x ≤ 0.090 m 且 claw_head min_x ≥ -0.095 m（真实 head 上限）| 接口 |

连续 scale 默认独立采样 → inequality 把 pivot origin 钉真实几何 + head 尺度上限守门。全部在 `resolve_config` 内求解。**palette_style 只换 material rgba，绝不进 slot_choice / 不改拓扑。**

### 7.5 编译预算 / compile budget

自报本类别每-seed 编译预算 **~15-25 s**（依据：3-5 part、5-10 visual per part、`_ribbon` polyline extrude + `_profile` union + soften_edges fillet 是主 CQ 成本；compound_link 分支加两 bar；无重布尔雕刻、无 loft、无 groove 循环外的重复原语；参考类比 cutting_pliers 模板 12-18 s + 1-2 追加 part 增量）。分档 tessellation：pivot_pin / pivot_cap / pivot_back 用 SDK `Cylinder`；polyline mesh 通过 `mesh_from_cadquery(..., tolerance=0.0003, unit_scale=0.001)`；captured_spring 用 `mesh_from_cadquery` 直接（不用 spline tube helper，避免螺旋 tesselation 开销）。超出预算先降 hammer/claw forging tolerance 到 0.0004。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots 表达；source map 无多重性轴（`count_param: no strong repeated-part axis planned`）。本类无 groove / 齿列 / 叶片阵列可参数化。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Slot C leverage_mechanism：fixed_rivet（3-part）vs compound_link（5-part +2 REVOLUTE）；source_type=forked_anchor (V-L1) |
| └ multiplicity | 同构件 ×N | 无 | 本类无强多重性轴——source map 明示 `count_param: no strong repeated-part axis planned` |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | 全部 REVOLUTE 绕 +Z（pivot_to_hammer, pivot_to_claw + 可选 hammer_compound_link, claw_compound_link）；轴族一致 |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | 有 | Slot A hammer_claw_form：default_asymmetric / round_hammer_face / deep_staple_claw / offset_claw（4 candidate，均 form_subtype=Planar Boundary Form）；Slot D handle_form 3 candidate（形态原型不同）|
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | Slot B jaw_cutter：jaw_with_cutter（4 hardened 视觉）vs broad_serrated_jaw（省 cutter）vs twin_side_cutters（省 striking_face + 对称 head）；host-conformal visual 层 |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | overall_len_scale [0.90,1.15]、head_scale [0.90,1.10]、grip_girth_scale [0.90,1.10]、open_angle_scale [0.80,1.20]；joint motion 包络：pivot_to_hammer axis +Z range [-0.24, 0.12] × scale, pivot_to_claw [-0.12, 0.24] × scale；无 continuous 关节 |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | palette_style 6 档：steel_red_black / black_orange / chrome_natural / gunmetal_yellow / polished_silver / industrial_green；material 大类覆盖 metal (forged/polished/pivot/hardened steel) + rubber (grip/transition) |

**收尾自检**：每个"有"里列的取值，必须在 `template batch` 的 0-9 seed 渲染里可见——4 hammer_claw / 3 jaw_cutter / 2 leverage / 3 handle / 2 return + 6 palette 可辨。

## 采样与覆盖审计

总组合数（离散槽）：hammer_claw(4) × jaw_cutter(3) × leverage(2) × handle(3) × return(2) = **144** distinct 拓扑等价类。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed 做 deterministic procedural sampling——加权选 5 个离散 slot（基线偏多），采连续 scale，经 `resolve_config` 解析 clamp。`seed=0` 不特殊。
Topology target：1000-seed slot choice tuple distinct 目标 = 144。
Controlled local parameterization：初版即含 `overall_len_scale` / `head_scale` / `grip_girth_scale` / `open_angle_scale`。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 顺序：hammer_claw → jaw_cutter → leverage → handle → return → scales → palette；加权（各 slot baseline 偏多）| slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | (1) 所有 slot 正交。(2) pivot origin 恒钉 (0,0,0)，两 REVOLUTE 从 pivot 出发。(3) hammer_head max_x ≤ 0.090；claw_head min_x ≥ -0.095。(4) pivot_pin 与 hammer_forging / claw_forging captured 恒有 broad allow_overlap。| 无 floating / captured-pin origin 漂移 |
| controlled local variation | 4 个 clamped scale（overall_len / head / grip_girth / open_angle）| 比例变化不破坏 pivot origin、head 上限、grip 互穿、joint range |
| regression overrides | none（首版纯 procedural）| 仅 sweep 暴露的具体失败 seed 才稀疏添加 |
| random sweep | 初轮 seeds 0-49，成熟审计 0-999 | captured-pin overlap / compound_link 5-part 装配 / handle 长度 / palette |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A hammer_claw_form | 4 | yes | yes | default / round_face / deep_staple / offset |
| B jaw_cutter | 3 | yes | yes | jaw_with_cutter / broad_serrated / twin_side_cutters |
| C leverage_mechanism | 2 | yes | no | fixed_rivet / compound_link（source 已尽）|
| D handle_form | 3 | yes | yes | straight_dipped / long_fencing / flared_comfort |
| E return_spring | 2 | yes | no | captured_spring / no_spring（源 + 世界知识扩展）|

## Validator

- slot_choices_for_seed returns implemented module names（hammer_claw_form / jaw_cutter / leverage_mechanism / handle_form / return_spring）
- config_from_seed uses deterministic procedural sampling
- compatibility matrix / gating：所有 slot 正交；pivot origin 恒钉 (0,0,0)；head 上限守门
- critical captured-pin overlap：broad `allow_overlap(pivot, hammer_handle, elem_a="pivot_pin", elem_b="hammer_forging", reason="pivot pin captured through hammer half hub")`；同 claw；compound_link 分支加 broad `allow_overlap(hammer_handle, hammer_link)` + `allow_overlap(claw_handle, claw_link)`
- key joints：`pivot_to_hammer_half` REVOLUTE axis (0,0,+1) range 依 open_angle_scale；`pivot_to_claw_half` REVOLUTE 镜像 range；compound_link 分支加两 REVOLUTE range [-0.35, 0.35]
- 开合测试：pose `pivot_to_hammer_half` 到 upper 使 hammer_grip x 向内、hammer_forging x_max 变化；同 claw
- palette_style 只换 material rgba
- 所有 `.visual(material=mats[...])` 用 `mats` dict 索引

## Reject cases

- 把 pivot 或两 REVOLUTE 做成 FIXED 或省略（fencing pliers 必须有两半 pivot 开合）
- pivot origin 不落 (0,0,0)（漂浮 >0.002 m），或缺 broad allow_overlap → captured-pin 判失败
- leverage=compound_link 但缺 hammer_link / claw_link part 或缺对应 REVOLUTE
- jaw_cutter=broad_serrated_jaw 但仍发出 hammer_cutter / claw_cutter
- jaw_cutter=twin_side_cutters 但仍发出 striking_face 或两半 head 非对称
- hammer_claw_form=round_hammer_face 但 striking_face 仍为 `_profile` 三角块（不是圆盘）
- handle=long_fencing_handle 但 grip min_y 未越过 -0.245
- 用 boxy 占位代替真实 forging / head / grip polyline
- 连续 scale 越界使整长 < 0.22 或 > 0.32 m
- 把 palette_style / 连续尺寸当新 candidate 塞进 slot

## 与相邻类别的边界

- 不该混入：**Other_pliers 综合 / vise-grip / slip-joint / channel-lock / cutting_pliers / linesman**（本类专职 fencing：宽 hammer + 弯 claw + wire_slot + fork_slot 组合）
- 不该混入：**羊角锤 / hammer**（无双柄 pivot）
- 不该混入：**scissors / shears / 剪刀**
- 0611 大类内：区别于 pilers_cutting_pliers / pilers_needle_nose_pliers 等各独立小类

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工确认：(1) leverage_mechanism 仅 2 档是否达标（source 已尽）；(2) return_spring no_spring 世界知识扩展合理性；(3) jaw_cutter twin_side_cutters 保持"hammer_handle/claw_handle" 命名（简化 kinematics 断言）vs 改名 "left/right"（与 source 一致）——本模板选前者。 |

## 模板实现备注（可选）

- 共享 helper：`_profile(points, thickness, z0)`（V-R1 helper）、`_ribbon(centerline, widths, thickness, z0)`（V-R1 helper）、`_soften_vertical_edges(shape, radius)`（V-R1 helper）、`_captured_return_spring()`（V-R1 helper）、`_compound_link_bar(length, width, thickness, boss_radius, z0)`（V-L1 helper）、`_serrated_jaw_pad(points, thickness, z0, groove_count)`（V-JC1 helper）、`_mirror_x(points)`。
- 关键 captured-pin overlap：**broad** `allow_overlap(pivot, hammer_handle, elem_a="pivot_pin", elem_b="hammer_forging", reason="pivot pin captured through hammer half hub")`；同 claw；compound_link 分支加 broad `allow_overlap(hammer_handle, hammer_link, reason="compound link boss captured on hammer secondary pivot")` + 同 claw。
- 主 `pivot_to_hammer_half` / `pivot_to_claw_half` / 可选 `hammer_compound_link` / `claw_compound_link` 均**省略 MatingContract**（captured-pin grandfathered）。
- 派生与门控集中在 `resolve_config`：所有 slot 正交；scale clamp；head 上限守门；integrate handle scale。
- 链拓扑由 leverage_mechanism 派生：fixed_rivet=3-part；compound_link=5-part。
- 开合测试：pose `pivot_to_hammer_half` 到 upper (0.12) 使 hammer_grip x_center 位移 > 0.010 m；pose `pivot_to_claw_half` 到 upper (0.24) 使 claw_grip 位移。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| V-R1 | A/B/C/D/E baseline | default_asymmetric / jaw_with_cutter / fixed_rivet / straight_dipped / captured_spring | rec_0611_pilers_fencing_pliers_var_return_captured_spring | `_profile` L20-28, `_ribbon` L31-58, `_soften_vertical_edges` L61-66, `_captured_return_spring` L69-86, pivot L130-159, hammer_handle L162-343, claw_handle L345-497, joints L499-536 | 3-part 骨架基线；default hammer_claw + jaw_with_cutter + fixed_rivet + straight_dipped + captured_spring 各 slot 基线 |
| V-HC1 | A | round_hammer_face | rec_0611_pilers_fencing_pliers_var_hammer_claw_round_hammer_face | hammer_head L145-169, striking_face L211-221 | 圆盘 hammer face |
| V-HC2 | A | deep_staple_claw | rec_0611_pilers_fencing_pliers_var_hammer_claw_deep_staple_claw | claw_head L328-353, throat L364-375, fork_slot L376-380 | 加深 claw hook |
| V-HC3 | A | offset_claw | rec_0611_pilers_fencing_pliers_var_hammer_claw_offset_claw | hammer_head L145-235, claw_head L331-410 | 偏移 claw |
| V-JC1 | B | broad_serrated_jaw | rec_0611_pilers_fencing_pliers_var_jaw_cutter_broad_serrated_jaw | `_serrated_jaw_pad` + hammer_jaw L277-295, claw_jaw L430-450, test "no cutter" L570-573 | 宽 serrated pad, 省 cutter |
| V-JC2 | B | twin_side_cutters | rec_0611_pilers_fencing_pliers_var_jaw_cutter_twin_side_cutters | `_base_head` L128-142, `_base_jaw` L158-169, `_base_cutter` L172-182, per-half emit L273-313, test no striking_face L505-508 | 对称 side-cutter, 省 striking_face |
| V-L1 | C | compound_link | rec_0611_pilers_fencing_pliers_var_leverage_compound_link | `_compound_link_bar` L91-176, hammer_link L574-593, claw_link L596-615, hammer_compound_link L647-659, claw_compound_link L660-672 | 5-part 链 + 2 toggle bars + 2 REVOLUTE |
| V-H1 | D | long_fencing_handle | rec_0611_pilers_fencing_pliers_var_handle_long_fencing_handle | hammer_grip L271-288, claw_grip L427-444 | 加长柄 |
| V-H2 | D | flared_comfort_grip | rec_0611_pilers_fencing_pliers_var_handle_flared_comfort_grip | hammer_grip L277-291, hammer_transition L268-275, claw_grip L435-449 | 加宽 flare grip |
