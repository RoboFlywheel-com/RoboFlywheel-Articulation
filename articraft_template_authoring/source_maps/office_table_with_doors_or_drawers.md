# Office table with doors or drawers — SourceMap

export_category: office_table_with_doors_or_drawers

Authoritative records live under `data/records`. The category is an office / executive
table: a raised worktop at roughly 0.75 m carried by a grounded storage carcass that hosts
at least one real non-fixed joint — prismatic drawer trays and/or a closure leaf over a
storage bay — plus the closure and secondary-motion mechanisms introduced by the fork
variants.

Frame convention for the rebuild: `+X` runs along the desk width (right), `+Y` points
rearward (away from the user), `+Z` is up. The user side is therefore `-Y`: drawers pull
along `(0,-1,0)`, hinged closure leaves swing forward about a vertical axis, drop-fronts
hinge about a horizontal `X` line at the bottom of their opening, and the rear cable hatch
swings rearward. Record 001/002 used front `-Y`; record 003 used front `-X` with drawers on
`(1,0,0)`. That is a coordinate choice, not a structural difference, and the rebuild
standardizes on front `-Y`.

sync_records:
  - rec_picturex_0611__office_table_with_doors_or_drawers__001__png_57bac13add2c40b7addfb86887d0da4c
  - rec_picturex_0611__office_table_with_doors_or_drawers__002__png_a048366dd19d4c2cb5c7499522bfee15
  - rec_picturex_0611__office_table_with_doors_or_drawers__003__png_b4b10d9eca3648049dbe8a4bf3ea11e6
  - rec_0611_office_table_with_doors_or_dra_var_worktop_form_straight
  - rec_0611_office_table_with_doors_or_dra_var_worktop_form_compact_corner
  - rec_0611_office_table_with_doors_or_dra_var_worktop_form_u_return
  - rec_0611_office_table_with_doors_or_dra_var_storage_topology_drawer_pedestal
  - rec_0611_office_table_with_doors_or_dra_var_storage_topology_paired_door_pedestal
  - rec_0611_office_table_with_doors_or_dra_var_storage_topology_open_equipment_bay
  - rec_0611_office_table_with_doors_or_dra_var_closure_sliding_door
  - rec_0611_office_table_with_doors_or_dra_var_closure_drop_front
  - rec_0611_office_table_with_doors_or_dra_var_closure_tambour
  - rec_0611_office_table_with_doors_or_dra_var_secondary_motion_keyboard_tray
  - rec_0611_office_table_with_doors_or_dra_var_secondary_motion_cable_access_door
  - rec_0611_office_table_with_doors_or_dra_var_drawer_count_3
  - rec_0611_office_table_with_doors_or_dra_var_drawer_count_5

