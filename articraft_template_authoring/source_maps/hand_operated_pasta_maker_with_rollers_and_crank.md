# hand_operated_pasta_maker_with_rollers_and_crank — SourceMap

source_map_schema: 1
export_category: hand_operated_pasta_maker_with_rollers_and_crank
picture_category: 0611
picture_subcategory: hand_operated_pasta_maker_with_rollers_and_crank
category_scope: One chrome-bodied hand-cranked sheet pasta machine. The host is always the
  single load-bearing frame of source 001: broad flat base, two sloping side cheeks pierced by
  roller bearing bores, polished front apron with rolled lip, lower crossbar, upper cutter guard
  with tabs, and an under-table clamp bracket. Inside that host the sheet-roller nip, the cutter
  stage, the crank, the drive-side gear train, the thickness selector and the clamp screws are
  the replaceable mechanisms. Loose accessories (drying racks, ravioli attachments, separate
  motor units) are outside the host boundary and are not modelled.

Authoritative records are under
`<ARTI_SKILL_ROOT>/articraft_data/data/records/<record>/revisions/rev_000001/model.py`.
The single source image `pictureX/0611/hand_operated_pasta_maker_with_rollers_and_crank/001.png`
and all nine source models were inspected before this map was written.

All eight forks keep source 001's `_frame_shape` host verbatim except where their own structural
delta demands a host cut: `three_roller_feed` adds one bearing bore `(-0.007, 0.153)` to the side
profile, and `twin_screw_clamp` rebuilds the single clamp bracket as an indexed loop over
`CLAMP_X_CENTERS = (-0.045, 0.045)`. That is exactly the host-adaptation evidence the template
needs, so the frame stays one shared structural host and is not split into a structural family.

Slot independence: the transmission lives on the −X drive cheek, the crank on the +X socket, the
thickness selector on the −X lower boss, the cutter stage on the upper `(y≈0.043..0.069, z≈0.145)`
cradle, feed rollers in the `z≈0.126..0.153` bore column and clamp screws under the base. These
six regions never share geometry, so every combination is buildable through local host adaptation
(one extra bearing bore, one extra clamp bracket, a cassette guide rail, a detent-plate seat).
The `exposed_twin_gear` fork placed its spur pair on the +X crank cheek; the template normalises
every transmission candidate onto the −X cheek used by source 001 and by `enclosed_gears`, so the
crank socket stays free for both crank candidates. That is a mirror of the source placement, not a
change of the gear mechanism.

sync_records:
  - rec_picturex_0611__hand_operated_pasta_maker_with_rollers_and_crank__001__png_c564ec43cdba467fa808bf8fd76627c8
  - rec_picturex0611_pasta_var_detent_thickness
  - rec_picturex0611_pasta_var_enclosed_gears
  - rec_picturex0611_pasta_var_exposed_twin_gear
  - rec_picturex0611_pasta_var_folding_crank
  - rec_picturex0611_pasta_var_interchangeable_cutter
  - rec_picturex0611_pasta_var_single_cutter_attachment
  - rec_picturex0611_pasta_var_three_roller_feed
  - rec_picturex0611_pasta_var_twin_screw_clamp

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__hand_operated_pasta_maker_with_rollers_and_crank__001__png_c564ec43cdba467fa808bf8fd76627c8/rev_000001 | reviewed | used | Baseline host and four candidates: shared frame, open pinion transmission, rigid offset crank, fluted rotary thickness dial, fixed twin cutter, single clamp screw. |
| rec_picturex0611_pasta_var_exposed_twin_gear/rev_000001 | reviewed | used | Transmission candidate `exposed_twin_spur`: two real involute `SpurGear` parts on their own continuous joints, half-tooth clocked to mesh. |
| rec_picturex0611_pasta_var_enclosed_gears/rev_000001 | reviewed | used | Transmission candidate `enclosed_gear_case`: bolted sheet-metal shell with bearing collars, flange, and a hinged access cover on a real revolute. |
| rec_picturex0611_pasta_var_folding_crank/rev_000001 | reviewed | used | Crank candidate `folding_two_link_crank`: inner/outer links, visible pivot pin, added revolute fold joint. |
| rec_picturex0611_pasta_var_detent_thickness/rev_000001 | reviewed | used | Thickness candidate `indexed_detent_lever`: pivot hub + arm + detent pin against a notched frame-mounted detent plate, bounded revolute. |
| rec_picturex0611_pasta_var_interchangeable_cutter/rev_000001 | reviewed | used | Cutter candidate `removable_cassette`: keyed cartridge on a prismatic lift-out, carrying two cassette rollers on their own continuous joints. |
| rec_picturex0611_pasta_var_single_cutter_attachment/rev_000001 | reviewed | used | Cutter candidate `single_narrow_module`: one short 15-disc cutter shaft with its own driven gear, crank-mimicked at 1.33. |
| rec_picturex0611_pasta_var_three_roller_feed/rev_000001 | reviewed | used | Multiplicity evidence for `feed_roller_count`: one indexed upper idler at `(-0.007, 0.153)` plus the matching extra host bearing bore. |
| rec_picturex0611_pasta_var_twin_screw_clamp/rev_000001 | reviewed | used | Multiplicity evidence for `clamp_screw_count`: loop-emitted indexed clamp brackets and screws at `CLAMP_X_CENTERS`, broad pads. |

