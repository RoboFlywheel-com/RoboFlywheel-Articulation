# Modular Spec — Science / Surgical chair

## 元信息
| 项 | 值 |
|---|---|
| slug | `surgical_chair` |
| template path | `agent/templates/Science_Surgical_chair.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（2 个并列结构 slot：base × backrest-mechanism；外加 1 根条件 multiplicity 轴 `caster_count`） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 parent + 7 variants） |
| read_count | 8 |

| source_id | record_id | 结构家族 |
|---|---|---|
| S1 | rec_build-...-surg_20260609_183631_452724_821a91c4（parent） | 五星轮 base + 气压升降 seat + 固定 stalk 靠背；5 casters loop |
| S2 | rec_surgical_chair_var_pedestal | 固定中央立柱 + 圆盘脚 |
| S3 | rec_surgical_chair_var_fourleg | 四腿 splayed 框 |
| S4 | rec_surgical_chair_var_xcaster | 十字四臂轮 base |
| S5 | rec_surgical_chair_var_caster3 | caster N=3 |
| S6 | rec_surgical_chair_var_recline | 靠背 REVOLUTE 后仰 |
| S7 | rec_surgical_chair_var_headrest | 分体上头托 tilt REVOLUTE |
| S8 | rec_surgical_chair_var_legrest | 前腿托 swing-up REVOLUTE |

**共性骨架（脊柱）**：`seat_lift` PRISMATIC(+Z) 气压升降 + 两个 `*_arm_swing` REVOLUTE(+Z) 翼状扶手（恒在；扶手数固定 2，**不作为轴**）。5 casters / 2 pedals loop-emitted。CadQuery loft/revolve—— 无 boxy 降级。

## 核心身份
坐姿手术 / 检查椅（气压升降 stool 式）：座盆 + 升降柱 + 翼扶手。识别 = **气压升降 PRISMATIC + 翼扶手 REVOLUTE**。不该混入：平躺 surgical_bed（多段水平台）、普通办公椅（无气压升降/扶手摆动语义）、裸 stool（无靠背/扶手）。

## 槽位 + 候选模块表

### Slot A：base（底座支撑）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| five_star_caster | S1 (parent) | star_base L75-L118 / caster loop L397-L406 | eligible | 五辐星 + 双轮 caster + 黄 hub + 气压柱 |
| cross_caster | S4 | cross_base L75-L118 | eligible | 十字四臂 + 四 caster |
| fixed_pedestal | S2 | L66-L100 | eligible | 单立柱 + 加重圆盘脚（无轮） |
| four_leg_frame | S3 | leg L92-L115 / foot L118-L127 | eligible | 四斜腿框 + 橡胶脚（无轮） |

### Slot B：backrest-mechanism（靠背机构）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| fixed_stalk | S1 (parent) | — (0 joint, stalk 视觉) | eligible | 靠背刚性挂在 stalk 上，无 recline 关节 |
| reclining_backrest | S6 | `seat_to_backrest` REVOLUTE −Y, L465-L475 | eligible | 靠背独立成 part，座后铰接后仰 |
| split_headrest_tilt | S7 | `headrest_tilt` REVOLUTE +Y, L515-L527 | eligible | 下背 + 独立上头托，顶 tilt REVOLUTE |
| footrest_legrest | S8 | `legrest_hinge` REVOLUTE −Y, L640-L650 | eligible | 座前腿托上摆成近平躺 |

> **single-candidate slot degrade**：无（A=4, B=4）。脊柱关节（seat_lift + 2 arm_swing）保证每个组合 ≥1 非 fixed joint，即使 B=fixed_stalk。

## 槽位图（slot graph）
```
 [Slot A base] ──► gas_column ─seat_lift(PRISM +Z)─► seat
                                                       ├─ arm_swing_L / arm_swing_R (REVOLUTE +Z, 固定 2)
                                                       └─ [Slot B backrest] (fixed / recline REV / +headrest / +legrest)
   five_star_caster 时: base 含 [multiplicity] caster_{i} 等角环
