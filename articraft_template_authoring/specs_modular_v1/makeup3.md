# makeup3 — modular spec (0611 / Makeup3)

## 元信息
| 项 | 值 |
|---|---|
| slug | `makeup3` |
| template path | `agent/templates/makeup3.py` |
| test path (optional) | — |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star Makeup3 samples (2 parents + 8 fork variants) |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

articulated makeup compact — a hinged/slid cover over a shallow base holding one or
more pressed powder wells, plus a front closure (push button or toggle lever).
must_keep: shallow base + covering lid + at least one non-fixed joint (lid or closure),
plus visible powder wells. must_not_become: jewelry box, empty cosmetic case, lipstick,
mirror-only compact.

## 槽位 + 候选模块表

### Slot A: `case_form` (③ Primary Form Family)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| round | forked_anchor | rec_0611_makeup3_var_case_form_round (+ parent 002) | model.py:L27-L43 (base_wall LatheGeometry), L177-L206 (base assembly) | eligible if compatible | Planar Boundary Form: axisymmetric circle profile; stepped LatheGeometry base_wall, circular floor disc, circular lid |
| hexagonal | forked_anchor | rec_0611_makeup3_var_case_form_hexagonal | model.py:L164-L219 (polygon(6) base body + rim), L304-L327 (polygon lid_shell) | eligible if compatible | Planar Boundary Form: hexagonal polygon(6) profile; base_body / rim / lid_shell all polygon(6) extrusions |
| rectangular | forked_anchor | rec_0611_makeup3_var_case_form_rectangular | model.py:L217-L275 (rectangular base) | eligible if compatible | Planar Boundary Form: axis-aligned rectangle profile; base_wall as rounded box, rectangular floor + lid |

### Slot B: `lid_mechanism` (② joint type)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| hinge_flip | forked_anchor | rec_picturex_0611__makeup3__002 / __001 / rec_0611_makeup3_var_lid_module_fitted_inner_mirror | 002 model.py:L227-L259 (base_to_lid REVOLUTE -X); 001 L375-L395 | eligible if compatible | REVOLUTE about -X, hinge line at rear (+Y). Lid rotates up to reveal powder wells. Hinge knuckles on base and barrel on lid. |
| guided_slide | forked_anchor | rec_0611_makeup3_var_insert_motion_guided_slide | model.py:L391-L410 (base_to_lid PRISMATIC) | eligible if compatible | PRISMATIC along -Y with guided slide rails; lid translates forward off the case rather than pivoting. |

### Slot C: `closure` (② joint type)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| push_slide_button | forked_anchor | rec_picturex_0611__makeup3__002 / __001 (parents) | 002 model.py:L261-L281 (base_to_latch_button PRISMATIC +Y); 001 L407-L421 (base_to_clasp PRISMATIC +Y) | eligible if compatible | PRISMATIC along +Y at front (-Y edge). Short inward travel (~1.5mm). Rectangular button cap. |
| toggle_latch | forked_anchor | rec_0611_makeup3_var_closure_toggle_latch | model.py:L481-L505 (base_to_latch REVOLUTE about X) | eligible if compatible | REVOLUTE at front pivot (~11mm lever). Lever rotates to hook the lid. |

### Slot D: `powder_layout` (①/multiplicity)

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| single_pan | forked_anchor | rec_picturex_0611__makeup3__002, rec_0611_makeup3_var_case_form_round | 002 model.py:L46-L63 (`_powder_pan`, `_powder_cake`), L208-L225 (FIXED base_to_powder_insert) | eligible if compatible | Single circular powder pan (metal ring + cake disc) as a FIXED child part `powder_insert` on `base`. |
| two_well | forked_anchor | rec_0611_makeup3_var_powder_layout_2_well | model.py:L53-L89 (2-well pan + half-cake sectors), L25-L31 (WELL_COUNT=2) | eligible if compatible | Two 180-degree sector cakes inside a shared metal pan with center divider wall; single FIXED `powder_insert` child. |
| four_well | forked_anchor | rec_0611_makeup3_var_powder_layout_4_well | model.py:L27-L94 (WELL_COUNT=4, tray + wells + cakes), L260-L284 (per-well FIXED parts) | eligible if compatible | 2x2 grid: brushed tray + 4 individual FIXED `powder_well_i` parts with independent cakes, companion shade palette. |

