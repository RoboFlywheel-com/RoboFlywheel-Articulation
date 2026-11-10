# paint_roller (hand paint roller: spinning cover on a wire/shank frame) — Modular Spec

> 来源小类：`picture/Handtools/Paint roller`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Handtools__Paint_roller.md`。
> **"Paint roller" 在此 = 手用油漆滚筒（hand paint roller）：一只 cream/foam 圆筒 `roller_cover` 套在钢丝 / 钢杆 `handle_frame` 的轴上自由旋转，handle 端有用户握把。不是 lint roller（除尘滚筒）、不是擀面杖 rolling pin（无独立旋转 cover / 无握把 crank）、不是 paint brush（无滚筒）。**
> 结构家族 = 单旋转滚筒手具：`handle_frame`（root：grip + 钢丝 shank/cage，捕捉轴）+ 单一 `roller_cover`（moving child），二者由 `frame_to_roller` **CONTINUOUS** 关节（axis +X，origin 在轴线滚筒中心）连接 —— 这是**全候选共享的唯一活动机构**（滚筒自由旋转）。
>
> **同步状态**：本 spec 引用的 9 个 5 星样本（1 个 parent + 8 个 fork 槽位变体）**已同步进本仓库 `data/records/<id>/`，rating=5**。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一逐行读完整核对）。引用以 part / joint / helper **名字** 为准（`handle_frame`/`roller_cover` part；`frame_to_roller` joint；`_roller_cover_shape`/`_core_tube_shape`/`_frame_wire_path`/`_frame_wire_mesh`/`_handle_shape`/`_cage_spoke_path`/`_hub_cap_shape`/`_straight_shank_shape`/`_collar_shape`/`_finger_ridge_mesh`/`_grip_ring_shape`/`_thread_turn_points`/`_nap_ring_mesh`/`_lattice_rib_shape`/`_lattice_hoop_shape`/`_end_spider_shape` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `paint_roller` |
| template path | `agent/templates/Handtools_Paint_roller.py` |
| test path (optional) | `tests/agent/test_paint_roller_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 root `handle_frame` + 单一 moving child `roller_cover`；三个可替换层 cage_shank / grip / cover 各自决定 root 或 child 的 part 树与 mesh，唯一跨件 joint 是共享的 `frame_to_roller` CONTINUOUS）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9（1 parent + 8 fork 槽位变体；均 converged、compile success、各保留 `frame_to_roller` CONTINUOUS 非 fixed joint、workbench-only，rating=5）|
| read_count | 9（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests + allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 9/9 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **共享基线拓扑（全部 9 个样本）**：`handle_frame`（root，坐 grip + 钢丝 / 钢杆 shank，X 轴线 AXLE_Z=0，roller 居中 x=0）+ `roller_cover`（单一 moving child）。`frame_to_roller` **CONTINUOUS** axis=(1,0,0) origin=(0,0,AXLE_Z) 是**所有候选共享的唯一活动机构**（roller 绕长轴 +X 自由旋转）。所有样本的 run_tests 都断言 `joint_type==CONTINUOUS`、`abs(axis[0])>0.99`、quarter-spin 后 roller 仍居中（parent L335-348）。journal 捕捉：轴 / shank 嵌进 `roller_core` bore（`allow_overlap(wire_frame/shank/wire_axle, roller_core)` + `expect_overlap(axes="x", min_overlap≈0.15)`，parent L228-249）—— **唯一例外是 perforated_lattice_core**：删掉 `roller_core`，journal 改到 2 个 `end_spider_{i}` hub bore（`allow_overlap(wire_frame, end_spider_{i})`，perf L344-366）。
- **Slot A cage / frame shank 轴**：是 root part 内 visual 树 / 钢丝 path 的真正结构变化（轴线如何引到 grip、是否多 hub+spoke 阵列）。
  - z_crank_wire（parent）：单一 `wire_frame`（一根 `tube_from_spline_points`，`_frame_wire_path` 从远端 stub→穿 roller→+X 端 90° 下弯 crank→插进 grip），grip 在轴线下方 FRAME_DROP=0.055（parent L120-146, L177-187）。
  - birdcage_spider：`wire_axle`（直轴）+ `handle_stem`（从 hub 下弯到 grip）+ `hub_cap`（带轴 bore 的端盖）+ `cage_spoke_{i}`（`for i in range(N_SPOKES=6)`，`_cage_spoke_path` helper，等角 2π/N，从 hub 辐射到 roller OD 形成 retention cage）（birdcage L137-274）。**+ hub+6 spoke 阵列，journal/retention 在 +X 端 hub**。
  - straight_inline_shank：`shank`（单 `CylinderGeometry` 直杆，无 Z drop）+ `collar`（zinc ferrule 接头）+ grip 与 roller **同轴**（HANDLE_Z=AXLE_Z=0，无 crank）（straight L115-136, L186-201）；roller 端另加 `end_cap_{i}`（`for i in range(2)`）—— 这是 cover 子件，归 Slot C 的 N=2 装饰，不属 cage 轴。
- **Slot B grip 轴**：是 grip part visual 树的真正结构变化（profile 形态 + 是否多 ridge / ring / thread 阵列 + 是否多 socket 内腔）。
  - smooth_molded_grip（parent / 多数变体）：`handle_grip`（`_handle_shape` 单一 revolve barrel polyline）（parent L149-169）。
  - ribbed_scalloped_grip：`handle_grip`（scalloped peak/valley profile，`_handle_shape` 改写）+ `finger_ridge_{i}`（`for i in range(NUM_FINGER_RIDGES=5)`，`TorusGeometry` 环，`_finger_ridge_mesh` helper，等距 X，inline visual）（ribbed L169-227, L250-255）。
  - hollow_tube_sleeve：`handle_tube`（stepped-bore 直筒：宽 entry bore + 紧 socket bore，`_handle_tube_shape`，开口 through-tube）+ `grip_ring_{i}`（`for i in range(GRIP_RING_COUNT=6)`，`_grip_ring_shape` 环箍，等距 X，inline visual）（tube L167-265）。grip 名字从 `handle_grip` 变 `handle_tube`。
  - pole_socket_grip：`handle_grip`（flat butt face + 钻 extension-pole bore，`_handle_shape` + `cut(bore_cutter)`）+ `thread_turn_{i}`（`for i in range(NUM_THREAD_TURNS=6)`，螺旋 `tube_from_spline_points` via `_thread_turn_points`，inline visual）（pole L164-270）。
- **Slot C roller cover 轴**：是 child part（roller_cover）内 part 树 / mesh 拓扑的真正结构变化（cover shell 形态 + core 是否被 cage 替换 + journal 承载面在哪）。
  - smooth_foam_cylinder（parent / 多数变体）：`roller_cover`（cq tube w/ bore，`_roller_cover_shape`）+ `roller_core`（实心 sleeve，journal bore，`_core_tube_shape`）（parent L72-117, L190-200）。开口中空两端。
  - napped_pile_fabric：`roller_cover` + `roller_core` + `nap_ring_{i}`（`for i in range(NAP_RINGS=6)`，`MeshGeometry` 径向位移外顶点模拟 pile 纤维，`_nap_ring_mesh` helper，等距 X 段，nap 留 NAP_END_MARGIN 不到端口）（nap L182-311）。
  - feathered_taper_edge：`roller_cover`（`LatheGeometry` 中段圆柱→两端 feathered cone 尖 + `boolean_difference` 全长窄 bore + 中段宽 bore，`_roller_cover_shape`）+ `roller_core`（`CylinderGeometry`，更短，因尖端实心）（taper L82-147, L221-230）。edge/trim roller 形态。
  - perforated_lattice_core：`roller_cover`（同 smooth 的 cq tube）+ **删 `roller_core`** → `lattice_rib_{i}`（`for i in range(N_RIBS=8)`，等角，纵向 rod）+ `lattice_hoop_{i}`（`for i in range(N_HOOPS=5)`，等距 X，环箍）+ `end_spider_{i}`（`for i in range(2)`，hub+arm，**journal bore 捕轴**，`_end_spider_shape`）（perf L71-92, L134-204, L282-316）。开口端可见 cage 框架，journal 从 roller_core 迁移到 end_spider hub。

