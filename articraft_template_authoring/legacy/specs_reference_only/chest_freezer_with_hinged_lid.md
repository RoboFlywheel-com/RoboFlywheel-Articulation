# Chest Freezer With Hinged Lid Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `chest_freezer_with_hinged_lid` |
| template path | `agent/templates/chest_freezer_with_hinged_lid.py` |
| test path | `tests/agent/test_chest_freezer_with_hinged_lid_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 35 |
| read_count | 35 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
顶开式卧式冷柜 / 冷藏箱必须有厚壁保温箱体、上开口内胆、顶盖或顶盖组，以及沿后边、中心脊或导轨打开的 lid motion；常见细节包括密封条、铰链桶、前把手、控制面板、通风格栅和脚轮 / 脚垫。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_chest_freezer_with_hinged_lid_0001` | `data/records/rec_chest_freezer_with_hinged_lid_0001/revisions/rev_000001/model.py:L46-L354` | single hinged freezer body, liner, top rim, control panel, gasketed lid and rear hinge |
| S2 | `rec_chest_freezer_with_hinged_lid_1afab3911c0946f4a7a9003854338645` | `data/records/rec_chest_freezer_with_hinged_lid_1afab3911c0946f4a7a9003854338645/revisions/rev_000001/model.py:L34-L258` | split center-hinged twin lids, center divider / spine, mirrored hinge axes |
| S3 | `rec_chest_freezer_with_hinged_lid_a41f1625ddf14beeb1ebb414a8356e8f` | `data/records/rec_chest_freezer_with_hinged_lid_a41f1625ddf14beeb1ebb414a8356e8f/revisions/rev_000001/model.py:L30-L267` | commercial display body, glass sliding lid, guide rails and prismatic motion |
| S4 | `rec_chest_freezer_with_hinged_lid_80e1dc9e38e548a8a3658f82b5c16d93` | `data/records/rec_chest_freezer_with_hinged_lid_80e1dc9e38e548a8a3658f82b5c16d93/revisions/rev_000001/model.py:L49-L312` | hollow cooler shell, exposed barrel hinges, hold-open stay rod, drain spigot lever |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `body` / `cabinet` | 必需；厚壁保温箱体，包含底盘、四壁、内胆和上开口 rim | `body_length`, `body_width`, `body_height`, `wall_thickness`, `body_style` | S1 / `model.py:L75-L272`; S2 / `model.py:L34-L167`; S3 / `model.py:L30-L173`; S4 / `model.py:L99-L183` |
| `lid_i` / `sliding_lid` | 必需；单盖、双盖或玻璃滑盖 | `lid_layout`, `lid_thickness`, `lid_material_style`, `lid_count` | S1 / `model.py:L274-L340`; S2 / `model.py:L174-L236`; S3 / `model.py:L208-L257`; S4 / `model.py:L184-L238` |
| `gasket` / `top_rim` | 必需 visual；盖与箱体之间的密封、rim、runner 或 guide rail | `gasket_style`, `rim_height`, `guide_rail_profile` | S1 / `model.py:L153-L181`; S1 / `model.py:L297-L300`; S2 / `model.py:L108-L144`; S3 / `model.py:L138-L173` |
| `hinge_hardware` | 条件必需；hinged layouts 的 body hinge barrel / lid hinge leaf | `hinge_count`, `hinge_style`, `hinge_axis_side` | S1 / `model.py:L257-L266`; S1 / `model.py:L302-L354`; S2 / `model.py:L168-L256`; S4 / `model.py:L135-L166`; S4 / `model.py:L200-L223` |
| `handle` | optional；前拉手、嵌入把手、侧把手或活动 carry handle | `handle_style` | S1 / `model.py:L311-L333`; S2 / `model.py:L146-L158` |
| `control_panel` / `vent` | optional；温控旋钮、显示面板、压缩机通风格栅 | `control_panel_style`, `vent_style` | S1 / `model.py:L184-L237`; S3 / `model.py:L116-L129` |
| `stay_rod` | optional；支撑开盖的连杆 | `stay_rod_enabled` | S4 / `model.py:L167-L183`; S4 / `model.py:L224-L268`; S4 / `model.py:L295-L303` |
| `drain_plug` / `spigot_lever` | optional；户外 / marine cooler 的排水嘴和拨杆 | `drain_style` | S4 / `model.py:L113-L133`; S4 / `model.py:L270-L312` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `lid_hinge` | revolute | `(1, 0, 0)` or equivalent rear-edge horizontal axis | rear top edge | `[0, 1.35]` | 单块顶盖向上打开 | S1 / `model.py:L341-L354`; S4 / `model.py:L286-L294` |
| `lid_i_hinge` | revolute | `(±1, 0, 0)` | center spine or mirrored hinge line | `[0, 1.75]` | 双顶盖围绕中心脊或相邻 hinge line 独立打开 | S2 / `model.py:L238-L256` |
| `sliding_lid_slide` | prismatic | `(1, 0, 0)` | top guide rail center | `[0, 0.98]` scaled by body length | 玻璃展示盖沿顶面导轨滑开 | S3 / `model.py:L258-L267` |
| `stay_rod_joint` | revolute | `(0, 1, 0)` | lid side pin | `[-0.35, 1.15]` | 保持开盖的支撑杆随 lid 摆动 | S4 / `model.py:L295-L303` |
| `spigot_lever_joint` | revolute | `(0, 1, 0)` | drain nozzle side | `[-0.85, 0.85]` | 排水拨杆转动 | S4 / `model.py:L304-L312` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `body_style` | enum | `residential_white` / `commercial_display` / `marine_cooler` / `laboratory` / `split_lid_cooler` | `residential_white` | 决定比例、配色、附件默认值 | S1 / `model.py:L46-L354`; S2 / `model.py:L34-L258`; S3 / `model.py:L30-L267`; S4 / `model.py:L49-L312` |
| `lid_layout` | enum | `single_hinged` / `split_hinged` / `sliding_glass` | `single_hinged` | 派生 `lid_count`、joint type 和 hinge / rail hardware | S1 / `model.py:L274-L354`; S2 / `model.py:L174-L256`; S3 / `model.py:L208-L267` |
| `body_length` | float | `0.9-2.4` | `1.28` | display / body-bag variants use upper range | S1 / `model.py:L58-L73`; S3 / `model.py:L35-L173` |
| `body_width` | float | `0.34-0.95` | `0.72` | split narrow cooler may be small; display freezer wider | S1 / `model.py:L58-L73`; S2 / `model.py:L27-L32`; S3 / `model.py:L35-L173` |
| `body_height` | float | `0.35-1.0` | `0.88` | liner height and lid hinge z derive from body height | S1 / `model.py:L58-L73`; S4 / `model.py:L49-L87` |
| `wall_thickness` | float | `0.025-0.075` | `0.055` | rim width and cavity opening derive from wall thickness | S1 / `model.py:L58-L68`; S4 / `model.py:L76-L87` |
| `hinge_count` | int | `0 / 2 / 3` | `2` | `0` only for sliding lid; hinge visuals distributed along hinge edge | S1 / `model.py:L257-L266`; S4 / `model.py:L135-L166` |
| `hinge_style` | enum | `barrel_pair` / `piano` / `center_spine` / `guide_rail` | `barrel_pair` | constrained by `lid_layout` | S1 / `model.py:L257-L354`; S2 / `model.py:L168-L256`; S3 / `model.py:L162-L267` |
| `handle_style` | enum | `front_bar` / `recessed` / `molded_end_grip` / `carry_handle` / `none` | `front_bar` | display sliding uses pull grip; split cooler may use end grips | S1 / `model.py:L311-L333`; S2 / `model.py:L146-L158`; S3 / `model.py:L251-L256` |
| `gasket_style` | enum | `thin_black_strip` / `compressed_ring` / `glass_runner` | `thin_black_strip` | lid material and rim choose gasket form | S1 / `model.py:L297-L300`; S2 / `model.py:L133-L144`; S3 / `model.py:L239-L250`; S4 / `model.py:L195-L199` |
| `accessory_set` | enum | `none` / `control_vent` / `stay_and_drain` / `display_products` | `control_vent` | selects optional visuals / joints | S1 / `model.py:L184-L237`; S3 / `model.py:L95-L129`; S4 / `model.py:L113-L312` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| body / cabinet | residential box / long split cooler / wide commercial display / marine hollow cooler | no | yes | `body_style` | 不同使用场景有不同顶 rim、内胆、外壳细节和比例 |
| lid | single solid hinged / split hinged / sliding glass framed panel | no | yes | `lid_layout`, `lid_material_style` | revolute 与 prismatic motion、盖数量、材质拓扑不同 |
| hinge / rail | barrel pair / center spine / piano-like hinge / guide rail | no | yes | `hinge_style` | 连接件形态与 joint 类型直接相关 |
| handle | front bar / recessed / molded end grip / sliding pull / carry handle | no | yes | `handle_style` | 操作件位置和形态不同，不能只用尺寸表达 |
| gasket / rim | black strip / compressed ring / raised blue rim / glass runner | no | yes | `gasket_style` | sealing / runner 语义不同，影响 lid seating |
| controls / vents / drain | thermostat panel / grille / spigot lever / display products | no | yes | `accessory_set` | 附件集合与 body style 强相关 |
| feet / casters | short feet / rubber pads / none | yes | no | `foot_count`, `foot_height` | 主要是数量和高度变化，可用连续 / count 表达 |

