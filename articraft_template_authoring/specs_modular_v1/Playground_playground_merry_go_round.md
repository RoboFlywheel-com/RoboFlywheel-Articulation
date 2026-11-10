## 元信息
| 项 | 值 |
|---|---|
| slug | `playground_merry_go_round` |
| template path | `agent/templates/Playground_playground_merry_go_round.py` |
| test path (optional) | `tests/agent/test_playground_merry_go_round_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`pattern = mixed`：一个 fixed 中心支柱（Slot A）作为 parent，载一个 rideable cage（Slot B）作为单一 CONTINUOUS Z 旋转 child（`linear_chain` 主干 post→cage）；cage 内部用 `multiplicity` 复制 N 个 meridian 平面 + 次级纬环/竖栏（loop-emitted lattice，全部 fixed 到 cage 整体刚体）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in this category（1 parent + 6 rating-5 workbench variants）：逐个读取了 `model.py` |
| samples_adopted_as_module_sources | 7 |
| samples_read_but_not_adopted | 0 |
| source_index_policy | only adopted module sources are indexed below |

全量阅读后的结构族分布：

| 结构族 | 样本数 | 说明 |
|---|---:|---|
| square_box post + spherical_hoop cage（parent）| 1 | 方柱中心 + 上下轴颈 + 整球笼（纬向 Torus 环 + N 经向条纹弧）；单一 CONTINUOUS Z `cage_spin` |
| base_post 变体（同球笼，换支柱）| 2 | round_turned lathe 车削柱 / 三外撇腿 tripod stand；cage 拓扑不变 |
| cage_form 变体（同方柱，换笼体）| 2 | half_dome 半球穹顶落地环 / cylindrical_drum 上下等径环 + 竖栏鼓笼 |
| n_meridian multiplicity 档（同 post+球笼，换 N）| 2 | N=2 / N=4（parent N=3）→ 确认 meridian 平面数是 multiplicity 复制轴 |

被采纳样本逐条标注（全部 7 个都采纳为 module / multiplicity source；无未采纳样本）：
- `rec_model-a-spherical-playground-merry-go-round-orbi_20260610_085349_979414_2229be74` — adopted（parent）：square_box_post（Slot A）+ spherical_hoop_cage（Slot B）+ N=3 meridian multiplicity baseline。
- `rec_pmgr_var_roundpost` — adopted：Slot A `round_turned_post`（lathe 车削柱：base flange→锥轴→finial）。
- `rec_pmgr_var_tripod` — adopted：Slot A `tripod_stand`（三外撇腿 + 中央 hub + 升高 CENTER_Z）。
- `rec_pmgr_var_dome` — adopted：Slot B `half_dome_cage`（单上极轴承 + 半球弧落到底环 equator）。
- `rec_pmgr_var_drum` — adopted：Slot B `cylindrical_drum_cage`（上下等径环 + 竖栏 + spoke 辐臂）。
- `rec_pmgr_var_n2` — adopted：n_meridian N=2 档（结构与 parent 球笼相同，仅 N 不同）。
- `rec_pmgr_var_n4` — adopted：n_meridian N=4 档。

## 核心身份

`playground_merry_go_round` 是一个**可坐的旋转游乐设备**：地面上一根 fixed 中心支柱（post / stand）通过上（下）轴承 journal 承载一个 rideable cage（球笼 / 半球穹顶 / 圆鼓笼），整笼绕**竖直 Z 轴作单一 CONTINUOUS 360° 自由旋转**。cage 是一个 loop-emitted lattice：纬向水平环（Torus）+ N 个经向弧平面（candy-stripe 条纹管）或竖直栏杆，全部 fixed 到 cage，整笼作单刚体。成熟默认域应有：可辨认的固定中心支柱、贴 journal 的 collar 轴承、可坐尺度的笼体（直径 ~1.5–1.9 m）、candy-stripe 经向条纹、单一竖直 spin 关节。

边界：
- 这是一个**单 CONTINUOUS spin、无 per-seat 关节**的设备：整笼是一个刚体 child，不存在每个座位各自的 REVOLUTE。不要混入下面相邻类别。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_model-a-spherical-playground-merry-go-round-orbi_20260610_085349_979414_2229be74` | `data/records/rec_model-a-spherical-playground-merry-go-round-orbi_20260610_085349_979414_2229be74/revisions/rev_000001/model.py:L86-L113`（square_box post）, `L117-L213`（spherical_hoop cage + N meridian multiplicity）, `L218-L226`（cage_spin CONTINUOUS） | Slot A `square_box_post` + Slot B `spherical_hoop_cage` + n_meridian baseline + 主关节 |
| S2 | `rec_pmgr_var_roundpost` | `data/records/rec_pmgr_var_roundpost/revisions/rev_000001/model.py:L77-L98`（lathe profile）, `L115-L141`（round post build） | Slot A `round_turned_post` |
| S3 | `rec_pmgr_var_tripod` | `data/records/rec_pmgr_var_tripod/revisions/rev_000001/model.py:L87-L99`（leg spline）, `L116-L208`（tripod stand build + journals） | Slot A `tripod_stand` |
| S4 | `rec_pmgr_var_dome` | `data/records/rec_pmgr_var_dome/revisions/rev_000001/model.py:L120-L211`（hemisphere cage：单上极 collar + 半球弧到底环） | Slot B `half_dome_cage` |
| S5 | `rec_pmgr_var_drum` | `data/records/rec_pmgr_var_drum/revisions/rev_000001/model.py:L109-L252`（drum cage：上下等径环 + 竖栏 + spoke 辐臂 + clamp） | Slot B `cylindrical_drum_cage` + drum_bar multiplicity |
| S6 | `rec_pmgr_var_n2` | `data/records/rec_pmgr_var_n2/revisions/rev_000001/model.py:L51`（N=2）, `L182-L196`（meridian loop） | n_meridian N=2 档 |
| S7 | `rec_pmgr_var_n4` | `data/records/rec_pmgr_var_n4/revisions/rev_000001/model.py:L51`（N=4）, `L182-L196`（meridian loop） | n_meridian N=4 档 |

