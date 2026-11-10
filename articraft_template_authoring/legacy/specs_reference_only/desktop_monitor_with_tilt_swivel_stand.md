# Desktop Monitor With Tilt Swivel Stand Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `desktop_monitor_with_tilt_swivel_stand` |
| template path | `agent/templates/desktop_monitor_with_tilt_swivel_stand.py` |
| test path | `tests/agent/test_desktop_monitor_with_tilt_swivel_stand_template.py` |
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
桌面显示器，至少包含显示屏外壳、屏幕玻璃/面板、桌面底座、支撑颈/立柱，以及允许屏幕倾斜和整机水平转动的支架关节。高度调节、portrait 旋转、控制按钮和线缆盖是常见但可选的增强活动件。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041` | `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L31-L87` | office rounded pedestal base, slim neck, yoke ears, swivel joint |
| S2 | `rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041` | `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L89-L146` | flat display shell, bezel, hinge barrel, tilt revolute joint |
| S3 | `rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041` | `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L148-L193` | rocker and menu button controls with revolute/prismatic button joints |
| S4 | `rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436` | `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L24-L65` | curved screen cadquery planform and shell/screen surfaces |
| S5 | `rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436` | `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L90-L149` | tripod legs and split rear yoke mesh |
| S6 | `rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436` | `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L162-L382` | gaming base, height column, yoke, display, joystick, swivel/height/tilt/control joints |
| S7 | `rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280` | `data/records/rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280/revisions/rev_000001/model.py:L155-L243` | bounded swivel and height-adjustable mast with slider rails |
| S8 | `rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280` | `data/records/rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280/revisions/rev_000001/model.py:L246-L370` | tilt head, VESA plate, display shell, portrait rotation joint |
| S9 | `rec_desktop_monitor_with_tilt_swivel_stand_2bc82fbc8fc14ca8a8304febb6ff451f` | `data/records/rec_desktop_monitor_with_tilt_swivel_stand_2bc82fbc8fc14ca8a8304febb6ff451f/revisions/rev_000001/model.py:L209-L274` | hinged rear cable cover and cable door joint |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `base` | 桌面支撑底座，可为圆角底盘、矩形重底座、V 形脚或三脚 gaming base | `base_style`, `base_width`, `base_depth`, `base_foot_count` | S1 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L31-L87`; S5 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L90-L149`; S6 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L162-L195` |
| `stand` / `carriage` | 底座上的可转动或可升降支撑段 | `stand_layout`, `stand_height`, `height_travel`, `column_profile` | S1 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L47-L87`; S6 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L196-L234`; S7 / `data/records/rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280/revisions/rev_000001/model.py:L155-L243` |
| `yoke` / `tilt_head` | 屏幕后方的倾斜支架，含 yoke ears、tilt barrel、VESA plate 或 split yoke | `yoke_style`, `tilt_axis_height`, `has_vesa_plate` | S2 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L120-L146`; S5 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L106-L149`; S8 / `data/records/rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280/revisions/rev_000001/model.py:L246-L296` |
| `display` / `screen` | 显示器外壳、前 bezel、屏幕玻璃和后壳 | `screen_profile`, `screen_width`, `screen_height`, `screen_depth`, `bezel_style` | S2 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L89-L146`; S4 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L24-L65`; S6 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L260-L309` |
| `controls` | 下边框或屏幕底部的按钮、rocker、joystick、side wheel | `controls_style`, `menu_button_count`, `has_power_button` | S3 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L148-L193`; S6 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L310-L382` |
| `cable_cover` | 后部立柱或背壳的可开合线缆盖，optional | `cable_cover_style`, `cable_cover_height` | S9 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_2bc82fbc8fc14ca8a8304febb6ff451f/revisions/rev_000001/model.py:L209-L274` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `base_to_stand_swivel` | continuous or revolute | `(0, 0, 1)` | base bearing center | continuous or `[-0.65, 0.65]` | 底座上方支架水平转动 | S1 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L79-L87`; S6 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L330-L338`; S7 / `data/records/rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280/revisions/rev_000001/model.py:L155-L168` |
| `height_adjust_joint` | prismatic | `(0, 0, 1)` | sleeve/column centerline | `[0, 0.08]` m typical | 立柱升降，optional but common | S6 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L339-L347`; S7 / `data/records/rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280/revisions/rev_000001/model.py:L231-L243` |
| `tilt_joint` | revolute | `(1, 0, 0)` or `(-1, 0, 0)` | yoke barrel at stand head | `[-0.25, 0.40]` rad or approx `[-12°, 20°]` | 屏幕前后倾斜 | S2 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L133-L146`; S6 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L355-L368`; S8 / `data/records/rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280/revisions/rev_000001/model.py:L283-L296` |
| `portrait_pivot_joint` | revolute | `(0, 1, 0)` | VESA plate / rear hub center | `[-pi/2, pi/2]` | 屏幕横竖屏旋转，optional | S8 / `data/records/rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280/revisions/rev_000001/model.py:L359-L370` |
| `menu_button_joint` | prismatic | `(0, 1, 0)` | lower bezel button socket | `[0, 0.0035]` m | 菜单按钮向内按压，optional | S3 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L171-L193` |
| `rocker_or_joystick_joint` | revolute | `(1, 0, 0)` | lower bezel or underside socket | `[-0.28, 0.28]` rad typical | rocker 或 joystick 小幅摆动，optional | S3 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L148-L169`; S6 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L369-L382` |
| `cable_cover_hinge` | revolute | `(0, 0, 1)` | rear stand spine vertical edge | `[0, 1.35]` rad | 后部线缆盖向外打开，optional | S9 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_2bc82fbc8fc14ca8a8304febb6ff451f/revisions/rev_000001/model.py:L266-L274` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `screen_profile` | enum | `flat_rect` / `boxy_flat` / `thin_premium` / `curved_wide` | `flat_rect` | `curved_wide` 使用 curved planform mesh | S2 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L89-L146`; S4 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L24-L65` |
| `base_style` | enum | `rounded_pedestal` / `rect_plate` / `v_foot` / `tripod` | `rounded_pedestal` | `tripod` implies split yoke/gaming proportions | S1 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L31-L45`; S5 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L90-L149`; S6 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L162-L195` |
| `stand_layout` | enum | `slim_neck` / `broad_column` / `telescoping_column` / `split_yoke` | `telescoping_column` | drives height joint and yoke geometry | S1 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L47-L78`; S6 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L196-L259`; S7 / `data/records/rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280/revisions/rev_000001/model.py:L170-L243` |
| `controls_style` | enum | `none` / `menu_buttons` / `rocker_and_buttons` / `joystick` / `side_wheel` | `menu_buttons` | controls optional part count and joint type | S3 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L148-L193`; S6 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L310-L382` |
| `screen_width` | float | `0.52-0.90` | `0.62` | paired with aspect ratio | S2 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L89-L119`; S6 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L260-L309` |
| `screen_aspect_ratio` | float | `1.55-2.35` | `1.78` | `screen_height = screen_width / ratio` | S2 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L89-L119` |
| `height_travel` | float | `0.0-0.12` | `0.08` | `0` disables height joint unless `stand_layout=telescoping_column` | S6 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_4a6a5aebe7bc4500b9587338fba60436/revisions/rev_000001/model.py:L339-L347`; S7 / `data/records/rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280/revisions/rev_000001/model.py:L231-L243` |
| `tilt_range` | tuple[float, float] | `[-0.25, 0.40]` rad typical | `(-0.20, 0.35)` | maps to `tilt_joint.motion_limits` | S2 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L133-L146`; S8 / `data/records/rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280/revisions/rev_000001/model.py:L283-L296` |
| `has_portrait_pivot` | bool | `true` / `false` | `false` | if true insert `tilt_head -> screen` portrait joint | S8 / `data/records/rec_a-gaming-monitor-with-a-broad-screen-a-v-shaped-_20260407_110625_748379_119c2280/revisions/rev_000001/model.py:L359-L370` |
| `menu_button_count` | int | `0-5` | `3` | ignored when `controls_style=none` or `joystick` | S3 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_04c3533227724245bc59022d84d6b041/revisions/rev_000001/model.py:L171-L193` |
| `cable_cover_style` | enum | `none` / `hinged_rear_door` / `static_channel` | `none` | if `hinged_rear_door`, add `cable_cover_hinge`; if `static_channel`, use stand visual | S9 / `data/records/rec_desktop_monitor_with_tilt_swivel_stand_2bc82fbc8fc14ca8a8304febb6ff451f/revisions/rev_000001/model.py:L209-L274` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| display shell | flat rectangular / boxy business / thin premium / curved gaming | no | yes | `screen_profile` | 曲面 planform 和平面 box 不是单纯尺寸变化 |
| base | rounded pedestal / rectangular plate / V-shaped foot / tripod legs | no | yes | `base_style` | 底座拓扑差异明显 |
| stand / column | slim fixed neck / broad column / telescoping sleeve / split yoke | no | yes | `stand_layout` | 决定是否有高度 joint 和 yoke 结构 |
| yoke / tilt head | compact hinge barrel / two yoke ears / split rear yoke / VESA portrait housing | no | yes | `yoke_style`, `has_portrait_pivot` | 支架头部拓扑和 joint chain 不同 |
| controls | button row / rocker + buttons / joystick / side wheel / none | no | yes | `controls_style` | 操作件形态和关节类型不同 |
| cable cover | rear cable-cover door appears in prompts but adopted source not selected | no | yes | `cable_cover_style` | 观察到定性差异；默认 optional visual or review-gated joint |
| screen size | width/height/depth continuous variation | yes | no | `screen_width`, `screen_aspect_ratio` | 同一 screen profile 内尺寸可连续表达 |

