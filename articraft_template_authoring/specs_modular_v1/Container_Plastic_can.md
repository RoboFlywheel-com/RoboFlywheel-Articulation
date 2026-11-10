# Container / Plastic can (HDPE jerrycan / fuel jug / utility canister) — Modular Spec

> 来源小类：`picture/Container/Plastic can`（articraft_data 上游 Container/Plastic can fork-variant pool）。
> source map：`articraft_data/picture_expansion/template_source_maps/Container__Plastic_can.md`。
> 本 spec 逐一**全文读取**了全部 8 个源 record 的 `model.py`（4 parents + 4 forked variants），不抽样。
> 引用 `model.py:Lx-Ly` 来自各样本 arti-template 当前 `data/records/<id>/revisions/rev_000001/model.py`；以 part / joint / helper **名字** 为准
> （`_body_solid` / `_rrect_loft` / `_loft_rrects` / `_bottle_body` / `_left_wedge_cutter` / `_handle_solid` / `grip_hole` / `bar` / `tunnel` /
> `_rounded_slot_cutter` / `_bail_mesh` / `bail_swing` / `grip_pocket scoop` / `_closure_base_solid` / `_lid_solid` / `lid_hinge` /
> `_flip_cap_solid` / `cap_hinge` / `cap_carrier` / `cap_rotate` / `cap_slide` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `container_plastic_can` |
| template path | `agent/templates/Container_Plastic_can.py` |
| test path (optional) | `tests/agent/test_container_plastic_can_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots: body_form + handle_grip + cap_closure；handle / closure 子件挂到 can `body` 共同 root，无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（4 parents + 4 forked converged variants）|
| read_count | 8（全文逐一读取，无抽样）|
| read_scope | all source records in this 小类: 4 parents（gallon-jug `0f3f18ac` / oil-jug `47fb268a` / square-jerrycan `1078fc9e` / sloped-jerrycan `ab019c96`）+ 4 variants（`swing_bail` / `recessed_grip_pocket` / `flip_top_spout` / `hinged_tethered_lid`）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 slot 表与 §14 |

冗余/分流说明：
- 4 parents 共享同一核心 kinematics：`body`(root) 携带 massless `cap_carrier`（`cap_rotate` CONTINUOUS +Z @ neck）+ `cap`（`cap_slide` PRISMATIC +Z），即每个 parent 都有 decoupled screw cap。结构词汇分三独立轴：body 足迹/形态(A)、handle/grip 机构(B)、cap/closure 机构(C)。
- parent 001（gallon-jug）与 parent 002（oil-jug）都是 "tall rounded-rect" body 家族，但 002 是 full-width 肩 slab（无 draw-in deck，承 flush D-grip）vs 001 收肩 small deck（承 raised loop）。两者 body **建模 helper 不同**（`_rrect_loft` rect-loft vs `_loft_rrects` rounded-rect polyline loft），故分别保留为 A 的两个 candidate（共 4 个 A，含两族 tall_rounded_rect 变体），但保守计 3 distinct shape 家族（rounded_rect / square_cubic / tall_rectangular_sloped）已足够（见 §9）。
- 4 variants 只换 handle 或 closure 单轴（body 不变），归并入对应 slot：`swing_bail`/`recessed_grip_pocket` → handle_grip；`flip_top_spout`/`hinged_tethered_lid` → cap_closure。

## 核心身份

塑料（HDPE）jerrycan / fuel jug / utility canister：一只直立中空吹塑罐体，中心轴/足迹沿 +Z，底坐地 z=0，足迹居中于 (x=0,y=0)。罐体由 CadQuery `loft`（圆角矩形截面堆叠）/ `box+fillet+shell` 发射为**厚壁中空 shell**（真实 hollow 内腔 + 通到内腔的 pour-mouth bore），形态可为：高瘦圆角矩形吹塑 jug（gallon / oil，taller-than-wide，收肩 small deck 或 full-width 肩 slab）/ 近立方 chunky 方 pail（square_cubic，圆角竖棱 + 凹 recessed deck）/ 高矩形 jerrycan（斜肩 peaked plateau）。罐肩上偏置一只**短螺纹 neck**（boss + neck stub），neck 上方一只盖/closure 按某机构开合（**主活动语义**）。一只**集成 handle/grip**（loop / D-grip / strap / slot / bail / pocket）让人提携。默认成熟域：单罐 + 单 handle + 单 closure（无嵌套 / 无 multiplicity）。

身份关键词：**molded HDPE body + 集成 handle + 螺纹 cap/spout**，工业/家用油料/水/化学品容器。形态 chunky、厚壁、有 molded ribs / foot / groove 细节、offset neck（偏置而非居中），handle 是 jerrycan 类别身份的强标志。

不该混入：金属罐头 tin（`container_can`，金属薄壁、易拉环 / 卷边，无 molded handle，无 screw neck）、洗衣液瓶（`container_laundry_detergent_bottle`，单握把 + 大泵/翻盖量杯盖，瓶身更修长 + 单独握把柄）、泵式分液器 / 喷雾（`container_dispenser` / 喷头泵机构，按压泵/喷嘴而非 screw cap + handle）、细颈高瓶 / 酒瓶（`container_bottle`，细长瓶身长颈，无 handle）。

## 槽位 + 候选模块表

> **建模注记**：`body_form` 是 can `body`（root）的 mesh + neck 属性（一次发射 hollow shell + offset neck stub + pour-mouth bore + molded 细节），不是独立串联 slot。`handle_grip` 与 `cap_closure` 各自挂到 `body`（parallel children；handle 多为 body 上的 fixed cut/union visual，bail 例外是 REVOLUTE 活动件；closure 总含 ≥1 活动 joint）。三轴笛卡尔积构成拓扑多样性（见 §9）。

### Slot A：body_form（罐体形态 / 足迹——root `body` 的 mesh + offset neck）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| tall_rounded_rect_deck（基线）| rec_white-plastic-gallon-jug-..._0f3f18ac（parent 001）| `_rrect_loft` L78-90 + `_body_solid` L93-149（outer/inner rrect-loft + 收肩 small deck + offset `neck` loft + `neck_bore`）| eligible if compatible | 高瘦圆角矩形吹塑 jug（taller-than-wide），收肩 tapered shoulder → small top deck，厚壁 hollow shell + through pour-mouth；offset neck 近中线 |
| tall_rounded_rect_slab | rec_gold-plastic-engine-oil-jug-..._47fb268a（parent 002）| `_rrect_pts` L54-68 + `_loft_rrects` L71-81 + `_bottle_body` L84-130 + `_neck` L133-151 | eligible if compatible | 高瘦圆角矩形 4L oil jug，full-width 肩 slab（无 draw-in deck），`base_recess` ring foot + 深 `mouth` bore；offset neck 在角部 |
| square_cubic | rec_black-plastic-square-jerrycan-..._1078fc9e（parent 003）| `_body_solid` L57-175（`box`+`fillet("|Z",R)` chunky 方体 + inset `shoulder` slab + 凹 `pocket` recessed deck + `boss`/`neck` + `bore` + stacking `ridge` + `foot`）| eligible if compatible | 近立方 chunky 方 pail，圆角竖棱（filleted vertical edges），recessed 顶 deck，molded stacking ribs + flared foot；offset round neck |
| tall_rectangular_sloped | rec_black-plastic-jerrycan-..._ab019c96（parent 004）| `_left_wedge_cutter` L91-98 + `_inner_cavity` L101-110 + `_neck_boss` L142-156 + `_body_solid` L159-236（box body + sloped 肩 wedge → 高 plateau + `mouth` bore）| eligible if compatible | 高矩形 jerrycan（W>D，taller），斜/peaked shoulder 升到 flat 高 plateau，molded `_base_groove` + `_neck_boss` spout mound；offset neck 在低肩 -X 侧 |

硬约束记录：body_form 4 candidate（达 3-6 目标内）。全部 hollow 开口腔 + offset 短螺纹 neck + pour-mouth bore，共享 neck-stub helper；只换足迹（圆角矩形 vs 立方方 vs 高矩形）/ 高宽比 / 肩形（收 deck vs full-width slab vs recessed deck vs sloped plateau）/ molded 细节。保守计 3 distinct shape 家族（rounded_rect{deck,slab} / square_cubic / tall_rectangular_sloped）。

### Slot B：handle_grip（提携 / 抓握机构槽）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / joint / helper · 结构特征 |
|---|---|---|---|---|
| integrated_loop（基线）| rec_white-plastic-gallon-jug-..._0f3f18ac（parent 001）| `_handle_solid` L152-175（`loop` rrect extrude + `hole` finger-hole cut，filleted），union 入 `jug_shell` L191 | eligible if compatible | 升起的 rounded loop（real open finger hole），legs root 入 body 上肩壁，FIXED visual（无独立 joint）；偏 -X 侧 opposite neck |
| flush_dgrip | rec_gold-plastic-engine-oil-jug-..._47fb268a（parent 002）| `grip_hole` ellipse cut through 全 Y 深度 L118-129（`_bottle_body` 内）| eligible if compatible | flush 椭圆 finger hole 切穿肩 slab 全深（daylight 可见），grip bar flush 在 silhouette 内，FIXED（无 joint，无 protruding loop）|
| bridge_strap | rec_black-plastic-square-jerrycan-..._1078fc9e（parent 003）| `bar` strap union L100-108 + `tunnel` finger gap cut L113-121（`_body_solid` 内）| eligible if compatible | 顶部 raised arched strap，下方 `tunnel` 开 finger gap（gap floor < deck → 真实通过 clearance），FIXED（无 joint）；偏 -X 侧 opposite neck |
| recessed_top_slot | rec_black-plastic-jerrycan-..._ab019c96（parent 004）| `_rounded_slot_cutter` L113-122（front-to-back rounded-rect 切穿高 plateau，留 ~20mm grip bar）| eligible if compatible | molded carry slot 切在高 shoulder plateau（front-to-back through-slot 留顶 grip bar），FIXED（无 joint）；在 +X 高肩半 |
| swing_bail | rec_container_plastic_can_var_swing_bail | `_body_solid` 内两 `lug`/`col` mount @ `for sign in (-1,1)` L108-130 + `_bail_mesh`（`tube_from_spline_points` U-bar）L184-216 + `bail` part L259 + `bail_swing` REVOLUTE axis=(0,1,0) L270-283 | eligible if compatible | **活动 handle**：分离 U-bar bail tube 挂两 shoulder lug（pivot bearing），`bail_swing` REVOLUTE 绕 +Y，q=0 平贴肩 / 正 q 摆起提携 / q=π 折到对侧；唯一活动 handle，含独立 part + joint |
| recessed_grip_pocket | rec_container_plastic_can_var_recessed_grip_pocket | `for i, dz in (...)` 两 overlapping `scoop` sphere cut L124-131（`_bottle_body` 内）| eligible if compatible | 凹 molded 侧壁 hand-hold pocket（两 sphere 叠切成 elongated 凹陷），无 through-hole 无 loop，壁后留 solid，FIXED（无 joint）|

硬约束记录：handle_grip 6 candidate（达 3-6 目标上限）。5 个 FIXED（loop / flush_dgrip / bridge_strap / recessed_top_slot / pocket 均为 body 上 union/cut visual，无独立 joint）+ 1 个活动（swing_bail = 独立 `bail` part + `bail_swing` REVOLUTE）。结构差异：raised loop（proud past 壁）/ flush through-hole（壁内）/ arched strap + tunnel / molded plateau slot / 活动 U-bar bail / 凹 pocket（无穿透）。

### Slot C：cap_closure（**主开合机构槽**——neck 上的盖动作）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / part · 结构特征 |
|---|---|---|---|---|
| screw_cap（基线）| all 4 parents（典型 `0f3f18ac`）| `cap_carrier` part L232 + `cap` part + `_cap_mesh` knurled cap + `cap_rotate` CONTINUOUS +Z L260-268 + `cap_slide` PRISMATIC +Z L270-278 | eligible if compatible | 螺纹旋升盖：经 massless `cap_carrier`，`cap_rotate` CONTINUOUS +Z（旋）+ `cap_slide` PRISMATIC +Z（抬离 neck）；2 joint + 1 massless carrier part；knurl rib `for i in range(n)` mesh |
| flip_top_spout | rec_container_plastic_can_var_flip_top_spout | fixed `_closure_base_solid`（`collar`+`top_plate`+`spout` nozzle）L178-211 挂 body visual + `lid` part `_lid_solid`（hollow cup + hinge `ear`）L214-255 + `lid_hinge` REVOLUTE axis=(-1,0,0) @ 后 collar 边 L330-343 | eligible if compatible | snap flip-top：fixed collar + raised pour spout（body visual），hinged hollow `lid` 盖绕后 collar rim 水平 -X 轴 REVOLUTE，q=0 罩住 spout / 正 q 上翻露 spout，captive（不离体）；1 活动 part + 1 REVOLUTE |
| hinged_tethered_lid | rec_container_plastic_can_var_hinged_tethered_lid | fixed `collar`+`anchor` nub union body L234-250 + `flip_cap` part `_flip_cap_solid`（disc+rim+`strap` tab+`bump`）L266-334 + `cap_hinge` REVOLUTE axis=(-1,0,0) @ +Y collar 边 L374-387 | eligible if compatible | 一体 tethered 翻盖：fixed neck `collar` + `anchor` nub（living-hinge 固定端），captive `flip_cap`（strap tab 活动端）绕 collar 边 REVOLUTE 翻开，q=0 封口 / 正 q 翻起约 149°，盖 captive（tethered，bounded 位移）；1 活动 part + 1 REVOLUTE（无 carrier）|

硬约束记录：cap_closure 3 candidate（达下限 3）。含 CONTINUOUS+PRISMATIC（screw=2 joint + massless carrier）/ REVOLUTE +X（flip_top_spout = fixed spout base + hinged 罩 lid）/ REVOLUTE +X（hinged_tethered_lid = fixed collar+anchor + captive flip_cap）三种 closure 拓扑。每个 candidate **≥1 non-fixed joint**（满足 ≥1 活动机构）。flip_top_spout 与 hinged_tethered_lid 都 REVOLUTE 但**结构不同**：前者 lid 罩 over raised spout nozzle（fixed `spout` + hollow cup lid + `expect_within`），后者 flat flip_cap 封 collar 口（`collar`+`anchor` + strap tether，无 spout，强调 captive 位移界）。

## 槽位图（slot graph）

pattern: parallel_children（can `body` 为 root，坐地 z=0；handle / closure 子件挂到它；无 multiplicity）

```
body(body_form)  [ROOT, 坐地 z=0, offset 短螺纹 neck @ (NECK_X,NECK_Y,NECK_TOP_Z)]
   │
   ├── handle_grip = integrated_loop / flush_dgrip / bridge_strap / recessed_top_slot / recessed_grip_pocket:
   │       FIXED：handle 几何 union/cut 入 body `jug_shell`/`body_shell`（无独立 joint，无独立 part）
   │
   ├── handle_grip = swing_bail（唯一活动 handle）:
   │       body --[bail_swing: REVOLUTE +Y @ 两 shoulder lug 之间 (BAIL_X,0,BAIL_PIVOT_Z)]--> bail(独立 part)
   │       (bail tube 端 captured 入 lug bearing；q=0 平贴肩、正 q 摆起、q=π 折对侧)
   │
   ├── cap_closure = screw_cap（基线）:
   │       body --[cap_rotate: CONTINUOUS +Z @ neck rim top]--> cap_carrier(massless, 无 visual)
   │             cap_carrier --[cap_slide: PRISMATIC +Z]--> cap
   │
   ├── cap_closure = flip_top_spout:
   │       body 携 fixed closure_base visual（collar+top_plate+spout，挂 body, 无 joint）
   │       body --[lid_hinge: REVOLUTE -X @ 后 collar 边, z=collar top]--> lid(hollow cup, captive)
   │
   └── cap_closure = hinged_tethered_lid:
           body 携 fixed collar+anchor union（挂 body, 无 joint）
           body --[cap_hinge: REVOLUTE -X @ +Y collar 边, z=collar top]--> flip_cap(captive tethered)
