# Modular Spec — circuit_breaker (Electrical_Wiring / Circuit breaker)

## 元信息
| 项 | 值 |
|---|---|
| slug | `circuit_breaker` |
| registry key | `Electrical_Wiring_Circuit_breaker` |
| template path | `agent/templates/Electrical_Wiring_Circuit_breaker.py` |
| test path (optional) | `tests/agent/test_circuit_breaker_template.py` (skipped while batch-authoring) |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（fixed housing 根 + 单 revolute toggle 子；N 极 multiplicity；case/handle/terminal/front/mount 离散轴由 config enum 分支实现，cushion 式 hand-roll，不用 SlotSpec assembler） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 8 |
| read_count | 8 |
| read_scope | all 5-star samples in this category（2 origins + 6 forks，逐一读 model.py） |
| source_index_policy | only adopted module sources are indexed below |

**逐样本要点**
- **A `rec_use...eeb289c4`（origin，白 3P CHINT NB1-63H）**：`housing`(Box `molded_case` 0.054×0.072×0.086) + `blue_handle_assembly`(REVOLUTE)。全 Box+Cylinder。per-pole 端子腔+phillips 螺丝+槽（2 行×3 极 loop）、接触指示窗/bezel（per-pole）、fixed white 分隔肋 / pivot 框 / socket、side vents、DIN latch。handle：`blue_common_pivot_cylinder`(Cyl) + per-pole `blue_rotor_drum`/`index_rib` + **3 个复制粘贴 `blue_toggle_paddle_0/1/2`** + `blue_tie_bar`。joint `housing_to_blue_handle` REVOLUTE axis=(1,0,0) origin=(0,-0.0465,-0.013) limits[-0.42,0.42]。**pole_x=(-0.018,0,0.018)**。
- **B `rec_use...7bb9b32f`（origin，黑 2P Eaton/CH）**：`housing` + `toggle`(REVOLUTE)。**`body_shell`=`mesh_from_geometry(ExtrudeGeometry(rounded_rect_profile(0.074,0.064,0.006),0.110))`**，**`side_vent_panel`=`SlotPatternPanelGeometry`**（rule ③ 必保留）。per-pole 黄铜螺丝端子 top/bottom + 红/黑 `wire_jacket`+`copper_core` 引线；`rating_label`、`detent_stop_on/off`、`pivot_cheek`/`pivot_bearing`、`rotor_pocket`。toggle：`pivot_shaft`(Cyl) + per-pole `rotor_drum`/`rotor_hub`/`index_rib` + `common_tie_bar`+`finger_ridge`+ per-pole `thumb_paddle`。joint axis=(-1,0,0) origin=(0,-0.039,0.064) limits[0,0.50]。B 用 Z=挤出/竖直，X=极宽，Y=深度。
- **1pole@B / 4pole@A（N multiplicity）**：4pole 已把 `pole_x=tuple((i-(N-1)/2)*spacing)`、`housing_width=N*spacing`、分隔肋/pivot 框/pocket、`pivot_cyl_length=width+0.008`、`tie_bar_length=width+0.006` 全部 loop 化并随 N 求解（复制粘贴 paddle 改成 loop）。→ 模板 N-loop 蓝本。
- **mccb_rotary_handle@A**：删 3 个 per-pole paddle，换 **单个宽 `mccb_flipper_body` Box(0.048×0.008×0.024)** 跨全宽 + grip ribs（loop）+ on/off print，同一 revolute pivot。
- **plugin_stab_terminals@B**：删螺丝腔/引线，换 **flat `top_stab_blade`/`bottom_stab_blade` Box(0.010×0.003×0.024) tinned_copper**，嵌壳并上/下突出（`allow_overlap(body_shell, stab)` 保留）。
- **rcbo_test_button@A**：加 **proud 黄 `rcbo_test_button_cap`(Cyl) + bezel + dimple + T/IΔn print**，全部在 housing（fixed），仅 handle 动。
- **surface_mount_base@B**：删/并 DIN，加 **`mounting_foot` Box(0.090×0.004×0.130) 法兰 + 4 角 `mounting_hole`/`recess`(Cyl)**。

## 核心身份

