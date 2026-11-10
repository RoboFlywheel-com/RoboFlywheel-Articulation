# pictureX 0611 Cabinet_with_doors_and_drawers — SourceMap

export_category: pictureX_0611_Cabinet_with_doors_and_drawers

Authoritative records live under `<ARTI_SKILL_ROOT>/articraft_data/data/records`.
Category identity: a cabinet or sideboard that combines BOTH an openable door and a stack of
pull-out drawers on one load-bearing carcass. The co-existence of the two mechanisms is the
defining trait: a doors-only cabinet or a drawers-only chest is out of scope.

sync_records:
  - rec_picturex_0611__cabinet_with_doors_and_drawers__001__png__airflex_batch_20260710_b26f14a0a8da4826b66cc6fc0294d744
  - rec_picturex_0611__cabinet_with_doors_and_drawers__002__png__airflex_batch_20260710_8b60aed7a3bb4c399528842527b03ecd
  - rec_picturex_0611__cabinet_with_doors_and_drawers__003__png__airflex_batch_20260710_6c25f05e215043839872a63a4125bcf7
  - rec_picturex_0611__cabinet_with_doors_and_drawers__004__png__airflex_batch_20260710_cd51c566f69c4a0fa9ccb95e9e04b94f
  - rec_cabinet_with_doors_and_drawers_var_body_bowfront
  - rec_cabinet_with_doors_and_drawers_var_body_tapered
  - rec_cabinet_with_doors_and_drawers_var_door_sliding
  - rec_cabinet_with_doors_and_drawers_var_drawers_n2
  - rec_cabinet_with_doors_and_drawers_var_layout_drawers_over_door
  - rec_cabinet_with_doors_and_drawers_var_layout_flanking_doors
  - rec_cabinet_with_doors_and_drawers_var_support_metal_legs

## Accepted candidates

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| body_form | rect_box | straight panel carcass | rec_picturex_0611__cabinet_with_doors_and_drawers__003__png__airflex_batch_20260710_6c25f05e215043839872a63a4125bcf7/rev_000001 | model.py:L32-L72 | accepted | `_cabinet_wood_shape` builds a straight prism carcass with door and drawer zones |
| body_form | bow_front | convex front carcass | rec_cabinet_with_doors_and_drawers_var_body_bowfront/rev_000001 | model.py:L65-L137 | accepted | `_cq_bow_slab`/`_cq_bow_front`/`_cq_bow_side` arc the carcass, doors and drawer fronts together |
| body_form | tapered_box | canted carcass | rec_cabinet_with_doors_and_drawers_var_body_tapered/rev_000001 | model.py:L41-L81 | accepted | `_hw_at`/`_ihw_at`/`_trapezoid_xz` lean the side walls with height |
| storage_layout | doors_over_drawers | doors above a drawer bank | rec_picturex_0611__cabinet_with_doors_and_drawers__003__png__airflex_batch_20260710_6c25f05e215043839872a63a4125bcf7/rev_000001 | model.py:L113-L285 | accepted | two doors over one full-width drawer with a shared mid rail |
| storage_layout | drawers_over_doors | drawer bank above the doors | rec_cabinet_with_doors_and_drawers_var_layout_drawers_over_door/rev_000001 | model.py:L117-L290 | accepted | the door and drawer zones of 003 are swapped top for bottom |
| storage_layout | door_beside_drawers | door beside a drawer column | rec_picturex_0611__cabinet_with_doors_and_drawers__004__png__airflex_batch_20260710_cd51c566f69c4a0fa9ccb95e9e04b94f/rev_000001 | model.py:L200-L469 | accepted | one broad door next to a vertical stack of drawers with a centre divider |
| storage_layout | doors_flanking_drawers | doors either side of a central bank | rec_cabinet_with_doors_and_drawers_var_layout_flanking_doors/rev_000001 | model.py:L127-L280 | accepted | `_add_door_geometry` doors on both flanks of a central drawer column |
| door_kind | slab_panel | plain slab leaf | rec_picturex_0611__cabinet_with_doors_and_drawers__001__png__airflex_batch_20260710_b26f14a0a8da4826b66cc6fc0294d744/rev_000001 | model.py:L38-L66 | accepted | flush slab leaves with a shaped front cheek |
| door_kind | recessed_panel | moulded recessed-panel leaf | rec_picturex_0611__cabinet_with_doors_and_drawers__003__png__airflex_batch_20260710_6c25f05e215043839872a63a4125bcf7/rev_000001 | model.py:L73-L96 | accepted | `_door_shape`/`_door_pull_shape` recessed field with a moulded surround |
| door_kind | glazed_lattice | glazed leaf with lattice bars | rec_picturex_0611__cabinet_with_doors_and_drawers__002__png__airflex_batch_20260710_8b60aed7a3bb4c399528842527b03ecd/rev_000001 | model.py:L135-L228 | accepted | `_add_glazed_door` glass field crossed by real lattice members |
| door_mechanism | hinged_swing | vertical butt hinge | rec_picturex_0611__cabinet_with_doors_and_drawers__003__png__airflex_batch_20260710_6c25f05e215043839872a63a4125bcf7/rev_000001 | model.py:L113-L285 | accepted | `carcass_to_door_*` REVOLUTE about the jamb hinge line |
| door_mechanism | sliding_track | prismatic track door | rec_cabinet_with_doors_and_drawers_var_door_sliding/rev_000001 | model.py:L202-L476 | accepted | the leaf rides top and bottom rails on a PRISMATIC joint |
| drawer_front | plain_slab | plain drawer front | rec_cabinet_with_doors_and_drawers_var_drawers_n2/rev_000001 | model.py:L118-L201 | accepted | `_add_drawer_geometry` hollow tray with a plain front and pull |
| drawer_front | grained_slab | grained/veneered drawer front | rec_picturex_0611__cabinet_with_doors_and_drawers__004__png__airflex_batch_20260710_cd51c566f69c4a0fa9ccb95e9e04b94f/rev_000001 | model.py:L73-L115 | accepted | `_add_front_grain` lays real grain members across the drawer face |
| support_base | tapered_legs | four tapered legs | rec_picturex_0611__cabinet_with_doors_and_drawers__001__png__airflex_batch_20260710_b26f14a0a8da4826b66cc6fc0294d744/rev_000001 | model.py:L26-L37 | accepted | `_tapered_leg` slender tapered legs under the case |
| support_base | stone_plinth | solid stone plinth | rec_picturex_0611__cabinet_with_doors_and_drawers__002__png__airflex_batch_20260710_8b60aed7a3bb4c399528842527b03ecd/rev_000001 | model.py:L229-L300 | accepted | marble plinth block carrying the whole case |
| support_base | apron_feet_plinth | cutout apron plinth on feet | rec_picturex_0611__cabinet_with_doors_and_drawers__003__png__airflex_batch_20260710_6c25f05e215043839872a63a4125bcf7/rev_000001 | model.py:L113-L180 | accepted | shaped cutout apron between corner feet |
| support_base | metal_legs | slim metal legs | rec_cabinet_with_doors_and_drawers_var_support_metal_legs/rev_000001 | model.py:L200-L300 | accepted | slim metal legs with floor pads replacing the block legs |

