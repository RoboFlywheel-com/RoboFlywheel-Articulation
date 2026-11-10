# Casino Machine Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `casino_machine` |
| template path | `agent/templates/casino_machine.py` |
| test path | `tests/agent/test_casino_machine_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 16 |
| read_count | 16 |
| read_scope | all 5-star samples in this category: `model.py` / `revision.json` / `record.json` / `prompt.txt` were read |
| samples_adopted_as_module_sources | 6 |
| samples_read_but_not_adopted | 10 |
| source_index_policy | only adopted reusable snippets are indexed below |

全量阅读后的结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| reel slot cabinet with spinning reel(s) | 8 | one/three/five reels, CONTINUOUS reel axis usually horizontal, plus button/door/lever |
| bar-top / video poker terminal | 4 | shallow cabinet, screen/control shelf, tray flap or selector knob, prismatic buttons |
| slant-top / belly-door terminal | 3 | angled screen/deck, belly/cashbox door REVOLUTE, button PRISMATIC, knob CONTINUOUS |
| lever / side handle slot machine | 2 | side lever REVOLUTE plus spinning reels and payout tray |
| service / payout openings | 13 | service panel, cash door, tray flap, bill flap, maintenance panel as REVOLUTE |

被采纳样本逐条标注：
- `rec_casino_machine_0dc07bf220f3445398c77007f2a4ade3` — adopted：modern five-reel cabinet, reel window, upper display, spin button, maintenance panel。
- `rec_casino_machine_04dbcc128faa4a12a0cd9eda80de5f1f` — adopted：bar-top video poker terminal, cadquery cabinet, tray flap, prismatic button。
- `rec_casino_machine_a5d926cbd53d4a309199969ad8856d21` — adopted：three independent reel parts, two buttons, cashbox door。
- `rec_casino_machine_b7a9b3572cfb45ec8a7eb5ec3a7ed453` — adopted：classic side handle slot, three reels, coin tray door。
- `rec_casino_machine_cfba59645a80411f8bed2072f9a9bfcf` — adopted：window glass fixed part, side lever, payout tray flap, reel helper。
- `rec_casino_machine_e60bb68099834916986dbbf2af56a85d` — adopted：slant-top cabinet shell, belly door, spin button, volume knob。
- Remaining 10 samples — read but not adopted: same cabinet/reel/button/door/knob families or only axis sign/material/mesh implementation variants.

## 核心身份
`casino_machine` 是独立或吧台式博彩终端：必须有一个静态 cabinet，正面有 screen/reel window/control deck/payout area 等 casino-machine 识别面，并至少包含一个可交互机构，例如 spinning reel、prismatic push button、side pull lever、cash/service door 或 payout tray flap。默认成熟域以 slot/video-poker cabinet 为主，reels、buttons、lever、door/tray 可按模块组合，但不能退化成普通 ATM、售货机或显示器。

边界：
- 不包括 arcade cabinet：若没有 casino reel、payout、coin/bill、spin button 或 gambling controls，则出界。
- 不混入 vending machine：透明货架、商品 dispenser 不是核心。
- 不混入 generic kiosk：必须有 casino/slot/video poker identity。
- Reels 可以是 baked visual 或 independent spinning parts，但若声明 reel motion，必须有 CONTINUOUS joint。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_casino_machine_0dc07bf220f3445398c77007f2a4ade3` | `data/records/rec_casino_machine_0dc07bf220f3445398c77007f2a4ade3/revisions/rev_000001/model.py:L30-L41,L54-L423` | broad upright cabinet, reel_window/upper_display FIXED parts, spin_button PRISMATIC, maintenance_panel REVOLUTE |
| S2 | `rec_casino_machine_04dbcc128faa4a12a0cd9eda80de5f1f` | `data/records/rec_casino_machine_04dbcc128faa4a12a0cd9eda80de5f1f/revisions/rev_000001/model.py:L27-L99,L103-L156` | bar-top cadquery cabinet, tray flap REVOLUTE, button cap/deck shapes |
| S3 | `rec_casino_machine_a5d926cbd53d4a309199969ad8856d21` | `data/records/rec_casino_machine_a5d926cbd53d4a309199969ad8856d21/revisions/rev_000001/model.py:L26-L146,L160-L443` | three reel part helper, button helper, cashbox door, multi-reel CONTINUOUS joints |
| S4 | `rec_casino_machine_b7a9b3572cfb45ec8a7eb5ec3a7ed453` | `data/records/rec_casino_machine_b7a9b3572cfb45ec8a7eb5ec3a7ed453/revisions/rev_000001/model.py:L24-L107,L114-L415` | side handle lever, reel part helper, coin tray door |
| S5 | `rec_casino_machine_cfba59645a80411f8bed2072f9a9bfcf` | `data/records/rec_casino_machine_cfba59645a80411f8bed2072f9a9bfcf/revisions/rev_000001/model.py:L24-L71,L86-L382` | window glass FIXED, side lever REVOLUTE, payout tray flap REVOLUTE, reel visual helper |
| S6 | `rec_casino_machine_e60bb68099834916986dbbf2af56a85d` | `data/records/rec_casino_machine_e60bb68099834916986dbbf2af56a85d/revisions/rev_000001/model.py:L25-L115,L143-L414` | slant-top cabinet shell, belly door, spin button, volume knob |

