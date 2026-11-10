# Modular Spec — Robotics / Rack-and-pinion slider

## 元信息
| 项 | 值 |
|---|---|
| slug | `rack_and_pinion_slider` |
| template path | `agent/templates/rack_and_pinion_slider.py` |
| test path (optional) | `tests/agent/test_rack_and_pinion_slider_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children + multiplicity) |

`pattern` 说明：单一 `frame` 根件同时挂两个耦合运动子件——一个 REVOLUTE 齿轮 pinion 与一个 PRISMATIC 直线滑件（moving-rack 拓扑）；在 traveling-pinion 拓扑里改为 frame→pinion_carriage(PRISMATIC)→pinion(REVOLUTE) 的两级链。齿条齿 / pinion 齿由 multiplicity loop 复制。不是纯串链，故按 monitor_mount / dj_equipment 的 `__modular__` 手工装配 idiom 实现（enum slot + `slot_choices_for_seed` + 手工 articulation），不使用 `_modular.assemble()` 串链器。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (2 origins + 8 forks) |
| source_index_policy | only adopted module sources are indexed below |

（读取：origin A `rec_robotics__..._002`、origin B `rec_robotics__..._001`，及 8 个 fork：form_round_rack, form_enclosed_tube, carriage_linear_table, skeleton_traveling_pinion, skeleton_cantilever_pinion, n2_dual_pinion, n44_long_rack, n16_short_rack。全部为 PASS 记录。）

## 核心身份

线性传动机构：一枚绕固定轴旋转的直齿 pinion 啮合一条直齿 rack，把旋转转成沿单一直线的平移（或反之）。必须保留：带齿 pinion（spur gear）、带齿直 rack、一个 REVOLUTE pinion_spin + 一个 PRISMATIC 直线滑动、由 pitch-radius 耦合（旋转↔平移）、承载 pinion 轴并导向滑件的固定 guide frame/base、至少一个真实非-FIXED 关节。

不该混入：丝杠/滚珠丝杠（螺旋驱动，无齿条）、皮带线性滑台（柔性带，无齿啮合）、纯线性导轨/LM guide（无齿轮驱动）、旋转齿轮箱/蜗轮（无直线 rack）、链-链轮驱动、带拉杆的汽车转向 rack（变成整车转向总成）、弧形/扇形/斜齿 rack（漂向扇齿/蜗杆邻类）。

## 槽位 + 候选模块表

设计取舍：本小类结构词汇天然狭窄（REVOLUTE-pinion + PRISMATIC-rack 这一对 *就是* 类别 identity，② 不产生新关节类型）。为避免 5 个正交轴（moving/traveling × straddle/cantilever × single/dual × form × envelope）产生大量非法/易碰组合，按 `AUTHORING.md` §B「prefer more candidates over more slots」把 ①拓扑+支撑+pinion 数量 折进单个自包含的 `drive_skeleton` slot（每个候选都是一套完整、自支撑的驱动配置），落到 **3 个 slot**；rack 齿数作为 multiplicity 轴（§8）。

### Slot A：drive_skeleton（① 骨架/支撑/pinion 数量拓扑）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `moving_rack_straddle` | forked_anchor | origin B (`rec_robotics__..._001`) / origin A (`_002`) | B:L110-L270 · A:L98-L203 | eligible if compatible | frame 根 + 固定 pinion（两侧 torus-collar / cheek straddle 轴承支撑）+ 平移 rack_carriage。joints: frame→pinion REVOLUTE, frame→rack_carriage PRISMATIC。single pinion。 |
| `moving_rack_cantilever` | forked_anchor | skeleton_cantilever_pinion | L113-L169 (single-side support) | eligible if compatible | 同 moving-rack 拓扑，但 pinion 只由 **一侧** bearing_cheek + motor_housing stub 悬臂支撑（overhung），轴为 cantilever 短轴，无对侧轴承。 |
| `traveling_pinion` | forked_anchor | skeleton_traveling_pinion | L143-L256 | eligible if compatible | rack **固定** 到 frame（全长），新增 `pinion_carriage` 部件沿 guide rails 平移，pinion 在 carriage 上旋转。joints: frame→pinion_carriage PRISMATIC, pinion_carriage→pinion REVOLUTE。 |
| `moving_rack_dual` | forked_anchor | n2_dual_pinion | L70-L114,L144-L282 | eligible if compatible | moving-rack 拓扑，两枚 pinion（`pinion_0/1`）沿轴线 ±X 偏置、共同啮合同一 rack、各自独立 REVOLUTE（anti-backlash）；轴承支撑按 pinion 复制。 |

### Slot B：rack_form（③ 主体形态家族 / Primary Form Family — rack 截面）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `flat_bar_rack` | forked_anchor | origin B / origin A | B:L178-L199 · A:L65-L77 | Volumetric Envelope Form | eligible if compatible | 矩形 back bar（Box）+ 顶面 trapezoid 齿条；经典平齿条。 |
| `round_shaft_rack` | world_knowledge_extrapolation(仅③) | form_round_rack | L179-L198 | Volumetric Envelope Form | eligible if compatible | 圆柱 rack shaft（Cylinder 沿 +X）+ 顶切齿带；同 part tree / 同 trapezoid 齿 primitive / 同 interface，只换 rack 主体包络（方↔圆）。anchors 证明 SDK 可造且覆盖 observed 截面空间（方/圆两界）。 |

降到 2 个候选并说明理由：source pool 中 rack 截面只有「平-bar」与「圆-shaft」两种 source-backed 原型；弧形/扇形/斜齿 rack 已在 §核心身份/§11 排除为邻类。故 rack_form 合法地降到 2。

### Slot C：envelope_carriage（③ 宏观表面构成 / 滑件外观-封装）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `bare_open` | forked_anchor | origin B / origin A | B:L164-L177 · A:L150-L170 | Macro Surface Construction | eligible if compatible | 裸露机构：滑件为薄 carriage_bridge/block + 两条 carriage_shoe（或 traveling 的 pinion_carriage 本体），rack/pinion 全暴露。 |
| `linear_stage_table` | forked_anchor | carriage_linear_table | L165-L213 | Planar Boundary Form | eligible if compatible (moving-rack only) | 宽平 T-slot stage table（Box 平台 + 均布 slot rib loop）刚接到 rack 上，读作直线工作台。 |
| `enclosed_tube_housing` | forked_anchor | form_enclosed_tube | L91-L118,L197-L272 | Volumetric Envelope Form | eligible if compatible (straddle single only) | frame 上加一个盒式/管式 housing 壳（bottom+top+两侧+后壁 box 墙，前壁留 aperture），把 pinion 与缩回的 rack 罩住；rack 从 +X 端 aperture 伸出滑动。 |

硬约束满足：Slot A 4 候选（≥3）、Slot C 3 候选（≥3）、Slot B 2 候选（已说明降 2 理由）。每个候选结构不同（非换尺寸/色）。③ 主体形态家族由 Slot B（rack 截面）+ Slot C（宏观封装）共同承载，均登记进 `slot_choices`。

### 6 轴预检结论（详见 §8.5）
① 由 Slot A 承载（moving/traveling + straddle/cantilever + single/dual）；② 无新类型（REVOLUTE+PRISMATIC 即 identity）；③ 由 Slot B + Slot C 承载；④ record_only 共形；⑤ pinion 齿数/rack 齿数(N)/比例/行程；⑥ palette record_only。

## 槽位图（slot graph）

```
pattern: mixed (parallel_children + multiplicity)

