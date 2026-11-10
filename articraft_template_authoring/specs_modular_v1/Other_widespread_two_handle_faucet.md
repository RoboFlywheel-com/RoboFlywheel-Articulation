# Modular Spec — widespread_two_handle_faucet

分体台面三件式双把手龙头（widespread / 8-inch spread three-piece deck-mounted two-handle
bathroom faucet）。中央出水嘴 + 左右两个独立阀门把手，三件分体安装在台面/台盆面上，
把手间距约 0.30 m。

## 元信息
| 项 | 值 |
|---|---|
| slug | `widespread_two_handle_faucet` |
| template path | `agent/templates/Other_widespread_two_handle_faucet.py` |
| test path (optional) | `tests/agent/test_widespread_two_handle_faucet_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel_children 三件挂同一 deck root + multiplicity 阀门工位固定 ×2） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 3 master 母资产 + 90 copy-pipeline 重画样本（叶 001/003/006 × v01..v30）|
| read_count | 3 master 全文精读 + 90 copy 全量指纹归一分类，关键代表（001/003/006 v01、001_v20、001_v22、003_v04、001_v05）逐行读 |
| read_scope | all 5-star master assets + all copy-pipeline redraws in this category |
| source_index_policy | only adopted module sources are indexed below |

> ⚠️ copy-pipeline 重画样本每条**自创部件命名**（`arm_x/arm_y`、`vertical_spokes`、
> `bridge_bar`、`knob_body` …），字面名不可信。下表所有候选按**几何/角色归一**采源，
> 优先引用 3 个 master 母资产的干净源码片段，copy 样本仅作为覆盖率与长尾佐证。

采纳源 ID：
- **M_BLK** = `rec_model-a-matte-black-widespread-three-piece-bathr_20260610_084038_412400_7c2230f2`
  （亚黑；圆法兰柱 + 摆动鹅颈嘴 + T-lever；deck=石材板）— canonical 圆柱族母资产。
- **M_CHR** = `rec_model-a-polished-chrome-three-piece-deck-mounted_20260610_084223_806738_0da22859`
  （抛铬 Art-Deco；方锥柱 + 瀑布板嘴(FIXED) + 顶部转向 finial + 四辐 cross 把手；deck=深色板）— canonical 方锥族母资产。
- **C_003v01** = `rec_qwen_widespread_two_handle_faucet_003_v01`（亚黑鹅颈+T-lever，带 stem_collar + 冷热 cap 盘）。
- **C_003v04** = `rec_qwen_widespread_two_handle_faucet_003_v04`（亚黑；柱身 `TorusGeometry` 装饰 ring ridge + deck 底 seam ring；cylindrical lever pedestal）— 外观环装饰真源。
- **C_001v05** = `rec_qwen_widespread_two_handle_faucet_001_v05`（`.polygon(6)` 六棱柱身截面）— 六棱 section 真源。
- **C_001v22** = `rec_qwen_widespread_two_handle_faucet_001_v22`（`Box((LEVER_W,LEVER_H,LEVER_LEN))` 扁条拨杆叶 + ring ridge pedestal）— 扁条 lever 叶形真源。
- **C_006v01** = `rec_qwen_widespread_two_handle_faucet_006_v01`（Art-Deco cross + 方锥 + diverter；含鹅颈与瀑布两形）。
- **C_001v01** = `rec_qwen_widespread_two_handle_faucet_001_v01`（抛金鹅颈 + 圆法兰柱）。
- **C_001v20** = `rec_qwen_widespread_two_handle_faucet_001_v20`（pull-down：鹅颈嘴绕**水平铰** `axis=(1,0,0)` 翻转的长尾形）。
- **M_WALL** = `rec_model-a-wall-mounted-bathroom-faucet-in-polished_…a684e234`（壁挂式）— **不在本域**，仅作邻类边界参考（见末节）。

## 核心身份

物理含义：台面安装、**三件分体**（中央出水嘴 + 两侧独立阀门把手），冷热分控双把手，
把手中心间距 ≈ 0.30 m（"widespread / 8-inch"）。所有件竖直立于台面（deck top, z=0 或 z=DECK_T），
出水嘴前伸（±Y）。每个把手绕自身竖直阀杆轴 REVOLUTE 旋转；中央出水嘴或整体摆动、或固定+顶部转向钮、
或下拉翻转。真实尺度（米），deck 底面落 z=0。

默认成熟域：deck 板 + 三根独立竖柱（中央 + 左右），中央嘴 1 件、阀门把手固定 2 件。
不混入：单孔单把手龙头（centerset/single-hole，阀体与嘴一体）、厨房抽拉花洒、壁挂式（嘴从墙体水平伸出，
见 M_WALL）、浴缸落地龙头。

## 槽位 + 候选模块表

### Slot A：deck_column_family（台面板 + 三柱-escutcheon 几何族 / 共享 root）

决定 deck root 与全部三根安装柱（中央 + 左右阀柱）的截面几何与法兰/底座样式。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| cylindrical_flange | M_BLK | deck L100-L106；中央柱 flange+column L108-L121；阀柱 flange+body L168-L182 | eligible if compatible | 圆 deck 板(Box) root + 每柱"圆法兰盘 Cylinder + 圆柱身 Cylinder"；轴对称；柱顶= joint 高度 |
| tapered_pyramid | M_CHR | `_pyramid_frustum` L77-L85；中央方锥+双阶方帽 L213-L233；阀柱 `_add_valve_column` 方锥+方帽+杆 L173-L195；deck 板 L204-L211 | eligible if compatible | Art-Deco 方锥 frustum(loft) 底座 + 方形 step-cap + 细 bonnet stem；非轴对称方截面 |

> 降级理由（只有 2 个候选）：90 样本归一后 deck/柱**真实结构二分**为"圆法兰柱 (44 条)"
> 与"方锥柱 (28 条)"两族；C_003 的 `stem_collar` 环 + 冷热 cap 盘只是圆柱族的
> **module-local 装饰变体**（叠环），不改截面拓扑，并入 cylindrical_flange 作为可选 collar/cap 细节，
> 不计第 3 候选。无第 3 种真实柱截面**结构**来源（六棱只是把同一圆柱身换截面 primitive，part tree/法兰/joint 不变，
> 归入外观子轴 AX-1，见专节），按 §2.3 折叠而非发明。

### Slot B：center_spout（中央出水嘴：几何 + 关节 bundle，挂中央柱顶）

每个候选是"嘴形 + 关节拓扑"的**绑定 bundle**（关节类型与嘴形耦合），共享上游接口=中央柱顶 mount。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| gooseneck_swivel | M_BLK | `_gooseneck_solid` 扫掠 L79-L88；嘴 part(tube+collar+aerator) L131-L153；`spout_swivel` REVOLUTE 竖轴 L155-L165 | eligible if compatible | 直立 riser + threePointArc 鹅颈 + 末端 aerator；整嘴绕**中央柱竖轴** REVOLUTE(±45°)；1 活动件 |
| waterfall_diverter | M_CHR | `_waterfall_spout` lofted slab L88-L111；spout_body FIXED L213-L245；`_oval_finial` L114-L124 + finial part L247-L260 + `diverter_spin` REVOLUTE L261-L271 | eligible if compatible | 宽扁瀑布板嘴（前伸~0.18 下落），嘴体 **FIXED**；顶部 oval finial 转向钮绕竖轴 REVOLUTE(±90°)；活动件=顶钮 |
| gooseneck_diverter | C_006v01 | `_gooseneck_spout` L90；嘴体 FIXED + diverter REVOLUTE L275 区块 | eligible if compatible | 鹅颈嘴体 FIXED + 顶部转向 finial 旋转；鹅颈与 diverter 共存的混族变体（leaf006 多见） |
| gooseneck_pulldown_tilt | C_001v20 | 嘴 part + `hinge_barrel` L281；REVOLUTE **水平轴** `axis=(1,0,0)` L302-L307；captured overlap L474 区 | eligible if compatible, low weight | 鹅颈嘴绕**水平铰**翻转（下拉/抬起），关节轴=X 而非 Z；长尾(~5 样本)，需 clearance gate 防嘴撞柱 |

### Slot C：valve_handle（阀门把手模块；×2 工位复制）

挂在每个阀柱顶端，绕竖直阀杆 REVOLUTE。两个工位（hot/cold）共用同一选定 module（同款左右镜像）。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| t_lever | M_BLK | `_t_lever` L184-L213（stem L187 / 横 T-bar L193-L198 / 两端 cap 球 L199-L205 / 指示点 L207-L212）；handle REVOLUTE L236-L250 | eligible if compatible | 竖 stem + 偏置水平 T-横杆（外伸）+ 端球 + 冷热指示点；绕竖轴 REVOLUTE(±90°)；at q=0 横杆沿 X，q=90° 沿 Y |
| cross_spoke | M_CHR | `_add_cross_handle` L127-L171（hub L132 / hub_dome L138 / 四辐 spokes L144-L157 / 端球 balls L158-L170）；handle_spin REVOLUTE L287-L297 | eligible if compatible | 圆 hub + 顶 dome + 四根径向辐条 + 端球（十字星把手，~0.09 tip-to-tip）；绕竖轴 REVOLUTE(±180°)；90° 对称 |

> 降级理由（只有 2 个候选）：归一后把手**真实结构二分** cross/spoke (~50 条) vs t_lever (~39 条)；
> 文本里出现的 "wheel" 全部是注释/`widespread` 误命中，无连续圆环 rim 真源（搜 `wheel/rim_ring/torus`
> 在**把手 part 内** 0 命中）。故不立 wheel 第 3 **结构**候选；幅数(4/5/6)与可选轮缘只改 cross 的
> 辐条复制数/装饰环，不改 part-tree 拓扑或 joint，归入外观子轴 AX-2（见专节）。
> `arm_x/arm_y`、`x_spokes/y_spokes` 均归入 cross_spoke。

## 槽位图（slot graph）

pattern: mixed（parallel_children + 固定 multiplicity ×2）

```
deck_root (Slot A: deck 板 + 三柱几何族)
  ├─[FIXED @ (0,0,deck_top)]──> center_column ──[Slot B 关节]──> center_spout
  │        (center_spout 内关节: gooseneck_swivel=REVOLUTE z; waterfall/gooseneck_diverter=
  │         嘴FIXED + finial REVOLUTE z; pulldown_tilt=REVOLUTE x)
  ├─[FIXED @ (-spread_half,0,deck_top)]──> hot_valve_column ──[REVOLUTE z, ±lim]──> hot_handle (Slot C)
  └─[FIXED @ (+spread_half,0,deck_top)]──> cold_valve_column ──[REVOLUTE z, ±lim]──> cold_handle (Slot C)
