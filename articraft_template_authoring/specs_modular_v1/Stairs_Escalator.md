# Escalator — Modular Template Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `escalator` |
| template path | `agent/templates/Stairs_Escalator.py` |
| test path (optional) | `tests/agent/test_escalator_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（multiplicity step-band + named structural slots：balustrade_style / incline_geometry / landing_pit；外加 single-vs-twin unit 复制轴） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category（2 parents + 8 forked variants） |
| source_index_policy | only adopted module sources are indexed below |

阅读结论：

- **两条独立 spine**。Parent A (`e7415cae`，single-unit) 用一个 *solid wedge truss* + 中央 step band + 玻璃/金属 balustrade + 可选铰接 pit cover。Parent B (`8388963a`，twin-unit) 用 *side-truss + cross-bracing + 共享 center divider*，每个 unit 一条 step band（带 roller/guide-track），两 unit 镜像于 y=0。8 个 variant 全部落在这两条 spine 之一：
  - Single spine (parent A 衍生)：`metalpanel`（balustrade swap）、`steep`（35°）、`shallow`（22°）、`steps7`（N=7，TRUSS_RUN 派生）、`steps22`（N=22，TRUSS_RUN 派生）。
  - Twin spine (parent B 衍生)：`glasspanel`（balustrade swap）、`pitcover`（加 per-unit 铰接 pit cover）、`twinsteps14`（N=14，RUN/RISE 派生）。
- **类别核心 articulation = moving step band 的 PRISMATIC 平移**，轴 = incline 单位向量 `(cosθ,0,sinθ)`，行程恰为一个 step pitch `hypot(STEP_DEPTH, STEP_RISE)`。每个 unit 一条。两条 spine 都一致采用这一策略。
- **handrail 永远 FIXED**（焊接环路，刚性平移会脱离 newel 端），不作为独立运动件。
- **pit cover 出现时 = REVOLUTE about +Y**，铰链在 pit 上坡边、landing 顶面；闭合贴地、开启抬起。single spine 一个 cover；twin spine per-unit cover。
- step band 是真正的 multiplicity 轴：`steps7/steps22`（single）与 `twinsteps14`（twin）都用 `for i in range(N)` + 共享 step helper 发射 tread+riser，pitch=(STEP_DEPTH, STEP_RISE)。N 样本覆盖 {7, 11, 14, 16, 22}。
- incline 几何是真正的拓扑/比例变化轴：standard(30°/28°)、steep(35°，短 run)、shallow(22°，长 run)，axis 随 θ 重新派生。

## 核心身份

一台 **escalator（moving staircase / 自动扶梯）**：一条沿 ~22°–35° 倾斜的钢桁架（truss），从下层 landing 升到上层 landing；桁架中央是一条**连续移动的踏步带（step band）**——若干 tread+riser 沿 incline 等距排列，作为整体在 PRISMATIC 关节上沿斜面平移（类别定义性运动）。两侧是 balustrade（栏板，玻璃或实心金属），栏板顶缘焊接橡胶 handrail（环路，固定不动）。上下两端各有 landing 平台与 comb/floor plate（踏步从其下钻出/没入）。可选：下层 landing 设维修 pit + 铰接盖板（REVOLUTE 抬起）。可单台（single unit）或并排双台（twin units，含共享 center divider）。

默认成熟域：transit-hall / mall / airport 级整机扶梯，real-world 米制尺度，N 在 [4,60] 之间的合理 step band。

不该混入：
- **Elevator（电梯，独立类别）**：电梯是竖直 PRISMATIC 轿厢 + 井道 + 门，没有 incline truss、没有 step band、没有 handrail。escalator 的身份在 incline + moving step band。
- **plain Stairs（静态楼梯）**：普通楼梯无任何 articulation——没有 PRISMATIC step band、没有 handrail loop 语义、没有 pit cover。若产物没有沿斜面平移的 step band，就不是 escalator。

## 槽位 + 候选模块表

> 说明：spine（single vs twin）是 multiplicity 轴 D（见第 8 节），不是普通 slot；但它决定每个 slot 的 candidate 取舍（兼容矩阵见第 9 节）。

### Slot A：balustrade_style（两侧栏板材料 + 透明度 + 承载方式）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| tinted_glass_panel (single spine) | rec_..._e7415cae (parent A) | L234-L306 | eligible if compatible（spine=single） | deck rail 横跨 skirt→newel 承载，其上一片 `tinted_glass` 斜面玻璃 + 上下椭圆 nose 端帽；visual 名 `glass_left/right`；handrail 坐在玻璃顶缘 |
| solid_metal_panel (single spine) | rec_escalator_var_metalpanel | L235-L307 | eligible if compatible（spine=single） | 同 deck 承载，但栏板为不透明 `brushed_metal` 实心板（PANEL_T=0.018）+ 椭圆 nose；visual 名 `panel_left/right` |
| smoked_glass_panel (twin spine) | rec_escalator_var_glasspanel | L144-L179 + L488,L513-L518 | eligible if compatible（spine=twin） | side-truss 上的玻璃栏板 slab（`_build_balustrade`），下唇下探嵌入 truss slab；material `smoked_glass`(0.55 a)；per-unit `balustrade_left/right_{a,b}` |
| dark_metal_panel (twin spine) | rec_..._8388963a (parent B) | L144-L179 + L487,L513-L518 | eligible if compatible（spine=twin） | 同 `_build_balustrade` slab，但 material=`dark_steel`（不透明深金属）；parent B 默认；per-unit visual |

candidate 差异说明：玻璃 vs 实心金属在 single spine 上是不同 build 路径（`glass`+nose union vs `panel`+nose union，不同 visual 名/material 角色），在 twin spine 上是同一 `_build_balustrade` slab 的 material 角色切换（透明玻璃 vs 不透明深金属，影响身份读数）。两 spine 各 2 candidate，合计 4，>2 满足硬约束。

### Slot B：incline_geometry（倾角 θ + 水平 run + 由此派生的 step pitch）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| standard_30deg | rec_..._e7415cae (parent A) | L43-L75 | eligible if compatible | θ=30°，TRUSS_RUN=4.40，STEP_RISE=0.205/STEP_DEPTH=0.355；incline axis `(cos30,0,sin30)`；medium run |
| standard_28deg_long (twin) | rec_..._8388963a (parent B) | L43-L62 | eligible if compatible（spine=twin） | θ=atan2(3.40,6.40)≈28°，RUN=6.40/RISE=3.40，STEP_RISE=0.21，STEP_GO=RISE/tanθ；twin 默认 |
| steep_short_35deg | rec_escalator_var_steep | L43-L75 | eligible if compatible | θ=35°（space-saver），TRUSS_RUN=3.60（短），STEP_RISE=0.240/STEP_DEPTH=0.343；axis 随 35° 重派生 |
| shallow_long_22deg | rec_escalator_var_shallow | L44-L75 | eligible if compatible | θ=22°（transit-hall/airport），TRUSS_RUN=6.40（长），STEP_DEPTH=0.40、STEP_RISE=STEP_DEPTH·tan22°；axis 随 22° 重派生 |

candidate 差异说明：θ 改变 incline axis（PRISMATIC + REVOLUTE 几何参考）、truss 侧轮廓、step pitch (DEPTH,RISE)、handrail 旋转角——属真实几何/比例拓扑轴而非纯尺寸。模板内统一为连续 θ 区间 + 离散标称档（见第 7 节），但每档都有真实 5★ 源。4 candidate。

### Slot C：landing_pit（下层 landing 维修访问）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| hinged_pit_cover (single spine) | rec_..._e7415cae (parent A) | L453-L487（build）+ L538-L552（joint） | eligible if compatible（spine=single） | lower_landing 切 pit + dark machinery box（L143-L184），`pit_cover` part：plate 局部 -X 延伸 + 两 hinge knuckle；REVOLUTE about +Y，origin=(hinge_x,0,LANDING_TOP_Z)，limits lower=0,upper=1.4 |
| hinged_pit_cover (twin spine) | rec_escalator_var_pitcover | L494-L584（4 helpers）+ L711-L734（per-unit joint） | eligible if compatible（spine=twin） | per-unit `pit_cover_{a,b}` part：diamond-tread plate + recess + U-rim + 交替 hinge knuckles；REVOLUTE +Y，origin=(PIT_X_HINGE,y_off,FLOOR_Z)，limits lower=0,upper=1.2 |
| open_flush_landing (twin spine) | rec_..._8388963a (parent B) | L380-L422 | eligible if compatible | 无 pit、无额外 joint：comb/floor plate（`landing_plates`）齐平，踏步从其下钻出；身份上的 "无 pit" 档 |
| open_flush_landing (single spine) | rec_escalator_var_steps7 / steps22 (parent A 衍生，无 pit_cover) | steps7 L198-L208 (lower_comb) | eligible if compatible | single spine 也可省 pit：仅 lower_landing+comb，不建 `pit_cover` part / `frame_to_pit_cover` joint |

candidate 差异说明：hinged_pit_cover 引入一个 REVOLUTE part（拓扑变化），open_flush 不引入额外 part/joint。single 与 twin spine 的 cover build 是不同 helper 路径，故分列。4 entries（实为 2 结构家族 × 2 spine），每个都有真实源；single-spine open_flush 的源是 steps7/steps22（它们本就不建 pit_cover——只发射 lower_comb，证明该结构可省）。

## 槽位图（slot graph）

pattern: mixed

```
                         [unit multiplicity 轴 D: single | twin]
                                       │
                                       ▼
