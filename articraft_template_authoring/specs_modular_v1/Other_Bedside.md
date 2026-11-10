# bedside (bedside nightstand / cabinet) — Modular Spec

> 来源小类：`picture/Other/Bedside`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Other__Bedside.md`。
> **"Bedside" 在此 = 床头柜 / 床头收纳柜（bedside nightstand）**：一只落地中空 `carcass` 壳体（带 gallery lip 顶台 + 侧/后板 + 凹腔），下接一种**底座支撑**（悬浮 plinth / 外撇腿 / 踢脚箱 / 发夹钢腿），腔内含一种**储物开合机构**（N 个 PRISMATIC 抽屉 / 侧铰柜门 / 下翻门 / 上格+抽屉），抽屉/门面带一种**把手**（铬条 / 抠手 / 圆旋钮）。
>
> **同步状态**：本 spec 引用的 11 个 5 星样本（1 个 parent + 10 个 fork 槽位变体）已同步进本仓库 `data/records/`，rating=5。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一核对）。引用以 part / joint / helper **名字** 为准（`carcass` / `_build_drawer` / `_build_door` / `flap_door` / `carcass_to_{tag}_drawer` / `carcass_to_door` / `carcass_to_flap_door` / `hairpin_leg_{i}` / `base_toekick` / `_finger_pull_slab` / `_make_drawer_knob_mesh` / `drawer_{i}` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `bedside` |
| template path | `agent/templates/Other_Bedside.py` |
| test path (optional) | `tests/agent/test_bedside_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（固定 named slots: base_support + storage_mechanism + handle 各挂共同 `carcass`（parallel children），**外加** `drawer_count` 抽屉多重性轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11（1 parent + 10 fork 槽位变体；均 converged，compile success、≥1 非 fixed joint、workbench-only）|
| read_count | 11（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests）|
| read_scope | source map 列出的 11 个被采纳 5 星样本（parent + base×3 + storage×3 + handle×2 + drawer_count×2）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 11/11 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **parent**（`...c9162b4f`）= 基线拓扑：`carcass`（root，中空灰壳 + inset plinth + gallery lip 顶台 + bottom panel + runner rails）+ 2 只 `top_drawer`/`bottom_drawer`（child），各一 `carcass_to_{tag}_drawer` **PRISMATIC**（axis=(1,0,0)，origin=(D,0,cz)，lower=0/upper=0.36）。抽屉 = hollow open-top tray + front_slab + 铬条把手（`_build_drawer` helper）。
- **base_support 轴**（Slot A）：底座层只换 `carcass` 顶部以下的支撑几何（plinth → 腿 / 踢脚箱 / 发夹腿），**carcass 主壳、抽屉树、joint 拓扑全不变**——base_support 是 carcass-local visual 维度（腿 / 箱 inline 到 carcass），不发射独立 joint。four_splayed_legs（`_make_leg_mesh` LatheGeometry + splay 旋转，`leg_{i}`）/ solid_toe_kick_box（`base_upper`+`base_toekick` 两块，落地踢脚）/ hairpin_metal_legs（`_build_hairpin_leg_mesh` tube_from_spline_points，`hairpin_leg_{i}` + 安装板）相对 plinth 是 footprint/lift 维度而非拓扑维度，但显著改类别外观 → 作 candidate 轴。腿抬高时 `BODY_BOT_Z=LEG_H`、`H` 重算（见 §7 height 派生）。
- **storage_mechanism 轴**（Slot B）= **主机构槽**，真正改 joint 拓扑：two_prismatic_drawers（N×PRISMATIC +X，基线）/ hinged_cabinet_door（单 `door` child，`carcass_to_door` **REVOLUTE axis=+Z**，侧铰外开）/ drop_down_flap_door（单 `flap_door` child，`carcass_to_flap_door` **REVOLUTE axis=+Y**，底铰下翻）/ open_niche_over_drawer（上部固定开放格 `divider_shelf` + 下 1 只 `carcass_to_drawer` **PRISMATIC**）。这是 PRISMATIC vs REVOLUTE(+Z) vs REVOLUTE(+Y) vs 固定格+单PRISMATIC 的 joint-topology 差异。
- **handle 轴**（Slot C）：chrome_bar_on_posts（`handle_post_{i}`+`handle_bar`，Box 铬条，基线）/ recessed_finger_pull（`_finger_pull_slab` CadQuery 抠手槽 + `finger_pull_groove` accent，**无凸出件**）/ round_knobs（`_make_drawer_knob_mesh` lathe 旋钮，每面 2 个 `knob_{i}`，循环）。把手 = 储物面上的**非移动 visual**（inline 到 drawer/door part，无独立 joint，Rule 1）。
- **drawer_count 轴**（Slot D 多重性）：N=1（`DRAWER_COUNT=1`，单高抽屉，`drawer_{i}` for i in range(1)）/ N=2（parent，top/bottom）/ N=3（`N_DRAWERS=3`，`for i in range(N_DRAWERS)` `drawer_{i}` + `carcass_to_drawer_{i}` + 均匀 `CZ[i]` 栈）→ 同构抽屉 N 次复制，每只**独立 PRISMATIC** 关节（joint-bearing multiplicity，区别于 cushion 的非移动粉盘）。仅在 storage=two_prismatic_drawers 下生效（见 §8/§9）。

## 核心身份

