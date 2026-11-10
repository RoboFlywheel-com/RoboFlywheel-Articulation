# Modular Spec — miter_saw_arm_assembly

## 元信息
| 项 | 值 |
|---|---|
| slug | `miter_saw_arm_assembly` |
| template path | `agent/templates/miter_saw_arm_assembly.py` |
| test path (optional) | `tests/agent/test_miter_saw_arm_assembly_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`（核心是 parallel_children）：固定 `base` 是公共根，挂两条**平行分支** —— (1) `base --REVOLUTE Z--> turntable`（miter 转台调角），(2) `base --[arm linkage]--> saw_head --[blade/guard]`（锯臂下压切割链）。全部 5 个 5 星样本一致地把锯臂分支与转台分支并列挂在 base 上（锯刃前后向固定平面，靠转台带工件回转设 miter 角）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 5 |
| read_count | 5 |
| read_scope | all 5-star samples in this category（5 个全部精读 `model.py` + `prompt.txt`，未抽样） |
| source_index_policy | only adopted module sources are indexed below |

逐样本结构：

| 样本 | 锯臂联动 | 关节链 | blade/guard | 主 primitive |
|---|---|---|---|---|
| 0001 | direct 直接铰臂 | base→turntable(REVOLUTE Z,±0.82) ‖ base→saw_arm(REVOLUTE X,-0.07..0.95) | blade 为 saw_arm visual（无独立旋转）+ guard visual | ExtrudeWithHoles + tube |
| 0002 | rear yoke 后铰叉 | base→turntable(REVOLUTE Z,±50°) ‖ base→yoke(FIXED)→swing_arm(REVOLUTE Y,0..55°)→guard(FIXED) | blade_guard_housing FIXED（静态罩） | section_loft(arm) + tube + ExtrudeWithHoles |
| 0003 | slide 滑轨 | base→turntable(REVOLUTE Z,±45°) ‖ base→carriage(PRISMATIC Y,0..0.20)→saw_head(REVOLUTE X,-0.87..0) | blade/guard_shell 为 saw_head visual（静态） | mesh(carriage/guard/handle) + tube |
| b12308 | slide 滑轨 + 旋刃 | base→turntable(REVOLUTE Z,±0.87) ‖ base→carriage(PRISMATIC -Y,0..0.18)→saw_head(REVOLUTE X,0..0.55)→blade(CONTINUOUS X) | blade CONTINUOUS + 上罩 visual | ExtrudeWithHoles + mesh + tube |
| 8288 | direct 铰臂 + 旋刃 + 收罩 | base→table(REVOLUTE Z,±50°) ‖ base→arm(REVOLUTE X,-0.50..0.08)→blade(CONTINUOUS X)，arm→lower_guard(REVOLUTE X,0..1.25) | blade CONTINUOUS + lower_guard REVOLUTE 收缩 | ExtrudeWithHoles + 4×tube + mesh |

结构族分布：
- **arm linkage 轴**：direct 直接铰臂(0001,8288) / rear-yoke 后铰叉(0002) / slide 滑轨小车(0003,b12308) —— 这是最强拓扑差异轴（base→head 之间关节数/类型不同）。
- **blade/guard 轴**：静态刃+静态罩(0001,0002,0003) / CONTINUOUS 旋刃(b12308) / CONTINUOUS 旋刃+REVOLUTE 收缩下罩(8288)。

## 核心身份

`miter_saw_arm_assembly` 的不变身份：**一个台式斜切锯 —— 固定 base（带 fence 围栏 + miter 刻度 + 转台座）支撑两条平行运动：一个绕竖直 Z 轴回转设 miter 角的 turntable（带 kerf insert），以及一条从 base 出发、经直接铰臂 / 后铰叉 / 滑轨小车联动、向下俯仰下压做切割的 saw arm/head；head 端带圆锯片（静态或绕 arbor CONTINUOUS 旋转）与 blade guard（静态罩或 REVOLUTE 收缩下罩）。** 最小合法体 = base + turntable(REVOLUTE Z) + arm linkage(至少一个 REVOLUTE 俯仰把 head 压向 table) + 可见圆锯片 + guard。miter 回转 + 锯臂俯仰两个核心运动缺一不可。

