# Pet_Animal related / Bird cage — Modular Spec

> 来源小类：`picture/Pet_Animal related/Bird cage/{001,002}.png`（上游 articraft_data 鸟笼小类样本池）。
> 上游 source map：`articraft_template_authoring/picture_source_maps/Pet_Animal_related__Bird_cage.md`。
> **"Bird cage" 在此 = 栅栏/铁丝围合的养鸟笼**：可开合的取物门 + 内部栖木 + 底部粪盘/托盘，笼体为 barred/wire 围合（不是实壁鸟巢箱、不是玻璃缸/水族箱、不是啮齿动物笼、不是吊灯/灯笼）。笼身可为**方箱族**（barrel-vault / flat-top / gable 顶）或**圆/多边棱柱族**（dome round / hexagonal prism），但必须保住 wire-mesh 围合 + 至少一个真实非-fixed 关节的取物开口。
>
> **同步状态**：本 spec 引用的 13 个 5 星样本（2 origin + 11 fork 槽位变体）已同步进本仓库 `data/records/`。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计。引用以 part / joint / helper **名字**为准（`_add_rod` / `_add_arch` / `cage` / `door` / `latch` / `roof_hatch` / `door_hinge` / `latch_pivot` / `door_slide` / `base_tray` / `top_hook` / `carry_bail` / `feed_cup_{i}` / `perch_{i}`），行号仅作定位。模板已实现并 sweep `verdict=pass`（seeds 0-47 + corner，pass_rate=1.0）。

