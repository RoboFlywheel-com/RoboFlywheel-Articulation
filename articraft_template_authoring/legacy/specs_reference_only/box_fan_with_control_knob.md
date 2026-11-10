# Box Fan With Control Knob Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `box_fan_with_control_knob` |
| template path | `agent/templates/box_fan_with_control_knob.py` |
| test path | `tests/agent/test_box_fan_with_control_knob_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 57 |
| read_count | 57 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
带控制旋钮的箱式风扇，至少包含方形/矩形风扇外壳、前后护网或格栅、可连续旋转的叶轮/桨叶，以及安装在外壳或控制舱上的可旋转速度旋钮。可选支撑、提手、百叶/扩展板等只增强具体形态，不替代箱式风扇的核心身份。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_box_fan_with_control_knob_0001` | `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L38-L118` | curved blade loft + rectangular wire grille helper |
| S2 | `rec_box_fan_with_control_knob_0001` | `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L120-L348` | single square housing, carry handle, control pod, rotor, knob, spin/knob joints |
| S3 | `rec_box_fan_with_control_knob_0007` | `data/records/rec_box_fan_with_control_knob_0007/revisions/rev_000001/model.py:L151-L375` | wide twin-rotor layout and top control pod |
| S4 | `rec_box_fan_with_control_knob_0008` | `data/records/rec_box_fan_with_control_knob_0008/revisions/rev_000001/model.py:L167-L505` | U/yoke tilt stand, separate front/rear grille parts, vintage side knob |
| S5 | `rec_box_fan_with_control_knob_88551567beac46d193a74e7d338e8f17` | `data/records/rec_box_fan_with_control_knob_88551567beac46d193a74e7d338e8f17/revisions/rev_000001/model.py:L221-L427` | pedestal base, telescoping column, rear knob, vertical prismatic support |
| S6 | `rec_box_fan_with_control_knob_d9894599488843469b40328b8af07b4d` | `data/records/rec_box_fan_with_control_knob_d9894599488843469b40328b8af07b4d/revisions/rev_000001/model.py:L31-L398` | industrial square vent frame, four hinged shutter panels, side speed dial |
| S7 | `rec_box_fan_with_control_knob_c357865be60f4a25b2bf0bc3dff4de22` | `data/records/rec_box_fan_with_control_knob_c357865be60f4a25b2bf0bc3dff4de22/revisions/rev_000001/model.py:L190-L337` | hinged side expansion panels, broad rotor geometry, skirted fluted knob |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `housing` | required；方形/矩形主外壳，承载格栅、马达舱、控制面板、支撑连接点 | `housing_width`, `housing_height`, `housing_depth`, `housing_profile`, `housing_layout` | S2 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L133-L231`; S3 / `data/records/rec_box_fan_with_control_knob_0007/revisions/rev_000001/model.py:L151-L285`; S6 / `data/records/rec_box_fan_with_control_knob_d9894599488843469b40328b8af07b4d/revisions/rev_000001/model.py:L31-L122` |
| `front_grille` / `rear_grille` | required visual or fixed parts；护网可为线框格栅、矩形条栅或独立前后 grille part | `grille_style`, `grille_density`, `grille_depth_offset` | S1 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L71-L118`; S4 / `data/records/rec_box_fan_with_control_knob_0008/revisions/rev_000001/model.py:L365-L391` |
| `rotor` | required；中心叶轮或双叶轮，含 hub、cap、blade array | `rotor_count`, `blade_count`, `blade_shape`, `hub_style`, `rotor_radius` | S1 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L38-L68`; S2 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L258-L289`; S3 / `data/records/rec_box_fan_with_control_knob_0007/revisions/rev_000001/model.py:L287-L311`; S7 / `data/records/rec_box_fan_with_control_knob_c357865be60f4a25b2bf0bc3dff4de22/revisions/rev_000001/model.py:L237-L260` |
| `speed_knob` | required；外露速度/定时旋钮，带轴、指示线、可选裙边/滚花 | `knob_mount`, `knob_style`, `knob_radius`, `knob_range_deg` | S2 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L291-L314`; S4 / `data/records/rec_box_fan_with_control_knob_0008/revisions/rev_000001/model.py:L413-L451`; S7 / `data/records/rec_box_fan_with_control_knob_c357865be60f4a25b2bf0bc3dff4de22/revisions/rev_000001/model.py:L276-L300` |
| `control_pod` | optional；顶部或侧面控制舱/背板，旋钮可挂其上；简单样本可作为 housing visual | `control_pod_style`, `control_pod_mount` | S2 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L233-L256`; S3 / `data/records/rec_box_fan_with_control_knob_0007/revisions/rev_000001/model.py:L237-L248` |
| `support` | optional；桌面 U 架、底座、墙架、夹具或落地伸缩柱 | `support_style`, `tilt_range_deg`, `height_adjust_range` | S4 / `data/records/rec_box_fan_with_control_knob_0008/revisions/rev_000001/model.py:L167-L238`; S5 / `data/records/rec_box_fan_with_control_knob_88551567beac46d193a74e7d338e8f17/revisions/rev_000001/model.py:L221-L270` |
| `shutter_or_expansion_panel` | optional；通风百叶或窗口扩展侧板，可作为独立 hinged parts | `panel_layout`, `panel_count`, `panel_range_deg` | S6 / `data/records/rec_box_fan_with_control_knob_d9894599488843469b40328b8af07b4d/revisions/rev_000001/model.py:L200-L398`; S7 / `data/records/rec_box_fan_with_control_knob_c357865be60f4a25b2bf0bc3dff4de22/revisions/rev_000001/model.py:L262-L337` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `rotor_spin_i` | continuous | `(0, 1, 0)` default；部分样本以 X/Z 为建模光轴时需随模板坐标统一校正到风扇前后轴 | rotor hub center | unbounded；velocity 18-28 | 每个叶轮绕中心轴连续旋转 | S2 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L323-L334`; S3 / `data/records/rec_box_fan_with_control_knob_0007/revisions/rev_000001/model.py:L338-L355`; S4 / `data/records/rec_box_fan_with_control_knob_0008/revisions/rev_000001/model.py:L482-L492` |
| `speed_knob_turn` | revolute or continuous | mounted normal；front knob usually `(0, 1, 0)`, top knob usually `(0, 0, 1)` | knob shaft center on control pod/body | 0-120° / 0-275° / continuous | 速度旋钮旋转，必须附着在控制舱或 housing 上 | S2 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L335-L348`; S4 / `data/records/rec_box_fan_with_control_knob_0008/revisions/rev_000001/model.py:L494-L505`; S7 / `data/records/rec_box_fan_with_control_knob_c357865be60f4a25b2bf0bc3dff4de22/revisions/rev_000001/model.py:L329-L337` |
| `housing_tilt` | revolute, optional | `(1, 0, 0)` or equivalent horizontal hinge axis | side trunnions or yoke pivot | about -12° to 24°; compact stands may allow wider | 桌面/地面支架上的箱体俯仰 | S4 / `data/records/rec_box_fan_with_control_knob_0008/revisions/rev_000001/model.py:L454-L467` |
| `column_extension` | prismatic, optional | `(0, 0, 1)` | pedestal socket | 0-0.18 m | 落地款伸缩高度调节 | S5 / `data/records/rec_box_fan_with_control_knob_88551567beac46d193a74e7d338e8f17/revisions/rev_000001/model.py:L388-L395` |
| `panel_hinge_i` | revolute, optional | top/bottom panels around `(±1, 0, 0)`；side panels around `(0, 0, ±1)` | corresponding housing edge | 0-1.32 rad; expansion panels about -0.15-1.10 rad | 百叶/侧扩展板外翻 | S6 / `data/records/rec_box_fan_with_control_knob_d9894599488843469b40328b8af07b4d/revisions/rev_000001/model.py:L230-L364`; S7 / `data/records/rec_box_fan_with_control_knob_c357865be60f4a25b2bf0bc3dff4de22/revisions/rev_000001/model.py:L311-L328` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `housing_width` | float | 0.38-1.20 | 0.52 | `rotor_count=2` 时宽度增大 | S2 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L125-L163`; S3 / `data/records/rec_box_fan_with_control_knob_0007/revisions/rev_000001/model.py:L151-L235` |
| `housing_height` | float | 0.40-1.20 | 0.54 | tower/pedestal variants may decouple height and rotor radius | S2 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L125-L163`; S6 / `data/records/rec_box_fan_with_control_knob_d9894599488843469b40328b8af07b4d/revisions/rev_000001/model.py:L31-L122` |
| `housing_profile` | enum | `square_box` / `wide_twin` / `industrial_vent` | `square_box` | determines frame proportions and rotor placement | S2 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L133-L231`; S3 / `data/records/rec_box_fan_with_control_knob_0007/revisions/rev_000001/model.py:L151-L285`; S6 / `data/records/rec_box_fan_with_control_knob_d9894599488843469b40328b8af07b4d/revisions/rev_000001/model.py:L31-L122` |
| `rotor_count` | int | 1 / 2 | 1 | two rotors require `housing_profile=wide_twin` or equivalent widened layout | S3 / `data/records/rec_box_fan_with_control_knob_0007/revisions/rev_000001/model.py:L250-L355` |
| `blade_count` | int | 3-6 | 5 | drives radial array | S2 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L282-L289`; S3 / `data/records/rec_box_fan_with_control_knob_0007/revisions/rev_000001/model.py:L287-L295` |
| `blade_shape` | enum | `lofted_curved` / `flat_panel` / `broad_rotor_geometry` | `lofted_curved` | changes blade mesh, not just pitch | S1 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L38-L68`; S6 / `data/records/rec_box_fan_with_control_knob_d9894599488843469b40328b8af07b4d/revisions/rev_000001/model.py:L124-L189`; S7 / `data/records/rec_box_fan_with_control_knob_c357865be60f4a25b2bf0bc3dff4de22/revisions/rev_000001/model.py:L237-L260` |
| `grille_style` | enum | `wire_grid` / `rectangular_bar_guard` / `separate_chrome_grille` | `wire_grid` | controls helper and whether grille is visual vs fixed part | S1 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L71-L118`; S4 / `data/records/rec_box_fan_with_control_knob_0008/revisions/rev_000001/model.py:L365-L391` |
| `knob_mount` | enum | `top_pod` / `front_corner` / `side_panel` / `rear_boss` | `front_corner` | determines knob axis and origin | S2 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L233-L256`; S4 / `data/records/rec_box_fan_with_control_knob_0008/revisions/rev_000001/model.py:L413-L505`; S5 / `data/records/rec_box_fan_with_control_knob_88551567beac46d193a74e7d338e8f17/revisions/rev_000001/model.py:L357-L427` |
| `knob_style` | enum | `plain_cylindrical` / `ribbed_bakelite` / `skirted_fluted` | `plain_cylindrical` | changes knob body geometry and indicator | S2 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L291-L314`; S4 / `data/records/rec_box_fan_with_control_knob_0008/revisions/rev_000001/model.py:L413-L451`; S7 / `data/records/rec_box_fan_with_control_knob_c357865be60f4a25b2bf0bc3dff4de22/revisions/rev_000001/model.py:L276-L300` |
| `support_style` | enum | `none` / `feet` / `u_tilt_stand` / `pedestal_column` | `feet` | controls support part and optional joints | S2 / `data/records/rec_box_fan_with_control_knob_0001/revisions/rev_000001/model.py:L165-L203`; S4 / `data/records/rec_box_fan_with_control_knob_0008/revisions/rev_000001/model.py:L167-L238`; S5 / `data/records/rec_box_fan_with_control_knob_88551567beac46d193a74e7d338e8f17/revisions/rev_000001/model.py:L221-L270` |
| `panel_layout` | enum | `none` / `side_expansion_pair` / `four_shutters` | `none` | if not none, creates `panel_hinge_i` joints | S6 / `data/records/rec_box_fan_with_control_knob_d9894599488843469b40328b8af07b4d/revisions/rev_000001/model.py:L200-L398`; S7 / `data/records/rec_box_fan_with_control_knob_c357865be60f4a25b2bf0bc3dff4de22/revisions/rev_000001/model.py:L262-L337` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| housing | square box / wide twin-window / industrial vent frame | no | yes | `housing_profile` | 57 个 5 星样本中外壳拓扑和 rotor 布局不同，不能只靠宽高表达 |
| grille | wire grid / bar guard / separate framed front-rear grilles | no | yes | `grille_style` | 格栅结构决定识别度和是否独立固定 part |
| rotor/blades | lofted curved blades / flat box blades / broad SDK rotor blades / twin rotors | no | yes | `blade_shape`, `rotor_count` | blade 轮廓与数量/拓扑都有定性差异 |
| knob | plain small cylinder / ribbed bakelite / skirted fluted / top vs side vs rear mounting | no | yes | `knob_style`, `knob_mount` | 旋钮是类别名核心部件，安装面改变 axis/origin |
| support | feet / U tilt stand / pedestal telescoping column / none | no | yes | `support_style` | 支撑结构决定是否需要 tilt 或 prismatic joint |
| shutter_or_expansion_panel | none / side expansion pair / four hinged shutters | no | yes | `panel_layout` | 可动附加板是样本中的稳定定性变体，连续尺寸不足 |
| carry_handle | integrated top bridge / rear folding handle / none | no | yes | `handle_style` | 观察到固定提手和折叠提手，若实现需 enum；不作为 required |
| hub | layered cap/collar / simple cylinder / spherical nose cap | no | yes | `hub_style` | hub 外形是叶轮中心视觉差异，不能只靠半径表达 |

