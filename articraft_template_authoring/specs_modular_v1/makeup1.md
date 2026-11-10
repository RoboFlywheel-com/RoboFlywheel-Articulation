# makeup1 — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `makeup1` |
| template path | `agent/templates/makeup1.py` |
| test path (optional) | `tests/agent/test_makeup1_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 |
| read_count | 12 |
| read_scope | all 5-star Makeup1 records under `data/records/rec_picturex_0611__makeup1__00X__*` (origins 001/002/003) and 9 forked variants (`rec_0611_makeup1_var_*`) |
| source_index_policy | only adopted module sources are indexed below |

Key adaptations:
- Origin 001 (`nine_pan_makeup_compact_001`, `model.py:L182-L318`): rounded rectangular case + full-footprint domed lid + `cover_hinge` REVOLUTE around -X, 3×3 pressed powder grid — canonical multi-well palette.
- Origin 002 (`ten_well_concealer_palette`, `model.py:L131-L228`): black rectangular tray + clear polycarbonate lid, 2×5 pan grid, cover pivots π radians about +X (fold-flat pose).
- Origin 003 (`two_way_cake_compact`, `model.py:L43-L338`): dual-pan blush compact with mirror lid AND a prismatic front push-latch (LATCH is a second articulation) — the compact-latch source.
- All origins share: single moving lid + REVOLUTE hinge line at the rear rim. Origin 003 adds a PRISMATIC front latch as a second child of `base`.

## 核心身份

Articulated cosmetic compact / palette that retains powder or pressed cake in visibly identifiable wells behind a hinged (or slide) cover. Real defining features:
1. A grounded `base` shell with a recessed floor holding N powder wells.
2. A `cover` that opens (hinge / slide) to expose the wells.
3. Optional visible support interfaces (hinge barrels + captured pin, latch stem inside front housing).

不该混入的相邻类别：jewelry box (no powder), empty cosmetic case (no wells), lipstick tube, container (no wells / no hinged cover exposing powder).

## 槽位 + 候选模块表

### Slot A：`case_form` — the case footprint & profile (③ Primary Form Family)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rounded_rectangle` | forked_anchor | `rec_picturex_0611__makeup1__001__png_1e56ed25897943d1bb05005bc41aca4e` | L20-L86 (`_make_case_shell`, `_rounded_plate`) | eligible if compatible | Rounded rectangular molded shell (CASE_W×CASE_D×CASE_H) with shallow recess. Planar Boundary Form. |
| `elongated_rectangle` | forked_anchor | `rec_0611_makeup1_var_case_form_elongated_rectangle` (spec map row L27); shape from `rec_picturex_0611__makeup1__002__png_350d6df173ce4cc08935724fb35d43dc` L19-L82 (`PALETTE_WIDTH=0.198`, `PALETTE_DEPTH=0.086`) | L19-L82 | eligible if compatible | Wide 5×2 rectangular palette (aspect ~2.3). Planar Boundary Form. |
| `round_puck` | forked_anchor | `rec_0611_makeup1_var_case_form_round_puck` (spec map row L26) | derived analogous to `rec_picturex_0611__makeup1__001` case_shell with axisymmetric cylinder + rim | eligible if compatible | Cylindrical puck outline (`Cylinder(base_radius, base_height)`). Planar Boundary Form / Volumetric Envelope Form. |

Form-dominated ③ slot registered as required by §8.5.

### Slot B：`closure` — hinge or latch topology (② Joint Type)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rear_hinge` | forked_anchor | `rec_picturex_0611__makeup1__001__png_1e56ed25897943d1bb05005bc41aca4e` | L71-L86 (`_make_hinge_mounts`), L301-L318 (`cover_hinge` REVOLUTE ±X); also `rec_picturex_0611__makeup1__002__*` L64-L72 (rear knuckle rows), L210-L227 | eligible if compatible | Single REVOLUTE joint on rear rim; captured hinge pin through molded knuckles. |
| `push_latch` | forked_anchor | `rec_picturex_0611__makeup1__003__png_1e77f77007c24952b1f52a18542fa4d8` | L305-L334 (`latch` part + `latch_press` PRISMATIC +Y), L161-L198 (`base_knuckle_i`, `base_hinge_pin`) | eligible if compatible | Rear REVOLUTE hinge PLUS second front-push PRISMATIC latch (small travel, 1.2mm). Adds an extra child part `latch`. |
| `sliding_latch` | forked_anchor | `rec_0611_makeup1_var_closure_sliding_latch` (spec map row L31); topology inherits from origin 003 latch mechanism with lateral prismatic axis (X) | derived from L305-L334 with axis rotated 90° | eligible if compatible | Rear REVOLUTE hinge PLUS second front prismatic latch with sideways (X) travel of a slider button. |

