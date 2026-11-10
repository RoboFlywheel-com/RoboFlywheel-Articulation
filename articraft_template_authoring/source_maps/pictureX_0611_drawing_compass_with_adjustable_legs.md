# pictureX_0611_drawing_compass_with_adjustable_legs — SourceMap

source_map_schema: 1
export_category: pictureX_0611_drawing_compass_with_adjustable_legs
picture_category: 0611
picture_subcategory: drawing_compass_with_adjustable_legs
category_scope: A hand drawing compass — one head/pivot hub carrying exactly two legs on a shared transverse hinge axis, a radius-setting adjuster spanning the head or the two legs, a needle point on one leg and a lead/pen holder on the other, plus a top handle. Dividers with no lead holder, beam compasses with no head hinge, and protractors/rulers are outside this host.

sync_records:
  - rec_drawing_compass_var_bow_spring_head
  - rec_drawing_compass_var_center_point_collet_20260714
  - rec_drawing_compass_var_extension_bar_radius
  - rec_drawing_compass_var_folding_lower_legs_20260714
  - rec_drawing_compass_var_hinged_pen_adapter_20260714
  - rec_drawing_compass_var_lead_cartridge
  - rec_drawing_compass_var_quick_set_center_wheel
  - rec_drawing_compass_var_rack_pinion_head_20260714
  - rec_drawing_compass_var_ratchet_quadrant_lock_20260714
  - rec_drawing_compass_var_side_spindle_adjuster_20260714
  - rec_drawing_compass_var_tubular_legs_20260714
  - rec_picturex_0611__drawing_compass_with_adjustable_legs__001__png__airflex_batch_20260710_68de3d909b2143c5a9bd0ba516a4d072
  - rec_picturex_0611__drawing_compass_with_adjustable_legs__002__png__airflex_batch_20260710_3559da21872945b8bdb7caba02a48c14
  - rec_picturex_0611__drawing_compass_with_adjustable_legs__003__png__airflex_batch_20260710_2d7c021809004b9f99791a92647edf13
  - rec_picturex_0611__drawing_compass_with_adjustable_legs__004__png__airflex_batch_20260710_1dfc7a8e26e24466a8a1f62fd5cfc736

