# Modular Spec — fire_escape_ladder

## 元信息
| 项 | 值 |
|---|---|
| slug | `fire_escape_ladder` |
| template path | `agent/templates/fire_escape_ladder.py` |
| test path (optional) | `tests/agent/test_fire_escape_ladder_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (③ form-family dispatch + multiplicity of rungs + linear/parallel deploy children) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 14 |
| read_count | 14 |
| read_scope | all 5-star samples in this subcategory (2 origins + 12 forks) |
| source_index_policy | only adopted module sources are indexed below |

Read all 14 `model.py`:
- **origin B** `rec_...e6a5530c` — `exterior_fire_escape_ladder_with_cage`: rigid `fixed_ladder` (2 round rails, `fixed_rung_{i}` range(14)), semi-elliptical cage hoops (`tube_from_spline_points` mesh) + side struts + vertical ribs, wall standoff+anchor-plate array, forward slide-guide rails, **PRISMATIC** `lower_ladder` drop section (release sleeve, rubber feet) + **REVOLUTE** `safety_gate` (pin-in-sleeve).
- **origin A** `rec_...20b875b6` — `wall_fire_escape_ladder_cage`: `upper_ladder` (rail_0/1, `rung_{i}` while-loop, `cage_hoop_{i}` arc mesh + `cage_arm`/`cage_bar`, `wall_plate`/`standoff` array, `lower_slide_collar`), **PRISMATIC** `lower_ladder` captured in collars.
- **rungs_n4 / n8 / n12** — origin-B body with `fixed_rung_{i}` = range(4/8/12); n4 uses `SAFETY_ORANGE` rails (palette). Prove the N-rung multiplicity via for-loop, everything else invariant.
- **no_cage_grabrail** — origin-B body, cage removed, extended rails + curved `grab_rail_{s}` (`tube_from_spline_points`) handholds; keeps PRISMATIC drop + REVOLUTE gate.
- **fall_arrest_rail** — origin-A body, cage replaced by central vertical `arrest_rail` + `arrest_bracket_{i}` + separate `arrest_shuttle` on a **PRISMATIC** `shuttle_to_rail` joint (captured clamp), PRISMATIC drop preserved.
- **hinged_drop_section** — origin-A body, hinge ears/cross-brace, `lower_ladder` with `swing_sleeve`/`swing_pin`/`counterweight_arm` on a **REVOLUTE** swing hinge.
- **chain_rollup** — `upper_ladder` with flexible `chain_link_{s}_{i}` box side-members (alternating flat/edge), rungs + standoff stubs + head/foot bars + pivot boss, child `sill_hook` (sill plate/lip/flange/ears/pin) on **REVOLUTE** `sill_hook_pivot`.
- **strap_webbing** — `upper_ladder` with flat `side_strap_{s}` webbing boxes + tubular rungs + spacers + top/bottom plates + pivot brackets, child `hook` on **REVOLUTE** `hook_pivot`.
- **windowsill_hook / parapet_roof_hook** — origin bodies with hook heads on REVOLUTE pivots (informs the portable hook geometry; anchor variation).
- **folding_articulated** — 3 rigid segments `ladder_seg_{0,1,2}` each with `seg{n}_rung_{i}` range(N), joined by 2 **REVOLUTE** `fold_hinge_{n}` (pin+sleeve captured).
- **telescoping_multistage** — 3 nested stages (`upper_ladder`/`stage_1`/`stage_2`) decreasing rail radius, `stageN_rung_{i}` loops, chained by 2 **PRISMATIC** joints with retained guide collars.

## 核心身份

A deployable/climbable ladder for emergency egress from a building: **two parallel side members with regularly spaced horizontal rungs**, a **building anchor/mount interface**, and **at least one real deploy joint** (slide / fold / swing / hook pivot). Mature domain covers the rigid wall-mounted caged steel ladder (origins) and the portable/articulated escape ladders (chain roll-up, webbing, folding, telescoping). Must NOT drift to: step-stool / A-frame stepladder, scaffold/work-tower, balcony guardrail/handrail, rope-only or cargo-net descent device, fire-truck aerial ladder (see §11).

## 槽位 + 候选模块表

### Slot A：`ladder_family`（③ 主体形态家族 / Primary Form Family — 主导槽，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `fixed_cage` | origin_anchor | rec_...e6a5530c / rec_...20b875b6 | e6a5 L62-243 / 20b8 L53-193 | Volumetric Envelope Form (rigid caged column) | eligible | root `fixed_ladder`: 2 round steel rails + N `fixed_rung_{i}` loop + wall-standoff array + slide guides; carries `guard_system` + a `deploy` drop child |
| `portable_hook` | forked_anchor | rec_...chain_rollup / rec_...strap_webbing | chain L84-239 / strap L44-190 | Macro Surface Construction (flexible side-member run) | eligible | root `ladder_body`: flexible side members (`side_member` axis) + N rungs + standoff stubs + head/foot bars; child `sill_hook` REVOLUTE |
| `folding` | forked_anchor | rec_...folding_articulated | L70-198 | Volumetric Envelope Form (articulated segment chain) | eligible | 3 rigid segments `ladder_seg_{0,1,2}`, each 2 rails + N/3 rungs; 2 REVOLUTE `fold_hinge_{n}` (pin/sleeve captured); seg0 wall-anchored |
| `telescoping` | forked_anchor | rec_...telescoping_multistage | L53-262 | Volumetric Envelope Form (nested collapsible stages) | eligible | 3 nested stages decreasing rail radius, `stageN_rung_{i}` loops; 2 PRISMATIC joints with retained collars; stage0 wall-anchored |

≥4 recognizable ③ prototypes registered in `slot_choices`. Form-dominated 小类 satisfied.

### Slot B：`side_member`（① 骨架/拓扑 — gated by family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rigid_rail` | origin_anchor | rec_...e6a5530c | L79-96 | pinned for fixed_cage/folding/telescoping | 2 round steel `Cylinder` rails (the invariant two-member skeleton) |
| `chain_link` | forked_anchor | rec_...chain_rollup | L52-129 | eligible when portable_hook | 2 flexible chain side-members: loop-emitted `chain_link_{s}_{i}` alternating flat/edge boxes touching end-to-end |
| `webbing_strap` | forked_anchor | rec_...strap_webbing | L77-104 | eligible when portable_hook | 2 flat woven `side_strap_{s}` boxes (thin webbing) + rung spacers |

