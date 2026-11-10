# Urban Environment / Caster Trolley2 — chrome wire-basket shopping cart — Modular Spec

> 来源小类：`picture/Urban Environment/Caster Trolley2`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Urban_Environment__Caster_Trolley2.md`。
> 参考图：`picture/Urban Environment/Caster Trolley2/001.png`（tapered 铬丝篮 + 红把手/红角保 + 折叠童座 + 下层丝托 + 4 只万向脚轮）。
> **同步/评级注记**：本 spec 引用的 `model.py:Lx-Ly` 来自该小类的 workbench-only 样本（1 parent baseline + 5 个已采纳 REDO fork），已同步进本仓库沿途所用的 `articraft_data/data/records/`。当前 `record.json` 的 `rating` 字段读为 `null`（workbench fork 未回填评级），source map 已把这 6 个记为"variant-review 已通过、可进 proto-spec"的采纳集；本 spec 即以这 6 个为唯一 module 来源。引用以 part/joint/helper **名字** 为准（`basket`/`underframe`/`push_handle`/`child_seat_flap`/`caster_yoke_{i}`/`caster_wheel_{i}`/`_side_pt`/`_end_pt`/`add_caster`/`perimeter_loop`），行号按各样本当前 `revisions/rev_000001/model.py` 计。

## 元信息
| 项 | 值 |
|---|---|
| slug | `Urban_Environment_Caster_Trolley2` |
| template path | `agent/templates/Urban_Environment_Caster_Trolley2.py`（stem `shopping_cart`）|
| test path (optional) | `tests/agent/test_Urban_Environment_Caster_Trolley2_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（basket 根 + parallel children: underframe / push_handle / front_bumper×2 / child_seat_flap；**外加** frame→yoke→wheel 的 4 只脚轮 linear-chain 固定复制 ×4）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6（1 parent baseline + 5 个已采纳 REDO fork；均 converged、compile 通过、均有 URDF，workbench-only；`rating=null` 见上方注记，source map 已背书为采纳集）|
| read_count | 6（全部逐一全文读取，非抽样：parent `model.py` 全文 + 每个 REDO fork 对 parent 的完整 diff（envelope/module/test 段全部读到））|
| read_scope | all adopted samples in this subcategory（source map 列出的全部 6 个采纳记录都读；source map 记录的 5 个已删 var_* + 2 个已删 redo_* 不进 module 表）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；已删/被拒样本不列 |

样本分流说明（对齐 source map 六轴审计）：
- **6 个样本共享同一 skeleton 与同一 9 根非 fixed 关节集**（1 seat-flap REVOLUTE + 4 yaw CONTINUOUS + 4 spin CONTINUOUS）。5 个 REDO fork 全部只改**固定模块 / 主体形态 / 表面装饰**，不新增关节、不改关节 origin/axis/limit（source map motion-safety：URDF 对比确认每个 fork 与 parent 同 9 根非 fixed 关节）。因此本类别 ① 骨架图与 ② 关节类型**无独立变化轴**（见 §8.5），多样性来自 ③ 主体形态家族（篮体 + 下层甲板）+ ④ 表面装饰（前面板 / 边缘护条）+ ⑤ 尺寸行程 + ⑥ 涂装。
- 已删 fork（source map "Rejected/deleted"）：`var_rear_nesting_gate` / `var_child_seat_leg_holes` / `var_lower_rack_deep` / `var_front_swivel_rear_fixed` / `var_wire_density_high`（外观变化过弱或有运动/关节风险）+ `redo_plastic_basket_panels`（悬空几何）+ `redo_side_liner_panels`（前衬板断连 QC 未落地）。均不进 module 表，`var_front_swivel_rear_fixed` 之意图（前万向后固定）记入 §10 排除素材。

## 核心身份

超市**铬丝篮购物手推车**（chrome wire-basket shopping cart / supermarket trolley）：主体是一只**开口的锥形铬丝网篮**（tapered wire basket，前窄矮、后宽高，截面为圆角矩形，密排竖丝 + 纵向 rail + 细网底），坐在一副**外张铬管底架**（splayed chrome underframe：侧纵梁 + 前后横管 + 上斜撑到篮底 rim）上，底架下**4 只橡胶胎万向脚轮**（每只绕竖直 kingpin 连续 YAW + 绕轴连续 ROLL），底架腿间一层**下层丝托 / 货架**（lower wire tray/cargo shelf）；篮体后上方一根**塑料推把**（+X 高端，斜杆 + 端帽 + 短立柱），篮体后内一片**折叠童座翻板**（child-seat flap，绕横向 Y 轴 REVOLUTE：q=0 立起、正向折下成座）；前上角**塑料角保**（front corner bumper caps）。世界系：Z 向上、把手/推端 +X、前/嵌套端 −X、宽度 Y、四轮触 z≈0。

活动语义（motion 主契约，全部继承自 parent，5 fork 不变）：**4 只脚轮各 360° 万向转（yaw 连续）+ 各绕轴自转（roll 连续，轴过轮毂中心 → 原地自转）+ 童座翻板绕 Y 轴 REVOLUTE 下折（[0, ~1.5] rad）**。默认成熟域：单台整车，脚轮固定 ×4（真实购物车永远 4 轮，非采样 multiplicity 轴，见 §8）。

不该混入（详见 §11）：平板 / 台车 `caster_trolley`（平甲板 + 竖直推把、无丝篮、无童座——本类别的**同名邻类**）、手提购物篮 `shopping_bucket`（无轮无底架无脚轮，手提篮）、行李箱 `suitcase`（带轮拉杆硬壳）。

## 槽位 + 候选模块表

