# Modular Spec — fidget_spinner (Sports / Fidget Spinner)

## 元信息
| 项 | 值 |
|---|---|
| slug | `fidget_spinner` |
| template path | `agent/templates/Sports_Fidget_Spinner.py` |
| test path (optional) | `tests/agent/test_fidget_spinner_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `multiplicity` |

`multiplicity` 主轴 = `arm_count`（中心 cap 上挂一片 N-lobe 旋转盘，每个 lobe 复制一个 weight/bearing 子件 + 一条独立连续旋转关节）。Slot A/B/C 各有 3 个候选模块，统一作用在这套 N-lobe 复制结构上。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category (parent + 9 variants) |
| source_index_policy | only adopted module sources are indexed below |

读取清单（全部 `revisions/rev_000001/model.py`）：
- S0 parent `rec_red-three-arm-fidget-spinner-with-a-central-bear_20260605_165852_289472_5329f102`（round_pods + open_bearing + flat_button, N=3）
- S1 `rec_fidget_spinner_var_solid_disc`（Slot A solid_disc）
- S2 `rec_fidget_spinner_var_gear_edge`（Slot A gear_edge）
- S3 `rec_fidget_spinner_var_domed_weight`（Slot B domed_weight）
- S4 `rec_fidget_spinner_var_hex_weight`（Slot B hex_weight）
- S5 `rec_fidget_spinner_var_domed_cap`（Slot C domed_cap）
- S6 `rec_fidget_spinner_var_knurled_cap`（Slot C knurled_cap）
- S7 `rec_fidget_spinner_var_arms2`（multiplicity N=2）
- S8 `rec_fidget_spinner_var_arms4`（multiplicity N=4）
- S9 `rec_fidget_spinner_var_arms5`（multiplicity N=5）

## 核心身份

掌中旋转玩具：中心 `center_cap`（被两指捏住的 ROOT，含中央银色 hub 轴 + 每面一个红钮/穹顶/滚花帽）静止；一片 **N-lobe 旋转盘 `spinner_body`** 绕中央 +Z 轴 **CONTINUOUS** 自转（`cap_to_body`）；每个 lobe 各持一个 weight/bearing 子件，绕自己的 lobe +Z 轴 **CONTINUOUS** 旋转（`body_to_*_i`）。整体平躺在 XY 平面、厚度沿 +Z、以原点为中心。lobe 在 off-axis（半径 `LOBE_DIST`）布置，保证轴对称体的 spin 可被 AABB 检测；每个 weight/bearing 还带一个 off-axis marker/facet/六角面，使子件自转也可被 AABB 检出（见 KnobGeometry 轴对称 spin-check memory）。默认成熟域：3-arm 经典 fidget spinner，泛化到 2-bar dumbbell ~ 多臂 star。

不该混入：见“与相邻类别的边界”。

## 槽位 + 候选模块表

### Slot A：body_outline（spinner_body 旋转盘形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_pods | rec_red-three-arm-fidget-spinner-with-a-central-bear_…5329f102 (S0) | L63-L113 (`_tri_lobe_body`) | eligible if compatible | 中心 hub disc + N 个 round lobe disc + 锥形 web 桥；臂间留开口（gap）；每 lobe 钻 bearing pocket、中心钻 hub bore；`edges("|Z").fillet(0.0012)` 玻璃感倒角 |
| solid_disc | rec_fidget_spinner_var_solid_disc (S1) | L71-L135 (`_solid_reuleaux_plate`) | eligible if compatible | N 个 lobe circle + 中心 hub + 相邻 lobe 间宽矩形 bridge（宽=2·LOBE_R 切于 lobe 圆）填满臂间，形成无开口的 Reuleaux 连续实心盘；bearing pocket 直接钻穿 |
| gear_edge | rec_fidget_spinner_var_gear_edge (S2) | L72-L92 (`_make_tooth`) + L95-L170 (`_gear_body`) | eligible if compatible | round_pods 基底上每 lobe 沿 rim union `NUM_TEETH_PER_LOBE=14` 个梯形 sawtooth 齿（共享 `_make_tooth` helper + for 循环），齿尖超出 smooth lobe 半径；fillet 半径调小(0.0005)避免破坏齿尖，且包 try/except |

### Slot B：lobe_weight（每个 lobe pocket 装什么）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| open_bearing | rec_red-three-arm-fidget-spinner-with-a-central-bear_…5329f102 (S0) | L116-L143 (`_bearing_ring_mesh` + `_bearing_race_mesh`) | eligible if compatible | 暴露滑板轴承：黑橡胶 outer ring（环 annulus）+ 银 inner race + 开放中心孔；race 上 off-axis box marker（L136-141）使 spin 可检；2 个 visual（`bearing_i_ring`/`bearing_i_race`）；press-fit 进 pocket |
| domed_weight | rec_fidget_spinner_var_domed_weight (S3) | L111-L172 (`_dome_weight_mesh`) | eligible if compatible | 抛光金属双凸透镜：cylindrical plug 填满 pocket + 上/下两个球冠 dome 凸出体面；off-axis D 形平切 facet（L162-170）破对称使 spin 可检；单 visual `weight_i_dome`，chrome 材质 |
| hex_weight | rec_fidget_spinner_var_hex_weight (S4) | L66-L141 (`_tri_lobe_body` 内含 axle pin+spider) + L144-L170 (`_hex_nut_mesh`) | eligible if compatible | 黄铜六角螺母 prism（6 平面 + 中心 bore + chamfer）；本模块改写 body：pocket 中心保留 axle pin + 2 条正交 cross-spoke spider 桥（L106-128），hex 套在 pin 上自转；六平面天然使 AABB 非对称 |

### Slot C：center_cap（中心捏柄/held ROOT 形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_button | rec_red-three-arm-fidget-spinner-with-a-central-bear_…5329f102 (S0) | L155-L181 (cap build block) | eligible if compatible | 银 hub barrel（CylinderGeometry，跨过两面）+ 每面一个红色扁圆 `cap_button_top/bottom`（Cylinder disc，凸出体面 CAP_DISC_T）；3 个 visual |
| domed_cap | rec_fidget_spinner_var_domed_cap (S5) | L153-L197 (`_pinch_dome_profile`/`_pinch_dome_mesh`/`_pinch_dome_mesh_flipped`) + L207-L233 (cap build block) | eligible if compatible | 银 hub + 每面一个 LatheGeometry 蘑菇 pinch dome（Catmull-Rom 样条 lathe，带 base flange 与体面接触，dome 外悬）；上面正放、下面 `rotate_x(pi)` 翻转 |
| knurled_cap | rec_fidget_spinner_var_knurled_cap (S6) | L152-L170 (`_spin_cap_body` + `_knurl_ridge`) + L182-L249 (cap build block) | eligible if compatible | 银 hub（跨全高）+ 上面高 gunmetal spin cap（standing proud）+ 下面低 cap；每个 cap 沿 rim 用共享 `_knurl_ridge` helper 复制 `KNURL_COUNT=24` 条竖直 ridge inline visual（半埋半凸，knurl_steel 材质） |

候选数：每 slot 3 个（≥3，无需降级）。每个 candidate 结构差异显著（开口盘/实心盘/齿盘；开放轴承/实心穹顶/六角螺母+spider；扁钮/lathe穹顶/滚花高帽），非仅尺寸/颜色变化。

## 槽位图（slot graph）

pattern: multiplicity

```
center_cap (Slot C, ROOT, 静止)
   │
   └─[cap_to_body : CONTINUOUS, axis=+Z, origin=(0,0,HALF_T), 无限程]──> spinner_body (Slot A)
                                                                              │  (×N lobe, equal-spacing)
                                                                              └─[body_to_<wt>_i : CONTINUOUS, axis=+Z,
                                                                                  origin=(LOBE_DIST·cosθ_i, LOBE_DIST·sinθ_i, HALF_T),
                                                                                  无限程]──> lobe_weight_i (Slot B) ×N
