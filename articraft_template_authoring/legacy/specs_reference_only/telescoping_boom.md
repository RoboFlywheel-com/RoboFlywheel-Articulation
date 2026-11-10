# Telescoping Boom｜伸缩臂 Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `telescoping_boom` |
| template path | `agent/templates/telescoping_boom.py` |
| test path | `tests/agent/test_telescoping_boom_template.py` |
| status | baseline spec for style reference only |

> 这是已有类别的 baseline spec，只用于参考 spec 写法、结构组织和 validator 写法。新增类别的部件来源必须来自新 spec 中被采纳且有 `model.py:Lx-Ly` 的 5 星样本源码片段。

## 核心身份
多级嵌套伸缩臂，每一级沿同一轴线线性伸缩。

## 部件（Parts）
```
base_bracket（底座支架）
 └── outer_stage
      └── middle_stage（可选）
           └── inner_stage
                └── end_effector（可选）
```

## 关节（Joints）
| joint | 类型 | 含义 |
|---|---|---|
| stage_i_joint 或 parent_to_child 命名 | prismatic | 第 i 级伸缩段沿主轴滑动 |

关节命名允许两种风格：`stage_i_to_stage_i+1` 或 `outer_to_middle / middle_to_inner_*`。校验只检查 axis 共线性和数量，不强制命名。

## 已有模板写法参考
> 该字段只说明旧模板中可参考的写法，不表示部件来源。

telescoping_tube / prismatic_slide

## 参数范围汇总
| 参数 | 取值建议 |
|---|---|
| stage_count | 3 / 4 / 5 |
| tube_cross_section | rectangular（`Box`） / round（`Cylinder`） / hex（6 个 ±30° 旋转的 `Box` 拼接，或自定义 mesh） |
| boom_orientation | horizontal / angled / vertical |
| length_ratios | 逐级递减的连续比例（每段 0.6–0.9 区间）；**当前为纯连续值，未实现「离散桶 + class」字段**，新模板若沿用该机制建议补 `length_ratio_class` |
| overlap_ratio | 0.15–0.4 |
| base_style | plate / wall_bracket / pedestal / clamp / saddle_cheek / trunnion_yoke / sleeve_socket |
| end_effector | none / hook / light / camera / plate / clamp / lug；若非 none，必须用 FIXED articulation 接在最内层末端 |
| collar_count | stage_count − 1 |
| decoration | warning stripe / bolts / fake cylinder；装饰仅是 visual mesh，不创建独立 part 或 joint |
| material_style | metal / black_polymer / safety_yellow / safety_orange / industrial_blue |

## 部件多样性审计（Part Diversity Audit）
> baseline spec 未补完整审计。新增类别必须逐个核心部件填写本表。

| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| 待新增类别填写 | - | - | - | - | - |

## 约束
- 内层套筒尺寸必须小于外层。
- 所有 prismatic joint 的 axis 必须共线。
- 每一级伸出后仍要保留 overlap（min_overlap ≥ 0.6 × stage_length 推荐值）。
- end_effector 必须连接在最内层末端。
- locking_collar 位于两级套筒交界处。
- base_bracket 必须支撑 outer_stage。
- base part 命名建议包含 `base` / `support` / `bracket`，便于自动化校验。

## Validator
| 检查项 | 标准 |
|---|---|
| joint count | stage_count − 1 |
| joint type | 全部为 prismatic |
| axis collinearity | 所有伸缩轴共线 |
| nesting | 内层 bbox 小于外层 bbox |
| overlap | 每级有最小嵌套长度 |
| endpoint | end_effector 在最内层末端（若有） |
| no floating | collars / bolts / bracket 全连接 |

## Reject cases
- 多级管不嵌套。
- 各级伸缩方向不一致。
- prismatic axis 错误。
- 末端工具漂浮。
- 看起来像普通杆子，没有伸缩结构。

---
