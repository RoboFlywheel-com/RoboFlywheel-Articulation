# Trashcan1 — Modular Template Spec (SPEC_ONLY)

## 元信息
| 项 | 值 |
|---|---|
| slug | `trashcan1` |
| template path | `agent/templates/Urban_Environment_Trashcan1.py` |
| test path (optional) | `tests/agent/test_trashcan1_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children` (root `can_body` + lid_assembly child + handle children, with a body-local vertical-rib `multiplicity` axis) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (2 parents + 8 converged fork variants) |
| source_index_policy | only adopted module sources are indexed below |

**Reading summary.** Every sample is a **galvanized sheet-metal can**: a root `can_body` (hollow revolved/corrugated cylinder, solid floor disc, rolled top rim torus, inline riveted lug pads) that always sits at `z≈0` with a deep interior cavity, plus a removable/openable top and side carry handles. All ten share the identical coordinate convention (vertical axis +Z, footprint at z=0, lid hinge/lift at the rim plane `BODY_H`) and the identical helper family: `_corrugated_*_shell`, `_floor_disc`, `_rolled_rim`, `_lug_pad`, lid/handle wire loops via `tube_from_spline_points`.

The real **structural variation axes** (true topology, not size/color):
- **Body profile** — how `_radius_at(z)` is defined: linear taper wider-at-top (parents, `taper`), constant radius (`straightbody`), or linear+sinusoidal barrel bulge (`body_profile`). Same wall topology, different revolve profile.
- **Surface treatment** — how the wall is built: angular trig corrugation baked into the shell (`amp*cos(n*theta)`, parents), explicit bold `rib_{i}` protrusions on a smooth shell (`ribcount`), horizontal ring-band torus stack on a Lathe smooth shell (`surface_horizontal`), or a plain smooth shell (`surface_smooth`). This **changes the body part's visual set and primitive choices**.
- **Lid / top mechanism (defining joint)** — tall/shallow domed **REVOLUTE** rear-hinged flip lid (parents), **flat lift-off PRISMATIC** lid (`lidtype`), or **no lid / open rim** with the joint moved onto the side handles (`openrim`). Different child part, joint type and axis.
- **Handle style** — two fixed side ring/bail ears FIXED via lugs (parents), two **REVOLUTE** swinging drop-bail side handles (`openrim`), or a single **REVOLUTE** overhead carrying bail across the top (`handle`, two pivot lugs + two arms + crossbar). Different part count, joint count/type.
- **Vertical-rib multiplicity** — corrugation/rib count is a single count param that at coarse N (`ribcount`, RIB_COUNT=8 bold `rib_{i}` protrusions) becomes a genuine per-rib loop with distinct part naming; at fine N it is the trig flute frequency (parents, 28/40). This is the **one multiplicity axis**.

## 核心身份

Trashcan1 is a **classic galvanized steel trash / garbage can**: a hollow upright sheet-metal cylinder (tapered, straight, or barrel-bulged) with a corrugated/ribbed or smooth wall, a **solid floor disc** so it is a closed-bottom open-topped vessel, a **rolled top rim**, riveted **side lug pads**, and a **removable / openable domed top** plus **carry handles**. The category-defining articulation is the **loose lift-off DOME LID** (PRISMATIC vertical lift — the canonical joint) or a rear-hinged REVOLUTE flip lid, with side **ring/bail ear handles** (FIXED) or an **overhead swing BAIL** (REVOLUTE). The whole object reads as galvanized steel; color/material/weathering variety is cosmetic only, never a structural slot.

Mature domain: a single domestic/municipal hand-carried metal can roughly 0.40–0.50 m diameter, 0.60–0.70 m tall, footprint at z=0, deep hollow interior, at least one real non-fixed joint (lid lift/flip or handle swing).

## 与相邻类别的边界

- 不该混入 **Trashcan2 (swing-lid street can)**：那是固定外壳 + 内部弹簧/重力 swing-flap 投入口，盖永久铰接在壳上，不是 loose lift-off / 不能整盖移除；trashcan1 的盖是可分离 lift-off / 后铰翻盖，且整体是手提金属桶非固定街具。
- 不该混入 **Large_Trashcan (wheelie bin)**：那是塑料带轮 + 脚踏/铰接掀盖 + 滚轮底座；trashcan1 reference 无脚无轮，禁止 footed/wheeled base、step-pedal、spout（明确 dropped）。
- 不该混入 **Garbage_bin (dumpster)**：那是大型方箱钢斗 + 侧/顶举升铰接 + 叉举槽；trashcan1 是小型圆桶、圆形 revolve body、ring/bail 手提把手，不是方箱也不是叉举结构。
- 不该混入裸塑料垃圾桶 / kitchen step-bin：trashcan1 身份是 galvanized 镀锌钢 + corrugation + rolled rim + 金属丝 bail；纯塑料光壁 + 踏板属其他类别。