一枚 **DIN 导轨模块化断路器 (MCB)**：注塑外壳 (`housing`, fixed 根) + 唯一一个绕极轴(X)转动的 **操作 toggle** 子件——toggle 携带 per-pole 转子鼓 (`rotor_drum`) 串在共享 `pivot_shaft` 上，并把手柄(flag/rocker/flipper)固定在鼓外缘。极特征沿 pole_x 元组复制 N 次；tie-bar / pivot 轴长随 N 求解。前面板有端子(螺丝/引线/插拔片)、评级标签、可选接触指示窗或 RCBO 测试钮；背面 DIN 弹卡或表面螺钉法兰。

不该混入：**配电箱/面板**（无外壳阵列、无 breaker field、单一器件）；**浪涌保护器/插座开关**（无插座、无指示灯板阵列）。单器件、单 revolute DOF。

## 槽位 + 候选模块表

> 采用 cushion 式 hand-roll：`case_form` 是主 ③ 主体形态家族 slot（登记进 `slot_choices`）；`handle_form` 是 toggle 上的次 ③ 形态家族 slot；`terminal_type`/`front_feature`/`mount` 是 housing 上的 ④ 表面硬件/装饰离散轴；`pole_count` 是 ① multiplicity。所有轴都进 `slot_choices_for_seed`，供 `axis_realization`。

### Slot ③A：case_form（housing 主体形态家族，PRIMARY ③ slot）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling | 结构/form_subtype |
|---|---|---|---|---|---|
| `box_case` | forked_anchor | A eeb289c4 | L41-L46 | eligible | `Box` 矩形棱柱。**Volumetric Envelope Form**（直棱柱包络） |
| `rounded_case` | forked_anchor | B 7bb9b32f | L40-L47（`ExtrudeGeometry`+`rounded_rect_profile`+`mesh_from_geometry`） | eligible | 圆角挤出壳。**Volumetric Envelope Form**（圆角/倒角包络）。rule ③ 保留 mesh 原语 |
| `stepped_case` | world_knowledge_extrapolation(③) | anchors: A L41-L66（`molded_case`+更宽 `top/bottom_terminal_block` 台肩 + 内缩 `front_label_area`）+ reviewer | 生成函数 `_case_stepped` | eligible | Box 主体 + 内缩窄前盖阶 + 外伸端子肩，改变宏观表面读法。**Macro Surface Construction**。同 part tree/interface，仅改壳表面构成 |

### Slot ③B：handle_form（toggle 操作件形态家族）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling | 结构 |
|---|---|---|---|---|---|
| `flag_toggle` | forked_anchor | A eeb289c4 | L278-L313（per-pole `blue_toggle_paddle`+`off_print`，**改 loop**） | eligible | 窄高旗形拨杆 ×N |
| `thumb_rocker` | forked_anchor | B 7bb9b32f | L300-L330（`common_tie_bar`+`finger_ridge`+per-pole `thumb_paddle`） | eligible | 宽拇指摇片 ×N + 手指脊 |
| `mccb_wide_handle` | forked_anchor | mccb_rotary_handle@A | L278-L313（单 `mccb_flipper_body`+grip ribs loop，无 per-pole paddle） | eligible | 单个宽联动扳把跨全宽 |

### Slot ④C：terminal_type（housing 端子硬件）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling | 结构 |
|---|---|---|---|---|---|
| `screw_cavity` | forked_anchor | A eeb289c4 | L123-L145（腔`Cyl`+phillips`Cyl`+槽`Box`，2 行×极 loop） | eligible | 前面板螺丝盒端子 |
| `screw_wire_leads` | forked_anchor | B 7bb9b32f | L49-L73,L127-L150（黄铜螺丝 + 红/黑`wire_jacket`+`copper_core`） | eligible | 螺丝端子 + 带引线 |
| `plugin_stab` | forked_anchor | plugin_stab_terminals@B | L48-L70（`top/bottom_stab_blade` tinned_copper，嵌壳突出） | eligible | 扁平插拔/母排 stab 片 |

### Slot ④D：front_feature（housing 前面板特征）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling | 结构 |
|---|---|---|---|---|---|
| `indicator_window` | forked_anchor | A eeb289c4 | L193-L204（per-pole `contact_indicator_bezel`+`green_indicator_window`） | eligible | 接触指示窗 ×N |
| `plain_label` | forked_anchor | B 7bb9b32f | L79-L126（`front_arc_label_band`+`rating_label`，无窗无钮） | eligible | 纯评级标签 |
| `rcbo_test_button` | forked_anchor | rcbo_test_button@A | L216-L256（proud `cap`+`bezel`+`dimple`+T/IΔn print） | eligible | RCBO 残流测试钮 |

