# Modular Spec — emergency_exit_door

## 元信息
| 项 | 值 |
|---|---|
| slug | `emergency_exit_door` |
| template path | `agent/templates/emergency_exit_door.py` |
| test path (optional) | `tests/agent/test_emergency_exit_door_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel_children：多叶片挂到共同 frame；linear_chain：panic bar → latch/rod 机构链；multiplicity：active leaf 数 N∈{1,2}） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 14 |
| read_count | 14 |
| read_scope | all 5-star samples in this subcategory (2 origin anchors + 12 forks) |
| source_index_policy | only adopted module sources are indexed below |

阅读要点：
- **26c10e（origin, 001.png）** — loop 化 `add_door_leaf(name, side)` / `add_push_bar(name)`；纯 Box/Cylinder。frame（jamb_0/1 + header + threshold + hinge_line）为 root；door_0/door_1 各一条独立非 mimic REVOLUTE 铰（`frame_to_door_i`，轴 ±Z，origin 在 jamb hinge line）；每叶一条 PRISMATIC touch bar（`door_i_to_push_bar_i`，轴 −Y，行程 0.015）；door_0 带外露 vertical_rod + 4×rod_clamp + top/bottom latch（静态 visual）。这是本模板采用的**基准坐标系与骨架**。
- **e8695a（origin, 002.png）** — cadquery `mesh_from_cadquery` 圆角箱做 hardware；`_add_leaf_panel` / `_add_fixed_panic_hardware` helper；near/far leaf REVOLUTE（far 用 mimic）；near_push_bar PRISMATIC 驱动 center latch_bolt（PRISMATIC mimic ×1.65）。证明 touch-bar→latch 联动机构。
- **single_leaf** — 仅 door_0 一叶，frame 右 jamb 变 strike jamb；N=1。
- **leaf_and_half** — door_0 宽 active（1.15）+ door_1 窄 inactive（0.53，flush bolt 顶底，无 push bar）；N=2 不等宽。
- **sidelite** — 单 active leaf + 固定玻璃 sidelite 面板（frame root 上的静态 visual）+ mullion，frame 加宽。
- **transom** — frame 升高（frame_height 2.60），header 上方加 transom_header + transom_mullion + 2×transom_glass（frame root 静态玻璃）。
- **overhead_closer** — near_leaf 上加 surface closer housing（visual）+ `closer_arm` 一条 REVOLUTE（`near_leaf_to_closer_arm`，mimic hinge ×0.5，随门开折臂）。
- **vision_lite** — door slab 上开小 wired-glass lite（vision_glass + 4 条 glazing bead），静态。
- **narrow_vision** — 竖长满高玻璃条（同族，见 source map）。
- **full_glazed** — 叶片改 stile-and-rail：窄 anodized 边框 stile/rail + 大块 tinted glass_infill（③ Macro Surface Construction）。
- **vertical_rod** — SVR device：push_bar PRISMATIC 驱动 top_rod / bottom_rod 两条 PRISMATIC（mimic push bar），穿过 4×rod_clamp（captured-shaft，element-scoped allow_overlap）。
- **crash_paddle** — pivoting paddle 一条 REVOLUTE（`near_leaf_to_push_paddle`）+ latch_bolt PRISMATIC；paddle 绕水平顶边轴内翻。
- **recessed_bar** — flush touch plate 沉入 door skin mortise pocket，PRISMATIC，driving latch（mimic ×1.65）。
- **probe_glazed_paddle** — full_glazed 叶 + crash_paddle 组合（兼容性探针，converged）。

## 核心身份

一扇建筑疏散门：至少一片铰接（REVOLUTE）门叶在固定 frame 内向外摆动，配 panic/exit 硬件（横推 touch bar / 竖杆 SVR / crash paddle / 沉入式 touch bar），带 “EXIT / push to open” 绿色标识。默认成熟域：单/双钢制或玻璃疏散门叶 + panic 硬件 + 钢 frame，可带固定 sidelite / transom 玻璃、overhead closer。

**不该混入**：普通室内通过门/入户门（仅 lever/knob，无 panic 硬件）；gate / turnstile / 卷帘 / overhead shutter / 旋转门（非铰接摆叶）；window / 幕墙。

## 槽位 + 候选模块表

### Slot A：opening_config（① 骨架 + multiplicity：active leaf 数 N 与开口拓扑）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `double_leaf` | origin_anchor | rec_...26c10e | L96-L235 | eligible if compatible | frame(jamb_0/1+header+threshold+2 hinge_line) root；door_0/door_1 等宽（0.84）各一条独立 REVOLUTE（±Z）；N=2 |
| `single_leaf` | forked_anchor | rec_..._var_single_leaf | L53-L233 | eligible if compatible | frame 右 jamb 变 strike jamb（无 door_1）；door_0 一条 REVOLUTE；N=1 |
| `leaf_and_half` | forked_anchor | rec_..._var_leaf_and_half | L47-L297 | eligible if compatible | door_0 宽 active（1.15）+ door_1 窄 inactive（0.53，flush bolt 顶/底，无 push bar，独立 REVOLUTE）；N=2 不等宽 |
| `single_plus_sidelite` | forked_anchor | rec_..._var_sidelite | L58-L160 | eligible if compatible | 加宽 frame + mullion + 固定玻璃 sidelite（frame root 静态 visual）；door_0 一条 REVOLUTE；N=1 |

### Slot B：leaf_form（③ 主体形态家族 / Primary Form Family，作用于每片 active leaf）

| module_name | source_type | form_subtype | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|---|
| `solid_slab` | origin_anchor | Planar Boundary Form | rec_...26c10e | L108-L143 | eligible if compatible | 实心 galvanized slab + hinge/meeting stile + top/bottom rail（Box） |
| `vision_lite` | forked_anchor | Planar Boundary Form | rec_..._var_vision_lite | L146-L173 | eligible if compatible | slab + 小 wired-glass lite（vision_glass + 4 glazing bead）近顶部 |
| `narrow_vision` | forked_anchor | Planar Boundary Form | rec_..._var_narrow_vision | L146-L200（同族） | eligible if compatible | slab + 竖长满高玻璃窄条（vertical glazed strip + bead） |
| `full_glazed` | forked_anchor | Macro Surface Construction | rec_..._var_full_glazed | L121-L229 | eligible if compatible | stile-and-rail：窄 anodized 边框 + 大块 tinted glass_infill（读作整片玻璃叶） |

### Slot C：panic_hardware（② 关节/机构类型，作用于 active leaf）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `touch_bar` | origin_anchor | rec_...26c10e | L146-L214,L238-L255 | eligible if compatible | bar_mount 静态 housing + 横 push_bar（Cylinder rail + 端盖）PRISMATIC（−Y，0.015） |
| `vertical_rod` | forked_anchor | rec_..._var_vertical_rod | L163-L324 | eligible if compatible | push_bar PRISMATIC + top_rod/bottom_rod 两条 PRISMATIC（mimic push bar）穿 4×rod_clamp |
| `crash_paddle` | forked_anchor | rec_..._var_crash_paddle | L472-L582 | eligible if compatible | pivoting paddle 一条 REVOLUTE（水平顶边轴）+ latch_bolt PRISMATIC |
| `recessed_bar` | forked_anchor | rec_..._var_recessed_bar | L420-L647 | eligible if compatible | mortise pocket（宿主叶面凹槽 visual）+ 沉入 touch plate PRISMATIC + latch_bolt（mimic） |

### Slot D：header_style（① frame 上沿延伸 / ④ 固定玻璃）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `plain_header` | origin_anchor | rec_...26c10e | L55-L59 | eligible if compatible | 普通钢 header 封顶（无 transom） |
| `glazed_transom` | forked_anchor | rec_..._var_transom | L38-L100 | eligible if compatible | frame 升高 + transom_header + transom_mullion + 2×transom_glass（frame root 静态玻璃） |

降级理由：header 变化只有一个 fork（transom），故本 slot 2 candidate；plain 为 origin 基准，transom 为唯一 source-backed 上沿延伸。已过 reviewer。

### Slot E：closer（② 关节类型：可选 overhead closer 联动臂）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `no_closer` | origin_anchor | both origins | — | eligible if compatible | 无 closer（默认） |
| `overhead_arm` | forked_anchor | rec_..._var_overhead_closer | L420-L565,L730-L750 | eligible if compatible（gate：plain_header 且非 sidelite） | near_leaf 上 closer housing（visual）+ `closer_arm` 一条 REVOLUTE mimic hinge（×0.5，随门开折臂） |

降级理由：closer 只有一个 fork 支撑，`no_closer`（origin 双锚）为基准；2 candidate，其中 `overhead_arm` 唯一 source-backed 联动臂。已过 reviewer。

## 槽位图（slot graph）

pattern: mixed（parallel_children + linear_chain + multiplicity）

```
[Slot A opening_config]  frame(root)  --REVOLUTE(axis ±Z @ jamb hinge_line)-->  door_0 [+ door_1]   (parallel children，每叶独立铰)
        |                                                                              |
     [Slot D header_style] 静态加到 frame root（plain / transom 玻璃）          [Slot B leaf_form] 决定 door_i 主体形态（solid/vision/narrow/full_glazed）
        |                                                                              |
     [Slot A sidelite]   sidelite/mullion 静态加到 frame root                    [Slot C panic_hardware] 挂到 active leaf：
                                                                                    touch_bar → PRISMATIC push_bar
                                                                                    vertical_rod → push_bar PRISMATIC + 2×rod PRISMATIC(mimic)
                                                                                    crash_paddle → paddle REVOLUTE + latch PRISMATIC
                                                                                    recessed_bar → touch plate PRISMATIC + latch(mimic)
        |
     [Slot E closer]  overhead_arm → closer_arm REVOLUTE(mimic hinge) 挂到 active(near) leaf；housing visual 加到 leaf，anchor bracket visual 加到 frame
