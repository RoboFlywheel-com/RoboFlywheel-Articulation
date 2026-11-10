# Healthcare / Wheelchair — modular template spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `Healthcare_Wheelchair` |
| template path | `agent/templates/Healthcare_Wheelchair.py` |
| test path (optional) | `tests/agent/test_wheelchair_template.py` (skipped; sweep is authority) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (frame chassis root; propulsion / footrest / backrest / armrest / frame-brace children all parent to `frame`) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this category (1 parent + 6 forked variants) |
| source_index_policy | only adopted module sources are indexed below |

所有 7 个样本共享同一底盘：一个连通的深色钢管 `frame`（tube_from_spline_points 合成的 hero mesh），坐垫/靠背用 Box 布料 + 缝线条，2 个后驱动轮（CONTINUOUS y），2 个前万向脚轮（fork CONTINUOUS z swivel + wheel CONTINUOUS y roll）。变体各改一个功能层：小轮+推手（transit）、电机/电池/摇杆（powered）、抬腿（elevating legrest）、后仰靠背+头枕（reclining）、翻转桌板扶手（desk armrest）、剪式折叠 X-brace（folding）。

## 核心身份

手动 / 陪护(transit) / 电动(powered) 轮椅：刚性或可折叠的钢管框架；一张吊索/软垫座椅 + 靠背；**2 个后轮（CONTINUOUS 滚动）**；**2 个前万向脚轮（CONTINUOUS 摆头 swivel + CONTINUOUS 滚动 roll）**；脚踏 / 抬腿板；扶手。左右件为镜像对（multiplicity = 2，镜像跨 x-z 平面，y 取 ±）。默认成熟域是日常人力/陪护/电动轮椅，坐高约 0.46–0.50 m，后轮直径 0.30–0.61 m（transit 小轮 ~0.20 m），前脚轮 ~0.16–0.20 m。

不该混入：办公椅/exam 椅（Science_Surgical_chair 是单柱气升，不是双大轮 + 前脚轮行走底盘）；婴儿车/购物手推车（无坐姿乘员上身靠背 + 扶手 + 脚踏三件套）；医院病床（卧姿，无自走轮组）。

## 槽位 + 候选模块表

底盘 `frame` 是根 part（不是 slot；固定脊柱含 2 后轮 + 2 前脚轮 CONTINUOUS 关节，保证每个 seed 至少有可动关节）。5 个可替换结构层如下。

### Slot A：propulsion（后驱动轮 + 驱动系装饰）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| large_pushrim_manual | forked_anchor (parent) | rec_a-manual-wheelchair-…_dcd9a412 | `_rear_wheel_meshes` L109-126；rear wheel part+joint L291-307 | eligible if compatible | 大直径细胎轮：tire/rim/push_rim 三 torus + 28 chrome 辐条 + hub cylinder + 8 push-rim 支柱；手推圈自走 |
| small_transit | forked_anchor | rec_wheelchair_var_transit | `_transit_rear_wheel_meshes` L109-118；push handles L282-308；wheels L310-325 | eligible if compatible | 小实心后轮：tire torus + solid disk + hub，无 push_rim / 无辐条；靠背立管顶加陪护推手（stem + rubber grip） |
| powered_drive | forked_anchor | rec_wheelchair_var_powered | `_motor_drive_wheel_meshes` L109-122；battery L292-305；motor housing L307-321；joystick L323-349；wheels L351-367 | eligible if compatible | 加厚驱动轮 + 重电机 hub + 20 辐条；座下电池箱 + 左右电机/齿轮箱壳 + 右扶手前端摇杆 pod（base+stem+knob+LED）+ 摇杆支柱 |

### Slot B：footrest（脚踏 / 抬腿）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| swingaway_flipup | forked_anchor (parent) | rec_a-manual-wheelchair-…_dcd9a412 | frame hanger L158-167 + hinge pins L239-251；footplate part+joint L344-371 | eligible if compatible | 前吊架管 + hinge 销；双 `{side}_footplate` REVOLUTE（-Y，[0,1.55]）翻起，hinge barrel + 斜金属板 |
| elevating_legrest | forked_anchor | rec_wheelchair_var_elevating_legrest | `_legrest_arm_mesh` L198-212；frame stub L155-165 + pivot pins L245-251；legrest L343-368 | eligible if compatible | 短 pivot stub + 销；双 `{side}_legrest` REVOLUTE（-Y，[0,1.20]）抬起，chrome 支臂 + 叉形 rail + vinyl 小腿垫 |

