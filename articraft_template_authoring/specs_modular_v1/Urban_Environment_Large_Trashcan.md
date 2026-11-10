# Large Trashcan — Modular Spec (SPEC_ONLY_DRAFT)

## 元信息
| 项 | 值 |
|---|---|
| slug | `large_trashcan` |
| template path | `agent/templates/Urban_Environment_Large_Trashcan.py` |
| test path (optional) | `tests/agent/test_large_trashcan_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children wheels/casters + lid-count multiplicity; body shell + lift interface inlined as parent visuals) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (2 parents + 8 workbench variants) |
| source_index_policy | only adopted module sources are indexed below |

10 sources read in full. Two converged **parents** anchor the two structural families: **P1 wheelie** (`rec_gray-two-wheel-curbside-wheelie-trash-bin-lavex-…a2aacece`, 462 L) — tapered plastic shell + single domed lid + 2 rear wheels on a fixed axle + top grab lip; **P2 1100L** (`rec_large-commercial-waste-container-1100-liter-four…f6b001c4`, 559 L) — boxy steel shell + split twin lid + 4 swivel-stem casters + front DIN lift comb + side grab handles. The 8 workbench variants each isolate a single structural axis on one of the two parents: `four_caster_base` (2→4 casters, corner-list loop), `six_caster_long` (4→6 casters, layout-list loop), `split_twin_lid` (1→2 half-lids, sign loop), `triple_split_lid` (2→3 panels, slot-center loop), `single_flat_lid` (2→1 full-width lid), `front_lift_comb` (top-grip→trunnion bar + gussets), `side_grab_handles` (top-grip→two molded grips, sign loop), `boxy_body_profile` (tapered→boxy horizontal-corrugation shell). Shared idioms across all 10: `+Z` up, wheels touch `z=0`, front=`+X`, hinge at rear `-X` top rim, lid axis `(0,-1,0)` opens up/rearward, wheel/caster spin axis `(0,1,0)` CONTINUOUS, captured axle pins (`allow_overlap` axle↔hub), `_rrect` rounded-rect loft shells, skirt-laps-rim contact proof.

## 核心身份

A large wheeled curbside / commercial waste container: a hollow tapered-or-boxy **body shell** (240 L wheelie cart → 1100 L steel dumpster), **one or more rear-hinged flip lid(s)** (REVOLUTE about `-Y` at the rear top rim — the defining articulation), **N CONTINUOUS ground wheels/casters** (axis `+Y`) that touch `z=0`, and a **lift interface** (top grab lip / side grab handles / front DIN trunnion comb bar). Default mature domain: full-size mobile bins (~0.9–1.4 m tall), gray/green/blue plastic or steel, opened/closed at the lid hinge, rolled on its wheels. The lift comb / side handles / top grip are inlined static parent visuals, not separate articulated parts; the caster swivel kingpin is modeled as fixed-stem geometry (NOT a live DOF).

## 槽位 + 候选模块表

### Slot A：ground / wheel count N (滚动接地，CONTINUOUS spin)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| two_rear_wheels | rec_gray-two-wheel…a2aacece (P1) | L236-L342 | eligible if compatible | N=2 大轮 + 固定钢轴 + 模制后轴座 housing；`for name,sign` sign loop；axis `+Y` |
| four_casters | rec_large-commercial-1100…f6b001c4 (P2) | L186-L431 | eligible if compatible | N=4 角部 boss+swivel-pillar+fork 脚轮；`for sx in ±1: for sy in ±1` 嵌套 loop；trailing wheel |
| four_caster_base | rec_large_trashcan_var_four_caster_base | L79-L86 (corner list), L238-L425 | eligible if compatible | wheelie 车身改坐 4 脚轮；`CASTER_CORNERS` 4-pos list 驱动 `for i in range(n)`；short stem fork |
| six_caster_long | rec_large_trashcan_var_six_caster_long | L82-L93 (layout list), L101-L457 | eligible if compatible | 1100L 加中部一对脚轮 (4→6)；`CASTER_LAYOUT` 6-tuple list `(sx,sy)`，`sx=0` 中排 |

### Slot B：lid type / lid count multiplicity (后铰翻盖，REVOLUTE = defining joint)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_domed_lid | rec_gray-two-wheel…a2aacece (P1) | L181-L233 (mesh), L290-L311 (emit) | eligible if compatible | N=1 单片微拱翻盖 + 前抓边 + 下垂裙边；hinge 单点 `(HINGE_X,0,HINGE_Z)` |
| split_twin_lid | rec_large-commercial-1100…f6b001c4 (P2) | L255-L303 (mesh), L373-L400 (emit) | eligible if compatible | N=2 左右对开半盖；`for tag,sign` sign loop；共享 rear hinge X/Z，各盖偏 ±Y half |
| split_twin_on_wheelie | rec_large_trashcan_var_split_twin_lid | L81-L88 (consts), L190-L356 | eligible if compatible | wheelie 单盖→中线对开双半盖 (1→2)；`HALF_LID_SIGNS=(+1,-1)`，hinge Y-offset 分置；centerline gap |
| triple_split_lid | rec_large_trashcan_var_triple_split_lid | L75-L83 (slot centers), L267-L420 | eligible if compatible | N=3 顶面横向三片分盖；`LID_SLOT_CENTERS` 3-entry list 驱动 `for i in range(n)`；每片 hinge Y=slot center |
| single_full_width_lid | rec_large_trashcan_var_single_flat_lid | L254-L314 (mesh), L385-L408 (emit) | eligible if compatible | 1100L 双盖合并为一整片全宽平盖 (2→1)；单 hinge `(HINGE_X,0,HINGE_Z)` |

### Slot C：lift interface (起吊/抓取接口，inlined parent visuals — NO fixed-joint parts)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| top_grab_lip | rec_gray-two-wheel…a2aacece (P1) | L222-L231 (lip), L194-L199 (crown grip) | eligible if compatible | 盖前抓边 + 顶部微拱凹握；属于 lid visual，无独立 part |
| front_lift_comb | rec_large_trashcan_var_front_lift_comb | L77-L91 (consts), L197-L266 (gusset mesh), L329-L356 (emit) | eligible if compatible | 前面横向 DIN trunnion bar (Cylinder) + 两 trapezoidal gusset tie-plates 嵌入前壁；body visuals `trunnion_bar`/`gusset_{i}` |
| side_grab_handles | rec_large_trashcan_var_side_grab_handles | L77-L85 (consts), L270-L312 (handle mesh), L328-L345 (emit) | eligible if compatible | 两侧面外凸 molded grip bar + 2 mounting posts；`side_signs` sign loop；body visuals `side_handle_{i}` |
| front_comb_on_1100L | rec_large-commercial-1100…f6b001c4 (P2) | L153-L172 (comb + gussets) | eligible if compatible | 1100L 原生前 comb (Cylinder bar + 2 gusset box) co-present with side handles L174-L185；fused into shell mesh |

### Slot D：body profile (车身轮廓，inlined parent visual / shell mesh)

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| tapered_plastic | rec_gray-two-wheel…a2aacece (P1) | L88-L178 | eligible if compatible | 上宽下窄锥形塑壳 (loft BOT→TOP rrect) + 竖向前肋 `for yy in (...)` L145-L156 + rear axle housing |
| boxy_steel | rec_large-commercial-1100…f6b001c4 (P2) | L87-L152 | eligible if compatible | 近直壁方箱 + 横向波纹肋 `for zc in (...)` L135-L151 |
| boxy_corrugated_on_wheelie | rec_large_trashcan_var_boxy_body_profile | L57-L64 (rib list), L109-L137 (rib mesh), L141-L201 (shell), L310-L317 (emit) | eligible if compatible | wheelie 锥形→方箱；7 横波纹肋 collar 经 `_build_rib_mesh` 共享 helper + `for i,z in enumerate(RIB_Z_LIST)` |

所有 slot 均 ≥3 candidate，无单 candidate 槽，无降级理由需写。

## 槽位图（slot graph）

pattern: `mixed`

```
                         [Slot D body profile]  (root part `body`, static shell mesh)
                          tapered_plastic / boxy_steel / boxy_corrugated
                                    |
        +----------------+---------+----------+------------------+
        |                |                    |                  |
 [Slot C lift iface]  [Slot B lids]      [Slot A wheels]   (body.inertial)
 inlined body visuals  REVOLUTE child(ren)  CONTINUOUS children
 top_grip / comb /     axis (0,-1,0)        axis (0,1,0)
 side_handles          @ rear top rim       @ ground z=0
                       HINGE_X,*,HINGE_Z     N positions
