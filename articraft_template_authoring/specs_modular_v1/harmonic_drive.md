# Modular Spec — Robotics / Harmonic drive (`harmonic_drive`)

## 元信息
| 项 | 值 |
|---|---|
| slug | `harmonic_drive` |
| template path | `agent/templates/harmonic_drive.py` |
| test path (optional) | `tests/agent/test_harmonic_drive_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (coaxial concentric stack: fixed housing/flange root + coaxial moving members; parallel-children + serial explode chain depending on ② mechanism) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (3 origins + 6 forked variants + 1 compatibility probe) |
| source_index_policy | only adopted module sources are indexed below |

Read: `rec_...b50bce44` (B, component-tube exploded), `rec_...c263187d` (C, cup exploded),
`rec_...d4091bdf...` (A, pancake/flat rotary), `rec_harmonic_drive_var_form_tophat` (F1),
`rec_harmonic_drive_var_mechanism_continuous` (F2), `rec_harmonic_drive_var_skeleton_3element` (F3),
`rec_harmonic_drive_var_bolt_n8` (N1), `rec_harmonic_drive_var_bolt_n20` (N2),
`rec_harmonic_drive_var_probe_cup_rotary` (P, cup+rotary compatibility probe).

## 核心身份

A strain-wave (harmonic) gear reducer: an elliptical **wave generator** (input cam) inside a flexible
externally-toothed **flexspline** that meshes against a rigid internally-toothed **circular spline**, all
coaxial on one central +Z axis, with a mounting **bolt-hole flange** on the fixed housing and a central
hollow-shaft-capable bore. Single-stage high reduction. The template must keep the three functional gear
elements present-or-implied, keep everything coaxial concentric, expose a mount bolt circle, and carry at
least one real non-fixed joint (bounded/continuous coaxial reduction, or an exploded assembly-step slide).

不该混入：planetary / cycloidal (RV) reducer；plain ball / cross-roller bearing or slewing ring on its own；
electric servo motor；plain flange shaft coupling。

## 槽位 + 候选模块表

### Slot A：`form_family`（③ 主体形态家族 / Primary Form Family — 形态主导主轴，登记进 slot_choices）
决定固定 housing/flange 根件的外形轮廓 + 主 flexspline 体的可识别几何原型 + 各同轴动件的座落面高度。part tree/interface 不变（都是 housing 根 + 同轴 flexspline 体），只换离散主体形态原型。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `pancake_flat` | forked_anchor | rec_...d4091bdf (A) | L53-L67, L108-L199 | eligible if compatible | 薄扁同轴阶梯盘 housing（多段 annular）+ 扁 tooth-ring flexspline，整体低矮。**Volumetric Envelope Form**（扁盘包络） |
| `deep_cup` | forked_anchor | rec_...c263187d (C) | L40-L54, L75-L104 | eligible if compatible | flange_ring + 浅 circular_spline_bore 台阶 + 深 hollow cup flexspline（闭底膜片）。**Volumetric Envelope Form**（深杯包络） |
| `component_tube` | forked_anchor | rec_...b50bce44 (B) | L136-L188 | eligible if compatible | 宽 bolted flange + 高 ribbed 外壳筒 + top_lip + 内插 cartridge sleeve flexspline。**Macro Surface Construction**（肋筋筒壳大尺度表面构成） |
| `top_hat` | forked_anchor | rec_harmonic_drive_var_form_tophat (F1) | L50-L83, L127-L164 | eligible if compatible | flange + bore 台阶 + 短开口 barrel 顶端外翻 mounting brim（silk-hat）flexspline。**Planar Boundary Form**（外翻 brim 平面边界） |

### Slot B：`mechanism`（② 关节类型 — 动件相对固定根的关节拓扑）
part tree 的动件语义随之变（rotary → output_flange + wave 旋转；explode → flexspline + wave 平移），但都同轴 +Z。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rotary_revolute` | forked_anchor | rec_...d4091bdf (A) + rec_...probe_cup_rotary (P) | A L226-L245；P L224-L254 | eligible if compatible | housing→output_flange **REVOLUTE**(±,bounded, +Z)；housing→wave_generator REVOLUTE(+Z)；output→flexspline FIXED（flexspline 随 output 转）。装配式减速输出 |
| `rotary_continuous` | forked_anchor | rec_harmonic_drive_var_mechanism_continuous (F2) | L221-L240 | eligible if compatible | 同 rotary 但两旋转关节 **CONTINUOUS**（无界，running reducer）；无位置界 |
| `exploded_prismatic` | forked_anchor | rec_...c263187d (C) + rec_...b50bce44 (B) | C L132-L149；B L290-L307 | eligible if compatible | housing→flexspline **PRISMATIC**(+Z)；flexspline→wave_generator PRISMATIC(+Z)。爆炸装配步串链 |

