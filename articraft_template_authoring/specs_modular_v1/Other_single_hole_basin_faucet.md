# single_hole_basin_faucet — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `single_hole_basin_faucet` |
| template path | `agent/templates/Other_single_hole_basin_faucet.py` |
| test path (optional) | `tests/agent/test_single_hole_basin_faucet_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（root body 上挂 deck/spout 固定可视 + 顶/侧的 handle articulation 链） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 93（90 条 copy-pipeline 重画样本 leaves 004/005/008 各 v01..v30 + 3 条命名干净的 master 母资产） |
| read_count | 93（master 全文精读 3 条；90 条 copy 样本按归一化语义指纹批量解析 joint 拓扑 + 角色几何，并逐条精读 knob / 椭圆 gasket / oval pedestal 代表条目取真 line 范围；外观层补写阶段额外按 grep 指纹统计 KnobGrip style / collar·ring·escutcheon visual 名 / Cylinder-vs-Box 立柱 / 边缘 fillet 分布） |
| read_scope | all 5-star samples in this category（leaves 004/005/008 v01-30 + 3 masters） |
| source_index_policy | only adopted module sources are indexed below |

**关键阅读结论（务必看「样本覆盖分析」节的统计）**：

- 这批 copy 样本各自发明部件命名（同一角色出现 `base_plate` / `base_flange` / `deck_slab` / `pedestal` / `gasket` 等多种字面名）。**candidate 归一靠几何/角色，不靠字面名**。
- 全类是一个 **monobloc 单孔台盆混水龙头** 家族：一个固定 root `body`（deck 底座 + 立柱 + 单个前伸 spout + 顶/侧的安装座），加一组**单把手 / 单旋钮 / 单按压顶盖**的 articulation。没有 widespread 双把手、没有可变 N 的同构复制。
- 三条真正的结构变化轴：
  1. **handle_form**（把手机构 = 主 joint 拓扑差异）：lever 单杆混水（2×REVOLUTE：lift + swivel/twist）／knob 旋钮（1×REVOLUTE-Z）／push_cap 自闭按压（1×PRISMATIC press + 1×REVOLUTE turn）。**无 cross/wheel 十字/轮把手**（全类 0 条）。
  2. **spout_form**（出水嘴 mesh 家族）：tubular_downturned 圆管下弯／open_channel 开口 U 槽／flat_blade 扁平刀片（带 aerator collar + 暗色 outlet）。
  3. **deck_form**（台面底座）：round_flange 圆法兰(±椭圆 gasket)／square_step_plate 方形阶梯板／raised_pedestal 椭圆 pedestal / escutcheon 罩筒。
- handle 是唯一改 part-tree / joint-count / chain-depth 的轴；spout 与 deck 改 root body 的 primitive/mesh（固定可视，不加 joint），它们的差异体现在类别身份与造型，符合 §2.2「同一功能层不同承载方式」可作为 slot 的判据。

## 核心身份

`single_hole_basin_faucet` = **单孔台盆混水龙头（monobloc basin mixer）**：通过台盆/台面上的**单个安装孔**固定，一个直立 body 立柱，**单个前伸出水嘴**，以及**单个操作机构**（单把手 / 旋钮 / 按压顶盖）同时控制流量与冷热混合。默认成熟域：body 高 0.12–0.28 m，spout 前伸 0.06–0.20 m，落地于 z=0 的台面 deck，spout 指向 +X。

身份硬要素：单孔单立柱、单 spout、单操作机构、deck 落地。

## 槽位 + 候选模块表

### Slot A：handle_mechanism（操作机构 = 主 joint 拓扑轴）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `lever_top_swivel_lift` | S2 rec_model-a-polished-chrome-single-lever-tall-vessel | L136-L213 | eligible if compatible | 顶部 mounting_post → `lever_pivot_block`（REVOLUTE Z, 温度 ±45°）→ `lever_handle` 扁杆（REVOLUTE -Y, 流量 0..25°）。chain depth 3，2 joint 串联。pivot heel 座在 block 顶，handle 浮起 0.0015。 |
| `lever_side_disc_twist` | S1 rec_model-a-brushed-stainless-single-lever-basin-fau | L141-L211 | eligible if compatible | 体侧短 `lever_boss`（REVOLUTE -Y, lift/流量 ±40°）→ `lever_handle`=控制盘 disc + 前伸 lever_bar（REVOLUTE +X, twist/温度 ±30°），盘面带红/蓝 index dot。chain depth 3，2 joint，旋转轴布局与 top 变体不同（侧挂）。 |
| `knob_quarter_turn` | S4 rec_qwen_single_hole_basin_faucet_004_v03 | L149-L207 | eligible if compatible | body 顶 `knob_shaft` post → `flow_knob`（KnobGeometry 滚花筒 + knob_stem + 偏置 flow_tab），单 REVOLUTE-Z（0..90°）。chain depth 2，1 joint。 |
| `push_cap_press_turn` | S3 rec_model-a-polished-chrome-self-closing-timed-flow | L184-L232 | eligible if compatible | neck 顶 `valve_stem`（PRISMATIC -z, press 0..8mm 自闭）→ `push_cap` 按钮盖（REVOLUTE Z, 温度 ±60°, 带 index dot）。chain depth 3，1 PRISMATIC + 1 REVOLUTE，是唯一含直线副的把手。 |

### Slot B：spout_form（出水嘴 mesh 家族 = root body 固定可视）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `tubular_downturned` | S3 rec_model-a-polished-chrome-self-closing-timed-flow | L78-L115（`_build_spout_shape`）, 挂载 L169-L182 | eligible if compatible | cadquery 圆管：直 shank → tangentArc 下弯 → flared 出水口 + 真空心 bore。前伸 >0.06，口部下垂到 ~0.02。shank 座入 body（element-scoped allow_overlap）。 |
| `open_channel` | S1 rec_model-a-brushed-stainless-single-lever-basin-fau | L71-L108（`_build_spout`）, 挂载 L134-L139 | eligible if compatible | 开口 U 形槽 polyline profile 沿下垂 spline sweep，明渠造型，tip 下垂到根线下 ~0.048。 |
| `flat_blade` | S2 rec_model-a-polished-chrome-single-lever-tall-vessel | L105-L135（spout_blade + aerator_collar 环 + outlet_disc） | eligible if compatible | 扁平 Box 刀片悬臂，下方近 tip 处嵌真空心 aerator collar 环 + 暗色 recessed outlet 圆盘。前伸 ~0.17。 |

### Slot C：deck_base（台面底座 = root body 固定可视底座）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `round_flange` | S3 rec_model-a-polished-chrome-self-closing-timed-flow | L142-L149（base_flange）；可选椭圆 gasket S5 L102-L123 | eligible if compatible | 圆 Cylinder 法兰落地 z=0；module-local 可附椭圆 gasket（cadquery ellipse extrude，黑橡胶料）于法兰下，footprint 仍 ≈圆。 |
| `square_step_plate` | S2 rec_model-a-polished-chrome-single-lever-tall-vessel | L86-L97（base_plate_lower + base_plate_upper） | eligible if compatible | 方形双层阶梯 Box 底板（lower 0.090 + upper 0.068），footprint 方形，立柱也偏方。 |
| `raised_pedestal` | S6 rec_qwen_single_hole_basin_faucet_004_v02 | L141-L155（oval pedestal + 椭圆 column；可加 escutcheon 罩筒） | eligible if compatible | 椭圆/罩筒型抬高基座（cadquery oval cylinder），比 flat plate 更高更鼓，立柱座其上。代表「pedestal/escutcheon」长尾造型族。 |

硬约束满足：Slot A 4 候选、Slot B 3 候选、Slot C 3 候选，全部 ≥3，无单候选 slot，每候选带真 `model.py:Lx-Ly`，候选间结构差异均为 joint 拓扑 / primitive / mesh family（非纯尺寸/颜色）。

## 槽位图（slot graph）

pattern: `mixed`（root body 上：deck/spout 为固定可视并联挂在 root；handle 为串联 articulation 链）

```
deck_base(Slot C, root body 底座 visual)
   └─ body_column (root body, 固定 visual)
        ├─[FIXED / 同 part 内嵌可视]→ spout_form(Slot B, root body 前伸 visual)
        └─[mount face: body_top post / 体侧 boss / neck top]→ handle_mechanism(Slot A)
                lever_top:   post_top --REVOLUTE Z(swivel)--> pivot_block --REVOLUTE -Y(lift)--> handle
                lever_side:  body_side --REVOLUTE -Y(lift)--> boss --REVOLUTE +X(twist)--> disc/lever
                knob:        post_top --REVOLUTE Z--> flow_knob
                push_cap:    neck_top --PRISMATIC -z(press)--> valve_stem --REVOLUTE Z(turn)--> push_cap
