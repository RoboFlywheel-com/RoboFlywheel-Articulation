# table_with_drawers_no_door — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `table_with_drawers_no_door` |
| template path | `agent/templates/table_with_drawers_no_door.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 3 (原始 origin_anchor) + 10 (planned forked_anchor variants) = 13 |
| read_count | 13 |
| read_scope | all 5-star origin + variant records under `data/records/rec_picturex_0611__table_with_drawers_no_door_*` and `rec_0611_table_with_drawers_no_door_var_*` |
| source_index_policy | only adopted module sources indexed in module tables below |

## 核心身份

功能定义：a table (worktop-height, 0.72-0.82m from floor, worktop overhangs the case) whose visible storage identity is provided by one or more PRISMATIC front drawers. The apron/case beneath the top holds drawers only — never doors, never open shelves, never a cabinet-style enclosed compartment. Legs or a case-derived support carry the load to the ground.

Must keep: worktop overhang; visible drawer front(s) with articulated PRISMATIC forward travel (`-Y` axis convention: axis=`(0,-1,0)` in this template); support-to-ground path; upper/lower rails or case wall framing the drawer opening; a real anchoring visual behind every joint.

Must NOT become:
- **table_with_doors** — no REVOLUTE door-style hinged panel; no visible cabinet-door faceframe.
- **plain writing_desk** — a plain writing desk *with no drawers* is another slug; here at least one drawer is mandatory.
- **desk_with_drawer / drawer_cabinet_with_sliding_drawers** — those are workstation-desk or full cabinet slugs; here the identity is a *table* (long/narrow console/dining-table proportion, worktop overhang) NOT a broad workstation desktop nor a floor-standing cabinet.

## 槽位 + 候选模块表

### Slot A: worktop_form (③ Primary Form Family, form-dominated ③ slot)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rounded_rect_top` | forked_anchor | `rec_picturex_0611__table_with_drawers_no_door__001__png_42a5822a984f43559406c747740192ef` | model.py:L20-L27 (`_rounded_top`) + L98-L120 (tabletop+molding) | eligible if compatible | Planar Boundary Form: axis-aligned rounded rectangle with filleted edges + inset beveled molding band; single-slab worktop. |
| `overhanging_rect_top` | forked_anchor | `rec_picturex_0611__table_with_drawers_no_door__002__png_c1733499c8c544578ce4c1b03dd66481` | model.py:L137-L141 (tabletop lofting) + L131-L142 (frame overhang) | eligible if compatible | Planar Boundary Form: rectangular slab with filleted edges overhanging the case on all four sides; substantial ~40mm overhang. |
| `long_walnut_slab_top` | forked_anchor | `rec_picturex_0611__table_with_drawers_no_door__003__png_7b5f2d980e9d47ee8bbaaa1d3b915114` | model.py:L64-L90 (`_tabletop_shape`) + L184-L188 (tabletop visual) | eligible if compatible | Planar Boundary Form (with Macro Surface Construction accent): long rectangular slab with grain cuts sculpted into the top face; substantial 2.6× width:depth aspect ratio. |
| `demilune_top` | world_knowledge_extrapolation (③) | anchors: rec_002 (rectangular) + rec_003 (long slab) + reviewer | mesh generated in `_build_demilune_top` | eligible if compatible | Planar Boundary Form: half-elliptical worktop (front edge straight, rear edge curved) — a classic demilune console. Same part tree (frame+drawer), same PRISMATIC interfaces, only worktop planar boundary differs. `form_subtype=Planar Boundary Form`. |

