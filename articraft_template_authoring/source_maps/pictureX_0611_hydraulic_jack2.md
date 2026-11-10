# pictureX_0611_hydraulic_jack2 — SourceMap

source_map_schema: 1
export_category: pictureX_0611_hydraulic_jack2
picture_category: 0611
picture_subcategory: hydraulic_jack2
category_scope: A wheeled hydraulic floor (trolley) jack — a long low chassis running on front rollers and rear casters, a single lift arm pivoted at the rear that swings up to carry a load head at the front, a hydraulic ram in the chassis driving that arm, and a long pump handle at the rear. Standing bottle/ram jacks and scissor lifts are different hosts and belong to pictureX_0611_hydraulic_jack1 and pictureX_0611_hydraulic_jack.

sync_records:
  - rec_picturex0611_hydraulic_jack2_fork_air_over_hydraulic_20260714
  - rec_picturex0611_hydraulic_jack2_fork_bottle_jack_20260713
  - rec_picturex0611_hydraulic_jack2_fork_double_stage_ram_20260713
  - rec_picturex0611_hydraulic_jack2_fork_floor_trolley_jack_20260713
  - rec_picturex0611_hydraulic_jack2_fork_low_profile_floor_20260714
  - rec_picturex0611_hydraulic_jack2_fork_motorcycle_platform_20260714
  - rec_picturex0611_hydraulic_jack2_fork_safety_lock_bar_20260714
  - rec_picturex0611_hydraulic_jack2_fork_screw_extension_saddle_20260713
  - rec_picturex0611_hydraulic_jack2_fork_toe_jack_20260713
  - rec_picturex0611_hydraulic_jack2_fork_transmission_cradle_20260713
  - rec_picturex_0611__hydraulic_jack2__001__png_1e3d36c9f6f846b59e6a82e93b80e5e0

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__hydraulic_jack2__001__png_1e3d36c9f6f846b59e6a82e93b80e5e0/rev_000001 | reviewed | used | Image-grounded base for 001.png, the blue floor jack: chassis, ram cylinder and piston, rear-pivoted lift arm, disc saddle, long pump handle with its link, two rigid front rollers and two swivel rear casters. Supplies the host mechanism plus disc_saddle, plate_frame, lever_handle and BOTH wheel-station candidates — the source genuinely builds two different stations, a rigid roller on a stub axle and a swivel caster. |
| rec_picturex0611_hydraulic_jack2_fork_low_profile_floor_20260714/rev_000001 | reviewed | used | Same host on a long shallow low-entry chassis that reaches under a low sill. Source for the low_profile chassis style. |
| rec_picturex0611_hydraulic_jack2_fork_bottle_jack_20260713/rev_000001 | reviewed | used | Puts the ram on a short welded box chassis with closed side boxes. Taken for the boxed_frame chassis style only; its arm-less direct-ram lift is not taken because it removes the lift arm. |
| rec_picturex0611_hydraulic_jack2_fork_screw_extension_saddle_20260713/rev_000001 | reviewed | used | Adds a threaded screw post and load pad above the saddle to extend reach. Source for the screw_post load head. |
| rec_picturex0611_hydraulic_jack2_fork_transmission_cradle_20260713/rev_000001 | reviewed | used | Replaces the disc saddle with a vee cradle for a gearbox. Source for the vee_cradle load head. |
| rec_picturex0611_hydraulic_jack2_fork_motorcycle_platform_20260714/rev_000001 | reviewed | used | Replaces the saddle with a wide ribbed platform spanning the chassis. Source for the wide_platform load head. |
| rec_picturex0611_hydraulic_jack2_fork_air_over_hydraulic_20260714/rev_000001 | reviewed | used | Adds an air-assist module with a regulator knob and hose beside the hand pump. Source for the air_over_hydraulic pump drive. |
| rec_picturex0611_hydraulic_jack2_fork_safety_lock_bar_20260714/rev_000001 | reviewed | reference_only | Adds a lock bar and pawl. Not taken as a slot because the pawl only engages at one specific lift-arm angle, which would couple a safety slot to the arm angle through a shared tooth grid. |
| rec_picturex0611_hydraulic_jack2_fork_double_stage_ram_20260713/rev_000001 | reviewed | reference_only | Splits the ram into two nested stages. The rebuild drives the ram as a mimic of the lift arm rather than as an independent joint, so a second stage adds no separable component here; staged rams are carried by pictureX_0611_hydraulic_jack1. |
| rec_picturex0611_hydraulic_jack2_fork_toe_jack_20260713/rev_000001 | reviewed | reference_only | Adds a low toe lip in front of the saddle. Structurally the same "wider, lower load face" idea already taken as wide_platform, so it would be a duplicate candidate. |
| rec_picturex0611_hydraulic_jack2_fork_floor_trolley_jack_20260713/rev_000001 | reviewed | rejected_duplicate | Reproduces the base record's floor-jack host with no new component; it is the same chassis, arm, saddle and wheel set already taken from 001. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| saddle_head | disc_saddle | lift-arm load head | rec_picturex_0611__hydraulic_jack2__001__png_1e3d36c9f6f846b59e6a82e93b80e5e0/rev_000001 | model.py:L225-L245 | structure | Knurled disc saddle with a hardened contact face on the arm nose. |
| saddle_head | screw_post | lift-arm load head | rec_picturex0611_hydraulic_jack2_fork_screw_extension_saddle_20260713/rev_000001 | model.py:L246-L340 | structure | Threaded screw post and collar carrying a load pad well above the arm nose. |
| saddle_head | vee_cradle | lift-arm load head | rec_picturex0611_hydraulic_jack2_fork_transmission_cradle_20260713/rev_000001 | model.py:L227-L292 | structure | Vee cradle whose inclined cheeks meet at the groove root, with raised end lips. |
| saddle_head | wide_platform | lift-arm load head | rec_picturex0611_hydraulic_jack2_fork_motorcycle_platform_20260714/rev_000001 | model.py:L237-L283 | structure | Wide ribbed platform spanning most of the chassis width with turned-down edges. |
| chassis_style | plate_frame | chassis section | rec_picturex_0611__hydraulic_jack2__001__png_1e3d36c9f6f846b59e6a82e93b80e5e0/rev_000001 | model.py:L67-L146 | structure | Twin pressed side plates with a rolled top edge and open sides. |
| chassis_style | low_profile | chassis section | rec_picturex0611_hydraulic_jack2_fork_low_profile_floor_20260714/rev_000001 | model.py:L67-L153 | structure | Long shallow low-entry chassis with a tapered nose reaching under a low sill. |
| chassis_style | boxed_frame | chassis section | rec_picturex0611_hydraulic_jack2_fork_bottle_jack_20260713/rev_000001 | model.py:L52-L107 | structure | Short welded box chassis with closed side boxes and a deep cross deck. |
| pump_drive | lever_handle | pump input | rec_picturex_0611__hydraulic_jack2__001__png_1e3d36c9f6f846b59e6a82e93b80e5e0/rev_000001 | model.py:L246-L290 | structure | Long two-piece hand lever with a rubber grip swinging on the rear socket. |
| pump_drive | air_over_hydraulic | pump input | rec_picturex0611_hydraulic_jack2_fork_air_over_hydraulic_20260714/rev_000001 | model.py:L321-L408 | structure | Air-assist can with a regulator knob and hose on the chassis, driven by a short trigger lever. |
| wheel_station | swivel_caster | rear wheel station | rec_picturex_0611__hydraulic_jack2__001__png_1e3d36c9f6f846b59e6a82e93b80e5e0/rev_000001 | model.py:L339-L393 | structure+motion | Swivel fork on a vertical REVOLUTE kingpin carrying a wheel that spins on its own CONTINUOUS axle. |
| wheel_station | fixed_roller | rear wheel station | rec_picturex_0611__hydraulic_jack2__001__png_1e3d36c9f6f846b59e6a82e93b80e5e0/rev_000001 | model.py:L314-L338 | structure+motion | Rigid roller on a stub axle bracket with a single CONTINUOUS spin axis and no kingpin. |
