# lighter — Modular Spec

> 来源小类：`picture/Other/Lighter`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Other__Lighter.md`。
> **"lighter" 在此 = 一次性燧石/电子口袋打火机（disposable / flint / piezo pocket lighter，BIC 式），不是 zippo_lighter（既有翻盖防风金属打火机模板，见下相邻边界）。**
> 结构家族 = 中空储液壳体 + 顶部点火机构（燧石滚轮+撬杆 或 电子压电按钮）+ 铬罩 hood band/cheeks，外加可选喷嘴盖与火焰高度调节轮。
>
> **同步状态**：本 spec 引用的 7 个 5 星样本（1 个 parent + 6 个 fork 槽位变体）已同步进本仓库 `data/records/`，rating=5。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一核对）。引用以 part / joint / helper **名字** 为准（`reservoir_shell` / `hood_band` / `hood_cheeks` / `spark_wheel` / `fuel_lever` / `piezo_button` / `flip_top_cap` / `nozzle_cover` / `flame_adjust` 等），行号作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `lighter` |
| template path | `agent/templates/Other_Lighter.py` |
| test path (optional) | `tests/agent/test_lighter_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 named slots：body_shape + ignition_mechanism(主机构) + cap + flame_adjust，全部挂到共同 root `body`；无核心 multiplicity）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7（1 parent + 6 fork 槽位变体；均 converged，compile success、≥1 非 fixed joint、workbench-only）|
| read_count | 7（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 7/7 全部被采纳为某槽位 source，无未采用样本，无排除项 |

阅读要点（用于槽位分解）：
- **共享基线拓扑**（所有 7 样本）：root `body` 持有 `reservoir_shell`（中空蓝色储液壳，上口可见空腔）+ `valve_deck`（凹陷灰阀台）+ `flame_nozzle`/`nozzle_collar`（前喷嘴）+ `flint_tube`（滚轮下燧石管）+ `hood_band`（铬罩，前火焰缺口/侧通气孔/后切口）+ `hood_cheeks`（夹滚轮的双铬颊板）。基线点火 = `spark_wheel`（CONTINUOUS X，knurled KnobGeometry）+ `fuel_lever`（REVOLUTE -X，撬杆抬阀叉）。整机高 ~0.08 m，平面 ~0.025×0.012 m。
- **body_shape 轴**（Slot A）：parent stadium（`slot2D(BODY_LEN, BODY_DEP, 90)`）/ round（`circle(BODY_R)` lathe）/ rectangular（`rect(BODY_DEP, BODY_LEN)` 方角板）。三者**part 树 / joint 拓扑完全一致**，仅 `_reservoir_shell` / `_valve_deck` / `_hood_band` 的 2D 截面 profile 重写 → body_shape 是 mesh-helper 维度，不改拓扑（与 zippo body_case / cushion footprint 同性质）。
- **ignition_mechanism 轴**（Slot B，**主机构槽**）：flint_spark_wheel（`spark_wheel` CONTINUOUS X + `fuel_lever` REVOLUTE -X，**2 个非 fixed joint**）vs piezo_push_button（`piezo_button` 单 PRISMATIC -Z，**1 个非 fixed joint**，且**移除 spark_wheel + fuel_lever + hood_cheeks，改 hood 顶板 + button_guide 导柱 + piezo_electrode**）→ 真正的 part 数 / joint 类型 / joint 数拓扑变化。这是打火机身份的核心机构（点火方式）。
- **cap 轴**（Slot C）：none（无盖，parent/round/rect/piezo 默认）/ flip_top_cap（`flip_top_cap` 独立 part，REVOLUTE +X 翻盖 0→2.1rad，body 加 `cap_hinge_pin` 销）/ sliding_nozzle_cover（`nozzle_cover` 独立 part，PRISMATIC +Y 滑开 0→0.010，body 加 `slide_rail_0/1` 双轨）→ 盖机构是 part 数 / joint 拓扑变化（REVOLUTE vs PRISMATIC vs 无）。
- **flame_adjust 轴**（Slot D）：none（无调节，默认）/ flame_height_thumb_wheel（`flame_adjust` 独立 part，环抱喷嘴基部，CONTINUOUS Z 旋转 + `adjust_tooth_{i}` 滚花 inline 循环）→ 增 1 个 CONTINUOUS Z joint 的 part 拓扑变化。

## 核心身份

一只**一次性口袋打火机**（disposable / flint / piezo pocket lighter，BIC 式）：一只中空塑料**储液壳体** `body`（半透明royal-blue stadium / 圆柱 / 方板截面，上口可见空腔，内有凹陷灰阀台 `valve_deck`），阀台上立**铬火焰喷嘴** `flame_nozzle` + collar，顶部包一圈**铬防风罩** `hood_band`（前火焰缺口、侧通气孔、后切口露撬杆）。点火机构二选一：**燧石滚轮式**（夹在双铬颊板 `hood_cheeks` 间的滚花钢轮 `spark_wheel` CONTINUOUS 自转打火 + 撬杆 `fuel_lever` REVOLUTE 抬阀放气）或**电子压电按钮式**（顶部红色按钮 `piezo_button` PRISMATIC 直压点火，无滚轮无撬杆）。可选**喷嘴盖**（翻盖 REVOLUTE / 滑盖 PRISMATIC 罩住喷嘴）与可选**火焰高度调节轮**（喷嘴基部 `flame_adjust` 环 CONTINUOUS Z 旋转调火）。整机直立坐地于 body 底，高 ~0.08 m。默认成熟域：body_shape × ignition × cap × flame_adjust 的小型手持一次性打火机。

