# Modular Spec — `kick_scooter` (Sports / Scooter Racer)

## 元信息
| 项 | 值 |
|---|---|
| slug | `kick_scooter` |
| template path | `agent/templates/Sports_Scooter_Racer.py` |
| test path (optional) | `tests/agent/test_kick_scooter_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children steering + wheel branches off a shared deck/body; multiplicity over rear-wheel count) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | parent + all 6 forked variants (rating=5) synced into `arti-template/data/records/` |
| source_index_policy | only adopted module sources are indexed below |

Sources read (all `revisions/rev_000001/model.py`):
- S0 parent `rec_vintage-green-kick-scooter-...d68bd852` — curved_swept handlebar + running_board deck + rigid stem + N=2 (front + single rear).
- S1 `rec_kick_scooter_var_tbar_straight` — straight stem + level T crossbar.
- S2 `rec_kick_scooter_var_bmx_riser` — short stem + U-bend riser + cross-brace.
- S3 `rec_kick_scooter_var_swept_cruiser` — wide swept-back beach-cruiser bar.
- S4 `rec_kick_scooter_var_flat_plank` — long flat plank deck (CadQuery filleted) + grip-tape inlay.
- S5 `rec_kick_scooter_var_folding_hinge` — stem split lower/upper + hinge knuckle/pin + fold revolute.
- S6 `rec_kick_scooter_var_three_wheel` — two rear wheels on a shared rear axle (N_rear=2 → total 3).

## 核心身份

A kick scooter ("Scooter Racer"): a stand-on, foot-propelled two-axis ride toy. World Z up, rolling direction +Y, wheel axles along X. A low foot deck (`deck top ≈ 0.10 m`, top below 0.15 m) carries a front steering head (tilted ~18° back from vertical) at one end; a tall stem sweeps up to a handlebar with two grips (~0.82 m). A single steered front wheel hangs in fork legs off the steering column; one or two rear wheels carry the tail. Three articulated DOFs are mandatory: a **steering revolute** (front column about the tilted head axis, ±40°), a **front-wheel continuous roll**, and a **rear-wheel continuous roll** (one per rear wheel). Optional fourth DOF: a **stem-fold revolute** when the folding module is chosen. Default maturity domain = a stand-on toy/kid scooter at this scale (deck ~0.33 m long, wheels R≈0.09 m); not a motorized/seated vehicle.

## 槽位 + 候选模块表

### Slot A：handlebar / steering form (steering_column geometry above the head; revolute about STEER_AXIS)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| curved_swept | S0 `...d68bd852` | L256-L317 | eligible if compatible | tall gracefully curved stem spline sweeping up-then-forward (`curved_stem` tube), narrow T crossbar (`handlebar_crossbar`) + gooseneck + 2 grips; column carries fork legs + front_fender |
| tbar_straight | S1 var_tbar_straight | L256-L312 | eligible if compatible | single straight tube along STEER_AXIS (`straight_stem`, len `STEM_LENGTH` L62) + level T crossbar + stem_cap + 2 grips; cleanest upright modern T |
| bmx_riser | S2 var_bmx_riser | L256-L341 | eligible if compatible | short vertical `stem` (L256-269) topped by one continuous U-bend `riser_bar` (L271-296) braced by a lateral `cross_brace` tube (L298-310); grips set wide at U ends |
| swept_cruiser | S3 var_swept_cruiser | L256-L345 | eligible if compatible | curved stem + wide swept-back `cruiser_bar` (L297-317) arcing ±X / toward −Y; gooseneck (L319-324) + tangent-aligned grips (L325-345), grips wider & set back |

### Slot B：foot-deck form (root body; foot_deck visual + branding/grip inlay + front_neck + head_tube + rear_fender)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| running_board | S0 `...d68bd852` | L137-L199 | eligible if compatible | low vintage running-board `foot_deck` BoxGeometry (L137-139), raised silver `branding` plate (L142-147), bent-tube `front_neck` (L151-162), tilted `head_tube` (L165-169), `rear_fender` + supporting `rear_strut` (L171-199) |
| flat_plank | S4 var_flat_plank | L141-L165 | eligible if compatible | long flat rectangular CadQuery plank with filleted long edges (`foot_deck`, L141-157) + dark non-slip `grip_tape` inlay (L159-165); shares same front_neck/head_tube/rear_fender body furniture |

> Slot B degraded to 2 candidates: only two structurally distinct deck forms exist in the 5★ pool (raised running-board vs. flat chamfered plank). Both keep deck-top z < 0.15 and rear-axle Y so wheels reach ground; the difference is a real structural form change (box+branding-plate vs. CadQuery filleted plank+grip-tape inlay), not merely size/color. Reviewer may add a third deck form (e.g. concave/dished deck) when a future fork supplies it.

### Slot C：stem articulation / folding mechanism (steering_column split; optional fold revolute)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rigid | S0 `...d68bd852` | L242-L344 | eligible if compatible | one-piece column: whole stem+bar are a single `steering_column` part; only the steering revolute moves it; no fold |
| folding_hinge | S5 var_folding_hinge | L66, L122-L129, L271-L283, L314-L320, L345-L440 | eligible if compatible | column split: `lower_stem` (L271-283) + `hinge_barrel` (L314-320) stay on `steering_column`; `upper_stem` part (L345-418, carries bar+grips+`hinge_plate_i`+`hinge_pin`+release lever) folds about `fold_hinge` REVOLUTE axis X (L428-440), HINGE_WORLD L66, lower=0 upper=150° |

> Slot C degraded to 2 candidates (rigid vs. folding_hinge) — these are the only two stem-articulation topologies in the kick-scooter pool, and they are mutually exclusive structural variants (extra part + extra joint vs. none). This is the documented ≥2 floor; reviewer accepts 2 because a third fold style (e.g. telescoping prismatic) is not yet sourced.

## 槽位图（slot graph）

pattern: mixed (parallel_children + multiplicity)

```
                         body (root: Slot B)
                         ├─ deck/branding/front_neck/head_tube/rear_fender   (Slot B visuals)
                         │
   [steering REVOLUTE @ HEAD_BASE, axis STEER_AXIS, ±40°]
                         │
                  steering_column (Slot A geometry; Slot C lower/rigid)
                         ├─ stem/bar/grips/fork_legs/front_fender            (Slot A visuals)
                         ├──[front_wheel_roll CONTINUOUS @ fw_axle_local, axis X] front_wheel
                         └──[fold_hinge REVOLUTE @ hinge_local, axis X, 0..150°] upper_stem   (Slot C = folding_hinge only)
                         │
   [rear_wheel_roll_{i} CONTINUOUS @ (rear_wheel_x(i), REAR_WHEEL_Y, AXLE_Z), axis X]
                         └─ rear_wheel_{i}   (multiplicity axis N_rear)