### Slot E: `palette_style` (⑥ colorway)

| module_name | source_type | source evidence | notes |
|---|---|---|---|
| gloss_black_peach | record_only | 002 parent (L171-L175: gloss_black + peach_powder) | Family A canonical colorway. |
| polished_gold_champagne | record_only | 001 parent (L127-L162) | Family B canonical colorway (gold shell, champagne/rose/coral/cocoa powders). |
| pastel_rose | world_knowledge_extrapolation | anchors: parents + reviewer | Realistic pastel rose colorway (pink shell + warm powder). |
| brushed_silver | world_knowledge_extrapolation | anchors: parents + reviewer | Metallic silver / cool-white shell with rose-beige powder. |

## 槽位图 (slot graph)

pattern: mixed

```
base (root, footprint from case_form)
  ├─[REVOLUTE -X (hinge_flip) OR PRISMATIC -Y (guided_slide)]→ lid  (lid_mechanism, plus optional lid_module fitted mirror)
  ├─[PRISMATIC +Y (push_slide_button) OR REVOLUTE +X (toggle_latch)]→ closure  (closure)
  └─[FIXED base_to_powder_insert  (single_pan / two_well)]→ powder_insert
     OR
      [FIXED base_to_powder_well_i for i in range(4)]→ powder_well_i  (four_well)
```

- All non-FIXED joints have real anchoring geometry on both sides (Rule 2): hinge knuckles on base + barrel on lid; button cap in a socket; toggle pivot pin at front edge.
- FIXED joints for `powder_insert` and `powder_well_i` are legitimate composed kinematic sub-assemblies (each pan is a self-contained metal cup + cake pair, mirroring 5-star sources); their parents (base_body / tray_surface) provide the anchoring visual.
- Guided-slide lid + push_slide_button share the -Y edge — both PRISMATIC along Y — this is a compatibility risk documented below (§9 gating: guided_slide forces toggle_latch to avoid same-axis collision).

## 每槽位 Module Emits / Interfaces

### Slot A / case_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base` (root part) with footprint mesh, floor disc, hinge knuckles | 002 L177-L206 / 001 L163-L296 / hex L164-L302 / rect L217-L275 |
| internal joints | none | — |
| upstream interface | — (root) | — |
| downstream interface | rim top (z ≈ case_h), rear hinge line, front closure edge | shared across all |