不该混入：
- **zippo_lighter（既有模板）**——防风金属壳翻盖打火机：方钢壳 + 永久铰接翻盖（lid 始终在）+ insert 燃料仓 + cam lever，是不同结构家族（金属壳/翻盖永在/insert 分件）。本类是一次性塑料壳，盖为可选附加件而非身份核心，且有 piezo 电子点火分支。
- **火柴 / 长杆点火枪（utility lighter / candle lighter）**——长柄扳机机构，非口袋直立壳体。
- **煤气灶点火器 / 工业点火枪**——非口袋一次性形态。

## 槽位 + 候选模块表

> **建模注记**：`body_shape`（Slot A）是 `reservoir_shell` / `valve_deck` / `hood_band` **同一组 mesh 的截面 profile 家族**（stadium / round / rectangular），由 shape-aware mesh helper 一次决定，不是独立串联 slot、不贡献额外 joint；列为候选轴以对齐 schema，它与 ignition × cap × flame_adjust 的笛卡尔积共同撑开多样性（见 §9）。`ignition_mechanism`（主机构）、`cap`、`flame_adjust` 才是真正改 part 树 / joint 拓扑的轴。

### Slot A：body_shape（壳体截面家族——reservoir+deck+hood 共享的 2D profile）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| stadium_oval（基线） | parent (rec_model-a-classic-...c45ce5f7) | `_reservoir_shell` L78-86 / `_valve_deck` L89-95 / `_hood_band` L98-122 | eligible if compatible | `slot2D(BODY_LEN, BODY_DEP, 90)` 椭圆 stadium 储液仓；plan 0.025×0.012；基线 footprint |
| round_cylindrical | rec_variant-body-shape-round-cylindrical-...099fd912 | `_round_profile` L79-81 / `_reservoir_shell` L85-90 / `_valve_deck` L94-97 / `_hood_band` L101-129 | eligible if compatible | `circle(BODY_R)` 圆筒（lathe），d≈0.020；X≈Y 圆对称；part 树/joint 与 parent 一致，仅 profile 改 circle + AXLE_LEN 适配 |
| rectangular_slab | rec_variant-body-shape-rectangular-slab-...d28014ae | `_reservoir_shell` L84-93 / `_valve_deck` L96-103 / `_hood_band` L123-143 (+ `_hood_vent_cuts` L106-120 / `_vent_slot_geometry` L188-194) | eligible if compatible | `rect(BODY_DEP, BODY_LEN)` 方角扁板（无圆端）；4 个 `vent_slot_{i}` 通气孔 inline 视觉；part 树/joint 与 parent 一致 |

### Slot B：ignition_mechanism（点火机构 —— **主机构槽**，决定 part 树与 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| flint_spark_wheel（基线） | parent (rec_model-a-...c45ce5f7) | `spark_wheel` part L208-227 + `body_to_spark_wheel` CONTINUOUS L228-236 + `fuel_lever` part L239-261 + `body_to_fuel_lever` REVOLUTE L262-272 + `_hood_cheeks` L125-131 + `flint_tube` L191-196 + `_lever_pad`/`_lever_fork` L134-153 | eligible if compatible | **2 个非 fixed joint**：`spark_wheel`（knurled KnobGeometry）CONTINUOUS axis=(1,0,0) 自转打火；`fuel_lever`（撬杆 pad+fork+boss+pin）REVOLUTE axis=(-1,0,0)，0→-0.21rad 撬杆抬阀。滚轮夹在 `hood_cheeks` 间，pin 为 captured-pin |
| piezo_push_button | rec_variant-ignition-mechanism-piezo-push-button-...62f5cdf2 | `piezo_button` part L253-280 + `body_to_piezo_button` PRISMATIC L283-296 + body `button_guide` L224-231 + `piezo_electrode` L216-222；hood 顶板 `_hood_band` plate L141-157 | eligible if compatible | **1 个非 fixed joint**：`piezo_button`（domed cap + stem）PRISMATIC axis=(0,0,-1)，0→0.002m 直压点火。**移除 spark_wheel / fuel_lever / hood_cheeks**，改 hood 顶板带 stem 孔 + 阀台 `button_guide` 导柱 + `piezo_electrode` 电极。stem 滑过 guide 为 captured-sleeve |
> 注：一次性打火机点火现实词汇表仅燧石轮 vs 电子压电两类，本槽 2 候选已近真实上限（SPEC_TEMPLATE §4 允许样本池不足时降到 2，须说明理由——此处为类别真实结构上限，非样本池不足）。模板侧以 cap + flame_adjust 作机构多样性补充（见 §9）。

