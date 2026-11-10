# Desktop Pc Tower Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `desktop_pc_tower` |
| template path | `agent/templates/desktop_pc_tower.py` |
| test path | `tests/agent/test_desktop_pc_tower_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 27 |
| read_count | 27 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
桌面 PC 机箱/塔式主机，至少包含矩形 chassis、可访问的侧板或前/顶门、通风/前面板细节、内部托架或驱动位。核心活动方式是侧板/门/顶盖绕边缘铰链打开，或光驱/硬盘托盘沿导轨滑出。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_desktop_pc_tower_0004` | `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L21-L52` | full-tower chassis and tray dimension constants |
| S2 | `rec_desktop_pc_tower_0004` | `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L70-L309` | rectangular chassis shell, front fascia, internal visible computer details, feet |
| S3 | `rec_desktop_pc_tower_0004` | `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L311-L367` | hinged tempered-glass side panel with frame, handle, hinge barrels |
| S4 | `rec_desktop_pc_tower_0004` | `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L368-L440` | dual optical trays and side-panel/tray articulation definitions |
| S5 | `rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c` | `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L34-L97` | NAS tower shell, front drive bay rails, vents, status lights, hinge knuckles |
| S6 | `rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c` | `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L98-L142` | front door and multiple hot-swap tray drawer joints |
| S7 | `rec_desktop_pc_tower_3acf5926bb9b4657b642451b6c237f6f` | `data/records/rec_desktop_pc_tower_3acf5926bb9b4657b642451b6c237f6f/revisions/rev_000001/model.py:L180-L299` | swing-out drive cage and hinged top exhaust cover |
| S8 | `rec_desktop_pc_tower_42f2ff19b3f346b0b72b16faae6ef3cb` | `data/records/rec_desktop_pc_tower_42f2ff19b3f346b0b72b16faae6ef3cb/revisions/rev_000001/model.py:L152-L271` | SFF sliding top panel, slide rails, top panel prismatic joint |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `chassis` | 主机箱骨架，包含墙板、前面板、后墙、脚垫、通风或内部硬件 visual | `case_form`, `case_width`, `case_depth`, `case_height`, `vent_style` | S1 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L21-L52`; S2 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L70-L309`; S5 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L34-L97` |
| `side_panel` | 侧面可开合访问面板，可为钢板或玻璃门 | `side_panel_style`, `side_panel_hinge_side`, `has_side_panel` | S3 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L311-L367` |
| `front_door` | 前部访问门、mesh door、NAS smoked door 或 retro bezel，optional | `front_access_style`, `front_hinge_side` | S6 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L98-L117` |
| `drive_tray_i` | 光驱托盘或 NAS hot-swap drive drawer，optional multiple | `front_bay_layout`, `drive_tray_count`, `tray_travel` | S4 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L368-L440`; S6 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L119-L142` |
| `top_panel` | 可铰接或滑动的顶盖/滤网，optional | `top_access_style`, `top_panel_travel` | S7 / `data/records/rec_desktop_pc_tower_3acf5926bb9b4657b642451b6c237f6f/revisions/rev_000001/model.py:L228-L299`; S8 / `data/records/rec_desktop_pc_tower_42f2ff19b3f346b0b72b16faae6ef3cb/revisions/rev_000001/model.py:L152-L271` |
| `drive_cage` | 可摆出的内部硬盘架，optional | `drive_cage_style`, `drive_cage_count` | S7 / `data/records/rec_desktop_pc_tower_3acf5926bb9b4657b642451b6c237f6f/revisions/rev_000001/model.py:L180-L284` |
| `front_io` | 电源按钮、USB/LED、状态灯等，通常作为 chassis visual | `io_style`, `status_light_count` | S2 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L277-L289`; S5 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L70-L90` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `side_panel_hinge` | revolute | `(0, 0, 1)` | rear vertical edge of side opening | `[0, 1.1-1.35]` rad | 侧板绕竖直后缘打开 | S4 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L414-L422` |
| `front_door_hinge` | revolute | `(0, 0, 1)` or `(0, 0, -1)` | front vertical stile | `[0, 1.2-1.75]` rad | 前门/drive-bay 门向外打开 | S6 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L109-L117` |
| `drive_tray_slide_i` | prismatic | `(0, 1, 0)` or `(0, -1, 0)` | front bay opening center | `[0, tray_travel]` | 光驱或硬盘托盘沿机箱深度方向抽出 | S4 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L423-L440`; S6 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L134-L142` |
| `top_panel_hinge` | revolute | `(1, 0, 0)` or `(0, 1, 0)` | rear/front top edge | `[0, 1.2]` rad | 顶盖或滤网翻开，optional | S7 / `data/records/rec_desktop_pc_tower_3acf5926bb9b4657b642451b6c237f6f/revisions/rev_000001/model.py:L228-L299` |
| `top_panel_slide` | prismatic | `(0, 1, 0)` | top rail start | `[0, top_panel_travel]` | SFF/HTPC 顶盖滑开，optional | S8 / `data/records/rec_desktop_pc_tower_42f2ff19b3f346b0b72b16faae6ef3cb/revisions/rev_000001/model.py:L219-L271` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `case_form` | enum | `mid_tower` / `full_tower` / `mini_itx_cube` / `sff_htpc` / `rackmount_tower` / `nas_tower` / `open_frame` | `mid_tower` | drives aspect ratio and available access parts | S1 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L21-L52`; S5 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L34-L97` |
| `access_layout` | enum | `side_hinged` / `front_hinged` / `side_and_front` / `top_hinged` / `top_sliding` / `multi_panel` | `side_hinged` | selects active panels and joint set | S3 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L311-L367`; S6 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L98-L117` |
| `front_bay_layout` | enum | `none` / `single_optical` / `dual_optical` / `hot_swap_stack` / `mesh_door` / `solid_bezel` | `dual_optical` | controls tray count and front fascia openings | S4 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L368-L440`; S6 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L119-L142` |
| `side_panel_style` | enum | `solid_steel` / `tempered_glass` / `framed_glass` / `open_frame` | `framed_glass` | affects side panel visuals and transparency | S3 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L311-L367` |
| `vent_style` | enum | `front_mesh` / `vertical_slots` / `side_ribs` / `top_filter` / `minimal` | `front_mesh` | adds chassis visual details | S2 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L155-L289`; S5 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L70-L90` |
| `case_height` | float | `0.22-0.95` | `0.56` | paired with `case_form`; NAS/full tower taller | S1 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L21-L52`; S5 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L34-L47` |
| `case_width` | float | `0.20-0.55` | `0.24` | rackmount/HTPC wider and shorter | S1 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L21-L52` |
| `drive_tray_count` | int | `0-6` | `2` | `hot_swap_stack` defaults to 4-5; optical defaults 1-2 | S4 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L368-L440`; S6 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L15-L19` |
| `tray_travel` | float | `0.10-0.24` | `0.13` | clamped to tray body depth and guide rail overlap | S4 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L41-L52`; S6 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L15-L19` |
| `io_style` | enum | `power_button_only` / `top_io_cluster` / `status_light_strip` / `gaming_rgb` | `top_io_cluster` | adds chassis visuals only unless reviewed as controls | S2 / `data/records/rec_desktop_pc_tower_0004/revisions/rev_000001/model.py:L277-L289`; S5 / `data/records/rec_desktop_pc_tower_4ddce61273ad4811871440cad5d8c65c/revisions/rev_000001/model.py:L78-L90` |
| `top_access_style` | enum | `none` / `hinged_filter` / `sliding_lid` | `none` | selects `top_panel_hinge` or `top_panel_slide` | S7 / `data/records/rec_desktop_pc_tower_3acf5926bb9b4657b642451b6c237f6f/revisions/rev_000001/model.py:L228-L299`; S8 / `data/records/rec_desktop_pc_tower_42f2ff19b3f346b0b72b16faae6ef3cb/revisions/rev_000001/model.py:L219-L271` |
| `drive_cage_style` | enum | `none` / `swing_out_shelves` | `none` | if enabled, add internal hinged drive cage | S7 / `data/records/rec_desktop_pc_tower_3acf5926bb9b4657b642451b6c237f6f/revisions/rev_000001/model.py:L180-L284` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| chassis | tower / cube / low HTPC / rackmount / NAS / open-frame | no | yes | `case_form` | 机箱比例和拓扑差异明显 |
| access panel | side hinged / front hinged / top hinged / top sliding / multi-panel | no | yes | `access_layout` | joint 类型、axis 和 origin 均不同 |
| side panel | solid steel / tempered glass / framed glass / open frame | no | yes | `side_panel_style` | 透明侧板和实心钢板不是颜色差异 |
| front bay | optical tray / NAS hot-swap drawer stack / mesh door / solid bezel | no | yes | `front_bay_layout` | 前部功能件的数量和运动方式不同 |
| ventilation | mesh / slots / side ribs / top filter / minimal | no | yes | `vent_style` | 通风几何决定 PC 机箱可读性 |
| feet | none / four feet | yes | no | `foot_height`, `foot_count` | 观察到主要是尺寸和数量，可连续/整数表达 |
| internal detail | motherboard tray / GPU / PSU shroud / status LEDs | no | yes | `io_style`, `internal_detail_level` | 对玻璃侧板样本很重要，但不一定活动 |

## 组合逻辑（Composition Logic）
1. 根据 `case_form` 设定 chassis envelope；tower/NAS 竖高，HTPC/rackmount 低宽，open-frame 减少墙板改用 rails。
2. 创建 chassis 墙板、前框、后墙、脚垫、通风、I/O 和内部视觉件；这些通常是 `chassis.visual(...)`。
3. 根据 `access_layout` 添加 side/front/top panel part；每个活动面板都独立 part 并有 hinge 或 slide joint。
4. 根据 `front_bay_layout` 添加光驱托盘或 hot-swap trays；每个 tray 独立 part，沿机箱深度方向 prismatic。
5. 若有玻璃侧板，内部 motherboard tray、GPU、PSU shroud 至少有简化 visual，使透明面板有内容可读。
6. Front door 与 tray 可以共存；door 在外侧，tray 在 chassis bay 内，二者不得共享同一 child part。

## 已有模板写法参考
revolute_hinge / prismatic_slide / latch_lock / guide_shoe / button_slider

## 约束
- chassis 必须是可辨识的 PC enclosure，不能只有一个空盒。
- 至少一个活动 access panel 或 tray 必须存在。
- 竖直侧门和前门 hinge axis 必须为 Z 方向。
- tray slide axis 必须沿机箱深度方向，且打开后仍与 guide rail overlap。
- 玻璃侧板的 hinge barrels/handle 必须跟随 side_panel 移动。
- front bay opening 与 tray count 必须匹配。
- `case_form=nas_tower` 时必须有多层 drive bay 或 hot-swap tray stack。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | chassis + access panel/tray + front/vent/io details present |
| joint count | 至少 1 个 revolute 或 prismatic access joint |
| side/front hinge axis | vertical door axes are `(0, 0, ±1)` |
| tray axis | tray slide axis along depth `(0, ±1, 0)` |
| tray retained overlap | tray at max travel still overlaps guide rails |
| access layout consistency | active parts match `access_layout` and `front_bay_layout` |
| glass side detail | transparent side panel variants include visible internal hardware |
| part diversity | `case_form`, `access_layout`, `front_bay_layout`, `side_panel_style`, `vent_style` exist and drive geometry |
| no floating | hinge barrels, handles, vents, trays, feet connected to main tree |

## Reject cases
- 看起来像普通柜子，没有 PC 前面板、I/O、通风或内部硬件线索。
- 没有任何可动侧板、门、顶盖或托盘。
- 侧门 hinge 放在面板中心或 axis 不是竖直。
- 光驱/NAS tray 滑出方向横向错误。
- 托盘打开后完全脱离机箱导轨。
- front bay 参数要求多托盘但只生成一个静态面板。
- 玻璃侧板后面空无一物，失去 PC 机箱身份。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
