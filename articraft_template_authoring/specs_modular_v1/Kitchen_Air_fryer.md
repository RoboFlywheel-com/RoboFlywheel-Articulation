# air_fryer (countertop pull-out-basket air fryer) — Modular Spec

> 来源小类：`picture/Kitchen/Air fryer`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Kitchen__Air_fryer.md`。
> **"air fryer" 在此 = 台式抽屉篮空气炸锅（countertop pull-out-basket air fryer），不是微波炉（microwave，无抽篮 + 旋转门 / 玻璃门）、不是电饭煲（rice cooker，球形保温煲 + 上掀盖 + 内胆，无抽屉挤出篮）、不是烤箱（toaster oven，前开玻璃门 + 烤架）。**
> 结构家族 = 台式炸锅本体（`body`，root，坐地）+ 一只（或多只）下前部口袋里沿 +X PRISMATIC 抽出的炸篮抽屉（`basket_drawer` / `drawer_{i}`）。共享运动学：`drawer_slide` PRISMATIC +X、travel 0→0.16 m；body 顶部带控制面板（触屏 / 旋钮 / 按钮）；body 上缘铜色 trim band。clamshell 候选是唯一把定义运动从 PRISMATIC 改成 REVOLUTE（上掀盖铰链）、并把 `basket` 从 drawer 子件改为 body 固定件的耦合候选。
>
> **同步状态**：本 spec 引用的 8 个 5 星样本（1 个 parent + 7 个 fork 槽位变体）已同步进本仓库 `data/records/`，rating=5。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一核对，IN FULL 读完整 model.py）。引用以 part / joint / helper **名字** 为准（`body`/`basket_drawer`/`drawer_{i}`、`_build_body_shell`/`_build_drum_shell`/`_build_trim_band`/`_build_top_glass`、`_build_drawer_face`/`_build_handle`/`_build_basket`/`_build_fries_heap`、`_build_timer_knob`/`_build_temp_knob`/`_build_dial_shaft`/`_build_escutcheon_plate`/`_build_dial_bezel`/`_build_push_button`、`_build_lid_shell`/`_build_lid_handle`/`_build_hinge_barrel`、`drawer_slide`/`drawer_slide_{i}`/`body_to_timer_knob`/`body_to_temp_knob`/`lid_hinge`、`basket_slide_rail_{idx}`/`slide_rail_{i}_{j}`/`hinge_barrel_{i}` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `air_fryer` |
| template path | `agent/templates/Kitchen_Air_fryer.py` |
| test path (optional) | `tests/agent/test_air_fryer_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: body_silhouette + control + basket_opening 各自挂到共同 `body`（parallel children），**外加** `basket_count` 抽屉多重性轴；basket_opening=clamshell 时改写整树拓扑——见耦合槽说明）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 parent + 7 fork 槽位变体；均 converged，compile success、含 PRISMATIC（或 clamshell 的 REVOLUTE）非 fixed joint、workbench-only）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、run_tests 的 allow_overlap/expect_* 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 8/8 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解，**关键拓扑发现**）：
- **drawer 系（7/8 样本）共享同一拓扑骨架**：1 个 root `body` part（坐地，持有 shell + trim_band + 控制面板 + brand_logo + `basket_slide_rail_*` 轨）+ 1 个 `basket_drawer` part（PRISMATIC +X，承载 `drawer_face`+`window_glass`+`handle`+`basket`+`fries_heap`）。joint 计数 = N 个 PRISMATIC（single=1、dual=2），所有 drawer 样本一致 —— 这是类别身份。**坐标系恒定**：所有样本 +X 前（抽屉滑出方向）、+Y 左、+Z 上、body 坐 z=0；`drawer_slide` origin=(JOINT_X≈0.152, [cy], JOINT_Z≈0.088)、axis=(1,0,0)、travel 0→0.16。
- **body_silhouette 轴（Slot A）**：rounded_taper（parent，`_build_body_shell` 双 filleted-rect sketch loft + CORNER_R 倒角，略内收）/ square_tower（`cq.box` + `edges("|Z").fillet(EDGE_R)` 直角无 taper，更高 0.36）/ cylindrical_drum（`_build_drum_shell` 绕 Z revolve 矩形 profile + 前平面 facet 切除 + D 形 trim + D 形 top_glass）。三者只改 root 主壳 mesh 生成方式（loft / box / revolve）+ trim band profile，**抽屉口袋 + PRISMATIC + drawer 子树拓扑不变** → silhouette 是 mesh-helper 维度，正交于控制 / 开篮机构。
- **control 轴（Slot B）**：digital_touch（parent，`top_glass_panel` 单 smoked-glass Box visual，**0 added joint**，Rule 1）/ rotary_dials（`timer_knob`+`temp_knob` 两个独立 part + `_build_dial_shaft`，**2×REVOLUTE** body_to_timer_knob / body_to_temp_knob axis=(0,0,1)，escutcheon_plate + dial_bezel_{i} body visual；KnobGeometry caps）/ push_buttons（`for i in range(BUTTON_COUNT)` 6 个 `push_button_{i}` 2×3 grid，control_panel matte Box，**0 added joint**，装饰按钮 Rule 1）。→ control 是 part 数 / joint 拓扑变化轴（digital/buttons 无 joint、dials +2 REVOLUTE）。
- **basket_opening 轴（Slot C，耦合槽）**：windowed_drawer（parent，`_build_drawer_face` 带 window 切口 + tinted `window_glass` Box）/ solid_drawer（`_build_drawer_face` 返回实心面板、**删除 window_glass visual**，run_tests 断言 `"window_glass" not in visual_names`）/ clamshell_lid（**整树改写**：body shell 在 SPLIT_Z=0.195 切成下 bowl + 上 `lid`，`basket`+`fries_heap` 变为 **body 固定 visual**（无 drawer、无 PRISMATIC、无 rail），定义运动改 `lid_hinge` REVOLUTE axis=(0,-1,0) 后铰上掀，`hinge_barrel_{i}` 捕获 pin）。windowed/solid 只换 face visual（drawer 树不变）；clamshell **改 part 树 + joint type + basket 归属（drawer→body）** → 这是把 Slot C 视为既决定面板机构又决定 basket 归属与定义运动的耦合槽。
- **basket_count 轴（Slot D 多重性）**：parent=single（`basket_drawer` 单 part，body 宽 0.28）/ dual（`for i in range(NUM_BASKETS)`，`_populate_drawer` 共享 helper + 预建共享 mesh，`drawer_{i}` part + `drawer_slide_{i}` PRISMATIC + body 侧 `slide_rail_{i}_{j}`，中央 `DIVIDER_HALF` 分隔墙，POCKET_CY=±0.090，body 宽 0.40；独立性 test：开 drawer_0 不带动 drawer_1）→ 同构抽屉 N 次复制，N=1 即 parent。
- **palette**：所有 drawer 样本共享 gloss_black 壳 + copper trim/logo/handle + smoked_glass 面板 + basket_metal 篮 + fries_gold 薯条；buttons 另有 matte_panel/button_pad；dials 另有 knob_dark/shaft_steel；clamshell 另有 hinge_metal。→ 4-6 套 colorway（见 §7 palette_style）。

## 核心身份

