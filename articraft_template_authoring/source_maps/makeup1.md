# Makeup1 — SourceMap

export_category: makeup1

The source pool is three origin records (`001` nine-pan pressed-powder compact with a hinged
cover, `002` ten-well complexion palette with a framed clear cover, `003` two-way cake compact
with mirror lid and a front push latch) plus nine directed forks. The authoritative category
identity is an **articulated cosmetic compact / powder palette**: one moulded case body whose
top deck is a real recessed well field holding pan-cup + pressed-cake sub-assemblies, a real
hinged cover with an inner mirror plaque and a captured hinge pin, an optional front closure
(latch) hardware, and optional auxiliary opening trays (front fold-out tray, vertical fan-out
tray).

Four component slots are accepted: `case_form` (primary plan family), `well_pattern`
(well geometry/topology family), `closure` (front closure mechanism, differing in joint
count/type/axis) and `opening` (auxiliary opening mechanism, differing in joint count/axis).
The observed well counts are a multiplicity `N`, not slot candidates. Well field, lid seat,
hinge line, latch pocket and auxiliary mounts are all derived from the selected `case_form`,
so every declared slot combination remains legal without a compatibility gate.

Frame convention for the rebuild: `+X` runs along the case width, `+Y` points to the rear
(hinge side), `+Z` is up. The case bottom sits at `z = 0`; the cover closes down onto the case
rim. Source `001`/`003` author the lid in an already-open display pose and `002` authors it
folded flat behind the tray; the rebuild standardises on `q = 0` = closed and positive travel =
open. That is a datum choice, not a structural difference.

sync_records:
  - rec_picturex_0611__makeup1__001__png_1e56ed25897943d1bb05005bc41aca4e
  - rec_picturex_0611__makeup1__002__png_350d6df173ce4cc08935724fb35d43dc
  - rec_picturex_0611__makeup1__003__png_1e77f77007c24952b1f52a18542fa4d8
  - rec_0611_makeup1_var_case_form_elongated_rectangle
  - rec_0611_makeup1_var_case_form_round_puck
  - rec_0611_makeup1_var_closure_push_latch
  - rec_0611_makeup1_var_closure_sliding_latch
  - rec_0611_makeup1_var_opening_fan_out_tray
  - rec_0611_makeup1_var_opening_second_hinged_tray
  - rec_0611_makeup1_var_powder_layout_12_well
  - rec_0611_makeup1_var_powder_layout_4_quadrant
  - rec_0611_makeup1_var_powder_layout_6_radial

## Accepted component candidates