### Slot C：`guard_system`（② guard 拓扑 — gated: 仅 fixed_cage 变，其余 `open`）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `full_cage` | origin_anchor | rec_...20b875b6 / rec_...e6a5530c | 20b8 L104-137 / e6a5 L124-174 | eligible when fixed_cage | semi-elliptical `cage_hoop_{i}` (`tube_from_spline_points` mesh) + `cage_arm`/`cage_bar` following the envelope |
| `grab_rail` | forked_anchor | rec_...no_cage_grabrail | L118-154 | eligible when fixed_cage | cage removed; extended rails + curved `grab_rail_{s}` handhold tubes (mesh) at the landing |
| `fall_arrest` | forked_anchor | rec_...fall_arrest_rail | L94-131, L200-229 | eligible when fixed_cage | central `arrest_rail` + `arrest_bracket_{i}` + separate `arrest_shuttle` on a PRISMATIC `shuttle_to_rail` joint |
| `open` | forked_anchor | rec_...chain_rollup (cageless) | L291-298 | pinned for portable_hook/folding/telescoping | no guard geometry (physically incoherent to cage flexible/folding/telescoping bodies — see §Blocked) |

### Slot D：`deploy`（② 关节/机构 — 决定强制的非-FIXED 关节；conditional on family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `prismatic_drop` | origin_anchor | rec_...20b875b6 / rec_...e6a5530c | 20b8 L175-201 / e6a5 L244-337 | eligible when fixed_cage | child `lower_ladder` (rails+rungs+release sleeve+feet) captured in slide collars; **PRISMATIC** `ladder_to_lower` axis −z |
| `revolute_swing` | forked_anchor | rec_...hinged_drop_section | L139-218 | eligible when fixed_cage | child `lower_ladder` with `swing_sleeve`/`swing_pin`/`counterweight_arm`; **REVOLUTE** hinge about +x |
| `sill_hook` | forked_anchor | rec_...chain_rollup / rec_...strap_webbing | chain L171-237 / strap L134-188 | pinned for portable_hook | child `sill_hook` (arm/lip/ears/pin) on **REVOLUTE** `sill_hook_pivot` about +x |
| `fold_hinges` | forked_anchor | rec_...folding_articulated | L173-196 | pinned for folding | 2 **REVOLUTE** `fold_hinge_{n}` chaining the 3 segments |
| `telescope` | forked_anchor | rec_...telescoping_multistage | L236-260 | pinned for telescoping | 2 **PRISMATIC** stage joints along −z with retained collars |

