# pictureX_0611_Folding_sofa_bed2 — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Folding_sofa_bed2` |
| template path | `agent/templates/pictureX_0611_Folding_sofa_bed2.py` |
| stage | `P4_VALIDATED` |
| status | `accepted` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
Source map `0611__Folding_sofa_bed2.md` covers 8 accepted anchors: one rod-supported origin plus metal futon frame, storage plinth, chaise footprint, split ratchet back, bi-fold mattress panels, deployable front legs, and slatted support deck forks.

## 核心身份
Convertible sofa/chaise bed with a visibly supported underframe or storage/chaise footprint. It remains a sofa bed, not a separate cot or fixed bench.

## 槽位 + 候选模块表
| slot | candidates | source evidence | emits |
|---|---|---|---|
| body_style | `rod_frame`, `metal_futon`, `storage_base`, `chaise`, `slatted_base` | origin rod support, metal frame, storage plinth, chaise extension, and slatted deck anchors | fixed body, rails/plinth/chaise/slatted details |
| motion_style | `split_ratchet_back`, `bifold_mattress_panels`, `deployable_front_legs`, `slatted_pullout`, `clickclack_back`, `trifold_panels`, `pullout_deck` | split back, bi-fold mattress, deployable legs, slatted deck, and shared sofa-bed conversion axes | one child motion assembly |
| palette_style | `oak`, `painted`, `industrial`, `walnut`, `slate` | fabric, black metal, wood/metal support variants | material axis only; not counted as a structural slot tuple |
| panel_count | 2-4 | support deck / cushion-panel multiplicity | multiplicity coverage for repeated cushion/panel visuals; not counted as a structural slot tuple |

## 槽位图（slot graph）
Root `body` contains sofa, storage/chaise/frame structure. One active child attaches by hinge or rail. The child is chosen by `motion_style`; repeated slats/panels stay internal visuals.

## 每槽位 Module Emits / Interfaces
Body modules must contact the grounded body: rails intersect arms, storage plinth reaches the seat, front panels connect to plinth. Motion modules expose a single named joint `body_to_<motion_style>` with metadata and limits.

## Multiplicity / Copy Logic
- count_param: `panel_count`
- N range: 2-4 panels in template; source slatted deck uses repeated supports as record evidence
- naming: `bed_panel_{i}` when panel motion is selected
- placement: serial across the sleeping deck

## 参数范围汇总
`width` 1.05-1.75, `depth` 0.56-0.92, `seat_h` 0.30-0.44, `back_h` 0.48-0.76, `travel` 0.25-0.58, `swing` 0.75-1.45. Resolver clamps to geometry-safe ranges.

## 拓扑多样性审计
Skeleton coverage: rod frame, metal futon, storage base, chaise, and slatted base. Mechanism coverage: click-clack, pullout deck, trifold panels, and slatted pull-out. Pipeline slot coverage confirms 20 reachable structural tuples (5 body x 4 motion); axis realization separately observes palette and panel-count coverage, and no suspicious allowances.

## Validator
`run_picturex_0611_folding_sofa_bed2_tests` checks required parts, joint, and slot metadata. Official `sweep-pipeline pictureX_0611_Folding_sofa_bed2` PASS with 46/46 passing seeds and corner gate PASS.

## Reject cases
Outdoor cot, camp chair, fixed bench, pure colorway-only records, and unrelated recliner chairs are excluded.

## 与相邻类别的边界
Bed2 owns storage, chaise, and metal futon underframe variants. Side-panel/trifold identity without these footprint changes remains bed1; ratchet/arm/ottoman roll-out family belongs to bed3.

## 审核记录
2026-07-12: P2 sync completed, storage/rod/slat geometry repaired for disconnected-island gate, supplemented to 20 structural tuples, pipeline PASS.
2026-07-13: P1 source map corrected to 8 anchors; P2 re-sync confirmed all 8 IDs rating=5.
