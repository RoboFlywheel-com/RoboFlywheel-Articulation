# pictureX_0611_ergonomic_clamp_with_adjustable — SourceMap

source_map_schema: 1
export_category: pictureX_0611_ergonomic_clamp_with_adjustable
picture_category: 0611
picture_subcategory: ergonomic_clamp_with_adjustable
category_scope: A desk-edge C-clamp whose screw clamp carries one adjustable support structure ending in a concave forearm/wrist rest. The clamp jaw, screw spindle and self-aligning pressure shoe are always present; what varies is the adjustable structure between clamp and rest, and the rest head itself. A free-standing arm rest with no clamp, or a bare hand clamp with no support head, is out of scope.

sync_records:
  - rec_forearm_support_var_ball_socket_wrist
  - rec_forearm_support_var_deep_cradle_pad_20260714
  - rec_forearm_support_var_desk_edge_track_20260714
  - rec_forearm_support_var_gas_spring_arm
  - rec_forearm_support_var_linear_rail
  - rec_forearm_support_var_overcenter_cam_clamp_20260714
  - rec_forearm_support_var_parallel_linkage
  - rec_forearm_support_var_quick_release_pad_20260714
  - rec_forearm_support_var_ratchet_elbow
  - rec_forearm_support_var_rotary_column
  - rec_forearm_support_var_split_pad
  - rec_picturex_0611__ergonomic_clamp_with_adjustable__001__png__airflex_batch_20260710_0eb880af658b4bd19b563ba6e0817a3d

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_forearm_support_var_ball_socket_wrist/rev_000001 | reviewed | used | Base clamp plus plain rising arm; the distinct part is a two-axis ball/socket gimbal between wrist collar and pad. |
| rec_forearm_support_var_deep_cradle_pad_20260714/rev_000001 | reviewed | used | Reshapes the rest body itself into a deep U-section cradle with raised side bolsters and closed end walls; every mechanism above and below it is unchanged. |
| rec_forearm_support_var_desk_edge_track_20260714/rev_000001 | reviewed | used | Inserts a captured `carriage` on a bounded `carriage_slide` prismatic between the clamp frame and the arm base, so the whole support structure travels along the desk edge. |
| rec_forearm_support_var_overcenter_cam_clamp_20260714/rev_000001 | reviewed | used | Replaces the threaded spindle with an over-centre `cam_lever` and a `cam_follower` link that carries the pressure shoe; the clamp host is no longer a single screw mechanism. |
| rec_forearm_support_var_quick_release_pad_20260714/rev_000001 | reviewed | used | Splits the wrist-to-pad attachment into a `dovetail_carriage` on a bounded insertion prismatic plus a `cam_lock` lever, so the rest becomes removable. |
| rec_forearm_support_var_gas_spring_arm/rev_000001 | reviewed | used | Adds a real gas-spring strut (cylinder plus sliding piston) bracing the rising arm against the clamp frame. |
| rec_forearm_support_var_linear_rail/rev_000001 | reviewed | used | Adds a carriage sliding along a rail on top of the rising arm, giving reach adjustment ahead of the wrist. |
| rec_forearm_support_var_parallel_linkage/rev_000001 | reviewed | used | Replaces the single arm with a two-bar parallel linkage and a self-levelling carriage at its far end. |
| rec_forearm_support_var_ratchet_elbow/rev_000001 | reviewed | used | Clamp host and plain tilt saddle head are identical to the origin record; the distinct part is the toothed sector plus pivoting pawl at the elbow. |
| rec_forearm_support_var_rotary_column/rev_000001 | reviewed | used | Replaces the elbow with a vertical column, a collar sliding on it and a radial swing arm. |
| rec_forearm_support_var_split_pad/rev_000001 | reviewed | used | Distinct head: a yoke carrying a separate forearm pad and a separate wrist pad, each on its own tilt joint. |
| rec_picturex_0611__ergonomic_clamp_with_adjustable__001__png__airflex_batch_20260710_0eb880af658b4bd19b563ba6e0817a3d/rev_000001 | reviewed | used | Origin record for 001.png. Supplies the always-present clamp host and the two baseline candidates: a plain tapered rising arm and a single-tilt concave saddle head. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| support_linkage | plain_arm | single tapered rising arm on an elbow pivot | rec_picturex_0611__ergonomic_clamp_with_adjustable__001__png__airflex_batch_20260710_0eb880af658b4bd19b563ba6e0817a3d/rev_000001 | model.py:L61-L74, model.py:L377-L438 | structure+motion | `_arm_housing_shape` extrudes the tapered side profile of 001.png; one `arm_pitch` revolute at the clamp clevis carries the whole head. |
| support_linkage | ratchet_elbow | rising arm with a toothed sector and a pawl at the elbow | rec_forearm_support_var_ratchet_elbow/rev_000001 | model.py:L124-L186, model.py:L451-L543 | structure+motion | `_sector_teeth_shape` builds seven real asymmetric teeth on the frame clevis and `_pawl_shape` a bored pawl on its own `pawl_engage` revolute, so elevation is indexed rather than free. |
| support_linkage | gas_spring_arm | rising arm braced by a gas-spring strut | rec_forearm_support_var_gas_spring_arm/rev_000001 | model.py:L380-L552 | structure+motion | A separate `gas_spring_cylinder` on a `gas_spring_base_pivot` revolute at the frame plus a `gas_spring_piston` on a `gas_spring_extension` prismatic; two extra parts and a closed force path the plain arm does not have. |
| support_linkage | linear_rail | rising arm carrying a rail carriage for reach | rec_forearm_support_var_linear_rail/rev_000001 | model.py:L377-L571 | structure+motion | `rail_carriage` rides a `carriage_slide` prismatic along the top spine of the arm, so the head translates instead of only pitching. |
| support_linkage | parallel_linkage | two-bar parallel linkage with a levelling carriage | rec_forearm_support_var_parallel_linkage/rev_000001 | model.py:L59-L89, model.py:L444-L618 | structure | `_upper_link_shape`/`_lower_link_shape` give two distinct bars on `upper_link_pitch` and `lower_link_pitch`, closed by a `carriage` on `carriage_level`; the part tree is a linkage, not a single arm. |
| support_linkage | rotary_column | vertical column, sliding collar and radial swing arm | rec_forearm_support_var_rotary_column/rev_000001 | model.py:L62-L111, model.py:L422-L590 | structure+motion | `_column_post_shape`/`_sliding_collar_shape`/`_radial_arm_shape` replace the elbow with a `column_rotate` yaw axis, a `collar_slide` prismatic up the post and an `arm_swing` revolute. |
| pad_head | tilt_saddle | wrist collar plus one concave saddle on a single tilt | rec_picturex_0611__ergonomic_clamp_with_adjustable__001__png__airflex_batch_20260710_0eb880af658b4bd19b563ba6e0817a3d/rev_000001 | model.py:L103-L120, model.py:L510-L607 | structure | `_saddle_shell` intersects a clipped annulus into the genuinely concave trough of 001.png; head is wrist swivel plus one `forearm_pad_tilt`. |
| pad_head | ball_socket | wrist collar plus a two-axis ball gimbal under one saddle | rec_forearm_support_var_ball_socket_wrist/rev_000001 | model.py:L515-L681 | structure+motion | An extra `pad_gimbal` part splits the head into `pad_ball_pitch` and `pad_ball_roll`, so the saddle has two independent orientation axes. |
| pad_head | split_pad | yoke carrying separate forearm and wrist pads | rec_forearm_support_var_split_pad/rev_000001 | model.py:L563-L712 | structure+motion | `pad_yoke` on `yoke_tilt` carries two distinct contact bodies, `forearm_pad` and a smaller `wrist_pad`, each on its own tilt revolute. |
| pad_head | deep_cradle | wrist collar plus a deep contoured cradle on a single tilt | rec_forearm_support_var_deep_cradle_pad_20260714/rev_000001 | model.py:L103-L172, model.py:L605-L662 | structure | `_cradle_shell`/`_cradle_liner` extrude a closed U channel whose bolsters rise above the floor, and two `end_wall_i` close the channel: a different body family from the open saddle trough. |
| pad_head | quick_release | dovetail release carriage and cam lock under the rest | rec_forearm_support_var_quick_release_pad_20260714/rev_000001 | model.py:L619-L716 | structure+motion | `dovetail_carriage` on a bounded `dovetail_slide` prismatic plus a `cam_lock` on `cam_lock_flick` sit between wrist and pad, so the head gains two joints and two parts the fixed attachment has. |
| base_reach | fixed_mount | arm base pinned straight to the clamp frame | rec_picturex_0611__ergonomic_clamp_with_adjustable__001__png__airflex_batch_20260710_0eb880af658b4bd19b563ba6e0817a3d/rev_000001 | model.py:L189-L376 | structure | The clamp head carries the arm clevis directly: the elbow pin is the only interface between frame and support structure. |
| base_reach | edge_track | captured carriage on a desk-edge rail | rec_forearm_support_var_desk_edge_track_20260714/rev_000001 | model.py:L103-L115, model.py:L402-L446 | structure+motion | A separate `carriage` part rides a rail rooted on the fixed frame on a bounded `carriage_slide` prismatic, and the arm base is pinned to that carriage instead of the frame. |
| clamp_actuation | screw_spindle | threaded spindle and nut on the guided jaw | rec_picturex_0611__ergonomic_clamp_with_adjustable__001__png__airflex_batch_20260710_0eb880af658b4bd19b563ba6e0817a3d/rev_000001 | model.py:L189-L376 | structure+motion | The jaw carries a thread nut and a `spindle` on a CONTINUOUS `spindle_turn`, with the pressure shoe pivoting on the spindle head. |
| clamp_actuation | overcenter_cam | over-centre cam lever and follower link | rec_forearm_support_var_overcenter_cam_clamp_20260714/rev_000001 | model.py:L100-L149, model.py:L334-L458 | structure+motion | `cam_lever` on `cam_lever_swing` and `cam_follower` on `follower_pivot` replace the spindle entirely, and the shoe is carried by the follower rather than by a screw. |

## Rejected and reference notes

- No record is a duplicate or category drift: every one of the twelve active sources is used.
- The folded C-frame, the guided jaw, the trigger and the release lever are identical across all twelve
  records, so they stay a single parameterised host; the origin record's `model.py:L189-L376` is the
  reviewed reference for them. The clamp actuation is **not** shared: the 20260714 cam fork replaces the
  spindle with a lever-and-follower train, so it is its own slot.
- The reach interface is likewise its own slot: eleven records pin the arm base straight to the frame
  head, while the desk-edge-track fork interposes a real sliding carriage.
- Wing-nut and tommy-bar handle styles differ only in a small handle solid and do not change the part
  tree, joint set or assembly interface, so they are derived detail, not candidates.
