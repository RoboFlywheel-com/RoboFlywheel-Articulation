# makeup3 — SourceMap

export_category: makeup3

Authoritative records live under `data/records`. The rebuild target is one **articulated
makeup compact**: a shallow case body (round / rounded-rectangular / hexagonal footprint)
whose cavity carries `N` real powder inserts (metal cup + pressed cake sub-assemblies), a
cover that either flips on a rear revolute hinge or slides on a guided prismatic track, and
a front closure that is either a push-slide button captured in a wall pocket or a toggle
latch pivoting on a captured pin.

The pool is two origin records plus eight `_var_` forks. Origin `001` is the gold four-petal
palette family; origin `002` is the gloss-black single pressed-powder family. The forks were
authored one axis at a time, so each one isolates exactly one difference against its parent,
which is what makes the slot split defensible.

Frame convention for the rebuild: `+X` right, `+Y` back (hinge side), `-Y` front (closure
side), `+Z` up. The case footprint is centred on the origin in XY, its floor at `z=0`. The
lid joint's zero value is **closed** for both motions (revolute `lower=0` closed →
`upper=open_angle`; prismatic `lower=0` closed → `upper=slide_travel`). Sources 001/002 used
a negative-lower "ajar reference pose"; the rebuild standardises on closed-at-zero so the
static assembly is genuinely seated. That is a coordinate/limit convention, not a structural
change.

sync_records:
  - rec_picturex_0611__makeup3__001__png_d432b592bfe24d18aefa827f7ae9c15e
  - rec_picturex_0611__makeup3__002__png_4960c988351041a8a8bc5cc76140e8b6
  - rec_0611_makeup3_var_case_form_round
  - rec_0611_makeup3_var_case_form_rectangular
  - rec_0611_makeup3_var_case_form_hexagonal
  - rec_0611_makeup3_var_lid_module_fitted_inner_mirror
  - rec_0611_makeup3_var_insert_motion_guided_slide
  - rec_0611_makeup3_var_closure_toggle_latch
  - rec_0611_makeup3_var_powder_layout_2_well
  - rec_0611_makeup3_var_powder_layout_4_well

