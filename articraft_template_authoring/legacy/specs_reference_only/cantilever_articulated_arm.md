# Cantilever Articulated Arm Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `cantilever_articulated_arm` |
| template path | `agent/templates/cantilever_articulated_arm.py` |
| test path | `tests/agent/test_cantilever_articulated_arm_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 39 |
| read_count | 39 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
悬臂式多关节机械臂，由固定底座/墙座支撑一串外伸 link，并通过 shoulder、elbow、wrist 等 revolute joints 改变末端位置。类别身份来自清晰的串联悬臂链和端部工具/面板，而不是单根静态梁。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | rec_cantilever_articulated_arm_0002 | `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L106-L215` | pedestal + yaw housing + upper/forearm/tool head，含 yaw/shoulder/elbow/wrist |
| S2 | rec_cantilever_articulated_arm_033009cff45d49b98764c004628c5a04 | `data/records/rec_cantilever_articulated_arm_033009cff45d49b98764c004628c5a04/revisions/rev_000001/model.py:L197-L280` | root block、forked upper/fore links、end plate、同平面三段 pitch chain |
| S3 | rec_cantilever_articulated_arm_482bb4bc30fc4ab9a905d6a030180276 | `data/records/rec_cantilever_articulated_arm_482bb4bc30fc4ab9a905d6a030180276/revisions/rev_000001/model.py:L221-L336` | underslung support frame、shoulder/elbow/wrist links、三段 pitch joints |
| S4 | rec_cantilever_articulated_arm_0001 | `data/records/rec_cantilever_articulated_arm_0001/revisions/rev_000001/model.py:L112-L200` | planar swing-arm style with support, upper_arm, forearm, wrist and Z-axis revolute chain |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| base_support | required；固定底座、墙座、立柱、pedestal 或 support frame | base_mount_style, base_height, base_width, mount_orientation | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L106-L125`; S2 / `data/records/rec_cantilever_articulated_arm_033009cff45d49b98764c004628c5a04/revisions/rev_000001/model.py:L197-L211`; S3 / `data/records/rec_cantilever_articulated_arm_482bb4bc30fc4ab9a905d6a030180276/revisions/rev_000001/model.py:L221-L231` |
| shoulder_link | required；第一段承重悬臂，通常带根部 lug/fork | shoulder_link_length, link_profile, fork_gap | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L127-L136`; S2 / `data/records/rec_cantilever_articulated_arm_033009cff45d49b98764c004628c5a04/revisions/rev_000001/model.py:L213-L226`; S3 / `data/records/rec_cantilever_articulated_arm_482bb4bc30fc4ab9a905d6a030180276/revisions/rev_000001/model.py:L233-L252` |
| elbow_link | required；第二段 forearm/forelink | elbow_link_length, link_profile, taper_ratio | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L138-L147`; S2 / `data/records/rec_cantilever_articulated_arm_033009cff45d49b98764c004628c5a04/revisions/rev_000001/model.py:L228-L241`; S3 / `data/records/rec_cantilever_articulated_arm_482bb4bc30fc4ab9a905d6a030180276/revisions/rev_000001/model.py:L254-L273` |
| wrist_or_end_effector | required；末端 wrist、tool_head、end_plate 或 flange | wrist_style, wrist_length, end_effector_style | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L149-L157`; S2 / `data/records/rec_cantilever_articulated_arm_033009cff45d49b98764c004628c5a04/revisions/rev_000001/model.py:L243-L252`; S3 / `data/records/rec_cantilever_articulated_arm_482bb4bc30fc4ab9a905d6a030180276/revisions/rev_000001/model.py:L275-L293` |
| yaw_housing | optional；pedestal 上方旋转 turret/yaw housing | yaw_enabled, yaw_housing_style | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L116-L125` |
| braces / ribs / hinge cheeks | optional visual；link 上的 stiffeners、fork cheeks、gussets | detail_level, brace_style | S2 / `data/records/rec_cantilever_articulated_arm_033009cff45d49b98764c004628c5a04/revisions/rev_000001/model.py:L197-L247` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| base_yaw | revolute | `(0, 0, 1)` | pedestal/support 顶部中心 | `[-1.57, 1.57]` 建议 | optional；底座水平旋回 | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L160-L173` |
| shoulder_joint | revolute | `(0, -1, 0)` for vertical pitch chain；或 `(0, 0, 1)` for horizontal swing layout | base_support 到 shoulder_link 的铰链中心 | `[-1.10, 1.35]` 建议 | required；第一段悬臂摆动 | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L174-L187`; S2 / `data/records/rec_cantilever_articulated_arm_033009cff45d49b98764c004628c5a04/revisions/rev_000001/model.py:L254-L262`; S4 / `data/records/rec_cantilever_articulated_arm_0001/revisions/rev_000001/model.py:L157-L170` |
| elbow_joint | revolute | 与 shoulder pitch/swing axis 平行 | shoulder_link 末端 | `[-1.80, 1.35]` 建议 | required；第二段相对第一段折叠 | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L188-L201`; S2 / `data/records/rec_cantilever_articulated_arm_033009cff45d49b98764c004628c5a04/revisions/rev_000001/model.py:L263-L271`; S4 / `data/records/rec_cantilever_articulated_arm_0001/revisions/rev_000001/model.py:L171-L184` |
| wrist_joint | revolute | `(0, -1, 0)` pitch wrist or `(0, 0, 1)` yaw wrist | elbow_link 末端 | `[-1.35, 1.35]` 建议 | required；末端 plate/tool 朝向调节 | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L202-L215`; S2 / `data/records/rec_cantilever_articulated_arm_033009cff45d49b98764c004628c5a04/revisions/rev_000001/model.py:L272-L280`; S3 / `data/records/rec_cantilever_articulated_arm_482bb4bc30fc4ab9a905d6a030180276/revisions/rev_000001/model.py:L323-L336` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| arm_layout | enum | `vertical_pitch_chain` / `horizontal_swing_chain` / `pedestal_yaw_pitch_chain` / `underslung_pitch_chain` | `vertical_pitch_chain` | 决定 joint axes 和 support geometry | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L160-L215`; S3 / `data/records/rec_cantilever_articulated_arm_482bb4bc30fc4ab9a905d6a030180276/revisions/rev_000001/model.py:L295-L336`; S4 / `data/records/rec_cantilever_articulated_arm_0001/revisions/rev_000001/model.py:L157-L200` |
| base_mount_style | enum | `pedestal` / `wall_block` / `support_frame` / `column_turret` | `pedestal` | 派生 base_support visuals 和 yaw_enabled | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L106-L125`; S3 / `data/records/rec_cantilever_articulated_arm_482bb4bc30fc4ab9a905d6a030180276/revisions/rev_000001/model.py:L221-L231` |
| link_profile | enum | `box_beam` / `forked_link` / `underslung_shell` / `tapered_beam` | `forked_link` | 应用于 shoulder/elbow link shape | S2 / `data/records/rec_cantilever_articulated_arm_033009cff45d49b98764c004628c5a04/revisions/rev_000001/model.py:L213-L241`; S3 / `data/records/rec_cantilever_articulated_arm_482bb4bc30fc4ab9a905d6a030180276/revisions/rev_000001/model.py:L233-L273` |
| link_count | int | `2` / `3` | `2` | 2 表示 shoulder+elbow+wrist；3 可增加 intermediate link（inferred from repeated multi-link samples） | S2 / `data/records/rec_cantilever_articulated_arm_033009cff45d49b98764c004628c5a04/revisions/rev_000001/model.py:L213-L280` |
| shoulder_link_length | float | `0.28-0.55` | `0.40` | elbow origin = shoulder_link_length | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L127-L147` |
| elbow_link_length | float | `0.22-0.46` | `0.32` | wrist origin = elbow_link_length | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L138-L157`; S3 / `data/records/rec_cantilever_articulated_arm_482bb4bc30fc4ab9a905d6a030180276/revisions/rev_000001/model.py:L254-L293` |
| wrist_style | enum | `end_plate` / `tool_head` / `flange` / `wrist_block` | `end_plate` | 决定末端 geometry 和 wrist joint range | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L149-L157`; S2 / `data/records/rec_cantilever_articulated_arm_033009cff45d49b98764c004628c5a04/revisions/rev_000001/model.py:L243-L252` |
| yaw_enabled | bool | `true` / `false` | `false` | `base_mount_style = column_turret` 时 true | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L160-L173` |
| material_style | enum | `industrial_orange` / `brushed_aluminum` / `graphite` / `blue_tool` | `brushed_aluminum` | palette only | S1 / `data/records/rec_cantilever_articulated_arm_0002/revisions/rev_000001/model.py:L101-L104`; S3 / `data/records/rec_cantilever_articulated_arm_482bb4bc30fc4ab9a905d6a030180276/revisions/rev_000001/model.py:L217-L219` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| base_support | pedestal / wall block / support frame / column turret | no | yes | base_mount_style | 安装方式是拓扑和姿态差异 |
| arm chain layout | vertical pitch / horizontal swing / yaw+pitch / underslung | no | yes | arm_layout | 关节轴不同，不能用尺寸连续值替代 |
| links | box beam / forked link / underslung shell / tapered beam | no | yes | link_profile | link 截面、fork 和壳体轮廓不同 |
| wrist/end effector | flat plate / tool head / flange / block | no | yes | wrist_style | 末端识别件存在定性差异 |
| link lengths | none beyond scale variation | yes | no | shoulder_link_length, elbow_link_length | 长短变化可用连续参数表达 |
| hinge cheeks/ribs | ribs/forks/gussets/bolted cheeks | partly | yes | detail_level, brace_style | detail_level 控制装饰密度，核心 link_profile 控制结构形态 |

