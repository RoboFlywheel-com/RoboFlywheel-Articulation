# wrench (adjustable / movable wrench) — Modular Spec

> 来源小类：`picture/Handtools/Wrench`（articraft_data 上游小类样本池）。
> 上游 source map：`picture_expansion/template_source_maps/Handtools__Wrench.md`（pattern = parallel_children）。
> **"Wrench" 在此 = 可调 / 活动扳手（adjustable / movable wrench）**：一只长把手 + 一个带**固定颚 + 活动颚**的头部机构，活动颚由 PRISMATIC 滑动开合，并由一个旋转驱动件（蜗杆 / 旋调螺母 / 拇指杆）驱动。**身份硬约束：每个候选都必须保留 ≥1 个非 fixed 关节**（活动颚 PRISMATIC）。刚性 open-end / box-end / combination 扳手（0 活动关节）**不收**，是 documented reject case。
>
> **同步状态**：本 spec 引用的 8 个 5 星样本（2 个 parent + 3 个原 fork 槽位变体 + **3 个新补造的 cross-spine 把手变体**）已同步进本仓库 `data/records/<id>/`，`rating=5`（已逐一核对 `record.json`）。行号按各样本本仓库 `revisions/rev_000001/model.py` 实际行号计（已逐一核对）。引用以 part / joint / helper **名字** 为准（`wrench_body` / `head_frame` / `movable_jaw` / `worm_screw` / `adjust_nut` / `thumb_lever` / `jaw_slide` / `worm_turn` / `frame_to_jaw` / `frame_to_nut` / `lever_pivot` / `_build_head_local` / `_build_head_frame` / `build_head_frame_geometry` / `build_handle_geometry` / `build_tube_handle_geometry` / `_build_wood_grip` / `_build_tubular_shank` / `build_flat_handle_geometry` / `_add_teeth_x` 等），行号仅作定位。
>
> **2026-06 更新（handle 与 head-spine 解耦）**：原 spec 有 BLOCKER——handle 绑定 head-spine（crescent 只配 flat_steel，pipe 只配 wood/tubular），合法组合仅 5 < 10 拓扑门控。已**上游回 fork 池补造 3 个 cross-spine 把手变体**（`rec_wrench_var_crescent_wood` 证 crescent-spine 接受 wood、`rec_wrench_var_crescent_tubular` 证 crescent-spine 接受 tubular、`rec_wrench_var_pipe_flatsteel` 证 pipe-spine 接受 flat steel）。**handle 现已与 head-mechanism 正交**（不再 spine-gated），合法组合提至 crescent-spine heads{worm_rack, monkey, thumb}=3 × handle{flat, wood, tubular}=3 = 9，加 pipe-spine head{screw_nut}=1 × handle 3 = 3，= **12 ≥ 10（PASS）**。模板侧的唯一约束改为：handle module 的锚定坐标系必须按所选 head 的 spine **rebase**（crescent 就地 `wrench_body` 原位 vs pipe 经 `_lay()` 放倒的 `head_frame`），见 §9 / §13。

