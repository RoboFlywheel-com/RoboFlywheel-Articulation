# Robotic Arms Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `robotic_arms` |
| template path | `agent/templates/robotic_arms.py` |
| test path | `tests/agent/test_robotic_arms_template.py` |
| stage | `APPROVED` |
| status | `APPROVED` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 31 |
| read_count | 8 |
| read_scope | 8 个 5 星样本完整通读（覆盖 3-joint 极简 / 6-DOF turret+灵巧手 / 平行夹爪 / 球腕 / roll-flange / wrist roll-pitch 顺序互换 / 重型 turret / 桌面级），其余 23 个用 grep 提取 part 名、articulation 签名（type/parent/child/axis）、关节/部件计数、end-effector 与 mesh 构造方式做全量扫描 |
| source_index_policy | 只索引被采纳的可复用 part/joint 片段；六轴 + 多指灵巧手（5 条手指链）和平行夹爪都作为 end-effector slot 的 gated 候选，不混进默认 fixed-flange 分支；wrist DOF 数作为独立 slot，不靠 reach 缩放糊弄 |

## 核心身份
台式/工业串联机械臂，必须包含落地 base/pedestal、绕竖直 Z 的 base yaw、shoulder_pitch + elbow_pitch 两个平行轴主关节，以及连接它们的 upper_arm 与 forearm 串联连杆。腕部（pitch/roll/yaw 的 1-3 DOF 组合）和末端执行器（fixed flange / roll flange / 平行夹爪 / 灵巧手）沿串联链向远端扩展。边界：它不是单肩肘的二连杆 `serial_elbow_arm`（那个默认无 base yaw、无 wrist），也不是 pan-tilt 云台或伸缩臂；本类的身份是「base yaw + 双 pitch + 可扩展 wrist/末端」的多 DOF 拟人/工业臂。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_robotic_arms_a0610297f2d749b3bd3ce8a85fd1bd3e` | `data/records/rec_robotic_arms_a0610297f2d749b3bd3ce8a85fd1bd3e/revisions/rev_000001/model.py:L19-L58` | reach 常量（`UPPER_LEN`/`FOREARM_LEN`）、pedestal+turntable（shoulder 折进 upper_arm 的 combined-base 写法） |
| S2 | `rec_robotic_arms_a0610297f2d749b3bd3ce8a85fd1bd3e` | `data/records/rec_robotic_arms_a0610297f2d749b3bd3ce8a85fd1bd3e/revisions/rev_000001/model.py:L60-L210` | box_beam upper_arm（带 elbow fork+pin）、forearm beam、紧凑 wrist_head（roll flange）与三关节链 shoulder_yaw/elbow_pitch/wrist_roll |
| S3 | `rec_robotic_arms_9ed009fdf0844d298af6ecdbf3748d66` | `data/records/rec_robotic_arms_9ed009fdf0844d298af6ecdbf3748d66/revisions/rev_000001/model.py:L26-L210` | `_bolt_circle` 螺栓盘 helper、重型 pedestal+yaw_socket、独立 yaw turret（drum+deck+shoulder yoke）作为 yaw_turret 候选 |
| S4 | `rec_robotic_arms_9ed009fdf0844d298af6ecdbf3748d66` | `data/records/rec_robotic_arms_9ed009fdf0844d298af6ecdbf3748d66/revisions/rev_000001/model.py:L214-L470` | ribbed cast upper_arm/forearm/wrist/tool_flange 部件，CONTINUOUS base_yaw + 末端 roll-flange 五关节链 |
| S5 | `rec_robotic_arms_253b238964e940dbbeba044d0bb10531` | `data/records/rec_robotic_arms_253b238964e940dbbeba044d0bb10531/revisions/rev_000001/model.py:L32-L151` | yaw_carriage（datum turntable + yaw spindle + pitch cheeks）、captured-axle yoke 几何、wrist roll→pitch 顺序互换的 2-DOF 腕（roll 在前，pitch 接 tool_plate） |
| S6 | `rec_robotic_arms_16221926757646e0a4f3318673911433` | `data/records/rec_robotic_arms_16221926757646e0a4f3318673911433/revisions/rev_000001/model.py:L205-L290` | 3-DOF 球腕（wrist_yaw + wrist_pitch + tool_roll 串联三段）+ palm，配合下游夹爪 |
| S7 | `rec_robotic_arms_16221926757646e0a4f3318673911433` | `data/records/rec_robotic_arms_16221926757646e0a4f3318673911433/revisions/rev_000001/model.py:L277-L372` | 平行夹爪：两根 finger 部件 + 两个 PRISMATIC `finger_slide` 用 `Mimic` 对称开合 |
| S8 | `rec_robotic_arms_d13e0c2a54754a2aa1ac8d23a87dd008` | `data/records/rec_robotic_arms_d13e0c2a54754a2aa1ac8d23a87dd008/revisions/rev_000001/model.py:L133-L283` | cadquery `_finger_body` + wrist_pitch/wrist_roll(CONTINUOUS) 2-DOF 腕 + 两指 PRISMATIC mimic 夹爪（带 rubber pad） |
| S9 | `rec_robotic_arms_0001` | `data/records/rec_robotic_arms_0001/revisions/rev_000001/model.py:L289-L357` | `_add_digit_chain` helper：把一根三段手指链（proximal/middle/distal + 三个 REVOLUTE）以 parallel children 形式挂到 palm 上 |
| S10 | `rec_robotic_arms_0001` | `data/records/rec_robotic_arms_0001/revisions/rev_000001/model.py:L422-L810` | 六轴主链（base_yaw turret + shoulder/elbow/wrist_pitch/wrist_roll）、superellipse link shell、灵巧手 palm + 5 指 parallel 装配 |
| S11 | `rec_robotic_arms_b04b60f1f1cb48e1a9bf2fe03b9da825` | `data/records/rec_robotic_arms_b04b60f1f1cb48e1a9bf2fe03b9da825/revisions/rev_000001/model.py:L219-L332` | wrist_pitch_module + wrist_roll_module（roll output can + tool_body + flange）的 2-DOF roll-flange 腕，CONTINUOUS 末端 roll |
| S12 | `rec_robotic_arms_889477f5978f4a08a87bb80c115416f1` | `data/records/rec_robotic_arms_889477f5978f4a08a87bb80c115416f1/revisions/rev_000001/model.py:L135-L187` | gripper_base（wrist roll 段）+ left_jaw/right_jaw 两个对称 PRISMATIC 爪（cadquery fork 几何，captured pivot allow_overlap） |

## 槽位 + 候选模块表

### Slot A：base_yaw_root（落地底座 + 绕 Z 的 base yaw）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `combined_shoulder_base` | S1/S2 (`a0610...`) | `model.py:L34-L58` | yes | pedestal+turntable，无独立 yaw 部件；yaw 关节直接 base→upper_arm（shoulder 折进 upper_arm 根部）；最少 part 数 |
| `yaw_turret` | S3/S4 (`9ed009...`) | `model.py:L145-L210` | no | 独立 turret 部件（yaw drum + deck + shoulder yoke cheeks + shoulder pin），base→turret yaw，turret→upper_arm pitch；适合重型/工业 |
| `yaw_carriage` | S5 (`253b...`) | `model.py:L32-L60` | no | 独立 carriage/shoulder 部件（datum turntable + yaw spindle/bearing + riser block + pitch cheeks），带 datum rail；精密/桌面常用 |

### Slot B：shoulder_elbow_link（upper_arm + forearm 两段 + shoulder_pitch/elbow_pitch）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `box_beam_link` | S2 (`a0610...`) | `model.py:L60-L147` | yes | 矩形 beam + 端部 fork+pin + service cover；shoulder hub 在近端、elbow fork 在远端，primitive Box/Cylinder |
| `ribbed_cast_link` | S4 (`9ed009...`) | `model.py:L214-L356` | no | 铸造风 box beam + 侧 rib + 大 shoulder bearing 圆筒 + 偏置 elbow cartridge，重型外观 |
| `forked_yoke_link` | S5 (`253b...`) | `model.py:L61-L98` | no | 开放 yoke/fork 双 cheek 包 captured axle（elbow_fork + elbow_axle + bored bearings），datum 友好 |

### Slot C：wrist_module（腕部 DOF：沿串联链向远端扩展 0-3 个旋转关节）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `wrist_1dof_roll` | S2 (`a0610...`) | `model.py:L149-L208` | yes | 单段 wrist_head，forearm→wrist 一个 roll（X 轴）关节，紧凑 tool flange；最短腕 |
| `wrist_2dof_pitch_roll` | S11 (`b04b60...`) | `model.py:L219-L332` | no | wrist_pitch_module（-Y 轴）→ wrist_roll_module（X 轴）两段串联，标准工业腕 |
| `wrist_2dof_roll_pitch` | S5 (`253b...`) | `model.py:L88-L151` | no | wrist（roll，X 轴）→ tool_plate（pitch，-Y 轴），与上一候选关节顺序互换 |
| `wrist_3dof_spherical` | S6 (`16221...`) | `model.py:L205-L290` | no | wrist_yaw(Z) → wrist_pitch(Y) → tool_roll(X) 三段球腕，最高自由度 |

### Slot D：end_effector（末端执行器，挂在 wrist 末端 datum）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `fixed_flange` | S2/S4 (`a0610...`/`9ed009...`) | `model.py:L149-L181`(S2 wrist_head) | yes | 末端就是 tool flange/mounting face，fixed，无额外 DOF；最简单 |
| `roll_flange` | S4/S11 (`9ed009...`/`b04b60...`) | `model.py:L400-L470`(S4) | no | 末端独立 tool_flange 部件 + 一个 roll 关节（REVOLUTE/CONTINUOUS, X 轴），输出法兰可转 |
| `parallel_gripper` | S7/S8/S12 | `model.py:L277-L372`(S7) | no | gripper palm/base + `finger_count` 根 finger 部件 + 各一个 PRISMATIC 开合关节，全部归入同一个 `Mimic` 组（主关节驱动、其余 mimic）。**`finger_count=2`(样本默认)**：两指对置(±方向)沿夹持轴相向滑。**`finger_count=3`(参数外推，样本无)**：三指绕掌心轴按 `120°` 等分布置，每指 PRISMATIC 沿各自径向向心滑、同 Mimic 组同步；palm 由 2 指的矩形掌改为正三角/圆盘掌以容纳 3 个均布滑座。带 rubber pad |
| `dexterous_hand` | S9/S10 (`0001`) | `model.py:L289-L357`(S9 `_add_digit_chain`)、L422-L810(S10 5 指装配) | no | palm + **恒 5 条**三段手指链（每指 proximal/middle/distal + 3 个 REVOLUTE，复用 `_add_digit_chain`），parallel children 挂同一 palm；gated 高复杂度分支。**直接复刻样本 S10 的 5 指布局**：4 指沿掌缘前排均布 + 1 拇指侧向偏置相位；不外推 3/4 指（无样本支撑，易畸形）。手的多样性走"是否选 dexterous_hand"这一 enum 维度，不靠指数变化 |

## 槽位图（slot graph）
- pattern：**mixed**（主体 linear_chain，末端 multiplicity）
- 主串联链（每个 slot 选 1）：

```
[Slot A base_yaw_root] --base_yaw(Z)--> shoulder_pitch link root
        |
        +--shoulder_pitch(±Y)--> [Slot B upper_arm]
                                      |
                                      +--elbow_pitch(±Y)--> [Slot B forearm]
                                                                |
                                                                +--(Slot C wrist joints, 1-3 段串联)--> wrist tip
                                                                                                            |
                                                                                                            +--(Slot D end effector)
