# knife (utility / hand knife: slide-out box cutter & folding / fixed-blade variants) — Modular Spec

> 来源小类：`picture/Handtools/Knife`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Handtools__Knife.md`。
> **"Knife" 在此 = 手用工具刀 / 美工刀（utility / hand knife）：一只可手持的刀，root 是 `handle`（molded shell / barrel / 金属 bar），刀片通过某种 deployment 机构（滑出 / 折出 / 固定+翻盖护罩）暴露或收起。不是剪刀 scissors、不是菜刀 / 砍刀 cleaver、不是餐刀、也不是固定全长无机构的雕刻刀。**
> 结构家族 = 手持刀：一只 `handle`（root，坐地于 handle 长轴 +X；带 top channel / blade-exit groove / lanyard hole / thumb_grip）+ 一个 deployment 机构（**identity = ≥1 个非 fixed joint 始终存在**：snap-off 滑动 = PRISMATIC、full-retract = PRISMATIC、fold = REVOLUTE、flip-up-guard = REVOLUTE）+ 一片暴露刀片（blade profile）。可选 rear `end_cap`（FIXED part 或 inline visual）。
>
> **OLD 非模块化模板注记**：downstream 存在 `agent/templates/retractable_utility_knife.py`（旧单刀非模块化模板）——**它不是本 spec 的 source，本 spec 忽略它**；本模板是覆盖整个 Knife pool 的全新 modular template。
>
> **同步状态**：本 spec 引用的 10 个 5 星样本（1 个 parent + 9 个 fork 槽位变体）**已同步进本仓库 `data/records/<id>/`，rating=5**。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一逐行读完整文件核对）。引用以 part / joint / helper **名字** 为准（`handle`/`blade_carrier`/`blade`/`safety_guard`/`end_cap` part；`handle_to_carrier`/`handle_to_blade`/`handle_to_guard`/`handle_to_cap` joint；`_handle_body_shape`/`_build_barrel_body`/`_build_blade_shape`/`_build_blade_score_lines`/`_finger_groove_cuts`/`_build_tpr_rib`/`_sheepsfoot_outline_pts`/`post_{i}`/`tpr_rib_{i}`/`finger_groove_{i}` 等），行号仅作定位。

## 元信息
| 项 | 值 |
|---|---|
| slug | `knife` |
| template path | `agent/templates/Handtools_Knife.py` |
| test path (optional) | `tests/agent/test_knife_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（固定 root `handle` + 三个并行替换层：deployment 机构 / grip / blade profile；deployment 的活动件（carrier / blade / guard）挂 handle，blade profile 注入到该活动件或 inline 到 handle）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10（1 parent + 9 fork 槽位变体；均 converged、compile success、≥1 非 fixed joint、workbench-only，rating=5）|
| read_count | 10（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests + allow_overlap 段）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 10/10 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **共享基线拓扑（全部 10 个样本）**：`handle`（root，handle 长轴 +X、坐地、`HANDLE_LEN≈0.150`；带 top channel groove + thumb_grip + lanyard hole）。9/10 样本带一个 deployment 活动件（`blade_carrier` / `blade` / `safety_guard`）以 ≥1 个非 fixed joint 挂 handle；rear `end_cap` 为 FIXED part（parent/fold/guard/各 blade/各 grip）或 inline visual（retract_full）。`handle` mesh 由 `_handle_body_shape` lofted rounded-rect（parent / 多数）/ `_build_barrel_body` lofted circular（overmold）/ `box` uniform bar（flat_metal）三种 helper 之一生成。
- **Slot A deployment 机构轴（核心 identity，决定非 fixed joint 类型与活动件 part 树）**：
  - snap_off_slide（parent）：`blade_carrier` 独立 part，`handle_to_carrier` **PRISMATIC** axis=(1,0,0)（parent L372-382），carrier = blade_steel+blade_tip+blade_spine+thumb_button；blade 在 rest 只露 `BLADE_EXPOSED_REST≈0.012`，推出 nose；`handle_to_cap` FIXED（parent L385-391）。
  - retract_full（mech_retract）：`blade_carrier` 独立 part，`handle_to_carrier` **PRISMATIC** axis=(1,0,0)（retract L349-359），carrier = blade_body+blade_clamp+`post_{i}`(for i in range(2), retract L321-333)+thumb_button；q=0 刀片**全收进 body**（`BLADE_RETRACT≈0.006` 在 nose 后）；end_cap inline handle visual（retract L282-286）。与 snap_off 共享 PRISMATIC joint，但活动件 part 树（clamp+posts vs spine）与收回深度不同。
  - fold_pivot（mech_fold）：`blade` 独立 part，`handle_to_blade` **REVOLUTE** axis=(0,1,0)，origin=(PIVOT_X,0,PIVOT_Z)=(0.065,0,0.011)，limits 0..π（fold L321-334）；q=0 刀片**沿 -X 收进 handle 内**、q=π 摆出前 groove；handle 加 `pivot_pin`(brass)+`front_bolster` visual；`handle_to_cap` FIXED（fold L337-343）。
  - flipup_guard（mech_guard）：`safety_guard` 独立 part，`handle_to_guard` **REVOLUTE** axis=(0,-1,0)，origin=(HINGE_X,0,HINGE_Z)=(0.068,0,0.024)，limits 0..π（guard L478-488）；**刀片是 FIXED inline handle visual**（permanently exposed，`FIXED_BLADE_EXPOSED≈0.045`，guard L425-439），活动件改为橙色翻起 safety guard（barrel+plate+skirts+front_lip+ribs）；handle 加 `hinge_bracket` ears（guard L417-421）；`handle_to_cap` FIXED（guard L466-472）。
  > Joint 拓扑：PRISMATIC（snap_off / retract）+ 2 处不同 REVOLUTE（fold = 刀片绕 nose 附近 Y 折；guard = guard 绕刃口上方 -Y 翻）。
- **Slot B grip 轴（决定 `handle` 主壳 mesh helper + 表面细节，不改 deployment joint 拓扑）**：
  - tapered_molded（parent）：`_handle_body_shape` lofted rounded-rect（6 段 profile），yellow `handle_shell`（parent L74-109）；高鼓后端 → 尖 nose。
  - ergo_contoured（grip_ergo）：`_handle_body_shape` 带 palm-swell profile（8 段，中段加宽 ×1.22）+ `_finger_groove_cuts`（4 个半圆槽，ergo L160-196）+ `finger_groove_{i}` rubber insert（for i in range(4)，ergo L401-407）。
  - overmold_barrel（grip_overmold）：`_build_barrel_body` lofted circular barrel（9 段半径 profile，overmold L102-115）+ `tpr_rib_{i}` revolved ring 肋（for i in range(N_RIBS=8)，overmold L293-299）；圆截面橡胶 barrel。
  - flat_metal_bar（grip_flat）：`_handle_body_shape` = uniform squared `box` bar（`HANDLE_H≈0.014` slim，flat L149-160）+ `_blade_exit_slot`（flat L194-205）+ 侧面 `thumb_grip` via `_knurl_bumps_side`（flat L116-143, L233-262）；slim 方截面金属 bar。
- **Slot C blade profile 轴（决定暴露刀片 outline + tip + edge 细节，注入到 deployment 活动件 / 或 inline）**：
  - snap_off_segmented（parent）：`_build_blade_shape` 平行四边形（parent L184-209）+ `_build_blade_score_lines`（for i in range(5)，斜对角 score 切，parent L212-227）+ `_build_blade_tip_visual`（parent L230-248）；直段刀片 + 斜 score + 暗 tip。
  - hawkbill（blade_hawk）：`_build_blade_shape` spline（凹刃 + 下钩 tip，hawk L188-218）+ `_hawkbill_edge_z` helper 给 score line 定深（hawk L221-260）+ `_build_blade_tip_visual` 覆盖钩。
  - drop_point（blade_drop）：`_build_blade_shape` drop-point polyline（缓降 spine + belly + 居中尖，drop L187-217）+ `_build_blade_grind_line` bevel 槽（drop L220-242）+ `_build_blade_tip_visual`。
  - serrated_sheepsfoot（blade_serr）：`_sheepsfoot_outline_pts`（降 spine + 钝圆 tip + 14 三角齿 via loop，serr L180-245）+ `_build_blade_shape` + `_build_blade_tip_visual`（serr L266-308）；锯齿刃 + 钝圆 tip（无尖点）。

