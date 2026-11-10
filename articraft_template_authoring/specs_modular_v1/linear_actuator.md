# Modular Spec — Robotics / Linear actuator (`linear_actuator`)

## 元信息
| 项 | 值 |
|---|---|
| slug | `linear_actuator` |
| template path | `agent/templates/linear_actuator.py` |
| test path (optional) | `tests/agent/test_linear_actuator_template.py` (not created; sweep is the acceptance signal) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (+ `multiplicity` on the carriage/guide-rod axes; telescoping form uses a serial `linear_chain` of nested tubes) |

`pattern` note: the fixed `frame` root carries a linearly-guided `carriage` child
on a PRISMATIC joint and, when a rotary drive exists, a `lead_screw` /
`drive_pulley` child on a REVOLUTE joint — both parented to the frame
(parallel-children). The telescoping body-form realizes the moving member as a
serial prismatic chain of nested tubes (`stage_1` in `frame`, `stage_2` in
`stage_1`). Multiplicity axes: carriage count and guide-rod count.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (2 picture origins + 7 verified forks) |
| source_index_policy | only adopted module sources are indexed below |

Read in full: picture origins `rec_robotics__linear_actuator__002...` (A, rich
CadQuery rail stage) and `rec_robotics__linear_actuator__001...` (B, compact
all-primitive rail stage); forks `form_rod_cylinder`, `mechanism_belt`,
`skeleton_telescoping`, `skeleton_parallel_motor`, `n_carriage2`, `n_guiderod1`,
and probe `probe_pneumatic`.

## 核心身份

A powered single-DOF device that converts a rotary input (rotating lead screw or
driven belt pulley) or a direct fluid/piston input into ONE controlled
straight-line stroke: a carriage or rod that extends/retracts along a single
linear axis, guided by a rail / tube and supported by a fixed structural body
(extruded aluminium rail, round barrel, or nested telescoping tubes). Must keep:
one primary translational output (PRISMATIC), a fixed guiding body, and — when
driven rotationally — a real REVOLUTE drive element. Must NOT drift into:
`rack_and_pinion_slider` (pinion driving a toothed rack), a passive linear
rail/guide with no drive, a bare lead screw, a plain gearmotor with no linear
stage, or a furniture lift column (telescoping variant).

## 槽位 + 候选模块表

### Slot A：body_form / Primary Form Family (③)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `extruded_rail` | forked_anchor | rec_...__001 (B) + rec_...__002 (A) + n_carriage2 + n_guiderod1 | 001 L32-L219 | eligible if compatible | Planar Boundary Form: flat aluminium extrusion rail + end plates + motor block; open carriage rides on top on guide rods; central screw / side belt. Box/Cylinder part tree. |
| `barrel_tube` | forked_anchor | rec_..._form_rod_cylinder + rec_..._probe_pneumatic | form_rod_cylinder L137-L349 | eligible if compatible | Volumetric Envelope Form: round barrel tube + end caps + gland; coaxial extending rod; internal screw or direct piston. |
| `telescoping_column` | forked_anchor | rec_..._skeleton_telescoping | L17-L157 | eligible if compatible | Macro Surface Construction: base tube + 2 nested inner tubes as a serial prismatic chain; central screw drives the extension. |

### Slot B：drive_mechanism (②)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `lead_screw` | forked_anchor | rec_...__001/002 (A,B) | 001 L178-L219 | eligible if compatible | REVOLUTE `screw_spin` axis x; screw core + ring thread crests + couplers + end journals. |
| `belt_pulley` | forked_anchor | rec_..._mechanism_belt | L416-L458 | eligible if body_form=extruded_rail | REVOLUTE `drive_pulley_spin` axis z; drive pulley + idler + closed belt spans clamped near carriage. |
| `direct_piston` | forked_anchor | rec_..._probe_pneumatic | L254-L270 | eligible if compatible | No rotary drive; the carriage/rod PRISMATIC is the sole driven joint (pneumatic/hydraulic cylinder). |

### Slot C：motor_layout (① drivetrain topology, extruded_rail only)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `inline` | forked_anchor | rec_...__001/002 (A,B) | 001 L70-L81 | eligible if body_form=extruded_rail | Coaxial motor block + cap behind the drive-end plate, on the screw axis. |
| `parallel_offset` | forked_anchor | rec_..._skeleton_parallel_motor | L273-L319 | eligible if body_form=extruded_rail | Motor folded in -Y beside the rail on a bracket, coupled to the screw axis by a reduction belt + drive cover. |

