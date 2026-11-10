# Walking Cane — modular template spec (slug `Healthcare_Crutches`)

## 元信息
| 项 | 值 |
|---|---|
| slug | `Healthcare_Crutches` |
| template path | `agent/templates/Healthcare_Crutches.py` |
| test path (optional) | `tests/agent/test_Healthcare_Crutches_template.py` (skipped while batch-authoring) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (linear chain base→shaft→handle; multiplicity only on multi-foot bases) |

> IDENTITY NOTE: the picture 小类 is named "Crutches" but every reference image and every
> seeded source is a **walking cane** (single-point / tripod / quad base). This template is
> therefore a **WALKING CANE**. Underarm (axillary) and forearm (Lofstrand) crutches are a
> structurally distinct object (double upright + axilla pad / forearm cuff + mid-shaft grip)
> and are **excluded** (排除项 below).

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star canes in this 小类 (5 forked parents + 4 forked variants) |
| source_index_policy | only adopted module sources indexed below |

## 核心身份

A **walking cane / walking stick**: a slim vertical shaft the user grips at the top and
loads onto a small base at the bottom, ~0.82–0.98 m tall at rest. Three functional layers:
a ground **base/foot** (single rubber ferrule, or a splayed tripod/quad stabilizing base),
a **shaft** that adjusts height (push-button telescoping) or packs down (multi-section
folding), and an ergonomic **handle/grip** (T/derby, shepherd's crook, swan-neck offset, or
anatomical Fritz palm). Should NOT be confused with: underarm/forearm crutches (double
upright, axilla/forearm interface — different object), trekking poles (paired, spiked tip,
wrist loop dominant, no derby/crook handle), or shepherd's crooks / umbrellas (no ferrule +
telescoping cane hardware).

## 槽位 + 候选模块表

### Slot A：base（③ Primary Form Family — Volumetric Envelope of the ground base; ROOT slot）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_point_base` | forked_anchor | S1 / S5 | S1 L51-68 (ferrule), S1 L102-160 | eligible if compatible | 1 part `base`: LatheGeometry flared rubber ferrule + short socket collar. No foot loop. `form_subtype=Volumetric Envelope Form` (compact single-point tip). |
| `tripod_base` | forked_anchor | S2 | S2 L56-98 (hub), S2 L183-231 (leg loop) | eligible if compatible | `base` hub (Cylinder + Sphere + socket) + `leg_{0..2}` (3) each Cylinder tube + rubber ferrule + flared foot, FIXED to hub. `form_subtype=Volumetric Envelope Form` (3-splay tripod). |
| `quad_small_base` | forked_anchor | S3 | S3 L51-73 (plate), S3 L103-149 (foot loop) | eligible if compatible | `base` rounded rectangular plate (LoftGeometry) + socket + `foot_{0..3}` (4) rubber plug/pad, FIXED to plate. `form_subtype=Planar Boundary Form` (small rectangular plate). |
| `quad_wide_base` | forked_anchor | S4 | S4 L71-131 (hub + spline leg loop) | eligible if compatible | `base` hub (Cylinder plate + revolved socket) + `leg_{0..3}` (4) tube_from_spline curved legs + ferrule, FIXED to hub; WIDE splayed footprint offset to one side. `form_subtype=Volumetric Envelope Form`. |

### Slot B：handle（③ Planar Boundary Form of the grip — primary handle fork axis）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `t_derby_handle` | forked_anchor | S1 | S1 L71-90 (superellipse grip), S1 L208-231 | eligible if compatible | `handle` part: superellipse_side_loft ergonomic T/derby grip + neck + socket flare. `form_subtype=Planar Boundary Form`. |
| `crook_handle` | forked_anchor | V1 | V1 L71-107 (tube_from_spline arc), V1 L225-250 | eligible if compatible | `handle`: swept curved shepherd's-crook tube (arc in XZ) + socket ring. `form_subtype=Planar Boundary Form` (round hook silhouette). |
| `offset_handle` | forked_anchor | V2 | V2 L72-111 (swan neck + offset grip), V2 L231-256 | eligible if compatible | `handle`: S-curved swan-neck tube_from_spline + superellipse foam grip offset forward (+x). `form_subtype=Planar Boundary Form`. |
| `fritz_handle` | forked_anchor | V3 | V3 L37-87 (fritz grip), V3 L178-183 | eligible if compatible | `handle`: anatomical front-to-back palm grip (superellipse_side_loft elongated) + socket. `form_subtype=Planar Boundary Form`. |

