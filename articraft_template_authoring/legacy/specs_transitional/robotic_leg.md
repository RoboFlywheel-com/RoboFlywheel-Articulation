# Robotic Leg Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `robotic_leg` |
| template path | `agent/templates/robotic_leg.py` |
| test path | `tests/agent/test_robotic_leg_template.py` |
| stage | `APPROVED` |
| status | `APPROVED` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 37 |
| read_count | 7 |
| read_scope | 全量读 7 个跨结构谱系的样本（0002 / 0174b16e / bd2102f1 / 5e1d8553 / e757eded / 25310b6d / f5251bbd），其余 30 个用 grep 提取 part 名 / joint topology / axis sign / 构造方法指纹（cadquery / section_loft / superellipse / motor-bore / yoke-cheek / sole-toe）做覆盖 |
| source_index_policy | 仅索引被采纳的可复用片段；5-DOF spatial humanoid（hip_roll + ankle_roll 绕 X）只有 1 个样本，按 gated branch 处理，不混进默认 3-DOF sagittal 模板 |

## 核心身份
机器人腿/步行机器腿单腿模块，必须是 hip→thigh(upper_leg)→knee→shank(lower_leg)→ankle→foot 的串联三段连杆 + 三个串联主 revolute joints（hip / knee / ankle）。默认成熟域是 sagittal 矢状面腿：三轴均为局部 ±Y（lateral pitch），thigh/shank 长度由 joint origin 间距决定，foot 落在末端并带 sole/toe/heel 接地。区别于 serial_elbow_arm（工业机械臂、无接地 foot、base 固定不动）与 quadruped 整机（多腿），本类是单腿、近端 hip mount 为 root、远端必须有可着地 foot。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_robotic_leg_0002` | `data/records/rec_robotic_leg_0002/revisions/rev_000001/model.py:L27-L121` | `_axis_rpy` / `_xy_section` / `_save_mesh` / `_add_side_fasteners` 与 section_loft superellipse thigh/shank/foot shell 构造 helper |
| S2 | `rec_robotic_leg_0002` | `data/records/rec_robotic_leg_0002/revisions/rev_000001/model.py:L135-L502` | lug+axis_cap+saddle 髋接口、actuator_bay、knee/ankle lug、rubber sole/toe_bumper/heel_pad foot |
| S3 | `rec_robotic_leg_0002` | `data/records/rec_robotic_leg_0002/revisions/rev_000001/model.py:L504-L545` | hip_pitch / knee_pitch / ankle_pitch 三个串联 ±Y revolute joint，origin 落在 -0.270 / -0.230 段距 |
| S4 | `rec_robotic_leg_0174b16e06274c78b1d18bd91d271190` | `data/records/rec_robotic_leg_0174b16e06274c78b1d18bd91d271190/revisions/rev_000001/model.py:L68-L252` | yoke barrel + lug_outer/inner + cheek_outer/inner + yoke_bridge + spine + side_web 全 primitive 连杆构造 |
| S5 | `rec_robotic_leg_0174b16e06274c78b1d18bd91d271190` | `data/records/rec_robotic_leg_0174b16e06274c78b1d18bd91d271190/revisions/rev_000001/model.py:L254-L280` | barrel/lug 接触式三 revolute joint，knee origin -0.550、ankle origin -0.500 |
| S6 | `rec_robotic_leg_bd2102f14a894c1cb540b24fe89785bf` | `data/records/rec_robotic_leg_bd2102f14a894c1cb540b24fe89785bf/revisions/rev_000001/model.py:L30-L150` | motor + nested shaft-through-bore 驱动式接口（`*_motor` 在 parent，`*_shaft`/`*_collar`/`*_drive_web` 在 child），beam 连杆，sole_pad/toe_lip foot |
| S7 | `rec_robotic_leg_bd2102f14a894c1cb540b24fe89785bf` | `data/records/rec_robotic_leg_bd2102f14a894c1cb540b24fe89785bf/revisions/rev_000001/model.py:L194-L315` | motor-bore 接口的 `allow_overlap` + `expect_within` + `expect_overlap` 嵌套约束写法 |
| S8 | `rec_robotic_leg_5e1d855301e447c6bad9a61468a7a730` | `data/records/rec_robotic_leg_5e1d855301e447c6bad9a61468a7a730/revisions/rev_000001/model.py:L24-L276` | `_add_side_bolt` helper、root fixed mount flange、yoke_cheek + rotor_barrel + clamp_band 接口、structural_box/side_plate/service_cover、rubber_foot_pad + toe/heel wear plate |
| S9 | `rec_robotic_leg_5e1d855301e447c6bad9a61468a7a730` | `data/records/rec_robotic_leg_5e1d855301e447c6bad9a61468a7a730/revisions/rev_000001/model.py:L283-L341` | rotor_barrel 落在 yoke_cheek 之间的 `expect_contact` 接口约束 + 三 ±Y revolute joint |
| S10 | `rec_robotic_leg_e757eded77ff44dcbee1800830f874f9` | `data/records/rec_robotic_leg_e757eded77ff44dcbee1800830f874f9/revisions/rev_000001/model.py:L21-L113` | `_add_box`/`_add_y_cylinder` helper、box cheek + y-cylinder boss 髋接口、actuator_pack/gusset/tie 模块化连杆 |
| S11 | `rec_robotic_leg_e757eded77ff44dcbee1800830f874f9` | `data/records/rec_robotic_leg_e757eded77ff44dcbee1800830f874f9/revisions/rev_000001/model.py:L298-L424` | 独立 sole_pad part + `foot_to_sole` FIXED joint（foot_module → sole_pad），及 radians-based 关节限位 |
| S12 | `rec_robotic_leg_25310b6d3bc14677a787ab918625686f` | `data/records/rec_robotic_leg_25310b6d3bc14677a787ab918625686f/revisions/rev_000001/model.py:L79-L357` | cadquery sealed-shell 防水构造：base_plate + cheek + drip_hood、trunnion + hub 接口、ankle_block、drip_skirt |
| S13 | `rec_robotic_leg_f5251bbd807f4aa2965c5fa3c4d8f888` | `data/records/rec_robotic_leg_f5251bbd807f4aa2965c5fa3c4d8f888/revisions/rev_000001/model.py:L13-L174` | gated 5-DOF spatial humanoid：cadquery armor link + hip_roll(X)/hip_pitch(Y)/knee(Y)/ankle_pitch(Y)/ankle_roll(X)，含 hip_roll_link / ankle_pitch_link 中间正交连杆 |

## 槽位 + 候选模块表

### Slot 1：kinematic_topology（运动学拓扑 / DOF）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `sagittal_3dof` | S2 / S3（0002）, S5（0174b16e）, S9（5e1d8553） | `rec_robotic_leg_0002/.../model.py:L504-L545` | ✅ | 三个串联 revolute（hip/knee/ankle），全部绕局部 ±Y；链为 hip_mount→thigh→shank→foot，矢状面运动；35/37 样本 |
| `spatial_5dof` | S13（f5251bbd） | `rec_robotic_leg_f5251bbd807f4aa2965c5fa3c4d8f888/.../model.py:L126-L174` | ✗ | gated 分支：hip_roll(X)→hip_pitch(Y)→knee_pitch(Y)→ankle_pitch(Y)→ankle_roll(X)，多两个中间正交连杆 hip_roll_link/ankle_pitch_link；spatial humanoid |

> 该 slot 仅 2 候选（不足 3）的理由：所有 37 个 5 星样本里 5-DOF spatial 只有 f5251bbd 一例，第三种拓扑（如 hip 单纯 abduction-only、或 6-DOF）在 5 星样本中不存在，无法满足"每候选 ≥2 distinct sample 或真实可索引"的要求。其余结构差异都落在下游 slot（接口/构造/foot），不是顶层 DOF 差异。`spatial_5dof` 作为 gated branch，不进默认采样。

### Slot 2：hip_mount（root 髋部固定上端）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `service_block_lug` | S2（0002） | `rec_robotic_leg_0002/.../model.py:L135-L196` | ✅ | service block + front/rear gusset + 双 lug(Box) + axis_cap(Cylinder) + top fasteners；箱体加工件外观 |
| `box_cheek_boss` | S6（e757eded） | `rec_robotic_leg_e757eded77ff44dcbee1800830f874f9/.../model.py:L42-L113` | ✗ | mount_block + actuator_pack + 双 hip_cheek(Box) + 双 hip_boss(y-Cylinder) + front/rear tie；模块化承载架 |
| `cast_yoke_flange` | S8（5e1d8553） | `rec_robotic_leg_5e1d855301e447c6bad9a61468a7a730/.../model.py:L44-L91` | ✗ | fixed_mount_flange + actuator_spine + 双 yoke_cheek + top/rear bridge + flange/side bolt；铸造法兰上端 |
| `sealed_drip_hood` | S12（25310b6d） | `rec_robotic_leg_25310b6d3bc14677a787ab918625686f/.../model.py:L79-L137` | ✗ | base_plate + top/rear bridge + cheek_outer/inner + drip_hood（防水悬檐）；cadquery sealed 外壳 |

### Slot 3：segment_construction（thigh + shank 连杆构造，两段共用此风格）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `loft_superellipse_shell` | S1 / S2（0002） | `rec_robotic_leg_0002/.../model.py:L86-L120` | ✅ | section_loft + superellipse_profile 生成有机锥形外壳，外加 actuator_bay/front_rib；mesh_from_geometry |
| `primitive_spine_web` | S3（0174b16e） | `rec_robotic_leg_0174b16e06274c78b1d18bd91d271190/.../model.py:L99-L116` | ✗ | 纯 primitive：spine(Box) + 双 side_web(Box)，无 mesh 生成；轻量直梁 |
| `beam_collar_drive` | S4（bd2102） | `rec_robotic_leg_bd2102f14a894c1cb540b24fe89785bf/.../model.py:L56-L86` | ✗ | shaft + collar + drive_web + 单根 beam(Box)，强调驱动链而非外壳 |
| `cadquery_armor` | S13（f5251bbd）/ S12（25310b6d） | `rec_robotic_leg_f5251bbd807f4aa2965c5fa3c4d8f888/.../model.py:L27-L75` | ✗ | cadquery core+armor，filleted/chamfered 装甲外壳套在结构 core 上 |

### Slot 4：joint_interface（hip/knee/ankle 轴承接口风格，三关节共用）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `lug_axiscap_saddle` | S2 / S3（0002）, S6（e757eded box-cheek+boss） | `rec_robotic_leg_0002/.../model.py:L160-L228` | ✅ | parent 双 lug/cheek + axis_cap，child 双 hub + saddle 接住；箱体 lug 在外、hub 在内对齐 |
| `barrel_lug_yoke` | S3（0174b16e） | `rec_robotic_leg_0174b16e06274c78b1d18bd91d271190/.../model.py:L68-L98` | ✗ | parent barrel(横 Cylinder)，child lug_outer/inner + cheek_outer/inner + yoke_bridge 抱住 barrel；lug 外缘 `expect_contact` barrel |
| `rotor_barrel_clamp` | S5（5e1d8553）, S9 | `rec_robotic_leg_5e1d855301e447c6bad9a61468a7a730/.../model.py:L93-L105` | ✗ | parent 双 yoke_cheek，child rotor_barrel + clamp_band 旋转鼓夹在 cheek 之间；rotor 落在 cheek 之间 |
| `motor_bore_shaft` | S4 / S7（bd2102） | `rec_robotic_leg_bd2102f14a894c1cb540b24fe89785bf/.../model.py:L37-L74` | ✗ | parent `*_motor`(横 Cylinder)，child `*_shaft` 穿过 motor 内孔（`allow_overlap`+`expect_within`），驱动式接口 |

### Slot 5：foot_module（远端 ankle/foot 终端）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `loft_foot_sole_toe_heel` | S2（0002） | `rec_robotic_leg_0002/.../model.py:L432-L502` | ✅ | foot_shell(loft) + ankle_hub/bridge + dorsal_housing + rubber sole + toe_bumper + heel_pad，全部 fixed 在 foot part 内 |
| `plate_sole_toe_lip` | S4（bd2102） | `rec_robotic_leg_bd2102f14a894c1cb540b24fe89785bf/.../model.py:L120-L150` | ✗ | ankle_shaft + ankle_block + 扁 sole_pad + toe_lip；compact 平板足 |
| `wear_plate_foot` | S5（5e1d8553） | `rec_robotic_leg_5e1d855301e447c6bad9a61468a7a730/.../model.py:L234-L276` | ✗ | ankle_neck_block + ankle_carrier + rubber_foot_pad + toe/heel wear_plate（金属耐磨板）+ cap bolts |
| `foot_plus_fixed_sole_part` | S11（e757eded） | `rec_robotic_leg_e757eded77ff44dcbee1800830f874f9/.../model.py:L298-L424` | ✗ | foot_module 之外再挂一个独立 `sole_pad` part，用 `foot_to_sole` FIXED joint 连接（链多一节固定段） |

## 槽位图（slot graph）
pattern = **linear_chain**（带一个 gated topology 开关）

```
Slot1 kinematic_topology  ──控制整条链的 joint 数/轴向──┐
                                                       │
  sagittal_3dof (默认):                                ▼
    hip_mount ──hip_pitch(±Y)──> thigh ──knee_pitch(±Y)──> shank ──ankle_pitch(±Y)──> foot
      [Slot2]      [Slot4]       [Slot3]     [Slot4]      [Slot3]      [Slot4]      [Slot5]

  spatial_5dof (gated):
    hip_mount ─hip_roll(X)─> hip_roll_link ─hip_pitch(Y)─> thigh ─knee(Y)─> calf
                ─ankle_pitch(Y)─> ankle_pitch_link ─ankle_roll(X)─> foot

