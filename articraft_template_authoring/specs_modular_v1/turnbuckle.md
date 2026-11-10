# turnbuckle — modular spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `turnbuckle` |
| template path | `agent/templates/turnbuckle.py` |
| test path (optional) | `tests/agent/test_turnbuckle_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `linear_chain` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star (rating=5) samples in this workbench-only category (0611 turnbuckle: 4 origin picturex records + 7 P2-forked variant records) |
| source_index_policy | only adopted module sources are indexed below |

Origin anchors (workbench, rating=5 per task contract):

- `rec_picturex_0611__turnbuckle__001__png_689bc9e644844763a8ada4d8d9cd895c` — eye-eye, open forged barrel with polygonal outer frame + inspection window; opposed threaded shanks in shallow bores; REVOLUTE barrel + PRISMATIC right rod.
- `rec_picturex_0611__turnbuckle__002__png_5eeeedffab0d4787b0fdb48f25f4e307` — jaw-eye, closed faceted body + tapered shoulders; hidden internal spindle scaffold; REVOLUTE barrel + 2 PRISMATIC rod adjustments + 1 REVOLUTE clevis pin on fork.
- `rec_picturex_0611__turnbuckle__003__png_f334640b8817451f89c2694fb3384dfd` — jaw-jaw, open box barrel with rounded corners + window; two clevis pins; REVOLUTE barrel + PRISMATIC right rod + 2 REVOLUTE swivel pins.
- `rec_picturex_0611__turnbuckle__004__png_1cebe68f2a7d4b5080da47f9d2a8754f` — hook-eye, closed cylindrical barrel with polygonal flats + polished collars; hidden thread-bridge; REVOLUTE barrel + 2 PRISMATIC rod adjustments.

P2 forked variants (used only to substantiate slot candidates, not to add anchors beyond origins):

- `rec_0611_turnbuckle_var_end_topology_hook_hook` — hook end candidate.
- `rec_0611_turnbuckle_var_end_topology_hook_jaw` — mixed end candidate.
- `rec_0611_turnbuckle_var_barrel_form_closed_cylinder` — closed cylindrical barrel (③ Volumetric Envelope Form).
- `rec_0611_turnbuckle_var_barrel_form_forged_oval` — forged oval closed barrel (③ Volumetric Envelope Form).
- `rec_0611_turnbuckle_var_end_motion_swivel_ends` — REVOLUTE swivel pin on each jaw (② joint type).
- `rec_0611_turnbuckle_var_lock_paired_lock_nuts` — inline non-articulated lock-nut visuals near each rod-shoulder (④ surface hardware).
- `rec_0611_turnbuckle_var_pin_quick_release_clevis_pin` — jaw + captured clevis pin with keeper.

## 核心身份

Turnbuckle = tensioning coupler: a rotating threaded barrel/body with two opposed threaded rods emerging from its ends, one left-hand and one right-hand, terminating in load-transfer end fittings (hook, oval eye, or clevis-fork "jaw"). Rotating the barrel draws both rods inward or outward simultaneously; the rods themselves cannot rotate relative to the barrel bore (they translate axially). Ends can also be single-DOF swivels around a captured clevis pin. Overall silhouette: long-axis symmetric slender hardware, length ~ 5–7× diameter, along +X.

Must keep: (a) a central rotating barrel/body with opposed axial thread engagement; (b) two independent axial-adjustment DOFs (one per rod) OR one axial adjustment DOF (the opposite rod fixed, sample 001 style); (c) end fittings drawn from {hook, eye, jaw}. Must NOT become: a plain eye-bolt, a shackle, a chain-link, a quick-release clamp, a rigging screw with a solid one-piece body, or a two-piece pipe coupling.

## 槽位 + 候选模块表

Three structural slots + one multiplicity axis. Slot A (barrel_form) is the parent; both end slots (Slot B / Slot C) are parallel children of the barrel. Choosing an end candidate independently drives whether that end has a captured clevis pin (② swivel-end joint type).

### Slot A：barrel_form (③ Primary Form Family; ①/② parent)

Selects the geometry family + joint idiom of the central rotating body. Every candidate exposes the same downstream interface: two coaxial axial bores at `±half_len` along +X, and a REVOLUTE `barrel_rotation` joint at the origin about +X.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `closed_cylindrical_barrel` | forked_anchor | `rec_picturex_0611__turnbuckle__004__png_1cebe68f2a7d4b5080da47f9d2a8754f` / `rec_0611_turnbuckle_var_barrel_form_closed_cylinder` | `004.model.py:L132-L160` (`_build_barrel`, `_build_core`) | eligible if compatible | Volumetric Envelope Form = closed axial cylinder w/ polygonal-flat mid, round collars, polished bands; internal hidden `thread_bridge` support; REVOLUTE +X barrel |
| `closed_faceted_barrel` | forked_anchor | `rec_picturex_0611__turnbuckle__002__png_5eeeedffab0d4787b0fdb48f25f4e307` | `002.model.py:L74-L91` (`_barrel_shape`) | eligible if compatible | Volumetric Envelope Form = closed decagonal prism w/ conical shoulders + short round end collars; through bore; hidden spindle scaffold |
| `open_box_barrel` | forked_anchor | `rec_picturex_0611__turnbuckle__003__png_f334640b8817451f89c2694fb3384dfd` | `003.model.py:L53-L73` (`_build_open_barrel`) | eligible if compatible | Macro Surface Construction = filleted rectangular open frame with through-window + polygonal end sockets; visibly open-body |
| `open_forged_oval_barrel` | forked_anchor | `rec_picturex_0611__turnbuckle__001__png_689bc9e644844763a8ada4d8d9cd895c` / `rec_0611_turnbuckle_var_barrel_form_forged_oval` | `001.model.py:L72-L111` (`_open_turnbuckle_barrel`) | eligible if compatible | Macro Surface Construction = tapered forged frame with elongated inspection slot + raised end bosses + upper/lower pads; visibly open-body oval outline |

Rationale for 4 candidates (target 3-6): sources deliver two clearly different form families (Volumetric Envelope = closed body; Macro Surface Construction = open-frame) with two structurally-distinct realisations each. `form_subtype` per candidate is annotated inline.

### Slot B：end_fitting_left (①/② end topology + joint type)

Left rod + left end fitting. Every candidate exposes upstream_axial = `(-half_len, 0, 0)` along -X, and a PRISMATIC `left_adjustment` joint parented to the barrel about -X (rod extends further out as `q` grows). Two of the candidates additionally emit a captured swivel pin (`fitting_pin` REVOLUTE about +Y).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `hook_end` | forked_anchor | `rec_picturex_0611__turnbuckle__004__png_1cebe68f2a7d4b5080da47f9d2a8754f` / `rec_0611_turnbuckle_var_end_topology_hook_hook` | `004.model.py:L163-L186, L293-L364` (`_build_hook_rod`, hook rod visuals) | eligible if compatible | ① end topology = open forged planar hook; threaded rod core + shoulder + polyline hook; no captured pin (single DOF = PRISMATIC only) |
| `eye_end` | forked_anchor | `rec_picturex_0611__turnbuckle__001__png_689bc9e644844763a8ada4d8d9cd895c` / `rec_picturex_0611__turnbuckle__004__png_1cebe68f2a7d4b5080da47f9d2a8754f` | `001.model.py:L47-L69` (`_eye_fitting`); `004.model.py:L189-L212` (`_build_eye_rod`) | eligible if compatible | ① end topology = closed forged oval/elliptical eye ring; threaded shank + tapered neck; no captured pin |
| `jaw_end` | forked_anchor | `rec_picturex_0611__turnbuckle__002__png_5eeeedffab0d4787b0fdb48f25f4e307` / `rec_picturex_0611__turnbuckle__003__png_f334640b8817451f89c2694fb3384dfd` | `002.model.py:L94-L124` (`_left_fork_shape` + `_pin_shape`); `003.model.py:L76-L108` (`_build_jaw_fitting`, `_build_clevis_pin`) | eligible if compatible | ①+② end topology = clevis fork w/ two lugs + captured clevis pin; PRISMATIC rod + REVOLUTE `fitting_pin` about +Y |

### Slot C：end_fitting_right (①/② end topology + joint type)

Mirror of Slot B along +X; same candidates. See Slot B for structural detail. Every candidate exposes upstream_axial = `(+half_len, 0, 0)` along +X, and either:

- a PRISMATIC `right_adjustment` about +X (when `right_adjustable=True`, sampled per barrel — see §7), or
- a shared root policy where the right fitting is the reference frame (sample-001 style, mapped by `resolve_config` to just one rod adjustment).

Same three candidates (`hook_end`, `eye_end`, `jaw_end`) as Slot B; identical `sampling eligibility`. Independence of Slot B / Slot C is intentional: real-world catalogue turnbuckles mix ends freely.

### Multiplicity axis: lock_count (④/① auxiliary; 0 or 1 pair)

Optional lock-nut hardware. When present, one lock-nut visual is inlined on each rod between its shoulder and the barrel end collar. Not a separate part (Rule 1) — non-articulated washer/nut visuals.

`count_param = lock_count ∈ {0, 1}`; when `lock_count == 1` two lock-nut visuals are emitted (one per rod), paired by symmetry.

## 槽位图（slot graph）

pattern: `parallel_children` (barrel root; two ends are parallel children with independent DOFs)

```
barrel_form (root)  --[REVOLUTE +X barrel_rotation to hidden internal spindle scaffold]--> spindle_bearing
       ├──[PRISMATIC -X left_adjustment ; mating: barrel_shell / left_rod_engagement]──> end_fitting_left
       │       └──[REVOLUTE +Y left_fitting_pin ; captured clevis pin]──> left_pin  (only when Slot B == jaw_end)
       └──[PRISMATIC +X right_adjustment ; mating: barrel_shell / right_rod_engagement]──> end_fitting_right
               └──[REVOLUTE +Y right_fitting_pin ; captured clevis pin]──> right_pin  (only when Slot C == jaw_end)