```

Cross-slot interfaces:
- **Slot A ↔ body (steering):** body's `head_tube` (tilted to STEER_AXIS at HEAD_BASE=`(0,0.180,0.150)`) is the mating bearing. Steering REVOLUTE origin = HEAD_BASE, axis = STEER_AXIS = `(0, sin18°, cos18°)`, range ±40°. Every Slot-A candidate authors its stem geometry in the column-local frame via `_rel()` (subtract HEAD_BASE) and seats the stem base in this tube (`expect_overlap` head_tube↔stem in z ≥ 0.02).
- **Slot C fold (folding_hinge only):** the column splits inside Slot A. `lower_stem` + `hinge_barrel` stay child of body via steering; `upper_stem` is child of `steering_column` via `fold_hinge` REVOLUTE, axis X (`(-1,0,0)`), origin = `hinge_local` (= HINGE_WORLD − HEAD_BASE), range 0..150°. Bar+grips migrate from the column to `upper_stem` in this module.
- **Slot B ↔ wheels:** body carries the rear axle line (REAR_WHEEL_Y=−0.235, AXLE_Z=WHEEL_R=0.09) and the front_neck→head riser. Deck form changes must keep rear-axle Y and deck-top z < 0.15 so wheels reach ground.
- **Slot A ↔ front wheel:** fork legs (on `steering_column`) straddle the front hub at `fw_axle_local`; `front_wheel_roll` CONTINUOUS, axis X, origin = fw_axle_local.

## 每槽位 Module Emits / Interfaces

### Slot A / module curved_swept
| emits | 描述 | 来源 |
|---|---|---|
| parts | `curved_stem`, `fork_leg_0/1`, `handlebar_crossbar`, `gooseneck`, `grip_0/1`, `front_fender` (all visuals on `steering_column`) | S0 / L256-326 |
| internal joints | none internal to module (column is one rigid part) | S0 |
| upstream interface | stem base seats in body `head_tube` at HEAD_BASE; consumed by `steering` revolute | S0 / L333-344 |
| downstream interface | fork legs present `fw_axle_local` axle for `front_wheel_roll` | S0 / L365-373 |

### Slot A / module tbar_straight
| emits | 描述 | 来源 |
|---|---|---|
| parts | `straight_stem`, `fork_leg_0/1`, `handlebar_crossbar`, `stem_cap`, `grip_0/1`, `front_fender` | S1 / L256-321 |
| internal joints | none | S1 |
| upstream interface | straight tube along STEER_AXIS (len `STEM_LENGTH`) seats in head_tube | S1 / L62,L256-268 |
| downstream interface | fork legs → fw_axle_local | S1 / L360-368 |

### Slot A / module bmx_riser
| emits | 描述 | 来源 |
|---|---|---|
| parts | short `stem`, U-bend `riser_bar`, `cross_brace`, `fork_leg_0/1`, `grip_0/1`, `front_fender` | S2 / L256-350 |
| internal joints | none (riser + brace are fixed visuals) | S2 |
| upstream interface | short stem seats in head_tube | S2 / L256-269 |
| downstream interface | fork legs → fw_axle_local; `cross_brace` must stay within `riser_bar` X-envelope | S2 / L298-310, L492-497 |

### Slot A / module swept_cruiser
| emits | 描述 | 来源 |
|---|---|---|
| parts | `curved_stem`, wide `cruiser_bar`, `gooseneck`, tangent `grip_0/1`, `fork_leg_0/1`, `front_fender` | S3 / L256-354 |
| internal joints | none | S3 |
| upstream interface | curved stem seats in head_tube | S3 / L256-271 |
| downstream interface | fork legs → fw_axle_local; grips swept back/wide (±X large) — must clear front_neck at full steer | S3 / L297-345 |

### Slot B / module running_board
| emits | 描述 | 来源 |
|---|---|---|
| parts | `foot_deck` (box), `branding`, `front_neck`, `head_tube`, `rear_fender`, `rear_strut` (all body visuals) | S0 / L137-199 |
| internal joints | none (body is root) | S0 |
| upstream interface | root; world frame | S0 |
| downstream interface | `head_tube` = steering bearing at HEAD_BASE; rear-axle line at (REAR_WHEEL_Y, AXLE_Z) | S0 / L165-169, L226-234 |

### Slot B / module flat_plank
| emits | 描述 | 来源 |
|---|---|---|
| parts | filleted CadQuery `foot_deck`, `grip_tape`, `front_neck`, `head_tube`, `rear_fender`, `rear_strut` | S4 / L141-197 |
| internal joints | none | S4 |
| upstream interface | root; world frame | S4 |
| downstream interface | same head_tube bearing + rear-axle line (deck-top z still < 0.15) | S4 / L141-165 |

### Slot C / module rigid
| emits | 描述 | 来源 |
|---|---|---|
| parts | (none extra — Slot A geometry is one whole `steering_column`) | S0 / L242-326 |
| internal joints | only the cross-slot `steering` revolute | S0 / L333-344 |
| upstream interface | — | S0 |
| downstream interface | — | S0 |

### Slot C / module folding_hinge
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lower_stem` + `hinge_barrel` (on column); `upper_stem` part = `upper_stem_tube`, `handlebar_crossbar`, `gooseneck`, `grip_0/1`, `hinge_plate_0/1`, `hinge_pin`, release lever | S5 / L271-283, L314-320, L345-418 |
| internal joints | `fold_hinge` REVOLUTE, parent=steering_column child=upper_stem, axis X (−1,0,0), origin hinge_local, 0..150° | S5 / L428-440 |
| upstream interface | lower_stem seats in head_tube; HINGE_WORLD=(0,0.120,0.500) | S5 / L66, L271-283 |
| downstream interface | bar+grips ride on upper_stem; clevis `hinge_plate_i` + `hinge_pin` straddle `hinge_barrel` (captured-pin allow_overlap) | S5 / L394-410 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `handlebar_form` | enum | {curved_swept, tbar_straight, bmx_riser, swept_cruiser} | — | choice | deterministic procedural sampler | Slot A table |
| `deck_form` | enum | {running_board, flat_plank} | — | choice | deterministic procedural sampler | Slot B table |
| `stem_articulation` | enum | {rigid, folding_hinge} | — | choice | deterministic procedural sampler; gates an extra part+joint | Slot C table |
| `rear_wheel_count` | int | [1, 2] | 1 | choice | weighted (N=1 high freq, N=2 rarer); total wheels = 1 + N_rear | multiplicity |
| `palette_style` | enum | {vintage_green, chrome_classic, racer_red, midnight_black, candy_blue, cream_whitewall} | vintage_green | choice | per-seed colorway sample; recolors body/stem/grip/tire/whitewall/metal | materials L123-131 (all sources) |
| `deck_length_scale` | float | [0.85, 1.20] | 1.0 | independent | scales deck Y extent; clamp so deck stays between wheels | S0 L137 / S4 L141 |
| `deck_top_z_scale` | float | [0.85, 1.10] | 1.0 | inequality | `DECK_TOP_Z·scale + deck_thick/2 < 0.15` (deck-top low) and ≥ AXLE clearance;回缩 if violated | tests L398-401 |
| `stem_height_scale` | float | [0.92, 1.12] | 1.0 | inequality | column top z must satisfy `> 0.78` (tall-bar test); clamp to keep ≥ 0.78 | tests L432-436 |
| `handlebar_width_scale` | float | [0.85, 1.25] | 1.0 | conditional | grip half-span; upper bound lower for swept_cruiser/bmx_riser (already wide) so grips clear front_neck at ±40° steer | S2 L335-341 / S3 L325-345 |
| `wheel_radius_scale` | float | [0.90, 1.15] | 1.0 | equation | `AXLE_Z = WHEEL_R·scale` (wheels rest on ground; axle height derives from radius) | S0 L48,L53 |
| `rear_track_scale` | float | [0.80, 1.20] | 1.0 | conditional | only active when `rear_wheel_count == 2`; scales REAR_TRACK; clamp so wheels clear deck width | S6 L56-59,L126-128 |
| `steer_range` | float (deg) | [30, 45] | 40 | independent | steering revolute ±range; clamp ≤45 to stay in toy regime | S0 L340-343 |
| `fold_range` | float (deg) | [120, 155] | 150 | conditional | only when `stem_articulation == folding_hinge`; upper of fold_hinge | S5 L436-439 |
| (—) | constraint | — | — | inequality | front wheel ahead of rear: `FRONT_WHEEL_Y − REAR_WHEEL_Y > 0.30` after any deck_length_scale; 回缩 | tests L424-428 |
| (—) | constraint | — | — | conditional | `bmx_riser` cross_brace center z ∈ (0.50,0.75) and within riser X-envelope after stem_height_scale | S2 L481-497 |

