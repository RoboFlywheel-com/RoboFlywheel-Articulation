# pictureX_0611_bevel_gear_pair_with_perpendicular_shafts — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `pictureX_0611_bevel_gear_pair_with_perpendicular_shafts` |
| template path | `agent/templates/pictureX_0611_bevel_gear_pair_with_perpendicular_shafts.py` |
| test path (optional) | (skipped while authoring; sweep is authoritative) |
| stage | `IMPLEMENTED` |
| status | `complete_visual_confirmed_2026-07-13` |
| variant_gate | `confirmed_by_user_2026-07-12` |
| __modular__ | `True` |
| pattern | `parallel_children` (support_frame root → two CONTINUOUS shaft joints → horizontal_drive + vertical_drive, mesh-coupled by a Mimic; multiplicity on the per-gear tooth count) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 14 (1 usable origin + 13 normal forked variants; second origin blocked/excluded) |
| read_count | 14 |
| read_scope | all 5-star samples in this subcategory |
| source_index_policy | only adopted module sources are indexed below |

Reading summary: every source is a single-topology assembly — a machined root
`support_frame` carrying two child drives (`horizontal_drive` on axis X,
`vertical_drive` on axis Z) via **two CONTINUOUS joints** whose origins coincide
on the shaft-crossing line, the vertical joint a **Mimic** of the horizontal at
`multiplier = -gear_teeth/pinion_teeth`. Both bevel gears come from ONE
`BevelGearPair(...).assemble()` split by `mesh_components_from_cadquery` into
`gear_meshes[0]` (gear→horizontal) and `gear_meshes[1]` (pinion→vertical); both
placed with the same `xyz=(-0.0187605,0,0), rpy=(0,π/2,0)` transform so the pitch
cones mesh at the apex. The 13 variants each perturb exactly one structural axis
(tooth form, ratio, teeth grade, shaft-end interface, housing, hub boss),
confirming those are the real diversity axes. Origin `001` compiles at 5★; origin
`002` is blocked (>2 min timeout) and only used as visual evidence.

## 核心身份
两个圆锥（斜齿）bevel 齿轮在 **90° 轴角**啮合，各自装在自己的旋转轴上，两轴旋转由
齿轮啮合物理耦合。模板保持：两 bevel 齿轮 90° 啮合；每根轴一个 **CONTINUOUS** 旋转
关节（≥2 continuous joints）；啮合耦合（vertical Mimic horizontal，
`multiplier=-gear_teeth/pinion_teeth`）；牙齿由 `BevelGearPair`/`BevelGear` 几何 loop 发射；
一个同时承载两轴的 support。不该混入：spur-gear pair（平行轴）、worm-and-wheel、
planetary/epicyclic、differential（第三共线轴）。

## 槽位 + 候选模块表

### Slot A：tooth_form（③ Primary Form Family + ① for hypoid）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| straight | origin_anchor | 001.png parent (helix_angle default 0) | parent L144-163 | eligible | `BevelGearPair(helix_angle=0)`; straight radial teeth; form_subtype=Macro Surface Construction |
| spiral | forked_anchor | var_spiral_bevel | L151 `helix_angle=35.0` | eligible | 35° spiral tooth flanks (curved lengthwise); Macro Surface Construction |
| zerol | forked_anchor | var_zerol_bevel | `helix_angle=10.0` | eligible | ~10° gently curved (Zerol) teeth; Macro Surface Construction |
| hypoid | forked_anchor | var_hypoid_offset | L27 `HYPOID_OFFSET_MM=10`, L60/73/138/242 | eligible | lateral Y offset between the two shaft axes (non-intersecting 90°); ① skeleton offset |

### Slot B：ratio（① skeleton — cone-pair size + mesh ratio）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| miter | forked_anchor | var_miter_1to1 | `gear_teeth==pinion_teeth`, `mimic=-1.0` | eligible | equal teeth/cones, 1:1; mimic −1.0 |
| mild | origin_anchor | 001 parent | L144-152 (20/16), L245 `-20/16` | eligible | ~1.25 reduction; unequal crown/pinion cones |
| high | forked_anchor | var_reduction_high | 33/11, `mimic=-3.0` | eligible | ~3:1 large crown + small pinion; mimic −3.0 |

