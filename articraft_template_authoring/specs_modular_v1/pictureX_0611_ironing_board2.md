# pictureX_0611_ironing_board2

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_ironing_board2` |
| template path | `agent/templates/pictureX_0611_ironing_board2.py` |
| stage | `TEMPLATE_DRAFT` |
| status | `implemented` |
| __modular__ | `True` |
| pattern | `linear_chain` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 5 |
| read_count | 5 |
| read_scope | all 5-star samples in this category |
| source_index_policy | adopted module sources indexed in `0611__requested_batch_variant_source_map.md` |

## 核心身份
Foldable ironing board with elongated padded/perforated board, support/folding hardware, and brace/lock relationship. It must not become a generic table, rack, cutting board, or sleeve board only.

## 槽位 + 候选模块表
| slot | module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| board_style | capsule_perforated | forked_anchor | source 001 | `_capsule:L26-L49` | eligible | capsule board/perforation pattern |
| board_style | slotted_pan | forked_anchor | source 002 | `_perforated_pan:L33-L58` | eligible | slotted tray board |
| board_style | rear_iron_rest | forked_anchor | `rec_ironing_board2_var_rear_iron_rest` | generated variant | eligible | rear wire iron rest |
| support_style | x_leg_articulated | forked_anchor | `rec_ironing_board2_var_x_leg_articulated` | generated variant | eligible | real folding X-leg |
| support_style | support_rods | forked_anchor | source 002 | `_add_hinge_mount:L89-L114` | eligible | rod support/hinge mount |
| support_style | tabletop_short_legs | forked_anchor | `rec_ironing_board2_var_tabletop_short_legs` | generated variant | eligible | short tabletop folding legs |

## 槽位图（slot graph）
pattern: linear_chain

`body board` --[revolute Y folding hinge]--> `folding_leg_frame`; `lock_brace` is a prismatic stabilizing child attached to the board underside.

## 每槽位 Module Emits / Interfaces
| slot/module | emits | upstream interface | downstream interface |
|---|---|---|---|
| board_style/* | board body, nose, perforation/rest visuals | root board plane | underside hinge and brace rail |
| support_style/* | folding_leg_frame part | underside hinge | ground foot bar |
| brace | lock_brace part | underside guide | prismatic lock travel |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| board_style | enum | 3 candidates | capsule_perforated | choice | sampled | source/variants |
| support_style | enum | 3 candidates | x_leg_articulated | choice | sampled | source/variants |
| length | float | [0.72,1.48] | 1.18 | independent | clamp | board sources |
| width | float | [0.22,0.54] | 0.38 | independent | clamp | board sources |
| height | float | [0.22,0.95] | 0.78 | independent | clamp | support sources |
| fold_angle | float | [0.35,1.35] | 0.95 | independent | clamp | generated articulated variant |

## 编译预算 / compile budget
Per-seed budget: 20s; primitive-only construction.

## Multiplicity / Copy Logic
- No exposed count axis; slots/perforation bars are fixed surface decoration.

## 视觉多样性 6 轴考察
| 轴 | 有/无 | 说明 |
|---|---|---|
| ① 骨架图 | 有 | long board with X-leg/rod/tabletop supports |
| multiplicity | 无 | support count fixed per module |
| ② 关节类型 | 有 | revolute folding leg, prismatic lock brace |
| ③ 主体形态家族 | 有 | capsule board, slotted pan, rear rest variant |
| ④ 表面装饰 | 有 | perforations, cover/rest rails |
| ⑤ 尺寸/行程 | 有 | length/width/height/fold angle |
| ⑥ 涂装 | 有 | fabric/metal-like palettes |

## 采样与覆盖审计
Total combinations: 3 x 3 x 3 palettes = 27 plus scales. Sweep focus: board remains elongated, support folds from underside, brace does not float.

## Validator
- Required body, folding_leg_frame, lock_brace.
- Required revolute/prismatic joints.

## Reject cases
- Board becomes rectangular table without ironing cues.
- Missing folding support.
- Rear rest/accessory dominates category.