## 元信息
| 项 | 值 |
|---|---|
| slug | `wrench` |
| template path | `agent/templates/Handtools_Wrench.py` |
| test path (optional) | `tests/agent/test_wrench_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（root body / frame + head_mechanism slot 的活动颚 / 驱动件 + handle slot 的把手 visual 挂到共同 root；无 multiplicity 轴）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8（2 parent + 3 fork 头机构/把手变体 + 3 cross-spine 把手变体；均 converged：compile 成功、均含 ≥1 非 fixed joint（活动颚 PRISMATIC）、workbench-only）|
| read_count | 8（**全部读完整 `model.py`**，不抽样；含每个样本的 build helpers、part 树、articulation 与 run_tests）|
| read_scope | all 5-star samples in this category |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14；本批 8/8 全部被采纳，无未采用样本 |

阅读要点（用于槽位分解）：
- **样本池含两条运动 spine**（决定 head_mechanism 的 root builder；handle 经 rebase 可挂任一 spine）：
  - **Crescent spine**（parent A `6f106d91` + monkeyhead + thumbslide + crescent_wood + crescent_tubular）：root part = **`wrench_body`**，在世界 XY 平面就地平铺（`Z_LIFT`）。活动颚 = `movable_jaw`，`jaw_slide` **PRISMATIC**；驱动件 = `worm_screw`（`worm_turn` CONTINUOUS 绕滑动轴）或 `thumb_lever`（`lever_pivot` REVOLUTE 绕 Z）。**把手锚在 crescent root（in-place）**：可为扁钢条 + hex ring 蝶端（parent A，`_build_body` 内联）、锥木 + ferrule + 钢 butt（crescent_wood，`_build_wood_grip`+`_build_ferrule`+`_build_butt_cap` 沿世界 +X revolve + 钢 tang 贯穿）、或圆钢管 + 端 ferrule（crescent_tubular，`_build_tubular_shank` 沿世界 +X revolve，inline 进 `body_shell`）。
  - **Pipe spine**（parent B `4c74c601` + tubularshank + pipe_flatsteel）：root part = **`head_frame`**，在 tool frame 内创建后用 `LAY_RPY`/`_lay()` 整体放倒。活动颚 = `movable_jaw`，`frame_to_jaw` **PRISMATIC**（tool 长轴 = 世界 +X）；驱动件 = `adjust_nut`（`KnobGeometry` 滚花螺母，`frame_to_nut` CONTINUOUS）。**把手在 tool frame 沿 local −Z 创建后经 `_lay()`/`LAY_RPY` 挂 root**：可为锥木（parent B，`build_handle_geometry`+ferrule+worn+butt）、圆钢管 + grip ribs（tubularshank，`build_tube_handle_geometry`）、或扁锻钢条 + hex ring 蝶端（pipe_flatsteel，`build_flat_handle_geometry` 锥形 bar + hex 通孔 ring）。
- **head_mechanism 轴（Slot A）= 真正的 part 树 / joint 拓扑变化轴**：worm_rack_crescent（`movable_jaw` PRISMATIC + `worm_screw` CONTINUOUS，斜置 lens 头 + 角度颚口 + 蜗杆啮合 rack 齿）/ screw_nut_pipe（`movable_jaw` PRISMATIC + `adjust_nut` CONTINUOUS，钩颚 + housing window 内滚花螺母 + 双排锯齿）/ monkey_head（`movable_jaw` PRISMATIC 沿 −Y + `worm_screw` CONTINUOUS，方框头 + 平行平颚）/ thumb_slide（`movable_jaw` PRISMATIC + `thumb_lever` **REVOLUTE** 绕 Z，拇指杆 quick-adjust）。**每个候选 part 数 / joint 类型组合各异**（2 driver part 风格 vs lever REVOLUTE）。head_mechanism 仍决定 root 类型与 spine。
- **handle 轴（Slot B）= mesh / visual 维度，现与 head_mechanism 正交**：flat_steel（扁钢条 + hex ring 蝶端：crescent 用 parent A 内联 `_build_body`，pipe 用 `build_flat_handle_geometry`）/ tapered_wood（lathe 锥木 + ferrule + worn band + 钢 butt：pipe 用 `build_handle_geometry`，crescent 用 `_build_wood_grip`+`_build_ferrule`+`_build_butt_cap`+钢 tang）/ tubular（圆管 + grip ribs + 圆盘 cap：pipe 用 `build_tube_handle_geometry`，crescent 用 `_build_tubular_shank`）。把手不引入新活动关节，但**绑定 root 坐标约定**——故模板侧每个 handle 需按 spine 提供两套锚定（crescent 沿世界 +X 就地 revolve/extrude vs pipe 在 tool frame 沿 −Z 创建后 `_lay()`）。**3 个 cross-spine 样本已证 3 种 handle 均可同时挂 crescent 与 pipe spine**（见 Slot B 表 + §9）。
- **齿是 module 内部循环发射，非 slot 轴**：crescent rack 齿 `for i in range(5)`（parent A L251-259 / monkeyhead L242-248）、pipe 钩颚 + 活动颚锯齿 `_add_teeth_x(n_teeth=6)`（parent B / tubularshank）、grip 肋 / 脊 `for i in range(N)`（monkeyhead grip ridges L312-321 / thumbslide L337-346 / tubularshank grip ribs L407-414）。齿数 / 肋数是 module 内固定参数，**不作为独立 slot multiplicity 轴**（见 §8）。

## 核心身份

一只**可调 / 活动扳手**（adjustable / movable wrench）：一只细长把手（长轴沿世界 +X，扳手平铺于地面 z_min≈0），把手一端连一个**头部机构**——头内有一只与头一体的**固定颚**和一只可沿头部滑槽移动的**活动颚**（`movable_jaw`），活动颚由 **PRISMATIC 关节**开合颚口以夹不同尺寸的工件，由一个**旋转 / 摆动驱动件**（滚花蜗杆 `worm_screw` 绕滑轴 CONTINUOUS / 滚花旋调螺母 `adjust_nut` 绕工具长轴 CONTINUOUS / 拇指杆 `thumb_lever` 绕 Z REVOLUTE）操控。颚面带锯齿 / 平面（crescent 角度颚口 / monkey 平行平颚 / pipe 钩颚 + 上下排锯齿）。把手为扁锻钢条（带 hex 通孔 ring 蝶端）/ 锥形红木把（ferrule + 磨损带 + 钢 butt cap）/ 圆钢管（grip 肋 + 圆盘 cap）。

活动语义 = **活动颚的 PRISMATIC 滑动开合**（恒在）+ **驱动件转动**（worm/nut CONTINUOUS 或 lever REVOLUTE）。默认成熟域：head_mechanism × handle 的**全笛卡尔积**——handle 现与 head_mechanism 正交（3 cross-spine 样本已证 3 种把手均可挂 crescent 与 pipe 两条 spine），模板侧按所选 head 的 spine **rebase** handle 锚定坐标系（crescent 就地 vs pipe `_lay()` 放倒），不再 spine-gate。合法组合 = crescent heads(3)×handle(3) + pipe head(1)×handle(3) = **12**。尺度 ~0.30–0.45 m 长。

不该混入：
- **刚性 open-end / box-end / combination 扳手**（呆扳手 / 梅花扳手 / 两用扳手）——**0 个活动关节**，纯实心铸件，违反 ≥1 非 fixed joint 的身份硬约束。是 documented reject case（见 §10）。
- **套筒扳手 / 棘轮扳手（socket / ratchet wrench）**——主机构是棘轮方榫 / 套筒插换，不是滑动颚；运动 spine 与本类（滑动颚 + 旋调驱动）不同。
- **螺丝刀 / 钳子 / 老虎钳（pliers）**——钳是双臂绕单销 REVOLUTE 剪式，无滑动颚 + 旋调驱动的扳手身份。

## 槽位 + 候选模块表

> **建模注记**：wrench 是 **root（`wrench_body` 或 `head_frame`）+ parallel children**——head_mechanism slot 发射活动颚 `movable_jaw`（PRISMATIC child）+ 驱动件（worm/nut/lever child）并把固定颚 / housing 内联进 root visual；handle slot 决定 root 的把手 mesh。**关键约束（已修正）**：head_mechanism 决定 root 类型与运动 spine（crescent 就地 XY 平铺 `wrench_body` vs pipe tool-frame `_lay()` 放倒 `head_frame`）；handle **现与 head_mechanism 正交**——模板侧每个 handle module 须提供按 spine 的 **rebase**（crescent 锚：沿世界 +X 就地 revolve/extrude 进/挂 `wrench_body`；pipe 锚：在 tool frame 沿 local −Z 创建后经 `_lay()`/`LAY_RPY` 挂 `head_frame`）。3 个 cross-spine 样本已证 3 种把手均可挂两条 spine，故 Slot A × Slot B = **4×3=12 全合法笛卡尔积**（crescent heads 3 × handle 3 = 9，pipe head 1 × handle 3 = 3）。

### Slot A：head_mechanism（头部机构——**主机构槽**，决定活动颚 + 驱动件 part 树与 joint 拓扑）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 关键 joint / 结构特征 |
|---|---|---|---|---|
| worm_rack_crescent（基线） | rec_..._wren_..._6f106d91（parent A） | `_build_head_local` L125-172 / `_build_movable_jaw`（rack 齿 `for i in range(5)`）L217-267 / `_build_worm` L270-292 / `jaw_slide` PRISMATIC L335-346 / `worm_turn` CONTINUOUS L349-364 | eligible if compatible | 斜置（`HEAD_TILT_DEG=15`）lens/teardrop 头板，角度颚口；`movable_jaw`（颚块 + 内嵌 rack shank）**PRISMATIC** 沿斜滑轴 axis=(-1,0,0)；滚花 `worm_screw` **CONTINUOUS** axis=(1,0,0) 绕滑轴，蜗杆 rim 透两面 thumb windows 啮合 rack 齿。**crescent spine** |
| screw_nut_pipe | rec_..._wren_..._4c74c601（parent B） | `build_head_frame_geometry`（钩颚 + housing + window + 锯齿 `_add_teeth_x(n_teeth=6)`）L168-247 / `build_movable_jaw_geometry` L250-285 / `KnobGeometry` 螺母 L358-373 / `frame_to_jaw` PRISMATIC L379-387 / `frame_to_nut` CONTINUOUS L391-399 | eligible if compatible | 弯钩固定颚（下排锯齿）+ housing（nut window + 前 jaw channel）；`movable_jaw`（screw bar + 上排锯齿头）**PRISMATIC** 沿工具长轴 axis=(0,0,1)（世界 +X）；滚花 `adjust_nut`（`KnobGeometry` knurled）**CONTINUOUS** 绕同轴。**pipe spine**（tool-frame 放倒）|
| monkey_head | rec_wrench_var_monkeyhead | `_build_head_frame` L121-158 / `_build_movable_jaw`（rack 齿 `for i in range(5)`，`_rack_tooth` helper L201-208）L211-250 / `_build_worm` L253-275 / `jaw_slide` PRISMATIC axis=(0,-1,0) L343-355 / `worm_turn` CONTINUOUS L358-368 | eligible if compatible | 矩形头框（**无倾斜**，颚口垂直把手轴），**平行平颚**（vs crescent 角度颚口）；下颚 `movable_jaw`（shoe + shank）**PRISMATIC** 沿 −Y；滚花 `worm_screw` **CONTINUOUS** 绕 X 啮合 shank rack 齿。**crescent spine** |
| thumb_slide | rec_wrench_var_thumbslide | `_build_thumb_lever` L245-294 / `_build_movable_jaw`（无 rack 齿）L217-242 / `jaw_slide` PRISMATIC L351-364 / `lever_pivot` **REVOLUTE** axis=(0,0,1) L367-384 / grip ridges `for i in range(N_GRIP_RIDGES)` L337-346 | eligible if compatible | crescent 头廓 retained，但驱动件换为**拇指快调杆**：`movable_jaw`（颚块 + 滑 shank，无齿）**PRISMATIC** 沿斜滑轴；`thumb_lever`（engagement tab + arm + thumb pad）**REVOLUTE** 绕 Z 在头面 boss 销上，tab 扫入滑槽推动颚。**crescent spine**（唯一带 REVOLUTE 驱动）|

> 4 个候选均 ≥2 part（root + movable_jaw + 驱动件），均含 ≥1 非 fixed joint。无单候选 slot。driver-joint 拓扑覆盖 CONTINUOUS×3（worm 绕 X 斜颚 / nut 绕长轴钩颚 / worm 绕 X 方颚）+ REVOLUTE×1（lever 绕 Z），colliding rack 啮合 vs nut 包覆 vs lever tab 推送三种 captured 接口。

### Slot B：handle（把手 / shank——mesh / visual 维度，**与 head_mechanism 正交**，按 spine rebase 锚定）

> **每个 handle type 现有 2 条 spine 的源支持**（原 spine 内基线 + cross-spine 补造样本），证明该把手可挂 crescent 与 pipe 两条 spine。模板侧每个 handle module 提供两套锚定 builder（crescent 就地 vs pipe `_lay()`）。

| module_name | 5_star_source（crescent 锚 / pipe 锚） | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| flat_steel | **crescent**: rec_..._wren_..._6f106d91（parent A；monkeyhead / thumbslide 同形）/ **pipe**: rec_wrench_var_pipe_flatsteel | crescent: `_build_body`（ring 蝶端 + 扁钢把手内联）L175-214 + hex `_hex_profile` L115-122。pipe: `build_flat_handle_geometry`（锥形 bar + hex 通孔 ring + forged grooves）**L293-353** / hex `polygon(6,d)` L329-335 / 装配经 `_lay()`+`LAY_RPY` 挂 `head_frame` visual **L380-385** | eligible if compatible（两条 spine） | 扁锻钢条把手 + hex 通孔 box-ring 蝶端。crescent 锚：与就地 XY 头板共体 union 进 `wrench_body`（`HANDLE_W=0.026`×`HANDLE_T=0.0085`）。pipe 锚：tool-frame 锥形 bar（`HANDLE_W_TOP=0.026`→`HANDLE_W_RING=0.020`，`HANDLE_T=0.010` 薄向）+ hex ring（`RING_OD=0.034`/`RING_AF=0.019`），经 `_lay()` 挂 `head_frame`（**非独立 part**）|
| tapered_wood | **pipe**: rec_..._wren_..._4c74c601（parent B）/ **crescent**: rec_wrench_var_crescent_wood | pipe: `build_handle_geometry`（lathe revolve 锥木）L419-439 / ferrule L404-416 / `build_worn_band_geometry` L442-458 / `build_butt_cap_geometry`（钢尖）L461-477 / 装配 L313-347。crescent: `_build_wood_grip`（spline 半廓沿世界 +X revolve 360°）**L233-267** / `_build_ferrule`（黄铜颈圈）**L270-283** / `_build_butt_cap`（钢盘）**L286-298** / `_build_body_core`（ring + 钢 tang 贯穿 grip + 头）**L192-230** / 装配 visual **L386-407** | eligible if compatible（两条 spine） | 锥形红漆木把（中段最粗 lathe revolve）+ ferrule 颈圈 + 裸木磨损带 / 钢 butt cap。pipe 锚：4 lathe visual 经 `_lay()` 挂 `head_frame`。crescent 锚：木 grip 沿世界 +X revolve（`GRIP_MAX_R=0.014`）+ 黄铜 ferrule + 钢 butt + 隐藏钢 tang（`TANG_R=0.003`）把 ring/头串成 `wrench_body`（**非独立 part**）|
| tubular | **pipe**: rec_wrench_var_tubularshank / **crescent**: rec_wrench_var_crescent_tubular | pipe: `build_tube_handle_geometry`（中空圆管）L307-330 / `build_grip_rib_geometry` L345-361 / grip ribs `for i in range(GRIP_RIB_COUNT)` L407-414 / `build_butt_cap_geometry` L333-342。crescent: `_build_tubular_shank`（annular 廓沿世界 +X revolve 360° + 端 ferrule 环）**L165-204** / `_build_body`（tube ∪ 斜置 crescent 头）**L207-219** / 装配 visual（inline 进 `body_shell`）**L311-316** | eligible if compatible（两条 spine） | 直壁等截面中空圆钢管 + 端 ferrule / grip 环肋。pipe 锚：管 + `GRIP_RIB_COUNT=6` 环肋经 `_lay()` 挂 `head_frame`。crescent 锚：`SHANK_R=0.013`/`SHANK_WALL=0.002` annular tube 沿世界 +X revolve + butt ferrule 环（`FERRULE_R=0.0145`），inline 进 `wrench_body` 的 `body_shell`（**非独立 part**）|

> **handle 现与 head_mechanism 正交（无 spine gating）**：3 种把手均有 crescent + pipe 两条 spine 的 5★ 源支持（原 spine 基线 + cross-spine 补造样本）。模板侧约束改为 **spine-rebase**——handle module 不再被 head 的 spine 排他，而是按所选 head 的 spine 选对应锚定 builder（crescent 沿世界 +X 就地 revolve/extrude；pipe 在 tool frame 沿 local −Z 创建后 `_lay()`/`LAY_RPY` 挂 root）。**handle slot 3 candidate（≥3 ✓），每候选有真实 `model.py:Lx-Ly`，无单候选 slot**。组合预审见 §9：合法组合 = crescent heads(3)×handle(3) + pipe head(1)×handle(3) = 9 + 3 = **12 ≥ 10（PASS）**，与源 map §组合数预审一致。

## 槽位图（slot graph）

pattern: parallel_children（head_mechanism 的活动颚 / 驱动件 + handle 的把手 visual 挂到共同 root；**head_mechanism 决定 root 类型与运动 spine**，handle **与之正交**——按 spine rebase 锚定）

```
root  (head_mechanism 决定: crescent spine -> wrench_body (就地 XY 平铺);
       pipe spine -> head_frame (tool-frame 创建后 _lay() 放倒))
  │   坐标: 长轴沿世界 +X (把手 butt 在 -X, 头在 +X); 平铺 z_min ≈ 0
  │
  ├── [head_mechanism slot]  (互斥四选一; 决定 spine + root)
  │     ├─ worm_rack_crescent : movable_jaw ─[jaw_slide: PRISMATIC axis=-X, origin=斜滑轴铰点]   (crescent)
  │     │                       worm_screw ──[worm_turn: CONTINUOUS axis=+X, origin=头内蜗杆 pocket]
  │     ├─ screw_nut_pipe      : movable_jaw ─[frame_to_jaw: PRISMATIC axis=+Z(tool)=世界+X, origin=nut seat window]  (pipe)
  │     │                       adjust_nut ──[frame_to_nut: CONTINUOUS axis=+Z(tool), origin=screw bar 中线]
  │     ├─ monkey_head         : movable_jaw ─[jaw_slide: PRISMATIC axis=-Y, origin=cutout 中心]   (crescent)
  │     │                       worm_screw ──[worm_turn: CONTINUOUS axis=+X, origin=back wall pocket]
  │     └─ thumb_slide         : movable_jaw ─[jaw_slide: PRISMATIC axis=-X, origin=斜滑轴铰点]   (crescent)
  │                             thumb_lever ─[lever_pivot: REVOLUTE axis=+Z, origin=头面 boss 销]
  │
  └── [handle slot]  (root 的把手 visual, 无独立活动关节; 与 head 正交, 按 spine REBASE 锚定)
        │   spine-rebase: crescent -> 沿世界 +X 就地 revolve/extrude 进/挂 wrench_body;
        │                 pipe     -> tool frame 沿 -Z 创建后 _lay()/LAY_RPY 挂 head_frame
        ├─ flat_steel    : 扁钢条 + hex ring 蝶端   (crescent: 内联 _build_body; pipe: build_flat_handle_geometry+_lay)
        ├─ tapered_wood  : 锥木 + ferrule + 磨损带 + 钢 cap  (crescent: _build_wood_grip+tang; pipe: build_handle_geometry+_lay)
        └─ tubular       : 圆钢管 + 端 ferrule / grip 环肋   (crescent: _build_tubular_shank; pipe: build_tube_handle_geometry+_lay)
