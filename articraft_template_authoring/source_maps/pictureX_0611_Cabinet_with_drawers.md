# pictureX 0611 Cabinet_with_drawers — SourceMap

export_category: pictureX_0611_Cabinet_with_drawers

Authoritative records live under `<ARTI_SKILL_ROOT>/articraft_data/data/records`.
Category identity: a chest/dresser whose ONLY articulation is a set of pull-out drawers.
Every front opening is an independently sliding drawer; a swinging door leaf, a mixed
door+drawer sideboard, or open shelving is out of scope.

sync_records:
  - rec_picturex_0611__cabinet_with_drawers__001__png__airflex_batch_20260710_0739738ec7c94c7a8fd90660717f6585
  - rec_picturex_0611__cabinet_with_drawers__002__png__airflex_batch_20260710_7ff0d3b16d3f45a98e6d3f14ce3c21dd
  - rec_picturex_0611__cabinet_with_drawers__003__png__airflex_batch_20260710_26b9fe0822b64bcb80964e503e2567b2
  - rec_picturex_0611__cabinet_with_drawers__004__png__airflex_batch_20260710_9e2d698894684622a88e1b1d3dbcf16d
  - rec_picturex_0611__cabinet_with_drawers__005__png__airflex_batch_20260710_9d0d00f317a34743a1733e46730a4a6d
  - rec_cabinet_with_drawers_var_bowfront
  - rec_cabinet_with_drawers_var_tapered
  - rec_cabinet_with_drawers_var_toekick
  - rec_cabinet_with_drawers_var_grid2x2
  - rec_cabinet_with_drawers_var_n2
  - rec_cabinet_with_drawers_var_n4
  - rec_cabinet_with_drawers_var_n6

## Accepted candidates

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| body_form | rect_case | rectilinear panel carcass | rec_picturex_0611__cabinet_with_drawers__003__png__airflex_batch_20260710_26b9fe0822b64bcb80964e503e2567b2/rev_000001 | model.py:L226-L300 | accepted | straight side/back panels, top slab and framed front with square drawer openings |
| body_form | bombe_serpentine | double-curved swelling case | rec_picturex_0611__cabinet_with_drawers__001__png__airflex_batch_20260710_0739738ec7c94c7a8fd90660717f6585/rev_000001 | model.py:L26-L61; model.py:L278-L340 | accepted | `_curved_front`/`_front_y` bulge the front and sides so every drawer front follows the swell |
| body_form | oval_rounded | rounded oval-ended prism | rec_picturex_0611__cabinet_with_drawers__002__png__airflex_batch_20260710_7ff0d3b16d3f45a98e6d3f14ce3c21dd/rev_000001 | model.py:L36-L52; model.py:L127-L149 | accepted | `_rounded_prism`/`_carcass_shell` build an oval-ended shell with matching curved drawer fronts |
| body_form | bow_front | convex front only | rec_cabinet_with_drawers_var_bowfront/rev_000001 | model.py:L31-L119 | accepted | `_bow_front_profile_2d`/`_bow_front_mesh` bow the front while the sides stay straight |
| body_form | tapered_case | canted case | rec_cabinet_with_drawers_var_tapered/rev_000001 | model.py:L30-L58 | accepted | `_taper_offset`/`_tapered_panel_mesh` lean the side panels inward with height |
| drawer_layout | full_width_stack | graduated full-width stack | rec_picturex_0611__cabinet_with_drawers__003__png__airflex_batch_20260710_26b9fe0822b64bcb80964e503e2567b2/rev_000001 | model.py:L81-L225 | accepted | one full-width drawer per level with graduated front heights |
| drawer_layout | paired_grid | side-by-side column grid | rec_picturex_0611__cabinet_with_drawers__004__png__airflex_batch_20260710_9e2d698894684622a88e1b1d3dbcf16d/rev_000001 | model.py:L61-L167 | accepted | centre divider with `drawer_{row}_{col}` pairs on every level |
| drawer_layout | pair_over_full_width | mixed pairs over a full-width base | rec_picturex_0611__cabinet_with_drawers__005__png__airflex_batch_20260710_9d0d00f317a34743a1733e46730a4a6d/rev_000001 | model.py:L139-L202 | accepted | centre mullion with paired upper levels over a full-width deep bottom drawer |
| drawer_front | flat_panel | plain slab front | rec_cabinet_with_drawers_var_n4/rev_000001 | model.py:L52-L90 | accepted | plain graduated front with a small round pull |
| drawer_front | framed_cane | framed woven cane front | rec_picturex_0611__cabinet_with_drawers__004__png__airflex_batch_20260710_9e2d698894684622a88e1b1d3dbcf16d/rev_000001 | model.py:L61-L167 | accepted | cane field inside a moulded front frame with reeds |
| drawer_front | gothic_arch | pointed-arch tracery front | rec_picturex_0611__cabinet_with_drawers__003__png__airflex_batch_20260710_26b9fe0822b64bcb80964e503e2567b2/rev_000001 | model.py:L31-L64 | accepted | `_front_segment` builds the gothic slope/leg/sill tracery on the drawer face |
| drawer_front | applique_moulded | moulded front with brass appliqué | rec_picturex_0611__cabinet_with_drawers__001__png__airflex_batch_20260710_0739738ec7c94c7a8fd90660717f6585/rev_000001 | model.py:L91-L152 | accepted | `_add_center_applique`/`_add_corner_scrolls` crest and scrollwork on a moulded front |
| support_base | cabriole_apron | cabriole legs with a scalloped apron | rec_picturex_0611__cabinet_with_drawers__001__png__airflex_batch_20260710_0739738ec7c94c7a8fd90660717f6585/rev_000001 | model.py:L278-L340 | accepted | swept side posts continuing into a shaped front apron |
| support_base | fine_metal_legs | fine brass cylindrical legs | rec_picturex_0611__cabinet_with_drawers__002__png__airflex_batch_20260710_7ff0d3b16d3f45a98e6d3f14ce3c21dd/rev_000001 | model.py:L150-L230 | accepted | four slender brass legs with turned feet under a rounded shell |
| support_base | plinth_block_feet | stepped plinth on block feet | rec_picturex_0611__cabinet_with_drawers__003__png__airflex_batch_20260710_26b9fe0822b64bcb80964e503e2567b2/rev_000001 | model.py:L226-L300 | accepted | moulded base plinth carried on square block feet |
| support_base | splayed_tapered_legs | splayed tapered legs with shoes | rec_picturex_0611__cabinet_with_drawers__004__png__airflex_batch_20260710_9e2d698894684622a88e1b1d3dbcf16d/rev_000001 | model.py:L50-L60 | accepted | `_tapered_leg` splayed legs with brass mounting shoes |
| support_base | tapered_legs_apron | tapered legs with a scalloped apron | rec_picturex_0611__cabinet_with_drawers__005__png__airflex_batch_20260710_9d0d00f317a34743a1733e46730a4a6d/rev_000001 | model.py:L40-L80 | accepted | `_tapered_leg_mesh` plus `_front_apron_mesh` shaped skirt |
| support_base | toe_kick_plinth | recessed toe-kick plinth | rec_cabinet_with_drawers_var_toekick/rev_000001 | model.py:L40-L120 | accepted | continuous recessed plinth replacing the legs, flush to the floor |

