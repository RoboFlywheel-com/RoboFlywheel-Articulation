# Fire Hydrant — Modular Spec

## 元信息
| 项 | 值 |
|---|---|
| slug | `fire_hydrant` |
| template path | `agent/templates/Urban_Environment_Fire_Hydrant.py` |
| test path (optional) | `tests/agent/test_fire_hydrant_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed` |

`mixed`：三个固定 named slot（bonnet_shape + outlet_cap_style + base_form）挂在共同的 `body` chassis 上（parallel_children），外加 `outlet_{i}` 的 multiplicity 复制轴（同构 outlet 子装配 N 次复制）。顶部 operating nut 是 REVOLUTE 主关节，每个 outlet cap 是 PRISMATIC 关节并拖一条 serial-REVOLUTE round-link chain。

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 10 |
| read_count | 10 |
| read_scope | all 5-star samples in this category（9 个 pillar-hydrant 家族 + 1 个 off-identity handheld nozzle）|
| source_index_policy | only adopted module sources are indexed below；off-identity nozzle 仅用于 neighbor-boundary 说明，不进 module 表 |

阅读要点：
- **Parent（canonical identity）** `P_9a6935e0`：完整 pillar hydrant。`body` 单 root part（base_flange + bolts + ribbed barrel + valve_chamber + bonnet_flange + bonnet_dome + nut_boss 全部是 body 上的 visual，不是独立 part），顶部 `operating_nut` REVOLUTE 绕 Z（L260-L280），三个 outlet 由手写 `add_outlet(...)` 调用 3 次（L463-L473）。每个 outlet = stub + collar(body visual) + `{tag}_tether`(FIXED body eye) + `{tag}_cap`(PRISMATIC lift-off, L411-L419) + `{tag}_chain_{i}` serial round-link chain(REVOLUTE links, helper `_add_round_link_chain` L79-L106)。
- **bonnet_flat** `var_bonnet_flat`：把 DomeGeometry 换成扁平 LatheGeometry 圆盘盖 + 8 颗 cap-bolt 环 + 平顶 nut_boss（L220-L258 区段）。
- **bonnet_pointed** `var_bonnet_pointed`：锥形 LatheGeometry witch-hat（cone_height=0.30），nut_boss 抬到锥尖（L219-L239 区段）；body top > 1.05m。
- **cap_storz** `var_cap_storz`：cap_body 加 2 个外凸 lug ear（90°/270°，`for j in range(2)`），取代 6 棱滚花 lug（L312-L343 区段）。
- **cap_plain** `var_cap_plain`：光滑 DomeGeometry 风格 cap + 顶部单 bail loop（TorusGeometry），无 lug、无侧 ring；chain 从 bail 顶穿出（L316-L396 区段）。
- **base_sleeve** `var_base_sleeve`：直圆柱 sleeve skirt + 落地微 flare，删掉 base_flange 与 bolt 环（L126-L147 区段）。
- **outlets1 / outlets2 / outlets3stack**：multiplicity 三个 N 样本（N=1 单前 pumper / N=2 双侧 ±90° / N=3 等分 120°）。
- **off-identity** `nozzle_5af9d100`：横向 +X barrel + 喇叭 bell inlet + pistol grip + bail shut-off lever（REVOLUTE 横 Y 销）+ 旋转 fog diffuser collar。整机拓扑与 pillar hydrant 不同，**排除**。

## 核心身份

铸铁立柱式（PILLAR）消火栓：竖直 +Z barrel 车身，底部落地固定（bolted ground flange 或 cast sleeve skirt），中段 ribbed barrel，上部 widened valve chamber 承载侧向 hose outlet（每个带 lift-off cap + tether chain），上方 bolted bonnet flange + 铸顶 bonnet（domed / flat-bolted / pointed-cone），顶端一颗 square operating nut。

**默认成熟域**：~1.0 m 高（pointed cone 变体可到 ~1.1m），cast-iron 单 root body chassis；唯一旋转件是 top operating nut（REVOLUTE 绕 Z），唯一直线件是每个 outlet cap（PRISMATIC 沿 outlet 轴），加每条 cap chain 的 serial REVOLUTE round links。

