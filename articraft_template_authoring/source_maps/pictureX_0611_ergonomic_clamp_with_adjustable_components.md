# pictureX_0611_ergonomic_clamp_with_adjustable_components — SourceMap

source_map_schema: 1
export_category: pictureX_0611_ergonomic_clamp_with_adjustable_components
picture_category: 0611
picture_subcategory: ergonomic_clamp_with_adjustable_components
category_scope: A desk-edge screw clamp carrying an upright post, a height carriage locked by a knob, an adjustable arm structure and a work tray at its end. The clamp station, the upright post and the height carriage are always present; what varies is the number of clamp screw stations, the adjustable arm structure between carriage and head, and the tray head. A monitor arm with no tray, or a tray with no clamp, is out of scope.

sync_records:
  - rec_laptop_tray_arm_var_foldaway_tray_hinge_20260714
  - rec_laptop_tray_arm_var_four_bar_reach_20260714
  - rec_laptop_tray_arm_var_overcenter_cam_clamp_20260714
  - rec_laptop_tray_arm_var_sector_tilt_lock_20260714
  - rec_laptop_tray_arm_var_width_adjustable_tray_20260714
  - rec_laptop_tray_arm_var_dual_screw_clamp
  - rec_laptop_tray_arm_var_gas_spring
  - rec_laptop_tray_arm_var_quick_release_yoke
  - rec_laptop_tray_arm_var_scissor_linkage
  - rec_laptop_tray_arm_var_sliding_tray_rails
  - rec_laptop_tray_arm_var_telescoping_boom
  - rec_picturex_0611__ergonomic_clamp_with_adjustable_components__001__png__airflex_batch_20260710_b468a57ec62e4ffa8a18e65c7f02b971
  - rec_picturex_0611__ergonomic_clamp_with_adjustable_components__002__png__airflex_batch_20260710_792cf2b0f2204b51a17dabc1a51732c3

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_laptop_tray_arm_var_dual_screw_clamp/rev_000001 | reviewed | used | Two independent screw stations on one wide clamp frame; the rest of the machine repeats the 002 baseline. |
| rec_laptop_tray_arm_var_foldaway_tray_hinge_20260714/rev_000001 | reviewed | used | Replaces the tray-to-yoke tilt with a rear fold hinge, a bracket and a detent plate, so the deck parks vertically instead of tilting a few degrees. |
| rec_laptop_tray_arm_var_four_bar_reach_20260714/rev_000001 | reviewed | rejected_duplicate | Its anti-sag four-bar chain is the same paired upper/lower bar tree the gas-spring parallelogram fork already contributes; only the strut is absent, which is a component-presence detail rather than a new component. |
| rec_laptop_tray_arm_var_overcenter_cam_clamp_20260714/rev_000001 | reviewed | used | Drops the threaded spindle entirely: a `cam_lever` on the frame drives a `cam_follower` jaw on a prismatic, and the pressure pad rides the follower. |
| rec_laptop_tray_arm_var_sector_tilt_lock_20260714/rev_000001 | reviewed | used | Replaces the friction `tilt_handle` at the yoke axis with a toothed `tilt_sector` on the carrier and a sprung `tilt_pawl` part on the tray. |
| rec_laptop_tray_arm_var_width_adjustable_tray_20260714/rev_000001 | reviewed | used | Adds two captured side support rails on bounded prismatic joints under the retained central deck, so the tray width itself becomes adjustable. |
| rec_laptop_tray_arm_var_gas_spring/rev_000001 | reviewed | used | Parallelogram shoulder plus a real gas strut (cylinder and sliding piston) between the post and the upper link. |
| rec_laptop_tray_arm_var_quick_release_yoke/rev_000001 | reviewed | used | Distinct head: a dovetail carriage that slides out of the yoke and a lock lever that captures it. |
| rec_laptop_tray_arm_var_scissor_linkage/rev_000001 | reviewed | used | The single arm is replaced by two crossed scissor links with their own crossing pivot. |
| rec_laptop_tray_arm_var_sliding_tray_rails/rev_000001 | reviewed | used | Distinct head: the tray rides a prismatic carriage on the yoke with a latch pawl at its end. |
| rec_laptop_tray_arm_var_telescoping_boom/rev_000001 | reviewed | used | The elbow is replaced by a real outer/inner tube pair on a prismatic telescope stroke. |
| rec_picturex_0611__ergonomic_clamp_with_adjustable_components__001__png__airflex_batch_20260710_b468a57ec62e4ffa8a18e65c7f02b971/rev_000001 | reviewed | reference_only | Same shoulder/elbow/tray topology as the quick-release fork, plus a laptop and screen prop that is outside this subcategory. Reviewed for proportions only; it would only duplicate candidates already taken from that fork. |
| rec_picturex_0611__ergonomic_clamp_with_adjustable_components__002__png__airflex_batch_20260710_792cf2b0f2204b51a17dabc1a51732c3/rev_000001 | reviewed | used | Origin record for 002.png. Supplies the always-present clamp/post/height-carriage host and the three baseline candidates: a single screw station, a two-link arm and a plain tilting tray. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| clamp_form | single_screw | one screw station on a narrow C-frame | rec_picturex_0611__ergonomic_clamp_with_adjustable_components__002__png__airflex_batch_20260710_792cf2b0f2204b51a17dabc1a51732c3/rev_000001 | model.py:L174-L260 | structure | One `clamp_spindle` with `spindle_adjust`, one `pressure_pad` and one wing handle on a single-throat frame. |
| clamp_form | dual_screw | two screw stations on a wide C-frame | rec_laptop_tray_arm_var_dual_screw_clamp/rev_000001 | model.py:L34-L56, model.py:L195-L294 | structure+motion | `_wide_clamp_frame` carries two throats and the loop emits `clamp_spindle_{i}`, `pressure_pad_{i}` and `wing_handle_{i}` with independent `spindle_adjust_{i}` joints. |
| arm_form | two_link_arm | primary and secondary link on an elbow | rec_picturex_0611__ergonomic_clamp_with_adjustable_components__002__png__airflex_batch_20260710_792cf2b0f2204b51a17dabc1a51732c3/rev_000001 | model.py:L354-L433 | structure+motion | `primary_arm` on `carriage_to_arm` plus `secondary_arm` on `arm_elbow`; two revolutes and two distinct link bodies. |
| arm_form | telescoping_boom | outer and inner tube on a prismatic stroke | rec_laptop_tray_arm_var_telescoping_boom/rev_000001 | model.py:L43-L91, model.py:L415-L463 | structure+motion | `_primary_outer_tube`/`_secondary_inner_tube` are genuinely hollow sections and `arm_telescope` is prismatic, not a revolute elbow. |
| arm_form | scissor_linkage | two crossed links with a crossing pivot | rec_laptop_tray_arm_var_scissor_linkage/rev_000001 | model.py:L41-L141, model.py:L435-L507 | structure+motion | `_scissor_upper_link`/`_scissor_lower_link` cross at `scissor_cross`; the part tree is a scissor pair rather than a serial arm. |
| arm_form | gas_spring_parallelogram | parallelogram shoulder braced by a gas strut | rec_laptop_tray_arm_var_gas_spring/rev_000001 | model.py:L229-L417 | structure+motion | `lower_link`/`upper_link` form the parallelogram and a separate `gas_cylinder` plus `gas_piston` add a `gas_spring_extend` prismatic force path. |
| tray_head | fixed_tilt_tray | yoke plus one tray on a single tilt | rec_picturex_0611__ergonomic_clamp_with_adjustable_components__002__png__airflex_batch_20260710_792cf2b0f2204b51a17dabc1a51732c3/rev_000001 | model.py:L434-L495 | structure | `wrist_yoke` on `arm_to_wrist` carries `laptop_tray` on one `tray_tilt`; no further head motion exists. |
| tray_head | sliding_rails | tray riding a prismatic carriage with a latch | rec_laptop_tray_arm_var_sliding_tray_rails/rev_000001 | model.py:L490-L595 | structure+motion | `tray_carriage` adds a `tray_slide` prismatic and `slide_latch` a `slide_latch_pivot` revolute between yoke and tray. |
| tray_head | quick_release_dovetail | dovetail release carriage with a lock lever | rec_laptop_tray_arm_var_quick_release_yoke/rev_000001 | model.py:L372-L503 | structure+motion | `dovetail_carriage` on `dovetail_slide` plus `lock_lever` on `lock_lever_pivot` make the tray removable rather than fixed to the yoke. |
| clamp_form | overcenter_cam | over-centre cam lever driving a follower jaw | rec_laptop_tray_arm_var_overcenter_cam_clamp_20260714/rev_000001 | model.py:L118-L236 | structure+motion | `cam_lever` on a REVOLUTE at the frame and `cam_follower` on a PRISMATIC replace `spindle_slide`/`clamp_spindle`; the pad rides the follower. |
| tray_head | foldaway_hinge | rear fold hinge with a detent plate | rec_laptop_tray_arm_var_foldaway_tray_hinge_20260714/rev_000001 | model.py:L370-L470 | structure+motion | A `fold_bracket` with bored cheeks, a hinge pin and a `detent_plate` carry the deck on a 0-to-90-degree fold instead of a few degrees of tilt. |
| tray_width | fixed_deck | one fixed-width deck | rec_picturex_0611__ergonomic_clamp_with_adjustable_components__002__png__airflex_batch_20260710_792cf2b0f2204b51a17dabc1a51732c3/rev_000001 | model.py:L434-L495 | structure | The origin record's deck is a single plate with no lateral support members. |
| tray_width | sliding_side_rails | two captured side rails on a width stroke | rec_laptop_tray_arm_var_width_adjustable_tray_20260714/rev_000001 | model.py:L149-L167, model.py:L534-L559 | structure+motion | `_side_rail` emits left/right rails on bounded prismatic joints under the retained central deck. |
| tilt_lock | friction_handle | friction knob on the tilt axis | rec_picturex_0611__ergonomic_clamp_with_adjustable_components__002__png__airflex_batch_20260710_792cf2b0f2204b51a17dabc1a51732c3/rev_000001 | model.py:L434-L495 | structure | The origin record holds tray angle with a plain hand knob on the yoke axis and no indexing hardware. |
| tilt_lock | sector_pawl | toothed sector plus sprung pawl | rec_laptop_tray_arm_var_sector_tilt_lock_20260714/rev_000001 | model.py:L403-L467, model.py:L519-L572 | structure+motion | `tilt_sector` teeth on the carrier and a `tilt_pawl` part on its own release revolute index the tilt instead of a friction handle. |

## Rejected and reference notes

- The four-bar reach fork is reviewed and kept as a duplicate of the parallelogram linkage, not as a
  new candidate; see its review row.
- The laptop and screen props (`laptop_base`, `screen`) present in several sources are payload, not part of
  the clamp assembly, and are excluded from every candidate.
- The upright post, the `post_lock_knob`, the `height_carriage` and its `carriage_lock_knob` are identical in
  all eight sources, so they stay a single parameterised host rather than a slot; the origin record's
  `model.py:L261-L353` is the reviewed reference for them.
- Wing-nut versus T-bar handle styles change only a small handle solid and are derived detail, not candidates.
