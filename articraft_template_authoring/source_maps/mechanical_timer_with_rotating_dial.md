# Mechanical timer with rotating dial — SourceMap

export_category: mechanical_timer_with_rotating_dial

The authoritative source pool is `<ARTI_SKILL_ROOT>/articraft_data/data/records`.
The four picture-bound originals establish the timer family; the seven fork records each
contribute one explicitly requested structural component. No source closure or copied code is
stored here.

sync_records:
  - rec_picturex_0611__mechanical_timer_with_rotating_dial__001__png_43707496c3dc4b4ab4ac2ae5621a570e
  - rec_use-the-attached-reference-image-as-the-primary-_20260710_090613_155734_8b959953
  - rec_picturex_0611__mechanical_timer_with_rotating_dial__003__png_50670c8986354bcaa03f53921e9c95d9
  - rec_picturex_0611__mechanical_timer_with_rotating_dial__004__png_1c4b1da83b464c3c8b6568f660212212
  - rec_0611_mechanical_timer_with_rotating_var_body_form_round_puck
  - rec_0611_mechanical_timer_with_rotating_var_body_form_sloped_wedge
  - rec_0611_mechanical_timer_with_rotating_var_scale_concentric_dual_scale
  - rec_0611_mechanical_timer_with_rotating_var_winding_control_outer_rotating_bezel
  - rec_0611_mechanical_timer_with_rotating_var_support_folding_magnetic_stand
  - rec_0611_mechanical_timer_with_rotating_var_support_wall_bracket
  - rec_0611_mechanical_timer_with_rotating_var_alert_control_bell_silence_lever

