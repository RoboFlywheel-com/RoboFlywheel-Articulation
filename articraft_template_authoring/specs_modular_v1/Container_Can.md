# container_can (metal beverage/food/tin can with a lid closure) — Modular Spec

> 来源小类：`picture/Container/Can`（articraft_data 上游 Container/Can fork-variant pool）。
> 本 spec 逐一读取 6 个 parent + 8 个 `rec_container_can_var_*` 变体的 `revisions/rev_000001/model.py`（共 14 个 record，全读，未抽样）。
> 引用 `model.py:Lx-Ly` 来自各样本 `arti-template` 当前 `revisions/rev_000001/model.py`；以 part/joint/helper **名字** 为准（`_body_solid` / `_rounded_square_prism` / `_hex_body` / `_flask_body` / `_tub_solid` / `_lid_solid` / `_hex_lid` / `_neck_solid` / `_cap_mesh` / `_body_with_rim` / `body_to_lid` / `tin_to_lid` / `tub_to_lid` / `body_to_carrier` / `carrier_to_cap` / `cap_rotate` / `cap_slide` / `lid_hinge` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_can` |
| template path | `agent/templates/Container_Can.py` |
| test path (optional) | `tests/agent/test_container_can_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots: body_shape + closure；body 为 root 中空壳，closure（盖/帽）挂到 body 共同 parent，无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 14（6 parent + 8 `rec_container_can_var_*` 单轴控制变体）|
| read_count | 14（全读，未抽样）|
| read_scope | all 5-star samples in this category（6 parent + 全部 8 variant）|
| source_index_policy | only adopted module sources are indexed below（见 §Module Source Index）|

逐样本结构确认（读码）：
- **共同功能层** = body（root，中空壳：floor + 四壁/筒壁/棱壁，开口在 +Z；CadQuery `extrude`/`box`/`loft`/`polygon` 发射真实开口腔）+ closure（lid/cap，盖住口部）。这是 body + closure 的 parallel_children 结构，closure 是唯一（或主要）活动关节。
- **closure 关节类型现状**：lift-off 类用 PRISMATIC（沿 +Z 直拔，盖裙裹住口沿：`body_to_lid` / `tin_to_lid` / `tub_to_lid` / `lid_lift`）；screw 类用 CONTINUOUS + PRISMATIC 经 massless carrier 解耦旋拧 + 提起（fuel-flask parent 是 `cap_rotate`(CONT)→`cap_slide`(PRIS)；3 个 screwcap 变体反过来是 `body_to_carrier`(PRIS)→`carrier_to_cap`(CONT)，两种顺序都合法）；hinge 类用 REVOLUTE 绕后口沿水平 +X 轴（`body_to_lid` / `lid_hinge`）。
- **无 `for i in range(n)` 模板级结构复制层**——罐/盒本身不含 N 个同构子件；样本里的 `for i in range(THREAD_COUNT)` / `for i in range(n_ridges)` / `for i in range(N_GRIP_RIBS)` 全是螺纹圈 / 滚花 / 防滑筋的**装饰循环**，非小类级 multiplicity 轴（见 §Multiplicity）。
- **§4 可读性契约**：14 个样本均按功能层命名（body/tin_body/tub + lid/cap/screw_cap/cap_carrier + helper `_body_solid`/`_tub_solid`/`_hex_body`/`_flask_body`/`_lid_solid`/`_hex_lid`/`_cap_mesh`/`_neck_solid`/`_body_with_rim` 等），曲面用 CadQuery loft/extrude/polygon、cap 用 CylinderGeometry+Torus / KnobGeometry mesh，装饰（label/marker/grip_rib）内联为 parent.visual，joint 锚在真实口沿/颈面/后铰边 → 全部达标。

冗余/分流说明：
- **同格收敛冗余**：round_cylinder 格有 canister tin（`fb4296aa`）+ deli tub（`6b6cb24d`）两个 parent（锥壁/卷边食盒口味）；rounded_square 格有 square tin（`c6ba1d09`）+ clear food box（`926ea5c0`）两个 parent（透明扁身食盒口味）。每格只采纳金属罐基线为 body module source，clear-plastic 食盒口味仅作 palette / taper 口味折入，不另列 candidate（只换材质/比例不是新 candidate）。
- **身份提示**：本小类是金属/罐头/茶叶/食品罐（beverage/food/tin can），保留 lift-off / screw / hinge 三种封口；clear-plastic 食盒虽占同格，按身份提示归入 can（带盖食品罐），但默认 palette 偏金属。

## 核心身份

带盖的金属（或罐头/茶叶/食品）罐（lidded metal can / tin）：一只直立中空罐体，中心轴沿 +Z，底坐地 z=0，居中于 (x=0,y=0)。罐体发射为厚壁中空 shell（真实开口腔体），截面形态可为圆筒（直壁/锥壁卷边 deli）/圆角方截面（rabbet 口沿或透明扁身食盒）/正六棱柱（across-flats 茶叶罐）/扁矩 hip-flask（宽>深，圆角竖边）；罐口上方一只盖/帽按某种机构开合（**主活动语义**）：友配抬升盖（纯 PRISMATIC +Z lift-off，盖裙裹口沿/press-fit）/ 螺纹旋升盖（CONTINUOUS spin + PRISMATIC lift 经 massless carrier 解耦，knurled 螺盖坐螺纹颈）/ 后铰翻盖（REVOLUTE 绕后 rim 水平 +X 轴，盖上掀过竖直）。默认成熟域：单罐单盖（无嵌套 / 无 multiplicity / 无提环）。

