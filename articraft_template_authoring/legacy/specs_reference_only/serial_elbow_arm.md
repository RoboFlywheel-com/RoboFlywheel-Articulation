# Serial Elbow Arm Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `serial_elbow_arm` |
| template path | `agent/templates/serial_elbow_arm.py` |
| test path | `tests/agent/test_serial_elbow_arm_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 39 |
| read_count | 39 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below; planar-yaw arms are treated as a gated family or future split, not mixed into the default pitch-elbow arm |

## 核心身份
串联肘式机械臂/二连杆 elbow arm，必须包含固定 base/shoulder housing、近端 upper/proximal link、远端 forearm/distal link、以及两个串联主 revolute joints：shoulder 和 elbow。默认成熟域是 vertical-pitch serial elbow arm：shoulder_pitch 和 elbow_pitch 轴平行，link lengths 从 reach 派生，joint origins 位于真实 bearing/yoke 中心。planar_yaw pick-place arm 可以作为 `axis_family=planar_yaw` gated variant，但不能把 Z 轴 yaw 和 Y 轴 pitch 混在同一默认模板里导致语义错误。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_serial_elbow_arm_0003` | `data/records/rec_serial_elbow_arm_0003/revisions/rev_000001/model.py:L24-L103` | shoulder/elbow constants, primitive helpers, covers and bolt details |
| S2 | `rec_serial_elbow_arm_0003` | `data/records/rec_serial_elbow_arm_0003/revisions/rev_000001/model.py:L106-L271` | pedestal cheeks, upper arm hub/link/elbow cheeks, forearm hub/main/end flange helper shapes |
| S3 | `rec_serial_elbow_arm_0003` | `data/records/rec_serial_elbow_arm_0003/revisions/rev_000001/model.py:L282-L491` | pedestal, upper_arm, forearm parts and shoulder_pitch / elbow_pitch joints |
| S4 | `rec_serial_elbow_arm_c8111e5b8ef843138835f71ed1538cda` | `data/records/rec_serial_elbow_arm_c8111e5b8ef843138835f71ed1538cda/revisions/rev_000001/model.py:L24-L86` | shoulder z, link length, gap, cheek thickness constants and helpers |
| S5 | `rec_serial_elbow_arm_c8111e5b8ef843138835f71ed1538cda` | `data/records/rec_serial_elbow_arm_c8111e5b8ef843138835f71ed1538cda/revisions/rev_000001/model.py:L89-L283` | shoulder housing, hollow upper link, elbow cheeks, forearm carrier/pad plate helpers |
| S6 | `rec_serial_elbow_arm_c8111e5b8ef843138835f71ed1538cda` | `data/records/rec_serial_elbow_arm_c8111e5b8ef843138835f71ed1538cda/revisions/rev_000001/model.py:L286-L520` | shoulder_housing, upper_link, forearm parts and pitch joints |
| S7 | `rec_serial_elbow_arm_478aa122662d4b30b7125b7215d77d4b` | `data/records/rec_serial_elbow_arm_478aa122662d4b30b7125b7215d77d4b/revisions/rev_000001/model.py:L23-L67` | industrial pedestal/upper/forearm/end plate constants |
| S8 | `rec_serial_elbow_arm_478aa122662d4b30b7125b7215d77d4b` | `data/records/rec_serial_elbow_arm_478aa122662d4b30b7125b7215d77d4b/revisions/rev_000001/model.py:L69-L148` | pedestal shape, upper body, forearm body shapes |
| S9 | `rec_serial_elbow_arm_478aa122662d4b30b7125b7215d77d4b` | `data/records/rec_serial_elbow_arm_478aa122662d4b30b7125b7215d77d4b/revisions/rev_000001/model.py:L151-L261` | pedestal_to_upper_link, upper_link_to_forearm, forearm_to_end_plate joints |
| S10 | `rec_serial_elbow_arm_958fc14d6dc5464d82adfcbf2530c2b8` | `data/records/rec_serial_elbow_arm_958fc14d6dc5464d82adfcbf2530c2b8/revisions/rev_000001/model.py:L18-L50` | planar-yaw industrial base/controller, optional gated family |
| S11 | `rec_serial_elbow_arm_958fc14d6dc5464d82adfcbf2530c2b8` | `data/records/rec_serial_elbow_arm_958fc14d6dc5464d82adfcbf2530c2b8/revisions/rev_000001/model.py:L52-L138` | planar upper/forearm/tool flange/vacuum tube/suction cup |
| S12 | `rec_serial_elbow_arm_958fc14d6dc5464d82adfcbf2530c2b8` | `data/records/rec_serial_elbow_arm_958fc14d6dc5464d82adfcbf2530c2b8/revisions/rev_000001/model.py:L139-L156` | shoulder_yaw and elbow_yaw joints for planar-yaw branch only |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `base` / `pedestal` | 固定底座、肩部壳体或 root bracket，必须落地/固定 | `base_style`, `base_width`, `base_depth`, `shoulder_z`, `mount_plate_thickness` | S2 / S3 / S5 / S6 / S7 / S8 / S10 |
| `shoulder_yoke` / `shoulder_housing` | 承接 upper link 的双 cheek/bearing housing | `shoulder_gap`, `shoulder_boss_radius`, `cheek_thickness` | S2 / S5 / S6 |
| `upper_link` / `proximal_link` | 近端连杆，包含 shoulder hub、beam、distal elbow cheeks | `upper_len`, `link_style`, `upper_width`, `upper_height` | S2 / S3 / S5 / S6 / S8 / S9 |
| `elbow_hub` / `elbow_yoke` | upper/forearm 之间的 elbow bearing and cheek interface | `elbow_gap`, `elbow_boss_radius`, `bearing_clearance` | S2 / S5 / S6 |
| `forearm` / `distal_link` | 远端连杆，连接 elbow 到 end flange/tool carrier | `forearm_len`, `forearm_width`, `forearm_height`, `forearm_style` | S2 / S3 / S5 / S6 / S8 / S9 |
| `end_plate` / `tool_carrier` | 末端法兰、pad plate、tool mount 或 suction tool，fixed to forearm | `end_effector_style`, `flange_radius`, `tool_offset` | S2 / S3 / S5 / S6 / S9 / S11 |
| `bearing_covers` / `fasteners` | shoulder/elbow 轴盖、螺栓、spacers、labels 等 fixed details | `cover_style`, `bolt_count`, `detail_level` | S1 / S2 / S4 / S5 |
| `parallel_tie_bars` | 双平行连杆或 tie bars，optional，随 upper/forearm branch | `has_tie_bars`, `tie_bar_radius`, `tie_bar_spacing` | S11 |
| `cable_or_tube` | vacuum tube、wire guide、decorative cable，optional fixed along link | `has_cable_tube`, `tube_radius` | S11 |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `shoulder_pitch` | revolute | `(0, 1, 0)` or `(0, -1, 0)` | shoulder housing bearing center | `[-1.2, 1.4]` rad typical | 默认 vertical-pitch family 的第一个主关节 | S3 / S6 / S9 |
| `elbow_pitch` | revolute | `(0, 1, 0)` or `(0, -1, 0)` | upper link distal elbow bearing center | `[-1.7, 1.7]` rad typical | 默认 vertical-pitch family 的第二个主关节，轴应与 shoulder 平行 | S3 / S6 / S9 |
| `shoulder_yaw` | revolute | `(0, 0, 1)` | base top yaw bearing center | `[-pi, pi]` | planar-yaw branch only，不是默认 pitch template | S12 |
| `elbow_yaw` | revolute | `(0, 0, 1)` | upper link distal yaw bearing center | `[-pi, pi]` | planar-yaw branch only | S12 |
| `forearm_to_end_plate` | fixed | n/a | forearm distal tool datum | n/a | 末端法兰/工具固定到 forearm | S9 / S11 |
| `tool_optional_joint` | fixed or gated | branch-specific | end plate datum | branch-specific | 只有专门 tool variant 才添加吸盘/夹爪 DOF；默认 fixed | S11 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `axis_family` | enum | `vertical_pitch` / `planar_yaw` | `vertical_pitch` | drives joint axes and pose plane; planar_yaw gated | S3 / S6 / S9 / S12 |
| `base_style` | enum | `pedestal` / `root_fork` / `side_plate` / `floor_base` / `controller_box` | `pedestal` | drives root geometry and shoulder support | S2 / S5 / S8 / S10 |
| `link_style` | enum | `box_beam` / `open_plate` / `dual_parallel` / `industrial_cast` | `box_beam` | drives link cross-section and tie-bar availability | S2 / S5 / S8 / S11 |
| `total_reach` | float | `0.35-1.40` | sampled | `upper_len + forearm_len + tool_offset` | S2 / S5 / S7 / S11 |
| `link_ratio` | float | `0.45-0.58` | sampled | `upper_len = total_reach * link_ratio`, `forearm_len = total_reach - upper_len - tool_offset` | S2 / S5 / S7 |
| `upper_len` | float | derived, min `0.16` | derived | distance shoulder_origin -> elbow_origin | S3 / S6 / S9 |
| `forearm_len` | float | derived, min `0.14` | derived | distance elbow_origin -> tool_datum | S3 / S6 / S9 |
| `shoulder_z` | float | `0.10-0.45` | sampled | base height and shoulder housing center | S2 / S4 / S5 |
| `shoulder_gap` | float | derived | derived | `upper_width + 2 * bearing_clearance` | S2 / S5 |
| `elbow_gap` | float | derived | derived | `forearm_width + 2 * bearing_clearance` | S2 / S5 |
| `joint_limit_profile` | enum | `industrial_safe` / `wide_range` / `compact_service` | `industrial_safe` | sets shoulder/elbow ranges | S3 / S6 / S9 |
| `end_effector_style` | enum | `flange` / `pad_plate` / `suction_cup` / `tool_carrier` / `none` | `flange` | default fixed end plate; suction cup gated for planar sample style | S2 / S5 / S9 / S11 |
| `has_tie_bars` | bool | `true` / `false` | derived | allowed for `link_style=dual_parallel` | S11 |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| axis family | vertical pitch elbow / planar yaw pick-place | no | yes | `axis_family` | 关节轴和工作平面不同，必须 gate |
| base | pedestal / root fork / side plate / controller box | no | yes | `base_style` | shoulder support topology 不同 |
| link body | box beam / open plate / cast arm / dual parallel bars | no | yes | `link_style`, `has_tie_bars` | link construction affects yoke clearance |
| shoulder/elbow housing | cheek yoke / cylindrical boss / side bearing / covered joint | no | yes | `cover_style`, `cheek_thickness` | 可复用但需从 link width 派生 |
| end effector | flange / pad / tool carrier / suction cup | no | yes | `end_effector_style` | 末端语义不同，默认 fixed flange |
| joint limits | compact safe range / wide industrial range | yes within family | partly | `joint_limit_profile` | axis family 固定后可连续调节 range |
| decorative hardware | covers / bolts / spacers / cables | yes within style | partly | `detail_level`, `cover_style` | 只能固定到已有 hubs/links |

