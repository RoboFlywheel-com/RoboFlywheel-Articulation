# Modular Spec — Astronomy / Return capsule

## 元信息
| 项 | 值 |
|---|---|
| slug | `Astronomy_Return_capsule` |
| template path | `agent/templates/Astronomy_Return_capsule.py` |
| test path (optional) | `tests/agent/test_Astronomy_Return_capsule_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (root capsule body + parallel-children crew_hatch + parallel-children heat_shield + 2 decoration multiplicity axes) |
| function stem | `astronomy_return_capsule` (exports `build_astronomy_return_capsule`, `config_from_seed`, `run_astronomy_return_capsule_tests`) |

`pattern = mixed`: a single root `capsule` part (the crewed descent body) carries
two parallel-children slots that each manually parent their articulations to the
capsule (no serial chain joint): a crew **hatch** closure on the top collar and a
base **heat shield**. Two decoration multiplicity axes ride on top: `porthole_count`
and `rcs_count` (both are host-conformal surface details fused onto the capsule body).

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this subclass (origin 母本 + 8 forked variants) |
| source_index_policy | only adopted module sources are indexed below; all 9 were read in full |

Samples (all `collections=["workbench"]`, `rating=5`, synced from `articraft_data`):

- `rec_a-landed-shenzhou-style-return-capsule-a-bell-sh_...328c39d9` — ORIGIN 母本
  (bell-shaped LatheGeometry body, fused heat shield, hinged REVOLUTE crew hatch,
  2 portholes, 4 RCS ports, 6 scorch streaks).
- `rec_return_capsule_var_conical_command_module` — ③ form: bell -> straight Apollo
  conical frustum (2-segment lathe taper).
- `rec_return_capsule_var_spherical_descent` — ③ form: bell -> near-spherical Vostok
  descent ball (sphere-arc lathe via `_sphere_r(z)`).
- `rec_return_capsule_var_plug_hatch` — ② joint: crew hatch REVOLUTE -> PRISMATIC
  plug hatch (lifts straight out along +Z; adds `plug_seal_collar`).
- `rec_return_capsule_var_docking_nose` — ① skeleton: adds a forward docking ring +
  a second moving part `nose_cover` on a REVOLUTE hinge at the +X ring rim.
- `rec_return_capsule_var_separable_shield` — ① skeleton + ② joint: heat shield split
  into its own part on a PRISMATIC drop-away joint (-Z jettison).
- `rec_return_capsule_var_portholes_four` — ④ decoration multiplicity: portholes 2 -> 4.
- `rec_return_capsule_var_rcs_ports_eight` — ④ decoration multiplicity: RCS ports 4 -> 8.
- `rec_return_capsule_var_rcs_ports_twelve` — ④ decoration multiplicity: RCS ports 4 -> 12.

## 核心身份

A **landed / recovered crewed spacecraft return (descent / re-entry) capsule**: a
blunt-based ablative crew module modeled upright on its charred **heat shield**,
with a scorched tan-bronze **body** (bell / Apollo conical frustum / Vostok
spherical descent ball), a grey **hatch collar + white seal ring** on the flat top
face, a dark cabin recess, round **portholes**, radial **RCS thruster ports** near
the base, and dark re-entry **scorch streaks** swept up the wall. At least one real
non-fixed joint is always present: the **crew hatch** either swings open on a
REVOLUTE hinge (Shenzhou/Soyuz recovery pose) or lifts out on a PRISMATIC plug
axis; optionally a forward **docking-section nose cover** swings open (REVOLUTE) and
/ or the **heat shield** jettisons on a PRISMATIC drop-away joint. Default mature
domain: a ~2.5 m-across single-crew-module bell with a hinged hatch and a fused shield.

Not to be confused with the neighbouring picture subclass **Astronomy / Space
shuttle** (a winged glider, not a blunt axisymmetric capsule) nor **Astronomy /
Rocket engine / Antenna dish** (propulsion / ground assemblies). The return capsule
is a self-contained blunt re-entry body whose only appendages are its hatch and its
(optionally separable) shield — no wings, no engines, no ground pedestal.

## 槽位 + 候选模块表

### Slot A：body_form (root · ③ Primary Form Family)

The root descent body. Same part tree across candidates: one revolved body visual +
`hatch_collar` (shell ring) + `hatch_seal_ring` + `cabin_recess` + N `porthole_*`
pairs + N `rcs_port_*` + 6 `scorch_streak_*` (all fused as `capsule` part visuals,
Rule 1). Only the body envelope prototype changes; all three expose the identical
mounting envelope (`top_z` collar seat + `_body_radius(z)` conformal wall) so the
downstream hatch / shield slots are form-independent.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `bell_body` | forked_anchor (origin) | `rec_a-...328c39d9` | L80-L96 | eligible | multi-segment `LatheGeometry` bell (wide above shield, narrowing to flat top). **Volumetric Envelope Form** |
| `conical_frustum` | forked_anchor | `rec_return_capsule_var_conical_command_module` | L78-L96 | eligible | straight Apollo conical frustum: 2-segment `LatheGeometry` taper (rim 1.24 -> top 0.79). **Volumetric Envelope Form** |
| `spherical_ball` | forked_anchor | `rec_return_capsule_var_spherical_descent` | L51-L75, L107-L109 | eligible | near-spherical Vostok descent ball: `LatheGeometry` sphere arc `_sphere_r(z)`, truncated flat top. **Volumetric Envelope Form** |

### Slot B：crew_hatch (parallel child on top collar · ① skeleton + ② joint)

The category-defining moving closure on the top collar. Each candidate emits the
`hatch` part + its drive joint (parented directly to the capsule) and adds its own
capsule-side mount hardware (hinge posts / collar bore) as capsule visuals. The
hinge barrel / plug collar is a captured pivot -> joint grandfathered (no
MatingContract), element-scoped `allow_overlap` (Rule 2 captured-pivot exception,
exactly as every source declares).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `hinged_hatch` | forked_anchor (origin) | `rec_a-...328c39d9` | L164-L240 | eligible | 1 moving part `hatch`: domed `lid_shell` (lathe) + viewport + grab handle + `hinge_barrel` + straps; `capsule_to_hatch` **REVOLUTE** axis Y at the -X collar edge, lower=0 upper~2.0 (swings up-over). 2 `hinge_post_*` on capsule. |
| `plug_hatch` | forked_anchor | `rec_return_capsule_var_plug_hatch` | L170-L245 | eligible | ② joint change: same domed lid + `plug_seal_collar` (shell) on underside; `capsule_to_hatch` **PRISMATIC** axis +Z at the seal-ring top, lower=0 upper~0.30 (lifts straight out). No hinge posts. |
| `docking_hatch` | forked_anchor | `rec_return_capsule_var_docking_nose` | L184-L353 | eligible | ① skeleton change: hinged crew hatch (REVOLUTE, as `hinged_hatch`) PLUS a `docking_ring` + `dock_guide_*` + `nose_hinge_post_*` on the capsule and a SECOND moving part `nose_cover` (thin-wall dome `nose_shell` + `nose_hinge_barrel` + straps) on `capsule_to_nose_cover` **REVOLUTE** axis Y at the +X ring rim, lower=0 upper~2.0 (swings +X). |

### Slot C：heat_shield (parallel child at the base · ① skeleton + ② joint)

The base ablative shield. Two structurally distinct skeletons only — the confirmed
pool contains exactly these two shield realizations (fused vs separable), so this
slot degrades to **2 candidates** (justified: no third shield skeleton exists in the
9-sample pool; a re-skin would not be structurally distinct per AUTHORING §B).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `fixed_shield` | forked_anchor (origin) | `rec_a-...328c39d9` | L62-L76 | eligible | 0 extra parts / 0 joints: charred `heat_shield` (`LatheGeometry` disc) fused as a capsule visual under the body (like Tipping_Barrow `stand_legs` -> `parts_emitted=[]`). |
| `separable_shield` | forked_anchor | `rec_return_capsule_var_separable_shield` | L160-L177, L247-L258 | eligible | ① skeleton + ② joint: identical shield geometry as its OWN part `shield`; `capsule_to_shield` **PRISMATIC** axis -Z at (0,0,0), lower=0 upper~1.0-1.5 (Apollo/Dragon jettison), flush-seated at q=0. |

硬约束满足：body_form=3、crew_hatch=3 达到 3-6 目标；heat_shield=2（样本池仅有 fused /
separable 两种 shield 骨架，已说明理由，非 re-skin）。每个 candidate 有 forked_anchor +
`model.py:Lx-Ly`；无 `world_knowledge_extrapolation` candidate（③ 三个主体形态均 source-backed）。

## 槽位图（slot graph）

pattern: `mixed` (root + parallel children + multiplicity)

```
body_form (root capsule; bell / conical frustum / spherical ball)
   ├─[top collar seat (0,0,top_z) · REVOLUTE(Y, -X edge) or PRISMATIC(+Z); captured barrel/plug]→ crew_hatch  (1 part, or +nose_cover 2nd REVOLUTE part for docking)
   └─[base plane (0,0,0) · none (fused) or PRISMATIC(-Z drop-away); flush-seated]→ heat_shield  (0 parts, or separable shield part)
