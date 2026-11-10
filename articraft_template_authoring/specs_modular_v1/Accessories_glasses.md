# glasses — Modular Spec (SPEC_ONLY)

## 元信息
| 项 | 值 |
|---|---|
| slug | `glasses` |
| 大类/小类 | `Accessories/glasses` (eyewear) |
| source map | `articraft_data/picture_expansion/template_source_maps/Accessories__Accessories_glasses.md` |
| parent A (001.png) | `rec_create-a-highly-detailed-articulated-3d-model-of_20260620_143104_211959_619782b5` ← `picture/Accessories/glasses/001.png` (silver aviator **sunglasses**, tinted/amber lens) |
| parent B (002.png) | `rec_create-a-highly-detailed-articulated-3d-model-of_20260620_143104_209562_7e979b64` ← `picture/Accessories/glasses/002.png` (dark browline / clubmaster **sunglasses**) |
| template path | `agent/templates/Accessories_glasses.py` |
| test path (optional) | `tests/agent/test_glasses_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (front frame is root; bridge/nose detail + two mirrored temple chains hang off it) |

> Provenance note: the source map labels parent B (002.png) as "clear eyeglasses", but its actual `prompt.txt` and `model.py` build dark **clubmaster sunglasses** with smoky translucent lenses (`smoky_lens`, alpha 0.55). Both reference parents are sunglasses; the category is general eyewear and `palette_style` (§7) carries the clear/tinted variation, NOT a separate slot. Lens tint is a material axis, not topology.

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (2 parents + 8 named variants) |
| source_index_policy | only adopted module sources are indexed below |

**Shared structure (all 10).** Every sample is a root `front_frame` (or `frame_front`) part that carries the rim/brow + bridge + nose support + two hinge mounts, plus **two separate mirrored `temple_{side}` parts** joined to the front by **REVOLUTE fold joints** (the core articulation). Lenses are either separate FIXED-jointed parts or front-frame visuals. side_count is always 2 (left/right), never a variable multiplicity. Both reference parents and all variants fold the temples through ≈95° about a vertical (+Z) axis at the outer-top hinge.

**Two SDK lineages (important for the future template).** The samples split into two coexisting authoring styles that the template must unify under ONE coordinate convention:

- **Lineage A — cadquery / browline.** Sources: parent B (209562), `round_wire_rims`, `qwen_hexagonal_lenses`, `qwen_oval_panto_lenses`, `keyhole_bridge`, `spring_hinges`. Convention: `+Y`=wearer's left, `-Y`=right, `+X`=back-toward-ears (lens plane at X≈0), `+Z`=up. Lenses are **separate parts** (`lens_right`/`lens_left`) FIXED to `frame_front`; temple authored in local +X and folds about ±Z. Materials: `glossy_gunmetal` brow/temple, `smoky_lens`, `polished_metal` rim/hinge.
- **Lineage B — geometry-primitive / aviator.** Sources: parent A (211959), `cat_eye_frame`, `wraparound_shield`, `thick_sport_temples`. Convention: `+X`=wearer's right, `+Y`=forward (lenses face +Y), `+Z`=up; temple authored along local +X, joint origin has `rpy=(0,0,-90°)` so the open arm points world `-Y`. Lenses are **front-frame visuals** (`lens_{side}`), rims are continuous bent tubes (`tube_from_spline_points`), bridge is a double bar + struts, nose pads on curved stems. Materials: `polished_silver`, `black_bezel`, `amber_lens` (translucent), `black_acetate`/`rubber_grip`.

**Per-source differences (the structural axes).**
- Front rim/lens shape (Slot A): rounded-rect/browline (B), rectangular silver rims (A), cat-eye upsweep, round wire torus, one-piece wraparound shield, hexagonal, oval panto. Differences are in the lens outline point set + rim path + (shield) lens-count.
- Bridge/nose (Slot B): simple bridge + retained nose support (both parents) vs keyhole bridge with saddle cutout replacing the nose pads.
- Temple/hinge (Slot C): plain folding temples (both parents) vs spring-hinge with an added flex-link **intermediate part + extra revolute** (chain depth 2, 4 revolute joints) vs thick rubber-tipped sport temples.

## 核心身份

Eyewear: a head-worn front frame holding **two lenses** (or one continuous shield), supported on the nose by a **bridge + nose pads / saddle**, with **two temple arms that fold via revolute hinges** at the outer-top corners of the front frame. The defining articulation is the symmetric pair of temple-fold revolute joints; a glasses model with no folding temple is not eyewear. Total frame width ≈0.12–0.15 m; lenses translucent or tinted; rims/temples metal or acetate.

Default mature domain: a single front frame (root) + 2 lenses (or 1 shield) + bridge/nose support + 2 mirrored temple chains, each chain ending in a down-curled ear tip. Lens tint ranges clear→smoky→amber→black (palette axis, not a slot).

Neighbor boundary: NOT goggles (strap + sealed eyecups, no folding temple), NOT a face mask/visor (no per-eye lenses), NOT a magnifying handle/lorgnette (single handle, no temples), NOT a VR headset (head strap + display housing). The folding-temple pair + per-eye (or shield) lens front is what makes it THIS object.

## 槽位 + 候选模块表

### Slot A：front lens / rim shape

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rectangular_clear_rims (aviator rims) | rec_..._143104_211959_619782b5 (parent A) | L48-L65 (`_rounded_square_loop`), L75-L115 (rim/bezel/lens build) | eligible if compatible | rounded-square silver rim tube + black bezel + translucent lens disk, 2 separate rims |
| sport_front_frame (browline brow) | rec_..._143104_209562_7e979b64 (parent B) | L56-L72 (`_lens_profile_wire`), L125-L183 (`build_frame_front` brow+bridge), L91-L108 (`build_lower_rim`) | eligible if compatible | chunky glossy brow bar + thin lower half-rims, 2 rounded-rect smoky lenses |
| cat_eye_frame | rec_glasses_var_cat_eye_frame | L52-L98 (`_cateye_loop`), L108-L146 (rim/bezel/lens), L466-L503 (cat-eye shape asserts) | eligible if compatible | upswept outer-upper corner via Gaussian bump on ellipse; rim+lens follow same loop |
| round_wire_rims | rec_glasses_var_round_wire_rims | L65-L75 (`build_rim` torus), L78-L91 (`build_lens` circle), L94-L103 (`build_bridge`) | eligible if compatible | full circular wire rim (TorusGeometry rotated to X-axis) + circular lens disk |
| wraparound_shield | rec_glasses_var_wraparound_shield | L75-L92 (shield+brow assembly), L308-L403 (`_shield_lens_geometry`) | eligible if compatible | ONE continuous curved shield lens spanning both eyes + shallow brow bar; NO per-eye rims |
| hexagonal_lenses | rec_glasses_var_qwen_hexagonal_lenses | L56-L66 (`_lens_outline_points` hex), L100-L106 (`build_lens_rim` straight-edge), L83-L97 (`build_lens`) | eligible if compatible | crisp 6-edge hexagonal lens + full outline-matched straight-segment rim |
| oval_panto_lenses | rec_glasses_var_qwen_oval_panto_lenses | L56-L75 (`_lens_outline_points` panto), L103-L111 (`build_lens_rim` spline), L87-L100 (`build_lens`) | eligible if compatible | soft oval panto outline (fuller lower curve) + full spline rim |

### Slot B：bridge / nose structure

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| standard_bridge | rec_..._143104_209562_7e979b64 (parent B) | L167-L183 (brow+bridge union), L198-L215 (`build_nose_pad`) | eligible if compatible | short bridge connector between rims + 2 separate nose pads on thin stems (lineage-A form) |
| standard_bridge (aviator double-bar form) | rec_..._143104_211959_619782b5 (parent A) | L117-L143 (double bridge bars+struts), L145-L174 (nose stems+pads) | eligible if compatible | twin horizontal bars + 2 vertical struts + curved nose stems/pads on rear (-Y) face |
| keyhole_bridge | rec_glasses_var_keyhole_bridge | L178-L257 (`build_keyhole_bridge` block+saddle cutout), L130-L163 (`build_brow_bar`, bridge removed) | eligible if compatible | keyhole-shaped bridge solid with circular+slot saddle cutout; **replaces** the separate nose pads |

### Slot C：temple arm / hinge mechanism

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| folding_temples | rec_..._143104_209562_7e979b64 (parent B) | L218-L270 (`build_temple_arm`), L356-L394 (2 revolute hinges) | eligible if compatible | slim flat tapered temple + ear-hook tip, 1 revolute fold per side (2 total), captured-knuckle hinge |
| spring_hinges | rec_glasses_var_spring_hinges | L184-L228 (`build_spring_barrel`), L231-L272 (`build_flex_link`), L436-L517 (flex_link parts + 4 revolute joints) | eligible if compatible | **adds intermediate `flex_link` part + extra spring revolute (0-20°)**; chain depth 2; frame→flex→temple = 4 revolute joints |
| thick_sport_temples | rec_glasses_var_thick_sport_temples | L191-L268 (thick arm + broad rubber ear tip + fold joint), L38-L39 (sport materials) | eligible if compatible | thick rounded-rect sport arm + broad rubberized down-curled ear tip; 1 revolute fold per side |

## 槽位图（slot graph）

pattern: `parallel_children`

```
              front_frame (root part; rim/brow + bridge + nose + 2 hinge mounts)
                 │  │  │
   [Slot A geometry baked into front_frame visuals + 2 lens children]
                 │  │  │
   ┌─────────────┘  │  └─────────────┐
   │ FIXED          │ (Slot B detail │ FIXED
   ▼ (lens mate)    │  on front)     ▼ (lens mate)
 lens_left      [Slot B: bridge/    lens_right
                 nose / keyhole]      (or single shield_lens visual on front_frame
                                       when Slot A = wraparound_shield)

 front_frame ─[REVOLUTE fold_left  : axis ±Z, origin = left hinge,  range 0–95°]→ temple_left
 front_frame ─[REVOLUTE fold_right : axis ±Z, origin = right hinge, range 0–95°]→ temple_right

   (Slot C = spring_hinges inserts an intermediate part per side:)
 front_frame ─[REVOLUTE spring_{side}: axis ±Z, range 0–20°]→ flex_link_{side}
 flex_link_{side} ─[REVOLUTE fold_{side}: axis ±Z, range 0–95°]→ temple_{side}
