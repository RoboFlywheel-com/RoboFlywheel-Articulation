# Modular Spec — Science / Surgical bed

## 元信息
| 项 | 值 |
|---|---|
| slug | `surgical_bed` |
| template path | `agent/templates/Science_Surgical_bed.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（2 个并列结构 slot：base × accessories；外加 1 根 multiplicity 轴 `section_count` = 铰接床段链） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 parent + 7 variants） |
| read_count | 8 |

| source_id | record_id | 结构家族 |
|---|---|---|
| S1 | rec_build-...-surg_20260609_183628_574040_3fe8e15f（parent） | 单柱 pedestal + cross-foot；arm rails + horseshoe head；back/leg 两段铰接（N=3） |
| S2 | rec_surgical_bed_var_fourleg | 四腿 splayed base |
| S3 | rec_surgical_bed_var_casterbase | 轮式 trolley base（4 casters loop） |
| S4 | rec_surgical_bed_var_twincolumn | 双柱 H-frame base |
| S5 | rec_surgical_bed_var_siderails | 直边护栏 + IV 杆（替 arm rails/horseshoe） |
| S6 | rec_surgical_bed_var_armboards | padded arm boards（替 arm rails） |
| S7 | rec_surgical_bed_var_sections2 | section N=2（back+seat，无 leg fold） |
| S8 | rec_surgical_bed_var_sections4 | section N=4（多一个 mid hinge + foot 段） |

**共性骨架**：deck+rails+cushion 三明治床面，table-top 在 z≈0.98；seat 段为固定中段（spine），其余段绕轴 (0,−1,0) REVOLUTE 铰接。CadQuery `_deck_shape`/`_cushion_shape`/`_side_rails_shape` + swept-tube（horseshoe / arm rails）—— 无 boxy 降级。≥2 非 fixed 关节（`seat_to_back`/`seat_to_leg` REVOLUTE）。

## 核心身份
手术 / 检查用平躺手术台（operating table）：水平多段可铰接 mattress + 升降立柱底座。识别 = **平躺床面 + ≥1 段 REVOLUTE 铰接**。不该混入：坐姿 surgical_chair（连续座盆 + 环抱靠背，坐高 ~0.45m）、普通病床、裸担架/推车。

## 槽位 + 候选模块表

### Slot A：base / 立柱支撑
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| pedestal_crossfoot | S1 (parent) | L146-L182 / L266-L278 | eligible | 单锥形立柱 + 米字 cross-foot |
| four_leg_splayed | S2 | L145-L188 / L271-L284 | eligible | 中央 hub 下四根斜撑腿 + 四脚 |
| caster_trolley | S3 | L156-L269 / L362-L408 | eligible | 低矩形底盘 + 四 `caster_{i}`（loop）+ 短柱 |
| twin_column_H | S4 | L155-L212 / L296-L318 | eligible | 双立柱 + 横梁 H 架 |

### Slot B：accessories（床侧附件）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| arm_rails_horseshoe_head | S1 (parent) | L206-L246 / L362-L385 | eligible | 弯管臂托 + 马蹄形头托 |
| side_safety_rails_IV_pole | S5 | L191-L283 / L334-L355 | eligible | 直不锈钢护栏 + 一角 IV 立杆 |
| padded_arm_boards | S6 | L186-L286 / L322-L335 | eligible | 摆动支架上的扁平加垫臂板 + 平头垫 |

> **single-candidate slot degrade**：无（A=4, B=3）。

## 槽位图（slot graph）
```
 [Slot A base] ──FIXED──► deck_carrier (seat 中段, spine z≈0.98)
                              ├─ [multiplicity] section_{i} REVOLUTE chain off seat (back / leg / foot ...)
                              └─ [Slot B accessories] FIXED 挂在 seat/back 框边 (rails / arm boards / IV)
