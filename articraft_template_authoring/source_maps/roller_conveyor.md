# Roller conveyor — SourceMap

export_category: roller_conveyor

Authoritative records live under `data/records` of the `articraft_data` repo
(`<ARTI_SKILL_ROOT>/articraft_data/data/records`). The category is a
grounded beam frame carrying **N independently free-spinning rollers** on a
common transverse axis line, plus a floor-support structure under the frame.

Source pool: **12 record dirs — 2 picture origins and 10 forked variants. All 12
were read in full before any candidate was chosen.** The two origins were read
line by line. Each variant is a byte-level fork of one origin, so it was read as
a full unified diff against that parent; every changed line was reviewed and the
unchanged remainder is identical to a file already read line by line. Parentage
was established by diff size against **both** origins, not by name.

| Variant | Parent origin | Changed lines (vs 001 / vs 002) |
|---|---|---|
| `roller_count_5` | **001** | **47** / 733 |
| `roller_count_18` | **001** | **24** / 716 |
| `frame_form_expanding_straight` | **001** | **270** / 788 |
| `roller_count_12` | **002** | 716 / **10** |
| `roller_layout_staggered_rollers` | **002** | 759 / **69** |
| `roller_layout_split_rollers` | **002** | 821 / **145** |
| `height_telescoping_legs` | **002** | 801 / **167** |
| `support_scissor_base` | **002** | 799 / **205** |
| `support_folding_legs` | **002** | 833 / **265** |
| `frame_form_curved_arc` | **002** | 869 / **441** |

Frame convention for the rebuild: **`+X` is the conveying direction** (rollers
are pitched along X and the frame's long dimension is X), **`+Y` is the roller
spin axis** and the frame's width direction, **`+Z` is up and `z = 0` is the
floor** — 001's feet bottom out at exactly `z=0` (L92: foot centre `0.006`,
height `0.012`) and 002's foot pads bottom out at exactly `z=0` (L295: local
`-0.1075`, joint origin `z=0.120`, pad length `0.025`). The roller bed plane is
`ROLLER_AXIS_Z + ROLLER_RADIUS`. The one exception is `frame_form_curved_arc`,
where the conveying direction is the arc tangent and **each roller's spin axis is
the local radial direction** `(sin δ, cos δ, 0)`, not a global axis.

sync_records:
  - rec_picturex_0611__roller_conveyor__001__png_2bd58ebac63f4af6b9b728a17a7202a8
  - rec_picturex_0611__roller_conveyor__002__png_683f31d003644d4cb05f495eeafb0ce5
  - rec_0611_roller_conveyor_var_frame_form_curved_arc
  - rec_0611_roller_conveyor_var_frame_form_expanding_straight
  - rec_0611_roller_conveyor_var_height_telescoping_legs
  - rec_0611_roller_conveyor_var_roller_count_5
  - rec_0611_roller_conveyor_var_roller_count_12
  - rec_0611_roller_conveyor_var_roller_count_18
  - rec_0611_roller_conveyor_var_roller_layout_split_rollers
  - rec_0611_roller_conveyor_var_roller_layout_staggered_rollers
  - rec_0611_roller_conveyor_var_support_folding_legs
  - rec_0611_roller_conveyor_var_support_scissor_base

## Component slots and candidates

All record paths below are relative to `data/records/<record>/revisions/rev_000001/model.py`.
Diversity axis per `VISUAL_DIVERSITY_MODEL.md`: ① skeleton/topology, ② joint/mechanism,
③ form family.

### Slot A — `frame_form` (the host beam structure that carries every joint)

| Candidate | Record | Exact span | Axis | Key construction |
|---|---|---|---|---|
| `low_profile_extrusion_deck` | `…__001__png_2bd58ebac63f4af6b9b728a17a7202a8` | L44-L136 (frame), L20-L29 (constants) | ① | Desk-scale tabletop section, **all box primitives on one `frame` part**. Twin side rails per side — an upper `0.680×0.035×0.090` at `z=0.170` and a lower `0.680×0.028×0.035` at `z=0.090` (L48-L60) — two `0.030×0.510×0.055` end crossmembers (L63-L69), two `0.030×0.517×0.028` under-bed cross braces (L72-L78), four `0.070×0.020×0.209` corner plates each with a `0.100×0.058×0.012` foot (L81-L95), four `0.610×0.0016×0.004` extrusion grooves (L98-L105) and 16 recessed `r=0.0055` plate screws (L124-L136). **Rail top `0.215` sits 11 mm BELOW the roller crown `0.226`** — the conveying plane is above the rails |
| `deep_channel_rail_bed` | `…__002__png_683f31d003644d4cb05f495eeafb0ce5` | L139-L205 (frame), L18-L29 (constants) | ① | Floor-standing 2.4 m section. Each side is a real **three-piece channel**: web `2.400×0.045×0.150` at `z=0.790`, top flange `2.400×0.075×0.025` at `0.8775`, bottom flange `2.400×0.075×0.015` at `0.7075` (L139-L158), with faces exactly abutting (web top `0.865` = flange bottom `0.865`). Seven `0.055×0.840×0.060` under-bed crossmembers on an explicit non-uniform x-list `(-1.150,-0.900,-0.450,0,0.450,0.900,1.150)` (L160-L168), two `1.860×0.045×0.050` lower side braces and six trigonometric knee braces via `_add_diagonal_brace` (L80-L103, L183-L205). **Rail top `0.890` sits 36 mm ABOVE the roller crown `0.854`** — these rails are guide rails. The two origins disagree on this and the rebuild must derive it per candidate, not assume one |
| `pantograph_scissor_chords` | `…_var_frame_form_expanding_straight` | L31-L48 (derived constants), L63-L175 (frame) | ① | Fork of 001 with the box deck replaced by an **expanding pantograph**: top and bottom chord rails `0.680×0.035×0.020` at `z=0.212 / 0.030`, then `SCISSOR_BAYS=3` bays each carrying, per side, a rising and a falling `SCISSOR_BAR_LENGTH×0.005×0.028` diagonal at `∓SCISSOR_BAR_ANGLE` about Y (L87-L109). Every dimension is derived: `BAY_WIDTH = FRAME_LENGTH/3`, `SCISSOR_HEIGHT = (TOP_CHORD_Z − h/2) − (BOTTOM_CHORD_Z + h/2)`, `bar_length = √(bay² + height²)`, `angle = atan2(height, bay)` (L36-L46). `r=0.008` pivot pins at each of the 6 crossings (L111-L123). **The two diagonals of a bay genuinely intersect, and so do the pins — all on the `frame` part, so per `MECHANICAL_PRIORS.md` §1c that costs nothing.** Corner plates, grooves and plate screws are all deleted; feet become four `0.055×0.055×0.010` pads |
| `swept_curved_arc` | `…_var_frame_form_curved_arc` | L24-L46 (arc params), L51-L70 (`_arc_xy`/`_arc_path_3d`), L211-L255 (swept rails), L258-L283 (radial crossmembers) | ① + ② | Fork of 002 whose entire plan geometry moves onto a circular arc: `ARC_RADIUS=3.0`, `ARC_ANGLE=0.80 rad`, centre at `(0,−3.0)` so `δ=0` reproduces the straight parent's origin and tangent. The three channel pieces per side become **`sweep_profile_along_spline` meshes** over 48 path samples with 4-point rectangular profiles `_WEB_PROFILE / _TOP_FLANGE_PROFILE / _BOT_FLANGE_PROFILE` and `up_hint=(0,0,1)` (L211-L255), emitted through `mesh_from_geometry`. Crossmembers become boxes whose length is the true inner→outer chord and whose `yaw = −δ` aligns the box Y with the radial direction (L258-L283). **This is the only candidate that changes the joint axis**: `axis_dir = (sin δ, cos δ, 0)` per roller (L391-L398) |

