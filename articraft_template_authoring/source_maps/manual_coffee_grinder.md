# Manual coffee grinder — SourceMap

export_category: manual_coffee_grinder

Authoritative records are under
`<ARTI_SKILL_ROOT>/articraft_data/data/records/<record>/revisions/rev_000001/model.py`.
All three source images and all twelve source models were inspected again after deleting the
previous template and design artifacts. The loose silver burr beside source image 002 is a prop
and is intentionally omitted.

The previous decomposition was mechanically false: `catch` was an independent slot, so a drawer
could be selected behind a solid cylindrical body with no receiving opening. `TemplateDomain`
has no compatibility gates, therefore body, receiver topology, cavity/socket, rails and catch
motion are now one `structural_family` candidate. Every drawer family cuts the host before the
drawer is emitted; every cup family provides a matching open socket or lower seam. Drive,
closure and mounting are retained as independent slots only because each can be adapted locally
at a published bearing, rim or ground interface.

sync_records:
  - rec_picturex_0611__manual_coffee_grinder__001__png_c35ee4d5322147f7b86183d272e2207d
  - rec_picturex_0611__manual_coffee_grinder__002__png_a48c5a9133da44bb9ecf4fac20b35002
  - rec_picturex_0611__manual_coffee_grinder__003__png_3e1dc714e9524c71a7bac3f672f2b4cf
  - rec_0611_manual_coffee_grinder_var_body_form_square_wood_box
  - rec_0611_manual_coffee_grinder_var_body_form_slim_travel_cylinder
  - rec_0611_manual_coffee_grinder_var_catch_pull_out_drawer
  - rec_0611_manual_coffee_grinder_var_catch_threaded_cup
  - rec_0611_manual_coffee_grinder_var_drive_folding_top_crank
  - rec_0611_manual_coffee_grinder_var_drive_side_crank
  - rec_0611_manual_coffee_grinder_var_hopper_hinged_covered_hopper
  - rec_0611_manual_coffee_grinder_var_hopper_open_bowl
  - rec_0611_manual_coffee_grinder_var_mount_table_clamp

## Slot A — `structural_family`

This slot owns the fixed housing, source-specific hopper silhouette, burr chamber, receiver
opening, moving grounds receiver when present, and that receiver's joint. It publishes
`drive_axis`, `hopper_rim` and `ground_seat`.

| Slot | Candidate | Diversity axis | Component type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|---|
| structural_family | turned_wood_integrated | ① turned silhouette | integrated wooden body + open bowl | rec_picturex_0611__manual_coffee_grinder__001__png_c35ee4d5322147f7b86183d272e2207d/rev_000001 | model.py:L24-L64; model.py:L65-L404 | accepted source-backed | Turned 14-station wood profile, two dark beads, layered cast mount, genuinely thin-walled wide bowl, annular feed passage, long hollow bearing, spring stack and two-post frame. Grounds body is integrated; no fake moving catch is added. |
| structural_family | ribbed_travel_cup | ① travel silhouette | ribbed cylindrical housing + removable cup | rec_picturex_0611__manual_coffee_grinder__002__png_a48c5a9133da44bb9ecf4fac20b35002/rev_000001 | model.py:L20-L147; model.py:L148-L397 | accepted source-backed | Hollow 28.8 mm-radius shell with 43 dense ribs, annular internal floor/feed opening, lower burr carrier and genuinely open tapered grounds cup. Cup withdraws downward on a real Z prismatic seam. |
| structural_family | ribbed_threaded_cup | ③ receiver interface | ribbed cylindrical housing + threaded cup | rec_0611_manual_coffee_grinder_var_catch_threaded_cup/rev_000001 | model.py:L21-L192; model.py:L193-L458 | accepted source-backed | Same source-recognizable black ribbed host, but the housing carries a stepped annular thread socket and the open cup carries an engagement lip plus 24 readable knurl flats. Receiver motion is a +Z revolute unscrewing joint, not a drawer or fake prismatic slide. |
| structural_family | wood_cabinet_drawer | ① cabinet silhouette | cut wooden cabinet + pull drawer | rec_picturex_0611__manual_coffee_grinder__003__png_3e1dc714e9524c71a7bac3f672f2b4cf/rev_000001 | model.py:L33-L142; model.py:L143-L422 | accepted source-backed | Rounded square wood cabinet is cut by a 110×126×78 mm front cavity. The front recess has top/bottom/left/right rails; the tray is open and hollow, with a separate face and turned knob, translating along −Y. Dark bowl, top plate and burr flange preserve source 003. |
| structural_family | square_wood_cup | ① body silhouette | hollow square wood housing + removable cup | rec_0611_manual_coffee_grinder_var_body_form_square_wood_box/rev_000001 | model.py:L20-L181; model.py:L182-L435 | accepted source-backed | Hollow square wood upper shell with real top/bottom circular passages and an internal floor; lower open cup and source-002 coaxial seam are retained as one family. |
| structural_family | slim_drawer_cylinder | ① body silhouette | slim cylinder + cut drawer landing | rec_0611_manual_coffee_grinder_var_body_form_slim_travel_cylinder/rev_000001 | model.py:L33-L149; model.py:L150-L430 | accepted source-backed | Cylindrical wood body is fused to a rectangular front landing before the same real drawer cavity is subtracted. The drawer is therefore retained by an actual host opening and four rails, never placed against a solid curved wall. |

