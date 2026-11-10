# pictureX_0611_bi_fold_closet_door_system — SourceMap

source_map_schema: 1
export_category: pictureX_0611_bi_fold_closet_door_system
picture_category: 0611
picture_subcategory: bi_fold_closet_door_system
category_scope: Bi-fold closet door systems: a lined opening with side jambs, a sill and a header carrying a U-track, closed by one or more pairs of folding leaves whose inner leaf pivots on the jamb and whose outer leaf folds back on a centre hinge; sliding wardrobe doors, single swing doors and cabinet doors without a fold pair are not candidates.

sync_records:
  - rec_bi_fold_closet_door_system_var_dual_track
  - rec_bi_fold_closet_door_system_var_glass_lite
  - rec_bi_fold_closet_door_system_var_jamb_hinged
  - rec_bi_fold_closet_door_system_var_louver_slat_count
  - rec_bi_fold_closet_door_system_var_louvered
  - rec_bi_fold_closet_door_system_var_mirrored
  - rec_bi_fold_closet_door_system_var_pivot_only
  - rec_bi_fold_closet_door_system_var_plain_frame
  - rec_bi_fold_closet_door_system_var_quad_pair
  - rec_bi_fold_closet_door_system_var_raised_panel
  - rec_bi_fold_closet_door_system_var_single_pair
  - rec_bi_fold_closet_door_system_var_top_hung
  - rec_bi_fold_closet_door_system_var_trifold_leaf
  - rec_bi_fold_closet_door_system_var_triple_pair
  - rec_picturex_0611__bi_fold_closet_door_system__001__png__airflex_batch_20260710_d5115d15e5854d6ba411c6bd534b3258

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__bi_fold_closet_door_system__001__png__airflex_batch_20260710_d5115d15e5854d6ba411c6bd534b3258/rev_000001 | reviewed | used | Origin: a lined opening with jambs, sill and header U-track closed by two pairs of folding slab leaves on jamb pivots and centre hinges. |
| rec_bi_fold_closet_door_system_var_plain_frame/rev_000001 | reviewed | used | The plain slab leaf: a connected core with stiles and rails and no applied face treatment. |
| rec_bi_fold_closet_door_system_var_mirrored/rev_000001 | reviewed | used | The mirrored leaf: a framed reflective insert set inside the stile and rail frame. |
| rec_bi_fold_closet_door_system_var_louvered/rev_000001 | reviewed | used | The louvered leaf: evenly pitched angled slats captured between the top and bottom rails. |
| rec_bi_fold_closet_door_system_var_raised_panel/rev_000001 | reviewed | used | The raised-panel leaf: a stile-and-rail frame around raised centre fields with bevelled edges. |
| rec_bi_fold_closet_door_system_var_jamb_hinged/rev_000001 | reviewed | used | Only the hardware family is reused: edge butt hinge leaves at the jamb face replace the pivot pin and floor socket. |
| rec_bi_fold_closet_door_system_var_top_hung/rev_000001 | reviewed | used | Only the hardware family is reused: a top-hung carrier suspends the leaf from the header track and the bottom keeps only a slim locating pin. |
| rec_bi_fold_closet_door_system_var_single_pair/rev_000001 | reviewed | reference_only | Establishes PAIR_COUNT as the multiplicity rule and gives the one-pair proportions. |
| rec_bi_fold_closet_door_system_var_triple_pair/rev_000001 | reviewed | reference_only | The same PAIR_COUNT rule at three pairs; adds no new component form. |
| rec_bi_fold_closet_door_system_var_quad_pair/rev_000001 | reviewed | reference_only | The same rule at four pairs with mullion posts; adds no new component form. |
| rec_bi_fold_closet_door_system_var_dual_track/rev_000001 | reviewed | used | Only the hardware family is reused: a second bottom guide track in the sill with its own floor roller under the leaf. |
| rec_bi_fold_closet_door_system_var_pivot_only/rev_000001 | reviewed | used | Only the hardware family is reused: full-height jamb pivots carry the whole door load on stout corner plates and thicker pins, with no track roller at all. |
| rec_bi_fold_closet_door_system_var_glass_lite/rev_000001 | reviewed | used | The glass-lite leaf: the solid core is replaced by a perimeter frame that captures a rebated translucent field, so the leaf reads through rather than as a slab. |
| rec_bi_fold_closet_door_system_var_louver_slat_count/rev_000001 | reviewed | reference_only | Only varies the louver slat count on the reviewed louvered leaf. |
| rec_bi_fold_closet_door_system_var_trifold_leaf/rev_000001 | reviewed | used | The three-leaf accordion set: a mid leaf is added between the jamb leaf and the handle leaf, and the fold alternates direction at each centre hinge. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| fold_set | pair_fold | two-leaf fold set | rec_picturex_0611__bi_fold_closet_door_system__001__png__airflex_batch_20260710_d5115d15e5854d6ba411c6bd534b3258/rev_000001 | model.py:L241-L266 | structure+motion | Each bay closes with one jamb leaf and one handle leaf folding on a single centre hinge. |
| fold_set | trifold_fold | three-leaf accordion set | rec_bi_fold_closet_door_system_var_trifold_leaf/rev_000001 | model.py:L576-L622 | structure+motion | A mid leaf sits between the jamb and handle leaves, and the accordion alternates fold direction at each centre hinge. |
| leaf_face | plain_slab | plain stile-and-rail slab | rec_bi_fold_closet_door_system_var_plain_frame/rev_000001 | model.py:L58-L238 | structure | A connected core with near and far stiles and top and bottom rails and no applied face field. |
| leaf_face | mirrored | framed reflective insert | rec_bi_fold_closet_door_system_var_mirrored/rev_000001 | model.py:L71-L251 | structure | A thin reflective field is set inside the stile and rail frame, standing proud of the core face. |
| leaf_face | louvered | pitched louver slats | rec_bi_fold_closet_door_system_var_louvered/rev_000001 | model.py:L91-L275 | structure | Angled slats are evenly pitched between the rails, each embedded into the core as if mortised into the stiles. |
| leaf_face | raised_panel | raised centre fields | rec_bi_fold_closet_door_system_var_raised_panel/rev_000001 | model.py:L82-L331 | structure | A stile-and-rail frame surrounds raised centre fields with bevelled edges. |
| leaf_face | glass_lite | framed glass lite | rec_bi_fold_closet_door_system_var_glass_lite/rev_000001 | model.py:L82-L117 | structure | A perimeter frame captures a rebated translucent field instead of a solid door core. |
| hardware_set | heavy_pivot | full-height load-bearing pivots | rec_bi_fold_closet_door_system_var_pivot_only/rev_000001 | model.py:L137-L170 | structure | Stout top and bottom corner plates and thicker pins carry the entire leaf, replacing the captured track roller. |
| hardware_set | dual_track | top and bottom guide tracks | rec_bi_fold_closet_door_system_var_dual_track/rev_000001 | model.py:L281-L296 | structure | A second guide track is let into the sill and a floor roller under the leaf runs in it. |
| hardware_set | jamb_pivot | pin pivot and track roller | rec_picturex_0611__bi_fold_closet_door_system__001__png__airflex_batch_20260710_d5115d15e5854d6ba411c6bd534b3258/rev_000001 | model.py:L241-L266 | structure | Corner blocks carry a floor pivot pin and a top roller inset from the free edge so it stays captured in the track. |
| hardware_set | butt_hinge | edge butt hinges at the jamb | rec_bi_fold_closet_door_system_var_jamb_hinged/rev_000001 | model.py:L253-L267 | structure | Knuckled butt-hinge leaves at the jamb face replace the pivot pin and its floor socket. |
| hardware_set | top_hung | suspended carrier with a floor pin | rec_bi_fold_closet_door_system_var_top_hung/rev_000001 | model.py:L139-L257 | structure | A carrier bracket hangs the leaf from the header track and the bottom keeps only a slim locating pin. |

## Component evidence

- The opening lining, header U-track and the fold chain are identity-fixed host structure
  (`rec_bi_fold_closet_door_system_var_pivot_only/rev_000001` `model.py:L495-L510` for the
  U-track web and lips), so they are not a slot: every seed keeps a jamb-pivoted inner leaf
  and a centre-hinged outer leaf per pair.
- Pair multiplicity comes from `rec_bi_fold_closet_door_system_var_single_pair/rev_000001`
  `model.py:L20-L47`, which derives the bay width and leaf span from PAIR_COUNT.
