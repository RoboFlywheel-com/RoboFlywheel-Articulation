# Stretcher — Modular Spec (specs_modular_v1)

## 元信息
| 项 | 值 |
|---|---|
| slug | `stretcher` |
| template path | `agent/templates/stretcher.py` |
| test path (optional) | `tests/agent/test_stretcher_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children: deck root + undercarriage/restraint/casters hang off it; multiplicity: N casters) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 15 |
| read_count | 15 |
| read_scope | all 5-star samples in this subcategory (2 origins + 13 forked/probe variants) |
| source_index_policy | only adopted module sources are indexed inline below (`rec:model.py:Lx-Ly`) |

阅读结论：本小类有 **两条基础骨架** —
- **o1** `rec_...stretcher_39031c58` (001.png): 根 `lower_carriage`；`litter_frame` 经 PRISMATIC `height_slide` 升降；`backrest` REVOLUTE；两根 `side_rail` REVOLUTE 折叠护栏；两条 `scissor_arm` REVOLUTE 剪叉；四个 `caster` CONTINUOUS。纯 Box/Cylinder tube-frame（便宜）。
- **o2** `rec_...stretcher_c7b79ba9` (002.png): 根 `deck_frame`；`backrest` REVOLUTE；两根 `side_rail` REVOLUTE；`head_leg`/`foot_leg` REVOLUTE 折叠腿；四个 `caster` CONTINUOUS；IV 杆。含 `_curved_tube`（mesh 放样腿）+ mesh 轮（重）。

变体各自扩一根轴：telescoping_legs（PRISMATIC 腿）、trendelenburg_tilt（整床倾斜 REVOLUTE）、foot_gatch（脚段 REVOLUTE）、scoop_split（分半 PRISMATIC）、pole_canvas（担架杆+折叠撑杆 REVOLUTE，无轮）、basket_litter（Stokes 篮壳蛤壳对折 REVOLUTE）、spine_board（平板 HDPE + 头部固定块 REVOLUTE，无轮无腿）、canvas_deck（张紧帆布面）、strap_harness（约束带替护栏）、casters_two/six（N 轮）、telescoping_handles（伸缩把手 PRISMATIC）、wheeled_basket_probe（篮壳挂折叠腿轮架 FIXED 探针）。

**统一化决策（re-root）**：模板以 `deck_frame` 为**唯一根**，所有 undercarriage / restraint / caster 作为并联子件挂在 deck 之下。o1 的升降语义被重表达为 deck 固定、`lower_carriage` 经 PRISMATIC 相对 deck 收放（伸缩套管形式），运动语义（相对位移）与源一致（`AUTHORING.md` §A Rule 3 允许保持 part tree / primitive / joint type 不变的前提下换根）。

## 核心身份

Stretcher = 承载并搬运伤病员的**全身承托面** + **搬运/滚动/抬升手段**（轮式底架 / 抬杆 / 篮框）+ **≥1 个真实非固定关节**（折叠 / 铰接 / 伸缩 / 脚轮回转）。默认成熟域覆盖：轮式急救床（剪叉或折叠腿）、担架杆帆布担架、Stokes 篮式救援担架、刚性脊柱板。

不该混入：医院检查床 / 可调诊查床（多电机段、无搬运底架）；轮椅 / 爬楼椅（坐姿转运）；医院电动床架；手推车 / 家具型 gurney。每个 seed 必保留 ≥1 非 FIXED 关节（backrest / 折叠腿 / 撑杆 / 篮框对折 / 固定块铰 / 脚轮回转其一）。

## 槽位 + 候选模块表

三个主槽位（`deck` ③形态主导 · `undercarriage` ②机构+底架 · `restraint` ①约束）+ 一根 caster 复制数量轴。

### Slot A：`deck`（③ 主体形态家族 + patient_surface，ROOT，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `padded_cot` | origin_anchor | o1 / o2 | 39031c58:L78-L106（deck_pan+foot/seat pad）, L118-L162（backrest REVOLUTE）; c7b79ba9:L386-L406（deck_board+main_mattress） | Volumetric Envelope Form（分段泡沫床垫厚板） | eligible | Box deck 板 + 分段泡沫垫 visuals + `backrest` REVOLUTE 子件 + 座垫/床垫接缝 |
| `canvas_cot` | forked_anchor | rec_stretcher_var_canvas_deck | canvas_deck:L100-L145（canvas_deck+hem+lace+strap） | Macro Surface Construction（管框上张紧帆布膜） | eligible | 管周框 + 张紧帆布面板 + 缝边 hem visuals + `backrest` REVOLUTE 子件 |
| `basket_shell` | forked_anchor | rec_stretcher_var_basket_litter | basket_litter:L147-L262（_add_basket_half）, L286-L303（对折 REVOLUTE） | Volumetric Envelope Form（船型篮壳） | eligible（重，见 §7.5） | 椭圆周缘 rim 放样管 + 穿孔底盘 + 立肋 + 绳把手 + `foot_basket` 蛤壳对折 REVOLUTE 子件；无 backrest |
| `spine_board` | forked_anchor | rec_stretcher_var_spine_board | spine_board:L88-L111（_make_spine_board_mesh）, L185-L277（板+spider strap+把手） | Planar Boundary Form（带手孔的平面板） | eligible（mesh，见 §7.5） | ExtrudeWithHoles 平板 + 头垫 + spider 约束带 visuals + 端把手；无 backrest（关节由 restraint=immobilizer_blocks 提供） |

### Slot B：`undercarriage`（support_or_base + ② collapse/lift 机构 + 脚push handle；并联挂 deck 下）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `scissor_wheeled` | origin_anchor | o1 | 39031c58:L58-L75（lower_carriage）, L107-L115（height PRISMATIC）, L182-L211（scissor 视觉X）, L213-L227（caster loop） | eligible（padded/canvas） | `lower_carriage` 部件经 PRISMATIC `height_slide`（轴z）相对 deck 收放；剪叉 X 为 carriage visuals；N 个 caster CONTINUOUS；脚 push hoop |
| `foldleg_wheeled` | origin_anchor | o2 | c7b79ba9:L549-L552 + L630-L647（head/foot_leg REVOLUTE）, L554-L601（caster）；直管腿采 o1 tube 惯用法 | eligible（padded/canvas） | `head_leg`/`foot_leg` REVOLUTE 折叠（直 Cylinder 管腿，见 §7.5 降精说明）；N∈{2,4} caster CONTINUOUS；脚 push handle |
| `telescoping_wheeled` | forked_anchor | rec_stretcher_var_telescoping_legs | telescoping_legs:L210-L230（telescoping_leg PRISMATIC）, L232-L256（caster） | eligible（padded/canvas） | deck 固定外套管 + `lower_carriage` 内滑管经 PRISMATIC；N 个 caster CONTINUOUS |
| `carry_poles` | forked_anchor | rec_stretcher_var_pole_canvas | pole_canvas:L127-L157（_add_pole_geometry）, L160-L209（_add_spreader_geometry）, L388-L407（spreader REVOLUTE） | eligible（padded/canvas/board） | 两根抬杆（deck visuals，经 pole_strut 连回 deck）+ `head_spreader`/`foot_spreader` 折叠撑杆 REVOLUTE；无 caster |
| `bare_feet` | forked_anchor | rec_stretcher_var_spine_board / rec_stretcher_var_basket_litter | spine_board:L161-L172（"No wheels or legs"）; basket_litter（篮直接落地） | eligible（basket/board） | 四角短橡胶脚 stub（deck visuals，Rule1 不建 part、不建 joint）；无 caster；关节靠 deck/restraint 提供 |

### Slot C：`restraint`（restraint_or_side_rails ①；并联挂 deck 上）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `folding_rails` | origin_anchor | o1 / o2 | 39031c58:L164-L180（side_rail + side_rail_hinge REVOLUTE）; c7b79ba9:L544-L547 + L612-L629 | eligible（padded/canvas） | 两根 `side_rail_0/1` 管栏经 REVOLUTE 外翻折叠 |
| `strap_harness` | forked_anchor | rec_stretcher_var_strap_harness | strap_harness:L104-L124（chest/waist/leg 交叉带 + Y 肩带 visuals） | eligible（padded/canvas/basket） | 交叉约束带 + 肩带 + buckle 全部为 deck visuals（无独立 part、无 joint） |
| `immobilizer_blocks` | forked_anchor | rec_stretcher_var_spine_board | spine_board:L118-L154（_add_immobilizer_block）, L295-L312（REVOLUTE） | eligible（board 专用；为 board 提供必需关节） | 两块头部固定耳块经 REVOLUTE 外翻 |

硬约束核对：Slot A 4 候选 / B 5 候选 / C 3 候选，均 ≥3；每候选结构互异（换 part tree / joint / 主体形态原型，非仅换尺寸涂装）；每 ①/② candidate 有 `forked_anchor`/origin + `model.py:Lx-Ly`；③ `basket_shell`/`spine_board` 为真实 forked_anchor（非纯世界知识）。`bare_feet` 是"无底架"形态，由 spine_board/basket 源背书（不新增 skeleton/joint，仅省略底架）。

未采样（documented degrade）：`foot_gatch`（脚段 REVOLUTE）、`trendelenburg_tilt`（整床倾斜）、`scoop_split`（分半 PRISMATIC）、`telescoping_handles`（伸缩把手 PRISMATIC）暂不进 seed domain——① 骨架多样性已由 rails/straps/blocks + backrest 有无覆盖，② 机构多样性已由 PRISMATIC(height/telescoping)+REVOLUTE(foldleg/spreader/backrest/rails/blocks/fold)+CONTINUOUS(caster) 覆盖；纳入这些会增加跨槽 seam 与编译负担，遵 `AUTHORING.md` §B "prefer more candidates over more slots" + §7.5 预算收敛优先。reviewer 可后续增补。

## 槽位图（slot graph）

pattern: mixed（parallel_children 主导 + caster multiplicity）

```
deck_frame (ROOT, Slot A)
  ├─[REVOLUTE deck_to_backrest, axis y, origin=head hinge line]──> backrest        (仅 padded_cot / canvas_cot)
  ├─[REVOLUTE fold_hinge, axis y, origin=fold line]──────────────> foot_basket     (仅 basket_shell)
  │
  ├─ Slot B undercarriage (并联挂 deck 下, origin=deck 底面):
  │    scissor_wheeled/telescoping_wheeled: [PRISMATIC height_slide, axis z]──> lower_carriage
  │                                            └─[CONTINUOUS caster_spin_i]──> caster_i (i in 0..N-1)
  │    foldleg_wheeled: [REVOLUTE deck_to_head_leg / deck_to_foot_leg, axis y]──> head_leg / foot_leg
  │                        └─[CONTINUOUS leg_to_caster_i]──> caster_i
  │    carry_poles: [REVOLUTE deck_to_head_spreader / deck_to_foot_spreader, axis x]──> head_spreader / foot_spreader
  │    bare_feet: (deck visuals only, 无 joint)
  │
  └─ Slot C restraint (并联挂 deck 上, origin=deck 侧缘/头端):
       folding_rails: [REVOLUTE deck_to_side_rail_0/1, axis ∓x]──> side_rail_0 / side_rail_1
       strap_harness: (deck visuals only, 无 joint)
       immobilizer_blocks: [REVOLUTE deck_to_block_0/1, axis ∓x]──> imm_block_0 / imm_block_1
