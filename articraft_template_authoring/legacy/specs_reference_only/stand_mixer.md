# Stand Mixer｜厨师机 / 台式搅拌机 Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `stand_mixer` |
| template path | `agent/templates/stand_mixer.py` |
| test path | `tests/agent/test_stand_mixer_template.py` |
| status | baseline spec for style reference only |

> 这是已有类别的 baseline spec，只用于参考 spec 写法、结构组织和 validator 写法。新增类别的部件来源必须来自新 spec 中被采纳且有 `model.py:Lx-Ly` 的 5 星样本源码片段。

## 核心身份
台式厨师机，带底座、立柱、可抬起机头、搅拌碗、搅拌头、速度旋钮或控制件。

## 部件（Parts）
```
mixer_base                            # 底座 part；speed_selector / head_lock_control 等以 visual 挂在 base 或 head 上
bowl_carriage（可选；bowl_lift_type ≠ none 时）  # bowl 滑台 part
mixing_bowl                           # 搅拌碗 part（可 fixed 到 base / 可 prismatic 到 carriage）
mixer_head                            # 机头 part（revolute 抬起；motor_housing / attachment_socket 是 visual 子件）
tool_attachment                       # 搅拌工具 part（continuous 旋转）
```

注：motor_housing、attachment_socket、speed_selector 旋钮、head_lock 拨杆等都按 §0 「非可动子件挂载」用 `parent.visual(...)` 实现，不是独立 part。

## 关节（Joints）
| joint | 类型 | 含义 |
|---|---|---|
| head_tilt_joint | revolute | 机头绕后侧铰链抬起 |
| tool_spin_joint | continuous | 搅拌工具绕竖直轴旋转 |
| bowl_lift_or_slide_joint | prismatic | 碗运动（前后滑动 X/Y 轴 或 升降 Z 轴，可选；fixed bowl 仅在 prompt 明确说明时允许） |
| speed_selector_joint | continuous（可选，无控件时省略） | 速度旋钮 |
| head_lock_joint | revolute（可选） | 机头锁定拨杆 |

## 已有模板写法参考
> 该字段只说明旧模板中可参考的写法，不表示部件来源。

revolute_hinge / continuous_rotor / prismatic_slide / button_slider

## 参数范围汇总
| 参数 | 取值建议 |
|---|---|
| head_shape | rounded / boxy / retro / industrial |
| base_shape | oval / rectangle / rounded |
| bowl_shape | deep_bowl / wide_bowl / tapered |
| bowl_size_class | compact / standard / large（离散桶 + 桶内连续值） |
| tool_type | dough_hook / whisk / flat_beater |
| head_tilt_range_deg | 25–60° |
| bowl_lift_type | none（fixed） / slide_horizontal / lever_lift |
| bowl_slide_axis | x / y（仅 bowl_lift_type = slide_horizontal 时） |
| bowl_slide_range | short / medium（离散桶 + 桶内连续） |
| speed_selector_style | knob / lever / dial / none |
| speed_selector_mount | base_fixed / head_mounted |
| control_count | 1 / 2 / 3 |
| material_style | pastel / stainless / black / retro |
| detail_level | minimal / normal / detailed |

## 部件多样性审计（Part Diversity Audit）
> baseline spec 未补完整审计。新增类别必须逐个核心部件填写本表。

| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| 待新增类别填写 | - | - | - | - | - |

## 约束
- mixer_head 必须连接到 rear_column。
- head_tilt_joint 必须位于机头后侧或立柱顶部，默认 axis = (0, -1, 0)，部分样本使用 (1, 0, 0) 作为侧倾铰链亦可接受。
- tool_attachment 必须位于机头下方，并对准搅拌碗中心附近。
- tool_spin_joint 的 axis 应近似竖直 `(0, 0, 1)`。
- mixing_bowl 必须位于机头下方，不可漂浮。
- bowl 运动 axis 可为前后（X/Y）或竖直（Z，升降臂式）。
- speed_selector 必须附着在底座或机头侧面。
- 不表达真实齿轮传动，只表达搅拌头连续旋转。

## Validator
| 检查项 | 标准 |
|---|---|
| head joint | 有 revolute head tilt joint |
| tool joint | 有 continuous tool spin joint |
| tool alignment | 搅拌工具位于 bowl 中心附近 |
| bowl placement | bowl 在 base 上，且在 head 下方 |
| head sweep | 机头抬起不严重穿过立柱或碗 |
| control attachment | knob / lever 附着在主体上 |
| bowl motion | bowl 若可动，必须有 prismatic joint；fixed bowl 必须在 prompt 中说明 |
| identity | 必须像 stand mixer |
| no floating | bowl / tool / controls 全连接 |

## Reject cases
- 没有搅拌碗。
- 没有可旋转搅拌工具。
- 机头和立柱断开。
- 搅拌头不在碗上方。
- 变成 blender 或普通碗。

---
