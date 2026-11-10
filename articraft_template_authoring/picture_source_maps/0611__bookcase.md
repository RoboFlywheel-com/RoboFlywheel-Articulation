# 0611 / bookcase — template source map
status: converged — GATE P1 machine-pass; human variant inspection confirmed 2026-07-12
pattern: mixed (parallel_children doors/drawers + multiplicity shelves/bays/cubes)
parents:
- B1 rec_picturex_0611__bookcase__001__png__airflex_batch_20260710_9a0ee60395414b908c36814fa8c3e19a — picture/0611/bookcase/001.png (rectangular upright, full glass swing-doors over 6-shelf/bay open shelving, scalloped plinth, solid back; 2 joints)
- B2 rec_picturex_0611__bookcase__002__png__airflex_batch_20260710_d41a0a504a6449e792d71920814a0a92 — picture/0611/bookcase/002.png (rectangular upright, upper full-glass doors + 2 base drawers, 3 shelves; 4 joints)
- B3 rec_picturex_0611__bookcase__003__png__airflex_batch_20260710_9b1b91d9bff944029cc5e17122776e99 — picture/0611/bookcase/003.png (two-tier stacked hutch: arched glass doors top + solid panel doors base, 2 display shelves; 4 joints)
- B4 rec_picturex_0611__bookcase__004__png__airflex_batch_20260710_70016f2ca9054566885bb677d66ede1a — picture/0611/bookcase/004.png (arched-bonnet glazed highboy on turned legs, 3 shelves + 3 base drawers; 5 joints)
- B5 rec_picturex_0611__bookcase__005__png__airflex_batch_20260710_0cd3f4059b0b427ca0e827e61b6ac299 — picture/0611/bookcase/005.png (rectangular upright display, upper glass doors + 3 base drawers, 3 shelves, legs; 5 joints)
- B6 rec_picturex_0611__bookcase__006__png__airflex_batch_20260710_ef98d8962cc245f8a0ae664ac6b94981 — picture/0611/bookcase/006.png (three-bay grid glazed hutch, 3 upper glass + 3 drawers + 3 lower panel doors, 3 shelves/bay, legs; 9 joints)
canonical_baselines: none
underfilled_reason: none — 6 origins + 14 converged forks = 20 candidate anchors (rich class within budget)

## Subcategory Contract
- core_identity: a free-standing case of vertical side supports carrying a stack of horizontal shelves that store books.
- must_keep: vertical side supports; a stack of book shelves; at least one real non-fixed joint (door revolute / drawer or shelf prismatic).
- must_not_become: wardrobe; sideboard; display cabinet with no shelving; nightstand.
- image_evidence: open glazed shelving (001), glass-door + drawers (002/005), two-tier hutch (003), arched legged glazed case (004), three-bay grid hutch (006).
- parent_evidence: loop-emitted shelf boards (SHELF_Z / shelf_{index} / display_shelf_{index} / upper_shelf_{index}); revolute glazed doors; prismatic drawers; bay partitions.

## Slot Candidates
| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| carcass_form | rectangular upright | ③ | origin_anchor | B1/B2/B5 | carcass, side_panel_*, center_divider | present |
| carcass_form | two-tier stacked hutch | ③ | origin_anchor | B3 | upper+lower carcass, upper/lower doors | present |
| carcass_form | arched-bonnet legged highboy | ③ | origin_anchor | B4 | front_arch/roof_shell, _turned_leg | present |
| carcass_form | three-bay grid hutch | ③ | origin_anchor | B6 | upper_partition_{index}, per-bay modules | present |
| carcass_form | ladder / leaning trapezoid | ③ | forked_anchor | rec_bookcase_var_ladder (from B4) | raked side supports, tapered shelves | converged |
| carcass_form | corner L-plan | ③ | forked_anchor | rec_bookcase_var_corner (from B5) | L side panels, corner shelves | converged |
| carcass_form | cube-grid matrix | ③ | forked_anchor | rec_bookcase_var_cube_grid (from B6) | cube_{row}_{col}, nested loop | converged |
| carcass_form | barrister stacked sections | ③ | forked_anchor | rec_bookcase_var_barrister (from B1) | section_{i}, per-section glass door | converged |
| door_or_open | full glass swing doors | ② | origin_anchor | B1 | door_0/1, carcass_to_door_* revolute | present |
| door_or_open | upper glass + base drawers | ② | origin_anchor | B2/B5 | door_*, drawer_*, prismatic | present |
| door_or_open | glass top + solid panel base doors | ② | origin_anchor | B3/B6 | upper_door_*, lower_door_* revolute | present |
| door_or_open | fully open shelving | ② | forked_anchor | rec_bookcase_var_open_shelving (from B2) | shelves exposed, base drawer joint | converged |
| door_or_open | open shelves + base cabinet doors | ② | forked_anchor | rec_bookcase_var_base_cabinet_doors (from B2) | base_door_0/1 revolute | converged |
| door_or_open | barrister flip-up glass | ② | forked_anchor | rec_bookcase_var_flip_up_glass (from B1) | top-pivot horizontal-axis revolute | converged |
| shelf_mechanism | fixed shelves | ② | origin_anchor | all origins | shelf boards fixed to carcass | present |
| shelf_mechanism | adjustable prismatic shelves | ② | forked_anchor | rec_bookcase_var_adjustable_shelves (from B5) | display_shelf_{index} + prismatic | converged |
| shelf_count (N) | 3 shelves | N | origin_anchor / forked_anchor | B2/B5; rec_bookcase_var_shelves_n3 | display_shelf_{index} loop | present/converged |
| shelf_count (N) | 5 shelves | N | forked_anchor | rec_bookcase_var_shelves_n5 (from B5) | display_shelf_{index} loop | converged |
| shelf_count (N) | 6-7 shelves | N | origin_anchor / forked_anchor | B1 (6/bay); rec_bookcase_var_shelves_n7 | shelf loop | present/converged |
| shelf_count (N) | 2 shelves | N | origin_anchor | B3 | display_shelf_0/1 | present |
| base | plinth | ③ | origin_anchor / forked_anchor | B1; rec_bookcase_var_plinth_base (from B5) | front_apron / plinth block | present/converged |
| base | legs / turned legs | ③ | origin_anchor | B4/B5/B6 | _turned_leg, leg_{ix}_{iy} | present |
| base | recessed toe-kick | ③ | forked_anchor | rec_bookcase_var_toe_kick_base (from B2) | setback base rail | converged |
| bay_count (N) | 2 bays | N secondary | origin_anchor | B1 | bay_centers | present |
| bay_count (N) | 3 bays | N secondary | origin_anchor | B6 | upper_partition_{index} | present |
| bay_count (N) | 4 bays | N secondary | forked_anchor | rec_bookcase_var_bay_grid_n4 (from B6) | bay module loop *_0.._3 | converged |
| back_panel | solid | ④ | origin_anchor / record_only | B1/B4 | back_panel | present |
| back_panel | open (no back) | ④ | origin_anchor / record_only | B6 right bay | upper_back_2 omitted | present |
| back_panel | beadboard | ④ | world_knowledge_extrapolation | host-conformal surface only | — | record_only |

