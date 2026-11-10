# rabbit_hutch — Modular Spec (specs_modular_v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `rabbit_hutch` |
| template path | `agent/templates/rabbit_hutch.py` |
| test path (optional) | `tests/agent/test_rabbit_hutch_template.py` (not authored; sweep is authority) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children + multiplicity) |

`pattern` = mixed: every access member (hinged doors, top-hinge roof lid, drop ramp, slide-out
tray, rolling casters, latch hasps, guillotine pop-hole) parents to a single `hutch_frame` root
(parallel_children — no serial slot chain), plus a compartment-door-grid multiplicity axis
(`n_tiers`) for the enclosed grid-cabinet body form.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this category (2 origin anchors A/B + 5 forks/probe) |
| source_index_policy | only adopted module sources are indexed below |

Two origin families + five variant forks (all read in full):
- **Origin A** `rec_pet_animal_related__rabbit_hutch__001…` — compact **wheeled two-compartment
  hutch+run**: `hutch_frame` root carrying every fixed visual; children `upper_door`(acrylic
  REVOLUTE) / `lower_door`(mesh REVOLUTE) / `run_door`(large mesh REVOLUTE) / `roof_lid`(top-hinge
  REVOLUTE) / `front_ramp`(drop REVOLUTE) / `floor_tray`(PRISMATIC) / 4× `caster_wheel_i`
  (CONTINUOUS). Helpers `_front_mesh`/`_side_mesh` (loop wire grids), `_door_frame`.
- **Origin B** `rec_pet_animal_related__rabbit_hutch__002…` — tall natural-pine **3×3 grid cabinet
  on legs**: `hutch_frame` root + loop over `row_bottoms` × `columns`(solid / mesh_narrow /
  mesh_wide) → `{kind}_door_{row}`(REVOLUTE) each with a `{name}_latch`(REVOLUTE hasp child);
  `cleaning_tray`(PRISMATIC); sloped overhang roof. Helpers `_solid_door_geometry`,
  `_mesh_door_geometry`, `_add_hinge_knuckles`, `_add_latch_mount`, `_add_latch_bar`.
- `rec_rabbit_hutch_var_skeleton_aframe` (fork of A) — **triangular A-frame ark**: ridge beam +
  pitched slope frames + gables, enclosed nest box + sloped-face wire run, `run_door`(slope
  REVOLUTE), `front_ramp`(drop REVOLUTE), `floor_tray`(PRISMATIC). `_slope_mesh`, `_gable_frame`,
  `_gable_planks`.
- `rec_rabbit_hutch_var_mechanism_slide_door` (fork of A) — **guillotine pop-hole**: divider mesh
  split around a pop opening + trim frame + two U-channel guide rails + bottom stop + `pop_hole_door`
  vertical **PRISMATIC +Z** slide panel.
- `rec_rabbit_hutch_var_n2` / `rec_rabbit_hutch_var_n1` (forks of B) — `n_tiers`=2 / 1 drives
  `row_bottoms`/rails/floors/roof z-lines and the door-grid loop count (6 / 3 doors).
- `rec_rabbit_hutch_var_probe_cabinet_run` (compatibility probe, from B) — enclosed cabinet + an
  attached open post-and-rail wire run with its own run door + pop-hole ramp (informs the
  drop-ramp/pop-hole access members; not a separate body candidate).

## 核心身份

A **rabbit hutch** is a raised outdoor housing for pet rabbits: one or more enclosed
sleeping/shelter compartments with wire-mesh ventilated fronts, at least one human-access door or
lid that opens, raised off the ground on legs or casters, and (when present) a slide-out cleaning
tray and/or an attached open wire run. The mature domain spans the compact wheeled
two-compartment hutch+run (A), the tall enclosed multi-tier grid cabinet on legs (B), and the
triangular A-frame ark (fork). Every seed keeps an enclosed compartment, wire-mesh ventilation, at
least one opening access member, a raised stance, and a slide-out tray.

