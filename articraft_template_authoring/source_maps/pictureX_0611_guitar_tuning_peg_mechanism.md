# pictureX_0611_guitar_tuning_peg_mechanism — SourceMap

source_map_schema: 1
export_category: pictureX_0611_guitar_tuning_peg_mechanism
picture_category: 0611
picture_subcategory: guitar_tuning_peg_mechanism
category_scope: A geared guitar machine head — one grounded mount carrying N complete tuner units, each a worm shaft with a button on one end driving a worm gear on a string post that turns at the worm ratio. Friction violin pegs with no gear train, banjo planetary tuners and complete headstocks are outside this host.

sync_records:
  - rec_picturex0611_guitar_tuning_peg_var_classical_roller_post
  - rec_picturex0611_guitar_tuning_peg_var_cloverleaf_button
  - rec_picturex0611_guitar_tuning_peg_var_locking_split_post
  - rec_picturex0611_guitar_tuning_peg_var_open_back_ratio
  - rec_picturex0611_guitar_tuning_peg_var_sealed_die_cast_housing
  - rec_picturex0611_guitar_tuning_peg_var_side_mount_clover
  - rec_picturex0611_guitar_tuning_peg_var_staggered_posts
  - rec_picturex0611_guitar_tuning_peg_var_three_on_strip
  - rec_picturex_0611__guitar_tuning_peg_mechanism__001__png_6025567b16c44b3d82c56a57ea1dc988
  - rec_picturex_0611__guitar_tuning_peg_mechanism__002__png_0b7df3fa3d43402f853370564a63df8f
  - rec_picturex_0611__guitar_tuning_peg_mechanism__003__png_810f64ddef444b75a5caedd5bec3790f
  - rec_picturex_0611__guitar_tuning_peg_mechanism__004__png_48157ac16c654657b262f522935a05e2
  - rec_picturex_0611__guitar_tuning_peg_mechanism__005__png_6f66eb339bfd4847a01b803622118370