> **建模注记**：`basket`（根）+ `underframe` / `push_handle` / `front_bumper_{p,n}` / `child_seat_flap` 各自挂到 basket（parallel children，`basket_to_*` FIXED，flap 为 REVOLUTE）；4 只脚轮是 `frame → caster_yoke_{i} → caster_wheel_{i}` 的固定复制链（挂到 `underframe`）。下面 5 个 slot 是"可替换的固定模块 / 主体形态层"，它们与固定 ×4 脚轮链的笛卡尔积构成拓扑多样性（见 §9）。所有 slot 的 candidate **均不新增关节、不改 9 根非 fixed 关节的 origin/axis/limit**（motion-safety 硬契约）。

### Slot A：basket_form（③ 主体形态家族 / Primary Form Family——篮体主体，类别身份主承载）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype | 结构特征 |
|---|---|---|---|---|---|---|
| standard_tapered_basket（基线） | forked_anchor | S1 parent `58ed850d` | 截面参数 L56-L163 + basket 装配 L179-L279（`_side_pt`/`_end_pt`/`perimeter_loop`）| eligible if compatible | Volumetric Envelope Form | tapered 圆角矩形丝篮：前窄矮(B_FRONT)→后宽高(B_BACK)，标准墙深（back top≈0.66）；密竖丝 + 4 纵 rail + 顶/底 rim + 网底 |
| deep_family_basket | forked_anchor | S2 `redo_deep_family_basket` | envelope 参数 L60-L61（B_BACK_TOP_Z 0.66→**0.84**、B_FRONT_TOP_Z 0.575→**0.72**）+ 顶 rim 加粗 L217（RAIL_R+0.0035）| eligible if compatible | Volumetric Envelope Form | 同一 part tree / 同一 `_side_pt`/`_end_pt` 发射，near-vertical 墙**显著加深**（back 墙高≥0.35m）+ 顶 rim 加粗；家庭 / 仓储大容量篮 |
| straight_wall_basket | world_knowledge_extrapolation | anchors: S1+S2（同 `_half_y`/`_z` lerp 家族）+ reviewer | n/a（生成函数：令 B_FRONT_HALF_Y≈B_BACK_HALF_Y 且 front/back top_z 近平，taper→0）| eligible if compatible | Planar Boundary Form | 同 part tree / 同 primitive / 同 interface，仅把**平面足迹**从梯形改为近矩形（不收锥的直壁网篮，常见于货运 / 五金卖场车）；plan-view 轮廓离散变化，非缩放 |

硬约束记录：basket_form 3 candidate（达 3-6 目标下限，且形态主导类要求登记 ③ slot ✔）。A1↔A2 为 Volumetric Envelope（墙深 + rim 比例的离散原型，非均匀缩放——A2 另改 rim 半径与墙面比例，source 评审已把"deep family"作为 form-family 采纳）；A3 为 Planar Boundary（taper on/off，改 plan 轮廓）。三者共享 `_side_pt`/`_end_pt`/`perimeter_loop` 装配与 basket→children 全部接口，安全。

### Slot B：lower_deck（下层甲板模块——底架腿间的货架层）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| flat_wire_tray（基线） | forked_anchor | S1 parent `58ed850d` | `underframe` 内 tray 段 L405-L466（`tray_rim` 闭环 + 纵/横 tray wire，`tray_z=CHASSIS_Z+0.012`）| eligible if compatible | 平坦丝托：单层矩形丝网平台（周边 rail 闭环 + 7 纵 + 11 横丝），无立壁 |
| walled_cargo_basket | forked_anchor | S3 `redo_lower_basket_visible` | 下层货架段 L405-L528（密网底 13 纵×19 横 + 抬高 side/end rail `shelf_rail_z` + 四周竖 guard wire + 4 角 collar）| eligible if compatible | 有立壁下层货篮：密网底 + 抬高四边 rail（离地 0.05m）+ 四周短竖 guard 丝 + 角柱 collar，构成一只浅下层筐（比平托多"立壁"结构层）|

硬约束记录：lower_deck 仅 2 candidate（低于 3 目标，记理由）。理由：参考图与 6 个样本的下层甲板在结构上只有这两族（平丝托 / 有壁货篮），二者均为丝网、差在"有无立壁 + 网密"这一真实结构层；下层甲板**始终存在**（无"去掉下层"的采纳样本，且真实购物车基本都带下层托），不为凑第 3 个发明结构。多样性主承载在 Slot A（③ 形态家族）+ §9 的笛卡尔积。两 candidate 都挂 `underframe`、都在 wheel-top 之上、都受同一 clearance 不等式（见 §7/§9），安全。

### Slot C：handle_form（推把模块——后上方 FIXED 把手总成）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| red_bar_handle（基线） | forked_anchor | S1 parent `58ed850d` | `push_handle` L284-L324（红斜杆 Cylinder + 2 端帽 Cylinder + 2 短立柱 `handle_post_{p,n}` tube）| eligible if compatible | 简约红塑推把：单横斜杆 + 圆端帽 + 后角上立柱，`basket_to_handle` FIXED |
| ergonomic_sleeve_handle | forked_anchor | S4 `redo_handle_sleeves` | 人机把总成 L285-L372（cadquery 圆角矩形 sleeve + 2 厚端帽 + 2 侧夹 bracket + 7 grip 脊 + 铬立柱 `handle_post_{p,n}`）| eligible if compatible | 人机工学把：宽圆角 sleeve 主握 + 厚端帽 + 模塑侧夹 + 顶面防滑脊；立柱改铬（frame-mount 接口不变），`basket_to_handle` 仍 FIXED |
| loop_bar_handle | world_knowledge_extrapolation | anchors: S1（`_tube`/`tube_from_spline_points` 家族）+ reviewer | n/a（生成函数：单根 U 形连续 tube，绕后上 rim 两角起 → 顶横段）| eligible if compatible | 单根 U 形连续管环把（购物车极常见），同 `push_handle` FIXED part、同 tube primitive、同后角立柱接口；仅把"斜杆+帽+柱"离散重构为一体 loop（非缩放/换色）|

