# coffee_machine (upright espresso / coffee machine) — Modular Spec

> 来源小类：`picture/Kitchen/Coffee machine`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Kitchen__Coffee_machine.md`。
> **"Coffee machine" 在此 = 立式咖啡 / 浓缩咖啡机（upright espresso / bean-to-cup / pod machine），不是电热水壶 kettle、台式饮水机 / 直饮机 water dispenser、也不是滴滤壶 drip coffee carafe。**
> 结构家族 = 立式机身：一只 `body` root（base block / `core_shell` / 倾斜 `fascia_panel` / `top_deck`）+ 旋钮 `selection_dial`（CONTINUOUS，轴垂直于 15° 倾斜 fascia）+ `drip_tray`（PRISMATIC 前滑 +X）；super-automatic spine 上 `spout_block`（PRISMATIC 竖直下降）与 `steam_wand`（REVOLUTE）也属共享核心。三个独立结构槽：brew type（出咖前端）/ bean-hopper lid（豆斗盖）/ water tank（水箱）。
>
> **同步状态**：本 spec 引用的 7 个 5 星样本（1 个 parent + 6 个 fork 槽位变体）**已同步进本仓库 `data/records/<id>/`，rating=5**。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一逐行核对）。引用以 part / joint / helper **名字** 为准（`body`/`spout_block`/`drip_tray`/`steam_wand`/`hopper_lid`/`group_head`/`portafilter`/`capsule_flap`/`hopper_canister`/`water_tank` part；`fascia_to_dial`/`body_to_spout`/`body_to_tray`/`body_to_wand`/`deck_to_hopper_lid`/`body_to_group_head`/`body_to_portafilter`/`body_to_flap`/`body_to_hopper`/`body_to_tank` joint；`fascia_point` helper），行号仅作定位。
>
> **整机 spine 注记（重要，来自 source map）**：`super_automatic` 与 `portafilter` / `pod_capsule` 不是单层 diff。`pod_capsule` 是更大的整机 re-body（紧凑 `body_shell` ExtrudeGeometry、单 chrome 出咖嘴、顶部 capsule flap、机身集成 `water_tank` 视觉），**自带它专属的 Slot B（`capsule_flap` 顶翻盖）与 Slot C（机身集成 `water_tank` 视觉）默认值**；`portafilter` **删除了豆斗（无 hopper_lid）**，用预磨咖啡粉。因此 brew type 不是与 hopper / tank 完全正交的槽——它是携带各自 Slot B/C 默认的"整机 spine"，兼容矩阵必须把 pod / portafilter 的 hopper / tank 组合分别处理（见 §9）。

## 元信息
| 项 | 值 |
|---|---|
| slug | `coffee_machine` |
| template path | `agent/templates/Kitchen_Coffee_machine.py` |
| test path (optional) | `tests/agent/test_coffee_machine_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 root `body` + 三个并行替换层：brew_type / hopper_lid / water_tank，各自挂 `body`；共享 `selection_dial` CONTINUOUS + `drip_tray` PRISMATIC + super-automatic spine 上的 `spout_block` PRISMATIC + `steam_wand` REVOLUTE 也挂 `body`）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7（1 parent + 6 fork 槽位变体；均 converged、compile success、≥1 非 fixed joint、workbench-only，rating=5）|
| read_count | 7（**全部读完整 `model.py`**，不抽样；含每个样本的 dimensions / build helpers / part 树 / articulation 与 run_tests + allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 7/7 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **共享基线拓扑（super-automatic spine：parent + 4 个 fork 变体 hopper/tank 均沿用）**：`body`（root，base block / 侧裙 / `core_shell` / 前 cheeks / `channel_back_wall` / `spout_rail` / 倾斜 `fascia_panel` / `top_deck` / `cup_warming_grid` / 按钮阵列 / `wand_boss`，parent L80-186）+ `selection_dial`（`fascia_to_dial` CONTINUOUS，轴 = fascia 法向，parent L189-233）+ `drip_tray`（`body_to_tray` PRISMATIC +X 0.12 m，parent L262-318）+ `spout_block`（`body_to_spout` PRISMATIC -Z 0.06 m，parent L236-259）+ `steam_wand`（`body_to_wand` REVOLUTE 竖直轴 ~60°，parent L321-359）。`fascia_to_dial` CONTINUOUS 单独即保证 ≥1 非 fixed joint（即使某 slot 机构是 FIXED）。
- **Slot A brew type 轴**：是机身 spine / part 数 / joint 拓扑变化（**broader re-body**，非单层）。
  - `super_automatic`（parent）：`spout_block` 独立 part（双嘴 `left_nozzle`/`right_nozzle` 沿 `spout_rail` 竖直 **PRISMATIC** 下降，L236-259）；豆斗 + 水箱用各自 Slot B/C 候选；保留 spout + dial + tray + wand。
  - `portafilter`：`group_head` 独立 part（`gh_lock_ring`/`gh_body`/`gh_flange` 黄铜，`body_to_group_head` **FIXED**，L246-275）+ `portafilter` 独立 part（`pf_basket`/`pf_rim`/`pf_ear_{i}`/`pf_handle_*`，`body_to_portafilter` **FIXED**，L278-330）；body 加 `group_mount_boss`（L192-197）；**spout_block 删除、hopper_lid 删除**（run_tests 显式断言 L449-466）；保留 dial + tray + wand。
  - `pod_capsule`：整机 re-body——`body_shell` 用 `rounded_rect_profile` + `ExtrudeGeometry`（圆角紧凑机身，L64-70）+ 单 chrome `single_spout`/`spout_tip`（L97-109）+ 顶部 `capsule_slot`（L112-117）+ **机身集成 `water_tank` 视觉**（L120-125）+ `capsule_flap` part（`flap_plate`/`flap_grip`/`flap_hinge_pin`，`body_to_flap` **REVOLUTE** -Y 顶后铰，L207-243）+ `control_dial` CONTINUOUS（L155-204）+ `drip_tray` PRISMATIC（L246-312，0.08 m）。机身更小（W 0.14 / D 0.28 / H 0.30），**无 steam_wand、无独立 hopper、无独立可拆 tank**。
- **Slot B bean-hopper lid 轴**（仅 super-automatic spine 有；pod 自带 `capsule_flap` 作其 Slot B 默认；portafilter 无豆斗）：是 part 数 / joint 拓扑 / 轴变化。
  - `rear_hinge`（parent）：`hopper_lid`（`lid_plate`/`lid_grip_bar`）`deck_to_hopper_lid` **REVOLUTE** axis=(0,-1,0) 后缘翻盖 ~100°（parent L362-384）。
  - `side_hinge`：同一 lid plate 但 `deck_to_hopper_lid` **REVOLUTE** axis=(0,0,+1) 竖直铰，左侧缘 `LID_HINGE_X/Y/Z` 侧开 ~100°（side_hinge L361-392）。
  - `removable_canister`：`hopper_canister` 独立 part（`canister_shell` CadQuery hollow shell + `canister_lid_plate`/`canister_grip`/`canister_align_rib`，`body_to_hopper` **PRISMATIC** +Z 0.10 m，removable L403-455）；body 加 4 壁 guide bay（`hopper_guide_front/rear/left/right` + `hopper_bay_floor`，removable L201-226）。
