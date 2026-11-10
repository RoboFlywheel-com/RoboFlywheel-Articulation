# Modular Spec — Textiles_Fabric / Tailor's dummy

## 元信息
| 项 | 值 |
|---|---|
| slug | `tailor_s_dummy` |
| template path | `agent/templates/tailor_s_dummy.py` |
| test path (optional) | `tests/agent/test_tailor_s_dummy_template.py` (skipped — sweep is the acceptance signal) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern=mixed`: a single fabric torso shell on a shared telescoping vertical
stand (root = floor base, PRISMATIC height to the torso column) with parallel
articulated hardware children parented to the torso column (posable arms, sizing
dials, clamp knob, neck knob); the sizing-dial layer carries a multiplicity axis.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6 |
| read_count | 6 |
| read_scope | all 5-star samples in this category (2 origins + 4 verified variants) |
| source_index_policy | only adopted module sources are indexed below |

Read in full: S1 `rec_textiles_fabric__tailor_s_dummy__001…` (tripod, sizing dials,
telescoping pole, superellipse torso, collar+neck knobs); S2
`rec_textiles_fabric__tailor_s_dummy__002…` (5-spoke caster star base, static
wood posable arms, telescoping pole, clamp knob + wood finial); V1
`rec_tailor_s_dummy_var_arms_articulated` (S2 split into shoulder+elbow REVOLUTE
arm links); V2 `rec_tailor_s_dummy_var_base_round` (S1 tripod replaced by
LatheGeometry cast-iron domed disc); V3 `rec_tailor_s_dummy_var_dials_n6` /
V4 `…_dials_n9` (S1 dial loop extended to 6 / 9 seats across 3 z-bands).

## 核心身份

A headless, legless fabric-covered torso / dress form (shoulders-to-waist/hip
envelope) mounted on an adjustable vertical stand for fitting garments. The torso
is a single volumetric superellipse fabric shell with recessed seams; it rides a
telescoping pole (PRISMATIC height adjustment) rising from a floor base. Sizing
thumbwheels, a clamp knob and a neck knob/finial are the rotary hardware.
Not a full retail mannequin (no head, no legs, no standing figure), not a
clothing rack / coat tree, not a steamer / ironing board.

## 槽位 + 候选模块表

Torso column + telescoping pole + clamp knob + neck knob are **module-local
fixed structure** (shared spine, single honest ③ torso family; see §8.5 ③) — not
slots. Diversity is carried by the three source-backed slots below plus the dial
multiplicity axis.

### Slot A：base_support （① skeleton — floor topology）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `tripod_radial` | forked_anchor | S1 | `001…/model.py:L185-L221` | eligible if compatible | 4× radial `tripod_leg_{i}` cylinders + `foot_cap_{i}` rubber spheres around a central floor_hub; open splayed legs |
| `star_caster_rolling` | forked_anchor | S2 | `002…/model.py:L200-L221` | eligible if compatible | central hub + dome, 5× `spoke_{i}` swept tube legs each ending in `caster_fork_{i}` box + `caster_wheel_{i}` cylinder; rolling star base |
| `round_cast_disc` | forked_anchor | V2 | `…_base_round/model.py:L175-L219` | eligible if compatible | single solid `LatheGeometry` domed cast-iron disc + short `pedestal_collar`; closed weighted floor |

### Slot B：arms （① skeleton + ② joint — appendage topology）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `armless` | forked_anchor | S1 | `001…/model.py` (no arm parts/visuals) | eligible if compatible | no arm geometry — bare shoulder taper; 0 arm parts, 0 arm joints |
| `static_wood_arms` | forked_anchor | S2 | `002…/model.py:L257-L262` | eligible if compatible | folded wooden artist arms as `wood_arm_*`/`wood_hand_*` mesh visuals on the torso column + shoulder/elbow/wrist balls; NO joints (rigid decoration) |
| `articulated_posable_arms` | forked_anchor | V1 | `…_arms_articulated/model.py:L298-L443` | eligible if compatible | each arm split into `upper_arm_{i}` + `forearm_{i}` parts joined by REVOLUTE `shoulder_{i}` + `elbow_{i}` at ball mounts; posable |

### Slot C：adjustment （② joint — sizing mechanism）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `sizing_dials` | forked_anchor | S1 / V3 / V4 | `001…/model.py:L320-L340,L376-L386`; `…_dials_n9/model.py:L320-L391` | eligible if compatible | N `front_dial_{i}` parts (dial_stem + dial_face + screw_slot) each on its own CONTINUOUS `torso_to_front_dial_{i}` thumbwheel joint, seated on the torso surface; N is the multiplicity axis |
| `fixed_pinnable` | forked_anchor | S2 | `002…/model.py` (no dials) | eligible if compatible | no sizing wheels — a plain pinnable canvas form; 0 dial parts, 0 dial joints |

硬约束满足情况：
- Slot A 3 candidates, Slot B 3 candidates — 均 ≥3。
- Slot C 降到 2 candidate（`sizing_dials` / `fixed_pinnable`）：理由——真实样本池里只有两种 source-backed 的 adjustment 拓扑（S1 有连续 thumbwheels，S2 完全无 dials）；不存在第三种结构不同的调节机构来源（棘轮/滑块等均未被任何 5-star 资产支撑），造第三个会违反 Rule 3。
- 每个 candidate 都有 `source_type=forked_anchor` + `model.py:Lx-Ly` 来源。
- 无 `world_knowledge_extrapolation` skeleton/joint candidate；④ 装饰仅作宿主 visual。

## 槽位图（slot graph）

pattern: mixed

```
[base_support] --base_to_column PRISMATIC(z, height 0..~0.24)--> (column: pole+torso+neck)
     |                                                                 |
     +--base_to_clamp_knob CONTINUOUS(collar side)--> clamp_knob       +--column_to_top_knob CONTINUOUS(neck top)--> top_knob
                                                                       +--shoulder_{i} REVOLUTE / static visual --> arms  (Slot B, parallel on column)
                                                                       +--torso_to_front_dial_{i} CONTINUOUS --> front_dial_{i}  (Slot C, parallel on column)
