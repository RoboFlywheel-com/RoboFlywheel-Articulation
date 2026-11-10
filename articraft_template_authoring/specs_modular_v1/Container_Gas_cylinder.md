# Container / Gas cylinder (pressurized LPG / scuba-style tank) — Modular Spec

> 来源小类：`picture/Container/Gas cylinder`（articraft_data 上游 Container/Gas cylinder fork-variant pool）。
> 单母资产单参考图：所有候选均从同一 parent `rec_red-lpg-gas-cylinder-with-a-top-valve-handwheel-...5d5b07e2`（红色 LPG 钢瓶）逐格 fork 出来，diff 干净、基线一致。
> 引用 `model.py:Lx-Ly` 来自各 record 当前 `data/records/<id>/revisions/rev_000001/model.py`；以 part / joint / helper **名字** 为准（`body`/`_body_mesh`/`valve`/`_valve_mesh`/`handwheel`/`_handwheel_mesh`/`_collar_mesh`/`foot_ring`/`_foot_mesh`/`_neck_collar_mesh`/`bow_guard`/`body_to_bow_guard`/`_cage_bar_mesh`/`cage_top_ring`/`valve_to_handwheel`/`valve_to_lever`/`valve_to_bonnet`/`body_to_foot_{i}` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_gas_cylinder` |
| template path | `agent/templates/Container_Gas_cylinder.py` |
| test path (optional) | `tests/agent/test_container_gas_cylinder_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: top_guard + valve_closure + base，全部 parallel children 挂到 `body` root；**外加** `cage_bar_count` 一根 multiplicity 轴，归属 top_guard 的 `vented_cage_shroud` 候选）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 1 parent + 9 fork 变体 = 10 |
| read_count | 10（全文逐一读取：parent + solid_neck_collar / carry_handle_arch / vented_cage_shroud / cage_n6 / cage_n8 / lever_clip_valve / screw_bonnet_cap / concave_recessed_base / n_feet_base）|
| read_scope | all 5-star samples in this category（单母资产单图小类，全量读取，无抽样）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14 |

读取要点（拓扑变化轴识别）：
- **共享不变骨架**：所有 10 个样本共用 `_body_mesh`（LatheGeometry 钢瓶身：foot 过渡→直壁→圆肩→域顶→neck boss，`segments=64`，坐地 z=0，轴沿 +Z，`BODY_R=0.150`）+ `_valve_mesh`（CadQuery 布尔并集 brass 阀体：seat boss + 阀块 + +X 侧出气 spigot + 阀杆）+ `body_to_valve` FIXED（阀座在 neck boss 上）。这是类别身份骨架，**不入 slot**，固定发射。
- **Slot top_guard（阀顶护圈/护罩）**：parent = `_collar_mesh`（Torus 顶环 + `for i in range(4)` 4 struts，开放式）；solid_neck_collar = `_neck_collar_mesh`（LatheGeometry 实心杯形领圈，连续壁）；carry_handle_arch = `_bow_guard_mesh`（`tube_from_spline_points` 倒 U 拱杆，**升级为独立 `bow_guard` part + `body_to_bow_guard` REVOLUTE +Y**，含 2 个 `bow_anchor_pad_{i}` 固定 boss）；vented_cage_shroud = `_cage_bar_mesh` 循环 N 根竖条 + `cage_top_ring`/`cage_bottom_ring`（multiplicity 轴载体）。
- **Slot valve_closure（主机构槽，承载非 fixed joint）**：parent = `handwheel` part / `valve_to_handwheel` REVOLUTE 竖直 +Z（星形手轮 + off-axis lug+knob 使旋转可检测）；lever_clip_valve = `lever` part / `valve_to_lever` REVOLUTE 水平 +Y（自闭扳手下压开/弹回闭，limit `[0, 1.05]`）；screw_bonnet_cap = `bonnet` part / `valve_to_bonnet` REVOLUTE 竖直 +Z（域顶螺帽罩旋拧密封，limit `[0, 6π]`，indicator lug 使旋转可检测）。每个候选 ≥1 非 fixed joint。
- **Slot base（底座/支脚）**：parent = `foot_ring` part / `body_to_foot` FIXED（深色裙环）；concave_recessed_base = body shell 内凹碟形底（**无独立脚环 part**，靠一体外缘 rim 站立）；n_feet_base = `foot_{i}` parts × N（共享 `_stub_foot_mesh`）/ `body_to_foot_{i}` FIXED（N=3 短脚墩等角分布）。
- **Multiplicity 轴确认**：vented_cage_shroud(N=4) / cage_n6(N=6) / cage_n8(N=8) 三个样本同形不同 N，证实 `cage_bar_count` 是真实可复制结构轴（`N_CAGE_BARS` 常量 + `for i in range(N)` + 等角 placement + `cage_bar_{i}` 命名 + 全 FIXED 到 body）。
- 冗余/分流说明：parent 的 `_collar_mesh` 4 struts 与 `_handwheel_mesh` 4 spokes 是 visual 内部循环复制（merge 进单 mesh），**不**提为小类 multiplicity 轴。颜色/材质（红/蓝/灰钢瓶、brass↔chrome 阀）不算结构轴，归入 `palette_style`。

## 核心身份