```

- **slot 顺序 / parent**：`body_form` (capsule) 是 root，唯一被复用的 parent。`crew_hatch`
  与 `heat_shield` 都直接把各自 joint 的 `parent=capsule`，互不串联（parallel children）。
  两者只声明 `downstream`（re-export capsule），不声明 `upstream`，因此 assembler 不发射
  自动 chain joint（各模块自己发原始 joint，与 5 星源一致，同 Tipping_Barrow 惯用）。
- **接口点位**：crew_hatch -> capsule 顶 collar seat；REVOLUTE hinge 原点在 -X collar 边
  `(-0.49·cs, 0, 2.40·cs)`（capsule 有 `hinge_post_*`，hatch 有 `hinge_barrel` 在其原点）；
  PRISMATIC plug 原点在 seal-ring 顶 `(0,0,2.37·cs)`；docking nose 原点在 +X ring rim
  `(0.35·cs, 0, 2.49·cs)`。heat_shield -> capsule 基面 `(0,0,0)`（shield 顶 `heat_shield`
  与 bell 底 flush-seated）。
- **跨 slot joint type/axis/range**：crew hatch REVOLUTE(Y, [0, hatch_open≈2.0]) 或
  PRISMATIC(Z, [0, plug_travel≈0.30·cs])；nose_cover REVOLUTE(Y, [0, nose_open≈2.0])；
  shield PRISMATIC(-Z, [0, shield_drop≈1.2·cs])。
- **互斥/派生**：body 形态与 hatch/shield 完全正交（挂点仅随 `capsule_scale` 派生，与形态
  无关）。`plug_hatch` 无 hinge posts；`docking_hatch` 强制附带 nose_cover 第二关节；
  `fixed_shield` 无独立 part / joint。

## 每槽位 Module Emits / Interfaces

### Slot A / module bell_body | conical_frustum | spherical_ball
| emits | 描述 | 来源 |
|---|---|---|
| parts | `capsule` (single root part) | origin L60 |
| visuals | `bell_body` (bell/frustum/sphere lathe) + `hatch_collar` + `hatch_seal_ring` + `cabin_recess` + `porthole_rim_{i}`/`porthole_glass_{i}` (×N) + `rcs_port_{i}` (×N) + `scorch_streak_{i}` (×6) | origin L62-L162 |
| internal joints | none (root, static body) | — |
| downstream interface | `capsule` part, `bell_body` visual, face `positive_z`, anchor `(0,0,top_z)` (informational; children wire manually) | — |

### Slot B / module hinged_hatch | plug_hatch | docking_hatch
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hatch` (+ `nose_cover` for docking) | origin L174; docking L295 |
| capsule visuals added | `hinge_post_{0,1}` (hinged/docking); `docking_ring` + `dock_guide_{0..5}` + `nose_hinge_post_{0,1}` (docking) | origin L165-L171; docking L184-L224 |
| hatch visuals | `lid_shell` (lathe dome) + `viewport_rim` + `viewport_glass` + `handle_post_*` + `handle_bar` + `hinge_barrel` + `hinge_strap_*`; plug: `plug_seal_collar`; nose_cover: `nose_shell`+`nose_hinge_barrel`+`nose_strap_*` | origin L175-L230; plug L185-L195; docking L294-L340 |
| internal joints | `capsule_to_hatch` REVOLUTE(Y) or PRISMATIC(Z) (+ `capsule_to_nose_cover` REVOLUTE(Y) for docking) | origin L232-L240; plug L237-L245; docking L343-L353 |
| upstream interface | **none declared** (parallel-children; parents joints directly to `capsule`) | — |
| downstream interface | re-export capsule downstream (passthrough) | — |