```

- Root = `base` part (grounded floor). The shared spine `column` (inner_pole +
  support_plate + torso_shell + seams + neck_cap) is a PRISMATIC child of `base`
  (telescoping height). Slot A only changes the floor topology under the shared
  `outer_sleeve`/`height_collar` pole hardware.
- Interface base↔column: `inner_pole` (column) is retained inside `outer_sleeve`
  + `height_collar` (base) along the vertical Z symmetry axis — telescoping
  pin-in-sleeve; joint origin on the sleeve axis. PRISMATIC, grandfathered
  (captured-member overlap, no MatingContract — see §13).
- Arms (Slot B) parent to `column` at shoulder balls (`shoulder_{i}` REVOLUTE
  pivots at the shoulder-ball spheres; `elbow_{i}` at elbow balls). `static_wood_arms`
  emits torso visuals only (no joint); `armless` emits nothing.
- Dials (Slot C) parent to `column`; each dial pivots CONTINUOUS about its stem
  axis normal to the torso surface at `_torso_surface(theta, z)`.
- Clamp knob (base collar) + neck knob (column neck) are always-present rotary
  hardware (fixed structure), CONTINUOUS about their own axes.

## 每槽位 Module Emits / Interfaces

### Slot A / base_support
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (single part) | S1/S2/V2 |
| internal joints | none (floor topology is one rigid part) | — |
| upstream interface | root (grounded); no upstream | — |
| downstream interface | vertical Z pole axis: `outer_sleeve` + `height_collar` top → consumer PRISMATIC height joint to `column` | S1 L192-L203 |

### column (fixed spine)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `column` (inner_pole, support_plate, torso_shell, front/side seam, waist_band, neck_cap, neck_plug; + shoulder balls if arms present) | S1 L223-L270 |
| internal joints | none | — |
| upstream interface | `inner_pole` bottom retained in base sleeve (PRISMATIC consumer) | S1 L223-L236 |
| downstream interface | torso surface `_torso_surface(theta,z)` (dials), shoulder balls (arms), neck top (top_knob) | S1 |

### Slot B / arms
| emits | 描述 | 来源 |
|---|---|---|
| parts | `upper_arm_{i}`,`forearm_{i}` (articulated) / none (static → column visuals) / none (armless) | V1 L318-L353 |
| internal joints | `shoulder_{i}` REVOLUTE axis (0,∓side,0); `elbow_{i}` REVOLUTE axis (-1,0,0) | V1 L416-L443 |
| upstream interface | shoulder ball on `column` (parallel-children; no chain joint) | V1 L309-L316 |
| downstream interface | none (leaf) | — |

### Slot C / adjustment
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_dial_{i}` ×N (sizing_dials) / none (fixed_pinnable) | S1 L320-L340 |
| internal joints | `torso_to_front_dial_{i}` CONTINUOUS axis z (dial spin) | S1 L376-L386 |
| upstream interface | torso surface seat (parallel-children; no chain joint) | S1 L376-L378 |
| downstream interface | none (leaf) | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| base_support | enum | tripod_radial / star_caster_rolling / round_cast_disc | tripod_radial | choice | deterministic sampler | Slot A |
| arms | enum | armless / static_wood_arms / articulated_posable_arms | armless | choice | deterministic sampler | Slot B |
| adjustment | enum | sizing_dials / fixed_pinnable | sizing_dials | choice | deterministic sampler | Slot C |
| dial_count N | int | [3, 10] | 3 | conditional | only when adjustment=sizing_dials；权重档小 N 偏多 | §8 |
| material_style | enum | neoprene_grey / cream_canvas / cast_iron_chrome | neoprene_grey | choice | palette only（ride-along） | ⑥ |
| torso_width_scale | float | [0.90, 1.12] | 1.0 | independent | clamp；缩放 torso 截面 width/depth（seam/dial 由 `_torso_surface` 派生共形） | S1 L23-L33 |
| base_radius_scale | float | [0.90, 1.15] | 1.0 | independent | clamp；缩放 floor footprint（legs/spokes/disc 半径） | S1 L204-L221 |
| height_travel | float | [0.20, 0.26] | 0.24 | independent | clamp；PRISMATIC upper 行程 | S1 L349 |
| shoulder_span | float | derived | — | equation | `= f(torso_width_scale)` 由 `_torso_surface(0, z_shoulder)` 求得，不独立采样 | column surface |
| dial seat (theta,z) | derived | derived | — | equation | 由 `_torso_surface(theta,z)` 逐-z 派生，共形嵌入 | S1 L64-L81 |
| (—) | constraint | — | — | inequality | 相邻 dial 中心间距 ≥ 0.028（sweeping screw_slot 半径 ~0.010 不互撞）；违反时减 N 或改 seat | 接口 clearance |

