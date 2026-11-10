# Protractor with swing arm — SourceMap

export_category: protractor_with_swing_arm

Authoritative records live under `data/records` of the `articraft_data` repo
(`<ARTI_SKILL_ROOT>/articraft_data/data/records`). The category is a flat
graduated measuring plate carrying a swing arm that rotates about the plate
centre on a vertical axis, plus a separately-turning locking fastener concentric
with the same axis.

Source pool: **9 record dirs — 3 picture origins and 6 forked variants. All 9 were
read in full before any candidate was chosen.** The three origins were read line
by line. Each variant is a byte-level fork of one origin, so it was read as a full
unified diff against that parent: every changed line was reviewed and the
unchanged remainder is identical to a file already read line by line. Parentage
was established by diff size, not by name:

| Variant | Parent origin | Changed lines |
|---|---|---|
| `body_form_full_circle` | 002 | 34 |
| `body_form_quadrant` | 003 | 108 |
| `arm_form_long_ruler` | 003 | 35 |
| `lock_cam_lever` | 002 | 116 |
| `reading_module_vernier_plate` | 002 | 102 |
| `arm_count_dual_arms` | 001 | 290 |

Frame convention for the rebuild: the plate lies in the XY plane with `+Z` up and
`+Z` is the pivot axis for **every** joint in the category — arm and lock alike.
The plate's marked face is its `+Z` face; every moving member stacks above it.
`z=0` is the underside of the plate.

sync_records:
  - rec_picturex_0611__protractor_with_swing_arm__001__png_093c22d36b654f4084f5398231a08e55
  - rec_picturex_0611__protractor_with_swing_arm__002__png_0a68ef8fd5f242f3a7abe1db6a9833ac
  - rec_picturex_0611__protractor_with_swing_arm__003__png_0437faf5b68e4d3ba4f882021039b154
  - rec_0611_protractor_with_swing_arm_var_body_form_full_circle
  - rec_0611_protractor_with_swing_arm_var_body_form_quadrant
  - rec_0611_protractor_with_swing_arm_var_arm_form_long_ruler
  - rec_0611_protractor_with_swing_arm_var_lock_cam_lever
  - rec_0611_protractor_with_swing_arm_var_reading_module_vernier_plate
  - rec_0611_protractor_with_swing_arm_var_arm_count_dual_arms

## Component slots and candidates

All record paths below are relative to `data/records/<record>/revisions/rev_000001/model.py`.

### Slot A — `body_form` (host plate; ① silhouette + part tree)

| Candidate | Record | Exact span | Diversity axis | Key construction |
|---|---|---|---|---|
| `semicircular_solid_plate` | `…__001__png_093c22d36b654f4084f5398231a08e55` | L34-L88 | ① 180° solid sector + integral rule | `circle(60)` extruded 2.2 mm, intersected with a `centered=(True,False,False)` clip box to make a half disc, then unioned with a 304×18×1.8 mm `fixed_rule` offset to `(-44, -10)`. The rule is *fused into the same solid*, not a second part. Graduations at L66-L86 are **cut** (37 radial ticks, 2 guide arcs at r=42/51, 58 rule ticks) so the whole body stays one visual |
| `semicircular_arch_rail` | `…__002__png_0a68ef8fd5f242f3a7abe1db6a9833ac` | L29-L69 (+ markings L72-L134) | ① 180° annular arch | `_semidisk(0.078)` minus `_semidisk(0.054)` gives an open arch with a 24 mm wall; a separate 0.166×0.015 m rail spans both arch feet at `y=-0.0025`. Markings are a **second visual on the same part** built as one welded CAD solid (outer ink band + 37 radial ticks + baseline + 33 rule ticks + 2 side returns), not per-tick primitives |
| `full_circle_annulus` | `…_var_body_form_full_circle` | L38-L66 | ① 360° annular ring | Fork of `semicircular_arch_rail`: `circle(OUTER_RADIUS)` minus `circle(INNER_RADIUS)` full ring. **The straight rail is dropped entirely** — a closed ring has no feet to span. Author test L378-L385 asserts `body_y_min < -OUTER_RADIUS + 0.005`, i.e. the body really extends below the pivot centreline |
| `full_circle_solid_plate` | `…__003__png_0437faf5b68e4d3ba4f882021039b154` | L29-L44 | ① 360° solid disc with raised rim | `circle(0.075)` with a concentric `circle(PIVOT_HOLE_RADIUS)` bore, extruded 1.5 mm, plus a raised annular scale rim (r 0.057→0.075, 0.4 mm) unioned at `offset=BODY_THICKNESS - 0.00005`. The −0.05 mm overlap is deliberate: it welds the rim to the plate instead of leaving a coincident-face solid |
| `quadrant_sector` | `…_var_body_form_quadrant` | L29-L71 | ① 90° sector | Builds the full plate + full rim, then **cuts two half-space boxes** (`center(-R,0).rect(R*2,R*4)` and `center(0,-R).rect(R*4,R*2)`, both extruded `h_plate+h_rim+0.002` from `offset=-0.001`) leaving the `+X,+Y` quarter. Cutting from a complete body rather than authoring a sector profile keeps the rim weld intact |