### Slot C：cap（喷嘴盖/罩 —— 可选，互斥三选一）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| open_hood（基线，无盖） | parent (rec_model-a-...c45ce5f7) + round + rect + piezo（4 样本默认无盖）| 无盖 part（固定 `hood_band` 即罩，无独立盖件）| eligible if compatible | 无独立盖 part / 无盖 joint；喷嘴直接由固定 hood band 半罩（默认形态） |
| flip_top_cap | rec_variant-cap-flip-top-cap-...47195100 | `flip_top_cap` part L364-386 + `body_to_flip_cap` REVOLUTE L388-398 + body `cap_hinge_pin` L289-295 + `_flip_cap_shell` L184-228 / `_grip_ridge` L231-235 | eligible if compatible | **翻盖** `flip_top_cap`（铬壳 + `cap_barrel` 铰筒 + `cap_grip_{i}` 防滑棱 inline）REVOLUTE axis=(1,0,0)，0→2.1rad（~120°）翻起露喷嘴；body 加 `cap_hinge_pin` 销（captured-pin）。与 flint 点火并存 |
| sliding_nozzle_cover | rec_variant-cap-sliding-nozzle-cover-...b701f9ec | `nozzle_cover` part L327-336 + `body_to_nozzle_cover` PRISMATIC L337-349 + body `slide_rail_0/1` L246-259 + `_nozzle_cover_plate` L173-... | eligible if compatible | **滑盖** `nozzle_cover`（铬 stadium 板 `cover_plate`）PRISMATIC axis=(0,1,0)，0→0.010m 沿 +Y 滑开露喷嘴；body 加 `slide_rail_0/1` 双轨（captured-slide）。与 flint 点火并存 |

### Slot D：flame_adjust（火焰高度调节 —— 可选，二选一）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| none（基线，无调节） | parent + round + rect + piezo + flip + sliding（6 样本默认无调节）| 无独立 part / 无 joint | eligible if compatible | 无火焰调节件（空机构，默认） |
| flame_height_thumb_wheel | rec_variant-flame-adjust-flame-height-thumb-wheel-...fe4840b8 | `flame_adjust` part L308-330 + `body_to_flame_adjust` CONTINUOUS L331-340 + `_adjust_ring` L170-177 / `_adjust_tooth` L180-184 | eligible if compatible | **调节轮** `flame_adjust`（环抱喷嘴基部的滚花环 `adjust_ring` + `adjust_tooth_{i}` 齿 inline 循环 N=16）CONTINUOUS axis=(0,0,1) 绕喷嘴自转调火高；环套 `nozzle_collar` 为 captured-sleeve。与任意 ignition / cap 并存 |

## 槽位图（slot graph）

pattern: parallel_children（固定 named slots：body_shape 决定 `body` 截面 mesh；ignition_mechanism + cap + flame_adjust 各自挂到共同 root `body`）

```
body (root, 坐地; body_shape 决定 reservoir_shell/valve_deck/hood_band 截面 mesh + flame_nozzle/flint_tube/hood 硬件)
  │
  ├── [ignition_mechanism slot]  (互斥二选一 —— 主机构)
  │     ├─ flint_spark_wheel : spark_wheel ─[body_to_spark_wheel: CONTINUOUS axis=+X, origin=滚轮轴心(0,WHEEL_Y,WHEEL_Z)]
  │     │                       fuel_lever  ─[body_to_fuel_lever:  REVOLUTE  axis=-X, origin=撬杆 pivot(0,-0.0092,0.0712)]
  │     │                       (body 含 hood_cheeks 夹滚轮; flint_tube 在滚轮下)
  │     └─ piezo_push_button  : piezo_button ─[body_to_piezo_button: PRISMATIC axis=-Z, origin=hood 顶(0,0,HOOD_Z1)]
  │                              (body 改 hood 顶板+button_guide 导柱+piezo_electrode; 无 hood_cheeks/无滚轮/无撬杆)
  │
  ├── [cap slot]  (互斥三选一, 可选)
  │     ├─ open_hood          : (无盖 part, 固定 hood_band 即罩)
  │     ├─ flip_top_cap       : flip_top_cap ─[body_to_flip_cap: REVOLUTE axis=+X, origin=铰线(0,HINGE_Y,HINGE_Z) hood 顶上方; body 加 cap_hinge_pin]
  │     └─ sliding_nozzle_cover : nozzle_cover ─[body_to_nozzle_cover: PRISMATIC axis=+Y, origin=hood 顶(0,SLIDE_ORIGIN_Y,HOOD_Z1); body 加 slide_rail_0/1]
  │
  └── [flame_adjust slot]  (二选一, 可选)
        ├─ none              : (无调节 part)
        └─ flame_height_thumb_wheel : flame_adjust ─[body_to_flame_adjust: CONTINUOUS axis=+Z, origin=喷嘴基部(0,NOZZLE_Y,ADJUST_Z)]
```

