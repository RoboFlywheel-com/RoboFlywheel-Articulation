# Overhead projector with articulating mirror — SourceMap

export_category: overhead_projector_with_articulating_mirror

Authoritative records live under `data/records` of the `articraft_data` repo
(`<ARTI_SKILL_ROOT>/articraft_data/data/records`). The category is a
grounded low box housing carrying a glass stage, from which a vertical mast rises
to an optical head, with a mirror articulating above the head. Four independent
mechanisms are present in every seed: a mast height slide, an optical-head motion,
one or two mirror hinges, and two body-mounted controls (a rocker and a knob).

Source pool: **11 record dirs — 1 picture origin and 10 forked variants. All 11
were read in full before any candidate was chosen.** The origin was read line by
line. Every variant is a byte-level fork of that single origin, so each was read
as a full unified diff (`diff -u origin variant`): every changed line reviewed,
the unchanged remainder identical to a file already read line by line.

| Variant | Changed lines |
|---|---|
| `head_form_round_lamp_head` | 54 |
| `post_topology_folding_cantilever_mast` | 63 |
| `head_form_rectangular_enclosed_hood` | 65 |
| `post_topology_single_telescoping_mast` | 69 |
| `focus_sliding_lens_barrel_focus` | 87 |
| `post_topology_twin_column_mast` | 90 |
| `mirror_motion_fold_flat_mirror` | 114 |
| `focus_rack_and_pinion_head_focus` | 126 |
| `mirror_motion_swiveling_mirror_yoke` | 128 |
| `mirror_motion_dual_hinge_mirror` | 188 |

Frame convention for the rebuild: `+Z` is up, the housing sits on the ground at
`z=0`, `−Y` is the operator/front side (the rocker and lamp access panel are on
`−Y`), and the mast rises at `+X, +Y` (the rear-right corner). The **mast slide
and every yoke swivel are on `(0,0,1)`; every head and mirror tilt is on
`(0,1,0)`; both body controls are on `(1,0,0)`.** No joint in the pool uses any
other axis.

sync_records:
  - rec_picturex_0611__overhead_projector_with_articulating_mirror__001__png_05cea393e58442418c6e510b3f7de420
  - rec_0611_overhead_projector_with_articu_var_post_topology_single_telescoping_mast
  - rec_0611_overhead_projector_with_articu_var_post_topology_twin_column_mast
  - rec_0611_overhead_projector_with_articu_var_post_topology_folding_cantilever_mast
  - rec_0611_overhead_projector_with_articu_var_head_form_round_lamp_head
  - rec_0611_overhead_projector_with_articu_var_head_form_rectangular_enclosed_hood
  - rec_0611_overhead_projector_with_articu_var_focus_sliding_lens_barrel_focus
  - rec_0611_overhead_projector_with_articu_var_focus_rack_and_pinion_head_focus
  - rec_0611_overhead_projector_with_articu_var_mirror_motion_fold_flat_mirror
  - rec_0611_overhead_projector_with_articu_var_mirror_motion_swiveling_mirror_yoke
  - rec_0611_overhead_projector_with_articu_var_mirror_motion_dual_hinge_mirror

## Component slots and candidates

Paths below are relative to `data/records/<record>/revisions/rev_000001/model.py`.
The origin record is abbreviated `…__001__…`; variants by their `var_` suffix.

### Slot A — `post_topology` (mast + its sleeve; ① part tree + section)

