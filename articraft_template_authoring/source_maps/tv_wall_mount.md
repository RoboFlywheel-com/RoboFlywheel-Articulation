# tv_wall_mount SourceMap

export_category: tv_wall_mount

sync_records:
  - rec_picturex_0611__tv_wall_mount__001__png_256af3716b30482fa15f69af5e2edcd4
  - rec_picturex_0611__tv_wall_mount__002__png_742289b568674f468cc34207a1ecaffd
  - rec_picturex_0611__tv_wall_mount__003__png_d5fa4b15696c407b9ae0e136f07b9080
  - rec_picturex_0611__tv_wall_mount__004__png_62c79a78a7ac4b8681822a3374714d9f
  - rec_0611_tv_wall_mount_var_arm_topology_articulating_frame
  - rec_0611_tv_wall_mount_var_arm_topology_dual_arm_full_motion
  - rec_0611_tv_wall_mount_var_arm_topology_fixed_low_profile_plate
  - rec_0611_tv_wall_mount_var_arm_topology_single_arm_full_motion
  - rec_0611_tv_wall_mount_var_arm_topology_tilt_only_bracket
  - rec_0611_tv_wall_mount_var_height_adjustment_counterweighted_lift
  - rec_0611_tv_wall_mount_var_height_adjustment_gas_spring_vertical
  - rec_0611_tv_wall_mount_var_height_adjustment_toothed_lift_track
  - rec_0611_tv_wall_mount_var_lock_pull_cord_screen_latch
  - rec_0611_tv_wall_mount_var_screen_motion_portrait_roll_head
  - rec_0611_tv_wall_mount_var_screen_motion_push_pull_depth_carriage
  - rec_0611_tv_wall_mount_var_screen_motion_tilt_swivel_head
  - rec_0611_tv_wall_mount_var_vesa_interface_crossed_rails
  - rec_0611_tv_wall_mount_var_vesa_interface_four_independent_arms
  - rec_0611_tv_wall_mount_var_vesa_interface_sliding_twin_rails
  - rec_0611_tv_wall_mount_var_vesa_interface_universal_plate

## Source families

The four pictureX roots are the raw geometry families.  All use `rev_000001`.

| family | raw record/revision | exact model.py spans | source evidence |
|---|---|---|---|
| picturex_001 extended full-motion | rec_picturex_0611__tv_wall_mount__001__png_256af3716b30482fa15f69af5e2edcd4/rev_000001 | model.py:L83-L122, model.py:L125-L159, model.py:L162-L185, model.py:L188-L250, model.py:L253-L298, model.py:L301-L557 | sleeve/clevis, two arms, tilt barrel, bow-tie plate, diagonal rails |
| picturex_002 compact single-arm | rec_picturex_0611__tv_wall_mount__002__png_742289b568674f468cc34207a1ecaffd/rev_000001 | model.py:L31-L55, model.py:L58-L116, model.py:L119-L610 | tapered arm, sleeve pivots, butterfly VESA plate, tilt yoke |
| picturex_003 dual-arm cast/pressed | rec_picturex_0611__tv_wall_mount__003__png_d5fa4b15696c407b9ae0e136f07b9080/rev_000001 | model.py:L27-L61, model.py:L64-L112, model.py:L115-L179, model.py:L182-L404 | relieved links, pivot bosses, folded returns, H-shaped pressing |
| picturex_004 open articulating frame | rec_picturex_0611__tv_wall_mount__004__png_62c79a78a7ac4b8681822a3374714d9f/rev_000001 | model.py:L49-L70, model.py:L73-L104, model.py:L107-L143, model.py:L146-L164, model.py:L167-L450 | stamped wall frame, cheek arms, cross ties, pierced head, hooked rails |

## Accepted variant candidates

The rows below are the accepted `variant_intent.json` deltas.  Spans are exact function
spans from each cited revision's `model.py`; the final file re-expresses the structures as
ordinary functions and does not import these records.

