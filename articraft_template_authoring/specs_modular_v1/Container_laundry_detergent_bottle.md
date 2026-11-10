# Container / laundry detergent bottle (molded HDPE jug + integrated handle + screw measuring-cup cap) — Modular Spec

> 来源小类：`picture/Container/laundry detergent bottle`（articraft_data 上游 Container/laundry-detergent fork-variant pool）。
> 引用 `model.py:Lx-Ly` 来自各样本 `arti-template` 当前 `data/records/<id>/revisions/rev_000001/model.py`；以 part / joint / helper **名字** 为准（`_body_shell` / `_handle_solid` / `_top_carry_handle` / `_grip_recess` / `_spout_mesh` / `_cap_mesh` / `_lid_mesh` / `_neck_collar` / `_pump_housing_mesh` / `_actuator_head_mesh` / `cap_carrier` / `cap_rotate` / `cap_slide` / `body_to_lid` / `collar_screw` / `pump_press` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_laundry_detergent_bottle` |
| template path | `agent/templates/Container_laundry_detergent_bottle.py` |
| test path (optional) | `tests/agent/test_container_laundry_detergent_bottle_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots: body_shape + handle_grip + closure；handle 融入 body root visual，closure 各候选挂到共同 parent `body`，无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 parent + 7 fork 变体）|
| read_count | 8（全文读取，无抽样）|
| read_scope | all 5-star samples in this category（parent + 全部 `rec_container_laundry_detergent_bottle_var_*`）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14 |

读取清单与采纳分流：

- **parent** `rec_orange-tide-liquid-laundry-detergent-bottle-with_..._8f73f587`（351 行）：扁椭圆 jug `_body_shell` loft + 内缩肩 + 螺纹 neck + bored mouth；`_handle_solid` +X 侧环形提手（slab + 椭圆穿透抠手孔）；FIXED `pour_spout`；`_cap_mesh` 半透明蓝量杯盖经 massless `cap_carrier` 解耦 `cap_rotate`(CONTINUOUS +Z) + `cap_slide`(PRISMATIC +Z)。采纳为 body 基线 + side_loop_handle 基线 + measuring_cup_cap 基线。Tide bullseye / label_band / he_badge 内联为 body.visual（装饰，非 part）。
- **cyl_body** `..._var_cyl_body`（370 行）：`_body_shell` 改圆截面（circle-section）loft，高身圆柱罐，同 handle / cap / 双关节。采纳为 round_cylinder body candidate。
- **square_body** `..._var_square_body`（415 行）：`_main_body_box`（rect+extrude+fillet）+ `_shoulder_neck`（方肩台阶 step → 圆 neck），broad face 平、近竖侧壁。采纳为 square_shoulder body candidate（注意 body 发两段 visual `main_body` + `shoulder_neck`）。
- **waist_body** `..._var_waist_body`（367 行）：`_body_shell` 改中段收腰 loft（waist pinch z~0.075–0.115），人体工学握位。采纳为 waisted_contour body candidate。
- **grip_indent** `..._var_grip_indent`（364 行）：去掉 `_handle_solid`，改 `_grip_recess`（sphere 减去 → 凹形手指 scoop，壁连续无穿孔），`shell = _body_shell().cut(_grip_recess())`。采纳为 recessed_grip handle candidate。
- **top_handle** `..._var_top_handle`（389 行）：`_top_carry_handle`（XZ 平面 path sweep 倒 U 拱形顶提梁，HANDLE_PEAK_Z=0.290 高过罐顶），`shell = _body_shell().union(_top_carry_handle())`。采纳为 top_carry_handle handle candidate。
- **flip_cap** `..._var_flip_cap`（401 行）：body 加 `_neck_collar` 领圈；`_lid_mesh` 翻盖（disc + skirt + living-hinge tab + grip nub）作独立 `lid` part；`body_to_lid` REVOLUTE axis=(1,0,0) origin=后 collar 边，q∈[0,2.2] 上翻。采纳为 flip_top_cap closure candidate。
- **pump_cap** `..._var_pump_cap`（523 行）：`pump_base` part（`_pump_housing_mesh` 螺纹领+泵缸 + `dip_tube` 下伸入瓶 + `for i in range(GRIP_COUNT)` 领圈 grip ridge 装饰环）+ `pump_actuator` part（`_actuator_head_mesh` + nozzle + stem）；`collar_screw` CONTINUOUS +Z（body→pump_base）+ `pump_press` PRISMATIC -Z（pump_base→pump_actuator）。采纳为 pump_dispenser closure candidate。

冗余/分流说明：cyl / square / waist 三个 body 变体只换 `_body_shell` 截面族（圆 / 方 / 收腰），handle/cap/双关节保持 parent，归并入 body_shape slot；grip_indent / top_handle 只换提手机构、保持 measuring_cup_cap，归并入 handle_grip slot；flip_cap / pump_cap 只换封口机构，归并入 closure slot。三轴彼此正交，构成笛卡尔积拓扑多样性（见 §9）。装饰性 label/badge/grip_ridge 不另列 candidate。

## 核心身份

洗衣液瓶 / 壶（laundry detergent bottle / jug）：一只直立的吹塑 / 注塑 HDPE 中空壳体，瓶轴沿 +Z，底坐地 z=0，居中于 (x=0,y=0)，总高 ~0.26 m、广面朝 ±Y。三大功能层：