Must NOT drift into: dog kennel/crate, chicken coop / hen house, bird aviary, guinea-pig floor
cage without shelter, garden storage cabinet, greenhouse/cold frame (see §11).

## 槽位 + 候选模块表

### Slot A：body_form （③ 主体形态家族 + ① 骨架 — 主多样性槽）
Builds the `hutch_frame` root (posts/legs, walls, wire-mesh panels, roof) plus its inherent
compartment access doors + slide-out tray. Registered into `slot_choices` (form-dominated 小类).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `wheeled_hutch_run` | origin_anchor | origin A `hutch_frame` | L95-L286 (posts/rails, left enclosed compartment solid walls, right open wire run, roof lid, tray, casters) | eligible if compatible | box post-and-rail frame; enclosed left box (stacked `upper_door` acrylic + `lower_door` mesh REVOLUTE) + open right run (`run_door` REVOLUTE) + top-hinge `roof_lid`; **Volumetric Envelope Form** (rectangular box) |
| `grid_cabinet` | origin_anchor | origin B `hutch_frame` grid | L302-L524 (legs, front stile/rail grid, compartment floors, plank walls, sloped roof, `n_tiers`×3 latched doors, tray) | eligible if compatible | tall post-and-rail cabinet; uniform `n_tiers`×3 `{kind}_door_{row}` REVOLUTE grid each with a `{name}_latch` REVOLUTE hasp; **Volumetric Envelope Form** (tall box) — distinct ① part-tree from wheeled (uniform latched grid vs stacked-door box+run) |
| `aframe_ark` | forked_anchor | rec_rabbit_hutch_var_skeleton_aframe | L167-L457 (ridge beam, pitched slope frames, gables, nest box, sloped wire run, `run_door`, ramp, tray) | eligible if compatible | triangular A-frame: ridge + two pitched slope planes + gables; enclosed apex nest box + sloped-face wire run + slope `run_door` REVOLUTE; **Macro Surface Construction** (triangular prism envelope replaces the box read) |

Six-axis note: this is the required **③ Primary Form Family slot registered into `slot_choices`**.
Two box skeletons that are genuinely distinct ① part-trees (stacked-door box+run vs uniform latched
grid) + one distinct ③ Volumetric→Macro-Surface envelope (A-frame). ≥2 with the box→A-frame ③ jump
satisfies the form-dominated requirement; the wheeled/grid split is an honest ① part-tree
distinction (different door topology, run vs no run), not a re-skin.

### Slot B：mobility （① 支撑结构 + ② 关节 — 基座）
foot/base structure below the frame legs.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / joint |
|---|---|---|---|---|---|
| `swivel_casters` | origin_anchor | origin A `caster_*` | L158-L168, L273-L286 (4 caster plates/forks fixed + `caster_wheel_i` CONTINUOUS) | eligible if compatible | 4 corner caster plates+forks (frame `.visual`) + 4 `caster_wheel_i` CONTINUOUS wheels; frame legs stop at ~0.11 clearance |
| `fixed_legs` | origin_anchor | origin B `leg_ix_iy` | L313-L316 (4 load-bearing legs to ground) | eligible if compatible | frame legs continue to the ground; NO articulation; standard rabbit-hutch stance |

### Slot C：front_access （② 关节类型 — 附加通行/进出机构）
One extra articulated access member beyond the body form's own doors, mounted on the front /
divider of the primary enclosed compartment.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / joint |
|---|---|---|---|---|---|
| `drop_ramp` | origin_anchor | origin A `front_ramp` | L237-L257 (drop-down cleated ramp board REVOLUTE about lateral X) | eligible: all forms | `front_ramp` REVOLUTE about lateral X at the compartment front-bottom; drops to the ground, folds up |
| `guillotine_pop_hole` | forked_anchor | rec_rabbit_hutch_var_mechanism_slide_door | L162-L184, L320-L344 (U-channel guide rails + `pop_hole_door` vertical PRISMATIC +Z slide) | eligible: wheeled_hutch_run / aframe_ark (need a compartment↔run divider) | pop opening in the divider + two U-channel guides + bottom stop (frame `.visual`) + `pop_hole_door` PRISMATIC +Z clear slide panel |

