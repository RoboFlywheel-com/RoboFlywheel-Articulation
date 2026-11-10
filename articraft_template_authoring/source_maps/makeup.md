# Makeup — SourceMap

export_category: makeup

The source pool is two origin assets and fifteen directed forks. Both origins are the same
category: a **case-body chassis, a rear-hinged mirrored lid, and N independently articulated
palette / tray parts that visibly leave the case body**. Origin 1
(`rec_picturex_0611__makeup__001__png_…`) is a shallow black all-in-one case whose two palettes
swing out on real corner posts (`base_to_palette_{i}`, revolute about Z). Origin 2
(`rec_use-the-attached-reference-image-as-the-primary-_20260710_093913_953497_b3fcb0ac`) is a
tall children's travel vanity whose three trays slide out of real moulded tunnels
(`case_to_front_organizer`, `case_to_side_tray_{0,1}`, prismatic). The `1 + N` articulated
palette axis is what separates this template from its `makeup1/2/3` siblings, whose pans are
static on a single base.

The forks map onto five component slots plus one multiplicity. Nothing in this map is a
"complete asset" candidate: every row is a component of the shared chassis/lid/palette skeleton.

sync_records:
  - rec_picturex_0611__makeup__001__png_25a74d42e2cc47b8be52d1f0dd9e0807
  - rec_use-the-attached-reference-image-as-the-primary-_20260710_093913_953497_b3fcb0ac
  - rec_0611_makeup_var_applicator_storage_lid_brush_roll
  - rec_0611_makeup_var_case_form_book_style_folio
  - rec_0611_makeup_var_case_form_cylindrical_vanity_case
  - rec_0611_makeup_var_case_form_round_compact
  - rec_0611_makeup_var_case_form_train_case_tower
  - rec_0611_makeup_var_closure_over_center_clasp
  - rec_0611_makeup_var_opening_motion_telescoping_side_trays
  - rec_0611_makeup_var_palette_count_3_palette_trays
  - rec_0611_makeup_var_palette_count_5_palette_trays
  - rec_0611_makeup_var_palette_count_7_palette_trays
  - rec_0611_makeup_var_palette_topology_accordion_tier_carrie
  - rec_0611_makeup_var_palette_topology_fan_out_wing_carrier
  - rec_0611_makeup_var_palette_topology_flip_over_double_sided_leaf
  - rec_0611_makeup_var_palette_topology_pull_out_drawer_carri
  - rec_0611_makeup_var_pan_module_interface_snap_in_tile_grid

## Accepted component candidates