## 槽位 + 候选模块表

### Slot A：base_post（固定中心支柱 — 承 cage_spin 轴承）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `square_box_post` | S1 | `L86-L113` | eligible if compatible | 方柱中心：`base_plate` Box + `post_column` Box(POST_W×POST_W×POST_H) + `post_cap` + 上下 `journal_{tag}` Cylinder；笼挂上下双 journal。part tree=单 `post` part，多个 visual。 |
| `round_turned_post` | S2 | `L77-L98,L115-L141`| eligible if compatible | 圆车削柱：圆 `base_plate` Cylinder + `post_column` 用 `LatheGeometry(_turned_post_profile)`（base flange→锥肩→slim shaft→annular ridge→finial）+ 上下 journal。primitive=lathe 旋转体，与 square 拓扑同接口但 primitive 不同。 |
| `tripod_stand` | S3 | `L87-L99,L116-L208`| eligible if compatible | 三外撇腿落地：中央 `hub` Cylinder + `hub_flange` + 中央 `shaft` Cylinder + 3 条 `leg_{i}`（`tube_from_spline_points` hub→ground foot）+ `foot_{i}` + `leg_clamp_{i}` + 上下 journal。part tree 显著不同（loop3 腿件），CENTER_Z 抬高到 1.40。 |

### Slot B：cage_form（可坐笼体 — 整体随 CONTINUOUS spin 转）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `spherical_hoop_cage` | S1 | `L117-L213` | eligible if compatible | 整球：上下双 `collar_{tag}`（lathe shell sleeve）+ 4 条 `LATITUDE_RINGS` Torus（equator 最大）+ N 个 `meridian_arc_k`（极到极全弧，candy-stripe sleeve）+ `clamp_{tag}_{k}`。双极轴承。 |
| `half_dome_cage` | S4 | `L120-L211` | eligible if compatible | 半球穹顶：**单上极** `collar_upper` + 4 纬环（floor base 最大 → 向顶收缩）+ N 个 meridian 弧（顶极 collar 向下到 equator/floor ring，phi `[ARC_PHI0, π/2]`）+ clamp。无下极 journal，落在底环平面上。 |
| `cylindrical_drum_cage` | S5 | `L109-L252` | eligible if compatible | 圆鼓笼：上下双 collar + 4 条**等径** `DRUM_RINGS` Torus（同 DRUM_R）+ K 条竖直 `vertical_bar_i`（直管，candy-stripe）+ 上下 `spoke_{upper/lower}_i` 辐臂（collar→ring）+ clamp。无球面纬度，竖栏 lattice。 |