```

接口点位与 joint 语义：
- **head_mechanism 接口（互斥四选一，决定 root spine）**：
  - worm_rack_crescent：`movable_jaw` rack shank captured 进头板 slide slot（`jaw_slide` PRISMATIC，origin=斜滑轴铰点 `(HANDLE_X1 + JAW_ORIGIN_LX·cos, JAW_ORIGIN_LX·sin, Z_LIFT)`，rpy yaw=tilt，axis=(-1,0,0)，q∈[0, `JAW_TRAVEL`=0.018]）；`worm_screw` captured 进头内蜗杆 pocket（`worm_turn` CONTINUOUS，origin 落蜗杆中心，axis=(1,0,0)）。蜗杆 rim 啮合 rack 齿（colliding captured）。
  - screw_nut_pipe：`movable_jaw` screw bar 滑进 housing channel（`frame_to_jaw` PRISMATIC，origin=`_lay(0,0,WINDOW_Z)` rpy=`LAY_RPY`，axis=(0,0,1) tool=世界+X，q∈[0, `JAW_TRAVEL`=0.024]）；`adjust_nut` 坐进 nut window 包覆 screw bar（`frame_to_nut` CONTINUOUS，origin=`_lay(0.004,0,WINDOW_Z)`，axis=(0,0,1) 与滑轴共线）。
  - monkey_head：`movable_jaw` shank captured 进矩形头框 cutout channel（`jaw_slide` PRISMATIC，origin=`(cut_x_mid, JAW_FACE_Y_REST, Z_LIFT)`，axis=(0,-1,0)，q∈[0, `JAW_TRAVEL`=0.016]）；`worm_screw` captured 进 back wall pocket（`worm_turn` CONTINUOUS axis=(1,0,0)）。
  - thumb_slide：`movable_jaw` shank captured 进头板 slide slot（`jaw_slide` PRISMATIC 同 crescent，axis=(-1,0,0)）；`thumb_lever` bore 套头面 boss 销（`lever_pivot` REVOLUTE，origin=`(boss_x, boss_y, Z_LIFT+HEAD_T/2)` rpy yaw=tilt，axis=(0,0,1)，q∈[0, `LEVER_TRAVEL`=0.50]）；lever tab 扫入滑槽推 jaw shank（colliding tab/shank）。
- **handle 接口（root visual，无独立活动关节，按 spine REBASE 锚定，与 head 正交）**：
  - **crescent 锚（head ∈ {worm_rack, monkey, thumb}）**：把手沿世界 +X 就地 revolve/extrude 进/挂 `wrench_body`——flat_steel 扁钢条 + ring 与头板共体内联（`_build_body`，无接口面，整体 union）；tapered_wood 木 grip 沿 +X revolve + 黄铜 ferrule + 钢 butt + 隐藏钢 tang（`TANG_R=0.003`）贯穿 grip 把 ring/头串成核心（`_build_body_core` L192-230 + `_build_wood_grip` L233-267）；tubular annular tube 沿 +X revolve + butt ferrule 环 inline 进 `body_shell`（`_build_tubular_shank` L165-204 + `_build_body` L207-219）。
  - **pipe 锚（head = screw_nut_pipe）**：把手在 tool frame 沿 local −Z 创建后经 `Origin(xyz=_lay(...), rpy=LAY_RPY)` 挂 `head_frame`——tapered_wood / tubular lathe / 管 visual（parent B / tubularshank，shank 下端插木 ferrule / 管壁径向 overlap，见 tubularshank `SHANK_INSERTION=0.005`）；flat_steel 锥形 bar + hex ring（`build_flat_handle_geometry` L293-353，经 `_lay()` 挂 root，L380-385）。
- **mating policy**：所有 jaw slide / worm pocket / nut window / lever boss 是 captured-fit（shank-in-slot / cylinder-in-pocket / nut-around-bar / pin-in-bore），几何非两轴对齐面对接 → **省略 MatingContract（grandfather）**，由 `fail_if_articulation_origin_far_from_geometry` 守 origin + element-scoped `allow_overlap` 守 captured overlap（照搬各样本 run_tests 的 allow_overlap 段：parent A L383-403、parent B L636-656、monkeyhead L391-425（含 `allow_isolated_part` worm L418-425）、thumbslide L405-443（含 `allow_coplanar_surfaces` L436-443）、tubularshank L673-693；cross-spine 样本：crescent_wood L477-497、crescent_tubular L388-408、pipe_flatsteel L618-638）。
- **rest pose**：所有活动颚 q=0（颚口在标称小开度，`JAW_NOMINAL_GAP` / 标称 seat）；worm / nut q=0；lever q=0 收拢。**绝不**把 rest pose 设成全开（违反闭合姿态目检与样本 lower=0）。
- **互斥 / 可选 / 派生**：head_mechanism 四候选互斥（一次只一种头机构 + 一种 spine，spine 由 head 派生）；handle 三候选互斥，**与 head_mechanism 正交**（任一 handle 可配任一 head），但模板侧须按所选 head 的 spine **rebase** handle 锚定（crescent 就地 vs pipe `_lay()` 放倒）——这是实现细节，不限制采样合法性。

## 每槽位 Module Emits / Interfaces

### Slot A / head_mechanism — worm_rack_crescent（crescent spine）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wrench_body`（root，visual `body_shell`：ring + 扁钢把手 + 斜置 lens 头板 + 固定颚 + 蜗杆 pocket，由 `_build_body` union）；`movable_jaw`（visual `jaw_shell`：颚块 + 内嵌 rack shank + rack 齿）；`worm_screw`（visual `worm_wheel`：滚花蜗杆）| S1 / `_build_body` L175-214 / `_build_movable_jaw` L217-267 / `_build_worm` L270-292 |
| internal joints | `jaw_slide` PRISMATIC axis=(-1,0,0) origin=斜滑轴铰点 rpy yaw=tilt lower=0/upper=0.018；`worm_turn` CONTINUOUS axis=(1,0,0) origin=蜗杆中心 rpy yaw=tilt | S1 / L335-364 |
| upstream interface | root（坐地，无父）| — |
| downstream interface | rack shank captured 进头板 slide slot；worm captured 进蜗杆 pocket（rim 透两面 windows 啮合 rack）| S1 / `_build_head_local` slot L148-158 / pocket L164-171 |

