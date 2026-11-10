# Folding table 2 (caster / drop-leaf compact folding table) — SourceMap

export_category: pictureX_0611_Folding_table2

Authoritative records live under `<ARTI_SKILL_ROOT>/arti-template/data/records`.

Category identity: a compact folding table whose top carries a real moving leaf — a bi-fold half,
a drop leaf, a butterfly centre leaf or a latched tilting section — over folding supports that may
stand on casters. Neighbouring categories: `pictureX_0611_Folding_table` owns the general
bi-fold/trestle family and `pictureX_0611_Folding_table1` the tube-frame rolltop family.

sync_records:
  - rec_picturex0611_folding_table2_bifold_top
  - rec_picturex0611_folding_table2_butterfly_center_leaf
  - rec_picturex0611_folding_table2_drop_leaf_side
  - rec_picturex0611_folding_table2_dual_caster_sled
  - rec_picturex0611_folding_table2_four_corner_legs
  - rec_picturex0611_folding_table2_tilting_top_latch
  - rec_picturex0611_folding_table2_x_trestle_base
  - rec_picturex_0611__folding_table2__001__png_49f1fec0c3e148ed97f2cdfdb905c116

All records are read at `revisions/rev_000001/model.py`.

## Shared host preserved by every combination

> a fixed tabletop plus exactly one moving leaf, carried at working height by N folding supports
> hinged under the fixed top.

## Accepted candidates

| Slot | Candidate | Component type | Diversity axis | Record/revision | Exact model.py:Lx-Ly | Status | Accept reason | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|---|
| top_style | bifold_top | tabletop | ② joint / mechanism type — source fork | rec_picturex0611_folding_table2_bifold_top/rev_000001 | model.py:L110-L280 | accepted | the top folds in half on a centre REVOLUTE seam | root half + leaf |
| top_style | drop_leaf_side | tabletop | ② joint / mechanism type — source fork | rec_picturex0611_folding_table2_drop_leaf_side/rev_000001 | model.py:L110-L280 | accepted | a side leaf drops on a long-edge hinge | leaf + hinge (1,0,0) |
| top_style | butterfly_center_leaf | tabletop | ② joint / mechanism type — source fork | rec_picturex0611_folding_table2_butterfly_center_leaf/rev_000001 | model.py:L110-L280 | accepted | a centre leaf flips up out of the top | leaf + hinge (0,1,0) |
| top_style | tilting_top_latch | tabletop | ② joint / mechanism type — source fork | rec_picturex0611_folding_table2_tilting_top_latch/rev_000001 | model.py:L110-L280 | accepted | a latched rear section tilts up | leaf + latch tabs |
| support_style | four_corner_legs | support | ② joint type — source fork | rec_picturex0611_folding_table2_four_corner_legs/rev_000001 | model.py:L110-L300 | accepted | folding corner leg pairs under the top | `leg_i` tubes |
| support_style | x_trestle_base | support | ③ form family — source fork | rec_picturex0611_folding_table2_x_trestle_base/rev_000001 | model.py:L110-L300 | accepted | crossed trestle arms collapsing under the top | X arms |
| support_style | caster_sled | support | ③ form family — source anchor | rec_picturex_0611__folding_table2__001__png_49f1fec0c3e148ed97f2cdfdb905c116/rev_000001 | model.py:L110-L300 | accepted | a sled frame carrying the table on casters | sled frame |
| foot_style | flat_glide | foot | ① structural detail — source anchor | rec_picturex_0611__folding_table2__001__png_49f1fec0c3e148ed97f2cdfdb905c116/rev_000001 | model.py:L110-L300 | accepted | flat glide pads under each support | glide pads |
| foot_style | caster_wheels | foot | ① structural detail — source fork | rec_picturex0611_folding_table2_dual_caster_sled/rev_000001 | model.py:L156-L431 | accepted | swivel casters on short stems | caster stems + wheels |
| foot_style | brake_pad | foot | ① structural detail — source fork | rec_picturex0611_folding_table2_tilting_top_latch/rev_000001 | model.py:L191-L223 | accepted | a broad braked pad spreading the load | brake pads |
| leg_count | leg_count_n4 | support multiplicity | N — source fork | rec_picturex0611_folding_table2_four_corner_legs/rev_000001 | model.py:L110-L300 | accepted | four folding stations | leg_0..3 |
| leg_count | leg_count_n2 | support multiplicity | N — source fork | rec_picturex0611_folding_table2_dual_caster_sled/rev_000001 | model.py:L156-L431 | accepted | two sled stations | leg_0..1 |
| leg_count | x_trestle_capacity | support multiplicity | N — host capacity evidence | rec_picturex0611_folding_table2_x_trestle_base/rev_000001 | model.py:L110-L300 | accepted | the trestle loop stays index-general | trestle stations |

`core_domain = 4 (top_style) x 3 (support_style) x 3 (foot_style) = 36`;
`raw_domain = 36 x 3 (leg_count) = 108`.

Host adaptation instead of gates: every `top_style` exports the same under-top interface and one
leaf hinge line; `support_style` consumes only the under-top interface and reports its foot
positions to `foot_style`, so all 36 combinations build without a compatibility gate.

## Multiplicity and N derivation

- `leg_count = 2 | 4 | 6`, applied to `support_style`; `derived_N_range = 2..6` from the top
  length a station still needs and the pose budget. Each N re-derives the station pitch, the fold
  limit, the trestle reach and the foot spacing.

## Independent parameters (honest, not core/raw)

- `top_length_m` (0.60–1.85 m), `top_depth_m` (0.42–0.86 m), `top_height_m` (0.32–0.78 m),
  `top_thickness_m` (0.018–0.040 m).

## Rejected

- Rolltop slat decks and telescoping tube legs: they belong to `pictureX_0611_Folding_table1`.
- A-frame trestles and beam frames: they belong to `pictureX_0611_Folding_table`.
