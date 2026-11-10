# Modular Spec — Sports / Skateboard

## 元信息
| 项 | 值 |
|---|---|
| slug | `skateboard` |
| template path | `agent/templates/Sports_Skateboard.py` |
| test path (optional) | `tests/agent/test_skateboard_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children + multiplicity) |

`pattern` 说明：root = `deck`。两个 truck 子树 (`front` / `rear`) 作为 parallel children 挂在 deck 底面两个 FIXED 锚点上；每个 truck 内部是一条短 linear_chain (`baseplate` —REVOLUTE→ `hanger` —CONTINUOUS×2→ `wheel`)。叠加一根 multiplicity 轴 `bolt_count`（每个 truck 的 deck-top 安装螺栓数），bolts 内联为 deck visual（无 joint）。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (parent + 9 named fork variants) |
| source_index_policy | only adopted module sources are indexed below |

阅读清单（全部读完 `model.py`）：
- S0 parent `rec_wooden-skateboard-...b6b31add` — Slot A=popsicle / Slot B=cast_kingpin / Slot C=street_hard / bolts N=4 基线
- S1 `rec_skateboard_var_oldschool` (Slot A)
- S2 `rec_skateboard_var_longboard` (Slot A)
- S3 `rec_skateboard_var_penny` (Slot A)
- S4 `rec_skateboard_var_inverted_truck` (Slot B)
- S5 `rec_skateboard_var_wide_truck` (Slot B)
- S6 `rec_skateboard_var_cruiser_wheels` (Slot C — 仅尺度/材质，见 note)
- S7 `rec_skateboard_var_cored_wheels` (Slot C — 结构不同)
- S8 `rec_skateboard_var_bolts2` (multiplicity N=2)
- S9 `rec_skateboard_var_bolts6` (multiplicity N=6)

## 核心身份

Skateboard = 一块沿 X 拉长的木/塑甲板（deck，root，~0.55–1.10 m），底面前后各 FIXED 锚一只 metal truck；每个 truck = baseplate（FIXED 于 deck）+ hanger（绕倾斜 kingpin 轴 REVOLUTE lean/steer ±15°）+ 横置 cross-axle 上两只 wheel（各绕 Y 轴 CONTINUOUS roll）。总计固定 4 轮，四轮底面共面落地（板悬在轮上，轮是最低件）。活动语义铁律：2 个 REVOLUTE kingpin lean + 4 个 CONTINUOUS wheel roll，恒成立。成熟域覆盖 popsicle 双翘板、old-school 单翘 cruiser、pintail longboard、penny mini-cruiser；truck 含 SKP（standard kingpin）/ RKP（reverse-kingpin longboard）/ gullwing-wide cruiser；wheel 含实心街轮 / 大软 cruiser 轮 / cored longboard 轮。

不该混入：见「与相邻类别的边界」。

## 槽位 + 候选模块表

### Slot A：deck outline（`_deck_mesh` LoftGeometry 拉板）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| popsicle (parent) | rec_wooden-...b6b31add | L62-L99 | eligible if compatible | 对称双翘 popsicle；长椭圆，鼻/尾都圆且上翘 (raw[] 对称, 端 kick=0.030)；DECK_LEN 0.80 |
| oldschool | rec_skateboard_var_oldschool | L65-L111 | eligible if compatible | 宽平 cruiser；方头尖鼻 (nose kick=0)，单宽尾翘 (tail kick=0.048)，尾部更宽 (flared rails，y>0.22)，缓 concave；DECK_LEN 0.80 |
| longboard | rec_skateboard_var_longboard | L64-L107 | eligible if compatible | 长 drop pintail；DECK_LEN 1.10，宽圆鼻 + 尖 pintail 尾，全平无翘 (z-extent≈DECK_THICK)；FRONT_X/REAR_X 外移到 ±0.39 |
| penny | rec_skateboard_var_penny | L63-L105 | eligible if compatible | 短 molded mini board；DECK_LEN 0.55，圆角 pill 轮廓，仅尾翘 (tail kick=0.028, nose kick=0)；FRONT_X/REAR_X 内收到 ±0.19；deck 略厚 0.015 |

四个 candidate 结构差异在 `_deck_mesh` 的 station 列表 (`raw[]`) + `DECK_LEN`/`FRONT_X`/`REAR_X`/`DECK_THICK` 常量，候选数 = 4。

### Slot B：truck / hanger form（`_baseplate_mesh` + `_hanger_mesh`，kingpin REVOLUTE）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| cast_kingpin / SKP (parent) | rec_wooden-...b6b31add | baseplate L128-L136 · hanger L139-L154 · kingpin emit L216-L234 | eligible if compatible | 标准 cast street truck；plate 0.075²，boss 居中下伸，hanger 矮身 (0.030) + neck + 直臂；kp_axis=(tilt_sign·sinTILT,0,cosTILT) 向内倾；joint origin (0,0,AXLE_Z=-0.040)；WHEEL_Y=0.092 |
| inverted_truck / RKP | rec_skateboard_var_inverted_truck | const L66-L70 · baseplate L139-L147 · hanger L150-L173 · kingpin emit L220-L258 | eligible if compatible | reverse-kingpin longboard truck；boss/neck 移到 outboard 侧 (outboard_x=±BOSS_OFFSET_X)，joint origin (outboard_x,0,JOINT_Z)，kp_axis 反号 (`-tilt_sign·sinTILT` → 向外倾)，hanger 更高 (body_h 0.050)，axle 用 AXLE_LOCAL_Z=AXLE_Z-JOINT_Z；WHEEL_Y=0.092 |
| wide_truck / gullwing | rec_skateboard_var_wide_truck | baseplate L128-L143 · hanger L146-L190(approx, 至 `return`) · kingpin emit ~L233-L260 | eligible if compatible | 宽 gullwing/cruiser truck；plate 0.090×0.088 + 4 径向加强筋 + 高 boss(0.028)，hanger 宽身 + 翼臂 (wing) + 外露 bushing seat/crown，axle 更长；WHEEL_Y 加宽到 0.120（轮距更宽）；joint 名/轴语义同 parent |

候选数 = 3（≥3 满足）。三者结构差异：boss 位置 (center vs outboard)、kp_axis 倾向 (inward vs outward)、hanger 高度/翼形/bushing crown、WHEEL_Y 轮距。

### Slot C：wheel form（`_wheel_mesh`/`_tire_mesh` 或 cored 双 visual，CONTINUOUS roll）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| street_hard (parent) | rec_wooden-...b6b31add | wheel L102-L113 · tire L116-L125 · wheel-part emit L237-L260 | eligible if compatible | 小硬窄街轮；WheelGeometry+TireGeometry，WHEEL_RADIUS 0.0275 / WIDTH 0.034，rim+hub+circumferential tread×2；单 wheel_rim + wheel_tire visual |
| cruiser_wheels | rec_skateboard_var_cruiser_wheels | wheel L107-L123 · tire L126-L139 · const L57/L60-L61 | eligible if compatible (degraded, see note) | 大软 cruiser 轮；WHEEL_RADIUS 0.035 / WIDTH 0.050，宽 hub(0.014/0.044)，TireCarcass+TireShoulder 鼓 sidewall (bulge 0.08–0.10)；AXLE_Z 降到 -0.045 保持共面；同 part 结构（仍 rim+tire 两 visual） |
| cored_wheels | rec_skateboard_var_cored_wheels | spoke helper L103-L112 · hub_core L115-L141 · urethane_ring L144-L165 · wheel-part emit L278-L301 | eligible if compatible | cored longboard 轮：硬 inner hub core（NUM_SPOKES=5 经 `for i in range` 等角辐条 + bearing seat）+ 软 outer urethane LatheGeometry 环；两 visual = `hub_core` + `urethane_ring`（材质双色），结构与单实心轮根本不同 |

候选数 = 3。注：`cruiser_wheels` 相对 `street_hard` 主要是尺度 + 材质 + tire carcass 参数差异（part 拓扑同：rim+tire 两 visual），按 SPEC_TEMPLATE「只换尺寸/材质不算新 candidate」严格判它接近降级。保留为 candidate 的理由：它额外引入 `TireCarcass`/`TireShoulder` 子结构与 `AXLE_Z` 重算（落地共面约束的耦合），且是 1000-seed sweep 覆盖软轮成熟域所需；真正的拓扑分叉由 `cored_wheels`（双 part visual + spoke 循环）提供。若 reviewer 认为不足以算第三 candidate，可降级为 Slot C 的连续 `wheel_size_class` scale（hard/soft）+ `cored_wheels` 两态 enum，使 Slot C 退为 2 candidate；当前先按 3 candidate 记录并标注。

## 槽位图（slot graph）

pattern: mixed (parallel_children + per-truck linear_chain + multiplicity)

```
deck (root, Slot A)
 ├─[FIXED @ (FRONT_X,0,DECK_BOTTOM)]──> front_baseplate (Slot B)
 │     └─[REVOLUTE kp_axis(tilt) @ (0/outboard_x,0,AXLE_Z/JOINT_Z), ±15°]──> front_hanger (Slot B)
 │            ├─[CONTINUOUS axis=Y @ (0,-WHEEL_Y,0/AXLE_LOCAL_Z)]──> front_wheel_0 (Slot C)
 │            └─[CONTINUOUS axis=Y @ (0,+WHEEL_Y,0/AXLE_LOCAL_Z)]──> front_wheel_1 (Slot C)
 ├─[FIXED @ (REAR_X,0,DECK_BOTTOM)]───> rear_baseplate (Slot B)
 │     └─[REVOLUTE kp_axis(-tilt) @ ...]──> rear_hanger (Slot B)
 │            ├─[CONTINUOUS axis=Y]──> rear_wheel_0 (Slot C)
 │            └─[CONTINUOUS axis=Y]──> rear_wheel_1 (Slot C)
 └─ deck_bolt_{label}_{i}  (Slot A 内联 visual ×(bolt_count×2 trucks), 无 joint)
