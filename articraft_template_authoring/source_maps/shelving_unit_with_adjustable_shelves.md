# Shelving unit with adjustable shelves — SourceMap

export_category: shelving_unit_with_adjustable_shelves

Authoritative records live under `<ARTI_SKILL_ROOT>/articraft_data/data/records`.
This rebuild treats frame topology, shelf support, and lower storage as one coherent
`assembly_family`. The source assets show that these structures are not freely interchangeable.
All accepted families preserve a recognizable multi-bay shelving unit, source-like staggered
open cubbies, one lower storage module per bay, and N independently adjustable shelves. The
source six-bay / six-high-three-low layout is the center point of the grid multiplicities.

sync_records:
  - rec_picturex_0611__shelving_unit_with_adjustable_shelves__001__png_533ba1a88611432880d7a18eb92b3cf3
  - rec_0611_shelving_unit_with_adjustable_var_frame_open_ladder
  - rec_0611_shelving_unit_with_adjustable_var_frame_uniform_grid
  - rec_0611_shelving_unit_with_adjustable_var_frame_wall_rail
  - rec_0611_shelving_unit_with_adjustable_var_adjustment_slotted_standards
  - rec_0611_shelving_unit_with_adjustable_var_adjustment_clip_on_wire
  - rec_0611_shelving_unit_with_adjustable_var_shelf_count_3
  - rec_0611_shelving_unit_with_adjustable_var_shelf_count_5
  - rec_0611_shelving_unit_with_adjustable_var_shelf_count_7
  - rec_0611_shelving_unit_with_adjustable_var_tray_module_lidded_drawer
  - rec_0611_shelving_unit_with_adjustable_var_tray_module_pull_out_basket

## Accepted coherent assembly families

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| assembly_family | stepped_grid_open_bins | stepped grid shelving family | rec_picturex_0611__shelving_unit_with_adjustable_shelves__001__png_533ba1a88611432880d7a18eb92b3cf3/rev_000001 | model.py:L36-L434 | accepted | tall-left/low-right welded grid, seven cubbies, five source shelves, six hollow pull-out bins |
| assembly_family | stepped_grid_lidded_drawers | stepped grid shelving family | rec_0611_shelving_unit_with_adjustable_var_tray_module_lidded_drawer/rev_000001 | model.py:L36-L432 | accepted | source grid with six guided drawers and real separately articulated lids |
| assembly_family | stepped_grid_wire_baskets | stepped grid shelving family | rec_0611_shelving_unit_with_adjustable_var_tray_module_pull_out_basket/rev_000001 | model.py:L36-L508 | accepted | source grid with true rod-network shelves/baskets and pull-out guides |
| assembly_family | open_ladder_solid_shelves | open ladder shelving family | rec_0611_shelving_unit_with_adjustable_var_frame_open_ladder/rev_000001 | model.py:L36-L441 | accepted | paired open ladder uprights, sparse crossmembers, solid single-bay shelves |
| assembly_family | uniform_grid_slotted_shelves | uniform slotted shelving family | rec_0611_shelving_unit_with_adjustable_var_frame_uniform_grid/rev_000001 | model.py:L36-L401 | accepted | full-height regular lattice and repeated indexed shelf support |
| assembly_family | wall_rail_wire_shelves | wall rail shelving family | rec_0611_shelving_unit_with_adjustable_var_frame_wall_rail/rev_000001 | model.py:L36-L460 | accepted | stepped rear wall standards, backplates, cantilever support, wire decks |

## Multiplicity and source-derived placement

- `bay_count = 4 | 5 | 6 | 7 | 8 | 9`, applied to `assembly_family`. It changes the
  number of bays, posts, support spans, storage runners, and lower storage modules.
- `level_count = 4 | 5 | 6 | 7 | 8`, applied to `assembly_family`. It changes the tall
  side's vertical cells and rails; the stepped low side derives `ceil(level_count / 2)` cells.
- `shelf_count = 3 | 5 | 7`, applied to `assembly_family`.
- `bay_count` and `level_count` are structural multiplicities, not continuous scale parameters.
  Their derived frame, cubby, shelf, and storage placement is checked for every declared value.
- N adds exactly N shelf parts, N vertical prismatic adjustment joints, and each shelf's own
  four-point/clip support structure. Cubby count is derived from the free grid cells after shelf
  placement, capped at the source-like seven at the 6x6/3 baseline; storage count equals bay count.
- Placement tables are taken from the source N variants rather than evenly stacking shelves:
  `rec_0611_shelving_unit_with_adjustable_var_shelf_count_3/rev_000001/model.py:L245-L428`,
  `...shelf_count_5/.../model.py:L257-L433`, and
  `...shelf_count_7/.../model.py:L245-L431`.
- Every shelf remains inside one bay and uses only unoccupied source-style bay boundaries.

## Parameters and derivations

- `bay_width_m` (0.34–0.42 m) controls each bay width and derives the full frame width from
  `bay_count`.
- `level_pitch_m` (0.34–0.40 m) controls the vertical grid pitch and derives the tall/low frame
  heights from `level_count`; it is independent of shelf_count.
- `shelf_depth_m` (0.33–0.43 m) derives frame depth, cubby depth, shelf support reach, drawer
  runners, and wire basket depth.
- Insert width derives from bay width with post and operating clearance. Pull-out travel derives
  from shelf depth.

## Category identity and motion

- Exactly one `load_bearing_frame`, a grid-derived number of `open_cubby` parts, one
  `storage_module` per bay, and N `adjustable_shelf` parts are required. At the source baseline
  this is one frame, seven cubbies, six storage modules, and N shelves.
- Every cubby is fixed to the frame. Every shelf uses a short Z-prismatic adjustment. Every storage
  module is parented directly to the fixed frame and slides toward the viewer.
- Lidded drawers add one real X-axis lid hinge per drawer. Wire shelves/baskets use rods, not solid
  dark slabs.
- The stepped, open-ladder, uniform-grid, and wall-rail candidates retain visibly distinct source
  silhouettes and support structures.

## Rejected decompositions

- Independent frame × shelf × tray slots are rejected: they admit structurally incoherent
  combinations and lose the source family's proportions.
- Overall frame height is derived from `level_count`, never from shelf_count.
- Single-column bookcases, generic cabinet blocks, folding shelves, and decorative color-only
  variants are outside this category.
