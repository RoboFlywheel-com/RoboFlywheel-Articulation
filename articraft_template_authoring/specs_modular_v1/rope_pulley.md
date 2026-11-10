# Modular Spec — rope_pulley

## 元信息
| 项 | 值 |
|---|---|
| slug | `rope_pulley` |
| template path | `agent/templates/rope_pulley.py` |
| test path (optional) | `tests/agent/test_rope_pulley_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` (parallel_children hub: body root + sheave/attachment/rope-control children; multiplicity on sheave count) |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 14 |
| read_count | 14 |
| read_scope | all 5-star sources for this 小类 (3 origin anchors o1/o2/o3 + 11 forked/probe variants) |
| source_index_policy | only adopted module sources are indexed below |

Origin anchors (real image-grounded records):
- **S1 = o3** `rec_..._ad2de311f270426e89efa649f8081484` — single sheave, open pear cheek plates, fixed integral top eye, orange-anodized. Helpers `_side_plate_geometry` (L47-74, ExtrudeWithHolesGeometry pear + top-eye slot + axle bore), `_grooved_sheave_geometry` (L77-111, revolved MeshGeometry V-groove), `frame_to_sheave` CONTINUOUS axis (0,1,0) L180-188.
- **S2 = o2** `rec_..._8db7819e58414e1f9df89ef1651224ab` — single sheave, oval stainless cheeks with side window, swivel eye + carabiner clip, "15" load stamp. `_pulley_cheek_mesh` (L38-62, superellipse ExtrudeWithHoles), 3-cylinder flanged sheave L232-258, `upper_swivel` collar+carabiner L181-230, `housing_to_sheave` CONTINUOUS-Y L263-271, `housing_to_upper_swivel` CONTINUOUS axis (0,0,1) L279-287.
- **S3 = o1** `rec_..._3508f00573934a1e82b506b8bf7688c2` — double sheave, 4 stacked cheek plates, top+bottom swivel hooks, coiled rope. `_plate_mesh` (L28-38, ExtrudeGeometry rounded rect), `_sheave_mesh` (L41-56, LatheGeometry concave rim), `_hook_mesh` (L59-82, tube_from_spline_points), two sheaves loop `frame_to_{upper,lower}_sheave` CONTINUOUS-Y L215-238, `frame_to_{top,bottom}_hook` REVOLUTE axis (0,0,1) L248-274.

Forked variants adopted: `var_triple_block` (N=3 sheave loop L245-272), `var_snatch_block` (swing cheek `frame_to_swing_plate` REVOLUTE axis (-1,0,0) L233-240), `var_shell_block` (`_mortise_shell_body` cadquery L94-165), `var_tube_fairlead` (`_tube_shell_mesh` cadquery L25-83), `var_fixed_hook` (top_hook FIXED L246-252), `var_snap_shackle` (bail L209-234 + `upper_swivel_to_gate` REVOLUTE axis (0,-1,0) L326-338), `var_bail_shackle` (`_u_bail_geometry` L110-140, folded `frame.visual`), `var_becket` (`_becket_eye_mesh` TorusGeometry L87-90, folded bottom eye), `var_cam_cleat` (`_cam_jaw_mesh` L65-104, `housing_to_cam` REVOLUTE-Y L387-402), `var_progress_capture` (`_capture_cam_geometry` L128-177, `frame_to_capture_cam` REVOLUTE-Y L292-299), `probe_triple_becket` (triple + becket compat probe).

## 核心身份

一个绳索滑轮/滑车（rope block / pulley）：一个（或多个）带凹槽的 sheave（轮）在轴（axle）上绕 Y 轴**自由连续旋转**，被一对侧颊板 / 外壳 / 管状体（body）夹持捕获；body 顶部（或底部）带一个绳索连接接口（固定眼 / swivel eye / swivel hook / carabiner / snap shackle / U-bail / becket）。核心机构永远是**真实转动的 sheave（CONTINUOUS about Y, axis (0,1,0)）** —— 每个 seed 必须至少有一个。sheave 数量是一根 multiplicity 轴（single→quad block）。