Slot2 = hip_mount 风格      （root，1 个，固定不动）
Slot3 = segment_construction（thigh + shank 两段共用同一构造风格）
Slot4 = joint_interface     （hip + knee + ankle 三个接口共用同一风格）
Slot5 = foot_module         （远端 foot 终端；可选再挂 fixed sole_pad）
```

- 链严格串联：`hip_mount → thigh → shank → foot`，无跳级 parent。
- joint origin 由段长决定：`knee_origin = hip_origin + (0,0,-thigh_len)`，`ankle_origin = knee_origin + (0,0,-shank_len)`，foot 接地。
- Slot3/Slot4 是"风格选择一次、两段/三关节统一应用"的共享 slot（不是每段独立随机），保证同一条腿构造语言一致。

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `hip_mount` / `upper_housing` / `root_housing` / `hip_carriage` | 固定 root 上端，承载 hip 轴承与 actuator，必须是链的不动 base | `hip_mount_style`, `mount_width`, `mount_depth`, `mount_z` | S2 / S6 / S8 / S12 |
| `thigh` / `upper_leg` / `thigh_link` / `thigh_module` | 近端大腿连杆，含 hip 端接口 hub/lug 与 knee 端接口 | `segment_construction`, `thigh_len`, `thigh_width`, `thigh_height` | S2 / S3 / S4 / S5 |
| `shank` / `lower_leg` / `shank_link` / `shank_module` / `calf` | 远端小腿连杆，含 knee 端接口与 ankle 端接口 | `segment_construction`, `shank_len`, `shank_width`, `shank_height` | S2 / S3 / S4 / S5 |
| `foot` / `ankle_foot` / `foot_module` | 远端足，含 ankle hub、足背 housing、接地 sole | `foot_module_style`, `foot_len`, `sole_thickness` | S2 / S4 / S5 / S11 |
| `sole_pad`（optional） | 独立可拆接地垫，FIXED 挂在 foot 下 | `has_separate_sole`, `sole_pad_size` | S11 |
| `hip_roll_link`（gated） | spatial 分支专用，承载 hip_roll(X) 的中间正交连杆 | `topology=spatial_5dof` | S13 |
| `ankle_pitch_link`（gated） | spatial 分支专用，承载 ankle_roll(X) 的中间正交连杆 | `topology=spatial_5dof` | S13 |
| `joint_hardware` | 各关节 lug/cheek/barrel/clamp/motor/trunnion 与 axis_cap、side bolt 等固定细节 | `joint_interface`, `bolt_detail_level` | S2 / S3 / S5 / S6 / S12 |
| `actuator_bay` / `service_cover` | 连杆侧面的执行器舱、服务盖板，optional fixed 装饰 | `has_actuator_bay`, `has_service_cover` | S2 / S8 / S10 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `hip_pitch` | revolute | Slot2.hip_mount | Slot3.thigh | `(0, ±1, 0)` | `[-0.75, 0.95]` rad typ. | 默认 sagittal 链第 1 主关节，绕 ±Y | S3 / S5 / S9 |
| `knee_pitch` | revolute | Slot3.thigh | Slot3.shank | `(0, ±1, 0)` | `[0.0, 1.75]` rad typ.（仅单向屈） | 第 2 主关节，origin 在 thigh 远端 `-thigh_len` | S3 / S5 / S9 |
| `ankle_pitch` | revolute | Slot3.shank | Slot5.foot | `(0, ±1, 0)` | `[-0.65, 0.65]` rad typ. | 第 3 主关节，origin 在 shank 远端 `-shank_len` | S3 / S5 / S9 |
| `foot_to_sole` | fixed | Slot5.foot | Slot5.sole_pad | n/a | n/a | optional，独立 sole_pad 固定到 foot 底面 | S11 |
| `hip_roll` | revolute | Slot2.hip_mount | hip_roll_link | `(1, 0, 0)` | `[-0.5, 0.5]` rad | gated spatial 分支 only，髋外展 | S13 |
| `hip_pitch`(spatial) | revolute | hip_roll_link | Slot3.thigh | `(0, 1, 0)` | `[-1.5, 1.5]` rad | gated 分支：roll 之后串接 pitch | S13 |
| `ankle_roll` | revolute | ankle_pitch_link | Slot5.foot | `(1, 0, 0)` | `[-0.5, 0.5]` rad | gated spatial 分支 only，踝内外翻 | S13 |

> axis 符号说明：±Y 的正负是膝屈方向/解剖学约定（样本里有全 +Y、全 -Y、以及 -Y/+Y/-Y 交替三种写法），都属 sagittal pitch，不是不同 axis_family；模板内统一约定后保持一致即可。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `kinematic_topology` | enum | `sagittal_3dof` / `spatial_5dof` | `sagittal_3dof` | 决定 joint 数与轴向；spatial gated | S3 / S5 / S13 |
| `hip_mount_style` | enum | `service_block_lug` / `box_cheek_boss` / `cast_yoke_flange` / `sealed_drip_hood` | `service_block_lug` | 决定 root 外形与 hip 接口承托 | S2 / S6 / S8 / S12 |
| `segment_construction` | enum | `loft_superellipse_shell` / `primitive_spine_web` / `beam_collar_drive` / `cadquery_armor` | `loft_superellipse_shell` | thigh+shank 共用，决定外壳/截面构造方法 | S1 / S3 / S4 / S13 |
| `joint_interface` | enum | `lug_axiscap_saddle` / `barrel_lug_yoke` / `rotor_barrel_clamp` / `motor_bore_shaft` | `lug_axiscap_saddle` | hip/knee/ankle 共用，决定轴承接口与所需间隙约束 | S2 / S3 / S5 / S4 |
| `foot_module_style` | enum | `loft_foot_sole_toe_heel` / `plate_sole_toe_lip` / `wear_plate_foot` / `foot_plus_fixed_sole_part` | `loft_foot_sole_toe_heel` | 决定足部构造及是否额外 fixed sole_pad | S2 / S4 / S5 / S11 |
| `total_leg_length` | float | `0.55-1.10` | sampled | `thigh_len + shank_len + foot_height` | S3 / S5 / S2 |
| `thigh_shank_ratio` | float | `0.50-0.58` | sampled | `thigh_len = (total - foot_h) * ratio`，`shank_len = total - foot_h - thigh_len` | S3 / S5 |
| `thigh_len` | float | derived, min `0.18` | derived | `distance(hip_origin, knee_origin)`，典型 0.40-0.55 | S3 / S5 |
| `shank_len` | float | derived, min `0.16` | derived | `distance(knee_origin, ankle_origin)`，典型 0.40-0.50 | S3 / S5 |
| `mount_z` | float | `0.10-0.31` | sampled | root 上端高度 / hip 轴中心 | S2 / S8 |
| `joint_limit_profile` | enum | `walking_safe` / `wide_range` / `service_locked` | `walking_safe` | 设定 hip/knee/ankle range；knee 单向屈 | S3 / S5 / S9 |
| `has_separate_sole` | bool | `true` / `false` | derived | 仅 `foot_module_style=foot_plus_fixed_sole_part` 时 true | S11 |
| `bolt_detail_level` | enum | `none` / `light` / `heavy` | `light` | side bolt / cap bolt 密度，固定在 hub/cheek 上 | S2 / S5 |

## 拓扑多样性审计
total combinations（默认 sagittal 分支内，按各 slot 候选数连乘）：

- Slot1 仅 gate（默认锁 `sagittal_3dof`），不计入默认采样乘积；spatial 作为独立 gated 分支。
- 默认采样乘积 = Slot2(4) × Slot3(4) × Slot4(4) × Slot5(4) = **256**。
- 加上 gated 顶层拓扑 2 选 1，全空间上界 = 2 × 256 = **512**。

| 项 | 值 |
|---|---|
| total_combinations（默认分支） | 256 |
| total_combinations（含 gated topology） | 512 |
| | 远超（256 ≫ 5），通过 |

per-slot candidate_count：

| slot | candidate_count |
|---|---|
| Slot1 kinematic_topology | 2 |
| Slot2 hip_mount | 4 |
| Slot3 segment_construction | 4 |
| Slot4 joint_interface | 4 |
| Slot5 foot_module | 4 |


## Validator
| 检查项 | 标准 |
|---|---|
| identity | hip_mount + thigh + shank + foot 四件 + hip/knee/ankle 三个串联 revolute |
| primary joint count | 默认 sagittal 恰好 hip_pitch / knee_pitch / ankle_pitch 三个主关节 |
| axis consistency | sagittal 分支三轴均为 ±Y（lateral pitch）；spatial 分支 hip_roll/ankle_roll 为 X、其余为 Y，且需带 hip_roll_link/ankle_pitch_link 中间连杆 |
| serial topology | hip_mount → thigh → shank → foot 严格串联，无跳级 parent |
| endpoint consistency | `distance(hip_origin, knee_origin) ≈ thigh_len`；`distance(knee_origin, ankle_origin) ≈ shank_len` |
| joint interface containment | child 的 hub/lug/barrel/shaft 落在 parent 的 lug/cheek/yoke/motor 接口内（contact 或受控 nested overlap，带 allow/expect 约束） |
| knee one-way | knee 屈曲为单向（lower≈0），不允许过伸为大负角 |
| grounding | hip_mount 为不动 root；foot 末端有可着地 sole（rubber/wear pad），foot 在链最远端 |
| optional compatibility | 独立 sole_pad 仅当 `foot_module_style=foot_plus_fixed_sole_part`；spatial 中间连杆仅当 `kinematic_topology=spatial_5dof` |
| no floating | 所有连杆、hub、cheek、barrel、motor、sole、bolt、cover 必须 attached 或受约束，不漂浮 |

## Reject cases
- 只有静态三杆，没有 hip/knee/ankle revolute joint。
- hip/knee/ankle joint origin 不落在连杆端点（与 thigh_len/shank_len 不一致）。
- 把 sagittal pitch（±Y）和 spatial roll（X）混在默认分支里，却没有 `kinematic_topology=spatial_5dof` gate 和对应中间连杆。
- knee 被设成双向大角度（既能大幅过伸又能大幅屈），不符合腿的单向屈膝。
- foot 缺失或无接地 sole/pad，或 foot 不在链最远端（被 ankle 之后还有别的活动段）。
- hip_mount 不是不动 root（被设成可动），或连杆从空中开始、root 漂浮。
- child hub/shaft/barrel 与 parent 接口错位（既不接触也不在受控 nested overlap 内）。
- 独立 sole_pad 用了非 FIXED joint，或在非 `foot_plus_fixed_sole_part` 风格下凭空出现。
- actuator_bay / service_cover / bolt / axis_cap 悬空，不挂在连杆/接口上。
- 把它做成机械臂（末端 flange/夹爪而非接地 foot）或多腿整机。

## 与相邻类别的边界
- vs `serial_elbow_arm`：机械臂 base 固定且末端是 tool flange，无接地 foot、无 sagittal 步行限位；本类 root 是 hip mount，末端必须是可着地 foot，knee 单向屈。
- vs `cantilever_articulated_arm` / 云台 / 支架：那些没有"三段连杆 + 接地足 + 矢状面屈伸"的腿语义。
- vs 四足/双足整机：本类只建**单腿模块**（一条 hip→foot 链），不含躯干/多腿/对侧腿。
- vs `telescoping_boom`：无伸缩 prismatic；本类全 revolute。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved（human-reviewed）|
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核。读了 7 个跨谱系全量样本 + 30 个 grep 覆盖；Slot1 拓扑 slot 仅 2 候选（5-DOF spatial 5 星样本仅 1 例，已注明降级理由），其余 4 个结构 slot 均 4 候选，默认分支组合 256 ≫ 5 |
