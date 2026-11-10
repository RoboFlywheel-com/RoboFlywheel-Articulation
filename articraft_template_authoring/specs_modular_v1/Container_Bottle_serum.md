# container_bottle_serum — Modular Spec

> 来源小类：`picture/Container/Bottle serum`（articraft_data 上游 Container/Bottle serum fork-variant pool）。
> source map：`<ARTI_SKILL_ROOT>/articraft_data/picture_expansion/template_source_maps/Container__Bottle_serum.md`。
> 引用 `model.py:Lx-Ly` 来自各样本 `articraft_data` / `arti-template` 当前 `revisions/rev_000001/model.py`（两库逐字一致）；以 part/joint/helper **名字** 为准（`body` / `dropper` / `_body_glass_mesh` / `_collar_mesh` / `label_band` / `body_to_dropper` / `body_to_cap` / `body_to_pump` / `body_to_actuator` / `body_to_ball` / `body_to_overcap` / `body_to_wand` / `housing` / `dip_tube` / `pump_actuator` / `roller_ball` / `overcap` / `applicator_tip` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_bottle_serum` |
| template path | `agent/templates/Container_Bottle_serum.py` |
| test path (optional) | (inline `run_container_bottle_serum_tests`，sweep 为唯一验收) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots：body_shape（root 玻璃壳）+ closure（封口/分配机构，挂到 body 共同 parent）；无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11（1 parent + 10 single-axis converged fork 变体）|
| read_count | 11（全部读 `model.py` 全文：parent + tapered/squared/boston_round/tall_slim_vial/faceted_prism 5 个 body 轴变体 + screw_cap/pump_dispenser/mist_sprayer/roller_ball/brush_wand 5 个 closure 轴变体）|
| read_scope | all 5-star samples in this category（single-axis fork pool：A 行变体只改 body、closure 恒为 parent dropper；B 列变体只改 closure、body 恒为 parent round_cylinder）|
| source_index_policy | only adopted module sources are indexed below（§14）|

冗余/分流说明：
- parent（`rec_small-amber-glass-serum-bottle-with-a-white-rubb_...98768519`）自身占据 `(round_cylinder × dropper_prismatic)` 这一格，同时提供 **body_shape 基线**（`_body_glass_mesh` L58-L97）与 **closure 基线**（`dropper` 单刚体 + `body_to_dropper` PRISMATIC L184-L197）。
- 5 个 body 轴变体只换 `_body_glass_mesh` 的截面/轮廓（直筒→锥/方/球肩/高瘦/八棱），dropper 封口与 parent 逐字相同 → 采纳为 body_shape 候选，不进 closure。
- 5 个 closure 轴变体只换封口子树（旋盖/泵/喷雾/滚珠/刷棒），body 与 parent 逐字相同 → 采纳为 closure 候选，不进 body_shape。
- 全部变体共享 `body`(root) + `label_band` 视觉 + 单壳 hollow-bore 语义；只换尺寸/颜色不另列 candidate。

## 核心身份

`container_bottle_serum` 是**小号护肤/化妆品精华液瓶**：一只直立、矮（squat，多数 body 高 < 0.09 m）、窄（直径 ~0.013–0.038 m）的中空玻璃瓶，中心轴沿 +Z，底坐地 z=0，居中于 (x=0,y=0)。瓶身由 CadQuery `extrude`/`loft`/`polygon` 或 `LatheGeometry` 发射为**厚壁中空开口腔**（真实 bore，读作可装液的容器），中段缠一条白色 `label_band`（fixed parent visual，~0.012–0.062 m 高的环带）。瓶口上方一只**精华液专用小型封口/分配机构**按某种动作开合/分配（**主活动语义**）：

- 滴管（dropper：collar + 球泡 bulb + 透明 pipette 单刚体，PRISMATIC +Z 直拉拔出，pipette 抽离瓶口）；
- 旋盖（screw cap：白色带 grip 肋的盖，REVOLUTE +Z 绕瓶轴拧）；
- 乳液泵头（pump：固定 collar + dip tube 挂 body，pump_head actuator PRISMATIC −Z 下按）；
- 细雾喷头（mist sprayer：crimp collar + dip tube 挂 body，actuator 扁按钮 + 前置 nozzle PRISMATIC −Z 下按）；
- 滚珠涂抹（roller ball：housing socket 挂 body，钢珠 REVOLUTE +X 原位滚 + 可摘 overcap PRISMATIC +Z 拔起）；
- 刷棒/棒头（brush wand：twist-off 盖 + 长 stem + doe-foot applicator 单刚体，PRISMATIC +Z 直拉拔出）。

默认成熟域：单瓶单封口（无嵌套、无 multiplicity）。封口尺度小（精华液专用，盖直径 ~0.02–0.026 m），与大号乳液/喷雾瓶刻意区分。

不该混入：通用细颈液体瓶 / 酒瓶（`container_bottle`，更大、更长颈、封口家族更宽）、宽口带盖储物罐（`container_jar`，口径≈瓶身、旋盖为主）、通用玻璃瓶（`container_glass_bottle`，不限精华液小型封口语义）。serum 瓶的身份锚点：**小尺度 + 精华液专属封口（dropper/roller/wand 尤其专属）+ label band + 琥珀/磨砂玻璃外观**。

## 槽位 + 候选模块表

> **建模注记**：`body_shape` 是 `body`(root) 的 `_body_glass_mesh` 属性（一次发射 hollow shell + shoulder + neck + bore，外加 `label_band` fixed visual），不是独立串联 slot。`closure` 各候选挂到 `body` 共同 parent（parallel children；含 fixed visual + 1–2 个活动子件）。两轴笛卡尔积构成拓扑多样性（见 §9）。

### Slot A：body_shape（瓶身轮廓 / 形状家族——root `body` 的 `_body_glass_mesh` + `label_band`）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `round_cylinder`（基线）| rec_small-amber-glass-serum-bottle-with-a-white-rubb_...98768519 | `_body_glass_mesh` L58-L97（`circle.extrude` 直筒 + loft 圆肩 + circle neck + tapered loft cavity）+ `label_band` L133-L140 | eligible if compatible | 直筒圆柱身（H≈0.082, R=0.015）+ loft 圆肩 + 圆 neck，单壳 hollow open bore；环形 label_band |
| `tapered_cone` | rec_container_bottle_serum_var_tapered_body | `_body_glass_mesh` L68-L109（`circle→circle loft` 锥身 base R=0.017→top R=0.011）+ `_body_radius` L62-L65 + `_label_mesh`（锥形 loft 环带）L112-L135 | eligible if compatible | 底宽顶窄圆锥收腰身，平滑过渡到肩颈；label 跟随锥度 loft |
| `squared_faceted` | rec_container_bottle_serum_var_squared_body | `_body_glass_mesh` L76-L129（`rect.extrude.fillet("|Z")` 方身 + rect→circle 肩 loft + box-shell cavity）+ `_rounded_rect_solid` L64-L73 + `_label_band_mesh` L132-L143 | eligible if compatible | 方形截面（W=0.028）+ 圆角竖边平面身 → 升至圆肩 → 圆 neck，方 box-shell 中空；方形 label |
| `boston_round` | rec_container_bottle_serum_var_boston_round_body | `_body_glass_mesh` L116-L127（`LatheGeometry.from_shell_profiles` 旋转壳）+ `_outer_profile` L72-L92 + `_inner_profile` L95-L113（catmull-rom 样条）| eligible if compatible | 高身（H≈0.098）+ 鼓圆下肩（belly R=0.019）+ 明显收腰窄颈（NECK_R=0.0075），lathe 旋转 spline 壳 |
| `tall_slim_vial` | rec_container_bottle_serum_var_tall_slim_vial | `_body_glass_mesh` L61-L113（`circle.extrude` 高瘦直管 R=0.0065, H=0.098 + minimal loft 肩 + base_round cut）| eligible if compatible | 高纵横比细长直管身（aspect>6）+ 极简肩直入颈（安瓿/试管式血清瓶）；薄壁 WALL=0.0012 |
| `faceted_prism` | rec_container_bottle_serum_var_faceted_prism | `_body_glass_mesh` L78-L126（`polygon(8,DIAM).extrude` 八棱身 + polygon→circle 肩 loft + polygon-bore cavity）+ `_polygon_profile` L73-L75 + `_label_band_mesh` L129-L144 | eligible if compatible | 正八棱柱平面棱柱身（apothem=0.015）+ 棱面升至圆肩圆颈（区别于 4 面 squared）；八棱 label |

硬约束记录：body_shape 6 candidate（达 3-6 目标上限）。全部单壳 hollow open-bore + shoulder + neck，共享 `_collar` / closure 接口（neck rim @ NECK_TOP），只换截面族（圆 extrude / 锥 loft / 方 box-shell / lathe spline / 八棱 polygon）+ 高宽比 + label 形状。primitive 真实差异：`extrude` vs `loft` vs `rect+fillet+box-shell` vs `LatheGeometry` vs `polygon`。

### Slot B：closure（**主开合/分配机构槽**——精华液封口动作）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / joint / 结构特征 |
|---|---|---|---|---|
| `dropper_prismatic`（基线）| rec_small-amber-glass-serum-bottle-with-a-white-rubb_...98768519 | `dropper` part L149-L182（`_collar_mesh` L100-L117 + `bulb` Sphere L155-L160 + `bulb_stem` L162-L167 + `pipette` L171-L176）+ `body_to_dropper` PRISMATIC +Z L184-L197（upper=DROPPER_TRAVEL=0.068）| eligible if compatible | 滴管单刚体（collar + 球泡 + 透明 pipette）；1 活动 part + 1 PRISMATIC +Z joint，直拉拔出 pipette 抽离瓶口 |
| `screw_cap_revolute` | rec_container_bottle_serum_var_screw_cap | `cap` part L162-L189（`_cap_shell_mesh` L100-L121 + `rib_{i}` for-loop N_RIBS=24 L172-L183）+ `body_to_cap` REVOLUTE +Z L192-L205（origin z=NECK_TOP, upper=2π）| eligible if compatible | 白色带 24 grip 肋旋盖；1 活动 part + 1 REVOLUTE +Z joint（绕瓶轴拧），cap skirt 干涉配合罩 neck |
| `pump_dispenser_prismatic` | rec_container_bottle_serum_var_pump_dispenser | body-fixed `pump_collar`（`_collar_mesh` L112-L139）+ `dip_tube`（`_dip_tube_mesh` L142-L162）；`pump_head` part L253-L267（`_pump_actuator_mesh` head+nozzle+stem L165-L203）+ `body_to_pump` PRISMATIC −Z L272-L285（origin z=COLLAR_TOP, upper=PUMP_TRAVEL=0.008）| eligible if compatible | 乳液泵头：固定 collar + dip_tube 挂 body；actuator（head 盘 + 侧 nozzle + stem）1 活动 part，PRISMATIC −Z 下按；stem captured 在 collar bore |
| `mist_sprayer_prismatic` | rec_container_bottle_serum_var_mist_sprayer | body-fixed `crimped_collar`（`_collar_mesh` L124-L139）+ `crimp_ridge_{i}` for-loop N=12（`_crimp_ridge_mesh` L142-L154）+ `dip_tube`（`_dip_tube_mesh` L157-L174）；`actuator` part L263-L285（`spray_button` `_button_mesh` L177-L184 + `nozzle` `_nozzle_mesh` L187-L220 + `pump_stem`）+ `body_to_actuator` PRISMATIC −Z L289-L302（upper=PRESS_TRAVEL=0.006）| eligible if compatible | 细雾喷头：固定 crimp collar（12 crimp 肋）+ dip_tube 挂 body；actuator（扁按钮 + 前置 +Y nozzle + stem）1 活动 part，PRISMATIC −Z 下按 |
| `roller_ball_revolute` | rec_container_bottle_serum_var_roller_ball | body-fixed `housing`（`_housing_mesh` socket cup L120-L157）+ `retainer_tab_{i}` for-loop RETAINER_COUNT=3（`_retainer_tab_mesh` L160-L167）；`roller_ball` part L257-L268（Sphere）+ `overcap` part L271-L277（`_overcap_mesh` L170-L197）+ `body_to_ball` REVOLUTE +X L284-L297（origin z=BALL_CZ）+ `body_to_overcap` PRISMATIC +Z L302-L315（upper=OVERCAP_TRAVEL=0.055）| eligible if compatible | 滚珠涂抹：socket housing + 3 retainer tab 挂 body；**2 活动 part** —— 钢珠 REVOLUTE +X 原位滚（socket 捕获）+ 可摘 overcap PRISMATIC +Z 拔起；joint 拓扑最丰（2 joint，含 +X 轴）|
| `brush_wand_prismatic` | rec_container_bottle_serum_var_brush_wand | `wand` part L197-L225（`cap_shell` `_cap_shell_mesh`(dome+grip ring) L103-L143 + `stem` Cylinder L207-L212 + `applicator_tip` `_applicator_tip_mesh`(doe-foot loft) L146-L165）+ `body_to_wand` PRISMATIC +Z L227-L240（upper=WAND_TRAVEL=0.072）| eligible if compatible | 刷棒/棒头盖单刚体（twist-off 盖 + 长 stem + doe-foot applicator）；1 活动 part + 1 PRISMATIC +Z joint，直拉拔出，applicator 深入瓶 |

硬约束记录：closure 6 candidate（达 3-6 目标上限）。含 PRISMATIC +Z（dropper / wand 单刚体直拉）/ REVOLUTE +Z（screw 拧）/ PRISMATIC −Z（pump / mist 下按 + 固定 collar+dip_tube body visual）/ REVOLUTE +X + PRISMATIC +Z（roller 双活动件）四类 joint 拓扑 + 不同 part count（1 活动 part 的 dropper/screw/wand/pump/mist vs 2 活动 part 的 roller）+ 不同 body-fixed visual 组（dropper/screw/wand 无；pump/mist 加 collar+dip_tube；roller 加 housing+retainer_tab）。每个 candidate **≥1 non-fixed joint**（满足精华液瓶活动封口契约）。

## 槽位图（slot graph）

pattern: `parallel_children`（`body` 为 root，closure 子树挂到它；无 multiplicity）

```
body(body_shape)  [ROOT, 坐地 z=0；visual: body_glass shell + label_band 固定环带]
   │  neck rim datum @ NECK_TOP（mouth bore @ BORE_R，neck outer @ NECK_R）= 所有 closure 的共同接口面
   │
   ├── closure = dropper_prismatic:
   │     body --[body_to_dropper: PRISMATIC +Z @ origin(0,0,0)]--> dropper(collar+bulb+pipette 单刚体)
   │
   ├── closure = screw_cap_revolute:
   │     body --[body_to_cap: REVOLUTE +Z @ origin(0,0,NECK_TOP)]--> cap(shell + 24 ribs)
   │
   ├── closure = pump_dispenser_prismatic:
   │     body(+ pump_collar fixed visual + dip_tube fixed visual)
   │     body --[body_to_pump: PRISMATIC −Z @ origin(0,0,COLLAR_TOP)]--> pump_head(head+nozzle+stem)
   │
   ├── closure = mist_sprayer_prismatic:
   │     body(+ crimped_collar fixed + 12 crimp_ridge fixed + dip_tube fixed)
   │     body --[body_to_actuator: PRISMATIC −Z @ origin(0,0,COLLAR_TOP)]--> actuator(button+nozzle+stem)
   │
   ├── closure = roller_ball_revolute:
   │     body(+ housing fixed + 3 retainer_tab fixed)
   │     body --[body_to_ball:    REVOLUTE +X @ origin(0,0,BALL_CZ)]--> roller_ball(steel sphere)
   │     body --[body_to_overcap: PRISMATIC +Z @ origin(0,0,0)]--> overcap(protective shell)
   │
   └── closure = brush_wand_prismatic:
         body --[body_to_wand: PRISMATIC +Z @ origin(0,0,0)]--> wand(cap+stem+doe-foot 单刚体)
