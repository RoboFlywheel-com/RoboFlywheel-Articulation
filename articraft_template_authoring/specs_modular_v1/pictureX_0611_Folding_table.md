# pictureX_0611_Folding_table — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Folding_table` |
| template path | `agent/templates/pictureX_0611_Folding_table.py` |
| stage | `P4_VALIDATED` |
| status | `accepted` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
Source map `0611__Folding_table.md` covers 8 accepted anchors: four origins plus scissor/accordion base, paired A-frame trestle, telescoping legs, and suitcase-style bi-fold top forks.

## 核心身份
General folding table with a tabletop and collapsible support mechanism. It is a table first; articulation must represent a foldable support/top mechanism rather than a fixed workbench.

## 槽位 + 候选模块表
| slot | candidates | source evidence | emits |
|---|---|---|---|
| top_style | `single_panel`, `split_halves`, `framed_panel`, `suitcase_bifold_handle` | origin rounded panel, split-half anchor, framed tabletop anchor, and suitcase bi-fold fork | tabletop, optional center hinge barrel/frame rails/handle |
| support_style | `folding_legs`, `webbed_legs`, `brace_legs`, `beam_frame`, `scissor_base`, `a_frame_trestle`, `telescoping_legs` | origin leg/braces, webbed support, beam frame, locking braces, scissor, A-frame, and telescoping forks | fixed support visuals plus active support child |
| palette_style | `oak`, `painted`, `industrial`, `walnut`, `slate` | plastic/metal/rubber/wood finish range | material axis only; not counted as a structural slot tuple |
| slat_count | 6/10/12/16 | shared numeric coverage | numeric coverage only for this class; not counted as a structural slot tuple |

## 槽位图（slot graph）
Root `body` contains tabletop, edge rails, and fixed support hardware. Child `moving_support` attaches through `body_to_moving_support` and folds under the top.

## 每槽位 Module Emits / Interfaces
Top module emits table surface and hinge marker when split. Support module emits grounded sockets/web/scissor visuals plus one active support child. Fixed support visuals must touch the tabletop or edge rails.

## Multiplicity / Copy Logic
- count_param: `slat_count` retained for numeric coverage only; it is not a structural tuple multiplier for this class
- support copies: two mirrored leg/scissor frames under tabletop
- naming: `folding_leg_pair_<side>`, `x_frame_*`

## 参数范围汇总
`width` 0.58-1.08, `depth` 0.42-0.74, `height` 0.54-0.82, `travel` 0.09-0.22, `swing` 0.80-1.45, `slat_count` in 6/10/12/16.

## 拓扑多样性审计
Pipeline slot coverage realized three top styles and five support styles, for 15 reachable structural tuples. Axis realization separately observes slat_count and palette coverage without using them to inflate structural variant count. Source-backed axes include tabletop form, support topology, folding/scissor/brace/beam mechanisms, proportions, and material.

## Validator
`run_picturex_0611_folding_table_tests` checks `body`, `moving_support`, joint, and slot metadata. Official `sweep-pipeline pictureX_0611_Folding_table` PASS with 46/46 passing seeds.

## Reject cases
Drafting/tilt tables, ironing boards, fixed workbenches, serving carts, and non-folding cafe tables are excluded.

## 与相邻类别的边界
This class owns rounded/split general folding tables and scissor/web supports. Tube-frame rolltop/telescoping variants belong to Folding_table1; caster/drop-leaf/bifold compact variants belong to Folding_table2.

## 审核记录
2026-07-12: hinge marker, brace, beam-frame, and support contact repaired; supplemented to 15 structural tuples; pipeline PASS.
2026-07-13: P1 source map corrected to 8 anchors; P2 re-sync confirmed all 8 IDs rating=5.