- **Slot C water tank 轴**（super-automatic spine 有真实三候选；pod 自带机身集成 tank 视觉作其 Slot C 默认；portafilter 沿用 super-automatic 的 tank 候选）：是 part 数 / joint 拓扑 / 轴变化。
  - `internal`（parent）：**无独立 tank part**（水箱藏在 `core_shell` 内，无 joint，fold-into-body 默认）。
  - `side_removable`：`water_tank` 独立 part（`tank_body` 半透明 + `tank_cap`/`tank_handle`，`body_to_tank` **PRISMATIC** -Y 0.10 m 侧抽，side_removable L413-445）；body 加 `tank_bay_plate` + `tank_rail_{i}`（右侧 -Y flank，side_removable L199-212）。
  - `top_reservoir`：`water_tank` 独立 part（`tank_vessel` Extrude 圆角矩形 + `tank_water_fill` 可见水位 + `tank_lid`/`tank_grip`，`body_to_tank` **PRISMATIC** +Z 0.15 m 后部竖直提起，top_reservoir L416-464）；body 加后部 cradle（`tank_bay_platform`/`tank_bay_back_wall`/`tank_bay_left_wall`/`tank_bay_right_wall`，top_reservoir L194-215）。
- **multiplicity**：无可变 multiplicity 轴。fascia 上的 `{tag}_button_{k}`（3 按钮 × 2 侧）是装饰（FIXED visual，无 joint），不构成 multiplicity 轴（见 §8）。

## 核心身份

一只**立式咖啡 / 浓缩咖啡机**（upright espresso / bean-to-cup / pod machine）：一只立式 `body`（root，坐地 z=0；glossy black `core_shell` + base block + 侧裙 + 前出咖凹槽两侧 cheeks + 倾斜 `fascia_panel` 控制面板 + `top_deck` + 杯暖 grid），面板上有旋转 `selection_dial`（轴垂直于倾斜 fascia 的 **CONTINUOUS** 旋钮），底部有可前滑出的 `drip_tray`（**PRISMATIC** +X 接水盘）。出咖前端（Slot A brew type）按机型分三 spine：super-automatic 的双嘴可升降 `spout_block`（**PRISMATIC** -Z 降到杯高）+ `steam_wand`（**REVOLUTE** 蒸汽奶泡棒）；portafilter 的黄铜冲煮头 `group_head` + 可拆带柄 `portafilter`（FIXED）；pod 的紧凑机身 + 单 chrome 出咖嘴 + 顶部 capsule 翻盖。super-automatic spine 顶有豆斗盖（Slot B：后翻 / 侧翻 REVOLUTE / 可拆豆罐 PRISMATIC）与水箱（Slot C：内置无件 / 侧抽 PRISMATIC / 后部提起 PRISMATIC）。默认成熟域 = brew_type × hopper_lid × water_tank 的小型台式咖啡机（super-auto 机身 ~0.43 m 高 / 0.24 m 宽 / 0.35 m 深；pod 机身 ~0.30 m 高 / 0.14 m 宽 / 0.28 m 深）。活动语义 = **旋钮转动**（CONTINUOUS，所有 spine 共享，单独保 ≥1 非 fixed joint）+ **接水盘前滑**（PRISMATIC，所有 spine 共享）+ super-auto 的**出咖嘴升降**（PRISMATIC）/ **蒸汽棒摆动**（REVOLUTE）/ **豆斗盖开合**（REVOLUTE 或 PRISMATIC 提罐）/ **水箱抽出**（PRISMATIC）+ pod 的**capsule 翻盖**（REVOLUTE）。

不该混入：
- **电热水壶 / 烧水壶（kettle）**——只烧水、无冲煮头 / 豆斗 / 出咖嘴 / 旋钮选档；本类是冲煮咖啡的机器（有 brew front end），已有独立 slug `container_kettle`。
- **台式饮水机 / 直饮机 / 净水器（water dispenser）**——出冷热水龙头 + 大水桶 / 滤芯，无咖啡冲煮机构、无 fascia 旋钮选档、无 drip tray + 升降出咖嘴；主功能是配水不是冲咖啡。
- **滴滤咖啡壶 / 法压壶 / 摩卡壶（drip carafe / French press / moka pot）**——是分体壶具 / 手冲器，不是立式带电控制面板的整机；无 fascia + dial + 蒸汽棒 + 升降 spout spine。

## 槽位 + 候选模块表

> **建模注记**：本类三轴**不是完全正交**（区别于 clamp / cushion）。`brew_type`（Slot A）是携带各自 Slot B/C 默认的**整机 spine**：`super_automatic` 是真正暴露 Slot B(3) × Slot C(3) 自由组合的 spine；`pod_capsule` 自带 `capsule_flap`（B 默认）+ 机身集成 `water_tank` 视觉（C 默认）→ 在 pod spine 上 Slot B/C **不另选**（gate 为 spine 默认）；`portafilter` 删除豆斗（无 Slot B）但沿用 super-auto 的 Slot C 三候选（水箱在 portafilter 机上仍是真实可选项）。详见 §9 兼容矩阵与 §7 conditional 解析。

### Slot A：brew type / dispensing front end（出咖前端 —— 决定整机 spine、机身 mesh 与 part / joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| super_automatic（基线）| rec_model-a-delonghi-magnifica-style-super-automatic_...ed06768c（parent）| `spout_block` part + `left_nozzle`/`right_nozzle` L236-249 / `body_to_spout` **PRISMATIC** axis=(0,0,-1) 0.06 m L250-259 / `spout_rail` body visual L120-125 / `steam_wand` + `body_to_wand` **REVOLUTE** 竖直轴 ~60° L321-359 / `wand_boss` L181-186 | eligible if compatible | 双嘴升降出咖块沿竖直 `spout_rail` 下降到杯高（bean-to-cup）+ 蒸汽奶泡棒；机身 box 拼装（W 0.24 / D 0.35 / H 0.43）；**暴露 Slot B(3) × Slot C(3) 自由组合**；保留 spout + wand + dial + tray |
| portafilter | rec_coffee_machine_var_brew_portafilter | `group_head` part（`gh_lock_ring`/`gh_body`/`gh_flange` brass）+ `body_to_group_head` **FIXED** L246-275 / `portafilter` part（`pf_basket`/`pf_rim`/`pf_ear_{i}`/`pf_handle_lug`/`pf_handle_shaft`/`pf_handle_grip`）+ `body_to_portafilter` **FIXED** L278-330 / `group_mount_boss` body visual L192-197 / 矮 cheeks L119-125 | eligible if compatible | 圆柱黄铜冲煮头 + 可拆带侧柄 portafilter（两 FIXED）；**spout_block 删除、hopper_lid 删除**（用预磨粉，无豆斗；run_tests 断言 L449-466）；保留 dial + tray + wand；**无 Slot B**，沿用 Slot C 三候选 |
| pod_capsule | rec_coffee_machine_var_brew_pod | `body_shell` `rounded_rect_profile`+`ExtrudeGeometry` L64-70 / `single_spout`/`spout_tip` chrome L97-109 / `capsule_slot` L112-117 / 机身集成 `water_tank` 视觉 L120-125 / `capsule_flap` part（`flap_plate`/`flap_grip`/`flap_hinge_pin`）+ `body_to_flap` **REVOLUTE** axis=(0,-1,0) 顶后铰 ~100° L207-243 / `control_dial` CONTINUOUS L155-204 / `drip_tray` PRISMATIC 0.08 m L246-312 | eligible if compatible | 紧凑 Nespresso 式 pod 机：圆角拉伸机身（W 0.14 / D 0.28 / H 0.30）、单 chrome 出咖嘴、顶部 capsule 翻盖；**整机 re-body，自带 Slot B（capsule_flap）+ Slot C（机身集成 tank 视觉）默认**；无 steam_wand / 无独立可拆 hopper / 无独立可拆 tank |