```

接口点位与 joint 语义：
- **共同 datum**：`body`(root) 的 neck rim 平面 @ `NECK_TOP`（bore @ `BORE_R`，neck outer @ `NECK_R`）是每个 closure 子树的共享 mating datum。所有 closure 居中于瓶轴 (x=0,y=0)。
- **dropper / wand 接口（PRISMATIC +Z 单刚体拉出）**：`body_to_dropper` / `body_to_wand` origin (0,0,0)，axis +Z，PRISMATIC，q=0 collar/cap skirt 罩 neck（captured，pipette/stem 深入瓶），正 q 直拉拔出（pipette/applicator 抽离 NECK_TOP）。collar/cap skirt ↔ body_glass + pipette/stem ↔ body_glass 为 element-scoped `allow_overlap`。
- **screw 接口（REVOLUTE +Z 拧）**：`body_to_cap` origin (0,0,NECK_TOP)，axis +Z，REVOLUTE upper=2π；cap skirt 干涉配合罩 neck（`expect_overlap` along z ≥0.005），原位旋转不升降不平移。
- **pump / mist 接口（PRISMATIC −Z 下按 + body-fixed collar/dip_tube）**：`pump_collar`/`crimped_collar` + `dip_tube`（+ mist 的 12 `crimp_ridge`）是 **body 固定 visual**（无独立 joint），collar 罩 neck、dip_tube 伸到瓶底；`body_to_pump`/`body_to_actuator` origin (0,0,COLLAR_TOP)，axis −Z，PRISMATIC（q=0 head 在 collar 顶，正 q 下按 PUMP/PRESS_TRAVEL）；actuator stem captured 在 collar bore（`allow_overlap` + `expect_overlap` along z + `expect_origin_distance` xy<0.001 保轴对齐）。dip_tube 在按压时静止（属 body）。
- **roller 接口（REVOLUTE +X 滚 + PRISMATIC +Z 拔盖 + body-fixed housing）**：`housing`（socket cup）+ 3 `retainer_tab` 是 body 固定 visual；`body_to_ball` origin (0,0,BALL_CZ)，axis +X，REVOLUTE [-π,π]（钢珠原位滚，sphere 不变量：旋转后 AABB 不动，ball ↔ housing socket `allow_overlap`+`expect_contact` 捕获）；`body_to_overcap` origin (0,0,0)，axis +Z，PRISMATIC upper=OVERCAP_TRAVEL，q=0 overcap 罩住 ball（`expect_within` z 包容），正 q 拔起 clears ball（overcap ridge ↔ housing `allow_overlap`+`expect_contact` clip-fit）。
- **rest pose**：所有封口 q=0 闭合/坐下（dropper/wand pipette 深插、screw cap 罩 neck、pump/mist head 在 collar 顶、roller overcap 罩 ball + 钢珠 seated）。pull/press/twist/roll 为 viewer 目检的活动语义。
- **互斥 / 可选**：closure 各候选互斥（一次只一种封口机构）。无可选 slot；无 multiplicity。pump/mist/roller 的 body-fixed visual 组只在对应候选发射。

## 每槽位 Module Emits / Interfaces

### Slot A / `body`（body_shape，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（visual: `body_glass` 单壳 hollow open-bore + shoulder + neck + `label_band` 固定环带）| parent `_body_glass_mesh` L58-L97 / `label_band` L133-L140 |
| internal joints | 无（root 瓶体本身无活动件；label_band 是 fixed visual）| — |
| upstream interface | 坐地 z=0（root）| parent BODY_Z0 L33 |
| downstream interface | neck rim top 中心 @ NECK_TOP（bore @ BORE_R，neck outer @ NECK_R）= closure joint 的 parent 接口 | parent NECK_R/NECK_TOP/BORE_R L36-L39 |

### Slot B / closure（每候选发射对应活动封口）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dropper`(单刚体) / `cap`(+24 ribs) / `pump_head`(+body-fixed pump_collar+dip_tube) / `actuator`(+body-fixed crimped_collar+12 crimp_ridge+dip_tube) / `roller_ball`+`overcap`(+body-fixed housing+3 retainer_tab) / `wand`(单刚体) | 各 closure 源（见 slot 表）|
| internal joints | `body_to_dropper` PRISMATIC +Z / `body_to_cap` REVOLUTE +Z / `body_to_pump` PRISMATIC −Z / `body_to_actuator` PRISMATIC −Z / `body_to_ball` REVOLUTE +X + `body_to_overcap` PRISMATIC +Z / `body_to_wand` PRISMATIC +Z | parent L184-197 / screw L192-205 / pump L272-285 / mist L289-302 / roller L284-315 / wand L227-240 |
| upstream interface | closure mount 在 neck rim（dropper/wand/screw origin 在瓶轴；pump/mist collar 罩 neck + dip_tube 伸瓶底；roller housing socket 在 neck top）| 各源 collar/housing 几何 |
| downstream interface | 活动件末端（pipette tip / cap top / nozzle spout / ball surface / doe-foot tip）= viewer 目检活动语义 | 各源 |