### Slot C：backrest（靠背）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| fixed_sling_back | forked_anchor (parent) | rec_a-manual-wheelchair-…_dcd9a412 | tall uprights L149-150；backrest box + seams L260-279 | eligible if compatible | 立管上到 z≈0.90 折至 0.96；靠背 = frame 上的 fused Box + 竖缝条（不动 → parent.visual，非独立 part） |
| reclining_back | forked_anchor | rec_wheelchair_var_reclining_back | 短 uprights L149 + recline pivot shaft L187；backrest part L300-347 | eligible if compatible | 立管短到 z≈0.66；独立 `backrest` part（管架 + 高软垫 + 头枕 + 双 rubber grip）REVOLUTE（-Y，[0,0.60]）后仰 |

### Slot D：armrest（扶手）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| fixed_tubular_arm | forked_anchor (parent) | rec_a-manual-wheelchair-…_dcd9a412 | armrest pad L282-288 | eligible if compatible | 固定全长软垫扶手 = frame arm rail 上的 fused Box（不动 → parent.visual） |
| desk_flipback_arm | forked_anchor | rec_wheelchair_var_desk_armrest | `_armrest_mesh` L220-231；armrest part+joint L309-330 | eligible if compatible | 双 `{side}_armrest` REVOLUTE（-Y，[0,1.65]）向后翻起；钢管臂架 + 布垫；桌长 ~0.28 |

### Slot E：frame（刚性 vs 折叠）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| rigid_frame | forked_anchor (parent) | rec_a-manual-wheelchair-…_dcd9a412 | frame X-brace fused in mesh L177-178 | eligible if compatible | 座下 X-brace 直接熔进 frame hero mesh，不折叠，无额外 part |
| cross_brace_folding | forked_anchor | rec_wheelchair_var_folding_xframe | `_BRACE_PIVOT` L182；brace meshes L185-221；fold parts+joints L329-364 | eligible if compatible | `fold_brace_left`（FIXED 到 frame）+ `fold_brace_right`（REVOLUTE 绕 X 剪式，[0,0.50]）；两根斜管在 pivot 交叉钉合 |

硬约束满足：每个 candidate 都是 `forked_anchor` + 真 model.py:Lx-Ly；无单-candidate slot（A=3, B/C/D/E=2）。B/C/D/E 降到 2 的理由：该小类的这些功能层在样本池里只有"parent 基线 + 单一 fork 替代"两种结构（footrest 只有翻起/抬腿两式，backrest 只有固定/后仰，armrest 只有固定/桌板翻，frame 只有刚性/剪式折叠）——样本池不含第三种结构；③ 主多样性由 Slot A 的 3 个 propulsion 家族承载。

## 槽位图（slot graph）

pattern: parallel_children

```
                         frame (root chassis part, config-aware hero mesh)
                           │  (frame mesh + fixed upholstery adapt to C/D/A choices)
  ┌──────────────┬─────────┴───────────┬─────────────────┬──────────────────┐
  │              │                     │                 │                  │
[fixed spine] Slot A propulsion   Slot B footrest   Slot C backrest    Slot D armrest   Slot E frame-brace
 2×rear_wheel  rear wheel geom     footplate/legrest  (reclining →      (desk → separate    (folding →
  CONTINUOUS y  swap + motor/       ×2 REVOLUTE -Y     separate backrest  armrest ×2          fold_brace_left FIXED
 2×caster_fork  battery/joystick    at frame front     REVOLUTE -Y at     REVOLUTE -Y at      + fold_brace_right
  CONTINUOUS z  OR transit handles  hinge pins         recline shaft)     rear-upright pins)  REVOLUTE +X scissor)
 2×caster_wheel (frame visuals)
  CONTINUOUS y
```

接口点位（全部是 parent=`frame`（或 fork/fold_left）→ child 的直接 `model.articulation`，captured-pin 语义，**grandfathered 无 MatingContract**，理由：轮毂穿轴 / fork 穿脚轮 hub / hinge 销穿 barrel / brace 剪式钉合都是 pin-through-sleeve，无法表达成两个轴对齐面接触；用 element-scoped `allow_overlap` + `expect_overlap` 保留检查，镜像自各 source 的 run_tests）：

