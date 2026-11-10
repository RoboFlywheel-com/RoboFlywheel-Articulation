# pictureX_0611_Garden_pruner — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Garden_pruner
picture_category: 0611
picture_subcategory: Garden_pruner

category_scope: A one-handed garden pruner: two handle-and-jaw halves turning on a single main pivot bolt, a return spring that reopens them, a locking catch that holds them shut, and the cutting head at the far end. The single-pivot scissor pair with a return spring and a catch is the category identity; two-stage geared or compound-lever loppers change the whole handle topology and are out of scope.

sync_records:
  - rec_picturex0611_garden_pruner_var_adjustable_stop_screw
  - rec_picturex0611_garden_pruner_var_compound_linkage
  - rec_picturex0611_garden_pruner_var_geared_sector_assist
  - rec_picturex0611_garden_pruner_var_hooked_parrot_beak_blade
  - rec_picturex0611_garden_pruner_var_leaf_spring_return
  - rec_picturex0611_garden_pruner_var_long_bypass_blade
  - rec_picturex0611_garden_pruner_var_pivot_torsion_spring
  - rec_picturex0611_garden_pruner_var_ratchet_lock
  - rec_picturex0611_garden_pruner_var_replaceable_anvil_insert
  - rec_picturex0611_garden_pruner_var_rotating_lower_handle
  - rec_picturex0611_garden_pruner_var_sliding_thumb_lock
  - rec_picturex_0611__garden_pruner__001__png_1fb3fdfcc83c425f8d55bf2dec1bbb57
  - rec_picturex_0611__garden_pruner__002__png_a4fac9c0f0654977b6ccc47b55874c50
  - rec_picturex_0611__garden_pruner__003__png_6cb54782a7e4491aa10f109d158e4131
  - rec_picturex_0611__garden_pruner__004__png_6897c48ac959415388b3b05470fb9720

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__garden_pruner__002__png_a4fac9c0f0654977b6ccc47b55874c50/rev_000001 | reviewed | used | Image-grounded base for 002.png: a pivot boss carrying a curved cutting half and an anvil half, with a prismatic coil spring seat between them, a swinging latch on the anvil handle and a screw adjuster at the pivot. Supplies the bypass_blade head, the coil_seat return and the swing_latch catch. |
| rec_picturex_0611__garden_pruner__003__png_6cb54782a7e4491aa10f109d158e4131/rev_000001 | reviewed | used | Image-grounded base for 003.png: a pivot hub with a cutting half and a hooked parrot-beak counter jaw, a coil return spring and a latch. Supplies the hooked_beak head. |
| rec_picturex_0611__garden_pruner__004__png_6897c48ac959415388b3b05470fb9720/rev_000001 | reviewed | used | Image-grounded base for 004.png: a plate-built pivot frame with two mirrored halves, a captive pivot nut, a spring seat, a screw adjuster and a latch. Supplies the plate_frame handle build. |
| rec_picturex_0611__garden_pruner__001__png_1fb3fdfcc83c425f8d55bf2dec1bbb57/rev_000001 | reviewed | used | Image-grounded base for 001.png: the simplest reading, an anvil half and a blade half on one main pivot with sculpted bezier handle profiles. Supplies the sculpted_grip handle build. |
| rec_picturex0611_garden_pruner_var_hooked_parrot_beak_blade/rev_000001 | reviewed | rejected_duplicate | The same parrot-beak jaw pair as 003.png with only the handle sculpting redone, so it produces no candidate beyond the hooked_beak head already taken from that image. |
| rec_picturex0611_garden_pruner_var_long_bypass_blade/rev_000001 | reviewed | used | Lengthens the bypass blade and its tang into a long slender jaw with a separate cutting-edge solid. Source for the long_bypass head. |
| rec_picturex0611_garden_pruner_var_replaceable_anvil_insert/rev_000001 | reviewed | used | Cuts a seat into the counter jaw and fits a separate replaceable anvil insert into it. Source for the anvil_insert head. |
| rec_picturex0611_garden_pruner_var_pivot_torsion_spring/rev_000001 | reviewed | used | Replaces the coil between the handles with a torsion spring wrapped around the pivot and its own articulated leg. Source for the torsion_coil return. |
| rec_picturex0611_garden_pruner_var_leaf_spring_return/rev_000001 | reviewed | used | Uses a curved leaf spring bearing between the handles instead of a coil. Source for the leaf_spring return. |
| rec_picturex0611_garden_pruner_var_sliding_thumb_lock/rev_000001 | reviewed | used | Replaces the swinging latch with a prismatic thumb slider that shoots a bolt across the handles. Source for the thumb_slider catch. |
| rec_picturex0611_garden_pruner_var_ratchet_lock/rev_000001 | reviewed | used | Adds a pivoting pawl riding a toothed sector so the jaws close in ratcheted steps. Source for the ratchet_pawl catch. |
| rec_picturex0611_garden_pruner_var_adjustable_stop_screw/rev_000001 | reviewed | used | Adds a prismatic stop screw in the frame that limits how far the handles open. Source for the stop_screw catch. |
| rec_picturex0611_garden_pruner_var_rotating_lower_handle/rev_000001 | reviewed | used | Adds a rotating sleeve on the lower handle so the grip turns in the hand. Source for the rotating_sleeve catch station. |
| rec_picturex0611_garden_pruner_var_compound_linkage/rev_000001 | reviewed | reference_only | Adds a compound assist link that turns the single-pivot scissor pair into a two-stage lever train. That is a whole-host topology change rather than a component swap, so it stays a reference for handle proportions only. |
| rec_picturex0611_garden_pruner_var_geared_sector_assist/rev_000001 | reviewed | reference_only | Same two-stage reading with a geared sector instead of a link. It changes the drive topology for the same reason and is kept only as evidence for the sector radius the ratchet pawl rides on. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| head_build | bypass_blade | cutting head | rec_picturex_0611__garden_pruner__002__png_a4fac9c0f0654977b6ccc47b55874c50/rev_000001 | model.py:L133-L335 | structure | Curved bypass blade sweeping past a matching counter jaw, both sculpted from the same pivot boss. |
| head_build | hooked_beak | cutting head | rec_picturex_0611__garden_pruner__003__png_6cb54782a7e4491aa10f109d158e4131/rev_000001 | model.py:L204-L346 | structure | Parrot-beak pair: a hooked counter jaw that traps the stem against the cutting half. |
| head_build | long_bypass | cutting head | rec_picturex0611_garden_pruner_var_long_bypass_blade/rev_000001 | model.py:L92-L167 | structure | Long slender bypass jaw with a separate cutting-edge solid along its whole length. |
| head_build | anvil_insert | cutting head | rec_picturex0611_garden_pruner_var_replaceable_anvil_insert/rev_000001 | model.py:L163-L284 | structure | Flat counter jaw carrying a seated, replaceable anvil insert the blade closes onto. |
| return_build | coil_seat | return spring | rec_picturex_0611__garden_pruner__002__png_a4fac9c0f0654977b6ccc47b55874c50/rev_000001 | model.py:L415-L457 | structure+motion | Coil spring on a prismatic seat between the handles, compressing as they close. |
| return_build | torsion_coil | return spring | rec_picturex0611_garden_pruner_var_pivot_torsion_spring/rev_000001 | model.py:L383-L423 | structure+motion | Torsion spring wrapped around the pivot with its own articulated leg bearing on a handle. |
| return_build | leaf_spring | return spring | rec_picturex0611_garden_pruner_var_leaf_spring_return/rev_000001 | model.py:L143-L277 | structure | Curved leaf spring bearing between the handles instead of a coil. |
| catch_build | swing_latch | locking catch | rec_picturex_0611__garden_pruner__002__png_a4fac9c0f0654977b6ccc47b55874c50/rev_000001 | model.py:L371-L414 | structure+motion | Swinging hook latch on the handle that drops over the other half to hold the jaws shut. |
| catch_build | thumb_slider | locking catch | rec_picturex0611_garden_pruner_var_sliding_thumb_lock/rev_000001 | model.py:L152-L180 | motion | Prismatic thumb slider shooting a bolt across the handles instead of a swinging hook. |
| catch_build | ratchet_pawl | locking catch | rec_picturex0611_garden_pruner_var_ratchet_lock/rev_000001 | model.py:L24-L62 | structure+motion | Pivoting pawl riding a toothed sector so the jaws close in ratcheted steps. |
| catch_build | stop_screw | locking catch | rec_picturex0611_garden_pruner_var_adjustable_stop_screw/rev_000001 | model.py:L24-L62 | motion | Prismatic stop screw in the frame that limits how far the handles open. |
| catch_build | rotating_sleeve | locking catch | rec_picturex0611_garden_pruner_var_rotating_lower_handle/rev_000001 | model.py:L23-L91 | structure+motion | Rotating grip sleeve on the lower handle turning about the handle axis. |
| handle_build | sculpted_grip | handle pair | rec_picturex_0611__garden_pruner__001__png_1fb3fdfcc83c425f8d55bf2dec1bbb57/rev_000001 | model.py:L142-L348 | structure | Bezier-sculpted handle halves with swelling palm bellies and a soft return curve. |
| handle_build | plate_frame | handle pair | rec_picturex_0611__garden_pruner__004__png_6897c48ac959415388b3b05470fb9720/rev_000001 | model.py:L39-L91 | structure | Plate-built handle cores with a separate moulded grip shell wrapped over each. |
