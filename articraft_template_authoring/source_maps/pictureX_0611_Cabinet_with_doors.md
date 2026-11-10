# pictureX 0611 Cabinet_with_doors — SourceMap

export_category: pictureX_0611_Cabinet_with_doors

Authoritative records live under `<ARTI_SKILL_ROOT>/articraft_data/data/records`.
Category identity: one grounded (or wall-hung) load-bearing carcass enclosing a storage
cavity whose PRIMARY articulation is one or more door leaves. Drawers are out of scope
(sibling subcategory), and an all-glass vitrine without a cabinet body is out of scope.

sync_records:
  - rec_picturex_0611__cabinet_with_doors__001__png__airflex_batch_20260710_bd4dc1c159114aabb8cafb2af6082234
  - rec_picturex_0611__cabinet_with_doors__002__png__airflex_batch_20260710_561d6843d38e43fc97b410320d94e273
  - rec_picturex_0611__cabinet_with_doors__003__png__airflex_batch_20260710_12a242b290fd4dba8e000851a219e985
  - rec_picturex_0611__cabinet_with_doors__004__png__airflex_batch_20260710_01eba6da12584fa6b5a0b31b1845c152
  - rec_picturex_0611__cabinet_with_doors__005__png__airflex_batch_20260710_77e13e813dc946b7a78cb9f35059e9ab
  - rec_cabinet_with_doors_var_tapered_body
  - rec_cabinet_with_doors_var_flush_slab_doors
  - rec_cabinet_with_doors_var_sliding_doors
  - rec_cabinet_with_doors_var_bifold_door
  - rec_cabinet_with_doors_var_plinth_base
  - rec_cabinet_with_doors_var_wall_mounted
  - rec_cabinet_with_doors_var_single_door
  - rec_cabinet_with_doors_var_probe_single_door_cylindrical

## Accepted candidates

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| body_form | rect_box | rectilinear panel carcass | rec_picturex_0611__cabinet_with_doors__002__png__airflex_batch_20260710_561d6843d38e43fc97b410320d94e273/rev_000001 | model.py:L138-L215 | accepted | two side panels, top slab, base panel and inset back board bounding a real cavity |
| body_form | curved_bow_shell | swept annular shell | rec_picturex_0611__cabinet_with_doors__001__png__airflex_batch_20260710_bd4dc1c159114aabb8cafb2af6082234/rev_000001 | model.py:L41-L111; model.py:L213-L262 | accepted | `_arc_points`/`_extruded_polygon`/`_carcass_shell_shape` build a real annular drum wall with a front opening arc |
| body_form | tapered_box | lofted trapezoid carcass | rec_cabinet_with_doors_var_tapered_body/rev_000001 | model.py:L185-L265 | accepted | side panels lean inward from base to top, top slab narrower than the base panel |
| door_kind | framed_cane | stile/rail frame with woven field | rec_picturex_0611__cabinet_with_doors__002__png__airflex_batch_20260710_561d6843d38e43fc97b410320d94e273/rev_000001 | model.py:L42-L137 | accepted | `_add_door_visuals` builds outer/inner stiles, top/bottom rails and a woven cane field with brass pull |
| door_kind | glazed_curtain | glazed frame with gathered backing | rec_picturex_0611__cabinet_with_doors__004__png__airflex_batch_20260710_01eba6da12584fa6b5a0b31b1845c152/rev_000001 | model.py:L96-L242 | accepted | glass field inside a frame with a pleated curtain backing and drop pull |
| door_kind | fretwork_pierced | pierced scroll carved leaf | rec_picturex_0611__cabinet_with_doors__003__png__airflex_batch_20260710_12a242b290fd4dba8e000851a219e985/rev_000001 | model.py:L51-L148 | accepted | `_ornamental_door_mesh` composes real pierced blocks in front of a recessed backing |
| door_kind | raised_panel | moulded raised-field leaf | rec_picturex_0611__cabinet_with_doors__005__png__airflex_batch_20260710_77e13e813dc946b7a78cb9f35059e9ab/rev_000001 | model.py:L76-L146 | accepted | `_lower_door_wood` raises a bevelled centre field inside a moulded surround |
| door_kind | flush_slab | flat solid slab leaf | rec_cabinet_with_doors_var_flush_slab_doors/rev_000001 | model.py:L39-L80 | accepted | single-thickness slab leaf with a surface-mounted pull, no frame |
| door_mechanism | revolute_swing | vertical butt hinge | rec_picturex_0611__cabinet_with_doors__002__png__airflex_batch_20260710_561d6843d38e43fc97b410320d94e273/rev_000001 | model.py:L216-L293 | accepted | `carcass_to_door_*` REVOLUTE about the jamb-inset hinge line, outward limits |
| door_mechanism | sliding_bypass | offset bypass tracks | rec_cabinet_with_doors_var_sliding_doors/rev_000001 | model.py:L140-L260 | accepted | two leaves on front/rear tracks with PRISMATIC travel along the opening |
| door_mechanism | bifold | folding leaf pair | rec_cabinet_with_doors_var_bifold_door/rev_000001 | model.py:L146-L280 | accepted | primary leaf on the carcass jamb plus a second leaf folding off its leading stile |
| support_base | metal_legs | slender steel legs | rec_picturex_0611__cabinet_with_doors__001__png__airflex_batch_20260710_bd4dc1c159114aabb8cafb2af6082234/rev_000001 | model.py:L162-L193 | accepted | `_add_leg` round painted-steel legs with floor glides |
| support_base | dowel_legs | turned wood dowel legs | rec_picturex_0611__cabinet_with_doors__002__png__airflex_batch_20260710_561d6843d38e43fc97b410320d94e273/rev_000001 | model.py:L216-L260 | accepted | four round wood legs seated in visible sockets under the base panel |
| support_base | turned_feet | lathe-turned feet | rec_picturex_0611__cabinet_with_doors__004__png__airflex_batch_20260710_01eba6da12584fa6b5a0b31b1845c152/rev_000001 | model.py:L25-L95 | accepted | `_turned_foot_mesh` lathe profile plus scalloped apron band |
| support_base | feet_plinth | bracket feet on a moulded plinth | rec_picturex_0611__cabinet_with_doors__003__png__airflex_batch_20260710_12a242b290fd4dba8e000851a219e985/rev_000001 | model.py:L149-L171 | accepted | `_plinth_rail_mesh` moulded plinth carried on corner bracket feet |
| support_base | recessed_plinth | recessed toe-kick box | rec_cabinet_with_doors_var_plinth_base/rev_000001 | model.py:L141-L200 | accepted | continuous recessed plinth box under the base panel, no legs |
| support_base | wall_mount | rear hanging cleats | rec_cabinet_with_doors_var_wall_mounted/rev_000001 | model.py:L139-L200 | accepted | rail and mounting plates on the back panel, no floor support |
| interior_fitment | plain_shelf | flat slab shelf | rec_picturex_0611__cabinet_with_doors__002__png__airflex_batch_20260710_561d6843d38e43fc97b410320d94e273/rev_000001 | model.py:L210-L220 | accepted | plain interior shelf spanning between the side panels |
| interior_fitment | edge_banded_shelf | shelf with a front edge band | rec_picturex_0611__cabinet_with_doors__001__png__airflex_batch_20260710_bd4dc1c159114aabb8cafb2af6082234/rev_000001 | model.py:L112-L129; model.py:L258-L270 | accepted | `_middle_shelf_shape` plus a distinct `shelf_front_edge` band along the shelf nose |