## 核心身份

一只**手用工具刀 / 美工刀**（utility / hand knife）：root 是一只 `handle`（沿长轴 +X，坐地；molded plastic tapered shell / ergonomic contoured shell / rubber-overmolded barrel / slim flat metal bar 之一），handle 顶有 top channel（滑动机构）或前 blade-exit groove（折刀），后有 lanyard hole + 可选 rear `end_cap`，侧 / 顶有 thumb_grip。一片钢刀片通过某种 **blade-deployment 机构**暴露或收起——**身份核心 = 始终存在 ≥1 个非 fixed joint**：snap-off 滑动（PRISMATIC，刀片只露一截、可推出 nose）/ full-retract 滑动（PRISMATIC，刀片可全收进 body）/ fold-pivot（REVOLUTE，刀片折进 handle / 摆出前 groove）/ flip-up-guard（REVOLUTE，刀片**固定**全露、护罩翻起盖住刃口）。暴露刀片有不同 profile（直段 snap-off / 鹰嘴 hawkbill / drop-point / 锯齿 sheepsfoot）。默认成熟域：deployment(4) × grip(4) × blade(4) 笛卡尔积的小型手持刀（handle ~0.150m、blade ~0.050-0.060m）。活动语义 = **刀片 / 护罩通过机构运动**（PRISMATIC 滑出 / REVOLUTE 折出 / REVOLUTE 翻护罩）。

不该混入：
- **剪刀（scissors）**——双臂绕中心 pivot 对剪，两片刀刃 + 两环柄；本类是单刀片 + 单 handle + 单 deployment joint，不是对剪结构。
- **菜刀 / 砍刀 / 厨刀（cleaver / chef's knife）**——固定全长大刀片 + 木 / 塑柄，无 deployment 机构、无收纳运动；本类 identity 在于刀片有可动机构（滑 / 折 / 护罩），固定全长无机构出类。
- **餐刀 / 黄油刀（table knife / butter knife）**——固定全长钝刀，无机构、无 handle channel；同上无活动 joint 出类。
- **雕刻刀 / 手术刀（fixed-blade carving / scalpel）的纯固定刀**——除非配 flip-up-guard 护罩机构（本类 Slot A 第 4 候选即覆盖此"固定刀 + 护罩"形态），否则纯固定无机构刀不属本类。
- **多功能瑞士军刀（multi-tool / Swiss army）的多工具枢轴簇**——多个独立 REVOLUTE 工具叠在一个柄上；本类是单 deployment 机构 + 单刀片，不做多工具 multiplicity 簇（若需可作单独 slug）。

## 槽位 + 候选模块表

> **建模注记**：`grip`（Slot B）是 `handle` part **主壳 mesh 足迹 + 表面细节形态**（molded / ergo / barrel / flat bar），由 handle mesh helper 一次决定，**不改 deployment joint 拓扑**；但它确实改 handle 截面几何（rounded-rect loft vs circular loft vs box）与表面阵列（finger grooves / TPR ribs / knurl），列为真正的结构层（part-internal mesh + 固定阵列 visual 差异）。`deployment`（Slot A）是改非 fixed joint 类型 + 活动件 part 树的主轴；`blade`（Slot C）是改暴露刀片 outline 的 profile 轴。三轴正交（除 §9 兼容矩阵列出的 deployment×blade 一条互斥）。

### Slot A：deployment（blade-deployment 机构 —— 核心 identity 槽，决定非 fixed joint 类型与活动件 part 树）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| snap_off_slide（基线）| rec_build-...-knif_..._211319cd（parent）| `blade_carrier` part + `_build_blade_spine_carrier` L251-261 + `_build_thumb_button` L264-280 + `handle_to_carrier` **PRISMATIC** axis=(1,0,0) origin=(0,0,0) L372-382 + `handle_to_cap` FIXED L385-391 | eligible if compatible | 滑出式：`blade_carrier` **独立 part**（blade_steel+blade_tip+blade_spine+thumb_button），沿 channel **+X PRISMATIC**（lower=0/upper=SLIDE_TRAVEL≈0.034）；rest 露 ~12mm，推出 nose；**1 非 fixed joint（PRISMATIC）** + 1 FIXED end_cap |
| retract_full | rec_knife_var_mech_retract | `blade_carrier` part + `_build_trapezoidal_blade_shape` L178-208 + `_build_blade_clamp` L211-217 + `_build_clamp_post` L220-228 + `post_{i}` for i in range(2) L321-333 + `handle_to_carrier` **PRISMATIC** axis=(1,0,0) origin=(0,0,HANDLE_H−CHANNEL_DEPTH) L349-359 | eligible if compatible | 全收式：同 +X PRISMATIC（lower=0/upper≈0.038），但 q=0 刀片**全收进 body**（front 在 nose 后 ~6mm）；trapezoidal blade 由 clamp plate + 2 个 mounting post 夹持；end_cap inline handle visual（无独立 part）；**1 非 fixed joint（PRISMATIC）** |
| fold_pivot | rec_knife_var_mech_fold | `blade` part + `_build_blade_body` L194-211 + `_build_thumb_stud` L234-245 + handle `pivot_pin`/`front_bolster` visual L276-285 + `handle_to_blade` **REVOLUTE** axis=(0,1,0) origin=(PIVOT_X,0,PIVOT_Z)=(0.065,0,0.011) limits 0..π L321-334 + `handle_to_cap` FIXED L337-343 | eligible if compatible | 折刀式：PRISMATIC 滑动换成**折叠铰**；`blade` **独立 part**，绕 nose 附近 **Y REVOLUTE** 折（q=0 沿 -X 收进 handle、q=π 摆出前-top groove）；handle 加 brass pivot_pin + front_bolster；blade exit 用 `_blade_exit_groove`（fold L111-124）；**1 非 fixed joint（REVOLUTE 绕 Y）** |
| flipup_guard（固定刀）| rec_knife_var_mech_guard | `safety_guard` part + `_build_guard_body`（barrel+plate+skirts+front_lip+ribs）L296-390 + handle `hinge_bracket` ears L258-290, L417-421 + 刀片 inline handle visual L425-439 + `handle_to_guard` **REVOLUTE** axis=(0,-1,0) origin=(HINGE_X,0,HINGE_Z)=(0.068,0,0.024) limits 0..π L478-488 + `handle_to_cap` FIXED L466-472 | eligible if compatible | 固定刀+翻护罩式：刀片**永久固定**（inline handle visual，`FIXED_BLADE_EXPOSED≈0.045` 全露，**无 deployment**）；活动件改为橙色 **safety_guard** 翻起盖刃口，`safety_guard` **独立 part**，绕刃口上方 **-Y REVOLUTE** 翻（q=0 盖住刃口 / q=π 翻开露刃）；handle 加 hinge_bracket（2 ears + crossbar）；**1 非 fixed joint（REVOLUTE 绕 -Y）**。**与"刀片可收进 body"互斥（见 §9 矩阵）** |

