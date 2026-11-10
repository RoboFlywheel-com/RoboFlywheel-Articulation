# Refrigerator With Hinged Doors｜带铰链门冰箱 Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `refrigerator_with_hinged_doors` |
| template path | `agent/templates/refrigerator_with_hinged_doors.py` |
| test path | `tests/agent/test_refrigerator_with_hinged_doors_template.py` |
| status | baseline spec for style reference only |

> 这是已有类别的 baseline spec，只用于参考 spec 写法、结构组织和 validator 写法。新增类别的部件来源必须来自新 spec 中被采纳且有 `model.py:Lx-Ly` 的 5 星样本源码片段。

## 核心身份
冰箱主体，带一扇或多扇铰链门、门把手、内部隔板、抽屉、门封条。

## 部件（Parts）
```
fridge_body                           # 冰箱主 part
 ├── door_0 / door_1 / ...            # 每扇门一个独立 part；门把手、gasket、dispenser 都以 visual 挂在 door 上
 ├── shelf_i（每层独立 part）          # 必须有可见几何
 └── drawer_i（可选，每个独立 part）
```

注：dispenser、handle、gasket_strip 均以 `door.visual(...)` 挂在 door 上,不是独立 part；也没有 service_flap / subdoor / control_panel 这些 part 或 joint。

## 关节（Joints）
| joint | 类型 | 含义 |
|---|---|---|
| door_i_joint | revolute | 门绕侧边打开 |
| drawer_i_joint | prismatic（可选） | 抽屉前后滑动 |

## 已有模板写法参考
> 该字段只说明旧模板中可参考的写法，不表示部件来源。

revolute_hinge / handle_grip / gasket_strip / prismatic_slide

## 参数范围汇总
| 参数 | 取值建议 |
|---|---|
| size_class | mini / standard / tall（离散桶 + 桶内连续值；spine 字段） |
| door_layout | single / top_freezer / bottom_freezer / side_by_side / t_type_1up_2down / three_door_stacked / french_3door / french_4door / four_door_stacked |
| door_count | 由 `door_layout` 派生：single→1，top_freezer / bottom_freezer / side_by_side→2，t_type_1up_2down / three_door_stacked / french_3door→3，french_4door / four_door_stacked→4 |
| freezer_ratio | 0.25–0.5（仅在 layout 含冷冻区时生效；`single` 时被 build 代码忽略） |
| handle_style | vertical / horizontal / recessed |
| shelf_count | 2–6（独立采样；`_build_*` 按冰箱内高 / 隔板厚度自适应均匀分布，放不下时由 build 代码自然截断） |
| drawer_count | 0–3 |
| door_shelf_count | 0–4 |
| dispenser | none / water / ice |
| gasket_style | thin / thick / dark |
| material_style | white / stainless / black / retro |

## 部件多样性审计（Part Diversity Audit）
> baseline spec 未补完整审计。新增类别必须逐个核心部件填写本表。

| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| 待新增类别填写 | - | - | - | - | - |

## 约束
- 每扇门的 hinge axis 必须竖直 `(0, 0, ±1)`。
- 门的旋转轴必须在门边缘。
- 门打开范围建议 60–120°。
- shelves 必须在冰箱主体内部，且必须是显式 part。
- drawers 必须在主体内部并沿前后方向滑动。
- handles 必须附着在门上。
- gasket 必须跟随 door 移动（作为 door 的 visual 子件）。

## Validator
| 检查项 | 标准 |
|---|---|
| door joint | 每扇门有 revolute joint |
| hinge position | hinge 在门侧边 |
| shelf geometry | shelves 必须有可见 box/mesh part |
| shelf count range | 全局 2–6（layout-specific 下限作为 **数据集级** 覆盖率：top-bottom ≥ 3，French/side-by-side ≥ 4） |
| drawer axis | drawer 沿前后方向 prismatic |
| open sweep | 门打开不严重穿主体 |
| handle attachment | handle 附着在 door |
| gasket presence | door 必须有 gasket_strip 几何 |
| identity | 必须像 refrigerator |

## Reject cases
- 门不能打开。
- 门铰链在中间。
- 隔板或抽屉漂浮，或隔板只有空腔阴影没有实体几何。
- 冰箱变成普通柜子。
- 门布局和 hinge 方向不一致。

---
