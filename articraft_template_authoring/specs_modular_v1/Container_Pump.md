# Container pump (lotion / soap / cosmetic pump bottle) — Modular Spec

> 来源小类：`picture/Container/Pump`（articraft_data 上游 Container/Pump fork-variant pool）。
> 1 parent（clear-soap-dispenser-bottle, press pump）+ 9 fork 变体；全部 5★ converged。
> 引用 `model.py:Lx-Ly` 来自各 record 当前 `data/records/<id>/revisions/rev_000001/model.py`；以 part / joint / helper **名字** 为准（`bottle` / `_bottle_mesh` / `collar` / `bottle_to_collar` FIXED / `head_carrier` massless / `pump_swivel` REVOLUTE +Z / `pump_press` PRISMATIC +Z / `cap_hinge` / `sprayer_head` / `trigger_squeeze` / `twist_lock` / `cap_to_disc` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_pump` |
| template path | `agent/templates/Container_Pump.py` |
| test path (optional) | `tests/agent/test_container_pump_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots: body_profile + dispenser_head；瓶身是 root `bottle`，`collar` FIXED 挂 bottle，顶部机构挂 collar；无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10（1 parent + 9 fork 变体，全部 converged 5★）|
| read_count | 10（全部 model.py 全文阅读：parent press_pump + 3 body 变体 boxy_oval / tapered_waisted / tall_rectangular + 6 head 变体 flip_top_cap / disc_top_cap / trigger_sprayer / twist_lock_pump / foaming_pump / gooseneck_pump）|
| read_scope | all 5-star samples in this category（无抽样；源 map 列出的全部 parent + `rec_container_pump_var_*` 逐一读 model.py / run_tests）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14 |

冗余 / 分流说明：
- 9 个变体均为**单轴** diff：3 个换瓶身截面族（head 恒为 parent press_pump），6 个换顶部机构（瓶身恒为 parent round_body）。parent 自身免费占据 (round_body × press_pump) 这一格。跨轴组合（如 boxy_oval × trigger_sprayer）由模板采样器免费产出，源池不造组合变体。
- 所有变体共享**完全相同的 collar / neck 接口**（`collar` part、`bottle_to_collar` FIXED、neck rim top z≈0.176、knurl ring、3 圈 neck threads），是稳定 mating face，任一 body × 任一 head 都复用同一接口。只换尺寸 / 颜色 / 材质的差异未单列 candidate。

## 核心身份

按压泵分配瓶（lotion / soap / cosmetic **pump** container）：一只直立中空瓶（root `bottle`），中心轴沿 +Z，底坐地 z=0，居中于 (x=0,y=0)。瓶身由 lathe shell（`LatheGeometry.from_shell_profiles`）/ superellipse loft / CadQuery rect-extrude 发射为厚壁中空开口腔，附 label_band visual + neck threads；瓶颈上一只 `collar`（白色螺纹领圈，FIXED 挂 bottle）作为**共享 mating interface**。collar 之上骑一只**顶部分配 / 闭合机构**（**主活动语义**）：竖直按压泵头（`pump_swivel` REVOLUTE +Z 绕轴回转 + `head_carrier` massless + `pump_press` PRISMATIC +Z 下压回弹，带弯嘴 spout + 内 dip tube）/ 高大胖泡沫泵（宽混合腔 + 平顶下压片 + 短粗泡嘴 + 短内管）/ 长鹅颈乳液泵（高拱长鹅颈出嘴 + 下压泵 + 回转 + 长内管）/ 旋转锁定下压泵（`twist_lock` REVOLUTE +Z 限位 0..π/2 在解锁 / 锁死位切换，锁死位 cam 头下压封住行程 + `pump_press` PRISMATIC）/ 扳机喷雾头（`sprayer_swivel` REVOLUTE +Z + `trigger_squeeze` REVOLUTE -Y 手指扳机摆动回弹 + 前伸 nozzle + dip tube）/ 翻盖碟盖（`cap_hinge` REVOLUTE 单铰链开合露出出料孔，去泵 / 去内管）/ 碟形顶按压盖（`cap_to_disc` PRISMATIC +Z 中央圆碟下压开缝，去泵 / 去内管）。

**类别身份 = 顶部那只可动的分配 / 闭合机构 + collar 接口**；按压泵（press_pump / foaming / gooseneck / twist_lock）是核心成熟域，sprayer / flip / disc 为同小类真实邻接机构（源池已收敛）。默认成熟域：单瓶单机构（无嵌套 / 无 multiplicity / 无 cap-over-pump 防尘罩，见排除项）。

## 槽位 + 候选模块表

> **建模注记**：`body_profile` 是 root `bottle` 的 mesh / shell 属性（一次发射瓶身 shell + label + neck threads），不是独立串联 slot。`dispenser_head` 挂到共享 `collar`（`collar` 本身 FIXED 挂 bottle，是跨 body 恒定的 mating interface）。两轴笛卡尔积构成拓扑多样性（见 §9）。collar / neck 在所有 body_profile 候选上保持**轴对称且尺寸一致**（NECK_R=0.0150、COLLAR_R=0.0185、COLLAR_TOP=0.176），任一 head 都复用同一 mating face。

### Slot A：body_profile（瓶身轮廓 / footprint shape family——root `bottle` 的 shell）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_body（基线）| rec_clear-soap-dispenser-bottle-..._74587dd4（parent）| `_bottle_mesh` L47-69（`LatheGeometry.from_shell_profiles` 旋转体壳）+ `_neck_threads_mesh` L72-79 | eligible if compatible | 圆截面直筒身 + 圆肩收 neck + 螺纹圈，厚壁开口旋转体壳 |
| boxy_oval | rec_container_pump_var_boxy_oval | `_bottle_mesh` L84-114（`superellipse_profile`+`LoftGeometry` 截面 loft，BODY_EXP=4.0 圆角矩形）+ `_label_mesh` L119-134 | eligible if compatible | 圆角矩形（扁椭圆 / 超椭圆）截面瓶身，非旋转体，宽 X(0.060) 窄 Y(0.036) loft 到圆 neck；shell = outer/inner loft + ring_cap |
| tapered_waisted | rec_container_pump_var_tapered_waisted | `_body_radius_at` L56-82 + `_bottle_mesh` L85-121（waisted lathe profile：BASE_R 0.036 → WAIST_R 0.023 → UPPER_R 0.028）| eligible if compatible | 收腰 / 锥形侧轮廓（底宽—中段 WAIST_Z=0.065 收—上段微 flare—颈），lathe 侧轮廓改写 |
| tall_rectangular | rec_container_pump_var_tall_rectangular | `_bottle_mesh` L52-115（CadQuery `rect().extrude` slab + rect→rect `loft` 肩 → 圆 neck `circle().extrude`，`cut` 中空）+ `_label_mesh` L118-141 | eligible if compatible | 高直立矩形 slab（直角棱柱，宽 X 0.065 × 深 Y 0.038），平正面 + 平侧面 + 直角竖边，区别于 boxy_oval 的圆润超椭圆 |

