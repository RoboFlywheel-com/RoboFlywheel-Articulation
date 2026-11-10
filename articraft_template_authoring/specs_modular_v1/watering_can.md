# Modular Spec — Agricultural / Watering can

## 元信息
| 项 | 值 |
|---|---|
| slug | `watering_can` |
| template path | `agent/templates/watering_can.py` |
| test path (optional) | `tests/agent/test_watering_can_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：单一 `can` hub 承载全部固定 visual（旋转身、喷嘴、rib 带、后握把、pivot 五金）
+ parallel-children 顶部机构（唯一非固定运动件 parent 到 `can`）+ multiplicity（波纹 rib 带 ×N）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category（1 origin + 9 slot-fork variants） |
| source_index_policy | only adopted module sources are indexed below |

阅读结论：origin（镀锌圆筒身 + 长直锥喷 + 上摆提梁 `can_to_bail` revolute + 后 C 握把 +
`rose_plate`）是主骨架。9 个 fork 各改一个功能层：body 4 包络（cylinder/oval_drum/bulbous/
conical）、spout 3 形态（long_straight/gooseneck/stubby）、spout_end 2（rose/open_nozzle，
open 图真）、顶部机构 3（swing_bail/single_D_handle/hinged_half_lid，各含 revolute）、rib 带
N（3→6）。全部沿用 CadQuery 旋转身 + `_frustum_tube`/`tube_from_spline_points`/`_rose_plate`/
`sweep_profile_along_spline` mesh 家族，无一降级为 Box/Cylinder 占位。**origin 给了图里没有的
`rose_plate`；`open_nozzle` fork 是 picture-true 修正锚**。

## 核心身份

浇水壶：薄壁开口金属（或塑料）壶身（旋转体/椭圆鼓/球腹/锥形），侧壁开孔焊接一根锥形出水
管（直/鹅颈/短粗），管口为莲蓬洒水头或裸开口；顶部一个主铰接机构（可上摆提梁 / 刚性 D 握把
/ 铰接半盖）供搬运或加水；壶身有卷边口沿、卷边底脚、波纹加强 rib 带、竖直卷缝、后侧固定握把
与提梁 pivot 五金。默认成熟域 = 手提家用/园艺浇水壶（body 高 ~0.30m、口径 ~0.33m）。

不该混入：水桶/提桶（无出水管、无洒水头）、茶壶/水壶 kettle（有壶嘴但带盖+底座加热、比例矮胖
且非园艺）、喷雾器/加压罐（有泵/扳机机构）、油壶/漏斗（无提梁、口部不同）。身份锚点 = 「侧壁锥
形出水管 + 顶部提梁/铰盖 + 薄壁开口壶身」三件套。

## 槽位 + 候选模块表

### Slot A：body_form（③ Primary Form Family，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 / form_subtype |
|---|---|---|---|---|---|
| cylinder | forked_anchor | origin `rec_use-the-attached-...2134a642` | L25-L37 (BODY_PROFILE) · L94-L104 (_body_shell_solid) · L211-L215 (visual) | eligible if compatible | 直筒旋转身；Volumetric Envelope Form |
| oval_drum | forked_anchor | rec_wateringcan_var_body_ovaldrum | L29-L43 (OVAL_Y_RATIO+profile) · L100-L124 (GTransform Y-scale revolve+cut) · L127-L167 (_elliptical_torus) | eligible if compatible | 扁椭圆鼓身（X 宽 Y 窄，GTransform）；Volumetric Envelope Form |
| bulbous | forked_anchor | rec_wateringcan_var_body_bulbous | L25-L61 (belly profile) · L118-L128 (_body_shell_solid) | eligible if compatible | 球腹+收颈旋转身；Volumetric Envelope Form |
| conical | forked_anchor | rec_wateringcan_var_body_conical | L28-L41 (taper profile) · L49-L51 (_wall_radius) · L114-L125 (_body_shell_solid) | eligible if compatible | 上宽下窄锥形旋转身；Volumetric Envelope Form |

### Slot B：spout_form（③ 喷管形态，扫掠/旋转母线变化）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| long_straight | forked_anchor | origin | L38-L41 (常量) · L241-L258 (`_frustum_tube` 长直锥+collar) | eligible if compatible | 长锥直管（0.045→0.024），管口远伸；Volumetric Envelope |
| gooseneck | forked_anchor | rec_wateringcan_var_spout_gooseneck | L41-L47 (GOOSENECK_SPLINE) · L247-L277 (`tube_from_spline_points` S 弧) | eligible if compatible | S 弧鹅颈样条扫管，管口抬高；Macro Surface Construction |
| stubby | forked_anchor | rec_wateringcan_var_spout_stubby | L43-L48 (SPOUT 常量) · L246-L265 (`_frustum_tube` 短粗低锥) | eligible if compatible | 短粗低锥管（0.055→0.048）；Volumetric Envelope |

### Slot C：spout_end（① 骨架：管口末端有/无洒水头）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| rose_sprinkler | forked_anchor | origin | L171-L187 (`_rose_plate` 穿孔盘 cadquery) · L261-L266 (定向 visual) | eligible if compatible | 管口加穿孔莲蓬洒水盘（3 环孔）；host visual |
| open_nozzle | forked_anchor | rec_wateringcan_var_nozzle_open（picture-true） | L233-L243（去掉 rose，管口留 `_frustum_tube` 环状开口） | eligible if compatible | 裸开口锥形管口（图真）；无额外 visual |

> 候选 2 个，已说明理由：Slot C 是「加/减一个末端 visual」的二元 ①-轴；`diffuser`（上翻散水口）
> 真实但留模板外推（niche，见排除项），不凑第三候选发明结构。

### Slot D：top_mechanism（② 关节类型 / 主铰接机构，互斥）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| swing_bail | forked_anchor | origin | L325-L361 (`sweep_profile_along_spline` 弯带 + `can_to_bail` REVOLUTE axis +Y ±) | eligible if compatible | 上摆提梁弯带，pivot 在侧壁 lug/rivet；1 revolute |
| d_handle | forked_anchor | rec_wateringcan_var_handle_dhandle | L325-L400 (双臂+横 grip+boss，`can_to_dhandle` REVOLUTE axis +Y ±) | eligible if compatible | 刚性 D 握把在同一 lug 轴 pivot；1 revolute |
| hinged_lid | forked_anchor | rec_wateringcan_var_lid_hinged | L367-L414 (半盘 cadquery + grip tab + hinge rod，`can_to_lid` REVOLUTE axis −Y 0→上界) | eligible if compatible | 铰接半盖罩加水口，pivot 在口沿全径 hinge rod；1 revolute（单向） |

> swing_bail / d_handle 共用侧壁 `bail_lug`/`bail_rivet` pivot 五金（z≈0.208，轴 +Y，双向 ±）；
> hinged_lid 改用口沿 `lid_hinge_rod`（z≈0.295，轴 −Y，单向 0→上界）——三者互斥、各含 ≥1 revolute。
> **每个候选都保证 ≥1 非固定 revolute**（无单体无关节壶）。

### Multiplicity：rib_count（④ 波纹加强带 ×N，见 §8）

| module | source_type | source evidence | model.py:Lx-Ly | 说明 |
|---|---|---|---|---|
| body_seam_{i} loop | forked_anchor | rec_wateringcan_var_ribs_dense | L228-L242（`for i in range(rib_count)` 等距 z，FIXED 装饰 visual） | 波纹 rib 带 ×N，宿主面派生半径，全 FIXED |

## 槽位图（slot graph）

pattern: mixed

```text
can (root hub: body_shell 旋转身 + top_rim/rolled_foot 卷边 + body_seam_{i}×N ribs
     + spout_tube + spout_collar + [rose_plate] + rear_handle + vertical_seam
     + pivot 五金[条件性])
  │
  ├─ body_form(A)     决定 BODY_PROFILE / y_scale / body_outer_x(z) —— 全部 host visual 从此派生
  ├─ spout_form(B)  --[FIXED host visual，root_x = body_outer_x(port_z)*width − embed]--> 侧壁 +X 焊接
  ├─ spout_end(C)   --[FIXED host visual 或空，锚在 spout 管口 tip]-->
  ├─ rib_count(N)   --[FIXED host visual ×N，z 等距，radius=body_outer_x(z)]-->
  └─ top_mechanism(D) --[REVOLUTE：swing_bail/d_handle=axis +Y@z0.208(lug) ±；
                          hinged_lid=axis −Y@z0.295(mouth rod) 0→上界]--> 独立运动 part
