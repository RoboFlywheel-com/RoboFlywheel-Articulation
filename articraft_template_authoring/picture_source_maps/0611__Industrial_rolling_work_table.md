# 0611 / Industrial_rolling_work_table - template source map

pattern: wheeled industrial work table with lower shelf, work surface, optional drawers/height adjustment
parents: 4 origin records from `picture/0611/Industrial_rolling_work_table`
canonical_baselines: none
underfilled_reason: refill 20260713 added pegboard/tool-rack anchor; still short of the normal 8-anchor budget by 1 source-backed anchor (folding-leaf retry interrupted before persistence)

## Slot Candidates

| slot | candidate | diversity_axis | source_type | record/evidence | key parts/joints | status |
|---|---|---|---|---|---|---|
| table_body | original rolling work tables | ①/③ | origin_anchor | 4 origin records in `data/index/subcat/0611__Industrial_rolling_work_table.jsonl` | top, lower shelf, legs/frame, caster loops, handle/rail details | origin |
| storage_module | drawer cabinet under work surface | ③ | forked_anchor | `rec_industrial_rolling_work_table_var_drawer_cabinet` | three prismatic drawers, rails, pulls, cabinet bay, casters retained; 15 non-fixed joints | PASS |
| height_adjustment | adjustable-height table with lift posts | ② | forked_anchor | `rec_industrial_rolling_work_table_var_adjustable_height` | four telescoping post assemblies, collar clamps, caster loops retained; 16 non-fixed joints | PASS |

## Multiplicity / Copy Logic

- count_param: caster count, shelf rails, drawer count, telescoping post count.
- N samples: origin-specific caster loops; 3 drawers in drawer-cabinet fork; 4 telescoping leg assemblies in adjustable-height fork.
- suggested N_range: casters 4-6; drawers 2-4; side rails 2-6.
- copied object / naming / placement / joint policy: caster_i loops should share swivel/spin policy; drawers should be emitted by one helper with uniform prismatic slides.

| upper_tooling | rear pegboard / tool-rack work table | ① | forked_anchor | `rec_industrial_rolling_work_table_var_pegboard_rack_refill` | rear upright posts, pegboard/tool rack, sliding tray, caster base; 16 non-fixed joints | PASS |
| tabletop_module | hinged folding side leaves | ② / N | blocked/retry_needed | `rec_industrial_rolling_work_table_var_folding_leaf_refill` | fixed center top plus two hinged leaves and support brackets | interrupted before persisted record |

## Six-Axis Diversity Record

| axis | treatment | values / range / reason |
|---|---|---|
| ① skeleton / structural topology | source-backed | rolling table frame, shelves, caster base, drawer cabinet bay |
| ② joint / mechanism type | source-backed | caster swivel/spin, prismatic drawer slides, telescoping height posts |
| ③ primary form family | source-backed | plain rolling work table, drawer-cabinet work table, adjustable-height work table |
| ④ surface decoration | record_only | handles, rails, safety lips, labels, host-conformal only |
| ⑤ proportion / size / travel | source-backed | top/shelf proportions, drawer spacing, caster spacing, and telescoping travel inherited from origins/forks |
| ⑥ material / palette / finish | record_only | steel frame, rubber casters, painted or stainless work surfaces |

## Compatibility Probes

None yet.

## Blocked / Excluded

- First DashScope attempts for `rec_industrial_rolling_work_table_var_drawer_cabinet` and `rec_industrial_rolling_work_table_var_adjustable_height` stalled; OpenAI sequential retry passed both.
- Tool cart, cabinet-only, scissor lift cart: excluded unless explicitly treated as a same-family work table variant.