一只落地**床头柜 / 床头收纳柜**（bedside nightstand）：一只中空 `carcass`（root，矩形灰漆壳体，两厚侧板 + 后板高出 recessed 顶台 ~0.06 m 形成三面 gallery lip，前缘开口；内有 runner rails / bottom panel），整体 ~0.65(W)×0.45(D)×0.45(H) m。`carcass` 下接一种**底座支撑**（悬浮 inset plinth / 四外撇锥腿 / 落地踢脚箱 / 四发夹钢腿），腔内含一种**储物开合机构**（N 个前滑 PRISMATIC 抽屉 / 侧铰 REVOLUTE 柜门 / 底铰 REVOLUTE 下翻门 / 上固定开放格 + 下单抽屉），抽屉/门面带一种**把手**（两柱铬条 / 嵌入抠手槽 / 双圆旋钮）。活动语义 = **储物开合**（抽屉前滑 +X / 柜门绕 +Z 外开 / 翻门绕 +Y 下翻）。默认成熟域：base_support × storage_mechanism × handle × 抽屉数 N∈[1,4] 的小型床头柜，前面 +X、宽 Y、高 +Z，坐地。

不该混入：
- **大件衣柜 / 多抽屉斗柜（dresser / chest of drawers）**——本类是床头**小柜**（单宽 ~0.65 m、抽屉数小 N≤4），不是高宽多列大柜；如需可作 `drawer_cabinet_with_sliding_drawers` slug（已有）。
- **书桌 / 带桌面单抽屉桌（desk_with_drawer）**——本类无大桌面工作台，主体是收纳壳。
- **保险柜 / 带拨盘箱门（wall_safe）**——金属箱体 + 拨盘，非木 / 漆床头柜壳。
- **置物架 / 开放搁架（shelf）**——纯开放无开合机构；本类必含 ≥1 储物开合活动件。

## 槽位 + 候选模块表

> **建模注记**：`base_support`（Slot A）是 `carcass` 顶部以下的**支撑层 carcass-local visual**（plinth / 腿 / 踢脚箱），由 base helper 一次决定，**不发射独立 joint、不改抽屉/门 part 树**；腿类抬高 `BODY_BOT_Z`/`H`（见 §7）。`handle`（Slot C）是储物面上的**非移动 visual**（Rule 1，inline 到 drawer/door，无独立 joint）。**`storage_mechanism`（Slot B）是唯一改 joint 拓扑的主轴**；`drawer_count`（Slot D）是 joint-bearing 多重性轴（每抽屉一对 PRISMATIC），仅在 storage=two_prismatic_drawers 下展开。

### Slot A：base_support（底座支撑——carcass-local，决定 lift/footprint，不贡献 joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| inset_floating_plinth（基线） | parent (`...c9162b4f`) | `plinth` visual L152-157（在 `build_object_model` L137 起）| eligible if compatible | 四面内收悬浮 plinth（`Box(D-2·INSET, W-2·INSET, PLINTH_H)`），`BODY_BOT_Z=PLINTH_H=0.045`，H=0.45 |
| four_splayed_legs | rec_variant-base-support-four-splayed-legs-...65751baf | `_make_leg_mesh` L78-108 / 四角 `leg_{i}` 装配 L201-210 | eligible if compatible | 四锥形外撇腿（`LatheGeometry` profile + splay 旋转 8°），`LEG_H=0.12`，`BODY_BOT_Z=LEG_H`，H≈0.525；木腿 walnut |
| solid_toe_kick_box | rec_variant-base-support-solid-toe-kick-box-...6dddcda5 | `base_upper` L160-165 + `base_toekick` L170-175 | eligible if compatible | 落地踢脚箱（`base_upper` 全宽全深 + `base_toekick` 前缩 recess 形成踢脚凹），`BASE_H=0.055`，坐地 H=0.45 |
| hairpin_metal_legs | rec_variant-base-support-hairpin-metal-legs-...dcdcb159 | `_build_hairpin_leg_mesh` L74-99 / 四角 `hairpin_leg_{i}` + 安装板 L191-210 | eligible if compatible | 四 U 形弯钢发夹腿（`tube_from_spline_points` rod，`ROD_R=0.005`，XZ 平面 U 弯）+ 钢安装板，`LEG_H=0.12`，H≈0.525 |

### Slot B：storage_mechanism（**主机构槽**——决定储物 part 树与 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| two_prismatic_drawers（基线） | parent (`...c9162b4f`) | `_build_drawer` L62-134 + `carcass_to_{tag}_drawer` PRISMATIC L217-226 | eligible if compatible | N 只 `drawer`（hollow open-top tray + front_slab）child，每只 `carcass_to_*_drawer` **PRISMATIC** axis=(1,0,0)，origin=(D,0,cz)，lower=0/upper=0.36；与 drawer_count 多重性联动（见 §8）|
| hinged_cabinet_door | rec_variant-storage-mechanism-hinged-cabinet-door-...02643395 | `_build_door` L60-100 + `carcass_to_door` REVOLUTE L184-195 | eligible if compatible | 单 `door` child（`door_panel` + 把手），`carcass_to_door` **REVOLUTE** axis=(0,0,1) origin=(D,HINGE_Y,DOOR_CZ)，侧铰外开 lower=0/upper=DOOR_OPEN_ANGLE；drawer_count 强制 N=0/1（无抽屉栈）|
| drop_down_flap_door | rec_variant-storage-mechanism-drop-down-flap-door-...2bf8cef6 | `flap_door` part L157-167 + `carcass_to_flap_door` REVOLUTE L180-189 | eligible if compatible | 单 `flap_door` child（`door_slab` + 铬条把手），`carcass_to_flap_door` **REVOLUTE** axis=(0,1,0) origin=(HINGE_X,0,HINGE_Z)，底铰下翻 lower=0/upper≈1.50 |
| open_niche_over_drawer | rec_variant-storage-mechanism-open-niche-over-drawer-...bd3941ca | `divider_shelf` 固定格 L193-199 + 单 `drawer` + `carcass_to_drawer` PRISMATIC L231-240 | eligible if compatible | 上部**固定开放格**（`divider_shelf` 隔板，无 joint）+ 下 1 只 `drawer` child，单 `carcass_to_drawer` **PRISMATIC** +X；drawer_count 固定 N=1 |