```
接口：base 顶 → 气压柱 → seat_lift PRISMATIC；靠背机构锚在 seat 后缘（recline/headrest/legrest 各自的 REVOLUTE）。

## 每槽位 Module Emits / Interfaces
- **Slot A**：emits 底座 part（星辐 loop / 十字 / 立柱 / 四腿）；five_star/cross 含 `caster_{i}` loop；upstream = 顶接气压柱。
- **Slot B**：fixed_stalk emits 刚性靠背视觉（0 joint）；recline/headrest/legrest emits 独立 part + 各自 REVOLUTE。
- **Multiplicity**：`caster_{i}` 等角（θ=2πi/N+90°）FIXED 轮，仅 five_star_caster base 暴露。

## 参数范围汇总
| 参数 | 类型 | 取值 | 约束 | 来源 |
|---|---|---|---|---|
| base | enum | five_star_caster / cross_caster / fixed_pedestal / four_leg_frame | choice | Slot A |
| backrest_mechanism | enum | fixed_stalk / reclining_backrest / split_headrest_tilt / footrest_legrest | choice | Slot B |
| palette_style | enum | blue_vinyl_chrome / black_leather_chrome / white_clinical / teal_clinical（≥3） | palette only | S1-S8 |
| caster_count | int | {3,4,5}，N_range [3,6] | conditional multiplicity（仅 five_star_caster） | S5 |
| seat_h_scale / column_scale | float | [0.9,1.15] | independent clamp | S1 |
| (—) | constraint | 升降 seated 高度合理；caster 落地 | inequality | S1 |

## Multiplicity / Copy Logic
- **count_param**：`caster_count`（星辐 base 的脚轮数）。
- **N_range**：[3, 6]；采样 {3,4,5}（parent=5）。
- **copied object**：辐臂 + 双轮 caster（shared helper）。
- **naming**：`caster_{i}` / `spoke_{i}`，等角 θ=2πi/N+90°。
- **joint policy**：全 FIXED（装饰轮，无独立 joint）。**conditional**：仅 base=five_star_caster（或 cross_caster=4）暴露；pedestal/four_leg base 无 caster 轴。
- 扶手数固定 2，**不是 multiplicity 轴**（真实手术椅恒 2 扶手）。

## 拓扑多样性审计
- A(4) × B(4) = **16** 纯 slot；含 caster N 条件轴 → base 侧 7 个 distinct base-tuple × B(4) = **28** distinct。
- procedural_first：采 A/B 均匀 → 若 A=five_star/cross 则采 caster_count → palette → 连续 scale。
- 兼容矩阵：caster_count 仅 caster-type base；其余两两兼容。
- Topology target ~28；远超 10。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## Validator
- 脊柱 seat_lift PRISMATIC + 2 arm_swing REVOLUTE 恒在（保证 B=fixed_stalk 也有非 fixed joint）。
- caster_count 仅 caster base 暴露；pedestal/four_leg 不出 caster。
- 扶手恒 2，不被当轴。
- 连续 scale clamp；inequality 在 resolve_config。
- element-scoped allow_overlap（caster↔hub、cushion↔frame）。

## Reject cases
- 把座盆改成平躺多段床 → 出类目（surgical_bed）。
- seat_lift 降为 FIXED 且 B=fixed_stalk → 0 非 fixed joint，拒收。
- 扶手数当 multiplicity 轴 → 出真实椅类词汇表。
- caster_count 用在无轮 base → 非法组合。
- palette/scale 当 candidate → 非结构差异。

## 与相邻类别的边界
- surgical_bed：平躺多段台（非坐姿气压椅）。
- 办公转椅：无气压手术升降 + 翼扶手摆动语义。
- 裸 lab stool：无靠背/扶手/升降机构。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |

## Module Source Index
| source_id | slot | module | record_id |
|---|---|---|---|
| S1 | A/B | five_star_caster / fixed_stalk (parent) | rec_build-...-surg_..._821a91c4 |
| S2 | A | fixed_pedestal | rec_surgical_chair_var_pedestal |
| S3 | A | four_leg_frame | rec_surgical_chair_var_fourleg |
| S4 | A | cross_caster | rec_surgical_chair_var_xcaster |
| S5 | multiplicity | caster_count N=3 | rec_surgical_chair_var_caster3 |
| S6 | B | reclining_backrest | rec_surgical_chair_var_recline |
| S7 | B | split_headrest_tilt | rec_surgical_chair_var_headrest |
| S8 | B | footrest_legrest | rec_surgical_chair_var_legrest |