| Slot | Candidate | Diversity axis | Component type | Record/Revision | Exact model.py:Lx-Ly | Status | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| case_form | rounded_train_case | ③ primary form | case chassis shell | rec_picturex_0611__makeup__001__png_25a74d42e2cc47b8be52d1f0dd9e0807/rev_000001 | model.py:L30-L44; model.py:L158-L199 | accepted source-backed | `_rounded_case_shell` outer box with filleted vertical edges minus an inset cavity; `case_base`, `case_shell`, `organizer_insert`, `base_hinge_barrel_{i}`, `front_latch`. |
| case_form | round_compact | ③ primary form | case chassis shell | rec_0611_makeup_var_case_form_round_compact/rev_000001 | model.py:L30-L36; model.py:L137-L178 | accepted source-backed | Circular extruded shell minus a coaxial cavity; the lid becomes a disc + rim (`_lid_frame` L39-L60) and the hinge knuckles move inboard to `x=±0.083`. |
| case_form | train_case_tower | ③ primary form | case chassis shell | rec_0611_makeup_var_case_form_train_case_tower/rev_000001 | model.py:L31-L89; model.py:L240-L275 | accepted source-backed | `TOWER_DROP=0.082` deep body, two wraparound reinforcement rails (`rail_outer.cut(rail_inner)`) and a proud foot ring; lid gains raised edge rails (L124-L138). |
| case_form | book_style_folio | ③ primary form | case chassis shell | rec_0611_makeup_var_case_form_book_style_folio/rev_000001 | model.py:L30-L67; model.py:L171-L212 | accepted source-backed | Oversized rounded cover board (`CASE_W+0.012`), thin filleted shell and a bound rear spine bolster; lid becomes cover board + rim + lower binding (L70-L86). |
| case_form | cylindrical_vanity_case | ③ primary form | case chassis shell | rec_0611_makeup_var_case_form_cylindrical_vanity_case/rev_000001 | model.py:L37-L50; model.py:L220-L300; model.py:L356-L393 | accepted source-backed | `_cylindrical_disc` drum body with real slide tunnels cut through the curved wall, an arc-conformal `front_pale_band`, and a round lid disc hinged on the rear tangent line. |
| palette_topology | pull_out_drawer | ② joint/mechanism | articulated palette tray | rec_0611_makeup_var_palette_topology_pull_out_drawer_carri/rev_000001 | model.py:L38-L81; model.py:L443-L475; model.py:L531-L567; model.py:L597-L624 | accepted source-backed | `_hollow_tray` (outer minus inner, reinforced rim) + twin carrier rails and an inner crossbar (`front_slide_tail`, `side_slide_tail`) riding real runners; prismatic along the true pull direction. |
| palette_topology | telescoping_side_tray | ② joint/mechanism | articulated palette tray | rec_0611_makeup_var_opening_motion_telescoping_side_trays/rev_000001 | model.py:L436-L515; model.py:L544-L572 | accepted source-backed | Two-stage shell: a shallow stepped outer carriage unioned with a taller narrower inner tray, plus `telescoping_stage_collar`; travel grows from 0.105 to 0.130. |
| palette_topology | fan_out_wing | ② joint/mechanism | articulated palette tray | rec_0611_makeup_var_palette_topology_fan_out_wing_carrier/rev_000001 | model.py:L38-L87; model.py:L470-L540; model.py:L573-L596 | accepted source-backed | `_hollow_tray(..., fan_pivot=...)` grows a real pivot boss + bridge at the tray's corner; `wing_pivot_cap`, `wing_carrier_arm`; revolute about Z at the rear side corner. Also origin 1 `base_to_palette_{i}` (model.py:L348-L365). |
| palette_topology | flip_over_leaf | ② joint/mechanism | articulated palette tray | rec_0611_makeup_var_palette_topology_flip_over_double_sided_leaf/rev_000001 | model.py:L214-L231; model.py:L366-L407; model.py:L589-L601 | accepted source-backed | `flip_palette_leaf` slab with `palette_axle` and pans on both faces (`upper_face_pan_*`, `reverse_face_pan_*`) captured by two `palette_pivot_socket_*` knuckle tubes; revolute 0 → 3.02 rad. |
| palette_topology | accordion_tier | ② joint/mechanism | articulated palette tray | rec_0611_makeup_var_palette_topology_accordion_tier_carrie/rev_000001 | model.py:L78-L135; model.py:L343-L384 | accepted source-backed | `_palette_frame(direction, tier_index)` raises each tray by `tier_z = 0.010 + tier_index*0.016` on a broad diagonal cantilever carrier rising from the captured corner hub, with an `inner_edge=0.024` gap. |
| applicator_storage | front_organizer_channels | ① part tree | applicator retention | rec_use-the-attached-reference-image-as-the-primary-_20260710_093913_953497_b3fcb0ac/rev_000001 | model.py:L86-L123; model.py:L393-L419 | accepted source-backed | `_pocketed_plate` with `slot_pockets` cut as real brush channels plus `brush_channel_{i}` shadow strips inside them. |
| applicator_storage | lid_brush_roll | ① part tree | applicator retention | rec_0611_makeup_var_applicator_storage_lid_brush_roll/rev_000001 | model.py:L86-L103; model.py:L391-L429; model.py:L455-L478 | accepted source-backed | `lid_brush_roll_panel` fitted to the lid's inner apron with six `_tube_y` retaining sleeves and `brush_handle_{i}` rods; the front organiser degrades to a plain `front_accessory_pocket`. |
| applicator_storage | upright_tool_well | ① part tree | applicator retention | rec_picturex_0611__makeup__001__png_25a74d42e2cc47b8be52d1f0dd9e0807/rev_000001 | model.py:L240-L262 | accepted source-backed | Three narrow upright channels retaining `tool_handle_{i}` pencils plus `central_tube` and `tube_cap` standing in the organiser. |
| pan_module_interface | fixed_round_wells | ① part tree | pan seating interface | rec_use-the-attached-reference-image-as-the-primary-_20260710_093913_953497_b3fcb0ac/rev_000001 | model.py:L86-L123; model.py:L213-L236 | accepted source-backed | `central_palette_insert` plate with `circle_pockets` recesses and `central_pan_{i}` cylinders seated in them. |
| pan_module_interface | keyed_snap_tile_grid | ① part tree | pan seating interface | rec_0611_makeup_var_pan_module_interface_snap_in_tile_grid/rev_000001 | model.py:L126-L190; model.py:L266-L384 | accepted source-backed | `snap_tile_grid_insert` = base + perimeter rim + X/Y dividers; `_keyed_tile_seat` adds a locating key and finger notch per cell; `_keyed_snap_tile` refills have an asymmetric keyed corner. |
| closure | front_latch_strike | ① part tree | lid closure | rec_picturex_0611__makeup__001__png_25a74d42e2cc47b8be52d1f0dd9e0807/rev_000001 | model.py:L194-L199; model.py:L282-L287 | accepted source-backed | Fixed gold `front_latch` strike on the case front plus the mating `lid_clasp` tab on the lid; no extra joint. Also origin 2 `gold_clasp`/`clasp_jewel`/`lid_clasp_catch` (model.py:L264-L276, L366-L371). |
| closure | over_center_clasp | ② joint/mechanism | lid closure | rec_0611_makeup_var_closure_over_center_clasp/rev_000001 | model.py:L78-L96; model.py:L303-L351 | accepted source-backed | `_clasp_mount` U-shaped keeper with two ears on the lid rail plus a separate `lid_clasp` part (`clasp_pin`, `clasp_lever`, `clasp_grip`) on its own revolute `lid_to_clasp` joint. |

