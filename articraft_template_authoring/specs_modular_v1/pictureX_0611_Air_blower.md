# Modular Spec — pictureX_0611_Air_blower

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_Air_blower` |
| template path | `agent/templates/pictureX_0611_Air_blower.py` |
| test path (optional) | `tests/agent/test_pictureX_0611_Air_blower_template.py` (skipped — sweep is authority) |
| stage | `IMPLEMENTED` |
| status | `complete_visual_confirmed_2026-07-13` |
| variant_gate | `confirmed_by_user_2026-07-12` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children drivetrain / hinged-boards + multiplicity accordion·squirrel-cage; family-gated) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 15 (2 origins + 13 forked variants) |
| read_count | 15 |
| read_scope | all 5-star samples in this category (both origins fully read; 13 variants read for distinguishing geometry) |
| source_index_policy | only adopted module sources indexed in §14 |

两个 origin 是**结构上不同**的两大空气驱动形态家族：

- **BELLOWS 家族** (P1 = `rec_...__air_blower__001`, 手动壁炉风箱): 两块铰接梨形木板 (`lower_board`/`upper_board`) + 4 折皮革手风琴 (`bellows_fold_i`, mimic) + 黄铜锥形喷嘴 + 单向皮革进气瓣 (`intake_flap`) + 腕带手柄。运动 = **板挤压** `board_pivot` REVOLUTE(轴+Y, 0→5°) 驱动折叠 mimic。挤压容积→喷嘴出气。
- **BLOWER 家族** (P2 = `rec_...__air_blower__002`, 手摇离心风机): 蜗壳鼓形外壳 `housing` + 曲柄 `crank` CONTINUOUS → 同轴 `drive_shaft`(mimic) → 18 叶松鼠笼叶轮 `fan_rotor`(`BlowerWheelGeometry`, mimic) + 可调铝出气管(REVOLUTE 扭转) + 后栅格进气 + 顶部提手 + 触发拨杆。连续叶轮驱动气流。

一个 bellows body **不能**装轴向叶轮 (无鼓腔/无轴)，一个 blower drum **不能**做手风琴挤压 (无铰接板)——§10 Compatibility Matrix 把 body×motion 在 resolve 时 gate 死。

## 核心身份

一台通过**受驱叶轮**(离心松鼠笼 / 轴向螺旋桨) 或**受挤压气室**(风箱手风琴 / 橡胶球) 移动空气、从**喷嘴/出气口**吐出定向气流的手持或台式设备。每个 seed 至少有 1 个真实非-FIXED 关节驱动送风元件 (叶轮 CONTINUOUS 或 风箱/球 PRISMATIC/REVOLUTE)，配一个出气口与一个进气口。

身份边界 (keep neighbors OUT):
- 不混入 HVAC/暖通风机机组 (固定安装、无手持 archetype)。
- 不混入吹风机 (hair dryer — 单独 `Bathroom_Hair_dryer` 类；保留 blower archetype 而非发型工具)。
- 不混入发动机/汽油吹叶机 (背负发动机单元 = 不同 mechanism + harness)。

## 槽位 + 候选模块表

### Slot A：body_form（③ 主体形态家族 / Primary Form Family — 承载主多样性，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `bellows_boards` (family=bellows) | origin_anchor | S1 `rec_...__001` | L217-L360 (boards), L40-L152 (loft helpers) | eligible if compatible | Planar Boundary Form — 两块放样梨形木板 + mimic 手风琴腔；root=lower_board |
| `rubber_bulb` (family=bellows) | forked_anchor | S7 `rec_...var_rubber_bulb` | L84-L188 helpers, L211-L300 build | eligible if compatible | Volumetric Envelope Form — 单个中空椭球橡胶球体 + prismatic 挤压壁；root=bulb_body |
| `volute_drum` (family=blower) | origin_anchor | S2 `rec_...__002` | L145-L215 (drum housing) | eligible if compatible | Volumetric Envelope Form — 蜗壳圆鼓 (`_cylinder_y` 鼓 + 切向出口切割)；root=housing |
| `axial_barrel` (family=blower) | forked_anchor | S4 `rec_...var_axial_inline_barrel` | L149-L215 | eligible if compatible | Volumetric Envelope Form — 拉长在线轴向筒身 |
| `canister_tank` (family=blower) | forked_anchor | S5 `rec_...var_canister_tank` | L52-L62 (`_capsule_y`), L164-L215 | eligible if compatible | Volumetric Envelope Form — 水平胶囊罐 (圆柱+半球端盖) |
| `spherical_pod` (family=blower) | forked_anchor | S6 `rec_...var_spherical_turbine_pod` | L84-L101 (`_ovoid_pod_y`), L164-L215 | eligible if compatible | Macro Surface Construction — 旋转椭球涡轮舱 |

form_subtype 已逐候选标注；≥3 可识别原型 (远超 ≥2 底线)，跨两大家族。

### Slot B：motion_mechanism（② 关节类型 — family-gated）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `centrifugal_wheel` (blower) | origin_anchor | S2 | L425-L459 (`BlowerWheelGeometry` 18 叶 + `housing_to_rotor` CONTINUOUS mimic) | eligible if body∈blower | 松鼠笼叶轮，crank CONTINUOUS 驱动，shaft/rotor mimic |
| `axial_impeller` (blower) | forked_anchor | S3 `rec_...var_axial_impeller` | L429-L470 (`FanRotorGeometry` 螺旋桨) | eligible if body∈blower | 轴向螺旋桨叶轮 (不同 mesh geometry class，同 CONTINUOUS mimic 拓扑) |
| `board_squeeze` (bellows) | origin_anchor | S1 | L407-L444 (`board_pivot` REVOLUTE +Y + fold mimic) | eligible if body==bellows_boards | 铰接板 REVOLUTE 挤压，折叠 REVOLUTE mimic |
| `foot_pump` (bellows) | forked_anchor | S8 `rec_...var_foot_pump_prismatic` | L439-L478 (`board_pivot` PRISMATIC -Z + fold PRISMATIC mimic) | eligible if body==bellows_boards | 垂直行程 PRISMATIC 挤压，折叠 PRISMATIC mimic |
| `bulb_squeeze` (bellows) | forked_anchor | S7 | L262-L300 (squeeze_wall) + `bulb_squeeze` PRISMATIC 轴-Z | eligible if body==rubber_bulb | 单挤压壁 PRISMATIC (轴-Z, 0→8-15mm)；橡胶球唯一运动 |

每类 ② 都会在 sweep 中出现 (blower 抽 centrifugal/axial；bellows_boards 抽 board_squeeze/foot_pump；rubber_bulb 恒 bulb_squeeze)。

### Slot C：outlet（③ 子形态 — family-gated；每 seed 恒有出气口）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `brass_nozzle` (bellows) | origin_anchor | S1 | L155-L176, L244-L255 (`_nozzle_shell`/`_nozzle_rim`, fused on body) | eligible if family==bellows | 锥形黄铜喷嘴，FIXED 融进 body visual (不动→非独立 part) |
| `adjustable_tube` (blower) | origin_anchor | S2 | L272-L330 (`_tapered_tube_x` + collars, REVOLUTE 扭转) | eligible if family==blower | 可调铝管，独立 `nozzle` part，REVOLUTE ±0.35 rad |
| `flex_duct` (blower) | forked_anchor | S9 `rec_...var_flex_duct_outlet` | L84-L122 (`_corrugated_duct_x`), L313-L330 | eligible if family==blower | 波纹柔性软管，独立 `nozzle` part，REVOLUTE 扭转 |

### Slot D：intake（③ 子形态 — family-gated）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `flap_valve` (bellows) | origin_anchor | S1 | L362-L380, L445-L459 (`intake_flap` + `intake_hinge` REVOLUTE) | eligible if family==bellows | 单向皮革/橡胶瓣，REVOLUTE 单独 part |
| `spoked_grille` (blower) | origin_anchor | S2 | L84-L100, L226-L230 (`_rear_grille`, fused body visual) | eligible if family==blower | 辐条后栅格，FIXED 融进 housing visual |
| `filter_cap` (blower) | forked_anchor | S10 `rec_...var_filter_intake` | L84-L149 (`_filter_cap_outer_sleeve`), L152-L161 (foam core) | eligible if family==blower | 穿孔泡棉/网滤筒帽，FIXED 融进 housing visual |

### Slot E：grip（③ 子形态 — family-gated）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `board_handle` (bellows) | origin_anchor | S1 | L179-L194, L310-L321 (`_wrist_loop` 腕带 + 板尾手柄) | eligible if body==bellows_boards | 木板尾端 + 腕带，融进 board visual |
| `bulb_grip` (bellows) | forked_anchor | S7 | L177-L188 (squeeze ribs = 抓握面) | eligible if body==rubber_bulb | 球体本身即握持面 (grip ribs 融进 squeeze/bulb visual) |
| `top_grip` (blower) | origin_anchor | S2 | L154-L178 (`handle`/`top_rib` extrude 融进 main_body) | eligible if family==blower | 模制水平顶提手，融进 housing |
| `pistol_grip` (blower) | forked_anchor | S11 `rec_...var_pistol_grip` | L158-L230 (垂直手枪握把 extrude + finger ridges) | eligible if family==blower | 垂直下垂手枪握把，融进 housing |

## 槽位图（slot graph）

pattern: mixed（family-gated；blower=parallel_children drivetrain，bellows=hinged-boards + multiplicity）

```
resolve: body_form → family ∈ {bellows, blower}  (COMPATIBILITY GATE, §10)

