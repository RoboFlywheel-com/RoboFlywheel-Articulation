# Modular Spec — Science / Syringe

## 元信息
| 项 | 值 |
|---|---|
| slug | `syringe` |
| template path | `agent/templates/Science_Syringe.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（4 个并列 visual-swap slot：tip-hub × flange × plunger-rod × barrel-form；外加 1 根 multiplicity 轴 `tick_count`） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11（1 parent + 10 variants） |
| read_count | 11 |

**共性骨架（11 个样本一致）**：固定 2-part 骨架 root `barrel_assembly` + child `plunger`，唯一非 fixed 关节 `barrel_to_plunger` **PRISMATIC**（恒=1）。统一躺姿 rest（barrel 轴→world +Y，针→−Y）。所以四个 slot 都是这 2 个 part 上的 **visual-element swap，非 part 替换**。共享 helper：`_barrel_shell`(~L92) / `_graduation_marks`(~L112) / `_finger_flanges`(~L134) / `_hub`(~L154) / `_needle`(~L189) / `_plunger_rod`(~L234)。CadQuery revolve/boolean —— 无 boxy 降级。

## 核心身份
医用注射器（hypodermic syringe）。识别 = **`barrel_to_plunger` PRISMATIC 推拉**（hero joint，所有变体保留）。不该混入：药瓶/滴管（无活塞滑动）、笔式注射器（结构不同）、移液枪（带按钮机构）。

## 槽位 + 候选模块表

### Slot A：tip / hub（针座/出口）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| luer_lock_needle | parent | `_hub` L154-L188 + `_needle` L189-L216 | eligible | 不锈钢 luer 锁针座 + 斜面针 |
| slip_tip | rec_syringe_var_sliptip | `_slip_tip_nozzle` L154-L178 + `_needle` L179-L209 | eligible | 一体滑头喷嘴（无独立金属座） |
| blunt_cannula | rec_syringe_var_bluntcan | `_cannula` L190-L226 | eligible | 钝头平口套管 |
| safety_shield | rec_syringe_var_safetysh | `_safety_shield` L226-L263 | eligible | 针外半透明保护套 |

### Slot B：flange（指托）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_wings | parent | `_finger_flanges` L134-L153 | eligible | 两片扁平翼 |
| ring_collar | rec_syringe_var_ringflng | `_thumb_collar` L134-L159 | eligible | 整圈环形拇指托 |
| ribbed_grip | rec_syringe_var_ribgrip | `_ergonomic_grip_flange` L135-L196 | eligible | 带凹槽/肋的人体工学翼 |

### Slot C：plunger-rod（活塞杆截面）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| plus_cross | parent | `_plunger_rod` L234-L249 | eligible | 十字肋杆 |
| flat_plate | rec_syringe_var_flatrod | `_plunger_rod` L234-L243 | eligible | 单片平板矩形杆 |

> **single-candidate slot degrade（Slot C=2）**：已记降级理由 —— 单参考图只支持 2 个真实结构不同的杆截面（十字 vs 平板）；不臆造第三种（solid_round 不在样本）。两候选 part 几何不同，满足 ≥2 下限。

### Slot D：barrel-form（筒身家族）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| straight_cylindrical | parent | `_barrel_shell` L92-L111 | eligible | 直筒 3mL |
| slim_insulin | rec_syringe_var_slimbody | `_barrel_shell` L96-L115 | eligible | 细长胰岛素筒（窄径长比） |
| wide_stepped | rec_syringe_var_widebody | `_barrel_shell` L102-L156 | eligible | 大容量阶梯宽筒 |

## 槽位图（slot graph）
```
 barrel_assembly (root)
   ├─ [Slot D barrel-form] _barrel_shell 几何家族
   ├─ [multiplicity] _graduation_marks 刻度 N（合并进单一 scale_marks 视觉, 无 joint）
   ├─ [Slot A tip/hub] 出口端 (luer/slip/blunt/shield)
   ├─ [Slot B flange] 尾端指托 (wings/ring/ribbed)
   └─ barrel_to_plunger (PRISMATIC) ─► plunger ── [Slot C plunger-rod] 杆截面