frame/truss (ROOT, FIXED 全部静态结构) ──┬──[PRISMATIC, axis=incline_dir(θ), origin=(0,0,0),
   ├─ Slot A balustrade (parent visual, │      lower=0 upper=step_pitch]──> step_band  ◀ multiplicity 轴 N (steps)
   │    嵌入 truss slab / deck 承载)      │
   ├─ Slot B incline 几何 (决定 θ→axis,  ├──[FIXED, origin=(0,0,0)]──> handrail loop(s)  (per side / per unit)
   │    truss 轮廓, step pitch)           │
   └─ handrail mounts (栏板顶缘)          └──[REVOLUTE, axis=(0,1,0), origin=(hinge_x, y_off, FLOOR_Z),
                                             lower=0 upper≈1.2~1.4]──> Slot C pit_cover   (仅当 landing_pit=hinged)
   twin spine 额外: center_divider + cross_bracing 把两 side-truss 融为单一 FIXED frame
```

接口点位说明：

- **frame ↔ step_band（核心）**：PRISMATIC，axis = incline 单位向量（由 Slot B 的 θ 派生），origin=(0,0,0)（世界轴，band 几何已建在斜面上）。行程 = 一个 step pitch = `hypot(STEP_DEPTH, STEP_RISE)`。twin spine 每 unit 一个独立 joint（`step_travel_{a,b}`），band 几何建一次、用 `Origin(xyz=(0,y_off,0))` 复用。
- **frame ↔ handrail**：FIXED，origin=(0,0,0)。handrail 坐在 Slot A 栏板顶缘（seated overlap，run_tests 内 element-scoped allow_overlap）。single spine 两个 part（left/right）；twin spine handrail 作为 truss 的 parent visual（`handrail_band_{a,b}`，焊接，无 joint）。
- **frame ↔ pit_cover（可选）**：REVOLUTE about +Y，origin 在 pit 上坡边 landing 顶面。closed pose 贴地（top z < LANDING_TOP_Z+0.06），开启抬起（+0.25 以上）。仅 Slot C=hinged 时存在。
- **twin spine 额外**：center_divider + cross_bracing 把两 side-truss + 两 balustrade 融成单一连通 FIXED `truss_frame` part；step rollers 嵌进 fixed guide_tracks（seated overlap）。

互斥/可选/派生关系：
- Slot B 的 θ 派生 incline axis（喂给 PRISMATIC + REVOLUTE）、truss 侧轮廓、step pitch (DEPTH,RISE)。
- Slot C=open_flush 时不产生 `pit_cover` part 与 REVOLUTE joint（可选 moving child 缺省）。
- 轴 D=twin 时 Slot A/C 走 twin-spine candidate，且 step_band/handrail/pit_cover 都 per-unit 复制。

## 每槽位 Module Emits / Interfaces

### Slot A / module tinted_glass_panel (single)
| emits | 描述 | 来源 |
|---|---|---|
| parts | （并入 frame parent visual）`balustrade_deck_left/right`, `glass_left/right`(+nose), `newel_left/right` | S1 / model.py:L234-L329 |
| internal joints | 无（栏板静止） | — |
| upstream interface | deck 横跨 skirt_inner→newel_outer，承载于 frame slab | S1 / model.py:L243-L269 |
| downstream interface | 玻璃顶缘 = handrail 落座面（seated overlap `left_rail`↔`glass_left`） | S1 / model.py:L407,L577-L590 |

### Slot A / module solid_metal_panel (single)
| emits | 描述 | 来源 |
|---|---|---|
| parts | frame parent visual：`balustrade_deck_*`, `panel_left/right`(brushed_metal+nose), `newel_*` | S2 / model.py:L235-L307 |
| downstream interface | 金属板顶缘 = handrail 落座面 | S2 / model.py:L407-L429,L577-L591 |

### Slot A / module smoked_glass_panel & dark_metal_panel (twin)
| emits | 描述 | 来源 |
|---|---|---|
| parts | per-unit truss visual `balustrade_left/right_{a,b}`，slab 下唇嵌入 side-truss | S3 / model.py:L144-L179, L513-L518 |
| downstream interface | 栏板顶缘承 handrail_band（焊接 parent visual） | S3 / model.py:L182-L243,L530 |

### Slot B / incline_geometry（所有 module）
| emits | 描述 | 来源 |
|---|---|---|
| parts | truss_body / side-truss + skirts（parent visual）；几何随 θ | S1 / model.py:L94-L136；S5 steep L43-L70；S6 shallow L44-L71 |
| internal joints | 无（θ 喂给 step_band PRISMATIC axis 与 pit_cover REVOLUTE 几何） | S1 / model.py:L43-L75 |
| upstream interface | truss 两端嵌入上下 landing slab（连通） | S1 / model.py:L117-L124 |
| downstream interface | incline axis `_incline_dir()` → PRISMATIC；step pitch (DEPTH,RISE) → step_band 摆放 | S1 / model.py:L73-L75,L513 |

### Slot C / hinged_pit_cover (single)
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pit_cover` part：`pit_cover_plate` + `hinge_knuckle_p/n`；frame 内 pit 切口 + `pit_box` | S1 / model.py:L453-L487,L143-L184 |
| internal joints | `frame_to_pit_cover` REVOLUTE +Y，lower=0 upper=1.4 | S1 / model.py:L542-L552 |
| upstream interface | 铰链 origin=(hinge_x,0,LANDING_TOP_Z) on landing 顶面 | S1 / model.py:L538-L548 |
| downstream interface | closed 贴 landing，open 露 pit_box | S1 / model.py:L718-L733 |

