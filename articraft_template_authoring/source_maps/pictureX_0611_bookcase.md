# Bookcase (free-standing shelved case) — SourceMap

export_category: pictureX_0611_bookcase

Authoritative records live under `<ARTI_SKILL_ROOT>/arti-template/data/records`.

Category identity: a free-standing case built from vertical side supports carrying a stack of
horizontal book shelves, with at least one real non-fixed joint (a glazed/panel door, a drawer,
or a prismatic adjustable shelf). It is not a wardrobe, a sideboard, a nightstand, or a doored
display cabinet without shelving.

sync_records:
  - rec_picturex_0611__bookcase__001__png__airflex_batch_20260710_9a0ee60395414b908c36814fa8c3e19a
  - rec_picturex_0611__bookcase__002__png__airflex_batch_20260710_d41a0a504a6449e792d71920814a0a92
  - rec_picturex_0611__bookcase__003__png__airflex_batch_20260710_9b1b91d9bff944029cc5e17122776e99
  - rec_picturex_0611__bookcase__004__png__airflex_batch_20260710_70016f2ca9054566885bb677d66ede1a
  - rec_picturex_0611__bookcase__005__png__airflex_batch_20260710_0cd3f4059b0b427ca0e827e61b6ac299
  - rec_picturex_0611__bookcase__006__png__airflex_batch_20260710_ef98d8962cc245f8a0ae664ac6b94981
  - rec_bookcase_var_adjustable_shelves
  - rec_bookcase_var_barrister
  - rec_bookcase_var_base_cabinet_doors
  - rec_bookcase_var_bay_grid_n4
  - rec_bookcase_var_corner
  - rec_bookcase_var_cube_grid
  - rec_bookcase_var_flip_up_glass
  - rec_bookcase_var_ladder
  - rec_bookcase_var_open_shelving
  - rec_bookcase_var_plinth_base
  - rec_bookcase_var_shelves_n3
  - rec_bookcase_var_shelves_n5
  - rec_bookcase_var_shelves_n7
  - rec_bookcase_var_toe_kick_base

All records are read at `revisions/rev_000001/model.py`.

## Shared host preserved by every combination

> two vertical side panels + a top cap + a floor-standing base + N horizontal shelf boards
> spanning between the sides, with the front face open or closed by a moving front assembly.

Every source builds exactly this scaffold as one grounded `carcass` part and attaches its
moving children to it. The invariant kept across all form families is *vertical side supports
carrying a stack of book shelves*.

## Accepted candidates