## 组合逻辑（Composition Logic）
1. 先采 `axis_family`。默认 `vertical_pitch`：shoulder/elbow axes 都为 local ±Y 且彼此平行；`planar_yaw` 只作为 gated branch，axes 为 Z。
2. 采 `base_style` 与 `shoulder_z`，生成 grounded base/root bracket。shoulder bearing center = `(0, 0, shoulder_z)` 或 branch-specific base datum。
3. 采 `total_reach` 和 `link_ratio`，派生 `upper_len` 与 `forearm_len`。joint origin 绝不能随机摆放：elbow origin = shoulder origin + upper local X * `upper_len`。
4. 根据 `upper_width`、`bearing_clearance` 派生 `shoulder_gap`，生成 yoke cheeks 包住 upper shoulder hub。upper hub 必须在 shoulder yoke 内。
5. 生成 upper link：近端 hub 在 shoulder origin，远端 elbow cheeks/boss center 在 elbow origin。
6. 根据 `forearm_width` 派生 `elbow_gap`，生成 forearm hub，forearm body 从 elbow origin 延伸 `forearm_len` 到 tool datum。
7. 生成 end plate/tool carrier，fixed 到 forearm distal datum；默认不添加额外 tool DOF。
8. optional bearing covers、bolts、tie bars、cables 都从 hubs/links 的尺寸和位置派生，不能成为独立漂浮装饰。
9. planar-yaw branch 若启用，必须统一用 Z 轴 shoulder/elbow yaw，并把 gravity/pitch-specific counterweight/yoke constraints 关掉。