## 组合逻辑（Composition Logic）
1. 根据 `housing_profile` 和 `rotor_count` 先确定 housing 外包络、rotor 中心、front/rear face offset。
2. 构建 housing frame，再挂载格栅；简单 wire/bar grille 可作为 housing visual，独立 chrome grille 用 fixed part。
3. 为每个 rotor 创建 `rotor_i`，按中心点生成 hub、cap、blade array，并添加 `rotor_spin_i` continuous joint。
4. 根据 `knob_mount` 派生 control pod/backplate、knob origin 和 axis，再添加 `speed_knob_turn`。
5. 根据 `support_style` 可选添加 feet、U/yoke stand 或 pedestal column；只有支撑确实可动时添加 `housing_tilt` 或 `column_extension`。
6. 根据 `panel_layout` 可选添加 side expansion pair 或 four shutters，并把每块 panel 挂到 housing 边缘的 revolute hinge。

## 已有模板写法参考
continuous_rotor / revolute_hinge / prismatic_slide / telescoping_tube / button_slider / handle_grip

## 约束
- 必须至少有 1 个 rotor continuous joint 和 1 个 speed knob joint。
- 旋钮必须附着在 housing/control pod/support boss 上，不可漂浮在风扇前方。
- 叶轮必须位于格栅内侧，并与 housing 开口同心或在 twin 布局中与各自开口同心。
- `rotor_count=2` 时必须创建两个独立 rotor part 和两个 spin joints。
- 格栅不得严重遮挡旋钮；front grille 与 rotor 之间保留可见间隙。
- `support_style=pedestal_column` 时 column 必须从 base 竖直伸缩，housing 固定在 column 顶部。
- `panel_layout` 非 none 时每个 panel 的 hinge origin 必须在对应 housing 边缘。
- 非可动装饰如徽标、脚垫、标签默认作为 parent visual，不创建独立 part。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | 有箱式 housing、grille、rotor/blades、control knob |
| rotor joint count | `rotor_count` 个 continuous spin joints |
| rotor axis check | 默认 axis 与风扇前后轴一致，单模板坐标中为 `(0, 1, 0)` |
| knob joint | 至少 1 个 revolute/continuous knob joint，origin 在 knob shaft 上 |
| knob attachment | knob 与 control pod/housing 接触或小间隙嵌入 |
| grille placement | front grille 在 rotor 前方，rear grille/guard 不与 rotor 严重穿模 |
| support joints | tilt stand 有 revolute；pedestal column 有 Z prismatic；feet-only 不创建假 joint |
| panel joints | `panel_layout` 非 none 时每块 panel 有 revolute hinge，axis 与边缘方向一致 |
| part diversity | `housing_profile`, `grille_style`, `blade_shape`, `knob_style`, `knob_mount`, `support_style`, `panel_layout` 均暴露 |
| no floating | housing 是主树根，所有 required/optional movable parts 连接到主树 |

## Reject cases
- 没有可旋转叶轮或叶轮不在箱式格栅内部。
- 没有可见控制旋钮，或旋钮只是贴图/颜色点。
- 旋钮关节轴与安装面明显不一致。
- 外壳变成普通圆形台扇、无箱式框架。
- 格栅缺失或只用半透明平面代替。
- 双风扇布局只有一个 rotor joint。
- 支架、百叶或侧板漂浮，未通过 joint/fixed articulation 连接。
- 可动 shutter/panel 轴放在面板中间而不是边缘。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核 |
