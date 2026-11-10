# Car Sunroof Cassette Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `car_sunroof_cassette` |
| template path | `agent/templates/car_sunroof_cassette.py` |
| test path | `tests/agent/test_car_sunroof_cassette_template.py` |
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
汽车天窗 cassette 是嵌入车顶开口的浅框架模块，必须有矩形 frame/rails 和至少一个 glass/panel/shade/slat 活动件沿轨道滑动或绕前缘/横向轴翻起。高分样本的核心不是普通窗户，而是带导轨、密封、滑鞋/托架和车顶模块比例的集成机构。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | rec_car_sunroof_cassette_0004 | `data/records/rec_car_sunroof_cassette_0004/revisions/rev_000001/model.py:L62-L268` | tilt-and-slide cassette frame、rails、slider shoes、glass seals、slide + tilt joints |
| S2 | rec_car_sunroof_cassette_0003 | `data/records/rec_car_sunroof_cassette_0003/revisions/rev_000001/model.py:L154-L215` | panoramic two-panel frame、center crossmember、shared guide rails |
| S3 | rec_car_sunroof_cassette_9d06cedb894f4871881ce240240f3d40 | `data/records/rec_car_sunroof_cassette_9d06cedb894f4871881ce240240f3d40/revisions/rev_000001/model.py:L26-L256` | panoramic glass panel with guide shoes plus independent sun shade prismatic slide |
| S4 | rec_car_sunroof_cassette_32c0b57f1c6b438aa3dbc0b8a3745760 | `data/records/rec_car_sunroof_cassette_32c0b57f1c6b438aa3dbc0b8a3745760/revisions/rev_000001/model.py:L28-L173` | lamella louvre frame and synchronized glass slat revolute joints |
| S5 | rec_car_sunroof_cassette_33cf7906e2db4400b0bf1746f37c1967 | `data/records/rec_car_sunroof_cassette_33cf7906e2db4400b0bf1746f37c1967/revisions/rev_000001/model.py:L38-L290` | retractable canvas frame, rear drum continuous joint, guided panel slide |
| S6 | rec_car_sunroof_cassette_1e1a282c22cd4b32894b49d483fd8782 | `data/records/rec_car_sunroof_cassette_1e1a282c22cd4b32894b49d483fd8782/revisions/rev_000001/model.py:L38-L244` | tilt-only glass panel and front wind deflector hinge |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| cassette_frame | required；浅矩形车顶框架，含 side rails、front/rear headers、seal lands、drain/channel details | frame_layout, frame_length, frame_width, rail_profile, seal_style | S1 / `data/records/rec_car_sunroof_cassette_0004/revisions/rev_000001/model.py:L62-L151`; S2 / `data/records/rec_car_sunroof_cassette_0003/revisions/rev_000001/model.py:L154-L195`; S3 / `data/records/rec_car_sunroof_cassette_9d06cedb894f4871881ce240240f3d40/revisions/rev_000001/model.py:L26-L125` |
| glass_panel | required for glass/hard-panel layouts；带 tinted glass、frit/seal、corner shoes 或 hinge ears | panel_variant, panel_count, glass_opacity, guide_shoe_count | S1 / `data/records/rec_car_sunroof_cassette_0004/revisions/rev_000001/model.py:L202-L249`; S3 / `data/records/rec_car_sunroof_cassette_9d06cedb894f4871881ce240240f3d40/revisions/rev_000001/model.py:L126-L192`; S6 / `data/records/rec_car_sunroof_cassette_1e1a282c22cd4b32894b49d483fd8782/revisions/rev_000001/model.py:L138-L195` |
| slider_carriage | optional；tilt-and-slide layout 中承载玻璃的滑台/滑鞋 | slider_style, shoe_spacing, slide_travel | S1 / `data/records/rec_car_sunroof_cassette_0004/revisions/rev_000001/model.py:L153-L200` |
| center_crossmember | optional；panoramic multi-panel cassette 的中梁 | panel_count, crossmember_width | S2 / `data/records/rec_car_sunroof_cassette_0003/revisions/rev_000001/model.py:L197-L215` |
| sun_shade | optional；玻璃下方独立内遮阳板/roller shade | shade_enabled, shade_style, shade_travel | S3 / `data/records/rec_car_sunroof_cassette_9d06cedb894f4871881ce240240f3d40/revisions/rev_000001/model.py:L193-L256` |
| glass_slat_i | optional；lamella/louvre layout 中多片同步翻转玻璃叶片 | slat_count, slat_spacing, panel_variant | S4 / `data/records/rec_car_sunroof_cassette_32c0b57f1c6b438aa3dbc0b8a3745760/revisions/rev_000001/model.py:L118-L173` |
| rear_drum / canvas_panel | optional；soft-top canvas layout 的卷轴和软帘 | panel_variant, drum_radius, canvas_travel | S5 / `data/records/rec_car_sunroof_cassette_33cf7906e2db4400b0bf1746f37c1967/revisions/rev_000001/model.py:L122-L290` |
| wind_deflector | optional；前缘扰流板，随 tilt/vent 打开 | deflector_enabled, deflector_angle | S6 / `data/records/rec_car_sunroof_cassette_1e1a282c22cd4b32894b49d483fd8782/revisions/rev_000001/model.py:L196-L244` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| panel_slide | prismatic | `(0, -1, 0)` / `(0, 1, 0)` / `(1, 0, 0)`，沿 cassette 纵向轨道 | frame rail 起点或 slider closed pose | `0.35-0.55` m 建议 | 玻璃或滑台沿轨道后退 | S1 / `data/records/rec_car_sunroof_cassette_0004/revisions/rev_000001/model.py:L251-L259`; S3 / `data/records/rec_car_sunroof_cassette_9d06cedb894f4871881ce240240f3d40/revisions/rev_000001/model.py:L238-L246` |
| panel_tilt | revolute | `(1, 0, 0)` 或 `(-1, 0, 0)` 横向轴 | 玻璃前缘/前 cross rail | `[0, 0.11-0.25]` rad | panel rear edge vent/tilt | S1 / `data/records/rec_car_sunroof_cassette_0004/revisions/rev_000001/model.py:L260-L268`; S6 / `data/records/rec_car_sunroof_cassette_1e1a282c22cd4b32894b49d483fd8782/revisions/rev_000001/model.py:L227-L235` |
| shade_slide | prismatic | 与 panel_slide 平行 | lower shade rail | `0.45-0.60` m | optional；独立内遮阳帘滑动 | S3 / `data/records/rec_car_sunroof_cassette_9d06cedb894f4871881ce240240f3d40/revisions/rev_000001/model.py:L247-L255` |
| slat_i_tilt | revolute with optional Mimic | `(1, 0, 0)` | 每片 lamella 侧边 pin 轴 | `[0, 0.92]` rad | optional；多片玻璃叶片同步翻开 | S4 / `data/records/rec_car_sunroof_cassette_32c0b57f1c6b438aa3dbc0b8a3745760/revisions/rev_000001/model.py:L160-L173` |
| rear_drum_spin | continuous | `(1, 0, 0)` | rear drum 轴 | continuous | optional；canvas soft-top 卷轴 | S5 / `data/records/rec_car_sunroof_cassette_33cf7906e2db4400b0bf1746f37c1967/revisions/rev_000001/model.py:L268-L276` |
| canvas_slide | prismatic | `(0, 1, 0)` | soft-top side channels | `[0, 0.52]` m | optional；canvas front bow 沿轨道收回 | S5 / `data/records/rec_car_sunroof_cassette_33cf7906e2db4400b0bf1746f37c1967/revisions/rev_000001/model.py:L277-L290` |
| deflector_hinge | revolute | `(-1, 0, 0)` | front deflector support | `[0, 0.58]` rad | optional；扰流板随前缘翻起 | S6 / `data/records/rec_car_sunroof_cassette_1e1a282c22cd4b32894b49d483fd8782/revisions/rev_000001/model.py:L236-L244` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| frame_layout | enum | `single_panel` / `panoramic_two_panel` / `lamella_louvre` / `soft_top_canvas` / `vent_only` | `single_panel` | 决定 panel parts 和 joint set | S1 / `data/records/rec_car_sunroof_cassette_0004/revisions/rev_000001/model.py:L62-L268`; S2 / `data/records/rec_car_sunroof_cassette_0003/revisions/rev_000001/model.py:L154-L215`; S4 / `data/records/rec_car_sunroof_cassette_32c0b57f1c6b438aa3dbc0b8a3745760/revisions/rev_000001/model.py:L28-L173`; S5 / `data/records/rec_car_sunroof_cassette_33cf7906e2db4400b0bf1746f37c1967/revisions/rev_000001/model.py:L38-L290` |
| motion_mode | enum | `slide_only` / `tilt_only` / `tilt_and_slide` / `lamella_tilt` / `canvas_roll_slide` | `tilt_and_slide` | 派生 joints：slide/tilt/shade/drum/slat | S1 / `data/records/rec_car_sunroof_cassette_0004/revisions/rev_000001/model.py:L251-L268`; S4 / `data/records/rec_car_sunroof_cassette_32c0b57f1c6b438aa3dbc0b8a3745760/revisions/rev_000001/model.py:L160-L173`; S5 / `data/records/rec_car_sunroof_cassette_33cf7906e2db4400b0bf1746f37c1967/revisions/rev_000001/model.py:L268-L290` |
| panel_variant | enum | `glass_lite` / `solid_hard_panel` / `canvas_soft_panel` / `glass_lamella_slats` | `glass_lite` | 决定 moving panel geometry | S3 / `data/records/rec_car_sunroof_cassette_9d06cedb894f4871881ce240240f3d40/revisions/rev_000001/model.py:L126-L192`; S4 / `data/records/rec_car_sunroof_cassette_32c0b57f1c6b438aa3dbc0b8a3745760/revisions/rev_000001/model.py:L118-L173`; S5 / `data/records/rec_car_sunroof_cassette_33cf7906e2db4400b0bf1746f37c1967/revisions/rev_000001/model.py:L165-L267` |
| panel_count | int | `1` / `2` | `1` | panoramic_two_panel 时为 2 并启用 center_crossmember | S2 / `data/records/rec_car_sunroof_cassette_0003/revisions/rev_000001/model.py:L154-L215` |
| slat_count | int | `4-6` | `5` | frame_layout = lamella_louvre 时使用 | S4 / `data/records/rec_car_sunroof_cassette_32c0b57f1c6b438aa3dbc0b8a3745760/revisions/rev_000001/model.py:L94-L173` |
| shade_enabled | bool | `true` / `false` | `false` | panoramic glass 默认可启用 | S3 / `data/records/rec_car_sunroof_cassette_9d06cedb894f4871881ce240240f3d40/revisions/rev_000001/model.py:L193-L255` |
| deflector_enabled | bool | `true` / `false` | `false` | tilt_only / tilt_and_slide 时可启用 | S6 / `data/records/rec_car_sunroof_cassette_1e1a282c22cd4b32894b49d483fd8782/revisions/rev_000001/model.py:L196-L244` |
| slide_travel | float | `0.30-0.60` | `0.45` | prismatic upper limit；不得超过 rail length | S1 / `data/records/rec_car_sunroof_cassette_0004/revisions/rev_000001/model.py:L251-L259`; S3 / `data/records/rec_car_sunroof_cassette_9d06cedb894f4871881ce240240f3d40/revisions/rev_000001/model.py:L238-L246` |
| tilt_angle_rad | float | `0.08-0.25` | `0.16` | revolute upper limit | S1 / `data/records/rec_car_sunroof_cassette_0004/revisions/rev_000001/model.py:L260-L268`; S6 / `data/records/rec_car_sunroof_cassette_1e1a282c22cd4b32894b49d483fd8782/revisions/rev_000001/model.py:L227-L235` |
| rail_profile | enum | `twin_channel` / `recessed_track` / `soft_top_channel` / `lamella_bushing` | `twin_channel` | frame rail visuals and containment checks | S1 / `data/records/rec_car_sunroof_cassette_0004/revisions/rev_000001/model.py:L105-L146`; S4 / `data/records/rec_car_sunroof_cassette_32c0b57f1c6b438aa3dbc0b8a3745760/revisions/rev_000001/model.py:L94-L117`; S5 / `data/records/rec_car_sunroof_cassette_33cf7906e2db4400b0bf1746f37c1967/revisions/rev_000001/model.py:L68-L115` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| cassette_frame | single rectangular / panoramic with crossmember / lamella bushing frame / soft-top rear drum frame | no | yes | frame_layout, rail_profile | frame 拓扑和轨道类型变化明显 |
| moving panel | glass pane / hard panel / canvas soft panel / multiple lamella slats | no | yes | panel_variant | 材料和拓扑不同，不能只调透明度 |
| motion | slide / tilt / tilt-and-slide / louvre mimic / canvas roll+slide | no | yes | motion_mode | joint set 不同 |
| guide hardware | corner shoes / slider carriage / side channels / bushing pins | no | yes | slider_style, rail_profile | 导向结构是类别识别部件 |
| shade | none / independent sliding fabric shade / roller shade | no | yes | shade_enabled, shade_style | 样本中有独立活动遮阳件 |
| wind deflector | none / hinged front strip | no | yes | deflector_enabled | 有无独立前缘扰流件是拓扑差异 |
| frame dimensions | none beyond roof-module aspect ratio | yes | no | frame_length, frame_width | 尺寸比例可连续表达 |