```

Notes:

- The rotating barrel is realised as its own part and rotates about +X via a REVOLUTE joint to a hidden internal `spindle` scaffold (source 002 idiom) OR the barrel itself is the root and the two rods parent directly to it (sources 001/003 idiom). Both are supported — `resolve_config` picks one root policy per seed based on `barrel_form`; open-frame barrels use the "barrel-is-root" idiom (rods are children of the barrel), closed barrels use the hidden-spindle idiom (barrel + rods are all children of the hidden spindle). This preserves each source's authentic articulation graph.
- All non-FIXED joints declare a `MatingContract` between named visuals. Captured-pin overlaps use element-scoped `ctx.allow_overlap`.
- Interface points: for both root policies, the cross-slot interfaces are the two coaxial axial bores at `±half_len` (upstream barrel face) mating with the rod's `engagement` band (downstream face on the rod). The pin joints anchor on the two jaw lug pads.

## 每槽位 Module Emits / Interfaces

### Slot A / module `closed_cylindrical_barrel`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spindle` (hidden internal scaffold, one narrow cylinder), `barrel` (visible rotating body) | `004.model.py:L109-L160, L242-L291` |
| internal joints | `barrel_rotation` REVOLUTE +X (parent=spindle, child=barrel, `MatingContract` spindle.threaded_core ↔ barrel.barrel_shell, contact_tol 0.4 mm; captured overlap declared as bearing land) | `004.model.py:L434-L448` |
| upstream interface | root (world) | root |
| downstream interface | left face at `(-half_len, 0, 0)` -X; right face at `(+half_len, 0, 0)` +X; both `visual_name=barrel_shell`; keyed `axial_bore_28mm` (family key so both rods must be compatible) | 004 barrel bore |

