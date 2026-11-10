# pictureX_0611_industrial_crane_featuring_advanced_hydraulic

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_industrial_crane_featuring_advanced_hydraulic` |
| template path | `agent/templates/pictureX_0611_industrial_crane_featuring_advanced_hydraulic.py` |
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
Mobile industrial hydraulic shop/engine crane with caster base, mast, pivoting boom, hydraulic cylinder/pump handle, telescoping extension, and hook. It must not drift into tower crane, gantry crane, forklift, excavator, or static hoist.

## 槽位 + 候选模块表
| slot | module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| base_style | straight_legs | forked_anchor | source 001/002 | build_object_model spans | eligible | caster floor legs |
| base_style | foldable_legs | forked_anchor | `rec_hydraulic_crane_var_foldable_legs` | generated variant | eligible | fold pivots/outriggers |
| base_style | wide_u_base | forked_anchor | `rec_hydraulic_crane_var_wide_gantry_base` | generated variant | eligible | wider U base, still shop crane |
| boom_style | box_beam | forked_anchor | source 001 | build_object_model:L140-L523 | eligible | rectangular boom |
| boom_style | tubular_boom | forked_anchor | source 002 | `_boom_tube_mesh:L61-L65` | eligible | tubular boom |
| boom_style | double_stage_boom | forked_anchor | `rec_hydraulic_crane_var_double_stage_boom` | generated variant | eligible | nested telescoping boom |

## 槽位图（slot graph）
pattern: linear_chain

`body/base+mast` --[revolute Y boom pivot]--> `lifting_boom` --[prismatic X extension]--> `telescoping_extension`; `pump_handle` is a parallel revolute child on the body. Cylinder and caster details remain fixed visuals on body.

## 每槽位 Module Emits / Interfaces
| slot/module | emits | upstream interface | downstream interface |
|---|---|---|---|
| base_style/* | body, base legs, mast, casters, hydraulic cylinder | ground plane | mast boom pivot and pump handle pivot |
| boom_style/* | lifting_boom part, hook visuals | mast pivot | extension rail/socket |
| extension | telescoping_extension part | boom rail | load hook visual/end |
| pump | pump_handle part | body pivot | pump swing range |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| base_style | enum | straight_legs/foldable_legs/wide_u_base | straight_legs | choice | sampled | source/variants |
| boom_style | enum | box_beam/tubular_boom/double_stage_boom | box_beam | choice | sampled | source/variants |
| width | float | [0.55,1.18] | 0.82 | independent | clamp | caster base sources |
| length | float | [0.78,1.45] | 1.08 | independent | clamp | boom/base sources |
| height | float | [0.72,1.35] | 1.02 | independent | clamp | mast sources |
| extension_travel | float | [0.12,0.50] | 0.32 | independent | clamp | extension sources |
| boom_swing | float | [0.20,0.85] | 0.55 | independent | clamp | hydraulic motion |

## 编译预算 / compile budget
Per-seed budget: 20s; primitive-only construction.

## Multiplicity / Copy Logic
- No exposed count axis; caster count is fixed at four for stable shop crane identity.

## 视觉多样性 6 轴考察
| 轴 | 有/无 | 说明 |
|---|---|---|
| ① 骨架图 | 有 | straight/foldable/wide base plus boom extension family |
| multiplicity | 无 | caster count fixed |
| ② 关节类型 | 有 | revolute boom, prismatic extension, revolute pump |
| ③ 主体形态家族 | 有 | box/tubular/double-stage boom and base families |
| ④ 表面装饰 | 有 | caster forks, pivots, cylinder barrel as visuals |
| ⑤ 尺寸/行程 | 有 | width/length/height, extension and boom swing |
| ⑥ 涂装 | 有 | industrial, painted, walnut-compatible workshop palette |

## 采样与覆盖审计
Total combinations: 3 x 3 x 3 palettes = 27 plus scales. Sweep focus: boom pivot, extension rail, hook remains load-end, base stays mobile shop crane.

## Validator
- Required parts: body, lifting_boom, telescoping_extension, pump_handle.
- Required joints are non-fixed and metadata-bearing.

## Reject cases
- Tower/gantry/forklift identity.
- Missing hydraulic/pump cues.
- Extension or hook detached from boom.