### Slot B：grip（handle 主壳 mesh + 表面 —— 决定 handle 截面几何与固定阵列 visual，不改 deployment joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| tapered_molded（基线）| rec_build-...-knif_..._211319cd（parent）| `_handle_body_shape` lofted rounded-rect 6 段 profile L74-109 + `_channel_cut` L112-121 + `_lanyard_hole_cut` L124-134 + `_build_thumb_grip_visual` L155-178 | eligible if compatible | 经典 tapered molded 塑料壳：rounded-rect loft（YZ rect 沿 X loft），高鼓后端 → 尖 nose，顶 channel + 黑 knurled thumb pad |
| ergo_contoured | rec_knife_var_grip_ergo | `_handle_body_shape` palm-swell 8 段 profile + `edges("|X").fillet` L80-125 + `_finger_groove_cuts` 4 半圆槽 L160-185 + `_groove_positions` L188-196 + `_build_single_groove_insert` L199-228 + `finger_groove_{i}` for i in range(4) L401-407 | eligible if compatible | 人体工学 contoured 壳：中段 palm swell（×1.22 宽）+ 4 个凹 finger groove（半圆 Y 轴切）+ dark rubber insert（for-loop 复制）；part 树同 molded（finger groove / insert 是 module-local 固定阵列）|
| overmold_barrel | rec_knife_var_grip_overmold | `_barrel_radius_at` L89-99 + `_build_barrel_body` lofted circular 9 段 L102-115 + `_build_tpr_rib` revolved ring L162-178 + `tpr_rib_{i}` for i in range(N_RIBS=8) L293-299 | eligible if compatible | 圆 rubber-overmolded barrel：lofted circular（YZ circle 沿 X loft，~29mm 直径）+ N 个 revolved TPR rib ring（环向肋，绕 barrel 轴 revolve 360°）；`barrel_shell` rubber 材质；part 树同 molded（TPR rib 是 module-local 固定阵列）|
| flat_metal_bar | rec_knife_var_grip_flat | `_handle_body_shape` = `box` uniform bar `HANDLE_H≈0.014` slim L149-160 + `_blade_exit_slot` L194-205 + `_knurl_bumps_side`/`_knurl_bumps_xy` 共享 helper L85-143 + 侧面 `thumb_grip` L233-262 | eligible if compatible | slim 方截面金属 bar：uniform squared box（无 taper）+ 小 edge fillet + 前 blade-exit slot + 侧面 knurled grip pad；brushed steel 材质；part 树同 molded（knurl bump 是 module-local 固定阵列）。**slim body → 与 fold_pivot 的"刀片收进 body"需 clearance 校验（见 §9 矩阵）** |

### Slot C：blade（暴露刀片 profile —— 决定 blade outline + tip + edge 细节；注入 deployment 活动件 / 或 inline 到 handle@guard）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| snap_off_segmented（基线）| rec_build-...-knif_..._211319cd（parent）| `_build_blade_shape` 平行四边形 L184-209 + `_build_blade_score_lines` for i in range(5) 斜对角 L212-227 + `_build_blade_tip_visual` L230-248 | eligible if compatible | 直段 snap-off 刀片：平行四边形 outline，斜刃，5 条 18° 斜对角 score line（snap-off 段）+ 暗 worn tip |
| hawkbill | rec_knife_var_blade_hawk | `_build_blade_shape` spline（凹刃+下钩 tip）L188-218 + `_hawkbill_edge_z` 给 score 定深 L221-241 + `_build_blade_score_lines` L243-260 + `_build_blade_tip_visual`（覆盖钩）L263-282 | eligible if compatible | 鹰嘴：凹（concave）刃曲线收到 spine 线下的下钩 tip（z extent > 0.019，钩超 18mm 名义宽）；spine 直、score line 随局部刃深变化 |
| drop_point | rec_knife_var_blade_drop | `_build_blade_shape` drop-point polyline（缓降 spine+belly+居中尖）L187-217 + `_build_blade_grind_line` bevel 槽 L220-242 + `_build_blade_tip_visual` L245-270 | eligible if compatible | drop-point trimming 刀：缓降 spine、belly 曲、居中尖（tip 在 blade 中线）；带 bevel grind line 纵槽 |
| serrated_sheepsfoot | rec_knife_var_blade_serr | `_sheepsfoot_outline_pts`（降 spine+钝圆 tip+14 三角齿 loop）L180-245 + `_build_blade_shape` L248-263 + `_build_blade_tip_visual`（钝 tip 区）L266-308 | eligible if compatible | 锯齿 sheepsfoot：toothed 刃（14 三角齿 via loop）+ 钝圆 tip（spine 前端降下、tip 圆，**无尖点**）|

## 槽位图（slot graph）

pattern: parallel_children（固定 root `handle`；deployment 的活动件（carrier/blade/guard）以非 fixed joint 挂 handle；blade profile 注入到该活动件的 blade visual，或在 flipup_guard 时 inline 到 handle；grip 只换 handle 主壳 mesh + 固定阵列 visual；可选 rear end_cap 以 FIXED 挂 handle 或 inline）

```
handle (root, 坐地, 长轴 +X; 由 grip 决定主壳 mesh: rounded-rect loft / palm-swell loft / circular barrel loft / squared box bar
        + top channel groove(滑动机构) 或 blade-exit groove(折刀) + lanyard hole + thumb_grip
        + deployment 专属 handle 硬件: pivot_pin/front_bolster(fold) 或 hinge_bracket ears(guard))
  │
  ├── [deployment slot]  (四选一; identity = 始终 ≥1 非 fixed joint)
  │     ├─ snap_off_slide : blade_carrier(独立 part) ──[handle_to_carrier: PRISMATIC axis=(1,0,0), origin=(0,0,0)]
  │     │                     (carrier 含 blade profile visual + blade_spine + thumb_button; lower=0/upper≈0.034)
  │     ├─ retract_full   : blade_carrier(独立 part) ──[handle_to_carrier: PRISMATIC axis=(1,0,0), origin=(0,0,channel 底 Z)]
  │     │                     (carrier 含 blade profile visual + blade_clamp + post_{i}(N=2) + thumb_button; lower=0/upper≈0.038; q=0 全收进 body)
  │     ├─ fold_pivot     : blade(独立 part) ──[handle_to_blade: REVOLUTE axis=(0,1,0), origin=(PIVOT_X,0,PIVOT_Z)≈(0.065,0,0.011), 0..π]
  │     │                     (blade 含 blade profile visual + thumb_stud; q=0 收进 handle 沿 -X, q=π 摆出前 groove)
  │     └─ flipup_guard   : safety_guard(独立 part) ──[handle_to_guard: REVOLUTE axis=(0,-1,0), origin=(HINGE_X,0,HINGE_Z)≈(0.068,0,0.024), 0..π]
  │                           (刀片 FIXED inline 到 handle; safety_guard = barrel+plate+skirts+front_lip+ribs; q=0 盖刃口, q=π 翻开)
  │
  ├── [grip slot]  (四选一; 只换 handle 主壳 mesh helper + 固定阵列 visual, 不改 deployment joint)
  │     ├─ tapered_molded  : _handle_body_shape rounded-rect loft (yellow handle_shell)
  │     ├─ ergo_contoured  : _handle_body_shape palm-swell loft + finger_groove_{i}(N=4 固定阵列) + rubber insert
  │     ├─ overmold_barrel : _build_barrel_body circular loft (barrel_shell rubber) + tpr_rib_{i}(N=8 固定阵列)
  │     └─ flat_metal_bar  : _handle_body_shape box uniform bar (brushed steel) + 侧 knurl thumb_grip
  │
  ├── [blade slot]  (四选一; 注入暴露刀片 outline 到 deployment 活动件的 blade_steel visual; flipup_guard 时 inline 到 handle)
  │     ├─ snap_off_segmented : 平行四边形 + 5 斜 score line + 暗 tip
  │     ├─ hawkbill          : 凹刃 spline + 下钩 tip
  │     ├─ drop_point        : 缓降 spine + belly + 居中尖 + bevel grind line
  │     └─ serrated_sheepsfoot: 14 三角齿刃 + 钝圆 tip
  │
  └── [可选 end_cap]  rear gray cap: FIXED part(handle_to_cap, snap_off/fold/guard/各 blade/各 grip) 或 inline handle visual(retract_full)
```