**关键身份关节 = cap-on-chain + bonnet operating nut**：cap 必须能拉直滑离 outlet 而不翻转，并由 round-link chain 拴回 body eye；operating nut 必须绕竖直轴转。两者缺一即不是合格 pillar hydrant。

不该混入：见「与相邻类别的边界」。

## 槽位 + 候选模块表

### Slot A：bonnet_shape（顶部铸盖形状 —— 主结构轴；operating nut REVOLUTE 保持）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `bonnet_domed` | rec_cast-iron-pillar-fire-hydrant-bright-red-body-wi_20260608_164513_388731_9a6935e0 | L236-L254 | eligible if compatible | DomeGeometry(0.105) 低圆顶 + nut_boss CylinderGeometry 在顶；body top ~0.91m |
| `bonnet_flat_bolted` | rec_fire_hydrant_var_bonnet_flat | L220-L258 | eligible if compatible | 扁平 LatheGeometry 圆盘盖（flat_cap_h=0.028）+ `for i in range(n_cap_bolts)` 8 颗 cap-bolt 环 + 平顶 nut_boss；squat disc |
| `bonnet_pointed_cone` | rec_fire_hydrant_var_bonnet_pointed | L219-L239 | eligible if compatible | 锥形 LatheGeometry witch-hat（cone_height=0.30），nut_boss 在锥尖；body top > 1.05m |

### Slot B：outlet_cap_style（每个 outlet 盖样式 —— PRISMATIC lift-off + chain 保持；模板级统一应用到所有 outlet_{i}）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `cap_knurled_screw` | rec_cast-iron-pillar-fire-hydrant-bright-red-body-wi_20260608_164513_388731_9a6935e0 | L349-L401 | eligible if compatible | LatheGeometry cap_body + `for j in range(6)` 6 棱滚花 lug Box + 侧挂 cap_chain_ring（TorusGeometry）；chain 从侧 ring 出 |
| `cap_storz_lever` | rec_fire_hydrant_var_cap_storz | L312-L343 | eligible if compatible | cap_body + 仅 2 个外凸 lug ear（90°/270°，`for j in range(2)`，projects beyond rim）；Storz 1/4-turn 双耳盖；侧挂 ring 同 baseline |
| `cap_plain_dome_bail` | rec_fire_hydrant_var_cap_plain | L316-L396 | eligible if compatible | 光滑 dome cap + 顶部单 bail loop（TorusGeometry），无 lug、无侧 ring；chain 从 bail 顶穿出（cap_attach 改到 bail 顶） |

### Slot C：base_form（底部落地结构）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| `base_bolted_flange` | rec_cast-iron-pillar-fire-hydrant-bright-red-body-wi_20260608_164513_388731_9a6935e0 | L136-L167 | eligible if compatible | 宽 LatheGeometry base_flange + `for i in range(n_base_bolts)` 8 颗黄铜六角栓环；z=0 落地 |
| `base_straight_sleeve` | rec_fire_hydrant_var_base_sleeve | L126-L147 | eligible if compatible | 直圆柱 sleeve skirt + 落地微 flare（flare_r = skirt_r+0.012），无栓环；光面铸套裙座 |

> Slot C 只有 2 candidate：源池中底部结构仅这两种真实拓扑（bolted flange / cast sleeve）。其余差异（缩放、栓数）是装饰，规则禁止升轴。按 SPEC_TEMPLATE.md 第 4 节降到 2 candidate 的允许情形，已说明理由。

## 槽位图（slot graph）

pattern: `mixed`（parallel_children + multiplicity）