The pull-out-drawer fork is secondary evidence for both drawer candidates:
`rec_0611_manual_coffee_grinder_var_catch_pull_out_drawer/rev_000001`,
`model.py:L31-L166; model.py:L167-L463`. It specifies the open tray wall/bottom
construction, rabbet lip, complete recess frame and 80 mm −Y travel. It is not an independent
candidate because those features require a corresponding host cut.

## Slot B — `drive`

The selected structural family publishes a drive axis and adds the correct local top or side
bearing. All rotational joints are assembled from explicit axis interfaces.

| Slot | Candidate | Diversity axis | Component type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|---|
| drive | rigid_top_crank | ③ drive form | top crank + free-spinning grip | rec_picturex_0611__manual_coffee_grinder__001__png_c35ee4d5322147f7b86183d272e2207d/rev_000001 | model.py:L48-L64; model.py:L306-L404 | accepted source-backed | Vertical shaft, thin forged horizontal arm with circular pads, real handle pin and bored turned grip; crank and grip rotate about parallel +Z axes. |
| drive | folding_top_crank | ③ drive form | deployed folding-form crank + free-spinning grip | rec_0611_manual_coffee_grinder_var_drive_folding_top_crank/rev_000001 | model.py:L24-L102; model.py:L103-L503 | accepted source-backed | Two-ear clevis hub, bored tongue and raised deployed arm preserve the source folding-crank silhouette. The arm and clevis are one rigid manufactured crank in the delivered working pose; host→crank rotates about +Z and crank→grip remains free-spinning about +Z. |
| drive | side_crank | ③ drive placement | side shaft + crank + free-spinning grip | rec_0611_manual_coffee_grinder_var_drive_side_crank/rev_000001 | model.py:L38-L147; model.py:L148-L461 | accepted source-backed | Real side bearing and shaft passage on +X face; shaft and grip rotate about +X while the crank arm offsets the grip vertically. Host bearing position derives from family envelope and stays above drawer travel. |

## Slot C — `closure`

Closure is local to the published hopper rim. `open` preserves each family's source-specific open
hopper. `hinged_cover` adds a rim-sized slotted plate, recessed host saddle and two bored
knuckles around the registered hinge axis; it does not replace the underlying source-specific
bowl/cylinder.

| Slot | Candidate | Diversity axis | Component type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|---|
| closure | open | ② access state | open hopper rim | rec_0611_manual_coffee_grinder_var_hopper_open_bowl/rev_000001 | model.py:L24-L64; model.py:L65-L407 | accepted source-backed | Explicit inner/outer bowl profiles, flat caps and rolled rim preserve a visibly open bean cavity rather than a solid capped cone. |
| closure | hinged_cover | ③ closure mechanism | slotted hinged lid | rec_0611_manual_coffee_grinder_var_hopper_hinged_covered_hopper/rev_000001 | model.py:L20-L217; model.py:L218-L470 | accepted source-backed | Recessed fixed saddle, two bored outer knuckles, connecting webs, shaft-clearance opening and 0–100° registered revolute motion. The top drive is raised from the published rim envelope so the opened lid clears the crank sweep. |

