# Louvered Shutter Assembly Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `louvered_shutter_assembly` |
| template path | `agent/templates/louvered_shutter_assembly.py` |
| test path | `tests/agent/test_louvered_shutter_assembly_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `SPEC_ONLY_DRAFT` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 33 |
| read_count | 33 |
| read_scope | all 5-star samples in this category |
| source_index_policy | only adopted reusable snippets are indexed below |

## 核心身份
百叶窗 / 百叶门组件必须有外框或 shutter leaf、成排平行 louvers / slats、每片 slat 的 pivot 轴或同步 tilt linkage，以及可选的 panel hinge / bifold hinge / support arm。核心不是普通窗框，而是 slat array 可以绕水平轴开合，或通过 tilt rod / mimic joints 同步改变倾角。

采纳策略：默认成熟实现应先覆盖 `plantation_louver_core`，即单扇 / 双扇 shutter leaf + slat array + independent 或 tilt-rod-linked louver motion。bifold 和 storm shutter support arm 是可用的 5 星证据和 future variant，但它们改变 panel joint chain，应作为 review-gated branch 或后续 split，不应污染默认 seed。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_louvered_shutter_assembly_4492bf5f324e4691a5b50d1de1a2f7c5` | `data/records/rec_louvered_shutter_assembly_4492bf5f324e4691a5b50d1de1a2f7c5/revisions/rev_000001/model.py:L13-L58` | simple outer frame and 12 independent louver slat pivot joints |
| S2 | `rec_louvered_shutter_assembly_4492bf5f324e4691a5b50d1de1a2f7c5` | `data/records/rec_louvered_shutter_assembly_4492bf5f324e4691a5b50d1de1a2f7c5/revisions/rev_000001/model.py:L60-L101` | validator checks that slat pins remain within the frame |
| S3 | `rec_louvered_shutter_assembly_7c027fd83b684e1bb3d2b2f4c2656525` | `data/records/rec_louvered_shutter_assembly_7c027fd83b684e1bb3d2b2f4c2656525/revisions/rev_000001/model.py:L27-L96` | window frame, jambs, fixed hinge hardware and opening context |
| S4 | `rec_louvered_shutter_assembly_7c027fd83b684e1bb3d2b2f4c2656525` | `data/records/rec_louvered_shutter_assembly_7c027fd83b684e1bb3d2b2f4c2656525/revisions/rev_000001/model.py:L97-L264` | shutter leaf helper, leaf hinge, slat clips, vertical tilt rod, louver slats with pins and mimic joints |
| S5 | `rec_louvered_shutter_assembly_7c027fd83b684e1bb3d2b2f4c2656525` | `data/records/rec_louvered_shutter_assembly_7c027fd83b684e1bb3d2b2f4c2656525/revisions/rev_000001/model.py:L280-L402` | joint, spatial, contact and rod/slat motion tests |
| S6 | `rec_louvered_shutter_assembly_d2759605eb0f4d49bdb825400e4fb507` | `data/records/rec_louvered_shutter_assembly_d2759605eb0f4d49bdb825400e4fb507/revisions/rev_000001/model.py:L22-L117` | outer frame, panel and louver constants, louver mesh and center-z derivation |
| S7 | `rec_louvered_shutter_assembly_d2759605eb0f4d49bdb825400e4fb507` | `data/records/rec_louvered_shutter_assembly_d2759605eb0f4d49bdb825400e4fb507/revisions/rev_000001/model.py:L128-L349` | outer frame, panel frame, rod guides, tilt rod, louver joints, panel hinge and rod fixed joint |
| S8 | `rec_louvered_shutter_assembly_cd6b32786e5c4247a78b6d28fe29f505` | `data/records/rec_louvered_shutter_assembly_cd6b32786e5c4247a78b6d28fe29f505/revisions/rev_000001/model.py:L25-L174` | bifold dimensions, leaf frame helper, hinge hardware and vertical leaf joints |
| S9 | `rec_louvered_shutter_assembly_cd6b32786e5c4247a78b6d28fe29f505` | `data/records/rec_louvered_shutter_assembly_cd6b32786e5c4247a78b6d28fe29f505/revisions/rev_000001/model.py:L176-L365` | bifold control rods, louver parts, pivot joints and tests |
| S10 | `rec_louvered_shutter_assembly_54553517611c4467b1ced14026ea876f` | `data/records/rec_louvered_shutter_assembly_54553517611c4467b1ced14026ea876f/revisions/rev_000001/model.py:L22-L76` | louver blade mesh and panel dimension / louver position derivation |
| S11 | `rec_louvered_shutter_assembly_54553517611c4467b1ced14026ea876f` | `data/records/rec_louvered_shutter_assembly_54553517611c4467b1ced14026ea876f/revisions/rev_000001/model.py:L78-L342` | opening frame, hinge knuckles, shutter panel, support arm, louver joints and frame / panel / support arm joints |

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `outer_frame` / `window_frame` | 必需或条件必需；外部窗框、jamb、top/bottom rails、mounting frame | `frame_width`, `frame_height`, `frame_depth`, `frame_style`, `jamb_thickness` | S1 / `model.py:L13-L58`; S3 / `model.py:L27-L96`; S6 / `model.py:L128-L260`; S8 / `model.py:L25-L174`; S11 / `model.py:L78-L136` |
| `shutter_leaf_i` / `panel_i` | 必需；承载 louvers 的单扇、双扇、bifold leaf 或 storm shutter panel | `panel_layout`, `leaf_count`, `leaf_width`, `leaf_height`, `stile_width`, `rail_height` | S4 / `model.py:L97-L171`; S6 / `model.py:L22-L117`; S7 / `model.py:L128-L260`; S8 / `model.py:L25-L174`; S11 / `model.py:L138-L213` |
| `louver_slat_i` | 必需；平行百叶片，带 pivot pin / end caps，可单独或 mimic 转动 | `slat_count`, `slat_profile`, `slat_pitch`, `slat_angle_closed`, `slat_length`, `slat_thickness` | S1 / `model.py:L13-L58`; S4 / `model.py:L224-L264`; S6 / `model.py:L84-L117`; S7 / `model.py:L263-L331`; S9 / `model.py:L205-L237`; S10 / `model.py:L22-L76`; S11 / `model.py:L260-L299` |
| `slat_pin_i` / `pivot_clip_i` | 必需 visual or part support；slat 两端 pin、clip、bushing | `pin_radius`, `clip_style`, `pin_clearance` | S1 / `model.py:L13-L58`; S2 / `model.py:L60-L101`; S4 / `model.py:L173-L264`; S7 / `model.py:L263-L331` |
| `tilt_rod` / `control_rod` | optional but common；竖向操作杆，带 slat clips，可 prismatic 或 fixed | `control_style`, `rod_offset`, `rod_travel`, `rod_guide_count` | S4 / `model.py:L173-L264`; S5 / `model.py:L383-L402`; S7 / `model.py:L263-L349`; S9 / `model.py:L176-L237` |
| `hinge_hardware` | panel hinge / bifold 条件必需；knuckles、barrel、leaf plates、pins | `hinge_style`, `hinge_count`, `hinge_side` | S3 / `model.py:L27-L96`; S4 / `model.py:L97-L171`; S7 / `model.py:L334-L349`; S8 / `model.py:L108-L174`; S11 / `model.py:L78-L136` |
| `support_arm` / `stay_arm` | optional；storm shutter 或 propped-open panel 的侧支撑臂 | `support_arm_enabled`, `support_arm_length`, `support_arm_style` | S11 / `model.py:L214-L342` |
| `linkage_clip_i` | optional；tilt rod 到 slat 的小连杆 / clip，随 rod 或 slat 运动 | `linkage_style`, `clip_count` | S4 / `model.py:L173-L264`; S7 / `model.py:L263-L331`; S9 / `model.py:L176-L237` |
| `decorative_trim` | visual；screws、corner caps、labels、weather strip | `trim_style`, `screw_count` | S3 / `model.py:L27-L96`; S8 / `model.py:L108-L155`; S11 / `model.py:L78-L136` |

