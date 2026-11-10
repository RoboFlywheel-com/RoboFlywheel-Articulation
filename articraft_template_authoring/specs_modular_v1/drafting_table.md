# Modular Spec — Workspace / Drafting table (`drafting_table`)

## 元信息
| 项 | 值 |
|---|---|
| slug | `drafting_table` |
| template path | `agent/templates/drafting_table.py` |
| test path (optional) | `tests/agent/test_drafting_table_template.py` (skipped; sweep is authoritative) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (+ multiplicity) |

`pattern`：单一 grounded 支撑根（frame / 对望远：base→carriage）作为 chassis，携带一个 REVOLUTE 倾斜绘图板子件、两个 REVOLUTE 侧向锁定控件子件；抽屉/棘齿为宿主 visual 复制。所有 slot 的 part 挂到同一 mount chassis，因此是 parallel_children 而非串链。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (3 origins + 5 forks) |
| source_index_policy | only adopted module sources are indexed below |

三个 origin（001 cantilever 金属 Z 架、002 splayed-X 金属架、003 木托架 A-frame）+ 五个 verified-PASS fork（base_column 中央柱、base_fourpost 四直腿、mech_height 伸缩升降、grip_crank 摇把、n_drawers3 三抽屉）全部读完。

## 核心身份

绘图桌 / 制图台：一块宽平的**绘图板**（工作面）以**低前缘的铰链**倾斜（REVOLUTE tilt），由**落地支撑**架高到站/坐制图高度，并配一个**角度锁定控件**（旋钮 / 棘齿）把板固定在设定角度。默认成熟域：金属或木制底架 + 木绘图板 + 侧向锁定旋钮 + 可选前置抽屉/托盘。

不该混入：平写字桌/办公桌（顶不倾斜）、餐桌/工作台、画架（无落地桌面高度工作面）、抽屉柜/斗柜（有抽屉但无倾斜板）。识别核心 = 「宽平板 + 真实倾斜铰链 + 落地架 + 角度锁定」四件全在。

## 槽位 + 候选模块表

绘图板本体在全部样本里都是**同一平面板形态**（Planar Boundary Form，不构成 ③ 形态家族多样），因此**主结构多样性落在 ① 支撑底架 slot（6 候选）**，配合 ② 角度锁定硬件 slot 与 ③ 控件形态 slot、N 抽屉复制。绘图板 + 倾斜铰链是每个模型都在的常量层，不设 slot（<2 候选，折入 chassis）。

### Slot A：support_base（① 骨架 / 结构拓扑 —— 主多样性）

grounded 根。每个候选把 legs/support 结构建到一个**统一的上部接口平面**（前铰链轨 z≈0.755、侧旋钮座 z≈0.455、抽屉围板区），并暴露 `mount` chassis part（非伸缩=frame 自身；伸缩=carriage）。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `cantilever_zframe` | forked_anchor | rec_workspace__drafting_table__001 (`frame` 撇腿+脚杠+篮筐轨) | 001 model.py:L109-L227 | eligible if compatible | 前后撇腿（斜）+ 前后脚杠 + 顶轨 + 侧顶轨 + 篮筐/抽屉横轨；金属；part=frame（root=mount） |
| `splayed_xbrace` | forked_anchor | rec_workspace__drafting_table__002 (`frame` side_brace/rear_kick_brace X 腿) | 002 model.py:L70-L108 | eligible if compatible | 两侧 X 撑（side_brace+rear_kick_brace）+ 落地 runner + 顶侧轨；金属；root=mount |
| `wood_trestle` | forked_anchor | rec_workspace__drafting_table__003 (`support_frame` 立柱+托架足+横档) | 003 model.py:L135-L210 | eligible if compatible | near/far 托架立柱 + 脚墩 + 上下横档 stretcher；**木质**；root=mount |
| `pedestal_column` | forked_anchor | rec_drafting_table_var_base_column (十字足+中央柱+yoke 头) | var_base_column model.py:L73-L170 | eligible if compatible | 十字 foot_arm ×2 + 脚垫 + 单中央 `pedestal_column` + column_collar + yoke 横梁/前臂/侧撑；金属；root=mount |
| `four_post` | forked_anchor | rec_drafting_table_var_base_fourpost (4 直角腿+盒围板) | var_base_fourpost model.py:L76-L129 | eligible if compatible | 4 直立角腿（loop）+ 矩形围板（front/rear/left/right apron）+ 侧横档；金属；root=mount |
| `telescoping_carriage` | forked_anchor | rec_drafting_table_var_mech_height (base 外套筒 + carriage 内管 + prismatic) | var_mech_height model.py:L81-L156,L276-L284 | eligible if compatible | `base`（接地 runner+外套筒+夹环）与 `carriage`（内滑管+上框）拆分，1 个 PRISMATIC `base_to_carriage` 竖直行程 ~0.15 m；root=base，mount=carriage |