```

接口点位与 joint 语义：
- **screw 接口**：`cap_rotate` origin 落 neck rim top `(NECK_X,NECK_Y,NECK_TOP_Z)`，axis +Z（CONTINUOUS）；`cap_slide` 经 massless `cap_carrier`（无 visual），axis +Z（PRISMATIC，q=0 坐下、正 q 抬离）。carrier 解耦 rotate/slide 共享 +Z（旋转不改高度——见 parent 003 decoupled check）。
- **flip / tethered 接口**：`lid_hinge` / `cap_hinge` origin 在后/+Y collar 边硬件（`(NECK_X, NECK_Y+COLLAR_R, COLLAR_TOP_Z)` 类），axis -X，REVOLUTE 闭合 q=0、上翻正 q（露 spout / 露 mouth）。fixed closure base（collar / spout / anchor）作 body visual（无 joint）。
- **bail 接口**：`bail_swing` origin 在两 shoulder lug 之间 `(BAIL_X,0,BAIL_PIVOT_Z)`，axis +Y，REVOLUTE，q=0 平贴肩 / 正 q 摆起 / q=π 折对侧。bail tube 端 captured 入 lug bearing。
- **handle FIXED 接口**：integrated_loop / flush_dgrip / bridge_strap / recessed_top_slot / recessed_grip_pocket 全为 body 的 union/cut visual（无独立 joint，无独立 part）；loop/strap 在 body 上肩偏 neck 对侧、dgrip/slot 在肩 slab/plateau、pocket 在侧壁。
- **mating policy**：screw cap skirt 罩 over neck rim、flip lid 罩 over spout、bail tube 端 captured 入 lug、tethered cap strap ↔ anchor 接触——都是 captured / 友配（故意小重叠），非两轴对接面 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（origin 落真实 rim / hinge / lug 硬件）+ element-scoped `allow_overlap` 守 overlap（见各 parent/variant run_tests 的 `ctx.allow_overlap`）。
- **rest pose**：所有 cap / lid / flip_cap q=0 闭合（cap 坐 neck、lid 罩 spout、flip_cap 封口）；bail q=0 平贴肩；FIXED handle 静态。cap 旋转/抬升、lid/flip_cap 翻起、bail 摆起为 viewer 目检的活动语义。
- **互斥 / 可选**：handle_grip 各候选互斥（一次一种 grip）；cap_closure 各候选互斥（一次一种盖机构）。`cap_carrier` massless part 仅在 screw_cap 候选发射；`bail` 独立 part 仅在 swing_bail 发射。

## 每槽位 Module Emits / Interfaces

### Slot A / body（body_form，ROOT）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（visual: `jug_shell`/`body_shell`/`jug_body` hollow shell + offset neck stub + molded 细节[ + FIXED handle union/cut]）| 001 `_body_solid` L93-149 / 003 `_body_solid` L57-175 / 004 `_body_solid` L159-236 |
| internal joints | 无（root 罐体本身无活动件）| — |
| upstream interface | 坐地 z=0（root）| 各 parent |
| downstream interface | neck rim top 中心 `(NECK_X,NECK_Y,NECK_TOP_Z)`（closure joint 的 parent 接口）+ shoulder lug 座（bail）| 001 NECK_TOP_Z L57 / 003 NECK_TOP_Z L43 / swing_bail BAIL_PIVOT_Z L64 |

### Slot B / handle_grip（FIXED 5 候选挂 body visual；swing_bail 发射活动 bail）
| emits | 描述 | 来源 |
|---|---|---|
| parts | FIXED：无独立 part（loop/dgrip/strap/slot/pocket 为 body visual）；swing_bail：独立 `bail` part + 两 body lug | 001 `_handle_solid` / 002 `grip_hole` / 003 `bar`+`tunnel` / 004 `_rounded_slot_cutter` / pocket `scoop` / swing_bail `_bail_mesh`+lug |
| internal joints | FIXED：无；swing_bail：`bail_swing` REVOLUTE +Y（lower=0, upper=π）| swing_bail L270-283 |

### Slot C / cap_closure（每候选发射对应活动盖 + 可选 fixed base）
| emits | 描述 | 来源 |
|---|---|---|
| parts | screw_cap: `cap_carrier`(massless)+`cap` / flip_top_spout: fixed `closure_base` visual + `lid` part / hinged_tethered_lid: fixed `collar`+`anchor` union + `flip_cap` part | 001 L232-257 / flip L178-255 / tethered L234-334 |
| internal joints | screw_cap: `cap_rotate` CONTINUOUS +Z + `cap_slide` PRISMATIC +Z / flip_top_spout: `lid_hinge` REVOLUTE -X / hinged_tethered_lid: `cap_hinge` REVOLUTE -X | 001 L260-278 / flip L330-343 / tethered L374-387 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | tall_rounded_rect_deck / tall_rounded_rect_slab / square_cubic / tall_rectangular_sloped | tall_rounded_rect_deck | choice | deterministic procedural sampler 选 | module table |
| handle_grip | enum | integrated_loop / flush_dgrip / bridge_strap / recessed_top_slot / swing_bail / recessed_grip_pocket | integrated_loop | choice | sampler 选 | module table |
| cap_closure | enum | screw_cap / flip_top_spout / hinged_tethered_lid | screw_cap | choice | sampler 选 | module table |
| palette_style | enum | red_fuel / yellow_diesel / blue_water / green_utility / black_oil / matte_olive_mil / gold_oil / natural_hdpe / white_jug（9 colorway，含 finish 维度，≥3）| red_fuel | palette | palette only，**不计入 slot_choice**；per-seed `rng.choice(PALETTE_STYLES)` | palette（见下）|
| body_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放罐体高度 H → deck/plateau/NECK_TOP_Z → closure mount 高度，clamp | resolve clamp |
| body_width_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放罐体宽 W（足迹 X）→ neck X offset 同比，clamp | resolve clamp |
| body_depth_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放罐体深 D（足迹 Y），clamp | resolve clamp |
| neck_radius_scale | float | [0.90, 1.10] | 1.0 | equation | `NECK_R = base · neck_radius_scale`；cap/collar/lid bore 半径派生跟随（保盖罩 neck 配合）| resolve clamp |
| closure_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 cap_slide 行程 + lid/cap hinge upper limit + bail_swing limit，clamp（保不穿罐）| resolve clamp |
| handle_size_scale | float | [0.90, 1.12] | 1.0 | conditional | 缩放 handle 尺寸（loop 高 / dgrip 椭圆 / strap span / slot / bail arm / pocket R）；范围依 handle_grip enum 与 rim/plateau 口径在 resolve 解析 | resolve（按 handle 派生）|
| (—) | constraint | — | — | inequality | 盖罩配合：`cap_bore_R ≥ NECK_R + clearance` 且 `cap_outer_R ≤ neck_boss_R + proud`；bail/handle 不得超 body 足迹穿罐；违反按比例回缩 neck/closure/handle scale | 接口 / clearance |

所有连续 scale 在 `resolve_config` clamp / 派生（每 build 解析一次）。`neck_radius_scale` 为 equation（cap / collar / lid bore 半径跟随 neck 半径，保盖罩 neck 配合不破）。`handle_size_scale` 为 conditional（合法上限随所选 handle_grip 与 body rim/plateau 口径变化，resolve 解析）。scale 只动安全比例 / clearance / 细节尺寸，绝不改 body_form / handle_grip / cap_closure 的拓扑。

**palette_style 颜色域**（**9 个 coordinated colorway**，来自 5★ 真实 HDPE 容器配色 + 真实 jerrycan 行业色码；per-seed `rng.choice(PALETTE_STYLES)` 采样，**不计 slot_choice**）。

每个 colorway = **body 主色 + handle 色 + cap/closure 色 + accent 色 + 一个 finish**。`finish` 是一条**显式的材质-表面维度**（不是新 slot；只调 material 的 specular/roughness/alpha 语义，cosmetic），取值：

- `matte_molded` — 哑光吹塑 HDPE（低高光、高粗糙度，molded 颗粒感；fuel/diesel/water/utility 工业罐主流）
- `gloss_molded` — 高光吹塑 HDPE（高 specular、低粗糙度，光亮表面；油料/家用 jug）
- `translucent_natural` — 无染半透自然 HDPE（**带 alpha < 1**，雾面透光；液位可见的 natural jug）
- `satin_military` — 缎面军用涂层（中等高光、略哑、深色稳重；olive/black 军规油桶）

| palette_style | finish | body rgba | handle rgba | cap/closure rgba | accent rgba | 现实出处 / 5★ 源 |
|---|---|---|---|---|---|---|
| red_fuel | matte_molded | 红 (0.72,0.10,0.10,1) | 红 (0.72,0.10,0.10,1) | 黑 (0.08,0.08,0.09,1) | 白 marker (0.92,0.92,0.92,1) | 汽油 jerrycan 行业红（fuel 标准色）; black cap 锚 003 `cap_black` L202 |
| yellow_diesel | matte_molded | 黄 (0.85,0.70,0.10,1) | 黄 (0.85,0.70,0.10,1) | 黑 (0.08,0.08,0.09,1) | 红 marker (0.80,0.10,0.10,1) | 柴油 jerrycan 行业黄（diesel 标准色）; red marker 锚 003 `marker_red` L203 |
| blue_water | matte_molded | 蓝 (0.15,0.35,0.70,1) | 蓝 (0.15,0.35,0.70,1) | 白 (0.92,0.92,0.92,1) | 白 (0.97,0.98,1.0,1) | 饮用水 jerrycan 行业蓝（water 标准色）; white cap 锚 001 `cap_white` L185 |
| green_utility | matte_molded | 绿 (0.14,0.42,0.20,1) | 绿 (0.14,0.42,0.20,1) | 黑 (0.08,0.08,0.09,1) | 白 marker (0.92,0.92,0.92,1) | 通用化学/园艺 utility jerrycan 行业绿（gas/oil 之外的杂用色码）|
| black_oil | gloss_molded | 黑 (0.12,0.12,0.13,1) | 灰 (0.20,0.20,0.21,1) | 黑 (0.08,0.08,0.09,1) | 红 marker (0.80,0.10,0.10,1) | 黑 jerrycan parent 003 `hdpe_black` (0.12,0.12,0.13,1) L201 + `cap_black` L202; bail_gray (0.20,0.20,0.21,1) swing_bail L244; marker_red L203 |
| matte_olive_mil | satin_military | 橄榄绿 (0.27,0.28,0.16,1) | 橄榄绿 (0.27,0.28,0.16,1) | 哑黑 (0.055,0.055,0.060,1) | 哑黑 (0.07,0.07,0.075,1) | 军规 olive-drab 油料/水 jerrycan; matte cap 锚 004 `ribbed_black_cap` (0.055,0.055,0.060,1) L270 + tethered `dark_gray_cap` (0.07,0.07,0.075,1) |
| gold_oil | gloss_molded | 金琥珀 (0.62,0.52,0.18,1) | 金琥珀 (0.62,0.52,0.18,1) | 黑 (0.09,0.09,0.10,1) | 浅灰 (0.90,0.88,0.90,1) | 金/琥珀 engine-oil jug parent 002 `gold_hdpe` (0.62,0.52,0.18,1) L175 + `cap_black` (0.09,0.09,0.10,1) L176 + `label_accent` (0.90,0.88,0.90,1) L178 |
| natural_hdpe | translucent_natural | 半透自然 (0.91,0.90,0.85,**0.72**) | 半透自然 (0.91,0.90,0.85,0.72) | natural (0.91,0.90,0.85,1) | 黑 (0.08,0.08,0.09,1) | 无染半透 HDPE（**alpha<1 透光**）; 锚 flip_top_spout `closure_natural` (0.91,0.90,0.85,1) L265（body 加 alpha 透光，cap/closure 仍 opaque 罩 spout）|
| white_jug | gloss_molded | 白 (0.95,0.95,0.95,1) | 白 (0.95,0.95,0.95,1) | 白 (0.92,0.92,0.92,1) | 青 label (0.28,0.72,0.80,1) | gallon-jug parent 001 `hdpe_white` (0.95,0.95,0.95,1) L181 + `cap_white` (0.92,0.92,0.92,1) L185 + `label_teal` (0.28,0.72,0.80,1) L183 |

说明：
- **饱和度**：molded plastic 真实饱和色（red/yellow/blue/green/olive/gold），只有 `natural_hdpe` 携 alpha=0.72（雾面透光，液位可见），其余 opaque alpha=1。
- **accent / marker / label** 是 cosmetic decoration visual（marker 小块 / label 贴片），**不计 slot**；可按 colorway 配色或省略。
- **handle 配色**：FIXED handle（loop/dgrip/strap/slot/pocket）union 入 body → 取 body 同色；`swing_bail` 独立 part → 取 handle 列色（如 black_oil 用 bail_gray 0.20,0.20,0.21）。
- **cap/closure 配色**：screw `cap` / flip `lid` / tethered `flip_cap` 用 cap/closure 列色；flip/tethered 的 fixed closure base（collar/spout/anchor）随 body 或 cap 列择一（cosmetic）。
- 实现：模板定义 `PALETTE_STYLES`（9 entry，每 entry 含 4 component rgba + finish 标签），`config_from_seed` 内 `rng.choice(PALETTE_STYLES)`；`finish` 只调 material specular/roughness/alpha，不改任何 slot/joint/几何。

## Multiplicity / Copy Logic

- 无复制数量逻辑：核心结构由固定 named slots（body_form + handle_grip + cap_closure）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。单罐 + 单 handle + 单 closure。
- 部件内复制（**非小类轴，不作独立 slot**）：每个 screw cap 用 `for i in range(n)` 发 knurl rib（`_cap_mesh`，n≈20–36）；swing_bail 用 `for sign in (-1,1)` 发两 mount lug + col（共享 lug helper + 统一 REVOLUTE policy）；tethered lid 用 `for i in range(n_ridges)` 发 grip ridge。这些 rib / lug / ridge 数是 module-internal 参数，不是 小类 N 轴（一个 can 一 body、一 handle、一 closure）。
- N 样本已覆盖：无（无 multiplicity 轴）。模板建议 N_range：无。

## 拓扑多样性审计

总组合数：body_form(4) × handle_grip(6) × cap_closure(3) = **72**。
（保守计 3 distinct shape 家族：3 × 6 × 3 = **54 ≥ 10** 仍充裕。）

仅 handle_grip × cap_closure = **18 ≥ 10** 已可过门控；叠 body_form 后充裕。

理由：本类拓扑多样性来源充裕——handle_grip(6) × cap_closure(3) = 18 distinct 已超 10；叠 body_form 至 72。handle_grip 引入 5 FIXED（loop / flush_dgrip / strap / slot / pocket，改 body part tree + cut/union 拓扑）+ 1 活动（swing_bail = 独立 part + REVOLUTE）；cap_closure 引入 CONTINUOUS+PRISMATIC（screw 2 joint + massless carrier）/ REVOLUTE -X（flip_top_spout fixed spout base + hollow lid）/ REVOLUTE -X（hinged_tethered_lid fixed collar+anchor + captive flip_cap）等不同 joint 拓扑 + 不同 part count（screw=3 part 含 carrier / flip=2 part / tethered=2 part / bail 再 +1 part），是真实结构差异。slot_choices 编入三轴。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler `rng.choice` 三个 named slot（笛卡尔积近全合法，少量 gating 见下），再 uniform 各连续 scale（independent → equation 派生 → inequality 投影回缩 → conditional 解析 handle 范围）+ `rng.choice` palette_style。compatibility matrix 排除非法/易坏组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-9 初轮 / 0-49 扩展 / 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：1000-seed slot choice tuple distinct 预计接近 72（72 组合的采样空间足够；受真实词汇表约束的轴是 cap_closure(3)，但 body_form(4) × handle_grip(6) 已撑开 24）。低于 300 的原因：本小类真实结构词汇就是 4 body × 6 handle × 3 closure = 72，是该类目合理上限，不强行注水。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 scale（body_height / body_width / body_depth / neck_radius / closure_travel / handle_size）。全部 `resolve_config` clamp + 每 build 统一应用。`neck_radius_scale` 为 equation（cap/collar/lid bore 半径派生跟随）；`handle_size_scale` 为 conditional（随 handle_grip 与 rim/plateau 口径解析）。盖罩配合不等式 + bail/handle 不穿罐不等式在 resolve 内投影 / 回缩，不留到 builder。这些 scale 不破坏 closure joint origin（neck rim top / 后 collar hinge / shoulder lug）、盖罩 neck 配合、handle 位置或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` 三 named slot（近全正交），再 uniform 各 scale + palette_style | slot_choices_for_seed 含三轴且与 build 一致 |
| compatibility matrix | (1) `recessed_top_slot` handle 占高 plateau 顶 → 与 `tall_rectangular_sloped` body 最自然；用于其它 body 时 slot 切在该 body 的最高肩面（resolve 派生切位，不 gate 掉）。(2) `bridge_strap` / `recessed_top_slot` / `swing_bail` 都在顶 deck/肩，offset neck 在另一侧（NECK_X 与 handle X 异号，保 ≥0.06 间距，见 parent 003 "cap offset clear of bridge" check）→ closure（尤其 raised `flip_top_spout` spout）与顶 handle 竞争 deck 空间时，handle 偏一侧、closure 偏另一侧，resolve 派生 X offset 保 clearance。(3) `recessed_grip_pocket` / `flush_dgrip` 在侧壁/肩 slab，需 body 有足够侧壁深度（tall_rounded_rect / square 友好；sloped jerrycan 侧壁可用）。(4) 各 handle 互斥、各 closure 互斥。(5) screw_cap 必经 massless carrier；flip/tethered 的 fixed base（spout/collar/anchor）随 closure 发射。无硬 gate-out（72 组合全合法，只在 resolve 派生尺寸/位置适配）| 无 floating / collision / handle 或 lid 穿罐 / joint 轴或 origin 错位 / handle 与 closure 顶面冲突 |
| controlled local variation | 6 个 clamped scale，每 build 统一；neck_radius equation 驱动 cap/lid bore；handle_size conditional 随 handle + rim 解析 | 比例变化不破坏 closure joint origin / 盖罩配合 / bail-lug 配合 / 坐地 / 类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-9 初轮 / 0-49 扩展；0-999 成熟审计 | closure/bail 动作 / 坐地 / overlap QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 4 | yes | yes | rounded_rect{deck,slab} / square_cubic / tall_rectangular_sloped（≥3 distinct shape 家族）|
| handle_grip | 6 | yes | yes | loop / flush_dgrip / strap / slot / swing_bail(REVOLUTE 活动) / pocket |
| cap_closure | 3 | yes | yes | screw(CONT+PRIS+carrier) / flip_top_spout(REV X+fixed spout) / hinged_tethered_lid(REV X+captive) |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 (body_form, handle_grip, cap_closure) 三轴
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 各 scale clamp 到声明范围；neck_radius equation 驱动 cap/lid bore；handle_size conditional 随 handle + rim 解析；盖罩配合 + handle/bail 不穿罐不等式在 resolve 内投影 / 回缩
- compatibility matrix / gating：72 组合全合法（无硬 gate-out）；顶 handle（strap/slot/bail）与 offset neck/closure 在 resolve 派生 X offset 保 ≥0.06 clearance
- 连续 scale clamp 后不破坏 closure joint origin / 盖罩配合 / bail-lug 配合 / 坐地 / 类别身份
- 关键 joint：screw `cap_rotate` CONTINUOUS +Z (abs(axis[2])>0.99) + `cap_slide` PRISMATIC +Z + massless `cap_carrier`（无 visual）；flip_top_spout `lid_hinge` REVOLUTE -X (abs(axis[0])>0.99)；hinged_tethered_lid `cap_hinge` REVOLUTE -X；swing_bail `bail_swing` REVOLUTE +Y (abs(axis[1])>0.99) 有限 limit [0,π]
- captured-fit：element-scoped `allow_overlap`（cap skirt ↔ jug/body shell；lid ↔ closure_base/spout；bail tube ↔ shoulder lug；flip_cap strap ↔ collar anchor）
- hollow body：每 body_form 真 hollow shell + 通到内腔的 pour-mouth bore（不是 blind 凹）
- grandfather：盖罩 / bail-lug captured-fit 省略 MatingContract，由 origin 检查 + allow_overlap 守
- body 坐地 z=0、offset neck（非居中）、handle 是类别身份强标志