## Component slots and candidates

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Diversity axis | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| worktop_form | straight | raised work surface | rec_0611_office_table_with_doors_or_dra_var_worktop_form_straight/rev_000001 | model.py:L45-L100, model.py:L356-L386 | accepted | ① plan footprint / support span | One rectangular full-thickness slab with square corners, a straight-edge laminate field bounded by four perimeter reveal strips and one front edge band. No return wing, so the top is carried only by the two grounded storage volumes; no return-end support panel is derived |
| worktop_form | compact_corner | raised work surface | rec_0611_office_table_with_doors_or_dra_var_worktop_form_compact_corner/rev_000001 | model.py:L51-L74, model.py:L168-L180 | accepted | ① plan footprint / support span | A single L-shaped polyline slab: a wide main wing plus one shorter rear wing meeting at a 90° inner corner, vertical edges filleted. One cantilevered rear wing forces one derived return underlayer plus one grounded return-end support panel |
| worktop_form | u_return | raised work surface | rec_0611_office_table_with_doors_or_dra_var_worktop_form_u_return/rev_000001 | model.py:L30-L56, model.py:L180-L207 | accepted | ① plan footprint / support span | Main slab unioned with two symmetric rear wings and two cable pass-through cuts; the host answers with two return underlayers and two grounded return-end panels (`return_underlayer_0/1`, `return_end_panel_0/1`) |
| storage_topology | drawer_and_door_credenza | grounded storage carcass | rec_picturex_0611__office_table_with_doors_or_drawers__001__png_57bac13add2c40b7addfb86887d0da4c/rev_000001 | model.py:L51-L96, model.py:L124-L153, model.py:L184-L209 | accepted | ② carcass part tree / bay layout | One continuous full-width credenza: bottom deck, two outer side panels, one internal partition, top deck, back panel, recessed illuminated fascia reveal, and a low brushed-metal sled plinth with four feet. No knee bay; the wide drawer bay and the closure bay share one carcass and one partition |
| storage_topology | drawer_pedestal | grounded storage carcass | rec_0611_office_table_with_doors_or_dra_var_storage_topology_drawer_pedestal/rev_000001 | model.py:L105-L205, model.py:L246-L306 | accepted | ② carcass part tree / bay layout | Two separate grounded pedestals with an open knee bay between them: plinth, floor, inner wall, back, cap and a rounded outer end cheek per pedestal, plus per-level drawer guide rails, a vent-slit stack on the outer face, and the closure hinge leaves carried by the pedestal rather than the top |
| storage_topology | paired_door_pedestal | grounded storage carcass | rec_0611_office_table_with_doors_or_dra_var_storage_topology_paired_door_pedestal/rev_000001 | model.py:L145-L161, model.py:L196-L242 | accepted | ② carcass part tree / bay layout | The closure pedestal is widened and split into two independent half-width openings; two hinge-leaf pairs sit at the two opposite hinge edges (`hinge_edge_specs`), giving two closure leaves with mirrored vertical hinge axes and one extra revolute joint |
| storage_topology | open_equipment_bay | grounded storage carcass | rec_0611_office_table_with_doors_or_dra_var_storage_topology_open_equipment_bay/rev_000001 | model.py:L135-L184, model.py:L186-L246 | accepted | ② carcass part tree / bay layout | The tall pedestal volume becomes an open equipment cubby: two fixed open shelves, a real rear cable grommet bore for a tower/peripheral, and the vented outer face; the closure bay shrinks to the lower part of the same pedestal, so opening height must re-derive |
| closure | hinged_door | storage bay closure | rec_picturex_0611__office_table_with_doors_or_drawers__002__png_a048366dd19d4c2cb5c7499522bfee15/rev_000001 | model.py:L219-L230, model.py:L276-L324 | accepted | ③ joint type / axis / mechanism | Carcass-fixed hinge knuckles plus a leaf carrying two hinge barrels and two straps; revolute joint on a vertical hinge line, axis `(0,0,±1)`, 0 → ~1.72 rad, swinging outward toward the user. Same mechanism in 003 model.py:L142-L149 and L186-L221 |
| closure | sliding_bypass_doors | storage bay closure | rec_0611_office_table_with_doors_or_dra_var_closure_sliding_door/rev_000001 | model.py:L211-L235, model.py:L279-L316, model.py:L318-L353 | accepted | ③ joint type / axis / mechanism | Carcass-fixed top and bottom slide tracks plus two bypass tracks offset in Y; the hinges are gone and each leaf becomes a prismatic panel with a recessed grip, sliding along `(±1,0,0)`; two leaves per opening ride separate grooves so one passes behind the other |
| closure | drop_front | storage bay closure | rec_0611_office_table_with_doors_or_dra_var_closure_drop_front/rev_000001 | model.py:L194-L213, model.py:L249-L328, model.py:L341-L367 | accepted | ③ joint type / axis / mechanism | The hinge line moves to the bottom of the opening: a horizontal `X` hinge barrel with a full-width hinge leaf, rest bumpers relocated to the top of the opening, and revolute joints on axis `(±1,0,0)` from 0 to 1.50 rad, dropping the panel forward and down |
| closure | tambour | storage bay closure | rec_0611_office_table_with_doors_or_dra_var_closure_tambour/rev_000001 | model.py:L20-L37, model.py:L232-L241, model.py:L287-L347 | accepted | ③ joint type / axis / mechanism | A real guided rolling shutter: a vertical track channel cut into the pedestal side panel, two vertical metal track rails at the opening edges, a garage housing (back, fascia, floor) above the opening, and a slat curtain (ten slats + one flexible backing strip + bottom pull rail + grip) on a vertical prismatic joint `(0,0,1)` |
| drawer_style | runner_tray | prismatic drawer tray | rec_picturex_0611__office_table_with_doors_or_drawers__002__png_a048366dd19d4c2cb5c7499522bfee15/rev_000001 | model.py:L60-L139, model.py:L206-L217 | accepted | ② moving-member part tree | Hollow tray (flat front + floor + two sides + back) with two drawer-mounted metal runner members (`moving_rail_0/1`) matched to per-level carcass-mounted runner halves (`fixed_rail_{row}_{side}`), plus a small inset rectangular pull; prismatic pull on `(0,-1,0)` |
| drawer_style | rounded_pull_bar_tray | prismatic drawer tray | rec_0611_office_table_with_doors_or_dra_var_drawer_count_5/rev_000001 | model.py:L119-L140, model.py:L269-L307 | accepted | ② moving-member part tree | Wide front panel whose vertical edges are filleted by `_rounded_panel`, over a hollow tray built as one connected floor + two sides + back solid (`_drawer_box_shape`), finished with a full-width aluminium pull bar spanning the front. Same construction in 001 model.py:L211-L243 |
| drawer_style | flush_grip_tray | prismatic drawer tray | rec_picturex_0611__office_table_with_doors_or_drawers__003__png_b4b10d9eca3648049dbe8a4bf3ea11e6/rev_000001 | model.py:L151-L164, model.py:L225-L282 | accepted | ② moving-member part tree | Flat handleless front with a compact vertical finger grip; hollow tray (front + bottom + two sides + back) carried by paired carcass-side guide rails (`outer_drawer_rail_*` / `inner_drawer_rail_*`) rather than drawer-mounted runner members |
| secondary_motion | none | secondary desk mechanism | rec_picturex_0611__office_table_with_doors_or_drawers__002__png_a048366dd19d4c2cb5c7499522bfee15/rev_000001 | model.py:L163-L241 | accepted | ② part tree / joint count | The baseline carcass has no secondary mechanism: the knee bay carries only a fixed knee shelf with two dividers and a modesty panel, and the only non-fixed joints are the drawers and the closure leaf |
| secondary_motion | keyboard_tray | secondary desk mechanism | rec_0611_office_table_with_doors_or_dra_var_secondary_motion_keyboard_tray/rev_000001 | model.py:L99-L126, model.py:L214-L282 | accepted | ② part tree / joint count | Adds one part and one joint: two carcass-mounted slide rail tracks under the top panel plus a pull-out tray (platform, three raised lips, front pull, front lip, two slide engagement tabs riding inside the rails) on a prismatic joint `(0,-1,0)`, 0 → 0.250 m |
| secondary_motion | cable_access_hatch | secondary desk mechanism | rec_0611_office_table_with_doors_or_dra_var_secondary_motion_cable_access_door/rev_000001 | model.py:L51-L69, model.py:L265-L345, model.py:L355-L381 | accepted | ② part tree / joint count | Contributes the compact slotted access panel: a filleted panel with a real horizontal cable pass-through cut (`_cable_access_panel`, `panel.cut(slot)`), a small hinge barrel plus leaf, and a deliberately short revolute travel of 1.05 rad at reduced effort |