Compatibility (§9): `guillotine_pop_hole` needs a compartment↔run divider, so it is gated to
`wheeled_hutch_run` / `aframe_ark`; `grid_cabinet` (fully enclosed, no run) is restricted to
`drop_ramp`. Both candidates appear across the sweep.

Every candidate in every slot is structurally distinct (part tree / joint topology). Door infill
(solid plank / wire mesh / clear acrylic), plank-grain, felt cap, palette are ④/⑥ audit-only, not
candidates.

## 槽位图（slot graph）

pattern: mixed (parallel_children + multiplicity)

```
                       hutch_frame (root: posts/legs, walls, wire-mesh panels, roof, tray runners, hinge receivers)
   ├─[REVOLUTE vert-Z @front-face receiver]────> {compartment doors}         (body_form: A upper/lower/run ; B n_tiers×3 {kind}_door_{row})
   │        └─[REVOLUTE +Y @door pivot plate]──> {name}_latch                 (grid_cabinet only, per door)
   ├─[REVOLUTE lateral-X @run rear ridge]──────> roof_lid                     (wheeled_hutch_run only)
   ├─[PRISMATIC −Y @tray rails]────────────────> floor_tray / cleaning_tray   (all forms, always)
   ├─[CONTINUOUS +X @corner axle]──────────────> caster_wheel_i (×4)          (mobility=swivel_casters)
   ├─[REVOLUTE lateral-X @front-bottom hinge]──> front_ramp                   (front_access=drop_ramp)
   └─[PRISMATIC +Z @divider guides]────────────> pop_hole_door                (front_access=guillotine_pop_hole)
```

- Slot order (resolve): mobility sets `leg_bottom_z` (0.0 legs / ~0.11 casters) → body_form reads
  it to draw legs and emits doors+tray+roof_lid → front_access adds the ramp/pop child on the
  form's front/divider. All children parent to `hutch_frame` (parallel).
- Cross-slot connection points: every joint origin sits on real frame hardware — front-face hinge
  receivers (doors), the run rear ridge (roof lid), tray rails, corner caster forks, the
  front-bottom ramp receiver, the divider guide rails. Vertical door hinge axes thread through the
  horizontal front rails (rotational-axis-touches-hardware, source-proven).
- Every non-FIXED joint is a captured hinge/pin/rail: `MatingContract` cannot express interleaved
  hinge knuckles / captured latch pins / a panel in guide channels, so joints are **grandfathered**
  (omit `mating=`) and kept honest with element-scoped `allow_overlap` + `expect_contact` mirroring
  each source's `run_tests`.
- Mutual exclusion / gating: `guillotine_pop_hole` gated off `grid_cabinet`; `roof_lid` only on
  `wheeled_hutch_run`; latch hasps only on `grid_cabinet` doors; `caster_wheel_i` only when
  mobility=swivel_casters; `n_tiers`>1 only for `grid_cabinet`.

## 每槽位 Module Emits / Interfaces

### Slot A / body_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hutch_frame` root (all fixed structure as `.visual`) + door children (A: `upper_door`/`lower_door`/`run_door` + `roof_lid`; B: `{kind}_door_{row}`(+`{name}_latch`); aframe: `run_door`) + `floor_tray`/`cleaning_tray` | A L95-286 / B L302-524 / aframe L167-457 |
| internal joints | door REVOLUTE (vertical Z, open −Y); grid latch REVOLUTE (+Y); roof_lid REVOLUTE (lateral −X); tray PRISMATIC (−Y) | source articulations |
| upstream interface | reads `leg_bottom_z` from mobility; exposes `base_corners()` + `ramp_mount()` / `pop_mount()` for the other slots | — |
| downstream interface | front-face hinge receivers + tray rails (informational) | — |

