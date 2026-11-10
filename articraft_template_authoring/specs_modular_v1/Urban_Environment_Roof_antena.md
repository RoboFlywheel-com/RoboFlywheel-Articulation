# Roof Antenna Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `roof_antenna` |
| template path | `agent/templates/Urban_Environment_Roof_antena.py` |
| test path (optional) | `tests/agent/test_roof_antenna_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：核心是一条 `mast → antenna_head → array(boom)` 的 linear_chain 串两个 REVOLUTE 关节（azimuth +Z 主关节 + elevation Y 次关节），但 array 内部对 director/dipole 元件做 **multiplicity** 复制，mast 底座 mount 是 parallel 挂到 root mast 的可替换层。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category（1 parent baseline + 9 single-axis converged variants）；逐个读取 `model.py` 全文 |
| source_index_policy | only adopted module sources are indexed below |

被采纳样本逐条标注（全部 10 个均被采纳为 module source，每个对应一条结构轴）：
- `rec_rooftop-yagi-tv-antenna-on-a-tall-vertical-mast-_20260608_164527_444902_495f9ccb`（**parent / baseline**）— mast + antenna_head + 单 yagi boom + ~9-element director array + 17-rod reflector grid + flat_base mount；2 REVOLUTE（azimuth +Z, elevation -Y）。提供共享 mast/head/articulation 骨架 + `_rod` helper + flat_base mount + yagi_director_array 基线。
- `rec_roof_antenna_var_type_dish` — dish_reflector head（抛物面 lathe shell + torus rim + feed horn + 3 struts）替换 yagi array。
- `rec_roof_antenna_var_type_dipole_whip` — dipole crossbar + vertical whip + 8-segment loop ring head 替换 yagi array。
- `rec_roof_antenna_var_type_panel` — flat radome panel + 4×6 patch grid head 替换 yagi array。
- `rec_roof_antenna_var_elements_few` — yagi array 用 `for i in range(N)`、N≈5、computed taper（程序化元件循环）。
- `rec_roof_antenna_var_elements_many` — 同上 N≈14。
- `rec_roof_antenna_var_mount_tripod` — 3 splayed legs + foot pads 底座替换 flat_base。
- `rec_roof_antenna_var_mount_chimney_strap` — brick chimney stub + 3 hose straps 底座；mast pole 偏置贴 chimney 面。
- `rec_roof_antenna_var_mount_wall_bracket` — wall plate + 2 standoff arms + arm clamps 底座。
- `rec_roof_antenna_var_boom_xdual` — 两条 ±14° splay 交叉 boom，各带自己的 director 循环 + 共享 reflector grid。

## 核心身份

屋顶 TV / 通信天线：一根立在屋面 `z=0` 上的高 weathered 金属 mast（root，static），mast 顶部一个 azimuth 旋转 collar/hub（`antenna_head`），其上一个可俯仰的 array 组件（boom / dish / dipole+whip / panel）。**defining articulation = mast azimuth REVOLUTE about +Z**（主关节，瞄准就是绕竖直 mast 轴摆头），其次是 array 的 elevation tilt REVOLUTE about Y（次关节，微调仰角）。默认成熟域是 **rooftop yagi TV antenna**：mast + azimuth head + 单 boom + N 个沿 boom 横排的 director 元件 + 后部 reflector 栅格 + flat-base 底座。

每个变体都必须保留：(a) 立在 `z=0` 的高 mast（>3 m）；(b) mast 顶 azimuth +Z REVOLUTE；(c) array elevation Y REVOLUTE；(d) array 安装在 mast 顶部（head world z > 3）。

边界（见第 11 节）：身份是 **屋顶 yagi / 杆顶 TV-comm 天线**，不是 sci-fi 卫星天线整机、不是地面雷达转台、不是带馈线小室的电信基站。dish 候选是「小型屋顶碟」而非天文/深空大碟。

## 槽位 + 候选模块表

### Slot A：antenna_type（mast 顶 array 头部形态 — 主结构层；azimuth + elevation REVOLUTE 保持）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| yagi_director_array（基线） | rec_rooftop-yagi-tv-antenna-on-a-tall-vertical-mast-_20260608_164527_444902_495f9ccb | L135-L239（boom_spine + element loop + balun boxes + reflector grid/stiles/strut + inertial） | eligible if compatible | square boom spine 沿 +X；N 个横排 `element_rod_*` 沿 ±Y；后部 17-rod reflector 栅格 + 2 stiles + bridging strut；2 balun box |
| dish_reflector | rec_roof_antenna_var_type_dish | L180-L290（dish_assembly part）；helpers `_parabolic_dish_shell` L44-L70、`_strut_mesh` L73-L84 | eligible if compatible | LatheGeometry 抛物面 shell + torus rim + 焦点 feed horn + 3× `support_strut_{i}`（120°）+ stub_arm/pivot_bracket + junction_box |
| dipole_whip | rec_roof_antenna_var_type_dipole_whip | L152-L234（dipole_assembly part）；helpers `_vertical_rod` L54-L65、`_loop_segment` L68-L70 | eligible if compatible | center_hub + 横 dipole_crossbar + 竖 vertical_whip + balun + 8× `loop_rod_{i}` 八角环 + 4× `loop_support_{k}` 辐条 |
| panel | rec_roof_antenna_var_type_panel | L136-L228（panel part）；CadQuery radome via `mesh_from_cadquery` L171-L183 | eligible if compatible | stub_bracket + panel_mount_riser + 直立 filleted radome_panel + 24× `patch_{idx}`（4×6 grid）+ junction_box |

### Slot B：element_count_N（boom 上横排 director/dipole 元件 — multiplicity；仅当 Slot A = yagi 或 dipole 行型时活跃）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| elements_few（N≈5） | rec_roof_antenna_var_elements_few | L156-L176（`for i in range(n_elements)` n_elements=5，computed even spacing + front-taper） | eligible if compatible（A=yagi/dipole_whip 时） | 稀疏 director 行；`element_rod_{i}` 程序化生成，长度从 rear→front 线性递减 |
| elements_mid（N≈9，基线） | rec_rooftop-yagi-tv-antenna-on-a-tall-vertical-mast-_20260608_164527_444902_495f9ccb | L160-L180（hand-written `element_specs` 9-tuple list → `element_rod_{idx:02d}` loop） | eligible if compatible | 中等密度；模板将 hand-list 重写为单 N 参数 `for i in range(N)` computed taper（见第 8 节 copy logic）|
| elements_many（N≈14） | rec_roof_antenna_var_elements_many | L160-L176（`for i in range(n_elements)` n_elements=14，linear taper） | eligible if compatible（A=yagi/dipole_whip 时） | 密集 director 行；同一程序化循环，仅 N 与 taper 端点变化 |

### Slot C：mast_mount（屋面底座 — 折入 static root `mast` part 的 visual 层，替换基线 flat foot-plate + standoff tabs）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_base（基线） | rec_rooftop-yagi-tv-antenna-on-a-tall-vertical-mast-_20260608_164527_444902_495f9ccb | L76-L97（round `foot_plate` + 2× `standoff_bracket_{i}`/`standoff_pad_{i}`） | eligible if compatible | 圆 foot plate 坐 `z≈0` + 两个 standoff 墙撑 tab；mast 在轴上 |
| tripod_feet | rec_roof_antenna_var_mount_tripod | L76-L138（`tripod_hub` + `for i in range(3)` legs/pads + standoff tabs） | eligible if compatible | clamp hub + 3× `leg_{i}` splayed tube + 3× `foot_pad_{i}` 落地；mast 在轴上 |
| chimney_strap | rec_roof_antenna_var_mount_chimney_strap | L120-L173（mast pole 偏置 + `chimney_block` + `chimney_cap` + `for i in range(3)` `strap_{i}`）；helper `_chimney_strap_mesh` L58-L91（ExtrudeWithHoles） | eligible if compatible | 砖 chimney stub + concrete cap + 3× hose strap band 缠 chimney+mast；mast pole **偏置** 贴 chimney +X 面 → azimuth 关节 origin 随之 `xyz=(mast_x,0,head_z)` |
| wall_bracket | rec_roof_antenna_var_mount_wall_bracket | L99-L133（`wall_plate` + `for i in range(2)` `arm_{i}`/`arm_clamp_{i}`）；helper `_wall_plate_cq` L61-L75（CadQuery 板 + 4 螺孔） | eligible if compatible | 立 wall plate（x≈-0.20）+ 2× standoff arm + arm clamp 夹 mast；此候选无 standoff_bracket/pad（arms 取代）；mast 在轴上 |

### Slot D：boom_config（仅当 Slot A = yagi 时活跃 — boom spine 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single_boom（基线） | rec_rooftop-yagi-tv-antenna-on-a-tall-vertical-mast-_20260608_164527_444902_495f9ccb | L148-L154（单中央 `boom_spine`）+ element loop L156-L180 | eligible if compatible | 一条中央 boom spine 沿 +X；N 元件单行；reflector 单 bridging strut |
| X_dual_boom | rec_roof_antenna_var_boom_xdual | L145-L274（central `hub` + `for b,sign in (+1,-1)` 两 `boom_spine_{b}` ±14° splay，各带 `element_{b}_{i}` 循环 + `balun_box_{b}` + `reflector_strut_{b}` + center strut）；helper `_boom_point` L56-L62 | eligible if compatible | 两条 ±splay boom 在中央 hub 交叉成 X；每 boom 一行 director；共享居中 reflector 栅格 + 双 strut 支撑 |

## 槽位图（slot graph）

pattern: mixed（linear_chain spine + multiplicity inside array + parallel mount on root）

```
mast(root, static; Slot C mount geometry folded in)
  --[REVOLUTE azimuth +Z @ (mast_x,0,head_z), range ±π, DEFINING]-->