加压燃气钢瓶 / LPG 家用钢瓶 / 潜水式气罐（pressurized gas cylinder）：一只直立厚壁钢瓶身，中心轴沿 +Z，坐地 z=0，居中于 (x=0,y=0)。瓶身由 `LatheGeometry` revolve 发射为旋转体 shell（foot 过渡→直壁→圆肩 shoulder→域顶 dome→收 neck boss），明确**高 > 直径**（`bext[2] > 0.45` 且 `> max(x,y)`）。域顶中心轴上 FIXED 一只 brass 阀体（CadQuery 布尔并集：seat boss + 阀块 + 侧出气 spigot + 阀杆），阀顶上方一只**操作机构**绕某轴动作（**主活动语义**）：星形 handwheel 绕竖直阀轴 REVOLUTE 旋转（off-axis lug 使旋转可检测）/ 自闭 lever 绕水平轴 REVOLUTE 下压开弹回闭 / 螺帽 bonnet 绕竖直阀轴 REVOLUTE 旋拧下降密封。阀顶外围一圈**护圈/护罩**（top_guard）保护阀体：开放环+struts / 实心杯形领圈 / 倒 U 提手弓（可摆动 REVOLUTE）/ N 根竖条开槽护笼。瓶底一种**底座**站立：钢制裙状脚环 / 内凹碟形一体底 / N 个等角短脚墩。默认成熟域：单瓶单阀单护罩单底座（cage 护笼有 N 根竖条 multiplicity 轴）。

不该混入：
- **饮料/食品易拉罐（`container_can`）**：can 是薄壁短矮罐、拉环顶盖、无阀无护圈、矮 < 高比例不强；gas cylinder 是厚壁高瓶身 + 域顶 + neck 阀机构 + 护圈，高 >> 直径。
- **气雾喷漆罐（`container_paint_spray`）**：paint_spray 是细高罐 + 顶部按压喷嘴 actuator（按下喷射）+ 圆顶盖，无侧出气阀 + handwheel/lever/螺帽机构、无 struts/cage 护圈；gas cylinder 的阀是侧出气 spigot brass 阀体 + 旋/压/拧机构。

## 槽位 + 候选模块表

> **建模注记**：`body`（root，坐地 z=0）+ `valve`（FIXED 在 neck boss）是固定不变骨架，一次发射，不是 slot。`top_guard` / `valve_closure` / `base` 三个 named slot 全部 parallel children 挂到 `body`（valve_closure 链 = body→valve→机构）。三槽笛卡尔积 × cage multiplicity 构成拓扑多样性（见 §9）。

### Slot A：top_guard（阀顶护圈/护罩——含 multiplicity 候选）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| ring_on_struts（基线）| rec_red-...-5d5b07e2（parent）| `_collar_mesh` L125-141 + `collar_guard` visual L171 | eligible if compatible | Torus 顶环 + `for i in range(4)` 4 短 struts 升到 shoulder，开放式护圈；merge 单 mesh，挂 body 固定 visual，无独立 joint |
| solid_neck_collar | rec_container_gas_cylinder_var_solid_neck_collar | `_neck_collar_mesh` L125-151 + `neck_collar` visual L181 | eligible if compatible | LatheGeometry 实心冲压杯形领圈（连续圆柱壁 base flare→直壁→rolled lip），包裹阀，挂 body 固定 visual，无独立 joint；圆对称 x-span≈y-span |
| carry_handle_arch | rec_container_gas_cylinder_var_carry_handle_arch | `_bow_guard_mesh` L132-160 + `_bow_anchor_pad_mesh` L163-166 + `bow_guard` part L237-238 + `body_to_bow_guard` REVOLUTE +Y L242-255 | eligible if compatible | `tube_from_spline_points` 倒 U 拱提手（升级为**独立 part + REVOLUTE +Y 摆动**，可前后摆 ±0.55π），2 个 `bow_anchor_pad_{i}` 固定 boss 捕获两端；唯一一个含活动护罩的候选 |
| vented_cage_shroud | rec_container_gas_cylinder_var_vented_cage_shroud | `_cage_bar_geometry` L134-136 + `_cage_ring_mesh` L139-146 + `_cage_bar_mesh` L149-155 + `for i in range(N_CAGE_BARS)` L188-193 + `cage_top_ring`/`cage_bottom_ring` visual L186-187 | eligible if compatible | N 根等角竖条（`cage_bar_{i}`）+ 顶环 + 底环开槽护笼，挂 body 固定 visual，无独立 joint；**承载 `cage_bar_count` multiplicity 轴**（样本 N∈{4,6,8}）|

硬约束记录：top_guard 4 candidate（达 3-6 目标）。ring_on_struts/solid_neck_collar/vented_cage_shroud 均为 body 固定 visual（无独立 joint）；carry_handle_arch 是唯一含活动件（REVOLUTE +Y 摆动 bow_guard part + 2 anchor pads）的候选，贡献额外 joint 拓扑。vented_cage_shroud 承载 N 根竖条 multiplicity。

### Slot B：valve_closure（**主开合机构槽**——被操作的开关件，承载非 fixed joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| handwheel_valve（基线）| rec_red-...-5d5b07e2（parent）| `_handwheel_mesh` L100-122 + `handwheel` part L219-220 + `valve_to_handwheel` REVOLUTE +Z L227-235 | eligible if compatible | 星形手轮（hub+Torus rim+`for i in range(4)` spokes+off-axis lug+knob）绕竖直阀轴 REVOLUTE 旋转，limit `[-4π, 4π]`；off-axis lug 使 quarter-turn 可检测（rest +X bias → +Y bias）|
| lever_clip_valve | rec_container_gas_cylinder_var_lever_clip_valve | `_lever_mesh` L101-141 + `lever` part L240-241 + `valve_to_lever` REVOLUTE +Y L248-256 | eligible if compatible | 自闭式 clip-on 扳手阀（pivot hub + +X 水平 arm + paddle grip + spring boss），绕水平 +Y 轴 REVOLUTE 下压开（limit `[0, 1.05]`，q=0 水平闭合，正 q tip 下降开阀）；clip hub 卡阀杆 allow_overlap |
| screw_bonnet_cap | rec_container_gas_cylinder_var_screw_bonnet_cap | `_bonnet_mesh` L98-164 + `bonnet` part L264-265 + `valve_to_bonnet` REVOLUTE +Z L271-283 | eligible if compatible | 域顶螺帽罩（CadQuery skirt+hemisphere dome+blind bore+`for i in range(6)` grip ribs+indicator lug）绕竖直阀轴 REVOLUTE 旋拧（limit `[0, 6π]`≈3 圈，q=0 全密封）；indicator lug 使旋转可检测；罩盖阀杆 expect_overlap/allow_overlap |

