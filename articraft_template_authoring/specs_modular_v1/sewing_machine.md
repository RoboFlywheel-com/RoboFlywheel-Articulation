# Sewing machine Spec (modular v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `sewing_machine` |
| template path | `agent/templates/sewing_machine.py` |
| test path (optional) | `tests/agent/test_sewing_machine_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：一个接地的 **机身形态 (base + C-head)** 作为 root，携带一个 **旋转驱动系统**（手轮 + 可选踏板/曲柄/电机）与 **机头控制**（针杆恒定 + 可选拨盘/挑线杆），部分候选之间通过档位内 gating（molded vs cast 两大骨架族）约束合法组合。treadle 形态额外带抽屉 multiplicity。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this subcategory (2 origin parents + 6 verified fork variants) |
| source_index_policy | only adopted module sources are indexed below; every candidate cites a real `model.py:Lx-Ly` |

读取的 8 个样本（全部采纳为 module 来源）：
- `rec_an-antique-cast-iron-treadle-sewing-machine-tabl_...a491cf01` (parent A, treadle cabinet)
- `rec_a-white-compact-household-sewing-machine-brother_...396304d9` (parent B, compact molded)
- `rec_sewing_machine_var_base_freearm` (fork of B, free-arm bed + tray)
- `rec_sewing_machine_var_mechanism_handcrank` (fork of B, hand crank)
- `rec_sewing_machine_var_mechanism_takeup` (fork of B, take-up lever)
- `rec_sewing_machine_var_skeleton_industrial` (fork of A, K-frame power table + motor/belt)
- `rec_sewing_machine_var_n2` (fork of A, 2 drawers)
- `rec_sewing_machine_var_n6` (fork of A, 6 drawers)

## 核心身份

Sewing machine：一台在织物上形成线迹的机器。核心 = 一个 C 形机头（bed/pillar/arm/nose）在 stitch/needle plate 上方携带一根往复的 needle bar，由一个旋转 balance handwheel 驱动（可能再由 foot-treadle band wheel、hand crank 或 underslung motor+belt 供给动力），配合 thread tension / take-up / presser foot 等控制。机身可以是紧凑的 benchtop molded 塑料机身、cantilever free-arm、antique treadle cabinet+stand，或 industrial K-leg power table。

不该混入：serger/overlocker（多线锥 + loopers，无单一 lockstitch 机头）、多针刺绣机、纯桌子/柜子（无机头）、纯手工具（无机头的曲柄/轮子）。

## 槽位 + 候选模块表

三个可替换结构层 + 一根抽屉 multiplicity 轴。两大骨架族（**molded** = 塑料紧凑机身；**cast** = 铸铁/工业机头 + 桌台），部分候选按族 gating（详见 §9 compatibility matrix）。

### Slot A：machine_form（① 骨架 + ③ 主体形态家族 / Primary Form Family）
接地 root。**所有非活动刚性结构（base + head，cast 时还含 stand/table/frame/motor housing）融合进一个接地 `chassis` part**，只有真正会动的机构（needle_bar/handwheel/dials/band_wheel/treadle/drawers/pulley）才作为 jointed child。这消除了「结构 part 用绝对世界坐标 + FIXED 关节挂接 → 子 link 原点偏离几何 ~0.75m（origin-far + isolated-parts）」的病症：融合后所有绝对坐标都在同一 identity 帧里，一次成立。needle_bar（PRISMATIC 核心机构）+（molded 时）presser_foot（PRISMATIC）挂到 chassis。承载主形态多样性。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| `compact_bench` | forked_anchor | rec_...396304d9 (parent B) | L75-L213, L339-L398 | eligible if compatible | `chassis` 融合 平坦 molded 盒(bed) + molded C body(pillar∪arm∪head cadquery union，pillar 底伸入 bed 顶共享几何)；needle_bar/presser_foot PRISMATIC 挂 chassis。**form_subtype: Volumetric Envelope Form**（molded 一体化包络机身） |
| `free_arm` | forked_anchor | rec_sewing_machine_var_base_freearm | L92-L104, L168-L280, L406-L465 | eligible if compatible | `chassis` 融合 窄圆 cantilever free-arm sleeve + 同 molded body；`accessory_tray`(PRISMATIC 前滑脱，右缘避开 pillar 左面)；needle_bar/presser 挂 chassis。**form_subtype: Volumetric Envelope Form**（悬臂细筒包络） |
| `treadle_table` | forked_anchor | rec_...a491cf01 (parent A) | L83-L334, L368-L396, L506-L565 | eligible if compatible | `chassis` 融合 spline tube 铸铁腿架 + oak 桌+两侧 cabinet + 铸铁头(bed/pillar/arm/nose/faceplate/stitch_plate)，经 cabinet 壁桥接接地；needle_bar PRISMATIC；drawers multiplicity。**form_subtype: Planar Boundary Form**（框架 + 板箱轮廓） |
| `industrial_table` | forked_anchor | rec_sewing_machine_var_skeleton_industrial | L96-L340 | eligible if compatible | `chassis` 融合 方管 K 腿 + laminate 台面(带 bed 挖孔) + 工业平板 bed+铸铁头 + underslung motor housing(经 hanger 桥接台面下)；needle_bar PRISMATIC。**form_subtype: Planar Boundary Form**（钢管框架 + 平台面） |

### Slot B：drive_mechanism（② 关节/机构）
旋转驱动系统。每个候选自建其 balance handwheel（molded=KnobGeometry 侧手轮；cast=WheelGeometry 辐条平衡轮）+ 额外动力输入。结构上 4 个候选各不同。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `electric_handwheel` | forked_anchor | rec_...396304d9 (parent B) | L215-L246 | eligible if compatible (molded) | 仅侧 handwheel（KnobGeometry cap + shaft）CONTINUOUS +X。无外部动力件（内部电机驱动语义） |
| `hand_crank` | forked_anchor | rec_sewing_machine_var_mechanism_handcrank | L219-L310 | eligible if compatible (molded) | handwheel + `crank_arm`(FIXED 到轮面) + `crank_grip`(CONTINUOUS 在 crank pin 上自由转) |
| `foot_treadle` | forked_anchor | rec_...a491cf01 (parent A) | L336-L365, L398-L503 | eligible if compatible (treadle_table) | balance handwheel(辐条) + `band_wheel`(CONTINUOUS +X，带 crank_arm/crank_pin) + `treadle_pedal`(REVOLUTE +X，lattice + pitman rod + pitman eye 环绕 crank pin) |
| `underslung_motor` | forked_anchor | rec_sewing_machine_var_skeleton_industrial | L280-L461 | eligible if compatible (industrial_table) | balance handwheel + motor housing(融入 chassis) + `motor_pulley`(CONTINUOUS +X 挂 chassis) + `v_belt`(FIXED via `mount_fixed` 到 chassis，spline loop 缠绕 pulley↔handwheel) |

### Slot C：head_controls（② 关节/机构）
机头正面控制。molded 机身控制丰富，cast 机身控制稀疏（类别忠实）。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `domestic_full` | forked_anchor | rec_...396304d9 (parent B) | L248-L337 | eligible if compatible (molded) | `stitch_dial`(REVOLUTE) + `reverse_lever`(PRISMATIC 下压) + `tension_dial`(REVOLUTE) |
| `domestic_takeup` | forked_anchor | rec_sewing_machine_var_mechanism_takeup | L248-L387 | eligible if compatible (molded) | `stitch_dial`(REVOLUTE) + `tension_dial`(REVOLUTE) + `take_up_lever`(REVOLUTE 摆动，thread-eye 在前面 slot 里扫动) |
| `bare_mechanical` | forked_anchor | rec_...a491cf01 / var_skeleton_industrial | A:L260-L327 / ind:L219-L271 | eligible if compatible (cast) | 无额外可动前控件（铸铁/工业机头的 tension_knob / presser_bar / presser_foot 已作为 head visual 在 Slot A 内建）。等价 `none` 候选（precedent: turntable Slot D `none`） |

硬约束满足：Slot A 4 候选、Slot B 4 候选、Slot C 3 候选，全部 forked_anchor + `model.py:Lx-Ly`。候选间为真实结构差异（part/joint 数与形态原型不同），非仅尺寸/涂装。

## 槽位图（slot graph）

pattern: `mixed`

```text
[Slot A machine_form]  (单一接地 `chassis`：融合 base+head(+stand/table/frame/motor) ；needle_bar[PRISMATIC] + (molded)presser_foot[PRISMATIC] 挂 chassis)
  ├── drive parent = `chassis` @ molded:(0.200,0,0.2565) | cast:(HANDWHEEL_X,0,ARM_Z)
  │      └── handwheel_spin CONTINUOUS axis +X --> [Slot B drive_mechanism]
  │             (+ hand_crank: crank_arm FIXED(mount_fixed) on handwheel -> crank_grip CONTINUOUS +X)
  │             (+ foot_treadle: band_wheel CONTINUOUS +X on chassis; treadle_pedal REVOLUTE +X on chassis; pitman eye on crank pin)
  │             (+ underslung_motor: motor housing 融入 chassis -> motor_pulley CONTINUOUS +X on chassis -> v_belt FIXED(mount_fixed) to chassis)
  └── controls parent = `chassis` (molded only) --> [Slot C head_controls]
         (dials REVOLUTE about -Y bore axis; reverse_lever PRISMATIC down; take_up_lever REVOLUTE +X)

