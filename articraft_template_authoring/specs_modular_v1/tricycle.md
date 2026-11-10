# Modular Spec — tricycle (0611)

## 元信息
| 项 | 值 |
|---|---|
| slug | `tricycle` |
| template path | `agent/templates/tricycle.py` |
| test path (optional) | `tests/agent/test_tricycle_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：`chassis`（root，由 frame_form 决定 tube 拓扑与轮布局）挂 parallel
children —— `steering`（REVOLUTE，携 fork/handlebar/front wheel(s)）、`pedal_crank`
（REVOLUTE，drive slot 决定 parent 是 steering 还是 chassis）、rear wheel(s)（CONTINUOUS，
child of chassis）、`saddle`（FIXED，seat_count 多副）、`rear_module`（FIXED）。轮的
front/rear 拆分与 track 由 frame_form 派生（delta = 1 front + 2 rear；tadpole = 2 front + 1 rear）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 16 |
| read_count | 16 |
| read_scope | origin anchor + all 15 built forked variants under `data/records/rec_0611_tricycle_var_*` |
| source_index_policy | only adopted module sources are indexed below |

阅读要点：origin（`rec_picturex_0611__tricycle__001…`）是一辆前轮直驱童车三轮车 ——
一根曲线 tube spine 的 `chassis`（含 head tube、rear axle、cargo deck、seat post、fenders），
REVOLUTE `steering`（stem+bearing+fork_crown+fork legs+handlebar+grips+front fender+front
basket）绕 (0,0,1) 转，CONTINUOUS 前轮（大）+ 两个 CONTINUOUS 后轮（小），REVOLUTE
`pedal_crank`（child of steering，spindle 穿前轮 hub）+ 两个 CONTINUOUS `pedal`。所有 helper
（`_annular_sector_y` 弧形挡泥板、`_wheel_visuals` 模制轮、`_rounded_open_bin` / `_rounded_ring`
篮筐、`_tube_visual` 样条 tube、cadquery head tube）在全部 fork 中共享。fork 只在单一结构轴上
改写：frame_topology（改 chassis tube spline / 轮布局）、steering（改 steering 部件与关节轴）、
drive（改 crank parent + chainring/shaft 几何）、rear_module（cargo basket↔passenger bench）、
seat_count（1/2/3 副座椅 + 座管）。

## 核心身份

三轮人力踏板车：三个着地车轮（delta = 单前双后 / tadpole = 双前单后）、一个可转向前端、
至少一个 saddle、人力踏板驱动、以及一个后部承载层（货筐 / 座凳 / 平板）。默认成熟域是童车/
载货三轮车比例（前轮直驱或车架中置驱动）。核心非固定关节：转向 REVOLUTE + 每轮 CONTINUOUS
滚动 + 曲柄 REVOLUTE + 踏板 CONTINUOUS。

不该混入：两轮 bicycle（缺第三个着地轮 + 无货/座承载层）；四轮 pedal cart（第四轮 →
非 tricycle）。

## 槽位 + 候选模块表

### Slot A：frame_form（③ Primary Form Family + ① skeleton；root=chassis）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| low_step_child | origin_anchor | rec_picturex_0611__tricycle__001 | L193-L323 | eligible if compatible | delta 布局；低跨曲线 tube spine + 座背撑，童车比例。form_subtype=Volumetric Envelope Form |
| delta_adult | forked_anchor | rec_0611_tricycle_var_frame_topology_delta_adult_frame | L193-L324 | eligible if compatible | delta；直立成人三角车架（上管+下管+立管）。form_subtype=Planar Boundary Form |
| cargo_trike | forked_anchor | rec_0611_tricycle_var_frame_topology_front_cargo_box_frame | L193-L340 | eligible if compatible | delta；长直平台车架（载货比例）。form_subtype=Macro Surface Construction |
| drift_trike | forked_anchor | rec_0611_tricycle_var_frame_topology_drift_trike_frame | L193-L300 | eligible if compatible | delta；低矮后倾宽后轴 drift 车架。form_subtype=Volumetric Envelope Form |
| tadpole_twin_front | forked_anchor | rec_0611_tricycle_var_frame_topology_tadpole_two_front_frame | L193-L360 | eligible if compatible | tadpole：两条前置载重 rail 张开 + crossmember，双前轮单后轮。form_subtype=Planar Boundary Form |

### Slot B：steering_form（② joint / mechanism；child of chassis，携前轮）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| direct_fork | origin_anchor | rec_picturex_0611__tricycle__001 | L381-L507 | eligible if compatible | 竖直 kingpin (0,0,1)；stem+bearing+fork_crown+fork legs 直接携前轮 |
| linkage | forked_anchor | rec_0611_tricycle_var_steering_linkage_steering | L381-L470 | eligible if compatible | 竖直轴；前移 control stem + upper/lower steering links + link bosses 绑到 kingpin，一个刚性转向层 |
| lean | forked_anchor | rec_0611_tricycle_var_steering_lean_steering | L381-L470 | eligible if compatible | 后倾 lean 轴 `(-sin θ,0,cos θ)` 穿前轴；stem 沿斜轴，upper clamp tube |

### Slot C：drive_form（② joint / mechanism；pedal_crank + 2 pedals）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| front_direct_pedals | origin_anchor | rec_picturex_0611__tricycle__001 | L519-L580,L635-L661 | eligible if front_count==1 | 曲柄 child of steering，spindle 穿前轮 hub 直驱；仅单前轮合法 |
| mid_drive_freewheel | forked_anchor | rec_0611_tricycle_var_drive_mid_drive_freewheel | L23-L60,L200-L260 | eligible if compatible | 车架中置 bottom-bracket 曲柄（child of chassis）+ 齿盘 chainring 装饰 |
| shaft_drive | forked_anchor | rec_0611_tricycle_var_drive_shaft_drive | L23-L60,L200-L260 | eligible if compatible | 车架中置曲柄（child of chassis）+ 到后轴的 driveshaft tube + bevel 壳装饰 |

### Slot D：rear_module（① skeleton / ③ 承载层；FIXED child of chassis）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| cargo_basket | origin_anchor | rec_picturex_0611__tricycle__001 | L326-L343 | eligible if compatible | 圆角开口货筐 shell + rim + 前加强板 |
| passenger_bench | forked_anchor | rec_0611_tricycle_var_rear_module_passenger_bench | L200-L340 | eligible if compatible | 两人座凳：cushion + 侧栏 + 靠背/脚踏，rounded slab |
| flat_deck | world_knowledge_extrapolation | anchors: cargo_basket + passenger_bench + reviewer | 生成函数 `_rear_flat_deck` | eligible if compatible | ③ Macro Surface Construction：平板货台 + 边梁，同 part tree/interface（FIXED slab）只改主体形态 |

### Slot E（multiplicity）：seat_count（N=1/2/3；saddle part 承 N 组座 + chassis 承 N 个座管）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| seats_1 | origin_anchor | rec_picturex_0611__tricycle__001 | L346-L378 | eligible if compatible | 单模制 saddle（base+cushion+backrest）+ 单座管 |
| seats_2 | forked_anchor | rec_0611_tricycle_var_seat_count_2_seats | L23-L70,L346-L400 | eligible if compatible | 两组 saddle 沿 x 排列 + 两座管 |
| seats_3 | forked_anchor | rec_0611_tricycle_var_seat_count_3_tandem_seats | L23-L80,L346-L420 | eligible if compatible | 三组 tandem saddle + 三座管 |

硬约束满足：A 5 个 / B 3 个 / C 3 个 / D 3 个候选（均 ≥3），E multiplicity 3 档。每个普通
①/② candidate 都有 `forked_anchor`/`origin_anchor` 与真实行号；flat_deck 为 ③
`world_knowledge_extrapolation`（form_subtype=Macro Surface Construction，同 part tree/FIXED
interface，只改主体形态）。

## 槽位图（slot graph）

pattern: mixed

```
chassis (root, frame_form A; 提供 head-tube-top pivot / front-axle anchor / rear-axle anchor /
         seat-post ref / rear-deck top face)
   |
   |--[REVOLUTE axis(steering_form) @ head-tube-top]--> steering (B)
   |                                                       |
   |                                                       '--[CONTINUOUS y @ front axle]--> front_wheel(s)
   |
   |--[REVOLUTE y @ crank origin]--> pedal_crank (C)   (parent = steering if front_direct else chassis)
   |                                     '--[CONTINUOUS y]--> pedal_0, pedal_1
   |
   |--[CONTINUOUS y @ rear axle ±track]--> rear_wheel(s)
   |
   |--[FIXED @ seat-post top]--> saddle (E: N 组座视觉)
   |
   '--[FIXED @ rear-deck top face]--> rear_module (D)
