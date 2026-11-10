# Table Tennis Table — Modular Spec

> 来源小类：`picture/0611/table_tennis_table`（articraft_data 上游小类）。
> 上游 source map：`articraft_data/picture_expansion/template_source_maps/0611__table_tennis_table.md`。
> 已同步 records（本仓库 `data/records/`）：4 个 parent（001-004）+ 10 个 fork 变体（top_topology×2 / fold_motion×2 / support_topology×3 / caster_count×3），共 **14 个 5 星 workbench-only records**，全部 built ✓，全部 rating=5。行号按各 record 的最新 `revisions/rev_*/model.py`。

## 元信息
| 项 | 值 |
|---|---|
| slug | `table_tennis_table` |
| template path | `agent/templates/table_tennis_table.py` |
| test path (optional) | 不写；sweep-pipeline 为唯一验收 |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（中央 `chassis` root 携带两片可翻起 `table_half_*` + net 装配 + N 个 caster；固定 named slots，无 slot-graph 串链）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 14 |
| read_count | 14（全部读；4 parents 全文；10 forks 关键 module 段）|
| read_scope | 所有 5 星样本均已阅读 model.py 全文或采纳段。003 与 004 的 rev_000002 为最新已修复版本 |
| source_index_policy | 只有被采纳为 module source 的记录进入下方 source 表；未采纳的样本仅参与 §8.5 六轴辅证 |

## 核心身份

**Table tennis table** = 竞技/家用乒乓球台。核心结构：**中央承载底盘（chassis / trolley / pedestal）**，从上方以一对/一根 REVOLUTE 铰接托起 **两片蓝色 playing halves**，中央固定 **中央球网** 与 **网柱夹**。底盘下方由 **N 个滚轮/casters 或固定接地脚** 触地，两片桌面可各自或联动向上翻起进入 storage / playback 姿态。默认成熟域：**中央底盘 rollaway/portable table**（001/002/003），regulation 2.740 × 1.525 × 0.760 m 或 portable-scale。活动语义：two REVOLUTE 半桌翻抬（independent 或 synchronized-mimic）+ N 个 CONTINUOUS 滚轮 + 可选 caster swivel。

不该混入：**折叠桌/办公桌**（无网、无 blue 竞技面）、**折叠椅**（承坐、非承球）、**折叠床**（有卧面、无中央网）、**pool_table / billiards**（cushion+pocket 边框、非可折叠 blue 面）、**户外野餐桌 / picnic**（无中央网 + 无 blue 面 + 无 fold）、**004 全式 compact folding 面对面折叠 suitcase**（root 换成 west_top、无中央 chassis + net → 是独立形态子域，见 §9 说明；初版模板不采样该形态）。

## 槽位 + 候选模块表

> **建模注记（重要）**：核心 topology 为 `parallel_children`：以 `chassis`（=root）为共同 parent，`table_half_0` / `table_half_1` 各自以 REVOLUTE +Y / −Y 铰接，`caster_i` × N 各自以 CONTINUOUS +Y 铰接。net 与 net_posts / clamps 是 chassis 的 visuals（Rule 1：不动 → 非独立 part）。四个 slot（chassis_form / top_topology / fold_motion / caster_count）**不是串链而是选 chassis+halves+driver+wheel 的联合装配旋钮**；其笛卡尔积构成结构多样性，§9 有 gating。

### Slot A：`chassis_form`（底盘形态 / Primary Form Family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `portable_trolley_chassis`（基线） | forked_anchor | rec_picturex_0611__table_tennis_table__001 | rev_000001/model.py L63-176 | eligible if compatible | 双 lower_rail + crossrail + 4 uprights + net_post_clamp + center_net + net_tape；紧凑 trolley，四足向下伸出 caster stems |
| `commercial_double_rail_chassis` | forked_anchor | rec_picturex_0611__table_tennis_table__002 | rev_000001/model.py L186-278 | eligible if compatible | 两 lower_rails × 两 lower_crossbars + 4 uprights + upper_rails + hinge_beam + diagonal_braces；商用 double-rail 骨架，caster forks fixed on chassis |
| `rollaway_wheel_truck_chassis` | forked_anchor | rec_picturex_0611__table_tennis_table__003 | rev_000002/model.py L294-395 | eligible if compatible | X-braced center_beam + cross_beam + 两个 wheel_truck + lift_towers + hinge_blocks；rollaway 中央钢架 |

