# Folding table (general folding table) — SourceMap

export_category: pictureX_0611_Folding_table

Authoritative records live under `<ARTI_SKILL_ROOT>/arti-template/data/records`.

Category identity: a general folding table — a tabletop plus a collapsible support mechanism. It
is a table first: the articulation must be a foldable support or a folding top, not a fixed
workbench. Neighbouring categories: `pictureX_0611_Folding_table1` owns the tube-frame
rolltop/telescoping family and `pictureX_0611_Folding_table2` the caster / drop-leaf / compact
bi-fold family.

sync_records:
  - rec_picturex0611_folding_table4_var_leg_count_n6
  - rec_picturex0611_folding_table_a_frame_trestle
  - rec_picturex0611_folding_table_scissor_base
  - rec_picturex0611_folding_table_suitcase_bifold_handle
  - rec_picturex0611_folding_table_telescoping_legs
  - rec_picturex_0611__folding_table__001__png_4c4c814847524e32a28ec810e398ef86
  - rec_picturex_0611__folding_table__002__png_f2f71083d3f24464854e6f048c746976
  - rec_picturex_0611__folding_table__003__png_20026283e1e34d9cbb817acb4dbbd289
  - rec_picturex_0611__folding_table__004__png_a30fb8a6461c4f59ae6ad0834120488b

All records are read at `revisions/rev_000001/model.py`.

## Shared host preserved by every combination

> a rigid tabletop carried at working height by N folding support assemblies, each hinged under
> the top and each able to swing flat against it.

## Accepted candidates