硬约束满足：Slot A 3 candidate（≥3），Slot B 3 candidate（≥3），都有真实 `model.py:Lx-Ly`。

## 槽位图（slot graph）

pattern = `mixed`（主干 linear_chain + cage 内 multiplicity）

```
[Slot A base_post]  --CONTINUOUS spin (axis Z (0,0,1), origin xyz=(0,0,CENTER_Z))-->  [Slot B cage_form]
        |                                                                                   |
        |  upstream interface: post 顶/上极 journal_{tag} (round Cylinder, JOURNAL_R)         |  multiplicity 内部:
        |  contact plane: collar_inner_R 套在 journal_R 上 (shaft-in-bushing)                 |    ×N meridian_arc_k / vertical_bar_i (loop, fixed 到 cage)
        |                                                                                   |    ×M latitude/drum rings (loop, fixed 到 cage)
        +-----------------------------------------------------------------------------------+    ×(N·M) clamp brackets (fixed parent visual)
```

接口点位说明：
- **跨 slot 关节**：唯一一个 `cage_spin` CONTINUOUS，axis=`(0,0,1)`，origin=`(0,0,CENTER_Z)`（笼中心高度）。parent=base_post，child=cage。range=unlimited（360° 自由）。
- **mating face / contact plane**：cage 的 `collar_{tag}`（hollow lathe sleeve，bore=COLLAR_INNER_R）**captured** 在 post 的 `journal_{tag}`（Cylinder，JOURNAL_R<COLLAR_INNER_R 留 press fit）。collar↔journal 是有意 overlap 的 shaft-in-bushing（需 element-scoped allow_overlap）。
- **轴承数量由 Slot B 派生**：`spherical_hoop_cage` / `cylindrical_drum_cage` 用上下双 journal（post 也必须出双 journal）；`half_dome_cage` 只用上极单 journal（落地底环承底部）。这决定 Slot A 出几个 journal → 是 Slot A↔Slot B 的 conditional 接口。
- **互斥 / 派生**：三个 cage_form 互斥（一次只选一个）；三个 base_post 互斥。CENTER_Z 由（post + cage_form）组合派生（tripod 抬高、dome 落地环）。

## 每槽位 Module Emits / Interfaces

### Slot A / module `square_box_post`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 单 `post` part；visuals：`base_plate`,`post_column`(Box),`post_cap`,`journal_upper`,`journal_lower` | S1 / model.py:L86-L113 |
| internal joints | 无（全 fixed visual，根 part） | S1 / model.py:L86-L113 |
| upstream interface | 根 part，落地 base_plate（接地支撑面） | S1 / model.py:L86-L92 |
| downstream interface | 上下 `journal_{tag}` round Cylinder（JOURNAL_R），供 cage collar 套；提供 CONTINUOUS Z 轴 | S1 / model.py:L106-L112 |

### Slot A / module `round_turned_post`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 单 `post` part；visuals：圆 `base_plate`(Cylinder),`post_column`(LatheGeometry mesh),`journal_upper/lower` | S2 / model.py:L115-L141 |
| internal joints | 无 | S2 |
| upstream interface | 圆 base_plate 接地 | S2 / model.py:L117-L122 |
| downstream interface | 同 square：上下 journal（JOURNAL_R），CONTINUOUS Z 轴 | S2 / model.py:L134-L141 |

