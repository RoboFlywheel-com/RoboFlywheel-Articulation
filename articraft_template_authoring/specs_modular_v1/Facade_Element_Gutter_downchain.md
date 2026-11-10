# Modular Spec - rain_chain

## 元信息
| 项 | 值 |
|---|---|
| slug | `rain_chain` |
| 大类 / 小类 | `Facade Element` / `Gutter downchain` (rain chains / kusari-doi) |
| source map | `<ARTI_SKILL_ROOT>/articraft_data/picture_expansion/template_source_maps/Facade_Element__Gutter_downchain.md` |
| parent A (round-cup, PRIMARY) | `rec_build-a-realistic-articulated-3d-model-of-a-gutt_20260609_185904_296819_efa584a4` -> `picture/Facade Element/Gutter downchain/001.png` |
| parent B (square-funnel) | `rec_build-a-realistic-articulated-3d-model-of-a-gutt_20260609_185907_280318_3dcec91a` -> `picture/Facade Element/Gutter downchain/002.png` |
| template path | `agent/templates/Facade_Element_Gutter_downchain.py` |
| test path (optional) | `tests/agent/test_rain_chain_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `multiplicity` |

`multiplicity`：这是一个**近纯线性链 / 多重复制**物体。核心结构是一个固定的 gutter 根挂件 (Slot A)，下面悬挂 **N 个同构 hanging module** (Slot B 决定模块形状)，相邻模块之间用一个 REVOLUTE `swing_{i}` joint 串成钟摆链 (Slot C 决定耦合/摆动策略)。模板的主多样性来自 **`cup_count` / `link_count` 这根 multiplicity 轴**（N 个 `cup_{i}` 或 `link_{i}` 复制 + 每模块一个 `swing_{i}` REVOLUTE joint），slot 选择叠加在其上。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 6 |
| read_count | 6 |
| read_scope | all 5-star samples in this 小类: 2 parents + 4 converged variants; read `model.py` + `prompt.txt` for each |
| source_index_policy | only adopted module sources are indexed below (§14) |

读取的 6 个 5 星样本（全部已读 model.py）：

| record_id | 角色 | root | hanging module | 链接耦合 | swing axis | N | palette |
|---|---|---|---|---|---|---|---|
| `...efa584a4` (parent A, 001.png) | round-cup PRIMARY | `gutter_bracket` (flange+spout+lug+`bracket_eye` torus) | `cup_{i}`: LatheGeometry funnel `cup_shell` + torus `cup_rim` + `link_wire` bail + `bottom_boss`/`bottom_stem`/`bottom_eye` | bail hook 穿过上一模块的 `bottom_eye` (or `bracket_eye`); pivot 链经 `parent_pivot_z` 下传 | (0,1,0) Y | 5 | zinc green-grey + bright rim |
| `...3dcec91a` (parent B, 002.png) | square-funnel | `gutter_hanger` V-wire `hanger_wire` + apex bar | `cup_{i}`: cadquery 方锥 loft `shell` (drain hole + 底部 hanger bar) + `rim` 方唇 + `bail` 竖环 | bail 竖环 captured over 上一模块底部的 hanger bar (axle); CUP_DROP 间距 | (0,1,0) Y | 5 | galvanized grey |
| `rec_gutter_downchain_var_cup_count_3` | A 家族 N=3 | 同 parent A | 同 parent A (`cup_{i}`) | 同 parent A | (0,1,0) Y | 3 | 同 parent A |
| `rec_gutter_downchain_var_cup_count_8` | A 家族 N=8 | 同 parent A | 同 parent A (`cup_{i}`) | 同 parent A | (0,1,0) Y | 8 | 同 parent A |
| `rec_gutter_downchain_var_lotus_cups` | A 家族 lotus shape | 同 parent A | `cup_{i}`: lotus-flared `cup_shell` + scalloped MeshGeometry `cup_rim` (N_PETALS=8) | 同 parent A (bail seats on valley ring) | (0,1,0) Y | 5 | 同 parent A |
| `rec_gutter_downchain_var_round_cups` | B 家族 round bowl shape | 同 parent B (`gutter_hanger`) | `cup_{i}`: cadquery 圆碗 power-curve loft `shell` (drain+bar) + 圆 `rim` + `bail` | 同 parent B (captured loop over bar) | (0,1,0) Y | 5 | 同 parent B |

读取后的真实结构变化轴（去掉纯尺寸/颜色差异后）：

| 轴 | 观察到的真实结构变体 |
|---|---|
| root / hanger | (1) 短 outlet spout + collar + 水平挂耳 + 竖直 eye torus（A 家族 `gutter_bracket`）；(2) V 形挂钩 wire + 顶 apex axle bar（B 家族 `gutter_hanger`）；(3) spout + 水平 `bracket_ring` torus + 4 根 spoke（link_chain 家族） |
| hanging module shape | 圆锥 funnel cup / 方锥 funnel cup / lotus 花瓣 cup（flared shell + scalloped rim）/ oval chain link（无 cup 主体，纯椭圆环） |
| link coupling / swing policy | (1) bail-hook-through-eye 单 Y 轴钟摆（A）；(2) captured-loop-over-bar 单 Y 轴钟摆（B）；(3) interlocked oval links 交替 XZ/YZ 平面、交替 Y/X 摆轴（link_chain） |
| multiplicity N | `cup_count` ∈ {3,5,8} 已采样；link_chain 用 `link_count`=8；product 域扩展为 3–50，sweep 仅覆盖 3–10 |

## 核心身份

`rain_chain`（雨链 / kusari-doi）是装饰性落水管替代物：固定在 gutter outlet 下方的根挂件，垂直悬挂一串可见的同构金属 hanging module（杯 / 漏斗 / 花瓣杯 / 椭圆环），把雨水沿可见路径引到地面。它是一个**接地的钟摆式线性链**：根不动，每个模块通过一个 REVOLUTE `swing_{i}` joint 像钟摆一样绕一条水平轴摆动，摆动上游模块会带动下游整条链。

默认成熟域：product 域 3–50 个 hanging module 的竖直雨链，root 是 gutter 挂件，模块是杯型 funnel / lotus / 椭圆链环。模板把 N（`cup_count` / `link_count`）作为受控 multiplicity 轴；模板验收 sweep 只要求覆盖 N=3–10，N=11–50 属同一复制链逻辑外推。

**不该混入的东西**：实心落水管 / 雨水桶 / 排水沟槽（rain_chain 是开放可见的悬挂链，不是封闭管道）；项链 / 链条首饰（尺度、root 语义、悬挂用途不同）；风铃 / 串珠风格挂饰（这些不是 gutter 落水功能）；铰链臂 / 机械串联臂（rain_chain 是被动重力钟摆，不是驱动关节臂）。

## 槽位 + 候选模块表

### Slot A：root_hanger（固定根挂件，链条 ROOT）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| eye_bracket | rec_...efa584a4 (parent A) | L153-L185 | eligible if compatible | `gutter_bracket`: collar flange (Cylinder) + 短 outlet spout (Cylinder) + 水平 hanger lug (Box) + 竖直 `bracket_eye` torus loop；下游接口 = `bracket_eye` 处一个悬挂 eye，供首模块 bail hook 穿过 |
| vee_wire_hanger | rec_...3dcec91a (parent B) | L173-L211, L225-L230 | eligible if compatible | `gutter_hanger`: V 形 wire（两端 hook 卷过 gutter lip，dip 到低 apex）+ apex 处 Y 向 axle bar；下游接口 = apex bar，供首模块 bail 竖环 captured 套在上面 |
| ring_bracket | rec_gutter_downchain_var_link_chain | L113-L175 | eligible if compatible | `gutter_bracket`: flange + spout + 竖直 `hanger_bar` + 水平 `bracket_ring` torus (XY 平面) + 4 根 `ring_spoke_{j}`；下游接口 = 水平 ring，供首 oval link 穿过 |

三个 root 都有结构差异（eye torus vs V-wire+axle vs 水平 ring+spokes），且每个对应一类下游悬挂接口（eye / axle bar / horizontal ring）。

### Slot B：hanging_module（同构悬挂模块形状，被 multiplicity 轴复制 N 次）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| round_funnel_cup | rec_...efa584a4 (parent A) | L84-L138, L197-L274 | eligible if compatible | `cup_{i}`: LatheGeometry 圆锥 funnel `cup_shell`（宽口朝上、窄底朝下、薄壁 hollow）+ torus `cup_rim` + `link_wire` bail（两脚坐 rim 边、apex 在轴上）+ `bottom_boss`/`bottom_stem`/`bottom_eye`（底部封口 + 下挂 eye） |
| square_funnel_cup | rec_...3dcec91a (parent B) | L76-L170, L238-L265 | eligible if compatible | `cup_{i}`: cadquery 方锥 loft + shell `shell`（方口 funnel、底部 drain hole + Y 向 hanger bar）+ 方 lip `rim` + `bail` 竖环；hollow 方杯 |
| lotus_petal_cup | rec_gutter_downchain_var_lotus_cups | L96-L176, L271-L348 | eligible if compatible | `cup_{i}`: lotus-flared LatheGeometry `cup_shell`（上半向外 flare）+ scalloped MeshGeometry `cup_rim`（N_PETALS=8 花瓣 tip/valley 交替）+ bail（坐在 valley ring）+ 同 A 的 boss/stem/eye |
| oval_chain_link | rec_gutter_downchain_var_link_chain | L67-L97, L184-L201 | eligible if compatible | `link_{i}`: 纯椭圆 `oval_body`（tube_from_spline_points 闭合椭圆环，无 cup 主体）；相邻 link 交替 XZ/YZ 平面；这是唯一的 link-only（无杯）拓扑 |

### Slot C：coupling_swing_policy（相邻模块的耦合方式 + swing joint 策略）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| bail_eye_single_axis | rec_...efa584a4 (parent A) | L240-L274 | eligible if compatible | 每模块底部 `bottom_eye` torus 充当下一模块的 pivot；下一模块 `link_wire` bail hook 穿过它；`swing_{i}` REVOLUTE 单轴 (0,1,0) Y，limits ±35°；pivot z 经 `parent_pivot_z = BOT_EYE_Z` 下传 |
| captured_loop_over_bar_single_axis | rec_...3dcec91a (parent B) | L107-L119, L244-L265 | eligible if compatible | 每模块底部一根 Y 向 hanger bar（在 shell drain 上方）充当 axle；下一模块的竖直 `bail` 环 captured 套在 bar 上；`swing_{i}` REVOLUTE 单轴 (0,1,0) Y，limits ±0.7 rad；间距 CUP_DROP = CUP_H+BAIL_RISE-0.003 |
| interlocked_link_alternating_axis | rec_gutter_downchain_var_link_chain | L184-L226 | eligible if compatible | 相邻 oval link 互穿；奇/偶 link 交替 XZ/YZ 平面，`swing_{i}` 摆轴随之在 Y / X 之间交替（even→(0,1,0)，odd→(1,0,0)），limits ±35°；pivot z 经 `BOTTOM_PIVOT_Z` 下传；这是唯一带交替-轴拓扑的耦合策略 |

## 槽位图（slot graph）

pattern: multiplicity（核心是 root + N 个同构悬挂模块的线性钟摆链）

```
[Slot A root_hanger]  (ROOT, fixed)
   -- swing_1 REVOLUTE (axis from Slot C) at root downstream pivot -->