接口点位与 joint 语义：
- **handle → deployment 活动件（互斥四选一，identity joint）**：
  - snap_off_slide：mating = handle top channel rail。PRISMATIC axis=(1,0,0)，origin=(0,0,0)（parent L377）；carrier 的 `blade_spine` 捕入 `top_channel`（captured-slide，`allow_overlap(blade_spine,top_channel)` + `allow_overlap(blade_steel,top_channel)`，parent L467-482）；lower=0/upper≈0.034；rest 露 ~12mm，full travel 仍 retained（`expect_overlap(blade_steel,handle_shell,axes=x,min=0.005)`）。
  - retract_full：同 channel rail。PRISMATIC axis=(1,0,0)，origin=(0,0,HANDLE_H−CHANNEL_DEPTH)（retract L354）；blade_clamp 捕入 channel（`allow_overlap(blade_clamp,top_channel)`）+ post / clamp / blade carrier 内部过盈（`allow_overlap(post_{i},blade_body)`/`(post_{i},blade_clamp)`/`(blade_clamp,blade_body)`，retract L459-502）；q=0 全收（`blade_body` 全在 handle body 内，`allow_overlap(blade_body,handle_shell)`）。
  - fold_pivot：mating = nose 附近 pivot pin。REVOLUTE axis=(0,1,0)，origin=(PIVOT_X,0,PIVOT_Z)=(0.065,0,0.011)（fold L326）；q=0 blade 整体收进 handle（`allow_overlap(blade,handle)` part-level + `expect_within(blade_body,handle_shell,axes=xy)` + `expect_overlap(blade_body,handle_shell,axes=x,min=0.030)`，fold L377-401）；q=π 摆出前 groove。
  - flipup_guard：mating = handle hinge_bracket ears。REVOLUTE axis=(0,-1,0)，origin=(HINGE_X,0,HINGE_Z)=(0.068,0,0.024)（guard L483）；guard hinge barrel 捕入 bracket（`allow_overlap(guard_body,hinge_bracket)` + `expect_contact(guard_body,hinge_bracket,tol=0.008)`，guard L631-647）；q=0 盖刃口（`expect_overlap(guard_body,blade_steel,axes=x,min=0.035)`，guard L570-578）/ q=π 翻开。刀片本身 FIXED inline，无 deployment joint。
- **handle → blade profile（注入，非独立 joint）**：blade profile（snap_off_segmented / hawkbill / drop_point / serrated_sheepsfoot）是注入到 deployment 活动件 `blade_steel` visual 的 mesh helper 选择；snap_off / retract / fold 时注入 carrier / blade part 的 blade_steel；flipup_guard 时注入 handle 的 inline blade_steel。**blade profile 不增减 joint，只换刀片 outline**。
- **handle → end_cap（可选 FIXED）**：snap_off/fold/guard/各 blade/各 grip 用 `end_cap` 独立 FIXED part（`handle_to_cap` FIXED，origin (0,0,0)，`expect_contact(end_cap,handle)` + cap 在 -X 端）；retract_full 把 end_cap 做成 handle inline visual（无 FIXED joint）。模板统一：默认 end_cap 为 FIXED part（多数样本范式），retract_full 风格 inline 仅作 module-local 选项不进 slot_choice。
- **mating policy**：所有 captured 接口（blade_spine/blade_clamp 在 channel 内滑、blade 折进 handle、guard barrel 捕入 bracket、post 穿 blade hole、carrier 内 clamp 夹 blade）都是 captured-fit（嵌 / 滑 / 销入孔），**非两轴对齐面对接 → 省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段）。
- **rest pose**：snap_off q=0（露 ~12mm）/ retract q=0（全收）/ fold q=0（闭合收进 handle）/ guard q=0（护罩盖刃口）—— 全部 rest=收纳 / 盖住姿态，lower=0。
- **互斥 / 可选 / 派生**：deployment 四候选互斥（一次一种机构）；grip 四候选互斥；blade 四候选互斥（但 flipup_guard 的刀片 FIXED，blade profile 仍可换——见 §9）。snap_off_slide / retract_full 共享 PRISMATIC joint 类型但活动件 part 树不同（spine vs clamp+posts）+ 收回深度不同 → 仍是 distinct module。

## 每槽位 Module Emits / Interfaces

### Slot B / grip（以 tapered_molded 为例；ergo/barrel/flat 仅换 handle mesh helper + 固定阵列 visual）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `handle`（root，visual：`handle_shell` 主壳 + `top_channel` rail + `thumb_grip` + grip 专属阵列 + deployment 专属硬件）| parent `_handle_body_shape`+`_build_top_channel_visual`+`_build_thumb_grip_visual` L74-178 |
| internal joints | 无（handle 是 root）| — |
| upstream interface | root（坐地，无父）| — |
| downstream interface | top channel rail（供 snap_off/retract PRISMATIC）/ blade-exit groove（供 fold）/ hinge_bracket（供 guard）/ rear 端（供 end_cap）/ blade seat（供 blade profile）| parent L112-121 / fold L111-124 / guard L258-290 |

### Slot B / grip — ergo_contoured（额外固定阵列）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`handle_shell` palm-swell + `finger_groove_{i}` rubber insert（N=4 module-local 固定阵列）作 handle visual | ergo `_finger_groove_cuts` L160-185 / `finger_groove_{i}` for i in range(4) L401-407 |
| joints | 无（finger groove 非移动件，Rule 1 inline）| — |
| placement | `for i in range(4)`，沿 X 等距（`_groove_positions` 4 个绝对 X）| ergo L188-196 |

### Slot B / grip — overmold_barrel（额外固定阵列）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；`barrel_shell` circular loft + `tpr_rib_{i}`（N=8 module-local 固定阵列）作 handle visual | overmold `_build_barrel_body` L102-115 / `tpr_rib_{i}` for i in range(N_RIBS) L293-299 |
| joints | 无（TPR rib 非移动件，Rule 1 inline）| — |
| placement | `for i in range(N_RIBS)`，沿 X 等距（`RIB_ZONE_START`..`RIB_ZONE_END` 均分）；每 rib revolve 360° 环向| overmold L292-299 |

### Slot A / deployment — snap_off_slide
| emits | 描述 | 来源 |
|---|---|---|
| parts | `blade_carrier`（visual：`blade_steel`(注入 blade profile) + `blade_tip` + `blade_spine` + `thumb_button`）| parent L324-366 |
| internal joints | `handle_to_carrier` PRISMATIC axis=(1,0,0)，origin=(0,0,0)，lower=0/upper≈0.034 | parent L372-382 |
| upstream interface | `blade_spine` 捕入 handle `top_channel`（captured-slide）；blade 在 handle 内 retained（X 重叠）| parent L467-503 |

### Slot A / deployment — retract_full
| emits | 描述 | 来源 |
|---|---|---|
| parts | `blade_carrier`（visual：`blade_body`(注入 blade profile) + `blade_clamp` + `post_{i}`×2 + `thumb_button`）；end_cap inline handle visual | retract L291-344, L282-286 |
| internal joints | `handle_to_carrier` PRISMATIC axis=(1,0,0)，origin=(0,0,channel 底 Z)，lower=0/upper≈0.038；q=0 全收进 body | retract L349-359 |
| upstream interface | `blade_clamp` 捕入 `top_channel`（captured-slide）+ carrier 内 post/clamp/blade 过盈 | retract L451-522 |

### Slot A / deployment — fold_pivot
| emits | 描述 | 来源 |
|---|---|---|
| parts | `blade`（visual：`blade_body`(注入 blade profile) + `blade_tip` + `thumb_stud`）；handle 加 `pivot_pin`(brass) + `front_bolster` visual | fold L292-308, L276-285 |
| internal joints | `handle_to_blade` REVOLUTE axis=(0,1,0)，origin=(PIVOT_X,0,PIVOT_Z)=(0.065,0,0.011)，lower=0/upper=π | fold L321-334 |
| upstream interface | blade 折进 handle（part-level `allow_overlap(blade,handle)` + closed `expect_within`/`expect_overlap`）；pivot 在 nose 附近 | fold L377-401 |