## Component slots and candidates

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Diversity axis | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| case_form | round | forked primary form | rec_0611_makeup3_var_case_form_round/rev_000001 | model.py:L27-L43, model.py:L177-L206, model.py:L417-L447 | accepted | ③ primary form | axisymmetric stepped case wall (`_base_wall` `LatheGeometry.from_shell_profiles`), circular floor disc, circular rim; roundness assertion `base_xy_ratio > 0.92` proves the footprint is the identity |
| case_form | rounded_rect | forked primary form | rec_0611_makeup3_var_case_form_rectangular/rev_000001 | model.py:L19-L28, model.py:L33-L75, model.py:L98-L176, model.py:L393-L412 | accepted | ③ primary form | rounded-rectangle footprint (`_rounded_rect_plate`, `_rounded_rect_tube`, `_base_wall`, `_base_floor`), 96×80 mm plan with corner fillet, matching rectangular lid + skirt; assertion `base_dx > base_dy + 0.004` |
| case_form | hexagonal | forked primary form | rec_0611_makeup3_var_case_form_hexagonal/rev_000001 | model.py:L164-L224, model.py:L304-L344, model.py:L549-L565 | accepted | ③ primary form | six-sided `polygon(6)` base body, hexagonal tray, hexagonal outer rim, hexagonal lid shell and lacquer panel; assertion `dx > dy * 1.08` (vertices on ±X, flats on ±Y) |
| lid_motion | flip_hinge | origin joint/mechanism | rec_picturex_0611__makeup3__002__png_4960c988351041a8a8bc5cc76140e8b6/rev_000001 | model.py:L66-L139, model.py:L189-L206, model.py:L227-L259 | accepted | ② joint type | REVOLUTE about X on a rear hinge line; two fixed case knuckles (`hinge_knuckle_0/1`) plus a lid barrel inside `_lid_shell_closed`, lid skirt, `base_to_lid` with bounded limits |
| lid_motion | guided_slide | forked joint/mechanism | rec_0611_makeup3_var_insert_motion_guided_slide/rev_000001 | model.py:L114-L122, model.py:L198-L228, model.py:L292-L308, model.py:L350-L366, model.py:L390-L408 | accepted | ② joint type | PRISMATIC lid: `_slide_rail` raised rails replace the hinge barrels, tray guide channels, centred lid shell with a `lid_slider_bar`, `base_to_lid` prismatic along Y with `SLIDE_TRAVEL` |
| lid_module | lacquer_inlay | origin lid interior/exterior module | rec_picturex_0611__makeup3__001__png_d432b592bfe24d18aefa827f7ae9c15e/rev_000001 | model.py:L75-L91, model.py:L298-L338, model.py:L354-L373 | accepted | ① part tree | gold lid shell with a recessed black lacquer inlay panel on the inner face plus eight raised four-lobed `_clover_motif` ornaments on the outer face; no plaque, no mirror |
| lid_module | engraved_plaque | origin lid module | rec_picturex_0611__makeup3__002__png_4960c988351041a8a8bc5cc76140e8b6/rev_000001 | model.py:L100-L139, model.py:L142-L147, model.py:L227-L241 | accepted | ① part tree | herringbone groove field cut into the lid crown plus a real `label_recess` pocket carrying a separate `label_plaque` element in a contrasting material; no inlay, no mirror |
| lid_module | fitted_inner_mirror | forked lid module | rec_0611_makeup3_var_lid_module_fitted_inner_mirror/rev_000001 | model.py:L162-L165, model.py:L302-L359, model.py:L541-L550 | accepted | ① part tree | fitted `inner_mirror` pane in `mirror_glass` seated on the lid inner face inside the lacquer surround, checked by the `fitted inner mirror on lid inner face` assertion |
| closure | push_slide_button | origin joint/mechanism | rec_picturex_0611__makeup3__002__png_4960c988351041a8a8bc5cc76140e8b6/rev_000001 | model.py:L150-L155, model.py:L261-L281 | accepted | ② joint type | PRISMATIC `latch_button` pressed inward along +Y at the front wall, short (~1.4 mm) travel, rectangular cap; parent 001 carries the same mechanism as `base_to_clasp` with a cap+stem in a cut housing slot |
| closure | toggle_latch | forked joint/mechanism | rec_0611_makeup3_var_closure_toggle_latch/rev_000001 | model.py:L115-L151, model.py:L211-L243, model.py:L355-L377, model.py:L469-L498 | accepted | ② joint type | REVOLUTE `latch` lever: `_toggle_lever` bar + pivot boss + hook + grip, two base mounting lugs with a spanning `pivot_pin`, a lid `catch_tab`, `base_to_latch` revolute about X with `lower=0, upper=1.30` |
| powder_insert | round_metal_cup | origin + forked insert sub-assembly | rec_picturex_0611__makeup3__002__png_4960c988351041a8a8bc5cc76140e8b6/rev_000001 | model.py:L46-L63, model.py:L208-L225 | accepted | ① part tree | circular metal cup (`_powder_pan`: floor disc + annular wall) plus a flat pressed `_powder_cake` disc, retained as a FIXED `powder_insert` child of the case |
| powder_insert | petal_pressed_pan | origin insert sub-assembly | rec_picturex_0611__makeup3__001__png_d432b592bfe24d18aefa827f7ae9c15e/rev_000001 | model.py:L21-L45, model.py:L184-L205, model.py:L220-L256 | accepted | ① part tree | spline `_petal_shape` profile: narrow end toward the case centre, recessed petal well (`*_well`, shadowed) plus a smaller petal-profile pressed fill; tray surface carries matching petal openings |

## Shared (non-slotted) category anchors

Present in every accepted record, so rebuilt as shared geometry rather than slot candidates:

- Shallow open-top case body with a real cavity and a seating rim: 002 `model.py:L177-L188`
  (`_base_wall` shell + `base_floor`), 001 `model.py:L163-L182` (`base_body` with the cut
  closure housing slot), rect `model.py:L55-L75`, hex `model.py:L164-L185`.
- Cover that fully overlaps the case plan when closed: 002 `model.py:L66-L98`, 001
  `model.py:L298-L321`, asserted in every record (`closed lid covers compact body` /
  `closed lid covers the circular palette`).
- Visible pressed powder: every record keeps at least one powder cake with its own powder
  material — 002 `model.py:L214-L218`, 001 `model.py:L226-L256`, 4-well
  `model.py:L260-L284`, 2-well `model.py:L244-L253`.
- Exactly one root part (`base`) carrying every movable and retained child: 001
  `model.py:L437-L446`, 002 `model.py:L321-L333`, 4-well `model.py:L401-L410`.