1. **body_shape**（root `body` 的 mesh + 内缩肩 + 螺纹 neck + 沿瓶轴 bored pour mouth）：扁椭圆 jug / 高圆柱 / 方肩矩形 / 中段收腰 contour。CadQuery `loft`（圆 / 扁椭圆 / 收腰 rounded-rect 截面族）或 `box+fillet+shell`（方身）发射，开口腔体真实（mouth 贯通至 neck top）。
2. **handle_grip**（融入 body root visual 的提手 / 握持机构）：+X 侧整体环形提手（slab + 椭圆穿透抠手孔，封闭成环可勾手）/ 广面凹形手指 scoop（sphere cut，壁连续无穿孔）/ 跨肩倒 U 拱形顶提梁（path sweep 管，HANDLE_PEAK 高过罐顶）。提手是 body 的 mesh 操作（`union` 提梁 / `cut` 凹位），不是独立活动 part。
3. **closure**（**主活动语义**——封口 / 分配机构）：螺纹旋升量杯盖（经 massless `cap_carrier` 解耦 `cap_rotate` CONTINUOUS +Z + `cap_slide` PRISMATIC +Z，盖即量杯，半透明蓝）/ 后铰 snap 翻盖（`body_to_lid` REVOLUTE +X 绕后 collar 上翻）/ 螺纹领泵头分配器（`collar_screw` CONTINUOUS +Z + `pump_press` PRISMATIC -Z，带 dip tube 下伸入瓶）。

固定装饰内联为 body.visual：Tide bullseye 圆标 / label_band / he_badge / pour_spout（FIXED）/ collar grip ridges。默认成熟域：单瓶单盖（无嵌套 / 无 multiplicity）。

不该混入（相邻类别边界，见 §11）：通用塑料罐 `container_plastic_can`（短粗罐 + 提环盖，无整体侧提手 + 无量杯盖 spine）、皂液 / 乳液分配器 `container_dispenser`（细颈瓶 + 长泵管按压头，无大容积壶身 + 无侧环提手）、化妆 / 洗手液压泵瓶 `container_pump`（小容量泵瓶，泵是主体而非洗衣液壶的可替换封口）。

## 槽位 + 候选模块表

> **建模注记**：`body_shape` 是 root `body` 的 mesh 属性（一次 `_body_shell(body_shape)` 发射 shell + neck + thread + bored mouth；方身走 `_main_body_box`+`_shoulder_neck` 两段 visual），不是独立串联 slot。`handle_grip` 在 body mesh 阶段 `union`（提梁）/ `cut`（凹位）或 `union`（侧环 slab），仍是 body 的 visual，不是独立 part。`closure` 各候选挂到 root `body`（parallel children，含 1–2 活动 part）。三轴笛卡尔积构成拓扑多样性（见 §9）。

### Slot A：body_shape（瓶身轮廓 / 截面形状族——root `body` 的 mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_oval_jug（基线）| rec_orange-tide-...-8f73f587 | `_body_shell` L47-95（rounded-rect 截面 loft + 内缩肩 + neck + bored mouth）| eligible if compatible | 扁椭圆 jug：rounded-rect 截面竖向 `loft(ruled=False)`，广面朝 ±Y，half_x≫half_y，内缩肩 → 螺纹 neck，沿轴 bored pour mouth |
| round_cylinder | rec_...-var_cyl_body | `_body_shell` L52-93（circle 截面 loft，BODY_R=0.055）| eligible if compatible | 高身圆柱罐：圆截面 loft，X/Y 等径，圆肩收颈，同容积竖向更高，bored mouth |
| square_shoulder | rec_...-var_square_body | `_main_body_box` L64-80 + `_shoulder_neck` L83-109（rect extrude + fillet "|Z" + 方肩 step + 圆 neck）| eligible if compatible | 方截面矩形棱柱身（BODY_W=0.15×BODY_D=0.09）+ 平广面 + 近竖侧壁 + 方肩台阶 step（SHOULDER_W<BODY_W）收颈；body 发两段 visual `main_body`+`shoulder_neck` |
| waisted_contour | rec_...-var_waist_body | `_body_shell` L52-103（11 段 rounded-rect loft，含 waist pinch z~0.075–0.115）| eligible if compatible | 中段收腰 contour：底/肩宽、中段窄（waist 最窄 half_x=0.052），人体工学握位 loft，bored mouth |

硬约束记录：body_shape 4 candidate（达 3-6 目标内）。全部中空开口腔（bored pour mouth 贯通至 neck top），共享 neck（NECK_R=0.0235, NECK_TOP_Z=0.214）+ pour_spout helper，只换 footprint / 高宽比 / 收腰 / 方圆截面族。

### Slot B：handle_grip（提手 / 握持机构——body root 的 mesh union/cut）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| side_loop_handle（基线）| rec_orange-tide-...-8f73f587 | `_handle_solid` L98-122（XZ slab + `edges("|Y").fillet` + 椭圆 `cut`）；`shell = _body_shell().union(_handle_solid())` L176 | eligible if compatible | +X 侧整体环形提手：板坯 slab（x 0.054..0.094, z 0.060..0.160）融入上身 + 椭圆穿透抠手孔，外握杆封闭成闭环可勾手，`union` 入 body |
| recessed_grip | rec_...-var_grip_indent | `_grip_recess` L99-115（sphere 减去，scoop_r=0.042, depth=0.016）；`shell = _body_shell().cut(_grip_recess())` L169 | eligible if compatible | 广面 +X 侧压出凹形手指 scoop：球面 `cut` 出连续凹位，壁不穿孔，模制抠手凹（无外握杆环）|
| top_carry_handle | rec_...-var_top_handle | `_top_carry_handle` L112-142（XZ path sweep 倒 U 管，HANDLE_PEAK_Z=0.290）；`shell = _body_shell().union(_top_carry_handle())` L194 | eligible if compatible | 跨肩倒 U 拱形顶提梁：圆截面管沿 line+threePointArc path `sweep`，双脚 embed 入肩（HANDLE_FOOT_Z=0.178），拱峰 0.290 高过罐顶从顶部提携 |

