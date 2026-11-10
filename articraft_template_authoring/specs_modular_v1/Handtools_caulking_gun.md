# caulking_gun (cartridge caulking gun / sealant dispenser) — Modular Spec

> 来源小类：`picture/Handtools/caulking gun`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Handtools__Handtools_caulking_gun.md`。
> **"caulking gun" 在此 = 手持筒装密封胶/玻璃胶挤出枪（cartridge sealant gun），不是热熔胶枪（hot glue gun，已排除 003.png parent）、不是黄油枪（grease gun，除非仍读作 caulking）。**
> 结构家族 = 装料筒夹持架（cradle/frame，root，固定持有 cartridge）+ 后部握把（grip）+ 推杆驱动（plunger drive）。共享运动学：plunger_rod 沿 +X PRISMATIC 推进、trigger 绕 +Y REVOLUTE 摆动、cartridge FIXED 坐于架内。
>
> **同步状态**：本 spec 引用的 8 个 5 星样本（2 个 parent + 6 个 fork 槽位变体）已同步进本仓库 `data/records/`，rating=5（逐一核对）。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计。引用以 part / joint / helper **名字** 为准（`barrel_body`/`frame`、`_barrel_cradle`/`_build_cradle`/`_barrel_tube`/`_front_cone_cap`/`_rib_rod_geometry`、`_handle_frame`/`_grip_wing`/`_build_grip`/`_build_dring_loop`/`_build_d_handle`、`_plunger_rod`/`_hook_handle`/`_ring_handle`/`_build_plunger_mesh`、`plunger_drive`/`frame_to_plunger`、`trigger_pivot`/`frame_to_trigger`、`cartridge_seat`/`frame_to_cartridge` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `caulking_gun` |
| template path | `agent/templates/Handtools_caulking_gun.py` |
| test path (optional) | `tests/agent/test_caulking_gun_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 root frame，cradle/grip/plunger-drive 三个 part 挂到共同 root；rib_cage 候选内部含 `rib_count` for-loop multiplicity，**非小类级 multiplicity 轴**）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（2 parent + 6 fork 槽位变体；均 converged，compile success、含 PRISMATIC + REVOLUTE 非 fixed joint、workbench-only）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation、run_tests 的 allow_overlap/expect_* 段）|
| read_scope | all 5-star samples in this category（不含 003.png 热熔胶枪 parent，已在 source map 排除，不入池、不 fork）|
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 8/8 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解，**关键拓扑发现**）：
- **8 个样本共享同一拓扑骨架**：1 个 root frame part（固定持有 cartridge）+ 1 个 `cartridge`/`front_cap` FIXED 子件 + 1 个 plunger part（PRISMATIC +X）+ 1 个 trigger part（REVOLUTE +Y）。joint 计数 = 3（1 FIXED + 1 PRISMATIC + 1 REVOLUTE），所有样本一致 —— 这是类别身份。
- **两个坐标 / 命名族**（重要兼容约束，见 §9）：
  - **A 族**（parent A `24ba16de`、closed_barrel、sausage、ring_pull）：root part 名 `barrel_body`，几何在 barrel 轴 z=0 处建模后整体 `lift=(0,0,AXIS_Z)`；joints 名 `cartridge_seat`/`plunger_drive`/`trigger_pivot`；trigger 是后部 `_handle_frame` U-yoke 上挂的下垂 blade（PIVOT_Z≈+0.085 高于轴），grip = `_grip_wing` 固定翼；plunger 在 rod-local frame 建模、PRISMATIC upper≈0.060。
  - **B 族**（parent B `ff090a9c`、ribframe、dgrip、inline_handle）：root part 名 `frame`，几何直接在 barrel 轴 z=0 处建模（不 lift）；joints 名 `frame_to_cartridge`/`frame_to_plunger`/`frame_to_trigger`；trigger 是 barrel 下方-前方 pivot（PIVOT_Z≈-0.040 低于轴）的下垂 blade（pistol/dgrip）或上方 thumb lever（inline）；plunger 在世界 frame 建模、PRISMATIC upper≈0.180。
- **Slot A cradle/frame**（真正改 root 几何 + cartridge 封装方式）：half_barrel（A，下半 shell trough，cartridge 顶部外露）/ skeleton_halfpipe（B，~300° 开口 half-pipe，顶部 60° 开槽）/ closed_barrel（全闭合圆筒 + 底部 loading slot，cartridge 全包）/ sausage_tube（lathe revolve 全闭合筒 + 螺纹 `front_cone` 旋盖 + 软 sausage pack）/ rib_cage（B，`for i in range(N_RODS)` 等角发射 N 根 `rib_rod_{i}` 开放笼）。
- **Slot B grip**（root 上的握把 visual 形态 + trigger 锚点位置）：bracket_wing（A，后部 `_handle_frame` U-yoke + `_grip_wing` 固定翼，trigger 后挂高位）/ pistol_grip（B，`_build_grip` 下垂弧形 pistol tongue，trigger 前下低位）/ d_ring_loop（dgrip，`tube_from_spline_points` 闭合 D 环 round-bar bow，trigger 在环内）/ inline_handle（inlinehandle，`_build_d_handle` 轴向矩形 D-handle，trigger 上挑 thumb lever）。
- **Slot C plunger drive**（plunger part 尾端形态）：ratchet_jhook（A，`_hook_handle` spline-sweep 180° J 弯钩，紧贴 rod 尾）/ thumb_plate（B，`_build_plunger_mesh` 内嵌的后部矩形 thumb plate）/ ring_pull（ringpull，`_ring_handle` torus revolve 闭合拉环）。
- **palette**：A 族 gunmetal/black_plastic/white_cartridge/label_blue/bright_steel；B 族 frame_red/cartridge_blue/collar_red/nozzle_white/steel；sausage 另有 aluminum/dark_steel；inline 另有 handle_grey。→ 4-6 套 colorway（见 §7 palette_style）。

## 核心身份

一只手持**筒装密封胶挤出枪（cartridge caulking / sealant gun）**：一个细长 root `frame`/`barrel_body`（沿 +X，barrel 轴在 Y-Z 面内，长 ~0.21-0.26 m），把一支固定 `cartridge`（白/蓝标筒 或 蓝灰硅胶筒 或软 sausage pack）夹持在 cradle/barrel/cage 内，筒前端为锥形 nozzle + 白尖 tip 指向 +X muzzle；root 后/下方有一个握把（pistol grip / U-yoke bracket+wing / D 环 / 轴向 D-handle）；一根钢 `plunger_rod` 从后部 cap/plate bore 穿出，前端 push disc 顶住 cartridge 后塞、尾端为 J 钩 / thumb plate / 拉环。活动语义恒为：**plunger_rod 沿 barrel 轴 +X PRISMATIC 推进**（挤出密封胶）+ **trigger 绕 +Y REVOLUTE 摆动**（扣动 squeeze）；cartridge 始终 FIXED 坐于架内。默认成熟域：cradle/frame × grip × plunger-drive 笛卡尔积的单支 ~300 ml 手动棘爪枪。