```

- 跨 slot 接口点位：steering ↔ chassis = head-tube 内孔（bearing 压入，captured pin，无
  MatingContract，`allow_overlap`）；front wheel ↔ steering = fork-end 轴孔（captured hub）；
  rear wheel ↔ chassis = rear axle 孔（captured hub）；crank ↔ parent = bottom-bracket / 前轴孔
  （captured spindle）；pedal ↔ crank = pedal 轴（captured）；saddle ↔ chassis = 座管顶面接触
  （FIXED，物理接触）；rear_module ↔ chassis = cargo deck 顶面接触（FIXED，物理接触）。
- 互斥/派生：front_direct_pedals 仅当 front_count==1（delta）合法，tadpole → 降级 mid_drive_freewheel。
  前轮数量、后轮数量、track、轮半径均由 frame_form 派生。

## 每槽位 Module Emits / Interfaces

### Slot A / module frame_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | `chassis`（root）：frame tube visuals + head_tube + head collars + rear_axle stub + cargo_deck + seat posts + fenders + (tadpole) front rails/crossmember | origin L193-L323 + frame forks |
| internal joints | 无（root part 内部无关节） | — |
| upstream interface | root（无 upstream） | — |
| downstream interface | head-tube-top pivot (steering) / front-axle anchor / rear-axle anchor / seat ref / rear-deck top | origin L582-L661 |

### Slot B / module steering_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | `steering`：stem+bearing+fork_crown+fork legs+handlebar+grips+front fender(+links / +lean clamp) | origin L381-L507 |
| internal joints | 无（前轮为独立关节，见下） | — |
| upstream interface | head-tube 内孔；joint = REVOLUTE，axis 依 steering_form，range ±0.55 | origin L599-L607 |
| downstream interface | fork-end 前轴孔 → front wheel CONTINUOUS y | origin L608-L616 |

### Slot C / module drive_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pedal_crank` + `pedal_0` + `pedal_1`；chassis 上加 chainring/shaft 装饰视觉 | origin L519-L580 |
| internal joints | `crank_joint` REVOLUTE y (±π)；`pedal_i_spin` CONTINUOUS y | origin L635-L661 |
| upstream interface | crank origin（steering 前轴孔 or chassis bottom-bracket），captured spindle | origin L635-L643 |
| downstream interface | pedal 轴孔（captured） | origin L644-L661 |