### Slot B — `arm_form` (swing member; ① blade silhouette / part tree)

| Candidate | Record | Exact span | Diversity axis | Key construction |
|---|---|---|---|---|
| `tapered_rule_pointer_tail` | `…__001__…` | L91-L126 | ① single-ended blade + tail | 5-point tapered profile 0→260 mm narrowing 9→8 mm then to a point, unioned with an `r=14` pivot boss **and a separate 5-point `pointer_tail` spanning x −25→+1 mm**, so the blade is single-ended but has a short indexing tail across the pivot. Bore `r=4.9`. Scale ticks and a 230 mm sight line are cut at L116-L125 |
| `pointed_strip` | `…__002__…` | L137-L155 | ① short strip + hub | 108 mm strip, constant 10.4 mm width until a point at the tip, unioned with an `r=0.0110` hub. Much shorter than the plate is wide; carries a separate `tip_stop` Box visual at L259-L264 that reads as the pointer |
| `double_ended_blade` | `…__003__…` | L47-L77 | ① symmetric double-ended blade | 12-point outline spanning y −0.080→+0.068 — an **upper straight ruler and a lower tapered pointer on opposite sides of the pivot**, plus a concentric `circle(0.0049)` in the same `.polyline().close()` call so the bore is part of the profile. Extruded `both=True` about `z=0`, so the arm is symmetric about its own mid-plane, and it carries its **own** `r=0.0125/0.0049` pivot boss on top (L70-L76) for the fastener to seat on |
| `vernier_plate_arm` | `…_var_reading_module_vernier_plate` | L158-L196 (plate), L199-L229 (vernier ink) | ① widened reading head | Fork of `pointed_strip`: the strip is cut back to start at `x=0.026` and a **26 × 26 mm rectangular vernier plate** is unioned in over the hub region. Ten vernier divisions at 3 mm pitch plus a 30 mm baseline are welded into one ink solid. Author test asserts the plate's Y extent ≥ 0.025 m, i.e. the widening is real and not decorative |

### Slot C — `lock_module` (fastener on the pivot axis; ③ joint parent + capture topology)