## Reject cases

- 用纯 Box 占位体当 molded HDPE body（无 hollow shell / 无 fillet / 无 offset neck）→ 失类别身份；body 必须 hollow loft / box+fillet+shell + offset 短螺纹 neck + pour-mouth bore。
- closure joint origin 放在罐底 / 任意点而非 neck rim top / 后 collar hinge / shoulder lug 真实硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- screw 盖不用 massless `cap_carrier` 解耦 rotate/slide，直接把 CONTINUOUS+PRISMATIC 串到 cap 单 part → 旋转与抬升耦合错误（应 body→carrier→cap 两 joint；旋转不应改高度）。
- cap_closure / bail rest pose 设成张开 / 抬起而非 q=0 闭合/平贴 → current-pose 与 viewer 目检不符。
- 给盖罩 / bail-lug captured-fit 补 MatingContract 硬对接 → 配合几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异（palette_style 是 palette，不计 slot_choice；body 大小是 scale）。
- handle（loop/strap/bail）与顶 closure 抢同一 deck 中心 / 互穿 → resolve 未派生 X offset clearance（应 handle 偏一侧、closure 偏另一侧）。
- bail / lid 摆动时穿罐壁 / origin 漂移 / 飞离（非 captive）→ closure_travel/bail limit 不等式或 captive 位移界（dist<0.08）FAIL。
- 把 jerrycan body 做成细颈高瓶 / 金属薄壁罐 → 出 plastic can 语义（细颈归 `container_bottle`，金属罐归 `container_can`）。