### Slot C：`skeleton`（① 骨架图 — gear-element 分解）
加/减一个会动关系的 part：圆花键是并入 housing 还是独立件。降到 2 candidate（类别结构极窄，样本池只支持 fused / separated 两种真实骨架，见 §5 underfilled_reason）。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fused_housing` | forked_anchor | rec_...d4091bdf (A) + rec_...b50bce44 (B) | A L167-L179；B L166-L188 | eligible if compatible | circular-spline 齿环作为 **visual** 融进固定 housing part；无额外 part |
| `separated_elements` | forked_anchor | rec_harmonic_drive_var_skeleton_3element (F3) | L108-L126, L183-L212, L300-L315 | eligible if compatible | circular_spline 提升为**独立 FIXED part**（bolted 进 housing bore，自带齿环 + spline_line）；flexspline 体独立 |

### multiplicity：`mount_bolts`（N — 固定 flange 安装螺栓数，登记进 slot_choices）
| module family | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `bolts_n{N}` (N∈[8,30]) | forked_anchor | origins {12 (C), 14 (A), 24 (B)} + forks {8 (N1), 20 (N2)} | C L88-L96；A L61-L65；B L44-L56；N1/N2 L88-L96 | eligible if compatible | 固定 bolt-circle 半径上等角 radial `bolt_{i}` FIXED-decoration visual 环；N 变数量 |

硬约束落实：每个 candidate 都 `forked_anchor` + 真实 `model.py:Lx-Ly`；候选间结构差异真实（换主体形态原型 / 换关节类型 / 加减 part），不是换尺寸涂装；③ 形态主导 slot（form_family，4 候选 ≥3）登记进 slot_choices。

## 槽位图（slot graph）

pattern: **mixed**

```
housing (form_family: 固定 grounded 根件, 中心 bore + bolt 圈 + circular-spline 座)
   │
   ├─[mechanism=rotary_*]  housing --REVOLUTE/CONTINUOUS (+Z centerline)--> output_flange
   │                       output_flange --FIXED (mount ring band)--> flexspline(form body)
   │                       housing --REVOLUTE/CONTINUOUS (+Z centerline)--> wave_generator
   │
   ├─[mechanism=exploded]  housing --PRISMATIC (+Z)--> flexspline(form body)
   │                       flexspline --PRISMATIC (+Z)--> wave_generator
   │
   └─[skeleton=separated]  housing --FIXED (bore seat ring band)--> circular_spline