### Slot C：`powder_layout` — pan grid multiplicity (①/multiplicity)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `nine_pan_3x3` | forked_anchor | `rec_picturex_0611__makeup1__001__png_*` | L246-L270 (`spacing`, 3×3 loop) | eligible if compatible | 3×3 grid; 9 pans; square rounded pans. |
| `ten_well_2x5` | forked_anchor | `rec_picturex_0611__makeup1__002__png_*` | L176-L187 (2×5 loop, radial pans) | eligible if compatible | 2×5 grid; 10 pans; circular pans. |
| `dual_pan` | forked_anchor | `rec_picturex_0611__makeup1__003__png_*` | L107-L159 (two extruded loft pans + rims) | eligible if compatible | 1×2; 2 pans; dual side-by-side. |
| `four_quadrant` | forked_anchor | `rec_0611_makeup1_var_powder_layout_4_quadrant` (spec map row L23) | derived 2×2 grid extending origin 001 layout | eligible if compatible | 2×2 grid; 4 pans. |
| `six_radial` | forked_anchor | `rec_0611_makeup1_var_powder_layout_6_radial` (spec map row L24) | derived from origin 002 pan pattern | eligible if compatible | 6 pans arranged 2×3. |
| `twelve_well` | forked_anchor | `rec_0611_makeup1_var_powder_layout_12_well` (spec map row L25) | derived 3×4 grid extending origin 002 layout | eligible if compatible | 3×4 grid; 12 pans. |

## 槽位图（slot graph）

pattern: `mixed` (parallel-children on a single `base` chassis)

```
case_form  →  base (chassis)  →  ├─ closure.rear_hinge:  REVOLUTE joint (base ↔ cover)  → cover
                                 ├─ closure.push_latch:  REVOLUTE (base ↔ cover) + PRISMATIC (base ↔ latch)
                                 ├─ closure.sliding_latch: REVOLUTE (base ↔ cover) + PRISMATIC (base ↔ latch)
                                 └─ powder_layout: N pan visuals inlined on `base` cavity floor (Rule 1)
```

- `case_form` drives base footprint (rx, ry) — parametrizes ALL other slots' extents.
- `closure` writes hinge hardware onto `base` rim + emits `cover` child part + optional `latch` child part.
- `powder_layout` writes pan / cake visuals as `base.visual(...)` — no joint (Rule 1).
- Pan row width must fit within `2*(rx - 1.5*wall)`.

## 每槽位 Module Emits / Interfaces

### Slot A / module `rounded_rectangle` / `elongated_rectangle`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (root) | S1 / model.py:L223 |
| internal joints | none | — |
| upstream interface | ground-plane rest at z=0 | — |
| downstream interface | rear rim line (0, ry, rim_z) for hinge; front rim (0,-ry,rim_z) for latch; cavity floor at z_floor for powder | S1 / L20-L86 |

### Slot A / module `round_puck`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` | derived |
| internal joints | none | — |
| upstream interface | ground | — |
| downstream interface | rear rim (0, ry, rim_z), cavity floor | derived |

### Slot B / module `rear_hinge`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cover` | S1 / model.py:L272 |
| internal joints | `cover_hinge` REVOLUTE ±X, `[0, ~π]` | S1 / L301-L318 |
| upstream interface | rear rim of `base` (mating: cover shell tail edge ↔ base rear rim) | S1 |
| downstream interface | none | — |

### Slot B / module `push_latch` / `sliding_latch`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cover`, `latch` | S3 / L200, L305 |
| internal joints | `cover_hinge` REVOLUTE ±X, `latch_press` PRISMATIC (±Y or ±X) | S3 / L287-L334 |
| upstream interface | rear rim (cover) + front rim (latch stem in housing) | S3 |
| downstream interface | none | — |