```

- 组装顺序/parent：`center_cap` 是 ROOT；`spinner_body` 挂在 cap 下（中央 +Z spin）；每个 `lobe_weight_i` 挂在 body 下（各自 lobe +Z spin）。
- 接口点位：
  - C→A：中央 +Z 对称轴 / 体中心 hub bore（cap hub barrel 穿过 `spinner_body` 中心孔，origin 在 (0,0,HALF_T)）。symmetry plane = 中央 Z 轴。
  - A→B：lobe pocket（半径 `BEARING_POCKET_R` 的圆形 pocket，圆心在 (LOBE_DIST·cosθ_i, LOBE_DIST·sinθ_i)）。pivot = 各 lobe 的 +Z 轴，z 在板厚中点 HALF_T。
- joint：两层都是 CONTINUOUS（无限程，`MotionLimits(effort, velocity=80)`），轴均为 (0,0,1)；无 prismatic/revolute-limit。
- 互斥/派生：lobe 数量 N 由 `arm_count` 派生（A 的 lobe 与 B 的子件数量必须一致）；Slot A/B/C 三个轴正交，原则上自由组合（少量兼容门控见审计节）。

## 每槽位 Module Emits / Interfaces

### Slot A / module round_pods
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spinner_body` part；单 visual `tri_lobe_body`（red 材质）；inertial=Cylinder(LOBE_DIST+LOBE_R) | S0 / L184-194 |
| internal joints | 无（盘本体为单刚体） | S0 |
| upstream interface | 中心 hub bore(半径 CAP_HUB_R+0.0004) 接受 cap hub；cap_to_body 关节 origin=(0,0,HALF_T) child | S0 / L102-109,195-203 |
| downstream interface | N 个 lobe pocket(半径 BEARING_POCKET_R, 圆心 LOBE_DIST·(cosθ,sinθ))；body_to_bearing_i 关节 parent | S0 / L89-100,207-239 |

