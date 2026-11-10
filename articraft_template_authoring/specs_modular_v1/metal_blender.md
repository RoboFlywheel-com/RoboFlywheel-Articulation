# metal_blender — bench manual metal bender / forming machine — Modular Spec

> 来源小类：`picture/0611/Metal_blender`（articraft_data 上游小类样本池；"Blender" 是小类源名 typo，实体是 **manual metal bender / bench forming machine**）。
> 上游 source map：`picture_expansion/template_source_maps/0611__Metal_blender.md`。
> 参考图：`picture/0611/Metal_blender/001.png`（FB-4 风格 bench steel bending brake：宽底板 + 主 housing + 长翻杆 + 三辐 handwheel + 左侧成形手柄）。
> **同步/评级注记**：本 spec 引用的 `model.py:Lx-Ly` 来自该小类的 workbench-only 样本（1 parent origin + 10 已采纳 REDO fork），已同步进本仓库。`record.json` 的 `rating` 字段读为 `null`（workbench fork 未回填评级），source map / P2 已把这 11 个记为"variant-review 已通过、可进 proto-spec"的采纳集；本 spec 即以这 11 个为唯一 module 来源。

## 元信息
| 项 | 值 |
|---|---|
| slug | `metal_blender` |
| template path | `agent/templates/metal_blender.py`（stem `metal_blender`）|
| test path (optional) | `tests/agent/test_metal_blender_template.py`（不写，sweep 为唯一验收）|
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `parallel_children`（frame 根 + 3 个 parallel movable children：clamp_lever / feed_handwheel / forming_crank；所有可替换 slot 皆为固定模块 / 主体形态 / 装饰层的替换，不改 4-part 骨架、不改 3 根非-FIXED 关节集）|

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 11（1 parent origin + 10 已采纳 REDO fork，均 workbench-only；`rating=null` 见上方注记，source map 已背书为采纳集）|
| read_count | 11（parent 全文 + 每个 fork 与 parent 的完整 diff：header / frame / lever / handwheel / crank / joint / run_tests 段全部读到）|
| read_scope | all adopted samples in this subcategory |
| source_index_policy | 仅被采纳为 module source 的样本进入下方 source 表与 §14 |

**分流说明**：11 个样本共享同一 skeleton：`frame` 根 + `clamp_lever` + `feed_handwheel` + `forming_crank` 共 4 part、3 根非-FIXED 关节（`clamp_lever_pivot` REVOLUTE y、`feed_handwheel_spin` CONTINUOUS x、`forming_crank_pivot` REVOLUTE x）。fork 只改**固定模块 / 主体形态 / 附加成形辊 / 装饰层**：`forming_topology` 变体新增/换成形辊几何但仍挂 `forming_crank`；`clamping` 变体只重塑 `clamp_lever` visual；`feed_motion` 变体极少数把 feed 关节改成 PRISMATIC —— **本 spec 保守起见 采用 origin baseline 的 CONTINUOUS feed 语义**，不采样 PRISMATIC feed 分支（motion-safety：sampled-pose overlap 稳定性 + spec §8.5 ② 无独立轴的诚实归档见 §8.5）；`die_profile` 变体只改 `fixed_die` 的凸模轮廓（③ 主体形态家族）。

## 核心身份

**手动金属折弯机 / bench forming machine**：核心是一台**紧凑台式钢制折弯 / 成形机**（FB-4 风格 bench steel bending brake），非厨房 blender、非动力冲床。世界系：Z 向上，长翻杆（clamp lever）向 −X 伸出（左端为握把），右端（+X）是三辐 handwheel（进给 / 压力调整），左端（−X）是成形手柄（forming crank，绕 X 轴旋转翻折工件），后方（+Y）是靠背/后挡（backstop），主 housing 居中，宽底板带 4 只穿孔脚脚垫钉在工作台上。核心 part 集：
- `frame`（根，FIXED；含：`base_plate` 宽底板 + `housing_shell` 主壳 + `rear_plinth`/`front_plinth`/`lower_rail` 支撑肋 + `left_backstop` + `left_spindle_bracket` + `fixed_die` 固定凸模（③ 主体形态家族）+ `reference_strip` + `clamp_pivot_bracket` + `feed_bearing`/`forming_bearing` 两只 annular tube 轴承 + `blank_badge`/`badge_accent`/`inspection_port` + 4×`front_fastener_{i}` + 4×`foot_{i}` 脚垫）。
- `clamp_lever`（REVOLUTE y，[0, 0.82] rad）：长杠杆板 `lever_plate` + 端部 `lever_grip` 塑握把 + `pivot_pin` 轴销（scoped allow_overlap 于 `clamp_pivot_bracket`）。
- `feed_handwheel`（CONTINUOUS x，360°）：`screw_core` 主轴（scoped allow_overlap 于 `feed_bearing`）+ 12×`thread_crest_i` 螺纹脊 + `wheel_hub` 轮毂 + 3×`spoke_i` 辐条 + `hub_nut` 六角螺母 + `acorn_cap` 帽盖。
- `forming_crank`（REVOLUTE x，[−1.35, 1.35] rad）：`crank_shaft` 长成形轴（scoped allow_overlap 于 `forming_bearing`）+ `crank_hub` + `tommy_bar` 手柄杆 + `paddle_grip` 手柄头 + `bar_stop` 端塞。