BLOWER  housing[root]
        ├─[REVOLUTE +X, socket@(0.079,0,0.045)]→ nozzle (adjustable_tube|flex_duct)   Slot C
        ├─[CONTINUOUS +Y, origin(0,-0.057,0)]→ crank ─(grip fused)                    Slot B
        ├─[CONTINUOUS +Y mimic crank]→ drive_shaft                                    Slot B
        ├─[CONTINUOUS +Y mimic crank]→ fan_rotor (centrifugal_wheel|axial_impeller)   Slot B (multiplicity: fan_blade_count)
        └─(fused visuals) grille|filter_cap  Slot D · top_grip|pistol_grip  Slot E · brass? no

BELLOWS_BOARDS  lower_board[root] (nozzle+board_handle fused)                          Slot C/E
        ├─[REVOLUTE +Y | PRISMATIC -Z]→ upper_board                                    Slot B
        ├─[× N mimic board_pivot]→ bellows_fold_i (multiplicity: bellows_fold_count)   Slot B
        └─[REVOLUTE +X]→ intake_flap                                                   Slot D

RUBBER_BULB  bulb_body[root] (nozzle+grip ribs fused)                                  Slot C/E
        ├─[PRISMATIC -Z]→ squeeze_wall                                                 Slot B
        └─[REVOLUTE +X]→ intake_flap                                                   Slot D
