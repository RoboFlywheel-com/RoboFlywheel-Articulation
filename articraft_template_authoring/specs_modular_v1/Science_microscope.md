# Modular Spec — Science / microscope

## 元信息
| 项 | 值 |
|---|---|
| slug | `microscope` |
| template path | `agent/templates/Science_microscope.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（3 个并列结构 slot：head × illumination × focus-stage；外加 1 根 multiplicity 轴 `objective_count`） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10（1 parent + 9 variants） |
| read_count | 10 |

| source_id | record_id | 结构家族 |
|---|---|---|
| S1 | rec_build-...-micr_20260609_183637_825621_5f8b9008（parent） | 单目斜筒 + sub-stage 聚光灯 + 侧旋钮垂直 stage；objectives N=3 |
| S2 | rec_microscope_var_binoc | 双目头 |
| S3 | rec_microscope_var_vtube | 垂直直筒单目 |
| S4 | rec_microscope_var_mirror | 反光镜照明（fork 上 tilt REVOLUTE） |
| S5 | rec_microscope_var_leddisc | LED 圆盘底照明 |
| S6 | rec_microscope_var_dualknob | 粗/细同轴双旋钮 |
| S7 | rec_microscope_var_xystage | 机械 X/Y 平移载物台 |
| S8/S9/S10 | rec_microscope_var_obj{2,4,6} | objective N=2/4/6 |

**共性骨架**：刚性 root `base`（foot + 倾斜 arm + head housing），光轴在 X=0，arm 后置 +X。恒在 3 非 fixed 关节：`head_to_nosepiece` CONTINUOUS（转盘）+ 垂直 stage focus PRISMATIC + 侧 focus knob CONTINUOUS。Lathe/loft/CadQuery（turret cone / tapered barrels / arm extrude / lofted foot）—— 无 boxy 降级。objectives 已 loop-emit（`OBJ_LENGTHS`/`OBJ_ANGLES_DEG`，120° 等角）。

## 核心身份
复式光学显微镜（compound optical microscope）：转盘物镜 + 调焦 + 载物台。识别 = **nosepiece 转盘 CONTINUOUS + 调焦关节**。不该混入：望远镜（无转盘物镜 + 载物台）、放大镜（无机构）、相机三脚架。

## 槽位 + 候选模块表

### Slot A：head / eyepiece（观察头）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| monocular_inclined | S1 (parent) | L147-L194 | eligible | 单目 40° 斜筒 |
| binocular_head | S2 | L187-L241（+helper L72-L102） | eligible | 双平行斜目筒（加宽头座） |
| vertical_straight | S3 | L148-L195 | eligible | 垂直直立单目筒 |

### Slot B：illumination（照明 / 台下）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| condenser_lamp | S1 (parent) | L366-L404 | eligible | 圆柱聚光灯柱 |
| tilting_mirror | S4 | fork L385-L449 / mirror L456-L520 | eligible | 叉架上的圆反光镜，`fork_to_mirror` REVOLUTE 绕 Y（多 1 活动关节） |
| led_disc | S5 | L367-L420 | eligible | 嵌入底座的扁 LED 圆盘 |

### Slot C：focus / stage（调焦 + 载物台机构）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| side_coaxial_knob_vertical_stage | S1 (parent) | stage L286-L360 / knob L411-L472 | eligible | 侧同轴旋钮 + 垂直升降 stage PRISMATIC |
| dual_coarse_fine_knob | S6 | L470-L579 | eligible | 每侧粗 + 细同心双盘（2 CONTINUOUS + 1 PRISMATIC） |
| mechanical_xy_stage | S7 | stage FIXED L361-L367 / XY PRISM L374-L493 / drive knobs L503-L542 | eligible | X/Y 平移载物台滑架（2 PRISMATIC + 2 旋钮 REVOLUTE） |

> **single-candidate slot degrade**：无（每槽 3）。

## 槽位图（slot graph）
```
 base (root: foot + 倾斜 arm + head housing, 光轴 X=0)
   ├─ [Slot A head] arm 顶筒 (mono斜 / bino / vert)
   ├─ head ─head_to_nosepiece(CONTINUOUS)─► nosepiece_turret ── [multiplicity] objective_{i} (120/60/90°等角, rigid)
   ├─ [Slot C focus/stage] 侧旋钮 + stage PRISMATIC（或 dual knob / XY 平移）
   └─ [Slot B illumination] 台下 (condenser / mirror REV / LED disc)