### Slot C / hinged_pit_cover (twin)
| emits | 描述 | 来源 |
|---|---|---|
| parts | per-unit `pit_cover_{a,b}`：`cover_plate`+`hinge_knuckles_moving`；fixed rim/recess/fixed knuckles 入 truss | S4 / model.py:L494-L584,L665-L685 |
| internal joints | `pit_hinge_{a,b}` REVOLUTE +Y，origin=(PIT_X_HINGE,y_off,FLOOR_Z)，upper=1.2 | S4 / model.py:L711-L734 |

### Slot C / open_flush_landing
| emits | 描述 | 来源 |
|---|---|---|
| parts | comb/floor plate 齐平（`landing_plates` twin / `lower_comb` single），无额外 part | S3 / model.py:L380-L422；steps7 L198-L208 |
| internal joints | 无（缺省可选 moving child） | — |

### step_band（multiplicity，所有 spine）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `step_band`(single) / `step_band_{a,b}`(twin)：N 个 tread+riser（+ single 连续 stringer / twin roller+axle+chain） | S1 / model.py:L335-L397；S7(parent B) L246-L324；S8(twinsteps14) L255-L324 |
| internal joints | 无（整带作为单一刚体由外部 PRISMATIC 驱动） | — |
| upstream interface | comb plate 与 band 底啮合（seated overlap）；twin：rollers 嵌 guide_tracks | S1 / model.py:L198-L208,L592-L599；S7 L344-L377 |
| downstream interface | 受 frame→step_band PRISMATIC 驱动沿斜面平移一个 pitch | S1 / model.py:L513-L524 |

