# Bookcase2 (two-tier / sliding-door / mobile bookcase) — SourceMap

export_category: pictureX_0611_bookcase2

Authoritative records live under `<ARTI_SKILL_ROOT>/articraft_data/data/records`.

Category identity: a free-standing bookcase built as an open bay frame or panel carcass, whose
front band carries the moving hardware — hinged doors, **bypass sliding doors**, drawers or a
pull-out shelf tray — and which may stand on casters. Neighbouring categories:
`pictureX_0611_bookcase` owns the glazed display-cabinet family, `pictureX_0611_bookcase1` the
tall gallery/panelled household case, and `pictureX_0611_Bookshelf_with_books` the
shelf-with-contents family.

sync_records:
  - rec_bookcase2_var_adjustable_shelves
  - rec_bookcase2_var_bays_n4
  - rec_bookcase2_var_caster_base
  - rec_bookcase2_var_drawers_n6
  - rec_bookcase2_var_frame_raked_ladder
  - rec_bookcase2_var_lower_drawers_only
  - rec_bookcase2_var_lower_open_cubby
  - rec_bookcase2_var_pullout_shelf
  - rec_bookcase2_var_shelves_n4
  - rec_bookcase2_var_shelves_n5
  - rec_bookcase2_var_sliding_doors
  - rec_bookcase2_var_toe_kick_base
  - rec_bookcase2_var_two_tier
  - rec_bookcase2_var_upper_doors
  - rec_picturex_0611__bookcase2__001__png__airflex_batch_20260710_34c5026b659e48e4aa8fcf9aa81310a9
  - rec_picturex_0611__bookcase2__002__png__airflex_batch_20260710_025bea44031741e5abb27765f8859bc7
  - rec_picturex_0611__bookcase2__003__png__airflex_batch_20260710_9bdac952bef24599ba153fc9fe2eabfa

All records are read at `revisions/rev_000001/model.py`.

## Shared host preserved by every combination

> two vertical side supports + a top cap + a floor-standing base + N horizontal shelf boards,
> with a front band whose aperture carries the moving assembly.

## Accepted candidates