| slot | candidate | record/revision | model.py:Lx-Ly | diversity axis | source type | status | key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| arm_topology | articulating_frame | rec_0611_tv_wall_mount_var_arm_topology_articulating_frame/rev_000001 | model.py:L49-L70, model.py:L73-L114, model.py:L117-L126, model.py:L129-L133, model.py:L189-L472 | ② | structural component | accepted | triangulated rails, alternating braces, wall/elbow/tilt/VESA interfaces |
| arm_topology | dual_arm_full_motion | rec_0611_tv_wall_mount_var_arm_topology_dual_arm_full_motion/rev_000001 | model.py:L27-L77, model.py:L80-L128, model.py:L131-L143, model.py:L146-L171, model.py:L203-L431 | ② | structural component | accepted | relieved cast links and pivot bosses |
| arm_topology | fixed_low_profile_plate | rec_0611_tv_wall_mount_var_arm_topology_fixed_low_profile_plate/rev_000001 | model.py:L49-L72, model.py:L75-L91, model.py:L94-L105, model.py:L108-L112, model.py:L115-L144, model.py:L168-L451 | ② | structural component | accepted | short cheeks, tilt head, slots, captured rail hardware |
| arm_topology | single_arm_full_motion | rec_0611_tv_wall_mount_var_arm_topology_single_arm_full_motion/rev_000001 | model.py:L31-L55, model.py:L58-L116, model.py:L119-L611 | ② | structural component | accepted | enclosed tapered arm and sleeve pivots |
| arm_topology | tilt_only_bracket | rec_0611_tv_wall_mount_var_arm_topology_tilt_only_bracket/rev_000001 | model.py:L83-L122, model.py:L125-L159, model.py:L162-L197, model.py:L200-L223, model.py:L226-L237, model.py:L240-L254, model.py:L257-L307, model.py:L310-L341, model.py:L344-L389, model.py:L392-L649 | ② | structural component | accepted | compact bracket and substantial tilt yoke |
| height_adjustment | counterweighted_lift | rec_0611_tv_wall_mount_var_height_adjustment_counterweighted_lift/rev_000001 | model.py:L73-L92, model.py:L95-L104, model.py:L107-L111, model.py:L114-L143, model.py:L167-L484 | ② | mechanism component | accepted | counterweight housing and slotted lift envelope |
| height_adjustment | gas_spring_vertical_track | rec_0611_tv_wall_mount_var_height_adjustment_gas_spring_vertical/rev_000001 | model.py:L73-L92, model.py:L95-L104, model.py:L107-L111, model.py:L114-L143, model.py:L146-L172, model.py:L175-L468 | ② | mechanism component | accepted | guide rail, gas-spring barrel, running clearance |
| height_adjustment | toothed_lift_track | rec_0611_tv_wall_mount_var_height_adjustment_toothed_lift_track/rev_000001 | model.py:L73-L92, model.py:L95-L104, model.py:L107-L111, model.py:L114-L143, model.py:L146-L164, model.py:L167-L172, model.py:L175-L189, model.py:L192-L486 | ② | mechanism component | accepted | rack teeth, pinion, guided lift block |
| screen_motion | portrait_roll_head | rec_0611_tv_wall_mount_var_screen_motion_portrait_roll_head/rev_000001 | model.py:L188-L224, model.py:L227-L241, model.py:L244-L275, model.py:L278-L323, model.py:L326-L587 | ② | motion component | accepted | roll hub, portrait head, diagonal carrier rails |
| screen_motion | push_pull_depth_carriage | rec_0611_tv_wall_mount_var_screen_motion_push_pull_depth_carriage/rev_000001 | model.py:L192-L193, model.py:L196-L226, model.py:L229-L243, model.py:L246-L279, model.py:L282-L313, model.py:L316-L361, model.py:L364-L634 | ② | motion component | accepted | sleeve-guided depth carriage and swivel barrel |
| screen_motion | tilt_swivel_head | rec_0611_tv_wall_mount_var_screen_motion_tilt_swivel_head/rev_000001 | model.py:L188-L234, model.py:L237-L251, model.py:L254-L285, model.py:L288-L333, model.py:L336-L593 | ② | motion component | accepted | second head swivel axis and forked tilt carriage |
| vesa_interface | bow_tie_slotted_arms | rec_picturex_0611__tv_wall_mount__001__png_256af3716b30482fa15f69af5e2edcd4/rev_000001 | model.py:L188-L250, model.py:L253-L298 | ② | interface component | accepted | source bow-tie carrier with four diagonal slotted arms |
| vesa_interface | butterfly_plate | rec_picturex_0611__tv_wall_mount__002__png_742289b568674f468cc34207a1ecaffd/rev_000001 | model.py:L119-L610 | ② | interface component | accepted | compact four-lobed butterfly pressing and center bridge |
| vesa_interface | crossed_rails | rec_0611_tv_wall_mount_var_vesa_interface_crossed_rails/rev_000001 | model.py:L188-L199, model.py:L202-L216, model.py:L219-L250, model.py:L253-L334, model.py:L337-L593 | ② | interface component | accepted | crossed formed rails and pierced center plate |
| vesa_interface | four_independent_arms | rec_0611_tv_wall_mount_var_vesa_interface_four_independent_arms/rev_000001 | model.py:L27-L61, model.py:L64-L112, model.py:L115-L122, model.py:L125-L150, model.py:L153-L162, model.py:L165-L205, model.py:L208-L487 | ② | interface component | accepted | four independent load paths and end bosses |
| vesa_interface | h_bracket_plate | rec_picturex_0611__tv_wall_mount__003__png_d5fa4b15696c407b9ae0e136f07b9080/rev_000001 | model.py:L115-L179, model.py:L182-L404 | ② | interface component | accepted | source H-frame pressing with twin pierced uprights |
| vesa_interface | sliding_twin_rails | rec_picturex_0611__tv_wall_mount__004__png_62c79a78a7ac4b8681822a3374714d9f/rev_000001 | model.py:L107-L143, model.py:L146-L164, model.py:L167-L450 | ② | interface component | accepted | wide relieved carrier and two independently X-sliding vertical slotted rails |
| vesa_interface | universal_plate | rec_0611_tv_wall_mount_var_vesa_interface_universal_plate/rev_000001 | model.py:L31-L55, model.py:L58-L121, model.py:L124-L615 | ② | interface component | accepted | stamped 75/100 mm plate and outer slots |
| lock | pull_cord_screen_latch | rec_0611_tv_wall_mount_var_lock_pull_cord_screen_latch/rev_000001 | model.py:L151-L177, model.py:L180-L213, model.py:L216-L438 | ② | lock component | rejected | exposed latch body and pull ring obscure the VESA outline; it is not required by the support interface |

