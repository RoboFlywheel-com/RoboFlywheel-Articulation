# Coaxial Rotary Stack Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `coaxial_rotary_stack` |
| template path | `agent/templates/coaxial_rotary_stack.py` |
| test path | `tests/agent/test_coaxial_rotary_stack_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 45 |
| read_count | 45 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
同轴旋转堆栈是围绕同一竖直中心轴布置的多层机械转台 / 环形台阶；至少包含固定 base / shaft 和两个以上独立旋转 stage，每个 stage 的旋转轴同向、同心，并通过轴承座、隔圈、collar 或 thrust washer 明确支撑。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_coaxial_rotary_stack_0ac53fe2cb354ac397530039e58e7392` | `data/records/rec_coaxial_rotary_stack_0ac53fe2cb354ac397530039e58e7392/revisions/rev_000001/model.py:L57-L330` | nested turntable base, spindle, lower/middle/top stages, collars, pointers and serial revolute joints |
| S2 | `rec_coaxial_rotary_stack_23cfdeb0b15547488359eaa005184dfb` | `data/records/rec_coaxial_rotary_stack_23cfdeb0b15547488359eaa005184dfb/revisions/rev_000001/model.py:L49-L260` | underslung top support, suspended shaft/collars and multiple stages sharing one vertical axis |
| S3 | `rec_coaxial_rotary_stack_65e7956eb70e464a86151669776c0fc8` | `data/records/rec_coaxial_rotary_stack_65e7956eb70e464a86151669776c0fc8/revisions/rev_000001/model.py:L63-L247` | drum-style indexing head with stepped annular bodies, clamp ears, screws and independent shaft-mounted stages |
| S4 | `rec_coaxial_rotary_stack_2c6761e45ae645e2896765558c88beb3` | `data/records/rec_coaxial_rotary_stack_2c6761e45ae645e2896765558c88beb3/revisions/rev_000001/model.py:L55-L194` | variable multi-stage stepped stack loop with common shaft, support washers and per-stage revolute joints |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `base` / `shaft` / `frame` | 必需；固定根部，包含 plinth、center spindle / common shaft、support collars / washers | `support_layout`, `base_radius`, `shaft_radius`, `shaft_height`, `support_style` | S1 / `model.py:L120-L191`; S2 / `model.py:L153-L190`; S3 / `model.py:L119-L143`; S4 / `model.py:L68-L132` |
| `stage_i` | 必需；2-4 个同轴旋转 stage，按半径和高度递减或悬挂排列 | `stage_count`, `stage_radius_profile`, `stage_height_profile`, `stage_body_style` | S1 / `model.py:L193-L290`; S2 / `model.py:L191-L231`; S3 / `model.py:L145-L218`; S4 / `model.py:L134-L183` |
| `bearing_land_i` / `collar_i` / `support_washer_i` | 必需 visual；每层旋转件的轴承支撑或分隔件 | `bearing_style`, `stage_gap`, `collar_radius` | S1 / `model.py:L139-L174`; S2 / `model.py:L82-L97`; S3 / `model.py:L151-L206`; S4 / `model.py:L94-L117` |
| `index_marker_i` / `pointer_i` / `drive_lug_i` | optional；表现可读刻度、零位指针、驱动凸耳 | `index_marker_style`, `marker_count` | S1 / `model.py:L211-L222`; S1 / `model.py:L247-L285`; S3 / `model.py:L156-L190`; S4 / `model.py:L165-L179` |
| `clamp_ears` / `fasteners` | optional；drum indexing head 的夹紧耳、螺钉、安装孔 | `fastener_style`, `clamp_enabled` | S3 / `model.py:L78-L107`; S3 / `model.py:L156-L190`; S3 / `model.py:L208-L217` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `stage_i_rotate` | revolute / continuous | `(0, 0, 1)` | common shaft center at stage support z | `[-pi, pi]` or `[0, tau]` | 第 i 层 stage 绕共同竖直轴独立旋转 | S1 / `model.py:L292-L330`; S2 / `model.py:L233-L260`; S3 / `model.py:L219-L247`; S4 / `model.py:L184-L192` |
| `base_to_spine` | fixed | n/a | root base center | n/a | 当 support_layout 需要单独 spine / shaft part 时固定连接 | S1 / `model.py:L120-L191`; S4 / `model.py:L68-L132` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `stage_count` | int | `2-4` | `3` | 派生 stage parts、joint 数、washer / collar 数 | S4 / `model.py:L134-L192`; S1 / `model.py:L193-L330` |
| `support_layout` | enum | `upright_spindle` / `underslung` / `saddle_body` / `tower_post` / `drum_indexer` | `upright_spindle` | 决定 root frame、stage z order 和 support visuals | S1 / `model.py:L120-L191`; S2 / `model.py:L153-L260`; S3 / `model.py:L119-L247` |
| `stage_body_style` | enum | `solid_disk` / `annular_ring` / `spoked_ring` / `stepped_drum` / `fixture_cup` | `annular_ring` | 决定 stage mesh / visuals | S1 / `model.py:L75-L92`; S1 / `model.py:L193-L290`; S2 / `model.py:L100-L141`; S3 / `model.py:L63-L107` |
| `stage_radius_profile` | enum | `descending` / `nested_equal_outer` / `underslung_descending` | `descending` | 约束 `stage_i.radius` 单调关系 | S1 / `model.py:L36-L50`; S2 / `model.py:L191-L231`; S4 / `model.py:L134-L140` |
| `base_radius` | float | `0.22-0.50` | `0.36` | stage 0 radius <= base radius unless underslung | S3 / `model.py:L63-L75`; S4 / `model.py:L68-L80` |
| `shaft_radius` | float | `0.02-0.07` | `0.04` | bore radius and collar inner radius derive from shaft radius | S1 / `model.py:L30-L50`; S4 / `model.py:L81-L117` |
| `stage_gap` | float | `0.006-0.055` | `0.018` | z offsets between stage bearing faces | S1 / `model.py:L52-L54`; S2 / `model.py:L31-L46`; S4 / `model.py:L94-L117` |
| `rotation_range_mode` | enum | `limited` / `continuous` / `full_turn_revolute` | `limited` | selects MotionLimits style | S1 / `model.py:L292-L330`; S3 / `model.py:L219-L247` |
| `index_marker_style` | enum | `none` / `pointer_tabs` / `tick_marks` / `drive_lugs` / `bolt_circle` | `pointer_tabs` | optional visual markers on stages / base | S1 / `model.py:L211-L222`; S3 / `model.py:L156-L190`; S4 / `model.py:L118-L126`; S4 / `model.py:L165-L179` |
| `bearing_style` | enum | `collar_stack` / `thrust_washer` / `bearing_land` / `hanger_collar` | `collar_stack` | support visuals at stage z positions | S1 / `model.py:L139-L174`; S2 / `model.py:L82-L97`; S3 / `model.py:L151-L206`; S4 / `model.py:L94-L117` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| support base / shaft | upright plinth with spindle / underslung top beam / drum mount plate / saddle body | no | yes | `support_layout` | 支撑拓扑和 z 方向关系不同 |
| rotary stage body | disk / annular ring / spoked ring / stepped drum / fixture cup | no | yes | `stage_body_style` | stage 截面、开孔和轮廓差异无法用半径厚度表达 |
| stage count | two / three / four stages | yes | no | `stage_count` | 数量变化可用整数参数表达，不需要形态 enum |
| bearing support | collar / washer / bearing land / hanger collar | no | yes | `bearing_style` | 支撑件形态影响视觉和接触关系 |
| index features | pointer tabs / tick marks / drive lugs / bolt circles / none | no | yes | `index_marker_style` | 标记形式是定性差异 |
| radius / height proportions | broad lower stage to compact upper stage; thin wafer vs tall drum | yes | no | `stage_radius_profile`, continuous radii | 多数比例变化可通过连续半径、厚度和 gap 表达 |