## 槽位 + 候选模块表

### Slot A：cabinet_body
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `upright_reel_cabinet` | S1 | `model.py:L54-L257` | eligible if compatible | tall front cabinet with reel window, upper display, lower controls |
| `bar_top_video_poker` | S2 | `model.py:L27-L143` | eligible if compatible | shallow bar-top cabinet, screen and short control shelf |
| `slant_top_terminal` | S6 | `model.py:L95-L288` | eligible if compatible | angled screen/control deck and belly service area |
| `classic_lever_slot` | S4 | `model.py:L114-L270` | eligible if compatible | upright slot with side lever mount and coin tray area |

### Slot B：game_display_or_reels
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `five_reel_window` | S1 | `model.py:L269-L302` | eligible if compatible | separate reel_window + upper display fixed modules; reel joint exists under cabinet |
| `three_independent_reels` | S3 | `model.py:L92-L126,L382-L406` | eligible if compatible | left/center/right reel parts, each CONTINUOUS |
| `single_window_glass_reel` | S5 | `model.py:L39-L71,L262-L278` | eligible if compatible | fixed window glass over internal reel helper |
| `screen_only_video_poker` | S2 | `model.py:L111-L143` | eligible if compatible | screen/control-panel visual, no exposed spinning reel |

### Slot C：controls_and_openings
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `spin_button_and_service_panel` | S1 | `model.py:L360-L423` | eligible if compatible | prismatic spin_button + rear/side maintenance_panel REVOLUTE |
| `tray_flap_and_button` | S2 | `model.py:L143-L156` | eligible if compatible | payout tray flap REVOLUTE plus prismatic button family |
| `side_lever_and_coin_door` | S4 | `model.py:L307-L415` | eligible if compatible | pull lever REVOLUTE and coin tray door REVOLUTE |
| `belly_door_button_knob` | S6 | `model.py:L288-L414` | eligible if compatible | belly_door REVOLUTE + spin_button PRISMATIC + volume_knob CONTINUOUS |
| `payout_tray_side_lever` | S5 | `model.py:L305-L382` | eligible if compatible | side lever + payout tray flap, both REVOLUTE |

## 槽位图（slot graph）
pattern = `mixed`

```
[Slot A cabinet_body]
      ├── FIXED / baked --> [Slot B display/window/reel fascia]
      ├── optional CONTINUOUS --> [Slot B reel_i]
      ├── PRISMATIC --> [Slot C push_button_i]
      ├── REVOLUTE --> [Slot C service/cash/tray door]
      └── optional REVOLUTE/CONTINUOUS --> [Slot C side_lever or knob]
```