[Slot A treadle_table] --[table_to_<drawer_i> PRISMATIC axis -Y, parent=chassis]--> drawer_0..drawer_{N-1}  (multiplicity)
```

接口点位：
- 刚性结构（bed/body、stand/table/head/frame/motor）**融合进单一接地 `chassis`**，无结构间 FIXED 关节；chassis 内各件靠真实接触（pillar 底伸入 bed、cabinet 壁桥接 stand↔table、motor hanger 桥接台面）连成一体。
- handwheel/needle/dials 的 shaft 是 captured pin-in-bore（穿套语义）→ 关节 **omit `mating=`**（Rule 2 grandfather 豁免），用 element-scoped `allow_overlap` 声明 shaft↔bore 捕获。
- band_wheel/motor_pulley 轴捕获于 bearing boss / 电机轴 → 同上 captured。
- pitman eye 环绕 crank pin（torus 套 cylinder）→ element-scoped allow_overlap（coupled treadle 机构，独立 QC 相位互穿）。
- v_belt 缠绕 handwheel/pulley rim → element-scoped allow_overlap（belt wrap）。
- drawers 在 cabinet 空腔内滑动（drawer 比空腔窄，无壁穿模）；PRISMATIC -Y。

## 每槽位 Module Emits / Interfaces

### Slot A / machine_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | molded: `chassis`(root=bed+body 融合),`needle_bar`,`presser_foot`,(free_arm:+`accessory_tray`)；cast: `chassis`(root=stand/table/head 或 frame/table/head/motor 融合),`needle_bar`,(treadle:+`drawer_i`) | B/freearm/A/industrial |
| internal joints | **无结构间 FIXED**（bed/body/stand/table/head/frame/motor 全融进 chassis）；`needle_stroke`(molded)/`head_to_needle_bar`(cast) PRISMATIC parent=chassis；`presser_lift` PRISMATIC(molded)；`tray_slide` PRISMATIC(free_arm)；`table_to_<drawer_i>` PRISMATIC(treadle) parent=chassis | 各源 |
| upstream interface | root（接地 chassis，无 upstream） | — |
| downstream interface | drive parent face（molded body pillar 侧面 / cast head arm 轴心）；controls parent（molded body 前面 bore） | 各源 |

### Slot B / drive_mechanism
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handwheel`(全部)；hand_crank:+`crank_arm`,`crank_grip`；foot_treadle:+`band_wheel`,`treadle_pedal`；underslung_motor:+`motor_pulley`,`v_belt`(motor housing 融入 chassis) | 各源 |
| internal joints | `handwheel_spin` CONTINUOUS +X；`crank_arm_mount` FIXED(via `mount_fixed`) + `crank_grip_spin` CONTINUOUS；`stand_to_band_wheel` CONTINUOUS + `stand_to_treadle` REVOLUTE；`motor_to_pulley` CONTINUOUS + `chassis_to_belt` FIXED(via `mount_fixed`)。仅 crank_arm 与 v_belt 两处保留真实 FIXED | 各源 |
| upstream interface | 全部挂到接地 `chassis`（handwheel/band_wheel/treadle/pulley）；crank_arm 挂到 handwheel；v_belt 经 `mount_fixed` 挂到 chassis（pulley 顶 belt 控制点，落在 motor 壳 ~10mm 内） | 各源 |