| Candidate | Record | Exact span | Key construction | Host adaptation it forces |
|---|---|---|---|---|
| `round_telescoping_post` | `…__001__…` | L46-L49 (sleeve), L204-L234 (post), joint L236-L245 | Round tube sleeve `circle(0.014)` extruded 0.200 with a `circle(0.0097)` bore; inner post `Cylinder(r=0.0085, len=0.380)`, `stop_collar` `Cylinder(r=0.014, len=0.008)`, `head_crossbar` 0.050×0.070×0.012, two 0.035×0.008×0.050 forks | none — the baseline stage frame is untouched |
| `single_telescoping_mast` | `…_var_post_topology_single_telescoping_mast` | L54-L66 (sleeve), L69-L75 (mast), L78-L84 (collar) | **Rectangular** closed section: sleeve outer box 0.034×0.028×0.200 minus a 0.026×0.020×0.204 bore; mast a 0.024×0.018×0.410 box; collar an interference split clamp (0.038×0.032×0.008 minus 0.0235×0.0175) | **The stage frame grows a `mast_land`** 0.060×0.052×0.008 at `(0.170, 0.115)` (L46-L52), and the bracket grows 0.040×0.056×0.076 → 0.050×0.060×0.082. The comment states the intent: transfer mast load into the stage surround rather than hanging the sleeve off the shell |
| `twin_column_mast` | `…_var_post_topology_twin_column_mast` | L52-L81 (paired sleeve), L84-L102 (twin post) | Two `circle(0.014)` columns at `y = ∓0.018` **welded by a 0.028×0.036×0.200 web**, then two `circle(0.0097)` bores cut through; the post is two `circle(0.0085)` columns joined by a 0.026×0.054×0.016 `upper_bridge` | **The stage frame is RELIEVED, not built up** — a 0.026×0.086×0.014 `mast_relief` is *cut* at `(0.151, 0.105)` (L44-L50). Bracket Y 0.056→0.082, collar → 0.030×0.064, crossbar Y 0.070→0.078. Author test L573-L590 asserts all three widths |
| `folding_cantilever_mast` | `…_var_post_topology_folding_cantilever_mast` | L53-L64 (sleeve), L216-L245 (post) | Rect sleeve 0.036×0.030 minus a 0.024×0.018 bore; mast a 0.022×0.016×0.390 box; the crossbar is replaced by a **`cantilever_beam` 0.095×0.070×0.016 offset to `x=−0.036`**, and the forks move to `x=−0.070` | Stage frame grows a `mast_landing` 0.060×0.066×0.008 at `(0.165, 0.107)` (L45-L51). **The head joint origin moves with the beam**: `head_tilt` origin `(0,0,0.255)` → `(−0.070, 0, 0.255)` (L332-L341). This is a genuine cross-slot binding, not a cosmetic offset |

### Slot B — `head_form` (optical head shell + arm; ③ form family)

| Candidate | Record | Exact span | Key construction | Host adaptation it forces |
|---|---|---|---|---|
| `open_barrel_head` | `…__001__…` | L247-L288 | Spline arm `tube_from_spline_points` over 4 control points, `radius=0.013`; shell `Cylinder(r=0.034, len=0.050)`, `lens_ring` r 0.030, `projection_lens` r 0.025 | baseline: drum `len=0.052`, forks at `y=∓0.030` |
| `round_lamp_head` | `…_var_head_form_round_lamp_head` | L52-L73 (shell), L241-L253 (crossbar/forks), L278-L296 (arm) | An **8-point profile revolved 360°** in the XZ plane (radii 0→0.058, z −0.018→0.066) with a `circle(0.029)` lens throat *cut* through — a real domed crown with an open throat, not a capped cylinder. Arm re-routed and thinned to `radius=0.012` | Crossbar becomes a `Cylinder(r=0.012, len=0.070)` rotated about X; forks 0.035→0.030 wide, 0.050→0.054 tall |
| `rectangular_enclosed_hood` | `…_var_head_form_rectangular_enclosed_hood` | L52-L57 (arm), L59-L63 (hood), L229-L246 (crossbar/forks) | The spline tube is replaced by **folded sheet-metal CAD**: a 0.220×0.032×0.034 main beam unioned with a 0.060×0.092×0.034 offset neck. The hood is a 0.125×0.115×0.074 box with a `circle(0.0295)` lens well cut into the underside | **Drum `len` 0.052→0.060, forks move to `y=∓0.034`, crossbar Y 0.070→0.078.** The head's own pivot width drives the post's fork spacing — see mating rule 2 |

