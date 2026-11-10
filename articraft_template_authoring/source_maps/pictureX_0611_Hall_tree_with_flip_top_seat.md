# pictureX_0611_Hall_tree_with_flip_top_seat — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Hall_tree_with_flip_top_seat
picture_category: 0611
picture_subcategory: Hall_tree_with_flip-top_seat
category_scope: A floor-standing entryway hall tree whose bench top flips up on a rear-edge hinge. The fixed category identity is a plinth-borne lower carcass, a bench seat hinged along its rear edge, and a tall back tower rising above the seat between two side cheeks. Everything under the seat (drawers, a door cabinet, or a bare storage well), everything on the tower above it (cubbies, a mirror, a hook rail, a framed board) and the case's own base/crown dress (stepped plinth, recessed toe kick, flush base) is a component swap on that one host. Wall-hung racks that delete the plinth and stand on cleats, and benches with no tall tower, are outside this category.

sync_records:
  - rec_picturex0611_hall_tree_var_closed_mirror_panel
  - rec_picturex0611_hall_tree_var_six_drawers
  - rec_picturex0611_hall_tree_var_six_hooks
  - rec_picturex0611_hall_tree_var_three_cubbies
  - rec_picturex0611_hall_tree_var_true_flip_seat
  - rec_picturex0611_hall_tree_var_two_drawers
  - rec_picturex0611_hall_tree_var_wall_mounted_rack
  - rec_picturex_0611__hall_tree_with_flip_top_seat__001__png_6ebe988b7462418e94a01da45437d165
  - rec_picturex_0611__hall_tree_with_flip_top_seat__002__png_c51775fc3eee486f828d6ebce6a354b4
  - rec_picturex_0611__hall_tree_with_flip_top_seat__003__png_0907115181d64307bf5265cba86c4e24

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__hall_tree_with_flip_top_seat__001__png_6ebe988b7462418e94a01da45437d165/rev_000001 | reviewed | used | Image-grounded base for 001.png: one painted carcass with a stepped plinth, a four-bay drawer face frame under the seat, tall side cheeks, a cubby floor/top with three dividers and a broad crown. Supplies the drawer_bank lower build, the open_cubbies tower and the flush_base_crown case dress (base flush with the carcass, one broad deep crown board, applied stiles up the tall sides). Its own seat is modelled fixed; the flip hinge comes from the true_flip_seat revision below. |
| rec_picturex_0611__hall_tree_with_flip_top_seat__002__png_c51775fc3eee486f828d6ebce6a354b4/rev_000001 | reviewed | used | Image-grounded base for 002.png: a narrower frame with drawer runners rising off the cabinet bottom, rear seat ledgers that carry the closed flip-top, and a plain tall back with an applied board frame instead of cubbies. Source for the framed_board tower, for the toe_kick_rail case dress (a shallow front-only plinth board set back under the case, applied front stiles and a single thin crown rail with no overhang) and for the seat-ledger/runner construction the host reuses. |
| rec_picturex_0611__hall_tree_with_flip_top_seat__003__png_0907115181d64307bf5265cba86c4e24/rev_000001 | reviewed | used | Image-grounded base for 003.png: a narrow white hall tree whose lower carcass is closed by a single overlay barn door on strap hinges with an interior shelf, above a dark flip seat and an open cubby bay. Source for the door_cabinet lower build and for the stepped_plinth_crown case dress (a broad plinth stepping out past the carcass on all four sides under a two-piece crown board plus wider cap). |
| rec_picturex0611_hall_tree_var_true_flip_seat/rev_000001 | reviewed | used | Replaces the fixed 001 slab with a walnut seat hinged along its rear edge on two barrel hinges, and hollows the zone under it into a walled storage well (floor, front/rear/side walls) instead of drawer boxes. Source for the seat_bin lower build and for the rear-edge flip hinge that defines the category. |
| rec_picturex0611_hall_tree_var_closed_mirror_panel/rev_000001 | reviewed | used | Keeps the 003 carcass and door but closes the tower's open bay with a framed mirror glass panel and flanking hook rails. Source for the mirror_panel tower. |
| rec_picturex0611_hall_tree_var_six_hooks/rev_000001 | reviewed | used | Drops the cubby-aligned hook pattern for a dedicated lower back hook rail carrying six evenly spaced double-prong J hooks inset from each end. Source for the hook_rail tower and for the even-spacing rule the multiplicity slot uses. |
| rec_picturex0611_hall_tree_var_three_cubbies/rev_000001 | reviewed | used | Same 003 carcass with the tower bay divided into three cubbies by two dividers on a derived equal-width rule. Source for bay_count=3 and evidence that the divider count is a multiplicity of one mechanism, not a separate tower. |
| rec_picturex0611_hall_tree_var_six_drawers/rev_000001 | reviewed | reference_only | Same 001 carcass and same drawer construction with the face frame re-cut into six equal bays on a derived spacing rule (`bay_spacing = 1.084 / num_drawers`), so the fronts, trays and pulls all shrink with the count. It is evidence that the bay count is a multiplicity of the drawer_bank mechanism rather than a separate lower build, and it fixes the upper end of that multiplicity's range. |
| rec_picturex0611_hall_tree_var_two_drawers/rev_000001 | reviewed | reference_only | Same 002 carcass with the same runners and ledgers, re-cut into two wide full-height bays and losing only the horizontal mid-rail. Together with six_drawers it brackets the bay-count multiplicity — a bay's front width follows from the count, so neither end is a distinct component. |
| rec_picturex0611_hall_tree_var_wall_mounted_rack/rev_000001 | reviewed | reference_only | Deletes the plinth and both floor-standing side panels and hangs the whole assembly on two wall cleats. Nothing under the seat remains to swap and the load path inverts from floor-borne to wall-borne, so this is a whole-host topology change rather than a component swap on the hall-tree host. Reviewed for its cleat/shelf proportions, which informed the rear seat-ledger depth, but it does not become a candidate. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| lower_build | drawer_bank | under-seat storage | rec_picturex_0611__hall_tree_with_flip_top_seat__001__png_6ebe988b7462418e94a01da45437d165/rev_000001 | model.py:L127-L215 | structure+motion | Face-frame dividers with a prismatic drawer per bay: shaker front, open tray box and a bar pull, sliding out of the carcass on runners. |
| lower_build | door_cabinet | under-seat storage | rec_picturex_0611__hall_tree_with_flip_top_seat__003__png_0907115181d64307bf5265cba86c4e24/rev_000001 | model.py:L87-L120, L227-L300 | structure+motion | A single overlay barn door on strap-hinge knuckles swinging on a vertical axis, closing one tall cavity with a fixed interior shelf, instead of drawer boxes. |
| lower_build | seat_bin | under-seat storage | rec_picturex0611_hall_tree_var_true_flip_seat/rev_000001 | model.py:L161-L234 | structure | A walled well (floor, front/rear/side walls) directly under the seat with no independent moving storage — the flip seat itself is the only access. |
| upper_build | open_cubbies | tower treatment | rec_picturex0611_hall_tree_var_three_cubbies/rev_000001 | model.py:L278-L300 | structure | Cubby floor and top boards closed by vertical dividers on a derived equal-width rule, leaving open pigeonholes across the tower. |
| upper_build | mirror_panel | tower treatment | rec_picturex0611_hall_tree_var_closed_mirror_panel/rev_000001 | model.py:L172-L246 | structure | The bay is closed by a glass panel held in an applied surround, with hook rails moved to the flanks. |
| upper_build | hook_rail | tower treatment | rec_picturex0611_hall_tree_var_six_hooks/rev_000001 | model.py:L70-L100, L177-L200 | structure | A dedicated horizontal rail across the lower tower carrying double-prong J hooks on an even inset spacing, with the bay left fully open. |
| upper_build | framed_board | tower treatment | rec_picturex_0611__hall_tree_with_flip_top_seat__002__png_c51775fc3eee486f828d6ebce6a354b4/rev_000001 | model.py:L91-L164 | structure | A plain tall back closed by an applied stile-and-rail board frame with a recessed centre field and no shelf, mirror or hook hardware. |
| case_dress | stepped_plinth_crown | case base and crown | rec_picturex_0611__hall_tree_with_flip_top_seat__003__png_0907115181d64307bf5265cba86c4e24/rev_000001 | model.py:L175-L195, L290-L306 | structure | Broad base plinth stepping out past the carcass on all four sides, closed at the top by a crown board with a wider cap over it. |
| case_dress | toe_kick_rail | case base and crown | rec_picturex_0611__hall_tree_with_flip_top_seat__002__png_c51775fc3eee486f828d6ebce6a354b4/rev_000001 | model.py:L66-L107 | structure | Front-only plinth board set back under the carcass as a recessed toe kick, applied stiles on the front edges, and one thin crown rail flush with the sides. |
| case_dress | flush_base_crown | case base and crown | rec_picturex_0611__hall_tree_with_flip_top_seat__001__png_6ebe988b7462418e94a01da45437d165/rev_000001 | model.py:L117-L140 | structure | Base flush with the carcass face and no step, under a single broad deep crown board with applied stiles running up the tall sides.
