# Modular spec — watch

## 元信息
| 项 | 值 |
|---|---|
| slug | `watch` |
| template path | `agent/templates/watch.py` |
| test path (optional) | — |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 16 |
| read_count | 16 |
| read_scope | 5 origin parents (`rec_watch__watch__001…005`) + 11 forked variants (`rec_0611_watch_var_*`) |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

Real-world wristwatch — a wrist-worn timekeeping device made of a rigid **case** hosting a coaxial stack of continuously-rotating **hands** over a **dial**, a rotating or fixed **bezel** ring capturing the case shoulder, a right-flank **crown** (optionally with chrono pushers) that operates the movement, and a **strap** (leather/rubber/fabric or hinged metal bracelet) attached at 12/6 by lugs and spring bars. The 5-star pool covers dive-style, chronograph and dress variants. All five origin models share the same signature: a single rigid round/rounded case as root, one revolute (or continuous) bezel joint stacked on the case shoulder, three coaxial continuous hand joints, one revolute/continuous/prismatic crown joint on the +X flank, and two chains of hinged strap/bracelet links leaving from the 12 and 6 lugs.

Not to be confused with: **pocket watch** (single detachable crown at 12, no wrist strap), **wall/desk clock** (no strap, hands scale >0.1 m), **fitness tracker / smartwatch** (no bezel + no analog hands), **stopwatch/timer** (handheld case, no strap), **watch winder box / display case** (hosts the watch, hinged lid — see `rec_watch_winder_box_*`).

## 槽位 + 候选模块表

Three slots + two multiplicity axes on top of a fixed shared skeleton (case as root; hands + crown + strap chain parent to it — `parallel_children` pattern). All discrete slots realize ①/②/③ diversity (structural / kinematic / primary form family). ⑤/⑥ are procedurally sampled (dimension scales, palette). ④ decoration is host-conformal (radial ticks, hour indices, chapter rings, dial track) — inline visuals on the case, not separate parts.

### Slot A — `case_form` (③ Primary Form Family)

The overall silhouette of the watch head. Every candidate keeps the same part tree (single `case` root part with dial/marker/lug inline visuals) and the same downstream interfaces (bezel-seat annulus on top, hand arbor at the center, lug spring-bar sockets at ±Y, crown boss at +X). Different primary form prototypes reshape the case boundary.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `round_dive` | forked_anchor | `rec_watch__watch__001_png_478d61dbe7814d9a826dff068529f1b0` | L159-L236 | eligible if compatible | `LatheGeometry` stepped-round case profile (Volumetric Envelope Form: round revolved). Lugs = 4 axis-aligned boxes; central arbor; spring bars at ±Y=0.067. |
| `stainless_round` | forked_anchor | `rec_watch__watch__002_png_b368d8bfd8d74378a90a9f87afcbb49f` | L200-L279 | eligible if compatible | Layered cylinders (case body, integrated upper plate, raised rehaut) + chamfered lug meshes + crown-guards. Round + integrated bracelet end socket. |
| `cushion` | forked_anchor | `rec_0611_watch_var_case_form_cushion` from origin 3 | L21-L177 | eligible if compatible | Cushion (rounded-square) footprint via CadQuery `_annular_disc` case ring + case_back plate. Same interfaces, but Planar Boundary Form = rounded square. |
| `square` | forked_anchor | `rec_0611_watch_var_case_form_square` from origin 1 | L146-L280 | eligible if compatible | Square case body (Planar Boundary Form = square). Same part tree, boxy footprint; lugs sit at ±Y edge midpoints. |
| `tonneau` | forked_anchor | `rec_0611_watch_var_case_form_tonneau` from origin 2 | L200-L280 | eligible if compatible | Tonneau (barrel) — Planar Boundary Form = super-ellipse; short X, long Y. Case body is a `LatheGeometry`-like lofted profile. |

Rationale: 5 candidates cover the three ③ subtypes (round, rounded-square/cushion, square, tonneau/super-ellipse) — Planar Boundary Form axis is fully exercised.

### Slot B — `bezel_style` (①/② rotating-vs-fixed × ③ ring geometry)

