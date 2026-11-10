# Modular Spec — Powertools / drill

## 元信息
| 项 | 值 |
|---|---|
| slug | `cordless_drill` |
| template path | `agent/templates/Powertools_drill.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（3 个结构 slot：body-form × battery-mount × bit-style；外加 2 根 count-only multiplicity 子轴：chuck-jaws、clutch-detents） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7（1 parent + 6 variants） |
| read_count | 7 |

| source_id | record_id | 结构家族 |
|---|---|---|
| S1 | rec_build-...-drill_...611bf0fa（parent，pistol-grip） | 手枪握把；keyless chuck CONTINUOUS + clutch + trigger + selector + battery；jaws N=3 / detents N=12 |
| S2 | rec_cordless_drill_var_rtangle | 直角 L 形机身 |
| S3 | rec_cordless_drill_var_thandle | 紧凑 T 形机身 |
| S4 | rec_cordless_drill_var_podbatt | 扁平滑入 pod 电池底 |
| S5 | rec_cordless_drill_var_jaw2 | chuck 2 爪 |
| S6 | rec_cordless_drill_var_clutch16 | 离合 16 档 |
| S7 | rec_cordless_drill_var_clutch20 | 离合 20 档 |

**共性骨架（脊柱）**：root `housing` + 5 非 fixed 关节恒在：`housing_to_chuck` **CONTINUOUS**（chuck 整体单刚体旋转）+ clutch_collar REVOLUTE + trigger REVOLUTE + selector PRISMATIC + battery_pack PRISMATIC。LatheGeometry（collar/chuck nose / optional twist bit tip）, KnobGeometry（chuck 滚花）, ExtrudeGeometry（trigger）, CadQuery（housing）。chuck jaws / optional twist bit / clutch detents / collar ribs / vents 均已 loop-emit。

## 核心身份
手持充电钻 / 起子（cordless drill-driver）。识别 = **keyless chuck CONTINUOUS 自转 + trigger/clutch/battery 机构**。不该混入：车床卡盘（4 爪独立卡盘）、冲击起子（hex 套筒非 chuck）、锤钻（功能差异但非结构家族变更）、手动螺丝刀（无机构）。

## 槽位 + 候选模块表

### Slot A：body-form（机身/握把拓扑）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| pistol_grip | S1 (parent) | `_housing_solids` L42-L98 | eligible | 手枪握把 + 水平钻轴 |
| right_angle | S2 | L-housing L63-L151 | eligible | 握把下沉、钻轴前端垂直，L 形直角布局 |
| t_handle_compact | S3 | T-housing L46-L112 | eligible | 握把居中于电机下方，短粗 T 形 |

### Slot B：battery-mount（电池接口）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| slide_on_stick | S1 (parent) | battery L307-L350 | eligible | 高 stick 电池包从握把脚后向滑入轨 |
| flat_pod_slide | S4 | 燕尾 foot L64-L85 / pod L317-L390 | eligible | 扁平 pod 电池从握把下水平滑入燕尾 |

> **single-candidate slot degrade**：battery-mount 仅 2 候选 —— 已记降级理由：真实手持充电钻的电池接口家族在样本里只有 stick-vs-pod 两种结构不同形态（4 爪/keyed 等属 chuck 轴，不在此槽）；两候选 part 树不同（高 stick 轨 vs 扁 pod 燕尾），满足 ≥2 结构差异下限。

### Slot C：bit-style（夹头前端附件）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none | template baseline | `_build_chuck` | eligible | 仅 keyless chuck 与夹爪，无外露钻杆 |
| twist_bit | template extension | `_build_chuck` | eligible | 独立 steel 麻花钻头：芯杆 + 锥尖 + 双螺旋排屑纹，刚性挂在 chuck 内并随 CONTINUOUS chuck 一起转 |

## 槽位图（slot graph）
```
 housing (root, [Slot A body-form])
   ├─ housing_to_chuck (CONTINUOUS) ─► chuck ── [Slot C bit-style] twist_bit_* + [multiplicity N1] jaw_{i} (等角, rigid 在 chuck 内)
   ├─ clutch_collar (REVOLUTE) ── [multiplicity N2] detent tick_{i} + rib_{i} (loop, 装饰)
   ├─ trigger (REVOLUTE) / selector (PRISMATIC)
   └─ [Slot B battery-mount] battery_pack (PRISMATIC: stick 轨 / pod 燕尾)