| Candidate | Record | Exact span | Joint parent in source | Key construction |
|---|---|---|---|---|
| `knurled_clamp_screw` | `…__001__…` | L129-L144, joint L256-L269 | **body** (`protractor`) | Captive shaft `r=3.5` running 10 mm *below* the plate, lower flange `r=9.2`, grip `r=9.4`, cap `r=8.9`, then **32 axial ribs** unioned at `r=9.25` around the grip. A separate `Cylinder(0.0112, 0.0006)` washer visual seats on the arm. Limits ±4π — a multi-turn screw |
| `slotted_screw` | `…__002__…` | L177-L197, joint L304-L317 | **arm** | Shaft `r=0.0023` + head `r=0.0062`, with a real 8.2×1.2×0.7 mm slot **cut** into the head, and a dark `screw_slot` Box dropped into the machined slot so the turn is legible. Limits ±π |
| `capstan_screw_retainer` | `…__003__…` | L230-L270, joint L272-L290 | **arm** | Four-visual assembly: `screw_shaft` r 0.0037, `screw_cap` r 0.0100 above, **`underside_retainer` r 0.0063 below the plate**, and two crossed slot bars. The retainer is what makes this candidate structurally different — the fastener *captures* the plate from underneath rather than merely resting on top. Author test L422-L429 checks that contact |
| `cam_lever` | `…_var_lock_cam_lever` | L210-L252, host relief L158-L165 | **arm** | Eccentric lobe `r=0.0070` offset `+1.8 mm` from the axis, 26 mm handle, `r=0.0029` rounded tip, and an `r=0.0042` collar that seats on the hub. **Host adaptation is mandatory and source-attested**: the arm hub gets a 36 × 6.8 × 0.4 mm flat relief *cut* into its top face at `x=+0.014` (L158-L164) for the handle to lie in when clamped |

### Slot D — `arm_count` (multiplicity N)

| Record | Exact span | Mechanism |
|---|---|---|
| `…_var_arm_count_dual_arms` | L211-L246 (build), L283-L296 (clamp), L24-L26 (angles) | The **only** multiplicity evidence in the pool, and it is index-general. Arms are **stacked in Z on a shared axis, all parented to the body** (not chained arm-to-arm): `arm_z[i] = 0.0024 + i * arm_thickness`, i.e. `seat_z + i·t`. Rest angles are spread so arms do not coincide (`[48°, 120°]`) and each arm keeps its own full `lower=-rest, upper=pi-rest` range. The clamp is lifted onto the topmost arm by `clamp_z = arm_z[-1] + arm_thickness` (L284) and its washer contact test retargets from `arm_0` to `arm_1` (L481-L488) |

## Mating mechanisms (sampled across records, not per candidate)

Per `MECHANICAL_PRIORS.md` §1b these were read across *all* records rather than one
per candidate. They are the numbers that decide whether the assembly stands up, and
they differ record to record.

**1. Two distinct arm bearings exist in the pool — do not assume one.**

* *Thrust-boss seating* (001, 002): the body carries a low **annular** boss around
  the bore and the arm's flat underside lands on it exactly.
  001 L57: `circle(7.6).extrude(0.2)` at `z=2.2` → seat `z=2.4 mm`, joint origin
  `xyz=(0,0,0.0024)` (L247), test `expect_gap(max_gap=0.00005)`.
  002 L53-L60: `circle(0.0105).circle(0.0031).extrude(0.0005)` at `z=BODY_THICKNESS`
  → joint origin `BODY_THICKNESS + PIVOT_CLEARANCE_Z` (L293) where
  `PIVOT_CLEARANCE_Z = 0.0005` **is exactly the boss height** (L26), test
  `max_gap=0.00003`. So the arm seat plane is *derived* from the boss, never a magic
  constant.
* *Running clearance* (003): **no body boss at all.** Plate 1.5 mm + rim 0.4 mm =
  1.9 mm top; arm extruded `both=True` about its own origin at `ARM_FRAME_Z=0.0032`
  so its underside is at 2.05 mm — a **0.15 mm air gap**, asserted as
  `expect_gap(min_gap=0.00002, max_gap=0.00025)` (L406-L413). Here the arm carries
  its own boss on *top* instead, for the fastener.

Both are legitimate; the template must derive the seat plane from whichever bearing
the body/arm pair actually builds, and must not close 003's clearance to satisfy a
support check.

**2. Bore/shaft fits are a consistent rule, not per-record noise.**

