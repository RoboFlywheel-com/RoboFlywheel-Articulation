# pictureX_0611_full_height_turnstile — SourceMap

source_map_schema: 1
export_category: pictureX_0611_full_height_turnstile
picture_category: 0611
picture_subcategory: full_height_turnstile
category_scope: A full-height security turnstile — one grounded galvanized guard structure that carries a floor bearing and an overhead bearing, plus one full-height multi-wing rotor that spins about the vertical spindle between them, with the usual access-control hardware and an optional second mechanism. Waist-high tripod turnstiles, revolving doors with glazed panels and multi-lane banks are outside this host.

sync_records:
  - rec_picturex0611_full_height_turnstile_var_arched_header_frame
  - rec_picturex0611_full_height_turnstile_var_card_reader_post
  - rec_picturex0611_full_height_turnstile_var_cylindrical_guard_cage
  - rec_picturex0611_full_height_turnstile_var_emergency_breakaway_wing
  - rec_picturex0611_full_height_turnstile_var_four_wing_rotor
  - rec_picturex0611_full_height_turnstile_var_guard_upright_n8
  - rec_picturex0611_full_height_turnstile_var_locking_pawl_hub
  - rec_picturex0611_full_height_turnstile_var_overhead_indexing_cam
  - rec_picturex0611_full_height_turnstile_var_rotor_tier_n6
  - rec_picturex0611_full_height_turnstile_var_rotor_tier_n8
  - rec_picturex0611_full_height_turnstile_var_rotor_vertical_bar_n6
  - rec_picturex_0611__full_height_turnstile__001__png_6b7e15d6e87242ac98409635abccc39b
  - rec_picturex_0611__full_height_turnstile__002__png_da54abc7e8844e8599f629d58357b56e
  - rec_picturex_0611__full_height_turnstile__003__png_1ffe2f2c8ebd43499f4e65e482fe1601
  - rec_picturex_0611__full_height_turnstile__004__png_104746ac4b87457a9090aff843d68651