硬约束记录：handle_grip 3 candidate（达下限 3）。三者结构差异真实：环形穿透提手（union slab + 椭圆孔）vs 连续凹位（球面 cut，无外握杆）vs 顶提梁（sweep 管 union，改罐顶包络与最高几何）。全部为 body mesh 操作，无独立活动 part / joint。

### Slot C：closure（**主开合 / 分配机构槽**——挂 root `body` 的活动件）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| measuring_cup_cap（基线）| rec_orange-tide-...-8f73f587 | `_cap_mesh` L135-160 + `cap_carrier`(massless) L209-210 + `cap_rotate` CONTINUOUS L228-236 + `cap_slide` PRISMATIC L238-246 | eligible if compatible | 半透明蓝量杯盖：经 massless `cap_carrier` 解耦 `cap_rotate`(CONTINUOUS +Z @ CAP_SEAT_Z)（旋拧）+ `cap_slide`(PRISMATIC +Z, q∈[0,CAP_HEIGHT])（直拔离 neck）；2 joint + 1 massless carrier + off-axis `cap_marker` 观测旋转 |
| flip_top_cap | rec_...-var_flip_cap | `_neck_collar` L131-146 + `_lid_mesh` L159-214（disc+skirt+living-hinge tab+nub）+ `lid` part L273 + `body_to_lid` REVOLUTE axis=(1,0,0) L285-294 | eligible if compatible | 后铰 snap 翻盖：body 加 `_neck_collar` 领圈，独立 `lid` part 绕后 collar 边 `body_to_lid` REVOLUTE +X（HINGE_ORIGIN=(0,-COLLAR_R,COLLAR_TOP_Z)，q∈[0,2.2] 上翻 ~126°），q=0 disc 盖住 mouth |
| pump_dispenser | rec_...-var_pump_cap | `_pump_housing_mesh` L159 + `pump_base` part L273 + `dip_tube` visual L297-302 + `_actuator_head_mesh` + `pump_actuator` part L319 + `collar_screw` CONTINUOUS L352-360 + `pump_press` PRISMATIC L365-373 | eligible if compatible | 螺纹领泵头分配器：`pump_base`（螺纹领+泵缸+dip tube 下伸入瓶）经 `collar_screw`(CONTINUOUS +Z @ COLLAR_SEAT_Z) 挂 body；`pump_actuator`（head+nozzle+stem）经 `pump_press`(PRISMATIC axis=(0,0,-1), q∈[0,STROKE]) 按压下行；2 joint + 2 part + dip_tube |

硬约束记录：closure 3 candidate（达下限 3）。含 CONTINUOUS+PRISMATIC（screw cap 经 massless carrier 解耦）/ REVOLUTE +X（flip 后铰）/ CONTINUOUS+PRISMATIC（pump 螺旋领 + 压头）三种 joint 拓扑 + 不同 part count（cap=carrier+cap 2 part / flip=lid 1 part / pump=base+actuator 2 part）。每个 candidate **≥1 non-fixed joint**（满足活动机构）。样本池仅这三族封口；主多样性由 body_shape × handle_grip × closure 提供（见 §9）。

## 槽位图（slot graph）

pattern: parallel_children（root `body` 承载 body_shape mesh + handle_grip mesh；closure 活动件挂到 body；无 multiplicity）

```
body(body_shape mesh ⊕ handle_grip mesh ⊕ FIXED pour_spout ⊕ 装饰 label/badge)  [ROOT, 坐地 z=0]
   │  handle_grip 是 body mesh 操作（union 侧环/提梁 或 cut 凹位），非独立 part/joint
   │  downstream interface = neck rim top / collar top 中心 (0,0,~CAP_SEAT_Z|COLLAR_SEAT_Z)
   │
   ├── closure = measuring_cup_cap:
   │     body --[cap_rotate: CONTINUOUS +Z @ (0,0,CAP_SEAT_Z)]--> cap_carrier(massless,无 visual)
   │              cap_carrier --[cap_slide: PRISMATIC +Z]--> cap(蓝量杯 + cap_marker)
   │
   ├── closure = flip_top_cap:
   │     body(+_neck_collar) --[body_to_lid: REVOLUTE +X @ (0,-COLLAR_R,COLLAR_TOP_Z)]--> lid(flip disc+skirt+hinge tab)
   │
   └── closure = pump_dispenser:
         body --[collar_screw: CONTINUOUS +Z @ (0,0,COLLAR_SEAT_Z)]--> pump_base(housing+dip_tube+grip ridges)
              pump_base --[pump_press: PRISMATIC -Z @ (0,0,PUMP_TOP_LOCAL)]--> pump_actuator(head+nozzle+stem)
```