默认成熟域：台式/复合/滑动复合斜切锯（chop saw / compound / sliding compound miter saw），含 fence、kerf 板、miter 刻度、motor housing、handle、blade guard。

不该混入：见“与相邻类别的边界”。

## 槽位 + 候选模块表

### Slot A：base_table（固定根 base + fence + miter 转台，REVOLUTE-Z 回转）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| bench_slab_base | rec_miter_saw_arm_assembly_0001 | base L173-L220 + turntable L221-L252 | eligible if compatible | 平板 slab base + turntable seat + fence + 转台(kerf insert)，简洁台式 |
| cast_wing_base | rec_miter_saw_arm_assembly_0003 | base L89-L162 + turntable L163-L187 | eligible if compatible | plinth + rear_deck + 左右 support wing + 双 fence + rear_column + rail_bridge（含滑轨柱）+ 转台(miter lock + kerf) |
| heavy_rib_base | rec_miter_saw_arm_assembly_8288f5516faf4febbaccc03d9944b0d1 | base L196-L250 + miter_table L251-L275 | eligible if compatible | 铸重 base + fence + tube 加强肋(4×tube_from_spline) + miter_table |

### Slot B：arm_linkage（base→saw head 的下压切割联动；核心拓扑轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| direct_pivot_arm | rec_miter_saw_arm_assembly_0001 | saw_arm L253-L332 + tilt joint L346-L364 | eligible if compatible | base→saw_arm 单 REVOLUTE 俯仰（axis X，rear pivot），arm 自带 motor/handle，chop 式 |
| rear_yoke_swing_arm | rec_miter_saw_arm_assembly_0002 | yoke L150-L186 + swing_arm L187-L241 + joints L305-L325 | eligible if compatible | base→rear_pivot_yoke(FIXED)→swing_arm(REVOLUTE Y,0..55°)，后立叉 + 摆臂(section_loft 壳) |
| slide_rail_carriage | rec_miter_saw_arm_assembly_0003 | carriage L188-L211 + saw_head L212-L273 + joints L282-L300 | eligible if compatible | base→carriage(PRISMATIC Y 滑轨,0..0.20)→saw_head(REVOLUTE X 俯仰)，双轨小车，滑动复合 |

### Slot C：blade_guard（head 端圆锯片 + 护罩）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| static_blade_fixed_guard | rec_miter_saw_arm_assembly_0002 | blade_guard_housing L242-L290 + arm_to_guard FIXED L326 | eligible if compatible | 圆锯片为 head visual（不旋转）+ 圆形 blade guard housing（FIXED 到 arm），静态罩 |
| spinning_blade_upper_guard | rec_miter_saw_arm_assembly_b12308f6ee3641ce9ed294755c6ebaa9 | blade L295-L310 + head_to_blade CONTINUOUS L353 | eligible if compatible | 独立 blade part + arbor CONTINUOUS 旋转 + 固定上罩 shell(head visual) |
| spinning_blade_retracting_guard | rec_miter_saw_arm_assembly_8288f5516faf4febbaccc03d9944b0d1 | blade L383-L396 + lower_guard L397-L417 + joints L446-L465 | eligible if compatible | 独立 blade(CONTINUOUS) + lower_guard part(REVOLUTE X,0..1.25 收缩下罩) + guard hub |

硬约束确认：A=3、B=3、C=3 candidate；均有真实 5 星 `model.py:Lx-Ly` 来源；candidate 间为 part tree / joint 拓扑 / primitive 差异（base massing / 联动关节数与类型 / blade-guard 关节拓扑），非颜色/尺寸/材质差异。

## 槽位图（slot graph）