```

- **Root**: Slot D `body` part is the static root; Slots A/B/C all attach to it (parallel children + inlined visuals).
- **Slot B → body (defining joint)**: each lid panel is a REVOLUTE child; joint origin = `(HINGE_X, y_center, HINGE_Z)` at the rear (`-X`) top rim; axis `(0,-1,0)`; the lid mesh frame puts the hinge edge at local origin and the plate extends `+X` so `-Y` lifts the free front edge up/back (P1 L301-L311, P2 L390-L400). Multiplicity: N lids share `HINGE_X/HINGE_Z`, split equally across width via per-panel `y_center` (single → Y=0; twin → ±offset; triple → slot centers).
- **Slot A → body**: each wheel/caster is a CONTINUOUS child; joint origin at the wheel center `(±CASTER_X, ±CASTER_Y, CASTER_Z=R)` so contact patch sits at `z=0`; axis `(0,1,0)`; spin RPY orients WheelGeometry/TireGeometry local-X spin to world `+Y` (`-pi/2` left vs `+pi/2` right, P1 L318, P2 L406). The axle/stem (boss+pillar+fork or rear housing) is fused into the body shell mesh; a short steel pin Cylinder is a body visual captured in the hub bore (`allow_overlap` axle↔wheel, P1 L440-L457, P2 L531-L554).
- **Slot C → body**: lift interface is inlined. `top_grab_lip` lives on the lid mesh (degrades to part of Slot B); `front_lift_comb` and `side_grab_handles` are extra `body.visual` calls (`trunnion_bar`/`gusset_{i}` or `side_handle_{i}`), NOT articulated parts.
- **Slot D**: changes the root shell mesh + which ribs are emitted; affects body AABB and where the rim/hinge/axle anchors land. Mutually exclusive (one profile per build).
- **Compatibility**: Slot A/B/C/D are independent; the only gates are scale-domain (a 2-wheel rear-axle ground works on the smaller tapered body; 4/6 casters work on either body but 6 needs a deeper body — see compatibility matrix). Caster swivel is NOT a DOF.

## 每槽位 Module Emits / Interfaces

### Slot A / two_rear_wheels (P1)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `left_wheel`,`right_wheel` (WheelGeometry+TireGeometry) | P1 L314-L333 |
| internal joints | `left_wheel_spin`,`right_wheel_spin` CONTINUOUS axis `(0,1,0)` effort5/vel20 | P1 L334-L342 |
| upstream interface | spin origin `(AXLE_X, ±HALF_AXLE_Y, AXLE_Z=R)`; rear axle housing fused in shell | P1 L160-L176, L339 |
| downstream interface | captured axle Cylinder body-visual in hub bore (`allow_overlap`) | P1 L278-L283, L440-L457 |

### Slot A / four_casters (P2) & four_caster_base & six_caster_long
| emits | 描述 | 来源 |
|---|---|---|
| parts | `caster_{tag}` / `caster_{i}` each WheelGeometry+TireGeometry | P2 L403-L421, four_base L387-L410, six L426-L455 |
| internal joints | `*_spin` CONTINUOUS axis `(0,1,0)` per caster | P2 L422-L430, four_base L411-L417, six L447-L453 |
| upstream interface | spin origin from corner/layout list; boss+pillar+fork fused into shell mesh | P2 L186-L251, four_base L238-L294, six L101-L296 |
| downstream interface | per-caster captured axle pin Cylinder body-visual (`axle_{tag}`/`axle_{i}`) | P2 L357-L366, six L378-L389 |

### Slot B / single_domed_lid (P1) & single_full_width_lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid` (domed/flat plate + skirt + front grab lip) | P1 L181-L233 / single_flat L254-L314 |
| internal joints | `lid_hinge` REVOLUTE axis `(0,-1,0)` lower0 upper~1.9 | P1 L301-L311 / single_flat L399-L408 |
| upstream interface | hinge origin `(HINGE_X,0,HINGE_Z)` rear top rim; lid frame hinge-edge at origin, plate→+X | P1 L292-L306 / single_flat L385-L404 |
| downstream interface | closed: skirt laps rim lip (`allow_overlap`+`expect_contact`) | P1 L411-L420 |