**成熟默认域**：便携五金滑轮 / 攀岩救援滑轮 / 帆船 block / block-and-tackle 滑车。
**不该混入**：无轮的 carabiner / snap-hook / rappel ring（相邻类，无 sheave）；chain hoist / winch / gin wheel / capstan（缠绳绞车，非重定向滑轮）；裸轮无壳；无 sheave 的 cleat。

## 槽位 + 候选模块表

### Slot A：body_form（③ 主体形态家族 / Primary Form Family，ROOT，捕获 sheave 的主体）

| module_name | source_type | source evidence | model.py:Lx-Ly | form_subtype | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| open_plate_block | origin_anchor | S3 (o1), S1 (o3) | S3 L28-38,L157-238 / S1 L47-111 | Planar Boundary Form | eligible | 平面颊板 block：outer(±) + inner(±) 圆角矩形板（ExtrudeGeometry），板间 spacer rail，每个 sheave 一根 Y 向 axle pin；支持 sheave_count 1–4、snatch 铰链、becket、cam。 |
| mortise_shell_block | forked_anchor | var_shell_block | L94-165,L192-250 | Volumetric Envelope Form | eligible | 实心圆角 mortise 壳体（cadquery box + 圆角 + sheave pocket + rope mouth slot + axle bore + eye hole + strop groove），单 sheave 内嵌。 |
| tube_fairlead | forked_anchor | var_tube_fairlead | L25-83,L146-180 | Macro Surface Construction | eligible | 管状 fairlead / rope-glider 壳（cadquery 中空圆柱 + 端 web + 顶 boss + 底 rope-passage slots），单 sheave 内嵌 + 顶 boss 接 swivel。 |

### Slot B：top_attachment（② 关节类型 + ③ 接口形态，body 顶部的绳索连接接口）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| fixed_eye | origin_anchor | S1 top_slot | S1 L67 | eligible | body 顶部整体眼孔/眼环（**折入 body visual，无独立 part**）。静态。 |
| fixed_hook | forked_anchor | var_fixed_hook | L244-252 | eligible | 顶部刚性焊接 hook（**折入 body visual**，非活动，符合 Rule 1）。静态。 |
| u_bail | forked_anchor | var_bail_shackle | L110-140,L196-217 | eligible if open_plate_block | 捕获式 U-bail 跨过颊板顶（腿穿双板，**折入 frame visual**）。静态。仅 plate body。 |
| swivel_eye | origin_anchor | S2 upper_swivel | S2 L181-199,L279-287 | eligible | 独立 part：swivel collar + eye，`body_to_upper_swivel` CONTINUOUS axis (0,0,1)。 |
| swivel_hook | origin_anchor | S3 top_hook | S3 L240-256 | eligible | 独立 part：swivel shank + 弯钩体（tube_from_spline），`body_to_top_hook` REVOLUTE axis (0,0,1)。 |
| snap_shackle | forked_anchor | var_snap_shackle | L185-338 | eligible | 独立 part：swivel bail（CONTINUOUS-Z）+ 弹簧 gate 子 part（`upper_swivel_to_gate` REVOLUTE axis (0,-1,0)）。 |

### Slot C：rope_control（② 关节类型，sheave 之外的绳索控制机构）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| plain | origin_anchor | S1/S2/S3 | — | eligible | 无额外机构，只有自由旋转 sheave。 |
| cam_cleat | forked_anchor | var_cam_cleat | L65-104,L264-278,L387-402 | eligible if open_plate_block | 独立 part：偏心齿 cam_jaw，`body_to_cam` REVOLUTE axis (0,1,0)，行程 [-0.10, 0.90]（自锁 cleat）。 |
| progress_capture | forked_anchor | var_progress_capture | L128-177,L270-299 | eligible if open_plate_block | 独立 part：棘齿 capture_cam，`body_to_capture_cam` REVOLUTE axis (0,1,0)，行程 [-0.1, 0.5]（progress-capture 棘轮）。 |

