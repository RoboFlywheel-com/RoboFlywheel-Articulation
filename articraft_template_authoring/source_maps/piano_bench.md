# piano_bench — SourceMap

export_category: piano_bench

Authoritative records live under `<ARTI_SKILL_ROOT>/arti-template/data/records`.

SOURCES = 12: three origin anchors (`__001`, `__002`, `__003`) plus nine
single-axis fork variants. For the `piano_bench` category the recognizable
identity is a **wide two-person bench seat carried on a grounded frame with a
real height-adjustment mechanism**. Every origin anchor supplies that mechanism
directly: 001 a threaded side-knob spindle driving a guided storage carriage,
002 a side handwheel driving a paired lifting yoke, 003 twin lift posts inside
welded pedestal sleeves. Height adjustment is therefore the category's core
mechanism, not an optional feature, and it is modelled as a **mandatory slot**:
every candidate emits at least one rotary control plus the prismatic seat lift.
This is the direct fix for the defect that motivated the rebuild — the previous
template made the storage lid the only articulation source, so seeds that
sampled the no-lid candidate exported rigid bodies.

sync_records:
  - rec_picturex_0611__piano_bench__001__png_79e7aa5905704c5ea4666f6ea07be47d
  - rec_picturex_0611__piano_bench__002__png_40f64d0afe014cf084e43a5c586b96f2
  - rec_picturex_0611__piano_bench__003__png_9089cd9627714abeb4526ba1b9a84e99
  - rec_0611_piano_bench_var_support_four_leg_apron
  - rec_0611_piano_bench_var_support_folding_x_frame
  - rec_0611_piano_bench_var_seat_form_round_stool
  - rec_0611_piano_bench_var_seat_form_duet_rectangle
  - rec_0611_piano_bench_var_height_mechanism_central_spindle
  - rec_0611_piano_bench_var_height_mechanism_twin_side_knobs
  - rec_0611_piano_bench_var_height_mechanism_scissor_lift
  - rec_0611_piano_bench_var_storage_hinged_seat_lid
  - rec_0611_piano_bench_var_footrest_folding_rail

## Slots and candidates

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| support_frame | four_leg_apron | four square legs + four aprons + corner blocks + feet | rec_picturex_0611__piano_bench__002__png_40f64d0afe014cf084e43a5c586b96f2/rev_000001 | model.py:L88-L164 | accepted | four `leg_{i}` posts at ±0.226/±0.135, four aprons, `front_top_ledge`/`rear_top_ledge`, four `corner_block_{i}`, rubber `foot_{i}`; confirmed by `rec_0611_piano_bench_var_support_four_leg_apron/rev_000001` model.py:L94-L171 carrying the same skeleton onto the 001 storage host |
| support_frame | twin_pedestal | welded twin-pedestal H-frame with rectangular lift sleeves | rec_picturex_0611__piano_bench__003__png_9089cd9627714abeb4526ba1b9a84e99/rev_000001 | model.py:L36-L56, L101-L121 | accepted | two long feet, twin 0.052 columns at x=±0.195, upper/lower H rails, `sleeve_void` cut for the lift posts, four `foot_pad_*` |
| support_frame | folding_x_frame | crossed X side legs + top rails + centre stretcher | rec_0611_piano_bench_var_support_folding_x_frame/rev_000001 | model.py:L89-L216 | accepted | X-crossed leg pairs per side with top rails and a central stretcher; folding-furniture skeleton |
| seat_form | rectangle_padded | rectangular board + crowned upholstered cushion | rec_picturex_0611__piano_bench__002__png_40f64d0afe014cf084e43a5c586b96f2/rev_000001 | model.py:L21-L37, L193-L219 | accepted | `_padded_cushion` two-stage crowned box, `seat_board`, front/rear roller tracks on the underside |
| seat_form | round_stool | round seat pad + circular board on the pedestal host | rec_0611_piano_bench_var_seat_form_round_stool/rev_000001 | model.py:L59-L90, L138-L213 | accepted | circular seat board/cushion replacing the rectangular plan form — a real ③ primary-form change, not a proportion change |
| height_mechanism | side_handwheel_yoke | side handwheel + paired two-rail lifting yokes + prismatic seat | rec_picturex_0611__piano_bench__002__png_40f64d0afe014cf084e43a5c586b96f2/rev_000001 | model.py:L40-L67, L221-L239, L241-L281 | accepted | `wheel_turn` REVOLUTE +X, `arm_pivot_0/1` REVOLUTE ∓Y with `coupled_travel_rad`, `seat_lift` PRISMATIC +Z 0–0.055, `screw_pitch_m_per_rad` |
| height_mechanism | central_spindle | central threaded rod + bevel-gear housing + drive shaft | rec_0611_piano_bench_var_height_mechanism_central_spindle/rev_000001 | model.py:L40-L72, L173-L202, L251-L253, L270-L307 | accepted | `_central_spindle_geometry` rod + thread ridges + top collar, fixed spindle nut under the platform, `wheel_turn`/`spindle_turn` REVOLUTE + seat PRISMATIC |
| height_mechanism | twin_side_knobs | two opposed side knobs on one transverse screw | rec_0611_piano_bench_var_height_mechanism_twin_side_knobs/rev_000001 | model.py:L44-L78, L179-L205, L234-L251, L253-L290 | accepted | `_add_side_knob_visuals` per side, internal threaded spindle + lift nuts, `knob_turn_0`/`knob_turn_1` REVOLUTE ±X + shared seat PRISMATIC |
| height_mechanism | scissor_lift | crossed scissor arm pair + pivot mounts + guide rails | rec_0611_piano_bench_var_height_mechanism_scissor_lift/rev_000001 | model.py:L56-L90, L189-L208, L224-L229, L252-L297 | accepted | `_add_scissor_visuals` crossed bars + centre pivot pin, frame pivot mounts and lower-tip guide rails, `wheel_turn` REVOLUTE + two scissor REVOLUTE + seat PRISMATIC |
| storage | plain_apron | closed seat with no storage bay | rec_picturex_0611__piano_bench__002__png_40f64d0afe014cf084e43a5c586b96f2/rev_000001 | model.py:L193-L219 | accepted | 002's seat is a solid board + cushion with no cavity or lid; the common non-storage bench |
| storage | hinged_lid_box | rabbeted storage box + rear-hinged upholstered lid | rec_0611_piano_bench_var_storage_hinged_seat_lid/rev_000001 | model.py:L76-L134, L279-L344, L366-L421 | accepted (origin anchor `rec_picturex_0611__piano_bench__001.../rev_000001` model.py:L217-L315, L317-L372) | `_rabbeted_apron_shape` shell + cavity + rabbet shelf, felt lining, `lid_board`/`hinge_leaf`/`hinge_barrel`, `lift_to_lid` REVOLUTE 0–1.35 about −X |

