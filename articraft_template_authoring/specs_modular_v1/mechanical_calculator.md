# mechanical_calculator — modular spec (v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `mechanical_calculator` |
| template path | `agent/templates/mechanical_calculator.py` |
| test path (optional) | `tests/agent/test_mechanical_calculator_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 3 (origin_design anchors) |
| read_count | 3 |
| read_scope | all origin_design 5★ anchors listed in the P2 source map (variants are structural forks of these three) |
| source_index_policy | only adopted module sources are indexed below |

Sources (workbench-only, category returns 0 via `--category-slug`; enumerated from source map):

- **S1** — `rec_picturex_0611__mechanical_calculator__001__png_3c15e16013b5410bb59e4a17fa83e3fb`
  (`revisions/rev_000001/model.py`, ~L37-L509). Cast tapered wedge housing, 9x9 key matrix (81 keys),
  6 function keys, 4 setting sliders, 9 counter wheels behind a covered display bank, 8 carry wheels,
  paper roll, side crank on trunnion bearing. `mesh_from_geometry(_calculator_housing_mesh(), ...)` +
  many `Box` visuals.
- **S2** — `rec_picturex_0611__mechanical_calculator__002__png_bfb3ab073a6b4a5a8e31a0dc5139ecbe`
  (`revisions/rev_000001/model.py`, ~L33-L456). Olive-enameled cadquery shell (`_housing_shell` extruded
  side profile), 8x10 key matrix (80 keys), 10 stepped-drum wheels on common axle, 2 sliders,
  carry rack (prismatic), 2-piece crank (`_crank_tube_mesh` splined path + `_grip_mesh` capsule) with a
  free-spinning handgrip.
- **S3** — `rec_picturex_0611__mechanical_calculator__003__png_6c29e006127e48e78c56f9b8f384a8da`
  (`revisions/rev_000001/model.py`, ~L62-L442). Black slant-wedge housing (`_wedge_box` mesh + `_add_quad`
  helper), exposed 4x5 key matrix (20 keys), 7 pinwheel drums (with 8 stepped teeth each) on individual
  shafts, 3 selector sliders, side crank + crank_grip (2-part chain).

## 核心身份

Hand-operated desktop **mechanical calculator**: a heavy cast/enameled tabletop chassis with a
downward-facing keyboard (digit key matrix + a few function/selector keys/sliders), a rear register
tower carrying numbered wheels or exposed pinwheel drums that spin about an X-axis, and a side crank
that turns about the +X shaft to drive computation. Not a general adding machine (no printer as the
core identity), not a typewriter (no type bars, no platen), not an electronic calculator (mechanical
key stems + rotating wheels + physical crank are the defining kinematic identity), not a cash
register (no drawer, no bell-crank). It must always retain: (a) a keyboard matrix (≥10 pressable keys)
with **PRISMATIC** downward joints, (b) at least one row of rotating counter/register wheels or
pinwheels with **REVOLUTE** joints on a shared X axis, and (c) exactly one crank with **REVOLUTE**
joint about the +X shaft on the operator's right-hand side.

## 槽位 + 候选模块表

### Slot A: `calculator_topology` (① skeleton + ③ Primary Form Family)

Structural / form family of the whole chassis; picks the housing mesh style AND
the register bank layout (covered display window bank vs exposed pinwheel tower).

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `wedge_cast_covered_bank` | forked_anchor | S1 | model.py:L37-L217 (housing mesh + display sill/brow + covered rear cover with mullions/windows/wheels behind them) | eligible if compatible | tapered cast wedge chassis; rear cover with 9 mullion-framed display windows; carry bed + paper roll bridge; digit wheels sit **behind** the covered display bank |
| `olive_extruded_axle_bank` | forked_anchor | S2 | model.py:L33-L237 (`_housing_shell` cadquery extrude + display upper/lower rail + wheel_axle + wheel supports + carry_rack visuals) | eligible if compatible | olive enameled shell with side profile; rail-framed display band; wheels share ONE common wheel_axle; carry_rack cross-bar overhead; form_subtype=Volumetric Envelope Form (extruded side profile) |
| `slant_wedge_exposed_pinwheel` | forked_anchor | S3 | model.py:L62-L216 (`_wedge_box` mesh + register_tower + tower_cover + carry_rack + carry_pawls + display_bezels) | eligible if compatible | black slant-wedge with an exposed register tower carrying visible display cards + individual bezels; carry_rack + carry_pawls sit on top; form_subtype=Planar Boundary Form (slant wedge) |

**form_subtype** per candidate:

- `wedge_cast_covered_bank` → `Macro Surface Construction` (tapered wedge + covered bank cover reads as "sealed cast metal calculator" family, e.g., mechanical adding machine).
- `olive_extruded_axle_bank` → `Volumetric Envelope Form` (side-profile extrusion produces a distinctive lofted envelope).
- `slant_wedge_exposed_pinwheel` → `Planar Boundary Form` (flat slant wedge with exposed mechanism reads as pinwheel calculator).

### Slot B: `drive` (② joint / mechanism)

The side-crank assembly. All candidates preserve a REVOLUTE about +X on the right side, but differ in
part-count / chain depth.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_arm_crank` | forked_anchor | S1 | model.py:L471-L509 (crank_shaft + crank_arm + crank_grip fused as ONE `crank` part; 1 REVOLUTE joint) | eligible if compatible | 1-part crank (shaft + arm + grip visuals fused); 1 REVOLUTE joint about +X |
| `folding_side_crank_with_grip` | forked_anchor | S2 | model.py:L416-L456 (crank tube spline + free-spinning `grip` as second part with its own REVOLUTE about +X) | eligible if compatible | 2-part crank (crank + grip); 2 REVOLUTE joints (crank_turn about housing +X, grip_spin about crank +X) |
| `two_part_crank_with_grip` | forked_anchor | S3 | model.py:L366-L442 (crank + crank_grip; both REVOLUTE about +X; crank_grip is a spinning handle on the crank end pin) | eligible if compatible | 2-part crank (crank + crank_grip); 2 REVOLUTE joints on parallel +X axes (housing→crank, crank→crank_grip) |

