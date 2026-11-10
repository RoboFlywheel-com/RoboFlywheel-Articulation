# Flexible track lighting system — SourceMap

export_category: pictureX_0611_flexible_track_lighting_system
registry_key: pictureX_0611_flexible_track_lighting_system

Records-root: `data/records`. This rebuild replaces a forbidden thin-shell that imported
`picturex_0611_source_replay` and clamped joint motion. The new template is self-contained
(stdlib + `sdk` only) and models the category directly: one lighting track carrying N
repositionable spotlight heads, each head an independent pan+tilt gimbal with a real vertical
pan axis and a real horizontal tilt trunnion.

The two source records are genuinely distinct in four orthogonal, freely-combinable ways:
track shape, TRACK-MOUNT CONSTRUCTION, head/housing profile, and gimbal/yoke mechanism. They
therefore anchor four independent component slots plus one head-count multiplicity. Every combination builds through
parameter derivation (track length / oval perimeter derived from N and the head motion envelope
so adjacent heads never collide across the full pan/tilt range).

## Source records

- REC_001 = `rec_picturex_0611__flexible_track_lighting_system__001__png__airflex_batch_20260710_eedb0610ab714620adb4449ccd2a0ecd`
  (rev_000001, 486 lines): flexible black **oval monorail** (closed spline tube), **8** hanging
  lamps, each a **cylindrical** open-lens can on a compact **crossbar trunnion** yoke; three
  ceiling suspension stems + canopies; pan REVOLUTE Z ±180°, tilt REVOLUTE Y ±50°.
- REC_002 = `rec_picturex_0611__flexible_track_lighting_system__002__png__airflex_batch_20260710_3dd257f9175a487bb8d42cefcfea70cc`
  (rev_000001, 553 lines): **straight rigid rail** (rounded extrusion + underside power channel),
  **3** pendant heads, each a **tapered lofted** open-front can with a thick front rim on a tall
  flat **U-bracket** yoke with external side pivot knobs; pan REVOLUTE Z ±2.80, tilt REVOLUTE Y ±0.70.

## Slots and candidates

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| lighting_track | flexible_oval_rail | closed-spline oval monorail | rec_picturex_0611__flexible_track_lighting_system__001__png__airflex_batch_20260710_eedb0610ab714620adb4449ccd2a0ecd/rev_000001 | model.py:L83-L140 | accepted | `tube_from_spline_points` closed oval (broad 1.22×0.56 silhouette) + 3 suspension stems/canopies |
| track_adapter | flush_block | mount embedded in the track (no link) | rec_picturex_0611__flexible_track_lighting_system__001__png__airflex_batch_20260710_eedb0610ab714620adb4449ccd2a0ecd/rev_000001 | model.py:L243-L248, L271-L276 | accepted | `track_frame.visual(Box(...), name=f"track_adapter_{index}")` is a fixed VISUAL on the track; the pan REVOLUTE `lamp_{index}_pan` is authored `parent=track_frame, child=swivel` -- no adapter link, no fixed joint |
| track_adapter | shoe_spindle_mount | dedicated rail-shoe LINK + FIXED joint | rec_picturex_0611__flexible_track_lighting_system__002__png__airflex_batch_20260710_3dd257f9175a487bb8d42cefcfea70cc/rev_000001 | model.py:L91-L116, L243-L245, L261-L268, L269-L276 | accepted | `_add_adapter_visuals` builds rail_shoe + locking_tab + swivel_boss + pan_spindle on a separate `model.part(f"adapter_{index}")`; `mount_{index}` is a FIXED articulation track->adapter and `pan_{index}` is authored `parent=adapter_{index}` -- the pan REVOLUTE's parent link changes |
| lighting_track | straight_rigid_rail | extruded straight rail | rec_picturex_0611__flexible_track_lighting_system__002__png__airflex_batch_20260710_3dd257f9175a487bb8d42cefcfea70cc/rev_000001 | model.py:L23-L33, L231-L232 | accepted | `_rail_geometry` 1.02×0.05×0.03 rounded box with underside 0.98×0.015 power channel |
| light_head | cylindrical_can | straight cylindrical lens can | rec_picturex_0611__flexible_track_lighting_system__001__png__airflex_batch_20260710_eedb0610ab714620adb4449ccd2a0ecd/rev_000001 | model.py:L25-L34, L287-L313 | accepted | `_spotlight_shell` open-lens cylinder + gold reflector disc + warm lens + Y trunnion axle |
| light_head | tapered_can | tapered lofted flared can | rec_picturex_0611__flexible_track_lighting_system__002__png__airflex_batch_20260710_3dd257f9175a487bb8d42cefcfea70cc/rev_000001 | model.py:L35-L88, L158-L180 | accepted | `_housing_geometry` twin-loft shell + front rim + rear neck; `_reflector_geometry` conical gold |
| pan_gimbal | crossbar_trunnion | compact crossbar yoke | rec_picturex_0611__flexible_track_lighting_system__001__png__airflex_batch_20260710_eedb0610ab714620adb4449ccd2a0ecd/rev_000001 | model.py:L37-L53, L250-L267 | accepted | swivel collar + drop stem + horizontal crossbar bridging two short arms capturing the axle |
| pan_gimbal | u_bracket | tall flat U-bracket yoke | rec_picturex_0611__flexible_track_lighting_system__002__png__airflex_batch_20260710_3dd257f9175a487bb8d42cefcfea70cc/rev_000001 | model.py:L91-L155 | accepted | swivel puck + stem + flat bridge + two long side arms + external pivot knobs at axle ends |

