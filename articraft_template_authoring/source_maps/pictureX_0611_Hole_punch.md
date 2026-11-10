# pictureX_0611_Hole_punch — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Hole_punch
picture_category: 0611
picture_subcategory: Hole_punch
category_scope: Heavy-duty desk paper punches: one or more vertical punch pins guided over matching dies on a stable metal base, driven by a hand lever or press plunger, with adjustable paper registration guides and a chip bed or catch tray; office plier punches, staplers, eyelet presses and guillotines are not candidates.

sync_records:
  - rec_picturex0611_hole_punch_var_cloop
  - rec_picturex0611_hole_punch_var_lever_linkage
  - rec_picturex0611_hole_punch_var_n3
  - rec_picturex0611_hole_punch_var_plunger
  - rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d
  - rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d/rev_000001 | reviewed | used | First origin: tapered cast nose base with a one-piece hood, a single long ball-grip lever, one deep punch carriage, a side guide rail with sliding paper stops and a pull-out chip tray. |
| rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff/rev_000001 | reviewed | used | Second origin: bench base with a built-up twin side-plate frame, a compound twin-strap U-grip handle, two collared punch carriages over annular dies, and bed-mounted lateral and depth guides on a fixed tray. |
| rec_picturex0611_hole_punch_var_cloop/rev_000001 | reviewed | used | Only the frame family is reused: a one-piece deep-throat C-loop cast profile extruded in y with widened pivot cheeks capturing the handle axle. |
| rec_picturex0611_hole_punch_var_plunger/rev_000001 | reviewed | used | Only the actuation family is reused: a guided stem through the head-beam bore with a return-spring collar, mushroom press cap and driver plate, on a PRISMATIC joint instead of a lever. |
| rec_picturex0611_hole_punch_var_lever_linkage/rev_000001 | reviewed | used | Only the actuation family is reused: a bored drag-link plate with captured pins at both ends, pivoting on the handle and mimicking it. |
| rec_picturex0611_hole_punch_var_n3/rev_000001 | reviewed | reference_only | Only the station multiplicity rule is reused: PUNCH_STATION_COUNT with an evenly spaced 54 mm y-position loop emitting uniform carriages and dies. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| frame_form | nose_hood | one-piece cast hood | rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d/rev_000001 | model.py:L35-L111 | structure | A tapered nose footprint intersected with a side wedge carries a hood cut by a central lever throat and an axle bore. |
| frame_form | side_plate | built-up twin side-plate frame | rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff/rev_000001 | model.py:L108-L158 | structure | Two rear side plates with rounded pivot bosses, a lower crossbeam, a head neck and a head beam bridged by two bearing blocks. |
| frame_form | c_loop | one-piece deep-throat C frame | rec_picturex0611_hole_punch_var_cloop/rev_000001 | model.py:L32-L87 | structure | A closed C profile drawn in xz and extruded in y, with a cut throat and two widened pivot cheeks. |
| actuation | direct_lever | single long lever arm | rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d/rev_000001 | model.py:L112-L133 | structure+motion | An annular pivot eye bored for the axle carries a long flat bar ending in a ball grip and swings on one revolute axis. |
| actuation | compound_lever | twin-strap compound lever | rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff/rev_000001 | model.py:L175-L220 | structure+motion | Two rounded straps outboard of the frame carry pivot discs and a broad U-shaped cross grip on a single revolute axis. |
| actuation | plunger | vertical press plunger | rec_picturex0611_hole_punch_var_plunger/rev_000001 | model.py:L164-L224 | structure+motion | A guided stem through the head-beam bore carries a return-spring collar, a mushroom press cap and a driver plate on a prismatic joint. |
| actuation | lever_linkage | lever with drag-link transmission | rec_picturex0611_hole_punch_var_lever_linkage/rev_000001 | model.py:L155-L197 | structure+motion | A flat link plate with real pin bores at both ends is captured by pins and pivots on the handle as a visible transmission. |
| punch_station | collared_pin | collared guided carriage | rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff/rev_000001 | model.py:L222-L262 | structure | The carriage block carries an upper guide stem, a spring cap collar and a short pin over an annular die. |
| punch_station | long_pin | deep single-throw carriage | rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d/rev_000001 | model.py:L407-L434 | structure | A wider carriage block drives one long punch pin through a deep throat with no collar. |
| paper_guide | rail_guides | side rail with sliding stops | rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d/rev_000001 | model.py:L435-L494 | structure+motion | Two collared stops with fences slide along a graduated side rail on independent prismatic joints. |
| paper_guide | bed_guides | bed lateral and depth stops | rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff/rev_000001 | model.py:L263-L333 | structure+motion | A lateral fence slides across the bed and a depth fence slides along it, each on a footed knob-topped carrier. |
| chip_handling | pull_out_tray | pull-out chip drawer | rec_picturex_0611__hole_punch__001__png_71c0df550fa24757bcee07669b2a4e6d/rev_000001 | model.py:L162-L206 | structure+motion | A thin catch tray following the base underside slides out on a prismatic joint and carries a pull tab and loop. |
| chip_handling | fixed_bed | fixed paper bed plate | rec_picturex_0611__hole_punch__002__png_a3a370f3dd1245beb455c2172430dfff/rev_000001 | model.py:L86-L107 | structure | A rounded bed plate with a front pull lip is fixed on the deck in front of the punch line. |

## Component evidence

- The base, dies and punch chain are identity-fixed host structure from both origins
  (001 `model.py:L247-L316` base, die plate and pedestal; 002 `model.py:L50-L85` deck, feet and
  annular dies), so they are not a slot.
- Station multiplicity comes from `rec_picturex0611_hole_punch_var_n3/rev_000001`
  `model.py:L33-L41`, which derives evenly spaced y positions from a station count rather than
  hard-coding two holes; 001 (N=1) and 002 (N=2) are the other reviewed counts.
- The drag link mimics the handle rather than driving the carriage, because the SDK has no
  revolute-to-prismatic mimic; the same limitation is visible in
  `rec_picturex0611_hole_punch_var_lever_linkage/rev_000001` `model.py:L508-L530`.
