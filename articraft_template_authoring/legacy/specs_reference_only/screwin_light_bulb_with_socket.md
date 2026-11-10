# Screwin Light Bulb With Socket Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `screwin_light_bulb_with_socket` |
| template path | `agent/templates/screwin_light_bulb_with_socket.py` |
| test path | `tests/agent/test_screwin_light_bulb_with_socket_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 48 |
| read_count | 48 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below; service boxes, guard cages, and calibration rigs are gated variants, not mandatory clutter |

## 核心身份
螺口灯泡与灯座组件，必须包含 socket/fixture、socket 内螺纹或 threaded insert、灯泡螺口金属套、外螺纹、灯泡玻璃/发光体，以及沿灯座中心轴旋入的 screw motion。默认成熟域是 Edison screw bulb in socket：socket 固定，bulb 作为可动组件绕 Z 轴旋转并可选沿螺距轴向推进。simple spin 可以作为轻量模型，但推荐 `threaded_turn_lift` 记录 pitch、turns、insertion depth，避免灯泡旋转方向、轴向推进和接触点语义错误。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_screwin_light_bulb_with_socket_0001` | `data/records/rec_screwin_light_bulb_with_socket_0001/revisions/rev_000001/model.py:L66-L138` | ring geometry、helix points、coil/filament helpers |
| S2 | `rec_screwin_light_bulb_with_socket_0001` | `data/records/rec_screwin_light_bulb_with_socket_0001/revisions/rev_000001/model.py:L141-L201` | socket rings、ribs、contacts |
| S3 | `rec_screwin_light_bulb_with_socket_0001` | `data/records/rec_screwin_light_bulb_with_socket_0001/revisions/rev_000001/model.py:L203-L345` | bulb body, screw sleeve, helical bulb thread, contact, glass, filament assembly |
| S4 | `rec_screwin_light_bulb_with_socket_0001` | `data/records/rec_screwin_light_bulb_with_socket_0001/revisions/rev_000001/model.py:L347-L374` | bulb_screw revolute and fixed bulb glass/filament joints |
| S5 | `rec_screwin_light_bulb_with_socket_1dc69a231a07414994cd08d1fb1f1513` | `data/records/rec_screwin_light_bulb_with_socket_1dc69a231a07414994cd08d1fb1f1513/revisions/rev_000001/model.py:L22-L136` | THREAD_PITCH / THREAD_TRAVEL constants and threaded helpers |
| S6 | `rec_screwin_light_bulb_with_socket_1dc69a231a07414994cd08d1fb1f1513` | `data/records/rec_screwin_light_bulb_with_socket_1dc69a231a07414994cd08d1fb1f1513/revisions/rev_000001/model.py:L139-L246` | socket shell、brass liner、internal thread、contacts、set screws |
| S7 | `rec_screwin_light_bulb_with_socket_1dc69a231a07414994cd08d1fb1f1513` | `data/records/rec_screwin_light_bulb_with_socket_1dc69a231a07414994cd08d1fb1f1513/revisions/rev_000001/model.py:L247-L423` | hidden thread axis, bulb sleeve/thread/contact/glass/filament, screw_rotation + thread_advance |
| S8 | `rec_screwin_light_bulb_with_socket_df6bc323aa9243aeb314e9ea467118d6` | `data/records/rec_screwin_light_bulb_with_socket_df6bc323aa9243aeb314e9ea467118d6/revisions/rev_000001/model.py:L51-L155` | housing shell, threaded insert shell, bulb glass, male/female thread helpers |
| S9 | `rec_screwin_light_bulb_with_socket_df6bc323aa9243aeb314e9ea467118d6` | `data/records/rec_screwin_light_bulb_with_socket_df6bc323aa9243aeb314e9ea467118d6/revisions/rev_000001/model.py:L156-L377` | field-service box, collar, cable gland, hinge brackets, terminal block, service door |
| S10 | `rec_screwin_light_bulb_with_socket_df6bc323aa9243aeb314e9ea467118d6` | `data/records/rec_screwin_light_bulb_with_socket_df6bc323aa9243aeb314e9ea467118d6/revisions/rev_000001/model.py:L379-L469` | bulb part, service door hinge, insert_to_bulb screw joint |
| S11 | `rec_screwin_light_bulb_with_socket_e81c7386027e4833bc5699a7e434716e` | `data/records/rec_screwin_light_bulb_with_socket_e81c7386027e4833bc5699a7e434716e/revisions/rev_000001/model.py:L20-L159` | PITCH/TURN_LIMIT and threaded cylinder / hollow threaded collar helpers |
| S12 | `rec_screwin_light_bulb_with_socket_e81c7386027e4833bc5699a7e434716e` | `data/records/rec_screwin_light_bulb_with_socket_e81c7386027e4833bc5699a7e434716e/revisions/rev_000001/model.py:L219-L352` | calibration socket base, thread collar, contact, index ring joint |
| S13 | `rec_screwin_light_bulb_with_socket_e81c7386027e4833bc5699a7e434716e` | `data/records/rec_screwin_light_bulb_with_socket_e81c7386027e4833bc5699a7e434716e/revisions/rev_000001/model.py:L354-L505` | adjustment screws, bulb_turn revolute, bulb prismatic thread advance |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `socket_body` / `fixture_body` | 灯座外壳，可为陶瓷座、服务盒、校准夹具或带护罩 fixture | `socket_style`, `socket_outer_radius`, `socket_height`, `fixture_box_size` | S2 / S6 / S8 / S9 / S12 |
| `threaded_insert` / `socket_liner` | 内部金属螺纹套或 threaded collar，是 bulb screw 的固定父件 | `thread_standard`, `socket_inner_radius`, `insert_height`, `internal_thread_depth` | S6 / S8 / S11 / S12 |
| `internal_thread` | socket 内螺纹/螺旋槽，与 bulb 外螺纹共轴 | `thread_pitch`, `thread_turns`, `thread_clearance` | S6 / S8 / S11 / S12 |
| `center_contact` / `terminal_contacts` | 底部中心触点、侧触片、terminal block，fixed to socket | `contact_style`, `contact_radius`, `terminal_style` | S2 / S6 / S9 / S12 |
| `bulb_screw_sleeve` | 灯泡金属螺口套，是 bulb moving assembly 的机械接口 | `bulb_base_radius`, `base_height`, `base_band_count` | S3 / S7 / S10 / S13 |
| `external_thread` | bulb 外螺纹，必须 fit socket internal thread | `thread_pitch`, `thread_turns`, `thread_profile_height` | S3 / S7 / S10 / S13 |
| `bulb_contact_button` | bulb 底部中心触点，closed pose 应接近 socket center contact | `button_radius`, `contact_gap_closed` | S3 / S7 / S10 / S13 |
| `bulb_glass` / `envelope` | 玻璃泡壳，可为 A bulb、globe、candle、tubular、frosted LED dome | `bulb_profile`, `glass_radius`, `glass_height`, `glass_material` | S3 / S7 / S10 / S13 |
| `filament_or_led` | 灯丝、LED 柱或发光芯片，fixed to bulb/glass assembly | `emitter_style`, `filament_turns`, `support_wire_count` | S1 / S3 / S7 |
| `service_door` | 维修盒盖，optional，只在 field-service style 中启用 | `has_service_door`, `door_open_angle` | S9 / S10 |
| `index_ring` / `adjustment_screws` | 校准 socket 的刻度环、X/Y 调整螺钉，optional gated | `has_index_ring`, `has_adjustment_screws`, `adjustment_travel` | S12 / S13 |
| `guard_cage` / `shade_mount` | 护罩、灯罩安装环或 cage，optional fixed to fixture | `guard_style`, `shade_ring_radius` | S8 / S9 |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `socket_to_bulb_screw` / `bulb_screw` | continuous or revolute | `(0, 0, 1)` | socket/thread centerline | continuous or `[0, screw_turns * 2pi]` | simple spin model 的螺入旋转 | S4 / S10 |
| `screw_rotation` / `bulb_turn` | revolute | `(0, 0, 1)` | socket thread axis | `[0, screw_turns * 2pi]` | threaded model 的旋转 DOF | S7 / S13 |
| `thread_advance` / `bulb_turn_to_bulb` | prismatic | `(0, 0, 1)` or `(0, 0, -1)` branch-specific | same thread axis | `[0, insertion_depth]` | threaded model 的轴向推进，travel 与 pitch 一致 | S7 / S13 |
| `socket_to_insert` | fixed | n/a | socket collar datum | n/a | threaded insert 固定在 socket 中 | S6 / S10 |
| `bulb_to_glass` | fixed | n/a | bulb neck/glass base | n/a | glass envelope 随 bulb screw sleeve 运动 | S4 / S7 |
| `bulb_to_filament` | fixed | n/a | emitter supports inside glass | n/a | filament/LED 随 bulb 运动并留在玻璃内部 | S4 / S7 |
| `service_door_hinge` | revolute | `(1, 0, 0)` or `(0, 1, 0)` | service box side hinge | `[0, 1.7]` rad typical | service box cover，optional | S9 / S10 |
| `index_ring_spin` | revolute | `(0, 0, 1)` | socket top collar | limited or continuous | calibration index ring，optional | S12 |
| `adjustment_screw_x/y` | prismatic | `(1,0,0)` / `(0,1,0)` | screw guide centerlines | small travel | calibration screws，optional gated | S13 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `socket_style` | enum | `ceramic_socket` / `field_service_box` / `calibration_fixture` / `guarded_fixture` | `ceramic_socket` | drives fixture body and optional branches | S2 / S6 / S9 / S12 |
| `bulb_profile` | enum | `a_bulb` / `globe` / `candle` / `tubular` / `frosted_led` | `a_bulb` | drives glass dimensions and emitter style | S3 / S7 / S10 / S13 |
| `thread_standard` | enum | `E12` / `E14` / `E26` / `E27` | `E26` | maps to base radius, pitch, insertion depth ranges | S5 / S6 / S11 |
| `thread_pitch` | float | `0.002-0.006` | derived by standard | sets `insertion_depth = thread_pitch * screw_turns` | S5 / S7 / S11 / S13 |
| `screw_turns` | float | `1.0-3.0` | sampled | turn limit = turns * 2pi | S5 / S7 / S11 / S13 |
| `insertion_depth` | float | derived | derived | pitch * turns; cap closed contact uses this depth | S7 / S13 |
| `socket_inner_radius` | float | derived | derived | `bulb_base_thread_outer_radius + thread_clearance` | S6 / S8 / S11 |
| `bulb_base_radius` | float | derived by standard | derived | must fit socket internal thread | S3 / S7 / S10 / S13 |
| `thread_clearance` | float | `0.0006-0.0025` | sampled | positive clearance between male/female threads | S6 / S8 / S11 |
| `motion_model` | enum | `simple_spin` / `threaded_turn_lift` | `threaded_turn_lift` | selects one joint or revolute+prismatic pair | S4 / S7 / S10 / S13 |
| `contact_gap_closed` | float | `0.0-0.003` | sampled | closed pose bulb button near socket center contact | S2 / S3 / S6 |
| `has_service_door` | bool | `true` / `false` | derived | true only for `field_service_box` | S9 / S10 |
| `has_adjustment_screws` | bool | `true` / `false` | derived | true only for `calibration_fixture` | S12 / S13 |
| `guard_style` | enum | `none` / `wire_cage` / `shade_ring` / `protective_collar` | `none` | fixed to socket/fixture, outside bulb screw envelope | S8 / S9 |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| socket body | ceramic cylinder / service box / calibration fixture / guarded fixture | no | yes | `socket_style` | 外壳拓扑和 optional joints 完全不同 |
| thread standard | E12 / E14 / E26 / E27-like proportions | no | yes | `thread_standard` | 半径、pitch、insertion depth 要一起变 |
| screw motion | pure spin / rotation + axial advance | no | yes | `motion_model` | 关节语义不同 |
| bulb glass | A bulb / globe / candle / tubular / LED dome | no | yes | `bulb_profile` | 玻璃外形不是简单 scale |
| emitter | filament coil / LED column / simple glowing core | no | yes | `emitter_style` | 必须固定在 glass 内部 |
| service features | door / terminal block / cable gland / no service access | no | yes | `has_service_door`, `terminal_style` | field-service branch 才合法 |
| calibration features | index ring / adjustment screws / none | no | yes | `has_index_ring`, `has_adjustment_screws` | 校准夹具 branch 才合法 |

