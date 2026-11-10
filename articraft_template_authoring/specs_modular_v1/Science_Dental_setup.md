# Modular Spec — Science / Dental setup

## 元信息
| 项 | 值 |
|---|---|
| slug | `dental_setup` |
| template path | `agent/templates/Science_Dental_setup.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（3 个并列结构 slot：chair-recline × light-arm × delivery-head；外加 1 根 multiplicity 轴 `instrument_count`） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（1 parent + 8 variants） |
| read_count | 9 |
| read_scope | all 5-star samples in this category |

读取的 9 个 5 星样本（均 rating=5，model.py 可读；注：record.json 的 rating 字段为 null，按 source map 已收敛声明计为 5★）：

| source_id | record_id | 结构家族 |
|---|---|---|
| S1 | rec_build-...-dent_20260609_183622_759989_90de439f（parent） | single-body recline + single rigid light-arm + round-dish head, instruments N=5 |
| S2 | rec_dental_setup_var_seatback2 | 2-section backrest（独立 backrest REVOLUTE on fixed seat） |
| S3 | rec_dental_setup_var_seatback3 | 3-section（+footrest fold REVOLUTE） |
| S4 | rec_dental_setup_var_armelbow | 2-segment light-arm（upper+forearm，elbow REVOLUTE） |
| S5 | rec_dental_setup_var_armparallel | 平行四边形 light-arm（4-bar，Mimic 保持水平） |
| S6 | rec_dental_setup_var_ledhead | rectangular LED panel head |
| S7 | rec_dental_setup_var_swingtray | delivery head 移到摆臂上（delivery_arm_swing REVOLUTE） |
| S8 | rec_dental_setup_var_instr3 | instrument N=3（loop + per-instrument hose） |
| S9 | rec_dental_setup_var_instr7 | instrument N=7 |

**共性骨架（9 个样本一致）**：root `base`（floor_pad + chair_pedestal + seat_carrier + light_post），companion `delivery_column` + `stool`（5-star caster base，legs/casters loop n=5）。3 个非 fixed 关节恒在：`backrest_recline`(REVOLUTE −Y) + `light_arm_swing`(REVOLUTE Z) + `light_head_tilt`(REVOLUTE Y)。Primitive: LatheGeometry（pedestal/reflector/cuspidor/stool seat）, section_loft（cushion）, sweep_profile_along_spline（arm）, TorusGeometry（rim）, tube_from_spline（handle/leg）—— 无 boxy 降级。

## 核心身份
一套牙科诊疗设备（dental treatment unit）：可斜躺的患者椅 + 头顶可摆动/俯仰的无影灯臂 + 器械递送台。载身识别 = **chair 斜躺 + light-arm 摆动/俯仰**（至少这两层的 REVOLUTE 关节）。不该混入：普通办公转椅（无无影灯臂 + 器械台）、独立落地灯（无椅）、surgical_bed（平躺手术台，非坐姿牙椅）、橱柜（无机构）。

## 槽位 + 候选模块表

### Slot A：chair-recline（患者椅斜躺机构）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_body_recline | S1 (parent) | L147-L188 / joint L467-L475 | eligible | seat+back+headrest 作为一块 slab 绕侧轴斜躺，单 REVOLUTE |
| two_section_backrest | S2 | L148-L240 / joint L513-L532 | eligible | backrest 独立成 part，铰接在固定 seat pan 上（自己的 REVOLUTE recline） |
| three_section_footrest | S3 | L149-L234 / joint L513-L536 | eligible | 在 2-section 基础上加独立 footrest leg 段，自己的 fold REVOLUTE |

### Slot B：light-arm（无影灯支臂结构）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_rigid_arm | S1 (parent) | L195-L237 / joint L479-L487 | eligible | 单根 swept 刚臂，1 个 swing REVOLUTE |
| two_segment_elbow | S4 | L196-L281 / joint L522-L544 | eligible | upper arm + forearm，elbow REVOLUTE 折叠（多 1 个活动关节） |
| parallelogram | S5 | L232-L343 / joint L581-L631 | eligible | 平行四杆，2 平行 bar（loop 发射）+ `Mimic` 保持灯头水平；≥1 REVOLUTE |

### Slot C：delivery / light-head（灯头 + 递送台形式）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_dish_head | S1 (parent) | L244-L305 | eligible | 圆碟反光罩灯头（Lathe + Torus + glass），yoke tilt REVOLUTE |
| led_panel | S6 | L245-L316 | eligible | 矩形 LED 面板灯头（Box + BezelGeometry），仍 yoke tilt |
| swing_tray_delivery | S7 | L391-L456 / joint L569-L577 | eligible | 递送头从固定柜顶移到独立摆臂上，自己的 delivery_arm_swing REVOLUTE |

> **single-candidate slot degrade**：无。三个 slot 各 ≥3 候选。

## 槽位图（slot graph）
```
 base (root, FIXED chassis: pedestal/seat_carrier/light_post)
   ├─ [Slot A chair-recline]  seat/back(/foot) REVOLUTE chain off seat_carrier
   ├─ [Slot B light-arm] light_post ─swing(REV Z)─► (elbow/parallelogram)─► light_head_yoke
   │                                                     └─ [Slot C head] yoke ─tilt(REV Y)─► dish/led head
   └─ delivery_column (FIXED) ── [multiplicity] handpiece_{i} + hose_{i}  (FIXED to host)
         host = delivery_column；Slot C=swing_tray 时 host = delivery_arm（随摆臂动）