| Slot | Candidate | Component type | Diversity axis | Record/revision | Exact model.py:Lx-Ly | Status | Accept reason | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|---|
| case_frame | open_bay_frame | carcass | ③ primary form family — source anchor | rec_picturex_0611__bookcase2__001__png__airflex_batch_20260710_34c5026b659e48e4aa8fcf9aa81310a9/rev_000001 | model.py:L156-L381 | accepted | open bay frame: slim uprights and full-width rails carrying independent drawer units | `frame` uprights, bay rails |
| case_frame | panel_carcass | carcass | ③ primary form family — source anchor | rec_picturex_0611__bookcase2__002__png__airflex_batch_20260710_025bea44031741e5abb27765f8859bc7/rev_000001 | model.py:L47-L138, model.py:L162-L262 | accepted | closed panel carcass with a full-width upper opening and a lower cabinet | `carcass` panel shell |
| case_frame | slim_upright | carcass | ③ primary form family — source anchor | rec_picturex_0611__bookcase2__003__png__airflex_batch_20260710_9bdac952bef24599ba153fc9fe2eabfa/rev_000001 | model.py:L110-L186 | accepted | slim upright frame with thin side stiles and a shelf run behind the doors | `frame` stiles, shelves |
| case_frame | two_tier_split | carcass | ③ primary form family — source fork | rec_bookcase2_var_two_tier/rev_000001 | model.py:L47-L164, model.py:L189-L262 | accepted | upper and lower carcass split at a mid deck, each with its own opening | `carcass` mid deck |
| case_frame | bay_grid | carcass | ③ primary form family — source fork | rec_bookcase2_var_bays_n4/rev_000001 | model.py:L156-L339 | accepted | side-by-side bays divided by full-depth uprights | `frame` bay uprights |
| case_frame | raked_ladder_frame | carcass | ③ primary form family — source fork | rec_bookcase2_var_frame_raked_ladder/rev_000001 | model.py:L110-L228 | accepted | leaning frame: raked uprights over a vertical lower cabinet | `frame` raked uprights |
| lower_front | hinged_upper_doors | front_assembly | ② joint / mechanism type — source fork | rec_bookcase2_var_upper_doors/rev_000001 | model.py:L26-L120, model.py:L199-L225 | accepted | paired doors REVOLUTE about vertical stiles closing the upper opening | `door_0/1` |
| lower_front | hinged_lower_doors | front_assembly | ② joint / mechanism type — source anchor | rec_picturex_0611__bookcase2__003__png__airflex_batch_20260710_9bdac952bef24599ba153fc9fe2eabfa/rev_000001 | model.py:L26-L109, model.py:L187-L214 | accepted | paired lower cabinet doors REVOLUTE about vertical stiles | `door_0/1` |
| lower_front | bypass_sliding_doors | front_assembly | ② joint / mechanism type — source fork | rec_bookcase2_var_sliding_doors/rev_000001 | model.py:L110-L121, model.py:L234-L300 | accepted | two bypass leaves on front and rear tracks, PRISMATIC along the width | `door_0/1` on tracks, axis (1,0,0) |
| lower_front | lower_drawers | front_assembly | ② joint / mechanism type — source fork | rec_bookcase2_var_lower_drawers_only/rev_000001 | model.py:L110-L133, model.py:L200-L270 | accepted | full-width drawer plus stacked lower drawer boxes, PRISMATIC to the front | `drawer`, `ldrawer_i` |
| lower_front | pullout_shelf | front_assembly | ② joint / mechanism type — source fork | rec_bookcase2_var_pullout_shelf/rev_000001 | model.py:L27-L191, model.py:L209-L418 | accepted | a shelf tray that pulls out of the case on side runners, PRISMATIC | pullout tray |
| lower_front | open_cubby_with_drawer | front_assembly | ② joint / mechanism type — source fork | rec_bookcase2_var_lower_open_cubby/rev_000001 | model.py:L110-L127, model.py:L202-L233 | accepted | open lower cubby keeping one full-width sliding drawer | `drawer` |
| shelf_mechanism | fixed_shelves | shelf_stack | ② joint type — source anchor | rec_picturex_0611__bookcase2__003__png__airflex_batch_20260710_9bdac952bef24599ba153fc9fe2eabfa/rev_000001 | model.py:L127-L186 | accepted | shelf boards fused into the frame | frame shelf boards |
| shelf_mechanism | adjustable_shelves | shelf_stack | ② joint type — source fork | rec_bookcase2_var_adjustable_shelves/rev_000001 | model.py:L184-L226 | accepted | each shelf is its own part on a small-travel PRISMATIC Z joint | `shelf_i` + prismatic |
| base_style | plinth_base | base | ① structural detail — source anchor | rec_picturex_0611__bookcase2__002__png__airflex_batch_20260710_025bea44031741e5abb27765f8859bc7/rev_000001 | model.py:L162-L202 | accepted | recessed plinth under the carcass | carcass plinth |
| base_style | caster_base | base | ① structural detail — source fork | rec_bookcase2_var_caster_base/rev_000001 | model.py:L156-L431 | accepted | four caster assemblies on mounting plates lifting the case | caster plates + wheels |
| base_style | toe_kick | base | ① structural detail — source fork | rec_bookcase2_var_toe_kick_base/rev_000001 | model.py:L149-L246 | accepted | recessed toe kick under a front-flush apron | carcass toe kick |
| shelf_count | shelf_count_n4 | shelf_stack multiplicity | N — source anchor | rec_bookcase2_var_shelves_n4/rev_000001 | model.py:L110-L200 | accepted | four-shelf instance of the index-general shelf loop | shelf boards 0..3 |
| shelf_count | shelf_count_n5 | shelf_stack multiplicity | N — source anchor | rec_bookcase2_var_shelves_n5/rev_000001 | model.py:L110-L200 | accepted | five-shelf instance of the same loop | shelf boards 0..4 |
| shelf_count | bays_n4 | shelf_stack multiplicity | N — host capacity evidence | rec_bookcase2_var_bays_n4/rev_000001 | model.py:L156-L339 | accepted | four-bay frame proving per-bay runs stay index-general | bay uprights |
| shelf_count | drawers_n6 | shelf_stack multiplicity | N — host capacity evidence | rec_bookcase2_var_drawers_n6/rev_000001 | model.py:L156-L400 | accepted | six stacked drawer units proving the front band stays index-general | drawer units |

`core_domain = 6 (case_frame) x 6 (lower_front) x 2 (shelf_mechanism) x 3 (base_style) = 216`;
`raw_domain = 216 x 4 (shelf_count) = 864`.

Host adaptation instead of gates: every `case_frame` exports the same aperture interface (front
plane, aperture half-width and centre, an upper and a lower band in z) and its own shelf rows;
`lower_front` consumes only that aperture. The bypass sliding doors additionally consume a track
pair derived from the aperture width, and the pull-out tray a runner pair derived from the case
depth, so all 216 combinations build without a compatibility gate.

## Multiplicity and N derivation

- `shelf_count = 2 | 4 | 5 | 7`, applied to `shelf_mechanism`.
  - `observed_N = 4, 5` (shelves_n4 / shelves_n5) with 4-bay and 6-drawer host-capacity forks.
  - `derived_N_range = 2..7`: the shelf loop is index-general; the bound comes from the clear bay
    height and the compile/pose budget, not from the source integers.
  - validation: every N adds one shelf board (or one shelf part plus one prismatic joint) and
    re-derives shelf pitch, the front bands, the door/drawer heights and the shelf travel.

## Independent parameters (honest, not core/raw)

- `width_m` (0.60–1.50 m), `depth_m` (0.24–0.52 m), `height_m` (1.05–2.10 m),
  `shelf_thickness_m` (0.016–0.030 m).

## Rejected

- Wardrobe / sideboard forks: they drop the shelf stack and leave the category.
- Palette and hardware-finish only variants: surface-only, no structural candidate.