```

- Slot C 是「可变长串联段」：1dof = +1 part/+1 joint；2dof = +2；3dof = +3，全部沿同一条链顺接，axis 在 Z/±Y/X 间切换但同一段内自洽。
- Slot D 的 `parallel_gripper` / `dexterous_hand` 在链末端引入 multiplicity：从同一个 palm/gripper_base 并联挂 2 根手指（夹爪）或 N 条手指链（灵巧手），这是 mixed 模式里唯一的 parallel-children 分叉点。
- combined_shoulder_base（Slot A）会少一个独立 yaw 部件：base yaw 关节直接连到 upper_arm；其余两个候选多一个 turret/carriage 中间部件。

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `base` / `pedestal` | 落地底座、floor plate/plinth、column、yaw bearing/socket、anchor bolts，必须接地 | `base_style`, `base_radius`, `base_z`, `yaw_bearing_radius` | S1 / S3 / S5 |
| `turret` / `carriage` / `shoulder` | 可选 yaw 旋转部件（drum/deck + shoulder yoke/cheeks），承接 shoulder_pitch | `yaw_root_style`, `cheek_thickness`, `shoulder_gap` | S3 / S5 |
| `upper_arm` | 近端连杆：shoulder hub + beam + elbow fork/cartridge | `upper_len`, `link_style`, `upper_width`, `upper_height` | S2 / S4 / S5 / S10 |
| `forearm` | 远端连杆：elbow hub/lug + beam + wrist bearing/seat | `forearm_len`, `forearm_width`, `forearm_height`, `link_style` | S2 / S4 / S5 / S10 |
| `wrist` / `wrist_pitch` / `wrist_yaw` / `tool_roll` | 腕部 1-3 段，根据 wrist_dof 串联，每段一个 hub + 短 link | `wrist_dof`, `wrist_order`, `wrist_scale` | S2 / S5 / S6 / S11 |
| `tool_flange` / `tool_plate` / `gripper_base` / `palm` | 末端载体：法兰、夹爪掌、灵巧手掌 | `end_effector_style`, `flange_radius`, `tool_offset` | S2 / S4 / S7 / S9 / S11 |
| `finger_i`（i=0..N-1，含 `left_jaw`/`right_jaw`/`thumb` 别名）| 夹爪指或灵巧手指链，共 `finger_count`(N) 根，均匀挂在 palm/gripper_base 上（夹爪 `360°/N` 等分、手沿掌缘均布）| `finger_count`, `finger_len`, `finger_travel` | S7 / S8 / S9 / S10 / S12 |
| `bolts` / `covers` / `cable_cover` / `nameplate` | shoulder/elbow/yaw 螺栓盘、service cover、cable cover 等固定细节 | `detail_level`, `bolt_count` | S2 / S3 / S4 / S5 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `base_yaw` | revolute / continuous | A.base | A.turret 或 B.upper_arm | `(0,0,1)` | `[-pi, pi]` 或 continuous | 绕竖直 Z 的回转，combined-base 时直接连 upper_arm | S1 / S3 / S5 / S6 / S10 |
| `shoulder_pitch` | revolute | A.turret/carriage 或 A.base | B.upper_arm | `(0,1,0)` 或 `(0,-1,0)` | `[-0.25, 1.6]` typical | 第一个 pitch 主关节 | S2 / S4 / S5 / S6 / S10 |
| `elbow_pitch` | revolute | B.upper_arm | B.forearm | `(0,1,0)` 或 `(0,-1,0)` | `[-1.25, 2.75]` typical，轴与 shoulder 平行 | 第二个 pitch 主关节 | S2 / S4 / S5 / S6 / S10 |
| `wrist_pitch` | revolute | B.forearm 或 C.wrist_yaw | C.wrist_pitch | `(0,±1,0)` | `[-1.85, 1.85]` typical | 2dof/3dof 腕的 pitch 段 | S5 / S6 / S10 / S11 |
| `wrist_roll` | revolute / continuous | B.forearm 或 C.wrist_pitch | C.wrist 或 D.tool_flange | `(1,0,0)` | `[-pi, pi]` 或 continuous | 1dof/2dof 腕的 roll 段，沿 forearm 轴线 | S2 / S5 / S11 |
| `wrist_yaw` | revolute | B.forearm | C.wrist_yaw | `(0,0,1)` | `[-1.9, 1.9]` typical | 仅 3dof 球腕的首段 | S6 |
| `tool_roll` | revolute / continuous | C.wrist_pitch | D.tool_roll | `(1,0,0)` | `[-pi, pi]` | 3dof 球腕末段 roll | S6 |
| `tool_fixed` | fixed | C.wrist | D.tool_flange | n/a | n/a | fixed_flange 末端固定 | S2 / S4 |
| `finger_slide` | prismatic | D.gripper_base | D.finger/jaw | `(0,±1,0)` 或 `(±1,0,0)` | `[0, 0.01-0.036]` | 平行夹爪开合，对侧用 `Mimic` 同步 | S7 / S8 / S12 |
| `finger_mcp/pip/dip` | revolute | D.palm 或上一指节 | D.finger 指节 | `(0,1,0)` | `[0, 1.0-1.4]` | 灵巧手每指三段屈曲，parallel children | S9 / S10 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `base_style` / `yaw_root_style` | enum | `combined_shoulder_base` / `yaw_turret` / `yaw_carriage` | `combined_shoulder_base` | 决定是否有独立 yaw 部件及 base_yaw 的 child | S1 / S3 / S5 |
| `link_style` | enum | `box_beam` / `ribbed_cast` / `forked_yoke` | `box_beam` | 决定 upper_arm/forearm 截面与 yoke 写法 | S2 / S4 / S5 |
| `wrist_dof` | enum | `1dof_roll` / `2dof_pitch_roll` / `2dof_roll_pitch` / `3dof_spherical` | `1dof_roll` | 决定 wrist 段数与关节轴序列 | S2 / S5 / S6 / S11 |
| `end_effector_style` | enum | `fixed_flange` / `roll_flange` / `parallel_gripper` / `dexterous_hand` | `fixed_flange` | 决定末端 part 与是否引入 parallel children | S2 / S4 / S7 / S9 |
| `total_reach` | float | `0.45-1.50` | sampled | `upper_len + forearm_len + wrist_len + tool_offset` | S1 / S2 / S10 |
| `link_ratio` | float | `0.48-0.58` | sampled | `upper_len = (total_reach - wrist_len - tool_offset) * link_ratio` | S1 / S2 |
| `upper_len` | float | derived, min `0.18` | derived | distance shoulder_origin → elbow_origin | S2 / S10 |
| `forearm_len` | float | derived, min `0.16` | derived | distance elbow_origin → wrist_origin | S2 / S10 |
| `base_z` | float | `0.10-0.60` | sampled | base 高度 + shoulder/yaw bearing 中心 | S1 / S3 / S5 |
| `joint_limit_profile` | enum | `industrial_safe` / `wide_range` / `compact_service` | `industrial_safe` | 设定各关节 range | S2 / S6 / S10 |
| `finger_count` | int | `parallel_gripper`: `2 / 3`（权重 `{2:0.75, 3:0.25}`，偏 2，multiplicity 唯一变量）；`dexterous_hand`: 恒 `5`（直接复刻样本 S10，不外推 3/4 指） | 夹爪 `2`、灵巧手 `5` | 夹爪指绕掌心轴 `360°/N` 等分（2=对置、3=三爪 120°）且同属一个 `Mimic` 组同步开合；灵巧手恒 5 指（4 指前排均布 + 1 拇指偏置），复用 S10 的 `_add_digit_chain`，每指 proximal/middle/distal 三段 REVOLUTE | S7 / S9 / S10 |
| `finger_travel` | float | `0.010-0.036` | sampled | 平行夹爪 prismatic 行程 | S7 / S8 / S12 |
| `detail_level` | enum | `clean` / `bolts` / `industrial` | `clean` | 螺栓盘/cover/cable 装饰密度 | S3 / S4 / S5 |

## 拓扑多样性审计
- total combinations = `len(Slot A) * len(Slot B) * len(Slot C) * len(Slot D)` = `3 * 3 * 4 * 4` = **144**

| slot | candidate_count |
|---|---|
| Slot A base_yaw_root | 3 |
| Slot B shoulder_elbow_link | 3 |
| Slot C wrist_module | 4 |
| Slot D end_effector | 4 |
| product | 144 |

## Validator
| 检查项 | 标准 |
|---|---|
| identity | base + base_yaw(Z) + shoulder_pitch + elbow_pitch + upper_arm + forearm 全部存在 |
| primary joints | 至少含 base_yaw、shoulder_pitch、elbow_pitch 三个主关节；shoulder/elbow pitch 轴平行（同为 ±Y） |
| yaw axis | base_yaw 轴为 `(0,0,1)`；combined-base 时其 child 是 upper_arm，否则是 turret/carriage |
| serial topology | base →(turret/carriage?)→ upper_arm → forearm → wrist 段 → end effector，单链无跳级 parent |
| endpoint consistency | `distance(shoulder_origin, elbow_origin) ~= upper_len`；`distance(elbow_origin, wrist_origin) ~= forearm_len` |
| wrist chain | wrist_dof 段数与实际 wrist 关节数一致；每段轴在 Z/±Y/X 内取值且 hub 位于上一段末端 |
| end effector attach | fixed_flange 用 fixed；roll_flange 末端 roll 关节；gripper `finger_count` 指各一 PRISMATIC、绕掌心 `360°/N` 等分、同属一个 Mimic 组同步；hand `finger_count` 条指链挂 palm 且每指三段 REVOLUTE、沿掌缘均布 |
| finger multiplicity | 夹爪 `finger_count`∈{2,3} 是唯一可变指数：几何同构、绕掌心 `360°/N` 等分、同 Mimic 组（N=2 对置、N=3 三爪 120°）；灵巧手恒 5 指（复刻 S10，不可变）|
| grounding | base 接地，turret/carriage（若有）坐落 base 顶面 yaw bearing |
| no floating | 所有 link/hub/finger/cover/bolt/flange 都有 attached 或 captured（yoke 内）几何 |

## Reject cases
- 没有 base yaw 关节，或 yaw 轴不是竖直 Z（退化成纯肩肘二连杆 `serial_elbow_arm`）。
- shoulder_pitch 与 elbow_pitch 轴不平行（一个 Y、一个 Z 且无明确分支）。
- upper_len/forearm_len 参数与实际 joint 间距不一致，连杆从空中起跳。
- wrist_dof 声明 2/3 段但实际只接了一个关节，或 wrist hub 不在上一段末端。
- 平行夹爪各指不等分/不对称 / 没有 Mimic 同步 / 用 revolute 冒充滑动开合 / finger_count 不在 {2,3}。
- 灵巧手指节漂浮、不挂 palm，或某指段数与其它指不一致 / 灵巧手指数不是 5（本类灵巧手恒 5 指，不做 3/4 指外推）。
- finger_count 与实际挂出的 finger 部件数不符，或夹爪多根手指相位不均匀（重叠/偏挤在一侧）。
- end effector 或 tool flange 没有 fixed/roll parent，悬空。
- base 或 turret/carriage 漂浮，不接地。
- 螺栓盘、cover、cable、nameplate 等装饰悬空，不挂在 base/link/hub 上。

## 与相邻类别的边界
- `serial_elbow_arm`：默认无 base yaw、无 wrist DOF 的二连杆 pitch/yaw elbow arm。本类必须含 base_yaw 且常带 1-3 DOF wrist 与可换末端，是它的多 DOF 超集；不要把无 yaw 无 wrist 的样本塞进 robotic_arms 默认分支。
- pan-tilt 监控云台：只有 yaw+pitch 两轴且末端是相机头，没有 shoulder/elbow 连杆链。
- `telescoping_boom` / `cantilever_articulated_arm`：以伸缩或单悬臂为主，缺少 base yaw + 双 pitch + wrist 的完整串联骨架。
- 平行夹爪/灵巧手只能作为本类 end_effector slot 的 gated 候选出现，独立的 gripper/hand 不属于 robotic_arms。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved（human-reviewed）|
| reviewer notes | SPEC_ONLY_DRAFT; waiting for human review |
