# Watermill Waterwheel Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `watermill_waterwheel` |
| template path | `agent/templates/Machinery_Watermill.py` |
| test path | `tests/agent/test_watermill_waterwheel_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

> **⚠ 重叠预警（与 overshot_waterwheel 重复，需人工合并裁决）**：本类别的同级 spec
> `specs_modular_v1/overshot_waterwheel.md` 已存在，且基于 **31 个真实 5 星样本**写成。
> 该 spec 的 support / bucket-wheel / water-control 槽位与本 picture-subcat 池（8 个
> workbench fork）有实质重叠：两者都覆盖 overshot bucket wheel + 支撑架 + 水平连续 hub
> 自旋。本 spec 的池更宽（同时覆盖 breastshot 斜扇叶与 flat-paddle 平桨板，不止 overshot），
> 且引入了 spokes 槽（辐条/腹板结构）与 mount 槽（trestle/millhouse/sluice）的显式拆分。
> 请人工审核决定：**(a)** 把本 spec 合并进 `overshot_waterwheel`（扩展其 wheel_type 槽），
> 还是 **(b)** 保留为更宽的独立 "watermill" 类别。详见「核心身份」与「审核记录」。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all candidates in this picture-subcat fork pool: 1 parent baseline + 8 planned workbench variants（`Machinery__Watermill`） |
| source_index_policy | 每个 slot candidate 的 module 来源都来自这 9 条记录中真实的 part/joint/helper 源码 |

**Dataset-root caveat**：这 9 条记录是 workbench-only 的 picture-subcat fork，rooted in the
`articraft_data` repo（`collections=['workbench']`，未 promote 到正式 dataset，
非传统 5 星抽样）。全部 fork 自同一 parent `afe3e6a1`（picture/Machinery/Watermill/001.png），
last compile = success，`run_tests` 通过 baseline 门控（恰含 1 条非 fixed joint =
`<mount>_to_waterwheel` CONTINUOUS hub spin，桨/斗循环计数 = `PADDLE_COUNT`）。引用一律写成
`data/records/<id>/revisions/rev_000001/model.py:Lx-Ly`。

源记录（record_id == variant dir）：

- parent 基线：`rec_model-a-stylized-wooden-watermill-waterwheel-mou_20260610_081149_220030_afe3e6a1`
- wheel_type：`rec_watermill_var_wheeltype_overshot`、`rec_watermill_var_wheeltype_breastshot`
- mount：`rec_watermill_var_mount_millhouse`、`rec_watermill_var_mount_sluice`
- spokes：`rec_watermill_var_spokes_clasparm`、`rec_watermill_var_spokes_solidweb`
- paddle_count（multiplicity 样本）：`rec_watermill_var_paddles_n12`、`rec_watermill_var_paddles_n16`

## 核心身份

Watermill waterwheel 是一只绕水平轴连续自旋的木/石质水轮：静态 mount（自立 A 字台架 /
磨坊墙立面 / 砌石水渠）通过两端镗孔轴承块托住穿过双轮缘轮毂的金属轴；轮上沿圆周等角分布
N 块取水单元（平桨板 / overshot 封闭水斗 / breastshot 斜扇叶），轮缘内由辐条（直辐 / 抱箍
罗盘臂 / 实心腹板盘）填充；整轮相对 mount 只有**一条** CONTINUOUS hub 自旋（world +Y 水平轴）。
取水单元随轮刚体，无独立 joint。默认成熟域是低多边形风格化木水轮（轮径 ~1.8 m，整体高 ~2.2 m，
轮宽 ~0.5 m）。

边界：
- 不包括 undershot 之外读不出水力语义的普通飞轮 / 齿轮（必须有取水单元 + 取水语义）。
- 不混入 windmill：不能有 cap yaw 或 wind sail lattice。
- 不混入 ferris wheel：不能有座舱/吊舱。
- 不给单块桨板加独立 REVOLUTE（那是可调距桨轮机构，偏离静态展示水轮，且与"整轮单 hub 自旋"冲突）。

> **与 `overshot_waterwheel.md` 的关系（必读）**：该 spec 已从 31 个真实 5 星样本写成，
> 覆盖 support_and_feed / bucket_wheel / water_control_or_service 三槽，与本 spec 的
> mount + wheel_type 子集实质重叠。差异点：本 spec 把 wheel_type 拓宽到 overshot **加**
> breastshot **加** flat-paddle，并显式拆出 spokes 槽；overshot spec 则额外有 chute/launder/
> sluice-gate/brake/guard 的 water-control 槽（本 fork 池没造这些活动控制件）。两者是否应合并由
> 人工裁决——见「审核记录」。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S0 | `rec_..._afe3e6a1` | `data/records/rec_model-a-stylized-wooden-watermill-waterwheel-mou_20260610_081149_220030_afe3e6a1/revisions/rev_000001/model.py:L124-L250` | parent 基线：trestle + flat_paddle + radial spokes + hub spin + paddle_count 循环 |
| S1 | `rec_watermill_var_wheeltype_overshot` | `data/records/rec_watermill_var_wheeltype_overshot/revisions/rev_000001/model.py:L128-L251` | enclosed overshot bucket helper + bucket emit loop |
| S2 | `rec_watermill_var_wheeltype_breastshot` | `data/records/rec_watermill_var_wheeltype_breastshot/revisions/rev_000001/model.py:L125-L233` | breastshot 斜扇叶 geometry/origin helper + emit loop |
| S3 | `rec_watermill_var_mount_millhouse` | `data/records/rec_watermill_var_mount_millhouse/revisions/rev_000001/model.py:L131-L261` | 磨坊墙立面 mount + 外伸轴承托架 + `wall_to_waterwheel` |
| S4 | `rec_watermill_var_mount_sluice` | `data/records/rec_watermill_var_mount_sluice/revisions/rev_000001/model.py:L116-L264` | 砌石水渠 mount（渠墙 + 底板 + 墙顶轴承墩）+ `sluice_to_waterwheel` |
| S5 | `rec_watermill_var_spokes_clasparm` | `data/records/rec_watermill_var_spokes_clasparm/revisions/rev_000001/model.py:L127-L269` | 抱箍/罗盘臂成对辐 + 方毂盒 + segment helper |
| S6 | `rec_watermill_var_spokes_solidweb` | `data/records/rec_watermill_var_spokes_solidweb/revisions/rev_000001/model.py:L96-L223` | 实心腹板盘（取代开放辐条）+ web helper |
| S7 | `rec_watermill_var_paddles_n12` | `data/records/rec_watermill_var_paddles_n12/revisions/rev_000001/model.py:L51,L211-L220` | paddle_count multiplicity 样本 N=12 |
| S8 | `rec_watermill_var_paddles_n16` | `data/records/rec_watermill_var_paddles_n16/revisions/rev_000001/model.py:L51,L211-L220` | paddle_count multiplicity 样本 N=16 |

## 槽位 + 候选模块表

### Slot A：wheel_type（被复制取水单元的几何样式——决定 `paddle_{pi}`/`bucket_{pi}` 循环里发射什么）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `flat_paddle`（基线） | `rec_..._afe3e6a1` | L51-L53, L211-L221 | eligible if compatible | `Box(PADDLE_DIMS)` 平直桨板，切向贴轮缘，`rpy=(0,ang,0)` 随角对齐，中心半径 `PADDLE_R=0.84` |
| `enclosed_bucket`（overshot） | `rec_watermill_var_wheeltype_overshot` | L128-L150（helper `_bucket_solid`）, L240-L251（emit） | eligible if compatible | L 形封闭水斗：floor + 抬高 back wall，`BUCKET_R=0.795` 嵌入轮缘，开口朝 +X（顶进水式） |
| `angled_scoop`（breastshot） | `rec_watermill_var_wheeltype_breastshot` | L125-L135（helper `_scoop_vane_geometry`/`_scoop_vane_origin`）, L225-L233（emit） | eligible if compatible | 斜置 `PADDLE_TILT=30°` 离径的扇叶，`rpy=(0, ang+TILT, 0)`（腰进水式） |

### Slot B：mount（静态地参——`<mount>_to_waterwheel` joint 的 parent part）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `trestle_aframe`（基线） | `rec_..._afe3e6a1` | L132-L179（build）, L117-L121（`_bearing_block_solid`） | eligible if compatible | 自立 A 字木台架：双侧斜腿 `leg_{fi}_{li}` + 方脚 `foot` + 横撑 `cross_brace` + 顶端镗孔轴承块 + 前后对角撑 |
| `millhouse_wall` | `rec_watermill_var_mount_millhouse` | L131-L192（build）, L253-L261（joint `wall_to_waterwheel`） | eligible if compatible | 竖板墙立面 `plank_wall` + 板缝/横档 + 两根外伸轴承托架 `bearing_bracket_{fi}` + 斜撑 gusset + 螺栓 |
| `masonry_sluice` | `rec_watermill_var_mount_sluice` | L116-L195（build + `_channel_wall_solid`）, L256-L264（joint `sluice_to_waterwheel`） | eligible if compatible | 双侧渠墙 `channel_wall_{wi}` + 底板 `channel_floor` + 墙顶轴承墩 `bearing_pier_{wi}`，轮落槽内 |

### Slot C：spokes（轮缘内辐条结构——`waterwheel` 内的固定填充）
| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `radial_spoke_bars`（基线） | `rec_..._afe3e6a1` | L200-L209（spoke loop）, L195-L199（hub） | eligible if compatible | 3 根直径杆/侧（`SPOKE_BARS=3`,`rpy=(0,si*pi/3,0)`）→ 6 直辐，汇于圆柱轮毂 `hub_{ri}` |
| `clasp_compass_arm` | `rec_watermill_var_spokes_clasparm` | L127-L139（helper `_segment_box_origin`）, L212-L269（hub_box + clasp loop） | eligible if compatible | 弦切落缘的成对抱箍/罗盘臂 `clasp_arm_{ri}_{si}_{ai}` + 弦 `clasp_chord` + 方毂盒 `hub_box_{ri}` |
| `solid_web_disc` | `rec_watermill_var_spokes_solidweb` | L96-L110（helper `_web_disc_solid`）, L204-L223（web emit） | eligible if compatible | 实心圆腹板盘 `web_disc_{ri}` 带中心毂孔，取代开放辐条，配圆柱毂 `hub_{ri}` |

> 三槽基线均由同一 parent 覆盖，每槽各补两个结构性不同的候选 → 每槽 3 candidate，无空格子。
> Candidate 之间为真实拓扑差异（封闭水斗 vs 平板 vs 斜扇叶；台架 vs 墙 vs 渠墙；直辐 vs 抱箍臂
> vs 实心盘），非纯尺寸/颜色变体。

## 槽位图（slot graph）

pattern: `mixed`（parallel_children + multiplicity）

```text
[Slot B mount] -- <mount>_to_waterwheel CONTINUOUS, axis=(0,1,0) @ z=AXLE_Z=1.30 --> [waterwheel 主旋转部件]
[waterwheel] <== Slot A wheel_type: N× FIXED-to-wheel 取水单元 paddle_{pi}/bucket_{pi}（无独立 joint）
[waterwheel] <== Slot C spokes: 固定填充辐条/腹板（无独立 joint）
```

接口点位与约束：
- **mount ↔ wheel**：`bearing_block_*` 沿局部 Y 的 `BORE_R=0.033` 通孔 = 轴颈承托面；consumer
  joint `<mount>_to_waterwheel` 原点贴轴心 `(0,0,AXLE_Z)`，axis = +Y（轴线），`axle`/
  `axle_collar_{ci}` 故意 captured 在轴颈孔内（parent 已用 `allow_overlap`+`expect_overlap`
  规约，变体须沿用）；type = CONTINUOUS，无限程，`MotionLimits(effort=80, velocity=6)`。
- **取水单元 ↔ wheel**：挂在 `waterwheel` 缘上，中心半径 `PADDLE_R`/`BUCKET_R`，mating face =
  轮缘外圈，anchor = 各单元 `(R*sin(ang),0,R*cos(ang))` 角向中心；随轮刚体，**无独立 joint**。
- **spokes ↔ rim/hub**：落在 `rim_{ri}` 平面（`RIM_Y=±0.21` 偏置）与 `hub_{ri}`/`hub_box_{ri}`
  之间，承托面 = 轮毂外缘 + 轮缘内圈。
- Slot A / Slot C 互斥关系：同一轮上只选一个 wheel_type 与一个 spokes module（不并存）。
  Slot B 与 wheel 解耦，仅改 joint parent part 与首段 joint 名（`trestle_/wall_/sluice_`）。

## 每槽位 Module Emits / Interfaces

### Slot A / module `flat_paddle`
| emits | 描述 | 来源 |
|---|---|---|
| parts | N× `paddle_{pi}` visual（baked 进 `waterwheel`） | S0 / model.py:L211-L221 |
| internal joints | 无（随轮刚体 FIXED） | S0 / model.py:L211-L221 |
| upstream interface | 轮缘外圈，中心半径 `PADDLE_R`，角 `ang=2π·pi/N` | S0 / model.py:L211-L221 |
| downstream interface | 无（终端取水单元） | — |

### Slot A / module `enclosed_bucket`
| emits | 描述 | 来源 |
|---|---|---|
| parts | N× `bucket_{pi}`（helper `_bucket_solid`：floor+back wall） | S1 / model.py:L240-L251 |
| internal joints | 无（随轮刚体 FIXED） | S1 / model.py:L240-L251 |
| upstream interface | 轮缘外圈，`BUCKET_R=0.795` 嵌入双 rim 平面（`expect_overlap` y≥0.04） | S1 / model.py:L240-L251, L426-L443 |
| downstream interface | 无 | — |

### Slot A / module `angled_scoop`
| emits | 描述 | 来源 |
|---|---|---|
| parts | N× `paddle_{pi}` 斜扇叶（共享 `Box(PADDLE_DIMS)`） | S2 / model.py:L225-L233 |
| internal joints | 无（随轮刚体 FIXED） | S2 / model.py:L225-L233 |
| upstream interface | 轮缘外圈，`rpy=(0, ang+30°, 0)`（离径倾斜） | S2 / model.py:L130-L135 |
| downstream interface | 无 | — |

### Slot B / module `trestle_aframe`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `trestle_frame`：`leg`/`foot`/`cross_brace`/`bearing_block_{fi}`/`diagonal_brace` | S0 / model.py:L132-L179 |
| internal joints | 无（单刚体静态地参） | S0 / model.py:L132-L179 |
| upstream interface | 接地：feet 在 z=0；apex 镗孔轴承块在 `AXLE_Z=1.30` | S0 / model.py:L161-L168 |
| downstream interface | `bearing_block_*` 轴颈孔 → consumer joint `trestle_to_waterwheel` | S0 / model.py:L240-L248 |

### Slot B / module `millhouse_wall`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `mill_wall`：`plank_wall`/`plank_seam`/`wall_batten`/`bearing_bracket_{fi}`/`angle_gusset`/`bearing_block_{fi}`/`bearing_bolt` | S3 / model.py:L131-L192 |
| internal joints | 无 | S3 / model.py:L131-L192 |
| upstream interface | 接地：墙底 z=0；外伸托架 `expect_contact` 嵌墙；wheel `expect_gap` x≥0.03 离墙 | S3 / model.py:L411-L426 |
| downstream interface | `bearing_block_*` → joint `wall_to_waterwheel` | S3 / model.py:L253-L261 |

### Slot B / module `masonry_sluice`
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sluice_mount`：`channel_floor`/`channel_wall_{wi}`/`bearing_pier_{wi}`/`bearing_block_{bi}` | S4 / model.py:L163-L195 |
| internal joints | 无 | S4 / model.py:L163-L195 |
| upstream interface | 接地：底板 z=0；墙顶墩 + 轴承座 `expect_overlap`/`expect_gap`；wheel 落槽内 | S4 / model.py:L372-L402 |
| downstream interface | `bearing_block_*` → joint `sluice_to_waterwheel` | S4 / model.py:L256-L264 |