### Slot C：handle（把手——储物面非移动 visual，Rule 1，无独立 joint）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| chrome_bar_on_posts（基线） | parent (`...c9162b4f`) | `handle_post_{tag}` + `handle_bar` L119-131（`_build_drawer` 内）| eligible if compatible | 两柱 + 铬条把手（3 个 Box），凸出 front_slab ~0.019 m；door 变体复用同型（hinged door L77-95）|
| recessed_finger_pull | rec_variant-handle-recessed-finger-pull-...968aa0b6 | `_finger_pull_slab` CadQuery L72-90 + `finger_pull_groove` accent L114-118 | eligible if compatible | 嵌入式抠手槽（`slot2D().cutBlind` 切 front 面顶缘）+ 槽内深色 accent trim，**无凸出件**（front_slab 改 CadQuery mesh）|
| round_knobs | rec_variant-handle-round-knobs-...0504431c | `_make_drawer_knob_mesh` lathe L68-92 + 每面 `knob_{i}` 循环 L154-161 | eligible if compatible | 每储物面 2 个圆旋钮（`LatheGeometry` 旋钮 silhouette 旋到 +X），`for i in range(2)` 沿 Y 间距并排，凸出 ~0.028 m |

## 槽位图（slot graph）

pattern: mixed（固定 named slots: base_support + storage_mechanism + handle 各挂共同 `carcass`（parallel children），外加 `drawer_count` 在 storage=two_prismatic_drawers 下沿 +Z 栈复制抽屉）

```
carcass (root, 坐地; 中空灰壳 + gallery lip 顶台 + 侧/后板 + runner rails + bottom panel)
  │
  ├── [base_support slot]  (carcass-local visual, 互斥四选一, 无 joint)
  │     ├─ inset_floating_plinth : plinth (inset Box, BODY_BOT_Z=0.045)
  │     ├─ four_splayed_legs     : leg_{i}×4 (lathe+splay, BODY_BOT_Z=LEG_H=0.12, H 重算)
  │     ├─ solid_toe_kick_box    : base_upper + base_toekick (落地, BASE_H=0.055)
  │     └─ hairpin_metal_legs    : hairpin_leg_{i}×4 + 安装板 (tube, BODY_BOT_Z=0.12, H 重算)
  │
  ├── [storage_mechanism slot]  (主机构, 互斥四选一)
  │     ├─ two_prismatic_drawers : drawer_{i} ──[carcass_to_drawer_{i}: PRISMATIC axis=+X, origin=(D,0,CZ[i])]  (i∈range(N))
  │     ├─ hinged_cabinet_door   : door ──[carcass_to_door: REVOLUTE axis=+Z, origin=(D,HINGE_Y,DOOR_CZ)]
  │     ├─ drop_down_flap_door   : flap_door ──[carcass_to_flap_door: REVOLUTE axis=+Y, origin=(HINGE_X,0,HINGE_Z)]
  │     └─ open_niche_over_drawer: divider_shelf(固定) + drawer ──[carcass_to_drawer: PRISMATIC axis=+X]  (N=1)
  │
  ├── [handle slot]  (储物面 non-moving visual, 互斥三选一, 无 joint)
  │     ├─ chrome_bar_on_posts : handle_post_{i}+handle_bar  (inline 到 drawer/door)
  │     ├─ recessed_finger_pull: front_slab 改 CadQuery 抠手槽 + finger_pull_groove accent
  │     └─ round_knobs         : knob_{i}×2  (inline 到每储物面)
  │
  └── [drawer_count multiplicity 轴]  drawer_{i} / carcass_to_drawer_{i}  i∈range(N)
        仅 storage=two_prismatic_drawers 展开 N∈[1,4]; 其余 storage 固定 N∈{0,1}
        沿 +Z 均匀栈 (CZ[i] 绝对式由 N 与 ZONE_H 解析)
```

接口点位与 joint 语义：
- **base_support 接口（互斥, 无 joint）**：plinth / 腿 / 踢脚箱均 inline 为 `carcass` 的 visual，坐地（min z≈0）。腿类令 `BODY_BOT_Z=LEG_H`、`H=LEG_H+CARCASS_BODY_H`（carcass body 高 0.405 保持），plinth/toe_kick 令 H=0.45。base 与储物/把手**正交**（任意 base 配任意 storage/handle）。
- **storage_mechanism 接口（互斥）**：
  - two_prismatic_drawers：抽屉 child 原点 = front_slab 外面（local x=0），`carcass_to_drawer_{i}` **PRISMATIC** axis=(1,0,0)，origin=(D,0,CZ[i])（carcass 前开口面 +X），q=0 前面 flush、tray 内嵌；runner rail 锚定原点几何。
  - hinged_cabinet_door：`door` 原点在侧铰线，`carcass_to_door` **REVOLUTE** axis=(0,0,1)，origin=(D,HINGE_Y,DOOR_CZ)（前面侧缘 +Z 铰），q=0 闭合 flush、外开。
  - drop_down_flap_door：`flap_door` 原点在底铰线，`carcass_to_flap_door` **REVOLUTE** axis=(0,1,0)，origin=(HINGE_X,0,HINGE_Z)（前缘底部），q=0 竖直闭合、下翻打开。
  - open_niche_over_drawer：上 `divider_shelf` 固定无 joint，下单 `drawer` 同 two_prismatic_drawers 的 PRISMATIC（N 固定 1）。
