# switch (European wall light switch / socket plate) — Modular Spec

> 来源小类：`picture/Other/Switch`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Other__Switch.md`。
> **"Switch" 在此 = 欧式墙面开关/插座面板（European wall switch plate）**：一块坐在墙上的薄面板（root=墙板，FIXED 接 faceplate），面板上横向并排 N 个**执行件**（rocker 跷跷板 / toggle 拨杆 / push button 按钮 / rotary dimmer 旋钮），可选一只**静态 Schuko 插座**模块。不是闸刀开关、不是船舶/工业控制台、不是路由器面板。
>
> **同步状态**：本 spec 引用的 8 个 5 星样本（1 个 parent + 7 个 fork 槽位/multiplicity 变体）已同步进本仓库 `data/records/`，rating=5。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一读全核对）。引用以 part / joint / helper **名字**为准（`wall_panel` / `faceplate` / `rocker_{i}` / `toggle_{i}` / `button_{i}` / `dimmer_{i}` / `*_pivot` / `*_press` / `*_spin` / `_plate_mesh` / `_trim_ring_mesh` / `_rocker_mesh` / `_toggle_lever_mesh` / `_button_mesh` / `_dimmer_knob_mesh`），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `switch` |
| template path | `agent/templates/Other_Switch.py` |
| test path (optional) | `tests/agent/test_switch_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: actuator_type + faceplate_shape 各挂共同 `faceplate`（parallel children），**外加** `gang_count` 执行件多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（1 parent + 4 actuator 变体 + 2 faceplate 变体 + 2 gang_count 变体；均 converged，compile=success、≥1 非 fixed joint、workbench-only）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、placement 公式与 run_tests 的 allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 8/8 全部被采纳，无未采用样本，无 contamination |

阅读要点（用于槽位分解）：
- **共享骨架（所有 8 样本一致）**：`wall_panel`（root，warm-beige `Box` 墙板，origin y=-WALL_T/2，墙面在 y=0）→ FIXED `wall_to_faceplate` → `faceplate`（child；visual = `plate_field`（ivory `_plate_mesh`）+ `trim_ring`（chrome `_trim_ring_mesh`），用 `_CQ_TO_WALL=(-π/2,0,0)` 把 cq +Z 映到 world +Y 出墙）。执行件全部以 `faceplate` 为 parent，沿 X 等距并排。坐标系：+Z 上、plate 宽沿 X、面朝 +Y、墙面 y=0。（**wall-local** 约定，模板内所有 mesh/joint 均按此授权；模板在 `wall_to_faceplate` 上额外加 yaw=π，使世界系正面朝 **-Y** —— 那才是 preview/gallery 相机所在的 +X/-Y 象限，朝 +Y 会渲成墙板背面。）
- **actuator_type 轴（Slot A，主机构槽）**：4 个候选是**真正的 joint 拓扑变化**——rocker(`rocker_{i}_pivot` REVOLUTE axis=(1,0,0) ±0.10 跷跷板) / toggle(`toggle_{i}_pivot` REVOLUTE axis=(1,0,0) ±0.35 拨杆翻转，pivot 在面前) / push_button(`button_{i}_press` PRISMATIC axis=(0,-1,0) 0..0.003 压入) / rotary_dimmer(`dimmer_{i}_spin` CONTINUOUS axis=(0,1,0) 自由旋转)。每个候选自带不同的 `_plate_mesh` 开口（rocker/button=方 pocket 带薄底；toggle=raised escutcheon + 窄 slot；dimmer=圆 shaft hole）与不同的 actuator mesh（`_rocker_mesh` loft 凸盖 / `_toggle_lever_mesh` 锥形 loft / `_button_mesh` 阶梯 cap+guide / `_dimmer_knob_mesh` KnobGeometry）。
- **faceplate_shape 轴（Slot B，足迹）**：rounded_rect_horizontal（parent，横向圆角矩形 + chrome 圆角矩形 ring + **Schuko 插座** tile）/ square_single（方形 0.082×0.082，圆角方 ring，**无 Schuko**，WALL 缩小到 0.18）/ round_plate（圆形 0.17 dia，圆环 chrome ring lathe，**无 Schuko**）。三者只改 `_plate_mesh`/`_trim_ring_mesh` 的 **mesh profile + Schuko 有无**，**part 树 / joint 拓扑不变**（actuator 仍是同样的 child + 同样 joint）→ faceplate_shape 是 mesh-footprint 维度，非串联 slot、不贡献额外 joint。
- **gang_count 轴（multiplicity）**：N=1（`rec_..._e21d2998`，单 rocker 居中，`_make_rocker` helper + `ROCKER_X = tuple(i*PITCH-(N-1)*PITCH/2 for i in range(N))`）/ N=2（parent，两 rocker）/ N=4（`rec_..._e3244d88`，四 rocker，`ROCKER_X = tuple((i-(N-1)/2)*PITCH for i in range(N))`，**TRIM_W/PLATE_W/WALL_W 随 N 放大**）。同构执行件 N 次复制（绝对式等距 placement），N 与 actuator_type 自由组合（N 个同类型执行件）。
- **Schuko 插座**：rounded_rect_horizontal 上的**静态**模块（raised `tile` + 真空 `well`（`circle.extrude` cut）+ 两 pin hole + `ground_clip_upper`/`ground_clip_lower` steel `Box`），无独立 joint，inline 进 `faceplate` visual / `_plate_mesh`。是 horizontal 面板的身份件，但随 faceplate_shape 派生（方/圆变体省略）。

## 核心身份