```

接口点位: blower nozzle mates 切向 outlet_socket (X-normal, REVOLUTE 扭转轴+X); crank/shaft/rotor 共轴 +Y 挂 housing (captured-pin/journal, element-scoped allow_overlap); bellows upper_board 挂 lower_board pivot@(PIVOT_X,0,UPPER_Z); folds 挂 lower_board (mimic); flap 挂 body @intake hole。

## 每槽位 Module Emits / Interfaces

### Slot A / module bellows_boards
| emits | 描述 | 来源 |
|---|---|---|
| parts | lower_board(root, +nozzle+handle+hinge支承), upper_board | S1 L217-L360 |
| internal joints | (由 Slot B/D 提供) | — |
| upstream interface | root (无) | — |
| downstream interface | pivot @(PIVOT_X,0,UPPER_Z) 给 upper_board；intake hole 给 flap | S1 L407-L459 |

### Slot A / module volute_drum (代表 blower body)
| emits | 描述 | 来源 |
|---|---|---|
| parts | housing(root): main_body 鼓 + outlet_socket + fused grille/filter + fused grip + screws + feet + front_seam | S2 L145-L268 |
| internal joints | 无 (子件由 Slot B/C 挂载) | — |
| upstream interface | root (无) | — |
| downstream interface | 切向 outlet_socket 面@x≈0.105 给 nozzle(REVOLUTE+X)；+Y 轴腔给 crank/shaft/rotor | S2 L217-L330,L373-L459 |

### Slot B / module centrifugal_wheel
| emits | 描述 | 来源 |
|---|---|---|
| parts | crank(+grip fused), drive_shaft, fan_rotor(`BlowerWheelGeometry` N 叶 + fan_hub) | S2 L334-L459 |
| internal joints | housing_to_crank CONTINUOUS +Y; housing_to_shaft/housing_to_rotor CONTINUOUS mimic(crank) | S2 L373-L459 |
| upstream interface | 共轴 +Y 挂 housing | S2 |
| downstream interface | 无 (叶轮为终端) | — |

### Slot B / module board_squeeze
| emits | 描述 | 来源 |
|---|---|---|
| parts | upper_board, bellows_fold_i × N | S1 L323-L405 |
| internal joints | board_pivot REVOLUTE +Y [0, 5°]; fold_i_compression REVOLUTE mimic(board_pivot, ratio (i+1)/N) | S1 L407-L444 |
| upstream interface | 挂 lower_board pivot | S1 |
| downstream interface | 无 | — |

（其余 module emits 对称，见 §14 source index；活动件均有 articulation 语义，不动细节 (screws/tacks/grain/seam/rim/ribs/handle/nozzle/grille) 一律写宿主 part visual，符合 Rule 1。）

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | bellows_boards / rubber_bulb / volute_drum / axial_barrel / canister_tank / spherical_pod | volute_drum | choice | procedural sampler | Slot A |
| motion_mechanism | enum | centrifugal_wheel / axial_impeller / board_squeeze / foot_pump / bulb_squeeze | — | conditional | 由 family gate 解析 (§10) | Slot B |
| outlet | enum | brass_nozzle / adjustable_tube / flex_duct | — | conditional | family gate | Slot C |
| intake | enum | flap_valve / spoked_grille / filter_cap | — | conditional | family gate | Slot D |
| grip | enum | board_handle / bulb_grip / top_grip / pistol_grip | — | conditional | body gate | Slot E |
| palette_style | enum | walnut_brass / painted_steel / matte_black / safety_orange / patina_copper | walnut_brass | choice | rng.choice per seed，独立于 family | §8.5 ⑥ |
| fan_blade_count | int | {8, 18, 32} | 18 | conditional | 仅 blower；`BlowerWheelGeometry`/`FanRotorGeometry` blade_count | S2/S12/S13/S3 |
| bellows_fold_count | int | {2, 4, 6} | 4 | conditional | 仅 bellows_boards；循环生成 N 折 + N mimic joint | S1/S14/S15 |
| body_scale | float | [0.92, 1.10] | 1.0 | independent | 主体尺度，clamp | S1/S2 |
| outlet_len_scale | float | [0.85, 1.15] | 1.0 | independent | 出气管/喷嘴长度 | S2 L276 |
| crank_radius_scale | float | [0.90, 1.12] | 1.0 | independent | blower 曲柄半径 | S2 L341 |
| squeeze_travel_scale | float | [0.85, 1.15] | 1.0 | independent | bellows 行程 | S1/S7/S8 |
| (—) | constraint | — | — | inequality | blower: fan outer_radius ≤ drum inner_radius − 0.006 (叶轮入壳)；违反按比例回缩 | S2 L426 |
| (—) | constraint | — | — | inequality | bellows: fold_i rest_z 单调升 & compressed travel_i < travel_{i+1} (telescoping)；由生成器保证 | S1 L423-L444 |

## 参数范围汇总 / compile budget（§7.5）

编译预算: **≤18 s/seed** (sweep watchdog `--compile-timeout 120` = ~6×，仅防挂)。依据: P2 松鼠笼 32 叶 (`fan_blades_32` 变体) + 主体 boolean 雕刻是本类最重几何，库内实测 blower ≈10-16s、bellows loft ≈6-10s、rubber_bulb ≈5s。分档 tessellation: `BlowerWheelGeometry` 默认段数即可 (叶片是主英雄面)；小半径特征 (screws/ribs/collars) 用 primitive `Cylinder`/`Box` 不 mesh；N 折/N 叶复用同一 helper/geometry class (叶片在 geometry class 内循环，单 Mesh)。fan_blade_count=32 是最重档 → 早探。

## Multiplicity / Copy Logic

**两根独立 multiplicity 轴 (family-gated，各自加权采样、各自编进 slot_choices、各自 clamp)：**

- **fan_blade_count (blower family)**
  - count_param: `BlowerWheelGeometry`/`FanRotorGeometry` blade_count (4th 位参，origin=18)
  - N_range: {8, 18, 32}；sampling domain 权重 (0.34, 0.40, 0.26) — 中档高频、密叶稀有
  - copied object: 单个扫掠叶片 (geometry class 内部径向均布 `i*2π/n`)；naming: 类内 mesh；placement: 绕 rotor 轴均布；joint policy: 单 `housing_to_rotor` CONTINUOUS mimic (叶片刚性锁在 fan_rotor)
  - source/gating: S2(18)/S12(8)/S13(32)；仅 blower，bellows 时不暴露

- **bellows_fold_count (bellows_boards)**
  - count_param: 生成的 `BELLOWS_FOLDS` 条目数 (origin=4)
  - N_range: {2, 4, 6}；权重 (0.30, 0.44, 0.26)
  - copied object: `bellows_fold_i` part (由 `_bellows_fold` 放样)；naming: `bellows_fold_{i}`；placement: 沿 +Z 在两板间叠放/望远，rest_z 单调升；joint policy: 每折自己的 `bellows_fold_{i}_compression` REVOLUTE(或 foot_pump 时 PRISMATIC) mimic(board_pivot)，angle/stroke ratio=(i+1)/N 单调升
  - source/gating: S1(4)/S14(2)/S15(6)；仅 bellows_boards，rubber_bulb 无折 (单挤压壁)

- rubber_bulb: 无 multiplicity 轴 (单挤压壁 + 单进气瓣)。
- 其他同构件 (screws×4, grille spokes×6, tacks×12, grip ribs) = 装饰复制，写宿主 visual 循环，非 candidate anchor。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part/边 | 有 | 3 类运动学骨架: (a) blower 单-root drivetrain 并联子件 (housing→crank/shaft/rotor/nozzle) [S2]; (b) bellows 铰接双板 + mimic 手风琴链 [S1]; (c) rubber_bulb 单-root + 挤压壁 + 瓣 [S7]。均 origin/forked_anchor source-backed |
| └ multiplicity | 同构件 ×N | 有 | 见 §8: fan_blade_count {8,18,32}; bellows_fold_count {2,4,6}，两轴 loop/param-emitted |
| ② 关节类型 | 换 type/轴 | 有 | CONTINUOUS 离心/轴向叶轮 [S2/S3]; REVOLUTE 板挤压 [S1]; PRISMATIC 脚泵/球挤压 [S8/S7]; REVOLUTE 出气扭转/进气瓣。每种都在 sweep 出现 |
| ③ 主体形态家族 | 换核心 part 可识别形态原型 | 有 | body_form slot 6 候选 (bellows_boards=Planar Boundary / rubber_bulb·volute_drum·axial_barrel·canister=Volumetric Envelope / spherical_pod=Macro Surface) + outlet(nozzle/tube/duct) + intake(flap/grille/filter) + grip(board/bulb/top/pistol)。登记进 slot_choices。source-backed anchors，跨两大家族 |
| ④ 表面装饰 | 叠表面细节 | 有 (record_only + world_knowledge) | brass tacks×12 + 油木纹 (bellows) [S1]; 模制肋/front_seam/cover_screws×4/foot pads (blower) [S2]; 手枪握把 finger ridges (host-conformal) [S11]; filter 穿孔环 [S10]。均写宿主 visual，随 ③/⑤ 共形，无独立 part/joint |
| ⑤ 尺寸/行程 | 连续改尺寸/行程 | 有 | body_scale [0.92,1.10], outlet_len_scale [0.85,1.15], crank_radius_scale [0.90,1.12], squeeze_travel_scale [0.85,1.15]（见 §7）。运动包络: board_pivot REVOLUTE +Y [0, 5°] 闭合方向-Z / foot_pump PRISMATIC -Z [−STROKE,0] / bulb_squeeze PRISMATIC -Z [0, 8-15mm] / nozzle REVOLUTE +X [−0.35,0.35] / intake_hinge REVOLUTE +X [−0.24,0.55] / crank·rotor CONTINUOUS 整圈。motion_test_plan: 跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64, ignore_fixed=True)` (每 family ≤2 独立活动关节 + mimic)，每机构 1 条 targeted `ctx.pose` (叶轮转 90° reorient / 板下压 / 球壁内移 / 瓣外开 / 喷嘴扭转)；captured-pin/telescoping/journal 处 element-scoped `allow_overlap` |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类: metal (brass/aluminum/gunmetal/copper) + plastic + painted-steel + wood + leather/rubber。5 配色 walnut_brass / painted_steel / matte_black / safety_orange / patina_copper (≥3-6)；材质大类覆盖 ≥ ceil(0.5×5)=3。palette_style rng.choice per seed，独立于 family，驱动每个 .visual |