### Slot A / module solid_disc
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spinner_body` part；单 visual `solid_plate`（连续 Reuleaux 实心盘，无臂间开口） | S1 / L206-211 |
| internal joints | 无 | S1 |
| upstream interface | 同 round_pods（中心 hub bore） | S1 / L126-133 |
| downstream interface | N 个 lobe pocket（直接钻穿盘） + body_to_bearing_i parent | S1 / L113-124,229-261 |

### Slot A / module gear_edge
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spinner_body` part；单 visual `gear_body`（round_pods 基底 + 每 lobe rim 14 齿 sawtooth） | S2 / L240-246 |
| internal joints | 无（齿为 body mesh 一部分，非独立 part） | S2 |
| upstream interface | 中心 hub bore | S2 / L155-162 |
| downstream interface | N 个 lobe pocket + body_to_bearing_i parent；齿尖超出 smooth 半径需在 AABB envelope/clearance 中计入 | S2 / L142-153,262-296 |

### Slot B / module open_bearing
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bearing_i` part ×N；2 visual（`bearing_i_ring` 黑橡胶 + `bearing_i_race` 银 race+marker） | S0 / L207-229 |
| internal joints | 无（ring+race 同 part 刚体） | S0 |
| upstream interface | press-fit 进 lobe pocket（允许 ring↔body overlap）；body_to_bearing_i child, origin=(cx,cy,HALF_T) | S0 / L230-239,321-333 |
| downstream interface | 开放中心孔（终端，无下游子件） | S0 / L127-143 |

### Slot B / module domed_weight
| emits | 描述 | 来源 |
|---|---|---|
| parts | `weight_i` part ×N；单 visual `weight_i_dome`（chrome 双凸透镜 + off-axis facet） | S3 / L236-260 |
| internal joints | 无 | S3 |
| upstream interface | press-fit 进 lobe pocket；body_to_weight_i child, origin=(cx,cy,HALF_T) | S3 / L251-260,356-368 |
| downstream interface | dome 凸出体面（终端，可见凸顶，无下游） | S3 / L111-172,344-354 |

### Slot B / module hex_weight
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hex_weight_i` part ×N；单 visual `hex_weight_i_nut`（黄铜六角 prism + 中心 bore） | S4 / L233-258 |
| internal joints | 无（但本模块要求 body 内置 axle pin + spider 桥） | S4 |
| upstream interface | 套在 body 内置 axle pin 上（pin/spider 穿 hex bore，allow_overlap body↔hex）；body_to_hex_weight_i child, origin=(cx,cy,HALF_T) | S4 / L106-128,344-373 |
| downstream interface | 终端 | S4 / L144-170 |

