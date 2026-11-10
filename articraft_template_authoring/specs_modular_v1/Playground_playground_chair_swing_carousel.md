## 元信息
| 项 | 值 |
|---|---|
| slug | `playground_chair_swing_carousel` |
| template path | `agent/templates/Playground_playground_chair_swing_carousel.py` |
| test path (optional) | `tests/agent/test_playground_chair_swing_carousel_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：核心是 `multiplicity`（绕中央 rotor 等角复制 N 个臂+座 station），叠加 `linear_chain`（base_form → rotor → arm_structure → seat），并在 rotor 上挂多个 `parallel_children`（N 个 seat）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples adopted for this template (2 converged parents + 7 rating-5 workbench variants) |
| source_index_policy | only adopted module sources are indexed below |

已完整读取本类别 9 个 5 星样本的 `model.py`（2 个 converged parents + 7 个 rating-5 workbench fork variants），以及 source map `Playground__Playground_playground_chair_swing_carousel.md`。样本覆盖：
- Parent A “old”（rec_…e48c2551）：圆盘外撇腿底座、8 根 spline-tube X-lattice 曲管臂、板条桶座 + 环抱弯管护栏；rust_red/cream 配色；用 `tube_from_spline_points` / `mesh_from_cadquery`。
- Parent B “weathered”（rec_…82f97e28）：方板底座 + 四地脚螺栓、白柱 + 2 道 rust band、4 根直辐射臂 + 8 根 X-truss 撑 + clevis 端、平板座 + 简单靠背；纯 Box/Cylinder；white+blue/yellow 配色。
- 7 个 variant 各填一个 EMPTY cell：pedestal（LatheGeometry 单中央粗柱→大圆盘底脚）、tripod（3 撇腿 + 中央毂）、cantilever（单根锥形悬臂 frustum）、chainhung（顶毂方环 + 双链垂挂钟摆）、bucket（深包围 CadQuery 桶座 + lap bar）、n2（SEAT_COUNT=2，180° 间隔）、n6（SEAT_COUNT=6，60° 间隔）。

未采纳的非结构差异（纯配色 / 纯比例 / 同拓扑跨轴组合）只作为审计输入，不进入 module source table。

## 核心身份

`playground_chair_swing_carousel` 是一台**带动力的座椅旋转秋千（chair-swing carousel / wave swinger 的游乐场小型版）**。核心身份是：地面有一个固定 `base_form`（圆盘撇腿 / 方板 / 单柱 pedestal / 三脚架），中央立柱顶端有一个 `rotor`（hub sleeve + cap）通过**一个 CONTINUOUS Z 关节**绕柱旋转；rotor 上沿等角（`360/N`）伸出 N 套 `arm_structure`（直辐射臂 / spline-tube 桁臂 / 单悬臂 / 顶环吊链），每套臂端有一个**水平切向 REVOLUTE 关节**让一把座椅（`seat_type`：平板 / 板条桶 + 护栏 / 深桶 + lap bar）整体向外/向内摆荡（±~30°）。成熟默认域：直径约 2–3.5 m、立柱高约 1.1–1.6 m、座面悬于地面之上约 0.5 m 的 park-equipment 比例；必须有真实落地底座、可见 rotor bearing、N 套臂、N 把摆动座椅，以及 1 个旋转 + N 个摆动的关节语义。

不应混入的相邻类别见 §「与相邻类别的边界」（merry-go-round 旋转木马、plain playground swing 普通秋千、Ferris wheel 摩天轮）。

## 槽位 + 候选模块表

### Slot A：base_form（地面固定底座 — 承中央立柱 + CONTINUOUS spin rotor）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `square_slab_base` | rec_model-a-weathered-four-seat-playground-chair-swi_20260610_085325_366519_82f97e28 | L57-L94 | eligible if compatible | 方形 Box `base_plate`（0.55×0.55×0.05）+ 四角 `anchor_bolt_i` 地脚螺栓 + 白柱 `column_shaft` + `column_base_collar` + 2 道 rust band；纯 Box/Cylinder，柱顶提供 spin 接口。 |
| `splayed_leg_base` | rec_model-an-old-four-seat-playground-chair-swing-ca_20260610_085340_162128_e48c2551 | L71-L102 | eligible if compatible | 圆盘 `base_plate`（Cylinder r=0.17）+ rust_red `column_shaft` + `bearing_collar` + 顶端 `spindle` 螺杆 + 六角 `spindle_nut`（mesh_from_cadquery）；柱顶 bearing collar 提供 spin 接口。注：源里底盘是单圆盘，外撇腿在重建时由 column 派生短撇腿 visual。 |
| `pedestal_column` | rec_pcsc_var_pedestal | L59-L101 | eligible if compatible | LatheGeometry `pedestal_foot`：宽圆盘底脚（外缘 r=0.40）bell-flare 收成柱身；`column_shaft` + collar + 2 道 rust band。单中央粗柱拓扑，无独立腿。 |
| `tripod_stand` | rec_pcsc_var_tripod | L58-L125 | eligible if compatible | 中央 `tripod_hub` + `for i in range(3)` 发射 3 根撇腿 `leg_i`（120° 间隔，pitch=atan2(dr,dz)）+ `ground_pad_i` + `pad_bolt_i` + `column_shaft` + bands。三脚架落地拓扑。 |

### Slot B：arm_structure（承座臂 — 从 rotor 伸出，臂端 → 每座 REVOLUTE swing pivot）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `straight_radial_arm` | rec_model-a-weathered-four-seat-playground-chair-swi_20260610_085325_366519_82f97e28 | L119-L176 | eligible if compatible | `for i` 发射直辐射臂 `arm_i`（Cylinder，alternating blue/yellow）+ 臂端 clevis：`tip_yoke_i` + 两 `tip_lug_i_j` + 切向 `pivot_pin_i`；外加 8 根 `brace_n` X-truss（相邻臂间双交叉对角）。pivot pin 即 swing 接口。 |
| `spline_tube_lattice` | rec_model-an-old-four-seat-playground-chair-swing-ca_20260610_085340_162128_e48c2551 | L125-L158 | eligible if compatible | 每座切向 `pivot_bar_i`，外加每座 2 根 splayed `arm_tube_i_k`（`tube_from_spline_points` 曲管，hub 端 ±55° 撇出使相邻对交叉成 plan-view X-lattice）。pivot bar 即 swing 接口。 |
| `cantilever_arm` | rec_pcsc_var_cantilever | L165-L190（helper `_tapered_cantilever_arm` L58-L94） | eligible if compatible | 每座单根锥形悬臂 `cantilever_arm_i`：CadQuery loft 圆锥 frustum（hub 端 r=0.040 渐细到 tip r=0.028），无桁架；仍配切向 `pivot_bar_i` 作 swing 接口。 |
| `overhead_chain_hung` | rec_pcsc_var_chainhung | L177-L245（seat 侧 `_build_seat_visuals` L51-L100） | eligible if compatible | 不用刚性辐射臂：rotor 上 4 根 `strut_i` 斜撑升到抬高方环 `ring_seg_i`（世界 z≈1.55）；座由环顶 vertex 经 `hanger_bracket` + 双 `chain_j` 垂挂（钟摆）；swing 接口在 ring vertex（切向 REVOLUTE）。 |

### Slot C：seat_type（座面 — fixed 到对应 swing pivot 件，整座随 REVOLUTE 摆）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `flat_platform_seat` | rec_model-a-weathered-four-seat-playground-chair-swi_20260610_085325_366519_82f97e28 | L190-L236 | eligible if compatible | `hanger_sleeve` 套 pivot pin + 双 `hanger_strap_j` + 平板 `platform`（Box 0.35×0.45）+ 双 `backrest_post_j` + `backrest_rail` 低靠背。 |
| `slatted_bucket_rail` | rec_model-an-old-four-seat-playground-chair-swing-ca_20260610_085340_162128_e48c2551 | L175-L268 | eligible if compatible | 双 `collar_j` 捕获 pivot bar + 双 `strap_j` + 双 `side_rail_j` + 6 条板条 `slat_j`（板条桶座面）+ 环抱弯管 `guard_rail`（`tube_from_spline_points` 包外缘+两侧，向中心开口）+ 双 `rail_post_j`。 |
| `deep_bucket_seat` | rec_pcsc_var_bucket | L246-L310（shell helper `_make_bucket_shell` L57-L99） | eligible if compatible | `hanger_sleeve` + 双 `hanger_strap_j` + `hanger_mount` 板 + 深 CadQuery `bucket_shell`（外箱 fillet 减内腔减前开口，高侧壁包裹）+ 跨前 `safety_bar` lap bar + 双 `bar_bracket_j`。 |

硬约束记录：Slot A=4、Slot B=4、Slot C=3，均 ≥3，满足目标 3-6。每个 candidate 均有真实 `model.py:Lx-Ly` 来源，且彼此为结构差异（part tree / joint 接口 / primitive family 不同），非纯尺寸/材质/装饰差异。

## 槽位图（slot graph）

pattern: `mixed`（multiplicity 主轴 + linear_chain + parallel_children）

```text
base_form (root, 落地固定)
  --[CONTINUOUS Z 关节 `rotor_spin`，origin=柱顶 (0,0,HUB_Z)，axis=(0,0,1)]-->