> 说明（Slot A=3，全 converged）：三候选都是真实 brew-type 结构家族（bean-to-cup 双嘴升降 / 预磨 portafilter 带柄冲煮头 / pod 胶囊翻盖），part 树 / joint 拓扑 / 机身 mesh 均显著不同（升降 PRISMATIC spout vs 两 FIXED brew group vs REVOLUTE 顶翻盖 + 拉伸机身）。pod 的整机 re-body 性质见顶部 spine 注记与 §9。

### Slot B：bean-hopper lid / fill access（顶 deck 后半的豆斗盖 —— 仅 super-automatic spine 暴露三候选）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| rear_hinge（基线）| rec_..._ed06768c（parent）| `hopper_lid` part（`lid_plate`/`lid_grip_bar`）L362-374 / `deck_to_hopper_lid` **REVOLUTE** axis=(0,-1,0) 后缘铰 origin=(X_REAR,0,0.418) ~100° L375-384 | eligible if compatible | 经典后缘翻起盖：lid plate 从后铰沿 +X 延伸，绕 -Y 向上翻开 lower=0 闭合 / upper=LID_OPEN(~1.745) |
| side_hinge | rec_coffee_machine_var_hopper_side_hinge | `hopper_lid` part（同 plate + grip）L369-382 / `deck_to_hopper_lid` **REVOLUTE** axis=(0,0,+1) 左侧缘竖直铰 origin=(LID_HINGE_X=-0.115, LID_HINGE_Y=0.105, 0.418) ~100° L383-392 | eligible if compatible | 同一 lid plate 但绕**竖直 Z 轴**在左侧 flank 侧开（plate 沿 -Y 延伸，grip 在右侧自由缘 L377-382），而非向上翻起 |
| removable_canister | rec_coffee_machine_var_hopper_removable | `hopper_canister` part（`canister_shell` CadQuery hollow shell L406-419 + `canister_lid_plate`/`canister_grip`/`canister_align_rib` L421-443）/ `body_to_hopper` **PRISMATIC** axis=(0,0,1) 0.10 m L445-455 / body 4 壁 guide bay `hopper_guide_{front/rear/left/right}` + `hopper_bay_floor` L201-226 | eligible if compatible | 提出式豆罐替代铰链盖：竖直 **PRISMATIC** +Z 从 guide bay 提起（lower=0 坐底 / upper=0.10）；`canister_align_rib` 坐 `hopper_bay_floor`（captured，allow_overlap L498-504）|

### Slot C：water tank / reservoir mount（水箱 —— super-automatic / portafilter spine 暴露三候选）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| internal（基线）| rec_..._ed06768c（parent）| 无 dedicated tank part（水箱藏在 `core_shell` 内，L98-103）| eligible if compatible | 无独立、无关节水箱——隐藏内置水箱（fold-into-body 默认）；**无独立 part / joint**（Rule 1，水箱 = `core_shell` 内含视觉，不单列）|
| side_removable | rec_coffee_machine_var_tank_side_removable | `water_tank` part（`tank_body` translucent + `tank_cap`/`tank_handle`）L413-434 / `body_to_tank` **PRISMATIC** axis=(0,-1,0) 0.10 m L435-445 / body 右 flank `tank_bay_plate` + `tank_rail_{i}` L199-212 | eligible if compatible | 半透明水箱从右 flank docking bay **侧抽**（-Y，lower=0 坐 / upper=0.10）；`tank_body` 贴 `tank_bay_plate`/`tank_rail_{i}`（captured，allow_overlap L684-704）|
| top_reservoir | rec_coffee_machine_var_tank_top_reservoir | `water_tank` part（`tank_vessel` Extrude 圆角矩形 + `tank_water_fill` 可见水位 + `tank_lid`/`tank_grip`）L416-452 / `body_to_tank` **PRISMATIC** axis=(0,0,1) 0.15 m L453-464 / body 后部 cradle `tank_bay_platform`/`tank_bay_back_wall`/`tank_bay_{left/right}_wall` L194-215 | eligible if compatible | 透明后置水箱（可见水位），从后部 cradle **竖直提起**（+Z，lower=0 坐 / upper=0.15）；`tank_vessel` 坐 `tank_bay_platform`（expect_within/overlap L710-727）|

## 槽位图（slot graph）

pattern: parallel_children（固定 root `body`；`selection_dial` CONTINUOUS + `drip_tray` PRISMATIC 全 spine 共享挂 body；super-auto spine 上 `spout_block` PRISMATIC + `steam_wand` REVOLUTE 也挂 body；三结构槽 brew_type / hopper_lid / water_tank 各自的件按候选挂 body。**Slot A=brew_type 是整机 spine，决定 Slot B/C 是否暴露——非纯正交**）

```
body (root, 坐地 z=0; 由 brew_type 决定机身 mesh（box 拼装 / 拉伸圆角紧凑机身）+ fascia + top_deck + 各槽硬件)
  │
  ├── selection_dial ──[fascia_to_dial / body_to_dial: CONTINUOUS axis=fascia 法向]   ← 全 spine 共享；单独保 ≥1 非 fixed joint
  │
  ├── drip_tray ──[body_to_tray: PRISMATIC axis=(1,0,0), 前滑 +X 0.08–0.12 m]          ← 全 spine 共享
  │
  ├── [Slot A = brew_type spine]  (互斥三选一; 决定 spine + 下游槽暴露)
  │     ├─ super_automatic : spout_block ──[body_to_spout: PRISMATIC axis=(0,0,-1) 0.06 m, origin 顶, captured on spout_rail]
  │     │                    steam_wand  ──[body_to_wand:  REVOLUTE axis=(0,0,-1) ~60°, origin=wand_boss 侧轴]
  │     │                    → 暴露 Slot B(3) × Slot C(3)
  │     ├─ portafilter     : group_head  ──[body_to_group_head: FIXED, origin 前凹槽]
  │     │                    portafilter ──[body_to_portafilter: FIXED, docked 在 group_head 下]
  │     │                    → 无 Slot B（删豆斗）; 暴露 Slot C(3); spout_block / hopper_lid 删除
  │     └─ pod_capsule     : capsule_flap ─[body_to_flap: REVOLUTE axis=(0,-1,0) 顶后铰 ~100°]
  │                          single_spout/spout_tip (body visual); 机身集成 water_tank (body visual)
  │                          → Slot B 固定 = capsule_flap; Slot C 固定 = 机身集成 tank 视觉; 无 steam_wand
  │
  ├── [Slot B = hopper_lid slot]  (仅 super_automatic spine; 互斥三选一)
  │     ├─ rear_hinge        : hopper_lid ──[deck_to_hopper_lid: REVOLUTE axis=(0,-1,0), origin=(X_REAR,0,0.418) 后缘铰线]
  │     ├─ side_hinge        : hopper_lid ──[deck_to_hopper_lid: REVOLUTE axis=(0,0,+1), origin=(LID_HINGE_X,LID_HINGE_Y,0.418) 左侧竖直铰]
  │     └─ removable_canister: hopper_canister ─[body_to_hopper: PRISMATIC axis=(0,0,1) 0.10 m, origin=(HOPPER_CENTER_X,0,DECK_TOP_Z) guide bay 底]
  │
  └── [Slot C = water_tank slot]  (super_automatic / portafilter spine; 三选一)
        ├─ internal       : (无独立 tank part, 藏 core_shell 内, 无 joint)
        ├─ side_removable : water_tank ──[body_to_tank: PRISMATIC axis=(0,-1,0) 0.10 m, origin=(TANK_X_C,TANK_DOCK_Y,TANK_Z_C) 右 flank dock 面]
        └─ top_reservoir  : water_tank ──[body_to_tank: PRISMATIC axis=(0,0,1) 0.15 m, origin=(-0.210,0,0.418) 后 cradle 底]
```