硬约束记录：body_profile 4 candidate（达 3-6 目标）。全部厚壁中空开口腔，**共享同一 round collar / neck 接口** + `label_band` + `_neck_threads_mesh`，只换 footprint / 截面族 / 高宽比 / 直角 vs 圆角。三种发射方式覆盖 lathe（round / waisted）/ superellipse loft（boxy_oval）/ CadQuery rect-extrude（tall_rectangular）。

### Slot B：dispenser_head（**主分配 / 闭合机构槽**——顶部机构动作）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| press_pump（基线）| rec_clear-soap-dispenser-bottle-..._74587dd4（parent）| `head_carrier` part L214-219 + `pump_swivel` REVOLUTE +Z L224-232 + `head` part L235-242 + `pump_press` PRISMATIC +Z L244-252 + `_head_mesh` L111-152（cap+弯嘴 spout+stem）+ `_dip_tube_mesh` L155-159 | eligible if compatible | 竖直按压泵头：`pump_swivel` REVOLUTE +Z（绕轴回转瞄准）经 massless `head_carrier` → `pump_press` PRISMATIC +Z（下压 -0.015 回弹），弯嘴 spout off-axis(+X) + 长 dip tube 入瓶底；2 joint + 1 massless carrier |
| foaming_pump | rec_container_pump_var_foaming_pump | `head_carrier` L266-272 + `pump_swivel` REVOLUTE +Z L274-282 + `foamer_head` part L285-296 + `pump_press` PRISMATIC +Z L298-306 + `_foamer_chamber_mesh` L127-147 + `_actuator_mesh` L165-176 + `_short_dip_tube_mesh` L205-213 | eligible if compatible | 高大胖泡沫泵：同 swivel+press 拓扑（massless carrier），宽圆柱混合腔（FOAMER_R 0.020 高出领圈至 0.258）+ 平顶下压 actuator 片 + 短粗泡嘴（SPOUT_REACH 0.015，无长鹅颈）+ 短 dip tube（不达瓶底）|
| gooseneck_pump | rec_container_pump_var_gooseneck_pump | `head_carrier` L223-231 + `pump_swivel` REVOLUTE +Z L233-241 + `head` part L244-251 + `pump_press` PRISMATIC +Z L253-261 + `_head_mesh` L113-161（长鹅颈 `tube_from_spline_points` 11 点高拱至 z≈0.304）| eligible if compatible | 长曲鹅颈乳液泵：保留 swivel+press（massless carrier），短嘴换成高拱长鹅颈出嘴（高出 head 至 0.304，外伸至 0.088）+ 长 dip tube 入瓶底 |
| twist_lock_pump | rec_container_pump_var_twist_lock_pump | `lock_ring` part L295-301 + `twist_lock` REVOLUTE +Z 限位 0..π/2 L306-314 + `head` part L317-324 + `pump_press` PRISMATIC +Z L327-335 + `_lock_ring_mesh` L123-173（grip ribs + bayonet lugs）+ `_head_mesh`（cam pins）L176-233 | eligible if compatible | 旋转锁定下压泵：`twist_lock` REVOLUTE +Z **限位**（解锁 0 ↔ 锁死 π/2）→ `pump_press` PRISMATIC +Z；bayonet lug + cam pin，锁死位 cam 头下压封住行程；**无 massless carrier**（lock_ring 是实体 part）；2 活动件，弯嘴 spout + 长 dip tube |
| trigger_sprayer | rec_container_pump_var_trigger_sprayer | `sprayer_head` part L267-283 + `sprayer_swivel` REVOLUTE +Z L286-294 + `trigger` part L297-303 + `trigger_squeeze` REVOLUTE -Y L308-316 + `_sprayer_body_mesh` L124-139 + `_nozzle_mesh` L142-155 + `_trigger_lever_mesh` L193-212 | eligible if compatible | 扳机喷雾头：`sprayer_swivel` REVOLUTE +Z（整头回转瞄准）→ `trigger_squeeze` REVOLUTE -Y（手指扳机绕 pivot @(0.020,0,0.196) 摆动 0..0.55 回弹）；前伸 nozzle off-axis(+X 0.046) + 长 dip tube 入瓶底；2 REVOLUTE 活动件 |
| flip_top_cap | rec_container_pump_var_flip_top_cap | `collar` part（含 hinge lugs + orifice）L237-251 + `flip_cap` part L254-260 + `cap_hinge` REVOLUTE -X L265-275 + `_cap_disc_mesh` L164-201 + `_collar_mesh`（hinge lugs+plate+orifice）L91-148 | eligible if compatible | 翻盖碟形盖：`cap_hinge` REVOLUTE axis=(-1,0,0) @ 后 rim hinge pin（origin (0, HINGE_Y, HINGE_Z)），q=0 闭合盖座 collar top、正 q（0..2.4）上翻露出 collar 顶 dispensing orifice；**去泵 / 去 dip tube**；1 活动件 |
| disc_top_cap | rec_container_pump_var_disc_top_cap | `cap_base` part L250-256 + `collar_to_cap_base` FIXED L262-268 + `disc` part L273-288 + `cap_to_disc` PRISMATIC +Z L290-300 + `_cap_base_cadquery` L142-176（bore + dispensing slot）+ grip nubs for-i L280-283 | eligible if compatible | 碟形顶按压盖：`cap_base` FIXED 挂 collar（带 bore + 侧 +X dispensing slot）→ 中央 `disc` 圆碟 `cap_to_disc` PRISMATIC +Z 下压（-0.004 回弹）开缝；**去泵 / 去 dip tube**；1 PRISMATIC 活动件 + fixed 中间件 |