（Primary Form Family = ③ 主体形态家族；每 candidate 标 `form_subtype`：`portable_trolley_chassis` = Volumetric Envelope Form（紧凑立方 trolley 体量）；`commercial_double_rail_chassis` = Planar Boundary Form（双低轨的水平边界）；`rollaway_wheel_truck_chassis` = Macro Surface Construction（X-brace + wheel_truck 宏观构成））

### Slot B：`top_topology`（两片桌面顶板 topology）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `rigid_one_piece_half`（基线） | forked_anchor | rec_picturex_0611__table_tennis_table__001（top-topology anchor 001） | rev_000001/model.py L178-257 + L259-260 | eligible if compatible | 单片 `blue_surface` + apron + 白色边线 + leg_mount；每 half 一整片刚性顶板 |
| `four_panel_top` | forked_anchor | rec_0611_table_tennis_table_var_top_topology_four_panel | rev_000001/model.py（`playing_panel` + `net_panel` 语义）| eligible if compatible | 每 half 划分 playing_panel（连续 blue）+ 白线 + 边界 apron；panel 语义化的四片分区顶板（视觉/结构等价于单片但白线细分为独立子 visuals，改变宏观表面构成） |

（两 candidate 都是同 part-tree（chassis + half_0 + half_1）、同关节；仅换 half 的 visual family（整片 blue vs 四分 panel），属于 ③ Macro Surface Construction 分支。 2 个 candidate 是样本池上限；理由：source map 仅提供两个 top-topology fork。）

### Slot C：`fold_motion`（半桌 fold 关节机制 / joint type family）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `independent_dual_lift`（基线） | forked_anchor | rec_picturex_0611__table_tennis_table__001 | rev_000001/model.py L262-281（`chassis_to_half_0` / `chassis_to_half_1`） | eligible if compatible | 两个独立 REVOLUTE(+Y / −Y) 关节，两 half 各自翻抬；lower=0，upper=1.50-1.55 rad；关节数 2（fold）|
| `synchronized_dual_lift` | forked_anchor | rec_0611_table_tennis_table_var_fold_motion_synchronized_dual_lift | rev_000001/model.py L458-527（synchronization_shaft + Mimic followers）| eligible if compatible | 新增 `synchronization_shaft` 独立 part + 一根 REVOLUTE(+Y) `synchronized_dual_lift` 驱动关节，两 half REVOLUTE Mimic(driver, ±1, offset 0/−π/2)；关节数 3（1 driver + 2 mimic follower）|
| `manual_playback_half` | forked_anchor | rec_picturex_0611__table_tennis_table__003 | rev_000002/model.py L451-468（`near_half_lift` / `far_half_lift`, upper/lower 均为 ±π/2） | eligible if compatible | 两独立 REVOLUTE(+Y / −Y)，range 覆盖 playback（一片直立 / 一片平放）+ storage（两片直立），关节数 2 |

（3 candidate；`independent_dual_lift` 与 `manual_playback_half` 结构同（2 REV），只 range 不同——判为 ② 关节类型细分（range 覆盖 playback 姿态语义）。`synchronized_dual_lift` 新增独立 shaft part + Mimic follower → 关节拓扑真的不同。样本池支撑充分。）

### Slot D：`caster_count`（滚轮 multiplicity 轴）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `n4_casters`（基线） | forked_anchor | rec_0611_table_tennis_table_var_caster_count_4 / 001 parent | rev_000001/model.py L114-140,349-372 | eligible if compatible | 4 wheels，位于四角；CONTINUOUS(+Y) 独立；每个 wheel 一 tire + hub |
| `n6_casters` | forked_anchor | rec_0611_table_tennis_table_var_caster_count_6 | rev_000001 | eligible if compatible | 6 wheels，均匀 3×2 或 2×3 分布 |
| `n8_casters` | forked_anchor | rec_0611_table_tennis_table_var_caster_count_8 / 002 | rev_000001/model.py L338-361 | eligible if compatible | 8 wheels，4×2 分布 |

（module-per-N；multiplicity 计入 slot_choice 名（`n4/n6/n8`）；N 计"覆盖不计数"—`VISUAL_DIVERSITY_MODEL.md` §2；见 §8。）

## 槽位图（slot graph）

pattern: `parallel_children`（固定 named parts + 4 orthogonal 选择槽；无串链）