接口点位与 joint 语义：
- **screw-cap 接口**：`cap_rotate` origin 落在 neck top 中心 `(0,0,CAP_SEAT_Z≈0.196)`，axis +Z（CONTINUOUS）；`cap_slide` 经 massless `cap_carrier`（无 visual，1e-4 mass Box inertial），axis +Z（PRISMATIC，q=0 坐下、正 q 抬离 q∈[0,CAP_HEIGHT]）。carrier 解耦旋转 / 平移共享 +Z（parent 来源 L228-246）。
- **flip 接口**：`body_to_lid` origin 在后 collar 边硬件 `(0, -COLLAR_R, COLLAR_TOP_Z)`，axis +X，REVOLUTE 闭合 q=0（disc 盖 mouth）、上翻正 q∈[0,2.2]。body 须为此候选加 `_neck_collar` 领圈作 hinge 座（flip_cap L229）。
- **pump 接口**：`collar_screw` origin 在 collar seat `(0,0,COLLAR_SEAT_Z)`，axis +Z CONTINUOUS（旋拧上瓶）；`pump_press` origin 在泵缸顶面 `(0,0,PUMP_TOP_LOCAL)`，axis (0,0,-1) PRISMATIC（正 q 按压头下行 q∈[0,STROKE]）；`dip_tube` 为 pump_base 的 visual，沿轴下伸穿 neck 入瓶内（element-scoped allow_overlap dip_tube↔jug_shell）。
- **handle 接口**：side_loop_handle / top_carry_handle 为 body mesh `union`（slab / sweep 管融入上身），recessed_grip 为 body mesh `cut`（球面凹位）；均无独立 joint，是 body 的 jug_shell visual 一部分。
- **mating policy**：盖 / 翻盖 / 泵头与 neck / collar 是 captured / 友配（skirt 罩 over neck rim 故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（落在真实 neck top / 后 collar / collar seat 硬件）+ element-scoped `allow_overlap`（cap_cup↔jug_shell、cap_cup↔pour_spout、lid skirt↔collar、dip_tube↔jug_shell、actuator_stem↔pump_housing）守 overlap（见各样本 run_tests 的 `ctx.allow_overlap`）。
- **rest pose**：cap q=0 坐 neck；flip lid q=0 盖 mouth；pump actuator q=0 头在顶（未按压）。盖旋升 / 翻起 / 泵按压为 viewer 目检的活动语义。
- **互斥 / 可选**：closure 各候选互斥（一次只一种封口）。`cap_carrier` massless part 仅在 measuring_cup_cap 候选发射；`_neck_collar` 仅 flip_top_cap；`dip_tube`/`pump_base`/`pump_actuator` 仅 pump_dispenser。

## 每槽位 Module Emits / Interfaces

### Slot A / body（body_shape，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（visual: `jug_shell` shell+neck+bored mouth[+handle mesh]；方身另发 `main_body`+`shoulder_neck`；+ FIXED `pour_spout` + 装饰 `bullseye_label`/`label_band`/`he_badge`）| parent `_body_shell` L47-95 / square `_main_body_box`+`_shoulder_neck` L64-109 |
| internal joints | 无（root 瓶体本身无活动件）| — |
| upstream interface | 坐地 z=0（root，居中 x=y=0）| parent BODY_BOTTOM_Z L37 |
| downstream interface | neck rim top / collar seat 中心 (0,0,~CAP_SEAT_Z\|COLLAR_SEAT_Z)（closure joint 的 parent 接口）| parent CAP_SEAT_Z L41 |

### Slot B / handle_grip（body root 的 mesh 操作，无独立 part）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（side_loop / top_carry 为 jug_shell `union`，recessed 为 jug_shell `cut`）| parent `_handle_solid` L98-122 / top `_top_carry_handle` L112-142 / grip `_grip_recess` L99-115 |
| internal joints | 无 | — |
| downstream interface | 改 body 的 +X 包络（side/top）或最高几何（top_carry HANDLE_PEAK 0.290 > 罐顶）| top L355-359 |