moving-rack 拓扑 (moving_rack_straddle / _cantilever / _dual):
  frame (root)
    │
    ├──[REVOLUTE  axis=(0,-1,0)  origin=pinion_center  · 捕获轴承(pin-through-bore, grandfathered)]──> pinion[_k]
    │        （mesh 接口：pinion 齿在 pitch line 啮合 rack 顶齿；Slot B 决定 rack 截面）
    └──[PRISMATIC axis=(1,0,0)   origin=rack_frame_z    · 滑轨(grandfathered, rack 悬于 guide_rail 上方)]──> rack_carriage
             （Slot C 决定 carriage 外观：bridge/shoes · stage_table · 罩内 block）

traveling-pinion 拓扑 (traveling_pinion):
  frame (root, 含 FIXED 全长 rack 作为 frame visual)
    └──[PRISMATIC axis=(1,0,0)]──> pinion_carriage
             └──[REVOLUTE axis=(0,-1,0)]──> pinion
             （pinion 啮合 frame 上固定 rack；carriage 的 guide_slider 骑双导轨）
```

接口点位：
- pinion↔rack **啮合接口**：pinion 齿顶在 pitch line 与 rack 顶齿交错（tooth envelopes interleave，齿在 1mm 邻近内 → 连通；实体经 half-pitch phasing 不实碰，或经 gear-mesh `allow_overlap` 声明为意图啮合）。这是 rack_carriage↔frame 的主要支撑连通路径（frame→pinion 轴承→rack 啮合）。
- pinion 轴承接口：pinion axle 穿过 frame（或 carriage）上 torus bearing_collar / bearing_boss；captured journal fit（pin-through-bore），element-scoped `allow_overlap`，joint 无 MatingContract（grandfathered）。
- 滑动接口：rack_carriage 的 carriage_shoe/bridge 骑 guide_rail 上方（expect_gap）；traveling 的 guide_slider 接触双导轨。
- 跨 slot joint type/axis/range：REVOLUTE pinion_spin axis=(0,-1,0)，range 由 pitch 与 travel 派生（约 ±1 rad）；PRISMATIC rack_slide/carriage axis=(1,0,0)，range=[-travel, travel]，travel 由 rack 齿数 N × pitch 派生。
- 互斥/派生：Slot C 的 `linear_stage_table` 与 `enclosed_tube_housing` 仅 moving-rack 有意义（traveling_pinion 无 rack_carriage → 强制 bare_open）；`enclosed_tube_housing` 仅 `moving_rack_straddle`（single、两侧支撑，罩壳几何忠实于 origin A）。gating 见 §9。

## 每槽位 Module Emits / Interfaces

### Slot A / module moving_rack_straddle
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame(root), rack_carriage, pinion | B:L110,L164,L201 |
| internal joints | frame→pinion REVOLUTE axis(0,-1,0); frame→rack_carriage PRISMATIC axis(1,0,0) | B:L245-L270 |
| frame visuals | base_plate, guide_rail, rail_stop_{0,1}, mount_bolt_{0..3}, per-side bearing_web/bearing_saddle/bearing_collar(torus) | B:L110-L162 |
| pinion visuals | root_wheel(Cyl), pinion_tooth_{i}(trapezoid loop), raised_hub, axle, axle_cap_{0,1} | B:L201-L243 |
| mating/anchor | pinion axle in torus bearing_collar（captured, allow_overlap, no MatingContract）; rack 悬 guide_rail 上方（PRISMATIC grandfathered） | B tests L282-L354 |

### Slot A / module moving_rack_cantilever
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame, rack_carriage, pinion | cantilever L98,L180,L202 |
| frame visuals(变) | 单侧 bearing_cheek_0 + cheek_foot_0 + motor_housing(Cyl) + bearing_boss_0 + 悬臂 pinion_shaft stub | cantilever L113-L169 |
| joints | 同 straddle | cantilever L214-L233 |

### Slot A / module traveling_pinion
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame(含固定 rack visual), pinion_carriage, pinion | traveling L99,L143,L217 |
| internal joints | frame→pinion_carriage PRISMATIC; pinion_carriage→pinion REVOLUTE | traveling L232-L256 |
| carriage visuals | bearing_cheek_{0,1}, guide_slider_{0,1}, carriage_crossbar, pinion_shaft, carriage_bolt_{0,1} | traveling L143-L214 |
| frame visuals(变) | 固定 straight_rack(+齿) 作 frame visual + rack_bed | traveling L114-L128 |

### Slot A / module moving_rack_dual
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame, rack_carriage, pinion_0, pinion_1 | n2 L166,L225,L263 |
| internal joints | frame→pinion_k REVOLUTE ×2; frame→rack_carriage PRISMATIC ×1 | n2 L270-L299 |
| frame visuals | per-pinion 复制 bearing_web/saddle/collar | n2 L198-L222 |

### Slot B / module flat_bar_rack / round_shaft_rack
| emits | 描述 | 来源 |
|---|---|---|
| rack 主体 | flat: rack_bar Box; round: rack_bar Cylinder（沿 X） | B:L178 · round:L180-L188 |
| rack 齿 | rack_tooth_{i} trapezoid loop（half-pitch phasing）+ rack_end_cap_{0,1} | B:L184-L199 |
| interface | 顶齿在 pitch line 供 pinion 啮合；截面只改 Box↔Cylinder，齿 primitive/interface 不变 | round tests L364-L377 |

### Slot C / module bare_open / linear_stage_table / enclosed_tube_housing
| emits | 描述 | 来源 |
|---|---|---|
| bare_open | rack_carriage: carriage_bridge + carriage_shoe_{0,1}（或 block+bolts） | B:L164-L177 · A:L157-L170 |
| linear_stage_table | rack_carriage: stage_table(Box) + table_slot_rib_{i} loop + carriage_shoe_{0,1} | table L165-L213 |
| enclosed_tube_housing | frame: housing 壳（box 墙 bottom/top/side/back + 前壁 aperture）+ carriage: rack_bar+block | enclosed L91-L118,L197-L298 |

要求满足：活动件（pinion/rack_carriage/pinion_carriage）都有 articulation 语义；不动细节（housing 墙、rib、bolt、end_cap、bearing 硬件、motor_housing）全写成宿主 part visual，无独立 FIXED part。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| drive_skeleton | enum | moving_rack_straddle / moving_rack_cantilever / traveling_pinion / moving_rack_dual | moving_rack_straddle | choice | deterministic sampler | Slot A |
| rack_form | enum | flat_bar_rack / round_shaft_rack | flat_bar_rack | choice | deterministic sampler | Slot B |
| envelope_carriage | enum | bare_open / linear_stage_table / enclosed_tube_housing | bare_open | conditional | 合法集随 drive_skeleton gating（§9） | Slot C |
| rack_tooth_count (N) | int | [12, 56]（偶数） | 30 | independent | 加权采样（小 N 偏多）；驱动 rack 长度+travel | §8 · B:L191 |
| pinion_teeth | int | [18, 26] | 22 | independent | clamp；驱动 pitch_radius | B:L85 · A:L24 |
| tooth_pitch | float | 常数 0.019 | 0.019 | equation(const) | 锁定以保护啮合；`pitch_radius=tooth_pitch·pinion_teeth/2π` | B:L84-L86 |
| pitch_radius | float | derived | — | equation | `= tooth_pitch·pinion_teeth/(2π)` | B:L86 |
| rack_travel | float | derived | — | equation | `= min(pitch_radius, N·tooth_pitch·0.18)`（对称 ±travel） | B:L263-L268 · n44:L266 |
| face_scale | float | [0.9, 1.15] | 1.0 | independent | 同步缩放 rack_width 与 gear_width（保持啮合面关系） | B:L88-L89 |
| base_length | float | derived | — | equation | `= N·tooth_pitch + 齿条余量`；rail/base 随之 | n44:L112-L122 |
| palette_theme | enum | steel_oxide / warm_machined / office_white / dark_carbon / anodized_blue | steel_oxide | choice | 仅涂装 | ⑥ |
| (—) | constraint | — | — | inequality | `rack_travel ≤ pitch_radius` 且 `base_half ≥ rack_half + rack_travel + rail_stop_margin`；违反按比例回缩 rack_travel | 接口/clearance |
| (—) | constraint | — | — | inequality | `pinion_center_z = rack_tooth_tip_z + gear_root_radius + 0.001`（啮合锁定，单一来源） | B:L95 |

连续尺寸采样契约：先采 independent（pinion_teeth, N, face_scale）→ 派生 equation（pitch_radius, rack_travel, base_length, 全部 z 高度经 `_GearGeom`）→ inequality 回缩 rack_travel/base → 解析 conditional（envelope 合法集）。所有 equation/inequality 在 `resolve_config` 求解。

### 7.5 编译预算 / compile budget
每-seed 预算 **≤ 12s**。全部几何为 Box / Cylinder / TorusGeometry(36 段) / 8-顶点 trapezoid prism mesh（无 cadquery 布尔），最重情形为 N≤56 rack 齿 + dual 2×≤26 pinion 齿 ≈ 130 个微小 mesh，共享 `rack_tooth_mesh` / `gear_tooth_mesh` 单一 `mesh_from_geometry` 复用。tessellation：torus 36 tubular / 20 radial；Cylinder 默认段数足够。超预算先降 torus 段数再迭代。sweep `--compile-timeout 120`（3× 余量看门狗）。

## Multiplicity / Copy Logic

**count_param (primary)：rack 齿数 / rack 长度** — `rack_tooth_{idx}` trapezoid loop（source-backed：B 的 `for i in range(-15,15)` 30 齿；fork n44=44、n16=16）。
- N_range（产品域）：[12, 56]；测试偏小、产品全程。
- sampling domain（权重档）：short(≤20) 高频、mid(21-40) 常见、long(>40) 稀有。slot_choices 用 band（short/mid/long）。
- copied object：单一 `rack_tooth` trapezoid mesh 经共享 `_trapezoid_prism` helper；placement：沿 +X 均布 half-pitch 相位（`x=(i+0.5)·tooth_pitch`，pinion 下留 valley）；joint policy：齿随 moving rack_carriage（PRISMATIC）整体运动或随固定 rack（traveling），无 per-tooth joint；naming：`rack_tooth_{idx:02d}`。
- gating：N 决定 rack_bar 长度、base/rail 长度、rack_travel。

**count_param (secondary, N/record_only)：pinion 齿数** — `pinion_tooth_{idx}` 径向 loop（origin 显示 {22(B),28(A)}）。作为 ⑤ 连续量 clamp 采样 [18,26]，naming `pinion_tooth_{idx:02d}`，radial 均布 `theta=π+idx·2π/n`；驱动 pitch_radius（equation）。已 2 sample 跨 origin，作 ⑤ 采样不单独 fork。

**count_param (structural, forked)：pinion 数量** — 折入 `moving_rack_dual` 候选（N=1 origins vs N=2 fork）。dual 用 pinion-instance loop（`pinion_0/1`）+ 各自 REVOLUTE + 复制轴承支撑，均布 ±X（spacing 取 pitch 整数倍以保 valley 相位）。

**其它 loop (record_only)：** mount_bolt {4}, guide_rail {1-2}, bearing_support {2/per-pinion}, table_slot_rib, housing_bolt/rib — loop-emitted、FIXED-as-visual、indexed，记录不单独 sweep。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Slot A 4 候选（forked_anchor）：moving_rack_straddle（frame→pinion REVOLUTE + frame→rack PRISMATIC，single，两侧轴承）· moving_rack_cantilever（单侧悬臂支撑）· traveling_pinion（rack 固定，新增 pinion_carriage，PRISMATIC 移到 carriage，链变 frame→carriage→pinion）· moving_rack_dual（+第二枚 pinion + 第二个 REVOLUTE）。part/joint 图确有增减。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：rack 齿 N∈[12,56] 权重档；pinion 数 1↔2（dual 候选）。 |
| ② 关节类型 | 换 type/轴 | 无（仅一对固有类型） | REVOLUTE pinion_spin axis(0,-1,0) + PRISMATIC rack_slide axis(1,0,0)，两者由 pitch 耦合，*即* 本类身份；诚实无新关节类型（dual 是第二个同型 REVOLUTE，traveling 是同型关节换 parent）。声明的两种类型都在每个 seed 出现。 |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | Slot B（rack 截面）：flat_bar_rack（Volumetric Envelope，forked_anchor B/A）· round_shaft_rack（Volumetric Envelope，world_knowledge_extrapolation on form_round_rack）。Slot C（宏观封装）：bare_open（Macro Surface，B/A）· linear_stage_table（Planar Boundary，forked_anchor table）· enclosed_tube_housing（Volumetric Envelope，forked_anchor enclosed）。均登记进 `slot_choices`。 |
| ④ 表面装饰 | 叠加表面细节 | 有(record_only) | trapezoid 齿侧面、机加 hub、torus bearing-collar 环、蓝 axle end-cap、rail_stop、mount-bolt/screw 头、table T-slot rib、housing rib/bolt。全部由宿主 part 表面派生（贴 base/rack/pinion/housing 面），非独立 part、非新关节。派生顺序 ③→⑤→④。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | pinion_teeth[18,26]、rack N[12,56]、face_scale[0.9,1.15]、base_length(派生)、rack_travel(派生)。**运动包络**：REVOLUTE pinion_spin axis(0,-1,0)、[闭合 0, 可行上界 ≈ +1 rad]（对称 ±1）；PRISMATIC rack_slide/carriage axis(1,0,0)、开启方向 +X、[−travel, +travel]，travel≤pitch_radius。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`（齿啮合经 gear-mesh `allow_overlap` 意图声明，轴承经 element-scoped allow_overlap）；targeted `ctx.pose`：{pinion_spin=+1,rack_slide=+pitch_radius} 证明耦合 → rack +X 平移；{rack_slide=+travel} 证明伸出且仍被 base 承托；traveling 证 pinion_carriage +X 平移。continuous 无（两关节皆有限行程）。 |
| ⑥ 涂装 | 只改材质/颜色 | 有(record_only) | 材质大类 metal 主（brushed steel/aluminum、dark oxide/carbon、warm machined gear、zinc、blue anodized cap）；5 palette 预设，材质大类覆盖 metal/painted ≥ ceil(0.5×5)=3。 |