不该混入：
- **热熔胶枪（hot glue gun）**——电热熔棒、电源 rocker、chrome 锥嘴、胶棒后送，无 cartridge 夹持架、无 squeeze-ratchet plunger 语义（003.png parent 已排除，不作 fork 源）。
- **黄油枪（grease gun）**——虽同为筒装挤压枪，若仍读作 caulking（cradle + 锥嘴 + squeeze trigger + plunger rod）可勉强归入；但黄油枪典型为加压注油枪管 + 软管/直嘴 + 杠杆/气动，**若出现软管接头 / 加压泵 / 注油直嘴**即出类，拒绝。
- **注射器 / 一次性胶枪 / 电动挤胶枪**——无可换 cartridge 夹持架 + squeeze trigger + ratchet rod 这套手动挤出身份的，出类。

## 槽位 + 候选模块表

> **建模注记**：caulking_gun 是 **root frame（dispatch cradle/grip 几何 + cartridge FIXED）+ 三个 parallel children**：cartridge（FIXED，consumable）、plunger（PRISMATIC +X）、trigger（REVOLUTE +Y）。三个 slot 中 **Slot A（cradle/frame）改 root 主壳几何 + cartridge 封装与 nozzle 承载方式**，**Slot B（grip）改 root 上握把 visual + trigger 锚点位置（pivot origin）+ trigger blade 形态**，**Slot C（plunger drive）改 plunger part 尾端 visual + PRISMATIC 行程上限**。两个坐标族（A=lift 后挂高位 trigger，B=轴心 z=0 前下低位 trigger）决定了 cradle/grip/drive 的兼容矩阵（见 §9）：A 族 cradle 默认配 A 族 grip（bracket_wing）+ A 族 drive；B 族 cradle 默认配 B 族 grip（pistol/dring/inline）+ B 族 drive。跨族组合需 trigger-pivot 锚点重解析（见 §9 兼容矩阵的统一化策略）。

### Slot A：cradle / frame（root 主壳 —— cartridge 封装 + nozzle/front 承载）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| half_barrel（A 族基线） | rec_..._caul_..._24ba16de（parent A）| `_barrel_cradle` L164-188 / `_front_collar` L191-204 / `_rear_cap` L207-223 / root 装配 L544-575 | eligible if compatible | 下半圆 shell trough（outer cut inner，再 box-cut 上半留 ~0.18R 唇），cartridge 顶部外露坐入；带 `front_collar` 环 + `rear_cap`（bored）；`cartridge` FIXED 子件含 `cartridge_tube`+`cartridge_label`+`nozzle_cone`+`white_tip` |
| skeleton_halfpipe（B 族基线） | rec_..._caul_..._ff090a9c（parent B）| `_build_cradle` L66-85 / `_build_front_ring` L88-97 / `_build_rear_plate` L100-109 / `_build_frame_mesh` L177-183 | eligible if compatible | ~300° 开口 half-pipe（full tube wall 沿 Z 拉伸再 box-cut 顶部 60° gap，旋转到 X 轴），带 `front_ring`（bored）+ `rear_plate`（bored）；`cartridge` 蓝灰硅胶筒 + `front_collar` loft + `nozzle` |
| closed_barrel | rec_caulk_var_closedbarrel（from A）| `_barrel_tube` L169-198（含 bottom loading slot cut）/ root 装配 L555-585 | eligible if compatible | 全闭合圆筒（outer cut inner）+ 底部 -Z 纵向 loading slot；cartridge 全周包裹；run_tests 有 `expect_within(cartridge,barrel_tube,yz)` + "barrel extends above cartridge center" 全包封检查 L728-751 |
| sausage_tube | rec_caulk_var_sausage（from A）| `_barrel_tube`（revolve annular profile）L145-163 / `_front_cone_cap`（revolve threaded cone）L166-198 / `front_cap` part L471-486 | eligible if compatible | lathe revolve 全闭合 aluminum 筒 + **独立 `front_cap` part**（螺纹 `front_cone` 旋盖 + `nozzle_cone` + `white_tip`，FIXED `front_cap_seat`）；装软 sausage pack（无 rigid cartridge 子件，front_cap 取代 cartridge 的 nozzle 承载）|
| rib_cage | rec_caulk_var_ribframe（from B）| `_rib_rod_geometry` L70-82（shared helper）/ `for i in range(N_RODS)` L346-354 / `_build_spine_rail` L112-124 / `_build_frame_body_mesh` L192-199 | eligible if compatible | 开放 rod 笼：N 根（基线 N_RODS=4）等角 `rib_rod_{i}` 沿下圆周发射，连 `front_ring`+`rear_plate`，全长 `spine_rail` 底脊承载 grip/pivot；rod = 共享 `_rib_rod_geometry` helper 复用（**内部 rib_count multiplicity 轴，见 §8**）|

### Slot B：grip / handle（root 上握把 visual + trigger 锚点 + trigger 形态）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键结构 / trigger 锚点特征 |
|---|---|---|---|---|
| bracket_wing（A 族基线） | rec_..._caul_..._24ba16de（parent A）| `_handle_frame`（U-yoke 双侧板+lugs+web+guide boss）L226-296 / `_grip_wing`（固定锥翼）L310-329 / `_pivot_pin` L299-307 / `_trigger_blade` L484-529 | eligible if compatible | 后部 U-yoke bracket（straddle rod）+ 固定 `grip_wing` 翼，形成开口 "V"；trigger 高位后挂（origin=(PIVOT_X, 0, AXIS_Z+PIVOT_Z)，PIVOT_Z≈+0.085），squeeze 时 blade 下端摆向 -X；`trigger_pivot` REVOLUTE axis (0,1,0) upper=0.55 |
| pistol_grip（B 族基线） | rec_..._caul_..._ff090a9c（parent B）| `_build_grip`（下垂弧形 tongue polyline）L112-133 / `_build_pivot_lugs`（双侧板 yoke）L136-174 / `_build_trigger_mesh` L253-288 | eligible if compatible | barrel 下方后部下垂 pistol-grip tongue（GRIP_LEN≈0.115）；trigger 前下低位（origin=(PIVOT_X≈GRIP_FRONT+0.018, 0, PIVOT_Z≈-0.040)），手指在 grip 与 trigger 间隙；REVOLUTE axis (0,1,0) upper=0.5 |
| d_ring_loop | rec_caulk_var_dgrip（from B）| `_build_dring_loop`（`tube_from_spline_points` 闭合 D 环）L128-139 / `_build_dring_bosses` L142-162 / `DRING_PATH` L56-66 | eligible if compatible | 闭合 D 环 round-bar bow（spline-sweep 闭合环 + 两 mounting boss 焊点），手穿过环、trigger 在环内；trigger 锚点同 pistol（PIVOT_X≈-0.042, PIVOT_Z≈-0.040）；run_tests 检 "trigger sits inside D-ring opening" L487-497 |
| inline_handle | rec_caulking_gun_var_inlinehandle（from B）| `_build_d_handle`（轴向矩形 D-frame + 内 cutout）L124-182 / `_build_pivot_lugs`（顶轨上挑 lugs+bridge）L185-226 / `_build_trigger_mesh`（thumb lever 上挑）L321-361 | eligible if compatible | barrel 后**轴向**矩形 D-handle（HANDLE_LEN≈0.110 向后，top/bot rail 上下对称包轴）；trigger 是 barrel 顶上挑 thumb lever（origin=(TRIG_PIVOT_X≈BACK_X-0.002, 0, TRIG_PIVOT_Z≈CRADLE_OUTER_R+0.020)，squeeze 时 lever 顶 tip 前倾 +X）；含 `for i in range(4)` `rivet_{i}` 顶轨装饰（visual，非 part）|

