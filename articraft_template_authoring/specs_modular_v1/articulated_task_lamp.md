# Articulated Task Lamp Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `articulated_task_lamp` |
| template path | `agent/templates/articulated_task_lamp.py` |
| test path | `tests/agent/test_articulated_task_lamp_template.py` |
| stage | `APPROVED` |
| status | `APPROVED` |
| __modular__ | `True` |
| pattern | `linear_chain` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 78 |
| read_count | 78 |
| read_scope | all 5-star samples in this category |
| samples_adopted_as_module_sources | 11 |
| samples_read_but_not_adopted | 67 |
| source_index_policy | only adopted reusable snippets are indexed below |

全量 78 个 5 星样本均已读取 `model.py`、`revision.json`、`record.json` 与 prompt metadata；其中 11 个作为模块采纳源，67 个仅作拓扑族归类与边界证据，不写入来源索引。

### 全量样本清单
| record_id | 拓扑族 | 状态 |
|---|---|---|
| `rec_articulated_task_lamp_0001` | desk_architect_3r | ✅ adopted — Slot A/B/C source |
| `rec_articulated_task_lamp_0002` | desk_architect_3r | read but not adopted — duplicate twin-rail topology |
| `rec_articulated_task_lamp_0007` | wall_mount | read but not adopted — wall-mount family |
| `rec_articulated_task_lamp_0008` | desk_architect_3r | read but not adopted — duplicate desk topology |
| `rec_articulated_task_lamp_0009` | clamp_mount | read but not adopted — clamp-mount family |
| `rec_articulated_task_lamp_0010` | prismatic_gooseneck | read but not adopted — prismatic spine family |
| `rec_articulated_task_lamp_0011` | wall_mount | ✅ adopted — Slot A wall bracket |
| `rec_articulated_task_lamp_0012` | wall_mount | ✅ adopted — Slot B scissor arm |
| `rec_articulated_task_lamp_0a36acca0a084b5fa067884aabf8fcb4` | wall_mount | read but not adopted |
| `rec_articulated_task_lamp_0ea8876741a9438f8b2df4997f7f502d` | ceiling_medical | read but not adopted — ceiling medical family |
| `rec_articulated_task_lamp_15bd124cb9714f1f92e1a3efb785697c` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_165522499c1142948f4038fedbeada87` | wall_mount | ✅ adopted — Slot A wall swing bracket |
| `rec_articulated_task_lamp_1ced2c27ee8f432bae52389fe97aa492` | floor_standing | read but not adopted — floor-standing family |
| `rec_articulated_task_lamp_244bcbee8b0b4d649d50f33f08289b9e` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_26b8afbe241c433fa325fbf23fe8edda` | wall_mount | read but not adopted |
| `rec_articulated_task_lamp_2c59d871ad95406c8d26633340092d37` | magnifier_lamp | read but not adopted — magnifier ring head family |
| `rec_articulated_task_lamp_2c74aed683954497833472dce42ed3b8` | high_dof_arm | read but not adopted — 6R counterbalance outlier |
| `rec_articulated_task_lamp_3078b945e60c47be998a445dd4a12b3e` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_30ca40f786d04dd4a371cdc628f08877` | desk_architect_3r | read but not adopted |
| `rec_articulated_task_lamp_30edba7af97b448c9bd3c35f505aacd7` | ceiling_medical | read but not adopted |
| `rec_articulated_task_lamp_3d271de8f1554baf9627ec79fa530412` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_3f2808ab47f14c6fa1d52fdad9685c83` | prismatic_gooseneck | ✅ adopted — Slot B telescoping stages (gated branch evidence) |
| `rec_articulated_task_lamp_3f9a2e86d3a54517bb08371e9a859fa8` | floor_standing | read but not adopted |
| `rec_articulated_task_lamp_40a6b812a19a487e857babea0348cfe7` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_4224e4fd1125405e8d7d07f7bb27a9e2` | prismatic_gooseneck | read but not adopted |
| `rec_articulated_task_lamp_428f952641214ade91c520e3fc83a9b5` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_42ef6ec3e5b34bda8f834ac25c34dfd6` | wall_mount | read but not adopted — multi-arm tree outlier |
| `rec_articulated_task_lamp_471fd346de6d4db19cfe409765c12902` | wall_mount | ✅ adopted — Slot B spring-balanced arm |
| `rec_articulated_task_lamp_533231cc3b204edf9f901e5f4e6fbc0a` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_54062170900c4a5abf3397d97a1baf3d` | wall_mount | read but not adopted |
| `rec_articulated_task_lamp_64f98407b3a145eba7cb8d04cc6b5c3b` | desk_architect_3r | read but not adopted |
| `rec_articulated_task_lamp_65621ad867e644a282a5b5a13697c4bd` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_670a2a3b4c2a4bb793c39db1be180271` | clamp_mount | ✅ adopted — Slot A C-clamp + boom |
| `rec_articulated_task_lamp_681a2fa021bf400b87fdcbe2394ec79d` | floor_standing | read but not adopted |
| `rec_articulated_task_lamp_6965d989f1d94637a333e90911d17085` | wall_mount | read but not adopted |
| `rec_articulated_task_lamp_6bf6f6cd53254d98b2f5dae048a7f762` | two_link_lamp | read but not adopted — 2R banker/piano family |
| `rec_articulated_task_lamp_6c01aa125cd94f2c96df9b40203481d5` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_6dacbcddf32b48299f148171c603c1e9` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_6e57f7ca48f94eb6b7eab7837960f129` | floor_standing | read but not adopted |
| `rec_articulated_task_lamp_7438b7845cdf4c3fa5c1f7138edd595c` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_7f8067caf9ee4daa9e5577f4265ccfa8` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_7fa39103797943efa136e77928178391` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_855f4ebd01b74b2a9b84e03da7991596` | desk_architect_3r | read but not adopted |
| `rec_articulated_task_lamp_881f7667505547d1a5b4beb68756f84b` | two_link_lamp | ✅ adopted — Slot B/C single-arm banker dome |
| `rec_articulated_task_lamp_882af0f035b148fd9e7a6bf55d5fe5a2` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_8ab1126883304ed48ca94d1f5f1fd194` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_9200ab1a6b0e4686869aa67bc8ca0b29` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_928efb007101437d8a379e46f85eac60` | wall_mount | read but not adopted |
| `rec_articulated_task_lamp_960a3f5d314347e4a138406845c8004b` | wall_mount | read but not adopted |
| `rec_articulated_task_lamp_9b48b4a0694e48ee98188cf4f074ab02` | floor_standing | read but not adopted |
| `rec_articulated_task_lamp_9c3237b98579495abab4e932a79818ff` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_9c49ebf95fbb477088ecaf8f319f1011` | two_link_lamp | read but not adopted |
| `rec_articulated_task_lamp_a3585ee937bc4ba8990c6aec052366e3` | magnifier_lamp | read but not adopted |
| `rec_articulated_task_lamp_a7fb8de10c874f1bb217b293d86eeac6` | wall_mount | read but not adopted |
| `rec_articulated_task_lamp_ab1182e4835d49a68785a4ebb2f41bd9` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_ab1296dbfee94e06875d5accfabd25b7` | wall_mount | read but not adopted |
| `rec_articulated_task_lamp_ae09411ed1834f5c80a2b1b6b9a66a36` | desk_architect_3r | ✅ adopted — Slot A post+swivel, Slot B rail fork arm |
| `rec_articulated_task_lamp_ae5cfd5956bb4b84a82edecbe031e16a` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_b34c0dca722346b2acaa5b6adbbd9f32` | wall_mount | read but not adopted |
| `rec_articulated_task_lamp_c34b2afba0814d15a225b93e3d1d4775` | floor_standing | read but not adopted |
| `rec_articulated_task_lamp_c5d513f31f80480d878489269d948987` | wall_mount | ✅ adopted — Slot A rectangular weighted base |
| `rec_articulated_task_lamp_cb106700d7204856b75ac6c9b9a03855` | two_link_lamp | read but not adopted |
| `rec_articulated_task_lamp_cee3c5ec5bc04c0f84a64376bf5d817a` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_d10a06366931437ca72efd5753970a07` | ceiling_medical | read but not adopted |
| `rec_articulated_task_lamp_d197e448810041a0a4d8be80da3e0478` | wall_mount | read but not adopted |
| `rec_articulated_task_lamp_d979b0bea4d5494b8922395f176b14a3` | desk_architect_3r | read but not adopted |
| `rec_articulated_task_lamp_de95775712a145348a3cce334bd95be9` | wall_mount | read but not adopted |
| `rec_articulated_task_lamp_e179909383b54540899b4483f6b8c8a8` | prismatic_gooseneck | read but not adopted |
| `rec_articulated_task_lamp_e3b37e132fda4a8b848be4c5ba370d7e` | floor_standing | read but not adopted |
| `rec_articulated_task_lamp_efb71056299f446f9b9abc277720f89d` | clamp_mount | read but not adopted |
| `rec_articulated_task_lamp_f25cf0f6b3b0431fa0df88c604812360` | magnifier_lamp | read but not adopted |
| `rec_articulated_task_lamp_fcc4f8c9b66747e798e0208412c61c27` | ceiling_medical | read but not adopted |
| `rec_create-a-black-adjustable-desk-lamp_20260423_092936_989069_06f1bc16` | desk_architect_3r | read but not adopted |
| `rec_create-a-realistic-articulated-desk-lamp-with-a-_20260514_221150_836652_f0074cc6` | desk_architect_3r | read but not adopted |
| `rec_create-a-simple-office-desk-lamp-with-a-weighted_20260426_043510_578326_bec61660` | desk_architect_3r | ✅ adopted — minimal CadQuery skeleton |
| `rec_create-a-simple-office-desk-lamp-with-a-weighted_20260426_043517_753346_bec61660` | desk_architect_3r | read but not adopted |
| `rec_create-a-simple-office-desk-lamp-with-a-weighted_20260426_224635_740536_bec61660` | desk_architect_3r | read but not adopted |
| `rec_make-a-lamp_20260410_102000_880409_7c3a1815` | desk_architect_3r | read but not adopted |

