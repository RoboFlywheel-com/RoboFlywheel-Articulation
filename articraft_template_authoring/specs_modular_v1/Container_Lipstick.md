# container_lipstick (twist-up bullet lipstick / lip-gloss tube) — Modular Spec

> 来源小类：`picture/Container/Lipstick`（articraft_data 上游 Container/Lipstick fork-variant pool）。
> 引用 `model.py:Lx-Ly` 来自各样本 `data/records/<id>/revisions/rev_000001/model.py`（本仓 `arti-template/data/records`，与 articraft_data 同源镜像），以 part/joint/helper **名字** 为准（`tube_base` / `cap` / `bullet_carrier` / `bullet` / `slider` / `_tube_base_solid` / `_octa_prism` / `_squircle_prism` / `_waisted_body_mesh` / `_bullet_cup_solid` / `_bullet_red_solid` / `_wand_mesh` / `_tip_mesh` / `_slider_solid` / `_external_thread_ridges` / `_internal_thread_ridges` / `hinge_lug` / `hinge_knuckle` / `bullet_twist` / `bullet_rise` / `cap_pull` / `tube_to_cap` / `slider_push` / `cap_screw` / `cap_flip`），行号仅作定位（已逐文件实读核对）。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_lipstick` |
| template path | `agent/templates/Container_Lipstick.py` |
| test path (optional) | `tests/agent/test_container_lipstick_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots: body_form + dispense_mech + cap_closure；cap 与出膏机构都挂到 tube_base 共同 root，无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7（2 parent + 5 `rec_container_lipstick_var_*` fork 变体）|
| read_count | 7（全文实读，无抽样）|
| read_scope | all 5-star samples in this category（2 parent + square_rounded / tapered_waisted / push_up_swivel_pot / screw_thread_twist_off / hinged_flip_cap）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14 |

逐样本结构摘要（全部实读）：
- **parent A 口红**（`rec_lipstick-...-twist-up_...d2d2bc8b`）：圆直筒 `tube_base`（`_tube_base_solid` L46-60，circle.extrude 中空开口）+ 银 `center_band` L119-124；`cap` 直拔摩擦盖（`cap_pull` PRISMATIC +Z L155-163）；twist-up 链 = massless `bullet_carrier`（`bullet_twist` CONTINUOUS +Z L168-176）→ `bullet`（`bullet_rise` PRISMATIC +Z L202-210），红膏斜切头（`_bullet_red_solid` L74-100），银 carrier cup（`_bullet_cup_solid` L63-71），off-axis `twist_marker` L191-196。**4 part / 3 joint**。
- **parent B 唇釉**（`rec_lip-gloss-...-applicato_...86a4438e`）：八边棱柱 `tube`（`_octa_prism` L48-63 + `_tube_body_mesh` L66-87）+ 透明 `clear_base` + 粉 `gloss`（`_gloss_mesh` L102-117）；`cap_applicator`（帽+杆+软头一体刚体）经 `tube_to_cap` PRISMATIC +Z 直抽（L199-210）；doe-foot 细杆 `_wand_mesh` L135-150 + 软头 `_tip_mesh` L153-165。**2 part / 1 joint**。
- **var square_rounded**：squircle 截面 body（`_squircle_prism` L59-70 / `_squircle_tube` L73-86 / `_tube_base_solid` L89-91，`rect.fillet("|Z")`）；机构同 parent A（twist-up + pull-off）；新增 4 条 `guide_rib_*` 在 squircle bore 内滑配 L219-233。
- **var tapered_waisted**：收腰沙漏 body 用 SDK `LatheGeometry`（`_waisted_body_mesh` L59-94，Catmull-Rom 平滑 (r,z) profile 绕轴）+ lathe `cap` 壳（`_waisted_cap_mesh` L97-130）；机构同 parent A。
- **var push_up_swivel_pot**：出膏机构换成单 PRISMATIC `slider`（`_slider_solid` L78-102 = cup+rib+外露 thumb tab，`slider_push` PRISMATIC +Z L205-215），**无独立旋转 carrier**（仅 2 joint：cap_pull + slider_push）；body 上 `+X` 壁开竖 slot（`_tube_base_solid` L56-75）让 thumb tab 穿出。
- **var screw_thread_twist_off**：cap 换成旋拧盖（`cap_screw` CONTINUOUS +Z L236-244），可见外螺纹 `_external_thread_ridges`（twistExtrude L92-106）+ 盖内螺纹 `_internal_thread_ridges` L124-140，窄 threaded neck（`_tube_base_solid` L66-89）；twist-up 链不变。
- **var hinged_flip_cap**：cap 换成侧翻盖（`cap_flip` REVOLUTE axis=(1,0,0) origin=后 rim L183-191），可见 `hinge_lug`（base 上 L145-150）+ `hinge_knuckle`（cap 上 L169-174）；twist-up 链不变。

冗余/分流说明：
- 全部 7 样本共享同一根 spine（tube 沿 +Z 立地 z=0、cap 在顶、出膏件沿 +Z 出腔）。真实结构变化收敛到三条正交轴：**body 截面**（round / octagon / squircle / waisted）、**出膏机构**（twist-up 双 joint / doe-foot 单抽 / push-up 单 slider）、**cap 机构**（pull-off PRISMATIC / screw CONTINUOUS / flip REVOLUTE）。只换颜色 / 比例 / 金银白红磨砂的差异归 palette / scale，不另列 candidate。

## 核心身份