antenna_head(rotation collar; elevation_post stub on top)
  --[REVOLUTE elevation Y @ (0,0,~0.12 above collar), range ±0.35]-->
array(Slot A: yagi_director_array / dish / dipole_whip / panel)
    └─ multiplicity Slot B: element_{i} loop along boom +X (yagi/dipole 行型)
    └─ Slot D boom_config (single / X_dual) only when A=yagi
```

接口点位与装配：
- **mast ↔ antenna_head（azimuth）**：mating = mast 顶 `head_z = mast_len-0.05`；antenna_head part frame 居中在 mast 轴（chimney_strap 时偏 `mast_x`），collar 抱住 mast 顶（intentional `allow_overlap` collar↔mast_pole + clamp_block↔mast_pole）。axis `(0,0,1)`，range `[-π,π]`。**这是 defining 关节**。
- **antenna_head ↔ array（elevation）**：mating = `elevation_post` 顶部 `origin xyz=(0,0,0.12)`；pivot boss 坐进 array 的 boom_spine / hub / stub_arm / stub_bracket / center_hub（per-type intentional `allow_overlap`）。axis `(0,±1,0)`，range `[-0.35,0.35]`。
- **Slot C mount**：不是独立 part、不引入新 joint，而是折入 static root `mast` part 的 visual 层；底座件直接坐在 `z≈0`。flat_base/tripod/wall_bracket mast 在轴上；chimney_strap mast pole 偏置 → azimuth origin 同步偏 `mast_x`。
- **Slot B 元件**：FIXED 随 boom（无独立 joint），作为 array 的 inline boom visual 横排 ±Y。
- **Slot D**：single → 一条 boom spine；X_dual → 中央 hub + 两 splay spine，各自承载 element loop，共享居中 reflector。

互斥 / 派生关系：
- Slot B 只在 Slot A ∈ {yagi_director_array, dipole_whip(行型)} 时有意义；A = dish / panel 时 N 不暴露（折叠为固定 grid 几何，见 compatibility matrix）。
- Slot D 只在 Slot A = yagi_director_array 时活跃；A ≠ yagi 时 D 强制 single（无意义）。

## 每槽位 Module Emits / Interfaces

### Slot A / module yagi_director_array
| emits | 描述 | 来源 |
|---|---|---|
| parts | `yagi_boom` part：`boom_spine` + `element_rod_{i}` ×N + `balun_box_rear`/`junction_box_front` + reflector `reflector_grid_{g:02d}`×17 + `reflector_stile_{0,1}` + `reflector_strut` | parent / model.py:L135-L239 |
| internal joints | 无（元件/reflector 全 FIXED 随 boom） | parent / L156-L233 |
| upstream interface | boom local origin = elevation pivot；boom_spine 接 elevation_post（intentional overlap） | parent / L307-L317 |
| downstream interface | 无（array 是链末端） | parent |

### Slot A / module dish_reflector
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dish_assembly` part：`stub_arm` + `pivot_bracket` + `dish_reflector`(lathe) + `dish_rim`(torus) + `feed_horn` + `support_strut_{i}`×3 + `junction_box` | rec_..._type_dish / L180-L290 |
| internal joints | 无（dish 全 FIXED 随 elevation child） | 同上 |
| upstream interface | `stub_arm`/`pivot_bracket` 接 elevation_post（intentional overlap + expect_contact L367-L389） | 同上 |
| helpers | `_parabolic_dish_shell` L44-L70、`_strut_mesh` L73-L84 | 同上 |

