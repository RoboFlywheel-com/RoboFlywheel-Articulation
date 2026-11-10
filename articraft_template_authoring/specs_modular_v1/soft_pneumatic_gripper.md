# Modular Spec — Robotics / Soft pneumatic gripper

## 元信息
| 项 | 值 |
|---|---|
| slug | `soft_pneumatic_gripper` |
| template path | `agent/templates/soft_pneumatic_gripper.py` |
| test path (optional) | `tests/agent/test_soft_pneumatic_gripper_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel_children + multiplicity） |

`pattern` 说明：一个接地 `manifold`（气动歧管/安装根）作为 chassis，N 根**并行子件**软气动手指以独立 REVOLUTE 弯曲关节挂到它上面（parallel_children）；`finger_count` 是主 multiplicity 轴。base / finger form / actuation mechanism 三个离散 slot 都不是串链，而是共享同一个 `manifold` 父 + 每个 finger station 的 mating 接口。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (2 origins + 7 forks) |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

Soft pneumatic gripper = 一个末端执行器，其抓取件是**柔性、气压驱动的硅胶波纹管/气动执行器手指**，挂在一个刚性气动歧管 / 安装板上；手指在充气时向内弯曲以包裹易碎或不规则物体。物理构成永远是：刚性 manifold（路由气路 + 承载手指）+ ≥2 根 compliant bellows 手指（非刚性连杆）+ 可见气路（软管、倒钩接头、弯头）+ 每根手指至少一条真实的非固定内弯关节（REVOLUTE 近似软 curl）。

不该混入：刚性平行夹爪（rigid parallel-jaw）、真空吸盘夹爪、腱驱动刚性多连杆机械手、颗粒阻塞（jamming）夹爪——这些没有 compliant 充气波纹手指。

## 槽位 + 候选模块表

三个源支撑离散 slot：`base_manifold`（①骨架 + support 根）、`finger_form`（③主体形态家族）、`actuation_mechanism`（②关节机构）；外加 `finger_count` multiplicity 轴（§8）。所有 slot 都并行挂到同一 `manifold` 父；finger form 与 mechanism 通过每个 finger station 的 hinge/mating 接口和 `model.meta["spg"]` 发布的 station 表连接。

### Slot A：base_manifold（① 骨架 / support 根，接地 root part `manifold`）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| crossed_rail_radial | forked_anchor(origin) | rec_robotics__soft_pneumatic_gripper__001 | L83-L168 | eligible if compatible | 冲孔矩形安装板(ExtrudeWithHolesGeometry mesh) + central_boss + air_manifold_block + 十字滑轨 rail_x/rail_y + slot_x/slot_y + standoff/cap_screw + 每 station yoke_cheek/yoke_bridge/hinge_pin/fixed_elbow/air_tube；radial 站位 yaw=2π·idx/N |
| clevis_frame_opposing | forked_anchor(origin) | rec_robotics__soft_pneumatic_gripper__002 | L21-L155 | eligible if compatible | 机加工铝框架(cadquery `_cq_box` union: 顶板+standoffs+两 actuator block+clevis cheeks+中央气动体) mesh_from_cadquery + screw/hex/port/barb 圆细节 + fixed_air_tube 样条管 + swivel_socket；opposing 两 station (x=±) |
| wrist_flange_radial | forked_anchor | rec_soft_pneumatic_gripper_var_base_wrist_flange | L84-L172 | eligible if compatible | 圆 ISO-9409 手腕法兰盘(ExtrudeWithHolesGeometry 圆盘 + 中央 pilot 孔 + 螺栓圆 flange_bolt_{i} FIXED 装饰) + central_boss + air_manifold_block + 每 station elbow_boss/yoke/hinge_pin/fixed_elbow/air_tube；radial 站位 |
| inline_beam | forked_anchor | rec_soft_pneumatic_gripper_var_skeleton_inline | L84-L214 | eligible if compatible | 单根长 manifold 梁(beam + beam_slot) 沿 +X + 加长冲孔板 + central_boss + air_manifold_block + standoff；每 station 沿 x 等距 (x0+idx·pitch, y=0) 的 yoke/hinge_pin/elbow/air_tube；linear 站位 yaw=0 |

### Slot B：finger_form（③ 主体形态家族 / Primary Form Family；per-finger 静态几何）

| module_name | source_type | form_subtype | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| corrugated_oval | forked_anchor(origin) | Volumetric Envelope Form | rec_robotics__soft_pneumatic_gripper__001 | L38-L64 | eligible if compatible | `_finger_bellow_geometry`：内 web box + 8 层堆叠 oval CylinderGeometry(32seg,scale 1.10×0.58) 压力腔 + Sphere 远端 pad，MeshGeometry.merge，读作手风琴波纹 |
| ribbed_fin_pneunet | forked_anchor(origin) | Macro Surface Construction | rec_robotics__soft_pneumatic_gripper__002 | L55-L66 | eligible if compatible | `_finger_shape`：cadquery base pad + 竖直 body + 5 层外凸 ribbed fin box(fillet) + 圆 tip cap，mesh_from_cadquery，读作 PneuNet 外肋气室 |
| fiber_cylinder | forked_anchor | Volumetric Envelope Form | rec_soft_pneumatic_gripper_var_form_fiber_cylinder | L38-L106 | eligible if compatible | `_finger_bellow_geometry`(平滑锥柱 12 薄片切成 taper + Sphere pad) + `_fiber_wrap_mesh`(2.5 圈螺旋 spline tube 纤维缠绕)，读作 McKibben/PneuFlex 纤维增强光滑执行器 |

三个 candidate 保持**同一 per-finger part tree**（actuator_base Box + soft_neck Box + `bellow` mesh visual + 表面装饰），**同一 upstream 接口**（actuator_base 在 hinge station 被 hinge_pin 捕获），只改变 `bellow` 的可识别几何形态原型 → 合法 ③ 结构差异（AUTHORING §B / §A Rule 3）。

### Slot C：actuation_mechanism（② 关节 / 机构；per-finger 运动学）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| single_swivel | forked_anchor(origin) | rec_...__001 / rec_...__002 | L171-L245 / L155-L202 | eligible if compatible | 每 finger 一条独立内弯 REVOLUTE `manifold_to_finger_{idx}`(axis 切向, [0,upper]) + 一个 `hose_connector_{idx}` swivel 子件(barbed_port/port_collar/hose_stub) REVOLUTE `finger_to_connector_{idx}`(±swivel) |
| multi_segment | forked_anchor | rec_soft_pneumatic_gripper_var_mechanism_multisegment | L70-L82,L231-L253 | eligible if N≤4 | 在 single_swivel 基础上，每 finger 追加 `finger_{idx}_tip` 远端段(同 form 的 tip 几何) + 串联 REVOLUTE `finger_{idx}_knuckle`(同向内弯) 做 progressive curl |
| span_carriage | forked_anchor | rec_soft_pneumatic_gripper_var_mechanism_span_prismatic | L69-L80,L206-L247 | eligible if N==2 | 每 jaw 插入 `finger_carriage_{idx}` 滑块(cadquery dovetail)：manifold→carriage PRISMATIC `manifold_to_carriage_{idx}`(沿宽度轴, [0,~0.03]) 做 span 调节；finger bend 关节重挂到 carriage 上；仍带 hose swivel |

硬约束满足：base 4 个、finger_form 3 个、actuation_mechanism 3 个 candidate（均 ≥2，slot A/主形态 ≥3）。每个 candidate 结构不同且 source-backed，非 re-skin。size/color/decoration-only 差异不作 candidate（见 §8.5 ④⑤⑥ record_only）。

## 槽位图（slot graph）

pattern: mixed（parallel_children + multiplicity）

```
                 base_manifold (root `manifold`)
                         │  publishes model.meta["spg"]: stations[(x,y,yaw,bend_z,axis)], n_fingers, arrangement, hinge_pin names, support_ref
       ┌─────────────────┼───────────────────────────────┐
       │ (parallel children, ×N stations)                 │
 finger_form                                        actuation_mechanism
  builds N × finger_{idx}                            builds joints + mechanism parts:
  (actuator_base+soft_neck+bellow[form])              - bend REVOLUTE manifold(或 carriage)→finger_{idx}  [切向轴, 0..upper(N)]
  (+ N × finger_{idx}_tip 若 multi_segment)           - swivel REVOLUTE finger_{idx}→hose_connector_{idx}
  NO joints (静态几何)                                 - knuckle REVOLUTE finger_{idx}→finger_{idx}_tip  (multi)
                                                       - PRISMATIC manifold→finger_carriage_{idx} (span, N==2)
