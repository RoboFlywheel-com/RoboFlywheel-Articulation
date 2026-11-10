# Retractable Utility Knife Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `retractable_utility_knife` |
| template path | `agent/templates/retractable_utility_knife.py` |
| test path | `tests/agent/test_retractable_utility_knife_template.py` |
| primary_anchor | `rec_retractable_utility_knife_cad8e728806e47b09531688f7de35ba7:rev_000001` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 22 |
| read_count | 22 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below; knife variants that do not share retractable-blade semantics should not be forced into this template |

## 核心身份
可伸缩美工刀/utility knife，必须包含固定外壳、内部导轨/滑槽、可沿刀身方向直线移动的 blade carrier，以及随 carrier 一起移动的刀片和 thumb slider。默认成熟域是 single-axis retractable knife：blade carrier 通过 prismatic joint 沿 handle X 方向伸缩，刀片固定在 carrier 上，thumb slider 固定在 carrier 上。可选 lock wheel、service door、sliding nose guard、storage tray，但这些部件必须从 handle/cavity 派生，不能悬空或和刀片运动语义冲突。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_retractable_utility_knife_cad8e728806e47b09531688f7de35ba7` | `data/records/rec_retractable_utility_knife_cad8e728806e47b09531688f7de35ba7/revisions/rev_000001/model.py:L25-L78` | blade mesh、rounded/lofted body、thumb slider helper |
| S2 | `rec_retractable_utility_knife_cad8e728806e47b09531688f7de35ba7` | `data/records/rec_retractable_utility_knife_cad8e728806e47b09531688f7de35ba7/revisions/rev_000001/model.py:L93-L193` | body shell、rails、nose cheeks、grip strips |
| S3 | `rec_retractable_utility_knife_cad8e728806e47b09531688f7de35ba7` | `data/records/rec_retractable_utility_knife_cad8e728806e47b09531688f7de35ba7/revisions/rev_000001/model.py:L195-L267` | blade carrier、blade、score lines、thumb slider |
| S4 | `rec_retractable_utility_knife_cad8e728806e47b09531688f7de35ba7` | `data/records/rec_retractable_utility_knife_cad8e728806e47b09531688f7de35ba7/revisions/rev_000001/model.py:L269-L335` | lock wheel and body_to_carrier prismatic / fixed child joints |
| S5 | `rec_retractable_utility_knife_0003` | `data/records/rec_retractable_utility_knife_0003/revisions/rev_000001/model.py:L39-L130` | lofted housing shell、inner cavity、top slot、blade/carrier/slider helpers |
| S6 | `rec_retractable_utility_knife_0003` | `data/records/rec_retractable_utility_knife_0003/revisions/rev_000001/model.py:L132-L229` | housing guides、integrated blade carrier、prismatic slide joint |
| S7 | `rec_retractable_utility_knife_14ce81bcecaa40e8a75ce0494a0de25f` | `data/records/rec_retractable_utility_knife_14ce81bcecaa40e8a75ce0494a0de25f/revisions/rev_000001/model.py:L59-L141` | handle shell、nose、grips、service-door hinge barrel |
| S8 | `rec_retractable_utility_knife_14ce81bcecaa40e8a75ce0494a0de25f` | `data/records/rec_retractable_utility_knife_14ce81bcecaa40e8a75ce0494a0de25f/revisions/rev_000001/model.py:L143-L239` | carriage、blade、thumb slider、service door、carriage prismatic and door hinge |
| S9 | `rec_retractable_utility_knife_9365487b3ea4413891567b9153bbf0ab` | `data/records/rec_retractable_utility_knife_9365487b3ea4413891567b9153bbf0ab/revisions/rev_000001/model.py:L69-L171` | handle guide, blade carrier, blade, thumb button |
| S10 | `rec_retractable_utility_knife_9365487b3ea4413891567b9153bbf0ab` | `data/records/rec_retractable_utility_knife_9365487b3ea4413891567b9153bbf0ab/revisions/rev_000001/model.py:L188-L226` | sliding nose guard and guard prismatic joint |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `handle_shell` | 外壳/root，含左右壳体厚度、导轨、鼻端开口、手握曲面或侧面防滑纹 | `knife_body_style`, `handle_length`, `handle_width`, `handle_height`, `shell_thickness` | S2 / S5 / S7 / S9 |
| `rail_channel` | carrier 的内部通道和限位 rails，可建为 handle 的固定几何 | `channel_width`, `channel_height`, `rail_clearance`, `rear_stop_x`, `front_stop_x` | S2 / S5 / S6 / S9 |
| `blade_carrier` | 可滑动刀片座，包含 rail shoe、blade clamp、slider post | `carrier_len`, `carrier_width`, `carrier_height`, `slide_travel` | S3 / S6 / S8 / S9 |
| `blade` | 梯形刀片、snap-off segmented blade 或 compact blade，固定在 carrier 上 | `blade_style`, `blade_len`, `blade_height`, `blade_thickness`, `segment_count` | S1 / S3 / S5 / S8 / S9 |
| `thumb_slider` | 顶部/侧部推钮，固定到 carrier，随 prismatic joint 一起移动 | `slider_style`, `slider_len`, `detent_count`, `slider_slot_len` | S1 / S3 / S5 / S8 / S9 |
| `nose_guard` | 前端护套或可滑动鼻罩，optional | `guard_style`, `guard_travel`, `guard_clearance` | S10 |
| `lock_wheel` / `lock_lever` | 锁定轮、锁片或安全钮，optional | `lock_style`, `lock_radius`, `lock_axis` | S4 |
| `service_door` | 换刀侧门、后盖或 blade storage tray，optional | `service_door_style`, `door_hinge_axis`, `door_open_angle` | S7 / S8 |
| `grip_pads` / `fasteners` | 防滑垫、螺丝、铆钉、标签等 fixed details | `grip_style`, `fastener_count` | S2 / S7 / S9 |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `body_to_blade_carrier` / `blade_slide` | prismatic | `(1, 0, 0)` | rail channel centerline at retracted carrier pose | `[0, slide_travel]` | 刀片座沿刀身前后伸缩，是主语义关节 | S4 / S6 / S8 / S9 |
| `carrier_to_blade` | fixed | n/a | blade clamp datum | n/a | 刀片固定到 carrier，随 carrier 移动 | S3 / S4 / S8 / S9 |
| `carrier_to_thumb_slider` | fixed | n/a | slider post datum | n/a | 推钮固定到 carrier，不能留在 handle 上 | S3 / S4 / S8 / S9 |
| `body_to_lock_wheel` | revolute or continuous | `(0, 1, 0)` typical | lock wheel center on side wall | `[-pi, pi]` or limited | 旋钮式锁定，optional | S4 |
| `body_to_service_door` | revolute | `(0, 0, 1)` or `(0, 1, 0)` | handle side/rear hinge barrel | `[0, 1.8]` rad typical | 换刀门或储刀盖，optional | S8 |
| `body_to_nose_guard` | prismatic | `(1, 0, 0)` | nose guard rail center | `[0, guard_travel]` | 可滑动护鼻，optional，不得与 blade_slide 混淆 | S10 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `knife_body_style` | enum | `snap_off_slim` / `box_cutter` / `heavy_duty` / `compact_safety` | `heavy_duty` | drives handle proportions, blade style, guard/door availability | S2 / S5 / S7 / S9 |
| `handle_length` | float | `0.13-0.23` | sampled | root envelope; constrains `carrier_len`, `slide_travel` | S2 / S5 / S7 / S9 |
| `handle_width` | float | `0.018-0.045` | sampled | derives channel width and blade thickness clearance | S2 / S5 / S7 / S9 |
| `handle_height` | float | `0.025-0.065` | sampled | derives rail/channel height and slider protrusion | S2 / S5 / S7 / S9 |
| `blade_style` | enum | `trapezoid` / `snap_off_segmented` / `compact_hook_like` | derived | `snap_off_slim` favors segmented; heavy duty favors trapezoid | S1 / S3 / S5 |
| `carrier_len` | float | derived, `0.28-0.45 * handle_length` | derived | must fit in channel at both retracted and extended poses | S3 / S6 / S8 / S9 |
| `slide_travel` | float | derived, typically `0.025-0.075` | derived | `min(max_blade_exposure, handle_length - rear_stop - nose_clearance - carrier_len)` | S4 / S6 / S8 / S9 |
| `max_blade_exposure` | float | `0.018-0.065` | sampled | caps `slide_travel`; blade tip exposure at max extension | S3 / S6 / S8 |
| `rail_clearance` | float | `0.0008-0.003` | sampled | channel dimensions = carrier dimensions + clearance | S2 / S5 / S9 |
| `detent_count` | int | `3-8` | sampled | positions along slider slot, does not create extra joints | S1 / S3 |
| `lock_style` | enum | `none` / `thumb_detent` / `lock_wheel` / `side_lever` | `thumb_detent` | `lock_wheel` enables revolute lock joint | S4 |
| `guard_style` | enum | `none` / `fixed_nose` / `sliding_nose` | `fixed_nose` | `sliding_nose` enables guard prismatic branch | S10 |
| `service_door_style` | enum | `none` / `side_hatch` / `rear_cap` / `storage_tray` | `none` | side/rear access part, gated by handle body style | S7 / S8 |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| handle shell | slim snap-off / chunky box cutter / compact safety / serviceable handle | no | yes | `knife_body_style` | 外壳拓扑、slot、door/guard availability 都不同 |
| blade | trapezoid / segmented snap-off / compact hook-like | no | yes | `blade_style`, `segment_count` | 刀尖和伸出量语义不同 |
| slider | top ridged tab / side thumb button / long slot slider | no | yes | `slider_style`, `detent_count` | 必须随 carrier 运动 |
| lock | detent only / lock wheel / lever | no | yes | `lock_style` | 是否有额外 revolute joint |
| guard | fixed nose / sliding nose guard / none | no | yes | `guard_style` | sliding guard 有独立 prismatic joint |
| service access | none / side door / rear cap / storage tray | no | yes | `service_door_style` | optional part 需要 hinge 或 fixed cap |
| slide travel | same topology inside handle | yes | no | `slide_travel`, `max_blade_exposure` | 由 handle/cavity 派生，不能自由采样 |

## 组合逻辑（Composition Logic）
1. 先采 `handle_length`, `handle_width`, `handle_height` 与 `knife_body_style`，生成 handle/root envelope 和 nose opening。
2. 从 handle envelope 派生内部 `rail_channel`：`channel_width = carrier_width + 2 * rail_clearance`，`channel_height = carrier_height + 2 * rail_clearance`。
3. 再采 `blade_style` 和 `max_blade_exposure`，根据 blade length、nose thickness、rear stop 计算 `slide_travel`。若计算结果小于最小可见伸出，必须重新采样 handle 或 blade，而不是把刀片悬空移出。
4. 生成 `blade_carrier` 的 retracted pose：carrier 后端不得穿过 rear stop，前端必须仍在 channel 内。
5. blade 固定到 carrier，刀尖在 retracted pose 可完全缩入或只露出安全小尖；max extension 时刀片露出不超过 `max_blade_exposure`。
6. `thumb_slider` 固定到 carrier，slider slot 长度 = `slide_travel + slider_len + detent_margin`，slot 位于 handle 顶部或侧面。
7. `lock_style=lock_wheel` 时，锁轮中心落在 side wall 上并与 carrier/slot 对齐；不得成为 carrier 的父 joint。
8. `guard_style=sliding_nose` 时，guard slide 与 blade slide 平行但独立，guard 必须包住 nose rails，不能覆盖 blade joint origin。
9. service door 只在 handle 侧壁/后端开口，hinge barrel 与 shell 接触；换刀门打开后不能切过 blade carrier 的 slide path。

## 已有模板写法参考
| 模板文件 | 可参考写法 |
|---|---|
| `agent/templates/Window_Sliding_window.py` | prismatic sliding part inside a retained frame/track, travel derived from opening size |
| `agent/templates/desk_with_drawer.py` | drawer-like prismatic slide, retained overlap, handle fixed to moving drawer |
| `agent/templates/camcorder_with_flipout_screen.py` | compact hinge placement for small service/access panels |
| `agent/templates/tackle_box_with_simple_hinged_lid.py` | hinged lid/door joint limits and fixed latch/details on parent body |


## 约束
- 必须存在 `blade_slide` prismatic joint，axis 为 handle 长轴 X。
- blade 和 thumb slider 必须是 carrier 的 fixed children 或同一 moving part；不能固定在 handle 上。
- `slide_travel` 必须由 handle length、carrier length、nose clearance、max blade exposure 派生。
- carrier 在 max extension 时仍要有 retained rail overlap，不得完全脱离 handle。
- blade thickness 必须小于 channel width 且穿过 nose opening，不得与 shell 侧壁穿模。
- slider slot 必须覆盖 slider 在 min/max pose 的轨迹。
- guard/door/lock 是 optional branch，必须与 handle 接触或通过 joint 连接。
- lock wheel/door/guard 的关节不能替代 blade_slide 语义。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | handle shell + blade carrier + blade + thumb slider present |
| main joint | exactly one primary blade prismatic joint along `(1,0,0)` unless explicitly multi-stage safety variant |
| moving group | blade and thumb slider move with carrier |
| retained overlap | carrier at max extension still overlaps rail/channel by `retained_overlap_min` |
| blade exposure | retracted and extended blade tip positions within legal range |
| slot coverage | thumb slider slot covers whole travel plus margin |
| channel clearance | carrier fits inside channel in Y/Z with positive clearance |
| optional compatibility | lock/guard/service door only present with matching style and valid joint axis |
| no floating | blade、slider、guard、door、lock、grip pads 均有 parent 或 contact |

## Reject cases
- 刀片只是固定在 handle 前端，没有可滑动 carrier。
- thumb slider 不随刀片运动，或 slider 留在 handle 上。
- blade_slide axis 不是刀身长轴，导致刀片横向/竖向滑动。
- carrier 最大伸出时完全脱离导轨。
- 刀片伸出长度随机过大，穿过 handle 或不受 nose opening 约束。
- service door、lock wheel、nose guard 悬空或关节轴语义错误。
- 只有开合刀/折刀 hinge，没有 retractable utility knife 的 slide 语义。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