### Slot A / module `tripod_stand`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 单 `tripod_stand` part；visuals：`hub`,`hub_flange`,`shaft`,`shaft_collar`,`shaft_cap`,3×`leg_i`/`foot_i`/`leg_clamp_i`,上下 journal | S3 / model.py:L116-L208 |
| internal joints | 无（腿/hub/shaft 全 fixed） | S3 |
| upstream interface | 3 个 `foot_i` 落地三点支撑（LEG_SPREAD 外撇） | S3 / model.py:L177-L185 |
| downstream interface | 上下 journal（JOURNAL_R），CONTINUOUS Z 轴；CENTER_Z 抬高到 1.40 | S3 / model.py:L199-L208 |

### Slot B / module `spherical_hoop_cage`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 单 `hoop_cage` part；visuals：上下 `collar_{tag}`，4×纬环 Torus，N×`meridian_arc_k`+stripe，clamp | S1 / model.py:L117-L213 |
| internal joints | 无（全 fixed 到 cage，单刚体） | S1 |
| upstream interface | 上下 `collar_{tag}` bore（COLLAR_INNER_R）套上下 journal；consumer of CONTINUOUS spin | S1 / model.py:L119-L139 |
| downstream interface | rideable cage 表面（终端，无下游） | S1 |

### Slot B / module `half_dome_cage`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 单 `hoop_cage` part；visuals：**单** `collar_upper`，4×纬环（底环最大→上收缩），N×meridian 弧（顶极→equator floor），clamp | S4 / model.py:L120-L211 |
| internal joints | 无 | S4 |
| upstream interface | 仅 `collar_upper` 套上极 journal（要求 post 出上极 journal）；底环落在 equator 平面 | S4 / model.py:L122-L136 |
| downstream interface | rideable 半球面（终端） | S4 |

### Slot B / module `cylindrical_drum_cage`
| emits | 描述 | 来源 |
|---|---|---|
| parts | 单 `drum_cage` part；visuals：上下 collar，4×等径 Torus，K×`vertical_bar_i`+stripe，上下 `spoke_{u/l}_i` 辐臂，clamp | S5 / model.py:L109-L252 |
| internal joints | 无 | S5 |
| upstream interface | 上下 collar 套上下 journal；spoke 辐臂从 collar 外缘伸到 drum ring（结构支撑路径） | S5 / model.py:L111-L131,L204-L234 |
| downstream interface | rideable 圆鼓面（终端） | S5 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `base_post` | enum | `square_box_post`,`round_turned_post`,`tripod_stand` | `square_box_post` | choice | 由 deterministic procedural sampler 选；选择 Slot A module | S1/S2/S3 |
| `cage_form` | enum | `spherical_hoop_cage`,`half_dome_cage`,`cylindrical_drum_cage` | `spherical_hoop_cage` | choice | 同上；选择 Slot B module；派生 journal 数量与 CENTER_Z | S1/S4/S5 |
| `n_meridian` | int | `[2, 6]`（产品域；sources 覆盖 2,3,4） | `3` | independent | 加权采样（小 N 偏多）；经向平面数；drum 用于竖栏档间接 | S1/S6/S7 |
| `palette_style` | enum | `classic_candy`,`sky_blue_yellow`,`steel_worn`,`rust_retro`,`mint_coral` | `classic_candy` | choice | 仅改材质 rgba，不改拓扑；见 palette 节 | S1-S5 |
| `n_latitude_ring` | int | `[3, 5]`（sweep-only 次级档） | `4` | independent | 纬环/鼓环数量；hemisphere 向顶收缩，drum 等径 | S1/S4/S5 |
| `n_drum_bar` | int | `[8, 16]`（仅 drum，sweep-only） | `12` | conditional | 仅 `cage_form==cylindrical_drum_cage` 时有效；竖栏数 | S5/model.py:L50 |
| `cage_radius_scale` | float | `[0.92, 1.06]` | `1.0` | independent | 笼半径整体缩放（SPHERE_R/DRUM_R）；clamp 后受 rideable 尺度约束 | S1/S5 |
| `post_height_scale` | float | `[0.95, 1.08]` | `1.0` | independent | post/shaft 高度缩放 | S1/S3 |
| `center_z` | float | derived | — | equation | `= f(base_post, cage_form, post_height_scale)`：square/round 球笼=1.10，tripod=1.40，dome 落地环派生；不独立采样 | S1/S3/S4 |
| `journal_count` | int | derived | — | conditional | `= 1 if cage_form==half_dome_cage else 2`；post 出对应数量 journal | S4 |
| (—) | constraint | — | — | inequality | `COLLAR_INNER_R > JOURNAL_R`（press fit，collar bore 必须 ≥ journal 半径，留 ~0.001 间隙；违反则回缩 journal） | 接口 / clearance |
| (—) | constraint | — | — | inequality | `cage min_z > 0.05`（笼离地，CONTINUOUS 自由旋转不蹭地）；违反按比例抬 CENTER_Z 或回缩 cage_radius_scale | 接口 / support |
| (—) | constraint | — | — | inequality | `cage_radius·cage_radius_scale ≤ rideable 上限 (~0.98)`，下限保证可坐 (~0.72)；违反 clamp | 类别 identity |