All records are read at `revisions/rev_000001/model.py`.

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex0611_full_height_turnstile_var_arched_header_frame/rev_000001 | reviewed | used | Adds a real double-rib circular arch springing off two side posts above the 003 guard cage, with cap plates and a split header crossbeam that clears the upper bearing. Distinct header family. |
| rec_picturex0611_full_height_turnstile_var_card_reader_post/rev_000001 | reviewed | used | Moves the access control off the portal onto a free-standing outboard post with its own base, cap, reader housing, screen, LED, conduit and welded brackets/gussets. Distinct access-control component. |
| rec_picturex0611_full_height_turnstile_var_cylindrical_guard_cage/rev_000001 | reviewed | used | Fills the arc between the structural posts of the 003 cage with a dense ring of intermediate vertical cage bars, making the guard read as a closed cylindrical cage. Distinct guard family. |
| rec_picturex0611_full_height_turnstile_var_emergency_breakaway_wing/rev_000001 | reviewed | used | Splits the third rotor wing off into its own `breakaway_wing` part on a second REVOLUTE that folds it toward the spindle, with a hinge stile and a red release marker. Distinct second mechanism. |
| rec_picturex0611_full_height_turnstile_var_four_wing_rotor/rev_000001 | reviewed | reference_only | Same rotor construction as 001 with `wing_count=4`; it is N evidence that the wing loop is index-general, not a separate structural candidate. |
| rec_picturex0611_full_height_turnstile_var_guard_upright_n8/rev_000001 | reviewed | reference_only | Same guard construction as 001 with eight uprights instead of five; N evidence for the repeated guard-member count, not a separate structural candidate. |
| rec_picturex0611_full_height_turnstile_var_locking_pawl_hub/rev_000001 | reviewed | used | Adds a CadQuery toothed ratchet ring at the rotor base and a separate `pawl` lever part on its own horizontal REVOLUTE that lifts its tip out of the teeth. Distinct second mechanism. |
| rec_picturex0611_full_height_turnstile_var_overhead_indexing_cam/rev_000001 | reviewed | used | Adds an overhead eccentric-lobe `index_cam` mimic-driven from the rotor plus an `index_roller_arm` follower on a horizontal REVOLUTE inside a cast indexer shell. Distinct second mechanism. |
| rec_picturex0611_full_height_turnstile_var_rotor_tier_n6/rev_000001 | reviewed | reference_only | Same curved ladder rotor as 004 with six bar tiers per wing; N evidence for the tier loop, not a separate structural candidate. |
| rec_picturex0611_full_height_turnstile_var_rotor_tier_n8/rev_000001 | reviewed | reference_only | Same curved ladder rotor as 004 with eight bar tiers per wing; N evidence for the tier loop, not a separate structural candidate. |
| rec_picturex0611_full_height_turnstile_var_rotor_vertical_bar_n6/rev_000001 | reviewed | used | Replaces the horizontal arm ladder with a palisade of vertical bars spanning each wing between a top and bottom rail. Distinct rotor family. |
| rec_picturex_0611__full_height_turnstile__001__png_6b7e15d6e87242ac98409635abccc39b/rev_000001 | reviewed | used | Origin anchor: rectangular four-post portal with base rails, a boxy overhead drive housing, a horizontal-arm three-wing rotor, a post-mounted reader enclosure and a hinged framed service guard leaf on its own REVOLUTE. |
| rec_picturex_0611__full_height_turnstile__002__png_da54abc7e8844e8599f629d58357b56e/rev_000001 | reviewed | used | Second origin: the same portal skeleton but infilled with horizontal side bars between the posts and a braced rotor whose wings carry an outer wing post plus lower/top braces. |
| rec_picturex_0611__full_height_turnstile__003__png_1ffe2f2c8ebd43499f4e65e482fe1601/rev_000001 | reviewed | used | Third origin: a curved welded guard of arc rails on five uprights under a round overhead drive housing, annular CadQuery bearings, a bracket-mounted reader with keypad, and a rotor of full-height wing stiles with horizontal rungs. |
| rec_picturex_0611__full_height_turnstile__004__png_104746ac4b87457a9090aff843d68651/rev_000001 | reviewed | used | Fourth origin: twin curved spline-tube guard panels with dense rails and heavy/light uprights under a folded sheet header carrying indicator bezels and lenses, plus a curved-bar ladder rotor with stiles and braces. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| guard_frame | portal_post_frame | fixed guard structure | rec_picturex_0611__full_height_turnstile__001__png_6b7e15d6e87242ac98409635abccc39b/rev_000001 | model.py:L60-L98 | structure | Four square corner posts on a rectangular base-rail perimeter under a boxy `drive_housing`, with `floor_bearing`, `top_bearing` and `floor_pivot_plate` on the spindle line; the lane sides are left open. |
| guard_frame | barred_portal_frame | fixed guard structure | rec_picturex_0611__full_height_turnstile__002__png_da54abc7e8844e8599f629d58357b56e/rev_000001 | model.py:L87-L233 | structure | The same portal skeleton but with `side_bar_{side}_{bar}` horizontal infill between the posts and top rails, plus a `top_housing`/`front_fascia` pair and `_bearing_ring` CadQuery races. |
| guard_frame | arc_rail_cage | fixed guard structure | rec_picturex_0611__full_height_turnstile__003__png_1ffe2f2c8ebd43499f4e65e482fe1601/rev_000001 | model.py:L82-L194 | structure | A curved guard swept from `_add_tube_between` arc segments on five box uprights with feet, tied to the spindle by three floor braces under a round `overhead_housing` and true `_annulus` bearing races. |
| guard_frame | cylindrical_bar_cage | fixed guard structure | rec_picturex0611_full_height_turnstile_var_cylindrical_guard_cage/rev_000001 | model.py:L152-L166 | structure | The arc cage is closed into a cylinder by `cage_bar_{i}` intermediate vertical bars filling every non-structural arc station between the posts. |
| guard_frame | curved_panel_cage | fixed guard structure | rec_picturex_0611__full_height_turnstile__004__png_104746ac4b87457a9090aff843d68651/rev_000001 | model.py:L55-L187 | structure | Two opposed spline-tube curved rail panels, each on heavy/light alternating uprights, under a folded sheet `header_body`/`header_cap` and carried on a low `floor_mount_rail` with a `pivot_floor_plate`. |
| header_form | flat_header | overhead header | rec_picturex_0611__full_height_turnstile__002__png_da54abc7e8844e8599f629d58357b56e/rev_000001 | model.py:L173-L186 | structure | The overhead mechanism sits in a flat slab housing with a front fascia directly on top of the guard structure. |
| header_form | arched_header | overhead header | rec_picturex0611_full_height_turnstile_var_arched_header_frame/rev_000001 | model.py:L97-L180 | structure | Two parallel circular `arch_rib_{rib}_{seg}` ribs with lateral ties spring from `arch_post_{side}` posts through `arch_cap_plate_{side}`, and the header crossbeam is split to clear the upper bearing. |
| rotor_form | arm_tier_rotor | rotating rotor | rec_picturex_0611__full_height_turnstile__001__png_6b7e15d6e87242ac98409635abccc39b/rev_000001 | model.py:L102-L141 | structure | Each wing is a horizontal arm ladder: `arm_{wing}_{level}` tubes cantilevered off the spindle, closed by a full-height `wing_{wing}_tip` post and a `wing_{wing}_lower_cap`. |
| rotor_form | braced_arm_rotor | rotating rotor | rec_picturex_0611__full_height_turnstile__002__png_da54abc7e8844e8599f629d58357b56e/rev_000001 | model.py:L235-L299 | structure | The arm ladder gains a heavier outer `wing_post_{wing}` and two diagonal-level `lower_brace`/`top_brace` members per wing, so the wing reads as a braced frame rather than free arms. |
| rotor_form | stile_rung_rotor | rotating rotor | rec_picturex_0611__full_height_turnstile__003__png_1ffe2f2c8ebd43499f4e65e482fe1601/rev_000001 | model.py:L244-L292 | structure | Each wing is a welded ladder between the spindle and a `wing_stile_{wing}` outer post, with `rotor_bar_{wing}_{bar}` rungs built as real tubes between the two. |
| rotor_form | curved_bar_rotor | rotating rotor | rec_picturex_0611__full_height_turnstile__004__png_104746ac4b87457a9090aff843d68651/rev_000001 | model.py:L189-L237 | structure | The rotor wing is a dense stack of `wing_{i}_bar_{j}` rails between the spindle and a `wing_{i}_stile`, with `wing_{i}_brace_{k}` diagonals — the curved-cage counterpart of the ladder rotor. |
| rotor_form | vertical_bar_rotor | rotating rotor | rec_picturex0611_full_height_turnstile_var_rotor_vertical_bar_n6/rev_000001 | model.py:L103-L147 | structure | The wing is a palisade: vertical bars spanning between a bottom and top wing rail instead of horizontal arms, so the visible grain of the barrier is rotated 90 degrees. |
| access_control | post_reader_box | access control | rec_picturex_0611__full_height_turnstile__001__png_6b7e15d6e87242ac98409635abccc39b/rev_000001 | model.py:L86-L98 | structure | A compact `access_box` enclosure clamped to the entry post with a `reader_face`, an indicator strip and a fastener. |
| access_control | bracket_reader_keypad | access control | rec_picturex_0611__full_height_turnstile__003__png_1ffe2f2c8ebd43499f4e65e482fe1601/rev_000001 | model.py:L195-L242 | structure | A `reader_bracket` stands the reader off the entry upright on the guard radius, and the reader carries a separate `reader_keypad` plate. |
| access_control | standalone_reader_post | access control | rec_picturex0611_full_height_turnstile_var_card_reader_post/rev_000001 | model.py:L210-L300 | structure | A free-standing `access_post` with base and cap outboard of the guard, carrying a `card_reader_housing`, screen and LED, a `conduit` down to the floor and `post_bracket_{i}`/`post_gusset_{i}` ties back to the frame. |
| access_control | header_indicator_panel | access control | rec_picturex_0611__full_height_turnstile__004__png_104746ac4b87457a9090aff843d68651/rev_000001 | model.py:L88-L120 | structure | The control moves up into the header: an `access_control_box` with a face plate and a row of coloured `*_indicator_bezel`/`*_indicator_lens` pairs on the fascia. |
| second_mechanism | service_guard_leaf | second articulated mechanism | rec_picturex_0611__full_height_turnstile__001__png_6b7e15d6e87242ac98409635abccc39b/rev_000001 | model.py:L146-L189, model.py:L207-L222 | structure+motion | A framed leaf of hinge/latch stiles, uprights and rails on its own `guard_hinge` REVOLUTE about +Z that swings the service barrier out of the lane. |
| second_mechanism | emergency_breakaway_wing | second articulated mechanism | rec_picturex0611_full_height_turnstile_var_emergency_breakaway_wing/rev_000001 | model.py:L156-L184, model.py:L266-L287 | structure+motion | The third wing becomes its own part hinged to the rotor on `rotor_to_breakaway_wing`, folding toward the spindle for emergency egress with a hinge stile and release marker. |
| second_mechanism | locking_pawl_hub | second articulated mechanism | rec_picturex0611_full_height_turnstile_var_locking_pawl_hub/rev_000001 | model.py:L67-L130, model.py:L456-L512 | structure+motion | A CadQuery toothed ratchet ring rides on the rotor base and a `pawl` lever with tip, tail and bushing swings about a horizontal axis on the frame to release it. |
| second_mechanism | overhead_indexing_cam | second articulated mechanism | rec_picturex0611_full_height_turnstile_var_overhead_indexing_cam/rev_000001 | model.py:L64-L116, model.py:L400-L489 | structure+motion | An eccentric-lobe cam disk turns coaxially above the spindle mimic-coupled to the rotor, and an `index_roller_arm` follower pivots on a horizontal axis as the lobe passes under its roller. |