## Authoring decisions

- All reviewed variants have `multiplicity.applies=false`; accepted variants are structural or
  functional evidence, not copied N objects.  This category has no honest runtime N: the source-004
  VESA family always uses exactly two installation rails, so it is not counted as multiplicity.
- Whole source parent trees are not cross-combined.  The four component slots share a common wall,
  arm, height-carrier and head boundary; local transition shoulders, yokes, apertures and
  support spans make every declared Cartesian combination buildable without a gate.
- The wall host has no fixed center crossbar in the carriage sweep.  A narrow moving
  vertical carriage captures the upper/lower perimeter rails and translates left/right;
  the arm wall-swivel is mounted on that carriage rather than fixed to the wall plate.
- Height adjustment is an explicit fixed-guide/moving-saddle chain.  The front arm carries
  a twin C-channel fixed track, while guide rollers constrain one Z-prismatic saddle that
  carries the complete screen head.  End ties remain outside the swept shoe envelope; the
  counterweight, gas spring and rack/pinion sit behind or outside the running lane and are
  split according to which side of the joint they physically belong to.
- The screen-side chain stays visually sparse: a compact yoke/carriage directly supports
  the selected VESA plate instead of adding a second decorative backplate and rail layer.
  Portrait roll, push-pull depth and tilt-swivel heads retain their distinct source
  mechanisms (roll hub, twin sleeves/rods, and bored swivel cartridge).
- The source-004 VESA rails remain two independent parts with X-prismatic adjustment joints.
  Their pierced webs sit visibly in front of the carrier, while shallow rear hooks engage
  explicit upper/lower rolled tracks; their vertical orientation does not imply vertical travel.
- Source tests informed the new author tests but are not copied into runtime.
- The exposed pull-cord latch is intentionally not published as a slot: it does not carry the
  display and visually disrupts both the open-arm and universal-plate VESA families.  The two
  tilt-lock knobs remain the only continuous lock-control joints.
