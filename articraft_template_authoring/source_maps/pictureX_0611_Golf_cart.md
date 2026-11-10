# pictureX_0611_Golf_cart — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Golf_cart
picture_category: 0611
picture_subcategory: Golf_cart

category_scope: A four-wheel golf cart: one rigid chassis with a roof-supporting body, two steered front wheels on their own knuckles, two driven rear wheels, a driver control that steers them, foot pedals, a hinged seat over the battery bay, a folding windshield and a cargo bed at the back. The steered-front/driven-rear four-wheel chassis with a folding windshield and a hinged seat is the category identity; two-wheel push trolleys and enclosed utility vehicles are out of scope.

sync_records:
  - rec_picturex0611_golf_cart_var_a_post_canopy
  - rec_picturex0611_golf_cart_var_bucket_seat_pair
  - rec_picturex0611_golf_cart_var_center_fold_windshield
  - rec_picturex0611_golf_cart_var_flatbed_side_rails
  - rec_picturex0611_golf_cart_var_full_width_windshield
  - rec_picturex0611_golf_cart_var_rear_facing_bench
  - rec_picturex0611_golf_cart_var_rear_passenger_bench
  - rec_picturex0611_golf_cart_var_tiller_steering
  - rec_picturex_0611__golf_cart__001__png_3fe1ea57bef642a1a1a0a145a7230265

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__golf_cart__001__png_3fe1ea57bef642a1a1a0a145a7230265/rev_000001 | reviewed | used | Image-grounded base for 001.png: a chassis carrying a two-piece folding windshield, a hinged bench seat, a steering wheel on its column, brake and accelerator pedals, two steered front knuckles with their wheels, two rear wheels and a hinged tailgate. Supplies the split_fold windshield, the bench seat, the wheel_column steering and the tailgate bed. |
| rec_picturex0611_golf_cart_var_center_fold_windshield/rev_000001 | reviewed | used | Splits the screen down the middle into two panels that fold toward each other on a centre hinge instead of folding over horizontally. Source for the center_fold windshield. |
| rec_picturex0611_golf_cart_var_full_width_windshield/rev_000001 | reviewed | used | One full-width screen on a single hinge with no upper leaf. Source for the full_width windshield. |
| rec_picturex0611_golf_cart_var_a_post_canopy/rev_000001 | reviewed | used | Carries the screen on raked A-posts running up to the canopy, changing how the screen meets the body. Source for the a_post_canopy windshield. |
| rec_picturex0611_golf_cart_var_bucket_seat_pair/rev_000001 | reviewed | used | Replaces the single bench with a pair of separately hinged bucket seats. Source for the bucket_pair seat. |
| rec_picturex0611_golf_cart_var_rear_facing_bench/rev_000001 | reviewed | used | Turns the seat around to face the rear over the bed, and drops the tailgate that would block it. Source for the rear_facing seat. |
| rec_picturex0611_golf_cart_var_rear_passenger_bench/rev_000001 | reviewed | used | Adds a raised rear floor with its own seat pedestal, backrest supports, crossbar and pad behind the front row. The raised deck is what distinguishes it: the cushion no longer sits on the chassis bay but on a platform with a step board, so it becomes the rear_deck_row seat candidate rather than a second copy of the front row. |
| rec_picturex0611_golf_cart_var_tiller_steering/rev_000001 | reviewed | used | Replaces the steering wheel and column with a tiller and a separate steering link driving the knuckles. Source for the tiller steering. |
| rec_picturex0611_golf_cart_var_flatbed_side_rails/rev_000001 | reviewed | used | Replaces the tailgate box with an open flatbed and side rails. Source for the flatbed bed. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| screen_build | split_fold | windshield | rec_picturex_0611__golf_cart__001__png_3fe1ea57bef642a1a1a0a145a7230265/rev_000001 | model.py:L60-L200 | structure+motion | Two-piece screen: a fixed lower leaf on a mount and an upper leaf that folds over it. |
| screen_build | center_fold | windshield | rec_picturex0611_golf_cart_var_center_fold_windshield/rev_000001 | model.py:L60-L200 | structure+motion | Screen split down the middle into left and right panels folding toward each other. |
| screen_build | full_width | windshield | rec_picturex0611_golf_cart_var_full_width_windshield/rev_000001 | model.py:L60-L200 | structure | One full-width screen on a single hinge with no upper leaf. |
| seat_build | bench | seat | rec_picturex_0611__golf_cart__001__png_3fe1ea57bef642a1a1a0a145a7230265/rev_000001 | model.py:L200-L340 | structure | One full-width hinged bench cushion over the battery bay. |
| seat_build | bucket_pair | seat | rec_picturex0611_golf_cart_var_bucket_seat_pair/rev_000001 | model.py:L200-L360 | structure | Two separately hinged bucket cushions with a console gap between them. |
| seat_build | rear_facing | seat | rec_picturex0611_golf_cart_var_rear_facing_bench/rev_000001 | model.py:L200-L340 | structure | Bench turned to face the rear over the bed, with its backrest at the front edge. |
| steer_build | wheel_column | steering | rec_picturex_0611__golf_cart__001__png_3fe1ea57bef642a1a1a0a145a7230265/rev_000001 | model.py:L340-L470 | structure+motion | Dished steering wheel on a raked column driving both knuckles. |
| steer_build | tiller | steering | rec_picturex0611_golf_cart_var_tiller_steering/rev_000001 | model.py:L340-L500 | structure+motion | Upright tiller with a separate steering link that drives the knuckles. |
| bed_build | tailgate | cargo bed | rec_picturex_0611__golf_cart__001__png_3fe1ea57bef642a1a1a0a145a7230265/rev_000001 | model.py:L470-L560 | structure+motion | Boxed cargo bed closed by a hinged drop tailgate. |
| bed_build | flatbed | cargo bed | rec_picturex0611_golf_cart_var_flatbed_side_rails/rev_000001 | model.py:L470-L560 | structure | Open flatbed deck with side rails instead of a tailgate box. |
| canopy_build | cowl_post_canopy | canopy support | rec_picturex_0611__golf_cart__001__png_3fe1ea57bef642a1a1a0a145a7230265/rev_000001 | model.py:L150-L205 | structure | The canopy's front edge stands on a pair of vertical posts rising off the cowl behind the windshield. |
| canopy_build | a_post_canopy | canopy support | rec_picturex0611_golf_cart_var_a_post_canopy/rev_000001 | model.py:L150-L215 | structure | The vertical front posts are replaced by raked A-posts ahead of the windshield, tied together by a crossbar under the canopy's front edge. |
| seat_build | rear_deck_row | seat module | rec_picturex0611_golf_cart_var_rear_passenger_bench/rev_000001 | model.py:L120-L190 | structure | The cushion sits on its own raised rear deck with a step board at its front instead of directly on the chassis bay, so the whole row rides higher. |