### closure 内 body-fixed visual（pump / mist / roller 时，固定 visual 挂 `body`）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`pump_collar` / `crimped_collar`+`crimp_ridge_{i}` / `dip_tube` / `housing`+`retainer_tab_{i}` 为 `body` 的固定 visual）| pump L240-244 / mist L247-254 / roller L233-245 |
| internal joints | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `body_shape` | enum | round_cylinder / tapered_cone / squared_faceted / boston_round / tall_slim_vial / faceted_prism | round_cylinder | choice | deterministic procedural sampler 选 | Slot A module table |
| `closure` | enum | dropper_prismatic / screw_cap_revolute / pump_dispenser_prismatic / mist_sprayer_prismatic / roller_ball_revolute / brush_wand_prismatic | dropper_prismatic | choice | sampler 选 | Slot B module table |
| `palette_style` | enum | amber_apothecary / clear_minimal / frosted_white / cobalt_blue / green_glass / opaque_white / soft_touch_black / gold_luxe / pearlescent_blush / matte_sage | amber_apothecary | palette | palette only，每 seed `rng.choice` 选；**不计入 slot_choice / topology**；含独立 finish 维度 | §palette（5★ 源材料）|
| `body_height_scale` | float | [0.85, 1.18] | 1.0 | independent | 缩放 BODY_TOP/SHOULDER_TOP/NECK_TOP → closure mount 高度同步，clamp | parent L34-37 |
| `body_radius_scale` | float | [0.88, 1.15] | 1.0 | independent | 缩放 BODY_R / BODY_W / apothem / belly R → label R 同比，clamp（neck R 不动，保封口配合）| parent L32 / squared L35 / faceted L35 |
| `neck_radius_scale` | float | [0.92, 1.10] | 1.0 | equation | `NECK_R = base · neck_radius_scale`；collar bore / cap bore / housing bore / cap_shell skirt 半径派生跟随（保罩/插配合）| parent L36 / 各 closure collar bore |
| `closure_size_scale` | float | [0.90, 1.12] | 1.0 | equation | `= clamp(0.9·neck_radius_scale + 0.1)`；缩放 collar/cap/housing/bulb/head 外径，跟随 neck 派生（封口随瓶口比例）| 各 closure 外径 |
| `joint_travel_scale` | float | [0.85, 1.12] | 1.0 | independent | 缩放 DROPPER/WAND/OVERCAP/PUMP/PRESS_TRAVEL + ball/screw limit，clamp | 各 closure TRAVEL/limit |
| (—) | constraint | — | — | inequality | 封口配合：`collar_bore_R ≥ NECK_R + clearance` 且 `collar_outer_R ≤ body_max_R + proud`；违反按比例回缩 closure_size/neck scale | 接口 / clearance |
| (—) | constraint | — | — | inequality | 身份保形：`0.010 < body_dia < 0.045` 且（除 boston/vial 外）`body_h < 0.095`；pipette/stem/dip_tube `tip_z < SHOULDER_TOP − 0.010`（深插）；违反则按 body_shape 派生界回缩 | 类别身份 / 各源 check |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。采样契约：先采 `independent`（body_height/body_radius/joint_travel）→ 按 `equation` 派生 neck_radius 驱动 collar/cap/housing bore + closure_size → 用 `inequality` 把封口配合 + 身份保形投影/回缩，无法满足则拒绝重采。scale 只动安全比例 / clearance / 细节尺寸，绝不改 body_shape / closure 的拓扑、joint 轴或 part count。`palette_style` 是 palette，不计入 slot_choice 或 topology 等价类。

