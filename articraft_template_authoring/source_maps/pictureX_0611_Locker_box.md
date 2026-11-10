# Locker box — SourceMap

export_category: pictureX_0611_Locker_box
registry_key: pictureX_0611_Locker_box

Authoritative records live under `data/records`. A locker box is a lockable storage box:
a hollow sheet-acrylic carcass (side walls + floor + top + back + horizontal shelves) whose
front opening is closed by hinged doors, each side-hinged on a vertical edge and carrying
visible lock hardware. This rebuild models the repeated locker cell as a vertical stack of
N compartments, each with its own real side-hinged door, and captures five independent
structural axes that are all directly observable across the three records: the door leaf
construction, the lock mechanism, the hinge hardware, the carcass front frame, and the
interior subdivision. Every declared combination builds; nothing is gated out.

sync_records:
  - rec_picturex_0611__locker_box__001__png_530198ce33344903b0ba8c8e5a959124
  - rec_use-the-attached-reference-image-as-the-primary-_20260712_092616_643603_0832e6dc
  - rec_use-the-attached-reference-image-as-the-primary-_20260712_095210_303286_0832e6dc

## Records — what each models

| Record | Rev | Mechanism summary |
|---|---|---|
| rec_picturex_0611__locker_box__001__png_530198ce33344903b0ba8c8e5a959124 | rev_000001 | One wide acrylic carcass with 4 plain horizontal shelves and NO vertical dividers (`L86-L100`); ONE full-front door side-hinged about world Z on three discrete butt-hinge stations whose carcass knuckles/leaves interleave in Z with the door knuckles/leaves (`L102-L125`, `L150-L164`); a grid of rotary **key** locks (each a REVOLUTE-Y knob seated on a collar) plus a pivoting **latch lever** (REVOLUTE-Y) and a fixed carcass latch keeper (`L127-L135`, `L166-L279`); flush acrylic shelf-rail edge strips only, no fasteners (`L95-L100`). |
| rec_use-the-attached-reference-image-as-the-primary-_20260712_092616_643603_0832e6dc | rev_000001 | 20 individually side-hinged (Z) compartment doors; each door is a **framed** acrylic leaf (panel + 4 perimeter edge strips + 2 hinge knuckles, `L186-L215`), with **static** cam latch + molded padlock + brass shackle + number label (`L217-L274`); carcass has shelves AND vertical dividers (`L131-L155`) and raised metal front **mullions** with screw fasteners (`L157-L177`). |
| rec_use-the-attached-reference-image-as-the-primary-_20260712_095210_303286_0832e6dc | rev_000001 | Single articulated side-hinged (Z) **flat** door leaf (panel + full-height hinge leaf + full-height barrel + screws, `L209-L226`) against a carcass-side full-height hinge mount block + long pin (`L200-L208`); **static** cam latch + padlock + U-shackle (`L87-L109`); carcass has shelves AND vertical dividers (`L166-L178`) and flush polished corner/edge rails (`L171-L188`). |

## Accepted candidates

