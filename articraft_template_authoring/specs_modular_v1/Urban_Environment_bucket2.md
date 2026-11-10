# bucket2 — Wooden Keg / Barrel (Urban Environment)

## 元信息
| 项 | 值 |
|---|---|
| slug | `bucket2` |
| template path | `agent/templates/Urban_Environment_bucket2.py` |
| test path (optional) | `tests/agent/test_bucket2_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (surface-of-revolution root + named-slot closure + N-multiplicity hoop array + optional carry-handle joint) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category (parent + 7 converged variants) |
| source_index_policy | only adopted module sources are indexed below |

读取的 8 个样本（全部 5★，全部读完整 `model.py`）：

| id | 角色 | 主要贡献 module |
|---|---|---|
| `rec_small-wooden-keg-barrel-with-staved-bulged-body-_20260608_164508_499567_ad0a147f` | parent / baseline | bulged body + 2 hand-written hoops + slide-off lid (PRISMATIC) + arched grip |
| `rec_bucket2_var_straight_keg` | body 变体 | constant-radius cylinder profile (`_outer_radius` returns `R_BODY`) |
| `rec_bucket2_var_tapered_pail` | body 变体 | linear taper profile (`R_BASE→R_MOUTH`), renamed `pail_body` |
| `rec_bucket2_var_hoop_count` | multiplicity | `for i in range(N)` hoop loop, `_hoop_z_positions(n)`, `body_to_hoop_{i}` FIXED |
| `rec_bucket2_var_hinged_lid` | closure | lid REVOLUTE about rear-rim Y axis, hinge-frame lid mesh |
| `rec_bucket2_var_bunghole_plug` | closure | fixed top head + side bunghole + tapered bung, radial PRISMATIC |
| `rec_bucket2_var_swing_bail` | handle | 2 FIXED pivot ears (`for i in range(2)`) + swept bail, REVOLUTE about X |
| `rec_bucket2_var_side_ear_rings` | handle | 2 FIXED ears + 2 fold-out rings, each own REVOLUTE about X |

共同骨架（所有 8 个一致）：`barrel_body` 为 root（XZ profile `.revolve(360,(0,0,0),(0,1,0))`，实心 floor `FLOOR_T`，`N_STAVES=16` 槽刻成 cosmetic stave 缝），FIXED 金属 hoop 环，最终一个非 FIXED 关节（lid / bung / bail / ring）承载身份动作。`BODY_H=0.360`，base 坐 z=0，mouth 在 z=BODY_H。

## 核心身份

**主身份：开口空心木桶 / 木盆（open hollow wooden bucket / pail）**——大多数 seed 是 `closure=open_top`：桶口完全敞开、无盖封顶，口沿有一道收边木唇环（rim_lip），透过宽口能看到很深的中空 staved 内腔（内壁明显高，floor 降低加深 cavity）。其 ≥1 非 fixed 关节由 **carry handle**（swing_bail / side_ear_rings，REVOLUTE）承载（open_top 自身无关节）。带盖 keg + bunghole 变体作为**少数多样性变体**保留（仍中空、盖在上）。

旧身份（少数变体）：一个小型**木制 staved keg / barrel**（木桶 / 啤酒桶 / 小琵琶桶）。身体是绕世界 +Z 的 surface of revolution：竖直木板（staves）拼成的 bulged（中部鼓出）/ straight（直筒）/ tapered（锥形）外壳，外表面刻有 `N_STAVES` 条竖直 stave 缝沟，底部为实心木 floor（FLOOR_T 闭合，桶身中空但不漏底）。身体由 **N 个深色金属 hoop 环带**箍紧（multiplicity 轴）。顶部有 closure（可滑离 / 铰接掀开的 lid，或固定 head + 侧面拔塞 bung），加上可选的 carry handle（lid 上固定拱形把手 / swing bail / 折叠环耳）。**非 fixed 关节由 closure（lid / bung）或 carry handle（bail / ring）承载** —— 这是 keg/barrel 身份动作。

成熟域：小型木桶（高 ~0.3-0.45 m，半径 ~0.12-0.20 m），木色 + 金属箍配色，2-4 道箍。

## 槽位 + 候选模块表

### Slot A：body_profile（vessel 外形；surface of revolution 的 `_outer_radius(z)` 决定结构外形，非纯缩放）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `bulged_barrel` | parent `rec_small-wooden-keg-...ad0a147f` | L72-L113（`_outer_radius` 抛物鼓出 + `_build_body_mesh`） | eligible if compatible | 对称抛物中鼓 `R_END=0.150→R_MID=0.186`；13 段 outer / 12 段 inner profile revolve；mouth 半径 = R_END |
| `straight_keg` | `rec_bucket2_var_straight_keg` | L71-L113（`_outer_radius` 返回 `R_BODY`，2 点直壁 profile） | eligible if compatible | 恒定半径 `R_BODY=0.150` 直筒，竖直外壁，无 belly；mouth 半径 = R_BODY |
| `tapered_pail` | `rec_bucket2_var_tapered_pail` | L73-L115（`_outer_radius` 线性 taper，groove 用 `r_mid`） | eligible if compatible | 线性锥 `R_BASE=0.120→R_MOUTH=0.180`，宽口窄底；mouth 半径 = R_MOUTH |

所有三者共用同一 revolve / floor / stave-groove builder，仅 `_outer_radius(z)` profile 函数和 mouth 半径不同 → 下游 rim/lid/hoop 半径全部由 `_outer_radius` 派生，slot 切换不破坏接口。

### Slot B：hoop_count_N（multiplicity 轴 —— loop-emit `hoop_{i}`）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `hoop_array_N` | `rec_bucket2_var_hoop_count` | L79-L87（`_hoop_z_positions(n)`）+ L234-L246（part loop）+ L270-L277（FIXED joint loop） | eligible if compatible | `for i in range(N)` 生成 `hoop_0..hoop_{N-1}`，共享 `_build_hoop_mesh(name,z)` helper，`_hoop_z_positions` 均匀 z-pitch（首末距端 `HOOP_MARGIN=0.050`），统一 `body_to_hoop_{i}` FIXED |

distinct-N = 3（N ∈ {2,3,4}）。N=2 即 parent 的 upper/lower 双箍语义；N=3/4 为多箍 keg。单 candidate slot 的降级理由：multiplicity slot 的「结构差异」来自不同的 distinct-N（2/3/4 各产生不同 part-count 与 joint-count 拓扑等价类），而非不同 mesh family；parent 的两条 hand-written hoop（`upper_hoop`/`lower_hoop`，L222-L237 of parent）已被 loop 重写吸收，是同一 module 的 N=2 实例，不另立 candidate。

### Slot C：closure（主机构 —— 口部 finish / 开闭动作；保留 ≥1 非 fixed）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 / 关键关节 |
|---|---|---|---|---|
| `open_top` (PRIMARY, weight 0.58) | new — 开口空心身份 | `_emit_open_top`（emits 无 part 无 joint）+ `_open_rim_mesh`（body rim_lip 环）+ 降低 floor | eligible only with handle∈{swing_bail, side_ear_rings} | 桶口全开、无盖；body 加 `rim_lip` 收边木唇环（annular lathe，bore=内腔半径，口不被盖住）；floor 降到 `_OPEN_FLOOR_T=0.014` 加深可见中空腔；**自身无关节**，≥1 非 fixed 关节由 handle 承载 |
| `slide_off_lid` | parent `...ad0a147f` | L155-L178（lid mesh）+ L278-L286（PRISMATIC +Z）+ L116-L133（rim ledge） | eligible if compatible | 木 lid（flange + 下垂 plug），沿 +Z 直拔离 mouth；`body_to_lid` PRISMATIC axis (0,0,1)，limits 0→`LID_TRAVEL=0.12` |
| `hinged_lid` | `rec_bucket2_var_hinged_lid` | L163-L192（hinge-frame lid，圆心偏到 `(R_FLANGE,0)`）+ L299-L307（REVOLUTE） | eligible if compatible | lid 绕后缘 Y 轴掀起；`body_to_lid` REVOLUTE，origin `(HINGE_X=-R_FLANGE,0,BODY_H)`，axis (0,-1,0)，0→`LID_OPEN_ANGLE=1.50` rad |
| `bunghole_plug` | `rec_bucket2_var_bunghole_plug` | L157-L174（tapered bung mesh）+ L124-L135（fixed top head）+ L230-L244（radial PRISMATIC） | eligible if compatible | 固定木 head 封顶 + 侧壁 bunghole + tapered bung 径向拔出；`body_to_bung` PRISMATIC axis (1,0,0)，origin `(_outer_radius(BUNG_Z),0,BUNG_Z)`，0→`BUNG_TRAVEL=0.065` |

### Slot D：handle / carry（保留 ≥1 非 fixed；视 closure 而定可为 none）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 / 关键关节 |
|---|---|---|---|---|
| `lid_arched_grip` | parent `...ad0a147f` | L181-L201（arched grip mesh）+ L290-L296（FIXED on lid） | eligible if compatible（仅 lid closure） | 两腿 + 横梁拱形把手，FIXED 在 lid 顶，随 lid 动；无独立关节 |
| `swing_bail` | `rec_bucket2_var_swing_bail` | L163-L180（ear+pin mesh）+ L183-L216（swept bail）+ L269-L291（2 FIXED ears loop）+ L330-L337（REVOLUTE bail） | eligible if compatible | 两枚 FIXED pivot ear（`for i in range(2)`，左右 ±X）+ 横跨 bail 把手；`body_to_bail` REVOLUTE，origin `(0,0,Z_EAR)`，axis (1,0,0) |
| `side_ear_rings` | `rec_bucket2_var_side_ear_rings` | L166-L195（fork ear mesh）+ L197-L218（torus ring）+ L273-L306（2 ears FIXED + 2 rings each REVOLUTE） | eligible if compatible | 两枚 FIXED fork ear（`for i in range(2)`，±X）+ 各自一枚折叠 ring；每个 `ear_{i}_to_ring_{i}` REVOLUTE axis (1,0,0)，0→`RING_UPPER=1.80` rad |
| `no_handle` | 派生 / 折入 | bunghole `body` head 即顶面（L188 of bung，无 handle 部件） | eligible if compatible（与 bunghole_plug 搭配） | closure=bunghole 时顶为固定 head，无 carry handle；非独立 mesh，degrade 选项 |

注：`open_top` 自身无关节，其 ≥1 非 fixed 关节**必须**来自 handle，故仅与 `swing_bail` / `side_ear_rings`（均 REVOLUTE）兼容，**不**配 `lid_arched_grip`（需 lid）或 `no_handle`（无关节）；`lid_arched_grip` 是 lid 的子件（FIXED），仅在 closure ∈ {slide_off_lid, hinged_lid} 时合法；`swing_bail` / `side_ear_rings` 挂在 body，与任意 closure 兼容；`no_handle` 仅在 closure=bunghole_plug 时作 fallback（避免 fixed-head 桶上凭空长把手）。

## 槽位图（slot graph）

pattern: mixed（root 单体 + 主机构命名 slot + N 复制 + 可选 carry 关节）

```
                  barrel_body (ROOT, surface of revolution about +Z, base@z=0)
                  └ visual: staved shell + rim_ledge | top_head (closure-dependent)
                  │
   [Slot B ×N]    ├──[FIXED, origin (0,0,0)]──> hoop_0 .. hoop_{N-1}   (均匀 z-pitch, wraps body)
                  │
   [Slot C]       ├──[closure joint, mounts at mouth/wall]──> closure part
                  │      · slide_off_lid : PRISMATIC +Z   @ (0,0,BODY_H)
                  │      · hinged_lid    : REVOLUTE (0,-1,0) @ (HINGE_X,0,BODY_H)
                  │      · bunghole_plug : PRISMATIC +X (radial) @ (r(BUNG_Z),0,BUNG_Z)
                  │
   [Slot D]       └──[carry, body- or lid-mounted]──> handle part(s)
                         · lid_arched_grip : FIXED on barrel_lid  (lid closures only)
                         · swing_bail      : ear_0/ear_1 FIXED on body (±X) → bail REVOLUTE about X @ (0,0,Z_EAR)
                         · side_ear_rings  : ear_{i} FIXED on body (±X) → ring_{i} REVOLUTE about X each
                         · no_handle       : (bunghole only) none