- rear wheel：origin `(-0.220, ±0.380, 0.300)`，axis `(0,1,0)`，CONTINUOUS。frame 的 `rear_axle` cylinder 提供 hub 穿轴对称轴。
- caster fork：origin `(0.420, ±0.235, 0.210)`，axis `(0,0,1)`，CONTINUOUS。frame 的 `{side}_caster_socket` 提供竖直摆头轴。
- caster wheel：parent=fork，origin `(-0.105, 0, -0.110)`，axis `(0,1,0)`，CONTINUOUS。fork 尾部 axle crossbar 提供 hub 轴。
- footplate：origin `(0.455, ±0.135, 0.255)`，axis `(0,-1,0)`，REVOLUTE [0,1.55]。frame `{side}_footrest_hinge` 销。
- legrest：origin `(0.325, ±0.135, 0.420)`，axis `(0,-1,0)`，REVOLUTE [0,1.20]。frame `{side}_legrest_pivot` 销。
- backrest（仅 reclining）：origin `(-0.245, 0, 0.500)`，axis `(0,-1,0)`，REVOLUTE [0,0.60]。frame recline pivot shaft。
- desk armrest：origin `(-0.245, ±0.280, 0.655)`，axis `(0,-1,0)`，REVOLUTE [0,1.65]。frame `{side}_arm_hinge` 销（模板新增：从 arm rail y=0.235 伸到 y=0.290 的横向销，保证 armrest post 与 frame 有真接触 + 支撑关节原点）。
- fold brace：`frame_to_fold_brace_left` FIXED origin `(0.018,0,0.380)`；`fold_brace_left_to_right` REVOLUTE origin `(0,0,0)` axis `(1,0,0)` [0,0.50]。

互斥/派生：
- Slot C=reclining → frame 立管变短（z→0.66）且不 emit fused backrest box；新增 recline pivot shaft + drop 顶部 cross-member。C=fixed → 立管高（0.90→0.96）+ fused backrest box。
- Slot D=desk → 不 emit fused armrest pad，改 emit `{side}_arm_hinge` 销；D=fixed → emit fused armrest pad Box。
- Slot A=transit → 推手仅在 C=fixed 时由 frame emit（C=reclining 时独立 backrest 已自带 grip，避免重复）。A=powered → 摇杆 pod 立在自带 `joystick_post`（从 arm rail z=0.655 升到 pod 底）上，与 D 选择无关地被 frame 支撑。

## 每槽位 Module Emits / Interfaces

### root / frame（config-aware）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame` | 全样本 build L219-288 |
| visuals（always） | `tubular_frame` hero mesh（config-aware：立管高/前脚架式样/是否 recline shaft）、`rear_axle`、`{side}_caster_socket`、`seat_cushion`、`seat_seam_*` | L219-279 |
| visuals（conditional） | C=fixed: `backrest`+`backrest_seam_*`；D=fixed: `{side}_armrest_pad`；B=swingaway: `{side}_footrest_hinge`+`{side}_footrest_bracket`；B=elevating: `{side}_legrest_pivot`；D=desk: `{side}_arm_hinge`；A=transit&C=fixed: `{side}_push_handle_stem/grip`；A=powered: `battery_box`+`{side}_motor_housing`+`{side}_gearbox_cap`+`joystick_post`+`joystick_base/stem/knob/led` | 见各 source |
| internal joints | 无（frame 是 root）| — |
| downstream interface | 概念性：frame 是所有 child 的公共 parent；无 assembler chain joint，直接 `model.articulation(parent=frame,…)`（parallel-children 模式，见 AUTHORING §B） | — |

### Slot A / rear wheels + casters（fixed spine casters）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `left_rear_wheel`,`right_rear_wheel`,`left_caster_fork`,`right_caster_fork`,`left_caster_wheel`,`right_caster_wheel` | L291-341 |
| internal joints | `frame_to_{side}_rear_wheel` CONTINUOUS y；`frame_to_{side}_caster` CONTINUOUS z；`{side}_caster_to_wheel` CONTINUOUS y | L299-341 |

### Slot B / footrest
| emits | parts `{side}_footplate` (swingaway) 或 `{side}_legrest` (elevating)；joint `frame_to_{side}_footplate/legrest` REVOLUTE -Y | L344-371 / L343-368 |

### Slot C / backrest（仅 reclining 出 part）
| emits | part `backrest`（frame_tubes + back_panel + headrest_pad + back_seam_* + {side}_grip）；joint `frame_to_backrest` REVOLUTE -Y | L300-347 |