### Slot C — `focus` (what the head-to-post joint actually is; ② joint type)

| Candidate | Record | Exact span | Joint | Key construction |
|---|---|---|---|---|
| `folding_tilt` | `…__001__…` | L320-L329 | **REVOLUTE** `(0,1,0)`, `lower=−0.20 upper=1.25`, effort 20 | The head folds up about a horizontal axis; the `pivot_drum` is captured between two short forks |
| `sliding_lens_barrel` | `…_var_focus_sliding_lens_barrel_focus` | L52-L57, L59-L64, L237-L247, joint L334-L344 | **PRISMATIC** `(0,0,1)`, `lower=−0.018 upper=0.055`, effort 35 | The forks lengthen 0.050 → **0.140** and rise to `z=0.280` so they become slide rails; the drum thins r 0.021→0.015; the head shell becomes a genuinely **open barrel** (`circle(0.036)` minus `circle(0.0305)`) and the lens ring a real retaining ring (`circle(0.032)` minus `circle(0.0245)`) whose shoulder captures the lens edge |
| `rack_and_pinion` | `…_var_focus_rack_and_pinion_head_focus` | L53-L64 (rack), L66-L76 (guides), L268-L296 (carriage), joint L363-L373 | **PRISMATIC** `(0,0,1)`, `lower=−0.055 upper=0.055`, effort 35 | The crossbar becomes a **190 mm rack with 22 teeth at 8 mm pitch** (0.009×0.024×0.0045 each, unioned onto a 0.012×0.054×0.190 bar); both forks become 190 mm guide cheeks with a `circle(0.0055)` shaft passage **cut** through (§7 — the moving shaft gets a real bore, not a notch). The head gains a 0.030×0.044×0.068 carriage, a real `SpurGear(module=0.002, teeth_number=18, width=0.014, bore_d=0.006)` pinion, a 0.078 shaft and an r 0.018 knob |

Every `focus` candidate re-derives the post's fork/rail geometry. This slot and
Slot A both write into `lift_post`, so their host adaptations must compose.

### Slot D — `mirror_motion` (hinge topology; ② joint count + part tree)

| Candidate | Record | Exact span | Joints on the mirror chain | Key construction |
|---|---|---|---|---|
| `head_carried_yoke` | `…__001__…` | L290-L318 (yoke), L331-L367 (mirror + joint) | 1 (`mirror_tilt`, REVOLUTE `(0,1,0)`, −0.40…0.55) | Two spline yoke tubes rise from the head at `y = −0.120→−0.150` and `−0.060→−0.030`, ending in `Sphere(0.005)` sockets at `z=0.130`; the mirror carries matching `Sphere(0.005)` bosses at `y=∓0.050`. The mirror plate is mounted with an internal `rpy=(0,−0.65,0)` so `q=0` is the deployed optical angle |
| `fold_flat_mirror` | `…_var_mirror_motion_fold_flat_mirror` | L46-L56 (frame), L347-L373 (mirror), joint L375-L387 | 1 | The mirror becomes a **perimeter frame** (0.148×0.116×0.005 minus a 0.132×0.100 opening) translated so its **hinge edge is at local `x=0`** and the whole panel lies to one side of the axis — that is what lets it rotate truly flat. The rest angle moves into the joint (`rpy=(0,−0.72,0)`) instead of into the visual; limits −0.18…0.72. Author test asserts folded Z extent < 0.015 m vs deployed > 0.075 m |
| `swiveling_mirror_yoke` | `…_var_mirror_motion_swiveling_mirror_yoke` | L286-L294 (head boss), L309-L337 (yoke part), L339-L348 (swivel), L377-L387 (tilt) | 2 (`yoke_swivel` REVOLUTE `(0,0,1)`, ±0.45; then `mirror_tilt`) | The yoke leaves the head and becomes **its own part** on a turntable: head keeps only a `yoke_mount` boss `Cylinder(r=0.012, len=0.016)`; the yoke has an r 0.018 turntable, a 0.026×0.132×0.012 crossbar, two 0.012×0.012×0.072 uprights and two `Cylinder(r=0.007, len=0.008)` trunnion sockets |
| `dual_hinge_mirror` | `…_var_mirror_motion_dual_hinge_mirror` | L304-L346 (yoke part), L348-L357 (swivel), L386-L396 (tilt) | 2 (`yoke_swivel` REVOLUTE `(0,0,1)`, ±0.60; then `mirror_tilt`) | Same two-axis idea with a taller carrier: swivel pin, 0.018×0.018×0.050 neck, 0.018×0.118×0.014 bridge, two cheeks and two `Cylinder(r=0.008, len=0.012)` sockets, mounted lower on the head (`z=0.043`) so the mirror sits on a real column rather than a low turntable |