### Slot A / head_mechanism — screw_nut_pipe（pipe spine）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `head_frame`（root，visual `frame_steel`：钩固定颚 + 下排锯齿 + housing + nut window + jaw channel + shank，经 `_lay()` 放倒）；`movable_jaw`（visual `jaw_steel`：screw bar + 上排锯齿头）；`adjust_nut`（visual `nut_knurled`：`KnobGeometry` 滚花螺母）| S2 / `build_head_frame_geometry` L168-247 / `build_movable_jaw_geometry` L250-285 / nut L358-373 |
| internal joints | `frame_to_jaw` PRISMATIC axis=(0,0,1)(tool)=世界+X origin=`_lay(0,0,WINDOW_Z)` rpy=`LAY_RPY` lower=0/upper=0.024；`frame_to_nut` CONTINUOUS axis=(0,0,1) origin=`_lay(0.004,0,WINDOW_Z)` 与滑轴共线 | S2 / L379-399 |
| upstream interface | root（`_lay()` 放倒坐地，无父）| — |
| downstream interface | screw bar 滑进 housing channel + nut window；nut 坐 window 包覆 bar（双排锯齿啮合工件，非自身齿）| S2 / window L204-209 / channel L211-217 |

### Slot A / head_mechanism — monkey_head（crescent spine）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wrench_body`（root，visual `body_shell`：ring + 扁钢把手 + 矩形头框 + 固定上颚 + 蜗杆 pocket）；`movable_jaw`（visual `jaw_shell`：shoe + shank + rack 齿，平行平颚）；`worm_screw`（visual `worm_wheel`）| S3 / `_build_body` L161-198 / `_build_head_frame` L121-158 / `_build_movable_jaw` L211-250 / `_build_worm` L253-275 |
| internal joints | `jaw_slide` PRISMATIC axis=(0,-1,0) origin=`(cut_x_mid, JAW_FACE_Y_REST, Z_LIFT)` lower=0/upper=0.016；`worm_turn` CONTINUOUS axis=(1,0,0) origin=back wall pocket | S3 / L343-368 |
| upstream interface | root（坐地，无父）| — |
| downstream interface | jaw shank captured 进矩形头框 cutout channel；worm captured 进 back wall pocket（`allow_isolated_part` 守 pocket 全包覆）| S3 / cutout L135-142 / pocket L148-157 |

### Slot A / head_mechanism — thumb_slide（crescent spine，REVOLUTE 驱动）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `wrench_body`（root，visual `body_shell`：ring + 扁钢把手 + 斜置 lens 头板 + 固定颚 + **头面 boss 销**，无蜗杆 pocket）；`movable_jaw`（visual `jaw_shell`：颚块 + 滑 shank，**无 rack 齿**）；`thumb_lever`（visual `lever_shell`：engagement tab + arm + thumb pad + grip ridges）| S4 / `_build_body` L178-214 / boss L166-174 / `_build_movable_jaw` L217-242 / `_build_thumb_lever` L245-294 |
| internal joints | `jaw_slide` PRISMATIC axis=(-1,0,0) origin=斜滑轴铰点 rpy yaw=tilt lower=0/upper=0.018；`lever_pivot` **REVOLUTE** axis=(0,0,1) origin=`(boss_x, boss_y, Z_LIFT+HEAD_T/2)` rpy yaw=tilt lower=0/upper=0.50 | S4 / L351-384 |
| upstream interface | root（坐地，无父）| — |
| downstream interface | jaw shank captured 进头板 slide slot；lever bore 套头面 boss 销（pin-in-bore，`allow_coplanar_surfaces` 守 lever 贴头面）；lever tab 扫入滑槽推 jaw shank（colliding tab/shank） | S4 / boss L166-174 / lever bore L287-293 |