### Slot C / module flat_button
| emits | 描述 | 来源 |
|---|---|---|
| parts | `center_cap` part(ROOT)；3 visual（`cap_hub` 银 barrel + `cap_button_top`/`cap_button_bottom` 红扁钮） | S0 / L155-176 |
| internal joints | 无 | S0 |
| upstream interface | ROOT（无 parent） | S0 |
| downstream interface | hub barrel 穿过 body 中心 bore（allow_overlap cap_hub↔body）；cap_to_body 关节 parent, origin=(0,0,HALF_T) | S0 / L157-163,195-203 |

### Slot C / module domed_cap
| emits | 描述 | 来源 |
|---|---|---|
| parts | `center_cap` part(ROOT)；银 hub + 每面一个 lathe 蘑菇 pinch dome | S5 / L207-233 |
| internal joints | 无 | S5 |
| upstream interface | ROOT；hub origin 调整为穿过两面 (z=BODY_THICK) | S5 / L211-219 |
| downstream interface | hub 穿 body 中心 bore；cap_to_body parent | S5 / L220-233 |

### Slot C / module knurled_cap
| emits | 描述 | 来源 |
|---|---|---|
| parts | `center_cap` part(ROOT)；银 hub(跨全高) + 上高/下低 gunmetal spin cap + 每 cap KNURL_COUNT 条 ridge inline visual | S6 / L182-249 |
| internal joints | 无（ridge 是 inline visual，非 part） | S6 |
| upstream interface | ROOT；hub_center_z 由 cap 总高推算 | S6 / L186-200 |
| downstream interface | hub 穿 body 中心 bore；cap_to_body parent；cap 总高与 body 厚干涉需 clearance（见 reject） | S6 / L189-216 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_outline` | enum | {round_pods, solid_disc, gear_edge} | round_pods | choice | deterministic procedural sampler 选择 | Slot A 表 |
| `lobe_weight` | enum | {open_bearing, domed_weight, hex_weight} | open_bearing | choice | sampler 选择 | Slot B 表 |
| `center_cap` | enum | {flat_button, domed_cap, knurled_cap} | flat_button | choice | sampler 选择 | Slot C 表 |
| `palette_style` | enum | {classic_red_silver, gunmetal_steel, brass_machined, chrome_polished, neon_acid, stealth_black} | classic_red_silver | choice | 每 seed 采样配色;映射 body/cap/weight 材质 rgba | 见下 palette 节 |
| `arm_count` | int | 测试 [2,5]，产品 [2,8] | 3 | conditional | multiplicity 主轴;360/arm_count 等角;见 Multiplicity 节 | S7/S8/S9 |
| `body_thick_scale` | float | [0.85, 1.20] | 1.0 | independent | 缩放 BODY_THICK;范围内均匀采样后 clamp | S0 / L40 |
| `lobe_dist_scale` | float | [0.90, 1.20] | 1.0 | independent | 缩放 LOBE_DIST（臂展） | S0 / L44 |
| `lobe_r_scale` | float | [0.85, 1.10] | 1.0 | equation | `LOBE_R = clamp(0.0150·s)`，但受下方不等式约束 | S0 / L43 |
| `pocket_r` | float | derived | — | equation | `= LOBE_R − pocket_margin`（pocket 必须含于 lobe） | S0 / L43,47 |
| `bearing_outer_r` | float | derived | — | equation | `= BEARING_POCKET_R + press_fit(≈0.0003)` 过盈 | S0 / L47-48 |
| (—) | constraint | — | — | inequality | **臂不重叠**：`LOBE_R ≤ LOBE_DIST·sin(pi/arm_count)·k`（k≈0.95）。N 增大时 lobe 半径上限收紧;违反则按比例回缩 LOBE_R 或拒采 | 接口/几何 |
| (—) | constraint | — | — | inequality | **pocket 含于 lobe**：`BEARING_POCKET_R + wall_min ≤ LOBE_R`（wall_min≈0.002） | S0 / L43,47 |
| (—) | constraint | — | — | inequality | **hub 不吃 pocket**：`HUB_R + web_clear ≤ LOBE_DIST − BEARING_POCKET_R` | S0 / L44-47 |
| (—) | constraint | — | — | inequality | **knurled_cap 高度**：`cap 总高(TOP_CAP_T+BOTTOM_CAP_T+BODY_THICK)` 与 arm_count=2 bar 厚不干涉;否则降 cap 高或门控（见兼容矩阵） | S6 / L58-66 |

palette_style → 材质映射（取自 5★ 实际观测材质）：
- `classic_red_silver`：body=glossy_red(0.82,0.07,0.09) / hub=silver_steel(0.78,0.80,0.83) / weight=rubber_black+silver（S0）。
- `gunmetal_steel`：cap=gunmetal_cap(0.38,0.40,0.43) / ridge=knurl_steel(0.50,0.52,0.55) / body=silver_steel（S6）。
- `brass_machined`：weight=machined_brass(0.76,0.60,0.12) / hub=silver_steel / body=glossy_red（S4）。
- `chrome_polished`：weight=polished_chrome(0.85,0.87,0.90) / body=silver_steel / hub=silver_steel（S3）。
- `neon_acid`：body=glossy_red 调亮高饱和（红/绿/紫之一）/ hub=silver_steel（S0 glossy_red 基础上提饱和度,realistic anodized 玩具配色）。
- `stealth_black`：body=rubber_black(0.06,0.06,0.07) / hub=gunmetal_cap / weight=silver_steel（S6/S0 黑+金属）。

（颜色为 module-local 选择，不改拓扑;weight/cap 的具体 rgba 在所选 module 内按 palette 重映射。）

## Multiplicity / Copy Logic

单轴 multiplicity。

- `count_param`：`arm_count`（lobe/arm 数量;每 lobe 携带一个 weight/bearing 子件 + 一条独立 CONTINUOUS 关节）。
- `N_range`：测试偏小 `[2, 5]`（已被 5★ 覆盖：S7=2 / S0=3 / S8=4 / S9=5）；产品全程 `[2, 8]`（real fidget spinner 2..~7 臂;>8 不再读作 spinner，取上界 8）。
- sampling domain（加权）：小 N 高频、尾部稀有。建议权重 N=3 最高(经典)，2/4/5 次之，6/7/8 长尾稀有。例：{2:0.16, 3:0.34, 4:0.20, 5:0.14, 6:0.08, 7:0.05, 8:0.03}（人工审核后定档）。
- copied object：一个 lobe 单元 = body 上的 {lobe disc + web 桥（或 solid bridge / 齿环 / spider，随 Slot A/B 决定，inline body visual）} + 一个 {bearing_i / weight_i / hex_weight_i} child part（含自己的 CONTINUOUS spin 关节）。
- naming：body 上 inline lobe/web 几何（无独立命名 part）；子件 part = `bearing_i`/`weight_i`/`hex_weight_i`（按 Slot B 模块命名）；关节 `body_to_bearing_i` / `body_to_weight_i` / `body_to_hex_weight_i`（i=0..arm_count-1）。
- placement：等角 `θ_i = base_angle + i·2π/arm_count`，base_angle=π/2（S0/S8/S9 约定;S7 用 0 起始）。lobe 中心 (LOBE_DIST·cosθ_i, LOBE_DIST·sinθ_i)，z 子件原点在 HALF_T。
- joint policy：每个 lobe 子件各一条 CONTINUOUS revolute 绕 lobe +Z（相对 body），所有 i 一致（uniform）；中央 `cap_to_body` CONTINUOUS +Z 关节独立，与 N 无关、不复制。
- source/gating：N=1 排除（单臂只有中央一个旋转面，读不出 spinner，N_range 下界取 2，见排除项）。lobe 半径上限随 N 收紧（见参数表臂不重叠不等式，conditional/inequality）。

## 拓扑多样性审计

总组合数：A × B × C × N = 3 × 3 × 3 × |N_samples|。
- 仅 slot 组合 = 3×3×3 = 27。
- 计入 N 测试样本 {2,3,4,5}（4 档）= 27 × 4 = **108** distinct 拓扑（产品 N∈[2,8] 7 档 = 189）。

理由：27 个纯 slot 组合已远超 10；叠加 multiplicity N 后 108+。即使扣除少量兼容门控组合（见矩阵）仍 >>10。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed` 用 deterministic 加权采样：先采三个 slot enum（各 1/3 近似均匀，可对经典 round_pods/open_bearing/flat_button 略加权）、再加权采样 `arm_count`（小 N 偏多）、再采 `palette_style`、最后采连续 scale（先 independent：body_thick/lobe_dist/lobe_r → 派生 pocket/bearing_outer → 用不等式投影回缩 lobe_r/拒采）。slot_choices_for_seed 必须与 build 选择一致。compatibility matrix 在采样后过滤非法组合并 fallback。Topology target：1000-seed slot choice tuple distinct 富类别建议 ≥300（report-only）；本类 27 slot 组合 × 7 N = 189 上限，足够 ≥300（低于纯几何上界属正常，类别本身 slot 维度有限，已在审计说明）。