### Slot C / closure（每候选发射对应活动件，挂 body）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cap_carrier`(massless)+`cap`(+`cap_marker`) / `lid`(flip) / `pump_base`(+`dip_tube`+grip ridges)+`pump_actuator`(+nozzle+stem) | 各 closure 源 |
| internal joints | `cap_rotate` CONTINUOUS +Z + `cap_slide` PRISMATIC +Z（screw）/ `body_to_lid` REVOLUTE +X（flip）/ `collar_screw` CONTINUOUS +Z + `pump_press` PRISMATIC -Z（pump）| parent L228-246 / flip L285-294 / pump L352-373 |
| upstream interface | neck rim top（cap/pump screw）/ 后 collar 边（flip hinge）| parent CAP_SEAT_Z / flip HINGE_ORIGIN / pump COLLAR_SEAT_Z |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_shape | enum | flat_oval_jug / round_cylinder / square_shoulder / waisted_contour | flat_oval_jug | choice | deterministic procedural sampler 选 | module table |
| handle_grip | enum | side_loop_handle / recessed_grip / top_carry_handle | side_loop_handle | choice | sampler 选 | module table |
| closure | enum | measuring_cup_cap / flip_top_cap / pump_dispenser | measuring_cup_cap | choice | sampler 选 | module table |
| palette_style | enum | tide_orange_blue / gain_green_white / persil_white_red / arm_hammer_yellow / allfree_teal / ecover_amber / purex_purple / downy_pink_twotone / seventh_gen_matte_pearl | tide_orange_blue | palette | palette only，**不计入 slot_choice**（9 colorway + 显式 material-finish 维，per-seed `rng.choice`）| §palette |
| body_height_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放罐体高度 H → SHOULDER_Z/NECK_*/CAP_SEAT_Z 同比平移 → closure mount 高度，clamp | resolve clamp |
| body_width_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放罐体广面半宽 / 半径（half_x / BODY_R / BODY_W），clamp（neck 不跟随，保盖配合）| resolve clamp |
| neck_radius_scale | float | [0.92, 1.08] | 1.0 | equation | `NECK_R = base · neck_radius_scale`；cap_skirt / lid skirt / collar 半径派生跟随（保罩配合）| resolve clamp |
| handle_size_scale | float | [0.85, 1.15] | 1.0 | conditional | 缩放 handle 尺寸：side_loop=slab+孔、recessed=scoop_r、top_carry=tube_R+leg_span；范围依 handle_grip 选择解析（top_carry 须留 PEAK > 罐顶 clearance）| resolve clamp |
| closure_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 cap_slide / pump_press 行程 + flip hinge upper limit，clamp | resolve clamp |
| (—) | constraint | — | — | inequality | 盖罩配合：`cap_bore_R ≥ NECK_R + clearance` 且 `cap/lid/collar outer_R ≤ body_half_min + proud`；违反按比例回缩 neck/closure scale | 接口 / clearance |
| (—) | constraint | — | — | inequality | top_carry handle：`HANDLE_PEAK_Z·body_height_scale > body_top_z + tube_clearance`（提梁拱峰须高过罐顶 + closure），违反回缩 handle_size / 抬高 peak | 接口 / clearance |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`neck_radius_scale` 为 equation（cap_skirt / lid skirt / collar 半径跟随 neck 半径，保盖罩配合不破）。`handle_size_scale` 为 conditional（合法范围依所选 handle_grip）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 body_shape / handle_grip / closure 的拓扑。

### palette_style 取值（per-seed 采样，9 realistic colorway，含显式 material-finish 维）
来自 5★ 源的真实材质（parent `tide_orange` (0.95,0.46,0.07,1.0) + `cap_blue` (0.30,0.55,0.85,0.5) 半透明 + `label_yellow` (0.98,0.83,0.10,1.0) / `label_blue` (0.10,0.22,0.62,1.0) + `he_silver` (0.78,0.80,0.82,1.0)；pump `pump_white` (0.92,0.92,0.93,1.0) / `pump_dark` (0.25,0.25,0.28,1.0) + `accent_teal` (0.10,0.65,0.68,1.0)；flip `lid_blue` (0.15,0.40,0.78,1.0)；`marker_white` (0.92,0.92,0.95,1.0)）扩展为 9 个协调的洗衣液品牌色板。每个 colorway 给 **body + handle + 量杯盖/spout + label accent** 四件套颜色，外加一列显式 **finish（材质表面处理维）**。

**material-finish 维（显式取值集）**：`glossy_hdpe`（光面注塑 HDPE 品牌色，alpha=1）/ `translucent`（半透明壶身或半透明量杯盖，carries alpha<1）/ `opaque_matte`（哑光不透明，低高光）/ `pearlescent`（珠光 / 金属感漆，浅高光偏白）。finish 只是材质外观语义（spec 层记号，模板以 rgba + alpha 表达；matte/pearlescent 为 rgba 倾向，translucent 必带 alpha<1），不引入新拓扑 / slot / 几何。

> handle_grip 是 body mesh 操作（union 侧环 / 提梁、cut 凹位），与 body 同色同件，故 handle 列与 body 主色绑定（同一 `jug_shell` visual）；下表"handle / body 主色"列即 jug_shell 颜色，单独列出以满足"body + handle"四件套要求。pour_spout 始终随 body 主色（parent L180/L233 即用 `orange` 上 spout）。