活动语义（motion 主契约，全部继承自 origin baseline，10 forks 中 8 保留、2 个 feed_motion 变体改 PRISMATIC 我们排除；见 §8.5 ②）：**clamp_lever 翻起夹紧（REVOLUTE y，[0, 0.82]）+ feed_handwheel 连续转（CONTINUOUS x）+ forming_crank 前后翻折（REVOLUTE x，[−1.35, 1.35]）**。默认成熟域：单台整机，桌面挂钉在工作台上。

不该混入（详见 §11）：**厨房 immersion_blender / blender_countertop**（这是纯食物 blender / 电动搅拌器 —— 完全不同类别，虽然小类名撞车但 image 与 source 记录都明确是 bench bender）；**动力冲床 stamping_press**（powered ram + 电机 flywheel，本类是手动 crank + handwheel）；**bench vise**（只有夹紧，无成形辊/凸模）。

## 槽位 + 候选模块表

> **建模注记**：4-part 骨架 + 3 根非-FIXED 关节 **在所有 candidate 组合下不变**。以下 3 个 slot 是"可替换的固定模块 / 主体形态 / 附加成形辊几何"，构成拓扑多样性 = A×B×C 笛卡尔积 + palette。所有 candidate 均**不新增关节、不改 3 根非-FIXED 关节的 origin/axis/limit**（motion-safety 硬契约）。

### Slot A：forming_topology（成形拓扑——由 `forming_crank` 附加成形辊 / 保留 tommy_bar 手柄决定的作业形态）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| classic_bench_brake（基线） | forked_anchor | S1 parent origin | `forming_crank` L357-L390 + `fixed_die` L166-L173 | eligible if compatible | 经典弯折 brake：`forming_crank` 装 `tommy_bar` + `paddle_grip` + `bar_stop`（无附加辊），配合 `fixed_die` 上凸模作板料弯折 |
| bead_roller | forked_anchor | S2 `rec_0611_metal_blender_var_forming_topology_bead_roller` | `forming_crank.visual(...beading_roll..., "lower_forming_roll")` L432-L439 + upper roll on feed_handwheel L344-L354 段 | eligible if compatible | 双辊压筋机：`forming_crank` 保 tommy_bar 且加装 `lower_forming_roll`（带凸筋/沟槽的旋转辊）；同一 `forming_crank_pivot` REVOLUTE x，range 扩到 [−π, π]（bead 卷筋要连续多圈） |
| three_roll_slip_roller | forked_anchor | S3 `rec_0611_metal_blender_var_forming_topology_three_roll_slip_rolle` | `forming_crank` 段 L393-L432（改 CONTINUOUS + wheel_hub 装 roll）| eligible if compatible | 三辊卷板：`forming_crank` 加装圆柱辊；本 spec 为守 motion-safety **保 REVOLUTE x + range [−1.35, 1.35]**（不采样 CONTINUOUS 分支，见 §8.5 ②）；侧重卷板辊几何 |
| v_die_press_brake | forked_anchor | S4 `rec_0611_metal_blender_var_forming_topology_v_die_press_brake` | `forming_crank`+forming_bearing 段 L364-L432 + upper V-die 段 | eligible if compatible | V-die press brake：`forming_crank` 保 tommy_bar；`fixed_die` 侧凸模变 V 形（与 die_profile 交叉受控，见 §9） |

硬约束记录：forming_topology 4 candidate（≥3 目标 ✔）。全部为 forked_anchor（S1-S4）。四者共享 `forming_crank` part 名 + `forming_crank_pivot` 关节（type/axis/origin/limit **不变**；bead_roller 单独把 upper limit 放宽到 π 我们**回退到 1.35** 以保 sampled-pose 稳定，见 §7.5 / §8.5）；差异在 `forming_crank` 内部附加的 mesh（成形辊 / 无辊）+ `fixed_die` 顶面凸模高度轮廓（V 分支与 die_profile V 联动）。所有 candidate 皆保 tommy_bar + paddle_grip（保 targeted pose 检测）。

### Slot B：clamping_style（`clamp_lever` 主体形态——夹紧机构的可识别形态原型）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| classic_lever_plate（基线） | forked_anchor | S1 parent origin | `clamp_lever` L259-L303 | eligible if compatible | 经典过中心夹紧长杠杆：`lever_plate` 长七边形板（带 slot 长孔 + pivot 圆孔）+ 后端粗方 `lever_grip` + 中心 `pivot_pin` |
| eccentric_cam_clamp | forked_anchor | S5 `rec_0611_metal_blender_var_clamping_eccentric_cam_clamp` | `clamp_lever` 段 L272-L332 | eligible if compatible | 偏心凸轮夹紧：`lever_plate` 主板 + 偏心凸轮盘 visual（挂在 lever_plate 上） + `lever_grip` + `pivot_pin`；同一 REVOLUTE y、range 收紧到 [0, 0.68] |
| screw_beam_clamp | forked_anchor | S6 `rec_0611_metal_blender_var_clamping_screw_beam_clamp` | `clamp_lever` 段 L279-L340 | eligible if compatible | 螺杆压梁夹紧：`lever_plate` + 附加 `screw_core` 螺杆 visual（挂在 lever_plate 上）+ `lever_grip` + `pivot_pin`；同一 REVOLUTE y、range [0, 0.82] |

