# camp_chair — SourceMap

source_map_schema: 1
export_category: camp_chair
picture_category: Camping_Outdoor Gear
picture_subcategory: Camp chair
category_scope: Portable outdoor fabric or sling seats whose recognizable support is a foldable tube, pole, loop, scissor, or linked recliner frame; excludes rigid indoor chairs, non-seating cots, and unrelated patio furniture.

sync_records:
  - rec_camp_chair_var_bar_height
  - rec_camp_chair_var_bench_multi
  - rec_camp_chair_var_butterfly_sling
  - rec_camp_chair_var_director_frame
  - rec_camp_chair_var_flat_cot_lounger
  - rec_camp_chair_var_low_pole_hub
  - rec_camp_chair_var_moon_saucer
  - rec_camp_chair_var_probe_full_recliner
  - rec_camp_chair_var_recline_back
  - rec_camp_chair_var_rocker_base
  - rec_camp_chair_var_swivel_seat
  - rec_camp_chair_var_tripod_stool
  - rec_camp_chair_var_xframe_stool
  - rec_camp_chair_var_zero_gravity
  - rec_camping-outdoor-gear-camp-chair-001-png-use-the-_20260706_151429_784260_ff85d60d
  - rec_camping_outdoor_gear__camp_chair_da47f30a91aa4278b213ea8f9ebf9b93

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_camp_chair_var_bar_height/rev_000001 | reviewed | used | Tall quad-scissor host adds elongated legs and a captured front foot rail. |
| rec_camp_chair_var_bench_multi/rev_000001 | reviewed | reference_only | Repeated seat-bay evidence is retained for a later host-growth pass; the present template still fixes one seat bay. |
| rec_camp_chair_var_butterfly_sling/rev_000001 | reviewed | used | Two crossed closed tube loops and a corner-pocket sling form a complete one-pivot structural family. |
| rec_camp_chair_var_director_frame/rev_000001 | reviewed | used | Rigid rectangular side frames, paired transverse X braces, taut canvas, and wood arms form a complete director family. |
| rec_camp_chair_var_flat_cot_lounger/rev_000001 | reviewed | used | Near-coplanar sling seat/back and hinged foot section establish a low chaise structural family. |
| rec_camp_chair_var_low_pole_hub/rev_000001 | reviewed | used | Compact hub-and-pole frame with short shock-cord-style members is a distinct backpacking family, not merely a seat-height scalar. |
| rec_camp_chair_var_moon_saucer/rev_000001 | reviewed | used | Tilted circular rim, deep lathed bowl, and four raked rim-support legs define the saucer family. |
| rec_camp_chair_var_probe_full_recliner/rev_000001 | reviewed | reference_only | Probe of the origin-A recliner lineage; accepted chaise and linked-recliner evidence is represented by fuller sibling records. |
| rec_camp_chair_var_recline_back/rev_000001 | reviewed | used | Adds a captured lateral hinge carrying the full back frame on the quad-scissor host. |
| rec_camp_chair_var_rocker_base/rev_000001 | reviewed | used | Pair of curved fore-aft runner tubes replaces individual pad feet on the quad-scissor chair. |
| rec_camp_chair_var_swivel_seat/rev_000001 | reviewed | used | Raised bearing hub and continuous vertical-axis seat carrier establish a real swivel mechanism. |
| rec_camp_chair_var_tripod_stool/rev_000001 | reviewed | reference_only | Three radial legs and their tangent fold axes belong to a dedicated camp-stool topology rather than the chair template's scissor spine. |
| rec_camp_chair_var_xframe_stool/rev_000001 | reviewed | used | Backless fabric seat on the shared three-brace X frame supplies the compact stool family. |
| rec_camp_chair_var_zero_gravity/rev_000001 | reviewed | used | Coupled recline frame, seat, back, and foot section provide a complete zero-gravity linkage family. |
| rec_camping-outdoor-gear-camp-chair-001-png-use-the-_20260706_151429_784260_ff85d60d/rev_000001 | reviewed | used | Canonical padded quad-fold chair supplies the four-leg host, seat/back envelope, and three captured scissor pivots. |
| rec_camping_outdoor_gear__camp_chair_da47f30a91aa4278b213ea8f9ebf9b93/rev_000001 | reviewed | used | Canonical fabric lounge supplies the bent-tube base, sagged fabric panels, hinged armrests, and reclining foot section. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| structural_family | padded_quad_scissor | complete chair host | rec_camping-outdoor-gear-camp-chair-001-png-use-the-_20260706_151429_784260_ff85d60d/rev_000001 | model.py:L49-L221 | structure+motion | Four upright/raked corner members, perimeter rails, fabric envelope, and three captured scissor children form the canonical quad-fold topology. |
| structural_family | fabric_recliner_lounge | complete chair host | rec_camping_outdoor_gear__camp_chair_da47f30a91aa4278b213ea8f9ebf9b93/rev_000001 | model.py:L127-L518 | structure+motion | Bent-tube base, sagged seat/back meshes, independently folding legs and arm/foot sections define the lounge lineage. |
| structural_family | butterfly_loop_sling | complete chair host | rec_camp_chair_var_butterfly_sling/rev_000001 | model.py:L107-L337 | structure+motion | Two closed spline-tube loops cross at one lateral bolt and tension a four-pocket sling. |
| structural_family | director_rect_frame | complete chair host | rec_camp_chair_var_director_frame/rev_000001 | model.py:L41-L243 | structure+motion | Two rigid rectangular side frames are coupled by front/rear transverse X braces beneath taut canvas and hardwood arms. |
| structural_family | moon_saucer | complete chair host | rec_camp_chair_var_moon_saucer/rev_000001 | model.py:L50-L271 | structure+motion | Tilted torus rim and lathed bucket are carried directly by four raked legs with three scissor pivots. |
| structural_family | flat_cot_lounger | complete chair host | rec_camp_chair_var_flat_cot_lounger/rev_000001 | model.py:L127-L529 | structure+motion | Near-coplanar fabric seat, low back, hinged foot panel, and supporting bent-tube frame form a chaise-like chair mode. |
| structural_family | low_pole_hub | complete chair host | rec_camp_chair_var_low_pole_hub/rev_000001 | model.py:L48-L179 | structure+motion | Compact pole tips converge through a central hub and support a low ripstop sling with a single fold member. |
| structural_family | backless_x_stool | complete chair host | rec_camp_chair_var_xframe_stool/rev_000001 | model.py:L48-L193 | structure+motion | Backless padded sling removes back posts and arm structure while retaining the three-brace X-fold base. |
| structural_family | zero_gravity_linkage | complete chair host | rec_camp_chair_var_zero_gravity/rev_000001 | model.py:L134-L603 | structure+motion | A moving recline carrier parents seat, back, footrest, and arm links into the characteristic zero-gravity mechanism. |
| stance_module | rocker_runners | grounded support | rec_camp_chair_var_rocker_base/rev_000001 | model.py:L50-L253 | structure | Two curved spline-tube runners replace four isolated pads and alter the ground-contact path. |
| stance_module | bar_height_rail | grounded support | rec_camp_chair_var_bar_height/rev_000001 | model.py:L49-L230 | structure | Elongated quad legs and a captured front rail create a tall perch with a load-bearing foot support. |
| comfort_motion | captured_back_recline | moving back module | rec_camp_chair_var_recline_back/rev_000001 | model.py:L49-L272 | structure+motion | Full back posts and padded panel rotate together about a lateral captured hinge at the rear seat rail. |
| comfort_motion | swivel_bearing | moving seat module | rec_camp_chair_var_swivel_seat/rev_000001 | model.py:L64-L334 | structure+motion | Raised central bearing and radial spokes carry the seat on a continuous vertical-axis joint above the folding base. |