## 元信息
| 项 | 值 |
|---|---|
| slug | `bird_cage` |
| template path | `agent/templates/bird_cage.py` |
| test path (optional) | `tests/agent/test_bird_cage_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（单 `cage` 根 chassis 携带互斥的 body_form + door_mechanism + support_base + interior named slots（parallel children），外加 perch 计数与 wall-bar 密度两根 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 13（2 origin + 11 fork 槽位变体；均 converged、compile success、≥1 非 fixed joint、单轴 diff、绑定门禁通过）|
| read_count | 13（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests）|
| read_scope | all 5-star samples in this category（按显式给定的 2 origin + 11 var 清单）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 13/13 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **origin A（方箱基线）** `…_291ba037`（002.png）：`cage`（root：`base_tray`+4 `caster_*` 万向轮 L134-151，bottom/spring 矩形 rail + 4 `corner_post_{i}` + side/rear/front wire 栅格 L155-200，拱形 `_add_arch` barrel-vault 顶 L228/L258，`front_*_split`/`fixed_door_frame_*` 门洞切口 + `latch_strike` L239-245，2 `*_wood_perch` L273-274）+ `door`（wire 面板 + `door_hinge_leaf_{i}`）+ `latch`。**2 个 REVOLUTE**：`door_hinge`（cage→door，axis=(0,0,-1)，L306-313，upper 1.35）+ `latch_pivot`（door→latch，axis=(0,1,0)，L330-337，upper 1.57）。方箱族 body/door/support/interior 全部脱胎于此。
- **origin B（圆笼基线）** `…_eaa2a62a`（001.png）：`base_tray`（root，`LatheGeometry.from_shell_profiles` 车削托盘 L251-276 + 脚）+ `wire_frame`（`TorusGeometry` 圆箍 + 径向 wire + 门洞 skip L119-168 + dome 子午线 + crown ring + `_top_hook_mesh` 顶钩 L232-315）+ `perch`（`_perch_mesh` 单栖木 L276-319）+ `access_door` + `latch`。**REVOLUTE** `frame_to_door` L342-344（+ latch）。圆/dome/hook/footed-tray/单栖木族脱胎于此。
- **door_mechanism 轴（② 关节）**：side_hinge（A/B `door_hinge` REVOLUTE 侧铰）/ drop_front（`rec_..._mechanism_dropfront` `door_hinge` REVOLUTE **axis=(1,0,0)** 底缘下翻 L338-345）/ slide_door（`rec_..._mechanism_slidedoor` PRISMATIC 垂直导轨 + `left/right_guide_rail` L251-263 + `door_lug` L318-321）/ top_hatch（`rec_..._mechanism_topopen` 顶盖 REVOLUTE + `roof_hatch` part + `hatch_*` 铰 L175-289）。是真正的 joint type/轴/接口父级差异。
- **support_base 轴（① 骨架）**：caster_tray（A `base_tray`+4 万向轮 slide-out 托盘 L134-151）/ leg_stand（`rec_..._support_legstand` 4 `stand_leg`+`apron`+`shelf`+`foot` 四腿落地架 L103-110）/ footed_tray（B 车削 footed 托盘 + `top_hook` L251-315）/ hanging_bail（`rec_..._support_hanging` 浅催盘 + `carry_bail` 单一提梁 L232-261，无脚）。是支撑骨架的真实拓扑差异。
- **interior 轴（N 多重性）**：perch N=1（B 单 `perch` L318-319）/ N=2（A 2 `*_wood_perch` L273-274）/ N=3（`rec_..._n3_perch` loop 3 栖木）；feeder cups N=2（`rec_..._accessory_feedcups` `feed_cup_{i}`+`feed_bracket_{i}` clip 前栅 L279-304）。
- **wall-bar 密度轴（N 多重性）**：dense（A/B origin 密栅）/ coarse（`rec_..._n_bars_coarse` 半数粗栅，per-face `bar_count` 驱动）。
- **skeleton_hexagon**（`rec_..._skeleton_hexagon`）：圆箍→六边环 `_hex_ring_rails` L105-106 + 6 面 bar + 6 角子午线到 crown（L33-51 六边角点），是 body_form ③ 的多边棱柱候选（挂在 round 族）。**skeleton_flattop / roof_gable**（`rec_..._skeleton_flattop` / `rec_..._roof_gable`）：方箱顶从 barrel-vault 换 flat-top 网格 / 双坡 gable 脊，是 body_form ③ 的方箱顶候选。

## 核心身份

一只**养鸟的栅栏/铁丝笼（barred/wire bird cage）**：一个坐地或吊挂的 `cage` 根围合体（垂直 wire 栅 + 环/矩形 rail + 顶盖，全为不动 `parent.visual`，Rule 1），携带**一个可开合的取物开口**（`door` 侧铰翻门 / 底铰 drop-front / 垂直 guillotine 滑门 / 顶盖 `roof_hatch`——真实非-fixed 关节），铰门另配一枚可转 `latch` 门闩（REVOLUTE）。笼底为**粪盘/托盘**（滑出托盘 + 万向轮 / 车削 footed 托盘 / 浅催盘），内部有 **1–3 根栖木**（`perch_{i}`，dowel 端穿对侧 wire）及可选 **2 个喂食杯**（`feed_cup_{i}` clip 前栅）。身份核心 = wire-mesh 围合 + 真实取物门关节 + 内栖木 + 底托盘。默认成熟域：小到 ~0.8 m 桌面圆笼（B）、大到 ~1.65 m 落地方笼（A）；至少 1 个非-fixed 取物门关节（铰门再加 latch）。

不该混入：
- **鸟巢箱 / 巢盒（birdhouse / nest box，实壁）**——本类是通透 wire 围合，非实壁封闭盒。
- **玻璃缸 / 水族箱（terrarium / aquarium）**——透明实壁容器，无 wire 栅、无取物铰门。
- **仓鼠/啮齿动物笼（hamster/rodent cage）**——矮阔塑料盆底 + 横向管道；本类是竖高 wire 养鸟笼 + 栖木。
- **展示柜 / 陈列罩（display case / vitrine）**——玻璃陈列，非养鸟 wire 笼。
- **灯笼 / 吊灯（lantern / pendant lamp）**——含光源语义的照明件；hex_prism / dome / hanging_bail 候选须保住鸟笼身份（内栖木 + 门 + 托盘），不得漂成灯具。

## 槽位 + 候选模块表

> **建模注记**：4 个 named slot 都把 part/visual 挂到共同的 `cage` 根（`mixed`：body_form 决定 `cage` 围合几何 + 顶盖 + 门洞；door_mechanism 决定唯一/主活动件 `door`/`roof_hatch` 的 part + joint type/轴/父级（+ 铰门的 `latch`）；support_base 与 interior 各贡献一组不动 `cage` visual），外加 `n_perches` 与 `bar_density` 两根 multiplicity 轴。`family` 由 body_form 派生（box / round），并**门禁**兼容的 door/support/interior 子集（见 §9 兼容矩阵）。slot 之间通过共享 `cage` 的 mating face（前面门洞 / 顶后缝铰线 / 侧导轨 / 底 rail / dome crown）装配。

### Slot A：body_form（主体形态家族 ③ —— 换 `cage` 围合的可识别几何形态原型；同 part 树、同 wire primitive、同 door_hinge 拓扑家族）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | form_subtype · 结构特征 |
|---|---|---|---|---|---|
| barrel_vault_box（方箱基线）| forked_anchor | origin A `…_291ba037` | `_build_box_body` 源 L155-200 + barrel `_add_arch` 顶 L228,L258-267 | eligible if compatible | **Volumetric Envelope Form**：矩形 wire 箱 + 半圆筒 barrel-vault 拱顶（`_add_arch` 半径=half_w，roof_r 弧肋 + longitudinal + gable 竖丝）；`top_z = spring_z + half_w` |
| flat_top_box | world_knowledge_extrapolation（③；anchor `rec_..._skeleton_flattop`）| `rec_..._skeleton_flattop` L495 全文 | 采纳其 flat-top 网格顶结构（并行顶丝 + 横丝） | eligible if compatible | **Macro Surface Construction**：方箱身 + 平顶开放网格（spring_z 平面并行 `roof_longitudinal_{i}` + `roof_cross_wire_{i}`）；`top_z = spring_z`；**唯一能载 top_hatch 的顶** |
| gable_box | world_knowledge_extrapolation（③；anchor `rec_..._roof_gable`）| `rec_..._roof_gable` L512 全文 | 采纳其双坡脊 A-frame 顶结构 | eligible if compatible | **Volumetric Envelope Form**：方箱身 + 双坡脊 gable 顶（`roof_rib_{i}_l/r` 两坡 + `roof_ridge_purlin` 脊檩 + 坡 longitudinal + gable 竖丝）；`top_z = spring_z + 0.35·hs` |
| dome_round（圆笼基线）| forked_anchor | origin B `…_eaa2a62a` | `_build_round_body` 源 L119-168（`TorusGeometry` 箍 + 径向 bar + dome 子午线 + crown）| eligible if compatible | **Volumetric Envelope Form**：圆柱 wire 身（`TorusGeometry` 箍 + 20/12 径向直丝）+ 半球 dome（子午线 spline 到 crown ring + 顶尖）；门洞 skip 前弧 |
| hex_prism | forked_anchor | `rec_..._skeleton_hexagon` | 六边环 `_hex_ring_rails` L105-106 + 6 角点 L33-51 + 6 面 bar + 子午线到 crown | eligible if compatible | **Planar Boundary Form**：正六边棱柱截面（6 `_mtube` 边环替圆箍 + 沿 6 面直丝 + 6 角子午线到 crown）；`faceted=True`，门洞切一面 |

> 5 candidate 全为可识别主体形态原型（barrel 半圆筒 / flat 平顶 / gable 双坡 / dome 半球 / hex 六棱），共享 wire-rod primitive 家族与"cage 根 + 取物门 REVOLUTE/PRISMATIC"接口。box 三形共享 `_build_box_body` + `_add_rod` 方栅词汇；round 两形共享 `_build_round_body` + mesh（Torus/tube/lathe）词汇。flat_top/gable 两 box-③ candidate 由世界知识 author（标 `world_knowledge_extrapolation`）但各有 fork anchor 背书、保同 part 树/同 primitive/同门接口——只改顶部宏观表面/包络形态（符合 Rule 3）。

### Slot B：door_mechanism（取物开口机构 —— ② 关节类型/轴/父级轴；`door`/`roof_hatch` part + joint 拓扑变化）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|---|
| side_hinge（基线）| forked_anchor | origin A `…_291ba037`（+ B 同款侧铰）| `door` 面板 + `door_hinge_leaf_{i}` L284-299；`door_hinge` REVOLUTE L306-313；`latch`+`latch_pivot` L316-337 | eligible if compatible | **侧铰翻门**：`door` 独立 part，**REVOLUTE** `door_hinge` **axis=(0,0,-1)** 竖铰（origin 在门洞左缘 `dxmin`），upper 1.35 外摆；配 `latch` part REVOLUTE `latch_pivot` axis=(0,1,0) 门闩。cage 侧发 `cage_hinge_pin`+`hinge_standoff` 捕获销、box 另发 `latch_strike`+`strike_standoff` 门闩座（桥接到 `fixed_door_frame_right` 竖挺）。**方箱+圆笼共用**|
| drop_front | forked_anchor | `rec_..._mechanism_dropfront` | `door_hinge` REVOLUTE **axis=(1,0,0)** L338-345 | eligible if compatible | **底铰下翻门**：`door` 对称面板，**REVOLUTE** `door_hinge` **axis=(1,0,0)** 底缘水平铰（origin 在门洞底 `db`），upper 1.55 前下翻；无摆动 latch（改用不动 `drop_front_catch` 顶部固定卡扣，避免自扫栅）。仅方箱 |
| slide_door | forked_anchor | `rec_..._mechanism_slidedoor` | `left/right_guide_rail` L251-263 + `door_lug` L318-321；PRISMATIC 垂直滑轨 | eligible if compatible | **垂直 guillotine 滑门**：`door` 面板 + 4 `door_lug_{i}` 侧耳，**PRISMATIC** `door_slide` **axis=(0,0,1)** 上滑（travel≈0.86·dh）；cage 发 `left/right_guide_rail` 侧导轨捕获门耳 + `door_stop_pin` 止销。仅方箱 |
| top_hatch | forked_anchor | `rec_..._mechanism_topopen` | `roof_hatch` part + `hatch_*` L175-289 | eligible if compatible | **顶盖掀开**：独立 `roof_hatch` part（loop `hatch_bar_{i}` 网格 + `hatch_frame_*` + `hatch_handle_*`），**REVOLUTE** `door_hinge` **axis=(-1,0,0)** 后顶缘铰（origin=(0,back_y,hinge_z)），upper 1.20 上掀；cage 发 `hatch_hinge_rail`+`hatch_hinge_post_{i}` 后铰座（captured hinge，barrel 包销）。**仅 flat_top_box**（唯一平顶可载 hatch）|

> 4 candidate 为真正不同 joint 拓扑等价类：side/drop 竖轴 vs 水平轴 REVOLUTE、slide PRISMATIC、top_hatch 独立顶盖 part + 后铰。`slot_choices` 记 door_mechanism 名，distinct 不折叠。

### Slot C：support_base（支撑/底座 —— ① 骨架/拓扑轴；`cage` 上不动 visual，Rule 1）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| caster_tray（方箱基线）| forked_anchor | origin A `…_291ba037` | `base_tray`+lip L134-138 + 4 `caster_*_{ix}_{iy}`（stem/fork/wheel）L140-151 + `tray_riser` | eligible if compatible | **滑出托盘 + 万向轮**：矩形 `base_tray` + 4 边 lip + 4 组万向脚轮（stem+双 fork+wheel）+ 4 `tray_riser` 撑到笼底 rail；全 non-moving。仅方箱 |
| leg_stand | forked_anchor | `rec_..._support_legstand` | 4 `stand_leg`+`apron`+`shelf`+`foot_pad` L103-110 | eligible if compatible | **四腿落地架**：4 `stand_leg_{i}` 角腿 + `foot_pad_{i}` + 上 `apron_*` 围框（笼座于此）+ 下 `shelf_*` 网格 + `cage_tray` 薄托盘 + `tray_riser`；全 non-moving。仅方箱 |
| footed_tray（圆笼基线）| forked_anchor | origin B `…_eaa2a62a` | `_lathe_tray_mesh` 车削托盘 L251-276 + `tray_foot_{i}` + `_top_hook_mesh` L232-315 | eligible if compatible | **车削 footed 托盘 + 顶钩**：`LatheGeometry.from_shell_profiles` 车削浅盘 `base_tray` + 4 scrollwork `tray_foot_{i}` + dome crown 起 `top_hook` 提钩；全 non-moving。仅圆/hex |
| hanging_bail | forked_anchor | `rec_..._support_hanging` | 浅 `_lathe_tray_mesh` 催盘 + `carry_bail` 提梁 L232-261 | eligible if compatible | **吊挂提梁（无脚）**：浅悬催盘 `base_tray` + dome crown 起单一 `carry_bail` 拱形提梁作唯一支撑（无脚）；全 non-moving。仅圆/hex |

> 4 candidate 为真实支撑骨架拓扑（滚轮托盘 / 四腿架 / footed 顶钩 / 吊梁），门禁按 family 分：box→{caster_tray, leg_stand}，round→{footed_tray, hanging_bail}。全 non-moving `cage` visual（Rule 1）。

### Slot D：interior（内部栖木/喂食杯 —— N 多重性轴 + 结构变化；`cage` 上不动 visual，Rule 1）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| perch1 | forked_anchor | origin B `…_eaa2a62a` | 单 `perch` `_perch_mesh` L276-319 | eligible if compatible | 1 根 `perch_0` 栖木横跨内部，端座对侧 wire。所有 body 兼容 |
| perch2（方箱基线）| forked_anchor | origin A `…_291ba037` | 2 `lower/upper_wood_perch` L273-274 | eligible if compatible | 2 根 `perch_{i}` 分高错落。所有 body 兼容 |
| perch3 | forked_anchor | `rec_..._n3_perch` | loop 3 栖木 | eligible if compatible | 3 根 `perch_{i}` loop 发射、等距分高。所有 body 兼容 |
| perch2_feed2 | forked_anchor | `rec_..._accessory_feedcups`（+ A 双栖木）| `feed_cup_{i}`+`feed_bracket_{i}` L279-304 | eligible if compatible | 2 栖木 + **2 `feed_cup_{i}`** clip 前栅（cup lathe 壳 + bracket）。**仅方箱**（喂食杯挂前平栅/门挺）|
| perch3_feed2 | forked_anchor | `rec_..._accessory_feedcups`+`rec_..._n3_perch` | 组合 | eligible if compatible | 3 栖木 + 2 `feed_cup_{i}`。**仅方箱** |

> interior 同时是 **N 多重性轴**（perch 数 1/2/3）与结构轴（是否带 feed cups）。`n_perches`∈{1,2,3} loop 发射 `perch_{i}`；`n_feed_cups`∈{0,2} loop 发射 `feed_cup_{i}`。round/hex 只兼容 perch-only（perch1/2/3），feed cups 仅方箱（需前平栅挂杯）。

硬约束记录：Slot A=5、Slot B=4、Slot C=4、Slot D=5（含 2 根 multiplicity：perch 数 + feed 数），另 `bar_density` wall-bar 密度轴 = 2；全部来自被采纳五星样本（flat_top/gable 两 ③ 候选标 `world_knowledge_extrapolation` 且各有 fork anchor 背书），无 1-candidate 槽。

## 槽位图（slot graph）

pattern: `mixed`（单 `cage` 根 chassis 携带互斥 body_form + door_mechanism + support_base + interior（parallel children），外加 `n_perches` / `bar_density` 两根 multiplicity 轴）

```
cage (root, 坐地/吊挂; body_form 决定围合几何 + 顶盖 + 门洞切口; support_base + interior 挂不动 visual)
  │
  ├── [body_form slot]  (③ 主体形态; 互斥五选一; box 族 vs round 族 派生 family + 门禁)
  │     ├─ box 族  : barrel_vault_box / flat_top_box / gable_box  (_build_box_body + _add_rod 方栅)
  │     └─ round 族: dome_round / hex_prism                       (_build_round_body + Torus/tube/lathe mesh)
  │
  ├── [door_mechanism slot]  (② 关节; 互斥; family-门禁)
  │     ├─ side_hinge : door ──[door_hinge: REVOLUTE axis=(0,0,-1) 门洞左缘] + latch ──[latch_pivot: REVOLUTE axis=(0,1,0)]
  │     ├─ drop_front : door ──[door_hinge: REVOLUTE axis=(1,0,0) 门洞底缘]  (+ 固定 drop_front_catch, box only)
  │     ├─ slide_door : door ──[door_slide: PRISMATIC axis=(0,0,1) 侧导轨]   (+ guide_rail/door_stop_pin, box only)
  │     └─ top_hatch  : roof_hatch ──[door_hinge: REVOLUTE axis=(-1,0,0) 后顶缘] (flat_top_box only)
  │
  ├── [support_base slot]  (① 骨架; 互斥; family-门禁; non-moving cage visual)
  │     ├─ caster_tray (box): base_tray + 4 caster_*_{ix}_{iy} + tray_riser
  │     ├─ leg_stand   (box): 4 stand_leg_{i} + apron_* + shelf_* + cage_tray
  │     ├─ footed_tray (round): 车削 base_tray + tray_foot_{i} + top_hook
  │     └─ hanging_bail(round): 浅 base_tray + carry_bail (唯一支撑, 无脚)
  │
  ├── [interior slot]  (① multiplicity + 结构; non-moving cage visual)
  │     ├─ perch_{i}    i∈range(n_perches), n_perches∈{1,2,3}  (端座对侧 wire)
  │     └─ feed_cup_{i} i∈range(n_feed_cups), n_feed_cups∈{0,2}  (clip 前栅, box only)
  │
  └── [bar_density multiplicity 轴]  wire 栅数 dense / coarse (per-face bar_count 驱动; 全 non-moving)