| Slot | Candidate | Diversity axis | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| body_form | arched_rect | ③ major housing silhouette | enclosure | rec_picturex_0611__mechanical_timer_with_rotating_dial__001__png_43707496c3dc4b4ab4ac2ae5621a570e/rev_000001 | model.py:L208-L294 | accepted | Filleted tall rectangular housing, inset front face, rear spring case and paired tabletop feet. |
| body_form | soft_square | ③ major housing silhouette | enclosure | rec_picturex_0611__mechanical_timer_with_rotating_dial__004__png_1c4b1da83b464c3c8b6568f660212212/rev_000001 | model.py:L26-L49; model.py:L230-L280 | accepted | Rounded compact square housing with stepped rear spring case. |
| body_form | round_puck | ③ major housing silhouette | enclosure | rec_0611_mechanical_timer_with_rotating_var_body_form_round_puck/rev_000001 | model.py:L20-L75; model.py:L240-L300 | accepted | Fork intent targets body_form; circular puck housing and stepped circular rear shell replace the parent outline. |
| body_form | sloped_wedge | ③ major housing silhouette | enclosure | rec_0611_mechanical_timer_with_rotating_var_body_form_sloped_wedge/rev_000001 | model.py:L25-L90; model.py:L223-L310 | accepted | Fork intent targets body_form; wedge depth and inclined front plane create a freestanding sloped timer body. |
| body_form | tall_program_case | ③ integral housing layout | enclosure with lower support body | rec_picturex_0611__mechanical_timer_with_rotating_dial__003__png_50670c8986354bcaa03f53921e9c95d9/rev_000001 | model.py:L36-L85; model.py:L235-L265 | accepted | Circular timer head is fused to a long rounded lower case with a recessed front feature, three slots and indicator lens; this macro silhouette must remain a body candidate rather than being reduced to a rear plug. |
| body_form | pedestal_round | ③ integral housing layout | pedestal enclosure | rec_use-the-attached-reference-image-as-the-primary-_20260710_090613_155734_8b959953/rev_000001 | model.py:L33-L62; model.py:L138-L187 | accepted | Round spring case, narrow pedestal, widened rounded foot and rear gusset form the characteristic freestanding source silhouette. The coupled source shape is retained as one parameterized body candidate. |
| scale | numbered_radial | ③ face information architecture | dial scale | rec_use-the-attached-reference-image-as-the-primary-_20260710_090613_155734_8b959953/rev_000001 | model.py:L74-L112; model.py:L189-L209 | accepted | Sixty radial ticks plus twelve upright 5–60 minute labels using the source's true font outlines rather than block seven-segment approximations. |
| scale | direction_ring | ③ face information architecture | dial scale | rec_picturex_0611__mechanical_timer_with_rotating_dial__003__png_50670c8986354bcaa03f53921e9c95d9/rev_000001 | model.py:L106-L149; model.py:L331-L344 | accepted | Minute ring, cardinal numerals and curved direction arrow form a distinct program-timer face. |
| scale | concentric_dual | ③ face information architecture | dial scale | rec_0611_mechanical_timer_with_rotating_var_scale_concentric_dual_scale/rev_000001 | model.py:L106-L175; model.py:L342-L372 | accepted | Fork intent targets scale; two concentric tick bands and direction markings replace the single radial scale. |
| winding_control | center_paddle | ② moving control mechanism | rotary control | rec_use-the-attached-reference-image-as-the-primary-_20260710_090613_155734_8b959953/rev_000001 | model.py:L115-L135; model.py:L212-L239; model.py:L279-L293 | accepted | Long shaped central paddle and coaxial spindle rotate independently at the face center. |
| winding_control | outer_bezel | ② moving control mechanism | rotary control | rec_0611_mechanical_timer_with_rotating_var_winding_control_outer_rotating_bezel/rev_000001 | model.py:L207-L234; model.py:L312-L377 | accepted | Fork intent targets winding_control; scalloped outer grip ring and marker rotate on a bounded coaxial joint. |
| support | tabletop_feet | ③ installation mode | fixed support | rec_picturex_0611__mechanical_timer_with_rotating_dial__001__png_43707496c3dc4b4ab4ac2ae5621a570e/rev_000001 | model.py:L287-L294 | accepted | Paired rubber rear feet provide ordinary countertop support. |
| support | rear_plug | ③ installation mode | fixed support | rec_picturex_0611__mechanical_timer_with_rotating_dial__003__png_50670c8986354bcaa03f53921e9c95d9/rev_000001 | model.py:L384-L418 | accepted | Rear boss with a practical two-blade layout forms a plug-in wall support; the source's third blade is omitted as a realism refinement. |
| support | folding_magnetic_stand | ① articulated support topology | articulated support | rec_0611_mechanical_timer_with_rotating_var_support_folding_magnetic_stand/rev_000001 | model.py:L131-L170; model.py:L307-L385 | accepted | Fork intent targets support; magnetic kickstand panel adds a revolute rear hinge with 0–1.05 rad travel. |
| support | wall_bracket | ③ installation mode | fixed support | rec_0611_mechanical_timer_with_rotating_var_support_wall_bracket/rev_000001 | model.py:L171-L213; model.py:L429-L444 | accepted | Fork intent targets support; stamped bracket has twin keyholes, reinforcing ribs and a fixed rear mount. |
| alert_control | none | ① optional mechanism absent | optional mechanism | rec_picturex_0611__mechanical_timer_with_rotating_dial__001__png_43707496c3dc4b4ab4ac2ae5621a570e/rev_000001 | model.py:L161-L440 | accepted | Baseline source has only housing, dial, pointer and winding stem; no alert-control part or joint is present. |
| alert_control | bell_silence_lever | ① optional mechanism present | prismatic control | rec_0611_mechanical_timer_with_rotating_var_alert_control_bell_silence_lever/rev_000001 | model.py:L295-L300; model.py:L397-L471 | accepted | Fork intent targets alert_control; side mount and graspable lever add a Z-axis prismatic joint with 14 mm travel. |

## Semantic decisions

- Original 002's pedestal and original 003's long lower case are integral macro silhouettes. They
  remain coupled inside their respective body candidates, while their dial-axis and rear-plane
  interfaces are normalized so scale, winding, pointer and rear-support candidates can still vary.
- Numeral rendering is a sampled surface-detail parameter rather than a structural scale candidate:
  the robust block seven-segment style is retained alongside original 002's printed font outlines
  and original 003's slim instrument segments. It does not contribute to core/raw diversity.
- The timer always has a rotating dial and pointer. Those category-invariant mechanisms are assembly
  structure rather than diversity slots.
- There is no honest multiplicity axis in these sources. Repeated ticks, labels, feet, magnets and
  plug blades are fixed internal details, not template-level N.
- All accepted components can be sized from shared body/dial interfaces, so no compatibility gate is
  currently justified.