接口点位与 joint 语义：
- **body → selection_dial（全 spine 共享）**：mating = 倾斜 fascia 法向。super-auto `fascia_to_dial` CONTINUOUS，origin=`fascia_point(0.005,0,0)`，axis 经 rpy=(0,π/2−TILT,0) 映射到 fascia 法向（parent L222-233）；pod `body_to_dial` CONTINUOUS，origin=(X_FRONT+0.001,0,0.20) rpy=(0,π/2,0)，axis 映射到前面法向 +X（pod L196-204）。`dial_stem` 插入 fascia / body_shell（captured，allow_overlap parent L406-412 / pod L330-343）。`dial_pointer` 离轴 → run_tests 验半周扫到对侧（parent L604-616）。
- **body → drip_tray（全 spine 共享）**：mating = base block 前接水盘 bay。`body_to_tray` PRISMATIC axis=(1,0,0)，origin=(0,0,0)（super-auto，parent L310-318）或 (X_FRONT−0.12,0,0.015)（pod L304-312）；lower=0 docked / upper=TRAY_TRAVEL（0.12 super-auto / 0.08 pod）。
- **body → spout_block（仅 super_automatic）**：mating = `spout_rail` 竖直导轨。`body_to_spout` PRISMATIC axis=(0,0,-1)（正 q 下降到杯高），origin=(0.146,0,0.250)，lower=0 顶 / upper=0.06（parent L250-259）；`spout_housing` captured 在 `spout_rail`（allow_overlap parent L418-419，expect_overlap z≥0.05 L515-523）。
- **body → steam_wand（仅 super_automatic）**：mating = 左 flank `wand_boss`。`body_to_wand` REVOLUTE axis=(0,0,-1)（竖直，正 q 向前摆），origin=(0.085,0.138,0.285)，lower=0 / upper=WAND_SWING(~1.047)（parent L350-359）；`pivot_knuckle` captured 在 `wand_boss`（allow_overlap parent L420-426）。
- **body → group_head / portafilter（仅 portafilter）**：两 **FIXED**。`body_to_group_head` origin=(GH_X=0.155,0,GH_Z=0.185)（L269-275）；`body_to_portafilter` origin=(0.155,0,PF_Z=0.176)（L324-330）。`group_head` 坐 `group_mount_boss`（allow_overlap L479-483），`portafilter` rim/ears 嵌 `gh_lock_ring`（allow_overlap L485-495）。FIXED 件靠 dial CONTINUOUS 保 ≥1 非 fixed。
- **body → capsule_flap（仅 pod）**：mating = 顶后缘 `flap_hinge_boss`。`body_to_flap` REVOLUTE axis=(0,-1,0)，origin=(X_REAR,0,DECK_TOP)，lower=0 闭合 / upper=FLAP_OPEN(~1.745)（pod L235-243）；`flap_hinge_pin` captured 在 `flap_hinge_boss`（allow_overlap pod L344-357）。
- **body → hopper_lid（仅 super_automatic; 互斥）**：rear_hinge `deck_to_hopper_lid` REVOLUTE axis=(0,-1,0) origin=(X_REAR,0,0.418)（parent L375-384）；side_hinge 同名 joint REVOLUTE axis=(0,0,+1) origin=(LID_HINGE_X,LID_HINGE_Y,0.418)（side_hinge L383-392）；removable `body_to_hopper` PRISMATIC axis=(0,0,1) origin=(HOPPER_CENTER_X,0,DECK_TOP_Z)（removable L445-455），canister 坐 guide bay floor（allow_overlap L498-504）。
- **body → water_tank（super_automatic / portafilter; 互斥）**：internal 无 joint（隐藏内置，Rule 1）；side_removable `body_to_tank` PRISMATIC axis=(0,-1,0) origin=(TANK_X_C,TANK_DOCK_Y,TANK_Z_C)（side_removable L435-445），tank 贴 bay plate/rails（allow_overlap L684-704）；top_reservoir `body_to_tank` PRISMATIC axis=(0,0,1) origin=(-0.210,0,0.418)（top_reservoir L453-464），vessel 坐 cradle platform（expect_within/overlap L710-727）。
- **mating policy**：所有接口是 captured-fit（dial stem 插 fascia、spout housing 嵌 rail、wand knuckle 嵌 boss、flap pin 嵌 boss、canister rib 坐 bay floor、tank body 贴 rail / cradle、portafilter rim 嵌 lock ring）—— 非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：dial q=0；tray q=0 docked；spout q=0 顶（喷嘴悬杯上方）；wand q=0；hopper lid / capsule flap q=0 闭合（盖坐 top_deck，parent expect_contact L495-502 / pod L415-421）；canister / tank q=0 坐底。
- **互斥 / 可选 / 派生**：brew_type 三 spine 互斥（决定下游槽暴露）；hopper_lid 三候选互斥（仅 super-auto）；water_tank 三候选互斥（super-auto / portafilter）；pod 的 Slot B/C 固定为 spine 默认（不另选）；portafilter 无 Slot B。

## 每槽位 Module Emits / Interfaces

### Slot A / brew_type — super_automatic（含共享核心 body / dial / tray）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（root，visual：base_block / 侧裙 / `core_shell` / `{tag}_front_cheek` / `channel_back_wall` / `spout_rail` / `fascia_panel` / `top_deck` / `cup_warming_grid` / 按钮阵列 / `power_button` / `brand_badge` / `wand_boss`）+ `selection_dial` + `drip_tray` + `spout_block` + `steam_wand` | parent body L80-186 / dial L189-233 / tray L262-318 / spout L236-259 / wand L321-359 |
| internal joints | `fascia_to_dial` CONTINUOUS（fascia 法向）+ `body_to_tray` PRISMATIC +X 0.12 + `body_to_spout` PRISMATIC -Z 0.06 + `body_to_wand` REVOLUTE 竖直 ~60° | parent L222-233 / L310-318 / L250-259 / L350-359 |
| upstream interface | root（坐地，无父）| parent L80 |
| downstream interface | 后 deck（供 Slot B hopper_lid）+ 右 flank / 后 cradle 区（供 Slot C water_tank）| parent L134-139 |

### Slot A / brew_type — portafilter
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（同核心但矮 cheeks + 加 `group_mount_boss`，**无 spout_rail 用途**）+ `selection_dial` + `drip_tray` + `steam_wand` + `group_head` + `portafilter` | portafilter body L93-197 / gh L246-275 / pf L278-330 |
| internal joints | `fascia_to_dial` CONTINUOUS + `body_to_tray` PRISMATIC + `body_to_wand` REVOLUTE + `body_to_group_head` **FIXED** + `body_to_portafilter` **FIXED** | portafilter L232-243 / L377-385 / L417-426 / L269-275 / L324-330 |
| upstream interface | root（坐地）；group_head 坐 `group_mount_boss` | portafilter L479-483 |
| downstream interface | 无 Slot B（豆斗删除，run_tests 断言 `hopper_lid` not in parts L449-453）；保留 Slot C water_tank 接口 | portafilter L447-466 |

### Slot A / brew_type — pod_capsule
| emits | 描述 | 来源 |
|---|---|---|
| parts | `body`（紧凑 `body_shell` Extrude + `top_deck` + `front_fascia` + `dispensing_recess` + `single_spout`/`spout_tip` + `capsule_slot` + 机身集成 `water_tank` 视觉 + `base_platform` + `tray_guide_{i}` + `flap_hinge_boss`）+ `control_dial` + `capsule_flap` + `drip_tray` | pod body L61-152 / dial L155-204 / flap L207-243 / tray L246-312 |
| internal joints | `body_to_dial` CONTINUOUS（前面法向 +X）+ `body_to_flap` REVOLUTE -Y 顶后铰 ~100° + `body_to_tray` PRISMATIC +X 0.08 | pod L196-204 / L235-243 / L304-312 |
| upstream interface | root（坐地）| pod L61 |
| downstream interface | Slot B 固定 = `capsule_flap`；Slot C 固定 = 机身集成 `water_tank` 视觉（不暴露独立可拆候选）| pod L120-125, L207-243 |