## 槽位 + 候选模块表

### Slot A：body_profile（revolve 轮廓 / silhouette）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `profile_tapered` (baseline) | rec_galvanized-steel-trash-can-with-a-slightly-taper_…e62b5cca | L55-L58 (`_radius_at`), L41-L43 dims | eligible if compatible | 线性锥体 `r = R_BOT + (R_TOP-R_BOT)*t`，rim 宽于 foot（R_TOP 0.215 > R_BOT 0.170）；下游 lug/lid/rim 半径都读 `_radius_at(z)` |
| `profile_straight` | rec_trashcan1_var_straightbody | L41 (`BODY_R=0.215`), L54-L108 (`_corrugated_straight_shell`) | eligible if compatible | 恒定半径直筒；`r_in = BODY_R - amp - wall` 常数内壁；不用 `_radius_at`，用 `BODY_R` 常量 |
| `profile_barrel` | rec_trashcan1_var_body_profile | L43-L46 (R_RIM/R_FOOT/R_BULGE), L58-L67 (`_radius_at` 带 bulge) | eligible if compatible | 线性 + `R_BULGE*sin(pi*t)` 鼓肚，mid-height 最宽、两端收；rim 与 foot 都窄 |

### Slot B：surface（壁面纹理 / wall 构建方式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `surface_vertical_flutes` (baseline) | rec_galvanized-steel-trash-can-with-a-slightly-taper_…e62b5cca | L61-L116 (`_corrugated_tapered_shell`) | eligible if compatible | 角向 trig 波纹 `ro = rbase + amp*cos(n_ribs*theta)`，`ang_segs=n_ribs*4`；hollow 双壁；细 flutes (N=28/40)。multiplicity 走频率 |
| `surface_smooth` | rec_trashcan1_var_surface_smooth | L60-L116 (`_smooth_tapered_shell`) | eligible if compatible | 光壁 hollow 双壁，无角向调制 `ro = rbase`；`ang_segs=72`。无 multiplicity rib |
| `surface_horizontal_rings` | rec_trashcan1_var_surface_horizontal | L64-L92 (`_smooth_tapered_shell` via `LatheGeometry.from_shell_profiles`), L95-L99 (`_ring_band`), L206-L221 (ring loop) | eligible if compatible | Lathe 光壁 + `RING_COUNT` 个水平 torus 环带 stack `ring_band_{i}`（水平 multiplicity 替代竖向）；环 z 均布 |
| `surface_bold_ribs` | rec_trashcan1_var_ribcount | L26-L51 (`_smooth_tapered_shell`+rib dims), L124-L185 (`_bold_rib` peaked-ridge), L284-L301 (`rib_{i}` loop) | eligible if compatible | 光壁 + 显式 `rib_{i}` 凸棱循环（peaked-ridge mesh, depth 0.012），bold 少量 N (8)；rib 随 `_radius_at` taper。这是 vertical-rib multiplicity 的显式 loop 形态 |

### Slot C：lid_top（顶部机构 — 定义性 joint 槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `lid_dome_revolute` (baseline) | rec_galvanized-steel-trash-can-with-a-slightly-taper_…e62b5cca | L167-L203 (`_lid_geometry` tall dome+brim+skirt+loop), L268-L284 (REVOLUTE) | eligible if compatible | 高 domed 盖 (DomeGeometry, rise 0.085) + 顶 loop handle；REVOLUTE 后铰，axis=(-1,0,0)，0..100°；closed skirt nests over rim |
| `lid_dome_shallow_revolute` | rec_old-galvanized-steel-garbage-can-with-a-vertical_…15c2b69d | L171-L208 (`_lid_geometry` disc-stack dome, rise 0.045), L272-L291 (REVOLUTE) | eligible if compatible | 浅 domed 盖 = `for k in range(levels)` 收缩 disc 堆 + skirt + loop；同 REVOLUTE 后铰 0..100° |
| `lid_flat_liftoff_prismatic` (canonical joint) | rec_trashcan1_var_lidtype | L167-L222 (`_flat_lid_geometry` disc+skirt+central bail), L287-L303 (PRISMATIC) | eligible if compatible | **平 lift-off 盖**：flat disc + 下沉 skirt 套 rim + 中央 bail loop；**PRISMATIC** axis=(0,0,1)，lift 0..0.40 m，无横移；`LID_SEAT_Z = BODY_H + LID_DISC_T/2` |
| `top_open_rim` | rec_trashcan1_var_openrim | L173-L232 (无 lid part；body 同), L317-L322 (open-top test) | eligible only with handle_swing_bail | 无盖开口；body top ≈ rim 高；joint 转移到 side handle（必须配 Slot D `handle_swing_bail`，否则无 non-fixed joint） |