接口点位与 joint 语义：
- **ignition 接口（互斥主机构）**：所有点火件挂在 root `body` 上。
  - flint_spark_wheel：`spark_wheel` CONTINUOUS axis=(1,0,0)，origin=(0,WHEEL_Y,WHEEL_Z) 落在颊板间滚轮轴心，`wheel_axle` 为 captured-pin（穿 `hood_cheeks`/`hood_band`）；`fuel_lever` REVOLUTE axis=(-1,0,0)，origin=LEVER_PIVOT 落在 hood 内 pivot，`lever_pin` captured-pin。两件并行挂 body。
  - piezo_push_button：`piezo_button` PRISMATIC axis=(0,0,-1)，origin=(0,0,HOOD_Z1) 在 hood 顶板孔，`button_stem` 滑过 `button_guide` 导柱（captured-sleeve）。**此分支 body 不发射 hood_cheeks，且 hood_band 改带顶板**（见兼容矩阵）。
- **cap 接口（互斥可选）**：
  - open_hood：无 joint（固定 hood_band 半罩，默认）。
  - flip_top_cap：REVOLUTE axis=(1,0,0)，origin=(0,HINGE_Y,HINGE_Z) 落在 hood 顶上方铰线，body `cap_hinge_pin` ↔ cap `cap_barrel`（captured-pin）；q=0 闭合罩喷嘴、q→2.1 翻起露喷嘴。
  - sliding_nozzle_cover：PRISMATIC axis=(0,1,0)，origin=(0,SLIDE_ORIGIN_Y,HOOD_Z1)，body `slide_rail_0/1` ↔ cover `cover_plate`（captured-slide）；q=0 罩喷嘴、q→0.010 滑开露喷嘴。
- **flame_adjust 接口（可选）**：
  - none：无 joint。
  - flame_height_thumb_wheel：CONTINUOUS axis=(0,0,1)，origin=(0,NOZZLE_Y,ADJUST_Z) 落在喷嘴基部阀台面，`adjust_ring` 内孔套 `nozzle_collar`（captured-sleeve）。
- **mating policy**：所有 hinge 是 pin-in-barrel captured-pin、slide 是 rail-on-plate captured-slide、wheel/ring 是 axle/sleeve captured —— 几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（见各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：spark_wheel q=0、fuel_lever q=0（撬杆抬起前）、piezo_button q=0（未压）、flip_cap q=0 闭合、nozzle_cover q=0 罩住、flame_adjust q=0。所有盖闭合姿态 lower=0。
- **互斥 / 可选 / 派生**：ignition 二候选互斥（一次只一种点火）；cap 三候选互斥（一次只一种盖，含无盖）；flame_adjust 二候选；piezo 分支不发射 hood_cheeks/spark_wheel/fuel_lever（拓扑收缩，见 §9）。

## 每槽位 Module Emits / Interfaces

### Slot A / body_shape（以 stadium 为例；round/rectangular 仅换 profile helper）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（visual: `reservoir_shell` 中空壳 + `valve_deck` 阀台 + `flame_nozzle`/`nozzle_collar` + `flint_tube` + `hood_band` 罩 + `hood_cheeks` 颊板；rect 额外 `vent_slot_{i}`）| parent `_reservoir_shell` L78-86 + 装配 L166-206 / rect vent L251-261 |
| internal joints | 无（body 是 root，内部无活动件）| — |
| upstream interface | root（坐地，无父）| — |
| downstream interface | 滚轮颊板/阀台/喷嘴基部/hood 顶（供 ignition / cap / flame_adjust 接入）| parent L191-206 |

### Slot B / ignition_mechanism — flint_spark_wheel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spark_wheel`（`wheel_knurl` KnobGeometry + `wheel_axle`）+ `fuel_lever`（`lever_pad`+`lever_fork`+`lever_boss`+`lever_pin`）| parent L208-227 / L239-261 |
| internal joints | `body_to_spark_wheel` CONTINUOUS axis=(1,0,0) origin=(0,WHEEL_Y,WHEEL_Z)；`body_to_fuel_lever` REVOLUTE axis=(-1,0,0) origin=LEVER_PIVOT，lower=-0.21/upper=0 | parent L228-236 / L262-272 |
| upstream interface | `wheel_axle` 落入 body `hood_cheeks`（captured-pin）；`lever_pin` 落入 hood 内（captured-pin）| parent L287-302 |

### Slot B / ignition_mechanism — piezo_push_button
| emits | 描述 | 来源 |
|---|---|---|
| parts | `piezo_button`（`button_cap` domed + `button_stem`）；body 改加 `button_guide` 导柱 + `piezo_electrode` + hood 顶板 | piezo L253-280 / body L216-231 / hood plate L141-157 |
| internal joints | `body_to_piezo_button` PRISMATIC axis=(0,0,-1) origin=(0,0,HOOD_Z1)，lower=0/upper=0.002 | piezo L283-296 |
| upstream interface | `button_stem` 滑过 body `button_guide`（captured-sleeve）；cap 穿 hood 顶板孔 | piezo L311-324 |