### Slot E：`rung_count`（N multiplicity — 强轴，登记进 slot_choices）
见 §8. N ∈ [4,16], 权重偏小 N；`f"n{N}"`。

硬约束满足：每个 slot ≥2 candidate（gated 时至少 2 个值在 sweep 中实现——family=4, side_member=3, guard=4, deploy=5）。每个非-③ candidate 有 `forked_anchor` + `model.py:Lx-Ly`。③ 家族 candidate 标 `form_subtype`。无单-candidate slot。

## 槽位图（slot graph）

pattern: `mixed`

```
[ladder_family] (root body, ③)
   ├─ fixed_cage:   root fixed_ladder --[emits guard_system as parent.visual / fall_arrest shuttle child]
   │                 fixed_ladder --[deploy: PRISMATIC −z in slide-collar | REVOLUTE +x hinge]--> lower_ladder
   │                 (fall_arrest) fixed_ladder --[PRISMATIC +z on arrest_rail]--> arrest_shuttle
   ├─ portable_hook: root ladder_body (side_member ①) --[REVOLUTE +x at head]--> sill_hook
   ├─ folding:      ladder_seg_0 --[REVOLUTE +x pin]--> ladder_seg_1 --[REVOLUTE +x pin]--> ladder_seg_2
   └─ telescoping:  stage_0 --[PRISMATIC −z collar]--> stage_1 --[PRISMATIC −z collar]--> stage_2
```

接口点位 / joint policy:
- **prismatic_drop**: child `lower_ladder` local origin = slide axis; parent slide-guide `lower_slide_collar_{i}` captures the child rail (element-scoped `allow_overlap`); joint origin on parent guide geometry; PRISMATIC exempt from origin-far check. Captured-slide → omit `MatingContract` (grandfathered, Rule 2).
- **revolute_swing / sill_hook / fold_hinges**: pin-through-sleeve/barrel at the child local origin (hinge cylinder at (0,0,0) on the axis) so `fail_if_articulation_origin_far_from_geometry` passes on both sides; captured-pin → omit `MatingContract`, element-scoped `allow_overlap` for pin↔sleeve.
- **telescope**: nested rails captured in collars (allow_overlap), PRISMATIC.
- guard_system geometry (cage hoops/arms/bars, grab rails, arrest rail+brackets) is **non-moving → emitted as `parent.visual` on the root body (Rule 1)**, never a FIXED joint. Only the `arrest_shuttle` is a real PRISMATIC child.

## 每槽位 Module Emits / Interfaces

### Slot A / `fixed_cage`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `fixed_ladder`; child `lower_ladder`; (+`arrest_shuttle` iff fall_arrest) | e6a5 / 20b8 / fall_arrest |
| visuals | `fixed_side_rail_{s}` (Cylinder z), `fixed_rung_{i}` loop (Cylinder x), `wall_standoff_{s}_{lv}`+`wall_anchor_plate_{s}_{lv}` array, `slide_guide_rail_{s}`+`lower_slide_collar_{s}`, guard visuals | e6a5 L79-192 |
| internal joints | `ladder_to_lower` (PRISMATIC −z) or `swing` (REVOLUTE +x); optional `shuttle_to_rail` (PRISMATIC +z) | e6a5 L329-337 / hinged L210 / fall_arrest L216 |

### Slot A / `portable_hook`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `ladder_body`; child `sill_hook` | chain L119-239 |
| visuals | `side_member` (chain_link loop | webbing straps), `rung_{i}` loop, `standoff_{i}_{s}` stubs, `head_bar`/`foot_bar`/`pivot_boss` | chain L126-166 |
| internal joints | `sill_hook_pivot` REVOLUTE +x | chain L224-237 |

### Slot A / `folding`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ladder_seg_0` (root, wall-anchored) + `ladder_seg_1` + `ladder_seg_2` | folding L88-171 |
| visuals | per seg: `seg{n}_rail_{s}`, `seg{n}_rung_{i}` loop, `fold_pin_{n}`/`fold_sleeve_{n}`; seg0 wall anchors; seg2 feet | folding L91-171 |
| internal joints | `fold_hinge_0`, `fold_hinge_1` REVOLUTE +x | folding L177-196 |

