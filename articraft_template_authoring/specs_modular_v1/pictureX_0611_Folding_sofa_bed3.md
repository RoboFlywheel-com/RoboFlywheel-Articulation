# pictureX_0611_Folding_sofa_bed3 — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Folding_sofa_bed3` |
| template path | `agent/templates/pictureX_0611_Folding_sofa_bed3.py` |
| stage | `P4_VALIDATED` |
| status | `accepted` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
Source map `0611__Folding_sofa_bed3.md` covers 8 accepted anchors: padded tubular/X origin plus ratchet back, split back panels, fold-down arms, deployable/rollout legs, crossed scissor underframe, tri-fold mattress deck, and hinged ottoman-like front extension forks.

## 核心身份
Padded sofa-bed variant where the visible transformation is a ratcheting back, fold-down side/arm panel, rollout support legs, or ottoman-style front extension.

## 槽位 + 候选模块表
| slot | candidates | source evidence | emits |
|---|---|---|---|
| body_style | `tubular_base`, `x_tube_base`, `panel_sofa` | origin padded base with tubular/X support plus arm/panel body | fixed sofa body |
| motion_style | `ratchet_back`, `split_back_panels`, `scissor_underframe`, `trifold_mattress_deck`, `fold_down_arms`, `dual_arm_foldout`, `rollout_legs`, `ottoman_extension` | ratchet/split backs, scissor underframe, tri-fold deck, fold-down arms, deployable legs, and ottoman-extension anchors | one child motion assembly |
| palette_style | `oak`, `painted`, `industrial`, `walnut`, `slate` | upholstery/black tube/metal hinge palettes | material axis only; not counted as a structural slot tuple |
| panel_count | 2-4 | shared cushion multiplicity range | multiplicity coverage where relevant; not counted as a structural slot tuple |

## 槽位图（slot graph）
`body` is the grounded sofa. `motion_style` creates one child: ratchet back, folding arm panel, deployable leg assembly, or ottoman extension. `body_style` controls the fixed support appearance.

## 每槽位 Module Emits / Interfaces
Motion modules emit a revolute joint with hardware touching the parent at the hinge or support socket. `rollout_legs` includes a crossbar centered on the joint axis so child geometry is mechanically grounded at the closed pose.

## Multiplicity / Copy Logic
- count_param: `panel_count`
- side arms and deployable legs are mirrored visuals inside one motion assembly
- naming: `deployable_leg_<side>`, `rubber_foot_<side>`, `folding_arm_panel`

## 参数范围汇总
`width` 1.05-1.75, `depth` 0.56-0.92, `seat_h` 0.30-0.44, `back_h` 0.48-0.76, `travel` 0.25-0.58, `swing` 0.75-1.45.

## 拓扑多样性审计
Pipeline slot coverage realizes three body styles and eight motion styles, for 24 reachable structural tuples. Axis realization separately observes palettes and 2/3/4 panel counts; these are coverage axes, not structural tuple multipliers. Source-backed axes include ratchet/split backrest, scissor underframe, deployable legs, single/dual arm folding, X-tube base, tri-fold deck, and ottoman/front extension.

## Validator
`run_picturex_0611_folding_sofa_bed3_tests` checks `body`, active child, active joint, and slot metadata. Official `sweep-pipeline pictureX_0611_Folding_sofa_bed3` PASS with 46/46 passing seeds.

## Reject cases
Separate ottoman sets without sofa-bed motion, recliner-only chairs, fixed sofas, and storage/chaise bed2 variants are excluded.

## 与相邻类别的边界
Bed3 owns ratchet/arm/rollout-leg/ottoman-extension mechanisms. Bed1 owns click-clack, pull-out, and tri-fold body families; bed2 owns storage/chaise/metal futon frame families.

## 审核记录
2026-07-12: rollout-leg and dual-arm joint/contact geometry repaired; supplemented to 15 structural tuples; pipeline PASS.
2026-07-13: P1 source map corrected to 8 anchors; scissor underframe and tri-fold deck synced as 5★ sources; template sampling now includes `scissor_underframe`.