不该混入：塑料桶/塑料罐身的 squeeze 容器（是 `container_plastic_can`——本类是金属/罐头罐，body 用金属 shell，封口是 lid/cap 机构而非软挤压瓶身）、带按压喷头/喷嘴的喷罐（是 `container_paint_spray`——本类封口无 actuator/喷嘴喷雾机构，只有盖/帽/铰盖）、带阀门/调压器的高压气瓶（是 `container_gas_cylinder`——本类无阀门颈/瓶肩高压结构，是常压日用罐）。

## 槽位 + 候选模块表

> **建模注记**：`body_shape` 是 body（root）的 mesh 属性（一次发射对应截面的 shell：圆筒 `extrude(circle)` / 方 `box+fillet("|Z")+shell` / 六棱 `polygon(6)` / 扁矩 `box+fillet`），不是独立串联 slot。`closure` 各候选挂到 body（parallel children）。`body_shape × closure` 笛卡尔积构成拓扑多样性（见 §9）。screw / hinge 候选要求 body 在口部发射对应硬件（threaded neck / hinge ear-or-barrel），由 body module 的口部 helper 派生。

### Slot A：body_shape（罐身截面 / 形状家族——root body 的 mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_cylinder（基线）| rec_round-metal-canister-tin-with-a-lift-off-lid_..._fb4296aa | `_body_solid` L41-L53（`circle(BODY_R).extrude` 外筒 cut 内 bore）| eligible if compatible | 中空圆柱筒身,直壁,圆口沿开顶,floor 封底；taller-than-wide |
| round_tapered_tub | rec_clear-round-plastic-deli-tub-food-container-with_..._6b6cb24d | `_tub_solid` L38-L66（base→mouth `loft(ruled)` 锥壁 + 卷边 rim flange）| eligible if compatible | 圆锥壁敞口 tub（mouth 比 base 宽）+ 卷边 rim flange；wider-than-tall（deli 口味）|
| rounded_square | rec_square-metal-tin-box-with-a-press-fit-lift-off-l_..._c6ba1d09 | `_rounded_square_prism` L42-L50 + `_body_solid` L53-L78（outer prism cut inner cavity + rim rabbet）| eligible if compatible | 圆角方截面中空壳（filleted 竖边）+ 内缩 rabbet 口沿；近立方 |
| hex_prism | rec_hexagonal-metal-tea-tin-with-a-lift-off-lid_..._f4f34d34 | `_hex_body` L56-L71（`polygon(6, BODY_DIAM).extrude` cut inner `polygon(6)` cavity）| eligible if compatible | 正六棱柱中空身,across-flats 截面,floor 封底开顶；taller-than-wide |
| flat_rect_flask | rec_metal-rectangular-fuel-flask-with-a-round-screw-_..._6e35123f | `_flask_body` L62-L93（`box.edges("\|Z").fillet` + `edges("\|X or \|Y").fillet` + inner cavity + mouth cut）| eligible if compatible | 扁矩 hip-flask 身,宽(X)>深(Y),圆角竖边 + 软化顶底边,真实开口腔 |

硬约束记录：body_shape 5 candidate（达 3-6 目标）。全部 CadQuery extrude/box/loft/polygon 中空开口腔，共享 floor + open-mouth helper，只换 footprint 截面（圆/锥圆/方/六棱/扁矩）/ 高宽比 / 卷边 vs rabbet 口沿。round_tapered_tub 与 round_cylinder 同为圆截面但 **loft 锥壁 + 卷边 rim** 是真实结构差异（非纯尺寸），故列为独立 candidate。

### Slot B：closure（**主开合机构槽**——罐盖/帽动作）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| lift_off_lid（基线）| rec_round-metal-canister-tin-with-a-lift-off-lid_..._fb4296aa | `_lid_solid` L56-L76（平顶 plate + 下垂 skirt 环）+ `body_to_lid` PRISMATIC +Z L113-L121 | eligible if compatible | 友配抬升盖：单 `body_to_lid`/`tin_to_lid`/`tub_to_lid`/`lid_lift` PRISMATIC +Z（无旋转），盖裙裹口沿，q=0 坐下 / 正 q 直抬离 ~0.04 m；1 joint，盖 1 part |
| press_fit_skirt_lid | rec_square-metal-tin-box-with-a-press-fit-lift-off-l_..._c6ba1d09 | `_lid_solid` L81-L98（plate + 内缩 skirt 环裹 rabbet rim）+ `tin_to_lid` PRISMATIC L134-L142 | eligible if compatible | press-fit 套盖：skirt 内缩裹 rabbet 口沿（更紧的友配捕获），PRISMATIC +Z；与 lift_off 同 joint 拓扑但 skirt 几何为方/内缩 rabbet 口味 |
| screw_cap | rec_metal-rectangular-fuel-flask-with-a-round-screw-_..._6e35123f | `_cap_mesh` L109-L130（CylinderGeometry knurl + Torus lip）+ massless `cap_carrier` L168-L169 + `cap_rotate` CONTINUOUS L184-L192 + `cap_slide` PRISMATIC L193-L201 | eligible if compatible | 螺纹颈 + 旋拧螺盖：经 massless `cap_carrier`，CONTINUOUS +Z（旋）+ PRISMATIC +Z（抬离 neck）；2 joint + 1 massless carrier。变体里顺序可为 PRIS→CONT，两种解耦顺序都合法 |
| hinge_lid | rec_container_can_var_round_hingelid | `_lid_cap` L78-L102 + `_lid_knuckle` L105-L114（hinge ear 在 body L64-L74）+ `body_to_lid` REVOLUTE axis=(1,0,0) origin=后 rim L155-L163 | eligible if compatible | 后铰翻盖：盘盖绕后 rim 水平 +X 轴 REVOLUTE，q=0 闭合盖座 rim，正 q 上翻 ~115-160°，盖与 body 在铰侧有 hinge ear/knuckle 捕获 |