### Slot C / head_controls
| emits | 描述 | 来源 |
|---|---|---|
| parts | domestic_full: `stitch_dial`,`reverse_lever`,`tension_dial`；domestic_takeup: `stitch_dial`,`tension_dial`,`take_up_lever`；bare_mechanical: 无 | B/takeup/A |
| internal joints | `stitch_select` REVOLUTE、`tension_adjust` REVOLUTE、`reverse_press` PRISMATIC、`takeup_oscillate` REVOLUTE | B/takeup |
| upstream interface | 全部挂到 molded `body`（前面 bore） | B/takeup |

活动件均有 articulation 语义；不动细节（decal/faceplate/spool pin/take-up slot/art panel）写成宿主 part visual，不作独立 part。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `machine_form` | enum | compact_bench / free_arm / treadle_table / industrial_table | compact_bench | choice | deterministic procedural sampler | Slot A |
| `drive_mechanism` | enum | electric_handwheel / hand_crank / foot_treadle / underslung_motor | electric_handwheel | conditional | 由 machine_form gating（molded→{electric,hand_crank}; treadle→{foot_treadle}; industrial→{underslung_motor}） | Slot B |
| `head_controls` | enum | domestic_full / domestic_takeup / bare_mechanical | domestic_full | conditional | molded→{full,takeup}; cast→{bare_mechanical} | Slot C |
| `palette_theme` | enum | molded: white / mint / cream；cast/industrial: 固定 | white | choice | 仅换 molded 机身/装饰颜色 | ⑥ record_only |
| `drawer_count` | int (multiplicity) | [2,6]，权重偏小 N | 3 | conditional | 仅 treadle_table；drawer 高度 = clamp(interior/ceil(N/2)-gap) | §8 |
| `molded_bed_depth_scale` | float | [0.92, 1.12] | 1.0 | independent | 缩放 molded bed/foot 的 Y 跨度；不动 needle/plate/presser 相对几何 | B |
| `needle_travel_scale` | float | [0.85, 1.18] | 1.0 | independent | 缩放 needle prismatic 行程（仅 motion_limits，无几何重建） | 各源 |
| `table_span_scale` | float | [0.94, 1.08] | 1.0 | conditional | 仅 cast：缩放 oak/laminate 台面宽度 + cabinet/腿间距（box 参数化）；不动机头/驱动几何 | A/industrial |
| `handwheel_effort` 等 | float | — | 源值 | independent | 关节 effort/velocity 非几何标称，保持源值 | 各源 |
| (—) | constraint | — | — | inequality | drawer 竖排总高 ≤ cabinet interior：`ceil(N/2)·drawer_h ≤ CAB_interior`，违反时按比例回缩 drawer_h | 接口 |
| (—) | constraint | — | — | inequality | needle 全行程 tip 保持在 stitch plate 上方（molded solid plate；cast plate hole）：clamp lower travel | Rule 5 |