### handrail（FIXED，所有 spine）
| emits | 描述 | 来源 |
|---|---|---|
| parts | single：`left_handrail`/`right_handrail` part；twin：`handrail_band_{a,b}` parent visual | S1 / model.py:L403-L447；S3 L211-L243,L530 |
| internal joints | FIXED（single：`frame_to_left/right_handrail`；twin：无 joint，焊接 parent visual） | S1 / model.py:L529-L536；S3 L582-L587 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `balustrade_style` | enum | {tinted_glass_panel, solid_metal_panel}(single) / {smoked_glass_panel, dark_metal_panel}(twin) | — | choice | 由 sampler 选；受 spine gate | Slot A 表 |
| `incline_geometry` | enum | {standard_30, standard_28_long, steep_35, shallow_22} | standard_30 | choice | 由 sampler 选；映射到 θ 标称档 | Slot B 表 |
| `landing_pit` | enum | {hinged_pit_cover, open_flush_landing} | hinged(single)/open(twin) | choice | 由 sampler 选；spine 决定 build 路径 | Slot C 表 |
| `unit_layout` | enum | {single, twin} | single | choice | multiplicity 轴 D；决定 spine 与 per-unit 复制 | parent A/B |
| `step_count` (N) | int | [4, 60] | 11(single)/16(twin) | independent | 加权抽样（小 N 高频）；clamp 到 [4,60] | multiplicity（见第 8 节） |
| `incline_angle` θ | float | [22°, 35°] | 由 incline_geometry 档定 | conditional | 范围由 enum 档解析；连续微扰 ±1.5° 后 clamp | S1 L43;S5 L43;S6 L44 |
| STEP_RISE | float | derived | 0.205~0.24 | equation | `= STEP_DEPTH · tan θ`（shallow 档显式如此）；保持踏步沿斜面 | S6 / model.py:L57-L58 |
| TRUSS_RUN / RUN | float | derived | — | equation | `= INCL_X0_margin + (N-1)·STEP_DEPTH + STEP_DEPTH + end_margin`（steps7/steps22 模式） | S7steps7 L60;S9steps22 L54 |
| TRUSS_RISE / RISE | float | derived | — | equation | `= TRUSS_RUN · tan θ` | S1 / model.py:L49 |
| `width_scale` | float | [0.9, 1.15] | 1.0 | independent | WIDTH/TREAD_WIDTH 等比缩放后 clamp；不破 skirt 间隙 | S1 L47,L54 |
| `balustrade_height_scale` | float | [0.9, 1.1] | 1.0 | independent | BALUS_H 缩放；handrail 高度随动 | S1 L60 |
| `palette_style` | enum | {brushed_steel_glass, dark_metal, warm_bronze, transit_white, stainless_smoked}（≥5） | brushed_steel_glass | choice | 仅改 material rgba，不改拓扑 | S1 L81-L89;S3 L486-L491 |
| (—) | constraint | — | — | inequality | step band y 半宽 ≤ TREAD_WIDTH/2 − skirt_gap（不蹭 skirt）；违反回缩 width_scale | S2parentB L432 |
| (—) | constraint | — | — | inequality | twin：两 band y 区间不相交（unit_gap>0.05）；违反加大 UNIT_GAP | S3 L711-L720 |
| (—) | constraint | — | — | inequality | step pitch 行程 = hypot(STEP_DEPTH,STEP_RISE)；PRISMATIC upper 恒等于此（不独立采样） | S1 L513,L522 |

