# Manual grain mill 2 — SourceMap

export_category: manual_grain_mill2

The source pool is one rustic horizontal wooden trough mill and nine directed forks. The
authoritative category identity is a long open trough, a vertical grinding element centered in
the trough relief, paired bearing cheeks, a horizontal Y shaft, vertical bearing adjustment and
a detailed hand drive. Variants are mapped to six component slots; they are not complete-asset
family candidates. Host openings, bearing span, feed throat and discharge geometry are derived
from the selected grinding element so every declared slot combination remains legal.

sync_records:
  - rec_use-the-attached-reference-image-as-the-primary-_20260723_082608_013360_b2c00c51
  - rec_0611_manual_grain_mill2_var_arched_bearing_cheeks
  - rec_0611_manual_grain_mill2_var_feed_ramp_lipped
  - rec_0611_manual_grain_mill2_var_segmented_vertical_wheel
  - rec_0611_manual_grain_mill2_var_trough_side_rails
  - rec_0611_manual_grain_mill2_var_wheel_profile_dished
  - rec_0611_manual_grain_mill_var_drive_side_crank
  - rec_0611_manual_grain_mill_var_grinding_element_conical_burr_pair
  - rec_0611_manual_grain_mill_var_hopper_form_tapered
  - rec_0611_manual_grain_mill_var_outlet_side_spout

## Accepted component candidates

| Slot | Candidate | Diversity axis | Component type | Record/Revision | Exact model.py:Lx-Ly | Status | Key evidence |
|---|---|---|---|---|---|---|---|
| trough_body | open_straight_rails | ③ trough form | load-bearing trough | rec_use-the-attached-reference-image-as-the-primary-_20260723_082608_013360_b2c00c51/rev_000001 | model.py:L25-L127; model.py:L214-L233 | accepted source-backed | Long shallow floor, straight side rails, one closed feed end and a real central wheel relief. |
| trough_body | tapered_chamfered_rails | ③ trough form | load-bearing trough | rec_0611_manual_grain_mill2_var_trough_side_rails/rev_000001 | model.py:L21-L178; model.py:L266-L293 | accepted source-backed | Both rails share a longitudinal station profile with tapered height and chamfered hand-built edges. |
| trough_body | tapered_hopper_trough | ③ inlet/body form | load-bearing trough with hopper | rec_0611_manual_grain_mill_var_hopper_form_tapered/rev_000001 | model.py:L21-L273; model.py:L330-L403 | accepted source-backed | Hollow tapered timber hopper, broad rim and open throat are retained above the same long trough and shaft line. |
| feed_path | shallow_plain_ramp | ③ feed interface | feed ramp | rec_use-the-attached-reference-image-as-the-primary-_20260723_082608_013360_b2c00c51/rev_000001 | model.py:L50-L63; model.py:L116-L127 | accepted source-backed | Broad low triangular ramp routes grain toward the centered grinding bed. |
| feed_path | narrowing_lipped_tray | ③ feed interface | lipped feed tray | rec_0611_manual_grain_mill2_var_feed_ramp_lipped/rev_000001 | model.py:L47-L211; model.py:L298-L329 | accepted source-backed | Open sloped floor, paired low lips and a narrowed throat are derived from one feed descriptor. |
| outlet | open_end_discharge | ③ outlet interface | trough discharge | rec_use-the-attached-reference-image-as-the-primary-_20260723_082608_013360_b2c00c51/rev_000001 | model.py:L25-L127; model.py:L226-L233 | accepted source-backed | Source trough remains open beyond the grinding bed and uses a short supported meal ramp. |
| outlet | side_spout_tray | ③ outlet interface | side spout and catch tray | rec_0611_manual_grain_mill_var_outlet_side_spout/rev_000001 | model.py:L21-L319; model.py:L414-L445 | accepted source-backed | A real side-wall opening, flanged sloped channel, braces and open collection tray share one outlet descriptor. |
| grinding_element | plain_vertical_stone | ③ grinding form | rotating vertical wheel | rec_use-the-attached-reference-image-as-the-primary-_20260723_082608_013360_b2c00c51/rev_000001 | model.py:L20-L22; model.py:L155-L164; model.py:L248-L277 | accepted source-backed | Thick chamfered vertical wheel and integral horizontal axle occupy the trough centerline. |
| grinding_element | dished_wooden_wheel | ③ grinding form | rotating vertical wheel | rec_0611_manual_grain_mill2_var_wheel_profile_dished/rev_000001 | model.py:L20-L43; model.py:L172-L221; model.py:L303-L332 | accepted source-backed | Revolved recessed faces, raised working rim, hub seat and axle bore form one continuous wheel. |
| grinding_element | sloped_dished_wheel | ③ grinding form | rotating vertical wheel | rec_0611_manual_grain_mill2_var_wheel_profile_dished/rev_000001 | model.py:L20-L43; model.py:L172-L221; model.py:L303-L332 | accepted source-derived | The source dished-wheel family is adapted to one continuous conical runner: a smaller circular end transitions through a sloped wall to a larger circular grinding face, with no neighboring box and the runner remaining vertical on the horizontal axle. |
| grinding_element | segmented_vertical_stone | ③ grinding construction | rotating vertical wheel | rec_0611_manual_grain_mill2_var_segmented_vertical_wheel/rev_000001 | model.py:L20-L23; model.py:L156-L194; model.py:L278-L310 | accepted source-backed | Shallow radial face joints produce twelve readable segments while retaining a continuous structural core. |
| grinding_element | conical_burr_pair | ③ grinding form | coaxial rotor/stator burr pair | rec_0611_manual_grain_mill_var_grinding_element_conical_burr_pair/rev_000001 | model.py:L16-L327; model.py:L346-L509 | accepted source-backed | Male rotor and supported female stator share a Y axis, radial clearance, hub seat, feed throat and conformal bed opening. |
| bearing_cheeks | straight_slotted_cheeks | ① support profile | paired axle supports | rec_use-the-attached-reference-image-as-the-primary-_20260723_082608_013360_b2c00c51/rev_000001 | model.py:L65-L152; model.py:L235-L246 | accepted source-backed | Straight front bored cheek plus open rear sliding guide support the same horizontal shaft from both sides. |
| bearing_cheeks | arched_paired_cheeks | ① support profile | paired axle supports | rec_0611_manual_grain_mill2_var_arched_bearing_cheeks/rev_000001 | model.py:L21-L214; model.py:L246-L279 | accepted source-backed | Congruent arched cheek crowns, real bores, broad feet and a rear carriage opening share one descriptor. |
| drive | straight_axial_grip | ③ hand-drive form | coaxial free-spinning grip | rec_use-the-attached-reference-image-as-the-primary-_20260723_082608_013360_b2c00c51/rev_000001 | model.py:L167-L182; model.py:L279-L331 | accepted source-backed | Source-like tapered bored wooden dowel is carried on the protruding horizontal shaft pin. |
| drive | offset_side_crank | ③ hand-drive form | crank arm and free-spinning grip | rec_0611_manual_grain_mill_var_drive_side_crank/rev_000001 | model.py:L167-L198; model.py:L289-L371 | accepted source-backed | Rounded steel crank arm, side hub, offset pin, tapered bored grip and parallel grip axis form a complete hand drive. |