## 已有模板写法参考
| 模板文件 | 可参考写法 |
|---|---|
| `agent/templates/cantilever_articulated_arm.py` | two-link serial arm topology, endpoint-derived joint origins, yoke/bearing geometry |
| `agent/templates/telescoping_boom.py` | industrial beam proportions, end effector mounting, reach-derived sizing |
| `agent/templates/coaxial_rotary_stack.py` | bearing covers, coaxial hubs, axis consistency checks |


## 约束
- 默认必须恰好有两个主 revolute joints：`shoulder_pitch` 和 `elbow_pitch`。
- `vertical_pitch` family 中 shoulder 和 elbow axes 必须平行且均为 ±Y。
- `planar_yaw` family 中 shoulder 和 elbow axes 必须均为 Z，不能与 pitch family 混用。
- `upper_len` 必须等于 shoulder-to-elbow distance；`forearm_len` 必须等于 elbow-to-tool distance。
- base/root 必须落地或固定，shoulder housing 必须与 base 接触。
- upper link 和 forearm 的 hubs 必须位于 yoke/bearing 中心，不能漂浮或偏离 joint origin。
- end plate/tool carrier 必须 fixed 到 forearm distal datum。
- decorative covers、bolts、cables、tie bars 必须挂在 base/link/hub 上。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | base + upper link + forearm + two serial primary revolute joints present |
| primary joint count | default vertical-pitch has exactly shoulder_pitch and elbow_pitch as main joints |
| axis consistency | pitch branch uses parallel ±Y axes; yaw branch uses parallel Z axes |
| endpoint consistency | `distance(shoulder_origin, elbow_origin) ~= upper_len`; `distance(elbow_origin, tool_datum) ~= forearm_len` |
| yoke containment | upper/forearm hubs lie inside derived shoulder/elbow gaps with clearance |
| serial topology | base -> upper_link -> forearm -> end_plate chain, no skipped parent |
| base grounding | base contacts ground/mount plane and supports shoulder housing |
| optional compatibility | planar-yaw samples only if `axis_family=planar_yaw`; tie bars only if matching link style |
| no floating | links、hubs、covers、bolts、end effector、cables all attached or constrained |

## Reject cases
- 只有两个静态杆件，没有 shoulder/elbow revolute joints。
- shoulder/elbow joint origins 不在 link/hub 端点。
- pitch 和 yaw 轴混用，导致一个关节绕 Y、另一个绕 Z 但没有明确 branch。
- upper/forearm 长度参数和实际 joint distance 不一致。
- base 或 shoulder housing 漂浮，连杆从空中开始。
- end plate/tool carrier 不在 forearm 末端或没有 fixed parent。
- planar pick-place arm 被硬塞进 vertical-pitch 默认分支。
- covers、bolts、cables、suction cup 悬空。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