- Two non-fixed mechanisms (cover + closure) in all ten records: 001 `model.py:L452-L458`,
  002 `model.py:L334-L354`, toggle `model.py:L542-L548`, slide `model.py:L465-L471`.
- Decorative rim / medallion / plaque detail is retained as surface detail only (001
  `model.py:L207-L218`, `model.py:L258-L267`; hex `model.py:L210-L224`); it is not slotted.

## Multiplicity and where the observed N values come from

- `well_count = 1 | 2 | 3 | 4`, `item_slot = powder_insert`, one `powder_pan_{i}` part per
  well with a uniform FIXED joint to the case.
- Observed N in the pool: **1** (002 `model.py:L208-L225` single `powder_insert`; round fork
  same span), **2** (2-well fork `model.py:L25-L31` `WELL_COUNT = 2` with
  `_powder_pan_2well` `model.py:L53-L67` and `_half_well_cake` `model.py:L70-L89`), **4**
  (4-well fork `model.py:L26-L35` `WELL_COUNT = 4` with `_well_pan` / `_well_cake` /
  `_well_tray` `model.py:L57-L94` and four indexed FIXED children `model.py:L260-L284`).
  `N = 3` interpolates inside the observed 1..4 span; it introduces no new geometry kind.
- **Why the counts are N and not slot candidates.** The 2-well and 4-well forks do not
  change the *kind* of insert: both keep a metal tray/cup plus pressed cake, both keep the
  uniform FIXED-to-base joint policy, and the 4-well fork explicitly factors the well into
  one shared helper pair (`_well_pan`, `_well_cake`, `model.py:L57-L76`) instantiated four
  times. That is textbook multiplicity. The 2-well fork's half-sector cakes
  (`model.py:L70-L89`) are the *same* pressed cake profile intersected with a half space to
  share one round pan — a packing consequence of N=2 inside one circular pan, not a new
  part tree. The rebuild therefore keeps one cup+cake sub-assembly per well and derives the
  pack (grid for `round_metal_cup`, radial rosette for `petal_pressed_pan`) from N.
- **What *is* a genuine insert slot.** Origin 001's petal insert
  (`_petal_shape` `model.py:L21-L45`) is a different profile family and a different
  well/fill pair (recessed shadow well plus a smaller petal fill oriented narrow-end-inward,
  `model.py:L220-L256`) from 002's circular cup+cake (`model.py:L46-L63`). Two profiles,
  two well-outline shapes, two tray-opening shapes — so `powder_insert` is a slot with two
  candidates and `well_count` multiplies whichever candidate is active.
- Spacing / capacity: the pack pitch and each well's outer size are solved from the derived
  cavity boundary, never from constants. `round_metal_cup` uses a
  `1→1×1, 2→2×1, 3→3×1, 4→2×2` grid whose pitch is maximised against the real cavity
  boundary distance; `petal_pressed_pan` uses an `N`-fold rosette at `360/N` pitch (N=1
  becomes one centred, enlarged petal pan). The case tray plate is generated with exactly
  `N` matching through-openings, so host capacity is `N` by construction.

## Parameters and derivations

- `case_span_m` (0.070–0.104 m) is the overall X span. `hx = case_span/2`; `hy = hx` (round),
  `hx·cos30°` (hexagonal), `hx·0.82` (rounded_rect, from the fork's 80/96 mm plan,
  rect `model.py:L20-L21`). Wall thickness, cavity half-extents, floor height, rim height and
  the lid plan all derive from these.
- `case_height_m` (0.0135–0.0235 m) is the rim height. Floor thickness, cavity depth, cup
  height, hinge height, closure pocket height and skirt drop derive from it.
- `lid_open_angle_rad` (1.25–1.85 rad, from 002 `model.py:L256` ≈ 1.68 rad and 001
  `model.py:L18` 1.83 rad) sets the revolute upper limit and the derived rear rim relief
  depth, so the lid's rear corner clears the rim over the whole sweep.
- `slide_travel_ratio` (0.34–0.52 of the case Y span; the fork used 0.035 m on a 0.089 m
  span ≈ 0.39, `model.py:L18`) sets the prismatic upper limit, the guide-slot length and the
  guide-post station. The band reaches 0.52 so the fully open sliding cover really uncovers
  the powder pack instead of only the front rim.
- `button_travel_m` (0.0010–0.0022 m, from 002 `model.py:L278` 0.0014 and 001
  `model.py:L418` 0.0015) sets the prismatic closure limit and the pocket depth between the
  outer flange and the inner retaining lug.