### Slot A / module `closed_faceted_barrel`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spindle`, `barrel`; barrel decorated with `center_mark` (④ inline visual) | `002.model.py:L74-L91, L163-L195` |
| internal joints | `barrel_rotation` REVOLUTE +X with hidden-spindle-bearing idiom | `002.model.py:L233-L247` |
| upstream interface | root | root |
| downstream interface | same as `closed_cylindrical_barrel` (two coaxial +X/-X faces, `barrel_shell` visual) | 002 barrel bore |

### Slot A / module `open_box_barrel`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `barrel` only (barrel-is-root idiom; visible open frame with polygonal end sockets) | `003.model.py:L53-L73, L136-L144` |
| internal joints | none (root); `barrel_rotation` here becomes the joint FROM barrel to left_fitting (rotational) — actually source 003 uses jaw_fitting_0 as root, so we invert to: barrel is root, left fitting REVOLUTE +X for `barrel_rotation`. For consistency across candidates, this module registers as root and the `barrel_rotation` semantic is folded into the `left_adjustment` chain (see §9 gating). To keep uniform joint semantics, this module additionally emits a hidden `spindle` scaffold as in the closed variants. | `003.model.py:L170-L186` |
| upstream interface | root | root |
| downstream interface | two coaxial faces `barrel_shell=open_frame`, both `+X` / `-X` bores in the polygonal end sockets | 003 sockets |

