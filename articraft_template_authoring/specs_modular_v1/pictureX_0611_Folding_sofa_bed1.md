# pictureX_0611_Folding_sofa_bed1 — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Folding_sofa_bed1` |
| template path | `agent/templates/pictureX_0611_Folding_sofa_bed1.py` |
| stage | `P4_VALIDATED` |
| status | `accepted` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
Source map `0611__Folding_sofa_bed1.md` now covers 8 accepted anchors: three origins (`001.png`, `002.png`, `003.png`) plus click-clack backrest, pull-out deck, paired fold-out support legs, slatted pull-out frame, and tri-fold cushion panel forks.

## 核心身份
Convertible sofa bed: a fixed sofa body with arms/back/seat plus one articulated conversion module. It must read as a sofa in the closed pose and expose a sleep-surface transformation through hinged back, sliding deck, or serial cushion panels.

## 槽位 + 候选模块表
| slot | candidates | source evidence | emits |
|---|---|---|---|
| body_style | `panel_sofa`, `framed_foldout`, `u_leg_foldout` | origin anchors `002.png`, `003.png`; side panels, framed supports, U-leg fold-out frame | fixed `body` with seat, arms, back frame, optional rails/U-leg hardware |
| motion_style | `clickclack_back`, `pullout_deck`, `foldout_support_legs`, `slatted_pullout_frame`, `trifold_panels`, `seat_flip_forward` | click-clack, pull-out deck, fold-out support legs, slatted pull-out frame, tri-fold, and compatibility flip-forward sleep panel anchors | one child part named by motion style |
| palette_style | `oak`, `painted`, `industrial`, `walnut`, `slate` | six-axis material range | material axis only; not counted as a structural slot tuple |
| panel_count | 2-4 | trifold multiplicity fork | multiplicity coverage for trifold bed-panel visuals; not counted as a structural slot tuple |

## 槽位图（slot graph）
`body` is the root. `body_style` changes fixed structure. `motion_style` attaches exactly one non-fixed child through `body_to_<motion_style>`. `panel_count` only affects repeated panel visuals when the child is a fold-out panel deck.

## 每槽位 Module Emits / Interfaces
`body_style` emits one grounded body with inertial and supporting geometry. `motion_style` emits one revolute or prismatic joint, motion limits, metadata, and child visuals. The joint interface is always parent `body`, child `<motion_style>`, with overlap allowance only at hinge/rail mounting hardware.

## Multiplicity / Copy Logic
- count_param: `panel_count`
- N range: 2-4 cushion/bed panels
- naming: `bed_panel_{i}`
- placement: regular spacing forward from the sofa seat
- joint policy: template uses one articulated child for the active conversion assembly; repeated panels are visuals inside that assembly.

## 参数范围汇总
`width` 1.05-1.75, `depth` 0.56-0.92, `seat_h` 0.30-0.44, `back_h` 0.48-0.76, `travel` 0.25-0.58, `swing` 0.75-1.45. Resolvers clamp broader external inputs to safe compile ranges.

## 拓扑多样性审计
Six-axis coverage is source-backed for skeleton, mechanism, primary form, proportion, and material. Surface decoration is represented by seams, rails, ratchet plates, U-leg hardware, and hinge caps. Pipeline slot coverage confirms 12 reachable structural tuples (3 body x 4 motion); axis realization separately observes palette coverage and 2/3/4 panel-count coverage without using them to inflate structural variant count.

## Validator
`run_picturex_0611_folding_sofa_bed1_tests` requires `body`, active child, required joint, and slot metadata. Official `sweep-pipeline` passed fast/final/corner stages with 45/45 passing seeds.

## Reject cases
Storage-base sofa bed belongs to Folding_sofa_bed2. Bunk/loft beds, recliner-only chairs, fixed sofas, and non-convertible benches are excluded.

## 与相邻类别的边界
This class keeps side-panel/framed sofa-bed variants. Storage plinth, chaise footprint, tubular/X-base, ottoman front extension, and fold-down arms are assigned to the sibling sofa-bed classes.

## 审核记录
2026-07-12: source maps confirmed, P2 synced, template registered, geometry repaired for sweep gates, supplemented to 12 structural tuples, `sweep-pipeline pictureX_0611_Folding_sofa_bed1` PASS.
2026-07-13: P1 source map corrected to 8 anchors and origin `001.png` reconciled; P2 re-sync confirmed all 8 IDs rating=5.
