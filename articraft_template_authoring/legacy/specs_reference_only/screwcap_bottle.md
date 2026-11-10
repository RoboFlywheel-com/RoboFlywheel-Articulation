# Screwcap Bottle Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `screwcap_bottle` |
| template path | `agent/templates/screwcap_bottle.py` |
| test path | `tests/agent/test_screwcap_bottle_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 37 |
| read_count | 37 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below; decorative bottle cages and unusual containers are sampled only when compatible with screwcap semantics |

## 核心身份
带螺纹旋盖的瓶子，必须包含瓶身、瓶颈/外螺纹、旋盖/内螺纹或裙边、以及围绕瓶颈中心轴的 cap screw motion。默认成熟域是 axis-aligned bottle with screw cap：瓶身和瓶颈共轴，cap 的内径、裙边高度、密封垫和螺纹都从瓶颈尺寸派生。运动可以是 simple continuous spin，也可以采用更成熟的 threaded turn + axial lift 双关节模型；若使用双关节，必须显式记录 pitch/turns/travel，避免“只旋转不沿螺纹上升”的语义错位。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_screwcap_bottle_0002` | `data/records/rec_screwcap_bottle_0002/revisions/rev_000001/model.py:L30-L94` | superellipse body sections、cap shell、knurl band helpers |
| S2 | `rec_screwcap_bottle_0002` | `data/records/rec_screwcap_bottle_0002/revisions/rev_000001/model.py:L105-L147` | bottle body、shoulder finish、neck finish、external thread bands、grip pads |
| S3 | `rec_screwcap_bottle_0002` | `data/records/rec_screwcap_bottle_0002/revisions/rev_000001/model.py:L256-L315` | cap shell、inner sleeve、cap thread bands、knurls、tether lug、cap_spin joint |
| S4 | `rec_screwcap_bottle_3b72f1b06e424f34a33ec81fc85feb89` | `data/records/rec_screwcap_bottle_3b72f1b06e424f34a33ec81fc85feb89/revisions/rev_000001/model.py:L28-L49` | helix point helper for true thread path |
| S5 | `rec_screwcap_bottle_3b72f1b06e424f34a33ec81fc85feb89` | `data/records/rec_screwcap_bottle_3b72f1b06e424f34a33ec81fc85feb89/revisions/rev_000001/model.py:L52-L236` | bottle shell、base ring、neck helical thread、cap shell、internal cap thread、grip rings |
| S6 | `rec_screwcap_bottle_3b72f1b06e424f34a33ec81fc85feb89` | `data/records/rec_screwcap_bottle_3b72f1b06e424f34a33ec81fc85feb89/revisions/rev_000001/model.py:L238-L263` | cap_lift prismatic + cap shell spin for thread advance semantics |
| S7 | `rec_screwcap_bottle_aa1625790e9e4236941bc4c2650955de` | `data/records/rec_screwcap_bottle_aa1625790e9e4236941bc4c2650955de/revisions/rev_000001/model.py:L58-L138` | explicit helical thread mesh and cap shell with knurls/windows |
| S8 | `rec_screwcap_bottle_aa1625790e9e4236941bc4c2650955de` | `data/records/rec_screwcap_bottle_aa1625790e9e4236941bc4c2650955de/revisions/rev_000001/model.py:L141-L263` | rugged body rails、external neck thread、cap internal thread and index mark |
| S9 | `rec_screwcap_bottle_aa1625790e9e4236941bc4c2650955de` | `data/records/rec_screwcap_bottle_aa1625790e9e4236941bc4c2650955de/revisions/rev_000001/model.py:L265-L282` | body_to_cap_turn revolute + cap_thread_lift prismatic |
| S10 | `rec_screwcap_bottle_6b2c1386d07447bfa26806abf78b4935` | `data/records/rec_screwcap_bottle_6b2c1386d07447bfa26806abf78b4935/revisions/rev_000001/model.py:L35-L126` | lower/middle/neck/cap lathe shell helpers for segmented bottle profiles |
| S11 | `rec_screwcap_bottle_6b2c1386d07447bfa26806abf78b4935` | `data/records/rec_screwcap_bottle_6b2c1386d07447bfa26806abf78b4935/revisions/rev_000001/model.py:L140-L255` | segmented lower/middle/neck bottle, thread turns, cap seal plug, grip ribs |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `bottle_body` | 主瓶身，可为圆形、superellipse、slender、rugged 或分段 body | `bottle_profile`, `body_cross_section`, `body_height`, `body_radius`, `wall_thickness` | S1 / S2 / S5 / S10 / S11 |
| `shoulder` / `middle_body` | 从 body 到 neck 的肩部、腰线或分段中段 | `shoulder_style`, `shoulder_height`, `middle_height` | S2 / S5 / S10 / S11 |
| `neck_finish` | 瓶颈圆柱、stop bead、finish ring，是 cap 的父轴参考 | `neck_radius`, `neck_height`, `finish_bead_radius` | S2 / S5 / S8 / S11 |
| `external_thread` | 瓶颈外螺纹，可为 helical mesh 或 thread bands | `thread_pitch`, `thread_turns`, `thread_radius`, `thread_height` | S2 / S4 / S5 / S7 / S8 / S11 |
| `screw_cap` | 旋盖外壳，包含顶盖、裙边、外 grip 或 rugged shell | `cap_style`, `cap_height`, `cap_outer_radius`, `cap_skirt_height` | S3 / S5 / S7 / S8 / S11 |
| `internal_thread` | cap 内螺纹或内圈凸起，必须与 external thread 共轴 | `internal_thread_radius`, `thread_clearance`, `thread_lead` | S3 / S5 / S7 / S8 |
| `seal_liner` / `plug` | cap 内部密封垫、塞头或压圈，fixed to cap | `seal_style`, `seal_thickness`, `plug_depth` | S3 / S5 / S11 |
| `knurl_grips` | cap knurls、grip ribs、index marks，fixed to cap | `knurl_count`, `grip_style`, `index_mark` | S1 / S3 / S5 / S7 / S8 / S11 |
| `armor_or_tether` | rugged cage、base boot、tether lug 等 optional fixed details | `has_armor`, `has_tether`, `armor_style` | S3 / S8 |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `body_to_cap_spin` / `cap_spin` | continuous or revolute | `(0, 0, 1)` | neck center axis at thread datum | continuous or `[0, screw_turns * 2pi]` | simple screwcap rotation model | S3 |
| `body_to_cap_turn` | revolute | `(0, 0, 1)` | neck center axis at thread datum | `[0, screw_turns * 2pi]` | threaded model 的旋转 DOF | S9 |
| `cap_thread_lift` / `body_to_cap_lift` | prismatic | `(0, 0, 1)` | same neck axis or hidden cap axis | `[0, thread_travel]` | threaded model 的轴向升降，travel = pitch * turns | S6 / S9 |
| `cap_to_seal_liner` | fixed | n/a | cap inner top center | n/a | 密封垫随 cap 运动 | S3 / S11 |
| `body_segment_fixed` | fixed | n/a | segment interfaces | n/a | lower/middle/neck body 分段固定 | S11 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `bottle_profile` | enum | `cylindrical_water` / `slender_cosmetic` / `wide_jar` / `rugged_rect` / `squeeze_bottle` | `cylindrical_water` | drives body radius/height/shoulder and cap proportions | S1 / S2 / S5 / S10 / S11 |
| `body_cross_section` | enum | `round` / `superellipse` / `rounded_rect` | `round` | rugged/squeeze may use superellipse | S1 / S2 |
| `body_height` | float | `0.12-0.34` | sampled | root bottle scale; neck starts at top minus shoulder/neck | S2 / S5 / S10 / S11 |
| `body_radius` | float | `0.025-0.075` | sampled | constrains neck and cap radius | S2 / S5 / S10 / S11 |
| `neck_radius` | float | `0.28-0.55 * body_radius` | derived | `cap_inner_radius = neck_outer_thread_radius + thread_clearance` | S2 / S5 / S8 / S11 |
| `neck_height` | float | `0.018-0.065` | sampled | must exceed thread height + finish bead | S2 / S5 / S8 / S11 |
| `thread_pitch` | float | `0.002-0.006` | sampled | `thread_travel = thread_pitch * thread_turns` | S4 / S5 / S7 / S9 |
| `thread_turns` | float | `1.0-3.5` | sampled | determines cap turn limit and lift travel | S5 / S8 / S11 |
| `thread_clearance` | float | `0.0008-0.003` | sampled | cap internal thread radius clearance | S5 / S7 / S8 |
| `cap_style` | enum | `smooth` / `knurled` / `ribbed` / `rugged_windowed` / `tethered` | `knurled` | drives cap shell and grip details | S3 / S5 / S7 / S8 / S11 |
| `cap_height` | float | derived | derived | `thread_height + seal_thickness + top_thickness + grip_margin` | S3 / S5 / S11 |
| `cap_outer_radius` | float | derived | derived | `neck_radius + thread_height + wall_thickness + grip_depth` | S3 / S5 / S7 / S8 |
| `screw_motion_model` | enum | `simple_spin` / `threaded_turn_lift` | `threaded_turn_lift` | selects one joint or revolute+prismatic pair | S3 / S6 / S9 |
| `has_armor` | bool | `true` / `false` | sampled | allowed only if body profile supports rugged cage/base boot | S8 |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| body profile | cylinder / superellipse / segmented / rugged / jar-like | no | yes | `bottle_profile`, `body_cross_section` | 只改 radius/height 不够表达外形类别 |
| shoulder/neck finish | short neck / long neck / bead ring / segmented finish | partly | yes | `shoulder_style`, `neck_height` | neck geometry 直接影响 cap fit |
| thread representation | bands / helical mesh / visual ridges | no | yes | `thread_representation` | helical 可用时更成熟，但 bands 可作为 fast path |
| cap shell | smooth / knurled / ribbed / rugged windowed / tethered | no | yes | `cap_style`, `grip_style` | cap 是视觉差异主要来源 |
| screw motion | pure spin / spin + axial lift | no | yes | `screw_motion_model` | joint semantics 不同，必须离散选择 |
| seal | liner disc / inner plug / pressure ring / none | no | yes | `seal_style` | 随 cap 固定运动 |
| armor/tether | none / cage rails / base boot / tether lug | no | yes | `has_armor`, `has_tether` | optional，但不能改变 screwcap 核心语义 |