主约束基准是 cabinet front plane 和 control deck plane。按钮沿 deck normal 滑动，tray/door hinge 挂在 panel edge，reel axis 由 reel window 横向轴派生。

## 部件（Parts）

### Slot A / cabinet_body
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `cabinet` / `base_cabinet` | ~8-35 | 主机柜，包括 screen surround、control deck、trim、payout recess | S1 / S2 / S4 / S6 |

### Slot B / game_display_or_reels
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `reel_window` / `window_glass` | ~1-4 | 固定透明/边框窗口件 | S1 / S5 |
| `upper_display` | ~1-3 | 顶部显示/灯箱 | S1 |
| `reel`, `left_reel`, `center_reel`, `right_reel` | ~4-10 each | 可自旋 reel drum / symbol band | S3 / S4 / S5 |

### Slot C / controls_and_openings
| part | visual_count | 描述 | 来源 |
|---|---:|---|---|
| `spin_button` / `button` | ~2-4 | prismatic push button | S1 / S2 / S3 / S6 |
| `service_panel` / `cashbox_door` / `belly_door` | ~3-6 | hinged access door | S1 / S3 / S6 |
| `tray_flap` / `coin_tray_door` / `payout_tray_flap` | ~1-5 | payout tray hinged flap | S2 / S4 / S5 |
| `side_handle` / `side_lever` | ~4-6 | side pull lever, revolute around side-axis | S4 / S5 |
| `volume_knob` / `selector_knob` | ~2-4 | continuous rotary knob | S6 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `reel_i_spin` | CONTINUOUS | A.cabinet | B.reel_i | `(1,0,0)` or panel-local horizontal | unlimited | slot reel 横轴自旋 | S1 / S3 / S4 / S5 |
| `button_i_press` | PRISMATIC | A.cabinet or control shelf | C.button_i | deck/front normal, typically `(0,0,-1)` | `[0, 0.04]` | 按钮沿面板法线短行程按下 | S1 / S2 / S3 / S6 |
| `service_door_hinge` | REVOLUTE | A.cabinet | C.service/cash/belly door | panel vertical edge `(0,0,±1)` or local hinge edge | `[0, 1.35]` | 维修/现金门侧开 | S1 / S3 / S6 |
| `tray_flap_hinge` | REVOLUTE | A.cabinet | C.tray_flap | horizontal tray edge `(1,0,0)` / `(0,1,0)` | `[0, 1.1]` | payout tray 向外下翻 | S2 / S5 |
| `side_lever_pull` | REVOLUTE | A.cabinet | C.side_lever | side-local horizontal `(1,0,0)` or `(0,1,0)` | `[-0.75, 0.15]` | 拉杆向下/向前摆动 | S4 / S5 |
| `knob_spin` | CONTINUOUS | A.cabinet | C.knob | panel normal | unlimited | volume/selector knob 旋转 | S6 |
| `display_fixed` | FIXED | A.cabinet | B.window/display | n/a | n/a | 独立 display/window fixed part | S1 / S5 |

## 每槽位 Module Emits / Interfaces

本 spec 是 modular v1 早期写法；每个 slot/module 的 emitted parts、internal joints、upstream/downstream interface 已在「槽位 + 候选模块表」「槽位图」「部件（Parts）」「关节（Joints）」和 adopted source index 中给出。模板实现阶段必须把这些信息逐 module 显式落成 `ModuleBuild`、`InterfaceSpec` 和 `MatingContract`，不能只按全局部件清单拼装。