硬约束记录：clamping_style 3 candidate（≥3 目标 ✔），全部 forked_anchor。三者共享 `clamp_lever` part 名 + `clamp_lever_pivot` 关节（type/axis/origin **不变**；eccentric 变体单独把 upper limit 稍收紧我们**保持 0.82 上限但把 targeted pose 用 0.68 rad** 以保稳）；差异在 `lever_plate` 主板轮廓 + 是否加装偏心凸轮 / 螺杆 visual。所有 candidate 皆保 `pivot_pin` + `lever_grip`（保源 targeted pose 检测与 captured-pin allow_overlap）。

### Slot C：die_profile（③ 主体形态家族 / Primary Form Family——`fixed_die` 凸模轮廓的可识别几何形态原型）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | form_subtype | 结构特征 |
|---|---|---|---|---|---|---|
| flat_die（基线） | forked_anchor | S1 parent origin | `fixed_die` L166-L173 | eligible if compatible | Planar Boundary Form | 长矩形棱模：`cq.Workplane("XY").box(0.31, 0.042, 0.020).edges("|X").chamfer(0.003)`；平顶带边倒角，工件沿 X 走 |
| round_bead_die | forked_anchor | S7 `rec_0611_metal_blender_var_die_profile_round_bead_dies` | `fixed_die` 段（长条 + 圆弧顶）| eligible if compatible | Volumetric Envelope Form | 圆珠筋凸模：主 box 上顶叠一条纵向圆弧脊（`Cylinder` 半嵌 + 沿 X 长条），弯出圆珠筋 |
| sharp_v_die | forked_anchor | S8 `rec_0611_metal_blender_var_die_profile_sharp_v_dies` | `fixed_die` 段（V 形棱） | eligible if compatible | Planar Boundary Form | 尖 V 形凸模：主 box 上顶叠 V 形棱（两个倾斜 box 拼成三角脊），弯出锐角 V 折 |

硬约束记录：die_profile 3 candidate（≥3 目标 ✔，且形态主导类要求登记 ③ slot ✔）。全部 forked_anchor（S1/S7/S8）。三者共享 `fixed_die` visual 名（挂 frame）+ 挂点（`origin` 落在 frame 顶面上方 z≈0.259 附近）+ 材质 `black_oxide` + primitive 家族（cadquery mesh）；差异在顶面凸模轮廓（平/圆弧/V）。**form_subtype**：flat = Planar Boundary（矩形边界）；round_bead = Volumetric Envelope（圆弧包络的凸起）；sharp_v = Planar Boundary（三角脊边界）。装饰性叠加保持在 `fixed_die` 的 visual 组内（同一 part），不新增独立 part / 关节。

## 槽位图（slot graph）

```text
pattern: parallel_children on frame root

                             frame (ROOT, FIXED)
                             ├─ base_plate / housing_shell / plinths / rails / backstop
                             ├─ Slot C: fixed_die  ← ③ Primary Form Family
                             │   （flat / round_bead / sharp_v — frame 内 visual）
                             ├─ reference_strip / clamp_pivot_bracket
                             ├─ feed_bearing / forming_bearing  ← annular tube 轴承（收纳右/左侧轴）
                             ├─ blank_badge / badge_accent / inspection_port
                             ├─ front_fastener_×4 / foot_×4
   ┌─────────────────────────┼─────────────────────────┐
   │ REVOLUTE y              │ CONTINUOUS x            │ REVOLUTE x
   │ clamp_lever_pivot       │ feed_handwheel_spin     │ forming_crank_pivot
   │ origin=(0.060,          │ origin=(0.255, 0.0,     │ origin=(−0.255,
   │        −0.091, 0.285)   │        0.170)           │        −0.032, 0.145)
   │ axis=(0, 1, 0)          │ axis=(1, 0, 0)          │ axis=(1, 0, 0)
   │ limit=[0, 0.82]         │ CONTINUOUS              │ limit=[−1.35, 1.35]
   ▼                         ▼                         ▼
 clamp_lever              feed_handwheel           forming_crank
 （Slot B                  （固定内部：screw_core     （Slot A 变体 attaches：
   classic /                + thread_crests + hub      classic tommy_bar /
   eccentric /              + spokes + hub_nut         + lower_forming_roll (bead) /
   screw_beam）             + acorn_cap）              + roll cylinder (three_roll) /
 - lever_plate                                        + tommy_bar (v_die)）
 - lever_grip
 - pivot_pin
```

