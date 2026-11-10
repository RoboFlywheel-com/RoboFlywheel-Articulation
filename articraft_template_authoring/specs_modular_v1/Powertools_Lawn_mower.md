# Modular Spec — Powertools / Lawn mower

## 元信息
| 项 | 值 |
|---|---|
| slug | `lawn_mower` |
| template path | `agent/templates/Powertools_Lawn_mower.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（3 个结构 slot：power-unit × grass-collection × handle；外加 1 根 multiplicity 轴 `wheel_count`） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（1 parent + 8 variants） |
| read_count | 9 |

**共性骨架**：root `deck`（Lathe 罩壳），`engine` FIXED，`blade` CONTINUOUS，4 轮 CONTINUOUS（`WHEEL_SPECS` 表 loop），`handlebar` REVOLUTE 折叠。共 6 非 fixed 关节。`build_object_model` ~L66-L450，`_mirror_y` ~L62。LatheGeometry 罩壳 + WheelGeometry/TireGeometry + tube_from_spline handle。

## 核心身份
手推式汽油割草机（walk-behind push mower）。识别 = **轮 CONTINUOUS + 立式 blade 自转 + handle 折叠**。不该混入：骑乘式割草机、滚筒(reel)割草机、机器人割草机、打草机/trimmer、通用手推车。

## 槽位 + 候选模块表

### Slot A：power-unit（动力单元）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| gas_engine | parent | build L66-L260（engine block + recoil + 油箱） | eligible | 单缸汽油机 + 反冲启动 |
| corded_electric | rec_lawn_mower_var_electric | build L65-L300 | eligible | 低矮电机罩 + 拖线 |
| battery_brushless | rec_lawn_mower_var_battery | build L67-L300 | eligible | 可拆电池包 + 无刷电机座 |

### Slot B：grass-collection（集草机构）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| side_discharge | rec_lawn_mower_var_sidechute | `_build_curved_panel` L71-L144 + build | eligible | 侧排导流罩 + 翻转 deflector（REVOLUTE） |
| rear_bag | rec_lawn_mower_var_rearbag | build L69-L560（后袋 + 后门 flap REVOLUTE） | eligible | 后集草袋 + 弹簧后门 |
| mulch_plug | rec_lawn_mower_var_mulchplug | `_curved_shell_segment` L170-... + build L74 | eligible | 后口塞 + 盖板（碎草回流） |

> parent 本身无袋（侧排/碎草基线）；本 slot 候选取自三个 collection 变体。

### Slot C：handle（推把）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| u_handle_fold | parent | build（U 把 + `handlebar` REVOLUTE 折叠） | eligible | U 形把，单 fold REVOLUTE |
| telescoping_2seg | rec_lawn_mower_var_telehandle | build L76-L530 | eligible | 下管 + 上滑管，高度 pivot（保留 fold REVOLUTE） |
| loop_bullhorn | rec_lawn_mower_var_loophandle | build L68-L475 | eligible | 单 loop 牛角把（保留 fold REVOLUTE） |

> **single-candidate slot degrade**：无（每槽 3）。

## 槽位图（slot graph）
```
 deck (root)
   ├─ [Slot A power-unit] engine/motor/battery → blade (CONTINUOUS 立轴)
   ├─ [multiplicity] {pos}_wheel_{i} (CONTINUOUS, WHEEL_SPECS loop)
   ├─ [Slot B grass-collection] side-chute(REV deflector) / rear-bag(REV door) / mulch-plug
   └─ [Slot C handle] U-fold(REV) / telescoping / loop, 锚 deck 后裙