硬约束记录：closure 4 candidate（达 3-6 目标）。含 PRISMATIC（lift_off / press_fit 两种 skirt 口味）/ CONTINUOUS+PRISMATIC（screw 2 joint + massless carrier）/ REVOLUTE +X（hinge）三种 joint 拓扑 + 不同 part count（lid=1 / cap+carrier=2）。每个 candidate **≥1 non-fixed joint**（满足 ≥1 活动机构）。lift_off 与 press_fit 同为 PRISMATIC 但 skirt 几何差异显著（外裹 vs 内缩 rabbet 套盖），列为独立 candidate（边界用例见 §排除项；若 reviewer 认为二者结构等价可降为 module-local skirt variant 折入 lift_off，则 closure 降 3 candidate，body×closure=15 仍过门控）。

#### Slot B 跨形状空格（变体已填，单轴控制：只换 closure，身形恒为各自最近 parent）
| 候选格 | record_id | parent(最近) | 关键 part·joint·helper 名（model.py:Lx-Ly）| 结构特征 |
|---|---|---|---|---|
| round_cylinder × screw_cap | rec_container_can_var_round_screwcap | ..._fb4296aa | `_body_solid`(neck L88-L102) + `_ring_solid` L119-L126(carrier visual) + `_cap_knob` L129-L138 + `body_to_carrier` PRIS L186-L194 + `carrier_to_cap` CONT L198-L206 | 圆筒身换螺纹颈 + 旋盖（KnobGeometry knurl + tamper ring carrier）,PRIS→CONT 顺序 |
| round_cylinder × hinge_lid | rec_container_can_var_round_hingelid | ..._fb4296aa | `_lid_cap` L78-L102 + `_lid_knuckle` L105-L114 + body hinge ear L64-L74 + `body_to_lid` REVOLUTE L155-L163 | 圆筒身换后铰翻盖,绕水平 +X 轴掀开（hinge ear + knuckle 捕获）|
| rounded_square × screw_cap | rec_container_can_var_square_screwcap | ..._c6ba1d09 | `_neck_solid` L125-L143 + `_build_screw_cap` L146-L166(KnobGeometry+skirt+bore) + `body_to_carrier` PRIS L216-L226 + `carrier_to_cap` CONT L231-L239 | 方身顶面中心立圆螺纹颈 + 旋盖（massless carrier 无 visual）|
| rounded_square × hinge_lid | rec_container_can_var_square_hingelid | ..._c6ba1d09 | `_knuckle_cylinder` L67-L75 + 交错 knuckle(body even/lid odd) L90-L95/L127-L132 + `body_to_lid` REVOLUTE L170-L181 | 方身换后铰翻盖,交错 hinge knuckle（5 段）绕后顶边 +X 掀开 ~130° |
| hex_prism × screw_cap | rec_container_can_var_hex_screwcap | ..._f4f34d34 | `_neck_tube` L105-L124 + `_screw_cap_body` L147-L178 + `_carrier_gasket` L137-L144(carrier visual) + `body_to_carrier` PRIS L258-L271 + `carrier_to_cap` CONT L274-L282 | 六棱身顶中心立圆螺纹颈 + 旋盖 + carrier gasket 密封,PRIS→CONT |
| hex_prism × hinge_lid | rec_container_can_var_hex_hingelid | ..._f4f34d34 | `_body_with_hinge`(barrel L84-L90) + `_hex_flip_lid` L94-L140(back_cut 去铰侧裙) + `body_to_lid` REVOLUTE L178-L191 | 六棱身换后铰翻盖,后顶边 hinge barrel 绕 +X 掀开 ~115° |
| flat_rect_flask × lift_off_lid | rec_container_can_var_flatrect_liftofflid | ..._6e35123f | `_body_with_rim` L71-L109(raised rim) + `_lid_solid` L112-L145(plate+skirt 裹 rim) + `lid_lift` PRISMATIC L207-L217 | 扁矩身去掉颈/螺盖/提环,改全宽 press 抬升盖（raised rim + 周裙裹 rim）+ grip ribs |
| flat_rect_flask × hinge_lid | rec_container_can_var_flatrect_hingelid | ..._6e35123f | `_top_rim` L104-L118 + `_hinge_barrel` L121-L130 + `_lid_plate` L133-L141 + lid_knuckle/lid_tab visual L192-L205 + `lid_hinge` REVOLUTE L216-L226 | 扁矩身去掉颈/螺盖/提环,改后铰翻盖（rim + hinge barrel + 前 grip tab）绕后长边 +X 掀开 ~115° |

注：每个变体单轴控制——身形恒为各自最近 parent，只替换 closure 机构。Slot A 五种身形全部由 parent 免费占据；Slot B 四种封口里 lift_off / press_fit / screw_cap 已有 parent，hinge_lid 为全新候选（8 个变体补满 body_shape × closure 网格的空格，并验证 screw / hinge 在每种 body 上的口部硬件）。

## 槽位图（slot graph）

pattern: parallel_children（body 为 root，坐地 z=0；closure（盖/帽 + 可选 massless carrier）挂到它；无 multiplicity）