### Slot B: support_style (① skeleton / structural topology)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `four_tapered_legs` | forked_anchor | `rec_picturex_0611__table_with_drawers_no_door__001__png_42a5822a984f43559406c747740192ef` | model.py:L38-L45 (`_tapered_leg`) + L164-L181 (leg placement) | eligible if compatible | 4 corner legs (mesh loft from square top → square base), each independently reaching the floor; skeleton graph has 4 leaf leg visuals sharing the case as their parent. |
| `four_turned_legs` | forked_anchor | `rec_picturex_0611__table_with_drawers_no_door__002__png_c1733499c8c544578ce4c1b03dd66481` | model.py:L34-L57 (`_turned_leg`) + L84-L86 (leg placement) | eligible if compatible | 4 turned-profile legs (revolve of a moulded profile), same 4-corner skeleton, different Volumetric Envelope of each leg. |
| `four_splayed_legs` | forked_anchor | `rec_picturex_0611__table_with_drawers_no_door__003__png_7b5f2d980e9d47ee8bbaaa1d3b915114` | model.py:L27-L61 (`_splayed_leg_mesh`) + L252-L274 (leg placement) | eligible if compatible | 4 splayed legs (top center displaced inward relative to bottom center); adds outward rake to the leg endpoints; same 4-leg parallel-children skeleton. |
| `trestle` | forked_anchor | `rec_0611_table_with_drawers_no_door_var_support_trestle` from rec_003 | inherits `_splayed_leg_mesh` + trestle-style planks | eligible if compatible | Two lateral plank-style trestles + a stretcher (2 vertical plank visuals + 1 lower horizontal stretcher); skeleton edge count differs from the 4-leg parallel children — 3 leaf visuals for support. |
| `twin_pedestal` | forked_anchor | `rec_0611_table_with_drawers_no_door_var_support_twin_pedestal` from rec_003 | inherits `_splayed_leg_mesh` + boxed pedestal | eligible if compatible | Two solid boxed pedestals under the two ends of the case (each a rectangular box footing the two ends); skeleton has 2 wide pedestal visuals replacing 4 legs. |

### Slot C: drawer_count (① multiplicity)

Multiplicity axis: `drawer_count ∈ [1, 5]`. See §8.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `n1_drawer_bank` | forked_anchor | rec_001 (single wide) | model.py:L216-L310 (one drawer + PRISMATIC) | eligible if compatible | 1 wide drawer spanning the front opening; single PRISMATIC joint. |
| `n2_drawer_bank` | forked_anchor | rec_002 (two side-by-side) | model.py:L162-L216 (`for index, x in enumerate(drawer_centers)`) | eligible if compatible | 2 drawers side-by-side across the front. |
| `n3_drawer_bank` | forked_anchor | `rec_0611_table_with_drawers_no_door_var_drawer_count_3` from rec_002 | inherits `_build_drawer` | eligible if compatible | 3 drawers side-by-side; narrower per-drawer width. |
| `n4_drawer_bank` | world_knowledge_extrapolation (① multiplicity — coverage of the declared N range, no new skeleton element) | anchors: n2, n3, n5 | procedural | eligible if compatible | 4 drawers side-by-side (interpolates within the declared N range). |
| `n5_drawer_bank` | forked_anchor | `rec_0611_table_with_drawers_no_door_var_drawer_count_5_narrow` from rec_003 | inherits `_drawer_front_shape` + `_drawer_box_shape` | eligible if compatible | 5 narrow drawers across a wide front. |

### Slot D: palette_style (⑥ material/palette/finish)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `weathered_taupe_wood` | record_only | rec_001 | model.py:L71-L86 | eligible | Warm taupe wood + dark grain + dark aged metal hardware. |
| `warm_walnut` | record_only | rec_002 | model.py:L118-L122 | eligible | Warm walnut + darker top + aged brass hardware. |
| `dark_walnut_espresso` | record_only | rec_003 | model.py:L150-L173 | eligible | Deep walnut top + espresso legs + blackened steel hardware. |
| `painted_white` | world_knowledge_extrapolation (⑥) | reviewer | palette dict | eligible | Off-white painted case + oak top + bronze hardware — realistic modern console palette. |
| `oak_light` | world_knowledge_extrapolation (⑥) | reviewer | palette dict | eligible | Pale oak with brushed nickel hardware — realistic Scandinavian console palette. |

## 槽位图（slot graph）

pattern: `mixed` (parallel_children beneath a single fixed root frame, plus multiplicity along the drawer axis)

```
frame (root) ─┬─ worktop_form  [visual: parent visual on frame, 0 joints — Rule 1: worktop is fixed]
              ├─ support_style [visuals: 2..4 leg/pedestal/trestle visuals attached as parent.visual on frame]
              ├─ apron/rails   [parent visuals on frame — the drawer opening frame]
              └─ N × drawer_i   [each: separate PART, PRISMATIC joint frame→drawer_i, axis (0,-1,0)]
```