```

接口点位：
- **Slot B → body**：hoop 半径 = `_outer_radius(z_center)`（自动随 body_profile），FIXED origin (0,0,0)，z-overlap ≥ 0.01 wrap body。
- **Slot C → body mouth/wall**：lid closures 的 mating face = mouth top 平面 z=BODY_H + `rim_ledge` 内座；lid flange 半径 = `_outer_radius(BODY_H) - 0.003`；plug 半径派生自 mouth 内壁。bunghole 的 mating face = 侧壁外面 z=BUNG_Z 处，固定 head 封 mouth（用 `top_head` 取代 rim_ledge+lid）。
- **Slot D → body / lid**：ears 挂在 `_outer_radius(Z_EAR)` 的 ±X 外面（FIXED），pivot 轴沿世界 X；grip 挂 lid 顶面（FIXED，随 lid PRISMATIC/REVOLUTE 动）。
- 互斥/派生：closure=bunghole_plug ⇒ body 加 `top_head` visual、去掉 `rim_ledge`；Slot D 此时取 `swing_bail` / `side_ear_rings` / `no_handle`（不取 lid_arched_grip）。

## 每槽位 Module Emits / Interfaces

### Slot A / barrel_body（所有 profile 共用，root）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `barrel_body`（staved shell + rim_ledge 或 top_head visual） | parent L213-L220 / L116-L133 |
| internal joints | 无（root） | — |
| upstream interface | base footprint @ z=0（world ground） | parent L86-L93 |
| downstream interface | mouth top 平面 z=BODY_H + `rim_ledge` 内座（lid 用）；侧壁外面（bung/ear 用）；`_outer_radius(z)` 半径函数供下游派生 | parent L116-L133, L159-L162 |

### Slot B / hoop_array_N
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hoop_0..hoop_{N-1}`（每个 `_build_hoop_mesh`，dark_metal） | hoop_count L234-L246 |
| internal joints | `body_to_hoop_{i}` FIXED origin (0,0,0) | hoop_count L270-L277 |
| upstream interface | wraps body 外面 @ `_outer_radius(z_i)`，`_hoop_z_positions(N)` 均匀 z | hoop_count L79-L87 |
| downstream interface | 无（叶节点） | — |