```

## 每槽位 Module Emits / Interfaces
- **Slot A**：emits 机身/握把 CadQuery 实体（手枪 / 直角 / T）；不改 5 关节集合，仅重排几何与钻轴朝向。
- **Slot B**：emits 电池座接口（高 stick 轨 / 扁 pod 燕尾）+ battery PRISMATIC origin 锚在接口面。
- **Multiplicity N1**（chuck jaws）：`jaw_{i}` box 等角（2πi/N）rigid 在 chuck 单刚体内（无 per-jaw 关节）；loop 已存在，仅改 count。
- **Multiplicity N2**（clutch detents）：collar 周向 detent tick + grip rib loop；改 count + 按比例改 rib 数；纯装饰，挂 clutch_collar。

## 参数范围汇总
| 参数 | 类型 | 取值 | 约束 | 来源 |
|---|---|---|---|---|
| body_form | enum | pistol_grip / right_angle / t_handle_compact | choice | Slot A |
| battery_mount | enum | slide_on_stick / flat_pod_slide | choice | Slot B |
| bit_style | enum | none / twist_bit | choice | Slot C |
| palette_style | enum | lime_green / yellow_black / blue / red / teal（≥3，按真实品牌色） | palette only | S1-S7 |
| jaw_count | int | {2,3}，N_range [2,3]（4 爪=车床，出类目） | multiplicity（rigid in chuck） | S5 |
| detent_count | int | {12,16,20}，N_range [10,24] | multiplicity（collar 装饰） | S6/S7 |
| body_scale / chuck_scale | float | [0.9,1.15] | independent clamp | S1 |

## Multiplicity / Copy Logic
- **两根 count-only 子轴**（两个 loop 在 parent 已存在，仅改 count）：
  - `jaw_count` ∈ {2,3}，N_range [2,3]：copied = `jaw_{i}` box，等角 2πi/N，**rigid 在 chuck 单刚体**（chuck 整体 CONTINUOUS 自转，无 per-jaw 关节）；4 爪卡盘是车床词汇，excluded。
  - `detent_count` ∈ {12,16,20}，N_range [10,24]：copied = 周向 detent tick + grip rib，等角，FIXED 装饰挂 clutch_collar；改 count 时 rib 数按比例同步。
- chuck CONTINUOUS、clutch/trigger/battery 关节在所有组合恒在。

## 拓扑多样性审计
- A(3) × B(2) = **6** 纯 slot；× jaw N{2,3} × detent N{12,16,20} = **36** distinct。
- procedural_first：采 A/B → 采 jaw_count / detent_count → palette → 连续 scale。
- 兼容矩阵：四轴两两独立兼容（jaw 与 body/battery/detent 无冲突）。
- Topology target ~36；远超 10。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## Validator
- chuck `housing_to_chuck` CONTINUOUS + clutch/trigger/selector/battery 关节恒在。
- jaw_count ∈ {2,3}（拒 4）；jaws rigid 在 chuck（无独立关节）。
- detent_count 改动同步 rib 数。
- 连续 scale clamp；battery 接口 origin 锚在接触面。
- element-scoped allow_overlap（jaw↔chuck、battery↔housing 轨）。

## Reject cases
- 4 爪独立卡盘 → 车床词汇，出类目。
- keyed chuck（无参考图）→ 暂不引入。
- chuck 关节降为 FIXED → 0 自转，拒收。
- jaws 给每爪独立关节 → 与单刚体 chuck 契约冲突。
- palette/scale 当 candidate → 非结构差异。

## 与相邻类别的边界
- 车床卡盘：独立可调 4 爪 + 无手持机身。
- 冲击起子：hex 快换套筒（非 keyless chuck）。
- 锤钻：功能模式差异，非结构家族（折入连续参数，不单列）。
- 手动螺丝刀：无机构。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |

## Module Source Index
| source_id | slot | module | record_id |
|---|---|---|---|
| S1 | A/B | pistol_grip / slide_on_stick (parent) | rec_build-...-drill_..._611bf0fa |
| S2 | A | right_angle | rec_cordless_drill_var_rtangle |
| S3 | A | t_handle_compact | rec_cordless_drill_var_thandle |
| S4 | B | flat_pod_slide | rec_cordless_drill_var_podbatt |
| S5 | multiplicity N1 | jaw_count N=2 | rec_cordless_drill_var_jaw2 |
| S6 | multiplicity N2 | detent_count N=16 | rec_cordless_drill_var_clutch16 |
| S7 | multiplicity N2 | detent_count N=20 | rec_cordless_drill_var_clutch20 |