接口点位与关节策略（全部继承 origin，candidate 不改）：
- **frame → clamp_lever**：REVOLUTE，axis=(0, 1, 0)，origin=(0.060, −0.091, 0.285)，limit=[0, 0.82]；pivot 落在 `clamp_pivot_bracket` 圆孔上。captured-pin：`pivot_pin` ↔ `clamp_pivot_bracket`（scoped allow_overlap，源模板 grandfathered，无 MatingContract）。
- **frame → feed_handwheel**：CONTINUOUS，axis=(1, 0, 0)，origin=(0.255, 0.0, 0.170)；轴穿过 `feed_bearing` annular tube 中心。captured-pin：`screw_core` ↔ `feed_bearing`（scoped allow_overlap，grandfathered）。
- **frame → forming_crank**：REVOLUTE，axis=(1, 0, 0)，origin=(−0.255, −0.032, 0.145)，limit=[−1.35, 1.35]；轴穿过 `forming_bearing` annular tube 中心。captured-pin：`crank_shaft` ↔ `forming_bearing`（scoped allow_overlap，grandfathered）。
- **Slot A / B / C**：均**同一 part 内变形**（Slot A 换 `forming_crank` 附加 mesh；Slot B 换 `clamp_lever` 主板轮廓 + 附加 visual；Slot C 换 `fixed_die` 顶面凸模轮廓）；无跨 slot 关节；均随所在 part 的关节 origin 派生（clamp_lever ↔ clamp_pivot_bracket，forming_crank ↔ forming_bearing 沿 X）。

互斥 / 派生说明：Slot A 各 candidate 均保 tommy_bar + paddle_grip（targeted pose 需读它们）；bead_roller 的 `lower_forming_roll` 与 die_profile 无兼容冲突（辊沿 x 悬挑）。Slot C V-die 与 Slot A v_die_press_brake 独立组合（不强联动）——V-die C candidate 是 fixed_die 顶面轮廓、A v_die_press_brake 是 forming 侧几何；两者可各自出现或同时。

## 每槽位 Module Emits / Interfaces

### Slot A / forming_topology（classic / bead_roller / three_roll / v_die）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `forming_crank`（part 名不变）；内部 visuals：`crank_shaft`（Cylinder，长 0.17 基线 / bead 加长到 0.70）+ `crank_hub` + `tommy_bar` + `paddle_grip` + `bar_stop` + **Slot A 附加**：`lower_forming_roll` mesh (bead) / roll cylinder (three_roll) | S1 L357-L390 / S2 L404-L439 |
| internal joints | 无（`forming_crank_pivot` REVOLUTE x 挂 frame → forming_crank，type/axis/origin/limit 不变） | S1 L412-L421 |
| upstream interface | `crank_shaft` ↔ `forming_bearing` captured-pin（x-axis 插入 ≥0.014，scoped allow_overlap） | S1 L630-L652 |
| downstream interface | 无 | — |

### Slot B / clamping_style（classic / eccentric / screw_beam）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `clamp_lever`（part 名不变）；内部 visuals：`lever_plate`（cadquery polyline，主板轮廓随 candidate 变）+ `lever_grip`（后端粗方 Box）+ `pivot_pin`（中心 Cylinder，y-axis）+ **Slot B 附加**：偏心凸轮盘 Cylinder (eccentric) / 螺杆 Cylinder (screw_beam) | S1 L259-L303 / S5 L272-L332 / S6 L279-L340 |
| internal joints | 无（`clamp_lever_pivot` REVOLUTE y 挂 frame → clamp_lever） | S1 L392-L401 |
| upstream interface | `pivot_pin` ↔ `clamp_pivot_bracket` captured-pin（y-axis 插入 ≥0.012，scoped allow_overlap） | S1 L582-L604 |
| downstream interface | 无 | — |

