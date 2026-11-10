# Camera Flash Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `camera_flash` |
| template path | `agent/templates/camera_flash.py` |
| test path | `tests/agent/test_camera_flash_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 34 |
| read_count | 34 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
相机热靴闪光灯，至少包含安装脚/热靴底座、竖向电池/控制机身、可转向的颈部或 yoke，以及带前置 diffuser/fresnel face 的闪光灯头。典型活动包括灯头 yaw/pan、pitch/tilt，部分样本还带弹出 bounce card、侧电池门和按钮/拨盘。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_camera_flash_1f41067553084bc89875784f5e1765b9` | `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L45-L246` | hotshoe body, rear controls, articulated neck, box head, prismatic bounce card |
| S2 | `rec_camera_flash_584b3bd58a0748b49ed38a865bd36875` | `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L65-L268` | professional yoke arms, rear dial, button bank, head slot and bounce card |
| S3 | `rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b` | `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L50-L243` | stepped battery body, hinged side battery door, trunnion yoke, lamp head |
| S4 | `rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3` | `data/records/rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3/revisions/rev_000001/model.py:L71-L247` | tall body with hotshoe rails, compact yoke, broad head, prismatic buttons |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `body` | required；竖向电池/控制机身，带 hotshoe foot、rear panel、display/buttons | `body_height`, `body_width`, `body_depth`, `body_profile`, `control_layout` | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L45-L110`; S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L65-L145`; S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L50-L84`; S4 / `data/records/rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3/revisions/rev_000001/model.py:L71-L124` |
| `mount_foot` | required visual on body；热靴底板、shoe block、rails、contact plate | `mount_style`, `rail_width`, `lock_ring` | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L49-L66`; S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L65-L75`; S4 / `data/records/rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3/revisions/rev_000001/model.py:L77-L100` |
| `neck` / `yoke` | required；在 body 和 head 之间的 yaw/pan/tilt 结构，可为 short neck 或 side yoke arms | `neck_style`, `yoke_span`, `swivel_socket_radius` | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L112-L145`; S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L147-L198`; S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L130-L165`; S4 / `data/records/rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3/revisions/rev_000001/model.py:L126-L160` |
| `head` | required；boxy/wide flash lamp head，含 front diffuser/fresnel face、pivot bosses、slot rails | `head_width`, `head_depth`, `head_height`, `head_shape`, `diffuser_style` | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L146-L205`; S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L200-L251`; S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L167-L214`; S4 / `data/records/rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3/revisions/rev_000001/model.py:L162-L192` |
| `bounce_card` | optional；从灯头顶部/前部滑出的反光卡 | `bounce_card_enabled`, `bounce_card_travel` | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L206-L246`; S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L253-L268` |
| `battery_door` | optional；侧面铰链电池门 | `battery_door_enabled`, `battery_door_side`, `battery_door_range_deg` | S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L86-L129`; S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L216-L224` |
| `rear_controls` | optional；LCD、command dial、button bank；复杂样本中按钮是 prismatic parts | `control_layout`, `button_count`, `dial_enabled` | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L67-L104`; S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L100-L145`; S4 / `data/records/rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3/revisions/rev_000001/model.py:L213-L245` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `body_to_neck_yaw` / `body_to_yoke_swivel` | revolute | `(0, 0, 1)` | top swivel socket of body | about -pi to pi, or -1.35 to 1.35 | 灯头底部 yaw/pan 旋转 | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L220-L228`; S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L190-L198`; S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L225-L233`; S4 / `data/records/rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3/revisions/rev_000001/model.py:L194-L202` |
| `neck_to_head_tilt` / `yoke_to_head` | revolute | `(1, 0, 0)` or `(0, -1, 0)` depending head/yoke local layout; template should normalize to head side-pivot axis | side trunnion/pivot boss | about -0.25 to 1.55 rad | 灯头向上抬起/俯仰 | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L229-L237`; S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L243-L251`; S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L234-L242`; S4 / `data/records/rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3/revisions/rev_000001/model.py:L203-L211` |
| `bounce_card_slide` | prismatic, optional | `(0, 0, 1)` | top/front head card slot | 0-0.024 / 0-0.045 | bounce card 从 head 内向上滑出 | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L238-L246`; S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L260-L268` |
| `battery_door_hinge` | revolute, optional | `(0, 0, -1)` or side-door hinge axis | side edge of body battery door | 0-1.75 rad | 电池门向外打开 | S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L216-L224` |
| `button_press_i` | prismatic, optional | into rear panel, often `(1, 0, 0)` | individual button center | 0-0.0025 | 后部按钮按压 | S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L123-L145`; S4 / `data/records/rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3/revisions/rev_000001/model.py:L223-L245` |
| `rear_dial_turn` | revolute, optional | dial normal, e.g. `(-1, 0, 0)` | rear dial center | -pi to pi | rear command wheel/dial rotation | S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L100-L121` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `body_profile` | enum | `compact_stepped` / `tall_control_body` / `narrow_speedlight` | `compact_stepped` | controls body shell, rear panel, socket height | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L45-L110`; S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L50-L84`; S4 / `data/records/rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3/revisions/rev_000001/model.py:L71-L124` |
| `neck_style` | enum | `short_neck` / `trunnion_yoke` / `side_yoke_arms` | `short_neck` | determines neck/yoke geometry and tilt axis | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L112-L145`; S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L147-L198`; S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L130-L165` |
| `head_shape` | enum | `boxy_speedlight` / `wide_professional` / `rounded_rect_bezel` | `boxy_speedlight` | changes head proportions and diffuser face | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L146-L205`; S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L200-L251`; S4 / `data/records/rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3/revisions/rev_000001/model.py:L162-L192` |
| `diffuser_style` | enum | `flat_panel` / `bezel_plus_lens` / `fresnel_face` | `fresnel_face` | controls head front visuals | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L178-L183`; S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L186-L214`; S4 / `data/records/rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3/revisions/rev_000001/model.py:L168-L179` |
| `bounce_card_enabled` | bool | true / false | true | if true create card part and prismatic joint | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L206-L246`; S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L253-L268` |
| `battery_door_enabled` | bool | true / false | false | if true create door part and hinge | S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L86-L129`; S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L216-L224` |
| `control_layout` | enum | `screen_only` / `dial` / `button_bank` / `screen_dial_buttons` | `screen_dial_buttons` | determines rear controls and button/dial joints | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L67-L104`; S2 / `data/records/rec_camera_flash_584b3bd58a0748b49ed38a865bd36875/revisions/rev_000001/model.py:L100-L145`; S4 / `data/records/rec_camera_flash_1113425bfbfd453e91eea0051e4aeaa3/revisions/rev_000001/model.py:L213-L245` |
| `head_tilt_range_deg` | float | 75-105 | 90 | maps to tilt upper limit | S1 / `data/records/rec_camera_flash_1f41067553084bc89875784f5e1765b9/revisions/rev_000001/model.py:L229-L237`; S3 / `data/records/rec_camera_flash_18fb7cd292e24d7cbb0b445c0144bf2b/revisions/rev_000001/model.py:L234-L242` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| body | compact stepped / tall rear control body / narrow speedlight | no | yes | `body_profile` | 控制面、热靴和 socket 的布局不同 |
| neck/yoke | short articulated neck / trunnion yoke / side yoke arms | no | yes | `neck_style` | 关节结构和 tilt axis 来源不同 |
| head | boxy head / broad professional head / rounded bezel head | no | yes | `head_shape` | 灯头几何不是宽高连续变化即可覆盖 |
| diffuser | flat diffuser / bezel + lens / fresnel face | no | yes | `diffuser_style` | 前脸视觉和开口结构有定性区别 |
| bounce card | none / sliding top card | no | yes | `bounce_card_enabled` | 有无 card 改变 part/joint |
| battery door | none / side hinged door | no | yes | `battery_door_enabled` | 电池门是可动件，不能用贴图代替 |
| rear controls | LCD only / dial / prismatic button bank / combined | no | yes | `control_layout` | 控件数量和 joint 类型随布局变化 |
| mount foot | plate only / rails + shoe block / contact + lock ring | no | yes | `mount_style` | 热靴底座是类别识别部件，形态不同 |

