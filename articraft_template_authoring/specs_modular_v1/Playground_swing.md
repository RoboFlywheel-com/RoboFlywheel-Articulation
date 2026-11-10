# Modular Spec — Playground Swing Set

## 元信息
| 项 | 值 |
|---|---|
| slug | `playground_swing_set` |
| template path | `agent/templates/Playground_swing.py` |
| test path (optional) | `tests/agent/test_playground_swing_set_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（3 个结构 slot：frame_type × suspension × seat_type；外加 1 根 multiplicity 轴：swing_count N，及次级 sweep-only chain_link_count） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（2 parents + 6 rating-5 workbench variants） |
| read_count | 8 |
| read_scope | all 5-star samples adopted for this slug (2 converged parents + 6 cell-filling variants) |
| source_index_policy | only adopted module sources are indexed below |

已完整读取 8 个样本的 `model.py`：2 个 converged parent（commercial red-steel A-frame chain swing set；rustic log rope double swing）+ 6 个 rating-5 workbench fork（var_arch / var_hframe / var_rod / var_tire / var_n1 / var_n3）。两 parent 均覆盖 N=2；variant 各填一个 EMPTY 单元格（arch frame、H frame、rigid rods、tire seat、N=1、N=3）。所有样本共享同一骨架：**固定顶梁支架 + N 个 loop-emit 的吊挂秋千座，每座绕顶梁一根 REVOLUTE fore/aft pivot 独立摆动（1 driver + 余 mimic / 各自独立 joint）**。

## 核心身份

`playground_swing_set` 是一台**直立、独立站地的多座儿童游乐场秋千架**：一个可见固定支架（A 字端架 / 原木撇柱 / 单拱 / 直立 H 框）把一根顶梁（top_rail / crossbeam）撑到 ~2.0–2.4 m 高，N 个相同的吊挂秋千座沿顶梁等距悬挂，每座是一根刚性钟摆（chains / ropes / rods 吊挂 + 座面），绕顶梁轴上的 REVOLUTE pivot 前后摆动，座间运动相互独立。成熟默认域应保持 park-equipment 比例（顶梁 ~3 m 宽、~2.4 m 高、~1.6 m 脚距），有真实落地脚 + 底板、可见顶梁、吊点五金、吊挂件、座具和 fore/aft 摆轴。

**与相邻 slug 的区别（重要）**：
- 不同于 `wood_swing`：那是**单座花园/门廊 glider 长椅**（garden/porch swing bench），识别是「A 架/花架 + 一个对坐长凳/daybed 前后摆」，常带顶棚（canopy/pergola），是 furniture-like。`playground_swing_set` 是**直立多座游乐场框**，无顶棚，强调 N 座独立钟摆 + 儿童座（belt/plank/tire）。
- 不同于 `playground_swing`（一个更宽的总类 slug，含 multi-station wide frame + glider/platform/nest/disc 等复杂 payload）：本 slug **窄而专**，只做「固定 overhead frame + N 个同构吊挂座的标准秋千阵列」，不引入 multi-station-per-bay recipe、parallelogram glider、平台、nest basket 或 swivel 两级关节。座是单一同构的 multiplicity，不是 per-station 异构 recipe。

不该混入：单座婴儿桶秋千（toddler bucket，单座专用产品）、吊床（布吊无刚架钟摆）、跷跷板、滑梯。

## 槽位 + 候选模块表

### Slot A：frame_type（固定支架 — 承 top rail + swing pivots）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `red_steel_A_frame` | rec_model-a-commercial-playground-swing-set-with-a-g_…83c0a0b1 | L116-L143（`_add_a_frame_end`）, L214-L224（root `frame`/`top_rail`） | eligible if compatible | 红钢方管 A 字端架：每端两条外撇斜腿（`end_i_leg_{0,1}`，tilt=atan2(FOOT_Y, APEX_Z−FOOT_Z)）+ 上下横撑（upper 1.35 / lower 0.60）+ 4 块带孔底板 + Box 顶梁；root part，顶梁下提供沿 X 的 pivot line。 |
| `rustic_log_frame` | rec_model-a-rustic-playground-double-swing-built-fro_…4094e053 | L88-L150（splayed posts + 横梁 + finials） | eligible if compatible | 圆木撇柱：两对外撇 log post（`post_{pair}_{i}`，pitch=atan2(±dx, POST_TOP_Z)）+ 顶部绳箍 lashing band ×2/对 + 一根横置 log `crossbeam`（rpy=(π/2,0,0)）+ 4 个 brass finial（stem/ball/tip）；root part，pivot 沿 Y。 |
| `single_arch_frame` | rec_pswg_var_arch | L100-L122（`_arch_geometry`）, L144-L160（`_add_arch_end`） | eligible if compatible | 单倒-U 拱：每端一根 half-ellipse swept tube（YZ 平面，foot→apex→foot，`tube_from_spline_points`）跨越摆区，落地脚 + 底板；无外撇斜腿/横撑，顶梁仍为 Box top_rail。 |
| `straight_H_frame` | rec_pswg_var_hframe | L116-L144（`_add_h_frame_end`） | eligible if compatible | 直立 H 框：每端两条**竖直无外撇** Box post（`end_i_post_{0,1}`，POST_HALF_Y=0.45）+ 上下横撑（1.50 / 0.65）+ 底板；窄脚距（~1.0 m），顶梁 Box top_rail。 |

> single-candidate degrade：无（A=4）。frame 候选间 part 数、leg 数、leg 倾角、tube 几何（Box vs swept tube vs Cylinder）、脚距与横撑拓扑均不同，非纯尺寸/材质差异。

### Slot B：suspension（吊挂机构 — 核心 fore/aft REVOLUTE pendulum）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `oval_link_chains` | rec_model-a-commercial-playground-swing-set-with-a-g_…83c0a0b1 | L65-L79（`_oval_link_geometry`）, L180-L189（链节 loop）, L198-L207（pivot REVOLUTE） | eligible if compatible | 每座两条镀锌 oval 链：`for k in range(N_LINKS)` loop-emit `chain_c_link_k`（交替 yz/xz 朝向，pitch>2(A−R) 互穿 ~2 mm），顶链节坐在 clevis `hanger_pin` 上（captured-pin）；REVOLUTE 轴沿梁 (1,0,0)。 |
| `tapered_ropes` | rec_model-a-rustic-playground-double-swing-built-fro_…4094e053 | L160-L200（rope cone + rings + knots）, L246-L256（REVOLUTE） | eligible if compatible | 每座两条 tan 锥形麻绳（`cq.Solid.makeCone` 上粗下细）+ 绕梁 wrap ring（washer，snug 2 mm 嵌）+ 多个 knot（top/mid×2/seat）；rope ring 抱 crossbeam（allow_overlap + expect_contact）；REVOLUTE 轴沿梁 (0,1,0)。 |
| `rigid_rods` | rec_pswg_var_rod | L164-L194（`_add_swing`：直 Cylinder rod + clamp + REVOLUTE） | eligible if compatible | 每座两根直钢杆 `rod_i`（Cylinder，ROD_LENGTH≈1.485 m，无链节循环）从 hanger_pin 直插到 clamp 顶；rod 顶 captured 在 pin 上；REVOLUTE 轴沿梁 (1,0,0)。part 数远少于链。 |

> single-candidate degrade：无（B=3）。三者 part-count 与几何拓扑差异大：N_LINKS 个 loop 链节 vs 锥绳+ring+knots vs 单根 Cylinder；均保留顶端 REVOLUTE pendulum。

### Slot C：seat_type（座面 — fixed 到 driver 吊挂件，整座作 pendulum）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `rubber_belt_seat` | rec_model-a-commercial-playground-swing-set-with-a-g_…83c0a0b1 | L97-L113（`_seat_belt_geometry`）, L190-L196（clamp + belt） | eligible if compatible | 下垂橡胶带座：`sweep_profile_along_spline` 沿 X 扫成浅 U（SEAT_SAG=0.113），两端被 `clamp_c` Box 夹在两吊挂件下端；软带，无靠背。 |
| `plank_seat` | rec_model-a-rustic-playground-double-swing-built-fro_…4094e053 | L74-L76（`_seat_plank` chamfer）, L202-L242（seat + back_rail + corner fittings） | eligible if compatible | 木板座：chamfered Box `seat_plank` + 两短柱 + 一根 `back_rail`（Cylinder rpy=(π/2,0,0)）+ 4 个 brass corner fitting；硬板带靠条。 |
| `tire_seat` | rec_pswg_var_tire | L80-L89（`_tire_attachment_points`）, L226-L233（`TorusGeometry` 水平胎） | eligible if compatible | 水平吊轮胎：`TorusGeometry`（major 0.22 / tube 0.065）平躺（axis Z），4 根 converging rope 从 pivot 汇聚到胎面 4 点 + stopper knots；无 belt/plank/back_rail/corner。 |

> single-candidate degrade：无（C=3）。座 primitive 家族不同（swept belt vs chamfered plank+rail vs flat torus），part 树和接口（两侧 clamp / 四角 fitting / 多绳汇聚）不同。

## 槽位图（slot graph）

pattern: `mixed`（multiplicity 主导 + 3 slot 串联）

```text
[Slot A frame_type]  (A_frame / rustic_log / single_arch / straight_H)
   └─ top_rail / crossbeam underside ── top pivot line（沿梁 X 或 Y，等距 N 个 pivot socket）
        └─ [Slot B suspension]  oval_link_chains | tapered_ropes | rigid_rods
              └─ swing_i_pivot (REVOLUTE, fore/aft)  ── lower hanger ends / seat clamps / tire anchors
                    └─ [Slot C seat_type]  rubber_belt | plank | tire   (FIXED 到 driver 吊挂件，整座作钟摆)