### Slot C：shaft（② joint-type axis — telescoping vs folding height mechanism）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `telescoping_2piece` | forked_anchor | S1 / S3 / S5 | S1 L102-206, S3 L151-246, S5 L92-216 | eligible if compatible | 2 parts `lower_shaft` (revolved hollow lower tube + collar + flush height holes) + `upper_shaft` (inner tube + top ferrule); internal **PRISMATIC** (axis +z). |
| `folding_4section` | forked_anchor | V4 | V4 L84-162 | eligible if `base==single_point` | 4 parts `shaft_seg_{0..3}` (revolved hollow tube + pivot band) chained by 3 internal **REVOLUTE** fold joints (axis +x), `coupled_chain` mimic-coupled. |

硬约束满足：每个 slot ≥2 结构不同 candidate（A=4, B=4, C=2），全部 `forked_anchor` 且有真实 `model.py:Lx-Ly`。无 single-candidate slot。

## 槽位图（slot graph）

pattern: mixed（linear chain + base-only multiplicity）

```
base (ROOT, grounded) --[FIXED, base_socket +z ↔ shaft_bottom -z]--> shaft
shaft --[FIXED, shaft_top +z ↔ handle_socket -z]--> handle
```

- **base → shaft**：assembler FIXED chain joint. Parent face = base `base_socket` (+z, hub/plate socket top); child face = shaft `lower_tube`/`tube_0` bottom (−z). Child upstream anchor at part-frame (0,0,0), normal-axis (z) component 0.
- **shaft → handle**：assembler FIXED chain joint. Parent face = shaft downstream (telescoping: `upper_shaft.top_ferrule` +z on the SLIDING member so the handle rides height changes; folding: `shaft_seg_3.tube_3` top +z). Child face = handle `socket_flare` (−z).
- Internal motion lives INSIDE the shaft module: telescoping PRISMATIC (`lower_shaft`→`upper_shaft`); folding REVOLUTE `fold_joint_{0..2}` (`seg_i`→`seg_{i+1}`). Both cross-slot chain joints are FIXED.
- 互斥/gating：`folding_4section` 只与 `single_point_base` 组合（真实折叠手杖均为单点；tripod/quad 不折叠）。所有 handle × base 组合合法。

## 每槽位 Module Emits / Interfaces

### Slot A / module single_point_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (ferrule Mesh + socket collar) | S1 L102-160 |
| internal joints | none | — |
| upstream interface | none (root) | — |
| downstream interface | `base_socket` face_side positive_z, anchor (0,0,socket_top) | S1 |

### Slot A / module tripod_base（+ quad_small_base / quad_wide_base 同构）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (hub/plate + socket) + loop `leg_{i}`/`foot_{i}` | S2 L56-231 / S3 L103-149 / S4 L71-131 |
| internal joints | `base_to_leg_{i}` / `base_to_foot_{i}` FIXED (no mating; element allow_overlap at hub socket) | S2 L225-231, S3 L143-149, S4 L125-131 |
| upstream interface | none (root) | — |
| downstream interface | `base_socket` positive_z, anchor (0,0,socket_top) | S2/S3/S4 |