[Slot B hanging_module instance #1]
   -- swing_2 REVOLUTE (axis from Slot C) at module#1 bottom pivot -->
[Slot B hanging_module instance #2]
   -- swing_3 ... -->
   ...
   -- swing_N REVOLUTE -->
[Slot B hanging_module instance #N]   (bottom of chain)
```

说明：

- **slot 顺序 / parent 关系**：Slot A 是 grounded ROOT；Slot B 的 N 个实例串成一条 serial 链，`swing_{i}` 的 parent 是上一模块（或 root），child 是当前模块。Slot C 不是独立 part，而是**决定相邻模块如何耦合 + 每个 `swing_{i}` 的 axis / origin / range 的策略层**。
- **每条跨 slot 连接的接口点位**：
  - root → module#1：Slot A 下游 pivot（eye torus 中心 / V-apex axle bar / 水平 ring 中心），其 z 即首 joint origin 的 `parent_pivot_z`（A: `BRACKET_EYE_Z`；B: `-(BAIL_RISE-0.003)`；ring: `BRACKET_RING_Z`）。
  - module#i → module#{i+1}：上一模块底部的悬挂接口（A: `bottom_eye` at `BOT_EYE_Z`；B: 底部 hanger bar at `-CUP_H+...`；link: oval 底弧 at `BOTTOM_PIVOT_Z`），其 z 作为下一 `swing` 的 `parent_pivot_z`。
- **跨 slot joint type / axis / range**：全部 `ArticulationType.REVOLUTE`。Slot C 决定 axis：`bail_eye` / `captured_loop` → 全部 (0,1,0) Y 单轴；`interlocked_link` → even (0,1,0) / odd (1,0,0) 交替。range 由 Slot C 给（±35° 或 ±0.7 rad）。
- **互斥 / 派生关系（compatibility）**：
  - `oval_chain_link` (Slot B) 与 `interlocked_link_alternating_axis` (Slot C) **强绑定**：oval link 必须用交替-轴互穿耦合（这是它的真实拓扑）；且 root 需用 `ring_bracket`（水平 ring 让首 oval link 穿过）。
  - `square_funnel_cup` + `round_funnel_cup(B 家族 cadquery 版)` 与 `captured_loop_over_bar_single_axis` + `vee_wire_hanger` 绑定（B 家族：drain+bar+竖环 + V 挂钩）。
  - `round_funnel_cup(A 家族 lathe 版)` + `lotus_petal_cup` 与 `bail_eye_single_axis` + `eye_bracket` 绑定（A 家族：eye torus + bail-through-eye）。
  - 见 §9 compatibility matrix（这是一个**家族锁**：root×module×coupling 三者按家族联动，而不是自由三元笛卡尔）。

## 每槽位 Module Emits / Interfaces

### Slot A / module eye_bracket
| emits | 描述 | 来源 |
|---|---|---|
| parts | `gutter_bracket`（单 root part，多 visual）：`bracket_flange`, `outlet_spout`, `hanger_lug`, `bracket_eye` (torus mesh) | S-A1 / L153-L185 |
| internal joints | 无（root 固定） | S-A1 |
| upstream interface | 顶部 collar flange，名义上 bolt 到 gutter outlet 孔；root 接地 | S-A1 / L157-L162 |
| downstream interface | `bracket_eye` 竖直 eye loop，z=`BRACKET_EYE_Z`(=-GUTTER_LEN-0.010)，供首模块 bail hook 穿过 → 首 `swing` origin | S-A1 / L177-L181, L195 |

### Slot A / module vee_wire_hanger
| emits | 描述 | 来源 |
|---|---|---|
| parts | `gutter_hanger`（单 root part）：`hanger_wire`（V 形 spline wire + Y 向 apex axle bar，merge 成一个 mesh） | S-A2 / L173-L211, L225-L230 |
| internal joints | 无（root 固定） | S-A2 |
| upstream interface | 两端 hook 卷过 gutter lip（hook_z≈0.090） | S-A2 / L180-L189 |
| downstream interface | apex 处 Y 向 axle bar，z=0（hanger local），供首模块 bail 竖环 captured 套上 → 首 `swing` origin = `-(BAIL_RISE-0.003)` | S-A2 / L199-L210, L244-L248 |

### Slot A / module ring_bracket
| emits | 描述 | 来源 |
|---|---|---|
| parts | `gutter_bracket`：`bracket_flange`, `outlet_spout`, `hanger_bar` (竖), `bracket_ring` (XY 水平 torus), `ring_spoke_0..3` | S-A3 / L113-L175 |
| internal joints | 无（root 固定） | S-A3 |
| upstream interface | collar flange bolt 到 gutter | S-A3 / L116-L121 |
| downstream interface | 水平 `bracket_ring` (z=`BRACKET_RING_Z`=-GUTTER_LEN-0.014)，供首 oval link 穿过 → 首 `swing` origin | S-A3 / L139-L151, L182 |

### Slot B / module round_funnel_cup
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cup_{i}`（multiplicity 复制）：`cup_shell` (Lathe funnel), `cup_rim` (torus), `link_wire` (bail), `bottom_boss`, `bottom_stem`, `bottom_eye` | S-B1 / L197-L249 |
| internal joints | 无（模块内部刚性；唯一活动是上游 `swing_{i}`） | S-B1 |
| upstream interface | part-frame 原点 = 顶 pivot/hook 点（PIVOT_Z=0）；`link_wire` bail apex 在原点，hook 上一模块的 eye | S-B1 / L118-L138, L218-L222 |
| downstream interface | `bottom_eye` torus at `BOT_EYE_Z`，作为下一模块 pivot | S-B1 / L240-L245, L274 |

### Slot B / module square_funnel_cup
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cup_{i}`：`shell` (cadquery 方锥 loft, drain hole + 底 hanger bar), `rim` (方 lip), `bail` (竖环) | S-B2 / L238-L242 |
| internal joints | 无 | S-B2 |
| upstream interface | mouth-frame 顶 z=0；`bail` 竖环 apex 在 +BAIL_RISE，hook 上一模块底部 bar | S-B2 / L135-L170 |
| downstream interface | 底部 Y 向 hanger bar（shell drain 上方，z≈-CUP_H+WALL*0.5），供下一模块 `bail` 环套住 | S-B2 / L107-L119 |

### Slot B / module lotus_petal_cup
| emits | 描述 | 来源 |
|---|---|---|
| parts | `cup_{i}`：lotus-flared `cup_shell` (Lathe), scalloped `cup_rim` (MeshGeometry N_PETALS=8), `link_wire`, `bottom_boss`, `bottom_stem`, `bottom_eye` | S-B3 / L271-L319 |
| internal joints | 无 | S-B3 |
| upstream interface | part-frame 原点 = 顶 pivot；`link_wire` bail（坐 valley ring，半径 (TIP+VALLEY)/2） | S-B3 / L287-L296 |
| downstream interface | `bottom_eye` torus at `BOT_EYE_Z`，下一模块 pivot | S-B3 / L314-L319 |

### Slot B / module oval_chain_link
| emits | 描述 | 来源 |
|---|---|---|
| parts | `link_{i}`：`oval_body`（闭合椭圆 tube，无 cup 主体）；交替 XZ/YZ 平面 | S-B4 / L184-L201 |
| internal joints | 无 | S-B4 |
| upstream interface | part-frame 原点 = 顶 pivot（椭圆顶弧 z=0 处穿过上一 link 底弧） | S-B4 / L67-L97 |
| downstream interface | 椭圆底弧 at `BOTTOM_PIVOT_Z`，下一 link 在此穿过 | S-B4 / L52-L56, L225 |

### Slot C / coupling_swing_policy candidates
| module | swing joint type/axis/range | pivot 链 | 来源 |
|---|---|---|---|
| bail_eye_single_axis | REVOLUTE, axis (0,1,0) Y, ±35°, effort 1.0 | origin = parent eye z；`parent_pivot_z = BOT_EYE_Z` 下传 | S-C1 / L256-L274 |
| captured_loop_over_bar_single_axis | REVOLUTE, axis (0,1,0) Y, ±0.7 rad, effort 2.0 | 首 origin `-(BAIL_RISE-0.003)`；之后每段 `-CUP_DROP` | S-C2 / L244-L265 |
| interlocked_link_alternating_axis | REVOLUTE, even axis (0,1,0)/odd (1,0,0), ±35°, effort 0.5 | origin = parent 底弧 z；`parent_pivot_z = BOTTOM_PIVOT_Z` 下传 | S-C3 / L207-L226 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| root_hanger | enum | eye_bracket / vee_wire_hanger / ring_bracket | — | choice | deterministic procedural sampler；受 family lock gating（§9） | Slot A |
| hanging_module | enum | round_funnel_cup / square_funnel_cup / lotus_petal_cup / oval_chain_link | — | choice | sampler；受 family lock gating | Slot B |
| coupling_swing_policy | enum | bail_eye_single_axis / captured_loop_over_bar_single_axis / interlocked_link_alternating_axis | — | choice | conditional：由 hanging_module 家族派生（见 §9） | Slot C |
| cup_count / link_count | int (multiplicity) | product 域 [3,50]（cup 链 / link 链）；sweep/test 覆盖 [3,10] | 5 | conditional | 普通 seed 加权采样（小 N 偏多、11–50 长尾）；clamp 到 [3,50]；sweep overrides 只枚举 [3,10]；见 §8 | source N∈{3,5,8}；产品扩展策略 |
| cup_top_r_scale | float | [0.85, 1.18] | 1.0 | independent | 缩放 mouth 半径/half-width；clamp 保证 bail span 仍坐在 rim 上 | S-B1 L52, S-B2 L44 |
| cup_taper_scale | float | derived | 1.0 | equation | `cup_bot_r = cup_top_r * k_taper`，k_taper∈[0.30,0.48]（保持 funnel 收口，测试要求 bot<0.5*top） | S-B1 L52-L53 |
| cup_height_scale | float | [0.85, 1.20] | 1.0 | independent | 缩放 CUP_H；影响模块竖直占位 | S-B1 L54, S-B2 L46 |
| module_pitch_scale | float | derived | 1.0 | equation | `pitch_i = (CUP_H + link_drop)*module_pitch_scale`；= f(cup_height_scale)，保证相邻模块不穿插 | S-C1 L72-L74, S-C2 L66 |
| swing_limit_scale | float | [0.7, 1.15] | 1.0 | independent | 缩放 `swing_{i}` motion limits；clamp 后 rest pose q=0 必须合法，单轴 ≤ ±45°，交替轴 ≤ ±40° | S-C1 L263-L268, S-C2 L261-L263 |
| link_oval_aspect | float | [1.6, 2.6] | 2.0 | independent | oval link 长轴/短轴比（仅 oval_chain_link）；测试要求 half_len > 1.5*half_wid | S-B4 L45-L46 |
| n_petals | int | {6, 8, 10, 12} | 8 | conditional | 仅 lotus_petal_cup；测试要求 ≥6 | S-B3 L90 |
| palette_style | enum | weathered_copper / aged_verdigris_zinc / galvanized_grey / brushed_aluminium / antique_bronze / blackened_steel | — | choice | 仅颜色/材质，不改拓扑；见 §palette | all sources |
| (—) | constraint | — | — | inequality | `Σ pitch_i + module_height ≤ chain_envelope`（链总长在可视包络内）；超出按比例回缩 module_pitch_scale | 接口 / clearance |
| (—) | constraint | — | — | inequality | bail/eye 半径 vs module 半径：`eye_r + wire_r ≤ cup_top_r * 0.25`，保证 hook 能坐在 rim 边而不悬空 | S-B1 L68, S-C1 |

### palette_style colorways（≥3，目标 4–6；均来自 5 星样本观察）
| 名称 | shell / module 主体 | rim / 次色 | wire / bail | 来源观察 |
|---|---|---|---|---|
| aged_verdigris_zinc | (0.55,0.58,0.52) 风化绿锌灰 | (0.80,0.82,0.84) 亮 rim | (0.74,0.76,0.79) 钢灰 | parent A / cup_count / lotus (A 家族原色) |
| galvanized_grey | (0.66,0.68,0.70) 镀锌铝灰 | (0.55,0.57,0.59) 暗 lip | (0.60,0.62,0.64) 锌灰 wire | parent B / round_cups (B 家族原色) |
| weathered_copper | (0.62,0.41,0.26) 暖铜 | (0.48,0.32,0.22) 暗铜 | (0.50,0.52,0.54) 中性灰 bracket | link_chain (oval copper) |
| antique_bronze | (0.50,0.36,0.22) 古铜 | (0.40,0.30,0.20) 暗古铜 | (0.55,0.50,0.42) 暖灰 | link_chain copper 派生（暗化保形） |
| brushed_aluminium | (0.72,0.73,0.75) 拉丝铝 | (0.58,0.60,0.62) 暗铝 | (0.66,0.68,0.70) 铝灰 | parent B galv 提亮派生 |
| blackened_steel | (0.30,0.31,0.33) 黑化钢 | (0.45,0.46,0.48) 亮边 | (0.40,0.41,0.43) 深灰 | 中性金属派生（保持 muted 金属约束） |

注：palette 仅替换 material rgba，不改任何 part tree / joint / 尺寸。模板按 seed 选一个 colorway，全链统一上色（rim 比 shell 亮、wire 钢灰的 source 约束保持）。

## Multiplicity / Copy Logic

本类别有**一根**核心 multiplicity 轴：`cup_count` / `link_count`（cup 链与 link 链是同一根轴的两种命名，按所选 hanging_module 家族取名）。这是模板主多样性来源。

- **count_param**：`cup_count`（cup 家族：round/square/lotus）/ `link_count`（oval_chain_link 家族）。模板内部统一为一个 `module_count` 变量，按 module 家族决定命名前缀。
- **N_range**：产品域 `[3, 50]`。5 星已采样 N∈{3, 5, 8}（cup_count_3 / parent=5 / cup_count_8；link_chain=8）。**sweep/test 域只覆盖 [3, 10]**：若 N=3..10 的复制、命名、joint origin 传递、相邻 contact/allow_overlap 都通过，则 N=11..50 属同一线性链循环外推，普通 seed 可生成但不作为 sweep 必测范围。
- **copied object**：N 个同构 `cup_{i}` / `link_{i}` part（i=1..N），各自带其 §6 列出的 visual 组；外加 N 个 `swing_{i}` REVOLUTE joint。
- **naming**：cup 家族 part `cup_1..cup_N`、joint `swing_1..swing_N`（1-based，对齐 5 星源）；oval 家族 part `link_0..link_{N-1}`、joint `swing_0..swing_{N-1}`（0-based，对齐 link_chain 源）。模板需按家族保持其原命名约定（reviewer 可统一为 1-based，但默认对齐源以便回溯）。
- **placement**：每个模块的 part-frame 原点 = 该模块的顶 pivot/hook 点；模块几何全部挂在原点下方（-Z）。第 i 个 `swing` 的 origin z = 上一模块（或 root）的下游 pivot z（A: `BOT_EYE_Z`；B: `-CUP_DROP`；oval: `BOTTOM_PIVOT_Z`）。竖直间距由 `module_pitch_scale`（= f(cup_height_scale)）派生，保证相邻模块的接口贴合、不穿插、不悬空。
- **joint policy**：每个复制模块对应**恰好一个** REVOLUTE `swing_{i}`。axis 由 Slot C 决定：单轴策略全 (0,1,0) Y；`interlocked_link_alternating_axis` 按 i 奇偶在 (0,1,0)/(1,0,0) 间交替。motion limits 来自 source（±35° 或 ±0.7 rad）× `swing_limit_scale`，clamp 后必须包含 rest pose q=0。
- **source/gating**：N=3 ← `rec_gutter_downchain_var_cup_count_3` L76, L325；N=5 ← parents；N=8 ← `rec_gutter_downchain_var_cup_count_8` L76 / `rec_gutter_downchain_var_link_chain` L58。N=9..50 为同一复制循环的产品域扩展；模块内部的重复小件（rim petal tip、spoke、boss/stem）是 module-local visual/helper，**不计入** topology multiplicity。

无第二根 multiplicity 轴：`n_petals`（lotus rim 花瓣数）是 module-local 装饰密度参数，不改 part tree / joint 拓扑，不作为 multiplicity 轴。

## 拓扑多样性审计

总组合数（family-lock 合法化后）：

- 家族 α（A 系：eye_bracket × {round_funnel_cup, lotus_petal_cup} × bail_eye_single_axis）= 1×2×1 = 2 slot 形态
- 家族 β（B 系：vee_wire_hanger × {square_funnel_cup, round_funnel_cup(cadquery 圆碗)} × captured_loop_over_bar_single_axis）= 1×2×1 = 2 slot 形态
- 家族 γ（link 系：ring_bracket × oval_chain_link × interlocked_link_alternating_axis）= 1×1×1 = 1 slot 形态

→ 5 种合法的 (root, module, coupling) slot 形态。再乘 multiplicity product N∈{3..50}（48 个值）→ **5 × 48 = 240 distinct product (slot-form × N) 拓扑**；sweep 覆盖 N∈{3..10}（8 个值）→ **5 × 8 = 40 distinct sweep 拓扑**（part tree / joint count / axis 模式随 N 与家族真实变化）。oval 家族还带交替-轴拓扑差异，进一步区分于 cup 家族。


理由：N 本身改变 part tree（`cup_i`/`link_i` 个数）和 joint 个数，是真实拓扑维度；仅 sweep 域 5 种家族形态 × 8 个 N 值已远超 10。oval 家族的交替-轴模式与 cup 家族的单轴模式是不同的 joint-axis 拓扑等价类。N=11..50 是同一复制链循环的产品长尾外推，不要求 sweep 全量覆盖。

seed_domain_policy：procedural_first

Procedural Sampling / Sweep Plan：
- `config_from_seed(seed)` 对所有普通 seed 用 deterministic procedural sampling；`seed=0` 不特殊。
- 采样顺序：family（α/β/γ 加权）→ 由 family 解出 (root_hanger, hanging_module, coupling_swing_policy) 的合法子集并采样 → `module_count`（普通 seed product 域 3..50，小 N 高频、11..50 长尾；sweep overrides 只枚举 3..10）→ controlled local scales（cup_top_r/height/swing_limit/oval_aspect/n_petals）→ palette_style。
- `resolve_config` 应用 §9 compatibility matrix（family lock），把 (root, module, coupling) 投影到合法家族组合；clamp 所有连续 scale，按 inequality 回缩 pitch；最终选择经 `slot_choices_for_seed` 暴露。
- 初版 sweep：seeds 0–49 via `uv run articraft template sweep-pipeline rain_chain`。
- 成熟审计：seeds 0–999，目标 slot choice tuple distinct（含 N 维）富类别建议 ≥300（report-only）（5 家族形态 × product N 3..50 可达；sweep 必测仅 N 3..10）。若低于 300，原因通常是家族锁把 root×module×coupling 限成 5 种形态或 sampler 长尾权重过低，需检查 N=11..50 是否在普通 seed 中有稀有覆盖。
- Regression overrides：初版无。未来仅对已知失败回归 / reviewer 指定 seed 添加，须写明原因；不得用小型 curated/modulo 表当主 seed domain。

Controlled local parameterization：
- `cup_top_r_scale [0.85,1.18]` independent：clamp 保证 bail span 仍坐在 rim 边（不悬空）。
- `cup_taper_scale` equation：`cup_bot_r = cup_top_r * k`，k∈[0.30,0.48]，保持 funnel 收口（测试 bot<0.5*top）。
- `cup_height_scale [0.85,1.20]` independent：影响模块竖直尺寸。
- `module_pitch_scale` equation：`= f(cup_height_scale)`，保证相邻模块接口贴合、不穿插。
- `swing_limit_scale [0.7,1.15]` independent：limits 永远包含 rest q=0；单轴 ≤±45°、交替轴 ≤±40°。
- `link_oval_aspect [1.6,2.6]` independent（仅 oval）：保持 half_len>1.5*half_wid。
- `n_petals {6,8,10,12}` conditional（仅 lotus）。
- 所有 scale 在 `resolve_config` 内 clamp/派生；inequality（链总长包络、bail/eye 半径配合）在 `resolve_config` 求解，不留到 builder。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | family-first 加权（α/β/γ）→ 家族内 slot 子集 → N 加权小 → scales → palette；最终选择精确导出 | `slot_choices_for_seed` 匹配实际 build 的 root/module/coupling/N |
| compatibility matrix | family lock：root×module×coupling 三者按家族联动（α/β/γ）；非法跨家族组合被投影/fallback | 无跨家族错配（如 oval link 配 eye_bracket）、无悬空模块、无穿模、无非法 axis、链不超包络 |
| controlled local variation | clamp top_r/taper/height/pitch/swing_limit/oval_aspect/n_petals | 比例变化不破坏 bail-rim 接触、swing pivot origin、相邻模块贴合、类别 identity |
| regression overrides | none | 仅 reviewer/failure-driven 稀疏 override |
| random sweep | 0–49 初版，0–999 成熟审计；sweep 必测 N=3..10，普通 seed 可生成 N=11..50 | （含 N）、joint origin、相邻模块 contact、rest/posed 下穿模与悬空 |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| root_hanger | 3 | yes | yes | eye torus / V-wire+axle / 水平 ring+spoke，真实结构差异 |
| hanging_module | 4 | yes | yes | round/square/lotus funnel + oval link（含 link-only 无杯拓扑） |
| coupling_swing_policy | 3 | yes | yes | bail-eye 单轴 / captured-loop 单轴 / interlocked 交替轴 |

Compatibility matrix / gating（family lock；优先排除易坏组合）：
- 家族 α（A 系）：`eye_bracket` ↔ {`round_funnel_cup`(lathe), `lotus_petal_cup`} ↔ `bail_eye_single_axis`。bail hook 穿 eye torus，单 Y 轴。
- 家族 β（B 系）：`vee_wire_hanger` ↔ {`square_funnel_cup`, `round_funnel_cup`(cadquery 圆碗)} ↔ `captured_loop_over_bar_single_axis`。竖环套 axle bar，单 Y 轴。
- 家族 γ（link 系）：`ring_bracket` ↔ `oval_chain_link` ↔ `interlocked_link_alternating_axis`。oval 互穿、交替 XZ/YZ + 交替 Y/X 轴。**强绑定，不可拆**。
- 跨家族非法组合（必须 gate 掉）：oval_chain_link 配任何单轴 coupling 或 eye/V 挂件（oval 需水平 ring + 交替轴）；cup 模块配 ring_bracket（cup 不穿水平 ring）；lotus/round(lathe) 配 captured_loop（A 系 cup 无底部 axle bar）。
- N 边界：N<3 退化为非链（拒绝）；N>8 超出已读源域（clamp 到 8，或 reviewer-gate 才扩）。
- swing range：limits 必须含 q=0；交替-轴家族两个轴的 range 独立 clamp，避免相邻 link 在大角度互穿。

## Validator

- `slot_choices_for_seed(seed)` 返回三个 slot 的已实现 module 名 + `module_count` N。
- `config_from_seed(seed)` 对所有普通 seed 用 deterministic procedural sampling；`seed=0` 不特殊。
- `resolve_config` 仅由 family 解出 (root, module, coupling) 合法组合（family lock），并 clamp 所有 local scale；inequality（链包络、bail/eye 配合）在此求解。
- 链精确 emit N 个 REVOLUTE joint：cup 家族 `swing_1..swing_N`，oval 家族 `swing_0..swing_{N-1}`。
- 每个 `swing_{i}` 的 axis 符合 Slot C：单轴策略全 (0,1,0)；interlocked 策略 even (0,1,0)/odd (1,0,0)；range 含 q=0。
- 每个 `swing_{i}` origin 落在上一模块的真实下游 pivot（eye / axle bar / 底弧）上，不悬空。
- 相邻模块有真实 contact（bail↔eye / bail↔bar / oval↔oval），用 element-scoped allow_overlap 声明 captured 关系（不全局放开）。
- 模块形状源语义保持：lathe funnel 保持 LatheGeometry；cadquery 方/圆杯保持 mesh_from_cadquery（drain+bar）；lotus 保持 scalloped MeshGeometry；oval 保持 tube_from_spline_points 闭合椭圆。
- palette_style 仅改 material；rim 比 shell 亮、wire 钢灰/中性的 source 约束保持。
- rest pose：root 在最上，N 个模块竖直递降（每段 z 明显低于上一段），整链挂在 root 下方；posed pose：摆动 top joint 带动整链横移（top 模块与 bottom 模块都横移）。

## Reject cases

- 任何 sampled build 的 `module_count` < 3 或 > 8（超出已读源域）。
- 用连续尺寸参数伪造更多模块（应只用 multiplicity 轴 + 真实 source 模块）。
- oval_chain_link 与单轴 coupling / eye 或 V 挂件错配（破坏交替-轴互穿真实拓扑）。
- cup 模块挂在 `ring_bracket` 上（cup 不穿水平 ring，会悬空）。
- 某个模块缺少 `swing_{i}` REVOLUTE，或 axis 非 source 语义（如给 cup 链交替轴、给 oval 链单轴）。
- 模块悬空 / 不与上一模块接触（bail 不到 eye、竖环不套 bar、oval 不互穿）。
- captured-pin overlap 被全局放开，而非 element-scoped 声明真实 bail↔eye / bail↔bar / oval↔oval 关系。
- 模块源 primitive 被降级成 Box 占位（funnel/lotus/oval 失去 hollow / scalloped / 椭圆 identity）。
- palette 把金属 shell 上成高饱和非金属色（违反 muted 金属约束）。
- swing limits 排除 rest q=0，或链在大角度自穿插 / 穿过 root。

## 与相邻类别的边界

- 不该混入：实心 `downpipe` / 落水管 / 排水沟（rain_chain 是开放可见的悬挂钟摆链，不是封闭管道；无 N-模块 multiplicity 钟摆）。
- 不该混入：`chain` / 项链 / 链条首饰（尺度、root=gutter 挂件语义、落水用途都不同；rain_chain 的模块是杯/漏斗/lotus 或专用 oval 落水环）。
- 不该混入：`wind_chime` / 串珠风铃挂饰（功能是声响/装饰，不是 gutter 引流；不强制 root-挂件 + funnel 模块）。
- 不该混入：`n_joint_revolute_chain` / 机械串联臂（rain_chain 是被动重力钟摆链、模块同构且无驱动 end-effector；不是驱动关节臂）。
- 不该混入：`bell_tower` / 摆钟摆（单摆 + 塔，不是 N 个同构悬挂模块的线性链）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 基于本小类全部 6 个 5 星样本（2 parents + 4 converged variants）逐个读 model.py 作出。这是近纯 multiplicity / 线性钟摆链：主轴 = `cup_count`/`link_count`，源采样 {3,5,8}，product 域扩展到 N∈[3,50]，sweep/test 只要求 N∈[3,10]。3 个 slot（root_hanger×3, hanging_module×4, coupling_swing_policy×3）按 3 个真实家族（α eye-bracket cup / β V-hanger cup / γ ring oval）锁定联动——非自由三元笛卡尔，故组合靠 N×家族形态（product 5×48=240；sweep 5×8=40 distinct）过 diversity 门槛。palette 6 套 colorway（verdigris/galvanized/copper/bronze/aluminium/blackened，均源自样本）。待审核后再实现模板。 |

## 模板实现备注（可选）

- 用 family（α/β/γ）作为顶层 gate：先采家族，再由家族解出 (root, module, coupling) 合法三元，避免非法跨家族组合从源头产生。
- module factory 消费 `index i`、`module_count N`、family、resolved scales、palette、`ctx.rng`，按家族保持源 primitive（Lathe / cadquery / MeshGeometry / tube）。
- pivot 链：把每模块的“下游 pivot z”作为下一 `swing` 的 origin（A `BOT_EYE_Z` / B `-CUP_DROP` / γ `BOTTOM_PIVOT_Z`）；首段用 root 下游 pivot。
- element-scoped allow_overlap：A 系 `link_wire↔bottom_eye`/`link_wire↔cup_rim`/`bottom_stem↔*`；B 系 `bail↔shell(bar)`；γ 系 `oval_body↔oval_body`/`oval_body↔bracket_ring`/`ring_spoke↔hanger_bar` —— 复制 §10 reject 中所有家族的真实 captured 关系。
- oval 家族交替轴：even→(0,1,0)、odd→(1,0,0)；交替材质 copper/copper_dark 是 module-local，不计 multiplicity。
- N 命名：默认对齐源（cup 1-based、oval 0-based）以便回溯；如统一为 1-based 须同步更新 run_tests 命名断言。

## Module Source Index

| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S-A1 | root_hanger | eye_bracket | rec_...efa584a4 (parent A) | L153-L185 | collar+spout+lug+eye torus root；下游 eye 接口 |
| S-A2 | root_hanger | vee_wire_hanger | rec_...3dcec91a (parent B) | L173-L211 | V-wire hanger + apex axle bar root |
| S-A3 | root_hanger | ring_bracket | rec_gutter_downchain_var_link_chain | L113-L175 | spout + 水平 ring + spokes root（oval 链用） |
| S-B1 | hanging_module | round_funnel_cup | rec_...efa584a4 (parent A) | L84-L138, L197-L249 | LatheGeometry 圆锥 funnel cup + bail + boss/stem/eye |
| S-B2 | hanging_module | square_funnel_cup | rec_...3dcec91a (parent B) | L76-L170, L238-L242 | cadquery 方锥 funnel（drain+bar）+ 方 lip + bail 竖环 |
| S-B3 | hanging_module | lotus_petal_cup | rec_gutter_downchain_var_lotus_cups | L96-L176, L271-L319 | lotus-flared shell + scalloped MeshGeometry rim |
| S-B4 | hanging_module | oval_chain_link | rec_gutter_downchain_var_link_chain | L67-L97, L184-L201 | 闭合椭圆 oval link（交替 XZ/YZ）|
| S-C1 | coupling_swing_policy | bail_eye_single_axis | rec_...efa584a4 (parent A) | L256-L274 | bail-hook-through-eye 单 Y 轴 ±35° swing |
| S-C2 | coupling_swing_policy | captured_loop_over_bar_single_axis | rec_...3dcec91a (parent B) | L244-L265 | 竖环 captured over axle bar 单 Y 轴 ±0.7 swing |
| S-C3 | coupling_swing_policy | interlocked_link_alternating_axis | rec_gutter_downchain_var_link_chain | L184-L226 | oval 互穿 + 交替 Y/X 轴 ±35° swing |
</content>
</invoke>
