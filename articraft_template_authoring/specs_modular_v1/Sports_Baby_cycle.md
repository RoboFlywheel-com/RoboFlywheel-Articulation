# baby_cycle — modular spec (SPEC_ONLY_DRAFT)

## 元信息
| 项 | 值 |
|---|---|
| slug | `baby_cycle` |
| template path | `agent/templates/Sports_Baby_cycle.py` |
| test path (optional) | `tests/agent/test_baby_cycle_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel_children steering/frame/foot + a multiplicity wheel-loop axis） |

`pattern` 说明：frame 是 root，saddle/steering/wheels 都是挂到 frame（或 steering）的 parallel children；
wheel_arrangement 是一根 `for i in range(n)` multiplicity 轴（共享 `_wheel_part` helper）。foot 与
frame 的 rail/peg/crank 是 module-local 的 `for i in range(2)` 次级复制循环，不暴露为独立 N 轴。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category（parent + 8 variants） |
| source_index_policy | only adopted module sources are indexed below |

读到的 9 个源（全部 rating=5，已 sync 进 `data/records/`）：
- S1 parent `rec_toddler-balance-trike-baby-cycle-white-frame-wit_20260605_165756_379018_4aab549e`
- S2 `rec_baby_cycle_var_quad4`（N=4）
- S3 `rec_baby_cycle_var_inline2`（N=2）
- S4 `rec_baby_cycle_var_crossbar`（diamond frame）
- S5 `rec_baby_cycle_var_twinbeam`（twin-beam deck frame）
- S6 `rec_baby_cycle_var_pedals`（front pedals）
- S7 `rec_baby_cycle_var_footrest`（footrest pegs）
- S8 `rec_baby_cycle_var_tbar`（T-bar）
- S9 `rec_baby_cycle_var_apehanger`（ape-hanger loop bar）

所有 9 个源共用同一套 helper 骨架（`_spin_origin` / `_swept_tube` / `_cyl_between` / `_wheel_part` /
`_fork_mesh` / `_handlebar_mesh`）和同一套 articulation 拓扑：steering REVOLUTE（raked head-tube 轴，
±π/4）+ 每个 wheel 一个 CONTINUOUS roll（local X 轴，effort=2 velocity=20）+ saddle FIXED。

## 核心身份

baby_cycle = 幼儿（toddler）骑乘玩具车：白色管状车架为 root，低矮 step-through / 钻石 / 双梁 deck 车架，
一个软坐垫 FIXED 在车架后段，蓝色把手 + 前叉绕倾斜（raked）头管一起 REVOLUTE 转向，front wheel(s) 是
steering 的 child、rear wheel(s) 是 frame 的 child，全部沿各自轴 CONTINUOUS 滚动。核心成熟域 =
**平衡车（balance bike/trike）** 与可选 **前驱踏板三轮**，车轮总数 2–4。每个 wheel = 黑胎环 + 蓝侧盘 +
中央 hub barrel + 一个 off-axis valve-stem marker（供 AABB spin 检测）。

不该混入：成人自行车（链传动/后驱/曲柄踏板成对前后），电动 / 平衡轮（陀螺/自平衡），推车手柄式幼儿车
（有家长推杆），以及无转向的滑板/scooter（无 raked head tube + 无 steering REVOLUTE）。

## 槽位 + 候选模块表

### Slot A：wheel_arrangement（multiplicity 轴：wheel 总数 N + front/rear split）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| trike_1f2r (N=3) | S1 parent | L298-L330（front_wheel_roll + rear_left_roll + rear_right_roll）；wheel helper L187-L229 | eligible if compatible | 1 前轮挂 fork（trail FRONT_AXLE_Y），2 后轮 splayed 挂 rear axle bridge（±REAR_HALF_TRACK）；基线 |
| quad_2f2r (N=4) | S2 quad4 | L299-L339（`for i in WHEEL_LAYOUT` 循环）；layout L61-L66；shared helper `_build_wheel` L203-L231 | eligible if compatible | 加宽横向前轴 carries 2 前轮（±FRONT_HALF_TRACK，children of steering）+ 2 后轮 = 4 |
| inline_1f1r (N=2) | S3 inline2 | L306-L326（`for i in range(len(wheel_defs))`）；helper L196-L238 | eligible if compatible | 1 前轮挂 fork + 1 中线后轮（centerline rear stub），inline 平衡自行车形 |

> Slot A 即 multiplicity N-sample 轴；候选数 = 已采样的 N 配置 {3,4,2}。模板里全部统一成
> `wheel_{i}` 循环 + 共享 helper（见 Multiplicity 节），N=3 的 splayed-rear 与 N=4 的 dual-front
> 用 front_count/rear_count + half-track 派生表达，不是三段手写。

### Slot B：frame_form

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| step_through_loop | S1 parent | `_frame_mesh` L97-L125（`_swept_tube` 低 U backbone + head + axle bridge + 2 stays）；saddle mount L255-L261 | eligible if compatible | 低单根曲 U backbone，无上管，最易跨坐；基线 |
| crossbar_diamond | S4 crossbar | `_frame_mesh` L109-L151（head+top_tube+down_tube+seat_tube+seat_post+chain/seat stays）；常量 L60-L68；saddle on seat post L282 | eligible if compatible | 闭合钻石侧影：水平 top_tube 横在轮上方 + seat_post 撑坐垫 |
| twin_beam_deck | S5 twinbeam | `_rail_path` L100-L113 + `_build_rail` L114-L117 + `_build_frame_structure` L119-L149 + `_build_deck` L151-L165；`for i in range(2)` rail loop L284-L295；deck plate L297-L302 | eligible if compatible | 两根镜像并行侧 rail（`rail_{i}`）+ 平 deck plate，坐垫坐在 deck 上 |

### Slot C：foot_interface

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| none_balance | S1 parent | （无 foot part；build L232-L332 不含 foot 块） | eligible if compatible | 纯平衡车，脚踩地，无 foot 件；基线 |
| front_pedals | S6 pedals | `_crank_pedal_pair` L107-L160；常量 L51-L56；`for i in range(2)` crank/pedal visuals on front_wheel L379-L394 | eligible if compatible（gated, 见兼容矩阵） | 2 曲柄 180° 相对 + 踏板，作为 visuals 挂 front_wheel，随 front roll joint 一起转（无独立 joint） |
| footrest_pegs | S7 footrest | `_footrest_peg_geometry` L97-L105；`for i in range(2)` peg visuals on frame L264-L275 | eligible if compatible | 2 个固定侧 peg（frame visual，镜像，非活动）供 coasting 时搁脚 |

### Slot D：handlebar_form

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| swept_riser | S1 parent | `_handlebar_mesh` L169-L184（`_swept_tube` 双起伏低 bar）；grips loop L271-L279 | eligible if compatible | 低 swept bar 带两个 rise，直 grips；基线 |
| t_bar_straight | S8 tbar | `_tbar_mesh` L169-L188（straight 横 crossbar cyl + clamp boss）；angled grips loop L279-L293（`for i, sx in enumerate((-1,1))`，命名 `grip_{i}` 而非 grip_left/right） | eligible if compatible | 平水平 T crossbar，grips 略向后 yaw（~12°） |
| ape_hanger_loop | S9 apehanger | `_handlebar_mesh` L169-L192（`_swept_tube` 高 rounded-U）；近距高位 grips loop L280 | eligible if compatible | 高起 cruiser rounded-U loop，grips 高而近身 |

> Slot D 的 part 永远归 steering，所以 bar 始终随 fork 一起转。Slot B/C/D 全部保留 parent 的
> steering REVOLUTE + 每轮 CONTINUOUS roll joints 不变。

## 槽位图（slot graph）

pattern: mixed（frame=root 的 parallel_children + wheel multiplicity 轴）

```
frame (root, Slot B)
 ├─[FIXED  origin≈(0,-0.085,0.10) deck/seat_post/deck-plate 顶面]──> saddle
 ├─[REVOLUTE  pivot=HEAD_BOT  axis=STEER_AXIS(raked, Y-Z 平面) range=±π/4]──> steering (owns Slot D bar+grips+fork)
 │     └─[CONTINUOUS roll  origin=front axle(局部, 减 HEAD_BOT)  axis=(1,0,0)]──> wheel_{i}  (front wheels, Slot A)
 ├─[CONTINUOUS roll  origin=(±REAR_HALF_TRACK 或 0, REAR_AXLE_Y, AXLE_Z)  axis=(1,0,0)]──> wheel_{j}  (rear wheels, Slot A)
 └─ (Slot C) none_balance: 无件 │ front_pedals: crank_{k}/pedal_{k} = front_wheel 的 visuals（随 roll 一起转）│ footrest_pegs: footrest_{k} = frame visuals（固定）