```

接口点位：
- **frame → door_i（REVOLUTE）**：origin 在 jamb hinge_line（x=±hinge_x, z=sill_height），轴 (0,0,±1)，range [0, 1.55]。pin 铰 → grandfathered（omit MatingContract；origin 落在 hinge_line cylinder 硬件上，过 origin-far 检查）。
- **active leaf → push_bar / touch plate（PRISMATIC）**：origin 在叶前面 bar 高度（z≈1.055），轴 (0,−1,0)（touch）或 (0,+1,0)（e8695a 方向）；行程 0.015–0.024。captured-slider：bar 经 back_contact_pad 接触 bar_mount → 连通；pressed pose 与 mount overlap 用 element-scoped allow_overlap。prismatic origin gauge-exempt。
- **active leaf → top_rod/bottom_rod（PRISMATIC, mimic push_bar）**：origin 在 rod 竖线，轴 (0,0,∓1)；穿 rod_clamp（captured-shaft，element-scoped allow_overlap）。
- **active leaf → paddle（REVOLUTE）**：origin 在 paddle 顶边 pivot pin（硬件 visual），轴 (1,0,0)，range [0,0.35]。pin 铰 grandfathered。
- **active leaf → latch_bolt（PRISMATIC, mimic）**：origin 在 meeting stile 侧，轴 (−1,0,0)，行程 0.050。
- **active(near) leaf → closer_arm（REVOLUTE, mimic hinge ×0.5）**：origin 在 closer housing spindle（硬件 visual），轴 (0,0,1)，range [0,0.52]。pin 铰 grandfathered。

互斥/派生：Slot A 决定 N 与是否有 door_1/sidelite；Slot C 只挂 active leaf（single/sidelite → 1 套；double → door_0 挂完整 C，door_1 挂 touch_bar 简版或 flush bolt（leaf_and_half））；Slot E overhead_arm 仅 gate 到 plain_header ∧ 非 sidelite。

## 每槽位 Module Emits / Interfaces

### Slot A / opening_config
| emits | 描述 | 来源 |
|---|---|---|
| parts | `frame`(root)；`door_0`[；`door_1`] | 26c10e L40-L194 |
| internal joints | `frame_to_door_0` REVOLUTE(±Z, [0,1.55])[；`frame_to_door_1`] | 26c10e L218-L235 |
| frame visuals | jamb_0/jamb_1(或 strike jamb)/header/threshold/hinge_line_i[；mullion + sidelite_glass（sidelite）] | 26c10e L40-L73；sidelite L74-L160 |
| downstream interface | frame root face（供 Slot D/E 静态挂件）；active leaf front face（z≈1.055）供 Slot C | — |

### Slot B / leaf_form
| emits | 描述 | 来源 |
|---|---|---|
| parts | 无新 part（叶片 visual 加到 door_i） | — |
| door visuals | solid_slab：door_slab+stile+rail；vision_lite/narrow_vision：+glass+bead；full_glazed：glass_infill + 窄 stile/rail 框 | 各 fork |
| internal joints | 无（叶体不动，作为 door_i 的 visual） | Rule 1 |

### Slot C / panic_hardware
| emits | 描述 | 来源 |
|---|---|---|
| parts | `push_bar_i`/`push_paddle`/`touch_plate`[；`top_rod`/`bottom_rod`；`latch_bolt`] | 各 fork |
| static leaf visuals | bar_mount/mount_slot（touch）；rod_clamp×4（vertical_rod）；mortise pocket 壁（recessed）；paddle bracket 座 | 各 fork |
| internal joints | PRISMATIC push（−Y/+Y）[；PRISMATIC rod×2 mimic；REVOLUTE paddle；PRISMATIC latch mimic] | 各 fork |
| upstream interface | active leaf front face | — |

### Slot D / header_style
| emits | 描述 | 来源 |
|---|---|---|
| frame visuals | plain：普通 header；glazed_transom：transom_header+mullion+2×transom_glass，frame_height 升高 | transom L38-L100 |
| internal joints | 无（transom 玻璃静态） | Rule 1 |

### Slot E / closer
| emits | 描述 | 来源 |
|---|---|---|
| parts | overhead_arm：`closer_arm` | closer L508-L565 |
| static visuals | closer housing/mounting plate/spindle（加到 near leaf）；anchor bracket/shoe（加到 frame） | closer L420-L500 |
| internal joints | overhead_arm：`near_leaf_to_closer_arm` REVOLUTE mimic hinge ×0.5 | closer L730-L750 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| opening_config | enum | double_leaf/single_leaf/leaf_and_half/single_plus_sidelite | double_leaf | choice | procedural sampler | Slot A 表 |
| leaf_form | enum | solid_slab/vision_lite/narrow_vision/full_glazed | solid_slab | choice | procedural sampler | Slot B 表 |
| panic_hardware | enum | touch_bar/vertical_rod/crash_paddle/recessed_bar | touch_bar | choice | procedural sampler | Slot C 表 |
| header_style | enum | plain_header/glazed_transom | plain_header | choice | procedural sampler | Slot D 表 |
| closer | enum | no_closer/overhead_arm | no_closer | conditional | overhead_arm 仅在 plain_header ∧ 非 sidelite 合法，否则回退 no_closer | Slot E 表 |
| palette_style | enum | galvanized_steel/satin_offwhite_steel/fire_door_red/brushed_stainless/bronze_glass/matte_black_brass | galvanized_steel | choice | rng.choice(PALETTE_STYLES) | ⑥ 见 §8.5 |
| leaf_count(N) | int(derived) | {1,2} | 2 | equation | `= 2 if opening_config∈{double_leaf,leaf_and_half} else 1` | multiplicity |
| door_height | float | [1.95, 2.12] | 2.03 | independent | 范围内均匀采样后 clamp | 26c10e L36 / e8695a |
| leaf_width（每 active 叶） | float | 派生 | 0.84 | equation | double：`opening/2−seam`；single：`opening`；leaf_and_half：wide=1.15·s / narrow=0.53·s | 各 fork |
| door_thickness | float | [0.040, 0.052] | 0.045 | independent | clamp | 26c10e L37 |
| opening_width_scale | float | [0.94, 1.08] | 1.0 | independent | clamp；驱动 frame span 与 leaf_width | 26c10e |
| bar_travel | float | [0.014, 0.024] | 0.015 | independent | push bar PRISMATIC upper | 26c10e/e8695a |
| latch_travel | float | 派生 | 0.050 | equation | `= bar_travel · 1.65`（mimic multiplier）或固定 0.050 | e8695a L582 |
| rod_retraction | float | 派生 | 0.025 | equation | `= bar_travel · (0.025/0.015)`（vertical_rod mimic） | vertical_rod L215 |
| paddle_open | float | [0.28, 0.38] | 0.35 | independent | crash paddle REVOLUTE upper | crash_paddle L570 |
| hinge_upper | float | [1.35, 1.55] | 1.55 | independent | 叶开启角上界（clamp，clearance 允许） | 26c10e L225 |
| (—) | constraint | — | — | inequality | `leaf_width_total ≤ opening_width − center_seam`（双叶不互穿）；违反按比例回缩 | 接口 |
| (—) | constraint | — | — | inequality | rod/latch/bar 行程内叶片自身与 clamp 为 captured-shaft，element-scoped allow_overlap，非碰撞失败 | Rule 5 |

**采样契约**：先采 independent（door_height/thickness/opening_width_scale/bar_travel/paddle_open/hinge_upper）→ 派生 equation（leaf_width/latch_travel/rod_retraction/N）→ inequality 投影回缩（leaf 总宽 ≤ 开口）→ conditional 解析（closer 合法性按 header/sidelite gate）。全部在 `resolve_config` 内求解。

### 7.5 编译预算 / compile budget（必填）
自报 **12s/seed**。依据：全 Box/Cylinder 基元（无 cadquery 布尔/放样），单 seed 约 40–80 个 visual，最重的是双叶 + full_glazed + vertical_rod + transom（~90 visual）。tessellation：Cylinder（hinge_line/push bar rail/rod/pivot pin）≤32 段；无英雄雕刻面。N 个相同子件（rod_clamp、glazing bead、bar_end）复用同参数 Box。超预算先降 Cylinder 段数再迭代。sweep `--compile-timeout 120`（≈10×预算 watchdog）。

## Multiplicity / Copy Logic

**轴 1：active leaf 数 N（主轴）**
- `count_param`：door leaf 数 / `frame_to_door_i` 铰数（= active push_hardware 套数）。`N_range`：产品域 {1,2}；测试全程覆盖两值。sampling domain：由 `opening_config` enum 派生（double_leaf/leaf_and_half→2，single_leaf/single_plus_sidelite→1），权重经 enum 均匀采样（4 值等概 → N=2 概率 0.5、N=1 概率 0.5）。
- copied object = door leaf via `_add_door_leaf(name, side, width, active)`，side=+1/−1 关于中缝镜像；naming door_0/door_1、push_bar_0/push_bar_1；placement 关于 frame 中线对称；joint policy = 每叶一条独立非 mimic REVOLUTE 铰（±Z），active 叶另挂一套 panic 硬件。>2 叶不属本小类（排除）。

**轴 2：SVR rod guide clamp 数（固定，非采样）**
- `count_param`：rod_clamp 数，固定 = 4（源 vertical_rod 恒 4）。不暴露 `*_count`，不随 seed 变。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或一条边 | 有 | Slot A：double_leaf(frame+2 铰叶)/single_leaf(1 铰叶+strike jamb)/leaf_and_half(宽 active+窄 inactive 各一铰)/single_plus_sidelite(1 铰叶+固定 sidelite)；Slot D：plain/glazed_transom(frame 上沿+3 静态件)；Slot E：+closer_arm 一条 REVOLUTE。全 forked_anchor/origin source-backed。 |
| └ multiplicity | 同构件 ×N | 有 | 见 §8：active leaf N∈{1,2}（enum 派生，权重 0.5/0.5）；rod_clamp 固定 4。 |
| ② 关节类型 | 图不变换 type/轴 | 有 | REVOLUTE leaf 铰(±Z, 所有)；PRISMATIC touch bar(−Y)；PRISMATIC SVR rod×2 mimic(±Z)；REVOLUTE crash paddle(X 轴)；PRISMATIC latch(−X) mimic；REVOLUTE overhead closer arm(Z) mimic。source-backed；每种在 sweep 中经 slot_choices 出现。 |
| ③ 主体形态家族 / Primary Form Family | 换核心叶体几何原型 | 有（登记进 slot_choices=Slot B） | solid_slab(Planar Boundary Form：实心 slab+stile/rail)；vision_lite(Planar Boundary：小 lite 开口)；narrow_vision(Planar Boundary：竖长满高玻璃条)；full_glazed(Macro Surface Construction：stile-and-rail 大玻璃叶)。4 个可识别原型，source-backed forked_anchor。 |
| ④ 表面装饰 | 原型不变叠表面细节 | 有 | 绿色 “push to open” exit sign + 白字条（record_only，所有叶）；hinge stile/meeting stile/top&bottom rail 凸线；kick-plate；vision lite glazing bead；SVR rod_clamp；mortise pocket 边框。装饰写成宿主 door part visual，按叶最终面（leaf_width/leaf_form）派生 x_center/z（③→⑤→④）。source_type=record_only + world_knowledge_extrapolation（fire-door red/stainless 配色下的同族装饰）。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | door_height[1.95,2.12]、door_thickness[0.040,0.052]、opening_width_scale[0.94,1.08]、leaf_width 派生、hinge_upper[1.35,1.55]、bar_travel[0.014,0.024]、paddle_open[0.28,0.38]（见 §7）。**运动包络**：leaf 铰 axis ±Z / 开向 +Y / [0, hinge_upper]；push bar axis −Y / [0,bar_travel]；SVR rod axis ±Z / [0,rod_retraction]；paddle axis +X / [0,paddle_open]；latch axis −X / [0,latch_travel]；closer arm axis +Z / [0,0.52]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses(max_pose_samples=48, ignore_fixed=True)`；captured-shaft（rod↔clamp、bar↔mount、latch↔stile、touch_plate↔pocket）用 element-scoped allow_overlap；targeted `ctx.pose`：叶开 0.8·upper 验证 +Y 摆出、push bar 压下验证 −Y 位移（及 latch/rod 联动缩回）、paddle 内翻验证、closer arm 随门折臂。全程不穿模。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 材质大类：metal(galvanized/stainless/painted steel) + glass(wired/tinted) + painted。配色 6：galvanized_steel、satin_offwhite_steel、fire_door_red、brushed_stainless、bronze_glass、matte_black_brass。material 大类覆盖 metal+glass+painted ≥ ceil(0.5×6)=3。source_type：record_only（前两、bronze_glass）+ world_knowledge_extrapolation（fire-door red/stainless/matte-black brass，crash_paddle run_notes 列出的 companion colorways）。 |

