# Technology_Telescope — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `Technology_Telescope` |
| template path | `agent/templates/Technology_Telescope.py` |
| test path (optional) | `tests/agent/test_Technology_Telescope_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（root→mount head 串成链 + optical_tube 挂到 mount 的 tilt 轴 + focuser / telescoping-leg 子件复制） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 (2 origins + 7 forked variants) |
| read_count | 9 |
| read_scope | all 5-star telescope sources in the source map（`model.py` 全量逐行读，无采样） |
| samples_adopted_as_module_sources | 9 |
| source_index_policy | 每个 candidate/机制都引到真实 `model.py:Lx-Ly` |

两个结构族（都是 optical-axis-along-+X 的望远镜，root→mount→OTA→focuser 链）：

- **Spyglass 族**（origin A + pillar 变体 + drawtube_segments 变体）：leather CadQuery loft 主筒 + brass objective_ring/lens + rear_collar + 铁 saddle_lug；mount = brass yoke_block + iron trunnion fork（`trunnion_plate_{side}` + `pivot_axle`）；root = 木三脚架 或 turned pillar_stand；focuser = 后置 brass draw-tube（单节 或 N=3 嵌套 `draw_segment_{i}`）。关节：`azimuth_rotation`(CONTINUOUS Z) + `altitude_tilt`(REVOLUTE −Y) + `drawtube_extend`/`draw_segment_{i}_extend`(PRISMATIC −X)。
- **Refractor/Reflector/Mak/EQ/Dob 族**（origin B + reflector + maksutov + equatorial + dobsonian + legs_telescoping 变体）：CadQuery loft `tube_shell` + `blue_band`/`dew_shield`/`objective_ring`/`cradle_ring`/`focuser_housing`；mount = alt-az U-yoke（`yoke_cheek_{side}` + `tilt_boss_{side}`）/ German EQ（tilted polar + `dec_bar` + counterweight）/ Dobsonian rocker box / metal 三脚架；focuser = `focuser_drawtube`（barrel，rear −X 或 reflector 的 radial +Z）。关节：`azimuth_rotation`(CONTINUOUS Z / tilted polar) + `tube_altitude`(REVOLUTE −Y) + `focuser_slide`(PRISMATIC −X/+Z) + telescoping `leg_extend_{i}`(PRISMATIC)。

逐条来源：

- S1 `rec_brass-and-leather-refractor-spyglass-telescope-o_20260605_173839_625665_87949333`（origin A）— 木三脚架 + trunnion fork + leather spyglass + 单 draw-tube。`model.py:L166-L289`(tripod+head)、`L302-L373`(tube+drawtube)、`L384-L419`(3 joints)。
- S2 `rec_small-refractor-telescope-on-an-adjustable-tripo_20260605_173830_455032_6d2f7e30`（origin B）— metal 三脚架 + U-yoke + banded refractor + focuser drawtube。`model.py:L82-L214`(tripod+head)、`L231-L343`(tube+focuser+joints)。
- S3 `rec_telescope_var_mount_dobsonian` — ground_board + rocker box + refractor tube。`model.py:L104-L211`(ground+rocker+az)、`L216-L340`(tube+alt+focuser)。
- S4 `rec_telescope_var_mount_equatorial` — 三脚架 + German EQ（tilted polar + dec_bar + counterweight）。`model.py:L176-L267`(head+RA joint)、`L275-L393`(tube+DEC+focuser)。
- S5 `rec_telescope_var_mount_pillar` — turned brass pillar_stand + trunnion fork + leather spyglass。`model.py:L195-L285`(pillar+head)、`L298-L415`(tube+drawtube+joints)。
- S6 `rec_telescope_var_tube_reflector` — Newtonian：fat short open tube + spider + 侧置 focuser（radial +Z）。`model.py:L242-L387`(tube+side focuser+slide)。
- S7 `rec_telescope_var_tube_maksutov` — 短胖 catadioptric：front corrector + rear_cell + rear focuser。`model.py:L283-L419`(tube+focuser)。
- S8 `rec_telescope_var_legs_telescoping` — 三脚架 telescoping legs：`leg_upper_{i}` visual + `leg_lower_{i}` 独立 part + `leg_extend_{i}` PRISMATIC。`model.py:L92-L218`(helper)、`L253-L288`(3 legs)。
- S9 `rec_telescope_var_drawtube_segments` — spyglass N=3 嵌套 `draw_segment_{i}` + `draw_segment_{i}_extend` PRISMATIC 链。`model.py:L129-L177`(seg mesh)、`L386-L477`(chain build)。

## 核心身份

带 grounded 支座（三脚架 / 落地 rocker box / 台面 pillar 柱）的天文/观测望远镜：**必须有一支可指向天空的光学筒（OTA，含 objective / corrector / mirror cell 身份件）+ 至少两级指向关节**（典型 azimuth CONTINUOUS + altitude/DEC REVOLUTE），可选调焦（focuser draw-tube PRISMATIC，单节或嵌套多节）。默认成熟域 = **三脚架 alt-az refractor / brass-leather spyglass**；EQ / Dobsonian / pillar / catadioptric 均为 source-backed 候选。

不该缺：OTA、azimuth、altitude 三者缺一不可（纯装饰筒 / 无指向自由度不算）。

## 槽位 + 候选模块表

### Slot A：optical_tube family（③ Volumetric Envelope / focuser 放置）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `leather_tapered_spyglass` | forked_anchor | S1 / S5 / S9 | S1 `model.py:L302-L373` | eligible if compatible | leather CadQuery loft 锥形主筒 + brass objective_ring/lens + rear_collar + 铁 saddle_lug；后置 draw-tube（单节或 N 嵌套）；tube 半径 ~0.046 |
| `banded_straight_refractor` | forked_anchor | S2 | S2 `model.py:L231-L276` | eligible if compatible | 直筒 CadQuery `tube_shell` + `blue_band` + `dew_shield` + `objective_ring` + `cradle_ring` + `focuser_housing`；后置 barrel focuser；半径 ~0.030 |
| `reflector_newtonian` | forked_anchor | S6 | S6 `model.py:L242-L320` | eligible if compatible | 短胖开口筒 + spider vane×4 + `secondary_mirror_hub` + `mirror_cell`/`primary_mirror` + **侧置** focuser（radial +Z）；半径 ~0.032 |
| `maksutov_catadioptric` | forked_anchor | S7 | S7 `model.py:L283-L351` | eligible if compatible | 短胖闭口 catadioptric：front `corrector_lens` + `front_ring` + `rear_cell` visual back + rear barrel focuser；半径 ~0.044 |

四个 candidate 覆盖 Volumetric Envelope 主要边界（long-thin refractor ↔ short-fat catadioptric ↔ open reflector ↔ tapered spyglass），part tree/interface 同构（都是 optical_tube part，tilt pivot 在 local 原点，focuser 为 child prismatic），只换主体形态原型 + focuser 放置。均 source-backed，无需 world_knowledge 额外 candidate。

### Slot B：mount family（①/② 最强结构轴 — root support + 指向关节拓扑）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `alt_az_trunnion_tripod` | forked_anchor | S1 | S1 `model.py:L166-L289` | eligible if compatible | 木三脚架（spline `leg_{i}`+`foot_{i}`+`spreader_{i}`）+ brass `yoke_block` + iron `trunnion_plate_{side}` + `pivot_axle`；az CONTINUOUS Z + tilt REVOLUTE −Y |
| `alt_az_uyoke_tripod` | forked_anchor | S2 | S2 `model.py:L82-L214` | eligible if compatible | metal 三脚架 + `az_turntable`/`az_post` + U-yoke `yoke_cheek_{side}` + `tilt_boss_{side}`；az CONTINUOUS Z + tilt REVOLUTE −Y |
| `equatorial_eq_counterweight` | forked_anchor | S4 | S4 `model.py:L176-L267` | eligible if compatible | 三脚架 + `polar_wedge`（tilted LAT）+ `polar_housing` + `dec_bar` + `cw_shaft`/`cw_ball`；az CONTINUOUS about tilted polar + DEC REVOLUTE |
| `dobsonian_rocker_box` | forked_anchor | S3 | S3 `model.py:L104-L211` | eligible if compatible | **无三脚架**：round `ground_board` + 方 rocker box（两 `side_board_{side}` + `front_brace`）；az CONTINUOUS Z(ground→rocker) + tilt REVOLUTE −Y(alt bearing) |
| `tabletop_pillar_stand` | forked_anchor | S5 | S5 `model.py:L195-L285` | eligible if compatible | 台面：CadQuery lathe `base_disc` + turned `center_post` + `pedestal_collar` + trunnion fork（同 S1 head）；az CONTINUOUS Z + tilt REVOLUTE −Y；无腿 |

5 个 candidate，root（三脚架 ↔ 落地 rocker ↔ 台面柱）与 mount 指向拓扑（trunnion fork ↔ U-yoke ↔ tilted-polar EQ ↔ rocker altitude bearing）均结构不同。任何 mount 通过一根穿过 tube 中心的 `pivot_axle`/`dec_bar`（captured pin，允许 overlap）承接 OTA，fork/yoke 间距由 `tube_outer_radius` 派生 → mount×OTA 自由组合。

## 槽位图（slot graph）

pattern: `mixed`

```
[Slot B root+mount]
   -- azimuth_rotation (CONTINUOUS, +Z or tilted polar; origin = bearing symmetry axis) -->