### Slot C / module fixed_shield | separable_shield
| emits | 描述 | 来源 |
|---|---|---|
| parts | none (fused) or `shield` (separable) | separable L160 |
| visuals | `heat_shield` (`LatheGeometry` disc) as a capsule visual (fused) or on the `shield` part (separable) | origin L62-L76; separable L160-L177 |
| internal joints | none (fused) or `capsule_to_shield` PRISMATIC(-Z) | separable L247-L258 |
| upstream / downstream interface | none declared / re-export capsule (passthrough) | — |

活动件语义：crew hatch 开启/展开；nose_cover 打开前向对接口；shield 抛离。不动细节
（collar/seal/cabin/portholes/RCS/streaks/docking ring/guide tabs/hinge posts）写成宿主
`capsule` visual，非独立 part（Rule 1）。captured hinge barrel / plug collar / flush shield
用 element-scoped allow_overlap（Rule 2 例外），REVOLUTE 原点落在 collar-edge 真实
hinge-post / barrel 几何（origin honesty）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_form` | enum | bell_body / conical_frustum / spherical_ball | bell_body | choice | procedural sampler | Slot A |
| `hatch_module` | enum | hinged_hatch / plug_hatch / docking_hatch | hinged_hatch | choice | procedural sampler | Slot B |
| `shield_module` | enum | fixed_shield / separable_shield | fixed_shield | choice | procedural sampler | Slot C |
| `palette_style` | enum | 6 colorways (see §⑥) | shenzhou_bronze | choice | procedural sampler | palette |
| `porthole_count` | int | {2,4} (obs: 2 origin, 4 portholes_four) | 2 | independent | weighted `{2:0.6, 4:0.4}` | origin L130, portholes_four L129 |
| `rcs_count` | int | {4,8,12} (obs: 4 origin, 8/12 variants) | 4 | independent | weighted `{4:0.5, 8:0.3, 12:0.2}` | origin L39, eight/twelve L39 |
| `capsule_scale` | float | [0.85, 1.20] | 1.0 | independent | uniform; scales radius+height+all mount z together (mating preserved) | origin L33-L37 |
| `radius_scale` | float | [0.92, 1.10] | 1.0 | independent | body-wall + conformal decoration + shield disc radial multiplier (proportion knob) | origin L80-L90 |
| `hatch_open` | float | [1.6, 2.2] | 2.0 | conditional | REVOLUTE crew hatch upper (rad); only hinged/docking | origin L37 |
| `plug_travel` | float | [0.18, 0.38] | 0.30 | conditional | PRISMATIC plug upper (m, ×capsule_scale); only plug_hatch | plug L36 |
| `nose_open` | float | [1.6, 2.2] | 2.0 | conditional | REVOLUTE nose cover upper (rad); only docking_hatch | docking L51 |
| `shield_drop` | float | [0.9, 1.5] | 1.2 | conditional | PRISMATIC shield jettison upper (m, ×capsule_scale); only separable_shield | separable L257 |

所有 conditional 在 `resolve_config` 内解析（按所选 module 决定是否生效）；builder 不失败。
`radius_scale` 只乘入 body 轮廓半径、`_body_radius(z)` 装饰径向落点与 shield 盘半径；collar /
hatch / nose / shield-drop 轴的挂点仅随 `capsule_scale`（均匀）派生，故 mating 关系与形态、
proportion 正交。

## 7.5 编译预算 / compile budget（必填）

**Per-seed compile budget: <= 15 s** (hang-guard `--compile-timeout 60`). Geometry is
a handful of `LatheGeometry` revolves at <=48 segments (body, shield, collar shell,
lid dome, plug/nose shells) + cheap `Box`/`Cylinder` decoration. No boolean sculpting,
no tube splines. All N portholes / RCS ports reuse the same small `Cylinder`. Tiers:
body/shield/lid/collar lathe <=48 seg; small cylinders default. Expect 4-9 s/seed;
downgrade lathe seg counts first if over.

## Multiplicity / Copy Logic

**两根独立 multiplicity 轴**（均为 ④ 表面装饰数量：宿主 `capsule` visual，随 ③ 形态 /
`radius_scale` 共形派生，不加/不减会动的 part -> 不计入结构 distinct，只覆盖）：

### 轴 1 — `porthole_count`（舷窗对数）
- `count_param`: `porthole_count`; `N_range` product `{2,4}`, test `{2,4}`; sampling
  domain 加权：`{2: 0.6, 4: 0.4}`（小 N 偏多）。
- copied object: 每扇 `porthole_rim_{i}` + `porthole_glass_{i}` 一对 `Cylinder`（rim + dark
  glass），沿 body 赤道均匀方位角 `ang = i·2π/N`，径向落点 `_body_radius(z_port)`（共形）。
- naming: `porthole_rim_{i}` / `porthole_glass_{i}`。placement: real body wall at z≈1.35·cs。
  joint policy: 无（装饰 visual）。
- source/gating: origin (N=2) L130, portholes_four (N=4) L129；全形态通用。

### 轴 2 — `rcs_count`（径向 RCS 推进口数）
- `count_param`: `rcs_count`; `N_range` `{4,8,12}`, test `{4,8,12}`; sampling domain 加权：
  `{4: 0.5, 8: 0.3, 12: 0.2}`（大 N 稀有）。
- copied object: 每个 `rcs_port_{i}` `Cylinder`，近基座 z≈0.50·cs 均匀方位角，径向落点
  `_body_radius(z_rcs)`（共形）。
- naming: `rcs_port_{i}`。placement: real body wall near the base。joint policy: 无（装饰 visual）。
- source/gating: origin (N=4) L39,L145, rcs_ports_eight (N=8)/rcs_ports_twelve (N=12) L39；全形态通用。

数量变化不改主体形态 / 机制（仍是同一 body + hatch + shield）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 结构骨架 candidate：crew_hatch 单动件（hinged/plug, forked_anchor）／docking_hatch 双动件（+nose_cover REVOLUTE part, docking_nose forked_anchor）；heat_shield fused（0 动件, origin）／separable（+shield PRISMATIC part, separable_shield forked_anchor）。全部 source-backed。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：porthole_count {2,4}（origin/portholes_four），rcs_count {4,8,12}（origin/eight/twelve）。均为 ④ 装饰数，不计结构 distinct。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | crew hatch REVOLUTE(Y)（origin）↔ PRISMATIC(Z)（plug_hatch）；nose_cover REVOLUTE(Y)（docking）；shield PRISMATIC(-Z)（separable）。全部 forked_anchor；每种类型都在 sweep 中出现。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | **登记进 slot_choices 的 body_form slot**：bell（origin）/ conical frustum（conical_command_module）/ spherical ball（spherical_descent）；form_subtype = Volumetric Envelope Form ×3；全部 forked_anchor。 |
| ④ 表面装饰 | 原型不变叠加表面细节 / 改装饰数 | 有 | `scorch_streak_*`（×6 深色再入烧蚀条）、`porthole_*`（×{2,4}）、`rcs_port_*`（×{4,8,12}）、`hatch_collar`/`hatch_seal_ring`/`cabin_recess`、docking `docking_ring`/`dock_guide_*` — 均为宿主 `capsule` visual，装饰径向落点由 `_body_radius(z)` 逐-z 派生、随 ③（形态）/⑤（radius_scale/capsule_scale）共形嵌入（派生顺序 ③→⑤→④）。source_type=record_only（origin/portholes_four/rcs_eight/rcs_twelve/docking_nose）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | §7 连续 scale：capsule_scale[0.85,1.20]（均匀）、radius_scale[0.92,1.10]（body 胖瘦 proportion）。关节运动包络（每个非-continuous joint）：crew hatch REVOLUTE axis Y，开向 up-over -X，[闭合 0, 可行 hatch_open<=2.2]；plug PRISMATIC axis +Z，[0, plug_travel<=0.38·cs]；nose_cover REVOLUTE axis Y，开向 +X，[0, nose_open<=2.2]；shield PRISMATIC axis -Z，[0, shield_drop<=1.5·cs]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)`；targeted `ctx.pose` — crew hatch 开启位移 lid、nose_cover 开启上抬 dome、shield 抛离下移。无 continuous 关节。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted/metal；配色 6 colorway：`shenzhou_bronze`（origin 炭褐 bell + 灰 collar + 白 seal）、`apollo_silver`（裸金属银）、`soyuz_olive`（橄榄烧蚀）、`charred_black`（深烧蚀）、`dragon_white`（现代白灰）、`orion_tan`（棕褐烧蚀）。材质大类覆盖 >= ceil(0.5×6)=3。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 bell/conical/sphere 三种 body、hinged/plug/docking
三种 hatch、fused/separable 两种 shield、2/4 舷窗与 4/8/12 RCS、材质配色多样、hatch/nose/shield
全程不穿模。