```

接口点位：
- backrest/foot_basket：hinge 在 deck 头端/中线，pin 管为 deck 与子件重叠的 captured-pin（element-scoped allow_overlap）。
- undercarriage：joint origin 落在 deck 底面 socket visual 上（origin-proximity 用 deck 底管/socket 支撑）。PRISMATIC 沿 z；REVOLUTE 沿 y（腿）/ x（撑杆）。
- restraint：joint origin 落在 deck 侧缘 rail_socket visual 上；REVOLUTE 沿 ∓x 外翻。
- 互斥/gating 见 §9 compatibility matrix。

## 每槽位 Module Emits / Interfaces

### Slot A / `padded_cot`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `deck_frame`(root: deck 板+分段泡沫垫+接缝+侧 socket visuals), `backrest`(pad+周框管+hinge pin) | 39031c58:L78-L162; c7b79ba9:L386-L406 |
| internal joints | `deck_to_backrest` REVOLUTE axis (0,1,0) range [-0.55, 0.60] | 39031c58:L154-L162 |
| interface | deck 底面 socket（undercarriage 上游）、deck 侧缘 rail_socket（restraint）；backrest hinge pin captured | c7b79ba9:L418-L466 |

### Slot A / `canvas_cot`
| parts | `deck_frame`(管周框+张紧帆布面板+hem+lace visuals), `backrest` | canvas_deck:L100-L145 |
| internal joints | `deck_to_backrest` REVOLUTE axis y | 同上 |

### Slot A / `basket_shell`
| parts | `deck_frame`(head 半篮: rim 放样管+穿孔盘+肋+绳把), `foot_basket`(foot 半篮) | basket_litter:L147-L291 |
| internal joints | `fold_hinge`(复用命名) REVOLUTE axis (0,-1,0) range [0, 2.6] 蛤壳对折 | basket_litter:L295-L303 |
| interface | hinge barrel captured-pin（allow_overlap）；篮外底可挂 foldleg/poles/bare | basket_litter:L238-L262 |

### Slot A / `spine_board`
| parts | `deck_frame`(ExtrudeWithHoles 平板+头垫+spider 带+端把手 visuals) | spine_board:L185-L277 |
| internal joints | 无（板本体不动）；关节由 restraint=immobilizer_blocks 提供 | — |

### Slot B / `scissor_wheeled` · `telescoping_wheeled`
| parts | `lower_carriage`(下框+剪叉X或内滑管 visuals), `caster_i`(tire+hub Cylinder) i in 0..N-1 | 39031c58:L58-L227; telescoping_legs:L210-L256 |
| internal joints | `height_slide` PRISMATIC axis (0,0,1) range [0, travel]; `caster_spin_i` CONTINUOUS axis y | 39031c58:L107-L115, L219-L227 |

### Slot B / `foldleg_wheeled`
| parts | `head_leg`,`foot_leg`(直 Cylinder 管腿+脚轮座), `caster_i` | c7b79ba9:L549-L601, L630-L647 |
| internal joints | `deck_to_head_leg`/`deck_to_foot_leg` REVOLUTE axis (0,∓1,0) range [0,1.20]; `leg_to_caster_i` CONTINUOUS axis x | c7b79ba9:L630-L647, L593-L601 |

### Slot B / `carry_poles`
| parts | 抬杆为 deck visuals; `head_spreader`,`foot_spreader` | pole_canvas:L127-L209 |
| internal joints | `deck_to_head_spreader`/`deck_to_foot_spreader` REVOLUTE axis (1,0,0) range [0,1.30] | pole_canvas:L388-L407 |

### Slot B / `bare_feet`
| parts | 四角短脚 stub = deck visuals（无 part、无 joint） | spine_board:L161-L172 |

### Slot C / `folding_rails`
| parts | `side_rail_0`,`side_rail_1`(hinge 管+顶护管+立柱) | 39031c58:L164-L180 |
| internal joints | `deck_to_side_rail_0/1` REVOLUTE axis (∓1,0,0) range [0,1.45] | c7b79ba9:L612-L629 |

### Slot C / `strap_harness`
| parts | chest/waist/leg 交叉带+Y 肩带+buckle = deck visuals（无 part、无 joint） | strap_harness:L104-L124 |

### Slot C / `immobilizer_blocks`
| parts | `imm_block_0`,`imm_block_1`(HDPE 基块+泡沫垫+hinge tab) | spine_board:L118-L154 |
| internal joints | `deck_to_block_0/1` REVOLUTE axis (∓1,0,0) range [0,1.45] | spine_board:L295-L312 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `deck` | enum | padded_cot / canvas_cot / basket_shell / spine_board | padded_cot | choice | procedural sampler | Slot A |
| `undercarriage` | enum | scissor_wheeled / foldleg_wheeled / telescoping_wheeled / carry_poles / bare_feet | scissor_wheeled | conditional | 合法集依赖 `deck`（§9） | Slot B |
| `restraint` | enum | folding_rails / strap_harness / immobilizer_blocks | folding_rails | conditional | 合法集依赖 `deck`（§9） | Slot C |
| `caster_count` | int(N) | 2 / 4 / 6 | 4 | conditional | 仅 wheeled undercarriage 采样；否则 0 | casters_two/six + o1/o2 |
| `palette_style` | enum | 6 colorway（§8.5⑥） | safety_orange | choice | 每 seed `rng.choice` | 全源 |
| `deck_len_scale` | float | [0.92, 1.08] | 1.0 | independent | clamp | ⑤ deck length ~1.8-2.0 m |
| `deck_width_scale` | float | [0.92, 1.08] | 1.0 | independent | clamp | ⑤ |
| `deck_height_scale` | float | [0.90, 1.10] | 1.0 | independent | 仅 wheeled；deck 站立高度 | ⑤ o2 站立高 ~0.83 |
| `height_travel` | float | derived | 0.10 | equation | `= 0.10·deck_height_scale`，且 ≤ carriage_top 到 deck 底净距 − 0.02 | 39031c58:L114 |
| `backrest_angle_scale` | float | [0.85, 1.12] | 1.0 | independent | backrest range 上界 × scale，clamp ≤0.60 | 39031c58:L161 |
| `fold_angle_scale` | float | [0.85, 1.12] | 1.0 | independent | 腿/栏/块 fold 上界 × scale，各自 clamp | 各源 |
| (—) | constraint | — | — | inequality | `carriage_top_z + height_travel ≤ deck_underside_z − 0.02`（升降不顶穿 deck），违反回缩 height_travel | 接口/clearance |
| (—) | constraint | — | — | inequality | caster 行 y 位于 deck 宽度内、纵向两排；N=6 中排对称加、N=2 仅脚端一对 | 复制策略 |

采样契约：先采 independent scales → 派生 `height_travel`（equation）→ 用 inequality 回缩 height_travel/校正 caster 行 → conditional（undercarriage/restraint 合法集、caster_count）在采样前按 `deck` 解析。全部在 `resolve_config` 内求解。

## 7.5 编译预算 / compile budget
自报每-seed 预算：**廉价形态（padded_cot/canvas_cot + 任意底架）≤8s**（纯 Box/Cylinder tube-frame + 便宜 Cylinder 脚轮 + ≤2 个 rounded_pad mesh）；**重形态（basket_shell / spine_board）≤15s**。依据：库内 Box/Cylinder 5-10s；basket 放样管 + 2 穿孔盘 + spine ExtrudeWithHoles 属中量 mesh，控精即可 <15s。sweep watchdog `--compile-timeout 120`（≈8×，仅 hang guard）。

分档 tessellation：
- 脚轮统一用 o1 的便宜 `Cylinder(tire)+Cylinder(hub)`（**非** o2 的 TireGeometry/WheelGeometry mesh），N 个脚轮共用同一 Cylinder 参数（无 per-wheel mesh 生成）。
- foldleg 用**直** Cylinder 管腿（o1 tube 惯用法），不用 o2 `_curved_tube` 放样腿（Rule3：直管腿由 o1-style 源背书，非降级）。
- basket：rim/bottom rail 放样管 `radial_segments≤12, samples_per_segment≤8`；肋 5 根；绳把 3 根/半（源为 5，降数控预算）；穿孔盘 `PerforatedPanelGeometry` 每半 1 个。
- spine_board：单 `ExtrudeWithHolesGeometry`（10 手孔），`corner_segments≤8`。
- rounded_pad mesh `corner_segments≤8`；小半径特征 ≤32 段，无英雄大面。

超预算先降精度（减肋/把/段数）再迭代（§C）。

## Multiplicity / Copy Logic

**一根复制轴：`caster_count` N（脚轮）。**
- `count_param`：wheeled undercarriage 的脚轮数 N；`N_range`：产品域 {2,4,6}（奇数罕见，排除）；测试与产品同域（小类枚举明确）。
- sampling domain：`scissor_wheeled`/`telescoping_wheeled`（车架式，可任意排布）采 N∈{4,6}（权重 0.68/0.32）；`foldleg_wheeled`（每腿一对轮）采 N∈{2,4}（权重 0.25/0.75，N=2=仅脚腿一对）；`carry_poles`/`bare_feet` → N=0。整体域 {2,4,6} 仍全覆盖（N=2 由 foldleg、N=6 由车架各实现）。
- copied object：脚轮=tire(Cylinder)+hub(Cylinder)+spin_marker 子装配。
- naming：`caster_i` / spin joint `caster_spin_i`（scissor/telescoping，parent=lower_carriage）或 `leg_to_caster_i`（foldleg，parent=head/foot_leg），i in 0..N-1。
- placement：两纵排共享轨道；N=4 头尾各一对；N=6 加中排对称一对；N=2 仅脚端一对。
- joint policy：每轮一个 CONTINUOUS spin joint 绕局部轴（y 或 x），loop 生成，绝不手写。
- source/gating：casters_two（N=2）、o1/o2（N=4）、casters_six（N=6）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | restraint: 折叠护栏(2 part) / 约束带(0 part) / 固定块(2 part)；backrest 有(cot)/无(basket/board)；undercarriage part 数: carriage(1)+N 轮 / 2 腿+N 轮 / 2 撑杆 / 0；basket 加 foot_basket 对折 part。全 source-backed（o1/o2/strap_harness/spine_board/basket/pole_canvas）。multiplicity 见下。 |
| └ multiplicity | 同构件 ×N | 有 | caster N ∈ {2,4,6}，权重档见 §8；来源 casters_two/six + o1/o2。 |
| ② 关节类型 | 图不变换 type/轴 | 有 | PRISMATIC(height_slide/telescoping, axis z)；REVOLUTE(foldleg axis y / spreader axis x / backrest axis y / rails axis x / blocks axis x / basket fold axis y)；CONTINUOUS(caster axis y 或 x)。每种在 sweep 出现。source-backed（各源）。 |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有（**主多样性槽 `deck`，登记进 slot_choices**） | padded_cot=Volumetric Envelope Form（分段泡沫床垫厚板, o1/o2）；canvas_cot=Macro Surface Construction（管框张紧帆布膜, canvas_deck）；basket_shell=Volumetric Envelope Form（船型 Stokes 篮壳, basket_litter）；spine_board=Planar Boundary Form（带手孔平面板, spine_board）。4 个 source-backed 原型。 |
| ④ 表面装饰 | 原型不变叠表面细节 | 有 | 约束带/肩带布局、床垫接缝、brake/release 红贴、板手孔、帆布缝边 hem/grommet、篮绳把——全 host-conformal（宿主 part visual，随 ③⑤ 尺寸派生），非独立 variant、非 joint。record_only + world_knowledge_extrapolation。来源各源。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | deck 长 scale[0.92,1.08]（~1.8-2.0 m）、宽 scale、高 scale；height_travel≈0.10·scale；关节包络：backrest axis y [闭合 0 → 上界 ≤0.60]；folding_rails axis ∓x [0→1.45·scale]；foldleg axis y [0→1.20]；spreader axis x [0→1.30]；imm_block axis ∓x [0→1.45]；basket fold axis y [0→2.6]；height_slide axis z [0→travel]；caster CONTINUOUS 整圈。`motion_test_plan`: 跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` + 每机构一条 targeted `ctx.pose`（backrest 抬起、rail/block 外翻降、腿/撑杆折入、height 收放、caster 自转）。captured-pin（backrest hinge / rail socket / leg socket / basket barrel）用 element-scoped allow_overlap（源已声明）。 |
| ⑥ 涂装 | 只改材质/配色 | 有 | 材质大类 metal/painted-metal + vinyl/foam + canvas + HDPE-plastic + rubber；配色 6：safety_orange(o1)、safety_yellow(o2)、rescue_orange(basket/board)、olive_drab(pole canvas)、ems_navy(companion)、hi_vis_lime(companion)。材质大类覆盖 ≥ ceil(0.5×6)=3（满足）。 |