### Slot C / die_profile（flat / round_bead / sharp_v）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame` 的 `fixed_die` visual：flat = box+edge chamfer；round_bead = box + 圆弧脊 Cylinder；sharp_v = box + 两倾斜 box 拼三角脊；全部是 frame 内的 visual（非独立 part、非关节） | S1 L166-L173 / S7 / S8 |
| internal joints | 无 | — |
| upstream interface | 挂 frame 顶面上方 z≈0.259（随 `housing_shell` 顶面派生） | S1 L167-L172 |
| downstream interface | 无 | — |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| forming_topology | enum | {classic_bench_brake, bead_roller, three_roll_slip_roller, v_die_press_brake} | — | choice | deterministic sampler 选 | Slot A |
| clamping_style | enum | {classic_lever_plate, eccentric_cam_clamp, screw_beam_clamp} | — | choice | sampler 选 | Slot B |
| die_profile | enum | {flat_die, round_bead_die, sharp_v_die} | — | choice | sampler 选 | Slot C |
| palette_style | enum | {factory_gunmetal, industrial_charcoal, machinery_green, safety_blue, red_industrial, hammertone_gray} | factory_gunmetal | choice | 仅涂装，不改几何（⑥）；≥3 材质大类（painted / brushed / bright metal / black rubber）| §8.5⑥ |
| base_length_scale | float | [0.92, 1.08] | 1.0 | independent | 缩放 base_plate 的 X 维（0.52·s）；随之派生 rear/front 立柱与孔位 | S1 L85 |
| housing_length_scale | float | [0.95, 1.06] | 1.0 | independent | 缩放 housing_shell 的 X 维（0.43·s）；须 ≤ base·0.86（不等式） | S1 L101 |
| lever_length_scale | float | [0.92, 1.08] | 1.0 | independent | 缩放 `lever_plate` 长度与 `lever_grip` 位置 | S1 L266-L297 |
| handwheel_radius_scale | float | [0.94, 1.06] | 1.0 | independent | 缩放 handwheel `wheel_hub`/spoke/hub_nut/acorn_cap 半径与位置 | S1 L327-L354 |
| crank_reach_scale | float | [0.92, 1.08] | 1.0 | independent | 缩放 tommy_bar 长度与 paddle_grip 距离；≤1.10（避免 paddle 撞 frame）| S1 L374-L390 |
| (—) | constraint | — | — | inequality | **housing ≤ base**：`housing_length ≤ 0.86 · base_length`；违反→回缩 housing_length_scale | S1 L85, L101 |
| (—) | constraint | — | — | inequality | **lever 全折 [0, 0.82] 不撞 frame**：clamp_lever 绕 y 从 0 → 0.82 rad sweep 不与 housing 上表面重叠；违反→回缩 lever_length_scale（tommy_bar 端 clearance）| Rule 5 sampled |
| (—) | constraint | — | — | inequality | **forming_crank [−1.35, 1.35] 不撞 backstop / housing**：paddle_grip 绕 x 从 −1.35 → 1.35 sweep 不与 `left_backstop` / `housing_shell` 重叠 | Rule 5 sampled |
| (—) | constraint | — | — | inequality | **feed_handwheel 整圈自转**：3 辐 handwheel 绕 x 整圈不与 frame 重叠；违反→回缩 handwheel_radius_scale（+ housing 端面外的自由空间已由 acorn_cap 位置保证）| Rule 5 sampled |

**连续尺寸采样契约**：先采所有 independent 主尺度（base/housing/lever/handwheel/crank）→ inequality 投影/回缩（housing ≤ base、lever 全折 clearance、crank 全 sweep clearance、handwheel 整圈 clearance）→ 无 equation / conditional 主分支。全部在 `resolve_config` 求解，不留 builder 才失败。

### 7.5 编译预算 / compile budget（必填）

**每-seed 编译预算 ≤ 18s**（依据：库内实测 —— origin 记录 `mesh_from_cadquery` 用了 `_annular_tube_x` × 2 + `_hex_prism_x` + fixed_die box + polyline lever_plate + housing_shell 带 boolean cut，共 6-8 个 cadquery 布尔操作 + ~30 简单 primitive；参照 `manual_grain_mill.py` / `manual_coffee_grinder.py` 同数量级 15-20s；bead_roller 分支额外 1 个 cadquery beading_roll mesh，仍在预算内）。分档 tessellation：`_mesh` 用 `tolerance=0.0009`, `angular_tolerance=0.12`（比 origin 稍粗一档以留头寸）；圆柱 handwheel spoke / 12×thread_crest 直接用 `Cylinder` primitive，不进 cadquery。N 个同构辐条 / 螺纹脊 / 脚垫 / 紧固件复用同一 `Cylinder` primitive（SDK 内部会 dedupe 相同 primitive）。

## Multiplicity / Copy Logic