硬约束记录：valve_closure 3 candidate（达下限 3，单母资产单图小类样本上限）。三者**全部 ≥1 非 fixed REVOLUTE joint**（满足主机构 ≥1 活动件）：竖直 +Z 旋（handwheel）/ 水平 +Y 压（lever）/ 竖直 +Z 拧（bonnet）。joint 轴向 + limit + 机构形态各异（旋钮 / 扳手 / 螺帽），是真实结构差异。所有候选挂 valve（body→valve→机构链），origin 在阀杆顶 / 阀块顶真实硬件。

### Slot C：base（底座/支脚）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键结构特征 |
|---|---|---|---|---|
| foot_ring（基线）| rec_red-...-5d5b07e2（parent）| `_foot_mesh` L144-154 + `foot_ring` part L189-190 + `body_to_foot` FIXED L195-201 | eligible if compatible | LatheGeometry 深色钢裙环（套在瓶底外缘），独立 `foot_ring` part / `body_to_foot` FIXED；坐地 z≈0，allow_overlap 套 body base |
| concave_recessed_base | rec_container_gas_cylinder_var_concave_recessed_base | `_body_mesh` 内凹底 profile L44-66（center 抬高 `DISH_DEPTH` → 外缘 rim 落地）+ **无 foot part** L256-261 | eligible if compatible | 一体内凹碟形底（dish center 抬高，外缘 rim z=0 站立），**无独立脚环 part / 无 base joint**（base 完全 fold 进 body shell）；test 断言 `"foot_ring" not in part_names` |
| n_feet_base | rec_container_gas_cylinder_var_n_feet_base | `_stub_foot_mesh` L152-165 + `for i in range(N_FEET)` L201-222 + `foot_{i}` part + `body_to_foot_{i}` FIXED L213-222 | eligible if compatible | N=3 短脚墩（共享 `_stub_foot_mesh` CadQuery filleted block），等角 FIXED 到 body 底缘（`foot_{i}` parts / `body_to_foot_{i}` joints，120° 等角）；含次级 foot_count 副本逻辑（见 §8）|

硬约束记录：base 3 candidate（达下限 3）。三者 part/joint 拓扑明确不同：foot_ring = 1 part + 1 FIXED joint；concave_recessed_base = 0 part + 0 base joint（fold 进 body）；n_feet_base = N parts + N FIXED joints（含次级 multiplicity）。坐地不变量一致（z≈0 站立）。

## 槽位图（slot graph）

pattern: mixed（`body` 为 root，valve/护罩/底座/机构挂它；vented_cage_shroud 含一根 cage_bar_count multiplicity 轴）

```
body(body_form 固定骨架)  [ROOT, 坐地 z=0, 轴沿 +Z]
   │
   ├── valve  --[body_to_valve: FIXED @ neck boss (0,0,VALVE_AXIS_Z-0.006)]  [固定骨架, brass 阀体]
   │     │
   │     └── valve_closure（主机构, 互斥一种）:
   │           ├─ handwheel_valve:  valve --[valve_to_handwheel: REVOLUTE +Z @ 阀杆顶 (0,0,0.072)]--> handwheel  (limit ±4π)
   │           ├─ lever_clip_valve: valve --[valve_to_lever:     REVOLUTE +Y @ 阀杆顶 (0,0,0.072)]--> lever      (limit [0,1.05])
   │           └─ screw_bonnet_cap: valve --[valve_to_bonnet:    REVOLUTE +Z @ 阀块顶 (0,0,0.046)]--> bonnet     (limit [0,6π])
   │
   ├── top_guard（阀顶护罩, 互斥一种）:
   │     ├─ ring_on_struts:      body 固定 visual `collar_guard`（Torus 环 + 4 struts），无 joint
   │     ├─ solid_neck_collar:   body 固定 visual `neck_collar`（实心杯壁），无 joint
   │     ├─ carry_handle_arch:   body 固定 visual `bow_anchor_pad_{0,1}` + body --[body_to_bow_guard: REVOLUTE +Y @ (0,0,BOW_ANCHOR_Z)]--> bow_guard part (limit ±0.55π)
   │     └─ vented_cage_shroud:  body 固定 visual `cage_top_ring`+`cage_bottom_ring`+ {`cage_bar_{i}` : i∈[0,N)}（N=cage_bar_count, 等角 FIXED visual），无 joint
   │
   └── base（底座, 互斥一种）:
         ├─ foot_ring:            body --[body_to_foot: FIXED @ (0,0,0)]--> foot_ring part
         ├─ concave_recessed_base: 无 part / 无 joint（内凹底 fold 进 body shell profile）
         └─ n_feet_base:          body --[body_to_foot_{i}: FIXED @ 等角底缘]--> foot_{i} part  (i∈[0,N_FEET), N_FEET=3)
```