## 组合逻辑（Composition Logic）
1. 先采 `socket_style` 与 `thread_standard`，建立固定 socket/root 和中心 screw axis。所有 socket rings、liner、contacts 都从该轴派生。
2. 根据 `thread_standard` 派生 `bulb_base_radius`、`socket_inner_radius`、`thread_pitch`、`thread_turns`、`insertion_depth`。不得分别随机采 male/female thread 半径。
3. 生成 socket threaded insert：inner thread radius = bulb outer thread radius + clearance；insert height >= insertion_depth + contact_margin。
4. 生成 bulb moving assembly：screw sleeve、external thread、contact button、glass、emitter 都挂在同一 moving chain 上。
5. bulb glass 从 screw sleeve 上方派生，closed pose 时玻璃必须在 socket 外侧上方，不得嵌入 socket body。
6. `motion_model=simple_spin` 时使用 `bulb_screw` continuous/revolute，仍必须保持 closed pose seated。
7. `motion_model=threaded_turn_lift` 时使用 hidden/thread axis 或 intermediate link：`screw_rotation` 绕 Z，`thread_advance` 沿 Z，travel = `thread_pitch * screw_turns`。根据坐标约定可向下插入或向上退出，但必须在 metadata 中清楚。
8. contact button closed pose 与 socket center contact gap <= `contact_gap_closed`，不能穿过 terminal block。
9. service box、door、terminal block、cable gland 只在 `field_service_box` branch；index ring/adjustment screws 只在 `calibration_fixture` branch；guard cage 必须避开 bulb screw envelope。

