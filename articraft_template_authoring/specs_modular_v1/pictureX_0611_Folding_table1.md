# pictureX_0611_Folding_table1 — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Folding_table1` |
| template path | `agent/templates/pictureX_0611_Folding_table1.py` |
| stage | `P4_VALIDATED` |
| status | `accepted` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
Source map `0611__Folding_table1.md` covers 8 accepted anchors: three origins plus standard/sparse/dense roll-top slat tabletop forks, telescoping height-adjustable legs, and cross-brace locking links.

## 核心身份
Tubular folding table family with light frame construction. Its distinctive axes are rolltop/slatted tabletops and telescoping or X-tube support legs.

## 槽位 + 候选模块表
| slot | candidates | source evidence | emits |
|---|---|---|---|
| top_style | `single_panel`, `rounded_plate`, `rolltop_slats`, `sparse_rolltop_slats`, `dense_rolltop_slats` | rounded plate and standard/sparse/dense roll-top forks | tabletop, rounded cap treatment, or repeated slats |
| support_style | `tube_x_frame`, `tube_u_frame`, `telescoping_legs`, `crossbrace_locks` | X/U tube frame, telescoping fork, and cross-brace lock fork | fixed tube frame, telescoping leg sockets, or locking brace hardware |
| palette_style | `oak`, `painted`, `industrial`, `walnut`, `slate` | aluminum/black tubes, wood/plastic top | material axis only; not counted as a structural slot tuple |
| slat_count | 6/10/12/16 | roll-top multiplicity | multiplicity coverage for `top_slat_{i}` visuals; not counted as a structural slot tuple |

## 槽位图（slot graph）
`body` contains tabletop, tube frame, and fixed leg sockets. `moving_support` is the active support child, revolute for X-frame folding or prismatic for telescoping legs.

## 每槽位 Module Emits / Interfaces
Rolltop module emits slats embedded into the tabletop surface. Telescoping module emits inner legs and crossbar touching the parent at the tabletop/socket interface. X-frame visuals are extended to contact the tabletop.

## Multiplicity / Copy Logic
- count_param: `slat_count`
- N range: 6, 10, 12, 16
- naming: `top_slat_{i}`
- placement: evenly spaced across table width

## 参数范围汇总
`width` 0.58-1.08, `depth` 0.42-0.74, `height` 0.54-0.82, `travel` 0.09-0.22, `swing` 0.80-1.45.

## 拓扑多样性审计
Pipeline slot coverage realizes five top styles and four support styles, for 20 reachable structural tuples. Axis realization separately observes slat-count and palette coverage; rolltop density, rounded plate, U/X-frame, telescoping, and cross-brace axes are source-backed by anchors.

## Validator
`run_picturex_0611_folding_table1_tests` checks body, moving support, active joint, and slot metadata. Official `sweep-pipeline pictureX_0611_Folding_table1` PASS with 45/45 passing seeds.

## Reject cases
Standing desks, drafting tables, carts with wheels, fixed tables, and generic scissor-only table variants are excluded.

## 与相邻类别的边界
Table1 owns tube/X-frame, rolltop, and telescoping-leg variants. General scissor/split folding table remains Folding_table; caster/drop-leaf compact table remains Folding_table2.

## 审核记录
2026-07-12: rolltop slat contact and X/U support-frame connectivity repaired; supplemented to 9 structural tuples; pipeline PASS.
2026-07-13: P1 source map corrected to 8 anchors; P2 re-sync confirmed all 8 IDs rating=5.
