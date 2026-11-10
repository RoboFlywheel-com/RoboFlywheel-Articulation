# Modular Spec — Agricultural / Seed spreader

## 元信息
| 项 | 值 |
|---|---|
| slug | `seed_spreader` |
| template path | `agent/templates/seed_spreader.py` |
| test path (optional) | `tests/agent/test_seed_spreader_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel_children off one grounded `spreader` root + 2 multiplicity axes: broadcast vanes N / ground wheels N；drop-hole N for the drop-bar mechanism） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 7 |
| read_count | 7 |
| read_scope | all 5-star samples in category `seed_spreader` (2 origins + 5 slot-fork variants) |
| source_index_policy | only adopted module sources are indexed below |

读取结论：
- **两个 origin 占满 chassis 两端**：A `..._155130` = 推行式（方锥 hopper 熔进单一 `spreader` part + T 把 + 2 白轮 + 旋盘 spinner，wheels/spinner continuous, lever revolute, gate prismatic）；B `..._034216` = 牵引式（圆角方 hopper + 红钢管架 + 牵引杆/挂钩 + 大 turf 轮 + disc+3vane spinner）。A 是 loop-clean base（`wheel_{i}` loop、mechanism/hopper 都从 A fork）；B 是手写 `wheel_0/wheel_1`。
- **5 个 variant 各改一根轴**：`hopper_conical`（③ 换 LatheGeometry 圆锥漏斗 + 圆 chute）、`frame_caster`（wheels N 2→3 加前脚轮）、`handle_fold`（推把拆成 REVOLUTE `handle` part）、`mech_dropbar`（spinner→drop bar + `agitator` continuous + `drop_hole_{i}` N=8）、`spinner_vanes6`（vane loop range(3)→range(6)）。
- 统一坐标系决定：所有 origin 的 hopper/frame/chute 都是同一 grounded 主体的**不动**几何（B 的 `frame_to_hopper` FIXED 正是 Rule 1 反例）→ 模板把 hopper+chassis+chute+static-mech-hardware 全部 fuse 进单一 root part `spreader`，只有真正会动的 wheel/spinner(agitator)/lever/gate/(folding handle) 拆成 child part。采用 A 的坐标系（throat≈z0.36、axle z0.18、spinner below throat）作为唯一基准，chassis/hopper/mechanism 只换 root 上的 visual 组 + child part。

## 核心身份

Broadcast/drop 种子（化肥）撒播机：一个开口 **hopper（料斗）** 装种子，底部 **flow gate（滑动闸门，PRISMATIC）** 经 chute 计量下料，再由 **rotary broadcast spinner（旋转撒盘 + N 片放射叶，CONTINUOUS）** 甩出（或 **drop bar** 直落式 + 内置 `agitator` 搅拌杆）；靠 **ground wheels（CONTINUOUS 滚轮）** 行走，人推 T 把或车拖挂杆牵引。身份 = hopper（料斗）+ broadcast 撒播机构，非独轮车/手推车（不能读成 wheelbarrow：核心是料斗顶开口 + 底部计量 + 撒盘，不是载物斗）。默认成熟域 = 带轮底盘的园艺/农用撒播机；排除无轮的手摇肩挂式与大型农机摆管式。

## 槽位 + 候选模块表

### Slot A：hopper_form（③ Primary Form Family，form_subtype=Volumetric Envelope Form）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `square_taper` | forked_anchor | origin A `..._155130` | L51-L90 (`_rect_shell_mesh`) + L166-L180 rings | eligible if compatible | MeshGeometry：rounded-rect 方口 tub 分 4 段下收到方 throat；hollow 内外壁；3 rounded-rect tube rings。方形 XY 截面。 |
| `rounded_square` | forked_anchor | origin B `..._034216` | L69-L115 (`_hopper_shell_mesh`) + L233-L242 rolled rim | eligible if compatible | MeshGeometry：更大 rounded-square 三段包络（0.40→1.05 top），厚 rolled top rim（closed tube spline）。圆角方 XY 截面、包络更方阔。 |
| `round_conical` | forked_anchor | `rec_spreader_var_hopper_conical` | L53-L84 (`LatheGeometry.from_shell_profiles`) + L150-L167 torus rings | eligible if compatible | LatheGeometry 旋转壳：圆 top rim → 中央锥 throat；3 TorusGeometry 圆环。圆形 XY 截面（旋转体母线）。**禁止降级为 Cylinder**（Rule 3）。 |

三者 part tree/interface 不变（都是 root `spreader` 上的 hopper visual 组 + throat 在 z≈0.36），只换 Planar Boundary（方/圆角方/圆）+ Volumetric Envelope（旋转母线）离散原型 → 合法 ③ candidate（≥3）。

### Slot B：chassis / propulsion（① skeleton + ② joint）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `push_fixed_handle` | forked_anchor | origin A `..._155130` | L197-L264 (frame tubes + gearbox + T-handle group) | eligible if compatible | 直钢管架 + gearbox + T 把（stem/handlebar/2 grip/bracket）**全熔进 root**（不动→非 part，Rule 1）；小白轮。无额外 joint。 |
| `push_folding_handle` | forked_anchor | `rec_spreader_var_handle_fold` | L236-L253 mount arms + L258-L302 `handle` part + L411-L419 REVOLUTE | eligible if compatible | 同直钢管架，但 T 把拆成 `handle` child part，`spreader_to_handle` REVOLUTE 折叠 pivot（frame base 有 mount arms + pivot pin stub）。+1 revolute。 |
| `tow_drawbar` | forked_anchor | origin B `..._034216` | L177-L228 (red tube frame + drawbar tongue + hitch clevis) | eligible if compatible | 红钢管三角架 + 前牵引杆 tongue + hitch clevis + cross braces（全熔进 root，Rule 1）；无 T 把；大 turf 轮（tire r 更大）。无额外 joint。 |

`push_fixed`↔`push_folding` 差 ①（把手是否成为会动 part）；`tow` 差 ① 骨架（架型）+ ⑤（轮径）。3 candidate。

### Slot C：mechanism（② joint + ① skeleton）

| module_name | source_type | source evidence | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|---|
| `broadcast_spinner` | forked_anchor | origin B `..._034216` (disc+vanes) + `rec_spreader_var_spinner_vanes6` | B L263-L275 (`spinner_disc`+`vertical_spinner_shaft`+`low_radial_spreader_vane_{i}`×3+`spinner_hub`)；vanes6 L263-L275 range(6) | eligible if compatible | `spinner` child part：Cylinder disc + shaft + hub + N 片放射 vane（inline visual，随盘转）；`spreader_to_spinner` CONTINUOUS 轴 z。root 侧有 bearing_arm + bearing_ring。 |
| `drop_bar` | forked_anchor | `rec_spreader_var_mech_dropbar` | L291-L337 drop bar/holes（root visuals）+ L423-L458 `agitator` part + L315-L326 `drop_hole_{i}` loop | eligible if compatible | root 上 full-width drop bar body + endcaps + brackets + `drop_hole_{i}`×N（inline）；`agitator` child part（rod + paddles + journals），`spreader_to_agitator` CONTINUOUS 轴 x。无 broadcast disc。 |

**降级说明（2 candidate）**：5 星池里 mechanism 只有 rotary_broadcast_spinner（A、B 两 origin）与 drop_bar（`mech_dropbar` 1 variant）两个结构族，无第三个 source-backed 机构；不为凑数发明结构（DESIGN_RULES：来源不足降到 2 并说明理由）。两者 ② joint 轴不同（spinner z vs agitator x）、① 骨架不同（disc+vanes vs bar+holes+agitator）、身份都忠实。

## 槽位图（slot graph）

pattern: mixed（parallel_children off one grounded root + multiplicity）

```
                 [root part: spreader]
   hopper_form(A visuals) + chassis(B visuals) + chute/gate-rail + static-mech-hardware
        |                 |                 |                 |                    |
  CONTINUOUS x       CONTINUOUS z/x     PRISMATIC -y      REVOLUTE x         REVOLUTE x (folding only)
  (axle)             (bearing/bar)      (throat)          (lever bracket)    (handle pivot)
        v                 v                 v                 v                    v
  wheel_{i}×N        spinner | agitator   flow_gate       control_lever         handle
  (+caster_wheel      (mechanism child)
   when N=3)