## Multiplicity / Copy Logic

One multiplicity axis (rear wheels). Front wheel is always singular (the steered wheel).

- **count_param:** `rear_wheel_count` (the only variable copy axis).
- **N_range:** rear_wheel_count ∈ **[1, 2]** (total wheels [2, 3]). Test-small = {1, 2}; product-full = identical {1, 2} — a kid tri-wheel tops out at 3 total. **Do not push N_rear > 2**: a 4-wheel object exits the kick-scooter category.
- **sampling domain (weights):** N_rear=1 high frequency (classic two-wheel scooter), N_rear=2 rarer (tri-wheel toddler form). Suggested ~70/30.
- **copied object:** one rear road wheel = shared `_wheel_meshes("rear_{i}")` helper (rim + tire + whitewall + off-axis valve marker), S0 L91-117 / S6 L241-271.
- **naming:** `rear_wheel_{i}` parts; visuals `rear_rim_{i}`/`rear_tire_{i}`/`rear_whitewall_{i}`/`rear_valve_{i}`; joints `rear_wheel_roll_{i}`.
- **placement:** symmetric left/right offsets along X on a shared rear axle at REAR_WHEEL_Y, AXLE_Z. Single rear wheel (N=1) is centered (i=0, x=0). For N=2, `rear_wheel_x(i) = −REAR_TRACK/2 + i·REAR_TRACK` (S6 L126-128), plus a visible `rear_axle` beam + central brace and per-wheel rear fenders (S6 L182-236).
- **joint policy:** one CONTINUOUS roll joint per rear wheel, axis (1,0,0), child of body, origin = `(rear_wheel_x(i), REAR_WHEEL_Y, AXLE_Z)` at the actual hub face; uniform across the loop. Front wheel keeps its own CONTINUOUS roll as child of steering_column.
- **gating:** N_rear=2 activates `rear_track_scale` and the rear_axle beam/brace furniture; N_rear=1 omits them (single centered fender like the parent).