- Every drawer is a separate PART attached to `frame` by a PRISMATIC joint (axis `(0,-1,0)`, forward = drawer opens toward the viewer, `[0, drawer_travel]`). Every such joint declares a `MatingContract` pinning `drawer_i.front_panel` (negative_y face) to `frame.front_lower_rail` (positive_z face) so contact is enforced (mating faces on real geometry).
- Support (legs / trestle / twin_pedestal) and the worktop are inline visuals on the single `frame` PART (Rule 1: they do not articulate).
- worktop_form and support_style are **independent** parallel choices under `frame`; drawer_count is an independent multiplicity axis.
- Drawer opening is bounded by rail geometry above/below the drawer bank. Adjacent drawers share the same opening plane — closed drawers all lie flush at `y = -case_depth/2 + front_thickness/2`.

## 每槽位 Module Emits / Interfaces

### Slot A / worktop_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | (none — worktop is a parent visual on `frame`, Rule 1) | S1 rec_001 L98-L120 |
| internal joints | none | — |
| upstream interface | worktop top-face contact plane at `z = case_top + worktop_thickness/2` | rec_001 L98-L108 |
| downstream interface | worktop bottom-face `negative_z` face, seats on frame top rails / apron | rec_001 L98-L108 |

### Slot B / support_style
| emits | 描述 | 来源 |
|---|---|---|
| parts | (none — supports are parent visuals on `frame`) | rec_001 L164-L181, rec_003 L252-L274 |
| internal joints | none | — |
| upstream interface | top of each support element contacts case underside at `z = case_bottom_z` | rec_001 L164-L181 |
| downstream interface | bottom of each support element at `z = 0.0` (ground plane) | rec_001 L164-L181 |

### Slot C / drawer_i (per-drawer)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drawer_i` (one part per drawer) | rec_001 L216-L256, rec_002 L163-L200, rec_003 L295-L342 |
| internal joints | none (front panel + box shell + pull hardware are inline visuals of `drawer_i`) | rec_001 L229-L276 |
| upstream interface (from frame) | drawer front `negative_y` face; MatingContract to frame `front_lower_rail` `positive_z` face | rec_001 L293-L310, rec_003 L344-L361 |
| downstream interface | none (drawer is a leaf part) | — |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| worktop_form | enum | rounded_rect_top / overhanging_rect_top / long_walnut_slab_top / demilune_top | overhanging_rect_top | choice | procedural sampler | Slot A table |
| support_style | enum | four_tapered_legs / four_turned_legs / four_splayed_legs / trestle / twin_pedestal | four_turned_legs | choice | procedural sampler | Slot B table |
| drawer_count | int | 1..5 | 2 | independent | weighted `rng.choices((1,2,3,4,5), weights=(0.15,0.35,0.25,0.15,0.10))` | Slot C table |
| palette_style | enum | 5 palettes | warm_walnut | choice | procedural sampler | Slot D table |
| case_width | float | [0.80, 1.35] m | 1.05 | independent | uniform sample, then clamp | rec_001..rec_003 aabb widths 0.94–1.30 |
| case_depth | float | [0.34, 0.52] m | 0.42 | independent | uniform sample, then clamp | rec_001..rec_003 aabb depths 0.40–0.50 |
| worktop_thickness | float | [0.028, 0.048] m | 0.036 | independent | uniform | rec_001..rec_003 |
| worktop_overhang | float | derived | derived | equation | `= max(0.020, 0.05 * case_depth)`; if worktop_form == `demilune_top`, front overhang forced to 0 (straight edge is case front) | rec_002 L137-L141 |
| worktop_length | float | derived | derived | equation | rectangular: `= case_width + 2*worktop_side_overhang`; demilune: rectangular half-length = case_width * 1.02 | rec_002 |
| leg_height | float | derived | derived | equation | `= case_bottom_z` where case_bottom_z is drawer-bank total height + rails; overall table height 0.72..0.82 | rec_001..rec_003 |
| drawer_travel | float | [0.16, 0.28] m | 0.22 | independent | uniform, then clamp to `drawer_box_depth * 0.85` | rec_001 (0.180), rec_002 (0.235), rec_003 (0.270) |
| drawer_front_width | float | derived | derived | equation | `= (drawer_bank_width - (N+1)*divider_thickness) / N` | multiplicity math |
| drawer_front_height | float | derived | derived | equation | `= drawer_bank_height - 2 * rail_gap`; drawer_bank_height ~ 0.10..0.14m | rec_001..rec_003 |
| drawer_box_depth | float | derived | derived | equation | `= case_depth - back_thickness - 0.04` | rec_001..rec_003 |
| (—) | constraint | — | — | inequality | drawer_travel ≤ drawer_box_depth * 0.85 (retained insertion ≥ 15%); if violated, shrink drawer_travel | rec_001 L293-L310 retained_insertion 0.040 |
| (—) | constraint | — | — | inequality | drawer_front_width ≥ 0.14m and case_width ≥ drawer_count * 0.16m; if violated, either reduce drawer_count or widen case_width to fit | packing feasibility |
| (—) | constraint | — | — | conditional | `demilune_top` restricted to `drawer_count ≤ 3`: narrow front doesn't accommodate more than 3 drawers | reviewer + form fit |