```

Interfaces / mating:
- **Slot A → front_frame**: Slot A owns the rim/brow visuals + lens outline. Lenses are FIXED to the front (lineage A) or are front_frame visuals (lineage B); the template normalizes to FIXED lens children for QC consistency. Mating = the lens sits in the rim opening at the lens plane; rim outline overlaps lens footprint (`expect_overlap axes=y/x, min_overlap≈0.01`).
- **Slot A ↔ Slot B**: bridge spans the inner edges of the two rims (gap ≈ `LENS_GAP`); nose support hangs below/behind the bridge. wraparound_shield removes the gap (one shield) → Slot B degrades to internal nose support only (see compatibility matrix).
- **Slot A/B → Slot C hinge mount**: hinge block / spring barrel sits at the outer-top rim corner (`HINGE_Y, HINGE_Z`); the temple knuckle (or flex-link boss) is captured inside it (`allow_overlap`, element-scoped). This is the pivot interface for the fold joint.
- **Slot C internal**: fold revolute axis = vertical (±Z), origin at the hinge mount, range 0–95°; mirrored sign of axis per side so positive q folds inward. spring_hinges adds one upstream small-range revolute through `flex_link`.

Exclusivity / derivation:
- wraparound_shield (Slot A) gates Slot B to a fixed internal nose-support form (no separate per-eye rims, no keyhole saddle as primary).
- spring_hinges (Slot C) is the only candidate that changes chain depth / joint count; it is independent of Slot A and Slot B.

## 每槽位 Module Emits / Interfaces

### Slot A / module rectangular_clear_rims (aviator)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `rim_{side}` tube, `bezel_{side}` ring, `lens_{side}` domed disk (front_frame visuals) | parent A / L75-L115 |
| internal joints | none (rims/lenses rigid on front) | parent A / L73-L115 |
| upstream interface | front_frame root; rim centers at `±RIM_CENTER_X` | parent A / L42-L44 |
| downstream interface | outer-top rim corner → hinge mount for Slot C; inner edge → Slot B bridge | parent A / L176-L186 |

### Slot A / module sport_front_frame (browline brow)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `brow_bar` (glossy brow+bridge solid), `lower_rim_{side}`, separate `lens_{side}` FIXED parts | parent B / L125-L183, L91-L108, L329-L354 |
| internal joints | `frame_to_lens_{side}` FIXED (lens mate) | parent B / L341-L354 |
| upstream interface | front_frame root; lens centers at `±LENS_CX` | parent B / L40 |
| downstream interface | brow outer-top corner → hinge; bridge in brow → Slot B | parent B / L167-L183 |

### Slot A / module wraparound_shield
| emits | 描述 | 来源 |
|---|---|---|
| parts | single `shield_lens` visual (spans both eyes) + `brow_frame` silver bar | variant / L75-L92, L308-L403 |
| internal joints | none | — |
| upstream interface | front_frame root; shield total_half_w ≈ `RIM_CENTER_X+RIM_HALF_W` | variant / L313-L316 |
| downstream interface | brow ends → hinge mounts; **no rim gap** → Slot B forced to internal nose support | variant / L94-L164 |

### Slot A / modules cat_eye / round_wire / hexagonal / oval_panto
| emits | 描述 | 来源 |
|---|---|---|
| parts | per-eye `rim_{side}` (loop/torus) + `lens_{side}` following the same outline | cat_eye L108-L146; round_wire L65-L91; hex L100-L106,L83-L97; panto L103-L111,L87-L100 |
| internal joints | round_wire/hex/panto: `frame_to_lens_{side}` FIXED; cat_eye: lens is front visual | round_wire L253-L259; hex L354-L367 |
| upstream interface | rim outline point set parameterizes lens + rim together | each module's `_*_loop`/`_lens_outline_points` |
| downstream interface | outer-top corner → hinge; inner edge → bridge | shared |

### Slot B / module standard_bridge
| emits | 描述 | 来源 |
|---|---|---|
| parts | bridge bar(s) (+ struts in aviator form) + `nose_pad_{side}` (+ `nose_stem_{side}`) | parent B L167-L215; parent A L117-L174 |
| internal joints | none (rigid on front) | — |
| upstream interface | spans rim inner edges across `LENS_GAP`; overlaps both rims for connectivity | parent A L118-L120 |
| downstream interface | nose pads sit on rear (-Y, lineage B) / front-below (lineage A) for nose contact | parent A L145-L174 |

### Slot B / module keyhole_bridge
| emits | 描述 | 来源 |
|---|---|---|
| parts | `keyhole_bridge` solid with circular+slot saddle cutout (NO separate nose pads) | variant / L178-L257 |
| internal joints | none | — |
| upstream interface | overlaps brow_bar vertically (Z) for connectivity; spans `LENS_GAP` | variant / L185-L204, L564-L569 |
| downstream interface | saddle cutout is the nose contact (replaces pads) | variant / L206-L256 |

### Slot C / module folding_temples
| emits | 描述 | 来源 |
|---|---|---|
| parts | `temple_{side}` flat tapered arm + ear-hook + hinge knuckle | parent B / L218-L270 |
| internal joints | `fold_{side}` REVOLUTE, axis ±Z, origin hinge, range 0–95° (2 total) | parent B / L356-L394 |
| upstream interface | knuckle captured inside `hinge_block_{side}` (element-scoped allow_overlap) | parent B / L417-L430 |
| downstream interface | ear tip free end (down-curled) | parent B / L250-L262 |

### Slot C / module spring_hinges
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spring_barrel_{side}` (front visual) + `flex_link_{side}` intermediate part + `temple_{side}` | variant / L184-L228, L231-L272, L439-L450 |
| internal joints | `{side}_spring` REVOLUTE (frame→flex, 0–20°) **and** `{side}_hinge` REVOLUTE (flex→temple, 0–95°) → 4 revolute total | variant / L455-L517 |
| upstream interface | flex boss captured in barrel; temple knuckle captured in flex (2 element-scoped allow_overlap per side) | variant / L544-L572 |
| downstream interface | ear tip free end | variant / L295-L347 |