pattern: mixed（parallel_children）

```
[Slot A base] (fixed root：base + fence + 转台座 + 可选 rail column)
   │
   ├─[table_yaw; REVOLUTE; axis=(0,0,1); 转台座 bearing; range≈±0.79..0.87(±45..50°)]
   │      ▼
   │   turntable（kerf insert + miter lock；属 Slot A）
   │
   └─[Slot B arm_linkage] (parallel branch，挂 base)
        ├─ direct_pivot_arm: base --REVOLUTE X(pitch,-0.07..0.95)--> saw_arm
        ├─ rear_yoke_swing_arm: base --FIXED--> yoke --REVOLUTE Y(0..0.96)--> swing_arm
        └─ slide_rail_carriage: base --PRISMATIC Y(0..0.20)--> carriage --REVOLUTE X(pitch)--> saw_head
             ▼  saw head（motor housing + handle + gear case）
             │
             └─[Slot C blade_guard]
                  ├─ static_blade_fixed_guard: blade(visual) + guard --FIXED--> head
                  ├─ spinning_blade_upper_guard: head --CONTINUOUS X(arbor)--> blade ; 上罩 visual
                  └─ spinning_blade_retracting_guard: head --CONTINUOUS X--> blade ; head --REVOLUTE X(0..1.25)--> lower_guard
```

接口点位与跨 slot joint：

- **A 内部 table_yaw（恒存在）**：REVOLUTE，axis=(0,0,1)。接口=turntable 底盘与 base 的 turntable_seat（轴向贴合 bearing），origin 落 seat 中心；range reviewer-gated（±45°/±50°）。
- **A→B（arm linkage，恒存在）**：linkage 的 root（saw_arm / yoke / carriage）挂 base：
  - direct：base 的 rear pivot post ↔ saw_arm 的 pivot barrel，REVOLUTE axis=(1,0,0)，俯仰下压。
  - yoke：base ↔ rear_pivot_yoke（FIXED，立叉座），yoke 顶 ↔ swing_arm（REVOLUTE axis=(0,1,0)，0..55°）。
  - slide：base 的 rail（双轨，cast_wing_base 提供 rail_column+rail_bridge）↔ carriage（PRISMATIC axis=(0,±1,0)，0..0.20m），carriage 的 yoke cheek ↔ saw_head pivot barrel（REVOLUTE axis=(1,0,0) 俯仰）。
- **B→C（blade_guard）**：
  - static：blade 为 head visual；guard housing FIXED 到 arm/head 前端。
  - spinning：head 的 blade_hub/arbor ↔ blade part（CONTINUOUS axis=(1,0,0)，arbor 轴）；上罩 shell 为 head visual。
  - retracting：另加 lower_guard part ↔ head（REVOLUTE axis=(1,0,0)，0..1.25 收缩），guard hub 与 arbor 同轴。

互斥/可选/派生：
- `slide_rail_carriage` ⇒ base 必须提供 rail column/bridge（cast_wing_base，或 base 派生 rail mount）；bench_slab/heavy_rib 不带轨时需派生 rail post 才能配 slide。
- `rear_yoke_swing_arm` 的 pitch 轴为 Y（横向后铰），其余为 X；axis 由 linkage 决定。
- `spinning_blade_*` ⇒ blade 为独立 CONTINUOUS part；`static_blade_*` ⇒ blade 为 head visual。
- `retracting_guard` ⇒ 需独立 lower_guard part + 与 arbor 同轴 REVOLUTE。

## 每槽位 Module Emits / Interfaces

### Slot A / module bench_slab_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | base(slab + fence + turntable_seat) + turntable(plate + kerf insert) | rec_…_0001 / L173-L252 |
| internal joints | table_yaw REVOLUTE Z range±0.82 | rec_…_0001 / L331-L345 |
| downstream interface | turntable seat bearing 面；base rear post 供 direct arm pivot | rec_…_0001 / L331-L364 |

