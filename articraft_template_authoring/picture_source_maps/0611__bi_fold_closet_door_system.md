# 0611 / bi_fold_closet_door_system — template source map
status: converged — GATE P1 machine-pass; human variant inspection confirmed 2026-07-12
pattern: multiplicity + mixed (folding linear-chain per leaf, parallel leaf pairs, multiplicity over pairs)
parents: rec_picturex_0611__bi_fold_closet_door_system__001__png__airflex_batch_20260710_d5115d15e5854d6ba411c6bd534b3258 (picture/0611/bi_fold_closet_door_system/001.png)
canonical_baselines: (none minted yet; parent compiles OK, 11 non-fixed joints)
budget_note: 13 normal candidate anchors + 1 probe-only record; within the 12–18 rich budget.


## Subcategory Contract
- core_identity: a bi-fold closet door system — a top track/frame plus one or more two-panel (or multi-panel) leaves whose panels are coupled by center hinges and fold accordion-style, each leaf anchored by a jamb pivot.
- must_keep: [top track + framed opening, at least one bi-fold leaf pair, the coupled folding hinge chain of multiple coupled REVOLUTE joints (jamb pivot + >=1 center hinge), the folding motion]
- must_not_become: [sliding/bypass closet door (single translate panel), single swing door (one hinge/one panel), top-hung barn door (sliding slab)]
- image_evidence: full-height opening, two slim folded four-leaf packets, aluminum top U-track, warm-gray smooth slab leaves, built-in carcass with central shelf/drawer tower and a hanging bay.
- parent_evidence: frame root with U-track (track_web/track_lip_0/1) + jamb pivot sockets; two leaf pairs (left/right pivot_leaf + handle_leaf) coupled by center hinges; top rollers (left/right_guide) in the track; 5 interior drawers on prismatic slides.

## Slot Candidates
| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| panel_pair_count | 1 pair / 2 panels | N | forked_anchor | var_single_pair | pair0_pivot_leaf/handle_leaf, frame_to_pivot_0, center_hinge_0, guide_spin_0 | converged |
| panel_pair_count | 2 pairs / 4 panels | N | origin_anchor | parent | left/right pivot+handle leaves, frame_to_*_pivot, *_center_hinge | source-backed |
| panel_pair_count | 3 pairs / 6 panels | N | forked_anchor | var_triple_pair | loop pairK + mullion posts/sockets | converged |
| panel_pair_count | 4 pairs / 8 panels | N | forked_anchor | var_quad_pair | loop pairK + mullion posts/sockets | converged |
| panel_fold_topology | 2-panel bi-fold per leaf | ① | origin_anchor | parent | frame_to_left_pivot -> left_center_hinge | source-backed |
| panel_fold_topology | 3-panel multi-fold per leaf | ① | forked_anchor | var_trifold_leaf | +left_mid_leaf, +left_center_hinge_2 | converged |
| panel_face_construction | flat laminate slab | ③ | origin_anchor | parent | door_core + face_panel + stiles/rails | source-backed |
| panel_face_construction | raised / shaker panel | ③ | forked_anchor | var_raised_panel | raised_field_K within stile/rail frame | converged |
| panel_face_construction | louvered / slatted | ③ | forked_anchor | var_louvered | louver_slat_K (loop) within frame | converged |
| panel_face_construction | framed glass lite | ③ | forked_anchor | var_glass_lite | glass_field within stile/rail frame | converged |
| panel_face_construction | mirrored | ③ | forked_anchor | var_mirrored | mirror_field within stile/rail frame | converged |
| track_guide | top-only U-track | ① | origin_anchor | parent | track_web, track_lip_0/1, left/right_guide + guide_spin | source-backed |
| track_guide | top+bottom dual track | ① | forked_anchor | var_dual_track | +bottom_track_web/lip, +bottom guides + bottom_guide_spin | converged |
| track_guide | pivot-only (no roller) | ② | forked_anchor | var_pivot_only | remove left/right_guide + guide_spin; header rail only | converged |
| jamb_mount | pivot-pin-in-socket | ② | origin_anchor | parent | bottom/top_pivot_pin + *_bottom/top_socket | source-backed |
| jamb_mount | edge butt-hinge line | ② | forked_anchor | var_jamb_hinged | jamb_hinge_knuckle_K, frame_to_*_pivot axis at leaf edge | converged |
| load_path | bottom-supported pivot | ② | origin_anchor | parent | left/right_bottom_socket carries leaf | source-backed |
| load_path | top-hung pivot | ② | forked_anchor | var_top_hung | top_pivot_pin/socket load-bearing, bottom = guide pin | converged |
| body_base | built-in wardrobe carcass | ① | origin_anchor | parent | carcass_side_*, tower_partition_*, shelves, drawers | source-backed |
| body_base | plain framed opening | ① | forked_anchor | var_plain_frame | frame = sill+jambs+header+track only; drawers removed | converged |
| handle_grip | long vertical pull_bar | ④ | record_only | parent | pull_bar, pull_mount_0/1 | companion |
| handle_grip | round knob / recessed edge pull / none | ④ | record_only / world_knowledge_extrapolation | companion on any leaf anchor | pull_bar swap | companion |