## 已有模板写法参考
| 模板文件 | 可参考写法 |
|---|---|
| `agent/templates/ceiling_light_fixture_adjustable.py` | light fixture body, bulb/glass proportions, fixture-mounted optional hardware |
| `agent/templates/coaxial_rotary_stack.py` | coaxial screw/rotation axis conventions and nested rotary children |
| `agent/templates/camera_lens.py` | concentric threaded-looking rings, grip bands, radial detail arrays |
| `agent/templates/tackle_box_with_simple_hinged_lid.py` | service door hinge and latch details for field-service socket branch |


## 约束
- socket axis、internal thread、bulb external thread、screw joint axis 必须共轴。
- bulb moving assembly 必须包含 screw sleeve、external thread、contact button、glass、emitter。
- `threaded_turn_lift` 的 axial travel 必须等于 pitch * turns，且与 rotation limit 对应。
- bulb closed pose 必须让 contact button 靠近 center contact，不能漂浮或穿过 socket bottom。
- glass envelope 必须位于 socket 上方并包住 filament/LED，不得与 socket body 大面积穿模。
- service door、index ring、adjustment screws 都是 gated optional，不能出现在普通 ceramic socket 中。
- guard cage/shape ring 必须固定到 socket，并避开 bulb 旋入/旋出路径。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | socket + threaded insert/internal thread + bulb screw sleeve + glass present |
| coaxiality | male thread, female thread, screw joint axes aligned with socket centerline |
| thread fit | socket inner radius > bulb thread outer radius + clearance_min |
| screw motion | simple_spin has one screw joint; threaded model has rotation + prismatic advance |
| pitch consistency | `insertion_depth ~= thread_pitch * screw_turns` for threaded model |
| contact semantics | closed pose contact button near socket center contact, not far above/floating |
| moving group | bulb sleeve/thread/contact/glass/emitter move together |
| emitter containment | filament/LED inside glass envelope |
| optional compatibility | service/calibration/guard branches only with compatible `socket_style` |
| no floating | socket liner、contacts、door、guard、bulb details attached or constrained |

## Reject cases
- 灯泡和灯座只是两个静态物体，没有 screw joint。
- bulb 旋转轴不在 socket 中心轴，或螺纹不同轴。
- bulb contact button 和 socket contact 相距很远，closed pose 悬空。
- threaded model 没有 axial advance 或 pitch/travel 不一致。
- glass/filament 留在 socket root 上，bulb 旋转时不随 bulb 移动。
- service door、adjustment screw、guard cage 悬空或穿过 bulb screw path。
- 普通 socket 被塞入校准 rig/field-service box 全部细节，导致语义混乱。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