- `latch_lock_angle_rad` (1.00–1.32 rad, from the toggle fork `model.py:L495` 1.30) sets the
  revolute closure upper limit and, with the lid's engagement height, the derived lever
  length so the hook always reaches the cover edge.
- `well_fill_ratio` (0.80–0.94) is the pressed-cake height as a fraction of the cup wall
  height (002 cake 0.0054 in a 0.0060 wall ≈ 0.90, `model.py:L46-L63`).
- Cross-slot derivations. The closure publishes a **front hardware top height**; the flip
  hinge lid derives its skirt drop from it so the skirt never fouls the button cap or the
  latch lugs. The lid publishes its **front outer face** and an **engagement height**; the
  toggle latch derives its pivot stand-off and lever length from them, and the push button
  derives its pocket height to stay under the cover plane. The powder pack publishes the
  well outline set; the case derives the tray plate openings and each well's seat pocket
  footprint from it.
- Palette is a five-way colorway sampled per seed (001's polished gold / champagne family
  `model.py:L126-L161`; 002's gloss black / peach / teal family `model.py:L171-L175`; plus
  three realistic companions). It changes no geometry and is not a slot.

## Category identity and motion

- Exactly one root part `case` (role `case_body`) carrying one `lid` (role `lid`), one
  `closure` (role `closure`) and `N` `powder_pan_{i}` parts (role `powder_pan`).
- `case_to_lid` is REVOLUTE about the real rear hinge line (`flip_hinge`) or PRISMATIC along
  the real guide-slot direction (`guided_slide`). `case_to_closure` is PRISMATIC along the
  real pocket axis (`push_slide_button`) or REVOLUTE about the real front pivot pin
  (`toggle_latch`). Both revolute cases are built with `AxisInterface` + `mate_axes` and
  registered with `register_interface_mate`; the axis passes through the pin/knuckle line,
  never tangential to a visible face.
- Every powder pan is a planar mount: `PlaneInterface` with the real seat-pocket footprint on
  the cavity floor mated with `mate_planes`. The sliding lid is mated the same way onto the
  real rim footprint.
- Captured hardware, not allowances: the hinge has two case knuckles with bores, a case pin
  through the lid barrel bore with radial clearance, and a knuckle/barrel axial seat; the
  slide has two case posts with retaining heads riding in real elongated lid slots; the push
  button has an outer flange, a stem through a real wall pocket and an inner retaining lug;
  the toggle lever has a bored pivot boss on a case pin between two case lugs. No
  `ctx.allow_overlap` anywhere.

## Rejected decompositions

- **Compatibility gates (the two carried by the legacy v1 spec) are rejected outright.**
  (a) "`guided_slide` + `push_slide_button` share the -Y axis" was a layout mistake, not a
  conflict: the button lives inside the front wall entirely below the rim plane while the
  sliding cover lives entirely above it, so the two mechanisms are separated in Z and both
  build. (b) "`rounded_rect` + four wells is cavity-tight" was caused by fixed well radius
  and spacing constants (4-well fork `model.py:L26-L35`); the rebuild solves the pack
  against the real cavity boundary for every footprint and N, so the tightest combination
  still has real clearance.
- `palette_style` as a slot: rejected. The pool's colour differences are ⑥-only (001
  `model.py:L126-L161` vs 002 `model.py:L171-L175`) and would be blocked as material-only
  candidates.
- Splitting the 2-well half-sector cake into its own candidate: rejected, see the
  multiplicity section — it is the same pressed cake profile packed two-up.
- Making the outer rim / centre medallion / label plaque their own slots: rejected. They are
  surface detail shared across records (001 `model.py:L207-L267`, hex `model.py:L210-L224`),
  not interchangeable load-bearing components.
- Merging `lid_module` into `lid_motion`: rejected. The mirror fork
  (`rec_0611_makeup3_var_lid_module_fitted_inner_mirror`) changes only the lid's inner-face
  module while keeping the hinge identical, and the slide fork keeps the same inner-face
  module while changing only the joint — so they are independently observed axes and compose
  without touching host topology.
- Treating `case_form` as a decorative outline: rejected. Each footprint fork rewrites the
  wall, floor, rim, cavity, tray and lid plan and asserts its own silhouette ratio, so it is
  a primary-form slot; the lid, tray, well pack and closure pocket are host-adapted to it.