### Slot B / mobility
| emits | 描述 | 来源 |
|---|---|---|
| parts | caster plates/forks as frame `.visual` + 4 `caster_wheel_i` parts (casters) — nothing extra for legs | A L158-286 / B L313-316 |
| internal joints | 4× caster CONTINUOUS +X (casters) / none (legs) | A L278-286 |
| upstream interface | sets `leg_bottom_z` on `hutch_frame` | — |
| downstream interface | corner base line consumed by body_form legs | — |

### Slot C / front_access
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_ramp` (drop_ramp) / `pop_hole_door` + guide rails+trim frame `.visual` (guillotine) | A L237-257 / slide_door L162-344 |
| internal joints | ramp REVOLUTE lateral −X / pop PRISMATIC +Z | source |
| upstream interface | parents to `hutch_frame`; origin on the front-bottom ramp receiver / divider guides | — |
| downstream interface | none (leaf) | — |

不动细节（plank seams, wood grain, face screws, felt/edge caps, hinge leaves, latch plates, ramp
cleats, pop-hole trim）都是宿主 part 的 `.visual(...)`，不是 FIXED-jointed part（Rule 1）。本模板
**没有任何 FIXED articulation**——每个 child 都是真正会动的关节。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_form` | enum | 3 modules (Slot A) | wheeled_hutch_run | choice | procedural sampler | Slot A table |
| `mobility` | enum | 2 modules (Slot B) | swivel_casters | choice | procedural sampler | Slot B table |
| `front_access` | enum | 2 modules (Slot C) | drop_ramp | conditional | sampled from form's allowed set (guillotine gated off grid) | Slot C table |
| `n_tiers` | int (mult.) | {1,2,3} | 3 | conditional | grid_cabinet only, else 1; weighted N3≥N2>N1 | B/n2/n1 |
| `palette` | enum | 4 colorways (see §8.5 ⑥) | white_grey | choice | rng.choice(PALETTES) | origins + forks |
| `leg_bottom_z` | float | derived {legs 0.0, casters 0.11} | 0.11 | equation | `= f(mobility)` | A/B |
| `door_swing` | float | [1.20, 1.50] rad | 1.35 | independent | REVOLUTE door upper limit; uniform then clamp | ⑤ door travel |
| `tray_travel` | float | [0.28, 0.34] m | 0.32 | independent | PRISMATIC tray upper limit; uniform then clamp | ⑤ tray travel |
| `roof_overhang_scale` | float | [0.90, 1.15] | 1.0 | independent | scales roof overhang/fascia box extents only (free space, no interface) | ⑤ proportion |
| (—) | constraint | — | — | conditional | front_access allowed-set resolved from form before use; n_tiers pinned to 1 off grid | §9 |

Body x/y footprint dims are **fixed standardized per form** (Contract 2c: standardized-hardware
comment) so the delicate door/receiver/latch/mesh contacts stay proven; proportion diversity is
carried by the discrete `n_tiers` (large height/part-count swing), the mobility stance
(`leg_bottom_z`), and the travel/overhang scales. All `equation`/`conditional` solved in
`resolve_config`; the builder never fails on ranges.

### 7.5 编译预算 / compile budget（必填）
自报预算 **≤18 s/seed**（典型 6–14 s）。依据：库内实测参考典型模板 5–20 s；本类主体是 `Box`+少量
`Cylinder` 图元（无 boolean/lathe/mesh 英雄面；A-frame gable 用 box planks 代替原 fork 的 cadquery cut
以省编译）。分档 tessellation：casters/hinge 小圆特征无需高精度（Cylinder 默认段数）；wire-mesh 用循环
`_box` 细线，列数 `= width/0.095`（≤~30 线/面）；grid_cabinet `n_tiers=3` 上界约 9 门+9 闩+1 盘+4 caster
+1 access ≈ 24 关节（对齐 probe 记录 22 关节的实测）。sweep `--compile-timeout 120` 作看门狗（≈3–7×
上限）。超预算先降 mesh 线密度再迭代。