[mount head part]
   -- tube_altitude (REVOLUTE, -Y / DEC; origin = pivot axle line through tube center @ x=0) -->
[Slot A optical_tube]
   -- focuser_slide (PRISMATIC, -X or +Z; captured barrel) --> [focuser_drawtube]
      或 draw_segment_0_extend → ... → draw_segment_{N-1}_extend (nested PRISMATIC 链)
[Slot B tripod mounts]（M1 telescoping 时）
   -- leg_extend_{i} (PRISMATIC, 沿 splay; origin = junction) --> [leg_lower_{i}] × 3
```

接口点位：
- **azimuth**：root 顶面 bearing 面（pedestal_collar / az_turntable / ground_board top / pillar 顶）；轴 = 竖直 Z（EQ 为 tilted polar，用 rpy 倾斜 head 帧）；origin 在 bearing 对称轴上（旋转关节按 symmetry-centerline 通过 origin honesty）。head 的 azimuth_ring/turntable 座在 root 顶（small embed 允许）。
- **tube_altitude**：mount 提供 tilt 轴锚点（head-local xyz + fork half-spacing = `tube_outer_radius + margin`）；一根 `pivot_axle`/`dec_bar` 沿 Y/X 穿过 tube 中心 → 保证 tube↔head 接触（captured pin allow_overlap）。OTA 在 tube-local 原点 = tilt pivot，optical axis +X。
- **focuser**：OTA 自带（barrel 插进 `focuser_housing` bore，或 nested `draw_segment` 插进 rear_collar bore）；PRISMATIC。
- **leg_extend**（仅 tripod mounts + M1=telescoping）：upper leg visual 在 tripod part，lower leg 独立 part，junction 处 PRISMATIC。

互斥 / 派生：`leg_extend` 仅在 root 为三脚架的 mount（trunnion / uyoke / equatorial）出现；dob / pillar 无腿。`draw_segment` 嵌套链仅 `leather_tapered_spyglass`（其余 OTA 单节 barrel）。

## 每槽位 Module Emits / Interfaces

### Slot A / optical_tube（各 candidate）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `optical_tube`（tube-local 原点 = tilt pivot，+X 光轴）；focuser child：`focuser_drawtube` 或 `draw_segment_{i}` | S1/S2/S6/S7 |
| internal joints | `focuser_slide`(PRISMATIC −X/+Z) 或 `draw_segment_{i}_extend`(PRISMATIC −X 链) | S2 L335-L343 / S9 L451-L477 |
| upstream interface | tube-local 原点处的 cradle/saddle（被 mount 的 pivot_axle 穿过）；`focus_knob` 离轴（azimuth witness） | S1/S2 |
| downstream interface | focuser child 的 barrel/segment 插入 bore（captured，allow_overlap） | S2/S9 |

### Slot B / mount（各 candidate）
| emits | 描述 | 来源 |
|---|---|---|
| parts | root（`tripod`/`ground_board`/`pillar_stand`）+ head（`azimuth_head`/`rocker_box`）；telescoping 时 `leg_lower_{i}` | S1-S5/S8 |
| internal joints | `azimuth_rotation`(CONTINUOUS)；EQ 用 rpy 倾斜 polar；`leg_extend_{i}`(PRISMATIC) | S1/S4/S8 |
| upstream interface | root 顶 bearing 面座地（feet z≈0 / disc z≈0） | S1-S5 |
| downstream interface | tilt 轴锚点（head xyz + fork half-spacing）+ 穿心 `pivot_axle`/`dec_bar` | S1/S2/S4 |

活动件全部为独立 part + articulation；不动细节（rings/bands/dew_shield/spider/foot_pad/marker）写成 host part visual，不作独立 part。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `ota_style` | enum | leather_tapered_spyglass / banded_straight_refractor / reflector_newtonian / maksutov_catadioptric | banded_straight_refractor | choice | deterministic 采样 | Slot A |
| `mount_family` | enum | alt_az_trunnion_tripod / alt_az_uyoke_tripod / equatorial_eq_counterweight / dobsonian_rocker_box / tabletop_pillar_stand | alt_az_uyoke_tripod | choice | deterministic 采样 | Slot B |
| `palette_style` | enum | brass_leather / blue_white / matte_white_reflector / pearl_orange / graphite_black / green_enamel | blue_white | choice | rng.choice(PALETTE_STYLES) | 6 源 livery |
| `leg_mechanism` | enum | fixed / telescoping | fixed | conditional | 仅 root=三脚架 的 mount 可 telescoping；dob/pillar 强制 fixed | S8 |
| `drawtube_segment_count` | int | [1,4] | 1 | conditional | 仅 ota=leather_spyglass 时 >1（嵌套 N 节）；其余强制 1 | S9 (N=3) |
| `tube_scale` | float | [0.90, 1.15] | 1.0 | independent | 均匀采样后 clamp；同缩 length+radius（保形） | S1/S2/S6/S7 |
| `tube_outer_radius` | float | derived | 见 base | equation | `= BASE_R[ota] * tube_scale`；mount fork 间距、focuser 尺寸都读它 | Slot A |
| `tube_length` | float | derived | 见 base | equation | `= BASE_L[ota] * tube_scale` | Slot A |
| `mount_scale` | float | [0.90, 1.15] | 1.0 | independent | 缩放三脚架高度 / pillar 高度 / rocker 尺寸 | S1/S2 |
| `tilt_lower/upper` | float | 固定 per mount | 源值 | conditional | trunnion/uyoke/pillar [−30°,+60°]；EQ DEC [−15°,+75°]；dob [−30°,+45°] | S1-S7 |
| (—) | constraint | — | — | inequality | fork_half_spacing `= tube_outer_radius + 0.006`（保证 yoke/plate 恰好夹到 cradle，不悬空不过深） | 接口 |

连续尺寸采样契约：先采 `tube_scale`/`mount_scale`（independent）→ 派生 `tube_outer_radius`/`tube_length`（equation）→ fork 间距 inequality 由 radius 投影 → `leg_mechanism`/`drawtube_segment_count`/`tilt_*` conditional 按上游 enum 解析。全部在 `resolve_config` 求解。

## 7.5 编译预算 / compile budget
自报预算 **≤18s/seed**（每 seed 只造一个 OTA + 一个 mount；各源单独 compile 均 <15s）。CadQuery loft（leather body / tube_shell / lathe post / draw segments）用 `tolerance=0.001, angular_tolerance=0.08`；tube_from_spline_points 腿 `radial_segments≤16`；Cylinder/Sphere 默认段数；嵌套 draw segment 各自 mesh（N≤4，几何小）。sweep `--compile-timeout 120`（≈6× 预算，纯 watchdog）。

## Multiplicity / Copy Logic

**两根独立复制轴 + 固定三腿复制。**

- **固定复制：tripod legs N=3** — copied object = splayed leg；naming `leg_{i}`/`foot_{i}`/`spreader_{i}`（equiangular 120°, base π/2）；joint policy = legs 为 tripod part 的 module-local visual 循环（FIXED 融进 root part，非独立 part）。N 固定 3，不采样（三脚架就是 3 腿）。
- **M1 count_param（机制轴，非 N）：`leg_mechanism` ∈ {fixed, telescoping}** — telescoping 时每腿加 `leg_upper_{i}`(tripod visual) + `leg_lower_{i}`(独立 part) + `leg_extend_{i}`(PRISMATIC 沿 splay，travel [0,0.05])。仅三脚架 root（trunnion/uyoke/equatorial）；dob/pillar 强制 fixed。source=S8。
- **M2 count_param：`drawtube_segment_count` N ∈ [1,4]** — copied object = 同心 brass draw-tube 段；naming `draw_segment_{i}`；placement = 沿 −X 递减半径嵌套；joint policy = linear_chain，每段自己的 PRISMATIC（seg0 出 rear_collar，segi 出 seg{i-1}），eyecup 在最内段。仅 `leather_tapered_spyglass`（其余 OTA 单节 `focuser_drawtube`）。N 采样域：小 N 高频（1/2 常见，3/4 稀有），source=S9(N=3)。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | mount family 换 root+指向拓扑（trunnion fork / U-yoke / tilted-polar EQ+counterweight / dob rocker box / pillar）；OTA 换筒族；focuser 单 barrel ↔ 侧 focuser ↔ 嵌套 N 段；telescoping legs 增 3 个 lower-leg part。全部 forked_anchor（S1-S9），无 world-knowledge 新骨架。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：tripod legs N=3 固定；`leg_mechanism`(fixed/telescoping)；`drawtube_segment_count` N∈[1,4] 加权。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | azimuth CONTINUOUS(Z / tilted polar RA)；altitude/DEC REVOLUTE(−Y)；focuser PRISMATIC(−X rear / +Z radial reflector)；telescoping-leg PRISMATIC(splay)。每 mount ≥2 non-fixed 指向自由度。全 forked_anchor（S1-S8），每种 type 在 sweep 出现。 |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有（登记进 slot_choices=ota_style） | source-backed Volumetric Envelope：`leather_tapered_spyglass`(tapered loft)、`banded_straight_refractor`(long-thin 直筒)、`reflector_newtonian`(short-fat open)、`maksutov`(stubby closed)。每 candidate form_subtype=Volumetric Envelope Form（三维包络/长径比/开闭口）。 |
| ④ 表面装饰 | 原型不变叠表面细节 | 有 | record_only：brass objective/rear rings、leather 缠绕、blue_band、orange_band、dew_shield、spider vanes、`focus_knob`、`azimuth_marker`、mirror faces、counterweight。均写成宿主 part visual，随 ③⑤ 尺寸派生（band 半径 = tube_outer_radius + δ，共形嵌入）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | `tube_scale`[0.9,1.15]、`mount_scale`[0.9,1.15]；tube L:R 随 ota。运动包络：azimuth CONTINUOUS(整圈)；tube_altitude REVOLUTE 轴−Y，正角抬 objective：trunnion/uyoke/pillar [−30°,+60°]、EQ DEC [−15°,+75°]、dob [−30°,+45°]；focuser PRISMATIC [0,0.03]（spyglass draw [0,0.05]）；leg_extend [0,0.05]。motion_test_plan：靠 baseline `harness_motion_qc`（sampled poses，honor allow_overlap）+ targeted `ctx.pose`：tilt→抬前端、azimuth→摆 focus_knob/marker、focuser→伸出；EQ/dob/telescoping 在 limit pose 加 `fail_if_parts_overlap_in_current_pose`。captured-pin(pivot_axle/dec_bar)、telescoping、nested、barrel-insert 全声明 allow_overlap，故不需要 sampled-pose exemption。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal(brass/chrome/anodized) + painted(white/blue/orange/black/green) + leather/wood + glass。`palette_style` ≥6 livery：brass_leather / blue_white / matte_white_reflector / pearl_orange / graphite_black / green_enamel。材质大类覆盖 ≥ ceil(0.5×6)=3（metal+painted+glass+leather 均现）。 |

**收尾自检**：0-9 seed 渲染须肉眼见到 4 种筒族 + 5 种 mount + 多种 livery，装饰贴合筒面不悬空，关节全程不穿模。

## 拓扑多样性审计

总组合数：ota(4) × mount(5) × leg_mechanism(≤2) × drawtube_N(≤4) × palette(6) ≫ 200（离散骨架/拓扑组合，未计连续 scale）。M1/M2 conditional，有效独立骨架组合 ota×mount=20，叠 leg/N 机制 ~60+。


seed_domain_policy：`procedural_first`。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)`（seed=0 不特殊）用 `random.Random(seed)` 加权采样 `mount_family`（均匀 5 选）、`ota_style`（refractor/reflector/mak 各 ~0.25，spyglass ~0.25）、`palette_style`（均匀 6 选）、`tube_scale`/`mount_scale`（[0.9,1.15] 均匀）；`leg_mechanism` 仅三脚架 mount 时 ~0.35 telescoping；`drawtube_segment_count` 仅 spyglass 时按 {1:0.45,2:0.30,3:0.17,4:0.08} 加权，其余强制 1。compatibility：mount×ota 全自由（fork 间距派生自 radius，focuser 由 OTA 自持）；`resolve_config` clamp scale + 解析 conditional。无 curated/modulo 主表。regression overrides：none。1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；ota×mount×leg×N 提供 ≥60 骨架，低于 300 时记录离散空间上限；scale 只补比例多样性。random sweep 0-35 初验，viewer 目检 0-9。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 加权 mount/ota/palette + conditional leg/N；`slot_choices_for_seed` 与 build 一致 | slot_choices 匹配 |
| compatibility matrix | mount×ota 全合法；leg_mechanism gated by tripod root；N gated by spyglass | 无 floating/collision/axis/max-multiplicity 失败 |
| controlled local variation | `tube_scale`/`mount_scale` clamp；fork 间距、focuser 尺寸 derived | 比例变化不破接口/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 初验，0-999 成熟审计 | contract failures；axis_realization |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| optical_tube (A) | 4 | yes | yes | |
| mount_family (B) | 5 | yes | yes | |
| leg_mechanism (M1) | 2 | yes | no | conditional（仅三脚架） |
| drawtube_segments (M2) | 4 (N) | yes | yes | conditional（仅 spyglass）；N 只覆盖不计 distinct |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名（ota_style / mount_family / leg_mechanism / drawtube_segment_count / palette_style）。
- `config_from_seed` 对所有普通 seed（含 0）用 deterministic 采样。
- compatibility gating 阻止非法组合（telescoping 只在三脚架；N>1 只在 spyglass）。
- controlled scale 全在 `resolve_config` clamp/derive，不破接口。
- 关键关节 type/axis：azimuth CONTINUOUS、tube_altitude REVOLUTE −Y、focuser/leg PRISMATIC；正 tube_altitude 抬前端。
- captured pin / telescoping / nested / barrel-insert 用 element-scoped allow_overlap。
- 每 seed ≥1 non-fixed 关节（实际 ≥2 指向 + focuser）。

## Reject cases

- 缺 OTA，或 OTA 无 objective/corrector/mirror 身份件。
- 指向自由度 < 2（除 focuser 外）。
- tube_altitude 轴与光轴（+X）平行（语义错误）。
- telescoping 出现在 dob/pillar（无腿 root）。
- draw segment 悬空（未嵌套进上游 bore）/ tube 悬空（fork 未夹到 cradle）。
- fork 间距与 tube 半径不匹配导致 tube 悬空或过深穿模。
- 连续 scale 未 clamp 导致 tube 撞 mount/legs。

## 与相邻类别的边界

- 不该混入：`astronomical_telescope_on_tripod`（同物但独立 slug；本 slug 由 telescope 小类 9 源新造，几何不共享）。
- 不该混入：`parabolic_dish_on_azimuth_elevation_mount`（射电/卫星 dish，非 OTA）。
- 不该混入：`radio_telescope`（dish reflector，无光学 objective/corrector）。
- 不该混入：binocular / camera pan-tilt / camera_lens（非 astronomical single OTA）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | spec 由 telescope 小类 9 源（2 origin + 7 变体）全量阅读产出；直接进入模板实现 |