硬约束记录：dispenser_head 7 candidate（超 3-6 目标，因这是主机构槽且源池真实覆盖 7 族）。含 REVOLUTE+PRISMATIC（press / foaming / gooseneck：swivel +Z + press +Z，经 massless carrier）/ REVOLUTE 限位+PRISMATIC（twist_lock：lock_ring 实体 + press）/ 双 REVOLUTE（trigger_sprayer：swivel +Z + squeeze -Y）/ 单 REVOLUTE（flip_top_cap：hinge -X）/ FIXED+PRISMATIC（disc_top_cap：cap_base fixed + disc push +Z）等不同 joint 拓扑 + 不同 part count + 有 / 无 dip tube。每个 candidate **≥1 non-fixed joint**（满足 §3 ≥1 活动机构；screw_cap_only 纯旋盖因 0 非 fixed joint 被排除，见排除项）。

## 槽位图（slot graph）

pattern: parallel_children（`bottle` 为 root 坐地 z=0；`collar` FIXED 挂 bottle 作共享接口；dispenser_head 各候选挂 collar；无 multiplicity）

```
bottle(body_profile)  [ROOT, 坐地 z=0, label_band + neck_threads visual]
   │
   └── bottle --[bottle_to_collar: FIXED @ (0,0,0)]--> collar  [共享 mating interface, neck rim top z≈0.176]
         │
         ├── dispenser_head = press_pump / foaming_pump / gooseneck_pump:
         │     collar --[pump_swivel: REVOLUTE +Z @ neck rim]--> head_carrier(massless, carrier_hub visual)
         │            head_carrier --[pump_press: PRISMATIC +Z]--> head/foamer_head (cap+spout/chamber+stem+dip_tube)
         │
         ├── dispenser_head = twist_lock_pump:
         │     collar --[twist_lock: REVOLUTE +Z 限位 0..π/2 @ neck rim]--> lock_ring (实体, grip ribs+bayonet lugs)
         │            lock_ring --[pump_press: PRISMATIC +Z]--> head (cap+spout+stem+cam pins+dip_tube)
         │
         ├── dispenser_head = trigger_sprayer:
         │     collar --[sprayer_swivel: REVOLUTE +Z @ neck rim]--> sprayer_head (body+nozzle+stem+dip_tube)
         │            sprayer_head --[trigger_squeeze: REVOLUTE -Y @ (0.020,0,0.196)]--> trigger (finger lever)
         │
         ├── dispenser_head = flip_top_cap:
         │     collar(+hinge lugs + dispensing orifice) --[cap_hinge: REVOLUTE -X @ 后 rim pin]--> flip_cap (disc+tab)
         │
         └── dispenser_head = disc_top_cap:
               collar --[collar_to_cap_base: FIXED]--> cap_base (bore + 侧 +X slot)
                    cap_base --[cap_to_disc: PRISMATIC +Z @ bore floor]--> disc (tile + grip nubs)
```

接口点位与 joint 语义：
- **collar 共享接口（恒定）**：`bottle_to_collar` FIXED @ (0,0,0)；collar 白色螺纹领圈罩 over neck（NECK_R 0.0150，COLLAR_R 0.0185，COLLAR_TOP 0.176）。所有 body_profile 候选的 neck 都为轴对称 round（即使 boxy_oval / tall_rectangular 的瓶身是 superellipse / 矩形，肩部 loft 收到**圆 neck**，见 boxy_oval L92-93 / tall_rectangular L69-85），故 collar mating face 跨 body 一致。
- **swivel / press 接口（press / foaming / gooseneck）**：`pump_swivel` origin @ (0,0,0)（落在 neck rim 中心轴），axis +Z REVOLUTE（-π..π 回转）；经 massless `head_carrier`（carrier_hub 低 flange 坐 collar top z≈0.178）→ `pump_press` origin @ (0,0,0)，axis +Z PRISMATIC（lower=-0.015，upper=0，q=0 rest）。carrier 解耦旋转 / 平移共享 +Z。
- **twist_lock 接口**：`twist_lock` origin @ (0,0,0)，axis +Z REVOLUTE **限位 0..π/2**；lock_ring 是实体 part（坐 collar top，grip ribs + bayonet lugs），`pump_press` parent=lock_ring（不经 massless carrier）。锁死位（twist=π/2）+ press 共同把头 cam 到更低 z（封住行程语义）。
- **trigger 接口**：`sprayer_swivel` origin @ (0,0,0) axis +Z REVOLUTE → `trigger_squeeze` origin @ (TRIGGER_PIVOT_X=0.020, 0, TRIGGER_PIVOT_Z=0.196)，axis -Y REVOLUTE（0..0.55 squeeze）；pivot 在 sprayer_body 前侧 boss 硬件上。
- **flip 接口**：`cap_hinge` origin @ (0, HINGE_Y=COLLAR_R-0.002, HINGE_Z=COLLAR_TOP+LUG_HEIGHT/2)，axis -X REVOLUTE（0..2.4），落在 collar 后 rim hinge pin 硬件；q=0 闭合坐 collar top plate、正 q 上翻露 orifice。collar 此候选额外发射 hinge lugs + top plate + dispensing orifice visual。
- **disc 接口**：`collar_to_cap_base` FIXED → `cap_to_disc` origin @ (0,0,DISC_REST_BOTTOM=0.184)（bore floor 实际接触面），axis +Z PRISMATIC（-0.004..0），disc 圆碟在 cap_base bore 内下压。
- **mating policy（captured / 友配）**：所有 head 的 stem / carrier hub / lock ring / cap_base / flip cap tab 与 collar bore / collar top 是 captured / nested fit（故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（落在真实 neck rim / hinge pin / bore floor 硬件）+ element-scoped `allow_overlap`（见各 record run_tests：collar↔bottle skirt / head stem↔collar bore / dip_tube↔bottle_shell / cap tab↔collar lugs / disc↔cap_base bore）守 overlap。
- **rest pose**：所有泵 / 碟 q=0 坐下（press=0 / disc=0）；twist q=0 解锁、flip cap q=0 闭合、trigger q=0 下垂、swivel q=0 spout 指 +X。下压 / 翻起 / 回转 / squeeze 为 viewer 目检的活动语义。
- **互斥 / 可选**：dispenser_head 各候选互斥（一次只一种顶部机构）。`head_carrier` massless part 仅 press / foaming / gooseneck 发射；`lock_ring` 仅 twist_lock；`cap_base` fixed 中间件 + dispensing slot 仅 disc_top_cap；hinge lugs + orifice 仅 flip_top_cap。dip_tube 仅泵 / sprayer 类发射（flip / disc 去内管）。