一块**欧式墙面开关/插座面板**：薄 warm-beige 墙板（root）上 FIXED 接一块横向（或方/圆）**面板**（matte ivory `plate_field` + 抛光 chrome `trim_ring`，~0.010-0.012 m 出墙），面板沿 X 等距并排 **N 个执行件**——宽 rocker 跷跷板 / 小 toggle 拨杆 / 方 push button / 圆 rotary dimmer 旋钮，每个执行件是 `faceplate` 的独立活动 child（REVOLUTE / PRISMATIC / CONTINUOUS）。横向面板右端可带一只**静态 Schuko 插座**（raised tile + 真空圆 well + 双 pin hole + 上下 steel 接地夹）。默认成熟域：actuator_type × faceplate_shape × gang_count N∈[1,6] 的墙面面板（完整笛卡尔积）。活动语义 = **执行件的开关动作**（rocker 翻 ±0.10 / toggle 翻 ±0.35 / button 压 0..0.003 / dimmer 自由旋）。

不该混入：
- **闸刀开关 / knife switch / 工业断路器把手**——本类是住宅墙面薄面板，执行件小且并排，非杠杆闸刀。
- **船舶/航空/机柜控制面板（按钮阵列 + 屏幕 + 拨码开关混排）**——本类是单一执行件词汇 + 可选单插座，非多功能仪表盘。
- **路由器 / 配电箱 / 接线盒面板**——无并排住宅执行件语义。
- **门铃 / 恒温器 / 单按钮设备**——单功能、非"N 个并排开关位"的面板形态。

## 槽位 + 候选模块表

> **建模注记**：`faceplate_shape`（Slot B）是 `faceplate` 同一组 mesh（plate_field + trim_ring + 可选 Schuko）**的足迹形态**（横矩形 / 方 / 圆），由 footprint-aware mesh helper（`_plate_mesh` / `_trim_ring_mesh`）一次决定，**不是独立串联 slot、不贡献额外 joint**；列为候选轴以对齐 schema，它与 actuator_type / gang_count 的笛卡尔积共同撑开多样性（见 §9）。`actuator_type`（决定执行件 part 树 + joint 拓扑）与 `gang_count`（multiplicity）才是真正改拓扑的轴。

### Slot A：actuator_type（**主机构槽 / 执行件词汇表**——决定并排执行件的 part 树与 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| rocker（基线） | rec_model-a-...-mo_..._c46f379f（parent）| `_rocker_mesh` L181-203 + 方 pocket cut（`_plate_mesh`）L153-159 + `rocker_{i}` part + `pivot_axle` L259-274 + `rocker_{i}_pivot` REVOLUTE L275-288 | eligible if compatible | 宽凸方 paddle（loft base+cap），`rocker_{i}_pivot` **REVOLUTE** axis=(1,0,0) origin=(xc,ROCKER_PIVOT_Y,0) lower=-0.10/upper=+0.10 跷跷板；`pivot_axle` steel `Cylinder` 沿 X，tips 捕获在 pocket 侧壁（captured-pin allow_overlap）|
| toggle_lever | rec_variant-actuator-type-toggle-lever-...-t_..._5e9273bf | `_toggle_lever_mesh` L189-211 + raised escutcheon + 窄 slot cut（`_plate_mesh`）L139-167 + `toggle_{i}` part + `pivot_axle` L267-282 + `toggle_{i}_pivot` REVOLUTE L283-296 | eligible if compatible | 小锥形拨杆（loft 两 profile，tip 缩 82%），`toggle_{i}_pivot` **REVOLUTE** axis=(1,0,0) origin=(xc,TOGGLE_PIVOT_Y=PLATE_DEPTH,0) lower=-0.35/upper=+0.35 上下翻；pivot 在面前突出 escutcheon slot，`pivot_axle` tips 捕获 slot 壁（captured-pin）|
| push_button | rec_variant-actuator-type-push-button-...-tw_..._531fc067 | `_button_mesh` L174-197 + 方 pocket cut（`_plate_mesh`）L145-152 + `button_{i}` part L255-261 + `button_{i}_press` PRISMATIC L262-275 | eligible if compatible | 方 cap + 窄 guide 阶梯按钮（cap 比 pocket 宽，seat on rim），`button_{i}_press` **PRISMATIC** axis=(0,-1,0) origin=(xc,PLATE_DEPTH,0) lower=0/upper=0.003 压入；cap flange seat on pocket rim（element-scoped allow_overlap，无 pivot pin）|
| rotary_dimmer | rec_variant-actuator-type-rotary-dimmer-...-_..._f19a560b | `_dimmer_knob_mesh`（KnobGeometry）L177-191 + 圆 shaft hole cut（`_plate_mesh`）L148-155 + `dimmer_{i}` part + `knob_body`/`shaft_stub` L251-275 + `dimmer_{i}_spin` CONTINUOUS L279-287 | eligible if compatible | 圆 skirted 旋钮（`KnobGeometry` tapered + ribbed grip + raised pointer），`dimmer_{i}_spin` **CONTINUOUS** axis=(0,1,0)（front-normal）origin=(xc,DIMMER_BASE_Y=PLATE_DEPTH,0) 自由旋；`shaft_stub` steel `Cylinder` 穿 plate 圆孔挂住旋钮（captured，allow_overlap shaft↔plate_field）|

### Slot B：faceplate_shape（面板足迹——plate_field+trim_ring+可选 Schuko 共享的 mesh 足迹）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| rounded_rect_horizontal（基线） | rec_model-a-...-mo_..._c46f379f（parent）| `_rounded_rect` L106-107 / `_trim_ring_mesh` L110-128（圆角矩形 ring）/ `_plate_mesh` L131-178（横矩 plate + raised Schuko tile + 真空 well + pin holes）/ Schuko clips L241-247 | eligible if compatible | 横向圆角矩形（TRIM_W≈0.24×TRIM_H≈0.09），chrome 圆角矩形 ring（rect.fillet cut opening），**含 Schuko 插座 tile**（raised tile + circular well cut + 2 pin holes + 上下 ground_clip）|
| square_single | rec_variant-faceplate-shape-square-single-...-the_..._812d68e4 | `_trim_ring_mesh` L89-107（圆角方 ring）/ `_plate_mesh(positions)` L110-127（方 plate 0.082² + pocket cut，**无 Schuko/tile/well/clip**）/ WALL 0.18² L34-36 | eligible if compatible | 方形单联（PLATE_W≈PLATE_H≈0.082，TRIM 圆角方），chrome 圆角方 ring；**省略 Schuko 模块**；缩小 wall slab；part 树/joint 与 parent 同（rocker child + REVOLUTE）|
| round_plate | rec_variant-faceplate-shape-round-plate-...-h_..._491b75e5 | `_trim_ring_mesh` L83-103（圆环 annulus：outer circle cut inner circle）/ `_plate_mesh` L106-131（圆 disk PLATE_D≈0.156 + 方 pocket cut，**无 Schuko**）| eligible if compatible | 圆形面板（TRIM_OD≈0.17 圆环 chrome，PLATE_D≈0.156 ivory disk），方 rocker pocket；**省略 Schuko**；part 树/joint 与 parent 同 |

