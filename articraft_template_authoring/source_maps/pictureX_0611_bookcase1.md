# Bookcase1 (tall household bookcase / display case) — SourceMap

export_category: pictureX_0611_bookcase1

Authoritative records live under `<ARTI_SKILL_ROOT>/articraft_data/data/records`.

Category identity: a tall household bookcase or display case — vertical side boards, a stack of
horizontal shelves, a back, and a lower cabinet band that carries the moving hardware (raised-panel
or glazed doors, base drawers, or a top-pivot glazed flap). It is not a wardrobe, a sideboard, a
desk, or an empty abstract frame. Neighbouring categories: `pictureX_0611_bookcase` owns the
glazed display-cabinet family, `pictureX_0611_bookcase2` the two-tier / sliding-door / caster
family, and `pictureX_0611_Bookshelf_with_books` the shelf-with-contents family.

sync_records:
  - rec_bookcase1_var_adjustable_shelves
  - rec_bookcase1_var_barrister
  - rec_bookcase1_var_corner
  - rec_bookcase1_var_cubby_cols_n5
  - rec_bookcase1_var_cube_grid
  - rec_bookcase1_var_drawers_n6
  - rec_bookcase1_var_flip_up_glass
  - rec_bookcase1_var_glass_doors
  - rec_bookcase1_var_ladder
  - rec_bookcase1_var_leg_base
  - rec_bookcase1_var_shelves_n2
  - rec_bookcase1_var_shelves_n5
  - rec_bookcase1_var_toe_kick_base
  - rec_picturex_0611__bookcase1__001__png__airflex_batch_20260710_af78e3aee09d4d56bc322c751dd82769
  - rec_picturex_0611__bookcase1__002__png__airflex_batch_20260710_2ae2eae6db184b82bf3b32de33e8d48c
  - rec_picturex_0611__bookcase1__003__png__airflex_batch_20260710_94e954a34485417090375e4901fd3a16

All records are read at `revisions/rev_000001/model.py`.

## Shared host preserved by every combination

> two vertical side boards + a top cap + a floor-standing base + N horizontal shelf boards, with a
> lower cabinet band whose front carries the moving assembly.

## Accepted candidates

