# drawer_cabinet_with_sliding_drawers — SourceMap

source_map_schema: 1
export_category: drawer_cabinet_with_sliding_drawers
picture_category: 0611
picture_subcategory: Cabinet_with_drawers
category_scope: A freestanding drawer chest with one load-bearing carcass and only independently prismatic hollow drawers; door leaves and open shelving are excluded.

sync_records:
  - rec_cabinet_with_drawers_var_bowfront
  - rec_cabinet_with_drawers_var_grid2x2
  - rec_cabinet_with_drawers_var_n2
  - rec_cabinet_with_drawers_var_n4
  - rec_cabinet_with_drawers_var_n6
  - rec_cabinet_with_drawers_var_probe_curved_pairs
  - rec_cabinet_with_drawers_var_tapered
  - rec_cabinet_with_drawers_var_toekick
  - rec_picturex_0611__cabinet_with_drawers__001__png__airflex_batch_20260710_0739738ec7c94c7a8fd90660717f6585
  - rec_picturex_0611__cabinet_with_drawers__002__png__airflex_batch_20260710_7ff0d3b16d3f45a98e6d3f14ce3c21dd
  - rec_picturex_0611__cabinet_with_drawers__003__png__airflex_batch_20260710_26b9fe0822b64bcb80964e503e2567b2
  - rec_picturex_0611__cabinet_with_drawers__004__png__airflex_batch_20260710_9e2d698894684622a88e1b1d3dbcf16d
  - rec_picturex_0611__cabinet_with_drawers__005__png__airflex_batch_20260710_9d0d00f317a34743a1733e46730a4a6d

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_cabinet_with_drawers_var_bowfront/rev_000001 | reviewed | used | Convex front-only host profile is structurally distinct from oval and bombe shells. |
| rec_cabinet_with_drawers_var_grid2x2/rev_000001 | reviewed | reference_only | Count fork confirms paired-grid indexing already contributed by origin 004. |
| rec_cabinet_with_drawers_var_n2/rev_000001 | reviewed | reference_only | Count fork proves N=2 full-width stack and hollow tray construction. |
| rec_cabinet_with_drawers_var_n4/rev_000001 | reviewed | used | Plain handleless front is the least ornamented front candidate and the fork proves N=4. |
| rec_cabinet_with_drawers_var_n6/rev_000001 | reviewed | reference_only | Count fork proves N=6 host capacity for a full-width stack. |
| rec_cabinet_with_drawers_var_probe_curved_pairs/rev_000001 | reviewed | reference_only | Adaptation probe confirms curved host fronts can serve paired drawers without a new candidate. |
| rec_cabinet_with_drawers_var_tapered/rev_000001 | reviewed | used | Tapered side panels provide a canted structural host candidate. |
| rec_cabinet_with_drawers_var_toekick/rev_000001 | reviewed | used | Recessed continuous toe-kick is a distinct load-bearing support candidate. |
| rec_picturex_0611__cabinet_with_drawers__001__png__airflex_batch_20260710_0739738ec7c94c7a8fd90660717f6585/rev_000001 | reviewed | used | Bombe shell, applique front and cabriole apron contribute independent source-backed geometry. |
| rec_picturex_0611__cabinet_with_drawers__002__png__airflex_batch_20260710_7ff0d3b16d3f45a98e6d3f14ce3c21dd/rev_000001 | reviewed | used | Oval shell and fine metal legs are independently recognizable structures. |
| rec_picturex_0611__cabinet_with_drawers__003__png__airflex_batch_20260710_26b9fe0822b64bcb80964e503e2567b2/rev_000001 | reviewed | used | Rectilinear carcass, full-width stack, Gothic front and block-foot plinth are source-backed. |
| rec_picturex_0611__cabinet_with_drawers__004__png__airflex_batch_20260710_9e2d698894684622a88e1b1d3dbcf16d/rev_000001 | reviewed | used | Paired grid, framed cane front and splayed legs are source-backed. |
| rec_picturex_0611__cabinet_with_drawers__005__png__airflex_batch_20260710_9d0d00f317a34743a1733e46730a4a6d/rev_000001 | reviewed | used | Pair-over-full-width layout and tapered-leg apron are source-backed. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| body_form | rect_case | rectilinear panel carcass | rec_picturex_0611__cabinet_with_drawers__003__png__airflex_batch_20260710_26b9fe0822b64bcb80964e503e2567b2/rev_000001 | model.py:L226-L300 | structure | Straight side and back panels frame square drawer openings. |
| body_form | bombe_serpentine | double-curved swelling carcass | rec_picturex_0611__cabinet_with_drawers__001__png__airflex_batch_20260710_0739738ec7c94c7a8fd90660717f6585/rev_000001 | model.py:L26-L61; model.py:L278-L340 | structure | Curved front and sampled front profile produce a bombe host and matching fronts. |
| body_form | oval_rounded | oval-ended carcass | rec_picturex_0611__cabinet_with_drawers__002__png__airflex_batch_20260710_7ff0d3b16d3f45a98e6d3f14ce3c21dd/rev_000001 | model.py:L36-L52; model.py:L127-L149 | structure | Rounded prism and shell define an oval-ended cabinet cavity. |
| body_form | bow_front | convex-front carcass | rec_cabinet_with_drawers_var_bowfront/rev_000001 | model.py:L31-L119 | structure | Bow profile curves the front while preserving straight side panels. |
| body_form | tapered_case | canted carcass | rec_cabinet_with_drawers_var_tapered/rev_000001 | model.py:L30-L58 | structure | Taper derivation and tapered panel mesh lean the case sides. |
| drawer_layout | full_width_stack | one drawer per level | rec_picturex_0611__cabinet_with_drawers__003__png__airflex_batch_20260710_26b9fe0822b64bcb80964e503e2567b2/rev_000001 | model.py:L81-L225 | structure+motion | Each level has a full-width hollow drawer and independent prismatic slide. |
| drawer_layout | paired_grid | two-column drawer grid | rec_picturex_0611__cabinet_with_drawers__004__png__airflex_batch_20260710_9e2d698894684622a88e1b1d3dbcf16d/rev_000001 | model.py:L61-L167 | structure+motion | Central divider and per-cell runner pairs support side-by-side drawers. |
| drawer_layout | pair_over_full_width | paired upper drawers over deep base | rec_picturex_0611__cabinet_with_drawers__005__png__airflex_batch_20260710_9d0d00f317a34743a1733e46730a4a6d/rev_000001 | model.py:L139-L202 | structure+motion | Paired upper levels share a divider above one full-width lower drawer. |
| drawer_front | flat_panel | plain slab front | rec_cabinet_with_drawers_var_n4/rev_000001 | model.py:L52-L90 | structure | Shallow bowed/plain applied front preserves the source handleless panel. |
| drawer_front | framed_cane | framed woven face | rec_picturex_0611__cabinet_with_drawers__004__png__airflex_batch_20260710_9e2d698894684622a88e1b1d3dbcf16d/rev_000001 | model.py:L61-L167 | structure | Frame members surround a recessed woven field and pull. |
| drawer_front | gothic_arch | pointed-arch tracery face | rec_picturex_0611__cabinet_with_drawers__003__png__airflex_batch_20260710_26b9fe0822b64bcb80964e503e2567b2/rev_000001 | model.py:L31-L64 | structure | Sloped and vertical trim segments form pointed Gothic panels. |
| drawer_front | applique_moulded | moulded applique face | rec_picturex_0611__cabinet_with_drawers__001__png__airflex_batch_20260710_0739738ec7c94c7a8fd90660717f6585/rev_000001 | model.py:L91-L152 | structure | Layered central crest and corner scrolls distinguish the front. |
| support_base | cabriole_apron | cabriole legs and apron | rec_picturex_0611__cabinet_with_drawers__001__png__airflex_batch_20260710_0739738ec7c94c7a8fd90660717f6585/rev_000001 | model.py:L278-L340 | structure | Shaped legs continue into a scalloped front apron. |
| support_base | fine_metal_legs | slender turned metal legs | rec_picturex_0611__cabinet_with_drawers__002__png__airflex_batch_20260710_7ff0d3b16d3f45a98e6d3f14ce3c21dd/rev_000001 | model.py:L150-L230 | structure | Four fine cylindrical legs carry the rounded shell. |
| support_base | plinth_block_feet | stepped plinth and block feet | rec_picturex_0611__cabinet_with_drawers__003__png__airflex_batch_20260710_26b9fe0822b64bcb80964e503e2567b2/rev_000001 | model.py:L226-L300 | structure | Moulded base plinth bears on four square feet. |
| support_base | splayed_tapered_legs | splayed tapered legs | rec_picturex_0611__cabinet_with_drawers__004__png__airflex_batch_20260710_9e2d698894684622a88e1b1d3dbcf16d/rev_000001 | model.py:L50-L60 | structure | Tapered leg mesh yields a visibly splayed support. |
| support_base | tapered_legs_apron | tapered legs and scalloped apron | rec_picturex_0611__cabinet_with_drawers__005__png__airflex_batch_20260710_9d0d00f317a34743a1733e46730a4a6d/rev_000001 | model.py:L40-L80 | structure | Tapered legs and shaped apron form one support family. |
| support_base | toe_kick_plinth | recessed toe-kick plinth | rec_cabinet_with_drawers_var_toekick/rev_000001 | model.py:L40-L120 | structure | Continuous recessed plinth replaces discrete legs. |