### Slot D：handle（提手 / 提梁）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `handle_two_ring_ears` (baseline) | rec_galvanized-steel-trash-can-with-a-slightly-taper_…e62b5cca | L141-L164 (`_ring_handle` oval drop-ring), L246-L266 (2× FIXED via lug loop) | eligible if compatible | 两侧 D-ring 垂吊把手，`for side_name,ang in (("right",0),("left",pi))` 2× **FIXED**；两 inline lug pad；ring 顶钩入 lug |
| `handle_two_bail_ears` | rec_old-galvanized-steel-garbage-can-with-a-vertical_…15c2b69d | L146-L168 (`_bail_handle` semicircular wire), L252-L270 (2× FIXED) | eligible if compatible | 两侧半圆 wire-bail 把手 FIXED；每侧两 lug（top/bot）；arc 外凸 |
| `handle_swing_bail_sides` (REVOLUTE) | rec_trashcan1_var_openrim | L136-L170 (`_bail_handle_local`+`_HANDLE_CONFIGS`), L234-L268 (2× REVOLUTE) | eligible if compatible | 两侧摆动 drop-ring，每侧一 lug pivot；2× **REVOLUTE** 水平切向 axis（±Y），0..90°；q=0 垂吊、正向外上摆 |
| `handle_overhead_bail` (REVOLUTE) | rec_trashcan1_var_handle | L144-L243 (`_bail_side_element` lug+arm, `_bail_crossbar`), L316-L398 (2 pivot lug loop + 2 arm loop + crossbar + 1 REVOLUTE) | eligible if compatible | 单过顶提梁：两 pivot lug + 两 arm（`for i` loop, 共享 helper）+ crossbar；单 **REVOLUTE** axis=(1,0,0) 过两 lug 连线，0..170°，从垂吊摆到过顶 |

硬约束满足：Slot A=3、B=4、C=4、D=4，均 ≥3。每个 candidate 有真实 `model.py:Lx-Ly` 且结构不同（profile=revolve 函数不同；surface=wall 构建方式/visual set 不同；lid=part+joint type 不同；handle=part count+joint type 不同）。`top_open_rim` 是唯一受限 candidate（须配 `handle_swing_bail_sides`），理由见兼容矩阵。

## 槽位图（slot graph）

pattern: `parallel_children` + 一根 body-local rib `multiplicity` 轴

```
can_body (ROOT, z=0 footprint)
  ├─ [Slot A profile -> _radius_at(z)]  drives wall/rim/lug radii
  ├─ [Slot B surface] wall visuals on body (flutes baked | smooth | ring_band_{i} | rib_{i})
  │      rib/ring multiplicity axis N -> body-local copied visuals (no joints)
  ├──[REVOLUTE rear hinge @ (0, R_rim+δ, BODY_H) axis -X  |  PRISMATIC @ (0,0,BODY_H+t/2) axis +Z  |  (none if open_rim)]──> lid_assembly  (Slot C)
  └──[FIXED via lug  |  REVOLUTE @ side-lug pivot axis ±Y  |  REVOLUTE @ overhead axis +X]──> handle part(s)  (Slot D)
```