| Record | body bore r | arm bore r | shaft r | min radial clearance |
|---|---|---|---|---|
| 001 | 4.7 mm (L61) | 4.9 mm (L112) | 3.5 mm (L131) | 1.2 mm |
| 002 | 3.1 mm (L63-L68) | 3.0 mm (L149-L154) | 2.3 mm (L178-L184) | 0.7 mm |
| 003 | 4.6 mm (`PIVOT_HOLE_RADIUS`, L24) | 4.9 mm (L68) | 3.7 mm (L240) | 0.9 mm |

Rule: `shaft_r ≈ min(bore_r) − 0.7…1.2 mm`, and 003 makes it an explicit author
check (L430-L437). The bores are **really cut through** in all three origins, which
is why the shaft can pass through the plate without a solid intersection — the
clearance is geometric, not an allowance.

**3. Fastener seating planes are derived, never authored twice.**

* 001: joint origin `z=0.0041` = arm seat `0.0024` + arm thickness `0.0017`, and the
  washer's local origin is `+0.0003` with length `0.0006`, so its underside lands on
  `z=0` of the screw frame = the arm's top face.
* 002: joint `origin=Origin()` — the screw frame *is* the arm frame — and the head
  is extruded from `z=0.0030 = ARM_THICKNESS` (L188-L190), i.e. off the arm's top face.
* 003: joint `origin=Origin()` again; `underside_retainer` centre `−0.00365`,
  length `0.0009` → top face at `−0.0032 = −ARM_FRAME_Z`, which in world lands
  exactly on the plate's underside at `z=0`. That is the capture derivation.

**4. Contact and overlap expectations the pool asserts on every seed.**

`expect_overlap(arm, body, axes="xy", min_overlap=0.010…0.020)` in all three origins
— the arm must genuinely cross the plate rather than perch over the hub — plus
`expect_origin_distance(..., axes="xy", max_dist=0.0001)` in 003 for concentricity of
plate, arm and screw.

**5. The quadrant body re-derives the arm's joint limits.**

This is the one true cross-slot binding in the category. `body_form_quadrant`
L245-L253 changes `body_to_arm` from `(-π, +π)` to `(0, π/2)` and its author test
L370-L384 asserts it. The arm's travel is the body's angular span; a 90° plate with
a 180° arm sweep would swing the blade off the scale. The same record also
re-derives graduation counts (`range(19)` outer, `range(9)` inner at L158/L180)
from the same span.

**6. Effort and scale.**

Arm joints run `effort` 0.8–2.0, `velocity` 2.0–3.0; lock joints `effort` 0.25–1.8,
`velocity` 4.0–5.0. Plate radii 0.060–0.078 m, plate thickness 0.0015–0.0030 m, arm
thickness 0.0017–0.0030 m. These are desk-scale objects throughout; there is no
large-scale member in the pool.

## Deliberate deviation from source construction — graduation emission

003 emits its graduations as **108 separate `Box` visuals** on the body part
(72 outer ticks L129-L148 + 36 red inner ticks L150-L168) and 8 more on the arm.
`sdk/_core/v0/exact_collisions.py` derives one collision solid per visual 1:1, so
that construction turns a decorative scale into ~116 collision bodies.

001 (L66-L86) and 002 (L72-L134) both take the other route: ticks are **cut into**,
or welded into, a single CAD solid, giving one visual per part with the same visible
detail. The rebuild uses the 001/002 route for every candidate, including the
full-circle and quadrant bodies forked from 003.

This is stated here rather than silently applied: it changes *how* 003's scale is
emitted, not *what* it looks like, and it is the construction 2 of the 3 origins
already use.

## Folded into a parameter rather than a candidate

`arm_form_long_ruler` (fork of 003) changes only the upper-ruler length,
`0.068 → 0.140 m` (L53-L56), the centre rule that dresses it (L194-L199) and the tick
count `6 → 15` (L206-L210). The outline point count, part tree, joint set and every
mating number are untouched. Per `VISUAL_DIVERSITY_MODEL.md` that is a proportion
change, so it becomes an independent continuous parameter of `double_ended_blade`
(`upper_ruler_length`, m, range 0.068–0.140, tick pitch derived from it) rather than
a fifth `arm_form` candidate. Both source extremes remain reachable.