- **无采样 multiplicity 轴**。3 辐 handwheel spokes（`spoke_0/1/2`）、12 螺纹脊、4 脚垫、4 前紧固件均为**结构常量**（源 records 全一致），不暴露 count 参数、不做加权 N 采样。
- 核心结构由固定 named parts / slot 表达，不通过循环复制模板级 visual / part / joint。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type/来源 · 或 理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | **无** | 11 样本共享同一 part-joint 运动学图（frame 根 + 3 parallel movable children），3 根非-FIXED 关节集恒定。所有 fork 只改固定模块 / 形态 / 附加成形辊 visual —— **不加不减会动的 part / 关节边**。故无 ① 变化轴 |
| └ multiplicity | 同构件 ×N | 无 | 见 §8：3 辐 / 12 螺纹脊 / 4 脚垫 / 4 紧固件均结构常量，非采样轴；无其它复制数量逻辑 |
| ② 关节类型 | 图不变，某条边换 type/轴 | **无** | 全部关节 type/axis 恒定（clamp REVOLUTE y、feed CONTINUOUS x、forming REVOLUTE x）；motion-safety 硬契约禁止改关节 origin/axis/limit。`feed_motion` 变体（PRISMATIC feed）与 bead_roller 的 CONTINUOUS forming 变体 **主动排除** 出采样域（诚实归档：为保 sampled-pose 稳定 + 避免 §11 与 stamping_press 语义混淆）。故无 ② 独立轴 |
| ③ 主体形态家族 | 图&关节不变，换核心 part 的可识别几何形态原型 | **有** | **Slot C die_profile（登记进 slot_choices）**：flat_die（Planar Boundary，forked S1）、round_bead_die（Volumetric Envelope，forked S7）、sharp_v_die（Planar Boundary，forked S8）—— 三种 fixed_die 顶面凸模轮廓，肉眼可辨。附加 Slot A forming_topology（classic tommy_bar / + bead 辊 / + three_roll 辊 / + v_die）也承载次级形态（forming_crank 是否带附加成形辊）。≥3 可识别 die 原型 ✔ |
| ④ 表面装饰 | 原型不变，叠加表面细节 / 改装饰数 | **有** | Slot B clamping_style 的 `lever_plate` 主板轮廓 + 附加凸轮盘 / 螺杆 visual 属主板级几何差异（近 ③），但也叠加了 lever_grip 位置装饰；`blank_badge` / `badge_accent` / `reference_strip` / `inspection_port` / 4×`front_fastener_{i}` 为固定装饰（record_only）；palette 变体带来的 red badge_accent 颜色变化属 ⑥。装饰几何均由宿主 part（frame / clamp_lever）派生嵌入，不悬空 |
| ⑤ 尺寸/行程 | 离散不变，只连续改尺寸/比例/行程 | **有** | 关键比例（见 §7）：base_length_scale [0.92,1.08]、housing_length_scale [0.95,1.06]、lever_length_scale [0.92,1.08]、handwheel_radius_scale [0.94,1.06]、crank_reach_scale [0.92,1.08]。**关节运动包络 + motion_test_plan**：(a) `clamp_lever_pivot` REVOLUTE (0,1,0)、开启方向 +q（抬起手柄），闭合 q=0，可行上界 0.82 —— targeted `ctx.pose({clamp:0.72})` 验 lever_grip z 上升 >0.12；(b) `feed_handwheel_spin` CONTINUOUS (1,0,0) —— `ctx.pose({feed:0.40})` 验 spoke_0 绕 x 转过（|z 位移|>0.025）；(c) `forming_crank_pivot` REVOLUTE (1,0,0)、开启方向 +q（正向翻折）、闭合 q=0，可行 [−1.35, +1.35] —— `ctx.pose({crank:0.70})` 验 paddle_grip 绕 x 转过（|z 位移|>0.04）。需 sampled collision（`fail_if_parts_overlap_in_sampled_poses` max_pose_samples=48，3 joints × 4 状态 + combos）+ 每关节 targeted pose |
| ⑥ 涂装 | 几何全不变，只改材质/颜色 | **有** | 材质大类：**painted**（housing/plinths gunmetal/charcoal）+ **brushed_steel**（lever_plate, reference_strip, blank_badge）+ **bright_steel**（tommy_bar, hub_nut, acorn_cap, thread_crests, fasteners）+ **black_oxide**（fixed_die, screw_core, forming_bearing, lower_rail, inspection_port）+ **black_rubber**（4×foot）+ badge accent（red）。palette ≥6：factory_gunmetal（基线）、industrial_charcoal（更深灰主体）、machinery_green（工业绿主体）、safety_blue（安全蓝）、red_industrial（红机身+黑机构）、hammertone_gray（锤纹灰）。材质大类覆盖：painted + brushed + bright + black_oxide + rubber ≥ ceil(0.5×6)=3 ✔（前 3 类每 palette 都出现）|

**收尾自检**：0-9 seed 渲染须肉眼可见——三种 die profile（平/圆珠/V）拉得开、Slot A 四种 forming（无辊 / bead 辊 / three_roll 辊 / v_die）可辨、Slot B 三种 clamp（经典/凸轮/螺杆）可辨、6 palette metal/painted/rubber 三大类都出现、clamp/forming 全程 sweep 不穿模、handwheel 整圈自转不撞。

## 采样与覆盖审计

总组合数：forming_topology(4) × clamping_style(3) × die_profile(3) = **36** 离散拓扑组合（palette 6 与 5 连续 scale 不计入结构 distinct）。

理由：3 个登记 slot 每候选均可达且 ≥3 distinct（A=4、B=3、C=3），无单候选 slot；sampler 对每 slot 独立均匀采样，全兼容（无互斥 gate）；reachable 全覆盖。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 deterministic `random.Random(seed)` 对 3 个 slot 各独立均匀采样（forming/clamping/die 各 uniform），再采 palette_style（6 态均匀）与 5 个连续 scale（§7 契约：independent → inequality 回缩）。seed=0 不特殊。compatibility：无非法组合（全兼容），仅 inequality 收紧连续 scale（housing ≤ base、lever/crank/handwheel sweep clearance）。random sweep：seeds 0-35 首轮（fast 0-15 + final 16-35），0-999 成熟审计。

