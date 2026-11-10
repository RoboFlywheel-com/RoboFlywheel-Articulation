# pictureX_0611_car_scissor_jack_with_screw_mechanism — SourceMap

source_map_schema: 1
export_category: pictureX_0611_car_scissor_jack_with_screw_mechanism
picture_category: 0611
picture_subcategory: car_scissor_jack_with_screw_mechanism
category_scope: A manual car scissor jack — a rhombus of four pinned arms standing on a base pan, with a left and a right end block at the rhombus waist, a horizontal lead screw drawing those two blocks together, and a load saddle at the apex. The rhombus linkage plus the waist screw is the fixed category identity; hydraulic rams and wheeled hosts belong to the pictureX_0611_hydraulic_jack* categories.

sync_records:
  - rec_car_scissor_jack_with_screw_mechanism_var_beam_saddle
  - rec_car_scissor_jack_with_screw_mechanism_var_double_stage
  - rec_car_scissor_jack_with_screw_mechanism_var_dual_nut_screw
  - rec_car_scissor_jack_with_screw_mechanism_var_dual_rail_base
  - rec_car_scissor_jack_with_screw_mechanism_var_flat_plate_saddle
  - rec_car_scissor_jack_with_screw_mechanism_var_folding_crank_handle
  - rec_car_scissor_jack_with_screw_mechanism_var_hex_drive_socket
  - rec_car_scissor_jack_with_screw_mechanism_var_probe_dualstage_hexdrive
  - rec_car_scissor_jack_with_screw_mechanism_var_probe_trapezoid_dualnut
  - rec_car_scissor_jack_with_screw_mechanism_var_trapezoid_frame
  - rec_car_scissor_jack_with_screw_mechanism_var_twin_plate_arms
  - rec_car_scissor_jack_with_screw_mechanism_var_wide_plate_base
  - rec_picturex_0611__car_scissor_jack_with_screw_mechanism__001__png__airflex_batch_20260710_ce3a0ecf99d2427b8e3b266171137760

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__car_scissor_jack_with_screw_mechanism__001__png__airflex_batch_20260710_ce3a0ecf99d2427b8e3b266171137760/rev_000001 | reviewed | used | Image-grounded base for 001.png, the black car scissor jack: pressed base pan, four pinned arms, two end blocks, lead screw with a crank ring, threaded nut and a notched saddle. Supplies the host rhombus mechanism plus notched_saddle, pressed_pan, crank_ring and stamped_channel. |
| rec_car_scissor_jack_with_screw_mechanism_var_beam_saddle/rev_000001 | reviewed | used | Replaces the notched saddle with a long transverse beam saddle spanning well past the arm width. Source for the beam_saddle load head. |
| rec_car_scissor_jack_with_screw_mechanism_var_flat_plate_saddle/rev_000001 | reviewed | used | Replaces the saddle with a plain flat bearing plate and a turned-down rim. Source for the flat_plate_saddle load head. |
| rec_car_scissor_jack_with_screw_mechanism_var_dual_rail_base/rev_000001 | reviewed | used | Stands the linkage on two separate folded rails instead of one pan. Source for the dual_rail base style. |
| rec_car_scissor_jack_with_screw_mechanism_var_wide_plate_base/rev_000001 | reviewed | used | Widens the base into a single broad footplate with turned edges. Source for the wide_plate base style. |
| rec_car_scissor_jack_with_screw_mechanism_var_hex_drive_socket/rev_000001 | reviewed | used | Ends the lead screw in a hex drive socket for a wheel brace instead of a crank ring. Source for the hex_socket drive head. |
| rec_car_scissor_jack_with_screw_mechanism_var_folding_crank_handle/rev_000001 | reviewed | used | Adds a folding crank handle on the screw end. Source for the folding_crank drive head. |
| rec_car_scissor_jack_with_screw_mechanism_var_twin_plate_arms/rev_000001 | reviewed | used | Builds each arm from parallel plates on a shared pin instead of one stamped channel. Source for the twin_plate arm form and for the arm-plate multiplicity rule. |
| rec_car_scissor_jack_with_screw_mechanism_var_double_stage/rev_000001 | reviewed | reference_only | Stacks a second rhombus on a mid block. Each stage needs its own screw and waist, so it duplicates the whole host rather than swapping a component; the rebuild keeps one rhombus and varies the arm build-up instead. |
| rec_car_scissor_jack_with_screw_mechanism_var_dual_nut_screw/rev_000001 | reviewed | reference_only | Adds a second nut on the same screw. That is a fastener count on a shared thread pitch, not a separable component, and it would couple a slot to the screw pitch. |
| rec_car_scissor_jack_with_screw_mechanism_var_trapezoid_frame/rev_000001 | reviewed | reference_only | Changes the rhombus itself into a trapezoid. That is the identifying linkage, not a component, so it is kept fixed rather than made a slot. |
| rec_car_scissor_jack_with_screw_mechanism_var_probe_dualstage_hexdrive/rev_000001 | reviewed | rejected_duplicate | A probe combining the double-stage frame with the hex drive; both are already reviewed above and it contributes no new component. |
| rec_car_scissor_jack_with_screw_mechanism_var_probe_trapezoid_dualnut/rev_000001 | reviewed | rejected_duplicate | A probe combining the trapezoid frame with the dual nut; both are already reviewed above and it contributes no new component. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| saddle_head | notched_saddle | apex load head | rec_picturex_0611__car_scissor_jack_with_screw_mechanism__001__png__airflex_batch_20260710_ce3a0ecf99d2427b8e3b266171137760/rev_000001 | model.py:L329-L344 | structure | Pressed saddle with a central notch and raised end horns that trap a sill seam. |
| saddle_head | beam_saddle | apex load head | rec_car_scissor_jack_with_screw_mechanism_var_beam_saddle/rev_000001 | model.py:L390-L405 | structure | Long transverse beam saddle spanning well past the arm width, with end caps. |
| saddle_head | flat_plate_saddle | apex load head | rec_car_scissor_jack_with_screw_mechanism_var_flat_plate_saddle/rev_000001 | model.py:L372-L387 | structure | Plain flat bearing plate with a turned-down rim and no notch. |
| base_style | pressed_pan | base footprint | rec_picturex_0611__car_scissor_jack_with_screw_mechanism__001__png__airflex_batch_20260710_ce3a0ecf99d2427b8e3b266171137760/rev_000001 | model.py:L280-L295 | structure | Single pressed pan with upturned side flanges carrying the lower pin lugs. |
| base_style | dual_rail | base footprint | rec_car_scissor_jack_with_screw_mechanism_var_dual_rail_base/rev_000001 | model.py:L315-L330 | structure | Two separate folded rails under the linkage with an open centre. |
| base_style | wide_plate | base footprint | rec_car_scissor_jack_with_screw_mechanism_var_wide_plate_base/rev_000001 | model.py:L297-L312 | structure | Single broad footplate with turned edges spreading the load. |
| drive_head | crank_ring | screw drive end | rec_picturex_0611__car_scissor_jack_with_screw_mechanism__001__png__airflex_batch_20260710_ce3a0ecf99d2427b8e3b266171137760/rev_000001 | model.py:L378-L386 | structure | Bent rod crank ring formed on the screw end. |
| drive_head | hex_socket | screw drive end | rec_car_scissor_jack_with_screw_mechanism_var_hex_drive_socket/rev_000001 | model.py:L394-L402 | structure | Hex drive socket on the screw end for a wheel brace. |
| drive_head | folding_crank | screw drive end | rec_car_scissor_jack_with_screw_mechanism_var_folding_crank_handle/rev_000001 | model.py:L438-L470 | structure | Folding crank handle with a knuckle and grip on the screw end. |
| arm_style | stamped_channel | scissor arm | rec_picturex_0611__car_scissor_jack_with_screw_mechanism__001__png__airflex_batch_20260710_ce3a0ecf99d2427b8e3b266171137760/rev_000001 | model.py:L296-L320 | structure | Single stamped channel section arm with folded flanges and pressed pin bosses. |
| arm_style | twin_plate | scissor arm | rec_car_scissor_jack_with_screw_mechanism_var_twin_plate_arms/rev_000001 | model.py:L339-L365 | structure | Arm built from parallel flat plates on a shared pin, with spacer collars between them. |
