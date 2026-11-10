# Pipeline Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pipeline` |
| template path | `agent/templates/Equipment_Pipeline.py` |
| test path | `tests/agent/test_pipeline_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：body/operator/port 三个结构命名 slot 串成竖直阀门塔（body 为固定根体，operator 铰接在 rising-stem 顶面，port 寄生在管-阀耦合面），再叠加一根 `outlet_count` multiplicity 轴在 body 上复制「出口总成（nozzle + cap + retaining chain）」。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13 |
| read_count | 13 |
| read_scope | 3 个 parent picture 记录 + 10 个 fork 变体（本 picture 子类候选池全部读取：`record.json` / 活动 `revision.json` / `prompt.txt` / `model.py` 全部扫过） |
| samples_adopted_as_module_sources | 13 |
| samples_read_but_not_adopted | 0 |
| source_index_policy | only adopted module sources are indexed below |

- **数据集根 caveat**：这些来源是 workbench-only 的 picture 子类 fork 记录，其 dataset 根是 **articraft_data** 仓库（`collections=['workbench']`，**不是** arti-template 已 promote 的 10K dataset）。`five_star_total` / `read_count` = source map 给出的 parent + variant 池（3 parents + 10 variants = 13），不代表全局 5 星统计。来源一律以标准相对路径 `data/records/<id>/revisions/rev_000001/model.py:Lx-Ly` 引用（相对 articraft_data 仓库根）。
- parents（3）：`rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180104_185804_d58aec8c`（黄色 gas line：90° 肘弯 + inline gate valve，bolted flange pair，3 辐手轮）、`rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180106_931724_6c9b7c6f`（fire-hydrant standpipe：立管 + 鼓形体，6 辐轮，**双出口 nozzle + lift cap + chain**，N=2 手写、未循环）、`rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180109_734374_b30771ae`（蓝色 flanged globe valve：球体，bolted RF flange，6 辐手轮）。
- variants（10，均 fork 自上述 parent）：`rec_pipeline_var_body_straightgate`、`rec_pipeline_var_body_anglevalve`、`rec_pipeline_var_operator_3spoke_globe`、`rec_pipeline_var_operator_5spoke`、`rec_pipeline_var_operator_lever`、`rec_pipeline_var_operator_teebar`、`rec_pipeline_var_port_socketweld`、`rec_pipeline_var_port_unionnut`、`rec_pipeline_var_outlet_1`、`rec_pipeline_var_outlet_3`。

## 核心身份

Pipeline 是工业管路阀门段：一只固定的管/阀**主壳体（body_form）**承载流道（直管 / 肘弯 / 球形阀体 / 鼓形立管阀体），顶部经 bonnet/yoke + rising stem 伸出一只可被铰接的**操作件（operator）**（手轮 / 扳手 / 十字把手），两端或多端通过**端口（port）**（螺栓法兰 / 承插焊套筒 / 活接螺母）与相邻管段耦合。主活动机构是 operator 绕竖直 stem 轴的转动（手轮/tee = CONTINUOUS，扳手 = 受限 REVOLUTE）；可选次活动机构是 hydrant/standpipe 血统的侧向出口盖板（PRISMATIC 拉出）+ retaining chain（serial REVOLUTE link chain）。

默认成熟域：单阀体 + 单操作件 + 法兰/承插/活接端口；standpipe 血统额外带 0..N 个出口总成。

边界：
- 不混入仪表/旋钮类（把手轮换成纯旋钮/拨盘会读成仪表而非阀门）。
- 不混入 pump/compressor（无叶轮、无驱动电机）。
- body 必须保留可铰接 operator；去掉 operator 的纯直管不属于本类。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180104_185804_d58aec8c` | `data/records/rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180104_185804_d58aec8c/revisions/rev_000001/model.py:L88-L184` | inline gate elbow body + bolted flange pair + 3 辐手轮 |
| S2 | `rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180106_931724_6c9b7c6f` | `data/records/rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180106_931724_6c9b7c6f/revisions/rev_000001/model.py:L162-L225` | standpipe riser body + 6 辐手轮 + N=2 手写出口（非循环源） |
| S3 | `rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180109_734374_b30771ae` | `data/records/rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180109_734374_b30771ae/revisions/rev_000001/model.py:L107-L203` | globe sphere body + bolted RF flange + 6 辐手轮 |
| S4 | `rec_pipeline_var_body_straightgate` | `data/records/rec_pipeline_var_body_straightgate/revisions/rev_000001/model.py:L87-L162` | straight-through gate body（去肘弯） |
| S5 | `rec_pipeline_var_body_anglevalve` | `data/records/rec_pipeline_var_body_anglevalve/revisions/rev_000001/model.py:L92-L233` | 90° 角阀 body（互相垂直进出口） |
| S6 | `rec_pipeline_var_operator_3spoke_globe` | `data/records/rec_pipeline_var_operator_3spoke_globe/revisions/rev_000001/model.py:L266-L361` | globe 血统 3 辐手轮（spoke 数轴值） |
| S7 | `rec_pipeline_var_operator_5spoke` | `data/records/rec_pipeline_var_operator_5spoke/revisions/rev_000001/model.py:L266-L361` | 5 辐手轮 |
| S8 | `rec_pipeline_var_operator_lever` | `data/records/rec_pipeline_var_operator_lever/revisions/rev_000001/model.py:L266-L371` | quarter-turn 直杆扳手（REVOLUTE 限位）+ 固定 stem |
| S9 | `rec_pipeline_var_operator_teebar` | `data/records/rec_pipeline_var_operator_teebar/revisions/rev_000001/model.py:L220-L313` | 十字 tee-bar 把手 |
| S10 | `rec_pipeline_var_port_socketweld` | `data/records/rec_pipeline_var_port_socketweld/revisions/rev_000001/model.py:L140-L176` | 承插焊/推入式套筒端口（无盘无螺栓） |
| S11 | `rec_pipeline_var_port_unionnut` | `data/records/rec_pipeline_var_port_unionnut/revisions/rev_000001/model.py:L180-L253` | 活接六角螺母联管节端口 |
| S12 | `rec_pipeline_var_outlet_1` | `data/records/rec_pipeline_var_outlet_1/revisions/rev_000001/model.py:L472-L554` | N=1 出口总成 `for i in range(OUTLET_COUNT)` 循环（copy-logic 源） |
| S13 | `rec_pipeline_var_outlet_3` | `data/records/rec_pipeline_var_outlet_3/revisions/rev_000001/model.py:L164-L185, L494-L559` | N=3 等分径向出口 `_outlet_angle` / `_outlet_local_to_body` 范式（任意 N copy-logic 源） |