硬约束记录：handle_form 3 candidate（达 3-6）。C1/C2 forked_anchor；C3 为 world_knowledge_extrapolation（U-loop 把，SDK 用 `tube_from_spline_points` 直接可造、类别忠实），仅重构 `push_handle` 内部几何、保 `basket_to_handle` FIXED 与后角立柱 mount 接口。三者 motion 契约：把手须在童座翻板全折下时留 z 间隙（见 §5/§7 不等式，源自 S4 的 `expect_gap(handle, flap, z, 0.010)` L831-L838）。

### Slot D：front_face（④ 表面装饰——前壁固定面板，含"无面板"空候选）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| plain_front（基线） | forked_anchor | S1 parent `58ed850d` | —（parent 前壁只有丝网 + 红角保，无面板 part / 无面板 visual）| eligible if compatible | 敞露丝网前壁（不发射面板 visual）|
| front_ad_panel | world_knowledge_extrapolation / record_only | S4→实为 S(front_ad) `redo_front_ad_panel` | 前广告面板段 L273-L381（`front_panel_body` rounded-rect ExtrudeGeometry + `front_panel_border` + 2 `front_panel_stripe_` + `front_panel_logo` + 4 `front_panel_tab_` 夹爪）| eligible if compatible | host-conformal 前面板：贴前壁平面（背面 flush 于 x=B_FRONT_X）的模塑广告板（板体 + 凸边框 + 横条 + logo + 4 夹爪），**全部作为 basket 的 visual**（非独立 part、非关节）；仅表面附加装饰层 |

硬约束记录：front_face 2 candidate（低于 3，记理由）。理由：这是 ④ 表面装饰轴（host-conformal、非结构、非关节），真实样本仅提供"无 / 有前广告板"两态；面板几何由前壁平面（`B_FRONT_X` / `B_FRONT_TOP_Z` / `B_FRONT_BOT_Z`）派生嵌入（派生顺序 ③basket_form→⑤尺寸→④panel，随 basket 前壁尺寸共形缩放），不悬空、不伪装成 module。face 与 rim（Slot E）为**可独立组合**的两个装饰轴（笛卡尔积见 §9）。面板须 clear 脚轮（z 分离 >0.10）与全折童座（x 分离，源自 S(front_ad) 测试 L945-L962）。

### Slot E：rim_treatment（④ 表面装饰——顶 rim / 角部保护，含 corner-bumper 基线）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| red_corner_bumpers（基线） | forked_anchor | S1 parent `58ed850d` | `front_bumper_{p,n}` L329-L345（前上角 2 只红 Box 角保，`basket_to_bumper_{p,n}` FIXED）| eligible if compatible | 最小保护：仅前上两角红塑角保盒（parent 默认） |
| orange_rim_guard_sleeves | forked_anchor | S6 `redo_rim_guard_bumpers` | 边缘护条段 material L175 + guards L223-L252（2 `rim_guard_side_` 沿左右顶 rim + `rim_guard_front` 前顶 rim + 4 `rim_guard_corner_` 角帽）| eligible if compatible | 满边缘护：橙色模塑厚护套沿左/右/前顶 rim + 4 角圆帽（`_side_pt(...,1.0)`/`_end_pt(...,1.0)` 沿顶 rim 派生的 tube），全部 basket visual、非关节；比基线多"沿 rim 连续护套"表面层 |

硬约束记录：rim_treatment 2 candidate（低于 3，记理由）。理由：④ 表面装饰轴，样本仅提供"最小角保 / 满 rim 护条"两态；护条几何由顶 rim 路径（`_side_pt(t,sy,1.0)` / `_end_pt(0,fy,1.0)`）逐-z 派生共形嵌入（随 ③basket_form 顶 rim 走），不悬空。护条须在 wheel-top 之上（>0.10）且内缘 outboard 于童座 Y 范围（source S6 测试 L810-L897：`rim_guard_side_*_outboard_of_flap` / `*_above_wheels`）。E 与 D 可独立组合。

## 槽位图（slot graph）

```text
pattern: mixed（parallel children on basket root + fixed ×4 caster linear chains under frame）

                         basket (ROOT = Slot A: basket_form ③)
                           │  几何身份：_side_pt/_end_pt/perimeter_loop 锥形丝篮
   ┌───────────────┬───────┴────────┬──────────────────┬─────────────────────────┐
   │FIXED          │FIXED           │REVOLUTE           │FIXED(装饰)               │FIXED(装饰)
   │basket_to_     │basket_to_      │basket_to_seat_flap│Slot D front_face          │Slot E rim_treatment
   │underframe     │handle          │(axis=(0,-1,0),    │(basket visuals,           │(basket visuals /
   ▼               ▼                │ limit[0,1.5])     │ 无新关节)                  │ front_bumper FIXED parts)
underframe      push_handle       ▼                    ▼                          ▼
(含 Slot B       (Slot C           child_seat_flap      前壁派生面板                顶 rim 派生护条 + 角帽
 lower_deck)      handle_form)      (翻板)
   │
   │ FIXED ×4（frame_to_caster_yoke_{i}, CONTINUOUS YAW axis=(0,0,1)）  ← 固定复制，非采样 multiplicity
   ▼
caster_yoke_{0..3}
   │ CONTINUOUS ROLL（caster_spin_{i}, axis=(0,1,0), origin 过轮毂中心 (-FORK_OFFSET,0,lb)）
   ▼
caster_wheel_{0..3}
```