## 与相邻类别的边界

- 不该混入：**container_can 金属罐头 tin**——理由：金属薄壁、易拉环 / 卷边盖、无 molded HDPE handle、无 screw neck；plastic can 是厚壁吹塑 + 集成 handle + 螺纹 cap/spout。
- 不该混入：**container_laundry_detergent_bottle 洗衣液瓶**——理由：洗衣液瓶身更修长、单独握把柄 + 大量杯/泵盖；plastic can 是 chunky jerrycan/jug 足迹 + 集成 loop/strap/slot/bail handle + screw/flip cap。
- 不该混入：**container_dispenser 泵式分液器 / 喷雾**——理由：dispenser 主机构是按压泵 / 喷头（trigger/pump），plastic can 主机构是 screw cap 旋升 / flip 翻盖。
- 不该混入：**container_bottle 细颈瓶 / 酒瓶**——理由：细长瓶身长颈、无 handle；plastic can 是宽足迹 chunky 罐身 + 集成 handle。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。8 源全文读取（4 parents + 4 variants）。4 body × 6 handle × 3 closure = 72 combos；handle×closure=18、body×handle=24 均清。三 closure 拓扑（screw CONT+PRIS+carrier / flip_top_spout REV + fixed spout / hinged_tethered_lid REV + captive）；6 handle（5 FIXED + swing_bail REVOLUTE 活动）；palette_style **9 coordinated colorway**（red_fuel / yellow_diesel / blue_water / green_utility / black_oil / matte_olive_mil / gold_oil / natural_hdpe / white_jug），每 colorway = body+handle+cap/closure+accent 四组件配色 + 显式 **finish 维度**（matte_molded / gloss_molded / translucent_natural[alpha<1] / satin_military），anchor 到 5★ RGBAs（001 white/cap_white/teal、002 gold/cap_black/accent、003 hdpe_black/cap_black/marker_red、004 ribbed_black_cap、swing_bail bail_gray、flip_top_spout closure_natural），palette-only 不计 slot_choice；无 multiplicity 轴。与 container_can(金属) / laundry_detergent_bottle / dispenser / bottle 边界明确。|

