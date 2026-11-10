# Ring Binder (3-ring binder) Spec — `ring_blinder`

> Folder name says "ring-blinder"; the real object is a **3-ring office/school binder**.
> Identity taken from the sample records, not the folder label.

## 元信息
| 项 | 值 |
|---|---|
| slug | `ring_blinder` |
| template path | `agent/templates/ring_blinder.py` |
| test path (optional) | `tests/agent/test_ring_blinder_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern=mixed`: one fixed `spine` root carries two revolute cover boards + a
FIXED paper stack (always-present chassis, single structural family — recorded
not slotted), plus a spine/back-cover-mounted metal ring mechanism whose form,
side-count, station-count, and mount vary, plus two optional parallel add-ons
(spine carry handle, fold-over closure strap).

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this subcategory (2 origins + 6 verified-PASS forks) |
| source_index_policy | only adopted module sources are indexed below; all 8 were read and all 8 are adopted |

- Origins: `rec_workspace__3_ring_binder__002_...` (B, loop-based single-moving), `rec_workspace__3_ring_binder__001_...` (A, split dual-arm).
- Forks (all verified PASS): `rec_ring_blinder_var_ring_dring`, `rec_ring_blinder_var_ring_slant`, `rec_ring_blinder_var_mount_back_cover`, `rec_ring_blinder_var_n2`, `rec_ring_blinder_var_handle_spine`, `rec_ring_blinder_var_closure_strap`.

## 核心身份

A ring binder: two hinged cover boards on a center spine, with a metal
multi-ring mechanism (2+ ring stations) that opens/closes to load and clamp
punched sheets. Default mature domain: office/school 2–4 ring binders, round /
D / slant-D ring cross sections, spine- or back-cover-mounted mechanism, with
or without a carry handle or closure strap.

Must NOT drift into: lever-arch file (single big lever + spring plate), 2-pocket
folder / document wallet / portfolio (no rings), 6-ring personal organizer /
planner (leather disc identity), clipboard, or spiral/coil notebook.

## 槽位 + 候选模块表

The always-present chassis (`spine` + `front_cover` + `back_cover` +
`paper_stack`, two cover revolutes) is a single structural family across all 8
samples — recorded, **not** a slot (no second cover-board form exists; folding
it into a fixed root per SPEC_TEMPLATE §4). Registered slots below each reach
≥2 structurally distinct, source-backed candidates.

### Slot A：ring_mechanism（② joint topology — includes its co-varying lever)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_moving` | forked_anchor | `rec_workspace__3_ring_binder__002_...` (B) | model.py:L171-L322 | eligible if compatible | `ring_bar` (FIXED plate) carries fixed ring halves; ONE `ring_halves` part on a shared `moving_hinge_rod` REVOLUTE (axis y, [0,0.62]) carries all moving halves; linked cam-strip `lever_tabs` REVOLUTE (axis x, ±5°). 3 moving parts, 2 revolutes. |
| `split_dual` | forked_anchor | `rec_workspace__3_ring_binder__001_...` (A) | model.py:L105-L412 | eligible if compatible | `ring_plate` (FIXED) carries TWO `ring_arm_0/1` banks, each its own REVOLUTE (opposite y axes, [0,0.55]) so both sides open; two independent `lever_0/1` REVOLUTEs (axis x). 4 moving parts, 4 revolutes; `_ring_bank_geometry` connected-arc mesh. |