一台**台式抽屉篮空气炸锅（countertop pull-out-basket air fryer）**：一个坐地的 root `body`（gloss_black 圆角内收方箱 / 直角方塔 / 圆柱鼓，~0.28-0.40 m 宽 × 0.32 m 深 × 0.33-0.36 m 高），下前部有一只（或并排两只）炸篮抽屉，抽屉沿 +X PRISMATIC 滑出（travel 0→0.16 m），抽屉面板带 copper 把手 + 可选观察窗（tinted `window_glass`），抽屉内是开顶 `basket` 炸篮 + `fries_heap` 薯条堆；body 顶部嵌控制面板（smoked-glass 触屏 / 两个旋转 REVOLUTE 旋钮 / 2×3 按钮阵）；body 上缘铜色 `rim_trim_band` + 前面 `brand_logo`；抽屉坐于 body 侧 `basket_slide_rail_*` 滑轨上（2 mm 座入 captured）。活动语义恒为：**炸篮抽屉沿 +X PRISMATIC 抽出**（定义运动；clamshell 候选改为 lid 后铰 REVOLUTE 上掀）+ 可选旋钮 REVOLUTE 旋转。默认成熟域：body_silhouette × control × basket_opening 笛卡尔积 × 篮数 N∈[1,3] 的单 / 双篮台式炸锅。

不该混入：
- **微波炉（microwave）**——大箱体 + 侧开 / 下翻玻璃门 + 转盘 + 大面控制面板，无下前部抽屉炸篮、无 PRISMATIC 篮挤出；门是 REVOLUTE 整面玻璃门而非小上掀盖。
- **电饭煲 / 慢炖锅（rice cooker / slow cooker）**——圆鼓保温煲 + 顶上掀整盖 + 可取内胆 + 提手，无抽屉、无前观察窗、无炸篮挤出；clamshell 候选虽也上掀但本类 lid 是带触控面板的上盖 + 下 bowl 固定炸篮，仍是炸锅形态（若退化成纯保温煲 + 内胆即出类）。
- **烤箱 / 多士炉烤箱（toaster oven）**——前开下翻大玻璃门 + 水平烤架 + 旋钮，运动 spine 是前门 REVOLUTE 整面翻下，无抽屉炸篮挤出。

## 槽位 + 候选模块表

> **建模注记**：air_fryer 是 **root `body`（dispatch silhouette 主壳 mesh + 控制面板硬件 + basket 口袋/滑轨）+ parallel children**。三个 slot 中 **Slot A（body_silhouette）改 root 主壳 mesh + trim/glass profile（不改 drawer 拓扑、不贡献额外 joint）**，**Slot B（control）改顶部控制面板 part 数与 joint 拓扑（digital/buttons 无 joint、dials +2 REVOLUTE）**，**Slot C（basket_opening）改抽屉面板 visual（windowed/solid）或整树改写（clamshell：drawer→lid、PRISMATIC→REVOLUTE、basket→body 固定件）**。clamshell 是耦合槽，与 multiplicity / 滑轨 / drawer 子树强相关，兼容矩阵需特判（见 §9）。Slot D（basket_count）是抽屉多重性轴。

### Slot A：body_silhouette（root 主壳 —— shell mesh + trim/glass profile）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rounded_taper（基线[P]） | rec_model-a-...air-fryer...92e8cb25（parent）| `_build_body_shell` L83-118（双 filleted-rect sketch `loft` + CORNER_R）/ `_build_trim_band` L121-129（圆角  rect ring）| eligible if compatible | 经典紧凑圆角方箱，底部略内收（top 0.32×0.28 → bot 0.30×0.26），lofted between 两 filleted rect sketch；下前部矩形抽屉口袋 cut + 顶部浅 recess |
| square_tower | rec_air_fryer_var_body_square | `_build_body_shell` L78-113（`cq.box` + `edges("\|Z").fillet(EDGE_R≈0.003)`）/ `_build_trim_band` L116-133（sharp rect ring）| eligible if compatible | 直立方塔，统一 footprint（无 taper，深 0.32 宽 0.28 高 0.36），近 90° 竖直锐角、平面；run_tests 检 "tower proportion height>width" + "flat faces no taper" |
| cylindrical_drum | rec_air_fryer_var_body_cylindrical | `_build_drum_shell` L81-134（绕 Z `revolve` 矩形 profile + 前平面 facet box-cut at FLAT_FRONT_X）/ `_build_trim_band` L137-162（D 形 ring）/ `_build_top_glass` L165-180（D 形 glass disk）| eligible if compatible | 圆鼓 footprint 被前平面 facet 截断（抽屉从平面拉出），lathe/revolve primitive；D 形 trim band + D 形 top glass 配合 facet；run_tests 检 "cylindrical footprint width≈depth" + "flat front facet truncates drum" |

### Slot B：control（顶部控制面板 —— part 树 + joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| digital_touch（基线[P]） | rec_model-a-...air-fryer...92e8cb25（parent）| `top_glass_panel` body visual L224-229（单 smoked-glass `Box((0.238,0.198,0.006))` at TOP_GLASS_Z）| eligible if compatible | flush 烟熏玻璃触屏嵌顶部 recess，**0 added joint**（Rule 1，body visual）；cylindrical 用 D 形 `_build_top_glass` mesh 代替 Box |
| rotary_dials | rec_air_fryer_var_control_dial | `_build_timer_knob` L224-236 / `_build_temp_knob` L239-250（KnobGeometry caps）/ `_build_dial_shaft` L253-259 / `_build_escutcheon_plate` L262-279 / `_build_dial_bezel` L282-294 / `timer_knob`+`temp_knob` parts + 2×REVOLUTE L388-431 / allow_overlap L676-682 | eligible if compatible | 两个机械旋钮 part（KnobGeometry cap + dial_shaft），各加一个 vertical-axis **REVOLUTE**（body_to_timer_knob upper≈5.24 / body_to_temp_knob upper≈4.71，axis=(0,0,1)）；body 上 escutcheon_plate + dial_bezel_{i} copper visual；shaft 穿 deck shaft hole（captured allow_overlap）|
| push_buttons | rec_air_fryer_var_control_buttons | `_build_push_button` L214-233 / `control_panel` matte Box visual L259-264 / `for i in range(BUTTON_COUNT)` `push_button_{i}` L266-275（2×3 grid via `_build_push_button(cx,cy)`）| eligible if compatible | matte 面板上凹陷触感按钮阵（BUTTON_ROWS=2 × BUTTON_COLS=3 = 6），loop-emitted 6 个 push_button_{i} body visual，**0 added joint**（装饰按钮 Rule 1）；run_tests 检 grid 3 cols × 2 rows |