```
                                  body (single root chassis, +Z barrel, z=0 落地)
                                    │
   Slot C base_form ──[FIXED, z=0 ground contact plane]──┐
   Slot A bonnet_shape ──[FIXED, bonnet_base_z=0.805 mating face on top of bonnet_flange]──┤
   (ribbed barrel + valve_chamber = body parent visual, fixed)                              │
                                    ├──[REVOLUTE axis=(0,0,1) @ nut_seat_z (bonnet apex)]── operating_nut   (Slot A 提供 nut_seat_z)
                                    │
   ┌── outlet_{i} loop（multiplicity，i=0..N-1，沿 valve_chamber 周向 yaw 分布）──┐
   │   body.{i}_stub + {i}_collar               = body parent visual (FIXED on chamber)     │
   │   {i}_tether  ──[FIXED @ chamber eye]──    body eye (chain anchor)                      │
   │   {i}_cap     ──[PRISMATIC axis=(0,0,1) local @ outlet mouth, rpy aims radial]── lift-off cap (Slot B 样式)
   │   {i}_chain_0..{i}_chain_{M-1} ──[serial REVOLUTE links, axis alt X/Y, ±35°]── 从 {i}_cap ring/bail → {i}_tether eye
   └──────────────────────────────────────────────────────────────────────────────────────┘
```

接口点位：
- **base ↔ ground**：base_form 底面 = z=0 contact plane（FIXED support）。base_flange / sleeve 都落在 z≈0。
- **bonnet ↔ body**：bonnet 坐在 `bonnet_base_z=0.805`（bonnet_flange 顶面 mating face），FIXED。bonnet_shape 决定 `nut_seat_z`（domed≈bonnet_base_z+0.110；flat≈bonnet_base_z+0.048；cone≈bonnet_base_z+0.30）。
- **operating_nut ↔ bonnet**：REVOLUTE @ `nut_seat_z`，axis=(0,0,1)，由 Slot A 派生高度。
- **outlet cap ↔ body**：PRISMATIC，joint frame 在 outlet mouth（`rpy=(0, π/2, yaw)` 把局部 +Z 转成径向外），cap 沿局部 +Z 直线拉出，lower=0（seated）→ upper≈0.12。
- **chain ↔ cap & tether**：root link REVOLUTE 接在 cap ring/bail（随 Slot B 改 attach 点）；尾 link 触及 body eye；links 之间 serial REVOLUTE，axis 交替 (1,0,0)/(0,1,0)。

互斥/派生：Slot A、B、C 互相独立可任意组合（无互斥）。Slot B 样式统一应用到所有 outlet_{i}（一个种子内所有 cap 同款）。outlet_{i} 的 N 由 multiplicity 轴决定；chain link 数 M 由 chain span 自动派生（`max(5, round(span/CHAIN_LINK_STEP))`）。

## 每槽位 Module Emits / Interfaces

### Slot A / module bonnet_domed
| emits | 描述 | 来源 |
|---|---|---|
| parts | bonnet_dome + nut_boss（均 body visual，非独立 part） | S1 / model.py:L236-L254 |
| internal joints | 无（盖固定）；下游提供 operating_nut REVOLUTE 的 seat 高度 | S1 / model.py:L260-L280 |
| upstream interface | 坐在 bonnet_base_z=0.805 mating face | S1 / model.py:L241 |
| downstream interface | nut_seat_z = bonnet_base_z + 0.110（供 operating_nut REVOLUTE @ axis Z） | S1 / model.py:L247,L277 |

### Slot A / module bonnet_flat_bolted
| emits | 描述 | 来源 |
|---|---|---|
| parts | bonnet_flat_cap（squat disc）+ `for i in range(n_cap_bolts)` 8 cap-bolt ring + 平顶 nut_boss | S_flat / model.py:L220-L258 |
| internal joints | 无 | S_flat / model.py:L237-L252 |
| upstream interface | 坐在 bonnet_base_z=0.805 | S_flat / model.py:L231 |
| downstream interface | nut_seat_z = bonnet_base_z + flat_cap_h(0.028) + boss_h(0.020) ≈ 0.853 | S_flat / model.py:L252-L256 |