### Slot B / handle — flat_steel（与 head 正交，按 spine rebase 锚定）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：扁钢条 + hex 通孔 ring 蝶端。crescent 锚：内联进 `wrench_body` 的 `body_shell`。pipe 锚：锥形 bar + hex ring 作 `head_frame` root visual（`flat_handle`）| crescent: S1 `_build_body` ring L177-191 + handle L194-204 / `_hex_profile` L115-122。pipe: S6 `build_flat_handle_geometry` L293-353 / hex L329-335 |
| internal joints | 无（把手不动）| — |
| upstream interface | crescent: 与头板共体 union（无接口面），整体坐地 `Z_LIFT`（S1 L213-214）。pipe: 经 `Origin(xyz=_lay(0,0,0), rpy=LAY_RPY)` 挂 `head_frame`（S6 L380-385）| S1 / S6 |

### Slot B / handle — tapered_wood（与 head 正交，按 spine rebase 锚定）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：锥木 grip + ferrule 颈圈 + (worn band) + 钢 butt cap。crescent 锚：`wood_grip`+`ferrule_collar`+`butt_cap` 作 `wrench_body` visual（+ 隐藏钢 tang 在 `body_core`）。pipe 锚：`ferrule`+`handle_body`+`handle_worn`+`butt_cap` 作 `head_frame` visual | crescent: S7 `_build_wood_grip` L233-267 / `_build_ferrule` L270-283 / `_build_butt_cap` L286-298 / tang in `_build_body_core` L214-220 / 装配 L386-407。pipe: S2 ferrule L313-320 / handle L322-329 / worn L331-338 / butt L340-347 / `build_handle_geometry` L419-439 |
| internal joints | 无（把手不动）| — |
| upstream interface | crescent: grip 沿世界 +X revolve，钢 tang（`TANG_R=0.003`）贯穿 grip 把 ring/头串成核心，整体坐地 `Z_LIFT`（S7 L214-230）。pipe: lathe visual 经 `Origin(xyz=_lay(-0.004,0,...), rpy=LAY_RPY)` 挂 root，shank 下端插木 ferrule（径向连接）（S2 L313-347）| S7 / S2 |

### Slot B / handle — tubular（与 head 正交，按 spine rebase 锚定）
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无独立 part：中空圆管 + 端 ferrule / grip 环肋 + 圆盘 cap。crescent 锚：annular tube + butt ferrule 环 inline 进 `body_shell`。pipe 锚：`handle_tube`+`grip_rib_{i}`+`butt_cap` 作 `head_frame` visual | crescent: S8 `_build_tubular_shank`（annular revolve + ferrule）L165-204 / `_build_body` L207-219 / 装配 L311-316。pipe: S5 `build_tube_handle_geometry` L307-330 / butt L333-342 / `build_grip_rib_geometry` L345-361 / ribs L407-414 |
| internal joints | 无（把手 / 肋不动）| — |
| upstream interface | crescent: `SHANK_R=0.013`/`SHANK_WALL=0.002` annular tube 沿世界 +X revolve，与斜置 crescent 头 union 进 `wrench_body`，整体坐地 `Z_LIFT`（S8 L207-219）。pipe: 管 visual 经 `_lay()` 挂 root，shank 下端 `SHANK_INSERTION=0.005` 插管壁；grip 肋 `for i in range(GRIP_RIB_COUNT)` 沿管等距（S5 ribs L407-414）| S8 / S5 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| head_mechanism | enum | worm_rack_crescent / screw_nut_pipe / monkey_head / thumb_slide | worm_rack_crescent | choice | deterministic procedural sampler 选；**决定 spine + root 类型**（互斥）| Slot A 表 |
| handle | enum | flat_steel / tapered_wood / tubular | flat_steel | choice | sampler **独立**选（**与 head_mechanism 正交**，任一 handle 配任一 head）；模板侧按所选 head 的 spine rebase 锚定，不限制采样合法性，见 §9 | Slot B 表 |
| spine（derived） | enum | crescent / pipe | crescent | equation | `= "crescent" if head_mechanism∈{worm_rack_crescent,monkey_head,thumb_slide} else "pipe"`；不独立采样；**仅用于选 handle 锚定 builder（rebase），不 gate handle 选择** | §5 spine 分析 |
| palette_style | enum | bright_chrome_steel / black_oxide_steel / blue_japanned_steel / red_wood_handle / galvanized_tube / dark_machined_steel | bright_chrome_steel | palette | palette only，**不计入 slot_choice**；按 spine/handle gating（红木把仅 tapered_wood）| 各样本材质（见下）|
| handle_len_scale | float | [0.88, 1.12] | 1.0 | independent | 缩放 `HANDLE_LEN`/`HANDLE_TOP-HANDLE_BOTTOM`（把手长），clamp 保平铺长 > 0.30 m | S1 L51 / S2 L103-104 |
| handle_girth_scale | float | [0.90, 1.10] | 1.0 | independent | 缩放把手宽 / 半径（`HANDLE_W`/`HANDLE_T` 或 `TUBE_OR`/`HANDLE_MAX_R`），clamp 保 shank 插接仍连通 | S1 L52-53 / S5 L111 |
| head_scale | float | [0.92, 1.10] | 1.0 | independent | 缩放头部主尺寸（`HEAD_LEN`/`FRAME_BODY_*`），clamp 保颚口与齿/slot 比例不破 | S1/S3 头廓 / S2 L74-79 |
| jaw_travel_scale | float | [0.85, 1.10] | 1.0 | independent | 缩放 `JAW_TRAVEL`（PRISMATIC upper），clamp 使全行程内 shank 仍 captured 在 slot/channel 内（见各样本 expect_within/overlap 全行程检查）| S1 L72 / S2 L101 / S3 L71 |
| driver_open_scale | float | [0.85, 1.10] | 1.0 | conditional | 仅 thumb_slide 有效；缩放 `lever_pivot` upper（`LEVER_TRAVEL`，REVOLUTE）；worm/nut CONTINUOUS 无 upper 不缩 | S4 L87 |
| grip_count（module-local，非 slot 轴） | int | [4, 8] | 6 | independent（module-local）| tubular 把手肋数 / monkey·thumb grip 脊数；**module 内固定参数，不进 slot_choice**（见 §8）| S5 L115 / S3 L312 / S4 L88 |
| (—) | constraint | — | — | inequality | 全行程 captured：`jaw_travel_scale·JAW_TRAVEL ≤ slot/channel 可用行程 − margin`；违反则回缩 travel（守"shank 全程不脱 slot"，见各样本 open-pose expect_within）| 接口 / clearance |
| (—) | constraint | — | — | inequality | 平铺细长：缩放后 `x_extent > 0.30`（crescent）/ `> 0.35` 且 `x_extent > 3·z_extent`（pipe）；违反回缩 handle_len_scale | S1 L431 / S2 L537 |
| (—) | constraint | — | — | conditional | handle 锚定 builder 随 head_mechanism spine 解析（crescent 就地 revolve/extrude；pipe `_lay()` 放倒）——**仅选锚定，不 gate handle 合法性**（handle 与 head 正交）；palette 红木把仅 tapered_wood | §9 |

所有连续 scale 在 `resolve_config` 中 clamp / 派生；每个 build 解析一次。scale 只动安全比例 / 行程，**绝不改变 head_mechanism / handle / spine 的拓扑**。**handle 独立于 head_mechanism 采样（正交）**；spine 仅派生用于选 handle 锚定 builder（rebase），不缩窄 handle 合法集。