### Slot C：basket_opening（开篮机构 —— **耦合槽**，决定抽屉面板 / 整树拓扑 / basket 归属 / 定义运动）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| windowed_drawer（基线[P]） | rec_model-a-...air-fryer...92e8cb25（parent）| `_build_drawer_face` L132-142（box + `window` cut through）/ `window_glass` tinted Box L251-256 / `basket_drawer` part L245-271 / `drawer_slide` PRISMATIC +X L274-282 | eligible if compatible | 抽屉面板带观察窗切口 + 凹陷 tinted 玻璃窗；`basket_drawer` PRISMATIC +X 拉出，`basket` 是 drawer 子件 |
| solid_drawer | rec_air_fryer_var_door_solid | `_build_drawer_face` L131-139（返回实心面板，无 window cut）/ drawer 装配 L241-262（**删除 window_glass visual**）/ `drawer_slide` PRISMATIC L264 / run_tests `"window_glass" not in visual_names` L377-380 | eligible if compatible | 同 PRISMATIC 抽屉但不透明实心前面板（无 window 切口、无玻璃窗）；drawer 子树其余与 windowed 完全相同 |
| clamshell_lid（耦合，swaps 定义运动）| rec_air_fryer_var_door_clamshell | `_build_body_shell` L79-116（split at SPLIT_Z=0.195，下 bowl 中空）/ `_build_lid_shell` L206-258 / `_build_lid_handle` L261-278 / `_build_hinge_barrel` L194-203 / `lid` part L334-352 / `lid_hinge` REVOLUTE axis=(0,-1,0) L355-365 / basket+fries 为 body 固定 visual L312-321 / hinge_barrel allow_overlap L483-502 | eligible if compatible | 顶部上掀蛤壳盖：body 在 SPLIT_Z 切成下 bowl + 上 `lid`（带 top_glass_panel + lid_handle），盖绕后上 rim **REVOLUTE** axis=(0,-1,0) 上掀（upper≈1.8）；`basket`+`fries_heap` 变 **body 固定件**（无 drawer、无 PRISMATIC、无 rail）；`hinge_barrel_{i}` 后铰硬件（captured-pin）。**把 Slot C 的定义运动从 PRISMATIC 改为 REVOLUTE、basket 从 drawer 子件改为 body 固定件** |

### Slot D：basket_count（抽屉多重性轴 —— 详见 §8）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| single（N=1，基线[P]） | rec_model-a-...air-fryer...92e8cb25（parent）| `basket_drawer` 单 part L245-271 / 单 `drawer_slide` L274-282 / 单对 `basket_slide_rail_{idx}` L236-242 | eligible if compatible | 单抽屉单 PRISMATIC，body 宽 0.28；N=1 退化（不进 range 循环） |
| dual（N=2，copy 源） | rec_air_fryer_var_basket_dual | `_populate_drawer` 共享 helper L202-225 / 预建共享 mesh L276-279 / body `slide_rail_{i}_{j}` `for i in range(NUM_BASKETS)` L265-273 / `drawer_{i}` + `drawer_slide_{i}` PRISMATIC `for i` L282-309 / 独立性 test L548-558 | eligible if compatible | 并排两抽屉，中央 `DIVIDER_HALF` 分隔墙，POCKET_CY=±0.090，body 宽 0.40；每篮独立 PRISMATIC（互不联动）；`for i in range(N)` 共享 helper + 共享 mesh 复用 |

## 槽位图（slot graph）

pattern: mixed（固定 named slots: body_silhouette + control + basket_opening 各自挂到共同 `body`（parallel children），外加 `basket_count` 在 `body` 上 N 次复制抽屉子树；basket_opening=clamshell 时整树改写——见下）

```
body (root, 坐地 z=0; 由 body_silhouette 决定主壳 mesh(loft/box/revolve) + trim band + 抽屉口袋 + slide rail 硬件; 由 control 决定顶部面板硬件)
  │
  ├── [control slot]  (互斥三选一)
  │     ├─ digital_touch : top_glass_panel (= body visual, 无 joint, Rule 1)
  │     ├─ rotary_dials  : timer_knob ──[body_to_timer_knob: REVOLUTE axis=(0,0,1), origin=(DIAL_X,-DIAL_Y_OFFSET,BODY_H)]
  │     │                  temp_knob  ──[body_to_temp_knob:  REVOLUTE axis=(0,0,1), origin=(DIAL_X,+DIAL_Y_OFFSET,BODY_H)]
  │     └─ push_buttons  : push_button_{0..5} (= body visual 2×3 grid, 无 joint, Rule 1)
  │
  ├── [basket_opening slot]  (耦合三选一)
  │     ├─ windowed_drawer : basket_drawer ──[drawer_slide: PRISMATIC axis=+X, origin=(JOINT_X,0,JOINT_Z), upper=0.16]  (basket = drawer 子件)
  │     ├─ solid_drawer    : basket_drawer ──[drawer_slide: PRISMATIC axis=+X, origin=(JOINT_X,0,JOINT_Z), upper=0.16]  (basket = drawer 子件, face 无窗)
  │     └─ clamshell_lid   : lid ──[lid_hinge: REVOLUTE axis=(0,-1,0), origin=(HINGE_X,0,HINGE_Z=SPLIT_Z) 后铰线, upper≈1.8]
  │                          basket + fries_heap = body 固定 visual (无 drawer, 无 PRISMATIC, 无 rail)
  │
  └── [basket_count multiplicity 轴]  仅 windowed_drawer / solid_drawer 有效（clamshell 锁 N=1）
        single(N=1): basket_drawer + drawer_slide + basket_slide_rail_{idx}  (body 宽 0.28)
        dual(N=2)+ : drawer_{i} + drawer_slide_{i} + slide_rail_{i}_{j}, POCKET_CY[i]=±(DIVIDER_HALF+POCKET_HW), body 宽随 N 加宽
```

接口点位与 joint 语义：
- **body_silhouette 接口（root，互斥三选一）**：决定 root 主壳 mesh + trim band profile + (cylindrical) top_glass mesh。三者均提供：下前部矩形抽屉口袋（PRISMATIC 抽屉拉出口）+ 顶部 recess（控制面板座）+ body 侧 `basket_slide_rail_*`（抽屉滑轨）。silhouette 与 control / basket_opening 正交（任意主壳可配任意控制 / 开篮机构；cylindrical 的圆 footprint 配 dual 需 facet 加宽，见 §9）。
- **control 接口（顶部，互斥三选一）**：所有控制硬件挂在 body 顶面 recess（z≈BODY_H）。digital_touch / push_buttons 无 joint（Rule 1 body visual）；rotary_dials 各旋钮 REVOLUTE axis=(0,0,1)，origin=(DIAL_X, ±DIAL_Y_OFFSET, BODY_H)（落在 deck shaft hole 硬件上），shaft captured 在 deck hole（allow_overlap）。control 与 basket_opening 正交，但 clamshell 把控制面板移到 lid 顶（digital 的 top_glass_panel 在 lid 上，dials/buttons 与 clamshell 组合需把面板锚点改到 lid 顶 deck，见 §9）。
- **basket_opening 接口（耦合互斥三选一）**：
  - windowed_drawer / solid_drawer：`drawer_slide` PRISMATIC axis=(1,0,0)，origin=(JOINT_X≈0.152, cy, JOINT_Z≈0.088)（落在抽屉口袋开口中心），q=0 闭合 flush、q=0.16 全抽出。basket 是 drawer 子件，bottom 2 mm 座入 body `slide_rail_*` top（captured-slide，allow_overlap + expect_overlap z min≈0.001）；window_glass 凹陷 framed by drawer_face（windowed 有 / solid 无）。
  - clamshell_lid：`lid_hinge` REVOLUTE axis=(0,-1,0)，origin=(HINGE_X=-DEPTH_AT_SPLIT/2, 0, HINGE_Z=SPLIT_Z)（后上 rim 铰线），q=0 盖合 / q≈1.8 上掀。`hinge_barrel_{i}`（body）captured 在 lid rear wall（allow_overlap + expect_overlap z）；trim band 在 SPLIT_Z 缝处包 lid（allow_overlap）；basket+fries 固定 body bowl 内（无 joint、无 rail）。