## Shared (non-slotted) category anchors

These appear in every accepted record and are rebuilt as fixed geometry on the single root
`desk_carcass` part, not as slot candidates:

- Raised full-thickness worktop slab at ~0.72–0.78 m with a front edge band and at least one
  cable pass-through: 001 model.py:L140-L182; 002 model.py:L30-L48 & L232-L239;
  003 model.py:L42-L79.
- A continuous under-slab layer / top rail tying the storage volumes into one supported
  carcass while keeping the knee bay open: 002 model.py:L173-L174 & L189-L197.
- Grounded plinth / recessed feet under every storage volume: 001 model.py:L83-L96;
  002 model.py:L190-L194 & L239-L241; 003 model.py:L110-L113.
- Modesty panel and rear closure of the knee space: 002 model.py:L199-L203;
  003 model.py:L90-L99.
- Fixed interior shelves inside the closure bay, visible when the leaf is opened:
  002 model.py:L219-L220; 003 model.py:L133-L140.
- Per-level drawer guide rails carried by the carcass: 002 model.py:L206-L217;
  003 model.py:L151-L164.
- Vent-slit stack on the exposed pedestal face and a rear cable grommet:
  003 model.py:L166-L182; open_equipment_bay model.py:L144-L151.

## Multiplicity and where the observed N values come from