## 采样与覆盖审计

总组合数（distinct slot-choice tuple 上界，不含 ④ 装饰数）：
- body 3 × hatch 3 × shield 2 = **18** 结构 tuple；乘 porthole 2 × rcs 3 = 108 含装饰变体。

理由：18 结构 tuple < 富类别建议 300，因为真实结构词汇在此高度收敛——所有样本共享同一
「blunt 再入体 + 顶 hatch + 底 shield」cell，可动轴只有两根离散槽 + 两根 ④ 装饰数。不硬凑
组合空间（质量红线：不反推上游变体数量）。report-only，不设 gate。

seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`
依次抽 body_form、hatch_module、shield_module、palette，再抽 porthole_count / rcs_count
与连续 scale。seed 0 pinned 到 origin 母本组合（bell_body + hinged_hatch + fixed_shield,
2 portholes / 4 RCS, shenzhou_bronze）作为 documented regression anchor（sparse override，
其余 seed 全 procedural）。random sweep `0-15`（fast）→ `0-35`（final）→ corner。

Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察；真实上界 18 结构 tuple（见上），
低于 300 的原因为结构词汇收敛，已记录。report-only。

Controlled local parameterization：`capsule_scale`（均匀 radius+height+mount z）、`radius_scale`
（body proportion）、`hatch_open`/`plug_travel`/`nose_open`/`shield_drop`（conditional joint
行程）。全部在 `resolve_config` clamp / 解析；不破坏 captured-pivot 接口、hinge 原点、multiplicity。
连续尺寸契约：先采 independent（capsule_scale/radius_scale）→ conditional 按 hatch/shield module
解析各关节行程上界。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 body->hatch->shield，加权 choice；multiplicity 各自加权 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | plug_hatch->无 hinge posts；docking_hatch->强制 nose_cover 第二关节；fixed_shield->无独立 part/joint；body×hatch×shield 正交自由组合 | 无 floating / collision / 轴错误 / max-N / bulky / 可选子件失败 |
| controlled local variation | 6 个 clamp 连续 scale | 比例变化不破坏接口/clearance/support/joint 原点/类别身份 |
| regression overrides | seed 0 = origin 母本（documented anchor）；无其它 | 仅母本 canonical 预览 |
| random sweep | seeds 0-15 fast, 0-35 final, + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 3 | yes | yes | bell / conical / sphere |
| crew_hatch | 3 | yes | yes | hinged / plug / docking |
| heat_shield | 2 | yes | no | fused / separable（样本池仅两种 shield 骨架，已说明理由） |

## Validator

- `slot_choices_for_seed` returns implemented module names (+ porthole_count/rcs_count axes)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 = documented母本 override only)
- compatibility resolution in `resolve_config`: plug->no hinge posts; docking->nose_cover; fixed->no shield part; conditional joint uppers gated by module
- controlled local scales clamped; cannot break captured-pivot interfaces, hinge origin honesty, or multiplicity
- captured hinge-barrel / plug-collar / flush-shield overlaps are element-scoped `allow_overlap` (not broad part-level)
- key joints have expected type/axis/range: crew hatch REVOLUTE(Y) or PRISMATIC(Z); nose_cover REVOLUTE(Y); shield PRISMATIC(-Z)
- copied `porthole_*` / `rcs_port_*` follow naming + conformal placement policy
- `run_astronomy_return_capsule_tests` calls `fail_if_parts_overlap_in_sampled_poses` + >=1 targeted `ctx.pose` per mechanism

## Reject cases

- Crew hatch opened pose collides with the body wall at the hinge upper -> clamp `hatch_open`, keep the hinge on the collar EDGE so the lid swings clear of the tapering body.
- Plug hatch travel too short to clear the collar bore, or `plug_seal_collar` never leaves the bore -> keep `plug_travel` >= 0.15·cs; declare the closed-pose bore overlap element-scoped only.
- docking `nose_cover` opened pose clips the open crew hatch -> the two hinges are on opposite (-X / +X) collar edges and open away from each other; do not widen both past the source uppers.
- Body form swap leaves portholes / RCS / streaks floating off the new wall (constant-radius decoration on cone/sphere) -> place every decoration at `_body_radius(z)` derived from the realized form (Rule 4).
- separable `shield` drops but re-enters the body envelope, or floats at q=0 -> flush-seat at q=0 (element-scoped `bell_body`/`heat_shield` overlap), drop strictly along -Z.
- Downgrading the `bell_body` / `heat_shield` / `lid_shell` `LatheGeometry` revolves to crude Box/Cylinder placeholders (Rule 3 violation).
- Emitting a non-moving decoration (docking ring, hinge posts, scorch streak) as a FIXED-joint part instead of a capsule visual (Rule 1 violation).

## 与相邻类别的边界

- 不该混入：**Astronomy / Space shuttle**（有翼滑翔再入器，非钝头轴对称 capsule）。
- 不该混入：**Astronomy / Rocket engine**（喷管 + 推力室推进组件，非载人再入体）。
- 不该混入：**Astronomy / Antenna dish / Pressurised module door**（地面/舱段结构，无 heat shield + hatch 身份特征）。
- 不该混入：一个纯静态的钟形壳（无任何 hatch / shield 活动关节 -> 至少一根真实非-FIXED 关节必存）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | heat_shield slot 仅 2 candidate（fused / separable），因确认池 9 样本中 shield 只有这两种骨架；已按 AUTHORING §B「样本池不足降到 2 并说明理由」处理，非 re-skin。其余 slot 均 >=3。 |

## 模板实现备注（可选）

- `capsule_scale` 均匀缩放（radius+height+mount z 同乘），single-sourced in `ResolvedConfig`（Contract 3c），hatch/shield/nose 挂点全部从中派生，body 形态 + proportion 正交。
- captured hinge barrel / plug collar / flush shield -> 原始 joint（no MatingContract, grandfathered）+ element-scoped `allow_overlap`，与全部 5 星源一致（Rule 2 例外）。
- `_body_radius(z)` per-form 共形 helper 单点定义（Contract 3c/3e）：bell 分段线性、conical 线性、sphere `_sphere_r(z)`；portholes/RCS/streaks/collar seat 全部读它。
- crew_hatch / heat_shield 走 parallel-children：capsule root 声明 downstream；两 slot 只声明 downstream（re-export capsule）-> 无自动 chain joint，各模块发原始 joint 到 capsule（同 Tipping_Barrow 惯用）。hatch 模块把自身 capsule-side 硬件（hinge posts / docking ring）作为 capsule visual 追加（同 caster mount 追加 frame visual）。
- 所有 N 个 portholes/RCS 复用同一 `Cylinder` 尺寸；body/shield/lid/collar 共享 <=48 seg lathe —— 保编译预算。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | bell_body + hinged_hatch + fixed_shield | `rec_a-...328c39d9` (origin 母本) | L47-L339 | capsule part tree, bell lathe, fused shield, hinged REVOLUTE hatch, portholes/RCS/streaks/collar, 全部 test 语义 |
| S2 | A ③ | conical_frustum | `rec_return_capsule_var_conical_command_module` | L78-L96 | 直锥台 body lathe + 共形装饰锚 |
| S3 | A ③ | spherical_ball | `rec_return_capsule_var_spherical_descent` | L51-L75, L107-L192 | 球形 descent ball `_sphere_r(z)` lathe + 共形舷窗/RCS/streak |
| S4 | B ② | plug_hatch | `rec_return_capsule_var_plug_hatch` | L170-L245 | PRISMATIC plug hatch + `plug_seal_collar` + bore 坐封 |
| S5 | B ① | docking_hatch | `rec_return_capsule_var_docking_nose` | L184-L353 | 前向 docking ring + 第二动件 nose_cover REVOLUTE + overlap 声明 |
| S6 | C ① | separable_shield | `rec_return_capsule_var_separable_shield` | L160-L177, L247-L258 | 分离式 shield PRISMATIC drop-away + flush-seat overlap |
| S7 | A mult | porthole_count=4 | `rec_return_capsule_var_portholes_four` | L129-L131 | porthole ④ multiplicity 上界 |
| S8 | A mult | rcs_count=8 | `rec_return_capsule_var_rcs_ports_eight` | L39 | RCS ④ multiplicity |
| S9 | A mult | rcs_count=12 | `rec_return_capsule_var_rcs_ports_twelve` | L39 | RCS ④ multiplicity 上界 |