### Slot C: `key_matrix` (① multiplicity axis — key row × column count)

Multiplicity axis for the digit keyboard. Each candidate is one N-band of the digit key matrix.
`key_press_{row}_{column}` PRISMATIC joints along -Z at the tilted key deck; per-key visuals shared
by a common helper.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `keypad_small` (10-key, 4×5=20 or ~10 layout) | forked_anchor | S3 | model.py:L21-L23 (KEY_ROWS=4, KEY_COLUMNS=5, 20 keys); variant `rec_0611_..._var_key_matrix_10_key_keypad` | eligible if compatible | small (2–4 rows × 3–5 cols); each key = stem + cap + legend disc; PRISMATIC -Z on tilted deck |
| `keypad_medium` (~50-key, e.g., 5×10) | forked_anchor | S2 | model.py:L25-L26, L273-L323 (KEY_ROWS=8, KEY_COLUMNS=10 → 80 keys; keypad_medium samples in the same band via smaller rows) | eligible if compatible | medium (4–6 rows × 8–10 cols); same per-key geometry helper |
| `keypad_full` (~90-key, 9×9 or larger) | forked_anchor | S1 | model.py:L219-L265 (9×9=81 keys, key stem + cap + legend) | eligible if compatible | full keyboard (8–9 rows × 9–10 cols); same per-key geometry helper |

### Slot D: `register_form` (③ register bank sub-form, tightly coupled with Slot A but sampled independently for wheel count)

Wheel/drum count band + geometry: 5-, 7-, or 9-wheel register. `wheel_{i}` REVOLUTE about +X.

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `register_five_wheel` | forked_anchor | S3 | model.py:L23 (WHEEL_COUNT=7 → sample band of small); `rec_0611_..._var_register_form_exposed_pinwheel_bank` | eligible if compatible | 5 wheels evenly spaced along +X |
| `register_seven_wheel` | forked_anchor | S3 | model.py:L23,L291-L329 (WHEEL_COUNT=7 in S3 pinwheel bank) | eligible if compatible | 7 wheels |
| `register_nine_wheel` | forked_anchor | S1 | model.py:L149,L362-L401 (9 counter wheels in S1) / S2 has 10 wheels | eligible if compatible | 9 wheels (also legal for the 10-wheel S2 case at the upper edge) |

## 槽位图 (slot graph)

pattern: `parallel_children`

