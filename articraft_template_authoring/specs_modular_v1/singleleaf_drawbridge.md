# Single-leaf Drawbridge Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `singleleaf_drawbridge` |
| template path | `agent/templates/singleleaf_drawbridge.py` |
| test path (optional) | `tests/agent/test_singleleaf_drawbridge_template.py` — 可选回归网，默认被 pytest 排除；验收以 compile-sweep 为准 |
| stage | `APPROVED` |
| status | `APPROVED` |
| __modular__ | `True` |
| pattern | `mixed`（身份永远是 `fixed_support → bridge_leaf` 单 REVOLUTE；hinge_bearing 可选引入独立 FIXED bearing parts；topside/shore 为 gated baked-visual 扩展） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 41 |
| read_count | 9 |
| read_scope | 41 个 5 星全部 grep 抽取（part 列表、每个 joint 的 name/type/parent/child/axis/limit、几何 primitive 计数、counterweight/tail/torus/cadquery/lathe/extrude/separate-bearing-part/approach/receiving/water/tower/trunnion/sleeve/collar/bore/seat 关键字矩阵）；其中 9 个跨结构全谱按行精读以采纳可复用源码块：0003（唯一 4-part 独立 bearing）、0004（全尺寸机房塔 + sleeve-over-pin）、5da09783（torus ring + 护栏 leaf）、a9f8a88（完整 bascule：counterweight 尾 + 引桥/受桥/水道/控制塔）、eec982cb（cadquery 镗孔 bearing block + through trunnion）、c5bac345（双塔机房 support_frame）、b800c64e（torus ring + 水道/路缘 shore_frame + 路面车道）、f04c79fe（helper 驱动 premium 道路 bascule + sleeve-over-ring）、303cdd7f（高墩切水面 + 圆柱 bearing housing + trunnion tube） |
| samples_adopted_as_module_sources | 9 |
| samples_read_but_not_adopted | 32（grep 全扫，结构均落在已采纳 9 个的 part-tree / hinge-interface / 扩展骨架谱内；32 个全部确认恰好 1 个 REVOLUTE、axis 几乎全为 `(0,-1,0)`、limit `0.0..~1.05-1.5`、2 part） |

全部 41 个 5 星样本（record_id 去前缀）+ 采纳标注：

- `0003` — **adopted** as source for Slot A.`masonry_abutment` 旁证、Slot B.`box_deck_girder`、**Slot C.`separate_bearing_parts`（唯一 4-part 独立 FIXED bearing 源）**、Slot D.`curb_guard`、Slot E（service cover/edge guard 旁证）
- `0004` — **adopted** as source for Slot A.`twin_tower_machinery`（machinery plinth/tower web/bearing housing/baked hinge pin）、Slot B.`box_deck_girder`（torque beam + 深 girder + cross rib + gusset + diagonal）、**Slot C.`leaf_sleeve_over_support_pin`**、Slot E.`abutment_machinery_house`
- `0005` — read but not adopted, reason: mesh_fg + approach span 的中尺度变体，落在 `masonry_abutment` + `mesh_girder_leaf` + `approach_span` 谱内
- `05c2bb3a` — read but not adopted, reason: 工业安全护栏/止动变体，落在 `box_deck_girder` + `curb_guard` 谱内
- `1489d0c0` — read but not adopted, reason: 成本优化 bore-bearing，落在 `cadquery_bored_shore` / `cylinder_housing` 谱内（hinge bore + approach/receiving）
- `23efc0cd` — read but not adopted, reason: 居中对称基础 shore_frame，`masonry_abutment` 谱
- `2f2abe98` — read but not adopted, reason: 止动 flange + secondary frame lip，`masonry_abutment` + approach 谱
- `2f65bfa3` — read but not adopted, reason: 偏置开口（重侧）变体，仍 2 part 单 revolute
- `303cdd7f` — **adopted** as source for **Slot A.`masonry_abutment`（高墩切水面 + bearing pedestal/side cheek）**、Slot B.`box_deck_girder`（trunnion tube + 主梁 + floorbeam）、**Slot C.`trunnion_tube_in_cylinder_housing`**
- `3efeb52d` — read but not adopted, reason: 止动 flange + 护栏 + 水道，谱内
- `43948793` — read but not adopted, reason: 单大无断板倾向 + extrude，落在 `mesh_girder_leaf` 谱
- `5489089b` — read but not adopted, reason: 户外防风雨密封变体 + mesh，谱内
- `5da097830` — **adopted** as source for Slot A.`torus_ring_road_abutment`（旁证）、**Slot B.`railed_road_leaf`**（护栏 + 栏杆柱 + tread bar）、**Slot C.`trunnion_shaft_through_torus_ring`**、Slot D.`rail_balustrade`
- `6051d7d6` — read but not adopted, reason: 主壳 + 单独 hinge-side 拆分（仍同 part，几何分块），谱内
- `60ebcf76` — read but not adopted, reason: 标准 shore_frame，谱内
- `665801eb` — read but not adopted, reason: approach + tower 中尺度，谱内
- `6de80023` — read but not adopted, reason: 护栏 + approach，谱内
- `75344e31` — read but not adopted, reason: torus ring + 护栏 + mesh，落在 `trunnion_shaft_through_torus_ring` 谱
- `756b2e3e` — read but not adopted, reason: 护栏 + approach，谱内
- `7eeaf5a2` — read but not adopted, reason: cadquery + bore + approach，落在 `cadquery_bored_shore` 谱
- `8864cd20` — read but not adopted, reason: cadquery，落在 `cadquery_bored_shore` 谱
- `8b9957c9` — read but not adopted, reason: **axis `(1,0,0)`** 变体（轴向沿河岸，仍单 revolute），用于参数 `hinge_axis` enum 旁证
- `96ce555e` — read but not adopted, reason: 标准 shore_frame，谱内
- `9840a6d6` — read but not adopted, reason: 桁架 + **counterweight** + approach/water/tower，落在 `bascule_counterweight_leaf` + `channel_water_context` 谱（采纳源以 a9f8a88 为主）
- `9fd6a67d` — read but not adopted, reason: approach 中尺度，谱内
- `a58ddcb8` — read but not adopted, reason: 水道 + seat，谱内
- `a76f28f2` — read but not adopted, reason: **axis `(1,0,0)`** + tower + approach，`hinge_axis` enum 旁证
- `a7b7b477` — read but not adopted, reason: mesh + sleeve + tower + approach，落在 `leaf_sleeve_over_support_pin` 谱
- `a7ed2abc` — read but not adopted, reason: 护栏 + tower + collar，谱内
- `a9f8a883` — **adopted** as source for **Slot B.`bascule_counterweight_leaf`（pivot 后的 counterweight 尾 + 桁架交叉撑）**、**Slot E.`channel_water_context`（water/pier/引桥/受桥/控制塔 baked visuals）**、Slot D.`rail_balustrade`（sidewalk/railing/road line）
- `b800c64e` — **adopted** as source for **Slot A.`torus_ring_road_abutment`（water + side curb + far landing sill + torus ring + backplate）**、Slot B.`railed_road_leaf`（through trunnion shaft + shaft collar + 车道线）、Slot C.`trunnion_shaft_through_torus_ring`、Slot E.`channel_water_context`（旁证）
- `c063ba08` — read but not adopted, reason: approach 中尺度，谱内
- `c2857792` — read but not adopted, reason: approach + collar，谱内
- `c5bac345` — **adopted** as source for **Slot A.`twin_tower_machinery`（drive cabinet + 双塔 cheek/saddle/crown/diagonal brace）**、Slot B.`box_deck_girder`（trunnion arm/neck/trunnion/hub）、Slot E.`abutment_machinery_house`
- `cc0dda9b` — read but not adopted, reason: 最简护栏 shore_frame（upper 1.5 偏大），谱内
- `d3e17d18` — read but not adopted, reason: **counterweight** + 护栏 + tower + approach，落在 `bascule_counterweight_leaf` 谱
- `eec982cb` — **adopted** as source for **Slot A.`cadquery_bored_shore`（mesh_from_cadquery box + cutThruAll + fillet bearing block）**、Slot B.`box_deck_girder`（cross girder + underside rib）、**Slot C.`trunnion_tube_in_cylinder_housing`（through trunnion 被 bore 捕获）**
- `eff8d1e6` — read but not adopted, reason: 护栏 + 大 cylinder 计数，谱内
- `f04c79fe` — **adopted** as source for **Slot A.`torus_ring_road_abutment`（helper `_add_box`/`_add_y_cylinder` + approach slab + side pier + bearing plinth + torus ring + cap pin）**、**Slot B.`railed_road_leaf`（rail post + top rail + trunnion hub + sleeve + hinge transom + lane marking）**、**Slot C.`leaf_sleeve_over_support_pin`（bearing_sleeve 套 bearing_ring）旁证**、Slot E.`approach_receiving_span`
- `f484d3d8` — read but not adopted, reason: **counterweight** + seat，落在 `bascule_counterweight_leaf` 谱
- `f4eecbe2` — read but not adopted, reason: 护栏 + approach + water，谱内