**收尾自检**：0-9 seed 渲染须肉眼见：Slot A 四种驱动骨架拉得开、Slot B 方/圆 rack、Slot C 裸露/工作台/罩壳三种、材质大类都出现、齿共形贴合不悬空、pinion 旋转+rack 滑动全程不穿模。

## 采样与覆盖审计

总组合数：drive_skeleton(4) × rack_form(2) × envelope_carriage(≤3, gated) = 名义 24，gating 后合法组合 ≈ 4(straddle:3 envelope)+ 2(cantilever:2)+... × rack_form(2) ≈ **20 合法 slot 组合**；再乘 N 权重档(3) × pinion_teeth 若干 × palette(5) → 组合空间充裕。

理由：本小类结构狭窄（simple band 8-12 counted anchors），20 合法离散组合 + N/⑤/palette 已覆盖 source 全部结构多样性；Topology target 1000-seed tuple 覆盖 report-only，不追求 >300（狭窄机构，源锚点上限 10）。

seed_domain_policy：procedural_first。**seed 0 不特殊**——`config_from_seed(0)` 与其它 seed 同走 `random.Random(seed)` 程序采样。
Procedural Sampling / Sweep Plan：每 seed `rng=random.Random(seed)`：均匀采 drive_skeleton；均匀采 rack_form；按 drive_skeleton gating 采 envelope_carriage 合法集；加权采 N（小偏多）；采 pinion_teeth、face_scale、palette。`resolve_config` clamp + 解 equation/inequality（rack_travel 回缩、envelope 合法性再校验并 fallback bare_open）。无 curated/modulo 主表。
Topology target：report-only；狭窄机构，不反推上游变体数。
regression overrides：none（首版；如后续 sweep 暴露特定 seed 回归再稀疏加，注明 seed+理由）。
Controlled local parameterization：pinion_teeth、rack N、face_scale、base_length(派生)、rack_travel(派生)。全部在 `resolve_config` clamp/派生；不破坏 pinion-rack 啮合（z 高度经 `_GearGeom` 单一来源锁定）、轴承接口、multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 skeleton→rack_form→envelope(gated)→N→scalars；weighted N | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | traveling_pinion→envelope 强制 bare_open；dual→envelope∈{bare_open,linear_stage_table}；cantilever→∈{bare_open,linear_stage_table}；enclosed_tube_housing 仅 moving_rack_straddle；round_shaft 全 skeleton 合法 | 无 floating/collision/axis/max-mult/bulky-module 失败 |
| controlled local variation | pinion_teeth/N/face_scale clamp；z 高度派生锁定 | 比例变化不破坏啮合/clearance/support/joint origin/类别 identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 初过；0-999 成熟度审计 | 契约失败；axis_realization；viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| drive_skeleton | 4 | yes | yes | |
| rack_form | 2 | yes | no | source pool 仅方/圆两 source-backed 截面，已说明降 2 |
| envelope_carriage | 3 | yes | yes | gated by skeleton |