## 组合逻辑（Composition Logic）
1. 先构建 body，并把 hotshoe foot/rails/contact 作为 body visuals。
2. 按 `neck_style` 创建 neck/yoke part，添加 yaw swivel joint 到 body 顶部 socket。
3. 构建 head，保证 diffuser/fresnel face 朝前；添加 head tilt joint 到 neck/yoke。
4. 若 `bounce_card_enabled`，在 head 内部 slot 添加 bounce_card part 和 Z 向 prismatic slide。
5. 若 `battery_door_enabled`，在 body 侧面添加 hinged battery_door。
6. 根据 `control_layout` 添加 rear LCD/dial/buttons；可动按钮和拨盘独立建 part，静态标签作为 body visual。

## 已有模板写法参考
revolute_hinge / prismatic_slide / button_slider / latch_lock

## 约束
- 必须有 body、mount foot、neck/yoke、head、front diffuser。
- 必须至少有两个头部瞄准关节：body-to-neck/yoke yaw 和 neck/yoke-to-head tilt。
- head tilt joint origin 必须穿过 head/yoke 的侧面 trunnion 或 pivot boss。
- mount foot 必须位于 body 下方，不可和 head 同层。
- bounce card 若启用，必须沿 head slot 向上滑出并保持部分插入。
- battery door 若启用，hinge origin 必须在 body 侧边。
- rear button bank 的按键若独立建模，必须是 prismatic press joints。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | hotshoe foot + vertical body + articulated head + diffuser present |
| yaw joint | 有 revolute yaw/swivel joint，axis 近似 `(0, 0, 1)` |
| tilt joint | 有 revolute head tilt joint，axis 穿过 yoke/head side pivots |
| head separation | head 位于 body 上方，经 neck/yoke 连接，不直接漂浮 |
| diffuser placement | diffuser/fresnel face 在 head 前端 |
| bounce card | enabled 时有 prismatic joint，axis 向上，行程后仍留在 slot 内 |
| battery door | enabled 时有 side hinge revolute，打开时远离 body |
| controls | `control_layout` 中要求的 dial/buttons 有对应 joints |
| part diversity | `body_profile`, `neck_style`, `head_shape`, `diffuser_style`, `control_layout` 均暴露 |
| no floating | body 为根，neck/yoke/head/card/door/buttons 全部连接到主树 |

## Reject cases
- 没有热靴安装脚，像普通手电或灯箱。
- head 不能 tilt/yaw，或只有一个假关节。
- diffuser 缺失，灯头只是黑盒。
- neck/yoke 与 body 或 head 断开。
- bounce card 滑出后完全脱离 head。
- rear controls 漂浮或按钮没有按压方向。
- 电池门 hinge 在门中心而非侧边。
- head 轴线与 yoke 明显不共线，转动时严重穿模。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核 |