| Slot | Candidate | Diversity axis | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| case_form | rounded_rectangle | ③ primary form family | moulded compact case body | rec_picturex_0611__makeup1__001__png_1e56ed25897943d1bb05005bc41aca4e/rev_000001 | model.py:L51-L68; model.py:L71-L86; model.py:L133-L179 | accepted source-backed | Rounded-rectangle plate body with a shallow continuous pan recess and a cut front thumbnail catch; two moulded rear knuckles on a low reinforcing rail; full-footprint cover with underside recess, barrel and web. |
| case_form | elongated_rectangle | ③ primary form family | moulded compact case body | rec_0611_makeup1_var_case_form_elongated_rectangle/rev_000001 | model.py:L66-L108; model.py:L164-L201; model.py:L203-L216; model.py:L404-L411 | accepted source-backed | Wider/shallower rounded-rectangle plan (0.150 x 0.055) with the well pair spread outboard, hinge knuckles pushed to x = ±0.058, a 0.140 pin and a matching 0.146 x 0.052 lid; the fork's own test asserts width > 1.8 x depth. |
| case_form | round_puck | ③ primary form family | moulded compact case body | rec_0611_makeup1_var_case_form_round_puck/rev_000001 | model.py:L20-L31; model.py:L55-L80; model.py:L145-L180; model.py:L476-L487 | accepted source-backed | Circular puck body extruded from a circle with a circular pan recess and a front catch cut into the curved wall; circular lid disc with a circular underside recess plus the retained rectangular inner plaque; the fork's own test asserts an approximately circular footprint. |
| well_pattern | orthogonal_grid | ③ well geometry/topology | recessed pan field | rec_picturex_0611__makeup1__001__png_1e56ed25897943d1bb05005bc41aca4e/rev_000001 | model.py:L89-L130; model.py:L246-L270 | accepted source-backed | Rounded-rectangle pressed pans with repeated loop-and-bar press marks laid out on an orthogonal 3x3 grid of pitch 0.0312 inside one continuous rounded-rectangle recess. |
| well_pattern | radial_ring | ③ well geometry/topology | recessed pan field | rec_0611_makeup1_var_powder_layout_6_radial/rev_000001 | model.py:L29-L42; model.py:L56-L94; model.py:L97-L104; model.py:L187-L194 | accepted source-backed | Circular pan inserts with a filleted top rim, each sitting in its own circular cavity cut in the tray floor, placed on a ring of radius 0.025 with even angular pitch 2*pi/N; the fork's own test asserts constant radius and equal angular spacing. |
| well_pattern | fan_sector | ③ well geometry/topology | recessed pan field | rec_0611_makeup1_var_opening_fan_out_tray/rev_000001 | model.py:L106-L120; model.py:L159-L163; model.py:L213-L226; model.py:L313-L320 | accepted source-backed | Sector/wedge pan inserts built from `moveTo`/`threePointArc` over a 50 degree arc, each yawed by `_fan_yaw` so it faces away from a common fan centre, arranged on a fan whose front row spans wider than its back row. |
| closure | rear_hinge | ① closure mechanism (1 joint) | cover retention | rec_picturex_0611__makeup1__002__png_350d6df173ce4cc08935724fb35d43dc/rev_000001 | model.py:L41-L82; model.py:L95-L128; model.py:L210-L227 | accepted source-backed | Only one non-fixed joint: the rear cover hinge. Retention is a moulded front seam/notch cut into the shell plus interleaved outer/inner hinge knuckles and support tabs; no separate latch part exists. |
| closure | push_latch | ① closure mechanism (2 joints, revolute rocker) | front push latch | rec_0611_makeup1_var_closure_push_latch/rev_000001 | model.py:L287-L294; model.py:L314-L352; model.py:L354-L367; model.py:L503-L513 | accepted source-backed | Separate `latch` part: button face above the pivot, rocker lever body, catch hook below the pivot and a cylindrical pivot boss; `latch_press` is REVOLUTE about (-1,0,0) with 0..18 degrees, and a `lid_strike` block on the cover is the catch face. |
| closure | sliding_latch | ① closure mechanism (2 joints, prismatic slider) | front sliding latch | rec_0611_makeup1_var_closure_sliding_latch/rev_000001 | model.py:L287-L292; model.py:L312-L333; model.py:L334-L347; model.py:L487-L496 | accepted source-backed | Separate `latch` part: front thumb slider tab, guided rail retained by the front housing and a hook; `latch_slide` is PRISMATIC about (1,0,0) with 0..0.004 m, and a `lid_catch_lip` on the cover is the strike. |
| opening | single_lid | ① opening mechanism (1 moving cover) | cover-only opening | rec_picturex_0611__makeup1__001__png_1e56ed25897943d1bb05005bc41aca4e/rev_000001 | model.py:L272-L299; model.py:L301-L318 | accepted source-backed | Exactly one independently moving section: `cover` on `cover_hinge` (REVOLUTE, axis (-1,0,0), -104..+7 degrees) with a captured 0.100 m steel pin; no auxiliary tray. |
| opening | second_hinged_tray | ① opening mechanism (2 revolute trays) | auxiliary hinged pan tray | rec_0611_makeup1_var_opening_second_hinged_tray/rev_000001 | model.py:L29-L37; model.py:L83-L94; model.py:L118-L183; model.py:L292-L322; model.py:L365-L385 | accepted source-backed | A second `second_tray` part hinged on the case's **front** (-Y) edge: dedicated front hinge knuckles and support tabs are unioned into the base shell, the tray is a thinner moulded shell with four recessed wells plus three interleaved inner knuckles and bridges, and `second_tray_hinge` is a second REVOLUTE joint on the front hinge line. |
| opening | fan_out_tray | ③ opening mechanism (fan-out tray on a vertical pivot) | auxiliary fan-out pan tray | rec_0611_makeup1_var_opening_fan_out_tray/rev_000001 | model.py:L29-L38; model.py:L52-L103; model.py:L106-L120; model.py:L159-L163 | accepted source-derived | The fork encodes a fan-out deck: a trapezoidal tray plan that widens toward the open edge, sector pans yawed about a common fan centre and an arc layout whose front row spans wider than its back row. The rebuild expresses that fan-out as a real sector tray on a vertical (0,0,1) pivot at the case's rear centre, so the geometry the fork describes as "fanning out" becomes an actual swept opening motion instead of a static plan change. |