```
接口：nosepiece 转盘 CONTINUOUS 单关节带所有物镜；stage 调焦 PRISMATIC 沿光轴；mirror tilt / XY stage 各自附加关节。

## 每槽位 Module Emits / Interfaces
- **Slot A**：emits 目镜头筒（单/双/直）；无新关节（光学头刚性）。
- **Slot B**：condenser/LED 为 FIXED 视觉；tilting_mirror emits fork + mirror + `fork_to_mirror` REVOLUTE。
- **Slot C**：parent 侧旋钮 CONTINUOUS + stage PRISMATIC；dual_knob 加第二同心旋钮；xy_stage 把垂直 stage 改 FIXED 并加 X/Y PRISMATIC 滑架 + 2 drive knob REVOLUTE。
- **Multiplicity**：`objective_{i}` 锥筒 + 色环（shared helper），等角 360/N rigid 挂转盘，单 CONTINUOUS 转盘关节（L231-L265）带动。

## 参数范围汇总
| 参数 | 类型 | 取值 | 约束 | 来源 |
|---|---|---|---|---|
| head | enum | monocular_inclined / binocular / vertical_straight | choice | Slot A |
| illumination | enum | condenser_lamp / tilting_mirror / led_disc | choice | Slot B |
| focus_stage | enum | side_coaxial / dual_coarse_fine / mechanical_xy | choice | Slot C |
| palette_style | enum | white_lab / black_chrome / graphite / blue_student / brushed_chrome_pro（≥3） | palette only | S1-S10 |
| objective_count | int | {2,3,4,6}，N_range [2,6] | multiplicity（360/N 等角） | S8-S10 |
| arm_h_scale / stage_scale | float | [0.9,1.15] | independent clamp | S1 |
| (—) | constraint | 物镜不互撞（角间距）、stage 在物镜下 | inequality | S1 |

## Multiplicity / Copy Logic
- **count_param**：`objective_count`（转盘物镜数）。
- **N_range**：[2, 6]；采样 {2,3,4,6}（parent=3）。
- **copied object**：锥形 chrome barrel + 彩色 band ring（shared helper）。
- **naming**：`objective_barrel_{i}` / `objective_ring_{i}`，等角 360/N。
- **joint policy**：全 rigid 挂在 nosepiece_turret 上，**单个 CONTINUOUS 转盘关节**带动（无 per-objective 关节）。N 变体只改 `OBJ_LENGTHS`/`OBJ_ANGLES_DEG`，须更新 run_tests 的物镜数断言。

## 拓扑多样性审计
- A(3) × B(3) × C(3) = **27** 纯 slot；× N{2,3,4,6} = **135** distinct。
- procedural_first：均匀采 A/B/C → 加权采 objective_count → palette → 连续 scale。
- 兼容矩阵：三槽两两独立兼容；N 与任意组合兼容。
- Topology target ~27 slot-distinct（× N）；远超 10。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## Validator
- nosepiece 转盘 CONTINUOUS + 调焦关节恒在。
- mirror/xy/dual 各自附加关节正确（mirror REVOLUTE、xy 2×PRISMATIC、dual 2×CONTINUOUS）。
- objective N 改动同步 run_tests 物镜数 + 等角扫掠 clearance。
- 连续 scale clamp；inequality（物镜互撞 / stage 位置）在 resolve_config。
- element-scoped allow_overlap（物镜↔转盘、stage↔arm）。

## Reject cases
- 去掉转盘物镜或载物台 → 出类目（望远镜/放大镜）。
- objective N=1（无转盘意义）或 N>6（学生镜不现实）→ 出词汇表。
- 转盘关节降为 FIXED → 0 关键关节。
- palette/scale 当 candidate → 非结构差异。

## 与相邻类别的边界
- 望远镜：无转盘物镜 + 无载物台 + 无台下照明。
- 放大镜/手持镜：无机构。
- 相机三脚架：云台非显微转盘 + 无目镜光路。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |

## Module Source Index
| source_id | slot | module | record_id |
|---|---|---|---|
| S1 | A/B/C | monocular / condenser / side_coaxial (parent) | rec_build-...-micr_..._5f8b9008 |
| S2 | A | binocular_head | rec_microscope_var_binoc |
| S3 | A | vertical_straight | rec_microscope_var_vtube |
| S4 | B | tilting_mirror | rec_microscope_var_mirror |
| S5 | B | led_disc | rec_microscope_var_leddisc |
| S6 | C | dual_coarse_fine_knob | rec_microscope_var_dualknob |
| S7 | C | mechanical_xy_stage | rec_microscope_var_xystage |
| S8/S9/S10 | multiplicity | objective_count N=2/4/6 | rec_microscope_var_obj{2,4,6} |