### 独立轴（非 module slot，见 §8 / §8.5）
- `sheave_count`（①-multiplicity）：1/2/3/4，仅 open_plate_block 可 >1。
- `snatch_hinge`（① skeleton）：bool，open_plate_block & sheave_count==1 时，后颊板变为 REVOLUTE swing_plate（snatch block，源 var_snatch_block）。
- `becket`（③ 底部特征）：bool，open_plate_block 时底部加折入式 becket eye（源 var_becket）。
- `palette_style`（⑥）；连续 scale（⑤）。

硬约束满足：body_form 3 candidate、top_attachment 6 candidate、rope_control 3 candidate（cam/progress 仅 plate；plate 上 3 全可，故 rope_control 满足 ≥2；非-plate body 下 rope_control 固定 plain，属 conditional gating 不算 candidate 缺失）。

## 槽位图（slot graph）

pattern: mixed（hub 型 parallel_children + sheave multiplicity）

```
body_form (ROOT part "frame"/housing, grounded)
  ├─[frame_to_sheave_i  CONTINUOUS axis(0,1,0) @ (0,0,z_i); captured-pin, allow_overlap axle∩bore]──> sheave_i   (× sheave_count)
  ├─[body_to_swing_plate REVOLUTE axis(-1,0,0) @ top hinge; snatch_hinge only]──> swing_plate  (rear cheek)
  ├─[body_to_upper_swivel CONTINUOUS axis(0,0,1) @ (0,0,top_z); captured shank-in-collar]──> upper_swivel / top_hook   (top_attachment moving)
  │       └─[upper_swivel_to_gate REVOLUTE axis(0,-1,0) @ hinge]──> shackle_gate  (snap_shackle only)
  └─[body_to_cam REVOLUTE axis(0,1,0) @ (0,0,cam_z); captured-pin, allow_overlap]──> cam_jaw / capture_cam  (rope_control != plain)
```

- 所有子件都直接以 body（root part）为 parent（hub 型 parallel children），不串链。
- 接口点位：sheave 在 axle pin 位置（Z=z_i, 轴向 Y）；swivel/hook 在顶 neck/collar（Z=top_z, 轴向 Z）；gate 在 bail 铰点（轴向 Y）；cam 在其独立 pivot pin（Z=cam_z, 轴向 Y）；swing_plate 在顶 hinge line（轴向 X）。
- 静态接口（fixed_eye / fixed_hook / u_bail / becket）折入 body/frame 的 visual，无 joint。
- joint origin 均落在真实硬件（axle pin / collar / cam pin / hinge boss）上。

## 每槽位 Module Emits / Interfaces

### Slot A / open_plate_block
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`（root）：outer/inner 圆角矩形颊板 ×2/×4、side spacer rail ×2、每 sheave 一根 axle pin、top/bottom rivet、top/bottom neck+collar；折入的 fixed_eye/fixed_hook/u_bail/becket visual | S3 L157-213 / S1 L67 |
| internal joints | 无（sheave/attachment/cam 由各自 slot 挂到 frame） | — |
| downstream interface | frame 顶 collar face @ (0,0,top_z)、底 neck @ (0,0,bot_z)、每 axle @ (0,0,z_i)、cam pin @ (0,0,cam_z) | S3 |

### Slot A / mortise_shell_block
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`（root）：cadquery mortise 壳 shell_body + axle pin + 2 端盖；顶 eye/boss；单 sheave pocket | var_shell_block L192-224 |
| downstream interface | 顶 boss/eye @ (0,0,top_z)、axle @ (0,0,0) | var_shell_block |