### Slot C / module `radial_spoke_bars`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 每 rim 3 根 `spoke_bar_{ri}_{si}` + 圆柱毂 `hub_{ri}` | S0 / model.py:L195-L209 |
| internal joints | 无（随轮刚体） | S0 / model.py:L195-L209 |
| upstream interface | `rim_{ri}` 内圈（`RIM_Y=±0.21` 平面）→ `hub_{ri}` 外缘 | S0 / model.py:L195-L209 |
| downstream interface | 无 | — |

### Slot C / module `clasp_compass_arm`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 每 rim 6 对 `clasp_arm_{ri}_{si}_{ai}` + 弦 `clasp_chord` + 方毂盒 `hub_box_{ri}` | S5 / model.py:L212-L269 |
| internal joints | 无 | S5 / model.py:L212-L269 |
| upstream interface | 弦切落 `rim` 内圈（`expect_overlap` xz≥0.025），臂框住 `hub_box`（≥0.015） | S5 / model.py:L407-L424 |
| downstream interface | 无 | — |

### Slot C / module `solid_web_disc`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 每 rim `web_disc_{ri}`（带中心毂孔）+ 圆柱毂 `hub_{ri}` | S6 / model.py:L204-L223 |
| internal joints | 无 | S6 / model.py:L204-L223 |
| upstream interface | `WEB_R_OUT=RIM_R_IN+0.015` 嵌入轮缘内圈；hub boss 盖住中心孔（`expect_overlap` xz≥0.16） | S6 / model.py:L354-L367 |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `wheel_type` | enum | `flat_paddle` / `enclosed_bucket` / `angled_scoop` | — | choice | 由 deterministic procedural sampler 选择 | Slot A 表 |
| `mount` | enum | `trestle_aframe` / `millhouse_wall` / `masonry_sluice` | — | choice | sampler 选择；改 joint parent + 首段 joint 名 | Slot B 表 |
| `spokes` | enum | `radial_spoke_bars` / `clasp_compass_arm` / `solid_web_disc` | — | choice | sampler 选择 | Slot C 表 |
| `paddle_count` | int | `[6, 24]` | 9 | independent | 加权采样（中段偏多，尾部稀有），clamp 到范围；N 上限控编译时长 | S0/S7/S8 |
| `wheel_radius_scale` | float | `[0.85, 1.15]` | 1.0 | independent | 缩放 `RIM_R_OUT`/`PADDLE_R`/`BUCKET_R` 等保形量；clamp | S0 / L38-L53 |
| `axle_height_scale` | float | derived | 1.0 | equation | `AXLE_Z = f(wheel_radius_scale)`，保证轮底离地（轮顶 ~2.2 m 随径变） | S0 / L36-L52 |
| `paddle_radius` | float | derived | `PADDLE_R` | equation | `= RIM_R_IN < r < RIM_R_OUT`，锁定在轮缘环内 | S0 / L52 |
| (—) | constraint | — | — | inequality | 取水单元周向不自碰：`N · paddle_tangential ≤ 2π·PADDLE_R · k`（k<1）；违反时回缩 N 或单元尺寸 | 接口 / clearance |
| (—) | constraint | — | — | inequality | mount 轴承跨距 ≥ rim 外侧面跨距 + 间隙（`expect_gap` rim↔bearing ≥0.005） | 接口 / clearance |

