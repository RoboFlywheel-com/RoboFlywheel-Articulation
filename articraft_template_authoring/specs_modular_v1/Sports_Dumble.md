# Modular Spec — `dumbbell` (Sports / Dumble)

## 元信息
| 项 | 值 |
|---|---|
| slug | `dumbbell` |
| template path | `agent/templates/Sports_Dumble.py` |
| test path (optional) | `tests/agent/test_dumbbell_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (fixed named slots: handle / plate-shape / collar; with a `multiplicity` axis = plates_per_side N copied per side) |

`pattern` rationale: the dumbbell is a fixed-topology bar (grip in the middle, two mirrored plate stacks, two outboard locking collars). The structural variety comes from swapping the plate-shape module (Slot A), the collar-lock mechanism (Slot B), and the grip form (Slot C), plus one multiplicity axis (N weight plates per side). Plates are mirrored across the x=0 symmetry plane (parallel mirror), and the per-side plate stack is the multiplicity copy. Not a pure linear chain (the two stacks branch off a common body) and not pure parallel_children (it carries a real N-copy axis) → `mixed`.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (2 parents + 7 variants) |
| source_index_policy | only adopted module sources are indexed below |

Sources read (all `revisions/rev_000001/model.py`):
- `rec_adjustable-black-iron-dumbbell-with-stacked-rubb_…e9921a05` (iron parent; CadQuery handle/collars; star-lock collar; asymmetric 3+5 stack)
- `rec_adjustable-chrome-dumbbell-with-stacked-round-st_…e0c0e76a` (chrome parent; SDK-primitive stack; plain spin-lock KnobGeometry nut; symmetric 5+5)
- `rec_dumbbell_var_hexplate` (Slot A: hex prism plate)
- `rec_dumbbell_var_dodecaplate` (Slot A: 12-gon prism plate)
- `rec_dumbbell_var_hexnut` (Slot B: inner fixed + outer spinning hex jam-nut pair)
- `rec_dumbbell_var_contourgrip` (Slot C: ergonomic lathe-revolved barrel grip)
- `rec_dumbbell_var_plates2` (N=2 per side)
- `rec_dumbbell_var_plates4` (N=4 per side)
- `rec_dumbbell_var_plates6` (N=6 per side; lengthened THREAD_LEN to keep collar seat)

## 核心身份

An adjustable-load **dumbbell**: one short knurled steel handle bar lying along +X with its midpoint at the origin, carrying a mirrored stack of removable weight plates on each end, each stack retained by a knurled locking collar/nut threaded onto the exposed bar end just outboard of the plates. Physical function = a hand-held free weight whose load is set by the number of plates and locked by spinning the collars. The only articulation is the two locking collars (CONTINUOUS spin about the bar axis +X); the plates are statically stacked (no joints). Default mature domain = symmetric loadout, round/faceted cast plates, knurled straight grip, plain or star/jam-nut collars. Color/material spans bright chrome, brushed steel, matte-black cast iron, zinc-plated nuts.

Should NOT drift into: barbell/long-bar (much longer shaft, sleeve collars, floor rack — a different category), kettlebell (single cast bell + handle loop, no plate stack), or weight-plate-as-standalone (a single plate is not a dumbbell).

## 槽位 + 候选模块表

### Slot A：plate shape (footprint family)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_plate | rec_adjustable-chrome-…e0c0e76a | L69-L86 (`_plate_stack_geom`) | eligible if compatible | Circular disc via `CylinderGeometry(r, PLATE_THICK)` rotated to +X, gentle per-plate radius taper (`r = PLATE_R - 0.004*i`), raised center hub + embossed rim torus; merged into one per-side `plates_{side}` mesh. Default. |
| hex_plate | rec_dumbbell_var_hexplate | L73-L133 (`_hex_profile` L73-L85 / `_hex_plate_geom` L97-L122 / `_plate_stack_geom` L125-L133) | eligible if compatible | Regular hexagon prism via `ExtrudeWithHolesGeometry(_hex_profile, [bore], thickness)`; flat top/bottom edges so it sits without rolling; center bore + hub + faceted rim ring. Z/Y AABB ratio ≈0.866 (flat-to-flat < corner-to-corner). |
| dodecagonal_plate | rec_dumbbell_var_dodecaplate | L70-L108 (`_dodecagon_profile` L70-L78 / `_plate_stack_geom` L81-L108) | eligible if compatible | 12-gon prism via `ExtrudeGeometry(_dodecagon_profile, PLATE_THICK)`; near-round with faceted edges; dodecagonal hub + 12-segment rim ring. |

### Slot B：plate-locking collar mechanism

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| spinlock_nut | rec_adjustable-chrome-…e0c0e76a | `_collar_geom` L107-L116; collar parts+joints L162-L191 | eligible if compatible | Single knurled `KnobGeometry` nut per side; child part `spinlock_collar_{side}` with off-axis marker box; CONTINUOUS joint `collar_spin_{side}` about +X seated at `COLLAR_X` on the thread. Default. |
| star_lock_collar | rec_adjustable-…iron…e9921a05 | `_collar_solid` L137-L166; `add_collar` L218-L244 | eligible if compatible | Knurled CadQuery nut body + N radiating tapered star/lever finger lobes (`STAR_POINTS=6`) + central cap; child part `left_collar`/`right_collar`; CONTINUOUS joint `body_to_{side}_collar` about +X. Bulkier radial finger silhouette. |
| hex_jamnut_pair | rec_dumbbell_var_hexnut | `_hex_nut_geom` L93-L98; inner (fixed, body visual) L174-L181; outer (jointed) L189-L225 | eligible if compatible | Two stacked 6-sided hex jam nuts per side: inner nut is a fixed body visual (`inner_hex_nut_{side}`), outer nut is the moving part (`outer_hex_nut_{side}`) that spins to jam against the inner; CONTINUOUS joint `nut_spin_{side}` anchored at the **contact face** between the two nuts (`CONTACT_FACE`), not on bare thread. |

### Slot C：handle grip form

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| straight_knurled_bar | rec_adjustable-chrome-…e0c0e76a | grip_core + knurl band L130-L141 | eligible if compatible | Constant-radius `CylinderGeometry` grip core + a `KnobGeometry` knurled band over the middle 62%. Default. (Iron parent equivalent: CadQuery `_knurled_cylinder`/`_handle_solid` L54-L118 — same straight-knurled identity, different toolchain; not a separate candidate.) |
| contoured_ergonomic | rec_dumbbell_var_contourgrip | `_ergonomic_grip_profile` L72-L84; lathe grip + corrugated knurl L150-L177 | eligible if compatible | Barrel/hourglass grip revolved with `LatheGeometry` from a cosine-blended (radius,z) profile (ends `HANDLE_R`, bulge `GRIP_MID_R`); knurl is a continuous corrugated lathe surface following the barrel. Swept radius vs constant radius is the structural diff. |

> Slot C degrades to **2** candidates. Reason: across all 9 sources only two structurally distinct grip forms exist — constant-radius knurled cylinder vs. swept-radius lathe barrel. The iron parent's CadQuery handle is the same straight-knurled topology (just a different build toolchain), so it is not a third candidate. Documented degrade; reviewer to confirm no third grip family is desired before build.

## 槽位图（slot graph）

pattern: mixed (fixed named slots + one multiplicity axis)

```
                         (x=0 symmetry plane, bar along +X)