## 核心身份

Articulated task lamp 是带可动臂与可定向灯头的局部照明器具：必须有 grounded mount（配重底座、墙板或夹具之一）、至少一段可摆动的 arm/boom 链，以及 lamp shade/head 相对臂末端的 tilt/pan 关节。类别身份来自「照明 + 串联关节臂 + 灯头」，不是 generic floor lamp（无臂仅柱+顶罩）、不是 ceiling fan、不是 monitor mount。

5 星样本横跨 desk architect lamp、wall swing lamp、C-clamp boom、gooseneck prismatic、medical ceiling arm、multi-arm tree lamp 等互斥拓扑。**默认成熟 seed domain** 收窄为 **weighted desk base + 2-link twin-rail arm + 3 revolute pitch joints（shoulder / elbow / shade tilt）**。wall / clamp / prismatic gooseneck / ceiling medical / multi-arm tree 保留为 evidence 与 future split source；除非 reviewer 明确批准，否则不进入默认 seed。

边界：
- 不包括无 arm 的 torchiere / arc floor post（仅柱+顶罩，无 elbow chain）。
- 不混入 `floor_lamp`（独立类别）、`studio_spotlight_on_yoke`（舞台灯 yoke 语义不同）、`monitor_mount`（无 lamp head）。
- 不把 medical dual-arm ceiling lamp 硬塞进默认 desk slug；应拆为 `articulated_task_lamp_ceiling_medical` 或 gated 分支。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_articulated_task_lamp_0001` | `data/records/rec_articulated_task_lamp_0001/revisions/rev_000001/model.py:L49-L163` | `_add_twin_arm_segment` helper、双轨臂段 mesh |
| S2 | `rec_articulated_task_lamp_0001` | `data/records/rec_articulated_task_lamp_0001/revisions/rev_000001/model.py:L179-L390` | 圆盘配重 base、lower/upper arm、rectangular head shell |
| S3 | `rec_articulated_task_lamp_0001` | `data/records/rec_articulated_task_lamp_0001/revisions/rev_000001/model.py:L392-L433` | shoulder/elbow/head_tilt 三 REVOLUTE -Y pitch 链与 range |
| S4 | `rec_articulated_task_lamp_c5d513f31f80480d878489269d948987` | `data/records/rec_articulated_task_lamp_c5d513f31f80480d878489269d948987/revisions/rev_000001/model.py:L38-L84` | `_rounded_base_mesh`、`_shade_shell_mesh` helpers |
| S5 | `rec_articulated_task_lamp_c5d513f31f80480d878489269d948987` | `data/records/rec_articulated_task_lamp_c5d513f31f80480d878489269d948987/revisions/rev_000001/model.py:L97-L251` | 矩形配重 base + 双平行杆臂 + Lathe shade |
| S6 | `rec_articulated_task_lamp_c5d513f31f80480d878489269d948987` | `data/records/rec_articulated_task_lamp_c5d513f31f80480d878489269d948987/revisions/rev_000001/model.py:L253-L288` | rest-pose rpy 补偿的三段 pitch joint |
| S7 | `rec_articulated_task_lamp_ae09411ed1834f5c80a2b1b6b9a66a36` | `data/records/rec_articulated_task_lamp_ae09411ed1834f5c80a2b1b6b9a66a36/revisions/rev_000001/model.py:L65-L125` | 配重盘 + 立柱 + swivel_head 转台 |
| S8 | `rec_articulated_task_lamp_ae09411ed1834f5c80a2b1b6b9a66a36` | `data/records/rec_articulated_task_lamp_ae09411ed1834f5c80a2b1b6b9a66a36/revisions/rev_000001/model.py:L127-L359` | rail fork 双轨臂 + 4DOF（Z swivel + 3×-Y pitch） |
| S9 | `rec_articulated_task_lamp_471fd346de6d4db19cfe409765c12902` | `data/records/rec_articulated_task_lamp_471fd346de6d4db19cfe409765c12902/revisions/rev_000001/model.py:L28-L170` | `_conical_shade_shell`、`_coil_spring`、`_add_arm_segment` 弹簧平衡臂 |
| S10 | `rec_articulated_task_lamp_471fd346de6d4db19cfe409765c12902` | `data/records/rec_articulated_task_lamp_471fd346de6d4db19cfe409765c12902/revisions/rev_000001/model.py:L183-L355` | Lathe 配重 base + 弹簧臂 + 锥形 shade + 3R joints |
| S11 | `rec_articulated_task_lamp_670a2a3b4c2a4bb793c39db1be180271` | `data/records/rec_articulated_task_lamp_670a2a3b4c2a4bb793c39db1be180271/revisions/rev_000001/model.py:L57-L183` | C-clamp base + horizontal boom + conical shade（clamp 族 evidence） |
| S12 | `rec_articulated_task_lamp_670a2a3b4c2a4bb793c39db1be180271` | `data/records/rec_articulated_task_lamp_670a2a3b4c2a4bb793c39db1be180271/revisions/rev_000001/model.py:L185-L221` | clamp screw PRISMATIC + Z swivel + Y shade tilt |
| S13 | `rec_articulated_task_lamp_0011` | `data/records/rec_articulated_task_lamp_0011/revisions/rev_000001/model.py:L78-L224` | wall_mount 背板 + 两段圆柱臂 + Lathe shade（wall 族 evidence） |
| S14 | `rec_articulated_task_lamp_0011` | `data/records/rec_articulated_task_lamp_0011/revisions/rev_000001/model.py:L226-L267` | 全 +Y 轴 wall arm 三 REVOLUTE |
| S15 | `rec_articulated_task_lamp_165522499c1142948f4038fedbeada87` | `data/records/rec_articulated_task_lamp_165522499c1142948f4038fedbeada87/revisions/rev_000001/model.py:L42-L204` | wall_bracket + 双平行 bar link + shade |
| S16 | `rec_articulated_task_lamp_165522499c1142948f4038fedbeada87` | `data/records/rec_articulated_task_lamp_165522499c1142948f4038fedbeada87/revisions/rev_000001/model.py:L206-L247` | Z 平面 swing + -Y shade tilt |
| S17 | `rec_articulated_task_lamp_881f7667505547d1a5b4beb68756f84b` | `data/records/rec_articulated_task_lamp_881f7667505547d1a5b4beb68756f84b/revisions/rev_000001/model.py:L35-L218` | banker 单臂 + green glass dome shade（2R 低 DOF 变体） |
| S18 | `rec_articulated_task_lamp_881f7667505547d1a5b4beb68756f84b` | `data/records/rec_articulated_task_lamp_881f7667505547d1a5b4beb68756f84b/revisions/rev_000001/model.py:L220-L247` | post_to_arm -Y + arm_to_shade +Y 双轴 |
| S19 | `rec_articulated_task_lamp_0012` | `data/records/rec_articulated_task_lamp_0012/revisions/rev_000001/model.py:L61-L156` | scissor 平行四边形臂 + shade_yoke/head 双 part（scissor 族 evidence） |
| S20 | `rec_articulated_task_lamp_0012` | `data/records/rec_articulated_task_lamp_0012/revisions/rev_000001/model.py:L158-L193` | 4R scissor + Z shade swivel |
| S21 | `rec_articulated_task_lamp_3f2808ab47f14c6fa1d52fdad9685c83` | `data/records/rec_articulated_task_lamp_3f2808ab47f14c6fa1d52fdad9685c83/revisions/rev_000001/model.py:L57-L242` | 三节 PRISMATIC gooseneck stages（gooseneck 族 evidence） |
| S22 | `rec_articulated_task_lamp_3f2808ab47f14c6fa1d52fdad9685c83` | `data/records/rec_articulated_task_lamp_3f2808ab47f14c6fa1d52fdad9685c83/revisions/rev_000001/model.py:L244-L441` | 伸缩段后接 2-link revolute arm + shade |
| S23 | `rec_create-a-simple-office-desk-lamp-with-a-weighted_20260426_043510_578326_bec61660` | `data/records/rec_create-a-simple-office-desk-lamp-with-a-weighted_20260426_043510_578326_bec61660/revisions/rev_000001/model.py:L16-L79` | 最小 CadQuery loft shade + 3R +Y 骨架 |

## 槽位 + 候选模块表

### Slot A：base_mount（接地安装件）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `weighted_round_disk` | S2 (0001) | `L179-L264` | eligible if compatible | Lathe/Extrude 圆盘配重 + 肩轴 yoke + 橡胶脚垫 |
| `weighted_rect_plate` | S5 (c5d513) | `L97-L145` | eligible if compatible | 圆角矩形配重板 + hinge pin + yoke |
| `post_with_swivel` | S7 (ae0941) | `L65-L125` | eligible if compatible | 配重盘 + 立柱 post + 顶部 swivel_head 转台 |
| `c_clamp_jaw` | S11 (670a2a) | `L57-L119` | eligible if compatible | C 型夹背板 + 上下颚 + 夹紧螺杆（PRISMATIC 子件） |
| `wall_backplate` | S13 (0011) | `L78-L113` | eligible if compatible | 壁装背板 + shoulder fork |
| `wall_swing_bracket` | S15 (165522) | `L42-L72` | eligible if compatible | 薄 wall bracket + brass pivot ears |

> Procedural sampler 可先在兼容矩阵中偏向 `weighted_round_disk` 与 `weighted_rect_plate`；其余为 gated `mount_style` 分支 evidence，模板阶段需 gate 干净或拆 slug。

### Slot B：arm_chain（臂链 / boom）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `twin_rail_two_link` | S1/S2 (0001) | `L49-L163,L266-L322` | eligible if compatible | 双平行 rail + hub barrel 的两段 architect arm |
| `parallel_bar_two_link` | S5 (c5d513) | `L147-L215` | eligible if compatible | 双平行圆柱/方杆 + barrel hinge 两段臂 |
| `rail_fork_two_link` | S8 (ae0941) | `L127-L271` | eligible if compatible | Box rail + cheek fork 双轨臂，可接 post swivel |
| `spring_balanced_two_link` | S10 (471fd3) | `L98-L170,L242-L272` | eligible if compatible | 双杆臂 + 可见 coil spring 平衡件 |
| `single_boom` | S11 (670a2a) | `L121-L151` | eligible if compatible | 单水平 boom 管 + 端 yoke（clamp 族） |
| `single_post_arm` | S17 (881f76) | `L93-L147` | eligible if compatible | 单段 spline tube arm + shade fork（2R 低 DOF） |
| `wall_cylinder_two_link` | S13 (0011) | `L115-L187` | eligible if compatible | 两段圆柱 beam + cheek（+Y 轴系） |
| `wall_bar_two_link` | S15 (165522) | `L74-L165` | eligible if compatible | 双平行 bar 连杆（Z 平面 swing） |
| `scissor_parallelogram` | S19 (0012) | `L86-L120` | eligible if compatible | 平行四边形剪刀臂 + brace |
| `telescoping_gooseneck_stages` | S21 (3f2808) | `L130-L242` | eligible if compatible | 三节 +Z PRISMATIC 伸缩 gooseneck（与 revolute 臂互斥） |
| `minimal_box_two_link` | S23 (create…) | `L32-L53` | eligible if compatible | CadQuery Box 臂 + fork 最小骨架 |

### Slot C：shade_head（灯罩 / 灯头）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `rectangular_architect_head` | S2 (0001) | `L324-L390` | eligible if compatible | Extrude 矩形 reflector head + visor |
| `lathe_conical_shade` | S5 (c5d513) | `L217-L251` | eligible if compatible | Lathe 旋转反射罩 + bulb |
| `lathe_small_shade` | S8 (ae0941) | `L273-L302` | eligible if compatible | 较小 Lathe shade，接 rail arm |
| `conical_clamp_shade` | S11 (670a2a) | `L153-L183` | eligible if compatible | 锥形 reflector + bulb（clamp boom） |
| `banker_glass_dome` | S17 (881f76) | `L149-L218` | eligible if compatible | 绿色玻璃 Lathe dome + neck tube |
| `scissor_box_reflector` | S19 (0012) | `L122-L156` | eligible if compatible | shade_yoke + box reflector head 双 part |
| `cadquery_loft_shade` | S23 (create…) | `L16-L19,L66-L69` | eligible if compatible | CadQuery loft 极简 shade |

### Slot D：base_swivel（可选底座水平转台，gated）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `none_fixed_base` | S2 (0001) | `L392-L405` | eligible if compatible | 默认：base 固定，无水平转台 |
| `z_axis_swivel_head` | S8 (ae0941) | `L96-L125,L304-L318` | eligible if compatible | post 顶部 Z 轴 REVOLUTE swivel → lower_arm |

## 槽位图（slot graph）

```
pattern: linear_chain (+ optional gated base swivel)

