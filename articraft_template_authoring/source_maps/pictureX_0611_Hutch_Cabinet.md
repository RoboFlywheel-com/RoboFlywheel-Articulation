# pictureX 0611 Hutch_Cabinet — SourceMap

export_category: pictureX_0611_Hutch_Cabinet

Authoritative records live under `<ARTI_SKILL_ROOT>/arti-template/data/records`.
Category identity: a two-tier dresser/hutch — a deeper lower base cabinet carrying a shallower
upper case under a crown, with storage in BOTH tiers. A single-tier cabinet or a bare open
shelf unit is out of scope.

sync_records:
  - rec_picturex_0611__hutch_cabinet__001__png_06992399ece7490a91f934345df0f0ba
  - rec_picturex0611_hutch_cabinet_fork_upper_glass_hinged_doors_20260713
  - rec_picturex0611_hutch_cabinet_fork_open_upper_shelves_20260713
  - rec_picturex0611_hutch_cabinet_fork_sliding_glass_upper_doors_20260714
  - rec_picturex0611_hutch_cabinet_fork_tambour_roll_front_20260713
  - rec_picturex0611_hutch_cabinet_fork_drop_front_secretary_20260713
  - rec_picturex0611_hutch_cabinet_fork_lift_up_flap_upper_20260714
  - rec_picturex0611_hutch_cabinet_fork_plate_rack_back_20260714
  - rec_picturex0611_hutch_cabinet_fork_lower_double_door_base_20260713
  - rec_picturex0611_hutch_cabinet_fork_lower_drawer_bank_20260713
  - rec_picturex0611_hutch_cabinet_fork_wine_cubby_lower_grid_20260714

## Accepted candidates

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| upper_front | glass_hinged_doors | hinged glazed upper doors | rec_picturex0611_hutch_cabinet_fork_upper_glass_hinged_doors_20260713/rev_000001 | model.py:L172-L246 | accepted | `_add_upper_door_details` glazed leaves with muntins on vertical hinges |
| upper_front | open_shelves | open upper shelf bay | rec_picturex0611_hutch_cabinet_fork_open_upper_shelves_20260713/rev_000001 | model.py:L116-L257 | accepted | the upper case carries real fixed shelves and no leaf |
| upper_front | sliding_glass_doors | bypass glazed uppers | rec_picturex0611_hutch_cabinet_fork_sliding_glass_upper_doors_20260714/rev_000001 | model.py:L120-L280 | accepted | glazed leaves on offset upper tracks with prismatic travel |
| upper_front | tambour_roll | roll-up slat front | rec_picturex0611_hutch_cabinet_fork_tambour_roll_front_20260713/rev_000001 | model.py:L95-L155 | accepted | `_add_tambour_details` builds a real slatted curtain |
| upper_front | drop_front_desk | fall-front writing flap | rec_picturex0611_hutch_cabinet_fork_drop_front_secretary_20260713/rev_000001 | model.py:L169-L234 | accepted | a bottom-pivoted flap drops forward into a writing surface |
| upper_front | lift_up_flap | top-hinged lift-up flap | rec_picturex0611_hutch_cabinet_fork_lift_up_flap_upper_20260714/rev_000001 | model.py:L120-L260 | accepted | the upper front is one top-hinged flap lifting up and out |
| lower_front | double_doors | hinged lower doors | rec_picturex0611_hutch_cabinet_fork_lower_double_door_base_20260713/rev_000001 | model.py:L55-L94 | accepted | `_add_lower_door_details` panelled leaves on the base cabinet |
| lower_front | drawer_bank | lower drawer bank | rec_picturex0611_hutch_cabinet_fork_lower_drawer_bank_20260713/rev_000001 | model.py:L214-L234 | accepted | `_add_drawer_details` hollow trays stacked in the base |
| lower_front | wine_cubby_grid | lattice bottle cubby | rec_picturex0611_hutch_cabinet_fork_wine_cubby_lower_grid_20260714/rev_000001 | model.py:L120-L260 | accepted-derived | the fork's cubby grid is kept as real cradle ribs, but each column is made a pull-out bottle cradle so the lower tier is articulated in every combination |
| crown_form | moulded_cornice | stepped moulded crown | rec_picturex_0611__hutch_cabinet__001__png_06992399ece7490a91f934345df0f0ba/rev_000001 | model.py:L24-L50 | accepted | `_crown_profile` steps the cornice out over the upper case |
| crown_form | arched_pediment | arched broken pediment | rec_picturex_0611__hutch_cabinet__001__png_06992399ece7490a91f934345df0f0ba/rev_000001 | model.py:L51-L124 | accepted-derived | `_door_top_values`/`_arched_panel` supply the arch profile used as a pediment |
| back_treatment | plain_back | plain boarded back | rec_picturex0611_hutch_cabinet_fork_open_upper_shelves_20260713/rev_000001 | model.py:L116-L200 | accepted | plain back board behind the upper bay |
| back_treatment | plate_rack | grooved plate rack back | rec_picturex0611_hutch_cabinet_fork_plate_rack_back_20260714/rev_000001 | model.py:L120-L260 | accepted | real plate-rack rails and spindles across the upper back |

## Rejected

- single-tier cabinets and bare shelf units: excluded by the subcategory contract.
- pull styles and timber colour: derived detail, not independent slots.

## Multiplicity

- `lower_unit_count = 1 | 2 | 3 | 4`, applied to `lower_front`.
  It is the number of independently articulated lower units — leaves for `double_doors`,
  trays for `drawer_bank`, cubby columns for `wine_cubby_grid`.
  N=2 origin 001 (paired lower doors, model.py:L235-L400);
  N=3 `rec_picturex0611_hutch_cabinet_fork_lower_drawer_bank_20260713/rev_000001`
  model.py:L235-L420; N=1 and N=4 use the same loop with the base opening resized.
  Base opening width, unit pitch, leaf/tray width and travel derive from N.
- `upper_shelf_count = 1 | 2 | 3`, applied to `back_treatment`, sets the fixed shelf ladder
  inside the upper case (open_upper_shelves fork, model.py:L116-L257).

## Parameters and derivations

- `carcass_width_m`, `base_depth_m`, `base_height_m`, `upper_height_m` are candidate-local to
  `crown_form`; the upper case derives a shallower depth from the base depth.
- The upper front mechanism derives its opening from the upper case and the lower front derives
  its opening from the base cabinet, so the two tiers never share geometry.

## Category identity and motion

- Exactly one `carcass` part carrying both tiers, the deck between them, the crown and the back.
- At least one moving `lower_unit` part in every combination; the upper front adds moving
  `upper_unit` parts except for the open-shelf candidate, which instead carries real fixed shelves.
- Hinged leaves rotate about a registered vertical axis; drop and lift flaps about a horizontal
  axis; tambour and bypass leaves translate.