| palette_style | body / handle 主色（jug_shell+spout）| 量杯盖 / closure 色 | accent / label | finish（material-finish 维）| 来源 |
|---|---|---|---|---|---|
| tide_orange_blue（基线）| 橙 HDPE (0.95,0.46,0.07,1.0) | 半透明蓝量杯 (0.30,0.55,0.85,0.5) | 黄圆标 (0.98,0.83,0.10,1.0) + 蓝带 (0.10,0.22,0.62,1.0) + 银 he (0.78,0.80,0.82,1.0) | glossy_hdpe body + translucent cap | parent L166-171 |
| gain_green_white | 草绿 HDPE (0.30,0.62,0.20,1.0) | 白盖 (0.95,0.95,0.96,1.0) | 蓝标 (0.10,0.22,0.62,1.0) | glossy_hdpe body + glossy_hdpe cap | parent 材质族衍生 |
| persil_white_red | 乳白 HDPE (0.96,0.96,0.93,1.0) | 半透明红量杯 (0.82,0.18,0.18,0.5) | 深蓝标 (0.08,0.16,0.48,1.0) | glossy_hdpe body + translucent cap | parent `cap_blue` alpha 模式衍生 |
| arm_hammer_yellow | 黄 HDPE (0.97,0.80,0.10,1.0) | 半透明白量杯 (0.92,0.92,0.95,0.5) | 红标 (0.78,0.12,0.12,1.0) | glossy_hdpe body + translucent cap | `label_yellow` 主色 + `marker_white` alpha 衍生 |
| allfree_teal | 青绿 HDPE (0.10,0.65,0.68,1.0) | 白盖 (0.92,0.92,0.93,1.0) | 紫标 (0.42,0.18,0.62,1.0) | glossy_hdpe body + glossy_hdpe cap | pump `accent_teal` L308 衍生 |
| ecover_amber | 琥珀半透明壶 (0.62,0.40,0.12,0.55) | 绿盖 (0.30,0.55,0.22,1.0) | 牛皮纸棕标 (0.55,0.42,0.28,1.0) | translucent body + opaque_matte cap | 环保品牌衍生（translucent 壶身）|
| purex_purple | 紫 HDPE (0.45,0.20,0.62,1.0) | 半透明薰衣草量杯 (0.62,0.45,0.82,0.5) | 银标 (0.78,0.80,0.82,1.0) | glossy_hdpe body + translucent cap | brand-color HDPE（紫）衍生 |
| downy_pink_twotone | 玫粉 HDPE (0.90,0.42,0.58,1.0) | 两段盖：白盖身 (0.95,0.95,0.96,1.0) + 深莓盖环 (0.62,0.10,0.30,1.0) | 白标 (0.95,0.95,0.96,1.0) | glossy_hdpe body + two-tone cap（白盖身 + 莓色盖环）| brand-color HDPE（粉）+ 双色盖衍生 |
| seventh_gen_matte_pearl | 哑光石板灰 HDPE (0.42,0.45,0.48,1.0) | 珠光银盖 (0.80,0.82,0.86,1.0) | 哑光墨绿标 (0.16,0.30,0.22,1.0) | opaque_matte body + pearlescent cap | 高端环保线（matte 壶身 + 珠光盖）衍生 |

palette_style 只改材质 rgba（含半透明 body/cap alpha<1 与 finish 记号），不改任何拓扑 / 尺寸 / slot；measuring_cup_cap 候选须保 cap alpha<1（半透明量杯身份，validator 守）——非 translucent-cap 的 colorway（gain/allfree/downy/seventh_gen）在 measuring_cup_cap 候选上仍须给量杯盖 alpha<1 子值或回退到该 colorway 的 translucent cap 变体（cap-alpha 守门优先于 finish 美学）。two-tone（downy）与 pearlescent（seventh_gen）仅是同一 cap visual 的 rgba 表达，不新增 part / joint。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（body_shape + handle_grip + closure）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。洗衣液瓶本身不含 N 个同构子件（无抽屉 / 叶片 / 链节）。
- 说明：pump_dispenser 候选内部 `for i in range(GRIP_COUNT)` 发射领圈 grip ridge（pump L278-291）是 **module-local 固定装饰环**，GRIP_COUNT 为常量、不暴露为模板参数、不改 part tree / joint topology，因此 **不构成 multiplicity 轴**（按 §2.2：只改装饰密度不是独立 slot / candidate）。

## 拓扑多样性审计

总组合数：body_shape(4) × handle_grip(3) × closure(3) = **36**。

仅 body_shape × closure = 4×3 = **12 ≥ 10** 已可过门控；叠 handle_grip 后 36 充裕。