Regression overrides：none（如后续 sweep 暴露特定 N×module 失败再补 seed + 理由，不作主 seed domain）。

Controlled local parameterization：初版模板包含 `body_thick_scale`、`lobe_dist_scale`、`lobe_r_scale`（→派生 pocket_r、bearing_outer_r）。全部在 `resolve_config` 内 clamp/派生/投影，不破坏 InterfaceSpec（hub bore / lobe pocket）、MatingContract（press-fit 过盈带）、multiplicity（等角布置）。臂不重叠、pocket 含于 lobe、hub 不吃 pocket 三条不等式跨部件依赖显式声明（见第 7 节），不当作独立自由变量各抽各的。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot order A→B→C→arm_count→palette→scales；slot 近均匀（经典略加权），N 小偏多 | slot_choices_for_seed matches build choices |
| compatibility matrix | 见下兼容门控 | no floating, collision, axis, max multiplicity, bulky module, cap-vs-bar clearance |
| controlled local variation | body_thick/lobe_dist/lobe_r scale + 派生 pocket/bearing_outer，clamp+不等式回缩 | proportions vary without breaking interfaces, clearance, joint origin, identity |
| regression overrides | none | previously failed / reviewer-selected only |
| random sweep | seeds 0-49 初轮，0-999 成熟审计 | contract failures |