```
接口：base 顶面 FIXED 托起 seat 中段；每个非 seat 段以 seat 为 parent，hinge origin 在段间接触缝（axis (0,−1,0)）；accessories 锚在 deck 长边/角。

## 每槽位 Module Emits / Interfaces
- **Slot A**：emits 立柱/底座 part（单柱 / 四腿 loop / caster trolley / 双柱）；caster trolley 的 `caster_{i}` loop 为 FIXED 装饰轮；upstream = 顶面托 seat。
- **Slot B**：emits 臂托/护栏/臂板 visual（FIXED 到 deck 边）；side_rails 额外 emits IV 立杆。
- **Multiplicity**：emits `section_{i}` deck+cushion+rail（shared helper），seat 为固定段，其余 N−1 段各一个 REVOLUTE 铰接 off seat（统一 policy）。

## 参数范围汇总
| 参数 | 类型 | 取值 | 约束 | 来源 |
|---|---|---|---|---|
| base | enum | pedestal_crossfoot / four_leg_splayed / caster_trolley / twin_column_H | choice | Slot A |
| accessories | enum | arm_rails_horseshoe / side_rails_IV / padded_arm_boards | choice | Slot B |
| palette_style | enum | stainless_blue / dark_grey / white_green / chrome_grey / teal（≥3） | palette only | S1-S8 |
| section_count | int | {2,3,4}，N_range [2,5] | multiplicity（1 fixed seat + N−1 REVOLUTE） | S7/S8 |
| deck_w_scale / column_h_scale | float | [0.9,1.15] | independent clamp | S1 |
| (—) | constraint | 段间接缝面共面、铰链 origin 在接触缝 | inequality | S1 |

## Multiplicity / Copy Logic
- **count_param**：`section_count`（铰接床段数）。
- **N_range**：[2, 5]；采样 {2,3,4}（parent=3）。
- **copied object**：deck+cushion+side-rail 段（shared helper）。
- **naming**：`section_{i}`，沿 +X 等距铺；seat 为固定中段（不计入 hinge）。
- **joint policy**：每个非 seat 段一个 REVOLUTE，axis (0,−1,0)，**统一以 seat 为 parent 的 off-seat 铰接**（明确拒绝 S8 那种链式叠 hinge —— 采用 sections2 L264-L286/L370-L391 的 loop-rewrite 范式，把 parent 手写的 seat/back/leg 改写为 `section_{i}` 循环）。
- **loop-rewrite 契约**：parent 手写 seat/back/leg 三段，multiplicity 变体必须改写为 `for i in range(N)` 发射 `section_{i}` + shared helper + 统一 REVOLUTE policy。

## 拓扑多样性审计
- A(4) × B(3) = **12** 纯 slot；× N{2,3,4} = **36+** distinct（N 编码进 slot_choices）。
- procedural_first：采 A/B 均匀 → 加权采 section_count{2,3,4} → palette → 连续 scale。
- 兼容矩阵：所有 base × accessories 两两兼容；section 链与任意 base/accessory 兼容。
- Topology target ~48；远超 10。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## Validator
- `slot_choices_for_seed` 返回 A(4)/B(3) 实现名 + section_chain_nK。
- ≥2 REVOLUTE 床段铰接恒在；统一 off-seat policy（非链式叠 hinge）。
- caster trolley 的 `caster_{i}` loop FIXED；side_rails 的 IV 杆存在。
- 连续 scale clamp；段接缝 inequality 在 resolve_config 求解。
- element-scoped allow_overlap（cushion↔deck、rail↔deck）。

## Reject cases
- 床段全 FIXED → 0 铰接，拒收（出"固定平台"类目）。
- 把坐姿座盆 + 环抱靠背塞入 → 变成 surgical_chair，出类目。
- section 用链式逐段叠 hinge 而非统一 off-seat → 不符合 copy-logic 契约（除非显式声明）。
- palette / scale 当新 candidate → 非结构差异。

## 与相邻类别的边界
- surgical_chair：坐姿（连续座盆 + 五星轮椅脚），非平躺多段台。
- 普通病床：固定平床面，无多段 REVOLUTE 铰接 + 升降立柱。
- 担架/推车：无铰接床段。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |

## Module Source Index
| source_id | slot | module | record_id |
|---|---|---|---|
| S1 | A/B | pedestal_crossfoot / arm_rails_horseshoe (parent) | rec_build-...-surg_..._3fe8e15f |
| S2 | A | four_leg_splayed | rec_surgical_bed_var_fourleg |
| S3 | A | caster_trolley | rec_surgical_bed_var_casterbase |
| S4 | A | twin_column_H | rec_surgical_bed_var_twincolumn |
| S5 | B | side_safety_rails_IV_pole | rec_surgical_bed_var_siderails |
| S6 | B | padded_arm_boards | rec_surgical_bed_var_armboards |
| S7 | multiplicity | section_count N=2 | rec_surgical_bed_var_sections2 |
| S8 | multiplicity | section_count N=4 | rec_surgical_bed_var_sections4 |
