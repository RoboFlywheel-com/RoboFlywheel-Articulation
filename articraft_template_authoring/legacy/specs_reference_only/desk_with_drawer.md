# Desk With Drawer Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `desk_with_drawer` |
| template path | `agent/templates/desk_with_drawer.py` |
| test path | `tests/agent/test_desk_with_drawer_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 70 |
| read_count | 70 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
带抽屉的书桌/工作桌，至少包含可用桌面、落地支撑结构、一个或多个前向抽屉，以及抽屉沿导轨直线滑出的 prismatic 关节。可选形态包括 pedestal desk、L 形桌、秘书桌 drop-front、升降桌、梳妆桌镜子、键盘托盘或折叠/倾斜桌面。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e` | `data/records/rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e/revisions/rev_000001/model.py:L17-L39` | simple writing desk top, four legs, aprons, drawer runners |
| S2 | `rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e` | `data/records/rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e/revisions/rev_000001/model.py:L41-L77` | single hollow drawer, front panel, handle, prismatic drawer pull |
| S3 | `rec_desk_with_drawer_0004` | `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L85-L161` | double pedestal carcass with separators and rail pairs |
| S4 | `rec_desk_with_drawer_0004` | `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L164-L251` | reusable drawer box with face, side walls, rails, pull hardware |
| S5 | `rec_desk_with_drawer_0004` | `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L263-L340` | desktop, left/right pedestals, fixed mounting, six prismatic drawer joints |
| S6 | `rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241` | `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L132-L337` | L-shaped standing desk profile, telescoping columns, height prismatic joint |
| S7 | `rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241` | `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L339-L458` | under-top drawer housing, drawer box, pull, drawer prismatic joint |
| S8 | `rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d` | `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L119-L280` | secretary desk body, legs, case, cubbies, rails |
| S9 | `rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d` | `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L282-L379` | drop-front leaf, pull-out writing shelf, stacked drawers, revolute/prismatic joints |
| S10 | `rec_desk_with_drawer_9b15398564334344b74629c6e92edb81` | `data/records/rec_desk_with_drawer_9b15398564334344b74629c6e92edb81/revisions/rev_000001/model.py:L124-L239` | drafting desk tilting top, drawer, top hinge, drawer slide |
| S11 | `rec_desk_with_drawer_86da86bf045e4e9f8dbdfd8c45a1fdd6` | `data/records/rec_desk_with_drawer_86da86bf045e4e9f8dbdfd8c45a1fdd6/revisions/rev_000001/model.py:L188-L244` | vanity mirror frame, mirror glass, side-post hinge joint |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `desktop` / `desk_top` | 主工作面，可为矩形、L 形、折叠 leaf 或倾斜 top | `desktop_profile`, `desk_width`, `desk_depth`, `top_thickness` | S1 / `data/records/rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e/revisions/rev_000001/model.py:L17-L39`; S5 / `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L263-L274`; S6 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L132-L337`; S9 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L282-L335` |
| `support` | 四腿、pedestal panels、trestle、wall brackets 或 telescoping columns | `support_style`, `leg_count`, `pedestal_count`, `height_adjustable` | S1 / `data/records/rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e/revisions/rev_000001/model.py:L17-L39`; S3 / `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L85-L161`; S6 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L153-L337`; S8 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L119-L280` |
| `drawer_housing` / `pedestal` | 抽屉所在的 apron bay、side pedestal、double pedestal 或 under-top housing | `drawer_layout`, `drawer_stack_count`, `drawer_columns`, `drawer_bay_height` | S1 / `data/records/rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e/revisions/rev_000001/model.py:L33-L39`; S3 / `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L85-L161`; S7 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L339-L400`; S8 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L223-L280` |
| `drawer_i` | 可滑动抽屉，包含箱体、front face、rails 和 pull | `drawer_count`, `drawer_width`, `drawer_depth`, `drawer_height`, `handle_style` | S2 / `data/records/rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e/revisions/rev_000001/model.py:L41-L77`; S4 / `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L164-L251`; S7 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L402-L458`; S9 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L316-L379` |
| `keyboard_tray` / `pull_out_shelf` | 键盘托盘或 secretary 内部写字板，optional | `has_keyboard_tray`, `shelf_travel`, `shelf_width` | S9 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L313-L349` |
| `drop_leaf` | secretary/Murphy/fold-down variant 的翻下写字面，optional | `has_drop_leaf`, `leaf_width`, `leaf_height`, `leaf_open_angle` | S9 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L282-L335` |
| `height_columns` | standing desk 的伸缩立柱，optional | `height_travel`, `column_count`, `column_profile` | S6 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L153-L337` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `drawer_slide_i` | prismatic | `(0, -1, 0)` or `(0, 1, 0)` | drawer bay front / housing origin | `[0, drawer_travel]` | 抽屉沿前后方向滑出 | S2 / `data/records/rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e/revisions/rev_000001/model.py:L68-L77`; S5 / `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L313-L340`; S7 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L445-L458`; S9 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L350-L379` |
| `height_adjust_joint` | prismatic | `(0, 0, 1)` | telescoping column center | `[0, height_travel]` | standing desk top assembly 升降，optional | S6 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L324-L337` |
| `drop_leaf_joint` | revolute | `(-1, 0, 0)` or `(1, 0, 0)` | front lower cabinet edge | `[0, pi/2]` | secretary/fold-down leaf 向下打开为写字面 | S9 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L322-L335` |
| `shelf_slide_joint` | prismatic | `(0, 1, 0)` or `(0, -1, 0)` | under-top shelf runners | `[0, shelf_travel]` | 键盘托盘或内部写字板抽出，optional | S9 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L336-L349` |
| `tilt_top_joint` | revolute | `(1, 0, 0)` | rear/top support beam | `[0, 0.95]` rad | drafting/over-bed variants 的桌面倾斜，optional | S10 / `data/records/rec_desk_with_drawer_9b15398564334344b74629c6e92edb81/revisions/rev_000001/model.py:L209-L222` |
| `mirror_or_door_joint` | revolute | `(1, 0, 0)` or `(0, 0, 1)` | mirror side posts or cabinet door edge | `[0, 1.2]` rad typical | vanity mirror, hutch door, cable flap 等 optional | S11 / `data/records/rec_desk_with_drawer_86da86bf045e4e9f8dbdfd8c45a1fdd6/revisions/rev_000001/model.py:L233-L244` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `desk_layout` | enum | `writing_single_drawer` / `side_pedestal` / `double_pedestal` / `l_corner` / `secretary_dropfront` / `standing_l` / `vanity` / `drafting` / `wall_mount` / `partners` / `card_catalog` | `writing_single_drawer` | drives `desktop_profile`, support, optional joints | S1 / `data/records/rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e/revisions/rev_000001/model.py:L17-L77`; S5 / `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L263-L340`; S6 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L132-L337`; S9 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L282-L379` |
| `desktop_profile` | enum | `rectangular` / `l_shaped` / `fold_down_leaf` / `tilting_top` / `wall_fold_down` | `rectangular` | set by layout unless explicitly overridden | S1 / `data/records/rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e/revisions/rev_000001/model.py:L17-L20`; S6 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L132-L337`; S9 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L282-L335` |
| `support_style` | enum | `four_legs` / `single_pedestal` / `double_pedestal` / `trestle` / `wall_brackets` / `telescoping_columns` / `c_base` | `four_legs` | derives part count and height joint availability | S1 / `data/records/rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e/revisions/rev_000001/model.py:L17-L39`; S3 / `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L85-L161`; S6 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L153-L337`; S8 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L119-L280` |
| `drawer_layout` | enum | `center_single` / `side_stack` / `double_stack` / `apron_three` / `card_catalog_grid` / `keyboard_tray_plus_drawer` | `center_single` | derives `drawer_count`, columns, z placement | S2 / `data/records/rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e/revisions/rev_000001/model.py:L41-L77`; S5 / `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L313-L340`; S7 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L339-L458` |
| `handle_style` | enum | `bar_pull` / `knob_pair` / `recessed_oval` / `finger_slot` / `none` | `bar_pull` | controls drawer front hardware | S2 / `data/records/rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e/revisions/rev_000001/model.py:L62-L66`; S4 / `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L226-L243`; S7 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L427-L438`; S9 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L295-L305` |
| `drawer_count` | int | `1-12` | `1` | derived from `drawer_layout`; card catalog may use 12 | S5 / `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L313-L340`; S7 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L402-L458` |
| `drawer_travel` | float | `0.12-0.35` | `0.22` | clamped by drawer depth and rail retained overlap | S2 / `data/records/rec_desk_with_drawer_04cc1a88d9734b57abdeb511f0e2867e/revisions/rev_000001/model.py:L68-L77`; S5 / `data/records/rec_desk_with_drawer_0004/revisions/rev_000001/model.py:L323-L338`; S7 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L445-L458` |
| `has_drop_leaf` | bool | `true` / `false` | `false` | true for `secretary_dropfront`, `wall_mount`, sewing/fold-down layouts | S9 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L282-L335` |
| `height_travel` | float | `0.0-0.35` | `0.0` | if >0, support_style must include telescoping columns | S6 / `data/records/rec_desk_with_drawer_9de29f90c01342db9f24b8b83ec61241/revisions/rev_000001/model.py:L324-L337` |
| `has_keyboard_tray` | bool | `true` / `false` | `false` | adds `shelf_slide_joint` under top | S9 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L313-L349` |
| `optional_feature` | enum | `none` / `keyboard_tray` / `drop_leaf` / `tilt_top` / `vanity_mirror` | `none` | `tilt_top` adds `tilt_top_joint`; `vanity_mirror` adds `mirror_or_door_joint` | S9 / `data/records/rec_desk_with_drawer_5365c5dc19f442b59e3d4049e8c6866d/revisions/rev_000001/model.py:L282-L349`; S10 / `data/records/rec_desk_with_drawer_9b15398564334344b74629c6e92edb81/revisions/rev_000001/model.py:L124-L239`; S11 / `data/records/rec_desk_with_drawer_86da86bf045e4e9f8dbdfd8c45a1fdd6/revisions/rev_000001/model.py:L188-L244` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| desktop | rectangular / L-shaped / fold-down leaf / tilting top / wall fold-down | no | yes | `desktop_profile`, `desk_layout` | 桌面拓扑和关节链不同，不能只用宽深表达 |
| support | four legs / pedestal panels / trestle / wall brackets / telescoping columns / C-base | no | yes | `support_style` | 支撑方式是类别外形核心差异 |
| drawer housing | apron bay / side pedestal / double pedestal / under-top housing / card catalog grid | no | yes | `drawer_layout` | 抽屉位置、列数和父件不同 |
| drawer | shallow pencil drawer / file drawer / stacked small drawers / card catalog drawers | no | yes | `drawer_layout`, `drawer_count` | 抽屉数量和分层布局是定性差异 |
| handle / pull | bar pull / knob pair / recessed oval / finger slot / none | no | yes | `handle_style` | 操作件形态差异明显 |
| optional work feature | keyboard tray / drop-front leaf / mirror / cable flap / monitor riser / tilt top | no | yes | `has_keyboard_tray`, `has_drop_leaf`, `optional_feature` | 多个 5 星样本包含额外活动件 |
| drawer slide travel | only length/depth variation inside same layout | yes | no | `drawer_travel` | 同一 drawer layout 内行程可连续表达 |

## 组合逻辑（Composition Logic）
1. 根据 `desk_layout` 选择 desk spine：simple writing desk 为 `desk_frame -> drawer`，pedestal desk 为 `desk_top -> pedestal(s) -> drawer_i`，standing/L desk 为 `base -> top_assembly -> drawer_housing -> drawer`，secretary 为 `body -> drop_leaf/shelf/drawers`。
2. 先生成 desktop 和主支撑，确保所有支撑落地或 wall-mount 有 wall plate。
3. 生成 drawer housing：apron runners、pedestal carcass、under-top housing 或 card grid。
4. 为每个 drawer 创建独立 part，front/box/rails/pull 均随 drawer 移动。
5. 为每个 drawer 添加 prismatic joint；axis 根据坐标约定可以是 `(0, -1, 0)` 或 `(0, 1, 0)`，但必须与 drawer front outward 方向一致。
6. 可选 drop leaf、keyboard shelf、height top、tilting top、mirror/door 按 layout 添加独立 part 和 joint。
7. 非活动装饰如 cubbies、modesty panel、apron trim、status/labels 优先挂为 parent visual。

## 已有模板写法参考
prismatic_slide / guide_shoe / revolute_hinge / telescoping_tube / handle_grip

## 约束
- 必须至少有一个 `drawer_slide_i` prismatic joint。
- drawer front 必须位于用户可见边，抽出方向必须远离 drawer housing。
- drawer 打开到最大行程时仍要有 rail overlap。
- `drawer_count` 与实际 drawer part 数必须一致。
- L-shaped top 必须是真实 L profile 或两段相交 top，不得只用大矩形代替。
- `support_style=telescoping_columns` 时 top assembly 必须沿 Z 升降并保持 column insertion。
- `has_drop_leaf=true` 时 leaf closed 为竖直/斜前面板，open pose 变为可用写字面。
- pedestal drawers 不能漂浮在桌面下方，必须由 pedestal/housing 包围或支撑。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | desktop + grounded support + at least one drawer present |
| drawer joint count | 至少 1 个 prismatic drawer joint；数量与 `drawer_count` 匹配 |
| drawer axis | drawer slide axis 沿前后方向 `(0, ±1, 0)` |
| drawer retained overlap | drawer at max travel still overlaps rails/housing |
| support grounding | legs/pedestals/wall brackets connect to top and ground/wall |
| layout consistency | `desk_layout`, `desktop_profile`, `support_style`, `drawer_layout` 互相兼容 |
| optional joints | drop leaf、height、keyboard tray、tilt top 若启用则有对应 joint 和合理 range |
| part diversity | `desktop_profile`, `support_style`, `drawer_layout`, `handle_style` 均存在并驱动几何分支 |
| no floating | drawers、handles、rails、optional leaves/shelves 不漂浮 |

## Reject cases
- 有桌子但没有可滑动抽屉。
- 抽屉只是画在正面，没有独立 part 或 prismatic joint。
- 抽屉滑出方向朝桌内或横向错误。
- pedestal 或腿与桌面脱节，桌面漂浮。
- L 形、秘书桌、升降桌等 layout 被普通矩形桌面吞掉，没有对应形态差异。
- 抽屉打开后完全脱离导轨或穿过支撑板。
- handle 留在 housing 上，抽屉运动时不随 drawer 移动。
- `drawer_count` 参数和实际抽屉数量不一致。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