## Mating mechanisms (sampled across all 11 records)

Per `MECHANICAL_PRIORS.md` §1b these were extracted across the whole pool, not one
representative per candidate. Every number below is a *derivation*, and the
derivations are what the rebuild must reproduce.

**1. Mast retention is a two-pose rule, not a single fit.**
Origin L46-L49 / L204-L245: sleeve bore r 0.0097 vs post r 0.0085 → **1.2 mm radial
clearance**, checked by `expect_within(inner_post ⊂ post_sleeve, axes="xy",
margin=0.0)`. Sleeve spans world z 0.155…0.355 (length 0.200); the post spans
0.195…0.575. Insertion at rest = **0.160 m**, asserted `min_overlap=0.150`; at the
`upper=0.080` stroke it drops to **0.080 m**, asserted `min_overlap=0.075` *inside a
posed block* (L595-L605). So the real constraint is
`sleeve_length − stroke ≥ 0.075`, and stroke and sleeve length can never be
parameterised independently.

**2. Fork spacing is derived from the head's pivot drum — exactly, in every record.**

| Record | `pivot_drum` length | fork `y` | fork thickness | fork inner face | crossbar Y |
|---|---|---|---|---|---|
| origin | 0.052 | ∓0.030 | 0.008 | ∓0.026 | 0.070 |
| `round_lamp_head` | 0.052 | ∓0.030 | 0.008 | ∓0.026 | 0.070 (now a cylinder) |
| `rectangular_enclosed_hood` | 0.060 | ∓0.034 | 0.008 | ∓0.030 | 0.078 |
| `sliding_lens_barrel` | 0.052 (r 0.015) | ∓0.030 | 0.008 | ∓0.026 | 0.070 |
| `twin_column_mast` | 0.052 | ∓0.030 | 0.008 | ∓0.026 | 0.078 (widened for the mast) |

The rule holds without exception: **`fork_y = drum_length/2 + fork_thickness/2`**,
so the drum's end faces land exactly on the forks' inner faces (`expect_contact`,
`contact_tol=0.0015`), and **`crossbar_Y ≥ 2·(fork_y + fork_thickness/2)`**. The
`rectangular_enclosed_hood` row is the proof that this is a live binding: widening
the hood widened the drum, which moved the forks, which widened the crossbar.

**3. Mirror trunnions are tangent, never coincident — and two records get this wrong.**
The origin puts `Sphere(0.005)` bosses at `y=∓0.050` in the mirror frame (world
`−0.140`, `−0.040`) against `Sphere(0.005)` sockets at world `−0.150`, `−0.030`:
centre distance exactly **0.010 = r_boss + r_socket**, i.e. *tangent, zero overlap*.
`swiveling_mirror_yoke` does the same with cylinders — sockets `r 0.007, len 0.008`
at `y=∓0.064` span `|y| ∈ [0.060, 0.068]`, bosses `r 0.0055, len 0.010` at `∓0.055`
span `[0.050, 0.060]`, so the end faces meet at `|y| = 0.060`. **This tangent
construction is the one the rebuild adopts for all four candidates.**