### Slot A / tube_fairlead
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`（root）：cadquery tube_shell + axle pin + fastener heads + 顶 swivel_socket boss；单 3-cyl sheave | var_tube_fairlead L146-180 |
| downstream interface | 顶 boss @ (0,0,top_z)、axle @ (0,0,0) | var_tube_fairlead |

### Slot A（所有 body）/ sheave_i（multiplicity）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `sheave_i`：LatheGeometry/revolved 凹槽轮 + 2 hub washer（plate）或 3-cyl 凸缘轮（tube） + rotation_mark 见证条 | S3 L215-229 / S1 L77-111 / S2 L232-258 |
| internal joints | `frame_to_sheave_i` CONTINUOUS axis(0,1,0) @ (0,0,z_i)，无 mating（captured-pin），allow_overlap(axle_pin_i, bore) | S3 L230-238 |

### Slot B / swivel_eye | swivel_hook | snap_shackle（moving）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `upper_swivel`(collar+eye/carabiner) 或 `top_hook`(shank+hook body)；snap_shackle 另加 `shackle_gate` | S2 L181-230 / S3 L240-247 / var_snap_shackle L244-266 |
| internal joints | `body_to_upper_swivel` CONTINUOUS(0,0,1) 或 `body_to_top_hook` REVOLUTE(0,0,1) [-π,π]；`upper_swivel_to_gate` REVOLUTE(0,-1,0) [0,0.60] | S2 L279-287 / S3 L248-256 / var_snap_shackle L326-338 |
| upstream interface | shank 底面坐 body 顶 collar face @ (0,0,top_z)（captured shank-in-collar，allow_overlap） | S2/S3 |

### Slot C / cam_cleat | progress_capture（moving）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cam_jaw`(cam_body + bushing) 或 `capture_cam`(棘齿 cam_body) | var_cam_cleat L264-278 / var_progress_capture L270-277 |
| internal joints | `body_to_cam` REVOLUTE(0,1,0) [-0.10,0.90] 或 `body_to_capture_cam` REVOLUTE(0,1,0) [-0.1,0.5]，captured-pin allow_overlap(cam_pin, bushing) | var_cam_cleat L387-402 / var_progress_capture L292-299 |
| upstream interface | cam bushing 坐 body cam pin @ (0,0,cam_z) | var_cam_cleat |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| body_form | enum | open_plate_block / mortise_shell_block / tube_fairlead | open_plate_block | choice | 采样器选择 | Slot A |
| top_attachment | enum | fixed_eye / fixed_hook / u_bail / swivel_eye / swivel_hook / snap_shackle | swivel_eye | choice | 采样；u_bail 仅 plate（否则降级 swivel_eye） | Slot B |
| rope_control | enum | plain / cam_cleat / progress_capture | plain | conditional | cam/progress 仅 open_plate_block，否则 plain | Slot C |
| sheave_count | int | 1–4（权重档 0.50/0.30/0.13/0.07） | 1 | conditional | 仅 open_plate_block 可 >1；否则 1 | §8 / S3,triple |
| snatch_hinge | bool | {False,True} | False | conditional | 仅 open_plate_block & sheave_count==1 | var_snatch_block |
| becket | bool | {False,True} | False | conditional | 仅 open_plate_block | var_becket |
| palette_style | enum | anodized_orange / stainless_silver / black_anodized / varnished_wood / anodized_blue | stainless_silver | choice | 采样 | ⑥ §8.5 |
| sheave_radius_scale | float | [0.85, 1.20] | 1.0 | independent | clamp | S1/S3 sheave dia 16–26mm |
| sheave_pitch_scale | float | [0.90, 1.15] | 1.0 | independent | clamp（sheave 间距） | S3/triple |
| block_width_scale | float | [0.88, 1.18] | 1.0 | independent | clamp（颊板/壳宽 X） | S1/S3 |
| attach_scale | float | [0.85, 1.20] | 1.0 | independent | clamp（attachment 尺寸） | S2/S3 |
| (—) | constraint | — | — | inequality | 板半高 plate_half_h ≥ (sheave_count-1)/2·pitch + sheave_r + margin；不满足则增高板 | 接口/clearance |
| (—) | constraint | — | — | inequality | plate_half_y（颊板 Y 间距）≥ sheave_width/2 + gap；sheave 全程不触板 | S1 L216-235 |