### Slot C / slide_off_lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | `barrel_lid`（flange + 下垂 plug，lid_wood） | parent L155-L178 |
| internal joints | `body_to_lid` PRISMATIC axis (0,0,1) 0→0.12 | parent L278-L286 |
| upstream interface | flange 底面 @ q=0 坐 mouth top z=BODY_H（flush，plug 进 rim 内座 allow_overlap） | parent L239-L249, L377-L390 |
| downstream interface | lid 顶面 @ z=LID_FLANGE_T 供 grip 把手挂载 | parent L251-L258 |

### Slot C / hinged_lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | `barrel_lid`（hinge-frame：圆心偏 `(R_FLANGE,0)`，铰边在原点） | hinged L163-L192 |
| internal joints | `body_to_lid` REVOLUTE axis (0,-1,0) @ (HINGE_X,0,BODY_H)，0→1.50 rad | hinged L299-L307 |
| upstream interface | q=0 lid 平躺座 mouth；铰链接触线在后缘 rim top | hinged L258-L268 |
| downstream interface | lid 顶面供 grip 挂载（local 圆心 (R_FLANGE,0)） | hinged L270-L277 |

### Slot C / bunghole_plug
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bung_plug`（tapered loft，bung_wood）；body 追加 `top_head` visual（fixed head） | bung L157-L174 / L124-L135 |
| internal joints | `body_to_bung` PRISMATIC axis (1,0,0) @ (r(BUNG_Z),0,BUNG_Z)，0→0.065 | bung L230-L244 |
| upstream interface | bung 外面 @ q=0 与侧壁外面齐平；bunghole bore 穿壁（BUNG_HOLE_R<3·WALL） | bung L293-L306 |
| downstream interface | 无（fixed head ⇒ Slot D 不取 lid grip） | bung L177-L193 |

### Slot D / lid_arched_grip
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid_handle`（两腿+横梁拱，handle_blue） | parent L181-L201 |
| internal joints | `lid_to_handle` FIXED（随 lid 动） | parent L290-L296 |
| upstream interface | 腿脚嵌入 lid 顶面（allow_overlap，expect_contact tol 0.006） | parent L402-L415 |
| downstream interface | 无 | — |