### Slot A / module bonnet_pointed_cone
| emits | 描述 | 来源 |
|---|---|---|
| parts | bonnet_cone（witch-hat LatheGeometry，cone_height=0.30）+ 锥尖 nut_boss | S_cone / model.py:L219-L239 |
| internal joints | 无 | S_cone / model.py:L239 |
| upstream interface | 坐在 bonnet_base_z=0.805 | S_cone / model.py:L233 |
| downstream interface | nut_seat_z = bonnet_base_z + cone_height(0.30)；body top > 1.05m | S_cone / model.py:L239 |

### Slot B / module cap_knurled_screw（应用于每个 outlet_{i}）
| emits | 描述 | 来源 |
|---|---|---|
| parts | {i}_cap_body（LatheGeometry）+ `for j in range(6)` 6 lug Box + {i}_cap_chain_ring（侧 Torus） | S1 / model.py:L349-L401 |
| internal joints | {i}_to_cap PRISMATIC（axis 局部 Z = 径向外，lower=0 upper≈0.12） | S1 / model.py:L406-L419 |
| upstream interface | joint frame @ outlet mouth (mouth_x, mouth_y, center_z), rpy=(0,π/2,yaw) | S1 / model.py:L411-L416 |
| downstream interface | cap_chain_ring 侧挂点 → chain root link REVOLUTE | S1 / model.py:L390-L401, L429-L458 |

### Slot B / module cap_storz_lever（应用于每个 outlet_{i}）
| emits | 描述 | 来源 |
|---|---|---|
| parts | {i}_cap_body + 仅 2 lug ear（90°/270°，`for j in range(2)`，projects beyond rim）+ 侧 ring | S_storz / model.py:L312-L343 |
| internal joints | {i}_to_cap PRISMATIC（同 baseline） | S1 / model.py:L406-L419 |
| upstream interface | joint frame @ outlet mouth（同 baseline） | S1 / model.py:L411-L416 |
| downstream interface | 侧 ring → chain root（同 baseline） | S1 / model.py:L429-L458 |

### Slot B / module cap_plain_dome_bail（应用于每个 outlet_{i}）
| emits | 描述 | 来源 |
|---|---|---|
| parts | {i}_cap_body（光滑 dome）+ {i}_cap_bail（顶部单 Torus loop），无 lug、无侧 ring | S_plain / model.py:L316-L340 |
| internal joints | {i}_to_cap PRISMATIC（同 baseline） | S1 / model.py:L406-L419 |
| upstream interface | joint frame @ outlet mouth（同 baseline） | S1 / model.py:L411-L416 |
| downstream interface | bail 顶 attach（cap_attach 移到 bail 顶）→ chain root；额外 link↔body/cap drape allow_overlap | S_plain / model.py:L368-L396 |

### Slot C / module base_bolted_flange
| emits | 描述 | 来源 |
|---|---|---|
| parts | base_flange（宽 LatheGeometry）+ `for i in range(n_base_bolts)` 8 黄铜六角栓环 | S1 / model.py:L136-L167 |
| internal joints | 无 | — |
| upstream interface | 底面 z=0 ground contact plane | S1 / model.py:L137-L153 |
| downstream interface | 顶面接 barrel（barrel_r+0.012 @ base_flange_h+0.02） | S1 / model.py:L143-L146 |

