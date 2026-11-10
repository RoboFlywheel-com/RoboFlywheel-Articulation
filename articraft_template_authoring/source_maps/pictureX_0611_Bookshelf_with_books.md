# Bookshelf with books (desktop book tray / organiser) — SourceMap

export_category: pictureX_0611_Bookshelf_with_books

Authoritative records live under `<ARTI_SKILL_ROOT>/articraft_data/data/records`.

Category identity: an injection-moulded **desktop file sorter** — a deck between two perforated
moulded end walls, split into upright bays by N movable divider plates. The source record states
the identity itself: the folder label is `Bookshelf_with_books`, but 001.png is a white translucent
moulded desktop file sorter (`classification_mismatch`, model.py:L106-L120), so the perforated end
walls and the tall sliding divider plates are the recognisable structure. The moving mechanism is
the divider set (sliding along the width, lifting out of sockets, or sliding bookends). It is not a
free-standing case: the `pictureX_0611_bookcase*` categories own those.

sync_records:
  - rec_bookshelf_with_books_var_bays_n3
  - rec_bookshelf_with_books_var_bays_n5
  - rec_bookshelf_with_books_var_bookend_supports
  - rec_bookshelf_with_books_var_books_row
  - rec_bookshelf_with_books_var_cube_grid
  - rec_bookshelf_with_books_var_fold_flat
  - rec_bookshelf_with_books_var_footed_base
  - rec_bookshelf_with_books_var_incline_rack
  - rec_bookshelf_with_books_var_ladder_riser
  - rec_bookshelf_with_books_var_liftout_dividers
  - rec_bookshelf_with_books_var_mesh_basket
  - rec_bookshelf_with_books_var_sliding_bookend
  - rec_bookshelf_with_books_var_solid_dividers
  - rec_bookshelf_with_books_var_stepped_tiers
  - rec_bookshelf_with_books_var_tilt_back
  - rec_picturex_0611__bookshelf_with_books__001__png__adjustable_rebuild_20260710_04de0b28014249f6921c8824d8eb81bc

All records are read at `revisions/rev_000001/model.py`.

## Shared host preserved by every combination

> a deck with two end walls carrying an upright row of books, plus N divider panels that move
> relative to the deck.

## Accepted candidates

