# Ferris Wheel｜摩天轮 Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `ferris_wheel` |
| template path | `agent/templates/ferris_wheel.py` |
| test path | `tests/agent/test_ferris_wheel_template.py` |
| status | baseline spec for style reference only |

> 这是已有类别的 baseline spec，只用于参考 spec 写法、结构组织和 validator 写法。新增类别的部件来源必须来自新 spec 中被采纳且有 `model.py:Lx-Ly` 的 5 星样本源码片段。

## 核心身份
大型回转娱乐设施，由支撑框架、绕水平轴旋转的车轮、径向分布的吊舱组成；吊舱绕各自枢纽点摇晃或随轮反向同步旋转。

## 部件（Parts）

**必需**
```
support_frame（底座 + 支撑结构）
 ├── platform_slab
 ├── support_legs（a_frame / truss_tower / inclined_legs 三选一）
 ├── fixed_axle
 └── bearing_blocks

wheel（车轮）
 ├── rim（double_torus / single_torus / twin_rings / concentric_double 四选一）
 ├── central_hub
 ├── spokes
 └── gondola_pivot_bar_i（径向分布，i = 0..num_gondolas-1）

gondola_i（box_cabin / open_basket / glass_capsule / bucket_seat / rounded_pod 五选一）
 ├── hanger_pin
 └── cabin_body / windows / handles
```

**可选**
```
support_frame
 ├── platform_railings
 ├── drive_house
 ├── operator_booth
 ├── boarding_bridge
 ├── loading_plinth
 └── service_deck
```

## 关节（Joints）
| joint | 类型 | 含义 |
|---|---|---|
| wheel_rotation | revolute（range [0, 2π]，实现上等价于 continuous 整圈旋转） | 车轮绕固定水平轴旋转 |
| gondola_pivot_i | revolute | 第 i 个吊舱绕枢纽杆摇晃；`gondola_motion_mode = counter_rotate_mimic` 时设 Mimic（multiplier = -1.0）跟随 wheel_rotation |

## 已有模板写法参考
> 该字段只说明旧模板中可参考的写法，不表示部件来源。

rotary_post / radial_array / continuous_rotor / revolute_hinge / mimic_link / handle_grip

## 参数范围汇总
| 参数 | 取值建议 |
|---|---|
| num_gondolas | 4–20（推荐 8 / 12 / 16） |
| spoke_count | `num_gondolas × 2` 或 `× 3`（偶数化） |
| scale_mode | compact / normal / landmark（离散桶 + 桶内连续；spine 字段） |
| rim_radius | 按 scale_mode 派生：compact 0.66–0.90 / normal 0.78–1.10 / landmark 1.10–1.65 m |
| wheel_half_width | 按 scale_mode 派生：compact 0.090–0.112 / normal 0.095–0.125 / landmark 0.118–0.155 m |
| gondola_style | box_cabin / open_basket / glass_capsule / bucket_seat / rounded_pod |
| support_style | a_frame / truss_tower / inclined_legs |
| rim_style | double_torus / single_torus / twin_rings / concentric_double |
| hanger_style | pivot_bar / yoke_fork / between_rims / leveling_arm（受 rim_style 约束：between_rims 仅 twin_rings；leveling_arm 仅非双环） |
| gondola_motion_mode | free_swing / counter_rotate_mimic（建议权重 0.7 / 0.3） |
| frame_palette / cabin_palette / gondola_palette | 命名调色板，详见 [agent/templates/ferris_wheel.py](agent/templates/ferris_wheel.py) `PALETTES` 表 |

## 部件多样性审计（Part Diversity Audit）
> baseline spec 未补完整审计。新增类别必须逐个核心部件填写本表。

| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| 待新增类别填写 | - | - | - | - | - |

## 约束
- 车轮旋转轴必须水平（世界 X 轴 `(1, 0, 0)`），与固定轴共线。
- 所有吊舱必须绕枢纽杆绕 X 轴摇晃，范围 ±π。
- 吊舱枢纽点的径向距离必须随 `num_gondolas` 缩放，防止相邻吊舱相撞。
- 最低吊舱底部到地面的间隙 ≥ 0.025 m（GROUND_CLEARANCE）；若 `loading_plinth` enabled，预留额外 0.045 m。
- `between_rims` hanger_style 仅在 `rim_style = twin_rings` 时有效。
- `leveling_arm` 仅在非双环 rim_style 下使用。
- 轮毂与轴承块必须紧靠，不漂浮。
- 平台栏杆位置与支撑脚跨度对齐。
- 装饰子件（curbstone / rail_post_i / 颜色条纹）以 `parent.visual(...)` 挂载，不创建独立 part。

## Validator
| 检查项 | 标准 |
|---|---|
| wheel joint count | 恰好 1 个 revolute `wheel_rotation`（range [0, 2π]） |
| gondola joint count | 恰好 `num_gondolas` 个 revolute `gondola_pivot_i` |
| axis check | `wheel_rotation.axis = (1, 0, 0)`，所有 `gondola_pivot_i.axis = (1, 0, 0)` |
| motion limits | `wheel_rotation ∈ [0, 2π)`，`gondola_pivot_i ∈ [-π, π]` |
| spoke count | `len(spokes) = spoke_count` |
| gondola count | `len(gondolas) = num_gondolas` |
| rim consistency | rim_style 与几何一致（torus / twin rings / concentric） |
| hanger constraint | between_rims ↔ twin_rings；leveling_arm ↔ 非双环 |
| ground clearance | 最低吊舱底部到地面 ≥ 0.025 m |
| mimic check | `gondola_motion_mode = counter_rotate_mimic` 时所有 gondola joint 含 Mimic（multiplier = -1.0） |
| no floating | 吊舱枢纽、轴承块、平台栏杆、装饰件均连接 |
| identity | 必须认得出摩天轮 |

## Reject cases
- 车轮不旋转或 `wheel_rotation` 关节缺失（关节本身为 revolute 类型，range = [0, 2π]）。
- 吊舱数量与 `num_gondolas` 不符。
- 吊舱无法摇晃（`gondola_pivot` 缺失或 axis 错）。
- 吊舱漂浮在轮 / 支架外。
- 支撑脚无法接地或倾斜。
- hanger_style 与 rim_style 约束违反（如 `between_rims` 搭配 `double_torus`）。
- 最低吊舱与地面或 `loading_plinth` 穿模 > 0.025 m。
- 轮辋与辐条断开，视觉上不是一个整体。
- 颜色为裸 RGB 随机，无命名调色板。

---
