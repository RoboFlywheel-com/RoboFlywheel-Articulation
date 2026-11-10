# Wheelbarrow Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `wheelbarrow` |
| template path | `agent/templates/wheelbarrow.py` |
| test path | `tests/agent/test_wheelbarrow_template.py` |
| stage | `APPROVED` |
| status | `APPROVED` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 33 |
| read_count | 14 |
| read_scope | 全量 grep 了 33 个 5 星样本的 part 树/articulation 类型/axis/parent-child/prompt；逐行精读 14 个覆盖全部拓扑族（单体 / frame+tray / 多模块串链 / 翻斗 / 折叠脚架 / fold-flat / 调平脚），其余按 part+joint 指纹归类 |
| source_index_policy | 仅索引被采纳的可复用片段；单 DOF（仅 wheel CONTINUOUS）是默认成熟域；翻斗 / 脚架 / fold-flat / 调平脚等第二自由度按 `aux_articulation` gated branch 处理，不强行混进同一默认配置 |

## 核心身份
单轮独轮车（wheelbarrow）：必须有一个落地的刚性 chassis/frame（承载 tray、两根 tubular handle、后部 rear legs/feet），一个前置 single front wheel 落在 fork 内，且 wheel 通过唯一的 CONTINUOUS 轴关节绕侧向轴自旋。区别于手推车/cart（多轮、wheel 在底部四角）和 hand truck/sack barrow（直立背板、两轮在底、靠倾斜搬运）。独轮车的判定锚点是"单前轮 + 两手柄 + 后支腿 + 前轮自旋"，重心靠人抬起后支腿来平衡。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_wheelbarrow_9de7eb8bec2c4c5fb4f3d767b5230123` | `data/records/rec_wheelbarrow_9de7eb8bec2c4c5fb4f3d767b5230123/revisions/rev_000001/model.py:L39-L115` | `_origin_between`/`_tube` 斜管 helper、tapered tray 壳 mesh（rounded_rect loft）helper |
| S2 | `rec_wheelbarrow_9de7eb8bec2c4c5fb4f3d767b5230123` | `data/records/rec_wheelbarrow_9de7eb8bec2c4c5fb4f3d767b5230123/revisions/rev_000001/model.py:L121-L200` | 单体 frame（tray+rim+handle+brace+leg+foot+fork+axle_boss 全部融合）与 SDK WheelGeometry/TireGeometry 轮 + 单 CONTINUOUS axle |
| S2b | `rec_wheelbarrow_91c0b1eb3bf34d4194cce3b0e236fc4a` | `data/records/rec_wheelbarrow_91c0b1eb3bf34d4194cce3b0e236fc4a/revisions/rev_000001/model.py:L221-L282` | LatheGeometry tire profile + 堆叠 Cylinder rim/hub 轮构造，frame→wheel CONTINUOUS（axis 1,0,0，长度沿 Y） |
| S3 | `rec_wheelbarrow_0002` | `data/records/rec_wheelbarrow_0002/revisions/rev_000001/model.py:L89-L139` | 堆叠 Cylinder 轮 helper（tire/sidewall/rim_band/hub/axle_sleeve/spoke_bar） |
| S4 | `rec_wheelbarrow_0002` | `data/records/rec_wheelbarrow_0002/revisions/rev_000001/model.py:L160-L296` | frame 集成 fork crown/arm/dropout + 后腿 skid + 铰链板 + axle washer 细节（翻斗族的固定底架） |
| S5 | `rec_wheelbarrow_0002` | `data/records/rec_wheelbarrow_0002/revisions/rev_000001/model.py:L298-L430` | LoftGeometry 深盘 tray + pivot boss/plate，frame→tray REVOLUTE 翻斗（axis 0,-1,0，lower 0 upper 0.5）+ wheel CONTINUOUS |
| S6 | `rec_wheelbarrow_cb2aea3557674fc18b7dae06b353e9c4` | `data/records/rec_wheelbarrow_cb2aea3557674fc18b7dae06b353e9c4/revisions/rev_000001/model.py:L310-L326` | 三段式 frame + FIXED tray_mount + wheel CONTINUOUS（tray 作为独立螺接件） |
| S7 | `rec_wheelbarrow_1c02a48e9be342039d546a6471a16d16` | `data/records/rec_wheelbarrow_1c02a48e9be342039d546a6471a16d16/revisions/rev_000001/model.py:L268-L402` | 独立 axle_module（shaft+spacer+nut）+ LatheGeometry shell 轮，upper_body→fork FIXED→axle FIXED→wheel CONTINUOUS 四件串链 |
| S8 | `rec_wheelbarrow_194a0df04e7a407fbd3d9c1e77a69ae6` | `data/records/rec_wheelbarrow_194a0df04e7a407fbd3d9c1e77a69ae6/revisions/rev_000001/model.py:L66-L95,L376-L475` | tube_from_spline_points 手柄/腿/fork arm + ExtrudeWithHolesGeometry dropout/axle/washer，分离 fork_assembly |
| S9 | `rec_wheelbarrow_194a0df04e7a407fbd3d9c1e77a69ae6` | `data/records/rec_wheelbarrow_194a0df04e7a407fbd3d9c1e77a69ae6/revisions/rev_000001/model.py:L514-L543` | 五件 FIXED 串链：handle_frame→tray FIXED / →rear_legs FIXED / →fork FIXED / fork→wheel CONTINUOUS |
| S10 | `rec_wheelbarrow_efeca1d8fd874d919977bfb8e49377d1` | `data/records/rec_wheelbarrow_efeca1d8fd874d919977bfb8e49377d1/revisions/rev_000001/model.py:L383-L437` | 折叠 rear_stand（hinge sleeve+foot pad），body→wheel CONTINUOUS + body→rear_stand REVOLUTE（axis 0,1,0，lower 0 upper 1.25） |
| S11 | `rec_wheelbarrow_2960ce51d55a4487994203a4e54d3a0a` | `data/records/rec_wheelbarrow_2960ce51d55a4487994203a4e54d3a0a/revisions/rev_000001/model.py:L298-L395` | `for index in (left,right)` 多重生成 side_tube FIXED + level_foot PRISMATIC（axis 0,0,1，lower -0.018 upper 0.040 可调平脚） |
| S12 | `rec_wheelbarrow_224ee9182cab4e9eaa3a2b8d99c7a404` | `data/records/rec_wheelbarrow_224ee9182cab4e9eaa3a2b8d99c7a404/revisions/rev_000001/model.py:L438-L480` | fold-flat 收纳变体：frame→tray REVOLUTE / →handles REVOLUTE / handles→rear_legs REVOLUTE / fork FIXED / fork→wheel CONTINUOUS |
| S13 | `rec_wheelbarrow_e94d070a072c489db76d7a00e2b1ccaa` | `data/records/rec_wheelbarrow_e94d070a072c489db76d7a00e2b1ccaa/revisions/rev_000001/model.py:L334-L355` | axle 作为 root：axle→wheel CONTINUOUS + axle→body REVOLUTE dump_pivot（绕前轮轴线翻斗，lower 0 upper 0.78） |

## 槽位 + 候选模块表

### Slot A：chassis_body（承载底架的部件分解方式）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `monolithic_frame` | S2 (9de7eb) | `model.py:L121-L158` | ✅ seed=0 | 单个 `frame` 部件融合 tray 壳 + rim + 双 handle + brace + 后腿 + foot + fork arm + axle boss，全部一体，无内部 FIXED 关节 |
| `frame_plus_bolted_tray` | S6 (cb2aea) | `model.py:L310-L316` | | `frame`（管架+fork+腿）与独立 `tray` 两件，tray 通过 FIXED `tray_mount` 螺接到 frame 上 |
| `upper_body_module_chain` | S7 (1c02a48) | `model.py:L34-L199,L380-L385` | | `upper_body_module` 把 tray+handle+腿合成一件，作为 bolt-on 串链的根模块（前接 fork_module）|
| `frame_tray_handles_legs_split` | S9 (194a0d) | `model.py:L59-L63,L514-L527` | | handle_frame 为根，tray / rear_legs 各为独立部件，分别 FIXED 到 handle_frame（最大化模块拆分）|

### Slot B：wheel_mount（fork/axle 接口与轮自旋父链）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `integrated_fork_axle` | S2 (9de7eb) | `model.py:L153-L158,L192-L200` | ✅ seed=0 | fork arm + plate + axle_boss 直接做在 chassis 上，wheel CONTINUOUS 的 parent 就是 chassis；origin 在两 fork plate 之间 |
| `separate_fork_module` | S9 (194a0d) | `model.py:L376-L445,L528-L543` | | 独立 `fork_assembly`（crown+arm+dropout+axle+washer），FIXED 到 chassis，wheel CONTINUOUS 的 parent 是 fork |
| `separate_axle_module` | S7 (1c02a48) | `model.py:L268-L303,L387-L402` | | fork 与 axle 再拆开：fork_module FIXED→ `axle_module`（shaft+spacer+nut）FIXED，wheel CONTINUOUS 的 parent 是 axle_module |
| `axle_root_pivot` | S13 (e94d07) | `model.py:L119-L133,L334-L342` | | `axle` 部件作为模型 root，wheel 与 body 都挂在 axle 下（用于绕轴线翻斗的特殊拓扑）|

### Slot C：front_wheel（前轮 mesh 构造方式）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `sdk_wheel_tire_geometry` | S2 (9de7eb) | `model.py:L160-L190` | ✅ seed=0 | 用 SDK `TireGeometry` + `WheelGeometry`（rim/hub/spokes/bore/bolt_pattern）生成高保真轮，绕 Z 转 90° 对齐 |
| `lathe_profile_wheel` | S2b (91c0b1) / S7 (1c02a48) | `model.py:L228-L272` | | 用 `LatheGeometry` 旋转 tire/rim/hub 剖面（再 rotate_y），断面真实、参数化轮廓 |
| `stacked_cylinder_wheel` | S3 (0002) | `model.py:L89-L139` | | 多个同轴 `Cylinder`（tire/sidewall/rim_band/hub/axle_sleeve）叠出轮，外加 spoke_bar，纯 primitive |
| `torus_annulus_wheel` | S8 (194a0d) | `model.py:L478-L512` | | `TorusGeometry` 做胎面 + `ExtrudeWithHolesGeometry` annulus 做 rim/disc/hub，环状构造 |

### Slot D：aux_articulation（除前轮自旋外的可选第二自由度，gated）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `none_single_dof` | S2 (9de7eb) / S2b (91c0b1) | `model.py:L192-L200` | ✅ seed=0 | 默认成熟域：除 wheel CONTINUOUS 外没有任何活动关节；所有 tray/腿/手柄都是 FIXED 或一体 |
| `dump_tray_revolute` | S5 (0002) / S13 (e94d07) | `model.py:L413-L421` | | tray（或 body）通过 REVOLUTE 绕侧向 Y 轴翻斗倾倒，lower≈0、upper≈0.5–0.78 rad |
| `folding_rear_stand_revolute` | S10 (efeca1) | `model.py:L429-L437` | | 独立 `rear_stand` 通过 REVOLUTE 绕 Y 折叠收起，lower 0 upper≈1.25 rad |
| `level_foot_prismatic` | S11 (2960ce) | `model.py:L361-L395` | | 左右 `level_foot` 通过 PRISMATIC 沿 Z 上下调平，lower≈-0.018 upper≈0.040 m（成对 multiplicity）|
| `fold_flat_revolute_set` | S12 (224ee9) | `model.py:L438-L464` | | 收纳变体：tray / handles / rear_legs 各一个 REVOLUTE 折平，lower 0 upper 1.25–1.45 rad |

### Slot E：rear_support_detail（后支撑腿/脚的形态）
| module_name | 5_star_source | model.py:Lx-Ly | seed=0 anchor | 结构特征 |
|---|---|---|---|---|
| `tube_legs_with_pads` | S8 (194a0d) | `model.py:L292-L374` | ✅ seed=0 | tube_from_spline_points 弯管腿 + spreader + 橙色 foot pad + mount riser，独立成 rear_legs 部件 |
| `box_strut_legs` | S7 (1c02a48) | `model.py:L126-L185` | | spline 管腿 + box leg_clamp + box foot + leg_spreader，融进 upper_body 模块 |
| `skid_rest_legs` | S4 (0002) | `model.py:L162-L267` | | 短斜管 rear leg + 大 box skid 脚 + rear_rest_pad（翻斗底架的稳定支撑）|

## 槽位图（slot graph）
- pattern：**mixed**（A→B→C 为结构主链 + D 为带 multiplicity 的可选活动支链 + E 为附着在 A 上的细节槽）
- 主链（linear chain，全部 FIXED 或一体）：
  ```
  [Slot A chassis_body] --FIXED/一体--> [Slot B wheel_mount fork/axle] --CONTINUOUS--> [Slot C front_wheel]
        |                                                                   ^
        | (E rear_support_detail 附着在 A 上，FIXED 或一体)                  |
        v                                                                   |
  [Slot D aux_articulation] (gated 第二自由度，挂在 A 或 B 上)               (唯一主关节)
  ```
- multiplicity（仅在 `level_foot_prismatic` / `fold_flat_revolute_set` 分支）：
  ```
  for side in (left, right):  side_tube_{i} --FIXED--> chassis ;  level_foot_{i} --PRISMATIC--> side_tube_{i}
  ```
- parallel children（仅 `axle_root_pivot` 分支）：axle 作为 root，wheel 与 body 为其两个 child（一个 CONTINUOUS，一个 REVOLUTE）

## 部件（Parts）
| 部件 | 描述 | 参数 | 来源 |
|---|---|---|---|
| `frame` / `chassis` / `upper_body` | 落地刚性底架：tray 壳 + 双 tubular handle + 横/斜 brace + fork 接口；可一体或拆成多模块 | `chassis_style`, `length`, `track_width`, `handle_rise`, `tray_depth` | S2 / S4 / S6 / S7 / S9 |
| `tray` | 装料盘（可独立或融进 chassis）；tapered loft / 深盘 / 平板皆可 | `tray_style`, `tray_len`, `tray_width`, `tray_height`, `wall_thickness` | S1 / S5 / S6 / S9 |
| `fork_assembly` / `fork_module` | 抱住前轮的双臂叉 + crown + dropout，外置或集成 | `fork_style`, `fork_gap`, `dropout_thickness` | S2 / S7 / S8 |
| `axle_module` | 可选独立轴模块：shaft + spacer + nut + washer | `has_axle_module`, `axle_radius`, `spacer_width` | S7 / S13 |
| `front_wheel` | 单前轮：tire + rim + hub（+ spoke/bore），绕侧向轴自旋 | `wheel_style`, `wheel_radius`, `wheel_width`, `hub_radius` | S2 / S2b / S3 / S8 |
| `rear_legs` / `feet` | 后支腿 + 脚垫/skid，落地稳定，可独立或融进 chassis | `rear_support_style`, `leg_spread`, `foot_pad_size` | S4 / S7 / S8 |
| `rear_stand` | 可选折叠脚架（gated `aux_articulation`）| `has_rear_stand`, `stand_len` | S10 |
| `level_foot` | 可选调平脚（gated，成对 PRISMATIC）| `has_level_feet`, `foot_travel` | S11 |
| `hardware_detail` | axle washer / bolt head / pivot plate / 防护件等 fixed 细节 | `detail_level` | S4 / S7 / S10 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `wheel_spin` | CONTINUOUS | B.fork_assembly / B.axle_module / A.chassis | C.front_wheel | `(0,1,0)` 或 `(1,0,0)`（取决于车身长轴朝向）| n/a（无限位）| 唯一主关节：前轮绕侧向 axle 自旋，origin 在两 fork plate/dropout 中心 | S2 / S2b / S5 / S7 / S9 |
| `chassis_to_tray` | FIXED | A.frame | A.tray | n/a | n/a | tray 螺接到 frame（仅 `frame_plus_bolted_tray` / split 分解时存在）| S6 / S9 |
| `chassis_to_fork` | FIXED | A.frame | B.fork_assembly | n/a | n/a | 外置 fork 固定到底架（`separate_fork_module` 时存在）| S9 |
| `fork_to_axle` | FIXED | B.fork_module | B.axle_module | n/a | n/a | axle 模块固定到 fork（`separate_axle_module` 时存在）| S7 |
| `chassis_to_rear_legs` | FIXED | A.frame | E.rear_legs | n/a | n/a | 后腿固定到底架（rear_legs 独立成件时存在）| S9 |
| `dump_pivot` | REVOLUTE | A.frame / B.axle | A.tray / A.body | `(0,-1,0)` | `[0, ~0.5–0.78]` rad | gated：tray 绕侧向轴翻斗倾倒（`dump_tray_revolute`）| S5 / S13 |
| `rear_stand_fold` | REVOLUTE | A.body | D.rear_stand | `(0,1,0)` | `[0, ~1.25]` rad | gated：折叠脚架收起（`folding_rear_stand_revolute`）| S10 |
| `level_foot_slide` | PRISMATIC | D.side_tube | D.level_foot | `(0,0,1)` | `[~-0.018, ~0.040]` m | gated：左右调平脚升降（`level_foot_prismatic`，成对）| S11 |
| `handle_fold` / `leg_fold` | REVOLUTE | A.frame / A.handles | A.handles / E.rear_legs | `(0,±1,0)` | `[0, ~1.35–1.45]` rad | gated：fold-flat 收纳（`fold_flat_revolute_set`）| S12 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `chassis_style` | enum | `monolithic` / `bolted_tray` / `upper_body_module` / `full_split` | `monolithic` | 决定 Slot A 部件数与内部 FIXED 关节数 | S2 / S6 / S7 / S9 |
| `wheel_mount_style` | enum | `integrated` / `fork_module` / `axle_module` / `axle_root` | `integrated` | 决定 wheel_spin 的 parent 与 fork/axle 拆分 | S2 / S7 / S9 / S13 |
| `wheel_style` | enum | `sdk_wheel` / `lathe` / `stacked_cylinder` / `torus_annulus` | `sdk_wheel` | 决定前轮 mesh 构造路径 | S2 / S2b / S3 / S8 |
| `aux_articulation` | enum | `none` / `dump_tray` / `rear_stand` / `level_feet` / `fold_flat` | `none` | gated 第二自由度；默认单 DOF | S5 / S10 / S11 / S12 |
| `rear_support_style` | enum | `tube_legs_pads` / `box_strut` / `skid_rest` | `tube_legs_pads` | 后支撑形态 | S4 / S7 / S8 |
| `body_axis` | enum | `x_forward` / `y_forward` | `x_forward` | 决定 wheel_spin axis：x_forward→(0,1,0)，y_forward→(1,0,0) | S2 / S2b / S9 |
| `overall_length` | float | `0.95-1.65` | sampled | overall AABB 长度（包络合理性）| S5 |
| `track_width` | float | `0.55-0.80` | sampled | overall 宽度 = handle/腿 横向跨度 | S5 |
| `wheel_radius` | float | `0.14-0.24` | sampled | tire 外半径；需 > 0.55 * frame_height（大轮约束）| S2 / S2b |
| `fork_gap` | float | derived | derived | `wheel_width + 2 * fork_clearance`，fork plate 须夹住 tire | S2 / S9 |
| `dump_limit` | float | `0.45-0.78` rad | derived | 仅 `aux=dump_tray`；REVOLUTE upper | S5 / S13 |
| `stand_fold_limit` | float | `1.0-1.45` rad | derived | 仅 `aux=rear_stand`/`fold_flat`；REVOLUTE upper | S10 / S12 |
| `foot_travel` | float | `0.03-0.06` m | derived | 仅 `aux=level_feet`；PRISMATIC 行程 | S11 |
| `detail_level` | enum | `clean` / `standard` / `heavy_hardware` | `standard` | washer/bolt/pivot plate/guard 密度 | S4 / S10 |

## 拓扑多样性审计
- per-slot candidate_count：

| slot | candidate_count |
|---|---|
| A chassis_body | 4 |
| B wheel_mount | 4 |
| C front_wheel | 4 |
| D aux_articulation | 5 |
| E rear_support_detail | 3 |

- total_combinations = 4 × 4 × 4 × 5 × 3 = **960**

## Validator
| 检查项 | 标准 |
|---|---|
| identity | 必须有 chassis/frame（含 tray + 双 handle + rear support）+ 单个 front_wheel + 至少一个 fork/axle 接口 |
| single front wheel | 恰好一个自旋轮部件；不允许多轮/后轮（否则是 cart/hand truck）|
| primary joint | wheel_spin 必须为 CONTINUOUS，axis 为侧向（与 body 长轴垂直且水平），无 lower/upper |
| wheel_spin parent | parent 必须是 fork/axle/chassis 中实际抱轮的部件；origin 在 fork plate/dropout 中心 |
| fork containment | fork plate/dropout 必须分列 tire 两侧并留 clearance（不穿胎、不悬空）|
| grounding | 静止位姿下 frame + rear legs/feet 与地面/前轮共同支撑，rear support 落地 |
| aux articulation gating | dump/rear_stand/level_feet/fold_flat 只在对应 `aux_articulation` 分支出现；默认 `none` 只有 wheel_spin |
| dump axis | `dump_tray` 的 REVOLUTE 轴为侧向 Y，lower=0、upper∈[0.45,0.78]，倾倒后 tray 不穿轮 |
| level feet multiplicity | `level_feet` 必须左右成对 PRISMATIC，axis Z，行程有限 |
| no floating | tray / handle / legs / fork / axle / wheel / 所有 hardware 均附着或受关节约束，无悬浮 |
| axis-vs-orientation | `body_axis` 与 wheel_spin axis 必须一致（x_forward↔(0,1,0)，y_forward↔(1,0,0)），不可矛盾 |

## Reject cases
- 多个轮子，或轮子在底部四角 → 是手推车/cart，不是独轮车。
- wheel_spin 用 REVOLUTE 带 lower/upper，或轴指向竖直/前后 → 前轮无法自由滚动。
- fork plate/dropout 不夹 tire（单侧或穿胎或悬空）。
- 把 tray-dump / 折叠脚架 / 调平脚硬塞进默认 `none` 配置，导致默认就有多余自由度。
- `dump_tray` 翻斗后 tray 与前轮/底架穿模，或 upper 限位 > π/2 不合常理。
- rear legs/feet 不落地，整车只靠前轮悬停。
- `body_axis` 与 wheel_spin axis 矛盾（例如长轴沿 X 却让轮绕 X 自旋）。
- handle/legs/washer/bolt/guard 等细节悬浮或未挂在 chassis/fork 上。

## 与相邻类别的边界
- vs **garden cart / utility cart**：cart 是两轮或四轮、wheel 在车厢底部、靠拉杆牵引；独轮车只有一个前轮且靠人抬后腿平衡。若样本出现 ≥2 个落地承重轮，应判为 cart，不属本类。
- vs **hand truck / sack barrow**：hand truck 有竖直背板、两个轮在底部、货物靠背板直立堆叠、倾斜推行；独轮车是水平 tray + 单前轮。
- vs **serial_elbow_arm / 其它机械臂**：本类只有 wheel_spin 一个 always-on 自由度，第二自由度仅限翻斗/脚架/调平/折平这些独轮车专属机构，不引入连杆式 reach 关节。
- vs **monitor_mount / 通用 pan-tilt**：独轮车的 REVOLUTE 仅用于翻斗/折叠，axis 固定为侧向，且必有落地支撑，不做空间指向调节。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | approved（human-reviewed）|
| reviewer notes | SPEC_ONLY_DRAFT；默认成熟域=单 DOF（monolithic_frame + integrated_fork + sdk_wheel + aux=none + tube_legs）；翻斗/脚架/调平/折平为 gated `aux_articulation` 分支。等待人工审核 |