口红 / 唇釉管（twist-up bullet lipstick tube）：一只纤细直立中空管体，中心轴沿 +Z，底坐地 z=0，居中于 (x=0,y=0)，高宽比明显细长（height ≫ 2.5·width，见 parent B run_tests L258-262）。tube_base 为 root，由 CadQuery `circle.extrude` / `rect.fillet` / SDK `LatheGeometry` 发射为薄壁中空开口管，截面可为圆直筒 / 八边棱柱 / 圆角方 squircle / 收腰沙漏。tube 上方一只 cap 按某种机构开合（**cap 活动语义之一**）：直拔摩擦盖（PRISMATIC +Z lift-off）/ 旋拧螺纹盖（CONTINUOUS +Z spin，可见内外螺纹）/ 侧翻铰链盖（REVOLUTE 绕后 rim +X 翻起）。tube 内一套**出膏 / 涂抹机构**（**主类别身份动作**）：旋升红膏弹头（massless `bullet_carrier` CONTINUOUS 旋 + `bullet` PRISMATIC 升的解耦螺旋链，斜切红膏头）/ doe-foot 涂抹杆（帽身一体刚体 PRISMATIC 直抽，软头浸 gloss 蓄液）/ 拇轮直推滑块（单 PRISMATIC slider，外露 thumb tab 穿 body 壁竖 slot）。中段银 `center_band`（固定 visual，分模线处）。默认成熟域：单管单盖单出膏件（无嵌套 / 无 multiplicity）。

不该混入：化妆盘 / 膏霜罐（palette/jar，是 `container_cosmetic`——宽口翻盖盘或矮胖旋盖罐，无内部上升弹头机构）、精华 / 滴管瓶（dropper/pump，是 `container_bottle_serum`——细颈瓶 + 滴管或泵头吸液，非红膏弹头）、宽口带盖储物 / 化妆罐（lidded jar，是 `container_jar`——矮胖宽口、盖罩 neck，无 twist-up bullet）。

## 槽位 + 候选模块表

> **建模注记**：`body_form` 是 root `tube_base` 的 mesh 属性（一次 `_body_mesh(body_form)` 发射薄壁开口管 + 可选 center_band/neck），不是独立串联 slot。`dispense_mech`（出膏件）与 `cap_closure`（盖）各自挂到 tube_base（parallel children）。三轴笛卡尔积构成拓扑多样性（见 §9）。识别要点：twist-up 出膏是 CONTINUOUS（旋）+ PRISMATIC（升）经 massless carrier 的双 joint 解耦链；push-up 是单 PRISMATIC；doe-foot 是帽身一体的单 PRISMATIC 抽出。

### Slot A：body_form（管体截面 / 轮廓家族——root tube_base 的 mesh）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_cylinder（基线）| rec_lipstick-...-twist-up_...d2d2bc8b（parent A）| `_tube_base_solid` L46-60（circle.extrude outer − bore，留薄 floor，开口顶）| eligible if compatible | 直筒圆柱体，恒定半径，cq circle 拉伸中空开口管 |
| octagon_faceted | rec_lip-gloss-...-applicato_...86a4438e（parent B）| `_octa_prism` L48-63（apothem→circumradius 8-gon polyline）+ `_tube_body_mesh` L66-87（八边 body + 圆 neck + 中空 bore + fillet("|Z")）| eligible if compatible | 正八边形棱柱体，刻面 body + 圆 threaded neck |
| square_rounded | rec_container_lipstick_var_square_rounded | `_squircle_prism` L59-70（rect.extrude + edges("|Z").fillet）+ `_squircle_tube` L73-86 + `_tube_base_solid` L89-91 | eligible if compatible | 圆角方形 squircle 截面棱柱，base+cap 同截面 |
| tapered_waisted | rec_container_lipstick_var_tapered_waisted | `_waisted_body_mesh` L59-94（SDK `LatheGeometry`，Catmull-Rom 平滑 (r,z) profile 绕轴 segments=48）| eligible if compatible | 收腰沙漏轮廓，中段内收（waist 0.0100）、底部外扩（base 0.0125），lathe 扫掠侧壁 |

硬约束记录：body_form 4 candidate（达 3-6 目标区间）。全部薄壁中空开口管，共享 center_band helper；只换 footprint（圆 / 八边 / 方圆 / 收腰）与发射方式（circle.extrude / polyline.extrude / rect.fillet / LatheGeometry）。八边/方圆是真实棱面拓扑差异（AABB 方形足迹，见 square run_tests L298-320）；收腰是 lathe 变半径 profile（base 宽于 top，run_tests L310-318）。

### Slot B：dispense_mech（**主出膏 / 涂抹机构槽**——类别身份动作）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| twist_up_bullet（基线）| rec_lipstick-...-twist-up_...d2d2bc8b（parent A）| massless `bullet_carrier`（`bullet_twist` CONTINUOUS +Z L168-176）→ `bullet`（`bullet_rise` PRISMATIC +Z L202-210）；`_bullet_cup_solid` L63-71 + `_bullet_red_solid` L74-100（斜切红膏头）+ `twist_marker` L191-196 | eligible if compatible | 旋升弹头：massless carrier 旋（CONTINUOUS）解耦 bullet 升（PRISMATIC），共享 +Z 轴；**2 joint + 1 massless carrier part + 1 bullet part** |
| doe_foot_applicator | rec_lip-gloss-...-applicato_...86a4438e（parent B）| `cap_applicator`（帽+杆+软头一体）经 `tube_to_cap` PRISMATIC +Z L199-210；`_wand_mesh` L135-150（细杆）+ `_tip_mesh` L153-165（doe-foot 软头）+ `_gloss_mesh` L102-117（粉 gloss 蓄液固定 visual on tube）| eligible if compatible | 帽身一体涂抹杆：单 `tube_to_cap` PRISMATIC +Z 直抽，软头浸 gloss、抽出露口；**与 cap_closure 合并为 1 part**（见兼容矩阵） |
| push_up_swivel_pot | rec_container_lipstick_var_push_up_swivel_pot | 单 `slider`（`slider_push` PRISMATIC +Z L205-215）；`_slider_solid` L78-102（cup + rib + 外露 thumb tab）+ `_bullet_red_solid` L105-128；body +X 壁竖 slot（`_tube_base_solid` L56-75）| eligible if compatible | 拇轮直推滑块：单 PRISMATIC slider（**无独立旋转 carrier**），thumb tab 穿 body 壁竖 slot 外露；**1 joint + 1 slider part** |