## 核心身份

一只**手用油漆滚筒**（hand paint roller）：一只 cream/foam 圆筒 `roller_cover`（~0.18m 长、~38mm 直径、开口中空两端，内有 hard core 或 lattice cage）套在一根钢丝 / 钢杆 `handle_frame`（root）的轴上**自由旋转**；frame 在轴线上引一根钢丝穿过 roller core bore（或 end-spider hub），到 handle 端用 **90° crank 下弯到偏置 grip**（z_crank / birdcage）或**同轴直引到 inline grip**（straight），grip 是 coral/pink 注塑握把（smooth barrel / ribbed scalloped / hollow tube sleeve / extension-pole socket）。默认成熟域：cage_shank(3) × grip(4) × cover(4) 笛卡尔积的小型手持滚筒。活动语义 = **roller_cover 绕长轴 +X 自由旋转**（核心 `frame_to_roller` CONTINUOUS，全候选共享，是唯一活动 joint）。

不该混入：
- **lint roller / 粘毛除尘滚筒**——虽同为旋转 cover + crank handle，但 cover 是粘性纸卷 / 短粗，且无 paint roller 的 foam/nap cover + 长 ~0.18m 比例 + 油漆作业身份；形态相邻但归类不同（如需可作单独 slug）。
- **擀面杖 / rolling pin**——cover/cylinder 在两端**带把手**绕自身轴转，但没有偏置 crank handle、没有 foam/nap cover、不是 root-grounded frame + single spinning child 的手具机构（主运动 spine 不同：rolling pin 是双端把手轴 = root，cylinder 中段是 root 本体不是独立旋转 child）。
- **paint brush / 油漆刷**——无滚筒、无旋转机构，纯刚性刷柄 + 刷毛。
- **bench roller / conveyor roller / 工业辊**——非手持、无 grip、无 crank，固定座辊轮。

## 槽位 + 候选模块表

> **建模注记**：三个 slot 都改真实结构（不是纯 mesh 维度）。`cage_shank`（Slot A）改 root `handle_frame` 的钢丝 path / hub-spoke 阵列 + grip 偏置方式（crank 下弯 vs 同轴），是 root part visual 树拓扑变化。`grip`（Slot B）改 grip part 的 profile + ridge/ring/thread 阵列 + 是否多 socket 内腔，是 grip visual 树拓扑变化（hollow_tube 还把 part visual 名从 `handle_grip` 换 `handle_tube`）。`cover`（Slot C）改 child `roller_cover` 的 part 树 / mesh + **journal 承载面**（smooth/nap/taper 走 roller_core 中段 bore；perforated_lattice **删 roller_core**、journal 迁到 end_spider hub）。**Slot C × Slot A 在 journal 承载面上有真实跨槽接口耦合**，见 §9 兼容矩阵。

### Slot A：cage / frame shank（`handle_frame` root：钢丝 / 钢杆从远端 stub 穿 roller bore 引到 grip —— 决定轴线引法、grip 偏置、是否多 hub-spoke 阵列）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / 结构特征 |
|---|---|---|---|---|
| z_crank_wire（基线）| rec_..._pain_..._ec6d7dba（parent）| `_frame_wire_path` L120-134 + `_frame_wire_mesh` L137-146 + `wire_frame` visual L183-187 + `_handle_shape`(@HANDLE_Z) L149-169 | eligible if compatible | 经典 bent 钢丝：单一 `wire_frame`（一根 swept tube）从远端 stub 穿 roller，+X 端 90° crank 下弯 FRAME_DROP=0.055 到偏置 grip（grip 在轴线下方）；grip 与 wire 一刚体（`expect_contact(wire_frame, handle_grip)` parent L325-332）|
| birdcage_spider | rec_paint_roller_var_cage_birdcage | `_axle_wire_path` L137-146 + `_handle_stem_path` L149-158 + `_cage_spoke_path` L161-184 + `_hub_cap_shape` L187-202 + 装配 L236-274（`wire_axle`/`handle_stem`/`hub_cap`/`cage_spoke_{i}`×6）| eligible if compatible | 直轴 `wire_axle` + `handle_stem`（hub 下弯到 grip）+ `hub_cap`（带轴 bore 端盖）+ **birdcage retention cage** `cage_spoke_{i}`（`for i in range(N_SPOKES=6)`，等角辐射，seat 到 roller OD 端面）；hub 在 +X 端、holds cover on axle（spoke↔roller_cover `allow_overlap` birdcage L328-338）|
| straight_inline_shank | rec_paint_roller_var_cage_straight | `_straight_shank_shape` L115-124（单 `CylinderGeometry`）+ `_collar_shape` L127-136（zinc ferrule）+ `_handle_shape`(@AXLE_Z) L139-158 + 装配 L186-201 | eligible if compatible | inline 直杆：`shank`（单 cylinder，**无 Z drop**，shank z_span<0.010 straight L286-293）→ `collar`（zinc 接头）→ grip 与 roller **同轴**（HANDLE_Z=AXLE_Z=0，handle_center_z≈0 straight L295-303）；shank↔collar↔grip 链式 `expect_contact`（straight L316-331）|

### Slot B：grip / handle（`handle_frame` 上的握把件 —— 决定 grip part 的 profile + ridge/ring/thread 阵列 + 是否多 socket 内腔）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / 结构特征 |
|---|---|---|---|---|
| smooth_molded_grip（基线）| rec_..._pain_..._ec6d7dba（parent）| `_handle_shape` L149-169 + `handle_grip` visual L178-182 | eligible if compatible | 平整 barrel-tapered 注塑握把：单一 `handle_grip`（一段 revolve barrel polyline，collar neck→belly→rounded toe），wire socket 插进 collar neck；无阵列子件 |
| ribbed_scalloped_grip | rec_paint_roller_var_grip_ribbed | `_handle_shape`(scalloped) L169-202 + `_ridge_x_position` L205-207 + `_finger_ridge_mesh` L210-227 + 装配 L236-255（`handle_grip` + `finger_ridge_{i}`×5）| eligible if compatible | 人体工学握把：peak/valley scalloped revolved body + `finger_ridge_{i}`（`for i in range(5)`，`TorusGeometry` 环绕 handle，等距 X 站位，凸出 valley 表面）；ridge 是 inline 非移动 visual（无独立 joint）|
| hollow_tube_sleeve | rec_paint_roller_var_grip_tube | `_handle_tube_shape` L167-216（stepped bore）+ `_grip_ring_shape` L219-232 + 装配 L240-265（`handle_tube` + `grip_ring_{i}`×6）| eligible if compatible | 开口管套握把：`handle_tube`（直筒 + **stepped bore**：宽 entry bore 可见环隙 + 紧 socket bore press-fit + 远端 open through-tube）+ `grip_ring_{i}`（`for i in range(6)`，环箍 grip texture，等距 X，press 进 tube 壁）；**grip part visual 名 = `handle_tube`（非 handle_grip）**；wire shank `expect_overlap(wire_frame, handle_tube, min=0.020)`（tube L424-432）|
| pole_socket_grip | rec_paint_roller_var_grip_pole | `_handle_shape`(flat butt+bore) L164-207 + `_thread_turn_points` L210-233 + 装配 L242-270（`handle_grip` + `thread_turn_{i}`×6）| eligible if compatible | 延长杆接口握把：`handle_grip`(butt 端 flat face + 钻 BORE_R=0.008 / BORE_DEPTH=0.022 female bore) + `thread_turn_{i}`（`for i in range(6)`，helical `tube_from_spline_points` 内螺纹，THREAD_PITCH 等距，contact bore 壁 pole L443-450）；socket boss 加宽以容 bore（pole L423-427）|