## Shared (non-slotted) category anchors

Every combination keeps the same three-role skeleton, so these are not slots:

- `case_body` — one rooted chassis with a real hollow deck recess, real per-station cavities or
  wall pockets, real hinge hardware and real palette bearing hardware. Sources:
  origin 1 model.py:L158-L199, origin 2 model.py:L152-L289.
- `mirror_lid` — one rear-hinged lid carrying an inset mirror and a mirror opening frame,
  rotating about the case-wide hinge line. Sources: origin 1 model.py:L264-L298,
  origin 2 model.py:L291-L371 and L498-L511.
- `palette_tray` — N independently articulated palette parts, each with its own joint.
  Sources: origin 1 model.py:L324-L365, origin 2 model.py:L373-L496 and L512-L553.

## Multiplicity

- `palette_count` is the number of independently articulated palette parts and is bound to the
  `palette_topology` component slot.
- Observed source values: **2** (origin 1, `palette_0`/`palette_1`, model.py:L324-L365),
  **3** (origin 2 and `rec_0611_makeup_var_palette_count_3_palette_trays`, model.py:L21-L22 and
  L487-L599), **5** (`rec_0611_makeup_var_palette_count_5_palette_trays`, model.py:L22,
  L443-L556: alternating sides with `stack_level = side_index // 2` and a 0.008 vertical pitch),
  **7** (`rec_0611_makeup_var_palette_count_7_palette_trays`, model.py:L21, L440-L570:
  `side_tray_layer_pitch = 0.0045` stacked layers with alternating pull directions).
- The template therefore samples `palette_count ∈ {2, 3, 4, 5, 6, 7}`; 4 and 6 interpolate inside
  the observed 2–7 bracket. N counts toward `raw_domain`, never toward `core_domain`.
- Station allocation follows the sources: sides cycle left / right / front (origin 2's exact
  three-station layout at N=3) and each station owns its own vertical level, the way the 5- and
  7-tray forks stack same-side trays. Host capacity is a derived requirement, not a gate:
  `body_height >= floor + palette_count * level_pitch + deck_slab + recess_depth`.