硬约束记录：dispense_mech 3 candidate（达下限 3，类目真实词汇上限）。含 CONTINUOUS+PRISMATIC 解耦双 joint（twist-up）/ PRISMATIC 单抽（doe-foot）/ PRISMATIC 单 slider（push-up）三种不同 joint 拓扑 + 不同 part count（2 vs 1 vs 1）。每个 candidate **≥1 non-fixed joint**（满足 ≥1 活动机构）。词汇表上限说明：口红出膏机构真实只有 twist-up / doe-foot / push-up 三族，再扩易出类目（见 §排除项）。

### Slot C：cap_closure（顶盖固定 / 开启关节）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| friction_pull_off（基线）| rec_lipstick-...-twist-up_...d2d2bc8b（+ parent B）| `cap`（`cap_pull` PRISMATIC +Z L155-163，cap_outer.cut(cap_bore) 闭顶罩壳 L134-149）[parent B：`cap_applicator` 经 `tube_to_cap` PRISMATIC +Z L199-210] | eligible if compatible | 直拔摩擦盖：单 PRISMATIC +Z（无旋转），盖罩 over rim/band，q=0 坐下 / 正 q 直抬离 |
| screw_thread_twist_off | rec_container_lipstick_var_screw_thread_twist_off | `cap`（`cap_screw` CONTINUOUS +Z L236-244）+ `_external_thread_ridges`（twistExtrude L92-106，neck 外螺纹 visual L195-199）+ `_internal_thread_ridges` L124-140（盖内螺纹 visual L219-223）+ `cap_marker` L225-230；窄 threaded neck `_tube_base_solid` L66-89 | eligible if compatible | 旋拧螺纹盖：单 CONTINUOUS +Z（绕轴旋脱），可见内外 helical 螺纹脊，窄 neck 收肩 |
| hinged_flip_cap | rec_container_lipstick_var_hinged_flip_cap | `cap`（`cap_flip` REVOLUTE axis=(1,0,0) origin=(0,-TUBE_R,BASE_TOP_Z) L183-191）+ `hinge_lug`（base 后 rim boss L145-150）+ `hinge_knuckle`（cap 上 X-轴 cyl L169-174）| eligible if compatible | 侧翻铰链盖：REVOLUTE 绕后 rim +X 轴，q=0 闭合罩 rim、正 q 上翻 ~115°（upper=2.4）；可见铰耳 + 铰节 |

硬约束记录：cap_closure 3 candidate（达下限 3）。含 PRISMATIC（pull-off）/ CONTINUOUS（screw）/ REVOLUTE +X（flip）三种不同 joint 拓扑 + 不同附件 visual（螺纹脊 / 铰耳+铰节）。每个 candidate **恰 1 non-fixed joint**。bayonet/卡扣 与 friction_pull_off 在外观与 joint 语义上区分度低，未单列（见 §排除项）。

## 槽位图（slot graph）

pattern: parallel_children（tube_base 为 root，cap 与出膏件挂到它；无 multiplicity）

```
tube_base(body_form)  [ROOT, 坐地 z=0, 轴 +Z, height ≫ 2.5·width]
   │  (+ center_band 固定 visual 在分模线 BAND_Z；screw 时 + neck_threads 固定 visual；flip 时 + hinge_lug 固定 visual)
   │
   ├── dispense_mech = twist_up_bullet:
   │     tube_base --[bullet_twist: CONTINUOUS +Z @ 内 bore 底 (0,0,0.006)]--> bullet_carrier(massless, 无 visual)
   │              bullet_carrier --[bullet_rise: PRISMATIC +Z, lower=0 upper=RISE_HEIGHT]--> bullet(carrier_cup + bullet_red 斜切头 + twist_marker)
   │
   ├── dispense_mech = doe_foot_applicator:
   │     tube_base --[tube_to_cap: PRISMATIC +Z @ (0,0,0)]--> cap_applicator(cap 壳 + wand_stem + doe_foot_tip 一体刚体)
   │              (gloss 蓄液为 tube_base 固定 visual；doe-foot tip 浸 gloss at rest)
   │              ※ doe_foot 时 cap_closure ≡ 此抽出件本身（见兼容矩阵：合并 1 part）
   │
   └── dispense_mech = push_up_swivel_pot:
         tube_base --[slider_push: PRISMATIC +Z @ (0,0,0.006)]--> slider(carrier cup + rib + 外露 thumb tab + bullet_red)
              (body +X 壁竖 slot 让 thumb tab 穿出；无独立旋转 carrier)

   并联 cap（仅 twist_up / push_up 时为独立盖件；doe_foot 时盖与出膏件合并）：
   ├── cap_closure = friction_pull_off:
   │     tube_base --[cap_pull: PRISMATIC +Z @ CAP_REST_Z(band/rim)]--> cap(cap_shell 闭顶罩壳)
   │
   ├── cap_closure = screw_thread_twist_off:
   │     tube_base --[cap_screw: CONTINUOUS +Z @ CAP_REST_Z(neck 肩)]--> cap(cap_shell + cap_threads + cap_marker)
   │     (tube_base 加 neck_threads 固定 visual；窄 threaded neck)
   │
   └── cap_closure = hinged_flip_cap:
         tube_base --[cap_flip: REVOLUTE +X @ (0,-TUBE_R,BASE_TOP_Z) 后 rim]--> cap(cap_shell + hinge_knuckle)
         (tube_base 加 hinge_lug 固定 visual 在后 rim boss)
```