- **Slot A** 不是独立 part，它通过 `_radius_at(z)` / `BODY_R` 决定 root body 的 revolve 半径，并被下游 rim torus 半径、lug pivot 半径 (`_radius_at(lug_z)`)、lid overhang (`LID_R = R_rim + 0.016`)、hinge_Y (`R_rim + 0.004`) 全部消费。
- **Slot B** 是 root body 的 wall 视觉层：要么把纹理烤进 shell（flutes），要么在 smooth shell 上叠加 `rib_{i}`/`ring_band_{i}` 复制视觉。接口是 body outer 半径面，与 lug/handle anchor 共面。
- **Slot C (lid)** 是定义性活动子件。接口点：**REVOLUTE** = 后 rim 线 `origin=(0, HINGE_Y, BODY_H)` axis `(-1,0,0)`，闭合时 skirt 套住 rolled rim（allow_overlap lid↔rim）。**PRISMATIC** = 盖盘心 `origin=(0,0,LID_SEAT_Z)` axis `(0,0,1)`，0..0.40 m 纯竖直 lift，skirt 下沉套 rim（allow_overlap lid↔rim+wall, expect_gap seat）。
- **Slot D (handle)** 挂在 body 侧壁 lug 上。FIXED ears：origin 在 lug，2× FIXED。swing bail sides：origin 在每侧 lug pivot `(lug_r·cosθ, lug_r·sinθ, lug_z)` axis 水平切向，2× REVOLUTE。overhead bail：单 REVOLUTE origin 在两 lug 中点 `(0,0,BAIL_LUG_Z)` axis `(1,0,0)`。
- **互斥/派生**：`top_open_rim` (Slot C) 移除 lid joint，因此必须搭配一个含 REVOLUTE 的 handle (`handle_swing_bail_sides`)，保证至少一个 non-fixed joint。其余 C×D 自由组合。pivot lug 是 inline body visual，但 handle 变体的 pivot lug 数量/位置随所选 handle module 走（FIXED ears=每侧1、bail ears=每侧2、overhead=两侧各1过顶）。

## 每槽位 Module Emits / Interfaces

### Slot A / profile_*（root body 半径函数，无独立 part）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（修改 can_body revolve 半径） | taper L55-L58 / straight L41 / barrel L58-L67 |
| internal joints | 无 | — |
| upstream interface | footprint disc @ z=0；root 坐标系 | parents L40-L52 |
| downstream interface | `_radius_at(z)`/`BODY_R` 供 wall/rim/lug/lid 半径消费 | taper L55-L58 |

### Slot B / surface_*（can_body wall 视觉层 + rib/ring multiplicity）
| emits | 描述 | 来源 |
|---|---|---|
| parts | body visual: `corrugated_wall` | `smooth_wall` | `smooth_wall`+`rib_{i}` | `smooth_wall`(Lathe)+`ring_band_{i}` | flutes L213-L225 / smooth L60-L116 / ribs L284-L301 / rings L206-L221 |
| internal joints | 无（复制视觉非 joint） | — |
| upstream interface | 接 root body outer 半径面 | — |
| downstream interface | outer 面供 lug/handle anchor；floor disc + rolled rim 共属 body | parents L226-L239 |

### Slot C / lid_*（lid_assembly 子件，定义性 joint）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid_assembly`（dome|disc-stack|flat disc + skirt + top loop/bail）；open_rim 无 part | dome L167-L203 / flat L167-L222 / open none |
| internal joints | `body_to_lid` REVOLUTE axis(-1,0,0) 0..100° | PRISMATIC axis(0,0,1) 0..0.40m | dome L276-L284 / flat L295-L303 |
| upstream interface | REVOLUTE: 后 rim 线 (0,HINGE_Y,BODY_H)；PRISMATIC: 盖盘心 (0,0,LID_SEAT_Z) | parents L51-L52 / flat L51 |
| downstream interface | closed skirt 套 rolled rim（allow_overlap；flat 另 expect_gap seat） | flat L356-L382 |

