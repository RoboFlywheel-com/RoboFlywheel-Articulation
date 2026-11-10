# Modular Spec — high_arc_gooseneck_faucet

## 元信息
| 项 | 值 |
|---|---|
| slug | `high_arc_gooseneck_faucet` |
| template path | `agent/templates/Other_high_arc_gooseneck_faucet.py` |
| test path (optional) | `tests/agent/test_high_arc_gooseneck_faucet_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（serial backbone：deck base → column → swivel gooseneck → outlet head；parallel children：handle(s) + control 挂到 column；multiplicity：handle 数 N∈{1,2}） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 62（60 copy 叶 `rec_qwen_high_arc_gooseneck_faucet_002_v01..v30` + `_007_v01..v30`，外加 2 母资产 `rec_model-a-brushed-gold-single-hole-kitchen-faucet-*`、`rec_model-a-gloss-black-monobloc-kitchen-mixer-tap-a*`） |
| read_count | 62（2 母资产逐行精读；60 copy 用结构指纹脚本归一 + 抽样精读 002_v05/v15、007_v04/v18/v25；视觉细节层补读 002_v06/v08、007_v18/v25） |
| read_scope | all 5-star samples in this category（全部 rating=5） |
| source_index_policy | only adopted module sources are indexed below |

**关键阅读结论（这批源的特殊性已核实）：**

1. copy-pipeline 每条自己发明部件命名（`mixer_housing` / `pre_rinse_spring` / `ribbed_sleeve` / `flow_knob` / `escutcheon` / `pedestal_step_*` …），**字面名不可信**。所有候选按几何/角色归一。line-span 写真实 `model.py:Lx-Ly`。
2. **不是离类**：002_v05/v18、007_v12/v25 等都是真·高弧鹅颈（倒-U `threePointArc` sweep，apex 0.38–0.45 m，绕立柱 Z 轴 swivel）。被指纹成「无 spout 」的少数其实是 pull-down/pre-rinse（弧由 riser + 下挂 head + 弹簧构成），不是直嘴。
3. 两条母资产代表两个真实家族：
   - **母 A（002, brushed-gold single-hole）**：锥形渐变立柱 + 单侧 mixer 拨杆 + 2 段伸缩下拉花洒（prismatic + Mimic）+ 触控屏 + 拨盘旋钮。
   - **母 B（007, gloss-black monobloc）**：圆柱立柱 + 铬底盘 + 横贯立柱的十字阀体 cross-tube（双 pin 拨杆，热/冷双工位）+ 固定铬嘴起泡器 + 纯手动。
4. **高弧鹅颈倒-U 弧嘴 + 立柱 + 绕 Z swivel 是该类身份固定特征，不作可变 slot。** 拓扑多样性全部来自 handle / outlet head / control 三层 + handle 多重数 N。
5. **视觉细节层在样本里真实大量存在且与拓扑解耦**：鹅颈管表面有「光面 / 缠绕弹簧(pre-rinse spring) / 罗纹套(ribbed sleeve)」三态（007_v18 helical 弹簧 helper、002_v06 周向凹槽切罗纹）；喷头 head body 有「光锥 / 罗纹桶 / 阶梯柱」三种 loft 截面（大量 copy「ribbed spray head」alternating ridge/valley loft）；handle/旋钮握感有「光面 / 直纹(fluted) / 罗纹(ribbed)」（`KnobGrip(style="fluted"/"ribbed")`）；底座有「无环 / 铬颈环 / escutcheon 盘」（007_v25 chrome collar ring + 0.055 m escutcheon）。这些**都不新增任何活动关节**，是 parent.visual 造型或焊接装饰可视，故全部归入下方「视觉细节 / 外观变化层」，**不计入拓扑等价类**。

## 核心身份

高弧鹅颈龙头 / pre-rinse 厨房水龙头：单孔台面安装（deck plane z=0），立柱沿 +Z 升起，顶端经 swivel collar 接一根**高耸的倒-U（swan-neck）鹅颈管**——直 riser → 半圆 `threePointArc` 高弧 → 短下挂 drop leg，弧顶 apex 落在 z≈0.36–0.50 m，水平 reach（+X，伸向水槽）≈ 0.12–0.20 m。鹅颈整体绕**立柱垂直轴 swivel**（REVOLUTE，±60°–±110°）。出水端（outlet head）要么是固定铬嘴 + 起泡器，要么是 2 段伸缩**下拉花洒**（PRISMATIC + Mimic）。控水由立在阀体上的**细 pin 拨杆**（REVOLUTE 绕水平 Y 轴，竖直↔前倾）完成，单工位（mixer）或双工位（热/冷）。可选**触控屏 + 拨盘 / 旋钮**电子控制。

默认成熟域：高弧、可绕轴 swivel、可控水的厨房龙头；apex≥0.36 m 的高拱是身份核心。

**不该混入：** 矮直嘴台盆龙头（apex 低、无高拱）；墙挂式龙头（无立柱、台面接口完全不同——见 §11）；纯装饰摆件。

## 槽位 + 候选模块表

> 命名约定：源以 `Lx-Ly` 指 `revisions/rev_000001/model.py`。母 A=`rec_model-a-brushed-gold-single-hole-kitchen-faucet-_20260610_084005_029915_7b6c63f8`，母 B=`rec_model-a-gloss-black-monobloc-kitchen-mixer-tap-a_20260610_084301_301855_c023a523`。copy 简写 `002_vNN` / `007_vNN`。

### 固定 backbone（非 slot）：BASE + COLUMN + GOOSENECK + SWIVEL
身份骨架，所有 slot 挂在它上面，不进入采样枚举。
- 立柱有 module-local 变体 `column_form ∈ {tapered_cone, cylindrical_disc}`，**由 handle_form 派生**（cross→`cylindrical_disc`+铬底盘；lever→二者皆可），仅改 visual primitive（loft 锥 vs cylinder+disc），不改拓扑，故不单列 slot。
- 鹅颈 = `threePointArc` sweep（riser→高弧→drop leg）+ swivel REVOLUTE 绕 Z。来源：母A `L85-L107,L136-148,L184-201`；母B `L86-L95,L106-119,L139-145,L147-176`。

### Slot A：handle_form（阀体/拨杆几何形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `side_lever` | 母A | L67-L74 + L261-L291 | eligible if compatible | 立柱侧/顶一个圆柱 valve boss，其上立一根细 pin 拨杆；拨杆 REVOLUTE 绕水平 Y 轴（boss 嵌入立柱 mount boss，captured-pin overlap）。part 树 = column(parent) + `pin_lever`(child)。 |
| `side_lever` (alt) | 007_v18 | L205-L211 + L267-L303 | eligible if compatible | 同形态独立实现：`lever_mount_boss` + 单 `side_lever`，REVOLUTE axis=(0,-1,0)；证实 single-lever 在 007 家族单立柱上也成立。 |
| `cross_tube` | 母B | L120-L138 + L178-L207 | eligible if compatible | 横贯立柱的水平十字阀缸（cross-tube，±Y 跨 0.18 m，两端 matte 端盖），其顶部升起两根 pin 拨杆；每杆独立 REVOLUTE 绕 Y。part 树 = column(含 cross_tube visual) + `pin_lever_0/1`(children)。**双工位（热/冷）。** |
| `cross_tube` (alt) | 007_v25 | L182-L194 + L271-L294 | eligible if compatible | 同形态 + `escutcheon`/`pedestal_step` 装饰底座 + `deck_plate`(FIXED) + 双 `pin_lever` 循环复制；可作 cross 形 control-rich 变体参考。 |

> Slot A 取 2 个结构不同候选（lever vs cross），满足 ≥2。两者 part 树 / joint 拓扑显著不同（侧 boss 单杆 vs 横缸双杆）。

### Slot B：outlet_head（出水端）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `pull_down_spray` | 母A | L110-L124 + L203-L259 | eligible if compatible | 2 段伸缩下拉花洒：`hose_stem`(sleeve) + `spray_head`(loft 锥头 + nozzle + spray_button + inner_hose)。两条 PRISMATIC（spray_pulldown + hose_slide），hose_slide 用 `Mimic(spray_pulldown, 1.0)` 联动；总行程 0.12 m。新增 2 part + 2 prismatic joint。captured telescoping overlap 需 elem-scoped allow_overlap。 |
| `fixed_aerator` | 母B | L75-L79 + L147-L165 | eligible if compatible | 固定铬 tip sleeve + 下出水 outlet_aerator 暗环，无 joint，焊在鹅颈 drop-leg 末端（spout 自身 visual）。part 数不增、joint 不增。 |
| `fixed_aerator` (pre-rinse alt) | 007_v18 | L103-L149 + L227-L251 | eligible if compatible | pre-rinse 变体：`pre_rinse_spring`（外缠弹簧 helper）+ 下挂 `spray_head` 固定头；视觉上是商用 pre-rinse 但出水端无活动 joint（弧由 riser+head 构成）。**该 pre-rinse 弹簧已降为 `gooseneck_surface` 视觉子轴的一个值**（见 §视觉细节层），不再作拓扑分叉。 |

> Slot B 取 2 个结构不同候选（带 2 prismatic 的活动下拉头 vs 无 joint 固定嘴）。

### Slot C：control（电子/旋钮控制）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `touch_dial` | 母A | L156-L182 + L293-L326 | eligible if compatible | 立柱前 control pod（横圆柱）+ 触控屏 Box + 红/蓝温度图标 + 立柱侧 `dial_cap`（`KnobGeometry` fluted）绕 pod 轴 REVOLUTE ±135°（off-axis dot 验证连续转动）。新增 1 part（dial）+ 1 revolute + 若干 parent visual。 |
| `flow_knob` | 007_v25 | L297-L329 | eligible if compatible | 独立流量旋钮：`flow_knob`(mesh) + `knob_boss`，REVOLUTE 绕水平 X 轴；无触控屏。仅 +1 part +1 revolute，part graph 与 touch_dial 不同（无 display/icon 簇）。 |
| `manual_none` | 母B | （无 control 部件，全 record） | eligible if compatible | 无电子控制；阀杆即唯一控制。control slot 不 emit 任何 part / joint。**降级理由**：这是真实主流形态（007 家族 ~70% 纯手动），非凑数；作为「空 module」与另两个有 joint 的 module 形成拓扑差。 |

> Slot C 取 3 个候选（2 个有 revolute control joint + 1 个空）。`manual_none` 单部件为空是合法降级——它代表占多数样本的纯手动形态，且使 control 轴产生 +1revolute / +0joint 的真实拓扑分叉。

## 槽位图（slot graph）

pattern: mixed

```
            [BASE+COLUMN]  (deck z=0, 立柱 +Z；column_form 由 handle_form 派生)
                 |
   +-------------+----------------+--------------------+
   |             |                |                    |