### Slot D / swing_bail
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ear_0`/`ear_1`（plate+pin，dark_metal）+ `bail_handle`（swept wire，bail_metal） | swing L163-L216 |
| internal joints | `body_to_ear_{i}` FIXED ×2（`for i in range(2)`，±X）；`body_to_bail`（或 ear→bail）REVOLUTE axis (1,0,0) @ (0,0,Z_EAR) | swing L269-L291, L330-L337 |
| upstream interface | ears 嵌入 `_outer_radius(Z_EAR)` ±X 外面（allow_overlap）；bail 端点架在 pin 上 | swing L269-L291 |
| downstream interface | 无 | — |

### Slot D / side_ear_rings
| emits | 描述 | 来源 |
|---|---|---|
| parts | `ear_0`/`ear_1`（fork bracket）+ `ring_0`/`ring_1`（torus，dark_metal） | side L166-L218 |
| internal joints | `body_to_ear_{i}` FIXED ×2（±X）；`ear_{i}_to_ring_{i}` REVOLUTE axis (1,0,0)，0→1.80 ×2 | side L273-L306 |
| upstream interface | ears 嵌入 ±X 外面；ring pivot 在 fork prong 间 | side L266-L291 |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_profile` | enum | {bulged_barrel, straight_keg, tapered_pail} | — | choice | deterministic procedural sampler；决定 `_outer_radius(z)` 与 mouth 半径 | Slot A 表 |
| `closure` | enum | {slide_off_lid, hinged_lid, bunghole_plug} | — | choice | sampler；非 fixed 关节来源 | Slot C 表 |
| `handle` | enum | {lid_arched_grip, swing_bail, side_ear_rings, no_handle} | — | choice | sampler，受 compatibility gate（见下） | Slot D 表 |
| `N_HOOPS` | int | [2, 4]（distinct N=3） | 2 | multiplicity | 加权采样（小 N 偏多）；clamp [2,4] | hoop_count L56, L79-L87 |
| `body_height_scale` | float | [0.85, 1.20] | 1.0 | independent | `BODY_H *= s`，clamp；rim/lid/hoop/bung z 全派生 | parent L45 |
| `body_radius_scale` | float | [0.85, 1.20] | 1.0 | independent | 缩放 R_END/R_MID 或 R_BODY 或 R_BASE/R_MOUTH | parent L46-L47 |
| `bulge_ratio` | float | [1.05, 1.30] | 1.24 | conditional | 仅 bulged_barrel；`R_MID = R_END * bulge_ratio`，clamp（保证 mid>end） | parent L47 |
| `taper_ratio` | float | [0.55, 0.85] | 0.67 | conditional | 仅 tapered_pail；`R_BASE = R_MOUTH * taper_ratio` | tapered L47-L48 |
| `lid_travel_scale` | float | [0.8, 1.3] | 1.0 | independent | slide_off_lid 行程 `LID_TRAVEL`；clamp，保证 open lid 越 mouth | parent L65 |
| `hinge_open_angle` | float | [1.2, 1.55] rad | 1.50 | independent | hinged_lid `LID_OPEN_ANGLE`；clamp ≤1.55（<90°，不翻越铰） | hinged L68 |
| `bung_travel_scale` | float | [0.8, 1.4] | 1.0 | independent | bunghole `BUNG_TRAVEL`；clamp，保证拔出越壁 | bung L66 |
| `ring_open_angle` | float | [1.4, 1.85] rad | 1.80 | independent | side_ear_rings `RING_UPPER` | side L84 |
| `wall_thickness` | float | derived | 0.016 | equation | `WALL = 0.016 * body_radius_scale`，保持 inner_r>0.10 | parent L48 |
| (—) | constraint | — | — | inequality | `WALL < 0.5·_outer_radius(BODY_H)` 且 `inner_r = _outer_radius(BODY_H)-WALL > 0.10`；违反则回缩 radius/wall | parent L338-L344 |
| (—) | constraint | — | — | inequality | hoop 不重叠：`HOOP_MARGIN ≥ HOOP_HALF_H` 且 `pitch = (BODY_H-2·HOOP_MARGIN)/(N-1) ≥ 2·HOOP_HALF_H`（N=4 时收紧 margin） | hoop_count L86 |
| (—) | constraint | — | — | inequality | bunghole 在腰带间：`FLOOR_T+0.02 < BUNG_Z < BODY_H-0.02` 且 `BUNG_HOLE_R < 3·WALL`；BUNG_Z 避开 hoop z-band | bung L293-L306 |
| `palette_style` | enum | {oak_iron, dark_stain_iron, weathered_iron, oak_brass, light_ash_iron, dark_stain_brass}（≥4 colorway） | oak_iron | choice | 见下 palette 表；只改材质，不改拓扑 | parent L207-L210 |