| Slot | Candidate | Diversity axis | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| door_leaf | flat_leaf | ① part-tree | plain hinged acrylic panel | rec_use-the-attached-reference-image-as-the-primary-_20260712_095210_303286_0832e6dc/rev_000001 | model.py:L209-L226 | accepted | flat single-thickness leaf `moving_door_panel` + number plate + 2 assembly screw cylinders; no perimeter frame |
| door_leaf | framed_leaf | ① part-tree | perimeter-framed acrylic panel | rec_use-the-attached-reference-image-as-the-primary-_20260712_092616_643603_0832e6dc/rev_000001 | model.py:L186-L215 | accepted | `door_panel` + raised `top_edge`/`bottom_edge`/`hinge_edge`/`latch_edge` perimeter stiles (4 extra boxes) forming a real frame |
| lock | rotary_key | ① joint-graph | rotary key knob + pivot latch lever | rec_picturex_0611__locker_box__001__png_530198ce33344903b0ba8c8e5a959124/rev_000001 | model.py:L166-L279 | accepted | `lock_plate`/`lock_collar` on the door, child `key_knob` part (shaft+hub+bow) on REVOLUTE-Y `door_to_key`, `latch_pivot` + child `door_latch` part on REVOLUTE-Y `door_to_latch`, plus a fixed carcass `latch_keeper` (L127-L135); +2 joints per door |
| lock | cam_padlock | ① part-tree | static cam latch + molded padlock | rec_use-the-attached-reference-image-as-the-primary-_20260712_092616_643603_0832e6dc/rev_000001 | model.py:L217-L264 | accepted | static `cam_hub`/`cam_handle`/`lock_eye` + `padlock_body` + 2 `shackle_leg` + `shackle_bridge`, all on the door part; zero extra joints; cf. 095210 `_add_lock_hardware` L87-L109 |
| hinge | knuckle_pair | ① part-tree | discrete butt hinges | rec_picturex_0611__locker_box__001__png_530198ce33344903b0ba8c8e5a959124/rev_000001 | model.py:L102-L125 | accepted | two discrete stations, each carcass `hinge_leaf`+`hinge_knuckle_{lower,upper}` interleaved in Z with the door `door_knuckle`/`door_hinge_leaf` (door side L150-L164); 4 carcass knuckles + 2 door knuckles per door |
| hinge | piano_barrel | ① part-tree | continuous full-height hinge | rec_use-the-attached-reference-image-as-the-primary-_20260712_095210_303286_0832e6dc/rev_000001 | model.py:L200-L215 | accepted | carcass `door_hinge_mount` block + `door_hinge_pin` stubs against a single full-height door `moving_hinge_leaf` + `moving_hinge_barrel`; 2 carcass stubs + 1 long door barrel per door |
| carcass_front | mullion_frame | ① part-tree | metal front rails + fasteners | rec_use-the-attached-reference-image-as-the-primary-_20260712_092616_643603_0832e6dc/rev_000001 | model.py:L157-L177 | accepted | raised metal vertical `front_rail_*` posts + per-compartment cross rails + `rail_screw_*` fastener cylinders |
| carcass_front | edge_strip | ① part-tree | polished acrylic edge strips | rec_picturex_0611__locker_box__001__png_530198ce33344903b0ba8c8e5a959124/rev_000001 | model.py:L95-L100 | accepted | flush thin acrylic `shelf_rail_*` edge strips only, no fasteners; cf. 095210 `shelf_edge_*`/`divider_edge_*` L171-L178 |
| interior | open_shelf | ① part-tree | plain horizontal shelves | rec_picturex_0611__locker_box__001__png_530198ce33344903b0ba8c8e5a959124/rev_000001 | model.py:L86-L100 | accepted | `shelf_{i}` full-width horizontal panels only; the compartment behind each door is one open volume |
| interior | grid_cubby | ① part-tree | shelves + vertical dividers | rec_use-the-attached-reference-image-as-the-primary-_20260712_092616_643603_0832e6dc/rev_000001 | model.py:L131-L155 | accepted | `shelf_{row}` plus `divider_{col}` vertical panels splitting every compartment into cubbies; cf. 095210 `horizontal_divider_*`/`vertical_divider_*` L166-L178 |

Rejected / folded decompositions:

- Single full-front door topology (001, one leaf over a 20-cell grid) is NOT a separate
  `door_leaf` candidate: 1-door vs N-doors is a whole-host topology change, so per
  AUTHORING §4 it is folded into the multiplicity `compartment_count` instead. 001's
  distinctive mechanisms (rotary key + pivot latch + keeper) are kept as the `rotary_key`
  lock candidate applied per door.
- Top-hinged lid / hinge SIDE is not a candidate: all three records side-hinge on a
  vertical edge, so no top-hinged lid is invented.