## Validator

- slot_choices_for_seed 返回已实现的 module 名（4×2×3 命名空间）
- config_from_seed 对所有普通 seed（含 0）用 deterministic 程序采样
- compatibility gating 阻止非法组合（traveling+table/tube、dual+tube、cantilever+tube）→ fallback
- 无 regression overrides（首版）
- 主 seed domain 非小型 curated/modulo 表
- pinion_teeth/N/face_scale clamp，不破坏啮合 z 关系、轴承接口、multiplicity
- 跨部件 scale 依赖（rack_travel≤pitch_radius、base≥rack_half+travel+margin）在 resolve_config 求解
- 关键接口存在：pinion axle-in-collar 捕获（allow_overlap）、pinion↔rack 啮合（allow_overlap/相位）、rack 悬 rail 上方（PRISMATIC）
- 关键 joint 类型/轴：pinion_spin REVOLUTE axis(0,-1,0)；rack_slide/carriage PRISMATIC axis(1,0,0)；dual 两个 REVOLUTE；traveling PRISMATIC parent=frame,child=pinion_carriage
- 复制件命名/布局：rack_tooth_{i}/pinion_tooth_{i}/pinion_{k}/table_slot_rib_{i} 索引稳定

## Reject cases

- pinion 不带齿 / rack 不带齿（退化成光轴滑台，失类别 identity）
- 缺 REVOLUTE 或缺 PRISMATIC（不再是 rack-and-pinion）
- pinion 齿在旋转全程与 rack 齿实碰穿模（相位/clearance 错，未声明啮合 allow_overlap）
- rack_carriage / pinion 漂浮（未经啮合或轴承与 frame 连通 → isolated part）
- rack_slide 行程超出 base 承托或撞 rail_stop（travel 未回缩）
- 关节 origin 远离硬件（pinion_center 未落在 axle/collar，PRISMATIC 例外）
- enclosed housing 壳与 pinion/rack 运动全程碰撞（aperture/内腔尺寸不足）
- 装饰（rib/label）以常数半径套在圆 rack / 缩放体外悬空（未共形派生）
- 用 cadquery 重布尔导致 >20s/seed 编译（超预算）