### palette_style 配色（≥3，目标 4-6）
| style | 木 body rgba | lid/head 木 | hoop 金属 | 把手/bail accent |
|---|---|---|---|---|
| oak_iron (default) | (0.74,0.52,0.32) | (0.80,0.60,0.39) | dark iron (0.16,0.17,0.19) | (0.20,0.30,0.45) blue grip |
| dark_stain_iron | (0.40,0.26,0.16) | (0.46,0.30,0.19) | dark iron (0.16,0.17,0.19) | (0.22,0.22,0.24) |
| weathered_iron | (0.62,0.50,0.38) gray-wash | (0.66,0.54,0.42) | rusted iron (0.34,0.22,0.16) | (0.28,0.28,0.30) |
| oak_brass | (0.74,0.52,0.32) | (0.80,0.60,0.39) | brass (0.72,0.58,0.24) | brass (0.72,0.58,0.24) |
| light_ash_iron | (0.82,0.70,0.52) | (0.86,0.74,0.56) | dark iron (0.16,0.17,0.19) | (0.20,0.30,0.45) |
| dark_stain_brass | (0.40,0.26,0.16) | (0.46,0.30,0.19) | brass (0.72,0.58,0.24) | brass (0.72,0.58,0.24) |

连续尺寸采样契约：先采 independent（height/radius/travel/angle scales）→ 派生 equation（WALL，R_MID/R_BASE 由 ratio）→ 投影 inequality（wall/inner_r、hoop pitch、bung 位置）→ 解析 conditional（bulge/taper 仅对应 profile）。所有约束在 `resolve_config` 求解。