| emits | 描述 | 来源 |
|---|---|---|
| parts / visuals | 以各 slot candidate 的结构特征和「部件（Parts）」表为准；不动装饰优先作为 parent visual | adopted source index + slot table |
| internal joints | 以「关节（Joints）」表和 slot graph 中的 joint type / axis / range 为准 | adopted source index + joints table |
| upstream interface | 来自 slot graph 中的 parent face、hinge line、socket、rail、axis、contact plane 或 support policy | slot graph + source snippets |
| downstream interface | 消费相邻 slot 的 mating point / axis / face；必须在实现中转成真实 `InterfaceSpec` | slot graph + source snippets |
| mating contracts | 每个 separate moving child 和跨 slot 连接必须有可见支撑路径；captured pin / shaft / bearing overlap 需要局部 allow-overlap 理由 | validator + reject cases |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `cabinet_style` | enum | `upright_reel`, `bar_top`, `slant_top`, `classic_lever` | `upright_reel` | Slot A module | S1 / S2 / S4 / S6 |
| `game_face_style` | enum | `five_reel_window`, `three_reels`, `single_window_reel`, `screen_only` | `five_reel_window` | Slot B module; screen_only disables reel_count | S1 / S2 / S3 / S5 |
| `control_module` | enum | `spin_button_service`, `tray_flap_button`, `side_lever_coin_door`, `belly_button_knob`, `payout_lever` | `spin_button_service` | Slot C module | S1-S6 |
| `reel_count` | int | `{0,1,3,5}` | `5` | `0` only for screen_only; 3/5 spawn reel part+joint | S1 / S3 / S4 |
| `button_count` | int | `1..5` | `1` | copied prismatic buttons on deck; bounded by deck width | S1 / S2 / S3 |
| `cabinet_width` | float | `[0.55, 1.35]` | `0.9` | controls/reels spacing derived from cabinet width | S1 / S6 |
| `cabinet_height` | float | `[0.8, 2.1]` | `1.55` | style-specific clamp; bar_top shorter | S1 / S2 / S6 |
| `front_angle` | float | `[0, 0.45]` rad | `0.12` | slant_top uses high angle, upright clamps near 0 | S6 |
| `door_style` | enum | `none`, `service_panel`, `cashbox`, `belly`, `coin_tray`, `payout_tray` | `service_panel` | derived from control_module | S1 / S3 / S4 / S5 / S6 |
| `lever_style` | enum | `none`, `side_pull`, `selector_knob`, `volume_knob` | `none` | mutually exclusive with some compact bar-top layouts | S4 / S5 / S6 |

## Multiplicity / Copy Logic

- `reel_count`: `N_range={0,1,3,5}`, sampling domain=`discrete`; copied object=part+CONTINUOUS joint for exposed reels, or fixed/baked reel-window visuals for S1-style five-reel facade; placement=even horizontal row behind reel window; naming=`reel_i` / `reel_i_spin`; source=S1/S3/S4.
- `button_count`: `N_range=1..5`, sampling domain=`all integers`; copied object=button part+PRISMATIC joint; placement=even row on control deck; naming=`button_i` / `button_i_press`; source=S1/S2/S3.
- Decorative lights, symbol tick marks, cabinet trim screws, payout labels are module-local fixed visuals, not template-level count parameters.

## 拓扑多样性审计

总组合数：4 cabinet modules x 4 game-face modules x 5 control modules x reel_count/button_count branches = >80 legal combinations after gating.


| slot | candidate_count | 是否 >=3 | 备注 |
|---|---:|---|---|
| cabinet_body | 4 | yes | upright/bar-top/slant/classic |
| game_display_or_reels | 4 | yes | fixed display, one/three/five reel variants |
| controls_and_openings | 5 | yes | button, tray, door, lever, knob combinations |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| cabinet | upright tall / bar-top shallow / slant-top / classic lever slot | no | yes | `cabinet_style` | 主 silhouette 与 panel topology 差异大 |
| game face | screen-only / reel window / individual reels / fixed glass | no | yes | `game_face_style`, `reel_count` | 是否有 spinning reel 是拓扑差异 |
| controls | push buttons / side lever / selector knob / volume knob | no | yes | `control_module`, `lever_style` | joint type 不同 |
| doors/trays | service panel / cashbox / belly door / payout tray flap | no | yes | `door_style` | hinge axis/origin 与外形不同 |
| button caps | round / rectangular / ringed | partial | yes | `button_style` | 样本中 button geometry 有定性差异 |
| reel symbols/labels | none / symbol strips / glass overlay | partial | yes | `reel_visual_style` | 类别识别视觉，不只是颜色 |