### palette_style 取值（8–10 coordinated colorways + 显式 finish 维度，锚定 5★ 源材料）

> palette 只换**配色 + 表面 finish 语义**，不改任何几何 / 拓扑 / slot / joint / multiplicity。每个 colorway 给四组件配色 —— **body_glass（瓶身）/ closure_cap（封口/盖/dropper 主体）/ collar_accent（领圈/accent 件）/ label（标签纸带）** —— 加一列**显式 `finish`**（gloss_glass / frosted_glass / opaque_matte / soft_touch / metallic / pearlescent）。`finish` 是 palette 内的独立外观维度（不另立 slot），与 rgba 一同由 `rng.choice(PALETTE_STYLES)` 整组选中。
>
> **finish 维度取值**（材料表面语义，决定 alpha / 高光读法，**非几何**）：
> - `gloss_glass` —— 高光透明玻璃，带真实 alpha（0.40–0.55），r/g/b 透色（amber/clear/cobalt/green）。
> - `frosted_glass` —— 磨砂半透玻璃，中等 alpha（0.55–0.70），柔白雾面。
> - `opaque_matte` —— 不透明哑光瓷/塑料，alpha=1.0，无高光。
> - `soft_touch` —— 软触橡胶哑光涂层，alpha=1.0，深色低反。
> - `metallic` —— 金属/电镀盖件（金/钢），alpha=1.0，中高明度暖/冷金属，**非霓虹**。
> - `pearlescent` —— 珠光半透微闪，alpha≈0.85，浅粉/裸色柔光。

