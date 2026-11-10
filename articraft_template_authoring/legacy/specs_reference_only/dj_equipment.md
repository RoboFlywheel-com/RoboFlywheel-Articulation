# DJ Equipment Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `dj_equipment` |
| template path | `agent/templates/dj_equipment.py` |
| test path | `tests/agent/test_dj_equipment_template.py` |
| primary_anchor | `rec_dj_equipment_47e2bd7d05da479eb2363c19da61276b:rev_000001` |
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
DJ equipment 是过宽类别：5 星样本覆盖 turntable / CDJ deck、mixer、all-in-one controller、pad sampler、monitor speaker 和 rack-like devices。共同核心不是某一个固定外壳，而是专业音频控制台 / 演出设备：有带面板的硬质机身、可操作控制件，以及至少一种真实运动语义，如 platter / jog wheel 旋转、fader 直线滑动、knob 旋转、pad 按压、tonearm 摆动或 speaker tilt。

审核建议：若目标是成熟模板，优先拆分为 `dj_turntable_deck`、`dj_mixer_controller`、`dj_performance_pad_controller`、`dj_monitor_speaker` 等稳定子类；若仍保留单 slug，`config_from_seed` 必须只采样已实现并测试覆盖的稳定子域，不能把所有 39 个样本拓扑一次性硬塞进一个模板。