### Slot A / module `open_forged_oval_barrel`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spindle`, `barrel`; barrel decorated with `upper_pad` / `lower_pad` (④ inline visuals from source) | `001.model.py:L72-L111, L161-L175` |
| internal joints | `barrel_rotation` REVOLUTE +X (hidden-spindle idiom for uniformity) | `001.model.py:L204-L218` |
| upstream interface | root | root |
| downstream interface | two coaxial faces on the left/right bosses along +X/-X; `barrel_shell=open_barrel` visual | 001 bosses |

### Slot B/C / module `hook_end`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `end_fitting_<side>` (one part: rod_core + shoulder + engagement band + hook_fitting visuals) | `004.model.py:L163-L186, L293-L364` |
| internal joints | none | — |
| upstream interface | `engagement` band + `rod_core` cylinder ride in the barrel bore; single face at `(±half_len ∓ engagement_len/2, 0, 0)` mated to `barrel_shell`; PRISMATIC ±X `<side>_adjustment` (parent=barrel, child=fitting) | 004 `hook_adjustment` |
| downstream interface | none (end of chain) | — |

### Slot B/C / module `eye_end`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `end_fitting_<side>` (rod_core + shoulder + engagement + eye_fitting) | `001.model.py:L47-L69` + `004.model.py:L189-L212` |
| internal joints | none | — |
| upstream interface | same as `hook_end` (engagement in barrel bore); PRISMATIC ±X | — |
| downstream interface | none | — |

### Slot B/C / module `jaw_end`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `end_fitting_<side>` (rod + neck + bridge + 2 lugs); `<side>_pin` (clevis pin captured through lug bores) | `002.model.py:L94-L124` + `003.model.py:L76-L108` |
| internal joints | `<side>_fitting_pin` REVOLUTE +Y (parent=end_fitting_<side>, child=<side>_pin, captured overlap declared) | `002.model.py:L278-L292` + `003.model.py:L203-L232` |
| upstream interface | same as `hook_end` (engagement in barrel bore); PRISMATIC ±X | — |
| downstream interface | none | — |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `barrel_form` | enum | `{closed_cylindrical, closed_faceted, open_box, open_forged_oval}` | — | choice | procedural sampler | Slot A table |
| `end_left` | enum | `{hook, eye, jaw}` | — | choice | procedural sampler | Slot B table |
| `end_right` | enum | `{hook, eye, jaw}` | — | choice | procedural sampler | Slot C table |
| `lock_count` | int | `{0, 1}` | 0 | choice | weighted procedural sampler | multiplicity axis |
| `palette_style` | enum | `{zinc_bright, galvanized_matte, forged_dark, painted_red, bronze_patina}` | `zinc_bright` | choice | procedural sampler | §8.5 ⑥ |
| `barrel_length` | float | `[0.100, 0.170]` m | 0.145 | independent | uniform in range then clamp | 001/002/003/004 |
| `barrel_radius` | float | `[0.0075, 0.014]` m | 0.010 | independent | uniform + clamp | 001/002/003/004 |
| `rod_core_radius` | float | derived | 0.0033 | equation | `= 0.30 · barrel_radius` (rod inside bore) | 001/002/004 |
| `engagement_len` | float | derived | 0.028 | equation | `= 0.20 · barrel_length` | 001/002/003/004 |
| `rod_travel` | float | derived | 0.012 | equation | `= min(0.014, 0.60 · engagement_len)` (keep threaded engagement at full travel) | 004 hook_adjustment upper |
| `end_length` | float | `[0.028, 0.050]` m | 0.035 | independent | uniform + clamp; feeds hook loop / eye ring / jaw fork length | 001/002/003/004 |
| (—) | constraint | — | — | inequality | `rod_core_radius + 0.001 ≤ barrel_bore_radius ≤ barrel_radius − 0.001` (bore clearance) | derivation |
| (—) | constraint | — | — | inequality | `engagement_len − rod_travel ≥ 0.010` (min residual engagement at max travel) | 002/003 test_report |
| (—) | constraint | — | — | inequality | overall length `L_total = barrel_length + 2·end_length ≤ 0.38 m` (mesh budget) | budget |

