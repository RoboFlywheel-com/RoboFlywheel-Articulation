# 0611 / ball_transfer_unit_with_spring_loaded_ball — template source map
status: converged — GATE P1 machine-pass; human variant inspection confirmed 2026-07-12
pattern: mixed (linear_chain housing->carrier->roll_frame->load_ball + multiplicity support-ball ring)
parents: rec_picturex_0611__ball_transfer_unit_with_spring_loaded_ball__001__png__airflex_batch_20260710_a5cb276866604f55b526fe1f5f1ce1a1 (picture/0611/ball_transfer_unit_with_spring_loaded_ball/001.png)
canonical_baselines: none
underfilled_reason: mechanically simple part — one load ball, one housing, one spring stack. Real structural vocabulary is dominated by the mounting interface plus a few body-form / mechanism / orientation variants. 11 candidate anchors + 1 probe is honest coverage; not padded toward the upper budget.

## subcategory_contract
```yaml
subcategory_contract:
  category: 0611
  subcategory: ball_transfer_unit_with_spring_loaded_ball
  core_identity: a housing/cup that captures one large load-bearing ball which rolls freely (multi-axis) on a support race, spring-loaded or rigidly seated, with a mounting interface to a machine/table
  must_keep:
    - single large protruding load ball as the primary transfer element
    - free multi-axis rolling articulation of that load ball (continuous joints)
    - a closed housing/cup with a retainer that captures the ball
    - a mounting interface to ground the unit
  must_not_become:
    - swivel/rigid caster (no fork, wheel, or swivel yoke)
    - plain ball/thrust bearing (no housingless raceway of equal balls without a single protruding load ball)
    - trackball / decorative ball ornament / gravity ball drop
  image_evidence:
    - tall polished steel cylinder with a broad shallow top flange (shoulder + flange)
    - single large mirror-finish load ball exposed at the top crown inside a pressed retaining cup
    - smooth cylindrical body, NO external bolt holes (press-fit / drop-in body)
  parent_evidence:
    - parts housing, retainer, compression_spring, spring_carrier, roll_frame, load_ball
    - helpers _housing_geometry, _retainer_geometry, _carrier_geometry
    - joints housing_to_carrier (PRISMATIC 3mm), carrier_to_roll_frame + roll_frame_to_ball (CONTINUOUS, 2-axis roll), housing_to_retainer/housing_to_spring (FIXED)
    - meta: smooth cylindrical press-fit body, no flange bolt holes visible
```

## Slot Candidates
| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| support_or_base (mount) | press-fit cylindrical body | ① | origin_anchor | parent 001.png / _housing_geometry | housing | converged (parent) |
| support_or_base (mount) | bolt-down mounting flange (ring of holes) | ① | forked_anchor | var_flange_bolt_mount | housing (_housing_geometry) | converged |
| support_or_base (mount) | threaded stud/shank mount | ① | forked_anchor | var_threaded_stud_mount | housing | converged |
| support_or_base (mount) | side / L-bracket mount | ① | forked_anchor | var_side_bracket_mount | housing | converged |
| support_or_base (mount) | machined square base plate + corner holes | ① | forked_anchor | var_machined_square_base | housing | converged |
| body_form | stepped round cylinder | ③ | origin_anchor | parent | housing | converged (parent) |
| body_form | hexagonal (wrench-flats) body | ③ | forked_anchor | var_hex_body | housing (_housing_geometry) | converged |
| body_form | shallow wide flanged cup (low-profile) | ③ | forked_anchor | var_shallow_wide_cup | housing | converged |
| opening_or_motion (preload) | spring-loaded prismatic carrier | ② | origin_anchor | parent housing_to_carrier PRISMATIC | spring_carrier, compression_spring | converged (parent) |
| opening_or_motion (preload) | rigid non-spring seated carrier | ② | forked_anchor | var_rigid_nonspring_seat | housing_to_carrier FIXED | converged |
| skeleton (orientation) | ball-up (parent) | ① | origin_anchor | parent | full stack | converged (parent) |
| skeleton (orientation) | ball-down / inverted top-mount | ① | forked_anchor | var_ball_down_orientation | full stack, inverted origins | converged |
| multiplicity (support balls) | support-ball nest N=8 | N | forked_anchor | var_support_balls_n8 | support_ball_{i:02d} fixed to spring_carrier | converged |
| multiplicity (support balls) | support-ball nest N=12 | N | forked_anchor | var_support_balls_n12 | support_ball_{i:02d} | converged |
| multiplicity (support balls) | support-ball nest N=16 | N | forked_anchor | var_support_balls_n16 | support_ball_{i:02d} | converged |