## Multiplicity / Copy Logic

本类别有 **1 根主 multiplicity 轴 + 2 根次级 sweep-only 轴**。

### 主轴：`n_meridian`（经向平面数）
- `count_param`: `n_meridian`
- `N_range`: `[2, 6]`（产品全程；sources 覆盖 N=2/3/4，模板向上外推到 6）
- sampling domain（权重档）：小 N 高频（N=2,3,4 主力），N=5,6 稀有尾部；按加权采样。
- copied object：每个平面 emit 一个 `meridian_arc_k`（candy-stripe spline tube）+ 其 `meridian_stripe_{k}_{s}` sleeve + 每个纬环交点 `clamp_{tag}_{k}`。`spherical_hoop_cage`/`half_dome_cage` 用经向弧；`cylindrical_drum_cage` 的对应轴是 `n_drum_bar`（竖栏）见下。
- naming：`for k in range(2 * n_meridian)`（每平面 2 半弧）→ `f"meridian_arc_{k}"`；角度 `yaw = k * π / n_meridian`。
- placement：绕 Z 等角分布（`k·π/n_meridian`）。
- joint policy：全部 fixed 到 cage（无独立关节）；整笼单刚体随唯一 `cage_spin` 转。
- source/gating：S1(N=3)/S6(N=2)/S7(N=4)。

### 次级轴 1：`n_latitude_ring`（纬环 / 鼓环数）
- `count_param`: `n_latitude_ring`，`N_range`=`[3,5]`，sampling domain=均匀小档（默认 4）。
- copied object：水平 Torus 环（球笼按纬度堆叠并按 `sqrt(SPHERE_R²−h²)` 收缩；hemisphere 向顶收缩；drum 等径）+ 对应 clamp 行。naming=`ring_i` / `latitude_ring_{i}`。placement=沿 Z 按纬度堆叠。joint policy=fixed 到 cage。source=S1/S4/S5。

### 次级轴 2：`n_drum_bar`（竖栏数，仅 drum）
- `count_param`: `n_drum_bar`，`N_range`=`[8,16]`，conditional：仅 `cage_form==cylindrical_drum_cage`。
- copied object：竖直 `vertical_bar_i`（直管 + candy-stripe sleeve）+ `clamp_{top/bot}_i`。naming=`vertical_bar_{i}`，角度 `i·2π/n_drum_bar`。placement=绕圆周等角。joint policy=fixed 到 cage。source=S5/model.py:L50,L163-L170。