### Slot B / split_twin_lid (P2) & split_twin_on_wheelie
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid_left`,`lid_right` / `half_lid_{i}` half-width plates | P2 L375-L389 / twin L326-L342 |
| internal joints | `{tag}_hinge` REVOLUTE axis `(0,-1,0)` per half | P2 L390-L400 / twin L344-L353 |
| upstream interface | shared hinge X/Z; P2 both at Y=0 with half plate offset, wheelie hinge Y at ±`HINGE_Y_OFFSET` | P2 L381-L395 / twin L335-L349 |
| downstream interface | lids split across centerline (`lids_split_y`); each laps rim | P2 L494-L512 / twin tests |

### Slot B / triple_split_lid
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid_0/1/2` panels via `for i in range(len(LID_SLOT_CENTERS))` | triple L395-L405 |
| internal joints | `lid_{i}_hinge` REVOLUTE axis `(0,-1,0)`, origin `(HINGE_X, slot_center_i, HINGE_Z)` | triple L412-L420 |
| upstream interface | `LID_SLOT_CENTERS=[-SLOT_W,0,+SLOT_W]` Y centers; panel width `SLOT_W-gap` | triple L75-L83, L396-L404 |
| downstream interface | 3 panels cover full top, count-asserted | triple L479-L483 |

