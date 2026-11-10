# Modular Spec — trekking_pole_collapsible

## 元信息
| 项 | 值 |
|---|---|
| slug | `trekking_pole_collapsible` |
| template path | `agent/templates/trekking_pole_collapsible.py` |
| test path (optional) | `tests/agent/test_trekking_pole_collapsible_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (linear collapse chain + per-mechanism section multiplicity N) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13 |
| read_count | 13 |
| read_scope | all 5-star samples in this 小类 (2 origin anchors + 11 forked/probe variants) |
| source_index_policy | only adopted module sources are indexed below |

Read in full: origin A (`306eae8f…`, single folding Z-fold pole, cork handle + palm hook + carabiner + basket + carbide/rubber tip), origin B (`da9d6d60…`, pair of telescoping flick-lock poles). Forks: `var_twist_lock` (CONTINUOUS twist collars, blue anodized), `var_pure_fold_tentpole` (4-segment all-fold + shock-cord proxy), `var_foam_grip` (single EVA foam grip + accent band), `var_t_handle` (perpendicular T crossbar cane grip), `var_snow_basket` (large torus + 8 loop spokes), `var_rubber_foot_tip` (angled rubber walking-foot), `var_n2/n4_telescope` + `var_n4/n5_fold` (multiplicity loops), `var_probe_twist_n4` (twist × N=4 compat probe).

Key structural facts: origins fuse grip + tip + basket as **visuals on the upper / terminal shaft part** (Rule 1); the only real parts are the collapse sections plus the lock actuators. Telescoping = nested coaxial tubes, one **PRISMATIC** per stage (axis −Z), each stage carrying a flick lever (**REVOLUTE**) or twist collar (**CONTINUOUS**). Folding = serial **REVOLUTE** Z-fold chain with alternating axis sign; deploy 0→π straightens.

## 核心身份

A hand-held **collapsible trekking / hiking pole**: a top grip (with wrist strap), a segmented shaft that packs down via a real collapse mechanism (telescoping nested sections OR folding Z-fold sections), a ground tip, and a removable basket. Single-pole canonical form (pole-count kit multiplicity is record_only, excluded per source map). Must keep: grip at top, ≥1 non-fixed collapse joint (prismatic telescope or revolute fold), ground tip, basket. Not: tent pole (no grip/tip/basket), ski pole, walking cane/crutch (no collapse), monopod/tripod, avalanche probe, fishing rod.

## 槽位 + 候选模块表

Grip and tip/basket are ③ Primary-Form-Family axes realized as **visual families on the root / terminal collapse part** (no separate part — they do not articulate, Rule 1); they are still registered in `slot_choices`. The collapse mechanism is the ② axis and owns all moving parts; N is its multiplicity.

### Slot A：grip_style （③ 主体形态家族，root part visuals）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| cork_ergonomic | origin_anchor | origin A + B | A L29-40 (`_ergonomic_handle_mesh`) / B L60-72 (`_make_cork_handle_mesh`) + foam sub-grip B L75-95 | Volumetric Envelope Form | eligible | LatheGeometry flared cork grip + ribbed foam sub-grip + top cap + palm-hook/strap visuals |
| eva_foam | forked_anchor | `var_foam_grip` | L60-74 (`_make_eva_grip_mesh`) + L120-129 | Volumetric Envelope Form | eligible | single long near-cylindrical EVA lathe grip w/ top swell + choke + accent band; no separate sub-grip |
| t_crossbar | forked_anchor | `var_t_handle` | L29-40 (`_t_grip_crossbar_mesh`) + L332-349 | Macro Surface Construction | eligible | perpendicular horizontal T crossbar (lathe) on a neck collar — cane-style read; no top cap |

### Slot B：collapse_mechanism （② 关节/机构，owns moving parts + N multiplicity）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| telescope_flick | origin_anchor | origin B | L205-337 (`_add_mid_stage`/`_add_lower_stage`/loop) | eligible | N−1 nested tubes, one **PRISMATIC** (−Z) per stage + one **REVOLUTE** flick lever per stage; N∈{2,3,4} |
| telescope_twist | forked_anchor | `var_twist_lock` | L81-96, L245-307 | eligible | same PRISMATIC nesting, flick levers replaced by **CONTINUOUS** twist-collar parts (axis +Z); N∈{2,3,4} |
| fold_z | origin_anchor | origin A / `var_pure_fold_tentpole` | A L478-504 / pure L556-583 | eligible | serial **REVOLUTE** Z-fold chain, alternating axis sign, mimic-coupled deploy 0→π; hinge hardware visuals; N∈{3,4,5} |

### Slot C：tip_basket_style （③ 主体形态家族，terminal part visuals）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| carbide_trekking | origin_anchor | origin A + B | B L220-237 (`_add_lower_stage`) + A L226-255 (`_add_basket`, 6 spokes) | Volumetric Envelope Form | eligible | ferrule + carbide cone spike + small torus basket + radial rib spokes |
| snow_basket | forked_anchor | `var_snow_basket` | L110-119, L236-278 | Planar Boundary Form | eligible | large-diameter torus outer ring + hub ring + 8 loop-emitted radial box spokes (wider projected boundary) |
| rubber_foot | forked_anchor | `var_rubber_foot_tip` | L43-56 (`_walking_foot_mesh`) + L449-465 | Volumetric Envelope Form | eligible | angled rubber walking-foot (paw) lathe over ferrule replacing the carbide spike + trekking basket |

Every candidate is a real structural / form-prototype distinction (mechanism topology, lathe母线, or projected basket boundary), not a re-skin. Each slot has 3 candidates (≥3). No single-candidate slot.

## 槽位图（slot graph）

pattern: mixed — grip visuals fuse onto the collapse ROOT part; tip/basket visuals fuse onto the collapse TERMINAL part; the collapse mechanism owns the moving chain.

```
grip_style(visuals) ─fused→ [collapse ROOT part]
   [collapse ROOT] ──PRISMATIC(−Z) OR REVOLUTE(±Y)──> stage/segment_1 ──…──> terminal_stage
   terminal_stage ←fused─ tip_basket_style(visuals)