Slot C (grip / body root)
   └─ Slot A plate stack [×N per side, mirrored ±X]  — FIXED stack, butted to grip shoulder, stacking outward
        └─ Slot B locking collar  --[CONTINUOUS about +X]-->  collar child part
```

- **Root / parent**: `body` (Slot C grip + sleeves + both Slot A plate stacks + threaded ends are all baked into the root `body` part as visuals; Slot B inner jam-nut, if present, is also a `body` visual).
- **Slot C → Slot A interface**: grip-end **shoulder sleeve** at `SLEEVE_X`; the inner plate's inboard face butts against the sleeve at `STACK_START = GRIP_HALF + SLEEVE_LEN`. Plates stack outward along ±X at `PLATE_THICK (+PLATE_GAP)` pitch. Mirror plane = x=0.
- **Slot A → Slot B interface**: the plate stack ends at `STACK_END`; the exposed **threaded bar end** runs from `STACK_END` outward (`THREAD_LEN`). The collar seats on this thread just outboard of the stack:
  - spinlock_nut / star_lock_collar: joint origin at `COLLAR_X = STACK_END + ~0.026` (seated on bare thread; intentional nut↔thread overlap).
  - hex_jamnut_pair: inner nut is fixed at `STACK_END + HEX_THICK/2`; joint origin at `CONTACT_FACE = STACK_END + HEX_THICK` (the inner/outer nut contact plane).
- **Cross-slot joint** (the only articulation): `collar_spin_{side}` / `body_to_{side}_collar` / `nut_spin_{side}`, type **CONTINUOUS**, axis `(1,0,0)`, no limit (free spin), `MotionLimits(effort≈1–2, velocity≈8)`. One per side → 2 joints total, regardless of N.
- Slots are not mutually exclusive; every seed picks exactly one A, one B, one C, and one N. The plate stacks are derived from N (multiplicity), mirrored.

## 每槽位 Module Emits / Interfaces

### Slot A / round_plate (and hex_plate / dodecagonal_plate analogous)
| emits | 描述 | 来源 |
|---|---|---|
| parts | per-side merged visual `plates_{side}` on root `body` (N discs/prisms + hub + rim merged) | chrome L150-L151 / hexplate L198-L199 |
| internal joints | none (plates are FIXED static load) | — |
| upstream interface | inboard face butts against grip shoulder sleeve at `STACK_START` | chrome L57, L74 |
| downstream interface | stack outer face `STACK_END` exposes thread for the collar seat | chrome L59-L61 |

### Slot B / spinlock_nut
| emits | 描述 | 来源 |
|---|---|---|
| parts | child part `spinlock_collar_{side}` = knurled KnobGeometry nut + off-axis marker box | chrome L165-L177 |
| internal joints | `collar_spin_{side}` CONTINUOUS, axis +X, parent=body, no limit | chrome L183-L191 |
| upstream interface | bore seats on threaded bar end; joint origin `(±COLLAR_X,0,0)`; allow_overlap nut↔thread | chrome L188, L255-L274 |
| downstream interface | outermost element (terminal) | — |

### Slot B / star_lock_collar
| emits | 描述 | 来源 |
|---|---|---|
| parts | child part `left_collar`/`right_collar` = knurled nut + 6 radial finger lobes + cap + marker | iron L218-L234 |
| internal joints | `body_to_{side}_collar` CONTINUOUS, axis +X | iron L236-L244 |
| upstream interface | nut threaded on handle end; joint origin at `left/right_collar_x` outboard of last plate; allow_overlap nut↔handle | iron L211-L215, L331-L352 |
| downstream interface | terminal | — |

### Slot B / hex_jamnut_pair
| emits | 描述 | 来源 |
|---|---|---|
| parts | fixed body visual `inner_hex_nut_{side}` + child part `outer_hex_nut_{side}` (hex prism + marker) | hexnut L174-L210 |
| internal joints | `nut_spin_{side}` CONTINUOUS, axis +X, origin at `CONTACT_FACE` (inner/outer contact plane) | hexnut L216-L225 |
| upstream interface | inner nut fixed at `STACK_END + HEX_THICK/2`; outer nut spins against it; allow_overlap outer↔inner contact face | hexnut L64-L67 |
| downstream interface | terminal | — |

### Slot C / straight_knurled_bar
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `body` visuals `grip_core` + `grip_knurl` (KnobGeometry knurl band) | chrome L130-L141 |
| internal joints | none | — |
| upstream interface | n/a (root) | — |
| downstream interface | shoulder sleeves at `±SLEEVE_X` carry the plate stacks | chrome L146-L148 |

### Slot C / contoured_ergonomic
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `body` visuals `grip_core` (LatheGeometry barrel) + `grip_knurl` (corrugated lathe) | contourgrip L150-L177 |
| internal joints | none | — |
| upstream interface | n/a (root) | — |
| downstream interface | shoulder sleeves at `±SLEEVE_X` carry the plate stacks (ends taper to `HANDLE_R` to meet sleeve) | contourgrip L150-L153, L182-L184 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| plate_shape | enum | {round_plate, hex_plate, dodecagonal_plate} | round_plate | choice | deterministic procedural sampler | Slot A table |
| collar_lock | enum | {spinlock_nut, star_lock_collar, hex_jamnut_pair} | spinlock_nut | choice | deterministic procedural sampler | Slot B table |
| grip_form | enum | {straight_knurled_bar, contoured_ergonomic} | straight_knurled_bar | choice | deterministic procedural sampler | Slot C table |
| plates_per_side | int | [1, 8] product / {2,4,5,6} test samples | 5 | conditional | multiplicity count; weighted (small N higher prob); see §Multiplicity | chrome L44 / plates2/4/6 |
| palette_style | enum | {bright_chrome, brushed_steel, matte_black_iron, zinc_plated, gunmetal_cast, polished_dumbbell} | bright_chrome | choice | sampled per seed; maps material rgba sets | observed materials (below) |
| plate_radius_scale | float | [0.85, 1.15] | 1.0 | independent | scales `PLATE_R`; clamp | chrome L41 |
| plate_thick_scale | float | [0.85, 1.15] | 1.0 | independent | scales `PLATE_THICK`; clamp | chrome L42 |
| grip_len_scale | float | [0.85, 1.20] | 1.0 | independent | scales `HANDLE_LEN`/`GRIP_LEN` | chrome L34 |
| grip_mid_r_scale | float | [1.05, 1.45]·HANDLE_R | derived | conditional | only for contoured_ergonomic; `GRIP_MID_R = k·HANDLE_R`; ignored for straight bar | contourgrip L39 |
| stack_len | float | derived | derived | equation | `STACK_LEN = N·PLATE_THICK·plate_thick_scale + (N-1)·PLATE_GAP`; `STACK_END = STACK_START + STACK_LEN` | chrome L57-L59 |
| thread_len | float | derived | derived | conditional | grows with N so collar still seats on exposed thread: `THREAD_LEN ≥ collar_seat + COLLAR_LEN + margin`; plates6 raised it 0.050→0.058 | plates6 L49 |
| collar_seat_x | float | derived | derived | equation | `COLLAR_X = STACK_END + 0.026` (spinlock); `CONTACT_FACE = STACK_END + HEX_THICK` (jamnut) | chrome L61 / hexnut L66 |
| (—) | constraint | — | — | inequality | `COLLAR_X + COLLAR_LEN/2 ≤ STACK_END + THREAD_LEN`: collar must stay on exposed thread, not overhang the bar end; if violated, grow `THREAD_LEN` or reject | 排除项 / hexnut+plates6 notes |
| (—) | constraint | — | — | inequality | plate bore `BORE_R ≥ THREAD_RIDGE_R + clearance` so plates slip over the thread; hub `PLATE_HUB_R < PLATE_R - rim` | hexplate L49 / chrome L46-L48 |

**palette_style colorways** (drawn from materials actually present across the 5★ sources):
- `bright_chrome` — chrome (0.78,0.80,0.83) body + bright_chrome (0.86,0.88,0.90) plates + steel collars (chrome parent default).
- `brushed_steel` — steel (0.66,0.68,0.71) body/plates, dark_steel (0.52,0.54,0.57) knurl band.
- `matte_black_iron` — steel handle + plate_black (0.07,0.07,0.08) plates + collar_steel collars + red index marker (iron parent).
- `zinc_plated` — chrome body + zinc_plated (0.72,0.73,0.70) nuts (hexnut variant nut material).
- `gunmetal_cast` — cast_iron (0.38,0.39,0.41) faceted plates + dark_steel grip (hexplate/dodeca cast material).
- `polished_dumbbell` — all-bright chrome/bright_chrome high-polish set (chrome parent, max-gloss colorway).

## Multiplicity / Copy Logic

One multiplicity axis.

- **count_param**: `plates_per_side` (N).
- **N_range**: product `[1, 8]` per side (real adjustable-dumbbell loadout, capped where bar sleeve/thread length runs out); **test samples** {2, 4, 5, 6} (already covered: plates2 N=2, plates4 N=4, parents N=5, plates6 N=6).
- **sampling domain (weights)**: weighted toward small/medium realistic loadouts — peak around N=2–5, taper N=6–8 rarer; N=1 allowed but downweighted. (Small-N high frequency, tail rare per shared multiplicity policy.)
- **copied object**: one weight plate (shared per-slot plate geometry helper `_plate_stack_geom` / `_single_plate_geom`), emitted `for i in range(N)`.
- **naming**: per-side merged stack `plates_{pos|neg}` (chrome/hex/dodeca pattern) OR individual `{side}_plate_{i}` (iron / plates2 / plates6 pattern). Template should standardize on per-side `plates_{side}` merged-mesh naming for collision/QC simplicity, with the option of `plate_{i}` for individual-plate variants.
- **placement**: linear along the bar axis, pitch `PLATE_THICK + PLATE_GAP`, butted against the grip shoulder sleeve, stacking outward; mirrored across x=0 (default symmetric; iron parent demonstrates an optional asymmetric 3+5 loadout — keep symmetric as default, asymmetric as a gated rare option).
- **joint policy**: plates are **FIXED** to `body` (static load). Multiplicity adds **no joints**; it lengthens the static stack, shifts `STACK_END`, and re-derives the collar seat / thread length. The only non-fixed joints remain the two collars.
- **source/gating**: N is independent of the slot enums **except** the derived thread-length inequality (large N must grow `THREAD_LEN` so the collar still seats on exposed thread; see compatibility matrix).

## 拓扑多样性审计

总组合数：A(3) × B(3) × C(2) = **18** slot combos; × N test-samples (4 distinct: {2,4,5,6}) = **72** topology-distinct configurations (and far more across the full N∈[1,8] product domain).

理由：18 slot combos alone already exceed the 10-distinct floor before multiplicity; adding 4 sampled N values pushes well past it. Slot choices change part/visual/joint structure (plate prism vs disc, single-nut vs jam-nut-pair with an extra fixed inner visual + relocated joint origin, constant vs lathe grip), so distinct-topology counting is satisfied structurally, not just by scale jitter.

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed` deterministically picks (plate_shape, collar_lock, grip_form, plates_per_side, palette_style) via weighted draws, then samples independent scales, derives `STACK_LEN`/`STACK_END`/`thread_len`/collar seat, and projects against the thread-seat inequality. `slot_choices_for_seed` must return the same module names the builder uses. Compatibility gating (below) blocks the one fragile combo (faceted plates × jam-nut contact face) by deriving a real contact face. A handful of regression overrides reserved for the exact N=6 long-stack thread-seat case (the plates6 fix). Random sweep seeds 0–49 for the initial pass, 0–999 for the maturity audit.