## Shared (non-slotted) category anchors

Present in every accepted record, therefore rebuilt as shared geometry rather than slots:

- Moulded case body with a real recessed well deck and perimeter rim: 001 model.py:L51-L68;
  002 model.py:L41-L82; 003 model.py:L71-L90.
- Pan-cup + pressed-cake sub-assembly. The cake is never a painted rectangle: 003 builds a
  rose-gold pan liner and a separate raised pan rim (model.py:L107-L125) and lofts the pressed
  cake between two rounded-rectangle stations (model.py:L127-L141); 002 builds a filleted
  circular insert seated in its own cavity (model.py:L85-L92); 001 presses repeated
  loop-and-bar relief into the cake top (model.py:L89-L130); the 12-well fork keeps liner, rim
  and cake for all twelve wells (model.py:L151-L182).
- Perimeter metal trim ring on the rim: 003 model.py:L92-L105.
- Cover with an inner mirror/plaque layer: 003 mirror frame, dark inner edge and mirror glass
  model.py:L215-L272; 001 satin inner plaque model.py:L168-L179; 002 captured clear window
  model.py:L196-L208.
- Interleaved hinge knuckles + captured pin: 003 base knuckles/bosses/pin/caps
  model.py:L161-L198 with the cover barrel and bridge model.py:L274-L285; 002 outer base
  knuckles model.py:L64-L71 with three alternating cover knuckles model.py:L115-L127;
  001 base knuckles model.py:L71-L86 with the cover barrel + web model.py:L151-L159.
- Multi-shade pan palette (each well its own colour): 001 model.py:L208-L221;
  002 model.py:L147-L161; the second-tray fork adds four complementary tray shades
  model.py:L256-L263.

## Multiplicity and where the observed N values come from

- `well_count = 4 | 6 | 9 | 10 | 12`, `item_slot = well_pattern`.
- Observed: 4 (`var_powder_layout_4_quadrant` model.py:L245-L277, a 2x2 quadrant grid),
  6 (`var_powder_layout_6_radial` model.py:L29-L42 + L187-L194),
  9 (origin 001 model.py:L246-L270, a 3x3 grid),
  10 (origin 002 model.py:L176-L187, a 2x5 grid; the fan-out fork keeps 10 on an arc,
  model.py:L35-L38),
  12 (`var_powder_layout_12_well` model.py:L43-L62 + L151-L182, a 4x3 grid).
- Spacing: `orthogonal_grid` derives `(cols, rows)` from N and pitch from the well field
  divided by that grid; `radial_ring` derives an angular pitch of `2*pi/N` on an ellipse
  derived from the field; `fan_sector` derives an angular pitch of `fan_span/N` about the fan
  apex. In all three the pan across-size is `pan_fill_ratio * min(available pitch, field
  clearance)`, so N = 12 fits the smallest legal case and N = 4 does not leave the field.
- Origin 003 also shows a 2-well "two-way cake" deck (model.py:L64-L67, L107-L159). That is a
  count below the accepted N range and is not modelled as a separate candidate; the accepted
  range starts at 4 because 2 wells cannot express any of the three well-geometry families
  (a 2-pan radial ring or 2-pan fan degenerates).

## Why `powder_layout` splits into a slot plus an N

The nine forks name a `powder_layout` axis whose members are 4 / 6 / 9 / 10 / 12 wells. Read
against the source code, those forks change two independent things:

1. **Well geometry / topology family.** `var_powder_layout_6_radial` replaces the orthogonal
   cavity grid with an angularly-spaced ring of *circular* cavities and adds a radial layout
   invariant (model.py:L34-L42, L253-L294). `var_opening_fan_out_tray` replaces the pan insert
   itself with a *sector/wedge* solid that must be yawed per instance about a common fan centre
   (model.py:L106-L120, L159-L163). Those are different cavity topologies, different pan
   profiles and a different per-instance orientation rule — a genuine component slot,
   `well_pattern`.