**palette_style 来源（6 真实 colorway，全部取自 5★ 样本材质）**：
- `bright_chrome_steel`：亮镀铬合金钢（parent A `STEEL=(0.74,0.75,0.77)` + `STEEL_DARK` + `KNURL`）——crescent 默认。
- `black_oxide_steel`：黑发蓝 / 氧化深钢（thumbslide `LEVER_OXIDE=(0.38,0.40,0.42)` + `STEEL_DARK`）——发黑表面。
- `blue_japanned_steel`：蓝烤漆钢颚（monkeyhead `STEEL_BLUE=(0.42,0.47,0.58)` 活动颚 + 钢身）——蓝颚 monkey 风。
- `red_wood_handle`：红漆木把 + 裸木磨损 + 钢头（parent B `RED_PAINT=(0.74,0.13,0.11)` + `BARE_WOOD=(0.62,0.49,0.31)` + `STEEL`/`DARK_STEEL`/`BUTT_STEEL`；crescent_wood 用 `WOOD=(0.52,0.32,0.15)`+`BRASS` ferrule）——**仅 tapered_wood 把手**（任一 spine）。
- `galvanized_tube`：镀锌 / 红漆钢管把 + 滚花螺母（tubularshank `RED_PAINT` 管 + `KNURL_STEEL` + `GRIP_RUBBER`+`BUTT_STEEL`）——**仅 tubular 把手**（任一 spine）。
- `dark_machined_steel`：暗机加工面（`STEEL_DARK`/`DARK_STEEL` 主导，knurl 件深色），通用。

## Multiplicity / Copy Logic

- **无模板级复制数量逻辑（无独立 multiplicity 轴）**：核心结构由固定 named slots（head_mechanism + handle）表达，不暴露 `*_count` 作为 slot 轴，也不通过循环复制模板级 visual/part/joint 来撑拓扑多样性。
- **module 内部复制（非轴，不进 slot_choice）**：
  - **jaw 齿**：crescent rack 齿 `for i in range(5)`（parent A L251-259 / monkeyhead `_rack_tooth` helper L201-208 + 循环 L242-248）；pipe 钩颚 + 活动颚锯齿 `_add_teeth_x(n_teeth=6)` 共享 helper（parent B L236-245+L275-284 / tubularshank L255-264+L294-303）。齿等距沿滑动 / 颚面发射，共享三角齿 helper，全部 union 进各自 jaw/frame visual（**FIXED 内联，非独立 part / joint**）。
  - **grip 脊 / 肋**：monkeyhead 把手 grip ridges `for i in range(7)` L312-321；thumbslide thumb pad grip ridges `for i in range(N_GRIP_RIDGES=4)` L337-346；tubularshank 管 grip ribs `for i in range(GRIP_RIB_COUNT=6)` L407-414。等距发射相同 rib visual，**inline 进 root/lever visual，无独立 joint**。
  - 这些循环计数（齿数 / 肋数）是各 module 内固定参数，可作受控 `grip_count`∈[4,8] 局部连续参数（§7），但**不暴露为 slot multiplicity 轴**——wrench 不存在"任意 N 个头 / 颚 / 把手"的产品域，多样性全部来自 head_mechanism × handle 的离散槽。

## 拓扑多样性审计

总组合数（**handle 与 head_mechanism 正交**，cross-spine 补造后无 spine gating）：
- crescent spine head_mechanism = {worm_rack_crescent, monkey_head, thumb_slide}(3) × handle{flat_steel, tapered_wood, tubular}(3) = **9**
- pipe spine head_mechanism = {screw_nut_pipe}(1) × handle{flat_steel, tapered_wood, tubular}(3) = **3**
- **合法离散组合数 = 9 + 3 = 12**


理由与说明：原 spec 把 handle 绑死在各自 head-spine（crescent 只 flat_steel、pipe 只 wood/tubular），合法组合仅 5 < 10。已**回 fork 池补造 3 个 cross-spine 把手变体**——`rec_wrench_var_crescent_wood`（crescent 头 + 锥木把：木 grip 沿世界 +X revolve + 黄铜 ferrule + 钢 butt + 隐藏钢 tang）证 crescent-spine 接受 wood；`rec_wrench_var_crescent_tubular`（crescent 头 + 圆管把：annular tube 沿世界 +X revolve + 端 ferrule）证 crescent-spine 接受 tubular；`rec_wrench_var_pipe_flatsteel`（pipe 头 + 扁钢把：tool-frame 锥形 bar + hex ring 经 `_lay()` 挂 `head_frame`）证 pipe-spine 接受 flat steel。**3 种把手现各有 crescent + pipe 两条 spine 的 5★ 源支持**，handle 与 head_mechanism 正交，合法组合提至 12。

**spine-rebase 注记（模板实现要点）**：handle 不再被 head 的 spine 排他，但**模板必须把 handle module 的锚定坐标系 rebase 到所选 head 的 spine 上**——crescent spine（in-place `wrench_body`）下把手沿世界 +X 就地 revolve/extrude 并 union/挂进 `wrench_body`；pipe spine 下把手在 tool frame 沿 local −Z 创建后经 `_lay()`/`LAY_RPY` 挂 `head_frame`。这是实现层的 rebase（选锚定 builder），**不是采样层的 gating**（采样上 handle 自由独立）。每个 handle module 因此需带两套锚定路径（cross-spine 样本已逐一证可移植）。

> **GATE P3 注记（PASS）**：head_mechanism slot 4 candidate（≥3 ✓），handle slot 3 candidate（≥3 ✓），**每候选（含 3 个新 cross-spine 源）有真实 `model.py:Lx-Ly`**，无单候选 slot，齿/肋 multiplicity 已声明为 module-local 非轴。**离散拓扑组合数 12 ≥ 10 拓扑门控（PASS）**。BLOCKER 已解除：handle 经 cross-spine 补造与 head_mechanism 正交，模板侧仅需 spine-rebase handle 锚定。

seed_domain_policy：procedural_first（`config_from_seed(seed)` 对所有 seed 用 `random.Random(seed)` 采样；seed=0 不特殊）。

Procedural Sampling / Sweep Plan：sampler 先 `rng.choice` head_mechanism（4 选 1），派生 spine，再 **`rng.choice` handle（3 选 1，独立 / 与 head 正交，不受 spine gate）**，按派生 spine 选 handle 的锚定 builder（crescent 就地 vs pipe `_lay()`），再 `rng.choice` palette（按 handle gating，红木把仅 tapered_wood、galvanized_tube 仅 tubular），再 uniform 各连续 scale（handle_len/girth、head_scale、jaw_travel；driver_open 仅 thumb_slide），经两条 captured/细长 inequality 投影回缩。无 regression overrides（首版纯 procedural）。random sweep seeds 0-49 初轮 + 0-999 成熟审计；viewer 目检 seeds 0-9（每 head_mechanism 至少看 1 个，并覆盖 cross-spine 组合如 crescent+wood / crescent+tubular / pipe+flat）。


Controlled local parameterization：见 §参数表的 handle_len_scale / handle_girth_scale / head_scale / jaw_travel_scale / driver_open_scale（conditional@thumb_slide）/ grip_count（module-local @pipe·tubular/monkey/thumb）。全部 `resolve_config` clamp + 每 build 统一应用。采样契约：先采 head_mechanism → 派生 spine → **独立采 handle（与 head 正交，不 gate）** → 按 spine 选 handle 锚定 builder（rebase）+ palette gating → 采 independent handle/head/jaw_travel scale → 解析 driver_open（仅 thumb_slide）→ 用两条 inequality（全行程 captured、平铺细长）投影 / 回缩。跨部件依赖（jaw_travel vs slot 可用行程、handle_len vs 平铺长）显式落在 §7 inequality，在 `resolve_config` 内求解。这些 scale 不破坏 jaw_slide/worm/nut/lever origin、captured 接口、齿/肋复制逻辑或类别身份。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 先 `rng.choice` head_mechanism(4)，派生 spine，再 **`rng.choice` handle(3，独立 / 正交)**，按 spine 选 handle 锚定 builder，再 palette(按 gating)，再 uniform scale | slot_choices_for_seed 含 `("head_mechanism", ...)` + `("handle", ...)` 且与 build 一致；12 distinct 组合可达 |
| compatibility matrix | (1) **handle 与 head_mechanism 正交（无 spine gating）**：任一 handle ∈ {flat_steel, tapered_wood, tubular} 可配任一 head ∈ {worm_rack_crescent, monkey_head, thumb_slide, screw_nut_pipe}；3 cross-spine 样本已证 3 把手挂两条 spine 均可。模板侧约束改为 **spine-rebase**：按派生 spine 选 handle 锚定 builder（crescent 就地 revolve/extrude 进/挂 `wrench_body`；pipe tool-frame `_lay()` 挂 `head_frame`）——选锚定，不 gate 合法性。 (2) **palette gating**：`red_wood_handle` 仅 tapered_wood；`galvanized_tube` 仅 tubular；钢系 palette 通用。 (3) **driver_open_scale** 仅 thumb_slide（REVOLUTE）；worm/nut CONTINUOUS 无 upper。 (4) jaw_travel clamp 守全行程 captured。 | 无 floating / handle 锚定 rebase 错（crescent 没就地 / pipe 没 `_lay()`）/ shank 脱 slot / 颚口反向（rest 应小开非全开）/ 刚性无关节 |
| controlled local variation | 5 clamped scale（handle_len/girth、head_scale、jaw_travel、driver_open@thumb）+ module-local grip_count[4,8]，每 build 统一 | 比例变化不破坏 jaw/worm/nut/lever origin、captured 接口、平铺细长、闭合姿态、类别身份 |
| regression overrides | none（首版纯 procedural）| — |
| random sweep | seeds 0-49 初轮；0-999 成熟审计 | （12，PASS）+ 逐机构 QC + cross-spine 组合 QC |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A head_mechanism | 4 | yes | yes | worm 斜颚 / nut 钩颚 / worm 方颚 / lever 斜颚；含 CONTINUOUS×3 + REVOLUTE×1 驱动 |
| B handle | 3 | yes | yes | flat_steel / tapered_wood / tubular；**与 head 正交**（各有 crescent+pipe 两条 spine 源），4×3=12 全笛卡尔积 |