### Slot B / hopper_lid — rear_hinge
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hopper_lid`（visual：`lid_plate` + `lid_grip_bar`）| parent L362-374 |
| internal joints | `deck_to_hopper_lid` REVOLUTE axis=(0,-1,0)，origin=(X_REAR,0,0.418)，lower=0 / upper=LID_OPEN(~1.745) | parent L375-384 |
| upstream interface | lid plate 坐 `top_deck`（闭合 expect_contact）| parent L495-502 |

### Slot B / hopper_lid — side_hinge
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hopper_lid`（同 plate + grip，plate 沿 -Y 延伸、grip 在右自由缘）| side_hinge L369-382 |
| internal joints | `deck_to_hopper_lid` REVOLUTE axis=(0,0,+1)，origin=(LID_HINGE_X=-0.115, LID_HINGE_Y=0.105, 0.418)，~100° | side_hinge L383-392 |
| upstream interface | lid plate 坐 `top_deck`（闭合 expect_contact，side_hinge L503-510）| side_hinge L503-510 |

### Slot B / hopper_lid — removable_canister
| emits | 描述 | 来源 |
|---|---|---|
| parts | `hopper_canister`（`canister_shell` CadQuery hollow shell + `canister_lid_plate` + `canister_grip` + `canister_align_rib`）；body 加 `hopper_guide_{front/rear/left/right}` + `hopper_bay_floor` | removable canister L403-443 / guide bay L201-226 |
| internal joints | `body_to_hopper` PRISMATIC axis=(0,0,1)，origin=(HOPPER_CENTER_X,0,DECK_TOP_Z)，lower=0 / upper=0.10 | removable L445-455 |
| upstream interface | `canister_align_rib` 坐 `hopper_bay_floor`（captured，allow_overlap）| removable L498-504 |

### Slot C / water_tank — internal
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part（水箱 = `core_shell` 内含视觉，Rule 1）| parent L98-103 |
| internal joints | 无 | — |
| upstream interface | 水箱概念藏 `core_shell` 内（无外露 dock）| parent L98-103 |

### Slot C / water_tank — side_removable
| emits | 描述 | 来源 |
|---|---|---|
| parts | `water_tank`（`tank_body` translucent + `tank_cap` + `tank_handle`）；body 加 `tank_bay_plate` + `tank_rail_{i}`×2 | side_removable tank L413-434 / bay L199-212 |
| internal joints | `body_to_tank` PRISMATIC axis=(0,-1,0)，origin=(TANK_X_C,TANK_DOCK_Y,TANK_Z_C)，lower=0 / upper=0.10 | side_removable L435-445 |
| upstream interface | `tank_body` 贴 `tank_bay_plate`/`tank_rail_{i}`（captured，allow_overlap）| side_removable L684-704 |

### Slot C / water_tank — top_reservoir
| emits | 描述 | 来源 |
|---|---|---|
| parts | `water_tank`（`tank_vessel` Extrude 圆角矩形 + `tank_water_fill` 可见水位 + `tank_lid` + `tank_grip`）；body 加 `tank_bay_platform` + `tank_bay_back_wall` + `tank_bay_{left/right}_wall` | top_reservoir tank L416-452 / cradle L194-215 |
| internal joints | `body_to_tank` PRISMATIC axis=(0,0,1)，origin=(-0.210,0,0.418)，lower=0 / upper=0.15 | top_reservoir L453-464 |
| upstream interface | `tank_vessel` 坐 `tank_bay_platform`（expect_within/overlap）| top_reservoir L710-727 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| brew_type | enum | super_automatic / portafilter / pod_capsule | super_automatic | choice | 由 deterministic procedural sampler 选；决定整机 spine + 机身 mesh + 下游槽暴露（见 §9）| Slot A 表 |
| hopper_lid | enum | rear_hinge / side_hinge / removable_canister | rear_hinge | conditional choice | 仅 brew_type=super_automatic 时采样；portafilter→无（删豆斗）；pod→固定 capsule_flap（spine 默认，不另选）| Slot B 表 |
| water_tank | enum | internal / side_removable / top_reservoir | internal | conditional choice | brew_type∈{super_automatic, portafilter} 时采样；pod→固定机身集成 tank 视觉（spine 默认，不另选）| Slot C 表 |
| palette_style | enum | gloss_black_stainless / matte_graphite / cream_retro / red_accent / brushed_inox | gloss_black_stainless | palette | palette only，**不计入 slot_choice**；每 seed 采一套（材质 / 色，见下表）| 各样本材质 |
| body_height_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放机身 Z（HEIGHT / core_shell 高 → top_deck Z / fascia Z / lid 铰链 Z 联动），clamp | parent L36 / pod L36 |
| body_width_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放机身 Y（WIDTH → fascia / deck / tray / 各 bay 宽），clamp | parent L34 / pod L34 |
| body_depth_scale | float | [0.92, 1.12] | 1.0 | independent | 缩放机身 X（DEPTH → X_FRONT / X_REAR / cheeks / tray 深），clamp | parent L35 / pod L35 |
| fascia_tilt_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 TILT（fascia 倾角；联动 fascia_point / dial 轴），clamp（保 TILT∈[8°,22°]）| parent L40 |
| tray_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 `body_to_tray` upper（接水盘行程；≤ tray 不脱 bay）| parent L53 / pod L44 |
| spout_travel_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 brew_type=super_automatic 有效；缩放 `body_to_spout` upper（≤ 喷嘴到 drip plate 可达行程）| parent L52 |
| wand_swing_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 super_automatic 有效；缩放 `body_to_wand` upper（保 ≤π·0.5）| parent L54 |
| lid_open_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 super_automatic（rear/side_hinge）/ pod（capsule_flap）有效；缩放 REVOLUTE 盖 upper（保 ≤π·0.95）| parent L55 / side_hinge L55 / pod L45 |
| canister_lift_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 hopper_lid=removable_canister 有效；缩放 `body_to_hopper` upper（≥ canister 脱 guide bay）| removable L68 |
| tank_travel_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 water_tank∈{side_removable, top_reservoir} 有效；缩放 `body_to_tank` upper（≥ tank 脱 bay / cradle）| side_removable L56 / top_reservoir L59 |
| (—) | constraint | — | — | inequality | 接水盘行程不脱 bay：`tray_travel·tray_travel_scale ≤ DEPTH·body_depth_scale − tray_engage_min`；违反按比例缩 travel | parent L53, L262-318 |
| (—) | constraint | — | — | inequality | 喷嘴降到杯不穿 drip plate：`spout_travel·spout_travel_scale ≤ (rest_nozzle_z − drip_plate_top_z) − cup_clear`；违反缩 travel（照搬 expect_gap z≥0.01）| parent L556-562 |
| (—) | constraint | — | — | inequality | 盖闭合覆盖豆斗口：closed lid plate XY 覆盖 deck 后半 ≥0.08（rear/side_hinge）；违反加大 lid plate 或拒绝重采 | parent L495-502 |
| (—) | constraint | — | — | inequality | 提罐 / 提箱脱 bay：`canister_lift·scale ≥ GUIDE_H + clear`（removable）、`tank_travel·scale ≥ bay 包络 + clear`（top_reservoir）；违反加大 travel 或缩 bay 高 | removable L684-693 / top_reservoir L728-737 |