```
housing (Slot A + Slot D emit chassis visuals + rear register bank hardware)
  ├──[REVOLUTE +X ; hinge_line at right-side crank bearing]──> crank                (Slot B)
  │       └──[REVOLUTE +X ; on crank-end pin]──> crank_grip                        (Slot B, if 2-part)
  ├──[PRISMATIC -Z ; deck at DECK_TILT]──> key_{r}_{c}                              (Slot C, N children)
  ├──[REVOLUTE +X ; shared display axle]──> wheel_{i}                              (Slot D, N children)
  └──[PRISMATIC ±Y ; on side control lane]──> slider_{i}                            (2–4 children, fixed multiplicity 3)
```

- All chained joints parent to the single `housing` part (parallel children).
- Non-FIXED joints declare `MatingContract` where they meet a real visible face on
  housing (key stem → key_plate, slider stem → slider_track_i, wheel drum overlap
  with shared wheel_axle/display_backing, crank_shaft → crank_bearing).
- Crank-grip (Slot B) declares a mating contract onto crank_end_pin visual.
- Non-articulated frame details (mullions, feet, paper roll, front trim, decoration
  bands) are `housing.visual(...)` (Rule 1).

## 每槽位 Module Emits / Interfaces

### Slot A / module `wedge_cast_covered_bank`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `housing` (visuals: housing_shell mesh, front_lip, front_trim, blank_badge, display_sill, display_brow, rear_cover, display_side_a/b, window_mullion_i, display_window_i, carry_bed, carry_bridge, carry_post_a/b, paper_standard_a/b, crank_bearing, foot_i, key_plate, slider_track_i) | S1 model.py:L37-L217 |
| internal joints | none (all decoration is parent visual) | — |
| upstream interface | none (root) | — |
| downstream interface | keyboard deck face at key_plate, wheel_axle line at rear cover, crank_bearing on right side | S1 |

### Slot A / module `olive_extruded_axle_bank`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `housing` (visuals: housing_shell extruded mesh, base_skirt, keyboard_cover, key_plate, front_lip, display_lower_rail, display_upper_rail, display_side_0/1, display_backing, window_divider_i, wheel_axle, wheel_support_0/1, display_bridge_0/1, slider_track_0/1, carry_guide_0/1, crank_bearing) | S2 model.py:L33-L237 |
| internal joints | none | — |
| upstream interface | none | — |
| downstream interface | wheel_axle shared cylinder, slider_track_i faces, crank_bearing on right side | S2 |

### Slot A / module `slant_wedge_exposed_pinwheel`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `housing` (visuals: base_floor, side_cheek_0/1 mesh, front_fascia mesh, keyboard_bed, front_trim, mechanism_floor, front_shaft_rail, rear_shaft_rail, register_tower, tower_cover, display_card_i, display_bezel_i, display_glass_i, carry_support_0/1, carry_rack, carry_pawl_i, key_guide_row_i, slider_track_i_j, foot_i_j, crank_bearing) | S3 model.py:L62-L216 |
| internal joints | none | — |
| upstream interface | none | — |
| downstream interface | key_guide_row_i, slider_track_i_j, wheel_shaft line at register_tower, crank_bearing on right side | S3 |

### Slot B / module `single_arm_crank`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `crank` (crank_shaft cyl + crank_arm box + crank_grip cyl fused visuals) | S1 model.py:L471-L509 |
| internal joints | none | — |
| upstream interface | housing→crank REVOLUTE +X at crank_bearing (mating: crank_shaft ↔ crank_bearing) | S1 |
| downstream interface | none | — |

### Slot B / module `folding_side_crank_with_grip`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `crank` (spline crank_tube mesh) + `grip` (capsule handgrip mesh) | S2 model.py:L71-L98, L416-L456 |
| internal joints | crank→grip REVOLUTE +X (grip_spin) with element-scoped allow_overlap on the crank-end pin | S2 |
| upstream interface | housing→crank REVOLUTE +X at crank_bearing (mating: crank_tube ↔ crank_bearing) | S2 |
| downstream interface | crank-end pin visual (mating for grip) | S2 |

### Slot B / module `two_part_crank_with_grip`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `crank` (crank_shaft + crank_arm + grip_boss) + `crank_grip` (grip_sleeve + grip_end sphere + grip_marker box) | S3 model.py:L366-L442 |
| internal joints | crank→crank_grip REVOLUTE +X | S3 |
| upstream interface | housing→crank REVOLUTE +X at crank_bearing (mating: crank_shaft ↔ crank_bearing) | S3 |
| downstream interface | grip_boss end pin visual (mating for crank_grip) | S3 |

