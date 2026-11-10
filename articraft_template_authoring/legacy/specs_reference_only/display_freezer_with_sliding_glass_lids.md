# Display Freezer With Sliding Glass Lids Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `display_freezer_with_sliding_glass_lids` |
| template path | `agent/templates/display_freezer_with_sliding_glass_lids.py` |
| test path | `tests/agent/test_display_freezer_with_sliding_glass_lids_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 33 |
| read_count | 33 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
展示冷柜带滑动玻璃盖，必须有低矮厚壁冷柜箱体、上开口冷藏腔、顶面导轨 / 分层 runner，以及一块或多块透明玻璃盖沿导轨水平滑动。类别识别重点不是“冰柜颜色”，而是 display freezer 的 open-top insulated tub、framed glass lid、rail overlap、pull grip、内胆 / 篮筐 / 控制面板等商业冷柜细节。

采纳策略：全部 5 星样本用于确定真实类别分布，但模板阶段不应强行复刻每个样本。被采纳代码片段应映射到 `cabinet envelope helper`、`lid profile helper`、`rail helper`、`interior storage helper`、`control/caster optional helper`；无法放进同一 body/lid/rail/storage 兼容矩阵的样本只作为 future variant 或 split evidence。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_display_freezer_with_sliding_glass_lids_5717fea023294d5486ce6ea63a47b2e7` | `data/records/rec_display_freezer_with_sliding_glass_lids_5717fea023294d5486ce6ea63a47b2e7/revisions/rev_000001/model.py:L59-L126` | reusable framed glass lid helper: side rails, cross rails, glass pane, pull grip and sliding shoes |
| S2 | `rec_display_freezer_with_sliding_glass_lids_5717fea023294d5486ce6ea63a47b2e7` | `data/records/rec_display_freezer_with_sliding_glass_lids_5717fea023294d5486ce6ea63a47b2e7/revisions/rev_000001/model.py:L222-L393` | insulated cabinet envelope, walls, top rim, inner liner, dual guide rails and end stops |
| S3 | `rec_display_freezer_with_sliding_glass_lids_5717fea023294d5486ce6ea63a47b2e7` | `data/records/rec_display_freezer_with_sliding_glass_lids_5717fea023294d5486ce6ea63a47b2e7/revisions/rev_000001/model.py:L395-L548` | wire basket insert, two sliding lids, prismatic lid joints and travel limits |
| S4 | `rec_display_freezer_with_sliding_glass_lids_4aeda36374044bd4b297e66c6a6c34d2` | `data/records/rec_display_freezer_with_sliding_glass_lids_4aeda36374044bd4b297e66c6a6c34d2/revisions/rev_000001/model.py:L28-L151` | broad low cabinet, top rail, gasket, center track and top service opening layout |
| S5 | `rec_display_freezer_with_sliding_glass_lids_4aeda36374044bd4b297e66c6a6c34d2` | `data/records/rec_display_freezer_with_sliding_glass_lids_4aeda36374044bd4b297e66c6a6c34d2/revisions/rev_000001/model.py:L153-L367` | upper/lower framed glass lids, service hatch geometry, lid prismatic joints and hatch revolute joint |
| S6 | `rec_display_freezer_with_sliding_glass_lids_2ba0cc1a83c64ca5bf0086b5f1ffdbca` | `data/records/rec_display_freezer_with_sliding_glass_lids_2ba0cc1a83c64ca5bf0086b5f1ffdbca/revisions/rev_000001/model.py:L40-L128` | parameterizable lid helper with rails, glass insert, pull grip and prismatic slide |
| S7 | `rec_display_freezer_with_sliding_glass_lids_2ba0cc1a83c64ca5bf0086b5f1ffdbca` | `data/records/rec_display_freezer_with_sliding_glass_lids_2ba0cc1a83c64ca5bf0086b5f1ffdbca/revisions/rev_000001/model.py:L146-L445` | three-bay freezer body, lid rails, control wall, lock hardware, three lids and side lock flap hinge |
| S8 | `rec_display_freezer_with_sliding_glass_lids_84b667201ca04178883be8d5243aca46` | `data/records/rec_display_freezer_with_sliding_glass_lids_84b667201ca04178883be8d5243aca46/revisions/rev_000001/model.py:L25-L109` | curved transparent lid geometry and rounded hollow freezer body |
| S9 | `rec_display_freezer_with_sliding_glass_lids_84b667201ca04178883be8d5243aca46` | `data/records/rec_display_freezer_with_sliding_glass_lids_84b667201ca04178883be8d5243aca46/revisions/rev_000001/model.py:L123-L326` | two-level rails, end stops, control panel, curved lid parts, knob and lid / knob joints |
| S10 | `rec_display_freezer_with_sliding_glass_lids_dbfc4a989f6e4308b407b3d568b5128a` | `data/records/rec_display_freezer_with_sliding_glass_lids_dbfc4a989f6e4308b407b3d568b5128a/revisions/rev_000001/model.py:L35-L314` | compact deli cabinet, guide shelves, single sliding lid, thermostat dial revolute and fixed product baskets |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `cabinet` / `freezer_body` | 必需；低矮厚壁冷柜箱体，包含外壳、保温壁、内胆、顶面 rim、底座和可选 compressor / control wall | `cabinet_width`, `cabinet_depth`, `cabinet_height`, `wall_thickness`, `body_profile`, `bay_count` | S2 / `model.py:L222-L393`; S4 / `model.py:L28-L151`; S7 / `model.py:L146-L397`; S8 / `model.py:L90-L109`; S10 / `model.py:L35-L165` |
| `inner_liner` / `cold_well` | 必需 visual；由外壳尺寸和 wall thickness 派生的上开口冷藏腔 | `liner_depth`, `liner_floor_thickness`, `cavity_clearance` | S2 / `model.py:L222-L393`; S4 / `model.py:L28-L151`; S7 / `model.py:L146-L397`; S10 / `model.py:L35-L165` |
| `top_rail_system` | 必需；顶面前后 rails、中心轨、分层 runner、end stops 和 guide shelves | `rail_layout`, `rail_tier_count`, `rail_height`, `rail_clearance`, `end_stop_style` | S2 / `model.py:L222-L393`; S4 / `model.py:L28-L151`; S7 / `model.py:L146-L397`; S9 / `model.py:L123-L212`; S10 / `model.py:L35-L165` |
| `sliding_lid_i` | 必需；透明滑动玻璃盖，包含金属 / 塑料框、玻璃 pane、前后 cross rail、滑靴或 roller pads | `lid_count`, `lid_profile`, `lid_frame_thickness`, `glass_thickness`, `lid_overlap`, `lid_travel` | S1 / `model.py:L59-L126`; S3 / `model.py:L498-L548`; S5 / `model.py:L153-L367`; S6 / `model.py:L40-L128`; S8 / `model.py:L25-L87`; S9 / `model.py:L218-L326`; S10 / `model.py:L167-L225` |
| `pull_handle_i` / `grip` | 必需或条件必需；安装在滑盖前缘或侧缘，随 lid 运动 | `handle_style`, `handle_width`, `handle_offset` | S1 / `model.py:L59-L126`; S6 / `model.py:L40-L128`; S9 / `model.py:L269-L326`; S10 / `model.py:L167-L225` |
| `interior_storage_system` / `basket_i` / `bin_cell_i` | 常见且应随机化；内部 wire basket、可移食品篮、分隔格、瓶罐槽、商品托盘或多层展示格，必须由 liner 可用体积派生 | `interior_storage_layout`, `basket_count`, `storage_grid_cols`, `storage_grid_rows`, `storage_tier_count`, `divider_count`, `basket_style`, `product_fill` | S3 / `model.py:L395-L497`; S10 / `model.py:L262-L314` |
| `control_panel` / `thermostat` | optional；温控旋钮、面板、标签、通风格栅 | `control_style`, `dial_count`, `vent_style` | S7 / `model.py:L146-L397`; S9 / `model.py:L123-L212`; S10 / `model.py:L227-L259` |
| `service_hatch` / `lock_flap` | optional；检修小盖、锁扣翻片或侧锁 | `hatch_style`, `lock_flap_enabled` | S5 / `model.py:L286-L367`; S7 / `model.py:L405-L445` |
| `caster_i` / `foot_i` | optional；底部脚轮、脚垫或固定支脚 | `base_support_style`, `caster_count` | S1 / `model.py:L551-L585`; S10 / `model.py:L35-L165` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `lid_slide_i` | prismatic | `(1, 0, 0)` or `(-1, 0, 0)` | corresponding top rail centerline | `[0, lid_travel_i]` | 每块玻璃盖沿顶面 guide rail 水平滑开；左右 / 上下轨可用反向 axis 表达互滑 | S3 / `model.py:L498-L548`; S5 / `model.py:L342-L367`; S6 / `model.py:L40-L128`; S7 / `model.py:L405-L445`; S10 / `model.py:L167-L225` |
| `service_hatch_hinge` | revolute | `(1, 0, 0)` or `(0, 1, 0)` according to hatch edge | service hatch hinge edge on lid or top frame | `[0, 1.35]` | 检修小盖 / 加料小窗围绕自身铰链打开，optional | S5 / `model.py:L286-L367` |
| `lock_flap_hinge` | revolute | `(0, 0, 1)` or local latch hinge axis | side lock bracket edge | `[-0.45, 1.05]` | 侧面锁扣翻片或止挡翻转，optional | S7 / `model.py:L405-L445` |
| `thermostat_dial_joint` | revolute | `(0, 1, 0)` or panel normal axis | dial center on control panel | `[-2.8, 2.8]` | 温控旋钮绕面板法线旋转，optional | S10 / `model.py:L227-L259` |
| `caster_swivel_i` | continuous | `(0, 0, 1)` | caster fork vertical pin | unbounded | 可选万向脚轮绕竖直轴转向 | S1 / `model.py:L551-L585` |
| `caster_wheel_spin_i` | continuous | `(1, 0, 0)` or wheel axle axis | wheel axle center | unbounded | 可选脚轮滚动 | S1 / `model.py:L551-L585` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `body_profile` | enum | `flat_rectangular_chest` / `rounded_commercial_tub` / `compact_deli_counter` / `three_bay_island` | `flat_rectangular_chest` | 决定 cabinet proportions、corner style、control wall 默认位置 | S2 / `model.py:L222-L393`; S4 / `model.py:L28-L151`; S7 / `model.py:L146-L397`; S8 / `model.py:L90-L109`; S10 / `model.py:L35-L165` |
| `cabinet_width` | float | `1.0-3.0` | `1.65` | 先采外壳宽度，再派生 bay width、lid span、rail length | S2 / `model.py:L222-L393`; S4 / `model.py:L28-L151`; S7 / `model.py:L146-L397`; S10 / `model.py:L35-L165` |
| `cabinet_depth` | float | `0.55-1.2` | `0.78` | 派生 front/back rail y、lid depth、basket depth | S2 / `model.py:L222-L393`; S4 / `model.py:L28-L151`; S9 / `model.py:L123-L212`; S10 / `model.py:L35-L165` |
| `cabinet_height` | float | `0.55-1.15` | `0.82` | 派生 liner height、control panel z、caster clearance | S2 / `model.py:L222-L393`; S4 / `model.py:L28-L151`; S8 / `model.py:L90-L109`; S10 / `model.py:L35-L165` |
| `wall_thickness` | float | `0.035-0.09` | `0.055` | liner opening = cabinet envelope minus wall and rim thickness | S2 / `model.py:L222-L393`; S4 / `model.py:L28-L151`; S7 / `model.py:L146-L397` |
| `bay_count` | int | `1 / 2 / 3` | `2` | `bay_width = (cabinet_width - side_walls - center_tracks) / bay_count` | S2 / `model.py:L222-L393`; S7 / `model.py:L146-L397`; S10 / `model.py:L35-L165` |
| `lid_layout` | enum | `two_overlapping_flat` / `single_deli_slider` / `three_independent_bays` / `curved_barrel_pair` / `upper_lower_tier` | `two_overlapping_flat` | 决定 `lid_count`, rail tiers, lid profile and travel direction | S1 / `model.py:L59-L126`; S5 / `model.py:L153-L367`; S6 / `model.py:L40-L128`; S8 / `model.py:L25-L87`; S10 / `model.py:L167-L225` |
| `lid_count` | int | `1-3` | `2` | 由 `lid_layout` 与 `bay_count` 合法化；three bay layout uses 3 | S3 / `model.py:L498-L548`; S7 / `model.py:L405-L445`; S10 / `model.py:L167-L225` |
| `lid_profile` | enum | `flat_framed_glass` / `curved_barrel_glass` / `raised_service_hatch` | `flat_framed_glass` | 决定 glass mesh and frame rails | S1 / `model.py:L59-L126`; S5 / `model.py:L153-L367`; S8 / `model.py:L25-L87`; S9 / `model.py:L218-L267` |
| `rail_layout` | enum | `parallel_front_back` / `center_spine_two_tier` / `three_bay_tracks` / `guide_shelves` | `center_spine_two_tier` | 与 `lid_layout` 匹配，派生 rail z offsets and clearances | S2 / `model.py:L222-L393`; S4 / `model.py:L28-L151`; S7 / `model.py:L146-L397`; S9 / `model.py:L123-L212`; S10 / `model.py:L35-L165` |
| `lid_overlap` | float | `0.08-0.28` | `0.14` | closed pose 中相邻 lid 与 rim 必须保持 overlap | S1 / `model.py:L59-L126`; S3 / `model.py:L498-L548`; S5 / `model.py:L153-L367` |
| `lid_travel` | float | `0.18-0.75` | `0.42` | `min(max_opening_clearance, lid_span - retained_overlap)` | S3 / `model.py:L498-L548`; S5 / `model.py:L342-L367`; S7 / `model.py:L405-L445`; S10 / `model.py:L167-L225` |
| `handle_style` | enum | `front_bar` / `edge_pull` / `recessed_grip` / `round_knob` | `edge_pull` | round knob only for curved / service variants | S1 / `model.py:L59-L126`; S6 / `model.py:L40-L128`; S9 / `model.py:L269-L326`; S10 / `model.py:L167-L225` |
| `interior_storage_layout` | enum | `empty_open_well` / `wire_basket_array` / `removable_bin_grid` / `product_tray_rows` / `multi_tier_display_shelf` / `bay_divider_grid` | `wire_basket_array` | 先由 liner 可用宽深高和 `bay_count` 合法化，再决定内部格子拓扑 | S3 / `model.py:L395-L497`; S10 / `model.py:L262-L314` |
| `basket_style` | enum | `none` / `wire_hanging_basket` / `solid_plastic_bin` / `shallow_product_tray` / `bottle_channel` | `wire_hanging_basket` | 由 `interior_storage_layout` 派生；改变 rim、floor、post、product load 几何 | S3 / `model.py:L395-L497`; S10 / `model.py:L262-L314` |
| `basket_count` | int | `0-8` | `2` | `basket_count <= storage_grid_cols * storage_grid_rows * storage_tier_count`，并由 liner footprint / min basket size 夹紧 | S3 / `model.py:L395-L497`; S10 / `model.py:L262-L314` |
| `storage_grid_cols` | int | `1-4` | `2` | `floor((liner_width - 2 * storage_margin + gap) / min_cell_width)`，再受 `bay_count` 和 rail dividers 约束 | S3 / `model.py:L395-L497`; S10 / `model.py:L262-L314` |
| `storage_grid_rows` | int | `1-3` | `1` | `floor((liner_depth - 2 * storage_margin + gap) / min_cell_depth)`，product tray rows 通常用 2-3 | S3 / `model.py:L395-L497`; S10 / `model.py:L262-L314` |
| `storage_tier_count` | int | `1-2` | `1` | 由 `liner_height`, `min_clearance_under_lid`, `min_basket_height` 决定，多层 shelf 必须低于 sliding lid closed plane | S3 / `model.py:L395-L497`; S10 / `model.py:L262-L314` |
| `divider_count` | int | `0-6` | `2` | `vertical_dividers = max(storage_grid_cols - 1, bay_count - 1)`，row dividers 由 `storage_grid_rows` 派生 | S3 / `model.py:L395-L497`; S10 / `model.py:L262-L314` |
| `storage_margin` | float | `0.025-0.075` | `0.045` | liner 内壁到 basket/bin 外缘的安全距离 | S3 / `model.py:L395-L497`; S10 / `model.py:L262-L314` |
| `storage_gap` | float | `0.015-0.055` | `0.028` | 相邻 basket/bin/divider 之间的间隙；参与 cell size 公式 | S3 / `model.py:L395-L497`; S10 / `model.py:L262-L314` |
| `control_style` | enum | `none` / `front_panel` / `side_panel_with_dial` / `rear_service_wall` | `front_panel` | optional control visuals and thermostat joint | S7 / `model.py:L146-L397`; S9 / `model.py:L123-L212`; S10 / `model.py:L227-L259` |
| `base_support_style` | enum | `feet` / `casters` / `skid_base` | `feet` | casters add swivel/wheel continuous joints | S1 / `model.py:L551-L585`; S10 / `model.py:L35-L165` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| cabinet / body | rectangular chest / rounded commercial tub / compact deli counter / three-bay island | no | yes | `body_profile` | 外壳比例、角部、控制墙和 bay topology 差异明显，不能只靠宽深高表达 |
| cold well / liner | single open tub / divided bays / compact product shelf well | no | yes | `bay_count`, `interior_storage_layout` | 内部空间分舱影响 lid、rail 和 storage grid derivation |
| rail system | front-back rails / center two-tier rail / three-bay tracks / guide shelves | no | yes | `rail_layout`, `rail_tier_count` | rail 是滑动关节语义的主约束基准 |
| sliding lid | flat framed glass / curved barrel glass / raised hatch lid / single deli slider | no | yes | `lid_layout`, `lid_profile` | 盖板轮廓、数量、层级和 joint chain 不同 |
| pull handle | edge pull / front bar / round knob / recessed grip | no | yes | `handle_style` | handle 随 lid 运动，外形差异影响定位 |
| basket / product insert / storage cells | wire hanging basket / removable bin grid / shallow product trays / bottle rows / empty well | no | yes | `interior_storage_layout`, `basket_style`, `storage_grid_cols`, `storage_grid_rows`, `storage_tier_count` | 内部格子种类和数量不是装饰，必须像抽屉柜一样由内胆 envelope、margin、gap、最小单格尺寸派生 |
| control / thermostat | front control panel / side dial / rear service wall / none | no | yes | `control_style` | control 位置和可动 dial 语义不同 |
| caster / feet | caster assembly / simple feet / skid base | no | yes | `base_support_style` | caster 会引入连续 wheel/swivel joints；feet 只需 visual |

