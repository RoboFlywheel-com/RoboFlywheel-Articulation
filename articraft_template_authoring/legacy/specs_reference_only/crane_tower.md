# Crane Tower Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `crane_tower` |
| template path | `agent/templates/crane_tower.py` |
| test path | `tests/agent/test_crane_tower_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 28 |
| read_count | 28 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
塔式/门式起重机，至少包含承载基座、竖向支撑或门架、可回转或可平移的上部起重结构、长臂/桥梁、吊钩或吊具。核心活动方式是上部结构回转、吊运小车沿梁/臂滑动、或臂架俯仰/伸缩；静态杆件和配重只用于支撑类别身份。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_crane_tower_0008` | `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L64-L152` | square lattice mast and triangular truss helper patterns |
| S2 | `rec_crane_tower_0008` | `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L166-L208` | fixed foundation, pedestal cap, tall mast envelope |
| S3 | `rec_crane_tower_0008` | `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L214-L354` | hammerhead upperworks, cab, jib, counter-jib, ballast, rails |
| S4 | `rec_crane_tower_0008` | `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L356-L415` | trolley part and vertical slew / jib-axis prismatic joints |
| S5 | `rec_crane_tower_4c331560b98145f9b6f8d8d64e6883c5` | `data/records/rec_crane_tower_4c331560b98145f9b6f8d8d64e6883c5/revisions/rev_000001/model.py:L352-L501` | luffing jib, hook block, luff revolute joint, fixed hook suspension |
| S6 | `rec_crane_tower_6d8cd5ee74724f06a1be37a625472b4c` | `data/records/rec_crane_tower_6d8cd5ee74724f06a1be37a625472b4c/revisions/rev_000001/model.py:L162-L325` | self-erecting wheeled base, outriggers, telescoping mast sleeve |
| S7 | `rec_crane_tower_6d8cd5ee74724f06a1be37a625472b4c` | `data/records/rec_crane_tower_6d8cd5ee74724f06a1be37a625472b4c/revisions/rev_000001/model.py:L568-L608` | mast extension, jib slew, and trolley travel articulation set |
| S8 | `rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602` | `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L86-L187` | gantry runway rails and portal frame layout |
| S9 | `rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602` | `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L244-L440` | bridge girder, crab trolley, hook block, dual prismatic gantry joints |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `base` | 地面承载件，可为固定基础、移动底盘、法兰 pedestal 或 gantry runway | `base_style`, `base_width`, `base_depth`, `base_height`, `outrigger_count` | S2 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L166-L208`; S6 / `data/records/rec_crane_tower_6d8cd5ee74724f06a1be37a625472b4c/revisions/rev_000001/model.py:L162-L325`; S8 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L86-L187` |
| `mast` | 竖向支撑主体，固定或伸缩；gantry variant 中由 `portal_frame` 替代 | `mast_profile`, `mast_height`, `mast_width`, `mast_panel_count`, `telescoping_stage_count` | S1 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L64-L152`; S2 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L166-L208`; S6 / `data/records/rec_crane_tower_6d8cd5ee74724f06a1be37a625472b4c/revisions/rev_000001/model.py:L162-L325` |
| `upperworks` | 连接 mast 顶部的可回转上部结构，含转台、机械平台、司机室或 machinery house | `cab_style`, `upperworks_width`, `upperworks_depth`, `has_cab` | S3 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L214-L354` |
| `jib` / `boom` | 主起重臂，可为水平 truss jib、luffing boom、knuckle arms 或 gantry bridge | `jib_layout`, `jib_length`, `jib_pitch`, `truss_panel_count`, `boom_count` | S1 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L64-L152`; S3 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L214-L354`; S5 / `data/records/rec_crane_tower_4c331560b98145f9b6f8d8d64e6883c5/revisions/rev_000001/model.py:L352-L501`; S9 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L244-L440` |
| `counter_jib` | hammerhead/luffing variants 的反向短臂和 ballast 承载件；gantry/derrick 可省略 | `counter_jib_length`, `ballast_block_count`, `ballast_mass_visual_scale` | S3 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L299-L329`; S5 / `data/records/rec_crane_tower_4c331560b98145f9b6f8d8d64e6883c5/revisions/rev_000001/model.py:L352-L501` |
| `trolley` | 沿水平 jib 或 bridge girder 运动的吊运小车；luffing fixed-tip 可选 | `trolley_mode`, `trolley_width`, `trolley_travel` | S4 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L356-L415`; S9 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L323-L440` |
| `hook_block` | 吊钩/吊具，可作为 trolley 子件或 jib 端部固定子件 | `hook_block_style`, `hook_drop`, `has_sheaves` | S5 / `data/records/rec_crane_tower_4c331560b98145f9b6f8d8d64e6883c5/revisions/rev_000001/model.py:L414-L501`; S9 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L372-L440` |
| `portal_frame` | gantry variant 的双腿门架和轨道，optional | `portal_span`, `portal_height`, `runway_length` | S8 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L86-L187` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `slew_joint` | continuous 或 revolute | `(0, 0, 1)` | mast top / pedestal top | continuous 或 `[-pi, pi]` | 上部结构绕竖直轴回转 | S4 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L393-L401`; S7 / `data/records/rec_crane_tower_6d8cd5ee74724f06a1be37a625472b4c/revisions/rev_000001/model.py:L582-L596` |
| `trolley_travel_joint` | prismatic | `(1, 0, 0)` | jib lower rail root | `[0, jib_length - trolley_clearance]` | 小车沿水平 jib 或 bridge 横向滑动 | S4 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L402-L415`; S9 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L424-L440` |
| `luff_joint` | revolute | `(0, 1, 0)` or `(0, -1, 0)` | jib heel at upperworks cheek | `[0, 0.95]` rad | luffing boom 向上俯仰 | S5 / `data/records/rec_crane_tower_4c331560b98145f9b6f8d8d64e6883c5/revisions/rev_000001/model.py:L469-L501` |
| `mast_extension_joint` | prismatic | `(0, 0, 1)` | top of mast sleeve | `[0, extension_travel]` | self-erecting variant 的内桅杆升降 | S7 / `data/records/rec_crane_tower_6d8cd5ee74724f06a1be37a625472b4c/revisions/rev_000001/model.py:L568-L581` |
| `bridge_travel_joint` | prismatic | `(0, 1, 0)` | portal rail start | `[0, runway_length - bridge_depth]` | gantry bridge 沿纵向 runway 移动 | S9 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L410-L423` |
| `hook_suspension_joint` | fixed | n/a | below trolley or jib tip | n/a | 吊钩固定悬挂在 trolley 或 jib tip 下方；若后续实现 hoist，可扩展为 prismatic | S5 / `data/records/rec_crane_tower_4c331560b98145f9b6f8d8d64e6883c5/revisions/rev_000001/model.py:L492-L501`; S9 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L438-L440` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `crane_variant` | enum | `hammerhead` / `luffing_jib` / `self_erecting` / `derrick_pedestal` / `knuckle_boom` / `gantry_bridge` | `hammerhead` | 决定 `mast_profile`, `jib_layout`, joint set | S3 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L214-L354`; S5 / `data/records/rec_crane_tower_4c331560b98145f9b6f8d8d64e6883c5/revisions/rev_000001/model.py:L352-L501`; S8 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L86-L187` |
| `mast_profile` | enum | `square_lattice` / `square_telescoping` / `round_pedestal` / `portal_frame` | `square_lattice` | `crane_variant=gantry_bridge` 时为 `portal_frame` | S1 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L64-L152`; S6 / `data/records/rec_crane_tower_6d8cd5ee74724f06a1be37a625472b4c/revisions/rev_000001/model.py:L162-L325`; S8 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L86-L187` |
| `base_style` | enum | `fixed_foundation` / `wheeled_outrigger` / `pedestal_flange` / `portal_runway` | `fixed_foundation` | `self_erecting` prefers `wheeled_outrigger`; `gantry_bridge` requires `portal_runway` | S2 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L166-L208`; S6 / `data/records/rec_crane_tower_6d8cd5ee74724f06a1be37a625472b4c/revisions/rev_000001/model.py:L162-L325`; S8 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L86-L187` |
| `jib_layout` | enum | `horizontal_jib_counterjib` / `luffing_single_boom` / `knuckle_two_arm` / `gantry_bridge` | `horizontal_jib_counterjib` | 派生 `counter_jib`、`luff_joint`、`trolley_mode` | S3 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L252-L329`; S5 / `data/records/rec_crane_tower_4c331560b98145f9b6f8d8d64e6883c5/revisions/rev_000001/model.py:L352-L501`; S9 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L244-L440` |
| `mast_height` | float | `8.0-24.0` | `18.0` | 影响 slew origin z 与 jib root z | S2 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L192-L208` |
| `mast_panel_count` | int | `4-14` | `9` | lattice level count | S1 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L64-L102` |
| `jib_length` | float | `8.0-26.0` | `18.0` | trolley travel upper clamp | S3 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L252-L282`; S4 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L402-L415` |
| `counter_jib_length_ratio` | float | `0.25-0.55` | `0.38` | `counter_jib_length = jib_length * ratio` | S3 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L299-L329` |
| `trolley_mode` | enum | `jib_trolley` / `fixed_tip_hook` / `bridge_crab_trolley` | `jib_trolley` | luffing may use `fixed_tip_hook`; gantry requires `bridge_crab_trolley` | S4 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L356-L415`; S5 / `data/records/rec_crane_tower_4c331560b98145f9b6f8d8d64e6883c5/revisions/rev_000001/model.py:L414-L501`; S9 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L323-L440` |
| `hook_block_style` | enum | `simple_block` / `sheaved_block` / `curved_hook` | `sheaved_block` | controls hook visuals and cable drop | S5 / `data/records/rec_crane_tower_4c331560b98145f9b6f8d8d64e6883c5/revisions/rev_000001/model.py:L414-L463`; S9 / `data/records/rec_crane_tower_ec68175e8e8a495e8e0ec300303dc602/revisions/rev_000001/model.py:L372-L397` |
| `slew_range` | float or enum | `continuous` / `1.57-6.28` rad | `continuous` | maps to continuous/revolute joint limits | S4 / `data/records/rec_crane_tower_0008/revisions/rev_000001/model.py:L393-L401` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| base | fixed concrete foundation / wheeled base with outriggers / round pedestal flange / portal runway rails | no | yes | `base_style` | 基座拓扑不同，不能用尺寸连续缩放表示 |
| mast / support | square lattice mast / telescoping square sleeve / round pedestal mast / portal frame | no | yes | `mast_profile` | 支撑截面和拓扑变化是类别可读性的关键 |
| jib / boom | horizontal hammerhead jib / luffing single boom / knuckle boom / gantry bridge | no | yes | `jib_layout`, `crane_variant` | 臂架关节、父子链和外形均不同 |
| counter_jib / ballast | present with counterweights / short luffing tail / absent in gantry or pedestal samples | no | yes | `jib_layout`, `ballast_block_count` | 是否存在反臂是结构差异，不只是长度 |
| trolley | jib trolley / gantry crab trolley / absent with fixed-tip hook | no | yes | `trolley_mode` | 运动载体和滑动轴来源不同 |
| hook_block | simple block / sheaved block / curved hook mesh | no | yes | `hook_block_style` | 吊钩形态差异影响识别，但可保持同一悬挂父件 |
| cab / machinery house | center cab / side cab / machinery house only / none | no | yes | `cab_style` | 司机室有无和位置是显著视觉差异 |
| truss bracing | panel count and member radius only | yes | no | `mast_panel_count`, `truss_panel_count` | 观察到主要是数量和比例连续变化，lattice 拓扑稳定 |

## 组合逻辑（Composition Logic）
1. 根据 `crane_variant` 先选择 spine：tower spine 使用 `base -> mast -> upperworks`，gantry spine 使用 `track_base -> portal_frame -> bridge_girder`。
2. 生成承载基座；`wheeled_outrigger` 添加四个 outrigger visual，`portal_runway` 添加双轨道和门架。
3. 生成 mast 或 portal frame；lattice 和 truss 由 member helper 按 panel count 派生。
4. tower variants 在 mast 顶部创建 `upperworks` 并添加 `slew_joint`；gantry variant 用 `bridge_travel_joint` 替代 slew。
5. 按 `jib_layout` 添加 horizontal jib/counter-jib、luffing boom、knuckle arms 或 bridge girder。
6. `trolley_mode=jib_trolley` 时 trolley 挂在 jib/upperworks 下并沿 X 滑动；`bridge_crab_trolley` 时 bridge 先沿 Y 滑动，trolley 再沿 X 滑动；`fixed_tip_hook` 时 hook fixed 在 jib tip。
7. 所有配重、cables、walkway、cab glazing、warning marks 优先作为对应 parent visual，不创建独立活动件。

## 已有模板写法参考
telescoping_tube / prismatic_slide / revolute_hinge / rotary_post / continuous_rotor

## 约束
- tower variants 必须有可辨识的竖向 mast 或 pedestal，gantry variant 必须有 portal frame 和 runway rails。
- `slew_joint` 的 axis 必须为世界竖直 `(0, 0, 1)`。
- `trolley_travel_joint` 必须与 jib/bridge rail 平行，行程不得超过可见轨道长度。
- luffing boom 的 pivot 必须位于 upperworks cheek 或 mast head，打开范围不能让 boom 穿入 mast。
- hook block 必须位于 trolley 下方或 jib tip 下方，不能漂浮。
- `counter_jib` 和 ballast 只在对应 layout 中生成，不能悬空或位于主 jib 同侧。
- gantry bridge travel 与 crab trolley travel 必须正交。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | 至少包含 base/support、jib/bridge、hook block 三类核心部件 |
| support variant | `mast_profile` 与 `crane_variant` 一致；tower 不缺 mast，gantry 不缺 portal frame |
| joint count | hammerhead/self_erecting 至少 2 个活动 joint；luffing 至少 slew + luff；gantry 至少 2 个 prismatic |
| slew axis | tower slew axis 为 `(0, 0, 1)` |
| trolley axis | trolley slide 轴与可见 rail 平行，并且 range 小于 rail 长度 |
| luff range | luffing jib 在上下限姿态不穿 mast，tip 高度随正向 pose 上升 |
| mast extension | telescoping mast 保持 retained insertion 且 axis 为 `(0, 0, 1)` |
| hook placement | hook block 始终在 trolley 或 jib tip 下方 |
| part diversity | `base_style`, `mast_profile`, `jib_layout`, `trolley_mode`, `hook_block_style` 均存在并驱动几何分支 |
| no floating | cab、ballast、walkway、cables、hook 均连接到主树 |

## Reject cases
- 没有吊钩或吊具，导致看起来像普通塔架。
- mast/portal frame 和 jib/bridge 脱节或漂浮。
- 上部回转轴不是竖直轴。
- trolley 滑动方向与可见 jib/bridge rail 不一致。
- 用一根实心杆替代 lattice/truss，失去塔吊/门吊身份。
- luffing boom hinge 放在臂中部或地面，运动不可信。
- ballast 悬空或出现在主 jib 端部。
- gantry variant 只有桥梁没有 runway rails 和门架支撑。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