**收尾自检**: `template batch` 0-9 seed 需肉眼看到 bellows 与 blower 两大家族拉开、5 配色出现、装饰贴合、关节全程不穿模。

## 采样与覆盖审计

总组合数 (family-gated 合法组合):
- BLOWER: body{volute,axial_barrel,canister,spherical}=4 × motion{centrifugal,axial}=2 × outlet{tube,duct}=2 × intake{grille,filter}=2 × grip{top,pistol}=2 × fan_blade{8,18,32}=3 = **192**
- BELLOWS_BOARDS: motion{board_squeeze,foot_pump}=2 × fold{2,4,6}=3 = **6** (outlet=nozzle, intake=flap, grip=board 恒定)
- RUBBER_BULB: **1** (motion=bulb_squeeze, outlet=nozzle, intake=flap, grip=bulb 恒定)
- × palette 5 = (192+6+1)×5 = **995** slot_choice tuples

理由: blower 家族富组合 (192)，bellows 较窄但结构独立必须保留 (风箱是 origin，不可丢)。总 tuple 空间 ~995 满足富类别 ≥300 观察目标。

seed_domain_policy: procedural_first。**config_from_seed(seed)**: rng=Random(seed) → 采 body_form (加权) → family = FAMILY_OF[body_form] → 从 family 合法集采 motion/outlet/intake/grip → 采 multiplicity (仅对应 family 轴) → 采 palette + 连续 scale。seed=0 不特殊。无 curated/modulo 主表。