连续尺寸采样契约：先采 independent（molded_bed_depth_scale / needle_travel_scale），再按 conditional 解析 table_span_scale（依 form 族）与 drawer_h（依 N），最后 inequality 回缩 drawer_h。所有约束在 `resolve_config` 求解。

## 7.5 编译预算 / compile budget
自报 **每-seed ≈ 20-40s**（molded body / free-arm 用 cadquery union+fillet；treadle 用 spline tube legs + extrude-with-holes lattice；industrial 用 extrude-with-holes 台面 + spline belt）。依据：库内重布尔/放样类 30-60s，本类每 seed 只构建**一个** form 的重几何，落在中段。分档 tessellation：小特征（foot/knob/pin）默认段数，hero 面（wheel/body/lattice）沿用源精度；N 个 drawer 复用同一 box 生成 helper。sweep 用 `--compile-timeout 120`（≈3×预算，watchdog）。

## Multiplicity / Copy Logic

- **1 根 multiplicity 轴：cabinet drawers（`drawer_count`）**，仅 `treadle_table` form。
- `count_param`: `drawer_count`；`N_range`: 产品域 [2,6]（测试偏小 N，尾部稀有）。source N 样本：2 (var_n2)、3 (parent A)、6 (var_n6)。
- sampling domain：加权采样（N=2/3 高频，N=6 稀有）。
- copied object: 一个 dovetailed drawer = front_panel + medallion + knob_stem + knob + bottom + side_wall_0/1 + back_wall。
- naming: 索引 `drawer_0..drawer_{N-1}`（loop-emitted，shared helper `_add_drawer`）。
- placement: 分配到左右两 cabinet，每侧 `ceil(N/2)` 个竖直堆叠，uniform 间距；drawer 高度随 N 回缩以适配 cabinet interior。
- joint policy: 每个 drawer 独立 `table_to_drawer_i` PRISMATIC，axis -Y（前拉出），无 body-family / joint-type 改变。
- 其它 form 无 multiplicity。molded 控件、feet、spool pin 等是 module-local 固定结构 / baked visual，不是模板级复制轴。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source / 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | 4 种 part-joint 图（刚性结构均融入接地 chassis，只列会动机构）：compact_bench(chassis+needle+presser+handwheel+dials)、free_arm(+tray slide)、treadle_table(chassis+needle+balance wheel+band wheel+treadle+drawers)、industrial_table(chassis+needle+wheel+pulley+belt)。全部 forked_anchor |
| └ multiplicity | 同构件 ×N | 有 | drawers N∈[2,6]，见 §8（N=2/3/6 source-backed） |
| ② 关节类型 | 图不变换 type/轴 | 有 | CONTINUOUS(handwheel/band_wheel/crank_grip/motor_pulley, +X)；REVOLUTE(treadle +X, stitch_dial/tension_dial 绕 -Y, take_up_lever +X)；PRISMATIC(needle_stroke ±Z, presser_lift +Z, reverse_press -Z, tray_slide -Y, drawers -Y)；FIXED(仅 crank_arm、v_belt 两处，均 `mount_fixed` 单点声明；其余刚性结构融进 chassis 无 FIXED)。全部 source-backed；每种在 sweep 出现 |
| ③ 主体形态家族 / Primary Form Family | 换核心 part 可识别几何原型 | 有 | 登记进 `slot_choices` 的 machine_form slot（4 candidate）：Volumetric Envelope Form ×2（molded compact / free-arm cantilever）、Planar Boundary Form ×2（treadle 框架箱体 / industrial 钢管平台）。source-backed anchors |
| ④ 表面装饰 | 叠加表面细节 | 有 | molded: front_art_panel(paisley，cadquery cut 孔随 dial/lever 派生)、takeup_slot、brand 细节；cast: arm_decal/bed_decal(gold)、faceplate、medallion。record_only + host-conformal（宿主 part visual，随 ③ 变） |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | molded_bed_depth_scale[0.92,1.12]、table_span_scale[0.94,1.08]、needle_travel_scale[0.85,1.18]；关节运动包络见下 motion_test_plan |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类：painted-plastic(molded white/mint/cream)、cast-iron black+nickel+oak wood、steel/enamel industrial。配色 ≥3 组；材质大类 ≥ ceil(0.5×3)=2（plastic/metal/wood 均出现） |