```

接口点位与策略：

- **Slot C → root body**：deck_base 的顶面 z（`deck_top_z`）作为立柱 BASE_TOP；deck 与 column 同属 root `body` part 的固定可视（无 joint），靠共面 contact 装配，footprint primitive 由 deck 选择决定（Cylinder/Box/oval mesh）。
- **Slot B → root body**：spout 根部座入 body 立柱（element-scoped allow_overlap），是 root body 的内嵌可视（master S1/S3 用同 part visual，S3 用 FIXED 把独立 spout part 锚到 body 轴上的 SPOUT_S 站位）。模板统一用「root body 内嵌可视」表达 spout，不引入活动 joint。
- **Slot A → root body 安装面**：由 handle 类型派生安装锚点——`lever_top`/`knob` 用 body 顶 post 顶面（z=`post_top_z`，X-Y 居中）；`lever_side` 用体侧 boss 轴（−Y 侧，z≈上三分之一）；`push_cap` 用 neck 顶（z=`neck_top_z`，沿轴）。
- **跨 slot joint type/axis/range**：见 Slot A 候选表（REVOLUTE Z swivel/turn、REVOLUTE ±Y lift、REVOLUTE +X twist、PRISMATIC −z press）。Slot B / Slot C 不产生 joint（FIXED / 同 part 可视）。
- **互斥/派生**：handle 与 spout/deck 相互正交（无互斥），但有 clearance 派生 gate（见兼容矩阵）：handle 安装高度由 `body_height` + spout 顶面派生，保证 handle 在 rest/lift 全程不切入 spout。
- **外观子轴接口**：外观子轴（见专节）全部挂在已有 part 的 `visual` 上（root body 的 column/deck/spout 可视，或 knob part 已有的 KnobGeometry mesh），**不新增 part、不新增 joint、不新增安装锚点**，因此不影响上面任何 InterfaceSpec / MatingContract。

## 每槽位 Module Emits / Interfaces

### Slot A / module lever_top_swivel_lift
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lever_pivot_block`, `lever_handle`（含 handle_blade + pivot_heel + hot/cold dot） | S2 / model.py:L147-L202 |
| internal joints | `handle_swivel`(REVOLUTE Z, ±45°, parent=body child=block), `handle_lift`(REVOLUTE -Y, 0..25°, parent=block child=handle) | S2 / model.py:L169-L213 |
| upstream interface | body 顶 mounting_post 顶面（POST_TOP_Z），X-Y 居中 | S2 / model.py:L136-L141 |
| downstream interface | 终端 grip；pivot_heel 座 block 顶、handle_blade 浮起 0.0015 | S2 / model.py:L194-L202 |