注：`bucket`/`scoop` 的内部形状常量（floor/back-wall/tilt）为 module-local，固定随 module，不单独采样。

## Multiplicity / Copy Logic

本类别有 **1 根 multiplicity 轴**（`paddle_count`）。

- `count_param`：`paddle_count`（parent 源码常量 `PADDLE_COUNT`）
- `N_range`：`[6, 24]`（模板采样域；真实木水轮桨板常 8–20，留余量）
- sampling domain：中段加权（小/中 N 高频，大 N 稀有）；N 上限控编译时长
- copied object：单块取水单元 = 共享几何——`flat_paddle` 用 `Box(PADDLE_DIMS)`，
  `enclosed_bucket` 用 helper `_bucket_solid()`，`angled_scoop` 用 `_scoop_vane_geometry()`；
  每个一条 visual（依 wheel_type 命名）
- naming：`paddle_{i}`（overshot 风格为 `bucket_{i}`），`for pi in range(PADDLE_COUNT)` 循环发射
- placement：沿圆周角度等分，`ang = 2π·pi_i / PADDLE_COUNT`，
  `xyz=(R·sin(ang), 0, R·cos(ang))`，`rpy=(0, ang, 0)`（scoop 为 `ang+30°`），中心半径 `PADDLE_R`/`BUCKET_R`