| Slot | Candidate | Component type | Diversity axis | Record/revision | Exact model.py:Lx-Ly | Status | Accept reason | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|---|
| case_frame | gallery_cheeks | carcass | ③ primary form family — source anchor | rec_picturex_0611__bookcase1__001__png__airflex_batch_20260710_af78e3aee09d4d56bc322c751dd82769/rev_000001 | model.py:L28-L167, model.py:L168-L272 | accepted | side cheeks with the rounded rising gallery profile carrying open shelves | `carcass` side cheek profile, gallery top |
| case_frame | cubby_columns | carcass | ③ primary form family — source anchor | rec_picturex_0611__bookcase1__002__png__airflex_batch_20260710_2ae2eae6db184b82bf3b32de33e8d48c/rev_000001 | model.py:L158-L308 | accepted | full-height vertical column dividers splitting the case into cubbies | `carcass` column dividers, cubby shelves |
| case_frame | panelled_side_frame | carcass | ③ primary form family — source anchor | rec_picturex_0611__bookcase1__003__png__airflex_batch_20260710_94e954a34485417090375e4901fd3a16/rev_000001 | model.py:L32-L70, model.py:L209-L350 | accepted | stile-and-rail raised frame treatment on both visible side panels | `carcass` side stiles/rails, shelf run |
| case_frame | corner_wing | carcass | ③ primary form family — source fork | rec_bookcase1_var_corner/rev_000001 | model.py:L80-L119, model.py:L250-L400 | accepted | L-plan case with a perpendicular return wing and its own side treatment | `carcass` return wing panels |
| case_frame | cube_grid | carcass | ③ primary form family — source fork | rec_bookcase1_var_cube_grid/rev_000001 | model.py:L52-L151, model.py:L152-L212 | accepted | rows x cols cube matrix built from full boards and dividers | `carcass` cell boards |
| case_frame | raked_ladder | carcass | ③ primary form family — source fork | rec_bookcase1_var_ladder/rev_000001 | model.py:L37-L106, model.py:L214-L344 | accepted | leaning case: raked side panels, width and depth taper with height | `carcass` raked side panel loft |
| case_frame | barrister_stack | carcass | ③ primary form family — source fork | rec_bookcase1_var_barrister/rev_000001 | model.py:L160-L295 | accepted | stacked framed sections, one glazed opening per section | `carcass` section frames |
| lower_front | raised_panel_doors | front_assembly | ② joint / mechanism type — source anchor | rec_picturex_0611__bookcase1__003__png__airflex_batch_20260710_94e954a34485417090375e4901fd3a16/rev_000001 | model.py:L71-L172, model.py:L173-L208 | accepted | overlay raised-panel doors on the lower cabinet, REVOLUTE about a vertical stile | `door_i`, hinge axis (0,0,1) |
| lower_front | framed_glass_doors | front_assembly | ② joint / mechanism type — source fork | rec_bookcase1_var_glass_doors/rev_000001 | model.py:L124-L177, model.py:L410-L470 | accepted | glazed frame-and-panel doors over the shelf stack, REVOLUTE | `door_i` frame + glass |
| lower_front | base_drawers | front_assembly | ② joint / mechanism type — source anchor | rec_picturex_0611__bookcase1__001__png__airflex_batch_20260710_af78e3aee09d4d56bc322c751dd82769/rev_000001 | model.py:L273-L330 | accepted | stacked drawer units sliding out of the base, PRISMATIC toward the front | `drawer_i` box + bar pull |
| lower_front | flip_up_glass_flap | front_assembly | ② joint / mechanism type — source fork | rec_bookcase1_var_flip_up_glass/rev_000001 | model.py:L138-L189, model.py:L406-L436 | accepted | top-pivot glazed flap REVOLUTE about the width axis | `flap`, hinge axis (1,0,0) |
| lower_front | open_cubby_base | front_assembly | ② joint / mechanism type — source fork | rec_bookcase1_var_cubby_cols_n5/rev_000001 | model.py:L138-L157, model.py:L310-L340 | accepted | open cubby base with a single retained door leaf keeping one non-fixed joint | `door_0` |
| shelf_mechanism | fixed_shelves | shelf_stack | ② joint type — source anchor | rec_picturex_0611__bookcase1__002__png__airflex_batch_20260710_2ae2eae6db184b82bf3b32de33e8d48c/rev_000001 | model.py:L158-L308 | accepted | shelf boards fused into the carcass | carcass shelf boards |
| shelf_mechanism | adjustable_shelves | shelf_stack | ② joint type — source fork | rec_bookcase1_var_adjustable_shelves/rev_000001 | model.py:L304-L360 | accepted | each shelf is its own part on a small-travel PRISMATIC Z joint | `shelf_i` + prismatic joint |
| base_style | plinth_base | base | ① structural detail — source anchor | rec_picturex_0611__bookcase1__002__png__airflex_batch_20260710_2ae2eae6db184b82bf3b32de33e8d48c/rev_000001 | model.py:L158-L200 | accepted | continuous recessed plinth under the case | carcass plinth |
| base_style | turned_legs | base | ① structural detail — source fork | rec_bookcase1_var_leg_base/rev_000001 | model.py:L124-L171, model.py:L322-L352 | accepted | four turned legs and an apron rail lifting the case | `leg_i`, `apron_rail` |
| base_style | toe_kick | base | ① structural detail — source fork | rec_bookcase1_var_toe_kick_base/rev_000001 | model.py:L143-L230 | accepted | recessed toe kick under a front-flush apron | carcass toe kick |
| shelf_count | shelf_count_n2 | shelf_stack multiplicity | N — source anchor | rec_bookcase1_var_shelves_n2/rev_000001 | model.py:L188-L312 | accepted | two-shelf instance of the index-general shelf loop | shelf boards 0..1 |
| shelf_count | shelf_count_n5 | shelf_stack multiplicity | N — source anchor | rec_bookcase1_var_shelves_n5/rev_000001 | model.py:L188-L322 | accepted | five-shelf instance of the same loop | shelf boards 0..4 |
| shelf_count | cubby_cols_n5 | shelf_stack multiplicity | N — host capacity evidence | rec_bookcase1_var_cubby_cols_n5/rev_000001 | model.py:L138-L340 | accepted | five-column cubby grid proving the per-column runs stay index-general | column dividers 0..4 |
| shelf_count | drawers_n6 | shelf_stack multiplicity | N — host capacity evidence | rec_bookcase1_var_drawers_n6/rev_000001 | model.py:L168-L330 | accepted | six stacked drawer units proving the base band stays index-general | drawer_0..5 |

`core_domain = 7 (case_frame) x 5 (lower_front) x 2 (shelf_mechanism) x 3 (base_style) = 210`;
`raw_domain = 210 x 4 (shelf_count) = 840`.

Host adaptation instead of gates: every `case_frame` exports the same lower-band aperture (front
plane, aperture half-width and centre, and the band's z range) plus its own shelf rows; the
`lower_front` candidates consume only that aperture. The raked ladder exports its vertical base
box, the corner wing its front-facing wing, the cube grid and cubby columns their widest cell, and
the barrister stack its lowest section, so all 210 combinations build without a compatibility gate.

## Multiplicity and N derivation

- `shelf_count = 2 | 3 | 5 | 7`, applied to `shelf_mechanism`.
  - `observed_N = 2, 5` (shelves_n2 / shelves_n5), with n3/n5 cubby-column and n3/n6 drawer forks
    as host-capacity evidence.
  - `derived_N_range = 2..7`: the shelf loop is index-general; the bound comes from the interior
    clear height a bay still needs and from the compile/pose budget, not from the source integers.
  - validation: each N adds one shelf board (or one shelf part plus one prismatic joint) and
    re-derives shelf pitch, the lower band, the door/drawer heights and the adjustable travel.

## Independent parameters (honest, not core/raw)

- `width_m` (0.60–1.45 m) — case width; derives side spacing, shelf span, aperture half-width and
  leaf/drawer width.
- `depth_m` (0.24–0.52 m) — case depth; derives shelf depth, drawer travel, runner length.
- `height_m` (1.10–2.20 m) — case height; derives shelf pitch and the lower band.
- `shelf_thickness_m` (0.016–0.030 m) — board thickness; derives clear pitch and shelf travel.

## Rejected

- Wardrobe / sideboard / desk forks: they drop the tall shelf stack and leave the category.
- Palette, grain and knob-shape only variants: surface-only, no structural candidate.