## Slot D — `mount`

The mount consumes `ground_seat`. The clamp fork demonstrates a local annular plate and C-arm
below the grinder; its envelope is derived from family radius so it need not change upper
topology.

| Slot | Candidate | Diversity axis | Component type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|---|
| mount | countertop | ② mounting state | flat support seat | rec_picturex_0611__manual_coffee_grinder__003__png_3e1dc714e9524c71a7bac3f672f2b4cf/rev_000001 | model.py:L143-L422 | accepted source-backed | Source bodies sit on a complete wood/metal base with a stable real footprint; no extra floating mount part is emitted. |
| mount | table_clamp | ③ mounting mechanism | C-clamp bracket + screw | rec_0611_manual_coffee_grinder_var_mount_table_clamp/rev_000001 | model.py:L24-L138; model.py:L139-L485 | accepted source-backed | Annular attachment plate overlaps a radial arm, vertical spine and return jaw; a real screw hole, threaded screw, T-handle, retaining flange and contact pad form a readable table clamp. Cup families publish a higher body-side clamp seat so the bracket cannot intersect the removable receiver. |

## Continuous parameters and derivations

- `scale = 0.90–1.12` applies uniformly after family-specific source proportions are established.
- `drawer_travel_m = 0.050–0.080` only affects drawer families; cavity depth, rail length and
  rear stop are derived from the same value.
- `cup_release_m = 0.025–0.040` controls prismatic cups. Threaded cups instead use
  `thread_turns = 1.5–2.0`, with socket and engagement length derived together.
- `crank_reach_m = 0.078–0.105` and `grip_length_m = 0.045–0.064` apply to all drives.
- `wall_clearance_m = 0.0006–0.0012` derives drawer side/top clearances, cup radial clearance,
  shaft/bore clearance and hinge-knuckle clearance.
- `hopper_rim_radius_m` is published by the structural family; hinged lid radius, shaft slot,
  saddle offset and knuckle spacing derive from it.

## Assembly, interfaces and mechanical acceptance

- Root is always `housing`. Adjustment collar and selected drive remain real moving members.
- Drawer families: `housing -> grounds_drawer` is PRISMATIC along −Y, lower 0, upper
  `drawer_travel_m`. The housing CAD is cut by a cavity extending through the front wall; an open
  hollow tray enters that cavity; top, bottom, left and right rails plus a rear stop retain it.
- Prismatic-cup families: `housing -> grounds_cup` moves down −Z. Threaded cup:
  `housing -> grounds_cup` is REVOLUTE +Z with 1.5–2 turns and a real stepped socket/lip.
- `housing -> adjustment_collar`, every crank shaft and free-spinning grip use
  `AxisInterface`, `mate_axes` and `register_interface_mate`.
- Hinged closure uses a transverse registered axis outside the rim, bored knuckles and an open
  shaft clearance. Closed and fully open poses must remain collision-free.
- No `allow_overlap` is permitted. `allow_isolated_part` is limited to joint-retained rotating
  members and the threaded cup, whose positive running clearance intentionally separates them
  from the host. Static housing geometry must remain connected; moving shafts and receivers use
  real bores/cavities with positive clearance.

## Rejected constructions

- Independent `catch`, because it creates drawer/solid-body and cup/closed-base combinations.
- A drawer face merely touching or overlapping the outside of a solid body.
- Solid trays, solid bowls, decorative painted openings, absent side rails, and drawers whose
  motion axis does not point through the visible front opening.
- Complete-source family candidates mixed with independently authored body/catch candidates.
- The loose detached burr visible beside source image 002.
- Compatibility gates, overlap allowances and any geometry that only looks valid at the rest pose.