## 组合逻辑（Composition Logic）
1. 生成 base_support，并根据 `base_mount_style` 决定是否添加 yaw_housing。
2. 若 `yaw_enabled`，先连接 base_support -> yaw_housing，再从 yaw_housing 连接 shoulder_link。
3. 根据 `arm_layout` 选择所有 pitch/swing joint 轴向：vertical/underslung 使用 Y 轴 pitch；horizontal 使用 Z 轴 swing。
4. shoulder_link、elbow_link、wrist_or_end_effector 按串联链装配，child origin 放在 parent link 末端。
5. Fork cheeks、stiffeners、bolts、cover plates 作为对应 part 的 visual，除非它们本身需要活动。

## 已有模板写法参考
revolute_hinge / folding_link_chain / rotary_post

## 约束
- 至少有 shoulder、elbow、wrist 三个 revolute joints；base_yaw 可选。
- link origins 必须形成串联链，不能让 forearm 或 wrist 漂浮到 base 外。
- shoulder/elbow 轴在同一 layout 中应平行或按 yaw+pitch 逻辑正交。
- wrist/end effector 必须连接在最后一级 link 末端。
- link 的 bbox 和 joint origin 必须匹配，末端 joint 不应在 link 中心随意放置。
- `arm_layout` 为 horizontal 时，主要 swing axes 应为 Z；vertical/underslung 时主要 pitch axes 应为 Y。

## Validator
| 检查项 | 标准 |
|---|---|
| joint count | 至少 3 个 revolute joints |
| required parts | base_support、shoulder_link、elbow_link、wrist_or_end_effector 存在 |
| chain connectivity | base -> shoulder -> elbow -> wrist 串联，无跳接/漂浮 |
| axis consistency | arm_layout 与 joint axes 一致 |
| origin placement | elbow origin 接近 shoulder link 末端，wrist origin 接近 elbow link 末端 |
| yaw consistency | yaw_enabled 时有 Z 轴 base_yaw；false 时无额外 turret yaw |
| part diversity | arm_layout、base_mount_style、link_profile、wrist_style 参数存在 |
| identity | 必须像悬臂式多关节机械臂 |

## Reject cases
- 只有静态支架，没有多关节悬臂链。
- elbow 或 wrist 缺失，末端无法调节。
- link 漂浮或 joint origin 不在连接端。
- horizontal swing 和 vertical pitch 轴混用导致关节方向不可信。
- 末端工具/面板不在最后一级 link 末端。
- 用单根连续梁替代 shoulder/elbow link。
- 只通过颜色变化表达样本多样性。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核 |