## 核心身份

单叶卷扬/竖旋开启桥（single-leaf drawbridge / bascule）：恰好一个**接地固定支座**（abutment / shore_frame / support_frame / pier base，root part）+ 恰好一片**桥叶/桥面 leaf**，两者只由**一个 REVOLUTE** 铰接。铰轴是水平的、垂直于桥跨方向（本模板把 deck 沿 +Y 铺开、铰轴实现为世界 **`(1,0,0)`** 横向轴，等价于样本里的 transverse 销线），位于支座近岸侧的 trunnion/bearing 销线上。**`0 rad` = 图示水平闭合桥面（即默认静止位 / 缩略图位）**：正角把 leaf **向上抬**（露出航道），负角让 leaf **向下俯**至水平面以下。每 seed 采样 `upper ∈ [+30°, +60°]`（抬起）与 `lower ∈ [-45°, -15°]`（下俯）。wow + 唯一 articulation 就是这片桥面绕销线的上抬/下俯。abutment/塔/护栏/路缘/引桥/受桥/水道/控制塔/counterweight 全部是 baked 进 support 或 leaf 的 `part.visual(...)` 静态几何（41 个样本无一例外，连 counterweight 也是 leaf 上的死 visual），不另起 FIXED 装饰 part——唯一例外是 `0003` 把两侧 bearing 拆成独立 FIXED part（见 Slot C）。

边界：
- 不是双叶/对开 bascule（两片叶各自 revolute 向中央合拢）——本类恰好一片 leaf、一个 revolute。
- 不是平转桥（swing bridge，绕竖直 `(0,0,1)` 轴水平回转）或升降桥（vertical-lift，桥面整体 PRISMATIC 垂直平移）——本类是绕水平轴的 REVOLUTE 上翻。
- 不混入 `barrier_gate`（栏杆道闸：轻杆绕竖直/水平轴抬起拦车，无承重桥面/无 trunnion 销线）。
- counterweight / 引桥 / 受桥 / 控制塔即便造型抢眼，也只是 baked visual，不得各自起独立可动 part。