### Slot C / cap — flip_top_cap
| emits | 描述 | 来源 |
|---|---|---|
| parts | `flip_top_cap`（`cap_shell` + `cap_barrel` 铰筒 + `cap_grip_{i}` 棱×4）；body 加 `cap_hinge_pin` | flip L364-386 / body L289-295 |
| internal joints | `body_to_flip_cap` REVOLUTE axis=(1,0,0) origin=(0,HINGE_Y,HINGE_Z)，lower=0/upper=2.1 | flip L388-398 |
| upstream interface | `cap_barrel` 套 body `cap_hinge_pin`（captured-pin，穿 hood 壁）| flip L431-439 |

### Slot C / cap — sliding_nozzle_cover
| emits | 描述 | 来源 |
|---|---|---|
| parts | `nozzle_cover`（`cover_plate` stadium 板）；body 加 `slide_rail_0/1` 双轨 | sliding L327-336 / body L246-259 |
| internal joints | `body_to_nozzle_cover` PRISMATIC axis=(0,1,0) origin=(0,SLIDE_ORIGIN_Y,HOOD_Z1)，lower=0/upper=0.010 | sliding L337-349 |
| upstream interface | `cover_plate` 受 body `slide_rail_0/1` 导引（captured-slide）| sliding L246-259 / run_tests |

### Slot D / flame_adjust — flame_height_thumb_wheel
| emits | 描述 | 来源 |
|---|---|---|
| parts | `flame_adjust`（`adjust_ring` 环 + `adjust_tooth_{i}` 齿×16）| adjust L308-330 |
| internal joints | `body_to_flame_adjust` CONTINUOUS axis=(0,0,1) origin=(0,NOZZLE_Y,ADJUST_Z) | adjust L331-340 |
| upstream interface | `adjust_ring` 内孔套 body `nozzle_collar`（captured-sleeve）| adjust L496-498 |

### inline 视觉（非 multiplicity 复制；按 module 各自循环）
| emits | 描述 | 来源 |
|---|---|---|
| rect vent_slot | `vent_slot_{i}` ×4 通气孔暗插，`for i in range(4)` | rect L251-261 |
| cap_grip | `cap_grip_{i}` ×4 防滑棱，`for i in range(4)` | flip L378-386 |
| adjust_tooth | `adjust_tooth_{i}` ×16 滚花齿，`for i in range(16)` | adjust L319-330 |
| 说明 | 均为 module-local 装饰视觉（Rule 1，inline 到承载 part），齿数/孔数固定，**非模板级 multiplicity 轴**（见 §8）| — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_shape | enum | stadium_oval / round_cylindrical / rectangular_slab | stadium_oval | choice | 由 deterministic procedural sampler 选；决定 reservoir/deck/hood mesh helper | module table |
| ignition_mechanism | enum | flint_spark_wheel / piezo_push_button | flint_spark_wheel | choice | sampler 选；主机构（互斥），决定 part 数/joint 拓扑 | module table |
| cap | enum | open_hood / flip_top_cap / sliding_nozzle_cover | open_hood | choice | sampler 选；含空盖 open_hood（互斥）| module table |
| flame_adjust | enum | none / flame_height_thumb_wheel | none | choice | sampler 选；含空机构 none | module table |
| palette_style | enum | royal_blue_chrome / black_chrome / safety_red_piezo / translucent_amber / gunmetal_grey | royal_blue_chrome | palette | palette only，**不计入 slot_choice**；逐 seed 采样 | 各样本材质 |
| body_len_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 BODY_LEN（Y 长轴），clamp；hood/deck profile 等比跟随 | resolve clamp |
| body_dep_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 BODY_DEP（X 短轴），clamp；round 时锁定 = body_len_scale（保圆，见 equation 行）| resolve clamp |
| body_height_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放 BODY_H → hood Z / 各机构 Z 派生跟随，clamp | resolve clamp |
| lid_open_angle_scale | float | [0.85, 1.05] | 1.0 | conditional | 仅 flip_top_cap 有效；缩放 REVOLUTE 盖 upper（≤π·0.7 防过翻撞滚轮）| resolve clamp |
| slide_travel_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 sliding_nozzle_cover 有效；缩放 PRISMATIC upper（≥露喷嘴所需行程，≤轨长）| resolve clamp |
| (—) | constraint | — | — | equation | round_cylindrical 时 `body_dep_scale = body_len_scale`（圆截面 X=Y 保形，不独立采样）| 接口（round profile）|
| (—) | constraint | — | — | inequality | hood/机构 Z 链：`HOOD_Z1·body_height_scale + 机构高 ≤ 整机高上限`；wheel/button 顶须为最高点（验滚轮/按钮露 hood）| 接口 / clearance |
| (—) | constraint | — | — | conditional | ignition=piezo_push_button 时不发射 hood_cheeks/spark_wheel/fuel_lever，hood_band 用带顶板变体；cap 仍可叠（flip/sliding 罩按钮上方喷嘴）| §8 / §9 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 body_shape / ignition / cap / flame_adjust 的拓扑**。

## Multiplicity / Copy Logic