```
body(body_shape)  [ROOT, 坐地 z=0, 中空开口壳]
   │  (body 口部按 closure 派生硬件：lift_off/press_fit=裸口沿 or rabbet rim；
   │   screw=中心圆螺纹 neck + access hole；hinge=后口沿 hinge ear / knuckle / barrel)
   │
   ├── closure = lift_off_lid:
   │     body --[body_to_lid: PRISMATIC +Z @ rim seam plane]--> lid
   │
   ├── closure = press_fit_skirt_lid:
   │     body --[tin_to_lid: PRISMATIC +Z @ rabbet rim seat]--> lid
   │
   ├── closure = screw_cap:
   │     body --[cap_rotate CONTINUOUS +Z @ neck top]--> cap_carrier(massless,无 visual / 或 tamper-ring/gasket visual)
   │              cap_carrier --[cap_slide PRISMATIC +Z]--> cap
   │       （等价顺序：body --[body_to_carrier PRIS +Z]--> carrier --[carrier_to_cap CONT +Z]--> cap）
   │
   └── closure = hinge_lid:
         body --[body_to_lid / lid_hinge: REVOLUTE +X @ 后 rim 边, z=rim_top]--> lid
```

接口点位与 joint 语义：
- **lift-off / press-fit 接口**：`body_to_lid`/`tin_to_lid`/`tub_to_lid`/`lid_lift` origin 在 rim seam plane 中心 `(0,0,RIM_TOP_Z - seat_overlap)`，axis +Z PRISMATIC（无旋转），q=0 盖裙裹口沿坐下 / 正 q 直抬离 ~0.04 m。press_fit 的 skirt 内缩裹 rabbet rim（更紧捕获）。
- **screw 接口**：经 massless `cap_carrier`（无 visual，或带 tamper-ring/gasket 固定 visual，1e-4 mass）解耦旋转/平移共享 +Z。两种合法顺序：(a) `cap_rotate` CONTINUOUS @ neck top → `cap_slide` PRISMATIC（fuel-flask parent）；(b) `body_to_carrier` PRISMATIC @ neck top/base → `carrier_to_cap` CONTINUOUS（3 个 screwcap 变体）。origin 落在 neck top/base 中心 `(0,0,NECK_TOP_Z)`，cap bore 套 neck（thread engagement）。
- **hinge 接口**：`body_to_lid`/`lid_hinge` origin 在后 rim 边硬件 `(0, -BODY_HALF_DEPTH, RIM_TOP_Z)`（圆=`-BODY_R`、方=`-HALF`、六棱=`-ACROSS_FLATS/2`、扁矩=`-(RIM_D/2-RIM_T)`），axis +X REVOLUTE，q=0 闭合盖座 rim、正 q 上翻 ~115-160°（hinge ear / 交错 knuckle / hinge barrel 捕获）。
- **mating policy**：盖 skirt 裹 over rim / cap bore 套 neck / knuckle 套 ear-barrel 均为 captured / 友配（盖壁与 body 几何故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（origin 落在真实 rim / neck / hinge 硬件）+ element-scoped `allow_overlap` 守 overlap（见各样本 run_tests 的 `ctx.allow_overlap`）。
- **rest pose**：所有盖 q=0 闭合 / 坐下 / 套住；lid 旋转 / 抬升 / 翻起为 viewer 目检的活动语义。
- **互斥 / 可选**：closure 各候选互斥（一次只一种封口）；`cap_carrier` massless part 仅在 screw 候选发射。

## 每槽位 Module Emits / Interfaces

### Slot A / body（body_shape，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`/`tin_body`/`tub`（visual: 中空开口 shell；按 closure 加口部硬件：threaded neck / hinge ear-or-barrel / rabbet rim）| fb4296aa `_body_solid` L41-L53 / c6ba1d09 `_body_solid` L53-L78 / f4f34d34 `_hex_body` L56-L71 / 6e35123f `_flask_body` L62-L93 / 6b6cb24d `_tub_solid` L38-L66 |
| internal joints | 无（root 罐体本身无活动件；neck/rim/ear 为 body 固定 visual）| — |
| upstream interface | 坐地 z=0（root）| — |
| downstream interface | rim seam plane / neck top / 后 rim hinge 边（closure joint 的 parent 接口）| fb4296aa RIM_TOP_Z L38 / round_screwcap NECK_TOP_Z L64 / round_hingelid HINGE_Y,HINGE_Z L49-L50 |