### Slot C：plunger drive / pull end（plunger part 尾端 visual + 行程）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键结构 / joint 特征 |
|---|---|---|---|---|
| ratchet_jhook（A 族基线） | rec_..._caul_..._24ba16de（parent A）| `_plunger_rod`（rod-local，push disc）L421-441 / `_hook_handle`（spline-sweep 180° J 弯钩）L444-481 / `_cart_plunger` L406-418 / `plunger_drive` L645-653 | eligible if compatible | rod + 前 push disc + `cart_plunger` 盘 + 尾端 J 钩（rod 自身端弯 180° curl，紧贴 rod 轴 ~2 rod 径内）；rod-local frame，`plunger_drive` PRISMATIC axis (1,0,0) upper=0.060；run_tests 检 "hook compact within 2 rod dia" + "hook advances with rod" L722-754 |
| thumb_plate（B 族基线） | rec_..._caul_..._ff090a9c（parent B）| `_build_plunger_mesh`（plate+rod+rear thumb rect handle）L298-326 / `frame_to_plunger` L382-391 | eligible if compatible | push plate + 长 rod + 尾端矩形 thumb plate（rear rect 0.020×0.055 fillet）；世界 frame 建模，`frame_to_plunger` PRISMATIC axis (1,0,0) upper=0.180 |
| ring_pull | rec_caulking_gun_var_ringpull（from A）| `_ring_handle`（torus revolve 闭合拉环）L441-466 / `_plunger_rod` L418-438 / `plunger_drive` L630-638 | eligible if compatible | rod + push disc + 尾端**闭合圆拉环** `pull_ring`（torus 在 XZ 面竖立，RING_R≈0.013/wire 0.003，绕 Y 轴 revolve，焊于 rod 尾）；PRISMATIC upper=0.060；run_tests 检 "ring Z-extent confirms closed loop" + "thin in Y (loop with hole)" + "ring advances with rod" L707-744 |

## 槽位图（slot graph）

pattern: parallel_children（root frame 持有 cradle/barrel 主壳几何 + grip visual，三个 child part 挂到 root：cartridge FIXED、plunger PRISMATIC、trigger REVOLUTE）

```
frame / barrel_body  (root；坐地。由 cradle/frame slot 决定主壳 mesh（cradle/tube/cage）+ front ring/collar + rear cap/plate(bored)；由 grip slot 决定握把 visual + trigger pivot 硬件(lugs/pin))
  │
  ├── [cartridge]  (FIXED consumable；cradle slot 派生)
  │     ├─ half_barrel/halfpipe/closed/rib_cage → cartridge part(cartridge_tube/body + label + nozzle_cone/nozzle + white_tip)
  │     │                                          ──[cartridge_seat / frame_to_cartridge: FIXED origin=(0,0,AXIS_Z 或 0)]
  │     └─ sausage_tube → 无 rigid cartridge part；改为 front_cap part(front_cone + nozzle_cone + white_tip)
  │                       ──[front_cap_seat: FIXED origin=(0,0,AXIS_Z)]（软 sausage pack 隐含，nozzle 由 front_cap 承载）
  │
  ├── [plunger]  (plunger drive slot；三选一尾端)
  │     ├─ ratchet_jhook : plunger_rod + cart_plunger + hook_handle ──[plunger_drive: PRISMATIC axis=+X, origin=(ROD_FRONT_X,0,AXIS_Z), upper≈0.060]
  │     ├─ thumb_plate   : plunger(plate+rod+rear thumb plate)      ──[frame_to_plunger: PRISMATIC axis=+X, origin=(0,0,0), upper≈0.180]
  │     └─ ring_pull     : plunger_rod + cart_plunger + pull_ring   ──[plunger_drive: PRISMATIC axis=+X, origin=(ROD_FRONT_X,0,AXIS_Z), upper≈0.060]
  │
  └── [trigger]  (grip slot 派生锚点；REVOLUTE squeeze)
        ├─ bracket_wing : trigger_blade(后挂下垂) ──[trigger_pivot: REVOLUTE axis=+Y, origin=(PIVOT_X,0,AXIS_Z+PIVOT_Z≈+0.085 高位), upper≈0.55]
        ├─ pistol_grip  : trigger_blade(前下下垂) ──[frame_to_trigger: REVOLUTE axis=+Y, origin=(PIVOT_X,0,PIVOT_Z≈-0.040 低位), upper≈0.5]
        ├─ d_ring_loop  : trigger_blade(环内下垂) ──[frame_to_trigger: REVOLUTE axis=+Y, origin=(-0.042,0,-0.040), upper≈0.5]
        └─ inline_handle: trigger(顶上挑 thumb)   ──[frame_to_trigger: REVOLUTE axis=+Y, origin=(BACK_X-0.002,0,CRADLE_OUTER_R+0.020 顶位), upper≈0.5]
```

接口点位与 joint 语义：
- **cradle/frame 接口（root，互斥五选一）**：所有 cradle 决定 root 主壳 mesh + cartridge 封装 + nozzle 承载。half_barrel/halfpipe/closed/rib_cage 用 rigid `cartridge` 子件（FIXED，origin z=AXIS_Z[A 族] 或 0[B 族]）；sausage_tube 用 `front_cap` 子件（FIXED，承载 nozzle）替代 cartridge 的前端。所有 cradle 提供 bored rear cap/plate（plunger rod 穿出口）+ front ring/collar（nozzle 露出口）。
- **plunger 接口（互斥三选一）**：plunger PRISMATIC axis (1,0,0)，origin 在 rear cap/plate seating plane。rod push disc captured 在 cartridge/barrel bore 内（allow_overlap），rod 穿 rear cap bore（allow_overlap + expect_overlap min_overlap≈0.005）。尾端 visual（jhook/thumb/ring）随 rod 刚性平移（run_tests 检 "X advances with rod, dz≈0"）。upper 行程随族（A 族 0.060 短行程、B 族 0.180 长行程）—— 见 §7 行程 scale。
- **trigger 接口（grip slot 派生，互斥四选一）**：trigger REVOLUTE axis (0,1,0)，origin = pivot pin 硬件位置（lugs/boss）。trigger hub captured 在 pivot_pin 上（allow_overlap + expect_overlap yz min≈0.002）+ 在 lugs/frame 间转（allow_overlap）。pivot 高度随 grip：bracket_wing 高位（轴上 +0.085）、pistol/dring 低位（轴下 -0.040）、inline 顶位（轴上 +CRADLE_OUTER_R+0.020）。
- **mating policy**：所有 hinge 是 pin-in-hub captured-pin、所有 plunger 是 rod-in-bore captured-shaft、所有 cartridge 是 nested-consumable seated、sausage front_cap 是 threaded-overlap + expect_contact。几何均非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：所有 trigger q=0（blade 下垂 / lever 静位）、所有 plunger q=0（push disc 在 cartridge 后塞处坐底）、cartridge FIXED 坐架内。
- **互斥 / 可选 / 派生**：cradle 五选一互斥；grip 四选一互斥（派生 trigger pivot origin 与 trigger 形态）；plunger 三选一互斥（派生尾端 visual 与行程）。sausage_tube 取消 rigid cartridge 子件、改 front_cap 子件（cartridge↔front_cap 是 cradle-派生的承载件替换，非额外 slot）。