## 组合逻辑（Composition Logic）
1. 生成 cassette_frame：side rails、headers、seal lands、drain/channel visuals。
2. 根据 `frame_layout` 选择 moving elements：单 glass panel、双 panel、lamella slats、canvas panel 或 vent insert。
3. 根据 `motion_mode` 添加 slide、tilt、slat mimic、drum spin、shade slide、deflector hinge。
4. `tilt_and_slide` 建议链为 frame -> slider_carriage -> glass_panel；纯 slide 可直接 frame -> glass_panel。
5. guide shoes、frit、rubber seal、wear strips 优先作为 glass/frame 的 visual。
6. 多 panel/panoramic 布局添加 center_crossmember，且左右/前后 rail 对称。

## 已有模板写法参考
prismatic_slide / revolute_hinge / guide_shoe / gasket_strip / mimic_link

## 约束
- 必须存在 cassette_frame 和至少一个活动 panel/slat/shade。
- slide axis 必须平行于可见 guide rails。
- tilt axis 必须沿横向前缘/横梁，不能绕竖直轴翻开。
- slide_travel 不能超过 rail 有效长度。
- glass/panel 在 closed pose 应落在 seal land 内，不能完全悬空。
- lamella layout 中所有 slats 数量与 slat_count 一致，mimic 链统一方向。
- canvas layout 中 rear_drum_spin 和 canvas_slide 应同时存在。
- deflector 若启用，必须位于 frame front edge。