### Slot ④E：mount（housing 安装）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling | 结构 |
|---|---|---|---|---|---|
| `din_clip` | forked_anchor | A L243-L254 / B L155-L185 | — | eligible | DIN 导轨弹卡（背板+钩+爪） |
| `surface_screw_base` | forked_anchor | surface_mount_base@B | L200-L230（`mounting_foot` 法兰 + 4 角孔/沉孔） | eligible | 表面螺钉法兰底 |

> 2 候选（mount 样本池只支持 DIN 与表面两态；真实 MCB 也只有这两大安装法）——达标，非降级。其余 slot 均 ≥3。

### ① multiplicity slot：pole_count N

见 §8。N ∈ {1,2,3,4}（1pole@B / 2P(B) / 3P(A) / 4pole@A 全 source-backed；模板可外推更高 N，采样稀有）。

## 槽位图（slot graph）

pattern: mixed（parallel decoration on fixed root + 单 revolute 子 + N multiplicity）

```
housing (FIXED 根，part=housing)
  ├─ case_form         → 决定 shell 原语（Box / rounded-extrude mesh / stepped）+ 端子台肩 + pivot 轴承 + side_vent(SlotPatternPanelGeometry) + 分隔肋 + prints
  ├─ terminal_type     → per-pole 端子 visuals（top/bottom 行 loop）加到 housing
  ├─ front_feature     → 前面板 visuals 加到 housing
  ├─ mount             → 背面/侧安装 visuals 加到 housing
  └─[housing_to_toggle REVOLUTE axis=(1,0,0) @ front pivot line (0, front_pivot_y, pivot_z), limits[-0.40,0.40]]→
       toggle (part=toggle)
         └─ handle_form → pivot_shaft(跨 N 极) + per-pole rotor_drum/hub/index_rib(loop) + tie_bar(长∝N) + 手柄(flag paddles ×N / thumb rockers ×N / 单 mccb flipper)
```

- 唯一跨 part 连接 = `housing_to_toggle` REVOLUTE。轴 = 极轴 X，穿过 `pivot_shaft`（toggle 子件 local 原点，(0,0,0) 含于其内）；joint origin 落在前部 `handle_escutcheon`（raised 前 hub，rotor drum 嵌其中，captured pivot）+ 侧 `pivot_cheek_*` 硬件 2mm 内，满足 origin-proximity（<15mm）。
- 所有非活动件（case/terminal/front/mount/分隔/vent/print）= `housing.visual(...)`（Rule 1），不作独立 FIXED part。
- pivot line 在 front face 前方 y=front_pivot_y=-0.046；toggle 鼓/手柄 proud of 前面。

## 每槽位 Module Emits / Interfaces

### housing 骨架（case_form 承载）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `housing`（fixed 根） | A L37 / B L36 |
| visuals | shell(Box|rounded-extrude|stepped 台肩)、top/bottom_terminal_block、front_label_panel、per-pole `pole_separator`、`handle_escutcheon`(raised hub) + 侧 `pivot_cheek_{0,1}`、`side_vent_panel`(SlotPatternPanelGeometry)、per-pole prints、`detent_stop_on/off` | A L41-L254 / B L36-L267 |
| internal joints | 无（全 fixed 融进 housing visual） | Rule 1 |
| downstream(用于 revolute) | 前 pivot 线 (0, front_pivot_y, pivot_z)；轴承硬件 `pivot_bearing_*` | A L327-L336 / B L332-L348 |

### toggle（handle_form 承载）
| emits | 描述 | 来源 |
|---|---|---|
| parts | `toggle`（revolute 子） | A L258 / B L271 |
| visuals | `pivot_shaft`(Cyl，含 local 原点) + per-pole `rotor_drum`/`rotor_hub`/`rotor_index_rib`(loop) + `common_tie_bar`(长=width+0.006) + handle-form geom | A L259-L325 / B L273-L330 / mccb L278-L313 |
| internal joints | 无 | — |
| upstream | `pivot_shaft` local (0,0,0)，joint origin 落其上；轴 X = 其对称轴 | A L327 / B L332 |

