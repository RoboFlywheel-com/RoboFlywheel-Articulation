# pictureX_0611_generator — SourceMap

source_map_schema: 1
export_category: pictureX_0611_generator
picture_category: 0611
picture_subcategory: generator
category_scope: A small hand-driven demonstration generator — one grounded frame carrying two parallel shaft lines, a hand input on the first, a visible transmission to the second, and a rotating armature turning inside stator hardware with electrical terminals on the frame. Motorised alternators, engine-driven gensets and bare electric motors are outside this host.

sync_records:
  - rec_picturex0611_generator_var_armature_coil_n2
  - rec_picturex0611_generator_var_armature_coil_n3
  - rec_picturex0611_generator_var_bevel_gear_transmission
  - rec_picturex0611_generator_var_flywheel_input
  - rec_picturex0611_generator_var_friction_wheel_drive
  - rec_picturex0611_generator_var_gearbox_side_plate
  - rec_picturex0611_generator_var_handwheel_input
  - rec_picturex0611_generator_var_idler_tension_pulley
  - rec_picturex0611_generator_var_slotted_stator_bridge
  - rec_picturex0611_generator_var_terminal_n4
  - rec_picturex0611_generator_var_twin_magnet_posts
  - rec_picturex_0611__generator__001__png_350ef02be9dc4cdc8a58c6842bafc709
  - rec_picturex_0611__generator__002__png_39eb2ba17a7d498c86c917d6ce57b54e
  - rec_picturex_0611__generator__003__png_7e039f67b7a1456d8c640d8c6af56be1
  - rec_picturex_0611__generator__004__png_11d3985262e14371b76e27c16f948615

All records are read at `revisions/rev_000001/model.py`.

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex0611_generator_var_armature_coil_n2/rev_000001 | reviewed | reference_only | Same machine as 004 with two opposed armature coil packs instead of one; N evidence for the winding loop, not a separate structural component. |
| rec_picturex0611_generator_var_armature_coil_n3/rev_000001 | reviewed | reference_only | Same machine as 004 with three coil packs; N evidence for the winding loop, not a separate structural component. |
| rec_picturex0611_generator_var_bevel_gear_transmission/rev_000001 | reviewed | used | Turns the drive through a right-angle bevel pair on its own transfer shaft instead of a parallel spur pair. Distinct transmission. |
| rec_picturex0611_generator_var_flywheel_input/rev_000001 | reviewed | used | Puts a heavy rimmed flywheel on the input shaft beside the crank so the demo keeps spinning. Distinct hand input. |
| rec_picturex0611_generator_var_friction_wheel_drive/rev_000001 | reviewed | used | Replaces the belt with rubber friction wheels and adds a `tension_carrier` on a real PRISMATIC slide that presses them together. Distinct transmission. |
| rec_picturex0611_generator_var_gearbox_side_plate/rev_000001 | reviewed | used | Encloses the wheel plane behind a bolted gearbox side plate with its own pole ring around the armature. Distinct stator family. |
| rec_picturex0611_generator_var_handwheel_input/rev_000001 | reviewed | used | Replaces the offset crank with a spoked handwheel turning on the input axis itself. Distinct hand input. |
| rec_picturex0611_generator_var_idler_tension_pulley/rev_000001 | reviewed | used | Adds a sprung `idler` pulley on its own CONTINUOUS joint that runs on the back of the belt. Distinct transmission. |
| rec_picturex0611_generator_var_slotted_stator_bridge/rev_000001 | reviewed | used | Bridges a slotted U-shaped stator over the armature with pole pads either side. Distinct stator family. |
| rec_picturex0611_generator_var_terminal_n4/rev_000001 | reviewed | reference_only | Same machine as 001 with four terminal caps instead of two; N evidence for the terminal loop, not a separate structural component. |
| rec_picturex0611_generator_var_twin_magnet_posts/rev_000001 | reviewed | used | Stands two tall magnet posts with pole pads either side of the armature instead of a closed stator. Distinct stator family. |
| rec_picturex_0611__generator__001__png_350ef02be9dc4cdc8a58c6842bafc709/rev_000001 | reviewed | used | Origin anchor: an open frame with a single offset crank and grip, a stepped shaft with a flat pulley driving the rotor, and terminal caps on the base. |
| rec_picturex_0611__generator__002__png_39eb2ba17a7d498c86c917d6ce57b54e/rev_000001 | reviewed | used | Second origin: a housing with two opposed hand cranks and grips on one main shaft, driving a meshed gear pair into the armature. |
| rec_picturex_0611__generator__003__png_7e039f67b7a1456d8c640d8c6af56be1/rev_000001 | reviewed | used | Third origin: an open frame with a flat drive belt over two pulleys and a plain pole-piece stator around the rotor. |
| rec_picturex_0611__generator__004__png_11d3985262e14371b76e27c16f948615/rev_000001 | reviewed | used | Fourth origin: a geared demo where the input crank gear drives a transfer gear into the armature, with the coil pack count called out in the part meta. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| drive_input | crank_handle | hand input | rec_picturex_0611__generator__001__png_350ef02be9dc4cdc8a58c6842bafc709/rev_000001 | model.py:L253-L275 | structure+motion | One offset `crank` web with a `handle_grip` that spins on its own CONTINUOUS pin. |
| drive_input | dual_crank | hand input | rec_picturex_0611__generator__002__png_39eb2ba17a7d498c86c917d6ce57b54e/rev_000001 | model.py:L246-L279 | structure+motion | Two opposed cranks and two grips on the same main shaft so the demo can be turned from either side. |
| drive_input | handwheel_input | hand input | rec_picturex0611_generator_var_handwheel_input/rev_000001 | model.py:L280-L295 | structure | A spoked handwheel turning on the input axis itself instead of an offset crank pin. |
| drive_input | flywheel_input | hand input | rec_picturex0611_generator_var_flywheel_input/rev_000001 | model.py:L279-L316 | structure | A heavy rimmed flywheel beside the crank web, so the input carries real stored inertia. |
| transmission | shaft_pulley_train | transmission | rec_picturex_0611__generator__001__png_350ef02be9dc4cdc8a58c6842bafc709/rev_000001 | model.py:L224-L252 | structure+motion | A stepped shaft and flat pulley pass the drive to the rotor through an intermediate jackshaft line. |
| transmission | spur_gear_pair | transmission | rec_picturex_0611__generator__004__png_11d3985262e14371b76e27c16f948615/rev_000001 | model.py:L238-L360 | structure+motion | A toothed input gear meshes straight into the transfer gear on the armature line, mimic-coupled at the tooth ratio. |
| transmission | belt_two_pulley | transmission | rec_picturex_0611__generator__003__png_7e039f67b7a1456d8c640d8c6af56be1/rev_000001 | model.py:L358-L500 | structure+motion | A flat `drive_belt` wraps a large drive pulley and a small generator pulley, with the belt itself fixed to the frame. |
| transmission | idler_tension_pulley | transmission | rec_picturex0611_generator_var_idler_tension_pulley/rev_000001 | model.py:L400-L545 | structure+motion | The same belt run plus a sprung `idler` pulley on its own CONTINUOUS joint riding the belt back. |
| transmission | friction_wheel | transmission | rec_picturex0611_generator_var_friction_wheel_drive/rev_000001 | model.py:L414-L524 | structure+motion | Rubber-tyred friction wheels replace the belt and a `tension_carrier` on a real PRISMATIC slide presses them together. |
| transmission | bevel_gear | transmission | rec_picturex0611_generator_var_bevel_gear_transmission/rev_000001 | model.py:L285-L400 | structure+motion | A right-angle bevel pair on its own transfer shaft turns the drive through 90 degrees before the armature. |
| stator_form | open_pole_stator | stator and electrical hardware | rec_picturex_0611__generator__003__png_7e039f67b7a1456d8c640d8c6af56be1/rev_000001 | model.py:L193-L357 | structure | Plain pole pieces stand either side of the rotor on the open frame, with the terminals on the base. |
| stator_form | slotted_stator_bridge | stator and electrical hardware | rec_picturex0611_generator_var_slotted_stator_bridge/rev_000001 | model.py:L250-L454 | structure | A slotted U-shaped `stator_bridge` arches over the armature with pole pads either side. |
| stator_form | twin_magnet_posts | stator and electrical hardware | rec_picturex0611_generator_var_twin_magnet_posts/rev_000001 | model.py:L389-L421 | structure | Two tall magnet posts with pole pads stand either side of the armature instead of a closed stator. |
| stator_form | gearbox_side_plate | stator and electrical hardware | rec_picturex0611_generator_var_gearbox_side_plate/rev_000001 | model.py:L144-L296 | structure | A bolted side plate encloses the wheel plane and carries its own pole ring around the armature. |