### Slot B / closure（每候选发射对应活动盖/帽）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `lid`（lift_off/press_fit/hinge）/ `cap`+`cap_carrier`(massless)（screw）| fb4296aa lid L98 / 6e35123f cap+carrier L168-L172 / round_hingelid lid+knuckle L137-L147 |
| internal joints | `body_to_lid` PRISMATIC +Z（lift_off）/ `tin_to_lid` PRISMATIC +Z（press_fit）/ `cap_rotate` CONT +Z + `cap_slide` PRIS +Z（或 `body_to_carrier` PRIS + `carrier_to_cap` CONT）（screw）/ `body_to_lid`/`lid_hinge` REVOLUTE +X（hinge）| fb4296aa L113-L121 / c6ba1d09 L134-L142 / 6e35123f L184-L201 / round_screwcap L186-L206 / round_hingelid L155-L163 |
| upstream interface | mount 到 body 的 rim seam / neck top / 后 rim hinge 边 | 同 joint origin |
| downstream interface | 无（叶子件）| — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_shape | enum | round_cylinder / round_tapered_tub / rounded_square / hex_prism / flat_rect_flask | round_cylinder | choice | deterministic procedural sampler 选 | module table |
| closure | enum | lift_off_lid / press_fit_skirt_lid / screw_cap / hinge_lid | lift_off_lid | choice | sampler 选 | module table |
| palette_style | enum | brushed_steel / brushed_pewter / brass_lid_accent / dark_bronze_cap / clear_pet_tint / painted_tin / glossy_print / anodized_gold / anodized_blue / hammered_tin | brushed_steel | palette | palette only，**不计入 slot_choice**；每 colorway 自带 material-finish 维度；per-seed `rng.choice` | palette（见下）|
| body_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放罐体高度 H → RIM_TOP_Z / NECK_TOP_Z / hinge_z 同步抬升,clamp | resolve clamp |
| body_radius_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放罐体半径 / 半宽 / across-flats → 口径同比,clamp（保盖裹配合）| resolve clamp |
| neck_radius_scale | float | [0.90, 1.10] | 1.0 | equation | `NECK_R = base · neck_radius_scale`；cap bore / cap_skirt 半径派生跟随（保螺盖套配合）；仅 closure=screw_cap 时生效 | resolve clamp |
| lid_height_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放盖高 / skirt 深 / cap 高,clamp | resolve clamp |
| joint_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 lid lift 行程 + hinge open limit,clamp | resolve clamp |
| (—) | constraint | — | — | inequality | 盖裹配合：`lid_skirt_inner_R ≥ body_R + clearance`（lift/press）且 `cap_bore_R ≥ NECK_R + clearance`（screw）且 `lid_outer ≤ body_outer + proud`；违反按比例回缩 lid_height/neck/body scale | 接口 / clearance |
| (—) | constraint | — | — | conditional | hinge_lid 的 open limit 上限随 body_shape（圆/方/六棱足够上翻 ~2.5-2.8 rad；扁矩浅腔限 ~2.0 rad 防铰侧穿身）；screw neck 半径上限随 body_radius（neck 必须 < body 截面内接半径）| 接口 / resolve |

palette_style：**10 个 coordinated colorway**，每个 = body + lid/cap + accent/label/gasket 三组件配色 + 显式 **material finish** 维度（`finish` 列：brushed_metal / glossy_print / matte_paint / anodized / brass_bronze_accent / dark_bronze / clear_pet / hammered，渲染语义 hint，不改拓扑也不计 slot_choice）。前 6 个取自 5★ 源 RGBA（保留原 realistic 配色），后 4 个为金属罐合理推断配色（贴近 beverage/food/tin 真实成品）。per-seed `rng.choice(PALETTE_STYLES)`。

| colorway | finish（材质质感维度）| body rgba | lid/cap rgba | accent / label / gasket rgba | 锚 / 来源 |
|---|---|---|---|---|---|
| `brushed_steel`（基线）| brushed_metal（拉丝钢/铝，半哑光金属高光）| brushed (0.80,0.81,0.83,1) | brushed (0.80,0.81,0.83,1) | 同体（无对比 accent）| fb4296aa L82 |
| `brushed_pewter` | brushed_metal（白镴拉丝，盖微深）| body (0.74,0.75,0.77,1) | lid (0.70,0.71,0.73,1) | seam 微差 (0.70,0.71,0.73,1) | c6ba1d09 L104-L105 / f4f34d34 L107 |
| `brass_lid_accent` | brass_bronze_accent（拉丝身 + 黄铜盖/铰，暖金属）| brushed (0.62,0.64,0.67,1) | brass (0.72,0.60,0.30,1) | dark_brass ring/铰 (0.55,0.48,0.30,1) | flatrect_hingelid L154 / round_screwcap L145 |
| `dark_bronze_cap` | dark_bronze（深古铜盖 + 黑橡胶 gasket）| brushed (0.74,0.76,0.79,1) | cap dark_bronze (0.42,0.33,0.24,1) | gasket (0.12,0.12,0.12,1) | hex_screwcap L188-L190 |
| `clear_pet_tint` | clear_pet（透明 PET tint，半透）| clear (0.80,0.86,0.88,0.25) | clear (0.78,0.85,0.88,0.25) | label_white 微贴 (0.93,0.93,0.90,1) | deli tub L99 / clear food box L96（仅 round_tapered_tub / rounded_square 口味）|
| `painted_tin` | matte_paint（哑光彩漆 tin + 印刷标）| painted (0.82,0.16,0.14,1) | painted (0.82,0.16,0.14,1) | label_white (0.93,0.93,0.90,1) + marker_red (0.82,0.16,0.14,1) | fuel-flask L138-L139 |
| `glossy_print` | glossy_print（高光印刷图案 beverage/food 品牌罐）| glossy_blue (0.10,0.42,0.78,1) | glossy_silver (0.86,0.87,0.89,1) | label_white (0.95,0.95,0.93,1) + brand_red (0.86,0.14,0.16,1) | 推断（高光印刷饮料罐，体近 painted L138 但 specular 高）|
| `anodized_gold` | anodized（阳极氧化金，染色金属反光）| anod_gold (0.83,0.69,0.32,1) | anod_gold (0.83,0.69,0.32,1) | dark_brass seam (0.55,0.48,0.30,1) | 推断（阳极金，偏 brass L145 调暖染色）|
| `anodized_blue` | anodized（阳极氧化蓝铝，染色金属反光）| anod_blue (0.18,0.34,0.55,1) | anod_blue (0.18,0.34,0.55,1) | brushed rim (0.74,0.76,0.79,1) | 推断（阳极蓝铝，体偏冷 + 拉丝口沿 f4f34d34 L107）|
| `hammered_tin` | hammered（锤纹/纹理镀锡，哑暖灰金属）| hammered (0.66,0.63,0.58,1) | hammered (0.66,0.63,0.58,1) | dark_metal 纹路 (0.40,0.42,0.45,1) | 推断（锤纹镀锡，体近 fuel-flask dark_metal L137 提亮 + 纹理）|