## Multiplicity range

The pool shows N=1 (all three origins, all five single-arm variants) and N=2
(`arm_count_dual_arms`). The declared range is **N ∈ {1, 2, 3}**. The extension to
3 is an explicit extrapolation, justified because the source's stacking rule is
written index-generally — `arm_z[i] = seat + i·t`, `clamp_z = arm_z[-1] + t`, all
arms parented to the body — so N=3 needs no new mechanism, only one more term. Rest
angles are spread evenly across the body's angular span instead of the source's
hard-coded `[48°, 120°]`, which is the same intent generalised.

## Category anchors

1. **One root plate part** carrying graduation geometry. Every other part is a
   descendant; the plate is the only grounded member.
2. **N swing-arm parts, N ∈ {1,2,3}**, each with its own `REVOLUTE` joint whose
   axis is `(0,0,1)` and whose origin is on the plate centre — all parented to the
   plate, never chained arm-to-arm (`arm_count_dual_arms` L217-L246).
3. **Exactly one lock-module part** with a `REVOLUTE` joint about the same
   `(0,0,1)` axis, concentric with the arm pivot to within 0.1 mm. Its parent is
   the plate for `knurled_clamp_screw` and the topmost arm for the other three
   candidates — that difference is part of the candidate, not free choice.
4. **Every joint in the category is revolute about +Z.** There is no prismatic,
   continuous or non-vertical joint anywhere in the pool. This is what makes the
   category machine-checkable.
5. **Real through-bores.** Plate and every arm carry a cut bore on the axis, and
   the fastener shaft is strictly smaller than the smallest of them.
6. **The arm crosses the plate.** `expect_overlap(arm, body, axes="xy")` ≥ 0.010 m
   in every origin; an arm that does not reach past the graduations is not a
   protractor.

## Accepted candidate manifest (machine-readable)

The per-slot tables above are the human-readable evidence. This table is the same
set in the column layout `agent/source_maps.py` parses for `design-init`.