**motion_test_plan（⑤ 每个非-continuous 关节运动包络）**：
- `needle_stroke`/`head_to_needle_bar` PRISMATIC，Z 轴，[rest, 全行程 tip 仍在 plate 上方]；targeted pose：针下降不击穿 plate。
- `presser_lift` PRISMATIC，+Z，[0, 抬起]；targeted：抬离 plate。
- `reverse_press` PRISMATIC，-Z，[0, 下压 0.008]；targeted：向下位移。
- `tray_slide` PRISMATIC，-Y，[0, 前滑脱]；targeted：向 -Y 移出。
- `stitch_select`/`tension_adjust` REVOLUTE 绕 -Y；`take_up_lever` REVOLUTE +X 摆动；`treadle_pedal` REVOLUTE +X [−0.22,0.22] targeted：脚踏前缘下沉且离地。
- drawers PRISMATIC -Y [0,travel] targeted：前拉出并保持嵌入。
- CONTINUOUS（handwheel/band_wheel/crank_grip/motor_pulley）：整圈不穿模；crank_pin 绕轴 orbit、crank_grip 绕 pin 自转 targeted。
- 全模板跑 `fail_if_parts_overlap_in_sampled_poses`（captured shaft / pitman-eye-on-pin / belt-wrap / drawer-in-cabinet 用 element-scoped allow_overlap，理由具体）。