接口点位与关节策略（全部继承 parent，candidate 不改）：
- **basket → underframe**：FIXED；上斜撑焊到 basket 底 rim（`_side_pt(t,sy,0.0)`），mating = 篮底 rim 接触面。Slot B 只换 underframe **内部**下层甲板 visual，接口不变。
- **basket → push_handle**：FIXED；后角立柱 `handle_post_{p,n}` clamp 到后顶 rim 角（`_side_pt(1.0,sy,1.0)`），mating = 后顶 rim 角。Slot C 只换 sleeve/loop 内部几何，保立柱 mount 接口。
- **basket → child_seat_flap**：REVOLUTE，origin=(B_BACK_X−0.006, 0, 0.500)，axis=(0,−1,0)，limit=[0,1.5]；pivot = 后内横向铰线。**唯一非脚轮活动件**。
- **Slot D / E**：装饰层，无跨 slot 关节；由 basket 表面（前壁 / 顶 rim）派生，随 Slot A 形态共形。二者互相独立、与 A/B/C 独立组合。
- **underframe → caster_yoke_{i}**：CONTINUOUS，axis=(0,0,1)（kingpin YAW），origin 在 chassis 下 (cx,cy,CHASSIS_Z)；四组 FIXED 复制（cx∈{REAR_AXLE_X,FRONT_AXLE_X}, cy∈{±TRACK_HALF_Y}）。
- **caster_yoke_{i} → caster_wheel_{i}**：CONTINUOUS，axis=(0,1,0)（ROLL），origin 过轮毂中心 → clean-origin gate（原地自转 moved<1e-4）。

互斥 / 派生说明：Slot D `plain_front` = 空装饰（不发射面板）；Slot A 决定前壁 / 顶 rim 的尺寸，D/E 的派生几何**依赖 A 的当前 envelope**（conditional，见 §7）。

## 每槽位 Module Emits / Interfaces

### Slot A / basket_form（standard_tapered / deep_family / straight_wall）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `basket`（根 part）：顶/底 rim + 4 纵 rail（`perimeter_loop`）+ 密竖丝（side/front/back vwire）+ 网底（floor l/t wire）| S1 L179-L267 |
| internal joints | 无（根 part 无内部关节）| S1 |
| upstream interface | root（world）| S1 L166 |
| downstream interface | 底 rim 接触面（→underframe 上斜撑）、后顶 rim 角（→handle 立柱）、后内铰线(z=0.5)（→seat flap）、前壁平面（→Slot D）、顶 rim 路径（→Slot E）| S1 `_side_pt`/`_end_pt` L151-L157 |

### Slot B / lower_deck（flat_wire_tray / walled_cargo_basket）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `underframe` 内下层甲板 visual：平托 `tray_rim`+纵横丝 / 货篮网底+四边 rail+guard 丝+角 collar | S1 L405-L466 / S3 L405-L528 |
| internal joints | 无（甲板是 underframe 的 visual 组）| S1/S3 |
| upstream interface | 底架腿间（`shelf_z=CHASSIS_Z+0.012`，随 underframe FIXED 于 basket）| S1 L406 / S3 L98 |
| downstream interface | 无（末端装饰层）| — |

### Slot C / handle_form（red_bar / ergonomic_sleeve / loop_bar）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `push_handle`：横把主体 + 端帽 + 后角立柱 `handle_post_{p,n}`（+ C2 侧夹/防滑脊）| S1 L284-L324 / S4 L285-L372 |
| internal joints | 无（整把 FIXED）| S1 |
| upstream interface | 后角立柱 clamp 到后顶 rim 角 `_side_pt(1.0,sy,1.0)` | S1 L306-L316 |
| downstream interface | 无 | — |

### Slot D / front_face（plain_front / front_ad_panel）
| emits | 描述 | 来源 |
|---|---|---|
| parts | basket visual：`front_panel_body`/`_border`/`_stripe_*`/`_logo`/`_tab_*`（plain=不发射）| S(front_ad) L273-L381 |
| internal joints | 无（全 basket visual，非关节）| — |
| upstream interface | 前壁平面（背面 flush 于 x=B_FRONT_X，随 Slot A 前壁尺寸派生）| S(front_ad) L303-L305 |
| downstream interface | 无 | — |

### Slot E / rim_treatment（red_corner_bumpers / orange_rim_guard_sleeves）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_bumper_{p,n}`（FIXED parts，基线）/ basket visual `rim_guard_side_*`/`rim_guard_front`/`rim_guard_corner_*` | S1 L329-L345 / S6 L223-L252 |
| internal joints | `basket_to_bumper_{p,n}` FIXED（基线角保）；护条无关节 | S1 L340-L345 |
| upstream interface | 前上角 rim / 顶 rim 路径（`_side_pt(t,sy,1.0)` / `_end_pt(0,fy,1.0)`，随 Slot A 顶 rim 派生）| S6 L226-L252 |
| downstream interface | 无 | — |