(Slot A handle) (Slot C control)  |             [SWIVEL collar 顶端 z=SWIVEL_Z]
   |             |                 |                    |
 REVOLUTE       REVOLUTE          (parent visual)   --[REVOLUTE axis=Z, ±60..110°]-->
 绕 Y(拨杆)     绕 X/Y(旋钮)                          [GOOSENECK spout 高弧倒-U]
   |  (×N: handle_count multiplicity)                       |
 (cross⇒N=2 共享cross_tube;                          --[drop-leg 末端接口]-->
  lever⇒N∈{1,2} 各自 boss)                              (Slot B outlet_head)
                                                            |
                                              pull_down: --[PRISMATIC×2 +Mimic]--> spray_head
                                              fixed:      (焊接 spout visual, 无 joint)
```

接口点位：
- **handle → column**：valve boss / cross-tube 嵌入立柱（captured-pin，elem-scoped allow_overlap）；joint origin 在 boss 中心，axis=(0,±1,0)（绕水平 Y）。cross 形 origin 在 cross_tube 两端对称 ±Y；lever 形 single 在一侧、dual 对称 ±Y。
- **control → column**：pod / knob_boss 嵌入立柱前/侧面（seated insertion）；touch_dial axis 沿 pod 轴（Y），flow_knob axis 沿 X。
- **gooseneck → column**：swivel collar 顶面 z=SWIVEL_Z，REVOLUTE axis=(0,0,1)。鹅颈 riser 底端 `expect_contact` 坐在 collar 上。
- **outlet_head → gooseneck**：drop-leg 末端 (REACH_X, 0, DROP_END)。`pull_down`：PRISMATIC parent=hose→head + parent=spout→hose(Mimic)，axis=(0,0,-1)，总行程 0.12 m。`fixed`：tip_sleeve/aerator 作 spout 自身 visual，无 joint。

互斥 / 派生：
- `cross_tube` ⇒ handle_count N=2（横缸天然双阀体）；`side_lever` ⇒ N∈{1,2}。
- `column_form` 由 handle_form 派生（非独立采样）。
- 所有 control module 可与任意 handle / outlet 组合（无互斥）。
- **视觉细节层（gooseneck_surface / outlet_head_profile / grip_texture / base_trim）正交于全部结构 slot**，仅有轻量加权门控（见 §视觉细节层），不改 part 树 / joint 数 / joint 类型，不进入拓扑等价类。

## 每槽位 Module Emits / Interfaces

### Slot A / module side_lever
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pin_lever_i`(lever_boss + lever_pin[+tip])；valve boss 作 column parent visual | 母A L150-155,L261-280 / 007_v18 L205-211,L267-291 |
| internal joints | `lever_pivot_i` REVOLUTE axis=(0,-1,0) range≈[-90°,+45°]（竖直↔前倾） | 母A L281-291 / 007_v18 L292-303 |
| upstream interface | boss 嵌入 column valve mount（captured-pin overlap） | 母A L70-71 / 007_v18 L205-211 |
| downstream interface | 无（叶节点） | — |

