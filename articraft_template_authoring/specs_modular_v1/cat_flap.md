# cat_flap (Pet_Animal related / Cat flap) — Modular Spec

> 来源小类：`Pet_Animal related / Cat flap`（articraft_data 上游小类样本池）。
> 上游 source map：`articraft_template_authoring/picture_source_maps/Pet_Animal_related__Cat_flap.md`。
> **一个装在宿主面板 / 门 / 墙上的、猫可推穿的框边开口，由一片可上掀摆动的 flap 关闭。** 不是窗 / 舷窗 / 通风口 / 信箱口 / 柜门。
> 结构家族 = 单个接地 `panel_frame`（宿主面板 / 穿墙隧道 liner + 圆角矩形 / 圆形 bezel 开口 + 硬件），托一片（或前后两片）顶铰 REVOLUTE 摆动 flap，加可选滑动锁 / 电子芯片模块。**每个 seed 必须有 ≥1 个真实开启关节**（swing flap 的 top-hinge REVOLUTE）。
>
> **同步状态**：本 spec 引用的 7 个 5 星样本（2 origin + 5 fork 槽位变体）已在本仓库 `data/records/`，rating=5，category_slug=`cat_flap`。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一全文读完核对）。引用以 part / joint / helper **名字**为准（`panel_frame` / `front_trim` / `flap` / `frame_to_flap` / `inner_seal` / `hinge_pin` / `lock_slider` / `sensor_housing` / `mode_button` / `tunnel_wall_*` / `rear_frame` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `cat_flap` |
| template path | `agent/templates/cat_flap.py` |
| test path (optional) | `tests/agent/test_cat_flap_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（root `panel_frame`（parallel parent）+ opening_form / host_context / frame 固定形态轴叠在 frame 上，**外加** 主活动件 swing flap（top-hinge REVOLUTE）与可选 slide-lock（PRISMATIC）/ 电子 mode_button（REVOLUTE），含 flap-count 与 screw-count 多重性）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7（2 origin + 5 fork 槽位变体；均 PASS，compile success、≥1 非 fixed joint）|
| read_count | 7（**全部读完整 `model.py`**，不抽样；含每个样本的 helper、part 树、articulation 与 run_tests 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 7/7 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **两个 origin 是同一结构**：宿主薄面板 `panel_frame`（door_panel cutout + 圆角矩形 bezel `front_trim` + `inner_seal` + 螺钉 + 顶铰硬件 `hinge_pin`/`hinge_lug`/`hinge_boss` + 底部磁吸 `frame_magnet`/`magnet_mount`）+ 单片顶铰摆动 `flap`（`translucent_panel`/`flap_panel` + `hinge_sleeve`/`moving_hinge_barrel` + 磁吸 keeper + 边封 lips）+ 1 个 REVOLUTE `frame_to_flap`（axis=(1,0,0) 顶铰）。P001 用 `BezelGeometry`（圆角矩形），P002 用 cadquery `_rounded_ring`；仅宿主（木 / 玻璃）、trim helper、螺钉数不同，结构相同。
- **opening_form 轴**（Slot A，③ Primary Form Family / Planar Boundary）：rounded_rect（两 origin + 多数 fork，`BezelGeometry(...,opening_shape="rounded_rect")` + 矩形 `translucent_panel`）/ circular（`rec_cat_flap_var_form_round`，`opening_shape="circle"` 圆 bezel + 圆盘 flap `_flap_disc`/`_edge_ring`）。改 trim / door cutout / inner_seal / flap 的可识别平面轮廓，part 树 / 顶铰关节不变。
- **host_context 轴**（Slot B，① 骨架）：door_thin_panel（两 origin，薄 `door_panel` cutout 单面板宿主）/ wall_tunnel_liner（`rec_cat_flap_var_skeleton_tunnel`，去 door_panel，加 4 面 `tunnel_wall_*` 深隧道 liner + 末端 `rear_frame` 环，穿墙式）。
- **closure_lock 轴**（Slot C，② 关节类型）：magnet_latch（两 origin，仅磁吸闩，无额外关节）/ slide_lock（`rec_cat_flap_var_mechanism_slider`，加 `lock_slider` 刚性盖板捕获于 `guide_rail_0/1`，新增 1 个 **PRISMATIC** `frame_to_lock_slider` 跨开口滑动）。swing flap 恒在。
- **control_module 轴**（Slot D，① 骨架）：none（两 origin，仅磁吸）/ electronic_microchip（`rec_cat_flap_var_skeleton_microchip`，加 `sensor_housing`+`housing_flange`+`battery_cover`+`antenna_ring`+`led`+`button_boss` 固定件 + `mode_button` 旋钮 REVOLUTE `housing_to_mode_button`）。
- **flap 多重性**（Slot B/C 内子轴，N）：single（两 origin，1 flap）/ double（`rec_cat_flap_var_n2_dualflap`，前 + 后两片顶铰 flap 沿隧道深度 Y 串列，各自独立 REVOLUTE，共享 `_add_flap` helper）。
- **screw 多重性**（④ cosmetic，N）：N∈{4（P001），6（P002）}，两 origin 各示；螺钉是 ④-class fastener，loop 发 `screw_head_i`/`screw_slot_i`，编进 slot_choice 供覆盖。

## 核心身份

一个**猫门 / 宠物门**（Pet_Animal related / Cat flap）：装在宿主门 / 玻璃 / 墙板上的一个**框边 pet-sized 开口**，开口由一套 bezel/trim 框住（圆角矩形或圆形），口内挂一片（或穿墙隧道式前后两片）**顶铰摆动 flap**，猫推 flap 穿过；flap 底部有磁吸闩自动回位。可选加：手动 **4-way 滑动锁**（`lock_slider` 沿开口 PRISMATIC 滑出封住 flap）、**电子芯片选择性进入模块**（RFID `antenna_ring` + `sensor_housing` + `battery_cover` + `mode_button` 旋钮）。宿主 = 薄门板 / 穿墙深隧道 liner；开口 = 圆角矩形 / 圆形；螺钉 4 / 6。默认成熟域 = opening_form × host_context × closure_lock × control_module × flap-count × screw-count 的一扇猫门。活动语义 = **flap 顶铰上掀开启**（≥1 个 REVOLUTE）＋可选滑动锁 / 旋钮。

不该混入：
- **窗 / 舷窗 / 通风口 / 风道（window / porthole / vent / air duct）**——无 pet passage；本类是猫可推穿的、带磁吸摆动 flap 的宠物开口。
- **信箱口 / 邮件槽（mail slot / letterbox）**——细长投信口，无 pet-sized 开口 + 猫穿摆动 flap。
- **柜门 / 普通铰接板（cabinet door / plain hinged panel）**——无框边 pet 开口，只是一块铰板。
- **门铃 / 对讲 / 摄像头 / 智能锁面板（doorbell / intercom / camera / smart-lock）**——electronic_microchip 候选借电子模块，但整体仍是带摆动 flap 的猫门，不是纯电子面板。

## 槽位 + 候选模块表

> **建模注记**：`opening_form`（A）改 trim / door cutout / seal / flap 的**平面轮廓形态**（圆角矩形 vs 圆），part 树 / 顶铰不变 → ③ Planar Boundary。`host_context`（B）改宿主骨架（薄面板 vs 穿墙隧道 liner+rear_frame）→ ①。`closure_lock`（C）加不加 PRISMATIC 滑动锁 → ②。`control_module`（D）加不加电子芯片模块（含 mode_button REVOLUTE）→ ①。所有活动件（flap / slider / mode_button）都挂 root `panel_frame`（parallel children）。

### Slot A：opening_form（开口形态 —— ③ Primary Form Family / Planar Boundary）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| rounded_rect（基线）| forked_anchor | rec_...__001（P001）+ rec_...__002（P002）| P001 `front_trim` BezelGeometry rounded_rect L87-102 / `_panel_with_cutout` rect L39-48 / `inner_seal` L104-119 / `translucent_panel` Box L183-188 | Planar Boundary Form | eligible if compatible | 圆角矩形开口 + 矩形 flap 板 + 矩形 bezel/seal；四边 lips 封边 |
| circular（圆盘）| forked_anchor | rec_cat_flap_var_form_round | `front_bezel` circle L113-126 / `_panel_with_cutout` circle L39-46 / `_flap_disc`/`_edge_ring` L49-65 / 圆 `inner_seal` L129-142 / 45° 螺钉环 L144-162 | Planar Boundary Form | eligible if compatible | 圆形 porthole 开口 + 圆盘 flap `translucent_panel` + 圆环 `edge_ring` + 圆 bezel/seal；螺钉 45° 环布 |

### Slot B：host_context（宿主骨架 —— ① 骨架图）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / 结构特征 |
|---|---|---|---|---|---|
| door_thin_panel（基线）| forked_anchor | rec_...__001（P001）+ rec_...__002（P002）| P001 `door_panel`（`_panel_with_cutout` mesh）L79-85 | eligible if compatible | 薄宿主面板 `door_panel`（cutout 单面板，木 / 玻璃 / 白），trim + 硬件嵌在其上；开口深度薄 |
| wall_tunnel_liner（穿墙隧道）| forked_anchor | rec_cat_flap_var_skeleton_tunnel | 去 `door_panel`，`tunnel_wall_0..3`（4 面 liner 深度 ~0.15）L73-90 / `rear_frame` 环 L92-99 | eligible if compatible | 无大面板，`front_trim` 环 + 4 面 `tunnel_wall_*` liner 沿深度贯穿 + 末端 `rear_frame` 环；穿墙式，提供 flap-double 所需深度 |

### Slot C：closure_lock（关闭机构 —— ② 关节类型）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|---|
| magnet_latch（基线）| forked_anchor | rec_...__001（P001）+ rec_...__002（P002）| P001 `magnet_mount`/`frame_magnet` L159-170 + flap `flap_magnet` L218-223 | eligible if compatible | 仅磁吸自动闩：frame 底 `frame_magnet` + flap 底 `flap_magnet` keeper；无额外关节（swing flap 是唯一活动件）|
| slide_lock（4-way 滑锁）| forked_anchor | rec_cat_flap_var_mechanism_slider | `guide_rail_0/1` L182-189 / `lock_slider`（`lock_panel`+`slider_grip_tab`）L275-288 / **PRISMATIC** `frame_to_lock_slider` axis=(0,0,-1) L292-305 | eligible if compatible | 加 `lock_slider` 刚性盖板捕获于两侧 `guide_rail_*`，沿开口 **PRISMATIC** 下滑封 flap（q=0 缩回 flap 自由 / q=travel 封住）；swing flap 仍在 |

### Slot D：control_module（控制模块 —— ① 骨架图 / ② 旋钮）

| module_name | source_type | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / 结构特征 |
|---|---|---|---|---|---|
| none（基线）| forked_anchor | rec_...__001（P001）+ rec_...__002（P002）| P001 全 frame 无电子模块 | eligible if compatible | 无电子件，仅磁吸猫门（手动） |
| electronic_microchip（RFID 芯片）| forked_anchor | rec_cat_flap_var_skeleton_microchip | `sensor_housing`+`housing_flange` L194-206 / `battery_cover`+`battery_latch` L209-224 / `antenna_ring`（bezel 环）L226-247 / `led`+`button_boss` L250-265 / `mode_button`（KnobGeometry 旋钮）+ REVOLUTE `housing_to_mode_button` L336-370 | eligible if compatible | 顶部 `sensor_housing` 盒 + `battery_cover` + 绕开口 `antenna_ring`（RFID 线圈，随 opening_form 圆 / 方）+ `led` + `mode_button` 旋钮（REVOLUTE axis=(0,1,0)）；不挡 flap 路径 |

> **候选数说明**：A/B/C/D 均降到 2 candidate —— 原因：cat flap 是 source map §Budget 标注的 **simple band（低词汇量）** 物体，5 星样本池每根轴只有 2 种真实结构形态（rect/round、door/tunnel、magnet/slide、none/electronic），均 source-backed（origin + 对应 fork）。每 slot ≥2 结构不同候选成立且非单候选 slot；进一步扩（roll-up 帘 / N≥3 louver）会漂向 vent/window 邻类（source map §Blocked），故止于 simple band 顶。多样性由 4 个 2-候选离散 slot × 2 根多重性轴（flap-count / screw-count）叠出（见 §9 拓扑审计）。

## 槽位图（slot graph）

pattern: mixed（root `panel_frame` 为共同 parent（parallel children）；opening_form / host_context / control 的固定件都发在 `panel_frame`；活动件 flap / lock_slider / mode_button 挂到 `panel_frame`）

```
panel_frame (root; opening_form 决定 trim/seal/cutout 平面轮廓 + host_context 决定宿主(薄板|隧道liner+rear_frame)
             + 螺钉/顶铰硬件/磁吸; closure_lock=slide_lock 时另发 guide_rail_*; control=electronic 时另发
             sensor_housing/antenna_ring/battery_cover/led/button_boss)
  │
  ├── flap_{i}  (N∈[1,2]; single=1 前 flap; double=前+后两片沿隧道深度 Y 串列, 反向上掀)
  │     └─[frame_to_flap_{i}: REVOLUTE axis=±(1,0,0), origin=顶铰线, lower=0 闭合 / upper≈0.85 上掀]
  │
  ├── lock_slider   (仅 slide_lock)
  │     └─[frame_to_lock_slider: PRISMATIC axis=(0,0,-1), origin=开口上缘缩回位, lower=0 缩回 / upper≈travel 封住]
  │
  └── mode_button   (仅 electronic_microchip)
        └─[housing_to_mode_button: REVOLUTE axis=(0,1,0), origin=housing 面 button_boss, 旋钮原地转]