## 参数范围汇总 — 编译预算 / compile budget（必填）

自报预算：**每 seed ≤ 20s**（低复杂度类：一个 superellipse torso loft `segments=72`，
一个 LatheGeometry disc `segments=64`，其余 Cylinder/Box/Sphere + 少量 tube_from_spline
arms）。分档 tessellation：torso loft 72 段（英雄面），disc 64 段，dial/knob 小特征
≤32 段；N 个 dial 复用同一 build helper；arms tube radial ≤16 段。实测应落在 5-12s。

## Multiplicity / Copy Logic

- **axis 1 — sizing dials（唯一 multiplicity 轴）**
  - `count_param`: `dial_count` N（front/side sizing thumbwheels）。
  - `N_range`: 产品域 [3, 10]（真实可调形常带 8-10 只围绕 bust/waist/hip）；测试域同。
  - sampling domain（权重档）: 小 N 高频（3-4 常见）、大 N（8-10）稀有；`fixed_pinnable`
    时 N=0（不采样）。
  - copied object: `front_dial_{idx}` part（dial_stem + dial_face + screw_slot）+
    CONTINUOUS joint `torso_to_front_dial_{idx}`。
  - naming: `front_dial_{idx}` / `torso_to_front_dial_{idx}`（stable indexed）。
  - placement: 3 个 z-band（hip≈0.17 / waist≈0.35 / bust≈0.52）× front/left/right seats，
    由 `_torso_surface(theta, z)` 逐-z 派生，间距 ≥0.028。
  - joint policy: 每 dial 各自 CONTINUOUS thumbwheel joint，轴为其 stem 法线。
  - source/gating: S1(N=3)/V3(N=6)/V4(N=9)；仅在 adjustment=sizing_dials 时生效。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | base floor 拓扑 tripod(S1)/star-caster(S2)/round-disc(V2)；arm 拓扑 armless(S1)/arms-present(S2,V1)；均 forked_anchor |