## 槽位 + 候选模块表

### Slot A：body_form（主壳体——被铰接 operator 与端口寄生的固定根体）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `inline_gate_elbow` | `rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180104_185804_d58aec8c` | L88-L184 | eligible if compatible | `_pipeline_run`（垂直腿 + `_quarter_torus` 弯头 + 水平段，annular extrude 空心）+ `_valve_body`（中段加粗 barrel）；黄色直管带 90° 下弯肘，中央内联闸阀体 |
| `globe_sphere` | `rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180109_734374_b30771ae` | L107-L203 | eligible if compatible | `_make_body_mesh`：`sphere(BODY_R)` 球体 + `port(sign)` loft 颈 + 沿 X bore 通孔；球形铸铁阀体，两侧端口颈穿过球心 |
| `standpipe_riser` | `rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180106_931724_6c9b7c6f` | L162-L225 | eligible if compatible | `_riser_shape`（高立管）+ `_collar_shape` + `_body_shape`（revolve 鼓形体）+ `_bonnet_neck_shape` + `_dome_stem_shape`；竖立高立管 + 鼓形铸铁阀体，可挂侧向出口 |
| `straight_through_gate` | `rec_pipeline_var_body_straightgate` | L87-L162 | eligible if compatible | `_pipeline_run`（改写为直进口段，**去除弯头**）+ `_valve_body`（直通 full-bore barrel）；纯水平直通闸阀，无肘弯 |
| `angle_valve_90` | `rec_pipeline_var_body_anglevalve` | L92-L233 | eligible if compatible | `_angle_quarter_torus` + `_pipeline_run`（L 形路径）+ `_inlet_flange_pair`/`_outlet_flange_pair`（互相垂直端口）+ `_valve_body`（拐角铸件）；90° 角阀，进口竖直、出口转向 |