### Slot A / module cast_wing_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | base(plinth + rear_deck + 左右 wing + 双 fence + rear_column + rail_bridge + 双 rail) + turntable(plate + miter_lock + kerf) | rec_…_0003 / L89-L187 |
| internal joints | table_yaw REVOLUTE Z range±0.79 | rec_…_0003 / L274-L281 |
| downstream interface | 双 rail(Cylinder)供 carriage PRISMATIC；rail_bridge/rear_column 支撑 | rec_…_0003 / L143-L156, L282-L291 |

### Slot A / module heavy_rib_base
| emits | 描述 | 来源 |
|---|---|---|
| parts | base(铸座 + fence + 4×tube 加强肋) + miter_table | rec_…_8288 / L196-L275 + tubes L137-L183 |
| internal joints | table_yaw REVOLUTE Z range±50° | rec_…_8288 / L418-L431 |

### Slot B / module direct_pivot_arm
| emits | 描述 | 来源 |
|---|---|---|
| parts | saw_arm(motor housing + handle + gear case + pivot barrel) | rec_…_0001 / L253-L332 |
| internal joints | saw_arm_tilt REVOLUTE axis(1,0,0) range -0.07..0.95 | rec_…_0001 / L346-L364 |
| upstream interface | base rear pivot post ↔ saw_arm pivot barrel | rec_…_0001 / L346-L364 |
| downstream interface | head 前端供 blade/guard | rec_…_0001 / L253-L332 |

### Slot B / module rear_yoke_swing_arm
| emits | 描述 | 来源 |
|---|---|---|
| parts | rear_pivot_yoke(左右板 + web + bridge) + swing_arm(section_loft 壳 + handle tube) | rec_…_0002 / L150-L241 |
| internal joints | base_to_yoke FIXED L305；yoke_to_arm REVOLUTE axis(0,1,0) 0..55° L312 | rec_…_0002 / L305-L325 |
| upstream interface | base ↔ yoke FIXED 座（rear，-x 偏置） | rec_…_0002 / L305-L311 |
| downstream interface | swing_arm 前端供 guard(FIXED) / blade | rec_…_0002 / L187-L241, L326 |

### Slot B / module slide_rail_carriage
| emits | 描述 | 来源 |
|---|---|---|
| parts | carriage(carriage_body mesh + 左右 yoke cheek) + saw_head(pivot barrel + upper_arm + motor_brace + gear_case + motor_housing + blade_hub + guard_shell mesh + handle mesh) | rec_…_0003 / L188-L273 |
| internal joints | base_to_carriage_slide PRISMATIC axis(0,1,0) 0..0.20 L283；carriage_to_head_pitch REVOLUTE axis(1,0,0) -0.87..0 L292 | rec_…_0003 / L282-L300 |
| upstream interface | base 双 rail ↔ carriage（滑动 contact，rail in carriage bore） | rec_…_0003 / L143-L156, L282-L291 |
| downstream interface | saw_head blade_hub/arbor 供 blade/guard | rec_…_0003 / L212-L273 |

### Slot C / module static_blade_fixed_guard
| emits | 描述 | 来源 |
|---|---|---|
| parts | blade_guard_housing（圆罩，FIXED 到 arm）；blade 为 head/arm visual | rec_…_0002 / L242-L290 |
| internal joints | arm_to_guard FIXED L326 | rec_…_0002 / L326 |
| upstream interface | arm 前端 ↔ guard housing 座 | rec_…_0002 / L242-L290 |

### Slot C / module spinning_blade_upper_guard
| emits | 描述 | 来源 |
|---|---|---|
| parts | blade(blade disk mesh + hub)，独立 part；上罩 shell 为 head visual | rec_…_b12308 / L295-L310 |
| internal joints | head_to_blade CONTINUOUS axis(1,0,0) arbor L353 | rec_…_b12308 / L353-L364 |
| upstream interface | head arbor/blade_hub ↔ blade hub（同轴 captured） | rec_…_b12308 / L207-L310 |