```

接口点位：
- **spreader → wheel_{i}**：CONTINUOUS 轴 x，origin 在 `wheel_axle`(z0.180, x±)；captured-pin（bearing_sleeve↔wheel_axle）→ 无 MatingContract，grandfather + element-scoped allow_overlap。
- **spreader → caster_wheel**（wheel N=3，仅 push chassis）：CONTINUOUS 轴 x，origin 在 `caster_axle`；captured-pin grandfather。
- **spreader → spinner**：CONTINUOUS 轴 z，origin 在 spinner 对称中心线（bearing_ring 处）；shaft↔bearing_ring captured → grandfather。
- **spreader → agitator**：CONTINUOUS 轴 x，origin 在 drop_bar_body 中心；rod↔drop_bar_body captured → grandfather。
- **spreader → control_lever**：REVOLUTE 轴 x，origin 在 chassis 提供的 `lever_mount_bracket`（真实 visual）上；pin pivot → grandfather。
- **spreader → flow_gate**：PRISMATIC 轴 -y，origin 在 throat 下（prismatic origin 是 gauge freedom，免 origin-far）；slide_plate↔chute captured slot → grandfather。
- **spreader → handle**（push_folding only）：REVOLUTE 轴 x，origin 在 `handle_pivot_pin`；stem base captured → grandfather。

互斥/派生：caster（wheel N=3）仅在 push chassis 合法（tow 前端是挂钩）；vane_count 仅 broadcast_spinner 有效；drop_hole_count 仅 drop_bar 有效；lever_mount_bracket 位置由 chassis 派生。

## 每槽位 Module Emits / Interfaces

### Slot A / hopper_form（所有 candidate）
| emits | 描述 | 来源 |
|---|---|---|
| parts | root `spreader` 上的 hopper visual 组（shell mesh + rings + brand decal）| A L161-L195 / B L230-L249 / conical L145-L182 |
| internal joints | 无（hopper 不动）| — |
| upstream interface | root，无（grounded）| — |
| downstream interface | throat 顶面 z≈throat_z（chute/gate/mechanism 都锚在此下）| A L118-L141 chute |

### Slot B / chassis（所有 candidate）
| emits | 描述 | 来源 |
|---|---|---|
| parts | root 上 frame/axle/handle-or-drawbar visuals；push_folding 额外 `handle` child part | A L197-L264 / handle_fold L258-L302 / B L177-L228 |
| internal joints | push_folding：`spreader_to_handle` REVOLUTE 轴 x [0,2.2]；其余无 | handle_fold L411-L419 |
| upstream interface | root（挂到 `wheel_axle` z0.180 + hopper 下体）| A L198-L235 |
| downstream interface | `lever_mount_bracket`（lever pivot 派生位置）| A L259-L264 / B L224 |

### Slot C / broadcast_spinner
| emits | 描述 | 来源 |
|---|---|---|
| parts | `spinner` child（disc + shaft + hub + `low_radial_spreader_vane_{i}`×N inline）；root 上 bearing_arm+bearing_ring | B L263-L275 / A L285-L296 |
| internal joints | `spreader_to_spinner` CONTINUOUS 轴 z | A L402-L410 |
| upstream interface | root throat 下 spinner origin (0,-0.170,0.270) | A L407 |
| downstream interface | 无（叶片是终端）| — |

### Slot C / drop_bar
| emits | 描述 | 来源 |
|---|---|---|
| parts | root 上 drop bar body/endcaps/brackets + `drop_hole_{i}`×N inline；`agitator` child（rod + paddles + journals）| dropbar L291-L337 / L423-L458 |
| internal joints | `spreader_to_agitator` CONTINUOUS 轴 x | dropbar L450-L458 |
| upstream interface | root drop_bar_body 中心 (0,-0.04,0.24) | dropbar L455 |
| downstream interface | 无 | — |

### 通用 child parts（lever / gate）
| emits | 描述 | 来源 |
|---|---|---|
| control_lever | lever_arm Cylinder + fluted `lever_knob`（KnobGeometry）；REVOLUTE 轴 x | A L412-L443 |
| flow_gate | `slide_plate` Box；PRISMATIC 轴 -y [0,gate_travel] | A L445-L460 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| hopper_form | enum | square_taper / rounded_square / round_conical | — | choice | deterministic sampler | Slot A |
| chassis | enum | push_fixed_handle / push_folding_handle / tow_drawbar | — | choice | deterministic sampler | Slot B |
| mechanism | enum | broadcast_spinner / drop_bar | — | choice | deterministic sampler | Slot C |
| wheel_count | int | 2 / 3 | 2 | conditional | N=3(caster) 仅 push chassis；tow→2 | frame_caster |
| vane_count | int | 3 / 4 / 6 | 4 | conditional | 仅 broadcast_spinner 有效 | B / vanes6 |
| drop_hole_count | int | 6 / 8 / 10 | 8 | conditional | 仅 drop_bar 有效 | dropbar |
| palette_style | enum | 5 档（见 §8.5 ⑥）| black_poly_black_frame | choice | rng.choice(PALETTE_STYLES) | ⑥ |
| hopper_width_scale | float | [0.92, 1.10] | 1.0 | independent | clamp | ⑤ |
| hopper_height_scale | float | [0.92, 1.10] | 1.0 | independent | clamp | ⑤ |
| wheel_radius_scale | float | [0.90, 1.10] | 1.0 | independent | clamp；tow 基准更大 | ⑤ |
| gate_travel_scale | float | [0.85, 1.12] | 1.0 | independent | clamp | ⑤ |
| vane_length_scale | float | [0.90, 1.10] | 1.0 | independent | clamp | ⑤ |
| (—) | constraint | — | — | inequality | vane 半展 `hub_r + vane_len ≤ chute_out_half + spinner_disc_r`（叶不超盘沿太多，避免扫到 chute/frame）；违反回缩 vane_length_scale | 接口/clearance |
| (—) | constraint | — | — | inequality | throat_z 由 hopper_height_scale 派生，spinner/agitator/gate origin 全部随 throat_z 平移（single-sourced），避免 chute↔spinner gap 破裂 | Contract 3c |

连续采样契约：先采 independent 主尺度 → 由 throat_z 派生 mechanism/gate origin → inequality 回缩 vane 展长 → conditional（wheel/vane/drop_hole N 依 chassis/mechanism）在采样前解析。

## 7.5 编译预算 / compile budget
自报 **≤20s/seed**（重 mesh 雕刻类：hopper shell/loft/lathe + 2-3 个共享 TireGeometry+WheelGeometry 轮 mesh + tube_from_spline_points 框架）。分档 tessellation：tube radial_segments ≤14-18、rounded_rect corner_segments ≤8、LatheGeometry segments ≤36、TorusGeometry ≤36。**N 个轮复用同一 tire_mesh/rim_mesh**（origin A 做法）；spinner vane / drop hole 是廉价 Box/Cylinder。sweep `--compile-timeout 120`（3× 预算，watchdog）。

## Multiplicity / Copy Logic

三根独立复制轴：

- **vane_count（broadcast_spinner）**：`count_param=vane_count`，N_range 产品域 {3,4,6}（测试全覆盖）；sampling domain 加权 {3:0.34, 4:0.33, 6:0.33}。copied object=`low_radial_spreader_vane_{i}`（inline visual on `spinner` part，等角 `2π/N`，共享 geometry helper，FIXED 语义=随盘 continuous 转，非独立 joint→Rule 1 inline）；仅 mechanism=broadcast_spinner 时激活；source=B(3)/vanes6(6)/A(4)。encode `("vane_count", f"n{N}")`。
- **wheel_count**：`count_param=wheel_count`，N_range {2,3}；2=两驱动轮 loop `wheel_{i}`；3=额外前中 `caster_wheel`（独立 CONTINUOUS child part + caster fork visuals on root）。gating：N=3 仅 push chassis（tow 强制 2）。source=A(2)/frame_caster(3)。encode `("wheel_count", f"n{N}")`。
- **drop_hole_count（drop_bar）**：`count_param=drop_hole_count`，N_range {6,8,10}；copied=`drop_hole_{i}`（inline Cylinder on root，沿 bar 底等距）；仅 mechanism=drop_bar 时激活；source=dropbar(8)。encode `("drop_hole_count", f"n{N}")`。

驱动轮始终 `wheel_{i}` loop（共享 tire/rim mesh，统一 `spreader_to_wheel_{i}` CONTINUOUS）。

## 视觉多样性 6 轴考察

| 轴 | 怎么判断 | 有/无 | 取值/范围 + source_type / 来源 · 或理由 |
|---|---|---|---|
| ① 骨架图 | 加/减会动 part 或边 | 有 | chassis push_fixed(0 extra)/push_folding(+handle revolute)/tow；mechanism spinner(spinner part)/drop_bar(agitator part)；wheels 2 vs 3(+caster part)。全 forked_anchor（A/B/handle_fold/frame_caster/dropbar）。 |
| └ multiplicity | 同构件 ×N | 有 | vanes N{3,4,6}、wheels N{2,3}、drop-hole N{6,8,10}（见 §8）；小 N 权重档，N 只覆盖不计数。 |
| ② 关节类型 | 边换 type/轴 | 有 | CONTINUOUS（wheels x / spinner z / agitator x / caster x）、REVOLUTE（lever x / folding handle x）、PRISMATIC（gate -y）。全 source-backed；每种类型在 sweep 都出现。 |
| ③ 主体形态家族 | 换核心 part 几何原型 | 有 | hopper_form 3 原型（square_taper / rounded_square / round_conical），form_subtype=Volumetric Envelope Form（方/圆角方/圆旋转母线）；source-backed A/B/conical，登记进 slot_choices。 |
| ④ 表面装饰 | 表面叠加细节 | 有 | brand decal block + label_line{0-2}（raised Box，host-conformal 贴 hopper 前壁，随 ③ 面 z 派生）；rolled rims / seam ribs / reinforcing rings。record_only（A L182-L195 / B L247-L249）+ host-conformal world_knowledge。 |
| ⑤ 尺寸/行程 | 只连续改尺寸/行程 | 有 | hopper_width/height_scale [0.92,1.10]、wheel_radius_scale [0.90,1.10]、vane_length_scale [0.90,1.10]；gate PRISMATIC [0, ~0.13·travel_scale] 轴 -y、lever REVOLUTE [0,0.65]、folding handle REVOLUTE [0,2.2]。motion_test_plan：跑 sampled collision；targeted pose 覆盖 gate open / lever pivot / spinner|agitator spin(±90/180) / handle fold。 |
| ⑥ 涂装 | 只改材质/颜色 | 有 | 5 档（≥3，target 4-6）：`black_poly_red_frame` / `black_poly_green_frame` / `black_poly_black_frame` / `grey_poly_yellow_frame` / `galvanized`。材质大类 plastic(hopper)+painted/metal(frame)+rubber(tire)+metal(hub/hardware) 覆盖 ≥ ceil(0.5×5)=3。record_only（A/B 配色）。 |

收尾自检目标：batch 0-9 肉眼看到 3 种 hopper 形态、5 种涂装、folding handle 折叠、caster 第三轮、spinner N 叶 / drop bar N 孔切换、关节全程不穿模。

## 拓扑多样性审计

总组合数：hopper_form(3) × chassis(3) × mechanism(2) = 18 结构组合；× wheel N(2) × vane N(3, spinner) / drop_hole N(3, dropbar) → 采样上 ~18×(2..)×(3) ≈ 100+ 有效 seed 组合。


seed_domain_policy：procedural_first（seed=0 不特殊，`config_from_seed` 全程 rng）。
Procedural Sampling / Sweep Plan：每 seed 独立 `rng.choice` 各 slot + 加权 `rng.choices` 各 N；compatibility gating 在 `resolve_config`：wheel N=3→仅 push（tow 降 2）、vane_count 仅 spinner、drop_hole 仅 dropbar、lever_mount 位置派 chassis。无 regression override。random sweep 0-35 初轮，corner stage 补极值/未采组合。Topology target：1000-seed distinct 预计 按 ≥300 report-only 口径观察（18 结构×N 组合）。
Controlled local parameterization：hopper_width/height_scale、wheel_radius_scale、gate_travel_scale、vane_length_scale，全部 `resolve_config` clamp/派生；throat_z 单源派生 mechanism/gate origin（Contract 3c）；vane 展长受 inequality 回缩；不破坏 captured-pin allow_overlap 与 multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | slot 顺序 hopper→chassis→mechanism→N；weighted N；compatibility gates in resolve_config | slot_choices_for_seed == build choices |
| compatibility matrix | caster↔push only；vane↔spinner；hole↔dropbar；lever_mount↔chassis | no floating（swapped hopper↔frame seam）、collision（vane sweep）、caster on tow illegal blocked |
| controlled local variation | 5 连续 scale + clamp/derived | proportions vary，throat/spinner gap、gate travel、vane clearance 不破 |
| regression overrides | none | — |
| random sweep | seeds 0-35 初轮，0-999 成熟审计 | contract failures；axis_realization |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| hopper_form | 3 | yes | yes | |
| chassis | 3 | yes | yes | |
| mechanism | 2 | yes | no | 5 星池仅 2 机构族，降级说明见 Slot C |

## Validator
- slot_choices_for_seed 返回已实现 module 名（+ 各 multiplicity N 编码）
- config_from_seed 对所有 seed（含 0）用 deterministic procedural sampling
- compatibility gating 阻止 caster-on-tow / vane-on-dropbar / hole-on-spinner 非法组合
- 无 regression override 轮换小表
- 连续 scale 全 clamp；throat_z 派生 mechanism/gate origin（跨部件依赖在 resolve_config 解）
- 关键关节 type/轴：wheels CONTINUOUS x、spinner CONTINUOUS z、agitator CONTINUOUS x、lever REVOLUTE x、gate PRISMATIC -y、folding handle REVOLUTE x
- copied objects 命名 `wheel_{i}` / `low_radial_spreader_vane_{i}` / `drop_hole_{i}`，等距/等角，统一 joint policy
- captured-pin joints 无 MatingContract（grandfather）+ element-scoped allow_overlap，全 source-backed

## Reject cases
- swapped hopper（尤其 round_conical）不贴 frame/chute → root part 出现 disconnected island（compile-sweep 硬 fail）
- vane_length 过大 → 旋转全程 vane 扫到 chute_tray / frame（sampled-pose collision）
- caster 挂到 tow chassis（前端已是 hitch）→ 非法组合/穿模
- spinner↔throat gap 破裂（throat_z 派生漏改）→ chute feeds-above 断裂或 spinner 撞 hopper
- 把 vane / drop_hole 做成 FIXED-joint 独立 part（应 inline visual，Rule 1）
- 把 LatheGeometry 圆锥 hopper 降级为 Cylinder（Rule 3）
- 单色（palette_style 未驱动全部 `.visual(material=...)`）→ monochrome
- folding handle 折叠时 lever/cable 悬空（lever 锚在 frame stub 而非折叠件）

## 与相邻类别的边界
- 不该混入：Wheelbarrow / 独轮手推车（理由：撒播机身份=顶开口料斗+底部计量闸+撒盘/落料，非载物斗；即便 hopper 方阔也有 broadcast/drop 机构与 chute）。
- 不该混入：手摇肩挂式 handheld spreader（理由：无轮底盘、近类目边界，不可从任一 origin fork）。
- 不该混入：大型农机摆管式 broadcaster（理由：类目漂移，非园艺/农用带轮撒播机）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 双 origin 满 chassis；mechanism 2-candidate 已说明降级理由；统一坐标系 fuse 不动件进 root（Rule 1）；captured-pin 全 grandfather。 |

## 模板实现备注（可选）
- 共享 helper：`_tube_mesh`(tube_from_spline_points)、`_rect_shell_mesh`/`_hopper_shell_mesh`/`_conical_hopper_mesh`、`_wheel_meshes`（tire+rim 复用）、`_emit_vanes`、`_emit_drop_holes`。
- throat_z、spinner_origin、gate_origin、lever_pivot 全部由 `Resolved...Config` 单源字段派生（Contract 3c）。
- captured-pin overlap 全 element-scoped allow_overlap（wheel bearing↔axle、spinner shaft↔bearing_ring、agitator rod/paddle↔drop_bar_body、handle stem↔pivot pin/mount arm、gate slide_plate↔chute）。
- 连接性保险：所有 hopper form 都在 throat 加 `throat_collar` 桥接 hopper↔chute↔frame，避免 swapped hopper island。
