# pictureX_0611_hydraulic_jack1 — SourceMap

source_map_schema: 1
export_category: pictureX_0611_hydraulic_jack1
picture_category: 0611
picture_subcategory: hydraulic_jack1
category_scope: A hand-operated vertical hydraulic ram jack that stands on its own base — a rigid frame carrying an upright hydraulic cylinder, a ram that extends upward out of that bore, a lever hand pump and a screw release valve. Wheeled trolley chassis and horizontal lift-arm jacks are outside this host and belong to pictureX_0611_hydraulic_jack2.

sync_records:
  - rec_picturex0611_hydraulic_jack1_fork_air_over_hydraulic_module_20260713
  - rec_picturex0611_hydraulic_jack1_fork_bottle_jack_20260713
  - rec_picturex0611_hydraulic_jack1_fork_double_stage_ram_20260713
  - rec_picturex0611_hydraulic_jack1_fork_floor_trolley_jack_20260713
  - rec_picturex0611_hydraulic_jack1_fork_motorcycle_platform_20260714
  - rec_picturex0611_hydraulic_jack1_fork_safety_lock_bar_20260714
  - rec_picturex0611_hydraulic_jack1_fork_screw_extension_saddle_20260714
  - rec_picturex0611_hydraulic_jack1_fork_toe_jack_20260713
  - rec_picturex0611_hydraulic_jack1_fork_transmission_cradle_20260713
  - rec_picturex_0611__hydraulic_jack1__001__png_fe4f01a5f14542c8ac8e1e3e53fb8613
  - rec_picturex_0611__hydraulic_jack1__002__png_343b03cbe8414658969055f2ca9c7a13

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__hydraulic_jack1__001__png_fe4f01a5f14542c8ac8e1e3e53fb8613/rev_000001 | reviewed | used | Image-grounded base: yellow ram cylinder, ram rod with flat saddle, lever hand pump in a clevis, screw release valve, manifold and routed hose. Supplies the host mechanism plus the chrome_rod, flat_saddle and lever_pump candidates. |
| rec_picturex_0611__hydraulic_jack1__002__png_343b03cbe8414658969055f2ca9c7a13/rev_000001 | reviewed | reference_only | Red bottle jack from 002.png. Same upright-cylinder-plus-lever-pump mechanism as 001 with no additional component structure; its base pad is already covered by the bottle_jack fork. |
| rec_picturex0611_hydraulic_jack1_fork_double_stage_ram_20260713/rev_000001 | reviewed | used | Splits the ram into two nested telescopic stages with a machined shoulder collar and stop land, each on its own PRISMATIC joint. Source for the stepped_ram stage form and for the telescopic multiplicity rule. |
| rec_picturex0611_hydraulic_jack1_fork_screw_extension_saddle_20260714/rev_000001 | reviewed | used | Adds a threaded extension screw with a collar on the ram head, carried on a REVOLUTE joint. Source for the screw_extension load interface. |
| rec_picturex0611_hydraulic_jack1_fork_transmission_cradle_20260713/rev_000001 | reviewed | used | Replaces the flat saddle with a vee-grooved cradle with raised side lips. Source for the grooved_cradle load interface. |
| rec_picturex0611_hydraulic_jack1_fork_air_over_hydraulic_module_20260713/rev_000001 | reviewed | used | Adds an air motor can, inlet fitting and a short trigger lever alongside the hand pump. Source for the air_over_hydraulic pump drive. |
| rec_picturex0611_hydraulic_jack1_fork_bottle_jack_20260713/rev_000001 | reviewed | used | Compact bottle-jack body on a plain rolled base pad with a rimmed edge. Source for the flat_pad base mount. |
| rec_picturex0611_hydraulic_jack1_fork_safety_lock_bar_20260714/rev_000001 | reviewed | used | Its frame stands on a wider bolt-down flange with corner fixing bosses; source for the flanged_bolt base mount. The lock bar itself is not taken as a slot because its pawl only makes sense against a specific rack pitch on the ram, which would couple two slots through a shared tooth grid. |
| rec_picturex0611_hydraulic_jack1_fork_toe_jack_20260713/rev_000001 | reviewed | used | Puts the cylinder on twin channel skids with a front toe plate reaching under a low load edge. Source for the channel_skid base mount. |
| rec_picturex0611_hydraulic_jack1_fork_floor_trolley_jack_20260713/rev_000001 | reviewed | rejected_category_drift | Replaces the standing frame with a wheeled chassis and a horizontal lift arm on a second REVOLUTE joint. That is a whole-host topology change, not a component swap, and it duplicates pictureX_0611_hydraulic_jack2. |
| rec_picturex0611_hydraulic_jack1_fork_motorcycle_platform_20260714/rev_000001 | reviewed | rejected_category_drift | Turns the jack into a wide wheeled motorcycle lift platform; same whole-host change as the floor trolley fork and outside this category scope. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| ram_stage | chrome_rod | ram stage tube | rec_picturex_0611__hydraulic_jack1__001__png_fe4f01a5f14542c8ac8e1e3e53fb8613/rev_000001 | model.py:L273-L291 | structure | Plain polished ram rod with a wiper-riding land and a saddle disc on top. |
| ram_stage | stepped_ram | ram stage tube | rec_picturex0611_hydraulic_jack1_fork_double_stage_ram_20260713/rev_000001 | model.py:L279-L325 | structure+motion | Telescopic stage tube turned down to a neck above a machined shoulder collar, with a stop land at the foot; each stage carries its own PRISMATIC joint. |
| head_fitting | flat_saddle | ram load interface | rec_picturex_0611__hydraulic_jack1__001__png_fe4f01a5f14542c8ac8e1e3e53fb8613/rev_000001 | model.py:L273-L291 | structure | Knurled flat saddle disc with a hardened contact face on the ram head. |
| head_fitting | screw_extension | ram load interface | rec_picturex0611_hydraulic_jack1_fork_screw_extension_saddle_20260714/rev_000001 | model.py:L329-L361 | structure+motion | Threaded extension screw and collar on the ram head, turned on its own REVOLUTE joint to add reach. |
| head_fitting | grooved_cradle | ram load interface | rec_picturex0611_hydraulic_jack1_fork_transmission_cradle_20260713/rev_000001 | model.py:L220-L246 | structure | Vee-grooved transmission cradle whose two inclined cheeks meet at the groove root, with raised side lips. |
| pump_drive | lever_pump | pump input | rec_picturex_0611__hydraulic_jack1__001__png_fe4f01a5f14542c8ac8e1e3e53fb8613/rev_000001 | model.py:L293-L312 | structure | Bare lever bar with a rubber grip swinging on the pump clevis. |
| pump_drive | air_over_hydraulic | pump input | rec_picturex0611_hydraulic_jack1_fork_air_over_hydraulic_module_20260713/rev_000001 | model.py:L338-L381 | structure | Air motor can with a banded shell and inlet fitting on the pump body, driven by a short trigger lever instead of a long hand bar. |
| base_mount | flat_pad | base footprint | rec_picturex0611_hydraulic_jack1_fork_bottle_jack_20260713/rev_000001 | model.py:L87-L201 | structure | Plain rolled base pad with a pressed rim under the cylinder. |
| base_mount | flanged_bolt | base footprint | rec_picturex0611_hydraulic_jack1_fork_safety_lock_bar_20260714/rev_000001 | model.py:L189-L243 | structure | Wider bolt-down flange carrying four corner fixing bosses and bolt heads. |
| base_mount | channel_skid | base footprint | rec_picturex0611_hydraulic_jack1_fork_toe_jack_20260713/rev_000001 | model.py:L144-L333 | structure | Twin folded channel skids lifting the plate clear of the floor, with a front toe plate. |