## Multiplicity and N derivation

- `coil_count = 1 | 2 | 3`, applied to `stator_form`.
  - `observed_N`: one coil pack in 004 and `gearbox_side_plate`, two in `var_armature_coil_n2`,
    three in `var_armature_coil_n3`.
  - `derived_N_range = 1..3`: the winding loop is index-general — each pack is placed at
    `2*pi*k/coil_count` around the armature — and the bound comes from keeping a real gap
    between adjacent packs at the smallest armature radius.
  - validation: each pack is placed from the same derived armature radius, and the pack width,
    the pole clearance and the armature balance mass are re-derived with it.
- `terminal_count = 2 | 3 | 4`, applied to `stator_form`.
  - `observed_N`: two terminal caps in 001/003, four in `var_terminal_n4`.
  - `derived_N_range = 2..4`: the terminal loop is index-general along the base pad; the bound
    comes from keeping a real gap between adjacent posts on the derived base width.
  - validation: each terminal is placed from the same derived base pad and its post spacing and
    cap diameter are re-derived with the count.

## Coverage note

All fifteen active records in the `0611 / generator` workbench pool are reviewed. Twelve
contribute a structural candidate — 001 and 003 each back both a hand input or stator and a
transmission — and the three pure N forks (`armature_coil_n2`, `armature_coil_n3`,
`terminal_n4`) are recorded as `reference_only` because they are the multiplicity evidence for
the two loops above. The two parallel shaft lines, the saddle bearings and the rotating armature
are shared host geometry.

`core_domain = 4 (drive_input) x 6 (transmission) x 4 (stator_form) = 96`;
`raw_domain = 96 x 3 (coil_count) x 3 (terminal_count) = 864`.