### Slot A / `telescoping`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `stage_0` (root, anchored) + `stage_1` + `stage_2`, decreasing rail radius | telescoping L76-234 |
| visuals | `stage{n}_rail_{s}`, `stage{n}_rung_{i}` loop, `stage{n}_slide_collar_{s}`+brackets, stage2 foot bar | telescoping L84-234 |
| internal joints | `stage0_to_stage1`, `stage1_to_stage2` PRISMATIC −z | telescoping L241-260 |

活动件皆有 articulation；guard/hook/standoff/cage 等不动细节全部 `parent.visual`。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `ladder_family` | enum | fixed_cage/portable_hook/folding/telescoping | — | choice | procedural sampler | Slot A |
| `side_member` | enum | rigid_rail/chain_link/webbing_strap | rigid_rail | conditional | =rigid_rail unless portable_hook; then sample {chain_link,webbing_strap} | Slot B |
| `guard_system` | enum | full_cage/grab_rail/fall_arrest/open | full_cage | conditional | sample {cage,grabrail,fall_arrest} iff fixed_cage else `open` | Slot C |
| `deploy` | enum | prismatic_drop/revolute_swing/sill_hook/fold_hinges/telescope | prismatic_drop | conditional | fixed_cage→sample{prismatic,swing}; portable→sill_hook; folding→fold_hinges; telescoping→telescope | Slot D |
| `rung_count` N | int | [4,16] weighted small | 8 | independent | weighted sample; clamp [4,16] | §8 / e6a5 L88 |
| `rail_gap_scale` | float | [0.85,1.15] | 1.0 | independent | half-spacing of side members; clamp | 20b8 L69 |
| `rung_pitch_scale` | float | [0.90,1.12] | 1.0 | independent | rung vertical pitch (base 0.30–0.32) | e6a5 L88 |
| `rail_radius_scale` | float | [0.85,1.20] | 1.0 | independent | rail/rung tube radius | 20b8 L71 |
| `cage_radius_scale` | float | [0.90,1.12] | 1.0 | conditional | only used by full_cage; clamp; cage radius > rail_gap so hoop clears rails | 20b8 L72 |
| `drop_travel_scale` | float | [0.85,1.15] | 1.0 | independent | PRISMATIC drop / telescope stage travel; clamp | e6a5 L336 |
| `standoff_depth_scale` | float | [0.85,1.20] | 1.0 | independent | wall standoff arm depth | e6a5 L184 |
| (—) | constraint | — | — | inequality | `cage_radius ≥ rail_half_gap + 0.12` (hoop must bracket the rails); enforced by deriving cage_radius = max(base·scale, rail_gap+0.12) | 20b8 cage |
| (—) | constraint | — | — | inequality | rung length spans the two members: `rung_len = 2·rail_half_gap + overhang` (derived, not free) | e6a5 L94 |
| `palette_style` | enum | ≥4 colorways (see §8.5 ⑥) | galvanized_steel | choice | `rng.choice(PALETTE_STYLES)` → `mats[...]` dict | multi-source |

连续采样契约：先采 independent scales → 派生 rung_len / cage_radius (equation/inequality) → conditional (side_member/guard/deploy per family, cage_radius only when full_cage) → clamp。全部在 `resolve_config` 内求解。

## 7.5 编译预算 / compile budget（必填）
自报 **≤18s/seed**。依据：主体为 `Cylinder`/`Box` (廉价)；仅 `full_cage`/`grab_rail` 用 `tube_from_spline_points` mesh (中等)。分档 tessellation：cage hoop `radial_segments=14`, `steps≤26`, `samples_per_segment=2`；grab-rail `radial_segments=12`；小特征 ≤16 段。N 个 rung/chain-link 复用同一 helper（同 `Cylinder`/`Box`），不逐个新 mesh。portable chain_link 数上限受 N 与 ladder 高度约束（≤~34 links）。sweep `--compile-timeout 120`（≈3× 预算 watchdog）。

## Multiplicity / Copy Logic