Topology target：1000-seed slot choice tuple distinct rich-category guideline ≥300 (report-only) is **not reachable from slots alone** (18 slot combos × N). With the full N∈[1,8] domain (8 values) the ceiling is 18×8 = 144 distinct topologies, plus palette and continuous-scale variation; so ≥300 is achievable across the 1000-seed domain but is dominated by the N axis. Documented: this is a low-slot-cardinality category (a dumbbell is geometrically simple); main diversity = plate shape × collar mechanism × N. This is the category constraint, not a sampler defect.

Controlled local parameterization：`plate_radius_scale` [0.85,1.15] independent; `plate_thick_scale` [0.85,1.15] independent; `grip_len_scale` [0.85,1.20] independent; `grip_mid_r_scale` conditional (contoured grip only); derived `stack_len`/`stack_end`/`collar_seat_x` (equation); conditional `thread_len` (grows with N). All clamped/derived in `resolve_config`; none may break the mirror symmetry, the collar-on-thread seat, the plate-bore-over-thread clearance, or the CONTINUOUS joint axis/origin.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted slot picks (A,B,C) + weighted N (small-N peak) + palette; then scales → derive → project | slot_choices_for_seed matches build choices |
| compatibility matrix | faceted plate × jam-nut: derive real inner/outer contact face (no phantom anchor); large-N: grow thread_len; asymmetric loadout gated rare | no floating plates, collar seated on thread, jam-nut contact face exists, no plate-bore phantom |
| controlled local variation | plate/grip scales clamped; thread_len/stack_end derived | proportions vary without breaking mirror, seat, bore clearance, or joint origin |
| regression overrides | N=6 long-stack thread-seat case (plates6 fix); otherwise none | previously failed seat case only |
| random sweep | seeds 0–49 initial, 0–999 maturity | and contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A (plate shape) | 3 | yes | yes | round / hex / dodeca |
| B (collar lock) | 3 | yes | yes | spinlock_nut / star_lock / hex_jamnut_pair |
| C (grip form) | 2 | yes | no | degraded to 2 (only 2 structural grip families exist) |

