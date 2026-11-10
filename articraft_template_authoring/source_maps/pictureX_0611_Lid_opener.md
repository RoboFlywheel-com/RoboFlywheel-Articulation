# pictureX_0611 Lid opener — SourceMap

export_category: pictureX_0611_Lid_opener

Authoritative records live under `data/records`. All four accepted seeds are hand-held manual
jar/can lid openers built as a plier-action tool: a fixed stamped stainless **frame** carries the
working head, one molded handle grip and the main pivot pin, and a moving stamped **lever**
carries the second grip and the moving jaw, swinging about a single Z pivot that opens and closes
the gripping head over a lid rim. The four records agree on this backbone and differ on four
genuinely separable structural axes — the **working head mechanism / joint topology**, the
**working lid mouth** cut into (or hooked onto) the carrier nose, the **handle grip
construction**, and the **carrier reinforcement layer**. These become four independent slots whose
full cartesian product (4 × 4 × 2 × 2 = 64) is buildable: head hardware occupies the mid-head
region, the mouth occupies the nose beyond it, the grips occupy the handles and the reinforcement
is a second sheet layer under the cheek, so no two axes contend for the same host region.

sync_records:
  - rec_picturex_0611__lid_opener__001__png_3629ffb09bed420e8847dce28465922d
  - rec_use-the-attached-reference-image-as-the-primary-_20260712_094150_036146_45e44262
  - rec_use-the-attached-reference-image-as-the-primary-_20260712_094150_039038_45e44262
  - rec_use-the-attached-reference-image-as-the-primary-_20260712_094513_583310_45e44262

## Slot `head` — working head mechanism (owns the rotary joint graph)

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| head | rotary_crank | crank-driven multi-shaft rotary head | rec_picturex_0611__lid_opener__001__png_3629ffb09bed420e8847dce28465922d/rev_000001 | model.py:L258-L372 (cutter+axle L269-292; feed wheel+axle L295-318; drive gear+crank+knob L321-372) | accepted | Three spinning shafts on the stamped cheek PLUS the plier pivot — a spur drive gear turned by a short crank and molded knob, a serrated feed wheel, and a hardened cutter disc. The only record with a hand crank or more than one rotary axis. 3 rotors / 3 CONTINUOUS joints. |
| head | feed_gear | single continuous serrated feed gear, static cutter | rec_use-the-attached-reference-image-as-the-primary-_20260712_094150_036146_45e44262/rev_000001 | model.py:L167-L184 (cutter bracket + cutting wheel + screw), L261-L291 (`feed_gear` part + `gear_rotation` CONTINUOUS) | accepted | Exactly ONE continuous rotor (serrated feed gear) on the frame; the sharpened cutting wheel, its bracket and screw are static frame visuals. Distinct joint topology: 1 revolute + 1 continuous. |
| head | lever_cutter | cutting wheel rides the moving lever | rec_use-the-attached-reference-image-as-the-primary-_20260712_094150_039038_45e44262/rev_000001 | model.py:L180-L195 (static drive_gear + feed_wheel on `body`), L305-L318 (`cutting_wheel` + axle are visuals of the MOVING `upper_handle`) | accepted | Zero rotors: the sharpened cutter is parented to the moving lever and swings toward the frame's fixed feed wheel as the handles close. Reduction + feed gears are static. Genuine part-tree difference (cutter on lever, not frame). |
| head | guarded_head | folded U guard over an all-static head | rec_use-the-attached-reference-image-as-the-primary-_20260712_094513_583310_45e44262/rev_000001 | model.py:L138-L198 (static drive/feed gears L138-141; cutting_disc + rivet L163-174; guide_roller L175-180; guard_post / guard_bridge / guard_post_2 L181-198) | accepted | Zero rotors and a distinctive fixed folded U guard (two posts + a bridge) over the static cutting disc, plus a guide roller. Silhouette and part tree differ from `lever_cutter` even though both add no joint. |

Head distinction summary (joint-graph / part-tree, not material): rotor counts 3 / 1 / 0 / 0, and
the two zero-rotor families differ by which half carries the cutter and by the folded-guard members.

## Slot `mouth` — the working lid opening on the carrier nose

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| mouth | crescent | open crescent throat with a squared exit | ...094513_583310/rev_000001 | model.py:L91-L102 (circle ∪ `mouth_exit` box cut from the carrier), L201-L206 (`jaw_pad`) | accepted | The carrier's working mouth is cut as an open crescent with a squared exit, leaving two jaw tips; a rubber jaw pad guards a painted lid rim. |
| mouth | round_throat | closed circular throat bored through the nose | ...094150_039038/rev_000001 | model.py:L121-L129 (`throat` cut), L198-L208 (`nose_rivet`) | accepted | "Functional throat opening at the nose instead of a solid symbolic head": a closed bore, topologically different from an open mouth (the carrier becomes an extrusion-with-hole). |
| mouth | notched_cheek | notch bitten out of the lower cheek edge | rec_picturex_0611__lid_opener__001__png_...922d/rev_000001 | model.py:L143-L165 (`notch=(-47.0, -3.0, 10.5)` at L159) | accepted | The working bite is a notch taken out of the stamped cheek EDGE, not an opening in the nose — a different silhouette and a different lid-engagement geometry. |
| mouth | hooked_jaw | added hooked anti-slip claw, solid nose | ...094150_036146/rev_000001 | model.py:L154-L172 (`hooked_jaw` profile + `cutter_bracket` support) | accepted | The nose stays solid and the gripping geometry is an ADDED hook claw profile with a support block: an extra part-tree member instead of a cut. |