### Slot C：roller cover（`roller_cover` moving child —— 决定 cover shell 形态 + core 是否被 cage 替换 + journal 承载面）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 part / journal / 结构特征 |
|---|---|---|---|---|
| smooth_foam_cylinder（基线）| rec_..._pain_..._ec6d7dba（parent）| `_roller_cover_shape` L72-93 + `_core_tube_shape` L96-117 + 装配 L190-200 | eligible if compatible | 平整中空 foam 圆筒：`roller_cover`（cq tube + 真 bore，开口中空两端）+ `roller_core`（实心 sleeve，外壁 contact cover bore、内 bore = journal 捕轴）；**journal 在 roller_core 中段 bore**（基线，与所有 cage_shank 兼容）|
| napped_pile_fabric | rec_paint_roller_var_cover_nap | `_roller_cover_shape` L82-103 + `_core_tube_shape` L106-127 + `_nap_ring_mesh` L182-270 + 装配 L291-311（`roller_cover`/`roller_core`/`nap_ring_{i}`×6）| eligible if compatible | 绒毛 pile fabric cover：smooth shell + core，外加 `nap_ring_{i}`（`for i in range(NAP_RINGS=6)`，`MeshGeometry` 径向位移外顶点模拟 raised fiber，等距 X 段，留 NAP_END_MARGIN 不到端口）；**journal 仍在 roller_core 中段 bore**；nap 是 roller 子件 inline visual |
| feathered_taper_edge | rec_paint_roller_var_cover_taper | `_smoothstep` L77-79 + `_roller_cover_shape`(Lathe) L82-131 + `_core_tube_shape`(Cyl) L134-147 + 装配 L221-230 | eligible if compatible | edge/trim roller：`roller_cover`（`LatheGeometry` 中段圆柱→两端 feathered cone 尖 + `boolean_difference` 全长窄 bore（清尖端）+ 中段宽 bore（坐 core））+ `roller_core`（`CylinderGeometry`，更短，避尖端实心区）；**journal 仍在 roller_core 中段 bore**（taper run_tests min_overlap 放宽到 0.10 taper L271-279）|
| perforated_lattice_core | rec_paint_roller_var_cover_perf | `_lattice_rib_shape` L134-145 + `_lattice_hoop_shape` L148-165 + `_end_spider_shape` L168-204 + 装配 L282-316（`roller_cover`/`lattice_rib_{i}`×8/`lattice_hoop_{i}`×5/`end_spider_{i}`×2，**无 roller_core**）| eligible if compatible | 开笼 lattice core：`roller_cover`（同 smooth cq tube）+ `lattice_rib_{i}`（`for i in range(N_RIBS=8)` 纵 rod，等角）+ `lattice_hoop_{i}`（`for i in range(N_HOOPS=5)` 环箍，等距 X）+ `end_spider_{i}`（`for i in range(2)` hub+arm）；**删 roller_core，journal 迁到 2 个 end_spider hub bore**（`allow_overlap(wire_frame, end_spider_{i})` perf L344-366）；开口端可见 cage |

## 槽位图（slot graph）

pattern: parallel_children（固定 root `handle_frame`；单一 moving child `roller_cover`；cage_shank 改 root 钢丝 path + grip 偏置；grip 改 root 上握把件 profile/阵列；cover 改 child mesh + journal 承载面；唯一跨件 joint = 共享 `frame_to_roller` CONTINUOUS）

```
handle_frame (root, 坐 grip; 由 cage_shank 决定钢丝/钢杆 path + grip 偏置, 由 grip 决定握把件)
  │   visual: [cage_shank 件] + [grip 件] + 钢丝/钢杆 在 AXLE_Z=0 轴线上穿 roller bore
  │
  ├── [cage_shank slot]  (互斥三选一; 都把 frame 钢丝引到 grip, 区别在 path/hub/偏置)
  │     ├─ z_crank_wire         : 单 wire_frame swept tube, +X 端 90° crank 下弯到偏置 grip(HANDLE_Z=-0.055)
  │     ├─ birdcage_spider      : wire_axle 直轴 + handle_stem 下弯 + hub_cap + cage_spoke_{i}×6 retention cage(+X 端 hub)
  │     └─ straight_inline_shank: shank 直杆(无 drop) + collar(zinc) + grip 与 roller 同轴(HANDLE_Z=0)
  │
  ├── [grip slot]  (互斥四选一; 都是 root 上握把件)
  │     ├─ smooth_molded_grip   : handle_grip 单 revolve barrel
  │     ├─ ribbed_scalloped_grip: handle_grip(scalloped) + finger_ridge_{i}×5 (torus 环, inline visual)
  │     ├─ hollow_tube_sleeve   : handle_tube(stepped bore) + grip_ring_{i}×6 (环箍, inline visual)
  │     └─ pole_socket_grip     : handle_grip(flat butt+bore) + thread_turn_{i}×6 (内螺纹 helix, inline visual)
  │
  └── roller_cover (单一 moving child) ──[frame_to_roller: CONTINUOUS axis=(1,0,0), origin=(0,0,AXLE_Z)]  ← 全候选共享唯一活动机构
        │   journal 捕捉: 轴/shank 嵌进承载面(allow_overlap + expect_overlap axes="x")
        │
        └── [cover slot]  (互斥四选一; 都是 roller_cover child 的 mesh/子件)
              ├─ smooth_foam_cylinder  : roller_cover(tube) + roller_core(sleeve, journal bore)         ← journal 在 roller_core 中段
              ├─ napped_pile_fabric    : roller_cover + roller_core + nap_ring_{i}×6                    ← journal 在 roller_core 中段
              ├─ feathered_taper_edge  : roller_cover(Lathe taper) + roller_core(Cyl, 短)                ← journal 在 roller_core 中段
              └─ perforated_lattice_core: roller_cover + lattice_rib_{i}×8 + lattice_hoop_{i}×5 + end_spider_{i}×2  ← 删 roller_core, journal 迁到 end_spider hub
```

接口点位与 joint 语义：
- **frame → roller（全候选共享，唯一跨件 joint）**：mating = roller 中段轴线的 journal 捕捉。**CONTINUOUS** axis=(1,0,0)，origin=(0,0,AXLE_Z=0)（所有样本一致，parent L204-212）；roller 绕 +X 自由旋转无 limit（仅 effort/velocity）。journal 是 captured 过盈（轴在 bore / hub 内）：
  - smooth / nap / taper：`allow_overlap(<frame 钢丝 elem>, roller_core)` + `expect_overlap(axes="x", min_overlap≈0.15)`（taper 放宽 0.10）；钢丝 elem 名随 cage_shank（z_crank=`wire_frame`、birdcage=`wire_axle`、straight=`shank`）。
  - perforated_lattice：**无 roller_core** → `allow_overlap(<frame 钢丝 elem>, end_spider_{i})`（i∈{0,1}）+ `expect_overlap(axes="x", min_overlap≈0.001)` 各 hub（perf L344-366）。