## 每槽位 Module Emits / Interfaces

### Slot A / cradle — half_barrel（A 族基线；closed_barrel 仅换主壳 mesh helper）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `barrel_body`（root，visual: `barrel_cradle` gunmetal 半 shell + `front_collar` + `rear_cap` bored）；`cartridge` 子件（`cartridge_tube`+`cartridge_label`+`nozzle_cone`+`white_tip`）| A `_barrel_cradle` L164-188 / `_front_collar` L191-204 / `_rear_cap` L207-223 / `_cartridge_*` L332-403 |
| internal joints | `cartridge_seat` FIXED parent=barrel_body child=cartridge origin=(0,0,AXIS_Z)| A L632-638 |
| upstream interface | root（坐地，lift=AXIS_Z；AXIS_Z=REAR_CAP_R 使最低点 rear cap rim 落 z=0）| A L136, L544 |
| downstream interface | bored `rear_cap`（plunger rod 穿出）+ `front_collar` bore（nozzle 露出）+ 上方开口（cartridge 顶部外露 + grip 锚硬件接入）| A L207-223 |

### Slot A / cradle — closed_barrel
| emits | 描述 | 来源 |
|---|---|---|
| parts | 同 half_barrel 但主壳 = `barrel_tube`（全闭合圆筒 + 底部 loading slot）；cartridge 全周包裹 | closedbarrel `_barrel_tube` L169-198 |
| internal joints | `cartridge_seat` FIXED origin=(0,0,AXIS_Z)| closedbarrel L643-649 |
| downstream interface | bored rear_cap + front_collar bore + bottom loading slot（装料口，非 grip 接口）| closedbarrel L65-68, L189-197 |

### Slot A / cradle — sausage_tube
| emits | 描述 | 来源 |
|---|---|---|
| parts | `barrel_body`（`barrel_tube` lathe revolve aluminum 筒 + rear_cap + frame/grip/pin）；**`front_cap` 子件**（`front_cone` 螺纹旋盖 + `nozzle_cone` + `white_tip`）替代 rigid cartridge | sausage `_barrel_tube` L145-163 / `_front_cone_cap` L166-198 / front_cap part L471-486 |
| internal joints | `front_cap_seat` FIXED parent=barrel_body child=front_cap origin=(0,0,AXIS_Z)| sausage L513-519 |
| downstream interface | bored rear_cap（rod 穿出）+ front_cap threaded ring（overlap barrel 外壁，expect_contact）+ cone tip（nozzle 承载）| sausage L201-216, L766-779 |

### Slot A / cradle — skeleton_halfpipe（B 族基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`（root，`frame_shell` = cradle half-pipe + front_ring + rear_plate + grip + pivot_lugs union + `pivot_pin`）；`cartridge`（`cartridge_body`+`front_collar`+`nozzle`）| B `_build_cradle` L66-85 / `_build_frame_mesh` L177-183 / `_build_cartridge_mesh` L200-247 |
| internal joints | `frame_to_cartridge` FIXED origin=(0,0,0)（无 lift，几何直接在轴心）| B L352-358 |
| downstream interface | bored front_ring + rear_plate（rod 穿出）+ 顶部 60° gap（cartridge 外露 + grip 在 frame 内联）| B L88-109 |

### Slot A / cradle — rib_cage（内含 rib_count multiplicity）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`（`frame_body` = front_ring + rear_plate + `spine_rail` 底脊 + grip + lugs union + `pivot_pin`）；N 根 `rib_rod_{i}` steel visual（`for i in range(N_RODS)` 等角发射，共享 `_rib_rod_geometry` helper）；`cartridge` 同 B | ribframe `_rib_rod_geometry` L70-82 / loop L346-354 / `_build_frame_body_mesh` L192-199 |
| internal joints | `frame_to_cartridge` FIXED origin=(0,0,0)| ribframe L366-372 |
| upstream interface | root；`spine_rail` 底脊（替代 cradle 壁，承载 grip + pivot lugs，使开放笼仍刚性）| ribframe `_build_spine_rail` L112-124 |
| downstream interface | bored front_ring + rear_plate（rod 穿出）+ 开放 rod 间隙（cartridge 外露）| ribframe L88-109 |

### Slot B / grip — bracket_wing（A 族基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | root visual: `handle_frame`（U-yoke 双侧板 + 圆 lugs + foot web + rod-guide boss）+ `grip_wing`（固定锥翼）+ `pivot_pin`；child `trigger_lever`（`trigger_blade` loft 楔 + hub + neck，bored hub）| A `_handle_frame` L226-296 / `_grip_wing` L310-329 / `_trigger_blade` L484-529 |
| internal joints | `trigger_pivot` REVOLUTE axis (0,1,0) origin=(PIVOT_X,0,AXIS_Z+PIVOT_Z) lower=0 upper=0.55| A L658-666 |
| upstream interface | trigger hub captured 在 `pivot_pin`（allow_overlap）+ 在 `handle_frame` lugs 间转（allow_overlap）| A L845-869 |

### Slot B / grip — pistol_grip（B 族基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | root visual: `_build_grip` 下垂弧形 tongue（union 进 frame_shell）+ `_build_pivot_lugs` 双侧板 yoke + `pivot_pin`；child `trigger`（`trigger_blade` polyline 弧形 + hub）| B `_build_grip` L112-133 / `_build_pivot_lugs` L136-174 / `_build_trigger_mesh` L253-288 |
| internal joints | `frame_to_trigger` REVOLUTE axis (0,1,0) origin=(PIVOT_X,0,PIVOT_Z≈-0.040) lower=0 upper=0.5| B L368-376 |
| upstream interface | trigger hub captured 在 `pivot_pin`（allow_overlap）| B L488-495 |

### Slot B / grip — d_ring_loop
| emits | 描述 | 来源 |
|---|---|---|
| parts | root visual: `dring_loop`（`tube_from_spline_points` 闭合 D 环 round-bar）+ `dring_bosses` 两焊点 + `pivot_lugs` + `pivot_pin`；child `trigger`（同 pistol blade）| dgrip `_build_dring_loop` L128-139 / `_build_dring_bosses` L142-162 / `DRING_PATH` L56-66 |
| internal joints | `frame_to_trigger` REVOLUTE axis (0,1,0) origin=(-0.042,0,-0.040) lower=0 upper=0.5| dgrip L398-406 |
| upstream interface | trigger 在 D 环开口内（run_tests "trigger sits inside D-ring opening"）；hub captured 在 pin + bar 在 pivot 处汇合（allow_overlap dring_loop↔trigger_blade）| dgrip L487-497, L561-575 |