兼容矩阵 / gating（排除项素材，部分待 sweep 回填）：
- N=1 永远排除（出类目，N_range 下界=2）。
- `knurled_cap × arm_count=2`：knurled_cap hub 总高(TOP_CAP_T+BOTTOM_CAP_T+BODY_THICK) 较高，2-bar dumbbell 体薄，若 hub 长度与 bar 厚干涉则门控或自动降 cap 高（源:排除项待跑回填 + S6 L58-66）。
- `gear_edge` 在 segments 偏高 / 齿距偏细时 CadQuery 布尔可能 "Profile area must be non-zero" 退化（见 roller-skate memory）→ 退低分段或粗齿距;`_gear_body` 已对 fillet 包 try/except。
- `solid_disc × gear_edge` 不共存（互斥 enum，同一 Slot A 不会同时选;source map 提到“实心盘把齿吃掉”仅作语义提醒，模板内本就单选）。
- `hex_weight` 要求 body 内置 axle pin + spider 桥（body 几何随 Slot B 选择微调）；若 Slot A=gear_edge/solid_disc，pin+spider 仍可加在各 lobe pocket 中心（pocket 几何一致），原则兼容，但需在 build 中按 lobe_weight==hex_weight 条件注入 pin/spider（conditional body 变体）。

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A body_outline | 3 | yes | yes | round_pods / solid_disc / gear_edge |
| B lobe_weight | 3 | yes | yes | open_bearing / domed_weight / hex_weight |
| C center_cap | 3 | yes | yes | flat_button / domed_cap / knurled_cap |
| (mult) arm_count | 7 (N∈[2,8]) | yes | yes | 测试 {2,3,4,5} |

## Validator

- slot_choices_for_seed returns implemented module names（A/B/C enum + arm_count + palette）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds
- compatibility matrix / gating prevents illegal combos（N≥2、knurled×N2 clearance、hex 注入 pin/spider、gear 布尔退化 fallback）
- optional regression overrides are sparse / none
- final template does not endlessly cycle a small curated table as main seed domain
- controlled local scale params clamped；臂不重叠/pocket含于lobe/hub不吃pocket 不等式在 resolve_config 求解，不留到 builder
- critical InterfaceSpec/MatingContract 存在：中心 hub bore（cap hub 穿 body）、N 个 lobe pocket（weight press-fit）
- key joints：`cap_to_body` CONTINUOUS axis=(0,0,1) origin=(0,0,HALF_T)；`body_to_*_i` CONTINUOUS axis=(0,0,1) origin=(LOBE_DIST·cosθ_i,…)，共 arm_count 条
- copied objects 命名/布置遵循 policy（`*_i`，等角，i=0..arm_count-1）
- spin 可检：body off-axis lobe + 每子件 off-axis marker/facet/六角面（AABB 在 90° 旋转下交换 x/y extent）

