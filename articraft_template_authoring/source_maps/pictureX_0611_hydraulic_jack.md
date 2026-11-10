# pictureX_0611_hydraulic_jack — SourceMap

source_map_schema: 1
export_category: pictureX_0611_hydraulic_jack
picture_category: 0611
picture_subcategory: hydraulic_jack
category_scope: A scissor lift jack — a rigid base frame, a crossed scissor linkage, and a load platform that rises parallel to the base, actuated from the base. 001.png is a blue slotted-plate lab scissor jack and 002.png is an orange hydraulic scissor lift table on casters; both are this host. Single-lift-arm floor/trolley jacks have no scissor linkage and belong to pictureX_0611_hydraulic_jack2.

sync_records:
  - rec_picturex0611_hydraulic_jack_fork_air_over_hydraulic_20260714
  - rec_picturex0611_hydraulic_jack_fork_bottle_jack_20260713
  - rec_picturex0611_hydraulic_jack_fork_double_stage_ram_20260713
  - rec_picturex0611_hydraulic_jack_fork_floor_trolley_jack_20260713
  - rec_picturex0611_hydraulic_jack_fork_low_profile_floor_20260714
  - rec_picturex0611_hydraulic_jack_fork_safety_lock_bar_20260714
  - rec_picturex0611_hydraulic_jack_fork_screw_extension_saddle_20260713
  - rec_picturex0611_hydraulic_jack_fork_toe_jack_20260713
  - rec_picturex0611_hydraulic_jack_fork_transmission_cradle_20260714
  - rec_picturex_0611__hydraulic_jack__001__png_af55d19fd79043eeaaa91f76169ade14
  - rec_picturex_0611__hydraulic_jack__002__png_53523a539a204bcf896a11590eedafae

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__hydraulic_jack__001__png_af55d19fd79043eeaaa91f76169ade14/rev_000001 | reviewed | used | Image-grounded base for 001.png: slotted blue side plates on base and platform, four scissor links on REVOLUTE pivots with sliding guide shoes, hydraulic cylinder and pump handle. Supplies the host scissor mechanism plus slotted_side_plate, flat_deck, hydraulic_pump and foot_pad. |
| rec_picturex_0611__hydraulic_jack__002__png_53523a539a204bcf896a11590eedafae/rev_000001 | reviewed | used | Image-grounded orange scissor lift table for 002.png: the same scissor host, built as TWO stacked X stages with plain boxed bar links. Supplies the boxed_bar_arm link form and the evidence that the stage count is the category's real multiplicity. Its swivel casters/caster locks are a base trim of that particular trolley body and are not taken as a slot. |
| rec_picturex0611_hydraulic_jack_fork_bottle_jack_20260713/rev_000001 | reviewed | used | Puts the same lift on a plain welded box-channel base frame instead of slotted side plates. Taken for the boxed_channel frame style only; its single-cylinder direct lift is not taken because it removes the scissor. |
| rec_picturex0611_hydraulic_jack_fork_toe_jack_20260713/rev_000001 | reviewed | used | Base frame extended into a channel section carrying a low toe rail under the load edge. Source for the toe_channel frame style. |
| rec_picturex0611_hydraulic_jack_fork_screw_extension_saddle_20260713/rev_000001 | reviewed | used | Adds a threaded riser and saddle pad above the lift platform on its own REVOLUTE joint. Source for the screw_riser deck fitting. |
| rec_picturex0611_hydraulic_jack_fork_transmission_cradle_20260714/rev_000001 | reviewed | used | Replaces the flat deck with a vee cradle saddle on the platform. Source for the vee_cradle deck fitting. |
| rec_picturex0611_hydraulic_jack_fork_air_over_hydraulic_20260714/rev_000001 | reviewed | used | Adds an air-assist module with a pneumatic piston and an air valve lever beside the hand pump. Source for the air_over_hydraulic drive unit. |
| rec_picturex0611_hydraulic_jack_fork_double_stage_ram_20260713/rev_000001 | reviewed | reference_only | Splits the actuator into two nested ram stages. The rebuild does not articulate the actuator rod independently (it is only meaningful simultaneously with the scissor angle), so this yields no separable component; the staged-ram idea is already carried by pictureX_0611_hydraulic_jack1. |
| rec_picturex0611_hydraulic_jack_fork_safety_lock_bar_20260714/rev_000001 | reviewed | reference_only | Adds a prop bar that drops into a notch. Not taken as a slot because its pawl only engages at one specific scissor angle, which would couple the safety slot to the lift angle through a shared notch grid. |
| rec_picturex0611_hydraulic_jack_fork_floor_trolley_jack_20260713/rev_000001 | reviewed | rejected_category_drift | Deletes the scissor linkage and lifts with a single horizontal arm on a wheeled chassis. That is a whole-host topology change and is the pictureX_0611_hydraulic_jack2 host. |
| rec_picturex0611_hydraulic_jack_fork_low_profile_floor_20260714/rev_000001 | reviewed | rejected_category_drift | Same single-lift-arm trolley host as the floor trolley fork, in a low-profile body; outside this category scope. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| frame_style | slotted_side_plate | base frame section | rec_picturex_0611__hydraulic_jack__001__png_af55d19fd79043eeaaa91f76169ade14/rev_000001 | model.py:L38-L59 | structure | Pressed side plates carrying long lightening slots, as on the blue lab jack in 001.png. |
| frame_style | boxed_channel | base frame section | rec_picturex0611_hydraulic_jack_fork_bottle_jack_20260713/rev_000001 | model.py:L114-L164 | structure | Plain welded box-section base with closed side walls and a rolled top edge. |
| frame_style | toe_channel | base frame section | rec_picturex0611_hydraulic_jack_fork_toe_jack_20260713/rev_000001 | model.py:L75-L199 | structure | Channel-section base extended into a low toe rail reaching under the load edge. |
| deck_fitting | flat_deck | platform load interface | rec_picturex_0611__hydraulic_jack__001__png_af55d19fd79043eeaaa91f76169ade14/rev_000001 | model.py:L175-L223 | structure | Rounded flat upper deck with slotted skirts and cross tubes underneath. |
| deck_fitting | screw_riser | platform load interface | rec_picturex0611_hydraulic_jack_fork_screw_extension_saddle_20260713/rev_000001 | model.py:L492-L597 | structure+motion | Threaded riser column with a saddle pad turned on its own REVOLUTE joint above the platform. |
| deck_fitting | vee_cradle | platform load interface | rec_picturex0611_hydraulic_jack_fork_transmission_cradle_20260714/rev_000001 | model.py:L316-L382 | structure | Vee cradle saddle whose inclined cheeks meet at the groove root, with raised end lips. |
| drive_unit | hydraulic_pump | lift actuator input | rec_picturex_0611__hydraulic_jack__001__png_af55d19fd79043eeaaa91f76169ade14/rev_000001 | model.py:L296-L367 | structure+motion | Hydraulic cylinder cradled on the base with a lever pump handle on a REVOLUTE pivot. |
| drive_unit | air_over_hydraulic | lift actuator input | rec_picturex0611_hydraulic_jack_fork_air_over_hydraulic_20260714/rev_000001 | model.py:L449-L590 | structure+motion | Air-assist can and pneumatic module with an air valve lever on a REVOLUTE pivot in place of the long hand bar. |
| arm_style | slotted_plate_arm | scissor link | rec_picturex_0611__hydraulic_jack__001__png_af55d19fd79043eeaaa91f76169ade14/rev_000001 | model.py:L60-L118 | structure | Twin pressed link plates carrying a long lightening slot, with exposed pivot heads, as on the blue lab jack. |
| arm_style | boxed_bar_arm | scissor link | rec_picturex_0611__hydraulic_jack__002__png_53523a539a204bcf896a11590eedafae/rev_000001 | model.py:L319-L350 | structure | Plain solid boxed bar links with welded end bosses and a tie spacer, as on the orange lift table. |