> finish 维度说明：`finish` 不是 slot/candidate，仅作 colorway 自带的渲染质感标签（每 colorway 一个），与 body/lid/accent rgba 同属 palette_style 数据；模板按 colorway 选 material 名 + rgba + finish hint，不影响 body_shape / closure / joint / dimension / topology。

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`neck_radius_scale` 为 equation（cap bore / cap_skirt 半径跟随 neck 半径，保螺盖套 neck 配合不破）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 body_shape / closure 的拓扑。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（body_shape + closure）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。单罐单盖。
- 样本里的 `for i in range(THREAD_COUNT)`（螺纹圈）/ `for i in range(n_ridges)`（滚花）/ `for i in range(N_GRIP_RIBS)`（防滑筋）/ 交错 hinge knuckle 循环全是 module 内部装饰/连接细节，固定密度，**非小类级 multiplicity 轴**——不暴露为模板参数（若需可作 module-local 固定常量，不进 slot_choices）。

## 拓扑多样性审计

总组合数：body_shape(5) × closure(4) = **20**（无 multiplicity，N=1）。

理由：body_shape(5) × closure(4) 笛卡尔积即 20 distinct，>10。closure 引入 PRISMATIC（lift_off / press_fit）/ CONTINUOUS+PRISMATIC（screw 2 joint + massless carrier）/ REVOLUTE +X（hinge）三种 joint 拓扑 + 不同 part count（lid=1 / cap+carrier=2），是真实结构差异；body_shape 在圆筒 / 锥圆 tub / 方 / 六棱 / 扁矩之间改 root mesh primitive（extrude-circle / loft / box+shell / polygon(6) / box+fillet）+ 截面足迹，也是真实结构差异。slot_choices 编入两轴。8 个 fork 变体已实地验证 screw / hinge 在每种 body 上的口部硬件可落，20 格基本全合法（少量 conditional 适配见下）。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 两个 named slot（笛卡尔积近全合法，少量 conditional 见下），再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除/适配组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：见 §参数表的 5 个 scale（body_height / body_radius / neck_radius / lid_height / joint_travel）。全部 `resolve_config` clamp + 每 build 统一应用。`neck_radius_scale` 为 equation（cap bore / cap_skirt 半径派生跟随，仅 screw_cap 时生效）。盖裹配合不等式 + hinge/neck conditional 在 resolve 内投影 / 回缩 / 按 body_shape 解析，不留到 builder。这些 scale 不破坏 closure joint origin（rim seam / neck top / 后 rim hinge）、盖裹/套配合、坐地或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 两 named slot（近全正交），再 uniform 各 scale + `rng.choice` palette_style | slot_choices_for_seed 含两轴且与 build 一致 |
| compatibility matrix | (1) screw_cap 在任意 body_shape 上：圆 neck 坐平顶/收肩面中心合法（方/六棱身顶面立圆颈已由变体验证）→ neck 半径在 resolve 按 body 内接半径 clamp（neck < body 截面）。(2) hinge_lid 后铰轴锚在真实后口沿（圆 `-BODY_R`、方/六棱后 flat 边、扁矩后长边）；open limit 按 body_shape conditional（扁矩浅腔限 ~2.0 防铰侧穿身）。(3) lift_off vs press_fit：press_fit skirt 内缩裹 rabbet rim，圆截面身可用裸口沿 lift_off、方截面身可用 rabbet press_fit，二者跨 body 仍合法（skirt 几何按 body 截面在 resolve 派生），不硬 gate。(4) round_tapered_tub 的卷边 rim flange 与 lid skirt 配合按 mouth 半径派生。(5) 各 closure 互斥；cap_carrier 仅 screw 发射。无硬 gate-out（20 组合全合法，只在 resolve 派生尺寸/limit 适配）| 无 floating / collision / 盖穿罐 / joint 轴或 origin 错位 / 扁矩 hinge 铰侧穿身 |
| controlled local variation | 5 个 clamped scale，每 build 统一；neck_radius equation 驱动 cap bore；hinge limit / neck 半径 conditional 随 body_shape | 比例变化不破坏 closure joint origin / 盖裹套配合 / 坐地 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | 盖动作 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_shape | 5 | yes | yes | 圆筒 / 锥圆 tub / 方 / 六棱 / 扁矩五族 |
| closure | 4 | yes | yes | lift_off(PRIS) / press_fit(PRIS,内缩 rabbet) / screw(CONT+PRIS+carrier) / hinge(REV X) |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_shape, closure) 两轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（`random.Random(seed)`）
- `resolve_config` 各 scale clamp 到声明范围；neck_radius equation 驱动 cap bore（仅 screw）；盖裹/套配合不等式在 resolve 内投影 / 回缩；hinge open limit / neck 半径 conditional 按 body_shape 解析
- compatibility matrix / gating：20 组合全合法（无硬 gate-out），screw neck 半径按 body 内接半径 clamp、hinge 后铰锚真实后口沿 + 扁矩 limit conditional
- 连续 scale clamp 后不破坏 closure joint origin / 盖裹套配合 / 坐地 / 类别身份
- 关键 joint：lift_off/press_fit `body_to_lid`/`tin_to_lid` PRISMATIC +Z (abs(axis[2])>0.99)；screw `cap_rotate`/`carrier_to_cap` CONTINUOUS +Z + `cap_slide`/`body_to_carrier` PRISMATIC +Z + massless `cap_carrier`；hinge `body_to_lid`/`lid_hinge` REVOLUTE +X (abs(axis[0])>0.99) origin 在后 rim
- captured-fit：element-scoped `allow_overlap`（盖 skirt ↔ body shell 裹 rim；cap shell ↔ body neck 套；hinge knuckle/barrel ↔ body ear）
- grandfather：盖裹/套/铰 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守
- palette_style 是 palette（10 colorway，每个自带 material-finish 维度），per-seed `rng.choice`，不计入 slot_choice

