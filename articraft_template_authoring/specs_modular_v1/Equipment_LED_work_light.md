# LED Work Light Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `led_work_light` |
| template path | `agent/templates/Equipment_LED_work_light.py` |
| test path | `tests/agent/test_led_work_light_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 (parent + 9 forks) |
| read_count | 10 |
| read_scope | parent `f7e038e0` + 全部 9 个 workbench fork（mount/head/panel/led_count 各轴），逐个读 `model.py` |
| samples_adopted_as_module_sources | 10（全部采纳：4 mount × 3 head × 3 panel 的去重模块 + 3 led_count 计数样本，parent 同时贡献 3 个槽的基线） |
| source_index_policy | only adopted module sources are indexed below |

**Dataset-root caveat（重要）**：本类不是常规 5 星生产类别，而是 picture-subcat fork 家族。所有样本是 workbench-only 的 picture 子类 fork，根植于 `articraft_data` 仓库（`collections=['workbench']`，未 promote）。因此引用一律写 `data/records/<id>/revisions/rev_000001/model.py:Lx-Ly`，而非常规数据集路径。

- parent（fork 基线，copy-logic 源）：`rec_build-a-realistic-articulated-3d-model-of-a-led-_20260609_180048_908359_f7e038e0`
- 全部 9 个 fork 均 forked from 上述 parent，分别填 mount / head / panel 三个结构槽和 led_count 一个 multiplicity 轴：
  - mount：`rec_led_work_light_var_mount_aframe`、`rec_led_work_light_var_mount_tripod`、`rec_led_work_light_var_mount_hook`
  - head：`rec_led_work_light_var_head_tiltpan`、`rec_led_work_light_var_head_telescope`
  - panel：`rec_led_work_light_var_panel_cob_round`、`rec_led_work_light_var_panel_dual`
  - led_count：`rec_led_work_light_var_leds_sparse`、`rec_led_work_light_var_leds_dense`
- **head 变体专门说明**：`tilt_pan` 与 `telescope` 都把头部俯仰铰从 root 直挂 (`stand_to_head`) **改挂到一个中间 part**（`u_yoke` / `inner_mast`），即头铰的 parent 是可被 head 槽改写的接口端。`tilt_pan` 同时**移除头部 `battery_pack` 与 `battery_port_panel`**（让出 U-yoke 中空，避免支撑穿过后壳，见 `rec_led_work_light_var_head_tiltpan/.../model.py:442-443` 显式断言电池被移除）；`telescope` 保留电池盒（`...var_head_telescope/.../model.py:371-383`）。模板须把"电池后部 furniture 是否随 head 槽重新安置"作为兼容性矩阵的一项。

## 核心身份

LED work light 是便携可充电 LED 泛光/工作灯：一个静态承托机构（mount）把一只矩形/圆形泛光头举离地面，泛光头围绕一条水平左右轴（Y）做俯仰（REVOLUTE），头面是玻璃漫射板 + 黑边框 + LED 阵列，常带黄色电池盒与 U 形提手。主机构永远是 head 俯仰；mount 与 head 槽可再叠加折叠腿（REVOLUTE）、挂钩（REVOLUTE）、pan 转盘（REVOLUTE-Z）或升降 mast（PRISMATIC-Z）。

成熟域：工地/作业泛光灯（jobsite flood）。颜色基线为安全黄管架 + 黑头，但身份由"水平俯仰泛光头 + 离地承托"决定，不由配色决定。

边界（详见末节）：
- 不是 `articulated_task_lamp`（多节臂台灯）：本类是单/双段承托 + 泛光头，不是平行四连杆/多关节悬臂灯。
- 不是 handheld flashlight / spotlight：必须有离地承托语义与 REVOLUTE 俯仰头。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S0 | parent `…_f7e038e0` | `data/records/rec_build-a-realistic-articulated-3d-model-of-a-led-_20260609_180048_908359_f7e038e0/revisions/rev_000001/model.py:L61-L346` | H-frame mount 基线 + side_tilt head 基线 + rect_flood panel 基线 + `led_{r}_{c}` 双层循环 copy-logic 源 |
| S1 | `rec_led_work_light_var_mount_aframe` | `…var_mount_aframe/revisions/rev_000001/model.py:L77-L219` | folding A-frame mount + 两条折叠腿 REVOLUTE |
| S2 | `rec_led_work_light_var_mount_tripod` | `…var_mount_tripod/revisions/rev_000001/model.py:L79-L158` | tripod hub + 三放射腿（range(3) 循环）+ 中央 mast yoke |
| S3 | `rec_led_work_light_var_mount_hook` | `…var_mount_hook/revisions/rev_000001/model.py:L93-L204` | 紧凑手持模塑底 pod + 折叠挂钩 REVOLUTE |
| S4 | `rec_led_work_light_var_head_tiltpan` | `…var_head_tiltpan/revisions/rev_000001/model.py:L135-L220` | vertical_post + u_yoke（pan REVOLUTE-Z → tilt REVOLUTE-Y 串联，移除电池） |
| S5 | `rec_led_work_light_var_head_telescope` | `…var_head_telescope/revisions/rev_000001/model.py:L151-L240` | 固定外套筒 + inner_mast（lift PRISMATIC-Z → tilt REVOLUTE-Y 串联） |
| S6 | `rec_led_work_light_var_panel_cob_round` | `…var_panel_cob_round/revisions/rev_000001/model.py:L177-L254` | lathe 圆形 COB 头壳 + 圆玻璃 + 同心环 LED |
| S7 | `rec_led_work_light_var_panel_dual` | `…var_panel_dual/revisions/rev_000001/model.py:L68-L321` | `_emit_flood_housing` helper + 共享 crossbar 上并排双泛光壳 |
| S8 | `rec_led_work_light_var_leds_sparse` | `…var_leds_sparse/revisions/rev_000001/model.py:L249-L264` | led_count 计数样本 N=15（3×5） |
| S9 | `rec_led_work_light_var_leds_dense` | `…var_leds_dense/revisions/rev_000001/model.py:L249-L264` | led_count 计数样本 N=88（8×11） |

## 槽位 + 候选模块表

### Slot A：mount（底座/承托机构槽——决定 head 如何离地与被托起）
| module_name | record_id | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `h_frame_stand`（基线） | parent `…_f7e038e0` | `model.py:L75-L154` | eligible if compatible | 黄色管式 H 底（`side_rail_*`/`base_cross_member`/`foot_fr/br/fl/bl`）+ 两根外张立柱 `upright_pos_y/neg_y` 夹住头侧 boss + `pivot_knob_*`；无附加 joint |
| `folding_aframe` | `rec_led_work_light_var_mount_aframe` | `model.py:L77-L219` | eligible if compatible | apex 桥架 `apex_crossbar` + `leg_pin_0/1` + `pivot_yoke_*`/`yoke_gusset_*`；两个 child part `folding_leg_0/1`（`hinge_barrel`/`side_strut_*`/`foot_bar`/`rubber_foot_*`），各加一条 `stand_to_leg_i` REVOLUTE-Y（折叠，L210-L219） |
| `tripod_mast` | `rec_led_work_light_var_mount_tripod` | `model.py:L79-L158` | eligible if compatible | `hub_collar` + 三条等角放射腿（`for i in range(3)` L91-L114）+ 中央 `mast`/`mast_top_collar` + `pivot_yoke_0/1` + 贯穿 `pivot_axle`；无附加 joint |
| `handheld_hook` | `rec_led_work_light_var_mount_hook` | `model.py:L93-L204` | eligible if compatible | `_rounded_box` 模塑手持底 `handheld_base`（`base_shell`/`top_saddle`/`control_panel`/`rear_stand_foot`/`hook_lug_*`/`yoke_arm_*`/`yoke_socket_*`）+ child `hanging_hook`（`hook_hinge_barrel`/`folding_hook`），加 `base_to_hook` REVOLUTE-Y（L382-L390） |

### Slot B：head（头部承托链/铰接形态槽——决定头有几个自由度，及头铰挂在哪个 parent）
| module_name | record_id | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `side_tilt`（基线） | parent `…_f7e038e0` | `model.py:L266-L344`（head boss + 单铰） | eligible if compatible | 头直接挂 mount 立柱顶，单条 `stand_to_head` REVOLUTE-Y（L336-L344），1 DOF |
| `tilt_pan_yoke` | `rec_led_work_light_var_head_tiltpan` | `model.py:L135-L220`（stand 后段 + u_yoke），joints L379-L396 | eligible if compatible | 立柱顶加 `u_yoke` 中间 part（`yoke_turntable`/`support_socket`/`center_post`/`fork_arm_*`/`pivot_cheek_*`/`pivot_axle`）；`stand_to_yoke` REVOLUTE-**Z**（pan ±π）→ `yoke_to_head` REVOLUTE-Y（tilt）串联；**移除头 `battery_pack`/`battery_port_panel`** |
| `telescope_tilt` | `rec_led_work_light_var_head_telescope` | `model.py:L151-L240`（outer sleeves + inner_mast），joints L423-L440 | eligible if compatible | 固定 `outer_post_*`/`outer_sleeve_*`（`_open_tube` 环形套筒）/`mast_clamp_*` + `inner_mast` 中间 part（`upright_*`/`yoke_plate_*`/`pivot_axle`）；`stand_to_mast` PRISMATIC-**Z**（travel 0→`MAST_TRAVEL`=0.055）→ `mast_to_head` REVOLUTE-Y 串联；保留电池 |

### Slot C：panel（发光面/头壳形态槽——LED 被排布与封装的载体）
| module_name | record_id | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `rect_flood`（基线） | parent `…_f7e038e0` | `model.py:L163-L264` | eligible if compatible | 矩形 tub 壳（`housing_back`/`housing_wall_*`/`bezel_*`）+ 矩形 `led_glass_panel`（Box）+ `led_{r}_{c}` 矩形网格（L248-L264） |
| `cob_round_disc` | `rec_led_work_light_var_panel_cob_round` | `model.py:L177-L254` | eligible if compatible | `_lathe` 车削圆头壳 `round_housing_shell` + `ring_bezel` + 圆 `round_glass_panel`（Cylinder）+ `cob_carrier_disc`；LED 用同心环 `led_{i}`（`LED_RING_COUNTS=(1,8,14,20)`=43，L37-L38 + L238-L254） |
| `dual_flood_bar` | `rec_led_work_light_var_panel_dual` | `model.py:L68-L321` | eligible if compatible | `_emit_flood_housing(head,…,center_y)` helper（L68-L186）被 `for i in range(PANEL_COUNT=2)` 循环（L312-L321）；`shared_crossbar` + 每壳 `led_{index}_{r}_{c}` 子网格 + `bezel_screw_*`；`FLOOD_W=(HEAD_W-HOUSING_GAP)/2`，读作单一俯仰单元 |

注：Slot C 的 `cob_round_disc`（同心环 `led_{i}`）与 `dual_flood_bar`（每壳子网格 `led_{index}_{r}_{c}`）各自带**不同的 LED 放置策略**，与下方矩形网格 `led_count` 轴**正交**——它们换的是 panel 载体形态，不是矩形阵列的计数轴。

## 槽位图（slot graph）

pattern: `mixed`（mount 结构槽 + head 链槽 + panel 形态槽 + led_count multiplicity 轴）

```text
[Slot A mount root]
   │   downstream: 顶部 yoke/upright/cheek 内侧面 + (可选)贯穿 pivot_axle
   │   ── 头俯仰铰的 parent 端（可被 Slot B 改写）──
   ▼