## Parameters and derived host adaptation

- `trough_length_m = 0.52–0.66 m` and `trough_width_m = 0.16–0.20 m` preserve the long,
  shallow source proportions. Rail stations, floor, end wall and outlet support derive from them.
- `grinding_radius_m = 0.118–0.145 m` changes the real vertical grinding envelope. Wheel relief,
  feed throat, grinding bed, bearing height and hopper throat clearance derive from this value.
- `adjustment_travel_m = 0.004–0.008 m` controls the real Z-prismatic bearing travel while slot
  height and top bridge clearance are derived from the same travel.
- `grip_length_m = 0.12–0.17 m` applies to both hand-drive candidates.
- `crank_throw_m = 0.085–0.115 m` applies only to `offset_side_crank`; arm, pin and swept radial
  clearance derive from it.

## Assembly and category identity

- The joint chain is always `mill_body -> adjustable_bearing` (Z prismatic),
  `adjustable_bearing -> grinding_shaft` (Y continuous), and
  `grinding_shaft -> hand_grip` (Y continuous).
- All three joints use explicit axis interfaces. The axle passes through actual oversized bores;
  the rear bearing slides inside a real open guide; the grip surrounds a real undersized pin bore.
  No overlap or isolated-part allowance is permitted.
- The grinding element remains centered between two cheeks and inside the trough wheel/burr relief.
  The outlet is opposite or axially clear of the hand drive, and the complete offset crank sweep
  stays outside the cheek and rail planes.

## Rejected constructions

- Complete source assets as candidates in one family slot, a wheel outside the trough, one-sided
  or floating shaft support, solid cheeks without bores, solid feed/outlet blocks and simplified
  box-and-cylinder placeholder drives are rejected.
- Any use of `allow_overlap` or `allow_isolated_part` is rejected for this template.