## Validator

- `slot_choices_for_seed` 返回已实现的 module 名，含 `("head_mechanism", <name>)` + `("handle", <name>)`
- `config_from_seed` 对所有 seed 用 deterministic procedural sampling（seed=0 不特殊）
- `resolve_config` 派生 spine（按 head_mechanism，仅用于选 handle 锚定 builder）、**handle 独立采样（与 head 正交，不 gate）**、按 spine rebase handle 锚定、palette gating（红木把仅 tapered_wood、galvanized_tube 仅 tubular）；各 scale clamp 到声明范围；driver_open 仅 thumb_slide；两条 inequality（全行程 captured、平铺细长）在 resolve 内投影 / 回缩
- compatibility matrix：handle 与 head_mechanism 正交（任一 handle 配任一 head）；唯一约束是按 spine **rebase** handle 锚定（crescent 就地 vs pipe `_lay()`），错锚（crescent 没就地 / pipe 没 `_lay()`）→ floating / 穿模 FAIL
- 连续 scale clamp 后不破坏 jaw/worm/nut/lever origin / captured 接口 / 平铺细长 / 闭合姿态 / 齿·肋复制
- 关键 joint：worm_rack_crescent `jaw_slide` PRISMATIC axis≈(-1,0,0) + `worm_turn` CONTINUOUS axis≈(1,0,0)；screw_nut_pipe `frame_to_jaw` PRISMATIC axis≈(0,0,1)(tool=世界+X) + `frame_to_nut` CONTINUOUS 与滑轴共线；monkey_head `jaw_slide` PRISMATIC axis≈(0,-1,0) + `worm_turn` CONTINUOUS axis≈(1,0,0)；thumb_slide `jaw_slide` PRISMATIC axis≈(-1,0,0) + `lever_pivot` REVOLUTE axis≈(0,0,1)
- **身份硬约束**：每个候选必含活动颚 PRISMATIC（≥1 非 fixed joint）；rigid open-end/box-end 永不进 seed domain
- captured 接口：element-scoped `allow_overlap`（jaw shank↔slot/channel；worm↔pocket（含 monkey `allow_isolated_part`）；nut↔window+bar；lever↔boss（含 `allow_coplanar_surfaces`）+ tab↔shank），照搬各样本 run_tests 段
- copied object（齿 / 肋）遵循循环命名 + 等距 placement + FIXED 内联（无独立 joint）
- grandfather：所有 captured 接口省略 MatingContract，由 origin 检查 + allow_overlap 守
- rest pose：所有活动颚 / 驱动件 q=0（颚口小开 / lever 收拢），非全开

## Reject cases

- **刚性 open-end / box-end / combination 扳手**（0 活动关节）进 seed domain → 违反 ≥1 非 fixed joint 身份硬约束；本类只收可调 / 活动扳手。
- 把活动颚做成 FIXED 或省掉 `movable_jaw` PRISMATIC → 不再是可调扳手（出类）。
- **handle 锚定未按 spine rebase**：crescent head 下用了 pipe 的 `_lay()` 锚定（或反之），导致把手漂浮 / 错位 / 与头脱节 → floating / 穿模 FAIL。cross-spine 组合本身合法（已有源），但模板必须按所选 head 的 spine 选对应锚定 builder（crescent 沿世界 +X 就地 revolve/extrude；pipe tool-frame `_lay()` 挂）。**注意：这是要求 rebase，不是禁止跨 spine 组合**——把 handle 重新 spine-gate（如"crescent 头不许配木把"）是过时的旧约束，不再适用。
- 把 jaw_travel 放大到 shank 脱出 slot/channel → 违反 §7 全行程 captured inequality（各样本 open-pose expect_within FAIL）；须回缩 travel。
- 活动颚 rest pose 设成全开而非 q=0 小开 → current-pose 与 viewer 目检不符（所有样本 lower=0 闭合）。
- jaw_slide/worm/nut/lever origin 放在头中心或任意点而非真实滑轴铰点 / pocket / window / boss 销 → `fail_if_articulation_origin_far_from_geometry` FAIL。
- 给 captured-shank/worm-pocket/nut-window/lever-boss 补 MatingContract 硬对接 → 几何对不上，mating-gap FAIL；应 grandfather + allow_overlap。
- 把齿数 / grip 肋数当独立 slot multiplicity 轴 → wrench 无"任意 N 个"产品域；齿 / 肋是 module 内固定循环（§8），多样性来自离散头 / 把槽。
- 把连续尺寸 / 颜色 / 材质（palette_style / handle scale）当新 candidate 塞进 slot → 不是结构差异。
- 把"套筒 / 棘轮扳手"或"钳子"语义混入（棘轮方榫 / 剪式双臂）→ 出类，本类是滑动颚 + 旋调驱动的活动扳手。

## 与相邻类别的边界

- 不该混入：**刚性 open-end / box-end / combination 扳手**（呆扳手 / 梅花 / 两用）——0 活动关节、纯实心铸件；与本类（≥1 活动颚 PRISMATIC + 旋调驱动）是不同结构家族，且违反身份硬约束（documented reject case）。
- 不该混入：**套筒扳手 / 棘轮扳手（socket / ratchet wrench）**——主机构是棘轮方榫 / 套筒插换，运动 spine 不同。
- 不该混入：**钳子 / 老虎钳（pliers）**——双臂绕单销 REVOLUTE 剪式，无滑动颚 + 旋调驱动；如需可作单独 slug。
- 不该混入：**螺丝刀 / 改锥**——旋拧单轴、无颚口。
- Handtools 大类内：区别于 Hammer / Screwdriver / Pliers / Saw 等无"滑动颚 + 旋调驱动"身份的手工具。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | **2026-06 更新：原 BLOCKER（拓扑门控 5<10）已解除**——上游已补造 3 个 cross-spine 把手变体（crescent_wood / crescent_tubular / pipe_flatsteel，均 rating=5、已同步入本仓库），handle 现与 head_mechanism 正交，合法组合提至 **12 ≥ 10（PASS）**。剩余待人工审核项：(1) handle 与 head_mechanism 正交后，模板侧 **spine-rebase**（每个 handle 带两套锚定 builder：crescent 就地 vs pipe `_lay()`）是否接受为实现方案，而非采样层 gating。(2) palette 6 档（红木把仅 tapered_wood、galvanized_tube 仅 tubular gating）是否符合预期。(3) 齿 / grip 肋按 module-local 循环（非 slot multiplicity 轴）+ `grip_count`∈[4,8] 受控连续参数是否符合 multiplicity 审计期望。(4) screw_nut_pipe 的 `KnobGeometry` 螺母（KnobGrip knurled）实现注意点（见 MEMORY KnobGeometry API gotchas）。|