### Slot A / module dipole_whip
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dipole_assembly` part：`center_hub` + `dipole_crossbar` + `vertical_whip` + `balun_box` + `loop_rod_{i}`×8 + `loop_support_{k}`×4 | rec_..._dipole_whip / L152-L234 |
| internal joints | 无（全 FIXED） | 同上 |
| upstream interface | `center_hub` 接 elevation_post（intentional overlap L303-L309） | 同上 |
| helpers | `_vertical_rod` L54-L65、`_loop_segment` L68-L70 | 同上 |

### Slot A / module panel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `panel` part：`stub_bracket` + `panel_mount_riser` + `radome_panel`(CadQuery) + `patch_{idx}`×24 + `junction_box` | rec_..._panel / L136-L228 |
| internal joints | 无（全 FIXED） | 同上 |
| upstream interface | `stub_bracket` 接 elevation_post（intentional overlap L297-L303） | 同上 |

### Slot B / module elements_{few,mid,many}
| emits | 描述 | 来源 |
|---|---|---|
| parts | `element_{i}` 横排 rod，inline 进 boom part（boom visual，非独立 part） | few L156-L176 / many L160-L176 |
| internal joints | 无（FIXED 随 boom；Rule1 inline boom visuals） | 同上 |
| upstream interface | 骑在 boom_spine 上，沿 +X 均布，长度 rear→front 递减 | 同上 |

### Slot C / module flat_base / tripod_feet / chimney_strap / wall_bracket
| emits | 描述 | 来源 |
|---|---|---|
| parts | 折入 static `mast` part 的 visual：foot_plate/standoff（flat）；`tripod_hub`+`leg_{i}`+`foot_pad_{i}`（tripod）；`chimney_block`+`chimney_cap`+`strap_{i}`（chimney）；`wall_plate`+`arm_{i}`+`arm_clamp_{i}`（wall） | C 表各源 |
| internal joints | 无（mount 全 static，无 joint） | 同上 |
| upstream interface | 坐在 `z≈0`；chimney_strap 偏置 mast pole 并移 azimuth origin 至 `mast_x` | chimney / L120-L125,L324 |
| downstream interface | mast 顶 `head_z` 喂 azimuth 关节 | parent / L243-L256 |

### Slot D / module single_boom / X_dual_boom
| emits | 描述 | 来源 |
|---|---|---|
| parts | single：一 `boom_spine` + 单行 element + 单 reflector_strut。X_dual：`hub`+`boom_spine_{b}`×2 + `element_{b}_{i}` 双行 + `balun_box_{b}` + `reflector_strut_{b}`×2 + `reflector_center_strut` | single parent L148-L180 / xdual L145-L274 |
| internal joints | 无 | 同上 |
| upstream interface | single boom_spine / X_dual hub 接 elevation_post（intentional overlap；xdual 还 overlap elevation_post↔boom_spine_{0,1} L359-L366） | 同上 |
| helper | `_boom_point` L56-L62（splay world 坐标） | xdual |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| antenna_type | enum | {yagi_director_array, dish_reflector, dipole_whip, panel} | — | choice | deterministic procedural sampler 选择 | Slot A 表 |
| mast_mount | enum | {flat_base, tripod_feet, chimney_strap, wall_bracket} | — | choice | sampler 选择；chimney_strap 触发 mast_x 偏置 + azimuth origin 同步 | Slot C 表 |
| boom_config | enum | {single_boom, X_dual_boom} | single_boom | conditional | 仅 antenna_type=yagi 时可 X_dual；否则强制 single | Slot D 表 |
| element_count_N | int | [5,14]（产品域）；测试偏小 | 9 | conditional | 仅 antenna_type∈{yagi,dipole_whip} 时暴露并采样；dish/panel 不暴露 | Slot B 表 |
| palette_style | enum | {aluminium, galvanized, black, weathered, white_painted, bronze}（≥3，目标 4-6） | aluminium | choice | 仅改 4 个 material rgba；不改拓扑/尺寸 | parent L58-L61 materials |
| mast_height_scale | float | [0.90, 1.20] | 1.0 | independent | clamp；mast_len = 3.40·scale，须保证 height>3.0（验证器） | parent L64 mast_len |
| mast_radius_scale | float | [0.85, 1.30] | 1.0 | independent | clamp；mast_r = 0.016·scale（collar/clamp 内径同步派生避免穿模） | parent L65 mast_r |
| head_z | float | derived | — | equation | `= mast_len - 0.05`（collar 坐 mast 顶下） | parent L66 |
| collar_inner_r | float | derived | — | equation | `= mast_r + ε`，ε∈[0.010,0.016]；随 mast_radius_scale 派生 | parent L109 collar r=0.030 |
| boom_len_scale | float | [0.85, 1.25] | 1.0 | independent | clamp；仅 yagi/X_dual 用；boom_len = 1.55·scale | parent L142 boom_len |
| element_taper | float | derived | — | equation | `elen_i = max_len - frac·(max_len-min_len)`，frac=i/(N-1)；rear>front | few L168 / many L168 |
| element_spacing | float | derived | — | equation | 沿 boom 均布 `x_i = start + frac·(end-start)`，由 N 与 boom_len 派生 | few L167 |
| dish_radius_scale | float | [0.85, 1.20] | 1.0 | independent | clamp；仅 dish；feed_horn 焦点位置随之派生 | dish L201-L250 |
| boom_splay_deg | float | [10, 18] | 14 | conditional | 仅 X_dual；clamp；过大→两 boom 后端碰撞，回缩 | xdual L151 |
| (—) | constraint | — | — | inequality | element 行总宽 `≤ 2·refl_half_w + margin`，最长 rear 元件不超 reflector 宽；违反按比例回缩元件长度 | parent reflector L197 |
| (—) | constraint | — | — | inequality | X_dual：`boom_len·cos(splay)` 前端两 tip Y 间距 ≥0.15 且后端元件不互相穿模；违反回缩 splay 或 boom_len | xdual test L399-L423 |
| (—) | constraint | — | — | inequality | head world z（= head_z）必须 >3.0 且 mast aabb min z <0.02；mast_height_scale 下限保证 | parent test L322-L340 |

## Multiplicity / Copy Logic

本类别有 **1 根 multiplicity 轴**：boom 上的 director/dipole 元件行。

- `count_param`：`element_count_N`（横排 director/dipole rod 数）。
- `N_range`：`[5, 14]`（产品全域；parent 基线 9）。测试 sweep 偏小（多数 seed 落 5-10），尾部 N>11 稀有。
- sampling domain（权重档）：小 N 高频（5-9 约占多数），大 N（12-14）稀有尾部；按 per-N 加权抽样（小 N 偏多）。
- copied object：单条横向 rod 元件（`_rod` 沿 +X 生成、rpy 旋到 ±Y 横跨 boom）。
- naming：`element_{i}`（X_dual 时 `element_{b}_{i}`，b∈{0,1} 每 boom 一行）。
- placement：沿 boom +X 均布 `x_i = start + i/(N-1)·(end-start)`；长度 front-taper `elen_i = max_len - i/(N-1)·(max_len-min_len)`，rear 最长（driven/near-reflector），front 最短（director）。
- joint policy：**FIXED**，作为 boom inline visual 随 elevation child 一起 tilt（无独立 joint）。
- source/gating：parent hand-written `element_specs`（L160-L171）必须重写为 `for i in range(N)` 程序化（few L156-L176 / many L160-L176 已示范）。仅 antenna_type∈{yagi_director_array, dipole_whip} 暴露；dish/panel 时 N 不采样（其 grid/patch/loop 密度固定为类型几何，**不**作为独立 multiplicity 轴 — 见排除项）。

固定（非模板 multiplicity 轴）的复制：reflector grid 17 rods、reflector stiles 2、tripod legs 3、straps 3、wall arms 2、dish struts 3、dipole loop 8 / spokes 4、panel patches 24 — 这些是 module-local 固定循环，随类型几何走，不暴露为 `*_count` 参数。

## 拓扑多样性审计

总组合数：
- 非 N 候选乘积：antenna_type 4 × mast_mount 4 × boom_config(yagi 时 2，否则 1) = (1·2 + 3·1) × 4 = 5 × 4 = **20**（type×boom 合法组合 5，乘 mount 4）。
- 计入 distinct-N（yagi/dipole 行型，按 ~5/~9/~14 三档区分）：20 + 额外 N 拓扑等价类。yagi×mount×boom×N(3) + dipole×mount×N(3) 远超基线，**总 distinct topology ≈ 50+**。
- 源 source map 预审：4×4×2×3 = 96 ≥ 10 ✓。

理由：仅非 N 的 type×mount×boom 合法组合就 20 ≥ 10；加 distinct-N 与 palette（palette 不计入拓扑）后冗余充足。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed` 对普通 seed 用 deterministic procedural sampling：(1) 按权重抽 antenna_type；(2) 按 type 解析 boom_config（非 yagi 强制 single）与 element_count_N（非 yagi/dipole 不暴露）；(3) 抽 mast_mount；(4) 抽 palette_style；(5) 抽 independent scales（mast_height/radius、boom_len、dish_radius、splay）→ 按 equation 派生（head_z、collar_inner_r、taper、spacing）→ 按 inequality 投影回缩（元件行宽、X_dual tip 间距、head_z>3）。`seed=0` 不特殊。无主-seed-domain 的 curated/modulo 表。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别 type×mount×boom×N 名义乘积 96，叠加 N 连续档与小类兼容约束后预计 distinct 落在 50-96 区间。低于 300 的原因：antenna_type/mount/boom/N 是有限离散轴，连续 scale 不改变拓扑等价类（按设计只改安全比例）；这是该类别离散结构轴数量的固有上限，符合 source map HARD GATE。