- **无核心复制逻辑**：打火机核心结构由固定 named slots（body_shape + ignition_mechanism + cap + flame_adjust）表达，不暴露 `*_count`，也不通过循环复制模板级 visual/part/joint。
- 样本中存在的 `for i in range(N)` 循环——rect `vent_slot_{i}`（4 孔）、flip `cap_grip_{i}`（4 棱）、adjust `adjust_tooth_{i}`（16 齿）——均为 **module-local 固定装饰视觉**（Rule 1，inline 到承载 part，齿/孔/棱数为该 module 的固定细节），**不是模板级 multiplicity 轴**，不编入 `slot_choices`、不随 seed 改变复制数。source map「格子覆盖」亦确认无核心 multiplicity。

## 拓扑多样性审计

总组合数：body_shape(3) × ignition_mechanism(2) × cap(3) × flame_adjust(2) = **36**。

仅 ignition(2) × cap(3) × flame_adjust(2) = **12**（joint 拓扑维度：CONTINUOUS+REVOLUTE / PRISMATIC 点火 × 无盖 / REVOLUTE 盖 / PRISMATIC 盖 × 无调节 / CONTINUOUS 调节）≥ 10 已稳过门控；叠 body_shape(3) → 36 充裕。

理由：ignition × cap × flame_adjust 提供真正的 joint 拓扑差异（点火 2 类含 1/2 个 joint 与 CONTINUOUS/REVOLUTE/PRISMATIC 不同类型；盖 3 类含无/REVOLUTE/PRISMATIC；调节 2 类含无/CONTINUOUS = 2×3×2=12 种 joint-topology 等价类），叠 body_shape(3) 后总 36 distinct。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 四个 named slot（body_shape / ignition_mechanism / cap / flame_adjust），经兼容矩阵合法化（主要解析 piezo 分支的部件收缩 + flip/sliding 盖在 piezo 上的座位调整），再 uniform 各连续 scale，再 `rng.choice` palette_style。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：见 §参数表的 body_len_scale / body_dep_scale（round 时 equation 锁 = body_len_scale）/ body_height_scale / lid_open_angle_scale（conditional@flip）/ slide_travel_scale（conditional@sliding）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（解析 conditional：piezo 收缩部件、cap 决定盖件、flame_adjust 决定调节件）→ 采 independent body_len/height scale → 派生（round 锁 body_dep=body_len；hood/deck/各机构 Z 随 body_height 等比）→ 用 hood-Z 链 inequality 投影（保滚轮/按钮为最高点、盖行程足够露喷嘴）→ 解析 conditional 角度/行程范围（仅对应盖存在时）。跨部件依赖（round X=Y、hood Z 链、盖行程 vs 轨长）显式落在 §7，在 `resolve_config` 内求解。这些 scale 不破坏 wheel/lever/button origin、captured-pin/slide/sleeve 接口或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 四 named slot（经兼容矩阵），再 uniform 各 scale，再 `rng.choice` palette | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | (1) **ignition=piezo_push_button**：不发射 `hood_cheeks`/`spark_wheel`/`fuel_lever`，hood_band 用带顶板变体（stem 孔）+ `button_guide`/`piezo_electrode`；flint=保留滚轮+撬杆+颊板。两分支互斥，sampler 据此切换 body helper 子集。 (2) **cap × ignition**：flip_top_cap / sliding_nozzle_cover 罩的是喷嘴区，与 flint（滚轮在后）/ piezo（按钮在顶）均不冲突 → 允许任意 cap × 任意 ignition；但 piezo 顶按钮高度须低于盖闭合内净空（clamp button travel / 盖 Z），否则 gate 为 open_hood。 (3) **flame_adjust × *）**：调节环在喷嘴基部，与任意 ignition / cap 正交 → 允许全组合。 (4) **body_shape 与机构正交**（stadium/round/rect 均可配任意 ignition/cap/adjust）。 | 无 floating / collision / 盖撞滚轮 / piezo 顶按钮顶盖 / 调节环穿喷嘴 / 滑盖行程不足露喷嘴 |
| controlled local variation | 5 个 clamped scale（body_len、body_dep(round=len)、body_height、lid_open_angle@flip、slide_travel@sliding），每 build 统一；lid_open_angle / slide_travel 为 conditional | 比例变化不破坏 wheel/lever/button/cap origin、captured 接口、盖闭合罩喷嘴、滚轮/按钮露顶、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐机构 QC（点火/盖/调节 joint 类型与 axis）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_shape | 3 | yes | yes | stadium 为 parent 基线，round/rect 为 fork（mesh-helper 维度）|
| ignition_mechanism | 2 | yes | no | 燧石 vs 电子已是类别真实结构上限（§4 说明，非样本池不足）；主机构槽 |
| cap | 3 | yes | yes | 无盖 / REVOLUTE 翻盖 / PRISMATIC 滑盖（互斥可选）|
| flame_adjust | 2 | yes | no | 无 / CONTINUOUS 调节轮（可选；真实形态二选一）|

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名（`(body_shape, …)`, `(ignition_mechanism, …)`, `(cap, …)`, `(flame_adjust, …)` 四元组），与 build choices 一致
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling；seed=0 不特殊
- `resolve_config` 校验 enum 合法、各 scale clamp 到声明范围；round 时 body_dep_scale=body_len_scale；lid_open_angle / slide_travel 为 conditional 随 cap 解析；hood-Z 链 inequality 在 resolve 内投影
- compatibility matrix / gating 阻止非法组合（piezo 分支收缩 hood_cheeks/spark_wheel/fuel_lever 并用顶板 hood；盖闭合内净空不足时 cap 降级 open_hood）
- 连续 scale clamp 后不破坏 wheel/lever/button/cap/adjust origin、captured-pin/slide/sleeve 接口、盖闭合罩喷嘴、滚轮/按钮露顶
- 关键 joint：flint `body_to_spark_wheel` CONTINUOUS axis≈(1,0,0)（abs(axis[0])>0.99）+ `body_to_fuel_lever` REVOLUTE axis≈(-1,0,0) lower=-0.21；piezo `body_to_piezo_button` PRISMATIC axis≈(0,0,-1) upper≈0.002；flip `body_to_flip_cap` REVOLUTE axis≈(1,0,0) upper≈2.1；sliding `body_to_nozzle_cover` PRISMATIC axis≈(0,1,0) upper≈0.010；adjust `body_to_flame_adjust` CONTINUOUS axis≈(0,0,1)
- captured-pin / slide / sleeve：element-scoped `allow_overlap`（`wheel_axle`↔`hood_cheeks`/`hood_band`；`lever_pin`↔`hood_cheeks`/`hood_band`；`button_stem`↔`button_guide`；`cap_barrel`↔`cap_hinge_pin`/`hood_band`；`adjust_ring`↔`nozzle_collar`；rect `vent_slot_{i}`↔`hood_band`），照搬各样本 run_tests 的 allow_overlap 段
- inline 装饰（vent_slot/cap_grip/adjust_tooth）遵循 `*_{i}` 命名 + module-local 固定数量 + Rule 1（无独立 joint），不编入 slot_choice
- grandfather：所有 hinge/slide/sleeve captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- piezo_push_button 分支仍发射 `spark_wheel` / `fuel_lever` / `hood_cheeks` → 电子打火机不应有燧石滚轮撬杆；必须按兼容矩阵收缩部件、用带顶板 hood。
- 把 body_shape（stadium/round/rect）当独立串联 slot 或给它发额外 joint → 它只是 reservoir/deck/hood 的 mesh profile 维度，不改拓扑。
- flip_top_cap / sliding_nozzle_cover rest pose 设成张开而非 q=0 闭合 → current-pose 与 viewer 目检不符（所有盖样本闭合姿态 lower=0）。
- round_cylindrical 时 body_dep_scale 与 body_len_scale 各自独立采样 → 圆截面退化为椭圆，破坏 round 身份；必须 equation 锁 X=Y。
- hinge/slide/sleeve origin 放在 body 中心或任意点而非真实滚轮轴心 / 铰线 / 轨面 / 喷嘴基部 → `fail_if_articulation_origin_far_from_geometry`（0.020）FAIL。
- 给 captured-pin / captured-slide / captured-sleeve 补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 盖闭合后撞滚轮 / piezo 顶按钮顶穿盖 / 滑盖行程不足露喷嘴 → §7 hood-Z 链 / 盖行程不等式 FAIL；须 clamp 角度/行程或 gate open_hood。
- 把 `vent_slot_{i}` / `cap_grip_{i}` / `adjust_tooth_{i}` 齿孔数当模板级 multiplicity 编进 slot_choice / 随 seed 改 → 它们是 module-local 固定装饰（Rule 1），非结构 multiplicity 轴。
- 把连续尺寸 / 颜色 / 材质（palette_style / body scale）当新 candidate 塞进 slot → 不是结构差异。
- 把 zippo 式金属翻盖 + insert + cam 结构混入 → 出类，本类是一次性塑料壳 + 可选盖，盖为附加件而非永久翻盖（见相邻边界）。