**轴 1 — `rung_count` N（唯一 forked 复制轴）**
- `count_param`: 主爬梯段的 rung 数量（origin B `range(14)`，origin A while-loop）。
- `N_range`: 产品域 3–20；本模板采样 **[4,16]**，测试偏小。
- sampling domain（权重档）：小 N 高频、大 N 稀有 —— weights 近似 `n∈{4,5,6}` 高，`≥13` 稀有。
- copied object: 单根水平 rung `Cylinder`（`_cyl_x`），loop `for i in range(N)`。
- naming: `fixed_rung_{i}` / `rung_{i}`；分段家族 `seg{n}_rung_{i}`、分级 `stage{n}_rung_{i}`。
- placement: 沿 z 等间距 `pitch ≈ 0.30·rung_pitch_scale`；rails/cage/standoff/guides 随 run 高度缩放。
- joint policy: rung 焊死（无 per-rung joint）；multiplicity fork 只改 rung 数，不改 family/joint/anchor。
- source/gating: fixed_cage & portable 用总 N；folding/telescoping 每段 `max(2, round(N/3))`（分段递减），登记的仍是采样 N。

**次级 multiplicity（record_only，不单独 fork）**: cage hoop 数、standoff level 数、chain_link 数——皆 loop 驱动、随 run 高度派生，暴露但不枚举成 variant（避免 padding）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | rigid round rails (origins) vs flexible chain-link vs flexible webbing side members；folding=3 段+2 铰、telescoping=3 级+2 滑、fixed=body+drop child。two-parallel-members+rungs 不变量恒守。source-backed（rigid_rail/chain_link/webbing_strap + family part trees），登记进 `side_member`/`ladder_family` |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：rung N∈[4,16] 权重偏小 |
| ② 关节类型 | 图不变换 type/轴 | 有 | PRISMATIC drop (origins) + PRISMATIC telescope + PRISMATIC fall-arrest shuttle；REVOLUTE swing/sill-hook/fold-hinge。每种类型都在 sweep 出现（fixed_cage 采样 prismatic|swing；folding/telescoping/portable 各自 pinned 但会被采到）。source-backed |
| ③ 主体形态家族 | 图&关节不变换核心形态原型 | 有 | 4 family（fixed_cage/portable_hook/folding/telescoping），各标 form_subtype（Volumetric Envelope ×3 + Macro Surface ×1），登记进 `slot_choices`；source-backed anchors |
| ④ 表面装饰 | 原型不变叠表面细节 | 有 (record_only + world_knowledge) | safety-yellow/red `release_sleeve`/`latch_tab`（origins）、travel-arrow 省略、hazard-stripe on sleeve；host-conformal：sleeve 包在 rail cylinder 上（随 rail_radius 共形），latch tab 贴 rail 面。无专门 variant |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | rung pitch 0.30·[0.90,1.12]；N 4–16；rail_gap [0.85,1.15]；rail_radius [0.85,1.20]；cage_radius [0.90,1.12]；drop/telescope travel [0.85,1.15]。**运动包络**：PRISMATIC drop 轴 −z `[0, travel]`；REVOLUTE swing/sill-hook 轴 +x `[0, upper≈1.4–1.7]` 开向前/下；fold_hinge 轴 +x `[0, ≈1.6]` 前折避免与母段重叠；telescope PRISMATIC −z `[0, stage_travel]`；fall-arrest shuttle PRISMATIC +z `[−h,h]` 前置于 rung 面避让。`motion_test_plan`: 跑 `fail_if_parts_overlap_in_sampled_poses` + 每机构一条 targeted `ctx.pose` 证位移方向/端点 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal + painted（≥ceil(0.5×5)=3 满足：galvanized/zinc/aluminium=metal，safety_orange/painted_red=painted）。配色 ≥5：galvanized_steel / zinc_plated / safety_orange / anodized_aluminium / painted_red_brackets。palette 只改材质不改几何 |

收尾自检：`template batch` 0-9 seed 里 4 个 family 拉得开、metal+painted 都出现、release sleeve/latch 贴面不悬空、每个 deploy 关节全程不穿模。

## 采样与覆盖审计

总组合数（离散拓扑）：
- fixed_cage: guard(3) × deploy(2) = 6
- portable_hook: side_member(2) = 2
- folding: 1 ; telescoping: 1
= **10 discrete topologies × N∈[4,16] (13) = 130 拓扑×N 组合**，再叠 6 连续 scale + 5 palette。report-only topology target 达标（离散域本身 130，加 palette×scale 远超 300）。

理由：families 之间 guard×deploy 组合物理不相容（cage 只存在于 rigid fixed；flexible/folding/telescoping 强制 cageless），故非全正交而是 family-gated——避免非法组合而非 probe。