- **cage_shank 接口（互斥）**：所有 cage_shank 把 frame 钢丝从远端 stub 引到 grip socket，钢丝↔grip 一刚体（`expect_contact(<钢丝 elem>, <grip elem>)`，parent L325-332 / birdcage `handle_stem`↔`handle_grip` L455-462 / straight `shank`↔`collar`↔`handle_grip` L316-331）。
  - z_crank_wire：单 swept tube，+X 端 90° 下弯，grip 在轴线下方（`gzmax < AXLE_Z-0.02`）。
  - birdcage_spider：hub 在 +X 端（`ROLLER_X_MAX-0.005 < hub_x < ROLLER_X_MAX+0.015` birdcage L400-404），`cage_spoke_{i}`（6 根）辐射 seat 到 roller_cover 端面（`allow_overlap(cage_spoke_{i}, roller_cover)` + `expect_contact(contact_tol=0.006)` birdcage L328-338, L420-427）。
  - straight_inline_shank：shank 直杆 + zinc collar，grip 与 roller 同轴。
- **grip 接口（互斥）**：所有 grip 件挂 root，wire socket 插进 grip collar/socket：
  - smooth：单 `handle_grip`，wire 进 collar neck。
  - ribbed：`finger_ridge_{i}`（5 个 torus）凸出 valley 表面、等距 X 站（`abs(center_x - expected) < 0.004`、uniform spacing ribbed L441-478），inline visual。
  - hollow_tube：`handle_tube` stepped bore（ENTRY_BORE_R>AXLE_R+0.001 宽、SOCKET_BORE_R<AXLE_R 紧、ENTRY_BORE_DEPTH>0.008 tube L412-421），`grip_ring_{i}`（6 个环箍）等距 X，wire shank `expect_overlap(min=0.020)` 进 bore。
  - pole_socket：`handle_grip` flat butt + female bore，`thread_turn_{i}`（6 turn 内螺纹）等距 X 站、contact bore 壁（pole L430-450）。
- **cover 接口（互斥）**：所有 cover 是 roller_cover child 的 mesh/子件：
  - smooth/nap/taper：`roller_core` 外壁 `expect_contact(roller_core, roller_cover, contact_tol=0.0006)`（坐 bore 不漂浮）；nap_ring/taper cover 各自子件。
  - perforated_lattice：`lattice_rib_{i}`/`lattice_hoop_{i}` `expect_within(yz, ..., roller_cover, margin=0.001)` + `expect_contact(..., roller_cover, contact_tol=0.001)`（坐 bore 壁不漂浮）；`end_spider_{i}` `expect_contact(end_spider_{i}, lattice_hoop_<near>, contact_tol=0.003)`（spider 接 hoop）（perf L426-480）。
- **mating policy**：所有 journal / spoke-seat / shank-in-collar / wire-in-socket / ridge-on-body / ring-on-tube / thread-in-bore / lattice-on-bore 都是 **captured-fit 过盈**（轴 / 杆 / 颈 / 环嵌入孔 / 坐面），**非两轴对齐面对接 → 省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 `frame_to_roller` origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：`frame_to_roller` q=0（roller 静止，CONTINUOUS 无 limit，rest=0 自然），run_tests 用 pose({spin: π/2}) 验证可旋转且居中。
- **互斥 / 可选 / 派生**：cage_shank 三候选互斥；grip 四候选互斥；cover 四候选互斥。perforated_lattice **删 roller_core 改 journal 承载面** → 与 cage_shank 的 journal 假设有跨槽耦合（见 §9）。所有 cage_shank 与 grip 正交（任意组合合法，钢丝都引到 grip socket）。

## 每槽位 Module Emits / Interfaces

### Slot A / cage_shank — z_crank_wire（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`wire_frame` 单一 swept tube 作 `handle_frame` root visual）| parent `_frame_wire_mesh` L137-146 / L183-187 |
| internal joints | 无（cage_shank 全是 root visual，无独立 joint）| — |
| upstream interface | root（坐 grip，无父）；钢丝远端 stub 穿 roller bore（供 journal）| parent L120-134 |
| downstream interface | +X 端 90° crank 下弯插进 grip socket（`expect_contact(wire_frame, handle_grip)`）+ 轴线 journal 面（供 `frame_to_roller`）| parent L325-332 |

### Slot A / cage_shank — birdcage_spider
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`wire_axle` + `handle_stem` + `hub_cap` + `cage_spoke_{i}`×6 全作 root visual）| birdcage L246-274 |
| internal joints | 无 | — |
| upstream interface | root；直 `wire_axle` 穿 roller bore（供 journal）| birdcage L137-146 |
| downstream interface | `handle_stem` 下弯插进 grip（`expect_contact(handle_stem, handle_grip)`）+ `hub_cap`/`cage_spoke_{i}` 在 +X 端 retention（spoke↔roller_cover `allow_overlap`+`expect_contact`）| birdcage L420-462 |

### Slot A / cage_shank — straight_inline_shank
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`shank` + `collar` 作 root visual；grip 由 grip slot 提供）| straight L186-201 |
| internal joints | 无 | — |
| upstream interface | root；`shank` 直杆穿 roller bore（供 journal，无 Z drop）| straight L115-124 |
| downstream interface | `shank`→`collar`(zinc)→grip 链式 `expect_contact`，grip 与 roller 同轴 | straight L316-331 |

### Slot B / grip — smooth_molded_grip（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`handle_grip` 单 revolve barrel 作 root visual）| parent L178-182 |
| internal joints | 无 | — |
| upstream interface | wire socket 进 collar neck（`expect_contact(<钢丝>, handle_grip)`）| parent L325-332 |

### Slot B / grip — ribbed_scalloped_grip
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`handle_grip`(scalloped) + `finger_ridge_{i}`×5 作 root visual）| ribbed L236-255 |
| internal joints | 无（ridge 是 inline 非移动 visual，Rule 1）| — |
| upstream interface | wire socket 进 collar neck；ridge 凸出 valley 表面、等距 X 站 | ribbed L441-478 |

### Slot B / grip — hollow_tube_sleeve
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`handle_tube`(stepped bore) + `grip_ring_{i}`×6 作 root visual）| tube L240-265 |
| internal joints | 无 | — |
| upstream interface | wire shank press-fit 进 socket bore（`expect_overlap(wire_frame, handle_tube, min=0.020)`）；ring 等距 X 凸出 tube | tube L424-460 |

### Slot B / grip — pole_socket_grip
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（`handle_grip`(flat butt+bore) + `thread_turn_{i}`×6 作 root visual）| pole L242-270 |
| internal joints | 无 | — |
| upstream interface | wire socket 进 collar neck；butt 端 female bore + 内螺纹 thread_turn contact bore 壁 | pole L417-450 |

### Slot C / cover — smooth_foam_cylinder（基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `roller_cover`（moving child；visual `roller_cover` tube + `roller_core` sleeve）| parent L190-200 |
| internal joints | 无（roller 内无活动件；活动是 `frame_to_roller` 跨件）| — |
| upstream interface | journal = `roller_core` 内 bore 捕轴（`allow_overlap(<钢丝>, roller_core)` + `expect_overlap(axes="x", min=0.15)`）；`roller_core` 外壁 `expect_contact` cover bore | parent L228-293 |

### Slot C / cover — napped_pile_fabric
| emits | 描述 | 来源 |
|---|---|---|
| parts | `roller_cover`（visual `roller_cover` + `roller_core` + `nap_ring_{i}`×6）| nap L291-311 |
| internal joints | 无（nap 是 roller 子件 inline visual，Rule 1）| — |
| upstream interface | 同 smooth（journal 在 roller_core）；nap 径向凸出 + 留 NAP_END_MARGIN 不到端口 | nap L474-515 |