### Slot C：teeth_grade（multiplicity N — per-gear tooth count; module rescaled to hold pitch dia）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| coarse | forked_anchor | var_teeth_coarse | `module=3.5, 12/10` | eligible | low tooth count, large module (~35mm pitch dia) |
| mid | origin_anchor | 001 parent | `module=2.1, 20/16` | eligible | mid count (~34mm pitch dia) |
| fine | forked_anchor | var_teeth_fine | `module=1.3, 32/26` | eligible | high count, small module (~34mm pitch dia) |

### Slot D：shaft_form（① shaft-to-gear interface）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| keyed | origin_anchor | 001 parent | L190-195 / L219-224 (Box keys) | eligible | rectangular key on each shaft |
| bare | forked_anchor | var_shaft_bare | keys removed | eligible | plain shafts, no key/hub |
| hub_setscrew | forked_anchor | var_shaft_hub_setscrew | L190-208 (collar+boss+hex) | eligible | hub collar + radial setscrew boss + hex socket mark |
| flanged | forked_anchor | var_shaft_flanged | `_make_flange_disc` L89-127, L228-237/263-272 | eligible | flange disc + bolt-circle ring (secondary multiplicity, N∈{4,6,8}) |

### Slot E：housing（① support structure envelope）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| open_cage | origin_anchor | 001 parent | `_make_support_frame` L29-76 | eligible | windowed machined box, integral bearing bosses |
| bracketed | forked_anchor | var_housing_bracketed | rebuilt `_make_support_frame` | eligible | open pillow-block brackets / base plate |
| gearbox | forked_anchor | var_housing_gearbox | closed housing L30-125 | eligible | enclosed case + cavity + cast ribs + cover bolts (gears enclosed) |

### Slot F：hub_boss（③ gear body construction）
| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| thin_spacer | origin_anchor | 001 parent | L181-189 / L213-218 | eligible | thin spacer cylinder behind each gear |
| extended_hub | forked_anchor | var_hub_boss | hub-boss meshes | eligible | enlarged/lengthened hub cylinder behind each gear |

Every slot has ≥2 source-backed candidates; tooth_form/ratio/shaft_form/housing
have ≥3. `palette_style` (⑥, below) is a parameter, not a slot.

## 槽位图（slot graph）

pattern: parallel_children

```
support_frame (root, grounded; housing = Slot E)
  ├─[CONTINUOUS axis X @ (0,0,SHAFT_CENTER_Z)]──> horizontal_drive  (gear_meshes[0])
  └─[CONTINUOUS axis Z @ (0,0,SHAFT_CENTER_Z)+hypoidY]──> vertical_drive (gear_meshes[1], Mimic of horizontal)
```

- 两个 drive 都是 root `support_frame` 的并列子件（parallel-children），不串链。
- 跨 slot 接口：shaft-in-bearing 捕获（shaft 圆柱穿过 bearing race 内孔，
  symmetry-centerline pivot）；gear-to-gear 啮合接触在 pitch cone apex（tested，
  非 joint）。
- 关节：两个 CONTINUOUS 旋转关节；vertical 是 horizontal 的 Mimic，
  multiplier = −gear_teeth/pinion_teeth，逐 seed 由 Slot B/C 决定。
- Slot A(tooth_form)/B(ratio)/C(teeth_grade)/D(shaft_form)/F(hub_boss) 修改 drive
  的 visual 与齿轮参数；Slot E(housing) 修改 root 几何；均不新增 part/joint。

## 每槽位 Module Emits / Interfaces

### root / housing (Slot E)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `support_frame` | parent L105 |
| visuals | `frame_body` (cadquery mesh) + `side_bearing_0/1` + `top_bearing` (annulus meshes) | parent L106-140 |
| internal joints | none | — |
| downstream interface | two shaft pivots at `(0,0,SHAFT_CENTER_Z)` (X and Z), each a bearing bore | parent L226-246 |

### horizontal_drive (Slots A/B/C/D/F)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `horizontal_drive` | parent L165 |
| visuals | `horizontal_shaft` (Cylinder) + `horizontal_bevel_gear` (gear_meshes[0]) + hub (`horizontal_hub`) + shaft-end feature | parent L166-195 |
| joint | `support_to_horizontal` CONTINUOUS axis (1,0,0) @ (0,0,SHAFT_CENTER_Z) | parent L226-235 |

