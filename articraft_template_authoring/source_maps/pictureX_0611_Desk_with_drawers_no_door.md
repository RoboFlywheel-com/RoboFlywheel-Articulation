# pictureX 0611 Desk_with_drawers (no door) — SourceMap

export_category: pictureX_0611_Desk_with_drawers_no_door

Authoritative records live under `<ARTI_SKILL_ROOT>/arti-template/data/records`.
Category identity: a writing desk whose only articulation is a set of pull-out drawers under a
worktop. There is no door of any kind: a swinging or sliding leaf puts the object in a sibling
subcategory, and a bare table with no drawer is out of scope.

sync_records:
  - rec_picturex_0611__desk_with_drawers_no_door__001__png__airflex_batch_20260710_0a4495b8d3674ce895b5dcc93b34fa8b
  - rec_picturex_0611__desk_with_drawers_no_door__002__png__airflex_batch_20260710_7613e188f1a643e0ae2025f65a32cc54
  - rec_picturex_0611__desk_with_drawers_no_door__003__png__airflex_batch_20260710_e8f92b30f5d64469bc7be694c4008080
  - rec_picturex_0611__desk_with_drawers_no_door__004__png__airflex_batch_20260710_d23b1cac1d54454d99cc04c6c0bc6fcf
  - rec_picturex_0611__desk_with_drawers_no_door__005__png__airflex_batch_20260710_69a514c4d7e942d49d0a196cbfa9012b
  - rec_picturex0611_desk_with_drawers_fork_twin_pedestal_n8_20260714
  - rec_picturex0611_desk_with_drawers_fork_shallow_apron_n2_20260714
  - rec_picturex0611_desk_with_drawers_fork_l_shaped_return_20260714

## Accepted candidates

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| desk_form | single_pedestal | one drawer pedestal beside a knee hole | rec_picturex_0611__desk_with_drawers_no_door__005__png__airflex_batch_20260710_69a514c4d7e942d49d0a196cbfa9012b/rev_000001 | model.py:L137-L319 | accepted | one pedestal carries the drawer stack, the other side stands on legs |
| desk_form | twin_pedestal | drawer pedestal on both sides | rec_picturex0611_desk_with_drawers_fork_twin_pedestal_n8_20260714/rev_000001 | model.py:L155-L320 | accepted | mirrored pedestals with a knee hole between them |
| desk_form | apron_rail_desk | shallow apron rail under the top | rec_picturex_0611__desk_with_drawers_no_door__004__png__airflex_batch_20260710_d23b1cac1d54454d99cc04c6c0bc6fcf/rev_000001 | model.py:L24-L55 | accepted | `_turned_leg_geometry`/`_arched_apron_geometry` carry shallow drawers on an apron |
| desk_form | l_shaped_return | main run plus a rear return wing | rec_picturex0611_desk_with_drawers_fork_l_shaped_return_20260714/rev_000001 | model.py:L47-L386 | accepted | a second worktop wing returns from the main run on its own support |
| leg_form | turned_legs | lathe-turned legs | rec_picturex_0611__desk_with_drawers_no_door__004__png__airflex_batch_20260710_d23b1cac1d54454d99cc04c6c0bc6fcf/rev_000001 | model.py:L24-L44 | accepted | `_turned_leg_geometry` real turned profile |
| leg_form | tapered_legs | square tapered legs | rec_picturex_0611__desk_with_drawers_no_door__002__png__airflex_batch_20260710_7613e188f1a643e0ae2025f65a32cc54/rev_000001 | model.py:L17-L328 | accepted | square legs tapering toward the floor |
| leg_form | hairpin_frame | slim metal frame legs | rec_picturex_0611__desk_with_drawers_no_door__003__png__airflex_batch_20260710_e8f92b30f5d64469bc7be694c4008080/rev_000001 | model.py:L22-L43 | accepted | `_add_cylinder_between` builds a real bent metal frame |
| leg_form | panel_end | solid panel end supports | rec_picturex_0611__desk_with_drawers_no_door__001__png__airflex_batch_20260710_0a4495b8d3674ce895b5dcc93b34fa8b/rev_000001 | model.py:L30-L51 | accepted | `_hood_cheek` solid end cheeks carrying the top |
| drawer_front | bail_pull_front | moulded front with a bail pull | rec_picturex_0611__desk_with_drawers_no_door__001__png__airflex_batch_20260710_0a4495b8d3674ce895b5dcc93b34fa8b/rev_000001 | model.py:L61-L151 | accepted | `_add_bail_pull`/`_add_main_drawer` moulded front with a swing bail |
| drawer_front | flush_front | flush front with a recessed grip | rec_picturex_0611__desk_with_drawers_no_door__003__png__airflex_batch_20260710_e8f92b30f5d64469bc7be694c4008080/rev_000001 | model.py:L44-L306 | accepted | flush fronts with a routed finger grip |
| drawer_front | lipped_front | lipped/edge-banded front | rec_picturex_0611__desk_with_drawers_no_door__005__png__airflex_batch_20260710_69a514c4d7e942d49d0a196cbfa9012b/rev_000001 | model.py:L21-L136 | accepted | `_add_drawer` front with a proud lip and a knob |
| top_form | rect_top | rectangular worktop | rec_picturex_0611__desk_with_drawers_no_door__002__png__airflex_batch_20260710_7613e188f1a643e0ae2025f65a32cc54/rev_000001 | model.py:L17-L200 | accepted | plain rectangular worktop with a square edge |
| top_form | leather_inset_top | leather writing field inset in the top | rec_picturex_0611__desk_with_drawers_no_door__001__png__airflex_batch_20260710_0a4495b8d3674ce895b5dcc93b34fa8b/rev_000001 | model.py:L219-L400 | accepted | a real inset writing field with a surrounding timber border |
| top_form | bullnose_top | thick top with a rounded front edge | rec_picturex0611_desk_with_drawers_fork_shallow_apron_n2_20260714/rev_000001 | model.py:L56-L355 | accepted | a thicker top whose front edge is rounded over |

## Rejected

- doors, hutches and roll fronts: excluded by the subcategory contract (`no_door`).
- pull styles beyond the three accepted front families: derived detail, not independent slots.

## Multiplicity

- `drawer_count = 1 | 2 | 3 | 4 | 5 | 6`, applied to `drawer_front`.
  N=2 `rec_picturex0611_desk_with_drawers_fork_shallow_apron_n2_20260714/rev_000001`
  model.py:L56-L355 (shallow apron pair);
  N=3 origin 005 (single pedestal stack, model.py:L137-L319);
  N=8-class evidence from `rec_picturex0611_desk_with_drawers_fork_twin_pedestal_n8_20260714/rev_000001`
  model.py:L37-L154, whose loop distributes the trays over both pedestals; the template caps N at 6
  so every tray keeps a real front height on the smallest desk.
  Tray width, front height, box depth and travel derive from the host pedestal or apron and from N.

## Parameters and derivations

- `desk_width_m`, `desk_depth_m`, `desk_height_m` are candidate-local to `desk_form`;
  the L-shaped form derives its return wing from the same worktop thickness and leg family.
- The drawer zone is derived per form: one pedestal, two pedestals, a shallow apron band, or the
  main run of the L, and N is distributed over the available pedestals.

## Category identity and motion

- Exactly one `desk` carcass part carrying the worktop, the legs or pedestals and the runner rails.
- N moving `drawer` parts, each a hollow tray on its own prismatic slide along -Y.
- No revolute joint and no door leaf exists in any combination.