## Reject cases

- 用 boxy 占位体（纯 Box）当圆罐 body → 失类别身份；圆 body 必须 extrude(circle)/loft，方 body 用 box+fillet("|Z")+shell，六棱用 polygon(6)，扁矩用 box+双向 fillet。
- closure joint origin 放在罐底 / 任意点而非 rim seam top / neck top / 后 rim hinge 真实硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- screw 盖不用 massless carrier 解耦 rotate/slide，直接把 CONTINUOUS+PRISMATIC 串到 cap 单 part → 旋转与抬升耦合错误（应 body→carrier→cap 两 joint；两种顺序均可，但必须经 carrier）。
- closure rest pose 设成张开 / 抬起而非 q=0 闭合 → current-pose 与 viewer 目检不符。
- 给盖裹/套/铰 captured-fit 补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice；round_cylinder vs round_tapered_tub 是 loft 锥壁 + 卷边的真实结构差异才列独立 candidate）。
- 把 plastic squeeze 罐身 / 喷头喷罐 / 阀门气瓶塞回 body_shape/closure → 出 can 语义（分别归 container_plastic_can / container_paint_spray / container_gas_cylinder）。
- 扁矩 hinge_lid open limit 过大 → 铰侧盖穿罐身 / origin 漂移；neck 半径超 body 内接半径 → neck 穿壁。盖裹配合不等式或 conditional limit FAIL。

## 与相邻类别的边界

- 不该混入：**container_plastic_can（塑料罐 / squeeze 容器）**——理由：本类是金属/罐头/茶叶/食品罐，body 用金属 shell（extrude/box+shell），封口是 lid/cap/铰盖机构；塑料 squeeze 罐是软挤压瓶身、不同材质身份与封口语义。
- 不该混入：**container_paint_spray（喷罐 / 气雾罐）**——理由：本类封口只有盖/帽/后铰盖，无按压喷头 / 喷嘴 / actuator / 喷雾 nozzle 机构；喷罐的主活动件是喷头按压。
- 不该混入：**container_gas_cylinder（高压气瓶）**——理由：本类是常压日用罐，无阀门颈 / 调压器 / 高压瓶肩 / handwheel；气瓶的封口是阀门而非盖/帽。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待审核。5 body_shape × 4 closure = 20 combos（无 multiplicity），body×closure=20 直接过 。closure 含 lift_off/press_fit(PRIS) / screw(CONT+PRIS+massless carrier，两种解耦顺序合法) / hinge(REV +X)。palette_style 10 colorway（前 6 取自 5★ 源 RGBA，后 4 为金属罐合理推断），每 colorway 自带显式 material-finish 维度（brushed_metal / glossy_print / matte_paint / anodized / brass_bronze / dark_bronze / clear_pet / hammered），palette-only 不计 slot_choice。8 个 fork 变体实地填满 body×closure 网格空格。开放问题：(1) press_fit_skirt_lid 与 lift_off_lid 同为 PRISMATIC，若 reviewer 认为 skirt 几何差异不足以构成独立 candidate，可降为 lift_off 的 module-local skirt variant（则 closure 降 3 candidate，body×closure=15 仍过门控）。(2) round_tapered_tub（deli 锥壁卷边）默认偏 clear_pet_tint palette，是否保留金属罐口味由 reviewer 定。 |

## 模板实现备注（可选）