**收尾自检**：0-9 seed 渲染须肉眼可见：solid/vision/narrow/full_glazed 主体形态拉开；metal 与 glass 配色都出现；exit sign/stile/bead 贴合叶面不悬空；叶开合、bar 压下、rod/latch/paddle 联动全程不穿模。

## 采样与覆盖审计

总组合数：A(4) × B(4) × C(4) × D(2) × E(2, gated) = 256 名义组合（closer gate 后有效 ~192）。加 N∈{1,2}（由 A 派生）与连续尺度，充分。

理由：主多样性来自离散 Slot A/B/C（③ 形态家族在 B 登记进 slot_choices），D/E 为 source-backed 上沿/联动扩展；连续尺度只做局部比例/行程微调，均在 `resolve_config` clamp/派生，不破坏铰接与身份。

seed_domain_policy：procedural_first（seed 0 不特殊）。
Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `random.Random(seed)` 依次采 A/B/C/D，用去相关流采 palette；closer 用条件 gate（plain_header ∧ 非 sidelite 才允许 overhead_arm，否则 no_closer）。`resolve_config` 归一化非法组合（透明化 gate），解连续尺度。无 curated/modulo 主表；无 regression override（首版）。random sweep 0-35 初检、0-999 成熟度观察。
Topology target：256 名义 slot tuple，>300 目标下 combos + N + 连续档足够；report-only。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | 顺序采 A→B→C→D→palette(去相关)→continuous；closer 条件 gate | slot_choices_for_seed 与 build 选择一致 |
| compatibility matrix | overhead_arm gate=plain_header∧非 sidelite；leaf_and_half 的 door_1 恒 flush-bolt inactive（不挂 panic C）；C 挂 active leaf；full_glazed + 任意 C 合法（probe 已 converged） | 无悬空/穿模/轴/closed-pose/max-N/bulky/optional-child 失败 |
| controlled local variation | door_height/thickness/opening_width_scale/bar_travel/paddle_open/hinge_upper 连续 clamp；leaf_width/latch/rod 派生 | 比例变化不破坏 interface/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | 0-35 初 pass，0-999 成熟度 | contract failures; axis_realization; viewer |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A opening_config | 4 | yes | yes | |
| B leaf_form (③) | 4 | yes | yes | Primary Form Family slot |
| C panic_hardware | 4 | yes | yes | |
| D header_style | 2 | yes | no | 单 fork 支撑，降级说明见 Slot D |
| E closer | 2 | yes | no | 单 fork 支撑，gated；降级说明见 Slot E |