```

接口点位与 joint：
- deck → baseplate：mating face = deck 底面 (z=DECK_BOTTOM=0)；锚点 (FRONT_X/REAR_X,0,0)；FIXED support，名 `deck_to_{label}_baseplate`。前后锚关于 deck center X-对称 (`abs(front_x+rear_x)<0.01`)。
- baseplate → hanger：pivot = 倾斜 kingpin 轴。SKP/wide：origin (0,0,AXLE_Z)，axis (tilt_sign·sinTILT,0,cosTILT)；RKP：origin (outboard_x,0,JOINT_Z)，axis 反号。REVOLUTE，名 `{label}_baseplate_to_hanger`，range ±15°，effort 8 / vel 4。
- hanger → wheel：axis = cross-axle (Y)。origin (0, s·WHEEL_Y, AXLE_LOCAL_Z 或 0)，s∈{-1,+1}。CONTINUOUS，名 `{label}_hanger_to_wheel_{side}`，side∈{"0","1"}，effort 2 / vel 30。
- 落地接触面：四轮底面共面 (zmax-zmin<0.006)，且为整装最低件 (wheel zmin < deck zmin − 0.04)。Slot A/B/C 任何动 FRONT_X/REAR_X/AXLE_Z/WHEEL_RADIUS 都必须重解此共面约束。

互斥/派生：Slot A 决定 FRONT_X/REAR_X/DECK_LEN/DECK_THICK（下游 baseplate 锚点 X 与 bolt 网格中心由此派生）；Slot B 决定 WHEEL_Y（轮距）与 kingpin origin/axis 几何，下游 wheel origin 的 Y 由 WHEEL_Y 派生、Z 由所选 truck 的 axle 局部高度派生。

## 每槽位 Module Emits / Interfaces

### Slot A / module deck (popsicle/oldschool/longboard/penny)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `deck` (root part)；visual `deck_board` (lofted mesh) | S0 L171-L172 / 各 deck variant `_deck_mesh` |
| internal joints | 无（deck 是 root，bolts 内联无 joint） | — |
| upstream interface | root；deck 底面 z=DECK_BOTTOM=0 为 baseplate mating face | S0 L213 |
| downstream interface | 两 FIXED 锚 (FRONT_X/REAR_X,0,0) 给 baseplate；bolt 网格中心 = 各 truck X | S0 L208-L214 / L177-L186 |

### Slot B / module truck (cast_kingpin / inverted / wide)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{label}_baseplate`（visual `baseplate`）、`{label}_hanger`（visual `hanger`） | S0 L203-L218 |
| internal joints | `deck_to_{label}_baseplate` FIXED；`{label}_baseplate_to_hanger` REVOLUTE kp_axis ±15° | S0 L208-L234 |
| upstream interface | baseplate 顶面贴 deck 底 (allow_overlap baseplate↔deck_board + expect_contact) | S0 L348-L358 |
| downstream interface | hanger cross-axle (Y) + axle 局部高度，供 wheel CONTINUOUS roll 挂接 | S0 L237-L260 |