```
chassis (ROOT, chassis_form 槽决定其骨架 visual + net + net_posts + net_clamps 装配)
   │  visuals: rails / uprights / hinge_beam / net_panel / net_tape / net_posts / net_clamps
   │
   ├──[chassis_to_half_0: REVOLUTE +Y @ hinge_beam(-seam_gap/2, 0, top_z)]──> table_half_0 (top_topology 决定 visuals)
   │                                        · if fold_motion == synchronized_dual_lift → mimic(driver, +1, offset=0)
   │                                        · range: independent[0,1.50] / playback[0,π/2] / synchronized[0,π/2 via mimic]
   │
   ├──[chassis_to_half_1: REVOLUTE −Y @ hinge_beam(+seam_gap/2, 0, top_z)]──> table_half_1 (top_topology 决定 visuals)
   │                                        · if fold_motion == synchronized_dual_lift → mimic(driver, +1, offset=-π/2)
   │
   ├──(可选，仅 fold_motion == synchronized_dual_lift)
   │  [chassis_to_sync_shaft: REVOLUTE +Y @ sync_bearing]──> synchronization_shaft
   │
   └── caster_i × N (caster_count 决定 N 与位置):
       [chassis_to_caster_i: CONTINUOUS +Y @ (x_i, y_i, wheel_r)]──> caster_i
                                        · axis = +Y（世界轴 / 沿 y 前后滚动）
```

接口点位与 joint 语义：
- **hinge_beam（core interface）**：chassis 顶端一根 `hinge_beam` visual（world y-span、TABLE_WIDTH+margin 宽），承担 `chassis_to_half_0` / `chassis_to_half_1` 的 origin；MatingContract 声明 parent `hinge_beam` positive_z 面 vs child `playing_panel` negative_z 面。
- **caster 接口**：chassis 底端下伸的 `caster_socket_i` visual（fork_crown 或 caster_crown），与 caster 独立 part 的 `swivel_stem` positive_z 面对接。
- **fold_motion=synchronized_dual_lift** 时新增 `sync_bearing_block` visual on chassis + `synchronization_shaft` part + 两个 Mimic 关系（chassis_to_half_i.mimic = synchronized_dual_lift, multiplier=1.0, offset=0 or -π/2 按 side）。
- **rest pose**：所有 fold 关节 = 0 → 两片桌面水平贴 hinge_beam；caster 关节 = 0 → 桌立地。
- **MatingContract 政策**：`chassis_to_half_i` 声明 MatingContract（`hinge_beam` +z ↔ `playing_panel` -z, contact_tol=0.003）；`chassis_to_sync_shaft` 声明（`sync_bearing_block` +y ↔ `cross_shaft` −y? 不宜——用 grandfathered captured-pin 处理 shaft，declare element-scoped `allow_overlap`(sync_bearing_block, cross_shaft, reason="shaft captured in bearing")）；每个 `chassis_to_caster_i` grandfather（swivel-stem 捕获）+ element-scoped allow_overlap(caster_socket_i, swivel_stem)。

## 每槽位 Module Emits / Interfaces

### Slot A / `portable_trolley_chassis`（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chassis`（visuals: lower_rail_near/far, lower_crossrail, stiffener_crossrail, crossrail_riser_0/1, upper_strut_0_0..1_1, support_pad_0_0..1_1, net_post_0/1, net_clamp_0/1, net_clamp_brace_0/1, center_net, net_tape, hinge_beam, caster_socket_i…）| 001 L63-176 |
| internal joints | 无（chassis 是 root，无 chassis-internal REVOLUTE）| — |
| interfaces | hinge_beam +z（承载 halves）；caster_socket_i +z（承载 casters） | 001 |

### Slot A / `commercial_double_rail_chassis`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chassis`（visuals: lower_rail_0/1, lower_crossbar_0/1, upright_ix_iy, upper_rail_0/1, diagonal_brace_0/1, hinge_beam, net_post_0/1, net_clamp_0/1, net_panel, net_tape, caster_socket_i…）| 002 L186-278 |
| internal joints | 无 | — |
| interfaces | hinge_beam +z；caster_socket_i +z | 002 |

