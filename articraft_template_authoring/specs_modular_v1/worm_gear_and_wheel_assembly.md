# Worm Gear And Wheel Assembly Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `worm_gear_and_wheel_assembly` |
| template path | `agent/templates/worm_gear_and_wheel_assembly.py` |
| test path (optional) | — |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel_children：worm + wheel 均挂到固定 housing；backlash 可插入 prismatic worm carriage） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 12 |
| read_count | 12 |
| read_scope | 源映射内全部 12 个 5 星样本（2 origin + 10 forked anchor）逐一读取 model.py |
| source_index_policy | 仅索引下方采纳 module source |

结构族分布（读全部 12 个源）：

| 结构族 | 样本 | 说明 |
|---|---|---|
| 固定 support/carrier + worm(CONTINUOUS,X) + wheel(CONTINUOUS,Y, mimic -1/N) | 全部 12 | 核心两轴啮合拓扑，轴永远互相垂直 |
| 轻量 mesh 几何（`_helical_thread_geometry` / `_toothed_wheel_profile` / `LatheGeometry` / `ExtrudeWithHolesGeometry`） | origin 001 及其 fork（split_housing / vertical_shaft / 2_start） | 无 cadquery，编译快 |
| 重 cadquery（`Worm` / `SpurGear` + 布尔壳体） | origin 002 及其 fork（enclosed_gearbox / top_mesh / eccentric / sliding / 1_start / 4_start） | 提供 housing/backlash 拓扑思想 |
| worm 轴竖直（Z）、置于 wheel +X 侧 | vertical_shaft fork | ③ 主体形态家族第二原型 |
| worm carriage + PRISMATIC（backlash 调节） | sliding_worm_carriage fork | ② 关节类型（新增 prismatic + 中间 part） |

被采纳样本（作为 module 源）：
- `S1 = rec_worm_gear_and_wheel_assembly__worm_gear_and_wheel_assembly__001_png_c097f6455b834d47b95478b26e163c36`（origin，轻量 mesh；worm/wheel/thread/toothed-wheel helper）。
- `S2 = rec_worm_gear_and_wheel_assembly__worm_gear_and_wheel_assembly__002_png_d1bae7f8a0f645068588a092bf260924`（origin，carrier + bearing collars + keyed hub 布局）。
- `S3 = rec_0611_worm_gear_and_wheel_assembly_var_housing_topology_enclosed_gearbox`（enclosed gearbox 壳体）。
- `S4 = rec_0611_worm_gear_and_wheel_assembly_var_housing_topology_adjustable_split_hous`（split housing）。
- `S5 = rec_0611_worm_gear_and_wheel_assembly_var_mesh_orientation_vertical_shaft_worm`（竖轴 worm）。
- `S6 = rec_0611_worm_gear_and_wheel_assembly_var_backlash_adjustment_sliding_worm_carri`（prismatic worm carriage）。
- `S7 = rec_0611_worm_gear_and_wheel_assembly_var_worm_starts_2_start_worm` / `..._4_start_worm` / `..._1_start_worm`（多头 worm）。

## 核心身份

**啮合的 worm-and-wheel 传动**：一根带螺旋螺纹的钢 worm 输入轴与一个多齿黄铜 worm wheel 啮合，两轴**永远互相垂直**（wheel 绕 Y，worm 绕 X 或 Z），并各自有一个真实的**旋转关节**（CONTINUOUS）。worm 螺纹始终与 wheel 齿顶**相切啮合**（螺纹外圆到齿顶保留一条小正间隙，切向啮合足迹重叠）。啮合几何**派生**：`center_distance = wheel_tip_radius + thread_outer_radius + mesh_clearance`，不硬编码放置。

边界（must_not_become）：
- 不是 **spur gear pair**（两平行轴同平面正齿轮啮合）——worm/wheel 轴必须垂直、worm 必须是螺旋螺纹而非直齿。
- 不是 **decorative gear display**（无真实关节的齿轮摆件）——必须有 ≥2 个真实非 FIXED 旋转关节且 wheel 随 worm 联动（mimic）。

## 槽位 + 候选模块表

