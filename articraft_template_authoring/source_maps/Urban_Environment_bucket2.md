# Urban_Environment_bucket2 — SourceMap

source_map_schema: 1
export_category: Urban_Environment_bucket2
picture_category: Urban Environment
picture_subcategory: bucket2
category_scope: A small coopered wooden keg / barrel / pail standing on its own base: one hollow staved surface-of-revolution body with a solid wooden floor, wrapped by repeated dark metal hoop bands, closed at the top by exactly one closure mechanism (a lift-off plug lid, a hinged top hatch, or a permanent head pierced by a side bunghole and its bung plug), and optionally carrying one body- or lid-mounted carry fitting (a swing bail, a pair of pivoting side-ear rings, or a fixed arched lid grip). Excludes wheeled or trolley barrels, multi-tier stacks, spigot/tap dispensing barrels, and non-staved plastic drums.

sync_records:
  - rec_bucket2_var_bunghole_plug
  - rec_bucket2_var_hinged_lid
  - rec_bucket2_var_hoop_count
  - rec_bucket2_var_side_ear_rings
  - rec_bucket2_var_straight_keg
  - rec_bucket2_var_swing_bail
  - rec_bucket2_var_tapered_pail
  - rec_small-wooden-keg-barrel-with-staved-bulged-body-_20260608_164508_499567_ad0a147f

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_small-wooden-keg-barrel-with-staved-bulged-body-_20260608_164508_499567_ad0a147f/rev_000001 | reviewed | used | Reference-image parent. Owns the parabolic mid-bulge staved body, the recessed inner seating ledge, the flange+plug lift-off lid on a PRISMATIC +Z joint and the fixed arched grip handle. Every fork below was cut from it. |
| rec_bucket2_var_straight_keg/rev_000001 | reviewed | used | Straight-walled cylindrical staved body: `_outer_radius` collapses to a constant, so the shell profile, hoop seats and lid diameter all follow one radius. Distinct body-profile family. |
| rec_bucket2_var_tapered_pail/rev_000001 | reviewed | used | Linearly tapered pail body (mouth wider than base) with per-height hoop radii and a mouth-sized lid. Distinct body-profile family. |
| rec_bucket2_var_hoop_count/rev_000001 | reviewed | used | Parametric hoop array: `N_HOOPS` plus `_hoop_z_positions` emit index-general evenly-spaced hoop bands and one FIXED joint per band, with author checks on count, absence of an extra band and uniform spacing. The multiplicity source. |
| rec_bucket2_var_hinged_lid/rev_000001 | reviewed | used | Hinged top closure: the lid mesh is re-authored in a hinge frame at the rear rim edge and `body_to_lid` becomes REVOLUTE about a horizontal Y axis anchored on the rim contact line. Distinct closure mechanism. |
| rec_bucket2_var_bunghole_plug/rev_000001 | reviewed | used | Permanent top head plus a bored side bunghole and a tapered bung plug on a PRISMATIC radial joint; also the only record that carries no carry handle at all. Distinct closure mechanism and the evidence for a bare no-handle keg. |
| rec_bucket2_var_side_ear_rings/rev_000001 | reviewed | used | Two metal ear brackets with forked pivot prongs, each carrying a REVOLUTE drop ring that folds against the stave face or swings outward. Distinct carry-fitting mechanism (two joints). |
| rec_bucket2_var_swing_bail/rev_000001 | reviewed | used | Two pivot ears on opposite stave faces and one arched wire bail spanning them on a single REVOLUTE horizontal axis, swinging from resting-at-the-side to overhead; the top mouth is closed by a fixed head. Distinct carry-fitting mechanism (one joint). |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| body_profile | bulged_stave | staved barrel body | rec_small-wooden-keg-barrel-with-staved-bulged-body-_20260608_164508_499567_ad0a147f/rev_000001 | L72-L75, L78-L113, L116-L133 | structure | `_outer_radius` is a symmetric parabolic mid-bulge; `_build_body_mesh` revolves that profile into a hollow shell with a solid floor and carves N vertical stave seam grooves; `_build_rim_mesh` adds the recessed inner seating ledge. |
| body_profile | straight_stave | staved barrel body | rec_bucket2_var_straight_keg/rev_000001 | L71-L73, L76-L113, L341-L361 | structure | `_outer_radius` returns the constant `R_BODY`, so `_build_body_mesh` revolves a straight two-point outer wall; the author test proves the radius spread over the height is zero (no mid-bulge). |
| body_profile | tapered_pail | staved pail body | rec_bucket2_var_tapered_pail/rev_000001 | L73-L76, L79-L115, L332-L344 | structure | `_outer_radius` interpolates linearly from `R_BASE` to a wider `R_MOUTH`; the shell, the per-height hoop radii and the lid diameter all follow the taper, and the author test asserts monotone widening toward the mouth. |
| hoop_band | flat_iron_band | metal hoop band | rec_bucket2_var_hoop_count/rev_000001 | L79-L87, L148-L164, L234-L246 | structure | `_hoop_z_positions` spaces N band centres evenly between margins and `_build_hoop_mesh` revolves a rectangular band section that bites into the wood and stands proud; `build_object_model` emits the whole array from one index-general loop. |
| closure | slide_off_lid | top closure | rec_small-wooden-keg-barrel-with-staved-bulged-body-_20260608_164508_499567_ad0a147f/rev_000001 | L155-L178, L239-L249, L276-L286 | structure+motion | `_build_lid_mesh` unions a flange disk with a downward plug that nests into the recessed mouth; `body_to_lid` is PRISMATIC about +Z with the joint frame on the mouth plane so q=0 seats the lid. |
| closure | hinged_lid | top closure | rec_bucket2_var_hinged_lid/rev_000001 | L74-L77, L163-L192, L295-L307 | structure+motion | The lid mesh is authored in a hinge frame whose origin is the rear (-X) rim edge; `body_to_lid` becomes REVOLUTE about a horizontal Y axis anchored on the rim contact line and swings the lid up instead of lifting it. |
| closure | bung_plug | top closure and side bung | rec_bucket2_var_bunghole_plug/rev_000001 | L81-L121, L124-L135, L157-L174, L230-L244 | structure+motion | `_build_body_mesh` bores a radial bunghole through the stave wall, `_build_head_mesh` closes the mouth with a permanent head, `_build_bung_mesh` is a tapered plug and `body_to_bung` is PRISMATIC along the outward radial direction. |
| handle | swing_bail | carry fitting | rec_bucket2_var_swing_bail/rev_000001 | L163-L180, L183-L216, L267-L291, L327-L343 | structure+motion | `_build_ear_mesh` gives each pivot ear a plate and a protruding pin, `_build_bail_mesh` sweeps the arched wire between the two pins, and `body_to_bail` is a single REVOLUTE about the horizontal pivot line from resting-at-the-side to overhead. |
| handle | side_ear_rings | carry fitting | rec_bucket2_var_side_ear_rings/rev_000001 | L166-L194, L197-L218, L265-L308 | structure+motion | `_build_ear_mesh` is a forked bracket with two prongs and a pivot gap, `_build_ring_mesh` is a torus hanging from that pivot, and the `for i in range(2)` loop emits two independent REVOLUTE ring joints on opposite stave faces. |
| handle | arched_grip | carry fitting | rec_small-wooden-keg-barrel-with-staved-bulged-body-_20260608_164508_499567_ad0a147f/rev_000001 | L181-L201, L251-L258, L288-L296 | structure | `_build_handle_mesh` builds a squared arch of two feet and a crossbar seated into the closure top, emitted as its own part and welded on with the FIXED `lid_to_handle` joint, so it rides the closure instead of articulating. |
| handle | no_handle | carry fitting | rec_bucket2_var_bunghole_plug/rev_000001 | L177-L246 | structure | `build_object_model` emits only body, head, hoops and bung: the bare keg with no ear, bail, ring or grip part and no carry joint at all. |