- **handle 接口（互斥, 无 joint）**：把手 / 旋钮 inline 到储物面 part（drawer 或 door）的 visual；finger_pull 是把 front_slab 换成带槽 CadQuery mesh（无新增凸件）。Rule 1：把手非移动件。
- **drawer_count 接口（多重性）**：每抽屉一对 `(drawer_{i}, carcass_to_drawer_{i})`，沿 +Z 绝对式均匀栈（`CZ[i]` 由 N 与 ZONE_H 解析，非累加漂移）；每只独立 PRISMATIC。仅 two_prismatic_drawers 展开（N∈[1,4]）。
- **mating policy**：抽屉滑轨是 tray-on-rail captured-slide（runner rail 托盘底）、门铰是 hinge-at-edge（door 原点在前缘铰线）—— 几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin（runner rail / 前开口面 / 铰线硬件）+ whole-part / element-scoped `allow_overlap` 守 closed-pose 共面 overlap（照搬各样本 run_tests 的 allow_overlap 段 / expect_within）。
- **rest pose**：所有抽屉 q=0 前面 flush、门 / 翻门 q=0 闭合（lower=0）；base 坐地。
- **互斥 / 可选 / 派生**：base_support 四候选互斥；storage_mechanism 四候选互斥；handle 三候选互斥；drawer_count 仅在 two_prismatic_drawers 下为自由轴，其余 storage 派生固定 N（door/flap→0 抽屉、niche→1 抽屉）（见 §9 兼容矩阵）。

## 每槽位 Module Emits / Interfaces

### Slot A / base_support — inset_floating_plinth（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`plinth` 为 carcass visual）| parent `plinth` L152-157 |
| internal joints | 无 | — |
| upstream interface | inline 到 `carcass`，四面内收，坐地；`BODY_BOT_Z=PLINTH_H=0.045`，H=0.45 | parent L152-157 |
| downstream interface | 抬起 carcass body，供 storage/handle 在其上发射 | parent L159 |

### Slot A / base_support — four_splayed_legs
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`leg_{i}`×4 为 carcass visual）| legs `_make_leg_mesh` L78-108 |
| internal joints | 无 | — |
| upstream interface | 四角 lathe 锥腿（splay 8°）embed 2 mm 入 carcass 底，坐地；`BODY_BOT_Z=LEG_H=0.12`，H≈0.525 | legs L201-210 + L48-52 |

### Slot A / base_support — solid_toe_kick_box
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`base_upper`+`base_toekick` 为 carcass visual）| toe_kick L160-175 |
| internal joints | 无 | — |
| upstream interface | 全宽全深 base_upper + 前缩 base_toekick（踢脚凹），坐地；`BASE_H=0.055`，H=0.45 | toe_kick L157-175 |

### Slot A / base_support — hairpin_metal_legs
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`hairpin_leg_{i}`×4 + 安装板 为 carcass visual）| hairpin `_build_hairpin_leg_mesh` L74-99 |
| internal joints | 无 | — |
| upstream interface | 四角 U 形钢 rod + 安装板，坐地；`BODY_BOT_Z=LEG_H=0.12`，H≈0.525 | hairpin L191-210 |

### Slot B / storage_mechanism — two_prismatic_drawers（基线 + drawer_count 载体）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drawer_{i}`（`front_slab` + hollow open-top tray: `tray_bottom`/`tray_back_wall`/`tray_side_wall_{tag}`/`tray_front_wall` + 把手）| parent `_build_drawer` L62-134 |
| internal joints | `carcass_to_drawer_{i}` PRISMATIC axis=(1,0,0)，origin=(D,0,CZ[i])，lower=0/upper=0.36 | parent L217-226 / N=3 L223-233 |
| upstream interface | front_slab 外面 flush carcass 前开口 +X；tray 底坐 runner rail | parent L191-205, L296-307 |

### Slot B / storage_mechanism — hinged_cabinet_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | `door`（`door_panel` + 把手）| hinged `_build_door` L60-100 |
| internal joints | `carcass_to_door` REVOLUTE axis=(0,0,1)，origin=(D,HINGE_Y,DOOR_CZ)，lower=0/upper=DOOR_OPEN_ANGLE | hinged L184-195 |
| upstream interface | door 原点在前面侧缘铰线；闭合 flush | hinged L60-66, L184-189 |

### Slot B / storage_mechanism — drop_down_flap_door
| emits | 描述 | 来源 |
|---|---|---|
| parts | `flap_door`（`door_slab` + 铬条把手）| flap L157-167 |
| internal joints | `carcass_to_flap_door` REVOLUTE axis=(0,1,0)，origin=(HINGE_X,0,HINGE_Z)，lower=0/upper≈1.50 | flap L180-189 |
| upstream interface | flap_door 原点在前缘底部铰线；q=0 竖直闭合 | flap L159-167, L180-186 |

### Slot B / storage_mechanism — open_niche_over_drawer
| emits | 描述 | 来源 |
|---|---|---|
| parts | `divider_shelf`（carcass 固定隔板 visual）+ 单 `drawer`（同 two_prismatic_drawers）| niche `divider_shelf` L193-199 / `_build_drawer` L70 |
| internal joints | `carcass_to_drawer` PRISMATIC axis=(1,0,0)，origin=(D,0,CZ_DRAWER)，lower=0/upper=0.36（N 固定 1）| niche L231-240 |
| upstream interface | divider_shelf 隔出上开放格（无 joint）+ 下抽屉 front flush | niche L192-199, L231-237 |

### Slot C / handle — chrome_bar_on_posts（基线；door 复用同型）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`handle_post_{i}`+`handle_bar` inline 到 drawer/door）| parent L119-131 / hinged L77-95 |
| internal joints | 无（Rule 1）| — |
| placement | 储物面外面，凸出 ~0.019 m，沿 Y 双柱 | parent L116-131 |

### Slot C / handle — recessed_finger_pull
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（front_slab 改 CadQuery 抠手槽 mesh + `finger_pull_groove` accent visual）| finger `_finger_pull_slab` L72-90 / accent L114-118 |
| internal joints | 无 | — |
| placement | 顶缘嵌入槽（cutBlind），无凸出件 | finger L82-89 |

### Slot C / handle — round_knobs
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`knob_{i}`×2 inline 到每储物面）| knobs `_make_drawer_knob_mesh` L68-92 |
| internal joints | 无 | — |
| placement | `for i in range(2)` 沿 Y 间距并排，凸出 ~0.028 m | knobs L150-161 |