2. **Count only.** `4_quadrant` (model.py:L245-L277) and `12_well` (model.py:L43-L62,
   L151-L182) keep exactly the orthogonal rounded-rectangle liner/rim/cake construction of
   origin 001/003 and only change how many of them are emitted and the grid pitch. That is a
   multiplicity, so it becomes `well_count`, not a candidate.

Modelling all five counts as candidates would have inflated `core_domain` with pure counting
and hidden the two real geometry families; modelling only N would have thrown away the radial
and sector pan construction. The honest split is three `well_pattern` candidates x
`well_count` in {4, 6, 9, 10, 12}.

## Parameters and derivations

Independent (with units):

- `case_width_m` 0.085–0.150 m — plan width, and the puck diameter for `round_puck`.
- `case_depth_m` 0.060–0.115 m — plan depth for the two rectangular forms only
  (`round_puck` derives depth = diameter).
- `case_height_m` 0.013–0.024 m — body height; wall, cavity depth, rim, hinge height, latch
  pocket height and lid seat all derive from it.
- `puck_flat_ratio` 0.04–0.12 ratio — depth of the rear/front chord flats on `round_puck`,
  as a fraction of the puck radius.
- `lid_open_rad` 1.75–2.15 rad — cover hinge upper travel (source 001 uses 104 degrees,
  003 uses 100 degrees, 002 uses 180 degrees; the rebuild brackets 100–123 degrees).
- `thumb_catch_width_m` 0.016–0.036 m — width of the moulded front catch on `rear_hinge`
  (source 001 cuts a 0.026 catch, 002 a 0.026 notch).
- `latch_press_rad` 0.14–0.35 rad — rocker travel for `push_latch` (source fork: 18 degrees).
- `latch_travel_m` 0.0030–0.0065 m — slider travel for `sliding_latch` (source fork: 0.004).
- `pan_fill_ratio` 0.60–0.90 ratio — pan across-size as a fraction of the available pitch.
- `pan_depth_m` 0.0035–0.0070 m — real well depth (source 002 uses 0.0067 inserts in a
  0.0078 cavity).
- `aux_tray_depth_m` 0.028–0.052 m — front fold-out tray depth (source second-tray fork
  uses 0.058 with 0.009 thickness).
- `aux_open_rad` 1.35–1.60 rad — front fold-out tray travel (flat-deployed to upright); the
  upper bound is derived so the upright tray never leans back into the cover's swept envelope.
- `fan_sweep_rad` 1.30–2.05 rad — fan-out tray swept angle about the vertical pivot.
- `fan_radius_ratio` 0.90–1.20 ratio — fan tray outer radius as a fraction of case depth.

Key derivations (host adaptation):

- `wall_t`, `rim_w`, `floor_t` are fixed shell constants; `cavity_depth = pan_depth_m +
  cup_floor_t + seat clearance`, and `case_height_m` is range-checked so the deepest well plus
  the rim always fits.
- The **well field** derives from `case_form`: a rectangle inset from the plan for the two
  rectangular forms, and `1.414 * (rear_flat_y_m - wall_t_m - field_margin_m)` — the inscribed
  square of the pan-recess circle measured from the derived rear chord flat — for `round_puck`
  (so a puck still hosts an orthogonal grid).
- **Hinge line**: `hinge_y = rear_face_y + knuckle_r + hinge_gap`, `hinge_z = case_height_m +
  lid_t/2 - seat_interference`. For `round_puck` the rear face is a derived chord flat
  (`puck_flat_ratio`) so the knuckles and the reinforcing rail land on real flat material
  instead of a tangent curve.
- **Lid**: plan = case plan grown by `skirt_t + skirt_clearance`; the lid's local origin is on
  the hinge axis, every lid element stays at a radial distance greater than
  `knuckle_r + clearance` from that axis, and the barrel bore is `pin_r + pin_clearance`, so
  the captured pin needs no overlap allowance at any pose.