## Validator

- slot_choices_for_seed 返回已实现 module 名（A/B/C/D/E + palette）
- config_from_seed 对所有普通 seed（含 0）用 deterministic procedural sampling
- compatibility gating 阻止非法组合（overhead_arm 仅 plain_header∧非 sidelite；door_1 inactive 不挂 panic）
- 无 endless curated/modulo 主表；无 regression override
- 连续 scale 在 resolve_config clamp/派生，不破坏 interface/clearance/joint origin/N
- 关键关节存在：`frame_to_door_0` REVOLUTE ±Z；active leaf panic PRISMATIC/REVOLUTE 按 C；mimic 联动（rod/latch/closer）
- 复制件命名/对称 placement 遵循 policy（door_i/push_bar_i，中线镜像）
- 每片 active leaf 有 exit sign + panic 硬件（身份）；帧内每片叶有铰

## Reject cases

- 无 panic/exit 硬件（退化为普通门）→ fail 身份
- 叶不铰接 / 无 REVOLUTE leaf 铰 → fail
- 双叶闭合互穿或与 frame 穿模（closed pose）→ fail
- panic bar/paddle/rod 行程中穿模（sampled pose，无正当 captured-shaft allow_overlap）→ fail
- leaf/hardware 悬空（isolated part / island，无接触支撑）→ fail
- exit sign / stile / bead 常数尺寸套在缩放或 full_glazed 叶面上悬浮（违 Rule 4）→ fail
- >2 active 叶 / sliding/roller/turnstile 拓扑 → 越出小类
- closer arm 或 latch 用 FIXED 假关节或漂浮 → fail