### Slot C / module spinning_blade_retracting_guard
| emits | 描述 | 来源 |
|---|---|---|
| parts | blade(disk mesh + hub) + lower_guard(guard_shell mesh + guard hub) | rec_…_8288 / L383-L417 |
| internal joints | arm_to_blade CONTINUOUS axis(1,0,0) L446；arm_to_lower_guard REVOLUTE axis(1,0,0) 0..1.25 L455 | rec_…_8288 / L446-L465 |
| upstream interface | arm arbor ↔ blade hub + lower_guard hub（同轴） | rec_…_8288 / L383-L417 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| base_choice (A) | enum | bench_slab_base / cast_wing_base / heavy_rib_base | sampled | deterministic procedural sampler | Slot A table |
| linkage_choice (B) | enum | direct_pivot_arm / rear_yoke_swing_arm / slide_rail_carriage | sampled | 受 base_choice gating（slide 需 rail column） | Slot B table |
| blade_guard_choice (C) | enum | static_blade_fixed_guard / spinning_blade_upper_guard / spinning_blade_retracting_guard | sampled | 派生 blade 是否独立 part | Slot C table |
| slide_rail_count | int (multiplicity) | 1 或 2 | 2 | 仅 slide linkage；双轨/单轨 | rec_…_0003 L143-L156 |
| fence_segment_count | int (multiplicity) | 1 或 2 | 2 | base 左右 fence 半段 | rec_…_0003 L116-L130 |
| base_wing_count | int (multiplicity) | 0 或 2 | 0 | base 侧延伸 wing | rec_…_0003 L99-L112 |
| miter_yaw_range | float | [±0.70, ±0.90] | ±0.82 | reviewer-gated miter 角 | 全样本 |
| arm_pitch_range | float pair | lower∈[-0.10,0], upper∈[0.50,0.98] | 0..0.90 | reviewer-gated 下压行程 | 0001/0002/0003 |
| slide_travel | float | [0.12, 0.22] | 0.18 | 仅 slide；rail 长度派生 | rec_…_0003 / b12308 |
| blade_radius | float | [0.085, 0.130] | 0.105 | head 尺寸 / guard 半径派生 | rec_…_0003 L255 |
| support_width_scale | float | [0.9, 1.15] | 1.0 | base 平面安全缩放 | resolve_config clamp |
| arm_length_scale | float | [0.92, 1.1] | 1.0 | arm/carriage reach；clamp 使刃落 kerf | resolve_config clamp |

参数只表达语义选择、尺寸、行程、角度、multiplicity 数量、palette；未实现拓扑不进 enum。

## Multiplicity / Copy Logic

**(1) slide_rail_count（核心，slide linkage 派生）**
- count_param：`slide_rail_count`，N_range={1,2}，仅 linkage=slide_rail_carriage
- copied object：导轨 Cylinder（base 上）+ 对应 carriage bore
- naming：`left_rail`/`right_rail`（2）或 `center_rail`（1）
- placement：双轨镜像于中线 x=±0.07；单轨居中
- joint policy：carriage PRISMATIC 沿 rail 轴；rail 静态，无独立 joint
- source/gating：rec_…_0003 L143-L156（twin）；rec_…_b12308（twin）

**(2) fence_segment_count（base 围栏半段）**
- count_param：`fence_segment_count`，N_range={1,2}
- copied object：fence Box（左/右半段，让出锯缝）
- placement：左右镜像于 kerf 线
- source/gating：rec_…_0003 L116-L130（双 fence）；rec_…_0001（单 fence）

**(3) base_wing_count（侧延伸支撑）**
- count_param：`base_wing_count`，N_range={0,2}
- copied object：support wing Box，base 两侧外伸
- source/gating：rec_…_0003 L99-L112（2 wings）