### 7.5 编译预算 / compile budget

Per-seed compile budget: **~15s** (target). Rationale: cadquery lofted legs (`_turned_leg`) and demilune worktop are the heaviest ops; all other visuals are `Box` / `Cylinder` primitives. `_splayed_leg_mesh` is hand-built `MeshGeometry` (fast). 4 legs × cadquery loft per seed keeps compile bounded. tessellation: turned-leg profile 16 revolve segments; worktop fillet radius kept as literal (~6mm); no fine sculpting cuts on the top face in template (grain lines are `Box` visuals only, at most 3 per seed to reduce cost). `--compile-timeout 120` gives 8× headroom for the tail.

## Multiplicity / Copy Logic

- `count_param`: `drawer_count`
- `N_range`: `[1, 5]` (product-full range; sweep sampled range same)
- `sampling domain (weights)`: N=1 (0.15), N=2 (0.35), N=3 (0.25), N=4 (0.15), N=5 (0.10) — smaller N weighted higher (matches 5-star source distribution: rec_001 N=1, rec_002 N=2, rec_003 N=2 + planned N=3,5 forks).
- copied object: per-drawer PART named `drawer_{i}`, using shared helper `_build_drawer_visuals(drawer, r, i)`; each has its own PRISMATIC joint `frame_to_drawer_{i}`.
- naming: `drawer_{i}`, `frame_to_drawer_{i}`, `drawer_runner_{i}`.
- placement: drawer center `x = -(bank_width - front_w)/2 + i*(front_w + divider)`.
- joint policy: uniform — every drawer PRISMATIC on axis `(0,-1,0)`, `[0, drawer_travel]`, MatingContract on `front_panel(negative_y)` → `front_lower_rail(positive_z)`.
- gating: `demilune_top` clamps N≤3; if `case_width < drawer_count * 0.16`, `drawer_count` is shrunk in `resolve_config` (procedural degrade, not builder failure).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | **有** | (a) drawer multiplicity 1..5 (每 N 加/减一个 drawer part + 一条 PRISMATIC 边) — `forked_anchor` (rec_001 N=1, rec_002 N=2, rec_003 N=2 + variants N=3, N=5); (b) support_style skeleton: four_tapered / four_turned / four_splayed / trestle (3 support visuals) / twin_pedestal (2 pedestal visuals) — `forked_anchor` origins + trestle/twin_pedestal forks. |
| └ multiplicity | 同构件 ×N | **有** | drawer N ∈ [1, 5]，权重 (0.15, 0.35, 0.25, 0.15, 0.10)；见 §8。 |
| ② 关节类型 | 图不变,某条边换 type/轴 | **有** | 每 drawer 都是 PRISMATIC axis `(0,-1,0)` `[0, drawer_travel]` — 单一 non-FIXED joint 类型。声明的类型（PRISMATIC）在 sweep 中必出现（每 seed 1..5 个 PRISMATIC 关节）。`forked_anchor` (rec_001/002/003 all PRISMATIC). |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变,换核心 part 的可识别几何形态原型 | **有** | worktop_form 4 candidates: `rounded_rect_top`（Planar Boundary Form: 圆角矩形）、`overhanging_rect_top`（Planar Boundary Form: 矩形悬挑）、`long_walnut_slab_top`（Planar Boundary Form: 长比例矩形 + Macro Surface Construction 表面凹槽）、`demilune_top`（Planar Boundary Form: 半椭圆）。前 3 `forked_anchor`, `demilune_top` `world_knowledge_extrapolation`. 登记进 `slot_choices`. |
| ④ 表面装饰 | 原型不变,叠加表面细节 / 改装饰数 | **有** | 装饰：drawer_pull hardware（knob / bar / recessed pull — 3 style + 数量档 1..N knobs per drawer）、drawer front grain lines（0..3 count per drawer）。装饰几何都是宿主 drawer 表面的 host-conformal `Box`/`Cylinder`；`record_only + world_knowledge_extrapolation`. 派生顺序 ③→⑤→④（drawer 前面板 form 定型后再放 pull）。 |
| ⑤ 尺寸/行程 | 离散全不变,只连续改尺寸/比例/行程 | **有** | case_width ∈ [0.80, 1.35]; case_depth ∈ [0.34, 0.52]; worktop_thickness ∈ [0.028, 0.048]; drawer_travel ∈ [0.16, 0.28]. **PRISMATIC 关节运动包络**: axis `(0,-1,0)`, 开启方向 -Y (向观察者), `[0, drawer_travel]`; **motion_test_plan**: `qc_samples=4` (0, mid, upper, and 0.9*upper) covering closed / partially-open / fully-extended states; `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)` covers pairwise drawer combos. Targeted `ctx.pose({slide: r.drawer_travel})` asserts extended drawer moves forward > 0.15m and remains laterally within the case. |
| ⑥ 涂装 | 几何全不变,只改材质/颜色 | **有** | 5 palette_style: weathered_taupe_wood (record_only rec_001), warm_walnut (record_only rec_002), dark_walnut_espresso (record_only rec_003), painted_white (world_knowledge_extrapolation), oak_light (world_knowledge_extrapolation). 材质大类覆盖: painted, wood_stain (walnut variants), painted_metal (hardware) — 覆盖 painted + wood ≥ 2 大类。 |