No record was rejected, duplicated or kept as reference only: every one of the nine sources
contributes either a candidate or a multiplicity rule.

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| transmission | open_pinion_pair | exposed pinion visuals fused to the roller shafts | rec_picturex_0611__hand_operated_pasta_maker_with_rollers_and_crank__001__png_c564ec43cdba467fa808bf8fd76627c8/rev_000001 | model.py:L52-L64; model.py:L296-L342 | structure | `_gear_shape` builds an 18-tooth alternating-radius pinion at `x=-0.112` for both smooth rollers and a 16-tooth pinion at `x=+0.116` for both cutters; the gears are visuals of the roller parts, so torque transfer is expressed purely by the `Mimic` chain. |
| transmission | exposed_twin_spur | two independent meshing spur-gear parts | rec_picturex0611_pasta_var_exposed_twin_gear/rev_000001 | model.py:L68-L94; model.py:L398-L418; model.py:L493-L516 | structure+motion | `SpurGear(module=0.002, teeth_number=17, width=0.006)` bored 9 mm, rotated onto the X shaft axis, with the driven gear clocked by `pi/17` so teeth interleave across the 34 mm roller centre distance; each gear has an 8 mm annular hub and its own continuous joint mimicking the crank at ±1.0. |
| transmission | enclosed_gear_case | bolted gear shell plus hinged access cover | rec_picturex0611_pasta_var_enclosed_gears/rev_000001 | model.py:L263-L341; model.py:L342-L376; model.py:L505-L551; model.py:L630-L655 | structure+motion | `_gear_housing_shape` cuts a 2.5 mm-wall cavity open on −X, drills both shaft pass-throughs, adds bearing collars, a bolted mounting flange with four fastener holes, a top-edge hinge barrel and an internal gear support shelf; `_housing_cover_shape` is a panel with three hinge knuckles and a latch tab on a 0–1.8 rad revolute. |
| crank | rigid_offset_crank | one-piece bent crank + free grip | rec_picturex_0611__hand_operated_pasta_maker_with_rollers_and_crank__001__png_c564ec43cdba467fa808bf8fd76627c8/rev_000001 | model.py:L233-L237; model.py:L344-L363; model.py:L401-L419 | structure | `_crank_shape` is a square-socket insert from `x=-0.011` to `x=0.030`, a radial leg to `(0.045, -0.026)` and a grip stub; the black grip is a separate part free-spinning on `crank_to_grip`. |
| crank | folding_two_link_crank | two-link crank with pinned fold joint | rec_picturex0611_pasta_var_folding_crank/rev_000001 | model.py:L233-L243; model.py:L244-L254; model.py:L359-L391; model.py:L442-L465 | structure+motion | `_crank_inner_shape` ends in a 12 mm hinge eye carrying a visible 2.5 mm pivot pin; `_crank_outer_shape` starts at a mating eye and continues the radial leg to the grip stub; `crank_inner_to_outer` is a 0–2.8 rad revolute about the shaft-parallel X axis so the outer link folds against the body. |
| thickness_adjust | fluted_rotary_dial | fluted rotary knob on a side boss | rec_picturex_0611__hand_operated_pasta_maker_with_rollers_and_crank__001__png_c564ec43cdba467fa808bf8fd76627c8/rev_000001 | model.py:L240-L260; model.py:L365-L376; model.py:L459-L468 | structure | `_dial_shape` extrudes a 32-point alternating 21/19 mm flute profile plus a 4.3 mm captive stem and a 15 mm index face; the marker sphere reads the selected step; the frame carries a hollow boss ring at `(-0.058, 0.087)`. |
| thickness_adjust | indexed_detent_lever | detent lever against a notched plate | rec_picturex0611_pasta_var_detent_thickness/rev_000001 | model.py:L240-L243; model.py:L246-L278; model.py:L280-L318; model.py:L430-L445; model.py:L527-L544 | structure+motion | `_lever_shape` is a captive stem, a 10 mm pivot hub, a 48 mm flat arm, a finger grip and a 2.5 mm detent pin at radius 10 mm; `_detent_plate_shape` is a bored 18 mm plate whose outer edge is cut by `_LEVER_DETENT_COUNT = 7` scallops spread over `_LEVER_ARC_SWEEP = 1.05` rad at the pin radius, with a mounting tab into the cheek. |
| cutter_stage | fixed_twin_cutter | two permanently mounted cutter rollers | rec_picturex_0611__hand_operated_pasta_maker_with_rollers_and_crank__001__png_c564ec43cdba467fa808bf8fd76627c8/rev_000001 | model.py:L216-L230; model.py:L320-L342; model.py:L440-L458 | structure | `_cutter_roller_shape` is an 8.2 mm core with a through axle and 25 discs of radius 10.5 mm at 6 mm pitch; the two shafts sit in the frame's `(0.043, 0.145)` and `(0.069, 0.145)` bores and counter-rotate through a mimic pair. |
| cutter_stage | removable_cassette | keyed lift-out cartridge with two rollers | rec_picturex0611_pasta_var_interchangeable_cutter/rev_000001 | model.py:L235-L316; model.py:L317-L341; model.py:L432-L472; model.py:L573-L605 | structure+motion | `_cassette_frame_shape` builds two side plates, a top bridge with grip rib, a front entry lip, a rear separator comb, four keyed outer grooves and two bored roller bearings; `_cassette_roller_shape` uses an asymmetric axle so the cutter gear sits outside the cassette plate; `frame_to_cassette` is a 0–60 mm vertical lift-out and both cassette rollers are children of the cassette. |
| cutter_stage | single_narrow_module | one short removable cutter attachment | rec_picturex0611_pasta_var_single_cutter_attachment/rev_000001 | model.py:L232-L250; model.py:L343-L359; model.py:L463-L473 | structure+motion | `_cutter_module_shape` is a 48 mm-long, 8.0 mm core with only 15 discs, visibly narrower than the sheet rollers, carried on an axle that reaches its own 14-tooth driven gear at `x=0.108`; `frame_to_cutter_module` mimics the crank at 1.33 to express the smaller pitch diameter. |
| feed_rollers | smooth_nip_roller | indexed polished sheet roller on the shared bore column | rec_picturex0611_pasta_var_three_roller_feed/rev_000001 | model.py:L67-L110; model.py:L321-L332; model.py:L453-L462 | structure+motion | This is the multiplicity item candidate emitted N times. The fork proves the rule is index-general at the host: one extra entry `(-0.007, 0.153)` in `_frame_shape`'s `bearing_centers` produces the matching bore, both collar rings and the side-cheek support, and the extra roller is a full `_smooth_roller_shape` part on its own continuous joint mimicking the crank at ±1.0. |
| clamp_screws | tommy_bar_screw_clamp | indexed under-frame clamp bracket with tommy-bar screw | rec_picturex0611_pasta_var_twin_screw_clamp/rev_000001 | model.py:L26-L28; model.py:L93-L116; model.py:L388-L412; model.py:L482-L496 | structure+motion | This is the multiplicity item candidate emitted N times. Bracket and screw both come from one loop over `CLAMP_X_CENTERS = (-0.045, 0.045)` at `CLAMP_Y = 0.055`, `CLAMP_Z_ORIGIN = -0.056`; each index owns a drop, a tapped jaw, a bored hole, a threaded stem, a broad pad, a tommy handle and its own continuous screw joint. |