```

- slot 顺序：base_manifold → finger_form → actuation_mechanism（`assemble` 顺序遍历）；后两个 slot **不声明 upstream 接口**（抑制自动 chain joint），改为读 `ctx.upstream_interface.part_name`（=`manifold`）与 `model.meta["spg"]`，各自 emit 自己的 part/joint，并把 body 接口 re-export 成 downstream（同 `water_filter_pump` parallel-children 写法）。
- 跨 slot 接口点位：每个 finger station 的 hinge_pin（`manifold` 上，(x,y,bend_z)）= bend REVOLUTE 的 pivot；actuator_base 捕获 hinge_pin（captured-pin，element-scoped `allow_overlap`）。span 情况下 carriage 的 dovetail 舌插入 manifold 轨槽（PRISMATIC，grandfather）。
- 跨 slot joint type/axis/range：bend REVOLUTE 切向轴 [0, upper(N)]；swivel REVOLUTE ±0.30；knuckle REVOLUTE 同向 [0,0.50]；carriage PRISMATIC 宽度轴 [0,0.030]。
- 互斥/gating：span_carriage 需 N==2，否则降级 single_swivel；multi_segment 需 N≤4，否则降级 single_swivel（见 §9 compatibility matrix）。

## 每槽位 Module Emits / Interfaces

### Slot A / module base_manifold（任一 candidate）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `manifold`（root，唯一接地件） | S1/S2/S3/S4 |
| visuals | 板/框/法兰/梁 + central_boss + air_manifold_block + 每 station yoke_cheek/yoke_bridge/hinge_pin/fixed_elbow/air_tube（+ crossed_rail:rail_x/y,slot；wrist_flange:flange_bolt_{i};inline:beam/beam_slot） | S1 L83-168 / S2 L30-155 / S3 L84-172 / S4 L84-214 |
| internal joints | 无（manifold 内部全是 visual，非动=非 part，Rule 1） | — |
| upstream interface | root，无（首 slot） | — |
| downstream interface | `manifold` body 面（part=`manifold`, +z），re-export 给后续 slot（不被自动 chain joint 消费） | S1-S4 |
| meta published | `spg`: stations、n_fingers、arrangement、finger_radius、hinge_pin/ support_ref 名 | 本模板 |

### Slot B / module finger_form（任一 candidate）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `finger_{idx}` ×N（actuator_base Box + soft_neck Box + `bellow`[form] mesh + 表面装饰 visual）；`finger_{idx}_tip` ×N（仅 multi_segment，同 form tip 几何） | S1 L171-198 / S2 L141-153 / S5 L213-239 |
| internal joints | 无（静态几何；关节由 Slot C emit） | — |
| upstream interface | 不声明（parallel child） | — |
| downstream interface | re-export `ctx.upstream_interface`（manifold body 面） | 本模板 |
| meta published | `spg_fingers`: finger part 名、tip 名（若 multi） | 本模板 |

### Slot C / module actuation_mechanism（任一 candidate）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hose_connector_{idx}` ×N；`finger_carriage_{idx}` ×N（仅 span） | S1 L212-236 / S6 L69-80 |
| internal joints | `manifold_to_finger_{idx}` REVOLUTE 切向 [0,upper]（span 时 parent=carriage）；`finger_to_connector_{idx}` REVOLUTE ±0.30；`finger_{idx}_knuckle` REVOLUTE [0,0.50]（multi）；`manifold_to_carriage_{idx}` PRISMATIC [0,0.030]（span） | S1 L201-245 / S5 L235-253 / S6 L207-247 |
| upstream interface | 不声明（parallel child） | — |
| downstream interface | re-export `ctx.upstream_interface` | 本模板 |