Each supported structural slot reaches ≥2 distinct source-backed candidates
(body_form 3, drive_mechanism 3, motor_layout 2). Size/colour/decoration-only
differences are not candidates. Multiplicity axes (carriage/guide-rod count) are
declared in §8, not as slots.

## 槽位图（slot graph）

pattern: parallel_children (+ multiplicity; telescoping = serial linear_chain)

```
frame (root, body_form ③)
  ├─[PRISMATIC axis x, carriage_JOINT_Z; Mating-free bushing support]→ carriage_{i}  (×carriage_count)
  ├─[REVOLUTE  axis x  @ z=_SCREW_Z]→ lead_screw          (drive=lead_screw)
  └─[REVOLUTE  axis z  @ drive pulley]→ drive_pulley      (drive=belt_pulley)
   (drive=direct_piston → no rotary child)

telescoping_column body_form:
frame(stage_0) ─[PRISMATIC x]→ stage_1 ─[PRISMATIC x]→ stage_2   (+ central lead_screw REVOLUTE x)
```

Interface points:
- carriage↔frame: the carriage bearing shoe(s) ride the guide rod(s) (sliding
  bushing contact, small overlap); the block clears the rail. Prismatic axis x,
  travel `[0, carriage_travel]`.
- lead_screw↔frame: screw end journals seat in the end-plate bearing bores
  (captured overlap). Revolute axis x. Axisymmetric → rotation never collides.
- drive_pulley↔frame: pulley journalled on a frame boss; belt wraps the pulley.
  Revolute axis z (axisymmetric).
- telescoping stages: each inner tube nests inside its parent tube (sliding fit,
  captured overlap). Serial prismatic chain, axis x.

Mutually-exclusive / derived: `belt_pulley` only with `extruded_rail`;
`motor_layout` and carriage/guide-rod multiplicity only with `extruded_rail`;
round forms force inline / single carriage.

## 每槽位 Module Emits / Interfaces

### Slot A / module extruded_rail
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame (rail_extrusion, foot, T-slots, 2 end_plate, motor block/cap or offset bracket+belt, guide_rod_{i}, rail_hole_{i}) | 001 L32-L127 |
| internal joints | none (all frame visuals) | — |
| upstream interface | root — no upstream | — |
| downstream interface | rail top + guide rods (carriage bushing plane); end-plate bores (screw journals) | 001 L84-L90 |

### Slot A / module barrel_tube
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame (barrel_tube, rear/front_cap, gland_ring, band, motor or port bosses, feet); carriage_0 (rod + rod_end_disk + piston_disk) | form_rod_cylinder L161-L286 |
| internal joints | none on frame; carriage rod is the moving member | — |
| downstream interface | front cap bore (rod passage); barrel bore (rod/screw coaxial capture) | form_rod_cylinder L187-L214 |

### Slot A / module telescoping_column
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame (motor, bracket, stage_0 base tube+flange+ring); stage_1, stage_2 nested tubes | skeleton_telescoping L31-L129 |
| internal joints | stage_slide_1 (frame→stage_1), stage_slide_2 (stage_1→stage_2) PRISMATIC axis x | skeleton_telescoping L113-L128 |

### Slot B / module lead_screw
| emits | 描述 | 来源 |
|---|---|---|
| parts | lead_screw (screw_core, thread_crest_{i} rings, couplers, bearing_journal_{i}) | 001 L178-L200 |
| internal joints | screw_spin REVOLUTE axis x, ±π | 001 L211-L218 |

### Slot B / module belt_pulley
| emits | 描述 | 来源 |
|---|---|---|
| parts | drive_pulley (body, flanges, coupler) + frame idler/belt spans/bosses | mechanism_belt L286-L431 |
| internal joints | drive_pulley_spin REVOLUTE axis z, ±π | mechanism_belt L448-L458 |

### Slot B / module direct_piston
| emits | 描述 | 来源 |
|---|---|---|
| parts | none extra (no rotary drive) | probe_pneumatic L254-L270 |
| internal joints | none; carriage PRISMATIC is the sole driven joint | probe_pneumatic L257-L270 |

