# pictureX_0611_drum_pedal_with_beater_and_spring_return — SourceMap

source_map_schema: 1
export_category: pictureX_0611_drum_pedal_with_beater_and_spring_return
picture_category: 0611
picture_subcategory: drum_pedal_with_beater_and_spring_return
category_scope: A single bass-drum pedal — one floor frame carrying a hinged footboard, a drive coupling from the board to a rocker shaft/cam, a beater swinging off that shaft, a hoop clamp at the front of the frame, and a return spring with its tension adjuster. Double pedals with a remote slave, hi-hat stands and drum thrones are outside this host.

sync_records:
  - rec_drum_pedal_var_beater_height_carriage_20260714
  - rec_drum_pedal_var_direct_drive_link
  - rec_drum_pedal_var_double_chain_drive
  - rec_drum_pedal_var_eccentric_accelerator_cam_20260714
  - rec_drum_pedal_var_leaf_spring_return_20260714
  - rec_drum_pedal_var_longboard
  - rec_drum_pedal_var_overcenter_hoop_clamp_20260714
  - rec_drum_pedal_var_reversible_beater_head_20260714
  - rec_drum_pedal_var_split_heel_plate
  - rec_drum_pedal_var_strap_drive
  - rec_drum_pedal_var_twin_post_open_rail_frame_20260714
  - rec_picturex_0611__drum_pedal_with_beater_and_spring_return__001__png__airflex_batch_20260710_56292a78640e4f3984db72c4f8918ac9

