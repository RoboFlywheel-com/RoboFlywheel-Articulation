# pictureX_0611_Folding_table3 — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Folding_table3
picture_category: 0611
picture_subcategory: Folding_table3
category_scope: A wooden drop-leaf folding dining table — one fixed center top section spanning the short axis, two drop leaves hinged along both of its long edges, and a folding support system that stands the table on the floor and can be collapsed for storage. The hinged-leaf top plus a collapsible support is the fixed category identity. Tables whose whole top folds in half on a single centre hinge belong to pictureX_0611_Folding_table1, and pure fixed-frame folding worktables belong to pictureX_0611_Folding_table2.

sync_records:
  - rec_picturex0611_folding_table3_var_center_pedestal_fold_feet
  - rec_picturex0611_folding_table3_var_d_leaf_rect_spine
  - rec_picturex0611_folding_table3_var_dual_prop_arms
  - rec_picturex0611_folding_table3_var_folding_end_trestle_frames
  - rec_picturex0611_folding_table3_var_gateleg_support
  - rec_picturex0611_folding_table3_var_leaf_narrow_wide
  - rec_picturex0611_folding_table3_var_racetrack_leaf_profile
  - rec_picturex0611_folding_table3_var_scissor_link_supports
  - rec_picturex0611_folding_table3_var_slide_out_leaf_supports
  - rec_picturex0611_folding_table3_var_splayed_aframe_legs
  - rec_picturex0611_folding_table3_var_x_trestle_braces
  - rec_picturex_0611__folding_table3__001__png_27f22d79ac0b41399c93ce8a594e2746
  - rec_picturex_0611__folding_table3__002__png_1d2b460cfb1f4c52b963597c7ee88e86

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__folding_table3__001__png_27f22d79ac0b41399c93ce8a594e2746/rev_000001 | reviewed | used | Image-grounded base for 001.png: round warm-oak top built as a clipped centre strip plus two circular-segment drop leaves on alternating hinge knuckles, carried on four independently folding tapered oak legs pivoted off the centre apron. Supplies the round_arc top profile and the corner_fold_legs support. |
| rec_picturex_0611__folding_table3__002__png_1d2b460cfb1f4c52b963597c7ee88e86/rev_000001 | reviewed | used | Image-grounded base for 002.png: elliptical top cut into a centre strip and two leaves, with a narrow splayed round-tube U trestle hinged off each leaf underside and a separate swinging locking brace. Supplies the ellipse_oval top profile and the narrow_u_trestle support. |
| rec_picturex0611_folding_table3_var_racetrack_leaf_profile/rev_000001 | reviewed | used | Replaces the elliptical outline with a stadium/racetrack wire — straight long sides closed by semicircular end caps — and re-cuts the centre and leaf solids from it. Source for the racetrack top profile. |
| rec_picturex0611_folding_table3_var_d_leaf_rect_spine/rev_000001 | reviewed | used | Narrow rectangular centre spine with two semicircular D leaves whose straight edge is the hinge seam. Source for the d_leaf_rect top profile. |
| rec_picturex0611_folding_table3_var_folding_end_trestle_frames/rev_000001 | reviewed | used | Broad end trestle: wide hinge crossbar, two straight vertical legs at the full half-span, lower stretcher and paired feet. Structurally distinct from the narrow splayed U of 002. Source for the broad_end_trestle support. |
| rec_picturex0611_folding_table3_var_x_trestle_braces/rev_000001 | reviewed | used | Two diagonal legs crossing in an X with a real through pivot pin, caps and a stretcher below the crossing. Source for the x_braced_trestle support. |
| rec_picturex0611_folding_table3_var_splayed_aframe_legs/rev_000001 | reviewed | used | A-frame leg pair converging to a narrow apex crossbar and splaying wide at the floor, with hinge sockets, mid cross stretcher and diagonal triangulating braces. Source for the splayed_aframe support. |
| rec_picturex0611_folding_table3_var_gateleg_support/rev_000001 | reviewed | reference_only | Gate legs swing on a vertical axis and their stiles stay vertical at every gate angle. On a host whose leaves fold flat that stance is a whole-host topology change, not a component swap: a gateleg table's leaf hangs beside a rigid frame instead of over a collapsible one. Reviewed for its swing-out arm/stile proportions, which informed the trestle stance, but it does not become a candidate.
| rec_picturex0611_folding_table3_var_center_pedestal_fold_feet/rev_000001 | reviewed | used | Replaces perimeter legs with a lathed central pedestal column, mount plate, hub hinge brackets and radial folding feet carrying arm, knuckle, pad, cap and locking brace. Source for the center_pedestal support. |
| rec_picturex0611_folding_table3_var_dual_prop_arms/rev_000001 | reviewed | used | Swinging steel prop arms pivoted on the centre apron that rise under a raised leaf and carry a contact pad at the tip. Source for the prop_arm leaf stay and for the per-leaf stay multiplicity rule. |
| rec_picturex0611_folding_table3_var_slide_out_leaf_supports/rev_000001 | reviewed | used | Prismatic wooden pull-out rails running in apron guides, with an outer stop block and fastener heads, extending to catch the leaf underside. Source for the slide_rail leaf stay. |
| rec_picturex0611_folding_table3_var_scissor_link_supports/rev_000001 | reviewed | used | Crossed scissor arm pair on a real through pivot pin with washers and four end brackets, folding flat under the leaf. Source for the scissor_link leaf stay. |
| rec_picturex0611_folding_table3_var_leaf_narrow_wide/rev_000001 | reviewed | reference_only | Identical construction to 002 with only the constants moved (CENTER_WIDTH 0.180 → 0.100, TOP_WIDTH 1.120 → 1.020, hinge X shifted to match). It is evidence that the centre-strip width and leaf reach are a continuous parameter of the same mechanism, not a separate structural candidate. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| top_profile | round_arc | tabletop outline | rec_picturex_0611__folding_table3__001__png_27f22d79ac0b41399c93ce8a594e2746/rev_000001 | model.py:L31-L71 | structure | Circular plan: centre strip clipped out of a full circle, leaves are the two remaining circular segments. |
| top_profile | ellipse_oval | tabletop outline | rec_picturex_0611__folding_table3__002__png_1d2b460cfb1f4c52b963597c7ee88e86/rev_000001 | model.py:L55-L76 | structure | Elliptical plan with independent long/short axes, cut into centre strip and two leaf halves. |
| top_profile | racetrack | tabletop outline | rec_picturex0611_folding_table3_var_racetrack_leaf_profile/rev_000001 | model.py:L55-L94 | structure | Stadium plan: straight long sides closed by semicircular end caps, giving a flat-sided leaf edge. |
| top_profile | d_leaf_rect | tabletop outline | rec_picturex0611_folding_table3_var_d_leaf_rect_spine/rev_000001 | model.py:L33-L54 | structure | Narrow rectangular centre spine with two half-round D leaves whose straight edge is the hinge seam. |
| support_system | corner_fold_legs | folding leg set | rec_picturex_0611__folding_table3__001__png_27f22d79ac0b41399c93ce8a594e2746/rev_000001 | model.py:L300-L377 | structure+motion | Four independent tapered oak legs, each on its own tangential revolute pivot in an apron bearing, folding inward under the top. |
| support_system | narrow_u_trestle | folding leg frame | rec_picturex_0611__folding_table3__002__png_1d2b460cfb1f4c52b963597c7ee88e86/rev_000001 | model.py:L79-L146 | structure+motion | Narrow splayed round-tube U trestle hinged off the leaf underside, with lower stretcher, cross feet, rubber caps and a swinging locking brace on a pin boss. |
| support_system | broad_end_trestle | folding leg frame | rec_picturex0611_folding_table3_var_folding_end_trestle_frames/rev_000001 | model.py:L80-L150 | structure | Wide end trestle with a full-span hinge crossbar and two straight vertical legs instead of the narrow splayed U. |
| support_system | x_braced_trestle | folding leg frame | rec_picturex0611_folding_table3_var_x_trestle_braces/rev_000001 | model.py:L79-L197 | structure | Two diagonal legs crossing in an X on a real through pivot pin with caps, plus a stretcher below the crossing. |
| support_system | splayed_aframe | folding leg frame | rec_picturex0611_folding_table3_var_splayed_aframe_legs/rev_000001 | model.py:L79-L174 | structure | Legs converging to a narrow apex crossbar and splaying wide at the floor, with hinge sockets, mid stretcher and diagonal triangulation. |
| support_system | center_pedestal | folding leg frame | rec_picturex0611_folding_table3_var_center_pedestal_fold_feet/rev_000001 | model.py:L177-L406 | structure+motion | Lathed central pedestal column with a mount plate and hub hinge brackets carrying radial folding feet instead of perimeter legs. |
| leaf_stay | prop_arm | leaf support stay | rec_picturex0611_folding_table3_var_dual_prop_arms/rev_000001 | model.py:L334-L396 | structure+motion | Steel prop arm swinging up from an apron pivot with a captured pin and a contact pad meeting the leaf underside. |
| leaf_stay | slide_rail | leaf support stay | rec_picturex0611_folding_table3_var_slide_out_leaf_supports/rev_000001 | model.py:L335-L392 | motion | Prismatic wooden rail sliding out of an apron guide, with an outer stop block and fastener heads, instead of a swinging arm. |
| leaf_stay | scissor_link | leaf support stay | rec_picturex0611_folding_table3_var_scissor_link_supports/rev_000001 | model.py:L240-L300 | structure | Crossed scissor arm pair on a through pivot pin with washers and four end brackets that folds flat under the leaf. |