## Multiplicity / Copy Logic

**轴 1：hoop_count（唯一 multiplicity 轴）**
- `count_param`: `N_HOOPS`，Slot B。
- `N_range`: 产品域 [2, 4]，distinct-N = 3。测试偏小（N=2/3 高频，N=4 稀有）。
- sampling domain: 加权 `{2: 0.45, 3: 0.40, 4: 0.15}`（小 N 高频，4 箍 keg 稀有）。
- copied object: `hoop_{i}` 金属环带（`_build_hoop_mesh(name, z)`）。
- naming: `hoop_0 .. hoop_{N-1}`，joint `body_to_hoop_{i}`。
- placement: `_hoop_z_positions(N)` 均匀 z-pitch，首末距端 `HOOP_MARGIN`，半径 = `_outer_radius(z_i)`（随 body_profile）。
- joint policy: 每个 FIXED，origin (0,0,0)，axis 无；z-overlap ≥0.01 wrap body；allow_overlap（coopered fit 嵌木）。
- source/gating: hoop_count L79-L87 / L234-L246 / L270-L277；clamp N∈[2,4]，N=4 收紧 HOOP_MARGIN 以保 pitch≥2·HOOP_HALF_H。

**次级 fixed loops（非 multiplicity 轴，固定 2 个）**：swing_bail 与 side_ear_rings 各用 `for i in range(2)` 生成左右 pivot ear（uniform per-side policy，±X 对称），ear count 固定为 2，不暴露为参数。

**staves**：`N_STAVES=16` groove loop 是 body 上的 cosmetic 单体特征（刻在一个 fused mesh 上），**不是** jointed part 轴，不暴露 count 参数。

## 拓扑多样性审计

总组合数（考虑 closure→handle 兼容门控 + distinct-N）：
- closure=slide_off_lid：handle ∈ {lid_arched_grip, swing_bail, side_ear_rings} = 3
- closure=hinged_lid：handle ∈ {lid_arched_grip, swing_bail, side_ear_rings} = 3
- closure=bunghole_plug：handle ∈ {swing_bail, side_ear_rings, no_handle} = 3
合法 (closure,handle) 对 = 9；× body_profile(3) × distinct-N(3) = **9 × 3 × 3 = 81 ≥ 10 ✓**

仅结构 slot：closure(3) × hoop_N(3) = 9，再 × body(3) = 27 ≥ 10。distinct-N = 3。