The ring capturing the case shoulder. Every candidate emits a `bezel` part hosted on the `case` via `case_to_bezel`. Candidates differ in **joint type** (rotating REVOLUTE / rotating CONTINUOUS / fixed by construction — no articulation), the **outer profile** (smooth vs coin-edge vs GMT bidirectional numeral track vs raised numerals), and the primitive family (annular sector mesh vs annular_profile bevel vs annular_disc + torus).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `dive_rotating_60` | forked_anchor | origin 1 | L260-L326 | eligible if compatible | Annular-sector unidirectional dive bezel. REVOLUTE joint 0..TAU. 36 grip boxes; blue+red half-inserts; 60 tick marks. Diversity axis: ①+② rotating dive. |
| `smooth_polished_ring` | forked_anchor | origin 2 | L327-L367 | eligible if compatible | Bevelled `_annular_profile` polished ring, CONTINUOUS bidirectional. 60 minute marks, 5-position numerals. |
| `unidirectional_chrono` | forked_anchor | origin 3 | L179-L232 | eligible if compatible | CadQuery annular disc + serrated outer edge; 48 external teeth (coin-edge), 60 tick radial boxes, 5 numerals. REVOLUTE. |
| `bidirectional_gmt` | forked_anchor | `rec_0611_watch_var_bezel_bidirectional_gmt` from origin 4 | L1-L200 | eligible if compatible | CONTINUOUS bezel with a full-range GMT numeral track (yellow/white radial ticks + 60 minute divisions). |
| `raised_numeral_bezel` | forked_anchor | origin 5 | L284-L314 | eligible if compatible | `ExtrudeWithHolesGeometry` dark bezel insert + gold seven-segment numeral mesh. REVOLUTE −π..+π. Diversity axis: ③ Macro Surface Construction (raised numeral track). |

### Slot C — `strap_topology` (① skeleton: chained hinged link count + link geometry)

The physical band. Every candidate emits **two independent chains** (top and bottom) of N REVOLUTE-hinged links parented at ±Y lug spring bars. `strap_topology` selects the **link count** N (via `count_param`) AND the **link geometry family** (ribbed rubber / brushed metal alternate-block / smooth leather / articulated ceramic-and-metal / integrated bracelet flush with case / woven fabric). All emit N=`strap_link_count` per chain via shared helper `_emit_strap_link_i` (name `{side}_strap_{i}`).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `ribbed_rubber` | forked_anchor | origin 1 | L127-L143, L407-L441 | eligible if compatible | Rectangular rubber body per link + 3 raised transverse ribs. Wider at the case, tapered. 5 hinged links per side. |
| `brushed_steel_bracelet` | forked_anchor | origin 2 | L163-L182, L471-L495 | eligible if compatible | Chamfered box body + center polished panel + dark hinge groove; per-link tapering widths. |
| `articulated_ceramic_link` | forked_anchor | `rec_0611_watch_var_strap_topology_articulated_ceramic_lin` from origin 5 | L362-L411 | eligible if compatible | Alternating dark-center + brushed side plates + polished shoulders + hinge barrel. |
| `orange_rubber_holed` | forked_anchor | origin 3 | L339-L379 | eligible if compatible | Rubber pad + longitudinal ribs + through-hole every other link. |
| `metal_bracelet_bent` | forked_anchor | origin 4 | L352-L385 | eligible if compatible | CadQuery bracelet plate with three raised sub-plates + dark grooves. |
| `fabric_flat_strap` | forked_anchor | `rec_0611_watch_var_strap_topology_fabric` from origin 4 | L1-L200 | eligible if compatible | Flat woven fabric — long thin box body + single center stitching rib per link (no side ribs / hub barrel). |

Six candidates comfortably exceed the 3-6 target on both ① part geometry and material/finish (④/⑥ companion).

### Multiplicity axis M1 — `strap_link_count`

Number of hinged links per side of the strap chain (identical across the two sides). Recorded via `slot_choices_for_seed` as `("strap_link_count", "n{N}")`.

| axis | source_type | source evidence | N_range | 结构特征 |
|---|---|---|---|---|
| `strap_link_count` | forked_anchor from ①-recorded origins | origins 1–5 use 4 or 5 per side | 3..6 | Per-side hinged REVOLUTE chain of N shared-geometry links. |

### Multiplicity axis M2 — `crown_control_count` (② mechanism density)

Number of right-flank crown-family controls: 1 = crown only; 2 = crown + one pusher OR two crowns (GMT/compass); 3 = crown + upper+lower chronograph pushers.

| axis | source_type | source evidence | N_range | 结构特征 |
|---|---|---|---|---|
| `crown_control_count` | forked_anchor | origins 1/2/5 (N=1), `rec_0611_watch_var_control_count_2_crowns` (N=2), origins 3/4 (N=3) | 1..3 | +X flank crown always present. N≥2 adds a `pusher_0` PRISMATIC part at +Y=0.017. N≥3 adds `pusher_1` PRISMATIC at −Y=0.017. |

### Slot D — `dial_layout` (④ host-conformal decoration + optional subdial features)