## Multiplicity evidence

| Multiplicity | Item slot | Source rule | Record/Revision | Exact model.py:Lx-Ly | Evidence |
|---|---|---|---|---|---|
| feed_roller_count | feed_rollers | indexed upper idler above the smooth nip | rec_picturex0611_pasta_var_three_roller_feed/rev_000001 | model.py:L91 (frame bearing bore list); model.py:L321-L332; model.py:L453-L462 | The fork proves the rule is index-general at the host: one extra entry `(-0.007, 0.153)` in `_frame_shape`'s `bearing_centers` produces the matching bore, collar pair and side-cheek support, and the idler is a full `_smooth_roller_shape` part on a continuous joint mimicking the crank. The template keeps N ∈ {2, 3}: the usable bore column between the nip at `z=0.126` and the cutter guard at `z=0.163` is 37 mm, so a second idler at the 15 mm roller radius has no supported seat. That is a host-capacity bound, not a source-value bound. |
| clamp_screw_count | clamp_screws | loop-emitted indexed under-frame clamps | rec_picturex0611_pasta_var_twin_screw_clamp/rev_000001 | model.py:L26-L28; model.py:L93-L116 (clamp bracket loop); model.py:L388-L412; model.py:L482-L496 | The fork emits both bracket and screw from one loop over `CLAMP_X_CENTERS = (-0.045, 0.045)` at `CLAMP_Y = 0.055`, `CLAMP_Z_ORIGIN = -0.056`, each with its own threaded stem, broad pad, tommy handle and continuous screw joint. The template keeps N ∈ {1, 2}: the 215 mm base spans the two source centres with margin, and a third bracket would land under the crank-side cheek. |