### Slot B / grip — inline_handle
| emits | 描述 | 来源 |
|---|---|---|
| parts | root visual: `_build_d_handle` 轴向矩形 D-frame（outer cut inner cutout）+ `_build_pivot_lugs` 顶轨上挑 lugs+bridge + `pivot_pin` + `for i in range(4)` `rivet_{i}` 装饰；child `trigger`（thumb lever 上挑 polyline + hub）| inlinehandle `_build_d_handle` L124-182 / `_build_pivot_lugs` L185-226 / `_build_trigger_mesh` L321-361 |
| internal joints | `frame_to_trigger` REVOLUTE axis (0,1,0) origin=(TRIG_PIVOT_X≈BACK_X-0.002,0,TRIG_PIVOT_Z≈CRADLE_OUTER_R+0.020 顶位) lower=0 upper=0.5（squeeze 时 lever 顶 tip 前倾 +X）| inlinehandle L447-455 |
| upstream interface | trigger hub captured 在 pin + 在 lugs Y span 内（expect_within y）| inlinehandle L581-603 |

### Slot C / plunger — ratchet_jhook（A 族基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `plunger_rod` part（`plunger_rod` rod+push disc + `cart_plunger` 盘 + `hook_handle` J 钩）| A `_plunger_rod` L421-441 / `_hook_handle` L444-481 / `_cart_plunger` L406-418 |
| internal joints | `plunger_drive` PRISMATIC axis (1,0,0) origin=(ROD_FRONT_X,0,AXIS_Z) lower=0 upper=0.060| A L645-653 |
| upstream interface | rod 穿 `rear_cap` bore（allow_overlap + expect_overlap x min=0.005）；push disc/cart_plunger captured 在 cartridge tube（allow_overlap）；hook 紧贴 rod 尾 ~2 rod 径| A L816-840 |

### Slot C / plunger — thumb_plate（B 族基线）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `plunger` part（plate + rod + 尾端矩形 thumb plate handle）| B `_build_plunger_mesh` L298-326 |
| internal joints | `frame_to_plunger` PRISMATIC axis (1,0,0) origin=(0,0,0) lower=0 upper=0.180| B L382-391 |
| upstream interface | rod 滑入 cradle + 穿 rear_plate bore（allow_overlap frame_shell）；push plate 顶 cartridge 后塞（allow_overlap）；advanced 时 expect_within yz| B L497-543 |

### Slot C / plunger — ring_pull
| emits | 描述 | 来源 |
|---|---|---|
| parts | `plunger_rod` part（rod+push disc + `cart_plunger` + `pull_ring` torus 闭合环）| ringpull `_ring_handle` L441-466 / `_plunger_rod` L418-438 |
| internal joints | `plunger_drive` PRISMATIC axis (1,0,0) origin=(ROD_FRONT_X,0,AXIS_Z) lower=0 upper=0.060| ringpull L630-638 |
| upstream interface | rod 穿 rear_cap bore（allow_overlap + expect_overlap）；ring 焊于 rod 尾、随 rod 刚性平移（run_tests Z-extent/thin-in-Y/advances 检）| ringpull L806-844, L707-744 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| cradle | enum | half_barrel / skeleton_halfpipe / closed_barrel / sausage_tube / rib_cage | half_barrel | choice | deterministic procedural sampler 选；决定 root 主壳 mesh + cartridge/front_cap 承载 | Slot A 表 |
| grip | enum | bracket_wing / pistol_grip / d_ring_loop / inline_handle | bracket_wing | choice | sampler 选；派生 trigger pivot origin + trigger 形态（互斥）| Slot B 表 |
| plunger_drive | enum | ratchet_jhook / thumb_plate / ring_pull | ratchet_jhook | choice | sampler 选；派生尾端 visual + 行程上限（互斥）| Slot C 表 |
| rib_count (N) | int | 声明域 [3,6]；sweep 采样域 [3,6]（偏小加权：4 高频、3/5 常见、6 长尾）| 4 | conditional→slot_choice | 仅 cradle=rib_cage 有效；编入 slot_choice 为 `n{N}`（拓扑维度）；非 rib_cage 时 N 不存在 | rib_cage `for i in range(N_RODS)` |
| palette_style | enum | gunmetal_pro / red_consumer / blue_silicone / aluminum_sausage / industrial_grey | gunmetal_pro | palette | palette only，**不计入 slot_choice**；见下方 colorway 说明 | 各样本材质 |
| barrel_len_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放 BARREL_LEN/TUBE_LEN 主尺寸（保细长），clamp；连带 cartridge 长 = equation 派生 | resolve clamp |
| barrel_girth_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放 barrel/cartridge R（截面），clamp 使 cartridge 仍坐入、rod push disc 仍套合 | resolve clamp |
| plunger_travel_scale | float | [0.85, 1.10] | 1.0 | conditional | 缩放 PRISMATIC upper（A 族基 0.060 / B 族基 0.180，按 plunger 族解析后再缩）；clamp ≤ cartridge 可用行程 | A L652 / B L390 |
| trigger_open_angle_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 REVOLUTE upper（基 0.5-0.55）；clamp ≤ 0.95·squeeze 极限（trigger 不穿 grip）| A L665 / B L375 |
| grip_drop_scale | float | [0.90, 1.10] | 1.0 | conditional | 仅 pistol_grip/d_ring_loop 有效；缩放 GRIP_LEN/DRING 下垂量；clamp 使握把仍落地下方、trigger 仍在握区 | B L48-50 / dgrip DRING_PATH |
| rib_thickness_scale | float | [0.85, 1.15] | 1.0 | conditional | 仅 rib_cage 有效；缩放 ROD_R（rib 杆径）；clamp 使 N 根 rib 不互撞且仍包住 cartridge | rib_cage L45 |
| (—) | constraint | — | — | inequality | cartridge 长 ≤ cradle 内长 − 2·margin（cartridge 坐入不溢出）：`cartridge_len·barrel_len_scale ≤ cradle_inner_len`；违反则按比例回缩 cartridge | 接口 / clearance |
| (—) | constraint | — | — | inequality | plunger 满行程后 push disc 仍在 cartridge 内 + rod 仍穿 rear cap bore（`travel ≤ cartridge_len − push_disc_seat` 且 `rod_len ≥ travel + bore_engage`）；违反回缩 travel | 接口 / captured-shaft |
| (—) | constraint | — | — | inequality | trigger 满 squeeze 不穿 grip / cartridge：bracket_wing 检 "blade clears grip_wing"（A L781）、B 族检 trigger 不撞 cartridge（local z≤+0.009）；违反回缩 trigger_open_angle | 接口 / clearance |
| (—) | constraint | — | — | inequality | rib_cage：`N·(2·ROD_R·rib_thickness_scale) ≤ 0.85·lower_arc_len`（N 根 rib 沿下圆周不互撞）；违反回缩 N 或 rib_thickness | rib_cage ROD_ARC L47-49 |
| (—) | constraint | — | — | conditional | cradle=sausage_tube 时无 rigid cartridge，cartridge-相关 inequality 改用 front_cap + sausage pack 包络；cradle∈{A 族} 用 lift=AXIS_Z 坐标、cradle∈{B 族} 用 z=0 坐标（见 §9 统一化）| 接口 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / clearance / 行程 / 角度，**绝不改变 cradle / grip / plunger_drive / rib_count 的拓扑**。