**(4) blade teeth / kerf / handle — 固定，不采样**
- 锯齿、kerf 板、handle 为 module-local fixed mesh/visual，不暴露 `*_count`。

## 拓扑多样性审计

总组合数（gating 前）：A(3) × B(3) × C(3) = 27；× slide_rail_count(2) × fence_segment(2) × base_wing(2) 在 slide/相关子集中再翻几倍。compatibility matrix 裁剪后估算合法组合 **≥ 40**（slide 需 rail base；yoke pitch 轴 Y）。

理由：仅 A×B×C 合法子集已 >10 distinct 拓扑等价类（base massing × linkage 关节数/类型 [direct 1 REVOLUTE / yoke FIXED+REVOLUTE / slide PRISMATIC+REVOLUTE] × blade-guard 关节拓扑 [0 / CONTINUOUS / CONTINUOUS+REVOLUTE]）；再叠 slide_rail_count、fence/wing multiplicity、yaw/pitch range。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed deterministic procedural sampling —— 先选 base_choice → 经 compatibility matrix 得 linkage 合法子集再选（slide 需 rail base）→ 选 blade_guard_choice → 派生 slide_rail_count / fence_segment_count / base_wing_count / yaw·pitch range / 连续 scale。`seed=0` 不特殊。所有非法组合由 compatibility matrix + resolve_config clamp 拦截。random sweep：seeds 0-49 初判，0-999 成熟审计；viewer 目检覆盖每个 base×linkage×blade_guard 家族至少 1 例，重点：刃落 kerf 线、down-pose 刃不穿 table/base、guard 收缩不穿刃、slide 全行程 carriage 不脱轨、yaw 极限刃不撞 fence、blade arbor 同轴。
Topology target：1000-seed slot choice tuple distinct 建议 ≥40（类别本身组合有限，受 slide↔rail base 等强 gating 约束）；低于 300 已在此说明原因（仅 3×3×3 主轴 + 有限 multiplicity）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
regression overrides：初版默认 none；若 sweep 暴露特定失败组合再以稀疏、显式 + 失败回归理由加入，不得用小型 curated/modulo 表当主 seed domain。
Controlled local parameterization：初版即纳入 `support_width_scale [0.9,1.15]`、`arm_length_scale [0.92,1.1]`、`blade_radius [0.085,0.130]`、`slide_travel [0.12,0.22]`、`miter_yaw_range`、`arm_pitch_range`（后两 reviewer-gated）。全部在 resolve_config clamp / 派生，受 刃-kerf 对齐、down-pose 刃-table 间隙、guard-刃 同轴、carriage-rail 行程、yaw-fence 间隙约束；不改变 slot/module 选择、slide_rail_count、blade 独立性等拓扑量。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | base→linkage→blade_guard 顺序选择 + 每步 compatibility gate；weighted（chop 家族权重高，slide 次之） | slot_choices_for_seed matches build choices |
| compatibility matrix | slide_rail_carriage↔rail base（cast_wing 或派生 rail post）；yoke pitch 轴 Y；spinning blade↔独立 CONTINUOUS part；retracting guard↔独立 lower_guard REVOLUTE 同轴 arbor | no floating（blade/guard/carriage 不漂浮）、collision（down-pose 刃 vs table/base、guard vs 刃）、axis（yaw Z、pitch X/Y、arbor X）、max multiplicity（rail≤2）、bulky module、optional child（blade/guard 缺省安全） |
| controlled local variation | support_width/arm_length/blade_radius/slide_travel/yaw·pitch range，全 clamp | 比例变化不破坏 刃-kerf 对齐、刃-table 间隙、arbor 同轴、carriage 行程、joint origin、类别 identity |
| regression overrides | none（初版） | 仅失败回归或审核指定时显式加入 |
| random sweep | seeds 0-49 初判，0-999 成熟审计 | 与 contract failures（floating/overlap/axis/down-pose 穿模） |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A base_table | 3 | yes | yes | |
| B arm_linkage | 3 | yes | yes | 核心拓扑轴 |
| C blade_guard | 3 | yes | yes | |