### Slot B：operator（被铰接的执行控制件）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `handwheel_3spoke` | `rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180104_185804_d58aec8c` | L220-L253（mesh）/ L306-L314（joint） | eligible if compatible | `_handwheel`：rim torus + hub + `for i in range(N_SPOKES)` N_SPOKES=3；joint `valve_handwheel` CONTINUOUS +Z |
| `handwheel_6spoke` | `rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180109_734374_b30771ae` | L266-L328（mesh）/ L353-L361（joint） | eligible if compatible | `_make_handwheel_mesh`：N_SPOKES=6 rim+hub+spoke；joint `body_to_handwheel` CONTINUOUS +Z（standpipe 血统 `_wheel_shape` L394-L428 / `body_to_wheel` L497-L505 为同构副本） |
| `handwheel_3spoke_globe` | `rec_pipeline_var_operator_3spoke_globe` | L266-L328（mesh）/ L353-L361（joint） | eligible if compatible | `_make_handwheel_mesh` N_SPOKES=3（globe 血统上的 spoke 数轴值）；joint `body_to_handwheel` |
| `handwheel_5spoke` | `rec_pipeline_var_operator_5spoke` | L266-L328（mesh）/ L353-L361（joint） | eligible if compatible | `_make_handwheel_mesh` N_SPOKES=5；joint `body_to_handwheel` |
| `quarter_turn_lever` | `rec_pipeline_var_operator_lever` | L307-L340（lever mesh）/ L266-L304（fixed_stem）/ L363-L371（joint） | eligible if compatible | `_make_lever_mesh`：hub + 单根 bar + end_knob，`_make_stem_mesh` 固定 `fixed_stem`；joint `body_to_lever` **REVOLUTE** +Z，limits [0, π/2]；四分之一转直杆扳手 |
| `crossed_tee_bar` | `rec_pipeline_var_operator_teebar` | L220-L245（hub/bar mesh）/ L294-L299（visuals）/ L305-L313（joint） | eligible if compatible | `_handle_hub` + `_handle_bar(index)`（`for i in range(2)` 互转 90°）；十字 tee-bar 把手；joint `valve_handle` CONTINUOUS +Z |

### Slot C：port（管端/管-阀联接形式）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `bolted_flange_pair` | `rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180104_185804_d58aec8c` | L143-L176（flange/pair）/ L279-L283（visual） | eligible if compatible | `_flange`：raised face + `for i in range(N_BOLTS)` N_BOLTS=12 六角螺栓环；`_flange_pair` 4 盘（进/出口各一对）；面对面对夹 |
| `bolted_RF_flange` | `rec_build-a-realistic-articulated-3d-model-of-a-pipe_20260609_180109_734374_b30771ae` | L144-L163（disc+rf）/ L251-L263（bolts）/ L98-L104（`_bolt_ring`） | eligible if compatible | `_make_body_mesh.port()`：loft 颈 + `circle(FLANGE_R)` 盘 + 凸面 rf；`_make_bolts_mesh` `_bolt_ring` N_BOLTS=8 螺栓环 |
| `socket_weld` | `rec_pipeline_var_port_socketweld` | L140-L176 | eligible if compatible | `_socket_collar`（光滑环形 bell 套筒，**无盘、无螺栓**）+ `_socket_joint_centers`；平口承插焊/推入式套筒接头 |
| `union_nut` | `rec_pipeline_var_port_unionnut` | L180-L253 | eligible if compatible | `_make_union_coupling_mesh`：`_x_hex_prism` 六角螺母 + `_x_cylinder` 两侧 shoulder 环；活接（union）六角螺母联管节 |

硬约束满足说明：
- Slot A=5、Slot B=6、Slot C=4，全部 ≥3，无单候选 slot。
- 每个 candidate 均有真实 `model.py:Lx-Ly` 来源（见上）。
- candidate 之间结构差异：A 区分直管/肘弯/球体/立管/角阀流道拓扑；B 区分 rim-wheel（CONTINUOUS）vs 直杆扳手（REVOLUTE 限位）vs 十字双杆把手；C 区分带螺栓盘/凸面盘/光滑套筒/六角活接四种耦合几何。spoke 数 {3,5,6} 视作 operator 的**子轴**（见参数表 `spoke_count`），而非三个独立 module——`handwheel_3spoke` / `handwheel_3spoke_globe` 是同一 rim-wheel module 在不同血统上的 spoke 取值，compatibility matrix 去重，不重复造。

## 槽位图（slot graph）

pattern: `mixed`