## 采样与覆盖审计

总组合数：worktop_form (4) × support_style (5) × drawer_count (5) × palette_style (5) = **500** discrete slot tuples.

理由: 4 × 5 × 5 × 5 covers form × skeleton × multiplicity × palette. compatibility gate (demilune → N≤3) rules out (1×2×5) = 10 tuples, giving 490 legal tuples.

seed_domain_policy: `procedural_first`

Procedural Sampling / Sweep Plan:
- `config_from_seed(seed)` uses `random.Random(seed)` and independently samples each enum + the multiplicity N via weighted choice, then samples continuous case_width/case_depth/worktop_thickness/drawer_travel uniformly in declared range.
- `resolve_config` applies compatibility gates: demilune → N≤3; case_width < N*0.16 → shrink N to floor(case_width/0.16).
- `resolve_config` clamps continuous scales, derives dependent dims (worktop_length, worktop_overhang, drawer_front_width, drawer_box_depth), and applies inequality projection for drawer_travel ≤ 0.85*box_depth.
- No `seed=0` special-case; `config_from_seed(0)` samples like any other seed.
- Random sweep: fast 0-15, final 16-35, corner append; smoke probe 0-4 pre-full-sweep.

Topology target: 1000-seed distinct slot tuple target ≥ 300; here declared combination space 490 legal → an easy target.