```

接口点位与 joint 语义：
- **opening_form 接口**：rounded_rect 用 `BezelGeometry(opening_shape="rounded_rect")` 发 `front_trim`/`inner_seal`，rect `door_panel` cutout，矩形 `flap` 板 + 四边 lips；circular 用 `opening_shape="circle"` 圆 bezel + 圆 cutout + 圆盘 `flap` + `edge_ring`。flap 板轮廓随之圆 / 方，但顶铰 joint 语义（axis / origin=顶铰线）不变 → 与 B/C/D 正交。
- **host_context 接口**：door_thin_panel 发大 `door_panel`（trim / 硬件嵌其上）；wall_tunnel_liner 去 `door_panel`，发 `front_trim` 环 + `tunnel_wall_0..3`（沿 −Y 深度贯穿，两端 overlap 进 front_trim / rear_frame 保连通）+ `rear_frame` 环。硬件 / flap 顶铰仍在前面 `_plane`。
- **flap 接口（挂 root `panel_frame`）**：flap `hinge_sleeve`（part 原点）↔ frame `hinge_pin`/`hinge_lug`/`hinge_boss`（captured-pin）；`frame_to_flap_{i}` REVOLUTE axis=±(1,0,0)，origin=`(0, HINGE_Y, HINGE_Z)`（落在顶铰硬件上），lower=0 闭合（flap 悬垂封口）/ upper≈0.85·scale 上掀（front flap +Y 向外掀、rear flap −Y 向内掀，反向不撞）。
- **closure_lock 接口**：slide_lock 的 `lock_slider` `lock_panel` 捕获于 frame `guide_rail_0/1` C 槽（captured-slide）；`frame_to_lock_slider` PRISMATIC axis=(0,0,-1)，origin=开口上缘缩回位，lower=0 缩回（flap 自由）/ upper≈travel 下滑封 flap（滑板扫过 seal / magnet 为 intentional overlap，element-scoped allow_overlap）。
- **control 接口**：electronic 的 `sensor_housing`/`antenna_ring`/`battery_cover`/`led`/`button_boss` 都是 `panel_frame` visual（固定，不挡 flap 上掀路径，发在开口上方 / 四周）；`mode_button` 旋钮挂 frame，`housing_to_mode_button` REVOLUTE axis=(0,1,0)，origin=`button_boss` 面，原地旋转（不位移）。antenna_ring 用 bezel 随 opening_form 圆 / 方共形。
- **mating policy**：flap 顶铰 = pin-in-sleeve captured-pin、slider = shoe/panel-in-rail captured-slide、mode_button = boss-mounted 旋钮 —— 几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry`(0.015) 守 origin（prismatic 豁免）+ element-scoped `allow_overlap` 守 captured / 闭合 bedding overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：flap q=0 闭合（悬垂封口、磁吸对齐）；slider q=0 缩回（flap 自由）；mode_button q=0。
- **互斥 / 可选 / 派生**：closure_lock / control_module 各独立二选一；flap-count double 仅 rounded_rect+wall_tunnel_liner 有效（需隧道深度串前后两片）；slide_lock 仅 rounded_rect（矩形滑板）；screw N=6 仅 rounded_rect（圆用 45° 4 螺钉）。见 §8 / §9。