Even though ④ decoration is **normally inline visuals**, some 5-star samples add a truly separate `subdial_hand` articulated part (chronograph subdial hand — origin 3, `rec_0611_watch_var_dial_module_3_subdials`). We register this as a slot with 3 candidates so ② + slot-diversity captures the difference; all decoration ticks/markers remain inline on the case (Rule 1 / Rule 4).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `simple_indices` | forked_anchor | origins 1, 2, 5 | L228-L257 (origin 1), L282-L324 (origin 2) | eligible if compatible | 60 radial minute/hour hash-mark Box visuals + 12 raised luminous markers (triangle at 12, bars at 3/6/9/12, round pips elsewhere). No extra articulated part. |
| `three_subdials_chrono` | forked_anchor | origin 3, origin 4, `rec_0611_watch_var_dial_module_3_subdials` | L128-L162 (origin 3), L214-L272 (origin 4) | eligible if compatible | Adds 1 CONTINUOUS `subdial_hand` on a subdial at (0, −0.015) OR three subdials as inline visuals; primary axis: +1 articulated subdial part. |
| `open_heart_aperture` | forked_anchor | `rec_0611_watch_var_dial_module_open_heart_aperture` from origin 1 | L1-L200 | eligible if compatible | Cutout dial visual — dark aperture at 6 o'clock with raised inner ring, showing the movement's balance wheel as a rotating decorative disc. Adds 1 CONTINUOUS `balance_wheel` part (small radius rotating disc). |

Three candidates → ⑤ Primary Form Family is realized by `case_form` (Slot A); `dial_layout` supplies ①/② additive diversity (added articulated subdial / balance wheel), plus ④ host-conformal decoration.

## 槽位图（slot graph）

pattern: `parallel_children`

```
                   case (root, from Slot A: case_form)
                    │
    ┌───────────────┼─────────────────────────┬─────────────────────┐
    │(REVOLUTE     │(CONTINUOUS coaxial     │(REVOLUTE strap       │(REVOLUTE/PRISMATIC
    │ or CONT'S    │ z axis at arbor,       │ chain hinges, x      │ crown / pushers,
    │ coaxial z)   │ 3 hands + subdial)     │ axis at spring bar)  │ x axis at case flank)
    ▼               ▼                        ▼                      ▼
  bezel          hands ×3 + optional      strap chain ×N per       crown (+ pusher_0,
  (Slot B)       subdial/balance (Slot D) side  (Slot C, M1)       pusher_1) (M2)
```