### Slot A / module lever_side_disc_twist
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lever_boss`, `lever_handle`（control_disc + lever_bar + hot/cold dot） | S1 / model.py:L144-L198 |
| internal joints | `boss_lift`(REVOLUTE -Y, ±40°, parent=body child=boss), `lever_twist`(REVOLUTE +X, ±30°, parent=boss child=handle) | S1 / model.py:L153-L211 |
| upstream interface | body 体侧 −Y 面，boss 轴 z≈DISC_CENTER_Z（上三分之一） | S1 / model.py:L153-L164 |
| downstream interface | 前伸 lever_bar tip；disc 出体侧外（disc_outboard） | S1 / model.py:L166-L198 |

### Slot A / module knob_quarter_turn
| emits | 描述 | 来源 |
|---|---|---|
| parts | `flow_knob`（KnobGeometry knob_body + knob_stem + flow_tab） | S4 / model.py:L160-L195 |
| internal joints | `knob_rotate`(REVOLUTE Z, 0..90°, parent=body child=knob) | S4 / model.py:L197-L207 |
| upstream interface | body 顶 knob_shaft post 顶面（POST_TOP_Z） | S4 / model.py:L149-L155 |
| downstream interface | knob_stem 包住 shaft（element-scoped allow_overlap），flow_tab 偏置作旋转见证 | S4 / model.py:L177-L195 |

### Slot A / module push_cap_press_turn
| emits | 描述 | 来源 |
|---|---|---|
| parts | `valve_stem`, `push_cap`（cap_shell + cap_top + temp_indicator_dot） | S3 / model.py:L185-L223 |
| internal joints | `cap_press`(PRISMATIC -z, 0..8mm, parent=body child=stem), `cap_turn`(REVOLUTE Z, ±60°, parent=stem child=cap) | S3 / model.py:L194-L232 |
| upstream interface | body neck 顶（NECK_S1，沿 body 轴；可含轻微 tilt） | S3 / model.py:L194-L202 |
| downstream interface | cap 浮于 neck 上方 0.002-0.012，stem 嵌 neck bore（element-scoped allow_overlap） | S3 / model.py:L204-L232 |

### Slot B / module tubular_downturned
| emits | 描述 | 来源 |
|---|---|---|
| parts | root body 内嵌可视 `spout_tube`（cadquery mesh，空心 bore） | S3 / model.py:L78-L115, L169-L182 |
| internal joints | 无（FIXED 锚到 body 轴 SPOUT_S；或同 part 可视） | S3 / model.py:L176-L182 |
| upstream interface | shank 座入 body 立柱（allow_overlap spout↔body_barrel） | S3 / model.py:L92-L95 |
| downstream interface | flared 出水口下垂到 z≈0.02 | S3 / model.py:L96-L115 |

### Slot B / module open_channel
| emits | 描述 | 来源 |
|---|---|---|
| parts | root body 内嵌可视 `spout_channel`（开口 U 槽 sweep mesh） | S1 / model.py:L71-L108, L134-L139 |
| internal joints | 无 | — |
| upstream interface | 根部埋入 body 立柱前面（SPOUT_ROOT_Z） | S1 / model.py:L134-L139 |
| downstream interface | tip 下垂到根线下 ~0.048 | S1 / model.py:L79-L108 |

### Slot B / module flat_blade
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spout_blade`(Box) + `aerator_collar`(空心环) + `outlet_disc`(暗色 recessed) | S2 / model.py:L105-L135 |
| internal joints | 无 | — |
| upstream interface | blade 后端齐立柱后面，blade 顶齐立柱顶 | S2 / model.py:L105-L113 |
| downstream interface | tip 前伸 ~0.17；aerator 在下面近 tip | S2 / model.py:L114-L135 |

### Slot C / module round_flange
| emits | 描述 | 来源 |
|---|---|---|
| parts | root body `base_flange`(Cylinder) + 可选 `base_gasket`(椭圆 mesh) | S3 / L142-L149; S5 / L102-L123 |
| internal joints | 无 | — |
| upstream interface | 落地 z=0 | S3 / model.py:L144-L149 |
| downstream interface | 顶面 `deck_top_z` 接立柱 | S3 / model.py:L150-L155 |

### Slot C / module square_step_plate
| emits | 描述 | 来源 |
|---|---|---|
| parts | `base_plate_lower` + `base_plate_upper`（双层方 Box） | S2 / model.py:L86-L97 |
| internal joints | 无 | — |
| upstream interface | 落地 z=0 | S2 / model.py:L86-L91 |
| downstream interface | BASE_TOP_Z 接立柱 | S2 / model.py:L92-L97 |