- **Latch pocket**: cut into the front wall between `case_height_m - pocket_h` and
  `case_height_m`, sized from the latch envelope plus clearance; `round_puck` derives a front
  chord flat so the pocket has a flat mouth. `push_latch` gets two solid inward pivot stubs on
  the pocket walls and the rocker gets a through bore; `sliding_latch` gets a real through
  guide slot whose length is `rail_len + latch_travel_m + 2*clearance`.
- **Hinge hardware span**: `rear_span_m` / `aux_span_m` are the half-widths of real flat
  material on the rear and front faces (the chord half-width for `round_puck`, half the plan
  width otherwise). Knuckle position, knuckle length, pin length and barrel length all derive
  from them, so the puck's knuckles never hang off its tangent circle. The cover barrel and the
  front tray barrel keep a real 0.8 mm axial clearance inside the knuckle gap; a bored thrust
  collar on each barrel end carries the axial location against the knuckle face, which is also
  the real running contact that keeps every moving part supported at every pose.
- **Auxiliary mounts**: `second_hinged_tray` derives front hinge knuckles below the lid skirt
  bottom, at `front_hinge_y = -(depth/2 + aux_hinge_offset)` so the whole tray sweep stays in
  front of the cover's swept envelope. `fan_out_tray` derives a vertical pivot post on the case
  underside plus a shallow circular relief, and the sector tray's wells are recessed into its
  top face so the stowed tray clears the case bottom.
- `aux_well_count = clamp(round(well_count/3), 2, 4)` and the auxiliary pan size derive from
  the main pan module, so the auxiliary trays scale with N.

## Category identity and motion

- Exactly one root part `case` (role `case`). Children: `lid` (role `lid`, REVOLUTE about
  `(-1,0,0)` on the rear hinge line, `lower = 0` closed, `upper = lid_open_rad`); optionally
  `latch` (role `latch`, REVOLUTE about `(-1,0,0)` for `push_latch`, PRISMATIC about `(1,0,0)`
  for `sliding_latch`); optionally `front_tray` (role `front_tray`, REVOLUTE about `(-1,0,0)`
  on the front hinge line) or `fan_tray` (role `fan_tray`, REVOLUTE about `(0,0,1)`).
- Every revolute joint is solved with `AxisInterface`/`mate_axes` and registered with
  `register_interface_mate`; each axis runs through the real pin, stub or pivot post.
- The closed lid seats on the real case rim (a `PlaneInterface` whose `extent` is the rim
  footprint, solved with `mate_planes`), clears every pressed cake, and its skirt closes over
  the case outer wall with a real clearance gap.
- No `allow_overlap` is used anywhere: the pin sits in a bored barrel, the rocker bore sits on
  solid stubs, the slider rail passes through a real through-slot, and the fan pivot post sits
  in a real bore.

## Rejected decompositions

- **Well count as slot candidates** — rejected; see the split section above. Counting is N.
- **A separate `palette_style` slot** (the legacy v1 spec had five palettes) — rejected: colour
  and material alone never make a structural candidate. Palettes are sampled per seed for
  appearance variety and count toward neither `core_domain` nor `raw_domain`.
- **A `mirror` slot** — rejected: every origin record has an inner cover layer (satin plaque,
  clear window, framed mirror), so it is a shared anchor, not an interchangeable variant.
- **Making the source 003 prismatic front push button a fourth `closure` candidate** —
  rejected: `var_closure_push_latch` supersedes it with the same front-push semantics but real
  rocker hardware (pivot boss, catch hook, lever body) and a revolute axis, which keeps the
  three closure candidates distinct in joint type as well as geometry.
- **Folding the auxiliary tray back over the case top** (the source fork drives
  `second_tray_hinge` to `pi`, model.py:L365-L385) — rejected as a *motion* target for the
  rebuild: the rebuilt cover is genuinely closable, so a tray that folds over the deck would
  have to interpenetrate the closed cover. The rebuild keeps the fork's structure (front hinge
  line, dedicated knuckles, thinner welled tray shell, second revolute joint) and derives the
  travel so the tray sweep and the cover sweep are disjoint half-planes.
- **Compatibility gates between `case_form` and the other slots** (the legacy v1 template gated
  `round_puck` against several layouts) — rejected and removed: the puck now derives chord
  flats for the hinge and latch and an inscribed well field, so all 81 slot combinations build.