接口点位与 joint 语义：
- **twist-up 接口**：`bullet_twist` origin 落在内 bore 底中心 `(0,0,0.006)`，axis +Z（CONTINUOUS）；`bullet_rise` 经 massless `bullet_carrier`（无 visual，1e-4 mass Box inertial）解耦旋转/平移共享 +Z（PRISMATIC，q=0 缩入 / 正 q 升出，upper=RISE_HEIGHT≈0.040）。
- **doe-foot 接口**：`tube_to_cap` origin 在 `(0,0,0)`，axis +Z PRISMATIC（cap+杆一体直抽，q=0 软头浸 gloss / 正 q 杆出口，upper=PULL≈0.072）。**此件同时是 cap**，因此 doe_foot 时不再发射独立 cap_closure（互斥合并，见兼容矩阵）。
- **push-up 接口**：`slider_push` origin 在 `(0,0,0.006)`，axis +Z PRISMATIC（单 slider，q=0 缩入 / 正 q 推出）；thumb tab 穿 body +X 壁竖 slot 外露（slot 在 `_tube_base_solid` 内 cut）。
- **cap 接口（独立盖件，twist_up/push_up 时）**：`cap_pull` origin 在 `(0,0,CAP_REST_Z)` band/rim 高度、+Z PRISMATIC；`cap_screw` origin 在 neck 肩高度、+Z CONTINUOUS；`cap_flip` origin 在后 rim 硬件 `(0,-TUBE_R,BASE_TOP_Z)`、+X REVOLUTE。
- **seal/visual 接口**：center_band（所有）、neck_threads（screw）、hinge_lug（flip）、gloss（doe_foot）均为固定 visual 挂 tube_base（无独立 joint）。
- **mating policy**：盖 skirt 罩 over rim/band、bullet/slider cup 缩在 bore 内、doe-foot 浸 gloss、螺纹脊互嵌、铰节裹铰耳——都是 captured / 友配（故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（落在真实 bore 底 / rim / neck 肩 / 后 rim 铰）+ element-scoped `allow_overlap` 守 overlap（见各 record run_tests 的 `ctx.allow_overlap`：parent A L254-288 / screw L351-382 / flip L310-345 / push L272-300 / gloss L223-251 / square 多 rib L323-368）。
- **rest pose**：所有 cap q=0 闭合 / 坐下 / 罩 rim；bullet/slider/doe-foot q=0 缩入腔（red bullet 隐于管、doe-foot 浸 gloss）。出膏件升出 / cap 抬升或翻起为 viewer 目检的活动语义。
- **互斥 / 可选**：dispense_mech 三候选互斥（一次只一种出膏件）；cap_closure 三候选互斥（一次只一种盖）；`bullet_carrier` massless part 仅在 twist_up 发射；**doe_foot_applicator ⇒ cap_closure 合并到该抽出件**（doe-foot 帽身一体，不再有独立盖关节）。

## 每槽位 Module Emits / Interfaces

### Slot A / tube_base（body_form，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `tube_base`（visual: 截面 mesh `tube_body` 薄壁开口管 + 银 `center_band`[ + screw 时 `neck_threads` + flip 时 `hinge_lug`]）| parent A `_tube_base_solid` L46-60 / band L119-124；gloss `_tube_body_mesh` L66-87；square `_squircle_tube` L73-91；waisted `_waisted_body_mesh` L59-94 |
| internal joints | 无（root tube 本身无活动件）| — |
| upstream interface | 坐地 z=0（root），轴 +Z，height ≫ 2.5·width | parent B run_tests L258-262 |
| downstream interface | 内 bore 底 `(0,0,0.006)`（出膏 joint parent 接口）/ band-rim `CAP_REST_Z` / neck 肩 / 后 rim `(0,-TUBE_R,BASE_TOP_Z)`（cap joint parent 接口）| parent A L173/L160；flip L188 |

### Slot B / dispense_mech（每候选发射对应出膏件）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `bullet_carrier`(massless) + `bullet`（twist_up）/ `cap_applicator`（doe_foot，与 cap 合并）/ `slider`（push_up）| parent A L166/L179；gloss L189；push L189 |
| internal joints | `bullet_twist` CONTINUOUS +Z + `bullet_rise` PRISMATIC +Z（twist_up）/ `tube_to_cap` PRISMATIC +Z（doe_foot）/ `slider_push` PRISMATIC +Z（push_up）| parent A L168-176+L202-210；gloss L199-210；push L205-215 |
| upstream interface | bore 底中心 `(0,0,0.006)`（twist/push）/ `(0,0,0)`（doe-foot）| parent A L173；push L210；gloss L207 |
| downstream interface | red bullet / doe-foot 软头从口升出（活动语义）；push 的 thumb tab 穿 body 壁竖 slot 外露 | parent A run_tests L327-342；push L352-358 |