接口点位与 joint 语义：
- **valve_closure 接口**：所有机构挂 `valve`（parent），origin 在阀杆顶 valve-local `(0,0,0.072)`（handwheel/lever）或阀块顶 `(0,0,0.046)`（bonnet 真实落座面）。handwheel/bonnet 轴 +Z（竖直阀轴，`abs(axis[2])>0.99`），lever 轴 +Y（水平，`abs(axis[2])<0.01`）。rest pose q=0 闭合/水平/全密封。lever clip hub / bonnet 罩盖阀杆为 captured-fit allow_overlap（hub bore 卡阀杆 / 阀杆顶 nest 进 bonnet 域顶）。
- **top_guard 接口**：ring_on_struts/solid_neck_collar/vented_cage_shroud 为 body 固定 visual（无独立 joint），struts/cage 底环坐 shoulder（`SHOULDER_TOP_Z` 附近），顶环高于阀（`collar/cage top z ≥ valve z`）。carry_handle_arch 例外：`body_to_bow_guard` REVOLUTE 绕 +Y 轴 origin 在 `(0,0,BOW_ANCHOR_Z)`（两 anchor pad 中点），bow_guard part 可前后摆，2 个 `bow_anchor_pad_{i}` 固定 visual 捕获两端（pad↔tube allow_overlap）。
- **base 接口**：foot_ring `body_to_foot` FIXED origin `(0,0,0)`（瓶底）；n_feet_base `body_to_foot_{i}` FIXED origin 等角 `(FOOT_R·cosθ, FOOT_R·sinθ, FOOT_TOP_Z)` + rpy `(0,0,θ)`；concave_recessed_base 无 base joint（dish 底直接是 body shell 的 lathe profile，外缘 rim z=0 落地）。脚环/脚墩坐地 allow_overlap 套 body base。
- **mating policy**：护罩 struts/cage/collar 套 shoulder、阀座套 neck boss、脚环套瓶底、clip hub 卡阀杆、bonnet 罩阀杆均为 captured / 友配 captured-fit（故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（落真实 neck/阀杆/shoulder/底缘硬件）+ element-scoped `allow_overlap`（见各 record run_tests 的 `ctx.allow_overlap`）。
- **rest pose**：所有机构 q=0 闭合（handwheel 居中 / lever 水平 / bonnet 全密封）；bow_guard q=0 直立拱起；cage/collar/脚座固定。机构旋转/下压/拧 + bow 摆动为 viewer 目检的活动语义。
- **互斥 / 可选**：top_guard / valve_closure / base 各候选互斥（一次只一种）；concave_recessed_base 是空 base 机构（不发射 foot part / joint）；carry_handle_arch 是 top_guard 中唯一含活动 part 的候选；cage_bar_count multiplicity 仅在 vented_cage_shroud 候选激活。

## 每槽位 Module Emits / Interfaces

### 固定骨架（非 slot）/ body + valve（ROOT 链）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`(visual: `body_shell` lathe 钢瓶身 + `hazard_label` Box 固定 visual) / `valve`(visual `valve_body`) | parent `_body_mesh` L43-59 / `_valve_mesh` L62-97 / hazard L175-180 |
| internal joints | `body_to_valve` FIXED @ neck boss `(0,0,VALVE_AXIS_Z-0.006)` | parent L210-216 |
| upstream interface | 坐地 z=0（body root） | parent L33-37 |
| downstream interface | neck boss top（valve_closure 链 parent）/ shoulder（top_guard 套）/ 瓶底缘（base 套）| parent L36-40 |

### Slot A / top_guard（每候选发射对应护罩）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `collar_guard` visual / `neck_collar` visual / `bow_guard` part + `bow_anchor_pad_{0,1}` visual / `cage_top_ring`+`cage_bottom_ring`+`cage_bar_{i}` visual | 见 slot 表各源 |
| internal joints | 仅 carry_handle_arch 有 `body_to_bow_guard` REVOLUTE +Y（limit ±0.55π）；其余 candidate 无 joint（固定 visual）| carry_handle_arch L242-255 |
| upstream interface | 挂 body：struts/cage 底环坐 shoulder，collar/cage 顶环高于阀 | 各 record collar/cage test |

### Slot B / valve_closure（每候选发射对应活动机构，parent=valve）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handwheel` / `lever` / `bonnet` | 各机构源 |
| internal joints | `valve_to_handwheel` REVOLUTE +Z (limit ±4π) / `valve_to_lever` REVOLUTE +Y (limit [0,1.05]) / `valve_to_bonnet` REVOLUTE +Z (limit [0,6π]) | parent L227-235 / lever L248-256 / bonnet L271-283 |
| upstream interface | origin 在阀杆顶 `(0,0,0.072)` 或阀块顶 `(0,0,0.046)` 真实硬件 | 各 record |

### Slot C / base（每候选发射对应底座）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `foot_ring` part / 无（concave fold 进 body）/ `foot_{i}` parts × N_FEET | foot_ring parent L189 / n_feet `_stub_foot_mesh` L152-165 |
| internal joints | `body_to_foot` FIXED / 无 / `body_to_foot_{i}` FIXED × N_FEET | parent L195-201 / n_feet L213-222 |
| upstream interface | 坐地 z≈0：脚环套底缘 / dish 外缘 rim / 脚墩等角 FIXED | 各 record base test |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| top_guard | enum | ring_on_struts / solid_neck_collar / carry_handle_arch / vented_cage_shroud | ring_on_struts | choice | deterministic procedural sampler 选 | module table |
| valve_closure | enum | handwheel_valve / lever_clip_valve / screw_bonnet_cap | handwheel_valve | choice | sampler 选 | module table |
| base | enum | foot_ring / concave_recessed_base / n_feet_base | foot_ring | choice | sampler 选 | module table |
| cage_bar_count | int | [3, 12]（仅 top_guard=vented_cage_shroud 时激活）| 4 | conditional | 仅当 top_guard=vented_cage_shroud 时加权采样（见 §8）；其余 top_guard 不暴露 | vented_cage_shroud L126,188 |
| foot_count | int | [3, 4]（仅 base=n_feet_base 时激活，次级副本逻辑）| 3 | conditional | 仅当 base=n_feet_base 时采样（见 §8）；等角 FIXED | n_feet_base L44,201 |
| palette_style | enum | industrial_red_lpg / industrial_blue_lpg / industrial_grey_steel / safety_yellow / medical_white / forest_green_propane / galvanized_zinc / brushed_steel_scuba / matte_powder_coat / weathered_scuffed | industrial_red_lpg | palette | palette only，**不计入 slot_choice**；含显式 finish 维度（见下 colorway 表）| 各 record material |
| body_height_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放瓶身高 H（直壁段 → shoulder/neck/护罩 mount 同比抬升），clamp；保高>直径不变量 | resolve clamp |
| body_radius_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放瓶身半径 `BODY_R` → 脚环/护罩环半径派生跟随，clamp | resolve clamp |
| guard_ring_radius_scale | float | [0.92, 1.10] | 1.0 | equation | `GUARD_R = base · guard_ring_radius_scale`；cage/collar/struts 环半径 + cage_bar 放置半径派生跟随（保护罩仍 encircle 阀且不撞 body 外缘）| resolve clamp |
| joint_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 lever limit / bow_guard 摆动 limit（不动 handwheel/bonnet 的 ±n·π 圈数），clamp | resolve clamp |
| (—) | constraint | — | — | inequality | 护罩 encircle 不撞：`GUARD_R ≥ valve_outer_R + clearance` 且 `GUARD_R ≤ BODY_R·body_radius_scale − margin`；违反按比例回缩 guard_ring scale | 接口 / clearance |
| (—) | constraint | — | — | inequality | bow_guard 摆动不穿阀/护罩：`BOW_RISE·height_scale > handwheel_top_z + clearance`；违反回缩 height/travel scale | 接口 / clearance |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`guard_ring_radius_scale` 为 equation（cage/collar 环半径 + cage_bar 放置半径跟随），并受 encircle 不等式约束。scale 只动安全比例 / clearance / 细节尺寸，绝不改 top_guard / valve_closure / base 的拓扑或 cage_bar_count multiplicity。