### Slot D / armrest（仅 desk 出 part）
| emits | parts `{side}_armrest`（armrest_frame + armrest_pad）；joint `frame_to_{side}_armrest` REVOLUTE -Y | L309-330 |

### Slot E / frame-brace（仅 folding 出 part）
| emits | parts `fold_brace_left`(FIXED)+`fold_brace_right`(REVOLUTE +X)；joints `frame_to_fold_brace_left`,`fold_brace_left_to_right` | L329-364 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| propulsion | enum | large_pushrim_manual / small_transit / powered_drive | — | choice | deterministic sampler | Slot A |
| footrest | enum | swingaway_flipup / elevating_legrest | — | choice | sampler | Slot B |
| backrest | enum | fixed_sling_back / reclining_back | — | choice | sampler | Slot C |
| armrest | enum | fixed_tubular_arm / desk_flipback_arm | — | choice | sampler | Slot D |
| frame_brace | enum | rigid_frame / cross_brace_folding | — | choice | sampler | Slot E |
| palette_style | enum | chrome_navy / black_powder_black / blue_powder_navy / red_powder_black / grey_powder_teal | chrome_navy | choice | sampler；驱动每个 `.visual(material=…)` | ⑥ |
| wheel_dia_scale | float | [0.95, 1.08] | 1.0 | independent | 缩放后驱动轮 torus/rim/push_rim/hub/spoke 半径；hub 长度不变（穿轴不变） | L112-126 |
| seat_width_scale | float | [0.94, 1.06] | 1.0 | independent | 只缩座垫/靠背/扶手垫 Box 的 y 维（不动 frame track）；upholstery 派生 | L256-288 |
| back_height_scale | float | [0.92, 1.10] | 1.0 | independent | 缩 fixed backrest box z 维 / reclining back_panel z 维 | L260/L307 |
| (—) | constraint | — | — | inequality | `rear_wheel_major·wheel_dia_scale` 保持 hub 长 0.070 内穿轴；wheel_dia_scale 下限 0.95 保证 manual 轮直径 ≥ 0.556（run_tests 用 config 派生期望值，不写死） | 接口 |

连续尺寸采样契约：先独立采 3 个 scale（均匀 + round），无 equation/conditional 依赖（各自 clamp）；无跨部件 inequality 需回缩（scale 都是局部 upholstery/wheel 半径，clamp 即安全）。

### 7.5 编译预算 / compile budget
自报 **≤15 s/seed**（依据：单样本记录本身编译约 5–12 s；最重是 manual 后轮 28 辐条 ×2 + 3 torus/轮 ×96 段）。分档 tessellation：torus `tubular_segments=64, radial_segments=16`（比 source 的 96 略降，hero 轮仍圆滑）；hub/pin cylinder `radial_segments=32`；辐条/管 `samples_per_segment=1`（直段）；frame 主曲管 `samples_per_segment` 保 4-8。L/R 两侧复用同一 mesh 生成函数。超预算先降 torus 段再迭代。sweep `--compile-timeout 120`（3× 预算 watchdog）。

## Multiplicity / Copy Logic