### Slot C / module raised_pedestal
| emits | 描述 | 来源 |
|---|---|---|
| parts | `pedestal`（椭圆/罩筒 cadquery mesh，抬高基座） | S6 / model.py:L141-L155 |
| internal joints | 无 | — |
| upstream interface | 落地 z=0 | S6 / model.py:L142-L147 |
| downstream interface | PED_H 顶面接（椭圆）立柱 | S6 / model.py:L149-L155 |

## 外观子轴（Cosmetic Sub-Axes）

> **力度决定**：模板输出不能只是「结构够但细节单调的换色骨架」。视觉多样性 = **连续参数拉满（见「参数范围汇总」）+ 4 个外观子轴**。
>

| cosmetic_axis | 候选（#） | 样本支撑（grep 指纹） | 几何做法（不写代码，仅描述） | 作用 part.visual / 适用条件 |
|---|---|---|---|---|
| `body_section`（立柱/身截面） | `round` / `square`（2） | round：S3 `body_barrel`、S1 `body_column` 用 `Cylinder`（全类 `body_column` 32 + `body_barrel` 18 命名）；square：S2 `column` 用 `Box`，全类 36 条样本立柱用 Box；其中 9 条对方柱 `edges("\|Z").fillet` 倒圆角 | round = 立柱 `Cylinder`（半径 = `column_radius`）；square = 立柱 `Box`（边长 = `2·column_radius`），并对竖直棱 `edges("\|Z").fillet(corner_r)`（corner_r 由 `edge_round_scale` 给，软↔利落）。deck footprint 仍由 Slot C 决定，body_section 只换 root `body` 的 `body_column` 主可视 primitive | root `body`.visual `body_column`；全 handle 通用（安装锚点仍取 body 轴，不受截面影响） |
| `knob_grip`（旋钮握感） | `knurled` / `fluted` / `ribbed`（3） | `KnobGrip(style="fluted")`×10、`("knurled")`×6、`("ribbed")`×3（SDK `KnobGrip.style` 支持 fluted/scalloped/knurled/ribbed/diamond_knurl） | 把 `KnobGrip(style=<choice>, count=…, depth=…)` 喂给 knob 候选已有的 `KnobGeometry`（knurled：细密斜滚花；fluted：较少较深竖纹；ribbed：粗肋）。只改 `flow_knob` 已有 mesh 的侧壁纹理，不改 knob 半径/高/joint | knob part 已有的 `flow_knob` KnobGeometry mesh；**conditional：仅当 `handle_mechanism == knob_quarter_turn`**，其余 handle 记 `na`、不采样 |
| `spout_tip_collar`（嘴尖装饰/起泡器环） | `collared` / `plain`（2） | `aerator_collar`×8、`aerator_disc`×19、`spout_collar`×8、`outlet_ring`/`outlet_bezel`/`outlet_collar` 若干；S2 flat_blade 原生带 collar+outlet | collared = 在 spout 出水口加一圈薄空心环（`Cylinder` 空心环 / 小 torus，annulus 让暗色 outlet 露出，半 embed 进嘴口避免漂浮岛）；plain = 仅 bored 出水口无装饰环。环为 root body（或 spout）固定可视 | root `body`/spout.visual（嘴尖）；**conditional：`flat_blade` 恒为 collared（原生），`tubular`/`open_channel` 两态可选** |
| `base_escutcheon`（底座装饰环） | `ring` / `none`（2） | `base_collar`×9、`base_gasket`×9、`oval_gasket`×4、`escutcheon`/`decorative_ring`/`gasket_ring` 若干 | ring = 在 deck 顶面 / 法兰下沿加一圈薄装饰环或 gasket 盘（`Cylinder` 薄盘 / 椭圆 mesh，半 embed 进 deck 顶，footprint 不超 deck）；none = 光底座。环为 root body 固定可视 | root `body`.visual（deck 处）；全 deck 通用（`round_flange` 已有的可选椭圆 gasket 即此轴 ring 态的一种实现） |

附：**边缘处理（倒角 vs 圆角）** 不单列为一根计数子轴，而是折成一个连续量 `edge_round_scale`（见参数表）+ `body_section==square` 时的 `corner_r`：样本既有 `.edges(">Z").fillet`（S3 cap、9 条方柱倒圆角，共 26 文件用 fillet/chamfer），模板对 deck 角 / body 顶沿 / cap 沿统一用一个「全部圆角」幅度量表达，避免再撑一根离散轴。

