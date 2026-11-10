# Manual water dispenser pump — Modular Spec

> Source pool: articraft_data `picture/0611/Manual_water_dispenser_pump` — 2 parent origins
> (`rec_picturex_0611__manual_water_dispenser_pump__001` blue+white side-outlet dispenser,
> `rec_picturex_0611__manual_water_dispenser_pump__002` ivory hand-pump w/ D-handle + flexible
> hose) + 8 fork variants (`rec_0611_manual_water_dispenser_pump_var_*`). All 10 records
> 5★. `model.py:Lx-Ly` lines below cite each record's active `revisions/rev_000001/model.py`.

## 元信息
| 项 | 值 |
|---|---|
| slug | `manual_water_dispenser_pump` |
| template path | `agent/templates/manual_water_dispenser_pump.py` |
| test path (optional) | not written (sweep is the acceptance signal) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (root `pump_body` at z=0 carries a bottle-mount interface, a side spout, and one child actuation part; spout may itself be an articulated child) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 (2 parents + 8 fork variants, all rating=5) |
| read_count | 10 (every `revisions/rev_000001/model.py` read fully: build_object_model + run_tests) |
| read_scope | all 5-star samples in this category (`data/records/rec_picturex_0611__manual_water_dispenser_pump__001|002` + all `rec_0611_manual_water_dispenser_pump_var_*`) |
| source_index_policy | only adopted module sources are indexed below and in §14 |

Redundancy / consolidation notes:
- All 10 records preserve the same two-part topology (`pump_body` root + one moving `plunger`/`lever`/`spout` child) and a single primary actuation joint. Variants diff exactly one axis at a time: actuation type (3 variants), spout treatment (2 variants), bottle interface (2 variants), plunger stages (1 variant, a sub-family of top_plunger).
- `plunger_stages_two_stage_stem` is a sub-detail of the top-plunger actuation (adds a stepped stem inside the same PRISMATIC top plunger); NOT registered as a separate actuation candidate — expressed as a boolean detail on the `top_plunger` module (see §7 `plunger_stages`).
- Both origins use identical mechanism semantics (single non-fixed joint on a plunger/lever child); this makes actuation the primary ② axis and lets the spout become an independent slot (fixed on the body, or itself REVOLUTE for `folding_spout`).

## 核心身份

A hand-actuated pump head that screws (or clamps) onto the top of an inverted water bottle
and delivers water through a side spout when the user pushes/pulls a plunger, lever, or
bellows. Root part is `pump_body` (grounded at z=0, axis +Z; the bottle itself is context
and NOT modeled). One child moving part carries the identity actuation — a **single
non-FIXED mechanism joint** (PRISMATIC top plunger, REVOLUTE top/side lever, PRISMATIC
bellows compression). A side spout on the pump_body delivers water (short curved elbow,
tall arched gooseneck, or a foldable REVOLUTE hinged spout — the only case that adds a
second non-fixed joint).

The pump body is **form-dominated** (③ Primary Form Family slot): a tall corrugated /
transparent spring housing with visible bellows ribs (parent 001), a slim stepped shell
with molded bands (parent 002), and a squatter round body cover extrapolated forms
observed in the parent + variant pool.

Not a: refillable soap/lotion pump-bottle (that's `container_pump`; container_pump is
mounted **on** its bottle, water-dispenser pumps mount **into** an inverted 3–5 gal
bottle); tap-only water dispenser (no pump mechanism); manual air pump (no bottle interface,
long piston-only stroke).

## 槽位 + 候选模块表

> Slot A `body_form` is the ③ Primary Form Family slot (registered per §8.5). It changes
> the `pump_body` shell prototype — the same part tree, same primitive family (lathe /
> tapered lofted cylinder), same collar/plunger interface, different Volumetric Envelope
> silhouette. Slot B `bottle_interface` swaps the base-mount features on `pump_body`.
> Slot C `actuation` is the identity mechanism (single non-fixed joint on the moving
> child). Slot D `spout` swaps the side outlet visuals (fixed) OR spawns a REVOLUTE child.

### Slot A：body_form (③ Primary Form Family — root `pump_body` shell prototype)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| tall_spring_chamber | forked_anchor | `rec_picturex_0611__manual_water_dispenser_pump__001` | `_main_housing` L38-58, spring_chamber + bellows_ribs L134-160, return_spring `tube_from_spline_points` L162-186 | eligible if compatible | Tall transparent spring-chamber housing with visible corrugated bellows ribs stacked around a clear tube and a metal helical return spring; `_main_housing` is a lofted CadQuery hollow taper (form_subtype = Volumetric Envelope Form) |
| slim_stepped_column | forked_anchor | `rec_picturex_0611__manual_water_dispenser_pump__002` | `housing_shell` `LatheGeometry.from_shell_profiles` L98-127, torus bands L131-149 | eligible if compatible | Slim narrow stepped lathe housing with three torus bands (radius ≈0.015-0.018) and molded shoulders; form_subtype = Volumetric Envelope Form |
| squat_round_body | world_knowledge_extrapolation | anchors: parent 001 + parent 002 | n/a (procedurally generated wider/shorter lathe shell using the same `LatheGeometry.from_shell_profiles` primitive as slim_stepped_column) | eligible if compatible | Shorter (H≈0.14) wider (R≈0.055) round barrel body, common on countertop bottle dispensers; form_subtype = Volumetric Envelope Form. Same lathe-shell primitive, same collar/plunger interface — differs only in the discrete envelope proportions (H,R families) not in scaled sizes |