### Slot A / deployment — flipup_guard
| emits | 描述 | 来源 |
|---|---|---|
| parts | `safety_guard`（visual：`guard_body` = barrel+plate+skirts+front_lip+grip_ribs）；handle 加 `hinge_bracket` ears + 刀片 inline（`blade_steel`(注入 blade profile)+`blade_tip`）| guard L457-462, L417-439 |
| internal joints | `handle_to_guard` REVOLUTE axis=(0,-1,0)，origin=(HINGE_X,0,HINGE_Z)=(0.068,0,0.024)，lower=0/upper=π | guard L478-488 |
| upstream interface | guard hinge barrel 捕入 handle `hinge_bracket` ears（`allow_overlap(guard_body,hinge_bracket)` + `expect_contact tol=0.008`）；刀片 FIXED inline（无 joint）| guard L631-647 |

### Slot C / blade profile（注入；non-articulating mesh helper）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part；blade profile 是 deployment 活动件 `blade_steel` visual 的 mesh（snap_off/retract/fold 注入 carrier/blade，guard 注入 handle inline）| parent L184-248 / hawk L188-282 / drop L187-270 / serr L180-308 |
| joints | 无（blade profile 不增减 joint，只换 outline）| — |
| internal copy loop | score line（for i in range(5)，snap_off/hawk）/ sheepsfoot 齿（14 via loop，serr）—— **module-internal 刀刃细节 loop，非 slot 轴 / 非 multiplicity 轴** | parent L212-227 / serr L234-239 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| deployment | enum | snap_off_slide / retract_full / fold_pivot / flipup_guard | snap_off_slide | choice | 由 deterministic procedural sampler 选；决定非 fixed joint 类型 + 活动件 part 树（互斥）| Slot A 表 |
| grip | enum | tapered_molded / ergo_contoured / overmold_barrel / flat_metal_bar | tapered_molded | choice | sampler 选；只换 handle 主壳 mesh helper + 固定阵列 visual（互斥）| Slot B 表 |
| blade | enum | snap_off_segmented / hawkbill / drop_point / serrated_sheepsfoot | snap_off_segmented | choice | sampler 选；注入暴露刀片 outline（互斥）| Slot C 表 |
| palette_style | enum | safety_yellow_abs / industrial_black / red_pro / steel_brushed / hi_vis_orange_guard | safety_yellow_abs | palette | palette only，**不计入 slot_choice**；每 seed 采一套（材质/色，见下表）| 各样本材质 |
| handle_len_scale | float | [0.88, 1.12] | 1.0 | independent | 缩放 `HANDLE_LEN`（联动 channel 长、slide travel 上限、pivot/hinge X），clamp | parent L50 |
| handle_height_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放 `HANDLE_H`（联动 channel 深、z_blade_top、hinge Z），clamp；flat_metal slim 基线 H≈0.014 单独基线 | parent L51 / flat L55 |
| handle_width_scale | float | [0.88, 1.15] | 1.0 | independent | 缩放 `HANDLE_W`（联动 channel 宽、barrel 直径基线），clamp | parent L53 |
| blade_len_scale | float | [0.85, 1.15] | 1.0 | independent | 缩放暴露刀片长 `BLADE_LEN`（联动 retract / slide 行程派生），clamp | parent L58 |
| blade_width_scale | float | [0.90, 1.12] | 1.0 | independent | 缩放刀片宽（spine→edge Z 向 `BLADE_W`），clamp（保 ≤ handle 内可容刃宽）| parent L59 |
| slide_travel_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 deployment∈{snap_off_slide, retract_full} 有效；缩放 PRISMATIC upper（≤ 推出 nose 所需 / blade_len 派生上限）| parent L63 / retract L65 |
| fold_open_scale | float | [0.85, 1.05] | 1.0 | conditional | 仅 fold_pivot 有效；缩放 `handle_to_blade` upper（保 ≤π·0.99，q=π 全开）| fold L332 |
| guard_open_scale | float | [0.85, 1.05] | 1.0 | conditional | 仅 flipup_guard 有效；缩放 `handle_to_guard` upper（保 ≤π·0.99，翻开露刃）| guard L486 |
| barrel_radius_scale | float | [0.90, 1.12] | 1.0 | conditional | 仅 overmold_barrel 有效；缩放 `BARREL_R_MAX`（保 24-34mm 直径，run_tests 范围）| overmold L43 |
| tpr_rib_count (N_RIBS) | int | 声明域 [4, 16]；标称 8 | 8 | **module-local 固定参数**（**不进 slot_choice**，非 multiplicity 轴）| 仅 overmold_barrel 内有效；环向 rib 数（clamp [4,16]）| overmold L57 |
| finger_groove_count | int | 声明域 [2, 5]；标称 4 | 4 | **module-local 固定参数**（**不进 slot_choice**，非 multiplicity 轴）| 仅 ergo_contoured 内有效；finger groove 数（clamp [2,5]）| ergo L160-196 |
| (—) | constraint | — | — | inequality | snap_off/retract 推出行程：`slide_travel·slide_travel_scale ≤ blade_len − rest_retain_margin`（保 full travel 仍 retained，`expect_overlap(blade_steel,handle_shell,axes=x,min=0.005)`）；违反按比例缩 travel | parent L519-527 / retract L411-419 |
| (—) | constraint | — | — | inequality | retract_full 全收：q=0 时 `blade_body.max_x < handle.max_x`（刀片全收进 body）；handle_len / blade_len 配比须满足，违反缩 blade_len 或拒采 | retract L390-397 |
| (—) | constraint | — | — | inequality | fold_pivot 收纳：q=0 时 blade 在 handle footprint 内（`expect_within(blade_body,handle_shell,axes=xy,margin=0.003)` + `expect_overlap(...,axes=x,min=0.030)`）；blade_len ≤ handle 内可容长，违反缩 blade_len（flat_metal slim H 尤其紧，见 §9）| fold L383-401 |
| (—) | constraint | — | — | inequality | flipup_guard 盖刃：q=0 时 `expect_overlap(guard_body,blade_steel,axes=x,min=0.035)` 且 guard_len ≥ 暴露刀片长；违反加长 guard 或缩固定刀片暴露长 | guard L570-578 |
| (—) | constraint | — | — | inequality | channel 容刃：`BLADE_W·blade_width_scale ≤ HANDLE_H·handle_height_scale − channel_top_margin`（刀片宽不超 handle 高可容）；违反缩 blade_width | parent L55-61 |

palette_style 候选（每 seed 采一套，**不计入 slot_choice**，跨 5★ 样本观察的真实材质 / 色集）：
| palette_style | handle | blade | channel/hardware | accent | 来源样本 |
|---|---|---|---|---|---|
| safety_yellow_abs（默认）| 黄 ABS (0.96,0.78,0.10) | stainless (0.80,0.82,0.85) | gray channel (0.62,0.63,0.66) | 黑 grip (0.10,0.10,0.11) + 暗 tip (0.30,0.34,0.46) | parent / hawk / drop / serr / ergo |
| industrial_black | 黑 rubber barrel (0.22,0.22,0.24) | stainless | gray channel | 黑 TPR rib (0.14,0.14,0.16) | overmold |
| red_pro | 红 ABS handle (0.80,0.18,0.14) | stainless | gray channel | 黑 grip | parent yellow 换红外推 |
| steel_brushed | brushed steel bar (0.72,0.73,0.76) | stainless | dark steel channel (0.38,0.40,0.44) | 黑 grip + dark cap (0.28,0.30,0.34) | flat_metal_bar |
| hi_vis_orange_guard | 黄 ABS handle | stainless 固定刀 | gray channel + gray hinge_bracket | 橙 safety guard (0.95,0.45,0.10) | mech_guard（含 brass pivot 配色可与 fold 共用）|

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / 行程 / 角度 / clearance，**绝不改变 deployment / grip / blade 的拓扑**。

## Multiplicity / Copy Logic