```

接口点位与 joint 语义：
- **body_form → cage**（互斥五选一）：box 族用 `_build_box_body`（矩形 wire 栅 + `_add_arch`/flat/gable 顶 + `front_*_split`/`fixed_door_frame_*` 门洞），round 族用 `_build_round_body`（Torus/tube 箍 + 径向直丝 + dome/hex crown + 前弧门洞 skip）。family 派生并门禁 door/support/interior 子集。
- **door_mechanism**（互斥；family-门禁）：
  - side_hinge：`door_hinge` REVOLUTE axis=(0,0,-1)，origin 门洞左缘 `(dxmin, door_y, db)`，upper 1.35；`door` 沿 -y 外摆；cage 发 `cage_hinge_pin`(销)+`hinge_standoff`×2 捕获门铰边框；box 另发 `latch_strike`+`strike_standoff`（**桥接到 `fixed_door_frame_right` 竖挺**，非浮空岛）。配 `latch` REVOLUTE `latch_pivot` axis=(0,1,0)。
  - drop_front：`door_hinge` REVOLUTE **axis=(1,0,0)**，origin 门洞底 `(0, door_y, db)`，upper 1.55 前下翻；不动 `drop_front_catch` 顶卡扣（不用摆动 latch，避免自扫）。box only。
  - slide_door：`door_slide` PRISMATIC axis=(0,0,1)，origin `(dxmin, door_y, db)`，travel 0.86·dh 上滑；cage 发 `left/right_guide_rail` 捕获 `door_lug_{i}` + `door_stop_pin`。box only。
  - top_hatch：`door_hinge` REVOLUTE **axis=(-1,0,0)**，origin `(0, back_y, hinge_z)` 后顶缘，upper 1.20 上掀；独立 `roof_hatch` part；cage 发 `hatch_hinge_rail`+`hatch_hinge_post_{i}` 后铰座（**captured hinge**：hatch 后框 `hatch_frame_rear` + `hatch_hinge_barrel_{i}` 同轴包 cage 铰 rail/post，element-scoped allow_overlap）。flat_top_box only。
- **support_base → cage**（互斥；family-门禁；non-moving，Rule 1）：box→{caster_tray 滚轮托盘 / leg_stand 四腿架}；round→{footed_tray 车削托盘+顶钩 / hanging_bail 吊梁}。全为 `cage` 的 visual，`tray_riser` 撑到笼底 rail 确保连通。
- **interior → cage**（non-moving，Rule 1）：`perch_{i}` loop 发射，端点 `(±half_w±0.006 / ±cage_r±0.006, y, z)` 座到真实侧壁 wire（box）或 y≈0 的 angle-0/π 直丝（round）；`feed_cup_{i}` clip 前栅（box），`feed_bracket_{i}` 从门挺伸出捕获。
- **mating policy**：所有活动接口是 captured 几何——铰门边框包 `cage_hinge_pin`/standoff、latch spindle 穿 `door_latch_boss`、slide `door_lug` riding `guide_rail`、top_hatch 后框/barrel 包 cage 铰 rail/post —— 非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap。
- **rest pose**：门 q=0 闭合座门洞、latch q=0 悬扣 `latch_strike`、slide q=0 门在下位、hatch q=0 平盖闭合、栖木/杯/托盘坐位。
- **互斥 / 可选 / 派生**：body_form 五候选互斥并派生 family；door/support/interior 由 family 门禁（见 §9 兼容矩阵）；top_hatch 仅 flat_top_box；feed cups 仅 box。

## 每槽位 Module Emits / Interfaces

### Slot A / body_form — barrel_vault_box（方箱基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cage`（root：矩形 wire 栅 + `corner_post_{i}` + side/rear/front 栅 + `_add_arch` barrel 顶 + `fixed_door_frame_*` 门洞）| A L155-267 |
| internal joints | 无（body 全 non-moving visual，Rule 1）| — |
| downstream interface | 前面门洞（`dxmin/dxmax`、`db/door_top_z`）供 door；spring_z rail 供 support/roof；侧壁 wire 供 perch | A L188-200 |