## 关节（Joints）
| 关节 | 类型 | axis | origin | range | 描述 | 来源 |
|---|---|---|---|---|---|---|
| `louver_pivot_i` | revolute | `(1, 0, 0)` if slats span X, or leaf local slat-long axis | slat end-pin centerline through both stiles | `[-0.9, 0.9]` typical | 每片百叶围绕自身长轴翻转开合 | S1 / `model.py:L13-L58`; S2 / `model.py:L60-L101`; S4 / `model.py:L224-L264`; S7 / `model.py:L263-L331`; S9 / `model.py:L205-L237`; S11 / `model.py:L260-L299` |
| `tilt_rod_slide` | prismatic | `(0, 0, 1)` or local vertical along leaf | rod guide centerline | `[0, rod_travel]` | 竖向 tilt rod 上下滑动，同步带动 louvers | S4 / `model.py:L173-L264`; S5 / `model.py:L383-L402`; S7 / `model.py:L263-L349` |
| `louver_pivot_i_mimic` | mimic revolute | same as `louver_pivot_i` | same slat pin axis | source=`tilt_rod_slide` or master slat, multiplier / offset defined by linkage | tilt rod / master slat 同步驱动多个百叶角度 | S4 / `model.py:L224-L264`; S5 / `model.py:L383-L402`; S7 / `model.py:L263-L331` |
| `panel_hinge_i` | revolute | `(0, 0, 1)` vertical hinge axis | jamb / panel side hinge line | `[0, 1.65]` | 单扇 / 双扇 shutter leaf 向外打开 | S4 / `model.py:L97-L171`; S7 / `model.py:L334-L349`; S11 / `model.py:L301-L342` |
| `bifold_hinge_i` | revolute | `(0, 0, 1)` vertical hinge axis | between adjacent bifold leaves | `[0, 2.2]` | bifold leaf 之间折叠 | S8 / `model.py:L157-L174`; S9 / `model.py:L253-L365` |
| `support_arm_base_joint` | revolute | `(0, 1, 0)` or side-pin axis | support arm base bracket | `[0, 1.25]` | storm shutter support arm 从 frame / sill 翻出 | S11 / `model.py:L214-L342` |
| `support_arm_tip_joint` | revolute | `(0, 1, 0)` or local pin axis | support arm tip at panel bracket | `[-0.8, 0.8]` | support arm tip 随 panel 开合，optional | S11 / `model.py:L214-L342` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `panel_layout` | enum | `single_panel` / `double_plantation` / `bifold_pair` / `storm_shutter_with_stay` / `fixed_frame_only` | `double_plantation` | 决定 leaf_count、panel hinges、bifold joints and support arm | S1 / `model.py:L13-L58`; S4 / `model.py:L97-L264`; S7 / `model.py:L128-L349`; S8 / `model.py:L25-L365`; S11 / `model.py:L78-L342` |
| `seed_domain` | enum | `plantation_louver_core` / `bifold_review_gated` / `storm_shutter_split_candidate` | `plantation_louver_core` | default seed 只采样 single/double plantation leaf + louver controls；bifold/storm support 需要审核或拆分 | S1 / `model.py:L13-L58`; S4 / `model.py:L97-L264`; S7 / `model.py:L128-L349`; S8 / `model.py:L25-L365`; S11 / `model.py:L78-L342` |
| `frame_style` | enum | `simple_outer_frame` / `window_jamb` / `plantation_frame` / `storm_opening_frame` | `plantation_frame` | controls outer frame and hinge hardware | S1 / `model.py:L13-L58`; S3 / `model.py:L27-L96`; S6 / `model.py:L128-L260`; S11 / `model.py:L78-L136` |
| `frame_width` | float | `0.55-1.8` | `1.0` | leaf widths derive from frame opening and leaf_count | S1 / `model.py:L13-L58`; S3 / `model.py:L27-L96`; S6 / `model.py:L22-L80`; S8 / `model.py:L25-L35` |
| `frame_height` | float | `0.65-2.2` | `1.25` | slat count derives from opening height, rails and pitch | S1 / `model.py:L13-L58`; S6 / `model.py:L22-L80`; S8 / `model.py:L25-L35`; S10 / `model.py:L57-L76` |
| `leaf_count` | int | `1 / 2 / 4` | `2` | from `panel_layout`; bifold pair often 4 leaves | S4 / `model.py:L97-L264`; S8 / `model.py:L25-L174`; S11 / `model.py:L138-L213` |
| `slat_count` | int | `6-24` | `12` | derived by `floor((leaf_height - top_bottom_rails) / min_slat_pitch)` and clamped | S1 / `model.py:L13-L58`; S6 / `model.py:L84-L117`; S10 / `model.py:L57-L76` |
| `slat_profile` | enum | `flat_blade` / `airfoil_beveled` / `curved_cambered` / `thick_wooden` | `airfoil_beveled` | controls slat mesh; pivot axis remains through pin centerline | S6 / `model.py:L84-L117`; S10 / `model.py:L22-L45`; S11 / `model.py:L260-L299` |
| `slat_pitch` | float | `0.045-0.13` | `0.075` | derived / clamped by leaf height and `slat_count` | S1 / `model.py:L13-L58`; S6 / `model.py:L22-L117`; S10 / `model.py:L57-L76` |
| `slat_angle_closed` | float | `-0.45-0.45` rad | `0.15` | closed pose tilt; open range centered around pivot axis | S1 / `model.py:L13-L58`; S4 / `model.py:L224-L264`; S7 / `model.py:L263-L331` |
| `control_style` | enum | `independent_slats` / `tilt_rod_mimic` / `fixed_rod_visual` / `hidden_linkage` | `tilt_rod_mimic` | determines rod part and mimic relationship | S1 / `model.py:L13-L58`; S4 / `model.py:L173-L264`; S5 / `model.py:L383-L402`; S7 / `model.py:L263-L349`; S9 / `model.py:L176-L237` |
| `rod_travel` | float | `0.04-0.22` | `0.11` | mapped to slat angle by linkage multiplier, clamped by rod guides | S4 / `model.py:L173-L264`; S5 / `model.py:L383-L402`; S7 / `model.py:L263-L349` |
| `hinge_style` | enum | `side_barrel` / `bifold_knuckles` / `strap_hinge` / `none` | `side_barrel` | constrained by `panel_layout` | S3 / `model.py:L27-L96`; S8 / `model.py:L108-L174`; S11 / `model.py:L78-L136` |
| `support_arm_enabled` | bool | `true` / `false` | `false` | true for storm shutter with stay arm | S11 / `model.py:L214-L342` |

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| outer frame | simple frame / window jamb / plantation frame / storm opening frame | no | yes | `frame_style` | 影响 hinge mount、panel inset 和外观身份 |
| panel / leaf layout | single panel / double pair / bifold / storm support panel | no | yes | `panel_layout`, `leaf_count` | 主 joint chain 和父子关系不同 |
| slat blade | flat / beveled airfoil / curved cambered / thick wooden | no | yes | `slat_profile` | slat 外形是百叶身份核心，不能只靠厚度表达 |
| slat count / spacing | continuous pitch and count variation within same leaf | yes | no | `slat_count`, `slat_pitch` | 同一 layout 内可以用公式派生 |
| tilt control | independent slats / vertical tilt rod / hidden linkage / fixed visual rod | no | yes | `control_style` | 决定 mimic/prismatic joint semantics |
| hinge hardware | side barrels / bifold knuckles / strap hinge / none | no | yes | `hinge_style` | panel open motion 和视觉 hardware 不同 |
| support arm | none / stay arm with base and tip pivots | no | yes | `support_arm_enabled`, `support_arm_style` | support arm 是额外连杆 topology |
| pins / clips | simple pins / external clips / guide bushings | no | yes | `clip_style` | 决定 slat seating and rod linkage visuals |