### Slot C / cap_closure（每候选发射对应盖件；doe_foot 时与 dispense 合并）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cap`（cap_shell[ + screw 时 cap_threads + cap_marker；flip 时 hinge_knuckle]）| parent A L132-149；screw L213-235；flip L158-179 |
| internal joints | `cap_pull` PRISMATIC +Z（pull-off）/ `cap_screw` CONTINUOUS +Z（screw）/ `cap_flip` REVOLUTE +X（flip）| parent A L155-163；screw L236-244；flip L183-191 |
| upstream interface | band/rim 高 `CAP_REST_Z`（pull）/ neck 肩（screw）/ 后 rim `(0,-TUBE_R,BASE_TOP_Z)`（flip）| parent A L160；screw L241；flip L188 |
| downstream interface | 无（盖为终端件，开合即活动语义）| — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | round_cylinder / octagon_faceted / square_rounded / tapered_waisted | round_cylinder | choice | deterministic procedural sampler 选 | module table |
| dispense_mech | enum | twist_up_bullet / doe_foot_applicator / push_up_swivel_pot | twist_up_bullet | choice | sampler 选 | module table |
| cap_closure | enum | friction_pull_off / screw_thread_twist_off / hinged_flip_cap | friction_pull_off | choice | sampler 选；doe_foot 时被 dispense 合并（不独立选）| module table |
| palette_style | enum | classic_white_silver_red / gold_pink_gloss / matte_black_gunmetal / rose_gold_nude / frosted_clear_berry / pearlescent_lilac_silver / lacquer_red_gold / gunmetal_softtouch_plum / two_tone_cream_navy_coral / marble_print_mauve | classic_white_silver_red | palette | palette only（含 **finish 维度**），**不计入 slot_choice**；每 seed `rng.choice(PALETTE_STYLES)`，10 档 | palette（见下）|
| tube_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放管高 H → BASE_TOP_Z / BAND_Z / CAP_REST_Z / 出膏 RISE_HEIGHT 行程同比，clamp（保细长 h>2.5w）| parent A L31-44；resolve clamp |
| tube_radius_scale | float | [0.88, 1.12] | 1.0 | independent | 缩放管外半径 / 半宽 TUBE_R → INNER_R / CUP_R / BULLET_R 派生跟随，clamp | parent A L28-42 |
| cap_radius_scale | float | derived | 1.0 | equation | `CAP_R = (TUBE_R·tube_radius_scale) + clearance`；盖罩半径派生跟随管半径（保罩配合）| parent A L35；screw L51 |
| cap_height_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放盖高 CAP_LEN / skirt 深，clamp | parent A L36 |
| dispense_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 bullet_rise / slider_push / tube_to_cap / cap 行程 + flip limit，clamp（保升出露口 & 不超腔）| parent A L43；gloss L45 |
| (—) | constraint | — | — | inequality | 出膏件径配合：`CUP_R ≤ INNER_R − clearance` 且 `BULLET_R < INNER_R`（弹头/滑块缩在 bore 内），违反按比例回缩 radius scale | parent A L33/L40-41 |
| (—) | constraint | — | — | inequality | 盖罩配合：`cap_bore_R ≥ TUBE_R + clearance`（screw 时 ≥ neck thread outer）且 `cap_outer_R ≤ TUBE_R + proud`，违反回缩 cap/neck scale | parent A L35；screw L51-52 |
| (—) | constraint | — | — | inequality | 升出露口：`RISE_HEIGHT·dispense_travel_scale ≥ (BASE_TOP_Z − bullet_seat_z) + margin`（升满露口），不满足则提高 travel 或拒采 | parent A run_tests L338-342 |

palette_style 配色档（**10 档协调配色，含显式 finish 维度**）：每档列四组件色 + finish。组件 = **tube_base 管体 / cap 顶盖 / bullet·product 膏头(或唇釉·doe-foot 蓄液) / accent 中段 band**。`finish` 列是 palette 内显式的材质质感维度（仅描述/驱动渲染语义，**不改任何 slot / candidate / joint / 拓扑**）：`glossy_lacquer`(亮漆) / `matte`(哑光) / `metallic`(金属：gold/silver/rose_gold/gunmetal) / `pearlescent`(珠光) / `frosted_gloss`(磨砂/透明亮膏管) / `soft_touch`(软触磨砂黑) / `two_tone`(双色拼接) / `marble_print`(大理石纹印)。RGBA 锚定 5★ 源（parent A L106-109 / parent B L171-175 / push·flip gunmetal）；标 *(inferred)* 的为这些锚色插值/组合出的真实口红配色（金属不荧光、膏头取真实唇色）。

| # | colorway 名 | tube_base 管体 | cap 顶盖 | bullet / product 膏头 | accent band 中段 | finish | 锚源 |
|---|---|---|---|---|---|---|---|
| 1 | `classic_white_silver_red` | tube_white (0.93,0.93,0.94) | tube_white (0.93,0.93,0.94) | lipstick_red (0.86,0.10,0.10) | silver (0.74,0.75,0.78) | glossy_lacquer | parent A L106-109 |
| 2 | `gold_pink_gloss` | gold (0.78,0.62,0.18) | clear_base (0.86,0.88,0.90,0.32) | pink_gloss (0.93,0.55,0.66) / tip_pink (0.86,0.18,0.45) | gold (0.78,0.62,0.18) | frosted_gloss | parent B L171-175 |
| 3 | `matte_black_gunmetal` | matte_black (0.12,0.12,0.13) | matte_black (0.12,0.12,0.13) | lipstick_red (0.86,0.10,0.10) | gunmetal (0.40,0.42,0.45) | matte | push L137 / flip L128 gunmetal *(inferred 主色重配)* |
| 4 | `rose_gold_nude` | rose_gold (0.80,0.55,0.50) | rose_gold (0.80,0.55,0.50) | nude (0.78,0.52,0.45) | silver (0.74,0.75,0.78) | metallic | classic↔gold 插值 *(inferred)* |
| 5 | `frosted_clear_berry` | frosted_clear (0.88,0.88,0.90,0.55) | frosted_clear (0.88,0.88,0.90,0.55) | berry (0.55,0.10,0.25) | silver (0.74,0.75,0.78) | frosted_gloss | clear_base 透明档 + 深莓红 *(inferred)* |
| 6 | `pearlescent_lilac_silver` | pearl_lilac (0.86,0.82,0.90) | pearl_lilac (0.86,0.82,0.90) | mauve_pink (0.80,0.45,0.55) | silver (0.74,0.75,0.78) | pearlescent | tube_white↔silver 偏冷紫珠光 *(inferred)* |
| 7 | `lacquer_red_gold` | lacquer_red (0.72,0.08,0.12) | lacquer_red (0.72,0.08,0.12) | classic_red (0.86,0.10,0.10) | gold (0.78,0.62,0.18) | glossy_lacquer | lipstick_red + gold 锚 *(inferred 深酒红漆)* |
| 8 | `gunmetal_softtouch_plum` | soft_black (0.14,0.14,0.16) | gunmetal (0.32,0.33,0.36) | plum (0.45,0.12,0.28) | gunmetal (0.40,0.42,0.45) | soft_touch | flip L128 (0.32,0.33,0.36) + push L137 gunmetal *(inferred)* |
| 9 | `two_tone_cream_navy_coral` | cream (0.95,0.92,0.84) | navy (0.13,0.18,0.34) | coral (0.90,0.38,0.34) | gold (0.78,0.62,0.18) | two_tone | cream 管 + navy 盖双色拼接 *(inferred)* |
| 10 | `marble_print_mauve` | marble_white (0.90,0.89,0.88) + grey_vein (0.55,0.55,0.58) | silver (0.74,0.75,0.78) | mauve_rose (0.72,0.40,0.48) | silver (0.74,0.75,0.78) | marble_print | tube_white + silver 灰纹 *(inferred 大理石印)* |