```

- 顺序 / parent: the collapse mechanism defines the spine. Root = top section (carries grip). Each subsequent section is a child of the previous.
- 跨 slot 连接:
  - grip → root: **fused visuals** (no joint; grip does not move, Rule 1).
  - collapse internal chain: telescoping = **PRISMATIC** axis (0,0,−1) at the parent clamp mouth; nested coaxial by decreasing tube radius; each stage also gets a lock actuator child (REVOLUTE flick lever on the parent, or CONTINUOUS twist collar). Folding = **REVOLUTE** axis (0,±1,0) alternating, origin on the hinge bushing hardware, mimic-coupled via `coupled_chain`.
  - terminal → tip/basket: **fused visuals** on the terminal collapse part (no joint).
- 互斥 / 派生: N range is **conditional** on collapse_mechanism (telescope 2–4, fold 3–5). Lock actuators exist only for telescope_flick (revolute) / telescope_twist (continuous); fold_z has no separate lock part (hinge hardware = visuals).

## 每槽位 Module Emits / Interfaces

### Slot B / telescope_flick (or telescope_twist)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `grip_section` (root, holds grip visuals), `stage_1..stage_{N-1}` (last holds tip visuals), plus per stage `lever_{i}` (flick) or `collar_{i}` (twist) | B L275-337 |
| internal joints | `sec{k}_to_sec{k+1}` PRISMATIC axis (0,0,−1) ×(N−1); `clamp_hinge_{i}` REVOLUTE axis (1,0,0) or `twist_{i}` CONTINUOUS axis (0,0,1) | B L296-337 / twist L280-307 |
| upstream interface | grip visuals fused onto `grip_section`; part is root (grounded) | B L141-202 |
| downstream interface | tip/basket visuals fused onto `stage_{N-1}` (ferrule mouth at bottom) | B L220-237 |

### Slot B / fold_z
| emits | 描述 | 来源 |
|---|---|---|
| parts | `grip_section` (root), `segment_1..segment_{N-1}` (last holds tip) | A L276-470 / pure L279-546 |
| internal joints | `fold_{k}` REVOLUTE axis (0,±1,0) alternating, mimic-coupled (driver = fold_1) | A L478-495 / pure L556-583 |
| interfaces | grip → root visuals; tip/basket → terminal segment visuals; hinge bushings at each fold origin | A L165-223 (`_add_fold_hinge_hardware`) |

活动件 = collapse sections + flick lever / twist collar (real articulation). 不动件 (grip, tip, basket, ferrules, bands, straps, hinge hardware) = parent visuals.

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| grip_style | enum | cork_ergonomic / eva_foam / t_crossbar | cork_ergonomic | choice | procedural sampler | Slot A |
| collapse_mechanism | enum | telescope_flick / telescope_twist / fold_z | telescope_flick | choice | procedural sampler | Slot B |
| section_count N | int | telescope 2–4 / fold 3–5 | 3 | conditional | range depends on collapse_mechanism | Slot B / §8 |
| tip_basket_style | enum | carbide_trekking / snow_basket / rubber_foot | carbide_trekking | choice | procedural sampler | Slot C |
| palette_style | enum | graphite_cork / carbon_white / blue_anodized / eva_orange / red_snow | graphite_cork | choice | procedural sampler | §6轴⑥ |
| deployed_length_scale | float | [0.88, 1.15] | 1.0 | independent | uniform then clamp; scales section tube lengths | ⑤ B L207-223 |
| shaft_radius_scale | float | [0.90, 1.12] | 1.0 | independent | scales base tube radius r0 | ⑤ B L156-181 |
| section_travel | float | derived | — | equation | `= min(0.75·nest_len, tube_len − retain)`; per-stage prismatic upper bound so inner tube stays retained | inequality below |
| (—) | constraint | — | — | inequality | telescope: `travel_k ≤ nest_overlap_k − retain_min(0.05)` so each stage stays inserted at full extension; else shrink travel | B L488-506 retention checks |
| (—) | constraint | — | — | inequality | telescope: `r_{k+1} ≤ r_k − wall(0.0018)` monotone decreasing so tubes nest coaxially | B tube radii |
| fold_open | float | derived | π | conditional | fold deploy driver upper = π, clamped by `coupled_chain` clearance solver | A L485 |

连续尺寸采样契约: 采 independent (`deployed_length_scale`,`shaft_radius_scale`) → 派生 per-stage tube lengths/radii/travel (equation) → project travel by retention inequality → resolve N-range by mechanism (conditional). 全部在 `resolve_config` 内求解。

## 7.5 编译预算 / compile budget
Per-seed budget **≤ 18s** (typical modular tube/lathe/torus category,库内参考 5–20s). Primitives: Cylinder tubes/collars/ferrules, LatheGeometry grips (segments ≤48), ConeGeometry tip (32), TorusGeometry basket (tubular ≤64). N同构 stages reuse ONE shared stage-build helper; snow-basket spokes ≤8 boxes. No booleans. Sweep hang-guard `--compile-timeout 120` (~3×). 超预算先降 lathe/torus 段数再迭代。

## Multiplicity / Copy Logic

**Axis 1 — section_count N (per collapse_mechanism, conditional range):**
- `count_param`: number of shaft sections (incl. root). Joints = N−1.
- `N_range`: telescope **[2,4]**; fold **[3,5]** (product domain per source map §Multiplicity; test 偏小).
- sampling domain (weights, small-N high freq): telescope N∈{2,3,4} weights (0.30,0.45,0.25); fold N∈{3,4,5} weights (0.45,0.35,0.20).
- copied object: a shaft-section part = tube + (telescope: receiving sleeve + clamp collar + band + lock actuator part) / (fold: hinge-bridge + ferrule + hinge hardware visuals).
- naming: `stage_{i}` / `segment_{i}`; joints `sec{k}_to_sec{k+1}` / `fold_{k}`; actuators `lever_{i}` / `collar_{i}`.
- placement rule: telescope = linear coaxial nested chain, decreasing radius, PRISMATIC −Z, built at collapsed pose (q=0 nested). fold = alternating Z-fold chain, REVOLUTE ±Y, built at folded bundle pose (q=0), deploy→π.
- joint policy: exactly one collapse joint added/removed per N step; keep lock actuator per telescope stage.
- source/gating: telescope N from origin B + `var_n2/n4_telescope`; fold N from origin A + `var_n4/n5_fold`.

**Axis 2 — basket spoke count (secondary, record_only):** trekking = 6 ribs (origin A), snow = 8 loop spokes (`var_snow_basket`). Encoded inside tip_basket_style module, NOT a separate `slot_choices` axis.

Pole-count (1 vs 2) is **excluded** (kit packaging multiplicity per source map); single pole only.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 有 | 两大 part-joint 拓扑: 嵌套 telescoping 链 (PRISMATIC 串) vs 串行 Z-fold 链 (REVOLUTE 串); N 改变链长。source-backed: origin A/B + forks |
| └ multiplicity | 同构件 ×N | 有 | 见 §8: telescope N[2,4] / fold N[3,5], 加权小N偏多 |
| ② 关节类型 | 换 type/轴 | 有 | PRISMATIC(−Z telescope) / REVOLUTE(±Y fold, +X flick lever) / CONTINUOUS(+Z twist collar); 每种都在 sweep 出现。source-backed: origin B / origin A / `var_twist_lock` |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | grip 家族 {cork Volumetric / eva Volumetric / t-crossbar Macro-Surface} + tip/basket 家族 {carbide+trekking Volumetric / snow Planar-Boundary / rubber-foot Volumetric}; 均 source-backed，登记进 `slot_choices` |
| ④ 表面装饰 | 叠加表面细节 | 有(record_only/world) | carbon-look label strip (`pole_carbon_label` B L160-166)、black decorative bands、strap tag/webbing、accent band (eva); host-conformal: 贴附在宿主 tube 逐-z 半径面（band 半径 = tube_r(z)+ε），随 ③/⑤ 共形。派生顺序 ③→⑤→④ |
| ⑤ 尺寸/行程 | 只改尺寸/行程 | 有 | deployed_length_scale[0.88,1.15], shaft_radius_scale[0.90,1.12]; **每关节运动包络**: PRISMATIC telescope 轴(0,0,−1) 开启=向下伸出 [0, travel_k]（retention 保留 inserted）; REVOLUTE fold 轴(0,±1,0) 开启=展直 [0, π] mimic-coupled; REVOLUTE flick lever 轴(1,0,0) [0,1.25]; CONTINUOUS twist 整圈。`motion_test_plan`: 跑 `fail_if_parts_overlap_in_sampled_poses`(max_pose_samples=48; fold 用 coupled 后独立采样面缩小) + targeted `ctx.pose` 每机构一条 (telescope 伸出下移 / lever 外翻 / fold 展直成轴). 见下方 exemption 说明 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal/plastic(cork,foam,rubber)/anodized-metal; 配色 5 档: graphite_cork, carbon_white, blue_anodized, eva_orange, red_snow (source: origin A/B, twist_lock 蓝, foam_grip 橙, snow_basket 红). 材质大类覆盖 ≥ ceil(0.5×5)=3 ✓ |

**motion sampled-pose 说明:** telescope + flick/twist 用 `fail_if_parts_overlap_in_sampled_poses` 全采样 + element-scoped `allow_overlap`（nested tube ↔ sleeve/collar/band，captured pin ↔ knuckle）。fold_z 的相邻段在展开中途会互相扫掠（真实 Z-fold 由 shock-cord 顺序展开，离散独立采样会误报）——因此 fold_z **用 `coupled_chain` 把所有 fold 关节 mimic 到单一 driver**，只在耦合轨迹上被 clearance solver 采样/夹紧；相邻折段声明 element-scoped `allow_overlap`（Z-fold bundle 语义，源记录同款）。此为 Rule 5 的机构级处理，非放宽 range。

## 采样与覆盖审计

总组合数：grip(3) × mechanism(3) × tip_basket(3) × N(telescope 3 + fold 3 = 6, 但 N 与 mechanism 耦合) × palette(5)
= 3 grip × [ (telescope_flick+telescope_twist: 2 mech × 3 N) + (fold_z: 1 mech × 3 N) ] × 3 tip × 5 palette
= 3 × 9 × 3 × 5 = **405** discrete topology-bearing combos (>300 富类别门槛).

理由: 主多样性来自离散 slot（grip 形态 / 机构拓扑 / N / tip 形态 / 涂装），连续 scale 仅微调比例。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` = `random.Random(seed)`; 依次 sample grip_style, collapse_mechanism, 然后按 mechanism 取 conditional N (加权), tip_basket_style, palette_style, 再采连续 scale。compatibility gating 在 `resolve_config`: N clamp 到 mechanism 的合法域; travel 按 retention inequality 回缩; tube radii 单调递减。无 curated/modulo 主表。seed=0 不特殊。
Topology target：1000-seed slot-choice tuple 覆盖用于成熟度观察 (report-only)。
Controlled local parameterization：`deployed_length_scale`,`shaft_radius_scale` (独立采样后 clamp); `section_travel` (equation 派生 + retention inequality 回缩); 均不破坏 nesting/retention/joint origin/identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | grip→mech→N(conditional weighted)→tip→palette→scales | slot_choices_for_seed matches build choices |
| compatibility matrix | N∈mechanism-legal-range; travel≤retention; radii monotone; t_crossbar/eva/snow/foot 与任意机构兼容 | no floating, no closed-pose collision, retention holds, coupled fold deploys |
| controlled local variation | length/radius scale clamp; travel derived+projected | proportions vary; interfaces/clearance/identity intact |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial (corner appended), 0-999 maturity | axis_realization shows all mech/grip/tip/N |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| grip_style | 3 | yes | yes | |
| collapse_mechanism | 3 | yes | yes | ② core |
| tip_basket_style | 3 | yes | yes | |
| section_count N | 3/mech | yes | yes | multiplicity, conditional |