palette 目标 4-6 colorway：`brushed_steel_glass`（浅灰 body+stainless+tinted glass，parent A）、`dark_metal`（dark_steel+smoked glass，parent B）、`warm_bronze`（暖青铜 body+琥珀玻璃）、`transit_white`（白 newel+冷玻璃，机场风）、`stainless_smoked`（亮不锈钢+烟灰玻璃）。共 5。

连续尺寸采样契约：先采 independent（width_scale, balustrade_height_scale, θ 微扰）→ 派生 equation（STEP_RISE, TRUSS_RUN, TRUSS_RISE）→ 投影 inequality（band 宽 vs skirt、twin band 不相交）→ conditional（θ 范围按 incline_geometry 档解析，N_range 不随 spine 变但 twin 标称偏大）。

## Multiplicity / Copy Logic

本类别有 **2 根独立 multiplicity 轴**。

### 轴 N — step band 踏步数（核心，category-defining）
- `count_param`：`step_count` (N) — incline 上 tread+riser 的数量。
- `N_range`：`[4, 60]`（产品域；样本覆盖 {7,11,14,16,22}，测试偏小、产品全程；远大于样本属正常）。
- sampling domain（权重档）：小 N 高频——N∈[6,16] 约占 ~70%（含标称 11/16），N∈[17,30] 约 ~22%，N∈[31,60] 约 ~8% 稀有尾部（大 N 由构造安全、sweep 稀疏采样）。N<6 仅作短梯边界保留 ~低频。
- copied object：one step = tread + riser（single 另有连续 side stringer 把所有 step 绑成一带；twin 另有 roller bracket + transverse axle + 2 guide wheels + 2 drive-chain bar）。
- naming：`step_i` 风格，发射进单一 `step_band` part 的一个 union visual（`step_treads` / `step_band_chain`），**不是** N 个独立 part。
- placement：沿 incline 等距，pitch=(STEP_DEPTH, STEP_RISE)；用共享 incline-dir helper；`for i in range(N)`：x=INCL_X0+0.10+i·STEP_DEPTH，z=INCL_Z0+i·STEP_RISE。
- joint policy：**每 unit 单一 PRISMATIC step-band joint**（不是每 step 一个 joint），axis=incline 单位向量，行程=一个 step pitch；handrail 永远 FIXED；pit cover 存在时 REVOLUTE +Y。
- source/gating：S1 L374-L391（single 循环）、S7 parentB L258-L299、S8 twinsteps14 L255-L321（显式 N + `_build_one_step` helper + RUN/RISE 派生）。N 改变时 TRUSS_RUN/RISE 必须按 equation 重派生（steps7 L60 / steps22 L54 / twinsteps14 L54-L55）以保证桁架包住全部踏步。