## Validator

- slot_choices_for_seed returns implemented module names {round_plate|hex_plate|dodecagonal_plate} × {spinlock_nut|star_lock_collar|hex_jamnut_pair} × {straight_knurled_bar|contoured_ergonomic}
- config_from_seed uses deterministic procedural sampling for all ordinary seeds (slots + N + palette)
- compatibility matrix / gating: faceted-plate × jam-nut derives a real contact face; large-N grows thread_len; no illegal combos
- optional regression overrides sparse and justified (N=6 thread-seat)
- main seed domain is procedural, not a small curated/modulo table
- controlled local scales clamped; cannot break mirror symmetry, collar seat, plate-bore clearance, or joint origin
- cross-part scale dependencies (stack_len/stack_end/thread_len/collar_seat) resolved in resolve_config
- critical interfaces exist: grip-shoulder→stack butt, stack-end→thread→collar seat
- key joints: exactly 2 collar joints, CONTINUOUS, axis (1,0,0), no limit; plates carry NO joints
- copied objects follow naming (`plates_{side}` or `plate_{i}`) and outward-stacking placement; both sides mirrored about x=0

## Reject cases

- Collar joint emitted as REVOLUTE-with-limit or FIXED, or axis not +X → must be CONTINUOUS free-spin about the bar axis.
- More than 2 articulated parts, or plates emitted as separate jointed parts → plates must be FIXED static visuals.
- Collar overhangs the bar end / floats off the thread (large N buried the thread and `THREAD_LEN` was not grown) → violates the seat inequality.
- Plate bore narrower than the thread ridge radius (plates won't slip over the bar) → `BORE_R ≥ THREAD_RIDGE_R + clearance`.
- Jam-nut pair built with a phantom contact pad / no real inner-nut face (faceted-plate combo) → joint origin must be the real inner/outer contact plane.
- Asymmetric loadout produced by default (non-mirrored stacks) without the gated rare path → default must be mirror-symmetric about x=0.
- Plate stack detached from grip (gap at `STACK_START`, inner plate not butted to shoulder sleeve) → floating stack.
- Hub/rim emboss larger than the plate (`PLATE_HUB_R ≥ PLATE_R`) → degenerate plate face.

## 与相邻类别的边界

- 不该混入：barbell / 长杠铃（理由：barbell 是长轴 + sleeve 卡箍 + 落地架，轴长/卡箍机制不同；dumbbell 是短手持杆，midpoint 在 origin）。
- 不该混入：kettlebell（理由：壶铃是单体铸钟 + 提手环，无可拆卸 plate 叠层，无 collar spin 关节）。
- 不该混入：单片 weight plate（理由：一片配重盘不是 dumbbell；缺手柄 + collar 锁紧整体结构）。

## 模板实现备注（可选）

- All three plate-shape modules share the per-side `_plate_stack_geom(sign)` skeleton (hub + rim emboss + N-loop); only the base profile differs (Cylinder vs ExtrudeWithHoles hex vs Extrude dodeca). Factor a `plate_profile(shape, r)` helper.
- `hex_jamnut_pair` is the only Slot B that adds a **fixed body visual** (`inner_hex_nut_{side}`) in addition to the moving part, and relocates the joint origin from `COLLAR_X` (bare thread) to `CONTACT_FACE`. Its overlap allow-list differs (outer↔inner contact, not nut↔thread).
- Element-scoped `allow_overlap` + `expect_overlap` (min_overlap ≈0.004 on x) is required on every collar↔seat pairing — replicate per side and per collar module.
- `contoured_ergonomic` grip requires `LatheGeometry`/`ExtrudeGeometry` imports and a cosine-blend (radius,z) profile; ends must taper to `HANDLE_R` to meet the shoulder sleeve cleanly.
- thread_len derivation must be a function of N (plates6 raised THREAD_LEN 0.050→0.058 for N=6) — bake into resolve_config, not a constant.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Slot C degraded to 2 candidates (only 2 structural grip families in the source pool) — confirm acceptable. Confirm N weighting (small-N peak) and whether asymmetric loadout should remain a gated rare path or be dropped. Topology ≥300 over 1000 seeds is N-dominated (low slot cardinality is inherent to the category). |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | Slot A | round_plate | rec_adjustable-chrome-…e0c0e76a | L69-L86 | plate stack + hub/rim + upstream/downstream interface |
| S2 | Slot A | hex_plate | rec_dumbbell_var_hexplate | L73-L133 | hex prism plate profile + bore + flat-sit |
| S3 | Slot A | dodecagonal_plate | rec_dumbbell_var_dodecaplate | L70-L108 | 12-gon prism plate + faceted hub/ring |
| S4 | Slot B | spinlock_nut | rec_adjustable-chrome-…e0c0e76a | L107-L116, L162-L191 | knurled nut part + CONTINUOUS collar joint |
| S5 | Slot B | star_lock_collar | rec_adjustable-…iron…e9921a05 | L137-L166, L218-L244 | star-finger nut part + collar joint |
| S6 | Slot B | hex_jamnut_pair | rec_dumbbell_var_hexnut | L93-L98, L174-L225 | fixed inner + spinning outer hex nut + contact-face joint |
| S7 | Slot C | straight_knurled_bar | rec_adjustable-chrome-…e0c0e76a | L130-L141 | constant-radius knurled grip |
| S8 | Slot C | contoured_ergonomic | rec_dumbbell_var_contourgrip | L72-L84, L150-L177 | lathe barrel grip + corrugated knurl |
| S9 | multiplicity | plates_per_side | rec_dumbbell_var_plates2/4/6 | plates6 L44-L58, L148-L149; plates2 L44, L150 | N copy logic + thread_len growth with N |
