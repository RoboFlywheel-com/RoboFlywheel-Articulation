# Tackle Box With Simple Hinged Lid｜带简单铰链盖的钓具箱 / 工具箱 Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `tackle_box_with_simple_hinged_lid` |
| template path | `agent/templates/tackle_box_with_simple_hinged_lid.py` |
| test path | `tests/agent/test_tackle_box_with_simple_hinged_lid_template.py` |
| status | baseline spec for style reference only |

> 这是已有类别的 baseline spec，只用于参考 spec 写法、结构组织和 validator 写法。新增类别的部件来源必须来自新 spec 中被采纳且有 `model.py:Lx-Ly` 的 5 星样本源码片段。

## 核心身份
一个箱体，带后侧铰链盖，通常带前侧锁扣、提手，可有内部托盘和分隔格。

## 部件（Parts）

**必需**（参考 [agent/templates/tackle_box_with_simple_hinged_lid.py](agent/templates/tackle_box_with_simple_hinged_lid.py)）
```
body                                  # 箱体主 part
 └── lid                              # 盖子 part，绕后侧 revolute 连接到 body；铰链硬件以 visual 形式挂在 body / lid 上，不是独立 part
      └── handle / lid_handle（visual 子件，挂在 lid 上）
```

**可选**
```
latch_0 / latch_1 / ...   # 锁扣，每个独立 part（不是 front_latches 容器），revolute 连接到 body
feet / corner_guards / ribs / trays   # 全部为 body 的 visual 子件，不创建 part
```

注：inner_tray、corner_guard、加强筋、feet 一律按 §0 「非可动子件挂载」规则用 `body.visual(...)` 实现，不作为独立 part。

## 关节（Joints）
| joint | 类型 | 含义 |
|---|---|---|
| lid_joint | revolute | 盖子绕后侧铰链打开 |
| latch_joint_i | revolute / fixed（可缺省，若 latch_count = 0） | 锁扣翻转 |
| handle_joint | revolute / fixed（可缺省） | 提手翻转 |

## 已有模板写法参考
> 该字段只说明旧模板中可参考的写法，不表示部件来源。

revolute_hinge / latch_lock / handle_grip

## 参数范围汇总
| 参数 | 取值建议 |
|---|---|
| box_aspect_ratio | long / compact / deep |
| lid_style | flat / raised / ribbed / recessed |
| latch_count | 0 / 1 / 2 / 3 |
| latch_style | flip_tab / clamp / hook |
| handle_style | top bar / folding / molded / none |
| tray_count | 0 / 1 / 2 |
| compartment_count | 2–12 |
| corner_guard | none / small / reinforced |
| feet_count | 0 / 4 |
| material_style | plastic / metal / rugged polymer |

## 部件多样性审计（Part Diversity Audit）
> baseline spec 未补完整审计。新增类别必须逐个核心部件填写本表。

| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| 待新增类别填写 | - | - | - | - | - |

## 约束
- lid_joint 必须在箱体后侧。
- 若存在 latch，必须在前侧或前侧附近。
- inner_tray 必须在箱体内部。
- 若存在 carry_handle，必须连接在盖子或箱体上方。
- 盖子打开范围建议 60–120°（0.0–2.1 rad）。
- 锁扣（若存在）不能漂浮在箱体前方。

## Validator
| 检查项 | 标准 |
|---|---|
| lid joint | 必须有 revolute lid joint |
| hinge position | hinge 在后侧边缘 |
| latch position | 若 latch_count > 0，必须在前侧 |
| lid sweep | 盖子打开不严重穿过 body |
| tray containment | tray 在 box 内 |
| no floating | 已有零件全部连接 |
| identity | 必须像钓具箱 / 工具箱 |

## Reject cases
- 没有可动盖子。
- 铰链在箱体中间。
- 锁扣漂浮（若有）。
- 内部托盘在箱外。
- 变成普通 storage bin。

---
