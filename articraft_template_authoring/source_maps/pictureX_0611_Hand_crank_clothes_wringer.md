# pictureX_0611_Hand_crank_clothes_wringer — SourceMap

source_map_schema: 1
export_category: pictureX_0611_Hand_crank_clothes_wringer
picture_category: 0611
picture_subcategory: Hand-crank_clothes_wringer
category_scope: Hand-cranked laundry wringers built around a rigid frame, a hand-driven horizontal roller nip, pressure adjustment over the moving bearing carrier, and a real bench, floor, or wall mounting structure; powered mangles, pasta makers, rolling mills, and printing presses are outside scope.

sync_records:
  - rec_picturex0611_hand_crank_clothes_wringer_fork_dual_handwheel_pressure_20260714
  - rec_picturex0611_hand_crank_clothes_wringer_fork_exposed_twin_gear_drive_20260713
  - rec_picturex0611_hand_crank_clothes_wringer_fork_fold_down_feed_shelf_20260714
  - rec_picturex0611_hand_crank_clothes_wringer_fork_folding_crank_handle_20260714
  - rec_picturex0611_hand_crank_clothes_wringer_fork_freestanding_floor_frame_20260713
  - rec_picturex0611_hand_crank_clothes_wringer_fork_pressure_screw_bridge_20260713
  - rec_picturex0611_hand_crank_clothes_wringer_fork_spring_loaded_bridge_20260713
  - rec_picturex0611_hand_crank_clothes_wringer_fork_table_clamp_frame_20260713
  - rec_picturex0611_hand_crank_clothes_wringer_fork_three_roller_feed_path_20260713
  - rec_picturex0611_hand_crank_clothes_wringer_fork_wall_bench_bracket_20260713
  - rec_picturex_0611__hand_crank_clothes_wringer__001__png_528e7f40341c4a72899b19b423e8248b

## Source review

| Record/Revision | Review status | Decision | Note |
|---|---|---|---|
| rec_picturex_0611__hand_crank_clothes_wringer__001__png_528e7f40341c4a72899b19b423e8248b/rev_000001 | reviewed | used | Origin host supplies the classic boss-mounted screw clamps, fixed bent crank, plain front apron, central pressure screw, twin rollers, exposed gears, and the journalled drive chain. |
| rec_picturex0611_hand_crank_clothes_wringer_fork_table_clamp_frame_20260713/rev_000001 | reviewed | used | Reinforced bench clamp family with deep jaw brackets, triangular gussets, threaded bushings, detailed screws, pads, and handles. |
| rec_picturex0611_hand_crank_clothes_wringer_fork_freestanding_floor_frame_20260713/rev_000001 | reviewed | used | Freestanding support family with four tall legs, base crosses, foot bars, cross braces, and floor pads. |
| rec_picturex0611_hand_crank_clothes_wringer_fork_wall_bench_bracket_20260713/rev_000001 | reviewed | used | Rear mounting-plate family with four wall bolts and two triangular side gussets. |
| rec_picturex0611_hand_crank_clothes_wringer_fork_pressure_screw_bridge_20260713/rev_000001 | reviewed | used | Overhead screw-yoke family with bridge posts, gussets, crossbar, bushing, knurled screw, pressure bar, and twin screw pads. |
| rec_picturex0611_hand_crank_clothes_wringer_fork_spring_loaded_bridge_20260713/rev_000001 | reviewed | used | Spring bridge family with paired guide posts, anchors, helical compression springs, and spring seats over the moving bearing blocks. |
| rec_picturex0611_hand_crank_clothes_wringer_fork_dual_handwheel_pressure_20260714/rev_000001 | reviewed | used | Paired side-handwheel pressure family with a tie bar, two threaded posts, seats, independent handwheel parts, and coupled rotary motion. |
| rec_picturex0611_hand_crank_clothes_wringer_fork_folding_crank_handle_20260714/rev_000001 | reviewed | used | Folding crank family adds a separate handle, hinge ear, hinge pin, hinge eye, and bounded revolute park joint. |
| rec_picturex0611_hand_crank_clothes_wringer_fork_fold_down_feed_shelf_20260714/rev_000001 | reviewed | used | Hinged feed-module family adds frame knuckles, shelf panel, hinge barrels, side stops, and a bounded folding joint. |
| rec_picturex0611_hand_crank_clothes_wringer_fork_three_roller_feed_path_20260713/rev_000001 | reviewed | used | Source evidence for the single indexed roller-bank component at N=3, including per-roller bearings, spin joints, and host growth; N remains multiplicity rather than a second core candidate. |
| rec_picturex0611_hand_crank_clothes_wringer_fork_exposed_twin_gear_drive_20260713/rev_000001 | reviewed | rejected_duplicate | Same exposed 16-tooth twin-spur-gear mechanism as the origin; its refined tooth dimensions are implementation evidence, not another structural candidate. |

## Candidate map