## Multiplicity / Copy Logic

**Axis 1 — `n_tiers` (compartment-door grid rows), source origin B / `rec_rabbit_hutch_var_n2` /
`rec_rabbit_hutch_var_n1`.**
- `count_param` = `n_tiers`; product domain [1,3] (n=4+ excluded — beyond realistic rabbit-hutch
  height); sampling domain weighted N3≥N2>N1 (tall grid is the canonical B image).
- copied object = one compartment row = 3 columns `{kind}_door_{row}` (REVOLUTE hinge) + per-door
  `{name}_latch` (REVOLUTE hasp child); column pattern fixed (solid / mesh_narrow / mesh_wide).
- placement: vertical stack, `row_bottoms[i] = body_bottom + 0.085 + i·tier_spacing`; front rails
  (`n_tiers`+1), compartment floors, wall + roof z-lines all regenerated from `n_tiers`; legs +
  body_top track the tier count.
- joint policy: each copied door keeps its own `frame_to_{name}` REVOLUTE + `{name}_to_latch`
  REVOLUTE; loop-emitted, stable indexed names — no hand-written rows.
- gating: `n_tiers`>1 only for `grid_cabinet`; other forms pin `n_tiers=1` (unused).

Secondary copy (record_only, NOT a template N axis): 4× casters (per-wheel CONTINUOUS, driven by
mobility=swivel_casters, fixed count 4); wire-mesh wires via `_front_mesh`/`_side_mesh`/`_slope_mesh`
loops (decorative infill, count derived from panel size, not a swept N).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | body_form changes the part-joint graph: wheeled (stacked box doors + run door + roof lid) vs grid (uniform n_tiers×3 latched doors) vs aframe (single slope run door); mobility ±4 caster children; front_access ±ramp/±pop child. source-backed: origin A / origin B / aframe fork / slide_door fork. |
| └ multiplicity | 同构件 ×N | 有 | `n_tiers`∈{1,2,3} for grid_cabinet drives 3/6/9 doors+latches (source B / n2 / n1). Weighted N3≥N2>N1. See §8. |
| ② 关节类型 | 边换 type/轴 | 有 | REVOLUTE vertical-Z (compartment doors), REVOLUTE lateral-X (roof lid, drop ramp), REVOLUTE +Y (latch hasp), PRISMATIC −Y (tray), PRISMATIC +Z (guillotine pop-hole), CONTINUOUS +X (casters). All source-backed. Every declared type appears in the sweep. |
| ③ 主体形态家族 | 换核心几何原型 | 有 | 3 prototypes (Slot A): wheeled box + grid box (Volumetric Envelope Form) vs aframe (Macro Surface Construction, triangular prism). source-backed anchors + fork; registered in `slot_choices`. |
| ④ 表面装饰 | 表面叠加细节 | 有 (record_only + world_knowledge_extrapolation) | door infill solid-plank / wire-mesh / clear-acrylic; plank seams + fine wood grain + face screws (B `_add_wood_grain`/`_add_face_screws`), plank lines (A), gable planks (aframe), roof edge caps, black hinge leaves + latch plates. Host-conformal: each is a `.visual(...)` on the host door/frame face it sits on (derive order ③→⑤→④). Decoration reads ride the palette. |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | `n_tiers` (large height swing), mobility stance `leg_bottom_z` {0.0, 0.11}, `roof_overhang_scale` [0.90,1.15]. **Motion envelopes** (axis / open-dir / [closed, feasible-upper]): compartment door REVOLUTE vertical-Z, opens −Y, [0, `door_swing`∈1.20–1.50]; roof_lid REVOLUTE lateral −X, opens +Z, [0, 1.20]; drop_ramp REVOLUTE lateral −X, drops then folds +Z, [0, 1.35]; latch hasp REVOLUTE +Y, lifts, [0, 1.15]; tray PRISMATIC −Y, [0, `tray_travel`∈0.28–0.34]; pop-hole PRISMATIC +Z, lifts, [0, 0.24]; caster CONTINUOUS +X full turn. `motion_test_plan`: run `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=28, ignore_fixed=True)` + one targeted `ctx.pose(...)` per mechanism family present (door opens −Y; roof lifts +Z; ramp folds +Z; latch lifts; tray slides −Y; pop lifts +Z; caster spins). No sampled-pose exemption. |
| ⑥ 涂装 | 只改材质/颜色 | 有 | material classes painted-wood + natural-wood + galvanized/black wire-mesh (metal) + plastic/galvanized tray + clear acrylic; ≥4 colorways: white_grey (A), natural_pine (B), warm_timber (aframe), slate_grey (companion). Material-class coverage ≥ ceil(0.5×4)=2 (wood + metal-mesh + plastic present every seed). |