## 采用源码索引（Adopted Source Index）
| source_id | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|
| S1 | `rec_singleleaf_drawbridge_0003` | `data/records/rec_singleleaf_drawbridge_0003/revisions/rev_000001/model.py:L71-L131`（abutment）/`L133-L176`（**独立 bearing part + 2 FIXED joint**）/`L178-L290`（leaf：trunnion shaft/collar/gusset）/`L292-L305`（revolute） | Slot C.`separate_bearing_parts` 唯一源（4-part + 2 FIXED）；Slot B box deck + side girder ExtrudeGeometry；Slot A masonry 旁证 |
| S2 | `rec_singleleaf_drawbridge_0004` | `model.py:L24-L106`（`_midpoint`/`_distance`/`_rpy_for_z_aligned_member`/`_add_cylinder_member`/`_add_bolt_*` helper）/`L121-L322`（twin-tower support_frame + baked hinge pin/cap）/`L324-L493`（leaf：torque beam/girder/cross rib/gusset/diagonal）/`L495-L508`（revolute）/`L552-L565`（**sleeve-over-pin `allow_overlap`**） | Slot A.`twin_tower_machinery`；Slot B.`box_deck_girder`；Slot C.`leaf_sleeve_over_support_pin`；Slot E.`abutment_machinery_house` |
| S3 | `rec_singleleaf_drawbridge_5da097830be74be1a62dcee585dbdd43` | `model.py:L29-L114`（abutment + `TorusGeometry` bearing ring + pedestal/saddle/tie/gusset）/`L116-L223`（leaf：deck plate + side girder + **guard rail + rail post + tread bar** + hinge shaft/trunnion/lug/web）/`L225-L233`（revolute） | Slot B.`railed_road_leaf`；Slot C.`trunnion_shaft_through_torus_ring`；Slot D.`rail_balustrade`；Slot A torus 旁证 |
| S4 | `rec_singleleaf_drawbridge_a9f8a88394de41ffb8ab36a8330dc07c` | `model.py:L25-L61`（base：water/pier/**approach+receiving deck**/sidewalk/railing/**control tower**）/`L63-L91`（leaf：trunnion + girder + cross brace + **counterweight** baked visual）/`L80-L90`（deck + sidewalk + railing + road line）/`L92-L100`（revolute） | Slot B.`bascule_counterweight_leaf`；Slot E.`channel_water_context`；Slot D.`rail_balustrade` |
| S5 | `rec_singleleaf_drawbridge_eec982cb16564a2a89fb24f834100865` | `model.py:L28-L43`（`cq.Workplane.box().faces(">Y").circle().cutThruAll().edges("|Y").fillet()` + `mesh_from_cadquery`）/`L45-L129`（shore_frame + 镗孔 bearing block + bracket + pad）/`L131-L192`（leaf：through trunnion shaft + cross girder + underside rib + 警示条）/`L194-L202`（revolute）/`L213-L293`（bore 捕获 trunnion 的 `allow_overlap`+`expect_within`+`expect_overlap`） | Slot A.`cadquery_bored_shore`；Slot C.`trunnion_tube_in_cylinder_housing`（bore）；Slot B box girder 旁证 |
| S6 | `rec_singleleaf_drawbridge_c5bac34520c944059512bf4bf86cc9bf` | `model.py:L31-L139`（support_frame：foundation + approach slab + **drive cabinet** + 双塔 cheek/saddle/bearing cap/crown/diagonal brace + Inertial）/`L141-L220+`（leaf：deck + heel deck + girder + crossbeam + trunnion arm/neck/trunnion/hub） | Slot A.`twin_tower_machinery`；Slot B.`box_deck_girder`；Slot E.`abutment_machinery_house` |
| S7 | `rec_singleleaf_drawbridge_b800c64ef1104598b4321f2f3710dba6` | `model.py:L29-L84`（shore_frame：**channel water + side curb + shore abutment + hinge sill + far landing sill** + `TorusGeometry` ring + backplate）/`L86-L138`（leaf：through trunnion shaft + deck panel + road surface + side girder + cross rib + hinge web + **shaft collar** + 车道线）/`L140-L148`（revolute）/`L172-L180`（collar-in-ring `allow_overlap`） | Slot A.`torus_ring_road_abutment`；Slot C.`trunnion_shaft_through_torus_ring`；Slot E.`channel_water_context`旁证；Slot B 车道线 |
| S8 | `rec_singleleaf_drawbridge_f04c79fe3c5740aeba941118a287d30b` | `model.py:L20-L35`（`_add_box`/`_add_y_cylinder`/`_y_cylinder_origin` helper）/`L57-L97`（abutment：approach slab + side pier + bearing plinth/saddle/web + `TorusGeometry` ring + cap pin）/`L99-L162`（leaf：deck slab + road surface + side girder + curb cap + **rail post + top rail** + trunnion hub + **bearing sleeve** + hinge transom + crossbeam + lane marking）/`L175-L183`（revolute） | Slot A.`torus_ring_road_abutment`；Slot B.`railed_road_leaf`；Slot C.`leaf_sleeve_over_support_pin`（sleeve 套 ring）；Slot D.`rail_balustrade`；Slot E.`approach_receiving_span` |
| S9 | `rec_singleleaf_drawbridge_303cdd7f972b4df2b2391183ee43d755` | `model.py:L28-L81`（shore_frame：高 abutment core + **cutwater face** + 双 bearing pedestal + **side cheek** + **圆柱 bearing housing** + bearing cap + Inertial）/`L83-L138`（leaf：leaf surface + deck plate + heel crossbeam + **trunnion tube** + main girder + curb + floorbeam + tip nose）/`L140-L153`（revolute） | Slot A.`masonry_abutment`；Slot C.`trunnion_tube_in_cylinder_housing`（圆柱 housing）；Slot B box girder 旁证 |

## 槽位 + 候选模块表

### Slot A：fixed_support（接地固定支座，root part）

铰链接地侧，承载销线一侧的 bearing/pedestal/cheek 与岸基安装几何，是 root part。命名样本里为 `abutment` / `shore_frame` / `support_frame` / `base`。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `masonry_abutment` | S9 (303cdd7f) / S1 (0003) | 303cdd7f:L28-L81 / 0003:L71-L131 | eligible if compatible | 实心混凝土 abutment core/foundation + 切水面（cutwater）+ 路面/service cover + 双侧 bearing pedestal + side cheek + 圆柱/box bearing housing + bearing cap，全 Box+Cylinder，最经典稳健 |
| `twin_tower_machinery` | S6 (c5bac345) / S2 (0004) | c5bac345:L31-L139 / 0004:L121-L322 | eligible if compatible | foundation + approach slab + drive/power cabinet + **双侧机房塔**（inner/outer web + front/back cheek + saddle pad + bearing cap + tower crown + diagonal brace）+ baked hinge pin/cap，机房卷扬观感，最重 |
| `torus_ring_road_abutment` | S8 (f04c79fe) / S7 (b800c64e) | f04c79fe:L57-L97 / b800c64e:L29-L84 | eligible if compatible | helper 驱动（`_add_box`/`_add_y_cylinder`）approach slab + side pier + bearing plinth/saddle/web + **`TorusGeometry` bearing ring**（mesh_from_geometry）+ cap pin / backplate，道路 bascule 观感 |
| `cadquery_bored_shore` | S5 (eec982cb) | eec982cb:L28-L129 | eligible if compatible | foundation slab + side wall + rear abutment + cross tie + **`mesh_from_cadquery` 镗孔 bearing block**（`box().faces(">Y").circle().cutThruAll().edges(" | Y").fillet()`）+ bracket + pad，唯一 cadquery 源（见说明） |

说明：`cadquery_bored_shore` 有 **3 个 cadquery 5 星源**（eec982cb 已精读采纳；7eeaf5a2、8864cd20 经实测确认同用 `mesh_from_cadquery` 镗孔块；另 1489d0c0 是 bore 但非 cadquery），bearing 表达（实心块镗通孔捕获 through-trunnion）与其余三者（实心 pedestal+housing / torus ring）拓扑/primitive 明确不同，源支撑充分。常见 reference example 可选 `masonry_abutment`（占 5 星多数：shore_frame/abutment 名族）。

### Slot B：bridge_leaf（运动桥叶，child part）

绕销线上翻的活动桥面。结构必含 deck plate + 沿跨向两条 side girder + 近岸 trunnion/hinge 接口几何。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `box_deck_girder` | S9 (303cdd7f) / S2 (0004) / S6 (c5bac345) | 303cdd7f:L83-L138 / 0004:L324-L493 / c5bac345:L141-L220 | eligible if compatible | deck plate/surface + 双深 side girder + heel/hinge cross girder + N 条 floorbeam/cross rib + tip nose + trunnion tube/arm/hub，全 Box+Cylinder 拼装，最稳健 |
| `railed_road_leaf` | S8 (f04c79fe) / S3 (5da09783) / S7 (b800c64e) | f04c79fe:L99-L162 / 5da09783:L116-L223 / b800c64e:L86-L138 | eligible if compatible | deck slab + road surface + side girder + **栏杆柱 + top rail/guard rail** + curb cap + through trunnion shaft + trunnion hub/sleeve + hinge transom + lane marking/tread bar，道路桥观感（含护栏 baked） |
| `mesh_girder_leaf` | S1 (0003) / S2(0004 diagonal) | 0003:L37-L48,L178-L290 | eligible if compatible | deck plate + **`ExtrudeGeometry.centered` 锥形 side girder mesh**（`leaf_side_girder.obj`）+ center/cross stiffener + curb beam + nose beam + trunnion shaft/collar/hinge gusset，挤出梁断面观感 |
| `bascule_counterweight_leaf` | S4 (a9f8a88) / S9(303cdd7f heel) | a9f8a88:L63-L91 | eligible if compatible | trunnion + 双 girder + N 条 cross brace + **pivot 后方 counterweight baked box**（配重尾）+ deck + sidewalk + railing + road line，真 bascule 配重平衡观感（counterweight 仍是 leaf 的死 visual，不另起 part；另有 9840a6d6/d3e17d18/f484d3d8 三个 counterweight 旁证记录） |

### Slot C：hinge_bearing_interface（铰链销线机构 / 是否独立 bearing part，决定 part 数与 captured-pin 重叠声明）

销线上 trunnion 与 bearing 的咬合方式 + 铰轴方向。**唯一改变 part/joint 数的槽位**：`separate_bearing_parts` 引入 2 个独立 FIXED bearing part（4 part / 1 REVOLUTE + 2 FIXED），其余三者均为 2 part / 1 REVOLUTE（bearing 是 support 的 visual，trunnion 是 leaf 的 visual）。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `trunnion_tube_in_cylinder_housing` | S9 (303cdd7f) / S5 (eec982cb) | 303cdd7f:L61-L75,L102-L107 / eec982cb:L28-L43,L131-L137 | eligible if compatible | leaf 上一根全跨 `trunnion_tube`（Cylinder，rpy 沿 Y）插入 support 的圆柱 bearing housing / 镗孔 block，`expect_within`+`expect_overlap` 捕获，2 part |
| `trunnion_shaft_through_torus_ring` | S7 (b800c64e) / S3 (5da09783) | b800c64e:L29-L84,L86-L131 / 5da09783:L59-L76,L189-L202 | eligible if compatible | support 上 `TorusGeometry` bearing ring（+ pedestal/plinth），leaf 上 through `trunnion_shaft` + `shaft_collar` 穿过 ring，collar/shaft-in-ring `allow_overlap`，2 part |
| `leaf_sleeve_over_support_pin` | S2 (0004) / S8 (f04c79fe) | 0004:L250-L281,L398-L413,L552-L565 / f04c79fe:L80-L87,L136-L144 | eligible if compatible | support 上 baked `hinge_pin`/`cap_pin` Cylinder（或 ring），leaf 上 `hinge_sleeve`/`bearing_sleeve` 套住它，sleeve-over-pin `allow_overlap`，2 part |
| `separate_bearing_parts` | S1 (0003) | 0003:L133-L176,L240-L263,L292-L305 | eligible if compatible | **唯一 4-part 骨架**：两侧 `left_bearing`/`right_bearing` 作独立 part 经 2 个 FIXED joint 固定到 support，leaf 上 trunnion shaft/collar 坐入 bearing shell（`expect_contact`），REVOLUTE 仍 support→leaf（见说明） |

说明：`separate_bearing_parts` 仅 1 个直接源（0003），但它是真实世界分体铸造/螺栓轴承的标准设计、并在 5 星样本里实证（实测 0003 = support + 2 独立 bearing + leaf = **4 part**，joint = 1 REVOLUTE + 2 FIXED），拓扑骨架与其余三者（均 2-part）本质不同——保留它是为这一真实结构模式而非凑拓扑计数。最终去留以 compile-sweep + viewer 目检为准：若 0003 式 4-part 在多 seed 上 bearing 漂浮 / trunnion 坐不进 shell，则按经验证据折叠。默认/常见 procedural 权重可偏向最稳健的 2-part `trunnion_tube_in_cylinder_housing`。`hinge_axis` 作派生参数（见参数表），不单列槽位。

### Slot D：leaf_topside_extras（桥面附件，gated baked visuals，无附加 DOF）

leaf 顶面/侧面的可选静态扩展，全部 baked 进 leaf 的 visual，**不引入任何新 DOF / part**。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `curb_guard` | S1 (0003) / S6 (c5bac345) | 0003:L222-L233 / c5bac345:L115-L120 | eligible if compatible | 仅双侧 curb beam / safety stripe（低路缘 + 警示色），最简扩展（默认） |
| `rail_balustrade` | S8 (f04c79fe) / S3 (5da09783) / S4 (a9f8a88) | f04c79fe:L119-L133 / 5da09783:L145-L157 / a9f8a88:L82-L90 | eligible if compatible | 双侧 N 根栏杆柱 + top rail + sidewalk + lane/road line，完整人行护栏栏杆 |
| `tread_underside_ribs` | S3 (5da09783) / S5 (eec982cb) | 5da09783:L166-L187 / eec982cb:L168-L192 | eligible if compatible | 顶面 N 条 tread bar/wearing panel + 底面 N 条 longitudinal/cross rib（结构加劲），工程化裸面观感 |

### Slot E：shore_context（岸基环境，gated baked visuals，无附加 DOF）

support 的可选环境扩展，全部 baked 进 support 的 visual，**不引入任何新 DOF / part**。决定模型是“孤立铰链支座”还是“嵌在岸基/水道里的成桥”。

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `bare_abutment` | S9 (303cdd7f) / S5 (eec982cb) | 303cdd7f:L28-L46 / eec982cb:L45-L93 | eligible if compatible | 仅 abutment core + 路面 apron + hinge sill，无引桥/水道，最简（默认） |
| `approach_receiving_span` | S8 (f04c79fe) / S2(0004) | f04c79fe:L58-L97 / 0004:L121-L163 | eligible if compatible | 近岸 approach slab/curb + 远岸 far landing/receiving sill（+ 路面）baked，成对引桥/受桥跨 |
| `channel_water_context` | S4 (a9f8a88) / S7 (b800c64e) | a9f8a88:L25-L61 / b800c64e:L34-L65 | eligible if compatible | water plane + pier/cutwater + 引桥 + 受桥 +（可选）控制塔，完整水道成桥场景（最重 baked，几何抢眼但全静态） |

## 槽位图（slot graph）
```
pattern = mixed
（恒定身份链 fixed_support → bridge_leaf 单 REVOLUTE；hinge_bearing 决定 2 vs 4 part；topside/shore 为 gated baked-visual 扩展）

   Slot E (shore_context, baked visuals on support)
        ╲  (baked)
         ▼
   [Slot A: fixed_support] ──────●────── REVOLUTE (exactly 1) ──────▶ [Slot B: bridge_leaf]
     (root / grounded)        hinge line                              (child, 上翻 0..~1.05-1.5 rad)
        │                     axis (0,-1,0) 主 / (1,0,0) 旁              ▲
        │ FIXED ×2                                                     │ (baked)
        │ (仅 Slot C = separate_bearing_parts)                          ╱
        ▼                                                  Slot D (leaf_topside_extras, baked visuals on leaf)
  [left_bearing / right_bearing]  ← 独立 FIXED part（4-part 骨架）
        │
        └── Slot C 决定：trunnion_tube_in_cylinder_housing / trunnion_shaft_through_torus_ring /
            leaf_sleeve_over_support_pin（均 2-part，bearing 是 support visual、trunnion 是 leaf visual）
            vs separate_bearing_parts（4-part，多 2 个 FIXED joint）
```
- 身份链恒为 `fixed_support → bridge_leaf`（REVOLUTE，1 个，axis 水平横向）。
- Slot C = `separate_bearing_parts` 时额外引入 2 个独立 FIXED bearing part（part 数 2→4，joint 数 1→3）；其余三者 part 数恒 2、joint 数恒 1。
- Slot D / Slot E 纯 baked visual（含 counterweight / 护栏 / 引桥 / 水道 / 控制塔），不改 part/joint 拓扑。

## 部件（Parts）

### Slot A / module（fixed_support，root）
| part | visual_count | 描述 | 来源 |
|---|---|---|---|
| `fixed_support`（`abutment`/`shore_frame`/`support_frame`/`base`） | ~6-40 | 接地混凝土/钢支座 + bearing pedestal/housing/ring/塔 + 岸基安装几何；落地 root | S9 / S6 / S8 / S5 |

### Slot B / module（bridge_leaf，child）
| part | visual_count | 描述 | 来源 |
|---|---|---|---|
| `bridge_leaf`（`leaf`） | ~10-50 | deck plate + 双 side girder + cross rib/floorbeam + tip nose + 近岸 trunnion 接口几何 +（gated）护栏/counterweight/tread | S9 / S8 / S1 / S4 |

### Slot C / module（hinge_bearing_interface）
| part | visual_count | 描述 | 来源 |
|---|---|---|---|
| `left_bearing` / `right_bearing`（**仅 `separate_bearing_parts`**） | ~4 each | 独立 FIXED bearing part（mount block + bearing shell mesh + cap bolt），固定到 support，leaf trunnion 坐入 | S1 (0003) |
| `trunnion_tube/shaft` + `bearing_housing/ring/sleeve/pin`（其余三者） | n/a（part 内 visual） | trunnion 是 leaf 的 visual、bearing 是 support 的 visual，非独立 part | S9 / S7 / S2 |

## 关节（Joints）
| 关节 | 类型 | parent_slot.part | child_slot.part | axis | range | 描述 | 来源 |
|---|---|---|---|---|---|---|---|
| `leaf_hinge`（`support_to_leaf`/`frame_to_leaf`/`abutment_to_leaf`/`main_trunnion`） | REVOLUTE | A `fixed_support` | B `bridge_leaf` | `(1,0,0)`（横向，deck 沿 +Y）| `lower∈[-0.785,-0.262]`（下俯 −45°..−15°）, `upper∈[+0.524,+1.047]`（抬起 +30°..+60°），`0 rad`=水平 | 唯一主关节：桥叶绕近岸水平销线上抬/下俯 | S1/S2/S3/S4/S5/S7/S8/S9（全 41） |
| `frame_to_left_bearing` / `frame_to_right_bearing` | FIXED | A `fixed_support` | C `left_bearing`/`right_bearing` | n/a | n/a | **仅 Slot C=`separate_bearing_parts`**：两侧独立 bearing 钉死到 support | S1 (0003:L163-L176) |

## 每槽位 Module Emits / Interfaces

本 spec 是 modular v1 早期写法；每个 slot/module 的 emitted parts、internal joints、upstream/downstream interface 已在「槽位 + 候选模块表」「槽位图」「部件（Parts）」「关节（Joints）」和 adopted source index 中给出。模板实现阶段必须把这些信息逐 module 显式落成 `ModuleBuild`、`InterfaceSpec` 和 `MatingContract`，不能只按全局部件清单拼装。

| emits | 描述 | 来源 |
|---|---|---|
| parts / visuals | 以各 slot candidate 的结构特征和「部件（Parts）」表为准；不动装饰优先作为 parent visual | adopted source index + slot table |
| internal joints | 以「关节（Joints）」表和 slot graph 中的 joint type / axis / range 为准 | adopted source index + joints table |
| upstream interface | 来自 slot graph 中的 parent face、hinge line、socket、rail、axis、contact plane 或 support policy | slot graph + source snippets |
| downstream interface | 消费相邻 slot 的 mating point / axis / face；必须在实现中转成真实 `InterfaceSpec` | slot graph + source snippets |
| mating contracts | 每个 separate moving child 和跨 slot 连接必须有可见支撑路径；captured pin / shaft / bearing overlap 需要局部 allow-overlap 理由 | validator + reject cases |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 默认值 | 派生关系 | 来源 |
|---|---|---|---|---|---|
| `support_style` | enum | `masonry_abutment` / `twin_tower_machinery` / `torus_ring_road_abutment` / `cadquery_bored_shore` | `masonry_abutment` | drives Slot A 支座构造 | S9 / S6 / S8 / S5 |
| `leaf_style` | enum | `box_deck_girder` / `railed_road_leaf` / `mesh_girder_leaf` / `bascule_counterweight_leaf` | `box_deck_girder` | drives Slot B 桥叶构造 | S9 / S8 / S1 / S4 |
| `hinge_bearing` | enum | `trunnion_tube_in_cylinder_housing` / `trunnion_shaft_through_torus_ring` / `leaf_sleeve_over_support_pin` / `separate_bearing_parts` | `trunnion_tube_in_cylinder_housing` | drives Slot C：是否独立 bearing part + captured-pin 重叠声明 | S9 / S7 / S2 / S1 |
| `topside_extras` | enum | `curb_guard` / `rail_balustrade` / `tread_underside_ribs` | `curb_guard` | drives Slot D（baked，无新 DOF） | S1 / S8 / S3 |
| `shore_context` | enum | `bare_abutment` / `approach_receiving_span` / `channel_water_context` | `bare_abutment` | drives Slot E（baked，无新 DOF） | S9 / S8 / S4 |
| `hinge_axis` | enum | `transverse`（v1 唯一采样，本模板实现为世界 `(1,0,0)`，deck 沿 +Y）/ `alongshore`（v1 暂缓，见实现备注）| `transverse` | revolute.axis；横向水平销线（实测 **39** 个 transverse，2 个 8b9957c9/a76f28f2 用 alongshore——后者均 read-but-not-adopted，0 行 adopted 源码） | 全样本 / 8b9957c9 / a76f28f2 |
| `leaf_open_upper` | float | `+0.524 - +1.047` rad（抬起 +30°..+60°） | `1.047`（+60°） | revolute upper；`0 rad`=水平闭合位，正角向上抬 | 用户指定（向上最多 60°） |
| `leaf_open_lower` | float | `-0.785 - -0.262` rad（下俯 −45°..−15°） | `-0.524`（−30°） | revolute lower；负角向下俯至水平面以下 | 用户指定（向下最多 45°） |
| `span_length` | float | `0.72 - 12.0`（leaf 跨长，模型量级随 scale 大幅变化） | sampled | leaf deck 长 = span_length；tip nose 在其末端 | 0003(0.72)/303cdd7f(11)/f04c79fe(12) |
| `deck_width` | float | `0.30 - 4.3` | sampled | leaf 宽；与 support bearing 间距协调 | S9 / S8 / S3 |
| `bearing_track` | float | derived | derived | 两侧 bearing 的 y 间距 ≈ deck_width 内缩；trunnion 销线全跨长由此派生 | S9 / S2 / S8 |
| `trunnion_radius` | float | `0.05 - 0.5` | sampled | trunnion shaft/tube 半径 < bearing bore/ring 内径（留 press-fit） | S9 / S5 / S7 |
| `cross_rib_count` | int | `3 - 8` | sampled | leaf 底面 floorbeam/cross rib 段数 | S9(5)/S2(6)/S8(7) |
| `rail_post_count` | int | `5 - 8`（仅 `rail_balustrade`/护栏） | sampled | 护栏柱数 | S8(8)/S3(5) |
| `has_counterweight` | bool | `true` ⇔ `leaf_style=bascule_counterweight_leaf` | `false` | pivot 后 baked 配重 box（非独立 part） | S4 / 9840a6d6 / d3e17d18 / f484d3d8 |
| `heel_fraction` | float | `0`（无配重）/ `0.2 - 0.5`（`bascule_counterweight_leaf`，提议范围待 sweep 调） | derived | 仅 counterweight：pivot 后方配重尾长 = `span_length · heel_fraction`；deck 前伸段仍 = `span_length`（pivot→tip），pivot 落在 deck 与配重尾交界；leaf 总长 = `span_length·(1+heel_fraction)`，闭合位 deck 前段须对齐 support 岸基路面（closed-seam） | S4 |

## Multiplicity / Copy Logic

- 无模板级复制数量逻辑：核心结构由固定 named slots 和 gated module-local fixed copies 表达，不暴露全局 `*_count` 作为主拓扑采样轴。
- 若某个 module source 内部包含固定成对、环形阵列或若干重复 visual/part，模板实现应把它保留为 module-local construction，并使用稳定命名；不得把未审核的可变复制数量加入 seed domain。
- 未来若要把固定重复结构升级为可变 multiplicity，必须补充来源、N_range、placement、joint policy、regression seeds 和 reviewer 审核记录。

## 拓扑多样性审计

总组合数（笛卡尔积）：A(4) × B(4) × C(4) × D(3) × E(3) = **576**。


理由：仅看**改变 part/joint 拓扑骨架**的维度就足够。Slot C 直接劈出两类骨架——`separate_bearing_parts`（4 part = support + leaf + 2 bearing，joint = 1 REVOLUTE + 2 FIXED）vs 其余三者（2 part，1 REVOLUTE）。再叠加：(1) Slot A 四种支座（box 实心 / 双塔机房 / torus-ring / cadquery 镗孔块——不同 primitive 家族与 visual 数量级），(2) Slot B 四种桥叶（box girder / 护栏路桥 / extrude-mesh 梁 / counterweight bascule——其中 `bascule_counterweight_leaf` 多一组 cross-brace + 配重几何块，`mesh_girder_leaf` 用 ExtrudeGeometry mesh 而非 Box），（注：`hinge_axis` 的 alongshore 变体 v1 暂缓采样，不计入此处多样性——见参数表与实现备注）。仅 C(4) 的“2-part vs 4-part”× A 的四种支座家族约给出 ≥8 个可区分的 part/visual-tree 骨架；叠加 B/D/E 的 baked-skeleton 变化后离散组合达 576，远超 10。每个槽位候选数均 ≥3。

每槽位候选数：
| slot | candidate_count | 是否 ≥3 | 备注 |
|---|---|---|---|
| Slot A fixed_support | 4 | yes | cadquery 有 3 个 5 星源（eec982cb 采纳 + 7eeaf5a2/8864cd20 实测确认）|
| Slot B bridge_leaf | 4 | yes | counterweight 源 1 直接 + 3 旁证 |
| Slot C hinge_bearing_interface | 4 | yes | separate_bearing_parts 仅 1 源（唯一 4-part 骨架，必保留） |
| Slot D leaf_topside_extras | 3 | yes | baked，无新 DOF |
| Slot E shore_context | 3 | yes | baked，无新 DOF |

### Procedural Sampling / Sweep Plan

seed_domain_policy：procedural_first。`config_from_seed(seed)` 对普通 seed 使用 deterministic procedural sampling；`seed=0` 不特殊，不作为 anchor 或 reference seed。Sampling 先选择上游结构槽，再从 compatible 下游 candidate 集合中选择 module / multiplicity / module-local variant。

Compatibility matrix / gating：以「槽位图」「每槽位 Module Emits / Interfaces」「Validator」中定义的接口、joint 轴、支撑面、range 和互斥关系为准；不兼容组合必须在 sampler 或 `resolve_config` 中降级、重采样或拒绝，不能让 builder 后期失败。

Regression overrides：默认无。若未来 sweep 发现稳定失败组合，或 reviewer 指定固定回归样本，可以添加少量显式 regression seed，但必须写明 seed、组合和原因；不得用小型 curated / modulo 表作为主 seed domain。

Random sweep / viewer plan：首次模板验收跑 `uv run articraft template sweep-pipeline <slug>`，依赖 0、0-4、0-19、0-49 的 cumulative random seeds 检查 build、MatingContract、joint origin / axis / range、support、collision 和 。机械通过后 viewer 目检一小批随机 seed，重点看类别身份、比例、closed pose、bulky module、optional moving child、max multiplicity、captured-pin / bearing / hinge / rail 接口。


## Validator（author_run_tests 必须覆盖的点）
| 检查项 | 标准 |
|---|---|
| identity | 恰好一个 root `fixed_support` + 一个 `bridge_leaf`；二者由 exactly one REVOLUTE 相连 |
| revolute count | `len([a for a in articulations if a.type==REVOLUTE]) == 1`（唯一主关节） |
| part count | 2 part（`hinge_bearing≠separate_bearing_parts`）或 4 part（support + leaf + 2 bearing，含恰好 2 个 FIXED `frame_to_*_bearing`，`separate_bearing_parts`） |
| hinge axis | `axis == (1,0,0)` 且水平横向（deck 沿 +Y）；revolute.origin 落在销线中心、贴近 leaf trunnion 与 support bearing 几何（fail_if_articulation_origin_far_from_geometry） |
| motion range | `0 rad`=水平闭合位（默认静止位）；`upper ∈ [+0.524,+1.047]`（抬起 +30°..+60°）且 `lower ∈ [-0.785,-0.262]`（下俯 −45°..−15°），`lower < 0 < upper` 跨水平双向 |
| closed seam | 水平位（pose=0）leaf deck 与 support 路面 apron 在销线处沿桥跨方向几乎对齐/小 gap（`expect_gap`/`expect_overlap` 跨缝宽度匹配），deck 不穿透 support |
| trunnion captured | trunnion shaft/tube/collar 与 support bearing housing/ring/pin 共轴咬合（`expect_within` xz 居中 + `expect_overlap` 沿轴向穿过 / `separate_bearing_parts` 用 `expect_contact` 坐入 shell）；press-fit 用 `allow_overlap` 声明 |
| leaf lifts up | pose=upper 时 leaf tip/nose AABB 顶 Z 抬升量 `Δz ≥ 0.6 · span_length · sin(upper)`（几何下界；upper、span 均已知，对 span=0.72 与 span=12 等量级自适应）且 tip 沿 Y 朝销线回退（`Δy < 0`），不与 support/水道实体非预期穿模；pose=lower 时 leaf tip 下俯至水平面以下（Δz<0） |
| grounding | `fixed_support` 落地（最低面 z≈0 或基础块落地），leaf 闭合位坐落在 bearing 销线高度，不漂浮 |
| no floating | bearing（独立或 visual）、counterweight、护栏、引桥、水道、控制塔全部 baked 进 support/leaf 或 FIXED；无悬空装饰 part |
| baked-not-part | counterweight / 引桥 / 受桥 / 控制塔 / 护栏 均为 `part.visual(...)`，绝不另起独立 part 或 FIXED 装饰件（Slot C 的 bearing 是唯一允许的独立 FIXED part） |

## Reject cases（必须能识别并拒绝）
- 无 leaf（只有支座 + 静态桥面），或 leaf 用 FIXED/PRISMATIC/CONTINUOUS 而非有限 REVOLUTE 上翻。
- ≥2 个 REVOLUTE（双叶对开 / 串联铰）或 revolute 轴竖直 `(0,0,1)`（那是平转桥 swing bridge）。
- 桥叶整体 PRISMATIC 垂直平移（vertical-lift bridge），无绕销线转动。
- revolute origin/axis 不在 leaf trunnion 与 support bearing 的共同销线上，leaf 绕错误中心摆动。
- trunnion 与 bearing 不共轴/不咬合（trunnion 飞在 bearing 外、或穿模未声明 `allow_overlap`）。
- `separate_bearing_parts` 声称独立 bearing part 却不 FIXED 到 support（bearing 漂浮），或反之把 bearing 该是 visual 时拆成无谓 FIXED part。
- 闭合位 leaf 不与岸基路面对齐（悬在半空 / 跨缝处投影不接续 / 穿透 support）。
- counterweight / 引桥 / 受桥 / 控制塔 / 护栏 被做成独立可动 part 或 FIXED 装饰件（违反“不动就不是 part”）。
- motion range 不真实（`0 rad` 不是水平闭合位；upper 抬起 <+30° 几乎不开或 >+60° 过冲翻折；lower 下俯超过 −45°）。
- 把栏杆道闸（barrier_gate）、平转桥、升降桥、双叶 bascule 硬塞进本模板。

## 与相邻类别的边界
- vs `barrier_gate`（栏杆道闸）：本类是承重桥面绕 trunnion 销线上翻、有 deck/girder/bearing 全套结构；道闸是轻杆抬起拦车、无承重桥面、无 trunnion 销线。
- vs `revolving_door` / swing bridge（平转桥）：那些绕**竖直** `(0,0,1)` 轴回转；本类绕**水平横向**轴上翻。
- vs vertical-lift bridge（升降桥）：桥面整体 PRISMATIC 垂直平移；本类是 REVOLUTE 上翻，无移动副。
- vs 双叶 / 对开 bascule：那是两片 leaf 各一 revolute 向中央合拢；本类恰好一片 leaf、一个 revolute。
- vs `crane_tower` / 起重臂：那些是多段串联 revolute 的 reach 臂链；本类 exactly one revolute、无连杆链。
- 同类内 scope（孤立铰链支座 vs 嵌岸基成桥 vs 水道控制塔成桥）用 `shore_context` gate 区分，不把水道/控制塔几何塞进默认 `bare_abutment` 分支。

## 模板实现备注（可选）
- Slot A/B/E 共享 S2/S8 的几何 helper：`_add_box` / `_add_y_cylinder`（local-Z cylinder 旋到世界 Y 沿销线）/ `_add_cylinder_member`（端点→中点+rpy）/ `_add_bolt_on_y_face`/`_add_bolt_on_z_face`，以及 S2 的 `_rpy_for_z_aligned_member`。
- Slot C：`separate_bearing_parts` 的 2 个 `frame_to_*_bearing` FIXED joint 是唯一允许的非身份 articulation——在 module docstring 注明“需独立 bearing 参考系坐住 leaf trunnion”；其余三者 bearing/trunnion 全走 visual。
- captured-pin 重叠：`trunnion_shaft_through_torus_ring`（collar/shaft ↔ ring）、`leaf_sleeve_over_support_pin`（sleeve ↔ pin）、`trunnion_tube_in_cylinder_housing`（tube ↔ housing bore）三者都需在 `run_singleleaf_drawbridge_tests` 里对 trunnion↔bearing 声明 `ctx.allow_overlap(... reason="press-fit / seated trunnion ...")`（参照 S2:L552-L565 / S5:L213-L232 / S7:L172-L180）。
- `hinge_axis=alongshore=(1,0,0)`：**v1 暂不采样**。仅 2 个样本（8b9957c9/a76f28f2）且都 read-but-not-adopted（0 行 adopted 源码），而它要求 Slot A/B/C 坐标系整体转 90°（leaf/trunnion 长轴、bearing 销线、deck 跨向、closed-seam 匹配逻辑全部同步旋转），高实现成本配低多样性增量（只是轴旋转、非新拓扑骨架）。留作 future work；日后启用须对 alongshore seed 单独 viewer 目检。
- counterweight（`bascule_counterweight_leaf`）务必 baked 进 leaf 的 visual 并置于 pivot 后方（-X 侧），不另起 part。span 前后分配：配重尾长 = `span_length·heel_fraction`、deck 前伸段 = `span_length`，pivot 在两段交界；务必让闭合位 deck 前段与 support 岸基路面对齐（closed-seam），勿因配重尾把 pivot 推离销线导致 deck 悬空或穿透 support。