> module-local 固定复制（不暴露 count）：collar sleeve、spoke 辐臂（drum 固定 6 个）、stripe band 段数、base_plate/cap/finial ridge、tripod 的 3 条腿（结构固定 3，非可调 multiplicity）——这些作为 baked visual，不出 template-level count。

## 拓扑多样性审计

总组合数：
- slot 组合：base_post(3) × cage_form(3) = **9** distinct（post part-tree × cage lattice）。
- × n_meridian 采样档（N∈[2,6]=5 档，但 drum cage 用 n_drum_bar 而非 meridian）：对 spherical/dome 两个 cage，9 中 6 个组合 ×5 N 档 = 30；drum 3 个组合 × n_drum_bar 档(≈3 有效 distinct 拓扑档) = 9。
- 合计 distinct module/multiplicity 拓扑 ≈ **39+**（未计 n_latitude_ring 次级档与连续 scale）。


理由（低关节物体如何到 ≥10）：本类别**只有 1 个关节**（单 CONTINUOUS spin），多样性不来自关节数，而来自 **STRUCTURE**：
1. **base_post part-tree 3 种**（方柱单 part / lathe 旋转体 / 三腿 loop+hub+shaft → 显著不同 part/primitive skeleton）。
2. **cage_form lattice 3 种**（双极球面纬环+经弧 / 单极半球+底环 / 双极等径鼓环+竖栏+辐臂 → 不同 part 计数、不同 journal 数、不同 emit loop）。
3. **n_meridian / n_drum_bar multiplicity**：N 改变经向弧/竖栏复制件数 → part-count 拓扑等价类不同（N=2 vs N=6 是不同 distinct）。
4. journal_count（1 vs 2）随 dome 派生 → 又一拓扑分叉。
仅 (1)×(2)=9 已接近门槛，叠加 multiplicity 档轻松 ≥10（实测 distinct ≈39）。

seed_domain_policy：procedural_first。

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 对普通 seed 用 deterministic procedural sampling，`seed=0` 不特殊。先采上游 `base_post`，再采 `cage_form`（与 base_post 兼容性 gating），再对该组合解析 `journal_count`/`CENTER_Z`，再加权采 `n_meridian`（drum 时采 `n_drum_bar`），再采 `n_latitude_ring` 与连续 scale，最后 `resolve_config` 投影 inequality（press fit / 离地 / rideable 尺度）。少量 regression override 仅用于已知失败回归。random sweep + viewer 目检见下表。

Topology target：1000-seed slot choice tuple distinct 建议 ≥30（低于富类别建议 300 是因为本类别 slot 组合上界 9 + multiplicity 档，结构上界有限；这是低关节 single-spin 类别的合理上限，已在上文说明）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：初版模板应含 `cage_radius_scale`[0.92,1.06]、`post_height_scale`[0.95,1.08]，并 derive `center_z` / `journal_count`；连续 scale 仅改安全比例，受 press-fit / 离地 / rideable inequality clamp，不破坏 InterfaceSpec（collar↔journal）/multiplicity。按第 7 节 independent→equation→inequality→conditional 顺序在 `resolve_config` 求解。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | base_post → cage_form（gating）→ journal_count/center_z derive → 加权 n_meridian / n_drum_bar → n_latitude_ring → 连续 scale | slot_choices_for_seed matches build choices |
| compatibility matrix | half_dome_cage 强制 journal_count=1（post 只出上极 journal，底环落地）；spherical/drum 强制 journal_count=2；tripod_stand 抬高 center_z；n_drum_bar 仅 drum 有效（其它 cage 忽略） | no floating（collar 必须套 journal）、no collision（meridian 不互穿）、axis（Z spin）、cage 离地、max multiplicity（N≤6, bar≤16） |
| controlled local variation | cage_radius_scale / post_height_scale + clamp；center_z / journal_count derived | proportions 变化不破坏 collar↔journal 接口、离地 clearance、spin 轴、rideable identity |
| regression overrides | none / 已知失败回归或 reviewer 指定时才加（写明 seed+原因） | previously failed or reviewer-selected cases only |
| random sweep | seeds 0-49 初验，0-999 成熟审计 | 与 contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| base_post | 3 | yes | yes | square_box / round_turned / tripod |
| cage_form | 3 | yes | yes | spherical_hoop / half_dome / cylindrical_drum |