| palette_style | finish | body_glass rgba | closure_cap rgba | collar_accent rgba | label rgba | 说明 / 来源 |
|---|---|---|---|---|---|---|
| `amber_apothecary`（基线）| gloss_glass | (0.45, 0.24, 0.06, 0.5) | (0.95, 0.95, 0.94, 1.0) | (0.95, 0.95, 0.94, 1.0) | (0.97, 0.97, 0.96, 1.0) | 琥珀玻璃（半透 r>b）+ 白塑封口 —— 全 11 个 5★ 样本 body/closure/label 逐字材质（parent L123-126，amber/white_plastic/label_white）|
| `clear_minimal` | gloss_glass | (0.85, 0.90, 0.92, 0.40) | (0.95, 0.95, 0.94, 1.0) | (0.92, 0.92, 0.91, 1.0) | (0.97, 0.97, 0.96, 1.0) | 透明/淡蓝玻璃（精华液常见无色瓶）+ 白盖 | 5★ clear_glass/clear_tube (0.85,0.90,0.92,0.35) L126/L216 提升为 body + white_plastic/pump_white |
| `frosted_white` | frosted_glass | (0.93, 0.93, 0.92, 0.58) | (0.95, 0.95, 0.94, 1.0) | (0.88, 0.88, 0.90, 1.0) | (0.97, 0.97, 0.96, 1.0) | 磨砂半透白玻璃（高端精华瓶）+ 白盖 + 浅灰 accent | white_plastic L124 半透化 + cap_gray (0.88,0.88,0.90,1.0) L212 collar |
| `cobalt_blue` | gloss_glass | (0.10, 0.18, 0.45, 0.5) | (0.95, 0.95, 0.94, 1.0) | (0.72, 0.73, 0.76, 1.0) | (0.97, 0.97, 0.96, 1.0) | 钴蓝玻璃（精油/精华常见）+ 白盖 + 钢色领圈 | amber 半透结构的蓝色变体 + steel_ball (0.72,0.73,0.76,1.0) L211 accent |
| `green_glass` | gloss_glass | (0.16, 0.34, 0.18, 0.5) | (0.95, 0.95, 0.94, 1.0) | (0.95, 0.95, 0.94, 1.0) | (0.97, 0.97, 0.96, 1.0) | 茶绿/橄榄玻璃 + 白塑封口 | amber 半透结构的绿色变体 + white_plastic L124 |
| `opaque_white` | opaque_matte | (0.96, 0.96, 0.95, 1.0) | (0.95, 0.95, 0.94, 1.0) | (0.88, 0.88, 0.90, 1.0) | (0.97, 0.97, 0.96, 1.0) | 不透明白瓷/塑料精华瓶（无 alpha）+ 白盖 + 浅灰 accent | white_plastic L124（不透明）+ cap_gray L212 |
| `soft_touch_black` | soft_touch | (0.10, 0.10, 0.11, 1.0) | (0.14, 0.14, 0.15, 1.0) | (0.20, 0.20, 0.21, 1.0) | (0.93, 0.93, 0.92, 1.0) | 软触哑光黑瓶（男士/高端精华）+ 深灰盖 + 浅标签 | white_plastic L124 暗化为软触深色（推断真实 colorway）|
| `gold_luxe` | metallic | (0.18, 0.13, 0.06, 0.55) | (0.78, 0.62, 0.30, 1.0) | (0.78, 0.62, 0.30, 1.0) | (0.85, 0.74, 0.50, 1.0) | 深棕玻璃身 + 金属金盖/金领圈（奢华精华），金非霓虹（暖中明度）| amber 半透结构 deepened body + 推断 metallic gold cap |
| `pearlescent_blush` | pearlescent | (0.93, 0.84, 0.83, 0.85) | (0.96, 0.90, 0.88, 1.0) | (0.82, 0.70, 0.62, 1.0) | (0.97, 0.95, 0.94, 1.0) | 珠光裸粉瓶（半透微闪）+ 柔粉盖 + 玫瑰金 accent | white_plastic 调暖珠光化（推断真实精华 colorway）|
| `matte_sage` | opaque_matte | (0.62, 0.66, 0.55, 1.0) | (0.95, 0.95, 0.94, 1.0) | (0.55, 0.55, 0.56, 1.0) | (0.93, 0.93, 0.91, 1.0) | 哑光鼠尾草绿瓶（草本/天然精华）+ 白盖 + 灰 accent | green_glass 不透明哑光变体 + pump_grey (0.55,0.55,0.56,1.0) L230 accent |