- **basket_count 接口**：抽屉子树（drawer part + PRISMATIC joint + body 侧 rail）沿 Y **绝对式**对称复制；single 单 `basket_drawer`、dual+ 用 `drawer_{i}`/`drawer_slide_{i}`/`slide_rail_{i}_{j}`，POCKET_CY[i] 由 N 与中央 DIVIDER_HALF 解析（绝对式，不累加漂移），body 宽随 N 加宽（0.28→0.40）。每篮独立 PRISMATIC（互不联动，独立性 test 守）。
- **mating policy**：所有 hinge 是 pin-in-barrel captured-pin（clamshell hinge_barrel）、所有 drawer 是 basket-on-rail captured-slide（2 mm 座入）、dial shaft 是 shaft-in-hole captured。几何均非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：所有 drawer q=0 闭合 flush、clamshell lid q=0 盖合、所有 dial q=0、basket 座 rail / 座 bowl。
- **互斥 / 可选 / 派生**：body_silhouette 三候选互斥；control 三候选互斥（digital/buttons 无 joint、dials +2 REVOLUTE）；basket_opening 三候选互斥（windowed/solid 是 PRISMATIC drawer、clamshell 是 REVOLUTE lid + basket 归 body）。clamshell 取消 drawer 子树 + rail + PRISMATIC → basket_count 失效（clamshell 锁 N=1，见 §9 兼容矩阵）。

## 每槽位 Module Emits / Interfaces

### Slot A / body_silhouette — rounded_taper（基线；square_tower / cylindrical_drum 仅换主壳 + trim mesh helper）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（root，visual: `shell` gloss_black loft 主壳 + `rim_trim_band` copper + `brand_logo` copper + `basket_slide_rail_{idx}` ×2）| parent `_build_body_shell` L83-118 / `_build_trim_band` L121-129 / 装配 L213-242 |
| internal joints | 无（body 是 root，内部无活动件；活动由 control / basket_opening / multiplicity 提供）| — |
| upstream interface | root（坐地 z=0，无父）| parent L213 |
| downstream interface | 下前部抽屉口袋（PRISMATIC 抽屉口）+ 顶部 recess（控制面板座）+ `basket_slide_rail_*`（抽屉滑轨座）| parent L93-117, L236-242 |

### Slot A / body_silhouette — square_tower
| emits | 描述 | 来源 |
|---|---|---|
| parts | 同 rounded_taper 但 `shell` = `cq.box` + `edges("\|Z").fillet(EDGE_R)` 直角方塔（高 0.36），`rim_trim_band` 为 sharp rect ring | square `_build_body_shell` L78-113 / `_build_trim_band` L116-133 |
| downstream interface | 同 rounded_taper（口袋 + recess + rail）| square L88-129 |

### Slot A / body_silhouette — cylindrical_drum
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（`shell` = `_build_drum_shell` revolve + 前 facet 切除；`rim_trim_band` = D 形 ring；`top_glass_panel` = D 形 `_build_top_glass` mesh disk（替代 Box））| cyl `_build_drum_shell` L81-134 / `_build_trim_band` L137-162 / `_build_top_glass` L165-180 |
| downstream interface | 前平面 facet 上的抽屉口袋（FLAT_FRONT_X 处）+ 圆形顶 recess + rail；facet 宽度限 single（dual 需加宽 facet，见 §9）| cyl L99-124 |

### Slot B / control — digital_touch（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`top_glass_panel` 为 body visual）| parent L224-229 |
| internal joints | 无（Rule 1）| — |
| upstream interface | 坐 body 顶 recess（z≈0.3265，cylindrical 用 D 形 mesh）| parent L224-229 / cyl L288-292 |

### Slot B / control — rotary_dials
| emits | 描述 | 来源 |
|---|---|---|
| parts | `timer_knob`（KnobGeometry cap + dial_shaft）+ `temp_knob`（同）；body 加 `escutcheon_plate` + `dial_bezel_{0,1}` copper visual | dial `_build_timer_knob` L224-236 / `_build_temp_knob` L239-250 / parts L388-421 |
| internal joints | `body_to_timer_knob` REVOLUTE axis=(0,0,1) origin=(DIAL_X,-DIAL_Y_OFFSET,BODY_H) upper≈5.24 + `body_to_temp_knob` REVOLUTE axis=(0,0,1) origin=(DIAL_X,+DIAL_Y_OFFSET,BODY_H) upper≈4.71 | dial L400-408, L423-431 |
| upstream interface | dial_shaft 穿 body deck shaft hole（captured，allow_overlap）；knob cap 坐 deck 面 | dial `_build_body_shell` 钻 hole L132-139 / allow_overlap L676-682 |

### Slot B / control — push_buttons
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`control_panel` matte Box + `push_button_{0..5}` 为 body visual，loop-emitted 2×3 grid）| buttons `control_panel` L259-264 / loop L266-275 |
| internal joints | 无（装饰按钮 Rule 1）| — |
| upstream interface | 坐 body 顶面（BUTTON_BASE_Z）；`_build_push_button(cx,cy)` 网格定位 | buttons `_build_push_button` L214-233 / L266-275 |

### Slot C / basket_opening — windowed_drawer（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `basket_drawer`（visual: `drawer_face` 带 window 切口 + `window_glass` tinted Box + `handle` copper + `basket` metal + `fries_heap` gold）| parent `_build_drawer_face` L132-142 / 装配 L245-271 |
| internal joints | `drawer_slide` PRISMATIC axis=(1,0,0) origin=(JOINT_X,0,JOINT_Z) lower=0 upper=0.16 | parent L274-282 |
| upstream interface | basket bottom 2 mm 座入 body `basket_slide_rail_*` top（captured-slide，allow_overlap + expect_overlap z）| parent run_tests L335-354 |

### Slot C / basket_opening — solid_drawer
| emits | 描述 | 来源 |
|---|---|---|
| parts | 同 windowed_drawer 但 `_build_drawer_face` 返回实心面板（无 window cut），**删除 window_glass visual** | solid `_build_drawer_face` L131-139 / 装配 L241-262 |
| internal joints | `drawer_slide` PRISMATIC axis=(1,0,0) origin=(JOINT_X,0,JOINT_Z) upper=0.16 | solid L264 |
| upstream interface | 同 windowed_drawer（basket 座 rail）；run_tests 断言 `"window_glass" not in visual_names` | solid L377-380 |

### Slot C / basket_opening — clamshell_lid（耦合，整树改写）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（下 bowl `shell` split at SPLIT_Z + `rim_trim_band` 缝处 + `brand_logo` + **`basket`+`fries_heap` 固定 visual** + `hinge_barrel_{0,1}`）；`lid`（`lid_shell` + `top_glass_panel` + `lid_handle`）| clamshell `_build_body_shell` L79-116 / basket+fries L312-321 / hinge_barrel L324-331 / lid L334-352 |
| internal joints | `lid_hinge` REVOLUTE axis=(0,-1,0) origin=(HINGE_X,0,HINGE_Z=SPLIT_Z) lower=0 upper≈1.8（**无 drawer_slide PRISMATIC、无 rail**）| clamshell L355-365 |
| upstream interface | `hinge_barrel_{i}`（body 后上 rim）captured 在 lid rear wall（allow_overlap + expect_overlap z）；trim band 包 lid 缝（allow_overlap）；basket 固定 bowl 内 | clamshell allow_overlap L483-523 |