## 组合逻辑（Composition Logic）
1. 生成 `base`，按 `base_style` 创建底盘、脚架或 tripod visual。
2. 在 base 上创建 `stand` 或 `carriage`；添加 yaw/swivel joint。
3. 若 `height_travel > 0`，用 sleeve/inner column 结构插入 `height_adjust_joint`。
4. 创建 yoke 或 tilt head，使 tilt origin 位于屏幕后方支架中心，不在屏幕几何中点乱放。
5. 创建 display/screen；`curved_wide` 使用 curved planform，其他 profile 使用 rounded bezel 或 Box/BezelGeometry。
6. 添加 `tilt_joint`；若 `has_portrait_pivot`，tilt head 先连接 portrait housing，再连接 screen。
7. controls 按 `controls_style` 作为小 part 挂到 display 下边框或 underside；普通静态刻线可为 visual。

## 已有模板写法参考
revolute_hinge / prismatic_slide / telescoping_tube / button_slider

## 约束
- 屏幕必须宽于高，除非 portrait joint 在 pose 中旋转。
- `tilt_joint` axis 必须水平且穿过 stand head/yoke，不得位于底座。
- `base_to_stand_swivel` axis 必须为 `(0, 0, 1)`。
- 高度调节的 inner column 必须保持插入 sleeve，不得升高后漂浮。
- yoke ears 或 hinge barrel 必须与 display rear hub 接触或被捕获。
- controls 必须贴在 lower bezel/underside，不能漂浮在屏幕前方。
- `curved_wide` 必须有可见弧形 shell/screen，不允许只用平面 box 冒充。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | 必须有 base、stand/yoke、display/screen |
| joint count | 至少 1 个 swivel/yaw + 1 个 tilt revolute |
| swivel axis | base swivel axis 为 `(0, 0, 1)` |
| tilt axis | tilt axis 为水平 X 方向或其反向 |
| height adjustment | 若 `height_travel > 0`，column 沿 Z 上升且 retained insertion 成立 |
| portrait pivot | 若 `has_portrait_pivot=true`，pose 后屏幕 AABB 高宽方向交换 |
| control attachment | controls 与 lower bezel/underside 接触，且 menu buttons 数量匹配 |
| part diversity | `screen_profile`, `base_style`, `stand_layout`, `controls_style` 均存在并驱动几何分支 |
| no floating | display、yoke、column、controls 全连接到主树 |

## Reject cases
- 只有屏幕和一个静态杆，没有 tilt 或 swivel joint。
- tilt axis 竖直或放在底座上，导致不是屏幕倾斜。
- 底座太小或不接触桌面，整机像漂浮屏幕。
- 曲面显示器仍是完全平板几何。
- 高度调节 column 拉出后脱离 sleeve。
- 按钮、rocker 或 joystick 漂浮在 bezel 外。
- portrait pivot 与 tilt joint 混成同一轴，无法横竖屏旋转。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