| Slot | Candidate | Component type | Diversity axis | Record/revision | Exact model.py:Lx-Ly | Status | Accept reason | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|---|
| top_style | single_panel | tabletop | ③ primary form family — source anchor | rec_picturex_0611__folding_table__002__png_f2f71083d3f24464854e6f048c746976/rev_000001 | model.py:L41-L149 | accepted | one rigid slatted panel with a perimeter rail; no top hinge | `tabletop` slats + rails |
| top_style | split_halves | tabletop | ② joint / mechanism type — source anchor | rec_picturex_0611__folding_table__001__png_4c4c814847524e32a28ec810e398ef86/rev_000001 | model.py:L131-L262 | accepted | two halves joined by a centre REVOLUTE seam so the top folds in half | `tabletop_half_0/1`, seam hinge |
| top_style | framed_panel | tabletop | ③ primary form family — source anchor | rec_picturex_0611__folding_table__003__png_20026283e1e34d9cbb817acb4dbbd289/rev_000001 | model.py:L37-L200 | accepted | panel carried in a perimeter beam frame with end spines | `left_top`/`right_top`, beam frame |
| top_style | suitcase_bifold_handle | tabletop | ③ primary form family — source fork | rec_picturex0611_folding_table_suitcase_bifold_handle/rev_000001 | model.py:L201-L336 | accepted | bi-fold top with latch tabs and a carry handle on the seam | latch tabs, handle |
| support_style | folding_legs | support | ② joint type — source anchor | rec_picturex_0611__folding_table__001__png_4c4c814847524e32a28ec810e398ef86/rev_000001 | model.py:L263-L400 | accepted | independently folding tube legs on under-top brackets | `leg_i`, revolute about the depth axis |
| support_style | webbed_legs | support | ③ form family — source anchor | rec_picturex_0611__folding_table__002__png_f2f71083d3f24464854e6f048c746976/rev_000001 | model.py:L29-L210 | accepted | flat webbed leg panels folding under the top | `leg_i` web panel |
| support_style | brace_legs | support | ② joint type — source anchor | rec_picturex_0611__folding_table__004__png_a30fb8a6461c4f59ae6ad0834120488b/rev_000001 | model.py:L130-L340 | accepted | leg pairs with a separate locking brace link | `leg_pair_i`, `brace_i` |
| support_style | beam_frame | support | ③ form family — source anchor | rec_picturex_0611__folding_table__003__png_20026283e1e34d9cbb817acb4dbbd289/rev_000001 | model.py:L201-L330 | accepted | beam spine carrying end frames instead of separate legs | beam spine, end frames |
| support_style | scissor_base | support | ② joint type — source fork | rec_picturex0611_folding_table_scissor_base/rev_000001 | model.py:L142-L260 | accepted | crossed scissor arms collapsing under the top | `scissor_arm_i` |
| support_style | a_frame_trestle | support | ③ form family — source fork | rec_picturex0611_folding_table_a_frame_trestle/rev_000001 | model.py:L141-L400 | accepted | paired A-frame trestles with a spreader bar | `trestle_i`, spreader |
| support_style | telescoping_legs | support | ② joint type — source fork | rec_picturex0611_folding_table_telescoping_legs/rev_000001 | model.py:L152-L295 | accepted | outer leg plus a PRISMATIC inner leg section | `leg_i`, `leg_inner_i` |
| foot_style | flat_glide | foot | ① structural detail — source anchor | rec_picturex_0611__folding_table__002__png_f2f71083d3f24464854e6f048c746976/rev_000001 | model.py:L150-L210 | accepted | flat glide pads under each leg | glide pads |
| foot_style | swivel_pad | foot | ① structural detail — source anchor | rec_picturex_0611__folding_table__001__png_4c4c814847524e32a28ec810e398ef86/rev_000001 | model.py:L300-L346 | accepted | swivelling foot pads on a stem | foot stems + pads |
| foot_style | floor_rail | foot | ① structural detail — source fork | rec_picturex0611_folding_table_a_frame_trestle/rev_000001 | model.py:L191-L223 | accepted | a floor rail spreads the load under each support | spreader/floor rail |
| leg_count | leg_count_n4 | support multiplicity | N — source anchor | rec_picturex_0611__folding_table__001__png_4c4c814847524e32a28ec810e398ef86/rev_000001 | model.py:L263-L400 | accepted | four independently folding legs | leg_0..3 |
| leg_count | leg_count_n6 | support multiplicity | N — host capacity evidence | rec_picturex0611_folding_table4_var_leg_count_n6/rev_000001 | model.py:L40-L200 | accepted | six-leg instance proving the leg loop stays index-general | leg_0..5 |
| leg_count | leg_pair_n2 | support multiplicity | N — source anchor | rec_picturex_0611__folding_table__004__png_a30fb8a6461c4f59ae6ad0834120488b/rev_000001 | model.py:L304-L400 | accepted | two folding leg assemblies (pairs) under a bi-fold top | leg_pair_0/1 |

`core_domain = 4 (top_style) x 7 (support_style) x 3 (foot_style) = 84`;
`raw_domain = 84 x 3 (leg_count) = 252`.

Host adaptation instead of gates: every `top_style` exports the same under-top interface (top
plane z, usable half-length, half-depth, and the hinge line for each support station); the
`support_style` candidates consume only that interface and the `foot_style` candidates only the
support's foot plane, so all 84 combinations build without a compatibility gate.

## Multiplicity and N derivation

- `leg_count = 2 | 4 | 6`, applied to `support_style`.
  - `observed_N = 4` (001 four folding legs), `2` (004 leg pairs) and `6` (the n6 fork).
  - `derived_N_range = 2..6`: the support loop is index-general (stations derived from the usable
    length); the bound comes from the top length a station still needs and from the pose budget.
  - validation: each N adds one support assembly (and, for telescoping legs, its prismatic inner
    section), and re-derives the station pitch, the brace geometry and the foot spacing.

## Independent parameters (honest, not core/raw)

- `top_length_m` (0.60–1.85 m), `top_depth_m` (0.42–0.86 m), `top_height_m` (0.32–0.78 m),
  `top_thickness_m` (0.018–0.040 m).

## Rejected

- Drafting/tilt tables, ironing boards and fixed workbenches: they are other categories.
- Rolltop slat and caster-sled forks: they belong to Folding_table1 / Folding_table2.