### Slot B — `support_form` (how the frame reaches the floor)

| Candidate | Record | Exact span | Axis | Key construction |
|---|---|---|---|---|
| `fixed_corner_plate_feet` | `…__001__…` | L81-L95 | ① | No legs at all. Four vertical `0.070×0.020×0.209` corner plates spanning `z 0.006→0.215` with a `0.100×0.058×0.012` foot pad each. **Zero support joints** — the whole object has only the N roller joints. This is what makes N the only multiplicity in that family |
| `square_tube_legs_leveling_feet` | `…__002__…` | L36-L77 (leg), L170-L181 (placement), L278-L315 (feet) | ② | Six **open-bottom square tubes** built from four walls (`outer=0.060`, `wall=0.007`, `height=0.520`, `z 0.120→0.640`) rather than a solid box — L44-L67 — at `LEG_XS=(-0.900,0,0.900) × (±0.420)`. Each leg carries two `0.012×0.016×0.030` leveler jaws at `z=0.135` (L71-L77) whose inner faces sit at `x=±0.011`, **exactly the leveling stem's radius** — a tangent capture with no overlap. Six `leveling_foot_i` parts (stem `r=0.011 l=0.155`, pad `r=0.052 l=0.025`) on PRISMATIC joints, axis `(0,0,-1)`, origin `(x, y, 0.120)` = the leg's bottom plane, travel `0…0.030` (L299-L314) |
| `telescoping_sleeve_legs` | `…_var_height_telescoping_legs` | L36-L83 (leg), L288-L325 (foot), L28 (`FOOT_TRAVEL=0.080`) | ② | Fork of 002. Square tube → **`r=0.030` cylindrical sleeve** `z 0.120→0.640`, plus an `r=0.036 l=0.030` locking collar at `z=0.135`, a `0.070×0.070×0.008` mount plate at `z=0.644` under the crossmember, and an `0.012×0.038×0.014` lock lever standing proud on the collar OD (L48-L83). The foot's `threaded_stem` becomes an `r=0.024 l=0.280` **inner tube** and travel more than doubles, `0.030 → 0.080` |
| `folding_hinged_legs` | `…_var_support_folding_legs` | L41-L140 (leg part + joint), L236-L252 (frame hinge lugs), L358-L394 (feet) | ② + ① | Fork of 002. The leg stops being frame geometry and becomes **six separate `folding_leg_i` parts, each with its own REVOLUTE `leg_fold_i` joint** about `(0,1,0)` at `origin=(x, y, HINGE_Z=0.640)`, limits `0 → 1.30 rad` (L122-L139). The leg's local origin is on the hinge and the tube runs along −Z. Frame keeps only the fixed half: two `0.006×0.045×0.080` hinge lugs per leg at `x ± 0.024`, `z=0.605` (L236-L252). Leaf and lug **interleave in Y without touching** (lug spans `y ± 0.0225`, leg plates sit at `y = ±0.033 ± 0.0025`) — a real clevis, and the reason this record needs no overlap allowance. **The only depth-2 chain in the pool**: `foot_adjust_i` is re-parented `frame → folding_leg_i` with origin `(0,0,−LEG_HEIGHT)` (L378-L394), so the feet fold with the legs. `lower_side_brace` is deleted and the knee braces are relocated to `z 0.655→0.705` because they would otherwise foul the folded leg |
| `scissor_crossed_base` | `…_var_support_scissor_base` | L30-L33 (constants), L40-L118 (station), L211-L218 (placement), L314-L357 (feet) | ① | Fork of 002. Six legs → **three X-shaped stations in the YZ plane**. Two `0.018×arm_length×0.055` flat bars per station running foot `y=±0.500, z=0.120` to rail `y=∓0.420, z=0.640`; `arm_length = √(0.920² + 0.520²) = 1.0568`, roll `= atan2(dz, ±dy)` (L55-L79). Crossing point is derived, not authored: `t = foot_y/(foot_y+rail_y) = 0.5435`, `cross_z = 0.120 + t·0.520 = 0.4026` (L82-L84). Two `0.040×0.040×0.030` top gussets and two `0.050×0.060×0.012` foot plates per station. The feet move outboard to `y=±0.500` and the `lower_side_brace` is raised `0.340 → 0.660` to clear the arms |

### Slot C — `roller_form` (the moving member)