Lever style co-varies with the mechanism in **both** source records (B=linked
strip + single, A=dual levers + split); it is not an independent axis and is
folded into each `ring_mechanism` module (SPEC_TEMPLATE §4 "fold weak ones into
a neighbor").

### Slot B：ring_form（③ Primary Form Family — ring cross section)

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `round` | forked_anchor | B / A | B model.py:L210-L275 | Volumetric Envelope Form | eligible if compatible | O-ring: fixed half arcs out then up, moving half mirrors; tube-from-spline point lists. |
| `dring` | forked_anchor | `rec_ring_blinder_var_ring_dring` | model.py:L210-L275 | Planar Boundary Form | eligible if `single_moving` | D-ring: fixed half is a straight vertical back post, moving half is a top arc meeting it (flat-backed D outline). |
| `slant` | forked_anchor | `rec_ring_blinder_var_ring_slant` | model.py:L210-L275 | Planar Boundary Form | eligible if `single_moving` | slant-D: back leg tilts forward, arc leans — leaning-D profile distinct from round and upright-D. |

Same part tree / same `tube_from_spline_points` primitive / same
`ring_bar_to_ring_halves` interface — only the ring path point lists change
(a legal ③ structural distinction, not size/paint). `dring`/`slant` are gated to
`single_moving` (the split-dual bank uses connected round arcs; forcing a D/slant
onto it would invent geometry the A source lacks).

### Slot C：mechanism_mount（① skeleton — mechanism root)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `spine` | forked_anchor | B / A (`spine_to_ring_bar`) | B model.py:L240-L246 | eligible if compatible | metal plate FIXED to the center spine top face (mechanism centered on spine). |
| `back_cover` | forked_anchor | `rec_ring_blinder_var_mount_back_cover` | model.py:L241-L251 | eligible if compatible | plate FIXED to the inner back-cover face near the spine edge; rings rise from the back cover and follow it when the cover hinges. |

### Slot D：handle_or_grip（① skeleton — optional carry grip)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | forked_anchor | B / A | B model.py (no handle) | eligible if compatible | no carry grip (default binder). |
| `folding_spine` | forked_anchor | `rec_ring_blinder_var_handle_spine` | model.py:L347-L398 | eligible if compatible | `spine_handle` part (two lugs + two arms + grab bar) on the outer spine face, ONE `spine_to_handle` REVOLUTE (axis y, [0, π/2]) folds flat / swings out. |

### Slot E：closure（② joint — optional fold-over closure)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `none` | forked_anchor | B / A | B model.py (no closure) | eligible if compatible | open binder, no strap. |
| `foldover_strap` | forked_anchor | `rec_ring_blinder_var_closure_strap` | model.py:L362-L395 | eligible if compatible | `closure_strap` part (strap body + hinge loop + catch tab) rooted at the front-cover free edge, ONE `front_cover_to_closure_strap` REVOLUTE (axis y, [0,2.5]) folds across the opening. |

Slot candidate counts: A=2, B=3, C=2, D=2, E=2 (+ N multiplicity 3 values). No
1-candidate slots; lever + cover-board form folded into neighbors as noted.

## 槽位图（slot graph）

pattern: `mixed`

```text
spine (fixed root)
  ├─[REVOLUTE axis +y, spine edge x=-SPINE_W/2]→ front_cover ─[FIXED]→ (paper_stack on back_cover)
  ├─[REVOLUTE axis −y, spine edge x=+SPINE_W/2]→ back_cover ─[FIXED]→ paper_stack
  ├─[Slot C FIXED, top face]→ ring_mechanism plate (Slot A)
  │        └─ single_moving: plate ─[REVOLUTE axis y]→ ring_halves ; plate ─[REVOLUTE axis x]→ lever_tabs
  │        └─ split_dual:    plate ─[REVOLUTE axis ±y]→ ring_arm_0/1 ; plate ─[REVOLUTE axis x]→ lever_0/1
  │        (ring cross-section = Slot B ring_form on single_moving; round on split_dual)
  ├─[Slot D REVOLUTE axis y, outer spine face]→ spine_handle        (optional)
  └─(Slot E) front_cover ─[REVOLUTE axis y, free edge]→ closure_strap (optional)
```

Interface points: cover hinges = spine ±x board edge, axis y; mechanism mount =
board top face contact plane (FIXED); ring open = shared hinge rod near plate,
axis y; lever = plate end pivot, axis x; handle = outer spine face, axis y;
closure = front-cover free edge, axis y. Multiplicity N drives the ring-station
tuple `RING_Y` consumed by both mechanism modules + paper holes.

## 每槽位 Module Emits / Interfaces

### chassis (fixed root, always) / model.py B:L77-L168, L324-L345
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spine`, `front_cover`, `back_cover`, `paper_stack` | B:L77-L149, L324-L338 |
| internal joints | `spine_to_front_cover` REVOLUTE +y [0,2.15]; `spine_to_back_cover` REVOLUTE −y [0,2.15]; `back_cover_to_paper_stack` FIXED | B:L151-L168, L339-L345 |
| interfaces | spine top face (mount plane) + spine ±x board edges (cover hinges) + front-cover free edge (closure) + outer spine face (handle) | B model |

### Slot A single_moving / B:L171-L322
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ring_bar` (plate + fixed halves + saddles + rivets + lever standoffs), `ring_halves` (moving_hinge_rod + moving halves), `lever_tabs` | B:L171-L322 |
| internal joints | `ring_bar_to_ring_halves` REVOLUTE y [0,0.62]; `ring_bar_to_lever_tabs` REVOLUTE x ±5° | B:L277-L322 |
| upstream interface | plate bottom face FIXED to chassis mount plane (Slot C) | B:L240-L246 |

### Slot A split_dual / A:L105-L412
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ring_plate`, `ring_arm_0`, `ring_arm_1`, `lever_0`, `lever_1` | A:L247-L348 |
| internal joints | `plate_to_ring_arm_0` REVOLUTE −y [0,0.55]; `plate_to_ring_arm_1` REVOLUTE +y [0,0.55]; `plate_to_lever_0/1` REVOLUTE x [-0.55,0.55] | A:L377-L412 |
| upstream interface | `ring_plate` bottom face FIXED to chassis mount plane (Slot C) | A:L368-L374 |

### Slot D folding_spine / handle_spine:L358-L398 · Slot E foldover_strap / closure_strap:L367-L395
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spine_handle` (2 lugs + 2 arms + grab bar) / `closure_strap` (body + hinge loop + catch tab) | forks |
| internal joints | `spine_to_handle` REVOLUTE y [0,π/2] / `front_cover_to_closure_strap` REVOLUTE y [0,2.5] | forks |

Non-moving detail (creases, sleeves, pockets, saddles, rivets, standoffs, lips)
is emitted as `parent.visual(...)`, never a FIXED-joint part (Rule 1). Every
moving child parents to a real board/plate visual (Rule 2); captured hinge-rod ↔
saddle / lug overlaps are element-scoped `allow_overlap` in `run_tests`.

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `ring_mechanism` | enum | `single_moving` / `split_dual` | `single_moving` | choice | procedural sampler | Slot A |
| `ring_form` | enum | `round` / `dring` / `slant` | `round` | conditional | `= round` when `split_dual` (gate) | Slot B |
| `mechanism_mount` | enum | `spine` / `back_cover` | `spine` | choice | procedural sampler | Slot C |
| `handle` | enum | `none` / `folding_spine` | `none` | choice | procedural sampler | Slot D |
| `closure` | enum | `none` / `foldover_strap` | `none` | choice | procedural sampler | Slot E |
| `ring_count` (N) | int | {2, 3, 4} | 3 | choice | weighted sampler → source `RING_Y` tuple | §8 |
| `palette_theme` | enum | white_plastic / black_vinyl / colored_poly | white_plastic | choice | ⑥ companion; geometry-invariant | ⑥ |
| `binder_h` | float | [0.290, 0.340] | 0.310 | independent | clamp; must contain fixed mechanism (PLATE_L=0.262) | B:L22 |
| `cover_w` | float | [0.230, 0.280] | 0.255 | independent | clamp | B:L21 |
| `spine_w` | float | [0.045, 0.090] | 0.060 | independent | clamp (binder capacity) | B:L23 |
| (—) | constraint | — | — | inequality | `binder_h ≥ PLATE_L + 0.020`; else clamp binder_h up | mechanism fit |

The metal ring mechanism is **standardized hardware** — its own dimensions
(PLATE_L, PLATE_W, ring radii, saddle sizes) are fixed real constants (a real
binder ring bar is a stocked part), so a board-size draw never gaps the plate;
only the board dims (⑤) and the source `RING_Y` tuple (N) vary.

## 7.5 编译预算 / compile budget
Per-seed budget: **≤ 12s**. Geometry is mostly Box/Cylinder; the only meshes are
thin ring tubes (`tube_from_spline_points`, ≤18 radial × 14/seg over 3–5 pts) and
the two connected ring banks (`_tube` 10 sides). ≤ 4 rings × ≤ 2 tubes/ring +
2 banks + 4 rounded panels — well under budget. Tessellation caps: ring tubes 18
radial, rounded panels corner_segments 8, banks 10 sides. All N rings reuse one
helper per ring form.

## 8. Multiplicity / Copy Logic

Exactly **one** multiplicity axis: number of ring stations N.

- `count_param`: N = number of ring stations = `len(RING_Y)`.
- `N_range`: [2, 4] (product domain for true ring binders; 6/7-ring drifts to
  personal-organizer neighbor → excluded). Sampling domain (weighted): N=3 most
  common (0.5), N=2 (0.25), N=4 (0.25) — small N frequent, N=4 rarer.
- Source tuples (verbatim / source-faithful): N=2 `(-0.045, 0.045)` (fork `n2`
  used ±0.040), N=3 `(-0.105, 0.0, 0.105)` (B), N=4 `(-0.117,-0.039,0.039,0.117)` (A).
- copied object: one ring "station" = single_moving {`fixed_saddle_i`,
  `moving_saddle_i`, `rivet_i`, `fixed_ring_half_i`} on `ring_bar` +
  {`moving_lug_i`, `moving_ring_half_i`} on `ring_halves`; split_dual one arc per
  station inside each `ring_bank`; plus `reinforced_hole_i` on `paper_stack`.
- naming: stable `*_{i}` index suffix per station.
- placement: `RING_Y` tuple, evenly spaced, symmetric about spine center.
- joint policy: all moving halves share the ONE `ring_bar_to_ring_halves`
  revolute (single_moving) / the two arm revolutes (split_dual) — **no per-ring
  joints**; paper holes FIXED. Loop-emitted; N changes only the station tuple.
- `slot_choices` encodes N as raw value (narrow range) `("ring_count", "n{N}")`.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 有 | mechanism_mount spine vs back_cover (① `mount_back_cover` fork); ring_mechanism single (3 parts/2 rev) vs split_dual (5 parts/4 rev, A); handle none vs folding_spine (① `handle_spine` fork). All forked_anchor/origin. |
| └ multiplicity | 同构件 ×N | 有 | 见 §8: N∈{2,3,4}, weighted (0.25/0.5/0.25), source tuples n2/B/A. |
| ② 关节类型 | 边换 type/轴 | 有 | single_moving one shared ring revolute + linked lever revolute (B) vs split_dual two arm revolutes + two lever revolutes (A); optional closure revolute (`closure_strap`). All covers revolute. Every declared type appears in sweep. |
| ③ 主体形态家族 | 换核心 part 形态原型 | 有 | ring cross-section: `round` (Volumetric Envelope, B/A) / `dring` (Planar Boundary, `ring_dring`) / `slant` (Planar Boundary, `ring_slant`). Registered as `ring_form` slot. Cover-board family single (planar boards) → recorded not slotted. |
| ④ 表面装饰 | 叠加表面细节 | 有(companion) | spine label sleeve + insert (A), clear overlay view pockets (B), sealed edge lips (A) — `record_only`, host-derived `parent.visual`, no dedicated variant, not counted toward budget. |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | binder_h [0.29,0.34], cover_w [0.23,0.28], spine_w [0.045,0.09] (capacity). Motion envelopes: covers REVOLUTE +y/−y [0,2.15]; ring open REVOLUTE y [0,0.62] (single) / ±y [0,0.55] (split); lever REVOLUTE x ±5° (linked) / [-0.55,0.55] (dual); handle REVOLUTE y [0,π/2]; closure REVOLUTE y [0,2.5]. `motion_test_plan`: run `fail_if_parts_overlap_in_sampled_poses`; targeted `ctx.pose` for cover-fold-up, ring-open-outward, lever-rock, handle-swing-out, closure-fold-over. No continuous joints → no full-turn case. |
| ⑥ 涂装 | 只改材质/颜色 | 有(companion) | white_plastic / black_vinyl / colored_poly board + satin-nickel vs dark metal rings; ≥3 palettes. Geometry-invariant companion; material大类 plastic/painted-board dominate (binder identity), not counted toward structural budget. |

①②③ + N source-backed (origin/forked_anchor). ④⑤⑥ companion (record_only),
never standalone, never counted toward budget.

## 采样与覆盖审计

总组合数：ring_mechanism(2) × ring_form(gated: single→3, split→1 ⇒ 4) × mount(2) × handle(2) × closure(2) × N(3) = 4×2×2×2×3 = **96** slot-choice tuples (× palette 3 = 288 with ⑥). Ample for a `simple`-band binder.

理由：coverage-first per the source map's `simple` richness band — a ring binder
has thin honest structural vocabulary (fixed cover boards + spine; variety in
ring shape ③, side-count ②, station-count N, mount ①, + optional handle/closure).
No padding with out-of-category forms (lever-arch, organizer, zip portfolio).

seed_domain_policy：procedural_first. `config_from_seed(seed)` uses deterministic
`random.Random(seed)` for **every** seed including seed 0 (no special-case anchor,
no curated/modulo table). Procedural order: sample independent board dims →
sample slot enums → gate `ring_form=round` if `split_dual` → weighted N →
`resolve_config` clamps dims + resolves the fit inequality. No regression overrides.

Topology target：96 slot-choice tuples (report-only). Below 300 because the
subcategory is intrinsically simple (source map `simple`, 8 anchors); the real
combination space is bounded by the two mechanism origins + honest ①②③/N forks.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | board dims → slot enums → ring_form gate → weighted N; `random.Random(seed)` | `slot_choices_for_seed` matches build choices |
| compatibility matrix | `dring`/`slant` legal only with `single_moving` (else → `round`); everything else freely combinable; mechanism dims fixed hardware | no floating plate, no ring/lever collision through travel, mount follows cover |
| controlled local variation | binder_h / cover_w / spine_w clamped + fit inequality; mechanism dims fixed | proportions vary without breaking mount plane, ring clearance, joint origins, identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass; 0-999 maturity audit | contract failures; axis_realization covers all A/B/C/D/E candidates + N |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| ring_mechanism | 2 | yes | no | 2 source origins; a 3rd ② would drift to lever-arch (excluded) |
| ring_form | 3 | yes | yes | round / dring / slant |
| mechanism_mount | 2 | yes | no | spine / back_cover |
| handle_or_grip | 2 | yes | no | none / folding_spine |
| closure | 2 | yes | no | none / foldover_strap |
| ring_count (N) | 3 | yes | yes | 2 / 3 / 4 |

## Validator
- `slot_choices_for_seed` returns implemented module names for A/B/C/D/E + N.
- `config_from_seed` uses deterministic procedural sampling for all seeds (0 not special).
- gating: `dring`/`slant` never paired with `split_dual`.
- controlled scales clamped; `binder_h ≥ PLATE_L+0.020` resolved in `resolve_config`.
- key joints present with expected type/axis: cover revolutes ±y; ring-open revolute(s) y; lever revolute(s) x; handle revolute y; closure revolute y.
- copied ring stations follow `*_{i}` naming and `RING_Y` placement.
- captured hinge-rod/lug overlaps declared element-scoped only.

## Reject cases
- No metal ring mechanism, or rings that do not open (no non-fixed ring joint).
- Floating ring plate / handle / strap (no support path to a board).
- Rings collide through their open travel, or a moving ring sweeps into the fixed halves/saddles.
- Back-cover-mounted mechanism does not follow the back cover when it hinges.
- Cover boards do not share the spine hinge line, or covers not revolute.
- N outside [2,4] (drifts to organizer), or per-ring independent joints.
- `dring`/`slant` welded onto the split-dual bank (invented geometry).

## 与相邻类别的边界
- 不该混入 lever-arch file（single big spring-loaded lever + 2 upright rings；distinct mechanism, in must_not_become）。
- 不该混入 2-pocket folder / portfolio / document wallet（no rings）。
- 不该混入 6-ring personal organizer / planner（leather disc identity；N capped at 4）。
- 不该混入 clipboard / spiral notebook（no hinged covers + ring mechanism）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; authored from 2 origins + 6 verified-PASS forks; awaiting sweep + human 目检. |

## 模板实现备注
- Chassis (record B, flat-open covers) is the single shared body for all mechanisms; split-dual (record A) mechanism is grafted onto it, mounted on the board top face at z=BOARD_T/2 (not A's original spine_t).
- Metal mechanism dims are fixed constants (standardized hardware); only board dims + `RING_Y` vary.
- Both mechanism plates authored so local (0,0,0) = plate bottom on the mount plane → FIXED origin lands on the board (origin-honesty) and mating stays clean.
- Ring form only reshapes `tube_from_spline_points` point lists; `dring`/`slant` gated to `single_moving`.
- element-scoped `allow_overlap`: moving_hinge_rod ↔ moving_saddle, moving_lug ↔ moving_saddle (single); ring_bank ↔ ring_hinge_saddle (split); closure hinge_loop ↔ strap_hinge_lug; handle lug seating.
</content>
</invoke>