### Slot C / module telescoping_2piece
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lower_shaft` (hollow lower tube + collar + height holes), `upper_shaft` (inner tube + top ferrule) | S1 L102-191 |
| internal joints | `telescope_slide` PRISMATIC axis (0,0,1), lower→upper, limits [0, travel]; grandfathered (no mating — captured sliding tube-in-tube) | S1 L193-206 |
| upstream interface | `lower_tube` negative_z anchor (0,0,0), consumer_joint_type FIXED | S1 |
| downstream interface | `top_ferrule` positive_z anchor (0,0,shaft_top) ON upper_shaft (sliding) | S1 |

### Slot C / module folding_4section
| emits | 描述 | 来源 |
|---|---|---|
| parts | `shaft_seg_{0..3}` (hollow tube + pivot band; ferrule handled by single_point base) | V4 L108-145 |
| internal joints | `fold_joint_{0..2}` REVOLUTE axis (1,0,0), seg_i→seg_{i+1}; `coupled_chain(driver=fold_joint_0, followers=[1,2])`, MatingContract flat tube faces | V4 L148-162 |
| upstream interface | `tube_0` negative_z anchor (0,0,0), consumer_joint_type FIXED | V4 |
| downstream interface | `tube_3` positive_z anchor (0,0,seg3_top) | V4 |

### Slot B / module t_derby_handle（+ crook/offset/fritz 同构）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle` (grip Mesh + socket flare) | S1 L208-231 / V1 / V2 / V3 |
| internal joints | none | — |
| upstream interface | `socket_flare` negative_z anchor (0,0,0), consumer_joint_type FIXED | S1/V1/V2/V3 |
| downstream interface | none (terminal) | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| base_form | enum | single_point / tripod / quad_small / quad_wide | single_point | choice | procedural sampler | Slot A |
| handle_type | enum | t_derby / crook / offset / fritz | t_derby | choice | procedural sampler | Slot B |
| shaft_type | enum | telescoping / folding | telescoping | conditional | folding only if base_form==single_point | Slot C |
| palette_style | enum | anodized_black / bronze_copper / brushed_silver / champagne_gold / chrome_polished / lacquered_wood | anodized_black | choice | procedural sampler; drives every `.visual(material=...)` | ⑥ |
| height_scale | float | [0.96, 1.05] | 1.0 | independent | uniform then clamp; scales target handle-top | S1/S4 tests (~0.88–0.94 m) |
| shaft_radius_scale | float | [0.90, 1.15] | 1.0 | independent | uniform then clamp | S1 r≈0.012 |
| base_span_scale | float | [0.85, 1.15] | 1.0 | independent | uniform then clamp; base footprint | S2/S4 spans |
| telescope_travel | float | [0.08, 0.14] | 0.11 | conditional | only telescoping; ≤ 0.5·lower_tube_len | S1 0.10 / S5 0.12 |
| (—) | constraint | — | — | equation | `shaft_rise = target_top − base_top − handle_rise`; `target_top = 0.905·height_scale` | height model |
| foot_count | int (derived) | {1,3,4} | 1 | equation | `= {single:1, tripod:3, quad_small:4, quad_wide:4}[base_form]` | §8 |

连续尺寸采样契约：先采 independent（height_scale / shaft_radius_scale / base_span_scale / telescope_travel）→ 由 equation 派生 shaft_rise、segment 长度、base_top → conditional（folding gate, travel cap）在 `resolve_config` 内解析。跨部件量（base_top, shaft_rise, segment lengths, socket z）都单源于 helper，禁止 builder 重述。

### 7.5 编译预算 / compile budget
每-seed 预算 **≤ 15 s**（依据：全部几何为纯 Python 生成器——LatheGeometry (segments ≤48)、
tube_from_spline_points (radial ≤20)、superellipse_side_loft (segments ≤48)、LoftGeometry；
无 cadquery 布尔）。ferrule Mesh 每 base 生成一次复用于所有 foot；N 个 foot/leg 复用同一
ferrule/tube helper。`--compile-timeout 120` 为看门狗（~8×预算），非质量门。

## Multiplicity / Copy Logic

- **轴 1：foot_count**（仅多脚 base）。
  - count_param `foot_count`；`N_range` = 离散集 `{1 (single_point), 3 (tripod), 4 (quad_small/quad_wide)}`。非连续，无权重档——由 base_form 决定。
  - copied object：`leg_{i}`（tripod/quad_wide 斜撑腿）或 `foot_{i}`（quad_small 平板脚），uniform 径向/矩形排布，每个 FIXED 到 base hub/plate，各带 rubber ferrule/pad。
  - source/gating：tripod→3 (S2), quad→4 (S3/S4)；single_point 无复制循环（base 即 ferrule）。