### Slot C / powder_layout modules
| emits | 描述 | 来源 |
|---|---|---|
| parts | none (Rule 1: inlined visuals on `base`) | S1 L246-L270 |
| internal joints | none | — |
| upstream interface | `base` cavity floor | S1 |
| downstream interface | none | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| case_form | enum | `rounded_rectangle`, `elongated_rectangle`, `round_puck` | — | choice | procedural sampler | Slot A |
| closure | enum | `rear_hinge`, `push_latch`, `sliding_latch` | — | choice | procedural sampler | Slot B |
| powder_layout | enum | `nine_pan_3x3`, `ten_well_2x5`, `dual_pan`, `four_quadrant`, `six_radial`, `twelve_well` | — | choice | procedural sampler | Slot C |
| palette_style | enum | `pearl_white`, `satin_black`, `rose_gold_blush`, `matte_taupe`, `translucent_clear` | `pearl_white` | choice | sampler; drives ALL `.visual(material=...)` | palettes (see below) |
| footprint_len_scale | float | [0.88, 1.14] | 1.0 | independent | clamp | S1/S2 |
| footprint_width_scale | float | [0.88, 1.14] | 1.0 | independent | clamp | S1/S2 |
| case_height_scale | float | [0.90, 1.12] | 1.0 | independent | clamp | S1/S2 |
| lid_open_angle_scale | float | [0.85, 1.05] | 1.0 | independent | clamp; upper ≤ π*0.95 | S1/S2/S3 |
| latch_travel_scale | float | [0.85, 1.10] | 1.0 | independent | clamp; upper ≤ 0.0025 m | S3 |
| pan_spacing_scale | float | [0.90, 1.10] | 1.0 | independent | clamp | S1/S2 |
| (—) | constraint | — | — | inequality | `pan_row_width = (Ncols-1)*pan_spacing + 2*pan_r ≤ 2*(rx - 1.5*wall)`; shrink span → shrink pan radius | derived clearance |
| (—) | constraint | — | — | conditional | `round_puck` case forces `rx == ry` (min of len/width scaled) | Slot A gating |

**Palette styles** (each provides the full mat dictionary consumed by every visual):
- `pearl_white`: pearl polymer shell + pearl lid + satin silver accents (origin 001).
- `satin_black`: black ABS shell + black ABS lid + clear panel (origin 002).
- `rose_gold_blush`: black gloss lower + blush peach lid + rose gold trim + hinge steel (origin 003).
- `matte_taupe`: warm neutral polymer + brushed metal accents + beige powder (world_knowledge_extrapolation of origin 001 palette family).
- `translucent_clear`: clear polycarbonate lid + black chrome shell + rose gold accents (world_knowledge_extrapolation of origins 002/003 palette).

### 7.5 编译预算

Target 15-30s per seed (mesh-heavy loft/extrude for pans + cadquery cut cavities). Small pan radii use tessellation ≤32 segments; case shell fillets ≤16 segments. Multiple identical pans share a single `Mesh` (author once, reuse). Baseline sweep budget: `--compile-timeout 120`.

## Multiplicity / Copy Logic

- count_param: `powder_pan_count` — derived from `powder_layout` choice, NOT sampled independently (each layout module carries its own N: 9, 10, 2, 4, 6, 12).
- N_range: [2, 12] across layouts.
- copied object / naming: single shared pan mesh (parametric size), placed at N positions; visual names `powder_pan_{i}` (or `{row}_{col}`).
- placement: regular grid or dual-side; joint policy: none (Rule 1 inline visual).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part | 有 | `rear_hinge` = 2 parts / 1 joint; `push_latch`/`sliding_latch` = 3 parts / 2 joints. source-backed (origins 001/002/003). |
| └ multiplicity | 同构件 ×N | 有 (见 §8) | powder_pan_count ∈ {2,4,6,9,10,12} tied to layout module. |
| ② 关节类型 | 边换 type/轴 | 有 | REVOLUTE ±X (all closures) + PRISMATIC ±Y (push_latch) + PRISMATIC ±X (sliding_latch). All source-backed. |
| ③ 主体形态家族 | 换核心 part 形态 | 有 | `case_form` slot: Planar Boundary Form — rounded rectangle vs elongated rectangle vs round puck. 3 candidates registered; source-backed. |
| ④ 表面装饰 | 表面叠加细节 | 有 (record_only) | Front thumbnail catch notch (origin 001 L60-L66); front seam notch (origin 002 L74-L82); rim trims / edge trims (all origins). Host-conformal, `record_only`. |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | footprint scales [0.88,1.14]; height scale [0.90,1.12]; hinge lid open range [0, π*0.95]; latch travel [0, 0.0025]. Sampled collision runs via `fail_if_parts_overlap_in_sampled_poses`. motion_test_plan: closed pose (joint=lower) + open pose (joint=0.7*upper) + latched pose (latch_press.upper). |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 palette_styles covering plastic/metal/painted material classes; ≥3 required, we ship 5. |