### Slot D / basket_count multiplicity（抽屉子树复制）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drawer_{i}`（drawer_face + window_glass + handle + basket + fries_heap，`_populate_drawer` 共享 helper）+ body 侧 `slide_rail_{i}_{j}` | dual `_populate_drawer` L202-225 / rail loop L265-273 / drawer loop L282-309 |
| joints | `drawer_slide_{i}` PRISMATIC axis=(1,0,0) origin=(JOINT_X, POCKET_CY[i], JOINT_Z) upper=0.16（每篮独立，互不联动）| dual L299-309 |
| placement | `for i in range(N)`，沿 Y 绝对式对称（POCKET_CY[i]=±(DIVIDER_HALF+POCKET_HW)），body 宽随 N 加宽 | dual L36-43, L282-283 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_silhouette | enum | rounded_taper / square_tower / cylindrical_drum | rounded_taper | choice | deterministic procedural sampler 选；决定 root 主壳 mesh + trim/glass profile（互斥）| Slot A 表 |
| control | enum | digital_touch / rotary_dials / push_buttons | digital_touch | choice | sampler 选；digital/buttons 无 joint、dials +2 REVOLUTE（互斥）| Slot B 表 |
| basket_opening | enum | windowed_drawer / solid_drawer / clamshell_lid | windowed_drawer | choice | sampler 选；耦合槽（windowed/solid=PRISMATIC drawer、clamshell=REVOLUTE lid + basket 归 body）| Slot C 表 |
| basket_count (N) | int | 声明域 [1,3]；sweep 采样域 [1,3]（偏小加权：1 高频、2 常见、3 稀疏长尾）| 1 | conditional→slot_choice | 仅 basket_opening∈{windowed,solid} 有效；编入 slot_choice 为 `n{N}`（拓扑维度）；clamshell 锁 N=1（见 §8/§9）| dual 源 / source map |
| palette_style | enum | inox_copper / matte_graphite / retro_cream / stainless_steel / glass_black | inox_copper | palette | palette only，**不计入 slot_choice**；见下方 colorway 说明 | 各样本材质 |
| body_depth_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 body X 主深（保抽屉行程 + 口袋深），clamp | resolve clamp |
| body_height_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 body Z 高 → trim band / 控制面板 / clamshell SPLIT_Z 等比，clamp | resolve clamp |
| basket_width_scale | float | [0.92, 1.08] | 1.0 | independent | 缩放每篮 Y 宽（连带口袋 / face / basket），clamp 使篮仍坐 rail | resolve clamp |
| drawer_travel_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 windowed/solid 有效；缩放 PRISMATIC upper（基 0.16）；clamp ≤ 暴露 basket 所需行程且 ≤ basket 仍保留插入 | parent L46/L281 |
| lid_open_angle_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 clamshell 有效；缩放 lid_hinge REVOLUTE upper（基 1.8）；clamp ≤ 0.95·π（盖不翻穿）| clamshell L363 |
| dial_sweep_scale | float | [0.90, 1.05] | 1.0 | conditional | 仅 rotary_dials 有效；缩放旋钮 REVOLUTE upper（基 5.24/4.71）；clamp ∈(3.0,6.3)（run_tests "realistic sweep"）| dial L407/L430 |
| pocket_spacing_scale | float | [0.92, 1.10] | 1.0 | conditional | 仅 N≥2 有效；缩放并排抽屉 Y 间距（POCKET_CY），clamp 使抽屉不互撞、不超 body 宽 | dual L39 |
| (—) | constraint | — | — | inequality | 抽屉满行程后 basket 仍保留插入：`travel ≤ basket_len − retain_margin`（parent expect_overlap x min≈0.05 at full travel）；违反回缩 drawer_travel | 接口 / captured-slide |
| (—) | constraint | — | — | inequality | N 抽屉排布不超 body 宽：`N·(2·POCKET_HW) + (N−1)·divider + (N+1)·wall ≤ body_width`；body_width 随 N 加宽（single 0.28 / dual 0.40），违反则按比例缩 POCKET_HW / pocket_spacing 或加宽 body | dual L31-43 |
| (—) | constraint | — | — | inequality | clamshell lid 满开角 + basket 固定不冲突：lid 上掀 q=upper 时 lid 净空在 body top 之上（clamshell run_tests "open lid rises above body" / "handle above body top"）；违反回缩 lid_open_angle | clamshell L561-585 |
| (—) | constraint | — | — | conditional | basket_opening=clamshell 时 N 锁 1（无 drawer 子树可复制）；control∈{dials,buttons} 与 clamshell 组合时控制面板锚点改到 lid 顶（非 body 顶，见 §9）；cylindrical_drum × N≥2 需加宽前 facet（FLAT_FRONT_X 容两口袋）| 接口 / §9 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 body_silhouette / control / basket_opening / N 的拓扑**。

**palette_style colorway（5 套，来自 8 个 5★ 源材质）**：
- `inox_copper`（基线）：gloss_black 壳 (0.06,0.06,0.065) + copper trim/logo/handle (0.76,0.44,0.30) + smoked_glass 面板 (0.03,0.03,0.035) + basket_metal 篮 (0.16,0.16,0.16) + fries_gold (0.88,0.62,0.24)（parent / 多数 drawer 样本原色）。
- `matte_graphite`：matte_panel 壳 (0.09,0.09,0.095) + button_pad 灰按钮 (0.16,0.155,0.15) + steel handle + smoked_glass 面板（push_buttons 变体的哑光语义）。
- `retro_cream`：奶油白壳 (0.90,0.88,0.82) + copper trim/dial bezel + knob_dark 旋钮 (0.08,0.08,0.09) + basket_metal（rotary_dials 复古旋钮配色）。
- `stainless_steel`：不锈钢壳 (0.74,0.75,0.77) + shaft_steel 把手 (0.52,0.52,0.54) + smoked_glass + basket_metal（金属机身语义）。
- `glass_black`：全黑壳 + smoked_glass 大面触屏 (0.03,0.03,0.035) + 极简 copper 细 trim + tinted_window (0.12,0.085,0.06)（digital_touch 高端黑配色）。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（并排炸篮抽屉数）：