### Slot C / module wheel (street_hard / cruiser / cored)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{label}_wheel_{side}` ×2/truck；visual `wheel_rim`+`wheel_tire`+`roll_marker`（cored：`hub_core`+`urethane_ring`+`roll_marker`） | S0 L238-L248 / S7 L282-L298 |
| internal joints | 无（wheel 是叶子 part） | — |
| upstream interface | wheel 套在 hanger cross-axle 上 (allow_overlap wheel_rim/urethane↔hanger) | S0 L366-L374 / S7 L453-L470 |
| downstream interface | `{label}_hanger_to_wheel_{side}` CONTINUOUS axis Y；`roll_marker` pip 用于滚动验证 | S0 L252-L260 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `deck_outline` | enum | {popsicle, oldschool, longboard, penny} | popsicle | choice | deterministic procedural sampler | Slot A 表 |
| `truck_form` | enum | {cast_kingpin, inverted_truck, wide_truck} | cast_kingpin | choice | sampler；wide_truck × penny 受 gate | Slot B 表 |
| `wheel_form` | enum | {street_hard, cruiser_wheels, cored_wheels} | street_hard | choice | sampler | Slot C 表 |
| `bolt_count` | int | [2,8] (test small) / 产品全程见 Multiplicity | 4 | conditional | 偶数优先；范围与 truck 形态无关，但 bolt 网格须落在 baseplate footprint 内 | S8/S9 |
| `palette_style` | enum | {maple_natural, blue_plastic, longboard_woody, cruiser_pastel, urethane_cored, raw_metal_dark} | maple_natural | choice | 每 seed 采样；只改材质 rgba，不改拓扑 | 各 variant materials |
| `deck_length` | float | [0.55, 1.10] | 由 outline | conditional | 由 `deck_outline` 解析 (penny 0.55 / popsicle·oldschool 0.80 / longboard 1.10)；非自由 | Slot A const |
| `truck_x_frac` | float | [0.30, 0.71] | 由 outline | equation | `FRONT_X = truck_x_frac · deck_length/2`，`REAR_X = −FRONT_X`（前后对称） | Slot A FRONT_X/REAR_X |
| `wheel_radius_scale` | float | [0.9, 1.3] | 1.0 | independent | 在范围内独立采样后 clamp；soft/cruiser 偏上 | S6 WHEEL_RADIUS |
| `axle_z` | float | derived | -0.040 | equation | `= -(wheel_radius − ride_height_clear)`，使四轮底共面落地 | S6 AXLE_Z=-0.045 |
| `wheel_y_track` | float | [0.085, 0.125] | 0.092 | conditional | 上限随 `truck_form` 变（wide_truck 才允许 0.120+）；下游 wheel origin Y 派生 | S5 WHEEL_Y |
| (—) | constraint | — | — | inequality | 四轮底面共面带 `max(z_bottom)-min(z_bottom) < 0.006`；违反则按比例回缩 axle_z/wheel_radius_scale 后重采 | run_tests 落地检查 |
| (—) | constraint | — | — | inequality | wheel zmin < deck zmin − 0.04（轮为最低件）；调 deck_thick/axle_z 后校验 | run_tests |
| (—) | constraint | — | — | inequality | bolt 网格半幅 (bolt_dx·cols, bolt_dy·rows) ≤ baseplate 半尺寸，避免 bolt 越出 plate footprint | S9 bolt 网格 |