## 组合逻辑（Composition Logic）
1. 由 `cabinet_style` 建立 cabinet envelope、front plane、control deck plane、reel/screen aperture。
2. `game_face_style` 在 front plane 内派生 window/display/reel origin；reel axis 必须平行于 reel row，不独立随机。
3. `button_count` 在 deck plane 上等距布置，PRISMATIC axis 沿 deck normal，行程受 deck thickness 限制。
4. Door/tray hinge 从对应 panel 边缘派生，opening sweep 避免穿 cabinet。
5. Lever/knob 只挂侧面或 panel normal，不和 reel/window 重叠。

## 已有模板写法参考
`prismatic_button` / `revolute_hinge` / `rotary_knob` / `display_panel`（仅参考写法）

## 约束
- cabinet 是唯一 root 承载件；所有 display/reel/control/door 都必须 parent 到 cabinet 或 cabinet shelf。
- 如果 `reel_count > 0`，必须有 reel identity visual；若 reel 是 part，必须有 CONTINUOUS joint。
- button PRISMATIC 行程必须短且沿 panel/deck normal。
- side lever 不能出现在纯 screen-only video poker 的正面中央；应挂侧面。
- door/tray hinge 必须贴 panel edge，不得漂浮在 cabinet 前方。

### Procedural Sampling / Sweep Plan

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊，不作为 anchor 或 reference seed。Sampling 先选择上游结构槽，再从 compatible 下游 candidate 集合中选择 module / multiplicity / module-local variant。

Compatibility matrix / gating：以「槽位图」「每槽位 Module Emits / Interfaces」「Validator」中定义的接口、joint 轴、支撑面、range 和互斥关系为准；不兼容组合必须在 sampler 或 `resolve_config` 中降级、重采样或拒绝，不能让 builder 后期失败。

Regression overrides：默认无。若未来 sweep 发现稳定失败组合，或 reviewer 指定固定回归样本，可以添加少量显式 regression seed，但必须写明 seed、组合和原因；不得用小型 curated / modulo 表作为主 seed domain。

Random sweep / viewer plan：首次模板验收跑 `uv run articraft template sweep-pipeline <slug>`，依赖 0、0-4、0-19、0-49 的 cumulative random seeds 检查 build、MatingContract、joint origin / axis / range、support、collision 和 。机械通过后 viewer 目检一小批随机 seed，重点看类别身份、比例、closed pose、bulky module、optional moving child、max multiplicity、captured-pin / bearing / hinge / rail 接口。


## Validator
| 检查项 | 标准 |
|---|---|
| identity | cabinet + casino control/display/reel/payout features present |
| interaction | 至少一个 PRISMATIC/REVOLUTE/CONTINUOUS interactive joint |
| reel joint | exposed spinning reels have CONTINUOUS joints with horizontal axis |
| button joint | push buttons have PRISMATIC joints with short range |
| hinge placement | service/tray/door origin lies on cabinet edge/recess |
| no floating | controls, doors, levers, reels parented to cabinet/shelf |
| multiplicity | reel_count and button_count produce stable names and non-overlapping spacing |
| diversity | cabinet_style/game_face_style/control_module branches covered |

## Reject cases
- 普通显示器、ATM、售货机，没有 casino machine 身份。
- reel visual 存在但没有轴或轴方向错误，导致像轮子或风扇。
- 按钮用 REVOLUTE 或长距离 PRISMATIC，运动不可信。
- door/tray/lever 漂浮或 hinge 不贴 cabinet。
- 所有变化只是颜色/贴图，没有 cabinet/control/reel 拓扑差异。
- reel/button count 导致互相重叠或超出 cabinet。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 等待人工审核；未进入模板实现阶段 |