### Slot B：angle_mechanism（② 角度锁定硬件）

非活动的角度保持硬件，写成 mount chassis 的 `.visual(...)`（Rule 1：不动就不是 part）。倾斜 REVOLUTE 恒在（常量层）；本 slot 只换「锁定机构外观/结构」。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `friction_knob_lock` | forked_anchor | rec_workspace__drafting_table__001 (侧 hinge_cheek + 摩擦锁，无齿) | 001 model.py:L189-L195,L359-L397 | eligible if compatible | 仅侧铰颊 + 旋钮摩擦锁，无棘齿条；最简硬件 |
| `linear_toothed_ratchet` | forked_anchor | rec_workspace__drafting_table__002 (`ratchet_backbone` + 6 齿 loop) | 002 model.py:L85-L94 | eligible if compatible | 两侧 ratchet_backbone 直条 + `for tooth in range(6)` box 齿排 |
| `curved_ratchet_quadrant` | forked_anchor | rec_workspace__drafting_table__003 (`_annular_sector_geometry` 弧板) | 003 model.py:L65-L115,L224-L263 | eligible if compatible | 环形扇区 mesh 弧板（annular sector，此处置于 YZ 平面绕 X 铰轴）+ 螺孔点 |

### Slot C：control_handle（③ 控件形态家族 / ② 全 REVOLUTE）

真实 REVOLUTE 子 part（每候选 2 个），挂到 mount chassis 侧面标准旋钮位。原地自转锁定。

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `paired_symmetric_knobs` | forked_anchor | rec_workspace__drafting_table__002 (`lock_knob_0/1` 对称盘旋钮) | 002 model.py:L238-L267 | eligible if compatible | 两个**同构** knob_disk+knob_shaft+grip_rib×3 REVOLUTE 子件 |
| `differentiated_knobs` | forked_anchor | rec_workspace__drafting_table__003 (`lock_knob` 大 + `angle_knob` 小) | 003 model.py:L406-L474 | eligible if compatible | 一大（KnobGeometry lobed r0.070）+ 一小（r0.044）**异构** lobed 旋钮 REVOLUTE 子件 |
| `crank_winder` | forked_anchor | rec_drafting_table_var_grip_crank (`_add_crank_handle` 摇把) | var_grip_crank model.py:L87-L137,L408-L426 | eligible if compatible | 两个摇把子件：threaded_stem + crank_hub + 径向 crank_arm + 平行 crank_grip（离轴形态，非同心盘）REVOLUTE |

硬约束满足：三 slot 各 ≥3 candidate，均 `forked_anchor` + `model.py:Lx-Ly`；候选间结构不同（非仅换尺寸/色）。绘图板本体单一 planar 形态，不设 ③ 主体形态 slot，理由见 §8.5 ③。

## 槽位图（slot graph）

pattern: parallel_children (+ multiplicity)