**4. Every other contact in the pool is a derived face landing.**
* `stop_collar` r 0.014 = sleeve outer r, bottom at world 0.355 + 0.004 − 0.004 =
  **0.355 = sleeve top**.
* `switch_bezel` top = 0.1685 + 0.0015 = **0.170** = the `switch_rock` joint origin
  z, and the rocker is extruded from that plane (`local z=+0.004`, height 0.008).
* `lock_shaft` (r 0.005, len 0.018, X axis at x 0.205) ends at **x = 0.214** =
  the `lock_knob_turn` joint origin x, and `knob_body` starts there. When the
  single-mast variant thickens the bracket, *both* move together, 0.205→0.207 and
  0.214→0.216 (L224, L437). Nothing is authored twice.
* `swiveling_mirror_yoke`: turntable bottom at joint origin z 0.059 = `yoke_mount`
  top (0.051 + 0.016/2). Same pattern.

**5. Stage-frame host adaptation goes in both directions.**
`single_telescoping_mast` and `folding_cantilever_mast` **union a land** onto the
stage frame; `twin_column_mast` **cuts a relief** out of it. Both are local
adaptations of an unchanged square host, which is exactly the pattern
`AUTHORING.md` §4 asks for. The rebuild derives land-or-relief and its footprint
from the mast section rather than hard-coding one of the two.

**6. Scale and effort.**
Housing 0.360×0.350 × ~0.18 m tall on 4 feet; stage glass 0.288×0.258 m; total
height with mast ~0.68 m. Effort: mast slide 120, focus slide 35, head tilt 20,
yoke swivel 4–6, mirror tilt 5, knob 3, rocker 2. Effort clearly tracks the mass
each joint carries — a single constant cannot drive both the mast and the rocker.
The author test `mirror[0][2] > stage_top + 0.42` fixes the whole vertical stack-up
and is worth keeping as an anchor.

## `allow_overlap` sites — must not be reproduced

`preflight` **blocks `ctx.allow_overlap` outright** for Design-backed templates
(AUTHORING.md §5). Two records use it, and both use it to paper over a construction
the pool elsewhere gets right:

| Record | Sites | What it hides | Rebuild instead |
|---|---|---|---|
| `mirror_motion_fold_flat_mirror` | 4 (L599, L606, L629, L636) | Mirror hinge bosses moved to `y=∓0.060`, landing on socket centres at world `∓0.150 / ∓0.030` — coincident, not tangent | Tangent trunnions per mating rule 3 |
| `mirror_motion_dual_hinge_mirror` | 5 (L460, L467, L474, L481, L488) | Swivel pin driven into the head arm, and mirror trunnions driven through both yoke cheeks and into the socket bores | Tangent trunnion faces; weld the swivel pin's seat into the head as one solid (intra-part embedding is free, §1c) |

The remaining 9 records — including `swiveling_mirror_yoke`, which builds the same
two-axis mechanism — use **zero** allowances of either kind. `allow_isolated_part`
is not used anywhere in this pool and should not be needed: every moving member
here has a real seated contact.

## Deliberate deviations from source construction

1. **Graduation-free, but visual-count aware.** The body part emits ~20 separate
   primitive visuals in the origin (housing, lamp housing, access panel + pull,
   stage frame, fresnel + 2 marks, vent, 4 feet, grommet, cable, bracket, sleeve,
   lock shaft, bezel). Since `sdk/_core/v0/exact_collisions.py` derives one
   collision per visual 1:1, the rebuild welds the structurally-inert dressing
   (access panel + pull, fresnel marks, bezel, feet) into the housing CAD solid
   and keeps separate visuals only where a distinct material is load-bearing for
   recognizability (glass stage, vent, cable). This preserves every visible
   feature while cutting the body from ~20 collision solids to ~6.
2. **Mirror rest angle lives in the joint, not the visual.** The origin bakes
   `rpy=(0,−0.65,0)` into two mirror visuals (L335, L341); `fold_flat_mirror`
   moves it into the joint origin (L378). The rebuild uses the joint, because a
   parameterised mirror angle must re-derive the fold-flat limit with it.