## 每槽位 Module Emits / Interfaces

### Slot A / opening_form — rounded_rect（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `panel_frame` visual：`front_trim`(BezelGeometry rounded_rect)+`inner_seal`(rounded_rect)；flap `translucent_panel`(Box)+四边 lips | P001 L87-119,183-216 |
| internal joints | 无（形态轴） | — |
| downstream interface | 圆角矩形开口平面 + 顶铰线（供 flap / lock / antenna 接入） | P001 L30-36 |

### Slot A / opening_form — circular
| emits | 描述 | 来源 |
|---|---|---|
| parts | `front_trim`(circle bezel)+圆 `inner_seal`；flap 圆盘 `translucent_panel`(`_flap_disc`)+`edge_ring`；45° 螺钉环 | form_round L113-162,199-240 |
| internal joints | 无 | — |
| downstream interface | 圆形开口平面 + 顶铰线（弦跨开口顶） | form_round L31-35 |

### Slot B / host_context — door_thin_panel / wall_tunnel_liner
| emits | 描述 | 来源 |
|---|---|---|
| parts | door：大 `door_panel`(cutout mesh)；tunnel：去 door_panel，`tunnel_wall_0..3`+`rear_frame` 环 | P001 L79-85 / tunnel L73-99 |
| internal joints | 无 | — |
| downstream interface | 前面 trim/seal/硬件平面（door）或 front_trim 环 + 隧道深度（tunnel，供 double flap rear 片） | P001/tunnel |