palette_style 候选（每 seed 采一套，**不计入 slot_choice**，跨 7★ 样本观察 + 真实机型外推）：
| palette_style | body / core | fascia | dial / 金属件 | spout / tank | 来源样本 |
|---|---|---|---|---|---|
| gloss_black_stainless（默认）| gloss_black (0.10,0.10,0.11) | fascia_gray (0.55,0.56,0.575) | silver/stainless (0.72-0.80) | stainless 喷嘴 + translucent tank | parent / 各 super-auto 变体 |
| matte_graphite | graphite (0.17,0.17,0.185) | trim_black (0.065) | silver | stainless + 蓝 translucent tank (0.55,0.65,0.72) | side_removable tank 配色 |
| cream_retro | 米白机身外推 (0.90,0.87,0.80) | 米灰 fascia | chrome (0.78,0.80,0.82) | chrome 嘴 + clear tank (0.74,0.84,0.90) | pod chrome + top_reservoir clear 混 |
| red_accent | 红机身外推 (0.78,0.14,0.12) | 黑 fascia | chrome | stainless | 真实复古意式机外推 |
| brushed_inox | 拉丝不锈 (0.66,0.68,0.70) | 深灰 fascia | brushed silver | brushed + water_blue fill (0.28,0.48,0.68) | top_reservoir water_blue 配色外推 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全机身比例 / 行程 / 角度 / clearance，**绝不改变 brew_type / hopper_lid / water_tank 的拓扑**。

## Multiplicity / Copy Logic

- **无模板级可变 multiplicity 轴**：核心结构由固定 named slots（brew_type / hopper_lid / water_tank）表达，不暴露 `*_count`，也不通过循环复制模板级 visual / part / joint 形成结构差异轴。
- **存在固定 N 的对称 / 阵列 visual（非可变轴，不进 slot_choice）**：
  - fascia 按钮 `{tag}_button_{k}`：源用 `for sgn,tag in ((1,"left"),(-1,"right"))` × `for k,u in enumerate((...))` 发射 3 按钮 × 2 侧（parent L156-163）；**装饰**，无关节，固定阵列。source map 明确：buttons are decoration; not copied as articulated units。
  - super-auto 双喷嘴 `{tag}_nozzle`（parent L243-249，N=2）、前 cheeks `{tag}_front_cheek`（×2）、侧裙 `{tag}_base_skirt`（×2）、tray 侧壁 `tray_{tag}_wall`（×2）：对称结构 / 装饰阵列。
  - portafilter `pf_ear_{i}`（`for i in range(2)`，L294-301，N=2）、side_removable `tank_rail_{i}`（×2，L206-212）、removable `hopper_guide_{tag}`（4 bay 壁，L206-219）：module-local 固定阵列。
- 这些都是 **module-local 固定多份 visual**（对称喷嘴 / cheeks / 按钮 / ears / rails / bay 壁），按 module 而非 multiplicity 轴声明——clamp 不存在"任意 N 个出咖嘴 / N 个豆斗 / N 个水箱"的真实产品域。copied object 用小循环对称 / 绝对式 placement 发射，无独立 joint（FIXED 装饰，inline body / part visual，Rule 1）。

## 拓扑多样性审计

总组合数（**按 spine 暴露的下游槽计，非朴素 3×3×3**）：
- `super_automatic` spine：hopper_lid(3) × water_tank(3) = **9**。
- `portafilter` spine：无 Slot B × water_tank(3) = **3**。
- `pod_capsule` spine：Slot B 固定 × Slot C 固定 = **1**。
- 合计真实合法拓扑组合 = 9 + 3 + 1 = **13 ≥ 10 ✓**。

（朴素笛卡尔积 brew_type(3) × hopper_lid(3) × water_tank(3) = 27 是 source map 的"组合数预审"上界；模板侧按 §9 兼容矩阵把 pod 的 B/C gate 为 spine 默认、把 portafilter 的 hopper gate 掉，落到 13 真实合法组合——仍 ≥10。）