### Slot A / module cross_tube
| emits | 描述 | 来源 |
|---|---|---|
| parts | column 上 `cross_tube` + 两端 `valve_end_cap_0/1`（parent visual）；`pin_lever_0/1`(children) | 母B L120-138,L178-193 |
| internal joints | `lever_pivot_0/1` REVOLUTE axis=(0,-1,0) range≈[-90°,0]（两杆独立） | 母B L194-207 |
| upstream interface | cross_tube 横贯立柱（中段与 column_shaft overlap，结构融合） | 母B L120-126 |
| downstream interface | 无 | — |

### Slot B / module pull_down_spray
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hose_stem`(sleeve) + `spray_head`(head_body + nozzle + button + inner_hose) | 母A L206-239 |
| internal joints | `spray_pulldown` PRISMATIC(hose→head) + `hose_slide` PRISMATIC(spout→hose, Mimic ×1.0)；总行程 0.12 m | 母A L241-259 |
| upstream interface | hose_slide origin = drop-leg 末端 (REACH_X,0,DROP_END)；rest 时 head_body `expect_contact` spout tip | 母A L255 |
| downstream interface | spray nozzle 朝 -Z 下出水 | 母A L221-226 |

### Slot B / module fixed_aerator
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tip_sleeve` + `outlet_aerator`（spout 自身 visual；head body 截面由 `outlet_head_profile` 视觉子轴决定） | 母B L154-165 / 007_v18 L227-251 |
| internal joints | 无 | — |
| upstream interface | 焊在 drop-leg 末端，随 spout swivel | 母B L156,L162 |
| downstream interface | aerator 朝 -Z 下出水 | 母B L160-165 |