约束求解：先采 independent scale → 派生 z_i / plate 尺寸 → inequality 投影（板高/板距回缩到容纳 sheave 栈）→ conditional（body_form 决定 sheave_count / rope_control / snatch / becket 合法域）。全部在 `resolve_config` 完成。

## 7.5 编译预算 / compile budget
自报 **≤18 s/seed**。依据：open_plate_block 全为 revolved MeshGeometry（sheave 72 段）+ ExtrudeGeometry 板 + tube_from_spline hook/bail，典型 5–12 s；mortise_shell_block / tube_fairlead 用 cadquery 布尔（tolerance 4e-4），单壳约 8–15 s。分档 tessellation：sheave/washer/cam ≤72 段，hook/bail spline radial ≤18–20，cadquery angular_tolerance 0.08。N 个 sheave 复用同一个 `mesh_from_geometry` cache key（同尺寸时）。sweep `--compile-timeout 120`（≈3× 预算，watchdog）。

## Multiplicity / Copy Logic

**轴 1：sheave_count（唯一 multiplicity 轴）**
- count_param: `sheave_count` / N_range 产品域 [1,4]（single/double/triple/quad block；block-and-tackle 单 block 罕超 4）。测试偏小（多数 seed N=1或2）。
- sampling domain：权重 (0.50, 0.30, 0.13, 0.07)，小 N 高频、quad 稀有。
- copied object：grooved sheave part（LatheGeometry 凹槽轮 + 2 hub washer + rotation_mark），源 S3 `for z,label in [...]` L215。
- naming：`sheave_0 / sheave_1 / ...`（单 sheave 也用 `sheave_0`）。
- placement：沿 Z 等距共轴堆叠 z_i = (i-(N-1)/2)·pitch，全部坐同一 block（每 sheave 一根 axle pin）。
- joint policy：每 sheave 各自 `frame_to_sheave_i` CONTINUOUS axis(0,1,0)，无 mating（captured-pin），element-scoped allow_overlap(axle_pin_i, bore)。颊板 Y 间距与板高随 N 加宽/增高（inequality）。
- gating：仅 open_plate_block 可 N>1；shell/tube 强制 N=1。