## Validator
| 检查项 | 标准 |
|---|---|
| required frame | `cassette_frame` 存在，且有 side rails/header/seal visuals |
| moving element | 至少一个 moving panel/slat/shade part |
| slide axis | prismatic axis 与 rail 方向平行 |
| tilt axis | panel_tilt/slat_tilt axis 为横向轴 |
| travel range | slide upper limit 小于 rail usable length |
| containment | closed pose panel 在 frame opening/rails 内 |
| mode consistency | motion_mode 与 joint set 一致 |
| shade consistency | shade_enabled 时有 shade part 和 shade_slide |
| deflector consistency | deflector_enabled 时有 front deflector revolute joint |
| part diversity | frame_layout、motion_mode、panel_variant、rail_profile 参数存在 |
| identity | 必须像汽车天窗 cassette，而不是普通窗户或玻璃门 |

## Reject cases
- 没有 cassette frame 或没有可见 guide rails。
- panel 滑动方向和轨道方向不一致。
- tilt joint 在玻璃中心或竖直轴，导致不像天窗 vent。
- panel/slat 漂浮在 frame 外。
- panoramic layout 没有 crossmember 或 panel 数不一致。
- lamella layout 没有每片 slat 的 revolute/mimic 逻辑。
- canvas layout 有卷轴但没有滑动前缘，或相反。
- 用普通矩形窗框替代车顶模块细节。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核 |