## 模板实现备注（可选）
- 两条运动 spine 需各自 root builder：crescent spine = `_build_body`（ring/grip/tube + 头板就地 XY union，`Z_LIFT` 坐地）；pipe spine = `build_head_frame_geometry` + `_lay()`/`LAY_RPY` 放倒。head_mechanism 决定走哪条。
- **handle spine-rebase（核心，BLOCKER 修复要点）**：handle 与 head 正交，每个 handle module 须带**两套锚定 builder**，按所选 head 的 spine 选用：
  - **crescent 锚（沿世界 +X 就地）**：flat_steel = parent A `_build_body` 内联扁条+ring；tapered_wood = `_build_wood_grip`（spline 半廓沿世界 +X revolve）+`_build_ferrule`+`_build_butt_cap` + 隐藏钢 tang（`_build_body_core` L214-220 把 ring/头串起）；tubular = `_build_tubular_shank`（annular 廓沿世界 +X revolve + 端 ferrule）inline 进 `body_shell`。
  - **pipe 锚（tool frame 沿 −Z 创建后 `_lay()` 挂）**：tapered_wood = parent B `build_handle_geometry`+ferrule+worn+butt；tubular = `build_tube_handle_geometry`+`build_grip_rib_geometry`；flat_steel = `build_flat_handle_geometry`（锥形 bar + hex `polygon(6,d)` ring）经 `Origin(xyz=_lay(...), rpy=LAY_RPY)` 挂 `head_frame`。
- 共享 helper：crescent 头廓 `_build_head_local`（worm/thumb/crescent_wood/crescent_tubular 共用，monkey 用 `_build_head_frame` 矩形）；齿 helper（crescent rack `for i in range(5)` / pipe `_add_teeth_x`，跨样本同名可统一）；grip 肋 helper（`build_grip_rib_geometry` / `_grip_ridge`）；hex helper（crescent `_hex_profile` / pipe `polygon(6, RING_AF/cos30)`）。
- captured 接口 allow_overlap：`run_wrench_tests` 里逐机构补 element-scoped `allow_overlap`，照搬各样本 run_tests 段（parent A L383-403、parent B L636-656、monkeyhead L391-425 含 `allow_isolated_part`、thumbslide L405-443 含 `allow_coplanar_surfaces`、tubularshank L673-693；cross-spine：crescent_wood L477-497、crescent_tubular L388-408、pipe_flatsteel L618-638）。
- `KnobGeometry` 螺母（screw_nut_pipe）：`diameter=0.024, height=WINDOW_W-0.001, body_style="cylindrical", grip=KnobGrip(style="knurled", count=30, depth=0.0008, helix_angle_deg=18.0)`，沿 local +Z 居中即螺旋轴（lay-down 后世界 +X）；注意 MEMORY 记录的 KnobGeometry API gotchas（轴对称件 AABB spin 检查、BoltPattern 等），nut 用 `mesh_from_geometry`。
- 解析顺序：先采 head_mechanism → 派生 spine → **独立采 handle（与 head 正交，不 gate）** → 按 spine 选 handle 锚定 builder（rebase）+ palette gating + driver_open(仅 thumb) → 采 independent handle/head/jaw_travel scale → 投影两条 inequality（全行程 captured、平铺细长）。
- 参考模板：`agent/templates/Stationary_Pen.py`（同 parallel/serial children + 互斥主机构槽 + captured 接口 allow_overlap + module-local 循环 visual，运动拓扑相近，可同构改编）；spine 双 root + handle 双锚定模式（每 handle 两套坐标约定）需谨慎选 root builder + 锚定 builder。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A / B（crescent 基线）| worm_rack_crescent + flat_steel(crescent 锚) | rec_..._6f106d91（parent A）| `_build_body` L175-214 / `_build_head_local` L125-172 / `_build_movable_jaw`(rack `for i in range(5)`) L217-267 / `_build_worm` L270-292 / `jaw_slide` PRISMATIC L335-346 / `worm_turn` CONTINUOUS L349-364 / allow_overlap L383-403 | crescent spine 基线 + 蜗杆-rack 驱动 + 扁钢 ring 把 + captured 范式 |
| S2 | A / B（pipe 基线）| screw_nut_pipe + tapered_wood(pipe 锚) | rec_..._4c74c601（parent B）| `build_head_frame_geometry`(钩颚 + `_add_teeth_x` L236-245) L168-247 / `build_movable_jaw_geometry` L250-285 / `KnobGeometry` nut L358-373 / `build_handle_geometry`(木) L419-439 / ferrule L404-416 / worn L442-458 / butt L461-477 / `frame_to_jaw` PRISMATIC L379-387 / `frame_to_nut` CONTINUOUS L391-399 / allow_overlap L636-656 / `_add_teeth_x` helper L134-165 | pipe spine 基线 + 旋调螺母驱动 + 锥木把 + lay-down 范式 |
| S3 | A | monkey_head | rec_wrench_var_monkeyhead | `_build_head_frame` L121-158 / `_build_movable_jaw`(`_rack_tooth` L201-208, rack 循环 L242-248) L211-250 / `_build_worm` L253-275 / `jaw_slide` PRISMATIC axis −Y L343-355 / `worm_turn` CONTINUOUS L358-368 / allow_overlap+`allow_isolated_part` L391-425 | 方框头 + 平行平颚（crescent spine 变体）|
| S4 | A | thumb_slide | rec_wrench_var_thumbslide | `_build_thumb_lever` L245-294 / `_build_movable_jaw`(无齿) L217-242 / `jaw_slide` PRISMATIC L351-364 / `lever_pivot` REVOLUTE axis Z L367-384 / grip ridges L337-346 / allow_overlap+`allow_coplanar_surfaces` L405-443 | 拇指快调杆（唯一 REVOLUTE 驱动，crescent spine 变体）|
| S5 | B | tubular(pipe 锚) | rec_wrench_var_tubularshank | `build_tube_handle_geometry` L307-330 / `build_grip_rib_geometry` L345-361 / grip ribs `for i in range(GRIP_RIB_COUNT)` L407-414 / `build_butt_cap_geometry`(圆盘) L333-342 / shank insertion L201-209 / allow_overlap L673-693 | 圆钢管把 + 等距 grip 环肋（pipe spine 锚）|
| **S6** | **B** | **flat_steel(pipe 锚，cross-spine)** | **rec_wrench_var_pipe_flatsteel** | `build_flat_handle_geometry`(锥形 bar + hex ring + forged grooves) **L293-353** / hex `polygon(6, RING_AF/cos30)` L329-335 / 装配经 `_lay()`+`LAY_RPY` 挂 `head_frame` visual `flat_handle` **L380-385** / `_lay()` L124-126 / `LAY_RPY` L120 / `frame_to_jaw` PRISMATIC L417-425 / `frame_to_nut` CONTINUOUS L429-437 / allow_overlap L618-638 | **证 pipe-spine 接受 flat steel 把（cross-spine）**：扁锻钢条 + hex ring 挂 pipe `head_frame` |
| **S7** | **B** | **tapered_wood(crescent 锚，cross-spine)** | **rec_wrench_var_crescent_wood** | `_build_wood_grip`(spline 半廓沿世界 +X revolve 360°) **L233-267** / `_build_ferrule`(黄铜颈圈) **L270-283** / `_build_butt_cap`(钢盘) **L286-298** / `_build_body_core`(ring + 钢 tang `TANG_R=0.003` 贯穿 grip + 头) **L192-230** / 装配 visual **L386-407** / `jaw_slide` PRISMATIC L426-437 / `worm_turn` CONTINUOUS L440-455 / allow_overlap L477-497 | **证 crescent-spine 接受锥木把（cross-spine）**：木 grip + 黄铜 ferrule + 钢 butt + 隐藏钢 tang 挂 crescent `wrench_body` |
| **S8** | **B** | **tubular(crescent 锚，cross-spine)** | **rec_wrench_var_crescent_tubular** | `_build_tubular_shank`(annular 廓沿世界 +X revolve 360° + 端 ferrule 环 `FERRULE_R=0.0145`) **L165-204** / `_build_body`(tube ∪ 斜置 crescent 头) **L207-219** / 装配 visual(inline 进 `body_shell`) **L311-316** / `jaw_slide` PRISMATIC L340-351 / `worm_turn` CONTINUOUS L354-369 / allow_overlap L388-408 | **证 crescent-spine 接受圆管把（cross-spine）**：`SHANK_R=0.013` annular tube 沿世界 +X revolve + butt ferrule 环挂 crescent `wrench_body` |
