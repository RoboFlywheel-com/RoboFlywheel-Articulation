# Modular Spec — `bicycle` (Sports / Bike)

## 元信息
| 项 | 值 |
|---|---|
| slug | `bicycle` |
| template path | `agent/templates/Sports_Bike.py` |
| test path (optional) | `tests/agent/test_bicycle_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children: frame root with fork / front_wheel / rear_wheel / crank children; + multiplicity: spoke ring per wheel) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this subcat (parent + 9 forked variants) |
| source_index_policy | only adopted module sources are indexed below |

read 列表（全部精读 model.py）：
- S_parent = `rec_orange-hardtail-mountain-bike-with-a-front-suspe_20260605_165808_319413_f497242f` (diamond frame + suspension_fork + flat_bar + spokes28)
- S_step = `rec_bicycle_var_stepthrough`
- S_bmx = `rec_bicycle_var_bmx`
- S_cruiser = `rec_bicycle_var_cruiser`
- S_rigid = `rec_bicycle_var_rigidfork`
- S_dual = `rec_bicycle_var_dualcrown`
- S_riser = `rec_bicycle_var_riserbar`
- S_drop = `rec_bicycle_var_dropbar`
- S_sp18 = `rec_bicycle_var_spokes18`
- S_sp36 = `rec_bicycle_var_spokes36`

## 核心身份

一辆完整、可骑乘的两轮人力自行车：一个三角主车架（frame，root）承载前叉（fork）、前轮、后轮、曲柄（crank）四个子件，前后轮共面同径（直径 ~0.70 m，落地于 z=0），轴心在 z=WHEEL_R，后轴在车体后部、前轴在车体前部（轴距 ~1.05 m）。底部牙盘壳（bottom-bracket shell）位于车架前下方，曲柄绕其轴自旋；头管（head tube）以一条 XZ 平面内倾斜的转向轴贯穿，前叉+车把+前轮整组绕该轴转向。

每个 5★ 样本都**必须保留的核心运动学**（不参与 slot 变化）：
- `steering`：REVOLUTE，frame→fork，绕倾斜头管轴，range ≈ ±0.70 rad。
- `front_wheel_roll`：CONTINUOUS，fork→front_wheel，绕前轴 Y。
- `rear_wheel_roll`：CONTINUOUS，frame→rear_wheel，绕后轴 Y。
- `crank_spin`：CONTINUOUS，frame→crank，绕牙盘 Y。
Part tree：frame(root) → fork(steered) → front_wheel；frame → rear_wheel；frame → crank。

成熟域 = 真实可骑成人/青年自行车（MTB / step-through 通勤 / BMX / beach-cruiser / 公路），均为人力、链传动、辐条轮。不混入电机、外挂电池、踏板车/滑板车（无曲柄链传动）、摩托车、三轮/独轮、儿童带辅助轮等。

## 槽位 + 候选模块表

### Slot A：frame_geometry（车架主三角形态，root part）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| diamond | S_parent | L143-L203 | eligible if compatible | 经典直管前三角：水平上 tube (top_tube)、down_tube、近竖直 seat_tube、head_tube + 后三角 chainstay_{l,r}/seatstay_{l,r} + bb_shell |
| step_through | S_step | L148-L193 | eligible if compatible | 开放低跨：**无高横梁**，单根深弯 step_through_tube 从头管区一路下扫到 BB/seat-tube 接合处 (最低 z~0.38)，无 top_tube；其余 down/seat/head + 后三角不变 |
| bmx_compact | S_bmx | L142-L175 | eligible if compatible | 紧凑陡前三角：近水平短 top_tube 贴近座管、短直 seat_tube、**很短的 chainstay (~0.40)**、低鞍座，整体紧凑 |
| cruiser_cantilever | S_cruiser | L148-L213 | eligible if compatible | 双曲悬臂沙滩车：S 形 top_tube（先拱起再下扫）、深度后掠的弯 seat_tube、加长后三角，松弛低身姿长轮廓 |

### Slot B：fork_front_end（前叉，steered fork part）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| suspension_fork | S_parent | L230-L259 | eligible if compatible | 单冠伸缩前叉：steerer + 单 fork_crown(Box) + 每侧上段 fork_stanchion_{l,r}(银) + 下段 fork_lower_{l,r}(黑) 到轮轴 |
| rigid_fork | S_rigid | L230-L251 | eligible if compatible | 刚性叉：steerer + 单 fork_crown + 每侧**一根连续弯曲 fork_blade_{l,r}**（冠→前掠→dropout），无伸缩段/密封，slim 单片 |
| dual_crown | S_dual | L230-L296 | eligible if compatible | 三夹（双冠）DH 叉：steerer + lower_crown + upper_crown 两块夹板分两高度夹粗长行程腿 fork_stanchion_{l,r}(粗银) + fork_lower_{l,r}(更粗黑) + fork_arch 桥 |

### Slot C：handlebar_form（车把形态，挂在 fork 的 stem 上）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_bar | S_parent | L262-L285 | eligible if compatible | 近直平把：stem(Box) + 横跨 ±Y 略带后掠的 handlebar tube + grip_{l,r}，把端 ~z1.04 平视 |
| riser_bar | S_riser | L261-L296 | eligible if compatible | 上扬把：从中央 stem 夹处向上爬升再后掠外扫到高位 grips（把端 ~z1.26，高于 stem ~0.21 m），直立身姿 |
| drop_bar | S_drop | L262-L313 | eligible if compatible | 公路弯把：连续 drop_bar（tops→hoods 前伸→深下钩到 lower drops），加 brake_hood_{l,r} + bar_tape_{l,r}(缠带握位)；把端在下钩 (~z0.91) |

每个 slot 各有 ≥3 个结构性不同 candidate，无需降级。

## 槽位图（slot graph）

pattern: mixed（parallel_children 装配 + 每轮 spoke 多重复制）

```
frame (root, Slot A)
  ├─[REVOLUTE steering, axis=tilted head-tube (XZ), origin=HEAD_BOT, range ±0.70]→ fork (Slot B)
  │     └─ stem 接口面 → handlebar (Slot C, 固连于 fork 的 stem 顶)
  │     └─[CONTINUOUS front_wheel_roll, axis=Y, origin=FRONT_AXLE−HEAD_BOT]→ front_wheel (+spoke 多重复制)
  ├─[CONTINUOUS rear_wheel_roll, axis=Y, origin=REAR_AXLE]→ rear_wheel (+spoke 多重复制)
  └─[CONTINUOUS crank_spin, axis=Y, origin=BB]→ crank