- `drawer_count = 1 | 2 | 3 | 4 | 5`, `item_slot = drawer_style`. N is the number of
  independently articulated drawer trays in the drawer bay; it is a count, so it counts
  toward `raw_domain` only.
- Source-observed values: N=1 in record 001 (one broad drawer, model.py:L211-L243 with the
  joint at L325-L333); N=3 in record 002 (model.py:L207-L285), record 003
  (model.py:L225-L282) and `..._var_drawer_count_3` (model.py:L60-L68 & L217-L265); N=5 in
  `..._var_drawer_count_5` (model.py:L23-L36, L229-L248, L269-L307). N=2 and N=4 bracket the
  observed set without extrapolating beyond it.
- Spacing: `..._var_drawer_count_5` model.py:L27-L29 is the authoritative pitch rule — a fixed
  bay height is divided by N with a constant inter-front gap, giving
  `front_height = (bay_height - (N-1) * gap) / N` and `step = front_height + gap`. The
  rebuild reuses that rule, caps the front height so low N reads as a real drawer rather
  than a full-height slab, and fills any remainder with a fixed open cubby shelf.
- Host capacity: `floor((drawer_bay_height + gap) / (min_front_height + gap))` with a
  minimum front height of 0.070 m; the declared maximum of 5 stays inside capacity for the
  smallest legal worktop height.
- N also re-derives the per-level carcass structures: N-1 bay dividers
  (`..._var_drawer_count_5` model.py:L229-L237), N soft-close bumpers (L239-L248) and 2N
  carcass runner channels (002 model.py:L206-L217).

## Parameters and derivations

- `worktop_height_m` (0.72–0.78) sets the work-surface height. Slab, under-slab layer,
  pedestal cap, bay top, drawer stack height, closure opening height, tambour split and
  keyboard-tray mounting plane all derive from it.
- `main_span_m` (1.66–1.95) and `main_depth_m` (0.62–0.78) set the worktop plan. Carcass
  front/rear planes, pedestal centres, knee span, credenza partition position and drawer box
  depth derive from them.
- `pedestal_width_m` (0.34–0.44) sets the storage volume width, therefore the drawer
  opening, the drawer box width, the runner gauge and the closure opening width. The paired
  topology widens the closure volume by a fixed factor and splits it with a real mullion.
- `return_depth_m` (0.48–0.66) sets the rear wing depth for `compact_corner` and `u_return`;
  the return underlayer footprint and the grounded return-end panel position derive from it.
- `closure_panel_thickness_m` (0.018–0.026) sets the leaf thickness; the hinge axis offset,
  the hinge barrel radius, the sliding groove pitch and the fascia/curtain clearance all
  re-derive from it.
- `drawer_wall_m` (0.014–0.020) sets the tray wall thickness; the interior volume, the back
  panel width and the runner attachment face derive from it.
- `tray_depth_m` (0.26–0.34) and `hatch_width_m` (0.22–0.32) are local to the two positive
  secondary-motion candidates and drive the rail length / travel and the real back-panel
  opening respectively.
- Cross-component derivations: the closure opening `(width, height)` comes from the selected
  topology and is consumed by every closure candidate; the drawer cavity
  `(opening width, interior depth, level pitch)` comes from the topology and N and is
  consumed by every drawer style; the worktop footprint drives the number of grounded
  return-end panels; the secondary mechanism reserves a tray zone that shortens the drawer
  bay when there is no knee bay to hang the tray in.