### vertical_drive (Slots A/B/C/D/F)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `vertical_drive` | parent L197 |
| visuals | `vertical_shaft` (Cylinder) + `vertical_bevel_gear` (gear_meshes[1]) + hub (`vertical_hub`) + shaft-end feature | parent L198-224 |
| joint | `support_to_vertical` CONTINUOUS axis (0,0,1), Mimic(horizontal, −g/p) | parent L236-246 |

活动件 = 两根 drive（continuous）。所有不动细节（key/setscrew boss/hex/flange bolts/
ribs/bearings）都是宿主 part 的 visual，不是独立 FIXED part。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| tooth_form | enum | straight/spiral/zerol/hypoid | straight | choice | procedural sampler | Slot A |
| ratio | enum | miter/mild/high | mild | choice | procedural sampler | Slot B |
| teeth_grade | enum | coarse/mid/fine | mid | choice (weighted) | procedural sampler | Slot C |
| shaft_form | enum | keyed/bare/hub_setscrew/flanged | keyed | choice | procedural sampler | Slot D |
| housing | enum | open_cage/bracketed/gearbox | open_cage | choice | procedural sampler | Slot E |
| hub_boss | enum | thin_spacer/extended_hub | thin_spacer | choice | procedural sampler | Slot F |
| palette_style | enum | 5 colorways | bright_steel | choice | procedural sampler | ⑥ |
| n_flange_bolt | int | {4,6,8} | 4 | conditional | 仅 shaft_form==flanged 生效 | var_shaft_flanged |
| pinion_teeth | int | derived | — | equation | `= _PINION_BASE[teeth_grade]`（high 用小 pinion 表） | Slot B×C |
| gear_teeth | int | derived | — | equation | `= round(pinion_teeth * ratio_mult[ratio])`，clamp≥pinion(高 ratio)/==pinion(miter) | Slot B×C |
| module | float | derived | — | equation | `= _MODULE[teeth_grade]`（保持 pitch dia ~34mm） | Slot C |
| helix_angle | float | derived | — | equation | `= {straight:0, spiral:35, zerol:10, hypoid:0}[tooth_form]` | Slot A |
| hypoid_offset | float | derived | 0 | equation | `= 0.010 if tooth_form==hypoid else 0` | var_hypoid_offset |
| mimic_mult | float | derived | −g/p | equation | `= -gear_teeth/pinion_teeth`（恒等） | parent L245 |
| face_width | float | derived | ~0.010 | inequality | `< 0.35·(module/2·√(g²+p²))`（BevelGear gs_r assert 安全带） | gears.py L972 |
| shaft_len_scale | float | [0.9,1.12] | 1.0 | independent | clamp | ⑤ |
| gear_scale (module) | float | [0.92,1.08] | 1.0 | independent | module 微缩放后 clamp；不破坏 pitch/mesh | ⑤ |

## 7.5 编译预算 / compile budget
自报预算：**~22s/seed**（spiral/hypoid 峰值 ~24s）。依据：实测单个
`BevelGearPair(...).assemble()` 的 OCC 样条构造 ~14-17s（straight）/~16-19s（helix≠0），
是本类别的**内在**成本（与 5★ parent 记录相同的一次齿轮对构造），且**几乎与 tooth
count 无关**（12T 与 32T 同为 ~13-15s），tessellation 仅 ~0.3s（tol 0.35 / ang 0.2）。
frame cadquery mesh ~0.3s。每 seed 仅构造 **一个** `BevelGearPair`，两 mesh 组件复用；
不随 N loop 增长。`--compile-timeout 120` 为 watchdog（~5× 预算），不是质量门。
Tessellation 分档：gear tol 0.35/ang 0.2，frame tol 0.35/ang 0.12，bearing 默认。
sampled-pose 检查只有 1 个自由关节（vertical 是 mimic，不独立采样）→ 4 poses，
`max_pose_samples=32`。