### Slot C / module base_straight_sleeve
| emits | 描述 | 来源 |
|---|---|---|
| parts | sleeve_skirt（直圆柱 + 落地微 flare），无栓环 | S_sleeve / model.py:L126-L147 |
| internal joints | 无 | — |
| upstream interface | 底面 flare_r @ z=0 ground contact plane | S_sleeve / model.py:L131-L138 |
| downstream interface | 顶面接 barrel（barrel_r+0.006 @ skirt_top_z） | S_sleeve / model.py:L137 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| `bonnet_shape` | enum | `bonnet_domed` / `bonnet_flat_bolted` / `bonnet_pointed_cone` | bonnet_domed | choice | deterministic procedural sampler | Slot A 表 |
| `outlet_cap_style` | enum | `cap_knurled_screw` / `cap_storz_lever` / `cap_plain_dome_bail` | cap_knurled_screw | choice | deterministic procedural sampler；统一应用到所有 outlet_{i} | Slot B 表 |
| `base_form` | enum | `base_bolted_flange` / `base_straight_sleeve` | base_bolted_flange | choice | deterministic procedural sampler | Slot C 表 |
| `palette_style` | enum | `municipal_red` / `high_vis_yellow` / `silver_chrome` / `safety_green` / `industrial_blue` / `matte_black` | municipal_red | choice | 仅改 material rgba，不改拓扑；≥4 colorway | 见下 palette 说明 |
| `outlet_count` (N) | int | [1, 4]（multiplicity 轴，见下节） | 3 | choice | 加权采样；placement 由 N 解析 | Multiplicity 节 |
| `barrel_height_scale` | float | [0.90, 1.12] | 1.0 | independent | 缩放 barrel_top_z/chamber 段；clamp 后保证 body top（domed/flat>0.80m, cone>1.05m） | S1 / L120-L131 |
| `barrel_radius_scale` | float | [0.92, 1.10] | 1.0 | independent | 缩放 barrel_r/chamber_r；clamp | S1 / L123-L125 |
| `outlet_r_scale` | float | [0.85, 1.20] | 1.0 | independent | 每 outlet stub/cap 半径；pumper 派生更大 | S1 / L300,L349 |
| `pumper_r_factor` | float | derived | 1.45 | equation | `pumper_outlet_r = side_outlet_r · pumper_r_factor`（N≥3 含前 pumper 时） | S1 / L465-L472 |
| `nut_seat_z` | float | derived | — | equation | `= bonnet_base_z + f(bonnet_shape)`（domed 0.110 / flat 0.048 / cone 0.30） | S1/L247, flat/L252, cone/L239 |
| `chain_link_count` (M) | int | derived | — | equation | `M = max(5, round(chain_span/CHAIN_LINK_STEP))` per outlet | S1 / L444-L446 |
| (—) | constraint | — | — | inequality | outlet 周向 yaw 间隔 ≥ 角宽（基于 outlet_r 与 chamber_r 的弦角）以防相邻 stub/cap 穿插；违反则回缩 outlet_r_scale 或拒绝重采 | clearance |
| (—) | constraint | — | — | inequality | chain_span ≤ envelope（eye 与 cap ring 距离）；eye_z clamp ≥ chamber_bottom_z+0.022 保证 eye 坐在 chamber 壁 | S1 / L326 |
| (—) | constraint | — | — | inequality | base_form 顶半径必须 ≤ chamber_r 且 ≥ barrel_r（落地外径不穿 barrel）；按 barrel_radius_scale 重算 | S1/L143, sleeve/L137 |

**palette_style 说明**（≥3，目标 4-6 colorway）：每个 colorway 只改三种 material（body / brass-accent / chain）的 rgba，不动几何。
- `municipal_red`：body=(0.74,0.10,0.09)，accent=brass(0.82,0.62,0.16)，chain=dark(0.30,0.27,0.13)（baseline，S1/L112-L114）
- `high_vis_yellow`：body=(0.92,0.78,0.10)，accent=steel(0.62,0.63,0.66)，chain=dark_steel
- `silver_chrome`：body=(0.72,0.73,0.75)，accent=brass，chain=dark
- `safety_green`：body=(0.10,0.42,0.20)，accent=brass，chain=dark
- `industrial_blue`：body=(0.12,0.30,0.55)，accent=steel，chain=dark
- `matte_black`：body=(0.14,0.14,0.15)，accent=brass，chain=dark

## Multiplicity / Copy Logic

单一 multiplicity 轴：**outlet 数量 N**（valve chamber 上 outlet 子装配的数量）。