理由：closure × hoop_N alone = 9，加 body_profile 即 27 distinct 拓扑等价类（part-tree / joint-type / joint-count 都不同），远超 10。每个 closure 改变非 fixed joint 的 type/axis（PRISMATIC+Z / REVOLUTE-Y / PRISMATIC+X）；每个 handle 改变 part-count 与 joint topology（FIXED grip vs 2 ears+1 REVOLUTE bail vs 2 ears+2 REVOLUTE rings）；N 改变 hoop part/joint 数。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 对所有普通 seed 用 deterministic procedural sampling：先抽 body_profile → closure → handle（受 compatibility gate）→ N_HOOPS（加权）→ palette_style → 连续 scales。compatibility matrix（见下）剔除非法组合（lid grip 不挂 bunghole；bunghole 顶 fixed head 时不长 lid grip）。`seed=0` 不特殊。无大规模 regression override 表。random sweep：seeds 0-49 初轮，0-999 成熟审计。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别合法拓扑等价类上限 = 81（9×3×3，连续 scale 不计入拓扑等价类），低于 300 是因为类别本身组合域有限（3 slot enum × 3 N），已说明；81 distinct 已充分覆盖。
Controlled local parameterization：初版包含 `body_height_scale`、`body_radius_scale`、`bulge_ratio`/`taper_ratio`（conditional）、`lid_travel_scale`/`hinge_open_angle`/`bung_travel_scale`、`ring_open_angle`、派生 `wall_thickness`。全部在 `resolve_config` clamp/派生，受 wall/inner_r、hoop pitch、bung 位置、joint range 不等式约束，不破坏 InterfaceSpec/multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | order body→closure→handle(gated)→N(weighted)→palette→scales | slot_choices_for_seed matches build choices |
| compatibility matrix | lid_arched_grip ⇔ closure∈{slide_off_lid,hinged_lid}；swing_bail/side_ear_rings any closure；no_handle ⇔ closure=bunghole_plug；bunghole ⇒ body+top_head, 去 rim_ledge | no floating handle, no lid-grip on fixed head, hoop no-overlap, bung pierces wall |
| controlled local variation | height/radius/ratio/travel/angle scales，clamp 见参数表 | proportions vary; mouth/lid/hoop/bung interfaces, clearance, joint range, keg identity 不破坏 |
| regression overrides | none | — |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | , contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_profile | 3 | yes | yes | bulged / straight / tapered |
| B hoop_count_N | 1 module / distinct-N=3 | yes | yes (distinct-N) | multiplicity 轴，结构差异来自 N∈{2,3,4} |
| C closure | 3 | yes | yes | slide PRISMATIC / hinge REVOLUTE / bung PRISMATIC-radial |
| D handle | 4 | yes | yes | grip / bail / rings / none(gated) |

## Validator

- slot_choices_for_seed returns implemented module names（body_profile / closure / handle / N_HOOPS）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating prevents illegal combos（lid grip on fixed-head bunghole；floating handle）
- optional regression overrides are sparse and justified（none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params are clamped（wall/inner_r、hoop pitch、bung 位置、joint range）不破坏 interfaces/identity
- cross-part scale deps（wall=f(radius)、R_MID/R_BASE=ratio·R、hoop pitch、bung z）resolved in `resolve_config`
- critical interface points exist：mouth top 平面、rim_ledge 内座 / top_head、hoop wrap、bung bore 穿壁、ear ±X 外面
- key joints have expected type/axis/range：body_to_lid（PRISMATIC+Z 0→travel | REVOLUTE-Y 0→angle）、body_to_bung（PRISMATIC+X 0→travel）、body_to_bail/ear→ring（REVOLUTE about X）、hoop/ear/grip FIXED
- copied objects follow naming/placement：hoop_0..hoop_{N-1} 均匀 z-pitch FIXED；ear_0/ear_1 ±X 对称 FIXED

## Reject cases

- closure=bunghole_plug 仍生成 lid_arched_grip 或 rim_ledge（fixed head 上凭空长把手 / 双顶面冲突）。
- N_HOOPS 超 [2,4] 或 N=4 时 hoop pitch < 2·HOOP_HALF_H（相邻箍穿插）。
- body_radius_scale 过大使 `WALL ≥ 0.5·_outer_radius(BODY_H)` 或 `inner_r ≤ 0.10`（壁不再是薄壳 / 桶实心）。
- slide_off_lid 的 LID_TRAVEL 缩到 open lid z-min < BODY_H（开盖未越 mouth，仍盖着）。
- hinged_lid open angle ≥ π/2 使 lid 翻越铰链穿入 body；或 axis 写错方向使 q>0 lid 下沉穿桶。
- bunghole BUNG_Z 落在某 hoop z-band 内（bung 与金属箍穿插）或 BUNG_HOLE_R ≥ 3·WALL（孔过大破壁）。
- swing_bail / side_ear_rings 的 ear 半径与 `_outer_radius(Z_EAR)` 不一致（ear 悬空或埋入过深）；或 bail/ring REVOLUTE axis 非世界 X（摆动方向错）。
- body_profile 切换后 lid flange / hoop / bung 半径未由 `_outer_radius` 派生（接口脱节、lid 不座 mouth）。
- barrel base 不在 z=0（桶悬空 / 沉地）。

