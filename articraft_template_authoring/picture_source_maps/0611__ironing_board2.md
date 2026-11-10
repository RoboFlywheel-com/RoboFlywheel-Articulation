# 0611 / ironing_board2 - template source map

pattern: compact ironing board with padded board, underside tray, folding support legs, and lock brace
parents: 2 origin records from `picture/0611/ironing_board2`
canonical_baselines: none
underfilled_reason: refill 20260713 added wall-mount, tabletop, sleeve-board, and T-leg height-adjust anchors; still short of the normal 8-anchor budget by 1 source-backed anchor if strict budget is required (pullout retry not accepted)

## Slot Candidates

| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| board_top | original compact ironing board tops | ③ | origin_anchor | 2 origin records in `data/index/subcat/0611__ironing_board2.jsonl` | padded board, cover pattern, tray, hinge hardware | origin |
| support_or_base | compact freestanding X-leg folding support | ② | forked_anchor | `rec_ironing_board2_var_x_leg_floor` | crossing scissor leg frames, central pivot, board pivots, lock brace; 4 non-fixed joints | PASS |
| support_or_base | wall-mounted fold-down board | ② | blocked/retry_needed | `rec_ironing_board2_var_wall_mount_fold_down` planned from origin 001 | wall bracket, board hinge, support arm | no persisted record |

## Multiplicity / Copy Logic

- count_param: leg frames, rubber feet, perforation count on tray.
- N samples: 2 crossing leg frames in passed fork; origin tray/perforation details retained.
- suggested N_range: feet 2-4; tray holes 8-24 as host visuals.
- copied object / naming / placement / joint policy: leg_frame_i should be looped/mirrored with shared revolute policy; lock_brace_i follows the same support family.

| support_or_base | wall-mounted fold-down board | ② | forked_anchor | `rec_ironing_board2_var_wall_mount_fold_down_refill` | wall bracket, board hinge, folding support arm; 2 non-fixed joints | PASS |
| support_or_base | compact tabletop board with short U-legs | ③ / N | forked_anchor | `rec_ironing_board2_var_tabletop_short_legs_refill` | loop-emitted short U-leg frames, latch brace; 4 non-fixed joints | PASS |
| board_module | secondary hinged sleeve-board attachment | N | forked_anchor | `rec_ironing_board2_var_sleeve_board_refill` | main board plus narrow sleeve board with support bracket; 5 non-fixed joints | PASS |
| support_or_base | pull-out cabinet/drawer ironing board | ② | blocked/retry_needed | `rec_ironing_board2_var_pullout_cabinet_refill` | prismatic slide rails, cabinet box, hinged board support | provider timeout/no persisted record |
| support_or_base | T-leg height-adjustable board | ② / N | forked_anchor | `rec_ironing_board2_var_t_leg_height_adjust_refill` | telescoping center posts, locking collar; 4 non-fixed joints | PASS |

## Six-Axis Diversity Record

| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / structural topology | partial source-backed | original compact board + freestanding X-leg support PASS |
| ② joint / mechanism type | source-backed | central revolute pivot, board-end pivots, lock brace revolute joints |
| ③ primary form family | source-backed | padded ironing board with tray and folding supports |
| ④ surface decoration | record_only | patterned cover, perforated tray, rubber feet |
| ⑤ proportion / size / travel | record_only | compact board proportions; taller freestanding support in fork |
| ⑥ material / palette / finish | record_only | fabric cover, chrome wire legs, black rubber feet |

## Compatibility Probes

None yet.

## Blocked / Excluded

- `rec_ironing_board2_var_wall_mount_fold_down`: stopped before convergence; retry from origin 001 if wall-mount coverage is needed.
- Laundry drying rack, table, bench, ironing press: excluded as category drift.