## Rejected

- separate pull styles as a slot: knob / handleless / turned wood / bail plate change only small
  surface hardware, so they are derived from `drawer_front` instead of forming an independent slot.
- swinging door leaves and door+drawer mixes: excluded by the subcategory contract.

## Multiplicity

- `drawer_count = 2 | 3 | 4 | 5 | 6`, applied to `drawer_front`.
  N=2 `rec_cabinet_with_drawers_var_n2/rev_000001` model.py:L182-L260;
  N=3 origins 001/002/003; N=4 `rec_cabinet_with_drawers_var_n4/rev_000001` model.py:L166-L240
  and `rec_cabinet_with_drawers_var_grid2x2/rev_000001` model.py:L172-L250;
  N=5 origin 005; N=6 origin 004 (2x3 grid) and
  `rec_cabinet_with_drawers_var_n6/rev_000001` model.py:L208-L300.
  Every drawer is an independent hollow tray with its own prismatic slide and its own runner pair.
  Level pitch, front heights, runner heights, divider height and travel all derive from N and the
  layout candidate; the bottom level is graduated deeper exactly as in the origins.

## Parameters and derivations

- `carcass_width_m`, `carcass_depth_m`, `carcass_height_m` are candidate-local to `body_form`;
  the oval and bombe cases derive their plan profile from the same width/depth.
- `drawer_travel_ratio` bounds the slide as a fraction of the real box depth so the runner stays
  engaged with its rail at full extension.
- Front curvature is a cross-slot derivation: each drawer front is struck from the host's own plan
  profile over that drawer's x-range, so a bombe, bow or oval case gets curved fronts and a
  rectilinear or tapered case gets flat ones.

## Category identity and motion

- Exactly one `carcass` part carrying the shell, the support base, the runner rails and any divider.
- N `drawer` parts, each a hollow tray (bottom, two sides, rear wall, front) — never a solid block.
- One prismatic joint per drawer along -Y with lower=0 at closed and upper=travel at open.
- Runners sit on the drawer's left and right sides and stay engaged with the carcass rails through
  the full travel; no cross-drawer bar is used as a runner.