```
接口：light-arm swing 锚在 light_post 顶面（REVOLUTE Z）；head tilt 锚在 arm 末端 yoke（REVOLUTE Y）；chair recline 锚在 seat_carrier 上缘。Slot C=swing_tray 把 instrument host 从柱顶改挂到摆臂（唯一跨槽 conditional）。

## 每槽位 Module Emits / Interfaces
- **Slot A**：emits 椅面 part 树（single slab / backrest part / +footrest part）；internal joints = recline REVOLUTE（two/three 段各自带 hinge）；upstream = seat_carrier 上缘 anchor；downstream = headrest 面。
- **Slot B**：emits 灯臂 part（1/2 段 / 4-bar）；internal joints = swing REVOLUTE（+elbow / +parallelogram Mimic）；upstream = light_post 顶 boss；downstream = arm 末端 yoke 接口。
- **Slot C**：emits 灯头 visual（dish Lathe+Torus / LED Box+Bezel）+ yoke；internal joints = head tilt REVOLUTE；swing_tray 额外 emits delivery_arm + delivery_arm_swing REVOLUTE。
- **Multiplicity**：emits `handpiece_{i}` + `hose_{i}`（shared helper，沿 host 前缘等距），FIXED 到 host（hose 为 drape 装饰，无独立 joint）。

## 参数范围汇总
| 参数 | 类型 | 取值 | 约束 | 来源 |
|---|---|---|---|---|
| chair_recline | enum | single_body / two_section / three_section | choice | Slot A |
| light_arm | enum | single_rigid / two_segment_elbow / parallelogram | choice | Slot B |
| delivery_head | enum | round_dish / led_panel / swing_tray | choice；swing_tray → instrument host = delivery_arm | Slot C |
| palette_style | enum | navy_tan / white_mint / grey_clinical / teal_chrome / sand_warm（≥3） | palette only，不计入 slot_choice | S1-S9 材质 |
| instrument_count | int | {3,5,7} 采样，N_range [2,8] | multiplicity；FIXED to host | S8/S9 |
| chair_h_scale / arm_len_scale / column_h_scale | float | [0.9,1.15] | independent，clamp | S1 |
| (—) | constraint | light-head 在患者上方 ≥0.5；delivery y ≥0.30 | inequality（resolve_config） | S1 |

## Multiplicity / Copy Logic
- **count_param**：`instrument_count`（host 上的手机/软管数）。
- **N_range**：[2, 8]；采样域 {3,5,7}（parent=5）。
- **copied object**：handpiece + 其 drape hose（shared helper）。
- **naming**：`handpiece_{i}` / `hose_{i}`，沿 host 前缘等距。
- **joint policy**：全 FIXED 到 host part（delivery_column，或 swing_tray 模式下 delivery_arm）；hose 为装饰 drape，无 joint。
- **source**：S8(instr3 L73)、S9(instr7 L73, L96-L108) 的 `for i in range(n)` 循环。

## 拓扑多样性审计
- 纯 slot 组合 = A(3) × B(3) × C(3) = **27**；× N 样本 {3,5,7} = **189** distinct（N 编码进 slot_choices_for_seed）。
- seed_domain_policy：procedural_first。`config_from_seed`：均匀采 A/B/C → 加权采 instrument_count{3,5,7} → 采 palette → 采连续 scale；`resolve_config` 投影 inequality（灯头高度 / delivery 位置）。
- Topology target：~27 slot-distinct（连续 scale 提供比例多样性，不增 distinct）；远超 10。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
- 兼容矩阵：swing_tray ↔ instrument host=delivery_arm（其余 head 用 delivery_column）；其余槽两两兼容。

## Validator
- `slot_choices_for_seed` 返回已实现 module 名（A/B/C 各 3）。
- `config_from_seed` 全程 procedural（含 seed 0）。
- 3 个核心 REVOLUTE（recline / arm_swing / head_tilt）恒在；parallelogram 的 Mimic 正确耦合。
- instrument host 随 Slot C 正确切换（swing_tray → delivery_arm）。
- handpiece/hose element-scoped allow_overlap（hose drape 入 host），非 broad part-level。
- 连续 scale clamp，inequality（灯头在患者上方 / delivery 不穿椅）在 resolve_config 求解。

## Reject cases
- 去掉无影灯臂或患者椅 → 出类目（变成办公椅 / 落地灯）。
- chair recline 或 light-arm swing 降为 FIXED → 0 关键关节，拒收。
- 把 palette / 连续 scale 当新 candidate 塞 slot → 非结构差异。
- parallelogram 漏 Mimic → 灯头不保持水平（机构失真）。
- instrument hose 用 broad allow_floating 掩盖穿插 → authoring smell。

## 与相邻类别的边界
- 办公/理发转椅：无无影灯臂 + 器械递送台。
- 独立落地无影灯：无患者椅、无递送层。
- surgical_bed：平躺手术台（多段水平 mattress），非坐姿牙椅 + 灯臂。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |

## Module Source Index
| source_id | slot | module | record_id |
|---|---|---|---|
| S1 | A/B/C | single_body / single_rigid / round_dish (parent) | rec_build-...-dent_..._90de439f |
| S2 | A | two_section_backrest | rec_dental_setup_var_seatback2 |
| S3 | A | three_section_footrest | rec_dental_setup_var_seatback3 |
| S4 | B | two_segment_elbow | rec_dental_setup_var_armelbow |
| S5 | B | parallelogram | rec_dental_setup_var_armparallel |
| S6 | C | led_panel | rec_dental_setup_var_ledhead |
| S7 | C | swing_tray_delivery | rec_dental_setup_var_swingtray |
| S8 | multiplicity | instrument_count N=3 | rec_dental_setup_var_instr3 |
| S9 | multiplicity | instrument_count N=7 | rec_dental_setup_var_instr7 |