## 参数范围汇总
| 参数 | 类型 | 取值范围/候选 | 标称默认 | 约束类型 | 约束/函数 | 来源 |
|---|---|---|---|---|---|---|
| case_form | enum | box/rounded/stepped | box | choice | 采样 | Slot ③A |
| handle_form | enum | flag_toggle/thumb_rocker/mccb_wide_handle | flag_toggle | choice | 采样 | Slot ③B |
| terminal_type | enum | screw_cavity/screw_wire_leads/plugin_stab | screw_cavity | choice | 采样 | Slot ④C |
| front_feature | enum | indicator_window/plain_label/rcbo_test_button | indicator_window | choice | 采样 | Slot ④D |
| mount | enum | din_clip/surface_screw_base | din_clip | choice | 采样 | Slot ④E |
| pole_count N | int | [1,4]（外推更高稀有） | 2 | multiplicity | 加权采样（小 N 高频） | §8 |
| palette_style | enum | 5 colorways | white_blue | choice | 采样 | §8.5 ⑥ |
| pole_spacing | float | 常量 0.018 | 0.018 | const | DIN 18mm/module | A L39 |
| body_depth_scale | float | [0.92,1.10] | 1.0 | independent | clamp | ⑤ |
| body_height_scale | float | [0.92,1.12] | 1.0 | independent | clamp | ⑤ |
| handle_throw | float | [0.32,0.46] rad | 0.40 | independent | clamp（joint upper=+throw, lower=-throw） | A L335 |
| (—) | constraint | — | — | equation | `housing_width = N*pole_spacing`；`pivot_cyl_len = housing_width+0.008`；`tie_bar_len = housing_width+0.006`；`din/flange width = housing_width(+margin)` | 4pole L45,293,334 |
| (—) | constraint | — | — | inequality | handle 全程(±throw)不与 housing 前面板/端子/front_feature 穿模；越界回缩 throw | Rule 5 |

## 7.5 编译预算 / compile budget
**≤12 s/seed**（依据：全 Box+Cylinder，仅 `rounded_case` 用 1 个 `ExtrudeGeometry` 挤出 + 每壳 1 个 `SlotPatternPanelGeometry` side vent —— 库内 Box/Cyl 类典型 5-10s）。分档：cylinder/screw 小特征默认段数即可（半径≤7mm）；side-vent/extrude 单次；per-pole 子件复用同一 helper（N 个 drum 同几何），visual 数随 N 线性。超预算先降 side-vent slot 密度再迭代。`--compile-timeout 120` 仅作 watchdog。

## 8. Multiplicity / Copy Logic

**1 根 multiplicity 轴：pole_count N。**
- `count_param` = `pole_count`；`N_range` 产品域 = [1,4]（测试偏小；模板结构上可外推 N>4，但采样稀有/不进常规 sweep 主域）。
- sampling domain（权重档）：N=1:0.30, N=2:0.35, N=3:0.20, N=4:0.15（1P/2P 最常见，3P/4P 主断/三相稀）。
- copied object：per-pole = `rotor_drum`+`rotor_hub`+`rotor_index_rib`（toggle）、`terminal_*`/`stab_*`/`wire_*`（housing top+bottom 2 行）、`indicator_*`/prints；handle=flag/rocker 时 per-pole paddle，mccb 时不复制（单件）。
- naming：`{elem}_{col}`，col ∈ range(N)；端子行再 `{elem}_{row}_{col}`。
- placement：`pole_x=tuple((i-(N-1)/2)*pole_spacing)`；分隔肋在相邻极中点 `range(N-1)`；outer 肋/cheek 在 `±(housing_width/2)`。
- joint policy：所有极特征随同一 `housing_to_toggle` revolute 转（在 toggle 上的）或 fixed（在 housing 上的）；不新增 joint。
- source/gating：4pole@A + 1pole@B 证明 N-loop 求解；`pivot_cyl_len`/`tie_bar_len`/`din_width`/`flange_width` 全随 `housing_width` 求解。

## 8.5 视觉多样性 6 轴考察