### Slot C / module thick_sport_temples
| emits | 描述 | 来源 |
|---|---|---|
| parts | thick `arm_{side}` (sport_temple matte) + broad `ear_tip_{side}` (rubber_grip) | variant / L191-L233 |
| internal joints | `fold_{side}` REVOLUTE, axis ±Z, origin hinge, range 0–95° (2 total) | variant / L259-L268 |
| upstream interface | arm root at hinge mount (yaw -90° so open arm points -Y) | variant / L251-L257 |
| downstream interface | broad down-curled rubber ear tip | variant / L219-L233 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| front_shape (Slot A) | enum | rectangular_clear_rims / sport_front_frame / cat_eye_frame / round_wire_rims / wraparound_shield / hexagonal_lenses / oval_panto_lenses | — | choice | deterministic procedural sampler | Slot A table |
| bridge_style (Slot B) | enum | standard_bridge / keyhole_bridge | — | choice | sampler; gated by Slot A (see matrix) | Slot B table |
| temple_style (Slot C) | enum | folding_temples / spring_hinges / thick_sport_temples | — | choice | deterministic procedural sampler | Slot C table |
| palette_style | enum | clear_acetate / tortoise / matte_black / smoky_tint / amber_tint / silver_metal | smoky_tint | choice | sampler; ≥3 colorways (see below) | materials across all 10 sources |
| lens_half_w | float | [0.024, 0.030] | 0.0265 | independent | clamp; one lens half-width | parent A L39 / parent B L37 |
| lens_half_h | float | derived | 0.0235 | equation | `= lens_half_w * aspect`, aspect∈[0.82,1.0] (round_wire→1.0) | parent A L40 / round_wire L41-L43 |
| lens_gap | float | [0.014, 0.022] | 0.018 | independent | clamp; bridge span | parent B L39 |
| rim_center_x | float | derived | 0.039 | equation | `= lens_half_w + lens_gap/2` | parent A L43-L44 |
| temple_len | float | [0.115, 0.140] | 0.127 | independent | clamp; arm length | parent B L49 / aviator L197 |
| hinge_z | float | derived | top corner | equation | `= lens_half_h - 0.006` (outer-top corner) | parent B L48 |
| fold_range | float | [85°, 100°] | 95° | independent | clamp; main fold sweep ≥60° required | all sources (e.g. parent B L381) |
| spring_range | float | [12°, 25°] | 20° | conditional | only when temple_style=spring_hinges; sweep must stay 5°–30° | spring L65, L611-L614 |
| (—) | constraint | — | — | inequality | `bridge_w = lens_gap + 0.006…0.012 ≥ rim inner-edge gap` so bridge overlaps both rims (connectivity); shrink/expand to satisfy | parent A L118-L120 / round_wire L96-L101 |
| (—) | constraint | — | — | inequality | wraparound_shield: `shield_half_w ≥ rim_center_x + lens_half_w` (spans both eyes, asserted >0.10 m) | wraparound L313-L316, L499-L503 |
| (—) | constraint | — | — | conditional | Slot B legal set depends on Slot A enum (wraparound_shield ⇒ bridge_style forced to internal nose support) | compatibility matrix |