## Multiplicity / Copy Logic
- count_param: support_ball_count (N)
- N samples: 8, 12, 16 (source-backed via forked_anchor; parent represents the race as a single hidden bearing_core)
- suggested N_range: 6–20 single ring (below ~6 unrealistic bed; above ~18 crowds one ring and would push toward a second row = separate topology)
- copied object: one small support-ball Sphere (~0.0016–0.0018 m radius)
- naming: support_ball_{i:02d}
- placement: single radial ring at fixed pitch radius in the spring_carrier lower race, angle = 2*pi*i/N
- joint policy: each support ball FIXED to spring_carrier (captive bed); the main load_ball keeps its two CONTINUOUS rolling joints as the real non-fixed articulation
- note: flange bolt-hole count is a second latent multiplicity, but it requires the flange candidate first, so it is gated (see Compatibility Probes / Blocked), not a standalone N sample here.

## Six-Axis Diversity Record
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / structural topology | source-backed (candidate) | mount interface {press-fit, bolt flange, threaded stud, side bracket, machined square base}; orientation {ball-up, ball-down} |
| ② joint / mechanism type | source-backed (candidate) | preload {spring-loaded PRISMATIC (parent), rigid FIXED seat}; core 2-axis CONTINUOUS rolling kept in all |
| ③ primary form family | source-backed (candidate) | housing envelope {stepped round cylinder (parent), hexagonal prism, shallow wide cup} |
| ④ surface decoration | record_only | polished vs satin steel banding, pressed retainer seam; no dedicated fork (host-conformal only) |
| ⑤ proportion / size / travel | record_only | overall ~0.056 x 0.056 x 0.0655 m; load ball dia 0.025 m; prismatic travel 0.003 m; heavy-duty vs mini scale rides along only with shallow_wide_cup envelope |
| ⑥ material / palette / finish | record_only | satin_steel, polished_steel, bearing_steel, dark_steel; alt finishes (zinc, stainless, nylon ball) recordable, not forked |

## Compatibility Probes
| probe | record_id | combined axes | risk tested | result |
|---|---|---|---|---|
| flange-mount + ball-down | rec_ball_transfer_unit_with_spring_loaded_ball_var_probe_flangemount_balldown | ① mount x ① orientation | top bolt flange vs inverted retainer/ball crown clearance; bolt ring vs mounting plane clash | converged |

## Blocked / Excluded
- roller-based transfer (cylindrical roller instead of ball): drifts toward conveyor roller category — excluded.
- multiple large load balls in one housing: not a real BTU form; the single protruding load ball is category-defining — excluded.
- flange bolt-hole count as a standalone N axis: gated — needs the flange candidate first, so it would bundle two axes on an ordinary fork; record as gated multiplicity, revisit off the flange_bolt_mount forked_anchor if needed.
- static-only (no rolling) ball dome: violates must_keep rolling articulation — excluded.

## GATE P1 Verification (machine)
- normal variants forked & accepted: 11 (all exit 0)
- compatibility probe-only variants: 1 (`rec_ball_transfer_unit_with_spring_loaded_ball_var_probe_flangemount_balldown`)
- total synced source records after confirmation: 13 (1 origin + 11 normal variants + 1 probe-only variant)
- compile: ALL success
- articulation: every variant has >=1 non-fixed joint
- promotion: all workbench-only (dataset not in collections)
- binding: all bound to picture_category=0611 / picture_subcategory=ball_transfer_unit_with_spring_loaded_ball, parent_record_id set (verified in data/index/subcat/0611__ball_transfer_unit_with_spring_loaded_ball.jsonl)
- run_tests: every variant exports run_tests with axis-specific ctx.check/expect assertions (9-36 checks each)
- N-multiplicity axes verified to realize distinct counts (loop-emitted, stable indexed naming)
- human variant inspection: confirmed by user on 2026-07-12; downstream sync/spec/template stages may proceed.