Controlled local parameterization：初版应含 `mast_height_scale`[0.90,1.20]、`mast_radius_scale`[0.85,1.30]、`boom_len_scale`[0.85,1.25]、`dish_radius_scale`[0.85,1.20]、`boom_splay_deg`[10,18]。全部在 `resolve_config` clamp / 派生（head_z、collar_inner_r、element taper/spacing 为 equation；元件行宽、X_dual tip 间距、head_z>3 为 inequality）。这些 scale 只改安全比例，不破坏 azimuth/elevation 接口、`z=0` 落地、collar 抱杆 fit 或 multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 抽 type → 解析 boom/N conditional → 抽 mount → 抽 palette → 抽 scales → 派生 → inequality 投影 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | boom_config=X_dual 仅 type=yagi；element_count_N 仅 type∈{yagi,dipole_whip}；chimney_strap 触发 mast_x 偏置 + azimuth origin 同步；其余自由组合 | 无 floating / 穿模 / 错轴 / N 越界 / mount 漂浮 |
| controlled local variation | 5 个 clamped scale + equation/inequality 派生 | 比例变化不破坏接口、clearance、collar fit、joint origin、`z=0`、类别 identity |
| regression overrides | none | — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 与 contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A antenna_type | 4 | yes | yes | yagi/dish/dipole_whip/panel |
| B element_count_N | 3 | yes | yes | few≈5 / mid≈9 / many≈14；conditional on A |
| C mast_mount | 4 | yes | yes | flat_base/tripod/chimney/wall |
| D boom_config | 2 | yes | no | single/X_dual；conditional on A=yagi（仅 2 候选，因 X_dual 单源；single 为基线，结构差异明确，允许降到 2） |

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C/D 已实现候选）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos：X_dual 仅 yagi；N 仅 yagi/dipole；chimney_strap 同步 azimuth origin
- optional regression overrides 为空（无 curated/modulo 主 seed domain）
- controlled local scale params clamped；mast_height_scale 保证 height>3.0、head_z>3.0；collar_inner_r 随 mast_radius_scale 派生避免穿模或脱开
- cross-part scale deps（head_z=mast_len-0.05、collar_inner_r=mast_r+ε、element taper/spacing、行宽与 tip 间距 inequality）在 `resolve_config` 求解，不留到 builder
- critical InterfaceSpec / MatingContract 存在：mast↔head（azimuth +Z @ head_z/mast_x）、head↔array（elevation Y @ +0.12）、mount 折入 static mast 坐 z≈0
- key joints 类型/轴/范围：azimuth REVOLUTE axis (0,0,1) range[-π,π]（DEFINING）；elevation REVOLUTE axis (0,±1,0) range[-0.35,0.35]
- copied objects 遵循命名/placement：`element_{i}` / `element_{b}_{i}` 沿 boom +X 均布 + front-taper，FIXED riding boom
- per-type intentional overlaps element-scoped 声明：collar↔mast_pole、clamp_block↔mast_pole、elevation_post↔(boom_spine/hub/stub_arm/stub_bracket/center_hub)、chimney strap↔mast_pole