[Slot A base_mount] --(optional Slot D base_swivel)--> [Slot B arm_chain link_1]
      --REVOLUTE shoulder--> [link_2] --REVOLUTE elbow--> [link_n / boom end]
      --REVOLUTE shade_tilt--> [Slot C shade_head]

gated branches (mutually exclusive with default desk seed):
  mount_style=clamp  → A=c_clamp, B=single_boom, C=conical_shade, joints include PRISMATIC screw
  mount_style=wall   → A=wall_backplate, B=wall_cylinder/bar, axis family flips to +Y or Z
  arm_style=gooseneck → B=telescoping_prismatic_stages (+ optional revolute tail), not twin_rail
```

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `base` / `weighted_base` | 配重圆盘或矩形板，落地承载 | `base_style`, `base_radius`, `base_height`, `base_mass_visual` | S2 / S5 |
| `shoulder_yoke` / `hinge_boss` | 底座顶部肩轴轭架、pin、cheek | `shoulder_height`, `yoke_gap` | S2 / S5 / S10 |
| `swivel_head` | optional；立柱顶水平转台 | `swivel_enabled`, `swivel_radius` | S7 / S8 |
| `lower_arm` / `first_link` | 第一段臂：twin rail / parallel bar / cylinder beam | `lower_arm_length`, `arm_profile`, `rail_spacing` | S1 / S5 / S8 / S13 |
| `upper_arm` / `second_link` / `boom` | 第二段臂或单 boom | `upper_arm_length`, `boom_style` | S1 / S5 / S11 |
| `shade` / `head` / `reflector` | 灯罩：rectangular / Lathe / dome / box | `shade_style`, `shade_width`, `shade_depth`, `shade_tilt_limit` | S2 / S5 / S17 |
| `bulb` / `socket` | optional visual；灯泡或 LED 点光源 | `bulb_style`, `bulb_size` | S5 / S11 |
| `clamp_jaw` / `clamp_screw` | gated；C 夹上下颚与螺杆 | `clamp_opening`, `screw_travel` | S11 / S12 |
| `wall_plate` | gated；壁装背板 | `plate_width`, `plate_thickness` | S13 / S15 |
| `spring_coil` | optional visual；平衡弹簧 | `spring_enabled`, `spring_turns` | S9 / S10 |

## 关节（Joints）
| 关节 | 类型 | parent | child | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `base_swivel` | revolute | A.base | D.swivel_head | `(0,0,1)` | `[-2.7, 2.7]` | optional gated；底座水平转台 | S8 |
| `shoulder_pitch` | revolute | A.base / D.swivel | B.lower_arm | `(0,-1,0)` 默认 desk | `[-0.55, 0.70]` | 第一段臂俯仰 | S3 / S6 |
| `elbow_pitch` | revolute | B.lower_arm | B.upper_arm | `(0,-1,0)` 与 shoulder 平行 | `[-0.30, 0.95]` | 第二段臂折叠 | S3 / S6 |
| `shade_tilt` | revolute | B.upper_arm / boom | C.shade | `(0,-1,0)` 或 `(0,1,0)` | `[-1.05, 0.55]` | 灯头相对臂末端 tilt | S3 / S6 / S18 |
| `clamp_screw` | prismatic | A.clamp | A.clamp_screw | `(0,0,1)` | `[0, 0.055]` | gated clamp 族 | S12 |
| `boom_swivel` | revolute | A.clamp | B.boom | `(0,0,1)` | `[-2.36, 2.36]` | gated clamp 水平摆臂 | S12 |
| `wall_shoulder` | revolute | A.wall_plate | B.first_link | `(0,1,0)` | `[0, 1.15]` | gated wall 族 | S14 |
| `gooseneck_stage_i` | prismatic | stage_{i-1} | stage_i | `(0,0,1)` | `[0, stroke_i]` | gated gooseneck 伸缩 | S21 |

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
| `mount_style` | enum | `weighted_desk` / `weighted_rect` / `c_clamp` / `wall_plate` / `wall_swing` | `weighted_desk` | 决定 Slot A；默认 seed 仅 desk 两型 | S2 / S5 / S11 / S13 |
| `arm_style` | enum | `twin_rail_two_link` / `parallel_bar_two_link` / `rail_fork_two_link` / `spring_balanced` / `single_boom` / `single_post` / `wall_cylinder` / `wall_bar` / `scissor` / `gooseneck_telescoping` | `twin_rail_two_link` | 决定 Slot B 拓扑 | S1 / S5 / S8 / S10 / S11 / S13 / S19 / S21 |
| `shade_style` | enum | `rect_architect` / `lathe_conical` / `banker_dome` / `box_reflector` / `cadquery_loft` | `rect_architect` | 决定 Slot C | S2 / S5 / S17 / S19 / S23 |
| `swivel_enabled` | bool | `true` / `false` | `false` | true 时插入 Slot D | S8 |
| `pitch_axis_family` | enum | `neg_y_desk` / `pos_y_wall` / `z_swing_wall` | `neg_y_desk` | 与 mount_style 联动 | S3 / S14 / S16 |
| `lower_arm_length` | float | `0.18-0.38` | sampled | elbow origin = lower_arm_length along arm axis | S3 / S6 |
| `upper_arm_length` | float | `0.16-0.32` | sampled | shade origin = upper_arm_length | S3 / S6 |
| `base_radius` | float | `0.08-0.14` | sampled | 圆盘配重半径 | S2 |
| `base_height` | float | `0.02-0.05` | sampled | 配重盘厚度 | S2 / S5 |
| `shade_width` | float | `0.12-0.22` | sampled | head 开口宽度 | S2 |
| `shade_depth` | float | `0.10-0.18` | sampled | head 深度 | S2 |
| `spring_enabled` | bool | `true` / `false` | `false` | 仅 `arm_style=spring_balanced` | S10 |
| `material_style` | enum | `brushed_aluminum` / `matte_black` / `industrial_green` / `warm_brass` | `matte_black` | palette only | S2 / S17 |

## Multiplicity / Copy Logic

- 无复制数量逻辑：本类别核心可动件是固定 named slots（一个 base、一段 2-link arm chain、一个 shade），不随机采样 `*_count`。
- 固定单件不要写成 `arm_count=fixed 1`；lower_arm / upper_arm / shade 都是 named slots。
- gooseneck 的三节 prismatic stage 是 gated `arm_style=gooseneck_telescoping` 下的固定三节串联，不是模板级 `stage_count` 随机采样；若未来扩展可变节数需 reviewer 批准。
- multi-arm tree lamp（如 5 臂 tree floor lamp）不在本 slug；应拆独立 slug。

## 部件多样性审计（Part Diversity Audit）
| 部件类型 | observed_variation | 连续参数是否足够 | 是否需要离散参数 | 推荐参数 | 说明 |
|---|---|---|---|---|---|
| base_mount | weighted disk / rect plate / C-clamp / wall plate | no | yes | `mount_style` | 安装拓扑互斥 |
| arm_chain | twin rail / parallel bar / single boom / scissor / gooseneck prismatic | no | yes | `arm_style` | 关节图与轴系不同 |
| shade_head | rect / Lathe conical / glass dome / box reflector | no | yes | `shade_style` | 灯头识别外形不同 |
| base_swivel | fixed / Z swivel post | no | yes | `swivel_enabled` | 是否多一个 DOF |
| arm_lengths | scale variation within family | yes | no | `lower_arm_length`, `upper_arm_length` | 同族内尺寸连续 |
| spring_visual | present / absent | no | yes | `spring_enabled` | 仅 spring_balanced 族 |
| bulb_detail | bulb / LED puck / none | partly | yes | `bulb_style` | 次要 visual |

## 拓扑多样性审计
| slot | candidate_count | ≥3 | 备注 |
|---|---|---|---|
| A base_mount | 6 | yes | clamp/wall 为 gated |
| B arm_chain | 11 | yes | gooseneck 与 twin_rail 互斥 |
| C shade_head | 7 | yes | |
| D base_swivel | 2 | **no** | 仅 fixed vs swivel；2 候选 fallback，需 reviewer 确认 |

参考 procedural 组合示例：`weighted_desk` × `twin_rail_two_link` × `rect_architect` × `swivel=false` → 1 个稳定 reference example。

## 与相邻类别的边界
- 不该混入：`floor_lamp`（无 articulated arm chain，独立 slug）。
- 不该混入：`studio_spotlight_on_yoke`（舞台灯 yoke + barn door 语义）。
- 不该混入：`monitor_mount`（显示器支架，无 lamp shade）。
- 不该混入：`ceiling_fan` / `ceiling_light_fixture`（天花板安装语义不同）。
- 不该混入：`cantilever_articulated_arm`（工业悬臂，无端部 lamp shade 语义）。

### Procedural Sampling / Sweep Plan

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊，不作为 anchor 或 reference seed。Sampling 先选择上游结构槽，再从 compatible 下游 candidate 集合中选择 module / multiplicity / module-local variant。

Compatibility matrix / gating：以「槽位图」「每槽位 Module Emits / Interfaces」「Validator」中定义的接口、joint 轴、支撑面、range 和互斥关系为准；不兼容组合必须在 sampler 或 `resolve_config` 中降级、重采样或拒绝，不能让 builder 后期失败。

Regression overrides：默认无。若未来 sweep 发现稳定失败组合，或 reviewer 指定固定回归样本，可以添加少量显式 regression seed，但必须写明 seed、组合和原因；不得用小型 curated / modulo 表作为主 seed domain。

Random sweep / viewer plan：首次模板验收跑 `uv run articraft template sweep-pipeline <slug>`，依赖 0、0-4、0-19、0-49 的 cumulative random seeds 检查 build、MatingContract、joint origin / axis / range、support、collision 和 。机械通过后 viewer 目检一小批随机 seed，重点看类别身份、比例、closed pose、bulky module、optional moving child、max multiplicity、captured-pin / bearing / hinge / rail 接口。


## Validator
| 检查项 | 标准 |
|---|---|
| identity | base + arm chain + shade/head 均存在 |
| joint count | 默认 desk seed 至少 3 个 REVOLUTE（shoulder/elbow/shade） |
| chain connectivity | base → lower_arm → upper_arm → shade 串联，无跳接 |
| axis consistency | `pitch_axis_family` 与 `mount_style` 一致 |
| origin placement | elbow origin 在 lower_arm 末端，shade origin 在 upper_arm 末端 |
| shade aim | shade 开口朝外，tilt 后不与 arm 穿模 |
| mount grounding | weighted base 底部接触 z=0；wall plate 法向贴墙 |
| gated branches | clamp/wall/gooseneck 启用时 joint 图与默认 desk 不混用 |
| part diversity | mount_style / arm_style / shade_style 参数存在 |

## Reject cases
- 无 arm chain，仅 static post + top shade（torchiere）。
- 无 shade/head，只有 bare LED bar。
- elbow 或 shade joint 缺失，灯头不可定向。
- joint origin 不在 link 连接端，臂段漂浮。
- desk pitch 轴与 wall +Y 轴在同一 seed 未 gate 混用。
- 把 medical dual-arm ceiling lamp 硬塞进默认 desk slug。
- multi-arm tree（5 个独立 shade arm）未拆 slug。
- 仅用颜色变化表达样本多样性。

## 已有模板写法参考
- gold-standard：`serial_elbow_arm`（revolute 链 + resolve_config）、`cantilever_articulated_arm`（多 link 臂）
- 二级参考：`monitor_mount`（clamp base）、`ceiling_fan`（shade-like head + tilt）

## 模板实现备注（可选）
- 默认实现仅覆盖 `mount_style=weighted_desk|weighted_rect` + `arm_style=twin_rail_two_link|parallel_bar_two_link` + `shade_style=rect_architect|lathe_conical`。
- `S1._add_twin_arm_segment` 是最优先改编 helper；spring coil、scissor、gooseneck 作为 gated module 后续增量。
- rest-pose joint `rpy` 补偿参考 S6；viewer regression reference 可来自 0001 或 c5d513 之一作为 fingerprint reference。
- 建议拆分 future slugs：`articulated_task_lamp_wall_mount`、`articulated_task_lamp_clamp_mount`、`articulated_task_lamp_gooseneck`。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved（human-reviewed） |
| reviewer notes | 模板已实现：`agent/templates/articulated_task_lamp.py`（1863 行），测试 13/13 通过，CLI 已注册。 |