## Multiplicity / Copy Logic
主轴 = **每齿轮 tooth count N**（loop-emitted inside `BevelGear` via `BevelGearPair`）。
- count_param: `gear_teeth` / `pinion_teeth`；N_range: pinion 8..30，gear 10..42（真实
  bevel/miter 库存）；ratio 1:1 .. ~4:1。sampling domain（teeth_grade 加权）：
  coarse(0.30, 小 N 高频) / mid(0.45) / fine(0.25, 大 N 稀有)。
- copied object: 单个 bevel 牙；naming: `BevelGear` 内部 loop（非 per-tooth SDK part），
  count-driven；placement: 各 pitch cone 等角距径向；joint_policy: 牙是旋转齿轮的固定
  特征（无 per-tooth joint）。**mimic multiplier 每个 N 样本恒等 = −gear_teeth/pinion_teeth。**
- 次级 multiplicity: `n_flange_bolt` ∈ {4,6,8}（仅 flanged shaft_form，loop-emitted 螺栓环，
  count_param=n_flange_bolt，default 4）— 暴露 copy logic，但 teeth loop 是主 N 轴。

## 视觉多样性 6 轴考察
| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 固定骨架 = root + 2 continuous drives（恒定 identity，不删）；skeleton 变化来自 hypoid 轴偏移（非相交 90°，var_hypoid_offset）+ ratio 造成的 crown/pinion cone 尺寸差（miter/mild/high, var_miter/var_reduction_high）+ shaft interface（keyed/bare/hub_setscrew/flanged）+ housing envelope（open_cage/bracketed/gearbox）。全部 forked_anchor |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：teeth N（coarse/mid/fine，权重 0.30/0.45/0.25）+ flange bolt {4,6,8} |
| ② 关节类型 | 图不变换 type/轴 | 有（固定 identity，不作 fork） | 两个 CONTINUOUS 轴旋转关节（axis X / axis Z）+ Mimic 啮合耦合；**所有变体保持 ≥2 continuous joints**，绝不降级；不作独立 fork 轴。source-backed（parent L226-246） |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | tooth form: straight / spiral(35°) / zerol(10°) — 换 BevelGear 齿面形态（Macro Surface Construction）；gear body: thin_spacer vs extended_hub（Volumetric Envelope Form）；equal-vs-unequal cone pair（miter vs reduction）。登记进 slot_choices（tooth_form, hub_boss）。source-backed |
| ④ 表面装饰 | 叠加表面细节 | 有 | record_only / world_knowledge_extrapolation：hex socket mark（hub_setscrew）、flange bolt ring、gearbox cast ribs + cover bolts —— 均由宿主 part 表面派生的 host-conformal visual，无专用 module/joint |
| ⑤ 尺寸/行程 | 只连续改尺寸 | 有 | module ~1.3..3.5（保持 pitch dia）、face_width ~10、shaft_len_scale[0.9,1.12]、gear_scale[0.92,1.08]、hub/flange 尺寸；两关节均 **continuous 整圈无限旋转**（无 open/closed 状态），motion_test_plan：跑 sampled collision（4 poses），mesh 全程啮合由 blanket gear-gear allow_overlap 覆盖，无需 qc_samples |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类：metal（全部）；配色 ≥5：bright_steel / blackened / brass_gears / cast_iron / oiled_bronze（gear/frame/shaft/bearing/accent 角色）。source: parent L99-103 + ⑥ record_only 备选 |

## 采样与覆盖审计

总组合数（离散）：tooth_form(4) × ratio(3) × teeth_grade(3) × shaft_form(4) ×
housing(3) × hub_boss(2) × palette(5) = **4320**（未计 flange bolt N 与连续 scale）。
远超 300 成熟度阈值。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 用 `random.Random(seed)`
对每个 slot 独立加权采样（teeth_grade / palette / n_flange_bolt 加权，其余 uniform），
seed 0 不特殊。无 curated/modulo 主表。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 逐 slot rng.choice/choices；teeth→module/gear_teeth 派生 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | miter → gear_teeth==pinion_teeth（mimic −1.0）；high → 小 pinion 表；n_flange_bolt 仅 flanged；hypoid → 关节 Y offset + gear 互穿 allow_overlap；gearbox → 齿轮封闭 → gear/hub vs 壁 allow_overlap | 无悬空/穿模未声明、mesh 啮合、bore 捕获 |
| controlled local variation | shaft_len_scale, gear_scale(module) clamp；face_width 由 gs_r 不等式安全带 | 比例变化不破坏 mesh/bore/joint origin/identity |
| regression overrides | none | — |
| random sweep | 0-15 fast, 0-35 final, + corner | contract failures; axis_realization |