### drawer_count multiplicity（抽屉复制；joint-bearing）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `drawer_{i}`（hollow tray + front_slab + handle）| N=3 `_build_drawer` L66 / loop L219-221 |
| joints | `carcass_to_drawer_{i}` PRISMATIC ×N（每抽屉独立 +X）| N=3 L223-233 |
| placement | `for i in range(N)`，沿 +Z 绝对式均匀栈（`CZ[i]` 由 N 与 ZONE_H 解析）| N=3 `CZ` L55 / N=1 `DRAWER_CZ` L69-72 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| base_support | enum | inset_floating_plinth / four_splayed_legs / solid_toe_kick_box / hairpin_metal_legs | inset_floating_plinth | choice | sampler 选；决定底座 visual + lift（腿类抬 BODY_BOT_Z）| module table |
| storage_mechanism | enum | two_prismatic_drawers / hinged_cabinet_door / drop_down_flap_door / open_niche_over_drawer | two_prismatic_drawers | choice | sampler 选；主机构（互斥）；门槛 drawer_count（见下 conditional）| module table |
| handle | enum | chrome_bar_on_posts / recessed_finger_pull / round_knobs | chrome_bar_on_posts | choice | sampler 选；储物面非移动 visual（互斥）| module table |
| drawer_count (N) | int | 声明域 [1,4]；sweep 采样域 [1,4]（偏小加权：1/2 高频、3 常见、4 长尾）| 2 | conditional→slot_choice | 编入 slot_choice `n{N}`（拓扑维度）；仅 storage=two_prismatic_drawers 自由，door/flap→N=0、niche→N=1（见 §8）| N=1 / N=3 / parent |
| palette_style | enum | gray_lacquer / warm_walnut / matte_white / charcoal_chrome | gray_lacquer | palette | palette only，**不计入 slot_choice** | 各样本材质 |
| width_scale | float | [0.85, 1.18] | 1.0 | independent | 缩放 carcass W（Y 主尺寸），派生 INNER_W / 抽屉宽，clamp | resolve clamp |
| depth_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 carcass D（X 深 = 抽屉行程上限基），clamp | resolve clamp |
| body_height_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 CARCASS_BODY_H → ZONE_H → 抽屉/门高、HINGE_Z、CZ 栈，clamp | resolve clamp |
| leg_lift_scale | float | [0.85, 1.20] | 1.0 | conditional | 仅 base∈{four_splayed_legs, hairpin_metal_legs} 有效；缩放 LEG_H，派生 H | resolve clamp |
| drawer_travel | float | [0.10, 0.36] | 0.36 | conditional | 仅 storage 含抽屉有效；PRISMATIC upper，≤ D−back margin | resolve clamp |
| door_open_angle | float | [0.80·π/2, 1.10] rad clamp ≤0.95π | 1.40 | conditional | 仅 storage∈{hinged_door, flap_door}；REVOLUTE upper | resolve clamp |
| drawer_pitch_scale | float | [0.92, 1.08] | 1.0 | conditional | 仅 storage=two_prismatic_drawers & N≥2；缩放栈间距，clamp ≤ ZONE_H 容纳 | resolve clamp |
| (—) | constraint | — | — | inequality | 抽屉栈不超腔：`N·FACE_H + (N-1)·FACE_GAP + FACE_TOP_MARGIN ≤ ZONE_H`；违反时缩 FACE_H / pitch 或拒绝重采（见 N=3 FACE_H 派生 L52）| 接口 / clearance |
| (—) | constraint | — | — | inequality | 抽屉行程留插：`drawer_travel ≤ BOX_D − margin`（开到位仍保 tray 部分入腔，retains_insertion）；超界回缩 | 接口 / clearance |
| (—) | constraint | — | — | inequality | 翻门下翻不撞地：base 为悬浮/腿时 flap 底铰 q=0 高度 ≥ flap 长 · sin（保 H 足够）；不足则降 door_open_angle 或 gate | 接口 / clearance |
| (—) | constraint | — | — | conditional | storage 决定 drawer_count 域：two_prismatic_drawers→N∈[1,4]；open_niche→N=1；hinged/flap_door→N=0（无抽屉栈，drawer_count 不进 slot_choice 的 n{N} 维或记 n0）| 接口 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 base_support / storage_mechanism / handle / N 的拓扑**。

## Multiplicity / Copy Logic

**1 根 multiplicity 轴**（堆叠抽屉数）：

- **count_param**：`drawer_count`（模板内变量 N；carcass 凹腔内沿 +Z 堆叠抽屉数；基线 2）。
- **N_range**：声明产品域 **[1, 4]**（床头柜抽屉数现实上限很小——单 / 双 / 三 / 四抽屉已覆盖真实形态；source map 建议 [1,4]。样本直接覆盖 N∈{1,2,3}，N=4 由 N=3 循环 `for i in range(N)` 直接外推同构，无新拓扑 → 纳入声明域上界，sweep 加权稀疏）。`config_from_seed` 的 sweep 采样域 **[1, 4]**（偏小加权：N=1/2 高频、N=3 常见、N=4 长尾）。
- **sampling domain**：`config_from_seed` 用 `rng.choices((1,2,3,4), weights=偏小)`（仅在 storage=two_prismatic_drawers 时采样）；`resolve_config` 把任意外部 config 的 N clamp 到 [1,4]，并按 storage conditional（door/flap→N=0、niche→N=1）覆写。
- **copied object**：单只抽屉单元——`drawer_{i}`（hollow open-top tray: `tray_bottom`/`tray_back_wall`/`tray_side_wall_{tag}`/`tray_front_wall` + `front_slab` + 把手），由共享 `_build_drawer` helper 发射（N 只复用同一 helper / 几何）。
- **naming**：`drawer_{i}` / `carcass_to_drawer_{i}`，`for i in range(N)`（N=3 L219-233 已用此结构，可直接作 copy-logic 源；N=1 用 `DRAWER_COUNT=1` 单循环等价 range(1)）。
- **placement**：沿 +Z **绝对式**均匀栈——`CZ[i] = BODY_BOT_Z + i·(FACE_H + FACE_GAP) + FACE_H/2`（N=3 L55）或 `BODY_BOT_Z + FACE_H·(i+0.5) + FACE_GAP·i`（N=1 L69-72）；`FACE_H` 随 N 派生填满 ZONE_H（N=3 L52）。绝对式（每 i 的 z 由 N 与 ZONE_H 解析、不累加漂移）是 N-不变前提。
- **joint policy**：每抽屉**独立** `carcass_to_drawer_{i}` **PRISMATIC** axis=(1,0,0)，origin=(D,0,CZ[i])，lower=0/upper=drawer_travel；抽屉互不联动（parent run_tests `drawers_independent` L341-346）。
- **source/gating**：copy-logic 源取 N=3 的 `for i in range(N_DRAWERS)` `drawer_{i}` + `carcass_to_drawer_{i}` 循环（L219-233）与 FACE_H/CZ 派生（L52-55）；N=1 取 single-drawer 退化（L209-235）。多重性**仅在 storage=two_prismatic_drawers 时展开**；hinged_door / flap_door 为 0 抽屉、open_niche 固定 1 抽屉（见 §9 矩阵）。