```

## 每槽位 Module Emits / Interfaces
- **Slot A**：emits 出口端 visual（hub+needle / slip nozzle / cannula / shield）挂 barrel_assembly +Y 端；不增关节。
- **Slot B**：emits 尾端指托 visual；不增关节。
- **Slot C**：emits plunger 杆 visual（十字 / 平板）；plunger 仍单 PRISMATIC child。
- **Slot D**：emits barrel 壳几何（直/细/宽阶梯）；barrel 内径/长由 barrel_form equation 派生。
- **Multiplicity**：`_graduation_marks` 刻度循环并入单一 `scale_marks` 视觉（**无 joint** 装饰），改 n 即可。

## 参数范围汇总
| 参数 | 类型 | 取值 | 约束 | 来源 |
|---|---|---|---|---|
| tip_hub | enum | luer_lock_needle / slip_tip / blunt_cannula / safety_shield | choice | Slot A |
| flange | enum | flat_wings / ring_collar / ribbed_grip | choice | Slot B |
| plunger_rod | enum | plus_cross / flat_plate | choice | Slot C |
| barrel_form | enum | straight_cylindrical / slim_insulin / wide_stepped | choice；驱动 barrel_radius/length equation | Slot D |
| palette_style | enum | clear_blue_plunger / amber_body / orange_cap / all_white / teal_clinical / insulin_clear（≥3） | palette only | S 材质 |
| tick_count | int | {10,16,24}，N_range [6,40] | multiplicity（merged scale_marks, no joint） | ticks10/24 |
| barrel_r / barrel_len / gasket / liquid | float | derived from barrel_form | equation；gasket 全程保留、针 protrusion ≥0 | parent |

## Multiplicity / Copy Logic
- **count_param**：`tick_count`（刻度线数）。
- **N_range**：[6, 40]；采样 {10,16,24}（parent=16），小 N 偏重。
- **copied object**：单条刻度 tick box（`_graduation_marks` 循环），等距沿筒轴。
- **joint policy**：全部并入 **单一 `scale_marks` 非 joint 装饰视觉**（不拆成 FIXED part）；major-tick-每五的规则不变。

## 拓扑多样性审计
- A(4) × B(3) × C(2) × D(3) = **72** 纯 slot 组合；× tick N 不增 part-topology 但增视觉多样。
- procedural_first：均匀采 A/B/C/D → barrel_form 派生 barrel 尺寸 → 加权采 tick_count → palette → 连续 scale。
- 兼容矩阵：四 slot 两两独立兼容；plunger PRISMATIC 在所有组合恒在。
- Topology target ~72；远超 10。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## Validator
- `barrel_to_plunger` PRISMATIC 在所有 seed 恒在（hero joint）。
- Slot C 2 候选有降级理由；其余槽 ≥3。
- tick_count 改动只改 merged scale_marks 视觉（无 joint）。
- barrel 尺寸由 barrel_form equation 派生（gasket 保留行程、针 protrusion ≥0 inequality）。
- element-scoped allow_overlap（plunger↔barrel、gasket↔barrel）。

## Reject cases
- plunger PRISMATIC 降为 FIXED → 0 关键关节，拒收。
- 把刻度拆成 N 个 FIXED part → 违反"装饰内联"。
- 臆造第三种 plunger 截面塞 Slot C → 无样本支撑。
- palette / 纯缩放当 candidate（slim/wide 是 form-family 非纯缩放）→ 非结构差异。

## 与相邻类别的边界
- 药瓶/滴管：无活塞滑动机构。
- 笔式注射器/胰岛素笔：旋钮剂量机构，结构不同。
- 移液枪：按钮 + 吸头弹射，机构不同。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |

## Module Source Index
| source_id | slot | module | record_id |
|---|---|---|---|
| S1 | A/B/C/D | luer / flat_wings / plus_cross / straight (parent) | rec_build-...-syri_..._042137c8 |
| S2 | A | slip_tip | rec_syringe_var_sliptip |
| S3 | A | blunt_cannula | rec_syringe_var_bluntcan |
| S4 | A | safety_shield | rec_syringe_var_safetysh |
| S5 | B | ring_collar | rec_syringe_var_ringflng |
| S6 | B | ribbed_grip | rec_syringe_var_ribgrip |
| S7 | C | flat_plate | rec_syringe_var_flatrod |
| S8 | D | slim_insulin | rec_syringe_var_slimbody |
| S9 | D | wide_stepped | rec_syringe_var_widebody |
| S10/S11 | multiplicity | tick_count N=10/24 | rec_syringe_var_ticks{10,24} |
