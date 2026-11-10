# Rolling Toolbox With Telescoping Handle｜带伸缩拉杆的轮式工具箱 Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `rolling_toolbox_with_telescoping_handle` |
| template path | `agent/templates/rolling_toolbox_with_telescoping_handle.py` |
| test path | `tests/agent/test_rolling_toolbox_with_telescoping_handle_template.py` |
| status | baseline spec for style reference only |

> 这是已有类别的 baseline spec，只用于参考 spec 写法、结构组织和 validator 写法。新增类别的部件来源必须来自新 spec 中被采纳且有 `model.py:Lx-Ly` 的 5 星样本源码片段。

## 核心身份
可移动工具箱，带箱体、箱盖、锁扣、后轮、前支撑、伸缩拉杆。

## 部件（Parts）
```
toolbox_body                          # 箱体主 part
 ├── lid                              # 箱盖 part（revolute 到 body）
 ├── latch_0 / latch_1 / ...          # 锁扣，每个独立 part（不存在 front_latches 容器）
 ├── rear_wheel_0 / rear_wheel_1      # 后轮 part（每个独立，不存在 rear_wheels 容器）
 ├── front_caster_*（可选，front_support = small_casters 时）
 ├── handle_inner                     # 整体拉杆 part（prismatic）
 ├── handle_stage_2（可选，handle_stage_count ≥ 2 时）  # 二级嵌套段
 ├── drawer（可选，前抽屉，prismatic）
 └── （visual 子件挂在 body / lid 上）handle_outer_sleeve_l/r（导套）、carry_handle、front_feet、side_ribs、corner_guards、装饰
```

注：拉杆导套 (`handle_outer_sleeve_l/r`)、提手 (`carry_handle`)、脚 (`front_feet`)、护角等是 visual 子件,不创建独立 part。

## 关节（Joints）
| joint | 类型 | 含义 |
|---|---|---|
| wheel_joint_i | continuous | 后轮旋转 |
| handle_stage_joint | prismatic | 拉杆伸缩 |
| handle_stage_2_joint | prismatic（可选，stage_count ≥ 2 时使用） | 二级嵌套伸缩段 |
| lid_joint | revolute / fixed | 箱盖开合 |
| latch_joint_i | revolute | 锁扣翻转 |
| drawer_joint | prismatic（可选） | 前抽屉抽出 |

## 已有模板写法参考
> 该字段只说明旧模板中可参考的写法，不表示部件来源。

telescoping_tube / continuous_wheel / revolute_hinge / latch_lock / handle_grip / guide_shoe / caster_wheel

## 参数范围汇总
| 参数 | 取值建议 |
|---|---|
| box_size | compact / standard / jobsite large（离散桶 + 桶内连续） |
| wheel_size | small / medium / rugged large（离散桶 + 桶内连续） |
| wheel_tread | smooth / ribbed / chunky |
| handle_stage_count | 1 / 2 |
| handle_shape | U-shape / twin rod / suitcase-style |
| latch_count | 1 / 2 / 3 |
| lid_style | flat / raised / split |
| front_support | feet / small_casters |
| corner_guard | none / reinforced |
| material_style | yellow_black / red_black / gray / blue_black |

## 部件多样性审计（Part Diversity Audit）
> baseline spec 未补完整审计。新增类别必须逐个核心部件填写本表。

| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| 待新增类别填写 | - | - | - | - | - |

## 约束
- 后轮必须靠近箱体后下方。
- 拉杆必须从后侧或顶部后方伸出。
- 拉杆伸缩 axis 应接近竖直或后倾 ≤ 15°。
- 内外拉杆/导套必须保持嵌套，伸出末端导杆不脱离导套。
- 轮子必须接近地面。
- 锁扣必须在箱体前侧。
- 箱盖必须在箱体上方。

## Validator
| 检查项 | 标准 |
|---|---|
| wheel joint | 后轮为 continuous |
| handle joint | 拉杆为 prismatic |
| nesting | 拉杆杆体始终在导套内 |
| wheel contact | wheels 接近地面 |
| latch position | latch 在前侧 |
| lid position | lid 在上方 |
| no floating | handle / wheel / latch 全连接 |

## Reject cases
- 没有轮子。
- 拉杆不是伸缩结构。
- 后轮位置错误。
- 拉杆漂浮。
- 看起来不像工具箱。

---