## Category identity and motion

- Exactly one fixed root part `desk_carcass` (role `desk_carcass`) carries the worktop,
  the grounded storage volumes and every guide.
- N parts with role `storage_drawer`, each a hollow tray (front + floor + two sides + back),
  each on its own prismatic joint from the carcass with axis `(0,-1,0)`, `lower=0` (closed)
  and `upper=` full extension. The slide interface lives on the real left and right runners:
  a C-channel per side per level on the carcass and a matching runner member on the tray.
- 1, 2 or 4 parts with role `closure_leaf` depending on topology (one or two openings) and
  closure candidate (one leaf, or a bypass pair per opening). Revolute leaves
  (`hinged_door`, `drop_front`) are built from `AxisInterface`/`mate_axes` and registered
  with `register_interface_mate` on the real hinge line — vertical at the opening's outer
  edge, or horizontal along `X` at the bottom of the opening. Prismatic leaves
  (`sliding_bypass_doors`, `tambour`) are solved with `PlaneInterface`/`mate_planes` against
  the real track footprint and run in real grooves with clearance.
- 0 or 1 secondary part: `keyboard_tray` (prismatic, `(0,-1,0)`) or `cable_access_hatch`
  (revolute about a vertical axis, registered axis mate, swinging rearward through a real
  opening in the back panel).
- No `allow_overlap` anywhere: every guide is a real C-channel or groove with derived
  clearance, every hinge is a real barrel/knuckle pair interleaved along the axis, and every
  opening is a real hole in the host.

## Rejected decompositions

- `worktop_form=straight` is *not* rejected even though the literal delta in
  `..._var_worktop_form_straight` is confined to the worktop laminate field and its four
  perimeter reveals (model.py:L57-L88). The row is accepted because the record establishes
  the straight, square-cornered, return-less top form; the rebuild expresses it as a plain
  rectangular slab with no cantilevered wing and therefore no derived return-end support,
  which is a genuine footprint and support-span difference from the other two candidates.
- Treating the `..._var_storage_topology_drawer_pedestal` refactor as *only* a part-tree
  refactor is rejected. In that record the pedestal becomes its own sub-assembly with its own
  plinth, panels, shelves, per-level rails, vent stack and hinge leaves
  (model.py:L105-L205), which is the two-separate-pedestals-plus-knee-bay architecture; the
  rebuild keeps that as a distinct carcass family from the one-piece credenza of record 001.
- `..._var_secondary_motion_cable_access_door` implemented its axis by *replacing* the three
  main closure panels with small slotted ones (model.py:L265-L345). Carrying that over
  literally would collapse `secondary_motion` into `closure` and make the two slots
  non-independent, which the full-combination rule forbids. The rebuild instead keeps the
  record's characteristic contribution — the filleted panel with a real horizontal cable
  pass-through cut, the small barrel/leaf hinge and the deliberately short 1.05 rad travel —
  and mounts it as a dedicated access hatch over a real opening in the closure volume's back
  panel, so it composes with all four closure candidates.
- Making `closure` and `storage_topology` mutually exclusive (for example excluding
  `open_equipment_bay` from having any closure) is rejected: `TemplateDomain` has no gates.
  `open_equipment_bay` keeps the open cubby with its shelves and rear grommet in the upper
  part of the volume and derives a shorter closure opening below it, and `tambour` further
  halves whatever opening it is given into a curtain zone plus an equal garage pocket.
- Modelling the source tambour travel literally is rejected: `..._var_closure_tambour`
  model.py:L333-L347 slides a rigid 0.545 m curtain 0.460 m upward, which drives it straight
  through the pedestal cap and the worktop. The rebuild splits the closure bay into an
  opening and an equal-height garage pocket behind a fixed fascia so the full travel is real
  and collision-free.
- Making the worktop cable module, task-light reveal, edge bands, vent slits, grain inlays
  and pull finishes into slots is rejected: they are surface features shared across records
  and do not change the part tree, a joint or the topology.
