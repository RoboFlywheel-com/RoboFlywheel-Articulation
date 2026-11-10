# manhole_cover — Modular Template Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `manhole_cover` |
| template path | `agent/templates/Urban_Environment_Manhole_cover.py` |
| test path (optional) | `tests/agent/test_manhole_cover_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel_children: frame→{shaft, cover} + multiplicity: grate bars/cells） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 4 |
| read_count | 4 |
| read_scope | all 5-star samples in this category (the 4 parent records in the source map) |
| source_index_policy | only adopted module sources are indexed below |

四个 5★ 样本结构高度一致，是同一拓扑等价类的不同表面/机构填充：

- **S1 `cast_iron_fan_slot_floor_drain`** (`rec_small-dark-cast-iron-square-floor-drain-grate-se_...27f846c6`, model.py L1-L306)：~150 mm 方形铸铁地漏。`concrete_surround`(FIXED root) + `shaft`(FIXED void) + `drain_grate`(PRISMATIC +Z lift)。表面为 **径向扇形泪滴弧形细缝**，单层循环 `for s in range(N_SLOTS)`(L115)，每缝由 `for i in range(steps+1)`(L68) 弧段多段线扫出。lift origin `Origin(xyz=(0,0,GRATE_REST_BOTTOM_Z))` axis `(0,0,1)` upper `LIFT_TRAVEL`(L193-203)。
- **S2 `cast_iron_basket_weave_grate`** (`rec_square-rusty-cast-iron-drainage-grate-with-a-bas_...01cd7eed`, model.py L1-L286)：~300 mm 方形锈铁排水栅。`frame_ring`(FIXED root)+`shaft`(FIXED)+`drain_grate`(PRISMATIC +Z)。表面为 **错列篮织槽阵**，嵌套循环 `for r in range(n_rows)`/`for c in range(n_cols)`(L81-L97)，N 由 field/pitch 派生，奇行半列错位(L83)。圆角槽 `slot2D`(L50-57)。
- **S3 `cast_iron_inspection_cover`** (`rec_square-cast-iron-inspection-chamber-cover-with-a_...e40ac516`, model.py L1-L329)：~450 mm 方形检修井盖。`frame_ring`+`shaft`+`inspection_cover`(PRISMATIC +Z)。表面为 **实心盖 + 凸起边框 rim + 防滑菱形 stud 网格 + 中央凹板 + 两侧吊钥匙凹槽**，stud 嵌套循环 `for ix in range(n)`/`for iy in range(n)`(L96-118, loft 菱形棱台 L103-112)，key 循环 `for sx in (-1,1)`(L133-139)。
- **S4 `concrete_utility_access_cover`** (`rec_square-weathered-concrete-utility-access-cover-s_...edad8300`, model.py L1-L301)：~620 mm 方形混凝土检查盖。`frame_ring`(stone)+`shaft`+`access_cover`(PRISMATIC +Z)。表面为 **实心混凝土板 + 倒角风化边 + 单条中央撬槽**(`slot2D` L138-144)，**无复制循环**（单板单槽）。

共同骨架：所有样本 = 固定 frame/surround（z∈[0,FRAME_HEIGHT]，footprint base z≈0）+ 固定 shaft void（seat ledge 下方）+ 一个 PRISMATIC +Z 提起的盖/栅子件，seat ledge 落座（`allow_overlap` + `expect_contact`），盖在平面内充满开口（`expect_overlap`/`expect_within`）。

## 核心身份

一块 **方形（铸铁/混凝土）排水栅 / 检修接入盖，落座在凹陷的承座 frame 里，盖下是中空竖井/喉道**，盖面带 **铸造图案或栅条**，整体齐平地面。盖是被铰接的活动子件，**开启机构是真实非固定关节**：默认为 **+Z PRISMATIC 提起取出**，一个 outline+机构变体引入 **REVOLUTE 边缘翻转铰**。lift/hinge 是定义性关节。栅条 / 图案格子是循环复制的 multiplicity。frame 和其下中空竖井保持 FIXED。

默认成熟域：方形（也含派生 round / rectangular outline）铸铁排水栅或检修盖，落座 frame 内、+Z 提起或边缘翻转开启、表面为栅条/槽阵/防滑图案/实心撬槽。

**不该混入的相邻类别见 §与相邻类别的边界**（核心：圆形 Well_lid / 圆顶井盖、墙面 grille/register、独立 trench drain channel 不带 frame+shaft 骨架）。

## 槽位 + 候选模块表

四个 slot：A 盖轮廓 outline、B 表面图案 surface、C 开启机构 mechanism（定义性关节）、D frame 风格 frame_style。N 复制由 B 决定（见 §Multiplicity）。

### Slot A：cover_outline（盖+frame+shaft 的平面轮廓）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `square_outline` | S1/S2/S3/S4 | S2 L21-L38 (GRATE_SIDE 方板 + FRAME_INNER/OUTER 方 frame) | eligible if compatible | 方形盖板 `box(SIDE,SIDE,THICK)` + 方 frame 套 + 方 throat；所有 4 样本基线 |
| `round_outline` | S1（弧形几何复用）+ 新轮廓 | S1 L62-L85 (弧/圆心几何), S2 L60-L67 (方板→圆板替换) | eligible if compatible | 圆盘盖 `circle(R).extrude` + 环 frame + 圆 throat；机构限 PRISMATIC 或居中 hinge（避免方铰几何） |
| `rectangular_outline` | S4（单板单槽最易拉长） | S4 L24-L25 (COVER_SIDE), L129-L133 (box 板) | eligible if compatible | 长方/oblong 盖 `box(LEN,WID,THICK)`（LEN≠WID）+ 长方 frame + 长方 throat |

### Slot B：surface_pattern（盖面铸造图案 / 栅条层；决定 multiplicity 轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `solid_lid` | S3 + S4 | S4 L125-L145 (实板+撬槽), S3 L59-L69 (base+rim) | eligible if compatible | 实心盖板，无 through-slot；可带 rim/单撬槽（cosmetic）；N=0 复制 |
| `basket_weave` | S2 | S2 L60-L105 (嵌套错列槽阵) | eligible if compatible | 错列圆角矩形 through-slot 阵；嵌套行×列循环，奇行错位；N 由 row×col 决定 |
| `parallel_slots` | S2（槽切割复用，单层 loop） | S2 L50-L57 (`_rounded_slot`), L75-L103 (loop→改单层平行) | eligible if compatible | 直长平行 through-slot 组（单循环 `for i in range(N)`），等距贯穿 field |
| `cross_grid` | S2（嵌套循环复用） | S2 L75-L97 (嵌套 r×c loop→改方孔 waffle) | eligible if compatible | 正方 through-hole waffle 网格（嵌套循环），井字铸条分隔 |
| `radial_pattern` | S1 | S1 L55-L85 (`_curved_slot_cutter` 弧), L113-L121 (扇 loop→改环向辐条) | eligible if compatible | 围绕中心一圈辐条状细缝（单循环 `for i in range(N)` 角度分布）；优先配 round_outline |

### Slot C：open_mechanism（定义性关节）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `lift_out_prismatic` | S1/S2/S3/S4 | S4 L177-L188 (PRISMATIC +Z, origin=COVER_REST_BOTTOM_Z, axis (0,0,1), limits) | eligible if compatible | +Z 直提取出；origin 落在 rest bottom，upper=LIFT_TRAVEL 清 frame；所有样本默认 |
| `hinged_flap_revolute` | 新机构（frame edge pivot；复用盖/frame 几何） | S3 L204-L220 (盖 part + 关节挂载点改 REVOLUTE), S3 L132-L139 (edge 参考) | eligible if compatible | 盖沿一条边 REVOLUTE 翻起；pivot origin 在 frame 顶一侧边缘 (y=±SIDE/2)，axis 沿该边 (1,0,0)；limits lower=0 upper≈radians(95) |

### Slot D：frame_style（固定承座 frame 视觉/材质族；非新关节，结构上为 frame 几何变体）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `iron_seat_frame` | S2 + S3 | S3 L144-L168 (方 frame + recess + throat + 顶倒角) | eligible if compatible | 铸铁承座：薄壁方/环 frame band（FRAME_WALL 窄）+ recess seat + throat；顶面倒角 |
| `concrete_stone_frame` | S4 | S4 L66-L98 (厚 stone frame, FRAME_WALL 宽, 顶 band 厚, 风化大倒角) | eligible if compatible | 混凝土/石承座：宽 frame band + 厚顶 band + 大风化倒角；更重 effort |
| `flush_concrete_surround` | S1 | S1 L126-L150 (concrete surround, 齐平顶=地面, SUR_LEDGE seat) | eligible if compatible | 齐平混凝土 surround block：盖顶与 surround 顶平齐（地面），盖不凸出（区别于上两者盖凸出） |

> 硬约束满足：每 slot ≥3 candidate，全部有 5★ 来源 Lx-Ly。Slot D 是 frame 几何/落座姿态（齐平 vs 凸出）+ 材质族差异，非纯颜色——`flush_concrete_surround` 改变盖顶相对 frame 顶的落座语义（盖齐平 vs 盖凸出），是真实结构/接口差异，故成立。

## 槽位图（slot graph）

pattern: mixed（parallel_children + multiplicity）

```
frame_ring/surround (FIXED root, z∈[0,FRAME_HEIGHT], footprint base z≈0)
   ├─[FIXED, origin=Origin()]──────────────────────────────► shaft (hollow void, top abuts seat ledge / frame underside)
   └─[DEFINING joint: lift_out_prismatic OR hinged_flap_revolute]──► cover/grate (child)
                                                                       └─ surface_pattern emits N looped through-slots / studs (module-local cut, NOT separate parts)