- `count_param`: `outlet_count`
- `N_range`: `[1, 4]`（产品全程；测试偏小 N∈{1,2,3}）
  - N=1：单前 pumper（var_outlets1，yaw=0，大半径）
  - N=2：双侧对称 ±90°（var_outlets2，`yaw=radians(90+180·i)`）
  - N=3：等分 120°（var_outlets3stack，`yaw=2π·i/3`）或 parent 排布（2 侧 ±90° + 1 前 pumper）
  - N=4：罕见四向 90° 等分（采样稀有）
- sampling domain（权重档）：N=3 高频（baseline，~45%）、N=2 次之（~30%）、N=1（~15%）、N=4 稀有（~10%）。测试 sweep 主跑 N∈{1,2,3}。
- copied object：单个 outlet 子装配 = `{i}_stub`(body visual) + `{i}_collar`(body visual) + `{i}_cap`(PRISMATIC lift-off, Slot B 样式) + `{i}_tether`(FIXED body eye) + `{i}_chain_{j}` serial REVOLUTE round-link chain。
- naming：`outlet_{i}`（i=0..N-1），其下 `outlet_{i}_cap` / `outlet_{i}_tether` / `outlet_{i}_chain_{j}` / `outlet_{i}_collar` / `outlet_{i}_stub`。**KEY 模板化动作**：把 parent 的 3 次手写 `add_outlet(...)`（left_hose/right_hose/front_pumper，positional args）收成 `outlet_specs` 列表 + `for i, spec in enumerate(outlet_specs)` 循环，配置驱动 N（与 var_outlets2/3stack 的 `for i in range(...)` 写法一致）。
- placement：沿 valve_chamber 周向按 yaw 角分布。N=1→{0°}（pumper，center_z=chamber_bottom_z+0.060，大半径）；N=2→{90°,-90°}（侧，center_z=chamber_top_z-0.060，等径）；N=3→120° 等分同径 或 parent 混合（2 侧 + 1 低前 pumper）；N=4→{0,90,180,270}°。每个 spec 携带独立 `outlet_r / center_z / eye_yaw_deg`（pumper 更大更低，eye_yaw 偏移避让宽 stub）。
- joint policy：每个 cap = PRISMATIC 沿自身 outlet 局部 +Z（径向外），lower=0(seated) upper≈0.12，不翻转；每条 chain = serial REVOLUTE links（axis 交替 X/Y，±35°）；tether eye = FIXED。所有 outlet 共享同一 `add_outlet` 逻辑（统一策略，统一 Slot B 样式）。
- source/gating：N 与 yaw 周向间隔受 inequality 约束（相邻 outlet 弦角不重叠）；N≥3 时若含前 pumper 则 pumper 半径派生更大并下移 center_z 以避让侧 outlet。

## 拓扑多样性审计

总组合数：bonnet_shape 3 × outlet_cap_style 3 × base_form 2 × distinct-N 4（N∈{1,2,3,4}）= **3 × 3 × 2 × 4 = 72 ≥ 10 ✓**
（即便忽略 cap_style 与 base_form，仅 bonnet 3 × N 4 = 12 仍过门槛。）

理由：3×3×2 = 18 个纯 slot 组合即已 >10，且 distinct-N 把 outlet 子装配数量改成不同 part/joint 拓扑等价类（N=1/2/3/4 part 数与 joint 数不同），distinct 拓扑数远超 10。

seed_domain_policy：`procedural_first`

Procedural Sampling / Sweep Plan：`config_from_seed(seed)` 用 `ctx.rng`（seed 派生）做四次独立加权抽样——bonnet_shape、outlet_cap_style、base_form（均匀）+ outlet_count（小 N 偏多权重档），再独立采 `barrel_height_scale`/`barrel_radius_scale`/`outlet_r_scale`/`palette_style`。`resolve_config` 按 equation 派生 nut_seat_z / pumper_outlet_r / chain_link_count，按 inequality 投影 outlet 周向间隔与 base 外径，违反则回缩 scale 或拒绝重采。slot_choices_for_seed 返回 `[(bonnet_shape,…),(outlet_cap_style,…),(base_form,…),(outlet_count, N)]`（连续 scale 不进 slot_choices，除非 N 改变拓扑等价类）。`seed=0` 不特殊。compatibility matrix：三个固定 slot 全互兼容（无非法组合）；cap_plain_dome_bail 需额外 link↔body/cap drape allow_overlap（按 var_cap_plain 写法）；N=1 时强制 pumper-only（无 side），N=2 强制对称双侧无 pumper（gating 防 var_outlets1/2 测试断言冲突）。