其余复制（4 颊板、2 spacer rail、2 hub washer、cam 齿）为**固定结构**（源里定数），非模板级 multiplicity 轴。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | (a) sheave_count 改 sheave part 数（§8 multiplicity，1–4）；(b) snatch_hinge 把后颊板从静态 frame visual 变为独立 REVOLUTE `swing_plate` part（+1 会动 part + 1 边），source-backed var_snatch_block；(c) rope_control 增减 cam part + REVOLUTE 边，source-backed var_cam_cleat/var_progress_capture；(d) top_attachment moving 变体增减 upper_swivel/gate part。全部 forked/origin anchor 支撑。 |
| └ multiplicity | 同构件 ×N | 有 | sheave_count 1–4，权重 (0.50,0.30,0.13,0.07)，见 §8。 |
| ② 关节类型 | 图不变，换 type/轴 | 有 | sheave CONTINUOUS(0,1,0)（全体，必现）；top_attachment：swivel_eye CONTINUOUS(0,0,1) / swivel_hook REVOLUTE(0,0,1) / snap_shackle 再加 gate REVOLUTE(0,-1,0) / fixed_* 无关节（静态）；rope_control cam REVOLUTE(0,1,0)；snatch swing REVOLUTE(-1,0,0)。均 source-backed；每种在 sweep 出现（见 §9 采样）。 |
| ③ 主体形态家族 | 换核心 part 可识别几何原型 | 有 | body_form 3 原型登记进 slot_choices：open_plate_block=Planar Boundary Form（颊板边界，source S1/S3）、mortise_shell_block=Volumetric Envelope Form（实心壳包络，var_shell_block）、tube_fairlead=Macro Surface Construction（管状表面构成，var_tube_fairlead）。另 top_attachment 接口形态族（eye/hook/swivel/bail/shackle）+ becket 底眼为 ③ 接口形态 ride-along。 |
| ④ 表面装饰 | 原型不变叠加表面细节 | 有 | source_type=record_only + world_knowledge_extrapolation：sheave rotation_mark 见证条（S1 L173）、rivet/collar head（S3 L198-204）、"15" 载荷 stamp（S2）、axle cap。装饰几何随宿主 sheave 半径/板面派生（③→⑤→④）：rotation_mark 贴在 sheave 前凸缘半径处、cap 贴 axle 端。非结构、折入宿主 part visual。装饰档：基本(cap+mark) / +rivet head / +load stamp。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | sheave_radius_scale[0.85,1.20]、sheave_pitch_scale[0.90,1.15]、block_width_scale[0.88,1.18]、attach_scale[0.85,1.20]（见 §7）。非-continuous 关节运动包络：swivel_hook REVOLUTE(0,0,1) [-π,π] 绕竖轴自旋；snap gate REVOLUTE(0,-1,0) [0,0.60] 开门向 +X；cam REVOLUTE(0,1,0) [-0.10,0.90] 释放/自锁；capture_cam [-0.1,0.5]；swing_plate REVOLUTE(-1,0,0) [0,π/2] 向 -Y 打开露出 groove。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`（continuous sheave 采 {0,±90°,180°}）；对每个机构一条 targeted `ctx.pose`：sheave 自转轴心不动+mark 绕轴移动、swivel 整体绕 Z 旋转、gate 开启位移、cam 释放位移、swing_plate 向 -Y 露槽。sheave 是 continuous 整圈不穿模。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类 metal(brushed/polished/anodized/painted) + wood；配色 5：anodized_orange(S1)、stainless_silver(S3)、black_anodized(triple/S2 dark)、varnished_wood(shell_block)、anodized_blue(tube_fairlead)。每 palette 给 body/sheave/hardware/accent/rope 分色。材质大类覆盖 ≥ ceil(0.5×5)=3（metal+wood 已 ≥3 色种）。 |

**收尾自检**：0-9 seed 渲染须肉眼可见 3 种 body 形态、单/双/多 sheave、eye/hook/swivel/shackle/bail 接口、cam、5 配色都出现，装饰贴合不悬空，关节全程不穿模。

## 采样与覆盖审计

总组合数（离散骨架）：body_form(3) × top_attachment(6) × rope_control(3) × sheave_count(4) × snatch_hinge(2) × becket(2) = 864，经 compatibility gating（cam/becket/snatch/多sheave 仅 plate；u_bail 仅 plate）后合法组合约 **> 300**（plate 分支 6×3×4×2×2=288 + shell 分支 4×1×1×1×1=4 + tube 分支 4×1×1×1×1=4，另加 palette×scale 连续维度）。

理由：形态主导类，主多样性由 ③ body_form + ①multiplicity + ② attachment/rope_control 离散骨架承载，连续 scale 只做 ride-along。

seed_domain_policy：procedural_first（含 seed 0）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次采 body_form、top_attachment、rope_control、sheave_count（加权）、snatch_hinge、becket、palette_style、连续 scale；`resolve_config` 做 compatibility gating（非法组合按上表降级：非-plate → N=1/plain/无snatch/无becket/u_bail→swivel_eye；多sheave→无snatch）。无 curated/modulo 主表；无 regression override（初版）。
Topology target：1000-seed slot_choice tuple 覆盖用于成熟度观察（report-only）。合法离散空间 >300，满足富类别建议。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | body→attach→rope→N(加权)→snatch→becket→palette→scale，全 deterministic | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | 非-plate body：N=1、rope_control=plain、snatch=False、becket=False、u_bail→swivel_eye；N>1：snatch=False | 无悬空/穿模/轴错/闭合穿模/max-N/bulky/可选活动子件失败 |
| controlled local variation | sheave_radius/pitch、block_width、attach scale，全 clamp + inequality 回缩 | 比例变化不破坏捕获/clearance/joint origin/类别 identity |
| regression overrides | none | — |
| random sweep | 0-15 fast、0-35 final、corner；成熟审计 0-999 | contract failures；axis_realization；viewer focus |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| body_form | 3 | yes | yes | ③ 主体形态族 |
| top_attachment | 6 | yes | yes | |
| rope_control | 3 | yes | yes | cam/progress 仅 plate（conditional） |
| sheave_count(mult) | 4 | yes | yes | 权重档 |

## Validator
- slot_choices_for_seed 返回已实现 module 名（含 body_form/top_attachment/rope_control/sheave_count/snatch/becket）
- config_from_seed 对所有普通 seed（含 0）用 deterministic procedural sampling
- compatibility gating 阻止非法组合（非-plate 多 sheave / cam / snatch / becket / u_bail）
- 无小型 curated/modulo 主 seed 表
- 连续 scale 在 resolve_config clamp/派生/inequality 回缩，不留到 builder 失败
- 每个 sheave 都有 CONTINUOUS axis(0,1,0) joint；捕获-pin overlap 用 element-scoped allow_overlap
- 关键 joint 类型/轴/行程符合上表
- 复制 sheave 遵循 naming/placement/joint policy

## Reject cases
- 某 seed 无任何转动 sheave（核心机构缺失）
- sheave joint 非 CONTINUOUS 或轴非 (0,1,0)
- 非-plate body 出现 N>1 / cam / snatch / becket / u_bail（未 gating）
- sheave 闭合位或旋转全程与颊板/壳穿模（未留 axle 捕获 allow_overlap 或板距过窄）
- swing_plate / gate / cam 中途穿模（行程过大未 clamp）
- attachment 子件悬空（shank 未坐进 collar，无支撑路径）
- becket/u_bail/fixed_hook 做成独立 FIXED part（应折入 body visual，违反 Rule 1）
- 装饰（mark/stamp/cap）常数尺寸悬浮于缩放后 sheave/板面之外

## 与相邻类别的边界
- 不该混入：Carabiner / snap-hook / rappel ring（无 sheave 转轮，属相邻类；kit inset 里出现但排除）
- 不该混入：chain hoist / winch / gin wheel / capstan（缠绳绞车，非重定向/机械增益滑轮）
- 不该混入：rope thimble / aluminium sleeve（非滑轮五金）

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 初版；sheave CONTINUOUS-Y 为必现核心机构；body_form 为 ③ 主形态 slot；sheave_count 为唯一 multiplicity 轴。 |

## 模板实现备注
- 共享 helper：`_grooved_sheave_geometry`（revolved，plate/shell 用）、`_flanged_sheave`（3-cyl，tube 用）、`_plate_mesh`、`_hook_mesh`、`_cam_jaw` / `_capture_cam`、`_u_bail` / `_becket_eye`。
- 捕获-pin element-scoped allow_overlap：axle_pin_i∩sheave bore、cam_pin∩bushing、swivel shank∩collar、（tube）axle∩flange/groove、rope∩body slot。
- 静态 attachment（fixed_eye/fixed_hook/u_bail/becket）折入 root part visual，不建独立 part、不建 FIXED joint。
- Rule 5：`fail_if_parts_overlap_in_sampled_poses(ignore_fixed=True)` + 每机构一条 targeted `ctx.pose`。