### Slot C / top_grab_lip / front_lift_comb / side_grab_handles
| emits | 描述 | 来源 |
|---|---|---|
| parts | none — all inlined body/lid visuals | — |
| visuals (top) | lid front lip box + crown grip | P1 L194-L199, L222-L231 |
| visuals (comb) | `trunnion_bar` Cylinder + `gusset_{i}` trapezoidal tie-plates fused to front wall | comb L197-L266, L329-L356 |
| visuals (handles) | `side_handle_{i}` grip bar + 2 posts, sign loop, proud of ±Y faces | handles L270-L312, L328-L345 |
| interface | comb bar X at front-face tip (truck arm hook); handles standoff proud of side wall; no joints | comb L89-L91 / handles L329-L337 |

### Slot D / tapered_plastic / boxy_steel / boxy_corrugated
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body` root static shell mesh (loft rrect BOT→TOP, hollow, rim) | P1 L88-L178 / P2 L87-L130 / boxy L141-L201 |
| visuals | vertical front ribs (`for yy`) OR horizontal corrugations (`for zc` / `RIB_Z_LIST` loop) | P1 L145-L156 / P2 L135-L151 / boxy L310-L317 |
| upstream interface | provides rim top (`BODY_TOP_Z`) for hinge, base (`BODY_BOTTOM_Z`) + corners for wheels | all parents L65-L80 |
| downstream interface | body.inertial Box; AABB sanity (tapered ~0.9 m, boxy 1.05–1.4 m) | P1 L284-L288 / P2 L367-L371 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| ground_choice | enum | two_rear_wheels / four_casters / six_casters | — | choice | procedural sampler; gated by body size | Slot A table |
| lid_choice | enum | single / split_twin / triple | — | choice | procedural sampler | Slot B table |
| lift_choice | enum | top_grab_lip / front_lift_comb / side_grab_handles | — | choice | procedural sampler | Slot C table |
| body_profile | enum | tapered_plastic / boxy_steel | — | choice | procedural sampler; gates wheel/scale | Slot D table |
| palette_style | enum | municipal_gray / forest_green / civic_blue / hazard_orange / hospital_white / industrial_charcoal | municipal_gray | choice | ≥3 required, 6 provided | P1 L263-L267 / P2 L333-L337 |
| wheel_count | int | {2,4,6} | (per ground_choice) | conditional | 2 only if body tapered & small; 4/6 either body; 6 needs body_depth≥0.95 | A table multiplicity |
| lid_count | int | {1,2,3} | (per lid_choice) | conditional | 3 needs body_width≥0.9 (clean equal split) | B table multiplicity |
| body_height_scale | float | [0.92,1.10] | 1.0 | independent | clamp; scales `BODY_H` | P1 L48 / P2 L52 |
| body_width_scale | float | [0.92,1.12] | 1.0 | independent | clamp; scales `BODY_W/TOP_W` | P1 L50 / P2 L50 |
| body_depth_scale | float | [0.95,1.10] | 1.0 | independent | clamp; scales `BODY_D/TOP_D` | P1 L51 / P2 L51 |
| wheel_radius_scale | float | [0.90,1.12] | 1.0 | equation | `CASTER_Z = R·scale`; `BODY_BOTTOM_Z` re-derived so wheels touch z=0 | P1 L57/L64 / P2 L58-L66 |
| rib_count | int | derived | (sampler) | conditional | corrugation count = `floor(BODY_H/RIB_SPACING)`; cosmetic, sampler's job | boxy L57-L64 |
| (—) | constraint | — | — | inequality | wheel contact: `min_z(wheel) ≈ 0` after scale → re-solve `BODY_BOTTOM_Z = wheel_top + stem`; reject if `<0.012` violated | P1 L385-L392 / P2 L473-L477 |
| (—) | constraint | — | — | inequality | lid clearance: `Σ panel_W ≤ TOP_W + 2·overhang`; equal split `panel_W = (TOP_W+over)/N - gap` | P2 L374-L381 / triple L77-L78 |
| (—) | constraint | — | — | inequality | caster non-collision: fork/pillar X-band kept behind tire (`pillar_x = wxx - sx·tire_back_dx`); mid-row (sx=0) trails +X | P2 L196-L250 / six L101-L130 |

palette_style ≥3 target 4-6 → **6 colorways** provided. Each maps `(body, lid, wheel/tire, steel/accent)` rgba bundles (body+lid shades from P1 L263-L264 / P2 L333-L334; wheel/tire black from P1 L265-L266; steel accent P1 L267 / P2 L335).

## Multiplicity / Copy Logic

本模板有 **2 根独立 multiplicity 轴**：wheel_count (Slot A) 和 lid_count (Slot B)。

### 轴 1 — wheel_count (Slot A)
- count_param: `wheel_count`
- N_range: 产品域 `{2, 4, 6}`（离散；测试偏 2/4，6 稀有）
- sampling domain: 加权 — N=4 最常见 (~45%)，N=2 (~35%)，N=6 (~20% rare/long-body)
- copied object: 轮/脚轮 part (`left_wheel`/`right_wheel` 或 `caster_{i}`) + 各自 CONTINUOUS spin + 各自 captured axle pin body-visual
- naming: N=2 用 sign loop `for name,sign in (("left_wheel",1),("right_wheel",-1))` (P1 L314); N=4/6 用 list-driven `for i in range(n)` over `CASTER_CORNERS`/`CASTER_LAYOUT` → `caster_{i}` + `axle_{i}` (four_base L387, six L426)
- placement: N=2 后轴一对 `(AXLE_X, ±HALF_AXLE_Y)`; N=4 底四角 `(±CASTER_X, ±CASTER_Y)`; N=6 四角 + 中排 `(0,±CASTER_Y)` (six L86-L93)；轮心 z=R 触地
- joint policy: 每个轮 = CONTINUOUS axis `(0,1,0)`，effort5 vel20；swivel kingpin NOT a DOF
- source/gating: N=2 ↔ tapered small body only; N=6 ↔ `body_depth_scale·BODY_D ≥ 0.95` (mid casters need depth)

### 轴 2 — lid_count (Slot B)
- count_param: `lid_count`
- N_range: 产品域 `{1, 2, 3}`（测试偏 1/2，3 稀有）
- sampling domain: 加权 — N=1 (~40%)，N=2 (~40%)，N=3 (~20%)
- copied object: lid panel part + 各自 REVOLUTE hinge
- naming: N=1 `lid` 单 part；N=2 sign loop `for tag,sign` → `lid_left/lid_right` 或 `half_lid_{i}` (P2 L375 / twin L326); N=3 list loop over `LID_SLOT_CENTERS` → `lid_{i}` (triple L395)
- placement: 共享 `HINGE_X/HINGE_Z`（rear top rim）；按 N 等分宽度 — N=1 Y=0 全宽; N=2 Y center ±`HALF_LID_W/2`; N=3 Y=`{-SLOT_W,0,+SLOT_W}`
- joint policy: 每盖 = REVOLUTE axis `(0,-1,0)`, lower0 upper~1.9（开向上/后）— **defining joint**
- source/gating: N=3 ↔ `body_width_scale·TOP_W ≥ 0.9`（三等分需足够宽，避免窄条）

### 轴 (cosmetic, NOT forked) — rib/corrugation count
- 两 parent 都 loop-emit 多肋（P1 vertical `for yy`, P2 horizontal `for zc`, boxy `for i,z in RIB_Z_LIST`）；count = `floor(BODY_H/spacing)` 由 sampler 派生，不开独立 fork 轴（map 已声明）。

## 拓扑多样性审计

总组合数：Slot A(4 candidate, 含 distinct N {2,4,6}) × Slot B(5 candidate, 含 distinct N {1,2,3}) × Slot C(4 candidate) × Slot D(3 candidate)。
保守地按 **distinct-N × lift × profile** 计结构等价类：wheel-N{2,4,6}(3) × lid-N{1,2,3}(3) × lift{top,comb,handles}(3) × profile{tapered,boxy}(2) = **54** distinct topology classes（远超 map 的 27 下界，因把 D 算进去）。

理由：54 ≫ 10。即使只采 wheel-N × lid-N × lift = 3×3×3 = 27（map HARD GATE 已审为 PASS），也满足。distinct N 在两根轴上各贡献 3 个值，single-axis sweep 即可越过门槛。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 对每个普通 seed 各做 — (1) 加权抽 Slot D body_profile；(2) 加权抽 wheel_count 轴（按 §Multiplicity 权重，受 profile gate）；(3) 加权抽 lid_count 轴（受 width gate）；(4) 抽 Slot C lift_choice；(5) 抽 palette_style；(6) 采 independent scales → 派生 wheel_radius/BODY_BOTTOM_Z equation → 投影 inequality（接地、lid clearance、caster non-collision）。`slot_choices_for_seed` 返回 `[(A,module),(B,module),(C,module),(D,module)]` + 两个 count，不记录连续 scale。`seed=0` 不特殊。Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；54 结构类 × 离散 N 按该口径观察。低于 300 时说明类别本就只有 ~54 真结构类，连续 scale 不计入 tuple；不设门。

Controlled local parameterization：`body_height_scale [0.92,1.10]`、`body_width_scale [0.92,1.12]`、`body_depth_scale [0.95,1.10]`、`wheel_radius_scale [0.90,1.12]`（equation→re-derive BODY_BOTTOM_Z 保接地）。所有 scale 在 `resolve_config` clamp/派生/投影；跨部件依赖（轮半径↔车底高、N↔宽度/深度 gate）显式声明为 equation/inequality/conditional，不当作独立自由变量。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | weighted: profile→wheel_N(gated)→lid_N(gated)→lift→palette; counts in slot_choices | slot_choices_for_seed matches build (part names + N) |
| compatibility matrix | N=2↔tapered-small only; N=6↔depth≥0.95; lid_N=3↔width≥0.9; swivel NOT DOF; lift inlined | no floating wheel, no fork/pillar tire collision, no narrow lid sliver, no closed-pose seal |
| controlled local variation | 4 body scales + wheel_radius (equation) clamped | proportions vary; wheels stay on z=0; hinge stays on rim; lids cap top |
| regression overrides | none | — |
| random sweep | seeds 0-49 initial; 0-999 maturity | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A ground/wheel-N | 4 | yes | yes | distinct N {2,4,6} |
| B lid type/count | 5 | yes | yes | distinct N {1,2,3} |
| C lift interface | 4 | yes | yes | inlined visuals |
| D body profile | 3 | yes | yes | tapered/boxy/corrugated |

## Validator

- `slot_choices_for_seed` returns implemented module names + (wheel_count, lid_count)
- `config_from_seed` uses deterministic procedural sampling for all ordinary seeds (seed=0 not special)
- compatibility matrix prevents illegal combos (N=2 on big steel body; lid_N=3 on narrow body; mid casters without depth)
- no regression overrides
- controlled scales clamped/derived in `resolve_config`; wheel_radius→BODY_BOTTOM_Z equation keeps wheels on z=0; cross-part deps resolved before builder
- InterfaceSpec/MatingContract points exist: lid hinge on rear top rim; wheel spin at ground; captured axle pin in hub bore; lift comb/handle proud of wall
- key joints: lid `lid*_hinge` REVOLUTE axis `(0,-1,0)` lower0 upper~1.9; wheel `*_spin` CONTINUOUS axis `(0,1,0)`
- copied objects follow naming/placement: sign loop (N=2) / list loop (`caster_{i}`,`lid_{i}`); lids share HINGE_X/Z, split by y_center; wheels at corner positions z=R
- closed lid caps body top (`expect_overlap` xy) + laps rim (`allow_overlap`+`expect_contact`); open lid rises & swings rearward
- captured axle/wheel `allow_overlap` declared per wheel (element-scoped)

## Reject cases

- lid hinge axis not `(0,-1,0)` or hinge not at rear top rim → lid opens wrong way / floats
- wheel/caster spin axis not `(0,1,0)`, or wheel min_z far from 0 → not on ground (forgot BODY_BOTTOM_Z re-derive after wheel_radius_scale)
- swivel kingpin promoted to a real DOF (must stay fixed-stem geometry)
- lift comb / side handles / top grip emitted as articulated parts instead of inlined body/lid visuals
- lid_count=3 on a narrow scaled body → sub-0.2 m slivers / overlapping panels
- fork pillar/leg geometry entering the tire envelope (must stay above/behind/outside tire), or N=6 mid casters with insufficient body depth
- closed lid sealing the mouth with no `allow_overlap`/`expect_contact` rim proof, or lid not covering top (`expect_overlap` xy fail)
- sampling a module combo not implemented, or `slot_choices_for_seed` disagreeing with built part names/counts

## 与相邻类别的边界

- 不该混入：**Garbage_bin / 商业 dumpster**（理由：dumpster 是固定大铁箱，可有顶盖但典型无地面行走轮 + 用叉车口/钩臂，不是 curbside 可推的 wheeled bin；本类身份核心是 CONTINUOUS 地轮 + 推行）。
- 不该混入：**Trashcan1 / Trashcan2 街头小桶**（理由：街头垃圾桶是固定立柱/无轮小容器，无 REVOLUTE 翻盖+地轮组合；本类必须有 wheeled base + rear-hinged lift lid + lift interface 三件套，尺寸 ≥0.9 m）。
- 边界内保持：始终是 wheeled trash bin（不扩展成 swivel-DOF 推车、无轮固定箱、或带踏板/感应开盖的室内小桶）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- Slot A N=2 用 sign loop，N≥4 用 list loop；建议实现时统一成 list-of-positions（N=2 也写两条目），减少分支。
- 共享 helper：`_rrect` rounded-rect loft（全部 10 源通用）；`_build_lid_mesh(half_w)` 参数化半宽供 single/twin/triple 复用（P2 L255 already parametric）；`_caster_frame(sx,sy)` 计算 fork/pillar X（six L101）。
- captured-pin overlap 必须 element-scoped per wheel (`elem_a=axle_{i}, elem_b=wheel`)；勿用全局 allow_overlap。
- 关键 InterfaceSpec：lid hinge 共享 `(HINGE_X,*,HINGE_Z)`；wheel spin `(...,CASTER_Z=R·scale)` 必须随 wheel_radius_scale 一起 re-derive `BODY_BOTTOM_Z`，否则接地断言失败。
- 暂不进入 seed domain：caster swivel DOF、室内踏板/感应机构、可拆轮——非本类身份。