### Slot C / cover — feathered_taper_edge
| emits | 描述 | 来源 |
|---|---|---|
| parts | `roller_cover`（visual `roller_cover` Lathe taper + `roller_core` Cyl 短）| taper L221-230 |
| internal joints | 无 | — |
| upstream interface | journal 在 roller_core 中段 bore（taper `expect_overlap` 放宽 min=0.10）；窄 bore 清尖端、宽 bore 坐 core | taper L258-323 |

### Slot C / cover — perforated_lattice_core
| emits | 描述 | 来源 |
|---|---|---|
| parts | `roller_cover`（visual `roller_cover` + `lattice_rib_{i}`×8 + `lattice_hoop_{i}`×5 + `end_spider_{i}`×2；**无 roller_core**）| perf L282-316 |
| internal joints | 无 | — |
| upstream interface | **journal 迁到 `end_spider_{i}` hub bore**（`allow_overlap(<钢丝>, end_spider_{i})` + `expect_overlap(axes="x", min=0.001)` 各 hub）；rib/hoop 坐 cover bore 壁、spider 接 hoop | perf L344-480 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| cage_shank | enum | z_crank_wire / birdcage_spider / straight_inline_shank | z_crank_wire | choice | 由 deterministic procedural sampler 选；决定 root 钢丝 path + grip 偏置 + 是否多 hub-spoke | Slot A 表 |
| grip | enum | smooth_molded_grip / ribbed_scalloped_grip / hollow_tube_sleeve / pole_socket_grip | smooth_molded_grip | choice | sampler 选；决定 grip part profile + ridge/ring/thread 阵列 | Slot B 表 |
| cover | enum | smooth_foam_cylinder / napped_pile_fabric / feathered_taper_edge / perforated_lattice_core | smooth_foam_cylinder | choice | sampler 选；决定 roller_cover mesh + **journal 承载面**（perf 删 roller_core 迁 end_spider）| Slot C 表 |
| palette_style | enum | classic_coral_steel / industrial_black_zinc / pro_blue_yellow / mini_pastel_cream / safety_orange_grey | classic_coral_steel | palette | palette only，**不计入 slot_choice**；每 seed 采一套（frame 钢丝色 + grip 色 + cover nap 色，见下表）| 各样本材质 |
| roller_len_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放 ROLLER_LEN（联动钢丝 path X 站、core 长、nap/lattice X 站、hoop spacing），clamp | parent L42 |
| roller_dia_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 ROLLER_OUTER_R（联动 cover OD、cage_R、spoke r3），clamp（保 dia_y/z∈(0.034,0.042) run_tests 带）| parent L43 |
| axle_radius_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 AXLE_R + 同步 core_inner_r / spider_hub_bore（保 journal 过盈带），clamp | parent L46 |
| frame_drop_scale | float | [0.80, 1.15] | 1.0 | conditional | 仅 cage_shank∈{z_crank_wire, birdcage_spider} 有效；缩放 FRAME_DROP（grip 偏置量）；straight_inline 时忽略（drop=0）| parent L53 |
| handle_len_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 HANDLE_LEN（grip 长，联动 ridge/ring/thread 排布跨度），clamp | parent L54 |
| grip_belly_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 grip belly 半径 / tube OD（保读作握把），clamp | parent L160 / tube L70 |
| spoke_count (cage_local) | int | 见 §8（cage_shank=birdcage_spider 局部 count，默认 6）| 6 | conditional | **module-local 固定阵列 count，不进 slot_choice**；仅 birdcage 有效 | birdcage L66 |
| ridge_count (grip_local) | int | 见 §8（grip=ribbed 局部 count，默认 5）| 5 | conditional | **module-local，不进 slot_choice**；仅 ribbed 有效 | ribbed L78 |
| ring_count (grip_local) | int | 见 §8（grip=hollow_tube 局部 count，默认 6）| 6 | conditional | **module-local，不进 slot_choice**；仅 hollow_tube 有效 | tube L79 |
| thread_turn_count (grip_local) | int | 见 §8（grip=pole_socket 局部 count，默认 6）| 6 | conditional | **module-local，不进 slot_choice**；仅 pole_socket 有效 | pole L77 |
| nap_ring_count (cover_local) | int | 见 §8（cover=napped 局部 count，默认 6）| 6 | conditional | **module-local，不进 slot_choice**；仅 napped 有效 | nap L75 |
| rib_count / hoop_count (cover_local) | int | 见 §8（cover=perforated 局部 count，默认 8 / 5）| 8 / 5 | conditional | **module-local，不进 slot_choice**；仅 perforated 有效 | perf L71-72 |
| (—) | constraint | — | — | inequality | journal 过盈带：smooth/nap/taper `core_inner_r = AXLE_R·axle_radius_scale − 0.0006`（轴在 core bore 内过盈）；perf `spider_hub_bore_r = AXLE_R·axle_radius_scale − 0.0006`；违反则同步缩 bore 保过盈 | parent L104 / perf L82 |
| (—) | constraint | — | — | inequality | grip clears roller：`grip xmin > ROLLER_X_MAX·(roller_len_scale)/2`（`expect_gap(handle_grip/handle_tube, roller_cover, min_gap=0)`）；违反则推 grip 远端或缩 roller_len | parent L351-359 |
| (—) | constraint | — | — | inequality | birdcage spoke 不超 roller OD：`r3 = ROLLER_OUTER_R·roller_dia_scale − 0.002`（spoke 端 seat roller 端面不穿出）；随 roller_dia_scale 派生 | birdcage L172 |
| (—) | constraint | — | — | inequality | feathered taper bore 清尖端：`wire_clearance_r = AXLE_R·axle_radius_scale + 0.0008 < TIP_R`（窄 bore 须小于尖端半径，轴过尖端不穿）；违反则增 TIP_R 或缩 axle | taper L120 |
| (—) | constraint | — | — | inequality | nap / lattice 留端口：`nap_x ∈ (ROLLER_X_MIN+margin, ROLLER_X_MAX−margin)`（hollow 端可见，nap L510-515）；lattice rib_len > ROLLER_LEN·0.88（perf L420-424）；随 roller_len_scale 派生 | nap L195 / perf L138 |

palette_style 候选（每 seed 采一套，**不计入 slot_choice**，跨 5★ 样本观察的真实材质 / 色集 + 合理外推）：
| palette_style | frame 钢丝 / shank | grip / handle | cover / nap | end hardware（hub/collar/core/lattice）| 来源样本 |
|---|---|---|---|---|---|
| classic_coral_steel（默认）| 钢灰 (0.62,0.63,0.65) | coral/pink (0.86,0.45,0.43) | cream (0.93,0.91,0.84) / nap (0.96,0.95,0.90) | endcap 米灰 (0.80,0.78,0.72) | parent / 多数变体 |
| industrial_black_zinc | 黑钢 (0.10,0.11,0.12) | 黑 rubber (0.18,0.18,0.20) | 白灰 cover | zinc collar/hub (0.50,0.52,0.54) | straight `ZINC` + tube `DARK_RUBBER` 外推 |
| pro_blue_yellow | 镀锌 (0.74,0.76,0.79) | 蓝 grip (0.13,0.32,0.72) + 黄 ridge (0.95,0.80,0.10) | 黄绒 nap | 灰 lattice (0.76,0.76,0.74) | 行业配色外推 |
| mini_pastel_cream | 浅钢 | 薄荷 / 浅粉 pastel grip | cream cover | 米 endcap | parent cream 族外推 |
| safety_orange_grey | 钢灰 | 橙安全 grip (0.95,0.42,0.08) + 黑 ridge | 灰 cover | 灰 collar/lattice | 安全色外推 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / journal 过盈 / clearance / 偏置量 / 阵列跨度，**绝不改变 cage_shank / grip / cover 的拓扑**。

## Multiplicity / Copy Logic