连续采样契约：先采 independent (`wheel_radius_scale`) → equation 派生 (`truck_x_frac`→FRONT_X/REAR_X，`axle_z`) → inequality 投影/回缩（落地共面、最低件、bolt 网格）→ conditional 解析 (`deck_length`/`wheel_y_track` 上限按上游 enum)。

palette_style 颜色集（取自 5★ 实测 material rgba，下游每 seed 抽样）：
- `maple_natural` — maple deck (0.74,0.58,0.36) + silver truck_metal (0.62,0.64,0.66) + tan wheel (0.86,0.55,0.27) + dark bolt（parent/oldschool/longboard/wide/bolts 系基线）
- `blue_plastic` — blue plastic deck (0.15,0.55,0.78) + silver truck + tan wheel + dark bolt（penny molded look）
- `longboard_woody` — maple deck + silver truck + tan wheel（长板木纹，longboard/inverted 形态偏好）
- `cruiser_pastel` — maple deck + silver truck + 偏亮 tan/orange soft wheel（cruiser_wheels 软轮观感）
- `urethane_cored` — maple deck + silver truck + white hub_core (0.88,0.88,0.86) + orange urethane (0.82,0.48,0.22) + dark bolt（仅 cored_wheels 时双色生效）
- `raw_metal_dark` — maple deck + 暗 raw truck_metal + tan wheel + dark bolt（做旧 raw 铸件观感）