## 组合逻辑（Composition Logic）
1. 先生成 `body` 外包络，按 `wall_thickness` 派生 hollow liner、rim、cavity opening。
2. 根据 `lid_layout` 选择 lid part tree：单 lid、双 lid 或 sliding glass lid。
3. `single_hinged`：hinge origin 放在后上边，lid local geometry 从 hinge 轴向前覆盖开口；gasket 挂在 lid 下表面。
4. `split_hinged`：添加 center divider / spine，两个 lid 使用镜像 hinge axis，分别覆盖左右 / 前后半开口。
5. `sliding_glass`：body 顶面生成前后 guide rails 和 fixed glass leaf，sliding_lid 作为独立 part 沿 X 滑动。
6. 附件根据 `accessory_set` 加入；control / vent / fixed drain body 为 body visual，stay rod 和 spigot lever 才创建独立活动 part。
7. 非活动螺丝、脚垫、产品包、品牌条、内胆面板都作为所在 part 的 visual。

## 已有模板写法参考
revolute_hinge / prismatic_slide / gasket_strip / handle_grip / latch_lock

## 约束
- body 必须表现为顶开 hollow chest，不得变成立式冰箱或普通柜子。
- hinged lid 的 hinge origin 必须在顶盖后边、中心脊或有效 hinge edge。
- sliding lid 只能用于 display / drink cooler 变体，并必须有 guide rails 和 overlap。
- lid closed pose 必须覆盖开口且 gasket / rim 接触。
- 内胆 floor 和 liner 必须位于外壳内部。
- optional stay rod / spigot lever 若出现，必须连接到 body / lid，不得漂浮。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | body 有 hollow liner/top rim，lid 覆盖顶面开口 |
| lid joint | `single_hinged` / `split_hinged` 使用 revolute；`sliding_glass` 使用 prismatic |
| axis check | hinged axis 沿 lid hinge edge；sliding axis 沿 top guide rail |
| lid count | `single_hinged=1`, `split_hinged=2`, `sliding_glass=1 moving panel plus optional fixed leaf` |
| seal seating | closed lid 与 rim/gasket z gap 在小容差内 |
| guide rail retention | sliding lid 全开时 runner 仍与 rail overlap |
| part diversity | `body_style`, `lid_layout`, `hinge_style`, `handle_style`, `gasket_style` 均存在 |
| no floating | lid、hinge hardware、optional stay rod / drain lever 均连接到主树 |

## Reject cases
- 没有顶盖或顶盖不是可动件。
- 顶盖 hinge 在箱体中心随机位置，不能表现后边 / 中心脊开盖。
- 箱体没有内胆或上开口，像普通封闭箱子。
- sliding glass lid 没有导轨或滑出箱体。
- gasket / rim 与 lid 严重分离。
- stay rod、handle、spigot 漂浮。
- 只做小盒子加颜色，缺少冷柜识别细节如厚壁、rim、vent、control 或 seal。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核；当前仅为 SPEC_ONLY_DRAFT，未进入模板实现阶段。 |