Active parts have articulation semantics; every non-moving detail (T-slots,
thread crests, belt spans, feet, caps, motor cap) is a `parent.visual(...)`.

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | extruded_rail / barrel_tube / telescoping_column | extruded_rail | choice | deterministic sampler (weighted to extruded_rail) | Slot A |
| drive_mechanism | enum | lead_screw / belt_pulley / direct_piston | lead_screw | conditional | legal set = `_compatible_drives(body_form)` | Slot B |
| motor_layout | enum | inline / parallel_offset | inline | conditional | only extruded_rail; else forced inline | Slot C |
| carriage_count | int | {1, 2} | 1 | conditional | only extruded_rail; else forced 1 | n_carriage2 |
| guide_rod_count | int | {1, 2} | 2 | conditional | only extruded_rail; else forced 2 | n_guiderod1 |
| palette_theme | enum | brushed_aluminum / black_industrial / blue_barrel / steel_gray | brushed_aluminum | choice | ⑥ material/finish | all |
| rail_length | float | [0.55, 0.86] | 0.700 | independent | uniform then clamp; end plates derived | 001/002 |
| carriage_travel | float | [0.06, travel_cap] | 0.170 | inequality | `travel_cap = 0.06` (dual) else `rail_length-0.30`; keeps carriage on rail / clear of neighbour | 001 L209 |
| screw_radius | float | [0.0045, 0.0080] | 0.0055 | independent | uniform then clamp | 001 L180 |
| barrel_length | float | [0.34, 0.50] | 0.420 | independent | uniform then clamp | form_rod_cylinder |
| barrel_radius | float | [0.030, 0.048] | 0.038 | independent | uniform then clamp | probe_pneumatic |
| stroke | float | [0.12, 0.72·barrel_length] | 0.260 | inequality | rod retains barrel engagement at full stroke | form_rod_cylinder L123 |
| (—) | constraint | — | — | inequality | dual carriage: `0.100 - 0.055 ≥ -0.100 + travel + 0.055` ⇒ travel ≤ 0.09 (used 0.06) | 接口 / clearance |

All `conditional` / `inequality` constraints are resolved in `resolve_config`
(never deferred to the builder). Scales are independent unless a row says
otherwise.

## 7.5 编译预算 / compile budget
Per-seed budget: **≤ 6 s** (measured ≈ 0.05–0.30 s/seed). Geometry is
Box/Cylinder only — no CadQuery boolean cuts, no spline sweeps — so tessellation
is trivial. Repeated ring thread-crests and belt teeth reuse one Cylinder/Box
shape and are count-capped (`n_crest ≤ 22`). No hero meshes to down-tessellate.

## Multiplicity / Copy Logic

Two independent multiplicity axes, extruded_rail only:

- **carriage_count** — copied object: full carriage assembly (`carriage_block_{i}`
  + `bearing_shoe_{i}_{j}` + boss + hole visuals) with its own PRISMATIC
  `frame_to_carriage_{i}`.
  - `N_range` (product) [1, 2]; sampling domain weighted `{1:2, 2:1}` (single
    dominant, dual real but rarer). N-samples shown: origins {1}, fork
    n_carriage2 {2}.
  - placement: fixed x = ±0.100 for dual; joint policy: independent prismatic on
    axis (1,0,0), travel capped at 0.06 so the two carriages never collide at any
    sampled pose combination. source/gating: n_carriage2; barrel/telescoping → 1.
- **guide_rod_count** — copied object: `guide_rod_{i}` cylinder (FIXED frame
  visual) + matching `bearing_shoe_{i}_{j}` on each carriage.
  - `N_range` [1, 2]; sampling domain weighted `{2:2, 1:1}`. N-samples: origins
    {2}, fork n_guiderod1 {1}.
  - placement: 2 rods at y=±0.032; 1 rod offset to y=+0.030 (kept out of the
    central-screw yz footprint so the shoe never hits the screw); extrusion body
    provides anti-rotation. source/gating: n_guiderod1; round forms → 2.

- **record_only loops (not swept as anchors):** thread_crest_{i}, belt spans,
  rail_hole_{i}, telescoping stage count (fixed 3) — loop-emitted, indexed,
  FIXED decoration/internal; recorded, not padded into candidate anchors.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | inline single-carriage-on-rail (A,B); serial telescoping nested-tube chain (skeleton_telescoping); parallel/folded offset-motor drivetrain (skeleton_parallel_motor). All forked_anchor. |