### Slot D / module rear_module
| emits | 描述 | 来源 |
|---|---|---|
| parts | `rear_module`（basket shell/rim / bench slab / flat deck slab） | origin L326-L343 |
| internal joints | 无 | — |
| upstream interface | cargo deck 顶面接触，FIXED | origin L582-L589 |
| downstream interface | 无 | — |

### Slot E / seat_count
| emits | 描述 | 来源 |
|---|---|---|
| parts | `saddle`（承 N 组 base+cushion+backrest 视觉）；chassis 上 N 个座管视觉 | origin L346-L378 + seat forks |
| internal joints | 无（saddle FIXED 于 chassis） | origin L590-L596 |
| upstream interface | 座管顶面接触，FIXED | origin L590-L596 |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| frame_form | enum | low_step_child/delta_adult/cargo_trike/drift_trike/tadpole_twin_front | — | choice | procedural sampler | Slot A |
| steering_form | enum | direct_fork/linkage/lean | — | choice | procedural sampler | Slot B |
| drive_form | enum | front_direct_pedals/mid_drive_freewheel/shaft_drive | — | choice+conditional | front_direct 仅 front_count==1，否则降级 mid_drive | Slot C |
| rear_module | enum | cargo_basket/passenger_bench/flat_deck | — | choice | procedural sampler | Slot D |
| seat_count | int | {1,2,3} | 1 | choice(weighted) | 权重 (0.6,0.28,0.12) | Slot E |
| front_count / rear_count | derived | delta=(1,2) / tadpole=(2,1) | (1,2) | equation | `= f(frame_form)` | frame forks |
| front_wheel_radius | float | delta 0.185 / tadpole 0.145 | 0.185 | equation | `= f(layout)`；轮底 z=radius | origin L511 |
| rear_wheel_radius | float | delta 0.145 / tadpole 0.185 | 0.145 | equation | `= f(layout)` | origin L514 |
| wheel_radius_scale | float | [0.90,1.12] | 1.0 | independent | clamp | origin |
| frame_length_scale | float | [0.92,1.10] | 1.0 | independent | clamp（缩放 x 锚点） | origin |
| steer_range | float | [0.42,0.60] rad | 0.55 | independent | clamp；转向上下限 | origin L606 |
| rear_half_track | float | [0.20,0.28] | 0.2475 | independent | clamp | origin L622 |
| (—) | constraint | — | — | inequality | dual-track ≥ tire_half+gap；轮底恒 z=radius（触地）；pedal 半径 < 曲柄轴高（不触地） | clearance |