### palette_style colorway（≥3，本版 **10 配色**；从 5★ 源锚定 + 现实推断）

每个 colorway = body + valve/机构(guard/accent) + base(foot) + **finish（材质表面处理维度）** 四件配色。finish 是显式声明的独立维度（与 rgba 并列），下游模板按 finish 选 roughness/metalness 风格（gloss=低糙高金属反光、matte=高糙低反光、galvanized=斑驳锌花、brushed=方向性拉丝、weathered=磨损叠脏），但 finish **不改结构/slot/multiplicity**，纯外观。

| palette_style | finish（材质表面）| body 材质 (rgba) | valve / 机构材质 (rgba) | guard 材质 | base / foot 材质 (rgba) | 来源（5★ material）|
|---|---|---|---|---|---|---|
| industrial_red_lpg（基线）| glossy_industrial_paint（亮面工业漆）| weathered_red_steel (0.72,0.16,0.13) | brass_valve (0.78,0.62,0.22) | bare_steel (0.62,0.62,0.64) | dark_foot (0.12,0.12,0.13) | parent L160-164 |
| industrial_blue_lpg | glossy_industrial_paint（亮面工业漆）| industrial_blue_steel (0.16,0.28,0.55) | brass_valve (0.78,0.62,0.22) | bare_steel (0.62,0.62,0.64) | dark_foot (0.12,0.12,0.13) | parent material 族换色（源 §66 鼓励配色叠加）|
| industrial_grey_steel | glossy_industrial_paint（亮面工业漆）| bare_steel_grey (0.62,0.62,0.64) | brass_valve (0.78,0.62,0.22) | bare_steel (0.62,0.62,0.64) | dark_foot (0.12,0.12,0.13) | parent `bare_steel` L163 |
| safety_yellow | glossy_industrial_paint（安全亮黄漆）| safety_yellow_paint (0.86,0.72,0.14) | zinc_plated_cap (0.52,0.55,0.58) | bare_steel (0.62,0.62,0.64) | dark_foot (0.12,0.12,0.13) | screw_bonnet_cap `zinc_plated_cap` L206 + hazard 黄 L207 |
| medical_white | glossy_industrial_paint（医用亮白漆）| medical_white_paint (0.92,0.93,0.94) | chrome_valve (0.80,0.81,0.83) | bare_steel (0.62,0.62,0.64) | dark_foot (0.12,0.12,0.13) | parent material 族换色（医疗气瓶域）|
| forest_green_propane | glossy_industrial_paint（丙烷亮绿漆）| forest_green_paint (0.16,0.40,0.22) | brass_valve (0.78,0.62,0.22) | bare_steel (0.62,0.62,0.64) | dark_foot (0.12,0.12,0.13) | parent material 族换色 |
| galvanized_zinc | galvanized_zinc（热镀锌斑驳）| galvanized_zinc_body (0.66,0.68,0.70) | zinc_plated_cap (0.52,0.55,0.58) | galvanized_zinc_body (0.66,0.68,0.70) | dark_foot (0.12,0.12,0.13) | bonnet `zinc_plated_cap` L206 锌族扩展 |
| brushed_steel_scuba | brushed_steel（拉丝不锈钢）| brushed_steel_body (0.70,0.71,0.73) | chrome_valve (0.80,0.81,0.83) | brushed_steel_body (0.70,0.71,0.73) | dark_foot (0.12,0.12,0.13) | parent `bare_steel` L163 拉丝族（潜水气瓶域）|
| matte_powder_coat | matte_powder_coat（哑光粉末喷涂）| matte_charcoal_coat (0.22,0.23,0.25) | bare_steel (0.62,0.62,0.64) | matte_charcoal_coat (0.22,0.23,0.25) | dark_foot (0.12,0.12,0.13) | parent dark/steel 族哑光化 L162-163 |
| weathered_scuffed | weathered_scuffed（磨损刮蹭旧瓶）| weathered_red_steel (0.72,0.16,0.13) | brass_valve (0.78,0.62,0.22) | rusted_steel (0.46,0.34,0.24) | dark_foot (0.12,0.12,0.13) | parent `weathered_red_steel` L160 磨损族 |

palette_style 只换 rgba 材质 + finish 表面处理，**永不**改结构 / slot / multiplicity；下游模板 per-seed `rng.choice(PALETTE_STYLES)` 10 档（小类自由叠加在结构变化之上）。finish 维度仅驱动外观（roughness/metalness 风格），不计入 slot_choice、不动 topology distinct。

## Multiplicity / Copy Logic