```

接口点位：
- deck_root → 每根柱：mating face = deck 顶面 (z=deck_top)，FIXED，柱底坐落于面（contact, 不漂浮）。
- center_column 顶 → center_spout：mount face = 柱顶圆/方面；riser/hub embed 进柱顶（captured，allow_overlap）。
  - gooseneck_swivel / pulldown_tilt：嘴 riser 直接 REVOLUTE 到柱顶（嘴=活动件）。
  - waterfall/gooseneck_diverter：嘴体 FIXED 到柱顶，顶部 finial 再 REVOLUTE（活动件=顶钮）。
- 阀柱顶 → handle：hub/stem 捕获阀杆 bonnet stem（captured-pin allow_overlap），REVOLUTE 竖轴。
- 对称面：YZ 平面（x=0），中央嘴居中，hot/cold 关于 x=0 镜像。

互斥/派生：Slot B 各候选的关节类型互斥（一个 center 只取一种）；Slot A 的柱截面同时决定中央柱与两阀柱
（三柱同族，派生而非独立采样）。外观子轴（AX-1..AX-5）叠在已选 Slot 之上，不新增 slot/关节（见专节）。

## 每槽位 Module Emits / Interfaces

### Slot A / cylindrical_flange
| emits | 描述 | 来源 |
|---|---|---|
| parts | deck_root(deck 板)、center_column(flange+column)、hot/cold_valve_column(flange+body) | M_BLK L100-L121, L168-L182 |
| internal joints | 无（柱为静态 parent visual；柱↔deck 为 FIXED 外接口） | — |
| upstream interface | deck root；柱底面坐落 deck 顶 (z=deck_top)，FIXED | M_BLK L123-L129, L221-L234 |
| downstream interface | 柱顶面 = center_spout/handle 的 mount + joint origin (z=col_top) | M_BLK L160, L245 |

### Slot A / tapered_pyramid
| emits | 描述 | 来源 |
|---|---|---|
| parts | deck_root(深色板)、center_column(方锥+双阶方帽)、阀柱(方锥+方帽+bonnet stem) | M_CHR L204-L233, L173-L195 |
| internal joints | 无（柱静态 parent visual） | — |
| upstream interface | deck root；柱底坐落 deck 顶 (z=0)，FIXED | M_CHR L239-L245, L277-L283 |
| downstream interface | 方帽顶面 / bonnet stem 顶 = center_spout/handle mount + joint origin | M_CHR L266, L292 |

### Slot B / gooseneck_swivel
| emits | 描述 | 来源 |
|---|---|---|
| parts | center_spout(swept 鹅颈 tube + swivel collar + aerator) | M_BLK L131-L153 |
| internal joints | `spout_swivel` REVOLUTE，axis=(0,0,1)，range ≈ ±π/4 | M_BLK L155-L165 |
| upstream interface | riser embed 进中央柱顶 bore（captured，allow_overlap） | M_BLK L276-L282 |
| downstream interface | aerator 出水口（末端朝前下） | M_BLK L70-L76, L145-L153 |

### Slot B / waterfall_diverter
| emits | 描述 | 来源 |
|---|---|---|
| parts | center_spout(方锥/瀑布 slab 嘴体, FIXED)、diverter_finial(stem+oval) | M_CHR L213-L238, L247-L260 |
| internal joints | `diverter_spin` REVOLUTE，axis=(0,0,1)，range ≈ ±π/2（嘴体本身 FIXED） | M_CHR L261-L271 |
| upstream interface | 嘴体 FIXED 到中央柱顶；finial stem embed 进方帽顶（allow_overlap） | M_CHR L239-L245, L332-L338 |
| downstream interface | 瀑布板前缘出水（~0.18 前伸下落）；finial 顶钮 | M_CHR L384-L395 |

### Slot B / gooseneck_diverter
| emits | 描述 | 来源 |
|---|---|---|
| parts | center_spout(鹅颈 tube, FIXED)、diverter_finial | C_006v01 L90, diverter L275 区 |
| internal joints | finial REVOLUTE z（嘴体 FIXED） | C_006v01 L275 区 |
| upstream/downstream | 同 waterfall_diverter，仅嘴形换鹅颈 | C_006v01 |

### Slot B / gooseneck_pulldown_tilt
| emits | 描述 | 来源 |
|---|---|---|
| parts | center_spout(鹅颈 + hinge_barrel) | C_001v20 L281 |
| internal joints | REVOLUTE **水平轴** axis=(1,0,0)，下拉/抬起 range（嘴=活动件） | C_001v20 L302-L307 |
| upstream interface | hinge_barrel 捕获柱顶铰销（captured，allow_overlap） | C_001v20 L474 区 |
| downstream interface | 鹅颈末端出水口（随铰翻转高度变化） | C_001v20 |

### Slot C / t_lever（×2 工位）
| emits | 描述 | 来源 |
|---|---|---|
| parts | handle(stem + 偏置 T-横杆 + 两端 cap 球 + 冷热指示点) | M_BLK L184-L213 |
| internal joints | 无内部关节；handle↔阀柱为 REVOLUTE 外接口 | — |
| upstream interface | stem embed 进阀杆 bore（captured，allow_overlap） | M_BLK L283-L290 |
| downstream interface | `hot/cold_lever_turn` REVOLUTE z，range ≈ ±π/2 | M_BLK L236-L250 |

### Slot C / cross_spoke（×2 工位）
| emits | 描述 | 来源 |
|---|---|---|
| parts | handle(hub + hub_dome + 四辐 spokes + 端球 balls) | M_CHR L127-L171 |
| internal joints | 无内部关节；handle↔阀柱为 REVOLUTE 外接口 | — |
| upstream interface | hub 捕获阀杆 bonnet stem（captured，allow_overlap） | M_CHR L318-L331 |
| downstream interface | `left/right_handle_spin` REVOLUTE z，range ≈ ±π | M_CHR L287-L297 |

## 参数范围汇总

> 连续 scale 范围已**拉满到样本测量的胖瘦/高矮跨度**（不再保守 ±15%）；新增的
> `column_radius_scale / column_taper_ratio / spout_arc_curvature_scale / spout_outlet_height_scale /
> handle_bar_thickness_scale` 把"柱径/锥度、嘴弧曲率/出水高、把手粗细"显式参数化。
> 末段 `*_appearance` 行为**外观子轴**（详见后专节），只做 parent.visual/装饰可视件，**不计入

| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| deck_column_family | enum | {cylindrical_flange, tapered_pyramid} | — | choice | deterministic procedural sampler；决定全部三柱结构族 | Slot A 表 |
| center_spout | enum | {gooseneck_swivel, waterfall_diverter, gooseneck_diverter, gooseneck_pulldown_tilt} | — | choice | sampler；关节拓扑随之绑定 | Slot B 表 |
| valve_handle | enum | {t_lever, cross_spoke} | — | choice | sampler；两工位共用同款 | Slot C 表 |
| palette_style | enum | {polished_chrome, matte_black, polished_gold_brass, brushed_nickel, oil_rubbed_bronze} | polished_chrome | choice | `rng.choice(PALETTE_STYLES)` | 见 palette 节 |
| valve_station_count | int | 固定 = 2 | 2 | constant | 类别定义；不暴露为可变 count | Multiplicity 节 |
| spread_half | float | [0.10, 0.19]（全展 0.20–0.38m，median 0.30） | 0.15 | independent | 阀柱中心 x=±spread_half；clamp ≥ 柱半径+把手半展+clearance | M_BLK L36；样本 0.10–0.19 |
| center_col_height_scale | float | [0.80, 1.35] | 1.0 | independent | 中央柱高 = base·scale（柱高拉满）；clamp 嘴出水口高于 deck | M_CHR L45 / 样本 COL_H 0.08–0.16 |
| valve_col_height_scale | float | [0.80, 1.25] | 1.0 | independent | 阀柱高 = base·scale | M_BLK L57 / 样本 0.05–0.14 |
| column_radius_scale | float | [0.80, 1.45] | 1.0 | independent | 三柱身径/方截面边长同比缩放（胖瘦）；阀柱径 = center·0.90 派生 | 样本柱径 R 0.012–0.036 |
| column_taper_ratio | float | [0.55, 0.95] | 0.75 | independent | 柱顶截面/柱底截面比（锥度）；pyramid 族偏低(0.55-0.75)、cylinder 族偏高(0.85-0.95) | M_CHR L38-39 (0.66) / L47-48 (0.57) |
| spout_reach_scale | float | [0.80, 1.45] | 1.0 | independent | 嘴前伸/弧长；clamp 不超 deck 前缘过多 | M_BLK L48 / 样本 ARC_R 0.05–0.16 |
| spout_arc_curvature_scale | float | [0.80, 1.30] | 1.0 | independent | 鹅颈弧曲率半径（与 reach 解耦：挺拔↔低塌）；瀑布族映射为下落弧度 | M_BLK L48, L68-69 |
| spout_outlet_height_scale | float | [0.85, 1.25] | 1.0 | independent | 出水口离 deck 高度；clamp 嘴最低点 z>0、且 ≤ 中央柱高+弧高 | M_BLK L338-L344 |
| handle_span_scale | float | [0.80, 1.30] | 1.0 | independent | 把手 tip-to-tip（cross 幅长 / lever 杆长） | M_BLK L64 / M_CHR L64 / 样本 0.075–0.12 |
| handle_bar_thickness_scale | float | [0.75, 1.40] | 1.0 | independent | 把手 T-杆 / 辐条 / hub 粗细（与 span 解耦） | 样本 BAR_R/SPOKE_R 0.0042–0.0095 |
| section_profile_appearance | enum(appearance) | {round, square, hexagonal} | family 派生 | choice(appearance) | 柱/嘴身截面 skin（AX-1）；不改 part tree/法兰/joint，不计 diversity | AX-1 / C_001v05 |
| cross_spoke_form_appearance | enum(appearance) | {4_spoke, 5_spoke, 6_spoke, spoked_rim} | 4_spoke | conditional(appearance) | 仅 valve_handle=cross_spoke 活动；辐数/可选轮缘环（AX-2） | AX-2 / M_CHR / 样本 range(6) |
| lever_blade_form_appearance | enum(appearance) | {round_rod, flat_strip, tapered_leaf} | round_rod | conditional(appearance) | 仅 valve_handle=t_lever 活动；拨杆叶形（AX-3） | AX-3 / M_BLK / C_001v22 |
| escutcheon_ring_appearance | enum(appearance) | {none, ring} | none | choice(appearance) | 每柱底座装饰环（AX-4）；×3 柱复制 | AX-4 / C_003v04 |
| collar_ring_appearance | enum(appearance) | {none, collar} | family 派生 | choice(appearance) | 中央嘴根 collar 环（AX-5） | AX-5 / M_BLK L138-143 |
| escutcheon_diameter_scale | float | [0.90, 1.50] | 1.0 | conditional | 仅 escutcheon_ring=ring 时活动；环外径 = 柱法兰径·scale | AX-4 |
| escutcheon_thickness_scale | float | [0.70, 1.60] | 1.0 | conditional | 仅 ring 时活动；环厚/凸起高 | AX-4 / C_003v04 SEAM_TUBE_R |
| collar_size_scale | float | [0.80, 1.40] | 1.0 | conditional | 仅 collar_ring=collar 时活动；collar 径/高 | M_BLK L50-51 |
| (—) | constraint | — | — | inequality | `spread_half ≥ valve_col_r·column_radius_scale + 0.5·handle_span·handle_span_scale + handle_clearance`（两把手互不撞、不撞中央嘴）；违反则回缩 handle_span_scale / column_radius_scale 或拒采 | 接口 / clearance |
| (—) | constraint | — | — | inequality | `spout_reach ≤ deck_depth/2 + overhang_max` 且 嘴下落最低点 z > 0（不穿 deck/不悬空过界）；spout_reach=base·spout_reach_scale，弧高随 spout_arc_curvature_scale·spout_outlet_height_scale 派生 → 回缩 | M_CHR L391-L395 |
| (—) | constraint | — | — | inequality | `column_taper_ratio·base_section ≥ mount_min`（柱顶截面须仍能容纳 riser/hub/stem 的 captured bore；锥度过强会掐断顶面 mount）→ 抬高 taper_ratio 下限 | 接口 mount |
| (—) | constraint | — | — | conditional | gooseneck_pulldown_tilt 时：翻转全程嘴体与中央柱保持 clearance（嘴弧半径/铰高随 tilt 上限派生 clamp） | C_001v20 |
| (—) | constraint | — | — | conditional | section_profile=hexagonal：六棱内切圆（flat-to-flat 半径）须 ≥ captured riser/stem bore 半径（faceting 后仍包住捕获销）；不足则放大 column_radius_scale | AX-1 |
| (—) | constraint | — | — | conditional | escutcheon_ring=ring：`escutcheon_diameter_scale·flange_r ≤ spread_half − adj_clearance`（相邻三柱底座环互不重叠）；超限则回缩 escutcheon_diameter_scale | AX-4 |

## Multiplicity / Copy Logic

**1 根 multiplicity 轴：valve_station_count，固定 N=2（不采样）。**

- `count_param`：valve_station_count（常量 = 2，不暴露为 `*_count` 可变参数）。
- `N_range`：固定 [2,2]。类别身份即"two-handle / 三件分体"，两个阀门工位（hot 左 / cold 右）恒定 2；
  非加权采样轴。83/90 样本显式两阀柱，其余 7 条用 loop 命名（仍为 2 工位）。
- sampling domain：无（常量）。
- copied object：每工位 = 1 个 valve_column(Slot A 派生) + 1 个 handle(Slot C 选定 module) + 2 个关节
  （deck→valve_column FIXED，valve_column→handle REVOLUTE 竖轴）。**外观子轴对单工位 handle/阀柱模板
  生效后再镜像复制到两工位**（两侧 escutcheon 环、把手辐数/叶形一致；指示色 hot/cold 不同）。
- naming：`hot_*` / `cold_*`（或 `left_*` / `right_*`）前缀；handle 同款左右镜像，指示色 hot=red、cold=blue。
- placement：x = ∓spread_half（hot=-X，cold=+X），y=0，柱底 z=deck_top；关于 YZ 对称面镜像。
- joint policy：两工位 handle REVOLUTE 各自独立（hot 与 cold 可独立旋转）；竖轴 (0,0,1)；
  range 按 module（t_lever ±π/2，cross_spoke ±π）。**外观子轴不得新增任何活动关节。**
- source/gating：M_BLK L215-L250（双阀 loop）、M_CHR L274-L297（左右 loop）。

> 中央出水嘴**不是** multiplicity 轴（恒 1 件），由 Slot B 单选。

## 外观细节子轴（appearance sub-axes，不计拓扑）

> 这些子轴只为输出**真实视觉多样性**：每条仅作用在 **parent.visual 造型** 或 **静态装饰可视件**
> 它们与 16 个结构组合**叉乘**叠加视觉变化；其连续尺寸由 §7 的 `*_scale`/conditional 行 clamp。
> 采样：在 `config_from_seed` 里各做一次独立加权抽取（与结构 enum 同级、但单独标 `appearance=True`）。

### AX-1 — 柱/嘴身截面 profile：`{round, square, hexagonal}`
- **候选 & 样本支撑**：
  - `round`：圆柱身 — M_BLK `Cylinder` 柱身/riser（L117, L177, TUBE_R）。cylindrical_flange 族默认。
  - `square`：方锥身 — M_CHR `_pyramid_frustum`（L77-85）方截面 loft。tapered_pyramid 族默认。
  - `hexagonal`：六棱柱身 — `.polygon(6)` 真源（C_001v05 等共 **11 处** `polygon(6)` 命中），把柱身/嘴 riser
    截面换成正六边形棱柱。
- **几何做法**：section_profile 只替换**柱身 / 嘴 riser 的拉伸截面 primitive**（Cylinder→正六棱 prism 或方棱），
  法兰盘/方帽/joint origin/captured bore 不变。`round`/`square` 为对应 Slot A 族的默认值；`hexagonal` 作为
  可叠加的 faceting 值，对**任一**族都可施加（圆→六棱、方→倒角六边）。受 §7 conditional：六棱内切圆须包住捕获销。
- **不改拓扑理由**：part tree、visual 数量、joint 完全不变，仅换截面 primitive 形状。

### AX-2 — cross 手轮辐/缘式样：`{4_spoke, 5_spoke, 6_spoke, spoked_rim}`（仅 valve_handle=cross_spoke）
- **候选 & 样本支撑**：
  - `4_spoke`：四辐十字 — M_CHR `_add_cross_handle` spoke_dirs 4 项（L144-157）。默认。
  - `5_spoke`：五辐 — 在 4 辐复制循环里把方向表改为 5 等分（角度 = 2π·i/5）；插值于样本 range(4)/range(6) 之间。
  - `6_spoke`：六辐 — 样本 `range(6)` 辐条复制真源（spoke loop 6 等分）。
  - `spoked_rim`：辐条 + 外圈轮缘环 — 在辐尖半径处加一圈 `TorusGeometry` 轮缘（环本身是本类别**高频装饰词汇**：
    C_003v04 `ring_ridge`/`seam` torus L122-127, L162-165, L231-234 等 22 文件用 torus 装饰环），把端球替换/补成连续 rim。
    ⚠️ 诚实标注：样本里 torus 环只用作柱身 ridge/deck seam，**未**见装在把手辐尖；此候选 = 把同款 torus 环
    挪到把手辐尖半径，**低权重**采样。
- **几何做法**：只改 spoke 复制数（循环 N 等分）与可选外圈 torus rim 的 visual；hub/dome/joint/REVOLUTE 全不变。
  幅长由 `handle_span_scale`、辐粗由 `handle_bar_thickness_scale` 控制。
- 单工位生效 → 镜像复制到 hot/cold 两工位（两侧同式）。

### AX-3 — t_lever 拨杆叶形：`{round_rod, flat_strip, tapered_leaf}`（仅 valve_handle=t_lever）
- **候选 & 样本支撑**：
  - `round_rod`：圆杆横杆 + 两端球 — M_BLK `_t_lever` `Cylinder` bar + Sphere caps（L193-205）。默认。
  - `flat_strip`：扁条叶片 — `Box((LEVER_W, LEVER_H, LEVER_LEN))` 真源（C_001v22 L223-227，扁平拨片）。
  - `tapered_leaf`：锥叶（根粗尖细的锥形拨叶）— 用 loft 从根截面渐缩到尖截面（沿用 `_waterfall_spout`/frustum loft
    手法 M_CHR L88-111 / L77-85 作为 loft 技法支撑），把圆杆换成锥形叶片。
- **几何做法**：只替换 T-横杆/拨叶的 visual primitive（Cylinder↔Box↔loft），stem/captured bore/REVOLUTE/指示点不变。
  杆长由 `handle_span_scale`、厚度由 `handle_bar_thickness_scale` 控制。
- 单工位生效 → 镜像复制到 hot/cold 两工位。

### AX-4 — 每工位 escutcheon 底座环：`{none, ring}`（×3 柱复制）
- **候选 & 样本支撑**：
  - `none`：素法兰/方锥底，无环 — M_BLK 圆法兰、M_CHR 方锥底（无装饰环）。默认。
  - `ring`：柱底/法兰顶一圈装饰环 — `TorusGeometry` seam/base ring 真源（C_003v04 deck-base `*_seam` ring
    L162-165, L231-234；**62 文件**含 escutcheon/base-ring/seam 词汇）。
- **几何做法**：在每根柱（中央 + 两阀，共 3）底座法兰顶面加一圈 torus 装饰环 visual；环外径/厚由
  §7 conditional `escutcheon_diameter_scale`/`escutcheon_thickness_scale` 控制，受相邻三柱不重叠 inequality clamp。
  不改柱 part tree/joint。

### AX-5 — 嘴根 collar 环：`{none, collar}`（中央嘴 only）
- **候选 & 样本支撑**：
  - `collar`：嘴根 swivel collar 环 — M_BLK `swivel_collar` `Cylinder(COLLAR_R, COLLAR_H)`（L138-143）；
    C_003 `stem_collar`。gooseneck 族常见。
  - `none`：无根环（瀑布板嘴直接出柱）— M_CHR waterfall 嘴无根 collar。
- **几何做法**：在中央嘴 riser 根部加一段短 collar（Cylinder 环或 torus），径/高由 `collar_size_scale` 控制；
  对 gooseneck_* 族默认偏向 `collar`、对 waterfall 偏向 `none`（compatibility 偏好，非硬绑）。collar 随嘴体/嘴关节
  归属同一 part，不新增 joint。

> **复制语义**：AX-2/AX-3/AX-4 作用在**单工位** handle/阀柱模板上，再随 ×2 multiplicity 镜像到 hot/cold
> 两工位（两侧式样一致，仅冷热指示色不同）。AX-1 由一次抽取派生到全部三柱+嘴 riser。AX-5 仅中央嘴。
> 全部子轴**零新增关节**。

## 拓扑多样性审计

总组合数（**结构层**）：A × B × C = 2 × 4 × 2 = **16**（valve_station_count 固定 ×2 不增组合数）。
经 compatibility gating（见下）后净 distinct ≈ **14**（保守，去掉若干弱配对）。

**外观层不计入拓扑**：AX-1(3) × AX-2(4, 仅 cross) × AX-3(3, 仅 lever) × AX-4(2) × AX-5(2) 只改
parent.visual 造型/装饰可视件与连续比例，**part tree 与 joint 完全不变**，因此**不进入
在视觉上呈现大量不同实例**（截面 圆/方/六棱、辐数 4/5/6/带缘、拨叶 圆杆/扁条/锥叶、底座环有无、嘴根环有无、
连续胖瘦高矮）。

理由：handle{lever,cross} × center_spout{4 关节-绑定形} × deck{圆/方} 三轴均为真实结构/关节拓扑变化
（part tree、joint type/axis 不同），交叉后 ≥14 distinct，远超 10；外观子轴另在每个 distinct 之上叠加视觉变化。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 用 `ctx.rng` 对三个**结构** enum 做加权 deterministic
采样（handle、center_spout 近均匀；deck 近均匀），再对**外观子轴**各做一次独立加权抽取（标 `appearance=True`），
再独立采各连续 scale → 按 inequality 投影回缩（spread/handle_span/spout_reach/column_radius/taper/escutcheon）。
compatibility matrix 排除穿模/自撞组合及非法外观配对（六棱内切圆 vs 捕获销、底座环互不重叠）。无 curated/modulo
主表；`seed=0` 不特殊。少量 regression override 仅在出现已知失败回归时按 seed 记录。
Topology target：1000-seed **topology** distinct 上限为 16（枚举型小域，连续 scale 与外观子轴不计入拓扑等价类），（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
低于 300 的原因=本类别真实**拓扑**组合数本就 ≤16（三件式龙头结构家族有限），符合 §9 例外说明；视觉实例多样性
则远高于 16（外观层叉乘）。
Controlled local parameterization：spread_half、center_col_height_scale、valve_col_height_scale、
column_radius_scale、column_taper_ratio、spout_reach_scale、spout_arc_curvature_scale、spout_outlet_height_scale、
handle_span_scale、handle_bar_thickness_scale，以及 conditional 的 escutcheon_diameter/thickness_scale、collar_size_scale
（范围见第 7 节）。全部按 §7 约束类型采样 + clamp；跨件依赖（双把手互不干涉、嘴不穿 deck、tilt 全程 clearance、
锥度保 mount、六棱包销、底座环不重叠）以 inequality/conditional 行在 `resolve_config` 求解，不留到 builder。
这些 scale 与外观子轴只改安全比例/装饰/截面 skin，不改 enum 结构选择、阀门 ×2 或接口语义。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 三结构 enum 加权采样 + 5 外观子轴独立加权 + 各 scale independent 采样；slot_choices_for_seed 返回 (deck,spout,handle) 与外观维度 | slot_choices_for_seed 与 build 选择一致；外观维度记录但不计 distinct |
| compatibility matrix | waterfall_diverter 偏好 tapered_pyramid（Art-Deco 身份）；gooseneck_pulldown_tilt 低权重且必须过 tilt-clearance gate；spoked_rim 低权重；外观配对受 §7 conditional gate（六棱包销、底座环不重叠、collar 族偏好）；其余组合合法 | 无漂浮/穿模/自撞、关节轴正确、closed pose 合法、外观件不新增关节 |
| controlled local variation | 10 个主 scale + 3 个 conditional scale + clamp/inequality 回缩 | 比例/截面/装饰变化不破接口/clearance/joint origin/类别身份 |
| regression overrides | none（除非 sweep 暴露具体失败 seed，届时按 seed+原因记录） | 仅已知失败回归 |
| random sweep | 初轮 seeds 0-49；成熟审计 0-999 | 、外观件零关节、contract 失败 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A deck_column_family | 2 | yes | no | 真实柱**结构**二分；collar/cap/六棱为 module-local/外观，无第 3 真**结构**源（已降级说明） |
| B center_spout | 4 | yes | yes | 嘴形×关节绑定 bundle |
| C valve_handle | 2 | yes | no | cross vs lever；无 wheel 真**结构**源（已降级说明） |
| AX-1 section_profile（外观） | 3 | yes | yes | 圆/方/六棱 截面 skin；不计拓扑 |
| AX-2 cross_spoke_form（外观，cross only） | 4 | yes | yes | 4/5/6 辐 + 轮缘；不计拓扑 |
| AX-3 lever_blade_form（外观，lever only） | 3 | yes | yes | 圆杆/扁条/锥叶；不计拓扑 |
| AX-4 escutcheon_ring（外观） | 2 | yes | no | 底座环 有/无；不计拓扑 |
| AX-5 collar_ring（外观） | 2 | yes | no | 嘴根环 有/无；不计拓扑 |

## Validator

- slot_choices_for_seed returns implemented module names（deck, center_spout, handle）+ 外观维度（标 appearance）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combos（tilt-clearance、waterfall↔pyramid 偏好、六棱包销、底座环不重叠）
- optional regression overrides are sparse and justified
- final template does not endlessly cycle a small curated table as the main seed domain
- controlled local scale params clamped；不破接口/clearance/joint origin/×2 multiplicity
- cross-part scale deps（spread vs handle_span vs column_radius、spout_reach vs deck、taper vs mount、六棱内切 vs bore、
  escutcheon diam vs spread、tilt clearance）resolved in `resolve_config`
- **外观子轴零新增关节**：施加 AX-1..AX-5 后 articulation 数量与 baseline 完全一致（only deck-FIXED ×3 + spout 关节 + handle REVOLUTE ×2）
- 关键 InterfaceSpec/MatingContract 存在：三柱坐落 deck 顶（contact，非漂浮）、riser/hub/stem captured-pin allow_overlap；六棱/方截面后捕获销仍被包住
- key joints type/axis/range：两 handle REVOLUTE z（独立）；center_spout 关节按 module（swivel z ±π/4 / diverter z ±π/2 / tilt x）
- copied objects（两阀工位）遵循 hot/cold 命名、x=±spread_half placement、红/蓝指示色；外观式样左右一致
- 把手旋转有效性：pose 后把手 AABB-center 位移 > 阈值（cross 90° 对称，用 45° pose）
- 三件 widespread 间距：两 handle x 间距 ∈ [0.29, 0.31]·spread_scale，中央嘴居中 x≈0
- escutcheon_ring/collar_ring 存在时：装饰环 visual 出现且径/厚在 conditional 范围内，相邻底座环不重叠
- section_profile=hexagonal 时：柱身截面为 6 棱且内切圆 ≥ 捕获销半径

## Reject cases

- 阀门工位 ≠ 2（单把手或 3+ 把手）— 违反 two-handle 身份。
- 中央嘴与阀体一体/共柱（centerset / single-hole）— 非分体三件。
- 把手与中央嘴/另一把手碰撞（spread 太小或 handle_span/column_radius 太大未回缩）。
- 出水嘴穿透 deck、嘴最低点 z ≤ 0，或嘴漂浮（riser 未 embed 进柱）。
- handle/finial 关节缺失或轴错（应竖轴 REVOLUTE；tilt 例外为水平轴）；嘴体 FIXED 却给了旋转嘴的活动语义。
- 把手 hub/stem 未捕获阀杆而悬空（缺 captured allow_overlap → 断件/漂浮）；六棱/方截面或锥度过强掐断顶面 mount 致捕获销外露。
- gooseneck_pulldown_tilt 翻转全程嘴撞中央柱（未过 tilt-clearance gate）。
- 把手左右不镜像、冷热指示色错置（hot 蓝/cold 红）；外观式样左右不一致。
- 误把 wheel/连续圆环 rim 当 cross **结构**实现；或外观子轴新增了活动关节（外观件必须静态/随宿主件）。
- escutcheon 底座环互相重叠（escutcheon_diameter_scale 未受 spread clamp）。

## 与相邻类别的边界

- 不该混入：single-hole / centerset 单把手龙头（阀体与嘴共底座，单把手控混水；本类必须三件分体 + 双把手）。
- 不该混入：wall-mounted faucet（M_WALL：嘴/阀从竖直墙面水平伸出，VALVE_PITCH 0.10、yaw=π 安装；本类为台面竖立、spread 0.30）。
- 不该混入：厨房抽拉花洒 / 高拱厨房龙头（单把手、可拉出软管、无冷热分体双柱）。
- 不该混入：浴缸落地式龙头（落地高柱 + 手持花洒）。

## palette_style 颜色轴

`PALETTE_STYLES`（目标 5，≥3 满足）。每 style 给 metal 主色 + deck 色；红/蓝冷热指示为全 style 共享 accent。

| palette_style | metal rgba | deck rgba | 来源 |
|---|---|---|---|
| polished_chrome | (0.88, 0.89, 0.92, 1.0) | charcoal (0.09, 0.09, 0.10, 1.0) | M_CHR L201-L202 |
| matte_black | (0.07, 0.07, 0.07, 1.0) | stone (0.80, 0.79, 0.76, 1.0) | M_BLK L94-L95 |
| polished_gold_brass | (0.85, 0.66, 0.20, 1.0) | stone/charcoal | C_001v01 / M_WALL `polished_gold` |
| brushed_nickel | (0.66, 0.67, 0.68, 1.0) | stone | 由 chrome_accent (0.75,0.75,0.78) 调暗合成 |
| oil_rubbed_bronze | (0.20, 0.13, 0.09, 1.0) | stone | 合成（深古铜，常见龙头饰面）|

共享 accent：hot_red (0.78, 0.08, 0.08, 1.0)、cold_blue (0.10, 0.25, 0.82, 1.0)（指示点/冷热 cap 盘）。
来源 M_BLK L96-L97。deck 色可与 metal 独立小幅采样（light stone / dark charcoal 两档）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待审。重点确认：(1) Slot A/C 各 2 候选的降级理由是否接受；(2) center_spout 把"嘴形×关节"绑成 4 bundle 是否合理（替代方案=拆成 spout-geo 2 × articulation 3 两个 slot）；(3) gooseneck_pulldown_tilt 长尾(~5 样本)是否纳入 seed domain 还是降为 regression-only；(4) **新增外观层**：5 个外观子轴（AX-1 截面 圆/方/六棱 · AX-2 cross 辐 4/5/6/带缘 · AX-3 lever 圆杆/扁条/锥叶 · AX-4 底座环有无 · AX-5 嘴根 collar 环有无）均仅作 parent.visual/装饰件、零新增关节、不计 diversity，是否接受其支撑（尤其 spoked_rim 与 tapered_leaf 为低权重/loft 合成，无逐字把手真源，已诚实标注）；(5) 连续 scale 已拉满到样本胖瘦/高矮跨度并新增 column_radius/taper/arc_curvature/outlet_height/bar_thickness/escutcheon/collar 等参数，范围是否合理。|

## 模板实现备注（可选）

- 共享 helper：`_pyramid_frustum`（M_CHR L77-L85）、`_gooseneck_solid`（M_BLK L79-L88）、
  `_waterfall_spout`（M_CHR L88-L111）、`_oval_finial`（M_CHR L114-L124）。三柱（中央+两阀）由 Slot A
  同一 column factory 派生，仅尺寸不同（中央柱更高/更粗）。section_profile 在 column factory 内做截面 primitive
  切换（Cylinder / 方 frustum / `.polygon(6)` 棱柱）；tapered_leaf 用 frustum/loft helper 复用。
- 外观件均为静态 parent.visual 或装饰 visual，**禁止**新增 articulation；torus 装饰环参 C_003v04
  `TorusGeometry` 用法（ring ridge/seam）。
- captured-pin allow_overlap 需 element-scoped：riser↔center_column、hub/stem↔valve bonnet stem、
  finial_stem↔cap、hinge_barrel↔柱顶铰销（参 M_BLK L276-L290、M_CHR L318-L338、C_001v20 L474 区）；
  施加六棱/方截面后须复核捕获销仍被柱顶 mount 包住（§7 conditional）。
- 两阀工位为固定 ×2 loop（参 M_BLK L215-L250、M_CHR L274-L297）；外观式样在单工位生效后镜像复制。
- 若 reviewer 选"拆 spout-geo / articulation 两 slot"，则 Slot B → {gooseneck, waterfall} × {swivel_z,
  fixed_diverter, pulldown_tilt}，由 compatibility matrix gate 合法配对；当前默认绑定为 4 bundle 以降风险。