## Multiplicity / Copy Logic
- PRIMARY: count_param = panel_pair_count (N leaf pairs)
  - N samples: 1 (var_single_pair), 2 (parent origin_anchor), 3 (var_triple_pair), 4 (var_quad_pair)
  - suggested N_range: 1–4 (up to ~6 for full-wall closets)
  - copied object: leaf pair = pivot_leaf + handle_leaf (built by _add_leaf_visuals) + its joints (frame_to_pivot_K revolute, center_hinge_K revolute, guide_spin_K continuous) + its jamb/mullion socket set + its roller guide
  - naming: pairK_pivot_leaf / pairK_handle_leaf / frame_to_pivot_K / center_hinge_K / guide_spin_K / guideK
  - placement: pairs tiled at pitch across OPENING_WIDTH, anchored to left jamb / mullion posts / right jamb, alternating fold direction
  - joint policy: each pair emits 1 jamb (or mullion) revolute + 1 center-hinge revolute + 1 continuous roller (a real coupled folding chain per pair)
  - NOTE: parent hand-writes the 4 leaves; multiplicity forks MUST refactor to loop-based emission with a shared helper and stable indexed names (§7).
- SECONDARY: count_param = LOUVER_SLAT_COUNT (louver slats per leaf) — gated on the louvered ③ face family
  - N samples: 10 / 16 / 22 (default set inside var_louvered; second N demonstrated by var_louver_slat_count probe)
  - suggested N_range: 8–28
  - copied object: louver_slat_K box; placement: even vertical pitch between top_rail and bottom_rail; joint policy: static visuals only (no joints)
- INTERIOR (record_only, not a door-identity anchor): DRAWER_COUNT = 5 (loop-emitted drawer_K + drawer_slide_K prismatic). N_range ~3–7; recorded but not forked because it belongs to the wardrobe fit-out, not the bi-fold door module.

## Six-Axis Diversity Record
| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / structural topology | source-backed | folding chain frame->pivot_leaf->handle_leaf->guide (parent); forks: trifold_leaf (2 center hinges/leaf), dual_track (2nd guide rail), plain_frame (base swap), panel_pair_count multiplicity |
| ② joint / mechanism type | source-backed | revolute jamb pivot + revolute center hinge + continuous roller + prismatic drawer (parent); forks: pivot_only (drop roller), jamb_hinged (edge butt hinge), top_hung (load path) |
| ③ primary form family | source-backed | flat laminate slab (parent); forks: raised_panel, louvered, glass_lite, mirrored |
| ④ surface decoration | record_only / world_knowledge_extrapolation | face_panel, near/far_stile, top/bottom_rail, hinge_strap/knuckle/receiver, pull_bar; louver slats (as surface), handle knob/recessed/none as host-conformal decoration |
| ⑤ proportion / size / travel | record_only | LEAF_SPAN 0.365, LEAF_HEIGHT 2.09, LEAF_THICKNESS 0.032, PIVOT_X 0.745, FOLDED_PIVOT_ANGLE 80deg, FOLDED_CENTER_ANGLE 160deg, DRAWER travel 0.34; ride-along only |
| ⑥ material / palette / finish | record_only | taupe_laminate/face/edge, brushed_aluminum, dark_hardware, guide_polymer, charcoal_interior, light_shelf/ivory_drawer; alt colorways (white paint, natural wood, frosted/clear glass, mirror) ride-along only |

## Compatibility Probes
| probe | record_id | combined axes | risk tested | result |
|---|---|---|---|---|
| louver_slat_count | rec_bi_fold_closet_door_system_var_louver_slat_count | louvered ③ face x louver-slat N | dense loop-emitted slats stay within stile/rail frame and clear meeting-stile hinge knuckles + roller when folded | converged |

## Blocked / Excluded
- half-height café / saloon bi-fold: excluded (⑤ proportion + drift toward café doors, not a closet system).
- asymmetric (one swing panel + one bi-fold pair): excluded (drifts toward single swing door; violates must_not_become).
- freestanding accordion room-divider with many panels and no closet frame: excluded (loses top-track/closet identity).
- drawer_count as a primary anchor: excluded from door-module forks (interior fit-out multiplicity only; recorded as record_only).

## GATE P1 Verification (machine)
- normal variants forked & accepted: 13 (all exit 0)
- compatibility probe-only variants: 1 (`rec_bi_fold_closet_door_system_var_louver_slat_count`)
- total synced source records after confirmation: 15 (1 origin + 13 normal variants + 1 probe-only variant)
- compile: ALL success
- articulation: every variant has >=1 non-fixed joint
- promotion: all workbench-only (dataset not in collections)
- binding: all bound to picture_category=0611 / picture_subcategory=bi_fold_closet_door_system, parent_record_id set (verified in data/index/subcat/0611__bi_fold_closet_door_system.jsonl)
- run_tests: every variant exports run_tests with axis-specific ctx.check/expect assertions (9-36 checks each)
- N-multiplicity axes verified to realize distinct counts (loop-emitted, stable indexed naming)
- human variant inspection: confirmed by user on 2026-07-12; downstream sync/spec/template stages may proceed.