```

- 接口点位：所有跨件连接是**同轴 +Z 座落面**（housing 顶环座 / cup-mouth 唇 / bore 台阶 / 中心 boss）。旋转/平移关节 origin 在中心对称轴（symmetry centerline → 旋转关节 origin honesty 以中心线通过；prismatic 豁免）。FIXED 关节 origin 放在两件公共环材料带的半径点（非空 bore 中心）。
- 跨 slot joint type/axis/range：见 §8.5 ⑤。旋转 bounded `[-π,π]` 或 `[0,π]`；continuous 无界；explode PRISMATIC `[0, travel]`。
- 互斥/派生：mechanism 决定动件清单（rotary→output+wave；explode→flexspline+wave 平移）；skeleton=separated 追加 1 个 FIXED circular_spline part；form_family 决定 housing/flexspline 形态但不改关节拓扑。所有 4×3×2 组合都物理合法（见 §9 compatibility matrix，无需 gate）。

## 每槽位 Module Emits / Interfaces

### Slot A / form_family（每 candidate）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `housing`（grounded 根；outer body + 中心 bore + circular-spline 座/齿 + top lip/ledge，form 特有轮廓） | A L122-L179 / C L75-L96 / B L136-L188 / F1 L96-L125 |
| parts | `flexspline`（form 特有体：flat ring / hollow cup / cartridge sleeve / top-hat barrel+brim；由 mechanism 决定关节） | A(hint)/C L98-L116/B L189-L232/F1 L127-L164 |
| internal joints | 无（form 只出几何；关节由 mechanism 出） | — |
| upstream interface | housing 是根，无 upstream | — |
| downstream interface | housing 顶座面（z=`housing_top_z`, r=座环带）+ flex 体座落几何 → 供 mechanism/skeleton 关节参考 | C L48-L53 |

### Slot B / mechanism
| emits | 描述 | 来源 |
|---|---|---|
| parts | rotary_*: `output_flange`（旋转 disk + bearing land underside）+ `wave_generator`（elliptical_cam + center_hub）；exploded: 复用 form 的 `flexspline` 做 slider + `wave_generator` | A L181-L224 / C L118-L130 |
| internal joints | rotary: `housing_to_output` REVOLUTE/CONTINUOUS(+Z)、`output_to_flexspline` FIXED、`housing_to_wave` REVOLUTE/CONTINUOUS(+Z)；exploded: `housing_to_flexspline` PRISMATIC(+Z)、`flexspline_to_wave` PRISMATIC(+Z) | A L226-L245 / C L132-L149 |
| upstream interface | 同轴座落到 housing 顶座 / bore（parallel-children，parent=housing） | A L226-L235 |
| downstream interface | wave_generator 输入 cam 面（记录用；不再向下链） | — |

### Slot C / skeleton
| emits | 描述 | 来源 |
|---|---|---|
| parts | fused: 无额外 part（circular-spline 齿是 housing visual）；separated: `circular_spline`（ring + spline_line + 内齿环 visual） | F3 L183-L212 |
| internal joints | separated: `housing_to_circular_spline` FIXED（origin 在 bore 座环带） | F3 L300-L307 |
| upstream interface | 同轴座落到 housing 前 bore | F3 L108-L116 |
| downstream interface | circular_spline 内齿孔（flexspline 在其内啮合，allow_overlap） | F3 L412-L432 |

活动件均有 articulation 语义；不动细节（bolts / 齿 / bearing balls / groove line / keyway）写成宿主 part visual（Rule 1）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `form_family` | enum | pancake_flat / deep_cup / component_tube / top_hat | pancake_flat | choice | deterministic procedural sampler | Slot A |
| `mechanism` | enum | rotary_revolute / rotary_continuous / exploded_prismatic | rotary_revolute | choice | deterministic procedural sampler | Slot B |
| `skeleton` | enum | fused_housing / separated_elements | fused_housing | choice | deterministic procedural sampler | Slot C |
| `bolt_count` | int | [8, 30] | 12 | independent | 加权采样(小 N 偏多)后 clamp；等角放置 | multiplicity |
| `frame_scale` | float | [0.85, 1.25] | 1.0 | independent | 缩放整体 OD / 座环 / bore；范围内独采后 clamp | 全 origins OD 0.10-0.36 |
| `flex_height_scale` | float | [0.85, 1.20] | 1.0 | independent | 缩放 flexspline 体高（cup/tube/tophat 深浅） | C CUP_H |
| `bore_scale` | float | [0.8, 1.3] | 1.0 | independent | 中心 hollow bore 半径缩放（受 clamp 不超 flex_inner） | A/C bore |
| `bolt_circle_r` | float | derived | — | equation | `= flange_outer_r - bolt_margin`（随 frame_scale 派生） | C r=0.148 |
| `tooth_count` | int | derived | — | equation | `= round(k · flex_outer_r)`（随 frame_scale 派生，clamp [40,80]） | {42,60,72} |
| `cam_major_r` | float | derived | — | equation | `= flex_inner_r · 0.94`（cam 主半轴略小于 flex bore，保证旋转不新增穿模） | C ellipse |
| (—) | constraint | — | — | inequality | `bore_r ≤ flex_inner_r − wall_min`；`bolt_circle_r + bolt_head_r ≤ flange_outer_r`；违反按比例回缩 | 接口 / clearance |

连续尺寸采样契约：先采 independent（frame_scale, flex_height_scale, bore_scale, bolt_count）→ 派生 equation（bolt_circle_r, tooth_count, cam_major_r）→ inequality 投影回缩 → 无 conditional。全部在 `resolve_config` 求解。

### 7.5 编译预算 / compile budget（必填）
自报 **每-seed ≤ 25s**（依据：源记录每件多 mesh_from_cadquery 布尔——阶梯壳/深杯/肋筒/top-hat——库内实测重放样类 ~15-30s；本模板每 seed 3-6 个雕刻 mesh + loop 出的 primitive 齿/球/螺栓）。分档 tessellation：cadquery mesh tolerance 0.0008 / angular 0.04（同源记录）；小特征齿/球/螺栓用 `Box`/`Cylinder`/`Sphere` primitive（非 mesh）；N 个同构齿/球/螺栓共用同尺寸循环发射。sweep `--compile-timeout 120`（≈3× 预算，watchdog）。

## Multiplicity / Copy Logic

**count_param (primary)：`bolt_count`** — 固定 flange 上安装螺栓环。
- N_range：产品域 [8, 30]；测试偏小、产品全程。sampling domain：加权（小 N 高频，大 N 稀有；权重档 ≤12 高频 / 13-20 中 / 21-30 稀有）。
- copied object：through-bolt head visual，indexed `bolt_{i}`；placement：`bolt_circle_r` 上等角 `a=2πi/N`；joint policy：**FIXED-decoration visual**（不 articulate，Rule 1），挂在固定 housing part。
- source/gating：origins {12,14,24} + forks {8,20}；无 gate（数量不影响装配合法性）。
- slot_choices 登记：`("mount_bolts", "bolts_n{N}")`。

**count_param (secondary, record_only)：flexspline 外 `tooth_{i}`** — origin 已展 {42,60,72}；本模板由 `tooth_count = round(k·flex_outer_r)` 派生（equation，随尺寸共形），N_range≈[40,80]，loop-placed radial `Box` 齿，FIXED visual。record_only，不作独立 sweep 轴（源已 3 样本，避免 ④/内部填充）。

**other loops (record_only)：** bearing balls (28, `Sphere` visual)、housing 外肋/内齿 (B: 60/72)、output bolt-hole shadow (4)。loop-emitted、FIXED visual、indexed；record_only。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Slot C：`fused_housing`（花键并入 housing，无额外 part）vs `separated_elements`（circular_spline 独立 FIXED part）。forked_anchor：A/B（fused）、F3（separated）。降到 2 候选，underfilled_reason 见 §5 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：`bolt_count` N∈[8,30] 加权档（primary）；tooth_count 派生（record_only） |
| ② 关节类型 | 图不变换 type/轴 | 有 | Slot B：REVOLUTE(bounded, A/P) / CONTINUOUS(无界, F2) / PRISMATIC(explode, B/C)，全 +Z。三种都在 sweep 出现（每 candidate 独立采样）。forked_anchor |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有（形态主导主轴，登记 slot_choices） | Slot A 4 候选，各标 form_subtype：pancake_flat=Volumetric Envelope Form(扁盘)；deep_cup=Volumetric Envelope Form(深杯)；component_tube=Macro Surface Construction(肋筒壳)；top_hat=Planar Boundary Form(外翻 brim)。forked_anchor：A/C/B/F1 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有（record_only / host-conformal） | broached keyway relief、machined groove/spline_line 环、bearing-ball 环、spline-tooth 齿环、mount bolt 头。全部**宿主 part visual**，由宿主最终表面派生（齿在 `flex_outer_r(scale)` 上、bolt 在 `bolt_circle_r(scale)` 上，随 ③/⑤ 共形，派生顺序 ③→⑤→④）。非独立 candidate |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | frame_scale [0.85,1.25]、flex_height_scale [0.85,1.20]、bore_scale [0.8,1.3]（见 §7）。关节运动包络：rotary REVOLUTE 轴+Z 双向 `[-π,π]`（wave 输入）/`[0,π]`（output）；CONTINUOUS 整圈无界；PRISMATIC 轴+Z 向上开 `[0, explode_travel]`（travel≈0.08-0.18·frame_scale）。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`（同轴嵌套用 element-scoped allow_overlap 全程豁免）；targeted `ctx.pose`：rotary 转 π/2 验 elliptical cam AABB x-extent 变化（wave 真转）+ output 转动、explode 验 flexspline/wave +Z 抬升 gap。continuous 整圈不穿模（对称件+cam 在 bore 内）|
| ⑥ 涂装 | 只改材质/颜色 | 有（record_only, companion） | 材质大类 metal(brushed/satin aluminum, dark steel/black oxide, polished bearing steel) / painted(gray-green anodized) / (gold/bronze flexspline)。配色 ≥4 palette 主题（satin_aluminum / black_oxide / gray_green / bronze_gold）。companion，不单独 counted |