## Multiplicity

**This category has no multiplicity axis, and none is invented.** No record
contains a repeated structural member under a count parameter. The four rubber
feet are a fixed decorative count (they contribute to neither `core_domain` nor
`raw_domain` per `VISUAL_DIVERSITY_MODEL.md`), and the 22 rack teeth and 18 pinion
teeth are internal to a single candidate's geometry, not a slot. `raw_domain`
therefore equals `core_domain` = 4 × 3 × 3 × 4 = **144 combinations**.

## Folded into parameters rather than candidates

* Mast **stroke** (0.080 m in every record) and **sleeve length** (0.200 m in every
  record) become coupled independent parameters, bounded by mating rule 1.
* Head **arm reach** — the spline end point moves `(−0.250,−0.090,0.045)` →
  `(−0.235,−0.082,0.060)` between the origin and `round_lamp_head`, and the CAD
  arm reaches −0.250 in the hood variant. Pure proportion, so it is a continuous
  parameter (`head_reach`, 0.235–0.250 m) shared by all three head candidates.
* Mirror **panel size** 0.140×0.100 → 0.148×0.116. Proportion only.

## Category anchors

1. **One root `projector_body`** carrying the glass stage; it is the only grounded
   part. Every record asserts `len(root_parts()) == 1`.
2. **Exactly one PRISMATIC mast joint** `(0,0,1)`, body → mast, whose travel keeps
   at least 0.075 m of insertion at full extension.
3. **Exactly one head joint**, mast → head. Its type is the `focus` candidate:
   REVOLUTE `(0,1,0)` for `folding_tilt`, PRISMATIC `(0,0,1)` for the two focus
   slides. Nothing else in the category changes joint type.
4. **A mirror on a `(0,1,0)` tilt**, plus — for the two-axis candidates — a
   `(0,0,1)` yoke swivel between it and the head. The chain is strictly
   body → mast → head → [yoke] → mirror.
5. **Two body-mounted controls on `(1,0,0)`**: a bounded REVOLUTE rocker and a
   CONTINUOUS knob, both seated on real body features (bezel, shaft).
6. **The mirror clears the stage by ≥ 0.42 m** in the deployed pose — the
   projection geometry is what makes the object readable as an overhead projector
   rather than a lamp.
7. **The stage is a bordered frame around a translucent plate**, and the mast's
   footprint is reconciled with that frame by a land or a relief, never by
   floating the sleeve.

## Review ledger

All 11 records were opened and read before deciding what each contributes.

| Record | Depth | Verdict |
|---|---|---|
| `…__001__…` | full | **Candidate ×4**: baseline for every slot, and the source of all six mating derivations. The only record in the pool that is not a fork |
| `post_topology_single_telescoping_mast` | full diff | **Candidate**: rectangular closed-section mast; supplies the *build-up* stage-frame land |
| `post_topology_twin_column_mast` | full diff | **Candidate**: paired columns with a welded web; supplies the *relief-cut* stage-frame adaptation and the bracket/collar/crossbar width chain |
| `post_topology_folding_cantilever_mast` | full diff | **Candidate**: offset beam; the only record where the head joint origin itself moves with the mast candidate |
| `head_form_round_lamp_head` | full diff | **Candidate**: revolved profile with a cut lens throat; also the second data point for `head_reach` |
| `head_form_rectangular_enclosed_hood` | full diff | **Candidate**: CAD folded-sheet arm + boxed hood; **proves the drum→fork→crossbar binding is live** |
| `focus_sliding_lens_barrel_focus` | full diff | **Candidate**: REVOLUTE→PRISMATIC change with forks re-purposed as 140 mm slide rails; open-barrel shell and a real lens retaining ring |
| `focus_rack_and_pinion_head_focus` | full diff | **Candidate**: the pool's only geared mechanism (`SpurGear`), a 22-tooth rack, and guide cheeks with a **cut** shaft passage |
| `mirror_motion_swiveling_mirror_yoke` | full diff | **Candidate**: two-axis mirror on a turntable, built with **zero allowances** — the construction the other two-axis record should have used |
| `mirror_motion_dual_hinge_mirror` | full diff | **Candidate** for the tall-column yoke silhouette, but its 5 `allow_overlap` calls are rejected; rebuild uses the tangent construction |
| `mirror_motion_fold_flat_mirror` | full diff | **Candidate** for the frame-form panel with its hinge edge on the local origin — the idea is right and the storage pose is real; its 4 `allow_overlap` calls are rejected |