## 采样与覆盖审计

合法 slot-choice 组合（含 multiplicity）：
- compact_bench × {electric, hand_crank} × {domestic_full, domestic_takeup} = 4
- free_arm × {electric, hand_crank} × {domestic_full, domestic_takeup} = 4
- treadle_table × {foot_treadle} × {bare_mechanical} × drawer_N{2,3,6…} ≈ 3+
- industrial_table × {underslung_motor} × {bare_mechanical} = 1
**≈ 12 个离散拓扑 tuple + 连续 proportion + drawer N 权重。**

理由（拓扑 target < 300 说明）：本小类真实产品空间受 **molded vs cast 骨架族强耦合** 约束——molded 塑料机身只配内部电机/手摇曲柄与家用拨盘控件；cast 铸铁机头只配踏板/工业电机与稀疏控件。跨族混装（塑料机身配踏板柜、铸铁头配家用拨盘）非类别忠实，故 gating 排除。12 个忠实拓扑 tuple + drawer multiplicity + 连续尺度即真实组合空间；该指标 report-only，不作 gate。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对所有普通 seed（**含 seed 0**，不特殊）用 `random.Random(seed)` deterministic 采样：先均匀选 machine_form，再按族 gating 选 drive/controls，再采连续 scale 与 drawer_N。无 curated/modulo 主表。

Procedural Sampling / Sweep Plan：sampler 先选 form，用 form 决定的 compatible 集合选 drive 与 controls（compatibility matrix 在 `resolve_config` 内解析，非法组合不会到 builder）。drawer_N 仅 treadle 采样并 clamp。首验收跑 `sweep-pipeline sewing_machine`（0-15 fast → 16-35 final → corner），机械通过后 viewer 目检 0-2。

Topology target：1000-seed slot tuple 覆盖用于成熟度观察，本类真实组合 ≈12（见上），低于 300 已说明族耦合原因。