## Motion / joint anchoring (identical topology across both records; geometry differs)

- Pan joint: parent = track, child = gimbal, REVOLUTE about vertical **Z**. Source ranges ±180°
  (REC_001 L269-285) and ±2.80 (REC_002 L269-286). Template uses full ±π so pan azimuth is free.
- Tilt joint: parent = gimbal, child = head, REVOLUTE about horizontal **Y** trunnion. Source
  ranges ±50° (REC_001 L315-332) and ±0.70 (REC_002 L287-304). Template uses ±55°.
- Both records author the tilt axle (head) intentionally captured through the yoke arms — a
  PER-ELEMENT `allow_overlap(head, gimbal, elem_a="pivot_axle", elem_b=arm/crossbar)` only
  (REC_001 L444-450, REC_002 L497-504). No whole-part allowance, no motion clamp.
- The mount construction is NOT identical across the records, and it is now the `track_adapter`
  slot rather than a fold-in (see "Rejected decompositions", superseded):
  * `flush_block` reproduces REC_001: mount geometry is a fixed box visual on the track and the
    pan REVOLUTE's parent is the track part. Parts per head = 2 (gimbal, head).
  * `shoe_spindle_mount` reproduces REC_002: one extra `track_adapter__shoe_spindle_mount__
    adapter_{i}` LINK per head carrying rail_shoe / locking_tab / swivel_boss / pan_spindle,
    attached by a FIXED articulation to the track, with the pan REVOLUTE re-parented onto it.
    Parts per head = 3, joints per head = 3 (fixed + pan + tilt).
  Host adaptation absorbs the difference on both tracks: the shoe's top face is pressed
  `_SHOE_PRESS` = 0.5 mm into the rail underside (a HORIZONTAL mate, so the world-AABB overlap
  against the oval's whole-ellipse mesh AABB is only 0.5 mm on Z), and the pan pivot is dropped
  to `_SPINDLE_PAN_DROP` below the rail underside so the gimbal's swivel collar/puck journals
  0.6 mm onto the spindle tip. Both stay under `overlap_tol = 1e-3`, so no overlap allowance is
  used anywhere.

## Multiplicity — head_count (N)

- Observed N: REC_001 = 8 (`LAMP_COUNT=8`, L22, tests L379-385); REC_002 = 3 (`lamp_layout`
  3 entries, L237-241, tests require 3).
- Declared range: `head_count = 3 | 4 | 5 | 6 | 7 | 8`, applied to the whole assembly. N adds N
  gimbal parts + N pan joints + N head parts + N tilt joints, plus (with `shoe_spindle_mount`)
  N adapter links + N FIXED mount joints, or (with `flush_block`) N fixed track visuals.
- Spacing/capacity (validation): each head's worst-case horizontal reach from its pan axis is
  `head_length*sin(tilt_max) + head_radius + yoke_half_width`. Adjacent pan pivots are placed at
  `spacing = 2*reach + clearance`, so no two heads collide anywhere in the pan×tilt range.
  Straight rail: pivots at `x_i = (i-(N-1)/2)*spacing`, rail length derived from N. Oval:
  N pan pivots placed at equal arc length around the ellipse; the ellipse is uniformly scaled so
  the minimum adjacent chord ≥ spacing (uniform scale multiplies all chords linearly).

## Independent parameters and derivations (continuous — not in core/raw)

- `head_length_m` (0.066–0.115 m): housing length below the tilt pivot; drives envelope + spacing.
- `head_radius_m` (0.024–0.036 m): housing/front radius; drives lens, reflector, axle span, spacing.
- `drop_length_m` (0.045–0.100 m): gimbal drop from the pan pivot (track plane) to the tilt pivot.
- Derived: `tilt_max` fixed 55°; `head_reach`, `head_spacing`, rail length / oval semi-axes,
  reflector + lens radii, axle span, yoke arm span and knob positions, suspension stem count.

## Per-element legitimate contacts / overlaps

- `expect_contact(gimbal.swivel_collar/puck, track.adapter/shoe)` — pan bearing seats on track.
- `allow_overlap(head.pivot_axle, gimbal.<arm/crossbar>)` + `expect_contact(...)` — Y axle
  intentionally captured through the yoke; PER-ELEMENT only, scoped to that pin-through-bracket.

## Rejected decompositions

- SUPERSEDED (2026-07-27): "the template folds the fixed rail-shoe/adapter into the track part
  ... (cleaner, matches REC_001's direct track→swivel pan)". That rejection was reasoned as *not a
  clean drop-in interchange*, which is exactly the wrong reason: `TemplateDomain` has no
  compatibility gates and host adaptation is expected to absorb the difference. The two records
  genuinely disagree on this axis (REC_001 has no adapter link at all; REC_002 has a link plus a
  FIXED joint plus a re-parented pan REVOLUTE), so it is now the `track_adapter` slot and it
  raises core_domain from 8 to 16.
- A separate ceiling-mount / suspension slot is still rejected, but on evidence rather than on
  interchange grounds: only REC_001 authors suspension stems/canopies (L123-L140) and REC_002
  authors no mounting hardware above the rail at all, so a second candidate would have to be
  invented. The stems remain part of the oval track candidate's fixed silhouette.
- Head profile × gimbal are independent (both records expose a Y-axis trunnion axle on the head
  that any yoke can capture), so they are separate slots, not one fused family.