### Slot A / body_form — dome_round（圆笼基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cage`（root：`TorusGeometry` 箍 + 径向直丝 + dome 子午线 spline + crown ring/顶尖，前弧门洞 skip）| B L119-168 |
| internal joints | 无 | — |
| downstream interface | 前弧门洞 + 门框 heavy wire；dome crown 供 support（top_hook/bail）；angle-0/π 直丝供 perch | B L128-168 |

### Slot A / body_form — hex_prism / flat_top_box / gable_box
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cage`：hex=`_hex_ring_rails` 六边环+6 面丝+crown（`rec_..._skeleton_hexagon` L105-106,L33-51）；flat_top=平顶网格（`rec_..._skeleton_flattop`）；gable=双坡脊（`rec_..._roof_gable`）| 各 fork |
| internal joints | 无 | — |
| downstream interface | 同族门洞/顶/perch 接口；flat_top 平顶唯一载 top_hatch | 各 fork |

### Slot B / door_mechanism — side_hinge（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door`（wire 面板 + `door_hinge_barrel_{i}` + `door_hinge_leaf_{i}`）+ `latch`（`latch_pivot_disc`+`latch_tab`+`latch_spindle`）；cage 上 `cage_hinge_pin`+`hinge_standoff_{0,1}` + (box) `latch_strike`+`strike_standoff` | A L284-337 |
| internal joints | `door_hinge` REVOLUTE axis=(0,0,-1) origin 门洞左缘 range[0,1.35]；`latch_pivot` REVOLUTE axis=(0,1,0) range[0,1.57] | A L306-337 |
| upstream interface | 门洞左缘 `(dxmin, door_y, db)`（cage 侧 pin 捕获门铰边框）| A L306-313 |