### 轴 D — unit 数量（single vs twin）
- `count_param`：`unit_layout` ∈ {single(=1), twin(=2)}（离散二值，非自由 K）。
- `N_range`：{1, 2}（real-world 扶梯几乎只见单台/并排双台；不开放任意 K，避免非法 spine）。
- sampling domain：single ~55% / twin ~45%（两 parent 各一条 spine，均衡）。
- copied object：整个 unit 的 step_band（+ pit_cover 若有）+ handrail + balustrade，按 `UNITS=(("a",+off),("b",-off))` 复制；fixed 几何 build 一次、用 `Origin(xyz=(0,y_off,0))` 复用以控编译开销。
- naming：`step_band_{a,b}`、`step_travel_{a,b}`、`pit_cover_{a,b}`、`pit_hinge_{a,b}`、`balustrade_*_{a,b}`、`handrail_band_{a,b}`。
- placement：镜像于 y=0，偏移 `UNIT_OFFSET=(WIDTH+UNIT_GAP)/2`；twin 加 `center_divider` + `cross_bracing` 融成单一 FIXED frame。
- joint policy：每 unit 各一条 PRISMATIC step joint；pit cover 存在时每 unit 各一条 REVOLUTE；joint 数随 D 倍增。
- source/gating：S3 parentB L83-L86,L536-L573；twin pit per-unit S4 L711-L734。twin 必须有 center_divider 否则两 truss 漂浮（兼容矩阵 gate）。

> 跨轴说明：N 与 D 各自独立加权采样、各自 clamp、各自编进 `slot_choices`、sweep 各自设上限（N≤60，D≤2）。跨轴共享 step helper（`_build_one_step`）待第二个 multiplicity 模板出现再抽，不提前抽象。

## 拓扑多样性审计

总组合数（按 spine 分别算 slot 笛卡尔积，再并入 N 采样档与 D）：
- single spine：A(2) × B(4) × C(2) = 16 slot 组合
- twin spine：A(2) × B(4) × C(2) = 16 slot 组合
- spine 合计 = 32 slot 组合；× distinct-N 等价类（保守取 5 档：{tiny<6, 6-16, 17-30, 31-45, 46-60}）= **32 × 5 = 160** distinct topology 组合（远 ≥10）。
- 若按样本实测 distinct N {7,11,14,16,22} 计：32 × 5 = 160；按 source map 口径 2×3×2×5=60 亦 ≥10 ✅。