| Slot | Candidate | Component type | Diversity axis | Record/revision | Exact model.py:Lx-Ly | Status | Accept reason | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|---|
| carcass_form | rectangular_upright | carcass | ③ primary form family — source anchor | rec_picturex_0611__bookcase__005__png__airflex_batch_20260710_0cd3f4059b0b427ca0e827e61b6ac299/rev_000001 | model.py:L240-L324 | accepted | one upright box: two side panels + back + top cap + base + N shelf boards | `carcass` side_panel_0/1, back_panel, top_cap, display_shelf_i |
| carcass_form | two_tier_hutch | carcass | ③ primary form family — source anchor | rec_picturex_0611__bookcase__003__png__airflex_batch_20260710_9b1b91d9bff944029cc5e17122776e99/rev_000001 | model.py:L194-L297 | accepted | upper and lower carcass split by a mid divider shelf; two separate front apertures | `carcass` mid_divider, upper/lower openings |
| carcass_form | legged_highboy | carcass | ③ primary form family — source anchor | rec_picturex_0611__bookcase__004__png__airflex_batch_20260710_70016f2ca9054566885bb677d66ede1a/rev_000001 | model.py:L269-L477 | accepted | case lifted on four turned cylindrical legs with a crown band over the top | `carcass` leg_i (Cylinder), crown_band |
| carcass_form | grid_hutch | carcass | ③ primary form family — source anchor | rec_picturex_0611__bookcase__006__png__airflex_batch_20260710_ef98d8962cc245f8a0ae664ac6b94981/rev_000001 | model.py:L392-L542 | accepted | side-by-side bays separated by full-depth vertical partitions | `carcass` partition_i, per-bay shelf runs |
| carcass_form | ladder | carcass | ③ primary form family — source fork | rec_bookcase_var_ladder/rev_000001 | model.py:L64-L105, model.py:L169-L295 | accepted | leaning trapezoid: raked side stiles, width and depth decrease upward | `carcass` raked stile loft, tapered shelves |
| carcass_form | corner | carcass | ③ primary form family — source fork | rec_bookcase_var_corner/rev_000001 | model.py:L175-L185, model.py:L206-L360 | accepted | L-plan footprint: two perpendicular shelf wings meeting at a rear corner | `carcass` pentagon shelf slabs, wing side panels |
| carcass_form | cube_grid | carcass | ③ primary form family — source fork | rec_bookcase_var_cube_grid/rev_000001 | model.py:L210-L246, model.py:L247-L363 | accepted | rows x cols cube matrix with full-height and full-width dividers | `carcass` cell dividers |
| carcass_form | barrister | carcass | ③ primary form family — source fork | rec_bookcase_var_barrister/rev_000001 | model.py:L59-L126, model.py:L142-L229 | accepted | vertical stack of framed sections, one front opening per section | `carcass` section frames, plinth plate |
| front_treatment | full_glass_doors | front_assembly | ② joint / mechanism type — source anchor | rec_picturex_0611__bookcase__001__png__airflex_batch_20260710_9a0ee60395414b908c36814fa8c3e19a/rev_000001 | model.py:L64-L111, model.py:L370-L459 | accepted | one or two full-height glazed doors, REVOLUTE about a vertical stile axis | `door_i` stile/rail/glass, carcass_to_door_i |
| front_treatment | upper_glass_base_drawers | front_assembly | ② joint / mechanism type — source anchor | rec_picturex_0611__bookcase__005__png__airflex_batch_20260710_0cd3f4059b0b427ca0e827e61b6ac299/rev_000001 | model.py:L46-L118, model.py:L326-L398 | accepted | upper glazed doors REVOLUTE plus base drawers PRISMATIC toward the front | `door_i`, `drawer_i` hollow tray + side runners |
| front_treatment | glass_top_panel_base_doors | front_assembly | ② joint / mechanism type — source anchor | rec_picturex_0611__bookcase__003__png__airflex_batch_20260710_9b1b91d9bff944029cc5e17122776e99/rev_000001 | model.py:L52-L140, model.py:L298-L367 | accepted | upper glazed doors plus lower solid panel doors, both REVOLUTE | `upper_door_i`, `lower_door_i` |
| front_treatment | open_shelving | front_assembly | ② joint / mechanism type — source fork | rec_bookcase_var_open_shelving/rev_000001 | model.py:L25-L93, model.py:L154-L170 | accepted | exposed shelves with a single base drawer PRISMATIC — keeps one non-fixed joint | `drawer_0` tray, carcass_to_drawer_0 |
| front_treatment | base_cabinet_doors | front_assembly | ② joint / mechanism type — source fork | rec_bookcase_var_base_cabinet_doors/rev_000001 | model.py:L25-L106, model.py:L177-L232 | accepted | open upper shelves with paired lower solid cabinet doors REVOLUTE | `base_door_0/1` |
| front_treatment | flip_up_glass | front_assembly | ② joint / mechanism type — source fork | rec_bookcase_var_flip_up_glass/rev_000001 | model.py:L65-L112, model.py:L370-L460 | accepted | top-pivot glazed flap REVOLUTE about a horizontal width axis | `door_i`, hinge axis (1,0,0) |
| shelf_mechanism | fixed_shelves | shelf_stack | ② joint type — source anchor | rec_picturex_0611__bookcase__005__png__airflex_batch_20260710_0cd3f4059b0b427ca0e827e61b6ac299/rev_000001 | model.py:L291-L299 | accepted | shelf boards are carcass visuals; the stack carries no joint | carcass display_shelf_i |
| shelf_mechanism | adjustable_shelves | shelf_stack | ② joint type — source fork | rec_bookcase_var_adjustable_shelves/rev_000001 | model.py:L316-L383 | accepted | each shelf is its own part on a small-travel PRISMATIC Z joint | `display_shelf_i` part + carcass_to_display_shelf_i |
| base_style | plinth | base | ① structural detail — source fork | rec_bookcase_var_plinth_base/rev_000001 | model.py:L242-L330 | accepted | continuous recessed plinth box carrying the case to the floor | carcass plinth box |
| base_style | legs | base | ① structural detail — source anchor | rec_picturex_0611__bookcase__004__png__airflex_batch_20260710_70016f2ca9054566885bb677d66ede1a/rev_000001 | model.py:L269-L340 | accepted | four turned cylindrical legs lift the case off the floor | carcass leg_i |
| base_style | toe_kick | base | ① structural detail — source fork | rec_bookcase_var_toe_kick_base/rev_000001 | model.py:L152-L229 | accepted | recessed toe-kick notch under a front-flush apron | carcass toe_kick apron |
| back_panel | solid_back | back | ① structural detail — source anchor | rec_picturex_0611__bookcase__005__png__airflex_batch_20260710_0cd3f4059b0b427ca0e827e61b6ac299/rev_000001 | model.py:L243-L243 | accepted | one continuous back board closing the case | carcass back_panel |
| back_panel | open_back | back | ① structural detail — source fork | rec_bookcase_var_ladder/rev_000001 | model.py:L84-L105 | accepted | no back board; stiles and shelves carry the case | carcass (no back_panel) |
| back_panel | beadboard_back | back | ① structural detail — source anchor | rec_picturex_0611__bookcase__006__png__airflex_batch_20260710_ef98d8962cc245f8a0ae664ac6b94981/rev_000001 | model.py:L48-L91 | accepted | back built from vertical battens with raised beads | carcass batten_i |
| shelf_count | shelf_count_n3 | shelf_stack multiplicity | N — source anchor | rec_bookcase_var_shelves_n3/rev_000001 | model.py:L245-L300 | accepted | three-shelf instance of the same index-general shelf loop | display_shelf_0..2 |
| shelf_count | shelf_count_n5 | shelf_stack multiplicity | N — source anchor | rec_bookcase_var_shelves_n5/rev_000001 | model.py:L245-L300 | accepted | five-shelf instance of the same shelf loop | display_shelf_0..4 |
| shelf_count | shelf_count_n7 | shelf_stack multiplicity | N — source anchor | rec_bookcase_var_shelves_n7/rev_000001 | model.py:L245-L300 | accepted | seven-shelf instance of the same shelf loop | display_shelf_0..6 |
| shelf_count | host_capacity_bay_grid_n4 | shelf_stack multiplicity | N — host capacity evidence | rec_bookcase_var_bay_grid_n4/rev_000001 | model.py:L415-L597 | accepted | four-bay grid proving per-bay shelf runs stay index-general | bay partitions + per-bay doors/drawers |