All records are read at `revisions/rev_000001/model.py`.

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_drum_pedal_var_beater_height_carriage_20260714/rev_000001 | reviewed | used | Inserts a machined height carriage between the drive cam and the beater on a real PRISMATIC joint plus a locking knob, so the beater height is adjustable. Distinct beater assembly. |
| rec_drum_pedal_var_direct_drive_link/rev_000001 | reviewed | used | Replaces the flexible chain with a rigid direct linkage hinged on the footboard by a REVOLUTE joint. Distinct drive coupling. |
| rec_drum_pedal_var_double_chain_drive/rev_000001 | reviewed | used | Two indexed chain rows instead of one, each its own part fixed to the footboard. Distinct drive coupling. |
| rec_drum_pedal_var_eccentric_accelerator_cam_20260714/rev_000001 | reviewed | used | Reshapes the drive cam into an offset accelerator profile with a different radius law. Distinct cam component. |
| rec_drum_pedal_var_leaf_spring_return_20260714/rev_000001 | reviewed | used | Drops the coil spring and its knurled tension adjuster for a cantilever leaf spring bolted to the frame. Distinct return element. |
| rec_drum_pedal_var_longboard/rev_000001 | reviewed | used | A long single-plane board that reaches back over the heel instead of the short hinged plate. Distinct footboard. |
| rec_drum_pedal_var_overcenter_hoop_clamp_20260714/rev_000001 | reviewed | used | Replaces the screw hoop clamp with a three-part over-centre toggle: a cam lever, a toggle link and a pressure shoe. Distinct clamp mechanism. |
| rec_drum_pedal_var_reversible_beater_head_20260714/rev_000001 | reviewed | used | Adds a separate beater head that flips on its own REVOLUTE joint about the shaft axis to swap felt and plastic faces. Distinct beater assembly. |
| rec_drum_pedal_var_split_heel_plate/rev_000001 | reviewed | used | Splits the footboard into an independently hinged heel plate and toe board with two REVOLUTE joints. Distinct footboard. |
| rec_drum_pedal_var_strap_drive/rev_000001 | reviewed | used | A wide nylon strap replaces the chain between the footboard and the cam, and the cam it wraps is a 135-degree pie sector rather than a full disc. Contributes two candidates: a drive coupling and a cam profile. |
| rec_drum_pedal_var_twin_post_open_rail_frame_20260714/rev_000001 | reviewed | used | Rebuilds the frame as twin uprights joined by an open rail instead of the single cast post. Distinct frame. |
| rec_picturex_0611__drum_pedal_with_beater_and_spring_return__001__png__airflex_batch_20260710_56292a78640e4f3984db72c4f8918ac9/rev_000001 | reviewed | used | Origin anchor: cast single-post frame, hinged footboard, single chain, round drive cam, one-piece beater, screw hoop clamp and coil return spring with a knurled tension adjuster. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| frame_style | cast_post | pedal frame | rec_picturex_0611__drum_pedal_with_beater_and_spring_return__001__png__airflex_batch_20260710_56292a78640e4f3984db72c4f8918ac9/rev_000001 | model.py:L112-L248 | structure | One cast side post carries the rocker-shaft bearing, the heel hinge block and the rubber-footed base plate as a single closed body. |
| frame_style | twin_post_rail | pedal frame | rec_drum_pedal_var_twin_post_open_rail_frame_20260714/rev_000001 | model.py:L113-L278 | structure | Two uprights tied by an open cross rail, with the bearing bosses split between them — an open frame rather than one closed casting. |
| board_style | hinged_plate | footboard | rec_picturex_0611__drum_pedal_with_beater_and_spring_return__001__png__airflex_batch_20260710_56292a78640e4f3984db72c4f8918ac9/rev_000001 | model.py:L249-L309 | structure | A short ribbed plate hinged at the heel block, REVOLUTE about -Y with -0.05..0.20 rad travel. |
| board_style | longboard | footboard | rec_drum_pedal_var_longboard/rev_000001 | model.py:L242-L315 | structure | One long flat board that reaches back past the heel hinge, so the whole plate is a single continuous playing surface. |
| board_style | split_heel | footboard | rec_drum_pedal_var_split_heel_plate/rev_000001 | model.py:L301-L417 | structure+motion | The board becomes two parts — `heel_plate` and `toe_board` — each on its own REVOLUTE hinge (L342-L354 and L405-L417) with different effort limits. |
| drive_style | single_chain | drive coupling | rec_picturex_0611__drum_pedal_with_beater_and_spring_return__001__png__airflex_batch_20260710_56292a78640e4f3984db72c4f8918ac9/rev_000001 | model.py:L370-L394 | structure | One chain link strip fixed to the footboard and wrapping the cam. |
| drive_style | double_chain | drive coupling | rec_drum_pedal_var_double_chain_drive/rev_000001 | model.py:L400-L445 | structure | Two indexed `chain_row_i` parts side by side, each separately fixed to the footboard. |
| drive_style | strap | drive coupling | rec_drum_pedal_var_strap_drive/rev_000001 | model.py:L430-L482 | structure | A single wide nylon strap with a clamped end tab replaces the articulated chain links. |
| drive_style | direct_link | drive coupling | rec_drum_pedal_var_direct_drive_link/rev_000001 | model.py:L373-L449 | structure+motion | A rigid forged linkage that is REVOLUTE on the footboard (L437-L449) instead of a fixed flexible member. |
| cam_style | round_cam | drive cam | rec_picturex_0611__drum_pedal_with_beater_and_spring_return__001__png__airflex_batch_20260710_56292a78640e4f3984db72c4f8918ac9/rev_000001 | model.py:L313-L366 | structure | A concentric round cam sprocket on the rocker shaft; constant drive radius. |
| cam_style | eccentric_accel | drive cam | rec_drum_pedal_var_eccentric_accelerator_cam_20260714/rev_000001 | model.py:L347-L419 | structure | An offset accelerator profile whose drive radius grows through the stroke — a different rim law, not a resized round cam. |
| cam_style | d_sector | drive cam | rec_drum_pedal_var_strap_drive/rev_000001 | model.py:L68-L390 | structure | `_round_cam_sector` extrudes a 135-degree pie slice with a central bore plus a `cam_boss_ring` bridging the axle to the sector bore (L378-L387); the other cams are full discs, so the wrapped face is a partial disc rather than a whole rim. |
| beater_style | fixed_head | beater assembly | rec_picturex_0611__drum_pedal_with_beater_and_spring_return__001__png__airflex_batch_20260710_56292a78640e4f3984db72c4f8918ac9/rev_000001 | model.py:L398-L444 | structure | One-piece shaft plus felt head clamped straight onto the cam hub. |
| beater_style | reversible_head | beater assembly | rec_drum_pedal_var_reversible_beater_head_20260714/rev_000001 | model.py:L443-L508 | structure+motion | A separate `beater_head` on its own REVOLUTE joint about the shaft axis (L492-L508) so the felt and plastic faces can be swapped. |
| beater_style | height_carriage | beater assembly | rec_drum_pedal_var_beater_height_carriage_20260714/rev_000001 | model.py:L426-L555 | structure+motion | A machined carriage rides the cam hub on a PRISMATIC joint (L450-L462) with its own locking knob, and the beater hangs off the carriage instead of the hub. |
| clamp_style | screw_clamp | hoop clamp | rec_picturex_0611__drum_pedal_with_beater_and_spring_return__001__png__airflex_batch_20260710_56292a78640e4f3984db72c4f8918ac9/rev_000001 | model.py:L447-L510 | structure | A clamp lever hinged on the frame plus a knurled hoop adjuster screw turning on the lever. |
| clamp_style | overcenter_toggle | hoop clamp | rec_drum_pedal_var_overcenter_hoop_clamp_20260714/rev_000001 | model.py:L452-L619 | structure+motion | Three parts — `cam_lever`, `toggle_link` and `pressure_shoe` — on three chained REVOLUTE joints forming an over-centre latch. |
| spring_style | coil_return | return spring | rec_picturex_0611__drum_pedal_with_beater_and_spring_return__001__png__airflex_batch_20260710_56292a78640e4f3984db72c4f8918ac9/rev_000001 | model.py:L512-L608 | structure | A coil spring hung on the frame post with a separate knurled tension adjuster turning about the vertical axis. |
| spring_style | leaf_return | return spring | rec_drum_pedal_var_leaf_spring_return_20260714/rev_000001 | model.py:L601-L663 | structure | A cantilever leaf stack bolted to the frame with no coil and no rotating tension nut at all. |

## Coverage note

Every record in the active `0611 / drum_pedal_with_beater_and_spring_return` workbench pool is
reviewed and every one of the twelve contributes at least one candidate. The whole pool shares one
host — frame, footboard, rocker shaft/cam, beater, hoop clamp, return spring — so each fork is read
as a replacement for one of those components. `rec_drum_pedal_var_strap_drive` is the one fork that
changes two of them: the strap coupling and the 135-degree sector cam it wraps, so it appears in
both `drive_style` and `cam_style`.

`core_domain = 2 (frame_style) x 3 (board_style) x 4 (drive_style) x 3 (cam_style)
x 3 (beater_style) x 2 (clamp_style) x 2 (spring_style) = 864`; `raw_domain = 864`, because every
source builds one footboard, one cam and one beater, so there is no honest multiplicity.
