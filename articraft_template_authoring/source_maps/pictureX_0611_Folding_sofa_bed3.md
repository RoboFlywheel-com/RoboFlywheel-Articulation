# pictureX_0611_Folding_sofa_bed3 — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Folding_sofa_bed3
picture_category: 0611
picture_subcategory: Folding_sofa_bed3
category_scope: A lift-and-pull convertible sofa bed — an upholstered carcass with hinged tufted back panels, a carriage that slides forward out from under the seat, and a lift stage on that carriage that raises the bed deck up to seat level. The sliding carriage plus its vertical deck lift is the fixed category identity; folding-leaf sleepers belong to pictureX_0611_Folding_sofa_bed1 and reclining sofas to pictureX_0611_Folding_sofa_bed2.

sync_records:
  - rec_picturex0611_folding_sofa_bed3_fold_down_arms
  - rec_picturex0611_folding_sofa_bed3_ottoman_extension
  - rec_picturex0611_folding_sofa_bed3_ratchet_back
  - rec_picturex0611_folding_sofa_bed3_rollout_legs
  - rec_picturex0611_folding_sofa_bed3_scissor_underframe
  - rec_picturex0611_folding_sofa_bed3_split_back_panels
  - rec_picturex0611_folding_sofa_bed3_trifold_mattress_deck
  - rec_picturex_0611__folding_sofa_bed3__001__png_681510f392e64b02aa2e69f4fa42da4b

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__folding_sofa_bed3__001__png_681510f392e64b02aa2e69f4fa42da4b/rev_000001 | reviewed | used | Image-grounded base for 001.png: upholstered carcass with hinged tufted back panels, a PRISMATIC pull-out carriage under the seat, a lift stage on that carriage and the bed deck it raises. Supplies the host mechanism plus tufted_panel, slab_deck, post_lift and rail_carriage. |
| rec_picturex0611_folding_sofa_bed3_ratchet_back/rev_000001 | reviewed | used | Replaces the plain tufted back with side ratchet plates and multiple recline notches. Source for the ratchet_back build. |
| rec_picturex0611_folding_sofa_bed3_split_back_panels/rev_000001 | reviewed | used | Splits the back into independently articulated panels over a shared upholstered base. Source for the split_panel back build and for the back-panel multiplicity rule. |
| rec_picturex0611_folding_sofa_bed3_trifold_mattress_deck/rev_000001 | reviewed | used | Builds the sleeping deck as hinged upholstered mattress panels instead of one slab. Source for the trifold_deck build. |
| rec_picturex0611_folding_sofa_bed3_scissor_underframe/rev_000001 | reviewed | used | Replaces the straight lift posts with a crossed scissor underframe beneath the deck. Source for the scissor_underframe lift frame. |
| rec_picturex0611_folding_sofa_bed3_rollout_legs/rev_000001 | reviewed | used | Runs the carriage on roll-out feet under its front rail rather than in fixed guides. Taken for the roller_carriage form; the rebuild carries those feet on the carriage itself because the deck lift already takes the front load, so no extra articulated leg is needed. |
| rec_picturex0611_folding_sofa_bed3_fold_down_arms/rev_000001 | reviewed | used | Turns each arm top into a hinged panel that folds out into a bed extension. Re-reviewed: the carriage, lift, deck and back mechanisms are untouched and only the arm above the plinth changes, so it is a component swap on the arm, not a host topology change. |
| rec_picturex0611_folding_sofa_bed3_ottoman_extension/rev_000001 | reviewed | reference_only | Replaces the carriage with a hinged ottoman panel. It removes the sliding carriage and its lift, which are this category's identity. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| back_build | tufted_panel | back panel | rec_picturex_0611__folding_sofa_bed3__001__png_681510f392e64b02aa2e69f4fa42da4b/rev_000001 | model.py:L202-L243 | structure | Hinged upholstered back panel with button tufting and a piped top edge. |
| back_build | ratchet_back | back panel | rec_picturex0611_folding_sofa_bed3_ratchet_back/rev_000001 | model.py:L241-L312 | structure | Back panel carrying exposed side ratchet plates with stepped recline notches. |
| back_build | split_panel | back panel | rec_picturex0611_folding_sofa_bed3_split_back_panels/rev_000001 | model.py:L217-L276 | structure | Back split into two stacked pads over a shared upholstered base rail. |
| deck_build | slab_deck | bed deck | rec_picturex_0611__folding_sofa_bed3__001__png_681510f392e64b02aa2e69f4fa42da4b/rev_000001 | model.py:L309-L360 | structure | One slab mattress deck with a welted edge over a closed platform. |
| deck_build | trifold_deck | bed deck | rec_picturex0611_folding_sofa_bed3_trifold_mattress_deck/rev_000001 | model.py:L309-L360 | structure | Deck built as separate upholstered mattress pads with seam beads between them. |
| lift_frame | post_lift | deck lift frame | rec_picturex_0611__folding_sofa_bed3__001__png_681510f392e64b02aa2e69f4fa42da4b/rev_000001 | model.py:L295-L308 | structure | Straight telescoping lift posts in sockets on the carriage. |
| lift_frame | scissor_underframe | deck lift frame | rec_picturex0611_folding_sofa_bed3_scissor_underframe/rev_000001 | model.py:L242-L256 | structure | Crossed scissor links under the deck instead of straight posts. |
| carriage_style | rail_carriage | carriage frame | rec_picturex_0611__folding_sofa_bed3__001__png_681510f392e64b02aa2e69f4fa42da4b/rev_000001 | model.py:L244-L294 | structure | Carriage running on side rails let into the carcass with a boxed front rail. |
| arm_build | fixed_arm | carcass arm | rec_picturex_0611__folding_sofa_bed3__001__png_681510f392e64b02aa2e69f4fa42da4b/rev_000001 | model.py:L202-L243 | structure | One fixed upholstered arm surround runs the full height of the carcass on each side. |
| arm_build | fold_down_arm | carcass arm | rec_picturex0611_folding_sofa_bed3_fold_down_arms/rev_000001 | model.py:L121-L143, model.py:L428-L480 | structure+motion | `folding_arm_panel_{index}` sits on a hinge bracket over a shortened arm base and swings out on its own REVOLUTE joint to extend the sleeping surface. |
| carriage_style | roller_carriage | carriage frame | rec_picturex0611_folding_sofa_bed3_rollout_legs/rev_000001 | model.py:L362-L420 | structure | Carriage carried on roll-out feet with visible roller housings under its front rail. |