## 拓扑多样性审计

总组合数：base_support(4) × storage_mechanism(4) × handle(3) × drawer_count 有效采样（two_prismatic_drawers 下 4 档 {1,2,3,4}；其余 storage 各 1 档）。

近似计：4(base) × 3(handle) × [two_drawers×4(N) + hinged_door×1 + flap_door×1 + niche×1(N=1)] = 4 × 3 × 7 = **84** distinct（storage×N 联合 7 类）。

理由：storage_mechanism 提供真正 joint 拓扑差异（N×PRISMATIC(+X) / REVOLUTE(+Z) / REVOLUTE(+Y) / 固定格+单 PRISMATIC = 真 joint-topology 类），叠 drawer_count 把 PRISMATIC 抽屉栈细分为 N∈{1,2,3,4}（每 N 关节数不同 → 真拓扑维度），再叠 base(4) × handle(3)。**N 必须编入 `slot_choices_for_seed`**（`("drawer_count", f"n{N}")`，对齐 drawer_cabinet / cushion / shopping_bucket），否则单/双/三/四抽屉 slot_choice 同形，损失一整根拓扑维度。仅 base×handle×storage(无 N) = 4×3×4=48 已远超 10。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三 named slot（base_support / storage_mechanism / handle），经兼容矩阵合法化，再按 storage conditional 解析 drawer_count 域并 `rng.choices` 加权 N，再 uniform 各连续 scale（解析 conditional：leg_lift@腿、drawer_travel@含抽屉、door_open_angle@门、drawer_pitch@N≥2）。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。