## Reject cases

- arm_count=1 或 <2：单旋转面，不读作 fidget spinner（应被 N_range 下界拒）。
- lobe 互相穿模：LOBE_R 相对 N 过大未按不等式回缩（N=5/6 时 lobe 重叠）。
- bearing/weight 漂浮：子件未 press-fit 进 pocket（z 向 overlap 不足，或 pocket_r 与子件半径不匹配 → expect_overlap 失败）。
- 中央 cap 随 body 一起转：cap 不是静止 ROOT，或 cap_to_body parent/child 接反（cap 应不动）。
- spin 检测失败：body 轴对称无 off-axis lobe，或 weight 无 off-axis marker/facet（AABB 旋转前后不变 → spin 不可检）。
- center hub 未穿 body / 未与 body bore 对位：cap_hub 与 body 无 allow_overlap+expect_overlap，或 bore 半径 < hub 半径致 disconnected。
- knurled_cap 在 N=2 薄 bar 上 hub 干涉 body / cap 互撞未门控。
- gear_edge 齿布尔退化（"Profile area must be non-zero"）未 fallback 低分段/粗齿距。
- hex_weight 选中但 body 未注入 axle pin + spider，hex 漂浮（无支撑接触 → disconnected/floating）。

## 与相邻类别的边界

- 不该混入：**Yo-yo / 陀螺(spinning top)**（理由：fidget spinner 是平躺 XY、被两指捏住的多臂盘绕 +Z 自转;陀螺是立式绕自身竖轴在地面进动、yo-yo 有绳。本类无绳、无地面支撑、ROOT 是手捏 cap）。
- 不该混入：**轴承/齿轮零件(bearing / gear part)**（理由：open_bearing/gear_edge 只是 lobe 装饰与 weight 模块，整体仍是玩具;不应退化成单独一个工业轴承或齿轮，必须保留 N-lobe 旋转盘 + 中心 held cap 结构）。
- 不该混入：**按钮玩具 / fidget cube/popper**（理由：本类核心是连续无限程旋转关节（cap_to_body + body_to_weight），不是按压/拨动的有限行程开关）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核：(1) arm_count 产品上界取 8 是否合适;(2) palette_style 的 neon_acid 是否需收紧到 5★ 实测 rgba（目前为 glossy_red 提饱和的合理外推）;(3) hex_weight 作为 conditional body 变体（注入 axle pin+spider）是否拆成 Slot A 子状态而非 Slot B 副作用;(4) knurled_cap×N=2 clearance 门控阈值待 sweep 回填。 |

## 模板实现备注（可选）

- 共享 helper：`_lobe_angles(n)`（S9 L59-61 已是参数化版，建议作为模板基底）、`_bearing_ring_mesh`/`_bearing_race_mesh`（S0，open_bearing）、`_dome_weight_mesh`（S3）、`_hex_nut_mesh`（S4）、`_make_tooth`/`_gear_body`（S2）、`_pinch_dome_*`（S5）、`_spin_cap_body`/`_knurl_ridge`（S6）。各 Slot 模块直接复用对应 helper。
- InterfaceSpec 重点：中心 hub bore（cap_hub 穿 body，allow_overlap + expect_overlap z≥0.006）、lobe pocket（weight press-fit，allow_overlap + expect_overlap z≥0.004）。
- captured-pin overlap：hex_weight 的 axle pin+spider 穿 hex 中心 bore，需 element-scoped allow_overlap(body, hex_weight_i, elem tri_lobe_body/hex_weight_i_nut)（S4 L344-373）。
- 暂不进入 seed domain 的组合：N≥6 与 gear_edge 高分段（布尔退化风险，先用低分段/粗齿距 fallback）；knurled_cap×N=2（clearance 门控待回填）。
- arm_count 起始角统一 base_angle=π/2（与 S0/S8/S9 一致），避免 S7 的 0 起始导致 viewer 朝向不一致。