外观子轴组合数 = body_section(2) × knob_grip(3, 仅 knob) × spout_tip_collar(2, 非 flat_blade) × base_escutcheon(2)，与 36 结构拓扑**正交相乘**仅用于视觉去重，**不计入拓扑等价类**。

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `handle_mechanism` | enum | {lever_top_swivel_lift, lever_side_disc_twist, knob_quarter_turn, push_cap_press_turn} | — | choice | deterministic procedural sampler 选择 | Slot A 表 |
| `spout_form` | enum | {tubular_downturned, open_channel, flat_blade} | — | choice | sampler 选择 | Slot B 表 |
| `deck_base` | enum | {round_flange, square_step_plate, raised_pedestal} | — | choice | sampler 选择 | Slot C 表 |
| `palette_style` | enum | {polished_chrome, brushed_stainless, matte_black, brushed_gold} | polished_chrome | choice | `rng.choice(PALETTE_STYLES)`（cushion.py 模式），不改拓扑 | S1/S2/S3 + gold/black masters |
| `body_section` | enum (cosmetic) | {round, square} | round | choice | 外观子轴，改 `body_column` primitive，不计入拓扑/slot_choices | 外观子轴表 |
| `knob_grip` | enum (cosmetic) | {knurled, fluted, ribbed} | fluted | conditional | 仅 `handle==knob_quarter_turn` 采样；否则 `na`。喂 KnobGrip.style | 外观子轴表 |
| `spout_tip_collar` | enum (cosmetic) | {collared, plain} | collared | conditional | `flat_blade` 恒 collared；其余两态可选。装饰环 parent.visual | 外观子轴表 |
| `base_escutcheon` | enum (cosmetic) | {ring, none} | none | choice | 外观子轴，deck 处装饰环 parent.visual | 外观子轴表 |
| `body_height` | float | [0.12, 0.28] | 0.20 | independent | 范围内采样后 clamp；覆盖样本高瘦(S2 立柱 0.235)↔矮胖(S3 颈顶 0.104) | S1 0.20 / S3 0.13 / S5 0.26 / S2 0.235 |
| `column_radius_scale` | float | [0.75, 1.25] | 1.0 | independent | clamp；不与 deck footprint 冲突。覆盖细(S3 R0.025)↔粗(S2 0.035×0.045) | S1 BODY_RADIUS / S2 / S3 |
| `column_taper_ratio` | float | [0.78, 1.08] | 1.0 | independent | 立柱锥度 = top_radius / bottom_radius；<1 上细下粗(S3 stepped neck 收窄)，>1 微外扩 | S3 BODY_R→NECK_R / S5 |
| `spout_reach_scale` | float | [0.70, 1.30] | 1.0 | independent | spout 前伸 = base_reach·scale，clamp。覆盖短(S3 ~0.063)↔长(S2 blade 0.17) | S1/S2/S3 spout tip |
| `spout_droop_scale` | float | [0.75, 1.30] | 1.0 | independent | 嘴弧曲率/下垂 = base_droop·scale；覆盖浅弯(S3 tubular ~0.028)↔深垂(S1 channel ~0.048) | S1/S3 spout tip drop |
| `aerator_size_scale` | float | [0.80, 1.25] | 1.0 | independent | 起泡器/outlet 环+暗盘直径整体缩放（保持环 annulus 比例） | S2 AERATOR_OUTER/INNER_R |
| `deck_footprint_scale` | float | [0.80, 1.25] | 1.0 | independent | deck 半径/边长缩放，clamp | S2/S3/S6 base |
| `deck_height_scale` | float | [0.80, 1.30] | 1.0 | independent | deck 台阶高/厚度（flange/plate/pedestal 高），不破 z=0 落地 | S2 base plates / S3 FLANGE_H / S6 PED_H |
| `handle_len_scale` | float | [0.80, 1.25] | 1.0 | conditional | 仅 lever_* 的 bar/blade 长度（conditional on lever） | S1 BAR / S2 HANDLE_LEN |
| `handle_rest_tilt` | float | [-0.14, 0.21] rad | 0.0 | conditional | 仅 lever_* 的把手 rest 俯仰角（lift joint rest 偏置，仍在 lift 行程内、不切 spout） | S1/S2 lift range |
| `knob_size_scale` | float | [0.85, 1.20] | 1.0 | conditional | 仅 knob 的 KnobGeometry 直径/高整体缩放（不改 joint 轴/range） | S4 KnobGeometry |
| `collar_size_scale` | float | [0.85, 1.20] | 1.0 | conditional | 仅 `spout_tip_collar==collared` 时装饰环直径/厚 | 外观子轴 |
| `escutcheon_size_scale` | float | [0.90, 1.25] | 1.0 | conditional | 仅 `base_escutcheon==ring` 时装饰环直径/厚（≤deck footprint） | 外观子轴 |
| `edge_round_scale` | float | [0.0, 1.0] | 0.5 | independent | 全局边缘圆角幅度：0≈利落小倒角、1≈饱满圆角；映射 deck 角 / body 顶沿 / cap 沿 / 方柱竖棱 fillet 半径 | S3 `.fillet` / 9 条方柱 `edges("\|Z").fillet` |
| `post_top_z` (派生) | float | derived | — | equation | `= deck_top_z + body_height·column_h_frac + post_h`（handle 安装高度随 body 高派生） | S2 POST_TOP_Z |
| `spout_root_z` (派生) | float | derived | — | equation | `= deck_top_z + k·body_height`（spout 根高随 body 高派生） | S1 SPOUT_ROOT_Z |
| (—) | constraint | — | — | inequality | **handle 安装面/最低姿态 ≥ spout 顶面 + clearance**：top-mount handle（lever_top/knob/push_cap）的 rest（含 `handle_rest_tilt`）+全行程最低点 z 必须高于 spout 顶面（含 `spout_droop_scale` 后的最高点）（min_gap 0.02-0.03）；违反则抬高 post_top_z 或回缩 spout_reach/droop | S2 L332-L338 / S1 L285-L293 |
| (—) | constraint | — | — | inequality | **side lever 不撞 spout**：lever_side 下放（−lift）时 lever_bar 须从 spout 旁侧（Y 向）通过，min_gap 0.010 | S1 L341-L349 |
| (—) | constraint | — | — | inequality | **装饰环 footprint 内含**：`collar_size_scale` 后嘴尖环 ≤ spout 截面外缘；`escutcheon_size_scale` 后 deck 环 ≤ deck footprint（避免装饰件超出母体悬空） | 外观子轴 |
| (—) | constraint | — | — | conditional | `handle_len_scale` / `handle_rest_tilt` 仅 handle∈{lever_top, lever_side}；`knob_grip`/`knob_size_scale` 仅 knob；`spout_tip_collar==plain` 仅非 flat_blade；`collar_size_scale` 仅 collared；`escutcheon_size_scale` 仅 ring 时生效 | Slot A/B/C + 外观子轴 |