### Slot B / door_mechanism — drop_front
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door`（对称面板 + `door_hinge_barrel_{i}`）；cage 上 `drop_front_catch`+`catch_standoff` 不动卡扣 | `rec_..._mechanism_dropfront` L338-345 |
| internal joints | `door_hinge` REVOLUTE **axis=(1,0,0)** origin 门洞底 range[0,1.55]（无摆动 latch）| dropfront L338-345 |
| upstream interface | 门洞底缘水平铰线（cage `cage_hinge_pin` x 轴 + standoff）| dropfront L338-345 |

### Slot B / door_mechanism — slide_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door`（面板 + 4 `door_lug_{i}`）；cage 上 `left/right_guide_rail` + `door_stop_pin` | `rec_..._mechanism_slidedoor` L251-321 |
| internal joints | `door_slide` PRISMATIC axis=(0,0,1) origin 门洞左下 range[0, travel] | slidedoor 滑轨 |
| upstream interface | 侧导轨捕获门耳（`guide_rail` riding `door_lug`）| slidedoor L251-263 |

### Slot B / door_mechanism — top_hatch
| emits | 描述 | 来源 |
|---|---|---|
| parts | `roof_hatch`（`hatch_frame_*` + loop `hatch_bar_{i}` + `hatch_hinge_barrel_{i}` + `hatch_handle_*`）；cage 上 `hatch_hinge_rail`+`hatch_hinge_post_{i}` | `rec_..._mechanism_topopen` L175-289 |
| internal joints | `door_hinge` REVOLUTE **axis=(-1,0,0)** origin 后顶缘 range[0,1.20] | topopen L283-289 |
| upstream interface | 后顶缘 captured hinge（cage rail/post 被 hatch 后框/barrel 同轴包，allow_overlap）| topopen 铰段 |

### Slot C / support_base — caster_tray（基线）/ leg_stand / footed_tray / hanging_bail
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；caster=`base_tray`+4 `caster_*`+`tray_riser`（A L134-151）；leg=4 `stand_leg_{i}`+`apron/shelf/cage_tray`（`rec_..._support_legstand` L103-110）；footed=车削 `base_tray`+`tray_foot_{i}`+`top_hook`（B L251-315）；hanging=浅 `base_tray`+`carry_bail`（`rec_..._support_hanging` L232-261）| 各源 |
| internal joints | 无（Rule 1，non-moving）| — |
| upstream interface | box：`tray_riser` 撑到笼底 rail；round：托盘座笼底 + top_hook/bail 起自 dome crown | 各源 |

### Slot D / interior — perch_{i}（multiplicity）/ feed_cup_{i}
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`perch_{i}`（wood 横杆）+ `feed_cup_{i}`（lathe 杯）+`feed_bracket_{i}`（cage visual）| A L273-274 / B L318-319 / feedcups L279-304 |
| internal joints | 无（Rule 1，non-moving；随 cage 固定）| — |
| placement | `perch_{i}`：`for i in range(n_perches)` 等距分高，端座对侧 wire；`feed_cup_{i}`：`for i in range(n_feed_cups)` clip 前栅两高度 | A/B/feedcups |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | barrel_vault_box / flat_top_box / gable_box / dome_round / hex_prism | — | choice | sampler 选；派生 family(box/round)，门禁 door/support/interior | module table |
| door_mechanism | enum | side_hinge / drop_front / slide_door / top_hatch | — | conditional | `∈ _compatible_doors(body)`（box=前三+flat_top 加 top_hatch；round=side_hinge）| module table |
| support_base | enum | caster_tray / leg_stand / footed_tray / hanging_bail | — | conditional | `∈ _compatible_supports(body)`（box=caster/leg；round=footed/hanging）| module table |
| interior | enum | perch1 / perch2 / perch3 / perch2_feed2 / perch3_feed2 | — | conditional | `∈ _compatible_interiors(body)`（round 仅 perch1/2/3）；派生 `n_perches`/`n_feed_cups` | module table |
| n_perches (N) | int | [1,3]（perch{1,2,3} → 1/2/3）| 2 | conditional→slot_choice | 由 interior 派生；`perch_{i}` loop 数 | A/B/n3_perch |
| n_feed_cups (N) | int | {0,2}（feed2 → 2）| 0 | conditional | 由 interior 派生；仅 box | feedcups |
| bar_density | enum | dense / coarse | dense | choice | per-face `bar_count`（box 13/9→7/5；round 20/12）；wall-bar 多重性轴 | n_bars_coarse |
| palette_theme | enum | black_powder / aged_brass / white_coat | black_powder | palette | palette only，**不计入 slot_choice**；映射 material rgba | A/B material |
| width_scale | float | [0.86,1.16] 采样，clamp[0.80,1.22] | 1.0 | independent | 独立采样后 clamp；缩 W/D/cage_r | 各样本尺寸 |
| height_scale | float | [0.86,1.18] 采样，clamp[0.80,1.24] | 1.0 | independent | 独立采样后 clamp；缩 spring_z/straight_z1/dome | 各样本尺寸 |
| door_frac | float | [0.44,0.58] 采样，clamp[0.40,0.62] | 0.48 | independent | 门宽比例（box door_w = df·W）| A 门洞 |
| (—) | constraint | — | — | inequality | `door_w = clamp(df·W, 0.26, W-0.16)`；`door_h = clamp(0.58·hs, 0.30, spring_z-db-0.10)`；门洞不超壁 | resolve_config |
| (—) | constraint | — | — | conditional | top_hatch 仅 flat_top_box；feed cups 仅 box；round door_h/door_w 用 cage_r 派生 | body_form/family |

连续尺寸采样契约（`config_from_seed`/`resolve_config`）：先 `rng.choice` body_form → 按 family 门禁 `rng.choice` door/support/interior（解析 conditional）→ `rng.choice` bar_density/palette → uniform width/height/door_frac（independent）→ `resolve_config` 按 family 求解 box/round 尺寸并用 inequality clamp 门洞（door_w/door_h 投影回可行域）。所有 scale 在 `resolve_config` clamp/派生，**绝不改 slot enum、joint type 或 family 身份**。

## 7.5 编译预算 / compile budget