## 组合逻辑（Composition Logic）
1. 先采 `cabinet_width`, `cabinet_depth`, `cabinet_height` 和 `body_profile`，把 freezer_body 作为唯一 envelope 基准。
2. 由 `wall_thickness`, `rim_height`, `rail_height` 派生 inner liner 尺寸，保证 `liner_width = cabinet_width - 2 * wall_thickness`，`liner_depth = cabinet_depth - 2 * wall_thickness`，`liner_height < cabinet_height - rail_stack_height`。
3. 由 `bay_count` 和 `rail_layout` 派生 center tracks、bay dividers、guide shelf z offsets；禁止 lid / rail 单独随机位置。
4. 再采 `interior_storage_layout`，但必须先用 liner 可用空间合法化：`usable_w = liner_width - 2 * storage_margin`，`usable_d = liner_depth - 2 * storage_margin`，`usable_h = liner_height - bottom_clearance - lid_under_clearance`。
5. 依据 `interior_storage_layout` 和可用空间采样格子数量：`storage_grid_cols <= floor((usable_w + storage_gap) / (min_cell_width + storage_gap))`，`storage_grid_rows <= floor((usable_d + storage_gap) / (min_cell_depth + storage_gap))`，`storage_tier_count <= floor((usable_h + vertical_gap) / (min_cell_height + vertical_gap))`。
6. 单个 basket/bin/tray 尺寸由格子数派生：`cell_width = (usable_w - (storage_grid_cols - 1) * storage_gap) / storage_grid_cols`，`cell_depth = (usable_d - (storage_grid_rows - 1) * storage_gap) / storage_grid_rows`，`cell_height = (usable_h - (storage_tier_count - 1) * vertical_gap) / storage_tier_count`；禁止单个格子独立随机宽深高。
7. `wire_basket_array` 需要 hanger rails / rim / corner posts / wire floor；`removable_bin_grid` 需要 solid side walls；`product_tray_rows` 需要 shallow tray lips 和商品 rows；`bay_divider_grid` 需要 dividers 与 `bay_count` / center tracks 对齐。
8. 所有 storage cells 的 origin 从 liner inner corner、grid index、cell size、gap 派生，必须低于 lid closed plane，并保留 lid underside clearance；basket 可以 fixed 到 cabinet，但不能漂浮。
9. 由 rail centerline 派生每个 `sliding_lid_i` 的 closed origin、glass frame outer size、sliding shoe y/z 位置和 `lid_slide_i` joint origin。
10. `lid_travel_i` 从 rail length、lid length、retained overlap、end stop clearance 计算：打开到最大行程时，lid shoe 仍在 rail 上，玻璃盖仍有 `retained_overlap`。
11. `curved_barrel_pair` 使用 curved lid profile，但 joint 仍是沿 rail 的 prismatic；曲面只改变 lid visual，不改变运动语义。
12. thermostat dial、service hatch、lock flap、caster 只在对应 style 启用时创建独立 part 和 joint；普通 labels、vents、gaskets、screws 用 parent visual。
13. 所有活动件的 parent 必须是 body 或 lid 上的真实承载件；handle 必须随 lid part 运动，不得挂在 cabinet 上。
14. `resolve_config` 必须执行 body/lid/rail/storage 兼容矩阵：`compact_deli_counter` 只允许 `single_deli_slider` 或 `two_overlapping_flat`，并优先 `product_tray_rows` / `removable_bin_grid`；`three_bay_island` 只允许 `three_independent_bays` + `three_bay_tracks` + `bay_divider_grid`；`rounded_commercial_tub` 优先 `curved_barrel_pair` / `center_spine_two_tier` / `wire_basket_array`；`flat_rectangular_chest` 优先 `two_overlapping_flat` / `center_spine_two_tier` / `wire_basket_array`。
15. service hatch、lock flap、caster、thermostat dial 是 optional helper variants，不得因为某个 5 星样本出现就强制每个配置都生成。