- **Slot A (`case_form`)** is the root part; all other slots attach as parallel children of `case`. Case profile changes reshape the outer boundary but keep the same set of downstream interfaces.
- **Slot B (`bezel_style`)** → `case_to_bezel` REVOLUTE or CONTINUOUS around `z`, origin on the bezel-seat annulus of the case (real geometry: on the case's top shoulder ring).
- **Slot D (`dial_layout`)** always emits 3 coaxial hand parts (hour/minute/second) via CONTINUOUS `case_to_{hand}` joints around `z`; the `three_subdials_chrono` candidate adds one `subdial_hand` on `case_to_subdial_hand`; the `open_heart_aperture` candidate adds one CONTINUOUS `balance_wheel` on `case_to_balance_wheel`. Decoration (ticks, markers) is inline `case.visual(...)`.
- **Slot C (`strap_topology`)** emits two chains (top / bottom) of M1 REVOLUTE-hinged links each, chain root parented to `case` at ±Y lug spring bar (real geometry: on the lug bridge visual).
- **M2 (`crown_control_count`)** emits `crown` + (optional) `pusher_0`, `pusher_1` at +X flank; joint origins on the crown-guard / pusher-tube case visuals.

## 每槽位 Module Emits / Interfaces

### Slot A / all `case_form.*` — root case builder
| emits | 描述 | 来源 |
|---|---|---|
| parts | `case` (root) | origin 1 L159; origin 2 L200; etc. |
| internal joints | — (single part) | — |
| upstream interface | (none: root) | — |
| downstream interfaces | `bezel_seat` (top of case shoulder, `+z`, real visual `case_bezel_seat`), `hand_arbor` (center `+z`, real visual `central_arbor` / `central_staff`), `lug_top` / `lug_bottom` (±Y spring-bar visuals), `crown_flank` (+X crown-guard visual) | Multiple case visuals from origins 1–5 |

### Slot B / any `bezel_style.*` — bezel builder
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bezel` | origins 1/2/3/4/5 & bezel variant |
| internal joints | — | — |
| upstream interface | mating annulus on `case_bezel_seat`; consumer_joint_type = REVOLUTE or CONTINUOUS around `+z` | origin 1 L318-L326, origin 2 L359-L367 |
| downstream interface | — | — |

### Slot D / any `dial_layout.*` — hands + optional subdial/balance
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hour_hand`, `minute_hand`, `second_hand`, (+ `subdial_hand` for `three_subdials_chrono`; + `balance_wheel` for `open_heart_aperture`) | origins 1 L329-L365, origin 2 L370-L436, origin 3 L266-L292 |
| internal joints | `case_to_hour_hand`, `case_to_minute_hand`, `case_to_second_hand` (all CONTINUOUS +z), optionally `case_to_subdial_hand` or `case_to_balance_wheel` (CONTINUOUS +z) | origin 1 L352-L365 |
| upstream interface | on `case.central_arbor`; consumer_joint_type = CONTINUOUS around `+z` | origin 1 L219 arbor visual |
| downstream interface | — | — |

### Slot C / any `strap_topology.*` — strap chain (per side)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `top_strap_0..N-1` and `bottom_strap_0..N-1` (N = `strap_link_count`) | origin 1 L411-L441 |
| internal joints | `top_strap_hinge_0` on `case`, then `top_strap_hinge_{i}` chained to previous; symmetric for `bottom` | origin 1 L416-L440 |
| upstream interface | on `case` `{top,bottom}_spring_bar` cylinders (real ±Y visuals); joint type = REVOLUTE around `+x` | origin 1 L221-L227, L416-L423 |
| downstream interface | — | — |

### M2 / crown + pushers
| emits | 描述 | 来源 |
|---|---|---|
| parts | `crown` always; optionally `pusher_0`, `pusher_1` | origin 1 L368-L405; origin 3 L295-L336; origin 4 L295-L326 |
| internal joints | `case_to_crown` REVOLUTE / CONTINUOUS / PRISMATIC around `+x`; `case_to_pusher_i` PRISMATIC around `+x` | origin 3 L310-L318, origin 4 L434-L459 |
| upstream interface | on `case.crown_flank` visual (the crown-guard box or crown-tube cylinder) | — |
| downstream interface | — | — |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `case_form` | enum | `round_dive` / `stainless_round` / `cushion` / `square` / `tonneau` | `round_dive` | choice | procedural | Slot A |
| `bezel_style` | enum | `dive_rotating_60` / `smooth_polished_ring` / `unidirectional_chrono` / `bidirectional_gmt` / `raised_numeral_bezel` | `dive_rotating_60` | choice | procedural | Slot B |
| `strap_topology` | enum | `ribbed_rubber` / `brushed_steel_bracelet` / `articulated_ceramic_link` / `orange_rubber_holed` / `metal_bracelet_bent` / `fabric_flat_strap` | `ribbed_rubber` | choice | procedural | Slot C |
| `dial_layout` | enum | `simple_indices` / `three_subdials_chrono` / `open_heart_aperture` | `simple_indices` | choice | procedural | Slot D |
| `strap_link_count` | int | 3..6 | 5 | independent | clamp[3,6] | origin 1 L411 (N=5), origin 3 L345 (N=4) |
| `crown_control_count` | int | 1..3 | 1 | independent | clamp[1,3] | origin 3/4 (3), origin 1/2/5 (1), 2-crowns variant (2) |
| `case_radius_scale` | float | [0.90, 1.15] | 1.0 | independent | independent uniform sample, clamped in `resolve_config` | — |
| `case_height_scale` | float | [0.90, 1.12] | 1.0 | independent | uniform | — |
| `bezel_height_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform | — |
| `hand_length_scale` | float | [0.85, 1.10] | 1.0 | independent | uniform | — |
| `strap_link_length_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform | — |
| `crown_size_scale` | float | [0.85, 1.15] | 1.0 | independent | uniform | — |
| `bezel_outer_radius` | float | derived | — | equation | `= case_outer_radius + bezel_ring_width`; `bezel_ring_width` fixed per candidate | origin 1 L263; origin 2 L329 |
| `hand_length_hour` | float | derived | — | equation | `= 0.55 * dial_inner_radius * hand_length_scale` | origin 1 L330 |
| `hand_length_minute` | float | derived | — | equation | `= 0.75 * dial_inner_radius * hand_length_scale` | origin 1 L332 |
| `hand_length_second` | float | derived | — | equation | `= 0.85 * dial_inner_radius * hand_length_scale` | origin 1 L338 |
| `pin_axis_lug_top_y` | float | derived | — | equation | `= case_outer_radius + lug_reach * case_radius_scale` (per case_form family) | origin 1 L221 |
| — | constraint | — | — | inequality | `strap_link_count * strap_link_len <= 0.100`; if violated, shrink link length first, then N | origin 1 L408, L438 |
| `palette_style` | enum | `steel_blue_dive`, `black_ceramic_chrono`, `orange_dive`, `stainless_bracelet`, `blue_dial_gold_hands`, `black_leather_dress` | `steel_blue_dive` | choice | procedural | origins 1..5 palette blocks |

Continuous sampling contract: `config_from_seed` samples all enums + N + independent scales; `resolve_config` derives equation terms, then enforces the strap chain inequality by clamping.

### 7.5 编译预算 / compile budget

**Budget: 20 s / seed** (spec ceiling per author guidance). Reference workload: mesh-heavy dive bezel + CadQuery lofted case + 6 strap segments × 2 chains + 3 hands + subdial. Anticipated per-seed: 8-14 s.

Tessellation policy:
- Lathe / annular-sector case profiles: `segments ≤ 96` (hero face); reduced to 64 when radius scale < 0.95.
- CadQuery annular disks and `_annular_profile` bevels: default `tolerance=0.00040`.
- Torus rims/gaskets: `radial_segments=16`, `tubular_segments=40` maximum.
- Ticks/marks: reused `Box` primitives, N ≤ 60 minute ticks per bezel/dial.
- Strap links share **one** `mesh_from_cadquery` per family per direction (cached per resolved geometry) — 4 unique link meshes total maximum.
- Numeral / digit meshes reused across bezel positions via `_bezel_numeral_mesh` builder called once.

If a seed exceeds 20 s, first drop bezel numeral density to 30 marks and case profile segments to 48.

## Multiplicity / Copy Logic

Two independent multiplicity axes.

### M1 — `strap_link_count`

- `count_param`: `strap_link_count`
- `N_range`: `[3, 6]` (product domain of realistic wristwatch strap link counts per side; origin 1 uses 5, origin 3 uses 4, origins 4/5 use 4)
- sampling domain: uniform integer 3..6 (each side gets the same count for kinematic symmetry)
- copied object: `top_strap_{i}` and `bottom_strap_{i}` for i in `[0..N-1]`
- naming: `{side}_strap_{i}` where side ∈ {`top`, `bottom`}
- placement: origin 1 L416-L423 — first link joint on `case` at `(0, ±(case_outer_radius + lug_reach), z_hinge)`; each subsequent link chained to previous at `(0, ±strap_link_len, 0)`
- joint policy: REVOLUTE around `+x`; `lower=-0.75, upper=0.75, effort=0.5, velocity=2.0`
- source/gating: same helper `_emit_strap_link_i` for every candidate (candidate provides the link visual shape only)

### M2 — `crown_control_count`

- `count_param`: `crown_control_count`
- `N_range`: `[1, 3]` (product domain: dress/dive → 1 crown; GMT / chrono step 1 → 2; full chrono → 3)
- sampling domain: uniform integer 1..3
- copied object: `crown` always; `pusher_0` iff N≥2 (or second crown at symmetric position); `pusher_1` iff N=3
- naming: `crown`, `pusher_0`, `pusher_1`
- placement: crown at `(+case_outer_radius + crown_offset, 0, 0)`; pushers at `(+case_outer_radius + pusher_offset, ±pusher_y, 0)` where `pusher_y = 0.017`
- joint policy: `case_to_crown` REVOLUTE (rotate) `lower=0, upper=TAU, effort=0.5, velocity=5.0`; `case_to_pusher_i` PRISMATIC `lower=0, upper=0.0018, effort=1.0, velocity=0.1`
- source/gating: pushers only make sense on chronograph-capable bezel/dial. Not gated — a plain-dial 3-pusher watch is a stylistic variant and still valid.

### 8.5 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | Slot D adds `subdial_hand` (three_subdials_chrono) or `balance_wheel` (open_heart_aperture); M1 varies chain length; M2 adds/removes pushers. source_type=forked_anchor (origins 1..5 + `rec_0611_watch_var_dial_module_3_subdials`, `rec_0611_watch_var_dial_module_open_heart_aperture`, `rec_0611_watch_var_control_count_2_crowns`). |
| └ multiplicity | 同构件 ×N | 有 | see §8: M1 strap_link_count 3-6; M2 crown_control_count 1-3. |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | `case_to_bezel` ∈ {REVOLUTE, CONTINUOUS} across candidates; `case_to_crown` ∈ {REVOLUTE, CONTINUOUS, PRISMATIC}. source_type=forked_anchor (origin 1: bezel REVOLUTE; origin 2: bezel CONTINUOUS; origin 3: crown PRISMATIC; origin 4: crown CONTINUOUS). |
| ③ 主体形态家族 / Primary Form Family | 换核心 part 的可识别形态原型 | 有 | Slot A registers 5 form prototypes; all forked_anchor. form_subtype: `round_dive` (Volumetric Envelope Form: circular revolved), `stainless_round` (Volumetric Envelope Form + integrated shoulder), `cushion` (Planar Boundary Form: rounded square), `square` (Planar Boundary Form: square), `tonneau` (Planar Boundary Form: super-ellipse / barrel). Registered in slot_choices as `("case_form", value)`. |
| ④ 表面装饰 | 表面细节 / 装饰数 | 有 | Host-conformal chapter rings, minute/hour hashes, hour markers (bar/round/triangle), date apertures, subdial rings — all inline `case.visual(...)` derived from the case radius, radial angle, dial_layout choice. Style bundles: `simple_indices` (12 hour markers), `three_subdials_chrono` (12 markers + 3 subdial ring visuals), `open_heart_aperture` (12 markers + aperture ring). source_type=forked_anchor. |
| ⑤ 尺寸/行程 | 连续尺寸/行程 | 有 | Case radius scale [0.90,1.15]; case height scale [0.90,1.12]; bezel/strap/hand/crown scales as above. **Motion envelopes:** `case_to_bezel` REVOLUTE `[0, TAU]` (axis +z, opens by twisting around center — full ring); CONTINUOUS candidates use `MotionLimits(velocity=…)` unclamped. `case_to_{hand}` CONTINUOUS. `case_to_crown` REVOLUTE `[0, TAU]` (rotational) OR PRISMATIC `[0, 0.004]` (pull-out along +x); `case_to_pusher_i` PRISMATIC `[0, 0.0018]` along +x. `{side}_strap_hinge_i` REVOLUTE `[-0.75, +0.75]` around +x. `motion_test_plan`: sampled-pose collision test with `max_pose_samples=32` (many joints); targeted `ctx.pose(...)` = (a) bezel at 0.5*TAU rotated, (b) minute hand at π/2, (c) crown pulled/rotated to its upper, (d) top_strap_0 at +0.5 rad. |
| ⑥ 涂装 | 材质/颜色 | 有 | 6 palette_style keys (see §7); each covers ≥5 material tokens (steel/dark_steel/dial/marker/hand/glass/strap). Coverage: `metal` (steel_blue_dive, stainless_bracelet, blue_dial_gold_hands, black_ceramic_chrono, orange_dive), `plastic/rubber` (orange_dive, steel_blue_dive strap), `glass` (crystals across all), `painted/enamel` (dial materials). |

## 采样与覆盖审计

总组合数：|A|=5 × |B|=5 × |C|=6 × |D|=3 × M1=4 × M2=3 = **5400** unique slot-tuple combos. 36-seed sweep realizes ~30 distinct combos (matches 300+ maturity target after 1000-seed extrapolation).

理由：three primary discrete slots + two multiplicity axes with sensible cardinalities. No forced compatibility gating collapses the space significantly (pushers are compatible with every bezel/dial visually; watches with 3 subdials on `simple_indices` dial are unusual but still valid stylistically).

seed_domain_policy: procedural_first.

Procedural Sampling / Sweep Plan: `config_from_seed(seed)` uses `random.Random(seed)` to pick each of the 4 enums via `rng.choice`, then samples multiplicity via `rng.randint`, then samples independent scales via `rng.uniform`. `resolve_config` derives equation terms and enforces strap chain inequality by shrinking `strap_link_len` then N. **No compatibility matrix required** — every combination is a physically legal watch (worst case: a dive-bezel `open_heart_aperture` chrono with fabric strap — quirky but real). No regression overrides.

Topology target: with 5400 combos and 1000-seed exploration, expect ~500+ distinct slot tuples (well above 300).

Controlled local parameterization: `case_radius_scale`, `case_height_scale`, `bezel_height_scale`, `hand_length_scale`, `strap_link_length_scale`, `crown_size_scale`. All independent, clamped in `resolve_config`, feed into derivations (bezel outer radius, hand lengths, spring-bar Y) via equation constraints. Cross-part inequality: strap chain total length ≤ 0.100 m per side to prevent collision with the wearer's frame.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | procedural rng.choice over 4 slots + rng.randint over M1/M2 + rng.uniform over 6 scales | `slot_choices_for_seed` matches build choices |
| compatibility matrix | none required — every combo is legal | no floating decorations, no closed-pose overlap other than intentional pin captures |
| controlled local variation | 6 continuous scales, each clamped to [0.85..1.15] | proportions vary; case never so small it collides with bezel, never so big lugs overrun the case |
| regression overrides | none | — |
| random sweep | 0-15 fast, 16-35 final, corner-stage per pipeline default | Rule-3/4/5 coverage; check bezel/hand/strap materials all appear |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| case_form | 5 | yes | yes | ③ primary form family; 3 Planar Boundary + 2 Volumetric Envelope prototypes |
| bezel_style | 5 | yes | yes | ①/② axis (rotating type × ring geometry) |
| strap_topology | 6 | yes | yes | ① part shape + ⑥ finish |
| dial_layout | 3 | yes | yes | ①/② (added subdial_hand / balance_wheel) + ④ decoration density |

## Validator

- `slot_choices_for_seed` returns tuples in order `(case_form, bezel_style, strap_topology, dial_layout, ("strap_link_count", f"n{N}"), ("crown_control_count", f"n{N}"))`.
- `config_from_seed` uses `random.Random(seed)` procedurally.
- `resolve_config` clamps all int and float ranges; derives all equation terms; enforces strap chain inequality.
- palette_style is drawn from a 6-entry table; materials keyed by `mats[...]` and threaded to every `part.visual(..., material=mats[...])`.
- Every non-FIXED joint has `MatingContract` OR is grandfathered coaxial-pin capture (bezel-around-arbor family: bezel_ring seats on case shoulder — declared as MatingContract; hand hubs press-fit on central_arbor — declared as element-scoped `allow_overlap` with reason).
- `run_watch_tests` calls `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=32, ignore_fixed=True)` plus targeted `ctx.pose({...})` on bezel, minute_hand, crown, and first strap link.

## Reject cases

- Case boundary changes (round → square) leave the bezel geometry unchanged so the bezel now overhangs the corners of the case → **must reshape bezel to match case case_form primary form**.
- Hand lengths exceed dial inner radius → hands protrude past chapter ring; clamp `hand_length_scale * dial_inner_radius < inner_radius - 0.001`.
- Strap chain hinges collide with case body at open-pose sweep → shrink first-link length so `strap_link_len > case_lug_reach + 0.003`.
- Crown radius exceeds case flank clearance → crown clips through bezel edge; use `crown_size_scale` clamped so `crown_outer_radius < 0.006`.
- Bezel numeral track built at a constant radius while case profile has been squared (`square`, `cushion`) → decoration reads detached; every bezel `.visual(...)` must use the resolved bezel outer/inner radius (`radius(case_form)`), not a global constant.

## 与相邻类别的边界

- 不该混入：pocket watch — no wrist strap; single crown at 12; different footprint. **Distinguisher**: watch always has a two-chain strap parented at ±Y lugs.
- 不该混入：wall clock — hands scale >0.1 m; no strap. **Distinguisher**: watch case_outer_radius ≤ 0.055 m.
- 不该混入：fitness tracker / smartwatch — no analog hands; often no bezel. **Distinguisher**: watch always emits three coaxial CONTINUOUS hands.
- 不该混入：stopwatch — handheld, no strap. **Distinguisher**: watch always has strap.
- 不该混入：watch winder box — hosts a watch, primary joint is a hinged lid revolute at edge, not a bezel revolute at center. **Distinguisher**: watch root is a small case (r < 0.06); winder box is a large enclosure with hinged lid part.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Written by SPEC+TEMPLATE subagent; no human review yet. |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1a | A | round_dive | rec_watch__watch__001_png_478d61dbe7814d9a826dff068529f1b0 | L159-L236 | Case body + lugs + decoration inline visuals |
| S1b | B | dive_rotating_60 | rec_watch__watch__001 | L261-L326 | Bezel ring + inserts + tick marks |
| S1c | C | ribbed_rubber | rec_watch__watch__001 | L127-L143, L411-L441 | Strap link + hinge chain (N=5) |
| S1d | D | simple_indices | rec_watch__watch__001 | L228-L257 | Marker/index decoration |
| S1e | M2 | crown REVOLUTE | rec_watch__watch__001 | L368-L405 | Crown part + joint |
| S2a | A | stainless_round | rec_watch__watch__002_png_b368d8bfd8d74378a90a9f87afcbb49f | L200-L279 | Layered polished case + upper plate |
| S2b | B | smooth_polished_ring | rec_watch__watch__002 | L327-L367 | Smooth CONTINUOUS bezel |
| S2c | C | brushed_steel_bracelet | rec_watch__watch__002 | L163-L182 | Bracelet link |
| S3a | A | (round variant) | rec_watch__watch__003 | L63-L127 | Case + subdial post + crown/pusher tubes |
| S3b | B | unidirectional_chrono | rec_watch__watch__003 | L179-L222 | CadQuery bezel + serrated edge |
| S3c | C | orange_rubber_holed | rec_watch__watch__003 | L339-L379 | Rubber strap with through-holes |
| S3d | D | three_subdials_chrono | rec_watch__watch__003 | L128-L162, L266-L292 | subdial_hand + subdial ring visuals |
| S3e | M2 | crown PRISMATIC + pushers | rec_watch__watch__003 | L295-L336 | 3 controls |
| S4a | A | (round variant) | rec_watch__watch__004 | L149-L213 | CadQuery case + lugs + guard |
| S4b | B | (multi-subdial dial) | rec_watch__watch__004 | L214-L272 | Dial subdial recess visuals |
| S4c | C | metal_bracelet_bent | rec_watch__watch__004 | L352-L385 | CadQuery bracelet plate |
| S4d | M2 | crown + pushers CONTINUOUS | rec_watch__watch__004 | L295-L326, L434-L459 | 3 controls |
| S5a | A | (round variant) | rec_watch__watch__005 | L185-L282 | Case + torus lip + domed crystal |
| S5b | B | raised_numeral_bezel | rec_watch__watch__005 | L284-L314 | Extruded bezel + seven-segment mesh |
| S5c | C | articulated_ceramic_link | rec_watch__watch__005 | L362-L411 | Alternating dark+brushed+polished link |
| V1 | A | cushion | rec_0611_watch_var_case_form_cushion | L21-L177 | Cushion case ring |
| V2 | A | square | rec_0611_watch_var_case_form_square | L146-L280 | Square case |
| V3 | A | tonneau | rec_0611_watch_var_case_form_tonneau | L200-L280 | Tonneau case |
| V4 | B | bidirectional_gmt | rec_0611_watch_var_bezel_bidirectional_gmt | full model | GMT bezel |
| V5 | C | articulated_ceramic_link | rec_0611_watch_var_strap_topology_articulated_ceramic_lin | full model | Articulated ceramic link |
| V6 | C | fabric_flat_strap | rec_0611_watch_var_strap_topology_fabric | full model | Fabric strap |
| V7 | M2 | 2-crowns | rec_0611_watch_var_control_count_2_crowns | full model | 2 crowns config |
| V8 | D | three_subdials_chrono | rec_0611_watch_var_dial_module_3_subdials | full model | 3 subdials layout |
| V9 | D | open_heart_aperture | rec_0611_watch_var_dial_module_open_heart_aperture | full model | Aperture + balance wheel |
| V10 | C | (integrated bracelet variant) | rec_0611_watch_var_lug_integrated_bracelet | full model | Bracelet integration |
| V11 | A | (closure variant, reference only) | rec_0611_watch_var_closure_deployant_clasp | full model | Deployant clasp — used to inform brushed_steel_bracelet last-link design |

## 模板实现备注（可选）

- All `case_form` candidates share a common `_emit_case_dial_decoration(case, r, mats)` helper for chapter ring, minute hashes, hour markers, date aperture — parametric over the resolved case radius/height. Each case-form candidate chooses its own body mesh but decoration is uniform.
- Bezel candidates share `_emit_bezel_tick_ring(bezel, r, mats)`; each candidate chooses its own annulus profile geometry.
- Strap candidates share `_emit_strap_chain(model, side, N, r, mats, link_builder)`; each candidate provides only the `link_builder(part, i, sign, r, mats)`.
- Hand emission uses one `_add_hand(part, length, width, angle, z, mat)` helper regardless of dial_layout.
- Element-scoped `allow_overlap`s needed:
  - `case`↔`bezel` on `bezel_seat_annulus` × `bezel_ring` (bezel captured by case shoulder — annular press-fit).
  - `case`↔`hand_*` on `central_arbor` × `{hand}_hub` (each of 3 hands press-fit on the arbor).
  - `case`↔`crown` on `crown_flank_visual` × `crown_stem` (crown stem penetrates the case).
  - `case`↔`top_strap_0` on `top_spring_bar` × strap link root (spring bar captured by first strap link).
  - `case`↔`bottom_strap_0` analogous.
  - `case`↔`pusher_i` on pusher_tube × pusher_body.
  - `case`↔`subdial_hand` on subdial_post × subdial_hub (only in `three_subdials_chrono`).
  - `case`↔`balance_wheel` on balance_pivot × balance_hub (only in `open_heart_aperture`).