## Rejected

- tambour / roll-top and accordion (>2 leaf) fronts: no source record in this subcategory.
- vitrine-only all-glass box and any drawer front: excluded by the subcategory contract.
- separate `curved_slab` door candidate: the leaf curvature is a cross-slot derivation from
  `body_form=curved_bow_shell` (origin 001), not an independent front treatment. Keeping it as a
  door_kind candidate would duplicate `flush_slab` on a curved host and force an artificial
  compatibility gate.

## Multiplicity

- `door_count = 1 | 2 | 3 | 4`, applied to `door_kind`.
  N=1 `rec_cabinet_with_doors_var_single_door/rev_000001` model.py:L254-L285;
  N=2 origins 001/002/003; N=3 origin 004 (row of three);
  N=4 origin 005 (two tiers of two, model.py:L209-L340).
  Every leaf is an independent moving child with its own joint; the row/tier layout, cell pitch,
  leaf width, hinge line and interior swing limits derive from N and the opening width.
- `shelf_count = 1 | 2 | 3`, applied to `interior_fitment`.
  N=1 origin 002 (`interior_shelf`), N=2 origin 004 (`shelf_0`/`shelf_1` model.py:L310-L330),
  N=3 origin 003 (`shelf_{index}` loop model.py:L216-L235).
  Shelf pitch, span and depth derive from the cavity and from the mechanism's front intrusion.

## Parameters and derivations

- `carcass_width_m`, `carcass_depth_m`, `carcass_height_m` are template-level and metre-valued;
  the curved host derives its radius from width and keeps a circular footprint.
- `door_swing_rad` bounds the outward hinge travel; interior leaves in a row derive a reduced
  upper limit from their neighbour geometry instead of relying on an overlap allowance.
- `slide_travel_m` bounds bypass travel and is clamped by the real opening and leaf width.
- Support height, plinth depth and cleat height derive per support candidate; the cavity floor,
  shelf ladder and door row heights all derive from the resulting body bottom.

## Cross-slot host adaptation

- `curved_bow_shell` derives a flat chord front frame across its opening, so flat-front leaves,
  bypass tracks and fold hinges mount on a real planar jamb. A swinging leaf on this host keeps the
  source-001 curved slab profile struck from the same annulus; sliding and folding leaves use the
  chord frame.
- `tapered_box` derives its door opening from the narrowest (top) width so a leaf clears the
  leaning side panels through its full travel, and its track/fold hardware follows the same width.
- `wall_mount` removes the floor support but still derives a full cavity floor and cleat spacing
  from the carcass, so the door rows are unchanged.

## Category identity and motion

- Exactly one `carcass` part carrying the side/top/base/back structure and the support base.
- At least one leaf part per declared door, each a moving non-fixed child of the carcass.
- Swing leaves rotate about a vertical hinge line registered through `mate_axes`; bypass leaves
  translate along the opening; bifold pairs add a second leaf folding off the primary leading stile.
- Shelves are fused carcass geometry seated on a real supporting footprint inside the cavity.