## 与相邻类别的边界

- 不该混入：**zippo_lighter（既有模板）**——防风金属壳翻盖打火机（永久翻盖 lid + insert 燃料仓 + cam lever，金属方壳）。本类是一次性塑料壳打火机，盖（flip/sliding）为可选附加件、点火含 piezo 电子分支、无 insert 燃料仓拆分；二者主结构家族不同，须保持各自身份。
- 不该混入：**长杆点火枪 / 蜡烛点火器（utility / candle lighter）**——长柄扳机机构，非口袋直立壳体。
- 不该混入：**煤气灶点火器 / 工业点火枪**——非口袋一次性形态，主运动 spine 不同。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) body_shape 建模为 mesh-helper 维度（非串联 slot、不发 joint）；(2) ignition 2 候选（燧石/电子）作类别真实上限是否接受（主机构槽降到 2，§4 已说明）；(3) piezo 分支收缩 hood_cheeks/spark_wheel/fuel_lever + 顶板 hood 的兼容矩阵策略；(4) cap × piezo（顶按钮 vs 盖闭合净空）的 gate/clamp 策略；(5) Topology target 36<300 的说明是否接受（本小类真实结构上限）；(6) vent_slot/cap_grip/adjust_tooth 固定齿孔数判为 module-local 装饰（非 multiplicity）是否符合审计期望；(7) palette_style 5 档（royal_blue_chrome/black_chrome/safety_red_piezo/translucent_amber/gunmetal_grey）是否合适）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：`_reservoir_shell`/`_valve_deck`/`_hood_band`（按 body_shape 在 slot2D/circle/rect 间切换 profile）、`_hood_cheeks`（仅 flint 分支）、`_lever_pad`/`_lever_fork`（flint）、`_flip_cap_shell`/`_grip_ridge`（flip）、`_nozzle_cover_plate`（sliding）、`_adjust_ring`/`_adjust_tooth`（flame_adjust）。spark_wheel knurl 与 flame_adjust 均可复用 KnobGeometry/CONTINUOUS idiom（参见 zippo_lighter.py 的 wheel 工厂模式）。
- captured 接口 allow_overlap：`run_lighter_tests` 里逐 module 补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（parent L287-302 wheel/lever pin；piezo L313-317 stem/guide；flip L432-439 barrel/pin；rect L341-345 vent_slot；adjust L496-498 ring/collar）。仿 zippo 的 `_allow_if_present` 守护式 helper（按 part/elem 存在性条件性声明 overlap），适配 piezo 分支无 hood_cheeks 的情形。
- conditional 范围解析顺序：先采 body_shape / ignition / cap / flame_adjust → 解析 piezo 部件收缩 + cap 盖件 + 承载 part → 采 body_len/height independent scale → 派生（round 锁 body_dep=len；hood/各机构 Z 随 body_height）→ 投影 hood-Z 链 inequality → 解析 lid_open_angle（仅 flip）/ slide_travel（仅 sliding）conditional 范围。
- piezo 分支：body 工厂需按 ignition 选择发射不同 hood_band 变体（带顶板 vs 带后切口）与是否发射 hood_cheeks/spark_wheel/fuel_lever，建议 body helper 接 `ignition` 参数或拆 `_build_body_flint` / `_build_body_piezo` 两条装配路径（参见 zippo 的 BODY/INSERT 工厂分发表）。
- 参考模板：`agent/templates/zippo_lighter.py`（同小类近邻：mixed/parallel-children 打火机，body/lid/wheel/cam 工厂分发 + `slot_choices_for_seed` + captured-pin allow_overlap + KnobGeometry 滚轮 idiom + 互斥 cam gate，本类可同构改编，但须保持一次性塑料壳 + piezo 分支 + 可选盖的身份，不复制其永久翻盖/insert 结构）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C / D（parent 基线）| stadium + flint + open_hood + none | rec_model-a-classic-...c45ce5f7 | `_reservoir_shell` L78-86 / `_valve_deck` L89-95 / `_hood_band` L98-122 / `_hood_cheeks` L125-131 / spark_wheel+CONTINUOUS L208-236 / fuel_lever+REVOLUTE L239-272 / allow_overlap L287-302 | stadium footprint + flint 主机构基线 + 共享 hood/wheel/lever helper + captured-pin 范式 |
| S2 | A | round_cylindrical | rec_variant-body-shape-round-cylindrical-...099fd912 | `_round_profile` L79-81 / `_reservoir_shell` L85-90 / `_hood_band` L101-129 | 圆截面 mesh helper（part 树/joint 不变，X=Y 保形 + AXLE_LEN 适配）|
| S3 | A | rectangular_slab | rec_variant-body-shape-rectangular-slab-...d28014ae | `_reservoir_shell` L84-93 / `_hood_band` L123-143 / `_hood_vent_cuts` L106-120 / `_vent_slot_geometry` L188-194 / vent loop L251-261 | 方角板 mesh helper + vent_slot_{i} inline 装饰循环源 |
| S4 | B | piezo_push_button | rec_variant-ignition-mechanism-piezo-push-button-...62f5cdf2 | hood plate L141-157 / `piezo_electrode` L216-222 / `button_guide` L224-231 / piezo_button L253-280 / PRISMATIC L283-296 / allow_overlap L313-317 | 电子压电点火（PRISMATIC 直压 + 部件收缩 + 顶板 hood + 导柱）|
| S5 | C | flip_top_cap | rec_variant-cap-flip-top-cap-...47195100 | `_flip_cap_shell` L184-228 / `_grip_ridge` L231-235 / `cap_hinge_pin` L289-295 / flip_top_cap L364-386 / REVOLUTE L388-398 / allow_overlap L432-439 | 翻盖（REVOLUTE +X + captured-pin + cap_grip_{i} inline）|
| S6 | C | sliding_nozzle_cover | rec_variant-cap-sliding-nozzle-cover-...b701f9ec | `_nozzle_cover_plate` L173-... / slide_rail_0/1 L246-259 / nozzle_cover L327-336 / PRISMATIC L337-349 | 滑盖（PRISMATIC +Y + rail captured-slide）|
| S7 | D | flame_height_thumb_wheel | rec_variant-flame-adjust-flame-height-thumb-wheel-...fe4840b8 | `_adjust_ring` L170-177 / `_adjust_tooth` L180-184 / flame_adjust L308-330 / CONTINUOUS L331-340 / allow_overlap L496-498 | 火焰调节轮（CONTINUOUS Z 环抱喷嘴 + adjust_tooth_{i} inline）|