## Reject cases

- mast height ≤3 m 或 head world z ≤3（mast_height_scale 失控 / head_z 派生错）→ 失去屋顶高杆身份。
- mast foot 浮空或埋入（aabb min z ≥0.02）→ mount 没坐到 `z=0`。
- azimuth 关节缺失、非 REVOLUTE、或轴非 +Z → 丢 defining 关节（主关节是 azimuth）。
- elevation 关节缺失、非 REVOLUTE、或轴非 ±Y → 丢次关节。
- antenna_type≠yagi 却采样了 X_dual 或 element_count_N → 非法 conditional 组合。
- chimney_strap 偏置 mast pole 但 azimuth origin 没同步 `mast_x` → head 脱离 mast / 关节漂浮。
- collar_inner_r 没随 mast_radius_scale 派生 → 大杆穿出 collar 或细杆 collar 脱开（无 intentional overlap 兜底）。
- N 越界（<5 或 >14）、N=1 致 `frac=i/(N-1)` 除零、或元件最长超 reflector 宽未回缩 → 退化/穿模。
- reflector grid / dish / panel 漂浮（缺 bridging strut / stub / riser）→ 出现 disconnected island。
- 把 reflector-grid 密度、dish patch、loop 段当独立 multiplicity 轴暴露 → 与 element_count_N 近似重复（source map 已排除）。