`config_from_seed` follows the connect-the-dots contract: sample independent scales first, derive equations, project into inequalities (shrink `end_length` if L_total overshoots; shrink `rod_travel` if engagement thin). No `curated`/`modulo` fallback for the main domain.

### 7.5 编译预算 / compile budget

Target ≤ 22 s per seed (typical closed-barrel seed 12–16 s; open_forged_oval + two jaw_ends worst case ~20 s). Rationale: 4 cadquery meshes per seed (barrel + 2 rods + up to 2 pins), all with `tolerance ≥ 0.0003 m`; hook polyline reused as a single `tube_from_spline_points` mesh; jaw fork and eye ring extruded with `polygon(8..12)` or ellipse boundary (no boolean-heavy sculpting). Small features (threads) capped at ≤32 axial segments; barrel outer polygon capped at 12 sides; hook radial ≤12 seg. Every seed shares one thread-crest `Mesh` instance per rod when possible.

## Multiplicity / Copy Logic

- `count_param = lock_count`; `N_range = {0, 1}`; sampling weights `(0.55, 0.45)` (paired lock nuts are common but not universal in source photographs).
- Copied object: `lock_nut_<side>` inline visual (a short hexagonal prism at rod shoulder). Naming: `lock_nut_left`, `lock_nut_right`. Placement: at the rod shoulder just outside the barrel end collar. Joint policy: none (Rule 1 non-articulated hardware). Source/gating: from `rec_0611_turnbuckle_var_lock_paired_lock_nuts`; gated to `1` only when both ends have adjustable rods (skipped when either end uses a fixed rod).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 3 root part sets: (barrel + 2 fittings) / (barrel + 2 fittings + 2 pins) / (spindle + barrel + 2 fittings + optional pins). Jaw end adds a REVOLUTE clevis-pin edge. `hook_end` / `eye_end` contribute the "no pin" skeleton, `jaw_end` contributes the "captured pin" skeleton. All source-backed: 001/002/003/004 + P2 hook_hook / hook_jaw / swivel_ends variants. |
| └ multiplicity | 同构件 ×N | 有 | See §8: `lock_count ∈ {0, 1}`, sampled `(0.55, 0.45)`. |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | REVOLUTE +X on `barrel_rotation` (always); PRISMATIC ±X on `<side>_adjustment` (always for adjustable ends); REVOLUTE +Y `<side>_fitting_pin` (only when `jaw_end` chosen for that side). Source-backed: 002/003 pin joints + 004/001 rod adjustments. |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型 | 有 | Barrel: `closed_cylindrical` (Volumetric Envelope Form — round axisymmetric closed body) / `closed_faceted` (Volumetric Envelope Form — polygonal-flat closed body) / `open_box` (Macro Surface Construction — rectangular open frame w/ window) / `open_forged_oval` (Macro Surface Construction — tapered forged frame w/ elongated window). Ends: `hook` (Planar Boundary Form — open loop projection) / `eye` (Planar Boundary Form — closed elliptical loop) / `jaw` (Volumetric Envelope Form — bifurcated fork w/ lugs). All source-backed; `form_subtype` per candidate annotated in §4. Registered into `slot_choices`. |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 | Thread crest ripples on both rods (all origins). Barrel: polished collar bands (004), inspection window (001/003), center inspection mark (002), upper/lower forged pads (001). Lock-nut hex prism when `lock_count=1` (`rec_0611_turnbuckle_var_lock_paired_lock_nuts`). All host-conformal: thread crests wrap the rod at `rod_core_radius + 0.0006`; collar bands wrap the barrel at `barrel_radius + 0.0004`; pads sit tangent to the barrel outer envelope. Derivation order ③→⑤→④. |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | `barrel_length ∈ [0.100, 0.170]`, `barrel_radius ∈ [0.0075, 0.014]`, `end_length ∈ [0.028, 0.050]`. Motion envelopes: **barrel_rotation** REVOLUTE +X, `[-π, +π]` (spin about own axis; source 001/002/003/004; no envelope collision — motion is on-axis rotation, `qc_samples={-π, -π/2, 0, +π/2, +π}` via defaults). **left_adjustment / right_adjustment** PRISMATIC ∓X/+X, `[0, rod_travel]` with `rod_travel ≤ 0.014` and residual engagement `engagement_len − rod_travel ≥ 0.010` (source 002/004). **fitting_pin** REVOLUTE +Y, `[-π, +π]` continuous-in-practice (pin free to spin in fork; source 002/003). `motion_test_plan`: (a) sampled collision `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)`; (b) targeted `ctx.pose({barrel_rotation: π/2})` — barrel rotates in place; (c) targeted `ctx.pose({left_adjustment: rod_travel, right_adjustment: rod_travel})` — both rods extend outward with residual engagement in barrel via `expect_overlap`; (d) when jaw ends, `ctx.pose({<side>_fitting_pin: π/2})` — pin swept through fork. Element-scoped `allow_overlap` for: (i) rod engagement band inside barrel bore; (ii) captured clevis pin through lug pad + fork lugs. |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | `palette_style` ≥ 5: `zinc_bright` (bright galvanized 004), `galvanized_matte` (matte zinc 001), `forged_dark` (dark forged 002), `painted_red` (red-oxide/painted alt), `bronze_patina` (aged bronze alt). All are metal-family painted/plated — one material family (metal) covered by ≥ceil(0.5×5)=3 distinguishable finish states (bright metal, matte metal, painted). Each style provides `body`, `rod`, `pin`, `thread_crest`, `accent`, `lock_nut` colors. |