`core_domain = 8 (carcass_form) x 6 (front_treatment) x 2 (shelf_mechanism) x 3 (base_style) x 3
(back_panel) = 864`; `raw_domain = 864 x 4 (shelf_count) = 3456`.

Host adaptation instead of gates: every `carcass_form` derives the same front-aperture interface
(front plane y, aperture half-width, an upper band and a lower band in z) from its own geometry —
section frames for `barrister`, the front wing for `corner`, the raked front edge for `ladder`,
the widest bay for `grid_hutch`/`cube_grid`, the tier split for `two_tier_hutch`, the lifted floor
for `legged_highboy`. `front_treatment` consumes only that interface, so all 864 combinations
build and `TemplateDomain` needs no compatibility gate. The legacy template's `_gate_front`
front/form gate is therefore rejected.

## Multiplicity and N derivation

- `shelf_count = 2 | 3 | 5 | 8`, applied to `shelf_mechanism`.
  - `observed_N = 3, 5, 7` (the shelves_n* forks) with four-bay host-capacity evidence.
  - `derived_N_range = 2..8`: the shelf loop is index-general (pitch derived from the interior
    clear height), so the bound comes from host capacity — a shelf pitch must stay above the
    minimum book height — and from the compile/pose budget, not from the integers in the pool.
  - validation: every N adds one shelf board (or, for `adjustable_shelves`, one shelf part plus
    one prismatic joint) and re-derives shelf pitch, the interior clear height, the front
    aperture bands and the door/drawer heights.

## Independent parameters (honest, not core/raw)

- `width_m` (0.62–1.60 m; sources 0.70–1.55) — case width; derives side-panel spacing, shelf span,
  aperture half-width, door leaf width and drawer width.
- `depth_m` (0.26–0.58 m; sources 0.36–0.45) — case depth; derives shelf depth, drawer travel,
  runner length and door stand-off.
- `height_m` (1.20–2.30 m; sources 1.72–2.10) — case height; derives shelf pitch, aperture bands
  and base lift.
- `shelf_thickness_m` (0.018–0.032 m) — shelf board thickness; derives clear pitch and the
  adjustable-shelf travel window.

## Rejected

- Whole-carcass "wardrobe" and "sideboard" forks from the neighbouring 0611 categories: they
  drop the book-shelf stack, so they fall outside this category identity.
- Per-seed decorative-only variants (palette, grain strips, knob shape): surface-only, they do
  not contribute a structural candidate.

## Notes on quality preservation

- Doors keep their real stile/rail/glass construction (005 L46-L118) rather than becoming a slab.
- Drawers stay hollow trays: front + two sides + back + bottom (005 L171-L202), and slide along
  the real pull-out direction with the carcass providing side runners (005 L373-L381).
- The `legged_highboy` legs stay turned cylinders (004 L269-L340); the `ladder` stiles keep the
  raked loft profile; `corner` keeps the pentagon shelf plan.
- Hinges are built as real axis interfaces on the stile line, not as visual-only barrels.