要求已满足：活动件（finger/tip/connector/carriage）都有 articulation 语义；不动细节（板孔/螺栓/端口/倒钩/滑轨/法兰螺栓/气管）都是 `manifold`/`finger` 的 parent visual，非独立 FIXED part（Rule 1）。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| base_arrangement | enum | {crossed_rail_radial, clevis_frame_opposing, wrist_flange_radial, inline_beam} | crossed_rail_radial | choice | deterministic sampler | Slot A 表 |
| finger_form | enum | {corrugated_oval, ribbed_fin_pneunet, fiber_cylinder} | corrugated_oval | choice | deterministic sampler | Slot B 表 |
| actuation_mechanism | enum | {single_swivel, multi_segment, span_carriage} | single_swivel | conditional | span→N==2；multi→N≤4，否则降级 single_swivel | Slot C 表 |
| finger_count (N) | int(multiplicity) | radial:{2,3,4,6} / flange:{3,4,5,6} / opposing:2 / inline:{2,3,4,5} | 4 | conditional | 范围随 base 解析；加权小 N 偏多（§8） | §8 |
| finger_radius_scale | float | [0.90, 1.12] | 1.0 | independent | radial 手指圆半径 R = 0.101·scale，仅 clamp | S1 L116 |
| finger_length_scale | float | [0.88, 1.12] | 1.0 | independent | bellow 轴向长度比例，仅 clamp | S1 L38-64 |
| bend_upper | float | derived | 0.60 | equation | `= f(N)`：N≤3→0.62, N==4→0.55, N∈{5,6}→0.46（内弯不向心穿模） | S1 L208 / clearance |
| swivel_range | float | [0.24, 0.34] | 0.30 | independent | hose swivel ± 上界，clamp | S1 L244 |
| knuckle_upper | float | [0.42, 0.52] | 0.50 | independent | multi 远端段 curl，clamp | S5 L234 |
| span_travel | float | [0.024, 0.032] | 0.030 | independent | carriage PRISMATIC 上界，clamp | S6 L206 |
| palette_style | enum | {cyan_silicone, matte_black, food_white, safety_orange, blue_silicone} | cyan_silicone | choice | deterministic sampler | §8.5 ⑥ |
| (—) | constraint | — | — | inequality | radial 内弯不向心：`R − L·sin(bend_upper) ≥ tip_half_w / sin(π/N)`；违反时按 §7 步骤回缩 bend_upper（equation 已按 N 分档实现该保守回缩） | 接口/clearance |