finish 维度说明：finish 是 palette_style **档内的固定属性**（每档绑定一种 finish），不是独立采样轴——`rng.choice(PALETTE_STYLES)` 选档即同时定四色 + finish。finish 仅影响材质渲染语义（哑光/亮漆/珠光/磨砂透明/软触/双色/大理石纹），不增删 part / joint，不改 body_form / dispense_mech / cap_closure，故仍是纯 palette。doe_foot 分支下「bullet/product」槽对应唇釉膏体(gloss)＋tip 软头色，「cap」槽对应合并抽出件外壳色（取该档 cap 色）。frosted_gloss / 透明档保留 alpha<1（如 clear_base 0.32 / frosted 0.55），其余 finish alpha=1.0。所有膏头取真实唇色域（红/莓/裸/珊瑚/梅/紫粉），金属色不荧光。

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`cap_radius_scale` 为 equation（盖罩半径跟随管半径，保罩配合）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 body_form / dispense_mech / cap_closure 的拓扑。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（body_form + dispense_mech + cap_closure）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。单管单盖单出膏件——一支口红只有 1 个 bullet/applicator 与 1 个 cap，无同构子件 × N。（注：square_rounded 的 4 条 `guide_rib_*` 是该 body 的固定滑配 rib，属 module-local 细节，非模板级可变 multiplicity 轴。）

## 拓扑多样性审计

总组合数（含 doe_foot 合并约束）：
- 笛卡尔积上界 = body_form(4) × dispense_mech(3) × cap_closure(3) = 36。
- 兼容约束扣减：`doe_foot_applicator` 时 cap_closure 合并入抽出件（不独立选盖）⇒ doe_foot 分支组合 = body_form(4) × 1（doe_foot）× 1（cap≡抽出件）= 4。
- twist_up / push_up 分支 = body_form(4) × dispense_mech(2) × cap_closure(3) = 24。
- **合法组合合计 = 24 + 4 = 28**。

仅 body_form(4) × cap_closure(3) = **12 ≥ 10** 即已可过门控；叠 dispense_mech 后充裕（28）。