Topology target：84 组合的采样空间下，1000-seed slot choice tuple distinct 预计接近组合上限（84，受真实结构词汇表约束，**低于建议的 ≥300**）。原因说明：床头柜是结构高度收敛的小类——真实形态就是 base(4) × storage 机构(4，含抽屉 N 细分) × handle(3) 这 ~84 组拓扑等价类，没有更多真实结构可加（参照已 approved 的 drawer_cabinet 同小类，50 seeds → 41 distinct，量级一致）；多样性的"细分"靠 §7 连续 scale（width/depth/height/leg_lift/travel/angle/pitch）与 palette 实现而非新拓扑。84 distinct 远超 ≥10 机械门槛，符合本小类真实结构上限。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：见 §参数表的 width_scale / depth_scale / body_height_scale / leg_lift_scale（conditional@腿）/ drawer_travel（conditional@含抽屉）/ door_open_angle（conditional@门）/ drawer_pitch_scale（conditional@N≥2）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot + 解析 storage→N 域 + N（解析 conditional 范围）→ 采 independent width/depth/height scale → 派生（H=BODY_BOT_Z+CARCASS_BODY_H·height_scale；INNER_W、FACE_H 随 width/height 派生；DOOR_CZ/HINGE_Z 随 height 派生）→ 用三条 clearance inequality（抽屉栈不超腔、行程留插、翻门不撞地）投影 / 回缩。跨部件依赖（抽屉栈 vs ZONE_H、行程 vs 腔深、翻门 vs 离地高）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏抽屉 PRISMATIC origin / 门铰 origin / runner rail 接口 / N 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（经兼容矩阵），按 storage 解析 N 域后 `rng.choices` 加权 N，再 uniform 各 scale（按 conditional 解析） | slot_choices_for_seed 含 `("drawer_count", f"n{N}")` 且与 build 一致 |
| compatibility matrix | (1) **storage × drawer_count**：仅 two_prismatic_drawers 展开 N∈[1,4]；open_niche 固定 N=1；hinged_cabinet_door / drop_down_flap_door 为 0 抽屉栈（drawer_count 记 n0，不复制抽屉）。(2) **base × storage/handle 正交**：四 base 可配任意 storage / handle（base 只改 carcass 底座 visual + lift，不碰储物 part 树）。(3) **handle × storage**：chrome_bar / round_knobs 配抽屉与门均可（door 复用同型把手 helper）；recessed_finger_pull 把储物面 front_slab 换 CadQuery 槽 mesh，配抽屉与平板门可，**与 round_knobs 互斥**（一面一种）。(4) **flap_door × 腿/悬浮 base**：翻门下翻需足够离地高，base=腿（H≈0.525）安全，base=plinth/toe_kick（H=0.45）时 clamp door_open_angle 保翻门不撞地（见 §7 inequality）。 | 无 floating / collision / 抽屉数≠关节数 / 门撞地 / 行程不足 / 把手穿模 |
| controlled local variation | 8 个 clamped scale（width/depth/body_height、leg_lift@腿、drawer_travel@含抽屉、door_open_angle@门、drawer_pitch@N≥2），每 build 统一；conditional 按上游 enum/N 解析 | 比例变化不破坏 PRISMATIC/REVOLUTE origin、runner rail/铰线接口、抽屉栈、坐地、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| base_support | 4 | yes | yes | plinth(parent) + 三 fork（腿 / 踢脚 / 发夹）|
| storage_mechanism | 4 | yes | yes | N×PRISMATIC / REVOLUTE(+Z) / REVOLUTE(+Y) / 固定格+PRISMATIC（互斥主机构）|
| handle | 3 | yes | yes | 铬条 / 抠手槽 / 旋钮（非移动 visual）|
| drawer_count (N) | 4（采样域 {1,2,3,4}，1/2 高频 / 4 长尾）| yes | yes | joint-bearing 拓扑维度，编入 slot_choice；仅 two_prismatic_drawers 展开 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，且含 `("drawer_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，N 采样域 ⊆ [1,4] 且仅 two_prismatic_drawers 自由（door/flap→n0、niche→n1）
- `resolve_config` 把 drawer_count clamp 到 [1,4] 并按 storage conditional 覆写；各 scale clamp 到声明范围；leg_lift/drawer_travel/door_open_angle/drawer_pitch 为 conditional 随 base/storage/N 解析；三条 clearance inequality 在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（drawer_count 仅 two_prismatic_drawers 展开；flap_door 离地不足时 clamp door_open_angle；finger_pull 与 round_knobs 互斥）
- 连续 scale clamp 后不破坏抽屉 PRISMATIC origin / 门铰 REVOLUTE origin / runner rail 接口 / N 复制 / 坐地 / 类别身份
- 关键 joint：two_prismatic_drawers `carcass_to_drawer_{i}` PRISMATIC axis≈(1,0,0)（abs(axis[0])>0.99、abs(axis[2])<0.01）×N；hinged_cabinet_door `carcass_to_door` REVOLUTE axis≈(0,0,1)；drop_down_flap_door `carcass_to_flap_door` REVOLUTE axis≈(0,1,0)；open_niche `carcass_to_drawer` PRISMATIC +X（N=1）
- captured-slide / closed-pose overlap：whole-part / element-scoped `allow_overlap`（drawer↔carcass、相邻 drawer front 共面、door↔carcass 闭合、tray↔runner rail），照搬各样本 run_tests 的 allow_overlap / expect_within 段
- copied object 遵循 `drawer_{i}` / `carcass_to_drawer_{i}` 命名 + 绝对式沿 +Z 均匀栈 placement + 每抽屉独立 PRISMATIC
- grandfather：所有抽屉滑轨 / 门铰 captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把 N 当普通 int 参数、不进 slot_choice → 单/双/三/四抽屉 slot_choice 同形，损失拓扑维度（违反 §8/§9 硬要求）。
- drawer_count 在 hinged_cabinet_door / drop_down_flap_door 下仍复制抽屉栈 → 门后塞抽屉无样本支持、穿模；door/flap 必须 N=0，niche 固定 N=1。
- 抽屉栈 N·FACE_H 超过 ZONE_H（栈溢出顶台 / 底座）→ §7 第一条不等式 FAIL；须按 N 派生 FACE_H 填满 ZONE_H（照 N=3 L52）。
- drawer_travel 设过大致开到位 tray 完全脱腔 → retains_insertion FAIL；须 ≤ BOX_D − margin。
- 把抽屉滑动轴设为非 +X、或门铰 origin 放在腔中心而非前开口面 / 铰线硬件 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- 把把手 / 旋钮当独立活动 part 加 joint → 违反 Rule 1（把手非移动件，应 inline 到储物面 visual）。
- base=plinth/toe_kick（离地低）配 flap_door 大下翻角致翻门撞地 → §7 第三条不等式 FAIL；须 clamp door_open_angle 或 gate。
- 抽屉 / 门 rest pose 设成张开而非 q=0 闭合 → current-pose 与 viewer 目检不符（所有样本闭合 lower=0）。
- 把连续尺寸 / 颜色 / 材质（palette_style / *_scale）当新 candidate 塞进 slot → 不是结构差异。
- 把"大衣柜 / 多列斗柜 / 书桌 / 保险柜"语义混入 → 出类，本类是床头**小柜**（单宽、抽屉数小、含 ≥1 储物开合活动件）。

## 与相邻类别的边界

- 不该混入：**衣柜 / 多抽屉斗柜（dresser / chest of drawers）**——本类是床头小柜（单宽 ~0.65 m、N≤4），不是高宽多列大柜；高列大柜见 `drawer_cabinet_with_sliding_drawers` slug。
- 不该混入：**书桌 / 带桌面单抽屉桌（desk_with_drawer）**——本类主体是收纳壳，无大工作桌面。
- 不该混入：**保险柜 / 带拨盘箱门（wall_safe_with_hinged_door_and_dial）**——金属箱 + 拨盘，非木 / 漆床头柜壳。
- 不该混入：**开放置物架（shelf）**——纯开放无开合机构；本类必含 ≥1 储物开合活动件（抽屉 / 门 / 翻门）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) base_support 建模为 carcass-local visual 维度（非串联 slot、无独立 joint）；(2) drawer_count N_range 取 [1,4]（N=4 由 N=3 循环外推、无新拓扑，sweep 稀疏）是否接受；(3) storage × drawer_count 兼容（door/flap→N=0、niche→N=1、仅 two_prismatic_drawers 自由）；(4) flap_door × 低离地 base 的 door_open_angle clamp / gate 策略；(5) Topology target 84<300 的说明是否接受（本小类真实结构上限，对齐 drawer_cabinet 41 distinct）；(6) handle finger_pull 与 round_knobs 互斥 + Rule 1 inline 无独立 joint 是否符合期望）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：`_build_drawer`（抽屉，N 复制复用）、`_build_door`（侧铰门）、`flap_door` build（翻门）、`_make_leg_mesh`/`_build_hairpin_leg_mesh`（base 腿 mesh，按 base_support 切换）、`_finger_pull_slab`（CadQuery 抠手 front_slab）、`_make_drawer_knob_mesh`（旋钮 lathe）。把手 helper 在 drawer 与 door 间共享（hinged door 已复用铬条把手同型）。
- captured 接口 allow_overlap / expect_within：`run_bedside_tests` 里逐机构补 whole-part / element-scoped `allow_overlap`（drawer↔carcass 闭合、相邻 drawer front 共面、door↔carcass、tray↔runner rail）+ `expect_within(drawer, carcass, axes="y")`，照搬各样本 run_tests 段（parent L323-324、drawer_independence L341-346）。
- conditional 范围解析顺序：先采 base / storage / handle / N（按 storage 解析 N 域）→ 解析 leg_lift（仅腿）/ drawer_travel（仅含抽屉）/ door_open_angle（仅门）/ drawer_pitch（仅 N≥2）→ 采 width/depth/body_height independent scale → 派生 H / INNER_W / FACE_H / DOOR_CZ / HINGE_Z → 投影三条 clearance inequality。
- base lift 派生：腿类（four_splayed_legs / hairpin_metal_legs）令 `BODY_BOT_Z=LEG_H`、`H=LEG_H+CARCASS_BODY_H`（CARCASS_BODY_H=0.405·body_height_scale）；plinth 令 BODY_BOT_Z=PLINTH_H=0.045、H≈0.45；toe_kick 令 BODY_BOT_Z=BASE_H=0.055、H≈0.45。
- N=1 退化：用 single-drawer 路径（DRAWER_COUNT=1，等价 range(1)）；N≥2 走 `for i in range(N)` `drawer_{i}` + `CZ[i]` 栈。
- 参考模板：`agent/templates/drawer_cabinet_with_sliding_drawers.py`（**同小类、已 approved**：mixed pattern + cabinet body slot + drawer_count joint-bearing multiplicity（`"{N}_drawers"` 进 slot_choice）+ 前 stile/runner rail 锚定 PRISMATIC origin + 可选 REVOLUTE 门 + 木/漆 palette + whole-part allow_overlap，本类几乎同构改编，再加 base_support 四候选 + handle 三候选)；次参考 `agent/templates/Accessories_Cushion.py`（mixed: 固定 named slots + multiplicity 进 slot_choice + 兼容矩阵 gating）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S0 | A/B/C（parent 基线）| plinth + two_prismatic_drawers + chrome_bar | rec_model-a-modern-two-drawer-bedside-nightstand-...c9162b4f | `plinth` L152-157 / `_build_drawer` L62-134 / `carcass_to_*_drawer` PRISMATIC L217-226 / handle L116-131 | 基线 carcass + plinth + 双抽屉 PRISMATIC + 铬条把手 + drawer copy-logic |
| S1 | A | four_splayed_legs | rec_variant-base-support-four-splayed-legs-...65751baf | `_make_leg_mesh` L78-108 / `leg_{i}` L201-210 / BODY_BOT_Z=LEG_H L48-52 | 外撇锥腿 base + lift 派生 |
| S2 | A | solid_toe_kick_box | rec_variant-base-support-solid-toe-kick-box-...6dddcda5 | `base_upper` L160-165 / `base_toekick` L170-175 | 落地踢脚箱 base |
| S3 | A | hairpin_metal_legs | rec_variant-base-support-hairpin-metal-legs-...dcdcb159 | `_build_hairpin_leg_mesh` L74-99 / `hairpin_leg_{i}`+安装板 L191-210 | 发夹钢腿 base |
| S4 | B | hinged_cabinet_door | rec_variant-storage-mechanism-hinged-cabinet-door-...02643395 | `_build_door` L60-100 / `carcass_to_door` REVOLUTE +Z L184-195 | 侧铰柜门（REVOLUTE +Z）|
| S5 | B | drop_down_flap_door | rec_variant-storage-mechanism-drop-down-flap-door-...2bf8cef6 | `flap_door` L157-167 / `carcass_to_flap_door` REVOLUTE +Y L180-189 | 底铰下翻门（REVOLUTE +Y）|
| S6 | B | open_niche_over_drawer | rec_variant-storage-mechanism-open-niche-over-drawer-...bd3941ca | `divider_shelf` L193-199 / `carcass_to_drawer` PRISMATIC L231-240 | 固定开放格 + 单抽屉 |
| S7 | C | recessed_finger_pull | rec_variant-handle-recessed-finger-pull-...968aa0b6 | `_finger_pull_slab` CadQuery L72-90 / `finger_pull_groove` L114-118 | 嵌入抠手槽把手 |
| S8 | C | round_knobs | rec_variant-handle-round-knobs-...0504431c | `_make_drawer_knob_mesh` L68-92 / `knob_{i}` L154-161 | 双圆旋钮把手 |
| S9 | D（multiplicity）| drawer_count N=1 | rec_variant-drawer-count-1-make-it-a-single-tall-...b8d0c6c4 | `DRAWER_COUNT=1` / `DRAWER_CZ` L69-72 / `for i in range(DRAWER_COUNT)` L209-235 | 单抽屉退化 copy-logic 源 |
| S10 | D（multiplicity）| drawer_count N=3 | rec_variant-drawer-count-3-make-it-a-three-stacked-...50c223fe | `N_DRAWERS=3` / `FACE_H`/`CZ` L52-55 / `for i in range(N_DRAWERS)` `drawer_{i}`+`carcass_to_drawer_{i}` L219-233 | 三抽屉栈 copy-logic 源（FACE_H/CZ 派生）|