- **count_param**：`basket_count`（模板内变量 N / NUM_BASKETS；body 下前部并排抽屉数）。
- **N_range**：声明产品域 **[1, 3]**（真实台式 air fryer 基本是 single 或 dual side-by-side；3 篮极少见但结构上沿 Y 可平铺，采样域 ≥ 样本覆盖是正常的；source map 建议 [1,3]，样本覆盖 {1,2}，N=3 由 `for i in range(N)` + 绝对式 POCKET_CY 解析自然外推）。`config_from_seed` 的 sweep 采样域 **[1, 3]**（偏小加权：N=1 高频、N=2 常见、N=3 稀疏长尾）。N=1 即 parent 退化情形（单 `basket_drawer`，不进循环）。
- **sampling domain**：仅 basket_opening∈{windowed_drawer, solid_drawer} 时 `rng.choices((1,2,3), weights=偏小)`；`resolve_config` 把任意外部 config 的 N clamp 到 [1,3]。**basket_opening=clamshell 时不采 N（锁 1）、不编 slot_choice 的 `n{N}`**（无 drawer 子树可复制）。
- **copied object**：单只抽屉子树——`drawer_{i}`（`drawer_face` + `window_glass`(windowed) + `handle` + `basket` + `fries_heap`，由 `_populate_drawer` 共享 helper 发射）外加其 body 侧 `slide_rail_{i}_{j}` 与 PRISMATIC `drawer_slide_{i}`；N 个抽屉复用预建共享 mesh（`_build_drawer_face`/`_build_handle`/`_build_basket`/`_build_fries_heap` 各物化一次复用，符合可读性契约）。
- **naming**：`drawer_{i}` part / `drawer_slide_{i}` joint / `slide_rail_{i}_{j}` rail（嵌套 i=篮、j=轨），`for i in range(N)`（dual L282-309 已用此结构，可直接作 copy-logic 源）；**N=1 取 parent 的单 `basket_drawer` / `drawer_slide` / `basket_slide_rail_{idx}`**（未循环化，等价 range(1)）。
- **placement**：沿 Y **绝对式**等距并排——`POCKET_CY[i]` 以中央分隔墙 `DIVIDER_HALF` 两侧对称分布（single: cy=0；dual: ±(DIVIDER_HALF+POCKET_HW)=±0.090；N=3: 中央 + ±span）。绝对式（每个 i 的 cy 由 N 与中心解析、不累加漂移）是 N-不变前提。body 宽度随 N 加宽（single 0.28 → dual 0.40 → N=3 更宽）。
- **joint policy**：每篮一个独立 PRISMATIC `drawer_slide_{i}`（axis=(1,0,0)），**互不联动**（独立性 test 断言 drawer_0 开不带动 drawer_1，dual L548-558）；活动关节由 basket_opening drawer（PRISMATIC）+ control dials（可选 REVOLUTE）提供，与 basket_count 正交（dials 不随 N 复制）。
- **source/gating**：copy-logic 源取 dual L202-309 的 `_populate_drawer` 共享 helper + `for i in range(NUM_BASKETS)` 循环（rail 嵌套 `for j` + drawer `for i`）；**N=1 即 parent 基线**。basket_count 与 basket_opening 的兼容见 §9（clamshell 锁 N=1）；与 cylindrical_drum 的兼容见 §9（N≥2 需加宽前 facet）。

## 拓扑多样性审计

总组合数（离散槽 + multiplicity，**受 §9 兼容矩阵约束**）：
- 朴素笛卡尔积 = body_silhouette(3) × control(3) × basket_opening(3) = **27**（source map combo 预审）。
- 叠 basket_count：仅 basket_opening∈{windowed,solid} 的格子展开 N∈{1,2,3}（×3），clamshell 锁 N=1（×1）→ 合法组合 = `body(3) × control(3) × [windowed×3N + solid×3N + clamshell×1N] = 3 × 3 × (3+3+1) = 63`。
- 经 §9 兼容矩阵（clamshell × dial/button 面板移 lid + cylindrical × N≥2 facet 加宽），合法组合数仍 **≥ 50**（远超 ≥10 门控）。

仅 control(3) × basket_opening(3) = **9**（含 无 joint / 2×REVOLUTE 旋钮 × PRISMATIC 抽屉 / PRISMATIC 抽屉无窗 / REVOLUTE 上掀盖 的 joint 拓扑组合）≈ 已接近门控；叠 body_silhouette(3) → 27 ≥ 10 已稳过，叠 N 后充裕。