每-seed 编译预算 **≤15s**（wire-rod 主体全为 `_add_rod` Cylinder + 少量 Torus/tube/lathe mesh；round/hex 的 dome 子午线 spline + 车削托盘是唯一较重项，但分档 tessellation：小半径 wire ≤12 段、Torus ≤48 tubular、lathe ≤64 段）。N 个 `perch_{i}`/`caster_*`/wire 复用同一 `_add_rod` helper，无重布尔雕刻。实测全 sweep（48 seed，max-workers 6）≈52s，单 seed 均 ~1s，远在预算内。超预算先降 wire 段数/tubular 段数再迭代。

## Multiplicity / Copy Logic

**2 根 multiplicity 轴**：

**轴 1 — 内部栖木数（`n_perches`）**：
- **count_param**：`n_perches`（`cage` 上 `perch_{i}` 横杆条数），由 interior enum 派生（perch1/2/3 → 1/2/3）。
- **N_range**：产品域 **[1,3]**（鸟笼内栖木现实区间：桌面小笼 1 根到落地笼 3 根）；source 覆盖 N=1(B)/2(A)/3(fork)。
- **sampling domain**：由 interior slot 采样决定（box 5 候选含 1/2/3，round 3 候选含 1/2/3）。
- **copied object**：单根 wood 栖木 `perch_{i}`（`_add_rod` radius 0.013 material wood）；N 个复用同一 helper。
- **naming**：`perch_{i}`，`for i in range(n_perches)`。
- **placement**：等距分高（z_lo=bottom+0.34·H 到 z_hi=bottom+0.70·H，`frac = i/(n-1)`），端座对侧真实 wire（box 内侧壁 vertical / round angle-0/π 直丝）。绝对式（每 i 的 z 由 N 解析，不累加漂移）。
- **joint policy**：非移动件（Rule 1）→ inline 为 `cage` visual，无独立 joint。
- **source/gating**：copy 源 A L273-274（N=2）+ B L318-319（N=1）+ n3_perch（N=3）；round/hex 仅 perch-only。

**轴 2 — wall-bar 密度（`bar_density`→`bar_count`）**：
- **count_param**：per-face `bar_count`（box `_box_counts`：dense=(13,9)/coarse=(7,5)；round `n_sides`：dense=20/coarse=12；hex 固定 6）。
- **N_range**：产品域 per-face [5,13]（box）/ [12,20]（round）；两档 dense/coarse。
- **sampling domain**：`bar_density` enum 加权（dense/coarse 等权 `rng.choice`）。
- **copied object**：单根 vertical wire（`side_vertical_*`/`rear_vertical_*`/`front_vertical_*`/圆径向直丝）；N 根复用 `_add_rod`/`_mrod_z`。
- **naming**：`{face}_vertical_{i}` / round 循环 index。
- **placement**：每面沿 X/半径均匀等距（`bar_count` 驱动），rail 随之重排。
- **joint policy**：非移动件（Rule 1），无独立 joint。
- **source/gating**：dense=A/B origin，coarse=`rec_..._n_bars_coarse`；hex 固定 6 边不参与密度采样。

**说明**：`n_feed_cups`∈{0,2} 是 interior 结构位（feed2 → 2 杯），非独立加权 count 轴（仅 0/2 两态，随 interior 派生，仅 box）；4 `caster_*` / 4 `stand_leg` / dome 子午线数是 module 内部固定数量，**非模板级 multiplicity 轴**（不进 slot_choice，不加权采样）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | **有** | door_mechanism 换活动件（side/drop/slide 单铰门 vs top_hatch 顶盖 part vs +latch）；support_base 换支撑骨架（滚轮托盘 / 四腿架 / footed 顶钩 / 吊梁）。全 forked_anchor。见 §8 multiplicity |
| └ multiplicity | 同构件 ×N | **有** | perch 数 N∈[1,3]（§8 轴 1）；wall-bar 密度 dense/coarse（§8 轴 2）。均 source-backed |
| ② 关节类型 | 图不变，某边换 type/轴 | **有** | REVOLUTE 竖轴 side_hinge(0,0,-1) / REVOLUTE 横轴 drop_front(1,0,0) / PRISMATIC slide_door(0,0,1) / REVOLUTE top_hatch(-1,0,0) + latch REVOLUTE(0,1,0)。全 forked_anchor；每型均在 sweep 出现（axis_realization：side 30/drop 7/slide 8/top 3）|
| ③ 主体形态家族 | 图&关节不变，换核心 part 可识别形态原型 | **有（登记进 slot_choices 的 body_form slot）** | barrel_vault_box(Volumetric Envelope) / flat_top_box(Macro Surface, `world_knowledge_extrapolation`+fork anchor) / gable_box(Volumetric Envelope, `world_knowledge_extrapolation`+fork anchor) / dome_round(Volumetric Envelope) / hex_prism(Planar Boundary)。5 原型，source-backed |
| ④ 表面装饰 | 原型不变，叠表面细节 | **有（host-conformal）** | `record_only`：wire 栅格密度（bar_density，随 ③⑤ 共形）、crown ring/顶尖(round)、scrollwork `tray_foot`(footed)、gable 竖丝填充；均由宿主 wire 面派生，非独立 part/joint |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | **有** | width_scale[0.86,1.16]/height_scale[0.86,1.18]/door_frac[0.44,0.58]（§7）；关节行程：side upper 1.35（-y 外摆）/ drop 1.55（前下翻）/ slide travel≈0.86·dh（+z 上滑）/ top 1.20（+z 上掀）/ latch 1.57。`motion_test_plan`：run_tests 对每机构 targeted `ctx.pose` 验开启方向 + `fail_if_parts_overlap_in_sampled_poses(48)` 全程不穿模；captured-hinge 用 element-scoped allow_overlap 豁免 |
| ⑥ 涂装 | 只改材质/颜色 | **有** | 3 套 palette_theme：black_powder(黑粉末钢) / aged_brass(做旧黄铜+暗青铜) / white_coat(白烤漆)；材质大类覆盖 metal(黑/铜) + painted(白)。不计入 slot_choice |

**收尾自检**：body_form 5 原型（方箱 barrel/flat/gable + 圆 dome + 六棱 hex）在 axis_realization 全出现（9/12/7/9/11）；door 4 型全出现；support 4 型全出现（14/14/9/11）；palette 3 套 per-seed 采样；perch/feed 计数与 wire 密度肉眼可辨；关节开合全程 sweep 无未豁免穿模。达标。

## 采样与覆盖审计

总组合数（named slot，不含 palette/连续 scale/bar_density）：
- box 族：barrel/gable 各 doors(3)×supports(2)×interiors(5)=30 → 60；flat_top doors(4)×supports(2)×interiors(5)=40 → box 计 **100**
- round 族：dome/hex 各 doors(1)×supports(2)×interiors(3)=6 → **12**
- 合计 **112** 个合法 named-slot 四元组（1000-seed 实测 distinct=112，全空间可达）；叠 bar_density(2)=212。