## Validator

- slot_choices_for_seed returns implemented module names (grip_style, collapse_mechanism, section_count `nN`, tip_basket_style)
- config_from_seed uses deterministic procedural sampling for all seeds incl. seed 0
- N clamped to the mechanism's legal range (telescope 2–4 / fold 3–5) in resolve_config
- telescope tube radii strictly decreasing; per-stage travel ≤ retention overlap (solved in resolve_config)
- fold joints mimic-coupled via `coupled_chain` (no independent fold combos)
- each collapse joint has expected type/axis; flick lever REVOLUTE +X / twist collar CONTINUOUS +Z / fold REVOLUTE ±Y / telescope PRISMATIC −Z
- grip & tip/basket are visuals on collapse parts (no FIXED decorative part)
- controlled scale params clamped; cross-part travel/radius dependencies resolved in resolve_config
- `fail_if_parts_overlap_in_sampled_poses` + ≥1 targeted `ctx.pose` per mechanism present

## Reject cases

- 把 grip 或 basket 做成 FIXED-joint 独立 part（违反 Rule 1）。
- telescope 内管在全行程伸出后脱离 sleeve（无 retention）→ 漂浮/断链。
- telescope tube 半径非单调 → 无法同轴嵌套 / 闭合 pose 穿模。
- fold 关节各自独立（非 coupled）→ 中途扫掠穿模。
- fold hinge REVOLUTE origin 落在空中（不在 hinge bushing 硬件上）→ origin-far fail。
- N 超出 mechanism 合法域（telescope 5 / fold 2）。
- 降级 Lathe/Cone/Torus 到 Box/Cylinder 占位（违反 Rule 3）。
- 单色所有 seed（palette_style 未驱动 materials）。