rotor (hub_sleeve + hub_cap + N 套 arm_structure)
  --[每座 REVOLUTE 关节 `seat_swing_i`，origin=臂端 pivot (px,py,−PIVOT_DROP)+yaw θ_i，axis=(0,−1,0)，±SWING]-->
seat_i (seat_type 子件，i=0..N−1)
```

接口点位：

- `base_form.downstream.spin_bearing`：立柱顶端 bearing collar / 柱顶面，世界高度 `HUB_Z`（splayed/cantilever≈0.90，square/pedestal/tripod≈1.10），rotor hub sleeve 在此就位（captured-shaft proxy，scoped allow_overlap）。所有 base_form 必须把柱顶 spin 接口对齐到统一 `HUB_Z`（family-local 但在 resolve_config 中归一）。
- `rotor.upstream`：消费 spin_bearing，建立**唯一**的 `rotor_spin` CONTINUOUS Z 关节。
- `rotor.downstream.seat_pivots[i]`：N 个臂端切向 pivot 接口，逐 i 提供 world origin (px,py,−PIVOT_DROP)、yaw θ_i=2π·i/N、切向 axis；由 `arm_structure` 实现为 `pivot_pin_i`（straight）/`pivot_bar_i`（spline、cantilever）/ ring vertex（chain_hung）。
- `seat_type.upstream`：每座 `hanger_sleeve`/`collar_j`/`hanger_bracket` 必须与对应 seat_pivot 可见接触/捕获（captured-pin，scoped allow_overlap）；座椅整体 fixed 到 swing 件，随 REVOLUTE 摆。座内附件（`guard_rail`、`safety_bar`/lap_bar、`backrest_rail`）是同一活动 seat part 内的 visual，不浮空、不独立成 part。

跨 slot 互斥 / gating（详见兼容性矩阵）：

- `overhead_chain_hung`（Slot B）改写 rotor 拓扑（无刚性 `arm_i`/`pivot_bar_i`，改为 `strut_i`+`ring_seg_i`+座侧 chains），swing 接口下移到 ring vertex（世界 z≈1.55）。它对 Slot C 的下挂方式不同：座椅顶部要换成 `hanger_bracket`+双 `chain_j` 接口而非 `hanger_sleeve`/`collar`。因此 chain_hung 与三种 seat_type 都兼容，但 seat 的 upstream 接口必须切换到 bracket+chain 形态（由模板在 chain_hung 下重写 seat 顶部接口，shell/platform/slat 主体不变）。
- `slatted_bucket_rail`（Slot C）的上接口是双 `collar_j` 捕获**切向 pivot_bar**（不是 clevis pin）；与 `straight_radial_arm` 的 `pivot_pin` 也兼容（collar 改套 pin），模板统一以「切向 pivot 件 + 双 captured bushing/collar」表达。

## 每槽位 Module Emits / Interfaces

### Slot A / module `square_slab_base`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `support_column`：`base_plate`(Box) + 四 `anchor_bolt_k` + `column_shaft` + `column_base_collar` + `column_band_lower/upper` | S_B / model.py:L57-L94 |
| internal joints | none | S_B / model.py:L57-L94 |
| upstream interface | root，落地无 parent | S_B / model.py:L57-L63 |
| downstream interface | 柱顶 spin_bearing，世界 HUB_Z=1.10，rotor hub sleeve 就位 | S_B / model.py:L71-L76, L178-L186 |

### Slot A / module `splayed_leg_base`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `column`：圆盘 `base_plate`(Cylinder) + `column_shaft` + `bearing_collar` + `spindle` + `spindle_nut`(mesh)；重建时由 column 派生外撇腿 visual | S_A / model.py:L71-L102 |
| internal joints | none | S_A / model.py:L71-L102 |
| upstream interface | root，落地无 parent | S_A / model.py:L71-L77 |
| downstream interface | bearing_collar 顶面 spin_bearing，世界 HUB_Z=0.90；spindle+nut 外露于 hub cap 之上 | S_A / model.py:L84-L102, L160-L168 |

### Slot A / module `pedestal_column`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `support_column`：LatheGeometry `pedestal_foot`（宽圆盘底脚）+ `column_shaft` + collar + 2 道 band | S_PED / model.py:L59-L101 |
| internal joints | none | S_PED / model.py:L59-L101 |
| upstream interface | root，落地无 parent；圆形底脚 footprint dx≈dy>0.7 | S_PED / model.py:L59-L83 |
| downstream interface | 柱顶 spin_bearing，世界 HUB_Z=1.10 | S_PED / model.py:L78-L83, L185-L193 |

### Slot A / module `tripod_stand`
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `support_column`：`tripod_hub` + `for i in range(3)`：`leg_i`/`ground_pad_i`/`pad_bolt_i` + `column_shaft` + bands | S_TRI / model.py:L58-L125 |
| internal joints | none | S_TRI / model.py:L58-L125 |
| upstream interface | root，落地无 parent；3 脚 120° 等距，foot_r≈0.40 | S_TRI / model.py:L66-L100 |
| downstream interface | 柱顶 spin_bearing，世界 HUB_Z=1.10 | S_TRI / model.py:L102-L107, L209-L217 |

### Slot B / module `straight_radial_arm`
| emits | 描述 | 来源 |
|---|---|---|
| parts | rotor 上 N 套：`arm_i`(Cylinder) + `tip_yoke_i` + 双 `tip_lug_i_j` + `pivot_pin_i`；外加 2N 根 `brace_n` X-truss | S_B / model.py:L119-L176 |
| internal joints | none inside module（臂刚连 rotor） | S_B / model.py:L119-L176 |
| upstream interface | 挂在 rotor part 上，消费 hub 出口（r≈0.07 起） | S_B / model.py:L119-L128 |
| downstream interface | N 个 seat_pivots：切向 `pivot_pin_i` @ (px,py,−PIVOT_DROP)，axis=(0,−1,0) | S_B / model.py:L146-L152, L226-L236 |

### Slot B / module `spline_tube_lattice`
| emits | 描述 | 来源 |
|---|---|---|
| parts | rotor 上 N 套：切向 `pivot_bar_i` + 每座 2 根 splayed `arm_tube_i_k`（spline 曲管，相邻对交叉成 X-lattice） | S_A / model.py:L125-L158 |
| internal joints | none inside module | S_A / model.py:L125-L158 |
| upstream interface | 挂在 rotor part 上，arm tube hub 端 r≈0.095 起 | S_A / model.py:L137-L158 |
| downstream interface | N 个 seat_pivots：切向 `pivot_bar_i` @ (cx,cy,BAR_Z)，axis=(0,−1,0) | S_A / model.py:L129-L135, L255-L268 |

### Slot B / module `cantilever_arm`
| emits | 描述 | 来源 |
|---|---|---|
| parts | rotor 上 N 套：切向 `pivot_bar_i` + 单根锥形 `cantilever_arm_i`（CadQuery loft frustum，hub→tip 渐细，无桁架） | S_CAN / model.py:L165-L190；helper L58-L94 |
| internal joints | none inside module | S_CAN / model.py:L165-L190 |
| upstream interface | 挂在 rotor part 上，arm hub_r=0.105 起 | S_CAN / model.py:L176-L190 |
| downstream interface | N 个 seat_pivots：切向 `pivot_bar_i` @ (cx,cy,BAR_Z)，axis=(0,−1,0) | S_CAN / model.py:L168-L174, L287-L300 |

### Slot B / module `overhead_chain_hung`
| emits | 描述 | 来源 |
|---|---|---|
| parts | rotor 上：N 根斜撑 `strut_i` + N 段抬高方/多边环 `ring_seg_i`（世界 z≈1.55）；座侧 `hanger_bracket` + 双 `chain_j` 垂挂 | S_CHN / model.py:L177-L245；seat helper L51-L100 |
| internal joints | none inside module（rotor 刚性；座经 swing 关节） | S_CHN / model.py:L177-L215 |
| upstream interface | 挂在 rotor part 上，strut 从 hub r≈0.12,z≈0.17 升到 ring vertex | S_CHN / model.py:L177-L196 |
| downstream interface | N 个 seat_pivots 在 ring vertex (jx,jy,RING_Z_LOCAL)，axis=(0,−1,0)；座顶 bracket 捕获 ring tube（scoped overlap） | S_CHN / model.py:L198-L245 |

### Slot C / module `flat_platform_seat`
| emits | 描述 | 来源 |
|---|---|---|
| parts | seat part：`hanger_sleeve` + 双 `hanger_strap_j` + 平板 `platform` + 双 `backrest_post_j` + `backrest_rail` | S_B / model.py:L190-L236 |
| internal joints | none（仅上游 swing 关节） | S_B / model.py:L190-L236 |
| upstream interface | `hanger_sleeve` 套 pivot_pin/pivot_bar（captured，scoped overlap） | S_B / model.py:L194-L206 |
| downstream interface | 无下游 slot | S_B / model.py:L207-L225 |

### Slot C / module `slatted_bucket_rail`
| emits | 描述 | 来源 |
|---|---|---|
| parts | seat part：双 `collar_j` + 双 `strap_j` + 双 `side_rail_j` + 6 条 `slat_j` + 环抱 `guard_rail`(spline) + 双 `rail_post_j` | S_A / model.py:L175-L268 |
| internal joints | none（仅上游 swing 关节） | S_A / model.py:L175-L268 |
| upstream interface | 双 `collar_j` 捕获切向 pivot_bar（captured，scoped overlap）| S_A / model.py:L178-L185 |
| downstream interface | 无下游 slot | S_A / model.py:L204-L253 |

### Slot C / module `deep_bucket_seat`
| emits | 描述 | 来源 |
|---|---|---|
| parts | seat part：`hanger_sleeve` + 双 `hanger_strap_j` + `hanger_mount` + CadQuery `bucket_shell`（高侧壁前开口）+ `safety_bar` lap bar + 双 `bar_bracket_j` | S_BKT / model.py:L246-L310；shell helper L57-L99 |
| internal joints | none（lap bar 是 fixed visual，非铰；仅上游 swing 关节） | S_BKT / model.py:L246-L310 |
| upstream interface | `hanger_sleeve` 套 pivot_pin/pivot_bar（captured，scoped overlap）| S_BKT / model.py:L255-L261 |
| downstream interface | 无下游 slot | S_BKT / model.py:L270-L298 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `base_form` | enum | `square_slab_base`, `splayed_leg_base`, `pedestal_column`, `tripod_stand` | — | choice | deterministic procedural sampler（或 regression override）选择；决定 root part、落地 footprint 与柱顶 HUB_Z（resolve_config 归一） | Slot A table |
| `arm_structure` | enum | `straight_radial_arm`, `spline_tube_lattice`, `cantilever_arm`, `overhead_chain_hung` | — | choice | sampler 选择；决定 rotor 拓扑与 seat_pivots 形态（pin/bar/ring vertex） | Slot B table |
| `seat_type` | enum | `flat_platform_seat`, `slatted_bucket_rail`, `deep_bucket_seat` | — | choice | sampler 选择；座椅 part tree | Slot C table |
| `seat_count` (N) | int | `[2, 8]`（产品全程；测试偏小） | 4 | independent（加权） | 加权采样：小 N 高频、大 N 稀有（见 Multiplicity）；驱动 `360/N` 等角与所有 `*_i` 复制 | n2 L33-L38; n6 L50-L51; parents N=4 |
| `palette_style` | enum | `rust_red_cream`, `weathered_white_carnival`, `galvanized_steel`, `faded_teal_rust`, `candy_repaint` | `rust_red_cream` | choice (palette only) | 仅材质/配色，不改拓扑；见下方 palette 清单 | parents + variants material blocks |
| `seat_radius_scale` | float | `[0.85, 1.20]` | 1.0 | independent | SEAT_R/PIVOT_R 基准 ≈1.38–1.40；scale 后 clamp；整体直径 2·R·scale ∈ ~2.3–3.4 m | S_A L42; S_B L34 |
| `column_height_scale` | float | `[0.90, 1.20]` | 1.0 | independent | 缩放 HUB_Z 与柱身长度；rotor、seat_pivot z 随之派生 | S_A L41; S_B L33 |
| `swing_limit_rad` | float | `[0.42, 0.62]` | `0.524`(30°) | independent | seat_swing REVOLUTE 的 ±range | S_A L48; S_B L36 |
| `arm_thickness_scale` | float | `[0.80, 1.30]` | 1.0 | independent | 缩放臂/撑/桁架管半径；不改接口位置 | S_B L124; S_A L131 |
| `pivot_drop` | float | derived | `0.10` | equation | `= 0.10 · column_height_scale`；pivot 件相对 rotor 的下沉，保证 seat 接口随高度一致 | S_B L35 |
| `ring_height_local` | float | conditional/derived | `0.45` | conditional | 仅 `overhead_chain_hung`：ring vertex 局部 z，世界 z≈HUB_Z+0.45；非 chain_hung 不存在 | S_CHN L38 |
| (—) | constraint | — | — | inequality | **座椅周向不自碰**：相邻座 station 角间隔 `2π/N` 处的座宽弦长 `2·R·sin(π/N) ≥ seat_tangential_width + clearance`；N 偏大或 seat 偏宽时按比例回缩 seat_radius_scale↑ 或拒绝重采 | 接口 / clearance（n2 brace tangent offset L157） |
| (—) | constraint | — | — | inequality | **swing 摆出不撞中柱/相邻座**：座椅在 ±swing_limit 摆到内侧极限时 inner edge x 不进入 column 半径 + clearance | swing pose 检查（S_B L382-L401） |
| (—) | constraint | — | — | conditional | `overhead_chain_hung` 下 seat upstream 接口切换为 `hanger_bracket`+双 `chain_j`，并禁用 `hanger_sleeve`/`collar` 形态；其余 seat 主体（platform/slat/shell）不变 | S_CHN L51-L100 |

## Multiplicity / Copy Logic

本类别有 **1 根** multiplicity 轴：`seat_count` N（每个 station = 一套臂 + 一把摆动座 + 其 swing 关节，绕 rotor 等角复制）。

- `count_param`: `seat_count`（N）
- `N_range`: `[2, 8]`（产品全程；测试偏小，sweep 上限 8）。源覆盖 {2(var_n2), 4(both parents), 6(var_n6)}，模板把计数轴交给采样器。
- sampling domain（权重档）：小 N 高频、大 N 稀有。建议权重 N=2:0.10、N=3:0.12、N=4:0.30、N=5:0.16、N=6:0.16、N=7:0.08、N=8:0.08（标称偏 4）。每个 seed 对该轴做一次加权采样后 clamp 到 `[2,8]`。
- copied object：完整 station = `arm_structure` 的臂/桁架/撑/pivot 件（`arm_i`/`arm_tube_i_k`/`cantilever_arm_i`/`strut_i`+`ring_seg_i`/`pivot_bar_i`/`pivot_pin_i`+clevis）+ 一把 `seat_type` 子件（`seat_i`）+ 该座的 `seat_swing_i` REVOLUTE 关节。
- naming：`for i in range(seat_count)`，角度 `theta_i = 2π·i/N`；部件 `f"arm_{i}"`/`f"pivot_bar_{i}"`/`f"pivot_pin_{i}"`/`f"seat_{i}"`/`f"seat_swing_{i}"`/`f"strut_{i}"`/`f"ring_seg_{i}"`；X-truss `brace_n` 共 2N 根（仅 `straight_radial_arm`）。
- placement：绕 rotor 等角分布，半径固定（seat_radius_scale 后的 R）；座挂在臂端 swing pivot（`overhead_chain_hung` 挂在 ring vertex）。
- joint policy：**全局只有 1 个** `rotor_spin` CONTINUOUS（axis Z）；**每座 1 个** `seat_swing_i` REVOLUTE（切向 axis≈(0,−1,0)，±swing_limit）。station 间各自独立摆动，无 station-to-station mimic / 无闭环。
- gating：`overhead_chain_hung` 在大 N 时 ring 变 N 边多边形环（`ring_seg_i` 共 N 段，相邻 vertex 连线）；`spline_tube_lattice`/`straight_radial_arm` 的 X-lattice/X-truss 在大 N 时弦长变短需 tangent offset 防止交叉穿中柱（见 n2 `BRACE_TANGENT_OFFSET` L157）。源/gating：n2/n6 提供 N 参数化的 `ARM_ANGLES = [i·2π/N for i in range(N)]` 模式。

## 拓扑多样性审计

总组合数（slot 笛卡尔，未计 N 与 palette）：A × B × C = 4 × 4 × 3 = **48**。
计入 multiplicity：N ∈ [2,8] 共 7 档 → 48 × 7 = **336** 个 (slot×N) 组合（palette 不计入拓扑，因为只改材质）。


理由：候选不仅改尺寸，还改 part count、part tree、primitive family（Box/Cylinder vs LatheGeometry vs spline tube vs CadQuery loft/shell）、rotor 拓扑（刚性辐射臂+X-truss vs spline X-lattice vs 单悬臂 vs 顶环吊链）、swing 接口形态（clevis pin / 切向 bar / ring vertex bracket+chain）、底座落地形态（方板+螺栓 / 圆盘 / 单柱圆盘脚 / 三脚架），再叠加 N=2..8 的真实 station 复制（座/臂/关节数量随 N 变）。仅 base_form×arm_structure 就有 16 种结构上可分辨拓扑，远超 10。

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 用 deterministic procedural sampling；`seed=0` 不特殊。先选 base_form/arm_structure/seat_type 三槽，再加权采 N，再选 palette，最后采连续 scale（independent → 派生 pivot_drop/ring_height → inequality 投影座间隙/摆出间隙 → conditional 解析 chain_hung 接口）。

Procedural Sampling / Sweep Plan：sampler 顺序 = base_form → arm_structure → seat_type → seat_count(加权) → palette_style → 连续 scale。compatibility matrix 见下；不兼容/退化组合在 sampler 或 resolve_config 内降级/回缩/重采，不留到 builder。少量 regression override 仅在 sweep 发现稳定失败组合或 reviewer 指定时添加（默认无）。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）。本类别 (slot×N) 已有 336 个结构可分辨组合，加上连续 scale 的 binning，1000-seed 轻松 ≥300。

Controlled local parameterization：初版模板包含的关键连续 scale = `seat_radius_scale`（[0.85,1.20]）、`column_height_scale`（[0.90,1.20]，派生 HUB_Z/柱长/pivot_drop）、`arm_thickness_scale`（[0.80,1.30]，仅管半径）、`swing_limit_rad`（[0.42,0.62]）。全部在 resolve_config 内 clamp/派生，并受座间隙、摆出间隙、captured-pin 接口、joint origin、类别 identity 约束；按 §7 约束类型声明依赖（pivot_drop=equation(column_height_scale)；ring_height_local=conditional(arm_structure)；两条座/摆间隙=inequality），遵守「先 independent → 派生 equation → 投影 inequality → 解析 conditional」契约。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | base_form→arm_structure→seat_type→N(加权)→palette→连续 scale；deterministic per seed | slot_choices_for_seed 与 build choices 一致；N∈[2,8] |
| compatibility matrix | 见下表；chain_hung 切换 seat upstream 接口；slatted_bucket 统一以「切向 pivot + 双 collar」表达 | 无浮空座 / 无穿中柱 / 切向座间隙 / swing 轴+range / 关节 origin |
| controlled local variation | 4 个连续 scale，clamp + 派生 | 比例变化不破坏接口、clearance、support、joint origin、identity |
| regression overrides | none（如未来发现失败组合再加，注明 seed+原因） | 仅已知失败回归 / reviewer 指定 |
| random sweep | seeds 0、0-4、0-19、0-49 渐进，成熟期 0-999 | 与 MatingContract 失败 |

兼容性矩阵（base_form × arm_structure × seat_type）：

- base_form（全部 4 种）与 arm_structure（全部 4 种）**全兼容**：底座只负责落地+柱顶 spin_bearing，rotor 拓扑独立；模板把各 base_form 的柱顶接口归一到统一 HUB_Z。
- seat_type（全部 3 种）与 arm_structure：`straight_radial_arm`/`spline_tube_lattice`/`cantilever_arm` 提供切向 pivot 件（pin 或 bar），三种 seat 的 captured bushing（`hanger_sleeve`/双 `collar_j`）都能套上 → 全兼容。`overhead_chain_hung` 把座 upstream 切换为 `hanger_bracket`+双 `chain_j`（conditional），platform/slat/shell 主体保留 → 也与三种 seat 兼容。
- 退化/回缩点：大 N（≥7）下 `spline_tube_lattice`/`straight_radial_arm` 的交叉 lattice/truss 弦短易穿中柱 → 用 `BRACE_TANGENT_OFFSET`（n2 L157）侧移，或回缩到不交叉的单臂表达；座宽 vs `2·R·sin(π/N)` 间隙不足时 seat_radius_scale↑ 或拒绝重采。
- 互斥：无硬互斥 slot 对；唯一条件分支是 chain_hung 的 seat-upstream 接口切换（conditional，非互斥）。

## Validator

- `slot_choices_for_seed(seed)` returns implemented module names（base_form/arm_structure/seat_type ∈ 各表），并且 `seat_count ∈ [2,8]`、`len([seat_i]) == seat_count`、`len([seat_swing_i]) == seat_count`。
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling；`seed=0` 不特殊。
- compatibility matrix / gating 阻止非法组合；chain_hung 的 seat-upstream 接口切换在 resolve_config 内解析。
- optional regression overrides 稀疏且有理由（默认 none）。
- final 模板不无限轮换小型 curated 表作为主 seed domain。
- controlled local scale（seat_radius/column_height/arm_thickness/swing_limit）被 clamp/派生，不破坏接口、clearance、joint origin、N 复制。
- 跨部件 scale 依赖（pivot_drop=equation、ring_height=conditional、座/摆间隙=inequality）在 resolve_config 求解，不留到 builder 失败。
- 关键 InterfaceSpec / MatingContract 点存在：rotor hub_sleeve 就位 base_form 柱顶 bearing（captured-shaft，scoped allow_overlap + expect_contact/within）；每座 captured-pin（`hanger_sleeve`/`collar`/`hanger_bracket` 套 pivot_pin/pivot_bar/ring vertex，scoped allow_overlap + expect_overlap）。
- 关键 joints 类型/轴/range：`rotor_spin` = CONTINUOUS，axis=(0,0,1)，唯一一个；每 `seat_swing_i` = REVOLUTE，axis≈(0,−1,0)，lower/upper=∓swing_limit；正 q 让座向外+上摆、负 q 向内收（pose 检查）；spin 四分之一圈把 seat_0 从 +X 带到 +Y。
- copied objects 遵守 naming/placement：`*_i` 前缀、等角 `2π·i/N`、半径固定、座挂臂端 pivot。
- base_form 落地可见：方板/圆盘/pedestal 圆脚/三脚架有真实地面支撑路径；rotor 顶端 cap/spindle 收顶。

## Reject cases

- 座椅、桶座或平板浮空，没有可见的「臂/链 → rotor → 柱」支撑路径。
- rotor 不绕柱旋转（缺 `rotor_spin` CONTINUOUS）或把旋转做成 REVOLUTE 有限角（这是 carousel，不是有限摆台）。
- 把 N 把座做成一个 part 里复制 visual 却只暴露 1 个 swing 关节（必须 N 个独立 `seat_swing_i`）。
- seat_count 改了但 `ARM_ANGLES`/复制循环没跟着用 `2π/N`，导致座椅不均布或重叠。
- 大 N 下 spline/straight 的 X-lattice/X-truss 弦穿过中柱或相邻座互撞（未做 tangent offset / 未回缩）。
- `overhead_chain_hung` 仍保留刚性 `arm_i`/`pivot_bar_i`，或座顶仍用 `hanger_sleeve` 而不切换到 bracket+chain。
- 把 `slatted_bucket_rail`、`deep_bucket_seat`、`flat_platform_seat` 仅当作同一 mesh 的颜色/尺寸变体（必须不同 part tree / primitive）。
- swing 关节轴做成径向或竖直，导致座椅不是「向外/向内摆」而是绕错轴。
- captured-shaft / captured-pin overlap 未用 element-scoped allow_overlap，触发整体碰撞失败；或 hub sleeve 与柱顶 bearing 实际脱开浮空。
- 把 base_form 的柱顶 HUB_Z 留成各家不同未归一，导致 rotor/seat 接口 z 错位、座离地高度跑出 0.5 m 域。

## 与相邻类别的边界

- 不该混入：`merry_go_round` / 旋转木马（carousel horse）。理由：旋转木马是**封闭顶棚平台 + 上下起伏的固定木马**，骑乘者站/坐在随平台整体旋转的甲板上，没有「臂端切向 REVOLUTE 让单座向外摆荡」的钟摆语义；本类别核心是 spin + 每座独立 outward swing。
- 不该混入：`playground_swing` / 普通秋千（A-frame swing set）。理由：普通秋千是**固定顶梁/A 架下静止悬挂**、人力前后摆，没有中央 CONTINUOUS 旋转柱与等角 N 座绕轴公转；本类别必须有动力旋转 rotor。
- 不该混入：`ferris_wheel` / 摩天轮。理由：摩天轮是**竖直大轮在垂直平面内绕水平轴整轮旋转**、吊舱靠重力保持竖直；本类别是**水平面内绕竖直 Z 轴旋转**、座椅在切向竖直平面内小角度摆荡，尺度与轴向都不同。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY draft authored from 2 converged parents + 7 rating-5 variants (9 five-star samples). 3 slots (A=4, B=4, C=3 candidates), 1 multiplicity axis seat_count N∈[2,8], 5-color palette. Awaiting human review before template implementation. |

## 模板实现备注（可选）

- 共享 helper：`_radial(theta, radius, tangent)`（rotor 极坐标，几乎所有源都有）、`_polar`（splayed/cantilever 家族）、`ARM_ANGLES/SEAT_ANGLES = [i·2π/N for i in range(N)]`（N 参数化，来自 n2/n6）。
- arm_structure 专属 helper：`_tapered_cantilever_arm`（cantilever，CadQuery loft frustum，L58-L94）、`tube_from_spline_points`（spline_tube_lattice 曲管 + slatted guard_rail）、`_make_bucket_shell`（deep_bucket_seat，CadQuery box−cavity−front_cut，L57-L99）、`LatheGeometry`（pedestal_foot）。
- InterfaceSpec 两类：`spin_bearing`（柱顶 hub 就位，captured-shaft）、`seat_pivot[i]`（切向 pivot pin/bar 或 ring vertex，captured-pin）。MatingContract 要求 hub_sleeve 可见接触 bearing collar / 柱顶；每座 bushing/collar/bracket 可见捕获其 pivot 件。
- 所有 captured-shaft / captured-pin / chain_hung 的 bracket-ring overlap 必须 element-scoped allow_overlap（逐座、逐元素，参照各源 run_tests 的 allow_overlap 调用）。
- HUB_Z 归一：splayed/cantilever 源用 0.90、square/pedestal/tripod/chain 源用 1.10；resolve_config 应统一导出一个 HUB_Z（受 column_height_scale 缩放），再让 rotor、seat_pivot、ring 一致派生，避免座离地高度跑域。
- 大 N gating：`BRACE_TANGENT_OFFSET`（n2 L157）侧移 X-truss/X-lattice；chain_hung 的 `ring_seg_i` 在 N≠4 时退化为 N 边多边形环。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S_A | A/B/C | `splayed_leg_base` + `spline_tube_lattice` + `slatted_bucket_rail` | rec_model-an-old-four-seat-playground-chair-swing-ca_20260610_085340_162128_e48c2551 | L40-L268 | 圆盘脚底座、spline 曲管 X-lattice 臂、板条桶座+环抱护栏、HUB_Z=0.90 spindle 收顶 |
| S_B | A/B/C | `square_slab_base` + `straight_radial_arm` + `flat_platform_seat` | rec_model-a-weathered-four-seat-playground-chair-swi_20260610_085325_366519_82f97e28 | L33-L236 | 方板+螺栓底座、直辐射臂+clevis+X-truss、平板座+靠背、HUB_Z=1.10、N 参数化 spin/swing 关节契约 |
| S_PED | A | `pedestal_column` | rec_pcsc_var_pedestal | L59-L101 | LatheGeometry 宽圆盘底脚单柱 |
| S_TRI | A | `tripod_stand` | rec_pcsc_var_tripod | L58-L125 | for-range(3) 三脚架腿+hub+ground pad |
| S_CAN | B | `cantilever_arm` | rec_pcsc_var_cantilever | L58-L94, L165-L190 | 单根锥形悬臂 frustum helper |
| S_CHN | B | `overhead_chain_hung` | rec_pcsc_var_chainhung | L51-L100, L177-L245 | 顶环+斜撑+双链垂挂钟摆、ring vertex swing 接口 |
| S_BKT | C | `deep_bucket_seat` | rec_pcsc_var_bucket | L57-L99, L246-L310 | CadQuery 深桶 shell + lap bar |
| S_N2 | (multiplicity) | seat_count N=2 | rec_pcsc_var_n2 | L33-L38, L121-L185 | `ARM_ANGLES=[i·2π/N]` 参数化 + 大间隔 brace tangent offset |
| S_N6 | (multiplicity) | seat_count N=6 | rec_pcsc_var_n6 | L50-L51, L125-L158 | `SEAT_ANGLES=[i·2π/N]` 60° 间隔复制 |