> palette 整组换 body_glass / closure_cap / collar_accent / label 四组件配色 + `finish` 表面语义，**不改任何几何/拓扑/slot/joint/multiplicity**。每个 colorway 是一组**协调配色 + 一个 finish**，由 `rng.choice(PALETTE_STYLES)` 整体选中（per-seed）。玻璃系 finish（gloss_glass / frosted_glass / pearlescent）带真实 alpha（0.40–0.85）；金属盖（gold_luxe）暖中明度非霓虹；soft_touch 深色低反 alpha=1.0。各 closure 内部子件（bulb / pipette / housing / steel ball / doe-foot applicator / dip_tube / nozzle）仍沿用各源功能性材质（clear / steel_ball / flocked_tip / pump_grey），只 body+主封口外壳+collar accent+label 随 colorway 协调换色。target **10 coordinated colorways**（含 6 原始 realistic + 4 新增 soft_touch_black / gold_luxe / pearlescent_blush / matte_sage），最低门槛 ≥3 远超。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（body_shape + closure）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。单瓶单封口。
- 说明：`rib_{i}`(N=24, screw) / `crimp_ridge_{i}`(N=12, mist) / `retainer_tab_{i}`(N=3, roller) 是各 closure module 内部 **mesh 装饰细节计数**（fixed visual，固定常量，体现该封口身份），不是模板级 multiplicity 轴，不暴露为 `*_count`、不进 `slot_choices`、不改 part-tree 拓扑等价类。

## 拓扑多样性审计

总组合数：body_shape(6) × closure(6) = **36 distinct (body_shape, closure) 组合**。
（无 multiplicity 轴，N=1。）

拓扑等价类（由 closure 决定 joint 拓扑 + part count，body_shape 决定 root mesh 族）：6 body_shape × 6 closure = **36 distinct topology classes**（remote 一致：每组合的 part-tree / joint 集合不同）。仅 closure 一轴就给出 4 类 joint 拓扑（PRISMATIC+Z 单刚体 / REVOLUTE+Z / PRISMATIC−Z+body-fixed-collar / REVOLUTE+X+PRISMATIC+Z 双活动件）。

理由：36 distinct 组合远超 10。closure 引入 dropper/wand（PRISMATIC +Z 单刚体直拉）/ screw（REVOLUTE +Z）/ pump/mist（PRISMATIC −Z + body-fixed collar+dip_tube）/ roller（REVOLUTE +X 滚 + PRISMATIC +Z 拔盖，2 活动 part）等不同 joint 拓扑 + 不同 part count + 不同 body-fixed visual 组，是真实结构差异。body_shape 在 6 个 mesh 族（圆 extrude / 锥 loft / 方 box-shell / lathe spline / 八棱 polygon）间换 root primitive。slot_choices 编入两轴。10-seed sweep 即可轻松采到 ≥10 distinct。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 两个 named slot（笛卡尔积 36 全合法，少量 resolve 派生见下），再 uniform 各连续 scale（先 independent → equation 派生 → inequality 投影）+ `rng.choice` palette_style。compatibility matrix 在 resolve 内适配尺寸（无硬 gate-out）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 **36**（= body_shape × closure，本小类真实结构词汇上限；两轴均受真实样本词汇约束，不强行注水）。低于 300 guideline 的原因：精华液瓶真实结构家族就是 6 body × 6 closure = 36，是该类目合理上限，已远超 ≥10 机械门槛，noted。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表 5 个 scale（body_height / body_radius / neck_radius / closure_size / joint_travel）。全部 `resolve_config` clamp + 每 build 统一应用。`neck_radius_scale` 为 equation（collar/cap/housing bore + closure_size 派生跟随，保封口罩/插配合）；`closure_size_scale` 为 equation（跟随 neck）。封口配合 + 身份保形不等式在 resolve 内投影/回缩，不留到 builder。这些 scale 不破坏 closure joint origin（neck rim / COLLAR_TOP / BALL_CZ）、封口配合、label 位置、深插语义或类别身份（小尺度 squat 瓶）。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 两 named slot（36 全正交合法），再 uniform 各 scale（independent→equation→inequality）+ `rng.choice` palette_style | slot_choices_for_seed 含两轴且与 build 一致 |
| compatibility matrix | (1) pump/mist/roller 的 body-fixed collar/housing bore + dip_tube 需匹配各 body_shape 的 neck/bore；窄口 tall_slim_vial（NECK_R=0.0052）下 dip_tube/stem 半径按 BORE_R 派生回缩（resolve 解析，不 gate 掉，保多样性）。(2) squared/faceted/tapered 瓶身内 bore 与 pump/mist dip_tube 的潜在干涉：dip_tube 半径 + 落点按 body_shape 的内 bore 截面派生（dip_tube 居中瓶轴，圆/方/棱 bore 均含轴线，安全）。(3) boston_round/tall_slim_vial 的高 body 下 closure mount 高度由 NECK_TOP 派生跟随（roller housing/overcap 行程随之）。(4) 各 closure 互斥。**无硬 gate-out**（36 组合全合法，只在 resolve 派生尺寸适配）| 无 floating / collision / 封口穿瓶壁 / dip_tube 穿底 / joint 轴或 origin 错位 |
| controlled local variation | 5 个 clamped scale，每 build 统一；neck_radius equation 驱动 collar/cap/housing bore，closure_size equation 跟随 neck | 比例变化不破坏 closure joint origin / 封口配合 / 深插语义 / 坐地 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | 封口动作 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_shape | 6 | yes | yes | 圆 extrude / 锥 loft / 方 box-shell / lathe spline / 高瘦直管 / 八棱 polygon |
| closure | 6 | yes | yes | dropper(PRIS+Z)/screw(REV+Z)/pump(PRIS−Z)/mist(PRIS−Z)/roller(REV+X+PRIS+Z 双活动件)/wand(PRIS+Z)；各 ≥1 non-fixed joint |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_shape, closure) 两轴；`palette_style` 不计入 slot_choice
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（`random.Random(seed)`），seed=0 不特殊
- `resolve_config` 各 scale clamp 到声明范围；neck_radius / closure_size 为 equation 驱动 collar/cap/housing bore；封口配合 + 身份保形不等式在 resolve 内投影 / 回缩（不留到 builder）
- compatibility matrix / gating：36 组合全合法（无硬 gate-out），窄口/高身 body 时 dip_tube/stem/closure 尺寸 + mount 高度按 body_shape 的 NECK_R/NECK_TOP/BORE_R 在 resolve 派生
- 连续 scale clamp 后不破坏 closure joint origin / 封口配合 / 深插语义 / 坐地 / 类别身份（小尺度 squat 瓶）
- 关键 joint：dropper/wand `body_to_dropper`/`body_to_wand` PRISMATIC +Z (abs(axis[2])>0.99)；screw `body_to_cap` REVOLUTE +Z；pump/mist `body_to_pump`/`body_to_actuator` PRISMATIC −Z (axis[2]<−0.99)；roller `body_to_ball` REVOLUTE +X (abs(axis[0])>0.99) + `body_to_overcap` PRISMATIC +Z（**两活动件**）
- 每个 closure emits ≥1 non-fixed joint，rest pose q=0 闭合/坐下
- captured-fit：element-scoped `allow_overlap`（dropper collar/pipette ↔ body_glass；screw cap_shell ↔ body_glass；pump/mist stem ↔ collar；roller ball ↔ housing socket + overcap ridge ↔ housing；wand cap/stem/applicator ↔ body_glass）
- body-fixed closure visual（pump_collar / crimped_collar+crimp_ridge / dip_tube / housing+retainer_tab）挂 `body`、无独立 joint、按压/拔盖时静止
- pump/mist actuator stem 轴对齐 `expect_origin_distance` xy<0.001；roller ball sphere 旋转不变量（旋转后 AABB 不动）