- N 已覆盖：{3→tripod, 4→quad_small/quad_wide, 1→single_point}。

## 视觉多样性 6 轴考察

| 轴 | 处理 | 本小类取值 / 范围 / 理由 |
|---|---|---|
| ① 骨架图(+N) | forked_anchor | base→shaft→handle chain；foot multiplicity {1,3,4}。folding adds 4-seg + 3 REVOLUTE sub-skeleton。全部 source-backed。 |
| └ multiplicity | forked_anchor | 见 §8：foot_count {1,3,4} 离散。 |
| ② 关节类型 | forked_anchor | PRISMATIC（telescoping height, axis z, S1/S3/S5）；REVOLUTE（folding fold_joint, axis x, V4）；跨-slot FIXED。声明的两种运动关节都在 sweep 出现（telescoping 大多数 seed；folding ~1/8 seed）。 |
| ③ 主体形态家族 | forked_anchor | **Slot A（base）= 登记进 slot_choices 的 ③ Primary Form Family**：single/tripod/quad_small/quad_wide 四个可识别体量/平面原型（form_subtype 已标注）。Slot B（handle）= 第二根 ③（grip Planar Boundary：T-derby/crook/offset/fritz）。 |
| ④ 表面装饰 | record_only + host-conformal | 望远镜管上的 flush 高度调节孔行（宿主管面派生，同半径共形嵌入，Cylinder sunk into tube）、collar 明暗唇带、fold pivot band。皆为宿主 part visual，非独立 part/joint（Rule 1/4）。 |
| ⑤ 尺寸/行程 | record_only | shaft_rise 派生 ~0.72–0.86 m；telescope travel 0.08–0.14 m（axis +z, [0, travel]）；base footprint 0.05–0.28 m（base_span_scale）。**运动包络**：PRISMATIC [闭合0, 上界travel]，开启方向 +z，跑 sampled collision + targeted pose（handle 升高 ≥0.8·travel）；REVOLUTE fold [0, solver-clamped]，跑 coupled sampled collision + targeted pose（fold 使 seg 偏离竖直 + 手柄高度下降）。tube-in-tube 与 adjacent-seg knuckle 用 element-scoped allow_overlap（captured 嵌套/铰链），非 broad。 |
| ⑥ 涂装 | record_only | 6 配色：anodized_black / bronze_copper / brushed_silver / champagne_gold / chrome_polished / lacquered_wood（grip: black foam / rubber / tan / wood）。材质大类 metal(5) + painted-wood(1)，覆盖 ≥ ceil(0.5×6)=3。`palette_style` 每-seed 采样驱动全部 material。 |

收尾自检目标：`template batch` 0-9 seed 渲染中，四种 base form 拉得开、四种 handle 可辨、telescoping 与 folding 都出现、配色不单一、装饰贴合管面不悬空、关节全程不穿模。

## 拓扑多样性审计

总组合数：base(4) × handle(4) × shaft(gated) = 4×4×1 (tripod/quad→telescoping) + 1×4×2 (single_point→{tele,fold}) = 12 + 8 = **20** 合法拓扑（未含连续 scale / palette）。含 palette(6) → 120 视觉组合。


seed_domain_policy：procedural_first（seed=0 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次采 base_form、（条件）shaft_type、handle_type、palette_style 与连续 scale。gating：base≠single_point → shaft 强制 telescoping。`resolve_config` clamp 全部 scale、解析 folding gate 与 travel cap、派生 base_top/shaft_rise/segment 长度。`slot_choices_for_seed` 返回 (base_module, shaft_module, handle_module) 与 build 完全一致（每 slot 单 candidate=已解析选择，assembler procedural over 1）。random sweep 0-35 初检，0-999 成熟审计。
Topology target：1000-seed slot choice tuple distinct ≥ 20（本类别合法拓扑上限 20，连续 scale/palette 不计入结构 distinct）；低于 300 因 base×handle×gated-shaft 组合有限——类别内在（手杖结构受限），已说明。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
Controlled local parameterization：height_scale / shaft_radius_scale / base_span_scale / telescope_travel（§7 范围 + clamp/derive）；均不破坏 InterfaceSpec（socket/tube 面派生自 base_top/shaft helper）、MatingContract、multiplicity。
Regression overrides：none。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | base→(gated)shaft→handle→palette→scales, weighted uniform | slot_choices_for_seed matches build |
| compatibility matrix | folding⇔single_point only; all handle×base legal | no floating leg/foot, no telescoping tube false-collision, fold clearance solved |
| controlled local variation | 4 continuous scales, clamped/derived | proportions vary without breaking sockets/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial, 0-999 maturity | contract failures; axis_realization |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A base | 4 | yes | yes | ③ Primary Form Family |
| B handle | 4 | yes | yes | ③ grip Planar Boundary |
| C shaft | 2 | yes | no | ② joint type; folding gated to single_point |