## 组合逻辑（Composition Logic）
1. 先采 `bottle_profile`、`body_height`、`body_radius`，建立 bottle root 和中心轴 `z_axis`。
2. 从 body 顶部派生 shoulder 与 neck：`neck_radius < body_radius`，`neck_height >= thread_height + finish_bead_margin`。
3. 再采 `thread_pitch` 和 `thread_turns`，计算 `thread_height = thread_pitch * thread_turns + lead_margin`，`thread_travel = thread_pitch * thread_turns`。
4. external thread 的中心轴必须与 neck 共轴；helical mesh 或 banded thread 都从 `neck_radius + thread_profile_height` 派生。
5. cap 内径由 neck/thread 派生：`cap_inner_radius = neck_thread_outer_radius + thread_clearance`，`cap_outer_radius = cap_inner_radius + cap_wall + grip_depth`。
6. cap skirt height 至少覆盖 thread height 和 seal plug，`cap_height = cap_skirt_height + cap_top_thickness`。
7. `screw_motion_model=simple_spin` 时，cap 以 neck axis continuous/revolute 旋转；必须仍坐在 neck finish 上。
8. `screw_motion_model=threaded_turn_lift` 时，创建同轴 revolute + prismatic pair：turn limit = `thread_turns * 2pi`，lift limit = `thread_travel`；二者共享 thread metadata。
9. knurls、seal、index mark、tether lug 均固定到 cap；armor/base boot 固定到 bottle body，不改变 cap 父子链。