## Reject cases

- 用 boxy 占位体（纯 Box 无 hollow bore）当玻璃瓶 body → 失类别身份；圆 body 必须 extrude/loft/lathe，方 body 用 rect+fillet+box-shell，棱 body 用 polygon，全部带真实内 bore。
- closure joint origin 放在瓶底 / 任意点而非 neck rim / COLLAR_TOP / BALL_CZ 真实接口 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- closure 无 non-fixed joint（做成纯固定盖）→ 违反精华液瓶活动封口契约。
- closure rest pose 设成张开 / 抬起 / 拔出而非 q=0 闭合/坐下（pipette/stem 该深插、cap 该罩 neck、overcap 该罩 ball）→ current-pose 与 viewer 目检不符。
- joint 轴与可见机构不符（dropper/wand/pump/mist/overcap 必 ±Z PRISMATIC，screw 必 +Z REVOLUTE，ball 必 +X REVOLUTE）→ 机构语义错。
- pump/mist 的 collar/dip_tube 或 roller 的 housing 做成活动子件（应是 body 固定 visual，只 actuator/ball/overcap 活动）→ 静止件被错误关节化。
- dip_tube / pipette / stem 不深插瓶内（tip_z ≥ SHOULDER_TOP）或穿瓶底（tip_z<0）→ 深插语义破。
- 把瓶身做大（直径 >0.045 m 或高 >0.10 m 非 boston/vial）→ 出 serum 小型瓶语义（混入大号 `container_bottle`）。
- 给封口 captured-fit 补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + element-scoped allow_overlap。
- 把连续尺寸 / 颜色 / 材质（palette_style）当新 candidate 塞进 slot → 不是结构差异。

## 与相邻类别的边界

- 不该混入：**container_bottle 通用细颈液体瓶 / 酒瓶**——理由：那是更大、更长颈、封口家族更宽的手持瓶；serum 瓶是小尺度（盖 ~0.02 m）精华液专用，封口偏 dropper/roller/wand 等专属机构。
- 不该混入：**container_jar 宽口带盖储物罐**——理由：jar 口径≈瓶身、以旋盖为主；serum 瓶有明显窄颈 + 滴管/泵/喷雾/滚珠等小型分配封口。
- 不该混入：**container_glass_bottle 通用玻璃瓶**——理由：那个不限精华液小型封口语义；serum 瓶身份锚点是小尺度 + 精华液专属封口 + label band + 琥珀/磨砂玻璃外观。
- 不该混入：**container_cosmetic / container_lipstick / container_dispenser / container_pump**——理由：本模板封口轴已涵盖 dropper/screw/pump/mist/roller/wand 六族精华液封口；若上游另有独立大类，分流到对应 slug，本 slug 保持精华液小瓶。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 11 个 5★ 全文读取（1 parent + 5 body 轴 + 5 closure 轴 single-axis fork pool）。6 body_shape × 6 closure = 36 combos，远超。closure 轴含 4 类 joint 拓扑（PRIS+Z 单刚体 / REV+Z / PRIS−Z+body-fixed-collar / REV+X+PRIS+Z 双活动件 roller）。palette_style **10 coordinated colorways**（amber_apothecary/clear_minimal/frosted_white/cobalt_blue/green_glass/opaque_white + soft_touch_black/gold_luxe/pearlescent_blush/matte_sage），每 colorway 给 body/closure_cap/collar_accent/label 四组件配色 + 一列**显式 finish**（gloss_glass/frosted_glass/opaque_matte/soft_touch/metallic/pearlescent）；锚定全样本 amber/white_plastic/clear/steel_ball/cap_gray/pump_grey 5★ rgba + 结构无关推断配色，玻璃系带真实 alpha、金属盖非霓虹。无 multiplicity 轴（rib/crimp/tab 计数是 mesh 细节非模板轴）。每候选 model.py:Lx-Ly 均来自实读样本。|