### Slot A / `rollaway_wheel_truck_chassis`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chassis`（visuals: center_beam, cross_beam, lower_spine, upper_rail_0/1, wheel_truck_a/b, socket_a/b_a/b, leg_a/b_a/b（_segment），frame_brace_0/1, lift_tower_a/b, tower_brace_*, hinge_pin_i_j, hinge_block_i_j, bearing_strut_*, net, net_tape, net_post_0/1, net_clamp_0/1, net_support_*）| 003 L294-429 |
| internal joints | 无 | — |
| interfaces | hinge_beam ↔ chassis-carried `hinge_pin_i_j` +z；caster_socket_i +z | 003 |

### Slot B / `rigid_one_piece_half` × 2（half_0 / half_1）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `table_half_i`（visuals: blue_surface, far_boundary, near_boundary, end_boundary, center_marking, side_apron_near/far, end_apron, hinge_apron, leg_mount_0/1, latch_mount）| 001 L178-257 |
| internal joints | 无（可选 legs 不列入本模板初版）| — |
| interfaces | playing_panel −z（贴 hinge_beam +z）| 001 |

### Slot B / `four_panel_top` × 2
| emits | 描述 | 来源 |
|---|---|---|
| parts | `table_half_i`（visuals: playing_panel（一整块 blue）, sideline_0/1, end_line, side_apron_0/1, end_apron, seam_apron, underside_rail_0/1, leg_mount_0/1, brace_mount_0/1）| 002 L45-117 |
| internal joints | 无 | — |
| interfaces | playing_panel −z | 002 |

### Slot C / `independent_dual_lift`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无新 part | — |
| internal joints | `chassis_to_half_0` REVOLUTE +Y limits[0,1.50]；`chassis_to_half_1` REVOLUTE −Y limits[0,1.50] | 001 L262-281 |
| interfaces | 用 hinge_beam ↔ playing_panel MatingContract | 001 |