理由：本类拓扑多样性来源充裕——36 distinct 组合远超 10。closure 引入三种 joint 拓扑：CONTINUOUS+PRISMATIC（screw cap 2 joint + massless `cap_carrier`）/ REVOLUTE +X（flip 后铰 1 joint）/ CONTINUOUS+PRISMATIC（pump 2 joint + 2 part + dip_tube），part count 与 joint 链各异，是真实结构差异。handle_grip 改 body mesh 拓扑（union 侧环穿透孔 / cut 连续凹位 / union 顶提梁 sweep 管，改最高几何包络）。body_shape 改截面族（圆 / 扁椭圆 / 方+step / 收腰）与 visual 段数（方身 2 段）。slot_choices 编入三轴。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 三个 named slot（笛卡尔积近全合法，少量 conditional 见下），再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 处理非正交组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 36（36 组合的采样空间足够覆盖）。低于 300 的原因：本小类真实结构词汇就是 4 body × 3 handle × 3 closure = 36，是该类目的合理上限（洗衣液瓶结构家族有限：少数瓶身轮廓 × 少数提手 × 少数封口），不强行注水发明结构。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 5 个 scale（body_height / body_width / neck_radius / handle_size / closure_travel）。全部 `resolve_config` clamp + 每 build 统一应用。`neck_radius_scale` 为 equation（cap_skirt / lid skirt / collar 半径派生跟随）；`handle_size_scale` 为 conditional（范围依 handle_grip）。盖罩配合不等式 + top_carry 拱峰 clearance 不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏 closure joint origin（neck top / 后 collar / collar seat）、盖罩 neck 配合、handle 包络或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 三 named slot（近全正交），再 uniform 各 scale + `rng.choice` palette_style | slot_choices_for_seed 含三轴且与 build 一致 |
| compatibility matrix | (1) `top_carry_handle` × `pump_dispenser`：顶提梁拱峰会与泵头 actuator 抢占颈顶空间（潜在干涉，源映射 §排除项已标）→ resolve 内派生：拱峰 z 抬至 max(PEAK, pump_top + clearance)，腿 span 让开 collar，**不 gate-out**（保多样性），仅尺寸适配。(2) `flip_top_cap` 需 body 加 `_neck_collar` 领圈作 hinge 座；任意 body_shape 正交可加。(3) `recessed_grip` 凹位 depth 须 < body 壁厚余量，窄身（body_width_scale 低 + round_cylinder）时 scoop_r 按 body 半径 resolve 派生回缩，避免穿透成洞。(4) 各 closure 互斥；各 handle 互斥。(5) 36 组合全合法，无硬 gate-out，仅在 resolve 派生尺寸适配。| 无 floating / collision / 盖穿罐 / 提梁撞泵头 / scoop 穿壁 / joint 轴或 origin 错位 |
| controlled local variation | 5 个 clamped scale，每 build 统一；neck_radius equation 驱动 cap/lid/collar bore；handle_size conditional 按 handle_grip | 比例变化不破坏 closure joint origin / 盖罩配合 / 提梁 clearance / 坐地 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | closure 动作 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_shape | 4 | yes | yes | flat_oval / round_cyl / square_shoulder(+step) / waisted contour |
| handle_grip | 3 | yes | yes | side_loop(union 环+孔) / recessed(cut 凹) / top_carry(union sweep 管) |
| closure | 3 | yes | yes | screw cup(CONT+PRIS+carrier) / flip(REV X) / pump(CONT+PRIS+dip 2 part) |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_shape, handle_grip, closure) 三轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（`random.Random(seed)`，seed=0 不特殊）
- `resolve_config` 各 scale clamp 到声明范围；neck_radius equation 驱动 cap/lid/collar bore；handle_size conditional 按 handle_grip；盖罩配合 + top_carry 拱峰 clearance 不等式在 resolve 内投影 / 回缩
- compatibility matrix / gating：36 组合全合法（无硬 gate-out），top_carry×pump 时拱峰 z 在 resolve 抬高让开泵头、窄身时 scoop_r 派生回缩
- 连续 scale clamp 后不破坏 closure joint origin / 盖罩配合 / 提梁 clearance / 坐地 / 类别身份
- 关键 joint：screw `cap_rotate` CONTINUOUS +Z (abs(axis[2])>0.99) + `cap_slide` PRISMATIC +Z + massless `cap_carrier`（无 visual, mass≈1e-4）；flip `body_to_lid` REVOLUTE +X (abs(axis[0])>0.99) origin 在后 collar；pump `collar_screw` CONTINUOUS +Z + `pump_press` PRISMATIC axis≈(0,0,-1) + `dip_tube` 下伸入瓶
- captured-fit：element-scoped `allow_overlap`（cap_cup↔jug_shell、cap_cup↔pour_spout、lid skirt↔neck_collar、dip_tube↔jug_shell、actuator_stem↔pump_housing）
- palette_style：9 colorway + 显式 material-finish 维（glossy_hdpe / translucent / opaque_matte / pearlescent）；translucent body/cap colorway 带 alpha<1；measuring_cup_cap 候选 cap alpha<1（半透明量杯身份，cap-alpha 守门优先于 finish 美学）；two-tone / pearlescent 仅 cap rgba 表达不新增 part；palette 只改 rgba 不改拓扑
- grandfather：盖 / 翻盖 / 泵头 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守
- handle_grip：side_loop / top_carry 改 body +X / 顶部包络且融入 jug_shell；recessed scoop 壁连续不穿透

## Reject cases

- 用纯 Box 占位体当 jug body → 失类别身份；圆 / 扁椭圆 / 收腰 body 必须 `loft`，方 body 用 `box`+`fillet("|Z")`+方肩 step。
- closure joint origin 放在罐底 / 任意点而非 neck rim top / 后 collar 边 / collar seat 真实硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- measuring_cup_cap 不用 massless `cap_carrier` 解耦 rotate/slide，直接把 CONTINUOUS+PRISMATIC 串到 cap 单 part → 旋转与抬升耦合错误（应 body→carrier→cap 两 joint）。
- 把 side_loop_handle 抠手孔做成贯穿外壁的窗（破坏外握杆环）或把 recessed_grip 球面 cut 过深穿透成洞 → 失提手 / 凹位身份，scoop_r 须按 body 半径 resolve 回缩。
- top_carry_handle 拱峰未高过罐顶 + closure（PEAK 太低 / 与泵头 actuator 干涉）→ 提梁 clearance 不等式 FAIL，resolve 须抬高拱峰让开。
- closure rest pose 设成张开 / 抬起 / 翻起 / 按下而非 q=0 闭合坐位 → current-pose 与 viewer 目检不符。
- 把连续尺寸 / 颜色 / 材质 / grip_ridge 密度当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette、grip ridges 是 module-local 装饰，均不计 slot_choice）。
- 把 GRIP_COUNT 暴露成 `*_count` 模板参数当 multiplicity 轴 → 错误（领圈 ridge 是固定装饰环，非同构子件复制）。
- 盖 / 泵头 / dip_tube captured-fit 补 MatingContract 硬对接 → 配合几何对不上 mating-gap FAIL；应 grandfather + element-scoped allow_overlap。

## 与相邻类别的边界