### Slot B / lid_mechanism
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid` | 002 L227-L241 / slide L311-L389 |
| internal joints | `base_to_lid` (REVOLUTE or PRISMATIC) | 002 L242-L259 / slide L391-L410 |
| upstream interface | rim top / rear hinge line | — |
| downstream interface | (lid top) — for optional fitted_inner_mirror decoration | — |

### Slot C / closure
| emits | 描述 | 来源 |
|---|---|---|
| parts | `closure` (button or lever) | 002 L261-L266 / 001 L397-L406 / toggle L470-L479 |
| internal joints | `base_to_closure` (PRISMATIC or REVOLUTE) | 002 L267-L281 / toggle L481-L505 |
| upstream interface | front edge of base | — |
| downstream interface | — | — |

### Slot D / powder_layout
| emits | 描述 | 来源 |
|---|---|---|
| parts | `powder_insert` (single_pan / two_well) OR `powder_well_0..3` (four_well) | 002 L208-L218 / 2well L246-L294 / 4well L260-L284 |
| internal joints | FIXED `base_to_powder_insert` OR 4× FIXED `base_to_powder_well_i` | 002 L219-L225 / 4well L278-L284 |
| upstream interface | base cavity floor | — |
| downstream interface | — | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| case_form | enum | {round, hexagonal, rectangular} | — | choice | procedural sampler | Slot A |
| lid_mechanism | enum | {hinge_flip, guided_slide} | — | choice | procedural sampler | Slot B |
| closure | enum | {push_slide_button, toggle_latch} | — | choice | procedural sampler; guided_slide + push_slide_button → force toggle_latch | Slot C, §9 |
| powder_layout | enum | {single_pan, two_well, four_well} | — | choice | procedural sampler; rectangular + four_well → degrade to single_pan (footprint packing) | Slot D, §9 |
| palette_style | enum | {gloss_black_peach, polished_gold_champagne, pastel_rose, brushed_silver} | — | choice | procedural sampler | Slot E |
| case_footprint_scale | float | [0.90, 1.12] | 1.0 | independent | independent sample, clamped | 002 L21 CASE_RADIUS |
| case_height_scale | float | [0.88, 1.15] | 1.0 | independent | independent sample, clamped | 002 case dims |
| lid_open_angle_scale | float | [0.85, 1.10] | 1.0 | independent | clamped; final upper ≤ 0.95·π | 002 L253 REFERENCE_LID_ANGLE etc. |
| slide_travel_scale | float | [0.85, 1.10] | 1.0 | independent | clamped; final travel ∈ [0.060, 0.120] | slide L400-L410 |
| button_travel_scale | float | [0.80, 1.20] | 1.0 | independent | clamped; travel ∈ [0.001, 0.003] | 002 L272-L280 |
| (—) | constraint | — | — | inequality | (four_well): (2*well_spacing + 2*well_radius) ≤ 2*(case_r_inner - margin) — enforced by shrinking spacing then clamping to single_pan | 4well L27-L35 |

## 7.5 编译预算 / compile budget

Target ≤ 25 s per seed. Base + lid use LatheGeometry / polygon extrusions with 96
segments; powder pans use ≤48 seg circles; four_well emits 4 small identical cake
Meshes (reused helper). Rationale: comparable to Accessories_Cushion (≤20 s
observed). If seeds exceed 25 s, drop LatheGeometry segments to 64 and cake
tolerance to 3e-4.

## Multiplicity / Copy Logic

- count_param: `powder_well_count` (implicit in `powder_layout` enum)
- N_range: {1, 2, 4} — bounded by accepted source samples (single_pan=1, two_well=2, four_well=4)
- sampling domain: encoded into `powder_layout` enum choice (uniform over the 3 candidates); N never becomes a free integer parameter (no 3-well or 5-well 5-star source exists).
- copied object: single well helper (`_well_pan()` / `_well_cake()`) shared across four_well's 4 children; naming `powder_well_{i}`; regular 2x2 grid placement; per-well FIXED joint.

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减 part 或边 | 有 | powder_layout: {`base+powder_insert+lid+closure` (single/two_well)} vs {`base+powder_well_0..3+lid+closure` (four_well)} — 4-well adds 3 extra FIXED-child parts; forked_anchor: powder_layout_2_well, powder_layout_4_well |
| └ multiplicity | 同构件 ×N | 有 | powder_well N ∈ {1, 2, 4}; 见 §8 |
| ② 关节类型 | 换 type/轴 | 有 | lid_mechanism: REVOLUTE (-X) vs PRISMATIC (-Y); closure: PRISMATIC (+Y) vs REVOLUTE (+X). forked_anchor: parent 002 + insert_motion_guided_slide + closure_toggle_latch |
| ③ 主体形态家族 | 换 form prototype | 有 | case_form: round (Planar Boundary — circle), hexagonal (Planar Boundary — polygon(6)), rectangular (Planar Boundary — axis-aligned rect). forked_anchor: case_form_round, case_form_hexagonal, case_form_rectangular. **形态主导 → 登记为 slot** |
| ④ 表面装饰 | 表面细节 | 有 | (a) source: gold outer_rim / medallion / clover motifs (001 family); label_plaque + herringbone grooves (002 family). (b) world-extrapolation: subtle bezel / rim ring. host-conformal (rim inherits base polygon/circle). Note: keep decoration simple to preserve compile budget. |
| ⑤ 尺寸/行程 | 连续尺寸 | 有 | case_footprint_scale [0.90, 1.12], case_height_scale [0.88, 1.15]. Motion envelopes: hinge_flip REVOLUTE about -X, opens up, [0, ~1.62rad]; guided_slide PRISMATIC -Y, [0, 0.060-0.120]; push_slide_button PRISMATIC +Y, [0, 0.001-0.003]; toggle_latch REVOLUTE +X, [0, ~1.4rad]. `motion_test_plan`: `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` + targeted `ctx.pose(...)` for each mechanism. |
| ⑥ 涂装 | 材质/颜色 | 有 | 4 palettes: gloss_black_peach, polished_gold_champagne, pastel_rose, brushed_silver. Material classes: painted/metal/powder — covers ≥ ceil(0.5×4)=2 classes. |

## 采样与覆盖审计

Total combinations: 3 (case_form) × 2 (lid_mechanism) × 2 (closure) × 3 (powder_layout) × 4 (palette_style) = 144.
With §9 gating dropping ~1/6 of tuples, effective ≈ 120.

Reason: sufficient to cover Primary Form Family × joint type × multiplicity × palette in 0-35 sweep with margin.

seed_domain_policy: procedural_first
Procedural Sampling / Sweep Plan: deterministic `random.Random(seed)` chooses one candidate per slot, then §9 gating rewrites incompatible combinations. Compatibility gates:
1. `guided_slide` + `push_slide_button` share the -Y axis → force closure = `toggle_latch`.
2. `rectangular` + `four_well` → degrade to `single_pan` (rectangular cavity is short in Y).

Topology target: 144 combos; ~120 realized. 0-35 sweep covers all case_form × lid_mechanism × closure × powder_layout combos with high probability (144 combos vs 36 seeds is dense but every slot value appears ≥4 times in expectation).

Controlled local parameterization: `case_footprint_scale`, `case_height_scale`,
`lid_open_angle_scale`, `slide_travel_scale`, `button_travel_scale` — all
independent, clamped in `resolve_config`.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | deterministic per-slot uniform + compatibility gating | slot_choices_for_seed matches build choices |
| compatibility matrix | 2 gates as above | no PRISMATIC axis collision, no over-packed four_well |
| controlled local variation | 5 scales, clamped | proportions vary; joint travels stay within safe window |
| regression overrides | none initially | reviewer-added if sweep failures require |
| random sweep | 0-35 initial pass + corner | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| case_form | 3 | yes | yes | ③ registered |
| lid_mechanism | 2 | yes | no | pool limited to 2 real ② types in the 5-star sources |
| closure | 2 | yes | no | same |
| powder_layout | 3 | yes | yes | 1/2/4 well |
| palette_style | 4 | yes | yes | 4 palettes |

## Validator

- slot_choices_for_seed returns implemented module names for every slot
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating prevents illegal module combinations (guided_slide + push_slide_button; rectangular + four_well)
- controlled local scale params are clamped and cannot break interfaces, clearance, joint origin, or category multiplicity
- MatingContract declared on every non-FIXED joint (`base_to_lid`, `base_to_closure`), pinning to real hinge knuckle / lid barrel / button socket visuals
- key joints have expected type / axis / range
- copied objects (four_well wells) follow naming and placement policy
- `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` is called in `run_makeup3_tests` (Rule 5)

## Reject cases

- lid PRISMATIC (guided_slide) with lid-mechanism-hinge PRISMATIC same axis as closure → resolved by gating
- four_well cake radii exceeding rectangular cavity half-width → resolved by gating (degrade to single_pan)
- rectangular case + guided_slide with base rail overlap → allowed via element-scoped allow_overlap on rail vs base_wall
- lid closed-pose overlaps with rim → declared allow_overlap on lid vs base at closed pose (mirroring 002 parent's contact allowance)
- toggle_latch swept full range collides with lid front edge mid-travel → declared allow_overlap on lever vs base_body

## 与相邻类别的边界

- 不该混入：jewelry box（jewelry lacks powder wells; makeup3 must retain visible pans/cakes）
- 不该混入：cosmetic case/lipstick container（those have PRISMATIC lipstick tube, not powder wells）
- 不该混入：empty mirror-only compact（must retain at least one visible powder well cake）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | first draft, direct from 0611__Makeup3.md source map and 10 5-star records |