| Candidate | Record | Exact span | Axis | Key construction |
|---|---|---|---|---|
| `shell_axle_endcaps` | `…__001__…` | L139-L168 | ③ | Five visuals, all rotated `rpy=(π/2,0,0)` so their local Z lands on `+Y`: `r=0.026 l=0.482` shell, `r=0.006 l=0.494` through-axle, two `r=0.020 l=0.008` end caps at `y=±0.243`, and a `0.006×0.452×0.0015` polished `surface_highlight` strip at `z = ROLLER_RADIUS + 0.0004`. The strip is deliberately part-embedded (bottom at `0.02565` vs shell radius `0.026`) — intra-part, free — and exists so pose tests have a **non-axisymmetric feature to track** (L391-L417 rotates the joint π/2 and asserts the strip's centre-z drops by ≥ 0.020) |
| `steel_tube_endcaps` | `…__002__…` | L239-L260 | ③ | Four visuals: `r=0.034 l=0.684` tube, two `r=0.032 l=0.018` black end caps at `y=±0.351`, `r=0.006 l=0.765` axle. No highlight strip; the caps are nearly flush with the tube OD, giving a much heavier industrial read. **Note a live inconsistency in the source**: `ROLLER_TUBE_LENGTH = 0.720` (L23) is declared but the visual uses the literal `0.684`; the constant is only ever consumed by the split-roller fork (L213). The rebuild must pick one and derive from it |
| `split_twin_half_roller` | `…_var_roller_layout_split_rollers` | L212-L213, L256-L338 (roller), L209-L235 (frame axle + spacer) | ① + ② | Fork of 002 that **inverts the axle ownership**: the `r=0.006 l=0.765` axle moves onto the `frame` (L215-L224) together with an `r=0.016` central `split_spacer` (L225-L234), and the roller becomes a twin-half tube — two `r=0.034 l=0.345` halves at `y=±0.1875`, an `r=0.032 l=0.050` `bearing_sleeve` bridging the gap, two `r=0.033 l=0.005` split rings and the two outer end caps (L264-L324). `SPLIT_GAP=0.030`, `SPLIT_HALF_LENGTH=(ROLLER_TUBE_LENGTH − SPLIT_GAP)/2`, `half_offset = SPLIT_HALF_LENGTH/2 + SPLIT_GAP/2`. Both halves stay **one part** on one joint, so the split reads visually without adding a joint. See the `allow_overlap` section — this candidate as authored is the worst offender |

### Slot D — `roller_layout` (the station-placement rule)

| Candidate | Record | Exact span | Axis | Key construction |
|---|---|---|---|---|
| `uniform_inline` | `…__001__…` L110-L113 + L222; `…__002__…` L209 + L234 | — | ① | Both origins: stations on one line at one height, centred on `x=0`. Two algebraically identical spellings — `x_i = (i − (N−1)/2)·pitch` (001) and `first_x = −((N−1)·pitch)/2; x_i = first_x + i·pitch` (002) |
| `staggered_alternating_height` | `…_var_roller_layout_staggered_rollers` | L24-L26 (constants), L36-L38 (`_roller_axis_z`), L218-L241 (bearings), L245-L292 (rollers/joints) | ① | Fork of 002. `ROLLER_AXIS_Z` splits into `_LOW=0.810 / _HIGH=0.835` with `STAGGER_OFFSET=0.025`, and a single index-general helper `_roller_axis_z(i) = HIGH if i % 2 else LOW` feeds **both** the frame bearing inserts and the joint origins, so the fixed and moving halves can never drift apart (L224, L250, L286). Adjacent centre distance rises to `√(0.095² + 0.025²) = 0.0982` against `2r = 0.068`, so the stagger *increases* clearance. Part meta carries `stagger_level` and the author test at L457-L471 walks every even/odd index |

### Slot E — `roller_count` (multiplicity N) — see the dedicated section below

## Multiplicity: the exact index-general N rule

This is the section that decides the template. Three records sample the same
mechanism at three N: `roller_count_5` (N=5, parent 001), `roller_count_12`
(N=12, parent 002), `roller_count_18` (N=18, parent 001), against origins at
N=8 (001) and N=24 (002).

**1. Station x-position — one rule, two spellings, both centred on `x=0`.**

* 001 family, L110-L113 and L222: `x_i = (i − (N−1)/2) · ROLLER_PITCH`.
* 002 family, L209 and L234: `first_x = −((N−1)·ROLLER_PITCH)/2`, `x_i = first_x + i·pitch`.

These are the same expression. Crucially the **same `first_x` loop is used twice**
(002 L209-L230 for the frame's fixed bearings/fasteners, L232-L276 for the roller
parts and joints), so the fixed and moving halves are guaranteed co-indexed.

**2. Two frame-length strategies exist and the pool proves both are exact.**

*Mode A — fixed pitch, grow the frame* (001 family). `ROLLER_PITCH` stays `0.070`
across N=5/8/18 and `FRAME_LENGTH` moves `0.470 / 0.680 / 1.380`. Solving:

```
FRAME_LENGTH = (N − 1) · ROLLER_PITCH + 0.190
```

exact for all three (`4·0.07+0.19=0.470`, `7·0.07+0.19=0.680`, `17·0.07+0.19=1.380`).
That is a **constant 0.095 m inset from each end roller centre to the frame end.**

*Mode B — fixed frame, spread the pitch* (002 family). `roller_count_12` changes
**only** `ROLLER_COUNT 24→12` and `ROLLER_PITCH 0.095→0.190` (L19-L20), leaving
`FRAME_LENGTH = 2.400` alone. Solving:

```
ROLLER_PITCH = (FRAME_LENGTH − 0.120) / N      # 2.280/24 = 0.095, 2.280/12 = 0.190
```

exact for both. End inset is then `(FRAME_LENGTH − (N−1)·pitch)/2` = `0.1075` at
N=24 and `0.155` at N=12 — **not** constant, unlike Mode A.

The rebuild should adopt Mode A (pitch is a real physical property of a roller
bed and the frame follows), and expose `ROLLER_PITCH` as a continuous parameter
so Mode B's proportions remain reachable.

**3. Everything else on the frame that must re-derive with N.** `roller_count_5`
is the record that generalises 001's magic numbers, and it is the authority
(L30-L31, L64-L70, L74-L81, L84-L86, L102-L109):

| Feature | Generalised rule (count_5) | Check at N=8 (001) | Check at N=18 |
|---|---|---|---|
| `ROLLER_SPAN_HALF` | `(N−1)/2 · pitch` | 0.245 | 0.595 |
| `FRAME_HALF` | `FRAME_LENGTH/2` | 0.340 | 0.690 |
| end crossmember x | `±(ROLLER_SPAN_HALF + 0.070)` | ±0.315 ✓ | ±0.665 ✓ |
| corner plate / screw x | `±(FRAME_HALF − 0.015)` | ±0.325 ✓ | ±0.675 ✓ |
| rail groove length | `FRAME_LENGTH − 0.070` | 0.610 ✓ | 1.310 ✓ |
| cross brace x | `±1.5·pitch` (count_5 L74) | source uses ±0.175 = ±2.5·pitch; N=18 uses ±0.350 = ±5·pitch | — |

The brace rule is the one place the three records disagree. `±1.5·pitch` (0.105),
`±2.5·pitch` (0.175) and `±5·pitch` (0.350) are all `≈ FRAME_LENGTH/4`
(0.1175 / 0.170 / 0.345). **Use `±FRAME_LENGTH/4`** — it reproduces two of three
source values within 3 % and is the only rule that keeps the braces inboard at
every N.

**4. Naming pattern.** Parts `roller_{i}`; joints `roller_spin_{i}`; frame
visuals `bearing_{i}_{side}` and `rail_fastener_{i}_{side}` (002) or
`bearing_{i}_{side}` (001). Part meta carries `roller_index` / `reference_index`.
For the rebuild, prefix as `roller__<candidate>__{i}` per `AUTHORING.md` §6.

**5. Parentage: every roller parents to the frame, never chained.** 001 L236-L240
and 002 L261-L266 both pass `parent=frame, child=roller`, and 001's author test
L369-L383 asserts `parent_name == "frame"` for every index. There is no
roller-to-roller relation anywhere in the pool. `folding_legs` is the sole place
a depth-2 chain appears, and it is on the support slot, not the rollers.

**6. Declared range: N ∈ [4, 24], contiguous.** The bounds are set by the
mechanism, the host capacity and the budget — **not by which integers the source
pool happens to contain** (`AUTHORING.md` §3). The five source values 5, 8, 12, 18
and 24 are *evidence that the rule holds at five separate scales*; they are not the
range, and an earlier draft of this SourceMap wrongly presented them as one.

*Why a contiguous range is licensed at all (criterion 1).* The placement rule is
index-general in closed form, shown above: `x_i = (i − (N−1)/2)·pitch` in both
origins, `FRAME_LENGTH = (N−1)·pitch + 0.190` exact at three source points, and
`pitch = (FRAME_LENGTH − 0.120)/N` exact at two more. No term in either mode works
only at a sampled N, and the same station loop drives the frame's fixed bearings
and the roller joints, so nothing can drift between them as N moves.

*Lower bound 4 — geometry.* N stations give N−1 inter-roller gaps. Below N=4 there
are fewer than three gaps, so an item cannot be handed from one supporting pair to
the next without at some point resting on a single roller — that is a roller
*table*, not a roller *bed*, and the conveying function is what names the category.
N=3 also gives a Mode A frame of 0.330 m against a 0.580 m width, 43 % wider than
long. The source minimum of 5 sits inside the range, so all evidence stays
reachable; reaching 4 costs one more term of the same rule.

*Upper bound 24 — budget.* **Capacity does not bind here.** The clearance rule
`pitch ≥ 2r + 0.016` (001 L419-L427) is a per-config constraint that
`resolve_config` enforces, and under Mode A the pitch is independent so it can
always be raised; under Mode B at the widest frame it would permit N near 55. What
binds is cost, linear in N on three axes — parts `N + 1 + 4·stations`, mandatory
motion-QC poses `3N` from the CONTINUOUS roller joints, and collision solids
`69 + 8N` (up to `69 + 13N` for `split_twin_half_roller`):

| N | worst-case parts / joints | mandatory roller poses | collision solids (002 / split) |
|---|---|---|---|
| 4 | 17 / 16 | 12 | 101 / 121 |
| 12 | 25 / 24 | 36 | 165 / 225 |
| 18 | 31 / 30 | 54 | 213 / 303 |
| **24** | **37 / 36** | **72** | **261 / 381** |

The N=24 worst case (`folding_hinged_legs` at 3 stations) exceeds the fleet's
largest shipped object — 33 parts / 32 joints in
`shelving_unit_with_adjustable_shelves` — and is roughly double the fleet p90 of
19 parts. It is accepted because it is **not invented**:
`var_support_folding_legs` builds exactly that 37-part / 36-joint object at N=24
and asserts it at L408-L412. The `leg_station_count` parameter is capped at the
source's 3 for the same reason; a 4th station would take the same corner to
41 parts / 40 joints, beyond anything the pool builds.

*What stopping at 24 gives up.* The placement rule would carry much further and a
longer conveyor is a real object. Going higher needs two things this evidence
cannot supply: a leg-station rule for frames beyond 2.4 m (002 fixes three
stations regardless of N), and a pose budget that `3N` does not blow — at N=40 a
seed would carry 120 mandatory roller poses over ~590 collision solids. So 24 is a
**budget ceiling that happens to coincide with the largest attested value**, not a
ceiling set by it.

**7. What N must NOT change.** `ROLLER_RADIUS`, `ROLLER_AXIS_Z`,
`FRAME_OUTER_WIDTH`, roller length, rail cross-sections, and the leg/foot count
are all untouched by all three count forks. N is a pure multiplicity in the
`AUTHORING.md` §4 sense — `raw_domain` only.

## Mating mechanisms (sampled across records, not per candidate)

Per `MECHANICAL_PRIORS.md` §1b these were read across *all* twelve records. They
are the numbers that decide whether the assembly stands up, they differ record to
record, and none of them is visible to a mechanical extraction.

**1. The axial fit at the rail is a derived chain, not a set of magic numbers.
Both origins do it, differently, and both are exact.**

| Quantity | 001 | 002 |
|---|---|---|
| rail centre `y` | ±0.2725 (L48) | ±0.420 (L28) |
| rail thickness | 0.035 | 0.045 (web, L142) |
| **rail inner face** | **±0.255** (= `RAIL_INNER_Y`, L29) | **±0.3975** |
| roller shell/tube half-length | 0.241 (L24) | 0.342 (L240) |
| shell → rail axial clearance | **0.014 m** | **0.0555 m** |
| end cap outer face | ±0.247 (L25-L26) | ±0.360 (L248-L249) |
| cap → rail axial clearance | **0.008 m** | **0.0375 m** |
| axle half-length | 0.247 (L148) | 0.3825 (L256) |
| frame bearing element | `r 0.019 / bore 0.0085`, `l 0.008`, at `y=±0.251` (L32-L41, L114-L121) | `r 0.018`, `l 0.015`, at `y=±0.390` (L213-L221) |
| bearing spans | `y 0.247 → 0.255` | `y 0.3825 → 0.3975` |

Read the last two rows carefully — this is the whole mechanism:

* **002's bearing length is not chosen, it is solved.** `bearing_length =
  rail_inner_face − axle_half_length = 0.3975 − 0.3825 = 0.015` exactly. The
  insert is a spacer that fills the gap between the axle end face and the web,
  and its own author test is `expect_contact(roller_0, frame, contact_tol=0.0002)`
  (L384-L395) — a 0.2 mm tolerance, so this is intended as a genuine face touch.
* **001's ring is annular for a reason.** Bore `r=0.0085` against an axle
  `r=0.006` gives 2.5 mm radial clearance, and the axle end at `y=0.247` lands
  exactly on the ring's inner face; the `r=0.020` end cap's outer face also lands
  exactly on `0.247` against the ring's `r=0.019` annulus. The comment at
  L107-L108 says so explicitly. `expect_contact(contact_tol=0.0008)` at L384-L389.
* **`MECHANICAL_PRIORS.md` §4 compliance is genuine in both origins.** The spin
  axis passes through the roller centre (`origin=(x, 0, ROLLER_AXIS_Z)`,
  `axis=(0,1,0)`), the roller is bounded well inside the rails, and the frame
  provides real axial clearance rather than embedding the roller in the rail.
* **But both origins land at distance exactly 0, and the insert has two ends that
  need OPPOSITE treatment.** Per the rewritten `MECHANICAL_PRIORS.md` §1c, exact
  tangency is fragile in both directions: CadQuery `union` can keep tangent solids
  separate, triangulation can open at the seam, and connectivity is checked at
  `contact_tol=1e-6`. So:
  - the insert's **outer** end meets the rail — both are *frame* visuals, an
    intra-part weld — and gets a deliberate `fitting_weld_embed_m` INTO the rail;
  - the insert's **inner** end meets the rotating axle — a *running fit* between
    two parts — and keeps `running_clearance_m` as a real gap, with
    `ctx.allow_isolated_part(roller_i, …)` as the support escape.

  Same 8 mm feature, two interfaces, opposite signs. Getting this backwards in
  either direction is a defect: welding the axle end seizes the bearing, and
  kissing the rail can split the frame into two connectivity islands.

**2. Roller top vs rail top — the pool contains both conventions and it is a
per-candidate derivation.**

| Record | roller crown `Z_axis + r` | rail top | verdict |
|---|---|---|---|
| 001 | 0.200 + 0.026 = **0.226** | upper side rail top `0.215` | conveying plane **11 mm above** the rails |
| `expanding_straight` | 0.226 (unchanged) | top chord top `0.222` | **4 mm above** — same convention, tighter |
| 002 | 0.820 + 0.034 = **0.854** | top flange top `0.890` | rails **36 mm above** the crown — guide rails |
| `staggered` | 0.844 / 0.869 alternating | 0.890 | still below the flange at both levels |

A template that hard-codes either one will bury half its seeds' rollers in the
rails or leave them unguided. Derive `rail_top` from the frame candidate and
place the bed relative to it.

**3. Roller-to-roller pitch clearance is an asserted invariant.** 001 L419-L427
runs `expect_gap(roller[i+1], roller[i], axis="x", min_gap=0.016, max_gap=0.020)`
for every adjacent pair — `0.070 − 2·0.026 = 0.018`. 002's equivalent margin is
`0.095 − 0.068 = 0.027`. **`pitch ≥ 2·roller_radius + 0.016` is the hard N/pitch
constraint** and directly sets the upper N bound in Mode B.

**4. Leg-to-frame and leg-to-floor planes are all abutments, never overlaps
(002).** Leg tube spans `z 0.120 → 0.640` (L39-L41); the crossmember spans
`0.640 → 0.700` (L165): leg top = crossmember bottom, face to face. The foot
joint origin is `(x, y, 0.120)` — *exactly* the leg's bottom plane (L304). The
`0.052` foot pad bottoms out at `z = 0.120 − 0.1075 − 0.0125 = 0.000`. Every
plane in that chain is derived from `leg_bottom_z`.

**5. Leveling-stem insertion overlap, at both stroke ends.**

* 002: stem `r=0.011 l=0.155` at local `z=−0.0175` → world `0.025 … 0.180`.
  Insertion past the leg bottom `0.120` is **0.060 m at q=0** and **0.030 m at
  q=FOOT_TRAVEL=0.030**; the test asserts `min_overlap=0.025` *inside*
  `ctx.pose({joint: FOOT_TRAVEL})` (L460-L467), i.e. it checks the worst case.
* The stem never intersects the leg walls: the leveler jaws at `x = ±0.017` with
  half-width `0.006` put their inner faces at `x = ±0.011` = **exactly the stem
  radius** (L71-L77). This is the tangent-capture idiom, and it is why 002 needs
  no overlap allowance anywhere.
* `telescoping_legs`: inner tube `r=0.024 l=0.280` at local `+0.050` → world
  `0.030 … 0.310`; sleeve `0.120 … 0.640`. Insertion overlap is **0.190 m at
  min stroke and 0.110 m at max stroke (`FOOT_TRAVEL=0.080`)**, so the running
  fit is generous. The radial fit is `sleeve r 0.030` vs `tube r 0.024` = **6 mm**
  — but the sleeve is authored as a *solid* cylinder, so that 6 mm is not
  clearance, it is interpenetration. See the `allow_overlap` section.

**6. Scissor and folding pivot geometry.**

* `scissor_base` (L44-L118): stance `y=±0.500`, rail attach `y=±0.420` — the feet
  are **80 mm outboard of the rails**, which is why the frame AABB Y band in its
  author test widens `0.90…0.93 → 0.95…1.15` (L413-L419). Arms `1.0568 m` long,
  crossing at `t=0.5435` of the arm, `cross_z = 0.4026`. **Construction defect to
  fix in the rebuild:** the arms lie in the YZ plane (Box X-extent `0.018`), so
  the pivot bolt through them must run along **X**, but L85-L90 authors it with
  `rpy=(0,0,0)`, i.e. a Z-axis cylinder, and the two bolt flanges at
  `x = ±0.021` (L91-L98) are likewise Z-axis. Per `MECHANICAL_PRIORS.md` §4 the
  pin must be coaxial with the pivot; rebuild with `rpy=(0, π/2, 0)`.
* `folding_legs` (L67-L85, L236-L252): hinge axis at `z=HINGE_Z=0.640` =
  the leg-top / crossmember-bottom plane inherited from 002. Frame lugs
  `0.006 × 0.045 × 0.080` at `x = ±0.024` (so a 42 mm inner clear span for a
  60 mm tube — the lugs straddle it); leaf plates `0.070 × 0.005 × 0.060` at
  `y = ±0.033`, i.e. **outboard of the 22.5 mm lug half-width** — they interleave
  in Y and never touch. **Second defect:** the leaf's `pivot_bolt` is at local
  `z=−0.008`, so it sits 8 mm below the declared hinge axis at
  `origin.z = 0.640`. Put the pin on the axis.

**7. Curved-arc mating is where the straight derivations break, and the record
shows exactly how.** Two numbers had to change (L333-L355 vs 002 L213-L230):
bearing length `0.015 → 0.025` and rail fastener length `0.004 → 0.050`
("embedded deeply into web for connection"), plus the bearing moved from radial
offset `0.420` to `0.390`. The straight parent's face-tangency does not survive a
swept rail, and the record's answer was to inflate the parts and add 48
`allow_overlap` calls. The record also had to relax `expect_contact(tol=0.0002)`
into `expect_overlap(axes="xy", min_overlap=0.02)` and `expect_within` margin
`0.0 → 0.05` (L541-L566). **The correct rebuild is to re-evaluate the same
derivation chain in the local radial frame at each `δ`** — `bearing_length =
rail_inner_radial_offset − axle_half_length`, measured along `(sin δ, cos δ, 0)`
— which reproduces the straight parent's exactness on the arc.

**8. Connection overlaps vs running clearances — which is which.**

`MECHANICAL_PRIORS.md` §1c makes exact tangency a defect rather than a target, so
every zero-distance meeting in the pool has to be classified. The split is not
subtle once stated: **anything that never moves gets a deliberate overlap; anything
that moves keeps a real gap.**

| Site | Source value | Kind | Rebuild |
|---|---|---|---|
| rail web top ↔ top flange bottom (002 L142-L149) | both `0.865`, tangent | intra-part weld | `+structural_weld_embed_m` |
| leg top ↔ crossmember bottom (002 L39-L41 vs L165) | both `0.640`, tangent | intra-part weld | `+structural_weld_embed_m` |
| bearing insert outer face ↔ rail inner face (002 L213-L221) | both `0.3975`, tangent | intra-part weld | `+fitting_weld_embed_m` |
| rail fastener ↔ web outer face (002 L222-L230) | both `0.4425`, tangent | intra-part weld | `+fitting_weld_embed_m` |
| foot pad ↔ bottom chord (expanding L146-L150) | **already embedded** | intra-part weld | keep; source attests the idiom |
| rail fastener ↔ web (curved L347) | **already embedded** (`l=0.050`) | intra-part weld | keep, but sized not "deep" |
| bearing insert inner face ↔ axle end (001 L36/L148, 002 L213/L256) | tangent at `0.247` / `0.3825` | **running fit** | `−running_clearance_m`, `allow_isolated_part` |
| frame ring ↔ roller end cap (001 L114-L121 vs L153-L159) | both faces at `0.247` | **running fit** | `−running_clearance_m` |
| roller barrel ↔ rail inner face | 0.014 / 0.0555 clear | **running fit** | unchanged |
| adjacent rollers | `pitch − 2r ≥ 0.016` | **running fit** | unchanged |
| leveler jaw ↔ threaded stem (002 L71-L77) | tangent at `±0.011` | **running fit** (prismatic) | small clearance, `allow_isolated_part` |
| telescoping sleeve bore ↔ inner tube | source overlaps solid-in-solid | **running fit** | real bore, `sleeve_bore_clearance_m` |

The idiom is **source-attested, not invented**: two records already embed
deliberately and say why —
`var_frame_form_expanding_straight` L146-L148 ("Foot top face embeds slightly into
the bottom chord to ensure geometric connectivity") and
`var_frame_form_curved_arc` L347 ("embedded deeply into web for connection").

**Sizing.** `structural_weld_embed_m` = `clamp(frame_length_m × 0.00025, 0.3, 1.0) mm`
→ 0.3 mm on the 0.470 m desk section, 0.6 mm on the 2.400 m floor unit.
`fitting_weld_embed_m` = `max(0.2 mm, 0.6 × structural)`, smaller because 001's
whole bearing ring is only 8 mm long (L36) and 0.5 mm would be 6 % of it.

**Why this cannot trip the overlap gate.** Every site in the "weld" rows above is
*intra-part* — a frame visual meeting another frame visual — and
`fail_if_parts_overlap_*` compares **parts**, so it never looks at them. Even if a
weld were inter-part, `find_geometry_overlaps` (`sdk/_core/v0/geometry_qc.py:L3246`,
implementation `L1820`) only calls `fcl.collide` once the AABB intersection depth
exceeds `overlap_tol` on **all three axes**; the contact normal is always the
shallow axis for a face weld, so a sub-millimetre embed is filtered out first.
Note the strict default is `overlap_tol=1e-3` (1 mm) — fleet templates commonly
pass 4–6 mm, but the sizing above clears the 1 mm default, not just the loose one.

**This category has no rigid inter-part connection at all.** The frame is the only
root; rollers, leveling feet and folding legs are each carried by a joint. So every
cross-part meeting is a running fit, and `allow_isolated_part` — still permitted,
still not blocked by preflight — is the support escape throughout.

**9. Scale and effort.** Two scales exist and nothing in between: 001 is a
0.68 × 0.58 × 0.22 m desk section (bed height 0.200 m); 002 is a
2.40 × 0.915 × 0.78 m floor unit (bed height 0.820 m). Roller effort is `2.0` and
velocity `18–20` in both — a free gravity roller, effort does **not** scale with
size here. Foot prismatic joints run `effort=250.0, velocity=0.015,
damping=8.0, friction=4.0`; the folding hinge runs `effort=15.0, velocity=1.5`.
Roller joints carry `MotionProperties(damping=0.01, friction=0.015)` in the 002
family only.

## `allow_overlap` sites — preflight BLOCKS these for Design-backed templates

Four of the twelve records call `ctx.allow_overlap`. Neither origin does, and
neither do `roller_count_5/12/18`, `staggered_rollers`, `folding_legs` or
`expanding_straight`. Every site below must be re-expressed.
`ctx.allow_isolated_part(...)` remains permitted and is the sanctioned escape for
a member carried by its joint on a running clearance.

| Record | Exact span | Count | What overlaps | How to express it instead |
|---|---|---|---|---|
| `…_var_roller_layout_split_rollers` | L487-L493 | **N = 24 unscoped part-pair allowances** | The frame-mounted `axle_{i}` (`r=0.006`) and `split_spacer_{i}` (`r=0.016`) sit bodily inside the roller's solid tube halves and `bearing_sleeve`. The allowance is **not element-scoped** — it blankets the entire `frame × roller_i` pair, so it would also mask any genuine rail collision | Either (a) return the axle to the roller part, as both origins do — the split is purely visual and costs nothing on one part per §1c — or (b) keep the frame axle and make the roller's central member a **hollow annular sleeve** with bore > 0.006, exactly the construction 001 already uses for `_bearing_ring_mesh` (L32-L41). Fold `split_spacer` into the frame axle visual. Then declare `ctx.allow_isolated_part(roller_i, …)` |
| `…_var_frame_form_curved_arc` | L530-L540 | **2N = 48**, element-scoped (`bearing_{i}_{s}` × `axle`) | The bearing insert was lengthened `0.015 → 0.025` so it swallows the axle end | Re-derive `bearing_length` in the local radial frame (mechanism note 7). The straight parent achieves face contact at `0.015` with no allowance; hold a 0.2–0.5 mm positive gap and use `allow_isolated_part` on the roller |
| `…_var_height_telescoping_legs` | L498-L507 (sleeve × tube), L510-L519 (collar × tube) | **12**, element-scoped | Solid `r=0.030` sleeve vs solid `r=0.024` inner tube; solid `r=0.036` collar vs the same tube | Make sleeve and collar **real tubes** — annular CadQuery/lathe solids with bore ≥ 0.0245 — turning the 6 mm interference into a 0.5 mm running clearance. The foot is then carried by its prismatic joint: `ctx.allow_isolated_part(leveling_foot_i, …)`. This is also better source fidelity: 002's *square* leg is already authored hollow from four walls (L44-L67) precisely so the stem is not buried |
| `…_var_support_scissor_base` | L505-L525 | **12**, element-scoped (arm × stem, foot plate × stem) | The `r=0.011` threaded stem passes through the `0.018`-thick scissor arm and the `0.012`-thick foot plate | Copy the parent's own solution: 002's leveler jaws stop at exactly the stem radius (L71-L77). Give the foot plate a real bore, or split it into two tangent jaws, or merge the foot plate into the `leveling_foot_i` part (intra-part, free) |

## Visual and collision counts

`sdk/_core/v0/exact_collisions.py:L94-L118` derives **one collision solid per
visual, 1:1** for `Box`/`Cylinder`/`Sphere`, and one per mesh. With N up to 24
this is the dominant cost driver, so the per-seed budget must be planned, not
discovered.

| Construction | Frame visuals | Per roller | Other | Total at source N | As a function of N |
|---|---|---|---|---|---|
| 001 `low_profile_extrusion_deck` + `shell_axle_endcaps` | `26 + 2N` | 5 | 0 | **84** (N=8), 9 parts | `26 + 7N` |
| `roller_count_18` (same) | `26 + 2N` | 5 | 0 | **154** (N=18), 19 parts | `26 + 7N` |
| `expanding_straight` | `16 + 2N` | 5 | 0 | **88** (N=8), 9 parts | `16 + 7N` |
| 002 `deep_channel_rail_bed` + `steel_tube_endcaps` | `57 + 4N` | 4 | 12 (6 feet × 2) | **261** (N=24), 31 parts | `69 + 8N` |
| `split_rollers` | `57 + 6N` | 7 | 12 | **381** (N=24), 31 parts | `69 + 13N` |
| `folding_legs` | `33 + 4N` | 4 | 6 legs × 8 + 12 | **249** (N=24), 37 parts | `93 + 8N` |
| `curved_arc` | `8 meshes + 49 + 4N` | 4 | 12 | **265** (N=24), 31 parts | `69 + 8N`, 8 of them swept meshes |

Two consequences for the rebuild:

* **The 002 family's `rail_fastener_{i}_{side}` adds 2N collision solids for a
  4 mm decorative screw head** (L222-L230). 001 has no per-station fastener at
  all. Drop it, or weld it into the web — it is the cheapest 48-solid saving in
  the category and changes nothing visible.
* `split_rollers` at N=24 is 381 collision solids from 31 parts. That is the
  candidate most likely to hit the 12-second per-build budget in preflight; it is
  also the one whose overlap fix (single hollow sleeve rather than sleeve + two
  split rings + spacer) reduces the count.

## Folded into continuous parameters rather than separate candidates

Per `VISUAL_DIVERSITY_MODEL.md` a pure proportion change is not a candidate. The
following vary across the pool without changing part tree, joint set or interface,
so they become independent continuous parameters with the source range as the domain:

| Parameter | Source range | Evidence |
|---|---|---|
| `roller_radius` (m) | 0.026 – 0.034 | 001 L22 / 002 L21 |
| `bed_height` = `ROLLER_AXIS_Z` (m) | 0.200 – 0.820 | 001 L23 / 002 L22 |
| `frame_outer_width` (m) | 0.580 – 0.915 | 001 L28 / 002 L27 |
| `roller_length` (m) | 0.482 – 0.684 | 001 L24 / 002 L240 |
| `roller_pitch` (m) | 0.070 – 0.190 | 001 L21 / `roller_count_12` L20 |
| `foot_travel` (m) | 0.030 – 0.080 | 002 L28 / `telescoping` L28 |
| `stagger_offset` (m) | 0 – 0.025 | `staggered` L24-L26 (0 recovers `uniform_inline`, but the layout stays a candidate because it changes the *rule*, not just a length) |
| `arc_radius` (m) / `arc_angle` (rad) | 3.0 / 0.80 | `curved_arc` L24-L25 — only meaningful under `swept_curved_arc` |
| `scissor_bays` (count) | 3 | `expanding_straight` L40 — declared but sampled once; treat as a bounded integer parameter of that candidate, not a second N |

`FRAME_LENGTH` is **not** an independent parameter: it is derived from N and
pitch (Mode A above).

## Joint type: the source uses REVOLUTE, and the rebuild should not

Every roller joint in all twelve records is `ArticulationType.REVOLUTE` with
symmetric limits — 001 L243-L248 uses `±2π`, the whole 002 family L268-L273 uses
`±π`. A free gravity roller has no travel limit, and `AUTHORING.md` §5 gives
CONTINUOUS joints better motion coverage (neutral plus −90°, +90°, 180° are
mandatory poses). **Recommendation: build the roller joints as CONTINUOUS about
the transverse axis**, and state it as a deliberate deviation. Note the two
consequences: (a) 001's author test at L369-L383 asserts
`limits.lower < 0 < limits.upper`, which a CONTINUOUS joint will not satisfy —
the equivalent rebuild test must assert the axis and parentage instead; (b)
CONTINUOUS adds 3 required poses × N joints to motion QC, which combines badly
with N=24 and the collision counts above, so plan the per-seed budget around it.

The foot PRISMATIC joints and the folding-leg REVOLUTE joints keep their source
types and limits.

## Category anchors (machine-checkable)

1. **Exactly one root part, named for the frame.** 002's own test asserts
   `len(root_parts()) == 1 and root_parts()[0].name == "frame"` (L327-L337). Every
   other part is a descendant.
2. **N roller parts, N ∈ [4, 24], each with its own joint whose parent is the
   frame.** No roller is ever the parent of another roller. Asserted per index in
   both origins (001 L369-L383, 002 L419-L435).
3. **Every roller joint spins about the transverse axis through the roller
   centre.** Straight frames: `axis=(0,1,0)` and `origin=(x_i, 0, bed_z)`. The
   curved frame: `axis=(sin δ_i, cos δ_i, 0)` and `origin` on the arc centreline.
   The axis is never `(1,0,0)` (the conveying direction) and never vertical.
4. **Roller stations are monotonic and evenly pitched along the conveying
   direction.** 001 L332-L345 asserts `|x_{i+1} − x_i − pitch| ≤ 1e-7` for every
   adjacent pair.
5. **Adjacent rollers never touch:** `gap = pitch − 2·roller_radius ≥ 0.016 m`
   (001 L419-L427).
6. **Every roller is contained within the frame in plan and contacts it at the
   rails.** `expect_within(roller, frame, axes="xy")` for the first and last
   roller, plus a bearing contact/clearance at both ends (002 L384-L409).
7. **The object is grounded at `z = 0`** through the support slot — corner-plate
   feet (001), foot pads at min stroke (002 and its forks), or chord pads
   (`expanding_straight`, which as authored bottoms out at `z=0.015` and must be
   corrected in the rebuild).
8. **Support joints, when present, are: PRISMATIC about `(0,0,−1)` for leveling
   feet, and REVOLUTE about `(0,1,0)` for folding legs.** There is no other joint
   type or axis anywhere in the pool.
9. **No `allow_overlap` in any emitted seed.** Both origins already satisfy this;
   the four variants that do not are documented above with their fixes.

## Review ledger

Every one of the twelve records was opened and read in full — origins line by
line, variants as complete unified diffs against their established parent —
before deciding what it contributes.

| Record | Depth | Verdict |
|---|---|---|
| `…__001__png_2bd58ebac63f4af6b9b728a17a7202a8` | full | **Candidate**: `low_profile_extrusion_deck`, `fixed_corner_plate_feet`, `shell_axle_endcaps`, `uniform_inline`. Also supplies the annular bearing ring, the pose-trackable highlight strip, and the `pitch − 2r ≥ 0.016` invariant |
| `…__002__png_683f31d003644d4cb05f495eeafb0ce5` | full | **Candidate**: `deep_channel_rail_bed`, `square_tube_legs_leveling_feet`, `steel_tube_endcaps`. Supplies the solved `bearing_length = rail_inner − axle_half` derivation, the tangent leveler-jaw capture, and the rails-above-crown convention |
| `…_var_roller_count_5` | full diff (47 lines) | **Multiplicity authority**: the only record that generalises 001's frame magic numbers into `ROLLER_SPAN_HALF` / `FRAME_HALF` rules. Also marks the practical lower N bound by widening its own proportion band |
| `…_var_roller_count_18` | full diff (24 lines) | **Multiplicity**: third data point that pins `FRAME_LENGTH = (N−1)·pitch + 0.190` exactly. Keeps 001's hard-coded style, so it confirms the rule rather than stating it |
| `…_var_roller_count_12` | full diff (10 lines) | **Multiplicity**: the smallest diff in the pool and the most informative — changing only N and pitch proves Mode B (`pitch = (FRAME_LENGTH − 0.120)/N`) is exact and that N is independent of every other dimension |
| `…_var_roller_layout_staggered_rollers` | full diff (69 lines) | **Candidate** `staggered_alternating_height`. Its `_roller_axis_z(i)` helper feeding both the frame bearings and the joint origins is the pattern the rebuild should copy for any per-index geometry |
| `…_var_roller_layout_split_rollers` | full diff (145 lines) | **Candidate** `split_twin_half_roller`, and the pool's worst mechanical offender: 24 unscoped `allow_overlap` calls plus the heaviest collision count (381 at N=24). Cited with a mandatory reconstruction |
| `…_var_height_telescoping_legs` | full diff (167 lines) | **Candidate** `telescoping_sleeve_legs`. Supplies the min/max stroke insertion numbers (0.190 / 0.110 m) and the `FOOT_TRAVEL` upper bound. 12 `allow_overlap` calls caused by solid-in-solid sleeves |
| `…_var_support_scissor_base` | full diff (205 lines) | **Candidate** `scissor_crossed_base`. Supplies the derived crossing point `t = foot_y/(foot_y+rail_y)` and the outboard-stance frame-width consequence. Two defects recorded: Z-axis pivot bolt/flanges, and 12 `allow_overlap` calls the parent's jaw idiom already solves |
| `…_var_support_folding_legs` | full diff (265 lines) | **Candidate** `folding_hinged_legs`. The only record with a depth-2 chain and the only clevis in the pool; needs **no** overlap allowance, which is the proof that interleaving beats embedding. One defect: pivot bolt 8 mm off the declared hinge axis |
| `…_var_frame_form_expanding_straight` | full diff (270 lines) | **Candidate** `pantograph_scissor_chords`. Best example in the pool of fully-derived geometry (`BAY_WIDTH`, `SCISSOR_BAR_LENGTH`, `SCISSOR_BAR_ANGLE`) and of §1c intra-part crossing being free. One defect: feet bottom out at `z=0.015`, not `0` |
| `…_var_frame_form_curved_arc` | full diff (441 lines) | **Candidate** `swept_curved_arc`. The only record that changes the joint axis, the only one using `sweep_profile_along_spline`, and the clearest demonstration that a straight-frame mating derivation must be re-evaluated in the local frame rather than patched with allowances |

**What reading the non-candidate-bearing records changed.** Three
assembly-blocking findings came only from records that were read for their N or
layout content: the exact `FRAME_LENGTH`/`pitch` rules (from the three count
forks, none of which is a form candidate), the fact that `ROLLER_TUBE_LENGTH`
in 002 is dead and contradicts the tube's own literal length (visible only by
following it into `split_rollers` L213), and the confirmation that the tangent
leveler-jaw capture in 002 already solves the exact overlap that
`scissor_base` and `telescoping_legs` resorted to allowances for. Choosing what
to read from the candidate list alone would have missed all three.

**One caution the pool cannot answer.** The source author tests are lighter than
the template checks — 001 never checks part-pair overlap at all, and both origins
assert contact at *exactly zero distance*, which `fcl.collide` treats as a
collision. A construction being source-attested does not mean it survives
`fail_if_parts_overlap_in_sampled_poses`.

## Accepted candidate manifest (machine-readable)

One row per candidate across all slots. Every span here is a span already cited
and verified in the sections above.

| slot | candidate | diversity axis | source type | record/revision | exact model.py:Lx-Ly | key parts/joints/helpers | status |
|---|---|---|---|---|---|---|---|
| frame_form | low_profile_extrusion_deck | ① skeleton/topology | host beam frame | rec_picturex_0611__roller_conveyor__001__png_2bd58ebac63f4af6b9b728a17a7202a8/rev_000001 | model.py:L20-L29, model.py:L44-L136 | part `frame`; `_add_frame_visuals`; twin side rails, end crossmembers, cross braces, corner plates + feet, extrusion grooves, `_bearing_ring_mesh` annular bearings | accepted |
| frame_form | deep_channel_rail_bed | ① skeleton/topology | host beam frame | rec_picturex_0611__roller_conveyor__002__png_683f31d003644d4cb05f495eeafb0ce5/rev_000001 | model.py:L18-L29, model.py:L139-L205 | part `frame`; three-piece channel per side (web + top/bottom flange), 7 crossmembers, lower side braces, `_add_diagonal_brace` knee braces | accepted |
| frame_form | pantograph_scissor_chords | ① skeleton/topology | host beam frame | rec_0611_roller_conveyor_var_frame_form_expanding_straight/rev_000001 | model.py:L31-L48, model.py:L63-L175 | part `frame`; derived `BAY_WIDTH`/`SCISSOR_BAR_LENGTH`/`SCISSOR_BAR_ANGLE`; `scissor_rise_*`/`scissor_fall_*` diagonals, `pivot_pin_*`, chord rails, pad feet | accepted |
| frame_form | swept_curved_arc | ① skeleton/topology + ② joint axis | host beam frame | rec_0611_roller_conveyor_var_frame_form_curved_arc/rev_000001 | model.py:L24-L46, model.py:L51-L70, model.py:L211-L255, model.py:L258-L283 | part `frame`; `_arc_xy`, `_arc_path_3d`, `sweep_profile_along_spline` + `mesh_from_geometry` rails, radial crossmembers with `yaw = -delta`; per-roller radial joint axis | accepted |
| support_form | fixed_corner_plate_feet | ① skeleton/topology | floor support | rec_picturex_0611__roller_conveyor__001__png_2bd58ebac63f4af6b9b728a17a7202a8/rev_000001 | model.py:L81-L95 | `corner_plate_*` + `foot_*` visuals on `frame`; zero support joints; grounded at z=0 | accepted |
| support_form | square_tube_legs_leveling_feet | ② joint/mechanism | floor support | rec_picturex_0611__roller_conveyor__002__png_683f31d003644d4cb05f495eeafb0ce5/rev_000001 | model.py:L36-L77, model.py:L170-L181, model.py:L278-L315 | `_add_square_tube_leg` four-wall hollow tube + tangent `leveler_jaw_*`; parts `leveling_foot_i`; PRISMATIC `foot_adjust_i` axis (0,0,-1), travel 0-0.030 | accepted |
| support_form | telescoping_sleeve_legs | ② joint/mechanism | floor support | rec_0611_roller_conveyor_var_height_telescoping_legs/rev_000001 | model.py:L36-L83, model.py:L288-L325 | `_add_telescoping_leg` outer sleeve + locking collar + mount plate + lock lever; foot `inner_tube`; PRISMATIC travel 0-0.080 | accepted |
| support_form | folding_hinged_legs | ② joint/mechanism | floor support | rec_0611_roller_conveyor_var_support_folding_legs/rev_000001 | model.py:L41-L140, model.py:L236-L252, model.py:L358-L394 | parts `folding_leg_i`; REVOLUTE `leg_fold_i` axis (0,1,0) at HINGE_Z, limits 0-1.30; frame `hinge_lug_*` clevis; `foot_adjust_i` re-parented to the leg | accepted |
| support_form | scissor_crossed_base | ① skeleton/topology | floor support | rec_0611_roller_conveyor_var_support_scissor_base/rev_000001 | model.py:L40-L118, model.py:L211-L218, model.py:L314-L357 | `_add_scissor_base_leg` crossed arms with derived `t_cross`/`cross_z`, pivot bolt + flanges, top gussets, foot plates; feet outboard at y=±0.500 | accepted |
| roller_form | shell_axle_endcaps | ③ form family | rotating member | rec_picturex_0611__roller_conveyor__001__png_2bd58ebac63f4af6b9b728a17a7202a8/rev_000001 | model.py:L139-L168 | `_add_roller_visuals`; `roller_shell`, through `axle`, two `end_cap_*`, pose-trackable `surface_highlight` strip | accepted |
| roller_form | steel_tube_endcaps | ③ form family | rotating member | rec_picturex_0611__roller_conveyor__002__png_683f31d003644d4cb05f495eeafb0ce5/rev_000001 | model.py:L239-L260 | `tube`, two flush `end_cap_*`, `axle` sized so its end face abuts the frame bearing insert | accepted |
| roller_form | split_twin_half_roller | ① skeleton/topology + ② joint/mechanism | rotating member | rec_0611_roller_conveyor_var_roller_layout_split_rollers/rev_000001 | model.py:L212-L213, model.py:L215-L235, model.py:L264-L324 | frame-owned `axle_i` + `split_spacer_i`; roller `tube_left`/`tube_right`/`bearing_sleeve`/`split_ring_*`; one part, one joint; needs the allow_overlap reconstruction | accepted |
| roller_layout | uniform_inline | ① skeleton/topology | station placement rule | rec_picturex_0611__roller_conveyor__001__png_2bd58ebac63f4af6b9b728a17a7202a8/rev_000001 | model.py:L110-L113, model.py:L221-L253 | `roller_xs` centred on x=0; parts `roller_i`, joints `roller_spin_i` all parented to `frame` | accepted |
| roller_layout | staggered_alternating_height | ① skeleton/topology | station placement rule | rec_0611_roller_conveyor_var_roller_layout_staggered_rollers/rev_000001 | model.py:L24-L26, model.py:L36-L38, model.py:L218-L241, model.py:L245-L292 | `_roller_axis_z(i)` feeding both frame bearing inserts and joint origins; ROLLER_AXIS_Z_LOW/HIGH, STAGGER_OFFSET 0.025 | accepted |
| roller_count | index_general_station_rule | ① skeleton/topology | multiplicity N | rec_0611_roller_conveyor_var_roller_count_5/rev_000001 | model.py:L30-L31, model.py:L64-L72, model.py:L74-L82, model.py:L84-L86, model.py:L102-L109 | `ROLLER_SPAN_HALF`/`FRAME_HALF`; end crossmember at span_half+0.070, corner plate at FRAME_HALF-0.015, groove FRAME_LENGTH-0.070; N range [5,24] | accepted |
| roller_count | fixed_pitch_grow_frame_N18 | ① skeleton/topology | multiplicity N | rec_0611_roller_conveyor_var_roller_count_18/rev_000001 | model.py:L20-L27, model.py:L60-L66 | third data point pinning FRAME_LENGTH = (N-1)*pitch + 0.190 exactly | accepted |
| roller_count | fixed_frame_spread_pitch_N12 | ① skeleton/topology | multiplicity N | rec_0611_roller_conveyor_var_roller_count_12/rev_000001 | model.py:L19-L20, model.py:L209-L211 | Mode B: pitch = (FRAME_LENGTH - 0.120)/N, exact at N=24 and N=12; proves N is independent of every other dimension | accepted |
