# pictureX_0611_Folding_table5 — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Folding_table5
picture_category: 0611
picture_subcategory: Folding_table5

category_scope: A round gateleg drop-leaf table: a narrow fixed centre spine on its own standing frame, two semicircular leaves hinged along both long edges of that spine, and swing-out supports carried on the frame that hold a raised leaf. Folded, the table reads as a half-round or narrow console against a wall. The narrow spine plus frame-mounted swing-out supports is the category identity; tables whose leaves are carried by leaf-mounted trestles belong to pictureX_0611_Folding_table3.

sync_records:
  - rec_picturex0611_folding_table5_var_arc_gate_support
  - rec_picturex0611_folding_table5_var_brake_caster_locks
  - rec_picturex0611_folding_table5_var_double_shelf_spine
  - rec_picturex0611_folding_table5_var_folding_cross_trestle_support
  - rec_picturex0611_folding_table5_var_four_casters
  - rec_picturex0611_folding_table5_var_leaf_locking_latches
  - rec_picturex0611_folding_table5_var_shelf_spine
  - rec_picturex0611_folding_table5_var_single_drop_leaf_n1
  - rec_picturex0611_folding_table5_var_telescoping_gate_braces
  - rec_picturex0611_folding_table5_var_three_caster_layout_n3
  - rec_picturex0611_folding_table5_var_wall_bracket_arms
  - rec_picturex_0611__folding_table5__001__png_1ac9d775a5de4deaa6918c2b8db999a4
  - rec_picturex_0611__folding_table5__002__png_2402f0a0895c48cfa6267157874c2050
  - rec_picturex_0611__folding_table5__003__png_ef8fdc887f014728a345a684122913c2

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__folding_table5__001__png_1ac9d775a5de4deaa6918c2b8db999a4/rev_000001 | reviewed | used | Image-grounded base for 001.png: 1.10 m round top cut into a narrow engraved centre spine and two semicircular leaves, on a black steel frame with two rod-built swing gates. Supplies the swing_gate support and the open_spine frame. |
| rec_picturex_0611__folding_table5__002__png_2402f0a0895c48cfa6267157874c2050/rev_000001 | reviewed | used | Second image reading of the same table, with the frame built as a boxed spine carcass and both gates pivoting from its uprights. It supplies the proportions and the gate pivot station the host reuses, and the broad flat support pads under the foot bars that become the pad_foot foot candidate. |
| rec_picturex_0611__folding_table5__003__png_ef8fdc887f014728a345a684122913c2/rev_000001 | reviewed | used | Image-grounded base for 003.png: the same gateleg table standing on swivelling casters, with a swivel axis and a roll axis per caster. Supplies the caster_glide frame. |
| rec_picturex0611_folding_table5_var_arc_gate_support/rev_000001 | reviewed | used | Replaces the straight rod gate with an arched gate whose top rail sweeps up to the leaf. Source for the arc_gate support. |
| rec_picturex0611_folding_table5_var_folding_cross_trestle_support/rev_000001 | reviewed | used | Swaps the swinging gates for folding cross trestles that scissor out from the spine. Source for the cross_trestle support. |
| rec_picturex0611_folding_table5_var_telescoping_gate_braces/rev_000001 | reviewed | used | Adds a real prismatic brace that telescopes out of each gate to lock it at full swing. Source for the telescoping_brace support. |
| rec_picturex0611_folding_table5_var_wall_bracket_arms/rev_000001 | reviewed | used | Replaces the gates with folding bracket arms pivoting straight off the spine, as on a wall-hung drop-leaf. Source for the wall_bracket support. |
| rec_picturex0611_folding_table5_var_leaf_locking_latches/rev_000001 | reviewed | used | Adds a pivoting latch on the frame that locks a raised leaf down onto the gate. Source for the latch_gate support. |
| rec_picturex0611_folding_table5_var_shelf_spine/rev_000001 | reviewed | used | Fills the frame under the spine with a single fixed shelf and its edge rail. Source for the shelf_spine frame. |
| rec_picturex0611_folding_table5_var_double_shelf_spine/rev_000001 | reviewed | used | Two stacked fixed shelves in the frame instead of one. Source for the double_shelf frame. |
| rec_picturex0611_folding_table5_var_brake_caster_locks/rev_000001 | reviewed | used | Adds a pivoting brake pedal over each caster that swings down onto the tyre. Source for the braked_caster foot. |
| rec_picturex0611_folding_table5_var_four_casters/rev_000001 | reviewed | reference_only | The same caster construction as 003 with the wheel count fixed at four. It is evidence that the caster count is index-general multiplicity on the frame, not a separate structural candidate. |
| rec_picturex0611_folding_table5_var_three_caster_layout_n3/rev_000001 | reviewed | rejected_duplicate | Identical caster construction to the four_casters record with only the count changed, so it produces no distinct candidate beyond the multiplicity already recorded. |
| rec_picturex0611_folding_table5_var_single_drop_leaf_n1/rev_000001 | reviewed | reference_only | Drops one of the two leaves and its gate, leaving a half table. Reviewed as evidence that leaf and support stations are index-general; the rebuilt template keeps both leaves so the deployed top stays round, and carries the count on the per-leaf support instead. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| support_build | swing_gate | leaf support | rec_picturex_0611__folding_table5__001__png_1ac9d775a5de4deaa6918c2b8db999a4/rev_000001 | model.py:L90-L111 | structure+motion | Rod-built rectangular gate swinging on a vertical pivot out from the frame under the raised leaf. |
| support_build | arc_gate | leaf support | rec_picturex0611_folding_table5_var_arc_gate_support/rev_000001 | model.py:L90-L140 | structure | Arched gate whose top rail sweeps up in a curve to meet the leaf underside. |
| support_build | cross_trestle | leaf support | rec_picturex0611_folding_table5_var_folding_cross_trestle_support/rev_000001 | model.py:L60-L140 | structure | Folding cross trestle scissoring out of the spine instead of a single-plane gate. |
| support_build | telescoping_brace | leaf support | rec_picturex0611_folding_table5_var_telescoping_gate_braces/rev_000001 | model.py:L90-L160 | motion | Gate carrying a prismatic brace that telescopes out to lock it at full swing. |
| support_build | wall_bracket | leaf support | rec_picturex0611_folding_table5_var_wall_bracket_arms/rev_000001 | model.py:L70-L150 | structure | Folding bracket arms pivoting straight off the spine, as on a wall-hung drop leaf. |
| support_build | latch_gate | leaf support | rec_picturex0611_folding_table5_var_leaf_locking_latches/rev_000001 | model.py:L90-L170 | structure+motion | Gate paired with a pivoting latch that locks the raised leaf down onto it. |
| frame_build | open_spine | frame carcass | rec_picturex_0611__folding_table5__001__png_1ac9d775a5de4deaa6918c2b8db999a4/rev_000001 | model.py:L125-L214 | structure | Open black steel frame: spine rails, end uprights and floor glides with nothing between them. |
| frame_build | shelf_spine | frame carcass | rec_picturex0611_folding_table5_var_shelf_spine/rev_000001 | model.py:L60-L160 | structure | One fixed shelf with an edge rail filling the frame under the spine. |
| frame_build | double_shelf | frame carcass | rec_picturex0611_folding_table5_var_double_shelf_spine/rev_000001 | model.py:L60-L160 | structure | Two stacked fixed shelves in the frame instead of one. |
| foot_build | fixed_glide | frame foot | rec_picturex_0611__folding_table5__001__png_1ac9d775a5de4deaa6918c2b8db999a4/rev_000001 | model.py:L125-L214 | structure | Small rubber glides under each corner of the foot bars, so the frame stands straight on the floor with no rolling hardware. |
| foot_build | pad_foot | frame foot | rec_picturex_0611__folding_table5__002__png_2402f0a0895c48cfa6267157874c2050/rev_000001 | model.py:L240-L268 | structure | Broad flat pads with a steel bearing plate spreading the load along the foot bar instead of a small point glide. |
| foot_build | swivel_caster | frame foot | rec_picturex_0611__folding_table5__003__png_ef8fdc887f014728a345a684122913c2/rev_000001 | model.py:L90-L135 | structure+motion | Caster plate, swivel stem and fork carrying a wheel: a vertical swivel axis over a horizontal roll axis at each corner, lifting the whole frame onto its wheels. |
| foot_build | braked_caster | frame foot | rec_picturex0611_folding_table5_var_brake_caster_locks/rev_000001 | model.py:L140-L170 | structure+motion | The same caster with a pivoting brake lever whose pad swings down onto the tyre, adding a third joint per corner. |