理由：拓扑多样性来源充裕——28 合法组合远超 10。三轴各自引入真实 joint 拓扑差异：dispense_mech = CONTINUOUS+PRISMATIC 解耦双 joint（twist_up，2 part）/ PRISMATIC 单抽合并件（doe_foot，1 part）/ PRISMATIC 单 slider（push_up，1 part）；cap_closure = PRISMATIC（pull-off）/ CONTINUOUS（screw + 螺纹 visual）/ REVOLUTE +X（flip + 铰耳/铰节 visual）；body_form = circle.extrude / 8-gon polyline / squircle rect.fillet / LatheGeometry 四种截面发射。这些是 part tree / joint type / part count 的真实结构差异，非尺寸装饰。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` body_form，再 `rng.choice` dispense_mech；若 dispense_mech=doe_foot_applicator 则 cap_closure 由兼容矩阵锁为 `merged_into_dispense`（不再独立 `rng.choice`），否则 `rng.choice` cap_closure；再 uniform 各连续 scale + `rng.choice` palette_style。compatibility matrix 排除非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 28（28 合法组合即该类目合理上限，受真实词汇表约束）。低于 300 的原因：口红真实结构词汇就是 4 body × 3 dispense × 3 cap（含 doe_foot 合并）= 28，body 截面再扩（三角 / 心形）易出类目或失真、出膏机构超出 twist-up/doe-foot/push-up 三种无真实形态、cap 的 bayonet/卡扣与 pull-off 区分度低（见 §排除项），是该小类的合理上限，不强行注水。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 5 个 scale（tube_height / tube_radius / cap_radius(equation) / cap_height / dispense_travel）。全部 `resolve_config` clamp + 每 build 统一应用。`cap_radius_scale` 为 equation（盖罩半径派生跟随管半径）。出膏件径配合 / 盖罩配合 / 升出露口三条不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏出膏 joint origin（bore 底）、cap joint origin（band-rim / neck 肩 / 后 rim 铰）、罩配合、细长高宽比或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` body_form → dispense_mech；doe_foot 时 cap 锁 merged，否则 `rng.choice` cap_closure；再 uniform 各 scale + `rng.choice` palette_style | slot_choices_for_seed 含三轴且与 build 一致 |
| compatibility matrix | (1) `doe_foot_applicator` ⇒ cap_closure=`merged_into_dispense`（doe-foot 帽身一体，不发独立盖关节），不与 pull/screw/flip 组合。(2) `screw_thread_twist_off` 需窄 threaded neck → 与任意 body_form 兼容（neck 在 resolve 派生收肩，棱面 body 用圆 neck）。(3) `hinged_flip_cap` 需后 rim hinge_lug → 与任意 body_form 兼容（lug 挂 root rim）。(4) `push_up_swivel_pot` 需 body 壁竖 slot → 在 `_body_mesh` cut（任意 body_form 适配）。(5) twist_up/push_up 出膏件与 cap 三候选正交（共 24）。无其他硬 gate-out（28 组合全合法，只在 resolve 派生尺寸适配）| 无 floating / collision / 弹头穿壁 / cap 穿管 / joint 轴或 origin 错位 |
| controlled local variation | 5 个 clamped scale，每 build 统一；cap_radius equation 驱动盖 bore；出膏件径/盖罩/升出三不等式回缩 | 比例变化不破坏出膏/盖 joint origin / 罩配合 / 坐地 / 细长比 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | 出膏升出 / cap 开合 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 4 | yes | yes | circle / 8-gon / squircle / lathe-waisted 四截面族 |
| dispense_mech | 3 | yes | yes | twist_up(CONT+PRIS,2part) / doe_foot(PRIS,合并) / push_up(PRIS,1part) |
| cap_closure | 3 | yes | yes | pull-off(PRIS) / screw(CONT+螺纹) / flip(REV X+铰耳) |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_form, dispense_mech, cap_closure) 三轴；doe_foot 时 cap_closure 报 `merged_into_dispense`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling；seed=0 不特殊
- `resolve_config` 各 scale clamp 到声明范围；cap_radius equation 驱动盖 bore；出膏件径/盖罩/升出三不等式在 resolve 内投影 / 回缩
- compatibility matrix / gating：28 合法组合（doe_foot⇒cap 合并，其余正交，无硬 gate-out）；screw neck / flip lug / push slot 在 resolve 按 body_form 派生
- 连续 scale clamp 后不破坏出膏/盖 joint origin / 罩配合 / 坐地 / 细长高宽比 / 类别身份
- 关键 joint：twist_up `bullet_twist` CONTINUOUS +Z (abs(axis[2])>0.99) + `bullet_rise` PRISMATIC +Z + massless `bullet_carrier`（无 visual）；doe_foot `tube_to_cap` PRISMATIC +Z（帽身一体合并件）；push_up `slider_push` PRISMATIC +Z（单 slider，2 总 joint）；pull-off `cap_pull` PRISMATIC +Z；screw `cap_screw` CONTINUOUS +Z + 内外螺纹 visual；flip `cap_flip` REVOLUTE +X (abs(axis[0])>0.9) origin 后 rim + hinge_lug/hinge_knuckle visual
- captured-fit：element-scoped `allow_overlap`（cap_shell↔tube_body / cap_shell↔center_band 罩；carrier_cup/bullet_red↔tube_body 缩入 bore；doe_foot_tip↔gloss 浸；cap_threads↔neck_threads 螺纹互嵌；hinge_knuckle↔hinge_lug 铰裹；guide_rib_*↔tube_body 滑配；slider_body↔tube_body 穿 slot）
- grandfather：所有 captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守
- rest pose：cap q=0 闭合 / 罩 rim；出膏件 q=0 缩入腔（red bullet 隐于管 / doe-foot 浸 gloss）

## Reject cases

- 用 boxy 占位体（纯 Box）当圆管 body → 失类别身份；圆 body 必须 circle.extrude / LatheGeometry，方圆 body 用 rect.fillet("|Z")，八边用 polyline。
- 出膏 / cap joint origin 放在管底 / 任意点而非 bore 底 (0,0,0.006) / band-rim / neck 肩 / 后 rim 真实硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- twist_up 出膏不用 massless carrier 解耦 rotate/rise，把 CONTINUOUS+PRISMATIC 串到 bullet 单 part → 旋转与升出耦合错误（应 tube_base→carrier→bullet 两 joint）。
- doe_foot 还额外发独立 cap_closure（pull/screw/flip）→ 帽身一体已是盖，重复盖件穿模；doe_foot 必须把 cap 合并入抽出件。
- 出膏件 / cap rest pose 设成升出 / 抬起 / 翻开而非 q=0 缩入闭合 → current-pose 与 viewer 目检不符（red bullet 应隐于管、cap 应罩 rim）。
- 弹头/滑块/盖罩 半径未守不等式（CUP_R 超 INNER_R / cap_bore 小于 TUBE_R）→ 穿壁或盖卡不上，clearance FAIL。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice）。
- 管体做成矮胖宽口（h < 2.5·w）→ 失口红细长身份，落入 jar/cosmetic 类目。
- 给 captured-fit（罩/嵌/浸/铰）补 MatingContract 硬对接 → 配合几何对不上 mating-gap FAIL；应 grandfather + allow_overlap。

## 与相邻类别的边界