**compatibility matrix / gating (§10)**: body_form 决定 family；resolve_config 把任何 body×motion / family×outlet / family×intake / body×grip 非法组合**回落到 family 默认** (downgrade，永不 build+fail)。fan_blade_count 仅在 blower 暴露，bellows_fold_count 仅在 bellows_boards 暴露。

Topology target: ~995 tuple > 300，report-only。

Controlled local parameterization: body_scale / outlet_len_scale / crank_radius_scale / squeeze_travel_scale (§7)；全部 resolve_config 内 clamp/派生；受 fan-in-drum 不等式、fold telescoping、joint range、identity 约束，不破坏 captured-pin/journal 接口。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body→family→gated 子槽→multiplicity→palette→scale，加权 | slot_choices_for_seed == build choices |
| compatibility matrix | family gate: bellows↔{squeeze/foot_pump/bulb_squeeze, nozzle, flap, board/bulb}; blower↔{centrifugal/axial, tube/duct, grille/filter, top/pistol}；非法→family 默认 | 无 floating/collision/axis/穿模/bulky 失败 |
| controlled local variation | 4 连续 scale + clamp | 比例变化不破接口/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | 0-35 初过，0-999 成熟观察 | contract failures; axis_realization; viewer |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| A body_form | 6 | yes | yes | 跨两 family |
| B motion | 5 (blower 2 / bellows 3) | yes | yes | family-gated |
| C outlet | 3 | yes | yes | family-gated |
| D intake | 3 | yes | yes | family-gated |
| E grip | 4 | yes | yes | family-gated |