```text
[Slot A body_form]  --operator_spin  (CONTINUOUS handwheel/tee | REVOLUTE 限位 lever),  joint origin = rising-stem 顶面圆,  axis=+Z--> [Slot B operator]
[Slot A body_form]  --port_mate  (FIXED, mating face = 管-阀耦合 plane 处 PIPE_OR 环面, 沿 ±X 端口轴对夹)--> [Slot C port]   (端口寄生在 body 上, 每端一个)
[Slot A body_form (standpipe 血统)]  --outlet_pull (PRISMATIC, 沿出口局部径向轴)--> [outlet_i: cap_i]  --chain_swing (serial REVOLUTE link chain)--> [chain_i_j]
```

接口点位与跨 slot joint policy：
- **operator ↔ body**：所有手轮/扳手/tee 把手的 hub 局部 z=0 落在 rising stem 顶面；joint origin 贴 stem 顶面（gate 血统 elem `valve_stem`，x=X_VALVE_CENTER；globe 血统 `fixed_stem`/`dome_stem`，x=y=0），axis=+Z。mating face = stem 顶面圆，anchor = stem 轴心。手轮/tee 用 CONTINUOUS（无限位），lever 用 REVOLUTE（limits [0, π/2]）。互斥：每个 body 仅一个 operator。
- **port ↔ body**：法兰/承插/活接套筒包在管-阀耦合处的 joint plane（gate 血统 `_flange_pair` 的 x_in/x_out、`_socket_joint_centers`；globe 血统 `port(sign)` 颈端），mating face = 该平面处 PIPE_OR/BORE 环面，沿 ±X 端口轴对夹。port 为 body 的固定 visual（不独立铰接），但接口须落到真实耦合面。
- **outlet ↔ body**：nozzle root 嵌入鼓形体壁内（NOZZLE_ROOT_X，被 body 捕获）；cap 的 PRISMATIC 原点在 nozzle tip；链根 pin 在 cap 的 boss（`CHAIN_BOSS_LOCAL`，随 cap 走），链尾 link 缠绕 body 肩部 `chain_lug_{i}`（`CHAIN_LUG`）。
- **可选/派生**：outlet 轴主要由 `standpipe_riser` body 派生（鼓形体可挂侧向出口）；其余 body（inline/globe/straight/angle）默认 `outlet_count=0`。

## 每槽位 Module Emits / Interfaces

### Slot A / body_form（各 module）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 固定根 part：gate 血统 `pipeline_body`（`pipe_yellow`/`valve_body`/`flanges`/`bonnet`/`valve_stem` visuals），globe 血统 `valve_body`（`body_shell`/`bonnet_yoke`/`bonnet_bolts`），standpipe 血统 `standpipe_body`（`riser_pipe`/`body_collar`/`valve_body`/`bonnet_neck`/`dome_stem` + nozzle/lug visuals） | S1 L259-293 / S3 L340-343 / S2 L441-487 |
| internal joints | 无（body 是根，不含内部 joint） | — |
| upstream interface | parent policy：body 为世界根，foot 落地（standpipe riser 脚 z=0；inline/globe/angle 经支撑面/底坐） | S1-S5 |
| downstream interface | rising-stem 顶面圆（供 operator）、±X 管-阀耦合面（供 port）、鼓形体壁 NOZZLE_ROOT（供 outlet） | S1 L209-217 / S3 L126-165 / S2 L228-256 |

### Slot B / operator（各 module）
| emits | 描述 | 来源 |
|---|---|---|
| parts | rim-wheel：`handwheel` part（hub+rim+spokes）；lever：`lever_handle` part（`lever_bar` visual）+ body 侧 `fixed_stem` visual；tee：`cross_handle` part（`handle_hub`+`handle_bar_0/1`） | S6-S9 |
| internal joints | 无 operator 内部 joint（spoke/bar 为同一 part 的 visual loop） | S1 L240-252 / S9 L294-299 |
| upstream interface | hub 局部 z=0 = rising-stem 顶面（joint origin），axis=+Z | S3 L275 / S8 L362 |
| downstream interface | 无（operator 是叶子；captured-stem 过盈用 `allow_overlap`） | S1 L412-418 / S2 L819-826 |