## 每槽位 Module Emits / Interfaces

### Slot A / `bottle`（body_profile，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bottle`（visual: `bottle_shell` 中空壳 + `label_band` 缠绕 sleeve + `neck_threads` 螺纹圈）| parent `_bottle_mesh` L47-69 / boxy_oval `_bottle_mesh`+`_label_mesh` L84-134 / tapered `_bottle_mesh` L85-121 / tall_rect `_bottle_mesh`+`_label_mesh` L52-141 |
| internal joints | 无（root 瓶身本身无活动件）| — |
| upstream interface | 坐地 z=0（root）| 各 `BOTTLE_BOTTOM=0.0` |
| downstream interface | round neck rim top 中心 (0,0,~0.176)（collar 的 FIXED parent 接口；跨 body 恒定）| 各 `NECK_TOP`/`COLLAR_TOP` |

### Slot Shared / `collar`（共享 mating interface，FIXED 挂 bottle）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `collar`（visual: `collar_shell` 螺纹领圈 + `collar_knurl` 滚花；flip_top_cap 额外 hinge lugs + top plate + orifice）| parent `_collar_mesh` L82-96 / `_collar_knurl_mesh` L99-108 / flip `_collar_mesh` L91-148 |
| internal joints | `bottle_to_collar` FIXED @ (0,0,0) | parent L205-211 |
| downstream interface | collar top rim z≈0.176（dispenser_head 各 joint 的 parent 接口）| parent `COLLAR_TOP` L42 |

### Slot B / dispenser_head（每候选发射对应活动机构）
| emits | 描述 | 来源 |
|---|---|---|
| parts | press/gooseneck: `head_carrier`(massless)+`head` ／ foaming: `head_carrier`+`foamer_head` ／ twist: `lock_ring`+`head` ／ trigger: `sprayer_head`+`trigger` ／ flip: `flip_cap` ／ disc: `cap_base`(fixed)+`disc` | 各 head 源 |
| internal joints | `pump_swivel` REVOLUTE +Z + `pump_press` PRISMATIC +Z（press/foaming/gooseneck）／ `twist_lock` REVOLUTE +Z 限位 + `pump_press` PRISMATIC +Z（twist）／ `sprayer_swivel` REVOLUTE +Z + `trigger_squeeze` REVOLUTE -Y（trigger）／ `cap_hinge` REVOLUTE -X（flip）／ `collar_to_cap_base` FIXED + `cap_to_disc` PRISMATIC +Z（disc）| parent L224-252 / foaming L274-306 / gooseneck L233-261 / twist L306-335 / trigger L286-316 / flip L265-275 / disc L262-300 |
| upstream interface | 挂 collar top rim z≈0.176（swivel/twist/sprayer_swivel/cap_hinge/collar_to_cap_base 的 parent=collar）| 各 articulation parent=collar |
| downstream interface | dip_tube 入瓶腔（press/foaming/gooseneck/twist/trigger；flip/disc 无）| 各 `_dip_tube_mesh` |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_profile | enum | round_body / boxy_oval / tapered_waisted / tall_rectangular | round_body | choice | deterministic procedural sampler 选 | module table |
| dispenser_head | enum | press_pump / foaming_pump / gooseneck_pump / twist_lock_pump / trigger_sprayer / flip_top_cap / disc_top_cap | press_pump | choice | sampler 选 | module table |
| palette_style | enum | clear_white_pump / amber_natural / frosted_sage / cobalt_clinical / matte_charcoal / pearl_blush / ceramic_ivory / chrome_apothecary / soft_touch_olive（9 colorway，各带 finish 维度，详见 §配色表）| clear_white_pump | palette | palette only，**不计入 slot_choice**；每 seed `rng.choice` 抽一个 | palette（5★ 材质综合 + 真实推断）|
| body_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放瓶体高度 H → SHOULDER/NECK/COLLAR z 同比上移 → head mount 高度，clamp | resolve clamp |
| body_radius_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放瓶身半径 / 半宽半深（BODY_R / BODY_W / BODY_D / BASE_R）→ 不动 round neck，clamp | resolve clamp |
| neck_radius_scale | float | [0.92, 1.08] | 1.0 | equation | `NECK_R = base · neck_radius_scale`；`COLLAR_R = NECK_R + 0.0035`、head stem bore / lock_ring bore / cap_base bore 半径派生跟随（保接口配合）| resolve clamp |
| head_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放 head / foamer chamber / gooseneck arc / sprayer body 高度，clamp（不破 swivel/press origin）| resolve clamp |
| press_travel_scale | float | [0.80, 1.15] | 1.0 | independent | 缩放 `pump_press` / `cap_to_disc` 行程 + twist cam 下沉量，clamp（≤ stem 入瓶深度） | resolve clamp |
| spout_reach_scale | float | [0.85, 1.20] | 1.0 | conditional | 缩放 spout / nozzle / gooseneck 外伸量；上限随 dispenser_head（gooseneck 高、foaming 短）解析 | resolve clamp |
| (—) | constraint | — | — | inequality | 接口配合：`head_bore_R ≥ NECK_R + clearance` 且 `dip_tube_bottom ≥ BOTTLE_BOTTOM + 0.004`（dip tube 不穿底）；违反按比例回缩 neck_radius / press_travel scale | 接口 / clearance |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`neck_radius_scale` 为 equation（COLLAR_R + 各 head bore 半径跟随 neck，保证机构罩 collar 的配合不破）。`spout_reach_scale` 为 conditional（上限依赖所选 head）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 body_profile / dispenser_head 的拓扑。

## Palette Style 配色表（palette-only，9 coordinated colorways + finish 维度）