| └ multiplicity | 同构件 ×N | 有 | dial N∈[3,10]，见 §8（S1/V3/V4） |
| ② 关节类型 | 图不变，换 type/轴 | 有 | PRISMATIC 升降(S1,S2)；CONTINUOUS 每 dial thumbwheel(S1)；CONTINUOUS clamp knob + neck knob(S1)；REVOLUTE shoulder+elbow 关节臂(V1)；均 forked_anchor，声明的每种都在 sweep 出现 |
| ③ 主体形态家族 | 换核心 part 的可识别几何原型 | 无 | 单一 volumetric 织物躯干 superellipse 包络（Volumetric Envelope Form）。两个 origin 共享同一 body family；male/child/hip-length 属比例差异（⑤），不是结构不同的 ③ 族——record_only，不造第二个 ③ candidate 以免 padding（planner `underfilled_reason`）。主多样性由 ① base/arms slot 承载（真实结构差异，非尺寸/涂装） |
| ④ 表面装饰 | 原型不变，叠表面细节 | 有 | recessed front/side vertical seams、waist band、neck cap、dial faces/screw slots（record_only，S1 L245-L270）。装饰几何**由 `_torso_surface(theta,z)` 逐-z 派生**、随 ③ 单一形态 + ⑤ torso_width_scale 共形嵌入（派生顺序 ③→⑤→④） |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | torso_width_scale[0.90,1.12]、base_radius_scale[0.90,1.15]（§7）。运动包络：PRISMATIC 升降 axis z / 向上 / [0, 0.20..0.26]；CONTINUOUS dials & knobs 整圈；REVOLUTE shoulder axis(0,∓side,0) 抬臂方向 [-0.30, 1.20]；REVOLUTE elbow axis(-1,0,0) 屈肘 [-0.20, 1.80]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)`；targeted `ctx.pose`：升降抬升 torso、shoulder 正向抬臂、elbow 正向屈肘、dial 关节存在性；continuous dial/knob 全圈轴对称不穿模，无需额外 qc_samples |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted-fabric / metal / wood：neoprene_grey(S1)、cream_canvas(S2)、cast_iron_chrome(V2) ≥3 配色；材质大类覆盖 ≥ ceil(0.5×3)=2（fabric+metal 必现，wood 随 arms） |

**收尾自检**：base 三种 floor 拓扑、arms 三态、dial N 档、三种 palette 需在 `template batch`
0-9 渲染肉眼可见；seam/dial 贴合 torso 不悬空；升降与关节臂全程不穿模。（batch 目检本阶段 SKIP，交主循环统一跑。）

## 采样与覆盖审计

总组合数：base(3) × arms(3) × adjustment(2) = 18 骨架组合 × dial_count N(∈[3,10]，8 档，仅
sizing_dials 生效) × palette(3) → 有效离散拓扑组合 ≈ 18 + N 档扩展；1000-seed slot-choice
tuple 覆盖用于成熟度观察。

理由：低复杂度类，honest 结构词汇小；离散多样性主要来自 ① base/arms 与 dial 多样性。

seed_domain_policy：procedural_first（`config_from_seed` 对所有 seed 含 seed 0 走
`random.Random(seed)` 采样；seed 0 不特殊）。
Procedural Sampling / Sweep Plan：每 slot 独立加权 `rng.choice`；`resolve_config` 内 clamp
连续 scale、解析 conditional N（N 仅在 sizing_dials 时采）、应用兼容 gating（见下）。无
regression overrides。random sweep seeds 0-35 初判，0-999 成熟度审计。
Topology target：18 骨架 × N 档，低于 300 属实——真实组合空间受单一 torso 家族 + 小 honest
adjustment 词汇上限限制（report-only，不 gate）。
Controlled local parameterization：torso_width_scale、base_radius_scale、height_travel
（§7，均 independent，clamp）；shoulder_span 与 dial seat 由 `_torso_surface` 派生
（equation），不破坏接口/clearance/joint origin/multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 base→arms→adjustment→dial_count；各 weighted choice；N 仅在 sizing_dials | slot_choices_for_seed matches build choices |
| compatibility matrix | fixed_pinnable ⟹ N=0（无 dial part/joint）；armless ⟹ 无 arm part/joint；round_disc/star/tripod 均与共享 pole/torso 接口兼容（无非法组合） | no floating, collision, axis, max multiplicity |
| controlled local variation | torso_width_scale / base_radius_scale / height_travel clamp | proportions vary without breaking interfaces, clearance, joint origin, identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass, 0-999 maturity | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| base_support | 3 | yes | yes | |
| arms | 3 | yes | yes | |
| adjustment | 2 | yes | no | 源池仅两种 adjustment 拓扑，理由见槽位表 |

## Validator

- slot_choices_for_seed returns implemented module names (+ dial_count band)
- config_from_seed uses deterministic procedural sampling for all ordinary seeds (seed 0 not special)
- compatibility gating: fixed_pinnable→N0, armless→no arm joints
- no regression overrides
- controlled local scale params clamped in resolve_config; can't break interfaces / clearance / joint origin
- critical support: inner_pole retained in sleeve (allow_overlap), dial stems seat on torso, arm tubes rooted in balls
- key joints: base_to_column PRISMATIC z; torso_to_front_dial_* CONTINUOUS; shoulder_*/elbow_* REVOLUTE; clamp/neck knob CONTINUOUS
- copied dials follow `front_dial_{idx}` naming, seated via `_torso_surface`

## Reject cases

- torso becomes a full mannequin (head/legs added) or splits into hinged panels (not source-backed).
- base floor floats / pole not centered on floor topology.
- dials or seams built at constant radius (detached from tapered torso) — must derive from `_torso_surface`.
- articulated arm swings through the torso or arm tubes detach from shoulder/elbow balls at any sampled pose.
- PRISMATIC height fails to raise the torso, or inner_pole leaves the sleeve at full extension.
- dial_count sampled while adjustment=fixed_pinnable (illegal combo).
- adding a non-source-backed adjustment mechanism (ratchet/slider) to pad Slot C.

## 与相邻类别的边界

- 不该混入：retail mannequin（有头/四肢/站姿）——dress form 无头无腿，只有躯干envelope。
- 不该混入：clothing rack / coat tree / valet stand——那是挂衣杆非织物躯干。
- 不该混入：garment steamer / ironing board——无躯干成形面。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | ③ primary-form 单一（planner underfilled_reason，① base/arms 承载主多样性）；Slot C 降 2 candidate 已说明源池上限 |

## 模板实现备注（可选）

- 共享 helper：`_torso_sections(width_scale)` / `_torso_surface(sections,theta,z)` /
  `_make_torso_mesh` / `_make_vertical_seam` / `_make_waist_band`（S1 派生）；
  `_emit_stand_sleeve`（三种 base 共用 outer_sleeve+height_collar）；`_emit_dial`（N 复用）；
  arm tube helper（V1 派生）。
- InterfaceSpec/MatingContract：本模板全部 joint 为 telescoping / captured-pin / ball-mount /
  surface-seated thumbwheel，几何不是两个 axis-aligned 面贴合，按 §B 惯例 **grandfather**
  （omit `mating`），用 element-scoped `allow_overlap` 声明：`outer_sleeve∩inner_pole`、
  `height_collar∩inner_pole`、`dial_stem∩torso_shell`、`shoulder_ball∩upper_arm`、
  `elbow_ball∩forearm`、`upper_arm∩forearm`（elbow junction）。
- captured-pin overlap 均 element-scoped、局部、有 reason，不用 part 级宽 allow。
- Rule 5：非 FIXED joint 存在 → run_tests 调 `fail_if_parts_overlap_in_sampled_poses`
  + targeted `ctx.pose`（升降 / shoulder / elbow）。