Notes: 3 candidates (target 3–6). The third is `world_knowledge_extrapolation` — same lathe primitive as `slim_stepped_column`, different discrete envelope prototype (shorter+wider silhouette family that appears on real 3–5 gal countertop pumps but is not in our 5★ pool). Approved because both existing 5★ anchors already demonstrate the lathe-shell primitive is buildable and reads as a manual-water-dispenser pump; the new candidate keeps part tree / primitive family / neck & plunger interface constant and only changes discrete H/R envelope prototype.

### Slot B：bottle_interface (① mounting-feature family on `pump_body` base)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| thread_collar | forked_anchor | `rec_0611_manual_water_dispenser_pump_var_bottle_interface_thread_collar` (from parent 002) | `mounting_collar` L91-94, `bottle_gasket` torus L168-181, base collar rib set | eligible if compatible | Externally-threaded ivory collar with elastomer gasket ring at the base; standard screw-on interface |
| stepped_socket | forked_anchor | `rec_picturex_0611__manual_water_dispenser_pump__001` | `neck_socket` + `socket_shoulder` + `white_mount_ring` + `blue_lock_ring` + `socket_thread_i` L104-131 | eligible if compatible | Stacked ring stepped socket with visible thread rings on a wider clear-blue base plus a locking ring; press-into-neck style |

Notes: 2 candidates (below 3-target). Reason: the 5★ variant pool covers only two distinct bottle-interface families (thread collar from 002 + stepped socket from 001; the `cam_clamp` variant reuses the bottle_gasket ring without adding a distinct part-tree / joint change and is therefore folded into `thread_collar` as a colorway/detail; documented so downstream reviewers can add a proper cam_clamp candidate when a stronger 5★ source emerges).

### Slot C：actuation (② mechanism-type — the identity single non-fixed joint on the child part)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|---|
| top_plunger | forked_anchor | `rec_picturex_0611__manual_water_dispenser_pump__001` | plunger part L260-291, `pump_to_plunger` PRISMATIC +Z L292-311 | eligible if compatible | Rounded palm button + vertical piston stem + return-stop flange + piston seal; PRISMATIC axis (0,0,1) travel ≈0.020m spring-return. Two-stage stem detail (`piston_stem_upper`+`piston_stem_lower`+`stem_transition`) from variant `rec_0611_manual_water_dispenser_pump_var_plunger_stages_two_stage_stem` L275-301 is an optional boolean detail inside this module |
| top_lever | forked_anchor | `rec_0611_manual_water_dispenser_pump_var_actuation_top_lever` (from parent 001) | lever part L338-370, `pump_to_lever` REVOLUTE +Y L373-394 | eligible if compatible | Horizontal lever arm pivoting about +Y axis at housing crown; pressing_pad + pusher rod; REVOLUTE (0..0.45 rad) |
| side_lever | forked_anchor | `rec_0611_manual_water_dispenser_pump_var_actuation_side_lever` (from parent 002) + `rec_picturex_0611__manual_water_dispenser_pump__002` D-handle | handle_hub + handle_loop + piston_rod L280-337, `pump_stroke` REVOLUTE +Y L339-358 | eligible if compatible | Short push-pin + pivot hub (Cylinder, rpy rotates about X) + side-lever arm extending +X (tube_from_spline_points D-handle or single spline); REVOLUTE +Y at housing top (0..0.055 rad or 0..PUMP_TRAVEL) |
| compressible_bellows | forked_anchor | `rec_0611_manual_water_dispenser_pump_var_actuation_compressible_bellows` (from parent 001) | plunger part L243-284 (plunger_button + press_plate + guide_post + guide_seal), `pump_to_plunger` PRISMATIC +Z L289-308 | eligible if compatible | Compressible bellows press: palm button + press plate + guide post + rubber guide seal; PRISMATIC axis (0,0,1) travel ≈0.025m. Requires the pump_body to emit visible bellows body visuals (folded onto the tall_spring_chamber form; on other forms a compressed bellows plate is emitted as body visual to keep support graph valid) |

Notes: 4 candidates (target 3-6). Covers PRISMATIC top-mount (top_plunger + compressible_bellows) and REVOLUTE (top_lever + side_lever) — two distinct joint types with two distinct pose/geometry realizations each.