## Multiplicity / Copy Logic

一根 multiplicity 轴：

- `count_param`: `bolt_count`（每个 truck 的 deck-top 安装螺栓数）
- `N_range`: 产品域 `[2, 8]`；test-small `{2,4,6}`（即 5★ 实测覆盖：bolts2 / parent N=4 / bolts6）。真实 truck 多为 4 或 6 孔，2 为 old-school 极简，最多到 8 用于密钉/longboard 硬件。
- sampling domain（权重档）：N=4 最高频，N=6 次之，N=2 较少，N=8 稀有（小 N 偏多、尾部稀有；偏好偶数对称网格）。
- copied object: bolt head（`_bolt_mesh` = 小暗 CylinderGeometry，半径 0.0045 / 高 0.005）
- naming: `deck_bolt_{label}_{i}`（label∈{front,rear}, i∈range(bolt_count)），mesh 名 `bolt_{label}_{i}`
- placement: 每 truck baseplate footprint 上的规则对称网格，heads proud 于 deck top (z=DECK_THICK+0.001)，前后两 truck (FRONT_X/REAR_X) 各复制一份。N=2 → 沿 Y 两孔 (sy=±bolt_spacing_y)；N=6 → 2×3 网格 (col=i%2 给 X 偏移, row=i//2 给 Y 偏移)；通式 = 规则对称网格落在 plate 半尺寸内。
- joint policy: 无 joint —— bolts 内联为 deck（parent）visual（Rule 3）。
- source/gating: parent 的 hardcoded `for sx in(-1,1): for sy in(-1,1)` 2×2 必须重写为单一 `for i in range(bolt_count)` 共享 `_bolt_mesh` 循环（已在 bolts2/bolts6 实证）。bolt_count 与所有 slot enum 正交，仅受 inequality「网格 ≤ plate footprint」约束。

次级复制（非 fork 轴，但模板必须保留）：wheels ×4（每 truck 2 × 2 truck），经 per-truck `for s,side in ((-1,"0"),(1,"1"))` 各发一个 CONTINUOUS roll joint。标准滑板固定 4 轮；不进 fork 网格（非 4 轮会失去类别可读性）。模板可暴露 wheels-per-truck 但采样恒为 2。

## 拓扑多样性审计

总组合数：A × B × C × N_samples = 4 × 3 × 3 × (≥4 个 N 档) = 36 × 4 = **144**（仅 enum 槽位 36 个拓扑骨架，乘 multiplicity N 档）。

理由：仅 slot enum 已 36 个不同拓扑骨架（远超 10）；叠加 bolt_count 多档与连续 scale，distinct 拓扑充裕。即便把 cruiser_wheels 视为 street_hard 的尺度变体而降级 Slot C 到 2，仍有 4×3×2=24 骨架 > 10。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 用 deterministic 加权采样依次选 `deck_outline` → `truck_form` → `wheel_form` → `bolt_count` → `palette_style`，再采连续 scale 并按上述契约 clamp/派生/投影。compatibility gate 拦截 `penny × wide_truck`（见矩阵）。少量 regression overrides 仅用于已知失败/审核样本。random sweep：seeds 0-49 初轮、0-999 成熟审计；viewer 目检覆盖各 outline×truck×wheel 角组合 + N∈{2,4,6,8}。
Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类别 enum 骨架仅 36，受类别强约束（滑板拓扑天然有限），distinct 主要靠 36 骨架 × N 档 × palette 区分，预计 1000-seed 下 distinct 拓扑接近骨架上限（~36×有效 N 档），低于 300 属类别固有约束（滑板结构空间小），以连续 scale + palette 补充视觉多样性。
Controlled local parameterization：`wheel_radius_scale` [0.9,1.3] independent；`axle_z` equation 派生于轮半径（保落地共面）；`truck_x_frac`→FRONT_X/REAR_X equation 对称；`wheel_y_track` conditional 上限随 truck_form；`deck_length`/`deck_thick` 由 outline 解析。全部在 `resolve_config` 内 clamp/派生/投影，不破坏 FIXED 锚 / kingpin REVOLUTE origin/axis / wheel CONTINUOUS 轴 / bolt 网格 footprint / 落地共面。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 deck_outline→truck_form→wheel_form→bolt_count→palette；加权 (小 N 偏多)；compatibility gate 先判 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | `penny × wide_truck` 排除（gullwing 宽轮距在迷你 penny 板上轮子外溅出 deck 导轨/失类别读）→ fallback 到 cast_kingpin 或 inverted；其余 4×3×3 组合合法 | no wheel-outside-rail，no 穿模，落地共面，最低件，对称锚 |
| controlled local variation | wheel_radius_scale / axle_z(派生) / truck_x_frac(派生对称) / wheel_y_track(conditional) | 比例变化不破坏落地共面、kingpin origin/axis、wheel 轴、bolt footprint、类别 identity |
| regression overrides | none（除非 sweep 暴露具体失败 seed） | 仅 previously-failed / reviewer-selected |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A deck_outline | 4 | yes | yes | |
| B truck_form | 3 | yes | yes | |
| C wheel_form | 3 | yes | yes | cruiser_wheels 接近尺度变体；若 reviewer 否决可降级到 2 |
| (mult) bolt_count | N 档 | — | — | [2,8]，test {2,4,6} |

## Validator

- slot_choices_for_seed 返回已实现 module 名 (deck_outline / truck_form / wheel_form)
- config_from_seed 对所有普通 seed 用 deterministic procedural sampling
- compatibility gating 阻止 `penny × wide_truck`
- regression overrides 稀疏且有据
- 不把小型 curated/modulo 表当主 seed domain
- 连续 scale (wheel_radius_scale/axle_z/truck_x_frac/wheel_y_track) 在 resolve_config 内 clamp/派生/投影，不破坏接口、落地共面、joint origin、multiplicity
- 跨件依赖 (axle_z=f(wheel_radius)、FRONT_X/REAR_X 对称、wheel_y_track 上限随 truck) 在 resolve_config 解析
- 关键 InterfaceSpec/MatingContract 存在：deck 底面 mating、kingpin pivot、cross-axle、落地共面
- 关键 joint 保留名/类型/轴：`deck_to_{label}_baseplate` FIXED、`{label}_baseplate_to_hanger` REVOLUTE(kp_axis,±15°)、`{label}_hanger_to_wheel_{side}` CONTINUOUS(Y)
- copied bolts 遵循 `deck_bolt_{label}_{i}` 命名与对称网格 placement，N=bolt_count，无 joint

## Reject cases

1. 四轮底面不共面（zmax-zmin ≥ 0.006）—— 改 outline/axle_z/wheel_radius 后未重解落地约束。
2. 轮不是最低件（wheel zmin ≥ deck zmin − 0.04）—— deck 翘头/厚度或 axle_z 把 deck 压到轮下方。
3. kingpin REVOLUTE 丢失或轴退化（hanger lean 时 axle 不倾，leaned_z ≤ rest_z+0.004），或 RKP 没把 origin 移 outboard / axis 没反号。
4. wheel CONTINUOUS 失效（roll_marker pip 旋转后位移 ≤ 0.01）或轮数 ≠ 4。
5. bolt 仍用 hardcoded 2×2，未改 `for i in range(bolt_count)`；或 bolt 越出 baseplate footprint / 误挂 FIXED joint。
6. `penny × wide_truck` 未被 gate，轮子外溅出迷你板导轨，失类别读。
7. 前后 truck 不对称 (`abs(front_x+rear_x) ≥ 0.01`) 或 wheelbase 过小，板不像滑板。
8. palette_style 改了拓扑（如把 cored 双色硬塞进单实心轮，或漏 hub_core/urethane_ring visual）。

## 与相邻类别的边界

- 不该混入：Roller skate / inline skate（Sports）—— 那是靴体 + 一排沿纵向轮 (in-line) 或四轮台 (quad) 装在脚上，无拉长甲板、无 kingpin REVOLUTE lean truck；滑板是站立甲板 + 横置 cross-axle 双 truck。
- 不该混入：Scooter / kick scooter —— 有立柱 + 把手 + 前叉转向，滑板无立柱/把手，转向靠 truck lean 而非 steering column。
- 不该混入：Surfboard / snowboard / wakeboard —— 同为拉长板但无轮、无 truck、无任何 articulation，不满足关节地板。
- 不该混入：通用 4-wheel cart / dolly —— 轮在固定 caster 上无 kingpin lean 语义、无双翘甲板轮廓，类别读不同。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | (1) Slot C 的 cruiser_wheels 接近 street_hard 的尺度/材质变体——请裁决保留为第 3 candidate，还是降级为 `wheel_size_class` 连续 scale 使 Slot C 退 2 candidate。(2) bolt_count 产品域 [2,8]、test {2,4,6}、偶数偏好与权重档请确认。(3) `penny × wide_truck` 作为唯一硬 gate，其余 4×3×3 全合法——确认无需更多排除项。(4) palette_style 6 色集均取自 5★ 实测 rgba，可按需增减。 |

## 模板实现备注（可选）

- Slot B 三态共享 `{label}_baseplate_to_hanger` / `{label}_hanger_to_wheel_{side}` joint 名与轴语义，模板读 joint 语义不变；RKP 仅改 joint origin（outboard_x, JOINT_Z）+ axis 反号 + axle 局部 Z (AXLE_LOCAL_Z)，不改名。
- Slot C 的 cored 走双 visual (`hub_core`+`urethane_ring`) 双材质，且 spoke 用 `for i in range(NUM_SPOKES)` 共享 `_spoke_geo` helper；其余两轮单实心 rim+tire。模板按 wheel_form 分支决定 visual 集与材质数。
- captured-pin/seated overlap 须 element-scoped allow_overlap：baseplate↔deck_board、hanger↔baseplate、wheel(rim/urethane)↔hanger，对 cored 还需 urethane_ring↔hub_core（每个 truck/wheel 复制）。
- multiplicity bolt 循环与 wheels-per-truck 循环都保留为模板级 `for` 循环；bolts 无 joint，wheels 每个 CONTINUOUS joint。
- 暂不进 seed domain 的组合：`penny × wide_truck`（gate）；longboard × bolts8 等纯跨轴组合交给 sampler，不在样本池预置。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A/B/C/mult | popsicle+cast_kingpin+street_hard+bolts4 | rec_wooden-...b6b31add | deck L62-99 · truck L128-234 · wheel L102-260 · bolts L177-186 | 全 slot 基线 + part tree + joint 语义 |
| S1 | A | oldschool | rec_skateboard_var_oldschool | L65-111 | deck outline 候选 |
| S2 | A | longboard | rec_skateboard_var_longboard | L64-107 + FRONT_X/REAR_X L49-51 | deck outline + 锚点外移 |
| S3 | A | penny | rec_skateboard_var_penny | L63-105 + const L43-48 | deck outline + 锚点内收 |
| S4 | B | inverted_truck | rec_skateboard_var_inverted_truck | const L66-70 · L139-173 · emit L220-258 | RKP truck 几何/轴反号 |
| S5 | B | wide_truck | rec_skateboard_var_wide_truck | L128-190 · WHEEL_Y L57 | gullwing 宽 truck + 轮距 |
| S6 | C | cruiser_wheels | rec_skateboard_var_cruiser_wheels | L107-139 · const L57/L60-61 | 软大轮尺度+carcass+axle_z 重算 |
| S7 | C | cored_wheels | rec_skateboard_var_cored_wheels | L95-165 · emit L278-301 | cored 双 visual + spoke 循环 |
| S8 | mult | bolts2 | rec_skateboard_var_bolts2 | L174-188 | bolt for-i 循环 N=2 |
| S9 | mult | bolts6 | rec_skateboard_var_bolts6 | L174-191 | bolt for-i 2×3 网格 N=6 |
