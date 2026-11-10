# Camcorder With Flipout Screen Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `camcorder_with_flipout_screen` |
| template path | `agent/templates/camcorder_with_flipout_screen.py` |
| test path | `tests/agent/test_camcorder_with_flipout_screen_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 17 |
| read_count | 17 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
带翻出屏的摄像机，至少包含横向手持机身、前置镜头/镜筒、侧面 LCD 翻屏及其铰链。控制环、手带、取景器、顶把手、按键和模式拨盘可增强真实感，但不能替代“侧屏可翻出”的核心活动结构。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d` | `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L117-L205` | objective, screen door, nested screen panel, screen hinge geometry helpers |
| S2 | `rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d` | `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L226-L285` | body/objective/screen door/screen panel/mode dial part tree and joints |
| S3 | `rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05` | `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L98-L327` | documentary body, long lens with hood, top handle, two-link side screen arm |
| S4 | `rec_camcorder_with_flipout_screen_c0e525a2c15c48f2a7d03c53f846c765` | `data/records/rec_camcorder_with_flipout_screen_c0e525a2c15c48f2a7d03c53f846c765/revisions/rev_000001/model.py:L90-L263` | hand strap, single side screen hinge, lens ring, push buttons |
| S5 | `rec_camcorder_with_flipout_screen_6e80a320a70b4ca5a1121a6e9baf5792` | `data/records/rec_camcorder_with_flipout_screen_6e80a320a70b4ca5a1121a6e9baf5792/revisions/rev_000001/model.py:L103-L300` | tapered body, fixed viewfinder, diopter wheel, side display door |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `body` | required；横向摄像机主机身，包含侧面 display bay、hand grip/strap pads、battery hump 或 rear hump | `body_length`, `body_width`, `body_height`, `body_profile`, `grip_style` | S2 / `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L226-L235`; S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L98-L139`; S5 / `data/records/rec_camcorder_with_flipout_screen_6e80a320a70b4ca5a1121a6e9baf5792/revisions/rev_000001/model.py:L103-L151` |
| `lens_barrel` / `objective` | required；前置镜筒、玻璃和可选遮光罩/控制环座 | `lens_length`, `lens_radius`, `lens_style`, `hood_style` | S1 / `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L117-L136`; S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L141-L183`; S5 / `data/records/rec_camcorder_with_flipout_screen_6e80a320a70b4ca5a1121a6e9baf5792/revisions/rev_000001/model.py:L153-L183` |
| `flip_screen` / `display_door` | required；侧面翻出 LCD 门或面板，闭合时覆盖 display bay | `screen_width`, `screen_height`, `screen_layout`, `screen_corner_radius` | S1 / `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L139-L205`; S4 / `data/records/rec_camcorder_with_flipout_screen_c0e525a2c15c48f2a7d03c53f846c765/revisions/rev_000001/model.py:L179-L203`; S5 / `data/records/rec_camcorder_with_flipout_screen_6e80a320a70b4ca5a1121a6e9baf5792/revisions/rev_000001/model.py:L230-L253` |
| `screen_arm` | optional；翻屏窄铰链臂，screen_layout 为 armature 时出现 | `arm_length`, `arm_profile`, `arm_open_range_deg` | S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L225-L248` |
| `lens_control_ring` | optional；镜筒上的 focus/zoom ring，可连续旋转 | `ring_style`, `ring_width`, `ring_range` | S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L185-L191`; S4 / `data/records/rec_camcorder_with_flipout_screen_c0e525a2c15c48f2a7d03c53f846c765/revisions/rev_000001/model.py:L219-L232`; S5 / `data/records/rec_camcorder_with_flipout_screen_6e80a320a70b4ca5a1121a6e9baf5792/revisions/rev_000001/model.py:L185-L196` |
| `hand_strap` | optional；右侧手带/握带，可 fixed part 或 body visual | `strap_style`, `strap_offset` | S4 / `data/records/rec_camcorder_with_flipout_screen_c0e525a2c15c48f2a7d03c53f846c765/revisions/rev_000001/model.py:L152-L177`; S5 / `data/records/rec_camcorder_with_flipout_screen_6e80a320a70b4ca5a1121a6e9baf5792/revisions/rev_000001/model.py:L135-L151` |
| `viewfinder` | optional；后上方取景器和可选 diopter wheel | `viewfinder_style`, `diopter_wheel` | S5 / `data/records/rec_camcorder_with_flipout_screen_6e80a320a70b4ca5a1121a6e9baf5792/revisions/rev_000001/model.py:L198-L228` |
| `top_handle` | optional；documentary/prosumer 款顶把手 | `top_handle_style` | S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L193-L223` |
| `controls` | optional；模式拨盘和前侧/侧面小按键 | `button_count`, `button_layout`, `mode_dial_style` | S2 / `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L246-L285`; S4 / `data/records/rec_camcorder_with_flipout_screen_c0e525a2c15c48f2a7d03c53f846c765/revisions/rev_000001/model.py:L234-L261` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `screen_hinge` | revolute | usually `(0, 0, 1)` around vertical hinge barrel on side face | side display hinge line | 0-2.35 rad | 单片侧屏/显示门向外翻开 | S2 / `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L257-L265`; S4 / `data/records/rec_camcorder_with_flipout_screen_c0e525a2c15c48f2a7d03c53f846c765/revisions/rev_000001/model.py:L204-L217`; S5 / `data/records/rec_camcorder_with_flipout_screen_6e80a320a70b4ca5a1121a6e9baf5792/revisions/rev_000001/model.py:L287-L300` |
| `screen_swivel` | revolute, optional | `(0, 0, 1)` | inner pivot between door/arm and LCD panel | 0-3.05 rad | 二级翻屏可在门/臂上继续旋转 | S2 / `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L267-L275`; S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L312-L325` |
| `screen_arm_hinge` | revolute, optional | `(0, 0, -1)` or side-normal-equivalent hinge | body side arm root | -0.35-1.10 rad | 窄 hinge arm 从机身侧面摆出 | S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L298-L311` |
| `lens_ring_spin` | continuous | `(1, 0, 0)` optical axis | lens ring center | unbounded | 镜头 focus/zoom ring 连续旋转 | S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L282-L290`; S4 / `data/records/rec_camcorder_with_flipout_screen_c0e525a2c15c48f2a7d03c53f846c765/revisions/rev_000001/model.py:L221-L232`; S5 / `data/records/rec_camcorder_with_flipout_screen_6e80a320a70b4ca5a1121a6e9baf5792/revisions/rev_000001/model.py:L262-L270` |
| `mode_dial_turn` | revolute/continuous, optional | top or rear dial normal, often `(0, 0, 1)` | dial center | about -1.85-1.40 rad or continuous | 模式拨盘旋转 | S2 / `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L277-L285` |
| `button_press_i` | prismatic, optional | into body side, commonly `(0, -1, 0)` | each button guide | 0-`BUTTON_TRAVEL` | 小按钮按压 | S4 / `data/records/rec_camcorder_with_flipout_screen_c0e525a2c15c48f2a7d03c53f846c765/revisions/rev_000001/model.py:L234-L261` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `body_profile` | enum | `palm_rounded` / `tapered_home_video` / `documentary_block` / `shoulder_rear_hump` | `tapered_home_video` | controls body shell, battery hump, top surface | S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L98-L139`; S5 / `data/records/rec_camcorder_with_flipout_screen_6e80a320a70b4ca5a1121a6e9baf5792/revisions/rev_000001/model.py:L103-L151` |
| `lens_style` | enum | `short_objective` / `long_barrel` / `wide_hood` | `short_objective` | affects lens length, radius, hood | S1 / `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L117-L136`; S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L141-L183` |
| `screen_layout` | enum | `single_door` / `door_with_inner_swivel` / `armature_two_link` | `single_door` | determines part tree and joint count | S2 / `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L240-L275`; S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L225-L325`; S5 / `data/records/rec_camcorder_with_flipout_screen_6e80a320a70b4ca5a1121a6e9baf5792/revisions/rev_000001/model.py:L230-L300` |
| `screen_width` | float | 0.064-0.096 | 0.082 | tied to display bay size | S1 / `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L167-L205`; S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L250-L273` |
| `screen_open_range_deg` | float | 120-180 | 135 | maps to `screen_hinge` upper | S2 / `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L257-L275`; S4 / `data/records/rec_camcorder_with_flipout_screen_c0e525a2c15c48f2a7d03c53f846c765/revisions/rev_000001/model.py:L204-L217` |
| `grip_style` | enum | `none` / `side_pad` / `hand_strap` / `top_handle` / `strap_and_handle` | `hand_strap` | controls optional `hand_strap` and `top_handle` parts | S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L123-L127`; S4 / `data/records/rec_camcorder_with_flipout_screen_c0e525a2c15c48f2a7d03c53f846c765/revisions/rev_000001/model.py:L152-L177`; S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L193-L223` |
| `viewfinder_style` | enum | `none` / `rear_eyecup` / `raised_viewfinder_with_diopter` | `rear_eyecup` | `raised_viewfinder_with_diopter` creates diopter wheel joint | S3 / `data/records/rec_camcorder_with_flipout_screen_d0561924591248c2b36687a2c677aa05/revisions/rev_000001/model.py:L128-L139`; S5 / `data/records/rec_camcorder_with_flipout_screen_6e80a320a70b4ca5a1121a6e9baf5792/revisions/rev_000001/model.py:L198-L228` |
| `control_layout` | enum | `minimal` / `side_buttons` / `mode_dial` / `buttons_and_dial` | `buttons_and_dial` | creates optional buttons/dial joints | S2 / `data/records/rec_camcorder_with_flipout_screen_b5753ec789b546b0a058ca52bbcd590d/revisions/rev_000001/model.py:L246-L285`; S4 / `data/records/rec_camcorder_with_flipout_screen_c0e525a2c15c48f2a7d03c53f846c765/revisions/rev_000001/model.py:L234-L261` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| body | slim travel / rounded palm / deeper prosumer / documentary block / shoulder-style rear hump | no | yes | `body_profile` | 机身轮廓、后部电池包和顶部结构有定性差异 |
| flip screen | single side panel / door plus inner swivel / screen on narrow arm | no | yes | `screen_layout` | 翻屏拓扑直接决定 joint 数量 |
| lens | short objective / long barrel / hooded wide lens | no | yes | `lens_style`, `hood_style` | 镜筒长度和遮光罩不是单纯连续缩放 |
| grip/support | side pad / hand strap / top handle / none | no | yes | `grip_style` | 观察到右侧手带和 documentary 顶把手 |
| control ring | none / focus ring / zoom ring | no | yes | `ring_style` | 可动 ring 是否存在影响 part/joint |
| viewfinder | none / rear eyecup / raised viewfinder with diopter | no | yes | `viewfinder_style` | 取景器结构和 diopter wheel 是定性差异 |
| buttons/dials | side push buttons / top or rear mode dial / both / minimal | no | yes | `control_layout` | 控件布局影响 prismatic/revolute joints |
| side hinge hardware | simple barrel / recessed bay hinge / two-link arm | no | yes | `screen_layout` | hinge hardware 与 screen topology 绑定 |