```

接口点位：
- **frame ↔ fork**：mating = 头管底 HEAD_BOT 上的转向轴（`_steer_axis()` = 归一化 HEAD_TOP−HEAD_BOT，在 XZ 平面内）；REVOLUTE。fork 几何在绝对坐标作出后整体平移 −HEAD_BOT（child link frame 落在 joint origin）。fork_crown 必须坐贴 head_tube（`expect_contact fork_crown↔head_tube`），steerer 穿过 head_tube（allow_overlap）。
- **fork ↔ handlebar**：固连（同属 fork part 的 visual）。stem(Box) 夹住 steerer 顶 (~z1.045)，handlebar tube 的中央点固连在 stem 上方。handlebar 是 fork 的内部 visual，无独立 joint。
- **fork ↔ front_wheel**：dropout 接口 = 前叉下端抓前轮 hub 轴；CONTINUOUS 绕 Y；joint origin = FRONT_AXLE 在 fork 系下 (FRONT_AXLE−HEAD_BOT)。`expect_contact fork_lower/blade ↔ front_hub`。
- **frame ↔ rear_wheel**：后 dropout 接口 = chainstay/seatstay 末端抓后轮 hub；CONTINUOUS 绕 Y；origin=REAR_AXLE。
- **frame ↔ crank**：牙盘壳 bb_shell 轴；CONTINUOUS 绕 Y；origin=BB；spindle 穿 bb_shell（expect_contact + allow_overlap spindle↔{bb_shell,down_tube,seat_tube,chainstay_*}）。

互斥/派生：四个子件都是 frame 的并联 child（fork 再串前轮），无可选 child；handlebar 由 Slot B 的 fork 派生承载面（stem 几何由 fork 模块提供，不随 Slot C 变）。

## 每槽位 Module Emits / Interfaces

### Slot A / module frame_geometry（以 diamond 为基线，其余同构替换主管）
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame(root) 全部 visual：top_tube/step_through_tube、down_tube、seat_tube、head_tube、chainstay_{l,r}、seatstay_{l,r}、bb_shell、seatpost、saddle、saddle_nose、rear_caliper | S_parent L143-L203 |
| internal joints | 无（车架是单刚体 root） | — |
| upstream interface | root，无父；提供整车基准系 (+X 前 / +Z 上 / +Y 左) | S_parent L117-L131 |
| downstream interface | HEAD_BOT/HEAD_TOP 转向轴（给 fork）、REAR_AXLE（给 rear_wheel）、BB+bb_shell（给 crank）、后 dropout（chainstay/seatstay 端抓 rear_hub） | S_parent L38-L46,L155-L178 |

### Slot B / module fork_front_end（以 suspension_fork 为基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | fork part：steerer、fork_crown(/lower_crown+upper_crown)、fork_stanchion_{l,r} 或 fork_blade_{l,r}、fork_lower_{l,r}(susp/dual)、(dual: fork_arch)、front_caliper、stem | S_parent L230-L263 |
| internal joints | 无（前叉整组随 steering 一起转，stem/把固连） | — |
| upstream interface | fork_crown 坐贴 head_tube；steerer 穿 head_tube；几何整体 −HEAD_BOT | S_parent L213-L234 |
| downstream interface | fork_lower/blade 下端 dropout 抓 front_hub（CONTINUOUS 前轮）；stem 顶面承载 handlebar | S_parent L245-L263 |

### Slot C / module handlebar_form（以 flat_bar 为基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | handlebar/riser_bar/drop_bar tube + grip_{l,r}（drop 另加 brake_hood_{l,r}、bar_tape_{l,r}） | S_parent L266-L285 / S_drop L266-L313 |
| internal joints | 无（车把固连于 fork 的 stem） | — |
| upstream interface | 中央点固连在 fork 的 stem 顶 (~z1.045) | S_parent L262-L264 |
| downstream interface | grips = 骑手握点（终端 visual，无下游 joint） | S_parent L278-L285 |

### 多重复制 / module wheel_spokes（front & rear 共用 `_wheel_geometry` helper）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 每轮：{prefix}_tire、{prefix}_rim、{prefix}_hub、{prefix}_spoke_{i}×N、{prefix}_rotor、{prefix}_marker（rear 另加 rear_cassette） | S_parent L59-L114 |
| internal joints | 无（辐条是轮 part 的 visual，随该轮单一 CONTINUOUS roll 一起转） | S_parent L85-L98 |
| upstream interface | 轮 part 局部系，轴沿 Y；front 由 fork 承载、rear 由 frame 承载 | S_parent L294-L313 |
| downstream interface | 无（轮为叶端 part） | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| frame_geometry | enum | diamond / step_through / bmx_compact / cruiser_cantilever | — | choice | deterministic procedural sampler 选择 | Slot A 表 |
| fork_front_end | enum | suspension_fork / rigid_fork / dual_crown | — | choice | sampler 选择；与 C 有兼容门控（见下） | Slot B 表 |
| handlebar_form | enum | flat_bar / riser_bar / drop_bar | — | choice | sampler 选择 | Slot C 表 |
| n_spokes | int | [12, 48]（测试小样 {18,28,36}） | 28 | conditional | 同一 N 同时用于前后轮；下界 ≥12 保证轮面连通可见，上界 ≤48 真实带 | S_parent L82 / S_sp18,S_sp36 L82 |
| palette_style | enum | trail_orange / matte_stealth_black / chrome_silver_classic / racing_red / forest_green_cruiser / sky_blue_commuter | trail_orange | choice | 仅改 frame/accent 材质 rgba，不改几何/接口 | 见 palette 说明 |
| wheel_r | float | [0.30, 0.37] | 0.35 | independent | 前后轮共用同一 wheel_r（保证同径检查 |fw−rw|<0.02）；轴心 z=wheel_r | S_parent L35 |
| wheelbase_scale | float | [0.92, 1.08] | 1.0 | independent | 缩放 REAR↔FRONT 轴 x 距；保持 0.95≤Δx≤1.15 检查 | S_parent L37,L468-474 |
| head_tube_angle_scale | float | [0.95, 1.05] | 1.0 | equation | `HEAD_TOP/HEAD_BOT` x 派生使转向轴随之倾斜；fork rake 跟随，保持冠贴头管 | S_parent L45-L46,L52-56 |
| seat_height_scale | float | [0.92, 1.10] | 1.0 | conditional | seatpost+saddle 抬降；bmx_compact 下限收紧（低鞍座身份），与 top_tube 顶不穿 | S_parent L181-L193 / S_bmx |
| fork_leg_r_scale | float | [0.9, 1.3] | 1.0 | conditional | 腿/blade 半径；dual_crown 下限抬高（粗腿身份），rigid_fork 上限收（slim 身份） | S_dual L266-267 / S_rigid L249 |
| (—) | constraint | — | — | inequality | 叉腿/前轮间隙：`|leg_y| − leg_r ≥ TIRE_T + clearance`（腿在轮胎半宽外）；违反则回缩 leg_y 或减 leg_r | S_parent L237 |
| (—) | constraint | — | — | inequality | 链撑外撇间隙：rear stay 末端 `|y| ≥ TIRE_T + stay_r`（清后胎）；bmx 短链撑时尤需 | S_bmx L155-172 |
| (—) | constraint | — | — | inequality | crank pedal 摆动半径 ≤ chainstay/down_tube 净距（自旋不撞车架），pedal 偏轴量保持可检测 spin marker | S_parent L331-354 |

**palette_style 说明（≥3，取 6）**：所有 5★ 样本几何相同、车架统一 frame_orange，故 palette 为"按 seed 采样的真实涂装"层，取材自样本观察到的材质集（frame_orange `0.95,0.46,0.10`；component_black `0.12,0.13,0.14`；silver `0.74,0.76,0.79`；rim_silver；accent_red `0.80,0.12,0.10`；tire_black；drop 的 bar_tape `0.10,0.10,0.11`）并扩到真实自行车常见配色：
- `trail_orange`（橙车架 + 黑组件 + 银叉/轮 + 红点缀，= 父样基线）
- `matte_stealth_black`（哑光全黑车架 + 黑组件 + 暗银轮）
- `chrome_silver_classic`（亮银/铬车架 + 黑胎 + 银轮，复古钢架）
- `racing_red`（红车架 + 黑组件 + 银轮，公路竞速）
- `forest_green_cruiser`（深绿车架 + 棕/黑握把 + 银轮，沙滩车气质）
- `sky_blue_commuter`（天蓝车架 + 黑组件 + 银轮，通勤）
palette 只改材质 rgba，绝不改几何 / 接口 / multiplicity。

## Multiplicity / Copy Logic

**单轴 multiplicity：n_spokes（每轮辐条环）**
- `count_param`：`n_spokes`（同一 N 经共享 `_wheel_geometry(prefix=...)` 同时套用前、后两轮）。
- `N_range`：产品域 `[12, 48]`（真实自行车 16–48 辐条）；测试小样集 `{18, 28, 36}`（= S_sp18 / S_parent / S_sp36 已覆盖），sweep 可遍历全带。
- sampling domain：加权——常见档 24/28/32/36 高频，极少/极多（12,14,44,48）稀有尾部；小 N 偏多以压低 mesh 成本，但不退化到不可见连通。
- copied object：一根细直辐条 (`CylinderGeometry(0.0022, length)`)，从 hub flange (r≈0.030) 径向伸到 rim 内侧 (r = WHEEL_R − 2·TIRE_T)。
- naming：`f"{prefix}_spoke_{i}"`，prefix ∈ {front, rear}。
- placement：等角 `a = 2πi/n_spokes + 0.18`（常量偏移，使无辐条落在坐标轴上），绕 Y 旋到径向方向后平移到径向中点。
- joint policy：辐条是所属轮 part 的**非关节 visual**，随该轮唯一 CONTINUOUS roll 转；无 per-spoke joint。
- source/gating：S_parent L82-L98；前后轮**不是** multiplicity loop（它们是父级不同的两个独立 part：fork vs frame），只有"每轮内的辐条数"是复制轴。

## 拓扑多样性审计

总组合数：A(4) × B(3) × C(3) = 36 种 slot 拓扑；× n_spokes 采样档（产品域 [12,48] 取约 12 个加权档）→ 数百级别的可区分种子。

理由：单 slot 组合即 36 distinct（远超 10）；叠加 n_spokes 与 palette 后远超门槛。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 先按加权选 frame_geometry / fork_front_end / handlebar_form 三个 enum，再加权采 n_spokes、采 palette_style，最后采连续 scale（先 independent: wheel_r/wheelbase_scale → 派生 equation: head_tube_angle_scale 联动叉 rake → 投影 inequality: 叉腿-轮间隙 / 链撑-胎间隙 / pedal-车架净距 → 解析 conditional: seat_height/fork_leg_r 随 frame/fork enum 收边界）。compatibility matrix 通过 gating 排除少数几何上别扭的跨 slot 组合（见下）。`slot_choices_for_seed` 必须与 build 选择一致。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类 36 slot 拓扑 × 多 n_spokes 档可达到（若仅看 slot 拓扑则 36，需把 n_spokes/palette 计入才上百，符合"主多样性来自 slot/module/multiplicity"）。
若使用 regression overrides：默认无；仅在 sweep 发现具体失败 seed（如某 frame×fork 间隙临界）时加 sparse override，并注明 seed 与失败回归原因。
Controlled local parameterization：wheel_r、wheelbase_scale、head_tube_angle_scale(equation)、seat_height_scale(conditional)、fork_leg_r_scale(conditional)，范围与 clamp 见第 7 节；均在 `resolve_config` 内求解，遵循 independent→equation→inequality→conditional 契约，不破坏转向轴接口、dropout 接触、crank 自旋间隙、轮同径检查与辐条 multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 三 enum 加权 → n_spokes 加权 → palette → 连续 scale；`slot_choices_for_seed` 与 build 一致 | slot_choices_for_seed matches build choices |
| compatibility matrix | drop_bar(C) × dual_crown(B) = 现实中怪异（公路弯把配 DH 双冠叉），**gated 排除**，sampler 不产出该组合；其余 4×3×3−（drop×dual 的 4 个 frame）= 32 legal slot 拓扑 | no floating, no collision, steer axis ok, dropout contact, crank spin clear |
| controlled local variation | 上列连续 scale + clamp；保持前后同径、冠贴头管、叉腿在胎外 | proportions vary without breaking interfaces / clearance / joint origin / identity |
| regression overrides | none（除非 sweep 暴露具体失败 seed） | previously failed or reviewer-selected cases only |
| random sweep | seeds 0–49 初轮，0–999 成熟审计 | 与 contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A frame_geometry | 4 | yes | yes | |
| B fork_front_end | 3 | yes | yes | |
| C handlebar_form | 3 | yes | yes | drop×dual gated |

## Validator

- slot_choices_for_seed returns implemented module names（frame/fork/handlebar enum 值真实存在）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating 阻止 drop_bar×dual_crown 等非法组合
- optional regression overrides 稀疏且有据
- 不靠小型 curated/modulo 表当主 seed domain
- 连续 scale 全部 clamp，且不破坏转向轴 / dropout 接触 / crank 自旋间隙 / 前后同径 / 辐条复制
- 跨部件 scale 依赖（equation/inequality/conditional）在 `resolve_config` 内求解
- 关键 InterfaceSpec/MatingContract 存在：fork_crown↔head_tube 接触、steerer↔head_tube 过盈、spindle↔bb_shell 接触+过盈、前后 dropout↔hub 接触
- 关键 joint 类型/轴/range 正确：steering REVOLUTE ±0.70 倾斜轴；front/rear roll CONTINUOUS Y；crank_spin CONTINUOUS Y
- 复制对象遵循命名/布局：`{prefix}_spoke_{i}`，等角 + 0.18 偏移，径向跨 hub→rim
- 同径检查：front/rear 轮直径差 < 0.02；前轮直径 0.66–0.74
- 前轮在前、后轮在后：0.95 ≤ Δx ≤ 1.15
- 各运动副可检测位移：转向 yaw 使前轮 Y 展宽 +>0.05；前/后轮 marker 摆 >0.20；pedal 摆 >0.08

## Reject cases

- 没有 4 条核心运动副之一（缺 steering / 任一 wheel roll / crank spin），或把它们做成 fixed。
- 前后轮直径不一致（|Δ|≥0.02），或轮不落地 / 轴心不在 z=wheel_r。
- fork_crown 悬空不贴 head_tube，或 steerer 不与 head_tube 同轴（转向轴失配）。
- 叉腿/链撑穿前/后胎（违反 `|y|−leg_r ≥ TIRE_T+clearance` 间隙不等式）。
- crank pedal 自旋时撞车架（pedal 摆半径超净距），或 pedal 完全在轴上（spin 不可检测）。
- 把 step_through 仍画出高 top_tube（破坏开放低跨身份），或 cruiser 画成直管 / bmx 画成长链撑（身份漂移）。
- 采样产出被 gated 的 drop_bar×dual_crown 组合。
- 把前后两轮当 multiplicity loop 复制（它们是父级不同的独立 part），或辐条做成 per-spoke joint。
- 出现电机/外挂电池/踏板车/三轮等越域结构。

## 与相邻类别的边界

- 不该混入：电动自行车 / 电摩（会引入电池盒 + 轮毂电机，本类是纯人力链传动，无电气子件）。
- 不该混入：踏板车 / 滑板车（无曲柄牙盘链传动，站立平台 + 小轮，与 crank_spin + 大辐条轮身份冲突）。
- 不该混入：摩托车（发动机缸体 / 油箱 / 排气，重型，非人力）。
- 不该混入：独轮车 / 三轮车 / 带辅助轮童车（轮数与 frame 三角拓扑、前后双轮装配不符）。
- 不该混入：Crankset/Fork-and-handlebar/Dropper-seatpost 等**单组件**子总成（data/records 里同名 `rec_bicycle_*_assembly_*` 是零部件资产，非整车；本模板产出完整整车）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S_parent | A/B/C/mult | diamond / suspension_fork / flat_bar / spokes28 | rec_orange-hardtail-...f497242f | A L143-203, B L230-259, C L262-285, spoke L59-114 | 整车基线 + 所有接口/运动副 |
| S_step | A | step_through | rec_bicycle_var_stepthrough | L148-193 | 开放低跨车架 |
| S_bmx | A | bmx_compact | rec_bicycle_var_bmx | L142-175 | 紧凑短链撑车架 |
| S_cruiser | A | cruiser_cantilever | rec_bicycle_var_cruiser | L148-213 | 双曲悬臂车架 |
| S_rigid | B | rigid_fork | rec_bicycle_var_rigidfork | L230-251 | 刚性单片叉 |
| S_dual | B | dual_crown | rec_bicycle_var_dualcrown | L230-296 | 双冠 DH 叉 + arch |
| S_riser | C | riser_bar | rec_bicycle_var_riserbar | L261-296 | 上扬把 |
| S_drop | C | drop_bar | rec_bicycle_var_dropbar | L262-313 | 公路弯把 + hood + tape |
| S_sp18 | mult | spokes(N=18) | rec_bicycle_var_spokes18 | L82 | n_spokes copy logic 小样 |
| S_sp36 | mult | spokes(N=36) | rec_bicycle_var_spokes36 | L82 | n_spokes copy logic 小样 |

## 模板实现备注（可选）
- front/rear 两轮共享 `_wheel_geometry(prefix)` helper，n_spokes 单参套两轮。
- fork 几何按 S_parent 约定在绝对坐标作出后整体 −HEAD_BOT，再用 `_steer_axis()` 定 REVOLUTE 轴；head_tube_angle_scale 改 HEAD_TOP/HEAD_BOT 时务必让 fork rake 与冠贴合一起重算（equation 联动）。
- captured-pin / 过盈 allow_overlap 需 element-scoped 复刻：steerer↔head_tube、spindle↔{bb_shell,down_tube,seat_tube,chainstay_*}、冠↔head_tube、前后 dropout↔hub（参 S_parent run_tests L527-575）。
- bmx_compact 的 seat_height 下限、dual_crown 的 fork_leg_r 下限、rigid_fork 的上限是 conditional，依上游 enum 解析后再 clamp。
- drop_bar×dual_crown 暂不进入 seed domain（compatibility gate）。