- **无模板级可变 multiplicity 轴**：核心结构由固定 named slots（deployment / grip / blade）表达，不暴露刀级 `*_count`，也不通过循环复制模板级 visual/part/joint 形成结构差异轴。source map 明确："no multiplicity slot sweep — N is incidental texture, not a topology axis"。
- **存在 module-local 固定 / 受控 N 的细节阵列（非可变拓扑轴，不进 slot_choice）**：
  - overmold_barrel 的 `tpr_rib_{i}`：源 `for i in range(N_RIBS=8)`（overmold L293-299）发射 N 个环向 TPR rib ring。模板可把 `tpr_rib_count` 作 **module-local 受控参数**（声明域 [4,16]、标称 8、clamp），但**不进 slot_choice**——它只在 overmold_barrel 内部变 rib 密度，不改 deployment / grip / blade 拓扑等价类。
  - ergo_contoured 的 `finger_groove_{i}`：源 `for i in range(4)`（ergo L401-407）发射 4 对 cut+insert。模板可把 `finger_groove_count` 作 **module-local 受控参数**（声明域 [2,5]、标称 4、clamp），同样**不进 slot_choice**。
  - retract_full 的 `post_{i}`：源 `for i in range(2)`（retract L321-333）发射 2 个 blade-mount post，**固定 N=2**（与 trapezoidal blade 的 2 个 mounting hole 绑定，非可变）。
  - blade profile 内的刀刃细节 loop：score line（`for i in range(5)`，snap_off/hawk/drop 风格）/ sheepsfoot 齿（14 via loop，serr L234-239）—— **module-internal 刀刃纹理 loop，固定随 blade module，非 slot 轴 / 非 multiplicity 轴**。
- 这些都是 **module-local 固定 / 受控多份 visual**（rib ring / finger groove / mount post / score line / serration 齿），按 module 而非 multiplicity 轴声明——现实手用刀没有"任意 N 把刀片 / N 个机构"的真实产品域。copied object 用共享 helper 发射、绝对式等距 placement（沿 X 均分 / 环向 revolve 角），无独立 joint（FIXED 装饰 / 纹理 inline 到承载 part，Rule 1）。模板对每根细节 loop 各做 clamp，不编进 `slot_choices_for_seed`。

## 拓扑多样性审计

总组合数：deployment(4) × grip(4) × blade(4) = **64**（其中 1 条 deployment×blade 互斥需 gate，见 §9 — flipup_guard 的刀片 FIXED，4 个 blade profile 仍可注入护罩下的固定刀，**不删 combo**，仅在断言上区分；实质合法组合保持 64，无组合被删）。

仅 deployment(4) × blade(4) = **16 ≥ 10**（已达机械门控）；其中 joint 拓扑差异来自 deployment 的 {PRISMATIC ×2（spine vs clamp+posts 活动件）/ REVOLUTE 绕 Y（fold）/ REVOLUTE 绕 -Y（guard，刀片 FIXED）} 4 类真实 joint-topology 等价类。叠 grip(4)（handle 主壳 mesh 几何差异：rounded-rect loft / palm-swell loft / circular loft / box bar + 固定阵列差异）→ 64，充裕。

理由：deployment × blade 单独即 16 distinct 组合，含 4 类真实 joint 拓扑（PRISMATIC / PRISMATIC(不同活动件) / REVOLUTE-Y / REVOLUTE(-Y, 固定刀)）+ 活动件 part 数差异（carrier / blade / safety_guard）；叠 grip(4)（4 种不同 handle 主壳 mesh helper + 固定阵列）后 64 distinct，远超 ≥10。**deployment / grip / blade 三轴的 part/mesh/joint 差异天然进 `slot_choices_for_seed` 的 tuple**（`("deployment",m)`、`("grip",m)`、`("blade",m)`）。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` 三个 named slot（deployment / grip / blade），经兼容矩阵合法化（deployment×blade 的 flipup_guard 特例 gate：blade 注入固定刀且 deployment 检查改"刀片永久暴露"而非"刀片可收"；fold_pivot×flat_metal_bar 的 slim-body clearance gate），再 uniform 各连续 scale（解析 conditional：slide_travel@滑动、fold_open@fold、guard_open@guard、barrel_radius@barrel），再采 palette_style + module-local rib/groove count。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（重点看 snap_off 推出 / retract 全收 / fold 折出 / guard 翻起 + 各 blade profile + 各 grip handle 形态）。


Controlled local parameterization：见 §参数表的 handle_len/height/width_scale + blade_len/width_scale（independent）+ slide_travel_scale（@滑动）/ fold_open_scale（@fold）/ guard_open_scale（@guard）/ barrel_radius_scale（@barrel）（conditional）+ tpr_rib_count / finger_groove_count（module-local 受控，不进 slot_choice）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 named slot（解析 conditional 范围：slide_travel 仅滑动、fold_open 仅 fold、guard_open 仅 guard、barrel_radius 仅 barrel；rib/groove count 仅对应 grip）→ 采 independent handle/blade scale → 派生（channel 深随 handle_height、slide upper 随 blade_len、barrel 直径随 handle_width 基线）→ 用 5 条 inequality（推出 retained、retract 全收、fold 收纳、guard 盖刃、channel 容刃）投影 / 回缩。跨部件依赖（行程 vs blade_len、blade 收纳 vs handle 内腔、blade 宽 vs handle 高）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 channel-slide / pivot / hinge-barrel captured 接口、PRISMATIC/REVOLUTE joint origin、固定阵列 visual 或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` 三 named slot（deployment/grip/blade），经兼容矩阵合法化，再解析 conditional scale，再 uniform 各 independent scale，采 palette_style + module-local rib/groove count | slot_choices_for_seed 含 `("deployment",m)`/`("grip",m)`/`("blade",m)` 且与 build 一致 |
| compatibility matrix | (1) **flipup_guard × blade**：flipup_guard 刀片**永久固定全露**（无 deployment），4 个 blade profile 仍合法注入护罩下的固定刀，但断言切换：guard 时验"刀片永久暴露 + 护罩 q=0 盖刃 / q=π 翻开"，**不验"刀片收进 body / 推出 nose"**（那是滑动 / 折刀语义）→ gate 为断言分支，不删 combo。(2) **fold_pivot × flat_metal_bar**：flat bar slim（H≈0.014）内腔小，fold 刀片收进 body 余量紧 → fold_open 时 blade_len 须按 slim handle 内腔 clamp（§7 fold 收纳 inequality 收紧 margin），或采样时下调 blade_len_scale；若仍 FAIL 则把该 grip 在 fold 下退到 tapered_molded（fallback）。(3) **retract_full × 各 grip/blade**：retract 全收要求 handle_len ≥ blade_len + 余量 → handle_len_scale / blade_len_scale 联动 clamp（§7 retract 全收 inequality）。(4) deployment×grip 其余正交（任意 grip 配滑动 / fold / guard 合法，仅尺寸联动）；grip×blade 完全正交。 | 无 floating / collision / 刀片穿 handle 壁 / fold 收不进 slim bar / guard 不盖刃 / retract 收不全 / 行程不足或穿 nose |
| controlled local variation | 5 independent + 4 conditional clamped scale + 2 module-local count，每 build 统一；conditional 随 slot 解析 | 比例变化不破坏 channel-slide/pivot/hinge captured、PRISMATIC/REVOLUTE origin、收纳 / 推出 / 盖刃姿态、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | 逐 deployment 机构 QC（滑出 / 全收 / 折出 / 翻护罩）+ 逐 grip handle 形态 + 逐 blade profile |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| deployment | 4 | yes | yes | PRISMATIC(snap_off) / PRISMATIC(retract, clamp+posts 活动件) / REVOLUTE-Y(fold) / REVOLUTE(-Y, 固定刀+guard)；identity = 始终 ≥1 非 fixed joint |
| grip | 4 | yes | yes | tapered_molded / ergo_contoured / overmold_barrel / flat_metal_bar（4 种不同 handle 主壳 mesh helper + 固定阵列）|
| blade | 4 | yes | yes | snap_off_segmented / hawkbill / drop_point / serrated_sheepsfoot（暴露刀片 outline）|

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 `("deployment",m)`/`("grip",m)`/`("blade",m)`；**module-local rib/groove count 与连续 scale 不进 slot_choice**
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 把各 scale clamp 到声明范围；slide_travel/fold_open/guard_open/barrel_radius 为 conditional 随 deployment/grip 解析；tpr_rib_count/finger_groove_count clamp 到 [4,16]/[2,5]；5 条 inequality（推出 retained、retract 全收、fold 收纳、guard 盖刃、channel 容刃）在 resolve 内投影 / 回缩
- compatibility matrix 处理 flipup_guard×blade（断言分支：永久暴露 vs 可收）、fold_pivot×flat_metal_bar（slim 内腔 clearance clamp / fallback）、retract_full handle_len≥blade_len 联动；conditional scale 仅在对应 module 生效（不在 fold/guard 上设 slide_travel，不在非 barrel 上设 barrel_radius）
- 连续 scale clamp 后不破坏 channel-slide / pivot / hinge-barrel captured 接口、PRISMATIC/REVOLUTE joint origin、收纳 / 推出 / 折出 / 盖刃姿态、固定阵列 visual
- 关键 joint：deployment∈{snap_off_slide,retract_full} 时 `handle_to_carrier` **PRISMATIC** axis≈(1,0,0)（abs(axis[0])>0.99、y/z≈0）；fold_pivot 时 `handle_to_blade` **REVOLUTE** axis≈(0,1,0)（abs(axis[1])>0.99）；flipup_guard 时 `handle_to_guard` **REVOLUTE** axis≈(0,-1,0)（abs(axis[1])>0.99）；end_cap（FIXED 候选）`handle_to_cap` FIXED
- captured 接口：element-scoped `allow_overlap`（snap_off：`blade_spine`/`blade_steel`↔`top_channel`；retract：`blade_clamp`↔`top_channel` + `blade_body`↔`handle_shell` + carrier 内 `post_{i}`/`blade_clamp`/`blade_body`；fold：`blade`↔`handle` part-level；guard：`guard_body`↔`hinge_bracket`），照搬各样本 run_tests 的 allow_overlap 段
- 固定 / 受控阵列 visual 遵循 `tpr_rib_{i}`/`finger_groove_{i}`/`post_{i}` 命名 + 绝对式等距 / 环向 placement + Rule 1（无独立 joint）
- deployment 活动件 part 名随 module（`blade_carrier` / `blade` / `safety_guard`）；flipup_guard 时刀片是 handle inline visual（无独立 blade part、无 deployment joint）
- grandfather：所有 channel-slide / pivot / hinge-barrel / part-fold captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守
- rest pose：snap_off q=0（露 ~12mm）/ retract q=0（全收）/ fold q=0（收进 handle）/ guard q=0（盖刃）—— 全部 lower=0 收纳 / 盖住姿态