- joint policy：**取水单元本身无 joint（随轮刚体 FIXED 到 `waterwheel`）**；整轮仅一条 hub 关节
  `<mount>_to_waterwheel` = `ArticulationType.CONTINUOUS`，`parent=mount`，`child=waterwheel`，
  `origin z=AXLE_Z`，`axis=(0,1,0)`，`MotionLimits(effort=80, velocity=6)`；**改 N 不增 joint**
- source/gating：N 样本已实证覆盖 `{9（S0 基线）, 12（S7）, 16（S8）}`；parent 已是干净的
  `for pi in range(PADDLE_COUNT)` 循环发射，n12/n16 仅改常量上界 + 同一角度等分公式，copy logic
  一眼可读，模板可直接以 parent 或任一 N 变体作 multiplicity 源码。
- spokes 槽的 `SPOKE_BARS`/`CLASP_SPOKE_PAIRS` 是 **module-local** 固定结构常量（非模板级
  multiplicity 轴），不暴露为 `*_count`；首版固定，不进入 N 采样。

## 拓扑多样性审计

总组合数：`A(wheel_type)=3 × B(mount)=3 × C(spokes)=3 = 27`（slot 组合）。
把 `paddle_count` 的采样档算进去（保守取 3 档样本 {小,中,大}）：`27 × 3 = 81`。

