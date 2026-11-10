# badge_id_holder_clip — SourceMap

source_map_schema: 1
export_category: badge_id_holder_clip
picture_category: Workspace
picture_subcategory: Badge_ID holder clip

category_scope: A single wearable badge/ID holder clip. One rigid clip_body is the root; one moving clamp member grips clothing against it (a sprung metal jaw on a hinge pin, or a magnet backer that slides onto the body's guide pins); one badge_connector hangs from a swivel on the body's tail and turns freely in the badge plane. Everything the clip carries (strap, card frame, ring) is one connector component on that swivel. Lanyards, retractable reels with an internal spool, and multi-clip badge racks change the host topology and are out of scope.

sync_records:
  - rec_badge_id_holder_clip_var_bulldog
  - rec_badge_id_holder_clip_var_card_frame
  - rec_badge_id_holder_clip_var_magnetic_clamp
  - rec_badge_id_holder_clip_var_ring_loop
  - rec_badge_id_holder_clip_var_teeth_n10
  - rec_badge_id_holder_clip_var_teeth_n3
  - rec_workspace__badge_id_holder_clip__001_png_7dc48dbbc5dd43d0b06f6c79d8d3f735
  - rec_workspace__badge_id_holder_clip__002_png_3aa298bf627743c88a2d15ec0e880c1d

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_workspace__badge_id_holder_clip__002_png_3aa298bf627743c88a2d15ec0e880c1d/rev_000001 | reviewed | used | Image-grounded alligator reading: a long stamped lower leaf with two folded side cheeks carrying a through hinge pin and a torsion coil, a tapered spring jaw whose barrel wraps that pin and whose front end is folded into a blade, serrated tooth bars at the mouth, a swivel post with a crimped boss at the tail, and a perforated clear vinyl strap on the swivel. Supplies the alligator_yoke clamp, the serrated_bar grip, the post_boss swivel and the perforated_strap connector. |
| rec_workspace__badge_id_holder_clip__001_png_7dc48dbbc5dd43d0b06f6c79d8d3f735/rev_000001 | reviewed | used | Second image-grounded reading built quite differently: the lower jaw is stiffened by two folded side rails, the hinge is carried by two upright riveted ears with two separate spring coils flanking the jaw barrel, the moving jaw carries a riveted thumb pad, the grip is a row of discrete stamped teeth behind a rolled front lip, and the swivel sits on a raised rear bridge with a flat mount plate and a low disc receiver under a snap-plate strap with an oblong slot. Supplies the ear_hinge_thumb clamp, the discrete_teeth grip, the bridge_mount swivel and the slotted_strap connector. |
| rec_badge_id_holder_clip_var_bulldog/rev_000001 | reviewed | used | Bulldog reading: the clamp becomes short and wide instead of long and slender, and the moving leaf grows two bent sheet-metal finger levers behind the hinge line so the clip is squeezed open from the tail rather than pressed at the mouth. Supplies the bulldog_lever clamp. |
| rec_badge_id_holder_clip_var_magnetic_clamp/rev_000001 | reviewed | used | Drops the hinge entirely: a flat carrier plate and a separate rear magnet backer carrying cylindrical magnet poles, joined by a linear clamp joint that opens away from the carrier plate so cloth passes between them. Supplies the magnet_backer clamp, the only non-hinged attachment mechanism in the pool. |
| rec_badge_id_holder_clip_var_card_frame/rev_000001 | reviewed | used | Replaces the flexible strap with a rigid moulded open-face card holder: a thin back panel with raised left, right and bottom border rails and an open top edge so a portrait CR80 card slides in. Supplies the card_frame connector. |
| rec_badge_id_holder_clip_var_ring_loop/rev_000001 | reviewed | used | Replaces the strap with hardware: a short neck shank rising from the swivel hub into a standing torus ring a lanyard can be threaded through. Supplies the ring_loop connector. |
| rec_badge_id_holder_clip_var_teeth_n3/rev_000001 | reviewed | rejected_no_structural_value | Identical to the 002 alligator reading except that both tooth bars are rebuilt with three coarse serrations instead of six. Only the serration count and pitch move; the part tree, joints, interfaces and every profile are unchanged, so it produces no candidate. Kept as evidence that the tooth row is index-general. |
| rec_badge_id_holder_clip_var_teeth_n10/rev_000001 | reviewed | rejected_no_structural_value | The same file again with ten fine serrations. A pure decorative-count axis with no structural, motion or interface consequence, so it produces no candidate either. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| clamp_build | alligator_yoke | clamp mechanism | rec_workspace__badge_id_holder_clip__002_png_3aa298bf627743c88a2d15ec0e880c1d/rev_000001 | model.py:L154-L276, model.py:L312-L329 | structure+motion | Long slender stamped leaf with two folded side cheeks carrying a through hinge pin and a torsion coil; the sprung jaw's barrel wraps that pin and its front end is folded into a blade over the mouth. |
| clamp_build | ear_hinge_thumb | clamp mechanism | rec_workspace__badge_id_holder_clip__001_png_7dc48dbbc5dd43d0b06f6c79d8d3f735/rev_000001 | model.py:L73-L220 | structure | The same hinge duty built from different parts: folded side rails stiffen the lower jaw, two upright riveted ears carry the pin, separate spring coils flank the barrel, and the moving jaw carries a riveted thumb pad instead of a folded blade. |
| clamp_build | bulldog_lever | clamp mechanism | rec_badge_id_holder_clip_var_bulldog/rev_000001 | model.py:L113-L146, model.py:L196-L371 | structure | Short wide bulldog clamp whose moving leaf grows two bent sheet-metal finger levers behind the hinge, so the tail carries a lever pair the slender readings do not have. |
| clamp_build | magnet_backer | clamp mechanism | rec_badge_id_holder_clip_var_magnetic_clamp/rev_000001 | model.py:L102-L175, model.py:L216-L244 | structure+motion | No hinge at all: a flat carrier plate and a separate rear magnet backer with cylindrical poles, joined by a linear clamp joint instead of a revolute one. |
| grip_build | serrated_bar | grip face | rec_workspace__badge_id_holder_clip__002_png_3aa298bf627743c88a2d15ec0e880c1d/rev_000001 | model.py:L118-L138, model.py:L176-L181, model.py:L271-L276 | structure | Each gripping face is one connected serrated bar: a thin backing strip with rectangular teeth extruded out of it, welded into a single solid. |
| grip_build | discrete_teeth | grip face | rec_workspace__badge_id_holder_clip__001_png_7dc48dbbc5dd43d0b06f6c79d8d3f735/rev_000001 | model.py:L102-L115, model.py:L208-L220 | structure | The same duty as separate stamped teeth standing behind a rolled front lip instead of one welded bar, so the mouth reads as a folded lip with individual points. |
| swivel_build | post_boss | swivel mount | rec_workspace__badge_id_holder_clip__002_png_3aa298bf627743c88a2d15ec0e880c1d/rev_000001 | model.py:L212-L223, model.py:L299-L310 | structure | A slim round post standing off the tail of the body with a wide crimped boss flange at its tip, and a button ring on the connector closing over that flange. |
| swivel_build | bridge_mount | swivel mount | rec_workspace__badge_id_holder_clip__001_png_7dc48dbbc5dd43d0b06f6c79d8d3f735/rev_000001 | model.py:L147-L170, model.py:L243-L282 | structure | A raised rectangular rear bridge carrying a flat mount plate and a low disc receiver, with a reinforcement plate, pivot stem and capped button on the connector instead of a bare ring. |
| connector_build | perforated_strap | badge connector | rec_workspace__badge_id_holder_clip__002_png_3aa298bf627743c88a2d15ec0e880c1d/rev_000001 | model.py:L278-L298 | structure | Long clear vinyl strap punched with a swivel eye, a long oblong badge slot and a rectangular grid of ventilation holes. |
| connector_build | slotted_strap | badge connector | rec_workspace__badge_id_holder_clip__001_png_7dc48dbbc5dd43d0b06f6c79d8d3f735/rev_000001 | model.py:L43-L56, model.py:L222-L242 | structure | Shorter clear tab with one oblong key-ring slot and two raised stiffening edge rails running its whole length, a different plate profile and rib topology from the perforated strap. |
| connector_build | card_frame | badge connector | rec_badge_id_holder_clip_var_card_frame/rev_000001 | model.py:L118-L157, model.py:L321-L327 | structure | Rigid moulded card holder: a thin back panel with raised left, right and bottom border rails and a deliberately open top edge so a portrait card can be slid in. |
| connector_build | ring_loop | badge connector | rec_badge_id_holder_clip_var_ring_loop/rev_000001 | model.py:L278-L308 | structure | Hardware instead of a panel: a short neck shank rising from the swivel hub into a standing torus ring for a lanyard. |