### Slot D：spout (② spout mechanism — fixed decoration OR REVOLUTE folding child)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|---|
| side_short_elbow | forked_anchor | `rec_picturex_0611__manual_water_dispenser_pump__001` | `blue_spout` `tube_from_spline_points` L212-230, `clear_nozzle` L232-248 | eligible if compatible | Short side outlet: horizontal tube extending +X from housing at z≈mid-height, curving down at the tip; ends in a clear nozzle + rubber outlet opening. Fixed decoration on `pump_body` (no joint) |
| arched_gooseneck | forked_anchor | `rec_0611_manual_water_dispenser_pump_var_spout_arched_gooseneck` (from parent 002) | `flexible_discharge_hose` L208-231 + `arched_gooseneck_coupling` `tube_from_spline_points` L235-261 + `spout_grip_ring_i` L262-277 | eligible if compatible | Tall arched shepherd's-crook gooseneck: hose or spline coupling rising from housing then arcing over and back down. Fixed decoration on `pump_body` (no joint) |
| folding_spout | forked_anchor | `rec_0611_manual_water_dispenser_pump_var_spout_folding_spout` (from parent 001) | `folding_spout` part L215-281, `pump_to_spout` REVOLUTE L283+ | eligible if compatible | Foldable spout child part: pivot collar (Cylinder, rpy about X to give visible hinge barrel) + spout_tube (spline) + spout_nozzle + spout_outlet; child part with own REVOLUTE +Y hinge at housing side-outlet, folds up-and-back to stowed. Adds a SECOND non-fixed joint |

Notes: 3 candidates (target 3-6). folding_spout is the only spout that adds a joint; the sampler must therefore support 1-or-2 non-fixed joints (never 0).

## 槽位图（slot graph）

pattern: `parallel_children` (root `pump_body` with a fixed bottle_interface below, a fixed side spout OR articulated folding_spout, and one actuation child with a single non-fixed joint)

```
pump_body [ROOT, z=0, body_form (③) shell + bellows band decorations + spout visuals if fixed]
  │
  ├── pump_body itself carries bottle_interface visuals (thread_collar OR stepped_socket)
  │       [emitted as pump_body.visual(...) — bottle_interface has NO joint, only fixed features]
  │
  ├── pump_body --[actuation joint: PRISMATIC +Z OR REVOLUTE +Y]--> {plunger | top_lever | side_lever | bellows_plunger}
  │       joint origin: on housing top face (PRISMATIC) or through pivot barrel visual (REVOLUTE)
  │       axis: (0,0,1) for PRISMATIC (top_plunger, compressible_bellows), (0,1,0) for REVOLUTE (top_lever, side_lever)
  │       limits: [-0.025, 0] PRISMATIC (spring-return) OR [0, 0.45] REVOLUTE lever swing
  │
  └── pump_body --[spout joint: FIXED for side_short_elbow/arched_gooseneck, REVOLUTE +Y for folding_spout]--> {spout_visuals_fused | folding_spout_part}
          FIXED case: spout visuals are added directly onto pump_body (Rule 1: not moving → visual on parent) — NO separate part, NO FIXED joint emitted
          folding_spout case: spawns a distinct `folding_spout` part with its own REVOLUTE joint at the housing side-outlet (pivot Y axis), pivot_collar visual straddles both bodies (element-scoped allow_overlap)
```

Interface / mating rules:
- `pump_body` root anchors on ground: base of shell at z=0.
- `bottle_interface` visuals (`mounting_collar` or stacked socket rings + gasket) are `pump_body.visual(...)` — they do not move. NO FIXED joint is emitted for the bottle interface (Rule 1).
- Actuation joint origin: `_ACT_TOP_Z ≈ housing top rim` (source 001 uses ~0.204; source 002 uses ~0.180). Origin is on real housing crown visual, +Z axis for PRISMATIC or the pivot boss visual, +Y for REVOLUTE.
- MatingContract for the actuation joint: the plunger stem sleeves through the housing bore (`piston_stem` inside `main_housing` / `spring_housing`); this is a captured pin, so the plunger→pump_body joint OMITS `mating=` and is grandfathered by the compiler baseline (5★ sources do the same). Element-scoped `allow_overlap(plunger.piston_stem, pump_body.main_housing)` covers the captured-fit inside `run_tests`.
- Folding spout hinge: pivot_collar visual (Cylinder, rpy makes X-axis cylinder that reads as a hinge barrel) is on the spout part and overlaps the pump_body housing side wall; element-scoped `allow_overlap(folding_spout.spout_pivot_collar, pump_body.<side_wall_visual>)` grandfathers the pivot; joint origin lands on the barrel visual.
- rest pose: PRISMATIC q=0 released (plunger up), REVOLUTE q=0 with lever raised (side_lever/top_lever) or spout deployed horizontally (folding_spout).