## 与相邻类别的边界

- 不该混入：tent pole（无 grip/tip/basket，纯 shock-cord 杆）。
- 不该混入：ski pole / avalanche probe（无 telescoping 折叠收纳 / 无 trekking 握把 basket 组合的可收纳性）。
- 不该混入：walking cane / crutch（不可收纳、无 basket、grip 形态不同）。
- 不该混入：monopod / tripod（相机螺纹头、多腿）、fishing rod（导环 + 卷线器）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | authored from 13 5-star sources; single-pole canonical; telescope(prismatic)+fold(revolute) core ② axis, grip/tip ③ families, N multiplicity conditional on mechanism |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | B | telescope_flick | origin B `da9d6d60…` | L205-337 | prismatic nesting + flick lever topology |
| S2 | B | telescope_twist | `var_twist_lock` | L81-96,L245-307 | continuous twist collar |
| S3 | B | fold_z | origin A `306eae8f…` / `var_pure_fold_tentpole` | A L478-504 / pure L556-583 | revolute Z-fold chain + hinge hardware |
| S4 | A | grip cork | origin A/B | A L29-40 / B L60-95 | cork+foam grip lathe |
| S5 | A | grip eva | `var_foam_grip` | L60-74 | EVA foam grip lathe |
| S6 | A | grip t_crossbar | `var_t_handle` | L29-40,L332-349 | T crossbar cane grip |
| S7 | C | carbide_trekking | origin B + A | B L220-237 / A L226-255 | ferrule+carbide+trekking basket |
| S8 | C | snow_basket | `var_snow_basket` | L110-119,L236-278 | large torus + loop spokes |
| S9 | C | rubber_foot | `var_rubber_foot_tip` | L43-56,L449-465 | rubber walking-foot lathe |
</content>
</invoke>