### Slot A：housing_topology（① 骨架 / 固定根 part 的结构族）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `open_pillow_block` | forked_anchor | S1 | `L141-L178` | eligible | 敞开式：低基座 bar + 两根 shaft bearing post + 独立 wheel bearing 座；worm/wheel 完全外露 |
| `enclosed_gearbox` | forked_anchor | S3 | `L145-L205` | eligible | 铸造箱壳：底板 + 后板 + 两侧板 + 顶板，前面开 service aperture 露出 wheel/worm；壳壁在旋转包络外 |
| `split_housing` | forked_anchor | S4 | `L145-L260` | eligible | 上下对分箱体 + parting flange + bolt boss；下半为基座 |

三候选均把 housing 建成**一个固定 grounded part**，全部为 `housing.visual(...)`；共享同一 bearing 骨架（wheel 轴承座 + 两个 worm 端支座），仅外壳外形与螺栓/法兰细节不同。

### Slot B：mesh_orientation（③ 主体形态家族 / Primary Form Family，登记进 slot_choices）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | 结构特征 |
|---|---|---|---|---|---|
| `top_mesh` | forked_anchor | S2 | `L114-L143, L257-L276` | Volumetric Envelope Form | worm 轴水平（X），置于 wheel 正上方 +Z；worm_center = wheel + (0,0,cd)；worm 关节轴 (1,0,0) |
| `vertical_shaft` | forked_anchor | S5 | `L37-L42, L204-L248, L310-L322` | Volumetric Envelope Form | worm 轴竖直（Z），置于 wheel +X 侧；worm_center = wheel + (cd,0,0)；worm 关节轴 (0,0,1) |

mesh_orientation 同时改变 worm 关节**轴**（② 属性）与整体三维包络（③）：登记为 ③ 主体形态家族 slot。两原型都保持同一 part tree（housing/worm/wheel）、同一 primitive 家族（lathe 轴 + 螺旋螺纹 ribbon + 齿轮 extrude）、同一啮合接口（螺纹外圆切于齿顶），只改 worm 相对 wheel 的离散取向/包络（符合 §8.5 ③ + AUTHORING §A Rule 3）。

### Slot C：worm_starts（① multiplicity / N 头数）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `1_start_worm` | forked_anchor | S7(1_start) | `L204-L235` | eligible | 单头螺旋螺纹 1 条 ribbon |
| `2_start_worm` | forked_anchor | S7(2_start) | `L204-L235` | eligible | 双头：2 条 ribbon，相位差 π |
| `4_start_worm` | forked_anchor | S7(4_start) | `L204-L235` | eligible | 四头：4 条 ribbon，相位差 π/2 |

N 头数只增复制同构螺纹 ribbon（相同 outer radius → 啮合几何不变），是 §8 count 轴。

### Slot D：backlash_adjustment（② 关节 / 机构类型）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `eccentric_bearing` | forked_anchor | S2 | `L257-L276` | eligible | 基础 2 关节：worm 直接挂 housing（CONTINUOUS）；偏心轴承座为 housing visual 细节 |
| `sliding_carriage` | forked_anchor | S6 | `L267-L301` | eligible | 3 关节：新增 `worm_carriage` part，housing→carriage 为 **PRISMATIC**（沿 mesh_dir，调背隙），carriage→worm 为 CONTINUOUS |

### Slot E：palette_style（⑥ 材质 / 涂装）

| module_name | source_type | source evidence | 结构特征 |
|---|---|---|---|
| `polished_steel_brass` | record_only | S1 `L136-L139` | 抛光钢 worm + 金黄黄铜 wheel + 深槽阴影（origin 001 配色） |
| `cast_iron_brass` | record_only | S2/S3 `L25-L28` | 亮黄铜 wheel + 深铸铁 gunmetal housing + 抛光钢轴（origin 002 配色） |
| `gunmetal_bronze` | world_knowledge_extrapolation(⑥) | anchors S1,S2 + reviewer | 青铜 wheel + gunmetal housing + 钢轴（同族真实金属配色） |
| `machined_steel` | world_knowledge_extrapolation(⑥) | anchors S1,S2 + reviewer | 全机加工钢灰 + 淡黄铜 wheel |
| `blackened_steel_brass` | world_knowledge_extrapolation(⑥) | anchors S1,S2 + reviewer | 发黑钢 housing + 黄铜 wheel + 亮钢轴 |

## 槽位图（slot graph）

pattern = `mixed`（parallel_children + optional prismatic 中间件）