**What the ledger changed.** Reading only one representative per candidate would
have taken the origin's mirror hinge and both two-axis variants' `allow_overlap`
construction at face value. It was `swiveling_mirror_yoke` — a record that could
have been skipped as "another two-axis yoke" — that showed the same mechanism
built with tangent faces and no allowance at all. Likewise the drum→fork→crossbar
rule is invisible in any single record; it only appears once the same three
numbers are tabulated across five.

## Accepted candidate manifest (machine-readable)

The per-slot tables above are the human-readable evidence. This table is the same
set in the column layout `agent/source_maps.py` parses for `design-init`.

| slot | candidate | diversity axis | source type | record/revision | exact model.py:Lx-Ly | key parts/joints/helpers | status |
|---|---|---|---|---|---|---|---|
| post_topology | round_telescoping_post | ① part tree / mast section | mast | rec_picturex_0611__overhead_projector_with_articulating_mirror__001__png_05cea393e58442418c6e510b3f7de420/rev_000001 | model.py:L46-L49, model.py:L204-L245 | lift_post, inner_post, stop_collar, head_crossbar, head_fork_0, head_fork_1, post_sleeve, post_bracket, height_adjust, _post_sleeve_shape | accepted |
| post_topology | single_telescoping_mast | ① part tree / mast section | mast | rec_0611_overhead_projector_with_articu_var_post_topology_single_telescoping_mast/rev_000001 | model.py:L54-L66, model.py:L69-L84, model.py:L44-L52 | _post_sleeve_shape, _lift_mast_shape, _mast_collar_shape, mast_land, _stage_frame_shape, post_bracket, inner_post, stop_collar | accepted |
| post_topology | twin_column_mast | ① part tree / mast section | mast | rec_0611_overhead_projector_with_articu_var_post_topology_twin_column_mast/rev_000001 | model.py:L52-L81, model.py:L84-L102, model.py:L42-L50 | _post_sleeve_shape, _twin_lift_post_shape, mast_relief, upper_bridge, post_bracket, stop_collar, head_crossbar | accepted |
| post_topology | folding_cantilever_mast | ① part tree / mast section | mast | rec_0611_overhead_projector_with_articu_var_post_topology_folding_cantilever_mast/rev_000001 | model.py:L53-L64, model.py:L216-L245, model.py:L332-L341 | _post_sleeve_shape, mast_landing, cantilever_beam, head_fork_0, head_fork_1, head_tilt, inner_post | accepted |
| head_form | open_barrel_head | ③ form family | optical head | rec_picturex_0611__overhead_projector_with_articulating_mirror__001__png_05cea393e58442418c6e510b3f7de420/rev_000001 | model.py:L247-L288 | projection_head, pivot_drum, head_arm, projection_head_shell, lens_ring, projection_lens, tube_from_spline_points | accepted |
| head_form | round_lamp_head | ③ form family | optical head | rec_0611_overhead_projector_with_articu_var_head_form_round_lamp_head/rev_000001 | model.py:L52-L73, model.py:L241-L253, model.py:L278-L296 | _round_lamp_head_shape, lens_throat, projection_head_shell, head_crossbar, head_fork_0, head_fork_1, head_arm | accepted |
| head_form | rectangular_enclosed_hood | ③ form family | optical head | rec_0611_overhead_projector_with_articu_var_head_form_rectangular_enclosed_hood/rev_000001 | model.py:L52-L63, model.py:L229-L246, model.py:L260-L290 | _rectangular_head_arm_shape, _rectangular_head_hood_shape, main_beam, offset_neck, lens_well, pivot_drum, head_fork_0, head_fork_1, head_crossbar | accepted |
| focus | folding_tilt | ② joint type | head motion | rec_picturex_0611__overhead_projector_with_articulating_mirror__001__png_05cea393e58442418c6e510b3f7de420/rev_000001 | model.py:L320-L329 | head_tilt, projection_head, lift_post, pivot_drum, head_fork_0, head_fork_1 | accepted |
| focus | sliding_lens_barrel | ② joint type | head motion | rec_0611_overhead_projector_with_articu_var_focus_sliding_lens_barrel_focus/rev_000001 | model.py:L52-L64, model.py:L237-L247, model.py:L334-L344 | head_tilt, _projection_head_shell_shape, _lens_ring_shape, head_fork_0, head_fork_1, pivot_drum, projection_head_shell, lens_ring | accepted |
| focus | rack_and_pinion | ② joint type | head motion | rec_0611_overhead_projector_with_articu_var_focus_rack_and_pinion_head_focus/rev_000001 | model.py:L53-L76, model.py:L268-L296, model.py:L363-L373 | head_tilt, _focus_rack_shape, _focus_guide_shape, focus_carriage, focus_pinion, focus_shaft, focus_knob, SpurGear, head_crossbar, head_fork_0, head_fork_1 | accepted |
| mirror_motion | head_carried_yoke | ② joint count / hinge topology | mirror hinge | rec_picturex_0611__overhead_projector_with_articulating_mirror__001__png_05cea393e58442418c6e510b3f7de420/rev_000001 | model.py:L290-L318, model.py:L331-L367 | mirror, mirror_backing, mirror_face, pivot_boss_0, pivot_boss_1, mirror_yoke_0, mirror_yoke_1, yoke_socket_0, yoke_socket_1, mirror_tilt | accepted |
| mirror_motion | fold_flat_mirror | ② joint count / hinge topology | mirror hinge | rec_0611_overhead_projector_with_articu_var_mirror_motion_fold_flat_mirror/rev_000001 | model.py:L46-L56, model.py:L347-L387 | _fold_flat_mirror_frame_shape, mirror_backing, mirror_face, pivot_boss_0, pivot_boss_1, mirror_tilt | accepted |
| mirror_motion | swiveling_mirror_yoke | ② joint count / hinge topology | mirror hinge | rec_0611_overhead_projector_with_articu_var_mirror_motion_swiveling_mirror_yoke/rev_000001 | model.py:L286-L294, model.py:L309-L348, model.py:L377-L387 | mirror_yoke, yoke_turntable, yoke_crossbar, mirror_yoke_0, mirror_yoke_1, yoke_socket_0, yoke_socket_1, yoke_mount, yoke_swivel, mirror_tilt | accepted |
| mirror_motion | dual_hinge_mirror | ② joint count / hinge topology | mirror hinge | rec_0611_overhead_projector_with_articu_var_mirror_motion_dual_hinge_mirror/rev_000001 | model.py:L304-L357, model.py:L386-L396 | mirror_yoke, swivel_pin, yoke_neck, yoke_bridge, yoke_arm_0, yoke_arm_1, yoke_socket_0, yoke_socket_1, yoke_swivel, mirror_tilt | accepted |
| body_controls | rocker_and_lock_knob | ② joint type | fixed shared controls | rec_picturex_0611__overhead_projector_with_articulating_mirror__001__png_05cea393e58442418c6e510b3f7de420/rev_000001 | model.py:L369-L409 | power_switch, blue_rocker, switch_rock, lock_knob, knob_body, knob_grip, lock_knob_turn, switch_bezel, lock_shaft | accepted |