## 拓扑多样性审计

总组合数：Slot A (4) × Slot B (2) × Slot C (2) × N_rear (2 samples) = **32** distinct topologies (before continuous-scale variation).

理由：32 structural combos ≥ 10 even before scale sampling; each axis flips real part/joint structure (different stem part trees, deck primitive, ±fold part+joint, ±rear-wheel part+joint), so distinct-topology fingerprints will be well above the 10 floor.

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan: `config_from_seed` deterministically draws `handlebar_form`, `deck_form`, `stem_articulation` uniformly over their enums, `rear_wheel_count` via the weighted 1/2 draw, `palette_style` over the 6 colorways, then samples the independent continuous scales, derives the `equation` scales (AXLE_Z from wheel_radius_scale), and projects/回缩 the `inequality`/`conditional` constraints (deck-top z < 0.15, column top > 0.78, front-ahead-of-rear > 0.30, swept/bmx grip-width clamp, fold/track conditional ranges). `slot_choices_for_seed` returns implemented module names matching the build. No closed-loop joints. Topology target: 1000-seed distinct expected ≥ 32 (combinatorial ceiling); below the usual ≥300 because the category is genuinely small (a kick scooter has few legal structural axes) — documented here, not a defect. A few regression overrides may be reserved for known-bad combos only (none required at spec time).（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization: `deck_length_scale`, `deck_top_z_scale`, `stem_height_scale`, `handlebar_width_scale`, `wheel_radius_scale`, `rear_track_scale`, `steer_range`, `fold_range` — ranges and constraint types per §7. All clamped/derived in `resolve_config`; none may break the head_tube bearing seat, the fw_axle interface, the rear-axle ground contact, or category identity. Cross-part dependencies (AXLE_Z↔wheel_radius, deck-top inequality, front-ahead-of-rear, grip-clearance conditional) are declared as equation/inequality/conditional rows, not free variables.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | order A→B→C→N→palette→scales; uniform enums, weighted N, then clamp/derive | slot_choices_for_seed matches build choices |
| compatibility matrix | folding_hinge × (swept_cruiser/bmx_riser): fold envelope must avoid deck + front_fender; swept/bmx wide bars must avoid grip sweeping front_neck at ±40°. Both isolated-tested only; the sampler may emit them but the builder must clamp/clear. flat_plank works with any A/C/N. No hard-illegal pairs. | no floating, collision, joint axis/range, fold closed-pose, max-multiplicity, optional-child failures |
| controlled local variation | the 8 scales above, clamped per §7 | proportions vary without breaking interfaces, clearance, support, joint origin, identity |
| regression overrides | none / reviewer-selected only | previously failed cases only |
| random sweep | seeds 0-49 initial pass, 0-999 maturity audit | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A (handlebar) | 4 | yes | yes | |
| B (deck) | 2 | yes | no | only 2 distinct deck forms in 5★ pool; degrade documented |
| C (stem articulation) | 2 | yes | no | rigid vs. folding_hinge are the only two topologies; degrade documented |