## 组合逻辑（Composition Logic）
1. 按 `body_profile` 生成 body shell、display bay、lens mount、可选 battery hump/hand grip。
2. 在 body 前端创建 fixed lens/objective；如 `ring_style` 非 none，在 lens 上创建 control ring 并添加 continuous joint。
3. 按 `screen_layout` 生成单 screen、door+screen panel 或 side_arm+screen，并把 hinge origin 放在机身侧面 display bay 后缘。
4. 根据 `grip_style` 添加 hand strap/top handle；这些默认 fixed，除非后续审核明确要求可动。
5. 根据 `viewfinder_style` 添加 rear eyecup 或 raised viewfinder；diopter wheel 可 continuous。
6. 根据 `control_layout` 添加 mode dial 和/或多个 prismatic button，所有控件必须坐落在 body 表面。

## 已有模板写法参考
revolute_hinge / button_slider / continuous_rotor / handle_grip

## 约束
- 必须有侧面翻出 screen，且 screen 通过 revolute joint 连接到 body 或 screen_arm。
- 闭合状态下 screen 必须覆盖或紧贴 body 侧面的 display bay。
- lens 必须位于 body 前端并与 body optical axis 对齐。
- `screen_layout=door_with_inner_swivel` 必须有两个 revolute joints：door hinge 和 inner screen swivel。
- `screen_layout=armature_two_link` 必须有 body-to-arm 和 arm-to-screen 两个 hinge。
- 按键若为独立 part，必须有 prismatic press joint；静态小装饰可作为 body visual。
- hand strap/top handle 必须接触 body，不可漂浮。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | body + front lens + side flip screen present |
| screen joint | 至少 1 个 revolute hinge，axis 与侧边铰链方向一致 |
| screen closed placement | 闭合时 screen/display_door 与 display bay 在 XZ 上重叠 |
| screen open sweep | 打开姿态 screen 远离 body 侧面，无严重穿模 |
| lens alignment | lens/control ring 与 body optical axis 同心 |
| optional ring | `ring_style` 非 none 时有 continuous ring joint |
| control buttons | `control_layout` 包含 buttons 时有对应 prismatic joints |
| part diversity | `body_profile`, `screen_layout`, `lens_style`, `grip_style`, `viewfinder_style`, `control_layout` 均暴露 |
| no floating | screen/arm/lens/strap/handle/control parts 全部连接到主树 |

## Reject cases
- 翻屏缺失或只是画在机身上的贴片。
- screen hinge 不在侧边，打开时绕中心乱转。
- 没有前置镜头，变成普通盒子或手机。
- screen 与 body 闭合位置不对应，漂浮在外。
- 二级翻屏布局只实现一个 joint。
- 镜头控制环不与镜筒同轴。
- 手带、顶把手或取景器漂浮。
- 机身比例变成相机/投影仪，缺少摄像机横向主体。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核 |
