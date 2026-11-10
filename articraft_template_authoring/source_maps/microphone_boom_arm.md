# Microphone boom arm — SourceMap

export_category: microphone_boom_arm

The authoritative source pool is `<ARTI_SKILL_ROOT>/articraft_data/data/records`.
This map is semantic evidence only: it records exact `record/revision/model.py` spans and
does not copy source code or define a runtime closure.

sync_records:
  - rec_picturex_0611__microphone_boom_arm__001__png_40f72213fda046498d8240b2f25fc372
  - rec_picturex_0611__microphone_boom_arm__002__png_57c6553d3c90426287d7d05649c6d222
  - rec_picturex_0611__microphone_boom_arm__003__png_0696f40f5c9b438ca77c7ab59b5bf289
  - rec_picturex_0611__microphone_boom_arm__004__png_727d36bd44994666804b8c0ed0c101a8
  - rec_0611_microphone_boom_arm_var_arm_topology_low_profile_horizontal_bo
  - rec_0611_microphone_boom_arm_var_arm_topology_parallelogram_scissor_arm
  - rec_0611_microphone_boom_arm_var_arm_topology_three_link_articulated_ar
  - rec_0611_microphone_boom_arm_var_arm_topology_tubular_cantilever_arm
  - rec_0611_microphone_boom_arm_var_arm_topology_wall_swing_boom
  - rec_0611_microphone_boom_arm_var_base_mount_floor_stand_base
  - rec_0611_microphone_boom_arm_var_base_mount_grommet_mount
  - rec_0611_microphone_boom_arm_var_base_mount_wall_plate
  - rec_0611_microphone_boom_arm_var_base_mount_weighted_desktop_base
  - rec_0611_microphone_boom_arm_var_compensation_cable_counterweight
  - rec_0611_microphone_boom_arm_var_compensation_constant_force_spring
  - rec_0611_microphone_boom_arm_var_compensation_internal_gas_spring
  - rec_0611_microphone_boom_arm_var_compensation_torsion_spring_hinge
  - rec_0611_microphone_boom_arm_var_segment_count_3_boom_segments
  - rec_0611_microphone_boom_arm_var_segment_count_single_boom_segment

## Accepted three-slot candidates

| Slot | Candidate | Diversity axis | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| mechanism_family | folded_extension | ① topology + ② compensation | coupled box-link extension-spring boom | rec_picturex_0611__microphone_boom_arm__001__png_40f72213fda046498d8240b2f25fc372/rev_000001 | model.py:L26-L131; model.py:L134-L544; model.py:L547-L770 | accepted | Rounded lower/upper box links, fork cheeks, captured hinge pins, paired extension springs, cable guides and friction knobs. |
| mechanism_family | low_profile_extension | ① topology + ② compensation | coupled low-profile extension-spring boom | rec_0611_microphone_boom_arm_var_arm_topology_low_profile_horizontal_bo/rev_000001 | model.py:L28-L133; model.py:L136-L389; model.py:L439-L545 | accepted | Slim horizontal members, source-like forks, extension spring and cable-routing detail. |
| mechanism_family | wall_swing_torsion | ① topology + ② compensation | coupled wall-swing torsion boom | rec_0611_microphone_boom_arm_var_arm_topology_wall_swing_boom/rev_000001 | model.py:L29-L134; model.py:L137-L390; model.py:L440-L546 | accepted | Rising inboard link, long outboard boom, hinge-side torsion package and adjustment knobs. |
| mechanism_family | tubular_gas | ① topology + ② compensation | coupled tubular gas-strut boom | rec_0611_microphone_boom_arm_var_arm_topology_tubular_cantilever_arm/rev_000001 | model.py:L28-L155; model.py:L158-L355; model.py:L427-L528 | accepted | Twin tubular members, fork hubs, captured internal gas strut, guides and adjustment knobs. |
| mechanism_family | three_link_counterweight | ① topology + ② compensation | coupled three-link counterweight boom | rec_0611_microphone_boom_arm_var_arm_topology_three_link_articulated_ar/rev_000001 | model.py:L26-L116; model.py:L119-L385; model.py:L429-L538 | accepted | Three articulated links, routed cable and visible suspended counterweight. |
| mechanism_family | parallelogram_constant_force | ① topology + ② compensation | coupled parallelogram constant-force boom | rec_0611_microphone_boom_arm_var_arm_topology_parallelogram_scissor_arm/rev_000001 | model.py:L32-L145; model.py:L148-L397; model.py:L417-L559 | accepted | Paired rails, fork ends and twin constant-force spring paths. |
| base_mount | desk_clamp | ① load-bearing support | C-clamp support | rec_picturex_0611__microphone_boom_arm__004__png_727d36bd44994666804b8c0ed0c101a8/rev_000001 | model.py:L139-L264 | accepted | C-spine, jaws, rubber pad, captured screw, handle and swivel socket. |
| base_mount | weighted_desktop | ① load-bearing support | freestanding weighted support | rec_0611_microphone_boom_arm_var_base_mount_weighted_desktop_base/rev_000001 | model.py:L28-L46; model.py:L159-L212 | accepted | Broad weighted foot, stepped shell, rubber underside and top socket. |
| base_mount | grommet | ① load-bearing support | through-desk grommet support | rec_0611_microphone_boom_arm_var_base_mount_grommet_mount/rev_000001 | model.py:L28-L49; model.py:L159-L220 | accepted | Top flange, through-desk post, lower nut, tower and swivel socket. |
| base_mount | wall_plate | ① load-bearing support | wall-plate support | rec_0611_microphone_boom_arm_var_base_mount_wall_plate/rev_000001 | model.py:L31-L81; model.py:L194-L265 | accepted | Reinforced plate, four fasteners, cantilever and projected swivel socket. |
| base_mount | floor_stand | ① load-bearing support | floor support | rec_0611_microphone_boom_arm_var_base_mount_floor_stand_base/rev_000001 | model.py:L28-L47; model.py:L157-L216 | accepted | Wide weighted foot, tall riser, collar and top swivel socket. |
| terminal_mount | threaded_adapter | ① terminal interface | threaded microphone adapter | rec_picturex_0611__microphone_boom_arm__002__png_57c6553d3c90426287d7d05649c6d222/rev_000001 | model.py:L155-L426 | accepted | Wrist hub, friction knob, stepped collar and threaded microphone stud. |
| terminal_mount | studio_cradle | ① terminal interface | yoke-mounted studio microphone | rec_picturex_0611__microphone_boom_arm__003__png_0696f40f5c9b438ca77c7ab59b5bf289/rev_000001 | model.py:L120-L479 | accepted | Drop bracket, side yoke, pivot hardware and cylindrical studio microphone. |
| terminal_mount | shock_mount | ① terminal interface | elastic shock mount with pop filter | rec_picturex_0611__microphone_boom_arm__004__png_727d36bd44994666804b8c0ed0c101a8/rev_000001 | model.py:L387-L549 | accepted | Shock ring, elastomer struts, microphone, gooseneck and pop-filter interface. |