连续尺寸采样契约：先采 independent（finger_radius_scale/finger_length_scale/swivel_range/knuckle_upper/span_travel）→ 派生 equation（bend_upper=f(N)）→ 用 inequality 校验（bend_upper 分档已保证 radial 高 N 不向心）→ conditional（N 范围、mechanism 降级）在采样时按上游 base 解析。scale 默认独立，相关性只在 bend_upper=f(N) 显式落地。

## 7.5 编译预算 / compile budget（必填）

自报 ≤ 25s / seed。依据：corrugated_oval/fiber_cylinder 用 MeshGeometry.merge（8 层 CylinderGeometry 32seg + sphere 24-28seg + 一条 spline tube 8-14 radial），~0.1-0.3s；ribbed_fin/clevis_frame/span carriage 用 cadquery 布尔 union（~8-15 次 fillet union），单次 shape 1-3s。**N 根相同手指复用同一个 `bellow`/`tip` Mesh 资产（build 一次，per-finger 只换 visual 名）**，所以 N 不放大编译时间；cadquery frame/finger shape 每 seed 只构造一次。分档 tessellation：小特征 ≤32 段，主形态 ≤32 段。超预算先降段数再迭代。

## 8. Multiplicity / Copy Logic

- **count_param (primary, 唯一轴)：** `finger_count` (N) — radial/inline finger-station 循环 `for idx in range(N)`，复制整个 finger station。
  - `N_range`（本小类产品域，按 base 轴定，人工审核后取值）：
    - crossed_rail_radial：{2, 3, 4, 6}（origin 示 4；fork n3/n6）
    - wrist_flange_radial：{3, 4, 5, 6}
    - clevis_frame_opposing：2（固定，origin B 两 jaw）
    - inline_beam：{2, 3, 4, 5}（origin skeleton_inline 示 4）
  - sampling domain（权重档）：小 N 高频、大 N 稀有，如 radial 加权 `[2,3,3,4,4,4,6]`、inline `[2,3,3,4,4,5]`。
  - copied object：整个 finger station —— `finger_{idx}`(+actuator_base/soft_neck/bellow/表面装饰)、`hose_connector_{idx}`、以及 manifold 侧 `yoke_cheek_{idx}_{n}`/`yoke_bridge_{idx}`/`hinge_pin_{idx}`/`fixed_elbow_{idx}`/`air_tube_{idx}`（+ multi 的 `finger_{idx}_tip`、span 的 `finger_carriage_{idx}`）。
  - placement：radial 均布 yaw=2π·idx/N（固定 finger-circle 半径 R）；opposing yaw∈{0,π}；inline 沿梁 x=x0+idx·pitch, yaw=0。
  - joint policy：每 finger 一条独立 REVOLUTE `manifold_to_finger_{idx}` 弯曲（切向轴，[0,upper(N)]），彼此独立（非 mimic）。
  - source/gating：origin {2,4} + fork {3,6}；N 上限受 base 与 bend_upper=f(N) 向心 clearance gate 约束。