## 槽位图（slot graph）

pattern: mixed（固定 named slots: actuator_type + faceplate_shape 各自决定 `faceplate` 的 mesh/执行件（parallel children 挂 `faceplate`），外加 `gang_count` 在 `faceplate` 上 N 次复制执行件 + 其 joint）

```
wall_panel (root, warm-beige Box 墙板; 墙面 y=0)
  │
  └──[wall_to_faceplate: FIXED]── faceplate (child; 坐墙, 出墙 +Y)
        │   visual = plate_field (ivory _plate_mesh, 由 faceplate_shape 决定足迹+开口)
        │           + trim_ring (chrome _trim_ring_mesh, 由 faceplate_shape 决定形状)
        │           + [Schuko: ground_clip_upper/lower + tile/well inline 仅 rounded_rect_horizontal]
        │
        ├── [actuator_type slot]  (互斥四选一; 沿 X 等距复制 N 个)
        │     ├─ rocker        : rocker_{i}  ──[rocker_{i}_pivot:  REVOLUTE axis=+X, origin=(xc,ROCKER_PIVOT_Y,0)]
        │     ├─ toggle_lever  : toggle_{i}  ──[toggle_{i}_pivot:  REVOLUTE axis=+X, origin=(xc,PLATE_DEPTH,0)]
        │     ├─ push_button   : button_{i}  ──[button_{i}_press:  PRISMATIC axis=-Y, origin=(xc,PLATE_DEPTH,0)]
        │     └─ rotary_dimmer : dimmer_{i}  ──[dimmer_{i}_spin:   CONTINUOUS axis=+Y, origin=(xc,PLATE_DEPTH,0)]
        │
        └── [gang_count multiplicity 轴]  执行件_{i}  i∈range(N)
              placement: xc = (i-(N-1)/2)·MODULE_PITCH (绝对式, 中心对称)
              plate/trim/wall 宽随 N 放大: TRIM_W ≈ N·PITCH + 2·margin
```

接口点位与 joint 语义：
- **faceplate 接口（root→faceplate）**：`wall_to_faceplate` FIXED，origin=Origin()（identity）；faceplate 后面贴墙面 y=0（`expect_gap` max_gap=0.0005/penetration=0.0001），XZ 在 wall footprint 内（`expect_within`）。
- **actuator_type 接口（互斥，N 次复制）**：所有执行件挂 `faceplate`，origin x=xc（gang placement）、y=PLATE_DEPTH 或 ROCKER_PIVOT_Y（铰线/接触面）。
  - rocker：`rocker_{i}_pivot` REVOLUTE axis=(1,0,0) origin=(xc, ROCKER_PIVOT_Y≈0.0095, 0)（pocket 内 mid-depth 铰线）；`pivot_axle` steel Cylinder tips 嵌入 pocket 侧壁（captured-pin，`allow_overlap(pivot_axle↔plate_field)` + `expect_overlap` axes=x min=0.0005）。lower=0 非闭合（rest=0 中位）。
  - toggle_lever：`toggle_{i}_pivot` REVOLUTE axis=(1,0,0) origin=(xc, PLATE_DEPTH, 0)（面前铰线）；`pivot_axle` tips 嵌 escutcheon slot 壁（captured-pin allow_overlap）。
  - push_button：`button_{i}_press` PRISMATIC axis=(0,-1,0) origin=(xc, PLATE_DEPTH, 0)；button cap flange seat on pocket rim（element-scoped `allow_overlap(button_cap↔plate_field)` + `expect_contact`）。**无 pivot pin**。
  - rotary_dimmer：`dimmer_{i}_spin` CONTINUOUS axis=(0,1,0) origin=(xc, PLATE_DEPTH, 0)；`shaft_stub` steel Cylinder 穿 plate 圆 shaft hole（captured，`allow_overlap(shaft_stub↔plate_field)` + `expect_contact(knob_body↔plate_field)`）。
- **Schuko 接口（faceplate_shape 派生）**：仅 rounded_rect_horizontal 发射；raised tile + 真空 well + pin holes inline 进 `_plate_mesh`（plate_field visual），`ground_clip_upper`/`ground_clip_lower` steel `Box` inline 进 `faceplate` visual（坐 well 内，非移动件，Rule 1，无独立 joint）。square_single / round_plate 省略整块 Schuko。
- **mating policy**：rocker/toggle 是 pin-in-pocket-wall captured-pin、button 是 flange-on-rim captured-seat、dimmer 是 shaft-through-hole captured —— 几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：所有执行件 rest q=0（rocker/toggle 中位、button 未压、dimmer 0°）。注意 rocker/toggle 是对称 ±range（lower=-range），rest=0 即中位（非"闭合"）。
- **互斥 / 可选 / 派生**：actuator_type 四候选互斥（一次只一种执行件类型，N 个同类）；faceplate_shape 三候选互斥；Schuko 由 faceplate_shape 派生（仅 horizontal 有）；gang_count 与 actuator_type 自由组合。

## 每槽位 Module Emits / Interfaces