## 与相邻类别的边界

- 不该混入：丝杠/滚珠丝杠线性执行器（螺旋驱动、无齿条齿啮合）
- 不该混入：皮带/同步带线性滑台（柔性带、无齿轮啮合）
- 不该混入：纯线性导轨 / LM guide / 交叉滚子台（完全无齿轮驱动）
- 不该混入：旋转齿轮箱 / 蜗轮驱动（无直线 rack 件）
- 不该混入：带拉杆的汽车转向 rack（变成整车转向总成）
- 不该混入：弧形/扇形/斜齿 rack（漂向扇齿/蜗杆邻类）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 首版 spec；3 slot（4×2×3）+ rack 齿 N multiplicity；pinion 支撑/数量折入 drive_skeleton 候选以避免非法组合；两非-FIXED 关节皆机械捕获(轴承/啮合)故 grandfathered（无 MatingContract），啮合与轴承过盈以 element-scoped allow_overlap 声明；全 SDK 原语无 cadquery。 |

## 模板实现备注（可选）

- 共享 helper：`_trapezoid_prism`（齿 mesh，源自 B:L21-L67）；`_GearGeom`（单一来源锁定所有 z 高度/半径/pitch，Contract 3c）；`_build_pinion`（源自 dual fork L70-L114）；`_emit_rack_teeth`；`_build_frame_supports`。
- 无 MatingContract：pinion_spin（pin-through-bore 捕获轴承）与 rack_slide（悬空滑轨，rack 与 rail 间有意留 gap，声明 MatingContract 会触发 gap 检查失败）皆 grandfathered。
- captured/mesh overlap 需 element-scoped `allow_overlap`：pinion axle ↔ bearing_collar/boss/hub（journal fit）；pinion ↔ rack（齿啮合交错）；cantilever 的 bearing_boss ↔ hub。
- 暂不进 seed domain 的组合：traveling_pinion+enclosed/table、dual+enclosed、cantilever+enclosed（gating fallback bare_open）。
- Rule 5：run_tests 调 `fail_if_parts_overlap_in_sampled_poses`（allowances 已声明）+ targeted `ctx.pose` 耦合运动检查。