### Slot C / closure_lock — magnet_latch / slide_lock
| emits | 描述 | 来源 |
|---|---|---|
| parts | magnet：frame `magnet_mount`/`frame_magnet` + flap `flap_magnet`；slide：另发 frame `guide_rail_0/1` + `lock_slider`(`lock_panel`+`slider_grip_tab`) | P001 L159-170,218-223 / slider L182-189,275-288 |
| internal joints | slide：`frame_to_lock_slider` PRISMATIC axis=(0,0,-1)（lower=0/upper≈travel） | slider L292-305 |
| upstream interface | slide：`lock_panel` ↔ frame `guide_rail_*` captured-slide | slider L182-189 |

### Slot D / control_module — none / electronic_microchip
| emits | 描述 | 来源 |
|---|---|---|
| parts | none：无；electronic：frame `sensor_housing`+`housing_flange`+`battery_cover`+`battery_latch`+`antenna_ring`+`led`+`button_boss` + `mode_button` 旋钮 | microchip L194-265,336-351 |
| internal joints | electronic：`housing_to_mode_button` REVOLUTE axis=(0,1,0)（原地旋转） | microchip L357-370 |
| upstream interface | electronic：`mode_button` ↔ frame `button_boss` 面（旋钮座） | microchip L259-265 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| opening_form | enum | rounded_rect / circular | rounded_rect | choice | sampler 选；③ Planar 开口形态 | module table A |
| host_context | enum | door_thin_panel / wall_tunnel_liner | door_thin_panel | choice→conditional | sampler 选；① 宿主骨架 | module table B |
| closure_lock | enum | magnet_latch / slide_lock | magnet_latch | choice→conditional | sampler 选；② 加不加 PRISMATIC 滑锁 | module table C |
| control_module | enum | none / electronic_microchip | none | choice | sampler 选；① 加不加电子模块 | module table D |
| n_flaps (N_flap) | int | 声明域 [1,2]；sweep 采样域 [1,2]（偏 1 加权）| 1 | conditional→slot_choice | double 仅 rounded_rect+wall_tunnel_liner；编 slot_choice `n{N}`；否则 n1 | dualflap |
| n_screws (N_screw) | int | 声明域 [4,6]；sweep 采样域 {4,6}（rect）/ 4（circle）| 4 | conditional→slot_choice | ④ cosmetic；6 仅 rounded_rect；编 slot_choice `n{N}` | P001(4)/P002(6) |
| palette_style | enum | warm_white / charcoal_wood / brushed_metal / graphite_glass / cream_wood（5）| warm_white | palette | 材质 / 配色（trim 塑料 / 金属、host 玻璃 / 木、flap translucent） | 各样本材质 |
| opening_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放开口 + trim + flap 尺寸（保比例，重导 hinge_z / flap 尺寸）| P001 dims |
| flap_swing_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 `frame_to_flap` upper（上掀角），clamp 到安全上界 | 各样本 motion_limits |
| slide_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 slider PRISMATIC travel（仅 slide_lock），clamp | slider L44 |
| (—) | constraint | — | — | conditional | double 仅 rounded_rect+wall_tunnel；slide 仅 rounded_rect；screw6 仅 rounded_rect（resolve 内解析）| §8 |
| (—) | constraint | — | — | inequality | flap 上掀包络不撞 tunnel_wall / 邻 flap（前 +Y / 后 −Y 反向）；slider travel 不超开口高 | 接口 / clearance |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每 build 解析一次。scale 只动开口 / flap 比例 / 关节行程 —— **绝不改变 opening_form / host_context / closure_lock / control_module / N 的拓扑**。

### 7.5 编译预算 / compile budget（必填）