Controlled local parameterization: case_width_scale (0.80..1.35), case_depth_scale (0.34..0.52), worktop_thickness (0.028..0.048), drawer_travel (0.16..0.28). All clamped & derived in `resolve_config` per §7 contract.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | independent per-slot; weighted drawer_count | `slot_choices_for_seed` matches build choices; palette diversity visible in 0-9 batch |
| compatibility matrix | demilune→N≤3; case_width→shrink N to fit; drawer_travel→shrink to 0.85*box_depth | no illegal build; degrades cleanly |
| controlled local variation | case_width/case_depth/worktop_thickness/drawer_travel — clamp+derive | proportions vary without breaking mating / clearance / joint origin |
| regression overrides | none at first version | reserved for known-failure seeds |
| random sweep | seeds 0-15 fast, 0-35 final, corner append | contract failures; axis_realization; viewer focus for form/skeleton/palette |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| worktop_form | 4 | yes | yes | 3 forked_anchor + 1 world_knowledge_extrapolation |
| support_style | 5 | yes | yes | 3 forked_anchor origins + 2 forked_anchor variants |
| drawer_count | 5 | yes | yes | multiplicity axis (records N=1,2,3,5; N=4 world_knowledge covers range) |
| palette_style | 5 | yes | yes | 3 record_only + 2 world_knowledge_extrapolation |

## Validator

- `slot_choices_for_seed` returns implemented module names matching the build.
- `config_from_seed` uses deterministic procedural sampling for all seeds (including 0).
- Compatibility gates prevent demilune×N>3 and infeasible case_width×N combos in `resolve_config`.
- No regression overrides.
- No small curated table as seed domain.
- All continuous scales clamped in `resolve_config`; derived dims (worktop_length, worktop_overhang, drawer_front_width, drawer_box_depth) computed there; drawer_travel projected to feasible region.
- MatingContract present on every PRISMATIC drawer joint (front_panel negative_y → front_lower_rail positive_z, `contact_tol=0.001`).
- All 4 legs / 3 trestle visuals / 2 twin-pedestal visuals sit inside the frame PART as parent visuals (Rule 1).
- No FIXED articulation (every non-articulating detail is a parent visual).
- Every drawer has PRISMATIC axis `(0,-1,0)`, `[0, drawer_travel]`.
- No door/hinged panel; no REVOLUTE joint anywhere.
- `run_tests`: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)`; targeted `ctx.pose({slide_0: drawer_travel})` proves forward travel; `fail_if_joint_mating_has_gap`; `fail_if_articulation_origin_far_from_geometry`.

## Reject cases

- `worktop_form=demilune_top` with drawer_count>3: infeasible narrow front — degraded to N=3.
- case_width < 0.80m or > 1.40m: identity drift toward small end-table or dining table — clamped at `resolve_config`.
- drawer_travel > drawer_box_depth * 0.85: retained insertion falls below 15% (drawer would fall out) — shrunk.
- Any REVOLUTE joint (would be a lid/door): forbidden by construction.
- Drawer overlapping worktop or rails in closed pose: MatingContract fails; joint origin off geometry: joint-origin-far check fails.
- Legs floating above the ground (leg bottom_z > 0.01): would break connectivity — legs authored so bottom face touches z=0.

## 与相邻类别的边界

- 不该混入 table_with_doors: 本类别绝无 hinged REVOLUTE door/panel; only PRISMATIC drawers. Verified by test asserting `all(j.articulation_type == PRISMATIC for j in movable_joints)`.
- 不该混入 plain_writing_desk: 本类别至少 1 个 drawer；`drawer_count ≥ 1` 硬约束。
- 不该混入 desk_with_drawer / drawer_cabinet_with_sliding_drawers: 本类别核心是 *table*（长条 console/table 比例，worktop 悬挑，legs 或 trestle 支撑）；不是宽台面办公桌，也不是落地 cabinet。identity aabb 比例：case_width 0.80..1.35, case_depth 0.34..0.52, height 0.72..0.82；worktop 至少四面 overhang 或前后 overhang（demilune 例外，前边直）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Spec authored from 3 origin_anchor 5★ records + planned 10 forked_anchor variants. Slot A (③) covers 4 form_subtype prototypes (3 forked_anchor + 1 world_knowledge_extrapolation demilune). Slot B (①) covers 5 skeleton variants (all forked_anchor). Multiplicity N=1..5 with 4 forked + 1 world_knowledge interpolation. Palette ×5 with ≥2 material大类 (painted, wood_stain). |