## 7.5 编译预算 / compile budget
每-seed 目标 ≤ 18s（依据：库内 tube-sweep + 少量布尔的车辆类 ~10-18s，参照 Sports_Baby_cycle /
tractor）。tessellation 分档：tube `_tube_visual` radial_segments=18 / samples_per_segment=12；
挡泥板弧 segments≤28；torus radial≤20 tubular≤56；N 个相同轮/踏板/座复用同一 helper 生成的 mesh。
超预算先降段数再迭代。sweep `--compile-timeout 120`（3× watchdog）。

## Multiplicity / Copy Logic

- `count_param`：`seat_count`（1 根 multiplicity 轴）
- `N_range`：产品域 {1,2,3}；sampling domain 权重 (0.6, 0.28, 0.12)（单座最常见、双座次之、三座尾部）。
- copied object：一个 `{seat_post(chassis 视觉) + saddle base+cushion+backrest(saddle part 视觉)}`
  单元；naming `saddle_base_{i}` / `seat_post_{i}`；placement 沿 x 在座区规则排布；joint policy：
  saddle 单一 part FIXED 于 chassis（N 组视觉共享），座管为 chassis 视觉。
- source/gating：origin (N=1) + seat_count_2_seats + seat_count_3_tandem_seats。N 编入 `slot_choices`
  为 `("seat_count", f"seats_{N}")`，各自 clamp，sweep 上限 3。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | frame_form 改 chassis tube 拓扑 + 轮布局（delta 单前双后 ↔ tadpole 双前单后，改前/后 part 数）；rear_module 改后层 part。均 forked_anchor/origin_anchor |
| └ multiplicity | 同构件 ×N | 有 | seat_count N∈{1,2,3}，权重 (0.6,0.28,0.12)，见 §8 |
| ② 关节类型 | 图不变，换 type/轴 | 有 | steering_form 改转向关节轴（direct/linkage 竖直 (0,0,1) ↔ lean 后倾轴）；drive_form 改曲柄 parent/机构。REVOLUTE/CONTINUOUS/FIXED 均在 sweep 出现。forked_anchor |
| ③ 主体形态家族 | 换核心 part 几何形态原型 | 有 | frame_form 5 个 form_subtype（Volumetric Envelope×2 / Planar Boundary×2 / Macro Surface×1，登记进 slot_choices）；rear_module 3 个（bin / bench / flat_deck=Macro Surface，flat_deck 标 world_knowledge_extrapolation） |
| ④ 表面装饰 | 叠加表面细节 | 有 | grip ribs（origin L479-L488）、frame_badge、chainring 齿、bevel 壳、fender 弧 —— 均 host part visual、由宿主面派生（record_only）。装饰数随 form 变 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | wheel_radius_scale[0.90,1.12]、frame_length_scale[0.92,1.10]、rear_half_track[0.20,0.28]；关节行程：steering REVOLUTE 轴 x 平面 `[-steer_range,+steer_range]`（steer_range∈[0.42,0.60]）、crank REVOLUTE y `[-π,π]`、wheel/pedal CONTINUOUS 整圈。motion_test_plan：跑 `fail_if_parts_overlap_in_sampled_poses(ignore_fixed=True)` + targeted `ctx.pose`（转向侧移前轮、曲柄抬踏板、轮滚 marker 位移）。全程不穿模，captured pin/hub 对用 element-scoped `allow_overlap` |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 painted(frame/accent) + metal(hardware/hub) + rubber(tire)；配色 6：strawberry_pink / classic_red / sky_blue / mint_cream / sunny_yellow / charcoal_sport。金属大类覆盖 ≥ ceil(0.5×6)=3（全部含 metal 硬件） |

## 采样与覆盖审计

总组合数（离散）：A(5) × B(3) × C(3) × D(3) × E(3) = 405；再乘 tadpole 门控与连续 scale，实际
slot-tuple 组合空间 >300。

