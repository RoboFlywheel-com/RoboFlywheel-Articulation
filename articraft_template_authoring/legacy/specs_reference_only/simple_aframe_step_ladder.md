# Simple Aframe Step Ladder｜简单 A 字折叠梯 Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `simple_aframe_step_ladder` |
| template path | `agent/templates/simple_aframe_step_ladder.py` |
| test path | `tests/agent/test_simple_aframe_step_ladder_template.py` |
| status | baseline spec for style reference only |

> 这是已有类别的 baseline spec，只用于参考 spec 写法、结构组织和 validator 写法。新增类别的部件来源必须来自新 spec 中被采纳且有 `model.py:Lx-Ly` 的 5 星样本源码片段。

## 核心身份
A 字形折叠梯，前侧为爬梯框，后侧为支撑框，通过顶部铰链开合，带踏板和脚垫。

## 部件（Parts）
```
front_frame                           # 前爬梯框 part；左右立柱、踏板、top_cap 都以 visual 挂在它上
rear_support_frame 或 rear_frame      # 后支撑框 part；左右立柱、横撑、feet 以 visual 挂在它上，绕 frame_fold_joint 连到 front_frame
spreader_i（可选，spreader_type ≠ none 时）  # 防张开连杆，每条独立 part
```

注：top_cap、踏板、立柱、feet 均按 §0 「非可动子件挂载」用 `front_frame.visual(...)` / `rear_frame.visual(...)` 实现，不创建独立 part；折叠铰链就是 `frame_fold_joint`，不在 top_cap 内单独建 joint。

## 关节（Joints）
| joint | 类型 | 含义 |
|---|---|---|
| frame_fold_joint | revolute | 后支撑框相对前爬梯框折叠 |
| spreader_joint_i | revolute / fixed | 防张开连杆（可选） |

## 已有模板写法参考
> 该字段只说明旧模板中可参考的写法，不表示部件来源。

revolute_hinge / folding_link_chain

## 参数范围汇总
| 参数 | 取值建议 |
|---|---|
| ladder_height_class | low / medium / tall（离散桶 + 桶内连续值，每 class 一组实际 `top_rail_z` 范围；spine 字段） |
| step_count | 派生自 `ladder_height_class`：low → {2, 3}；medium → {3, 4, 5}；tall → {5, 6, 7} |
| frame_angle | 15–35° |
| step_style | flat / narrow rung / anti-slip；anti-slip 必须通过 grip 材质/凸起几何呈现 |
| rail_cross_section | rectangular / round |
| rear_support_style | simple / cross-braced |
| top_cap_style | narrow cap / tool tray / flat |
| spreader_type | none / side bar / folding link |
| foot_style | rubber pads / wide pads |
| material_style | aluminum / fiberglass / steel |

## 部件多样性审计（Part Diversity Audit）
> baseline spec 未补完整审计。新增类别必须逐个核心部件填写本表。

| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| 待新增类别填写 | - | - | - | - | - |

## 约束
- 踏板必须连接左右前立柱。
- 后支撑框必须通过顶部铰链接到前爬梯框。
- 前后脚都应接近地面。
- 展开后必须形成 A 字形。
- 折叠关节轴必须沿梯子宽度方向（世界坐标系下 Y 轴），不允许沿前后方向（X 轴）。
- 防张开连杆不能漂浮；若不存在，参数中必须显式声明 `spreader_type = none`。

## Validator
| 检查项 | 标准 |
|---|---|
| step count | 与参数一致 |
| hinge position | hinge 在顶部 |
| fold axis | 必须为宽度方向（Y 轴） |
| foot contact | 四个脚接近地面 |
| A shape | 前后框形成夹角 |
| step attachment | steps 连接左右 rail |
| collision | 折叠/打开时不严重穿模 |
| spreader consistency | spreader_type 与 spreader part 计数一致（0、2 或 4） |
| anti-slip evidence | step_style = anti-slip 时必须有 grip 几何或材质 |

## Reject cases
- 后支撑框没有铰链。
- 梯子不是 A 字形。
- 踏板漂浮。
- 脚不接地。
- fold joint axis 错为前后方向（X 轴）。

---