## 已有模板写法参考
| 模板文件 | 可参考写法 |
|---|---|
| `agent/templates/coaxial_rotary_stack.py` | coaxial parent/child axis setup and continuous/revolute rotary stack semantics |
| `agent/templates/camera_lens.py` | concentric rings, grip/knurl-like radial details, nested cylindrical components |
| `agent/templates/blender_countertop.py` | container/body proportions, cap/lid seating, derived clearance around a vertical axis |
| `agent/templates/refrigerator_with_hinged_doors.py` | gasket/seal-like fixed child details and closed-pose contact checks |


## 约束
- bottle body、neck、cap 必须共轴，默认 axis 为 Z。
- cap 内径必须大于 neck/thread 外径并保留 positive clearance。
- cap 在 closed pose 必须覆盖 neck thread，不能漂浮在瓶口上方。
- `threaded_turn_lift` 的 prismatic lift 必须等于 `thread_pitch * thread_turns` 或记录等价 lead metadata。
- cap 的 seal/knurl/index/tether 必须随 cap 一起运动。
- body profile 可变，但不能牺牲 screwcap 核心：neck finish + cap + screw joint 必须存在。
- rugged armor/cage 只能固定在 body 上，不能穿过 cap rotation envelope。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | bottle body + neck finish + screw cap present |
| coaxiality | body neck axis, external thread, internal cap thread, cap joint axis all aligned |
| cap fit | cap inner radius > thread outer radius + clearance_min; cap skirt covers thread height |
| screw joint | simple model has cap_spin; threaded model has revolute turn + prismatic lift |
| pitch consistency | `thread_travel ~= thread_pitch * thread_turns` for threaded model |
| closed contact | cap closed pose seated on neck/finish, not floating |
| moving group | cap shell, internal thread, seal, knurls move together |
| optional compatibility | armor/tether/boot do not intersect cap travel envelope |
| no floating | cap, seal, knurls, neck rings, armor details all attached or constrained |

## Reject cases
- 有瓶子和盖子但没有瓶颈螺纹或 screw joint。
- cap 与 neck 不共轴，或 cap 悬浮在瓶口上方。
- cap 内径小于 neck/thread 外径导致穿模。
- threaded model 只有旋转没有 axial lift，也没有说明为 simple_spin。
- seal/knurl 固定在 bottle body 上，cap 运动时不随 cap 走。
- rugged cage/rail 穿过 cap 的旋转/升降空间。
- 随机摆放 cap，而不是从 body/neck/thread 尺寸派生。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