| slot | candidate | diversity axis | source type | record/revision | exact model.py:Lx-Ly | key parts/joints/helpers | status |
|---|---|---|---|---|---|---|---|
| body_form | semicircular_solid_plate | ① silhouette / part tree | host plate | rec_picturex_0611__protractor_with_swing_arm__001__png_093c22d36b654f4084f5398231a08e55/rev_000001 | model.py:L34-L88 | protractor, protractor_body, _build_protractor_body, _box, half_disc, fixed_rule, pivot_boss, pivot_bore | accepted |
| body_form | semicircular_arch_rail | ① silhouette / part tree | host plate | rec_picturex_0611__protractor_with_swing_arm__002__png_0a68ef8fd5f242f3a7abe1db6a9833ac/rev_000001 | model.py:L29-L69, model.py:L72-L134 | protractor_body, transparent_body, degree_markings, _semidisk, _protractor_body_shape, _protractor_markings_shape, rail, pivot_boss | accepted |
| body_form | full_circle_annulus | ① silhouette / part tree | host plate | rec_0611_protractor_with_swing_arm_var_body_form_full_circle/rev_000001 | model.py:L38-L66 | protractor_body, transparent_body, _protractor_body_shape, outer, inner_cutter, pivot_boss, bore | accepted |
| body_form | full_circle_solid_plate | ① silhouette / part tree | host plate | rec_picturex_0611__protractor_with_swing_arm__003__png_0437faf5b68e4d3ba4f882021039b154/rev_000001 | model.py:L29-L44 | protractor_body, body_shell, _make_protractor_body, plate, rim, PIVOT_HOLE_RADIUS | accepted |
| body_form | quadrant_sector | ① silhouette / part tree | host plate | rec_0611_protractor_with_swing_arm_var_body_form_quadrant/rev_000001 | model.py:L29-L71, model.py:L245-L253 | protractor_body, body_shell, _make_protractor_body, full_plate, full_rim, cut_neg_x, cut_neg_y, body_to_arm | accepted |
| arm_form | tapered_rule_pointer_tail | ① blade silhouette | swing member | rec_picturex_0611__protractor_with_swing_arm__001__png_093c22d36b654f4084f5398231a08e55/rev_000001 | model.py:L91-L126 | swing_arm, swing_arm_body, _build_swing_arm, long_rule, pivot_boss, pointer_tail, pivot_bore, sight | accepted |
| arm_form | pointed_strip | ① blade silhouette | swing member | rec_picturex_0611__protractor_with_swing_arm__002__png_0a68ef8fd5f242f3a7abe1db6a9833ac/rev_000001 | model.py:L137-L155, model.py:L259-L264 | swing_arm, arm_plate, _swing_arm_shape, strip, hub, bore, tip_stop | accepted |
| arm_form | double_ended_blade | ① blade silhouette | swing member | rec_picturex_0611__protractor_with_swing_arm__003__png_0437faf5b68e4d3ba4f882021039b154/rev_000001 | model.py:L47-L77 | swing_arm, arm_shell, _make_swing_arm, blade, pivot_boss, ARM_THICKNESS | accepted |
| arm_form | vernier_plate_arm | ① blade silhouette | swing member | rec_0611_protractor_with_swing_arm_var_reading_module_vernier_plate/rev_000001 | model.py:L158-L196, model.py:L199-L229 | swing_arm, vernier_plate, vernier_scale, _vernier_plate_shape, _vernier_markings_shape, arm_strip, plate, hub | accepted |
| lock_module | knurled_clamp_screw | ③ joint parent / capture topology | pivot fastener | rec_picturex_0611__protractor_with_swing_arm__001__png_093c22d36b654f4084f5398231a08e55/rev_000001 | model.py:L129-L144, model.py:L256-L269 | clamp_screw, clamp_fastener, clamp_washer, _build_clamp_fastener, clamp_rotation, shaft, grip, cap, rib | accepted |
| lock_module | slotted_screw | ③ joint parent / capture topology | pivot fastener | rec_picturex_0611__protractor_with_swing_arm__002__png_0a68ef8fd5f242f3a7abe1db6a9833ac/rev_000001 | model.py:L177-L197, model.py:L304-L317 | lock_screw, locking_fastener, screw_slot, _locking_screw_shape, screw_turn, shaft, head, slot_cutter | accepted |
| lock_module | capstan_screw_retainer | ③ joint parent / capture topology | pivot fastener | rec_picturex_0611__protractor_with_swing_arm__003__png_0437faf5b68e4d3ba4f882021039b154/rev_000001 | model.py:L230-L270, model.py:L272-L290 | pivot_screw, screw_shaft, screw_cap, underside_retainer, slot_bar_x, slot_bar_y, arm_to_screw | accepted |
| lock_module | cam_lever | ③ joint parent / capture topology | pivot fastener | rec_0611_protractor_with_swing_arm_var_lock_cam_lever/rev_000001 | model.py:L210-L252, model.py:L158-L165 | cam_lever, cam_lever_body, lever_indicator, _cam_lever_shape, cam_lobe, handle, handle_tip, collar, lever_rest_flat | accepted |
| arm_count | stacked_arms_shared_axis | ② multiplicity / joint count | multiplicity | rec_0611_protractor_with_swing_arm_var_arm_count_dual_arms/rev_000001 | model.py:L211-L246, model.py:L283-L296 | arm_0, arm_1, arm_pivot_0, arm_pivot_1, arm_body_0, arm_body_1, arm_z_positions, clamp_z, ARM_REST_ANGLES_DEG | accepted |
| arm_form | long_ruler_blade | ⑤ proportion only | swing member | rec_0611_protractor_with_swing_arm_var_arm_form_long_ruler/rev_000001 | model.py:L47-L81 | _make_swing_arm, outline, upper_center_rule, arm_tick_positions | rejected — folded into the `upper_ruler_length` parameter of `double_ended_blade`; the part tree, joint set and every mating number are unchanged |