### 固定 ×4 脚轮链（frame → caster_yoke_{i} → caster_wheel_{i}）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `caster_yoke_{i}`（swivel_plate/kingpin/offset_bracket/fork_crown/fork_leg/axle）+ `caster_wheel_{i}`（WheelGeometry rim + TireGeometry tire）| S1 L521-L609 |
| internal joints | `frame_to_caster_yoke_{i}` CONTINUOUS z-yaw；`caster_spin_{i}` CONTINUOUS y-roll（origin 过轮毂）| S1 L611-L628 |
| upstream interface | kingpin 顶座 bolt 到 chassis (cx,cy,CHASSIS_Z)（scoped allow_overlap yoke↔frame）| S1 L611-L619, L661-L666 |
| downstream interface | 轮毂 bore 捕获 axle（scoped allow_overlap axle↔rim）| S1 L651-L657 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| basket_form | enum | {standard_tapered_basket, deep_family_basket, straight_wall_basket} | — | choice | deterministic sampler 选 | Slot A |
| lower_deck | enum | {flat_wire_tray, walled_cargo_basket} | — | choice | sampler 选 | Slot B |
| handle_form | enum | {red_bar_handle, ergonomic_sleeve_handle, loop_bar_handle} | — | choice | sampler 选 | Slot C |
| front_face | enum | {plain_front, front_ad_panel} | — | choice | sampler 选（与 rim_treatment 独立）| Slot D |
| rim_treatment | enum | {red_corner_bumpers, orange_rim_guard_sleeves} | — | choice | sampler 选 | Slot E |
| palette_style | enum | {classic_chrome_red, chrome_orange, chrome_blue, graphite_frame_red, white_coated_green, all_chrome_black}（6）| classic_chrome_red | choice | 仅涂装，不改几何（⑥）| §8.5⑥ |
| basket_length_scale | float | [0.90, 1.15] | 1.0 | independent | 缩放 (B_BACK_X − B_FRONT_X)；采样后 clamp | S1 L58-L59 |
| basket_width_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 B_*_HALF_Y；clamp | S1 L64-L67 |
| basket_wall_height_scale | float | conditional | 1.0 | conditional | 范围随 basket_form：standard [0.92,1.10]、deep [1.05,1.28]（贴 S2 back_top≈0.84）、straight [0.92,1.10]；缩放 (B_*_TOP_Z − B_*_BOT_Z) | S1 L60-L63 / S2 L60-L61 |
| taper_ratio | float | derived | — | equation | `= 1.0`（standard/deep 保 parent taper）/ `≈0`（straight_wall：B_FRONT_HALF_Y←B_BACK_HALF_Y、front_top←back_top）；由 basket_form 派生，不独立采样 | S1 L64-L67 |
| wheel_radius_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 WHEEL_RADIUS；clamp | S1 L70 |
| chassis_z | float | derived | — | equation | `CHASSIS_Z = f(WHEEL_RADIUS)` 使四轮触 z≈0（wheels_touch_floor，|z|≤0.012）| S1 L78, L521-L523 |
| track_half_scale | float | [0.94, 1.08] | 1.0 | independent | 缩放 TRACK_HALF_Y | S1 L77 |
| seat_flap_len_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 flap_len | S1 L485 |
| (—) | constraint | — | — | inequality | **童座折下留篮内**：flap 全折(q≈1.5)后 AABB 须在 basket XY 包络内且顶 ≤ B_BACK_TOP_Z（S2 `seat_flap_fold_clean_in_deep_basket` L826-L838）；违反→回缩 seat_flap_len_scale | S2 L826-L838 |
| (—) | constraint | — | — | inequality | **把手 clear 折下童座**：q≈1.5 时 handle↔flap z-gap ≥0.010（S4 `expect_gap` L831-L838）；违反→抬 htz/回缩 | S4 L831-L838 |
| (—) | constraint | — | — | inequality | **前面板 clear 轮与折板**：front_ad_panel 底 z > wheel_top+0.10 且 x 分离折下 flap（S(front_ad) L925-L962）；仅 front_face=front_ad_panel 时激活（conditional）| S(front_ad) L925-L962 |
| (—) | constraint | — | — | inequality | **下层甲板 clear 轮**：shelf 底 z > 2·WHEEL_RADIUS+0.02 且 |shelf_y| ≤ TRACK_HALF_Y+WHEEL_WIDTH/2+0.02（S3 `shelf_above_wheels`/`shelf_inside_wheel_footprint_y` L797-L816）| S3 L797-L816 |
| (—) | constraint | — | — | inequality | **护条 clear 轮 & outboard 童座**：rim guard 底 z > wheel_top+0.10、后段内缘 Y outboard 于 flap Y（S6 L810-L897）；仅 rim_treatment=orange_rim_guard_sleeves 时激活（conditional）| S6 L810-L897 |

连续尺寸采样契约：先采 independent 主尺度（length/width/wheel_radius/track/flap_len）→ 按 equation 派生（chassis_z from wheel_radius、taper_ratio from basket_form）→ conditional 解析 basket_wall_height_scale 范围（依 basket_form）与 D/E 的 clearance 不等式（依所选装饰）→ inequality 投影/回缩（童座折下留篮内、把手/面板/护条/甲板 clearance）。全部在 `resolve_config` 求解，不留到 builder。

## Multiplicity / Copy Logic

