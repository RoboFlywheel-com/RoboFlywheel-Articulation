# pictureX_0611_juicer_press_with_handle

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_juicer_press_with_handle` |
| template path | `agent/templates/pictureX_0611_juicer_press_with_handle.py` |
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
Hand-operated citrus/fruit press with base/frame, cup or strainer, vertical ram, long handle, and linkage/pivot. It must not become an electric juicer, blender, garlic press, wine press, or generic clamp.

## 槽位 + 候选模块表
| slot | module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| frame_style | straight_yoke | forked_anchor | source 001 | `_base_shell:L24-L39`, `_upper_crosshead:L42-L63` | eligible | upright yoke press |
| frame_style | arch_frame | forked_anchor | `rec_juicer_press_var_arch_frame` | generated variant | eligible | arched yoke |
| frame_style | dual_post_frame | forked_anchor | `rec_juicer_press_var_dual_post_frame` | generated variant | eligible | twin post commercial frame |
| receiver_style | cup_strainer | forked_anchor | source 001 | `_cup_geometry:L66-L94` | eligible | cup and strainer plate |
| receiver_style | bowl_strainer | forked_anchor | `rec_juicer_press_var_bowl_strainer_n` | generated variant | eligible | bowl with more perforations |
| receiver_style | deep_basket | forked_anchor | source/variant family | build spans | eligible | deeper receiver basket |
| mechanism_style | lever_ram | forked_anchor | source 001 | `_ram_geometry:L137-L161`, `_lever_arm_geometry:L164-L176` | eligible | lever-driven vertical ram |
| mechanism_style | screw_assist_ram | forked_anchor | `rec_juicer_press_var_screw_assist_ram` | generated variant | eligible | screw-assisted ram |

## 槽位图（slot graph）
pattern: parallel_children

`body frame` owns base, posts, cup/strainer. `vertical_ram` is a prismatic Z child. `press_handle` is a revolute Y child on upper frame; linkage is represented by handle/ram co-located interfaces.

## 每槽位 Module Emits / Interfaces
| slot/module | emits | upstream interface | downstream interface |
|---|---|---|---|
| frame_style/* | base, posts, crosshead | ground plane | ram guide and handle pivot |
| receiver_style/* | cup/strainer visuals | body base | centered under ram |
| mechanism_style/* | vertical_ram, press_handle | crosshead guide/pivot | press travel and handle swing |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| frame_style | enum | 3 candidates | straight_yoke | choice | sampled | source/variants |
| receiver_style | enum | 3 candidates | cup_strainer | choice | sampled | source/variants |
| mechanism_style | enum | 2 candidates | lever_ram | choice | sampled | source/variants |
| width | float | [0.28,0.60] | 0.42 | independent | clamp | source proportions |
| height | float | [0.46,0.96] | 0.72 | independent | clamp | source proportions |
| lever_length | float | [0.38,0.88] | 0.62 | independent | clamp | lever source |
| ram_travel | float | [0.07,0.26] | 0.16 | independent | clamp | ram source |

## 编译预算 / compile budget
Per-seed budget: 20s; primitive-only construction.

## Multiplicity / Copy Logic
- No exposed count axis; perforations are module-local decoration.

## 视觉多样性 6 轴考察
| 轴 | 有/无 | 说明 |
|---|---|---|
| ① 骨架图 | 有 | straight, arched, dual-post frame |
| multiplicity | 无 | perforation count not exposed as product axis |
| ② 关节类型 | 有 | prismatic ram, revolute handle |
| ③ 主体形态家族 | 有 | frame and receiver families |
| ④ 表面装饰 | 有 | strainer perforations, grip, screw detail |
| ⑤ 尺寸/行程 | 有 | width/height/lever/ram travel |
| ⑥ 涂装 | 有 | metal/painted/wood grip palettes |

## 采样与覆盖审计
Total combinations: 3 x 3 x 2 x 3 palettes = 54 plus scales. Sweep focus: ram centered above strainer, handle remains long and hand-operated.

## Validator
- Required body, vertical_ram, press_handle.
- Required prismatic ram and revolute handle joints.

## Reject cases
- Electric juicer/blender identity.
- Missing cup/strainer.
- Handle too short or ram not vertical.