兼容矩阵（合法 / 互斥 / fallback）：

- `slide_rail_carriage` ⇒ base ∈ {cast_wing_base}（自带 rail column/bridge）；若 base=bench_slab/heavy_rib 必须派生 rail post 才合法，否则 fallback 到 direct/yoke。
- `direct_pivot_arm` / `rear_yoke_swing_arm` ⇒ 任意 base（chop 式，不需 rail）。
- `rear_yoke_swing_arm` 的 pitch 轴=(0,1,0)（横向后铰）；direct/slide 的 pitch 轴=(1,0,0)。
- `spinning_blade_upper_guard` / `spinning_blade_retracting_guard` ⇒ blade 为独立 CONTINUOUS part（arbor axis (1,0,0)）。
- `static_blade_fixed_guard` ⇒ blade 为 head visual + guard FIXED；不建 CONTINUOUS。
- `spinning_blade_retracting_guard` ⇒ lower_guard 与 blade arbor 同轴 REVOLUTE；收缩 pose 不得穿刃/穿 table。
- miter yaw 轴必须 Z；arm pitch 必须水平（X 或 Y）；blade arbor 必须水平 X。

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C 三元组 + slide_rail_count 等派生）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal module combinations（slide↔rail base、yoke pitch 轴 Y、spinning↔独立 blade、retracting↔lower_guard 同轴）
- optional regression overrides are sparse and justified（初版 none）
- controlled local scale params (support_width/arm_length/blade_radius/slide_travel/yaw·pitch range) clamped；不破坏 刃-kerf 对齐、刃-table 间隙、arbor 同轴、carriage 行程、joint origin、类别 multiplicity
- critical InterfaceSpec / MatingContract points exist：turntable<->base seat（yaw bearing）、carriage<->rail（滑动）、arm/head pivot barrel<->base/carriage（pitch）、blade hub<->arbor（同轴 captured）、lower_guard hub<->arbor
- key joints have expected type/axis/range：table_yaw REVOLUTE Z ±0.79..0.87；carriage_slide PRISMATIC Y 0..0.20；arm/head pitch REVOLUTE X(或 Y) 下压；blade_spin CONTINUOUS X；lower_guard REVOLUTE X 0..1.25
- 几何/primitive：保留 ExtrudeWithHoles / section_loft / tube_from_spline_points / mesh_from_geometry（carriage/guard/handle/blade/lower_guard），不得降级成 Box/Cylinder
- copied objects follow naming/placement policy（left/right rail、左右 fence 镜像）
- down-pose（arm pitch 到下压极限）刃落 kerf 线、不穿 table/base；只在 rest pose 验会漏（见 reject）

## Reject cases

- 缺 miter yaw 或 arm pitch 任一核心运动（退化成静态锯/单 DOF）。
- yaw 轴非竖直 Z，或 arm pitch 轴竖直，或 blade arbor 非水平。
- slide linkage 配无 rail 的 base，carriage 脱轨/漂浮；或 carriage 不在 rail 上滑（PRISMATIC 轴与 rail 不平行）。
- spinning blade 不绕 arbor 同轴旋转（轴偏移），或 blade 与 head 脱开漂浮。
- retracting lower_guard 与 blade 不同轴、收缩 pose 穿刃或穿 table。
- 把 carriage/guard/handle 的 mesh、swing_arm 的 section_loft、base/table 的 ExtrudeWithHoles 降级成 Box/Cylinder（违反 primitive 保真）。
- 只在 rest pose 验俯仰 —— 改 pitch axis 符号/range 必须 pose 到下压极限实测刃-table 间隙与刃落 kerf（[[project_sweep_only_rest_pose]]）。
- guard/blade 第二/第三自由度几何不连贯（罩铰不同轴、blade 悬空）却靠 sweep pass 蒙混 —— viewer 目检，不连贯就退回 static（[[feedback_gated_aux_geometry_coherence]]）。
- 把 fence/刃罩做成不透明实心把运动件封死看不见（[[feedback_enclosed_mechanism_open_front]]）。