**收尾自检**：batch 0–9 seed 里应肉眼看到——wheeled/grid/aframe 三种主体拉得开、wood/mesh/plastic
材质都出现、mesh 贴合门框不悬空、door/roof/ramp/latch/tray/pop/caster 关节全程不穿模。

## 采样与覆盖审计

总组合数（realized，含 gating）：
- body_form(3) × mobility(2) × front_access(form-gated: wheeled 2 / grid 1 / aframe 2) →
  per-form (2·2 + 1·2 + 2·2) = 4+2+4 = **10 (form,mobility,access) combos**, × `n_tiers`{1,2,3} on
  grid (+2 tuples for the 2 grid combos → ~+4) → **≈14 distinct slot tuples**, × 4 palette ×
  continuous scales → topology target comfortably >300 over 1000 seeds. report-only.

理由：多样性主要来自离散 body_form(③/①) + mobility(①/②) + front_access(②) + n_tiers(mult) 槽；
连续 scale（door_swing/tray_travel/roof_overhang）仅做 clamp，不撑多样性。低于 300 是因为本小类真实
组合空间受形态数 × 兼容门控限制（3 forms × 门控 access × mult），已按源锚点上限如实覆盖。

seed_domain_policy：procedural_first（seed 0 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` = `random.Random(seed)`；先 `mobility` →
derive `leg_bottom_z`；`body_form`；`front_access` = rng.choice(ALLOWED_ACCESS[form])；`n_tiers`
weighted then gated to grid；`palette`；continuous scales uniform then clamp in `resolve_config`.
Compatibility matrix = `ALLOWED_ACCESS` dict + n_tiers gate (prevents illegal grid-pop-hole /
non-grid multi-tier). No regression overrides (procedural covers seed 0).
Topology target：≈300 over 1000-seed slot tuples (report-only, not a gate; true space is
gating-limited as noted).
Controlled local parameterization：`door_swing`, `tray_travel`, `roof_overhang_scale` (continuous,
clamped in `resolve_config`); they only touch joint upper limits / free-space roof overhang and can
never break the door/receiver/latch/mesh contacts, the caster axle, or the tray rails.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | mobility→leg_bottom_z, form, form-gated access, gated n_tiers, palette, scales | slot_choices_for_seed matches build choices |
| compatibility matrix | ALLOWED_ACCESS[form] + n_tiers gate; fallback → drop_ramp / n=1 | no floating, collision, axis, closed-pose, max-tier failures |
| controlled local variation | door_swing/tray_travel/roof_overhang, clamped | proportions/travel vary without breaking hinge receivers / latch pins / tray rails / joint origins / identity |
| regression overrides | none | procedural covers seed 0 |
| random sweep | seeds 0-35 initial pass (+corner), 0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 3 | yes | yes | ③ primary form slot |
| mobility | 2 | yes | — | ①/② casters vs legs |
| front_access | 2 | yes | — | ② (form-gated) |
| n_tiers (mult) | N∈{1,2,3} | yes | — | source B / n2 / n1 |

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names for (body_form, mobility,
  front_access, n_tiers)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed 0 not special)
- compatibility matrix (`ALLOWED_ACCESS` + n_tiers gate) prevents illegal combos in `resolve_config`
- no regression overrides; no curated/modulo main domain
- controlled scale params clamped in `resolve_config`; body xy footprint fixed per form so contacts hold
- every non-FIXED joint is a captured hinge/pin/rail with element-scoped `allow_overlap` +
  `expect_contact`; no `MatingContract` phantom anchors; no FIXED-jointed decoration parts
- key joints have expected type/axis/range (compartment door REVOLUTE vertical-Z; roof/ramp REVOLUTE
  lateral-X; latch REVOLUTE +Y; tray PRISMATIC −Y; pop PRISMATIC +Z; caster CONTINUOUS +X)
- copied grid objects follow `{kind}_door_{row}` / `{name}_latch` naming + vertical-row placement
- Rule 5: `fail_if_parts_overlap_in_sampled_poses` + one targeted `ctx.pose` per mechanism family

## Reject cases
- A door/roof/ramp that hovers off the frame with no hinge-receiver contact path (isolated island).
- Compartment doors whose full-open pose drives them through a neighbor door or the frame (穿模).
- Latch hasp / hinge / ramp / caster joint origin off the frame hardware (>15mm) → articulation-origin fail.
- guillotine pop-hole panel that escapes its guide channels or does not lift on +Z (dead joint).
- casters that do not spin (dead CONTINUOUS joint) or a wheel floating off its fork.
- grid_cabinet with `n_tiers`>1 built by hand-written rows instead of the loop (naming drift).
- Downgrading the wire-mesh / plank structure to a single flat box (loses category identity, Rule 3).
- Monochrome output (palette not driving `.visual(material=...)`).

## 与相邻类别的边界
- 不该混入：dog kennel / crate（无 mesh 通风前面 + 无 tray + 无兔子分区 sleeping box）。
- 不该混入：chicken coop / hen house（有 nest boxes + roost bars + egg door，不是 rabbit 分区）。
- 不该混入：bird aviary（全 mesh 高笼，无 enclosed 木质 shelter + tray）。
- 不该混入：garden storage cabinet / greenhouse（无 mesh 通风、无 raised pet 分区、无 tray）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Parallel-children `hutch_frame` spine (both origins share it); A-frame cadquery gable walls replaced by box gable planks for compile budget + primitive simplicity; run-attachment (probe) folded into the drop-ramp/pop-hole access members rather than a separate body candidate. |

## 模板实现备注（可选）
- Shared helpers: `_box`/`_cyl`; `_front_mesh`/`_side_mesh`/`_slope_mesh` (wire grids); source-B
  `_solid_door_geometry`/`_mesh_door_geometry`/`_add_hinge_knuckles`/`_add_latch_mount`/`_add_latch_bar`
  for the grid; source-A `_door_frame` for wheeled/aframe doors.
- Captured-pin element-scoped `allow_overlap` + `expect_contact`: door hinge leaf ↔ frame hinge
  receiver; grid latch pivot pin ↔ door pivot plate; caster wheel ↔ fork; ramp hinge rod ↔
  receiver; pop panel ↔ guide/trim (mirrors each source's run_tests).
- Every joint origin on real hardware; vertical door hinge axes thread the horizontal front rails
  (rotational-axis-touches-hardware). `n_tiers` z-lines single-sourced from `row_bottoms`.