理由：仅 mount 槽就让 joint parent part 与首段 joint 名（`trestle_/wall_/sluice_`）三态变化，
wheel_type 槽切换取水单元 visual 数与 helper 几何，spokes 槽切换 rim 内填充的 part 拓扑
（直辐 6 条 vs 抱箍 6×3 条 vs 实心盘 1 块/侧）。27 个 slot 组合已远超 10 distinct。

seed_domain_policy：procedural_first。

### Procedural Sampling / Sweep Plan
`config_from_seed(seed)` 对普通 seed 用 deterministic procedural sampling；`seed=0` 不特殊。
先选 mount（决定 joint parent），再选 wheel_type 与 spokes（互斥单选），再加权采 `paddle_count`，
最后采 `wheel_radius_scale` 并派生 `axle_height_scale`/`paddle_radius`，用 inequality 投影/回缩。
Compatibility matrix / gating 以「槽位图」「Validator」中的接口、joint 轴、承托面、clearance 为准；
不兼容组合在 sampler/`resolve_config` 内降级/重采/拒绝，不留到 builder 失败。

Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类 slot 组合上限 27（×N 档可上探），
低于 300 的原因是类别本身 slot 基数有限——这是预期，不视为缺陷。

Controlled local parameterization：首版包含 `paddle_count`（multiplicity）、`wheel_radius_scale`
（independent 主尺度）、`axle_height_scale`/`paddle_radius`（equation 派生）。所有连续参数在
`resolve_config` clamp/派生，受 InterfaceSpec（轴承轴颈、rim 内圈承托）/clearance/joint 轴约束。