本小类有 **1 根模板级 multiplicity 轴**（`cage_bar_count`，归属 top_guard 的 vented_cage_shroud 候选）+ 1 根次级候选内副本逻辑（`foot_count`，归属 base 的 n_feet_base 候选）。

### 轴 1（模板级）：cage_bar_count
- `count_param`：`cage_bar_count`（vented_cage_shroud 护笼竖条数）。
- `N_range`：`[3, 12]`（产品全程；护笼竖条现实区间约 3-12）。测试偏小（sweep 主采 3-8），大 N 稀有。
- sampling domain：加权采样，小 N 高频（N∈{4,5,6} 权重最高，覆盖样本 {4,6,8}），N≥9 稀有尾部；**仅当 top_guard=vented_cage_shroud 被选中时激活**，其余 top_guard 不暴露此参数（conditional）。
- copied object：单根竖直 `cage_bar`（共享 `_cage_bar_geometry(bar_r, height)` CylinderGeometry helper）。
- naming：`cage_bar_{i}`（i∈[0,N)），body 固定 visual。
- placement：绕阀轴等角分布在固定半径 `CAGE_RING_R`（受 guard_ring_radius_scale）环上，`ang = i·2π/N`，底端坐 `cage_bottom_ring`（shoulder 附近）顶端接 `cage_top_ring`（高于阀）。
- joint policy：全部 **FIXED visual 到 body**（随 body 动，无独立活动 joint）。
- source/gating：vented_cage_shroud(N=4) `_cage_bar_mesh` L149-155 + `for i in range(N_CAGE_BARS)` L188-193 / cage_n6(N=6) `_cage_bar_mesh` L135 + `for i in range(N_CAGE_BARS)` L187 / cage_n8(N=8) `_cage_bar_mesh` L135 + `for i in range(N_CAGE_BARS)` L198。三样本证实同形不同 N。

### 轴 2（次级，候选内副本逻辑，非小类主 multiplicity 轴）：foot_count
- `count_param`：`foot_count`（n_feet_base 脚墩数）。
- `N_range`：`[3, 4]`（脚墩现实区间窄）。fork 样本 N=3。
- sampling domain：仅当 base=n_feet_base 时采样（conditional），N=3 高频、N=4 偶发。
- copied object：单个短脚墩（共享 `_stub_foot_mesh` CadQuery filleted block）。
- naming：`foot_{i}`（i∈[0,N)）独立 part。
- placement：等角 `θ = i·2π/N`，origin `(FOOT_R·cosθ, FOOT_R·sinθ, FOOT_TOP_Z)` + rpy `(0,0,θ)`。
- joint policy：每个 `body_to_foot_{i}` **FIXED** 到 body 底缘（坐地站立）。
- source/gating：n_feet_base `for i in range(N_FEET)` L201-222。

注：parent 的 `_collar_mesh` 4 struts 与 `_handwheel_mesh` 4 spokes、bonnet 6 grip ribs 是 visual 内部循环复制（merge 进单 mesh），**不**提为小类 multiplicity 轴。

## 拓扑多样性审计

总组合数：top_guard(4) × valve_closure(3) × base(3) = **36** 基础组合。
叠 cage_bar_count multiplicity（仅 vented_cage_shroud 激活，N∈{3..12} 取 ~6 个有效采样档）：vented_cage_shroud 一格 × 3 × 3 × ~6 N = 54 cage 组合；其余 3 个 top_guard × 3 × 3 = 27 非 cage 组合 → **总 ≈ 81** distinct 拓扑组合（再叠 n_feet_base 的 foot_count{3,4} 次级 × ~6 base=n_feet 组合 → 更多）。

仅 top_guard × valve_closure × base = **36 ≥ 10** 已可过门控；叠 multiplicity 后充裕。