## 模板实现备注（可选）

- 共享 helper：`_rrect_loft`/`_loft_rrects`（圆角矩形 loft，rounded_rect body）+ `_box_fillet_shell_body`（square_cubic body，`box`+`fillet("|Z")`+inset shoulder+pocket+shell+cut）+ `_sloped_body`（box + `_left_wedge_cutter` plateau）+ `_neck_stub(neck_x,neck_y,rim_z,neck_r)` + `_mouth_bore` 全 body module 公用；handle helper `_loop`/`_dgrip_cut`/`_strap_bar_tunnel`/`_slot_cutter`/`_bail_tube`/`_pocket_scoop`；closure helper `_screw_cap`(carrier+cap)/`_flip_spout_base+lid`/`_tethered_collar+flip_cap`。
- screw_cap：必须经 massless `cap_carrier`（无 visual，1e-4 mass Box inertial）解耦 `cap_rotate`(CONTINUOUS)→`cap_slide`(PRISMATIC)；旋转不应改高度（decoupled check）。
- swing_bail：两 mount lug via `for sign in (-1,1)`（共享 lug+col helper），`bail` 独立 part + `bail_swing` REVOLUTE +Y limit [0,π]；bail tube `tube_from_spline_points` U-path。
- flip_top_spout / hinged_tethered_lid：fixed closure base（collar/spout/anchor）作 body visual（无 joint），活动 `lid`/`flip_cap` 经 REVOLUTE -X 挂 body；flip lid 是 hollow cup 罩 over raised spout（`expect_within`），tethered cap 强调 captive 位移界（dist<0.08）。
- captured-fit overlap：`run_container_plastic_can_tests` 里 `ctx.allow_overlap`（cap_shell ↔ body shell；lid_cap ↔ closure_base；bail_tube ↔ body_shell lug；flip_cap_shell ↔ body collar anchor），按各源 run_tests 的 allow_overlap reason 复制。
- neck_radius equation：`resolve_config` 派生 `cap_bore_R = NECK_R + clearance`、`cap_outer_R = neck_boss_R + proud`，盖罩配合不等式在 resolve 投影。
- 顶 handle × offset neck/closure clearance：resolve 派生 handle X 与 NECK_X 异号且 ≥0.06 间距（parent 003 "cap offset clear of bridge/bail" check）。
- 参考模板：`agent/templates/Container_Jar.py`（同 Container 大类、同 parallel_children body+closure+seal 三轴 + screw massless carrier + REVOLUTE flip + allow_overlap grandfather 骨架，最近邻）；`agent/templates/Chair_Folding_chair.py`（Config/ResolvedConfig + config_from_seed + resolve_config clamp + slot_choices_for_config 报 topology family + run_<stem>_tests allow_overlap 骨架）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | tall_rounded_rect_deck + integrated_loop + screw_cap | rec_white-plastic-gallon-jug-..._0f3f18ac | `_rrect_loft` L78-90 / `_body_solid` L93-149 / `_handle_solid` L152-175 / `cap_carrier`+`cap_rotate`+`cap_slide` L232-278 | 圆角矩形 body 基线 + raised loop handle + screw-cap 旋升 + massless carrier |
| S2 | A/B | tall_rounded_rect_slab + flush_dgrip | rec_gold-plastic-engine-oil-jug-..._47fb268a | `_loft_rrects` L71-81 / `_bottle_body` L84-130 / `grip_hole` L118-129 / `_neck` L133-151 | full-width 肩 slab body + flush 椭圆 D-grip 切穿 |
| S3 | A/B/C | square_cubic + bridge_strap + screw_cap | rec_black-plastic-square-jerrycan-..._1078fc9e | `_body_solid` L57-175（`box`+fillet+pocket+`bar`+`tunnel`+`boss`/`neck`+ribs+foot）/ `_cap_mesh` L178-195 / cap joints L236-253 | 近立方方 pail body + bridge strap handle + screw-cap（decoupled check 源）|
| S4 | A/B/C | tall_rectangular_sloped + recessed_top_slot + screw_cap | rec_black-plastic-jerrycan-..._ab019c96 | `_left_wedge_cutter` L91-98 / `_neck_boss` L142-156 / `_body_solid` L159-236 / `_rounded_slot_cutter` L113-122 / cap joints L298-315 | 高矩形斜肩 jerrycan body + plateau carry slot + screw-cap + neck boss |
| S5 | B | swing_bail | rec_container_plastic_can_var_swing_bail | 两 `lug`/`col` `for sign in (-1,1)` L108-130 / `_bail_mesh` L184-216 / `bail` part L259 / `bail_swing` REVOLUTE +Y L270-283 | 活动 U-bar swing bail handle（独立 part + REVOLUTE）|
| S6 | B | recessed_grip_pocket | rec_container_plastic_can_var_recessed_grip_pocket | 两 overlapping `scoop` sphere cut `for i,dz` L124-131 | 凹 molded 侧壁 hand-hold pocket（无 through-hole）|
| S7 | C | flip_top_spout | rec_container_plastic_can_var_flip_top_spout | `_closure_base_solid`（collar+top_plate+spout）L178-211 / `_lid_solid`（hollow cup+ear）L214-255 / `lid_hinge` REVOLUTE -X L330-343 | snap flip-top：fixed spout base + hinged hollow 罩 lid |
| S8 | C | hinged_tethered_lid | rec_container_plastic_can_var_hinged_tethered_lid | `collar`+`anchor` union L234-250 / `_flip_cap_solid`（disc+rim+strap+bump）L266-334 / `cap_hinge` REVOLUTE -X L374-387 | 一体 tethered 翻盖：fixed collar+anchor + captive flip_cap |