### Slot C / port（各 module）
| emits | 描述 | 来源 |
|---|---|---|
| parts | port 为 body 的固定 visual：`flanges`（螺栓盘）/ `bonnet_bolts`+RF 盘 / `socket_collar_0/1`（套筒）/ `union_nut_0/1`（六角活接） | S10/S11 |
| internal joints | 无（端口固定，不铰接） | — |
| upstream interface | 管-阀耦合 plane 处 PIPE_OR/BORE 环面，沿端口轴对夹 | S10 L170-176 |
| downstream interface | 朝向相邻管段的对夹面（mating contract：可见对夹支撑路径） | S10/S11 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_form` | enum | `inline_gate_elbow` / `globe_sphere` / `standpipe_riser` / `straight_through_gate` / `angle_valve_90` | `inline_gate_elbow` | choice | 由 deterministic procedural sampler 选择 | Slot A 表 |
| `operator` | enum | `handwheel_wheel` / `quarter_turn_lever` / `crossed_tee_bar` | `handwheel_wheel` | choice | sampler 选择；wheel 与 spoke_count 子轴解耦 | Slot B 表 |
| `spoke_count` | enum/int | {3, 5, 6} | 6 | conditional | 仅当 `operator==handwheel_wheel` 有效；其它 operator 忽略 | S6/S7/S2/S3 |
| `port_type` | enum | `bolted_flange_pair` / `bolted_RF_flange` / `socket_weld` / `union_nut` | `bolted_flange_pair` | choice | sampler 选择；跨血统组合见排除项 | Slot C 表 |
| `outlet_count` | int | `[0, 6]`（规划轴 N∈{0,1,2,3} 有样本） | 0 | conditional | 见 Multiplicity；N>0 主要 gating 到 `standpipe_riser` body | S12/S13/S2 |
| `bolt_count` | int | flange `[8, 12]`，活接固定 | 12（gate）/ 8（RF） | independent | 端口螺栓环 visual 密度，`for i in range(N_BOLTS)` | S1 L150 / S3 L101 |
| `body_scale` | float | [0.85, 1.20] | 1.0 | independent | body 主尺度，clamp；不破坏接口 | S1-S5 |
| `stem_len_scale` | float | [0.85, 1.15] | 1.0 | equation | `= f(body_scale)` 锁定 stem 顶面高度与 operator joint origin 一致 | S1 L211 / S3 L74 |
| `operator_radius_scale` | float | [0.85, 1.15] | 1.0 | independent | 手轮/扳手半径，clamp | S1 L66 / S8 L78 |
| (—) | constraint | — | — | inequality | `operator_radius·scale ≤ stem_top_clearance`；手轮不得与 body/bonnet 穿模，违反按比例回缩 | 接口 / clearance |
| (—) | constraint | — | — | conditional | `outlet_count > 0 ⇒ body_form ∈ {standpipe_riser}`（其它 body 默认 0）；出口径向间距 `2π/N` 须 ≥ 最小角间隙否则 clamp N | Multiplicity gating |

连续尺寸采样契约：先采 independent（`body_scale`、`operator_radius_scale`、`bolt_count`），再按 equation 派生 `stem_len_scale`，再用 inequality 把 operator 半径投影/回缩到 clearance 可行域，最后按上游 enum 解析 `spoke_count` / `outlet_count` 的 conditional 范围。

## Multiplicity / Copy Logic

本 spec 有 **1 根 multiplicity 轴**：`outlet_count`（standpipe/hydrant 血统的侧向出口总成复制）。

- `count_param`：`OUTLET_COUNT`（`rec_pipeline_var_outlet_1`，L83）/ `OUTLET_N`（`rec_pipeline_var_outlet_3`，L82）。模板统一暴露为 `outlet_count`。
- `N_range`：**[0, 6]**（规划轴；样本覆盖 N∈{0,1,2,3}。N=0 = 无出口的纯立管/直管，N=2 = parent 对侧双出口）。
- sampling domain（权重档）：小 N 高频（N∈{0,1,2} 偏多），大 N（4..6）稀有长尾；采样域大于样本属正常。
- copied object：一整套出口总成 = nozzle visual `nozzle_{i}`（`_nozzle_shape`）+ 锚耳 `chain_lug_{i}`（`_chain_lug_shape`）+ part `cap_{i}`（`_cap_shape`）+ 一条 retaining 链 `chain_{i}`（`_add_subchain`，链节 part `chain_{i}_{j}`）。
- naming：`nozzle_{i}` / `chain_lug_{i}` / `cap_{i}`；cap 滑动关节 `body_to_cap_{i}`；链节关节 `chain_{i}_swing_{j}`；统一 `for i in range(outlet_count)` 发射。
- placement：N=1 沿 +X 单出口（`direction`，S12 L472-486）；N=3 由 `_outlet_angle(i)=2π·i/OUTLET_N`（S13 L164-166）绕 +Z 等分、`_outlet_local_to_body(angle, local)`（S13 L177-185）做径向放置；parent N=2 为对侧 ±X。
- joint policy：每个 cap 独立 PRISMATIC，沿其出口局部径向轴（N=1 为 +X；N≥3 经 `rpy=(0,0,angle)` 旋到各自方向，S13 L539-547），lower=-CAP_DEFAULT_PULL、upper=0.020；每个链节独立 REVOLUTE，limits ±35°（CHAIN_SWING），互不联动（S12/S13 `_add_subchain`）。
- source/gating：**copy-logic 源码蓝本 = `rec_pipeline_var_outlet_1`（S12 L472-554）+ `rec_pipeline_var_outlet_3`（S13 L494-559 的 `for i in range(N)` + `cap_{i}` 循环链；`_outlet_angle`/`_outlet_local_to_body` 为任意 N 的径向放置范式）**。**parent `6c9b7c6f` 的 N=2 是手写 `right_cap`/`left_cap`（`body_to_right_cap`/`body_to_left_cap`，S2 L523-540），未循环化，不可直接作 copy-logic 源**，仅作 N=2 拓扑样本与 hydrant body/operator 来源。`outlet_count` 主要 gating 到 `standpipe_riser` body（鼓形体可承捕 nozzle root）；其它 body 默认 N=0。

## 拓扑多样性审计

总组合数：`A(5) × B(3 operator family) × C(4) = 60`（结构 slot 基本组合；spoke_count 子轴 ×3 仅在 handwheel family 内，叠加后远超）。再叠加 `outlet_count` 轴（N∈{0,1,2,3} 规划格子已收敛，N_range 到 6）：standpipe 血统 ≥ 4 个 N 拓扑 → **总拓扑组合 ≫ 60**。

理由：operator family 单独就给 CONTINUOUS-wheel / REVOLUTE-限位-lever / CONTINUOUS-tee 三种铰接拓扑；port 给四种耦合 visual 拓扑；body 给 5 种流道拓扑；outlet 轴给 0..N 的可变子件计数拓扑。任一双 slot 组合即已 >10 distinct。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊。Sampling 先选 body_form（上游结构），再从 compatible 集合选 operator（含 spoke_count 子轴）与 port，再对 `outlet_count` 轴按 body 兼容性做加权采样、各自 clamp、各自编进 `slot_choices`。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类受 outlet 轴 + 4 slot enum 组合驱动，预计可达。

Procedural Sampling / Sweep Plan：compatibility matrix / gating 以「槽位图」「每槽位 Module Emits / Interfaces」「Validator」定义的接口、joint 轴、对夹面、range 和互斥关系为准；不兼容组合（如 globe_sphere × socket_weld/union_nut 的跨血统耦合参数不共享）在 sampler 或 `resolve_config` 中降级/重采样/拒绝，不让 builder 后期失败。

Controlled local parameterization：初版模板应含 `body_scale`、`stem_len_scale`（=f(body_scale)）、`operator_radius_scale`、`bolt_count`、（standpipe 血统）`station_spacing`=出口角间距。取值范围/clamp 见参数表；按第 7 节 `约束类型` 声明依赖（先采 independent → 派生 equation → 投影/回缩 inequality → 解析 conditional），跨部件依赖（operator 半径 ↔ stem clearance、outlet 角间距 ↔ N）显式声明，不当作互相独立自由变量各抽各的，且不破坏 InterfaceSpec / MatingContract / outlet multiplicity。

Regression overrides：默认无。若未来 sweep 发现稳定失败组合或 reviewer 指定回归样本，再加少量显式 regression seed，写明 seed/组合/原因；不得用小型 curated / modulo 表作主 seed domain。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body → operator(+spoke_count) → port → outlet_count，加权选择，compatibility gates | slot_choices_for_seed matches build choices |
| compatibility matrix | outlet_count>0 仅 standpipe；跨血统 body×port（globe×socket/union）留待几何重派生前 fallback；每 body 仅一 operator | no floating, collision, axis, max multiplicity, bulky module, optional child failures |
| controlled local variation | body_scale / stem_len_scale(derived) / operator_radius_scale / bolt_count / outlet 角间距 + clamp | proportions vary without breaking interfaces, clearance, joint origin, identity |
| regression overrides | none | previously failed or reviewer-selected only |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | and contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_form | 5 | yes | yes | 流道拓扑各异 |
| B operator | 6 | yes | yes | 含 spoke_count {3,5,6} 子轴；按铰接拓扑分 3 family |
| C port | 4 | yes | yes | 螺栓盘/RF 盘/套筒/活接 |
| (axis) outlet_count | N∈{0,1,2,3}, range[0,6] | yes | yes | multiplicity 轴 |

## Validator
- slot_choices_for_seed returns implemented module names
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating prevents illegal module combinations（outlet_count>0 非 standpipe、跨血统 body×port 不共参数、双 operator）
- optional regression overrides are sparse and justified
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params（body_scale / stem_len_scale / operator_radius_scale / outlet 角间距）clamped 且不破坏接口、clearance、joint origin、multiplicity
- cross-part scale dependencies（stem_len=f(body_scale) equation；operator 半径 ↔ clearance inequality；outlet 角间距 ↔ N conditional）resolved in `resolve_config`
- 关键 InterfaceSpec / MatingContract 存在：rising-stem 顶面圆（operator）、±X 管-阀耦合面（port）、nozzle root 捕获 + cap-on-tip（outlet）
- 关键 joint type/axis/range：operator handwheel/tee = CONTINUOUS +Z；lever = REVOLUTE +Z limits[0,π/2]；cap = PRISMATIC 沿出口径向轴；chain link = REVOLUTE ±35°
- copied objects（`nozzle_{i}`/`chain_lug_{i}`/`cap_{i}`/`chain_{i}_{j}`）follow naming and placement policy（径向等分 `2π/N`）

## Reject cases
- body 去掉 operator（失去铰接，出类目）或把手轮换成纯旋钮/拨盘（读作仪表）。
- operator joint 轴非竖直，或 lever 缺 [0,π/2] 限位被当成无限旋转。
- operator hub 悬空、不落在 rising-stem 顶面（joint origin 漂浮）。
- port 端口悬空或用不可见接口盘连接，对夹面无支撑路径。
- outlet cap 做成未连接独立 FIXED child，或 cap 竖直抬起而非沿出口径向轴 PRISMATIC 拉出。
- retaining chain 断在中间（链节非 serial interlink）或链尾不缠绕 `chain_lug` body 锚耳。
- outlet_count>0 却挂在非 standpipe body 上导致 nozzle root 不被壁体捕获 / 出口穿模。
- 跨血统 body×port 直接复用不共享参数的 helper（globe loft 颈 × 直管 PIPE_OR 套筒）导致几何错位。

## 与相邻类别的边界
- 仪表/调节旋钮（pressure gauge / dial）：本类必须有可铰接阀门 operator + 流道 body，不是表盘。
- pump / compressor：本类无叶轮、无驱动电机，operator 是人工手轮/扳手而非动力轴。
- generic gear_train / pulley：本类必须有管-阀流道与端口耦合语义，不是纯传动件。

## 模板实现备注（可选）
- 共享 helper：`_bolt_ring`（flange 螺栓环）、`_add_subchain`/`_oval_chain_link_mesh`（retaining chain）、`_outlet_angle`/`_outlet_local_to_body`（任意 N 径向放置）可在 module 间复用。
- captured-pin overlap 需 element-scoped `allow_overlap`：operator hub ↔ rising stem（nested shaft fit）、cap recess ↔ nozzle tip（seated fit）、consecutive chain links（intentional interlink）。
- 暂不进入 seed domain 的组合：`globe_sphere` × `socket_weld`/`union_nut`（`_socket_collar` 以 PIPE_OR 为基、`_make_union_coupling_mesh` 以 globe PORT_HALF_SPAN 为基，跨血统不共参数）——留待模板矩阵时按当时几何重派生，先用 fallback 降级到同血统 flange 端口。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；workbench-only picture 子类 fork 来源（dataset 根 = articraft_data，非 promoted 10K）；等待人工审核 |