## 采样与覆盖审计

总组合数：`barrel_form (4) × end_left (3) × end_right (3) × lock_count (2) = 72` structural × `palette_style (5)` = 360. Excluded illegal combos: none — all end pairs mate cleanly (both ends parent to barrel via independent PRISMATIC joints; lug pin geometry doesn't collide with either barrel form).

理由：Turnbuckle is a mature standardized product with a small combinatorial space; realistic catalogues stock every end combination on every barrel style. 72 structural combos comfortably exceeds the 36-seed sweep + corner stage.

seed_domain_policy：`procedural_first`.

Procedural Sampling / Sweep Plan: `config_from_seed(seed)` seeds a `random.Random(seed)` and independently draws `barrel_form`, `end_left`, `end_right`, `lock_count`, `palette_style` (uniform); then draws continuous scales; then `resolve_config` derives dependent values and enforces inequalities. `slot_choices_for_seed(seed)` returns `(('barrel_form', <value>), ('end_left', <value>), ('end_right', <value>), ('lock_count', f'n{lock_count}'), ('palette_style', <value>))`. No regression overrides in the initial version. Sweep: seeds 0–15 fast, 0–35 final, corner stage per pipeline. Viewer inspection at seeds 0-9.

Topology target: 72 slot-tuple combos; 1000-seed probe will saturate near 100% given uniform sampling. Report-only.

Controlled local parameterization: `barrel_length`, `barrel_radius`, `end_length` (independent continuous scales). Derived: `rod_core_radius`, `engagement_len`, `rod_travel`. Inequality-clamped in `resolve_config` before builder.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | uniform per axis; `random.Random(seed)` per call | `slot_choices_for_seed` matches build choices |
| compatibility matrix | all combinations legal; both rod adjustments always PRISMATIC; pin joints only when jaw_end | no floating, no closed-pose collision, joint axis correct |
| controlled local variation | continuous scales as declared in §7; clamped in `resolve_config` | proportions vary; identity + engagement always retained |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial pass + corner; 0-999 later maturity audit | contract failures; `axis_realization` per slot |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| barrel_form | 4 | yes | yes | 2 closed + 2 open |
| end_left | 3 | yes | yes | hook/eye/jaw |
| end_right | 3 | yes | yes | hook/eye/jaw |
| lock_count | 2 | yes | no | multiplicity axis (2 states legitimate) |

### End-compatibility matrix (topology audit)

Rows = end_left; cols = end_right. All combinations legal (both ends only interact with the barrel, never with each other, and neither penetrates the other physically).

|            | hook_right | eye_right | jaw_right |
|------------|------------|-----------|-----------|
| hook_left  | legal      | legal     | legal     |
| eye_left   | legal      | legal     | legal     |
| jaw_left   | legal      | legal     | legal     |

## Validator

- `slot_choices_for_seed` returns implemented module names for every seed 0..35.
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds; `seed=0` not special.
- No illegal combinations — every legal end pair mates cleanly on any barrel.
- No regression overrides.
- Final templates do not endlessly cycle a small curated table as the main seed domain.
- Controlled continuous scales are clamped in `resolve_config` and cannot break engagement, joint origin (barrel_rotation axis is +X at (0,0,0); rod adjustments at `(±half_len, 0, 0)`; pin joints at lug pad centers), or category identity.
- Cross-part scale dependencies (`equation` / `inequality`) are resolved in `resolve_config`, not left to fail in builder.
- Critical InterfaceSpec / MatingContract points: barrel bore ↔ rod engagement (both ends); jaw lug pad ↔ pin head/keeper (jaw ends only). Every non-FIXED joint has a `MatingContract` between explicit named visuals; captured-pin overlaps declared element-scoped.
- Key joints: `barrel_rotation` REVOLUTE +X `[-π, +π]`; `left_adjustment` PRISMATIC -X `[0, rod_travel]`; `right_adjustment` PRISMATIC +X `[0, rod_travel]`; `<side>_fitting_pin` REVOLUTE +Y `[-π, +π]` (jaw only).
- Copied lock_nut visuals follow `lock_nut_<side>` naming; two per active count.

## Reject cases

- Barrel and rod detached (bore-clearance inequality violated → gap along barrel normal axis; caught by `fail_if_joint_mating_has_gap` and `expect_overlap`).
- Rod travel exceeds engagement (rod pops out of barrel at max q → `expect_overlap` on engagement band fails at `q=upper`).
- Jaw pin escaping lugs (captured-pin overlap declared but pin head outside lug pad footprint → `fail_if_parts_overlap_in_sampled_poses` at `pin_spin=π/2` fails).
- Hook loop polyline crossing rod core (self-collision inside `end_fitting_<side>` → `warn_if_part_contains_disconnected_geometry_islands` promoted to fail).
- Barrel rotation axis misaligned (any axis other than +X → `run_turnbuckle_tests` axis check fails).
- Lock-nut floating above rod (`lock_count=1` visual not embedded in rod core → island in end_fitting part → fail).
- Ends silently mismatched sizes so rod core sits proud of barrel bore (single-sourced barrel bore vs rod_core_radius derivation → violated Contract 3c).
- Palette not applied consistently: each seed's palette style must drive every visible visual (fails when material name is not per-style, degrades to hard-coded RGBA).

## 与相邻类别的边界

- 不该混入：**eye_bolt / shackle** — those are single-piece hardware without a rotating adjustment barrel; turnbuckle mandates a rotating middle body with opposed threads.
- 不该混入：**quick_release_clamp** — quick-release couples a hinged lever + captured cam, not opposed screws with a rotating body.
- 不该混入：**pipe_coupling** — union nuts hold two rigid pipes coaxially without axial adjustment travel.
- 不该混入：**chain_link / connecting rod** — chain links are single loops, connecting rods are single-body; neither exposes an in-line rotating adjustment sleeve.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Initial spec; single implementer / auto-authoring. |

## 模板实现备注（可选）

- `hook_end`, `eye_end`, `jaw_end` share a single `_build_rod_core(cfg, side)` helper that builds `rod_core + shoulder + engagement + thread_crests` (three cylinders + procedural thread-crest strip, all inside the `end_fitting_<side>` part). End-specific mesh (hook polyline / eye ring / jaw fork+lugs+pin) is a per-module add-on.
- `closed_cylindrical_barrel` / `closed_faceted_barrel` / `open_forged_oval_barrel` all use a hidden `spindle` scaffold for the barrel_rotation revolute; `open_box_barrel` also uses the same scaffold so joint semantics are uniform across candidates.
- MatingContract for `<side>_adjustment`: parent `barrel.barrel_shell`, child `end_fitting_<side>.rod_engagement`; face_side +X or -X depending on side; `tangential_containment` off (long rail-like PRISMATIC).
- Captured-pin overlaps declared element-scoped: `end_fitting_<side>.pin_hole_pad_i ↔ <side>_pin.pin_shaft`.
- All non-articulated decorations (`center_mark`, `upper_pad`, `lower_pad`, polished collar bands, thread crests, lock nuts) are `parent.visual(...)` (Rule 1).