Topology target：1000-seed slot choice tuple distinct 上限 = 36（本类别离散结构轴的天花板）。**低于富类别建议 300 的理由**：本小类是**单骨架、单关节拓扑的手动机床**——11 个采纳样本共享同一 part-joint 图与 3 根非-FIXED 关节集（motion-safety 明确禁止新增/改关节），真实结构变化轴仅限 ③ die 形态 + Slot A 成形辊附加 + Slot B clamp 主板；核心装配为结构常量。36 已穷尽 source-backed 合法离散组合；进一步"变多样"只能靠连续 scale + palette 在每个拓扑内产生视觉分化，非虚构新拓扑。1000-seed 视觉 distinct 远高于 36（36 × 6 palette × 5 scale 连续域），但结构 distinct 天花板即 36。report-only。

Controlled local parameterization：base/housing/lever/handwheel/crank 五个连续 scale（范围/clamp/inequality 见 §7）；全部在 `resolve_config` 求解，不破坏 InterfaceSpec（3 根 captured-pin allow_overlap）与 3 根非-FIXED 关节 origin/axis/limit。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 3 slot 各独立均匀采样 + palette(6) + 5 连续 scale；顺序 independent → inequality | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | 全兼容无互斥；inequality（housing/lever/crank/handwheel sweep）收紧连续 scale 回缩，不丢离散组合 | 无悬空 / 无穿模 / 关节 sweep 覆盖 / captured-pin allow_overlap 正确 |
| controlled local variation | §7 的 5 个 scale + 4 条 inequality | 比例变化不破接口 / clearance / 关节 origin |
| regression overrides | none（首版不需要；若 sweep 暴露特定失败 seed 再稀疏加，记 seed+理由）| 仅已知失败回归 |
| random sweep | seeds 0-35 首轮，0-999 成熟审计 | contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A forming_topology | 4 | yes | yes | 全 forked_anchor |
| B clamping_style | 3 | yes | yes | 全 forked_anchor |
| C die_profile（③）| 3 | yes | yes | Planar×2 + Volumetric×1 |

## Validator

- `slot_choices_for_seed(seed)` 返回已实现的 module 名（A/B/C 各自）
- `config_from_seed(seed)` 对所有 ordinary seed 用 deterministic procedural sampling（seed=0 不特殊）
- compatibility 无非法组合；inequality 收紧连续 scale 回缩
- 5 连续 scale 全部在 `resolve_config` clamp 并解 inequality（housing/lever/crank/handwheel sweep clearance），不留 builder 失败
- 关键 InterfaceSpec：3 个 captured-pin scoped allow_overlap（pivot_pin↔clamp_pivot_bracket / screw_core↔feed_bearing / crank_shaft↔forming_bearing），每个含 `expect_contact` + `expect_overlap`（axis + min_overlap）
- 3 根非-FIXED 关节 type/axis/origin/limit 恒定：clamp_lever_pivot REVOLUTE y limit [0, 0.82]；feed_handwheel_spin CONTINUOUS x；forming_crank_pivot REVOLUTE x limit [−1.35, 1.35]
- 4-part set 恒定：{frame, clamp_lever, feed_handwheel, forming_crank}
- palette_style 驱动全部 materials（每个 visual 从 palette 派生，不裸 RGBA）
- targeted pose：clamp 0.72 grip 抬起 >0.12；feed 0.40 spoke_0 位移 >0.025；crank 0.70 paddle 位移 >0.04
- `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)` 通过（Rule 5）
- die_profile 顶面轮廓可辨（`fixed_die` visual 存在 + 附加轮廓 visual 根据 candidate）

## Reject cases

- 改动 3 根非-FIXED 关节的任一 origin/axis/limit，或新增/删除会动的 part（违反 motion-safety 硬契约；如把 forming 改 CONTINUOUS 或把 feed 改 PRISMATIC）
- 把 fixed_die 拆成独立 part（离开 frame）→ 违反 Rule 1（不动的凸模不该 FIXED 出去）
- forming_crank 全 sweep（[−1.35, 1.35]）时 paddle_grip 撞 backstop 或 housing（未在 resolve_config 回缩 crank_reach_scale）
- clamp_lever 全折（q=0.82）时 lever_grip 或 tommy_bar 撞 housing 顶面（未回缩 lever_length_scale）
- feed_handwheel 整圈（CONTINUOUS）时 spoke 或 hub_nut 与 frame 相撞（未回缩 handwheel_radius_scale）
- captured-pin overlap 未声明（会引发 `fail_if_parts_overlap_in_current_pose`）：pivot_pin↔bracket / screw_core↔feed_bearing / crank_shaft↔forming_bearing
- 主 seed domain 是小型 curated / modulo 表；或只靠 palette / 连续 scale 撑多样性（③ die_profile 必须离散出现）
- 把类别当成厨房 blender（immersion_blender / blender_countertop）—— 无 impeller、无电机、无杯体
- 把类别做成 stamping_press（powered ram + 电动 flywheel）—— 本类是**手动** crank + handwheel

## 与相邻类别的边界