## Reject cases

- deployment slot 退化为"无非 fixed joint"（如把刀片做成纯 inline 固定 visual 而不带任何机构）→ 违反类别 identity（每个 deployment 候选必须 ≥1 非 fixed joint：滑动 PRISMATIC / 折 REVOLUTE / 护罩 REVOLUTE）。
- flipup_guard 给固定刀片补 `handle_to_carrier` PRISMATIC 或 `handle_to_blade` REVOLUTE（让"固定刀"又能滑 / 折）→ 违反该候选拓扑（guard 候选的刀片永久固定，唯一活动件是 safety_guard 的 -Y REVOLUTE）。
- 把 deployment×blade 的 flipup_guard combo 误删（以为"固定刀不能换 blade profile"）→ 错；guard 下固定刀仍可换 4 种 outline，仅断言分支不同（永久暴露 vs 可收），保留 64 combo。
- fold_pivot 配 flat_metal_bar 时 blade_len 不按 slim 内腔 clamp → 刀片收不进 slim bar（穿模 / 露刃）；须收紧 §7 fold 收纳 inequality margin 或 fallback grip。
- retract_full 的 handle_len < blade_len + 余量 → 刀片 q=0 收不全（front 超 nose）；须 handle_len/blade_len 联动 clamp。
- 把 score line / sheepsfoot 齿 / TPR rib / finger groove / mount post 当独立活动 part 加 joint → 违反 Rule 1（刀刃纹理 / 装饰阵列 / 固定 mount，应 inline 为承载 part visual）。
- 把 tpr_rib_count / finger_groove_count / 任何连续 scale 编进 `slot_choices_for_seed` → 错；它们是 module-local 受控参数 / 安全 scale，不是拓扑等价类轴（slot_choice 只编 deployment/grip/blade 三轴）。
- PRISMATIC / REVOLUTE origin 放在 handle 中心或任意点而非真实 channel rail / nose pivot / hinge bracket 硬件 → `fail_if_articulation_origin_far_from_geometry`（0.015）FAIL。
- snap_off / retract 推出行程过大致刀片脱出 handle（full travel 不再 retained）→ §7 推出 retained inequality FAIL；须缩 travel。
- 给 channel-slide / pivot / hinge-barrel captured 接口补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把连续尺寸 / 颜色 / 材质（palette_style / handle scale）当新 candidate 塞进 slot → 不是结构差异。
- 把剪刀（双臂对剪）/ 菜刀 / 餐刀（固定全长无机构）/ 多工具枢轴簇语义混入 → 出类，本类是单 handle + 单 deployment 机构 + 单刀片的手用工具刀。

## 与相邻类别的边界