```
[housing] (grounded, 固定根)
    |-- CONTINUOUS Y (mating: wheel_bearing_collar⟂thrust_collar) --> [worm_wheel]
    |                                                                   （mimic 关联到 worm，-1/teeth）
    |-- (eccentric)  CONTINUOUS worm_axis (grandfathered pin-in-collar) --> [worm_shaft]
    |
    |-- (sliding)    PRISMATIC mesh_dir (grandfathered rail) --> [worm_carriage]
                                              |-- CONTINUOUS worm_axis --> [worm_shaft]
```

- 接口点位：
  - housing→worm_wheel：wheel 轴向 Y 的**推力面接触**（housing `wheel_bearing_collar` 的 −Y 面 ⟷ wheel `axle_thrust_collar` 的 +Y 面）→ 真实 `MatingContract`。
  - housing→worm_shaft：worm 端 shaft 穿过 housing/carriage 的 bearing collar（pin-through-sleeve）→ Rule 2 grandfather，omit mating，element-scoped `allow_overlap`。
  - housing→worm_carriage（sliding）：carriage rail 在 housing rail guide 内滑动（prismatic 原点是 gauge 自由度，免 origin 检查）→ grandfather，`allow_overlap`。
- 跨 slot joint type / axis：wheel = CONTINUOUS Y（永远）；worm = CONTINUOUS，轴由 mesh_orientation 决定（top=X / vertical=Z）；carriage = PRISMATIC，轴 = mesh_dir。
- 互斥/派生：`sliding_carriage` 时 worm 的 parent 是 carriage 而非 housing；worm 端 bearing 支座随之挂到 carriage。

## 每槽位 Module Emits / Interfaces

### Slot A / housing（open_pillow_block / enclosed_gearbox / split_housing）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `housing`（单 part，全部 visual） | S1/S3/S4 |
| internal joints | 无（固定壳体细节全部 fuse 为 visual，遵 Rule 1） | S1 L141-178 |
| upstream interface | grounded 根，无 upstream | — |
| downstream interface | `wheel_bearing_collar`（−Y 面，供 wheel 推力 mating）；worm 端 bearing collar（供 worm 支承）；（sliding）rail guide | S2 L157-179 |

### Slot B / mesh_orientation（worm 放置 + 轴）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；决定 worm_center 与 worm_axis、prismatic 方向 mesh_dir | S2 / S5 |
| internal joints | worm 关节轴（X 或 Z） | S2 L272 / S5 L315 |

### Slot C / worm_starts（worm_shaft 螺纹 ribbon ×N）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `worm_shaft`：`chamfered_shaft`(lathe) + `helical_thread_k`(k∈[0,N)) + `valley_shadow` + 两 `thread_shoulder` | S1 L190-242, S7 |
| internal joints | 无（螺纹 ribbon 为 worm visual） | — |

### Slot D / backlash_adjustment
| emits | 描述 | 来源 |
|---|---|---|
| parts | eccentric：无额外 part；sliding：`worm_carriage`（bearing collars + saddle） | S6 L200-236 |
| internal joints | sliding：housing→carriage PRISMATIC + carriage→worm CONTINUOUS | S6 L277-301 |
| upstream interface | carriage rail 面（−mesh_dir，滑入 housing rail） | S6 |

