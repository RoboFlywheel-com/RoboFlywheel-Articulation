# Monitor Mount Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `monitor_mount` |
| template path | `agent/templates/monitor_mount.py` |
| test path | `tests/agent/test_monitor_mount_template.py` |
| primary_anchor | `rec_monitor_mount_997e8c29b2f44a30a7dd25da2a7c6fa6:rev_000001` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 31 |
| read_count | 31 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below; incompatible or over-specialized samples inform constraints but are not forced into the template |

## 核心身份
显示器支架/显示器臂，必须包含稳定的安装基座、串联支臂、显示器头部/转接板，以及至少一个真实可动关节。默认成熟域是 desk/wall/pole mounted two-link monitor arm：基座提供桌夹、墙板或立柱连接，支臂提供 reach，末端提供 VESA plate 的 pan/tilt。counterbalanced gas-spring arm、cable-spine wall arm、simple desk clamp arm 都可以作为 gated variants，但不能让显示器头、连杆或基座漂浮。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_monitor_mount_0001` | `data/records/rec_monitor_mount_0001/revisions/rev_000001/model.py:L51-L114` | desk clamp、vertical post、base collar、clamp pad 的成熟基座写法 |
| S2 | `rec_monitor_mount_0001` | `data/records/rec_monitor_mount_0001/revisions/rev_000001/model.py:L115-L205` | lower/upper arms、clevis、bearings、head yoke、VESA plate |
| S3 | `rec_monitor_mount_0001` | `data/records/rec_monitor_mount_0001/revisions/rev_000001/model.py:L207-L242` | base swivel、elbow、head yaw、VESA tilt 的基础关节链 |
| S4 | `rec_monitor_mount_997e8c29b2f44a30a7dd25da2a7c6fa6` | `data/records/rec_monitor_mount_997e8c29b2f44a30a7dd25da2a7c6fa6/revisions/rev_000001/model.py:L30-L183` | wall bracket、bearing cup、pan carriage、shoulder cheeks、mounting holes、cable window |
| S5 | `rec_monitor_mount_997e8c29b2f44a30a7dd25da2a7c6fa6` | `data/records/rec_monitor_mount_997e8c29b2f44a30a7dd25da2a7c6fa6/revisions/rev_000001/model.py:L185-L482` | counterbalanced primary/secondary arms、spring tube、gas spring、head knuckle、tilt yoke、VESA inserts |
| S6 | `rec_monitor_mount_997e8c29b2f44a30a7dd25da2a7c6fa6` | `data/records/rec_monitor_mount_997e8c29b2f44a30a7dd25da2a7c6fa6/revisions/rev_000001/model.py:L484-L533` | wall_pan、shoulder_lift、elbow_fold、head_pan、head_tilt 复合关节链 |
| S7 | `rec_monitor_mount_b009e88d6f924f3c90fb6e0ef457e60b` | `data/records/rec_monitor_mount_b009e88d6f924f3c90fb6e0ef457e60b/revisions/rev_000001/model.py:L31-L88` | wall plate、shoulder lugs、bosses 的紧凑墙装写法 |
| S8 | `rec_monitor_mount_b009e88d6f924f3c90fb6e0ef457e60b` | `data/records/rec_monitor_mount_b009e88d6f924f3c90fb6e0ef457e60b/revisions/rev_000001/model.py:L89-L284` | primary/secondary link、fixed cable spine、pan swivel、tilt cradle、VESA plate |
| S9 | `rec_monitor_mount_b009e88d6f924f3c90fb6e0ef457e60b` | `data/records/rec_monitor_mount_b009e88d6f924f3c90fb6e0ef457e60b/revisions/rev_000001/model.py:L285-L333` | wall_to_primary、primary_to_secondary、secondary_to_pan、pan_to_tilt 的 planar wall arm joints |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `base_mount` | 桌夹、墙板、立柱夹或重型底座，是整机唯一 ground/root 接触件 | `mount_base_style`, `base_width`, `base_depth`, `clamp_gap`, `wall_plate_height` | S1 / S4 / S7 |
| `vertical_post` / `wall_bearing` | desk clamp 的立柱或 wall mount 的 pan bearing cup | `post_height`, `post_radius`, `bearing_radius` | S1 / S4 |
| `shoulder_carriage` | 承接第一个支臂的 shoulder yoke/pan carriage，含 cheek gap 和 bearing boss | `shoulder_gap`, `shoulder_boss_radius`, `arm_plane` | S4 / S5 / S7 |
| `primary_link` | 近端支臂，可为箱形梁、双侧板、counterbalance tube 或 compact wall link | `primary_len`, `link_style`, `link_height`, `link_width` | S2 / S5 / S8 |
| `secondary_link` | 远端支臂，连接 elbow 到 head pan/tilt | `secondary_len`, `secondary_style`, `head_offset` | S2 / S5 / S8 |
| `counterbalance` | gas spring、spring tube、tension rod 或 decorative balance shell，optional | `has_counterbalance`, `spring_radius`, `spring_clearance` | S5 |
| `cable_spine` | 固定或随 secondary link 的线缆槽/盖板，optional | `has_cable_spine`, `cable_spine_width` | S4 / S8 |
| `head_yoke` / `pan_swivel` | 末端 pan/tilt 头，承接显示器板 | `head_dof`, `head_width`, `tilt_axis_offset` | S2 / S5 / S8 |
| `vesa_plate` | 显示器转接板，必须有 VESA hole/grid 或插槽 | `vesa_size`, `plate_width`, `plate_height`, `hole_radius` | S2 / S5 / S8 |
| `covers_knobs_fasteners` | 轴盖、调节旋钮、螺栓、线缆扣等非必要细节 | `detail_level`, `knob_style` | S2 / S4 / S5 |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `base_yaw` / `wall_pan` | revolute or continuous | `(0, 0, 1)` | base bearing / wall bearing center | `[-pi, pi]` or continuous | 基座水平旋转或墙装 pan | S3 / S6 / S9 |
| `shoulder_lift` | revolute | `(0, -1, 0)` or `(0, 1, 0)` | shoulder carriage cheek center | `[-0.8, 1.2]` rad typical | counterbalanced vertical-pitch arm 的肩部抬升，optional | S6 |
| `shoulder_yaw_or_primary_joint` | revolute | `(0, 0, 1)` for planar arm, `(0, ±1, 0)` for pitch arm | base/shoulder axis | branch-specific | simple two-link 的第一个支臂关节 | S3 / S9 |
| `elbow_fold` | revolute | `(0, 0, 1)` or `(0, ±1, 0)` | primary link distal bearing | branch-specific | 主臂到副臂折叠 | S3 / S6 / S9 |
| `head_pan` | revolute or continuous | `(0, 0, 1)` | secondary distal pan bearing | `[-pi, pi]` | 显示器头左右转 | S3 / S6 / S9 |
| `head_tilt` / `vesa_tilt` | revolute | `(0, 1, 0)` or `(0, -1, 0)` | head yoke tilt pin | `[-0.7, 0.7]` rad typical | VESA plate 上下倾斜 | S3 / S6 / S9 |
| `display_roll` | revolute | `(1, 0, 0)` | VESA plate center | `[-pi, pi]` optional | 横竖屏 roll，只有 `head_dof=pan_tilt_roll` 时启用 | S2 / S5 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `mount_base_style` | enum | `desk_clamp` / `wall_plate` / `pole_clamp` / `freestanding_base` | `desk_clamp` | drives root geometry and contact plane | S1 / S4 / S7 |
| `arm_topology` | enum | `simple_two_link` / `wall_planar_two_link` / `counterbalanced_lift_pitch` / `single_short_arm` | `simple_two_link` | selects joint chain and optional counterbalance | S2 / S5 / S8 |
| `arm_plane` | enum | `horizontal_yaw` / `vertical_pitch` / `hybrid_counterbalanced` | `horizontal_yaw` | sets shoulder/elbow axes and gravity visual details | S3 / S6 / S9 |
| `total_reach` | float | `0.35-1.05` | sampled | `primary_len + secondary_len + head_offset` | S2 / S5 / S8 |
| `link_ratio` | float | `0.42-0.58` | sampled | `primary_len = total_reach * link_ratio`, `secondary_len = total_reach - primary_len - head_offset` | S2 / S5 / S8 |
| `primary_len` | float | derived, min `0.16` | derived | clamped by `total_reach`, `link_ratio`, base clearance | S2 / S5 / S8 |
| `secondary_len` | float | derived, min `0.14` | derived | must exceed head/yoke clearance | S2 / S5 / S8 |
| `head_dof` | enum | `tilt_only` / `pan_tilt` / `pan_tilt_roll` | `pan_tilt` | controls head joints | S3 / S6 / S9 |
| `vesa_size` | enum | `75` / `100` / `dual_75_100` | `100` | sets hole grid, plate dimensions | S2 / S5 / S8 |
| `monitor_mass_class` | enum | `light` / `medium` / `heavy` | `medium` | heavy requires thicker links and preferably counterbalance | S5 |
| `has_counterbalance` | bool | `true` / `false` | derived | true if `arm_topology=counterbalanced_lift_pitch` or heavy pitch arm | S5 / S6 |
| `has_cable_spine` | bool | `true` / `false` | sampled | allowed for wall/counterbalanced arms; fixed to secondary or base branch | S4 / S8 |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| base/root | desk clamp / wall plate / pole clamp / free stand | no | yes | `mount_base_style` | 根部安装语义完全不同，必须离散选择 |
| arm topology | single arm / two-link yaw / wall planar / counterbalanced pitch | no | yes | `arm_topology`, `arm_plane` | 关节轴和 joint limits 不同，不能混采 |
| link body | box beam / dual rail / gas spring tube / cable spine link | no | yes | `link_style`, `has_counterbalance`, `has_cable_spine` | 视觉和碰撞厚度差异大 |
| head | tilt-only / pan-tilt / roll-capable VESA | no | yes | `head_dof` | 末端 DOF 是语义核心 |
| VESA plate | 75 / 100 / dual slot / insert grid | partly | yes | `vesa_size` | hole grid 需要离散尺寸 |
| counterbalance | none / visible spring / gas strut / spring tube | no | yes | `counterbalance_style` | 只在 pitch/counterbalanced branch 合法 |

## 组合逻辑（Composition Logic）
1. 先采 `mount_base_style`，建立唯一 root contact：desk clamp 必须有桌面夹口和下压 pad；wall plate 必须贴墙并有螺钉孔；pole clamp 必须环抱立柱；freestanding 必须有足够底盘面积。
2. 再采 `arm_topology` 与 `arm_plane`。若为 `counterbalanced_lift_pitch`，强制 `arm_plane=hybrid_counterbalanced`，启用 shoulder lift、elbow fold、counterbalance；若为 wall planar，使用 Z 轴平面折叠。
3. 采 `total_reach` 和 `link_ratio`，派生 `primary_len`、`secondary_len`、`head_offset`。不得直接随机摆放 secondary/head；所有 child origin 必须从 parent joint origin 加 link length 派生。
4. 生成 shoulder/yoke gap：`link_width + 2 * bearing_clearance <= shoulder_gap`，bearing boss 半径必须大于 link half height。
5. 生成 primary link：近端 hub center 在 shoulder origin，远端 elbow origin = shoulder origin + link local X * `primary_len`。
6. 生成 secondary link：近端 hub center 在 elbow origin，远端 head pan origin = elbow origin + secondary local X * `secondary_len`。
7. 末端先生成 `head_yoke`，再生成 `vesa_plate`；VESA plate 的 hole/grid 根据 `vesa_size` 派生，不允许随机孔距。
8. optional cable spine、spring、knobs 只能挂在已有 link 或 base 上；不能形成新的悬空 part。

## 已有模板写法参考
| 模板文件 | 可参考写法 |
|---|---|
| `agent/templates/cantilever_articulated_arm.py` | serial articulated arm chain、link endpoint derived joint origins、yoke/bearing spacing |
| `agent/templates/desktop_monitor_with_tilt_swivel_stand.py` | monitor head、tilt/swivel semantics、display mounting plate proportions |
| `agent/templates/coaxial_rotary_stack.py` | coaxial bearing stack and continuous/revolute axis conventions |


## 约束
- 必须至少有一个 root mounting part，且 root 不可漂浮。
- 支臂必须形成连续 serial chain：base -> shoulder/primary -> secondary -> head -> VESA。
- `primary_len`、`secondary_len` 必须从 `total_reach` 派生并用于 joint origin，不能只影响视觉长度。
- `arm_plane=horizontal_yaw` 时 shoulder/elbow 主轴为 Z；`vertical_pitch` 或 counterbalanced branch 时主轴为 ±Y。
- `has_counterbalance=true` 时必须存在 shoulder lift 语义或明显 pitch load path，不得把 spring 放在 planar yaw arm 上。
- VESA plate 必须在 head/tilt 子链上，不能固定在 base 或 link 中段。
- `head_tilt` axis 必须穿过 head yoke/plate，tilt 后不得与 arm link 穿插。
- cable spine、decorative covers、knobs 必须与父件接触或固定，不能独立浮在空间中。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | root mount + at least one arm link + head/VESA plate present |
| root contact | desk clamp/wall/pole/freestanding base 与对应 contact plane 有接触或包络 |
| serial continuity | 每个 moving child 的 joint origin 等于 parent link 端点或 bearing center |
| link length consistency | `distance(shoulder, elbow) ~= primary_len`; `distance(elbow, head_pan) ~= secondary_len` |
| axis semantics | yaw joints use Z; pitch/tilt joints use local ±Y; roll uses local X |
| VESA grid | hole spacing matches `vesa_size` and holes lie on plate |
| no floating | arm links、head、VESA、counterbalance、cable spine 均有 parent/constraint |
| optional compatibility | counterbalance only with pitch/hybrid branch; display roll only if `head_dof=pan_tilt_roll` |
| range safety | joint ranges keep link hubs interpenetration-free at representative closed/open poses |

## Reject cases
- 只有显示器板，没有安装基座或支臂。
- 支臂视觉上分离，joint origin 没在 link 端点。
- `primary_len` / `secondary_len` 与实际几何或 joint origin 不一致。
- desk clamp 没有夹口/桌面接触，wall plate 没贴墙，base 漂浮。
- head tilt/pan 轴语义错误，例如 tilt 绕 Z 轴或 pan 绕 X 轴。
- VESA plate 不在末端头部，或 hole spacing 随机错误。
- counterbalance spring 放在 horizontal yaw arm 上但没有 shoulder lift 语义。
- cable spine、knob、bearing cover 悬空。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