## Validator

- slot_choices_for_seed 返回已实现 module 名 (含 multiplicity 轴档)
- config_from_seed 对所有 seed (含 0) 用 deterministic procedural sampling
- compatibility matrix 在 resolve_config gate 掉非法 body×motion / family×outlet/intake / body×grip (downgrade，不 build 非法体)
- 无 regression overrides
- 连续 scale clamp/派生在 resolve_config；fan-in-drum 不等式、fold telescoping 在此求解
- MatingContract: 每个非-FIXED 子件 (nozzle REVOLUTE, upper_board pivot, squeeze_wall/foot PRISMATIC, intake_flap) 声明 MatingContract 到真实 visual (captured-pin/journal 处用 element-scoped allow_overlap 免 gap-check)
- 关键关节 type/轴/range: crank CONTINUOUS+Y / rotor mimic; board_pivot REVOLUTE+Y[0,5°] 或 PRISMATIC-Z; bulb_squeeze PRISMATIC-Z; nozzle REVOLUTE+X[±0.35]; intake_hinge REVOLUTE+X
- 复制件 naming: `bellows_fold_{i}` / geometry-class 内叶片

## Reject cases

1. bellows body 装 CONTINUOUS 叶轮 (无鼓腔/无轴) → gate 掉，回落 board_squeeze。
2. blower drum 做手风琴挤压 (无铰接板) → gate 掉，回落 centrifugal_wheel。
3. rubber_bulb 出 fold multiplicity (单壁，无折) → 不暴露 bellows_fold_count。
4. fan outer_radius ≥ drum inner_radius (叶轮撑爆壳) → 不等式回缩。
5. fold rest_z 非单调 / travel 非递增 → telescoping 生成器保证单调。
6. 喷嘴/栅格/提手做成独立 FIXED part (悬浮饰件) → 违反 Rule 1，一律融进宿主 visual。
7. crank/shaft/rotor 共轴 captured overlap 未 element-scoped allow_overlap → closed/sampled pose 误报穿模。
8. palette 被 family 特判 (default seed 特殊化) → 违反 rng.choice per seed 独立契约。

