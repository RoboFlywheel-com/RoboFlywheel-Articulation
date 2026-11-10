# pictureX_0611_Folding_sofa_bed1 — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Folding_sofa_bed1
picture_category: 0611
picture_subcategory: Folding_sofa_bed1
category_scope: A pull-out (sleeper) sofa bed — an upholstered carcass with fixed arms, a reclining backrest, a guided carriage that slides forward out of the carcass, folding mattress leaves carried on that carriage, and fold-down legs under the front leaf that reach the floor when the bed is made. The carriage plus folding leaves is the fixed category identity; click-clack sofas with no carriage belong to pictureX_0611_Folding_sofa_bed.

sync_records:
  - rec_picturex0611_folding_sofa_bed1_clickclack_back
  - rec_picturex0611_folding_sofa_bed1_foldout_support_legs
  - rec_picturex0611_folding_sofa_bed1_pullout_deck
  - rec_picturex0611_folding_sofa_bed1_slatted_pullout_frame
  - rec_picturex0611_folding_sofa_bed1_trifold_panels
  - rec_picturex_0611__folding_sofa_bed1__002__png_f3a7fcc7d38c4e7d8d79ea405442889c
  - rec_picturex_0611__folding_sofa_bed1__003__png_rerun_ef2699b37030410e922caf5507d1190e
  - rec_use-the-attached-reference-image-as-the-primary-_20260710_133744_517392_1fd605e7

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__folding_sofa_bed1__002__png_f3a7fcc7d38c4e7d8d79ea405442889c/rev_000001 | reviewed | used | Image-grounded record for 002.png: carcass frame, fixed seat, reclining backrest, PRISMATIC pull-out deck in guide sleeves, a hinged front deck leaf and fold-down support legs. This is the cleanest statement of the host mechanism and supplies plain_pad and sleeve_rail. |
| rec_picturex_0611__folding_sofa_bed1__003__png_rerun_ef2699b37030410e922caf5507d1190e/rev_000001 | reviewed | used | Image-grounded record for 003.png, the fully-made bed: same carriage host with a three-leaf slatted mattress and U-shaped fold-down legs. Supplies the slatted_panel mattress build and the u_leg support. |
| rec_use-the-attached-reference-image-as-the-primary-_20260710_133744_517392_1fd605e7/rev_000001 | reviewed | used | Image-grounded record for 001.png (its record id is an untrimmed prompt string, but its category slug is picturex_0611__folding_sofa_bed1__001__png_rerun). Slatted carriage platform and a folding slatted backrest; supplies slatted_frame and slatted_fold_back. |
| rec_picturex0611_folding_sofa_bed1_clickclack_back/rev_000001 | reviewed | used | Replaces the plain back pad with a click-clack back carrying visible side ratchet plates. Source for the clickclack_ratchet back style. |
| rec_picturex0611_folding_sofa_bed1_foldout_support_legs/rev_000001 | reviewed | used | Replaces the U legs with paired fold-out twin-post legs on visible hinge brackets. Source for the twin_post bed leg. |
| rec_picturex0611_folding_sofa_bed1_pullout_deck/rev_000001 | reviewed | used | Runs the carriage on nested telescoping support rails instead of square guide sleeves. Source for the nested_rail deck frame. |
| rec_picturex0611_folding_sofa_bed1_trifold_panels/rev_000001 | reviewed | used | Builds the mattress as hinged upholstered cushion panels rather than slatted frames, and emits them in a loop. Source for the tufted_panel mattress build and for the leaf multiplicity rule. |
| rec_picturex0611_folding_sofa_bed1_slatted_pullout_frame/rev_000001 | reviewed | rejected_duplicate | Structurally identical to the 001.png record above (same frame, seat_base, mattress_leaf, slatted deck, support legs and folding backrest); it contributes no distinct component. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| back_style | plain_pad | backrest | rec_picturex_0611__folding_sofa_bed1__002__png_f3a7fcc7d38c4e7d8d79ea405442889c/rev_000001 | model.py:L178-L207 | structure | Plain upholstered back pad on a hinge tube, no exposed hardware. |
| back_style | clickclack_ratchet | backrest | rec_picturex0611_folding_sofa_bed1_clickclack_back/rev_000001 | model.py:L368-L440 | structure | Click-clack back with exposed side ratchet plates and stepped notches at the hinge. |
| back_style | slatted_fold_back | backrest | rec_use-the-attached-reference-image-as-the-primary-_20260710_133744_517392_1fd605e7/rev_000001 | model.py:L266-L315 | structure | Folding back built as a slatted frame with an upholstered face and exposed rails. |
| deck_frame | sleeve_rail | carriage frame | rec_picturex_0611__folding_sofa_bed1__002__png_f3a7fcc7d38c4e7d8d79ea405442889c/rev_000001 | model.py:L221-L265 | structure | Carriage running on square guide sleeves let into the front apron. |
| deck_frame | nested_rail | carriage frame | rec_picturex0611_folding_sofa_bed1_pullout_deck/rev_000001 | model.py:L303-L374 | structure | Carriage on nested telescoping support rails with visible inner and outer sections. |
| deck_frame | slatted_frame | carriage frame | rec_use-the-attached-reference-image-as-the-primary-_20260710_133744_517392_1fd605e7/rev_000001 | model.py:L192-L236 | structure | Carriage built as an open slatted platform with transverse slats across side rails. |
| mattress_build | slatted_panel | mattress leaf | rec_picturex_0611__folding_sofa_bed1__003__png_rerun_ef2699b37030410e922caf5507d1190e/rev_000001 | model.py:L78-L161 | structure | Leaf built as a steel frame with a regular rhythm of transverse slats under a mattress pad. |
| mattress_build | tufted_panel | mattress leaf | rec_picturex0611_folding_sofa_bed1_trifold_panels/rev_000001 | model.py:L334-L379 | structure | Leaf built as an upholstered cushion panel with seams and buttons instead of exposed slats. |
| bed_leg | u_leg | fold-down bed leg | rec_picturex_0611__folding_sofa_bed1__003__png_rerun_ef2699b37030410e922caf5507d1190e/rev_000001 | model.py:L415-L438 | structure+motion | U-shaped tube leg with foot pads, hinged under the mattress leaf. |
| bed_leg | twin_post | fold-down bed leg | rec_picturex0611_folding_sofa_bed1_foldout_support_legs/rev_000001 | model.py:L179-L258 | structure+motion | Paired square posts on a visible hinge bracket with a tie bar between them. |
