# Standing Desk With Synchronous Telescoping Legs And Articulated Controls｜同步伸缩腿升降桌 Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `standing_desk_with_synchronous_telescoping_legs_and_articulated_controls` |
| template path | `agent/templates/standing_desk_with_synchronous_telescoping_legs_and_articulated_controls.py` |
| test path | `tests/agent/test_standing_desk_with_synchronous_telescoping_legs_and_articulated_controls_template.py` |
| status | baseline spec for style reference only |

> 这是已有类别的 baseline spec，只用于参考 spec 写法、结构组织和 validator 写法。新增类别的部件来源必须来自新 spec 中被采纳且有 `model.py:Lx-Ly` 的 5 星样本源码片段。

## 核心身份
办公升降桌，带桌面、双腿或多腿同步伸缩柱、横梁、控制面板和独立按钮。

## 部件（Parts）

**通用骨架（实际实现：多腿 + Mimic，单 pedestal 也走同一骨架）**
```
base                                  # 底座，可派生为多个 leg_i_outer 或单 pedestal
 ├── leg_i_outer（i = 0..leg_count-1）# stage_count = N 时每腿再嵌套 leg_i_stage_j（j = 1..N-1）
 ├── desktop（fixed 到主腿，由 Mimic 保证同步抬升）
 ├── crossbar（可选；可被 desktop apron 吸收）
 └── control_panel（fixed 到 desktop 或主腿；按钮 / dial 以 visual 挂在其上，不创建独立 part 也不创建 joint）
```

注：`leg_count = 1` 表示单中央 pedestal 模式。所有按钮 / 旋钮一律按 §0 「非可动子件挂载」用 `control_panel.visual(...)` 实现，**当前实现不带 button articulations**。

多腿 Mimic 必须使用 `Mimic` 关节，multiplier = 1.0，offset = 0，保证 max(Δz) − min(Δz) < 1 mm。

## 关节（Joints）
| joint | 类型 | 含义 |
|---|---|---|
| leg_i_lift_joint 或 leg_i_lift_joint_j | prismatic | 桌面/腿组件上下滑动；同腿后续 prismatic 全部 Mimic 到该腿第一段；多腿场景每条腿第一段再 Mimic 到主腿第一段 |

若 `stage_count = N`，每条腿需要 `N − 1` 个 prismatic 关节（outer→stage_1、stage_1→stage_2、…）。

## 已有模板写法参考
> 该字段只说明旧模板中可参考的写法，不表示部件来源。

telescoping_tube / prismatic_slide / mimic_link

## 参数范围汇总
| 参数 | 取值建议 |
|---|---|
| leg_count | 1 / 2 / 3（1 = 单中央 pedestal） |
| stage_count per leg | 2 / 3 |
| desktop_shape | rectangle / rounded / rounded_corner_rect |
| desktop_size | small / medium / large（离散桶 + 桶内连续） |
| desktop_edge_treatment | plain / edge_banded / front_lip / beveled_front / stepped_riser |
| leg_cross_section | rectangular / round / oval |
| crossbar_style | front / rear / double / integrated_into_desktop_apron |
| foot_style | T_foot / rectangular / wide |
| control_panel_position | left / right / center / front_underside |
| material_style | warm_oak_black / walnut_graphite / pale_birch_white / matte_black / satin_white / industrial_steel / charcoal_aluminum / warm_oak_steel |

## 部件多样性审计（Part Diversity Audit）
> baseline spec 未补完整审计。新增类别必须逐个核心部件填写本表。

| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| 待新增类别填写 | - | - | - | - | - |

## 约束
- 升降 axis 必须竖直 `(0, 0, 1)`。
- 左右内升降段必须与对应外桌腿轴线对齐。
- 桌面必须保持水平。
- 内层升降段必须嵌套在外层桌腿中。
- 桌脚必须接近地面。
- 控制面板必须在桌面下方或桌面前侧下沿；按钮 / 旋钮以 visual 挂在面板上。
- 多腿场景下，每条腿的 lift 关节必须有 Mimic 链接到主腿，且 axes 平行。

## Validator
| 检查项 | 标准 |
|---|---|
| lift joint | ≥ 1 个 prismatic lift joint |
| axis check | 升降轴竖直 |
| desktop level | 桌面水平 |
| leg alignment | 左右内外腿对齐 |
| nesting | inner stage 在 outer leg 内 |
| stability | feet 宽度足够支撑桌面 |
| sync check | 多腿场景 max(Δz) − min(Δz) < 1 mm |
| identity | 必须像升降桌 |

## Reject cases
- 没有升降关节。
- 桌面倾斜严重。
- 桌腿不嵌套。
- 看起来像普通桌子。

---