- 不该混入：**剪刀（scissors）**——双臂绕中心 pivot 对剪、两片刀刃 + 两环柄；本类是单刀片 + 单 handle + 单 deployment joint，运动 spine 完全不同。
- 不该混入：**菜刀 / 砍刀 / 厨刀（cleaver / chef's knife）**——固定全长大刀片、无 deployment 机构 / 无收纳运动；本类 identity 在刀片有可动机构（滑 / 折 / 护罩）。
- 不该混入：**餐刀 / 黄油刀（table / butter knife）**——固定全长钝刀、无机构 / 无 channel；无活动 joint 出类。
- 不该混入：**纯固定刀（fixed-blade carving / scalpel 无护罩）**——除非配 flip-up-guard（本类 Slot A 第 4 候选覆盖"固定刀 + 翻护罩"），否则纯固定无机构出类。
- 不该混入：**多功能瑞士军刀 / multi-tool 多枢轴工具簇**——多个独立 REVOLUTE 工具叠一柄；本类是单 deployment + 单刀片（若需可作单独 slug）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | （待人工审核：确认 (1) **deployment 是核心 identity 槽**，snap_off_slide 与 retract_full 共享 PRISMATIC 但活动件 part 树（blade_spine vs blade_clamp+post×2）+ 收回深度不同，是否接受为 2 个 distinct module（source map 明确两者都留）；(2) **flipup_guard×blade 不删 combo、仅断言分支**（固定刀仍可换 4 种 outline，guard 时验"永久暴露 + 护罩盖 / 翻"而非"收 / 推"）是否接受，保持 64 combo；(3) **fold_pivot×flat_metal_bar** 的 slim 内腔 clearance 处理：blade_len clamp 收紧 vs fallback 退 tapered_molded，哪种为首版策略；(4) **grip 列为真正结构层**（4 种不同 handle 主壳 mesh helper：rounded-rect loft / palm-swell loft / circular barrel loft / box bar + 固定阵列）而非纯 mesh-helper 维度，是否同意；(5) tpr_rib_count [4,16] / finger_groove_count [2,5] 作 **module-local 受控参数不进 slot_choice**（无刀级 multiplicity 轴）是否符合 multiplicity 审计期望；(6) Topology target 64<300 的说明是否接受（本小类真实结构上限）；(7) palette_style 5 套（safety_yellow_abs / industrial_black / red_pro / steel_brushed / hi_vis_orange_guard）是否合适，red_pro 为黄换红外推；(8) end_cap 统一为 FIXED part（多数样本范式）、retract_full 风格 inline 仅作 module-local 选项不进 slot_choice，是否接受。）|（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）
- **deployment 活动件统一约定**：handle 长轴 +X、坐地；snap_off/retract 的 carrier PRISMATIC axis=(1,0,0)（沿 channel 推出 nose）；fold 的 blade REVOLUTE axis=(0,1,0) origin 在 nose 附近 pivot；guard 的 safety_guard REVOLUTE axis=(0,-1,0) origin 在刃口上方 hinge_bracket。blade profile（Slot C）注入 deployment 活动件的 `blade_steel`/`blade_body` visual（snap_off/retract/fold）或 handle inline blade（guard）。
- **共享 helper**：`_handle_body_shape`（按 grip 切 rounded-rect / palm-swell / box bar profile）/ `_build_barrel_body`（overmold circular loft）；`_channel_cut`/`_build_top_channel_visual`（滑动机构 channel，snap_off/retract）/ `_blade_exit_groove`（fold）；`_build_blade_shape`（按 blade 切 snap_off 平行四边形 / hawkbill spline / drop_point polyline / sheepsfoot 齿 outline）+ `_build_blade_score_lines`（snap_off/hawk/drop，score）/ `_sheepsfoot_outline_pts`（serr 齿）；`_build_thumb_button`（snap_off/retract）/ `_build_thumb_stud`（fold）；`_build_guard_body`（guard）；`_build_tpr_rib`（barrel grip）/ `_finger_groove_cuts`+`_build_single_groove_insert`（ergo grip）/ `_knurl_bumps_side`+`_knurl_bumps_xy`（flat grip 共享 knurl，flat L85-143 已抽出）。
- captured 接口 allow_overlap：`run_knife_tests` 里逐 module 补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（parent L467-503、retract L451-522、fold L377-401、guard L631-647）。
- conditional 范围解析顺序：先采 deployment / grip / blade → 解析 slide_travel（仅滑动）/ fold_open（仅 fold）/ guard_open（仅 guard）/ barrel_radius（仅 barrel）/ tpr_rib_count（仅 barrel）/ finger_groove_count（仅 ergo）→ 采 independent handle/blade scale → 派生 channel 深（随 handle_height）+ slide upper（随 blade_len）+ barrel 直径（随 handle_width）→ 投影 5 条 inequality（推出 retained、retract 全收、fold 收纳、guard 盖刃、channel 容刃）。
- **flat_metal_bar slim 基线**：flat 的 `HANDLE_H≈0.014`（远小于其余 grip 的 0.026），channel_depth/blade_width 基线须随 grip 切换；fold_pivot×flat 的内腔收纳尤其紧（见 §9），实现时优先收紧 fold 收纳 inequality 或在该 combo 下下调 blade_len_scale 采样上限。
- **end_cap 范式**：默认 `end_cap` 为独立 FIXED part（parent/fold/guard/各 blade/各 grip 范式，`handle_to_cap` FIXED + `expect_contact` + cap 在 -X 端）；retract_full 源把 end_cap inline 进 handle visual——模板取 FIXED part 为统一范式（多数样本），inline 风格不进 slot_choice。
- 参考模板：选运动拓扑相近的——root chassis + 单可动 deployment child（cushion 的 base + 互斥 lid 机构 REVOLUTE/PRISMATIC + interior 互斥 / clamp 的 frame + screw PRISMATIC + 可选 pad/lever REVOLUTE / shopping_bucket 的 telescoping PRISMATIC + 翻盖 REVOLUTE）；knife 的 handle→(carrier PRISMATIC / blade REVOLUTE / guard REVOLUTE) 互斥 deployment 与 cushion/clamp 的"互斥主机构槽 + 共享 root"同构。knife 尺度小（handle ~0.150m、blade ~0.050-0.060m、channel/pivot/hinge 硬件 mm 级），joint origin 须精确落真实硬件面（channel rail / nose pivot / hinge bracket，≤0.015m baseline）。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B / C（parent 基线）| snap_off_slide + tapered_molded + snap_off_segmented | rec_build-...-knif_..._211319cd | `_handle_body_shape` L74-109 / `_build_top_channel_visual` L144-152 / `_build_thumb_grip_visual` L155-178 / `_build_blade_shape` L184-209 / `_build_blade_score_lines` L212-227 / `_build_blade_tip_visual` L230-248 / `blade_carrier` L324-366 / `handle_to_carrier` PRISMATIC L372-382 / `handle_to_cap` FIXED L385-391 / allow_overlap L467-503 | 基线 handle + 滑出 carrier（PRISMATIC）+ molded grip + snap-off blade + channel-slide captured 范式 + FIXED end_cap |
| S2 | A | retract_full | rec_knife_var_mech_retract | `_build_trapezoidal_blade_shape` L178-208 / `_build_blade_clamp` L211-217 / `_build_clamp_post` L220-228 / `post_{i}` for i in range(2) L321-333 / `handle_to_carrier` PRISMATIC origin=(0,0,channel底) L349-359 / end_cap inline L282-286 / allow_overlap L451-522 | 全收滑出（PRISMATIC，clamp+2 post 活动件，q=0 全收进 body，inline end_cap）|
| S3 | A | fold_pivot | rec_knife_var_mech_fold | `_blade_exit_groove` L111-124 / `_build_pivot_bolster` L134-144 / `_build_front_bolster` L147-158 / `blade` part + `_build_blade_body` L194-211 + `_build_thumb_stud` L234-245 / `handle_to_blade` REVOLUTE axis=(0,1,0) L321-334 / allow_overlap L377-401 | 折刀（REVOLUTE 绕 Y，blade 折进 handle / 摆出前 groove，brass pivot + bolster）|
| S4 | A | flipup_guard | rec_knife_var_mech_guard | `_build_hinge_bracket` L258-290 / 固定刀 inline L425-439 / `_build_guard_body`（barrel+plate+skirts+lip+ribs）L296-390 / `safety_guard` L457-462 / `handle_to_guard` REVOLUTE axis=(0,-1,0) L478-488 / allow_overlap L631-647 | 固定刀 + 翻护罩（REVOLUTE 绕 -Y，刀片 FIXED inline，guard 盖 / 翻刃口，hinge_bracket ears）|
| S5 | B | ergo_contoured | rec_knife_var_grip_ergo | `_handle_body_shape` palm-swell 8 段 L80-125 / `_finger_groove_cuts` L160-185 / `_groove_positions` L188-196 / `_build_single_groove_insert` L199-228 / `finger_groove_{i}` for i in range(4) L401-407 | 人体工学 contoured handle（palm swell + 4 finger groove + rubber insert 固定阵列）|
| S6 | B | overmold_barrel | rec_knife_var_grip_overmold | `_barrel_radius_at` L89-99 / `_build_barrel_body` circular loft L102-115 / `_build_tpr_rib` revolved ring L162-178 / `tpr_rib_{i}` for i in range(N_RIBS=8) L293-299 | 圆 rubber-overmolded barrel handle（circular loft + N TPR rib ring 固定阵列）|
| S7 | B | flat_metal_bar | rec_knife_var_grip_flat | `_handle_body_shape` box uniform bar L149-160 / `_blade_exit_slot` L194-205 / `_knurl_bumps_side` L116-143 / `_knurl_bumps_xy` L85-113 / 侧 `thumb_grip` L233-262 | slim 方截面金属 bar handle（box uniform + edge fillet + 侧 knurl grip + 共享 knurl helper）|
| S8 | C | hawkbill | rec_knife_var_blade_hawk | `_build_blade_shape` spline 凹刃+钩 L188-218 / `_hawkbill_edge_z` L221-241 / `_build_blade_score_lines` L243-260 / `_build_blade_tip_visual` L263-282 | 鹰嘴 blade outline（凹刃 + 下钩 tip）|
| S9 | C | drop_point | rec_knife_var_blade_drop | `_build_blade_shape` drop-point polyline L187-217 / `_build_blade_grind_line` L220-242 / `_build_blade_tip_visual` L245-270 | drop-point trimming blade outline（缓降 spine + belly + 居中尖 + bevel）|
| S10 | C | serrated_sheepsfoot | rec_knife_var_blade_serr | `_sheepsfoot_outline_pts`（14 齿 loop）L180-245 / `_build_blade_shape` L248-263 / `_build_blade_tip_visual` L266-308 | 锯齿 sheepsfoot blade outline（14 三角齿刃 + 钝圆 tip）|
</content>
</invoke>