## Rejected

- open cubby / mirror shelf zones: recorded in 001 and 002 as fixed carcass geometry, derived here
  from the layout rather than declared as an independent slot.
- drawers-only or doors-only variants: excluded by the subcategory contract.

## Multiplicity

- `drawer_count = 1 | 2 | 3 | 4`, applied to `drawer_front`.
  N=1 origin 003 (single full-width drawer, model.py:L97-L112);
  N=2 `rec_cabinet_with_doors_and_drawers_var_drawers_n2/rev_000001` model.py:L118-L201;
  N=3 origin 004 (stacked column, model.py:L116-L199);
  N=4 origin 001 (four-drawer bank, model.py:L67-L351).
  Every drawer is an independent hollow tray on its own prismatic slide with its own runner pair.
  The drawer zone height, level pitch, tray width, box depth and travel derive from N and from the
  layout candidate.
- Door count is not an independent multiplicity: it is derived from the layout
  (one broad leaf beside the drawers, one leaf per flank, or a pair across the door zone).

## Parameters and derivations

- `carcass_width_m`, `carcass_depth_m`, `carcass_height_m` are candidate-local to `body_form`.
- `door_zone_ratio` splits the case between the door zone and the drawer zone; the mid rail,
  the hinge stiles and the drawer ladder all derive from it.
- Door leaf curvature and drawer front curvature are cross-slot derivations from the host plan
  profile, so a bow-front case gets arced doors and drawer fronts.

## Category identity and motion

- Exactly one `carcass` part carrying the case shell, the support base, the mid rail, the divider
  and the runner rails.
- At least one `door_leaf` part (revolute about a vertical hinge, or prismatic on a track) AND at
  least one `drawer` part (prismatic along -Y): both mechanisms are always present.
- Drawers are hollow trays; door leaves are overlay leaves clear of the carcass face.