## 与相邻类别的边界

- 不该混入: HVAC 暖通风机机组 (固定管道安装、无手持/手摇 archetype)。
- 不该混入: 吹风机 hair dryer (加热造型工具，单独 `Bathroom_Hair_dryer` 类)。
- 不该混入: 发动机/汽油吹叶机 (背负发动机 + harness，不同 mechanism)。
- 不该混入: 真空吸尘器 / 喷漆枪 / 空压罐 / 台扇座扇 / 呼吸器 / 无人机·PC 风扇 (source map must_not_become)。

## 实现降级记录 (spec self-revision, per AUTHORING §C)

编译鲁棒性驱动的两处降级 (保持 same part tree / joint topology / primitive family，符合 Rule 3)：

1. **canister_tank: capsule → prolate ovoid (`_ovoid_pod_y`).** 原设计用 `_capsule_y` (圆柱+两半球端盖, S5)。实测：圆柱-半球结合处在 rear-cavity boolean cut 下会按 body_len_scale 尺度**偶发分裂出 disconnected 后盖 component** (seed 24/26 island)。降级为单一旋转 prolate ovoid (equatorial 0.074 / polar 0.082，明显拉长 → 与 spherical_pod 的 oblate ovoid 0.080/0.056 形态可区分)，是同一 Volumetric Envelope 家族、同一 part tree/interface、只改旋转母线离散形态 — 合法 ③ 变体 (world_knowledge_extrapolation)，且 boolean 全程连通。仍标 `canister_tank` (form_subtype: Volumetric Envelope Form — 拉长旋转体罐)。
2. **blower crank_grip: 独立 free-spin CONTINUOUS part → 融进 crank 的 visual (KnobGeometry 保留).** 原 P2 有独立 `crank_to_grip` CONTINUOUS 自由旋转握把。为减少一个关节的 motion-QC 组合并简化，把 ribbed KnobGeometry 握把 fuse 进 crank part (随曲柄公转，不再自转)。符合 Rule 1 (随父刚性运动的件写成 parent visual)；核心送风机构 (crank CONTINUOUS → mimic rotor) 不变。
3. **blower trigger 拨杆 excluded.** P2 的小型 air-control trigger (REVOLUTE) 未实现 — 非 identity-critical (source map 标 "small molded latch")，其细碎 bore 几何徒增 mating-gap/穿模 失败面。每 blower seed 仍有 crank CONTINUOUS + nozzle REVOLUTE 两个独立活动关节。
4. **blower drivetrain 连通性**: 加了一个 housing 内 central bearing spider (中央轴 spine + 3 根到壳壁的辐条，mirror hair_dryer `_front_mount_hub`)，把在轴的 crank/shaft/fan 连到壳体 (captured/journal element-scoped allow_overlap)。tangential outlet passage 的贯穿切割在 domed 体上会切碎壁，故出气口由 protruding `outlet_socket` boss 表达 (贴外表面，连通)。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | complete; visual confirmed by user 2026-07-13 |
| reviewer notes | family-gated 双家族单 slug 成功共存 (无需拆分)；compatibility matrix 见 §10；2026-07-13 single-worker post-gate rerun passed with final pass_rate=1.0 and corner stage clean (48/48 seeds, no failed seeds). Preview batch records generated for selected coverage seeds; user confirmed visual check on 2026-07-13. |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D/E | bellows_boards + board_squeeze + brass_nozzle + flap_valve + board_handle | rec_...__air_blower__001 | L32-L459 | bellows part tree + REVOLUTE 挤压 + 折叠 mimic + 喷嘴/瓣/手柄 |
| S2 | A/B/C/D/E | volute_drum + centrifugal_wheel + adjustable_tube + spoked_grille + top_grip | rec_...__air_blower__002 | L145-L517 | blower drivetrain + 松鼠笼 + 可调管 + 栅格 + 顶提手 |
| S3 | B | axial_impeller | rec_...var_axial_impeller | L429-L470 | `FanRotorGeometry` 螺旋桨叶轮 |
| S4 | A | axial_barrel | rec_...var_axial_inline_barrel | L149-L215 | 在线轴向筒身 |
| S5 | A | canister_tank | rec_...var_canister_tank | L52-L215 | 胶囊罐身 (`_capsule_y`) |
| S6 | A | spherical_pod | rec_...var_spherical_turbine_pod | L84-L215 | 旋转椭球舱 (`_ovoid_pod_y`) |
| S7 | A/B/C/D/E | rubber_bulb + bulb_squeeze + bulb_grip | rec_...var_rubber_bulb | L84-L300 | 椭球球体 + PRISMATIC 挤压壁 + 握持肋 |
| S8 | B | foot_pump | rec_...var_foot_pump_prismatic | L439-L478 | PRISMATIC 脚泵行程 + 折叠 PRISMATIC mimic |
| S9 | C | flex_duct | rec_...var_flex_duct_outlet | L84-L122 | 波纹柔性软管 (`_corrugated_duct_x`) |
| S10 | D | filter_cap | rec_...var_filter_intake | L84-L161 | 穿孔滤筒帽 + 泡棉芯 |
| S11 | E | pistol_grip | rec_...var_pistol_grip | L158-L230 | 垂直手枪握把 + finger ridges |
| S12 | B | fan_blade_count=8 | rec_...var_fan_blades_8 | L427-L436 | 松鼠笼 8 叶档 |
| S13 | B | fan_blade_count=32 | rec_...var_fan_blades_32 | L429-L436 | 松鼠笼 32 叶档 (最重) |
| S14 | B | bellows_fold_count=2 | rec_...var_bellows_folds_2 | L32-L37 | 手风琴 2 折档 |
| S15 | B | bellows_fold_count=6 | rec_...var_bellows_folds_6 | L32-L37 | 手风琴 6 折档 |

## GATE P3 自检
- [x] spec 完整；每 candidate 有真实 model.py:Lx-Ly
- [x] 无未记录的单-candidate slot (最小 3 candidate；family-gated 内每 family≥2)
- [x] topology audit (§8.5) + compatibility matrix (§9/§10) 齐备，family gating 是核心
- [x] §7.5 compile budget ≤18s/seed，松鼠笼 32 叶预算在内
- [x] palette_style ≥3 (5 配色)，rng.choice per seed
→ 进入模板实现，不停。
```