自报每-seed 编译预算 **≤ 12s**（典型 5-9s）。依据：主身份是薄 bezel / box / cylinder，唯一 mesh 是 `door_panel` cutout（cadquery，tolerance≈0.0008）+ 2-3 个 BezelGeometry（trim/seal/antenna）+ 可选圆盘 flap mesh —— 均轻量布尔，无复杂放样 / 大 N 复制（flap ≤2、screw ≤6、guide_rail ×2）。分档 tessellation：bezel corner / 圆盘 ≤32 段；door_panel cutout mesh tolerance 0.0008。N 个相同子件（flap / screw）复用同一几何构造。超预算先降精度再迭代。

## Multiplicity / Copy Logic

**2 根 multiplicity 轴**（条件激活）：

**轴 1 — n_flaps（flap 片数，结构）**
- **count_param**：`n_flaps`（沿宿主深度 Y 串列的顶铰 flap 数）。
- **N_range**：声明产品域 **[1,2]**；sweep 采样域 **[1,2]**（偏小加权：1 高频 / 2 常见）。source map 建议 [1,2]；**N=2 仅 rounded_rect+wall_tunnel_liner**（穿墙隧道提供前后两片串列所需深度；薄门板无深度、圆形无 double 源）。N≥3 会读成 louver/vent（source map §Blocked）→ 不采。
- **copied object**：单片 `flap_{i}`（`translucent_panel`+`hinge_sleeve`+lips+`flap_magnet`），共享 `_build_flap(model, frame, r, mats, index, hinge_y, sign)` helper；N 个复用同一几何。
- **naming**：`flap_{i}` / joint `frame_to_flap_{i}`，`for i in range(N)`（N=1 即单前片；dualflap L296-308 用此循环）。
- **placement**：沿 Y 串列——front flap（i=0）hinge 在前面 `HINGE_Y`（+Y 向外掀，axis=(+1,0,0)）；rear flap（i=1）hinge 在隧道末端 `−tunnel_depth+…`（−Y 向内掀，axis=(−1,0,0)）；**反向上掀确保两片全程不撞**。
- **joint policy**：每片独立 `frame_to_flap_{i}` REVOLUTE，统一 range（0..0.85·scale）；captured-pin 顶铰 grandfather + element-scoped allow_overlap（照搬 dualflap run_tests）。
- **source/gating**：源取 dualflap `_add_flap` L44-100 + loop L296-308；N=1 取 origin 单 flap（等价 range(1)）。仅 rounded_rect+wall_tunnel 激活；否则 n1 sentinel。

**轴 2 — n_screws（螺钉数，④ cosmetic）**
- **count_param**：`n_screws`（trim 上装饰螺钉数）。
- **N_range**：声明产品域 **[4,6]**；sweep 采样域 rect {4,6} / circle {4}。source N=4（P001）/6（P002）均 origin-shown。
- **copied object**：`screw_head_{i}`+`screw_slot_{i}`（Cylinder+Box），loop 发；rect 4 角（+2 中边 = 6），circle 4 个 45° 环布。
- **naming**：`screw_head_{i}`/`screw_slot_{i}`，`for i in range(N)`。
- **placement**：rect 绝对式角 + 中边；circle 45° 半径环。
- **joint policy**：FIXED 装饰 → 按 Rule 1 **写成 `panel_frame` visual，不作独立 part**（无关节）。
- **source/gating**：6 仅 rounded_rect；circle 恒 4。编进 slot_choice `n{N}`。

（跨轴共享的采样 helper 待第三个 multiplicity 模板出现再抽，不提前抽象。）

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加 / 减会动的 part 或一条边 | **有** | host_context（door_thin_panel / wall_tunnel_liner+rear_frame，① 宿主骨架）+ control_module（none / electronic_microchip 加 sensor_housing/antenna/battery/mode_button，① 加件+旋钮 part）+ flap-count（single/double 加一片会动 flap part）。全 `forked_anchor`（2 origin + tunnel/microchip/dualflap fork）|
| └ multiplicity | 同构件 ×N | **有** | 见 §8：n_flaps [1,2]（dualflap）+ n_screws {4,6}（P001/P002）；n_flaps 条件激活（rect+tunnel），编 slot_choice |
| ② 关节类型 | 图不变，某边换 type / 轴 | **有** | REVOLUTE（swing flap 顶铰 axis=±(1,0,0)、mode_button axis=(0,1,0)）+ **PRISMATIC**（slide_lock axis=(0,0,-1)）。全 `forked_anchor`；两种类型在 sweep 都出现（slide_lock / electronic 采样时）|
| ③ 主体形态家族 | 图 & 关节不变，换核心 part 可识别几何原型 | **有** | opening_form slot 登记进 slot_choices：rounded_rect（矩形开口 + 矩形 flap 板 + 矩形 bezel）vs circular（圆 porthole + 圆盘 flap + 圆环 edge_ring + 圆 bezel），form_subtype=**Planar Boundary Form**（核心开口 / flap 截面轮廓）。均 source-backed（origin rect + form_round fork）|
| ④ 表面装饰 | 原型不变，叠表面细节 | **有** | 螺钉 `screw_head`/`screw_slot`（数 4/6 档，随 opening_form 角布 / 45° 环共形）+ `gasket`/seal 条 + 磁吸条 + electronic 的 `led`/`battery_latch` decal + 圆盘 `edge_ring`。`record_only`；派生顺序 ③（圆 / 方）→⑤（尺寸）→④（螺钉沿最终 trim 边发）|
| ⑤ 尺寸 / 行程 | 离散不变，只连续改尺寸 / 行程 | **有** | opening_scale [0.90,1.12]（开口 + trim + flap 保比例）、flap_swing_scale [0.85,1.10]、slide_travel_scale [0.85,1.10]。运动包络（见 §motion_test_plan）：flap REVOLUTE axis=±(1,0,0) 上掀 [0,~0.85·scale]（front +Y / rear −Y）；slider PRISMATIC axis=(0,0,-1) 下滑 [0,~travel]；mode_button REVOLUTE 原地旋 [0,~1.5π]。**每非-continuous 关节全程跑 `fail_if_parts_overlap_in_sampled_poses` + targeted `ctx.pose` 证开启方向**。`record_only` |
| ⑥ 涂装 | 几何不变，只改材质 / 颜色 | **有** | palette_style 5 档：warm_white / charcoal_wood / brushed_metal / graphite_glass / cream_wood；trim（塑料白 / 炭 / 奶 · 金属 brushed）+ host（玻璃 green-tint / 木 / 白）+ flap（smoky / frosted translucent）都变。材质大类覆盖 plastic + metal + glass + wood ≥ ceil(0.5×5)=3。`record_only`（各样本材质）|

