# pictureX_0611_Industrial_rolling_work_table — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Industrial_rolling_work_table
picture_category: 0611
picture_subcategory: Industrial_rolling_work_table
category_scope: Mobile industrial work tables: a welded post-and-rail frame carrying one full-footprint worktop and four braked swivel casters, with a storage module (open shelves, a drawer bank or a pegboard rack) under or beside the top; static benches, hand trolleys, tool chests without a worktop and shop carts without casters are not candidates.

sync_records:
  - rec_industrial_rolling_work_table_var_adjustable_height
  - rec_industrial_rolling_work_table_var_drawer_cabinet
  - rec_industrial_rolling_work_table_var_pegboard_rack_refill
  - rec_picturex_0611__industrial_rolling_work_table__001__png_f858cd8fba4c466aa560b397ff1bf275
  - rec_picturex_0611__industrial_rolling_work_table__002__png_734e7a01404e4b83b5986c0a30093445
  - rec_picturex_0611__industrial_rolling_work_table__003__png_8d72ded99b91405e97f6507d3115c6b9
  - rec_picturex_0611__industrial_rolling_work_table__004__png_d11cca56695549bb9bda9bfd813476e2

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__industrial_rolling_work_table__001__png_f858cd8fba4c466aa560b397ff1bf275/rev_000001 | reviewed | used | Origin: a stainless post-and-rail frame with a full-footprint top and an undershelf, on four yoke casters whose wheel and brake pedal are separate articulated parts. |
| rec_picturex_0611__industrial_rolling_work_table__003__png_8d72ded99b91405e97f6507d3115c6b9/rev_000001 | reviewed | used | Origin: the same rolling frame carrying a thick laminated wood top with a rounded edge instead of a steel deck. |
| rec_picturex_0611__industrial_rolling_work_table__002__png_734e7a01404e4b83b5986c0a30093445/rev_000001 | reviewed | used | Workstation origin: the rear display arm with its own tilt joint, the pull-out keyboard tray on side runners and the fixed equipment module are the reusable bench accessories. |
| rec_picturex_0611__industrial_rolling_work_table__004__png_d11cca56695549bb9bda9bfd813476e2/rev_000001 | reviewed | used | Only the bracing family is reused: prominent crossed flat bars fill each side bay between the posts, which the plain-railed origins do not have. |
| rec_industrial_rolling_work_table_var_drawer_cabinet/rev_000001 | reviewed | used | Only the storage family is reused: a stack of hollow drawer trays with bilateral runners, a front face and a pull. |
| rec_industrial_rolling_work_table_var_pegboard_rack_refill/rev_000001 | reviewed | used | Only the storage family is reused: a perforated pegboard back panel with hooks over a sliding tray. |
| rec_industrial_rolling_work_table_var_adjustable_height/rev_000001 | reviewed | used | Only the leg family is reused: telescoping inner and outer posts with a locking collar and a real prismatic travel. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| top_surface | stainless_deck | folded steel deck | rec_picturex_0611__industrial_rolling_work_table__001__png_f858cd8fba4c466aa560b397ff1bf275/rev_000001 | model.py:L38-L143 | structure | The deck is a thin stainless panel with a turned-down edge skirt over the perimeter rails. |
| top_surface | butcher_block | laminated wood slab | rec_picturex_0611__industrial_rolling_work_table__003__png_8d72ded99b91405e97f6507d3115c6b9/rev_000001 | model.py:L59-L73 | structure | A thick laminated slab with visible glue lines and a rounded edge replaces the steel deck. |
| storage_module | open_shelf | open undershelf levels | rec_picturex_0611__industrial_rolling_work_table__003__png_8d72ded99b91405e97f6507d3115c6b9/rev_000001 | model.py:L96-L202 | structure | Full-footprint shelf panels sit on the lower rails between the four posts. |
| storage_module | drawer_bank | hollow drawer stack | rec_industrial_rolling_work_table_var_drawer_cabinet/rev_000001 | model.py:L156-L217 | structure+motion | Each drawer is a real open tray with side runners, a front face and a pull, sliding out of the cabinet. |
| storage_module | pegboard_rack | pegboard back with trays | rec_industrial_rolling_work_table_var_pegboard_rack_refill/rev_000001 | model.py:L65-L180 | structure | A perforated back panel with hooks stands over the frame and carries sliding trays instead of a closed cabinet. |
| side_bracing | plain_rails | open rail-only sides | rec_picturex_0611__industrial_rolling_work_table__001__png_f858cd8fba4c466aa560b397ff1bf275/rev_000001 | model.py:L38-L143 | structure | The side bays are left open between the perimeter rails, with no diagonal member. |
| side_bracing | x_braces | crossed flat side braces | rec_picturex_0611__industrial_rolling_work_table__004__png_d11cca56695549bb9bda9bfd813476e2/rev_000001 | model.py:L102-L124 | structure | Two crossed flat bars fill each side bay, set at the bay's own diagonal angle. |
| bench_accessory | monitor_arm | tilting display arm | rec_picturex_0611__industrial_rolling_work_table__002__png_734e7a01404e4b83b5986c0a30093445/rev_000001 | model.py:L206-L245 | structure+motion | A yoke on a tilt barrel carries a display shell that swings on its own horizontal axis above the bench. |
| bench_accessory | keyboard_tray | pull-out keyboard tray | rec_picturex_0611__industrial_rolling_work_table__002__png_734e7a01404e4b83b5986c0a30093445/rev_000001 | model.py:L246-L293 | structure+motion | A lipped pan hangs under the bench on two side runners and pulls out toward the operator. |
| bench_accessory | equipment_shelf | fixed equipment module | rec_picturex_0611__industrial_rolling_work_table__002__png_734e7a01404e4b83b5986c0a30093445/rev_000001 | model.py:L326-L348 | structure | A closed equipment box is fixed on the bench instead of a moving accessory. |
| leg_form | fixed_post | welded fixed posts | rec_picturex_0611__industrial_rolling_work_table__001__png_f858cd8fba4c466aa560b397ff1bf275/rev_000001 | model.py:L38-L143 | structure | Four square posts are welded to the perimeter rails at a fixed working height. |
| leg_form | telescopic_post | telescoping adjustable posts | rec_industrial_rolling_work_table_var_adjustable_height/rev_000001 | model.py:L80-L119 | structure+motion | An inner post slides in an outer post captured by a locking collar, giving a real height travel. |

## Component evidence

- The braked swivel caster is identity-fixed host structure in every reviewed source
  (`rec_picturex_0611__industrial_rolling_work_table__001__png_f858cd8fba4c466aa560b397ff1bf275/rev_000001`
  `model.py:L144-L199` for the yoke and brake pedal), so it is not a slot: every seed keeps four
  casters with a vertical swivel, a horizontal wheel spin and a pedal.
- Storage level multiplicity comes from the loop-emitted stacks in
  `rec_industrial_rolling_work_table_var_drawer_cabinet/rev_000001` `model.py:L334-L378` and
  `rec_industrial_rolling_work_table_var_pegboard_rack_refill/rev_000001` `model.py:L181-L258`.
