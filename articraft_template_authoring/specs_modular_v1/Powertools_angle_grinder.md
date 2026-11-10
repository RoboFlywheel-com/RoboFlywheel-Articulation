# Modular Spec — Powertools / angle grinder

## 元信息
| 项 | 值 |
|---|---|
| slug | `angle_grinder` |
| template path | `agent/templates/Powertools_angle_grinder.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（3 个结构 slot：disc-guard × switch × power-source；外加 1 根 multiplicity 轴 `handle_boss_count`） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 parent + 7 variants） |
| read_count | 8 |

**共性骨架**：root `body`，3 非 fixed 关节：`spindle_disc` CONTINUOUS（盘自转）+ `power_switch` PRISMATIC + `spindle_lock` PRISMATIC。`build_object_model` ~L40，vents loop `vent_slot_{i}`。LatheGeometry 罩壳 + LoftGeometry 齿轮头 + tube_from_spline 线。parent **无护罩**（结构空格）。

## 核心身份
手持电动角磨机（handheld angle grinder）。识别 = **磨盘 CONTINUOUS 自转**（护罩/开关/电池可增关节）。不该混入：直磨机/模具机、电锯、抛光机（无角传动头）、手持电钻（chuck 非磨盘）。

## 槽位 + 候选模块表

### Slot A：disc-guard（磨盘/护罩）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| bare_disc | parent | build L40-L300（无护罩） | eligible | 裸磨盘（盘 CONTINUOUS） |
| half_shroud_guard | rec_angle_grinder_var_guard | build L43-L360（`guard_band` + `guard_to_body` REVOLUTE z） | eligible | 半弧护罩，绕主轴 REVOLUTE 旋转挡屑（多 1 关节） |
| cutting_wheel_guard | rec_angle_grinder_var_guardcut | `_build_arc_wall` L50-L75 + `_build_annular_sector` L76-L105 | eligible | 薄切割片 + 窄深护罩（REVOLUTE） |

### Slot B：switch（开关机构）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| top_slide | parent | build（`power_switch` PRISMATIC） | eligible | 顶部滑板开关（PRISMATIC） |
| deadman_trigger | rec_angle_grinder_var_trigger | build L40-L318（`trigger_paddle` + `trigger_pivot` REVOLUTE） | eligible | 握把下死人扳机（REVOLUTE） |
| top_rocker | rec_angle_grinder_var_rocker | build L43-L339（`rocker_switch` + `rocker_pivot` REVOLUTE） | eligible | 顶部跷板开关（REVOLUTE） |

### Slot C：power-source（电源/尾端）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| corded | parent | build（尾端 strain-relief boot + 线） | eligible | 有线 + 应力保护套 |
| cordless | rec_angle_grinder_var_cordless | build L39-L362（`battery_pack` + `battery_release` PRISMATIC） | eligible | 尾端滑入电池包（PRISMATIC 退出） |

> **single-candidate slot degrade（Slot C=2）**：已记降级理由 —— 单参考图只支持 corded/cordless 两种结构不同尾端家族（机身罩壳形态属连续参数，不单列）；两候选 part 树不同（线尾 vs 电池座 + PRISMATIC），满足 ≥2 下限。

## 槽位图（slot graph）
```
 body (root)
   ├─ spindle ─spindle_disc(CONTINUOUS)─► [Slot A disc] ── guard(REVOLUTE z, half/cutting)
   ├─ [Slot B switch] slide(PRISM) / trigger(REV) / rocker(REV)
   ├─ spindle_lock (PRISMATIC)
   ├─ [Slot C power] corded boot / cordless battery(PRISMATIC)
   └─ [multiplicity] handle_boss_{i} (FIXED 螺纹座, 1/2/3)
```

## 每槽位 Module Emits / Interfaces
- **Slot A**：bare 无护罩；guard/cutting emits `guard_band` + `guard_to_body` REVOLUTE（绕主轴），盘仍 CONTINUOUS。
- **Slot B**：slide(PRISMATIC) / trigger(REVOLUTE) / rocker(REVOLUTE) 互斥三选一。
- **Slot C**：corded emits 线尾；cordless emits 电池座 + `battery_release` PRISMATIC。
- **Multiplicity**：`handle_boss_{i}` 螺纹侧把座（shared helper，FIXED），齿轮头侧/侧+顶等位。

## 参数范围汇总
| 参数 | 类型 | 取值 | 约束 | 来源 |
|---|---|---|---|---|
| disc_guard | enum | bare_disc / half_shroud_guard / cutting_wheel_guard | choice | Slot A |
| switch | enum | top_slide / deadman_trigger / top_rocker | choice | Slot B |
| power_source | enum | corded / cordless | choice | Slot C |
| palette_style | enum | yellow_black / teal / red / green（≥3，按真实品牌） | palette only | S 材质 |
| handle_boss_count | int | {1,2,3}，N_range [1,3] | multiplicity（FIXED 螺纹座 loop） | handle2/handle3 |
| body_scale | float | [0.9,1.12] | independent clamp | parent |

## Multiplicity / Copy Logic
- **count_param**：`handle_boss_count`（侧把螺纹座数）。
- **N_range**：[1, 3]；采样 {1,2,3}（parent=1）。
- **copied object**：螺纹侧把座（`_add_handle_boss_visuals` shared helper）。
- **naming**：`handle_boss_{i}`，齿轮头周向（+Y / −Y / 顶）。
- **joint policy**：全 FIXED（螺纹座不动）。
- 选 side-handle mount 作多重性轴（比 vent 数更有结构意义；vent 已 loop，归 N_range 不单列）。

## 拓扑多样性审计
- A(3) × B(3) × C(2) = **18** 纯 slot；× handle N{1,2,3} = **54** distinct。
- procedural_first：采 A/B/C → 采 handle_boss_count → palette → 连续 scale。
- 兼容矩阵：三槽 + N 两两独立兼容。
- Topology target ~54；远超 10。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## Validator
- `spindle_disc` CONTINUOUS 恒在（每组合 ≥1 非 fixed）；guard/cutting 加 REVOLUTE。
- switch 三选一互斥；各自 joint type 正确。
- cordless `battery_release` PRISMATIC。
- handle_boss_{i} FIXED loop（element-scoped allow_overlap boss↔head）。
- spindle_lock 基线保留；连续 scale clamp。

## Reject cases
- 磨盘 CONTINUOUS 降为 FIXED → 0 自转，拒收。
- 当成电钻（chuck）/直磨机（无角头）→ 出类目。
- 机身罩壳形当 candidate（连续参数）→ 非结构差异。
- vent 数刷成多余变体 → 归 template N_range，不单列。

## 与相邻类别的边界
- 手持电钻：keyless chuck（非磨盘 + 角传动头）。
- 直磨机/模具机：直轴小头，无角传动。
- 电圆锯：往复/圆锯片 + 底板，结构不同。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |

## Module Source Index
| source_id | slot | module | record_id |
|---|---|---|---|
| S1 | A/B/C | bare_disc / top_slide / corded (parent) | rec_model-a-compact-electric-...-grinder_..._28a8a3ef |
| S2 | A | half_shroud_guard | rec_angle_grinder_var_guard |
| S3 | A | cutting_wheel_guard | rec_angle_grinder_var_guardcut |
| S4 | B | deadman_trigger | rec_angle_grinder_var_trigger |
| S5 | B | top_rocker | rec_angle_grinder_var_rocker |
| S6 | C | cordless | rec_angle_grinder_var_cordless |
| S7/S8 | multiplicity | handle_boss_count N=2/3 | rec_angle_grinder_var_handle{2,3} |