**palette_style colorway（4-6 套，来自 8 个 5★ 源材质）**：
- `gunmetal_pro`：gunmetal 壳 (0.27,0.28,0.30) + black_plastic 帽/握把 + white_cartridge 筒 + label_blue 标 + bright_steel rod/钩（A 族 parent A / closed / ring 原色）。
- `red_consumer`：frame_red 壳 (0.84,0.15,0.15) + cartridge_blue 筒 (0.32,0.42,0.52) + collar_red + nozzle_white + steel rod（B 族 parent B / pistol 原色）。
- `blue_silicone`：同 red_consumer 但壳改深灰、突出 cartridge_blue 硅胶筒身份（dgrip/ribframe 变体语义）。
- `aluminum_sausage`：aluminum 筒 (0.68,0.70,0.72) + dark_steel front_cone (0.35,0.36,0.38) + black_plastic 帽 + white_tip（sausage 原色，bulk gun 身份）。
- `industrial_grey`：frame_red→handle_grey (0.42,0.43,0.45) 工业灰 + steel rod + nozzle_white（inline 变体的灰握把语义）。

## Multiplicity / Copy Logic

**1 根 module-local multiplicity 轴**（rib_cage 候选专属，**非小类级轴**）：

- **count_param**：`rib_count`（模板内变量 N / N_RODS；rib_cage cradle 内沿下圆周等角发射的 rib 杆数）。**仅当 cradle=rib_cage 时存在**；其它 4 个 cradle 候选无此轴。
- **N_range**：声明产品域 **[3, 6]**（开放 rod 笼现实上 3-6 根 rib 覆盖真实形态：3 根三角笼 / 4 根基线 / 5-6 根密笼；source map 建议 [3,6]，与样本基线 N_RODS=4 一致，N=3 与 N=6 由 `_rib_rod_geometry` 共享 helper + for-loop 自然外推）。`config_from_seed` 的 sweep 采样域 **[3, 6]**（偏小加权：N=4 高频、N=3/5 常见、N=6 长尾）。
- **sampling domain**：仅 cradle=rib_cage 时 `rng.choices((3,4,5,6), weights=偏中小)`；`resolve_config` 把任意外部 config 的 N clamp 到 [3,6]。非 rib_cage 时不采 N、不编 slot_choice。
- **copied object**：单根 rib 杆 `rib_rod_{i}`——共享 `_rib_rod_geometry(angle_rad)` helper（thin cylinder 沿 barrel 轴），N 个 visual 复用同一几何生成器（仅 angle 参数不同）。
- **naming**：`rib_rod_{i}`，`for i in range(N)`（ribframe L346-354 已用此结构，可直接作 copy-logic 源）。
- **placement**：沿下圆周 **绝对式**等角分布——`angle_deg = ROD_ARC_START + i·(ROD_ARC_END−ROD_ARC_START)/max(N−1,1)`（ribframe L347-349 范式，ARC 210°→330° 下 120° 弧），每个 i 的角由 N 与弧端解析、不累加漂移 → N-不变前提。
- **joint policy**：rib 杆是**非移动件**（Rule 1）→ 作 `frame` 的 root visual，**不发射独立 joint**；活动关节仍由 plunger（PRISMATIC）+ trigger（REVOLUTE）提供，与 rib_count 正交。
- **source/gating**：copy-logic 源取 ribframe L346-354 的 `for i in range(N_RODS)` 循环 + L70-82 共享 helper；**N=4 即样本基线**。rib_cage 与 grip/plunger 的兼容见 §9（rib_cage 为 B 族 frame，默认配 B 族 grip + B 族 plunger）。

> 注：inline_handle 的 `for i in range(4)` `rivet_{i}`（顶轨铆钉装饰）是固定 N=4 的 module-local visual 复制（非可变 count 轴、非移动件），按 Rule 1 inline 为 frame visual，不暴露为 multiplicity 轴。

## 拓扑多样性审计

总组合数（离散槽 + multiplicity，**受 §9 兼容矩阵约束**）：
- 朴素笛卡尔积 = cradle(5) × grip(4) × plunger_drive(3) = **60**（source map combo 预审）。
- 叠 rib_count：仅 cradle=rib_cage 的格子展开 N∈{3,4,5,6}（×4），其余 cradle 不展开 → 合法组合 = `4 cradle × (grip × plunger 合法组合) + 1 rib_cage × (grip × plunger 合法组合) × 4 (N)`。
- 经 §9 兼容矩阵（同族优先 + 跨族 trigger-pivot 统一化），合法组合数仍 **≥ 40**（远超 ≥10 门控）。