Regression overrides：默认无。若 sweep 发现稳定失败的跨格组合（如 enclosed_bucket + sluice：
水斗落槽穿模风险），由 reviewer 决定加少量显式 regression seed 或在 compatibility matrix 排除。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | mount → wheel_type → spokes → paddle_count → scales | slot_choices_for_seed matches build choices |
| compatibility matrix | wheel_type/spokes 互斥单选；enclosed_bucket+masonry_sluice 需查穿模；mount 与 wheel 解耦 | no floating, collision, axis, bucket-in-channel clearance |
| controlled local variation | `wheel_radius_scale` clamp + 派生 axle 高度/桨半径 | proportions vary without breaking bearing axis, rim seating, ground contact |
| regression overrides | none / reviewer-selected only | previously failed cross-slot combos |
| random sweep | seeds 0-49 初验，0-999 成熟审计 | , single-non-fixed-joint invariant, paddle count == PADDLE_COUNT |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A wheel_type | 3 | yes | yes | flat_paddle / enclosed_bucket / angled_scoop |
| B mount | 3 | yes | yes | trestle / millhouse / sluice |
| C spokes | 3 | yes | yes | radial_bars / clasp_arm / solid_web |

## Validator
- slot_choices_for_seed 返回已实现的 module 名（A/B/C 各 3）。
- config_from_seed 对所有普通 seed 用 deterministic procedural sampling。
- compatibility matrix / gating 阻止非法组合（互斥单选；bucket-in-sluice 穿模查验）。
- regression overrides 稀疏且有据。
- controlled local scale 被 clamp/派生，不破坏轴承轴线、rim 内圈承托、接地、joint 原点或类别 identity。
- cross-part scale 依赖（equation/inequality）在 `resolve_config` 求解，不留到 builder。
- 关键 InterfaceSpec/MatingContract 存在：`bearing_block_*` 轴颈孔 captured axle（allow+expect overlap）、
  rim↔bearing `expect_gap`、取水单元嵌 rim、spokes 嵌 rim 内圈/hub。