All records are read at `revisions/rev_000001/model.py`.

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_drawing_compass_var_bow_spring_head/rev_000001 | reviewed | used | Replaces the ring head with a curved bow-spring arch plus a tapered structural spine, and moves the adjuster to a vertical spreader screw rooted in the head. Two distinct components. |
| rec_drawing_compass_var_center_point_collet_20260714/rev_000001 | reviewed | used | Adds a real needle cartridge on a PRISMATIC insertion joint inside a slotted collet, plus a knurled release sleeve spinning on the leg axis. Distinct needle-end mechanism. |
| rec_drawing_compass_var_extension_bar_radius/rev_000001 | reviewed | used | Adds a PRISMATIC extension rail between the pencil leg and the hinged holder, extending the drawing radius. Distinct lead-end mechanism. |
| rec_drawing_compass_var_folding_lower_legs_20260714/rev_000001 | reviewed | used | Splits each leg into upper and lower sections joined by a REVOLUTE knee, so the legs fold. Distinct leg structural family. |
| rec_drawing_compass_var_hinged_pen_adapter_20260714/rev_000001 | reviewed | used | Adds a second-stage adapter yoke hinged on the pencil holder to carry a technical pen. Distinct lead-end mechanism. |
| rec_drawing_compass_var_lead_cartridge/rev_000001 | reviewed | used | Turns the lead collet into a separate rotating part on the leg axis instead of geometry fused into the leg. Distinct lead-end component. |
| rec_drawing_compass_var_quick_set_center_wheel/rev_000001 | reviewed | used | Replaces the fine-adjust screw with a quick-set centre wheel on a threaded axle carrying two cantilever release arms. Distinct adjuster mechanism. |
| rec_drawing_compass_var_rack_pinion_head_20260714/rev_000001 | reviewed | used | Adds a central pinion in the head engaging opposed curved rack sectors on the two legs. Distinct adjuster mechanism with a head-mounted rotation axis. |
| rec_drawing_compass_var_ratchet_quadrant_lock_20260714/rev_000001 | reviewed | used | Adds a toothed quadrant on one leg plus a pawl and a release tab on the other. Distinct adjuster mechanism with three moving parts. |
| rec_drawing_compass_var_side_spindle_adjuster_20260714/rev_000001 | reviewed | used | Transverse threaded spindle with a centred knurled wheel captured by hex pivot nuts on both legs, instead of the end-mounted wheel and guide collar of 001. Distinct adjuster component. |
| rec_drawing_compass_var_tubular_legs_20260714/rev_000001 | reviewed | used | Replaces the flat forged sheet leg with a hollow tube leg carrying a pivot lug and a tip socket. Distinct leg structural family. |
| rec_picturex_0611__drawing_compass_with_adjustable_legs__001__png__airflex_batch_20260710_68de3d909b2143c5a9bd0ba516a4d072/rev_000001 | reviewed | used | Origin anchor: hollow horseshoe ring head, tapered sheet legs with annular hinge eyes, cross-screw fine adjustment, spinning top grip, needle socket and fused lead collet. |
| rec_picturex_0611__drawing_compass_with_adjustable_legs__002__png__airflex_batch_20260710_3559da21872945b8bdb7caba02a48c14/rev_000001 | reviewed | used | Second origin. Its head is a distinct fifth family: a horseshoe annulus fused to a solid pivot cheek disc and two triangular cheeks that splay up and out (L27-L58) — four bodies where 001's ring is a plain annulus plus a narrow bridge. The same head is reused by three accepted forks. |
| rec_picturex_0611__drawing_compass_with_adjustable_legs__003__png__airflex_batch_20260710_2d7c021809004b9f99791a92647edf13/rev_000001 | reviewed | used | Origin anchor: solid disk hub head with a saddle, a knurled handle on its own revolute joint, and a side adjustment link driving a knurled wheel. |
| rec_picturex_0611__drawing_compass_with_adjustable_legs__004__png__airflex_batch_20260710_1dfc7a8e26e24466a8a1f62fd5cfc736/rev_000001 | reviewed | used | Origin anchor: plate yoke head with a spreader beam and threaded spindles, plate-profile legs with hinge eyes and inlays, a head-mounted adjustment wheel, a fixed handle cap and a hinged pencil holder. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| head_style | horseshoe_ring | compass head / hinge hub | rec_picturex_0611__drawing_compass_with_adjustable_legs__001__png__airflex_batch_20260710_68de3d909b2143c5a9bd0ba516a4d072/rev_000001 | model.py:L79-L101 | structure | `_head_ring` builds a hollow annular bow (outer 0.0155 / inner 0.0125) with an integral hinge bridge; the head part adds a transverse `hinge_pin` and two `hinge_cap` disks (L196-L225). |
| head_style | disk_hub | compass head / hinge hub | rec_picturex_0611__drawing_compass_with_adjustable_legs__003__png__airflex_batch_20260710_2d7c021809004b9f99791a92647edf13/rev_000001 | model.py:L179-L197 | structure | Solid `head_hub` disk (r=0.0125) plus a rectangular `head_saddle` Box(0.019,0.004,0.010) below it and a long `hinge_pin` — a closed disk head, not an open ring. |
| head_style | plate_yoke | compass head / hinge hub | rec_picturex_0611__drawing_compass_with_adjustable_legs__004__png__airflex_batch_20260710_1dfc7a8e26e24466a8a1f62fd5cfc736/rev_000001 | model.py:L76-L174 | structure | `head_yoke` is an extruded front-view plate profile carrying a `front_bridge`, a 0.12 m `spreader_beam` and upper/lower threaded spindles — a fabricated yoke with a built-in adjuster spine. |
| head_style | spring_bow | compass head / hinge hub | rec_drawing_compass_var_bow_spring_head/rev_000001 | model.py:L82-L130 | structure | `_spring_bow` sweeps a curved arch above the pivot and `_head_spine` tapers from the hinge area to the bow apex; the head is a sprung arch instead of a closed ring or disk. |
| head_style | cheeked_horseshoe | compass head / hinge hub | rec_picturex_0611__drawing_compass_with_adjustable_legs__002__png__airflex_batch_20260710_3559da21872945b8bdb7caba02a48c14/rev_000001 | model.py:L27-L58 | structure | `_head_frame_shape` fuses a hollow annulus, a solid R7 mm pivot cheek at the bore centre and two triangular cheeks splaying up and out; 001's ring has neither the pivot disc nor the cheeks. |
| leg_style | sheet_taper | compass leg | rec_picturex_0611__drawing_compass_with_adjustable_legs__001__png__airflex_batch_20260710_68de3d909b2143c5a9bd0ba516a4d072/rev_000001 | model.py:L41-L76 | structure | `_leg_body` lofts a tapered forged blade through width stations and unions an annular hinge eye; the leg is a flat plate of `LEG_THICKNESS`. |
| leg_style | plate_profile | compass leg | rec_picturex_0611__drawing_compass_with_adjustable_legs__004__png__airflex_batch_20260710_1dfc7a8e26e24466a8a1f62fd5cfc736/rev_000001 | model.py:L176-L237 | structure | `needle_leg_body` is a 6 mm extruded front-view profile with a separate 10 mm `needle_hinge_eye` cylinder, a thin `needle_leg_inlay` face plate and a `needle_leg_rivet`. Layered plate construction, not a single lofted blade. |
| leg_style | tubular | compass leg | rec_drawing_compass_var_tubular_legs_20260714/rev_000001 | model.py:L220-L298 | structure | `leg_0`/`leg_1` are built as hollow tubes with a pivot lug at the head end and a tip socket at the point end (`construction: hollow tube with pivot lug and tip socket`). |
| leg_style | folding_knee | compass leg | rec_drawing_compass_var_folding_lower_legs_20260714/rev_000001 | model.py:L65-L103 | structure+motion | `_upper_leg_shape` ends in a knee knuckle and `_lower_leg_shape` starts from one; each leg becomes two parts joined by a REVOLUTE `left_knee`/`right_knee` (L556-L573) with 0..2.4 rad travel. |
| adjuster_style | cross_screw | radius adjuster | rec_picturex_0611__drawing_compass_with_adjustable_legs__001__png__airflex_batch_20260710_68de3d909b2143c5a9bd0ba516a4d072/rev_000001 | model.py:L104-L145 | structure+motion | `_threaded_shaft` spans both leg bosses and `_adjustment_wheel` sits edge-on at one end; joint `adjust_screw_spin` is CONTINUOUS about the transverse X axis on the needle leg (L416-L430). |
| adjuster_style | center_spindle | radius adjuster | rec_drawing_compass_var_side_spindle_adjuster_20260714/rev_000001 | model.py:L471-L514 | structure | The spindle is centred between two hex pivot nuts captured in bracket pockets on both legs and the knurled wheel sits at mid-span, instead of 001's end wheel plus guide collar. |
| adjuster_style | side_link_wheel | radius adjuster | rec_picturex_0611__drawing_compass_with_adjustable_legs__003__png__airflex_batch_20260710_2d7c021809004b9f99791a92647edf13/rev_000001 | model.py:L362-L402 | structure+motion | A separate `adjustment_link` swings on the leg (REVOLUTE, L477-L485) and carries an `adjustment_wheel` that spins on the link (REVOLUTE, L486-L499) — a two-joint side linkage. |
| adjuster_style | head_wheel | radius adjuster | rec_picturex_0611__drawing_compass_with_adjustable_legs__004__png__airflex_batch_20260710_1dfc7a8e26e24466a8a1f62fd5cfc736/rev_000001 | model.py:L388-L414 | structure+motion | The adjuster is a single knurled wheel mounted on the head's threaded spindle spine, CONTINUOUS about the vertical Z axis (L406-L414), rather than anything mounted on a leg. |
| adjuster_style | bow_spreader | radius adjuster | rec_drawing_compass_var_bow_spring_head/rev_000001 | model.py:L133-L175 | structure+motion | `_spreader_shaft` is a vertical threaded spreader in the head frame and `_spreader_wheel` is its thumbwheel; joint `spreader_screw_spin` is CONTINUOUS about Z at the head (L457-L471). |
| adjuster_style | rack_pinion | radius adjuster | rec_drawing_compass_var_rack_pinion_head_20260714/rev_000001 | model.py:L337-L433 | structure+motion | A `pinion` part with real module/teeth metadata sits at `_PINION_CENTER` in the head and engages opposed curved rack sectors on the two legs; joint `head_to_pinion` is REVOLUTE about Y with ±2.0 rad. |
| adjuster_style | ratchet_quadrant | radius adjuster | rec_drawing_compass_var_ratchet_quadrant_lock_20260714/rev_000001 | model.py:L442-L503 | structure+motion | Three parts — a toothed `quadrant` on the right leg, a `pawl` on the left leg and a `release_tab` on the pawl — with three REVOLUTE joints (L567-L605) forming a locking ratchet instead of a screw. |
| adjuster_style | center_wheel | radius adjuster | rec_drawing_compass_var_quick_set_center_wheel/rev_000001 | model.py:L308-L358 | structure+motion | `center_wheel` is a knurled wheel on a threaded axle with two cantilever release arms, hinged REVOLUTE on the lead leg with a bounded ±0.35 rad quick-set travel (L403-L412). |
| lead_end_style | fixed_collet | lead / pen holder | rec_picturex_0611__drawing_compass_with_adjustable_legs__001__png__airflex_batch_20260710_68de3d909b2143c5a9bd0ba516a4d072/rev_000001 | model.py:L337-L363 | structure | `lead_collet` and `lead_point` are fused into the lead leg itself; the only moving hardware is the clamp screw. Simplest lead end. |
| lead_end_style | hinged_holder | lead / pen holder | rec_picturex_0611__drawing_compass_with_adjustable_legs__004__png__airflex_batch_20260710_1dfc7a8e26e24466a8a1f62fd5cfc736/rev_000001 | model.py:L287-L341 | structure+motion | `pencil_holder` is a separate plate part with its own hinge eye, REVOLUTE on the pencil leg (L371-L384) so the lead stays vertical as the legs open. |
| lead_end_style | extension_rail | lead / pen holder | rec_drawing_compass_var_extension_bar_radius/rev_000001 | model.py:L330-L367 | structure+motion | An `extension_rail` part slides on the leg via PRISMATIC `pencil_leg_to_extension_rail` (0..0.032 m, L456-L472) and carries the hinged holder at its lower end. |
| lead_end_style | pen_adapter | lead / pen holder | rec_drawing_compass_var_hinged_pen_adapter_20260714/rev_000001 | model.py:L441-L540 | structure+motion | An `adapter_yoke` part is hinged on the pencil holder (REVOLUTE ±15°, L527-L540) to clamp a technical pen — a second-stage holder that the other candidates do not have. |
| lead_end_style | rotating_collet | lead / pen holder | rec_drawing_compass_var_lead_cartridge/rev_000001 | model.py:L444-L477 | structure+motion | `lead_collet` is promoted to its own part turning about the leg axis (`left_leg_to_collet`, L571-L584) so the cartridge can be screwed in, instead of being fused into the leg. |
| needle_end_style | fixed_needle | centre point | rec_picturex_0611__drawing_compass_with_adjustable_legs__001__png__airflex_batch_20260710_68de3d909b2143c5a9bd0ba516a4d072/rev_000001 | model.py:L279-L305 | structure | `needle_socket` and `needle_point` are cylinders fused into the needle leg along the leg direction, retained by a `lower_fastener`. |
| needle_end_style | collet_cartridge | centre point | rec_drawing_compass_var_center_point_collet_20260714/rev_000001 | model.py:L556-L652 | structure+motion | A `needle_cartridge` part slides in the slotted collet on a PRISMATIC joint (0..0.006 m, L595-L609) and a knurled `release_sleeve` spins about the leg axis (L653-L662) to release it. |
| handle_style | spin_grip | top handle | rec_picturex_0611__drawing_compass_with_adjustable_legs__001__png__airflex_batch_20260710_68de3d909b2143c5a9bd0ba516a4d072/rev_000001 | model.py:L227-L256 | structure+motion | `top_grip` is a banded cylindrical grip on its own CONTINUOUS `top_grip_spin` joint about the vertical axis at the head top (L247-L256). |
| handle_style | knurled_handle | top handle | rec_picturex_0611__drawing_compass_with_adjustable_legs__003__png__airflex_batch_20260710_2d7c021809004b9f99791a92647edf13/rev_000001 | model.py:L326-L347 | structure+motion | `handle` is a stem plus a knurled knob on a bounded REVOLUTE `head_to_handle` joint (±π, L449-L462) — a different body and a bounded joint. |
| handle_style | fixed_cap | top handle | rec_picturex_0611__drawing_compass_with_adjustable_legs__004__png__airflex_batch_20260710_1dfc7a8e26e24466a8a1f62fd5cfc736/rev_000001 | model.py:L103-L115 | structure | `handle_stem` and `handle_cap` are visuals of the head itself with no joint at all — a rigid moulded cap instead of a turning grip. |

## Coverage note

Every record in the active `0611 / drawing_compass_with_adjustable_legs` workbench pool appears
once in the source review table and all fifteen contribute at least one candidate. Origin `002`
was previously kept as reference only; a re-read of `_head_frame_shape` (L27-L58) shows its head is
a distinct fifth family — a horseshoe annulus fused to a solid pivot cheek disc plus two flared
triangular cheeks, four bodies against 001's ring-plus-bridge — so it now contributes
`head_style=cheeked_horseshoe`. Its tapered legs and cross screw still duplicate origin `001` and
are not taken again.

`core_domain = 5 (head_style) x 4 (leg_style) x 8 (adjuster_style) x 5 (lead_end_style)
x 2 (needle_end_style) x 3 (handle_style) = 4800`; `raw_domain = 4800`, because every source builds
exactly two legs and one of each tip, so there is no honest multiplicity.