```

接口点位 / joint：
- frame→saddle：mating face = 车架后段 deck / seat_post 顶 / deck_plate 上表面；**FIXED**（无轴）。
  origin 随 Slot B 变（step_through ≈(0,-0.085,0.10)，crossbar=seat_post 顶，twin_beam=deck 上表面）。
- frame→steering：pivot = head tube 下端 HEAD_BOT；轴 = STEER_AXIS（沿 raked head tube，向上）；
  **REVOLUTE** range −π/4..+π/4（effort 4, velocity 4）。steering 内部含 fork 上探入 head tube 的 captured overlap。
- steering→front wheel(s)：interface = fork crown 下的前轴；joint origin 在 steering 局部坐标（减 HEAD_BOT）；
  **CONTINUOUS** roll，axis=(1,0,0)（局部 X），effort 2 velocity 20。front 数 = front_count（1 或 2，对称 ±FRONT_HALF_TRACK）。
- frame→rear wheel(s)：interface = rear axle bridge / 中线 stub；joint origin = world frame 坐标；
  **CONTINUOUS** roll，axis=(1,0,0)，effort 2 velocity 20。rear 数 = rear_count（1 中线 / 2 对称 ±REAR_HALF_TRACK）。
- Slot C front_pedals 不新增 joint：crank/pedal 是 front_wheel 的 visuals，继承其 roll；footrest 是 frame visuals 不动。

互斥 / 派生：Slot A 的 front/rear split 决定 front 是否对称双轮（驱动 `_fork_mesh` 选窄叉 vs 横轴宽叉）
与 rear 是否中线（驱动 `_frame_mesh` 是否出 axle bridge）。Slot C front_pedals 仅在 front_count==1（单前轮）下合法（见兼容矩阵）。

## 每槽位 Module Emits / Interfaces

### Slot A / module trike_1f2r / quad_2f2r / inline_1f1r（统一 wheel multiplicity）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel_{i}`（front_count + rear_count 个），每个含 `_tire`/`_disc`/`_marker` 三 visual | S1 L187-L229 / S2 L203-L231,L299-L318 / S3 L196-L238 |
| internal joints | 每个 wheel 一个 `wheel_{i}_roll` CONTINUOUS，axis=(1,0,0)，MotionLimits(effort=2, velocity=20) | S2 L331-L339 / S3 L318-L326 |
| upstream interface | front wheels parent=steering（origin 减 HEAD_BOT）；rear wheels parent=frame（world origin） | S2 L322-L329 |
| downstream interface | 无（wheel 是叶子）；marker 供 spin 检测 | S1 L216-L223 |

