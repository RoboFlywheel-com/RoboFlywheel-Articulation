# pictureX_0611_butterfly_valve_with_lever_operator — SourceMap

source_map_schema: 1
export_category: pictureX_0611_butterfly_valve_with_lever_operator
picture_category: 0611
picture_subcategory: butterfly_valve_with_lever_operator
category_scope: Quarter-turn butterfly valves: a short cast body with a real through bore and a seat liner, a disc on a vertical stem that turns across that bore, a stem tower with a locking quadrant, and a hand operator (lever or gear handwheel); ball valves, gate valves, plug cocks and check valves are not candidates.

sync_records:
  - rec_butterfly_valve_var_double_flanged_body
  - rec_butterfly_valve_var_gear_operator_handwheel
  - rec_butterfly_valve_var_grooved_end_body
  - rec_butterfly_valve_var_lug_body
  - rec_butterfly_valve_var_lug_bolt_hole_count
  - rec_butterfly_valve_var_offset_high_perf_disc
  - rec_butterfly_valve_var_probe_gear_operator_lug_body
  - rec_butterfly_valve_var_quadrant_notch_count
  - rec_butterfly_valve_var_tee_bar_handle
  - rec_butterfly_valve_var_triple_offset_disc
  - rec_butterfly_valve_with_lever_operator_var_bare_lever
  - rec_butterfly_valve_with_lever_operator_var_bolt_holes_n12
  - rec_butterfly_valve_with_lever_operator_var_bolt_holes_n4
  - rec_butterfly_valve_with_lever_operator_var_bolt_holes_n8
  - rec_butterfly_valve_with_lever_operator_var_double_offset_disc
  - rec_butterfly_valve_with_lever_operator_var_flanged_body
  - rec_butterfly_valve_with_lever_operator_var_grooved_end
  - rec_butterfly_valve_with_lever_operator_var_long_neck_bonnet
  - rec_butterfly_valve_with_lever_operator_var_notched_plate_lever
  - rec_picturex_0611__butterfly_valve_with_lever_operator__001__png__airflex_batch_20260710_e399fe268f844b668b428b4fea1cb5c9

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__butterfly_valve_with_lever_operator__001__png__airflex_batch_20260710_e399fe268f844b668b428b4fea1cb5c9/rev_000001 | reviewed | used | Origin: a blue cast body with a seat liner, a disc on a vertical stem, a stem tower with a notched locking quadrant and a trigger lever. |
| rec_butterfly_valve_var_lug_body/rev_000001 | reviewed | used | The lug-style body: a ring of bolt-ear lugs on a bolt circle, each drilled through after the casting is fused. |
| rec_butterfly_valve_with_lever_operator_var_flanged_body/rev_000001 | reviewed | used | The double-flanged body: raised end flanges drilled on a bolt circle instead of tapped lugs. |
| rec_butterfly_valve_with_lever_operator_var_grooved_end/rev_000001 | reviewed | used | The grooved-end body: machined coupling grooves and shoulders at both ends for a clamp coupling. |
| rec_butterfly_valve_var_offset_high_perf_disc/rev_000001 | reviewed | used | The high-performance disc: an offset hub and a profiled sealing edge instead of a flat concentric plate. |
| rec_butterfly_valve_var_gear_operator_handwheel/rev_000001 | reviewed | used | The gear operator: a gearbox housing on the stem tower carrying a spoked handwheel on its own input axis. |
| rec_butterfly_valve_var_lug_bolt_hole_count/rev_000001 | reviewed | reference_only | Establishes the bolt-hole count rule that the body candidates already implement. |
| rec_butterfly_valve_with_lever_operator_var_bolt_holes_n4/rev_000001 | reviewed | reference_only | The same count rule at four holes. |
| rec_butterfly_valve_with_lever_operator_var_bolt_holes_n8/rev_000001 | reviewed | reference_only | The same count rule at eight holes. |
| rec_butterfly_valve_with_lever_operator_var_bolt_holes_n12/rev_000001 | reviewed | reference_only | The same count rule at twelve holes. |
| rec_butterfly_valve_var_double_flanged_body/rev_000001 | reviewed | reference_only | Duplicates the reviewed flanged body form. |
| rec_butterfly_valve_var_grooved_end_body/rev_000001 | reviewed | reference_only | Duplicates the reviewed grooved-end form. |
| rec_butterfly_valve_var_probe_gear_operator_lug_body/rev_000001 | reviewed | reference_only | A gear operator on a lug body; both forms are already accepted separately. |
| rec_butterfly_valve_with_lever_operator_var_double_offset_disc/rev_000001 | reviewed | used | The double-offset disc: the disc centre is shifted off the shaft axis in two directions and rides an eccentric hub boss, so it cams away from the seat instead of pivoting in it. |
| rec_butterfly_valve_var_triple_offset_disc/rev_000001 | reviewed | used | The triple-offset disc: a revolved conical frustum, thick at the hub and tapering to the rim, with an axial cone offset that torque-seats instead of rubbing. |
| rec_butterfly_valve_var_quadrant_notch_count/rev_000001 | reviewed | reference_only | Only varies the number of locking notches on the quadrant. |
| rec_butterfly_valve_var_tee_bar_handle/rev_000001 | reviewed | used | The tee-bar operator: a short transverse crossbar with two rounded grip sleeves seated on the operator hub instead of a single long lever. |
| rec_butterfly_valve_with_lever_operator_var_bare_lever/rev_000001 | reviewed | reference_only | The same lever without its grip sleeve. |
| rec_butterfly_valve_with_lever_operator_var_notched_plate_lever/rev_000001 | reviewed | reference_only | The same lever with a different notch plate. |
| rec_butterfly_valve_with_lever_operator_var_long_neck_bonnet/rev_000001 | reviewed | used | The extended bonnet: a tall neck column between the body and the operator boss, with the gussets and the shaft bore stretched to span it. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| body_end | lug_body | drilled bolt-ear lugs | rec_butterfly_valve_var_lug_body/rev_000001 | model.py:L67-L132 | structure | A ring of lug bosses on a bolt circle is fused to the casting and then drilled through. |
| body_end | flanged_body | raised drilled end flanges | rec_butterfly_valve_with_lever_operator_var_flanged_body/rev_000001 | model.py:L67-L142 | structure | Raised flanges at both ends are drilled on a bolt circle instead of tapped lugs. |
| body_end | grooved_end | machined coupling grooves | rec_butterfly_valve_with_lever_operator_var_grooved_end/rev_000001 | model.py:L67-L142 | structure | Both ends carry a machined shoulder and a coupling groove for a clamp coupling. |
| disc_form | concentric_disc | flat concentric disc | rec_picturex_0611__butterfly_valve_with_lever_operator__001__png__airflex_batch_20260710_e399fe268f844b668b428b4fea1cb5c9/rev_000001 | model.py:L149-L156 | structure | A flat plate on the stem centreline seals against the liner all round. |
| disc_form | offset_disc | offset high-performance disc | rec_butterfly_valve_var_offset_high_perf_disc/rev_000001 | model.py:L135-L191 | structure | The hub is offset from the seat plane and the rim carries a profiled sealing edge. |
| operator | lever_trigger | trigger lever on the quadrant | rec_picturex_0611__butterfly_valve_with_lever_operator__001__png__airflex_batch_20260710_e399fe268f844b668b428b4fea1cb5c9/rev_000001 | model.py:L157-L212 | structure | A lever plate with a grip sleeve and a sprung trigger plate rides the notched locking quadrant. |
| disc_form | triple_offset_disc | conical triple-offset disc | rec_butterfly_valve_var_triple_offset_disc/rev_000001 | model.py:L123-L170 | structure | A revolved conical frustum thick at the hub and tapering to the rim, with an axial cone offset on the seating face. |
| disc_form | double_offset_disc | eccentric double-offset disc | rec_butterfly_valve_with_lever_operator_var_double_offset_disc/rev_000001 | model.py:L123-L167 | structure | A thin plate whose centre is shifted off the shaft axis in two directions, carried on an eccentric hub boss. |
| operator | tee_bar | transverse tee-bar handle | rec_butterfly_valve_var_tee_bar_handle/rev_000001 | model.py:L143-L162 | structure | A short transverse crossbar on the operator hub carries two rounded grip sleeves instead of one long lever arm. |
| bonnet_form | short_bonnet | wafer-height stem tower | rec_picturex_0611__butterfly_valve_with_lever_operator__001__png__airflex_batch_20260710_e399fe268f844b668b428b4fea1cb5c9/rev_000001 | model.py:L67-L100 | structure | The operator boss sits directly on the short cast tower above the body. |
| bonnet_form | extended_bonnet | tall extended neck column | rec_butterfly_valve_with_lever_operator_var_long_neck_bonnet/rev_000001 | model.py:L81-L100 | structure | A tall neck column lifts the operator boss clear of the body, with the gussets and the shaft bore stretched to span it. |
| operator | gear_handwheel | worm gearbox with a handwheel | rec_butterfly_valve_var_gear_operator_handwheel/rev_000001 | model.py:L131-L279 | structure+motion | A gearbox housing on the tower carries a spoked handwheel turning on its own input axis. |

## Component evidence

- The body bore, seat liner, stem and disc chain are identity-fixed host structure
  (`rec_butterfly_valve_var_lug_body/rev_000001` `model.py:L133-L146`), so they are not a slot:
  every seed keeps a quarter-turn disc on a vertical stem inside a lined bore.
- Bolt-hole multiplicity comes from `rec_butterfly_valve_var_lug_bolt_hole_count/rev_000001`
  `model.py:L33-L47`, which derives the lug positions from a count; the n4/n8/n12 records are the
  reviewed values.
