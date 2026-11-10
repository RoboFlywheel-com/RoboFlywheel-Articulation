# door_other — SourceMap

source_map_schema: 1
export_category: door_other
picture_category: Door
picture_subcategory: Other
category_scope: other single doors and stable/arched door assemblies with a standing frame, at least one real leaf motion, and visible leaf hardware.

sync_records:
  - rec_door_dutch
  - rec_door_other_arched
  - rec_door_other_var_centerpivot
  - rec_door_other_var_levered_panel
  - rec_door_other_var_louvered
  - rec_door_other_var_plankcount
  - rec_door_other_var_plankcount_three
  - rec_door_other_var_porthole
  - rec_door_other_var_roundtop
  - rec_door_other_var_segmental

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_door_dutch/rev_000001 | reviewed | used | Parent Dutch/stable door: two independently swinging leaves and rectangular wood casing. |
| rec_door_other_arched/rev_000001 | reviewed | used | Parent rustic arched plank door: jamb-edge leaf revolute, stone surround, strap hardware and ring pull. |
| rec_door_other_var_centerpivot/rev_000001 | reviewed | used | Adds a centerline pivot spine with top/bottom socket cups. |
| rec_door_other_var_levered_panel/rev_000001 | reviewed | used | Dutch-shell solid raised-panel infill and lever hardware. |
| rec_door_other_var_louvered/rev_000001 | reviewed | used | Dutch-shell louver frame and loop-emitted slat multiplicity. |
| rec_door_other_var_plankcount/rev_000001 | reviewed | used | Arched-shell individual plank loop and count-general copy logic. |
| rec_door_other_var_plankcount_three/rev_000001 | reviewed | reference_only | Arched-shell low-N plank evidence (three boards); retained as N evidence, while the count-general loop source is used. |
| rec_door_other_var_porthole/rev_000001 | reviewed | used | Flat-top leaf with circular porthole glass, muntin ring and ring pull. |
| rec_door_other_var_roundtop/rev_000001 | reviewed | used | Broad barn-segmental head profile. |
| rec_door_other_var_segmental/rev_000001 | reviewed | used | Shallow segmental head profile and concentric opening adaptation. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| split_mechanism | dutch_two_leaf | articulated shell | rec_door_dutch/rev_000001 | model.py:L230-L426 | structure+motion | two independent vertical-Z revolutes on upper/lower leaves |
| split_mechanism | single_solid_leaf | articulated shell | rec_door_other_arched/rev_000001 | model.py:L361-L452 | structure+motion | one jamb-edge vertical revolute plus optional ring-pull revolute |
| split_mechanism | center_pivot | articulated shell | rec_door_other_var_centerpivot/rev_000001 | model.py:L404-L492 | structure+motion | centerline vertical revolute with top/bottom pivot sockets |
| head_profile | flat_square | host profile | rec_door_dutch/rev_000001 | model.py:L245-L316 | structure | rectangular casing head |
| head_profile | full_semicircle | leaf/frame profile | rec_door_other_arched/rev_000001 | model.py:L105-L155,L277-L361 | structure | true semicircular leaf and opening |
| head_profile | broad_barn_segmental | leaf/frame profile | rec_door_other_var_roundtop/rev_000001 | model.py:L105-L155,L277-L361 | structure | low-rise broad segmental top |
| head_profile | shallow_segmental | leaf/frame profile | rec_door_other_var_segmental/rev_000001 | model.py:L105-L155,L277-L361 | structure | very low-rise segmental top |
| head_profile | flat_top_rect | host profile | rec_door_other_var_porthole/rev_000001 | model.py:L115-L146,L334-L379 | structure | flat leaf under arched surround |
| leaf_infill | glazed_lite | leaf face | rec_door_dutch/rev_000001 | model.py:L317-L345 | structure | glazed upper leaf with muntin grid |
| leaf_infill | solid_panel | leaf face/hardware | rec_door_other_var_levered_panel/rev_000001 | model.py:L308-L375 | structure | raised panels on both leaves plus lever |
| leaf_infill | louvered | leaf face/multiplicity | rec_door_other_var_louvered/rev_000001 | model.py:L283-L376 | structure | slatted vent with loop-emitted slats |
| leaf_infill | plank_strap | leaf face/hardware | rec_door_other_arched/rev_000001 | model.py:L371-L418 | structure | vertical planks, battens, straps and ring |
| leaf_infill | porthole | leaf face/hardware | rec_door_other_var_porthole/rev_000001 | model.py:L444-L490 | structure | circular through-light with muntin ring |
| multiplicity | plank_count | repeated leaf boards | rec_door_other_var_plankcount/rev_000001 | model.py:L397-L412 | structure | individual plank_{i} visuals |
| multiplicity | lite_grid | repeated glazing | rec_door_dutch/rev_000001 | model.py:L317-L345 | structure | muntin grid |
| multiplicity | louver_slat_count | repeated louver slats | rec_door_other_var_louvered/rev_000001 | model.py:L283-L319 | structure | slat_{i} loop |