- **无模板级可变 multiplicity 轴**：核心结构由固定 named slots（cage_shank / grip / cover）表达，不暴露顶层 `*_count`，也不通过循环复制模板级 part/joint 形成顶层结构差异轴。整件物体只有 **1 个 roller_cover、1 个 grip、1 根 frame** —— 与 source map §41-51 一致（"无顶层 multiplicity 轴"）。
- **存在 module-local 固定 / 局部可变阵列 visual（按 module 声明，不进 slot_choice）**：每个 cage_shank / grip / cover candidate 内部用 `for i in range(n)` + `name_{i}` + 共享 helper + 规则化 placement 写好的装饰 / 结构子件阵列。它们是各自 candidate 的**局部 count**，隔在 module 内，**不构成顶层 N 轴、不编进 `slot_choices_for_seed`**：
  - birdcage_spider 的 `cage_spoke_{i}`：`for i in range(N_SPOKES=6)`，等角 2π/N 辐射，inline root visual（birdcage L269-274）。局部域建议 spoke∈[4,8]，默认 6。
  - ribbed_scalloped_grip 的 `finger_ridge_{i}`：`for i in range(NUM_FINGER_RIDGES=5)`，等距 X，TorusGeometry inline visual（ribbed L250-255）。局部域 ridge∈[3,6]，默认 5。
  - hollow_tube_sleeve 的 `grip_ring_{i}`：`for i in range(GRIP_RING_COUNT=6)`，等距 X 环箍 inline visual（tube L259-265）。局部域 ring∈[3,8]，默认 6。
  - pole_socket_grip 的 `thread_turn_{i}`：`for i in range(NUM_THREAD_TURNS=6)`，螺旋等距 inline visual（pole L255-270）。局部域 thread∈[4,8]，默认 6。
  - napped_pile_fabric 的 `nap_ring_{i}`：`for i in range(NAP_RINGS=6)`，等距 X 段 roller 子件（nap L306-311）。局部域 nap∈[4,8]，默认 6。
  - perforated_lattice_core 的 `lattice_rib_{i}`×8 / `lattice_hoop_{i}`×5 / `end_spider_{i}`×2：`for i in range(N_RIBS/N_HOOPS/2)`（perf L293-316）。局部域 rib∈[6,12]、hoop∈[3,7]，end_spider 固定 2（两端 journal，结构必需，不可变）。
  - straight_inline_shank 的 `end_cap_{i}`：`for i in range(2)`，roller 两端 ring（straight L216-222）。固定 2（属 cover 子件装饰，随 straight cover 退化情形发射）。
- 这些都是 **module-local 阵列**（用共享 helper 发射、绝对式 / 等角规则 placement、无独立 joint，FIXED 装饰 inline visual，Rule 1）。**模板侧可把每个做成对应 module 的局部 count 参数**（spoke_count / ridge_count / ring_count / thread_turn_count / nap_ring_count / rib_count / hoop_count，域见上 + 各 module 内 clamp），但**它们各自隔在 candidate 内、不进顶层 slot_choice**——拓扑多样性的主体来自 cage_shank × grip × cover 三轴（§9），局部 count 只是 module 内细分（参考 clamp spec 的 module-local 固定阵列声明范式）。

## 拓扑多样性审计

总组合数：cage_shank(3) × grip(4) × cover(4) = **48**（与 source map §53 一致）。

仅 grip(4) × cover(4) = **16 ≥ 10**（已达机械门控）；叠 cage_shank(3) → 48，充裕。

理由：三轴各改真实 part 树 / mesh 拓扑（cage_shank 改 root 钢丝 path + hub-spoke 阵列 + grip 偏置；grip 改握把件 profile + ridge/ring/thread 阵列 + part visual 名；cover 改 child mesh + journal 承载面（perf 删 roller_core 迁 end_spider））。每条 `(slot, module)` tuple 自然进 `slot_choices_for_seed`（`("cage_shank", m)`、`("grip", m)`、`("cover", m)`），48 distinct 远超 ≥10。**注意**：唯一活动 joint（`frame_to_roller` CONTINUOUS）全候选共享，joint 拓扑本身不变——多样性来自 part 树 / mesh / 阵列 / journal 承载面的结构差异，不是 joint-type 差异（与 cushion/clamp 的多 joint-type 不同，本类是单 joint + 多结构层）。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（cage_shank / grip / cover），经兼容矩阵合法化（核心是 perforated_lattice 的 journal-承载面 gate，见下表），再（可选）`rng.choices` 各 module-local count，再 uniform 各连续 scale + 采 palette_style。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（重点看 roller 旋转居中、grip 偏置 / 同轴、birdcage retention cage、perf lattice 透过端口可见）。