## Multiplicity and N derivation

- `wing_count = 3 | 4`, applied to `rotor_form`.
  - `observed_N`: 3 in all four origins; 4 in `var_four_wing_rotor`.
  - `derived_N_range = 3..4`: the wing loop is index-general in every rotor candidate, but the
    guard opening a full-height turnstile leaves is only mechanically sensible for three or four
    sectors; five wings would foul the fixed cage arc at the sector angles the sources use.
  - validation: each wing rebuilds a complete ladder/palisade and the sector angle, the guard
    opening arc and the rotor motion limits are re-derived from `2*pi/wing_count`.
- `tier_count = 6 | 8 | 11`, applied to `rotor_form`.
  - `observed_N`: 11 in 001/002, 10 in 003, 12 in 004, 6 in `var_rotor_tier_n6`, 8 in
    `var_rotor_tier_n8`.
  - `derived_N_range = 6..11`: the tier loop is index-general; the bound comes from the rotor
    height a tier still needs and from the per-build pose budget, so the 12-rail 004 density is
    not reproduced at full count.
  - validation: each tier adds one real rung/arm per wing and the rung pitch, the wing stile
    length and the collar positions are re-derived from the rotor height.
- `guard_member_count = 5 | 8 | 12`, applied to `guard_frame`.
  - `observed_N`: 4 posts in 001, 5 uprights in 003/004, 8 uprights in `var_guard_upright_n8`,
    13 arc stations in `var_cylindrical_guard_cage`.
  - `derived_N_range = 5..12`: every guard candidate repeats a structural member around the same
    guard radius or portal perimeter, so the loop is index-general; the upper bound comes from
    keeping a real clear arc between adjacent members at the smallest guard radius.
  - validation: each member is placed from the same derived guard radius/perimeter and the guard
    rails, feet and bracket stations are re-derived so adjacent members keep clear spacing.

## Coverage note

All fifteen active records in the `0611 / full_height_turnstile` workbench pool are reviewed.
Eleven contribute a structural candidate; the four remaining pure N forks
(`four_wing_rotor`, `guard_upright_n8`, `rotor_tier_n6`, `rotor_tier_n8`) are recorded as
`reference_only` because they are the multiplicity evidence for the three N loops above rather
than separate structural components. The vertical spindle, the floor/overhead bearing pair and
the galvanized colourway are shared host geometry.

`core_domain = 5 (guard_frame) x 2 (header_form) x 5 (rotor_form) x 4 (access_control) x 4 (second_mechanism) = 800`;
`raw_domain = 800 x 2 (wing_count) x 3 (tier_count) x 3 (guard_member_count) = 14400`.