```
support_base(root=frame|base→carriage)
  ├─[REVOLUTE tilt, axis +X, origin (0,-0.365,0.755), captured-pin hinge]──> tabletop(常量绘图板)
  ├─[REVOLUTE lock, axis +X, origin (±0.60,-0.175,0.455), captured-pin socket]──> control_handle 子件 ×2
  ├─[host .visual on mount]── angle_mechanism 硬件（非关节）
  └─[host .visual on mount]── drawer_bank 抽屉围板 ×N（FIXED cosmetic，非关节）
telescoping_carriage 额外：base ─[PRISMATIC +Z, 0..0.15]─> carriage(=mount)
```

- 接口点位：**统一 mount 接口平面** —— 前铰链轨/销 (y=-0.365, z≈0.755, x 跨 ±0.58)、侧旋钮座 (x=±0.552, y=-0.175, z=0.455)、抽屉围板前区 (y≈-0.39, z≈0.585-0.685)。所有 base 候选把 legs 建到该平面并暴露同一 `mount` part。
- 跨 slot joint：tabletop / control_handle 直接 parent 到 mount part（parallel_children，不声明 upstream interface、不走 assembler 自动链接）。angle_mechanism/drawer 只往 mount 加 visual。
- 互斥/派生：drawer_bank N>0 仅在有前围板区的金属架（cantilever/xbrace/four_post/telescoping）；wood_trestle/pedestal_column 无抽屉区 → 强制 N=0。

## 每槽位 Module Emits / Interfaces

### Slot A / support_base（各候选）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`（root+mount）；telescoping 另加 `base`(root) 与 `carriage`(mount) | S1-S6 |
| internal joints | 非伸缩：无；telescoping：`base_to_carriage` PRISMATIC +Z lower0 upper0.15 | var_mech_height:L276-L284 |
| shared interface visuals | front_hinge_rail / hinge_pin / hinge_end_bracket_{idx} / rear_top_rail / top_side_rail_{idx} / knob_socket_{idx} / knob_mount_tab_{idx}（每 base 都发，保证接口一致） | 002:L97-L151 |
| base-specific visuals | 撇腿/X 撑/木立柱/中央柱+yoke/4 角腿/内外套筒（① 拓扑差异） | 见 slot 表 |
| downstream interface | mount part 名（frame|carriage），tabletop/knob/mechanism/drawer 挂此 | — |

### Slot B / angle_mechanism
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（全部 host `.visual` on mount，Rule 1） | — |
| internal joints | 无 | — |
| visuals | friction：侧铰颊；linear：backbone+6 齿×2 侧；curved：YZ 环扇弧板+螺孔 | 001/002/003 |

### Slot C / control_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | 2 个 REVOLUTE 子 part（`lock_knob_0/1` 或 `angle/lock_knob` 或 `crank_handle_0/1`） | 002/003/grip_crank |
| internal joints | `frame_to_lock_knob_{idx}` / `frame_to_crank_handle_{idx}` REVOLUTE axis +X lower -π upper π | 002:L259-L267 |
| upstream interface | 螺纹柄 threaded_stem 插入 mount 侧 knob_socket（captured pin，grandfather，用 allow_overlap） | 002:L310-L325 |

### 常量层 / tabletop（chassis 携带）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tabletop`：wood_drawing_board + front/rear/side lip + paper_channel + paper_stop + tilt_barrel + wood_grain×12 | 002:L153-L223 |
| internal joints | `frame_to_tabletop` REVOLUTE axis +X origin(0,-0.365,0.755) 预倾 20°，lower∈[-0.30,-0.20] upper∈[0.45,0.65] | 002:L225-L234 |
| interface | tilt_barrel 抱住 mount 的 hinge_pin（captured pin，grandfather） | 002:L281-L305 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| support_base | enum | 6 module names | — | choice | deterministic sampler | slot A 表 |
| angle_mechanism | enum | 3 module names | — | choice | deterministic sampler | slot B 表 |
| control_handle | enum | 3 module names | — | choice | deterministic sampler | slot C 表 |
| n_drawers | int | [0,4]（gated） | 0 | conditional | 仅金属前围板 base 可 >0；否则 clamp 0 | §8 |
| board_width_scale | float | [0.95, 1.10] | 1.0 | independent | 采样后 clamp；驱动板宽 + 顶轨/铰链轨半跨 | 002 board 1.20 |
| board_depth_scale | float | [0.95, 1.10] | 1.0 | independent | 采样后 clamp；驱动板深 | 002 depth 0.76 |
| tilt_upper | float | [0.45, 0.65] | 0.55 | independent | 倾斜关节上界 | 001/003 upper 0.45/0.65 |
| tilt_lower | float | [-0.30, -0.20] | -0.30 | independent | 倾斜关节下界 | 001/002 lower -0.30 |
| palette_style | enum | 4 配色 | pale_wood_black | choice | 材质/颜色 | ⑥ |
| half_width（派生） | float | derived | 0.60 | equation | `= 0.60·board_width_scale`；顶轨/铰链轨/旋钮跨单一来源 | Contract 3c |
| (—) | constraint | — | — | conditional | n_drawers>0 ⇒ base ∈ {cantilever,xbrace,four_post,telescoping}，否则 0 | 接口 |