Controlled local parameterization：见 §参数表的 roller_len_scale / roller_dia_scale / axle_radius_scale / handle_len_scale / grip_belly_scale（independent）+ frame_drop_scale（conditional@z_crank/birdcage）+ 各 module-local count（conditional@对应 module）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（解析 conditional 范围：frame_drop 仅 crank/birdcage、各 local count 仅对应 module）→ 采 independent roller/轴/grip scale → 派生（core_inner_r 随 axle_radius_scale、钢丝 path X 站随 roller_len_scale、spoke r3 随 roller_dia_scale、nap/lattice X 站随 roller_len_scale）→ 用五条 inequality（journal 过盈、grip clears roller、spoke 不超 OD、taper bore 清尖端、nap/lattice 留端口）投影 / 回缩。跨部件依赖（core bore vs 轴、grip vs roller、spoke vs OD、taper bore vs tip、nap/lattice vs 端口）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 `frame_to_roller` origin / journal captured 接口 / cage retention / 类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（cage_shank/grip/cover），经兼容矩阵合法化，再（可选）采各 module-local count，再 uniform 各 scale + palette | slot_choices_for_seed 含 `("cage_shank",m)`/`("grip",m)`/`("cover",m)` 且与 build 一致 |
| compatibility matrix | **核心 gate = perforated_lattice_core 的 journal 承载面**：perf 删 `roller_core`、journal 迁到 `end_spider_{i}` hub bore。(1) **cover=perforated_lattice × cage_shank=birdcage_spider**：birdcage 的 hub_cap + retention cage 也在 +X 端、本就 hold cover on axle；perf 又在两端各放 end_spider hub journal —— 两者都改 +X 端 axle 捕获面，hub/spider 可能重复 / 干涉（source map §60 标记的风险）。**裁决**：组合时把 birdcage 的 +X hub 与 perf 的 +X end_spider 二选一（优先保 perf 的 end_spider journal，把 birdcage 降级为不带 +X hub_cap 的 retention-only spoke，spoke 仍 seat roller 端面）；或更稳：**perforated_lattice 时 gate cage_shank∈{z_crank_wire, straight_inline_shank}**（两者 journal 不在 +X hub，与 end_spider 不冲突），birdcage 仅配 roller_core cover（smooth/nap/taper）。首版取后者（更稳）。 (2) **cover∈{smooth/nap/taper} × 任意 cage_shank**：journal 都在 roller_core 中段 bore，钢丝 elem 名随 cage_shank（wire_frame/wire_axle/shank），allow_overlap 对名即可，全合法。 (3) **grip 与 cage_shank / cover 正交**：四 grip 任意配三 cage_shank、四 cover，钢丝都引到 grip socket（hollow_tube 用 expect_overlap min=0.020、其余 expect_contact），全合法。 (4) straight_inline_shank（grip 同轴 HANDLE_Z=0）配 hollow_tube/pole_socket（butt socket）需对齐插入深度（collar↔socket anchor，source map §61）→ resolve 统一 socket X anchor。 | 无 floating / collision / +X hub 与 end_spider 重叠 / journal 不捕轴 / roller 旋转偏心 / grip 撞 roller / lattice 漂浮端口 |
| controlled local variation | 5 independent + 1 conditional scale + 7 module-local count（conditional），每 build 统一；count 仅在对应 module 解析 | 比例 / 阵列变化不破坏 frame_to_roller origin、journal captured、cage retention、grip clears、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 cover/cage 机构 QC（旋转居中 / birdcage cage / perf lattice 可见 / journal 捕轴）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| cage_shank | 3 | yes | yes | z_crank_wire / birdcage_spider / straight_inline_shank（root 钢丝 path + grip 偏置 + hub-spoke 阵列）|
| grip | 4 | yes | yes | smooth / ribbed / hollow_tube / pole_socket（profile + 阵列 + socket 内腔）|
| cover | 4 | yes | yes | smooth_foam / napped / feathered_taper / perforated_lattice（mesh + journal 承载面）|

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 `("cage_shank",m)`/`("grip",m)`/`("cover",m)`（module-local count 默认不进 slot_choice，除非审核要求把某 count 提为拓扑维度）
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 把各 scale clamp 到声明范围；frame_drop 为 conditional 随 cage_shank 解析（straight_inline 时 drop=0）；各 module-local count clamp 到对应域；五条 inequality（journal 过盈、grip clears roller、spoke 不超 OD、taper bore 清尖端、nap/lattice 留端口）在 resolve 内投影 / 回缩
- compatibility matrix gate perforated_lattice × birdcage_spider（journal 承载面冲突）：首版 perforated_lattice 时 cage_shank∈{z_crank_wire, straight_inline_shank}；其余组合三轴正交全合法
- 连续 scale / 阵列 count clamp 后不破坏 `frame_to_roller` origin / journal captured 接口 / cage retention / grip clears / 类别身份
- 关键 joint：`frame_to_roller` **CONTINUOUS** axis≈(1,0,0)（abs(axis[0])>0.99、y/z≈0，全候选共享，唯一活动 joint）；origin=(0,0,AXLE_Z=0) 落轴线滚筒中心；roller quarter-spin 后仍居中（y_center≈0、z_center≈AXLE_Z）
- journal captured 过盈：element-scoped `allow_overlap`——smooth/nap/taper `(<钢丝 elem>, roller_core)`（钢丝 elem 名随 cage_shank：z_crank=`wire_frame` / birdcage=`wire_axle` / straight=`shank`）；perforated `(<钢丝 elem>, end_spider_{i})` i∈{0,1}；birdcage 另加 `(cage_spoke_{i}, roller_cover)` ×6 retention seat —— 照搬各样本 run_tests 的 allow_overlap 段
- module-local 阵列遵循 `cage_spoke_{i}`/`finger_ridge_{i}`/`grip_ring_{i}`/`thread_turn_{i}`/`nap_ring_{i}`/`lattice_rib_{i}`/`lattice_hoop_{i}`/`end_spider_{i}`/`end_cap_{i}` 命名 + 等角 / 等距 placement + Rule 1（无独立 joint）
- perforated_lattice 断言无 `roller_core` part visual、journal 在 `end_spider_{i}`（照搬 perf L344-366, L426-480 lattice 坐 cover / spider 接 hoop 检查）
- grip clears roller：`expect_gap(<grip elem: handle_grip 或 handle_tube>, roller_cover, axis="x", min_gap=0)`（grip part visual 名随 grip slot）
- grandfather：所有 journal / spoke-seat / shank-in-collar / wire-in-socket / ridge / ring / thread / lattice captured 接口省略 MatingContract，由 `frame_to_roller` origin 检查 + allow_overlap 守

## Reject cases

- `frame_to_roller` 设成 REVOLUTE 带 limit（lower/upper）而非 CONTINUOUS 自由旋转 → 违反全候选共享的核心机构（所有样本 `joint_type==CONTINUOUS`，滚筒无角限）。
- `frame_to_roller` axis 设非 +X（如 +Z）或 origin 离轴线滚筒中心 → roller 旋转偏心，`abs(axis[0])>0.99` / quarter-spin 居中 / `fail_if_articulation_origin_far_from_geometry` FAIL。
- cover=perforated_lattice 仍发射 `roller_core` 或把 journal 放 roller_core（perf 删 core、journal 在 end_spider）→ 双 journal / 漂浮，违反 perf 拓扑（perf run_tests 断言 journal 在 end_spider hub）。
- cover=perforated_lattice × cage_shank=birdcage_spider 同时在 +X 端放 hub_cap + end_spider → 两 journal/retention 重叠干涉；必须 gate（首版 perf 仅配 z_crank/straight）。
- 把 module-local 阵列（cage_spoke / finger_ridge / grip_ring / thread_turn / nap_ring / lattice_rib / lattice_hoop）当独立活动 part 加 joint → 违反 Rule 1（FIXED 装饰 / 结构阵列，应 inline 为承载 part visual）。
- journal bore 开得比轴大（无过盈）致钢丝漂浮在 bore / hub 内 → `expect_overlap(axes="x")` FAIL；core_inner_r / spider_hub_bore_r 须比 AXLE_R 紧约 0.0006。
- grip 偏置错：z_crank/birdcage 把 grip 放轴线上（不下弯）或 straight_inline 把 grip 放轴线下方（带 drop）→ 违反各 cage_shank 的 grip 偏置语义（`gzmax<AXLE_Z-0.02` vs `handle_center_z≈AXLE_Z`）。
- grip 撞 roller（grip xmin ≤ roller xmax）→ `expect_gap` FAIL；须推 grip 远端或缩 roller_len。
- feathered_taper 的窄 bore ≥ TIP_R 致轴在尖端穿出 cover → taper bore 清尖端约束 FAIL；wire_clearance_r 须 < TIP_R。
- nap / lattice 铺到 roller 开口端 → 中空端口被遮、cage 不可见；nap 须留 NAP_END_MARGIN、lattice rib_len > ROLLER_LEN·0.88 但不到端口。
- 给 journal / captured 接口补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质（palette_style / roller scale）当新 candidate 塞进 slot → 不是结构差异。
- 把 lint roller / rolling pin / paint brush 语义混入（粘毛纸卷 / 双端把手轴 / 无滚筒）→ 出类，本类是单旋转 foam 滚筒手具。

## 与相邻类别的边界

