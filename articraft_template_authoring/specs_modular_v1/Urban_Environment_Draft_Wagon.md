# Draft Wagon — Modular Template Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `draft_wagon` |
| template path | `agent/templates/Urban_Environment_Draft_Wagon.py` |
| test path (optional) | `tests/agent/test_draft_wagon_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children chassis + multiplicity wheels/spokes/planks) |

`pattern` 说明：root `body` 是 chassis/bed；wheels 和（4 轮时）steering `front_bolster` 作为 parallel children 挂上去；spoke/plank/board/stake/hoop 都是 module-local multiplicity 复制。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11 |
| read_count | 11 |
| read_scope | all 5-star samples in this category (3 grid parents + 8 converged variants) |
| source_index_policy | only adopted module sources are indexed below |

全部 11 个 model.py 完整读取。共享结构家族：所有样本用同一 `_wheel_visuals(part, prefix, [radius,] wood, dark_wood, iron)` helper（felloe rim = closed `tube_from_spline_points`，radial spokes = `Cylinder` loop，`hub` + `hub_band`），所有 wheel-spin 关节 = CONTINUOUS world-Y，所有 4-wheel 样本共享 `front_bolster` + REVOLUTE world-Z `front_steer` + `kingpin_boss`/`bolster_beam`/`front_axle`/`standard_*`。bed 永远是 root `body` 上的 plank 复制（`floor_plank_{i}` 沿 X，side/end 墙板按高度 stack）。差异轴：wheel_config（轮/轴 station 数 + 是否有 steering bolster）、spoke_count、side-wall 形态（板数/footprint）、top cover（gabled roof / canvas tilt / drop tailgate / open）。

## 核心身份

木质 draft / farm 货运 wagon 或 hand cart：一个 plank cargo bed/tub（敞开或带盖）骑在大号 spoked wooden wheels 上的拖拉/手推车。覆盖三个成熟域：(1) 2-wheel hand cart / dray（单后轴 + 前撑腿 + pull shafts），(2) 4-wheel open farm wagon（steerable 前 bolster + 固定后轴 + draw poles），(3) 4-wheel covered caravan/vardo（同 4 轮底盘 + 高 cabin 墙 + 顶盖）。

DEFINING MOTION：wheels rolling = CONTINUOUS spin about world Y（永远存在，PRIMARY）；4-wheel 成员另加 steering front axle = REVOLUTE yaw about world Z（front bolster 携带前轮对 + draw poles）。永远有 forward pull handle/shafts 或 draw pole。所有不动细节（iron strapping、rope tie、swingletree、hub band、勾撑腿）是 parent visual，不是独立 part。

不该混入（见末节边界）：Caster_Trolley（小脚轮 + push handle，非大 spoked wheel、非 steering axle）、Tipping_Barrow（单轮独轮车 + 双撑腿，tub 绕前轴 tip）。

## 槽位 + 候选模块表

### Slot A：wheel_config（PRIMARY rolling topology — 决定 wheel/axle station 数 + 是否有 steering bolster）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_axle_two_wheel | rec_two-wheeled-wooden-hand-cart-tip-cart-dray-with-_20260608_164414_778806_b1d205ac | L255-L290 (wheels+joints), L196-L226 (axle+legs) | eligible if compatible | 1 后轴 stub on `body`, 2 wheel parts (`left_wheel`/`right_wheel`), 2× CONTINUOUS Y `*_wheel_spin`，无 bolster，前撑腿 props + 2 pull shafts |
| single_axle_two_wheel_dray | rec_draft_wagon_var_single_axle_two_wheel_dray | L255-L284 | eligible if compatible | 同 single-axle 但 wheels 折成 `for i in range(2)` 循环（`wheel_{i}` + `wheel_{i}_spin`），无 bolster；规范化的 2-wheel 折叠形式 |
| four_wheel_steered | rec_four-wheeled-wooden-farm-wagon-cart-with-two-pai_20260608_164439_774589_56699604 | L194-L330 | eligible if compatible | `front_bolster` part + REVOLUTE Z `front_steer` (L280-L288) + 4 wheels：rear pair child of `body`，front pair child of bolster；`kingpin_boss` on body, `front_axle`+`standard_*` on bolster；front 轮小于 rear 轮 |
| six_wheel_triple_axle | rec_draft_wagon_var_six_wheel_triple_axle | L46-L54 (axle stations), L266-L314 | eligible if compatible | `N_AXLES=3` 站点（front steerable + mid + rear fixed），6 wheels 经 `for i in range(N_AXLES)`×2 sides 循环（`wheel_{i}_{side}` + `spin_{i}_{side}`），station 0 child of bolster，其余 child of body |

### Slot B：spoke_count（wheel-internal multiplicity, N 轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| spokes_8 | rec_draft_wagon_var_heavy_eight_spoke_wheels | `_wheel_visuals` spoke loop (spoke_count=8) | eligible if compatible | `for s in range(8)` 粗 cartwheel spokes；radial `Cylinder`，pitch=`pi/2-a` |
| spokes_10 | rec_four-wheeled-covered-wooden-wagon-caravan-with-a_20260608_164450_131123_085f4a98 | L76-L88 | eligible if compatible | `spoke_count=10` in helper loop |
| spokes_12 | rec_four-wheeled-wooden-farm-wagon-cart-with-two-pai_20260608_164439_774589_56699604 | L73-L85 | eligible if compatible | `spoke_count=12`（farm + hand-cart 共用此默认；hand-cart `SPOKE_COUNT=12` @ L41/L88-L100） |
| spokes_16 | rec_draft_wagon_var_fine_sixteen_spoke_wheels | `_wheel_visuals` spoke loop (spoke_count=16) | eligible if compatible | `for s in range(16)` 纤细 spoke 轮 |

### Slot C：bed_sidewall（cargo bed 墙板 multiplicity + footprint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| low_three_plank_rails | rec_four-wheeled-wooden-farm-wagon-cart-with-two-pai_20260608_164439_774589_56699604 | L130-L167 | eligible if compatible | side `for k in range(3)`，end `for k in range(3)`，4 corner posts；低 open box（SIDE_WALL_H≈0.30） |
| tall_back_wall | rec_two-wheeled-wooden-hand-cart-tip-cart-dray-with-_20260608_164414_778806_b1d205ac | L146-L185 | eligible if compatible | side `range(3)` 低 + 后墙 `range(4)` 高板 + 2 back posts + front_rail；非对称（hand-cart 身份） |
| high_sided_grain_box | rec_draft_wagon_var_high_sided_grain_box | L56-L60 (params), L138-L175 | eligible if compatible | `N_WALL_BOARDS=6` side+end stacked boards（`_wall_board` helper），深墙 SIDE_WALL_H≈0.55 grain hauler |
| flat_rack_stake_bed | rec_draft_wagon_var_flat_rack_stake_bed | L61-L65 (params), L110-L185 | eligible if compatible | 无连续墙板，改 perimeter `stake_{i}` posts（`_stake_post_geometry` LatheGeometry tenon-taper）经 `N_SIDE_STAKES`/`N_END_STAKES` 计数循环绕 deck 边缘 |

### Slot D：top_cover（顶部形态 — 部分候选加真实关节）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| open_none | rec_four-wheeled-wooden-farm-wagon-cart-with-two-pai_20260608_164439_774589_56699604 | (no roof emit) | eligible if compatible | 无顶盖；敞开 box（degrade baseline） |
| gabled_plank_roof | rec_four-wheeled-covered-wooden-wagon-caravan-with-a_20260608_164450_131123_085f4a98 | L180-L229 | eligible if compatible | `ridge_beam` + 两 `*_roof_panel`（tilt box，roll=∓slope_angle）+ 4 `*_gable_*` 三角端填；body visual，无关节 |
| canvas_bow_tilt_cover | rec_draft_wagon_var_canvas_bow_tilt_cover | L61-L192 (helpers), L311-L330 | eligible if compatible | `N_HOOPS` semicircular bow `hoop_{i}`（`_build_bow_template` clone+translate 循环）+ draped `canvas_tilt` double-surface MeshGeometry；body visual，无关节 |
| drop_tailgate_open_box | rec_draft_wagon_var_drop_tailgate_open_box | L206-L248 (tailgate part), L388-L399 (hinge) | eligible if compatible | 独立 `tailgate` part（3 `tailgate_plank_{k}` + battens + iron hinge straps）+ REVOLUTE world-Y `tailgate_hinge` @ 后底边，lower=0 upper=pi/2 drop ramp |

## 槽位图（slot graph）

pattern: mixed（parallel_children chassis + module-local multiplicity）

```
                          (Slot B spoke_count drives every wheel's _wheel_visuals)
                                          │
  Slot A wheel_config ──> root `body` (bed/chassis)
     │                         │  ├─[Slot C bed_sidewall: plank/board/stake multiplicity ON body]
     │                         │  └─[Slot D top_cover: gabled/canvas = body visual;
     │                         │        drop_tailgate = REVOLUTE Y child part; open = none]
     │                         │
     ├─ 2-wheel members: 2× wheel parts ──[CONTINUOUS world-Y @ body rear axle stubs]──> body
     │     (no bolster; front prop legs + 2 pull shafts are body visuals)
     │
     └─ 4/6-wheel members: `front_bolster` ──[REVOLUTE world-Z `front_steer` @ kingpin under bed front]──> body
            ├─ front wheel pair ──[CONTINUOUS world-Y @ bolster front_axle]──> front_bolster
            ├─ draw poles / rope tie / swingletree = bolster visuals (steer with it)
            └─ mid/rear wheel pairs ──[CONTINUOUS world-Y @ body axle stubs]──> body
```

接口点位：
- **wheel→axle mount**：wheel `hub` 套在 parent 的 `axle`/`rear_axle`/`front_axle`/`axle_{i}` cylinder stub 上（local hub-through-axle 过盈，element-scoped `allow_overlap` hub & hub_band），joint origin = `(axle_x, ±HALF_TRACK, axle_z)`，axis=(0,1,0)，`axle_z = wheel_r + RIM_TUBE_R` 保证 rim 触地 z=0。
- **bolster→body kingpin turntable**：`kingpin_boss`（body 下，front_axle_x）seats into `bolster_beam`（`allow_overlap` kingpin_boss×bolster_beam, ×front_axle, ×draw_pole），`front_steer` origin=`(front_axle_x, 0, bolster_z)`，axis=(0,0,1)，range ±0.6。
- **front wheel local frame**：bolster child 的 front-wheel joint origin 写在 bolster local frame（`axle_local_z = FRONT_AXLE_Z - bolster_z`）。
- **bed_sidewall ON body**：plank/board/stake 全是 body visual，root 在 `BED_FLOOR_Z + FLOOR_THK/2`，无跨 slot 关节。
- **tailgate hinge**：`tailgate_hinge` origin=`(-BED_LEN/2, 0, BED_FLOOR_Z+FLOOR_THK/2)`，axis=(0,-1,0)，仅当 Slot D=drop_tailgate_open_box 时存在。

互斥 / 派生：
- Slot A=single_axle_two_wheel(_dray) 时 **无 bolster、无 steering**，且 Slot D ∈ {open_none, drop_tailgate_open_box}（hand-cart/dray 不带 gabled/canvas cabin；见 compatibility matrix）。Slot D=drop_tailgate 在 2-wheel 时 hinge 仍挂 body 后底边。
- Slot A∈{four_wheel_steered, six_wheel_triple_axle} 时 bolster + REVOLUTE steer 必有。
- Slot C=flat_rack_stake_bed 时 Slot D 应 ∈ {open_none, canvas_bow_tilt_cover}（stake deck 无连续墙承不住 gabled cabin / tailgate；degrade 到 open）。

## 每槽位 Module Emits / Interfaces

### Slot A / module single_axle_two_wheel(_dray)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wheel_{0,1}`（or left/right） | dray L261-L269 |
| internal joints | `wheel_{i}_spin` CONTINUOUS axis Y range ∞ | dray L271-L280 |
| upstream interface | child of `body`，origin `(AXLE_X, ±WHEEL_HALF_TRACK, AXLE_Z)` | dray L277 |
| downstream interface | hub 套 body `axle` stub；body 提供 front prop legs + pull shafts (body visuals) | hand-cart L196-L253 |

### Slot A / module four_wheel_steered
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_bolster`，`rear_left/right_wheel`，`front_left/right_wheel` | farm L195, L274-L277 |
| internal joints | `front_steer` REVOLUTE Z (±0.6)；4× `*_spin` CONTINUOUS Y | farm L280-L330 |
| upstream interface | bolster child of body @ `(FRONT_AXLE_X,0,bolster_z)`；rear wheels child of body | farm L280-L308 |
| downstream interface | front wheels child of bolster @ bolster-local；draw poles/rope tie = bolster visuals | farm L231-L261, L313-L330 |

### Slot A / module six_wheel_triple_axle
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_bolster`，`wheel_{i}_{l,r}` for i in 0..2 | six L266-L279 |
| internal joints | `front_steer` REVOLUTE Z；6× `spin_{i}_{side}` CONTINUOUS Y（station 0 child bolster, 其余 body） | six L284-L314 |
| upstream interface | `AXLE_X=[0.70,-0.10,-0.90]`，spacing > Σ 相邻 wheel_r 防 rim 撞 | six L46-L54 |
| downstream interface | hub 套 `axle_{i}` stub；mid/rear `axle_{i}` on body | six L341-L353 |

### Slot B / module spokes_{8,10,12,16}
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；改写 `_wheel_visuals` spoke loop 上限 | caravan L76-L88 |
| internal joints | 无 | — |
| upstream interface | spoke 内端在 `HUB_R-0.015`，外端 `radius+0.004` 物理连 hub→felloe | caravan L76-L80 |
| downstream interface | rim/hub/hub_band 不变；spoke 是 rotationally-nonsymmetric spin 证据元素 | caravan L81-L101 |

### Slot C / module low_three_plank_rails / tall_back_wall / high_sided_grain_box
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；全 body visual：`{side}_side_plank_{k}` / `back_plank_{k}` / `{side}_side_board_{i}` / `{end}_end_board_{i}` + corner posts | farm L130-L167, hand L146-L185, grain L138-L175 |
| internal joints | 无 | — |
| upstream interface | root @ `BED_FLOOR_Z+FLOOR_THK/2 + offset`，沿 BED_LEN/BED_WIDTH | farm L132-L140 |
| downstream interface | 墙顶 z 决定 Slot D cover 的 WALL_TOP_Z 接口 | caravan L60 |

### Slot C / module flat_rack_stake_bed
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`stake_{i}` body visuals（LatheGeometry tenon-taper） | stake L110-L185 |
| internal joints | 无 | — |
| upstream interface | perimeter 位置经 `N_SIDE_STAKES`/`N_END_STAKES` 计数循环生成，base @ `BED_FLOOR_Z+FLOOR_THK/2` | stake L153-L185 |
| downstream interface | 无连续墙顶 → Slot D 限 open/canvas | — |

### Slot D / module gabled_plank_roof / canvas_bow_tilt_cover
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；body visuals：`ridge_beam`+`*_roof_panel`+`*_gable_*`（gabled）或 `hoop_{i}`+`canvas_tilt`（canvas） | caravan L180-L229, canvas L311-L330 |
| internal joints | 无（静态盖） | — |
| upstream interface | 坐落于 WALL_TOP_Z（gabled）/ 拱起于 wall 顶（canvas，`BOW_RADIUS=BOX_WIDTH/2`） | caravan L60/L183, canvas L62-L82 |
| downstream interface | ridge/canvas 峰高于墙顶 +0.10（test 约束） | caravan L470, canvas L571 |

### Slot D / module drop_tailgate_open_box
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tailgate` part（`tailgate_plank_{k}` + battens + `hinge_strap_{i}`） | tailgate L206-L248 |
| internal joints | `tailgate_hinge` REVOLUTE axis=(0,-1,0) range [0, pi/2] | tailgate L388-L399 |
| upstream interface | child of body @ `(-BED_LEN/2, 0, BED_FLOOR_Z+FLOOR_THK/2)` 后底边 | tailgate L390-L396 |
| downstream interface | drop 成 loading ramp；iron hinge straps wrap barrel→bottom plank | tailgate L238-L248 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| wheel_config | enum | {single_axle_two_wheel, four_wheel_steered, six_wheel_triple_axle} | four_wheel_steered | choice | procedural sampler；single_axle 含 dray 折叠形式 | Slot A |
| spoke_count | int (N axis) | [6,16] | 12 | independent | weighted draw（见 Multiplicity） | Slot B |
| bed_sidewall | enum | {low_three_plank_rails, tall_back_wall, high_sided_grain_box, flat_rack_stake_bed} | low_three_plank_rails | choice | gated by wheel_config & top_cover | Slot C |
| top_cover | enum | {open_none, gabled_plank_roof, canvas_bow_tilt_cover, drop_tailgate_open_box} | open_none | choice | gated（见 compatibility matrix） | Slot D |
| side_board_count | int (N axis) | [2,7] | 3 | conditional | 仅 plank/board sidewall module 暴露；low=3, grain=6 | farm L133, grain L56 |
| stake_post_count | int (N axis) | side∈[2,8] end∈[1,3]/边 | 4/side | conditional | 仅 flat_rack module，total=2·side+2·end | stake L160-L177 |
| bow_hoop_count | int (N axis) | [3,7] | 5 | conditional | 仅 canvas top_cover module | canvas L66/L315 |
| axle_station_count | int (N axis) | {1,2,3} | 2 | conditional | 由 wheel_config 派生（single=1, four=2, six=3） | six L46 |
| wheel_radius_scale | float | [0.85, 1.15] | 1.0 | independent | clamp；缩放 REAR/FRONT_WHEEL_R，AXLE_Z 随之派生 | farm L37-L45 |
| front_rear_radius_ratio | float | derived | ~0.76 | equation | `FRONT_R = ratio·REAR_R`，ratio∈[0.70,0.82] 使 front 视觉小于 rear ≥0.05 | farm L412-L414 |
| half_track_scale | float | [0.9, 1.1] | 1.0 | independent | clamp；缩放 HALF_TRACK | farm L47 |
| bed_len_scale | float | [0.85, 1.2] | 1.0 | independent | clamp；缩放 BED_LEN | farm L53 |
| axle_z (per wheel) | float | derived | — | equation | `= wheel_r·wheel_radius_scale + RIM_TUBE_R`（rim 触地 z=0） | farm L44-L45 |
| palette_style | enum | {oak_natural, weathered_grey, dark_walnut, painted_red, pine_blond, green_painted_iron} | weathered_grey | choice | ≥4 colorways（见下） | materials L121-L124 等 |
| (—) | constraint | — | — | inequality | six-wheel: `AXLE_X[i]-AXLE_X[i+1] > wheel_r[i]+wheel_r[i+1]+2·RIM_TUBE_R` 防 rim 相撞，违反则拉开 spacing 或回退 axle_station_count | six L51 |
| (—) | constraint | — | — | inequality | `BED_FLOOR_Z = max(axle_z)+clearance`，墙/盖 height 不得使 inertial/AABB 自交；违反按比例回缩 | six L59 |
| (—) | constraint | — | — | conditional | top_cover 合法集随 bed_sidewall/wheel_config 解析（见 matrix） | 接口 |

**palette_style colorways（≥4 target 4-6）**：
1. `oak_natural` — wood(0.74,0.58,0.36), dark(0.45,0.33,0.20), plank(0.80,0.65,0.43), iron(0.16,0.16,0.17)（hand-cart L121-L124）
2. `weathered_grey` — wood(0.62,0.55,0.45), dark(0.40,0.34,0.27), plank(0.68,0.60,0.49), iron(0.17,0.17,0.18)（farm L104-L107）
3. `dark_walnut` — wood(0.46,0.32,0.20), dark(0.30,0.21,0.13), plank(0.52,0.38,0.24), iron(0.15,0.15,0.16)
4. `painted_red` — body(0.62,0.18,0.14), trim_dark(0.30,0.10,0.08), iron_black(0.12,0.12,0.13), wheel_wood(0.66,0.50,0.30)
5. `pine_blond` — wood(0.82,0.70,0.48), dark(0.55,0.44,0.28), plank(0.86,0.74,0.52), iron(0.20,0.20,0.21)
6. `green_painted_iron` — body(0.24,0.40,0.26), trim(0.14,0.24,0.16), iron(0.13,0.13,0.14), wheel_wood(0.60,0.46,0.30)

canvas/roof 专色（canvas(0.88,0.84,0.74) L241, roof_wood(0.64,0.49,0.30) caravan L110, rope(0.72,0.64,0.42) farm L108）按 palette 微调，不单列为 palette。

## Multiplicity / Copy Logic

本小类有 **4 根独立 multiplicity 轴**，各自加权采样。

### 轴 1 — spoke_count（每个 wheel 内）
- count_param：`spoke_count`
- N_range：产品 [6,16]；测试偏小 {8,10,12}
- sampling domain：weighted，{8,10,12} 高频，{14,16} 稀有，{6,7} 罕见
- copied object：radial `Cylinder` spoke（`_wheel_visuals` loop）
- naming：`spoke_{s}`
- placement：angle `a=2πs/spoke_count`，center `mid·(cos a,0,sin a)`，pitch `pi/2-a`，内端 hub 外端 felloe
- joint policy：无关节（wheel 内 visual）
- source/gating：caravan L76-L88；所有 wheel 共享同一 spoke_count

### 轴 2 — side_board_count（plank/board sidewall）
- count_param：`side_board_count`（per side/end stack 高度）
- N_range：产品 [2,7]；测试 {3,4,6}
- sampling domain：weighted，{3,4} 高频，{5,6} 中，{2,7} 稀有
- copied object：horizontal plank/board Box
- naming：`{side}_side_plank_{k}` / `{end}_end_plank_{k}` / `{side}_side_board_{i}` / `back_plank_{k}`
- placement：`z = floor_top + base_off + k·pitch`，沿 BED_LEN(side)/BED_WIDTH(end)
- joint policy：无（body visual）
- source/gating：farm L133-L152, grain L141-L160；仅 plank/board sidewall module 暴露（flat_rack 不暴露）

### 轴 3 — stake_post_count（flat_rack_stake_bed）
- count_param：`N_SIDE_STAKES`, `N_END_STAKES` → total = 2·side + 2·end
- N_range：side∈[2,8], end∈[1,3]；total 实际 [6,16]
- sampling domain：weighted，side {3,4,5} 高频，end {1,2} 高频，大端稀有
- copied object：LatheGeometry tenon-taper stake post
- naming：`stake_{i}`
- placement：perimeter 等距（side 沿 X，end 沿 Y），base @ `BED_FLOOR_Z+FLOOR_THK/2`
- joint policy：无（body visual）
- source/gating：stake L153-L185；仅 bed_sidewall=flat_rack_stake_bed

### 轴 4 — bow_hoop_count（canvas_bow_tilt_cover）
- count_param：`N_HOOPS`
- N_range：[3,7]；测试 {4,5,6}
- sampling domain：weighted，{4,5} 高频，{6,7} 中，{3} 稀有
- copied object：semicircular bow tube（`_build_bow_template` clone+translate）
- naming：`hoop_{i}`
- placement：`x_station = -hoop_span/2 + hoop_span·i/(N-1)`，arch 跨 BOX_WIDTH
- joint policy：无（body visual；canvas_tilt 单 mesh 覆盖）
- source/gating：canvas L311-L322；仅 top_cover=canvas_bow_tilt_cover

### 派生（非独立轴）— axle_station_count + wheel pairs
- 由 wheel_config 派生：single=1 站/2 wheel, four=2 站/4 wheel, six=3 站/6 wheel。
- copied object：wheel part + spin joint，`wheel_{i}_{side}` + `spin_{i}_{side}`（six L266-L314 是规范折叠形式；single/four 复用同 loop 模式）。
- joint policy：每 wheel CONTINUOUS world-Y；station 0（若 4/6 wheel）child of bolster，余 child of body。

## 拓扑多样性审计

总组合数（slot 笛卡尔积，未含 N）：A(3) × B(4 spoke 等价类) × C(4) × D(4) = **192**；扣除 compatibility gating（2-wheel 排除 gabled/canvas、flat_rack 排除 gabled/tailgate）后合法组合 ≈ **110**。
含 multiplicity 4 轴 distinct N（spoke{6..16}、side_board{2..7}、stake total{6..16}、hoop{3..7}、axle station{1,2,3}）后远超下限。

理由：单 Slot A(3) 已贡献 3 个不同 part/joint 拓扑（2/4/6 wheel + bolster 有无）；Slot D 的 drop_tailgate 加独立 part+REVOLUTE 关节、canvas/gabled 加不同 body-visual 群，Slot C 改 part-tree 板/桩复制结构；distinct-N（axle station 1/2/3 + spoke/board/stake/hoop 多值）独立倍增。最小诚实读：A(3)×distinct-N(≥3)=9，再加 Slot D 关节拓扑（tailgate vs others）≥2 → ≥18 ≥ 10。完整 ≈110 合法组合 × N 采样 ≫ 100。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `ctx.rng`/seed 派生 RNG：(1) 先采 wheel_config（加权，four_wheel 高频），(2) 由其解析 axle_station_count + 是否有 bolster，(3) 采 spoke_count（轴 1 加权），(4) 采 bed_sidewall（按 wheel_config gate：2-wheel 不选 grain 深墙? 允许；flat_rack 任意），(5) 采 top_cover（按 bed_sidewall + wheel_config compatibility 集合解析合法子集再加权），(6) 采暴露的 multiplicity 轴（side_board / stake / hoop）+ 连续 scale（independent → equation → inequality 回缩）。`slot_choices_for_seed` 返回 `[(wheel_config,…),(spoke_count 等价类),(bed_sidewall,…),(top_cover,…)]`（连续 scale 不记入 topology 等价类，但 spoke/board/stake/hoop 的 N 计入若改 part 数）。Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；合法组合 ≈110 × N，低于 300 时记录离散空间或采样权重原因。无 curated/modulo 主表；regression overrides 仅用于已知失败回归。

Controlled local parameterization：`wheel_radius_scale`[0.85,1.15] indep、`front_rear_radius_ratio`[0.70,0.82] equation（front 小于 rear ≥0.05）、`half_track_scale`[0.9,1.1] indep、`bed_len_scale`[0.85,1.2] indep；`axle_z = wheel_r·scale + RIM_TUBE_R`（equation，rim 触地）、six-wheel axle spacing inequality（防 rim 相撞）、`BED_FLOOR_Z = max(axle_z)+clearance`（equation）。全部 `resolve_config` 内 clamp/派生/回缩，不破坏 wheel-axle 接口、kingpin turntable、multiplicity、identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | wheel_config→station 派生→spoke→sidewall(gated)→top_cover(gated)→multiplicity+scale | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | 见下；mutually exclusive + fallback degrade | no floating wheel, axle rim collision, steer axis, tailgate closed-pose, bulky cover on stake deck |
| controlled local variation | 4 连续 scale + per-N clamp | 比例变化不破 wheel-touch-ground、front<rear、kingpin 接口 |
| regression overrides | none（除非 sweep 暴露失败 seed） | 已知失败回归专用 |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | contract failures |

**Compatibility matrix**：

| wheel_config \ top_cover | open_none | gabled | canvas | drop_tailgate |
|---|---|---|---|---|
| single_axle_two_wheel(_dray) | ✓ | ✗→open | ✗→open | ✓ |
| four_wheel_steered | ✓ | ✓ | ✓ | ✓ |
| six_wheel_triple_axle | ✓ | ✓ | ✓ | ✓ |

| bed_sidewall \ top_cover | open | gabled | canvas | drop_tailgate |
|---|---|---|---|---|
| low_three_plank_rails | ✓ | ✓ | ✓ | ✓ |
| tall_back_wall | ✓ | ✗→open | ✓ | ✓ |
| high_sided_grain_box | ✓ | ✓ | ✓ | ✓ |
| flat_rack_stake_bed | ✓ | ✗→open | ✓ | ✗→open |

理由：gabled/canvas cabin 需连续墙顶 WALL_TOP_Z 承载（stake deck 无连续墙→degrade open；tall_back_wall 非对称端墙不适合对称 gabled→degrade open）；drop_tailgate 需后端墙做 closed-pose（flat_rack 无端墙→degrade open）；2-wheel hand-cart 不带 cabin cover（身份）→gabled/canvas degrade open。

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A wheel_config | 4 (含 dray 折叠) | yes | yes | 3 个不同 wheel/axle 拓扑 |
| B spoke_count | 4 | yes | yes | N 轴等价类 {8,10,12,16} |
| C bed_sidewall | 4 | yes | yes | |
| D top_cover | 4 | yes | yes | 1 加独立 part+REVOLUTE |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名（wheel_config / spoke_count 等价类 / bed_sidewall / top_cover）
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling（seed=0 不特殊）
- compatibility matrix / gating 阻止非法组合（2-wheel cabin cover、stake deck gabled/tailgate）
- regression overrides 稀疏且有理由（默认 none）
- 不以小 curated/modulo 表作主 seed domain
- 连续 scale（wheel_radius/half_track/bed_len/ratio）clamp 且不破 wheel-axle 接口、kingpin turntable、front<rear、multiplicity
- 跨部件 scale 依赖（axle_z equation、six-wheel spacing inequality、BED_FLOOR_Z）在 `resolve_config` 解析
- 关键 InterfaceSpec/MatingContract 存在：wheel hub↔axle stub（element-scoped allow_overlap hub & hub_band）、kingpin_boss↔bolster_beam turntable、tailgate 后底边铰
- 关键关节类型/轴/range：每 wheel CONTINUOUS axis=(0,1,0)；`front_steer` REVOLUTE axis=(0,0,1) ±0.6；`tailgate_hinge` REVOLUTE axis=(0,-1,0) [0,pi/2]
- 复制对象遵循命名/placement：`spoke_{s}`/`{side}_*_{k}`/`stake_{i}`/`hoop_{i}`/`wheel_{i}_{side}`/`spin_{i}_{side}`
- 每 wheel 触地 z≈0（`axle_z=wheel_r+RIM_TUBE_R`）；4/6-wheel front 轮视觉小于 rear ≥0.05；左右对称

## Reject cases

- wheel-spin 关节非 CONTINUOUS 或轴非 world-Y（违反 PRIMARY rolling identity）
- 4/6-wheel 缺 `front_steer` REVOLUTE world-Z 或前轮不随 bolster swing（缺 steering identity）
- wheel hub 不套 axle stub（detached gap，悬空轮）或 wheel 不触地 z≠0
- six-wheel axle spacing 不足致 rim-to-rim 穿模（违反 spacing inequality）
- 2-wheel 配 gabled/canvas cabin cover（误入 caravan，且无连续墙承载）
- gabled/canvas/tailgate 落在 flat_rack stake deck（无连续墙/端墙承载，应 degrade open）
- tailgate_hinge 轴错误或 closed-pose 时 tailgate 不封后口（穿模/缝隙）
- spoke/board/stake/hoop 计数变成自由乱抽未 clamp，或 N 超 range 致 island/穿模
- front 轮不小于 rear 轮（4/6-wheel 比例破身份）
- 把 rope tie / swingletree / hub band / iron strap 做成独立 FIXED-joint part（应 parent visual）

## 与相邻类别的边界

- 不该混入：**Caster_Trolley**（小 swivel caster 脚轮 + push handle frame，无大 spoked wooden wheel、无 draw pole、无 steering front axle；rolling 由小脚轮提供，结构家族不同）。
- 不该混入：**Tipping_Barrow**（独轮 wheelbarrow：单前轮 + 两手柄 + 两撑腿，tub 绕前轴 tip dump；draft wagon 至少 2 个共轴轮且无 tub-tip 关节，pull 在前而非 push 在后）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A | single_axle_two_wheel | rec_two-wheeled-wooden-hand-cart-…b1d205ac | L255-L290, L196-L253 | 2-wheel body axle + prop legs + shafts + wheel/joint |
| S2 | A | single_axle_two_wheel_dray | rec_draft_wagon_var_single_axle_two_wheel_dray | L255-L284 | 2-wheel loop-folded form |
| S3 | A | four_wheel_steered | rec_four-wheeled-wooden-farm-wagon-…56699604 | L194-L330 | bolster + steer + 4-wheel canonical chassis |
| S4 | A | six_wheel_triple_axle | rec_draft_wagon_var_six_wheel_triple_axle | L46-L54, L266-L314 | N_AXLES station loop + 6-wheel |
| S5 | B | spoke_count helper | rec_…caravan…085f4a98 / farm | caravan L65-L101 / farm L61-L98 | shared `_wheel_visuals` spoke loop |
| S6 | B | spokes_8 / spokes_16 | rec_draft_wagon_var_heavy_eight_spoke_wheels / fine_sixteen_spoke_wheels | `_wheel_visuals` spoke_count | N 端点 {8,16} |
| S7 | C | low_three_plank_rails | rec_…farm…56699604 | L130-L167 | 低 open box 墙板 |
| S8 | C | tall_back_wall | rec_…hand-cart…b1d205ac | L146-L185 | hand-cart 非对称高后墙 |
| S9 | C | high_sided_grain_box | rec_draft_wagon_var_high_sided_grain_box | L56-L60, L138-L175 | 6-board 深墙 + `_wall_board` |
| S10 | C | flat_rack_stake_bed | rec_draft_wagon_var_flat_rack_stake_bed | L61-L65, L110-L185 | perimeter stake post 计数循环 |
| S11 | D | gabled_plank_roof | rec_…caravan…085f4a98 | L180-L229 | ridge+panel+gable |
| S12 | D | canvas_bow_tilt_cover | rec_draft_wagon_var_canvas_bow_tilt_cover | L61-L192, L311-L330 | bow hoop loop + canvas mesh |
| S13 | D | drop_tailgate_open_box | rec_draft_wagon_var_drop_tailgate_open_box | L206-L248, L388-L399 | tailgate part + REVOLUTE 铰 |

## 模板实现备注（可选）
- 所有 wheel 共享单 `_wheel_visuals(part, prefix, radius, spoke_count, palette)` helper（合并 hand-cart 无-radius 形式与 farm 有-radius 形式，spoke_count 提参）。
- wheel/spin 统一走 `for i in range(axle_station_count)` × 2-side 循环（采 six-wheel 折叠形式 six L266-L314），single/four 用同 loop 仅 station 数不同。
- element-scoped `allow_overlap` 必须随 slot 组合全部复现：每 wheel hub&hub_band × 对应 axle stub；4/6-wheel 加 kingpin_boss×{bolster_beam, front_axle, draw_pole}。
- front-wheel joint origin 必须写 bolster local frame（`axle_local_z=FRONT_AXLE_Z-bolster_z`），勿用 world z。
- Cylinder 原点在中心：axle/hub 旋转 `rpy=(pi/2,0,0)` 对齐 Y。
- 暂不进 seed domain 的组合：2-wheel × {gabled, canvas}、flat_rack × {gabled, tailgate}（degrade 到 open，见 matrix）。