### wheel（worm_wheel）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `toothed_rim`(extrude-with-hole 齿廓) + `bored_hub` + `dark_bore_depth` + `set_screw_hole_i` + `rear_axle_stub` + `axle_thrust_collar` | S1 L244-301, S2 L187-226 |
| internal joints | 无 | — |
| upstream interface | `axle_thrust_collar` +Y 面（与 housing wheel_bearing_collar mate）；`rear_axle_stub` 入 collar | S2 L215-226 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `housing_topology` | enum | open_pillow_block / enclosed_gearbox / split_housing | — | choice | 由 procedural sampler 选 | Slot A |
| `mesh_orientation` | enum | top_mesh / vertical_shaft | — | choice | 决定 worm_axis / mesh_dir | Slot B |
| `worm_starts` | int | {1,2,4} | 1 | choice | ribbon 复制数 | Slot C |
| `backlash_adjustment` | enum | eccentric_bearing / sliding_carriage | — | choice | 决定是否插入 prismatic carriage | Slot D |
| `palette_style` | enum | 5 colorways | polished_steel_brass | choice | `rng.choice(PALETTE_STYLES)` → mats[...] | Slot E |
| `wheel_size_scale` | float | [0.85, 1.25] | 1.0 | independent | 范围内均匀采样后 clamp | S1 L24-29 |
| `worm_size_scale` | float | [0.90, 1.15] | 1.0 | independent | 均匀采样后 clamp | S1 L33-36 |
| `worm_length_scale` | float | [0.85, 1.25] | 1.0 | independent | 均匀采样后 clamp | S1 L31-33 |
| `wheel_tip_radius` | float | derived | — | equation | `= 0.042 * wheel_size_scale`；root/hub/bore/width 按同比例派生 | S1 L24-29 |
| `thread_outer_radius` | float | derived | — | equation | `= 0.0102 * worm_size_scale`；thread_root/pitch/shaft_radius 同比 | S1 L33-36 |
| `center_distance` | float | derived | — | equation | `= wheel_tip_radius + thread_outer_radius + mesh_clearance` | 啮合接口 |
| `mesh_clearance` | const | 0.0012 | 0.0012 | 常量 | 螺纹外圆到齿顶正间隙；一句依据：>tessellation 误差且 <2mm 仍读作切向啮合 | S1 L37 |
| `shaft_length` | float | derived | — | inequality | `= thread_length + 0.106*worm_length_scale`，且 `≥ thread_length + 0.06`；违反则回缩 | S1 L31,33 |
| `carriage_travel` | float | [0, 0.005] | derived | conditional | 仅 sliding：prismatic [0, 0.005]，上界随 wheel_size clamp 使高背隙姿态仍不失足迹 | S6 L284-289 |
| (—) | constraint | — | — | inequality | worm 端 bearing collar 内圆 ≥ shaft_radius；worm 支座在 wheel 旋转包络外（`support_offset ≥ wheel_tip + 0.003`） | 接口 / clearance |

**连续尺寸采样契约**：先采 `wheel_size_scale` / `worm_size_scale` / `worm_length_scale`（independent，均匀）→ 派生 tip/root/hub/thread/center_distance（equation）→ `inequality` 回缩 shaft_length 与支座偏移 → `conditional` 解析 carriage_travel。全部在 `resolve_config` 求解。

### 7.5 编译预算 / compile budget（必填）

**自报预算：≤ 12s / seed**（依据：库内轻量 mesh 模板典型 5-20s；本模板只用 `LatheGeometry`(≤48 段)、`ExtrudeWithHolesGeometry`(36 齿×6 点 + bore 48 段) 与三角螺旋 ribbon(每头 ≈8 圈×24 样本)，无 cadquery 布尔）。分档 tessellation：circle/bore ≤48 段，lathe ≤48 段，thread `samples_per_turn=24`；N 头 worm 复用同一 `_helical_thread_geometry` helper 逐头生成。sweep `--compile-timeout 120`（约 10×预算，仅 watchdog）。超预算先降段数再迭代。

## Multiplicity / Copy Logic

- **M1 `worm_starts_count`（① multiplicity 轴）**
  - `count_param = worm_starts`；`N_range = {1,2,4}`（产品域即 3 个离散头数；本轴无大 N 尾部）。sampling domain：`rng.choice((1,2,4))` 等权。
  - copied object：`helical_thread_k` ribbon（k∈[0,N)，相位 `2πk/N`），共享同一 `_helical_thread_geometry` helper 与 outer radius。
  - naming：`helical_thread_{k}`；placement：绕 worm 轴等相位；joint policy：无（螺纹为 worm visual，不加关节）。
  - gating：N 不改 center_distance / 啮合足迹（outer radius 恒定），任意 N 与任意 orientation/backlash 兼容。