- 不该混入：**lint roller / 粘毛除尘滚筒**——形态相邻（旋转 cover + crank handle），但 cover 是粘性纸卷 / 短粗、无 foam/nap paint cover、非油漆作业身份；如需可作单独 slug（主结构相近但 cover 身份不同）。
- 不该混入：**擀面杖 / rolling pin**——cylinder 双端带把手绕自身轴转，无偏置 crank handle、无 foam/nap cover、主运动 spine 不同（rolling pin 把手轴 = root，cylinder 是 root 本体；本类 frame = root，cover 是独立旋转 child）。
- 不该混入：**paint brush / 油漆刷**——无滚筒、无旋转机构，纯刚性柄 + 刷毛。
- 不该混入：**工业 / 传送带辊轮**——非手持、无 grip、无 crank，固定座辊。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **perforated_lattice × birdcage_spider 兼容裁决**——首版取"perf 仅配 z_crank/straight"（最稳，birdcage 仅配 roller_core cover），还是要实现"二选一 +X journal"的更细 gate；(2) journal 承载面随 cover 切换（roller_core 中段 bore vs end_spider hub）的 allow_overlap 钢丝 elem 名映射（wire_frame/wire_axle/shank）是否模板内统一成一个 `_axle_elem_name(cage_shank)` helper；(3) grip part visual 名随 grip slot 变（handle_grip vs handle_tube）对 `expect_gap` / `slot_choices` 的影响是否需统一成 `handle_grip` 别名；(4) module-local count（spoke/ridge/ring/thread/nap/rib/hoop）是否暴露为可采样局部参数（域见 §8）还是首版固定各 module 默认值（6/5/6/6/6/8/5），是否要把某个提为顶层 slot_choice 拓扑维度；(5) straight_inline_shank 同轴 grip 配 hollow_tube/pole_socket butt socket 的插入深度对齐（collar↔socket anchor）；(6) Topology target 48<300 的说明是否接受（本小类真实结构上限）；(7) palette_style 5 套是否合适，pro_blue_yellow/mini_pastel/safety_orange 三套为样本配色外推。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- **共享 helper**：`_roller_cover_shape`（按 cover 切 cq tube / Lathe taper / lattice-host tube）、`_core_tube_shape`（smooth/nap/taper 用；perf 不用，改 lattice helper）、`_frame_wire_mesh`/`tube_from_spline_points`（z_crank/birdcage 钢丝；straight 用 `_straight_shank_shape` cylinder）、`_handle_shape`（按 grip 切 smooth barrel / scalloped / flat-butt-bore；hollow_tube 用 `_handle_tube_shape`）、`_finger_ridge_mesh`/`_grip_ring_shape`/`_thread_turn_points`/`_cage_spoke_path`/`_nap_ring_mesh`/`_lattice_rib_shape`/`_lattice_hoop_shape`/`_end_spider_shape`（各 module-local 阵列 helper）。
- **journal 承载面统一**：建议 `_axle_elem_name(cage_shank)` 返回钢丝 elem 名（z_crank→`wire_frame`、birdcage→`wire_axle`、straight→`shank`），`_journal_target(cover)` 返回承载 elem（smooth/nap/taper→`roller_core`、perf→`end_spider_0`/`end_spider_1`）；`run_paint_roller_tests` 据此逐组合补 element-scoped `allow_overlap` + `expect_overlap(axes="x")`，照搬各样本 run_tests 段（parent L228-249、birdcage L316-349、straight L250-269、perf L344-366）。
- **grip part visual 名归一**：hollow_tube 源用 `handle_tube`，其余用 `handle_grip`；建议模板内统一逻辑名（如都查 `grip` 件的 primary visual），`expect_gap`/`slot_choices` 用归一名，避免分支硬编码两套名字。
- conditional 范围解析顺序：先采 cage_shank / grip / cover → 解析 frame_drop（仅 crank/birdcage，straight=0）/ 各 module-local count（仅对应 module）/ journal 承载面（cover 决定）→ 采 independent roller/轴/grip scale → 派生（core_inner_r/spider_hub_bore 随 axle_radius_scale、钢丝 path X 站 / nap-lattice X 站 / hoop spacing 随 roller_len_scale、spoke r3 随 roller_dia_scale、taper bore 随 axle）→ 投影五条 inequality。
- **perforated_lattice 实现注记**：删 roller_core，2 个 end_spider 是结构必需 journal（不可减为 1）；rib/hoop 坐 cover bore 壁（`expect_within` + `expect_contact`），spider arm 接最近 hoop；journal `expect_overlap` min 放宽到 0.001（hub 短，perf L357-366）。birdcage 与 perf 同时改 +X 端 → 首版 gate（见 §9）。
- 参考模板：选运动拓扑相近的——root + 单一 CONTINUOUS spinning child + 多结构替换层。clamp 的 `frame` root + `screw` 单一 PRISMATIC child（同为 root + 单一活动 child + 多 slot 替换层 + module-local 固定阵列 + captured 过盈 allow_overlap + 三轴正交/少量 gate）与本类同构，可同构改编（本类把 PRISMATIC 换 CONTINUOUS、把 foot/handle/frame 三轴换 cage_shank/grip/cover）。paint_roller 尺度小（roller ~0.18m、轴 ~0.0028m），joint origin 须精确落轴线滚筒中心（≤0.015m baseline）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C（parent 基线）| z_crank_wire + smooth_molded_grip + smooth_foam_cylinder | rec_..._pain_..._ec6d7dba | `_frame_wire_path` L120-134 / `_frame_wire_mesh` L137-146 / `_handle_shape` L149-169 / `_roller_cover_shape` L72-93 / `_core_tube_shape` L96-117 / `frame_to_roller` CONTINUOUS L204-212 / journal allow_overlap+expect_overlap L228-249 | 基线坐标约定 + z-crank 钢丝 + smooth barrel grip + smooth foam cover + roller_core journal + 共享旋转机构范式 |
| S2 | A | birdcage_spider | rec_paint_roller_var_cage_birdcage | `_axle_wire_path` L137-146 / `_handle_stem_path` L149-158 / `_cage_spoke_path` L161-184 / `_hub_cap_shape` L187-202 / 装配 L236-274 / spoke allow_overlap L328-338 | 直轴 + 下弯 stem + hub_cap + 6-spoke retention cage（+X 端 hub journal/retention）|
| S3 | A | straight_inline_shank | rec_paint_roller_var_cage_straight | `_straight_shank_shape` L115-124 / `_collar_shape` L127-136 / `_handle_shape`(@AXLE_Z) L139-158 / `_end_cap_ring_shape` L161-175 / 装配 L186-222 / 链式 contact L316-331 | inline 直杆（无 drop）+ zinc collar + 同轴 grip + 2 端 cap ring |
| S4 | B | ribbed_scalloped_grip | rec_paint_roller_var_grip_ribbed | `_handle_shape`(scalloped) L169-202 / `_ridge_x_position` L205-207 / `_finger_ridge_mesh` L210-227 / 装配 L250-255 / ridge 检查 L429-490 | scalloped 握把 + 5 torus finger ridge（等距 X inline visual）|
| S5 | B | hollow_tube_sleeve | rec_paint_roller_var_grip_tube | `_handle_tube_shape`(stepped bore) L167-216 / `_grip_ring_shape` L219-232 / 装配 L240-265 / shank expect_overlap L424-432 | stepped-bore 管套握把（handle_tube）+ 6 grip ring + wire 进 socket bore |
| S6 | B | pole_socket_grip | rec_paint_roller_var_grip_pole | `_handle_shape`(flat butt+bore) L164-207 / `_thread_turn_points` L210-233 / 装配 L242-270 / thread 检查 L417-450 | flat butt + female bore + 6 helical thread turn（extension-pole socket）|
| S7 | C | napped_pile_fabric | rec_paint_roller_var_cover_nap | `_nap_ring_mesh`(MeshGeometry 径向位移) L182-270 / 装配 L306-311 / nap 检查 L472-515 | 绒毛 pile fabric（6 nap ring，留端口）+ roller_core journal 不变 |
| S8 | C | feathered_taper_edge | rec_paint_roller_var_cover_taper | `_smoothstep` L77-79 / `_roller_cover_shape`(Lathe+boolean) L82-131 / `_core_tube_shape`(Cyl 短) L134-147 / 装配 L221-230 / taper 检查 L295-323 | edge/trim roller（Lathe 中段→feathered cone 尖 + 全长窄 bore + 中段宽 bore）+ roller_core journal |
| S9 | C | perforated_lattice_core | rec_paint_roller_var_cover_perf | `_lattice_rib_shape` L134-145 / `_lattice_hoop_shape` L148-165 / `_end_spider_shape` L168-204 / 装配 L282-316（无 roller_core）/ end_spider journal allow_overlap L344-366 / lattice 坐 cover + spider 接 hoop L426-480 | 开笼 lattice（8 rib + 5 hoop + 2 end_spider）+ **journal 迁到 end_spider hub bore**（删 roller_core）|