## Slot `grip` — handle grip construction (applied to both halves)

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| grip | lofted_oval | curved multi-section lofted oval grips | rec_picturex_0611__lid_opener__001__png_...922d/rev_000001 | model.py:L37-L58 (`_handle_loft` ellipse-section loft), L97-L119 (UPPER/LOWER section tables), grip visuals L178-182 / L253-257 | accepted | Both handles are smooth ovals lofted from varying ellipse sections along a curved centreline (palm swell, tapered rounded ends). A genuinely 3D silhouette. |
| grip | stamped_molded | flat extruded molded plate grips with inlay | ...094150_036146/rev_000001 | model.py:L111-L124, L214-L234; corroborated by 094150_039038 model.py:L149-L158 / L274-L303 and 094513_583310 model.py:L106-L128 / L243-L265 | accepted | Closed outline extruded to a constant thickness with a thin raised soft-touch inlay/spine. Shared by the three plier records; a different grip silhouette from the lofted ovals. |

## Slot `spine` — stamped carrier reinforcement layer

| Slot | Candidate | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|
| spine | folded_bracket | folded U bracket under the cheek | rec_picturex_0611__lid_opener__001__png_...922d/rev_000001 | model.py:L183-L209 (`folded_bracket` = web + two folded legs) | accepted | "Pivot pin and a folded rear bracket physically tie the sheet layers together": a three-member folded section under the cheek. |
| spine | weld_backplate | spot-welded flat mechanism backplate | ...094150_036146/rev_000001 | model.py:L088-L096 (`mechanism_backplate`) | accepted | "A second stamped reinforcement is spot-welded behind the working head ... it provides the real support path from the cheek plate to the jaw and both axles": one flat plate (+ rivet) instead of a folded section. |

## Parameters and derivations

- `head_span_m` (independent, candidate-local on each `head` candidate; 0.048–0.072 m): pivot-to-mouth
  span. Derives the mouth centre, the carrier nose tip, every gear station and radius, the guard
  span and the head clearance envelope.
- `mouth_size_m` (independent, candidate-local on each `mouth` candidate; 0.016–0.026 m): nominal
  working opening. Derives the crescent arc radius, the bored throat radius, the notch width/depth
  and the hook claw scale.
- `grip_length_m` (independent, candidate-local on each `grip` candidate; 0.100–0.150 m): length of
  each molded handle grip. Derives the grip outline / loft span and both stamped tang reaches.
- Derived in `resolve_config`: `mouth_x = -(head_span_m + 0.012)`, `nose_tip_x = mouth_x - 0.020`,
  the three rotor stations and radii, `frame_tang_reach`, `lever_tang_reach`, `rotor_count`.

## Category identity and motion

- Exactly one fixed `frame` part (role `opener_frame`) and one moving `lever` part (role
  `opener_lever`), joined by one bounded Z-axis `handle_pivot` REVOLUTE, range -0.30 … +0.26 rad.
  Measured: a NEGATIVE angle squeezes the handles together and (the head being on the far side of
  the pivot) drives the moving jaw finger toward the carrier's fixed upper lip.
- `rotary_crank` adds three CONTINUOUS Z rotors, `feed_gear` one; `lever_cutter` and `guarded_head`
  add none. Every rotational joint is built with `mate_axes` on the true shaft/pin axis and
  registered with `register_interface_mate` (TEMPLATE_DOMAIN contract).

## Mechanism entities, supports, axes, ranges, envelopes

- Layering contract: every frame element except the pivot pin ends at or below z = 0.0100 and every
  lever element starts at or above z = 0.0110, so the two plier halves only ever meet at the pivot.
- The pivot pin top presses 0.6 mm into the lever plate's underside and every rotor hub presses
  0.6 mm into the carrier's top face: real seated capture (contact_tol is 1e-6, so tangency would
  read as a floating island) whose world-AABB lap on Z stays under the collision tolerance. No
  overlap allowance of any kind is declared.
- The three rotor stations keep a ≥ 0.10 × head_span radial gap at every head_span, and the crank
  sweep envelope (1.57 × drive gear radius) is derived to clear the feed wheel at every angle.

## Rejected decompositions / notes

- No prismatic/screw jaw exists in any source — all four use a lever-revolute plier action, so the
  "adjustable jaw" is the real bounded lever pivot, not an invented screw.
- Independent `frame_topology × cutter_location × gear_count` micro-slots are rejected: those
  differences are coherent per-record mechanisms and belong in one `head` structural slot.
- Grip inlays/spines, maker badges and warning plaques are host-conformal decoration and are emitted
  with their grip candidate rather than becoming a slot.
- No multiplicity (N): none of the records repeats a structural unit a variable number of times.