| └ multiplicity | 同构件 ×N | 有 | 见 §8: carriage_count {1,2} (n_carriage2), guide_rod_count {1,2} (n_guiderod1). |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | lead-screw REVOLUTE x + carriage PRISMATIC x (A,B); belt-and-pulley REVOLUTE z + carriage PRISMATIC x (mechanism_belt); direct single-PRISMATIC piston, drive removed (probe_pneumatic). All source-backed; each type appears in the sweep. |
| ③ 主体形态家族 | 图&关节不变，换核心 part 的可识别几何形态原型 | 有 | 3 registered `slot_choices` prototypes: `extruded_rail`=Planar Boundary Form (A,B), `barrel_tube`=Volumetric Envelope Form (form_rod_cylinder), `telescoping_column`=Macro Surface Construction (skeleton_telescoping). All forked_anchor. |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 (record_only) | T-slot grooves, thread_crest_{i} ring strips, rail_hole_{i}, belt teeth/spans, socket-head caps, tie-bolt heads. Host-derived parent visuals (crests wrap the screw radius; holes sit on the rail top); no dedicated candidate. |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | rail_length 0.55–0.86, screw_radius 0.0045–0.0080, barrel_length 0.34–0.50, barrel_radius 0.030–0.048 (§7). Motion envelopes: carriage PRISMATIC axis x [0, carriage_travel≤0.06 dual / ≤rail-0.30 single]; barrel rod PRISMATIC x [0, stroke≤0.72·barrel_length]; telescoping stages PRISMATIC x [0, ≤0.15] each; screw/pulley REVOLUTE ±π (axisymmetric). `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses(64)` over all joints + targeted `ctx.pose(primary_prismatic=upper)` asserting +x advance. No `qc_samples` override needed (defaults {0,lower,upper,mid} express the stroke). |
| ⑥ 涂装 | 只改材质/颜色 | 有 (record_only) | 4 palette themes covering metal (brushed/steel), painted (blue barrel), and dark-industrial families ≥ ceil(0.5×4)=2. |

①②③ + N are the source-backed candidate axes. ④⑤⑥ are record_only / companion.

## 采样与覆盖审计

总组合数（合法门控后）：reachable slot-choice tuples = **111** (sweep probe,
saturated). 理由：single structural cell (extruded rail + rotating drive +
sliding carriage) with three form families and gated drive/motor/multiplicity;
richness band normal-low (~8 counted anchors) per the source map.