```

接口点位：
- **spout 焊接口**：`root_x = body_outer_x(port_z)*width_scale − SPOUT_EMBED`（管内端埋进 +X 壁），
  port cutter 沿 +X 贯穿壁（cut volume < uncut volume）。单一来源 `body_outer_x(z)`（Contract 3c）。
- **rib / rim / foot 环**：半径 = `body_outer_x(z)*width_scale`（circular torus；oval 用 `_elliptical_torus`，
  ry=rx·y_scale）——宿主面逐-z 派生共形（Rule 4）。
- **pivot 五金**：swing_bail/d_handle 用侧壁 `bail_lug_{i}`/`bail_rivet_{i}`（y=±body_outer_x(0.208)·y_scale·width，
  z=0.208）；hinged_lid 用 `lid_hinge_rod`（沿 Y 全径，端部埋入侧壁）。**互斥条件性 emit，避免闲置五金**。
- 跨 slot joint：仅顶部机构一条（或说三选一 revolute）；rib/spout/end 全 FIXED host visual（Rule 1，不建 part）。

## 每槽位 Module Emits / Interfaces

### Slot A / body_form（cylinder/oval_drum/bulbous/conical）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（全部为 `can` host visual：body_shell + top_rim + rolled_foot + vertical_seam） | origin L211-L320 |
| internal joints | 无 | — |
| upstream interface | 是 root hub，无 upstream | — |
| downstream interface | `body_outer_x(z)`（+X 外壁半径）+ `y_scale` + `mouth_inner_r` + `rim_z` 供 B/C/D/rib 派生 | conical L49-L51 |

### Slot B / spout_form（long_straight/gooseneck/stubby）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `can` host visual：`spout_tube` + `spout_collar` | origin L241-L258 |
| internal joints | 无（FIXED host visual） | — |
| upstream interface | 焊接在 body +X 壁的 `root_x`@port_z（B 消费 A 的 `body_outer_x`） | conical L60,L268 |
| downstream interface | spout tip（x,z,tip_angle）供 C 的 rose 定向 | origin L260-L263 |

### Slot C / spout_end（rose_sprinkler/open_nozzle）
| emits | 描述 | 来源 |
|---|---|---|
| parts | rose：`can` host visual `rose_plate`；open：无 | origin L261-L266 / nozzle L242 |
| internal joints | 无 | — |
| upstream interface | 锚在 B 的 spout tip（rpy 由 tip_angle 定） | origin L263 |
| downstream interface | 无 | — |

### Slot D / top_mechanism（swing_bail/d_handle/hinged_lid）
| emits | 描述 | 来源 |
|---|---|---|
| parts | swing_bail→`bail_handle`；d_handle→`d_handle`；hinged_lid→`lid` | 各 fork |
| internal joints | `can_to_bail`/`can_to_dhandle`（REVOLUTE axis +Y，limits −u..+u）/`can_to_lid`（REVOLUTE axis −Y，0..upper） | origin L353-L361 / dhandle L392-L400 / lid L406-L414 |
| upstream interface | swing_bail/d_handle：`can` 侧壁 lug/rivet@z0.208；hinged_lid：`can` 口沿 `lid_hinge_rod`@z0.295（captured-pin，grandfather 无 MatingContract） | origin L288-L304 / lid L395-L404 |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | cylinder / oval_drum / bulbous / conical | — | choice | deterministic sampler | Slot A |
| spout_form | enum | long_straight / gooseneck / stubby | — | choice | deterministic sampler | Slot B |
| spout_end | enum | rose_sprinkler / open_nozzle | — | choice | deterministic sampler | Slot C |
| top_mechanism | enum | swing_bail / d_handle / hinged_lid | — | choice | deterministic sampler | Slot D |
| rib_count | int | [2, 10] | 3 | independent | 加权采样（小 N 偏多），clamp | ribs_dense L228 |
| palette_style | enum | galvanized_zinc / rusted_steel / enamel_green / enamel_red / cream / copper / plastic_green | galvanized_zinc | choice | `rng.choice(PALETTE_STYLES)` | ⑥ |
| body_width_scale | float | [0.94, 1.08] | 1.0 | independent | 缩放 profile 半径；`body_outer_x(z)*ws` 全派生 | ⑤ |
| spout_length_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放 spout reach（long/stubby 末端 x、gooseneck 伸展） | ⑤ |
| handle_height_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 bail/D-handle 顶点 z | ⑤ |
| (—) spout 焊接 | constraint | — | — | equation | `root_x = body_outer_x(port_z)*body_width_scale − SPOUT_EMBED`，非独立 | Contract 3c |
| (—) port 贯穿 | constraint | — | — | inequality | port cutter `x_c < body_outer_x(port_z)*ws < x_c+extrude`；违反回缩 x_c | origin L98-L104 |
| (—) bail 跨度 | constraint | — | — | inequality | `bail_span_y > body_outer_x(0.208)*y_scale*ws + margin`（提梁需宽过壁） | conical L365-L379 |
| (—) 铰盖半径 | constraint | — | — | inequality | `lid_radius ≤ mouth_inner_r*ws*0.90`（半盖须落进口内壁） | lid L369 |

连续尺寸采样契约：先采 `independent`（width/spout_length/handle_height/rib_count）→ 按 `equation`
派生 `root_x`/环半径/lug y → 用 `inequality` 投影（port cutter、bail 跨度、lid 半径）→ 无 `conditional`。
所有约束在 `resolve_config` 求解，不留到 builder。

### 7.5 编译预算 / compile budget
**≤ 20s/seed**。依据：单个 CadQuery 旋转身（≤24 点 profile）+ 侧壁 port 布尔切 + `mesh_from_cadquery`
tolerance≈0.001；oval 多一次 GTransform；rose seed 多一次 ~35 孔布尔（open_nozzle seed 省去）。
mesh 家族与 origin 单记录同量级（库内实测旋转/布尔类 5-20s）。分档：主体旋转身 tolerance 0.001、
frustum/环 tube ≤48 段、rose 孔环 6/12/16、lug/rivet ≤32 段；N 个 rib 复用同一 torus mesh。
若超预算先降 tolerance/段数再迭代。sweep `--compile-timeout 120`（3× watchdog）。

## Multiplicity / Copy Logic

一根 multiplicity 轴：

- `count_param`: `rib_count` · `N_range`: 产品域 [2,10]（本小类波纹带常 3-6，偶见密纹到 10）;
  测试偏小 · sampling domain：加权 `weights=(3,4,4,3,2,2,1,1,1)` for N=2..10（小 N 高频，大 N 稀有）。
- copied object：波纹 rib 带 `body_seam_{i}`（TorusGeometry / oval 时 `_elliptical_torus`）。
- naming：`body_seam_{i}` for `i in range(rib_count)`（共享 geometry helper，禁止 copy-paste N 块）。
- placement：`z = foot_z + (i+1)/(N+1) * (shoulder_z − foot_z)` 等距；radius = `body_outer_x(z)*ws`（共形）。
- joint policy：全 FIXED host visual（Rule 1，非独立 part）；机构关节仍是 D 的 revolute。
- source/gating：ribs_dense L228-L242；N 只买覆盖不计 distinct。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | top_mechanism 换运动 part（bail_handle / d_handle / lid）→ part-joint 图变；spout_end open vs rose 加/减末端 visual。forked_anchor（Slot C/D 各 fork）。 |
| └ multiplicity | 同构件 ×N | 有 | rib_count N∈[2,10]，见 §8（加权，小 N 偏多）。 |
| ② 关节类型 | 图不变，换 type/轴 | 有 | 全 REVOLUTE 但轴/方向/行程不同：bail/dhandle=+Y 双向 [−u,+u]@z0.208；lid=−Y 单向 [0,upper]@z0.295。forked_anchor（can_to_bail / can_to_dhandle / can_to_lid）。三者均在 sweep 出现。 |
| ③ 主体形态家族 | 换核心 part 可识别形态原型 | 有 | body_form 4 包络（cylinder/oval_drum/bulbous/conical，登记进 slot_choices）+ spout_form 3（long/gooseneck/stubby）。form_subtype：body=Volumetric Envelope Form、gooseneck=Macro Surface Construction。forked_anchor（4 body fork + 3 spout fork）。 |
| ④ 表面装饰 | 原型不变，叠表面细节/改装饰数 | 有 | rib 波纹带 ×N（多少档，record_only ribs_dense）+ `top_rim`/`rolled_foot` 卷边 + `vertical_seam` 竖缝；宿主面逐-z 派生半径（③→⑤→④ 共形）。record_only + world_knowledge_extrapolation。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/比例/行程 | 有 | body_width_scale[0.94,1.08]、spout_length_scale[0.85,1.20]、handle_height_scale[0.90,1.12]；关节行程：bail/dhandle [−1.0,+1.0]@axis+Y（开向 fore/aft，pose 0.7 测「摆向 spout」），lid [0,1.5]@axis−Y（开向 up，pose 1.0 测「盖抬起」）。motion_test_plan：`fail_if_parts_overlap_in_sampled_poses(max_pose_samples=64)` + 每机构一条 targeted `ctx.pose`；captured-pin overlap 用 element-scoped `allow_overlap`。全程不穿模（bail/dhandle 行程收到清 spout/rear_handle 的范围；hinged_lid 与残余 pivot 硬件 coupled allow）。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 7 配色：galvanized_zinc / rusted_steel / enamel_green / enamel_red / cream / copper / plastic_green。材质大类：painted-metal（前 6）+ plastic（plastic_green）——覆盖 ≥ ceil(0.5×?) 达标。record_only + world_knowledge_extrapolation。 |

收尾自检：0-9 seed 渲染须肉眼见 body 四包络拉得开、spout 三形态、rose vs open、三机构会动、
rib 密度变化、7 配色都出现、装饰贴壁不悬空、关节开合不穿模。

## 拓扑多样性审计

总组合数：A(4) × B(3) × C(2) × D(3) = 72 离散组合 ×（rib N 9 档采样）≈ 648 结构-覆盖点。

理由：每 slot ≥2 candidate 且全部 reachable；36 seed 均匀采样即可让每 slot key 现 ≥2 值，`axis_realization` 可核。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 对每个 slot
`rng.choice(...)`、对 rib_count `rng.choices(range(2,11), weights=...)`、对 3 个 scale `rng.uniform`。
seed=0 不特殊。compatibility gating（见下表）在 `resolve_config` 排除易坏组合。无 regression override。
random sweep 0-15→0-35，corner stage 探未实现极值/组合。viewer 目检 0-9。
Topology target：1000-seed distinct 预期 按 ≥300 report-only 口径观察（72 离散 × N × scale 量化）。

Controlled local parameterization：body_width_scale / spout_length_scale / handle_height_scale——
均 `independent` 在 clamp 内均匀采样；`root_x`/环半径/lug y 由 `body_outer_x(z)*ws` 派生（equation）；
port cutter、bail 跨度、lid 半径由 inequality 投影。不破坏接口/清 spout 行程/类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 A→B→C→D→rib→scale；`rng.choice`/加权 N；无 modulo 表 | slot_choices_for_seed == build choices |
| compatibility matrix | (1) hinged_lid 与 gooseneck：lid 在口沿、gooseneck 从 +X 壁抬高，几何不冲突→合法；(2) open_nozzle 与任意 spout_form 合法（仅去 rose visual）；(3) hinged_lid 不 emit lug/rivet（用 hinge rod），swing_bail/d_handle 不 emit hinge rod——互斥条件 emit，杜绝闲置/漂浮五金；(4) bail/dhandle 行程 clamp 到清 spout+rear_handle；(5) oval 时全部环用 `_elliptical_torus`。 | no floating, no closed/sampled-pose collision, axis, max N, identity |
| controlled local variation | 3 个 scale + rib N，全 clamp/派生 | 比例变而不破接口/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | seeds 0-15 → 0-35（初过）；0-999（成熟审计） | contract failures；axis_realization / |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form (A) | 4 | yes | yes | ③ Primary Form Family |
| spout_form (B) | 3 | yes | yes | |
| spout_end (C) | 2 | yes | no | 二元 ①-轴；diffuser 留外推（见排除项） |
| top_mechanism (D) | 3 | yes | yes | ② 关节类型 |
| rib_count (N) | 9 档 | yes | yes | multiplicity 覆盖 |

## Validator

- slot_choices_for_seed returns implemented module names（含 `rib_count` 编码 `f"n{N}"`）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed 0 不特殊）
- compatibility matrix / gating：hinged_lid↔lug/rod 互斥 emit；oval↔elliptical rings
- optional regression overrides：none
- controlled local scale params clamped，不破 interfaces/clearance/joint origin/multiplicity
- cross-part scale dependencies（root_x=equation、port/bail/lid=inequality）在 `resolve_config` 求解
- critical interface points exist（spout port 贯穿；pivot 五金 captured-pin）
- key joints have expected type/axis/range（revolute +Y ± / −Y 0→upper）
- copied objects follow naming/placement（`body_seam_{i}`，z 等距，radius 共形）

## Reject cases

1. body_form 降级成裸 `Cylinder`/`Box`（丢旋转身/椭圆 GTransform）——违 Rule 3。
2. rib/rim/foot 用常数半径套在锥/球腹/椭圆壁外——脱壁悬空，违 Rule 4。
3. 顶部机构无 revolute（做成固定提梁）——零关节，判负。
4. spout port 未真正贯穿壁（cut volume == uncut）——出水口假开。
5. bail/D-handle 行程过大扫穿 spout/rear_handle 且用 broad allow_overlap 掩盖——违 Rule 5。
6. hinged_lid 仍 emit 未用的 bail lug/rivet 或 lid_hinge_rod 漂浮在口中央空隙——闲置/漂浮岛。
7. oval_drum 只缩 body 却不缩 rim/foot/rib/lug 的 Y——环与身错位悬空。
8. rose_plate 定向错（未按 tip_angle）导致洒水盘穿进管壁或悬空。

## 与相邻类别的边界

- 不该混入：水桶 / 提桶（Bucket）——无侧壁出水管、无洒水头；浇水壶身份锚点是「锥形出水管+顶部提梁/铰盖」。
- 不该混入：茶壶 / 电水壶（Kettle）——虽有壶嘴，但带盖+底座+加热、比例矮胖、非园艺薄壁开口身。
- 不该混入：喷雾器 / 加压喷罐——有泵/扳机加压机构，浇水壶靠重力倾倒无泵。
- 不该混入：油壶 / 漏斗——无提梁、口部与洒水功能不同。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 单 `can` hub + 4 slot + rib multiplicity；沿用 origin CadQuery 旋转身 mesh 家族；captured-pin 关节 grandfather（元素级 allow_overlap，镜像 source run_tests）。open_nozzle 为 picture-true 锚。 |

## 模板实现备注（可选）

- 共享 helper：`_body_shell_solid(form, ws)`（CadQuery 旋转 + oval GTransform + port cut）、
  `_body_outer_x(form, z)`（+X 外壁半径控制点插值，单一来源）、`_ring(z, tube_r, form, ws)`
  （circular / elliptical torus 二选一）、`_frustum_tube`/`tube_from_spline_points`（沿用 source）、
  `_rose_plate`、`_emit_bail`/`_emit_dhandle`/`_emit_hinged_lid`。
- captured-pin overlap：swing_bail/d_handle 的 washer/boss↔`bail_lug_{i}`/`bail_rivet_{i}`（axes yz），
  hinged_lid 的 lid knuckle↔`lid_hinge_rod`——全用 element-scoped `allow_overlap`（镜像各 source）。
- hinged_lid 若开盖极值与残余口沿硬件近接，用 coupled element-scoped allow（reason 写明「盖绕口沿转出」）。
- 暂不进 seed domain：diffuser 上翻散水口（niche，排除项）。

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D 骨架 | origin | rec_use-the-attached-...2134a642 | L25-L361 | body cylinder + long_straight + rose + swing_bail + rim/foot/rear_handle/lug/seam |
| S2 | A | oval_drum | rec_wateringcan_var_body_ovaldrum | L29-L167 | 椭圆鼓 GTransform + `_elliptical_torus` |
| S3 | A | bulbous | rec_wateringcan_var_body_bulbous | L25-L128 | 球腹 profile |
| S4 | A | conical | rec_wateringcan_var_body_conical | L28-L125 | 锥形 profile + `_wall_radius` |
| S5 | B | gooseneck | rec_wateringcan_var_spout_gooseneck | L41-L277 | 鹅颈样条扫管 |
| S6 | B | stubby | rec_wateringcan_var_spout_stubby | L43-L265 | 短粗低锥管 |
| S7 | C | open_nozzle | rec_wateringcan_var_nozzle_open | L233-L243 | 裸开口管口（picture-true） |
| S8 | D | d_handle | rec_wateringcan_var_handle_dhandle | L325-L400 | 刚性 D 握把 + `can_to_dhandle` |
| S9 | D | hinged_lid | rec_wateringcan_var_lid_hinged | L367-L414 | 铰接半盖 + `can_to_lid` + hinge rod |
| S10 | N | ribs | rec_wateringcan_var_ribs_dense | L228-L242 | rib_count 循环复制 |