理由：frame_form × rear_module × seat_count 提供主体 ①/③ 多样性；steering_form × drive_form
提供 ② 多样性；连续 scale 只做尺度扰动。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次采
frame_form（uniform）、steering_form、drive_form、rear_module、palette（uniform），seat_count
（weighted），及连续 scale（uniform 后 clamp）。`resolve_config` 内解门控（tadpole→mid_drive）、
派生 front/rear count 与轮半径、投影 dual-track 不等式。无 curated/modulo 主表；seed=0 不特殊。
Topology target：1000-seed slot tuple 覆盖 report-only，预期 >300 distinct tuple。
regression overrides：none。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 A→B→C→D→E，uniform/weighted，门控在 resolve | slot_choices_for_seed == build choices |
| compatibility matrix | front_direct 仅 front_count==1，否则降级 mid_drive；dual-track 不等式 | 无 floating / collision / axis / max-N / bulky 失败 |
| controlled local variation | wheel_radius_scale / frame_length_scale / steer_range / rear_half_track，全 clamp | 比例变化不破接口/触地/关节原点/身份 |
| regression overrides | none | — |
| random sweep | seeds 0-35 initial，0-999 maturity | contract failures; axis_realization; viewer |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A frame_form | 5 | yes | yes | |
| B steering_form | 3 | yes | yes | |
| C drive_form | 3 | yes | yes | front_direct 门控 |
| D rear_module | 3 | yes | yes | flat_deck=③ world_knowledge |
| E seat_count | 3 | yes | yes | multiplicity |

## Validator

- slot_choices_for_seed 返回已实现 module 名（含 `seat_count` N 编码）
- config_from_seed 对所有普通 seed（含 0）用 deterministic procedural sampling
- 门控：front_direct 仅单前轮，否则降级 mid_drive；dual-track 不等式在 resolve 求解
- 无 regression overrides；不轮换小型 curated 表
- 连续 scale 全在 resolve_config clamp/派生，不留到 builder 失败
- 关键 captured pin/hub 关节存在且 axis/range 正确（steering REVOLUTE、wheel/pedal CONTINUOUS、crank REVOLUTE）
- 复制座椅遵循 naming/placement policy
- 每个非-FIXED 关节均为 captured pin/hub 类型 → 免 MatingContract（grandfathered），用 element-scoped allow_overlap

## Reject cases

- 前轮/后轮不触地（轮底 z≠radius）
- 转向或曲柄行程内穿模（未声明 captured allow_overlap）
- front_direct 用于 tadpole（双前轮）却未降级 → 曲柄横轴无法穿双前轮
- saddle / rear_module 与 chassis 无物理接触 → isolated part
- 把不动的 chainring/shaft/badge 做成独立 FIXED part（应为 chassis visual）
- 只靠涂装/尺寸撑多样性，frame_form / rear_module 形态未拉开
- pedal 半径过大触地；dual-track 过窄轮互穿

## 与相邻类别的边界

- 不该混入：bicycle（两轮，无第三着地轮、无货/座承载层）
- 不该混入：four-wheel pedal cart（四轮，超出 tricycle 身份）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 自写自审：5 slot（4 discrete + 1 multiplicity），均 ≥3 candidate；③ frame_form/rear_module 形态家族登记入 slot_choices；全部非 FIXED 关节为 captured pin/hub 免 MatingContract。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D/E | low_step_child/direct_fork/front_direct/cargo_basket/seats_1 | rec_picturex_0611__tricycle__001 | L175-L661 | 主 part tree + helpers + 关节拓扑 |
| S2 | A | delta_adult | rec_0611_tricycle_var_frame_topology_delta_adult_frame | L193-L324 | 直立三角车架 tube |
| S3 | A | cargo_trike | rec_0611_tricycle_var_frame_topology_front_cargo_box_frame | L193-L340 | 长平台车架 |
| S4 | A | drift_trike | rec_0611_tricycle_var_frame_topology_drift_trike_frame | L193-L300 | 低矮车架 |
| S5 | A | tadpole_twin_front | rec_0611_tricycle_var_frame_topology_tadpole_two_front_frame | L193-L360 | 双前 rail + crossmember |
| S6 | B | linkage | rec_0611_tricycle_var_steering_linkage_steering | L381-L470 | steering links + bosses |
| S7 | B | lean | rec_0611_tricycle_var_steering_lean_steering | L381-L470 | 后倾轴 |
| S8 | C | mid_drive_freewheel | rec_0611_tricycle_var_drive_mid_drive_freewheel | L23-L260 | chainring + 车架曲柄 |
| S9 | C | shaft_drive | rec_0611_tricycle_var_drive_shaft_drive | L23-L260 | driveshaft + bevel |
| S10 | D | passenger_bench | rec_0611_tricycle_var_rear_module_passenger_bench | L200-L340 | 座凳 slab |
| S11 | E | seats_2/seats_3 | rec_0611_tricycle_var_seat_count_2/3 | L23-L420 | 多座复制 |