palette_style colorways (≥3, observed across the 10 sources):
1. **clear_acetate** — clear/near-transparent lens (alpha≈0.25), light translucent acetate rim; the "clear eyeglasses" reading the 002.png label implies. Lens alpha low; rim light.
2. **tortoise** — warm brown mottled acetate rim/temple, light-amber translucent lens.
3. **matte_black** — `sport_temple` matte dark rim+temple (0.10,0.10,0.12), `rubber_grip` tips; from thick_sport_temples L38-L39.
4. **smoky_tint** — `glossy_gunmetal` (0.16,0.17,0.19) frame + `smoky_lens` (0.10,0.11,0.13, alpha 0.55) + `polished_metal` rim; from lineage-A clubmaster (parent B L280-L288).
5. **amber_tint** — `polished_silver` (0.82,0.84,0.87) rim + `amber_lens` (0.42,0.16,0.03, alpha 0.62) + `black_acetate` tips; from lineage-B aviator (parent A L33-L36).
6. **silver_metal** — full silver metal rim/temple + light grey lens (round_wire/aviator metal read).

## Multiplicity / Copy Logic

- **No template-level variable multiplicity axis.** side_count is **fixed at 2** (left/right) for temples, hinges, lenses (or 1 continuous shield for wraparound), bridge struts, and nose pads. This is a mirror symmetry, NOT a sampled N — there is no `*_count` parameter and no weighted N draw.
- copied object: the per-side assembly = `temple_{side}` (+ `flex_link_{side}` when spring_hinges) + its hinge mount + (per-eye) `rim_{side}`/`lens_{side}`/`nose_pad_{side}`.
- naming: emit by semantic side — `{side}` ∈ {`right`,`left`} (lineage B) or index `{i}` ∈ {0,1} (lineage A round_wire); template should normalize to `right`/`left`. Joints: `fold_{side}` (and `spring_{side}` for spring_hinges).
- placement: mirrored across the Y=0 (lineage B: X=0) symmetry plane; rim center at `±rim_center_x`, hinge at `±hinge_y` (outer-top corner).
- joint policy: each side gets an identical REVOLUTE fold (axis sign mirrored so positive q folds inward, range 0–95°); spring_hinges additionally gives each side an upstream small-range REVOLUTE through the flex link. **≥1 real revolute fold joint per side is mandatory** (the core articulation; never collapse to FIXED).
- source/gating: mirror loop is unconditional; the only per-side structural variation is spring_hinges adding the intermediate flex part (still mirrored).