## 模板实现备注（可选）

- 共享 helper：`_body_glass_mesh(body_shape, dims)` 分派到圆 extrude / 锥 loft / 方 box-shell / lathe spline / 八棱 polygon 五种发射路径（squared 需 `_rounded_rect_solid`、boston 需 catmull-rom + `LatheGeometry.from_shell_profiles`、faceted 需 `polygon`）；`_label_band_mesh(body_shape)` 跟随截面；`_collar_mesh(neck_r, bore)` 给 dropper/pump/mist 公用。
- 单刚体封口（dropper / wand）：一个 child part 内 union collar/cap + bulb/stem + pipette/applicator，单 PRISMATIC +Z joint origin (0,0,0)。
- body-fixed 封口（pump / mist / roller）：collar/housing + dip_tube/retainer_tab 是 `body` 的 fixed visual（按压/拔盖时静止）；只 actuator/ball/overcap 是活动 child。roller 是唯一 2 活动 child（ball REVOLUTE +X + overcap PRISMATIC +Z）。
- captured-fit overlap：`run_container_bottle_serum_tests` 里按 closure 分支声明 element-scoped `allow_overlap`（dropper collar/pipette↔body_glass；screw cap_shell↔body_glass；pump/mist stem↔collar；roller ball↔housing socket + overcap ridge↔housing；wand cap/stem/applicator↔body_glass）+ `expect_overlap`/`expect_contact`/`expect_within`/`expect_origin_distance` 镜像各源 run_tests。
- neck_radius equation：`resolve_config` 派生 `collar_bore_R = NECK_R + clearance`、`housing_bore_R = NECK_R`、`cap_skirt_R/closure_outer = f(neck, closure_size)`，封口配合不等式在 resolve 投影。
- 参考模板：`container_jar`（已实现的同大类 parallel_children：body mesh 属性 + closure parallel child + element-scoped grandfather + captured-fit allow_overlap 骨架）；`container_bottle`（dropper/pump/screw closure 词汇 + neck datum）；`shopping_bucket`（多 lid 机构分支 + captured-pin allow_overlap）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B | round_cylinder + dropper_prismatic | rec_small-amber-glass-serum-bottle-with-a-white-rubb_...98768519 | `_body_glass_mesh` L58-L97 / `label_band` L133-L140 / `dropper`(collar+bulb+pipette) L149-L182 / `body_to_dropper` PRISMATIC +Z L184-L197 | 圆筒 body 基线 + 滴管封口基线 + neck datum |
| S2 | A | tapered_cone | rec_container_bottle_serum_var_tapered_body | `_body_glass_mesh` L68-L109 / `_body_radius` L62-L65 / `_label_mesh` L112-L135 | 锥形收腰 body |
| S3 | A | squared_faceted | rec_container_bottle_serum_var_squared_body | `_body_glass_mesh` L76-L129 / `_rounded_rect_solid` L64-L73 / `_label_band_mesh` L132-L143 | 方截面 box-shell body |
| S4 | A | boston_round | rec_container_bottle_serum_var_boston_round_body | `_body_glass_mesh` L116-L127 / `_outer_profile` L72-L92 / `_inner_profile` L95-L113（lathe spline）| 鼓肩收腰 lathe body |
| S5 | A | tall_slim_vial | rec_container_bottle_serum_var_tall_slim_vial | `_body_glass_mesh` L61-L113（高瘦直管 + base_round）| 安瓿/试管式高瘦 body |
| S6 | A | faceted_prism | rec_container_bottle_serum_var_faceted_prism | `_body_glass_mesh` L78-L126 / `_polygon_profile` L73-L75 / `_label_band_mesh` L129-L144 | 八棱柱 polygon body |
| S7 | B | screw_cap_revolute | rec_container_bottle_serum_var_screw_cap | `cap`(`_cap_shell_mesh` L100-L121 + rib loop N=24 L172-L183) / `body_to_cap` REVOLUTE +Z L192-L205 | 旋盖封口（REVOLUTE +Z）|
| S8 | B | pump_dispenser_prismatic | rec_container_bottle_serum_var_pump_dispenser | body-fixed `pump_collar`(`_collar_mesh` L112-L139)+`dip_tube`(`_dip_tube_mesh` L142-L162) / `pump_head`(`_pump_actuator_mesh` L165-L203) / `body_to_pump` PRISMATIC −Z L272-L285 | 乳液泵封口（PRISMATIC −Z + 固定 collar+dip_tube）|
| S9 | B | mist_sprayer_prismatic | rec_container_bottle_serum_var_mist_sprayer | body-fixed `crimped_collar`(`_collar_mesh` L124-L139)+`crimp_ridge`×12(`_crimp_ridge_mesh` L142-L154)+`dip_tube`(`_dip_tube_mesh` L157-L174) / `actuator`(`_button_mesh` L177-L184+`_nozzle_mesh` L187-L220+stem) / `body_to_actuator` PRISMATIC −Z L289-L302 | 细雾喷头封口（PRISMATIC −Z + crimp collar）|
| S10 | B | roller_ball_revolute | rec_container_bottle_serum_var_roller_ball | body-fixed `housing`(`_housing_mesh` socket L120-L157)+`retainer_tab`×3(`_retainer_tab_mesh` L160-L167) / `roller_ball`(Sphere) L257-L268 / `overcap`(`_overcap_mesh` L170-L197) L271-L277 / `body_to_ball` REVOLUTE +X L284-L297 / `body_to_overcap` PRISMATIC +Z L302-L315 | 滚珠涂抹封口（REVOLUTE +X + PRISMATIC +Z 双活动件）|
| S11 | B | brush_wand_prismatic | rec_container_bottle_serum_var_brush_wand | `wand`(`_cap_shell_mesh` L103-L143+stem L207-L212+`_applicator_tip_mesh` L146-L165) L197-L225 / `body_to_wand` PRISMATIC +Z L227-L240 | 刷棒/棒头封口（PRISMATIC +Z 单刚体）|