- 不该混入：**container_cosmetic 化妆盘 / 膏霜罐**（palette/jar）——理由：cosmetic 是宽口翻盖盘或矮胖旋盖膏罐，内无上升红膏弹头 / 涂抹杆机构；口红的类别身份是细长管 + 内部 twist-up/push-up/doe-foot 出膏件。
- 不该混入：**container_bottle_serum 精华 / 滴管瓶**（dropper/pump）——理由：serum 是细颈瓶 + 滴管吸液或泵头压送液体，机构是吸/压而非红膏弹头升出；二者虽都细长，但出料件拓扑不同（滴管/泵 vs bullet/slider）。
- 不该混入：**container_jar 宽口带盖罐**——理由：jar 矮胖宽口、盖罩 neck、无 twist-up bullet；口红是细长管 + 升出弹头。
- 不该混入：**container_tube 软管 / 挤压管**——理由：tube 是软体挤压出料（无刚性升降机构），口红是刚性 twist-up/push-up 弹头 + 硬盖。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY draft。7 个 5★ 全读（2 parent + 5 var）。4 body × 3 dispense × 3 cap，doe_foot⇒cap 合并 ⇒ 28 合法组合；body×cap=12 即过 。三轴各引入真实 joint 拓扑（twist=CONT+PRIS 解耦双 joint+massless carrier、push=单 PRIS slider、doe_foot=帽身一体单抽合并、pull=PRIS、screw=CONT+螺纹、flip=REV X+铰耳）。palette_style **10 档协调配色 + 显式 finish 维度**（每档 tube/cap/bullet·product/accent 四组件色 + 一种 finish：glossy_lacquer / matte / metallic / pearlescent / frosted_gloss / soft_touch / two_tone / marble_print）；前 5 档锚 5★ 源色保留，后 5 档为锚色插值/组合的真实口红配色（金属不荧光、膏头取真实唇色）。finish 为档内固定属性，仍纯 palette（不计 slot_choice、不改任何 slot/candidate/joint/拓扑）。无 multiplicity 轴。待人工审核。|

## 模板实现备注（可选）

- 共享 helper：`_round_body` / `_octa_body(_octa_prism)` / `_squircle_body(_squircle_prism)` / `_waisted_body(LatheGeometry)` 四 body 发射器 + `_center_band` + `_bullet_red_solid`（斜切红膏头，twist/push 共用）+ `_neck_with_threads`（screw）+ `_hinge_lug/knuckle`（flip）。圆/收腰用 `mesh_from_cadquery`/`mesh_from_geometry`，方圆用 `rect.fillet("|Z")`，八边用 polyline.extrude。
- twist_up：必须经 massless `bullet_carrier`（无 visual，1e-4 mass Box inertial）解耦 `bullet_twist`(CONTINUOUS +Z)→`bullet_rise`(PRISMATIC +Z)；push_up 用单 `slider_push`(PRISMATIC) 不要 carrier（仅 2 总 joint：cap + slider）。
- doe_foot 合并：`cap_applicator` 一个 part 同时充当 cap_closure 与 dispense_mech，单 `tube_to_cap` PRISMATIC；此分支不发 cap_pull/screw/flip。
- captured-fit overlap：`run_container_lipstick_tests` 复刻各 record 的 `ctx.allow_overlap`（cap_shell↔tube_body/center_band、carrier_cup/bullet_red↔tube_body、doe_foot_tip↔gloss、cap_threads↔neck_threads、hinge_knuckle↔hinge_lug、guide_rib_*↔tube_body、slider_body↔tube_body+slot）。
- cap_radius equation：`resolve_config` 派生 `cap_bore_R = TUBE_R + clearance`（screw 时 ≥ neck thread outer）、`cap_outer_R = TUBE_R + proud`；出膏件径/升出不等式在 resolve 投影。
- 参考模板：`agent/templates/Container_Jar.py`（同 parallel_children + 多 cap 机构分支 + massless carrier 解耦 + element-scoped allow_overlap grandfather 骨架）；`agent/templates/Chair_Folding_chair.py`（Config/ResolvedConfig + config_from_seed + resolve_config clamp + slot_choices_for_config）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | round_cylinder + twist_up_bullet + friction_pull_off | rec_lipstick-...-twist-up_...d2d2bc8b（parent A）| `_tube_base_solid` L46-60 / `center_band` L119-124 / `bullet_twist` L168-176 / `bullet_rise` L202-210 / `_bullet_red_solid` L74-100 / `cap_pull` L155-163 | 圆管 body 基线 + twist-up 解耦双 joint + massless carrier + 直拔盖 |
| S2 | A/B/C | octagon_faceted + doe_foot_applicator + (merged cap) | rec_lip-gloss-...-applicato_...86a4438e（parent B）| `_octa_prism` L48-63 / `_tube_body_mesh` L66-87 / `_wand_mesh` L135-150 / `_tip_mesh` L153-165 / `_gloss_mesh` L102-117 / `tube_to_cap` L199-210 | 八边棱柱 body + doe-foot 涂抹杆（帽身一体合并盖）+ gloss 蓄液 |
| S3 | A | square_rounded | rec_container_lipstick_var_square_rounded | `_squircle_prism` L59-70 / `_squircle_tube` L73-86 / `_tube_base_solid` L89-91 / guide_rib L219-233 | 圆角方 squircle 截面 body + 滑配 rib |
| S4 | A | tapered_waisted | rec_container_lipstick_var_tapered_waisted | `_waisted_body_mesh` L59-94（LatheGeometry）/ `_waisted_cap_mesh` L97-130 | 收腰沙漏 lathe body |
| S5 | B | push_up_swivel_pot | rec_container_lipstick_var_push_up_swivel_pot | `_slider_solid` L78-102 / `slider_push` L205-215 / body slot `_tube_base_solid` L56-75 | 单 PRISMATIC slider 推膏 + 外露 thumb tab + 壁竖 slot |
| S6 | C | screw_thread_twist_off | rec_container_lipstick_var_screw_thread_twist_off | `cap_screw` CONTINUOUS L236-244 / `_external_thread_ridges` L92-106 / `_internal_thread_ridges` L124-140 / neck `_tube_base_solid` L66-89 | 旋拧螺纹盖 + 内外 helical 螺纹脊 + 窄 neck |
| S7 | C | hinged_flip_cap | rec_container_lipstick_var_hinged_flip_cap | `cap_flip` REVOLUTE +X L183-191 / `hinge_lug` L145-150 / `hinge_knuckle` L169-174 | 侧翻铰链盖 + 铰耳 + 铰节 |
</content>
</invoke>