- 不该混入：**container_plastic_can 通用塑料罐**——理由：plastic_can 是短粗罐 + 提环 / 螺旋盖，无洗衣液壶的整体 +X 侧环形提手 + 量杯螺纹盖 spine；本类身份是大容积 HDPE 壶 + 一体侧提手 + 量杯盖。
- 不该混入：**container_dispenser 皂液 / 乳液分配器**——理由：dispenser 是细颈瓶 + 长泵管按压头为主体，无大容积壶身 + 无侧环提手；本类 pump_dispenser 仅是洗衣液壶的一个**可替换封口候选**，主体仍是带提手的壶。
- 不该混入：**container_pump 压泵瓶**——理由：pump 瓶小容量、泵是固有主体；本类是洗衣液壶（jug 主体 + 整体侧提手），泵头只是 closure 三候选之一。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT：4 body × 3 handle × 3 closure = 36 combos；body×closure=12 clears 。closure 三族 joint 拓扑：screw cup(CONT+PRIS+massless carrier) / flip(REV +X 后铰) / pump(CONT+PRIS+dip_tube 2 part)。handle 为 body mesh 操作（union 环/提梁、cut 凹位），非独立 part。无 multiplicity 轴（pump grip ridges 为固定装饰环）。palette_style 9 colorway + 显式 material-finish 维（glossy_hdpe / translucent / opaque_matte / pearlescent；含 brand-color HDPE 橙/绿/黄/青/紫/粉、translucent 壶身或量杯盖、opaque_matte、white、two-tone cap、pearlescent；per-seed `rng.choice`，palette-only 不计 slot_choice）。注：源映射 joint 名 `neck_to_lid`/`body_to_pump` 实际为 `body_to_lid`/`collar_screw`+`pump_press`（已按真实 model.py 名校正）。|

## 模板实现备注（可选）

- 共享 helper：`_body_shell(body_shape, sections)`（圆 / 扁椭圆 / 收腰 loft）+ `_square_body`（box+fillet+方肩 step）+ `_neck_with_bore(neck_r, neck_top_z)` + `_pour_spout` 全 module 公用；handle 三族 `_handle_solid` / `_grip_recess` / `_top_carry_handle` 作 body mesh 阶段 union/cut helper。
- screw cup：必须经 massless `cap_carrier`（无 visual，1e-4 mass Box inertial）解耦 `cap_rotate`(CONTINUOUS)→`cap_slide`(PRISMATIC)；保 off-axis `cap_marker` 供 swing 测试。
- flip：body 须加 `_neck_collar` 领圈作 hinge 座，`lid` 独立 part 绕 `body_to_lid` REVOLUTE +X（HINGE_ORIGIN 后 collar 边）；lid local frame 原点在 hinge，disc 在 +Y 偏移盖回 mouth 中心。
- pump：`pump_base`（housing + dip_tube + grip ridges）→ `collar_screw` CONTINUOUS +Z；`pump_actuator`（head+nozzle+stem）→ `pump_press` PRISMATIC axis=(0,0,-1)；dip_tube 下伸穿 neck 入瓶（allow_overlap dip_tube↔jug_shell）。
- captured-fit overlap：`run_container_laundry_detergent_bottle_tests` 里 `ctx.allow_overlap`(cap_cup↔jug_shell、cap_cup↔pour_spout、lid skirt↔neck_collar、dip_tube↔jug_shell、actuator_stem↔pump_housing)。
- neck_radius equation：`resolve_config` 派生 `cap_bore_R = NECK_R + clearance`、`lid_skirt_inner_R = COLLAR_R + clearance`、`cap_outer_R ≤ body_half_min + proud`，盖罩配合不等式在 resolve 投影；top_carry 拱峰 clearance 不等式同样在 resolve 解。
- 参考模板：`agent/templates/Container_Jar.py`（同 Container 大类，body×lid×seal 三轴 parallel_children + massless carrier 解耦 screw + REVOLUTE flip + 多 closure 分支 + captured-fit allow_overlap 骨架，最近邻参考）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | flat_oval_jug + side_loop_handle + measuring_cup_cap | rec_orange-tide-...-8f73f587 | `_body_shell` L47-95 / `_handle_solid` L98-122 / `_cap_mesh` L135-160 / `cap_carrier` L209 / `cap_rotate`+`cap_slide` L228-246 | 扁椭圆 body 基线 + 侧环提手基线 + 量杯螺纹盖 + massless carrier 双关节 |
| S2 | A | round_cylinder | rec_...-var_cyl_body | `_body_shell` L52-93（circle 截面 loft）| 高身圆柱罐 body |
| S3 | A | square_shoulder | rec_...-var_square_body | `_main_body_box` L64-80 / `_shoulder_neck` L83-109 | 方截面 + 方肩 step body（2 段 visual）|
| S4 | A | waisted_contour | rec_...-var_waist_body | `_body_shell` L52-103（waist pinch loft）| 中段收腰 contour body |
| S5 | B | recessed_grip | rec_...-var_grip_indent | `_grip_recess` L99-115 / `shell.cut` L169 | 球面凹形手指 scoop（壁连续）|
| S6 | B | top_carry_handle | rec_...-var_top_handle | `_top_carry_handle` L112-142 / `shell.union` L194 | 倒 U 拱形顶提梁 sweep 管 |
| S7 | C | flip_top_cap | rec_...-var_flip_cap | `_neck_collar` L131-146 / `_lid_mesh` L159-214 / `body_to_lid` REVOLUTE L285-294 | 后铰 snap 翻盖（REVOLUTE +X）|
| S8 | C | pump_dispenser | rec_...-var_pump_cap | `_pump_housing_mesh` L159 / `pump_base`+`dip_tube` L273-302 / `_actuator_head_mesh`+`pump_actuator` L319 / `collar_screw`+`pump_press` L352-373 | 螺纹领泵头分配器（CONT+PRIS 2 part + dip tube）|