| Slot | Candidate | Component type | Diversity axis | Record/revision | Exact model.py:Lx-Ly | Status | Accept reason | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|---|
| tray_body | flat_tray | tray | ③ primary form family — source anchor | rec_picturex_0611__bookshelf_with_books__001__png__adjustable_rebuild_20260710_04de0b28014249f6921c8824d8eb81bc/rev_000001 | model.py:L106-L253 | accepted | flat book tray: floor deck, two end walls and a low back rail | `tray` deck, end walls |
| tray_body | incline_rack | tray | ③ primary form family — source fork | rec_bookshelf_with_books_var_incline_rack/rev_000001 | model.py:L114-L272 | accepted | deck pitched back with a front retaining lip so books lean | `tray` inclined deck, front lip |
| tray_body | stepped_tiers | tray | ③ primary form family — source fork | rec_bookshelf_with_books_var_stepped_tiers/rev_000001 | model.py:L135-L308 | accepted | two-level deck: a raised rear tier stepped above the front tier | `tray` step riser, rear deck |
| tray_body | cube_grid | tray | ③ primary form family — source fork | rec_bookshelf_with_books_var_cube_grid/rev_000001 | model.py:L81-L345 | accepted | mid board splits the tray into two rows of cubes | `tray` mid board |
| tray_body | mesh_basket | tray | ③ primary form family — source fork | rec_bookshelf_with_books_var_mesh_basket/rev_000001 | model.py:L146-L398 | accepted | walls built as an open lattice of slats instead of solid boards | `tray` lattice walls |
| end_walls | perforated_end_walls | end_wall | ③ primary form family — source anchor | rec_picturex_0611__bookshelf_with_books__001__png__adjustable_rebuild_20260710_04de0b28014249f6921c8824d8eb81bc/rev_000001 | model.py:L47-L105 | accepted | tapered moulded end wall carrying the 5x5 rounded through-slot grid that identifies the moulding | `tray` perforated panel + rims |
| end_walls | fold_flat_walls | end_wall | ② joint / mechanism type — source fork | rec_bookshelf_with_books_var_fold_flat/rev_000001 | model.py:L267-L306 | accepted | end walls hinge down flat, REVOLUTE about the depth axis | `end_wall_i`, axis (0,1,0) |
| end_walls | bookend_supports | end_wall | ① structural detail — source fork | rec_bookshelf_with_books_var_bookend_supports/rev_000001 | model.py:L47-L123 | accepted | L-profile bookend ends with a broad foot under the books | `tray` bookend feet |
| divider_mechanism | sliding_dividers | divider | ② joint type — source anchor | rec_picturex_0611__bookshelf_with_books__001__png__adjustable_rebuild_20260710_04de0b28014249f6921c8824d8eb81bc/rev_000001 | model.py:L254-L338 | accepted | N divider panels sliding along the tray width, PRISMATIC X | `divider_i`, axis (1,0,0) |
| divider_mechanism | liftout_dividers | divider | ② joint type — source fork | rec_bookshelf_with_books_var_liftout_dividers/rev_000001 | model.py:L112-L132, model.py:L293-L360 | accepted | N dividers lift straight out of floor sockets, PRISMATIC Z | `divider_i`, axis (0,0,1) |
| divider_mechanism | sliding_bookends | divider | ② joint type — source fork | rec_bookshelf_with_books_var_sliding_bookend/rev_000001 | model.py:L306-L410 | accepted | N L-profile bookends with feet sliding on a floor rail, PRISMATIC X | `bookend_i`, foot + rail |
| base_style | flat_base | base | ① structural detail — source anchor | rec_picturex_0611__bookshelf_with_books__001__png__adjustable_rebuild_20260710_04de0b28014249f6921c8824d8eb81bc/rev_000001 | model.py:L136-L200 | accepted | the tray sits flat on two full-length floor rails | `base` rails |
| base_style | footed_base | base | ① structural detail — source fork | rec_bookshelf_with_books_var_footed_base/rev_000001 | model.py:L59-L67, model.py:L159-L296 | accepted | four feet lift the tray off the desk | `base` feet |
| divider_count | divider_count_n3 | divider multiplicity | N — source anchor | rec_bookshelf_with_books_var_bays_n3/rev_000001 | model.py:L106-L338 | accepted | three-divider instance of the index-general divider loop | divider_0..2 |
| divider_count | divider_count_n5 | divider multiplicity | N — source anchor | rec_bookshelf_with_books_var_bays_n5/rev_000001 | model.py:L106-L338 | accepted | five-divider instance of the same loop | divider_0..4 |
| divider_count | solid_dividers_capacity | divider multiplicity | N — host capacity evidence | rec_bookshelf_with_books_var_solid_dividers/rev_000001 | model.py:L106-L338 | accepted | solid divider set proving bay width stays index-general | divider set |
| divider_count | books_row_capacity | divider multiplicity | N — host capacity evidence | rec_bookshelf_with_books_var_books_row/rev_000001 | model.py:L115-L348 | accepted | book row per bay proving the contents scale with N | book blocks |

`core_domain = 5 (tray_body) x 3 (end_walls) x 3 (divider_mechanism) x 2 (base_style) = 90`;
`raw_domain = 90 x 4 (divider_count) = 360`.

Host adaptation instead of gates: every `tray_body` exports the same deck interface (deck plane,
usable half-width, book-bay depth and wall height); `end_walls`, `divider_mechanism` and
`base_style` consume only that interface. The incline rack exports a pitched deck plane, the
stepped tier its front tier, the ladder riser its lower deck, the cube grid its lower row and the
mesh basket its lattice wall line, so all 162 combinations build without a gate.

## Multiplicity and N derivation

- `divider_count = 2 | 3 | 5 | 7`, applied to `divider_mechanism`.
  - `observed_N = 3, 5` (bays_n3 / bays_n5) plus the solid-divider and books-row forks.
  - `derived_N_range = 2..7`: the divider loop is index-general (bay pitch derived from the usable
    width); the bound comes from the bay width a book row still needs and the pose budget.
  - validation: every N adds one divider part, one prismatic joint, one book group and one floor
    rail/socket, and re-derives the bay pitch, the divider travel and the book block sizes.

## Independent parameters (honest, not core/raw)

- `width_m` (0.28–0.55 m; source SORTER_WIDTH 0.340), `depth_m` (0.14–0.32 m; source 0.250),
  `wall_height_m` (0.13–0.26 m; source end wall ~0.220), `panel_thickness_m` (0.008–0.016 m;
  source WALL_THICKNESS 0.0055 / DIVIDER_THICKNESS 0.0040).

## Rejected

- Free-standing bookcase forks (upright_multishelf): they belong to the `bookcase*` categories.
- Books-only recolouring variants: surface-only, no structural candidate.
- `ladder_riser` (rear riser + upper shelf) and `tilt_back` (whole tray on a tilting cradle):
  both are real forks, but on a desktop file sorter they read as a different product; they are
  dropped so the category keeps the moulded-sorter silhouette. The contents stay sparse for the
  same reason — the authoritative image shows the sorter empty.