连续尺寸契约：先采 independent（board_width/depth_scale、tilt_lower/upper）→ 派生 half_width=0.60·board_width_scale（顶轨/铰链轨/旋钮 x 跨全部从此单一来源）→ conditional 解析 n_drawers 合法域（按 base）。

### 7.5 编译预算 / compile budget（必填）
自报预算 **≤12s/seed**。绝大多数几何是 Box/Cylinder 直杆；mesh 仅：KnobGeometry lobed 旋钮（differentiated/paired 复用同一 mesh，count≤10）、grip_crank 纯 Box/Cylinder、curved_quadrant 环扇 mesh（segments≤40）、TorusGeometry ring pull（复用同一 mesh，radial≤18）。分档 tessellation：旋钮/环扇 ≤40 段，N 个 ring pull 复用单 `Mesh`。远低于重雕刻类。`--compile-timeout 120`（3× 预算的看门狗）。

## Multiplicity / Copy Logic

- count_param: `n_drawers`（板下前置补给抽屉，FIXED cosmetic 面板）
- N_range: 产品域 [0,4]；测试域同 [0,4]（小类抽屉数天然小）。sampling domain 权重：N=0/2 常见（origin A/C 直接展示），N=1/3/4 较少（3=fork，4=origin B，1=插值）。
- copied object: `drawer_face_{i}`（pale 面板）+ `pull_ring_{i}`（TorusGeometry，复用单 mesh）+ `pull_mount_{i}` + `drawer_divider_{i}`（N-1 个）
- naming: `drawer_face_{i}` / `pull_ring_{i}` / `pull_mount_{i}` / `drawer_divider_{i}`，i∈[0,N)
- placement: `drawer_apron` 前围板 X 宽内 `for i in range(N)` 均匀分格，共享 pull helper
- joint policy: 抽屉面 **FIXED cosmetic**（宿主 visual，parent 不开抽屉，Rule 1）——真实非固定关节只有 tilt + 2 控件（+ telescoping 的 prismatic），不变。
- source/gating: 2=origin A ring-pull loop, 4=origin B drawer_face loop, 3=fork n_drawers3, 0=origin C trestle；gate 见 §7。
- 次级 N（record_only 不 fork）：ratchet 齿 `for tooth in range(6)`（linear_ratchet 内部固定 6 齿，非暴露 count）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | **support_base 6 候选**（主多样性）：cantilever_zframe / splayed_xbrace / wood_trestle / pedestal_column / four_post / telescoping_carriage；telescoping 多一个 `base`/`carriage` part + 1 PRISMATIC 边。全部 forked_anchor（§4 slot A）。control_handle 子件数恒 2。 |
| └ multiplicity | 同构件 ×N | 有 | `n_drawers` N∈{0,1,2,3,4}，见 §8（gated 金属前围板 base）。 |
| ② 关节类型 | 图不变，换 type/轴 | 有 | tilt REVOLUTE(+X)恒在；control_handle 全 REVOLUTE(+X)；telescoping_carriage 引入 **PRISMATIC(+Z)** 升降。source-backed（002 revolute / var_mech_height prismatic）。声明的 REVOLUTE 与 PRISMATIC 都在 sweep 出现（tilt 恒 + telescoping 命中即 prismatic）。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别几何原型 | 无（主体）/ 有（控件） | **绘图板主体在全部 8 样本均为单一 Planar Boundary Form（宽平板）**，无主体形态家族多样 → 不设主体 ③ slot（理由：类别核心恒为一块平板，换体量/放样会破坏 identity）。形态多样落在 **control_handle slot**：对称盘旋钮 / 大+小 lobed 旋钮 / 径向摇把（离轴形态），source-backed（§4 slot C）。 |
| ④ 表面装饰 | 原型不变叠加表面细节/改数 | 有 | record_only + host-derived：木纹条 wood_grain×12（板面派生）、drawer ring-pull、ratchet 螺孔、curved 弧板螺孔、paper_stop/paper_channel 板缘、drawer 数量档（§8）。全部宿主 part visual、随板宽 half_width 共形（派生序 ③→⑤→④）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | board_width_scale [0.95,1.10]、board_depth_scale [0.95,1.10]（§7，half_width 单一派生）；**tilt REVOLUTE**：轴 +X，开启方向 = 抬后缘，[tilt_lower∈[-0.30,-0.20], tilt_upper∈[0.45,0.65]]；**control REVOLUTE**：轴 +X，原地自转 [-π,π]；**telescoping PRISMATIC**：轴 +Z，[0,0.15] 升。motion_test_plan 见 §9 与下。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal / wood / plastic / steel-hardware；4 配色：pale_wood_black(A)、warm_red_wood_black(B)、cherry_wood_black(C)、grey_metal_pale。木架候选(trestle)用 wood 主材，金属架用 black_metal。材质大类覆盖 ≥ ceil(0.5×4)=2（metal+wood 均现）。 |