## Validator

- slot_choices_for_seed returns implemented module names
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating handles folding × wide-bar envelope and grip-clearance at full steer
- optional regression overrides are sparse and justified
- final template does not endlessly cycle a small curated table as the main seed domain
- controlled local scale params are clamped and cannot break the head_tube seat, fw_axle interface, rear-axle ground contact, or fold pose
- cross-part scale dependencies (AXLE_Z=f(wheel_radius), deck-top inequality, front-ahead-of-rear, grip clearance, fold/track conditionals) are resolved in `resolve_config`
- critical InterfaceSpec/MatingContract points exist: head_tube↔stem seat (z-overlap ≥ 0.02), fw_axle_local, rear-axle line, hinge_local (folding)
- key joints: `steering` REVOLUTE axis STEER_AXIS ±40°; `front_wheel_roll`/`rear_wheel_roll_{i}` CONTINUOUS axis X; `fold_hinge` REVOLUTE axis X 0..150° (folding only)
- copied rear wheels follow `rear_wheel_{i}` naming + symmetric X placement on shared axle

## Reject cases

1. Deck top z ≥ 0.15 (deck not low) or deck not flat (z-extent ≥ 0.05) → fails deck-low/flat checks.
2. Either wheel fails to reach ground (`min z ≥ 0.02`) after wheel_radius/deck scaling — AXLE_Z not derived from WHEEL_R.
3. Front wheel not ahead of rear (`FRONT_WHEEL_Y − REAR_WHEEL_Y ≤ 0.30`) after deck_length_scale.
4. Handlebar/stem top z ≤ 0.78 (bars too short) after stem_height_scale clamp failure.
5. Steering moves the rear wheel (rear-wheel-on-fixed-body broken) — rear wheels mis-parented to column.
6. Stem not seated in head_tube (head_tube↔stem z-overlap < 0.02) — Slot-A stem base authored without `_rel`/HEAD_BASE.
7. rear_wheel_count > 2 or front wheel duplicated (exits kick-scooter category / wrong multiplicity axis).
8. folding_hinge upper_stem fold collides with deck/front_fender at full fold, or swept/bmx grips sweep through front_neck at ±40° steer (un-clamped width/clearance).