理由：`slot_choices_for_seed` 返回 `(body_form, door_mechanism, support_base, interior)` 四元组；112 个合法 distinct 组合（远超 ≥10 下限）。family 门禁排除非法组合（box 门/支撑 vs round 门/支撑、top_hatch 仅 flat_top、feed 仅 box），保证每个可达 seed 与 corner seed 合法。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` body_form → 按 `_compatible_doors/supports/interiors(body)` 门禁 `rng.choice` door/support/interior → `rng.choice` bar_density/palette → uniform width/height/door_frac。`resolve_config` 复核门禁（非法组合 raise）并 clamp/派生尺寸。compatibility matrix 主要守 family 门禁 + top_hatch/feed 特例 + 门洞不超壁。无 regression overrides（首版纯 procedural）。random sweep seeds 0-47 初轮 + corner seeds；viewer 目检 0-9。

Topology target：1000-seed 实测 distinct slot-choice 四元组 = **112**（叠 bar_density=212）。112 < 300 —— 本小类真实结构上限：body_form 5 × 兼容 door/support/interior 子集受 family 门禁收窄（round 族只 side_hinge + 2 支撑 + 3 内饰），非源锚点不足。report-only，不作 gate。

Controlled local parameterization：关键 scale = width_scale / height_scale（independent，clamp）、door_frac（independent，clamp）、door_w/door_h（equation+inequality 派生 clamp）、cage_r/spring_z/dome_z（equation 随 ws/hs 派生）。全部 `resolve_config` clamp/派生，遵循采样契约（body_form + family 门禁 conditional → independent scale → inequality 投影门洞）。这些 scale 不破坏门铰 origin、captured 接口、perch 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | `rng.choice` body_form → family 门禁 `rng.choice` door/support/interior → bar_density/palette → uniform scale | slot_choices_for_seed 四元组与 build 一致 |
| compatibility matrix | (1) **family 门禁**：box→{side/drop/slide door, caster/leg support, 全 interior}；flat_top 加 top_hatch；round→{side_hinge, footed/hanging support, perch-only interior}。(2) **top_hatch 仅 flat_top_box**（唯一平顶可载）。(3) **feed cups 仅 box**（需前平栅）。(4) 门洞 door_w/door_h clamp 不超壁。(5) 非法组合 `resolve_config` raise（守 corner seed）| 无 floating（strike/keeper 已桥接 jamb）、captured-hinge allow_overlap、门全程不穿模、门洞不超壁 |
| controlled local variation | width/height/door_frac scale + door_w/door_h/cage_r/spring_z 派生，全 clamp | 比例变化不破门铰 origin、captured 接口、perch 等距、坐门洞、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-47 + corner 初轮；0-999 成熟审计 | 逐机构 captured allow_overlap + closed-pose seat + body 形态 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form (③) | 5 | yes | yes | barrel/flat/gable box + dome/hex round；登记进 slot_choice |
| door_mechanism (②) | 4 | yes | yes | side/drop/slide REVOLUTE/PRISMATIC + top_hatch |
| support_base (①) | 4 | yes | yes | caster/leg (box) + footed/hanging (round) |
| interior (① N) | 5 | yes | yes | perch1/2/3 + perch2/3_feed2；含 perch 计数 multiplicity |
| bar_density (N) | 2 | yes | no | dense/coarse wall-bar 密度轴 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名四元组 `(body_form, door_mechanism, support_base, interior)`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 按 family 门禁复核 door/support/interior（非法组合 raise ValueError），clamp width/height/door_frac，派生 door_w/door_h/cage_r/spring_z/dome_z、n_perches/n_feed_cups；top_hatch/feed 特例解析
- compatibility matrix / gating 阻止非法组合（family 门禁、top_hatch 仅 flat_top、feed 仅 box、门洞不超壁）
- controlled local scale clamp 后不破门铰 origin / captured 接口 / perch 等距 / 坐门洞 / 类别身份
- cross-part scale 依赖（door_w/door_h inequality、cage_r/spring_z equation、conditional 门禁）在 `resolve_config` 解析，不留 builder
- 关键 joint：side_hinge `door_hinge` REVOLUTE axis≈(0,0,-1)；drop_front axis≈(1,0,0)；slide_door `door_slide` PRISMATIC axis≈(0,0,1)；top_hatch `door_hinge` REVOLUTE axis≈(-1,0,0)；`latch_pivot` REVOLUTE axis≈(0,1,0)（仅铰门）；joint origin 落门洞/后顶缘几何上
- captured 接口：element-scoped `allow_overlap`（铰门边框↔`cage_hinge_pin`/standoff、latch spindle↔`door_latch_boss`、slide `door_lug`↔`guide_rail`、top_hatch 后框/barrel↔cage 铰 rail/post）
- 连通性：`latch_strike`+`strike_standoff` 桥接到 `fixed_door_frame_right` 竖挺（非浮空岛）；`tray_riser` 撑到笼底 rail
- copied object 遵循 `perch_{i}`/`feed_cup_{i}` 命名 + 等距 placement + Rule 1（无独立 joint，随 cage 固定）
- grandfather：所有 captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守
- palette_theme 只换 material rgba，不进 slot_choice，不改 part 树

## Reject cases

- 让 body_form 降级成实壁盒/玻璃缸 → 丢失 wire-mesh 鸟笼身份；必须保留 `_add_rod`/`Torus` 通透 wire 围合。
- 把 top_hatch 配 barrel/gable/round（非 flat_top）→ 非平顶无法载后顶铰盖；门禁必须仅 flat_top_box。
- 把 feed cups 配 round/hex → 无前平栅可挂杯；门禁必须仅 box。
- 让 `latch_strike`/`strike_standoff` 浮空（不桥接 `fixed_door_frame_right`）→ `fail_if_part_contains_disconnected_geometry_islands` FAIL（本轮已修）。
- 漏 top_hatch captured-hinge 的 element-scoped allow_overlap（cage rail/post ↔ hatch 后框/barrel）→ `fail_if_parts_overlap_in_sampled_poses` FAIL（本轮已补全）。
- 给 drop_front 配摆动 latch → 门自扫其栅；drop_front 必须用不动 `drop_front_catch`。
- 把 box door/support 配 round body（或反）→ family 门禁 raise；采样必须按 `_compatible_*(body)`。
- 把 perch/feed/caster 等 copied 件当独立 joint 发射 → 违反 Rule 1；须 inline 为 `cage` visual。
- 把连续尺寸（width/height/door_frac）/ palette_theme / bar_density 当新 body candidate 塞进 body_form slot → 非主体形态原型差异。
- 门 rest pose 设成张开角而非 q=0 闭合 → 与 viewer 目检不符（所有样本 lower=0 闭合）。

## 与相邻类别的边界

- 不该混入：**鸟巢箱 / 巢盒（birdhouse / nest box）**——实壁封闭；本类通透 wire 围合 + 取物铰门。
- 不该混入：**玻璃缸 / 水族箱（terrarium / aquarium）**——透明实壁容器；本类 wire 栅 + 内栖木。
- 不该混入：**仓鼠/啮齿动物笼**——矮阔塑料盆底 + 管道；本类竖高养鸟 wire 笼 + 栖木 + 底托盘。
- 不该混入：**灯笼 / 吊灯（lantern / pendant lamp）**——含光源；hex_prism/dome/hanging_bail 候选须保鸟笼身份（内栖木 + 门 + 托盘），不漂成灯具。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) body_form 5 候选中 flat_top_box/gable_box 标 `world_knowledge_extrapolation` + fork anchor 背书是否接受；(2) family 门禁（box vs round 的 door/support/interior 子集、top_hatch 仅 flat_top、feed 仅 box）是否合理；(3) `n_perches`[1,3] + `bar_density` 两根 multiplicity 轴（perch 进 interior enum，bar_density 独立枚举）；(4) top_hatch captured-hinge 与 side_hinge captured-pin 的 element-scoped allow_overlap 是否为正当 captured 接口而非穿模掩盖；(5) Topology target 112<300 的真实结构上限说明是否接受（round 族门禁收窄）；(6) palette_theme 3 套是否覆盖足够材质大类）。模板已 sweep verdict=pass（pass_rate=1.0，seeds 0-47+corner，failure_triage 空）。|

## 模板实现备注（可选）

- 共享 helper：box 族 `_add_rod`/`_add_arch`/`_build_box_body`/`_build_box_roof`（barrel/flat/gable 顶分支）；round 族 `_mrod_z`/`_mrod_x`/`_mtube`/`_merge`/`_build_round_body`（Torus/tube/dome 子午线 spline）；`_lathe_tray_mesh`（footed/hanging 托盘车削）；`_door_panel_offset`（side/drop/slide 门面板）/`_add_latch`/`_emit_hinge_pin`（captured 销）。
- captured 接口 allow_overlap（`run_bird_cage_tests`）：side/drop_front（`cage_hinge_pin`/`hinge_standoff_{0,1}` × 门铰边框 8 元素 cross-product）；slide_door（`left/right_guide_rail` × `door_*_frame`/`door_lug_*`）；top_hatch（`hatch_hinge_rail`/`hatch_hinge_post_{0,1}`/`spring_rear_rail` × `hatch_frame_rear/left/right`/`hatch_hinge_barrel_{0,1}` cross-product）；latch（`door_latch_boss` × `latch_spindle`）。
- joint 轴/父级关键：side_hinge axis=(0,0,-1)、drop_front axis=(1,0,0)、slide_door PRISMATIC axis=(0,0,1)、top_hatch axis=(-1,0,0)，全 parent=cage；`latch_pivot` parent=door。严守勿混。
- 连通性守护：`strike_standoff` 从 `fixed_door_frame_right` 竖挺（x=dxmax+0.024）桥接到 `latch_strike`；`tray_riser` 撑笼底 rail；perch 端座真实 wire。
- multiplicity：`perch_{i}` `for i in range(n_perches)` 等距分高绝对式；`feed_cup_{i}` `for i in range(n_feed_cups)`；wire 密度 `bar_count` per-face 驱动。全 Rule 1 inline visual。
- 不调 `fail_if_parts_overlap_in_sampled_poses`（run_tests 用 samples=48, ignore_fixed=True）；captured overlap 全走 element-scoped allow_overlap。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A/B/C/D（box 基线）| barrel_vault_box + side_hinge + caster_tray + perch2 | rec_use-…`_291ba037`（002.png）| `cage` L131-267 / `door`+`door_hinge` L284-313 / `latch`+`latch_pivot` L316-337 / `caster_*`+`base_tray` L134-151 / `*_wood_perch` L273-274 | 方箱 chassis + barrel 顶 + 侧铰门+latch + 滚轮托盘 + 双栖木 |
| S1 | A/B/C/D（round 基线）| dome_round + side_hinge + footed_tray + perch1 | rec_pet_animal…`_eaa2a62a`（001.png）| `wire_frame` L119-168 / `access_door`+`frame_to_door` L321-344 / `_base_tray_mesh`+`_top_hook_mesh` L232-315 / `_perch_mesh` L276-319 | 圆 dome chassis + 车削 footed 托盘+顶钩 + 单栖木 |
| S2 | A | flat_top_box | rec_bird_cage_var_skeleton_flattop | flat-top 网格顶（并行 `roof_longitudinal`+`roof_cross_wire`）| 平顶方箱 ③ 候选（载 top_hatch）|
| S3 | A | gable_box | rec_bird_cage_var_roof_gable | 双坡 `roof_rib_{i}_l/r`+`roof_ridge_purlin`+坡 longitudinal | 双坡脊方箱 ③ 候选 |
| S4 | A | hex_prism | rec_bird_cage_var_skeleton_hexagon | `_hex_ring_rails` L105-106 + 6 角点 L33-51 + 6 面 bar + 子午线 | 六棱柱 ③ 候选 |
| S5 | B | drop_front | rec_bird_cage_var_mechanism_dropfront | `door_hinge` REVOLUTE axis=(1,0,0) L338-345 | 底铰下翻门 ② 候选 |
| S6 | B | slide_door | rec_bird_cage_var_mechanism_slidedoor | `left/right_guide_rail` L251-263 + `door_lug` L318-321 + PRISMATIC | 垂直 guillotine 滑门 ② 候选 |
| S7 | B | top_hatch | rec_bird_cage_var_mechanism_topopen | `roof_hatch` part + `hatch_*` 铰 L175-289 | 顶盖掀开 ② 候选 |
| S8 | C | leg_stand | rec_bird_cage_var_support_legstand | 4 `stand_leg`+`apron`+`shelf`+`foot` L103-110 | 四腿落地架 ① 候选 |
| S9 | C | hanging_bail | rec_bird_cage_var_support_hanging | `carry_bail` 提梁 L232-261（无脚）| 吊挂提梁 ① 候选 |
| S10 | D | perch3 | rec_bird_cage_var_n3_perch | loop 3 `perch_{i}` | 栖木 N=3 multiplicity |
| S11 | D | feed cups | rec_bird_cage_var_accessory_feedcups | `feed_cup_{i}`+`feed_bracket_{i}` L279-304 | 前栅喂食杯 N=2 |
| S12 | bar_density | coarse bars | rec_bird_cage_var_n_bars_coarse | per-face `bar_count` 半数粗栅 | wall-bar 密度 coarse 档 |
