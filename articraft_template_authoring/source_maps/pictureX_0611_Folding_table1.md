# Folding table 1 (tube-frame rolltop folding table) — SourceMap

export_category: pictureX_0611_Folding_table1

Authoritative records live under `<ARTI_SKILL_ROOT>/arti-template/data/records`.

Category identity: a light tube-framed folding table whose deck is a rolled slat run, a solid
panel or an open mesh, carried by folding tube supports. Neighbouring categories:
`pictureX_0611_Folding_table` owns the general bi-fold/trestle family and
`pictureX_0611_Folding_table2` the caster / drop-leaf / compact family.

sync_records:
  - rec_picturex0611_folding_table1_crossbrace_locks
  - rec_picturex0611_folding_table1_dense_rolltop_slats
  - rec_picturex0611_folding_table1_rolltop_slats
  - rec_picturex0611_folding_table1_sparse_rolltop_slats
  - rec_picturex0611_folding_table1_telescoping_legs
  - rec_picturex_0611__folding_table1__001__png_0b428e5ff1244f358d87b7bdb6280028
  - rec_picturex_0611__folding_table1__002__png_d8a89d70dc0f47578894d5248ec122c6
  - rec_picturex_0611__folding_table1__003__png_119980c9a7f043de91626799dd220807

All records are read at `revisions/rev_000001/model.py`.

## Shared host preserved by every combination

> a deck in a tube perimeter frame carried at working height by N folding supports, each hinged
> under the deck and able to swing flat against it.

## Accepted candidates

| Slot | Candidate | Component type | Diversity axis | Record/revision | Exact model.py:Lx-Ly | Status | Accept reason | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|---|
| top_style | rolltop_slats | tabletop | ③ primary form family — source anchor | rec_picturex_0611__folding_table1__001__png_0b428e5ff1244f358d87b7bdb6280028/rev_000001 | model.py:L27-L200 | accepted | rolled slat deck on two underside cross rails | slats + cross rails |
| top_style | dense_rolltop_slats | tabletop | ③ primary form family — source fork | rec_picturex0611_folding_table1_dense_rolltop_slats/rev_000001 | model.py:L27-L200 | accepted | the same roll at twice the slat density | dense slat run |
| top_style | solid_panel | tabletop | ③ primary form family — source anchor | rec_picturex_0611__folding_table1__002__png_d8a89d70dc0f47578894d5248ec122c6/rev_000001 | model.py:L41-L149 | accepted | a solid deck in the same tube frame | top panel + rails |
| top_style | mesh_panel | tabletop | ③ primary form family — source anchor | rec_picturex_0611__folding_table1__003__png_119980c9a7f043de91626799dd220807/rev_000001 | model.py:L20-L200 | accepted | perforated mesh deck of crossed straps | mesh straps |
| support_style | folding_tube_legs | support | ② joint type — source anchor | rec_picturex_0611__folding_table1__001__png_0b428e5ff1244f358d87b7bdb6280028/rev_000001 | model.py:L263-L400 | accepted | folding tube legs on under-top brackets | `leg_i` tubes |
| support_style | crossbrace_locks | support | ② joint type — source fork | rec_picturex0611_folding_table1_crossbrace_locks/rev_000001 | model.py:L130-L340 | accepted | leg pairs with diagonal locking cross braces | `leg_i` + braces |
| support_style | tube_x_frame | support | ③ form family — source fork | rec_picturex0611_folding_table1_rolltop_slats/rev_000001 | model.py:L142-L260 | accepted | crossed tube X-frames under the roll | X-frame arms |
| support_style | telescoping_legs | support | ② joint type — source fork | rec_picturex0611_folding_table1_telescoping_legs/rev_000001 | model.py:L152-L295 | accepted | outer tube plus a PRISMATIC inner section | `leg_i`, `leg_inner_i` |
| foot_style | flat_glide | foot | ① structural detail — source anchor | rec_picturex_0611__folding_table1__002__png_d8a89d70dc0f47578894d5248ec122c6/rev_000001 | model.py:L150-L210 | accepted | flat glide pads under each leg | glide pads |
| foot_style | swivel_pad | foot | ① structural detail — source anchor | rec_picturex_0611__folding_table1__001__png_0b428e5ff1244f358d87b7bdb6280028/rev_000001 | model.py:L300-L346 | accepted | swivelling foot pads on a stem | foot stems + pads |
| foot_style | floor_rail | foot | ① structural detail — source fork | rec_picturex0611_folding_table1_crossbrace_locks/rev_000001 | model.py:L191-L223 | accepted | a floor rail spreads the load under each support | floor rails |
| leg_count | leg_count_n4 | support multiplicity | N — source anchor | rec_picturex_0611__folding_table1__001__png_0b428e5ff1244f358d87b7bdb6280028/rev_000001 | model.py:L263-L400 | accepted | four folding stations | leg_0..3 |
| leg_count | leg_count_n2 | support multiplicity | N — source anchor | rec_picturex_0611__folding_table1__002__png_d8a89d70dc0f47578894d5248ec122c6/rev_000001 | model.py:L150-L210 | accepted | two folding stations | leg_0..1 |
| leg_count | sparse_dense_capacity | support multiplicity | N — host capacity evidence | rec_picturex0611_folding_table1_sparse_rolltop_slats/rev_000001 | model.py:L27-L200 | accepted | sparse/dense rolls prove the station loop stays index-general | slat + station loops |

`core_domain = 4 (top_style) x 4 (support_style) x 3 (foot_style) = 48`;
`raw_domain = 48 x 3 (leg_count) = 144`.

Host adaptation instead of gates: every `top_style` exports the same under-deck interface (deck
plane, usable half-length and half-depth, one hinge line per station); `support_style` consumes
only that interface and reports its foot positions to `foot_style`, so all 48 combinations build.

## Multiplicity and N derivation

- `leg_count = 2 | 4 | 6`, applied to `support_style`; `derived_N_range = 2..6` from the deck
  length a station still needs and the pose budget. Every N re-derives the station pitch, the
  fold limit, the X-frame reach and the foot spacing.

## Independent parameters (honest, not core/raw)

- `top_length_m` (0.60–1.85 m), `top_depth_m` (0.42–0.86 m), `top_height_m` (0.32–0.78 m),
  `top_thickness_m` (0.018–0.040 m).

## Rejected

- Bi-fold split tops and A-frame trestles: they belong to `pictureX_0611_Folding_table`.
- Caster sleds and drop leaves: they belong to `pictureX_0611_Folding_table2`.