## 与相邻类别的边界

- 不该混入：sci-fi satellite dish / 深空天线整机（理由：身份是屋顶小型 TV-comm 天线 + 高杆 + azimuth 摆头；不是巨型抛物碟卫星系统。dish 候选仅作「小型屋顶碟」头部，仍坐在同一 mast + 双 REVOLUTE 链上）。
- 不该混入：地面雷达 / 监控转台 / 电信基站机柜（理由：roof_antenna 的 root 是立在屋面 `z=0` 的高 mast，不是车载/地面机座或带馈线小室的基站；不引入额外 cabinet/dish-on-pedestal 大件）。
- 不该混入：旗杆 / 避雷针 / 烟囱本体（理由：必须有 mast 顶可瞄准的 array 头部 + azimuth/elevation 双关节；纯立杆无 array 不属本类。chimney 仅作 mount 背景件，非主体）。
- 不该混入：guy-wire / 拉索附件轴（理由：会产生 disconnected 细缆 island，结构价值低；source map 已 drop）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- 共享 helper：`_rod`（所有 rod-based type/reflector/mount 共用）；type-specific `_parabolic_dish_shell`/`_strut_mesh`（dish）、`_vertical_rod`/`_loop_segment`（dipole）、`_boom_point`（X_dual）、`_chimney_strap_mesh`（chimney ExtrudeWithHoles）、`_wall_plate_cq`（wall CadQuery）。panel 用 `mesh_from_cadquery` 内联，需 `import cadquery`。
- mast/antenna_head/articulation 骨架在 10 个样本间近乎逐字一致 → 抽成共享 builder，mount(Slot C) 与 array(Slot A) 作为可替换 emit。
- chimney_strap 是唯一会偏置 mast pole + 平移 azimuth origin 的 mount → resolve_config 必须把 `mast_x` 解析后同时喂给 mast 几何与 azimuth `Origin`。
- captured-pin / intentional overlap 需 element-scoped allow_overlap：collar↔mast_pole、clamp_block_{0,1}↔mast_pole、elevation_post↔per-type pivot 件、chimney strap_{i}↔mast_pole；X_dual 额外 elevation_post↔boom_spine_{0,1}。
- 暂不入 seed domain 的组合：无（type×mount×boom×N 全合法，仅受 conditional gating）。