理由：本类拓扑多样性来源充裕——36 基础笛卡尔积 distinct 远超 10。valve_closure 引入 3 种 REVOLUTE joint 拓扑（+Z 旋 handwheel / +Y 压 lever / +Z 拧 bonnet，limit/轴/机构形态各异）；top_guard 含 3 个固定 visual 候选 + 1 个含 REVOLUTE 活动 part 的候选（carry_handle_arch 多一根 `body_to_bow_guard` joint + 2 anchor pads），part/joint count 差异真实；base 含 1-part-1-joint（foot_ring）/ 0-part-0-joint（concave）/ N-part-N-joint（n_feet）三种 part-tree 形态。cage_bar_count 在 vented_cage_shroud 内改 visual 复制件数（真实结构差异，N 决定 cage_bar_{i} 数）。slot_choices 编入三 named 轴 + cage_bar_count（vented 时）+ foot_count（n_feet 时）。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（笛卡尔积近全合法），若 top_guard=vented_cage_shroud 则加权采 cage_bar_count∈[3,12]（小 N 偏多），若 base=n_feet_base 则采 foot_count∈[3,4]；再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除/适配组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 81（含 cage_bar_count N 采样档）。低于 300 的原因：本小类真实结构词汇就是 4 top_guard × 3 valve × 3 base，受单母资产单图约束，cage N 撑开到 ~81；不强行注水（连续 scale 与 palette 不计 slot choice tuple distinct）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 4 个 scale（body_height / body_radius / guard_ring_radius / joint_travel）。全部 `resolve_config` clamp + 每 build 统一应用。`guard_ring_radius_scale` 为 equation（cage/collar 环半径 + cage_bar 放置半径派生跟随）。护罩 encircle 不等式 + bow 摆动 clearance 不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏 valve joint origin（阀杆顶 / 阀块顶）、护罩 encircle 阀、坐地站立、cage_bar_count multiplicity 或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 三 named slot（近全正交），cage_bar_count（vented 时加权小 N 偏多）/ foot_count（n_feet 时），再 uniform 各 scale + palette | slot_choices_for_seed 含三轴 + 条件 N，且与 build 一致 |
| compatibility matrix | (1) 三 named slot 笛卡尔积全合法（36 组合无硬 gate-out，各候选独立挂 body/valve）。(2) cage_bar_count 仅 top_guard=vented_cage_shroud 时激活；其他 top_guard 不采该参数（conditional）。(3) foot_count 仅 base=n_feet_base 时激活。(4) valve_closure 各候选互斥（一次一种机构）；top_guard 各候选互斥；base 各候选互斥。(5) carry_handle_arch 的 bow_guard 摆动需高于阀+护罩 clearance → bow_rise 受 height_scale 不等式约束（resolve 解析）。(6) 大 cage N（≥10）+ 小 guard_ring scale 时 cage_bar 间距收窄 → resolve 校验最小间距，必要回缩 N 上限或 guard_ring 下限 | 无 floating / collision / 护罩穿 body / 机构穿阀 / joint 轴或 origin 错位 / cage bar 重叠 |
| controlled local variation | 4 个 clamped scale，每 build 统一；guard_ring equation 驱动 cage/collar 半径 | 比例变化不破坏 valve joint origin / 护罩 encircle / 坐地 / cage multiplicity / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | 机构动作 / 坐地 / 护罩 encircle / cage N / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| top_guard | 4 | yes | yes | ring_on_struts / solid_neck_collar / carry_handle_arch(REVOLUTE 摆动) / vented_cage_shroud(cage_bar_count 轴) |
| valve_closure | 3 | yes | yes | handwheel(REV +Z) / lever(REV +Y) / bonnet(REV +Z 拧)；每候选 ≥1 非 fixed joint |
| base | 3 | yes | yes | foot_ring(1 part) / concave(0 part) / n_feet(N part, foot_count 次级轴) |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (top_guard, valve_closure, base) 三轴 + cage_bar_count（top_guard=vented_cage_shroud 时）+ foot_count（base=n_feet_base 时）
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 各 scale clamp 到声明范围；guard_ring_radius equation 驱动 cage/collar/struts 半径 + cage_bar 放置半径；护罩 encircle 不等式 + bow 摆动 clearance 不等式在 resolve 内投影 / 回缩
- compatibility matrix / gating：36 基础组合全合法（无硬 gate-out）；cage_bar_count / foot_count conditional 仅在对应候选激活；大 cage N + 小 guard scale 时 resolve 校验 cage_bar 最小间距
- 连续 scale clamp 后不破坏 valve joint origin / 护罩 encircle / 坐地站立 / cage multiplicity / 类别身份
- 关键 joint：handwheel `valve_to_handwheel` REVOLUTE +Z (abs(axis[2])>0.99, limit ±4π, off-axis lug quarter-turn 可检测)；lever `valve_to_lever` REVOLUTE +Y (abs(axis[2])<0.01, limit [0,1.05], 下压 tip 降)；bonnet `valve_to_bonnet` REVOLUTE +Z (limit [0,6π], indicator lug 可检测)；carry_handle_arch `body_to_bow_guard` REVOLUTE +Y (limit ±0.55π, 前后摆)；base `body_to_foot`/`body_to_foot_{i}` FIXED
- captured-fit：element-scoped `allow_overlap`：valve_body↔body_shell（阀座套 neck boss）/ foot↔body_shell（脚环/脚墩套底缘）/ lever↔valve_body（clip hub 卡阀杆）/ bonnet↔valve_body（阀杆顶 nest 进域顶）/ bow_anchor_pad_{i}↔bow_guard_tube（拱端捕获）
- copied objects：cage_bar_{i} 共享 `_cage_bar_geometry` helper、等角 placement、全 FIXED visual；foot_{i} 共享 `_stub_foot_mesh`、等角 `body_to_foot_{i}` FIXED
- grandfather：所有 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 用薄壁矮罐 / Box 占位体当瓶身 → 失类别身份；瓶身必须 LatheGeometry revolve（高 > 直径，域顶 + neck boss）。
- 漏发 brass `valve`（侧出气 spigot 阀体）或 valve_closure 机构 → 退化成无阀容器（混入 can/box），类别身份丢失；valve 是固定骨架，机构是 ≥1 活动件。
- valve_closure joint origin 放在瓶底 / 任意点而非阀杆顶 `(0,0,0.072)` / 阀块顶 `(0,0,0.046)` 真实硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- 机构 rest pose 设成开启 / 下压 / 拧松而非 q=0 闭合 → current-pose 与 viewer 目检不符。
- 护罩（cage/collar/struts）半径太小不 encircle 阀，或太大撞 body 外缘 → encircle 不等式 FAIL；护罩底环须坐 shoulder、顶环高于阀。
- carry_handle_arch 的 bow_guard 摆动时穿阀 / 穿护罩 / origin 漂移 → bow 摆动 clearance 不等式或 origin 检查 FAIL。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice）。
- cage_bar_count 大 N 与小 guard_ring scale 组合致 cage_bar 互相穿插重叠 → 须 resolve 校验最小间距、回缩 N 或 guard_ring。
- concave_recessed_base 仍发射独立 foot part / base joint → 与「base fold 进 body shell」语义冲突（test 断言 `"foot_ring" not in part_names`）。

## 与相邻类别的边界

- 不该混入：**container_can 饮料/食品易拉罐**（薄壁短矮罐 + 拉环顶盖，无阀无护圈，矮宽比例）——理由：gas cylinder 是厚壁高瓶身 + 域顶 + neck 阀机构 + 护圈，高 >> 直径。
- 不该混入：**container_paint_spray 气雾喷漆罐**（细高罐 + 顶部按压喷嘴 actuator + 圆顶盖，无侧出气 brass 阀 + 旋/压/拧机构、无 struts/cage 护罩）——理由：gas cylinder 的阀是侧出气 spigot brass 阀体 + handwheel/lever/螺帽旋压拧机构 + 阀顶护罩。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。10 个 5★ record 全量读取（1 parent + 9 变体）。pattern=mixed：top_guard(4) × valve_closure(3) × base(3) = 36 基础组合，叠 cage_bar_count[3,12] multiplicity ≈81 distinct，远超。valve_closure 主机构槽 3 候选各非 fixed REVOLUTE（旋/压/拧）；top_guard 含 carry_handle_arch 的 REVOLUTE 摆动 bow_guard part；base 三候选 part-tree 形态各异（1/0/N part）；cage_bar_count 由 vented_cage_shroud/cage_n6/cage_n8 三样本证实；palette_style 10 档 colorway（含显式 finish 材质表面维度：glossy_industrial_paint / galvanized_zinc / brushed_steel / matte_powder_coat / weathered_scuffed），palette-only 不计 slot_choice。每个 candidate 均有真实 model.py:Lx-Ly。等待人工审核。|