## Reviewed but not independent slots

These six variant records are retained in the source audit, but are intentionally rejected as
independent domain axes. Their compensation mechanisms are absorbed into the six structural
families, and their segment graphs are not homogeneous multiplicity.

| Slot | Candidate | Diversity axis | Source type | Record/Revision | Exact model.py:Lx-Ly | Status | Key parts/joints/helpers |
|---|---|---|---|---|---|---|---|
| compensation | cable_counterweight | ② mechanism-coupled evidence | rejected independent compensation | rec_0611_microphone_boom_arm_var_compensation_cable_counterweight/rev_000001 | model.py:L27-L142; model.py:L153-L520; model.py:L523-L765 | rejected — coupled into three_link_counterweight | Routed cable, counterweight eye and suspended weight are topology-dependent. |
| compensation | constant_force_spring | ② mechanism-coupled evidence | rejected independent compensation | rec_0611_microphone_boom_arm_var_compensation_constant_force_spring/rev_000001 | model.py:L32-L139; model.py:L151-L549 | rejected — coupled into parallelogram_constant_force | Twin spring rolls and rail anchors require the paired-rail topology. |
| compensation | internal_gas_spring | ② mechanism-coupled evidence | rejected independent compensation | rec_0611_microphone_boom_arm_var_compensation_internal_gas_spring/rev_000001 | model.py:L29-L152; model.py:L167-L544 | rejected — coupled into tubular_gas | Gas body and rod are captured by the tubular member spacing. |
| compensation | torsion_spring_hinge | ② mechanism-coupled evidence | rejected independent compensation | rec_0611_microphone_boom_arm_var_compensation_torsion_spring_hinge/rev_000001 | model.py:L28-L164; model.py:L178-L553 | rejected — coupled into wall_swing_torsion | Torsion coil anchors and cheek depth belong to the wall-swing hinge. |
| segment_graph | single_boom_segment | ① topology evidence | rejected segment_count axis | rec_0611_microphone_boom_arm_var_segment_count_single_boom_segment/rev_000001 | model.py:L27-L177; model.py:L194-L582 | rejected — fixed family topology | Single-segment joint graph is not N repetition. |
| segment_graph | three_boom_segments | ① topology evidence | rejected segment_count axis | rec_0611_microphone_boom_arm_var_segment_count_3_boom_segments/rev_000001 | model.py:L27-L167; model.py:L179-L549 | rejected — fixed family topology | Three-segment joint graph is represented by three_link_counterweight. |

## Locked domain and interfaces

- The runtime has exactly three independent slots: `mechanism_family` (6), `base_mount` (5),
  and `terminal_mount` (3). Therefore `core_domain = raw_domain = 6 × 5 × 3 = 90`.
- There is no `multiplicity`, no `segment_count`, no independent compensation slot, and no
  compatibility gate. Each mechanism candidate carries its matched compensation system.
- Every base provides one vertical swivel `AxisInterface`; each family consumes it and provides
  one wrist pitch `AxisInterface`; each terminal consumes that wrist axis.
- Base support surfaces are planar host interfaces with candidate-specific real extents in the
  TemplateDesign; they are not sampled as a fourth slot.
- Palette and bounded continuous scale parameters change proportion or finish only and do not
  contribute to core/raw structural diversity.