### Slot C / `synchronized_dual_lift`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `synchronization_shaft`（visuals: cross_shaft, crank_hub_0/1, near_crank_arm_i, far_crank_arm_i, near_lift_link_i, far_lift_link_i）+ chassis 上增 `sync_bearing_block_0/1`, `sync_bearing_brace_0/1` | var_fold_motion_synchronized_dual_lift L360-547 |
| internal joints | `synchronized_dual_lift` REVOLUTE +Y limits[0,π/2]（driver）；`chassis_to_half_0` mimic(driver, +1, 0)；`chassis_to_half_1` mimic(driver, +1, −π/2）| var L519-547 |
| interfaces | 同 basic + shaft captured in bearing_block（grandfather + element-scoped allow_overlap）| var |

### Slot C / `manual_playback_half`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无新 part | — |
| internal joints | `chassis_to_half_0` REVOLUTE +Y limits[0,π/2]；`chassis_to_half_1` REVOLUTE −Y limits[−π/2,0] | 003 rev_000002 L451-468 |
| interfaces | 同 basic | 003 |

### Slot D / `n{4,6,8}_casters`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `caster_i` × N（visuals: wheel_tire Cylinder, wheel_hub Cylinder）+ chassis 上 caster_socket_i visuals | 001/002/003 各 caster helper |
| internal joints | `chassis_to_caster_i` CONTINUOUS axis=+Y (world Y=前后滚动方向)，N 个 | 001 L363-372 / 002 L350-361 / 003 L441-449 |
| interfaces | caster_socket_i (+z) ↔ caster_i.wheel_tire (Cylinder captured)；element-scoped allow_overlap(caster_socket, wheel_hub, reason="axle stem captured in fork") | source |

## 参数范围汇总

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `chassis_form` | enum | portable_trolley_chassis / commercial_double_rail_chassis / rollaway_wheel_truck_chassis | portable_trolley_chassis | choice | procedural sampler | Slot A |
| `top_topology` | enum | rigid_one_piece_half / four_panel_top | rigid_one_piece_half | choice | procedural sampler | Slot B |
| `fold_motion` | enum | independent_dual_lift / synchronized_dual_lift / manual_playback_half | independent_dual_lift | choice | procedural sampler；`synchronized_dual_lift` 依赖 chassis_form ∈ {commercial_double_rail_chassis, rollaway_wheel_truck_chassis}（bearing block 空间需要，`portable_trolley_chassis` 通过降级） | Slot C |
| `caster_count` | enum | n4_casters / n6_casters / n8_casters | n4_casters | choice | procedural sampler | Slot D |
| `palette_style` | enum | tournament_blue / powdercoat_black / commercial_blue / outdoor_galvanized | tournament_blue | choice | procedural sampler；驱动所有材质 rgba | palette |
| `table_length` | float | [2.10, 2.80] m | 2.740 | independent | 均匀采样后 clamp；规则设 upper 允许 short portable 缩放 | source |
| `table_width` | float | [1.20, 1.60] m | 1.525 | independent | 均匀采样 clamp | source |
| `table_height` | float | [0.72, 0.82] m | 0.760 | independent | 均匀采样 clamp | source |
| `half_length` | float | derived | derived | equation | `= (table_length − seam_gap) / 2` | 001 |
| `caster_radius` | float | [0.045, 0.075] m | 0.055 | independent | 均匀采样 clamp | source |
| `net_height` | float | [0.148, 0.158] m | 0.1525 | independent | 均匀采样 clamp（regulation ≈ 0.1525）| 001 |
| `fold_upper_half_0` | float | derived | derived | conditional | 由 fold_motion 决定：independent=1.50, synchronized=π/2（driver）, playback=π/2 | Slot C |
| (—) | constraint | — | — | inequality | 折叠 upper 状态两 half 必须不穿模；hinge_beam 与 chassis 主体不重叠 | 接口 |

**连续尺寸采样契约**：先采 `table_length/width/height/caster_radius/net_height` independent → 派生 `half_length` equation → clamp 到 [min,max] → conditional 按 fold_motion 派生 fold_upper。

### 7.5 编译预算 / compile budget（必填）

**每-seed 预算：≤20s（typical 8-15s）**。依据：整个模型使用纯 Box + Cylinder primitives（无 lathe / cadquery / mesh），part 总数 ~10-16（1 chassis + 2 halves + 4-8 casters ± 1 shaft），visual 总数 ~120-180；tessellation 分档：casters/hinge_beam ≤32 段，net/apron ≤48 段；shared caster mesh 复用同一 Cylinder。sweep 的 `--compile-timeout 120` 是 6× hangup 预算。

## Multiplicity / Copy Logic

- **有 1 根 multiplicity 轴：`caster_count`**：
  - `count_param`：`caster_count`（int），N_range=[4, 8]，实际实现档 `{4, 6, 8}`
  - sampling domain：`{n4: 0.45, n6: 0.35, n8: 0.20}`（小 N 高频、大 N 稀有）
  - copied object：caster part（`caster_i`，visuals: `wheel_tire` + `wheel_hub`）+ chassis 上 `caster_socket_i` visual
  - naming：`caster_0`..`caster_{N-1}`；joint `chassis_to_caster_i`
  - placement：均匀 2× x-station × (N/2)× y-side（N=4 → 2×2；N=6 → 3×2；N=8 → 4×2）
  - joint policy：每个 CONTINUOUS axis=+Y；MatingContract omit（swivel 捕获，grandfather）+ element-scoped allow_overlap(caster_socket_i, wheel_hub) + expect_contact(socket, tire)
  - source/gating：001 (n4) / var_count_6 / var_count_8；N 值在 slot_choice 里报原值（窄轴，无需分档）

## 视觉多样性 6 轴考察

| 轴 | 怎么判断（落到唯一主字段） | 有/无 | 若【有】列取值/范围 + source_type / 来源 · 若【无】写理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 3 chassis form（part-tree 一致但 visual family 变，属 ③ 的边界；仍列入 ①因为 chassis visuals 拓扑不同）；fold_motion 中 `synchronized_dual_lift` **加一条会动的 edge**（sync_shaft REVOLUTE + 两个 Mimic follower）→ 结构 distinct 一票；source-backed |
| └ multiplicity | 同构件 ×N | 有 | `caster_count ∈ {4, 6, 8}`；weighted `{0.45, 0.35, 0.20}`；报原值不分档；见 §8 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 有 | REVOLUTE(halves) + CONTINUOUS(casters) 均在 sweep；`fold_motion` 三 module 覆盖 independent-REVOLUTE / synchronized-driver+Mimic(REVOLUTE) / playback-REVOLUTE；range 不同；source-backed |
| ③ 主体形态家族 / Primary Form Family | 图&关节不变，换核心 part 的可识别几何形态原型（非缩放/换色）| 有 | **`chassis_form` slot 登记为 ③ Primary Form Family slot**：3 candidate，`form_subtype` 各为 Volumetric Envelope / Planar Boundary / Macro Surface Construction；每个 source-backed（001/002/003）|
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | 有 | 白色 boundary lines（`side_line_i` / `end_line` / `center_marking`）—— host-conformal（贴 blue_surface 顶面）；net_tape（白色 tape 顶带）；apron 印花 / safety_latch（红色）——均由宿主 blue_surface / apron 表面派生；record_only |
| ⑤ 尺寸/行程 | 离散全不变，只连续改尺寸/比例/行程 | 有 | table_length[2.10,2.80]，width[1.20,1.60]，height[0.72,0.82]，caster_radius[0.045,0.075]，net_height[0.148,0.158]；每非-continuous 关节运动包络：`chassis_to_half_i` REVOLUTE axis=±Y 方向=up-fold，range [0, upper]；upper: independent=1.50, synchronized=π/2 driver→mimic followers, playback ±π/2；`motion_test_plan`：`fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)` + targeted `ctx.pose({half_0_hinge: 0}, {half_0_hinge: upper/2}, {half_0_hinge: upper})` on both halves（or driver 单 pose 采样若 synchronized）|
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | 有 | 4 palette_style（≥3-6 覆盖）：`tournament_blue`（深蓝 + 白线 + 黑钢）；`powdercoat_black`（黑 chassis + 白线 + 深蓝 top）；`commercial_blue`（明蓝 + 银钢 + 红 accent）；`outdoor_galvanized`（灰镀锌 + 蓝浅面 + 无 accent）；材质大类 painted (all) + metal(steel/hardware) + rubber(caster tire)（≥ ceil(0.5×4)=2 大类 ✓）|

## 采样与覆盖审计

总组合数（不含 multiplicity 权重）：
**chassis_form(3) × top_topology(2) × fold_motion(3) × caster_count(3) × palette_style(4) = 216**。
拓扑 distinct（不含 palette、去 palette_style）：**3 × 2 × 3 × 3 = 54**。
若按 module_topology 关节数分类：j=2（independent/playback）× 4 组合 + j=3+2Mimic（synchronized）× 2 组合 → 拓扑等价类 ≈ 6 大类；覆盖充分。

理由：三个真结构轴（chassis_form=③, fold_motion=②/①, caster_count=multiplicity）+ 装饰轴 top_topology(④/③ 分区) + palette。fold_motion=synchronized 加一条 edge（sync_shaft）→ 关节图真的不同。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 独立采样各 enum + 各 continuous scale；seed=0 不特殊。

Procedural Sampling / Sweep Plan：
- sampler：`rng.choice` 五 enum（chassis_form, top_topology, fold_motion, caster_count, palette_style），再 uniform 各连续尺寸；
- compatibility matrix：仅一条 gate：`fold_motion == synchronized_dual_lift` **且** `chassis_form == portable_trolley_chassis` → 降级为 `independent_dual_lift`（trolley 无 lift_tower 空间放 sync bearing）。其他任意笛卡尔积均合法。
- random sweep seeds 0-35（初轮 pipeline fast+final），corner stage 覆盖极端 fold/caster 组合；
- viewer 目检：seeds 0-9 by `template batch`。

Topology target：1000-seed slot_choice tuple distinct 探针预计 ≈ 54 × N_effective(≈3) = 162（不到 300，但类别真实结构词汇表就 54 拓扑；report-only）。

Controlled local parameterization：`table_length` / `table_width` / `table_height` / `caster_radius` / `net_height` 均 `independent` 采样后 `resolve_config` clamp；`half_length = (table_length − seam_gap) / 2` 派生 `equation`；`fold_upper_half_i` 由 fold_motion `conditional` 派生。所有参数不改变 slot_choice、不破坏 hinge_beam ↔ playing_panel 接口 / caster socket 承载 / 半桌 fold 端点姿态 / 类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | rng.choice enums + uniform continuous | slot_choices matches build |
| compatibility matrix | synchronized ∧ portable_trolley → 降级 independent | no bearing overlap; no floating shaft |
| controlled local variation | 5 continuous scale independent + 1 equation + 1 conditional | proportions vary; hinge/caster interfaces stay |
| regression overrides | none | reviewer-selected only |
| random sweep | 0-35 fast+final +corner | axis_realization; failed_corner_seeds |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| chassis_form | 3 | yes | yes | ③ Primary Form Family（登记进 slot_choices）|
| top_topology | 2 | yes | 边界 | ④/③ visual family；source 上限 2 |
| fold_motion | 3 | yes | yes | 关节拓扑 & range family |
| caster_count | 3 | yes | yes | multiplicity 3 档 |

## Validator

- `slot_choices_for_seed(seed)` 返回 5 元组 `(chassis_form, top_topology, fold_motion, caster_count, palette_style)` 与实际 build 一致
- `config_from_seed(seed)` 对所有 seed 用 deterministic procedural sampling（含 seed=0）
- `resolve_config` clamp 各 continuous scale，派生 `half_length`，依 fold_motion 派 fold_upper，处理 synchronized-on-trolley 降级 gate
- MatingContract 存在于 `chassis_to_half_0/1`（`hinge_beam` +z ↔ `playing_panel`/`blue_surface` -z）
- fold 关节 axis=±Y，caster 关节 CONTINUOUS axis=+Y
- caster 数 N 与所选 `caster_count` 一致；每 caster 有 `wheel_tire` + `wheel_hub` visual，都有独立 CONTINUOUS 关节
- element-scoped `ctx.allow_overlap(chassis, caster_i, elem_a="caster_socket_i", elem_b="wheel_hub", reason="axle stem captured in fork")` × N
- 若 fold_motion == synchronized_dual_lift：`synchronization_shaft` part 存在，driver `synchronized_dual_lift` 是 REVOLUTE，两 half 关节 mimic=driver；element-scoped allow_overlap(sync_bearing_block_i, cross_shaft)
- 关节全程不穿模：`fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)` + targeted `ctx.pose({fold_driver: upper})` 单独测 storage 姿态

## Reject cases

- chassis 里塞入 fold 关节（如 tilt）而 chassis 应始终是 root 世界不动 → 违背 parallel_children 语义
- fold_motion=synchronized 但两 half 关节没写 mimic → 两 half 不联动
- 忘写 `chassis_to_half_i` MatingContract → hinge_beam 与 playing_panel 之间会 mating-gap FAIL
- caster_count 加了 leg/upright 数量 → multiplicity 溢出到不 sampled 结构
- palette_style 只影响一个 material，其他 material 硬编码 → 不满足 §7.5 palette 驱动全材质要求
- fold_upper 全程不限 → half 翻过头穿 chassis
- 未 element-scoped allow_overlap 而用 broad `allow_overlap(chassis, caster_i)` → 属 authoring smell

## 与相邻类别的边界

- 不该混入：**folding_table / 折叠餐桌**（无中央网 + 无 blue 竞技面 + 无 center hinge_beam vs seam）
- 不该混入：**pool_table / billiards_table**（cushion 边框 + pocket 洞、非可折叠）
- 不该混入：**picnic_table / bench**（无网 + 无 fold）
- 不该混入：**004 compact-folding suitcase**（root 换成 west_top，无 chassis + 无 net + 独立 form family）—— 初版模板不采样 004 形态，仅采样 001/002/003 中央 chassis 形态

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审：(1) `synchronized ∧ portable_trolley` 降级 gate（可否另选 upgrade 到 commercial）;(2) 004 compact-folding 独立 root 形态是否值得单开 slug（当前排除）;(3) caster_count multiplicity 权重 (0.45/0.35/0.20) 是否需要 tune;(4) top_topology 仅 2 candidate 是否满足 §8.5 ③ ≥3 门（因 chassis_form 已是 ③ slot，top_topology 主要承 ④ 装饰分区，2 足够） |

## 模板实现备注（可选）

- 共享 helper：`_add_caster(part, palette, r)` 生成 wheel_tire + wheel_hub Cylinder；`_add_half_visuals(part, side, top_module, r, palette)` 分派到 rigid_one_piece 或 four_panel 分支；`_add_chassis_visuals(chassis, chassis_form, r, palette)` 分派到三 chassis form。
- 关键 InterfaceSpec：hinge_beam 为共享几何量—必须由 `_hinge_beam_x/y/z()` helper 单点定义（Contract 3c）。
- captured-pin overlap：sync_shaft in sync_bearing_block、caster_socket in wheel_hub 必须 element-scoped `allow_overlap`。
- palette_style 驱动全部 materials（4 组 rgba dict）；`resolve_config` 拉出后 build_* 内一律用 named materials。
- 若 sweep 出现 top_topology=four_panel + fold_motion=synchronized 共出的 mating-gap，则在 `four_panel` half 的 `playing_panel` -z face 精确对齐 hinge_beam +z face。