采纳策略：5 星样本在本类别里主要用于识别不同设备族和提取可适配 control helpers。默认成熟实现不应覆盖全部设备族；应先选择 `controller_mixer_turntable_core`，把 platter、fader、knob、pad、tonearm、carry handle 分别做成兼容 helper。monitor speaker 和纯 pad sampler 若不拆分，应作为 reviewer-gated / future split candidate，不进入默认 seed domain。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_dj_equipment_6e26a372336146aa950bcca959ce6d20` | `data/records/rec_dj_equipment_6e26a372336146aa950bcca959ce6d20/revisions/rev_000001/model.py:L44-L77` | turntable plinth, arm rest, cue meshes and deck-specific geometry helpers |
| S2 | `rec_dj_equipment_6e26a372336146aa950bcca959ce6d20` | `data/records/rec_dj_equipment_6e26a372336146aa950bcca959ce6d20/revisions/rev_000001/model.py:L79-L300` | turntable top plate, platter, cue lift, tonearm parts, continuous platter joint, cue prismatic joint and tonearm revolute joint |
| S3 | `rec_dj_equipment_395917f2ec534974bdcae44f082b3856` | `data/records/rec_dj_equipment_395917f2ec534974bdcae44f082b3856/revisions/rev_000001/model.py:L55-L177` | mixer dimensions, fader / knob layout grid, top panel holes and slots |
| S4 | `rec_dj_equipment_395917f2ec534974bdcae44f082b3856` | `data/records/rec_dj_equipment_395917f2ec534974bdcae44f082b3856/revisions/rev_000001/model.py:L184-L323` | reusable fader and knob builders, crossfader, channel faders, master fader and EQ knob controls |
| S5 | `rec_dj_equipment_47e2bd7d05da479eb2363c19da61276b` | `data/records/rec_dj_equipment_47e2bd7d05da479eb2363c19da61276b/revisions/rev_000001/model.py:L39-L143` | platter / slider helpers and folding carry handle helper for all-in-one DJ controller |
| S6 | `rec_dj_equipment_47e2bd7d05da479eb2363c19da61276b` | `data/records/rec_dj_equipment_47e2bd7d05da479eb2363c19da61276b/revisions/rev_000001/model.py:L145-L435` | dual-jog controller housing, central mixer panel, pads, knobs, faders, carry handle and joints |
| S7 | `rec_dj_equipment_12cc4b441480440ab78ac715cebab79f` | `data/records/rec_dj_equipment_12cc4b441480440ab78ac715cebab79f/revisions/rev_000001/model.py:L22-L53` | lofted rounded pad mesh for performance buttons |
| S8 | `rec_dj_equipment_12cc4b441480440ab78ac715cebab79f` | `data/records/rec_dj_equipment_12cc4b441480440ab78ac715cebab79f/revisions/rev_000001/model.py:L65-L326` | pad-grid dimensions, 8x8 prismatic pads, lower faders and slot layout |
| S9 | `rec_dj_equipment_01b8a962219e49d29f1b01cacfc25b40` | `data/records/rec_dj_equipment_01b8a962219e49d29f1b01cacfc25b40/revisions/rev_000001/model.py:L63-L286` | wedge monitor speaker profile, tilt bracket, trunnions and speaker cabinet tilt joint |
| S10 | `rec_dj_equipment_395917f2ec534974bdcae44f082b3856` | `data/records/rec_dj_equipment_395917f2ec534974bdcae44f082b3856/revisions/rev_000001/model.py:L366-L405` | control-axis tests for faders and knobs, useful for later validator expectations |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `equipment_body` / `base_housing` | 必需；桌面式或楔形设备外壳，可为 turntable plinth、mixer chassis、controller body、pad sampler 或 speaker cabinet | `equipment_family`, `body_width`, `body_depth`, `body_height`, `body_profile` | S1 / `model.py:L44-L77`; S2 / `model.py:L79-L152`; S3 / `model.py:L55-L177`; S6 / `model.py:L145-L324`; S8 / `model.py:L65-L125`; S9 / `model.py:L63-L271` |
| `top_panel` / `control_panel` | 必需；带孔、槽、标线、LED / labels 的操作面板 | `panel_slope`, `panel_layout`, `channel_count`, `control_density` | S2 / `model.py:L79-L152`; S3 / `model.py:L55-L177`; S6 / `model.py:L145-L324`; S8 / `model.py:L65-L326` |
| `platter_i` / `jog_wheel_i` | turntable / controller 条件必需；圆形旋转盘、jog wheel、rim 或 platter well | `platter_count`, `platter_radius`, `platter_style`, `jog_ring_style` | S2 / `model.py:L154-L183`; S5 / `model.py:L39-L99`; S6 / `model.py:L326-L435` |
| `tonearm` / `cue_lift` | turntable 条件必需；唱臂、针头、arm rest、cue lever / lift | `tonearm_enabled`, `tonearm_length`, `cue_lift_travel` | S1 / `model.py:L44-L77`; S2 / `model.py:L185-L300` |
| `fader_i` | mixer / controller / pad sampler 条件必需；channel fader、crossfader、master fader，包含 slot 和 cap | `fader_count`, `fader_orientation`, `fader_travel`, `fader_cap_style` | S3 / `model.py:L55-L177`; S4 / `model.py:L184-L323`; S5 / `model.py:L39-L99`; S6 / `model.py:L326-L435`; S8 / `model.py:L287-L326` |
| `knob_i` / `rotary_encoder_i` | mixer / controller 条件必需；EQ、gain、filter、master 等旋钮 | `knob_count`, `knob_style`, `knob_bank_layout` | S3 / `model.py:L55-L177`; S4 / `model.py:L244-L323`; S6 / `model.py:L145-L324` |
| `pad_i` / `button_i` | performance pad 条件必需；可按压 rubber pad / cue button / transport button | `pad_grid_rows`, `pad_grid_cols`, `pad_shape`, `pad_travel` | S6 / `model.py:L145-L324`; S7 / `model.py:L22-L53`; S8 / `model.py:L65-L326` |
| `carry_handle` | optional；controller / portable sampler 的折叠提手 | `handle_enabled`, `handle_style`, `handle_hinge_span` | S5 / `model.py:L101-L143`; S6 / `model.py:L382-L435` |
| `speaker_tilt_cabinet` / `tilt_bracket` | optional 或建议拆分；DJ monitor speaker 的楔形音箱与倾角支架 | `speaker_enabled`, `speaker_tilt_range`, `bracket_style` | S9 / `model.py:L63-L286` |
| `trim_and_labels` | visual；刻度、ring ticks、channel labels、LED dots、screws、rubber feet | `label_style`, `led_count`, `trim_style` | S2 / `model.py:L79-L152`; S3 / `model.py:L55-L177`; S6 / `model.py:L145-L324`; S8 / `model.py:L65-L326` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `platter_spin_i` / `jog_spin_i` | continuous | `(0, 0, 1)` | platter / jog wheel center normal to top panel | unbounded | turntable platter 或 controller jog wheel 绕中心垂直轴旋转 | S2 / `model.py:L269-L300`; S6 / `model.py:L382-L435` |
| `tonearm_swing` | revolute | `(0, 0, 1)` | tonearm pivot post on deck | `[0, 0.75]` typical | 唱臂绕 pivot 在唱片面上方摆动 | S2 / `model.py:L185-L300` |
| `cue_lift_slide` | prismatic | `(0, 0, 1)` | cue lift post / rest | `[0, cue_lift_travel]` | cue lift 垂直抬起 / 放下唱臂 | S2 / `model.py:L185-L300` |
| `fader_slide_i` | prismatic | `(0, 1, 0)` or `(1, 0, 0)` according to slot orientation | fader slot centerline | `[0, fader_travel]` | channel fader 沿槽滑动；crossfader 通常横向 | S4 / `model.py:L184-L323`; S6 / `model.py:L382-L435`; S8 / `model.py:L287-L326`; S10 / `model.py:L366-L405` |
| `knob_turn_i` | revolute or continuous | `(0, 0, 1)` | knob center normal to top panel | `[-2.6, 2.6]` or unbounded encoder | EQ / gain knob 绕面板法线旋转 | S4 / `model.py:L244-L323`; S10 / `model.py:L366-L405` |
| `pad_press_i` | prismatic | `(0, 0, -1)` or local panel inward normal | pad center | `[0, pad_travel]` | performance pad / cue button 向下按压 | S7 / `model.py:L22-L53`; S8 / `model.py:L244-L285` |
| `carry_handle_hinge` | revolute | `(1, 0, 0)` or handle hinge-bar axis | rear / side bracket pin line | `[0, 1.75]` | portable controller 提手翻起 | S5 / `model.py:L101-L143`; S6 / `model.py:L382-L435` |
| `speaker_tilt_joint` | revolute | `(1, 0, 0)` | trunnion axis through side brackets | `[-0.45, 0.45]` | monitor speaker 在支架上俯仰 | S9 / `model.py:L161-L286` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `equipment_family` | enum | `turntable_deck` / `dj_mixer` / `all_in_one_controller` / `pad_sampler` / `tilt_monitor_speaker` | `all_in_one_controller` | 决定主 topology、活动件集合和 `config_from_seed` 稳定子域 | S2 / `model.py:L79-L300`; S3 / `model.py:L55-L323`; S6 / `model.py:L145-L435`; S8 / `model.py:L65-L326`; S9 / `model.py:L63-L286` |
| `seed_domain` | enum | `controller_mixer_turntable_core` / `pad_sampler_review_gated` / `monitor_speaker_split_candidate` | `controller_mixer_turntable_core` | default seed 只采样 controller / mixer / turntable 兼容域；其它族需要审核或拆分 | S2 / `model.py:L79-L300`; S3 / `model.py:L55-L323`; S6 / `model.py:L145-L435`; S8 / `model.py:L65-L326`; S9 / `model.py:L63-L286` |
| `body_profile` | enum | `flat_rectangular` / `rounded_controller` / `wedge_panel` / `tilted_speaker_box` / `pad_grid_slab` | `rounded_controller` | 由 `equipment_family` 默认派生，可审核后限制 | S1 / `model.py:L44-L77`; S3 / `model.py:L55-L177`; S6 / `model.py:L145-L324`; S8 / `model.py:L65-L125`; S9 / `model.py:L63-L271` |
| `body_width` | float | `0.28-0.95` | `0.62` | all-in-one controller 较宽；mixer / sampler 较窄 | S2 / `model.py:L79-L152`; S3 / `model.py:L55-L84`; S6 / `model.py:L145-L324`; S8 / `model.py:L65-L125` |
| `body_depth` | float | `0.22-0.68` | `0.38` | 派生 platter radius、fader lanes、pad pitch | S2 / `model.py:L79-L152`; S3 / `model.py:L55-L84`; S6 / `model.py:L145-L324`; S8 / `model.py:L65-L125` |
| `platter_count` | int | `0 / 1 / 2` | `2` | turntable=1, controller=2, mixer/pad/speaker=0 | S2 / `model.py:L154-L300`; S6 / `model.py:L326-L435` |
| `platter_style` | enum | `vinyl_turntable` / `cdj_jog_wheel` / `ribbed_controller_jog` / `none` | `ribbed_controller_jog` | 决定 rim ticks、disc material、height | S2 / `model.py:L154-L183`; S5 / `model.py:L39-L99`; S6 / `model.py:L326-L435` |
| `channel_count` | int | `2-4` | `2` | mixer grid rows / columns and fader count derive from channels | S3 / `model.py:L55-L177`; S4 / `model.py:L184-L323` |
| `fader_count` | int | `0-9` | `5` | from channel faders + crossfader + master fader | S4 / `model.py:L184-L323`; S6 / `model.py:L326-L435`; S8 / `model.py:L287-L326` |
| `fader_orientation` | enum | `vertical_channels_horizontal_cross` / `all_vertical` / `horizontal_bank` | `vertical_channels_horizontal_cross` | determines axis `(0,1,0)` vs `(1,0,0)` | S3 / `model.py:L55-L177`; S4 / `model.py:L184-L323`; S8 / `model.py:L287-L326` |
| `knob_bank_layout` | enum | `eq_rows` / `paired_deck_controls` / `single_master_strip` / `none` | `eq_rows` | derives knob count and positions | S3 / `model.py:L55-L177`; S4 / `model.py:L244-L323`; S6 / `model.py:L145-L324` |
| `pad_grid_rows` | int | `0 / 2 / 4 / 8` | `4` | controller default 2 or 4; pad sampler may use 8 | S6 / `model.py:L145-L324`; S8 / `model.py:L65-L326` |
| `pad_grid_cols` | int | `0 / 4 / 8` | `4` | compatible with rows; `0` if no pads | S7 / `model.py:L22-L53`; S8 / `model.py:L65-L326` |
| `pad_shape` | enum | `rounded_square` / `low_rect_button` / `circular_cue` | `rounded_square` | controls pad mesh profile and travel clearance | S7 / `model.py:L22-L53`; S8 / `model.py:L244-L285`; S6 / `model.py:L145-L324` |
| `tonearm_enabled` | bool | `true` / `false` | `false` | true only for `turntable_deck` unless reviewer approves hybrid | S1 / `model.py:L44-L77`; S2 / `model.py:L185-L300` |
| `handle_enabled` | bool | `true` / `false` | `false` | portable controller / sampler variants only | S5 / `model.py:L101-L143`; S6 / `model.py:L382-L435` |
| `speaker_enabled` | bool | `true` / `false` | `false` | should normally be separate `dj_monitor_speaker` template | S9 / `model.py:L63-L286` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| body / housing | turntable plinth / mixer chassis / all-in-one controller / pad slab / wedge speaker | no | yes | `equipment_family`, `body_profile` | 这些不是同一拓扑的尺寸变化，主部件和 joint set 不同 |
| top panel | platter deck / fader mixer grid / dual deck controller / 8x8 pad grid / speaker baffle | no | yes | `panel_layout`, `equipment_family` | 面板开孔、槽和 control grouping 完全不同 |
| rotating control | vinyl platter / controller jog / rotary knob / encoder | no | yes | `platter_style`, `knob_bank_layout` | 都旋转但尺度、位置和语义不同 |
| fader / slider | channel faders / crossfader / lower sampler sliders | no | yes | `fader_orientation`, `fader_count` | slot orientation 影响 axis 和 validator |
| pads / buttons | rounded square performance pads / cue buttons / transport buttons | no | yes | `pad_shape`, `pad_grid_rows`, `pad_grid_cols` | grid topology 是 sampler/controller 的身份核心 |
| tonearm / cue | present only on turntable, absent elsewhere | no | yes | `tonearm_enabled` | tonearm joint chain 与 mixer/controller 无关 |
| carry handle | folding controller handle / none | no | yes | `handle_enabled`, `handle_style` | 折叠 handle 是独立 hinge topology |
| speaker bracket | wedge speaker with trunnion / none | no | yes | `speaker_enabled`, `bracket_style` | 与桌面控制器拓扑差异大，建议拆分 |
| trim / labels | ticks / channel labels / LEDs / screws | yes | no | `label_style`, `led_count` | 装饰差异可连续 / count 表达，不应创建大量独立活动件 |

## 组合逻辑（Composition Logic）
1. 先根据 `equipment_family` 选择主 topology；不要先随机 controls 再拼到任意 body 上。
2. `turntable_deck`：以 plinth envelope 为基准，platter center 和 radius 从 top panel 可用圆形区域派生，tonearm pivot 放在 platter 后右侧安全扇区，cue lift 与 arm rest 贴近 tonearm pivot。
3. `dj_mixer`：以 top_panel grid 为基准，先派生 channel lanes，再派生每条 lane 的 fader slot、knob bank、button rows；fader cap origin 从 slot centerline 和 travel 派生。
4. `all_in_one_controller`：以左右 deck 圆形区域和中央 mixer strip 为约束基准，左右 jog wheel 镜像，center strip 放 faders / knobs，pads 放在 deck 下方或外侧。
5. `pad_sampler`：以 pad grid pitch 为基准，pad mesh、press joint origin、row/col labels 都从同一 grid 派生；lower faders 放在 grid 下方槽位。
6. `tilt_monitor_speaker`：以 tilt bracket trunnion axis 为基准，speaker cabinet 通过侧 trunnions 挂在 bracket 内，不应和 controller controls 混合。
7. 所有 fader 必须由 slot 定义 travel 和 axis；cap 在 closed / neutral pose 位于 slot 内，max travel 不离开槽。
8. 所有 knob / platter / jog 的 axis 必须沿面板法线，不能随 body size 随机倾斜；如果 panel 有 slope，需要用 local normal 转成世界系 metadata。
9. pad / button 的 prismatic axis 沿 panel inward normal，press travel 小于 pad thickness 和 panel clearance。
10. labels、LED、screws、rubber feet、decorative ticks 默认作为 parent visual，只有真实可动控制件创建 part。
11. `resolve_config` 必须执行 family/control 兼容矩阵：`all_in_one_controller` 允许双 jog、中央 mixer strip、2x4/4x4 pads 和 carry handle，但不允许 tonearm 或 speaker tilt；`turntable_deck` 需要 1 个 platter + tonearm/cue，可有少量 knobs/buttons，但不允许 8x8 pad grid；`dj_mixer` 需要 fader + knob banks，不允许 platter/tonearm；`pad_sampler` 需要 pad grid + lower faders，默认 review-gated；`tilt_monitor_speaker` 只允许 speaker cabinet + tilt bracket，默认 split candidate。
12. adopted source 只能填充对应 family 的 helper；例如 S9 的 speaker tilt 不能作为 all-in-one controller 的 body variant，S8 的 8x8 pad grid 不能强塞进 turntable deck。

## 已有模板写法参考
continuous_rotor / button_slider / prismatic_slide / guide_shoe / revolute_hinge / handle_grip

## 约束
- 审核前应决定是否拆分；若不拆分，模板实现必须显式限制 seed domain，不能随机生成未实现拓扑。
- 每个生成结果必须至少有一种真实 DJ control joint：platter/jog spin、fader slide、knob turn、pad press、tonearm swing 或 speaker tilt。
- fader slot、pad recess、platter well、knob hole 必须先由 panel layout 派生，活动件再坐进这些约束内。
- `turntable_deck` 必须有 platter；若 `tonearm_enabled=true`，tonearm pivot 和 cartridge 必须在 platter 工作半径外侧。
- `dj_mixer` 必须有 fader 和 knob bank；不能只生成一块带按钮的盒子。
- `all_in_one_controller` 必须有双 jog 或双 deck 结构，以及中央 mixer control strip。
- pad sampler 的 pad count 必须等于 rows x cols，pad joints 不得数量不匹配。
- speaker tilt 变体不应同时携带 turntable tonearm / mixer fader grid，除非 reviewer 明确接受超宽组合。
- `seed_domain=controller_mixer_turntable_core` 时，`pad_sampler` 和 `tilt_monitor_speaker` 不得被默认采样；如果 reviewer 不拆分，只能通过显式参数启用。
- 不能为了覆盖全部 5 星样本，在同一个设备上同时放 turntable tonearm、双 jog、8x8 pad grid 和 tilting monitor speaker。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | 有 professional audio equipment body + top/control panel + at least one active control joint |
| family consistency | `equipment_family` 决定的 required parts 都存在，互斥拓扑不混乱 |
| seed domain | default seed domain excludes review-gated pad sampler and monitor speaker split candidates |
| compatibility matrix | family/control combinations are legal before build; invalid controls are dropped or downgraded in `resolve_config` |
| platter axis | platter / jog continuous joint axis 沿面板法线，origin 在圆盘中心 |
| fader axis | fader prismatic axis 与 slot orientation 一致，cap travel 保持在 slot 内 |
| knob axis | knob revolute / continuous axis 沿面板法线，origin 在 knob center |
| pad travel | pad prismatic axis 沿面板 inward normal，press range 不穿透底板 |
| tonearm semantics | tonearm pivot 位于 deck 后侧，swing range 只扫过 platter 外缘到唱片区域 |
| split warning | if `equipment_family` includes speaker or pad sampler, reviewer must approve broad template or split slug |
| part diversity | `equipment_family`, `body_profile`, `panel_layout`, `platter_style`, `fader_orientation`, `pad_shape` 均存在并驱动几何分支 |
| no floating | platter、faders、knobs、pads、tonearm、handle、speaker cabinet 均坐在 panel / bracket / body 上 |

## Reject cases
- 普通音箱、普通按钮盒或随机电子设备，没有 DJ control identity。
- fader 是装饰条，没有独立 part 或 prismatic joint。
- knob / platter axis 水平或偏离中心，旋转语义错误。
- pad grid 数量与参数不一致，或 pads 悬空在 panel 上方。
- turntable 有 tonearm 但没有 platter，或 tonearm pivot 在唱片中心。
- all-in-one controller 没有双 deck / jog 结构，只是 mixer 拉宽。
- speaker bracket 和 controller controls 混在一起但没有合理父子结构。
- 把所有 39 个样本的互斥拓扑强行拼成一个怪物设备。
- adopted source 没有映射到具体 helper，只是因为样本是 5 星就把不兼容部件拼进当前 family。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review. 建议审核时先决定是否拆分 DJ 子模板。未进入模板实现阶段。 |