seed_domain_policy：procedural_first。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 采 family → 按 family gate 采 side_member/guard/deploy → 采 N（加权）→ 采 6 个连续 scale → 采 palette。`resolve_config` 做 gating + clamp + 派生（rung_len、cage_radius 不等式）。无 curated/modulo 主表；无 regression override（首版）。viewer 目检 seeds 0-9（含每 family + fall_arrest + swing + webbing + 大/小 N）。
Topology target：1000-seed slot tuple 覆盖 report-only；离散域 130，兼容约束已说明。
Controlled local parameterization：rail_gap_scale / rung_pitch_scale / rail_radius_scale / cage_radius_scale / drop_travel_scale / standoff_depth_scale，全部 `resolve_config` clamp/派生，不破坏 collar 捕获、hinge 轴、cage 包络、joint range、类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | family→gated sub-axes→N(weighted)→scales→palette | slot_choices_for_seed matches build choices |
| compatibility matrix | cage/grabrail/fall_arrest 仅 fixed_cage；flexible/folding/telescoping 强制 open；side_member 仅 portable 变 | no illegal cage-on-flexible; no floating; sampled collisions clear |
| controlled local variation | 6 clamped scales | proportions vary; interfaces/clearance/joint-origin/identity intact |
| regression overrides | none | — |
| random sweep | 0-35 initial, 0-999 maturity | axis_realization; motion_qc |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| ladder_family | 4 | yes | yes | ③ 主导 |
| side_member | 3 | yes | yes | gated (2 realized in portable) |
| guard_system | 4 | yes | yes | gated (3 realized in fixed_cage + open) |
| deploy | 5 | yes | yes | conditional (2 realized in fixed_cage) |
| rung_count | 13 (N band) | yes | yes | multiplicity |

## Validator

- `slot_choices_for_seed` returns implemented module names (family/side_member/guard/deploy/`n{N}`).
- `config_from_seed` deterministic procedural for all seeds incl. 0.
- gating prevents illegal combos (no cage on flexible/folding/telescoping; side_member only varies in portable).
- no regression overrides.
- controlled scales clamped in `resolve_config`; rung_len & cage_radius derived (equation/inequality) there, not in builder.
- every family has ≥1 non-FIXED joint; captured-pin/slide joints omit MatingContract and are guarded by element-scoped allow_overlap + flat origin baseline.
- key joints have expected type/axis: prismatic drop −z, revolute hinges +x, telescope −z, fall-arrest shuttle +z.
- rungs follow `*_rung_{i}` naming + even-pitch placement.
- `fail_if_parts_overlap_in_sampled_poses` + targeted `ctx.pose` per mechanism.

## Reject cases
- rung count not a for-loop / fixed 2–3 rungs → fails multiplicity identity.
- cage emitted on a chain/webbing/folding/telescoping body → illegal combo.
- deploy joint downgraded to FIXED, or no non-FIXED joint present → violates identity + Rule 5.
- cage hoop `tube_from_spline_points` mesh downgraded to Box/Cylinder loop → Rule 3.
- release sleeve/latch built at constant radius detached from a scaled rail → Rule 4.
- hinge origin >15mm off the pin/sleeve geometry, or child hinge cylinder not on the axis → origin-far fail.
- drop/swing/fold/telescope collides with body mid-travel (segments folding back onto parent, shuttle hitting rungs) → sampled-pose fail.
- side members become a single member / A-frame / rope → leaves subcategory.

## 与相邻类别的边界
- 不该混入：step-stool / A-frame stepladder（自立、非 building-egress mounted）。
- 不该混入：scaffold / work tower（多柱工作平台，非双-member 爬梯）。
- 不该混入：balcony guardrail / handrail（无 rungs、不可攀爬下降）。
- 不该混入：rope-only / cargo-net descent（无两条刚/柔 side member + rung 的可攀爬梯身）。
- 不该混入：fire-truck aerial ladder（车载伸缩臂，非建筑固定 egress）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 首版 spec；4 family + N multiplicity；family-gated 组合避免非法 cage 组合 |

## 模板实现备注
- 共享 helper：`_cyl_x/_y/_z`（同 origins）；`_cage_hoop_mesh`（tube_from_spline）；`_chain_link`。
- captured overlap（element-scoped allow_overlap）：drop rail↔collar；swing/sill/fold pin↔sleeve↔barrel；telescope rail↔collar；fall-arrest shuttle↔arrest_rail。
- fall-arrest & fold 特别注意 sampled-pose：arrest 组件前置 (+y) 避让 rung 面；fold 段前折 (+y offset) 避免与母段重叠、upper 角度 clamp。