## Validator

- `slot_choices_for_seed` 返回 implemented module names（`base_post`,`cage_form`）+ 主 multiplicity（n_meridian / n_drum_bar）。
- `config_from_seed` 对所有普通 seed 用 deterministic procedural sampling；seed=0 不特殊。
- compatibility matrix / gating 阻止非法组合：half_dome → journal_count=1；spherical/drum → journal_count=2；n_drum_bar 仅 drum；tripod center_z 抬高。
- optional regression overrides 稀疏且有理由；主 seed domain 不无限循环 curated / modulo 表。
- 受控 local scale（cage_radius_scale/post_height_scale）clamp，且不破坏 collar↔journal 接口、离地 clearance、spin 轴 origin、rideable 尺度 identity。
- cross-part scale 依赖（center_z=equation、journal_count=conditional、press-fit/离地=inequality）在 `resolve_config` 求解，不留到 builder。
- 关键 InterfaceSpec / MatingContract 存在：每个 `collar_{tag}` captured 在对应 `journal_{tag}`（element-scoped allow_overlap + expect_within + expect_contact）；cage 与 post 同轴（expect_origin_distance xy）。
- 主关节 `cage_spin` 类型=CONTINUOUS、axis=(0,0,1)、origin=(0,0,center_z)。
- copied objects 命名/placement 遵守 policy：`meridian_arc_{k}`/`vertical_bar_{i}`/`ring_i`/`clamp_*` 稳定命名，等角/堆叠 placement，不只复制 visual 漏接口。
- decisive spin pose：cage 转 π/2 后 equator/top-ring 上某 clamp 从 +X 搬到 +Y，cage 仍同轴。

## Reject cases

- 没有可旋转 cage 的 spin 关节（成了静态 jungle gym / 攀爬架）。
- cage 漂浮：collar 没套到 journal，或 dome 底环没落地、tripod 腿不接地。
- 主关节轴非竖直 Z，或被做成多个 per-seat REVOLUTE（变成 chair-swing carousel，非本类别）。
- collar bore < journal 半径导致 press fit 反向穿模，或 collar 完全脱离 journal 漂浮。
- meridian/竖栏复制只改 visual 不随 N 改变 part 计数，或 N 过大互穿。
- half_dome 仍出双 journal（下极悬空）/ spherical 只出单 journal（下极脱落）。
- cage 蹭地（min_z ≤ 0）或笼半径缩到不可坐 / 胀到非 playground 尺度。
- 形态只靠 palette 颜色变化，post/cage 拓扑无区别。

## 与相邻类别的边界

- 不该混入：**chair-swing carousel / 旋转秋千木马**（多个独立 per-seat REVOLUTE 吊椅绕中心轴各自摆/转）——本类别是**单一 CONTINUOUS spin、整笼一个刚体、无 per-seat 关节**；若出现每座位独立关节即越界。
- 不该混入：**静态 jungle gym / 攀爬球笼 / dome climber**（无旋转关节的固定攀爬架）——本类别核心身份是可旋转 cage + spin 关节；缺关节即非本类别。
- 不该混入：**Ferris wheel / 摩天轮**（大型立式轮，绕**水平**轴转，吊舱挂轮缘）——本类别绕**竖直** Z 轴、地面单柱中心支撑、可坐笼体尺度（~1.8 m），非立轮吊舱。
- 不该混入：**playground_swing**（顶梁 + 吊点 + 摆动座具，REVOLUTE 摆荡）——本类别是中心柱旋转笼，非顶梁悬挂摆动。