## 已有模板写法参考
prismatic_slide / guide_shoe / gasket_strip / handle_grip / latch_lock / caster_wheel / continuous_wheel

## 约束
- 必须是低矮 top-opening display freezer，不得变成立式冰箱、普通柜子或无导轨玻璃箱。
- 每个 sliding lid 必须有 guide rail / shoe / end stop 的物理语义，closed pose 覆盖上开口，open pose 保留 rail overlap。
- lid 的透明 glass pane 必须嵌在 frame 内，不得漂浮在轨道上方。
- interior storage 的 layout、格子数量、basket/bin/tray 尺寸必须由 liner 可用宽深高、margin、gap、最小单格尺寸派生，并位于冷藏腔内。
- `storage_grid_cols`, `storage_grid_rows`, `storage_tier_count`, `basket_count`, `divider_count` 必须互相一致；不能采样出比 liner 容量更多的格子。
- `lid_count`、`bay_count`、`rail_layout` 必须互相合法化；three-bay layout 不允许只生成两个随机 lid。
- service hatch、lock flap、thermostat dial、caster 若出现，必须有正确父子关系和 joint axis。
- 导轨、center spine、end stops 必须从 cabinet envelope 派生，不能单独随机导致穿模或错位。
- `body_profile`, `lid_layout`, `rail_layout`, `interior_storage_layout` 必须通过兼容矩阵合法化；非法组合应在 `resolve_config` 中降级到同族稳定组合。
- 被采纳 5 星源码片段必须落到具体 helper / variant；不能映射到当前兼容矩阵的样本不得硬塞进默认 seed domain。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | 有 low insulated cabinet、top open liner、rail system、transparent framed sliding lid |
| lid joint count | `lid_count` 个 `lid_slide_i` prismatic joints，axis 沿 rail centerline |
| lid retained overlap | max travel 时 sliding shoe 仍在 guide rail 上，lid 与 opening 保持最小 overlap |
| closed coverage | closed pose 中 lid frame 覆盖 top opening，glass 位于 rim 上方 |
| liner clearance | storage cells / baskets / products 不穿过 lid closed plane、wall、rail 或 center dividers |
| storage derivation | each basket/bin/tray cell size equals formula from liner usable dimensions, grid counts, margins and gaps |
| storage count consistency | `basket_count <= storage_grid_cols * storage_grid_rows * storage_tier_count` and dividers match grid/bay layout |
| rail consistency | `rail_layout` 与 `lid_layout` 匹配，rail z tiers 与 lid shoe z 相等或小容差 |
| optional joints | thermostat / service hatch / lock flap / caster 启用时有对应 joint type、axis、range |
| part diversity | `body_profile`, `lid_layout`, `lid_profile`, `rail_layout`, `handle_style`, `interior_storage_layout`, `basket_style` 均存在并驱动几何分支 |
| compatibility matrix | body/lid/rail/storage combinations are legal or degraded by `resolve_config` before build |
| no floating | lid、handle、rails、baskets、controls、casters 均连接到 cabinet 或活动父件 |

## Reject cases
- 只有透明板没有滑轨，或者滑盖没有 prismatic joint。
- 玻璃盖和导轨错层，closed pose 悬空或插进内胆。
- 滑盖打开时完全脱离轨道或穿出 end stop。
- cabinet 没有厚壁、rim 或 inner liner，看起来像普通盒子。
- handle 挂在 cabinet 上，lid 运动时不随滑盖移动。
- basket / product rows 漂浮在冷柜上方、穿过玻璃盖，或数量超过 liner 能容纳的 grid 容量。
- 内部格子尺寸独立随机，没有从 liner usable width/depth/height、margin、gap 和 count 公式派生。
- 为了覆盖某个 5 星样本，把 service hatch、caster、three-bay rails、curved lid 和 compact deli storage 同时塞进一个不兼容配置。
- 三舱 / 双层轨布局的 lid 数、bay 数和 rail 数互相不一致。
- thermostat、service hatch、lock flap 的 joint axis 随机，不能表达真实旋钮 / 小盖 / 锁扣运动。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review. 未进入模板实现阶段。 |
