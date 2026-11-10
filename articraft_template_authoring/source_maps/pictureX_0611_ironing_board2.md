# pictureX_0611_ironing_board2 — SourceMap

source_map_schema: 1
export_category: pictureX_0611_ironing_board2
picture_category: 0611
picture_subcategory: ironing_board2
category_scope: A domestic ironing board — one padded ironing top plus the support that holds it at working height and folds away. Garment steamers, laundry racks and fixed pressing tables without a folding or adjustable support are outside this host.

sync_records:
  - rec_ironing_board2_var_sleeve_board_refill
  - rec_ironing_board2_var_t_leg_height_adjust_refill
  - rec_ironing_board2_var_tabletop_short_legs_refill
  - rec_ironing_board2_var_wall_mount_fold_down_refill
  - rec_ironing_board2_var_x_leg_floor
  - rec_picturex_0611__ironing_board2__001__png_20c3543235f84c8c9cdc02c21fc7b567
  - rec_picturex_0611__ironing_board2__002__png_a42c994617f44685ada679afd555e0ef

All records are read at `revisions/rev_000001/model.py`.

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_ironing_board2_var_sleeve_board_refill/rev_000001 | reviewed | used | Adds a full second ironing surface — a `sleeve_board` part on its own REVOLUTE joint about the board's long axis — on top of the standard board. Distinct top assembly. |
| rec_ironing_board2_var_t_leg_height_adjust_refill/rev_000001 | reviewed | used | Replaces the folding leg frames with two telescoping `support_post_i` on PRISMATIC joints plus `lock_collar_i` twist locks. Distinct support family with a different joint type. |
| rec_ironing_board2_var_tabletop_short_legs_refill/rev_000001 | reviewed | used | Short tabletop legs whose lock braces hinge on the board rather than on the leg. Distinct support family. |
| rec_ironing_board2_var_wall_mount_fold_down_refill/rev_000001 | reviewed | used | Drops the legs entirely: a `wall_bracket` carries the board on a fold-down hinge and a separate `support_arm` props it. Distinct support family. |
| rec_ironing_board2_var_x_leg_floor/rev_000001 | reviewed | used | A compact freestanding X-leg base with the braces hinged on the board and long floor-reaching legs. Distinct support family. |
| rec_picturex_0611__ironing_board2__001__png_20c3543235f84c8c9cdc02c21fc7b567/rev_000001 | reviewed | used | Origin anchor: a tapered capsule board with a perforated tray and cover, on scissor leg frames whose lock braces hinge on the legs themselves. |
| rec_picturex_0611__ironing_board2__002__png_a42c994617f44685ada679afd555e0ef/rev_000001 | reviewed | used | Second origin: a rectangular slotted board with a perforated pan and elliptical patches — a different top construction from 001's capsule. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| board_style | tapered_capsule | ironing top | rec_picturex_0611__ironing_board2__001__png_20c3543235f84c8c9cdc02c21fc7b567/rev_000001 | model.py:L26-L131 | structure | `_capsule` sweeps a rounded, tapering silhouette, `_perforated_tray` builds the vented underside and `_cover_pattern` the padded cover — the classic narrowing board. |
| board_style | rect_slotted | ironing top | rec_picturex_0611__ironing_board2__002__png_a42c994617f44685ada679afd555e0ef/rev_000001 | model.py:L29-L132 | structure | `_slot_solid` plus `_perforated_pan` and `_ellipse_patch` build a straight-sided slotted pan; the top keeps a constant width instead of tapering. |
| sleeve_option | plain_top | ironing surface set | rec_picturex_0611__ironing_board2__001__png_20c3543235f84c8c9cdc02c21fc7b567/rev_000001 | model.py:L26-L131 | structure | The origin top is a single ironing surface with no second board. |
| sleeve_option | sleeve_board | ironing surface set | rec_ironing_board2_var_sleeve_board_refill/rev_000001 | model.py:L326-L461 | structure+motion | A second `sleeve_board` surface with its own pad and end cap swings up on a REVOLUTE joint about the long axis (L444-L461); the hinge posts stand on the retained main top, so the sleeve is an added surface rather than a different top construction. |
| support_style | scissor_legs | board support | rec_picturex_0611__ironing_board2__001__png_20c3543235f84c8c9cdc02c21fc7b567/rev_000001 | model.py:L176-L323 | structure+motion | Two `leg_frame_i` hinge under the board (L219-L233) and each carries its own `lock_brace_i` hinged on the leg (L284-L298): a true scissor pair. |
| support_style | floor_x_legs | board support | rec_ironing_board2_var_x_leg_floor/rev_000001 | model.py:L257-L388 | structure+motion | Long floor-reaching crossed legs whose braces hinge on the **board** (L374-L388) instead of on the leg, giving a different closed loop. |
| support_style | short_tabletop_legs | board support | rec_ironing_board2_var_tabletop_short_legs_refill/rev_000001 | model.py:L255-L365 | structure | Short legs sized to stand the board on a tabletop, with board-mounted braces; the whole support is a fraction of the standing height. |
| support_style | telescoping_posts | board support | rec_ironing_board2_var_t_leg_height_adjust_refill/rev_000001 | model.py:L245-L345 | structure+motion | Two `support_post_i` on PRISMATIC height joints (L290-L307) with T crossbars and `lock_collar_i` twist locks (L328-L345): no folding leg at all. |
| support_style | wall_bracket | board support | rec_ironing_board2_var_wall_mount_fold_down_refill/rev_000001 | model.py:L233-L321, model.py:L419-L510 | structure+motion | A `wall_bracket` back plate carries the board on a fold-down REVOLUTE hinge (L473-L490) and a `support_arm` props it from the same bracket (L493-L510); the board never reaches the floor. |

## Coverage note

All seven active records in the `0611 / ironing_board2` workbench pool are reviewed and all seven
contribute a candidate. The sleeve fork keeps the origin capsule top untouched and only adds a second
hinged surface on top of it, so the sleeve is its own slot rather than a third top construction, and it
mounts on the slotted pan just as well as on the capsule.

`core_domain = 2 (board_style) x 2 (sleeve_option) x 5 (support_style) = 20`; there is no honest
multiplicity, because every source uses exactly two support stations.