理由：control × basket_opening 提供真正的 joint 拓扑差异（0 joint / +2 REVOLUTE 旋钮 × PRISMATIC drawer / PRISMATIC drawer(无窗) / REVOLUTE lid(basket 归 body) = 含 PRISMATIC×0-2REVOLUTE 与 REVOLUTE-only 的多类 joint-topology），叠 body_silhouette(3) 与 N(3) 后总 ≥50 distinct。**N 必须编入 `slot_choices_for_seed` 的 tuple**（`("basket_count", f"n{N}")`，仅 windowed/solid 时；对齐 cushion pan_count / caulking_gun rib_count / fence_cascade），否则单篮与多篮在 slot_choice 上无法区分，损失一整根拓扑维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（body_silhouette / control / basket_opening），经兼容矩阵合法化（clamshell × dial/button 面板移 lid；cylindrical × N≥2 facet 加宽），再（basket_opening∈{windowed,solid} 时）`rng.choices` 加权 N∈[1,3]，再 uniform 各连续 scale（解析 conditional：drawer_travel 仅 windowed/solid、lid_open_angle 仅 clamshell、dial_sweep 仅 dials、pocket_spacing 仅 N≥2）。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：见 §参数表的 body_depth_scale / body_height_scale / basket_width_scale（independent）/ drawer_travel_scale（conditional@windowed/solid）/ lid_open_angle_scale（conditional@clamshell）/ dial_sweep_scale（conditional@dials）/ pocket_spacing_scale（conditional@N≥2）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（body/control/basket_opening，经兼容矩阵）+（windowed/solid 时）N（解析 conditional 范围）→ 采 independent body_depth/height/basket_width scale → 派生（trim band / 面板 / clamshell SPLIT_Z 随 height scale 等比）→ 用三条 clearance inequality（抽屉满行程保留插入、N 抽屉不超 body 宽、clamshell 开角净空）投影 / 回缩。跨部件依赖（抽屉行程 vs basket 长、N 排布 vs body 宽、lid 角 vs body top）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 drawer/lid/dial origin、captured-slide/pin 接口、N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（经兼容矩阵），basket_opening∈{windowed,solid} 时 `rng.choices` 加权 N∈[1,3]，再 uniform 各 scale | slot_choices_for_seed 含 `("body_silhouette",..),("control",..),("basket_opening",..)` 且 windowed/solid 时含 `("basket_count",f"n{N}")`，与 build 一致 |
| compatibility matrix | (1) **clamshell_lid × basket_count**：clamshell 取消 drawer 子树 + rail + PRISMATIC，basket 固定 body bowl → **N 锁 1**（dual/triple clamshell 罕见且本批无双铰证据样本，source map 已注排除）；basket_opening=clamshell 时不采 N、不编 `n{N}`。 (2) **clamshell_lid × control**：clamshell 把控制面板移到 lid 顶（parent clamshell 的 top_glass_panel 已在 lid 上 L341-346）；dials/buttons 与 clamshell 组合时控制硬件锚点 + REVOLUTE origin 重解析到 **lid 顶 deck**（而非 body 顶），首版可 **gate digital_touch + clamshell**（旋钮 / 按钮 + clamshell 需 lid-顶面板锚点统一化，先 gate），或把 dials/buttons 锚点表达为相对面板 deck 偏移以支持 lid 顶。 (3) **cylindrical_drum × basket_count(N≥2)**：圆鼓前 facet 默认宽度只容单口袋 → N≥2 时加宽 FLAT_FRONT_X facet（容并排两口袋）或 gate cylindrical 仅 N=1；首版可 gate cylindrical × N=1。 (4) **body_silhouette × control × (windowed/solid)**：三者正交（任意主壳 + 任意控制 + 任意 drawer 面板），零风险。 (5) **drawer_travel / pocket_spacing**：drawer 满行程 basket 保留插入、N 抽屉不超 body 宽，违反回缩。 | 无 floating / collision / 抽屉满行程脱出 / N 抽屉互撞或超宽 / clamshell 开盖穿底 / dial 穿面板 / 控制面板漂浮（clamshell 时不在 lid） |
| controlled local variation | 7 个 clamped scale（body_depth/height、basket_width independent；drawer_travel@windowed/solid、lid_open_angle@clamshell、dial_sweep@dials、pocket_spacing@N≥2 conditional），每 build 统一 | 比例变化不破坏 drawer/lid/dial origin、captured-slide/pin 接口、抽屉行程、lid 净空、坐 rail、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 silhouette/control/opening QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_silhouette | 3 | yes | yes | rounded/square/cylindrical，3 种主壳 mesh（loft/box/revolve）|
| control | 3 | yes | yes | digital(0 joint) / dials(2 REVOLUTE) / buttons(0 joint)，3 种控制拓扑 |
| basket_opening | 3 | yes | yes | windowed/solid(PRISMATIC drawer) / clamshell(REVOLUTE lid + basket 归 body)，耦合主机构 |
| basket_count (N) | 3（采样域 {1,2,3}，1 高频 / 3 长尾；仅 windowed/solid）| yes | yes | 拓扑维度，编入 slot_choice；clamshell 锁 N=1 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名（body_silhouette / control / basket_opening），windowed/solid 时含 `("basket_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，basket_count 采样域 ⊆ [1,3]（仅 windowed/solid；clamshell 锁 1）
- `resolve_config` 把 basket_count clamp 到 [1,3]、各 scale clamp 到声明范围；drawer_travel/lid_open_angle/dial_sweep/pocket_spacing 为 conditional 随 basket_opening/control/N 解析；三条 clearance inequality 在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（clamshell 锁 N=1；clamshell × dials/buttons 面板移 lid 或首版 gate digital；cylindrical × N≥2 facet 加宽或首版 gate N=1）
- 连续 scale clamp 后不破坏 drawer/lid/dial origin / captured-slide/pin 接口 / 抽屉行程 / lid 净空 / 坐 rail / N 复制
- 关键 joint：windowed/solid `drawer_slide`/`drawer_slide_{i}` PRISMATIC axis≈(1,0,0)（abs(axis[0])>0.99）upper≈0.16；clamshell `lid_hinge` REVOLUTE axis≈(0,-1,0)（abs(axis[1]+1)<1e-3）upper≈1.8；dials `body_to_timer_knob`/`body_to_temp_knob` 2×REVOLUTE axis≈(0,0,1) upper∈(3.0,6.3)
- captured-slide / pin / shaft：element-scoped `allow_overlap`（drawer `basket`↔body `basket_slide_rail_*`/`slide_rail_{i}_{j}`；clamshell `hinge_barrel_{i}`↔`lid_shell` + `rim_trim_band`↔`lid_shell`；dials shaft↔body deck hole），照搬各样本 run_tests 的 allow_overlap + expect_overlap 段
- copied object 遵循 `drawer_{i}`/`drawer_slide_{i}`/`slide_rail_{i}_{j}` 命名 + 绝对式沿 Y 等距 placement + 每篮独立 PRISMATIC（互不联动）
- grandfather：所有 hinge/slide/shaft captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把 N 当普通 int 参数、不进 slot_choice（windowed/solid 时）→ 单篮与多篮 slot_choice 同形，损失拓扑维度（违反 §8/§9 硬要求）。
- clamshell_lid 与 basket_count>1 组合（双 / 三上掀盖）→ 本批无双铰证据样本、单盖罩对应单一上掀腔；必须 gate（clamshell 锁 N=1）。
- clamshell_lid 仍发射 drawer_slide PRISMATIC + basket_slide_rail + basket 作 drawer 子件 → 错误（clamshell 是 lid REVOLUTE + basket 归 body 固定件，无 drawer/rail/PRISMATIC）；basket_opening 是耦合槽，clamshell 须整树改写。
- clamshell × dials/buttons 时控制面板仍锚在 body 顶（被 lid 切走）→ 面板漂浮 / 穿模；须把控制硬件锚点移到 lid 顶 deck（或首版 gate digital_touch + clamshell）。
- cylindrical_drum × N≥2 不加宽前 facet → 两口袋挤在窄 facet 上互撞 / 超出圆周；须加宽 FLAT_FRONT_X facet（或首版 gate cylindrical × N=1）。
- 把 push_button / dial_bezel / escutcheon / top_glass_panel / basket(clamshell) 当独立活动 part 加 joint → 违反 Rule 1（按钮 / 面板 / 固定篮是非移动 visual；旋钮 cap 才是 REVOLUTE part）。
- drawer / lid / dial rest pose 设成开 / 抽出 / 转角而非 q=0 闭合坐底 → current-pose 与 viewer 目检不符（所有样本 lower=0 闭合）。
- 抽屉满行程后 basket 脱出 body 口袋（travel 过大）→ §7 第一条不等式 FAIL；须回缩 drawer_travel（parent expect_overlap x min≈0.05 at full travel）。
- N 抽屉排布超 body 宽 / 互撞 → §7 第二条不等式 FAIL；须按比例缩 POCKET_HW / pocket_spacing 或随 N 加宽 body。
- drawer/lid/dial origin 放在 body 中心或任意点而非真实口袋开口 / 后铰线 / deck hole → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 给 captured-slide / captured-pin / shaft 接口补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质（palette_style / body scale）当新 candidate 塞进 slot → 不是结构差异。
- 把**微波炉 / 电饭煲 / 烤箱**语义混入（转盘 / 整面玻璃门 / 球形保温煲内胆 / 烤架）→ 出类，本类是抽屉篮台式炸锅。

## 与相邻类别的边界

- 不该混入：**微波炉（microwave）**——大箱体 + 侧 / 下开整面玻璃门（REVOLUTE 大门） + 转盘 + 大面控制面板，无下前部抽屉炸篮、无 PRISMATIC 篮挤出；运动 spine 不同。
- 不该混入：**电饭煲 / 慢炖锅（rice cooker / slow cooker）**——圆鼓保温煲 + 顶整盖上掀 + 可取内胆 + 提手，无抽屉 / 前观察窗 / 炸篮挤出；clamshell 候选虽上掀但本类是带触控面板上盖 + 下 bowl 固定炸篮的炸锅形态（退化成纯保温煲 + 内胆即出类）。
- 不该混入：**烤箱 / 多士炉烤箱（toaster oven）**——前开下翻大玻璃门 + 水平烤架，运动 spine 是前门 REVOLUTE 整面翻下；无抽屉炸篮挤出。
- Kitchen 大类内：区别于无"抽屉炸篮 +(可选)上掀盖 + 顶部控制面板"身份的其它台式厨电（电水壶 / 搅拌机 / 咖啡机）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) body_silhouette 建模为 mesh-helper 维度（loft/box/revolve 主壳 + trim/glass profile，非串联 slot、不贡献 joint）是否接受；(2) N_range 取 [1,3]（样本覆盖 {1,2}，N=3 由共享 helper + 绝对式 POCKET_CY 外推）是否接受；(3) **clamshell_lid 作为耦合槽**（整树改写 drawer→lid、PRISMATIC→REVOLUTE、basket drawer 子件→body 固定件）+ **clamshell 锁 N=1**（dual clamshell 无双铰证据样本）是否接受；(4) clamshell × dials/buttons 首版 gate digital_touch（旋钮 / 按钮 + clamshell 需 lid-顶面板锚点统一化）是否接受，还是要求一开始就实现 lid-顶控制面板锚点重解析；(5) cylindrical_drum × N≥2 首版 gate N=1（避免窄 facet 双口袋互撞）还是要求加宽 facet；(6) Topology target ~50-63 <300 的说明是否接受（clamshell 锁 N=1 收窄 + 厨电真实结构上限）；(7) palette_style 5 套 colorway 是否覆盖足够。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：body 主壳按 silhouette 分（`_build_body_shell` loft（rounded）/ box+fillet（square）/ `_build_drum_shell` revolve（cylindrical）；clamshell 用 split 版 `_build_body_shell`）；`_build_trim_band`（按 silhouette：圆角 rect / sharp rect / D 形）；cylindrical 另有 `_build_top_glass`（D 形 disk）；control 按候选分（digital=`top_glass_panel` Box / D 形 mesh；dials=`_build_timer_knob`/`_build_temp_knob`(KnobGeometry)/`_build_dial_shaft`/`_build_escutcheon_plate`/`_build_dial_bezel`；buttons=`_build_push_button`+loop）；basket_opening 按候选分（windowed/solid=`_build_drawer_face`(带/无 window)+`_build_handle`+`_build_basket`+`_build_fries_heap`；clamshell=`_build_lid_shell`/`_build_lid_handle`/`_build_hinge_barrel`+固定 basket）。N 复制复用 `_populate_drawer` + 预建共享 drawer mesh（face/handle/basket/fries 各物化一次）。
- captured 接口 allow_overlap：`run_air_fryer_tests` 里逐机构补 element-scoped `allow_overlap`（drawer `basket`↔body rail（single: `basket_slide_rail_{idx}` parent L335-345 / dual: `slide_rail_{i}_{j}` L377-395）；clamshell `hinge_barrel_{i}`↔`lid_shell` + `rim_trim_band`↔`lid_shell` L483-523；dials shaft↔body deck hole L676-682），照搬各样本 run_tests 段 + expect_overlap。
- 耦合槽实现（**最关键实现点**）：basket_opening=clamshell 时走 **独立 root 装配分支**——split body shell（下 bowl）+ `lid` part + `lid_hinge` REVOLUTE + basket/fries 作 body 固定 visual（**不发射 drawer / rail / PRISMATIC**），N 锁 1，control 面板锚点移 lid 顶；basket_opening∈{windowed,solid} 时走 drawer 分支（口袋 + rail + PRISMATIC + `for i in range(N)` 抽屉复制）。两分支是 basket_opening 派生的整树切换，不是单纯 face 换皮。
- conditional 范围解析顺序：先采 body_silhouette → control → basket_opening（经兼容矩阵：clamshell 锁 N + 面板移 lid、cylindrical × N≥2 facet）→ windowed/solid 时采 N → 解析 drawer_travel（windowed/solid）/ lid_open_angle（clamshell）/ dial_sweep（dials）/ pocket_spacing（N≥2）→ 采 body_depth/height/basket_width independent → 派生 trim/面板/SPLIT_Z → 投影三条 clearance inequality。
- N=1 退化：直接用 parent 的单 `basket_drawer` / `drawer_slide` / `basket_slide_rail_{idx}`（不进 range 循环），等价 range(1)；N≥2 走 dual 的 `_populate_drawer` + `for i in range(N)`（rail 嵌套 `for j`）。
- 参考模板：`agent/templates/Accessories_Cushion.py`（同为 mixed pattern：固定 named slots + `("count",f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 mesh 复用 + 兼容矩阵 gating + captured allow_overlap 骨架，**且含一个改写整树/换定义运动的耦合机构候选**（cushion 的 clamshell/slide lid 改 joint 拓扑），本类 clamshell_lid 耦合槽可同构改编）；`agent/templates/Handtools_caulking_gun.py`（含 root body + parallel children + conditional multiplicity + 坐标族分支兼容矩阵，本类两 basket_opening 装配分支可借鉴）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C/D（parent 基线）| rounded_taper + digital_touch + windowed_drawer + single | rec_model-a-...air-fryer...92e8cb25 | `_build_body_shell` L83-118 / `_build_trim_band` L121-129 / `top_glass_panel` L224-229 / `_build_drawer_face`(window) L132-142 / `basket_drawer` L245-271 / `drawer_slide` PRISMATIC L274-282 / rail allow_overlap L335-354 | rounded 主壳 + digital 面板 + windowed drawer + single 基线 + captured-slide 范式 |
| S2 | A | square_tower | rec_air_fryer_var_body_square | `_build_body_shell`(box+fillet) L78-113 / `_build_trim_band`(sharp rect) L116-133 | 方塔主壳 mesh helper（drawer 树不变）|
| S3 | A | cylindrical_drum | rec_air_fryer_var_body_cylindrical | `_build_drum_shell`(revolve+facet) L81-134 / `_build_trim_band`(D) L137-162 / `_build_top_glass`(D) L165-180 | 圆鼓主壳 + D 形 trim/glass（lathe revolve primitive）|
| S4 | B | rotary_dials | rec_air_fryer_var_control_dial | `_build_timer_knob` L224-236 / `_build_temp_knob` L239-250 / `_build_dial_shaft` L253-259 / `_build_escutcheon_plate` L262-279 / 2×REVOLUTE L388-431 / allow_overlap L676-682 | 两旋钮 part + 2×REVOLUTE（vertical axis）+ shaft-in-hole captured |
| S5 | B | push_buttons | rec_air_fryer_var_control_buttons | `_build_push_button` L214-233 / `control_panel` L259-264 / loop `push_button_{i}` L266-275 | 2×3 按钮阵（loop-emitted body visual，无 joint）|
| S6 | C | solid_drawer | rec_air_fryer_var_door_solid | `_build_drawer_face`(solid) L131-139 / 装配(删 window_glass) L241-262 / run_tests L377-380 | 实心抽屉面板（无窗，drawer 树同 windowed）|
| S7 | C | clamshell_lid（耦合）| rec_air_fryer_var_door_clamshell | `_build_body_shell`(split) L79-116 / `_build_lid_shell` L206-258 / `_build_lid_handle` L261-278 / `_build_hinge_barrel` L194-203 / `lid_hinge` REVOLUTE L355-365 / basket+fries body 固定 L312-321 / allow_overlap L483-523 | 上掀蛤壳盖（REVOLUTE，整树改写 + basket 归 body）|
| S8 | D（multiplicity）| basket_count N=2 | rec_air_fryer_var_basket_dual | `_populate_drawer` L202-225 / 共享 mesh L276-279 / rail `for i` L265-273 / `drawer_{i}`+`drawer_slide_{i}` `for i` L282-309 / 独立性 test L548-558 | 双抽屉 copy-logic 源（共享 helper + 共享 mesh + 绝对式 POCKET_CY + 独立 PRISMATIC）|