①②③ + N 源支撑登记；④⑤⑥ record_only / companion。

## 采样与覆盖审计

总组合数：form 4 × mechanism 3 × skeleton 2 = **24** 拓扑组合 × bolt N 档 ≈ 96（含连续 scale 视觉空间更大）。

理由：harmonic drive 结构极窄（都是同轴 concentric strain-wave reducer），①②③ 词汇在 normal band 低端饱和（源图计数 8 anchors）。24 拓扑 × N × 连续 scale 已覆盖真实产品空间；不填充 filler。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` deterministic 采样，seed 0 不特殊（走同一路径，恰好落在 pancake_flat/rotary_revolute/fused/N=12 附近但由 RNG 决定，非硬编码 table）。每 slot `rng.choice` 独立采；bolt_count/scale 加权/均匀采后 clamp。compatibility：全 24 组合物理合法，无非法对，无 gate（skeleton=separated 只追加 FIXED part；mechanism 只改动件关节；form 只改形态）。无 regression override。
Topology target：1000-seed slot-choice tuple 覆盖 report-only。真实离散拓扑空间 = 24 组合 × N 档，< 300：类别结构窄（underfilled_reason 同 §5），不反推上游变体数。
Controlled local parameterization：frame_scale / flex_height_scale / bore_scale / bolt_count；范围+clamp/derived 见 §7；均不破坏同轴 interface / clearance / joint origin / 类别 identity（bore clamp ≤ flex_inner−wall；bolt_circle+head ≤ flange_outer）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 独立 rng.choice + 加权 bolt_count/scale；seed 0 非特殊 | slot_choices_for_seed matches build choices |
| compatibility matrix | 全 24 组合合法；separated 追加 FIXED part；无互斥 gate / fallback | 无 floating（同轴嵌套 overlap 提供 connectivity）/ 无 closed-pose 穿模（element allow_overlap）/ 无 axis 错 |
| controlled local variation | frame/flex_height/bore/bolt scale，clamp+derive | 比例变而不破 interface/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 首过；0-999 成熟度 | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| form_family | 4 | yes | yes | ③ 形态主导 slot |
| mechanism | 3 | yes | yes | ② |
| skeleton | 2 | yes | no | ① 类别窄，样本池仅支持 fused/separated 两真实骨架 |
| mount_bolts (N) | ≥5 realized | yes | yes | multiplicity |

## Validator

- slot_choices_for_seed returns implemented module names（form_family / mechanism / skeleton / mount_bolts）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed 0 非特殊）
- compatibility：全组合合法，无非法对
- 无 regression override
- controlled local scale 全在 resolve_config clamp/derive，不破 interface/clearance/joint origin/identity
- 跨件 scale 依赖（bolt_circle_r/tooth_count/cam_major_r equation、bore/bolt inequality）在 resolve_config 求解
- 关键 joint 类型/轴/range 正确：rotary REVOLUTE/CONTINUOUS +Z；explode PRISMATIC +Z；FIXED origin 在环材料带
- 复制件命名 `bolt_{i}` / `tooth_{i}` / `bearing_ball_{i}` 稳定 indexed，等角放置
- 非-FIXED joint 模板：`fail_if_parts_overlap_in_sampled_poses` + targeted `ctx.pose`（Rule 5）

## Reject cases

- 把不动的 bolt/齿/bearing-ball/keyway 做成 FIXED-joint part（应为 host visual，违 Rule 1）
- circular-spline 提升为 part 却无 FIXED 关节或无 housing 座落 → floating / isolated part
- 同轴动件旋转/平移某姿态穿模而未 element-scoped allow_overlap（违 Rule 5）
- FIXED 关节 origin 放在空 bore 中心（离环材料 >15mm）→ origin honesty fail
- 把 form_family 退化成只换尺寸/涂装（非真实 ③ 原型切换）
- 把 primitive 精雕（hollow_cup / ribbed shell / top-hat / elliptical cam 的 cadquery mesh）降级成裸 Box/Cylinder（违 Rule 3）
- cam 主半轴 ≥ flex bore → 旋转新增穿模
- explode PRISMATIC travel 过大使动件飞离，或过小闭合姿态嵌套无 allow_overlap

## 与相邻类别的边界

- 不该混入：planetary / cycloidal (RV) reducer（多行星/摆线盘拓扑，非单 flexspline strain-wave）
- 不该混入：plain ball / cross-roller bearing / slewing ring（只有滚道无 flexspline+wave+circular-spline 三元件）
- 不该混入：servo motor / plain flange coupling（无减速齿元件）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 结构窄类别，skeleton slot 降 2 候选并已声明 underfilled_reason；24 拓扑 × N × scale 覆盖真实产品域 |

## 模板实现备注（可选）
- 共享 helper：`_annular_cylinder` / `_hollow_cup` / `_top_hat` / `_ribbed_shell` / `_pancake_shell` / `_elliptical_cam`（改编自源 helper，保 primitive 家族）；`_emit_bolts` / `_emit_teeth` / `_emit_balls` 循环发射。
- 同轴 captured-pivot 关节（rotary REVOLUTE/CONTINUOUS、explode PRISMATIC）**省略 MatingContract**（grandfathered pin/ring-bearing/captured coaxial；origin 走 symmetry-centerline/prismatic 豁免），用 element-scoped `allow_overlap` + `expect_contact` 表达座落，与源记录一致。
- FIXED 关节（output→flexspline、housing→circular_spline）origin 放两件公共环材料带半径点（非空 bore 中心），保 origin honesty。
- element-scoped allow_overlap：cam↔flexspline、flexspline↔housing-bore、flexspline↔circular_spline、output-land↔housing-top、wave-hub↔flexspline/bore。
- 24 组合全进 seed domain，无暂缓。

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S_A | form_family | pancake_flat | rec_...d4091bdf (A) | L53-67,L108-199 | 阶梯扁盘 housing + 扁 tooth ring + 输出盘 |
| S_C | form_family | deep_cup | rec_...c263187d (C) | L40-54,L75-116 | flange+bore + 深 hollow cup + 齿环 |
| S_B | form_family | component_tube | rec_...b50bce44 (B) | L136-232 | 宽 flange + 肋筒壳 + cartridge sleeve |
| S_F1 | form_family | top_hat | rec_..._var_form_tophat | L50-164 | 外翻 brim top-hat barrel |
| S_A2 | mechanism | rotary_revolute | rec_...d4091bdf (A) / probe | A L226-245 / P L224-254 | REVOLUTE output+wave, output→flex FIXED |
| S_F2 | mechanism | rotary_continuous | rec_..._var_mechanism_continuous | L221-240 | CONTINUOUS 无界旋转 |
| S_C2 | mechanism | exploded_prismatic | rec_...c263187d (C) / B | C L132-149 / B L290-307 | PRISMATIC 爆炸串链 |
| S_A3 | skeleton | fused_housing | rec_...d4091bdf (A) / B | A L167-179 | 齿环 visual 融进 housing |
| S_F3 | skeleton | separated_elements | rec_..._var_skeleton_3element | L108-126,L183-212,L300-315 | 独立 circular_spline FIXED part |
| S_N | mount_bolts | bolts_n{N} | origins + N1/N2 | C L88-96 / N1/N2 | 等角 bolt 环 N 复制 |
```