```

## 每槽位 Module Emits / Interfaces
- **Slot A**：emits 动力罩 + blade 立轴 CONTINUOUS（汽油/电/电池）；blade 自转恒在。
- **Slot B**：side-chute emits 导流罩 + deflector REVOLUTE；rear-bag emits 袋架 + 后门 REVOLUTE；mulch-plug emits 后口塞（FIXED）。
- **Slot C**：handle 折叠 REVOLUTE 恒在；telescoping 加高度 pivot；loop 改把形。
- **Multiplicity**：`{pos}_wheel_{i}` 经 `WHEEL_SPECS` 表 loop，每轮 CONTINUOUS。

## 参数范围汇总
| 参数 | 类型 | 取值 | 约束 | 来源 |
|---|---|---|---|---|
| power_unit | enum | gas_engine / corded_electric / battery_brushless | choice | Slot A |
| grass_collection | enum | side_discharge / rear_bag / mulch_plug | choice | Slot B |
| handle | enum | u_handle_fold / telescoping_2seg / loop_bullhorn | choice | Slot C |
| palette_style | enum | orange / red / green / black（≥3，按真实品牌） | palette only | S 材质 |
| wheel_count | int | {3,4}，N_range [3,4]（真实手推割草机仅 3/4） | multiplicity（WHEEL_SPECS loop） | 3wheel |
| deck_scale | float | [0.9,1.12] | independent clamp | parent |

## Multiplicity / Copy Logic
- **count_param**：`wheel_count`（轮数，WHEEL_SPECS 表长）。
- **N_range**：**[3, 4]**（真实手推割草机词汇；不臆造更高 N）。采样 {3,4}（parent=4，3wheel=前 caster + 后 2 轮）。
- **copied object**：轮（WheelGeometry+TireGeometry），WHEEL_SPECS 单一来源。
- **joint policy**：每轮 CONTINUOUS 横轴；N=3 用单前 caster（中线）+ 2 后轮。

## 拓扑多样性审计
- A(3) × B(3) × C(3) = **27** 纯 slot；× wheel N{3,4} = **54** distinct。
- procedural_first：采 A/B/C → 采 wheel_count → palette → 连续 scale。
- 兼容矩阵：三槽两两独立兼容；wheel_count 与任意组合兼容。
- Topology target ~54；远超 10。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## Validator
- blade CONTINUOUS + ≥1 轮 CONTINUOUS + handle fold REVOLUTE 恒在。
- wheel_count ∈ {3,4}，WHEEL_SPECS 单一来源 loop（3wheel 前 caster 中线）。
- side-chute deflector / rear-bag door 的 REVOLUTE 正确。
- element-scoped allow_overlap（轮↔轴、handle↔deck）。
- 连续 scale clamp。

## Reject cases
- 骑乘/滚筒/机器人割草机 → 出类目。
- wheel_count > 4 → 离开手推割草机词汇。
- blade 或全部轮降为 FIXED → 0 关键关节。
- deck 形当结构 candidate（罩壳是连续参数）→ 非结构差异。
- palette 当 candidate → 非结构差异。

## 与相邻类别的边界
- 骑乘式割草机：带座椅/方向盘，非手推。
- 滚筒(reel)割草机：水平刀辊，非立式 blade。
- 打草机/trimmer：手持线头，无 deck/轮。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |

## Module Source Index
| source_id | slot | module | record_id |
|---|---|---|---|
| S1 | A/C | gas_engine / u_handle_fold (parent) | rec_model-a-gas-powered-...-mower_..._adebd312 |
| S2 | A | corded_electric | rec_lawn_mower_var_electric |
| S3 | A | battery_brushless | rec_lawn_mower_var_battery |
| S4 | B | side_discharge | rec_lawn_mower_var_sidechute |
| S5 | B | rear_bag | rec_lawn_mower_var_rearbag |
| S6 | B | mulch_plug | rec_lawn_mower_var_mulchplug |
| S7 | C | telescoping_2seg | rec_lawn_mower_var_telehandle |
| S8 | C | loop_bullhorn | rec_lawn_mower_var_loophandle |
| S9 | multiplicity | wheel_count N=3 | rec_lawn_mower_var_3wheel |