[Slot B head chain]  --(直挂 side_tilt) 或 (插入中间 part u_yoke / inner_mast)-->
   │   stand_to_head / yoke_to_head / mast_to_head : REVOLUTE about Y, origin (0,0,PIVOT_Z(local))
   │   + 可选上游 pan REVOLUTE-Z / lift PRISMATIC-Z（中间 part 相对 root）
   ▼
[light_head part]  ← [Slot C panel] 把 head 壳/玻璃/LED 形态注入 light_head
   │   led_count 矩形计数轴只作用于 rect_flood panel
```

跨 slot 连接要点：
- **mount → head 俯仰轴**：head 的 `pivot_boss_pos_y/neg_y`（Y 向钢 boss，`boss_y ≈ HEAD_W/2 + 0.004`）被 mount 顶部承托几何捕获——基线 `upright_*` 顶、aframe `pivot_yoke_*`、tripod `pivot_yoke_0/1`+`pivot_axle`、hook `yoke_arm_*`、telescope `inner_mast.upright_*`+`pivot_axle`。consumer joint = REVOLUTE about Y，origin `(0,0,PIVOT_Z)`。mating face = 立柱/yoke 顶内侧面，anchor = boss 轴心。
- **head 槽改写"头铰 parent"**：`side_tilt` 直接 `stand_to_head`（parent=root）；`tilt_pan`/`telescope` 在 root 与 `light_head` 之间插入中间 part（`u_yoke`/`inner_mast`），把头俯仰铰改挂到中间件（`yoke_to_head`/`mast_to_head`），并在 root↔中间件之间加 pan(REVOLUTE-Z)/lift(PRISMATIC-Z)。模板须把"头铰的 parent"作为可被 head 槽改写的接口端。
- **panel → head 壳**：`led_glass_panel`/`round_glass_panel`/`led_glass_panel_{i}` 与 `bezel_*`/`ring_bezel` 座入头壳前 recess，玻璃塞进 bezel 唇下（不漂浮）；LED 贴玻璃前微凸 `led_z = glass_z + 0.004`。mating face = 头壳前开口，anchor = 面中心。
- 互斥/可选：head 槽的 pan/lift 是上游可选段；mount 槽的 leg-fold / hook-fold 是 mount-local 附加可选 child；panel 槽三者互斥（同为头壳载体形态，不可叠）。

## 每槽位 Module Emits / Interfaces

### Slot A / module mount（h_frame_stand / folding_aframe / tripod_mast / handheld_hook）
| emits | 描述 | 来源 |
|---|---|---|
| parts | root part `stand_frame`（或 `handheld_base`）；aframe 另加 `folding_leg_0/1`，hook 另加 `hanging_hook` | S0 L75；S1 L162-L208；S3 L186-L204 |
| internal joints | aframe `stand_to_leg_i` REVOLUTE-Y (-0.35,0.55)；hook `base_to_hook` REVOLUTE-Y (0,1.65)；h_frame/tripod 无 mount-local joint | S1 L210-L219；S3 L382-L390 |
| upstream interface | 地面接触（`foot_*`/`rubber_foot_*`/`foot_i`）；root 无 parent | S0 L111-L125 |
| downstream interface | mount 顶部承托几何（`upright_*` 顶 / `pivot_yoke_*` / `yoke_arm_*` / `mast`+`pivot_axle`），高度 `PIVOT_Z`，捕获 head pivot boss | S0 L130-L154；S2 L130-L158 |

### Slot B / module head（side_tilt / tilt_pan_yoke / telescope_tilt）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `light_head`（始终）；tilt_pan 另加 `u_yoke`；telescope 另加 `inner_mast` | S0 L163；S4 L152；S5 L199 |
| internal joints | 头俯仰 REVOLUTE-Y（`stand_to_head`/`yoke_to_head`/`mast_to_head`）；tilt_pan 上游 `stand_to_yoke` REVOLUTE-Z (±π)；telescope 上游 `stand_to_mast` PRISMATIC-Z (0,0.055) | S0 L336-L344；S4 L379-L396；S5 L423-L440 |
| upstream interface | head pivot boss（`pivot_boss_*`）被 parent 承托几何捕获；中间 part 的下端坐入 root 顶（turntable on `pan_bearing_top` / upright in `outer_sleeve`） | S4 L154-L159, L481-L487；S5 L526-L544 |
| downstream interface | `light_head` 前开口承接 panel；tilt_pan 移除 `battery_pack` 以让出 yoke 中空 | S4 L442-L443 |

### Slot C / module panel（rect_flood / cob_round_disc / dual_flood_bar）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 全部以 inline visual 注入 `light_head`（panel 不是独立 part） | S0 L163-L264 |
| internal joints | 无（LED/玻璃/壳全 FIXED inline，无 joint） | — |
| upstream interface | 头壳前 recess + bezel 唇；boss 在头侧（`pivot_boss_*`），与 panel 形态无关，保持 head 俯仰接口不变 | S0 L266-L276；S6 L256-L266 |
| downstream interface | 发光面（glass + LED 阵列），纯视觉 | S0 L235-L264；S6 L220-L254；S7 L149-L170 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `mount_style` | enum | `h_frame_stand` / `folding_aframe` / `tripod_mast` / `handheld_hook` | `h_frame_stand` | choice | deterministic procedural sampler 选择 | Slot A 表 |
| `head_style` | enum | `side_tilt` / `tilt_pan_yoke` / `telescope_tilt` | `side_tilt` | choice | deterministic procedural sampler 选择 | Slot B 表 |
| `panel_style` | enum | `rect_flood` / `cob_round_disc` / `dual_flood_bar` | `rect_flood` | choice | deterministic procedural sampler 选择 | Slot C 表 |
| `led_count` | int (rows×cols) | rows∈[3,10], cols∈[3,12]，N∈[9,120] | 5×8=40 | conditional | 仅当 `panel_style==rect_flood` 时为矩形计数轴；cob/dual 用各自固定放置策略 | S0 L248-L264；S8/S9 |
| `pivot_z_scale` | float | [0.85, 1.35] | 1.0 | independent | 头铰离地高度 `PIVOT_Z`（基线 0.150；aframe 0.200；tripod `MAST_H`=0.175；hook 0.200） | S0 L42-L45；S1 L44 |
| `mast_travel` | float | [0.040, 0.075] | 0.055 | conditional | 仅 `telescope_tilt`；PRISMATIC 行程上界 | S5 L50, L430 |
| `tilt_range` | float (rad) | [0.50, 0.80] | 0.70 | independent | head 俯仰 ±range | S0 L343 |
| `head_w` / `head_h` | float | [0.18, 0.26] | 0.220 | independent | 头面尺寸；cob 头为方形（`HEAD_H=HEAD_W`） | S0 L27-L29；S6 L29-L33 |
| (—) | constraint | — | — | inequality | `boss_y = HEAD_W/2 + clr ≤ mount 顶部承托内距`：head 宽度放大须同步放大 mount 顶部跨距，否则 boss 漂浮/穿模；违反时回缩 head_w 或重采 | mount↔head 接口 |
| (—) | constraint | — | — | inequality | `dual_flood_bar` 总宽 = `2·FLOOD_W + HOUSING_GAP ≤ head_w`；且双头质量下 telescope 力臂受限（见兼容矩阵） | S7 L34 |

## Multiplicity / Copy Logic

本类有 **1 根 multiplicity 轴**（`led_count`），且只作用于 `rect_flood` panel。

- `count_param`：`led_count`（parent 以 `led_rows, led_cols = 5, 8` 表达 → 40；模板可暴露为 rows×cols 或总数）
- `N_range`（本轴产品域）：**[9, 120]**（约 3×3 至 10×12）。样本已覆盖 {15 (3×5, S8)、40 (5×8, parent 基线)、88 (8×11, S9)}。
- sampling domain：低 N 高频、大 N 长尾并设上限（控编译时长）
- copied object：单颗 LED 发射子 = `Box((led_size, led_size, 0.0025))`，`led_size≈0.009`，贴玻璃前 `led_z = glass_z + 0.004`
- naming：`led_{r}_{c}`，嵌套 `for r in range(led_rows): for c in range(led_cols)`
- placement：沿玻璃面 `span_x × span_y` 等距矩形网格（`px = -span_x/2 + span_x*r/(rows-1)`，`py` 同理），居中
- joint policy：**LED 全部 FIXED on `light_head`（inline visual，无 joint）**；multiplicity 纯视觉计数，不增自由度——与 Fence panel 链式不同，复制体不铰接
- source/gating：**parent 的 LED 阵列已是干净的 `led_{r}_{c}` 双层 for 循环（本批已确认），parent 自身即 copy-logic 源码，sparse/dense 仅改 `led_rows, led_cols` 两上界与隐含间距，无需重写**。
- **正交说明**：`cob_round_disc`（`led_{i}` 同心环，`LED_RING_COUNTS=(1,8,14,20)`）与 `dual_flood_bar`（`led_{index}_{r}_{c}` 每壳子网格）是 panel 槽下的**替代放置策略**，与本矩形 `led_count` 计数轴正交、不共用——选中 cob/dual 时 `led_count` 不解析为矩形阵列。

## 拓扑多样性审计

总组合数（结构槽）：`4 mount × 3 head × 3 panel = 36` distinct 结构组合。叠加 `led_count` 取样（保守下界 3 个 N，仅 rect_flood）：`36 + (rect_flood 分支 × 额外 N 样本) ≈ 108`（与 source map 预审一致）。

理由：单 head 槽就给出三种不同关节图（1×REVOLUTE / REVOLUTE-Z+REVOLUTE-Y / PRISMATIC-Z+REVOLUTE-Y），mount 槽再叠加 0/2 条 leg-fold REVOLUTE 或 1 条 hook REVOLUTE，panel 槽改 part/visual 拓扑（单壳 vs 双壳子网格 vs 圆 lathe）。仅 head×mount 的关节图组合已远超 10。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling，`seed=0` 不特殊。先选 mount，再选 head（解析头铰 parent + 中间 part），再选 panel，最后按 panel 是否 rect_flood 解析 `led_count`。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类结构组合上界 36，叠 led_count 后约 108，受类别兼容约束（panel 互斥、dual×telescope gating）后实际 distinct 拓扑预计在 30-80 量级，低于 300 属类别固有约束（结构槽数量有限），可接受。

Controlled local parameterization：初版模板应包含 `pivot_z_scale`（头铰离地高度）、`mast_travel`（仅 telescope）、`tilt_range`、`head_w/head_h`；全部在 `resolve_config` 内 clamp/派生，受 mount↔head boss 跨距 inequality 约束，不破坏 InterfaceSpec/MatingContract/multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | mount → head → panel → led_count 顺序加权选择；head 选择决定头铰 parent 与中间 part；panel==rect_flood 才解析 led_count | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | panel 三候选互斥；`dual_flood_bar × telescope_tilt` 需 gate（双头质量 + 升降力臂，潜在 CoM/穿插）；head==tilt_pan 时强制移除 head 电池并安置；head_w 放大须同步 mount 顶跨距 | 无 floating、collision、轴/range、max led_count、bulky dual head、optional moving child 失败 |
| controlled local variation | `pivot_z_scale`/`mast_travel`/`tilt_range`/`head_w` 在 clamp 内 | 比例变化不破坏 boss 捕获、yoke 间距、玻璃座入、joint origin |
| regression overrides | none（如未来 sweep 发现稳定失败组合再补，须写明 seed+原因） | previously failed / reviewer-selected only |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | 与 contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| mount | 4 | yes | yes | |
| head | 3 | yes | yes | |
| panel | 3 | yes | yes | |
| led_count (multiplicity) | N∈[9,120]，3 样本 | yes | yes | 仅 rect_flood |

## Validator
- slot_choices_for_seed 返回已实现的 module 名（mount/head/panel）。
- config_from_seed 对所有普通 seed 用 deterministic procedural sampling。
- compatibility matrix / gating 阻止非法组合（panel 互斥；dual×telescope gating；head_w 与 mount 顶跨距联合可行域）。
- head 俯仰铰恒为 REVOLUTE about Y，origin `(0,0,PIVOT_Z(local))`；head==tilt_pan 时上游 `stand_to_yoke` 为 REVOLUTE-Z (±π)，head==telescope 时上游 `stand_to_mast` 为 PRISMATIC-Z (0,~0.055)。
- 头铰 parent 随 head 槽改写（root / `u_yoke` / `inner_mast`）且中间 part 真实坐入 root 承托面。
- head pivot boss 被 mount 顶部承托几何捕获（captured-pin overlap 需 element-scoped allow_overlap）。
- panel：玻璃/LED 座入头壳前 recess（不漂浮）；rect_flood LED 数与 `led_count` 一致且等距居中；cob 同心环数 = `sum(LED_RING_COUNTS)`；dual 双壳各自子网格齐全。
- head==tilt_pan 时 `battery_pack`/`battery_port_panel` 已移除。
- LED 复制体全 FIXED inline，无 per-LED joint。
- 连续 scale（pivot_z/mast_travel/head_w）在 `resolve_config` clamp/派生，不留到 builder 失败。

## Reject cases
- head 无 REVOLUTE-Y 俯仰，或俯仰轴竖直/前后向 → 不成其为 work light。
- head pivot boss 悬空 / 用不可见接口盘连接 mount，未被立柱/yoke/axle 捕获。
- head==tilt_pan/telescope 却仍把头铰直挂 root（未插入中间 part），或中间 part 漂浮不坐入 root。
- panel 三候选叠加（同时出现圆 lathe 壳与矩形 tub 壳），或 dual 双壳共用单 LED 网格。
- `led_count` 把 LED 做成独立 FIXED child part 并各加 joint（应为 inline 视觉计数）。
- head_w 放大未同步 mount 顶部跨距，导致 boss 穿模或 cheek 夹不住。
- 退化成多节平行四连杆悬臂（混入 task lamp）或无承托手电（混入 flashlight）。

## 与相邻类别的边界
- 不该混入 `articulated_task_lamp`：本类是 **jobsite flood light**——单段承托 + 大泛光头水平俯仰，发光面是 LED 阵列玻璃板；task lamp 是多节臂/平行四连杆台灯，关节链长且无泛光头/电池盒/U 提手语义。
- 不该混入 handheld flashlight / spotlight：本类必须有离地承托（H-frame/A-frame/tripod/handheld base）与 REVOLUTE 俯仰头；纯手电没有承托俯仰机构。
- 不该混入 `overshot_waterwheel` 等连续旋转类：head 是 bounded REVOLUTE 俯仰（非 CONTINUOUS），无水力/旋转主轴语义。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；picture-subcat fork 家族（workbench-only），引用根植 articraft_data 仓库；等待人工审核，审核通过前不进入模板实现 |
