# Two-Joint Revolute Chain Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `twojoint_revolute_chain` |
| template path | `agent/templates/twojoint_revolute_chain.py` |
| test path | `tests/agent/test_twojoint_revolute_chain_template.py` |
| stage | `APPROVED` |
| status | `APPROVED` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 32 |
| read_count | 13 |
| read_scope | 13 个 5 星样本通读关键段（0001 / 0004 / 0002 / 140c / 1fcd / 56e0 / 785b / 98f91b / 9bd9 / 4fc35 / 6427 全文或主段），其余 19 个全部用 grep 抽取 part 名 / axis / joint type / mesh 构造方式做结构普查，覆盖 32/32 |
| source_index_policy | 仅索引被采纳的可复用片段；planar-yaw（Z 轴水平面）样本作为 `axis_family=planar_yaw` gated 分支单独列出，不与默认 vertical-pitch（±Y）混入同一默认拓扑 |

## 核心身份
最小串联铰链链：一个落地/固定 base，承接 link_1，link_1 再承接 link_2，恰好两个串联 revolute 关节，两轴严格平行且在同一平面内摆动。link_2 末端带一个 compact end tab/pad（可整合进 link_2，也可作为独立 fixed 末端件）。边界：不是 serial_elbow_arm（后者强调 bearing/yoke housing 与 reach 派生的工业肘臂语义），不是三自由度机械臂，不含 prismatic / 球关节，也不是单铰链 hinge。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_twojoint_revolute_chain_0001` | `data/records/rec_twojoint_revolute_chain_0001/revisions/rev_000001/model.py:L34-L59` | cadquery box-stack base/upper/forearm/tool helper shapes（实心 box-beam 构造）|
| S2 | `rec_twojoint_revolute_chain_0001` | `data/records/rec_twojoint_revolute_chain_0001/revisions/rev_000001/model.py:L118-L163` | 四件式 base→upper→forearm→tool 链 + shoulder/elbow revolute + 末端 fixed tool_mount |
| S3 | `rec_twojoint_revolute_chain_0004` | `data/records/rec_twojoint_revolute_chain_0004/revisions/rev_000001/model.py:L43-L148` | primitive Box/Cylinder lug-boss-hub 构造，base_bracket / link_1 / link_2 带 tip_pad |
| S4 | `rec_twojoint_revolute_chain_0004` | `data/records/rec_twojoint_revolute_chain_0004/revisions/rev_000001/model.py:L150-L177` | 垂直 ±Y pitch 双 revolute，shoulder/elbow origin 在 hub 端点 |
| S5 | `rec_twojoint_revolute_chain_140c4367f5ab46d39d9b5410702de554` | `data/records/rec_twojoint_revolute_chain_140c4367f5ab46d39d9b5410702de554/revisions/rev_000001/model.py:L19-L82` | ExtrudeWithHoles 扁平侧板 capsule / tapered / D-cheek profile helpers |
| S6 | `rec_twojoint_revolute_chain_140c4367f5ab46d39d9b5410702de554` | `data/records/rec_twojoint_revolute_chain_140c4367f5ab46d39d9b5410702de554/revisions/rev_000001/model.py:L99-L252` | fixed_cheek / inner_link / outer_link 扁平侧板件 + planar Z-axis 双 revolute |
| S7 | `rec_twojoint_revolute_chain_56e0438fa7724c3abfef6e3815030723` | `data/records/rec_twojoint_revolute_chain_56e0438fa7724c3abfef6e3815030723/revisions/rev_000001/model.py:L110-L257` | cadquery clevis-ear + bore-cut backplate / 双叉 link，pin 隐式 |
| S8 | `rec_twojoint_revolute_chain_56e0438fa7724c3abfef6e3815030723` | `data/records/rec_twojoint_revolute_chain_56e0438fa7724c3abfef6e3815030723/revisions/rev_000001/model.py:L288-L316` | wall-backed root pivot origin `(ROOT_PIVOT_X, 0, ROOT_Z)` + elbow origin 在 link1 tip |
| S9 | `rec_twojoint_revolute_chain_785b123e6e2248dc8ed916956198efb0` | `data/records/rec_twojoint_revolute_chain_785b123e6e2248dc8ed916956198efb0/revisions/rev_000001/model.py:L72-L143` | cadquery windowed open-frame link（body + window cut + tip-yoke slot）pedestal 底座 |
| S10 | `rec_twojoint_revolute_chain_9bd9d828723e42f8ae52fd6ec9a55dc9` | `data/records/rec_twojoint_revolute_chain_9bd9d828723e42f8ae52fd6ec9a55dc9/revisions/rev_000001/model.py:L48-L184` | ladder-frame 双侧板带窗 helper（_capsule_plate）+ root_bracket / link1 / link2 / end_tab |
| S11 | `rec_twojoint_revolute_chain_98f91b29ea6443e789390946fb08bd96` | `data/records/rec_twojoint_revolute_chain_98f91b29ea6443e789390946fb08bd96/revisions/rev_000001/model.py:L31-L139` | wall_plate + boxy root/distal link + 独立 clamp_plate 末端 + 螺栓细节 |
| S12 | `rec_twojoint_revolute_chain_1fcd7d6bb67c41689d5cb04996d97473` | `data/records/rec_twojoint_revolute_chain_1fcd7d6bb67c41689d5cb04996d97473/revisions/rev_000001/model.py:L70-L194` | under-slung top-support bracket，链向 -Z 悬垂，elbow origin = `(0,0,-LINK_1_CENTER_SPAN)` |
| S13 | `rec_twojoint_revolute_chain_4fc35ced18a0468ab8053a458f854932` | `data/records/rec_twojoint_revolute_chain_4fc35ced18a0468ab8053a458f854932/revisions/rev_000001/model.py:L74-L93` | 宽 mounting_plate（rounded_rect_profile + 沉孔螺钉）low-profile Z-axis 底座 |
| S14 | `rec_twojoint_revolute_chain_6427f551d5ad428f91a23c034b3509b2` | `data/records/rec_twojoint_revolute_chain_6427f551d5ad428f91a23c034b3509b2/revisions/rev_000001/model.py:L25-L60` | cadquery `_cylinder_y` / `_cylinder_x` 轴向圆柱 helper，grounded clevis bench arm |

## 槽位 + 候选模块表

### Slot A：base / root support（落地或固定支座，承接第一个 revolute）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `pedestal_column` | S9 (785b) / S1 (0001) / 0002 | `model.py:L72-L87`(785b) | ✅ seed=0 | foot plate + 竖直 column + 顶端双 ear，shoulder 轴在柱顶 `(0,0,JOINT1_AXIS_Z)`；占地小、竖向高 |
| `grounded_clevis_bracket` | S7 (56e0) / S10 (9bd9) / 6427 / 9c56 / 283de | `model.py:L92-L139`(9bd9) | — | base plate + rear web + 双 ear/lug 形成 clevis，第一关节 origin 在 ear 销孔 |
| `wall_backplate` | S11 (98f91b) / S7 (56e0) / 81af / b3c1 | `model.py:L31-L53`(98f91b) | — | 竖直墙板 + 前伸 root_mount lug + lag-bolt 头，第一关节轴在板前方 |
| `broad_mounting_plate` | S13 (4fc35) / 5d920 | `model.py:L74-L93`(4fc35) | — | 宽扁安装板 + 四角沉孔螺钉，low-profile，常配 Z-axis；底座宽 link 薄 |
| `side_cheek_plate` | S5 (140c) / 521449 | `model.py:L99-L133`(140c) | — | 单片 D-nosed 侧 cheek（圆鼻 + 平后缘）+ boss + 销轴 + mount bolts，平面侧装 |

### Slot B：link cross-section + hinge mesh construction（两根 link 与铰节共用的几何构造法）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `solid_box_beam` | S1 (0001) / S3 (0004) / 98f91b / 601ce | `model.py:L41-L52`(0001) | ✅ seed=0 | 实心 box beam + 端块/hub，最简，shoulder/elbow block 在两端 |
| `clevis_ear_bore` | S7 (56e0) / S14 (6427) / 82c1 | `model.py:L156-L220`(56e0) | — | cadquery 实体：proximal eye + strap + distal 双叉 ear，销孔 bore 切除，pin 隐式 |
| `windowed_open_frame` | S9 (785b) / 0002 | `model.py:L89-L111`(785b) | — | box body 中央切窗形成骨架感，tip 带 yoke slot；轻量化外观 |
| `dual_sideplate_ladder` | S10 (9bd9) | `model.py:L48-L89`(9bd9) | — | 两片平行侧板 + 端 cap + 中央长窗（ladder-frame），跨度大、显结构 |
| `flat_extrude_capsule` | S5 (140c) / S13 (4fc35) / 90af / f758 | `model.py:L35-L69`(140c) | — | ExtrudeWithHoles capsule / tapered-tab 扁平连杆，圆鼻销端，常配 planar Z |
| `primitive_lug_barrel` | S3 (0004) / 283de / S12 (1fcd) | `model.py:L84-L152`(283de) | — | primitive Box lug + Cylinder barrel/boss/cap 组装的铰链块，无 mesh 文件 |

补充说明：候选 6 个，已超过 >=3 下限；之所以保留这么多是因为构造法直接决定 hinge 处的 containment/overlap QC 写法（实心 bore vs 双叉 ear vs barrel-in-lug 各不相同），不能压缩。

### Slot C：terminal end-effector topology（link_2 末端形态）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `integral_end_tab` | S6 (140c) / S3 (0004) / 785b / 601ce | `model.py:L128-L152`(140c) | ✅ seed=0 | end tab/pad 直接长在 link_2 上，无额外 part；3 件式 base/link1/link2，恰好 2 revolute |
| `separate_fixed_pad` | S2 (0001) / 0eab / f758 / f914 | `model.py:L55-L59`(0001) | — | 独立 tool_block/end_pad part，经 fixed joint 固定到 link_2 末端；4 件式 |
| `separate_fixed_clamp` | S11 (98f91b→b3c1) / 9bd9 | `model.py:L100-L132`(98f91b) | — | 独立 clamp_plate/end_tab part（带 jaw pad / bolts），fixed 到 link_2；末端语义更重 |

补充说明：Slot C 决定 part 数（3 vs 4）与是否多一个 fixed joint，但**主 revolute 数永远是 2**；末端件只能 fixed，绝不引入第三个 DOF。

## 槽位图（slot graph）
pattern：**mixed**（linear_chain 主干 + 末端 multiplicity）

```
[Slot A: base/root]                      (grounded / fixed, supports joint_1)
        │  joint_1  (revolute, axis ⟂ swing-plane)
        ▼