## 组合逻辑（Composition Logic）
1. 先采 `frame_width`, `frame_height`, `frame_depth`, `panel_layout`，定义 opening envelope 和 hinge side。
2. 由 frame opening、leaf_count、stile_width、center_gap 派生每个 shutter leaf 的 width / height / origin；叶片不能独立随机漂浮在 frame 内。
3. 对每个 leaf，根据 `rail_height`, `slat_pitch`, `min_slat_clearance` 派生 `slat_count` 和每个 slat center z；公式必须保证最上 / 最下 slat pin 在 top/bottom rails 内侧。
4. `slat_length = leaf_inner_width - 2 * pin_socket_depth`，pivot axis 通过 slat 两端 pin center；slat visual 以该 axis 为局部原点，避免 pivot 偏心。
5. `control_style=independent_slats` 时每片 slat 有自己的 revolute joint；`tilt_rod_mimic` 时设置 master rod prismatic 或 master slat joint，并让其它 slats mimic 同步角度。
6. tilt rod 的 x/y offset 由 leaf side 和 rod guide clearance 派生；rod travel 受 top/bottom rod guides 限制，不能滑出 leaf。
7. panel hinge origin 必须在 jamb / side stile 竖直 hinge line；bifold hinge origin 必须在相邻 leaves 的共享边。
8. support arm 若启用，base joint 在 frame / sill，tip joint 在 panel bracket，closed / open poses 必须与 panel hinge 形成可解释的支撑三角。
9. screws、corner caps、weather strips、decorative trim 作为 frame / leaf visual；只有 panel、slat、rod、support arm 创建活动 part。
10. `resolve_config` 必须执行 panel compatibility matrix：`single_panel` 使用 `leaf_count=1`，可有 side hinge 或 fixed outer frame；`double_plantation` 使用 `leaf_count=2` + side hinges + optional tilt rod；`bifold_pair` 使用 `leaf_count=4` + side hinges + inner bifold hinges，默认 review-gated；`storm_shutter_with_stay` 使用 support arm + storm frame + strap/side hinge，默认 split candidate；`fixed_frame_only` 不生成 panel hinge，只保留 frame 内 slat pivots。
11. S8 bifold hinge helper 和 S11 support arm helper 只能在对应 layout 启用；不得因为它们是 5 星样本就混入普通 double plantation 默认配置。