| 轴 | 判断 | 有/无 | 取值/理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动的 part 或边 | 无（单一图） | 所有真实 MCB = `housing`(fixed 根)+`toggle`(1 revolute 子) 同一 part-joint 图；A/B 两 origin 一致。不做骨架变体（避免混入配电箱/多器件）。source-backed: A/B 同构 |
| └ multiplicity | 同构件 ×N | 有 | pole_count N∈[1,4]，权重(0.30,0.35,0.20,0.15)；见 §8。source-backed: 1pole@B,4pole@A |
| ② 关节类型 | 换 type/轴 | 无 | 断路器唯一 DOF = toggle 绕极轴 X 的 REVOLUTE；所有 8 样本一致，无 prismatic/continuous 语义。声明单一 revolute，全 sweep 出现 |
| ③ 主体形态家族 | 换核心 part 几何原型 | **有（双 ③ slot）** | **case_form**（housing）：box(Volumetric Envelope)/rounded(Volumetric Envelope, filleted, `ExtrudeGeometry`)/stepped(Macro Surface Construction) —— box/rounded=forked_anchor，stepped=`world_knowledge_extrapolation`。**handle_form**（toggle）：flag_toggle/thumb_rocker/mccb_wide_handle，全 forked_anchor。均登记进 `slot_choices` |
| ④ 表面装饰 | 叠加表面细节/改数量 | 有 | **terminal_type**(screw_cavity/screw_wire_leads/plugin_stab)、**front_feature**(indicator_window/plain_label/rcbo_test_button)、**mount**(din_clip/surface_screw_base)——均 housing 非结构表面硬件/贴附（`record_only`+`forked_anchor`）；per-pole prints/labels 由前面板 face 逐-pole 派生、随 N/③⑤ 共形（派生序 ③→⑤→④）。装饰数量随 N |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | body_depth_scale[0.92,1.10]、body_height_scale[0.92,1.12]、housing_width=N·0.018；**关节**：`housing_to_toggle` REVOLUTE 轴=X，开启方向=手柄绕 pivot 上/下摆，`[闭合=-throw, 可行上界=+throw]`，throw∈[0.32,0.46]。`motion_test_plan`：跑 `fail_if_parts_overlap_in_sampled_poses`(sampled {0,lower,upper,mid}) + targeted `ctx.pose({joint:upper})`/`{lower}` 断言手柄 z 位移 + 鼓留轴；越界回缩 throw，无需 exemption |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 realistic MCB colorways：white_blue(Chint/Legrand)、black_gray(Eaton)、gray_blue(ABB)、white_red(main switch)、beige_black(Siemens)。材质大类 plastic(case/handle)+metal(terminal/screw/din) 全覆盖；`rng.choice(PALETTE_STYLES)` 每 seed 采样，驱动**每个** `.visual(material=mats[...])` |

**收尾自检**：case_form 三态(box/rounded/stepped)、handle 三态、terminal 三态、front 三态、mount 两态、N 1-4、5 涂装均须在 batch 0-9 肉眼可见；rounded 用 mesh 不降 Box；prints 贴前面板不悬空；手柄 ±throw 全程不穿模。

## 9. 拓扑多样性审计

总组合数：case(3)×handle(3)×terminal(3)×front(3)×mount(2)×N(4) = **648** 离散拓扑组合，×5 palette = 3240。


seed_domain_policy：procedural_first（`config_from_seed(seed)` = `random.Random(seed)` 对每轴独立加权采样，seed 0 不特殊；无 curated/modulo 主域）。1000-seed slot choice tuple distinct 预计 >按 ≥300 report-only 口径观察（648 拓扑组合）。

Procedural Sampling / Sweep Plan：每 seed 采 case_form/handle_form/terminal_type/front_feature/mount（均匀）、N（加权）、palette（均匀）、3 个连续 scale + throw（uniform→clamp）。兼容矩阵见下（几乎全合法，仅少量 clamp/派生，无非法组合）。sweep 0-15→0-35 + corner。

Controlled local parameterization：`body_depth_scale`/`body_height_scale`/`handle_throw` independent+clamp；`housing_width`/`pivot_cyl_len`/`tie_bar_len`/`din_width`/`flange_width` 全 equation 派生自 N，`resolve_config` 内求解，不破 interface/joint origin/multiplicity。