Topology target：1000-seed slot tuple 覆盖用于成熟度观察（report-only）。

## Validator
- `slot_choices_for_seed` 返回已实现 module 名。
- `config_from_seed` 对所有 seed（含 0）用 deterministic procedural sampling。
- compatibility gating 阻止非法组合（miter 齿数相等、n_flange_bolt 仅 flanged、face_width 安全带）。
- 关键几何：两 CONTINUOUS 关节存在、axis X/Z、origin 共线、vertical mimic
  multiplier == −gear_teeth/pinion_teeth；两 bevel gear mesh 在 apex 接触/重叠。
- cross-part scale 依赖（module→gs_r→face_width）在 `resolve_config` 求解。
- 齿由 `BevelGearPair` 几何 loop 发射，绝不降级为 Box/Cylinder。

## Reject cases
- 任一变体 <2 continuous joints，或 vertical 非 mimic → 违反 identity。
- mimic multiplier ≠ −gear_teeth/pinion_teeth（sweep-tuned 常数）。
- 齿轮降级为 Box/Cylinder 占位。
- 轴角非 90°（skew/crossed-helical）→ 越出 “perpendicular shafts” identity（hypoid 仅加横向偏移，仍 90°）。
- 变成 spur pair（平行轴）/ worm-wheel / planetary / differential（第三轴）。
- 未声明的 gear-gear 或 shaft-crossing 穿模导致 baseline overlap fail。
- face_width ≥ gs_r → BevelGear 构造 assert 崩溃。

## 与相邻类别的边界
- 不该混入：spur-gear pair（平行轴，失去 90° 圆锥啮合）。
- 不该混入：worm-and-wheel（单头蜗杆驱动蜗轮，是相邻蜗轮类）。
- 不该混入：planetary/epicyclic（行星架 + 多关节，破坏双轴 bevel identity）。
- 不该混入：differential（第三共线轴，读作差速器子类）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | complete; visual confirmed by user 2026-07-13 |
| reviewer notes | GATE P3: spec complete；每候选有 real model.py:Lx-Ly；无单候选 slot；topology audit + 兼容矩阵在列；§7.5 compile budget ~22s/seed（intrinsic BevelGearPair 构造，同 5★ parent）。Post-gate sweep final pass_rate=1.0 and corner stage clean after single-worker rerun. Preview seeds `0,7,86,343,11` generated workbench-only records; seed 343 replaces timed-out seed 39 while preserving spiral/bare/oiled_bronze coverage. User confirmed visual check on 2026-07-13. |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | root/all | parent | rec_picturex_...__001__... | L29-246 | 骨架 + 两关节 + mimic + 齿轮对 + open_cage + keyed + thin_spacer + straight + mild + mid |
| S1 | A | spiral | var_spiral_bevel | L151 | helix 35 |
| S2 | A | zerol | var_zerol_bevel | helix 10 | Zerol |
| S3 | A | hypoid | var_hypoid_offset | L27,60,73,138,242 | Y offset |
| S4 | B | miter | var_miter_1to1 | teeth eq, mimic −1.0 | 1:1 |
| S5 | B | high | var_reduction_high | 33/11, mimic −3.0 | 高减速 |
| S6 | C | coarse | var_teeth_coarse | module 3.5, 12/10 | 低齿数 |
| S7 | C | fine | var_teeth_fine | module 1.3, 32/26 | 高齿数 |
| S8 | D | bare | var_shaft_bare | keys removed | 光轴 |
| S9 | D | hub_setscrew | var_shaft_hub_setscrew | L190-208 | 套筒+顶丝+六角 |
| S10 | D | flanged | var_shaft_flanged | L89-127 | 法兰盘+螺栓环 |
| S11 | E | bracketed | var_housing_bracketed | rebuilt frame | 支座式 |
| S12 | E | gearbox | var_housing_gearbox | L30-125 | 封闭箱体 |
| S13 | F | extended_hub | var_hub_boss | hub meshes | 加长轮毂 |