- 不该混入 **immersion_blender / blender_countertop**（同名邻类，源类型名 "Metal_blender" 是 typo）：厨房 blender 主体是**杯 + 电机 + 刀片**，属食物加工；本类别核心身份是**桌面手动金属折弯 / 成形机**（长翻杆 + handwheel + 手柄成形辊 + 固定凸模），无杯体 / 无刀片 / 无电机。
- 不该混入 **powered stamping_press**：动力冲床有**电机 + 飞轮 + 上冲头**竖直往复；本类别是**手动** crank + handwheel，凸模固定于 frame。
- 不该混入 **bench_vise / clamp**：台钳只有夹紧螺杆，无成形辊、无凸模、无 forming crank。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | SPEC_ONLY_DRAFT。单骨架形态主导物：③ die_profile（3，登记 slot）+ A forming_topology（4）+ B clamping_style（3）= 36 离散组合 + 6 palette + 5 连续 scale。无采样 multiplicity。3 根非-FIXED 关节 motion-safety 硬契约（禁改 origin/axis/limit；主动排除 feed PRISMATIC 与 forming CONTINUOUS 分支以保稳）。36 <300 已在 §9 说明。**待模板阶段落实**：(1) slug `metal_blender` 加入 `cli/template.py` TEMPLATE_REGISTRY；(2) `resolve_config` 求解 §7 全 inequality；(3) 3 个 targeted pose + sampled collision（max_pose_samples=48）；(4) captured-pin scoped allow_overlap × 3。|

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C + root | classic_bench_brake / classic_lever_plate / flat_die / 全部 4-part 骨架 + 3 关节 | rec_picturex_0611__metal_blender__001__png_5eda8fb0cd7845e4a6db2e727f235d1e | L52-L423（build_object_model）+ L426-L688（run_tests）| 全 skeleton + 基线各 slot + 3 root 关节 + 3 captured-pin allow_overlap |
| S2 | A | bead_roller | rec_0611_metal_blender_var_forming_topology_bead_roller | L404-L439（forming_crank 加 lower_forming_roll）| 双辊压筋成形拓扑 |
| S3 | A | three_roll_slip_roller | rec_0611_metal_blender_var_forming_topology_three_roll_slip_rolle | L393-L432（forming_crank 加辊）| 三辊卷板拓扑（本 spec 保 REVOLUTE，见 §8.5 ②）|
| S4 | A | v_die_press_brake | rec_0611_metal_blender_var_forming_topology_v_die_press_brake | L364-L432 + upper V 段 | V-die 折弯拓扑 |
| S5 | B | eccentric_cam_clamp | rec_0611_metal_blender_var_clamping_eccentric_cam_clamp | L272-L332 | 偏心凸轮夹紧 clamp_lever 变体 |
| S6 | B | screw_beam_clamp | rec_0611_metal_blender_var_clamping_screw_beam_clamp | L279-L340 | 螺杆压梁 clamp_lever 变体 |
| S7 | C | round_bead_die | rec_0611_metal_blender_var_die_profile_round_bead_dies | fixed_die 段 | 圆珠筋凸模 |
| S8 | C | sharp_v_die | rec_0611_metal_blender_var_die_profile_sharp_v_dies | fixed_die 段 | 尖 V 凸模 |

## 模板实现备注（可选）

- 深读参考模板（按 pattern / 关节拓扑 / 接口选，不按类别名）：`Urban_Environment_Caster_Trolley2`（parallel_children 范式 + palette_style 驱动全 materials + captured-pin scoped allow_overlap）、`manual_grain_mill.py` / `manual_coffee_grinder.py`（同类桌面手动机床、frame + crank 语义 + cadquery 布尔预算）。
- **compile 成本预算**：cadquery 布尔操作集中在 `housing_shell.cut(feed_bore).cut(forming_bore)` + `base_plate` 4 孔 + `_annular_tube_x` × 2 + `_hex_prism_x`；die_profile 三候选中 round_bead 加一段圆弧脊 Cylinder（Cylinder primitive，不进 cadquery），sharp_v 加两段倾斜 box union。整机 ≤ 18s/seed（见 §7.5）。
- **captured-pin / scoped allow_overlap**（复刻 origin，3 处，grandfathered 无 MatingContract）：`pivot_pin` ↔ `clamp_pivot_bracket`（y-axis，min_overlap 0.012）；`screw_core` ↔ `feed_bearing`（x-axis，0.014）；`crank_shaft` ↔ `forming_bearing`（x-axis，0.014）。每处均 `expect_contact` + `expect_overlap`。
- **主动排除的变体分支**（诚实归档，见 §8.5 ②）：`feed_motion_rack_handwheel_feed` / `feed_motion_lead_screw_carriage_feed` 把 feed 改 PRISMATIC —— 排除，我们保 CONTINUOUS x；`forming_topology_three_roll_slip_rolle` 把 forming 改 CONTINUOUS + range → π —— 保 REVOLUTE + [−1.35, 1.35]（只借用其辊几何）。
- **stem / registry**：文件 stem `metal_blender`，registry key `metal_blender`（需加入 `cli/template.py` TEMPLATE_REGISTRY）。