## 与相邻类别的边界

- 不该混入：`paper_cutter_guillotine` —— 单铡刀下压、无 miter 回转转台、无圆锯片/arbor。
- 不该混入：通用 `rotary_table_with_tilting_trunnion` —— 无圆锯切割臂与 blade guard，仅回转+倾斜台。
- 不该混入：`bandsaw` / `table_saw` —— 锯片切割机构不同（带锯/台锯无下压俯仰臂 + miter 转台组合）。
- 不该混入：`drill_press` / `radial_arm` 通用摇臂 —— 必须有圆锯片 + miter 转台 + fence 的斜切锯身份。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | bench_slab_base / direct_pivot_arm / static blade ref | rec_miter_saw_arm_assembly_0001 | base L173-L252, saw_arm L253-L332, joints L331-L364 | 平板 base + 直接铰臂 chop 链 |
| S2 | A/B/C | flat base / rear_yoke_swing_arm / static_blade_fixed_guard | rec_miter_saw_arm_assembly_0002 | base L76-L149, yoke L150-L186, swing_arm L187-L241, guard L242-L290, joints L291-L326 | 后铰叉摆臂 + 静态罩(FIXED) + section_loft |
| S3 | A/B | cast_wing_base / slide_rail_carriage | rec_miter_saw_arm_assembly_0003 | base L89-L162, turntable L163-L187, carriage L188-L211, saw_head L212-L273, joints L274-L300 | 双轨滑动小车 + 俯仰 head + rail base |
| S4 | B/C | slide / spinning_blade_upper_guard | rec_miter_saw_arm_assembly_b12308f6ee3641ce9ed294755c6ebaa9 | base L63-L106, turntable L107-L162, carriage L163-L206, saw_head L207-L294, blade L295-L310, joints L311-L364 | 滑动复合 + CONTINUOUS 旋刃 |
| S5 | A/B/C | heavy_rib_base / direct arm / spinning_blade_retracting_guard | rec_miter_saw_arm_assembly_8288f5516faf4febbaccc03d9944b0d1 | base L196-L250, table L251-L275, arm L276-L382, blade L383-L396, lower_guard L397-L417, joints L418-L465 | 铸座 + 旋刃 + REVOLUTE 收缩下罩 |

## 模板实现备注（可选）

- 共享 helper：`_extrude_base`（ExtrudeWithHolesGeometry base/table，禁降级）、`_section_loft_arm`（swing_arm 壳）、`_tube`（handle/arm rail/rib via tube_from_spline_points）、`_carriage_mesh` / `_guard_mesh` / `_blade_mesh` / `_lower_guard_mesh`（mesh_from_geometry）、`_rails(n)`（slide_rail_count 镜像）、`_fence(n)`。
- 重点 InterfaceSpec / MatingContract：turntable↔base turntable_seat（yaw 轴向贴合）；carriage↔rail（滑动 captured，rail in carriage bore，element-scoped allow_overlap）；saw_arm/head pivot barrel↔base/carriage yoke cheek（pitch captured pin）；blade hub↔arbor（CONTINUOUS 同轴 captured）；lower_guard hub↔arbor（同轴）。
- captured-pin overlap：pivot barrel-in-yoke、blade hub-on-arbor、rail-in-carriage-bore、guard hub-on-arbor 处需 element-scoped allow_overlap，仅对真实意图穿插声明。
- 暂不进入 seed domain（待实现后再开）：单轨 slide_rail_count=1 与 base 派生 rail post（bench/heavy base + slide）二期；blade 锯齿细节作为 module-local mesh，不单列。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （新建 spec；5 个 5 星样本全量精读；parallel_children 主结构 base‖turntable + arm linkage；待人工审核） |