- Feet / plinth / skids are not a candidate: all three records sit on a plain bottom
  panel (001 `L59-L64`, 092616 `L100-L105`, 095210 `L155-L156`) with no base structure.
- Palette, numerals, screw counts and label plates are decorative — not core/raw diversity.

## Multiplicity N — `compartment_count` (item_slot = door_leaf)

- Observed: all three records lay out a dense grid of locker cells (5 rows x 4 cols = 20)
  with one door/lock station per cell (092616 = 20 real hinged doors, `model.py:L181-L302`).
  The repeated unit is the side-hinged locker compartment.
- Derived: this template stacks N compartments vertically (single column), each a real
  side-hinged door, keeping 1-D multiplicity with source-safe motion (stacked doors swing
  about parallel vertical axes at different heights and never meet).
- Range `compartment_count = 2 | 3 | 4 | 5`. Pitch = `cell_height_m`; carcass height =
  `compartment_count * cell_height_m`; one horizontal shelf separates each adjacent pair
  (`N - 1` shelves), mirroring the source shelves (001 `L86-L100`, 092616 `L131-L146`).
- Validation: preflight builds min/max N per `door_leaf` candidate and confirms N door
  parts, N hinge joints, N-1 shelves and (for `rotary_key`) N key + N latch children.

## Independent parameters (continuous, not core/raw diversity)

- `width_m` (0.28–0.44; source 001 CABINET_W 0.440, 092616 WIDTH 0.48, 095210 WIDTH 0.440):
  carcass + opening width; door width, shelf span, front-rail span all derive from it.
- `depth_m` (0.14–0.24; source 001 CABINET_D 0.160, 092616 DEPTH 0.32, 095210 DEPTH 0.180):
  carcass depth; the door front plane derives as `depth/2 + front_gap + door_t/2`.
- `cell_height_m` (0.09–0.15; source CELL_H = HEIGHT/ROWS = 0.064–0.080, enlarged to a
  single-column pitch): compartment pitch; carcass height, hinge station Z, shelf Z, door
  height, lock station Z and hinge barrel length all derive from it.

Wall thickness, door plane offset, hinge inset, knuckle engagement, collar/pivot placement
and shelf spans are derived from the above so parts stay coaxial and seated after changes.

## Door + latch mechanism entities, supports, axes, ranges, envelopes

- Door hinge: `AxisInterface` on the carcass front-left of each cell at
  `(-W/2 - hinge_offset, D/2 + front_gap + door_t/2, z_cell)`, axis `(0,0,1)`; consumer at
  the door-local origin (the leaf origin lies ON the hinge line); REVOLUTE lower 0.0,
  upper 1.55 rad. Measured sign: +theta about +Z carries the leaf (which extends toward +X)
  toward +Y, i.e. outward, matching 092616 `carcass_to_door_*` axis `(0,0,1)` lower 0 upper
  1.75 (`L288-L302`). The whole door plane sits `front_gap` ahead of the carcass face and
  the minimum swept Y over the entire range is the closed-pose back face, so the leaf never
  re-enters the carcass.
- Hinge capture: the carcass knuckles and the door knuckle/barrel are COAXIAL on the hinge
  line and engage axially by 0.5 mm. Because the pair is coaxial, that engagement is
  rotation-invariant, so the door stays connected (and under the 1 mm overlap tolerance) at
  every pose. No `allow_overlap` anywhere.
- Rotary key: `AxisInterface` on the door front, axis `(0,1,0)`, key child centred on the
  axis; REVOLUTE +-0.55 (001 `L223-L236`). Latch lever: axis `(0,1,0)` at the free edge;
  REVOLUTE +-0.65 (001 `L266-L279`). The key shaft / latch shaft butt their collar / pivot
  front face with a 0.5 mm axial engagement (contact, not bulk overlap).
- `cam_padlock`: no joints; all hardware lives on the door part, so the captured
  shackle-in-body fit of the source is intra-part and free.
