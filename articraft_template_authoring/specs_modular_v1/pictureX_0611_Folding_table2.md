# pictureX_0611_Folding_table2 — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Folding_table2` |
| template path | `agent/templates/pictureX_0611_Folding_table2.py` |
| stage | `P4_VALIDATED` |
| status | `accepted` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
Source map `0611__Folding_table2.md` covers 8 accepted anchors: compact central/castered origin plus X-trestle base, four corner legs, bi-fold top, drop-leaf side extensions, butterfly center leaf, tilting tabletop latch, and dual caster sled support forks.

## 核心身份
Compact folding table with caster/central support, X-trestle or corner-leg topology, and a foldable top such as bi-fold or drop-leaf extensions.

## 槽位 + 候选模块表
| slot | candidates | source evidence | emits |
|---|---|---|---|
| top_style | `single_panel`, `bifold_top`, `drop_leaf`, `dual_drop_leaf`, `butterfly_center_leaf`, `tilting_top_latch` | origin top, bifold fork, single/dual drop-leaf forks, butterfly center leaf, and tilt-latch fork | fixed top plus optional `moving_top` |
| support_style | `caster_column`, `folding_pedestal`, `x_trestle`, `four_corner_legs`, `dual_caster_sled` | origin caster support, folding pedestal, X trestle, corner-leg fork, dual caster sled fork | fixed base and optional moving support child |
| palette_style | `oak`, `painted`, `industrial`, `walnut`, `slate` | dark shell, metal supports, rubber/casters | material axis only; not counted as a structural slot tuple |
| slat_count | 6/10/12/16 | shared numeric coverage | numeric coverage only for this class; not counted as a structural slot tuple |

## 槽位图（slot graph）
`body` is the tabletop/base root. If `top_style` is `bifold_top` or `drop_leaf`, child `moving_top` attaches through a revolute hinge. Otherwise child `moving_support` models the folding support.

## 每槽位 Module Emits / Interfaces
Top modules emit center hinge or side leaf panel. Support modules emit caster base, X-trestle, or corner-leg sockets that contact the tabletop/root body. Moving child uses a single named articulation with metadata.

## Multiplicity / Copy Logic
- count_param: `slat_count`
- source multiplicity: 2 trestle frames, 4 corner legs, 2 tabletop halves/leaves
- template expression: one active child represents the moving module, with mirrored visuals inside that child when needed

## 参数范围汇总
`width` 0.58-1.08, `depth` 0.42-0.74, `height` 0.54-0.82, `travel` 0.09-0.22, `swing` 0.80-1.45, `slat_count` in 6/10/12/16.

## 拓扑多样性审计
Pipeline slot coverage realizes six top styles and five support styles, for 30 reachable structural tuples. Axis realization separately observes slat_count and palette coverage without using them to inflate structural variant count. Source-backed axes include central/castered support, dual caster sled, folding pedestal, X trestle, corner legs, bi-fold top, drop leaf, butterfly center leaf, and tilting latch.

## Validator
`run_picturex_0611_folding_table2_tests` checks `body`, the selected moving part, required joint, and slot metadata. Official `sweep-pipeline pictureX_0611_Folding_table2` PASS with 45/45 passing seeds.

## Reject cases
Serving carts with shelves/handles, fixed pedestal cafe tables, non-folding tables, and pure caster trolleys are excluded.

## 与相邻类别的边界
Table2 owns compact/castered, bifold/drop-leaf, X-trestle and corner-leg variants. General scissor/split tables remain Folding_table; tube/rolltop/telescoping variants remain Folding_table1.

## 审核记录
2026-07-12: caster/pedestal base connectivity and single/dual leaf hinge contact repaired; supplemented to 16 structural tuples; pipeline PASS.
2026-07-13: P1 source map corrected to 8 anchors; P2 re-sync confirmed all 8 IDs rating=5; template sampling now includes `dual_caster_sled`.