- **M2 wheel set-screw holes**：jointless，2 个 `set_screw_hole_i`（记录固定 2，不作独立采样轴）。
- 其余核心结构由固定 named parts（housing / worm_shaft / worm_wheel / 可选 worm_carriage）表达。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/来源 或 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 有 | housing_topology（3）改固定根壳体结构；backlash_adjustment：eccentric(2 关节) vs sliding(3 关节，+`worm_carriage` part + PRISMATIC 边)。均 forked_anchor（S1/S3/S4/S2/S6）。 |
| └ multiplicity | 同构件 ×N | 有 | worm_starts N∈{1,2,4} 螺纹 ribbon，见 §8 M1。 |
| ② 关节类型 | 图不变，边换 type/轴 | 有 | mesh_orientation 换 worm 关节轴（X↔Z）；sliding_carriage 新增 **PRISMATIC** 边（沿 mesh_dir）。两种类型都会在 sweep 出现。source-backed（S2/S5/S6）。 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | 有 | mesh_orientation：`top_mesh`（worm 水平置顶）/`vertical_shaft`（worm 竖直侧置），各标 form_subtype=Volumetric Envelope Form，已登记进 `slot_choices`。source-backed S2/S5（2 原型，样本池即 2 种取向，说明理由：观测主体形态空间只有横置/竖置两类啮合取向）。 |
| ④ 表面装饰 | 原型不变叠表面细节 | 有 | 宿主派生：wheel 端面 `set_screw_hole`/`dark_bore_depth`、worm `valley_shadow` 螺旋暗槽、housing 螺栓/法兰（split_housing bolt boss）。record_only + 少量 world_knowledge（铆钉/法兰环），均写成宿主 part visual、随 ③⑤ 共形。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | `wheel_size_scale`[0.85,1.25]、`worm_size_scale`[0.9,1.15]、`worm_length_scale`[0.85,1.25]（§7）。关节运动包络：worm CONTINUOUS（整圈）；wheel mimic 随动（整圈）；carriage PRISMATIC 轴=mesh_dir、开启方向=远离 wheel、[闭合 0, 上界 0.005]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`(max_pose_samples=48) + targeted `ctx.pose` 转 worm 一整圈验证 wheel 随动且啮合足迹保持；carriage 在 0/mid/upper 三态验证不失足迹不穿模。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | `palette_style` 5 档（金属大类：polished_steel/cast_iron/gunmetal/machined_steel/blackened_steel + 黄铜/青铜 wheel），§4 Slot E。材质大类覆盖 ≥ ceil(0.5×5)=3。 |

**收尾自检**：top_mesh vs vertical_shaft 形态明显拉开；5 档配色肉眼不同；螺纹暗槽/螺栓贴合宿主；worm 整圈旋转 + carriage 全行程不穿模。

## 采样与覆盖审计

总组合数：housing(3) × mesh_orientation(2) × worm_starts(3) × backlash(2) × palette(5) = **180**（另叠 3 个连续 scale）。

理由：4 个离散结构 slot + 1 涂装 slot 已给 180 个离散拓扑组合，远超成熟度观察需要；连续 scale 只做局部比例扰动，不承担主多样性。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 对每个 slot 独立 `rng.choice`（seed=0 不特殊），再采 3 个连续 scale，`resolve_config` 做 equation/inequality/conditional 求解与 clamp。compatibility：所有离散组合合法（啮合几何 outer-radius 恒定，N 与 orientation/backlash 正交；sliding 时 worm parent 切到 carriage）；无 gating 排除。无 regression override。random sweep：0-35 首过，corner 阶段覆盖 scale 极值 + 未实现组合；成熟度 0-999 report-only。
Topology target：180 离散组合，1000-seed 应覆盖大部分；report-only。
Controlled local parameterization：`wheel_size_scale`/`worm_size_scale`/`worm_length_scale`（§7 范围 + clamp）；`center_distance`/`shaft_length`/`support_offset` 为 equation/inequality 派生，保证不破坏 MatingContract、bearing 支承与啮合接口。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 housing→mesh→starts→backlash→palette 各独立 rng.choice + 连续 scale | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 全合法；sliding 时 worm.parent=carriage、worm 支座挂 carriage | 无浮岛、无穿模、worm 轴正确、closed pose 无重叠 |
| controlled local variation | 3 连续 scale，clamp + 派生 | 比例变化不破坏接口/clearance/支承/关节原点/身份 |
| regression overrides | none | — |
| random sweep | 0-35 首过，0-999 成熟度审计 | 契约失败；axis_realization；viewer 目检 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| housing_topology | 3 | yes | yes | |
| mesh_orientation | 2 | yes | no | ③ 观测主体形态空间仅横/竖两取向，样本池即 2，degrade 理由已写 |
| worm_starts | 3 | yes | yes | multiplicity N |
| backlash_adjustment | 2 | yes | no | ② 观测背隙调节仅偏心 vs 滑座两机构，样本池即 2，degrade 理由已写 |
| palette_style | 5 | yes | yes | ⑥ |

## Validator

- `slot_choices_for_seed` 返回已实现 module 名，与 build 一致
- `config_from_seed` 对所有 seed（含 0）用 deterministic procedural sampling
- 无非法组合（全离散组合合法）
- 无小型 curated/modulo 主 seed 表
- 连续 scale 全部 clamp/派生，不破坏接口/clearance/关节原点/multiplicity
- equation/inequality/conditional 在 `resolve_config` 求解
- wheel 关节声明 `MatingContract`（wheel_bearing_collar ⟷ axle_thrust_collar）；worm/carriage 关节按 Rule 2 grandfather（pin-in-sleeve / prismatic gauge）
- 两个非 FIXED 旋转关节存在且 worm 轴 ⟂ wheel 轴
- worm CONTINUOUS + wheel CONTINUOUS(mimic -1/teeth)；sliding 另加 PRISMATIC
- Rule 5：`fail_if_parts_overlap_in_sampled_poses` + targeted `ctx.pose` 转 worm 验证啮合足迹保持

## Reject cases

- worm/wheel 轴不垂直，或退化成平行轴 spur 齿轮对
- worm 用光 Cylinder 顶替螺旋螺纹（下调 primitive，违 Rule 3）
- 螺纹与齿在 closed / 旋转姿态穿模（center_distance 求解错误）
- 缺 mimic 或缺一个旋转关节（沦为摆件）
- housing 壳壁伸入旋转包络导致穿模
- worm 端 shaft 悬空未入 bearing collar（浮岛 / 未支承）
- sliding carriage 与 housing 断连或全行程失去啮合足迹
- N 头 worm ribbon 相互穿模或未共享 outer radius

## 与相邻类别的边界

- **spur gear pair**（平行轴正齿轮对）：两轴平行同平面，无螺旋 worm；本类别轴必须垂直、必须螺旋螺纹啮合。
- **decorative gear display**（齿轮摆件）：无真实关节；本类别必须 ≥2 真实旋转关节 + wheel mimic 联动。

## 模板实现备注（可选）

- housing / worm / wheel 共享 `_helical_thread_geometry`、`_toothed_wheel_profile`、`_circle_profile`（源自 S1）。
- 关键单源量（Contract 3c）：`center_distance`、`worm_center`、`mesh_dir`、`support_offset` 均在 `resolve_config`/module-level helper 一处定义。
- captured-pin：worm shaft 入 bearing collar、carriage 入 rail → element-scoped `allow_overlap`。
- wheel MatingContract 为唯一 mating；worm/carriage grandfather。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/C/wheel | open_pillow_block / worm 螺纹 / wheel 齿 | `rec_...__001_png_c097f6455b834d47b95478b26e163c36` | L24-L324 | 轻量 mesh helper + 两轴啮合拓扑 + open 支座 |
| S2 | A/B/D/wheel | carrier / top_mesh / eccentric / keyed hub | `rec_...__002_png_d1bae7f8a0f645068588a092bf260924` | L87-L365 | carrier 布局 + bearing collars + thrust collar |
| S3 | A | enclosed_gearbox | `rec_0611_..._housing_topology_enclosed_gearbox` | L145-L205 | 箱壳 + service aperture |
| S4 | A | split_housing | `rec_0611_..._housing_topology_adjustable_split_hous` | L145-L260 | 上下对分 + bolt boss |
| S5 | B | vertical_shaft | `rec_0611_..._mesh_orientation_vertical_shaft_worm` | L37-L322 | 竖轴 worm 放置 + 轴 Z |
| S6 | D | sliding_carriage | `rec_0611_..._backlash_adjustment_sliding_worm_carri` | L200-L301 | prismatic worm carriage |
| S7 | C | 1/2/4_start_worm | `rec_0611_..._worm_starts_{1,2,4}_start_worm` | L204-L235 | 多头螺纹 ribbon |

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 模板已实现并对齐 spec，sweep-pipeline `verdict=pass`、`pass_rate=1.0`（0-35 + corner 全清，无 escalation，~1s/seed）。axis_realization 全 slot 实现：housing 3/mesh 2/starts 3/backlash 2/palette 5。排除项：`wheel_bearing_eccentric_ring`（与旋转 wheel thrust collar 同轴穿模）已移出——② eccentric vs sliding 区别由关节拓扑（2 vs 3 关节 + PRISMATIC）承载，非装饰环。worm/carriage 旋转关节按 Rule 2 grandfather，wheel 关节用 MatingContract。 |
</content>
</invoke>