## 与相邻类别的边界

- 不该混入：普通室内/入户门（Door/Double_Door）——缺 panic/exit 硬件与 exit 标识，是本小类的 must_keep。
- 不该混入：Sliding/Garage shutter/Folding gate/Gate/Turnstile——非铰接摆叶机构族。
- 不该混入：Window/幕墙——无可通行铰接门叶。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | Slot D/E 为 2-candidate（各单 fork 支撑）已在表内说明降级理由；③ 形态家族由 Slot B 承载并登记进 slot_choices。 |

## 模板实现备注（可选）

- 共享 helper：`_add_door_leaf(model, door, r, mats, *, side, width, active, leaf_form)` 生成叶体（B）+ 静态 panic 座；`_add_panic_hardware(...)` 按 C 生成活动件与关节；`_add_frame(...)`（A+D）；`_add_closer(...)`（E）。
- captured-shaft element-scoped allow_overlap：bar↔bar_mount(pressed)、rod↔rod_clamp、latch↔meeting stile/center block、touch_plate↔mortise pocket 壁、closer_arm↔housing。
- push bar 用 back_contact_pad 与 bar_mount 保证接触连通（防 isolated part）。
- 全 Box/Cylinder（Rule 3 备注：hardware 为矩形金属件，box 形本身即 26c10e 5★ 源形；圆角 mesh 仅 e8695a 装饰性差异，不属英雄雕刻面下放）。
- leaf 铰、paddle、closer arm 为 pin 铰 → omit MatingContract（grandfathered），origin 落在 hinge_line/pivot pin/spindle 硬件 visual 上。
```