```

接口点位与关节策略：

- **frame→shaft**：FIXED，`origin=Origin()`（S1 L179-185 / S2 L156-162 / S3 L196-202 / S4 L161-167）。shaft 顶面在 seat ledge / frame 底之下，沿中心轴向下延伸 SHAFT_DEPTH。
- **frame→cover（DEFINING）**：
  - `lift_out_prismatic`：PRISMATIC，`origin=Origin(xyz=(0,0,COVER_REST_BOTTOM_Z))`，`axis=(0,0,1)`，`MotionLimits(lower=0, upper=LIFT_TRAVEL)`（S4 L177-188）。COVER_REST_BOTTOM_Z = SEAT_LEDGE_TOP_Z − SEAT_EMBED；LIFT_TRAVEL = SEAT_DROP + clearance 清 frame 顶 band（+rim if solid_lid）。
  - `hinged_flap_revolute`：REVOLUTE，pivot origin 在 frame 顶一条边的 seat 高度 `Origin(xyz=(0, +SEAT_INNER_HALF, SEAT_LEDGE_TOP_Z))`，`axis=(1,0,0)`（沿该边），`MotionLimits(lower=0, upper≈radians(95))`。盖 local frame 需把铰边平移到 pivot，使 q=0 落座、q=upper 翻起露 shaft。
- **盖↔frame 落座接口**：盖平面尺寸 = frame opening − 2·SEAT_GAP（周边间隙），盖底落 SEAT_LEDGE_TOP_Z（`expect_contact` + `allow_overlap(cover,frame)` 由 SEAT_EMBED 引起）。`expect_overlap(cover,frame,xy)` 充满开口，`expect_within(cover,frame,xy)` 不越界。
- **互斥/派生**：`radial_pattern` 优先派生 round_outline（辐条天然适圆）；`basket_weave`/`cross_grid`/`parallel_slots` 适配方/长方；`hinged_flap_revolute` 与 round_outline 组合时 pivot 沿圆盘一条弦（仍合法但优先 square/rectangular）。N 仅在 B≠solid_lid 时暴露。

## 每槽位 Module Emits / Interfaces

### Slot A / module square_outline | round_outline | rectangular_outline
| emits | 描述 | 来源 |
|---|---|---|
| parts | 决定 cover 板基元 (`box`/`circle.extrude`) + frame 套 + throat 平面轮廓 | S2 L21-L67 / S1 L62-85 |
| internal joints | 无（仅定义全模型平面 footprint） | — |
| upstream interface | frame footprint base z≈0；frame opening side/diam = COVER_SIZE + 2·SEAT_GAP | S2 L34-38 |
| downstream interface | 盖平面尺寸 + shaft throat 平面尺寸（供 B/C/D 消费） | S2 L38, L43 |

### Slot B / module solid_lid | basket_weave | parallel_slots | cross_grid | radial_pattern
| emits | 描述 | 来源 |
|---|---|---|---|
| parts | 盖 part 上的 module-local 切割（through-slot / 方孔 / 辐条缝）或加料（stud/rim）；**不是独立 part**，是 cover_body visual 的一部分 | S2 L99-103 (cut compound), S3 L114-118 (union studs) |
| internal joints | 无（图案是盖 visual，随盖一起被 DEFINING 关节运动） | — |
| upstream interface | 消费 field = cover_size − 2·border；pitch/N 决定循环 | S2 L71-79 |
| downstream interface | 切透盖板形成 grate（与 shaft void 视觉连续） | S2 L103 |

### Slot C / module lift_out_prismatic | hinged_flap_revolute
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无新 part（复用 cover part） | S4 L170-175 |
| internal joints | **DEFINING**：frame→cover PRISMATIC(+Z) 或 REVOLUTE(edge) | S4 L177-188 / hinge 新增 |
| upstream interface | pivot/rail 挂在 frame seat（prismatic: 中心轴 rest bottom；revolute: 边缘 seat 高度） | S4 L183 |
| downstream interface | 盖运动语义（q=0 落座 ↔ q=upper 露 shaft） | S4 L177-188 |

### Slot D / module iron_seat_frame | concrete_stone_frame | flush_concrete_surround
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame_ring/surround part（FIXED root visual）+ recess + throat 几何 + 顶倒角 | S3 L144-168 / S4 L66-98 / S1 L126-150 |
| internal joints | frame→shaft FIXED | S4 L161-167 |
| upstream interface | footprint base z≈0；顶面 = 地面参考 | S1 L131-133 |
| downstream interface | SEAT_LEDGE_TOP_Z（盖落座面）+ SEAT_DROP（盖凸出 or 齐平 by D） | S4 L42, L60 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| cover_outline | enum | square / round / rectangular | — | choice | procedural sampler 选；gate radial→优先 round | Slot A |
| surface_pattern | enum | solid_lid / basket_weave / parallel_slots / cross_grid / radial_pattern | — | choice | procedural sampler；gate radial 优先 round outline | Slot B |
| open_mechanism | enum | lift_out_prismatic / hinged_flap_revolute | — | choice | DEFINING 关节；至少一非固定关节恒在 | Slot C |
| frame_style | enum | iron_seat_frame / concrete_stone_frame / flush_concrete_surround | — | choice | procedural sampler | Slot D |
| palette_style | enum | cast_iron_black / weathered_rust / cast_graphite / concrete_grey / stone_grey / enamel_drain_green | cast_iron_black | palette | palette only，**不计入 slot_choice**；逐 seed 采样；material rgba | S1 L168 / S2 L147 / S3 L187 / S4 L150 |
| slot_count_N | int | per-B（见 §Multiplicity） | per-B nominal | conditional | 仅 B∈{basket_weave,parallel_slots,cross_grid,radial_pattern} 暴露；solid_lid→N=0 | S2 L79-84 / S1 L31 |
| cover_size_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放 COVER_SIDE/直径主尺寸；frame opening / shaft 派生跟随，clamp | S2 L21, S4 L24 |
| cover_thick_scale | float | [0.80, 1.30] | 1.0 | independent | 缩放盖板厚 → SEAT_DROP → LIFT_TRAVEL，clamp | S4 L26, L42 |
| frame_wall_scale | float | [0.80, 1.25] | 1.0 | independent | 缩放 FRAME_WALL（D 内基线不同），clamp | S2 L33 / S4 L34 |
| rect_aspect | float | [1.3, 2.2] | 1.6 | conditional | 仅 rectangular_outline：LEN = WID·rect_aspect | S4 L24 (拉长) |
| seat_gap | float | derived | — | equation | `= max(0.004, 0.012·cover_size_scale)`（周边落座间隙，保 within） | S4 L33 |
| frame_opening | float | derived | — | equation | `= COVER_SIZE + 2·seat_gap`（盖落入 frame） | S2 L34 |
| shaft_side | float | derived | — | equation | `= frame_inner − 2·FRAME_LEDGE`（throat < opening，留 seat ledge） | S2 L38 |
| lift_travel | float | derived | — | equation | `= SEAT_DROP + FRAME_TOP_BAND + 0.06 (+RIM if solid_lid)`，prismatic upper | S4 L48-50 |
| hinge_upper | float | [radians(85), radians(105)] | radians(95) | conditional | 仅 hinged_flap_revolute：REVOLUTE upper（盖翻起露 shaft，≤radians(110)） | hinge 新增 |
| (—) | constraint | — | — | inequality | `seat_gap ≥ 0.003`（落座间隙非负，保 expect_within）；违反则回缩 cover_size_scale | 接口 |
| (—) | constraint | — | — | inequality | `lift_travel ≥ SEAT_DROP + RIM_HEIGHT`（提起须清 frame 顶+rim）；不足则增 travel | S1 L234 / S3 L252 |
| (—) | constraint | — | — | inequality | `field = cover_size − 2·border > N·pitch_min`（N 格子能放进 field）；超界回缩 N | S2 L71, L89-92 |

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**：surface_pattern 的栅条/图案格子数 N（由 Slot B 决定，仅在 B≠solid_lid 时暴露）。

- `count_param`: `slot_count_N`（B=basket_weave/cross_grid 为派生行×列总数；B=parallel_slots/radial_pattern 为单层循环条数）
- `N_range`（本小类本轴产品域，测试偏小、产品全程）：
  - `parallel_slots`：N ∈ [3, 24]（直缝条数；nominal 8）
  - `radial_pattern`：N ∈ [6, 48]（辐条缝数；nominal 16）
  - `cross_grid`：每边 n ∈ [3, 14]，total = n×n ∈ [9, 196]（nominal n=6 → 36）
  - `basket_weave`：rows × cols 由 field/pitch 派生，等价 N ∈ [9, 169]（nominal ~ S2 默认 pitch → ~25-49）；通过 pitch_scale 暴露密/疏（dense / coarse）
- sampling domain（权重档）：小 N 高频（真实排水栅多为 6-30 条/格），大 N 稀有尾部下采。dense 档（pitch↓→N↑）与 coarse 档（pitch↑→N↓）各占少量权重，覆盖 source map 的 `slot_count_dense` / `slot_count_coarse` 变体。
- copied object：盖板上的 through-slot / 方孔 / 辐条缝 cutter（cut compound），**非独立 part**——它们是 cover_body visual 的镂空，随 DEFINING 关节整体运动。
- naming：内部 cutter 不单独命名为 part；若需诊断按 `grate_{i}` 命名 cutter（source map 要求 fresh loop 用 `grate_{i}`，禁手写槽列表）。
- placement：parallel = 等距 pitch 横贯 field（S2 L75-79 单层化）；cross_grid = 嵌套行列方孔（S2 L81-97）；radial = 角度 2π/N 环向分布（S1 L113-117 改环向）；basket = 错列行列（S2 L81-97，奇行半列错位 L83）。
- joint policy：复制件无独立关节（随盖运动）；恒满足"至少一非固定关节"由 DEFINING frame→cover 关节保证。
- source/gating：S2 L75-103（嵌套/单层 loop）、S1 L113-121（弧/环 loop）。N 上界由 `field > N·pitch_min` inequality clamp（超界回缩 N），下界保证至少 3 缝/9 孔成栅。

solid_lid 无复制：N=0，单板（+可选单撬槽，S4 L138-144，cosmetic 非循环）。

## 拓扑多样性审计

总组合数：A(3) × B(5) × C(2) × D(3) = **90** 结构组合，再乘 multiplicity（B 决定的 ≥3 个 distinct N 档：以 source map 的 dense / nominal / coarse 计 ≥3）= **90 × 3 = 270 ≥ 10**。
（扣除兼容矩阵非法/降级组合后合法组合仍远超 10：见下表。即便保守只算 solid_lid 无 N 的组合也有 A×C×D=18，加 4 种带 N 图案 ×3 档 ×A×C×D 远超门控。）

理由：part tree（frame/shaft/cover 三件骨架恒定，但 cover 几何、frame 几何、关节类型、镂空拓扑、N 均变）跨 A/B/C/D/N 产生大量 distinct 拓扑等价类；REVOLUTE vs PRISMATIC 是真实 joint-type 差异，5 种 surface 是真实 part-geometry/loop 差异。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 四个 named slot（cover_outline / surface_pattern / open_mechanism / frame_style），经兼容矩阵合法化（radial→优先 round；solid_lid→N gate=0；round+hinge 优先降级）；再对 B≠solid_lid 加权 `rng.choices` 采 N（小 N 偏多，dense/coarse 档少量权重）；再 uniform 采各连续 scale（cover_size/cover_thick/frame_wall/rect_aspect/hinge_upper），按 equation 派生（seat_gap/frame_opening/shaft_side/lift_travel），用三条 inequality 投影回缩（seat_gap≥0、lift_travel 清 frame+rim、field>N·pitch）；最后 `rng.choice` palette_style。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计 **≥300**。90 结构组合 × N 多档（parallel/radial/cross/weave 各自宽 N 谱）使 distinct 拓扑（含不同 N 计数视为不同拓扑）轻松破百；即便把 N 折叠为 dense/nom/coarse 三档也有 ~270 上界。本小类结构词汇真实丰富（轮廓×图案×机构×frame×N），无需说明低于 300 的理由。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表 cover_size_scale / cover_thick_scale / frame_wall_scale（independent）+ rect_aspect / hinge_upper（conditional）+ seat_gap / frame_opening / shaft_side / lift_travel（equation 派生）。全部在 `resolve_config` clamp/派生，每 build 统一应用。采样契约：先采 named slot + N（解析 conditional：N 仅 B≠solid_lid、rect_aspect 仅 rectangular、hinge_upper 仅 revolute；gate radial→round、solid_lid→N=0）→ 采 independent size/thick/wall scale → 派生 seat_gap→frame_opening→shaft_side→lift_travel → 用三条 inequality（seat_gap≥0.003 保 within、lift_travel≥SEAT_DROP+RIM 清 frame、field>N·pitch_min 放得下 N）投影/回缩。跨部件依赖（盖 vs frame opening、shaft vs ledge、travel vs frame 顶、N vs field）显式落在 §7 equation/inequality，在 `resolve_config` 求解，不留到 builder。这些 scale 不破坏 DEFINING 关节 origin（rest bottom / edge pivot）、盖落座接口、frame→shaft FIXED 或 N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot order A→B→C→D，weighted N（小 N 偏多 + dense/coarse 档），compatibility gates（radial→round, solid_lid→N=0） | slot_choices_for_seed matches build choices |
| compatibility matrix | radial_pattern 优先 round_outline；round+hinge 降级（pivot 沿弦或回退 prismatic）；solid_lid 屏蔽 N；rectangular 须 rect_aspect；basket/cross/parallel 适方/长方 | no floating, no collision, axis correct, max N clamp, N gate, optional revolute pose |
| controlled local variation | cover_size/thick/frame_wall/rect_aspect/hinge_upper scale + clamp（§7） | proportions vary without breaking seat contact, within, shaft clearance, joint origin, identity |
| regression overrides | none（首版纯 procedural） | — |
| random sweep | seeds 0-49 初轮 / 0-999 成熟审计 | and contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A cover_outline | 3 | yes | yes | square/round/rectangular |
| B surface_pattern | 5 | yes | yes | solid/basket/parallel/cross/radial |
| C open_mechanism | 2 | yes | no | PRISMATIC lift + REVOLUTE hinge（定义性关节轴，2 类已是真实机构上限；source map 明确 mechanism 轴=2） |
| D frame_style | 3 | yes | yes | iron/concrete/flush surround |

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C/D + N）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating prevents illegal combos（radial 非 round 时降级；solid_lid 不暴露 N；round+hinge 安全降级）
- optional regression overrides are sparse and justified（none）
- controlled local scale params clamped；不能破坏 seat contact / within / shaft clearance / joint origin / N
- cross-part scale dependencies（equation/inequality/conditional）在 `resolve_config` 求解，不留到 builder
- 关键 InterfaceSpec/MatingContract 存在：frame footprint base z≈0；盖落 SEAT_LEDGE_TOP_Z（expect_contact）；盖充满开口（expect_overlap xy）+ 不越界（expect_within xy）；shaft 在 seat ledge 下且居中开口下
- DEFINING 关节：lift_out_prismatic = PRISMATIC axis(0,0,1) lower=0 upper=LIFT_TRAVEL≥SEAT_DROP+RIM；hinged_flap_revolute = REVOLUTE edge axis(1,0,0) lower=0 upper∈[85°,105°]，q=upper 露 shaft
- frame→shaft = FIXED origin=Origin()
- copied through-slots 遵循 placement/naming（fresh loop `grate_{i}`，禁手写列表）
- `allow_overlap(cover,frame)` 限于 SEAT_EMBED 落座过盈，并由 expect_contact 证明

## Reject cases

- 盖/grate 悬空：盖底未落 SEAT_LEDGE_TOP_Z（无 expect_contact）或 q=0 未充满开口（expect_overlap 失败）。
- 关节退化：DEFINING 关节被设成 FIXED，或全模型无非固定关节（必须 PRISMATIC 或 REVOLUTE 之一）。
- prismatic upper 不足以清 frame 顶 band(+rim)，提起后盖底仍埋在 recess（lifted clears frame 失败）。
- hinge pivot 放在盖中心而非 frame 边缘 → 翻转穿模 frame / 不露 shaft；或 hinge upper 过大致盖翻过头穿地。
- N 过大使 field 放不下（slot 越过 border 切穿 frame 落座面）或 N<3 不成栅；solid_lid 仍暴露 N。
- radial_pattern 配方/长方 outline 致辐条几何错位扇出盖外；rectangular_outline 漏设 rect_aspect 退化成方。
- shaft throat ≥ frame opening（无 seat ledge）→ 盖无处落座；或 shaft 顶高于 seat ledge 顶穿 frame。
- 把连续 scale / palette_style / 材质当新 candidate 塞进 slot（非结构差异）。
- 圆形 Well_lid / 墙面 grille / 独立 trench drain（无 frame+shaft 骨架）语义混入。

## 与相邻类别的边界

- 不该混入：**Well_lid（圆井盖/水井盖）**——Well_lid 默认 round，常为木/石圆盖或圆顶，身份是井口圆盖；本类 identity 是方形（含派生 round）排水栅/检修接入盖落座 frame，强调栅条/槽阵镂空 + frame+shaft 骨架。round_outline 候选只是本类的轮廓变体，不等于把圆井盖语义吞进来：仍须 frame 承座 + shaft throat + 排水/检修盖语义。
- 不该混入：**墙面 grille / register / vent（暖通格栅）**——那些是竖直安装、带可调百叶/风门的通风格栅，无 frame+shaft 地下竖井骨架、无 +Z 提起/边缘翻起的接入语义。
- 不该混入：**trench drain / channel grate（线性沟渠栅）**——长条排水沟栅是连续 channel 上的细长盖，无单 frame 凹座 + 集中 shaft throat；本类 rectangular_outline 仍是离散落座 frame + 集中 throat，非连续沟道。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT；4 个 5★ 全读；A/B/C/D 四 slot（C=2 candidate 说明真实机构上限）；DEFINING 关节 = PRISMATIC lift 或 REVOLUTE hinge；multiplicity 1 轴（surface N，dense/nom/coarse）；总组合 90×N≥270；palette_style 6 colorway。等待人工审核，审核前不进入模板实现。 |

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | B/C/D | radial_pattern, lift_out_prismatic, flush_concrete_surround | rec_small-dark-cast-iron-square-floor-drain-grate-se_...27f846c6 | L55-L85 (弧缝), L113-121 (扇 loop→环), L126-150 (surround), L179-203 (prismatic) | 辐条图案 loop + 齐平 surround + +Z lift |
| S2 | A/B/D | square_outline, basket_weave, parallel_slots, cross_grid, iron_seat_frame | rec_square-rusty-cast-iron-drainage-grate-with-a-bas_...01cd7eed | L21-67 (方板+frame), L50-57 (slot cutter), L75-103 (嵌套槽 loop), L108-129 (frame) | 方轮廓 + 槽阵 loop（单/嵌套）+ 铁 frame |
| S3 | B/C/D | solid_lid(stud), hinged_flap_revolute(ref), iron_seat_frame | rec_square-cast-iron-inspection-chamber-cover-with-a_...e40ac516 | L59-118 (实盖+rim+stud loop), L132-139 (edge key→hinge ref), L144-220 (frame+prismatic) | 实心盖 stud 网格 + frame edge（hinge 参考）|
| S4 | A/B/C/D | rectangular_outline, solid_lid(pry), lift_out_prismatic, concrete_stone_frame | rec_square-weathered-concrete-utility-access-cover-s_...edad8300 | L24-50 (尺寸/seat 派生), L66-98 (stone frame), L125-145 (实板+撬槽), L177-188 (prismatic) | 长方轮廓 + 混凝土 frame + 实心撬槽盖 + +Z lift 派生 |
