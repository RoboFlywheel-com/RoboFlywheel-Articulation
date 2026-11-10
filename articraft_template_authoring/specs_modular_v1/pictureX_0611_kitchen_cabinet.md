# pictureX_0611_kitchen_cabinet

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_kitchen_cabinet` |
| template path | `agent/templates/pictureX_0611_kitchen_cabinet.py` |
| stage | `TEMPLATE_DRAFT` |
| status | `implemented` |
| __modular__ | `True` |
| pattern | `parallel_children` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 5 |
| read_count | 5 |
| read_scope | all 5-star samples in this category |
| source_index_policy | adopted module sources indexed in `0611__requested_batch_variant_source_map.md` |

## 核心身份
Kitchen cabinet unit with carcass, hinged front door(s), kitchen-scale panels, hardware, toe-kick or legs, and countertop cue. It must not become a wardrobe, bookcase, generic drawer chest, bathroom vanity, or appliance.

## 槽位 + 候选模块表
| slot | module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| carcass_style | plain_carcass | forked_anchor | source 001/003 | build spans | eligible | base cabinet carcass |
| carcass_style | compact_carcass | forked_anchor | source 004 | build_object_model:L16-L259 | eligible | compact single-door cabinet |
| carcass_style | legged_carcass | forked_anchor | source 005 | `_add_leg:L32-L51` | eligible | visible legs |
| front_style | single_door | forked_anchor | sources 001/002/004 | build spans | eligible | one hinged door |
| front_style | double_doors | forked_anchor | sources 003/005 | `_add_shaker_door:L55-L150` | eligible | paired hinged doors |
| door_style | flat_slab | forked_anchor | sources 002/004 | build spans | eligible | simple slab front |
| door_style | shaker_panel | forked_anchor | sources 003/005 | `_add_shaker_door:L55-L150` | eligible | rail/stile panel door |

## 槽位图（slot graph）
pattern: parallel_children

`body carcass` owns case, countertop, toe-kick/legs. One or two `cabinet_door_*` parts are revolute Z-axis children at front hinges.

## 每槽位 Module Emits / Interfaces
| slot/module | emits | upstream interface | downstream interface |
|---|---|---|---|
| carcass_style/* | body, case, countertop, support base | floor plane | front hinge lines |
| front_style/* | one or two moving door parts | carcass front | door swing range |
| door_style/* | slab or shaker rails/stiles on door part | door face | handle location |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| carcass_style | enum | 3 candidates | plain_carcass | choice | sampled | source map |
| front_style | enum | single_door/double_doors | double_doors | conditional | width < 0.62 forces single_door | source map |
| door_style | enum | flat_slab/shaker_panel | shaker_panel | choice | sampled | source map |
| width | float | [0.44,1.15] | 0.82 | independent | clamp | sources |
| depth | float | [0.28,0.62] | 0.42 | independent | clamp | sources |
| height | float | [0.52,1.08] | 0.84 | independent | clamp | sources |
| door_swing | float | [0.55,1.55] | 1.22 | independent | clamp | hinge sources |

## 编译预算 / compile budget
Per-seed budget: 20s; primitive-only cabinet construction.

## Multiplicity / Copy Logic
- Door count is a front_style slot (`single_door`/`double_doors`), not an open-ended multiplicity axis.

## 视觉多样性 6 轴考察
| 轴 | 有/无 | 说明 |
|---|---|---|
| ① 骨架图 | 有 | single vs double hinged doors, legged vs toe-kick carcass |
| multiplicity | 有 | door count is 1 or 2 via front_style |
| ② 关节类型 | 有 | revolute hinged doors |
| ③ 主体形态家族 | 有 | plain/compact/legged base cabinet |
| ④ 表面装饰 | 有 | shaker rails/stiles, pulls |
| ⑤ 尺寸/行程 | 有 | width/depth/height/door swing |
| ⑥ 涂装 | 有 | painted, oak, walnut |

## 采样与覆盖审计
Total combinations: 3 x 2 x 2 x 3 palettes = 36 before width gating. Sweep focus: kitchen cabinet proportions, hinges and pulls visible, no drawer/bookcase drift.

## Validator
- Required body and cabinet_door_0.
- Required hinged revolute joint metadata.

## Reject cases
- Doorless cabinet.
- Drawer-only chest.
- Wardrobe/bookcase proportions dominate.