> `palette_style` 是 **palette-only** 维度（**不计入 slot_choice**，不改任何 slot / candidate / multiplicity / joint / dimension / topology）：每 seed `rng.choice(PALETTE_STYLES)` 抽一个，把该 colorway 的 per-component 颜色 + finish 应用到 body / collar / pump-mech 材质组。9 个配色覆盖真实 lotion / soap / cosmetic pump 瓶常见外观，并显式声明 **material-finish 维度**（clear gloss / frosted translucent / opaque matte / amber translucent / soft-touch matte / ceramic glaze / metallic-chrome pump / pearlescent）。clear / frosted / amber 携 alpha<1.0；不透明 / 软触 / 陶釉 / 珠光携 alpha=1.0；metallic/chrome pump 用偏冷高反 RGBA 模拟镀铬。RGBA 锚定 5★ 现存材质（parent + foaming/twist 变体），推断 colorway 用同族真实取色。
>
> 每个 colorway = **bottle body（bottle_shell + neck_threads）** + **pump/dispenser head（head_shell / foamer / spout / actuator）** + **collar / accent（collar_shell + collar_knurl + grip/lock 件）** + **dip_tube** + **label**，外加一列 **finish（material-finish 维度）**。

| # | palette_style | finish（material-finish 维度）| bottle body rgba | pump/dispenser head rgba | collar / accent rgba | dip_tube rgba | label rgba | 备注 / 锚 |
|---|---|---|---|---|---|---|---|---|
| 1 | clear_white_pump（基线 / parent）| clear gloss（瓶身透明，泵头亮白）| clear `(0.74, 0.80, 0.82, 0.25)` | white `(0.93, 0.93, 0.94, 1.0)` | white collar `(0.93, 0.93, 0.94, 1.0)` | tube_white `(0.88, 0.90, 0.90, 0.85)` | warm white `(0.96, 0.96, 0.94, 1.0)` | parent 5★ 原值（透明瓶 + 白泵）|
| 2 | amber_natural | amber translucent（琥珀半透瓶 + 哑白泵）| amber `(0.55, 0.32, 0.10, 0.45)` | bone `(0.92, 0.90, 0.84, 1.0)` | bronze collar `(0.66, 0.50, 0.30, 1.0)` | amber tube `(0.55, 0.34, 0.14, 0.70)` | kraft `(0.86, 0.78, 0.62, 1.0)` | 天然 / 精油按压瓶；amber 携 alpha |
| 3 | frosted_sage | frosted / translucent（磨砂半透）| frosted sage `(0.70, 0.78, 0.68, 0.55)` | soft white `(0.94, 0.95, 0.93, 1.0)` | frosted collar `(0.80, 0.85, 0.78, 0.75)` | frosted tube `(0.82, 0.86, 0.80, 0.65)` | sage label `(0.74, 0.80, 0.70, 1.0)` | 磨砂玻璃感；frosted 携 alpha |
| 4 | cobalt_clinical | opaque matte（不透明诊所蓝）| cobalt `(0.13, 0.28, 0.52, 1.0)` | white `(0.95, 0.96, 0.97, 1.0)` | white collar `(0.95, 0.96, 0.97, 1.0)` | tube_white `(0.88, 0.90, 0.90, 0.85)` | white `(0.97, 0.97, 0.97, 1.0)` | 药妆 / 临床按压瓶；纯不透明 |
| 5 | matte_charcoal | soft-touch matte（软触哑黑）| charcoal `(0.16, 0.16, 0.18, 1.0)` | matte black `(0.10, 0.10, 0.11, 1.0)` | charcoal collar `(0.22, 0.22, 0.24, 1.0)` | dark tube `(0.18, 0.18, 0.20, 0.90)` | silver label `(0.78, 0.79, 0.80, 1.0)` | 男士 / 高端软触；软触哑面 |
| 6 | pearl_blush | pearlescent（珠光裸粉）| pearl blush `(0.95, 0.86, 0.86, 1.0)` | pearl white `(0.97, 0.94, 0.94, 1.0)` | rose-gold collar `(0.86, 0.66, 0.58, 1.0)` | blush tube `(0.93, 0.84, 0.84, 0.90)` | blush label `(0.96, 0.90, 0.90, 1.0)` | 美妆乳液；珠光高光 |
| 7 | ceramic_ivory（新增）| ceramic glaze（陶瓷釉面象牙）| ivory glaze `(0.94, 0.91, 0.84, 1.0)` | ivory glaze `(0.95, 0.92, 0.86, 1.0)` | brass collar `(0.78, 0.66, 0.40, 1.0)` | ivory tube `(0.90, 0.87, 0.80, 0.90)` | taupe label `(0.80, 0.74, 0.64, 1.0)` | 民宿 / 浴室陶瓷釉感；釉面不透明 |
| 8 | chrome_apothecary（新增）| metallic / chrome pump（透明药剂瓶 + 镀铬泵头）| clear amber `(0.62, 0.46, 0.24, 0.40)` | chrome `(0.82, 0.84, 0.87, 1.0)` | chrome collar `(0.80, 0.82, 0.85, 1.0)` | smoke tube `(0.55, 0.55, 0.58, 0.75)` | charcoal label `(0.20, 0.20, 0.22, 1.0)` | 药剂房风；金属/镀铬泵头（偏冷高反），瓶携 alpha |
| 9 | soft_touch_olive（新增）| soft-touch matte（软触哑橄榄绿）| olive `(0.28, 0.32, 0.20, 1.0)` | matte black `(0.11, 0.12, 0.10, 1.0)` | olive collar `(0.34, 0.38, 0.26, 1.0)` | dark tube `(0.16, 0.18, 0.14, 0.90)` | cream label `(0.90, 0.88, 0.78, 1.0)` | 草本 / 男士护理；软触哑面 |

finish 维度取值集合（material-finish dimension）：`clear_gloss` / `frosted_translucent` / `opaque_matte` / `amber_translucent` / `soft_touch_matte` / `ceramic_glaze` / `metallic_chrome_pump` / `pearlescent`。finish 仅影响材质外观语义（alpha 是否 <1.0、是否高反 / 软触 / 釉面），**不改任何几何 / slot / joint**。alpha<1.0 仅 clear / frosted / amber 瓶身及对应 dip_tube；不透明 / 软触 / 陶釉 / 珠光 / chrome 件 alpha=1.0（dip_tube 沿用各 colorway 自带半透 / 不透明值）。bottle_shell 的 `rgba[3]<1.0` 透明断言仅对 clear / frosted / amber 三个 colorway 成立（5★ 中 parent 透明瓶继承）；不透明 colorway 不挂该断言（per-colorway 适配，见 §Validator）。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（body_profile + dispenser_head + 共享 collar）表达，不暴露 `*_count`，也不通过循环复制模板级 visual / part / joint。单瓶单机构。
- 说明：Slot B 内部少量同构装饰（如 collar knurl 22 ribs、disc 4 grip nubs、foamer 16 grip ribs、twist 6 grip ribs + 2 bayonet lugs / 2 cam pins）用 module-local `for i in range(n)` 发射，是固定常量数量的 module-local 细节，**不是模板级 multiplicity 轴**（n 不暴露为采样参数）。