### Slot C / module touch_dial
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dial_cap`(KnobGeometry + off-axis dot)；control pod / touch_display / hot_icon / cold_icon 作 column parent visual | 母A L156-182,L293-315 |
| internal joints | `dial_knob` REVOLUTE axis=(0,-1,0) range ±135° | 母A L316-326 |
| upstream interface | pod 嵌入立柱前面；dial base 嵌 pod 端 1.5 mm（seated） | 母A L157-159,L321 |
| downstream interface | 无 | — |

### Slot C / module flow_knob
| emits | 描述 | 来源 |
|---|---|---|
| parts | `flow_knob`(mesh) + `knob_boss`(parent visual) | 007_v25 L297-320 |
| internal joints | `knob_joint` REVOLUTE axis=(1,0,0) | 007_v25 L324-329 |
| upstream interface | knob_boss 嵌入立柱侧面 | 007_v25 L297-313 |
| downstream interface | 无 | — |

### Slot C / module manual_none
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无（control 层空） | 母B 全 record |
| internal joints | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `handle_form` | enum | `{side_lever, cross_tube}` | — | choice | deterministic procedural sampler | Slot A 表 |
| `outlet_head` | enum | `{pull_down_spray, fixed_aerator}` | — | choice | sampler | Slot B 表 |
| `control` | enum | `{touch_dial, flow_knob, manual_none}` | — | choice | sampler | Slot C 表 |
| `handle_count` (N) | int | `[1,2]` | — | conditional | `cross_tube⇒2`；`side_lever⇒{1,2}`（加权） | §Multiplicity |
| `palette_style` | enum | `{brushed_gold, gloss_black, polished_chrome, brushed_stainless, matte_gunmetal}` | brushed_gold | choice | `rng.choice(PALETTE_STYLES)`（cushion.py 写法） | §palette |
| `column_form` | enum(derived) | `{tapered_cone, cylindrical_disc}` | — | conditional | `cross_tube⇒cylindrical_disc`；`side_lever`→任一 | backbone |
| **`gooseneck_surface`** | **enum(visual)** | `{smooth, pre_rinse_spring, ribbed_sleeve}` | smooth | choice | 加权 `rng.choice`；只改 spout parent visual，无 joint | 视觉层 / 007_v18,002_v06 |
| **`outlet_head_profile`** | **enum(visual)** | `{smooth_cone, ribbed_barrel, stepped_cylinder}` | smooth_cone | choice | 改 head body loft 截面，无 joint | 视觉层 / 多 copy「ribbed spray head」 |
| **`grip_texture`** | **enum(visual)** | `{smooth, fluted, ribbed}` | fluted | choice | `KnobGrip(style=...)` 应用到 pin_lever cap + 控件 knob，无 joint | 视觉层 / 母A,002_v08 |
| **`base_trim`** | **enum(visual)** | `{none, collar_ring, escutcheon}` | none | choice | 焊接静态环，融入底座/collar parent visual，无 part 节点、无 joint | 视觉层 / 007_v25 |
| `column_height_scale` | float | [0.78, 1.28] | 1.0 | independent | clamp；驱动 SWIVEL_Z / 立柱高（拉宽覆盖样本立柱高跨度） | 母A L45-48 / 母B L46-47 |
| `riser_height_scale` | float | [0.72, 1.35] | 1.0 | independent | clamp；倒-U 直 riser 段长（弧下方竖管），进 apex equation | 母A L50 / 母B L86-95 |
| `arc_radius_scale` | float | [0.80, 1.32] | 1.0 | independent | clamp ARC_R（弧半径 = 倒-U 开口宽 base） | 母A L53 / 母B L71 |
| `arc_aspect_scale` | float | [0.82, 1.32] | 1.0 | independent | clamp；**弧高/弧宽比**——半圆(=1)↔竖高尖拱(>1)/扁拱(<1)；`arc_height = ARC_R·arc_aspect_scale`，**弧形状解耦 reach** | 母A/母B threePointArc apex vs span 跨度 |
| `arc_reach` (倒U开口宽) | float | derived | — | equation | `= 2·ARC_R·arc_radius_scale`（弧水平开口 = reach） | 母A L54 / 母B L73 |
| `apex_world` | float | derived | — | equation | `= SWIVEL_Z + RISER_TOP·riser_height_scale + ARC_R·arc_aspect_scale + TUBE_R` | 母B L81 |
| `tube_radius_scale` | float | [0.82, 1.22] | 1.0 | independent | clamp TUBE_R（管胖瘦，拉宽覆盖样本粗细跨度） | 母A L52 / 母B L70 |
| `tube_taper_ratio` | float | [0.70, 1.00] | 1.0 | independent | 嘴管锥度：`outlet_tube_R = TUBE_R·tube_taper_ratio`（1=等径，<1=向出水端收锥） | 母A drop-leg 渐细 / 母B L70-79 |
| `spray_head_size_scale` | float | [0.82, 1.25] | 1.0 | conditional | 喷头大小：作用于 pull_down `spray_head` 或 fixed `outlet_aerator` head body | 母A L206-239 / 母B L147-165 |
| `handle_length_scale` | float | [0.80, 1.28] | 1.0 | independent | pin_lever 长度（把手长） | 母A L261-280 / 母B L178-193 |
| `handle_radius_scale` | float | [0.85, 1.22] | 1.0 | independent | pin_lever / boss 半径（握把粗细） | 母A L261-280 |
| `control_size_scale` | float | [0.85, 1.22] | 1.0 | conditional | 仅 control≠manual_none：缩放 touch_dial pod/display 或 flow_knob 整体 | 母A L156-182 / 007_v25 L297-320 |
| `valve_spacing_scale` | float | [0.80, 1.20] | 1.0 | conditional | 仅 N=2 生效；驱动 cross_tube 长 / dual lever ±Y 间距 | 母B L52-57 |
| `pulldown_travel_scale` | float | [0.78, 1.25] | 1.0 | conditional | 仅 `pull_down_spray` 生效；total=2·stage | 母A L58 |
| (—) | constraint | — | — | inequality | `apex_world ∈ [0.36, 0.50]`；违反按比例联合回缩 arc_radius_scale / arc_aspect_scale / riser_height_scale / column_height_scale 后重投影 | 接口/identity |
| (—) | constraint | — | — | inequality | `arc_reach ∈ [0.12, 0.20]`；保证高拱伸过水槽 | identity |
| (—) | constraint | — | — | inequality | `outlet_tube_R = TUBE_R·tube_taper_ratio ≥ 起泡器/花洒内径 + 壁厚`（锥度下出水口不退化） | clearance |
| (—) | constraint | — | — | inequality | `RISER_TOP ≥ 0` 且 swivel collar 顶 ≤ riser 底（gooseneck 坐在 collar 上） | 母B L294-311 |

连续尺寸采样契约：先采 independent（column/riser/arc_radius/arc_aspect/tube/tube_taper/handle_length/handle_radius）→ 派生 equation（arc_height、reach、apex）→ inequality 投影回缩（apex/reach 越界则按比例联合缩 arc_radius_scale & arc_aspect_scale & riser_height_scale & column_height_scale 再算；出水口锥度越界则抬 tube_taper_ratio）→ conditional（valve_spacing 仅 N=2、pulldown_travel 仅 pull_down、spray_head_size/control_size 按上游 choice）解析。视觉子轴（gooseneck_surface / outlet_head_profile / grip_texture / base_trim）在尺寸求解之后各自加权 `rng.choice`，只决定 visual primitive / 表面纹理 / 静态装饰环，不参与尺寸不等式、不新增 joint。

## 视觉细节 / 外观变化层（appearance sub-axes，不计拓扑）


### 子轴 1：`gooseneck_surface`（鹅颈管表面）
| 候选 | 5★ 样本支撑 | 几何做法 | 门控/权重 |
|---|---|---|---|
| `smooth`（默认） | 母A/母B 全部直管 | 纯 `threePointArc` sweep 光面管，无附加 visual | 任意组合，主权重 ~0.55 |
| `pre_rinse_spring` | 007_v18 L64-130（`SPRING_WIRE_R=0.0018`、`SPRING_COIL_R=TUBE_R+wire/2`、`SPRING_TURNS=10`、`_spring_points()` 螺旋 helper） | 沿弧段路径生成 helical 折线（每圈 24 点），扫一根细 wire 圆管，**coil_r 略嵌入主管**保证 connectivity；作 spout 子 visual，随 swivel 一起转 | 商用 pre-rinse 特征：fixed_aerator 时权重高，pull_down 时低（下拉头与弹簧并存少见但允许） |
| `ribbed_sleeve` | 002_v06 L120-140（周向凹槽切罗纹：loft 主体后用 annular cutter 逐环 `boolean_difference` 切 N 道沟，两端留 `margin=0.006` 光领） | 在 riser/drop-leg 段套一段略大半径 sleeve，沿轴向每隔 spacing 切一圈浅环槽形成罗纹；纯 visual，不动管心 | 任意组合，权重 ~0.20 |

### 子轴 2：`outlet_head_profile`（喷头/出水头形状）
| 候选 | 5★ 样本支撑 | 几何做法 | 门控 |
|---|---|---|---|
| `smooth_cone`（默认） | 母A spray_head L206-239（光锥 loft） | 单段渐变 loft 锥头 | 任意 outlet（pull_down spray_head 或 fixed head 都适用） |
| `ribbed_barrel` | 多 copy「ribbed spray head: loft with alternating ridge/valley radii」（如 002_v08 L109、007_v18 L57/L116「ribbed cylindrical spray head with circumferential ribs」） | head body loft 用交替 ridge/valley 半径，外径比光锥宽出 rib 高度；或周向切环槽 | 任意 |
| `stepped_cylinder` | 007_v18/007_v25 ribbed cylindrical head（柱身 + 阶肩） | 圆柱主体 + 一道直径阶跃 shoulder + 端面起泡器盘 | 任意 |

> 仅改 head body 的 loft/截面 visual，与 `spray_head_size_scale` 协同；不增 part、不增 joint。pull_down 的下拉头随 head 形变，其 2 条 PRISMATIC + Mimic 拓扑不变。

### 子轴 3：`grip_texture`（把手/旋钮握感）
| 候选 | 5★ 样本支撑 | 几何做法 | 门控 |
|---|---|---|---|
| `fluted`（默认） | 母A L299 + 绝大多数 copy `KnobGrip(style="fluted", count=24, depth=0.0008)` | pin_lever cap / dial_cap / flow_knob 用 `KnobGrip(style="fluted")` 直纹 | 任意 |
| `ribbed` | 002_v08 L432 `KnobGrip(style="ribbed", count=16, depth=0.0006)` | 同上换 `style="ribbed"` 横罗纹 | 任意 |
| `smooth` | 母B 手动杆（无 grip） | 不加 `KnobGrip`，光面杆/旋钮 | 任意 |

> 仅是已存在的 pin_lever / dial / knob 的**表面 KnobGrip 参数**，不改其 REVOLUTE 关节、不增 part。manual_none 下只作用于 pin_lever cap。

### 子轴 4：`base_trim`（底座/颈部装饰环）
| 候选 | 5★ 样本支撑 | 几何做法 | 门控/权重 |
|---|---|---|---|
| `none`（默认） | 母A/母B 极简 swivel collar | 仅基础 swivel_collar，无额外环 | 任意，主权重 ~0.5 |
| `collar_ring` | 007_v25 L41「chrome collar ring separates column from gooseneck spout」 | 在 column 顶 / swivel collar 处加一圈短铬环 visual，融入 collar parent visual | 任意 |
| `escutcheon` | 007_v25 L28/L36/L52（`ESCUTCHEON_R=0.055`、`ESCUTCHEON_H=0.005` 宽盘 + 两级 stepped pedestal） | deck 顶加一片宽 escutcheon 盘 + 1–2 级阶梯底座 pedestal，融入 base parent visual | monobloc/cross 家族权重略高 |


## Multiplicity / Copy Logic

**1 根 multiplicity 轴：handle_count（拨杆数 N）。**

- `count_param`：`handle_count` (N)
- `N_range`：`[1, 2]`（产品域：厨房龙头单工位或热/冷双工位；N≥3 属管汇/商用排阀，离类，不进采样）
- sampling domain（权重，按 handle_form conditional）：
  - `side_lever`：N=1 权重 0.6（单 mixer 主流）/ N=2 权重 0.4（双柄台式）
  - `cross_tube`：N=2 权重 1.0（横缸天然双阀体；N=1 非法）
- copied object：lever 组件 `pin_lever_i = (lever_boss + lever_pin[+tip])` 及其 `lever_pivot_i` REVOLUTE 关节。cross 形下 cross_tube 横缸为**共享**单 visual（不复制），仅复制两根杆；side_lever 形下每根杆各带自己的 valve boss。
- naming：`pin_lever_{idx}` / `lever_pivot_{idx}`，idx=0..N-1（数字后缀，无内在左右语义）。
- placement：N=1 → 单侧（-Y，母A）；N=2 → 对称 ±valve_spacing（母B `LEVER_Y=±0.058`）。
- joint policy：每杆独立 REVOLUTE 绕水平 Y 轴，互不 mimic；range≈[-90°,+45°]（竖直↔前倾）。
- source/gating：母A L261-291（N=1）；母B L178-207（N=2 loop）；gating 见兼容矩阵。

## 拓扑多样性审计

总组合数（拓扑类）：
- handle 拓扑 cell = handle_form×handle_count（gating 后）= {side_lever-1, side_lever-2, cross_tube-2} = **3**
- outlet_head = **2**
- control = **3**
- **3 × 2 × 3 = 18** 个 distinct 拓扑等价类。
- palette_style(5)、各 `*_scale` 连续参数、以及 4 个外观子轴（gooseneck_surface×3 / outlet_head_profile×3 / grip_texture×3 / base_trim×3）为**类内**视觉多样性，**均不计入拓扑类**（外观子轴不 emit joint、不改 part 节点数）。

理由：**鹅颈高弧 + swivel 是固定身份不作 slot**，但 handle(form×count)/outlet/control 三层各自改变 part 树 + joint 数 + joint 类型（REVOLUTE/PRISMATIC/无），组合出 18 个真实拓扑类，稳过 10 门槛。其中 handle 改 child/joint 数（1↔2 杆、cross 横缸 vs 侧 boss）、outlet 改 prismatic+Mimic 链 vs 无 joint、control 改 +1revolute(2 种 part graph) vs +0。

**类内视觉多样性来源（弧嘴固定身份下的核心补偿）**：本类身份特征（高弧倒-U + 立柱 + Z-swivel）固定，拓扑天花板恒为 18，因此**类内不重复主要靠三条腿撑**：(1) **连续弧形参数拉满**——riser_height / arc_radius / **arc_aspect（弧高/弧宽解耦，半圆↔尖拱↔扁拱）** / tube_radius / tube_taper 让"弧的形状"在 apex∈[0.36,0.50]、reach∈[0.12,0.20] 内连续大幅变化，正是低拓扑类别最值得开的维度；(2) **4 个外观子轴**（管表面 smooth/spring/ribbed、喷头 cone/barrel/stepped、握感 smooth/fluted/ribbed、底座 none/collar/escutcheon）共 3⁴=81 视觉组合，全部来自样本真实支撑且零新增关节；(3) **5 档 palette**（色骨架不动，按用户要求）。三者相乘 → 18(拓扑)×81(外观)×5(palette)×连续弧形空间，类内视觉绝不撞脸，同时拓扑等价类严格守在 18。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 用 `ctx.rng` 依次 (1) 选 handle_form；(2) 按 handle_form conditional 加权抽 handle_count N；(3) 选 outlet_head；(4) 选 control；(5) 派生 column_form；(6) 抽 palette_style；(7) 采 independent scales → 派生 equation → inequality 投影回缩 → conditional 解析；(8) 各外观子轴加权 `rng.choice`（gooseneck_surface / outlet_head_profile / grip_texture / base_trim）。compatibility matrix 阻止 `cross_tube×N=1`。无需 curated/modulo 主表；最多 0–2 个 regression override（若 sweep 暴露特定失败 seed 才加，附理由）。


Controlled local parameterization：初版应含连续 scale `column_height_scale`、`riser_height_scale`、`arc_radius_scale`(→reach equation)、`arc_aspect_scale`(→arc_height/apex equation)、`tube_radius_scale`、`tube_taper_ratio`、`spray_head_size_scale`(conditional outlet)、`handle_length_scale`、`handle_radius_scale`、`control_size_scale`(conditional control)、`valve_spacing_scale`(conditional N=2)、`pulldown_travel_scale`(conditional pull_down)；以及 4 个外观枚举子轴。全部在 `resolve_config` clamp/派生，受 apex∈[0.36,0.50]、reach∈[0.12,0.20]、出水口锥度、collar-seat 不等式约束，不破坏 InterfaceSpec/MatingContract/multiplicity；跨部件依赖（reach=2·ARC_R、apex 求和、outlet_R=TUBE_R·taper）显式声明，不当独立自由变量。外观子轴只改 visual，不入尺寸不等式。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | handle_form → (conditional)N → outlet → control → derive column_form → palette → scales → 4 外观子轴 | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 合法：side_lever×{1,2}、cross_tube×2、任意 outlet、任意 control、任意外观组合；非法：cross_tube×1（横缸单阀体无意义）；fallback：误采 cross×1 → 强制 N=2 | 无悬空 / 穿模 / joint 轴错 / apex 越界 / pull-down 链断 / 双杆碰撞 / spring 或 sleeve 与管脱离 |
| controlled local variation | 12 个 scale + clamp + 4 外观枚举（见上） | 高弧比例/弧形/纹理变化但 apex/reach/collar-seat/joint origin/身份不破，外观层零新增关节 |
| regression overrides | none（如 sweep 暴露失败 seed 再加，≤2 个并附理由） | 仅已知失败回归 |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | & contract failures & 外观 visual connectivity |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A handle_form | 2 | yes | no | lever vs cross 拓扑差显著；2 已足 |
| B outlet_head | 2 | yes | no | 活动下拉(2prismatic+Mimic) vs 固定嘴 |
| C control | 3 | yes | yes | touch_dial / flow_knob / manual_none |
| (视觉) gooseneck_surface | 3 | yes | yes | smooth/spring/ribbed_sleeve — 不计拓扑 |
| (视觉) outlet_head_profile | 3 | yes | yes | cone/barrel/stepped — 不计拓扑 |
| (视觉) grip_texture | 3 | yes | yes | smooth/fluted/ribbed — 不计拓扑 |
| (视觉) base_trim | 3 | yes | yes | none/collar/escutcheon — 不计拓扑 |

## Validator

- slot_choices_for_seed returns implemented module names（handle_form, outlet_head, control, handle_count, palette_style, 以及 4 外观子轴 gooseneck_surface/outlet_head_profile/grip_texture/base_trim）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix 阻止 `cross_tube × N=1`
- optional regression overrides sparse and justified（默认 none）
- final template 不循环小型 curated 主表
- controlled local scale 全部 clamp/派生（column/riser/arc_radius/arc_aspect/tube/tube_taper/handle_length/handle_radius/spray_head_size/control_size/valve_spacing/pulldown_travel），apex∈[0.36,0.50]、reach∈[0.12,0.20]、出水口锥度不破接口/clearance/joint origin/身份
- cross-part scale 依赖（reach=2·ARC_R·scale、apex 求和含 riser/arc_aspect、outlet_R=TUBE_R·taper、N=2 valve_spacing）在 resolve_config 求解
- **外观子轴不变量**：gooseneck_surface/outlet_head_profile/grip_texture/base_trim 的任何取值都不新增 part 节点、不新增 joint；spring/ribbed_sleeve/装饰环并入相邻 parent visual 并与主体 `expect_overlap` 保持 connectivity（无漂浮 island）
- 关键 InterfaceSpec/MatingContract：gooseneck riser `expect_contact` swivel collar；handle boss `expect_overlap` 入 column/cross_tube；pull_down head `expect_contact` spout tip 且伸缩两段 `expect_overlap` 保持插入；pre_rinse_spring coil `expect_overlap` 主管；ribbed_sleeve `expect_overlap` 管壁
- 关键 joint 类型/轴/range：spout_swivel REVOLUTE axis=Z；lever_pivot REVOLUTE axis=(0,±1,0)；spray_pulldown+hose_slide PRISMATIC axis=-Z + Mimic；dial/flow_knob REVOLUTE
- copied objects（pin_lever_i）遵循命名/对称 placement

## Reject cases

- 鹅颈 apex < 0.36 m 或无高拱（退化成直嘴/矮台盆龙头 → 离类）。
- arc_reach < 0.12 m（弧不伸过水槽，失去 pre-rinse/高弧身份）。
- arc_aspect 过大致弧顶失稳/穿过控件，或过小退化成扁平拱失去身份（受 apex/reach 不等式联合回缩拦截）。
- tube_taper_ratio 过小致出水口退化（< 起泡器内径 + 壁厚）。
- 立柱不落在 deck plane（z≠0，悬空）。
- `cross_tube × N=1`（横缸只挂一根杆，非法组合未被 gating 拦住）。
- pull_down 伸缩链在全行程下 sleeve/inner_hose 脱出 spout（穿帮、断开）。
- 双杆 N=2 互相碰撞（valve_spacing 过小）或与 control pod 冲突。
- handle boss 完全埋入或完全脱离 column（无 captured-pin overlap，悬空/穿模）。
- lever_pivot 轴方向错（绕 Z 或 X，拨杆变成绕错轴）。
- gooseneck riser 不坐在 swivel collar 上（缝隙/断开）。
- pre_rinse_spring coil 或 ribbed_sleeve 与主管脱离成漂浮 island（coil_r/sleeve 未嵌入主管）。
- 外观子轴意外 emit 了活动关节或新 part 节点（破坏「外观不计拓扑」不变量）。

## 与相邻类别的边界

- **不该混入：墙挂式龙头（wall_mounted_faucet）**——无台面立柱、无 deck-plane 接地，水路从墙出，接口与 swivel 立柱完全不同（母资产 `rec_model-a-wall-mounted-bathroom-faucet-*` 是另一类，不纳入本 spec）。
- **不该混入：矮直嘴台盆龙头 / 直管 spout**——apex 低、无倒-U 高拱、不绕 Z swivel；本类身份核心正是 apex≥0.36 m 的高弧 + swivel，直嘴会丢身份（见 §核心身份与 Reject）。
- **不该混入：商用排阀管汇 / N≥3 多工位**——超出 handle_count [1,2] 产品域。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 样本覆盖分析

按归一结构指纹（`handle_form-handle_count | outlet_head | control`）对 62 个 5★（60 copy + 2 母）分类计数：

| 归一指纹 cell | 计数 | 占比 | 映射到设计 slot 组合 |
|---|---:|---:|---|
| lever-1 \| pull_down \| control | 19（含母A） | 30.6% | side_lever×1 + pull_down_spray + touch_dial |
| cross-2 \| fixed \| manual | 12（含母B） | 19.4% | cross_tube×2 + fixed_aerator + manual_none |
| lever-1 \| fixed \| manual | 9 | 14.5% | side_lever×1 + fixed_aerator + manual_none |
| cross-2 \| pull_down \| manual | 8 | 12.9% | cross_tube×2 + pull_down_spray + manual_none |
| lever-2 \| pull_down \| control | 5 | 8.1% | side_lever×2 + pull_down_spray + touch_dial |
| cross-2 \| fixed \| control | 4 | 6.5% | cross_tube×2 + fixed_aerator + (touch_dial/flow_knob) |
| lever-1 \| fixed \| control | 2 | 3.2% | side_lever×1 + fixed_aerator + (touch_dial/flow_knob) |
| lever-1 \| pull_down \| manual | 1 | 1.6% | side_lever×1 + pull_down_spray + manual_none |
| cross-2 \| pull_down \| control | 1 | 1.6% | cross_tube×2 + pull_down_spray + (touch_dial/flow_knob) |
| lever-2 \| fixed \| manual | 1 | 1.6% | side_lever×2 + fixed_aerator + manual_none |

观察（拓扑覆盖）：
- **共 10 个不同 cell 被实际命中，全部 62 个样本 100% 映射到设计的 18 个合法 cell**（覆盖率 100%；无离类、无落到非法 `cross×1`）。
- 设计 18 cell 中 10 个有 5★ 来源（命中率 56%），其余 8 个为合法长尾组合（如 `flow_knob` 控制独立 cell、`side_lever×2 + cross/fixed` 余下排列、pre-rinse fixed 变体），由 sampler 程序化生成，结构均可由已采纳 module 拼装。
- 高频 head：`lever-1|pull_down|control`(30.6%) 与 `cross-2|fixed|manual`(19.4%) 即两条母资产形态，合计 50% —— 这正是两个家族母本，确认本 spec 双家族归并正确。
- **身份的高弧鹅颈 spout 在全部 62 个样本中 100% 固定存在**（threePointArc sweep + Z-swivel），证实其为身份特征而非可变 slot；多样性确实全部落在 handle / outlet / control 三层 + N，符合用户要求。

视觉细节层覆盖（4 外观子轴 × 弧形跨度，按几何/角色读，不信字面名）：
| 视觉子轴值 | 样本支撑命中 | 备注 |
|---|---|---|
| gooseneck_surface=smooth | 母A/母B + 多数 copy | 主流，最高权重 |
| gooseneck_surface=pre_rinse_spring | 007_v18（helical 弹簧 helper `_spring_points`，SPRING_TURNS=10） | 商用 pre-rinse，真实存在，优先纳入 |
| gooseneck_surface=ribbed_sleeve | 002_v06（周向凹槽切罗纹 N_RIBS） | 真实存在 |
| outlet_head_profile=smooth_cone | 母A spray_head | 默认 |
| outlet_head_profile=ribbed_barrel | 002_v08/007_v18 等多 copy「ribbed spray head」 | 高频视觉特征 |
| outlet_head_profile=stepped_cylinder | 007_v18/007_v25 ribbed cylindrical head | 真实存在 |
| grip_texture=fluted | 母A + 几乎全部 copy `KnobGrip(style="fluted")` | 默认，最高频 |
| grip_texture=ribbed | 002_v08 `KnobGrip(style="ribbed")` | 真实存在 |
| grip_texture=smooth | 母B 纯手动光杆 | 真实存在 |
| base_trim=none | 母A/母B 极简 | 默认 |
| base_trim=collar_ring | 007_v25「chrome collar ring」 | 真实存在 |
| base_trim=escutcheon | 007_v25（ESCUTCHEON_R=0.055 宽盘 + stepped pedestal） | 真实存在 |
| 连续弧形跨度（apex/reach/弧高弧宽比/管粗细/锥度） | 全 62 样本 apex 0.38–0.45 / reach 0.12–0.20 / 半圆↔尖拱 / 粗细管混杂 | 由 arc_radius/arc_aspect/riser_height/tube_radius/tube_taper 连续覆盖 |

观察（视觉覆盖）：4 个外观子轴的全部 12 个取值**都能找到 5★ 样本支撑**（spring/ribbed_sleeve/ribbed_barrel/stepped/fluted/ribbed grip/collar/escutcheon 均有真实出处），无凭空发明；3⁴=81 视觉组合由 sampler 程序化生成，结构均不增关节。连续弧形参数覆盖样本中半圆↔尖拱、粗↔细管、长↔短 riser 的全跨度——这是低拓扑类别补类内多样性的主力维度。

## 模板实现备注（可选）
- handle/control/outlet 三个 helper 各自封装 module factory；cross_tube 横缸是 column parent visual，仅复制 pin_lever。
- 外观层封装为独立 visual 修饰函数：`_apply_gooseneck_surface(spout, surface)`（smooth/spring/ribbed_sleeve）、`_head_profile(profile, size_scale)`（cone/barrel/stepped loft）、`grip = KnobGrip(style=grip_texture)`、`_base_trim(base, trim)`（none/collar_ring/escutcheon）；全部返回融入 parent 的 visual，不创建独立 part / joint。
- captured-pin overlap 需 element-scoped allow_overlap：handle boss↔column/cross_tube、pull_down sleeve↔spout、inner_hose↔sleeve、dial↔pod（参母A run_tests L349-383）；外观层新增 elem-scoped overlap：pre_rinse_spring coil↔主管、ribbed_sleeve↔管壁、collar_ring/escutcheon↔base（均 `expect_overlap` 保 connectivity）。
- `column_form` 由 handle_form 派生，不进 slot_choices_for_seed 枚举（不改拓扑等价类）。外观 4 子轴进 slot_choices_for_seed 但**不进**拓扑指纹（否则误把视觉算成拓扑类）。
- pull_down 的 hose_slide 必须 `Mimic(spray_pulldown,1.0)`，总行程 = stage×2（母A L435-444）。
- pre_rinse_spring 用折线 helix（每圈 24 点）扫细 wire 圆管；coil_r = TUBE_R + wire_r·0.5 略嵌主管避免漂浮 island（007_v18 L66）。
- 参考相近成熟模板（实现阶段读）：带 prismatic+Mimic 伸缩链 + 多 revolute 控件的模板（如 drinking_fountain 的 articulate-controls / hair_dryer 的轴对称旋转件）作 slot graph + 控件关节参考；KnobGrip 纹理参考 binocular/drinking_fountain 旋钮。
