# pictureX_0611_Industrial_rolling_work_table

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Industrial_rolling_work_table` |
| template path | `agent/templates/pictureX_0611_Industrial_rolling_work_table.py` |
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
Industrial rolling work table/cart: work surface, rolling caster frame, shop-scale storage/equipment features. It must not become an office desk, static bench, medical cart, or kitchen island.

## 槽位 + 候选模块表
| slot | module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| surface_style | equipment_deck | forked_anchor | source 002 | build_object_model:L83-L444 | eligible | equipment workstation deck/upright |
| surface_style | wood_top | forked_anchor | source 003 | `_wood_top_shape:L59-L73` | eligible | wood top rolling worktable |
| surface_style | bench_top | forked_anchor | source 004 | build_object_model:L41-L281 | eligible | compact bench-frame cart |
| surface_style | shelf_handle_cart | forked_anchor | `rec_rolling_work_table_var_lower_shelf_handle` | generated variant | eligible | shelf + push handle cart |
| utility_style | plain_lower_shelf | forked_anchor | source 003/004 | build spans | eligible | lower shelf |
| utility_style | keyboard_drawer | forked_anchor | source 002 | build spans | eligible | pullout tray/workstation |
| utility_style | brake_yoke | forked_anchor | source 001 | `_add_yoke_geometry:L144-L175` | eligible | brake/yoke detail |
| utility_style | push_handle | forked_anchor | generated variant | generated variant | eligible | push handle |

## 槽位图（slot graph）
pattern: parallel_children

`body frame` owns top, legs, casters, lower shelf, handles/uprights. `sliding_tray` is a prismatic X child under the surface for tray/drawer affordance.

## 每槽位 Module Emits / Interfaces
| slot/module | emits | upstream interface | downstream interface |
|---|---|---|---|
| surface_style/* | body visuals: work surface, optional upright | root frame | tray rail under top |
| utility_style/* | lower shelf / handle / brake visuals | body frame | optional tray clearance |
| sliding_tray | moving tray part | under-top rail | prismatic range `[0, drawer_travel]` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| surface_style | enum | 4 candidates | wood_top | choice | sampled | source map |
| utility_style | enum | 4 candidates | plain_lower_shelf | choice | sampled | source map |
| width | float | [0.55,1.25] | 0.88 | independent | clamp | sources |
| depth | float | [0.36,0.82] | 0.56 | independent | clamp | sources |
| height | float | [0.48,1.05] | 0.76 | independent | clamp | sources |
| drawer_travel | float | [0.08,0.32] | 0.20 | independent | clamp | tray source |

## 编译预算 / compile budget
Per-seed budget: 20s; boxes/cylinders only.

## Multiplicity / Copy Logic
- No exposed count axis; four casters and four legs are fixed for category readability.

## 视觉多样性 6 轴考察
| 轴 | 有/无 | 说明 |
|---|---|---|
| ① 骨架图 | 有 | workstation, wood table, bench cart, shelf/handle cart |
| multiplicity | 无 | caster/leg count fixed |
| ② 关节类型 | 有 | prismatic sliding tray |
| ③ 主体形态家族 | 有 | surface/upright/handle cart families |
| ④ 表面装饰 | 有 | perforated upright, shelf, brake/yoke |
| ⑤ 尺寸/行程 | 有 | width/depth/height/tray travel |
| ⑥ 涂装 | 有 | industrial, painted, oak, walnut |

## 采样与覆盖审计
Total combinations: 4 x 4 x 4 palettes = 64 plus scales. Sweep focus: stable caster footprint, tray rail, not office/kitchen furniture.

## Validator
- Required body/sliding_tray and prismatic joint.
- slot choices recorded.

## Reject cases
- No casters.
- No work surface.
- Tray or equipment module dominates into non-table category.
