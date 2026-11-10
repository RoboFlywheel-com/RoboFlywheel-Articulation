# Revolving Door｜旋转门 Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `revolving_door` |
| template path | `agent/templates/revolving_door.py` |
| test path | `tests/agent/test_revolving_door_template.py` |
| status | baseline spec for style reference only |

> 这是已有类别的 baseline spec，只用于参考 spec 写法、结构组织和 validator 写法。新增类别的部件来源必须来自新 spec 中被采纳且有 `model.py:Lx-Ly` 的 5 星样本源码片段。

## 核心身份
中心柱带 2、3 或 4 个径向门翼，在圆筒形或半圆形外壳中绕竖直轴连续旋转。单台旋转门 = 一个中心柱 + 一组门翼；多台 airlock 复合属于多个独立 instance，不属于本类别。

## 部件（Parts）
```
outer_drum（可选）                    # 静态外壳 part；top_cap / bottom_ring / side_glass_panels 等以 visual 挂在 drum 上
central_post                          # 旋转中心柱 part
 └── wing_0 / wing_1 / ...（visual）  # 门翼以 parent.visual(...) 挂在 central_post 上，作为 rotor 整体一起旋转，不创建独立 part
```

## 关节（Joints）
| joint | 类型 | 含义 |
|---|---|---|
| central_rotation_joint（命名风格 `*_spin` / `*_rotation`） | continuous | 中心门翼组件绕竖直轴旋转 |

## 已有模板写法参考
> 该字段只说明旧模板中可参考的写法，不表示部件来源。

rotary_post / radial_array / handle_grip

## 参数范围汇总
| 参数 | 取值建议 |
|---|---|
| wing_count | 3 / 4 |
| drum_type | full_cylinder / partial / open_frame / square |
| door_radius | small / medium / large（离散桶 + 桶内连续） |
| door_height | low / standard / tall（离散桶 + 桶内连续） |
| wing_material | glass / metal_frame / wood_panel |
| push_bar_style | straight / curved / d_handle / none |
| canopy_style | single_disc / soffit_crown / tiered |
| panel_density | low / med / high |
| canopy_skirt | none / low / tall |
| header_band | none / narrow / bold |
| kick_panel | none / low / tall |
| motor_housing | none / top_box（与 finial 装饰互斥） |
| top_cap_style | flat / thick / decorative |
| bottom_ring | none / low / full |
| sensor_module | none / small_blocks |
| material_style | glass / dark_metal / aluminum |

## 部件多样性审计（Part Diversity Audit）
> baseline spec 未补完整审计。新增类别必须逐个核心部件填写本表。

| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| 待新增类别填写 | - | - | - | - | - |

## 约束
- 门翼必须等角度分布。
- 中心旋转轴必须竖直 `(0, 0, 1)`。
- 门翼外缘不能超出外壳半径太多。
- 门翼必须连接到中心柱。
- 一个 record 内必须只有一组 wings；多台 airlock 必须拆分为多个 record。
- central_post + wings 作为整体旋转。
- 不能让每个 wing 独立乱转。

## Validator
| 检查项 | 标准 |
|---|---|
| joint count | 至少 1 个 continuous |
| axis check | 旋转轴竖直 |
| radial distribution | wings 等角度（容差 < 1°） |
| radius check | wings 在 drum 内 |
| connectivity | wings 连接 central post |
| no floating | push bars / caps / panels 连接 |
| single unit | 每个 record 只允许一组 central_post + wings |
| identity | 必须像 revolving door |

## Reject cases
- 变成普通门。
- 门翼数量不对称。
- 中心轴不竖直。
- 门翼穿出外壳太多。
- 每个门翼独立乱转。
- 一个 record 中出现两组以上独立旋转的 rotor。

---