**motion_test_plan**：flap —— sampled collision（每 flap 关节 {0,lower,upper,mid}，max_pose_samples=64；double 时 2 关节 combos）+ targeted `ctx.pose({frame_to_flap_0: ~0.8·swing})` 断言 flap 板 / 磁吸沿开启方向位移（front：+Y 且 z 抬升；rear：−Y 且 z 抬升）。slide_lock —— sampled + targeted `ctx.pose({frame_to_lock_slider: travel})` 断言 `lock_slider` z 下降 > 0.2 覆盖开口（+ slider 扫过 seal/magnet 的 element-scoped allow_overlap）。electronic —— targeted `ctx.pose({housing_to_mode_button: π/2})` 断言旋钮原地转（xz 不动）。captured overlap（顶铰 pin↔sleeve、slider panel↔rail、闭合 flap bed 到 inner_seal/front_trim、magnet↔frame_magnet、antenna↔hinge_sleeve）用 element-scoped `allow_overlap` 照搬各样本。double flap 前 +Y / 后 −Y **反向上掀**，全程不互撞。

**收尾自检**：0-9 seed 渲染须肉眼见 —— opening_form 圆 / 方拉得开、host 薄板 vs 穿墙隧道可辨、slide_lock 滑板 / electronic 芯片模块出现且不挡 flap、double flap 前后两片、5 palette 材质大类都出现、flap 上掀全程不穿模、rest pose flap 闭合。

## 采样与覆盖审计

总组合数：opening_form(2) × host_context(2) × closure_lock(2) × control_module(2) × n_flaps(≤2) × n_screws(≤2) ≈ 2×2×2×2×2×2=**64**（含条件 gating 后有效组合略少：circular 分支收敛 slide/double/screw6 → 约 40+ 有效离散组合）。

仅 opening_form(2) × closure_lock(2) × control_module(2) = **8**（含 REVOLUTE flap + PRISMATIC slide + REVOLUTE 旋钮 的 joint-拓扑 × 圆 / 方 form）；叠 host / n_flaps / n_screws 后 ≥ 40。