- **脚轮 ×4：固定复制，非采样 multiplicity 轴。** 4 只脚轮（`add_caster` 调 4 次，cx∈{REAR_AXLE_X,FRONT_AXLE_X}×cy∈{±TRACK_HALF_Y}，S1 L631-L634）是购物车的**结构常量**：参考图与全部 6 样本均为 4 轮，真实超市购物车永远 4 轮（增减轮数即不再是购物车 / 飘向平台车）。故**不暴露 `caster_count`**、不做加权 N 采样；模板固定发射 4 组 `caster_yoke_{i}`/`caster_wheel_{i}` 与对应 8 根 CONTINUOUS 关节（4 yaw + 4 roll）。
- **无其它模板级复制数量逻辑。** 篮体密竖丝 / 网底格数（n_side/n_end/n_floor）与下层丝密度属 ④ 表面装饰密度，不作为独立 multiplicity 轴（source map 已把 `var_wire_density_high` 判为过弱并删除）；核心结构由固定 named slots（A–E）+ 固定 ×4 脚轮表达。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type/来源 · 或 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 无 | 6 样本共享同一 part-joint 运动学图（basket 根 + 5 parallel children + 固定 ×4 脚轮链），9 根非 fixed 关节集恒定（source map motion-safety：URDF 对比确认同 9 根）。5 REDO fork 只改固定模块 / 形态 / 装饰，**不加不减会动的 part**。故无 ① 变化轴 |
| └ multiplicity | 同构件 ×N | 无 | 见 §8：脚轮固定 ×4（结构常量，非采样轴）；无其它复制数量逻辑 |
| ② 关节类型 | 图不变，某条边换 type/轴 | 无 | 全部关节 type/axis 恒定（seat-flap REVOLUTE y、4×yaw CONTINUOUS z、4×roll CONTINUOUS y）；motion-safety 硬契约禁止改关节 origin/axis/limit。source map 记 `var_front_swivel_rear_fixed`（前万向后固定）被删（运动风险），不引入 ②。故无 ② 轴 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 的可识别几何形态原型 | **有** | **Slot A basket_form（登记进 slot_choices）**：standard_tapered_basket（Volumetric Envelope，forked_anchor S1）、deep_family_basket（Volumetric Envelope，forked_anchor S2）、straight_wall_basket（Planar Boundary，world_knowledge_extrapolation，anchors S1+S2）。**附加** Slot B lower_deck 也承载次级形态（flat_wire_tray S1 / walled_cargo_basket S3，平托↔有壁货篮）。≥3 可识别篮体原型，均标 form_subtype |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | **有** | **Slot D front_face**（plain_front S1 / front_ad_panel，record_only+world_knowledge_extrapolation，前壁派生面板 S(front_ad) L273-L381）+ **Slot E rim_treatment**（red_corner_bumpers S1 / orange_rim_guard_sleeves，forked_anchor S6 L223-L252，顶 rim 派生护条+角帽）+ handle 防滑脊/侧夹（S4）。装饰几何均由宿主表面（前壁 / 顶 rim / 把面）逐-z 派生、随 ③③⑤ 共形嵌入（派生顺序 ③→⑤→④），不悬空 |
| ⑤ 尺寸/行程 | 离散不变，只连续改尺寸/比例/行程 | **有** | 关键比例（见 §7）：basket_length_scale[0.90,1.15]、basket_width_scale[0.90,1.12]、basket_wall_height_scale（conditional 依 form，deep 到 1.28）、wheel_radius_scale[0.92,1.10]、track_half_scale[0.94,1.08]、seat_flap_len_scale[0.90,1.10]。**关节运动包络 + motion_test_plan**：(a) `basket_to_seat_flap` REVOLUTE axis=(0,−1,0)、折下方向 +q、[0, 1.5] rad —— targeted `ctx.pose({seat:1.5})` 验折下顶落 & 前伸 & **留篮内/不撞把手/不撞前面板**（S2 L826-L838、S4 L831-L838、S(front_ad) L945-L962）；(b) `caster_spin_{i}` CONTINUOUS（整圈）—— `ctx.pose({spin0:0.6})` 验原地自转 moved<1e-4（轴过轮毂，S1 L780-L788）；(c) `frame_to_caster_yoke_{i}` CONTINUOUS（整圈 yaw）—— 轮组绕 kingpin 360° 不撞底架。需 sampled collision + targeted pose 覆盖 open(q=1.5)/closed(q=0) 童座 + spin/yaw 姿态 |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | **有** | 材质大类：metal(铬丝/铬架/钢脚轮/rim) + plastic(把手/角保/护条/面板 molded) + rubber(黑胎)。配色 ≥6：classic_chrome_red（铬+红+黑胎）、chrome_orange（铬+橙 molded+黑胎）、chrome_blue（铬+蓝 molded，取 S(front_ad) panel_blue 0.12/0.32/0.68）、graphite_frame_red（石墨粉涂丝架+红塑）、white_coated_green（白粉涂丝+绿塑，园艺卖场车）、all_chrome_black（铬+黑 molded+黑胎）。材质大类覆盖 ≥ ceil(0.5×6)=3（metal+plastic+rubber 均出现，✔）|

**收尾自检**：0-9 seed 渲染须肉眼可见——三种篮体形态（标准锥/深家庭/直壁）拉得开、下层平托↔有壁货篮可辨、把手三型（红杆/人机 sleeve/U-loop）可辨、前面板与橙护条贴宿主面不悬空、童座 q=0↔1.5 全程不穿模、脚轮原地自转 + 360° 万向、6 配色 metal/plastic/rubber 三大类都出现。


## 拓扑多样性审计

总组合数：basket_form(3) × lower_deck(2) × handle_form(3) × front_face(2) × rim_treatment(2) = **72** 个离散拓扑组合（脚轮固定 ×4 不计入；palette 6 与连续 scale 不计入结构 distinct）。

