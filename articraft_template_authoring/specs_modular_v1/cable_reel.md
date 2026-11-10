# Modular Spec — cable_reel (Electrical_Wiring / Cable reel)

## 元信息
| 项 | 值 |
|---|---|
| slug | `cable_reel` |
| registry key | `Electrical_Wiring_Cable_reel` |
| template path | `agent/templates/Electrical_Wiring_Cable_reel.py`（KEY-named 文件，stem-named 函数 build_cable_reel 等） |
| test path (optional) | `tests/agent/test_cable_reel_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（grounded frame → 1 spinning reel child → optional spinning grip child；flange/drive 并联 emit；flange 特征数为 multiplicity） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this category（2 origins 002/001 + 5 forks） |
| source_index_policy | only adopted module sources are indexed below |

源简写：S_A=cream 实心侧板落地卷盘(002, rec_...ea686860)；S_B=orange 开笼钢架(001, rec_...83201f3e)；
S_CH=rec_cable_reel_var_closed_housing；S_SP=rec_cable_reel_var_spoked_flange；
S_MO=rec_cable_reel_var_motorized_drive；S_WB=rec_cable_reel_var_wall_bracket；S_WC=rec_cable_reel_var_wheeled_cart。

关键共识：drum barrel + flange 盘 + hub 全用 圆 annular mesh(ExtrudeWithHolesGeometry) + torus rim（绝不 Box 盘，规则③）。
缠绕电缆取 单参数螺旋 spline tube（S_A L231-252 的方式，优于 S_B L387-399 的 31 个 torus 逐圈）。自旋轴 = X。

## 核心身份

一台电缆/水管卷盘：一个落地/壁挂/推车 frame（FIXED 根）承载一个绕 X 轴自由旋转的 reel
（圆 drum barrel + 两 flange 盘 + hub + 缠绕电缆 helix），可选一个手摇曲柄，曲柄端可带一个自旋 grip。
drum-spin 关节是每个 frame 形态都必须存在的 主 CONTINUOUS 关节；free grip 是次 CONTINUOUS 关节。
邻类边界：不是裸 spool（必须有 frame + drum barrel + spin 关节）；不是 winch/绞盘（无绞索张力棘轮语义）；
不是纯软管 hose cart（保留 outlet/socket/terminal/label 电气身份细节）。

## 槽位 + 候选模块表

### Slot A：frame_form（① 骨架 + ③ 主体形态家族 / Primary Form Family；grounded `frame` part）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `solid_stand` | forked_anchor | S_A | L109-166 | eligible if compatible | 两块实心侧板(ExtrudeWithHoles 轻量孔) + skid 双轨 base + 4 rubber 脚 + 4 uprights；Planar Boundary Form |
| `open_cage` | forked_anchor | S_B | L67-121, L159-246 | eligible if compatible | 两块三角减重开孔侧 cheek + 顶提手槽 + N tie-rod 笼 + 前 base rail + 脚；Macro Surface Construction |
| `closed_housing` | forked_anchor | S_CH | L118-250 | eligible if compatible | 前/后 圆 annular 壳板(轴承孔+出线槽) + 圆柱 rim 壁把 drum 全包 + 2 立柱脚；Volumetric Envelope Form |
| `wall_bracket` | forked_anchor | S_WB | L73-97, L134-221 | eligible if compatible | 一块平 wall plate + 两梯形 A-bracket 前伸到 bearing saddle 托轴，无落地 base；Planar Boundary Form |
| `wheeled_cart` | forked_anchor | S_WC | L120-315 | eligible if compatible | solid 侧板 + skid base + 2 wheel(cyl+tire torus)+cross-axle + trolley 推手；在 solid_stand 骨架上加 part（轮/推手）→ ① 骨架变化 |

degrade 说明：frame_form 有 5 个 source-backed candidate，是本类主形态多样性所在。mount(skid/wall/wheeled) 与 frame 高度耦合
（wall_bracket 无落地 base、closed_housing 自带脚、wheeled_cart 在 solid 上加轮），按 AUTHORING §B「不能共享 mating 面的两轴属同一 slot 的候选」
把 mount 折入 frame_form，不设独立 mount slot（避免 4-slot 的 mating-seam/allow_overlap 爆炸）。

### Slot B：flange_form（② reel 侧盘形态 / ③ Primary Form Family of the reel cheek；emit 到 `reel` part）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `solid_disc` | forked_anchor | S_A / S_B | S_A L190-224 / S_B L378-383 | eligible if compatible | 实心 annular 盘 cheek + rolled-lip torus + N flange bolt 螺栓圈；Planar Boundary Form |
| `spoked_disc` | forked_anchor | S_SP | L88-121, L245-283 | eligible if compatible | hub ring + rim ring + N radial spoke（annular sector 挖空）+ N spoke bolt；Macro Surface Construction |

degrade-to-2 理由：5 星池中 flange 仅两种结构形态（实心 vs 辐条），S_B 黑盘只是换色不算新 candidate。
主形态多样性由 Slot A(5) 承载；本 slot 满足 report-only ≥2 即可。

### Slot C：drive_type（④ 驱动 + ① 骨架：是否有第二自旋关节；emit 到 reel(+crank_grip)/frame）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `crank_free_grip` | forked_anchor | S_A | L296-341 | eligible if compatible | reel 上 crank_arm(tube)+hub_neck+root_boss+pin+washer；独立 crank_grip part(sleeve+rib+cap) 经 CONTINUOUS 关节挂 pin → 第二自旋关节 |
| `crank_fixed_knob` | forked_anchor | S_B | L426-444 | eligible if compatible | reel 上 crank_arm(box)+crank_peg+crank_knob 全熔进 reel，无独立 part、无第二关节 |
| `motorized` | forked_anchor | S_MO | L377-530, L582-602 | eligible if compatible | frame +X 侧 motor_body+gearbox+output_shaft+mount_plate+terminal_box；reel 侧 drive_gear+N gear_tooth；无曲柄无 grip 关节 |

## 槽位图（slot graph）

pattern: mixed（1 grounded frame + 主 spin 子 + 可选 grip 子；flange/drive 并联 emit）

frame_form(A, grounded root, FIXED to world)
  ├─ _emit_axle_hardware(frame): 两 bearing_race + axle_shaft/stub + nuts （固定 X 接口，跨所有 A 统一）
  ├─ [drive=motorized] motor+gearbox emit 到 frame(+X 侧)
  ├──[frame_to_reel CONTINUOUS axis=+X origin=(0,0,AXLE_Z) captured-journal grandfathered(mating 省略)]──> reel
  │      ├─ reel core: drum_core + hub_collar + hub_neck + wound_cable helix + outlet_block
  │      ├─ flange_form(B): 两侧 cheek 盘（solid/spoked）
  │      └─ drive(C) reel 侧件: crank_arm/pin/washer 或 drive_gear+teeth
  └──[reel_to_crank_grip CONTINUOUS axis=+X origin=crank_pin]──> crank_grip  （仅 crank_free_grip）

接口点位：
- frame_to_reel：origin 在 axle 中心线 (0,0,AXLE_Z)；parent 硬件=bearing_race/axle_shaft（axle 对称中心线，满足 articulation-origin honesty），child 硬件=drum_core（reel-local 原点，对称中心线）。captured journal → mating 省略、grandfathered、element-scoped allow_overlap。
- reel_to_crank_grip：origin=crank_pin 端；child grip 在 grip-local 原点放 grip_collar 破面锚。captured pin → mating 省略、grandfathered、element-scoped allow_overlap。
- flange/drive 为并联 emit（同 watermill spokes/wheel_type emit 到 wheel），不产生跨-slot chain 关节。

互斥/可选：drive=crank_free_grip 才有 crank_grip part 与第二关节；motorized 才有 frame motor 组 + reel drive_gear。frame_form 全部与任意 flange/drive 兼容（统一 axle 接口保证）。

## 每槽位 Module Emits / Interfaces

### Slot A / solid_stand
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame: base_rail_{0,1}、rubber_foot_{0..3}、rail_upright_{0..3}、{front,rear}_side_plate(ExtrudeWithHoles) | S_A L112-157 |
| internal joints | 无（全 parent visual） | — |
| downstream interface | 统一 axle 接口 | S_A L157-165 |

### Slot A / open_cage
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame: {front,rear}_side_plate(三角孔+顶提手 ExtrudeWithHoles)、tie_rod_{0..N-1}(+cap)、front_base_rail、front_foot_{0,1} | S_B L67-121,L159-246 |
| downstream interface | 统一 axle 接口 | S_B L213-225 |

### Slot A / closed_housing
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame: front_shell/rear_shell(圆 annular 壳+轴承孔+出线槽)、housing_rim(圆柱壁)、housing_seam_ring、base_foot_{0,1}+base_plate | S_CH L118-250 |
| downstream interface | 统一 axle 接口 + rim 内径 > drum 外径 | S_CH L193-201 |

### Slot A / wall_bracket
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame: wall_mounting_plate、a_bracket_{0,1}(梯形板)、bearing_saddle_{0,1}、wall_bolt_{i}、grounding_lug | S_WB L73-97,L134-221 |
| downstream interface | 统一 axle 接口（saddle 托 race）；无落地 base | S_WB L189-221 |

### Slot A / wheeled_cart
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame: base_rail、rail_upright、{front,rear}_side_plate + cross_axle_bar、wheel_rim_{0,1}(Cyl)、wheel_tire_{0,1}(torus)、trolley_post_{0,1}(tube)、trolley_grip_bar | S_WC L120-315 |
| downstream interface | 统一 axle 接口 | S_WC L286-301 |

### Slot B / solid_disc（emit 到 reel）
| emits | 描述 | 来源 |
|---|---|---|
| parts | {front,rear}_spool_cheek(annular_yz 实心)+{front,rear}_rolled_lip(torus)+flange_bolt_{i}(N) | S_A L190-224 |

### Slot B / spoked_disc（emit 到 reel）
| emits | 描述 | 来源 |
|---|---|---|
| parts | {front,rear}_spool_cheek(spoked_disc_yz: hub ring+rim ring+N sector 挖空)+rolled_lip+spoke_bolt_{i}(N) | S_SP L88-121,L245-283 |

### Slot C / crank_free_grip
| emits | 描述 | 来源 |
|---|---|---|
| parts(reel) | crank_arm(tube)、front_hub_neck、crank_root_boss、crank_pin、crank_washer | S_A L296-312 |
| parts(new) | crank_grip part: rubber_sleeve、grip_rib、end_cap、grip_collar(破面锚) | S_A L314-322 |
| joints | reel_to_crank_grip CONTINUOUS axis=+X origin=pin | S_A L333-341 |

### Slot C / crank_fixed_knob
| emits | 描述 | 来源 |
|---|---|---|
| parts(reel) | crank_arm(box)、front_hub_neck、crank_peg、crank_knob（全熔进 reel，无独立 part、无第二关节） | S_B L426-444 |

### Slot C / motorized
| emits | 描述 | 来源 |
|---|---|---|
| parts(frame) | motor_mount_plate、gearbox_housing、gearbox_output_shaft、shaft_bearing_collar、motor_body、motor_fin_{i}、motor_end_bell、motor_terminal_box、motor_nameplate | S_MO L382-530 |
| parts(reel) | front_hub_neck、drive_gear(annular)、gear_tooth_{i}(N=16) | S_MO L582-602 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| frame_form | enum | solid_stand / open_cage / closed_housing / wall_bracket / wheeled_cart | — | choice | deterministic sampler | Slot A |
| flange_form | enum | solid_disc / spoked_disc | — | choice | deterministic sampler | Slot B |
| drive_type | enum | crank_free_grip / crank_fixed_knob / motorized | — | choice | deterministic sampler | Slot C |
| flange_feature_count | int(N) | [4,8]（solid=bolt 圈；spoked=辐条） | 6 | independent | 加权采样(小 N 偏多)、clamp | S_SP L279-283 / S_A L220-224 |
| palette_style | enum | 见 §视觉多样性 ⑥（6 个） | safety_cream | choice | rng.choice(PALETTE_STYLES) | 全源材质 |
| reel_radius_scale | float | [0.90,1.10] | 1.0 | independent | 均匀采样后 clamp；uniform-about-axle | — |
| drum_len_scale | float | [0.92,1.08] | 1.0 | independent | 缩放 drum 轴向长度 + cheek 间距 + helix 跨度（联动） | — |
| (—) | constraint | — | — | inequality | flange 外径(0.232·scale) < housing rim 内径(0.262·scale)；sector 角宽 2π/N−spoke_angle>0（N≤8 恒满足） | 接口/clearance |

连续尺寸采样契约：先采 independent(reel_radius_scale、drum_len_scale)，无 equation 从属尺度，inequality 由 clamp(N≤8、scale∈[0.9,1.1]) 恒满足，全部在 resolve_config 求解。

### 7.5 编译预算 / compile budget（必填）
自报 ≤14s/seed（依据：mesh 卷积类模板典型 5-20s；每 seed 只建 1 frame_form + 1 reel，无重布尔雕刻，全 ExtrudeWithHolesGeometry/TorusGeometry/tube_from_spline_points，不用 cadquery boolean）。
分档 tessellation：drum/cheek annular segments ≤72，小 torus tubular ≤48，helix radial_segments=12、samples_per_segment=2、turns≤18；N 个小件复用 primitive。sweep --compile-timeout 120（watchdog）。

## Multiplicity / Copy Logic

一根 multiplicity 轴：flange_feature_count N。
- count_param=flange_feature_count；N_range=[4,8]（产品域；辐条/螺栓常见 4-8，>8 视觉过密罕见）。
- sampling domain：权重 1/(1+|N-6|)（6 偏多、4/8 稀），下游一次加权采样、编进 slot_choices 为 ("flange_n", f"n{N}")、clamp[4,8]、sweep 上限 8。
- copied object：solid_disc → N flange_bolt_{i} 均布螺栓圈(S_A L220-224)；spoked_disc → N spoke(sector 挖空,S_SP L111-118)+N spoke_bolt_{i}。
- naming/placement：for i in range(N)、name_{i}、角 2π·i/N、共享 helper、统一 Rule 1 FIXED-visual（无 per-bolt 关节）。
- source/gating：N≤8 时 sector 角宽恒 >0；无非法值。

其余重复子件（tie_rod、foot、upright、wall_bolt、motor_fin、gear_tooth）for 循环发射、非模板级可变数量，不单列 multiplicity 轴。

## 视觉多样性 6 轴考察

| 轴 | 判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | frame_form 加/减 part（轮+推手/壳体/壁托）；drive_type 决定第二自旋关节存在与否（crank_free_grip=2 关节 vs crank_fixed_knob/motorized=1 关节）。全 forked_anchor：S_A/S_B/S_CH/S_WB/S_WC/S_SP/S_MO |
| └ multiplicity | 同构件 ×N | 有 | flange_feature_count N∈[4,8]，见 §8 |
| ② 关节类型 | 图不变换 type/轴 | 有(受限) | 主 frame_to_reel 恒 CONTINUOUS +X（身份=自由自旋；S_B L461-470 CONTINUOUS，S_A L324 REVOLUTE 归一为 CONTINUOUS）；次 reel_to_crank_grip CONTINUOUS +X 仅 crank_free_grip 出现——存在性变化由 ① drive 承载，两态(有 grip/无 grip)都在 sweep 出现 |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | frame_form=登记进 slot_choices 的 ③ slot：Planar(solid_stand/wall_bracket)、Macro Surface(open_cage)、Volumetric Envelope(closed_housing)、便携推车(wheeled_cart)；reel flange_form：Planar(solid_disc) vs Macro Surface(spoked_disc)。全 forked_anchor |
| ④ 表面装饰 | 叠加表面细节/改数 | 有 | rating_label/warning_label/brand 条、rolled-lip torus、concentric recess ring、housing_seam_ring、motor_nameplate；均写宿主 part visual、贴宿主面（cheek recess 随 cheek 半径、rim seam 随 rim 半径）；record_only。装饰数随 flange_feature_count |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | reel_radius_scale[0.90,1.10]、drum_len_scale[0.92,1.08]。关节行程：frame_to_reel CONTINUOUS 整圈无穿模；reel_to_crank_grip CONTINUOUS 整圈无穿模。motion_test_plan：harness_motion_qc sampled collision({0,±90°,180°}) + targeted ctx.pose 证 reel/grip 旋转位移；captured-journal/pin 用 element-scoped allow_overlap，非 sampled-pose exemption |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted-metal / molded-plastic / galvanized-steel / rubber / brass；配色 6：safety_cream、safety_orange、industrial_yellow、graphite_black、galvanized_raw、hose_reel_red（材质大类覆盖 ≥ceil(0.5×6)=3 ✓）。source: S_A cream L97-105 / S_B orange L148-157 / S_WB grey |

收尾自检：batch 0-9 需肉眼见 ≥3 frame_form、solid+spoked flange、crank/motorized、多种 palette；关节整圈不穿模。

## 拓扑多样性审计

总组合数：frame_form(5) × flange_form(2) × drive_type(3) × N(5) = 150。


seed_domain_policy：procedural_first。
Procedural Sampling / Sweep Plan：config_from_seed(seed)=random.Random(seed) 独立 rng.choice 采 frame_form/flange_form/drive_type/palette_style + 加权采 N + 均匀采两 scale；seed=0 不特殊。无 compatibility gate（统一 axle 接口 + N≤8 保证全组合合法），无 regression override。1000-seed slot choice tuple distinct 预计 按 ≥300 report-only 口径观察。
Controlled local parameterization：reel_radius_scale[0.90,1.10]、drum_len_scale[0.92,1.08]，resolve_config clamp；uniform-about-axle 缩放不破 bearing/hub 接口、cheek↔side-plate 间隙、joint origin、multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 frame→flange→drive→N；独立 rng.choice + 加权 N | slot_choices_for_seed == build 选择 |
| compatibility matrix | 全 150 组合合法（统一 axle 接口）；N≤8 sector 恒有效 | 无 floating/collision/axis/max-N 失败 |
| controlled local variation | 两 scale clamp；uniform about axle | 比例变而不破接口/间隙/关节 |
| regression overrides | none | — |
| random sweep | 0-15 fast → 0-35 final → corner | contract failures; axis_realization |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| frame_form | 5 | yes | yes | ③ 主形态 slot |
| flange_form | 2 | yes | no | degrade-to-2（已说明） |
| drive_type | 3 | yes | yes | |

## Validator
- slot_choices_for_seed 返回已实现 module 名（frame_form/flange_form/drive_type/flange_n）
- config_from_seed 对所有普通 seed（含 0）用 deterministic procedural sampling
- 无非法组合（统一 axle 接口 → 全兼容）
- 无 regression override
- 连续 scale 在 resolve_config clamp，不破 interface/clearance/joint origin/multiplicity
- 关键关节：frame_to_reel=CONTINUOUS axis=(1,0,0)；crank_free_grip 时 reel_to_crank_grip=CONTINUOUS axis=(1,0,0)
- captured journal/pin overlap 用 element-scoped allow_overlap（不用宽 part 级）
- 复制件 flange_bolt/spoke/gear_tooth 遵守 name_{i} + 均布 + 共享 helper

## Reject cases
- flange/drum/hub 用 Box 盘而非圆 annular mesh（违反规则③）→ 拒
- 缠绕电缆用 31 离散 torus 而非单 helix spline tube → 拒
- frame_to_reel 关节缺失/非 X 轴/退化成 FIXED（无自旋）→ 拒
- crank_free_grip 无独立 grip part/无第二关节 → 拒；motorized 仍留手曲柄 → 拒
- 侧板/壳体 bearing 区与 reel hub 无对齐 → hub collar 悬空 island → 拒
- crank/grip sweep 整圈撞 frame（未统一 axle 接口导致 X 位错）→ 拒
- 装饰 label/recess 常数半径贴缩放/收锥面悬空（违反规则④）→ 拒
- closed_housing rim 内径 < flange 外径（drum 穿 rim）→ 拒

## 与相邻类别的边界
- 不该混入：裸 spool / bobbin（缺 frame + spin 关节）——必须有 grounded frame + 自旋 reel。
- 不该混入：winch / capstan 绞盘（钢缆张力绞拉、棘轮锁）——本类 free-spin 电缆存放，不建棘轮锁。
- 不该混入：纯软管 hose reel——保留 outlet_block/socket/terminal/label 电气身份。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | frame_form 折并 mount（5 candidate）；flange degrade-to-2 已说明；captured-journal/pin grandfathered。 |

## 模板实现备注（可选）
- 共享 helper：circle_profile/slot_profile/offset_profile/map_profile_extrusion_to_yz/annular_yz/plate_yz/torus_around_x/add_x_cylinder/spoked_disc_yz（全部来自源码，逐字复用）。
- _emit_axle_hardware(frame) 单点定义 bearing_race/axle_shaft/stub/nuts 的固定 X 接口，跨所有 frame_form 复用（Contract 3c 单一来源）。
- _emit_reel_core(reel) 单点定义 drum/hub_collar/hub_neck/wound_cable/outlet_block。
- captured overlap 元素级：(frame.axle_shaft, reel.front_hub_neck)、(frame.front_bearing_race, reel.front_hub_neck)、(frame.axle_shaft, reel.crank_root_boss/crank_arm)、(reel.crank_pin, grip.rubber_sleeve/end_cap)。
- frame_to_reel 与 reel_to_crank_grip 均 grandfather（mating 省略，captured journal/pin）。