理由：cat flap 是 simple-band 低词汇物体；离散多样性来自 4 个 2-候选 slot（rect/round ③、door/tunnel ①、magnet/slide ②、none/electronic ①）＋ 2 根多重性轴（flap-count / screw-count）。**N 必须编入 `slot_choices_for_seed`**（`("n_flaps", f"n{N}")` / `("n_screws", f"n{N}")`），否则单 / 双 flap、4 / 6 螺钉在 slot_choice 无法区分。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` opening_form / host_context / closure_lock / control_module，`rng.choice` palette，再按 gating 采 n_flaps（rect+tunnel→[1,2] 偏 1；否则 1）、n_screws（rect→{4,6}；round→4），再 uniform 采 opening_scale / flap_swing_scale / slide_travel_scale。compatibility matrix 合法化组合。无 regression overrides（首版纯 procedural）。random sweep seeds 0-35 初轮 + corner；0-999 成熟审计；viewer 目检 0-9。

Topology target：64 组合采样空间下，1000-seed slot choice tuple distinct 预计接近真实结构上限（~40-64）。**低于 300 说明**：cat flap 是 source map §Budget 明确标注的 simple band（低词汇量猫门）；真实结构 = opening_form(2)×host(2)×closure(2)×control(2)×flap-N(2)×screw-N(2) 这几组拓扑等价类（组合上限 ~64），受真实结构词汇表约束，进一步扩会漂向 window/vent 邻类。report-only，不设门，不反推上游变体数量。

Controlled local parameterization：opening_scale（independent [0.90,1.12]，保比例缩开口 + trim + flap，重导 hinge_z / flap 尺寸）、flap_swing_scale（independent [0.85,1.10]，缩 flap upper）、slide_travel_scale（independent [0.85,1.10]，缩 slider travel）。全部 `resolve_config` clamp。采样契约：先采离散 slot + palette + N（conditional gating）→ 采 3 个 independent scale → clamp。opening_scale 保比例（equation：trim/flap 尺寸 = k·opening），避免破 flap 装配；无跨部件独立自由变量各抽各。scale 不破 hinge 接口 / captured 接口 / N 复制 / 类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 四离散 slot + palette，按 gating 采 n_flaps/n_screws，再 uniform 3 scale | slot_choices_for_seed 含 `("n_flaps",n{N})`/`("n_screws",n{N})` 且与 build 一致 |
| compatibility matrix | (1) **n_flaps=2 仅 rounded_rect+wall_tunnel_liner**（需深度 + 矩形源；否则 n1）。 (2) **slide_lock 仅 rounded_rect**（矩形滑板；circular → magnet_latch）。 (3) **n_screws=6 仅 rounded_rect**（circle 恒 4 个 45°）。 (4) opening_form / control_module 与其它正交（antenna_ring 随圆 / 方共形；electronic 与任意 host / closure 兼容）。 (5) flap 上掀包络：single/前 flap +Y 向外、rear flap −Y 向内反向，全程不互撞、不撞 tunnel_wall。 | 无 floating / collision / 滑锁挡 flap / electronic 挡 flap / flap 撞隧道壁 / 缺开启关节 |
| controlled local variation | opening_scale / flap_swing_scale / slide_travel_scale 三 clamped scale，每 build 统一 | 比例变化不破 hinge origin / captured / N / 身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-35 初轮 + corner；0-999 成熟审计 | axis_realization（两 opening / 两 host / 两 closure / 两 control / flap-N / screw-N 直方图） |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| opening_form | 2 | yes | no | 圆角矩形 / 圆（③ Planar；池仅此二真实形态，simple band 降 2 有据）|
| host_context | 2 | yes | no | 薄门板 / 穿墙隧道（池仅此二真实宿主）|
| closure_lock | 2 | yes | no | 磁吸 / 滑锁（+PRISMATIC）（池仅此二）|
| control_module | 2 | yes | no | 无 / 电子芯片（池仅此二）|
| n_flaps | 2（{1,2}）| yes | no | 条件激活（rect+tunnel）；编 slot_choice |
| n_screws | 2（{4,6}）| yes | no | ④ cosmetic；6 仅 rect；编 slot_choice |

## Validator
- `slot_choices_for_seed` 返回已实现 module 名，且含 `("n_flaps",f"n{N}")` 与 `("n_screws",f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling；seed=0 不特殊
- `resolve_config`：gating（double 仅 rect+tunnel / slide 仅 rect / screw6 仅 rect）；opening_scale/flap_swing/slide_travel clamp；每 build 解析一次
- compatibility matrix / gating 阻止非法组合（double 错 host/form、slide 错 form、screw6 错 form）
- 每 seed 必有 ≥1 非 fixed 开启关节（swing flap REVOLUTE）；机构主关节 axis / type 断言（flap REVOLUTE axis≈±(1,0,0)；slide PRISMATIC axis≈(0,0,-1)；mode_button REVOLUTE axis≈(0,1,0)）
- Rule 5：非 fixed 关节 → `fail_if_parts_overlap_in_sampled_poses` + 每机构 ≥1 targeted `ctx.pose` 证开启位移 / 方向
- captured-pin / slide：element-scoped `allow_overlap`（顶铰 pin↔sleeve / slider panel↔rail / 闭合 flap bed 到 inner_seal·front_trim / magnet↔frame_magnet / antenna↔hinge_sleeve），照搬各样本 run_tests 段
- copied object 遵循 `flap_{i}` / `screw_head_{i}` 命名 + 绝对式 placement + 共享 helper
- grandfather：所有 captured 接口省略 MatingContract，由 origin(0.015) + allow_overlap 守（prismatic origin 豁免）
- Rule 1：不动的 `screw_*`/`gasket`/`led`/`antenna_ring`/`sensor_housing`/`edge_ring` 写成 `panel_frame` visual，不作独立 FIXED part
- Rule 3：circular 圆盘 flap 保 `_flap_disc`/`_edge_ring` mesh；连续 scale 不破接口
- 连续 scale clamp 后不破 hinge origin / captured / N 复制 / 身份

## Reject cases
- 某 seed 无任何开启关节（纯固定框）→ 出类 FAIL（每 seed 必有 swing flap REVOLUTE）。
- 把 n_flaps / n_screws 当普通 int、不进 slot_choice → 单 / 双 flap、4 / 6 螺钉 slot_choice 同形，损失拓扑维度。
- n_flaps=2 配 door_thin_panel / circular（无隧道深度 / 无 double 源）→ 前后片无深度串列、撞或悬空；double 须 gate 到 rect+tunnel。
- double flap 前后同向上掀（都 +Y）→ 后片扫进前片，sampled-pose collision FAIL；须前 +Y / 后 −Y 反向。
- slide_lock 配 circular（矩形滑板套圆口）→ 语义 / 几何不符；slide 须 gate 到 rounded_rect。
- 把顶铰 pin↔sleeve / slider panel↔rail 补 MatingContract 硬对接 → 几何对不上 mating-gap FAIL；应 grandfather + allow_overlap。
- 把不动的 `screw_*`/`gasket`/`led`/`antenna_ring`/`sensor_housing` 当独立 FIXED part → 违反 Rule 1（应 inline 为 `panel_frame` visual）。
- flap rest pose 设成张开而非 q=0 闭合 → current-pose 与目检不符（应 q=0 悬垂封口）。
- flap 顶铰 origin 放开口中心而非顶铰线硬件 → `fail_if_articulation_origin_far_from_geometry`(0.015) FAIL。
- circular 圆盘 flap 降级成 Box（丢 `_flap_disc`/`edge_ring` mesh）→ 违反 Rule 3。
- 把"窗 / 舷窗 / 通风口 / 信箱口 / 门铃面板"语义混入 → 出类（本类是带磁吸摆动 flap 的猫门）。
- 把连续尺寸 / 颜色 / 材质当新 candidate 塞进 slot → 不是结构差异。

## 与相邻类别的边界
- 不该混入：**窗 / 舷窗 / 通风口 / 风道**——无 pet passage；本类是猫可推穿的、带磁吸摆动 flap 的宠物开口。
- 不该混入：**信箱口 / 邮件槽**——细长投信口，无 pet-sized 开口 + 猫穿摆动 flap。
- 不该混入：**柜门 / 普通铰接板**——无框边 pet 开口，只是一块铰板。
- 不该混入：**门铃 / 对讲 / 摄像头 / 智能锁面板**——electronic 候选借电子模块，但整体仍是带摆动 flap 的猫门。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核：确认 (1) 4 个 slot 均降 2 候选（simple band 池仅二形态）是否接受；(2) n_flaps=2 gate 到 rounded_rect+wall_tunnel_liner（需深度 + 矩形 double 源）；(3) slide_lock / screw6 gate 到 rounded_rect；(4) double flap 前 +Y / 后 −Y 反向上掀防互撞建模是否忠实；(5) flap q=0 闭合（悬垂封口）rest pose 约定。|

## 模板实现备注（可选）
- 共享 helper：`_make_bezel(op,outer,depth,is_round,...)`（trim/seal/antenna bezel）；`_panel_cutout_mesh(r)`（door_panel cadquery cutout，rect/circle）；`_build_flap(model, frame, r, mats, index, hinge_y, sign, front)`（flap 多重性 + 圆 / 方分支）；`_build_electronic(frame, r, mats)`（芯片模块 visual）+ `mode_button` part；`_build_slide_lock(model, frame, r, mats)`（guide_rail + lock_slider）；螺钉 loop helper。
- captured 接口 allow_overlap：`run_cat_flap_tests` 里逐机构补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（P001 L254-278 hinge_pin↔hinge_sleeve / 闭合 flap↔trim / magnet；slider L386-406 panel↔seal/magnet + shoe↔rail；microchip L394-426 hinge_sleeve↔antenna_ring）。
- conditional 解析顺序：先采 opening_form / host_context / closure_lock / control_module → gating（slide/screw6 依 rect；double 依 rect+tunnel）→ 采 palette → 采 3 scale → clamp。
- 材质 role-key（`mats` dict）：trim / seal / flap / flap_edge / metal / magnet / host / liner / housing / antenna / button / led（5 palette 各给 trim + host + flap 一套色，其余硬件色共享）。
- 坐标系约定：采 P001 `BezelGeometry` frame（door_panel 在 XY 平面 rpy=(-π/2,0,0)；+Y=前 / 外，−Y=后 / 内；开口居中于原点）。**flap 建在 q=0 闭合（悬垂）位**——直接用各 flap visual 传给源 `_flap_origin` 的原始 (x,y,z)（= angle=0 悬垂位）作 raw Origin，joint lower=0/upper≈0.85·scale，与源已验证的 closed pose 等价。
- 参考模板：`agent/templates/greenhouse_vent_roof.py`（mixed pattern：root frame + 机构轴 + `("n",f"n{N}")` 进 slot_choice + 条件 gating + captured-pin element-scoped allow_overlap + palette dict + `_MECHANISM_BUILDERS` dispatch + Rule 5 sampled poses，本类同构改编）。

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A/B/C/D 基线 | rounded_rect + door_thin_panel + magnet_latch + none（N=4）| rec_...__001（P001，BezelGeometry frame）| `_panel_with_cutout` L39-48 / `front_trim`/`inner_seal` bezel L87-119 / 螺钉 L123-141 / hinge L143-170 / `flap`+lips L172-223 / `frame_to_flap` REVOLUTE L225-238 / allow_overlap L254-278 | 主坐标系 + 圆角矩形猫门 + 顶铰 flap + 磁吸 + captured-pin 范式 |
| S0b | A/D | rounded_rect + screw N=6 | rec_...__002（P002，cadquery frame）| `_rounded_ring`/`_rounded_panel` L21-41 / 6 螺钉 L152-172 / tunnel_side/top/sill L100-123 / flap L189-213 / `frame_to_flap` L215-223 | 螺钉 N=6 源 + 短隧道 sleeve 参照 |
| S1 | A | circular | rec_cat_flap_var_form_round | `_panel_with_cutout` circle L39-46 / `_flap_disc`/`_edge_ring` L49-65 / circle bezel L113-142 / 45° 螺钉 L144-162 / 圆盘 flap L199-240 | 圆形 porthole ③ Planar 形态（圆盘 mesh Rule 3）|
| S2 | B | wall_tunnel_liner | rec_cat_flap_var_skeleton_tunnel | `tunnel_wall_0..3` L73-90 / `rear_frame` 环 L92-99 / 去 door_panel | 穿墙深隧道 liner + rear_frame（① 骨架 + double flap 深度源）|
| S3 | C | slide_lock | rec_cat_flap_var_mechanism_slider | `guide_rail_0/1` L182-189 / `lock_slider` L275-288 / **PRISMATIC** `frame_to_lock_slider` L292-305 / allow_overlap L386-406 | 4-way 滑锁 PRISMATIC + rail/panel captured-slide（② 关节类型）|
| S4 | D | electronic_microchip | rec_cat_flap_var_skeleton_microchip | `sensor_housing`/`housing_flange` L194-206 / `battery_cover` L209-224 / `antenna_ring` bezel L226-247 / `led`/`button_boss` L250-265 / `mode_button` KnobGeometry + REVOLUTE L336-370 / allow_overlap L387-426 | RFID 电子芯片模块（① 骨架 + 旋钮 REVOLUTE）|
| S5 | B（multiplicity）| n_flaps N=2 | rec_cat_flap_var_n2_dualflap | `_add_flap(model,frame,index,hinge_y,...)` L44-100 / 前 + 后 flap loop L296-308 / 双面 hinge/gasket L262-290 | flap 多重性 copy-logic 源（前后串列，共享 helper）|