## 拓扑多样性审计

总组合数：body_profile(4) × dispenser_head(7) = **28**（palette_style 是 palette，不计组合）。

理由：本类拓扑多样性来源充裕——body_profile(4) × dispenser_head(7) 的笛卡尔积即 28 distinct，远超 10。dispenser_head 引入真实不同 joint 拓扑 + part count：REVOLUTE+PRISMATIC 经 massless carrier（press / foaming / gooseneck，3 part）/ REVOLUTE 限位+PRISMATIC（twist_lock，lock_ring 实体，无 carrier）/ 双 REVOLUTE（trigger_sprayer：swivel +Z + squeeze -Y，2 活动件）/ 单 REVOLUTE -X（flip_top_cap，去泵去内管）/ FIXED+PRISMATIC +Z（disc_top_cap，cap_base fixed 中间件）。body_profile 改 root bottle 的 shell 发射方式（lathe / superellipse loft / CadQuery rect-extrude）与截面族。slot_choices 编入两轴。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 两个 named slot（笛卡尔积近全合法，少量 gating 见下），再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除 / 适配易坏组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 28（28 组合的采样空间足够覆盖）。低于 300 的原因：本小类真实结构词汇就是 4 body × 7 head = 28，是该类目的合理上限（源池单轴 diff 决定的真实家族数），不强行注水到 100。28 ≫ 10 门槛充裕。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 6 个 scale（body_height / body_radius / neck_radius / head_height / press_travel / spout_reach）。全部 `resolve_config` clamp + 每 build 统一应用。`neck_radius_scale` 为 equation（COLLAR_R + 各 head bore 半径派生跟随）、`spout_reach_scale` 为 conditional（上限依赖所选 head）。接口配合 / dip-tube 不穿底不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏 head joint origin（neck rim / hinge pin / bore floor）、机构罩 collar 配合、dip tube 入腔或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 两 named slot（近全正交），再 uniform 各 scale + `rng.choice` palette_style | slot_choices_for_seed 含两轴且与 build 一致 |
| compatibility matrix | (1) 28 组合全合法（任一 body × 任一 head）——collar / round neck 接口跨 body 恒定，任一 head 复用同一 mating face。(2) `flip_top_cap` / `disc_top_cap` 去泵 + 去 dip_tube → 不发射 dip_tube / head_carrier，避免悬空内管（resolve 解析 emit 集合，不 gate 掉组合）。(3) `twist_lock_pump` 用实体 lock_ring 替 massless carrier；`pump_press` parent=lock_ring。(4) head bore / lock_ring bore / cap_base bore 半径由 neck_radius equation 驱动，避免窄 neck 时穿 collar 或宽 neck 时浮空。(5) dip_tube 长度 clamp 到 `≥ BOTTLE_BOTTOM+0.004` 不穿底（body_height_scale 缩放后在 resolve 重算）。无硬 gate-out | 无 floating / collision / head 穿瓶 / dip tube 穿底 / joint 轴或 origin 错位 / closed-pose 错位 |
| controlled local variation | 6 个 clamped scale，每 build 统一；neck_radius equation 驱动 head/lock/cap bore，spout_reach conditional 随 head | 比例变化不破坏 head joint origin / 机构罩 collar 配合 / 坐地 / dip tube 入腔 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | 机构动作（press / swivel / twist / squeeze / flip / disc）/ 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_profile | 4 | yes | yes | round（lathe）/ boxy_oval（superellipse loft）/ tapered_waisted（waisted lathe）/ tall_rectangular（CadQuery rect-extrude）|
| dispenser_head | 7 | yes | yes | press / foaming / gooseneck（REV+PRIS+massless carrier）/ twist_lock（REV 限位+PRIS）/ trigger_sprayer（双 REV）/ flip_top_cap（REV -X）/ disc_top_cap（FIXED+PRIS）|

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_profile, dispenser_head) 两轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling
- `resolve_config` 各 scale clamp 到声明范围；neck_radius equation 驱动 COLLAR_R + 各 head bore；spout_reach conditional 随 head；接口配合 + dip-tube-不穿底不等式在 resolve 内投影 / 回缩
- compatibility matrix / gating：28 组合全合法（无硬 gate-out），flip / disc 候选不发射 dip_tube / head_carrier（resolve 解析 emit 集合）
- 连续 scale clamp 后不破坏 head joint origin / 机构罩 collar 配合 / 坐地 / dip tube 入腔 / 类别身份
- 关键 joint：press/foaming/gooseneck `pump_swivel` REVOLUTE +Z (abs(axis[2])>0.99) + `pump_press` PRISMATIC +Z + massless `head_carrier`；twist_lock `twist_lock` REVOLUTE +Z 限位 (upper-lower ≤ π/2+ε) + `pump_press` PRISMATIC +Z（parent=lock_ring）；trigger `sprayer_swivel` REVOLUTE +Z + `trigger_squeeze` REVOLUTE -Y (abs(axis[1])>0.99)；flip `cap_hinge` REVOLUTE -X (abs(axis[0])>0.99)；disc `collar_to_cap_base` FIXED + `cap_to_disc` PRISMATIC +Z
- captured-fit：element-scoped `allow_overlap`（collar_shell ↔ bottle skirt / neck_threads；head_shell|stem ↔ collar_shell bore；dip_tube ↔ bottle_shell；carrier_hub ↔ collar_shell；cap_disc ↔ collar lugs；disc_tile ↔ cap_base bore；lock_ring ↔ collar）
- grandfather：机构罩 / stem captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守
- palette_style 是 palette（不计 slot_choice）；每 build `rng.choice` 抽一个 colorway（9 个，见 §Palette Style 配色表）应用到 body / collar / pump / dip_tube / label 材质组，并按各 colorway 的 finish 维度（clear gloss / frosted / opaque matte / amber / soft-touch / ceramic glaze / metallic-chrome pump / pearlescent）设 alpha / 反射语义；bottle_shell `rgba[3]<1.0` 透明断言仅对 clear / frosted / amber 三个 colorway 适配