Topology target：1000-seed slot choice tuple distinct 建议 >=72（=完整 slot×N 组合）；本类别 slot/N 组合数即 72，可达。低于 300 的原因：pillar hydrant 真实结构家族有限（铸件，固定 4 拓扑轴），由类别身份约束，非缺陷。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

Controlled local parameterization：初版应含 `barrel_height_scale`[0.90,1.12]、`barrel_radius_scale`[0.92,1.10]、`outlet_r_scale`[0.85,1.20]，全在 `resolve_config` clamp。依赖：`pumper_outlet_r = side_outlet_r·1.45`（equation）；`nut_seat_z = bonnet_base_z + f(bonnet_shape)`（equation）；`chain_link_count = max(5, round(span/STEP))`（equation）；outlet 周向间隔、base 外径（inequality，投影/回缩）。这些 scale 只改安全比例，不破坏 outlet PRISMATIC 轴、operating-nut REVOLUTE 轴、chain serial 拓扑、ground/bonnet mating face 或 multiplicity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | bonnet/cap/base 均匀 + outlet_count 小 N 偏多权重；4 轴独立 | slot_choices_for_seed matches build choices |
| compatibility matrix | 三固定 slot 全互兼容；cap_plain 加 drape allow_overlap；N=1→pumper-only，N=2→对称双侧无 pumper | no floating, collision, axis, max multiplicity(N≤4), optional moving-child(cap/chain) failures |
| controlled local variation | barrel_height/radius_scale + outlet_r_scale，clamp+派生+投影 | proportions vary without breaking PRISMATIC/REVOLUTE axes, ground/bonnet mating, chain reach, identity |
| regression overrides | none | — |
| random sweep | seeds 0-49 初查，0-999 成熟审计 | 与 MatingContract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A bonnet_shape | 3 | yes | yes | |
| B outlet_cap_style | 3 | yes | yes | |
| C base_form | 2 | yes | no | 源池底部结构仅 2 真实拓扑，已说明降级理由 |
| multiplicity N | 4 distinct | yes | yes | N∈{1,2,3,4} |

## Validator

- slot_choices_for_seed returns implemented module names（bonnet/cap/base + outlet_count N）
- config_from_seed uses deterministic procedural sampling for all ordinary seeds（seed=0 不特殊）
- compatibility matrix / gating prevents illegal combinations（N=1 pumper-only / N=2 对称双侧无 pumper / cap_plain drape overlaps）
- optional regression overrides are sparse and justified（none）
- final templates do not endlessly cycle a small curated table as the main seed domain
- controlled local scale params (barrel_height/radius, outlet_r) clamped；不破坏 interfaces/clearance/joint origin/multiplicity
- cross-part scale deps（pumper_r equation、nut_seat_z equation、chain_link equation、outlet-spacing inequality、base-外径 inequality）resolved in `resolve_config`
- critical InterfaceSpec / MatingContract：base↔ground z=0、bonnet↔bonnet_base_z=0.805、operating_nut↔nut_seat_z、cap↔outlet mouth、chain↔cap-ring/bail & body-eye 存在
- key joints：operating_nut REVOLUTE axis=(0,0,1)；每个 {i}_cap PRISMATIC 径向轴 lower=0 slides straight（lateral<0.006）；chain links serial REVOLUTE ±35°
- copied objects follow naming（outlet_{i}_cap/_tether/_chain_{j}）and周向 placement policy

## Reject cases