理由：13 真实合法组合中含丰富 joint 拓扑差异——super-auto spine 的 {PRISMATIC spout + REVOLUTE wand + (REVOLUTE -Y / REVOLUTE +Z / PRISMATIC +Z 豆斗) + (无 / PRISMATIC -Y / PRISMATIC +Z 水箱)} 9 类、portafilter 的 {2 FIXED brew group + (无 / PRISMATIC -Y / PRISMATIC +Z 水箱)} 3 类、pod 的 {REVOLUTE 顶翻盖 + 拉伸机身} 1 类。**每个槽选择都编入 `slot_choices_for_seed` 的 tuple**（`("brew_type",m)`、`("hopper_lid",m)`（仅 super-auto）、`("water_tank",m)`（super-auto / portafilter）），spine 派生的 part / joint 差异自然区分。13 distinct 远超 ≥10 机械门控。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` brew_type（整机 spine），再按 spine **条件采样**下游槽——super_automatic→`rng.choice` hopper_lid + water_tank；portafilter→`rng.choice` water_tank（无 hopper）；pod_capsule→B/C 锁定为 spine 默认（不采）。经兼容矩阵合法化后再解析 conditional scale（spout/wand 仅 super-auto；canister_lift 仅 removable；tank_travel 仅可拆水箱；lid_open 仅有铰盖），再 uniform 各 independent 机身 scale + 采 palette_style。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（重点看 spout 升降 / wand 摆动 / 豆斗盖开合 / 水箱抽出 / pod 翻盖 / 盖闭合姿态）。


Controlled local parameterization：见 §参数表的 body_height/width/depth_scale + fascia_tilt_scale + tray_travel_scale（independent）+ spout_travel/wand_swing/lid_open/canister_lift/tank_travel_scale（conditional 随 spine / slot 解析）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 brew_type spine → 条件采下游槽（解析 conditional 范围：hopper 仅 super-auto、tank 仅 super-auto/portafilter）→ 解析 conditional scale（spout/wand 仅 super-auto、lid_open 仅有铰盖、canister_lift 仅 removable、tank_travel 仅可拆水箱）→ 采 independent 机身 scale → 派生（top_deck Z / fascia Z / 铰链 Z 随 body_height_scale；各 bay 宽随 body_width_scale）→ 用四条 inequality（tray 不脱 bay、spout 不穿 drip plate、盖覆盖豆斗口、提罐 / 提箱脱 bay）投影 / 回缩。跨部件依赖（tray travel vs DEPTH、spout travel vs drip plate、盖 vs deck、travel vs bay 高）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 dial / spout / wand / flap / tank captured 接口、各 joint origin、固定阵列 visual 或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` brew_type spine，再按 spine 条件采 hopper_lid（仅 super-auto）/ water_tank（仅 super-auto/portafilter），经兼容矩阵合法化，再解析 conditional scale，再 uniform 各 independent 机身 scale，采 palette_style | slot_choices_for_seed 含 `("brew_type",m)` + 条件 `("hopper_lid",m)` / `("water_tank",m)`，且与 build 一致 |
| compatibility matrix | (1) **brew_type=pod_capsule**：自带 `capsule_flap`（Slot B）+ 机身集成 `water_tank` 视觉（Slot C）→ pod spine **不暴露独立 hopper_lid / water_tank 候选**，B/C gate 为 spine 默认（不进采样）。 (2) **brew_type=portafilter**：删豆斗 → **无 Slot B**（portafilter × 任意 hopper 候选非法，gate 掉）；保留 Slot C water_tank(3) 自由采样（portafilter 机仍有可选水箱）。 (3) **brew_type=super_automatic**：暴露 Slot B(3) × Slot C(3) 全 9 组合（hopper 三候选 × tank 三候选，正交合法）。 (4) source map 标注 portafilter × hopper 在真实物体上是弱组合 → 已通过"portafilter 无 Slot B"硬 gate 排除（不是 down-weight，是删除）。 | 无 floating / collision / pod 上挂可拆 hopper / portafilter 上挂豆斗 / 盖不覆盖豆斗口 / 喷嘴穿 drip plate / 水箱不脱 bay |
| controlled local variation | 5 independent + 5 conditional clamped scale，每 build 统一；conditional 随 spine / slot 解析（无件的候选不设对应 scale）| 比例变化不破坏 dial/spout/wand/flap/tank captured 接口、各 joint origin、盖闭合、tray docked、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 spine 机构 QC（spout 升降 / wand 摆动 / 豆斗盖 / 水箱抽出 / pod 翻盖）|

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| brew_type | 3 | yes | yes | super_automatic / portafilter / pod_capsule（整机 spine；决定下游槽暴露）|
| hopper_lid | 3 | yes | yes | rear_hinge / side_hinge（REVOLUTE）/ removable_canister（PRISMATIC）；仅 super_automatic spine 暴露 |
| water_tank | 3 | yes | yes | internal（无 joint）/ side_removable（PRISMATIC -Y）/ top_reservoir（PRISMATIC +Z）；super_automatic / portafilter spine 暴露 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 `("brew_type",m)`；super_automatic 附 `("hopper_lid",m)` + `("water_tank",m)`；portafilter 附 `("water_tank",m)`（无 hopper）；pod_capsule 仅 `("brew_type","pod_capsule")`（B/C 为 spine 默认不另列）
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）；下游槽按 brew_type spine 条件采样
- `resolve_config` 把各 scale clamp 到声明范围；spout/wand/lid_open/canister_lift/tank_travel 为 conditional 随 spine / slot 解析；四条 inequality（tray 不脱 bay、spout 不穿 drip plate、盖覆盖豆斗口、提罐 / 提箱脱 bay）在 resolve 内投影 / 回缩
- compatibility matrix / gating 阻止非法组合（pod 不挂可拆 hopper / 可拆 tank；portafilter 不挂豆斗；portafilter 可挂 water_tank 三候选；super-auto 全 9 组合）
- 连续 scale clamp 后不破坏 dial/spout/wand/flap/tank captured 接口、各 joint origin、盖闭合、tray docked、固定阵列 visual
- 关键 joint：`fascia_to_dial`/`body_to_dial` CONTINUOUS（unbounded，全 spine）；super-auto `body_to_spout` PRISMATIC axis≈(0,0,-1)（abs(axis[2])>0.99）、`body_to_wand` REVOLUTE axis≈(0,0,±1)（竖直）；`body_to_tray` PRISMATIC axis≈(1,0,0)（全 spine）；rear_hinge `deck_to_hopper_lid` REVOLUTE axis≈(0,-1,0)（abs(axis[1])>0.99）；side_hinge `deck_to_hopper_lid` REVOLUTE axis≈(0,0,+1)（abs(axis[2])>0.99）；removable `body_to_hopper` PRISMATIC axis≈(0,0,1)；side_removable `body_to_tank` PRISMATIC axis≈(0,-1,0)；top_reservoir `body_to_tank` PRISMATIC axis≈(0,0,1)；pod `body_to_flap` REVOLUTE axis≈(0,-1,0)
- captured 接口：element-scoped `allow_overlap`（`dial_stem`↔`fascia_panel`/`body_shell`；`spout_housing`↔`spout_rail`；`pivot_knuckle`↔`wand_boss`；`flap_hinge_pin`↔`flap_hinge_boss`；`canister_align_rib`↔`hopper_bay_floor`；`tank_body`↔`tank_bay_plate`/`tank_rail_{i}`；portafilter `pf_rim`/`pf_ear_{i}`↔`gh_lock_ring`、`gh_body`↔`group_mount_boss`），照搬各样本 run_tests 的 allow_overlap 段
- 固定阵列 visual 遵循 `{tag}_button_{k}`/`{tag}_nozzle`/`pf_ear_{i}`/`tank_rail_{i}`/`hopper_guide_{tag}` 命名 + 对称 / 绝对式 placement + Rule 1（无独立 joint）
- portafilter spine 断言无 `spout_block`、无 `hopper_lid` part（照搬 portafilter run_tests L449-466）
- grandfather：所有 captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守

## Reject cases

- brew_type=pod_capsule 仍挂独立可拆 `hopper_canister` 或独立可拆 `water_tank` → 违反 pod 整机 spine（pod 自带 capsule_flap + 机身集成 tank 视觉；必须 gate 为 spine 默认，见 §9）。
- brew_type=portafilter 仍发射 `hopper_lid` / `hopper_canister`（豆斗）→ portafilter 用预磨粉无豆斗，须 gate 掉 Slot B（portafilter run_tests 显式断言 `hopper_lid` not in parts）。
- 把 brew_type / hopper_lid / water_tank 的某选择不进 slot_choice → spine 与下游槽在 slot_choice 上无法区分，损失拓扑维度（违反 §9 硬要求）。
- 把按钮 `{tag}_button_{k}` / 双喷嘴 / cheeks / ears / rails / bay 壁当独立活动 part 加 joint → 违反 Rule 1（固定装饰 / 结构阵列，应 inline 为 body / part visual）。
- 盖 / 翻盖 / 喷嘴 / 水箱 rest pose 设成张开 / 降下 / 抽出而非 q=0 闭合 / 顶 / docked → current-pose 与 viewer 目检不符（所有样本 rest 闭合 lower=0：lid 坐 deck、spout 在顶、tank 坐底）。
- joint origin 放在机身中心或任意点而非真实铰线 / 导轨 / dock 硬件（fascia 法向 / spout_rail / wand_boss / 后铰 / guide bay / tank dock / cradle）→ `fail_if_articulation_origin_far_from_geometry` FAIL。
- 给 captured 接口（dial stem / spout rail / wand boss / flap pin / canister rib / tank rail / portafilter rim）补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- spout_travel 过大致喷嘴穿透 drip plate → §7 第二条 inequality FAIL；须按比例缩 travel（照搬 expect_gap z≥0.01）。
- 把连续尺寸 / 颜色 / 材质（palette_style / 机身 scale / 行程 scale）当新 candidate 塞进 slot → 不是结构差异。
- 把电热水壶 / 饮水机 / 滴滤壶语义混入（只烧水 / 出冷热水 / 手冲壶具，无 brew front end + fascia dial spine）→ 出类，本类是立式带电控冲煮咖啡机。

## 与相邻类别的边界