连续尺寸采样契约：先采 independent（body_height, column_radius_scale, column_taper_ratio, spout_reach_scale, spout_droop_scale, aerator_size_scale, deck_footprint_scale, deck_height_scale, edge_round_scale）→ 按上游 enum 解析 conditional 范围（handle_len_scale/handle_rest_tilt 按 lever、knob_grip/knob_size_scale 按 knob、collar/escutcheon size 按对应外观子轴是否 present）并采样 → 派生 equation（post_top_z, spout_root_z）→ 用 inequality 投影/回缩（clearance、side-lever 旁通、装饰环内含）。外观 enum（body_section/knob_grip/spout_tip_collar/base_escutcheon）在结构 enum 之后独立加权 choice，仅写入 `model.meta["cosmetic_choices"]`，**不进 `slot_choices`**。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots 表达（单 deck、单 spout、单 handle 机构），不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。单孔台盆龙头本质单机构单嘴；hot/cold index dot、滚花 knurl/fluted/ribbed grip、aerator 环、deck 装饰环等是 module-local / cosmetic 固定细节，不构成 multiplicity 轴（grip 齿数、环数等由 KnobGrip.count 等连续/固定参数表达，不暴露为模板复制轴）。

## 拓扑多样性审计

总组合数（**仅结构拓扑**）：handle(4) × spout(3) × deck(3) = **36 个拓扑组合**（palette(4) 仅着色；外观子轴 body_section/knob_grip/spout_tip_collar/base_escutcheon 仅改 parent.visual 造型/装饰，**不计入拓扑等价类**；含连续 scale 后采样空间远大于 36）。


seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 deterministic procedural sampling：依次对 handle / spout / deck 做加权 `rng.choice`（权重见下「样本覆盖分析」：lever 偏多 ~52%、knob ~29%、push_cap ~19%；spout open_channel≈tubular>flat_blade；deck single_plate 偏多、pedestal 长尾），再对 4 个外观子轴按上游条件做加权 choice（grip：fluted>knurled>ribbed；collar/escutcheon present 概率中高），再独立采连续量（body_height / 各 *_scale / taper / droop / edge_round 等），最后 `resolve_config` 解 conditional/equation/inequality。compatibility matrix 仅含 clearance 派生 gate（无硬互斥）。无 curated/modulo 主表。regression overrides：默认 none。random sweep：seeds 0-49 初版、0-999 成熟审计；viewer 目检覆盖 4 种 handle × 至少 2 种 spout × 至少 2 种 body_section × collar/escutcheon 有/无。
Topology target：1000-seed slot choice tuple distinct 期望 ≥36（受 36 个拓扑类上限约束，连续 scale 与外观子轴均不增拓扑等价类）；低于 300 的原因是本类拓扑空间本身只有 36 类（单机构单嘴单孔），属类别固有约束，符合 §9「低于 300 需说明类别约束原因」。视觉 distinct（人/像素层面）远高于 36，由 palette × 外观子轴 × 连续参数承担。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：初版应含 `body_height`、`column_radius_scale`、`column_taper_ratio`、`spout_reach_scale`、`spout_droop_scale`、`aerator_size_scale`、`deck_footprint_scale`、`deck_height_scale`、`edge_round_scale`（independent）+ `handle_len_scale`、`handle_rest_tilt`、`knob_size_scale`、`collar_size_scale`、`escutcheon_size_scale`（conditional）。全部在 `resolve_config` 内 clamp；`post_top_z`/`spout_root_z` 按 equation 派生；clearance、side-lever 旁通、装饰环内含按 inequality 投影/回缩。这些 scale + 外观子轴只改安全比例/造型/装饰，不改 joint 拓扑、不引入未声明 multiplicity、不破坏 InterfaceSpec（安装锚点高度始终派生自 body_height + spout 顶面）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | handle/spout/deck 加权 choice + 4 外观子轴条件加权 choice + 独立连续 scale；`slot_choices_for_seed` 只返回 (handle,spout,deck) 结构三元组；外观写 `cosmetic_choices` 不进 slot_choices | slot_choices_for_seed matches build choices；cosmetic_choices recorded separately |
| compatibility matrix | 无硬互斥；gate=clearance 派生（top-mount handle 高于 spout 顶面；side lever 旁通 spout）+ 外观条件（grip 仅 knob；collar 仅非 flat_blade 可 plain；装饰环 footprint 内含）；fallback=抬高 post_top_z / 回缩 spout_reach·droop / 缩装饰环 | no floating, no spout collision, joint axis/range correct, closed/rest pose clears spout, 装饰件不悬空 |
| controlled local variation | body_height + 十余连续 scale + 4 外观子轴，全 clamp/派生/条件 | 比例与造型变化不破坏 clearance、安装锚点、joint origin、类别身份；不新增 part/joint |
| regression overrides | none | — |
| random sweep | seeds 0-49 初版，0-999 成熟审计 | 、contract failures、外观子轴均被覆盖采到 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A handle_mechanism | 4 | yes | yes | joint 拓扑主轴 |
| B spout_form | 3 | yes | yes | root body 固定可视 mesh 族 |
| C deck_base | 3 | yes | yes | root body 底座 primitive/mesh 族 |
| (cosmetic) body_section | 2 | yes | no | 外观层，不计入拓扑 |
| (cosmetic) knob_grip | 3 | yes | yes | 外观层，conditional on knob，不计入拓扑 |
| (cosmetic) spout_tip_collar | 2 | yes | no | 外观层，不计入拓扑 |
| (cosmetic) base_escutcheon | 2 | yes | no | 外观层，不计入拓扑 |