All records are read at `revisions/rev_000001/model.py`.

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex0611_guitar_tuning_peg_var_classical_roller_post/rev_000001 | reviewed | used | Replaces the upright string post with a transverse classical roller carried between two end supports. Distinct post family. |
| rec_picturex0611_guitar_tuning_peg_var_cloverleaf_button/rev_000001 | reviewed | used | A four-lobed cloverleaf button on the worm shaft instead of an oval paddle. Distinct button family. |
| rec_picturex0611_guitar_tuning_peg_var_locking_split_post/rev_000001 | reviewed | used | Splits the post into a slit hollow tube and adds a cap-head locking screw as a fourth part on its own joint about the post axis. Distinct post family, and the only source that changes the joint count. |
| rec_picturex0611_guitar_tuning_peg_var_open_back_ratio/rev_000001 | reviewed | used | A larger driven gear on a longer post support gives a higher worm ratio on the same open plate. Distinct post family. |
| rec_picturex0611_guitar_tuning_peg_var_sealed_die_cast_housing/rev_000001 | reviewed | used | Encloses the gear train in a rounded die-cast shell with its own bearing boss. Distinct mount family. |
| rec_picturex0611_guitar_tuning_peg_var_side_mount_clover/rev_000001 | reviewed | used | A narrow side-mount bracket plate that bolts to the side of the headstock rather than the back face. Distinct mount family. |
| rec_picturex0611_guitar_tuning_peg_var_staggered_posts/rev_000001 | reviewed | reference_only | Two complete tuner units staggered on one plate; N evidence for the tuner loop, not a separate structural component. |
| rec_picturex0611_guitar_tuning_peg_var_three_on_strip/rev_000001 | reviewed | reference_only | Three complete tuner units on one strip plate; N evidence for the tuner loop, not a separate structural component. |
| rec_picturex_0611__guitar_tuning_peg_mechanism__001__png_6025567b16c44b3d82c56a57ea1dc988/rev_000001 | reviewed | used | Origin anchor: an open stamped mounting plate with an exposed worm drive and gear post. |
| rec_picturex_0611__guitar_tuning_peg_mechanism__002__png_0b7df3fa3d43402f853370564a63df8f/rev_000001 | reviewed | used | Second origin: an open-back plate with raised bearing ears, and a pierced butterfly button on the worm shaft. |
| rec_picturex_0611__guitar_tuning_peg_mechanism__003__png_810f64ddef444b75a5caedd5bec3790f/rev_000001 | reviewed | used | Third origin: a sealed right-angle housing that closes over the worm and post bores. |
| rec_picturex_0611__guitar_tuning_peg_mechanism__004__png_48157ac16c654657b262f522935a05e2/rev_000001 | reviewed | used | Fourth origin: an open-back nickel tuner whose plain string post carries the driven post gear directly. |
| rec_picturex_0611__guitar_tuning_peg_mechanism__005__png_6f66eb339bfd4847a01b803622118370/rev_000001 | reviewed | used | Fifth origin: a sealed gold gearbox bulb with a paddle button on the worm shaft. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| mount_form | open_plate | mount and gear enclosure | rec_picturex_0611__guitar_tuning_peg_mechanism__001__png_6025567b16c44b3d82c56a57ea1dc988/rev_000001 | model.py:L26-L73, model.py:L165-L268 | structure | `_mounting_plate_shape` is a filleted stamped rectangle unioned with a large gear lobe and a small lower lobe, then pierced for the post journal and two screws. The worm runs in two free-standing `_annular_bearing_shape` rings on bridge tabs, so the gear train is fully exposed. |
| mount_form | eared_plate | mount and gear enclosure | rec_picturex_0611__guitar_tuning_peg_mechanism__002__png_0b7df3fa3d43402f853370564a63df8f/rev_000001 | model.py:L52-L132, model.py:L208-L218 | structure | `_make_mounting_plate` is a 17-point stamped polyline outline with rolled rims fused around the screw holes, and the worm is carried by two bent ears — each a ring plus an arm block fused onto the plate face. One welded plate solid, no separate bearing visuals. |
| mount_form | sealed_housing | mount and gear enclosure | rec_picturex_0611__guitar_tuning_peg_mechanism__003__png_810f64ddef444b75a5caedd5bec3790f/rev_000001 | model.py:L51-L105, model.py:L191-L215 | structure | `_build_housing` closes a filleted box, an elliptical loft shoulder and a top boss over the train, then cuts a gear cavity, worm cavity, worm bore and post bore. A round proud cover with a bezel and two `_build_cover_screw` heads seals the gear side. |
| mount_form | die_cast_housing | mount and gear enclosure | rec_picturex0611_guitar_tuning_peg_var_sealed_die_cast_housing/rev_000001 | model.py:L26-L103, model.py:L194-L226 | structure | `_sealed_housing_shape` is a filleted 28x14x28 mm block with three protruding cylindrical bearing bosses (worm above and below, post on the front face), through-bores for both shafts, two back mounting holes, and a parting-line ridge around the equator. |
| mount_form | side_mount_bracket | mount and gear enclosure | rec_picturex0611_guitar_tuning_peg_var_side_mount_clover/rev_000001 | model.py:L51-L102, model.py:L196-L222 | structure | `_build_mounting_plate` is a narrow 20x3x40 mm flat bracket with compact worm and post bearing bosses unioned on, both shaft bores and two screw holes cut through, and `_build_mount_screw_head` phillips heads seated on the back face. |
| mount_form | gearbox_bulb | mount and gear enclosure | rec_picturex_0611__guitar_tuning_peg_mechanism__005__png_6f66eb339bfd4847a01b803622118370/rev_000001 | model.py:L44-L98, model.py:L153-L236 | structure | `_housing_shell` is a circular bulb around the gear unioned with a tall cylindrical worm-bearing tower and a filleted shoulder, hollowed by a gear cavity, worm cavity and both bores. A medallion, a knurled bezel ring, a nickel ring and two cover screws dress the front. |
| post_form | plain_post | string post | rec_picturex_0611__guitar_tuning_peg_mechanism__004__png_48157ac16c654657b262f522935a05e2/rev_000001 | model.py:L268-L328 | structure+motion | The driven `SpurGear` sits on a hub with a plain stepped axle and a larger-diameter string post projecting behind the mount, closed by a slotted gear screw on the front face. This is the baseline post: one part, one joint. |
| post_form | high_ratio_post | string post | rec_picturex0611_guitar_tuning_peg_var_open_back_ratio/rev_000001 | model.py:L26-L63, model.py:L352-L414 | structure+motion | The driven gear goes from 14 to 21 teeth on the same module, so the mimic multiplier changes with it, and the host plate grows from 28x32 to 34x42 mm with a 14 mm gear lobe to keep the bigger wheel enclosed. Ratio is a real geometric change, not a scale. |
| post_form | locking_split_post | string post | rec_picturex0611_guitar_tuning_peg_var_locking_split_post/rev_000001 | model.py:L170-L251, model.py:L409-L423, model.py:L443-L453 | structure+motion | `_make_locking_split_post` is a hollow tube whose wall is slit for 70% of its height, and `_make_locking_screw` is a cap head with a hex socket. The screw is a **separate part** on its own CONTINUOUS joint about the post axis, so this candidate adds one part and one joint per unit. |
| post_form | classical_roller_post | string post | rec_picturex0611_guitar_tuning_peg_var_classical_roller_post/rev_000001 | model.py:L135-L192, model.py:L359-L396 | structure | `_roller_yoke` carries a collar, a bridge plate and two prongs projecting along the post axis with a transverse axle at their tips, and `_string_roller` is a barrel spanning between them. The string wraps a crosswise roller instead of an upright post. |
| button_form | paddle_button | button | rec_picturex_0611__guitar_tuning_peg_mechanism__005__png_6f66eb339bfd4847a01b803622118370/rev_000001 | model.py:L101-L123, model.py:L272-L298 | structure | `_paddle_button` is a broad filleted keystone plate with clipped lower corners, extruded in the plane containing the shaft, plus a recessed oval washer and a face screw. One solid blade. |
| button_form | butterfly_button | button | rec_picturex_0611__guitar_tuning_peg_mechanism__002__png_0b7df3fa3d43402f853370564a63df8f/rev_000001 | model.py:L135-L172, model.py:L258-L276 | structure | `_make_button` is an ellipse unioned with a tapered lower web, then pierced by four rotated elliptical windows that leave a central X-shaped load-carrying web. The open windows are the identity. |
| button_form | cloverleaf_button | button | rec_picturex0611_guitar_tuning_peg_var_cloverleaf_button/rev_000001 | model.py:L108-L140, model.py:L227-L239 | structure | `_build_cloverleaf_button` unions a centre disk with four lobe cylinders at 90 degree spacing into a plate lying **perpendicular** to the shaft axis, with a hub boss below and a bore through. Unlike the other two it sweeps a disc, not a blade. |