seed_domain_policy：procedural_first (seed 0 not special-cased).

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` seeds a `random.Random`
and picks `body_form` (weighted), then samples the *compatible* drive / motor /
multiplicity for that form (gating in `_compatible_drives` + `resolve_config`),
then samples continuous scales. `slot_choices_for_seed` reports the 6-tuple
consumed by `axis_realization`. Compatibility gating forbids illegal combos
(belt on a round barrel; multi-carriage/telescoping on a barrel) so every
sampled seed is buildable; corner seeds are real reachable seeds so the gating
stays consistent. No curated/modulo table, no regression overrides.

Topology target：reachable 111 combos (report-only); acceptable for a
single-cell subcategory whose honest ①/②/③ + N vocabulary saturates near the
low end of the normal band (source-anchor upper bound, see source map §5).

Controlled local parameterization：rail_length, carriage_travel (inequality),
screw_radius, barrel_length, barrel_radius, stroke (inequality) — all clamped /
derived in `resolve_config`; none breaks the bushing support, screw-journal
seating, nested-tube capture, or dual-carriage clearance.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted body_form; gated drive/motor/counts; then continuous scales | slot_choices_for_seed matches build choices |
| compatibility matrix | belt_pulley ⇒ extruded_rail; motor_layout/carriage/guide-rod multiplicity ⇒ extruded_rail; round forms ⇒ inline/single/2-rod | no floating, collision, axis, or multiplicity failures |
| controlled local variation | 6 continuous scales, clamped/derived | proportions vary without breaking interfaces/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass; 0-999 maturity audit | axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form (③) | 3 | yes | yes | Planar / Volumetric / Macro-Surface prototypes |
| drive_mechanism (②) | 3 | yes | yes | lead_screw / belt_pulley / direct_piston |
| motor_layout (①) | 2 | yes | no | extruded_rail only; folded into the rail form |

## Validator

- slot_choices_for_seed returns implemented module names (6-tuple).
- config_from_seed uses deterministic procedural sampling for all seeds (incl. 0).
- compatibility gating prevents illegal module combinations (resolve_config).
- no regression overrides; no curated/modulo main domain.
- continuous scales clamped/derived in resolve_config; travel/stroke inequalities
  keep carriages on the rail and rods engaged.
- key joints: carriage/rod PRISMATIC axis x; lead_screw REVOLUTE x; drive_pulley
  REVOLUTE z; telescoping serial PRISMATIC x.
- copied carriages/guide rods follow indexed naming + fixed placement policy.
- captured/nested overlaps (bushings, journals, nested tubes, belt-on-pulley,
  rod-in-barrel) are element-scoped `allow_overlap`, never broad part-level.

## Reject cases

- A carriage/rod with no PRISMATIC output, or a drive whose axis is wrong.
- Rack-and-pinion drive (neighbour subcategory `rack_and_pinion_slider`).
- Belt drive on a round barrel, or multi-carriage/telescoping on a barrel.
- Guide rod placed in the central screw's yz footprint (shoe would hit the screw).
- Dual carriages whose travel lets them collide at a sampled pose.
- Down-tessellating to hero meshes / CadQuery booleans (blows the compile budget).
- Floating drive/idler/belt visuals with no support path to the frame body.

## 与相邻类别的边界

- 不该混入：`rack_and_pinion_slider`（pinion 齿轮驱动齿条；这里是螺杆/皮带/直接推杆驱动）。
- 不该混入：passive linear rail / linear guide（无驱动元件）。
- 不该混入：bare lead screw / gearmotor-only（缺少必要功能层）。
- 不该混入：furniture lift column（telescoping 变体必须是带可见驱动的单轴动力伸缩）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Implemented all-primitive; sweep 0-35 verdict=pass (fast/final/corner 1.0), module_topology_diversity pass, 0 failed corners. Barrel `direct_piston`+telescoping combos read as pneumatic/telescopic actuators. |

## 模板实现备注（可选）

- Shared helpers: `_guide_rod_layout`, `_build_rail_carriage`,
  `_build_lead_screw_rail/_barrel`, `_add_tube_visuals` (telescoping stages),
  `_add_belt_frame_visuals`.
- Single-sourced geometric constants: `_RAIL_TOP`, `_SCREW_Z`,
  `_CARRIAGE_JOINT_Z`, `_CARRIAGE_BLOCK_BOTTOM_Z`, `_GUIDE_ROD_Z/_R` (Contract 3c).
- Captured-overlap `allow_overlap` sites: bushing shoe↔guide rod; screw
  journal↔end plate / inline motor / (parallel) bracket+cover+reduction belt;
  belt span↔drive pulley + boss↔pulley; barrel bore↔rod/piston/screw; nested
  telescoping tube pairs + central screw.

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | extruded_rail + lead_screw + inline | rec_...__001 (B) | L32-L219 | rail part tree, carriage/shoe, screw, joints (all-primitive) |
| S2 | A/B/C | extruded_rail (rich) | rec_...__002 (A) | L131-L309 | rail-stage confirmation, journal/bearing idiom |
| S3 | A | barrel_tube | rec_..._form_rod_cylinder | L137-L349 | barrel + coaxial rod + internal screw |
| S4 | A | barrel_tube (direct) | rec_..._probe_pneumatic | L78-L270 | pneumatic cylinder: caps, gland, piston, single prismatic |
| S5 | B | belt_pulley | rec_..._mechanism_belt | L197-L458 | drive pulley + idler + belt loop, revolute z |
| S6 | A | telescoping_column | rec_..._skeleton_telescoping | L17-L157 | nested-tube serial prismatic chain |
| S7 | C | parallel_offset | rec_..._skeleton_parallel_motor | L222-L448 | folded offset motor + reduction belt |
| S8 | multiplicity | carriage_count=2 | rec_..._n_carriage2 | L129-L228 | indexed carriage copy + independent prismatic |
| S9 | multiplicity | guide_rod_count=1 | rec_..._n_guiderod1 | (origin B delta) | single guide rod + matching shoe |