## Recorded, not promoted to candidates

| Source | Observation | Treatment |
|---|---|---|
| rec_picturex_0611__piano_bench__001 (model.py:L26-L40 `_tapered_leg_shape`) | lofted tapered leg with chamfered foot | ⑤ proportion of the four-leg skeleton, not a separate topology → independent parameter `leg_taper_ratio` |
| rec_0611_piano_bench_var_seat_form_duet_rectangle (model.py:L214-L239) | wider duet seat on the same rectangular plan form | ⑤ proportion → independent parameter `seat_width_m`, not a candidate |
| rec_picturex_0611__piano_bench__001 (model.py:L49-L73 `_cushion_shape`, L346-L355 tuft buttons) | stitched channels + 4×3 button tufts | ④ surface decoration → seed-varied decoration on the cushion, contributes to neither core nor raw domain |
| rec_0611_piano_bench_var_footrest_folding_rail (model.py:L242-L266) | folding rail arm swapping the parent prismatic for a revolute | deferred: it changes the whole host lift topology rather than adding an independent component, so per the closed-combination rule it would have to become its own structural-family slot; recorded here so the decision is explicit rather than silent |

## Core mechanism entities, supports, joint axes and ranges

| Mechanism | Moving solid | Parent support / guide | Joint | Axis / origin | Range | Source |
|---|---|---|---|---|---|---|
| seat height lift | `seat` (board + cushion + underside tracks) | frame sleeves / lift nuts / yoke rollers depending on candidate | `seat_lift` PRISMATIC | +Z at the frame top plane | 0 → `lift_travel_m` (source 0.055–0.080) | 002 L251-L261, 003 L219-L233, 001 L300-L315 |
| side handwheel | `adjuster_wheel` disk + hub | frame apron face at the spindle axis | `wheel_turn` REVOLUTE | +X through the spindle centreline | 0 → 18 rad (002) | 002 L241-L250 |
| lifting yoke | `lift_arm_0/1` two-rail links + pivot pin + upper roller | frame pivot bosses; roller runs the seat underside track | `arm_pivot_0/1` REVOLUTE | ∓Y at the frame-top pivot line | 0 → 0.42 rad, coupled to `wheel_turn` | 002 L262-L281 |
| central spindle | `spindle` threaded rod + collar | fixed spindle nut below the frame platform; seat bracket above | `spindle_turn` REVOLUTE | +Z through the bench centreline | continuous drive range | central_spindle L281-L292 |
| twin side knobs | `adjuster_wheel`, `side_knob` | frame side aprons at the transverse screw axis | `knob_turn_0/1` REVOLUTE | ±X through the screw axis | 0 → 18 rad each | twin_side_knobs L253-L275 |
| scissor pair | `scissor_0/1` crossed bars + centre pin | frame pivot mounts below, lower-tip guide rails | `scissor_pivot_*` REVOLUTE | ±Y at the pivot mounts | 0 → 0.42 rad | scissor_lift L281-L297 |
| storage lid | `lid` board + cushion + hinge leaf | rabbet shelf on the storage box rim; hinge barrel on the rear edge | `lift_to_lid` REVOLUTE | −X along the rear long edge | 0 → 1.35 rad | storage_hinged_seat_lid L405-L421, 001 L357-L372 |

## Articulation invariant

Every reachable configuration carries **at least two movable joints**: one rotary
control from `height_mechanism` plus the `seat_lift` prismatic. `storage` adds a
third when `hinged_lid_box` is sampled. No candidate in any slot can produce a
rigid model, which is what preflight's `rigid_candidate_no_movable_joint` check
and the sweep/export `rigid_seed_no_movable_joint` gate now enforce mechanically.

## Combination notes (no compatibility gates)

- `round_stool` × `four_leg_apron` / `folding_x_frame`: the host derives a circular
  top frame ring from the seat radius instead of the rectangular ledge pair.
- `round_stool` × `hinged_lid_box`: the storage box and its lid are derived from the
  same seat plan profile, so a round seat yields a round box and a round lid.
- `twin_pedestal` × `side_handwheel_yoke` / `scissor_lift`: the pedestal columns
  derive an inner clearance well for the yoke/scissor sweep instead of the plain
  lift sleeve.
- `folding_x_frame` × any height mechanism: the X-frame emits a rigid top rail pair
  at the shared frame-top plane, so every mechanism mounts identically.
