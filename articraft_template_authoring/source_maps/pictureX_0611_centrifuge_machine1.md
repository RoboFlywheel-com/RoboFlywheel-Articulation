# pictureX_0611_centrifuge_machine1 — SourceMap

source_map_schema: 1
export_category: pictureX_0611_centrifuge_machine1
picture_category: 0611
picture_subcategory: centrifuge_machine1
category_scope: Benchtop laboratory centrifuges: a moulded housing with a recessed rotor well, a rotor carrying a ring of tube holders spinning about the vertical drive axis, a lid closing over that well, and a front control panel; blenders, spin dryers, floor-standing industrial separators and vortex mixers are not candidates.

sync_records:
  - rec_centrifuge_machine1_var_clinical_box
  - rec_centrifuge_machine1_var_lift_lid
  - rec_centrifuge_machine1_var_microfuge
  - rec_centrifuge_machine1_var_plinth_base
  - rec_centrifuge_machine1_var_probe_clinical_swing_bucket
  - rec_centrifuge_machine1_var_probe_sliding_lid_n24
  - rec_centrifuge_machine1_var_rotor_n12
  - rec_centrifuge_machine1_var_rotor_n24
  - rec_centrifuge_machine1_var_sliding_lid
  - rec_centrifuge_machine1_var_swing_bucket
  - rec_picturex_0611__centrifuge_machine1__001__png__redo_20260710_51206fe6f50f4dcea7bd67881b14c6cc

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__centrifuge_machine1__001__png__redo_20260710_51206fe6f50f4dcea7bd67881b14c6cc/rev_000001 | reviewed | used | Origin: a lofted benchtop shell with a recessed rotor well, a fixed-angle rotor and a hinged lid over the well. |
| rec_centrifuge_machine1_var_clinical_box/rev_000001 | reviewed | used | The clinical box housing: a squarer cabinet with a stepped front panel shelf instead of the lofted shell. |
| rec_centrifuge_machine1_var_microfuge/rev_000001 | reviewed | used | The compact microfuge housing: a small tall body whose rotor well is a narrow recess near the top. |
| rec_centrifuge_machine1_var_swing_bucket/rev_000001 | reviewed | used | The swing-bucket rotor: indexed bucket carriers hung off the rotor arms instead of drilled angled wells. |
| rec_centrifuge_machine1_var_sliding_lid/rev_000001 | reviewed | used | The sliding lid: the cover runs back on rails across the well instead of hinging up. |
| rec_centrifuge_machine1_var_rotor_n12/rev_000001 | reviewed | reference_only | Establishes the holder-count rule at twelve positions. |
| rec_centrifuge_machine1_var_rotor_n24/rev_000001 | reviewed | reference_only | The same rule at twenty-four positions. |
| rec_centrifuge_machine1_var_probe_sliding_lid_n24/rev_000001 | reviewed | reference_only | Combines the sliding lid with twenty-four holders; both forms are accepted separately. |
| rec_centrifuge_machine1_var_probe_clinical_swing_bucket/rev_000001 | reviewed | reference_only | Combines the clinical box with swing buckets; both forms are accepted separately. |
| rec_centrifuge_machine1_var_lift_lid/rev_000001 | reviewed | used | The lift-off dome lid: two vertical alignment posts on the rear deck guide the cover straight up off the well on a prismatic lift. |
| rec_centrifuge_machine1_var_plinth_base/rev_000001 | reviewed | used | The plinth housing: a continuous moulded pedestal skirt carries the body clear of the bench, changing the whole lower silhouette. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| housing_form | benchtop_shell | lofted benchtop shell | rec_picturex_0611__centrifuge_machine1__001__png__redo_20260710_51206fe6f50f4dcea7bd67881b14c6cc/rev_000001 | model.py:L106-L188 | structure | A lofted outline shell is cut with a circular rotor recess and a moulded well rim. |
| housing_form | clinical_box | squared clinical cabinet | rec_centrifuge_machine1_var_clinical_box/rev_000001 | model.py:L98-L200 | structure | A squarer cabinet body with a stepped front shelf carries the same rotor recess. |
| housing_form | microfuge | compact microfuge body | rec_centrifuge_machine1_var_microfuge/rev_000001 | model.py:L73-L180 | structure | A small tall body whose narrow rotor well sits just under the top face. |
| housing_form | plinth_shell | shell on a moulded plinth | rec_centrifuge_machine1_var_plinth_base/rev_000001 | model.py:L161-L175 | structure | A continuous lofted pedestal skirt under the body meets the bench and lifts the whole shell. |
| lid_action | lift_lid | guided lift-off dome | rec_centrifuge_machine1_var_lift_lid/rev_000001 | model.py:L285-L300 | structure+motion | The cover rises straight off the well on a prismatic lift, guided by two vertical posts on the rear deck. |
| panel_control | latch_lever | pivoting front latch lever | rec_centrifuge_machine1_var_lift_lid/rev_000001 | model.py:L405-L432 | structure+motion | A shafted lever with a tipped handle swings on the housing front to lock the lid. |
| panel_control | push_button | short-travel push control | rec_centrifuge_machine1_var_lift_lid/rev_000001 | model.py:L434-L452 | structure+motion | A small momentary button travels straight into its housing recess. |
| rotor_form | fixed_angle | drilled fixed-angle rotor | rec_picturex_0611__centrifuge_machine1__001__png__redo_20260710_51206fe6f50f4dcea7bd67881b14c6cc/rev_000001 | model.py:L189-L260 | structure | A solid conical rotor is drilled with evenly indexed angled tube wells. |
| rotor_form | swing_bucket | hung swing-bucket carriers | rec_centrifuge_machine1_var_swing_bucket/rev_000001 | model.py:L196-L300 | structure | Indexed bucket carriers hang off the rotor arms instead of being drilled into the body. |
| lid_action | hinged_lid | rear-hinged cover | rec_picturex_0611__centrifuge_machine1__001__png__redo_20260710_51206fe6f50f4dcea7bd67881b14c6cc/rev_000001 | model.py:L261-L340 | structure+motion | The cover swings up on a rear hinge line above the well rim. |
| lid_action | sliding_lid | rail-mounted sliding cover | rec_centrifuge_machine1_var_sliding_lid/rev_000001 | model.py:L262-L360 | structure+motion | The cover runs back on side rails across the well instead of hinging. |

## Component evidence

- The rotor well, drive boss and control panel are identity-fixed host structure
  (`rec_picturex_0611__centrifuge_machine1__001__png__redo_20260710_51206fe6f50f4dcea7bd67881b14c6cc/rev_000001`
  `model.py:L21-L23` for the well and mount datums), so they are not a slot.
- Holder multiplicity comes from `rec_centrifuge_machine1_var_rotor_n12/rev_000001`
  `model.py:L25-L26` and `rec_centrifuge_machine1_var_rotor_n24/rev_000001`, which derive the
  holder positions from a count rather than hard-coding them.
