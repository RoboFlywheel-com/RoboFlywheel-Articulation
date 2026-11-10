# Mechanical metronome with pendulum — SourceMap

export_category: mechanical_metronome_with_pendulum

Authoritative records live under
`<ARTI_SKILL_ROOT>/arti-template/data/records`. All directed variants preserve the same
mechanical interface: a wood case with an inset tempo scale, a visible upper pendulum rod,
one or two sliding tempo weights and a side winding key. Case, cover, tempo module, key,
handle and base variants are therefore compatible slots, with host dimensions and mount points
derived from the selected case and pendulum length.

sync_records:
  - rec_picturex_0611__mechanical_metronome_with_pendulum__001__png_93052d21a09e44f59a0309e028d26892
  - rec_0611_mechanical_metronome_with_pend_var_case_form_pyramid
  - rec_0611_mechanical_metronome_with_pend_var_case_form_rectangular
  - rec_0611_mechanical_metronome_with_pend_var_case_form_arched
  - rec_0611_mechanical_metronome_with_pend_var_front_closure_hinged_cover
  - rec_0611_mechanical_metronome_with_pend_var_tempo_module_bell_beat_slider
  - rec_0611_mechanical_metronome_with_pend_var_tempo_module_dual_weights
  - rec_0611_mechanical_metronome_with_pend_var_winding_folding_side_key
  - rec_0611_mechanical_metronome_with_pend_var_handle_swing_carry_handle
  - rec_0611_mechanical_metronome_with_pend_var_base_leveling_foot

## Accepted component candidates

| Slot | Candidate | Record/Revision | Exact model.py:Lx-Ly | Key evidence |
|---|---|---|---|---|
| case_form | pyramid_case | rec_0611_mechanical_metronome_with_pend_var_case_form_pyramid/rev_000001 | model.py:L21-L79; model.py:L82-L453 | continuous tapered X/Z shell, narrow crown and broad lower spring cover |
| case_form | rectangular_case | rec_0611_mechanical_metronome_with_pend_var_case_form_rectangular/rev_000001 | model.py:L21-L46; model.py:L49-L392 | straight-sided cabinet while retaining scale, pivot and key interfaces |
| case_form | arched_case | rec_0611_mechanical_metronome_with_pend_var_case_form_arched/rev_000001 | model.py:L21-L46; model.py:L49-L417 | continuous vertical body and rounded crown |
| front_closure | open_scale | rec_picturex_0611__mechanical_metronome_with_pendulum__001__png_93052d21a09e44f59a0309e028d26892/rev_000001 | model.py:L49-L402 | exposed inset black scale and lower bezel |
| front_closure | hinged_cover | rec_0611_mechanical_metronome_with_pend_var_front_closure_hinged_cover/rev_000001 | model.py:L49-L421 | framed transparent front leaf on a real lower X hinge |
| tempo_module | plain_slider | rec_picturex_0611__mechanical_metronome_with_pendulum__001__png_93052d21a09e44f59a0309e028d26892/rev_000001 | model.py:L49-L402 | bored ivory friction-fit tempo collar |
| tempo_module | bell_beat_slider | rec_0611_mechanical_metronome_with_pend_var_tempo_module_bell_beat_slider/rev_000001 | model.py:L49-L430 | wider indexed collar with structural detents and beat selector |
| winding_system | fixed_side_key | rec_picturex_0611__mechanical_metronome_with_pendulum__001__png_93052d21a09e028d26892/rev_000001 | model.py:L49-L402 | side shaft and annular bow turn on case X axis |
| winding_system | folding_side_key | rec_0611_mechanical_metronome_with_pend_var_winding_folding_side_key/rev_000001 | model.py:L49-L433 | turning hub plus separately hinged folding leaf |
| carry_handle | no_handle | rec_picturex_0611__mechanical_metronome_with_pendulum__001__png_93052d21a09e028d26892/rev_000001 | model.py:L49-L402 | uninterrupted source crown cap |
| carry_handle | swing_handle | rec_0611_mechanical_metronome_with_pend_var_handle_swing_carry_handle/rev_000001 | model.py:L49-L497 | two captured handle legs and a real X-axis swing |
| base_support | flat_plinth | rec_picturex_0611__mechanical_metronome_with_pendulum__001__png_93052d21a09e028d26892/rev_000001 | model.py:L49-L402 | broad weighted wood plinth and rubber underside |
| base_support | leveling_feet | rec_0611_mechanical_metronome_with_pend_var_base_leveling_foot/rev_000001 | model.py:L49-L454 | raised plinth with four distinct rubber leveling feet |

## Multiplicity

- `tempo_weight_count = 1 | 2`, applied to `tempo_module`.
- The dual-weight source record is
  `rec_0611_mechanical_metronome_with_pend_var_tempo_module_dual_weights/rev_000001`
  (`model.py:L21-L419`).
- N creates exactly N bored tempo-weight parts and N independent prismatic joints on the same
  visible pendulum rod. Starting positions and travel are derived from N and rod length so the
  collars remain separated.

## Parameters and host derivation

- `pendulum_length_m = 0.26–0.36 m` controls the visible source-style upper rod. Case height,
  shoulder/crown profile, scale endpoints, pivot height, slider start positions and slider travel
  derive from it.
- `swing_limit_rad = 0.28–0.50 rad` controls the real Y-axis pendulum joint limits.
- Closure hinge, winding key, top handle and base mounts derive from selected case width, depth,
  height and front plane; they are not placed with topology-independent constants.

## Category identity

- Exactly one `case_body`, one `pendulum`, one `winding_key` and N `tempo_weight` parts.
- The case must have a continuous manufactured silhouette, inset tapered scale, tempo marks and
  annular pivot bearing.
- The visible rod extends upward from the lower escapement pivot as in the source; it is not a
  floor-lamp-like pole with a decorative ball at the bottom.
- Every weight is captured on the rod by a prismatic joint; the side key turns about X and the
  pendulum swings about Y.

## Rejected constructions

- Stacked box courses standing in for the tapered case, a pendulum hanging below the case, fake
  weights detached from the rod and material-only case variants are rejected.
- Accessory combinations remain allowed only because all source variants share the same derived
  case interfaces; no independent accessory may ignore the selected host dimensions.
