# desk_with_drawer_card_catalog — SourceMap

source_map_schema: 1
export_category: desk_with_drawer_card_catalog
picture_category: 0611
picture_subcategory: Desk_with_drawers（no_door）
category_scope: A doorless writing desk with a broad work surface, one structurally supported drawer bank carrying a regular grid of independently guided prismatic card-index drawers; roll-top hoods, keyboard trays, doors, and freestanding dresser cabinets are outside this target. Support families (open-knee side panel, leg-supported apron bank, trestle ends) are structural variants of the same grid-bank host.

sync_records:
  - rec_picturex0611_desk_with_drawers_fork_l_shaped_return_20260714
  - rec_picturex0611_desk_with_drawers_fork_shallow_apron_n2_20260714
  - rec_picturex0611_desk_with_drawers_fork_twin_pedestal_n8_20260714
  - rec_picturex_0611__desk_with_drawers_no_door__001__png__airflex_batch_20260710_0a4495b8d3674ce895b5dcc93b34fa8b
  - rec_picturex_0611__desk_with_drawers_no_door__002__png__airflex_batch_20260710_7613e188f1a643e0ae2025f65a32cc54
  - rec_picturex_0611__desk_with_drawers_no_door__003__png__airflex_batch_20260710_e8f92b30f5d64469bc7be694c4008080
  - rec_picturex_0611__desk_with_drawers_no_door__004__png__airflex_batch_20260710_d23b1cac1d54454d99cc04c6c0bc6fcf
  - rec_picturex_0611__desk_with_drawers_no_door__005__png__airflex_batch_20260710_69a514c4d7e942d49d0a196cbfa9012b
  - rec_0611_table_with_drawers_no_door_var_drawer_layout_full_apron_bank
  - rec_0611_table_with_drawers_no_door_var_support_trestle
  - rec_0611_table_with_drawers_no_door_var_support_splayed_four_leg
  - rec_0611_table_with_drawers_no_door_var_drawer_count_2_wide
  - rec_0611_table_with_drawers_no_door_var_drawer_count_5_narrow
  - rec_0611_manual_coffee_grinder_var_catch_pull_out_drawer

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex0611_desk_with_drawers_fork_l_shaped_return_20260714/rev_000001 | reviewed | reference_only | L-return changes the whole worktop footprint and is outside the rectangular card-catalog desk target; its four-drawer bank repeats origin 003. |
| rec_picturex0611_desk_with_drawers_fork_shallow_apron_n2_20260714/rev_000001 | reviewed | rejected_no_structural_value | Two isolated apron drawers do not provide the dense card-index bank required by this target. |
| rec_picturex0611_desk_with_drawers_fork_twin_pedestal_n8_20260714/rev_000001 | reviewed | rejected_duplicate | Multiplicity fork repeats origin 005 drawer and pedestal construction in a mirrored second bank, while this target uses one grid cabinet base. |
| rec_picturex_0611__desk_with_drawers_no_door__001__png__airflex_batch_20260710_0a4495b8d3674ce895b5dcc93b34fa8b/rev_000001 | reviewed | rejected_category_drift | Roll-top secretary includes a tambour hood and pigeonholes that change the host topology beyond a card-catalog desk. |
| rec_picturex_0611__desk_with_drawers_no_door__002__png__airflex_batch_20260710_7613e188f1a643e0ae2025f65a32cc54/rev_000001 | reviewed | rejected_category_drift | Keyboard tray and mixed side pedestal mechanisms are outside the uniform catalog-drawer identity. |
| rec_picturex_0611__desk_with_drawers_no_door__003__png__airflex_batch_20260710_e8f92b30f5d64469bc7be694c4008080/rev_000001 | reviewed | used | Broad rectangular top, open knee space, supported single drawer bank, paired runners, and hollow guided drawers are directly reusable. |
| rec_picturex_0611__desk_with_drawers_no_door__004__png__airflex_batch_20260710_d23b1cac1d54454d99cc04c6c0bc6fcf/rev_000001 | reviewed | reference_only | Traditional turned-leg writing desk provides only two/four apron drawers and no cabinet-grid host. |
| rec_picturex_0611__desk_with_drawers_no_door__005__png__airflex_batch_20260710_69a514c4d7e942d49d0a196cbfa9012b/rev_000001 | reviewed | used | Open-front pedestal carcass and reusable hollow-drawer helper preserve realistic wall, runner, pull, and slide construction. |
| rec_0611_table_with_drawers_no_door_var_drawer_layout_full_apron_bank/rev_000001 | reviewed | used | Full-width apron bank under the worktop with corner legs supplies the four_leg_apron_bank host family. |
| rec_0611_table_with_drawers_no_door_var_support_trestle/rev_000001 | reviewed | used | End trestles (foot, post, top cleat) joined by a stretcher supply the trestle_open_bay host family. |
| rec_0611_table_with_drawers_no_door_var_support_splayed_four_leg/rev_000001 | reviewed | reference_only | Confirms leg-supported desk hosts for this subcategory; the apron-bank host geometry is taken from the full_apron_bank record instead. |
| rec_0611_table_with_drawers_no_door_var_drawer_count_2_wide/rev_000001 | reviewed | used | Wide drawer construction with an overlay lip front and knob hardware supplies the boxed_full_front drawer family. |
| rec_0611_table_with_drawers_no_door_var_drawer_count_5_narrow/rev_000001 | reviewed | used | Five narrow cells with bay dividers demonstrate the dense-grid capacity contract and finger-slot fronts. |
| rec_0611_manual_coffee_grinder_var_catch_pull_out_drawer/rev_000001 | reviewed | used | Pull-out catch drawer supplies turned knob and recessed pull hardware treatments for small drawers. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| desk_frame | single_bank_open_knee | load-carrying desk frame and open-front drawer-bank host | rec_picturex_0611__desk_with_drawers_no_door__003__png__airflex_batch_20260710_e8f92b30f5d64469bc7be694c4008080/rev_000001 | model.py:L44-L225 | structure | Broad worktop, open knee bay, supported side bank, paired fixed rails, and full-depth carcass walls establish the desk rather than dresser identity. |
| desk_frame | four_leg_apron_bank | leg-supported full-width apron drawer-bank host | rec_0611_table_with_drawers_no_door_var_drawer_layout_full_apron_bank/rev_000001 | model.py:L38-L326 | structure | Corner legs carry a full-width apron bank directly under the worktop, moving the grid to the desk center. |
| desk_frame | trestle_open_bay | trestle-supported centered drawer-bank host | rec_0611_table_with_drawers_no_door_var_support_trestle/rev_000001 | model.py:L27-L157 | structure | Two end trestles with feet, posts, and top cleats joined by a stretcher support a centered bank with open knee bays on both sides. |
| drawer_module | open_tray_guided | hollow moving drawer with paired runner strips and attached pull | rec_picturex_0611__desk_with_drawers_no_door__005__png__airflex_batch_20260710_69a514c4d7e942d49d0a196cbfa9012b/rev_000001 | model.py:L21-L134 | motion | Each drawer is a distinct open-topped tray whose front, side walls, bottom, back, moving rails, and pull share one prismatic motion. |
| drawer_module | boxed_full_front | boxed drawer with overlay lip front | rec_0611_table_with_drawers_no_door_var_drawer_count_2_wide/rev_000001 | model.py:L57-L360 | structure | Drawer fronts extend past the opening and overlap the dividers as a lip, with boxed carcass sides and bottom behind. |
| pull_style | bar_pull | twin-post horizontal bar pull | rec_picturex_0611__desk_with_drawers_no_door__005__png__airflex_batch_20260710_69a514c4d7e942d49d0a196cbfa9012b/rev_000001 | model.py:L21-L134 | decoration | Lower bail pull built from two posts and a cross bar on each drawer front. |
| pull_style | knob_pair | pair of turned knob pulls | rec_0611_manual_coffee_grinder_var_catch_pull_out_drawer/rev_000001 | model.py:L139-L167 | decoration | Turned knob hardware with base disc and stem suits small drawer fronts. |
| pull_style | finger_slot | recessed finger-slot pull | rec_0611_table_with_drawers_no_door_var_drawer_count_5_narrow/rev_000001 | model.py:L93-L139 | decoration | Narrow cell fronts use a dark recessed finger slot instead of applied hardware. |
| pull_style | recessed_oval | recessed oval cup pull | rec_0611_manual_coffee_grinder_var_catch_pull_out_drawer/rev_000001 | model.py:L139-L167 | decoration | Recessed oval cup with dark inset reads as flush card-catalog hardware. |