理由：5 个登记 slot 每个候选均可达且 ≥2 distinct（A=3、B=2、C=3、D=2、E=2），无单候选 slot（B/D/E 的 2-candidate 已在 §4 记 degrade 理由：④装饰轴 / 源池仅两态 / 甲板恒存），sampler 对每 slot 独立加权采样，5 slot 互相兼容（无互斥 gate，D/E 独立组合），reachable 全覆盖。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 用 deterministic RNG(seed) 对 5 个 slot 各独立加权采样（basket_form 三态近均匀；lower_deck / front_face / rim_treatment 各 ~50/50；handle_form 三态近均匀），再采 palette_style（6 态均匀）与连续 scale（§7 契约：independent→equation→conditional→inequality）。compatibility：无非法组合（5 slot 全兼容），仅 conditional clearance 不等式在 D=front_ad_panel / E=orange_rim_guard / basket_form=deep 时收紧 seat_flap_len_scale / htz / shelf_z（回缩而非拒绝，尽量不丢组合）。seed=0 不特殊。random sweep：seeds 0-49 首轮、0-999 成熟审计。
Topology target：1000-seed slot choice tuple distinct 上限 = 72（本类别离散结构轴的天花板）。**低于富类别建议 300 的理由**：本小类是**单骨架、单关节拓扑的形态主导物**——6 个采纳样本共享同一 part-joint 图与同一 9 根非 fixed 关节集（source map motion-safety 明确禁止新增/改关节），真实结构变化轴仅限 ③ 篮体形态 + 下层甲板 + ④ 前面板 / 边缘护条 + 把手形态；脚轮 ×4 为结构常量。72 已穷尽 source-backed + 单条 world-knowledge 形态外推的合法离散组合；进一步"变多样"只能靠连续 scale（§7 6 个 scale）与 palette（6）在每个拓扑内产生视觉分化，而非虚构新拓扑。1000-seed 的视觉 distinct 远高于 72（72 拓扑 × 6 palette × 连续 scale），但结构 distinct 天花板即 72，符合"低于 300 需说明类别/兼容约束原因"。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
Controlled local parameterization：basket_length_scale / basket_width_scale / basket_wall_height_scale(conditional) / wheel_radius_scale / track_half_scale / seat_flap_len_scale（范围/clamp/derived 见 §7）；chassis_z=f(wheel_radius) 保四轮触地，taper_ratio=f(basket_form)，全部在 `resolve_config` 求解，不破坏 InterfaceSpec/MatingContract（底 rim 焊接、立柱 clamp、铰线、kingpin bolt、轮毂捕获）与固定 ×4 脚轮。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 5 slot 各独立加权采样（basket_form/handle_form 三态近均匀；lower_deck/front_face/rim_treatment ~50/50）+ palette(6) + 连续 scale；顺序 independent→equation→conditional→inequality | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | 全兼容无互斥；conditional clearance（deep basket / front_ad_panel / orange_rim_guard）收紧连续 scale 回缩，不丢离散组合；fallback：回缩仍冲突则 clamp htz/shelf_z | 无悬空 / 无穿模 / 关节轴 & range / 童座 closed+open pose / 脚轮 360° / 装饰 clear 轮与折板 |
| controlled local variation | §7 的 6 个 scale + 2 个 derived + 5 条 inequality；全在 resolve_config clamp/派生 | 比例变化不破接口 / clearance / 关节 origin / 类别身份 |
| regression overrides | none（首版不需要；如后续 sweep 暴露特定失败 seed 再稀疏加，记 seed+理由）| 仅已知失败回归 |
| random sweep | seeds 0-49 首轮，0-999 成熟审计 | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A basket_form（③）| 3 | yes | yes | Volumetric×2 + Planar×1 |
| B lower_deck | 2 | yes | no | 源池仅两态（平托/有壁货篮），甲板恒存，§4 记理由 |
| C handle_form | 3 | yes | yes | forked×2 + world_knowledge U-loop×1 |
| D front_face（④）| 2 | yes | no | 装饰轴 plain/ad_panel，§4 记理由；与 E 独立组合 |
| E rim_treatment（④）| 2 | yes | no | 装饰轴 角保/满护条，§4 记理由；与 D 独立组合 |

## Validator

- slot_choices_for_seed 返回已实现的 module 名（A/B/C/D/E 各自）
- config_from_seed 对所有 ordinary seed 用 deterministic procedural sampling（seed=0 不特殊）
- compatibility 无非法组合；conditional clearance 只收紧连续 scale（回缩），不删离散组合
- regression overrides 为空（或稀疏且注明理由）
- 主 seed domain 不是小型 curated / modulo 表
- 连续 scale（length/width/wall_height/wheel_radius/track/flap_len）clamp，且 equation(chassis_z, taper_ratio) / inequality(童座留篮内、把手&面板&护条&甲板 clearance) / conditional(wall_height 范围、装饰激活) 全在 resolve_config 求解，不留 builder 失败
- 关键 InterfaceSpec/MatingContract 存在：底 rim 焊接(basket↔underframe)、后角立柱 clamp(basket↔handle)、后内铰线(seat flap REVOLUTE origin z=0.5)、kingpin bolt(frame↔yoke)、轮毂捕获(axle↔rim scoped allow_overlap)
- 关键关节 type/axis/range：seat-flap REVOLUTE axis|y|=1 limit[0,1.5]；4×frame_to_caster_yoke CONTINUOUS z；4×caster_spin CONTINUOUS y（origin 过轮毂 → 原地自转 moved<1e-4）
- 脚轮固定 ×4：4 组 yoke/wheel + 8 根 CONTINUOUS 关节，命名 caster_yoke_{i}/caster_wheel_{i}/frame_to_caster_yoke_{i}/caster_spin_{i}
- 装饰 clearance：front_ad_panel 与 orange_rim_guard 底 z > wheel_top+0.10；护条内缘 outboard 童座 Y；下层甲板底 z > 2·wheel_r+0.02 且在 wheel footprint 内
- 四轮触地：|wheel_bottom_z| ≤ 0.012（chassis_z=f(wheel_radius)）

## Reject cases

- 改动 9 根非 fixed 关节的任一 origin/axis/limit，或新增/删除会动的 part（违反 motion-safety 硬契约；如把某轮改固定、给篮加会动侧门）
- 脚轮数偏离 4（增减轮 / 前万向后固定 → 飘向平台车，source map 已删 `var_front_swivel_rear_fixed`）
- caster_spin origin 不过轮毂中心 → 自转不在原地（moved≥1e-4，clean-origin gate 失败）
- 童座翻板 q=1.5 折下时穿模篮壁 / 把手 / 前广告板（未在 resolve_config 回缩 seat_flap_len_scale / htz）
- 前广告板或橙护条悬空、或伸到轮上方 <0.10 撞轮、或护条内缘压住童座 Y 范围
- 下层甲板落到轮上（shelf 底 z ≤ 2·wheel_r+0.02）或伸出 wheel footprint
- 把 basket 做成实心 / 非锥形 / 无开口（丢丝篮身份）、或把下层甲板去掉（丢购物车下托身份）
- 用小型 curated / modulo 表当主 seed domain，或只靠连续 scale / palette 撑多样性（③ 形态家族必须离散出现）
- straight_wall_basket 改到丧失购物车语义（如做成平板无壁 → 飘向平台车）