理由：仅 slot 笛卡尔积（32）已远超 10；叠加 N 的 distinct 等价类（PRISMATIC step 数改变 part union 拓扑/joint 行程）与 D（joint 数倍增、center_divider 出现）后 slot choice tuple distinct ≥300。每个 candidate 都有真实 5★ 源，无臆造拓扑。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：`config_from_seed` 对普通 seed 做 deterministic 加权采样——先抽 `unit_layout`(D)，由 D gate 出可用 Slot A/C candidate 集合；再抽 incline_geometry(B)→解析 θ 与 step pitch；再抽 balustrade_style(A)、landing_pit(C)；再对 step_count(N) 做加权抽样并 clamp；最后采连续 scale（width/height/θ 微扰）并按 inequality 回缩。compatibility matrix（下表）gate 掉非法组合（如 single-spine 选了 twin balustrade module）。无 curated/modulo 主表。Topology target：1000-seed distinct 建议 按 ≥300 report-only 口径观察（本类别 160 组合上限支持）。少量 regression overrides 仅用于复刻两 parent + 8 variant 的已知良态（可选，非主域）。

Controlled local parameterization：`width_scale`[0.9,1.15]、`balustrade_height_scale`[0.9,1.1]、`incline_angle` 微扰 ±1.5°（conditional 于档）、`unit_gap_scale`（twin，[0.8,1.4]）。全部在 `resolve_config` clamp/派生：STEP_RISE=STEP_DEPTH·tanθ（equation），TRUSS_RUN/RISE 随 N、θ 派生（equation），band 宽 vs skirt 与 twin band 不相交为 inequality 回缩。这些 scale 不改 InterfaceSpec（PRISMATIC/REVOLUTE/FIXED origin 仍由 θ、y_off 确定）、不改 multiplicity、不改类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 D→gate slot→B(θ)→A→C→N(加权)→连续 scale；weighted choices | slot_choices_for_seed matches build choices |
| compatibility matrix | 见下；single↔twin candidate 互斥；open_flush 不建 pit part | no floating（twin 须 center_divider/cross_bracing）, collision（band vs skirt, twin band 相交）, axis（incline_dir 一致）, max multiplicity（N≤60,D≤2）, optional child（pit_cover 缺省合法） |
| controlled local variation | width/height/θ微扰/unit_gap scale + clamp | 比例变化不破 PRISMATIC/REVOLUTE origin、skirt clearance、handrail seating、step pitch 行程 |
| regression overrides | none（或可选：复刻 2 parent + 8 variant 良态，sparse） | previously良态 / reviewer-selected only |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 与 contract failures |

兼容矩阵（关键 gate）：

| spine D | 合法 balustrade A | 合法 landing_pit C | 备注 |
|---|---|---|---|
| single | tinted_glass_panel, solid_metal_panel | hinged_pit_cover(single), open_flush(single) | step_band/handrail/pit 单份；deck 承载玻璃/金属 |
| twin | smoked_glass_panel, dark_metal_panel | hinged_pit_cover(twin), open_flush(twin) | 须 center_divider+cross_bracing；step_band/handrail/pit per-unit；band 不相交 |
| 任意 | — | open_flush ⇒ 不生成 pit_cover part / REVOLUTE joint | 可选 moving child 缺省 |
| 任意 | — | hinged ⇒ closed pose 贴 landing（top z<LANDING_TOP_Z+0.06） | closed-pose 风险点 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A balustrade_style | 4 (2/spine) | yes | yes | 每 spine 2 |
| B incline_geometry | 4 | yes | yes | θ 档 + 连续微扰 |
| C landing_pit | 4 (2 家族×spine) | yes | yes | hinged / open_flush |
| D unit_layout (multiplicity) | 2 | yes | n/a | single/twin |
| N step_count (multiplicity) | 5 distinct 档 | yes | yes | [4,60] 加权 |

## Validator

- slot_choices_for_seed returns implemented module names（含 spine-gated A/C）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix gating 阻止 single↔twin candidate 错配、twin 缺 center_divider、band 相交
- optional regression overrides are sparse and justified（仅 parent/variant 良态）
- controlled local scale params clamped；不破 PRISMATIC/REVOLUTE origin、skirt clearance、handrail seating、step pitch 行程
- cross-part scale deps（STEP_RISE=DEPTH·tanθ；TRUSS_RUN/RISE 派生；band-vs-skirt / twin band-disjoint inequality）resolved in `resolve_config`
- 关键 InterfaceSpec：comb↔band seated overlap、handrail↔balustrade seated overlap、twin roller↔guide_track seated overlap 均存在
- 关键 joints：每 unit step_band = PRISMATIC，axis==incline_dir(θ)，upper==hypot(STEP_DEPTH,STEP_RISE)；handrail = FIXED 且 mimic is None；pit_cover（若有）= REVOLUTE about +Y，closed 贴地、open 抬起 >0.25
- copied objects 遵循 `step_band_{a,b}`/`pit_cover_{a,b}`/`pit_hinge_{a,b}` 命名与 ±UNIT_OFFSET 镜像 placement