## Validator

- slot_choices_for_seed returns implemented module names, matching build choices
- config_from_seed uses deterministic procedural sampling for all seeds (incl. 0)
- folding gated to single_point base; illegal combos never sampled
- controlled scales clamped in resolve_config; cannot break sockets/clearance/joint origin/height
- base→shaft and shaft→handle InterfaceSpec/MatingContract faces exist and contact
- telescoping = PRISMATIC axis z; folding = REVOLUTE axis x (coupled)
- foot loop follows `leg_{i}`/`foot_{i}` naming + FIXED policy + per-foot ferrule
- overall handle-top height stays walking-cane scale (~0.82–0.98 m)

## Reject cases

- Downgrading LatheGeometry / superellipse / tube_from_spline hero meshes to bare Box/Cylinder (Rule 3).
- Feet/legs floating off the hub (missing socket overlap → isolated parts) or hub-leg overlap unscoped.
- Telescoping tube-in-tube nesting flagged as collision (missing element-scoped allow_overlap).
- Folding modeled as independent REVOLUTE joints (self-intersecting sampled poses) instead of coupled_chain.
- Fixed one-piece cane with zero non-FIXED joints (every seed must keep telescoping PRISMATIC or folding REVOLUTE).
- Handle socket not seating on shaft top (mating gap) or handle not riding the sliding member on telescoping canes.
- Monochrome output (palette_style not driving all materials).
- Multi-foot base folding (illegal combo) or underarm/forearm-crutch structure.

## 与相邻类别的边界

- 不该混入：underarm / forearm crutch（双竖管 + 腋托/前臂环 + 中轴握把——结构不同物体，fork 自 cane parent 会离开类别）。
- 不该混入：trekking pole（成对、尖齿冰爪 tip、腕带主导、无 derby/crook 手柄）。
- 不该混入：umbrella / shepherd's crook（无 ferrule + 望远镜/折叠手杖硬件）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 单一模板覆盖单点/三脚/四脚 base × 4 手柄 × telescoping/folding shaft；folding gated to single_point。 |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/C/B | single_point_base / telescoping / t_derby | rec_a-single-point-...118f96a0 | L31-239 | ferrule, hollow tube, PRISMATIC, superellipse grip |
| S2 | A | tripod_base | rec_a-...tripod...0e009043 | L56-231 | hub + 3-leg loop |
| S3 | A/C | quad_small_base / telescoping | rec_a-...quad-small...41768fed | L51-266 | plate + 4-foot loop, collar |
| S4 | A | quad_wide_base | rec_a-...quad-wide...f6e00764 | L31-224 | wide splayed 4-spline-leg base, revolved socket |
| S5 | C | telescoping (hollow upper tube) | rec_a-...bronze...74ba54ab | L63-216 | nested tube telescoping, quad feet loop |
| V1 | B | crook_handle | rec_cane_var_crook_handle | L71-107,225-250 | swept crook arc |
| V2 | B | offset_handle | rec_cane_var_offset_handle | L72-111,231-256 | swan neck + offset grip |
| V3 | B | fritz_handle | rec_cane_var_fritz_handle | L37-87,178-183 | anatomical palm grip |
| V4 | C | folding_4section | rec_cane_var_folding | L84-198 | 4-seg + 3 REVOLUTE fold |