## 组合逻辑（Composition Logic）
1. 生成固定 root：按 `support_layout` 建立 upright base、underslung frame 或 drum shaft。
2. 计算 common axis `(0,0,1)` 和 stage z sequence；所有 joint origin 的 xy 必须相同。
3. 根据 `stage_count` 循环创建 `stage_i`，按 `stage_radius_profile` 派生半径和高度。
4. 每个 stage 添加 `stage_i_rotate` joint；parent 可为 base/shaft 或前一 stage，但 world axis 必须同心竖直。
5. 在固定 root 或父 stage 上添加 bearing land、collar、washer，证明 stage 被支撑且有间隙。
6. 根据 `stage_body_style` 和 `index_marker_style` 添加 annular mesh、spokes、tabs、tick marks、screws；非活动细节作为 stage visual。

## 已有模板写法参考
rotary_post / continuous_rotor / radial_array

## 约束
- 所有旋转 joint 的 axis 必须是 `(0, 0, 1)`。
- 所有旋转 joint 的 origin xy 必须一致；z 可按 stage support 位置递增或递减。
- 至少 2 个独立旋转 stage；推荐 3 个。
- stage 之间必须有可见 bearing / washer / collar 或明确接触面，不得漂浮。
- 相邻 stage 在 z 方向必须有正间隙或明确接触的 thrust surface，不得互相穿透。
- `underslung` layout 中 stage z 顺序向下，仍共享同一轴。

## Validator
| 检查项 | 标准 |
|---|---|
| stage count | `2 <= len(stage_i) <= 4` |
| joint count | stage rotate joint 数等于 `stage_count` |
| axis check | 所有 stage rotate joints `axis=(0,0,1)` |
| coaxial origins | 所有 rotate joint origin 的 xy 距离 <= 0.001 |
| support contact | 每个 stage 与对应 bearing / washer / collar 接触或 z gap <= 0.006 |
| clearance | 相邻 stage 非预期几何穿透；有可见 z separation |
| part diversity | `support_layout`, `stage_body_style`, `bearing_style`, `index_marker_style` 存在 |
| identity | 从外形可识别为多层同轴机械转台，而不是普通堆叠圆柱 |

## Reject cases
- stage 旋转轴不同心或 axis 不竖直。
- 只有一个旋转层。
- 多个圆盘堆在一起但没有轴承、collar、washer 或支撑关系。
- stage 漂浮在轴外或相邻 stage 严重穿模。
- stage 被固定死，没有独立 joint。
- 用普通静态塔状物替代 rotary stack。
- 只用颜色区分 stage，缺少 radius、height、bearing 或 marker 结构差异。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核；当前仅为 SPEC_ONLY_DRAFT，未进入模板实现阶段。 |