- handheld pistol-grip nozzle 形态：横向 barrel + bell inlet + pistol grip + bail shut-off lever（横 Y 销）——出 pillar-hydrant 身份，拒绝（源 nozzle_5af9d100 不作车身候选）。
- 缺 top operating nut 或 operating nut 不绕竖直 Z 轴旋转。
- outlet cap 不是 PRISMATIC lift-off（翻转/铰链）或拉开时 lateral 漂移 > 0.006（应直线滑离 outlet 轴）。
- outlet 无 tether chain，或 chain 不是 serial REVOLUTE round-link（变成静态独立 strand / 不接 cap）。
- body 不落地（base min z 偏离 0 > 0.006）或非竖直 +Z 单 root chassis。
- N 超出 [1,4]，或相邻 outlet stub/cap 周向穿插（违反 spacing inequality）。
- bonnet 漂浮（未坐在 bonnet_base_z mating face）或 nut_seat_z 与所选 bonnet 形状不匹配（nut 悬空/嵌入）。
- 把纯颜色/材质、纯缩放、rib band 数、bolt 数当独立 slot 或 candidate（规则禁止）。

## 与相邻类别的边界

- 不该混入：**handheld fire-hose nozzle / branch nozzle**（横向 barrel + flared bell inlet + pistol grip + bail shut-off lever + 旋转 fog diffuser collar；竖直落地 pillar 身份缺失。源 nozzle_5af9d100 仅贡献 Storz coupling 灵感，不作车身）。
- 不该混入：**Fire_Extinguisher**（便携红罐 + 顶部 squeeze handle/lever + 软管喷嘴；无 ground flange、无侧 outlet 阵列、无 top operating nut、无 cap-on-chain）。
- 不该混入：**Standpipe / valve manifold / bollard**（无 bonnet operating nut + lift-off cap-on-chain 的定义性关节组合，识别身份不同）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | — |

## Module Source Index
| source_id | slot | module | sample_id | model.py 来源 | 采纳用途 |
|---|---|---|---|---|---|
| S1 | A/B/C | bonnet_domed + cap_knurled_screw + base_bolted_flange + outlet loop + operating_nut + chain helper | rec_cast-iron-pillar-fire-hydrant-bright-red-body-wi_20260608_164513_388731_9a6935e0 | L79-L475 | canonical parent：body chassis、operating_nut REVOLUTE、add_outlet→outlet loop、PRISMATIC cap、round-link chain、baseline bonnet/cap/base |
| S_flat | A | bonnet_flat_bolted | rec_fire_hydrant_var_bonnet_flat | L220-L258 | 扁平 bolted disc bonnet + 平顶 nut_seat |
| S_cone | A | bonnet_pointed_cone | rec_fire_hydrant_var_bonnet_pointed | L219-L239 | 锥尖 bonnet + 锥尖 nut_seat |
| S_storz | B | cap_storz_lever | rec_fire_hydrant_var_cap_storz | L312-L343 | 2-lug Storz cap |
| S_plain | B | cap_plain_dome_bail | rec_fire_hydrant_var_cap_plain | L316-L396 | 光滑 dome cap + bail loop + drape overlaps |
| S_sleeve | C | base_straight_sleeve | rec_fire_hydrant_var_base_sleeve | L126-L147 | 直 sleeve skirt base |

## 模板实现备注（可选）

- 共享 helper：`_rpy_aim_negz` / `_round_chain_link_mesh` / `_world_vec_to_outlet_local` / `_add_round_link_chain` 从 parent 直接改编；`add_outlet` 改成 list-driven loop。
- captured-pin / drape overlap：consecutive chain links 互链、chain root↔cap ring/bail、chain tail↔body eye 需 element-scoped allow_overlap（parent L573-L644 已示范）；cap_plain_dome_bail 额外 link↔body/cap drape overlap（var_cap_plain L563-L612）；cap_body↔collar seat embed overlap。
- MatingContract 注意：nut_seat_z 随 bonnet_shape 派生，operating_nut REVOLUTE origin 必须用派生值（否则 cone 变体 nut 嵌入）；base 顶半径随 barrel_radius_scale 重算以续接 barrel。
- 暂不进 seed domain：无（所有 slot/N 组合合法）。