## 与相邻类别的边界

- 不该混入：**motorized/electric scooter** — kick scooter is foot-propelled; no motor, battery deck, throttle, or brake lever module. Keep the deck a passive stand-on platform.
- 不该混入：**seated mobility scooter / 4-wheel scooter** — rear_wheel_count is capped at 2 (total ≤ 3); no seat, no fourth wheel; ≥4 wheels exits the category.
- 不该混入：**bicycle / BMX bike** — single rider stands on a deck, not pedals on a seated frame; the bmx_riser candidate borrows only the bar shape, not a crank/seat/chain.
- 不该混入：**push-scooter trike toy with a basket / ride-on** — no seat, no enclosing body; only deck + steering + wheels.

## Multiplicity / Copy Logic 注记（cross-check）
Single axis only (`rear_wheel_count`); front-wheel singular. No Slot exposes any other `*_count`. Confirmed against S6 loop (L205-271).

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Slot B and Slot C each degraded to 2 candidates (documented, only 2 structurally distinct forms exist in the 5★ pool). Open questions: (1) accept 2-candidate B/C or request a 3rd deck/fold fork before template build? (2) confirm 70/30 weighting for rear_wheel_count. (3) confirm palette_style 6-colorway list — vintage_green is the only colorway actually present in source materials; the other 5 are plausible kick-scooter colorways proposed for downstream sampling, not observed in the 5★ sources. |