## Reject cases

- 用纯 Box / 纯 Cylinder 占位体当瓶身 → 失类别身份；瓶身必须厚壁中空开口腔（lathe shell / superellipse loft / CadQuery rect-extrude+cut）。
- head joint origin 放在瓶底 / 任意点而非 neck rim top（swivel/press/twist/sprayer_swivel）/ 后 rim hinge pin（flip）/ bore floor（disc）真实硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- press / foaming / gooseneck 不用 massless `head_carrier` 解耦 swivel/press，直接把 REVOLUTE+PRISMATIC 串到 head 单 part → 旋转与下压耦合错误（应 collar→carrier→head 两 joint）。
- 给 dispenser_head 设成张开 / 抬起 / 下压态而非 q=0 闭合 / 坐下（press=0 / twist=0 解锁 / flip 闭合 / disc=0 / squeeze=0）→ rest pose 与 viewer 目检不符。
- flip_top_cap / disc_top_cap 还挂 dip_tube / head_carrier → 内管 / carrier 悬空无机构承载（这两候选去泵去内管）。
- 给机构罩 / stem captured-fit 补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice）。
- 加 screw_cap_only 纯旋盖（0 非 fixed joint）/ clear_dome_overcap 防尘罩当 head 候选 → 丢唯一活动机构 / 强耦合无独立 joint（见排除项）。
- neck / collar 接口跨 body 不一致（boxy_oval / tall_rectangular 肩部不收到 round neck）→ head 罩不上 collar，穿模或浮空。
- dip tube 缩放后穿瓶底 / head 抬升 / flip 翻起穿瓶壁 → 接口配合 / dip-tube-不穿底不等式或 origin 检查 FAIL。

## 与相邻类别的边界

- 不该混入：**container_dispenser（手压分配瓶 / sibling 小类）**——理由：dispenser 是**未封盖**的暴露泵分配瓶，slot 拆成 body / pump-head / **collar 螺纹细节** / **dip-tube 路径可见性** 四轴（无 closure / cap 槽，源图无任何盖件），变体强调 collar 细节（oversized_ribbed_collar）+ dip-tube 路径（curved_dip_tube）+ detached_pump_insert 可分离泵。**container_pump 的判别身份在 dispenser_head 槽同时容纳泵 + 闭合机构（flip / disc 翻 / 按盖）**，collar 是恒定共享接口（不作独立可变轴），dip-tube 不作独立可见性轴。若一个变体的核心 diff 是 collar 螺纹细节或 dip-tube 路径而机构恒定，归 dispenser；若核心 diff 是顶部机构族（泵 / 喷雾 / 翻盖 / 按盖），归 pump。
- 不该混入：**container_bottle_serum 血清瓶**——理由：serum 的 closure 槽含 dropper（滴管球泡 pipette 直拉）/ roller_ball（滚珠）/ brush_wand（刷头棒）等**小容量精华瓶涂抹 / 滴取**机构，且 body 多为琥珀玻璃小瓶；pump 是较大容量 lotion / soap 按压泵瓶，机构是 press pump / sprayer / 翻按盖。serum 的 pump_dispenser_prismatic 候选与本类 press_pump 形似，但 serum 整体是小血清瓶语境（amber glass + dropper 基线），不混入。
- 不该混入：**container_bottle 细颈瓶 / 酒瓶 + 通用 container_jar 宽口罐**——理由：bottle 是细长瓶身 + 长颈无泵机构；jar 是宽口罐 + 旋 / 翻 / 撒料盖（无泵 + dip tube + spout 的分配机构）。pump 的身份是顶部按压 / 喷雾分配机构 + collar + dip tube。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。10 个 5★（1 parent + 9 fork 变体）全读 model.py。2 slot：body_profile(4) × dispenser_head(7) = 28 combos ≫ 10 门槛。dispenser_head 是主机构槽，覆盖 7 真实 joint 拓扑（press/foaming/gooseneck=REV+PRIS+massless carrier；twist_lock=REV 限位+PRIS 实体 lock_ring；trigger_sprayer=双 REV；flip_top_cap=REV -X 单铰；disc_top_cap=FIXED+PRIS push）。collar/round-neck 为跨 body 恒定共享接口（不作可变轴，区别于 dispenser 把 collar/dip-tube 拆成独立轴）。palette_style 9 colorway（palette-only，带显式 material-finish 维度：clear gloss / frosted translucent / opaque matte / amber translucent / soft-touch matte / ceramic glaze / metallic-chrome pump / pearlescent；见 §Palette Style 配色表，RGBA 锚定 parent + foaming/twist 5★ 材质 + 同族真实推断；clear/frosted/amber 携 alpha）。无 multiplicity 轴。排除 screw_cap_only（0 活动 joint）、clear_dome_overcap 防尘罩（无独立 joint，强耦合）、纯尺寸 / 配色（→ 连续 scale + palette）。|

## 模板实现备注（可选）