| Slot | Candidate | Component type | Record/Revision | Exact model.py:Lx-Ly | Distinction | Evidence |
|---|---|---|---|---|---|---|
| support_mount | classic_boss_clamps | boss-mounted screw-clamp pair | rec_picturex_0611__hand_crank_clothes_wringer__001__png_528e7f40341c4a72899b19b423e8248b/rev_000001 | model.py:L125-L137; model.py:L274-L296 | structure+motion | Two compact bored bosses under the beam carry prismatic clamp screws and broad pads. |
| support_mount | reinforced_table_clamps | gusseted jaw-bracket clamp pair | rec_picturex0611_hand_crank_clothes_wringer_fork_table_clamp_frame_20260713/rev_000001 | model.py:L127-L150; model.py:L286-L329 | structure+motion | Deep brackets, triangular gussets, threaded bushings, retained pads, and cross handles visibly replace the compact boss mounts. |
| support_mount | freestanding_floor_frame | braced four-leg floor stand | rec_picturex0611_hand_crank_clothes_wringer_fork_freestanding_floor_frame_20260713/rev_000001 | model.py:L84-L142 | structure | Four tall legs terminate in paired foot bars and pads and are tied by base crosses and diagonal braces. |
| support_mount | wall_bench_bracket | rear wall plate and gussets | rec_picturex0611_hand_crank_clothes_wringer_fork_wall_bench_bracket_20260713/rev_000001 | model.py:L179-L214 | structure | A rear plate with four mounting bolts and two triangular gussets creates a compact wall/bench installation topology. |
| pressure_mechanism | centre_screw | central T-handle pressure screw | rec_picturex_0611__hand_crank_clothes_wringer__001__png_528e7f40341c4a72899b19b423e8248b/rev_000001 | model.py:L251-L272 | structure+motion | One threaded stem passes through the top beam and carries a cross handle and hub. |
| pressure_mechanism | overhead_screw_bridge | screw yoke and pressure bar | rec_picturex0611_hand_crank_clothes_wringer_fork_pressure_screw_bridge_20260713/rev_000001 | model.py:L152-L181; model.py:L285-L338 | structure+motion | Twin posts and gussets support a crossbar/bushing; a knurled screw drives a separate pressure bar with two pads. |
| pressure_mechanism | spring_loaded_bridge | paired compression-spring bridge | rec_picturex0611_hand_crank_clothes_wringer_fork_spring_loaded_bridge_20260713/rev_000001 | model.py:L155-L175; model.py:L204-L241 | structure | Guide posts, a bridge bar, two helical springs, and seats visibly load the moving bearing blocks. |
| pressure_mechanism | dual_handwheels | paired threaded handwheel adjusters | rec_picturex0611_hand_crank_clothes_wringer_fork_dual_handwheel_pressure_20260714/rev_000001 | model.py:L255-L327 | structure+motion | Two handwheel parts turn above the bearing lines on threaded posts tied by a transverse bar. |
| crank_style | fixed_bent_crank | one-piece bent crank and grip | rec_picturex_0611__hand_crank_clothes_wringer__001__png_528e7f40341c4a72899b19b423e8248b/rev_000001 | model.py:L205-L248 | structure | A single crank-drive part carries the swept bent arm, long grip, and end cap. |
| crank_style | folding_park_crank | two-part hinged folding crank | rec_picturex0611_hand_crank_clothes_wringer_fork_folding_crank_handle_20260714/rev_000001 | model.py:L215-L282; model.py:L369-L378 | structure+motion | A crank stub with hinge ear and pin carries a separate handle through a bounded revolute park joint. |
| feed_module | plain_front_apron | fixed narrow feed apron | rec_picturex_0611__hand_crank_clothes_wringer__001__png_528e7f40341c4a72899b19b423e8248b/rev_000001 | model.py:L96-L100 | structure | The baseline has only a narrow fixed front apron ahead of the nip. |
| feed_module | fold_down_shelf | hinged wet-laundry feed shelf | rec_picturex0611_hand_crank_clothes_wringer_fork_fold_down_feed_shelf_20260714/rev_000001 | model.py:L151-L166; model.py:L314-L341; model.py:L439-L452 | structure+motion | A broad perforated shelf with hinge barrels and side stops folds against frame knuckles on a bounded axis. |
| roller_bank | indexed_parallel_roller_bank | indexed two-or-three roller bank | rec_picturex0611_hand_crank_clothes_wringer_fork_three_roller_feed_path_20260713/rev_000001 | model.py:L215-L400 | structure+motion | One index-general loop emits every roller, its two bearing interfaces, and a registered spin joint; N=3 proves real part/joint/host growth while the origin supplies N=2. |

## Component evidence

- The source pool contains four visibly and mechanically different support interfaces. The origin and reinforced table clamps remain separate because the latter replaces compact bosses with deep gusseted jaw brackets and bushings rather than merely changing size.
- The pressure families are independent of the roller bearings: central screw, overhead yoke, spring bridge, and paired handwheels all terminate at the same two moving bearing-carrier lines.
- The folding crank changes the part tree and adds a bounded park joint while preserving the same crank-drive axis; it is independent of the pressure and support choices.
- The feed shelf attaches to the frame front, outside the roller and pressure envelopes, so the fixed apron and hinged shelf form an independent feed-module slot.
- `roller_bank` has one structural candidate, not one candidate per count. The three-roller record builds indexed `roller_0..roller_2` parts and per-roller joints at `model.py:L215-L400`; the origin supplies the N=2 endpoint. TemplateDesign therefore owns N={2,3} as multiplicity, so this real topology growth doubles raw coverage without inflating core diversity.
- The exposed-twin-gear fork retains the same two 16-tooth exposed gears, axes, and functional semantics as the origin. It is deliberately not counted as another candidate.