## Multiplicity / Copy Logic
- count_param: shelf_count (primary), bay_count (secondary), cube cells (rows x cols), barrister sections
- N samples (shelves): 2 (B3), 3 (B2/B5/var_n3), 5 (var_n5), 6 (B1/bay), 7 (var_n7)
- suggested N_range: shelves 2–8; bays 1–5; cube grid up to ~4x4
- copied object / naming / placement / joint policy:
  - shelves: copied_object=shelf board; naming=display_shelf_{index}/shelf_{index}; placement=even vertical spacing; joint_policy=fixed to carcass (or per-shelf prismatic in var_adjustable_shelves)
  - bays: copied_object=bay module (partition+shelves+door+drawer); naming=*_{index}; placement=even horizontal grid; joint_policy=one revolute+one prismatic per bay
  - cubes: copied_object=cube cell; naming=cube_{row}_{col}; placement=grid; joint_policy=open, one representative door revolute
  - barrister: copied_object=stacked section; naming=section_{i}; placement=vertical stack; joint_policy=one revolute glass door per section

## Six-Axis Diversity Record
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / structural topology | source-backed | single upright case; two-tier stack (B3); legged highboy (B4); multi-bay grid (B6); ladder trapezoid, corner L-plan, cube grid, barrister stack (forks) |
| ② joint / mechanism type | source-backed | vertical-swing revolute glass/panel doors; prismatic drawers; top-pivot flip-up glass (fork); prismatic adjustable shelves (fork); fully-open (fork) |
| ③ primary form family | source-backed | rectangular upright / two-tier hutch / arched legged / grid hutch / ladder / corner / cube-grid / barrister |
| ④ surface decoration | record_only / world_knowledge_extrapolation | carved rosettes & pierced arch frames (B1), fielded panels, glazing muntins, beadboard back (extrapolation) — host-conformal only |
| ⑤ proportion / size / travel | record_only | width 1.0–1.55 m, depth 0.42–0.57 m, height 2.1–2.29 m; door swing ~1.55–1.85 rad; drawer travel ~0.22–0.27 m; shelf pitch ~0.20–0.32 m |
| ⑥ material / palette / finish | record_only | warm/dark walnut, mahogany, charcoal painted, gray oak laminate, black; sage/green-tinted/smoked/clear glazing; brass/bronze hardware |

## Compatibility Probes
| probe | record_id | combined axes | risk tested | result |
|---|---|---|---|---|
| corner door swing | rec_bookcase_var_corner | ③ corner + revolute door | diagonal door clears both L wings when open | converged |
| flip-up glass arc | rec_bookcase_var_flip_up_glass | ② top-pivot + full shelf stack | lifted door clears shelf edges/books through arc | converged |
| adjustable shelf vs door | rec_bookcase_var_adjustable_shelves | ② prismatic shelves + closed glass doors | shelf vertical travel does not collide with door frame | converged |

## Blocked / Excluded
- pure open bookcase with no articulation at all: excluded — violates non-fixed-joint rule; realized instead as var_open_shelving (retains base drawer) and var_adjustable_shelves (prismatic shelves).
- sideboard / wardrobe / doored display cabinet with no shelving: out of category (must_not_become).

## GATE P1 Verification (machine)
- normal variants forked & accepted: 14 (all exit 0)
- compatibility probes reuse normal variant records: 3 (`rec_bookcase_var_corner`, `rec_bookcase_var_flip_up_glass`, `rec_bookcase_var_adjustable_shelves`)
- compatibility probe-only variants: 0
- total synced source records after confirmation: 20 (6 origins + 14 normal variants)
- compile: ALL success
- articulation: every variant has >=1 non-fixed joint
- promotion: all workbench-only (dataset not in collections)
- binding: all bound to picture_category=0611 / picture_subcategory=bookcase, parent_record_id set (verified in data/index/subcat/0611__bookcase.jsonl)
- run_tests: every variant exports run_tests with axis-specific ctx.check/expect assertions (9-36 checks each)
- N-multiplicity axes verified to realize distinct counts (loop-emitted, stable indexed naming)
- human variant inspection: confirmed by user on 2026-07-12; downstream sync/spec/template stages may proceed.