### Slot D / handle_*（提手子件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ring_handle_{side}`×2 | `bail_handle_{side}`×2 | `bail_handle_{i}`×2 | 单 `bail_handle`(2 arm+crossbar)；inline `lug_*` body visuals | ring L246-L266 / sides L234-L268 / overhead L316-L398 |
| internal joints | 2× FIXED | 2× REVOLUTE 侧 axis±Y 0..90° | 1× REVOLUTE axis(1,0,0) 0..170° | FIXED L260-L266 / sides L255-L268 / overhead L383-L398 |
| upstream interface | 挂 body 侧壁 lug pivot；origin 在 lug 接触面 | sides L252-L260 / overhead L389 |
| downstream interface | ring/arm 顶钩入 lug（allow_overlap handle↔lug/wall） | parents L394-L395 / openrim L381-L404 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_profile` | enum | {profile_tapered, profile_straight, profile_barrel} | profile_tapered | choice | deterministic procedural sampler | Slot A |
| `surface` | enum | {surface_vertical_flutes, surface_smooth, surface_horizontal_rings, surface_bold_ribs} | surface_vertical_flutes | choice | sampler；rib/ring multiplicity 仅在 flutes/bold_ribs/horizontal_rings 启用 | Slot B |
| `lid_top` | enum | {lid_dome_revolute, lid_dome_shallow_revolute, lid_flat_liftoff_prismatic, top_open_rim} | lid_flat_liftoff_prismatic | choice | sampler；top_open_rim 须配 swing_bail（见 inequality 行） | Slot C |
| `handle` | enum | {handle_two_ring_ears, handle_two_bail_ears, handle_swing_bail_sides, handle_overhead_bail} | handle_two_ring_ears | choice | sampler | Slot D |
| `palette_style` | enum | {bright_galvanized, weathered_galvanized, dark_zinc, painted_green, painted_silver, matte_charcoal} (≥4) | bright_galvanized | choice | 仅改 material rgba，不改拓扑 | parents L209-L216 (galv/galv_dark/wire) |
| `rib_count` (N axis) | int | [6, 44]（见 Multiplicity） | 由 surface 派生 | conditional | flutes:[24,44] trig 频率; bold_ribs:[6,16] 显式 loop; horizontal_rings:[8,20] (ring N) | parents L47 (40/28) / ribcount L42 (8) / horizontal L49 (14) |
| `body_h` | float | [0.60, 0.70] | 0.660 | independent | clamp | parents L43 |
| `r_top` (or BODY_R / R_RIM) | float | [0.165, 0.225] | 0.215 | independent | clamp；圆筒直径 ~0.40-0.50 | parents L41 |
| `r_bot` | float | derived | 0.170 | equation | taper: `= r_top - taper_drop`, `taper_drop∈[0.03,0.06]`; straight: `= r_top`; barrel: foot/rim 独立窄 | taper L41-L42 / barrel L43-L45 |
| `lid_r` | float | derived | r_top+0.016 | equation | `= R_rim + 0.016`（盖外悬 rim） | parents L49 |
| `hinge_y` | float | derived | r_top+0.004 | equation | `= R_rim + 0.004`（后铰在 rim 线） | parents L52 |
| `lift_max` | float | [0.30, 0.45] | 0.40 | independent | 仅 PRISMATIC lid；clamp | lidtype L52 |
| `lid_rise` | float | [0.04, 0.10] | 0.085 | independent | 仅 dome lid；clamp（dome 显著隆起 >0.07） | parents L48 |
| (—) | constraint | — | — | inequality | `top_open_rim ⇒ handle ∈ {handle_swing_bail_sides}`（保证 ≥1 non-fixed joint）；违反则改采 lid_flat_liftoff_prismatic 或重采 handle | slot graph |
| (—) | constraint | — | — | inequality | `R_inner = R_rim - amp - wall > 0.10`（hollow 腔体）；`(BODY_H - RIM_TUBE) - FLOOR_T > 0.45`（深腔）；违反回缩 R_rim/BODY_H | parents L332-L334 |
| (—) | constraint | — | — | inequality | barrel: `R_BULGE ≤ 0.090` 且 `min(R_RIM,R_FOOT)+0` ≥ lug 半径下限，避免 bulge 撞 handle clearance | barrel L43-L45 |

无 enum 表达未实现拓扑。所有 equation/inequality/conditional 在 `resolve_config` 求解。

## Multiplicity / Copy Logic

**轴 1：vertical rib / wall corrugation count（唯一 multiplicity 轴）**

- `count_param`: `rib_count`（按 surface module 解析的语义档）
- `N_range`（产品域，测试偏小、产品全程）:
  - `surface_vertical_flutes`: N ∈ [24, 44]（trig 频率，`ang_segs = n*4`；细 flutes）
  - `surface_bold_ribs`: N ∈ [6, 16]（显式 `rib_{i}` peaked-ridge 凸棱）
  - `surface_horizontal_rings`: N ∈ [8, 20]（水平 `ring_band_{i}` torus 数）
  - `surface_smooth`: N = 0（无复制）
- sampling domain（权重档）：小 N 高频、大 N 稀有；三档 distinct N 至少覆盖 {coarse≈8, medium≈14-16, fine≈28-40}。sweep 测试上限：bold_ribs ≤16、rings ≤20、flutes ≤44（角段 = N·4，避免 mesh 过密 SIGKILL）。
- copied object：
  - bold_ribs → `_bold_rib(angle)` peaked-ridge mesh（共享 helper），均布 `angle = 2π·i/N`，随 `_radius_at(z)` taper。
  - horizontal_rings → `_ring_band(z)` torus（共享 helper），z 均布于 `[ring_z0, ring_z1]`。
  - flutes → 不是显式 part，是 shell 角向调制（单参数 multiplicity，可接受，无独立 part 命名）。
- naming：`rib_{i}` / `ring_band_{i}`（i=0..N-1）。flutes 无 per-rib 命名。
- placement：bold_ribs 角向均布；rings 竖向均布；都贴 body outer 半径面。
- joint policy：**无 joint**——rib/ring 是 body-local parent visuals（inline 装饰），不暴露 `*_count` 以外的 joint。
- source/gating：bold_ribs L284-L301（rib_{i} loop）；rings L206-L221（ring_band loop）；flutes parents L84-L89（trig）。gate：N 仅在对应 surface module 启用（conditional）。

side handle / pivot lug 的 2× 复制（`for side_name,ang in …` / `for i in range(2)`）不是模板级 multiplicity 轴，而是 handle module 内部固定 2-side 对称（FIXED 或 REVOLUTE 各一致 joint policy）；overhead bail 内部 2-arm loop 同理（固定 2，非可变 N）。

## 拓扑多样性审计

总组合数：A(3) × B(4) × C(4) × D(4) = 192 structural；扣除 `top_open_rim` 须配 swing_bail：
- C≠open_rim: 3(C) × 4(D) = 12；C=open_rim: 1 × 1(D) = 1 → C×D 合法 = 13。
- A × B × (C×D legal) = 3 × 4 × 13 = **156** structural combos。
- × distinct rib-N 档（≥3，仅 B∈{flutes,bold_ribs,rings} 有 N，smooth 无）→ 远超阈值。


seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对所有普通 seed 用 deterministic procedural sampling——依次加权抽 body_profile、surface、lid_top、handle、palette_style，再对启用的 surface 抽 rib_count（小 N 偏多、尾部稀有），最后抽 independent 连续 scale（body_h, r_top, lid_rise/lift_max）→ 派生 r_bot/lid_r/hinge_y → 投影 hollow/深腔/clearance inequality → 解析 open_rim⇒swing_bail conditional。compatibility matrix 在抽样阶段 gate 掉 `open_rim × non-swing handle`。无大型 curated/modulo 主域；regression overrides 仅留给已知失败 seed。`seed=0` 不特殊。

Topology target：1000-seed distinct 富类别建议 ≥300（report-only）；本类别 156 structural × 多档 N 可达。random sweep：seeds 0-49 初轮、0-999 成熟度审计。

Controlled local parameterization：关键连续 scale = `body_h`、`r_top`（→派生 r_bot 保锥度/直筒/鼓肚）、`lid_rise`(dome)、`lift_max`(prismatic)、`taper_drop`、`R_BULGE`(barrel)。全部在 `resolve_config` clamp/派生，受 hollow（R_inner>0.10）、深腔（>0.45）、盖外悬（lid_r=R_rim+0.016）、hinge/seat origin 约束；不改未声明拓扑、不改 rib-N multiplicity 语义、不破坏 InterfaceSpec/MatingContract。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 顺序加权抽 A,B,C,D,palette,rib_N + 连续 scale；compatibility gate | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | open_rim ⇒ handle=swing_bail（否则无 non-fixed joint）；rib_N 仅对应 surface 启用；smooth→N=0 | 无 floating/无 lid 又无活动 handle/无 collision/joint 轴正确/closed pose seal |
| controlled local variation | body_h/r_top/lid_rise/lift_max/taper_drop/R_BULGE clamp+derive | 比例变化不破 hollow/深腔/盖外悬/hinge origin/identity |
| regression overrides | none（如出现失败再加，注明 seed+原因） | 仅已知失败/审核样本 |
| random sweep | seeds 0-49 初轮，0-999 成熟度 | 与 contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_profile | 3 | yes | yes | taper/straight/barrel |
| B surface | 4 | yes | yes | flutes/smooth/h-rings/bold-ribs |
| C lid_top | 4 | yes | yes | dome-rev/shallow-rev/flat-prismatic/open |
| D handle | 4 | yes | yes | ring-FIXED/bail-FIXED/swing-REV/overhead-REV |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名（A/B/C/D + rib_N 档）
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling；seed=0 不特殊
- compatibility gating：`open_rim ⇒ swing_bail`；rib_N 仅对应 surface；smooth⇒N=0
- regression overrides 稀疏且有理由（默认 none）
- 不无限轮换小 curated 表作为主 seed domain
- 连续 scale (body_h/r_top/lid_rise/lift_max/taper_drop/R_BULGE) 在 `resolve_config` clamp/派生，不破接口/clearance/joint origin/multiplicity
- 跨件 scale 依赖（r_bot=f(r_top)、lid_r=R_rim+0.016、hinge_y=R_rim+0.004、hollow/深腔不等式）在 `resolve_config` 解析
- 关键 InterfaceSpec/MatingContract 存在：footprint z=0、deep hollow cavity、lid closed seats over rim、handle anchored on lug face
- 关键 joint 语义：REVOLUTE lid axis=(-1,0,0) 0..100°；PRISMATIC lid axis=(0,0,1) 0..lift_max 无横移；swing bail axis 水平切向 0..90°；overhead bail axis=(1,0,0) 0..170°
- 复制对象遵守命名/placement：`rib_{i}` 角向均布、`ring_band_{i}` 竖向均布、handle 2-side 对称

## Reject cases

- 盖移除 (open_rim) 却配 FIXED ears → 无 non-fixed joint（hard fail；必须 swing_bail）
- PRISMATIC lid 抬升时有横移（xy 漂移 >0.005）或 axis 非 +Z
- 闭合 dome/flat lid 没套住 rolled rim（无 allow_overlap / 出现穿模报错），或 closed lid 不覆盖开口
- body 非 z≈0 footprint / 内壁 R_inner≤0.10 实心化失去 hollow 身份 / 深腔 <0.45
- bold_ribs 的 `rib_{i}` 不随 `_radius_at` taper（直插出锥体面）或 N 超 mesh 上限致 SIGKILL
- handle 不挂在可见 lug 面上（invisible mm-anchor pad）/ ring 不钩入 lug
- 引入 footed/wheeled base、step-pedal、spout 或方箱 dumpster 形态（越界相邻类别）
- 把 palette/material/纯尺寸缩放当结构 slot（伪 candidate）

## 与相邻类别的边界
- 不该混入 **Trashcan2 swing-lid street can**：固定壳 + 永久铰接 swing-flap，盖不可整体 lift-off。
- 不该混入 **Large_Trashcan wheelie bin**：塑料带轮 + 脚踏掀盖；reference 无脚无轮。
- 不该混入 **Garbage_bin dumpster**：大型方箱钢斗 + 叉举/侧举铰接，非小圆桶手提结构。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 共享 helper：`_floor_disc`、`_rolled_rim`、`_lug_pad` 全部 sample 通用；`_radius_at(z)` 是 Slot A 的核心切换点（barrel/straight 改其定义或换 BODY_R 常量）。
- surface module 决定 wall helper：flutes→`_corrugated_*_shell`(trig)，smooth/bold_ribs→`_smooth_tapered_shell`，horizontal→`LatheGeometry.from_shell_profiles`。bold_ribs/horizontal 在 smooth shell 上叠加复制视觉。
- lid PRISMATIC 是 canonical 身份 joint：local 帧原点 = 盖盘心 (z=0)，skirt 向 -Z 下沉套 rim，bail 向 +Z；`origin=(0,0,BODY_H+LID_DISC_T/2)`。closed seat 用 `expect_gap`(max_penetration≈0.025) + 双 `allow_overlap`(flat_lid↔rolled_rim, flat_lid↔corrugated/smooth_wall)。
- REVOLUTE lid local 帧原点 = 后铰线，body 向 -Y 伸出，axis=(-1,0,0) 使 free edge 上翻后摆。
- overhead bail：两 pivot lug + 两 arm 经 `for i in range(2)` 共享 `_bail_side_element`；arm 顶端在 captured-pin 区与 lug 小过盈 → element-scoped allow_overlap(bail_arm↔bail_lug)。
- open_rim：lug pad 随 handle module 走 loop（pivot lug 数随 handle），不要写死 ring-ear lug。
- rib/ring multiplicity 上限严格设小（bold_ribs≤16、rings≤20、flutes≤44）防 mesh 过密 SIGKILL（角段=N·4）。
