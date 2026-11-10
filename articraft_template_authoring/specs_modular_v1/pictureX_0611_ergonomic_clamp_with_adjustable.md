# pictureX_0611_ergonomic_clamp_with_adjustable - Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_ergonomic_clamp_with_adjustable` |
| template path | `agent/templates/pictureX_0611_ergonomic_clamp_with_adjustable.py` |
| test path (optional) | inline author tests |
| stage | `TEMPLATE_VALIDATED` |
| status | `sweep_pipeline_pass_visual_qa_pass` |
| __modular__ | `True` |
| pattern | `linear_chain + optional parallel child` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | image-faithful forearm-support origin plus seven accepted forks; complete metadata/prompt/build/tests |
| source_index_policy | legacy label is subordinate to confirmed image identity; monitor/laptop arms excluded |

Sources: origin `rec_picturex_...ergonomic_clamp_with_adjustable...001...` L124-L612; forks parallel linkage L144-L789, linear rail L124-L674, gas spring L127-L725, split pad L124-L715, ball socket L129-L686, rotary column L160-L757, ratchet elbow L187-L717.

## 核心身份

Desk-clamped adjustable forearm support with a padded cradle and real reach/wrist/pad motion. It is not a hand clamp, monitor arm or laptop tray.

## 槽位 + 候选模块表

### Slot A：arm_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_pivot_arm` | origin_anchor | origin | L124-L612 | eligible | one revolute reach member |
| `parallel_linkage` | forked_anchor | parallel fork | L144-L789 | eligible | upper/lower link macro construction |
| `linear_rail` | forked_anchor | rail fork | L124-L674 | eligible | x-prismatic rail carriage |
| `gas_spring_arm` | forked_anchor | gas fork | L127-L725 | eligible | pivot arm with counterbalance visual |
| `rotary_column_arm` | forked_anchor | rotary fork | L160-L757 | eligible | column/collar/radial form |
| `ratchet_elbow_arm` | forked_anchor | ratchet fork | L187-L717 | eligible | toothed-sector elbow form |

### Slot B：wrist_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `tilt_wrist` | origin_anchor | origin | L124-L612 | eligible | captured y-revolute wrist |
| `ball_socket_wrist` | forked_anchor | ball-socket fork | L129-L686 | eligible | ball/socket primary form with bounded tilt |
| `yoke_wrist` | forked_anchor | split-pad fork | L124-L715 | eligible | yoke supports two semantic pads |

### Slot C：pad_module
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `single_forearm_pad` | origin_anchor | origin/most forks | ranges above | eligible | one padded cradle |
| `split_forearm_wrist_pad` | forked_anchor | split-pad fork | L124-L715 | eligible | separate articulated forearm/wrist zones |

## 槽位图（slot graph）

`body` desk clamp -> `arm_link` (z-revolute or x-prismatic) -> `wrist` (y-revolute) -> `forearm_pad` (x-revolute); split-pad adds `wrist_pad` as a parallel x-revolute child. Each joint origin lies on visible clamp column/hub/yoke geometry. Candidate compatibility is source locked.

## 每槽位 Module Emits / Interfaces
| slot | emits | joints | interface/source |
|---|---|---|---|
| clamp/base | `body`, jaws/spindle/pad/column host visuals | none | desk contact planes and shoulder hub; all sources |
| arm | `arm_link`, rail/link/gas/ratchet visuals | revolute or prismatic | shoulder support column; arm forks |
| wrist | `wrist` with hub/socket/yoke | y-revolute | arm endpoint hub; wrist anchors |
| pad | `forearm_pad`, optional `wrist_pad` | one/two x-revolute | yoke/top support plane; origin/split fork |

## 参数范围汇总
| 参数 | 类型 | 范围 | 默认 | 约束类型 | 约束 | 来源 |
|---|---|---|---|---|---|---|
| `source_candidate` | enum | 8 confirmed | single arm | choice | deterministic RNG | pool |
| module enums | enum | tables | derived | equation | candidate compatibility | source map |
| `reach` | float | [0.25,0.56] | 0.38 | independent | clamp | sources |
| `height` | float | [0.16,0.40] | 0.26 | independent | support column derives from it | sources |
| `pad_length` | float | [0.23,min(0.42,1.15 reach)] | 0.32 | inequality | avoids disproportionate pad | pad sources |
| `arm_swing` | float | [0.40,1.00] rad | 0.72 | conditional | revolute arms only | sources |

## compile budget

5-20s per seed; primitive arm/clamp geometry.

## Multiplicity / Copy Logic

- No arbitrary N. Split forearm/wrist pads are two semantic zones.

## 视觉多样性 6 轴考察
| 轴 | 有/无 | 取值 / 理由 |
|---|---|---|
| ① 骨架图 | 有 | single, parallel, rail, rotary, split-pad graphs |
| └ multiplicity | 无 | no repeated arbitrary array |
| ② 关节类型 | 有 | revolute reach/wrist/pad and prismatic rail |
| ③ 主体形态家族 | 有 | single/parallel/gas/rail/ratchet arm and single/split pad forms |
| ④ 表面装饰 | 有 | upholstery cushion/seam and scale marks as embedded host visuals |
| ⑤ 尺寸/行程 | 有 | ranges above; sampled motion and targeted reach/wrist/pad poses; folded pad-on-arm nesting is explicit |
| ⑥ 涂装 | 有 | industrial, painted, slate metal/polymer/foam palettes |

## 采样与覆盖审计

Eight source candidates select compatible arm/wrist/pad modules; dimensions then clamp/derive. No overrides. Sweep 0-35 plus corners; viewer 0-9 must preserve obvious padded forearm-support identity.

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| source_candidate | 8 | yes | yes | confirmed |
| arm_module | 6 | yes | yes | source-backed |
| wrist_module | 3 | yes | yes | source-backed |
| pad_module | 2 | yes | no | only two honest source-backed topologies |

## Validator

- desk clamp and padded support always visible; module choices exact and deterministic
- every separate child moves and has visible support; sampled collision + targeted poses
- split-pad folded nesting is scoped, not a generic collision waiver

## Reject cases

- bare hand clamp; monitor/laptop support; no pad; floating arm/pad; static joints; rail without guided support; split pads treated as arbitrary multiplicity.

## 与相邻类别的边界

- Monitor arm: excluded because terminal is a padded forearm cradle, not VESA head.
- Laptop tray arm: excluded because no broad equipment tray.

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved |
| reviewer notes | image identity governs legacy label; 8/8 sources read; pipeline and visual QA passed |