- 共享 helper：`_revolve_or_extrude_body(profile, segments)`（圆筒/锥 tub/六棱 body：extrude-circle / loft / polygon(6)）+ `_box_shell_body`（方/扁矩 body：box+fillet("|Z")[+("|X or |Y")]+shell+cut）+ `_open_mouth(rim_z)` + `_threaded_neck(neck_r, rim_z)`（screw 口部）+ `_hinge_hardware(back_edge, rim_z)`（hinge ear/knuckle/barrel）全 module 公用。
- screw：必须经 massless `cap_carrier`（无 visual 或带 tamper-ring/gasket 固定 visual，1e-4 mass Box inertial）解耦 rotate(CONTINUOUS)↔slide(PRISMATIC)；两种顺序皆可（fuel-flask=CONT→PRIS；变体=PRIS→CONT），实现选其一并在 run_tests 断言 joint type+axis。
- captured-fit overlap：`run_container_can_tests` 里 element-scoped `ctx.allow_overlap`：lid skirt ↔ body shell（裹 rim）、cap shell ↔ body neck（套 neck thread）、hinge knuckle/barrel ↔ body ear（捕获）；thread ridge ↔ neck、neck flange ↔ body top plate（同 body 内）同理（见 hex_screwcap run_tests L362-L385）。
- neck_radius equation：`resolve_config` 派生 `cap_bore_R = NECK_R + clearance`、`cap_skirt_R = NECK_R + proud`，盖套配合不等式在 resolve 投影；neck 半径按 body 内接半径 clamp（conditional）。
- hinge open limit conditional：圆/方/六棱 ~2.5-2.8 rad，扁矩 ~2.0 rad（resolve 按 body_shape 解析）。
- 参考模板：`agent/templates/Container_Jar.py`（同 Container 大类、parallel_children body+closure、screw 旋升 massless carrier + hinge REVOLUTE + lift PRISMATIC 的 Config/ResolvedConfig + `config_from_seed` + `resolve_config` clamp + `slot_choices_for_config` + `run_<stem>_tests` 的 element-scoped grandfather allow_overlap 骨架——本模板与之最近，直接复用其封口机构分支与 captured-fit overlap 习惯）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B | round_cylinder + lift_off_lid | rec_..._fb4296aa | `_body_solid` L41-L53 / `_lid_solid` L56-L76 / `body_to_lid` PRISMATIC L113-L121 | 圆筒 body 基线 + 友配抬升盖基线 |
| S2 | A | round_tapered_tub | rec_..._6b6cb24d | `_tub_solid` L38-L66（loft 锥壁 + 卷边 rim flange）| 圆锥壁敞口 tub body（deli 口味）|
| S3 | A/B | rounded_square + press_fit_skirt_lid | rec_..._c6ba1d09 | `_rounded_square_prism` L42-L50 / `_body_solid` L53-L78 / `_lid_solid` L81-L98 / `tin_to_lid` PRISMATIC L134-L142 | 圆角方截面 body + rabbet press-fit 套盖 |
| S4 | A | rounded_square (clear food box 口味) | rec_..._926ea5c0 | `_tub_solid` L50-L58（box+`shell(-WALL)`）/ clear material L96 | 方截面 shell-out 食盒（palette clear_pet_tint 口味，折入 rounded_square）|
| S5 | A | hex_prism | rec_..._f4f34d34 | `_hex_body` L56-L71 / `_hex_lid` L74-L101 | 正六棱柱 body + 六棱 lift-off 盖 |
| S6 | A/B | flat_rect_flask + screw_cap | rec_..._6e35123f | `_flask_body` L62-L93 / `_neck_solid` L96-L106 / `_cap_mesh` L109-L130 / massless `cap_carrier` L168-L169 / `cap_rotate` CONT L184-L192 / `cap_slide` PRIS L193-L201 | 扁矩 body + 螺纹颈 + 旋升螺盖（CONT→PRIS massless carrier 基线）|
| S7 | B | screw_cap (PRIS→CONT 顺序 + KnobGeometry) | rec_..._round_screwcap | `_body_solid`(neck) L88-L102 / `_cap_knob` L129-L138 / `_ring_solid` L119-L126 / `body_to_carrier` PRIS L186-L194 / `carrier_to_cap` CONT L198-L206 | 圆筒 screw 变体：KnobGeometry knurl cap + tamper ring carrier，PRIS→CONT 顺序 |
| S8 | B | screw_cap (square neck 中心立颈) | rec_..._square_screwcap | `_neck_solid` L125-L143 / `_build_screw_cap` L146-L166 / `body_to_carrier` PRIS L216-L226 / `carrier_to_cap` CONT L231-L239 | 方身顶中心圆螺纹颈 + 旋盖（massless carrier 无 visual）|
| S9 | B | screw_cap (hex neck + gasket carrier) | rec_..._hex_screwcap | `_neck_tube` L105-L124 / `_screw_cap_body` L147-L178 / `_carrier_gasket` L137-L144 / `body_to_carrier` PRIS L258-L271 / `carrier_to_cap` CONT L274-L282 | 六棱身圆螺纹颈 + 旋盖 + carrier gasket 密封 |
| S10 | B | hinge_lid (round, ear+knuckle) | rec_..._round_hingelid | body hinge ear L64-L74 / `_lid_cap` L78-L102 / `_lid_knuckle` L105-L114 / `body_to_lid` REVOLUTE +X L155-L163 | 圆筒后铰翻盖：hinge ear + knuckle 捕获，绕 +X 掀开 |
| S11 | B | hinge_lid (square, 交错 knuckle) | rec_..._square_hingelid | `_knuckle_cylinder` L67-L75 / 交错 knuckle L90-L95/L127-L132 / `body_to_lid` REVOLUTE L170-L181 | 方身后铰翻盖：5 段交错 hinge knuckle |
| S12 | B | hinge_lid (hex, barrel + back_cut) | rec_..._hex_hingelid | `_body_with_hinge`(barrel) L84-L90 / `_hex_flip_lid` L94-L140 / `body_to_lid` REVOLUTE L178-L191 | 六棱身后铰翻盖：hinge barrel + 去铰侧裙 back_cut |
| S13 | B | hinge_lid (flat_rect, rim+barrel+tab) | rec_..._flatrect_hingelid | `_top_rim` L104-L118 / `_hinge_barrel` L121-L130 / `_lid_plate` L133-L141 / lid_knuckle/lid_tab L192-L205 / `lid_hinge` REVOLUTE L216-L226 | 扁矩身后铰翻盖：raised rim + hinge barrel + 前 grip tab |
| S14 | A/B | flat_rect_flask + lift_off_lid (raised rim press) | rec_..._flatrect_liftofflid | `_body_with_rim` L71-L109 / `_lid_solid` L112-L145 / `lid_lift` PRISMATIC L207-L217 | 扁矩身 raised rim + 全宽周裙 press 抬升盖 + grip ribs（验证 lift_off 在扁矩身上）|