Controlled local parameterization：molded_bed_depth_scale、table_span_scale、needle_travel_scale（见 §7）；均在 `resolve_config` clamp/派生，受接口、needle/plate 对齐、drawer 适配、belt wrap 约束，不破坏 FIXED 接口、captured-pin 语义或 category identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | form 均匀 → 族 gating drive/controls → 连续 scale → drawer_N 加权 | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | molded↔{electric,hand_crank,domestic_full,domestic_takeup}; cast↔{foot_treadle|underslung,bare_mechanical}; 互斥跨族组合被 gating 排除 | 无跨族错配、悬空、穿模、轴/range、closed pose 失败 |
| controlled local variation | molded_bed_depth_scale/table_span_scale/needle_travel_scale + clamp | 比例变化不破接口/clearance/joint origin/identity |
| regression overrides | none | 仅在 sweep 发现稳定回归时按 seed 加，说明理由 |
| random sweep | seeds 0-35 initial pass；0-999 maturity audit | contract failures; axis_realization; viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| machine_form | 4 | yes | yes | ③ Primary Form Family slot（2 Volumetric + 2 Planar） |
| drive_mechanism | 4 | yes | yes | 族 gating |
| head_controls | 3 | yes | yes | 含 bare_mechanical(none) |

## Validator
- slot_choices_for_seed 返回已实现 module 名（machine_form/drive_mechanism/head_controls[+drawer_count 档]）。
- config_from_seed 对所有普通 seed（含 0）用 deterministic procedural sampling。
- compatibility gating 阻止跨族非法组合（在 resolve_config 解析）。
- 关键 InterfaceSpec/接触面：刚性结构融进接地 chassis（无结构间 FIXED，靠真实接触连通）；handwheel/needle/dial shaft captured 于 bore；crank_arm 与 v_belt 两处真实 FIXED 用 `mount_fixed` 单点声明（joint origin 落在双方真实几何 ≤15mm）；pitman eye on crank pin；belt wrap；drawer in cabinet。
- 关键关节 type/axis/range：handwheel CONTINUOUS +X；needle PRISMATIC 竖直；treadle REVOLUTE +X；drawers PRISMATIC -Y。
- copied drawers 遵循 naming/placement/joint policy。
- 连续 scale 在 resolve_config clamp/派生，不破接口/clearance/joint origin/multiplicity。
- run_tests 含 `fail_if_parts_overlap_in_sampled_poses` + 每机构 targeted `ctx.pose`（Rule 5）。

## Reject cases
- 无 needle bar 往复 或 无旋转 handwheel。
- 机头缺 C 形（无 pillar+arm 悬臂 over stitch plate）。
- 跨族错配（molded 机身 + 踏板柜；铸铁头 + 家用拨盘）。
- 悬空控件/装饰作为独立 FIXED 3mm anchor part（违 Rule 1）。
- needle 全行程击穿 needle plate / 沉入 bed。
- drawers 手写而非 loop-emitted，或数量不随 drawer_count。
- 漂移成 serger（多线锥 + loopers）或多针刺绣。

## 与相邻类别的边界
- serger / overlocker：多线锥 rack + loopers，无单一 lockstitch 机头——gated，不 emit。
- 多针刺绣机：多针杆阵列，邻类，out of scope。
- 纯桌/柜：无机头则不是 sewing machine（treadle/industrial 必须带铸铁头 + needle + handwheel）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；等待人工审核。族耦合 gating + drawer multiplicity 为主多样性来源 |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | compact_bench + electric_handwheel + domestic_full | rec_...396304d9 | L75-L398 | molded 机身、侧手轮、家用拨盘 |
| S2 | A/B | free_arm + electric/hand_crank | rec_sewing_machine_var_base_freearm | L92-L465 | free-arm bed + accessory tray |
| S3 | B | hand_crank | rec_sewing_machine_var_mechanism_handcrank | L219-L310 | crank arm + free-spinning grip |
| S4 | C | domestic_takeup | rec_sewing_machine_var_mechanism_takeup | L130-L387 | take-up lever REVOLUTE |
| S5 | A/B/C | treadle_table + foot_treadle + bare | rec_...a491cf01 | L83-L565 | 铸铁踏板柜 + 平衡轮 + 踏板 + 抽屉 |
| S6 | A/B | industrial_table + underslung_motor | rec_sewing_machine_var_skeleton_industrial | L96-L461 | K 腿电动台 + 电机/皮带 |
| S7 | mult | drawer N=2 / N=6 | var_n2 / var_n6 | A:L506-L565 | drawer multiplicity 档 |
</content>
</invoke>
