# Barrier Gate Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `barrier_gate` |
| template path | `agent/templates/barrier_gate.py` |
| test path | `tests/agent/test_barrier_gate_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 55 |
| read_count | 55 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
用于阻断车辆或行人的通道控制装置，至少包含固定支撑/导向结构和一个可运动的 barrier member。运动形式可为水平轴抬杆、折叠杆、滑移门扇、竖直升降柱/梁、翻起楔板或竖直轴摆门，但都必须表达“关闭时拦截通道、打开时让出通道”的关节关系。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | rec_barrier_gate_0002 | `data/records/rec_barrier_gate_0002/revisions/rev_000001/model.py:L32-L163` | parking/toll boom gate: cabinet/post, hinge fork, counterweighted boom, horizontal-axis lift joint |
| S2 | rec_barrier_gate_557f4d79951148ad88a0c526a09987a0 | `data/records/rec_barrier_gate_557f4d79951148ad88a0c526a09987a0/revisions/rev_000001/model.py:L27-L220` | folding boom: housing, inner/outer boom sections, main hinge and midpoint hinge |
| S3 | rec_barrier_gate_b31475654e4b41c3b48a69158cbd2fb6 | `data/records/rec_barrier_gate_b31475654e4b41c3b48a69158cbd2fb6/revisions/rev_000001/model.py:L185-L296` | sliding bi-parting gate: rail frame, center latch post, left/right panels, opposed prismatic slides |
| S4 | rec_barrier_gate_bea52ddfb098470fb53099d456d31da0 | `data/records/rec_barrier_gate_bea52ddfb098470fb53099d456d31da0/revisions/rev_000001/model.py:L99-L210` | rising bollard: ground sleeve, telescoping post, guide pads, optional hinged skirt |
| S5 | rec_barrier_gate_aac86b50737842bd8ac956d2e5251dc3 | `data/records/rec_barrier_gate_aac86b50737842bd8ac956d2e5251dc3/revisions/rev_000001/model.py:L31-L244` | road wedge: grade cassette, pit frame, hinge cheeks, wedge plate and rear-edge hinge |
| S6 | rec_barrier_gate_b870b87019dd4d72b99a9ed24e459e7a | `data/records/rec_barrier_gate_b870b87019dd4d72b99a9ed24e459e7a/revisions/rev_000001/model.py:L81-L270` | swing/bifold gate: post, framed leaf sections, vertical hinge axis and inter-leaf fold joint |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| fixed_support | 静态承载与导向结构；按 `barrier_layout` 派生为 post/cabinet、track_frame、ground_socket、road_cassette 或 hinge_post | support_style: enum, support_width/depth/height: float, guide_clearance: float | S1 / `data/records/rec_barrier_gate_0002/revisions/rev_000001/model.py:L32-L99`; S3 / `data/records/rec_barrier_gate_b31475654e4b41c3b48a69158cbd2fb6/revisions/rev_000001/model.py:L185-L250`; S4 / `data/records/rec_barrier_gate_bea52ddfb098470fb53099d456d31da0/revisions/rev_000001/model.py:L99-L135`; S5 / `data/records/rec_barrier_gate_aac86b50737842bd8ac956d2e5251dc3/revisions/rev_000001/model.py:L31-L171`; S6 / `data/records/rec_barrier_gate_b870b87019dd4d72b99a9ed24e459e7a/revisions/rev_000001/model.py:L81-L119` |
| boom_arm | 单段抬杆样式的可动拦截杆，含 pivot lug、尾管、配重、反光条和端帽 | boom_length: float, boom_section: enum, counterweight_style: enum, stripe_pattern: enum | S1 / `data/records/rec_barrier_gate_0002/revisions/rev_000001/model.py:L100-L148` |
| inner_boom / outer_boom | 双段折叠抬杆；outer_boom 在中点铰链处相对 inner_boom 折回 | boom_length: float, fold_ratio: float, fold_direction: enum, stripe_pattern: enum | S2 / `data/records/rec_barrier_gate_557f4d79951148ad88a0c526a09987a0/revisions/rev_000001/model.py:L107-L196` |
| sliding_panel_left / sliding_panel_right | 轨道门扇；可单扇或双扇对开，面板框架/网格/导轮作为 panel visual | panel_count: int, panel_width: float, panel_style: enum, track_style: enum | S3 / `data/records/rec_barrier_gate_b31475654e4b41c3b48a69158cbd2fb6/revisions/rev_000001/model.py:L252-L266` |
| bollard_post | 竖直升降柱体，沿固定套筒上下滑动；反光带和导向环为 visual | bollard_profile: enum, bollard_height: float, exposed_height: float | S4 / `data/records/rec_barrier_gate_bea52ddfb098470fb53099d456d31da0/revisions/rev_000001/model.py:L137-L167` |
| skirt_or_cap | bollard 变体的可选 hinged skirt/cap，用于覆盖套筒口 | cap_style: enum, cap_hinge_angle: float | S4 / `data/records/rec_barrier_gate_bea52ddfb098470fb53099d456d31da0/revisions/rev_000001/model.py:L168-L210` |
| wedge_plate | 翻起式路障板，带 deck plate、hinge tube、加强肋和警示带 | wedge_width: float, wedge_depth: float, rib_count: int, wedge_face_style: enum | S5 / `data/records/rec_barrier_gate_aac86b50737842bd8ac956d2e5251dc3/revisions/rev_000001/model.py:L172-L244` |
| swing_leaf_outer / swing_leaf_inner | 竖直轴摆门或 bifold 门扇；门扇框架由 stiles/rails/diagonal brace 组成 | leaf_count: int, leaf_width: float, infill_style: enum, bifold_enabled: bool | S6 / `data/records/rec_barrier_gate_b870b87019dd4d72b99a9ed24e459e7a/revisions/rev_000001/model.py:L120-L249` |
| catch_post | 单段 boom gate 的可选远端承托柱；样本中出现但不是所有布局必需 | catch_post_enabled: bool, catch_height: float | inferred from S1/S6 layout, no required source part |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| boom_hinge | revolute | `(0, -1, 0)` 或按 arm 横向轴换算的水平轴 | post/cabinet 顶部 hinge fork/pivot pin | `[0, 0.95]` 到 `[0, pi/2]` | 单段 boom 从水平关闭位向上抬起 | S1 / `data/records/rec_barrier_gate_0002/revisions/rev_000001/model.py:L150-L163` |
| folding_boom_main_hinge | revolute | `(0, -1, 0)` | housing 侧面 pivot fork | `[0, 1.35]` | 折叠 boom 的内段整体抬起 | S2 / `data/records/rec_barrier_gate_557f4d79951148ad88a0c526a09987a0/revisions/rev_000001/model.py:L197-L205` |
| folding_boom_mid_hinge | revolute | `(0, 1, 0)` 或 `(0, -1, 0)` | inner_boom 末端 midpoint knuckle | `[0, 2.10]` 或 `[-1.15, 0]` | outer_boom 在中点折回，避让净空 | S2 / `data/records/rec_barrier_gate_557f4d79951148ad88a0c526a09987a0/revisions/rev_000001/model.py:L206-L220` |
| sliding_panel_i_joint | prismatic | `(-1, 0, 0)` for left, `(1, 0, 0)` for right | panel closed center on ground rail | `[0, panel_travel]` | 双扇沿轨道从中心向两侧滑开 | S3 / `data/records/rec_barrier_gate_b31475654e4b41c3b48a69158cbd2fb6/revisions/rev_000001/model.py:L268-L296` |
| bollard_lift | prismatic | `(0, 0, 1)` | housing sleeve axis | `[lowered_offset, 0]` 或 `[0, post_travel]` | bollard 在地面套筒中竖直升降 | S4 / `data/records/rec_barrier_gate_bea52ddfb098470fb53099d456d31da0/revisions/rev_000001/model.py:L181-L194` |
| skirt_hinge | revolute | `(1, 0, 0)` | housing rim/skirt hinge boss | `[0, 1.35]` | bollard 套筒口保护裙板翻开 | S4 / `data/records/rec_barrier_gate_bea52ddfb098470fb53099d456d31da0/revisions/rev_000001/model.py:L195-L210` |
| wedge_hinge | revolute | `(0, -1, 0)` | rear edge hinge tube / pit cassette rear bearing | `[0, 1.05]` | wedge plate 从路面齐平状态翻起 | S5 / `data/records/rec_barrier_gate_aac86b50737842bd8ac956d2e5251dc3/revisions/rev_000001/model.py:L234-L244` |
| swing_leaf_hinge | revolute | `(0, 0, 1)` or `(0, 0, -1)` | post pintle axis at leaf stile | `[0, 1.65]` | swing gate leaf 绕立柱打开 | S6 / `data/records/rec_barrier_gate_b870b87019dd4d72b99a9ed24e459e7a/revisions/rev_000001/model.py:L250-L258` |
| bifold_inner_hinge | revolute | `(0, 0, 1)` or `(0, 0, -1)` | outer leaf trailing stile / center knuckle | `[0, 3.05]` | bifold 内扇相对外扇折叠 | S6 / `data/records/rec_barrier_gate_b870b87019dd4d72b99a9ed24e459e7a/revisions/rev_000001/model.py:L259-L270` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| barrier_layout | enum | `single_boom` / `folding_boom` / `sliding_panel` / `rising_bollard` / `rising_wedge` / `swing_leaf` / `bifold_leaf` | `single_boom` | 决定主 part 集和 joint 集 | S1-S6 |
| support_style | enum | `control_cabinet` / `flat_housing` / `rail_frame` / `ground_socket` / `road_cassette` / `pintle_post` | `control_cabinet` | 由 `barrier_layout` 限定合法集合 | S1-S6 |
| boom_section | enum | `rectangular_tube` / `tapered_box` / `trussed` | `rectangular_tube` | 仅 boom 布局有效 | S1 / `data/records/rec_barrier_gate_0002/revisions/rev_000001/model.py:L100-L148`; S2 / `data/records/rec_barrier_gate_557f4d79951148ad88a0c526a09987a0/revisions/rev_000001/model.py:L107-L196` |
| boom_length | float | `2.4-5.2` | `3.8` | support 高度与 hinge origin 缩放 | S1 / `data/records/rec_barrier_gate_0002/revisions/rev_000001/model.py:L100-L148` |
| counterweight_style | enum | `none` / `tail_block` / `counter_arm` / `fin` | `tail_block` | boom 布局有效；folding_boom 可弱化 | S1 / `data/records/rec_barrier_gate_0002/revisions/rev_000001/model.py:L113-L136` |
| stripe_pattern | enum | `none` / `long_red_strip` / `segmented_red_bands` / `yellow_hazard_bands` | `segmented_red_bands` | 不改变关节，只改变 visual | S1 / `data/records/rec_barrier_gate_0002/revisions/rev_000001/model.py:L137-L148`; S2 / `data/records/rec_barrier_gate_557f4d79951148ad88a0c526a09987a0/revisions/rev_000001/model.py:L150-L196`; S5 / `data/records/rec_barrier_gate_aac86b50737842bd8ac956d2e5251dc3/revisions/rev_000001/model.py:L225-L233` |
| fold_ratio | float | `0.40-0.65` | `0.52` | outer length = total boom length * fold_ratio | S2 / `data/records/rec_barrier_gate_557f4d79951148ad88a0c526a09987a0/revisions/rev_000001/model.py:L107-L220` |
| panel_count | int | `1 / 2` | `2` | `sliding_panel` 中 joint 数等于 panel_count | S3 / `data/records/rec_barrier_gate_b31475654e4b41c3b48a69158cbd2fb6/revisions/rev_000001/model.py:L252-L296` |
| panel_style | enum | `mesh_frame` / `tube_frame` / `solid_panel` | `mesh_frame` | 滑移/摆门/bifold 布局共享 | S3 / `data/records/rec_barrier_gate_b31475654e4b41c3b48a69158cbd2fb6/revisions/rev_000001/model.py:L252-L266`; S6 / `data/records/rec_barrier_gate_b870b87019dd4d72b99a9ed24e459e7a/revisions/rev_000001/model.py:L120-L249` |
| bollard_profile | enum | `round_post` / `square_post` | `round_post` | `rising_bollard` 布局有效 | S4 / `data/records/rec_barrier_gate_bea52ddfb098470fb53099d456d31da0/revisions/rev_000001/model.py:L137-L167` |
| wedge_face_style | enum | `flat_plate` / `ribbed_plate` / `reflector_front` | `ribbed_plate` | `rising_wedge` 布局有效 | S5 / `data/records/rec_barrier_gate_aac86b50737842bd8ac956d2e5251dc3/revisions/rev_000001/model.py:L172-L233` |
| infill_style | enum | `open_tube` / `mesh` / `diagonal_brace` / `ornamental` | `diagonal_brace` | swing/bifold/sliding panels 使用 | S6 / `data/records/rec_barrier_gate_b870b87019dd4d72b99a9ed24e459e7a/revisions/rev_000001/model.py:L120-L249` |
| open_angle | float | `0.65-1.65` | `1.35` | revolute boom/swing upper limit | S1 / `data/records/rec_barrier_gate_0002/revisions/rev_000001/model.py:L150-L163`; S6 / `data/records/rec_barrier_gate_b870b87019dd4d72b99a9ed24e459e7a/revisions/rev_000001/model.py:L250-L270` |
| slide_travel | float | `0.8-2.4` | `1.5` | sliding panel range | S3 / `data/records/rec_barrier_gate_b31475654e4b41c3b48a69158cbd2fb6/revisions/rev_000001/model.py:L268-L296` |
| lift_travel | float | `0.45-1.15` | `0.72` | bollard/vertical blocker prismatic range | S4 / `data/records/rec_barrier_gate_bea52ddfb098470fb53099d456d31da0/revisions/rev_000001/model.py:L181-L194` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| fixed_support | cabinet/post、flat housing、ground socket、road cassette、rail frame、pintle post | no | yes | support_style | 支撑拓扑差异决定 barrier_layout，不能用尺寸连续化 |
| movable_barrier | single boom、folding boom、sliding panel、rising bollard、rising wedge、swing/bifold leaf | no | yes | barrier_layout | 这是 55 个样本中最大的定性差异，必须显式枚举 |
| boom_arm | rectangular tube / segmented warning bands / counterweighted tail | no | yes | boom_section, counterweight_style, stripe_pattern | 杆件截面、配重和警示图案影响类别识别 |
| sliding_panel | mesh frame / tube frame / solid panel | no | yes | panel_style, infill_style | 面板拓扑和填充不是长宽能表达的差异 |
| bollard_post | round / square; with or without hinged cap/skirt | no | yes | bollard_profile, cap_style | 圆柱、方柱和盖板结构需要离散分支 |
| wedge_plate | flush ribbed steel plate / reflector face / guide cassette | no | yes | wedge_face_style | 楔板正面、肋和地坑框架是 road blocker 身份核心 |
| hinge/guide hardware | fork yoke、midpoint knuckle、track guide、pit hinge cheeks、pintle barrels | no | yes | hinge_style, track_style | 连接硬件随布局变化，连续尺寸不足 |
| catch_post | none / far-end support post | no | yes | catch_post_enabled | 仅部分 single_boom 样本出现，作为 optional |

## 组合逻辑（Composition Logic）
1. 先根据 `barrier_layout` 选择 spine：boom 类使用 post/cabinet 坐标系，sliding 类使用轨道中心线，bollard/wedge 使用地面套筒/坑框架，swing/bifold 使用立柱竖直轴。
2. 生成 `fixed_support`，并派生 hinge/guide origin；所有静态面板、灯、警示贴和导向块优先作为 support visual。
3. 生成可动 barrier member：boom、panel、bollard、wedge 或 leaf；同一布局只创建对应的活动 part，未选布局不创建空 part。
4. 按布局创建 joint；folding/bifold 布局需要串联第二级 revolute，sliding 双扇需要相反方向的 prismatic。
5. 装饰件和非运动硬件挂到最近父 part；只有真实可动件才创建独立 part。

## 已有模板写法参考
revolute_hinge / prismatic_slide / telescoping_tube / guide_shoe / folding_link_chain / handle_grip

## 约束
- `barrier_layout` 必须与 parts/joints 一致，不允许生成未使用布局的空活动件。
- boom hinge axis 必须水平，boom 关闭时横跨通道，打开时向上或折回。
- sliding panel 的 prismatic axis 必须沿轨道，双扇应从中心向相反方向打开。
- bollard/wedge 的 ground frame 必须位于地面，活动件必须保持导向嵌套或后缘铰接。
- swing/bifold 叶片 hinge axis 必须竖直，门扇关闭时应形成通道横向拦截面。
- 所有导向、铰链、配重、警示条必须附着到对应 part，不得漂浮。

## Validator
| 检查项 | 标准 |
|---|---|
| layout consistency | `barrier_layout` 对应的 required part 和 joint 全部存在，其他布局活动件不存在 |
| joint count | single_boom=1 revolute；folding_boom=2 revolute；sliding_panel=panel_count prismatic；rising_bollard=1 prismatic plus optional cap hinge；rising_wedge=1 revolute；swing_leaf/bifold_leaf=1 or 2+ revolute |
| axis check | boom/wedge 水平轴；sliding 沿轨道；bollard 竖直；swing/bifold 竖直轴 |
| range check | revolute upper > 0.6 rad；sliding/lift travel > 0；folding second hinge has meaningful fold travel |
| guide/nesting | bollard remains inside socket; sliding panels remain on rail; wedge hinge remains at rear cassette |
| no floating | hinge forks, guide pads, panels, counterweights, caps and warning strips are attached |
| part diversity | `barrier_layout`, `support_style`, and layout-specific `*_style` parameters exist |
| identity | closed pose visibly blocks a lane/path; open pose visibly clears it |

## Reject cases
- 只有静态栏杆，没有任何可动 barrier joint。
- boom hinge 轴竖直或位置在杆中间，导致像普通门扇。
- sliding panel 没有轨道/导向，或滑动方向与轨道垂直。
- bollard 升降时完全脱离套筒。
- wedge 板不在路面坑框中，或后缘 hinge 漂浮。
- bifold/swing 门扇 hinge axis 不竖直。
- 使用颜色变化冒充不同 barrier layout。
- 生成多种布局叠在一起，导致类别身份混乱。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