### Slot B / module step_through_loop / crossbar_diamond / twin_beam_deck
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`（root），visual = `frame_tube`（loop/diamond）或 `rail_{i}`+`deck_plate`（twin_beam） | S1 L243-L244 / S4 L131-L151 / S5 L284-L302 |
| internal joints | 无（frame 内全是 visual / compound；twin_beam 的 rail_{i} 仍是 frame 的 visual，不是 joint） | S5 L284-L295 |
| upstream interface | root，无 parent | S1 L243 |
| downstream interface | head tube（HEAD_BOT/HEAD_TOP 给 steering pivot）；rear axle 接口（bridge 或 stub 给 rear wheels）；saddle mount face | S1 L112-L124 |

### Slot C / module none_balance / front_pedals / footrest_pegs
| emits | 描述 | 来源 |
|---|---|---|
| parts | none_balance: 无；front_pedals: `crank_{k}`/`pedal_{k}` 作为 front_wheel 的 visuals；footrest_pegs: `footrest_{k}` 作为 frame 的 visuals | S6 L379-L394 / S7 L264-L275 |
| internal joints | 无（cranks 随 front_wheel roll；footrest 固定） | S6 L376-L394 |
| upstream interface | front_pedals 挂 front_wheel hub disc（boss 连接，captured overlap）；footrest 挂 frame backbone boss | S6 L133-L160 / S7 L97-L105 |
| downstream interface | 无 | — |

### Slot D / module swept_riser / t_bar_straight / ape_hanger_loop
| emits | 描述 | 来源 |
|---|---|---|
| parts | steering 的 `handlebar_bar`/`tbar_crossbar` + `grip_left`/`grip_right` visuals | S1 L169-L184,L271-L279 / S8 L169-L188 / S9 L169-L192 |
| internal joints | 无（bar/grips 是 steering 的固定 visuals） | S1 L268-L279 |
| upstream interface | 挂 steering 局部坐标（减 HEAD_BOT），与 fork stem 同 island | S1 L266-L269 |
| downstream interface | 无（叶子）；随 steering REVOLUTE 一起转 | S1 L285-L295 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| frame_form | enum | step_through_loop / crossbar_diamond / twin_beam_deck | — | choice | deterministic procedural sampler | Slot B 表 |
| foot_interface | enum | none_balance / front_pedals / footrest_pegs | — | choice | sampler；front_pedals 受 front_count==1 gate | Slot C 表 |
| handlebar_form | enum | swept_riser / t_bar_straight / ape_hanger_loop | — | choice | sampler | Slot D 表 |
| palette_style | enum | classic_white_blue / candy_pink_cream / mint_green_natural / sunshine_yellow_red / sky_blue_chrome / charcoal_lime_sport | classic_white_blue | choice | per-seed 抽样，仅改 material rgba 不改拓扑 | 见下 |
| front_count | int | {1, 2} | 1 | conditional | =2 当且仅当 quad 配置；front_pedals 要求 ==1 | S2 L61-L66 / S3 L309-L313 |
| rear_count | int | {1, 2} | 2 | conditional | inline → 1（中线）；其余 → 2（对称） | S1 / S3 |
| wheel_count | int (derived) | [2,4] | 3 | equation | `= front_count + rear_count` | Slot A 表 |
| FRONT_HALF_TRACK | float | [0.080, 0.110] | 0.095 | conditional | 仅 front_count==2 生效；front_count==1 时前轮在中线 | S2 L46 |
| REAR_HALF_TRACK | float | [0.095, 0.130] | 0.115 | conditional | 仅 rear_count==2 生效；rear_count==1 时后轮在中线 | S1 L46 |
| wheel_radius_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 WHEEL_RADIUS；AXLE_Z = WHEEL_RADIUS·scale 保持触地 | S1 L37,L44 |
| (—) | constraint | — | — | equation | `AXLE_Z = WHEEL_RADIUS · wheel_radius_scale`（轮底贴 z≈0） | S1 L44 |
| steer_rake_scale | float | [0.90, 1.10] | 1.0 | independent | 微调 HEAD_TOP/HEAD_BOT Y 差（rake 角）；STEER_AXIS 重算 | S1 L48-L56 |
| frame_length_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 wheelbase（FRONT_AXLE_Y、REAR_AXLE_Y）；saddle/steering origin 跟随 | S1 L42-L43 |
| (—) | constraint | — | — | inequality | `REAR_HALF_TRACK + WHEEL_RADIUS·scale ≤ 半车宽包络`；超出按比例回缩 rear track | 接口 / clearance |
| (—) | constraint | — | — | inequality | front_count==2 时 `2·FRONT_HALF_TRACK ≥ 2·(HUB_RADIUS+gap)` 防双前轮 hub 相撞；违反则回缩或拒采 | S2 L46 / clearance |
| steer_range | float | derived | π/4 | equation | `= π/4`（固定 ±45°，effort 4 velocity 4），不独立采样 | S1 L292-L294 |
| roll_limits | fixed | effort=2, velocity=20 | — | equation | 所有 wheel roll 统一 | S1 L306 |

**palette_style 候选（≥3，目标 4–6；取 6 个，全部基于源观察到的 material set + 真实幼儿车配色族）**：
源里所有 9 个 model 的 material 都是 `frame_white(0.95,0.95,0.96)` + `accent_blue(0.16,0.55,0.80)` /
`hub_blue(0.13,0.48,0.74)` / `grip_blue` + `tire_black(0.10,0.10,0.11)`（pedals 多一个 `crank_steel(0.72,0.73,0.74)`）。
palette_style 在此 material 词表上重映射 frame/accent/hub/grip 颜色（tire 恒黑、marker/steel 跟随 accent），
得到真实存在的幼儿平衡车配色：
1. `classic_white_blue` — 白车架 + 蓝坐垫/把手/轮盘（= 全部源的原配色，baseline）
2. `candy_pink_cream` — 奶白车架 + 糖果粉坐垫/把手/轮盘（女童款）
3. `mint_green_natural` — 薄荷绿车架 + 原木/米色坐垫把手（北欧风）
4. `sunshine_yellow_red` — 黄车架 + 红坐垫/把手（高饱和玩具款）
5. `sky_blue_chrome` — 天蓝车架 + 银/铬把手与轮盘（金属感）
6. `charcoal_lime_sport` — 炭灰车架 + 荧光绿 accent（运动款）

## Multiplicity / Copy Logic

**主轴（唯一模板级 N 轴）：wheel_arrangement**

- count_param：`wheel_count = front_count + rear_count`（front_count∈{1,2}，rear_count∈{1,2}）。
- N_range：total wheels **[2, 4]**（测试偏小：先测 N∈{2,3}；产品全程 {2,3,4}）。front∈{1,2}、rear∈{1,2}；
  source map 提到的 wide-track 3-rear scooter base 未采样，N>4 暂不进域。
- sampling domain（权重）：N=3（1f2r，trike）最常见高频；N=2（inline 平衡车）次之；N=4（quad）较稀。
  建议权重 ≈ {N3:0.5, N2:0.3, N4:0.2}；front/rear split 由 N 推：N3→(1,2)，N2→(1,1)，N4→(2,2)。
- copied object：one wheel = 黑胎环 `wheel_{i}_tire` + 蓝侧盘+hub barrel `wheel_{i}_disc` + off-axis
  valve-stem marker `wheel_{i}_marker`（spin 检测用）。共享 `_wheel_part`/`_build_wheel` helper。
- naming：`wheel_{i}`（i 全局 0..N-1，front 在前 rear 在后）+ `wheel_{i}_roll` joint。
- placement：front wheels = steering 的 child，在 front axle（front_count==2 时对称 ±FRONT_HALF_TRACK，
  ==1 时中线）；rear wheels = frame 的 child，在 rear axle（rear_count==2 时对称 ±REAR_HALF_TRACK，
  ==1 时中线 stub）。所有 wheel 底贴 z≈0（AXLE_Z=WHEEL_RADIUS·scale）。
- joint policy：每个 wheel 独立 CONTINUOUS roll，local X 轴（axle），统一 MotionLimits(effort=2,velocity=20)；
  front wheels parent=steering 故继承转向。
- source/gating：见兼容矩阵；front_pedals 仅 front_count==1。

**次级 copy 循环（module-local，不暴露为 N 轴）**：
- Slot B twin_beam_deck：`rail_{i}` for i in range(2)（镜像 sign=±1），frame 的 visual，无 joint。
- Slot C front_pedals：`crank_{k}`/`pedal_{k}` for k in range(2)（180° 相对），front_wheel 的 visual，随 roll。
- Slot C footrest_pegs：`footrest_{k}` for k in range(2)（镜像），frame 的 visual，固定。
这些都是固定 2 份镜像/对置，不参数化数量，因此不作为独立 multiplicity 轴。

## 拓扑多样性审计

总组合数：Slot B(3) × Slot C(3) × Slot D(3) × Slot A N-samples(3) = 27 × 3 = **81**。
（front_pedals×front_count==2 与 inline×front_pedals 被 gate 掉，仍 >> 10。）

理由：Slot B/C/D 三个轴各 3 个结构不同的 module，乘以 3 个 N 配置，且每个 module 改变 part 集合 /
visual 拓扑 / wheel 数 / joint 数，distinct 拓扑远超 10（即便扣掉少量非法 combo，legal ≈ 75+）。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 先按权重抽 Slot A 的 N（→front_count/rear_count
与 half-track 派生）、再独立抽 Slot B/C/D 的 module，应用兼容矩阵 gate（非法组合 fallback 到
none_balance 或重抽 Slot C），随后抽连续 scale（先 independent：wheel_radius_scale / steer_rake_scale /
frame_length_scale，派生 AXLE_Z 与对称 track，最后 inequality 投影 track/clearance）。
palette_style 独立抽样仅改 material。`slot_choices_for_seed` 必须与 build 实际 choice 一致。
Topology target：1000-seed slot choice tuple distinct 建议 ≥75（受限于 3×3×3×3 离散域；类别天然 combo 上限 81，（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
连续 scale 不计入拓扑 distinct），低于 300 的原因 = 离散 slot 组合上限本就 81，符合本类别结构约束。
regression overrides：none（无已知失败回归；若后续 sweep 暴露 quad×pedal 之类边界，再加 sparse override）。
Controlled local parameterization：初版关键连续 scale = wheel_radius_scale[0.85,1.15] /
steer_rake_scale[0.90,1.10] / frame_length_scale[0.92,1.10] / FRONT_HALF_TRACK[0.080,0.110] /
REAR_HALF_TRACK[0.095,0.130]，全部在 `resolve_config` clamp/派生；AXLE_Z=WHEEL_RADIUS·scale（equation），
double-track clearance（inequality），均不破坏 steering pivot / wheel roll origin / saddle mount / multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | Slot A(N 加权)→front/rear split & track 派生；Slot B/C/D 独立 choice；连续 scale clamp/派生 | slot_choices_for_seed matches build choices |
| compatibility matrix | front_pedals 需 front_count==1（gate，否则 fallback none_balance）；inline_1f1r×front_pedals 不进 combo 域（tippy）；quad_2f2r×ape_hanger 合法仅未必常采 | no floating, collision (dual-front hub clash), axis, max-N, optional-child failures |
| controlled local variation | wheel_radius/steer_rake/frame_length/track scales + clamp/inequality | proportions vary，不破 interface/clearance/joint origin/identity |
| regression overrides | none | previously failed or reviewer-selected only |
| random sweep | seeds 0-49 初查；0-999 成熟度审计 | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A wheel_arrangement | 3 (N 配置) | yes | yes | multiplicity 轴；{N3,N2,N4} |
| B frame_form | 3 | yes | yes | |
| C foot_interface | 3 | yes | yes | front_pedals gated |
| D handlebar_form | 3 | yes | yes | |

## Validator

- slot_choices_for_seed returns implemented module names（frame/foot/handlebar + N 配置）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating prevents illegal combos（front_pedals 仅 front_count==1；双前轮 hub 不相撞）
- optional regression overrides are sparse and justified（none 初版）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params clamped；AXLE_Z=WHEEL_RADIUS·scale 与 track clearance 在 resolve_config 求解
- cross-part scale dependencies (equation/inequality/conditional) resolved in resolve_config，不留到 builder
- critical InterfaceSpec/MatingContract 存在：head-tube pivot(HEAD_BOT)、front/rear axle、saddle mount face
- key joints：steering REVOLUTE axis=STEER_AXIS range ±π/4；每 wheel CONTINUOUS roll axis=(1,0,0) effort2/vel20
- copied objects 遵循命名/放置：`wheel_{i}`(+_tire/_disc/_marker)、`rail_{i}`、`crank_{k}`/`pedal_{k}`、`footrest_{k}`

## Reject cases

1. wheel 总数 < 2 或 > 4，或 front/rear split 不在 {1,2}×{1,2}（越界 multiplicity）。
2. front_count==2 同时选 front_pedals（双前轮无法挂对置曲柄；必须 gate）。
3. 某 wheel 缺 `_marker` 或 marker 在轴上（spin 检测失效）。
4. steering 不是 REVOLUTE，或轴非 STEER_AXIS（raked），或 range 不含 ±π/4（转向失效）。
5. front wheel parent≠steering（前轮不随转向转）或 rear wheel parent≠frame。
6. 任一 wheel 底面 z 明显离地（AXLE_Z 未跟 WHEEL_RADIUS·scale 派生，悬空/陷地）。
7. 双前轮或双后轮 hub 间距过小导致 tire/hub 互穿（track 未满足 clearance inequality）。
8. saddle 非 FIXED 或落在车架外（mount face 随 Slot B 未正确选取）。

## 与相邻类别的边界

- 不该混入 **成人自行车 / 山地车**：那是后驱链传动、成对前后曲柄、对称双叉单前轮单后轮、无幼儿玩具比例；
  baby_cycle 是 toddler 比例平衡/前驱、轮 2–4、把手随叉转。
- 不该混入 **儿童 scooter / 滑板车**：scooter 是站立踏板 + 无坐垫 + 通常无 raked head-tube 完整前叉；
  baby_cycle 必有坐垫 FIXED + steering REVOLUTE。
- 不该混入 **带推杆的幼儿三轮推车（stroller-trike）**：那有家长推杆 + 可能不可转向；本类别无推杆。
- 不该混入 **平衡轮 / 电动平衡车**：无 raked 前叉、无 saddle/handlebar 拓扑。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核。开放点：(1) Slot D 各 variant grip 命名不一致——parent/apehanger 用 `grip_left`/`grip_right`，tbar 用 `grip_{i}`（i=0/1），模板需统一命名；(2) front_pedals 是否也允许 front_count==1+rear_count==1（inline）组合——source map 将其列为"separately sampled, not as combo"，建议默认 gate 掉 inline×pedals；(3) palette_style 的 mint/yellow/chrome/lime 为真实配色推断，rgba 由模板按 material 词表落实，源里仅观察到 white/blue/black/steel。 |

## 模板实现备注（可选）

- 全部源共享 `_spin_origin`/`_swept_tube`/`_cyl_between`/`_wheel_part`(`_build_wheel`)/`_fork_mesh`/
  `_handlebar_mesh` helper；模板应统一成一套 helper + slot-dispatch，wheel 用 `wheel_{i}` 单循环（参照 S2/S3）。
- captured-pin / seated overlaps 需 element-scoped allow_overlap：frame↔saddle、frame↔steering（叉入头管）、
  steering↔front wheel（叉腿夹胎+轴）、frame↔rear wheel（后轴桥入 hub bore）；quad 把 front/rear overlap 各按轮复制；
  pedals 增 front_wheel↔crank boss overlap；footrest 增 frame↔peg boss overlap。
- front_count==1 时 `_fork_mesh` 用窄双叶 + 短轴（S1 L159-L165）；==2 时用 splayed 叶 + 横轴（S2 L171-L181）。
- rear_count==1 时 `_frame_mesh` 不出 axle bridge/stays，rear wheel 走中线 stub（S3）；==2 时出 bridge + 2 stays（S1 L114-L124）。
- Slot C front_pedals gated 到 front_count==1；inline×front_pedals 与 quad×ape_hanger 默认不进 seed 域（按 source map 排除项）。