## 模板实现备注（可选）

- `square_box_post` 与 `round_turned_post` 共享 journal helper（同 JOURNAL_R/JOURNAL_LEN，同接口），仅 post body primitive 不同（Box vs LatheGeometry）。
- collar↔journal captured-pin：每个 `(collar_{tag}, journal_{tag})` 对需 element-scoped `allow_overlap`（shaft-in-bushing），并配 `expect_within`(xy) + `expect_contact`。
- `half_dome_cage` 是唯一单 journal 组合：post factory 必须读 `journal_count` 只出上极 journal，否则下极悬空 journal 触发 floating/无用件。
- `cylindrical_drum_cage` 的 spoke 辐臂（collar→drum ring）是结构支撑路径，必须存在以避免 drum ring 仅靠竖栏悬挂；spoke 固定 6 根（module-local，不出 count）。
- meridian/drum-bar 与纬环交点的 clamp 是 parent visual（fixed），不是独立活动 part；但要随 N/纬环数同步生成命名。
- tripod 抬高 center_z=1.40，注意 cage 离地 inequality 在 tripod 下更宽松；square/round 球笼 center_z=1.10 时下极弧最低点需仍 >0.05 离地。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | Slot A / Slot B | square_box_post / spherical_hoop_cage | rec_model-a-spherical-...2229be74 | L86-L113 / L117-L213 / L218-L226 | post + cage + n_meridian baseline + 主关节 |
| S2 | Slot A | round_turned_post | rec_pmgr_var_roundpost | L77-L98, L115-L141 | lathe 车削柱 |
| S3 | Slot A | tripod_stand | rec_pmgr_var_tripod | L87-L99, L116-L208 | 三腿落地 stand |
| S4 | Slot B | half_dome_cage | rec_pmgr_var_dome | L120-L211 | 半球穹顶单极笼 |
| S5 | Slot B | cylindrical_drum_cage | rec_pmgr_var_drum | L109-L252 | 等径鼓笼 + 竖栏 + spoke + n_drum_bar |
| S6 | multiplicity | n_meridian N=2 | rec_pmgr_var_n2 | L51, L182-L196 | N=2 档 |
| S7 | multiplicity | n_meridian N=4 | rec_pmgr_var_n4 | L51, L182-L196 | N=4 档 |

## Palette / Colorway（palette_style）

观察自 7 个 source（共享材质：white_paint / steel_dark / sky_blue / worn_yellow / candy_red / stripe_white / rust）。`palette_style` 仅改材质 rgba，不改拓扑：

| palette_style | 描述（观察来源） | 主色映射 |
|---|---|---|
| `classic_candy`（默认） | white post + sky_blue 纬环 + 一道 worn_yellow + candy_red/white 经向条纹 | post=white_paint, ring=sky_blue, accent=worn_yellow, meridian=candy_red+stripe_white（S1-S5 默认） |
| `sky_blue_yellow` | 蓝黄主调，弱化红条纹（环全 sky_blue + yellow accent，经向偏蓝） | ring=sky_blue, accent=worn_yellow, meridian=sky_blue+stripe_white |
| `steel_worn` | 全 steel_dark 旧钢（无彩漆，工业旧设备感） | post/ring/meridian=steel_dark, accent=worn_yellow |
| `rust_retro` | 锈蚀做旧（rust 主 + 残留 candy_red） | post=rust, ring=rust, meridian=candy_red+rust, clamp=rust |
| `mint_coral` | 现代翻新薄荷+珊瑚（sky_blue 偏 mint + candy_red 偏 coral） | ring=mint(sky_blue 变体), meridian=coral(candy_red 变体)+stripe_white |

palette 数=5（满足 ≥3，落在 4–6 目标）。所有 colorway 复用既有 7 个 material key 的 rgba（或其轻微变体），不引入新结构。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 等待人工审核；未进入模板实现阶段 |