## 样本覆盖分析

**归一化语义指纹** = (handle_form, spout_form, deck_form)，对 90 条 copy 样本按几何/joint 拓扑（而非字面部件名）解析得出。

按轴边际分布（n=90）：
- handle_form：lever 47（52%）、knob 26（29%）、push_cap 17（19%）。**无 cross/wheel 十字轮把手（0 条）**。
- spout_form：open_channel 33、tubular 31、flat_blade 21（其余 5 归入最近族）。
- deck_form：round_flange 43、gasket_oval 25、square_plate 14、escutcheon/pedestal 6（前三折叠为 single_plate=82，第四为 pedestal=8）。

把 deck 折叠为模板 2 类（single_plate = round/oval/square footprint，pedestal = 抬高罩筒）后，模板 slot 空间 handle(3 族) × spout(3) × deck(2) 直接对照 90 样本：

| design cell (handle, spout, deck2) | 样本数 |
|---|---:|
| lever, tubular, single_plate | 15 |
| lever, open_channel, single_plate | 15 |
| lever, flat_blade, single_plate | 9 |
| knob, open_channel, single_plate | 10 |
| knob, tubular, single_plate | 8 |
| push_cap, tubular, single_plate | 8 |
| push_cap, open_channel, single_plate | 4 |
| lever, open_channel, pedestal | 3 |
| lever, flat_blade, pedestal | 3 |
| knob, flat_blade, single_plate | 3 |
| push_cap, flat_blade, single_plate | 3 |
| lever, tubular, pedestal | 2 |
| push_cap, tubular, pedestal | 2 |
| push_cap, flat_blade, pedestal | 2 |
| knob, tubular, pedestal | 1 |
| push_cap, open_channel, pedestal | 1 |
| knob, flat_blade, pedestal | 1 |
| knob, open_channel, pedestal | 0 |

**覆盖率结论**：
- 模板 slot 组合空间（handle 3 族 × spout 3 × deck2 2 = 18 cell；模板实际 deck 拆 3 候选把 single_plate 再细分为 round_flange/square_plate，pedestal=raised_pedestal，组合数升到 36）**覆盖 90/90 = 100% 的样本**——每一条样本都落入某个模板 cell。
- 18 个 (handle×spout×deck2) cell 中 **17 个在数据中实际出现**（仅 `knob × open_channel × pedestal` 为空），即 17/18 = 94% 的设计 cell 有真实样本支撑；剩余 1 个空 cell 由 slot 正交组合自然可达（外推，仍 eligible）。
- 高频 cell 全部命中：lever-tubular-plate(15)、lever-channel-plate(15)、knob-channel-plate(10)、lever-blade-plate(9)、knob-tubular-plate(8)、push_cap-tubular-plate(8) 等。
- 长尾（pedestal × 各组合、各 push_cap/knob 稀有组合）由 deck `raised_pedestal` 候选 + 加权采样尾部吃下。
- **外观层覆盖（不止结构）**：上面的 (handle,spout,deck) 指纹只刻画了**结构**覆盖；样本在同一结构 cell 内仍有大量**外观**差异（KnobGrip fluted 10/knurled 6/ribbed 3、aerator/spout collar 8+19+8 条、base collar/gasket 9+9+4 条、立柱 Cylinder vs Box 18+32 vs 36 条、26 文件用 fillet/chamfer），单靠结构 slot 无法复现。4 个外观子轴 + 拉满的连续参数把这层差异系统编码进来，使模板的**视觉覆盖**（而非仅拓扑覆盖）也对齐样本——同一 (handle,spout,deck) 拓扑可生成滚花/竖纹/粗肋旋钮、有/无嘴尖环、有/无底座装饰环、圆柱/方柱、高瘦/矮胖/锥/直等多种外观，避免「换色骨架」。

> 注：本节边际计数用关键词+joint 启发式归一，个别条目分类有 ±1-2 噪声，但不影响「3×3×(2~3) 组合 100% 覆盖 + 高频 cell 全中 + 外观层有真实支撑」的结论。

## Validator