仅 cradle(5) × plunger_drive(3) = **15** 已含 5 种主壳 × 3 种尾端的 joint-拓扑无关结构差异；叠 grip(4，含 4 种 trigger pivot 锚点拓扑：后高位 / 前下低位 / 环内低位 / 顶上挑）→ ≥40 ≥ 10 稳过。

理由：cradle(5 种 root 主壳几何 + cartridge/front_cap 承载差异) × grip(4 种 trigger pivot 锚点位置 + trigger 形态拓扑) × plunger_drive(3 种尾端 visual + 行程) 提供充裕真实结构差异；rib_count 在 rib_cage 格子内再 ×4。**rib_count 必须编入 `slot_choices_for_seed` 的 tuple**（`("rib_count", f"n{N}")`，仅 rib_cage 时），否则 rib_cage 的多 rib 拓扑维度损失（对齐 cushion pan_count / fence_cascade 范式）。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` cradle，再经兼容矩阵 `rng.choice` 合法 grip + 合法 plunger_drive（同族优先 / 跨族统一化），若 cradle=rib_cage 再 `rng.choices` 加权 N∈[3,6]，再 uniform 各连续 scale（解析 conditional：plunger_travel 按 plunger 族、grip_drop 仅 pistol/dring、rib_thickness 仅 rib_cage）。compatibility matrix 排除 / 降级非法组合（见下表）。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9。


Controlled local parameterization：见 §参数表的 barrel_len_scale / barrel_girth_scale / plunger_travel_scale（conditional@plunger 族）/ trigger_open_angle_scale / grip_drop_scale（conditional@pistol/dring）/ rib_thickness_scale（conditional@rib_cage）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（cradle→grip→plunger，经兼容矩阵）+（rib_cage 时）N（解析 conditional 范围）→ 采 independent barrel_len/girth/trigger_angle scale → 派生 cartridge 长随 barrel_len（equation）→ 用四条 clearance inequality（cartridge 坐入、plunger 行程+rod 穿 bore、trigger 不穿 grip/cartridge、rib 不互撞）投影 / 回缩。跨部件依赖显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 pivot/bore origin、captured-pin/shaft 接口、rib 复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` cradle，经兼容矩阵 `rng.choice` 合法 grip + plunger，rib_cage 时 `rng.choices` 加权 N∈[3,6]，再 uniform 各 scale | slot_choices_for_seed 含 `("cradle",..),("grip",..),("plunger_drive",..)` 且 rib_cage 时含 `("rib_count",f"n{N}")`，与 build 一致 |
| compatibility matrix | (1) **坐标族优先**：A 族 cradle(half_barrel/closed_barrel/sausage_tube) 默认配 A 族 grip(bracket_wing) + A 族 plunger(ratchet_jhook/ring_pull，rod-local frame, upper≈0.060)；B 族 cradle(skeleton_halfpipe/rib_cage) 默认配 B 族 grip(pistol/dring/inline) + B 族 plunger(thumb_plate，世界 frame, upper≈0.180)。同族组合零风险。 (2) **跨族 trigger-pivot 统一化**：若采样跨族（如 closed_barrel + pistol_grip），trigger pivot origin 必须按所选 grip 的锚点公式重解析到当前 cradle 的坐标族（A 族 lift=AXIS_Z 偏移 / B 族 z=0），并重投影 `fail_if_articulation_origin_far_from_geometry`（0.015）—— 模板需把 grip 的 pivot 高度表达为相对 barrel 轴的偏移而非绝对 z，跨族才安全；首版可 **gate 为同族优先**（跨族仅在 pivot 统一化实现后开放）。 (3) **sausage_tube × plunger**：sausage 用 front_cap 承载 nozzle、装软 pack，push disc 直接顶 barrel bore（ROD_PUSH_R=TUBE_R 密封），三种尾端均可（jhook/thumb/ring）；ring/jhook 优先（A 族原生）。 (4) **inline_handle × plunger**：inline 是顶上挑 thumb trigger，与所有 plunger 正交（rod 仍轴向）。 (5) **rib_cage**：N∈[3,6]，rib_thickness clamp 防互撞；rib_cage 仅 B 族 grip + thumb_plate（B 族原生，避免跨族 pivot 复杂度，首版 gate）。 | 无 floating / collision / trigger 穿 grip 或 cartridge / plunger 满行程脱 bore / rib 互撞 / 跨族 pivot origin 漂移 |
| controlled local variation | 6 个 clamped scale（barrel_len/girth、plunger_travel@族、trigger_angle、grip_drop@pistol/dring、rib_thickness@rib_cage），每 build 统一；travel/grip_drop/rib_thickness 为 conditional | 比例变化不破坏 pivot/bore origin、captured 接口、trigger 净空、cartridge 坐入、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 cradle/grip/drive QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| cradle | 5 | yes | yes | half_barrel/closed/sausage(A 族) + halfpipe/rib_cage(B 族)，5 种主壳 + cartridge 封装 |
| grip | 4 | yes | yes | bracket_wing(A) / pistol/dring/inline(B)，4 种 trigger pivot 锚点拓扑 |
| plunger_drive | 3 | yes | yes | jhook/ring(A,短行程) / thumb(B,长行程)，3 种尾端 visual |
| rib_count (N) | 4（采样域 {3,4,5,6}，仅 rib_cage）| yes | yes | module-local multiplicity，rib_cage 格子内编入 slot_choice |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名（cradle / grip / plunger_drive），rib_cage 时含 `("rib_count", f"n{N}")`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling，rib_count 采样域 ⊆ [3,6]（仅 rib_cage）
- `resolve_config` 把 rib_count clamp 到 [3,6]、各 scale clamp 到声明范围；plunger_travel/grip_drop/rib_thickness 为 conditional 随 plunger 族 / grip / cradle 解析；四条 clearance inequality 在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（坐标族优先；跨族 trigger-pivot 统一化或 gate 同族；rib_cage 限 B 族 grip+thumb；sausage 用 front_cap 承载）
- 连续 scale clamp 后不破坏 pivot/bore origin / captured-pin/shaft 接口 / trigger 净空 / cartridge 坐入 / rib 复制
- 关键 joint：plunger `plunger_drive`/`frame_to_plunger` PRISMATIC axis≈(1,0,0)；trigger `trigger_pivot`/`frame_to_trigger` REVOLUTE axis≈(0,1,0)；cartridge `cartridge_seat`/`frame_to_cartridge` FIXED（sausage 用 `front_cap_seat` FIXED）
- captured-shaft / pin / seated：element-scoped `allow_overlap`（plunger_rod↔rear_cap/plate bore；trigger_blade↔pivot_pin；trigger_blade↔handle_frame/frame_shell lugs；cartridge↔cradle shell；sausage front_cone↔barrel_tube 螺纹），照搬各样本 run_tests 的 allow_overlap + expect_overlap/expect_within/expect_contact 段
- copied object 遵循 `rib_rod_{i}` 命名 + 绝对式等角 placement + Rule 1（无独立 joint）
- grandfather：所有 hinge/shaft/seated captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- 把 rib_count 当普通 int 参数、不进 slot_choice（rib_cage 时）→ 单 rib 数与多 rib 数 slot_choice 同形，损失拓扑维度。
- 跨族组合（如 closed_barrel + pistol_grip）未统一化 trigger pivot origin → pivot 落在错误 z（A 族 lift 偏移 vs B 族 z=0），`fail_if_articulation_origin_far_from_geometry`（0.015）FAIL；必须按 grip 锚点公式重解析到当前 cradle 坐标族，或首版 gate 同族。
- 把 cartridge / front_cap / rib_rod / grip_wing / dring_loop / rivet 当独立活动 part 加 joint → 违反 Rule 1（cartridge 是 FIXED consumable、rib/wing/loop/rivet 是非移动 visual）。
- trigger / plunger rest pose 设成开 / 推出而非 q=0 → current-pose 与 viewer 目检不符（所有样本 lower=0 闭合 / 坐底）。
- plunger 满行程后 push disc 脱出 cartridge 或 rod 脱出 rear cap bore → §7 第二条不等式 FAIL；须回缩 travel。
- trigger 满 squeeze 穿过 grip_wing / cartridge → §7 第三条不等式 FAIL；须回缩 trigger_open_angle（bracket_wing 照搬 A "blade clears grip_wing" L781）。
- 给 captured-shaft / pin / seated 接口补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质（palette_style / barrel scale）当新 candidate 塞进 slot → 不是结构差异。
- 把**热熔胶枪**语义混入（电热熔棒 / 电源 rocker / chrome 锥嘴 / 胶棒后送）→ 出类，本类是手动 cartridge 密封胶枪（003.png parent 已排除）。
- 把**黄油枪加压泵 / 软管 / 注油直嘴**混入致出 caulking 身份 → 拒绝。

## 与相邻类别的边界

- 不该混入：**热熔胶枪（hot glue gun）**——电加热 + 胶棒后送 + 电源开关 + chrome 锥嘴，无 cartridge 夹持架 + squeeze-ratchet plunger；source map 003.png parent 已排除，不作 fork 源、不入采样域。
- 不该混入：**黄油枪（grease gun）**——加压注油枪管 + 杠杆/气动泵 + 软管/直嘴；若仍读作 caulking（cradle + 锥嘴 + squeeze trigger + plunger rod）可勉强归入，但出现软管接头 / 加压泵即出类。
- 不该混入：**注射器 / 电动挤胶枪 / 一次性胶枪**——无可换 cartridge 夹持 + 手动 squeeze trigger + ratchet rod 这套挤出身份。
- Handtools 大类内：区别于无"筒装挤出 + squeeze + plunger"身份的其它手动工具（钳 / 锤 / 螺丝刀 / 扳手）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) 两坐标族（A=barrel_body+lift+后高位 trigger / B=frame+z=0+前下/顶 trigger）的兼容矩阵策略——首版 gate "同族优先"（跨族需 trigger-pivot 统一化）是否接受，还是要求一开始就实现跨族 pivot 重解析以拉满 60 组合；(2) rib_count N_range 取 [3,6]（含基线 4，N=3/6 由共享 helper 外推）是否接受；(3) rib_cage 首版 gate 为 B 族 grip+thumb_plate（避免跨族 pivot 复杂度）是否接受；(4) sausage_tube 用 front_cap part 替代 rigid cartridge（cartridge↔front_cap 承载替换，非额外 slot）是否符合 cradle slot 抽象；(5) Topology target ~40-50 <300 的说明是否接受（兼容矩阵收窄 + 手动工具真实结构上限）；(6) palette_style 5 套 colorway 是否覆盖足够。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：cradle mesh 按族分（A 族 `_barrel_cradle`/`_barrel_tube`(closed)/`_barrel_tube`(revolve, sausage)；B 族 `_build_cradle`(half-pipe)/`_rib_rod_geometry`+for-loop(rib_cage)）；`_front_collar`/`_build_front_ring`(bored)、`_rear_cap`/`_build_rear_plate`(bored)、`_front_cone_cap`(sausage 旋盖)；grip 按候选分（`_handle_frame`+`_grip_wing` / `_build_grip` / `_build_dring_loop`(tube_from_spline_points) / `_build_d_handle`）；plunger 按候选分（`_plunger_rod`+`_hook_handle` / `_build_plunger_mesh`(thumb) / `_ring_handle`(torus)）；trigger 按 grip 族分（`_trigger_blade`(A 后挂) / `_build_trigger_mesh`(B 下垂 / inline 上挑)）。rib_rod N 复制复用同一 `_rib_rod_geometry`。
- captured 接口 allow_overlap：`run_caulking_gun_tests` 里逐组合补 element-scoped `allow_overlap`（plunger_rod↔rear_cap/plate bore；push disc↔cartridge/barrel_tube；trigger_blade↔pivot_pin + ↔handle_frame/frame_shell；cartridge↔cradle shell；sausage front_cone↔barrel_tube），照搬各样本 run_tests 段（A L816-869、B L470-514、sausage L727-805、ribframe L489-577、dgrip L500-575、ringpull L806-859）+ expect_overlap/expect_within/expect_contact。
- 坐标统一化（**最关键实现点**）：把每个 grip 的 trigger pivot 高度表达为**相对 barrel 轴的偏移**（bracket_wing=+PIVOT_Z 上、pistol/dring=-PIVOT_Z 下、inline=+CRADLE_OUTER_R 上），cradle 决定 AXIS_Z（A 族=REAR_CAP_R lift / B 族=0），trigger origin = (pivot_x, 0, AXIS_Z + offset)；这样跨族组合的 pivot 仍落真实硬件面（≤0.015）。首版若 gate 同族，可直接照搬各样本绝对 origin。
- conditional 范围解析顺序：先采 cradle → 经兼容矩阵采 grip / plunger（解析坐标族）→ rib_cage 时采 N → 解析 plunger_travel（按 plunger 族 0.060/0.180）/ grip_drop（仅 pistol/dring）/ rib_thickness（仅 rib_cage）→ 采 barrel_len/girth/trigger_angle independent → 派生 cartridge 长 → 投影四条 clearance inequality。
- 参考模板：`agent/templates/Stationary_Pen.py`（同为 root body + parallel/serial children：actuation 互斥主机构 + tip + clip + grip multiplicity；caulking_gun 的 cradle/grip/plunger 三 slot + rib_count 可同构改编 pen 的 actuation/tip/clip + grip_rib）；`agent/templates/Accessories_Cushion.py`（mixed pattern：固定 named slots + `("count",f"n{N}")` 进 slot_choice + 绝对式 placement + 兼容矩阵 gating + captured allow_overlap 骨架）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C（A 族 parent 基线）| half_barrel + bracket_wing + ratchet_jhook | rec_..._caul_..._24ba16de | `_barrel_cradle` L164-188 / `_handle_frame` L226-296 / `_grip_wing` L310-329 / `_plunger_rod`+`_hook_handle` L421-481 / joints L632-666 / allow_overlap L816-869 | A 族 cradle/grip/plunger 基线 + 后高位 trigger + captured-pin/shaft 范式 |
| S2 | A/B/C（B 族 parent 基线）| skeleton_halfpipe + pistol_grip + thumb_plate | rec_..._caul_..._ff090a9c | `_build_cradle` L66-85 / `_build_grip` L112-133 / `_build_pivot_lugs` L136-174 / `_build_plunger_mesh` L298-326 / joints L352-391 / allow_overlap L470-514 | B 族 cradle/grip/plunger 基线 + 前下低位 trigger + nested-consumable 范式 |
| S3 | A | closed_barrel | rec_caulk_var_closedbarrel | `_barrel_tube`(closed+slot) L169-198 / expect_within/extends-above L728-751 | 全闭合圆筒 cradle + 全包封检查 |
| S4 | A | sausage_tube | rec_caulk_var_sausage | `_barrel_tube`(revolve) L145-163 / `_front_cone_cap` L166-198 / front_cap part L471-486 / front_cap_seat L513-519 | lathe revolve 筒 + 螺纹旋盖 front_cap（替代 rigid cartridge）|
| S5 | A（multiplicity）| rib_cage + rib_count | rec_caulk_var_ribframe | `_rib_rod_geometry` L70-82 / `for i in range(N_RODS)` L346-354 / `_build_spine_rail` L112-124 | 开放 rod 笼 + rib_count copy-logic 源（共享 helper + 等角 for-loop + 底脊承载）|
| S6 | B | d_ring_loop | rec_caulk_var_dgrip | `_build_dring_loop`(tube_from_spline_points) L128-139 / `_build_dring_bosses` L142-162 / trigger-in-loop 检 L487-497 | 闭合 D 环 round-bar grip（trigger 在环内）|
| S7 | B | inline_handle | rec_caulking_gun_var_inlinehandle | `_build_d_handle` L124-182 / `_build_pivot_lugs`(顶上挑) L185-226 / `_build_trigger_mesh`(thumb) L321-361 | 轴向矩形 D-handle + 顶上挑 thumb trigger |
| S8 | C | ring_pull | rec_caulking_gun_var_ringpull | `_ring_handle`(torus revolve) L441-466 / ring closed-loop 检 L707-744 | 尾端闭合拉环（torus）plunger 尾 |