### Slot B / faceplate_shape — rounded_rect_horizontal（基线；含 Schuko）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wall_panel`（root, `wall_slab` Box）+ `faceplate`（`plate_field` ivory `_plate_mesh` + `trim_ring` chrome + `ground_clip_upper`/`ground_clip_lower` steel Box）| parent `wall_panel` L218-224 / `faceplate` L227-247 |
| internal joints | `wall_to_faceplate` FIXED origin=Origin() | parent L249-255 |
| upstream interface | wall root 坐墙 y=0（`expect_gap`/`expect_within`）| parent run_tests L320-334 |
| downstream interface | plate 前面 + pocket/slot/hole（供 actuator 接入）+ Schuko well inline | parent `_plate_mesh` L131-178 |

### Slot B / faceplate_shape — square_single / round_plate
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wall_panel` + `faceplate`（`plate_field` 方/圆 `_plate_mesh` + `trim_ring` 方/圆环；**无 Schuko/clip**）| square L158-196 / round L162-200 |
| internal joints | `wall_to_faceplate` FIXED | square L190-196 / round L194-200 |
| downstream interface | 方/圆 plate 前面 + pocket（供 actuator 接入）| square `_plate_mesh` L110-127 / round L106-131 |

### Slot A / actuator_type — rocker
| emits | 描述 | 来源 |
|---|---|---|
| parts | `rocker_{i}`（`rocker_paddle` ivory loft mesh + `pivot_axle` steel Cylinder）| parent `_rocker_mesh` L181-203 / `rocker_{i}` L260-274 |
| internal joints | `rocker_{i}_pivot` REVOLUTE axis=(1,0,0) origin=(xc,ROCKER_PIVOT_Y,0) lower=-0.10/upper=+0.10 | parent L275-288 |
| upstream interface | `pivot_axle` tips 嵌 pocket 侧壁（captured-pin allow_overlap）| parent run_tests L410-435 |

### Slot A / actuator_type — toggle_lever
| emits | 描述 | 来源 |
|---|---|---|
| parts | `toggle_{i}`（`toggle_lever` ivory 锥 loft + `pivot_axle` steel Cylinder）| toggle `_toggle_lever_mesh` L189-211 / `toggle_{i}` L268-282 |
| internal joints | `toggle_{i}_pivot` REVOLUTE axis=(1,0,0) origin=(xc,PLATE_DEPTH,0) lower=-0.35/upper=+0.35 | toggle L283-296 |
| upstream interface | `pivot_axle` tips 嵌 escutcheon slot 壁（captured-pin allow_overlap）| toggle run_tests L409-428 |

### Slot A / actuator_type — push_button
| emits | 描述 | 来源 |
|---|---|---|
| parts | `button_{i}`（`button_cap` ivory 阶梯 cap+guide mesh；**无 pivot pin**）| push `_button_mesh` L174-197 / `button_{i}` L255-261 |
| internal joints | `button_{i}_press` PRISMATIC axis=(0,-1,0) origin=(xc,PLATE_DEPTH,0) lower=0/upper=0.003 | push L262-275 |
| upstream interface | cap flange seat on pocket rim（element-scoped allow_overlap button_cap↔plate_field + expect_contact）| push run_tests L373-390 |

### Slot A / actuator_type — rotary_dimmer
| emits | 描述 | 来源 |
|---|---|---|
| parts | `dimmer_{i}`（`knob_body` KnobGeometry mesh + `shaft_stub` steel Cylinder）| dimmer `_dimmer_knob_mesh` L177-191 / `dimmer_{i}` L253-275 |
| internal joints | `dimmer_{i}_spin` CONTINUOUS axis=(0,1,0) origin=(xc,DIMMER_BASE_Y=PLATE_DEPTH,0)（无 limits）| dimmer L279-287 |
| upstream interface | `shaft_stub` 穿 plate 圆 shaft hole（captured，allow_overlap shaft_stub↔plate_field + expect_contact knob_body↔plate_field）| dimmer run_tests L404-421 |

### gang_count multiplicity（执行件复制；moving parts，各带独立 joint）
| emits | 描述 | 来源 |
|---|---|---|
| parts | N 个 `<actuator>_{i}`（actuator_type 决定形态），`for i in range(N)` | parent L259-288 / N=1 `_make_rocker` L164-195 / N=4 L204-218 |
| joints | N 个独立 `<actuator>_{i}_<verb>`（REVOLUTE/PRISMATIC/CONTINUOUS 随 actuator_type）| 同上 |
| placement | `xc = (i-(N-1)/2)·MODULE_PITCH`（绝对式中心对称；N=1→0 居中）；TRIM_W/PLATE_W/WALL_W 随 N 放大 | N=4 `ROCKER_X` L59, TRIM_W L42 / N=1 `ROCKER_X` L57 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| actuator_type | enum | rocker / toggle_lever / push_button / rotary_dimmer | rocker | choice | 由 deterministic procedural sampler 选；主机构（互斥），决定执行件 mesh+开口+joint 拓扑 | module table |
| faceplate_shape | enum | rounded_rect_horizontal / square_single / round_plate | rounded_rect_horizontal | choice | sampler 选；决定 plate/trim mesh + Schuko 有无（footprint 维度，不改 joint 拓扑）| module table |
| gang_count (N) | int | 声明域 [1,6]；sweep 采样域 [1,6]（偏小加权：1/2 高频、3 常见、4-6 长尾）| 2 | independent→slot_choice | 编入 slot_choice 为 `("gang_count", f"n{N}")`（拓扑维度）；**与 faceplate_shape 完全正交**——容量差异由 host 尺寸派生吸收，不 gate（见下 inequality + §8）| N=1/N=4 变体 + 绝对式 placement 的 N-不变性 |
| palette_style | enum | 14 个 colorway：ivory_chrome / soft_white / brushed_steel / matte_black / anthracite / graphite_gloss / antique_gold / copper_patina / navy_enamel / signal_red / walnut_trim / sage_kitchen / terracotta_loft / powder_blue | ivory_chrome | palette | palette only，**不计入 core/raw domain**（VISUAL_DIVERSITY_MODEL §core/raw）；改 wall/plate/trim/actuator/steel 五个 role 的 rgba **+ trim 的 finish**（metallic ring vs painted ring）。三条硬约束：(a) 分 role albedo 上限 wall 0.52 / plate·trim·actuator 0.68 / steel 0.60，保色相等比缩放——共用 preview 灯组总辐照 ~1.65x 且 view_transform=Standard 无 tonemap，>0.6 albedo 的正对面会削顶成纯白；(b) 材质名 `switch_<role>_<finish>_<palette>` 的 finish token 驱动 PBR 解析器，palette slug 内**不得**含 metal/brass/glass/clear/bakelite 等 token，否则 finish 会泄漏到所有 part（旧 `warm_brass` slug 曾让墙板变抛光金属）；(c) **执行件颜色是派生的、不是授权的**：`_actuator_rgba` 保证 actuator 与 plate 的 Rec.709 亮度差 ≥ `_ACTUATOR_CONTRAST`(0.14)——浅面板上压暗、深面板上提亮（各自有色域余量的方向）。授权值若本身已够对比则原样保留（如深蓝面板配白拨杆）。理由：执行件是**活动件**，必须作为独立 body 可辨识，无论在渲染里还是在 part segmentation 里；改前 14 组里有 6 组 actuator 与 plate **完全同色**，其余也只差 0.03–0.05，唯一的分界是 pocket 阴影。作者测试 `actuator colour separates from the plate` 守这条不变式| 各样本材质 + 真实墙板配色 + 实测 clip 点 |
| plate_width_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 TRIM_W/PLATE_W X 主尺寸（保 footprint 比例），clamp | resolve clamp |
| plate_height_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 TRIM_H/PLATE_H Z 主尺寸，clamp（round_plate 时与 width 锁定保圆）| resolve clamp |
| module_pitch_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放执行件并排间距 MODULE_PITCH，clamp | N=4 ROCKER_X |
| actuator_travel_scale | float | [0.85, 1.12] | 1.0 | independent | 缩放 REVOLUTE upper（rocker/toggle）/ PRISMATIC upper（button）；dimmer 无（CONTINUOUS），clamp（保 REVOLUTE ≤π·0.5、PRISMATIC ≤ pocket 深 −margin）| resolve clamp |
| (—) | constraint | — | — | equation | round_plate 时 `plate_height_scale = plate_width_scale`（保圆形）；TRIM_OD/PLATE_D 同步缩 | round_plate `_trim_ring_mesh` L83-103 |
| (—) | constraint | — | — | inequality | 执行件网格不超 plate，**X 与 Z 两条**：`max|xc| + ACTUATOR_W/2 + margin ≤ plate_w/2`、`max|zc| + ACTUATOR_W/2 + margin ≤ plate_h/2`；违反时按轴放大 plate（round_plate 按角点半径径向放大以保圆）| N=4 TRIM_W L42 + 接口 clearance + 二维网格 |
| (—) | constraint | — | — | equation | 墙板尺寸双轴 frame 面板：`WALL_W = max(0.18, TRIM_W+0.10)`、`WALL_H = max(0.24, TRIM_H+0.10)`（大 N 圆盘直径可达 ~0.46 m，标称 0.24 m 墙高会被面板穿出）| N=4 WALL_W 放大 |
| (—) | constraint | — | — | inequality | actuator 不撞墙：press/翻转 pose 下 actuator back y > pocket_floor + margin 且不穿墙 y<0（照搬各样本 pressed/tipped clearance check）| 各样本 run_tests pressed/tipped 段 |
| (—) | constraint | — | — | conditional | faceplate_shape=square_single / round_plate 时省略 Schuko 模块（tile/well/clip 不发射）；rounded_rect_horizontal 才发射 | square/round `_plate_mesh` |
| (—) | constraint | — | — | equation | round_plate 的**盘径随 N 派生**：`PLATE_D = max(0.156·width_scale, (N-1)·pitch + ACTUATOR_FOOTPRINT + 2·ROUND_RIM_MARGIN)`，TRIM_OD = PLATE_D + 0.014。N≤2 保持标称 0.156 盘；N≥3 就是一块更大的圆盘。**不再 gate N**（VISUAL_DIVERSITY_MODEL「完整组合原则」）| round PLATE_D≈0.156 作为标称下限 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 间距，**绝不改变 actuator_type / faceplate_shape / N 的拓扑**。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（并排执行件数 = 开关位数）：

- **count_param**：`gang_count`（模板内变量 N / GANG_COUNT；面板沿 X 并排的执行件数）。
- **N_range**：声明产品域 **[1, 6]**（source map 建议的上界，首版曾保守收到 [1,4] 因为只有 N=1/2/4 有样本；N=3/5/6 由 `for i in range(N)` + 绝对式 placement 公式安全构造，已由 random-36 + corner 实测覆盖，据此放宽到 [1,6]）。`config_from_seed` 的 sweep 采样域 **[1,6]**（偏小加权：N=1/2 高频、N=3 常见、N=4-6 长尾）。N=1 即各 single 变体的退化情形（居中单执行件）。
- **sampling domain**：`config_from_seed` 用 `rng.choices(GANG_COUNTS, weights=偏小)`；`resolve_config` 把任意外部 config 的 N clamp 到 [1,6]。
- **copied object**：单只执行件单元——`<actuator>_{i}` part（actuator mesh + pivot_axle/shaft_stub）+ 其 `<actuator>_{i}_<verb>` joint，共享 actuator mesh helper（一个 mesh 对象复用 N 次）。
- **naming**：`rocker_{i}` / `toggle_{i}` / `button_{i}` / `dimmer_{i}`（随 actuator_type），joint `rocker_{i}_pivot` / `toggle_{i}_pivot` / `button_{i}_press` / `dimmer_{i}_spin`，`for i in range(N)`（parent L259 / N=1 `_make_rocker` L164 / N=4 L204 已用此结构，可直接作 copy-logic 源）。
- **placement**：**二维绝对式网格**（`_gang_grid` + `_grid_positions`）。rounded_rect_horizontal 恒为单行（`1 x N`）——横排一条模块带就是该 footprint 的身份，Schuko 也挂在这条带的末端；square_single / round_plate 用最接近正方的网格 `cols = ceil(sqrt(N))`、`rows = ceil(N/cols)`，即 N=1→1x1、2→1x2、3/4→2x2、5/6→2x3，末行不满时按本行个数居中。两轴均为绝对式（`xc = (col-(in_row-1)/2)·pitch`、`zc = ((rows-1)/2-row)·pitch`，由 N 与中心解析、不累加漂移），保持 N-不变。**plate/trim/wall 两轴都随网格放大**；round_plate 按网格**角点半径**定盘径。
  - 这条派生修掉两个真实缺陷：单行让 square_single 在 N=6 时退化成 0.42x0.084 的信箱形（根本不方），并逼 round_plate 把盘径撑到 0.41 m 去容纳 5 连排（大圆盘上五个小执行件）。改网格后 N=6 方板 aspect 5.00→1.40，N=5 圆盘 0.414→0.272 m。**这是 placement 派生的改进，不是新语义槽位**：不新增候选、不进 slot_choice、core/raw domain 不变。
- **joint policy**：执行件是**移动件**（与 cushion 粉盘不同！）→ **每个执行件发射独立 joint**（REVOLUTE/PRISMATIC/CONTINUOUS 随 actuator_type），各自独立活动，不共享 joint。
- **source/gating**：copy-logic 源取 parent L259-288（N=2 enumerate）与 N=4 L204-218（`for i in range(N)`）的循环；**N=1 取 single 变体的居中单执行件**（`_make_rocker` helper，等价 range(1)）。N 与 round_plate **完全正交**：圆盘按 §7 equation 随 N 派生盘径来吸收容量差异，不排除任何组合。

## 拓扑多样性审计

总组合数：actuator_type(4) × faceplate_shape(3) × gang_count 采样数(6，即 {1..6}) = **72**，
**完整笛卡尔积、无 gate 扣除**（30000-seed 枚举实测可达 72/72）。core_domain（非 N）= 4×3 = 12。

仅 actuator_type(4) = **4 种 joint 拓扑类**（REVOLUTE 跷跷板 / REVOLUTE 拨杆 / PRISMATIC 按钮 / CONTINUOUS 旋钮）；× gang_count(6) = 24 已远超门控；叠 faceplate_shape(3) → 72 充裕。

理由：actuator_type 提供 4 种真正的 joint type 差异（REVOLUTE/PRISMATIC/CONTINUOUS），× N（1-4 个执行件，part 数 + joint 数变化）即 16 个 joint-topology 类，叠 faceplate_shape(3) footprint 后总 48 distinct。**N 必须编入 `slot_choices_for_seed`**（`("gang_count", f"n{N}")`，对齐 cushion/shopping_bucket/fence_cascade），否则单联与多联在 slot_choice 上无法区分，损失一整根拓扑维度。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 两个 named slot（actuator_type / faceplate_shape），经兼容矩阵合法化，再 `rng.choices` 加权 N∈[1,6]（与 faceplate_shape 无关，无上限收缩），再 uniform 各连续 scale。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：见 §参数表的 plate_width_scale / plate_height_scale（round_plate 时 equation 锁定 = width，且 width_scale 只缩标称盘、不缩 N 派生容量下限）/ module_pitch_scale / actuator_travel_scale。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（actuator_type / faceplate_shape）+ N（解析 conditional：Schuko 仅 horizontal、actuator_travel 上限随 actuator_type；round 盘径随 N 派生而非收缩 N）→ 采 independent plate_width/height/pitch/travel scale → 派生（round_plate 时 height=width；plate width 随 N 放大）→ 用执行件排布不超 plate + actuator 不撞墙两条 inequality 投影 / 回缩。跨部件依赖（执行件排布 vs plate 宽、actuator 行程 vs pocket 深）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 pivot/press/spin origin、captured-pin/seat/shaft 接口、N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` actuator_type + faceplate_shape（无需合法化：全组合），再 `rng.choices` 加权 N∈[1,6]（无 shape 相关 clamp），再 uniform 各 scale | slot_choices_for_seed 含 `("gang_count", f"n{N}")` 且与 build 一致 |
| cross-slot derivation（**无 compatibility gate**）| (1) **round_plate × N**：圆盘 PLATE_D 随 N 派生（见 §7 equation），N>2 就是更大的盘 —— 不改 faceplate_shape、不 clamp N。 (2) **Schuko × faceplate_shape**：Schuko 模块仅 rounded_rect_horizontal 发射（square_single/round_plate 省略）；Schuko 占一个 module 宽度的右端静态位，但**不**占 gang slot（执行件仍 N 个，Schuko 额外）→ horizontal 面板总横向 = N·PITCH(执行件) + Schuko tile，plate 宽据此放大。 (3) **actuator_type × N 正交**：4 种 actuator 均可 N 个并排（N 个同类型），自由组合。 (4) **actuator_travel × actuator_type**：dimmer 无 travel（CONTINUOUS 无 limits），rocker/toggle 的 REVOLUTE upper / button 的 PRISMATIC upper 各按 conditional clamp。 (5) faceplate_shape 与 actuator 正交（任意 actuator 配任意 footprint）。 | 无 floating / collision / 圆盘容不下多执行件（由派生盘径保证，作者测试 `round_plate disc contains the N=... actuator row` 守）/ actuator 撞墙 / Schuko 错配方圆面板 / 行程超 pocket 深 |
| controlled local variation | 4 个 clamped scale（plate_width/height、module_pitch、actuator_travel），每 build 统一；plate_height 在 round_plate 时 equation=width，actuator_travel 为 conditional@actuator_type | 比例变化不破坏 pivot/press/spin origin、captured 接口、actuator 不撞墙、坐墙、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 QC（REVOLUTE/PRISMATIC/CONTINUOUS 各验）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| actuator_type | 4 | yes | yes | REVOLUTE 跷跷板 / REVOLUTE 拨杆 / PRISMATIC 按钮 / CONTINUOUS 旋钮（互斥主机构，4 joint type）|
| faceplate_shape | 3 | yes | yes | 横矩(含 Schuko) / 方(无 Schuko) / 圆(无 Schuko)（footprint 维度）|
| gang_count (N) | 6（采样域 {1..6}，1/2 高频 / 4-6 长尾）| yes | yes | 拓扑维度，编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("gang_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，N 采样域 ⊆ [1,6]
- `resolve_config` 把 gang_count clamp 到 [1,6]（**无 shape 相关的二次 clamp**；round_plate 改为按 N 派生盘径），各 scale clamp 到声明范围；actuator_travel / plate_height 为 conditional / equation 随 actuator_type / faceplate_shape 解析；两条 clearance inequality（执行件排布不超 plate、actuator 不撞墙）在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（round_plate×N>2 降级；Schuko 仅 horizontal；actuator_travel 按 actuator_type）
- 连续 scale clamp 后不破坏 pivot/press/spin origin / captured-pin/seat/shaft 接口 / actuator 不撞墙 / 坐墙 / N 复制
- 关键 joint：rocker `rocker_{i}_pivot` REVOLUTE axis≈(1,0,0)（abs(axis[0])>0.99）lower≈-0.10/upper≈+0.10；toggle `toggle_{i}_pivot` REVOLUTE axis≈(1,0,0) ±0.35；button `button_{i}_press` PRISMATIC axis≈(0,-1,0) 0..0.003；dimmer `dimmer_{i}_spin` CONTINUOUS axis≈(0,1,0)（无 limits）
- captured-pin / seat / shaft：element-scoped `allow_overlap`（rocker/toggle `pivot_axle`↔`plate_field`；button `button_cap`↔`plate_field`；dimmer `shaft_stub`↔`plate_field`），照搬各样本 run_tests 的 allow_overlap 段
- copied object 遵循 `<actuator>_{i}` 命名 + 绝对式沿 X 等距 placement `(i-(N-1)/2)·PITCH` + 每执行件独立 joint
- faceplate seated flush on wall（`expect_gap` max_gap 0.0005/penetration 0.0001）+ faceplate within wall footprint
- grandfather：所有 pivot/seat/shaft captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把 N 当普通 int 参数、不进 slot_choice → 单联与多联 slot_choice 同形，损失拓扑维度（违反 §8/§9 硬要求）。
- 把执行件当**非移动 visual**（像 cushion 粉盘那样 inline 无 joint）→ 出类！本类执行件是**移动件**，每个必须发独立 joint（rocker/toggle REVOLUTE / button PRISMATIC / dimmer CONTINUOUS）。
- ~~round_plate 配 N>2~~ **不再是 reject case**：圆盘按 §7 equation 随 N 派生盘径，N>2 只是更大的盘。真正的 reject 仍是「派生后 pocket 仍超出 PLATE_D」，由作者测试 `round_plate disc contains the N=... actuator row` 守。
- 方/圆面板仍发射 Schuko 插座 → 与样本不符（square_single/round_plate 无 Schuko）；Schuko 仅 rounded_rect_horizontal。
- gang placement 用累加式（`x += pitch`）而非绝对式 `(i-(N-1)/2)·pitch` → N 变化时漂移、不居中。
- plate 宽不随 N 放大（固定 TRIM_W）→ N=4 时执行件挤出 plate 边缘（违反排布不超 plate 不等式）；TRIM_W 须随 N。
- pivot/press/spin origin 放在 plate 中心或任意点而非真实铰线/接触面（ROCKER_PIVOT_Y / PLATE_DEPTH）→ `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- 给 captured-pin/seat/shaft 补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- actuator_travel 过大致 button 压穿墙 / rocker 翻进 pocket 底 → §7 actuator 不撞墙不等式 FAIL；须按比例缩或拒绝。
- dimmer 加 motion_limits（CONTINUOUS 应无 limits）或 axis 设成 ±X/±Z 而非 +Y front-normal → 与样本不符。
- 把连续尺寸 / 颜色 / 材质（palette_style / plate scale）当新 candidate 塞进 slot → 不是结构差异。
- 把"闸刀开关 / 工控面板 / 路由器面板"语义混入 → 出类，本类是住宅墙面 N 联开关/插座薄面板。

## 与相邻类别的边界

- 不该混入：**闸刀开关 / knife switch / 工业断路器**——本类是住宅墙面薄面板 + 小并排执行件，非大杠杆闸刀（主运动 spine 不同）。
- 不该混入：**船舶/航空/机柜混排控制面板**（按钮+屏+拨码混排）——本类是单一执行件词汇 + 可选单 Schuko 插座，非多功能仪表盘。
- 不该混入：**路由器 / 配电箱 / 接线盒**——无并排住宅开关位语义。
- 不该混入：**门铃 / 恒温器 / 单按钮设备**——单功能、非"N 个并排开关位 + 面板 + chrome trim"形态；如需单独 slug。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) faceplate_shape 建模为 mesh-footprint 维度（非串联 slot）；(2) ~~N_range 取 [1,4] 还是 [1,6]~~ → **已定：[1,6]**，random-36 + corner 实测通过；(3) ~~round_plate×N>2 的兼容降级策略~~ → **已定：不降级**，改为盘径随 N 派生（Schuko 仍仅 horizontal，属 footprint 身份特征而非容量 gate）；(4) Topology target 72<300 的说明是否接受（本小类真实结构上限，与 cushion 同型）；(5) 执行件是 moving part 各带独立 joint（与 cushion 粉盘 Rule 1 inline 相反）是否符合 multiplicity 审计期望；(6) Schuko 占额外宽度而非占 gang slot 的建模是否接受）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）
- 共享 helper：`_rounded_rect`（通用 sketch）、`_trim_ring_mesh` / `_plate_mesh`（footprint mesh，按 faceplate_shape 切换：矩形 ring / 方 ring / 圆环 + Schuko 有无）、`_rocker_mesh` / `_toggle_lever_mesh` / `_button_mesh` / `_dimmer_knob_mesh`（actuator mesh，按 actuator_type 切换；N 复制复用同一 mesh 对象）、`_make_rocker` 风格的 per-actuator 发射 helper（N=1 变体 L164-195 已示范）。
- captured 接口 allow_overlap：`run_switch_tests` 里逐 actuator 补 element-scoped `allow_overlap`（rocker/toggle pivot_axle↔plate_field；button button_cap↔plate_field；dimmer shaft_stub↔plate_field），照搬各样本 run_tests 段（parent L410-435、toggle L409-428、push L373-390、dimmer L404-421）。
- conditional 范围解析顺序：先采 actuator_type / faceplate_shape / N → 解析 Schuko 仅 horizontal、actuator_travel 上限随 actuator_type、plate_height equation（round_plate）→ 采 plate_width/pitch/travel independent scale → 派生 plate 宽随 N 放大 → 投影两条 clearance inequality（排布不超 plate、actuator 不撞墙）。
- N=1 退化：用 single 变体的 `_make_rocker` 居中单执行件（不进多元 enumerate，等价 range(1)，xc=(0-(1-1)/2)·PITCH=0）；N≥2 走 `for i in range(N)`。
- dimmer 用 `KnobGeometry`（含 KnobGrip/KnobIndicator）；注意 axis=(0,1,0) front-normal CONTINUOUS **无 motion_limits**（仅 effort/velocity）。dimmer 的 KnobGeometry 轴对称，**spin AABB 检查**可能脆（参见 articraft-knob-spin-test memory：轴对称 KnobGeometry 易过不了 AABB spin 检查）→ 若 CONTINUOUS 旋转 AABB-change 检查脆，照搬 dimmer 样本 run_tests L463-478 的（指示器 pointer 偏心 + π/4 AABB 变化）写法，或验 indicator dot 位移而非整体 AABB。
- 参考模板：`agent/templates/Accessories_Cushion.py`（同为 mixed pattern：固定 named slots + `("count", f"n{N}")` 进 slot_choice + 绝对式 placement + 共享 mesh 复用 + 兼容矩阵 gating + captured-pin allow_overlap + footprint-as-mesh-dimension 骨架，本类几乎同构改编——主要差异：switch 执行件是 moving part 各带独立 joint，cushion 粉盘是 Rule 1 inline visual）；`agent/templates/Bag_Suitcase_Shopping_bucket.py`（绝对式 N 复制 + 兼容矩阵）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B（parent 基线）| rocker + rounded_rect_horizontal + Schuko + N=2 | rec_model-a-...-mo_..._c46f379f | `wall_panel`/`faceplate`/FIXED L218-255 / `_rocker_mesh` L181-203 / `rocker_{i}`+`rocker_{i}_pivot` REVOLUTE L259-288 / `_plate_mesh`(矩+Schuko) L131-178 / `_trim_ring_mesh`(矩 ring) L110-128 / Schuko clips L241-247 / allow_overlap L410-435 | 共享骨架 + rocker 基线 + 横矩 footprint + Schuko + captured-pin 范式 + N=2 placement |
| S2 | A | toggle_lever | rec_variant-actuator-type-toggle-lever-...-t_..._5e9273bf | `_toggle_lever_mesh` L189-211 / escutcheon+slot `_plate_mesh` L139-167 / `toggle_{i}`+`toggle_{i}_pivot` REVOLUTE ±0.35 L267-296 / allow_overlap L409-428 | 拨杆执行件（REVOLUTE 大行程翻转，面前 pivot）|
| S3 | A | push_button | rec_variant-actuator-type-push-button-...-tw_..._531fc067 | `_button_mesh` L174-197 / `button_{i}`+`button_{i}_press` PRISMATIC L255-275 / cap-on-rim allow_overlap L373-390 | 按钮执行件（PRISMATIC 压入，flange-on-rim 无 pivot pin）|
| S4 | A | rotary_dimmer | rec_variant-actuator-type-rotary-dimmer-...-_..._f19a560b | `_dimmer_knob_mesh`(KnobGeometry) L177-191 / `dimmer_{i}`+`knob_body`/`shaft_stub` L251-275 / `dimmer_{i}_spin` CONTINUOUS +Y L279-287 / allow_overlap L404-421 | 旋钮执行件（CONTINUOUS 自由旋，shaft-through-hole captured）|
| S5 | B | square_single | rec_variant-faceplate-shape-square-single-...-the_..._812d68e4 | `_trim_ring_mesh`(方 ring) L89-107 / `_plate_mesh`(方 plate,无 Schuko) L110-127 / WALL 0.18² L34-36 / `NUM_ROCKERS`/`ROCKER_POSITIONS` L55-56 | 方形单联 footprint（无 Schuko，缩小 wall，居中单执行件）|
| S6 | B | round_plate | rec_variant-faceplate-shape-round-plate-...-h_..._491b75e5 | `_trim_ring_mesh`(圆环 annulus) L83-103 / `_plate_mesh`(圆 disk,无 Schuko) L106-131 / `ROCKER_X` 居中对称 L50 | 圆形面板 footprint（圆环 lathe chrome，无 Schuko，圆盘容量有限）|
| S7 | multiplicity | gang_count N=1 | rec_variant-gang-count-1-...-switc_..._e21d2998 | `N_GANGS`/`ROCKER_X = tuple(i*PITCH-(N-1)*PITCH/2 ...)` L55-57 / `_make_rocker` helper L164-195 | N=1 退化 + per-actuator 发射 helper + 绝对式 placement 公式源 |
| S8 | multiplicity | gang_count N=4 | rec_variant-gang-count-4-...-switch-_..._e3244d88 | `GANG_COUNT`/`ROCKER_X = tuple((i-(N-1)/2)*PITCH ...)` L39,L59 / TRIM_W/PLATE_W/WALL_W 随 N 放大 L34,L42,L52 / `for i in range(N)` build L204-218 | N=4 copy-logic 源 + plate/trim/wall 宽随 N 放大公式 |