```

跨 slot 接口点位：
- `frame.downstream.top_pivot_line`：顶梁下方一条沿梁的 pivot line，frame 沿梁等距生成 `swing_count` 个 swing center 与每座两个 hanger socket（`hanger_pin` / 绕梁 wrap-ring 锚点 / rod pin）。world origin、axis 由 frame module 导出（A/arch/H 用 axis (1,0,0) z≈2.228；rustic_log 用 axis (0,1,0) z=BEAM_Z）。
- `suspension.upstream`：消费 top pivot line，为每座创建一根 `swing_i_pivot` REVOLUTE（chains/rods）或 `beam_to_swing_i`（ropes）。chains/rods 顶端 captured 在 `hanger_pin`（element-scoped allow_overlap）；ropes 用 wrap ring snug 抱 crossbeam（allow_overlap + expect_contact）。
- `suspension.downstream.lower_payload_interface`：两侧吊挂下端（chain clamp / rope seat knot / rod clamp）或 tire 的多绳汇聚锚点。
- `seat.upstream`：座必须与 lower interface 可见接触并 fixed 进同一 swing part（整座是单刚性钟摆 link）；不允许浮空。

兼容性 gate：
- A/B/C 三槽**两两全兼容**（任意 frame 出 top pivot line → 任意 suspension 顶端挂梁 → 任意座挂吊挂下端）。唯一需注意的是 pivot **axis 方向**由 frame 几何决定（A/arch/H = 沿 X；rustic_log 横梁 = 沿 Y），suspension/seat 的 local frame 须按 frame 导出的 axis 旋转对齐 —— 这是 builder 内部坐标统一，不是非法组合。
- `tire_seat` 用 4 绳汇聚到 pivot，天然适配任意 suspension 顶端（它自带绳，suspension 仅提供顶 REVOLUTE）；当 B=oval_link_chains/rigid_rods 时按「双吊挂 + 横置 tire」或「绳汇聚」二选一实现（推荐保留 tire 自带的 4-rope 汇聚以匹配 var_tire 源拓扑）。
- 无互斥对；无可选 moving child（座始终存在且摆动）。

## 每槽位 Module Emits / Interfaces

### Slot A / module `red_steel_A_frame`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `frame`：`top_rail` Box + 每端 2 外撇 leg + 上下横撑 + 4 底板 | S1 / model.py:L116-L143, L214-L224 |
| internal joints | none | S1 / model.py:L116-L143 |
| upstream interface | root ground support（底板落地 z≈0），无 parent | S1 / model.py:L131, L298-L301 |
| downstream interface | 顶梁下 pivot line z=PIVOT_Z=2.228，axis (1,0,0)，沿 X 等距 `hanger_pin` sockets | S1 / model.py:L146-L172, L198-L207 |

### Slot A / module `rustic_log_frame`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `log_frame`：4 splayed log post + 4 lashing band + log `crossbeam`（Cylinder 横置）+ 12 brass finial 段 | S2 / model.py:L88-L150 |
| internal joints | none | S2 / model.py:L88-L150 |
| upstream interface | root ground support（撇柱最低缘落地） | S2 / model.py:L98-L106 |
| downstream interface | crossbeam 轴 z=BEAM_Z=1.95，axis (0,1,0)，沿 Y 等距 swing pivot；座用 wrap-ring 抱梁 | S2 / model.py:L116-L122, L246-L256 |

### Slot A / module `single_arch_frame`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `frame`：每端一根倒-U swept arch tube + 2 底板 + Box `top_rail` | S3 / model.py:L100-L122, L144-L160 |
| internal joints | none | S3 / model.py:L144-L160 |
| upstream interface | root ground support（arch 脚落地 z≈FOOT_Z） | S3 / model.py:L154-L160, L347-L351 |
| downstream interface | 同 A_frame：pivot line z=2.228 axis (1,0,0)，hanger_pin 沿 X | S3 / model.py:L163-L189 |

### Slot A / module `straight_H_frame`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `frame`：每端 2 竖直 Box post（无外撇）+ 上下横撑 + 4 底板 + Box `top_rail` | S4 / model.py:L116-L144 |
| internal joints | none | S4 / model.py:L116-L144 |
| upstream interface | root ground support（post 落地） | S4 / model.py:L131-L136, L293-L297 |
| downstream interface | pivot line z=2.228 axis (1,0,0)，hanger_pin 沿 X | S4 / model.py:L147-L173 |

### Slot B / module `oval_link_chains`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 每座两条链：`chain_c_top_link` + `chain_c_link_k`（k=1..N_LINKS-1，shared oval mesh，交替朝向）+ 两个 `clamp_c` | S1 / model.py:L65-L79, L180-L195 |
| internal joints | none inside child；每座 1 `swing_i_pivot` REVOLUTE | S1 / model.py:L198-L207 |
| upstream interface | 顶链节 captured 在 `hanger_pin`（allow_overlap + expect_contact） | S1 / model.py:L251-L278, L315-L318 |
| downstream interface | clamp 夹座两端 | S1 / model.py:L190-L196 |

### Slot B / module `tapered_ropes`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 每座两条 cone rope `rope_i` + 两 wrap `rope_ring_i` + knots（top/mid×2/seat） | S2 / model.py:L160-L200 |
| internal joints | 每座 1 `beam_to_swing_i` REVOLUTE，axis (0,1,0) | S2 / model.py:L246-L256 |
| upstream interface | wrap ring snug 抱 crossbeam（allow_overlap + expect_contact） | S2 / model.py:L273-L289 |
| downstream interface | 绳底 seat knot 落在 plank 上 | S2 / model.py:L195-L209 |

### Slot B / module `rigid_rods`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 每座两根直 Cylinder `rod_i`（ROD_LENGTH≈1.485）+ 两个 `clamp_i` | S5 / model.py:L164-L182 |
| internal joints | 每座 1 `swing_i_pivot` REVOLUTE，axis (1,0,0) | S5 / model.py:L185-L194 |
| upstream interface | rod 顶 captured 在 `hanger_pin`（allow_overlap + expect_contact） | S5 / model.py:L230-L246, L300-L309 |
| downstream interface | clamp 夹座两端 | S5 / model.py:L176-L182 |

### Slot C / module `rubber_belt_seat`
| emits | 描述 | 来源 |
|---|---|---|
| parts | swept `seat_belt`（浅 U sag），被两 `clamp_c` 夹 | S1 / model.py:L97-L113, L196 |
| internal joints | none beyond swing pivot | S1 / model.py:L198-L207 |
| upstream interface | 两侧 clamp 下端 | S1 / model.py:L190-L196 |
| downstream interface | 无下游 slot | S1 / model.py:L97-L113 |

### Slot C / module `plank_seat`
| emits | 描述 | 来源 |
|---|---|---|
| parts | chamfered `seat_plank` + 2 rail post + `back_rail` + 4 corner fitting | S2 / model.py:L74-L76, L202-L242 |
| internal joints | none beyond swing pivot | S2 / model.py:L246-L256 |
| upstream interface | 绳底 seat knot 接触 plank | S2 / model.py:L195-L209 |
| downstream interface | 无下游 slot | S2 / model.py:L202-L242 |

### Slot C / module `tire_seat`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 水平 `tire_seat`（TorusGeometry）+ 4 converging rope + stopper knots + hanger knot | S6 / model.py:L199-L233 |
| internal joints | none beyond swing pivot | S6 / model.py:L236-L246 |
| upstream interface | 4 绳从 pivot 汇聚（rope ring 抱梁） | S6 / model.py:L80-L89, L192-L224 |
| downstream interface | 无下游 slot | S6 / model.py:L226-L233 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `frame_type` | enum | `red_steel_A_frame`, `rustic_log_frame`, `single_arch_frame`, `straight_H_frame` | — | choice | 由 deterministic procedural sampler 选择；决定 root part、pivot axis（X 或 Y）、落地脚拓扑 | Slot A table |
| `suspension` | enum | `oval_link_chains`, `tapered_ropes`, `rigid_rods` | — | choice | 由 sampler 选择；决定吊挂 part 树与顶端 captured 方式（pin vs wrap ring） | Slot B table |
| `seat_type` | enum | `rubber_belt_seat`, `plank_seat`, `tire_seat` | — | choice | 由 sampler 选择；决定座 primitive 家族与下端接口 | Slot C table |
| `palette_style` | enum | `red_steel_galv_rubber`, `natural_log_tan_rope_brass`, `arch_blue_galv`, `green_steel_tire`, `weathered_cedar_rope`, `safety_yellow_steel` | `red_steel_galv_rubber` | palette only | 仅改材质 rgba，非结构轴；≥3（本表 6 个） | parent 材质 + variant |
| `swing_count` | int | `[1, 4]`（产品域；样本覆盖 1,2,3） | `2` | multiplicity | N 座沿顶梁等距；权重档见 Multiplicity 节；frame 顶梁/脚距随 N 派生 | S(n1) L45-L50, S(n3) L31-L60 |
| `chain_link_count` | int | per-chain `[8, 40]`（仅 `oval_link_chains` 用） | `34` | conditional | 仅当 suspension=oval_link_chains 时有效；sweep-only，loop-emit，链总长 = HANG_DROP+(N-1)·LINK_PITCH 须 ≈ drop | S1 / model.py:L54, L180-L189 |
| `rail_length_m` | float | derived `[2.4, 5.0]` | `3.0` | equation | `= 2·end_margin + (swing_count−1)·swing_spacing + swing_footprint`；N 越多越宽 | S(n3) L38, L52-L60 |
| `end_apex_x_m` | float | derived `[1.2, 2.2]` | `1.38` | equation | `= rail_length/2 − end_inset`；N=2→1.38、N=3→1.68（源实测） | S(n3) L40 |
| `swing_spacing_m` | float | `[0.70, 0.95]` | `0.80` | independent | 相邻座中心距；采样后 clamp，再驱动 rail_length | S(n3) L48 |
| `frame_scale` | float | `[0.92, 1.10]` | `1.0` | independent | 整架等比缩放（高/宽/脚距同缩），clamp；不破坏 pivot/接口 | parents 比例 |
| `hanger_drop_m` | float | `[1.30, 1.65]` | `1.485` | independent | 顶 pivot 到座的垂向吊挂长度；驱动链节数/绳长/杆长 | S1 L60-L63, S5 L66-L67 |
| `swing_limit_rad` | float | `[0.7, 1.0]` | `1.0` | independent | fore/aft 摆幅；clamp 保证 full travel 不触地 | S1 L206, S2 L56-L58 |
| `pivot_axis` | vector | `(1,0,0)` 或 `(0,1,0)` | derived | conditional | 由 frame_type 导出：rustic_log→(0,1,0)，其余→(1,0,0) | S1 L204, S2 L252 |
| (—) | constraint | — | — | inequality | `swing_footprint·swing_count + (swing_count−1)·gap + 2·end_margin = rail_length`；座间不互穿，违反时缩 spacing 或拒采 | 接口 / clearance |
| (—) | constraint | — | — | inequality | full-travel floor clearance：座 zmin@(±swing_limit) > 0；违反时回缩 swing_limit 或抬 pivot | S2 L352-L360 |

连续尺寸采样契约：先采 independent（swing_spacing / frame_scale / hanger_drop / swing_limit）→ 按 equation 派生 rail_length / end_apex_x → 用 inequality 投影座间距与落地间隙（违反回缩 spacing / swing_limit 或拒采）→ 按 frame_type 解析 pivot_axis（conditional）。

## Multiplicity / Copy Logic

本 slug 有 **1 根主 multiplicity 轴（swing_count）+ 1 根次级 sweep-only 轴（chain_link_count）**。

### 轴 1：swing_count（主轴）
- `count_param`：`swing_count`
- `N_range`：`[1, 4]`（产品域；测试偏小 1–2，产品全程到 4。样本实测覆盖 1(var_n1) / 2(parents) / 3(var_n3)，N=4 由构造安全外推）
- sampling domain（权重档）：小 N 高频 —— 例 N=2 ≈40%、N=1 ≈25%、N=3 ≈25%、N=4 ≈10%（人工审核后定）。
- copied object：一整座吊挂秋千 = suspension 实例（两侧 chains/ropes/rods + clamps/rings/knots）+ seat 实例 + 该座的 `swing_i_pivot` REVOLUTE + 顶梁上该座的两个 hanger 五金（pin / wrap socket）。
- naming：`for i in range(swing_count)` → part `swing_{i}`；joint `swing_{i}_pivot`（chains/rods）或 `beam_to_swing_{i}`（ropes）；座内元素 `chain_c_link_k` / `rod_i` / `rope_i` / `clamp_i` / `seat_belt` 等。hanger 五金 `hanger_pin_{2i}` / `hanger_pin_{2i+1}`。
- placement：座沿顶梁等距，`swing_center_i = (i − (N−1)/2)·swing_spacing`（源 var_n3 公式）；每座两侧 hanger 锚在顶梁，`x = swing_center ± CHAIN_DX`。frame 顶梁长度与 end_apex_x 随 N 派生加宽（rail_length/end_apex_x equation）。
- joint policy：每座拥有自己独立的 REVOLUTE fore/aft pivot（轴由 frame_type 导出，沿梁 X 或 Y）；座 fixed 进单一刚性 pendulum part。1 driver + 余 mimic（multiplier 1.0）**或**各座各自独立 joint（源中各 swing 是完全独立 joint，互不联动）—— 优先各自独立以匹配源「independence」测试。
- source/gating：var_n1 / parents / var_n3 提供 N=1/2/3 的 frame 加宽与等距布座源模式。N=4 由同一公式外推；frame 须按 N 加宽顶梁与端架，不得只拉长无支撑横梁（端架始终在两端落地）。

### 轴 2：chain_link_count（次级，sweep-only，conditional）
- `count_param`：`chain_link_count`（每链节数）
- `N_range`：`[8, 40]`（parent loop-emit 34）
- 仅当 `suspension == oval_link_chains` 时有效（conditional gate）；ropes/rods 无此轴。
- copied object：`chain_c_link_k`（shared oval mesh，交替 yz/xz 朝向，pitch>2(A−R) 互穿 ~2 mm）。
- joint policy：链整体随座作钟摆，链节间无独立 joint（顶链节 captured 在 pin）。
- 仅由模板采样器/sweep 扫，**不专门 fork**。

## 拓扑多样性审计

总 slot 组合数：A(4) × B(3) × C(3) = **36** 纯 slot 组合。
计入 multiplicity：× swing_count N∈[1,4]（4 档）= **144** topology 级组合（次级 chain_link_count 仅尺寸级，不计入 topology）。


理由：候选不仅改尺寸，还改 part count（链 N_LINKS 节 vs 4 绳 vs 2 杆）、座 primitive 家族（swept belt / chamfered plank+rail / flat torus）、frame leg 拓扑（外撇斜腿 / 撇木柱 / 倒-U 拱 / 竖直 H）、pivot axis（X vs Y）、joint 数（= swing_count）。N=1..4 直接改 joint count 与 part 树规模，是真实 topology 轴而非纯 beam 拉伸。36 slot 组合 × 多 N → 远超 10 distinct。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 用 deterministic procedural sampling：先采 frame_type → suspension → seat_type → swing_count（加权）→ palette_style → 连续 scale（independent→equation→inequality→conditional）。`seed=0` 不特殊。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别真实词汇 36 slot × 4 N = 144 topology 上界，distinct 目标定 **≥80**（受类别真实词汇约束，低于 300 因这是窄而专的标准秋千阵列，无 multi-station/glider/platform 复杂 payload —— 这是与 `playground_swing` 总类 slug 的有意分工）。

Procedural Sampling / Sweep Plan：sampler 先选 3 个结构槽（两两全兼容，无 gate 拒绝），再加权采 swing_count，再 palette，再连续 scale。pivot_axis 由 frame_type 解析；连续尺寸按契约求解并 clamp，全部在 `resolve_config` 内完成，不留到 builder 失败。Regression overrides 默认无。Random sweep：`uv run articraft template sweep-pipeline playground_swing_set`，cumulative seeds 0 / 0-4 / 0-19 / 0-49（验收）→ 0-999（成熟审计）检查 build、MatingContract、joint origin/axis/range、support、collision、。机械通过后 viewer 目检随机一小批，重点看类别身份、N 座等距、落地脚、full-travel floor clearance、captured-pin / wrap-ring 接口、tire 水平姿态。

Controlled local parameterization：初版应含 `swing_spacing_m`、`frame_scale`、`hanger_drop_m`、`swing_limit_rad`（independent）+ 派生 `rail_length_m`、`end_apex_x_m`（equation）+ conditional `pivot_axis` / `chain_link_count`。取值范围与 clamp 见第 7 节；不破坏 top_pivot_line 接口、captured-pin 间隙、joint origin/axis/range 或类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | frame→suspension→seat→swing_count(加权)→palette→连续 scale；slot_choices_for_seed 与 build 一致 | slot_choices_for_seed matches build choices |
| compatibility matrix | A/B/C 两两全兼容；唯一耦合是 pivot_axis 由 frame_type 导出（坐标统一，非拒绝）；无互斥对 | no floating, collision, axis, max multiplicity |
| controlled local variation | swing_spacing/frame_scale/hanger_drop/swing_limit clamp + rail_length/end_apex_x 派生 | proportions vary without breaking interfaces, clearance, pivot axis, identity |
| regression overrides | none | previously failed or reviewer-selected only |
| random sweep | seeds 0-49 initial, 0-999 maturity | and contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A frame_type | 4 | yes | yes | A 架 / 撇木柱 / 单拱 / H 框，leg 拓扑与 pivot axis 不同 |
| B suspension | 3 | yes | yes | 链节 loop / 锥绳+ring / 直杆，part-count 与顶端 captured 不同 |
| C seat_type | 3 | yes | yes | belt / plank+rail / tire，座 primitive 家族不同 |
| swing_count | 4 | yes | yes | N∈[1,4]，直接改 joint count 与 part 树 |

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names；A/B/C 两两兼容，无非法组合。
- `swing_count` 在 `[1, 4]`；frame 顶梁/脚架按 N 加宽，端架始终落地（不出无支撑长梁）。
- 每座创建独立 `swing_{i}_pivot`（或 `beam_to_swing_{i}`）REVOLUTE，轴由 frame_type 导出（A/arch/H 沿 X，rustic_log 沿 Y），各座运动相互独立（独立 joint）。
- `oval_link_chains` 用 `for k in range(chain_link_count)` loop-emit 链节（非手写堆叠）；顶链节 captured 在 hanger_pin。
- `tapered_ropes` 的 wrap ring snug 抱 crossbeam（element-scoped allow_overlap + expect_contact）。
- `rigid_rods` 顶端 captured 在 hanger_pin；rod 是单 Cylinder（非链）。
- 每座座体 fixed 进单一 pendulum part，与 lower interface 可见接触，无浮空。
- full-travel floor clearance：座 zmin@(±swing_limit) > 0。
- captured pin / wrap ring overlap 只用 element-scoped allow_overlap（hanger_pin↔top_link/rod、crossbeam↔rope_ring）。
- 连续 scale 在 `resolve_config` clamp / 派生（rail_length/end_apex_x = f(swing_count, spacing)），不留到 builder 失败。

## Reject cases

- 座不摆（REVOLUTE 降 FIXED）→ 变固定多座长凳，拒收。
- 读成 `wood_swing`（单座花园 glider 长椅 + 顶棚）→ 出小类身份。
- 引入 multi-station 异构 recipe / glider / platform / nest / swivel 两级关节 → 越界到 `playground_swing` 总类，不属本 slug。
- `swing_count>1` 却把多座做成一个 part 只暴露一个 joint → 假多重性。
- 顶梁随 N 拉长却不在两端落地或不加宽端架 → 无支撑长梁。
- 链/绳手写堆叠不 loop-emit → 违反 copy-logic。
- 座浮空 / 顶端未 captured 在 pin 或 wrap ring 未抱梁 → 无支撑路径。
- 把 belt/plank/tire 当成同一座 mesh 的颜色/尺寸变体 → 非结构 candidate。
- palette_style / frame_scale 当独立 candidate → 非结构差异。
- tire 立着（axis 非 Z）当成垂直胎秋千 → 与 var_tire 水平胎源拓扑不符。

## 与相邻类别的边界

- 不该混入：`wood_swing`（garden/porch glider 长椅：单座对坐/长凳/daybed + 常带 canopy/pergola，furniture-like，非直立多座游乐场框）。
- 不该混入：`playground_swing`（更宽的总类 slug，含 multi-station wide frame、glider/platform/nest/disc 复杂 payload；本 slug 是其中「标准 overhead frame + N 同构吊挂座」的窄子集，不引入异构 station recipe）。
- 不该混入：单座 toddler bucket / baby swing（单座深桶安全座专用产品，非多座阵列）。
- 不该混入：`hammock`（布吊于两支撑间，无刚架顶梁 pivot 五金）。
- 不该混入：`seesaw` / `playground_slide`（中心支点跷板 / 静态滑道，无 overhead 吊挂钟摆）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY draft from 2 converged parents + 6 rating-5 workbench variants（var_arch/hframe/rod/tire/n1/n3）；3 slots A(4)×B(3)×C(3) + swing_count N[1,4] multiplicity；awaiting human review before template implementation. |

## 模板实现备注（可选）
- `resolve_config` 统一从 frame module 导出 `pivot_axis`、`pivot_z`、`swing_centers`、`hanger_xs`；suspension/seat 不直接猜 frame 尺寸，按导出值挂接。
- `InterfaceSpec` 应含 `top_pivot_line`（沿梁等距 N 个 pivot socket）+ `hanger_socket`（pin 或 wrap-ring）两类。
- `MatingContract`：顶端 captured 接触须可见 —— oval_link_chains/rigid_rods 顶端 ↔ hanger_pin；tapered_ropes wrap ring ↔ crossbeam。
- element-scoped allow_overlap：`hanger_pin_*`↔`chain_*_top_link`/`rod_*`、`crossbeam`↔`rope_ring_*`、链节↔链节（相邻互穿）。
- pivot_axis：rustic_log 横梁沿 Y → axis (0,1,0)；A/arch/H 顶梁沿 X → axis (1,0,0)。suspension local frame 须按此旋转，否则摆动方向错。
- swing_count 加宽：rail_length / end_apex_x 用 var_n3 公式派生（N=2→1.38, N=3→1.68），端架两端落地。
- chain_link_count 与 hanger_drop 联动：链总长 ≈ HANG_DROP + (chain_link_count−1)·LINK_PITCH 须 ≈ hanger_drop，否则座高漂移。

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | red_steel_A_frame / oval_link_chains / rubber_belt_seat | rec_…_83c0a0b1 (commercial) | L65-L318 | A 架 + 链节 loop + captured pin + 下垂带座 + N=2 等距布座 |
| S2 | A/B/C | rustic_log_frame / tapered_ropes / plank_seat | rec_…_4094e053 (rustic) | L60-L256 | 撇木柱 + 横梁 + wrap-ring 锥绳 + 木板座+靠条 + Y 轴 pivot |
| S3 | A | single_arch_frame | rec_pswg_var_arch | L100-L160 | 倒-U swept arch tube frame |
| S4 | A | straight_H_frame | rec_pswg_var_hframe | L116-L144 | 直立无外撇 H 框 |
| S5 | B | rigid_rods | rec_pswg_var_rod | L164-L194 | 直 Cylinder 刚杆吊挂 + captured pin |
| S6 | C | tire_seat | rec_pswg_var_tire | L80-L233 | 水平 TorusGeometry 胎座 + 4 绳汇聚 |
| S7 | mult | swing_count N=1 | rec_pswg_var_n1 | L45-L50 | 单座居中布置 |
| S8 | mult | swing_count N=3 | rec_pswg_var_n3 | L31-L60 | 3 座等距 + rail/apex 随 N 加宽公式 |
