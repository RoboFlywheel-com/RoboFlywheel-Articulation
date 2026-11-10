# Ceiling Fan Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `ceiling_fan` |
| template path | `agent/templates/ceiling_fan.py` |
| test path | `tests/agent/test_ceiling_fan_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 40 |
| read_count | 40 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
吊扇至少包含天花安装件/吊杆或低矮安装座、中心电机/轮毂、径向叶片组件，并有绕电机轴连续旋转的 rotor joint。可选特征包括灯罩、可折叠叶片、双头横杆、反转拨杆和工业护罩，但核心是悬挂式风扇与叶片旋转。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | rec_ceiling_fan_0004 | `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L217-L463` | traditional/tropical mount、rotor housing、radial blades、bottom globe、continuous spin |
| S2 | rec_ceiling_fan_3d06c0a576dd4800b90237b01580285c | `data/records/rec_ceiling_fan_3d06c0a576dd4800b90237b01580285c/revisions/rev_000001/model.py:L116-L281` | contemporary canopy/downrod/motor/blade_assembly chain with fixed downrod joints |
| S3 | rec_ceiling_fan_1f1b54669151405ab4d645caeeaf18f8 | `data/records/rec_ceiling_fan_1f1b54669151405ab4d645caeeaf18f8/revisions/rev_000001/model.py:L134-L336` | retractable blade storage ring, rotor spin, per-blade fold hinges |
| S4 | rec_ceiling_fan_e28b2f11959946fbad37ca3fb11f3ced | `data/records/rec_ceiling_fan_e28b2f11959946fbad37ca3fb11f3ced/revisions/rev_000001/model.py:L63-L247` | dual-head crossbar layout and two side fan heads on horizontal spin axes |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| ceiling_mount | required；canopy/ceiling plate/downrod 或 low-profile mount | mount_style, downrod_length, canopy_style, downrod_tilt_deg | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L217-L240`; S2 / `data/records/rec_ceiling_fan_3d06c0a576dd4800b90237b01580285c/revisions/rev_000001/model.py:L116-L198`; S4 / `data/records/rec_ceiling_fan_e28b2f11959946fbad37ca3fb11f3ced/revisions/rev_000001/model.py:L63-L93` |
| motor_housing | required；中心电机壳、hub、bearing cap 或 housing shell | housing_style, housing_radius, housing_height | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L242-L350`; S2 / `data/records/rec_ceiling_fan_3d06c0a576dd4800b90237b01580285c/revisions/rev_000001/model.py:L201-L248`; S3 / `data/records/rec_ceiling_fan_1f1b54669151405ab4d645caeeaf18f8/revisions/rev_000001/model.py:L134-L225` |
| rotor / blade_assembly | required；随 continuous joint 旋转的轮毂与叶片集合 | blade_count, blade_shape, blade_span, blade_pitch_deg, rotor_style | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L326-L383`; S2 / `data/records/rec_ceiling_fan_3d06c0a576dd4800b90237b01580285c/revisions/rev_000001/model.py:L252-L281`; S3 / `data/records/rec_ceiling_fan_1f1b54669151405ab4d645caeeaf18f8/revisions/rev_000001/model.py:L226-L336` |
| globe_or_light | optional；底部灯罩、light tray 或 globe | light_kit_style, globe_shape | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L384-L463` |
| retractable_blade_i | optional；可折叠叶片，每片有 root hinge | blade_variant, blade_fold_enabled, blade_fold_range | S3 / `data/records/rec_ceiling_fan_1f1b54669151405ab4d645caeeaf18f8/revisions/rev_000001/model.py:L270-L336` |
| crossbar / fan_head_i | optional；双头吊扇的横杆和左右风扇头 | fan_layout, head_count, guard_style | S4 / `data/records/rec_ceiling_fan_e28b2f11959946fbad37ca3fb11f3ced/revisions/rev_000001/model.py:L94-L247` |
| blade irons / brackets | optional visual；每片叶片根部金属支架 | bracket_style, detail_level | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L326-L377`; S2 / `data/records/rec_ceiling_fan_3d06c0a576dd4800b90237b01580285c/revisions/rev_000001/model.py:L265-L271` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| fan_spin | continuous | `(0, 0, 1)` for standard vertical fans | motor/rotor 共轴中心 | continuous | required；叶片组件绕竖直电机轴旋转 | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L433-L441`; S2 / `data/records/rec_ceiling_fan_3d06c0a576dd4800b90237b01580285c/revisions/rev_000001/model.py:L273-L281`; S3 / `data/records/rec_ceiling_fan_1f1b54669151405ab4d645caeeaf18f8/revisions/rev_000001/model.py:L255-L264` |
| blade_fold_i | revolute | `(0, 0, 1)` at blade root | retractable rotor hinge radius | `[0, pi/2]` | optional；可收纳叶片从切向折出到径向 | S3 / `data/records/rec_ceiling_fan_1f1b54669151405ab4d645caeeaf18f8/revisions/rev_000001/model.py:L314-L336` |
| downrod_to_motor | fixed | n/a | downrod lower collar | fixed | standard downrod layout 的固定连接 | S2 / `data/records/rec_ceiling_fan_3d06c0a576dd4800b90237b01580285c/revisions/rev_000001/model.py:L242-L248` |
| rotor_to_globe | fixed | n/a | rotor lower center | fixed | optional；灯罩跟随 rotor 或挂在 housing 下方，后续模板可固定到 rotor/housing | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L455-L463` |
| crossbar_yaw | revolute | `(0, 0, 1)` | downrod base | `[-0.75, 0.75]` | optional；双头横杆左右摆动 | S4 / `data/records/rec_ceiling_fan_e28b2f11959946fbad37ca3fb11f3ced/revisions/rev_000001/model.py:L219-L227` |
| fan_head_spin_i | revolute / continuous-compatible | `(1, 0, 0)` for dual side heads | each fan head motor axis | `[0, 2pi]` 或 continuous | optional；双头风扇左右 head 绕水平轴转 | S4 / `data/records/rec_ceiling_fan_e28b2f11959946fbad37ca3fb11f3ced/revisions/rev_000001/model.py:L228-L247` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| fan_layout | enum | `standard_downrod` / `hugger_low_profile` / `retractable` / `dual_head_crossbar` / `industrial_hvls` | `standard_downrod` | 决定 mount chain、spin axes、optional parts | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L217-L463`; S3 / `data/records/rec_ceiling_fan_1f1b54669151405ab4d645caeeaf18f8/revisions/rev_000001/model.py:L134-L336`; S4 / `data/records/rec_ceiling_fan_e28b2f11959946fbad37ca3fb11f3ced/revisions/rev_000001/model.py:L63-L247` |
| blade_count | int | `2-6` | `4` | standard/retractable radial placement；dual_head 每 head 可 3/4 | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L326-L383`; S2 / `data/records/rec_ceiling_fan_3d06c0a576dd4800b90237b01580285c/revisions/rev_000001/model.py:L265-L281` |
| blade_shape | enum | `flat_rectangular` / `palm_leaf` / `curved_airfoil` / `wide_hvls` / `guarded_small_rotor` | `curved_airfoil` | 决定 blade mesh/visual profile | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L352-L383`; S2 / `data/records/rec_ceiling_fan_3d06c0a576dd4800b90237b01580285c/revisions/rev_000001/model.py:L265-L271`; S4 / `data/records/rec_ceiling_fan_e28b2f11959946fbad37ca3fb11f3ced/revisions/rev_000001/model.py:L49-L60` |
| housing_style | enum | `cylindrical` / `drum` / `disc_hugger` / `wicker` / `rectangular_dual` / `storage_ring` | `cylindrical` | motor_housing shape | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L242-L325`; S2 / `data/records/rec_ceiling_fan_3d06c0a576dd4800b90237b01580285c/revisions/rev_000001/model.py:L201-L241`; S3 / `data/records/rec_ceiling_fan_1f1b54669151405ab4d645caeeaf18f8/revisions/rev_000001/model.py:L134-L225` |
| mount_style | enum | `short_downrod` / `long_downrod` / `angled_downrod` / `hugger_plate` / `crossbar_mount` | `short_downrod` | downrod_length and fixed mount joints | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L217-L240`; S2 / `data/records/rec_ceiling_fan_3d06c0a576dd4800b90237b01580285c/revisions/rev_000001/model.py:L116-L198`; S4 / `data/records/rec_ceiling_fan_e28b2f11959946fbad37ca3fb11f3ced/revisions/rev_000001/model.py:L63-L93` |
| downrod_length | float | `0.0-0.90` | `0.35` | `hugger_plate` 可为 0 | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L224-L239`; S4 / `data/records/rec_ceiling_fan_e28b2f11959946fbad37ca3fb11f3ced/revisions/rev_000001/model.py:L75-L92` |
| blade_variant | enum | `rigid_fixed` / `retractable_fold` / `dual_head_rotor` | `rigid_fixed` | 决定是否创建 blade_fold_i 或 horizontal fan_head joints | S3 / `data/records/rec_ceiling_fan_1f1b54669151405ab4d645caeeaf18f8/revisions/rev_000001/model.py:L270-L336`; S4 / `data/records/rec_ceiling_fan_e28b2f11959946fbad37ca3fb11f3ced/revisions/rev_000001/model.py:L191-L247` |
| light_kit_style | enum | `none` / `globe` / `integrated_tray` / `finial` | `none` | optional light/globe part | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L384-L463` |
| guard_style | enum | `none` / `dual_head_wire_cage` | `none` | dual_head_crossbar 默认 cage | S4 / `data/records/rec_ceiling_fan_e28b2f11959946fbad37ca3fb11f3ced/revisions/rev_000001/model.py:L118-L190` |
| material_style | enum | `brushed_metal` / `wood_traditional` / `tropical_wicker` / `matte_white` / `industrial_dark` | `brushed_metal` | palette only | S1 / `data/records/rec_ceiling_fan_0004/revisions/rev_000001/model.py:L204-L211`; S2 / `data/records/rec_ceiling_fan_3d06c0a576dd4800b90237b01580285c/revisions/rev_000001/model.py:L109-L113` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| mount/downrod | short downrod / long downrod / angled downrod / hugger plate / crossbar mount | no | yes | mount_style, fan_layout | 安装方式和父子链不同 |
| motor housing | cylinder/drum/disc/wicker/storage ring/rectangular dual | no | yes | housing_style | housing 是核心识别件，轮廓差异明显 |
| blades | flat / palm / curved airfoil / wide HVLS / guarded small rotor / retractable | no | yes | blade_shape, blade_variant | 叶片轮廓和折叠拓扑不能靠长度表达 |
| rotor layout | single vertical rotor / retractable radial hinges / dual horizontal heads | no | yes | fan_layout, blade_variant | 关节轴和 part tree 不同 |
| light kit | none / globe / integrated tray / finial | no | yes | light_kit_style | 灯具是常见定性变体 |
| blade count/span | none beyond count/scale | yes | no | blade_count, blade_span | 数量和长度可参数化，不需要额外 shape enum |
| decorative brackets | blade irons / collars / wire cage / ribs | partly | yes for cage | bracket_style, guard_style | cage 是 dual-head 识别结构；普通 brackets 可由 detail_level 控制 |

## 组合逻辑（Composition Logic）
1. 先生成 ceiling_mount：canopy、plate、downrod 或 hugger mount。
2. 生成 motor_housing，并通过 fixed joint 或 root visual 连接到 mount。
3. 标准布局创建 rotor/blade_assembly，并用 `fan_spin` continuous joint 绕 Z 轴旋转。
4. rigid blades 可作为 rotor visuals；若 `blade_variant = retractable_fold`，每片 blade 建独立 part 和 `blade_fold_i` revolute。
5. `dual_head_crossbar` 使用 mount -> crossbar -> fan_head_i，fan_head_i 绕水平 X 轴旋转。
6. light/globe、collars、blade irons、finials 可作为 rotor/housing visuals；若需要单独 validator 可用 fixed part。

## 已有模板写法参考
continuous_rotor / radial_array / revolute_hinge / rotary_post

## 约束
- 标准/低矮/伸缩叶片布局必须有一个主 continuous `fan_spin`，轴接近世界 Z。
- blade_count 与叶片 visual 或 blade part 数量一致，并等角度分布。
- 叶片根部必须连接到 hub/rotor，不可漂浮。
- `retractable_fold` 必须为每片 blade 创建 fold hinge，range 覆盖折叠到展开。
- `dual_head_crossbar` 的左右 fan head 必须位于 crossbar 两端，spin axis 接近 X。
- downrod 或 hugger plate 必须连接 ceiling canopy 和 motor housing。
- globe/light 若存在，必须位于 housing/rotor 下方且连接。

## Validator
| 检查项 | 标准 |
|---|---|
| required mount | 有 ceiling_mount/canopy 或 hugger plate |
| required rotor | 标准布局有 rotor/blade_assembly；dual 布局有 fan_head_i |
| spin joint | 标准布局有 continuous Z 轴 `fan_spin`；dual 布局每个 head 有水平 spin |
| blade count | 叶片数量等于 blade_count 或 dual 每 head 配置 |
| radial distribution | 单头叶片等角度分布 |
| retractable consistency | blade_variant=retractable_fold 时每片 blade 有 revolute fold joint |
| light consistency | light_kit_style != none 时有 globe/light visual or part |
| no floating | mount、motor、rotor、blades、light 全部连接 |
| part diversity | fan_layout、blade_shape、housing_style、mount_style、blade_variant 参数存在 |
| identity | 必须像吊扇，不是桌面风扇、螺旋桨或灯具 |

## Reject cases
- 没有可旋转叶片组件。
- 主旋转轴与电机轴不共线。
- 叶片数量和参数不一致或不等角分布。
- 叶片漂浮在 motor housing 外。
- 可折叠叶片样式没有 per-blade revolute hinge。
- 双头布局没有 crossbar 或 fan heads 不在两端。
- 只有灯具没有风扇身份。
- mount/downrod 缺失，导致不像 ceiling-mounted fixture。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核 |