## 采样与覆盖审计

总组合数：3 (case_form) × 3 (closure) × 6 (powder_layout) × 5 (palette_style) = 270 combos + 6 continuous scales.

seed_domain_policy: procedural_first. `config_from_seed(seed)` uses `random.Random(seed)` and independently samples every slot + palette + scales.

Procedural Sampling / Sweep Plan:
- Sample slot enums independently (no gating between case_form and closure/layout — all combinations are legal by construction because layouts are inline visuals on the cavity floor and closures parent to the shared rear rim).
- `resolve_config` clamps scales and enforces the pan-row-fits-in-cavity inequality by shrinking `pan_span` first then `pan_r` (up to 40 iterations).
- Sweep: 0-35 for pass, plus corner stage. Report-only 1000-seed topology target — 270 combos are the theoretical ceiling.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | independent per-slot uniform | `slot_choices_for_seed` matches build choices |
| compatibility matrix | all legal (parallel-children design) | closed lid clears pans; latch stays inside housing |
| controlled local variation | 6 scale params; clamp + inequality projection | pan row fits cavity, hinge open range < π |
| regression overrides | none | — |
| random sweep | 0-35 (main), corner extreme seeds | axis_realization must show every case_form / closure / layout |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| case_form | 3 | yes | yes | ③ Primary Form Family |
| closure | 3 | yes | yes | ② joint type mix |
| powder_layout | 6 | yes | yes | multiplicity axis |

## Validator

- `slot_choices_for_seed` returns the same enums the build uses.
- `config_from_seed(0)` succeeds and uses procedural sampling (not a curated table).
- `resolve_config` clamps and resolves inequality (pan row fits cavity).
- Every non-FIXED articulation has a real anchoring visual on both sides (hinge barrels on `base`, hinge pin on `cover`; latch housing on `base`, latch stem on `latch`).
- No FIXED articulations; every non-moving detail is a `.visual(...)` on `base` or `cover`.
- `run_makeup1_tests` calls `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48)` and one targeted `ctx.pose(...)` per non-FIXED joint.
- `palette_style` drives every material through the `mats` dict.

## Reject cases

1. `cover` free of visible support path to `base` (missing hinge hardware).
2. Pan row wider than cavity (missing inequality clamp).
3. Closed pose leaves lid `> 3mm` above the well frame (missing seat allowance / wrong `lid_open` lower bound).
4. Push-latch travel wide enough to eject the stem from the housing.
5. Any FIXED articulation (Rule 1 violation).
6. Monochrome palette (palette_style unused; all visuals share one material).

## 与相邻类别的边界

- 不该混入：jewelry box — no powder wells; typical hinged box with tray.
- 不该混入：empty cosmetic case (Container_Cosmetic) — no exposed pressed powder inside.
- 不该混入：lipstick tube — cylindrical stick, not a compact.
- 不该混入：eyeshadow palette without hinged cover — must have articulated closure.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Slot decomposition mirrors Accessories_Cushion.md idiom (case_footprint / lid_mechanism / interior); makeup1 emphasizes wide multiplicity of powder layouts. |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | Slot A / C | rounded_rectangle / nine_pan_3x3 | `rec_picturex_0611__makeup1__001__png_1e56ed25897943d1bb05005bc41aca4e` | L20-L318 | shell primitives, 3×3 pan grid, cover_hinge REVOLUTE ±X |
| S2 | Slot A / C | elongated_rectangle / ten_well_2x5 | `rec_picturex_0611__makeup1__002__png_350d6df173ce4cc08935724fb35d43dc` | L19-L228 | wide palette, 2×5 pan grid, hinge geometry |
| S3 | Slot B | push_latch / sliding_latch | `rec_picturex_0611__makeup1__003__png_1e77f77007c24952b1f52a18542fa4d8` | L43-L338 | REVOLUTE hinge + PRISMATIC latch, dual-pan geometry |