## 与相邻类别的边界

- 不该混入 **平台/台车 `caster_trolley`**（同名邻类，本仓库已有平台 trolley 模板）：平台车是**平甲板 / 网架平板 + 竖直推把**、无锥形丝篮、无童座翻板、货物摊在平面上；本类别核心身份是**锥形开口丝篮**（可嵌套）+ 后内折叠童座 + 斜后推把。straight_wall_basket candidate 须保留篮壁与开口，不得退化为平板。
- 不该混入 **手提购物篮 `shopping_bucket`**：手提篮**无轮、无外张底架、无脚轮**，靠 bail 提把手拎；本类别是**轮式**（4 万向脚轮 + 铬管底架），落地推行。
- 不该混入 **行李箱 `suitcase`**：suitcase 是带轮拉杆的封闭硬壳箱（升降拉杆 + 盖体开合）；本类别是开口丝篮、无拉杆、无壳盖开合，脚轮为万向非定向行李轮。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。单骨架形态主导物：③ basket_form（3，登记 slot）+ B lower_deck（2）+ C handle_form（3）+ ④ D front_face（2）+ ④ E rim_treatment（2）= 72 离散组合 + 6 palette。脚轮固定 ×4（非采样 multiplicity）。9 根非 fixed 关节 motion-safety 硬契约（禁改 origin/axis/limit）。72 <300 已在 §9 说明（单关节拓扑、source 约束）。**待模板阶段落实**：(1) slug 加入 `cli/template.py` TEMPLATE_REGISTRY allow-list；(2) resolve_config 求解 §7 全部 equation/inequality/conditional；(3) 童座 open/closed + 脚轮 spin/yaw 的 targeted pose + sampled collision。**开放问题**：B/D/E 各 2 candidate（已记 degrade 理由，符合"折入/装饰轴"例外）；straight_wall_basket 与 loop_bar_handle 为 world_knowledge_extrapolation，需 sweep + reviewer 复核类别忠实（勿飘向平台车 / 保 FIXED 把接口）。|

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/E + 脚轮 + root | standard_tapered_basket / flat_wire_tray / red_bar_handle / red_corner_bumpers / caster ×4 | rec_chrome-...-tapered-_..._58ed850d | L56-L634 | 全 skeleton + 基线各 slot + 固定 ×4 脚轮链 + 全部接口/关节 |
| S2 | A | deep_family_basket | rec_caster_trolley2_redo_deep_family_basket | L60-L61, L217（+ 测试 L702-L722, L826-L838）| 深家庭篮 envelope + 童座留篮内约束 |
| S3 | B | walled_cargo_basket | rec_caster_trolley2_redo_lower_basket_visible | L405-L528（+ 测试 L797-L816）| 有壁下层货篮 + 甲板 clear 轮约束 |
| S(front_ad) | D | front_ad_panel | rec_caster_trolley2_redo_front_ad_panel | L273-L381（+ 测试 L925-L962）| 前壁派生广告面板 + 面板 clear 轮/折板约束 |
| S4 | C | ergonomic_sleeve_handle | rec_caster_trolley2_redo_handle_sleeves | L285-L372（+ 测试 L831-L838）| 人机 sleeve 把 + 把手 clear 折板约束 |
| S6 | E | orange_rim_guard_sleeves | rec_caster_trolley2_redo_rim_guard_bumpers | L175, L223-L252（+ 测试 L810-L897）| 顶 rim 派生橙护条+角帽 + 护条 clear 轮/outboard 童座约束 |

## 模板实现备注（可选）

- 深读参考模板（按 slot graph / 运动拓扑 / 接口选，不按类别名）：`caster_trolley`（同 4 脚轮 continuous yaw+roll、FIXED child corner-origin，注意 memory 记的 corner-origin 悬空坑）、`fence_cascade`（parallel-children + 加权采样范式）、`container_locker`（parallel slot 装饰面板 boolean 成本坑，本类别丝篮竖丝密度同样是 compile 成本大头 → 可 coarsen n_side/n_end 或缓存 tube mesh）。
- **compile 成本**：basket 密竖丝 + 网底 + 下层丝网是 tube mesh 大户（parent 单台数百根 tube）。sweep 前考虑降 n_side/n_floor 或跨 seed 缓存 `_tube` 结果，避免 §load 下 compile-sweep flaky（见 memory「Compile-sweep flaky under load」，验收用 clean sequential foreground）。
- **captured-pin / scoped allow_overlap**（复刻 parent，5 fork 均保）：每轮 axle↔rim（`elem_a="axle"` `elem_b="rim"`）、每 yoke↔frame（kingpin bolt）、handle↔basket（立柱 clamp，S4 用 `elem` 级 top_rim↔handle_post_{p,n}）、bumper↔basket、underframe↔basket、flap↔basket。装饰组合时（D/E）新增的面板/护条↔basket 也需 scoped allow_overlap（贴面嵌入）。
- **stem / registry**：文件 stem `shopping_cart`，registry key `Urban_Environment_Caster_Trolley2`（memory「arti-template new slug registry」：新 slug 必须加进 `cli/template.py` TEMPLATE_REGISTRY，仅 importlib 文件名自动发现不够）。
- **basket_form=straight_wall / handle_form=loop_bar** 为 world_knowledge_extrapolation：实现须保同 part tree / 同 primitive / 同接口（straight 仍用 `_side_pt`/`_end_pt`/`perimeter_loop` 只令 taper→0；loop 仍是 `push_handle` FIXED + 后角立柱），过 Rule 4/5 sweep + reviewer 复核忠实。