## Reject cases

- step_band 不是 PRISMATIC，或 axis 不沿 incline（退化成静态楼梯 → 失去类别身份）。
- handrail 被建成可动 joint（应 FIXED 焊接；可动会脱离 newel 端）。
- twin 缺 center_divider / cross_bracing，两 side-truss 漂浮不连通。
- twin 两 step band 在 y 上相交（unit_gap 太小或 width_scale 过大）。
- N 改变后 TRUSS_RUN/RISE 未派生，踏步顶/底超出桁架或穿模 landing。
- pit_cover closed pose 不贴 landing（悬空）或开启不抬起（REVOLUTE 轴/origin 错）。
- balustrade module 与 spine 错配（single-spine 选 twin slab 模块，接口面不存在）。
- step band 宽超出 skirt 间隙，移动时蹭固定 skirt。

## 与相邻类别的边界

- 不该混入 **Elevator（电梯）**：电梯是竖直轿厢 PRISMATIC + 井道 + 滑门，无 incline truss、无沿斜面移动的 step band、无 handrail loop。escalator 必须有 incline + moving step band。
- 不该混入 **plain Stairs（静态楼梯）**：普通楼梯零 articulation；若产物没有 PRISMATIC step band、handrail 不是焊接 loop 语义、且无可选 pit cover，则不属本类别——moving step band 是 category-defining 运动，不可省。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- single 与 twin 是两条不同 root 几何 spine（solid-wedge truss vs side-truss+divider）。若实现时发现接口/坐标难以统一，按 README TEMPLATE_AFTER_REVIEW 优先在 `config_from_seed` 只采已实现稳定子域，或考虑拆 slug；首版建议两 spine 都实现但严格用 D gate 隔离 candidate。
- step helper（`_build_one_step`，twinsteps14 L255）可在两 spine 间共享；single 额外的连续 stringer 与 twin 的 roller/axle/chain 是 spine-local 附件。
- seated overlap 需 element-scoped allow_overlap：handrail↔balustrade（S1 L577-L590）、comb↔band（S1 L592-L599）、twin roller↔guide_track（S3 L613-L619）。
- twin fixed 几何务必 build 一次 + `Origin(xyz=(0,y_off,0))` 复用（S3 L495-L549）以控编译时间；大 N × twin 是 mesh-perf 风险点，必要时粗化 tessellation。
- pit_cover 在 single 与 twin 是不同 helper 路径（single S1 L453-L487 / twin S4 L494-L584），暂不合并。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/N/handrail | single spine 全栈 | rec_..._e7415cae (parent A) | L43-L552 | single truss+glass balustrade+step band+handrail+hinged pit |
| S2 | A | solid_metal_panel (single) | rec_escalator_var_metalpanel | L235-L307 | single 实心金属栏板 swap |
| S3 | A/B/C/N/handrail | twin spine 全栈 | rec_..._8388963a (parent B) | L43-L573 | twin side-truss+divider+roller step band+open flush |
| S4 | C | hinged_pit_cover (twin) | rec_escalator_var_pitcover | L494-L584,L711-L734 | twin per-unit 铰接 pit cover |
| S5 | B | steep_short_35deg | rec_escalator_var_steep | L43-L70 | 35° 陡梯几何 |
| S6 | B | shallow_long_22deg | rec_escalator_var_shallow | L44-L71 | 22° 缓梯几何（STEP_RISE=DEPTH·tanθ） |
| S7 | N | step multiplicity (single short) | rec_escalator_var_steps7 | L53-L74 | N=7，TRUSS_RUN 由 N 派生 |
| S8 | N/D | step multiplicity (twin explicit N) | rec_escalator_var_twinsteps14 | L50-L55,L255-L321 | N=14，RUN/RISE 由 N 派生 + `_build_one_step` helper |
| S9 | N | step multiplicity (single tall) | rec_escalator_var_steps22 | L48-L55 | N=22，TRUSS_RUN 由 N 派生 |
| S10 | A | smoked_glass_panel (twin) | rec_escalator_var_glasspanel | L488,L513-L518 | twin 玻璃栏板 material swap |