## 与相邻类别的边界

- 不该混入：**bucket1（sheet-metal fire bucket / 镀锌提桶）**。bucket1 是薄金属冲压桶（圆锥光滑壁、卷边、铆接吊耳、单一 swing bail），**无木 staves、无 stave 缝沟、无金属 hoop 箍、无 lid/bung closure**。bucket2 身份是**木 staved keg/barrel + 金属 hoop 箍 + closure(lid/bung)**；若失去 stave 缝或 hoop 箍即退化成 bucket1，必须保留 `N_STAVES` 缝 + ≥2 hoop 箍。
- 不该混入：**通用 pail / 无盖光滑桶**。tapered_pail candidate 仍保留 staves + hoops + closure，不是光滑塑料 / 镀锌桶；不要去掉 hoop 箍或把 body 做成光滑无缝壳。
- 不该混入：**barrel-shaped trash can / planter**（大型、无金属 hoop coopered 细节、无 bung）。本类别保持小型 coopered 木桶尺度（高 ~0.3-0.45 m）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | bulged_barrel | rec_small-wooden-keg-...ad0a147f | L72-L113 | profile + floor + stave-groove body builder（baseline 骨架） |
| S2 | A | straight_keg | rec_bucket2_var_straight_keg | L71-L113 | 恒定半径 profile |
| S3 | A | tapered_pail | rec_bucket2_var_tapered_pail | L73-L115 | 线性 taper profile |
| S4 | B | hoop_array_N | rec_bucket2_var_hoop_count | L79-L87, L234-L246, L270-L277 | N-loop hoop 复制 + 均匀 z-pitch + FIXED joint loop |
| S5 | C | slide_off_lid | rec_small-wooden-keg-...ad0a147f | L155-L178, L278-L286, L116-L133 | lid mesh + PRISMATIC+Z + rim_ledge |
| S6 | C | hinged_lid | rec_bucket2_var_hinged_lid | L163-L192, L299-L307 | hinge-frame lid + REVOLUTE-Y |
| S7 | C | bunghole_plug | rec_bucket2_var_bunghole_plug | L124-L135, L157-L174, L230-L244 | fixed top head + tapered bung + radial PRISMATIC |
| S8 | D | lid_arched_grip | rec_small-wooden-keg-...ad0a147f | L181-L201, L290-L296 | 拱形把手 + FIXED on lid |
| S9 | D | swing_bail | rec_bucket2_var_swing_bail | L163-L216, L269-L291, L330-L337 | 2 FIXED ears + swept bail REVOLUTE-X |
| S10 | D | side_ear_rings | rec_bucket2_var_side_ear_rings | L166-L218, L273-L306 | 2 FIXED fork ears + 2 ring REVOLUTE-X |

## 模板实现备注（可选）
- Slot A 三 profile 共用同一 revolve/floor/stave-groove helper，只切换 `_outer_radius(z)` 与 mouth 半径；rim/lid/hoop/bung 半径全部 `_outer_radius` 派生，避免接口脱节。
- closure=bunghole_plug 时 body 用 `top_head` visual 取代 `rim_ledge`，并把 Slot D gate 到 {swing_bail, side_ear_rings, no_handle}。
- captured-pin / 嵌入 overlap 需 element-scoped allow_overlap：hoop↔body（coopered fit）、lid plug↔rim、handle 脚↔lid、ear↔body、（swing_bail）bail 端↔pin。每个 closure/handle 组合都要在 test 中复制对应 allow_overlap（参考 parent L386-L407 / hoop_count L425-L442）。
- swing_bail / side_ear_rings 的 ear loop 固定 2 个（±X 对称），不抽象成 multiplicity 轴；唯一 multiplicity 轴是 hoop_count。