motion_test_plan（Rule 5）：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=40, ignore_fixed=True)`。targeted `ctx.pose`：(1) tilt→upper 抬后缘 ≥ +0.12 z；(2) 每控件 spin 1.2 rad 原地不平移（<1e-6）；(3) telescoping prismatic→0.15 抬 carriage ~0.15 且内管仍插在套筒内。captured-pin（hinge_pin↔tilt_barrel、knob_socket↔knob_shaft、外套筒↔内管）用 element-scoped allow_overlap，无 broad exemption。

## 采样与覆盖审计

总组合数：support_base(6) × angle_mechanism(3) × control_handle(3) × n_drawers(gated,~1-5) = 54 × drawer 档 ≈ 150-270 slot 组合（连续 scale 另计）。

理由：主多样性来自离散 slot（6×3×3）与 N 复制，连续 scale 只做受控扰动，远超 report-only topology target 下限观察需要。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 用 `random.Random(seed)` 采样全域，seed 0 不特殊。
Procedural Sampling / Sweep Plan：每 seed 独立采 support_base / angle_mechanism / control_handle（等权 rng.choice）、board_width/depth_scale、tilt_lower/upper、palette；再按 base gate 采 n_drawers（金属前围板 base 才 >0）。compatibility gating 阻止 trestle/pedestal 带抽屉、阻止非法接口。无小型 curated/modulo 主表。random sweep 0-35 首过；viewer 目检 0-2。
Topology target：6×3×3×drawer ≈ 富度中等；1000-seed slot-tuple 覆盖 report-only，>150 组合，兼容约束限制真实空间，不反推上游变体数。
Controlled local parameterization：board_width_scale / board_depth_scale / tilt_lower / tilt_upper。范围见 §7；half_width=0.60·board_width_scale 单一派生驱动顶轨/铰链轨/旋钮跨；不破坏 mount 接口（旋钮座/铰链销位随 half_width co-vary）。均在 resolve_config clamp/派生。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 等权 rng.choice；n_drawers 按 base gate 加权（小 N 偏多） | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | trestle/pedestal ⇒ n_drawers=0；金属前围板 base ⇒ n_drawers∈[0,4]；telescoping 加 prismatic | 无悬空/穿模/轴错/closed-pose/接口失败 |
| controlled local variation | board_width/depth_scale、tilt_lower/upper（clamp） | 比例变而不破接口/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-35 首过，0-999 成熟审计 | contract failures; axis_realization; viewer 目检 0-2 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| support_base | 6 | yes | yes | 主多样性 ① |
| angle_mechanism | 3 | yes | yes | 硬件 host visual |
| control_handle | 3 | yes | yes | REVOLUTE 子件 ③ |
| drawer_bank (N) | 5 (0-4) | yes | yes | gated multiplicity |

## Validator

- slot_choices_for_seed returns implemented module names（support_base/angle_mechanism/control_handle/n_drawers）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed 0 不特殊）
- compatibility gating prevents illegal combos（trestle/pedestal 无抽屉）
- no regression overrides
- final template does not cycle a curated table as main seed domain
- board_width/depth/tilt scales clamped，不破 mount 接口 / clearance / joint origin / 抽屉复制
- conditional n_drawers gate resolved in resolve_config
- captured-pin interfaces（hinge_pin↔tilt_barrel、knob_socket↔knob_shaft、outer_sleeve↔inner_tube）用 element-scoped allow_overlap；无 MatingContract（grandfathered pin geometry）
- key joints：frame_to_tabletop REVOLUTE +X（lower<0<upper）、frame_to_lock_knob/crank_{idx} REVOLUTE +X（|lower|≥π）、base_to_carriage PRISMATIC +Z（telescoping）
- copied drawer objects follow naming/placement policy（drawer_face_{i}/pull_ring_{i}/drawer_divider_{i}）

## Reject cases

- 绘图板顶不倾斜（无 REVOLUTE tilt）→ 退化为写字桌
- 无落地支撑或支撑不接地 → 悬空
- 无角度锁定控件（旋钮/摇把/棘齿全缺）
- 抽屉建成会动的 PRISMATIC/REVOLUTE part（应为 FIXED cosmetic visual）
- angle_mechanism/drawer 建成独立 FIXED part（应 host visual，违反 Rule 1）
- tilt 到 upper 时后缘穿过 rear_top_rail 或棘齿（sampled-pose 穿模）
- trestle/pedestal 强行挂前抽屉围板（悬空/无接口）
- 旋钮 spin 时整体平移（child 部件原点偏离铰轴）
- mount 接口不统一致 tabletop/knob 与某 base 对不上（gap / origin far）

## 与相邻类别的边界

- 不该混入：写字桌 / 办公桌（顶固定不倾斜；本类核心是 REVOLUTE 倾斜板）
- 不该混入：画架 easel（无落地桌面高度工作面 + 无侧锁旋钮机构）
- 不该混入：抽屉柜 / 斗柜（抽屉排但无倾斜绘图板；本类抽屉是可选 cosmetic 附属）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 主结构多样性在 support_base(①,6)；绘图板主体单一 planar 形态（③ 主体无家族，理由已述），形态多样落 control_handle。所有候选 forked_anchor + 行号来源。captured-pin 全 grandfather，无 MatingContract。 |

## 模板实现备注（可选）

- 共享 helper：`_beam`(rect tube via endpoints)、`_emit_mount_interface`(统一接口硬件)、`_emit_tabletop`(常量板)、`_knob_mesh`/`_add_crank_handle`、`_annular_sector_yz`(curved quadrant)、drawer loop helper。
- 6 base 共享同一上部接口（front_hinge_rail 跨 ±0.58 保证 `wide table top carried by frame` overlap≥1.0；hinge_pin len 1.18）。
- captured-pin element-scoped allow_overlap：hinge_pin↔tilt_barrel、knob_socket_{idx}↔knob_shaft/threaded_stem、outer_sleeve↔inner_tube、sleeve_collar↔inner_tube。
- telescoping：base=root grounded，carriage=mount；prismatic 采 var_mech_height 几何（内管插深 ≥0.15 静止，≥0.04 满伸）。
- 连续 scale 只 board_width/depth + tilt range，避免破接口。