## 模板实现备注（可选）

- 共享 helper：`_body_mesh(profile, scales)`（含 concave_recessed_base 的内凹底 profile 变体）+ `_valve_mesh()`（固定骨架，全 module 公用）+ `_cage_bar_geometry(bar_r, height)`（cage 复制 helper）+ `_stub_foot_mesh()`（n_feet 复制 helper）。圆瓶身 + 护罩环用 `LatheGeometry`/`TorusGeometry`/`CylinderGeometry`，阀体 + lever + bonnet + stub_foot 用 CadQuery 布尔并集 + `mesh_from_cadquery`，bow_guard 用 `tube_from_spline_points`。
- carry_handle_arch：唯一在 top_guard 引入活动 part 的候选——必须发射 `bow_guard` part + `body_to_bow_guard` REVOLUTE +Y (limit ±0.55π) + 2 个 `bow_anchor_pad_{i}` 固定 visual，pad↔tube element-scoped allow_overlap。
- captured-fit overlap：`run_container_gas_cylinder_tests` 里复制各 record 的 `ctx.allow_overlap`（valve↔body_shell / foot↔body_shell / lever↔valve / bonnet↔valve / bow_pad↔bow_tube）。
- guard_ring equation：`resolve_config` 派生 `GUARD_R = base · guard_ring_radius_scale`，cage_bar 放置半径 + collar/struts 环半径跟随；encircle 不等式 + bow clearance 不等式在 resolve 投影。
- cage_bar_count：`config_from_seed` 仅当 top_guard=vented_cage_shroud 时加权采 N∈[3,12]（小 N 偏多），编进 `slot_choices`；大 N 时 resolve 校验 cage_bar 最小角间距。
- 参考模板：`agent/templates/Container_Jar.py`（同 Container 大类，parallel_children + 固定 named slot + captured-fit grandfather + REVOLUTE/PRISMATIC 机构分支 + resolve clamp 骨架）；`agent/templates/Chair_Folding_chair.py`（Config/ResolvedConfig dataclass + multiplicity 复制循环 + 等角 placement + slot_choices_for_config 报 topology family）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | 骨架 | body + valve（固定）| rec_red-...-5d5b07e2 | `_body_mesh` L43-59 / `_valve_mesh` L62-97 / `body_to_valve` L210-216 | 钢瓶身 lathe + brass 阀体 + 阀座 FIXED（类别身份骨架）|
| S1 | A/B/C | ring_on_struts + handwheel_valve + foot_ring | rec_red-...-5d5b07e2（parent）| `_collar_mesh` L125-141 / `_handwheel_mesh` L100-122 + `valve_to_handwheel` L227-235 / `_foot_mesh` L144-154 + `body_to_foot` L195-201 | 开放护圈基线 + 手轮 REVOLUTE 基线 + 脚环基线 |
| S2 | A | solid_neck_collar | rec_container_gas_cylinder_var_solid_neck_collar | `_neck_collar_mesh` L125-151 + `neck_collar` visual L181 | 实心杯形领圈护罩 |
| S3 | A | carry_handle_arch | rec_container_gas_cylinder_var_carry_handle_arch | `_bow_guard_mesh` L132-160 + `_bow_anchor_pad_mesh` L163-166 + `body_to_bow_guard` REVOLUTE +Y L242-255 | 倒 U 拱提手（活动护罩 part）|
| S4 | A (mult) | vented_cage_shroud (N=4) | rec_container_gas_cylinder_var_vented_cage_shroud | `_cage_bar_geometry` L134-136 / `_cage_ring_mesh` L139-146 / `_cage_bar_mesh` L149-155 + `for i in range(N)` L188-193 | 护笼基线 + cage_bar_count multiplicity 载体 |
| S5 | A (mult N=6) | cage_bar_count=6 | rec_container_gas_cylinder_var_cage_n6 | `_cage_bar_mesh` L135 + `for i in range(N_CAGE_BARS)` L187 (N=6 L129) | cage N=6 多重性样本 |
| S6 | A (mult N=8) | cage_bar_count=8 | rec_container_gas_cylinder_var_cage_n8 | `_cage_bar_mesh` L135 + `for i in range(N_CAGE_BARS)` L198 (N=8 L46) | cage N=8 多重性样本 |
| S7 | B | lever_clip_valve | rec_container_gas_cylinder_var_lever_clip_valve | `_lever_mesh` L101-141 + `valve_to_lever` REVOLUTE +Y L248-256 | 自闭扳手阀（水平轴下压机构）|
| S8 | B | screw_bonnet_cap | rec_container_gas_cylinder_var_screw_bonnet_cap | `_bonnet_mesh` L98-164 + `valve_to_bonnet` REVOLUTE +Z L271-283 | 螺帽防护罩（旋拧密封机构）|
| S9 | C | concave_recessed_base | rec_container_gas_cylinder_var_concave_recessed_base | `_body_mesh` 内凹底 profile L44-66 + 无 foot part L256-261 | 一体内凹碟形底（无独立脚环）|
| S10 | C (mult) | n_feet_base | rec_container_gas_cylinder_var_n_feet_base | `_stub_foot_mesh` L152-165 + `for i in range(N_FEET)` L201-222 | N 短脚墩等角底（foot_count 次级轴）|