- 关键 joint 唯一：恰含 1 条非 fixed joint `<mount>_to_waterwheel` = CONTINUOUS，axis=(0,1,0)，
  origin z=AXLE_Z。
- copied 取水单元数 == `PADDLE_COUNT`，沿 rim 等角分布，命名 `paddle_{i}`/`bucket_{i}`。
- mount 接地（feet/墙底/底板在 z≈0），轮顶 ~2.2 m，轮径 ~1.8 m，轮宽 ~0.5 m（随 scale 浮动）。

## Reject cases
- 轮轴竖直，或没有 continuous hub 自旋（读成 flywheel/装饰盘）。
- 给单块取水单元加独立 REVOLUTE/可折桨 joint（读成可调距桨轮机构，越界）。
- 取水单元做成未连接的独立 FIXED child part（应 baked 进 `waterwheel`）。
- mount 悬空或 wheel 用不可见接口盘连接 mount（轴承轴颈接口缺失）。
- enclosed_bucket + masonry_sluice 组合时水斗穿渠墙/底板（未做 clearance gating）。
- spokes 与 rim/hub 之间有可见浮空缝（未嵌入 rim 内圈/hub）。
- 出现 windmill cap-yaw / 风帆 lattice 或 ferris 座舱（类别漂移）。
- 把整座磨坊建筑外壳塞进 mount 槽（喧宾夺主，读成 building 而非 watermill）。

## 与相邻类别的边界
- 不该混入：`overshot_waterwheel`（**重叠**，见预警）——若保留本 spec 为独立类别，两者需在
  compatibility/命名上人工对齐，避免重复造同一 overshot 子集。
- 不该混入：`traditional_windmill`（有风帆和 cap yaw；waterwheel 是水力驱动水平轮）。
- 不该混入：`ferris_wheel`（有座舱/乘客吊舱，不应有取水单元/水力语义）。
- 不该混入：`gear_train` / `pulley`（本类必须有取水单元 rim 和水力语义，非纯传动轮）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT，等待人工审核。**⚠ 合并裁决必读**：`specs_modular_v1/overshot_waterwheel.md` 已存在且基于 31 个真实 5 星样本，其 support_and_feed / bucket_wheel 槽与本 spec 的 mount + wheel_type(overshot 分支) 实质重叠。本 spec 来自 8 个 workbench picture-subcat fork（rooted in `articraft_data` repo），池更宽（额外覆盖 breastshot 斜扇叶 + flat-paddle 平桨板，并显式拆出 spokes 槽），但缺 overshot spec 的 water-control 槽（sluice-gate/brake/guard）。请人工决定：**(a)** 合并进 `overshot_waterwheel`（把本 spec 的 wheel_type/spokes 拓展并入），或 **(b)** 保留为更宽的独立 "watermill" 类别并在边界/命名上与 overshot spec 对齐。两条路径都需先解决命名与 slug 冲突再进入模板实现。 |