## 已有模板写法参考
revolute_hinge / mimic_link / prismatic_slide / folding_link_chain / guide_shoe / handle_grip

## 约束
- 必须包含一组平行 louvers，且 slat_count 与实际 `louver_pivot_i` 数量一致。
- slat pivot axis 必须沿 slat 长度方向，并穿过两端 pins；不能绕中心竖轴或随机法线旋转。
- 每片 slat 的 pin 必须位于 leaf side stile 内侧，不能穿出 frame。
- tilt rod 若存在，必须通过 guides 位于 leaf 表面或侧边，rod travel 不得超过 guides。
- panel hinge / bifold hinge axis 必须竖直，并位于 frame jamb 或 leaf side edge。
- support arm 若存在，必须连接 frame 与 panel，不得单端漂浮。
- `panel_layout` 和 `leaf_count` 必须一致；bifold 不允许只生成两片普通 hinged leaves。
- `seed_domain=plantation_louver_core` 时，默认只允许 `single_panel`, `double_plantation`, `fixed_frame_only`；bifold 和 storm support 必须显式审核或拆分。
- `panel_layout`, `leaf_count`, `hinge_style`, `control_style`, `support_arm_enabled` 必须通过兼容矩阵合法化。

## Validator
| 检查项 | 标准 |
|---|---|
| identity | outer/frame or panel + parallel slat array + louver pivot joints present |
| seed domain | default seeds stay inside `plantation_louver_core`; bifold/storm branches are review-gated |
| slat count | `len(louver_pivot_joints) == slat_count * leaf_count` for active-slat leaves |
| slat axis | each louver pivot axis equals slat long axis and passes through end pins |
| slat containment | slat pins and blade extents stay inside leaf frame at closed pose |
| rod linkage | if `control_style=tilt_rod_mimic`, rod has prismatic joint or valid mimic source and slats reference it |
| panel hinge | side/bifold hinges are vertical and placed on jamb / leaf edge |
| support arm | if enabled, base and tip joints connect frame to panel with non-floating endpoints |
| layout consistency | `panel_layout`, `leaf_count`, `hinge_style`, `support_arm_enabled` are compatible |
| compatibility matrix | illegal panel/control/support combinations are downgraded before build |
| part diversity | `frame_style`, `panel_layout`, `slat_profile`, `control_style`, `hinge_style` drive geometry |
| no floating | frames、leaves、slats、pins、rod、hinges、support arm all attach to the same assembly tree |

## Reject cases
- 只有普通窗框，没有可辨识的 louver slat array。
- slats 是固定 visual 且没有任何 louver pivot / mimic joint。
- slat axis 错成竖直轴，运动像门扇而非百叶翻片。
- slat pins 穿出 frame 或 slats 漂浮在 leaf 前方。
- tilt rod 漂浮，或 rod 运动不影响 slats。
- panel hinge 不在 jamb/side edge，打开时整扇窗随机绕中心转。
- bifold layout 没有中间 vertical hinge 或 leaf 数量错误。
- support arm 单端悬空或穿过 shutter panel。
- 普通 plantation double panel 默认配置里同时出现 bifold inner hinges 和 storm support arm。
- S8/S11 的特殊 topology 没有切换 `panel_layout` 就被硬塞进基础 shutter leaf helper。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review. 未进入模板实现阶段。 |