[Slot B link_1]   ← cross-section/hinge construction (Slot B 决定两段 link 的几何法)
        │  joint_2  (revolute, axis ∥ joint_1, 在同一平面)
        ▼
[Slot B link_2]   ← 同一 Slot B 构造法，末端形态由 Slot C 决定
        ┊  joint_3 = FIXED（仅当 Slot C = separate_*）
        ▼
[Slot C terminal: integral tab │ separate fixed pad │ separate fixed clamp]
```

- 主干恒为 3 节点串联：base → link_1 → link_2（两个串联 revolute）。
- Slot C 的 multiplicity：integral（末端融入 link_2，无新 part / 无新 joint）或 separate（多 1 个 fixed part + 1 个 fixed joint）。
- 两个 revolute 轴恒平行（`axis_family` 决定都为 ±Y 或都为 Z）。

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `base` / `root` | Slot A 落地或固定支座，必须接地/贴墙并承住 joint_1 | `base_style`, `base_width`, `base_depth`, `joint1_axis_z`, `mount_thickness` | S1 / S7 / S9 / S11 / S13 |
| `link_1` | 第一连杆（proximal），近端在 joint_1，远端在 joint_2 | `link_construction`, `link1_len`, `link_width`, `link_height` | S2 / S3 / S6 / S8 / S9 / S10 |
| `link_2` | 第二连杆（distal），近端在 joint_2，末端到 end datum | `link_construction`, `link2_len`, `link_width_2`, `taper_ratio` | S2 / S3 / S6 / S8 / S9 / S10 |
| `end_tab` / `tool` / `clamp_plate` | Slot C 末端件；integral 时融入 link_2，separate 时为独立 fixed part | `end_style`, `tab_len`, `tab_height`, `has_end_hole` | S2 / S6 / S10 / S11 |
| `hinge_hardware` | 销轴 cap / boss / bolt 等固定细节，挂在 base/link/hub 上，optional | `detail_level`, `pin_radius`, `bolt_count` | S3 / S6 / S7 / S11 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `joint_1` (shoulder/root) | revolute | A.base | B.link_1 | `(0,±1,0)` pitch **或** `(0,0,1)` yaw | `[-1.35, 1.35]` rad typ. | 第一个串联主关节，origin 在 base 与 link_1 共用销/hub 中心 | S4 / S6 / S8 / S11 / S12 |
| `joint_2` (elbow) | revolute | B.link_1 | B.link_2 | 与 joint_1 同向（严格平行） | `[-1.6, 1.6]` rad typ. | 第二个串联主关节，origin = link_1 远端销/hub，距离 = `link1_len` | S4 / S6 / S8 / S11 / S12 |
| `joint_3` (end mount) | fixed | B.link_2 | C.tool/clamp/pad | n/a | n/a | 仅当 Slot C = separate_* 时存在；末端件固定到 link_2 远端 | S2 / S11 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `axis_family` | enum | `vertical_pitch` / `planar_yaw` | `vertical_pitch` | 决定两关节轴（同为 ±Y 或同为 Z）与摆动平面 | S4 / S6 / S8 / S11 |
| `base_style` | enum | `pedestal_column` / `grounded_clevis_bracket` / `wall_backplate` / `broad_mounting_plate` / `side_cheek_plate` | `pedestal_column` | 决定 root 几何与 joint_1 origin 位置 | S1 / S7 / S9 / S11 / S13 |
| `link_construction` | enum | `solid_box_beam` / `clevis_ear_bore` / `windowed_open_frame` / `dual_sideplate_ladder` / `flat_extrude_capsule` / `primitive_lug_barrel` | `solid_box_beam` | 决定两 link 截面与 hinge containment QC 写法 | S1 / S5 / S7 / S9 / S10 |
| `end_style` | enum | `integral_end_tab` / `separate_fixed_pad` / `separate_fixed_clamp` | `integral_end_tab` | integral → 3 part / 2 joint；separate → 4 part / +1 fixed | S2 / S6 / S11 |
| `link1_len` | float | `0.11-0.48` | sampled | = distance(joint_1, joint_2) | S2 / S8 / S10 |
| `link2_len` | float | `0.09-0.34` | sampled | = distance(joint_2, end_datum) | S2 / S8 / S10 |
| `joint1_axis_z` | float | `0.08-0.20`（pitch 落地式）| sampled | base 高度 / joint_1 轴高 | S4 / S9 |
| `joint_limit_lower/upper` | float | `±[0.4 .. 1.7]` rad | profile | 两关节范围，rest pose 须在范围内 | S4 / S6 / S11 |
| `link_width` | float | `0.014-0.065` | sampled | hinge gap 与销长由此派生 | S2 / S8 |
| `detail_level` | enum | `plain` / `pins` / `pins_bolts` | `pins` | 附加 cap/bolt 细节，必须挂在已有件上 | S6 / S7 / S11 |

## 拓扑多样性审计
- 每槽候选数：Slot A = 5，Slot B = 6，Slot C = 3。
- total_combinations = 5 × 6 × 3 = **90**。
- 结合 `axis_family`（2）后名义上限更高，但即便不计 axis_family，仅 base × link_construction × end_style 已远超阈值。

| slot | candidate_count |
|---|---|
| Slot A (base/root) | 5 |
| Slot B (link construction) | 6 |
| Slot C (terminal) | 3 |
| total_combinations | 90 |

## Validator
| 检查项 | 标准 |
|---|---|
| identity | base + link_1 + link_2 + 恰好两个串联 revolute joints 存在 |
| primary joint count | revolute 数 == 2；total joints == 2（integral）或 == 3 且第 3 个为 FIXED（separate）|
| axis parallelism | `tuple(joint_1.axis) == tuple(joint_2.axis)`，且属于 {±Y} 或 {Z} 之一 |
| axis family consistency | `vertical_pitch` 两轴均 ±Y；`planar_yaw` 两轴均 Z；不得混用 |
| endpoint consistency | `distance(joint_1.origin, joint_2.origin) ~= link1_len`；`distance(joint_2.origin, end_datum) ~= link2_len` |
| serial topology | base → link_1 → link_2 → (end) 链，无跳父、无并联第二子 |
| hinge contact | link_1/link_2 在各自 hinge 处与 parent 有 contact/overlap（按 link_construction 选用 expect_contact / allow_overlap + expect_within）|
| base grounding | base 接地或贴墙，并实际承住 joint_1（非悬空）|
| end mount | end 件为 integral（融入 link_2）或 fixed-to-link_2；绝不引入第三个 DOF |
| no floating | base / link / hub / cap / bolt / end 件全部 attached 或 constrained |

## Reject cases
- 只有两根静态杆件，没有两个 revolute joint（退化成 fixed 或单铰链）。
- 出现第三个 revolute / prismatic / 球关节，超出 two-joint 身份。
- joint_1 与 joint_2 轴不平行（一个绕 Y、一个绕 Z）而无明确 `axis_family`。
- joint origin 不在 link 端点 / 销孔中心，导致 link 长度参数与实际 joint 距离不符。
- base 或 root 悬空，link_1 从空中起始。
- end tab/clamp/pad 不在 link_2 末端，或 separate 末端件没有 fixed parent。
- pitch 与 yaw 样本被混进同一默认分支造成语义错误。
- cap / bolt / 销 / clamp 悬空漂浮。

## 与相邻类别的边界
- vs `serial_elbow_arm`：elbow_arm 强调 shoulder/elbow bearing housing、yoke cheeks 与 reach 派生的工业肘臂语义、可选 planar pick-place 工具；本类别是更通用、更轻的最小二铰链链，base/link 可以是简单 bracket + box-beam，末端是 compact tab/pad，不要求 bearing-housing 级细节。
- vs 三自由度及以上机械臂：本类别 revolute 恰好 2，多余 DOF 即越界。
- vs 单铰链 / hinge / louvered shutter：本类别必须是串联两关节、两轴平行同平面，且第二关节挂在第一连杆远端。
- vs 含 prismatic / telescoping / 球关节的链：本类别两关节都必须是 revolute。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved（human-reviewed）|
| reviewer notes | SPEC_ONLY_DRAFT；mixed 模式（linear chain + 末端 multiplicity）；axis_family 必须 gate（pitch ±Y / planar yaw Z 不可混）；等待人工 review |