- 共享 helper：`_bottle_shell(body_profile, ...)` 分派 lathe（round / waisted）/ superellipse loft（boxy_oval：`superellipse_profile`+`LoftGeometry`+`_ring_cap`）/ CadQuery rect-extrude（tall_rectangular）；`_collar(neck_r, rim_z)` + `_collar_knurl` + `_neck_threads` 全 module 公用（跨 body 恒定 round neck 接口）。
- press / foaming / gooseneck：必须经 massless `head_carrier`（carrier_hub 低 flange visual + 1e-3 mass）解耦 `pump_swivel`(REVOLUTE +Z)→`pump_press`(PRISMATIC +Z)；foamer 换宽 chamber + actuator + 短 dip tube；gooseneck 换长 `tube_from_spline_points` 鹅颈。
- twist_lock：lock_ring 是**实体** part（替 massless carrier），`twist_lock` REVOLUTE +Z **限位 0..π/2**，`pump_press` parent=lock_ring；bayonet lugs（lock_ring）+ cam pins（head stem）为 module-local for-i 装饰。
- trigger_sprayer：`sprayer_swivel`(REVOLUTE +Z) → `trigger_squeeze`(REVOLUTE -Y @ pivot (0.020,0,0.196))；pivot bosses 为 sprayer_head 内联 visual（非独立 part）。
- flip_top_cap：collar 此候选额外发射 hinge lugs + top plate + dispensing orifice；`cap_hinge` REVOLUTE axis=(-1,0,0) @ 后 rim pin；**不发射 dip_tube / head_carrier**。
- disc_top_cap：`collar_to_cap_base` FIXED 中间件（bore + 侧 +X dispensing slot，CadQuery cut）→ `cap_to_disc` PRISMATIC +Z @ bore floor (z=0.184)；grip nubs for-i 装饰；**不发射 dip_tube / head_carrier**。
- captured-fit overlap：`run_container_pump_tests` 里复制各 record 的 `ctx.allow_overlap`（collar↔bottle skirt/neck_threads、head stem↔collar bore、dip_tube↔bottle_shell、carrier_hub↔collar、cap tab↔collar lugs、disc↔cap_base bore、lock_ring↔collar）；`ctx.expect_overlap(collar, bottle, axes="z", min_overlap=0.005)` collar 坐 neck。
- neck_radius equation：`resolve_config` 派生 `COLLAR_R = NECK_R + 0.0035`、head/lock/cap bore = NECK_R + clearance；接口配合 + dip-tube-不穿底不等式在 resolve 投影。
- palette_style：9 colorway（见 §Palette Style 配色表）各自给 (bottle_shell / neck_threads / label / collar / pump-mech / dip_tube / accent) 材质组 + 一列 finish（material-finish 维度）；clear_white_pump=parent (clear 0.74,0.80,0.82,0.25 + white 0.93,0.93,0.94)，amber_natural / frosted_sage / cobalt_clinical / matte_charcoal / pearl_blush / ceramic_ivory / chrome_apothecary / soft_touch_olive 为同族真实 lotion-soap-cosmetic 配色（含 amber 半透、磨砂、不透明、软触哑面、陶瓷釉、镀铬泵头、珠光）。finish→材质外观（alpha / 高反 / 软触 / 釉面），不改几何。`run_container_pump_tests` 的 bottle_shell `rgba[3]<1.0` 透明断言改为 per-colorway 适配（仅 clear / frosted / amber 三个 colorway 断言透明，不透明 colorway 不挂该断言），其余 allow_overlap / grandfather 不受 palette 影响。
- 参考模板：`agent/templates/Container_Jar.py`（Config/ResolvedConfig + `config_from_seed` + `resolve_config` clamp + `slot_choices_for_config` + `run_<stem>_tests` 的 allow_overlap + element-scoped grandfather 骨架，与本类 body×closure 两轴结构高度同源）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/shared | round_body + press_pump + collar | rec_clear-soap-dispenser-bottle-..._74587dd4（parent）| `_bottle_mesh` L47-69 / `_collar_mesh` L82-96 / `bottle_to_collar` FIXED L205-211 / `pump_swivel` REVOLUTE L224-232 / `head_carrier` L214-219 / `pump_press` PRISMATIC L244-252 / `_dip_tube_mesh` L155-159 | 圆瓶 body 基线 + collar 共享接口 + 按压泵机构（massless carrier）|
| S2 | A | boxy_oval | rec_container_pump_var_boxy_oval | `_bottle_mesh` L84-114（`superellipse_profile`+`LoftGeometry`+`_ring_cap`）/ `_label_mesh` L119-134 | 超椭圆圆角矩形截面瓶身 loft 到 round neck |
| S3 | A | tapered_waisted | rec_container_pump_var_tapered_waisted | `_body_radius_at` L56-82 / `_bottle_mesh` L85-121（waisted lathe）| 收腰锥形瓶身 lathe 侧轮廓 |
| S4 | A | tall_rectangular | rec_container_pump_var_tall_rectangular | `_bottle_mesh` L52-115（CadQuery rect-extrude + rect→rect loft 肩 + 圆 neck + cut）/ `_label_mesh` L118-141 | 高直角矩形 slab 瓶身 |
| S5 | B | foaming_pump | rec_container_pump_var_foaming_pump | `head_carrier`+`pump_swivel` L266-282 / `foamer_head`+`pump_press` L285-306 / `_foamer_chamber_mesh` L127-147 / `_actuator_mesh` L165-176 / `_short_dip_tube_mesh` L205-213 | 高大胖泡沫泵头（宽混合腔 + 平顶 actuator + 短嘴 + 短内管）|
| S6 | B | gooseneck_pump | rec_container_pump_var_gooseneck_pump | `head_carrier`+`pump_swivel` L223-241 / `head`+`pump_press` L244-261 / `_head_mesh` L113-161（长鹅颈 `tube_from_spline_points`）| 长鹅颈乳液泵头 |
| S7 | B | twist_lock_pump | rec_container_pump_var_twist_lock_pump | `lock_ring`+`twist_lock` REVOLUTE 限位 L295-314 / `head`+`pump_press` L317-335 / `_lock_ring_mesh` L123-173 / `_head_mesh`（cam pins）L176-233 | 旋转锁定下压泵（实体 lock_ring + bayonet + cam）|
| S8 | B | trigger_sprayer | rec_container_pump_var_trigger_sprayer | `sprayer_head`+`sprayer_swivel` L267-294 / `trigger`+`trigger_squeeze` REVOLUTE -Y L297-316 / `_nozzle_mesh` L142-155 / `_trigger_lever_mesh` L193-212 | 扳机喷雾头（swivel + 扳机 squeeze）|
| S9 | B | flip_top_cap | rec_container_pump_var_flip_top_cap | `collar`（hinge lugs+orifice）L237-251 / `flip_cap`+`cap_hinge` REVOLUTE -X L254-275 / `_cap_disc_mesh` L164-201 | 翻盖碟形盖（去泵去内管）|
| S10 | B | disc_top_cap | rec_container_pump_var_disc_top_cap | `cap_base`+`collar_to_cap_base` FIXED L250-268 / `disc`+`cap_to_disc` PRISMATIC L273-300 / `_cap_base_cadquery` L142-176 | 碟形顶按压盖（fixed cap_base + push disc，去泵去内管）|
</content>
</invoke>