(Note: rim screws / hinge barrels / strut counts are fixed local detail, not exposed as a multiplicity axis.)

## 拓扑多样性审计

总组合数:Slot A(7) × Slot B(2) × Slot C(3) = **42**.
Minus compatibility exclusions: wraparound_shield (1 of 7 in A) forces Slot B to the degenerate internal-nose form (counts as 1 effective B), so it contributes 1×3 = 3 instead of 2×3 = 6 → effective combos = 6×2×3 + 1×1×3 = 36 + 3 = **39 distinct topology classes** (well above the gate). side_count is fixed 2 → no multiplicity multiplier.

理由:Slot C alone gives a real joint-topology split (2 vs 4 revolute joints, chain depth 1 vs 2 via spring_hinges). Slot A gives 7 distinct part-tree/outline classes (incl. 1-lens shield vs 2-lens). Slot B gives a part-count/connectivity split (separate nose pads vs keyhole saddle, pads removed). Even gating wraparound, 39 topology classes ≫ 10.

seed_domain_policy：procedural_first.

Procedural Sampling / Sweep Plan:`config_from_seed(seed)` does a deterministic weighted draw over (front_shape, bridge_style, temple_style, palette_style) using `ctx.rng`. `seed=0` is not special. Weights: front_shape roughly uniform across the 7 (slight downweight of wraparound_shield since it constrains B); temple_style slightly favors `folding_temples` (the common case), `spring_hinges` rarer (extra-part path, more failure surface); bridge_style favors `standard_bridge`. Each draw is legalized through the compatibility matrix before building. `slot_choices_for_seed(seed)` returns the resolved `[(slotA,module),(slotB,module),(slotC,module)]`; continuous scales (lens_half_w, lens_gap, temple_len, fold_range) are sampled+clamped but NOT recorded as topology choices unless they change an equivalence class (they don't).

Topology target:1000-seed slot choice tuple distinct expected ≈ 39 (capped by the discrete combo count); below 300 is expected and justified — eyewear has a small but genuine topology space (7×2×3 gated), the rest of the diversity is controlled proportion + palette, not topology. This is the category's natural ceiling, not an authoring gap.（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization:key continuous scales = `lens_half_w` (independent [0.024,0.030]), `lens_half_h` (equation `= lens_half_w*aspect`), `lens_gap` (independent [0.014,0.022]), `rim_center_x` (equation `= lens_half_w + lens_gap/2`), `temple_len` (independent [0.115,0.140]), `fold_range` (independent [85°,100°]), `spring_range` (conditional, spring_hinges only). Sampling contract: sample independents (lens_half_w, lens_gap, temple_len, fold_range) → derive equations (lens_half_h, rim_center_x, hinge_z) → project inequalities (bridge_w overlaps both rims; shield spans both eyes) → resolve conditionals (spring_range only if spring_hinges; Slot B set by Slot A). All solved in `resolve_config`; none break the hinge origin, lens-in-rim mate, or the 2-temple symmetry.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted draw over A×B×C×palette via ctx.rng; wraparound downweighted; legalize via matrix before build | slot_choices_for_seed matches build choices |
| compatibility matrix | wraparound_shield→Slot B internal-only; spring_hinges independent of A/B; all other A×B×C legal | no floating shield ends, bridge overlaps rims, hinge captured, fold sweep ≥60° |
| controlled local variation | lens_half_w/lens_gap/temple_len/fold_range sampled+clamped; rest derived | proportions vary without breaking lens-in-rim, hinge origin, fold range, or eyewear identity |
| regression overrides | none initially (add only for a specific failed seed with reason) | previously failed or reviewer-selected cases only |
| random sweep | seeds 0-49 initial pass, 0-999 maturity audit |, contract failures (overlap, fold, connectivity) |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A (front lens/rim shape) | 7 | yes | yes | rect/browline/cat-eye/round-wire/shield/hex/panto |
| B (bridge/nose) | 2 | yes | no | standard_bridge (two source forms) + keyhole_bridge; 2 is the real structural space (pad-bridge vs saddle); see degrade note |
| C (temple/hinge) | 3 | yes | yes | folding/spring(4-joint)/thick-sport |

Slot B degrade note (2 candidates, < target 3): only two structurally distinct bridge topologies exist across all 10 5★ sources — (a) a bridge bar with separate nose pads (both parents, two stylistic forms that are the SAME topology: bar + 2 pad parts) and (b) the keyhole bridge solid whose saddle cutout REPLACES the nose pads (different part count + connectivity). Other "bridge" variation in the sources is pure dimension/material (single vs double bar), which §2.4 forbids as a candidate. Slot B stays at 2 with this documented reason rather than inventing a third bridge topology with no 5★ source. It is NOT a single-candidate slot.

## Validator

- slot_choices_for_seed returns implemented module names for all 3 slots
- config_from_seed uses deterministic procedural sampling for all ordinary seeds (seed=0 not special)
- compatibility matrix prevents illegal combos (wraparound_shield + per-eye bridge/keyhole)
- optional regression overrides are sparse and justified (none initially)
- final template does not endlessly cycle a small curated table as the main seed domain
- controlled local scale params (lens_half_w, lens_gap, temple_len, fold_range) are clamped; derived (lens_half_h, rim_center_x) and conditional (spring_range, Slot B set) resolved in `resolve_config`, never left to fail in the builder
- critical InterfaceSpec/MatingContract points exist: lens-in-rim overlap, bridge-spans-both-rims overlap, temple-knuckle-captured-in-hinge allow_overlap, (spring) flex-boss-in-barrel allow_overlap
- key joints: exactly 2 `fold_{side}` REVOLUTE (axis ±Z, range≈0–95°, sweep ≥60°); for spring_hinges additionally 2 `spring_{side}` REVOLUTE (range 5°–30°) → 4 revolute total
- copied objects follow naming/placement policy (mirrored `{side}`, symmetric origins)
- both temples actually rotate (AABB extent flips from along-fore/aft to across-width when folded 90°)

## Reject cases

- A temple that is FIXED or has no meaningful fold (sweep < 60°) — kills the core articulation.
- wraparound_shield combined with per-eye rims or a keyhole saddle bridge (geometry contradiction: one continuous shield has no inter-rim gap).
- Bridge that does not overlap both rims/lens footprints → disconnected front frame (floating rim).
- Lens floating outside its rim (lens half-extents not matched to rim opening) or shield narrower than 0.10 m (fails span check).
- Temple knuckle / flex boss NOT captured in the hinge mount (declared overlap missing) → QC overlap failure, or hinge mount absent → floating temple.
- spring_hinges with flex_link missing the upstream spring revolute (collapses to plain fold) or spring range outside 5°–30°.
- Monochrome output (palette_style not sampled) — single colorway across all seeds.
- Folded pose flying away from the frame (folded arm not staying near front in Z) — wrong axis sign / origin.

## 与相邻类别的边界

- 不该混入：goggles / swim goggles（密封 eyecups + 头带，无折叠 temple；glasses 的身份是 folding temple + 鼻托支撑）。
- 不该混入：face shield / visor / VR headset（整片面屏或显示外壳 + 头带，无 per-eye 镜片与铰链折叠）。
- 不该混入：lorgnette / magnifier（单手柄、无双 temple 折叠铰链）。
- 不该混入：monocle / single-lens loupe（单镜片、无 bridge、无双 temple）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Open questions for review: (1) Two SDK lineages (cadquery vs geometry-primitive) — template must pick ONE coordinate convention and port the other lineage's modules; recommend lineage B (geometry-primitive, +X=right/+Y=forward) since it covers shield+cat-eye and the rpy-based fold is cleaner. (2) Slot B has 2 candidates (degrade documented; only 2 real bridge topologies exist). (3) wraparound_shield gates Slot B (captured in compatibility matrix). (4) Lens tint clear/tortoise/black/tinted handled via palette_style (6 colorways), NOT a slot — both reference parents are sunglasses; "clear eyeglasses" label on parent B is a source-map mislabel (its prompt/model build clubmaster sunglasses with smoky lenses). (5) spring_hinges is the topology-defining Slot C member (4 revolute joints, chain depth 2). |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | rectangular_clear_rims | rec_..._211959_619782b5 (parent A) | L48-L65, L75-L115 | aviator rim+bezel+lens; lineage-B convention |
| S2 | A | sport_front_frame | rec_..._209562_7e979b64 (parent B) | L56-L72, L91-L108, L125-L183 | browline brow+lower-rim+lens; lineage-A convention |
| S3 | A | cat_eye_frame | rec_glasses_var_cat_eye_frame | L52-L98, L108-L146 | cat-eye upswept outline |
| S4 | A | round_wire_rims | rec_glasses_var_round_wire_rims | L65-L91, L94-L103 | torus wire rim + circular lens |
| S5 | A | wraparound_shield | rec_glasses_var_wraparound_shield | L75-L92, L308-L403 | single continuous shield lens + brow |
| S6 | A | hexagonal_lenses | rec_glasses_var_qwen_hexagonal_lenses | L56-L66, L83-L106 | hex outline + straight-edge full rim |
| S7 | A | oval_panto_lenses | rec_glasses_var_qwen_oval_panto_lenses | L56-L75, L87-L111 | panto oval outline + spline full rim |
| S8 | B | standard_bridge | parents A+B | A L117-L174 / B L167-L215 | bridge bar(s) + nose pads/stems |
| S9 | B | keyhole_bridge | rec_glasses_var_keyhole_bridge | L130-L163, L178-L257 | keyhole saddle bridge (replaces pads) |
| S10 | C | folding_temples | rec_..._209562_7e979b64 (parent B) | L218-L270, L356-L394 | slim folding temple + 2 revolute |
| S11 | C | spring_hinges | rec_glasses_var_spring_hinges | L184-L272, L436-L517 | flex_link intermediate + 4 revolute (chain depth 2) |
| S12 | C | thick_sport_temples | rec_glasses_var_thick_sport_temples | L38-L39, L191-L268 | thick sport arm + broad rubber ear tip |

## 模板实现备注（可选）

- Pick ONE coordinate convention and port modules across lineages. Recommend lineage B's geometry-primitive style (`tube_from_spline_points`, `sweep_profile_along_spline`, `BoxGeometry`, `+X`=right/`+Y`=forward, fold via `Origin(rpy=(0,0,-90°))` + mirrored axis sign). Lineage-A cadquery modules (brow bar, hexagonal/panto outlines, keyhole bridge) must be re-authored as geometry-primitive outlines/extrudes in the chosen frame.
- Shared helper: a single `lens_outline(shape, half_w, half_h)` returning the (x,z) point loop for rect/cat-eye/round/hex/panto, consumed by BOTH the lens geometry and the matching rim path (every Slot A source does exactly this).
- Element-scoped allow_overlap is REQUIRED for: temple-knuckle↔hinge-block (all Slot C), and additionally flex-boss↔spring-barrel + temple-knuckle↔flex-link (spring_hinges only). Replicate these per chosen side names.
- wraparound_shield: emit single `shield_lens` (no per-eye lens parts) and degrade Slot B to internal nose support; assert shield span > 0.10 m.
- spring_hinges is the only Slot C member that adds parts + a joint; keep its `flex_link_{side}` as a real intermediate part with its own upstream revolute, do not bake it into the temple.