## 每槽位 Module Emits / Interfaces

### Slot A / body_form: emits `pump_body` shell family
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pump_body` (ROOT, world z=0) | parent 001 L93-99 / parent 002 L61-66 |
| visuals | `main_housing` (lofted taper) or `spring_housing` (lathe), plus bellows/torus bands, plus form-specific decorations | 001 L38-58 + 134-160 / 002 L98-127 + 131-149 |
| internal joints | none (root has no self-joint) | — |
| upstream interface | grounded (base at z=0) | — |
| downstream interfaces | housing top rim (world z ≈ `HOUSING_TOP`; consumed by actuation joint), housing side wall (world z ≈ `SPOUT_Z`; consumed by spout visual or folding_spout hinge), housing base (consumed by bottle_interface visuals) | 001 pump_to_plunger origin (0,0,0.204) L297 / 002 pump_stroke origin (0,0,0.180) L334 / 001 blue_spout z=0.160 L215 |

### Slot B / bottle_interface: emits `pump_body` base-mount features (fused visuals — NOT a separate part)
| emits | 描述 | 来源 |
|---|---|---|
| parts | none (visuals fused into `pump_body`, Rule 1) | — |
| visuals | thread_collar: `mounting_collar` (LatheGeometry shell) + `bottle_gasket` (torus) + optional collar_ribs; stepped_socket: `neck_socket` + `socket_shoulder` + `white_mount_ring` + `blue_lock_ring` + `socket_thread_i` | 002 L70-94 + L168-181 / 001 L104-131 |
| internal joints | none | — |
| upstream interface | shares pump_body base | — |
| downstream interface | none (terminal decoration) | — |

### Slot C / actuation: emits child part + single non-fixed joint
| emits | 描述 | 来源 |
|---|---|---|
| parts | `plunger` (top_plunger, compressible_bellows) or `top_lever` (top_lever) or `plunger` w/ hub+arm (side_lever) — one part total | 001 L260-291 / top_lever variant L338-370 / side_lever variant L280-337 / bellows variant L243-284 |
| visuals | palm button + piston stem (+ optional two-stage stem detail) + return_stop_flange + piston_seal (top_plunger); lever_arm_body + pressing_pad + lever_pusher (top_lever); handle_hub + handle_loop + piston_rod (+ lever_grip) (side_lever); plunger_button + press_plate + guide_post + guide_seal (compressible_bellows) | see sources |
| internal joints | ONE non-fixed joint: `pump_to_plunger` PRISMATIC +Z (top_plunger, bellows) or `pump_to_lever` / `pump_stroke` REVOLUTE +Y (levers) | 001 L292-311 / top_lever L373-394 / side_lever L339-358 / bellows L289-308 |
| upstream interface | mates to pump_body housing top rim (world z=HOUSING_TOP); captured stem inside main_housing bore (`allow_overlap(piston_stem↔main_housing)`) | 001 origin (0,0,0.204) L297; source uses OMIT mating (captured pin) |
| downstream interface | none (terminal) | — |

### Slot D / spout: emits pump_body visuals (fixed cases) OR a child part + REVOLUTE joint (folding case)
| emits | 描述 | 来源 |
|---|---|---|
| parts | side_short_elbow: none; arched_gooseneck: none; folding_spout: `folding_spout` part | folding variant L215-281 |
| visuals | side_short_elbow: `blue_spout` tube + `clear_nozzle` tube + `outlet_opening` (all fused into pump_body); arched_gooseneck: `spout_coupling` gooseneck spline + `spout_grip_ring_i` toruses + tip (fused into pump_body); folding_spout: `spout_pivot_collar` + `spout_tube` + `spout_nozzle` + `spout_outlet` on the `folding_spout` part | 001 L212-258 / arched variant L235-278 / folding variant L224-281 |
| internal joints | side_short/arched: NONE (Rule 1 — no motion, no part, no FIXED joint); folding: `pump_to_spout` REVOLUTE +Y at housing side outlet, hinge origin on `spout_pivot_collar` visual (captured pin — omit mating) | folding variant L283+ |
| upstream interface | side outlet on housing side wall at world z ≈ `SPOUT_Z` | — |
| downstream interface | none (terminal) | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | tall_spring_chamber / slim_stepped_column / squat_round_body | tall_spring_chamber | choice | deterministic procedural sampler | Slot A |
| bottle_interface | enum | thread_collar / stepped_socket | thread_collar | choice | deterministic procedural sampler | Slot B |
| actuation | enum | top_plunger / top_lever / side_lever / compressible_bellows | top_plunger | choice | deterministic procedural sampler | Slot C |
| spout | enum | side_short_elbow / arched_gooseneck / folding_spout | side_short_elbow | choice | deterministic procedural sampler | Slot D |
| palette_style | enum | blue_white / ivory_dark / cobalt_clinical / matte_charcoal / sage_frost | blue_white | palette | palette-only (does NOT count toward slot_choices); `rng.choice(PALETTE_STYLES)` per seed | 5★ material tables |
| plunger_stages | enum | single / two_stage | single | conditional | Only applied when `actuation == top_plunger` (adds `piston_stem_upper` + `piston_stem_lower` + `stem_transition` visuals); otherwise coerced to `single` | plunger_stages_two_stage_stem variant L275-301 |
| body_height_scale | float | [0.88, 1.15] | 1.0 | independent | Scales housing height H → also raises HOUSING_TOP and SPOUT_Z proportionally in resolve | 001 total_height≈0.20 / 002 ≈0.185 |
| body_radius_scale | float | [0.90, 1.12] | 1.0 | independent | Scales housing radius family (main_housing outer, spring_chamber wrap, torus band radii) | 001 R≈0.055 / 002 R≈0.018 |
| press_travel_scale | float | [0.80, 1.20] | 1.0 | independent | Scales PRISMATIC travel or REVOLUTE angle upper bound; clamped in [0.010, 0.040] m / [0.15, 0.55] rad respectively | 001 travel=-0.022 / lever upper=0.45 |
| spout_reach_scale | float | [0.85, 1.15] | 1.0 | conditional | Scales side_short_elbow / arched_gooseneck / folding_spout spline reach; upper depends on chosen spout (folding_spout narrower) | 001 spout max_x≈0.16 / arched max_x≈0.27 |
| (—) | constraint | — | — | inequality | Actuation joint origin z >= body top rim + 0.001 (avoid intersecting housing top); `piston_stem_length ≤ HOUSING_TOP − 0.010` (captured deep in housing) — violation triggers resolve-time clamp | interface / clearance |
| (—) | constraint | — | — | inequality | Spout side-outlet z between `SPOUT_MIN_Z` and `HOUSING_TOP − 0.020` so spout does not clash with actuation top-mount hardware | 001 blue_spout z=0.160 vs housing_top=0.204 |

All `equation`/`inequality`/`conditional` constraints are resolved inside `resolve_config`; `slot_choices_for_seed` only exports the 4 discrete slot picks (palette_style is NOT a slot choice).

## 7.5 编译预算 / compile budget

**Budget: 15–25 s per seed** (justification: primary primitives are LatheGeometry (48 segments), 3–6 TorusGeometry (18×56 segments), 2–3 tube_from_spline_points (10–20 samples×20 radial), 1 lofted CadQuery main_housing (28 segments). No booleans on the plunger. Tessellation: `LatheGeometry` at 48 segments (main housing) / 32 (waisted body cap); TorusGeometry (bands, gaskets) at radial=14–18, tubular=36–56; `tube_from_spline_points` radial=18–20, samples_per_segment=12–18. Spring helix (metal helical) segments capped at 90 total.)

Any seed exceeding budget: drop tessellation first (segments -25%) then simplify spring helix / gooseneck to fewer sample points. sweep-pipeline compile-timeout set to 120s (5–6× budget) as a hang-guard.

## 8. Multiplicity / Copy Logic

- 无复制数量逻辑 / no template-level multiplicity axis. Core structure is fixed named slots (pump_body root + at most one actuation child + at most one folding_spout child). Small module-local repetition constants (`bellows_rib_i` count=6, `socket_thread_i` count=4, `collar_rib_i` count=16, `spout_grip_ring_i` count=3) are hard-coded per module; N is NOT exposed as a sampling parameter.

## 8.5 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 2 skeleton variants: {pump_body, plunger_or_lever} (1 non-fixed joint) — top_plunger/top_lever/side_lever/compressible_bellows OR {pump_body, plunger_or_lever, folding_spout} (2 non-fixed joints) — folding_spout spout. Selected via (Slot C × Slot D). source_type=forked_anchor (all 4 actuation variants + folding_spout variant) |
| └ multiplicity | 同构件 ×N | 无 | no template-level multiplicity axis; §8 declares this explicitly |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | Actuation joint: PRISMATIC +Z (top_plunger, compressible_bellows) / REVOLUTE +Y (top_lever, side_lever). Optional folding_spout joint: REVOLUTE +Y. source_type=forked_anchor (each type has a real 5★ variant); each type appears in slot_choices and sweep |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型（非缩放/换色） | 有 | Slot A body_form registered as ③ Primary Form Family: tall_spring_chamber (Volumetric Envelope Form — lofted CadQuery hollow taper w/ transparent spring chamber + bellows ribs), slim_stepped_column (Volumetric Envelope Form — slim lathe shell + torus bands), squat_round_body (Volumetric Envelope Form — wider/shorter lathe barrel; world_knowledge_extrapolation). 3 candidates, ≥2. Registered in `slot_choices` under key `body_form` |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | Bottle-interface thread rings (4 `socket_thread_i` on stepped_socket) / collar knurl ribs (16 on thread_collar). Bellows_rib_i (6 on tall_spring_chamber). Spout_grip_ring_i (3 on arched_gooseneck). All host-conformal (torus rings share their host's neck radius, socket thread rings straddle collar wall). source_type=record_only (all counts fixed) |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | body_height_scale [0.88, 1.15], body_radius_scale [0.90, 1.12], press_travel_scale [0.80, 1.20], spout_reach_scale [0.85, 1.15]. Non-continuous joints: **actuation** — PRISMATIC axis (0,0,1) travel [-0.025, 0] closed→open (spring-return released is q=0); REVOLUTE +Y lever angle [0, 0.45]; folding_spout REVOLUTE +Y [0, π/2]. motion_test_plan: `ctx.fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` in `run_tests`, plus targeted `ctx.pose(...)` for each mechanism proving direction of travel (plunger pressed z drops, lever tip x displaces, folding_spout tip rises). qc_samples: PRISMATIC {0, -travel/2, -travel}; REVOLUTE {0, upper/2, upper} |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | 5 palette_style colorways (target ≥4-6): blue_white (parent 001), ivory_dark (parent 002), cobalt_clinical (medical/office), matte_charcoal (office soft-touch), sage_frost (frosted-mint modern). Material classes covered: **plastic** (blue_white, ivory_dark, sage_frost — includes clear/frosted variants), **painted metal** (cobalt_clinical), **soft-touch matte** (matte_charcoal). ≥3 of 5 (60%) span multiple material classes ✓. Each seed picks one via `rng.choice(PALETTE_STYLES)` |

## 采样与覆盖审计

Total slot_choices combinations: body_form(3) × bottle_interface(2) × actuation(4) × spout(3) = **72** discrete tuples (palette_style is palette-only, not counted; plunger_stages is a conditional detail, not counted).

Rationale: 72 exceeds the recommended ≥300 threshold's lower end but is realistic given the source pool size (10 records × truly-diff axes yields ~4 primary axes with 2–4 candidates each). All 4 axes are ≥2, the two identity-critical axes (③ body_form, ② actuation) have ≥3 and ≥4 candidates respectively. Report-only; not gated.

seed_domain_policy: `procedural_first` — `config_from_seed(seed)` uses `random.Random(seed)` for every ordinary seed including seed=0. No regression overrides in the initial version.

Procedural Sampling / Sweep Plan: `rng.choice` picks each of the 4 slot enums independently, plus `rng.choice(PALETTE_STYLES)`, plus `rng.uniform` on each continuous scale (clamped in resolve). No compatibility gating is needed for the initial pass: all 72 tuples are geometrically legal because (a) all 3 body_form candidates share the same collar/plunger interface (housing top rim + side outlet), (b) both bottle_interface candidates emit only fused visuals on the pump_body base (no joint), (c) all 4 actuations mount at the same housing top rim origin (choice of PRISMATIC +Z vs REVOLUTE +Y is a joint-type toggle at the same location), (d) all 3 spouts mount at the same side-outlet location and either fuse into pump_body or spawn one folding_spout child. `plunger_stages` is coerced to `single` when `actuation ≠ top_plunger`.

Topology target: 1000-seed slot-choice tuple coverage estimated ≥60 distinct (of 72 possible; a few extremes may go unrealized in 36 seeds and are covered by the corner stage). Report-only.

Controlled local parameterization: 4 continuous scales (body_height_scale, body_radius_scale, press_travel_scale, spout_reach_scale) — all `independent` with clamps; no cross-part `equation` needed at first pass because the pump_body's housing top rim (=actuation joint origin) is derived from body_height_scale AND the plunger stem length re-derives from `HOUSING_TOP` inside `resolve_config`. Interface `inequality` constraints (actuation origin above housing rim, spout z between min/max, piston stem captured deep) resolved inside `resolve_config`.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 4 `rng.choice` slot picks + `rng.choice` palette + 4 `rng.uniform` scales; all indep | `slot_choices_for_seed` returns 4 slot pairs matching build |
| compatibility matrix | all 72 tuples legal; `plunger_stages` coerced to `single` unless actuation=top_plunger | no floating, mid-travel overlap, spout clash with actuation, folding_spout hinge origin off-barrel |
| controlled local variation | 4 clamped scales in resolve; HOUSING_TOP and SPOUT_Z derived from body_height_scale | proportions vary without breaking bottle_interface footprint, actuation origin, spout mount, or category identity |
| regression overrides | none | — |
| random sweep | seeds 0-15 fast, 16-35 final, plus corner stage | contract failures; axis_realization for body_form, bottle_interface, actuation, spout |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 3 | yes | yes | ③ Primary Form Family slot |
| bottle_interface | 2 | yes | no | source pool constraint (see Slot B note) |
| actuation | 4 | yes | yes | ② identity mechanism slot |
| spout | 3 | yes | yes | folding_spout adds a joint |

## Validator

- `slot_choices_for_seed(seed)` returns `((body_form, X), (bottle_interface, Y), (actuation, Z), (spout, W))` — exactly 4 pairs, all in implemented module names
- `config_from_seed(seed)` uses deterministic procedural sampling for all seeds
- `resolve_config` clamps all 4 scales, coerces `plunger_stages` to `single` when `actuation != top_plunger`, derives HOUSING_TOP + SPOUT_Z + piston stem length from `body_height_scale`, and enforces the two `inequality` constraints (origin above rim, stem captured)
- Compatibility matrix: all 72 tuples legal; no hard gate-outs
- Key joints:
  - `actuation=top_plunger` / `compressible_bellows`: `pump_to_plunger` PRISMATIC axis (0,0,1) with `motion_limits` bounded by `press_travel_scale` clamp
  - `actuation=top_lever`: `pump_to_lever` REVOLUTE axis (0,1,0) with upper bound 0.15–0.55 rad
  - `actuation=side_lever`: `pump_stroke` REVOLUTE axis (0,1,0) with lower=0, upper bounded
  - `spout=folding_spout`: `pump_to_spout` REVOLUTE axis (0,1,0) present as second non-fixed joint; otherwise NO extra joint
- Captured-fit `allow_overlap` element-scoped: `plunger.piston_stem`↔`pump_body.main_housing` (top_plunger, bellows: guide_post↔main_housing); `top_lever.lever_pusher`↔`pump_body.main_housing` (top_lever); `plunger.piston_rod`↔`pump_body.<housing>` + `plunger.handle_hub`↔`pump_body.<housing>` (side_lever); `folding_spout.spout_pivot_collar`↔`pump_body.<side_wall>` (folding); bottle_interface visuals fused into pump_body (no cross-part overlap)
- Motion test coverage (Rule 5): `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` + targeted `ctx.pose({joint: value}): ctx.check(...)` per non-fixed joint proving intended displacement direction
- `palette_style` is palette (not a slot_choice); each build's rng.choice picks one of 5 colorways and applies its per-slot rgba

## Reject cases

- Downgrading `LatheGeometry.from_shell_profiles` or `mesh_from_cadquery(_main_housing())` to a naked `Cylinder` / `Box` placeholder — Rule 3 violation (all 5★ sources use sculpted shells / lofted hollow tapers)
- Emitting a FIXED articulation to attach the bottle_interface or a fixed spout to `pump_body` — Rule 1 violation (fold into `pump_body.visual(...)`)
- Skipping the `MatingContract` or `allow_overlap` grandfather on the captured plunger stem — mating_gap FAIL (5★ sources omit `mating=` and rely on element-scoped overlap allowances)
- Placing the actuation joint origin above the housing crown by more than 15mm from real hardware — `fail_if_articulation_origin_far_from_geometry` FAIL
- Forgetting `fail_if_parts_overlap_in_sampled_poses` when a non-fixed joint exists — Rule 5 gate (motion_test_audit warning)
- `plunger_stages=two_stage` applied to a non-top_plunger actuation — visuals hover in space; must be coerced to `single` inside `resolve_config`
- Emitting `folding_spout` part with `spout=side_short_elbow` or `arched_gooseneck` — dead disconnected part; only emit when `spout==folding_spout`

## 与相邻类别的边界

- 不该混入：**container_pump (soap/lotion pump-bottle)** — reason: container_pump is mounted **on** a soap/lotion bottle that IS the root; the bottle is the geometry. In this class the water bottle is inverted context and NOT modeled — root is the pump body itself, and the interface below faces up into an inverted bottle. Different rest-orientation, different root, different scale (0.20m tall pump vs 0.30m tall filled bottle).
- 不该混入：**Water_dispenser (tap-only countertop dispenser)** — reason: those categories are a tank + tap (no hand-actuated pump mechanism); no PRISMATIC plunger or REVOLUTE lever. If the dominant motion is a valve knob turning, it's a `Water_dispenser`.
- 不该混入：**air_pump / bicycle_pump** — reason: no bottle interface at the bottom; open-ended shaft with a long stroke on the ground.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT. 10 5★ records fully read (2 parents + 8 fork variants). 4 slots: body_form(3, ③ Primary Form Family) × bottle_interface(2) × actuation(4, ② identity mechanism) × spout(3, one adds joint) = 72 combos. palette_style 5 colorways (3+ material classes). plunger_stages folded as conditional detail inside top_plunger (variant `plunger_stages_two_stage_stem` covers this). Rule 1: bottle_interface and non-folding spouts are pump_body visuals (no FIXED joint). Rule 3: preserved LatheGeometry / mesh_from_cadquery / tube_from_spline_points primitive families across all body_form candidates. Rule 5: `fail_if_parts_overlap_in_sampled_poses` + targeted pose checks per mechanism. Escalation triggers: 3-sweep-unchanged cluster → narrow config_from_seed exclusion list. |

## 模板实现备注

- Shared helpers: `_lathe_shell(body_form, scales) -> MeshGeometry` dispatches to a per-form lathe/CadQuery profile; `_bellows_bands(...)`, `_torus_bands(...)`, `_thread_ring_stack(...)`, `_spout_spline(...)`.
- `_HOUSING_TOP_Z` and `_SPOUT_Z` are derived once in `resolve_config` from `body_form` + `body_height_scale`; every mechanism module reads these from `ResolvedConfig`.
- Captured-fit overlaps declared in `run_tests` (not on the joint) so the sampled-pose collision gate does not fail on the deep-stem or hinge-barrel overlap.
- `folding_spout` part emits its own `spout_pivot_collar` (Cylinder rpy makes X-axis barrel that visually straddles the housing side outlet), and the joint origin lands on this collar; `allow_overlap(folding_spout.spout_pivot_collar, pump_body.main_housing, reason="hinge barrel captured")` grandfathers the pivot.
- palette_style: 5 palettes each specify (housing_light, housing_dark, accent, spring/spout_clear, gasket_rubber) rgba; alpha<1 for `clear_blue_plastic` (blue_white), `frosted` (sage_frost) shell visuals only. Materials named `mwdp_<slot>_<palette>` to keep the material set inspectable.

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | tall_spring_chamber | rec_picturex_0611__manual_water_dispenser_pump__001 | `_main_housing` L38-58 / spring_chamber + bellows_ribs L134-160 / return_spring L162-186 | tall transparent spring chamber body_form baseline |
| S2 | A | slim_stepped_column | rec_picturex_0611__manual_water_dispenser_pump__002 | `housing_shell` L98-127 / torus bands L131-149 | slim stepped lathe housing body_form |
| S3 | A | squat_round_body | world_knowledge_extrapolation (anchors S1, S2) | procedurally generated `LatheGeometry.from_shell_profiles` | wider/shorter barrel form variant (Volumetric Envelope Form family, same primitive as S2) |
| S4 | B | thread_collar | rec_0611_manual_water_dispenser_pump_var_bottle_interface_thread_collar (from parent 002) | mounting_collar L91-94 / bottle_gasket L168-181 | externally-threaded ivory collar with base gasket |
| S5 | B | stepped_socket | rec_picturex_0611__manual_water_dispenser_pump__001 | neck_socket + socket_shoulder + white_mount_ring + blue_lock_ring + socket_thread_i L104-131 | stacked ring stepped socket with locking ring |
| S6 | C | top_plunger | rec_picturex_0611__manual_water_dispenser_pump__001 | plunger part L260-291 / pump_to_plunger PRISMATIC +Z L292-311 | top palm-button plunger PRISMATIC +Z |
| S6b | C.detail | plunger_stages=two_stage | rec_0611_manual_water_dispenser_pump_var_plunger_stages_two_stage_stem | piston_stem_upper + piston_stem_lower + stem_transition L275-301 | two-stage stem detail on top_plunger |
| S7 | C | top_lever | rec_0611_manual_water_dispenser_pump_var_actuation_top_lever (from parent 001) | lever part L338-370 / pump_to_lever REVOLUTE +Y L373-394 | top pivoting lever REVOLUTE +Y |
| S8 | C | side_lever | rec_0611_manual_water_dispenser_pump_var_actuation_side_lever (from parent 002) + parent 002 D-handle | handle_hub + handle_loop + piston_rod L280-337 / pump_stroke REVOLUTE +Y L339-358 | side lever w/ pivot hub REVOLUTE +Y |
| S9 | C | compressible_bellows | rec_0611_manual_water_dispenser_pump_var_actuation_compressible_bellows (from parent 001) | plunger part L243-284 / pump_to_plunger PRISMATIC +Z L289-308 | compressible bellows PRISMATIC +Z |
| S10 | D | side_short_elbow | rec_picturex_0611__manual_water_dispenser_pump__001 | blue_spout + clear_nozzle + outlet_opening L212-258 | short side outlet (fixed decoration) |
| S11 | D | arched_gooseneck | rec_0611_manual_water_dispenser_pump_var_spout_arched_gooseneck (from parent 002) | arched_gooseneck_coupling + spout_grip_ring_i + tip L235-278 | tall arched gooseneck (fixed decoration) |
| S12 | D | folding_spout | rec_0611_manual_water_dispenser_pump_var_spout_folding_spout (from parent 001) | folding_spout part L215-281 / pump_to_spout REVOLUTE L283+ | foldable child part w/ REVOLUTE hinge |