- **其它循环（record_only，不作 multiplicity 轴）：** 板螺丝/standoff/端口孔、wrist-flange 螺栓圈 `flange_bolt_{i}` FIXED、grip_valley 装饰 —— loop-emitted、indexed、FIXED/visual 装饰，记录不 sweep。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 4 种 base 骨架 + station 拓扑：crossed_rail_radial(S1)、clevis_frame_opposing(S2)、wrist_flange_radial(S3)、inline_beam(S4)；multi_segment(S5) 给 finger 内部加一段 `finger_{idx}_tip`+knuckle 边；span_carriage(S6) 加 `finger_carriage_{idx}`+PRISMATIC 边。全 forked_anchor/source-backed |
| └ multiplicity | 同构件 ×N | 有 | `finger_count` N∈{2,3,4,5,6}，见 §8（N 域 + 加权档：小 N 高频） |
| ② 关节类型 | 图不变，换 type/轴 | 有 | REVOLUTE 内弯 bend(S1/S2)；REVOLUTE hose swivel(S1)；REVOLUTE 串联 knuckle(S5)；PRISMATIC span carriage(S6)。声明的每种 type 都在 sweep 出现（single/multi/span 都被采样）。全 source-backed |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | 登记进 `slot_choices` 的 `finger_form` slot：corrugated_oval(Volumetric Envelope Form,S1)、ribbed_fin_pneunet(Macro Surface Construction,S2)、fiber_cylinder(Volumetric Envelope Form,S5-form)。≥3 可识别原型，均 forked_anchor |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有(record_only) | grip_valley 暗插槽(S1)、drilled port/hex socket(S2)、barbed fitting、laser-etch 负载标签、flange 螺栓圈(S3)、fiber-wrap 螺旋肋(S5)。装饰几何均写作**宿主 part visual**、由宿主表面派生（fin/valley 随 bellow 逐层、螺栓圈随法兰半径、fiber wrap 随锥柱半径 r(z)），共形嵌入不悬空；record_only + world_knowledge_extrapolation，不单列 candidate |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | finger_radius_scale[0.90,1.12]、finger_length_scale[0.88,1.12]（§7）。关节运动包络：bend REVOLUTE 切向轴、内弯方向、[0, upper(N)=0.46~0.62]；swivel REVOLUTE ±[0.24,0.34]；knuckle REVOLUTE 同向 [0,0.50]；carriage PRISMATIC 宽度轴 [0,0.030]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`（6+ 关节时 max_pose_samples=32）；每机构一条 targeted `ctx.pose`：bend→finger 向内(半径减小/-x)、swivel→connector 有位移、knuckle→tip 更深内弯、carriage→jaw 对称外张。全程/整程不穿模 |
| ⑥ 涂装 | 只改材质/颜色 | 有(record_only) | 材质大类 metal(brushed/satin aluminum) + rubber(air tube) + plastic/silicone(bellows)；配色 ≥5：cyan_silicone(S1)、matte_black(S2)、food_white、safety_orange、blue_silicone。materials 大类覆盖 ≥ ceil(0.5×5)=3（metal+silicone/plastic+rubber）。companion-only |

①②③ + N 为候选锚轴，全 source-backed；④⑤⑥ record_only / companion，不单独计入预算。

## 采样与覆盖审计

总组合数：base(4) × finger_form(3) × mechanism(3) × N(平均~4 档) × palette(5) ≈ 720（gating 后可行组合略少）。

理由：base×form×mechanism = 36 离散拓扑；乘 N multiplicity 与 palette 远超 300 富类别门槛。span_carriage 仅 N==2、multi_segment 仅 N≤4 gating 排除易穿模组合。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次 `rng.choice` 采 base_arrangement、finger_form、actuation_mechanism、palette_style，加权采 N（按 base），uniform 采连续 scale。`resolve_config` 做 compatibility gating（span→N==2 else single_swivel；multi→N≤4 else single_swivel；N 按 base clamp）与 clamp/derive（bend_upper=f(N)）。`build_*` 调 `assemble(selection_mode="anchor_choices")`，各 slot 读 resolved config + meta。seed=0 不特殊（走同一 sampler）。`slot_choices_for_seed(seed)` 复算 resolved config 导出 (slot,module) 元组，含 `finger_count` band、`palette_style`。
Topology target：1000-seed slot-choice tuple 覆盖 report-only；本类真实离散组合空间 ≈ 36 base×form×mech 拓扑 × N 档，>300，达标。
regression overrides：none。
Controlled local parameterization：finger_radius_scale、finger_length_scale、swivel_range、knuckle_upper、span_travel（范围见 §7），全部 `resolve_config` clamp；bend_upper=f(N) 派生；不破坏 InterfaceSpec/MatingContract/multiplicity（hinge station 由 base 发布，finger 复用同一 bellow 资产）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 base→form→mechanism，加权 N，uniform scale，compatibility gate | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | span_carriage↔N==2；multi_segment↔N≤4；N↔base；违反降级 single_swivel/ clamp N | 无 floating/collision/axis/max-N/bulky/optional-child 失败 |
| controlled local variation | finger_radius/length/swivel/knuckle/span scale + clamp | 比例变化不破坏接口/clearance/support/joint origin/类别 identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 初次，0-999 成熟度审计 | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| base_manifold | 4 | yes | yes | ① + support 根 |
| finger_form | 3 | yes | yes | ③ 主体形态家族 slot |
| actuation_mechanism | 3 | yes | yes | ② 关节机构（含 PRISMATIC/串联 REVOLUTE） |

## Validator

- slot_choices_for_seed 返回已实现 module 名（base_arrangement / finger_form / actuation_mechanism / finger_count band / palette_style）
- config_from_seed 对所有普通 seed（含 seed 0）用 deterministic procedural sampling
- compatibility gating 阻止非法组合（span N≠2 / multi N>4）
- 无 regression overrides
- 不以小型 curated/modulo 表作为主 seed domain
- 连续 scale 全 clamp；bend_upper=f(N) 在 resolve_config 派生，不留到 builder 失败
- 关键接口：每 finger station hinge_pin + captured actuator_base（element-scoped allow_overlap）；span carriage dovetail↔manifold rail（grandfather PRISMATIC）
- 关键关节 type/axis/range：bend REVOLUTE 切向 [0,upper(N)]；swivel REVOLUTE ±；knuckle REVOLUTE 同向 [0,0.5]；carriage PRISMATIC 宽度 [0,0.03]
- 复制件命名 `finger_{idx}`/`hose_connector_{idx}`/`finger_{idx}_tip`/`finger_carriage_{idx}` + 均布/线性 placement

## Reject cases

- 手指做成刚性连杆或平行夹爪（丢失 compliant bellows 身份）
- bellow 被降级成裸 Box/Cylinder（违反 Rule 3 primitive；必须 mesh/cadquery/lathe 形态）
- 手指不向内弯（bend 轴/方向错）或全程穿模（向心/相邻 finger 相撞）
- hinge_pin 用 3mm 幽灵盘而非真实 actuator_base 捕获（违反 Rule 2）
- 装饰件（螺栓/端口/气管/滑轨）做成独立 FIXED part 而非宿主 visual（违反 Rule 1）
- N 超 base 上限或 span/multi 未 gating 导致自碰撞
- fiber_wrap / grip_valley 用常数半径套在锥/变尺寸 bellow 外（违反 Rule 4 共形）

## 与相邻类别的边界

- 不该混入：刚性平行夹爪 / 两指气动夹爪（rigid jaws，非 compliant bellows）
- 不该混入：真空 / 吸盘末端执行器（无充气弯曲手指）
- 不该混入：腱驱动刚性多连杆机械手 / 颗粒阻塞夹爪（不同抓取原理）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 形态主导 + multiplicity；③ finger_form slot 登记 slot_choices；② 含 PRISMATIC(span)/串联 REVOLUTE(multi)；all candidates forked_anchor |

## 模板实现备注（可选）
- 共享 helper：`_finger_bellow_mesh(form)` 每 form build 一次 Mesh，N 根 finger 复用（编译预算）；`_rot_xy`、`_circle_profile`、`_cq_box` 从源移植。
- InterfaceSpec：base 只声明 downstream（body 面）re-export；finger_form/actuation 不声明 upstream（parallel child，抑制自动 chain joint），re-export ctx.upstream_interface。
- captured-pin element-scoped allow_overlap：actuator_base↔hinge_pin（每 finger）；span carriage↔manifold rail dovetail；multi tip↔finger 连接 pad。
- 暂不进入 seed domain 的组合：span_carriage×(radial N≠2 / inline / flange)、multi_segment×N>4 —— 由 gating 降级 single_swivel。