## Parameters and derivations

Independent (all metres unless noted):

- `case_width_m` 0.265–0.405 and `case_depth_m` 0.155–0.235 keep the wide-shallow source plan
  (origin 1 0.300×0.210, origin 2 0.340×0.230, round fork 0.300×0.300, drum fork ⌀0.350).
  They drive every plan profile, rim, recess, cavity span and lid plan.
- `case_height_m` 0.055–0.150 brackets origin 1 (0.045 + 0.006 floor) through origin 2 (0.145)
  and the tower fork (0.045+0.082). It only raises the body above the N-derived requirement, so
  the plinth is derived, never negative.
- `lid_depth_m` 0.010–0.055 is the lid box wall height, from origin 2's flat 0.022 lid shell to
  the tower fork's railed lid; it changes the closed silhouette and the mirror well depth.
- `tray_height_m` 0.011–0.026 brackets the observed tray walls (0.0035 in the 7-tray fork,
  0.008 in the 5-tray fork, 0.026–0.036 in origin 2).
- `tray_extension_ratio` 0.45–0.82 (ratio) reproduces the observed travel/tray-length ratios
  (origin 2: 0.105 travel on a 0.200 tray; telescoping fork: 0.130).
- `corner_radius_m` 0.005–0.028 spans origin 1's 0.008 shell fillet, origin 2's 0.025 and the
  tower fork's 0.012/0.015 rails.
- `pan_pitch_m` 0.030–0.052 spans origin 1's 0.0315 shadow-pan pitch, origin 2's 0.042 central
  pitch and the tile-grid fork's `cell_pitch_x = 0.062` / `cell_pitch_y = 0.042`.

Key derived values: `level_pitch`, `bay_height`, `required_body_height`, `plinth_height`,
`deck_z`, `recess_depth`, `hinge_axis_z`, `lid_plan_*`, per-station `cavity_depth`,
`tray_travel`, `tail_length`, `wing_arm_length`, `leaf_length`, `pan_cols`, `pan_rows`. The
recess depth is raised by `upright_tool_well` (standing tools must clear the closed lid) and the
lid box depth is raised by `lid_brush_roll` (the sleeves live inside the lid box), which is host
adaptation, not a gate.

## Category identity and motion

- Joint chain: `case_body -> mirror_lid` (revolute about the case-wide X hinge line, lower =
  closed onto the case rim, upper ≈ 1.62 rad upright) and `case_body -> palette_tray_i` for every
  station. Palette joints are prismatic along the true pull direction for
  `pull_out_drawer` / `telescoping_side_tray`, revolute about the vertical post axis for
  `fan_out_wing` / `accordion_tier`, and revolute about the tangential knuckle line for
  `flip_over_leaf`. `over_center_clasp` adds `mirror_lid -> lid_clasp`.
- Every rotational joint is solved with `mate_axes` and registered with
  `register_interface_mate`; every prismatic tray is seated with `mate_planes` on the real runner
  footprint.
- All palette motion is confined below the case rim plane in Z or outside the case plan, so the
  closed lid never has to share space with a deployed tray.

## Rejected decompositions

- `opening_motion`, `case_form` and `palette_topology` as three independent mechanism slots on the
  same tray: the telescoping fork changes the same tray shell and joint travel that
  `palette_topology` owns, so it is folded into `palette_topology` as
  `telescoping_side_tray` rather than a second mechanism slot that would double-specify one part.
- Complete origin assets as candidates of one family slot: rejected, both origins decompose into
  the same chassis/lid/palette roles.
- Solid palette blocks, palettes resting on a solid host with no cavity, and hinge pins with no
  knuckle: rejected. Every mechanism has real bearing hardware and real running clearance.
- `ctx.allow_overlap(...)`: rejected for this template. Origin 2 used it for the captured hinge
  pin (model.py:L628-L641); the rebuild models a real interference-fit knuckle instead.
- Colour / powder-palette-only forks: not candidates at all.