**收尾自检**：`template batch` 0-9 seed 目检 4 个 ③ 原型都出现、6 配色不单调、装饰贴合宿主面、关节全程不穿模。

## 采样与覆盖审计

总组合数（离散，含 gating；以实现为准）：
- padded_cot & canvas_cot（2）× 底架实例{scissor(N4,N6=2), foldleg(N2,N4=2), telescoping(N4,N6=2), carry_poles(1)}=7 × {folding_rails,strap_harness}（2）= 2×7×2 = **28**
- basket_shell（1）× {bare_feet(1)} × {strap_harness}（1）+ foot_basket 对折 = **1**
- spine_board（1）× {bare_feet(1),carry_poles(1)}（2 实例）× {immobilizer_blocks}（1）= **2**
- 合计 ≈ **31** 合法离散组合 + 连续 scales。

理由：本小类真实产品域即约 12-15 个骨架锚点（源 map 12 anchors + 1 probe）；47 合法组合已覆盖并外推其主要边界。Topology target report-only：1000-seed slot tuple 覆盖预计 <300（离散空间受强兼容约束封顶 ~47），低于 300 的原因即真实组合空间受 must_not_become / 关节必存约束限制，非上游变体不足——report-only 不作 gate。

seed_domain_policy：procedural_first（seed 0 不特殊）。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)`：① `rng.choice` 采 `deck`；② 按 `deck` 解析 undercarriage/restraint 合法集后 `rng.choice`；③ wheeled 底架加权采 `caster_count`；④ `rng.choice(PALETTE_STYLES)`；⑤ 采 independent scales。`resolve_config` 再 `_pick` 校验 enum + `_clamp` scales + gating 复投影 + 派生 height_travel。无小 curated/modulo 表；无 regression override（首版）。random sweep seeds 0-35 初验、0-999 成熟度观察；viewer 目检 §9 选的 ~10 seeds。

Controlled local parameterization：`deck_len_scale`/`deck_width_scale`/`deck_height_scale`/`backrest_angle_scale`/`fold_angle_scale`（independent, clamp）+ `height_travel`（equation）+ caster 行位置（inequality）。均在 `resolve_config` clamp/派生，不破坏 socket 接口 / clearance / joint origin / caster 复制。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | deck→(gated undercarriage, restraint)→caster N→palette→scales | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 见下矩阵；非法组合在 config_from_seed/resolve_config 拦截 | 无悬空/穿模/轴错/closed-pose/max-N/可选子件失败 |
| controlled local variation | 5 scale + travel + caster 行 clamp/derive | 比例变化不破接口/clearance/joint origin/identity |
| regression overrides | none（首版） | — |
| random sweep | 0-35 初验, 0-999 成熟度 | contract failures; axis_realization; viewer |

Compatibility matrix：
- `padded_cot` / `canvas_cot` → undercarriage ∈ {scissor_wheeled, foldleg_wheeled, telescoping_wheeled, carry_poles}；restraint ∈ {folding_rails, strap_harness}；backrest 有。
- `basket_shell` → undercarriage = bare_feet（Stokes 船型壳落地；deck_frame 只含头半篮，head-only 根无法锚定头-尾贯通的腿/车架，故不配 wheeled/poles）；restraint = strap_harness（横带铺在头半篮穿孔盘上）；backrest 无；foot_basket 对折 REVOLUTE 提供必需关节。
- `spine_board` → undercarriage ∈ {bare_feet, carry_poles}；restraint = immobilizer_blocks（提供必需 REVOLUTE 关节）；backrest 无。
- caster_count 仅 {scissor,foldleg,telescoping}_wheeled 采样；否则 0。

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| deck | 4 | yes | yes | ③ 主形态槽 |
| undercarriage | 5 | yes | yes | ② 机构 + 底架 |
| restraint | 3 | yes | yes | ① 约束 |
| caster_count | 3 (N=2/4/6) | yes | yes | multiplicity 轴 |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名（deck/undercarriage/restraint/caster n{N}）。
- `config_from_seed` 对所有普通 seed（含 0）用 deterministic procedural sampling。
- compatibility matrix / gating 阻止非法组合（deck↔undercarriage↔restraint↔caster）。
- 无 regression override（首版）；不循环小 curated 表。
- 局部 scale clamp，且不破坏 socket 接口 / clearance / joint origin / caster 复制。
- 跨部件依赖（height_travel equation、caster 行 inequality、gating conditional）在 `resolve_config` 解析。
- 关键 MatingContract / captured-pin allow_overlap 点存在（backrest/rail/leg/basket hinge）。
- 关键 joint type/axis/range 正确（见 §6/§8.5②⑤）。
- 复制脚轮遵命名/放置策略（loop 生成）。
- 每 seed ≥1 非 FIXED 关节。

## Reject cases

- 某 deck 形态无任何非 FIXED 关节（如 spine_board 配 strap_harness/bare 却无 immobilizer_blocks）→ 违 must_keep。
- 把装饰（约束带/接缝/brake 贴/绳把）建成 FIXED part 或独立 joint → 违 Rule1。
- 脚轮/腿 hinge 无 MatingContract 或 captured-pin allow_overlap，导致 mating gap / 悬空。
- 升降 PRISMATIC 顶穿 deck（height_travel 未按 inequality 回缩）。
- foldleg/rail/block fold 上界过大导致自碰或翻穿 deck。
- basket 放样管/穿孔盘 tessellation 过细导致单 seed >20s（违 §7.5）。
- caster_count 采到奇数或 wheeled 外底架仍生成脚轮。
- deck↔undercarriage↔restraint 采到非法组合（如 spine_board 配 scissor_wheeled）。

## 与相邻类别的边界
- 不该混入：hospital exam/adjustable couch（多电机诊查段、无搬运底架；foot_gatch/backrest 已在担架身份内覆盖多段铰接）。
- 不该混入：wheelchair / stair-chair（坐姿转运，违 must_not_become）。
- 不该混入：hospital electric bed frame（固定病房床架）。
- 不该混入：hand cart / furniture gurney（无全身承托面）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 首版：3 主槽(deck③/undercarriage②/restraint①)+caster N 轴；未采样 foot_gatch/tilt/scoop/telescoping_handles（documented degrade，tractability + §7.5）。re-root 到 deck_frame 统一根。 |

## 模板实现备注
- 共享 helper：`_tube`(Cylinder between pts)、`_box`、`_curved_tube`(mesh 放样)、`_rounded_pad_mesh`、`_caster`(便宜 Cylinder 轮)。
- captured-pin element-scoped allow_overlap：backrest hinge_bar↔deck socket、side_rail lower_tube↔deck rail_socket、leg top_hinge↔deck leg_socket、basket hinge_barrel↔hinge_barrel、caster hub↔axle。
- 未进 seed domain 组合：见 §9 compatibility matrix 之外全部；foot_gatch/tilt/scoop/telescoping_handles 未采样。
</content>
</invoke>