- count_param: `side`（L/R 镜像对），wheels / casters / footplates / legrests / armrests 各 **固定 2**，跨 x-z 平面镜像（y → ±）。
- N_range: 固定 {2}，非自由 multiplicity 轴（真实轮椅恒 2 后轮 + 2 前脚轮 + 2 脚踏 + 2 扶手）。测试与产品域都是 2。
- copied object / naming / placement / joint policy: `{side}_<part>` for side in (`left`,`right`)，y 取 `+abs` / `-abs`；每个 wheel 自己的 CONTINUOUS roll，caster 自己的 CONTINUOUS swivel+roll，footrest/armrest 自己的 REVOLUTE，统一 joint policy（同 axis 同 range，仅 y 号镜像）。用一个 `for side in ("left","right")` 循环发射。
- source/gating: 无条件恒 2；不暴露 `*_count`。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 有 | frame 公共 parent + 镜像 L/R children；folding 追加 fold_brace_left(FIXED)+fold_brace_right(REVOLUTE) 是**替代骨架**；reclining 追加独立 backrest part；desk 追加独立 armrest ×2；elevating vs swingaway 换 footrest part。全 forked_anchor。|
| └ multiplicity | 同构件 ×N | 无自由轴 | 见 §8：L/R 固定 2，声明为非自由 multiplicity。|
| ② 关节类型 | 换 type/轴 | 有 | CONTINUOUS y（rear wheel / caster wheel）、CONTINUOUS z（caster swivel）、REVOLUTE -Y（footplate/legrest/backrest/armrest）、REVOLUTE +X（fold）、FIXED（fold_left）。每种都在 sweep 出现（casters/wheels 恒在；REVOLUTE 由 B/C/D/E 保证）。全 source-backed。|
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | Slot A propulsion 3 族：manual 大细胎多辐 push-rim 轮 / transit 小实心盘轮 / powered 加厚重电机轮+电池+电机壳（drivetrain 改主体读法）。form_subtype：Volumetric Envelope Form（后轮体量：细胎 vs 实心盘 vs 加厚）+ Macro Surface Construction（driveline：手推圈 / 陪护推手 / 电池-电机-摇杆）。加 Slot E rigid vs folding（剪式 X-brace 改座下宏观构成）。均 forked_anchor，登记进 `slot_choices`。|
| ④ 表面装饰 | 叠加表面细节 | 有 | 后轮辐条数（manual 28 / powered 20 / caster 6）、坐垫/靠背 upholstery 竖缝&横缝条、transit rubber 推手 grip、powered 电池箱导轨/齿轮箱盖/LED、reclining 头枕缝条。record_only + world_knowledge。装饰皆写成宿主 part visual、贴合宿主面（缝条贴坐垫/靠背面、辐条从 hub 半径派生），不作独立 part。|
| ⑤ 尺寸/行程 | 只改连续尺寸/行程 | 有 | wheel_dia_scale [0.95,1.08]、seat_width_scale [0.94,1.06]、back_height_scale [0.92,1.10]（见 §7）。关节运动包络：footplate REVOLUTE -Y [0,1.55]（翻起，顶端上移 ≥0.05）；legrest -Y [0,1.20]（抬起，顶端上移 ≥0.08）；backrest -Y [0,0.60]（后仰，背顶 -X 后移 & 下降）；armrest -Y [0,1.65]（后翻，pad footprint 移位）；fold +X [0,0.50]（剪式，右 brace z 范围变化 ≥0.02）；caster swivel CONTINUOUS z（转 90° 尾迹 y 位移 >0.025）；wheels CONTINUOUS 整圈。motion_test_plan：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=40, ignore_fixed=True)` + 每机构一条 targeted `ctx.pose`（footplate/legrest 抬升、backrest 后仰、armrest 移位、fold 剪动、caster 摆头）；captured-pin 用 element-scoped allow_overlap 全程豁免。|
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 colorways：chrome_navy / black_powder_black / blue_powder_navy / red_powder_black / grey_powder_teal。材质大类：metal（frame chrome/powder-coat + 轮 chrome rim/spoke/hub）、fabric（upholstery navy/black/teal）、rubber（tire/grip 恒黑）、plastic（powered 电机壳/摇杆）。metal + fabric + rubber ≥ ceil(0.5×5)=3 覆盖。|

**收尾自检**：template batch 0-9 需肉眼见到 manual/transit/powered 三种后轮明显不同、fixed vs reclining 靠背高度差、swingaway vs elevating 脚踏、rigid vs folding 座下、5 种涂装（frame 颜色 + upholstery 颜色）都出现、关节开合全程不穿模。

## 拓扑多样性审计

总组合数：A(3) × B(2) × C(2) × D(2) × E(2) = **48** 结构组合（× 5 palette × 3 连续 scale 域 → 视觉空间远大于 48）。


seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 对 5 个 slot 各 `rng.choice`（含 seed 0），palette `rng.choice`，3 个 scale `rng.uniform` + round。无 compatibility gate 需排除非法组合（所有 48 组合都物理可造：frame mesh 依 C 选择变立管高度，A=transit 推手依 C 条件 emit，A=powered 摇杆自带支柱——都在 build 内解析，无关 assembler）。无 regression override。random sweep 0-35 初验，viewer 目检 0-9。

Topology target：1000-seed slot choice tuple distinct 上界 = 48 结构组合（× scale 分箱 → 按 ≥300 report-only 口径观察 视觉 distinct），受本小类"L/R 固定 2、功能层各 2-3 式"真实结构约束，48 是类别真实上界，合理。

Controlled local parameterization：`wheel_dia_scale`、`seat_width_scale`、`back_height_scale`（§7）——均 independent clamp，不破坏接口（scale 只动 upholstery Box y/z 维 + 后轮半径，不动 frame track / 关节原点 / 穿轴 hub 长 / L-R multiplicity）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 5 slot 独立 rng.choice + palette + 3 scale uniform；seed 0 不特殊 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 全 48 组合合法；条件派生（frame 立管随 C、transit 推手随 C、powered 摇杆自撑）在 build 内解析 | 无 floating / collision / axis / 穿模 失败 |
| controlled local variation | 3 个局部 scale，resolve_config 内 clamp | 比例变而接口/clearance/joint origin/identity 不破 |
| regression overrides | none | — |
| random sweep | 0-15 fast → 0-35 final → corner | contract failures；axis_realization |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A propulsion | 3 | yes | yes | ③ 主多样性承载 slot |
| B footrest | 2 | yes | no | 样本池仅翻起/抬腿两式 |
| C backrest | 2 | yes | no | 样本池仅固定/后仰两式 |
| D armrest | 2 | yes | no | 样本池仅固定/桌板翻两式 |
| E frame | 2 | yes | no | 样本池仅刚性/剪式折叠两式 |

## Validator
- slot_choices_for_seed 返回已实现 module 名（A/B/C/D/E 五元组）
- config_from_seed 对所有 seed（含 0）用 deterministic 采样
- 全 48 组合合法，无非法组合需 gate
- 无 regression override
- 3 个局部 scale 在 resolve_config clamp，不破接口/clearance/joint origin/multiplicity
- captured-pin joint（wheel/caster/hinge/fold）grandfathered，element-scoped allow_overlap + expect_overlap 保留退化检查
- 关键 joint type/axis/range 符合 §槽位图
- L/R copied object 遵循 `{side}_` 命名 + y 镜像

## Reject cases
- 后轮/脚轮降级成 Box/Cylinder（须保留 torus+spoke+tube hero mesh）
- 装饰（缝条/电池箱/摇杆/推手/头枕）做成 FIXED part 而非 parent.visual（违反 Rule 1）
- fixed backrest / fixed armrest 做成独立 part（不动就不是 part）
- reclining 时 frame 立管仍高 → 与独立 backrest 重叠穿模；或 desk armrest 无 frame 侧 hinge 销 → armrest isolated part
- 摇杆 pod 悬空（无 joystick_post 支撑）/ transit 推手在 reclining 上重复
- 关节 origin 落在空气里（须落在 axle / socket / hinge 销 / recline shaft 上）
- monochrome（palette 未驱动 .visual）或 upholstery/frame 颜色不随 palette 变
- fold brace 剪式关节反向或范围过大导致座下穿模

## 与相邻类别的边界
- 不该混入：Science_Surgical_chair（单气升柱 exam 椅，无双大后轮 + 前脚轮行走底盘）
- 不该混入：Healthcare_Adjustable_hospital_bed（卧姿床，无坐姿乘员靠背/扶手/脚踏三件套 + 无自走轮组）
- 不该混入：购物/平板手推车（无乘员上身座椅系统）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | spec 与 template 同一 session 连续产出；captured-pin grandfathering 与 5-star source run_tests 一致 |

## 模板实现备注
- 共享 helper：`_merge_tube` / `_wheel_plane_torus` / `_wheel_axis_cylinder` / `_spoke_mesh` / `_caster_fork_mesh`（全样本一致）；wheel mesh 三个 dict 函数按 propulsion 分。
- 单一来源几何量：所有 z/x/y 锚点（axle z=0.300、caster socket 0.420/0.210、footrest hinge 0.455/0.255、legrest pivot 0.325/0.420、recline shaft 0.500、arm rail 0.655、fold pivot 0.018/0.380）定义成模块级常量，frame mesh 与 child 关节共用同一常量。
- captured-pin element-scoped allow_overlap（镜像各 source run_tests）：rear_axle↔hub、fork↔hub、footrest_hinge↔hinge_bar/plate_neck、legrest_pivot↔arm、recline shaft↔backrest frame_tubes、arm_hinge↔armrest post、motor_housing↔hub（powered）、fold_left↔fold_right + tubular_frame↔brace_tube。
- desk armrest 须新增 frame 侧 `{side}_arm_hinge` 横向销（arm rail y=0.235 → y=0.290），保证 armrest post 有真接触 + 关节原点落在硬件上。