- slot_choices_for_seed returns implemented module names（handle/spout/deck 三元组；外观子轴**不**出现在 slot_choices）
- cosmetic_choices recorded in `model.meta` separately（body_section/knob_grip/spout_tip_collar/base_escutcheon），且不影响 part-tree/joint 签名
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combinations（clearance 派生 gate；无硬互斥）+ 外观条件正确解析（grip 仅 knob、collar 仅非 flat_blade 可 plain、装饰环 footprint 内含）
- optional regression overrides are sparse and justified（默认 none）
- final templates do not endlessly cycle a small curated table（procedural-first）
- controlled local scale params clamped；不破坏 interface/clearance/joint origin/identity
- 外观子轴只产生 parent.visual 造型/装饰，不新增 part、不新增 joint/MatingContract（validator 应断言 part 数与 joint 数仅由 handle/spout/deck 决定，外观 enum 改变不改变这两个计数）
- cross-part scale dependencies（post_top_z/spout_root_z=equation；clearance/旁通/装饰环内含=inequality；handle_len/tilt/knob_size/collar_size/escutcheon_size=conditional）在 `resolve_config` 求解，不留到 builder
- critical InterfaceSpec/MatingContract points exist：deck_top→column、spout shank→body（allow_overlap）、handle 安装锚点→body 顶/侧/neck
- key joints have expected type/axis/range：lever_top(REV Z ±45 + REV -Y 0..25)、lever_side(REV -Y ±40 + REV +X ±30)、knob(REV Z 0..90)、push_cap(PRIS -z 0..8mm + REV Z ±60)
- copied objects follow naming/placement policy（无 multiplicity 复制；index dot/aerator/grip/装饰环为 module-local / cosmetic 固定可视）

## Reject cases

- 出现第二个把手/旋钮 → 变成 widespread/双把手龙头，越界（应为单机构）。
- spout 不前伸或无 spout / 多个 spout → 非单嘴台盆龙头。
- handle 安装锚点漂浮或低于 spout 顶面导致 rest/行程切入 spout（clearance gate 失败）。
- 把 deck/spout footprint 缩放当独立自由变量乱抽，导致立柱悬空或 base 不落地 z=0。
- 给 knob/push_cap 误加 lever bar、或给 lever 误加 PRISMATIC press（混用 handle 机构）。
- 出现十字/手轮 (cross/wheel) 把手（全类样本 0 条，不在域内）。
- spout shank 未座入 body（缺 element-scoped allow_overlap → 漂浮/断件）或 stem 未嵌 neck bore。
- joint 轴/range 错（如 swivel 用水平轴、lift 用垂直轴、press 用 REVOLUTE）。
- **外观装饰件悬空/穿模**：嘴尖环或底座装饰环未 embed 进母体（变成 disconnected island）或超出母体 footprint 悬空。
- **采无支撑外观候选**：上六棱 hex / polarArray 纵向沟槽立柱（样本 0 条），或给非 knob handle 强加 KnobGrip grip（grip 仅 knob 有支撑）。

## 与相邻类别的边界

- 不该混入：`widespread_two_handle_faucet`（双把手 + 三孔分体，本类是单孔单机构 monobloc）。
- 不该混入：`high_arc_gooseneck_faucet`（高拱鹅颈大弧 spout，本类 spout 短/中、tubular/channel/blade，无 gooseneck 高拱；样本中 gooseneck 0 条）。
- 不该混入：厨房 pull-down/侧喷 sprayer 软管龙头（带可拉拔软管/侧喷头，本类无软管 multiplicity）。
- 不该混入：`drinking_fountain`（饮水台带 bubbler/脚踏阀，不同安装与控制语义）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## 模板实现备注（可选）

- handle 安装锚点统一由一个 `_mount_anchor(handle, resolved)` helper 派生（top post / 体侧 boss / neck top），避免每 handle 各写一套高度逻辑。
- spout 三个 builder（cadquery）可共享一个「座入深度 + element-scoped allow_overlap(spout↔body)」装配 helper；flat_blade 额外 emit aerator collar + outlet 两个固定可视。
- captured-pin/seated overlap 需 element-scoped allow_overlap：spout shank↔body_barrel、knob_stem↔knob_shaft、valve_stem↔body_neck、cap_shell↔stem（照各 master run_tests 的 allow_overlap 块复制）。
- knob 候选用 `KnobGeometry`/`KnobGrip`/`KnobIndicator`（注意这些是 DIAMETER 参数，KnobGeometry 参数为直径）；`knob_grip` 外观子轴 = 给 `KnobGrip(style=...)` 传 {knurled, fluted, ribbed} 之一，外加 `knob_size_scale`，不改 knob joint。
- **外观子轴实现集中在少量 helper，且只调 `part.visual(...)`，绝不调 `model.part`/`model.articulation`**：
  - `body_section`：一个 `_body_column_visual(r)` 返回 `Cylinder`（round）或 `Box`+`edges("|Z").fillet(corner_r)`（square，corner_r 由 `edge_round_scale` 给）。
  - `spout_tip_collar`：一个 `_emit_tip_collar(body/spout, r)`，collared 时加薄空心环（半 embed 进嘴口），plain 时 no-op；flat_blade 走原生 collar 路径。
  - `base_escutcheon`：一个 `_emit_base_ring(body, r)`，ring 时加 deck 顶薄盘/椭圆 gasket（半 embed 进 deck，footprint≤deck），none 时 no-op。
  - `edge_round_scale`：deck 角 / body 顶沿 / cap 沿统一 fillet 幅度。
- `knob × open_channel × raised_pedestal` 为数据空 cell，可进 seed domain（正交可达），首轮 sweep 若该组合出 clearance 问题再 gate。