### Slot C / all `keypad_*` modules
| emits | 描述 | 来源 |
|---|---|---|
| parts | `key_{row}_{column}` × N_keys, each with `key_stem` + `key_cap` + `key_legend`/`legend_disc` visuals | S1/S2/S3 |
| internal joints | `key_press_{row}_{column}` PRISMATIC -Z (mating: key_stem ↔ key_plate/keyboard_bed) | S1/S2/S3 |
| upstream interface | housing key_plate/keyboard_bed face | — |
| downstream interface | — | — |

### Slot D / all `register_*_wheel` modules
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel_{i}` × N_wheels, each with drum + hub + digit patch (S1/S2) or wheel_shaft + wheel_core + 8 step_tooth_j (S3 pinwheel style) | S1/S2/S3 |
| internal joints | `wheel_{i}_spin` REVOLUTE +X (mating: drum ↔ display_backing OR shaft ↔ mechanism_floor) | S1/S2/S3 |
| upstream interface | housing wheel_axle shared cylinder OR register_tower shaft | — |
| downstream interface | — | — |

Sliders are 3 parts `slider_{i}` PRISMATIC ±Y on side control lane; not a sampling slot (fixed multiplicity 3).

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `calculator_topology` | enum | `wedge_cast_covered_bank` / `olive_extruded_axle_bank` / `slant_wedge_exposed_pinwheel` | `wedge_cast_covered_bank` | choice | procedural sampler | Slot A |
| `drive` | enum | `single_arm_crank` / `folding_side_crank_with_grip` / `two_part_crank_with_grip` | `single_arm_crank` | choice | procedural sampler | Slot B |
| `key_matrix` | enum | `keypad_small` / `keypad_medium` / `keypad_full` | `keypad_small` | choice | procedural sampler | Slot C |
| `register_form` | enum | `register_five_wheel` / `register_seven_wheel` / `register_nine_wheel` | `register_seven_wheel` | choice | procedural sampler | Slot D |
| `palette_style` | enum | `cast_brown_ivory` / `olive_enamel` / `black_ivory` / `oxide_red_brass` (≥3) | `cast_brown_ivory` | choice | procedural sampler | S1/S2/S3 material observation |
| `body_length_scale` | float | `[0.90, 1.10]` | 1.0 | independent | clamp | S1/S2/S3 housing X-extent |
| `body_depth_scale` | float | `[0.90, 1.10]` | 1.0 | independent | clamp | S1/S2/S3 housing Y-extent |
| `body_height_scale` | float | `[0.90, 1.15]` | 1.0 | independent | clamp | S1/S2/S3 housing Z-extent |
| `deck_tilt_deg` | float | `[6.0, 14.0]` | 10.0 | independent | clamp; used as key_press deck rpy | S1 DECK_PITCH ~atan2(0.10/0.36) ~15°; S2 DECK_TILT=12.5° |
| `key_row_count` | int | derived from `key_matrix` | 4 | conditional | small→[2,4]; medium→[4,6]; full→[8,9] | Slot C |
| `key_col_count` | int | derived from `key_matrix` | 5 | conditional | small→[3,5]; medium→[8,10]; full→[9,10] | Slot C |
| `wheel_count` | int | derived from `register_form` | 7 | conditional | 5 / 7 / 9 by enum | Slot D |
| (—) | constraint | — | — | inequality | `key_row_count * key_pitch_y + margin ≤ deck_y_span`; `key_col_count * key_pitch_x + margin ≤ deck_x_span` — otherwise `key_pitch` shrinks | interface |
| (—) | constraint | — | — | inequality | `wheel_count * wheel_pitch + 2*wheel_radius ≤ display_x_span` — otherwise wheel_pitch shrinks | interface |

### 7.5 编译预算 / compile budget (必填)

- **Per-seed target: ≤25 s wall-time** at nproc/12 workers with thread-caps. Rationale:
  full-keyboard variant emits ~81 PRISMATIC keys (worst case) + 9 REVOLUTE wheels + 3 PRISMATIC
  sliders + 1–2 REVOLUTE crank parts → ~95 joints, ~95 movable parts. Each key part reuses a
  single shared cadquery/box-composite; wheels reuse one shared mesh per style. No re-tessellation
  inside loops.
- Tessellation: axisymmetric small cylinders (key stems, wheel hubs, feet, crank shaft) ≤ 24 segments;
  hero housing meshes (chassis wedge, cadquery extruded shell, `_wedge_box`) ≤ 64 segments on curved
  edges. Number wheels/drums ≤ 32 segments.
- N identical keys share the same visual geometry (only origin changes). N identical wheels
  share the same `Mesh`/`Cylinder`. If a compile exceeds 25 s we first coarsen tessellation before
  editing structure.

## Multiplicity / Copy Logic

Two independent multiplicity axes:

1. `key_count` (axis under §8 ①-multiplicity)
   - count_param: `(key_row_count, key_col_count)`; `key_count = key_row_count * key_col_count`.
   - N_range: `[6, 90]` (spec §8 bands 10-key ≈ 6-20 / 50-key ≈ 21-60 / 90-key ≈ 61-90).
   - sampling domain (spec-declared bands): `small` (weight 0.4), `medium` (0.35), `full` (0.25).
   - copied object: `key_{row}_{column}` part with `key_stem` + `key_cap` + `key_legend/legend_disc` visuals.
   - naming: `key_{row}_{column}` / joint `key_press_{row}_{column}`.
   - placement: regular grid on the tilted deck; center-symmetric.
   - joint policy: PRISMATIC -Z with MotionLimits(lower=0, upper=0.005–0.007), MatingContract
     (key_stem ↔ key_plate/keyboard_bed).
   - source/gating: `key_matrix` slot; sweep budget caps 90 keys total.

2. `wheel_count` (axis under §8 ①-multiplicity)
   - count_param: `wheel_count`.
   - N_range: `[5, 9]`.
   - sampling domain: `register_five_wheel` / `register_seven_wheel` / `register_nine_wheel`.
   - copied object: `wheel_{i}` part with drum/hub/digit-patch visuals (S1/S2 style) or
     shaft/core/8-tooth visuals (S3 pinwheel style, gated by Slot A choice).
   - naming: `wheel_{i}` / joint `wheel_{i}_spin`.
   - placement: even X pitch along shared axle line.
   - joint policy: REVOLUTE +X, motion_limits (-π, π).
   - source/gating: `register_form` slot.

Fixed multiplicity: `slider_{0..2}` (3 sliders — evidence-backed by S1's 4 sliders, S2's 2 sliders,
S3's 3 sliders; a stable 3 covers all reference forms).

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 (落到唯一主字段) | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Slot B = 1-part vs 2-part crank chain (different edge count); Slot A + D swaps carry_rack (S2 present) / carry_pawl visuals; forked_anchor S1/S2/S3 |
| └ multiplicity | 同构件 ×N | 有 | `key_count` in [6, 90] with 3 bands (small/medium/full); `wheel_count` in [5, 9]. See §8. |
| ② 关节类型 | 图不变，某条边换 type / 轴 | 有 | Slot B swaps chain depth (1 REVOLUTE vs 2 REVOLUTE); all sampled types PRISMATIC/REVOLUTE observed; forked_anchor S1/S2/S3 |
| ③ 主体形态家族 / Primary Form Family | 换核心 part 的可识别几何形态原型 | 有 | Slot A 3 candidates → `Macro Surface Construction` (wedge_cast_covered_bank) / `Volumetric Envelope Form` (olive_extruded_axle_bank) / `Planar Boundary Form` (slant_wedge_exposed_pinwheel); each with `form_subtype` label; anchors S1/S2/S3 |
| ④ 表面装饰 | 原型不变，叠加表面细节 | 有 | host-conformal band/rib details: front_trim, front_lip, blank_badge (S1); base_skirt, display_rails (S2); front_trim, brass carry_rack, ivory display_card + display_bezel (S3); driven from `palette_style` + housing surface z-profile; `record_only` |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | body_{length/depth/height}_scale in [0.90,1.15]; deck_tilt_deg in [6,14]. Motion envelopes: `key_press_*` PRISMATIC axis (0,0,-1), range [0, 0.006]; `wheel_*_spin` REVOLUTE axis (1,0,0), range [-π, π] continuous-band; `slider_*_shift` PRISMATIC axis (0,±1,0), range [-0.010, 0.010]; `crank_turn` REVOLUTE axis (1,0,0), range [-π, π]; `grip_spin`/`crank_to_grip` REVOLUTE axis (1,0,0), range [-π, π]. `motion_test_plan`: run `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)`; `qc_samples`/`qc_sample_values`: default {0, lower, upper, mid} for prismatic; discrete {0, ±π/2, ±π} for continuous-like revolute wheels; targeted `ctx.pose({...})` per: (a) representative key press moves -Z, (b) one wheel rotates π and touch element circulates, (c) one slider shifts along its axis, (d) crank rotates π/2 and grip end sweeps. |
| ⑥ 涂装 | 只改材质 / 颜色 | 有 | `palette_style` ≥3: `cast_brown_ivory` (S1: painted_brown/aged_ivory/amber/nickel_steel/paper), `olive_enamel` (S2: olive_enamel/edge_highlight/keybed_shadow/key_ivory/key_teal/key_sage/wheel_cream/red_control), `black_ivory` (S3: painted_black/edge_black/green_key/red_key/ivory/brass/bronze/steel), `oxide_red_brass` (world_knowledge extrapolation over the S3 brass/bronze family). Material families cover painted metal / enamel / ivory / brass / rubber ≥ ceil(0.5×4)=2 broad families. |

## 采样与覆盖审计

总组合数 (structural axes only): 3 (Slot A) × 3 (Slot B) × 3 (Slot C) × 3 (Slot D) = **81** slot-choice tuples;
including 4 palette styles as ⑥ report-only, 4×81 = 324 seed-level distinct signatures at the design level.

Compatibility matrix / gating:

- `slant_wedge_exposed_pinwheel` (Slot A) MUST be paired with the pinwheel-style wheel geometry (Slot D
  `register_*_wheel` builders emit exposed pinwheel drums with 8 step_tooth_j visuals + wheel_shaft
  spanning the register tower). Other Slot A picks emit numbered-drum-style wheels.
- `folding_side_crank_with_grip` and `two_part_crank_with_grip` add a second part (`grip` / `crank_grip`);
  Slot A's crank_bearing must be axially deep enough to seat the additional joint's origin near the visible
  hardware; `crank_bearing` visual length is derived jointly per Slot A choice.
- `key_matrix=keypad_full` on a small `body_length_scale` may exceed the deck footprint — `resolve_config`
  applies the inequality (`key_pitch = min(nominal, (deck_span - margin) / (N - 1))`) and shrinks per-key
  pitch (never drops rows/cols after sampling) so keys always fit.
- Regression overrides: none at initial spec.
- Random sweep: seeds `0-35` initial pass; corner stage appended by pipeline. Viewer focus: seeds
  0/1/2 and one from each Slot A choice.

seed_domain_policy: `procedural_first`. `config_from_seed` samples independently for each slot with
weighted key_matrix bands (small 0.4 / medium 0.35 / full 0.25) and equal weight for other slots.

Topology target: with 81 slot-choice tuples, 1000-seed distinct target ≥ 60 (record-only).

Controlled local parameterization:
`body_length_scale`, `body_depth_scale`, `body_height_scale`, `deck_tilt_deg`, `key_pitch` (derived from
key_count + deck span), `wheel_pitch` (derived from wheel_count + display span). All clamped in
`resolve_config`; interface (key_plate face, wheel_axle line, crank_bearing) held stable so mating
contracts pass.

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | independent per-slot; key_matrix bands weighted 0.4/0.35/0.25; palette_style equal | slot_choices_for_seed matches build choices |
| compatibility matrix | pinwheel Slot A ↔ pinwheel wheel form; grip crank ↔ deep crank_bearing; deck footprint inequality shrinks key_pitch | no floating decoration, no keyboard overflow, wheel axle inside display band, crank_bearing axial gap OK |
| controlled local variation | body_*_scale ∈ [0.90, 1.10/1.15], deck_tilt_deg ∈ [6, 14]; key_pitch / wheel_pitch derived; slider positions fixed | proportions vary without breaking interfaces, clearance, joint origin, category identity |
| regression overrides | none | previously failed or reviewer-selected only |
| random sweep | seeds 0-35 initial; corner appended by pipeline; batch 0-9 for palette variety inspection | pass_rate ≥ 0.90; axis_realization confirms 3 Slot A / 3 Slot B / 3 Slot C / 3 Slot D / ≥3 palette_style; corner clean |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| calculator_topology | 3 | yes | yes | ③ Primary Form Family slot |
| drive | 3 | yes | yes | ② joint chain depth (1 vs 2 REVOLUTE) |
| key_matrix | 3 | yes | yes | ① multiplicity band (small/medium/full) |
| register_form | 3 | yes | yes | ① multiplicity band (5/7/9 wheels) |

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names for all 4 slots plus a palette_style tuple.
- `config_from_seed(seed)` uses deterministic procedural sampling for all ordinary seeds (`seed=0` is not special).
- Compatibility matrix / gating (in `resolve_config`) prevents illegal module combinations
  (pinwheel wheel form ↔ Slot A, grip depth ↔ Slot A).
- No small curated table; no regression overrides at spec time.
- Controlled local scale params are clamped in `resolve_config`; cannot break interfaces, clearance,
  joint origin, keyboard footprint, wheel span, category multiplicity.
- Cross-part scale dependencies (`key_pitch`, `wheel_pitch`, crank_bearing depth) resolved in
  `resolve_config`, not left to fail in builder.
- Critical `MatingContract`s: key_stem ↔ key_plate/keyboard_bed; slider_carriage/stem ↔ slider_track;
  wheel drum/shaft ↔ wheel_axle/mechanism_floor; crank_shaft/tube ↔ crank_bearing; grip/crank_grip
  ↔ crank end pin visual.
- Key joints have expected type/axis/range: `key_press_*` PRISMATIC (0,0,-1) [0,upper]; `wheel_*_spin`
  REVOLUTE (1,0,0) [-π,π]; `slider_*_shift` PRISMATIC (0,±1,0) [-0.010, 0.010]; `crank_turn` REVOLUTE
  (1,0,0) [-π,π]; `crank_to_grip`/`grip_spin` REVOLUTE (1,0,0) [-π,π].
- Copied objects follow naming and placement policy (`key_{r}_{c}`, `wheel_{i}`, `slider_{i}`).

## Reject cases

- Chassis with no keyboard matrix (identity failure).
- Wheel row not aligned on a single common X axis (breaks REVOLUTE axis semantics).
- Crank not on the right-side face — must sit on positive-X side.
- Key stems floating above the key_plate deck (Rule 2 mating gap).
- Decorative bands sitting at constant radius over a curved/tapered shell (Rule 4 conformity).
- Full-keyboard variant (81+ keys) overflowing the deck footprint (Rule 3 / interface violation).
- Pinwheel Slot A paired with drum-style wheel visuals (identity mismatch, cross-form illegal).
- FIXED articulation used for non-articulating trim (Rule 1).

## 与相邻类别的边界

- 不该混入：typewriter (type bars, platen roller, ribbon spool — none of these appear in
  mechanical_calculator; digit keys are not type keys).
- 不该混入：electronic calculator (no digital display, no PCB visuals; the register is a rotating
  numbered wheel bank or exposed pinwheel drums).
- 不该混入：cash register (no drawer, no bell-crank; sliders are setting sliders, not receipt keys).
- 不该混入：adding machine printer variant (paper roll is a decorative visual on S1 only; the crank
  turn drives register wheels, not a print mechanism as the identity feature).

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | authored 2026-07-12 from S1/S2/S3 origin_design anchors; 4 slots (calculator_topology / drive / key_matrix / register_form) + palette_style ≥ 3; two multiplicity axes (key_count, wheel_count). |

## 模板实现备注

- Shared helpers: `_key_visuals(key_part, palette)` shared across all key_matrix variants;
  `_wheel_visuals(wheel_part, palette, style)` branches on Slot A choice (drum vs pinwheel).
- Chassis helpers: `_build_wedge_cast_covered_bank_housing`, `_build_olive_extruded_axle_bank_housing`,
  `_build_slant_wedge_exposed_pinwheel_housing`; each emits its distinctive housing meshes and rail /
  bezel visuals + a small set of named "interface" visuals (key_plate, wheel_axle, crank_bearing) that
  MatingContracts anchor to.
- Element-scoped `allow_overlap` on: crank_shaft ↔ crank_bearing (captured pin), grip ↔ crank_end pin
  (spinning handle), wheel drum ↔ wheel_axle (S2 style), each stepped tooth ↔ wheel_core (S3 style).
- Slot A = pinwheel MUST route wheels to shafts (not shared axle); Slot A = other MUST route wheels
  to shared display axle.
- `run_mechanical_calculator_tests` calls `check_model_valid`, `fail_if_isolated_parts`,
  `fail_if_parts_overlap_in_current_pose`, `fail_if_articulation_origin_far_from_geometry(tol=0.015)`,
  `fail_if_joint_mating_has_gap`, plus `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48,
  ignore_fixed=True)` and targeted `ctx.pose(...)` checks for one key, one wheel, one slider, and the
  crank quarter-turn.