## Shared host mechanism

Every one of the thirteen records builds the same kinematic host, so it is shared geometry
rather than a slot:

- the mount is the single root part; the worm rotor and the driven post are its children;
- the worm turns about **+Z** with its button on top, and the string post turns about **+Y**,
  the two axes perpendicular and non-intersecting (001 L340-L349/L407-L417, 002 L333-L356,
  003 L311-L331, 004 L330-L360, 005 L349-L371);
- the post joint always carries `Mimic(worm_joint, multiplier=-1/teeth_number)` — 14, 19, 18,
  14, 24 and 21 teeth occur across the pool, so the ratio tracks the driven tooth count;
- the worm is `Worm(...)` built along local X and rotated onto the vertical shaft; the wheel is
  `SpurGear(...)` built along local Z and rotated onto the post axis;
- 3 of the 5 origins (002, 004, 005) put the decorated cover/screw face toward **-Y** and run
  the post out toward **+Y**; 001 and 003 mirror it. The -Y-front majority is adopted.

## Multiplicity and N derivation

- `tuner_count = 1 | 2 | 3`, applied to `mount_form`.
  - `observed_N`: one unit in all five origins, two staggered units in `var_staggered_posts`,
    three on a strip in `var_three_on_strip`.
  - `derived_N_range = 1..3`: each unit is a complete worm-and-post assembly repeated at the
    same derived pitch along the mount, so the loop is index-general; the bound comes from the
    mount length a strip still needs and from the per-build pose budget, so the six-a-side
    headstock strip is not reproduced at full count.
  - validation: each unit adds one worm part, one post part and one mimic pair, and the mount
    length, the bearing stations and the button clearance are re-derived with the count.

## Coverage note

All thirteen active records in the `0611 / guitar_tuning_peg_mechanism` workbench pool are
reviewed. Eleven contribute a structural candidate — 002 and 005 each back both a mount and a
button — and the two pure N forks (`staggered_posts`, `three_on_strip`) are recorded as
`reference_only` because they are the multiplicity evidence for the tuner loop. The worm-to-gear
mimic chain, the post bushings and the plated colourway are shared host geometry.

`core_domain = 6 (mount_form) x 4 (post_form) x 3 (button_form) = 72`;
`raw_domain = 72 x 3 (tuner_count) = 216`.