- 不该混入：**电热水壶 / 烧水壶（kettle）**——只烧水、无冲煮头 / 豆斗 / 出咖嘴 / 旋钮选档 / 蒸汽棒；已有独立 slug `container_kettle`（主功能与 spine 不同）。
- 不该混入：**台式饮水机 / 直饮机 / 净水器（water dispenser）**——出冷热水龙头 + 大水桶 / 滤芯，无咖啡冲煮机构、无 fascia 旋钮选档、无 drip tray + 升降出咖嘴。
- 不该混入：**滴滤咖啡壶 / 法压壶 / 摩卡壶（drip carafe / French press / moka pot）**——分体壶具 / 手冲器，不是立式带电控制面板整机；无 fascia + dial + 蒸汽棒 + 升降 spout spine。
- 不该混入：**意式手动杠杆咖啡机（manual lever espresso）的大摆杆**——本类三 spine 是 super-auto 升降嘴 / portafilter FIXED 冲煮头 / pod 翻盖，不含绕中柱大幅摆动的手动杠杆（如需可作单独 slug / 回 fork 池补造 brew 候选）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **brew_type 作为整机 spine 而非纯正交槽**的建模——pod 把 Slot B/C gate 为 spine 默认、portafilter 无 Slot B、仅 super_automatic 暴露 B(3)×C(3)，落到 13 真实合法组合（而非朴素 27）是否接受；(2) `slot_choices_for_seed` 按 spine 条件附 hopper/tank tuple（pod 只 1 个 tuple、portafilter 无 hopper tuple）是否符合 期望，还是要求统一长度 tuple（用占位 `("hopper_lid","none")` / `("water_tank","integral")`）以稳定区分；(3) portafilter × water_tank(3) 是否都收敛（样本只在 super-auto spine 上 fork 了 tank 变体，portafilter spine 上未单独 fork tank——模板侧把 super-auto 的 tank 模块改挂 portafilter body 是否需特别 QC，或 portafilter 限 internal）；(4) pod 机身用 ExtrudeGeometry 与 super-auto 的 box 拼装机身是两套 mesh helper，是否在模板内分支实现；(5) Topology target 13<300 的说明是否接受（本小类真实结构 + spine 兼容上限）；(6) palette_style 5 套是否合适，cream_retro/red_accent/brushed_inox 三套为样本配色外推。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- **brew_type spine 分支**：模板内按 brew_type 切两套机身 helper——super_automatic / portafilter 共享 box 拼装机身（`core_shell` + cheeks + fascia + top_deck，sgn-tag 小循环），pod 用 `rounded_rect_profile` + `ExtrudeGeometry.from_z0` 拉伸圆角机身（pod L64-70）。`fascia_point` helper（parent L58-64）super-auto / portafilter 复用；pod dial 用前面法向（pod L196-204）。机身尺寸常量随 spine（super-auto W0.24/D0.35/H0.43；pod W0.14/D0.28/H0.30）。
- **条件下游槽**：仅 super_automatic 调 hopper_lid + water_tank 两个 module factory；portafilter 仅调 water_tank（+ group_head/portafilter FIXED 件）；pod 不调（capsule_flap + 机身集成 tank 视觉是 pod spine 内联）。`slot_choices_for_seed` 据此返回变长 tuple（或按审核 (2) 用占位统一长度）。
- **共享 module factory**：dial（CONTINUOUS）/ tray（PRISMATIC）/ spout（PRISMATIC，仅 super-auto）/ wand（REVOLUTE，仅 super-auto）/ hopper_lid（rear/side REVOLUTE、removable PRISMATIC + guide bay）/ water_tank（internal 无件、side_removable PRISMATIC -Y + bay、top_reservoir PRISMATIC +Z + cradle）。
- captured 接口 allow_overlap：`run_coffee_machine_tests` 里逐 module 补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（parent L406-426、portafilter L469-495、pod L330-357、removable L498-504、side_removable L684-704）。
- conditional 范围解析顺序：先采 brew_type spine → 条件采 hopper_lid（仅 super-auto）/ water_tank（仅 super-auto/portafilter）→ 解析 conditional scale（spout/wand 仅 super-auto；lid_open 仅有铰盖 rear/side/pod-flap；canister_lift 仅 removable；tank_travel 仅可拆水箱）→ 采 independent 机身 scale → 派生（top_deck/fascia/铰链 Z 随 body_height_scale；各 bay 宽随 body_width_scale）→ 投影四条 inequality。
- 参考模板：选运动拓扑相近的——root chassis + parallel children + 多个并行可选 PRISMATIC/REVOLUTE child（`agent/templates/Accessories_Cushion.py` 的 base + lid REVOLUTE + interior 互斥；`agent/templates/Handtools_Clamp.py` 的 frame + screw PRISMATIC + 可选 pad/lever REVOLUTE；`agent/templates/Bag_Suitcase_Shopping_bucket.py` 的兼容矩阵 gating + slot_choice tuple + captured-pin allow_overlap 骨架）。coffee_machine 的 body→(dial CONTINUOUS + tray PRISMATIC + spout PRISMATIC + wand REVOLUTE + hopper + tank) 并行 children 与之同构；额外特点是 brew_type spine 决定下游槽暴露（条件采样 + 兼容 gate），实现时重点处理 spine 分支 + 变长 slot_choice。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C（parent 基线 spine）| super_automatic + rear_hinge + internal | rec_model-a-delonghi-magnifica-style-super-automatic_...ed06768c | `fascia_point` L58-64 / body L80-186 / `selection_dial`+`fascia_to_dial` CONTINUOUS L189-233 / `spout_block`+`body_to_spout` PRISMATIC L236-259 / `drip_tray`+`body_to_tray` PRISMATIC L262-318 / `steam_wand`+`body_to_wand` REVOLUTE L321-359 / `hopper_lid`+`deck_to_hopper_lid` REVOLUTE -Y L362-384 / allow_overlap L406-426 | super-auto spine 基线 + 共享核心（dial/tray/spout/wand）+ rear_hinge 豆斗盖 + internal 水箱 + captured 范式 |
| S2 | A | portafilter | rec_coffee_machine_var_brew_portafilter | `group_head`+`body_to_group_head` FIXED L246-275 / `portafilter`+`body_to_portafilter` FIXED L278-330 / `group_mount_boss` L192-197 / 删 spout/hopper 断言 L449-466 / allow_overlap L469-495 | 预磨 portafilter 整机 spine（两 FIXED brew group，删 spout + 豆斗，无 Slot B）|
| S3 | A | pod_capsule | rec_coffee_machine_var_brew_pod | `body_shell` Extrude L64-70 / `single_spout`/`spout_tip` L97-109 / `capsule_slot` L112-117 / 机身集成 `water_tank` L120-125 / `control_dial` CONTINUOUS L155-204 / `capsule_flap`+`body_to_flap` REVOLUTE L207-243 / `drip_tray` L246-312 / allow_overlap L330-357 | 紧凑 pod 整机 re-body spine（拉伸机身 + 单嘴 + 顶翻盖；自带 B/C spine 默认）|
| S4 | B | side_hinge | rec_coffee_machine_var_hopper_side_hinge | `hopper_lid` L369-382 / `deck_to_hopper_lid` REVOLUTE axis=(0,0,+1) 左侧竖直铰 L383-392 | 侧翻豆斗盖（竖直 Z 轴铰，区别于 rear -Y）|
| S5 | B | removable_canister | rec_coffee_machine_var_hopper_removable | guide bay `hopper_guide_{tag}`/`hopper_bay_floor` L201-226 / `hopper_canister`（`canister_shell` CadQuery shell）L403-443 / `body_to_hopper` PRISMATIC +Z L445-455 / allow_overlap L498-504 | 提出式豆罐（竖直 PRISMATIC 提起 + 4 壁 guide bay + align rib captured）|
| S6 | C | side_removable | rec_coffee_machine_var_tank_side_removable | tank bay `tank_bay_plate`/`tank_rail_{i}` L199-212 / `water_tank`（`tank_body` translucent + cap + handle）L413-434 / `body_to_tank` PRISMATIC -Y L435-445 / allow_overlap L684-704 | 侧抽半透明水箱（右 flank PRISMATIC -Y + dock bay + rails captured）|
| S7 | C | top_reservoir | rec_coffee_machine_var_tank_top_reservoir | cradle `tank_bay_platform`/`tank_bay_back_wall`/`tank_bay_{tag}_wall` L194-215 / `water_tank`（`tank_vessel` Extrude + `tank_water_fill` + lid + grip）L416-452 / `body_to_tank` PRISMATIC +Z L453-464 | 后置提起式透明水箱（可见水位 + 后 cradle PRISMATIC +Z）|