| item | policy | validator/viewer focus |
|---|---|---|
| sampler | 各轴独立采样（N 加权），slot_choices_for_seed 与 build 一致 | slot_choices == build choices |
| compatibility matrix | 全 648 组合合法；`plugin_stab`/`screw_wire_leads`/`screw_cavity` 互斥(单 enum)；mount 二选一；front 三选一。无需 hard gate | 无 floating/collision/axis/multiplicity 失败 |
| controlled local variation | 3 scale + throw，clamp；width/tie/din/flange 派生自 N | 比例变而不破 interface/clearance/joint origin/identity |
| regression overrides | none | — |
| random sweep | 0-35 首过，0-999 成熟审计 | axis_realization / topology report |

| slot | candidate_count | ≥2 | ≥3 | 备注 |
|---|---:|---|---|---|
| case_form (③A) | 3 | yes | yes | box/rounded/stepped |
| handle_form (③B) | 3 | yes | yes | flag/rocker/mccb |
| terminal_type (④C) | 3 | yes | yes | |
| front_feature (④D) | 3 | yes | yes | |
| mount (④E) | 2 | yes | no | 样本池仅 DIN/表面两态（真实唯二安装法），达标非降级 |
| pole_count (①) | 4 | yes(覆盖) | — | N 只覆盖不计 distinct |

## Validator
- slot_choices_for_seed 返回已实现 module 名，与 build 选择一致
- config_from_seed 对所有 seed（含 0）用 deterministic 采样
- 兼容矩阵/gating 排除非法组合（本类几乎全合法）
- 无 regression override
- 连续 scale 全 clamp/派生（width/tie/din/flange 自 N）；`resolve_config` 求解，builder 不失败
- 关键：`housing_to_toggle` REVOLUTE 存在，axis=X，origin 落 `pivot_bearing`/`pivot_shaft` 硬件；handle ±throw 全程不穿模
- 复制件按 `{elem}_{col}` 命名/规则布局；mccb 不复制
- rounded_case 保留 `ExtrudeGeometry`；side_vent 保留 `SlotPatternPanelGeometry`（rule ③）

## Reject cases
- 把 `body_shell`/side_vent 降级成 Box（违 rule ③）
- per-pole paddle 复制粘贴（须 loop）
- 端子/front/mount 做成独立 FIXED part（违 Rule 1，须 housing.visual）
- joint origin 悬在壳中心线 >15mm 无 `pivot_bearing` 硬件
- handle 摆动中撞前面板/端子/front_feature（穿模）
- stab 片/法兰嵌壳未声明 element-scoped `allow_overlap`
- tie_bar/pivot 轴长不随 N（短极浮空 / 长极穿出）
- 单色输出（palette 未驱动 visual）

## 11. 与相邻类别的边界
- 不该混入 **Distribution_board_panel**：那是外壳+多 breaker 阵列/母排 field；本类是单器件，无 enclosure。
- 不该混入 **Surge_protector_switch / 插座开关**：无插座/指示灯板阵列；本类是极轴 revolute 断路开关。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | GATE P3 自检：每候选有真实 model.py:Lx-Ly（stepped=world_knowledge_extrapolation ③ Macro Surface）；无单候选 slot（mount=2 达标）；拓扑审计 648 组合 + 编译预算 ≤12s 均在。 |

## 14. Module Source Index
| source_id | slot | module | sample_id | model.py | 采纳 |
|---|---|---|---|---|---|
| A | ③A/③B/④C/④D | box_case/flag_toggle/screw_cavity/indicator_window | rec_use...eeb289c4 | L37-L338 | 主脊柱 + 4 候选 |
| B | ③A/③B/④C/④D/④E | rounded_case/thumb_rocker/screw_wire_leads/plain_label/din_clip | rec_use...7bb9b32f | L36-L349 | mesh 壳 + side vent + 5 候选 |
| F1 | ③B | mccb_wide_handle | rec_circuit_breaker_var_mccb_rotary_handle | L278-L313 | 单宽扳把 |
| F2 | ④C | plugin_stab | rec_circuit_breaker_var_plugin_stab_terminals | L48-L70 | stab 片 |
| F3 | ④D | rcbo_test_button | rec_circuit_breaker_var_rcbo_test_button | L216-L256 | 测试钮 |
| F4 | ④E | surface_screw_base | rec_circuit_breaker_var_surface_mount_base | L200-L230 | 法兰底 |
| F5/F6 | ① | N-loop | var_1pole / var_4pole | 4pole L38-L45,293-340 | N 求解蓝本 |
