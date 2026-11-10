# Modular Spec — skincare_roller (Sports / Skincare Roller)

## 元信息
| 项 | 值 |
|---|---|
| slug | `skincare_roller` |
| template path | `agent/templates/Sports_Skincare_Roller.py` |
| test path (optional) | `tests/agent/test_skincare_roller_template.py` |
| stage | `SPEC_ONLY_DRAFT` |
| status | `pending` |
| __modular__ | `True` |
| pattern | `mixed`（parallel_children：fork-yoke + roller-head 都挂在共同 static handle body；multiplicity：roller-head + fork 单元按 roller_count 复制到 +Z/-Z 端） |

## 5 星样本阅读摘要
| 项 | 值 |
|---|---|
| five_star_total | 9 |
| read_count | 9 |
| read_scope | all 5-star samples in this category (parent + 8 variants) |
| source_index_policy | only adopted module sources are indexed below |

## 核心身份

手持式美容/面部按摩滚轮（jade / germanium facial massage roller）。一根**静态石质手柄**（grip body）水平居中于 x=0,y=0、轴沿 +Z 竖直；手柄两端各套一只**抛光金属 collar/ferrule**（手柄上的静态装饰）；从 collar 端升起**金属 fork/yoke**（静态，捕获滚轮的轴）；每个 fork 里夹一颗**石质滚轮头**，绕自己的 cross axle（轴沿 X）**自由连续旋转**——这是唯一的活动件。功能层固定为四层：static handle（grip）、collars（手柄静态装饰）、forks/yokes（静态轴承）、roller heads（活动件，每个一根 CONTINUOUS spin joint）。双端工具两端滚轮通常一大一小（小头在 +Z、大头在 -Z），尺寸差是**受控 per-unit 连续尺度参数**而非独立结构 candidate。默认成熟域：手柄长约 0.10 m、滚轮头 0.035–0.050 m、纯手持、无电动/无加热/无水箱。

## 槽位 + 候选模块表

每个 slot 是一个可替换的结构层；roller_count 是独立的 multiplicity 轴（见第 8 节）。

### Slot A：roller_head_form（每个 fork 里旋转的石头滚轮头）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| smooth_oval | rec_jade-facial-massage-roller-with-a-metal-handle-a_20260605_165942_156361_d964a399 | L76-L88（`_oval_roller`） | eligible if compatible | 扁椭球 jade oval：单位球 scale(half_x,ry,ry) + +Y rim off-axis marker nub；光滑表面 |
| faceted_gem | rec_skincare_roller_var_faceted_gem | L87-L144（`_faceted_roller`，MeshGeometry 手工三角化 ring_verts，FACET_N_RADIAL=10 × FACET_N_AXIAL=7 briolette barrel + 两端 cap fan） | eligible if compatible | 多刻面 cut-gem barrel：离散平面 facet（rose/briolette），decagonal 横截面而非光滑 |
| spiky_germanium | rec_skincare_roller_var_spiky_ball | L79-L112（`_spiky_ball`，core SphereGeometry + 嵌套 i(lat)×j(lon) nub 场 merge） | eligible if compatible | 近球 germanium massage ball + 规则 nub/spike 场（嵌套 for-range）；横截面 Y≈Z |
| textured_ridged | rec_skincare_roller_var_ridged | L80-L113（`_ridged_roller`，LatheGeometry wavy profile，cos 波 num_ridges 道环向沟槽 + marker nub） | eligible if compatible | barrel + 规则环向 grooves/ridges（lathe 旋转肋）；圆截面 barrel |

### Slot B：handle_form（静态石质 grip body）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| straight_stone_bar | rec_jade-facial-massage-roller-with-a-metal-handle-a_20260605_165942_156361_d964a399 | L103-L107（CylinderGeometry + bulge SphereGeometry merge，作为 handle visual） | eligible if compatible | 等径细圆杆 + 轻微中段 barrel bulge |
| contoured_waisted | rec_skincare_roller_var_waisted | L105-L118（n_profile=48 cosine-blend LatheGeometry，r_waist→r_end，两端 zero-r cap） | eligible if compatible | 人体工学束腰：中段收窄、两端 collar 座处外鼓；同长度 + collar 座 |
| flat_paddle_bar | rec_skincare_roller_var_paddle | L106-L109（`superellipse_profile(HANDLE_W,HANDLE_T,exp=2)` → `ExtrudeGeometry` center） | eligible if compatible | 扁桨 lozenge 横截面（X 宽 Y 薄）；同长度 + collar 座 |

### Slot C：fork_yoke_form（夹滚轮轴的金属 yoke）

| module_name | 5_star_source | model.py:Lx-Ly | sampling eligibility | 结构特征 |
|---|---|---|---|---|
| u_wire_fork | rec_jade-facial-massage-roller-with-a-metal-handle-a_20260605_165942_156361_d964a399 | L51-L73（`_u_fork`，7 点 `tube_from_spline_points` 连续弯管，两臂到 ±X axle tip） | eligible if compatible | 细圆弯线 U-fork，两臂到 ±X 轴端；roller 双侧支撑 |
| flat_blade_yoke | rec_skincare_roller_var_blade_yoke | L60-L123（`_blade_yoke`，Y 形 XZ 闭合 profile → `ExtrudeGeometry` along Y → `rotate_x`） | eligible if compatible | 冲压扁钣金 Y 形 yoke，两扁臂带轴孔；双侧支撑 |
| single_cantilever_arm | rec_skincare_roller_var_cantilever | L48-L74（`_cantilever_arm`，6 点 `tube_from_spline_points` 单臂弯到 -X tip）；stub axle L165-L172 | eligible if compatible（gated，见兼容矩阵） | 单侧悬臂弯管 + cantilever stub axle；roller 单侧支撑 |

约束说明：每个 slot 均 ≥3 个结构不同 candidate，无降级到 2 的情况。

## 槽位图（slot graph）

pattern: mixed（parallel_children + multiplicity）

```
                 Slot B handle_form  (body, static, +Z 竖直, 居中 x=0,y=0)
                       |
        +--------------+-----------------+
        |                                |
  collars (静态装饰, 固定在 handle 两端)   |
        |                                |
   per unit i ∈ range(roller_count):     |
     Slot C fork_yoke_form_i  --[fixed, rooted at collar 端 z_root]--> body
            |  (轴承, 静态 visual 挂 body)
            |  interface = arm/blade tip 处的 axle 座面 (z = axle_z, 跨 ±X 或 -X 单侧)
            v
     Slot A roller_head_form_i  --[CONTINUOUS spin]--> body
            joint roller_spin_i: parent=body, child=roller_i,
            origin=(0,0,axle_z)（u/blade）或 (-reach,0,axle_z)（cantilever）,
            axis=(1,0,0), range=continuous (∞), MotionLimits(effort 0.2/0.3, velocity 8)
```

接口点位说明：
- handle 是所有件的共同 parent。Slot B 只产 body visual（handle）+ inertial，决定 collar 座位置（z = ±(HANDLE_HALF − COLLAR_H·0.25)）。
- collars 是 handle 上的静态 parent visual（非独立 part），给 fork 提供 z_root。
- Slot C（fork/yoke）作为 **body 的静态 visual** emit，不是独立 part；它定义 axle 座的横向 span 与 z = axle_z（±0.094）。u_wire/blade = 双侧 ±X 臂；cantilever = 单侧 -X 臂。
- Slot A（roller head）是**独立 part**，通过 CONTINUOUS spin joint 挂 body；joint origin 在 axle 座面，axis=X。axle stub/rod 属于 roller part 的 visual，与对应 fork/yoke 之间是 element-scoped allow_overlap（座入轴孔）。

哪些互斥/派生：见第 8、9 节兼容矩阵——single_cantilever_arm 主要面向 roller_count=1（gated）；spiky_germanium × {flat_blade / cantilever} 有轴端 clearance 风险（需 fork_span 放大）。

## 每槽位 Module Emits / Interfaces

### Slot A / module smooth_oval
| emits | 描述 | 来源 |
|---|---|---|
| parts | `roller_{i}` part：`roller_stone_{i}`（oval）+ `axle_{i}`（X 向细 cylinder rod） | S1 / model.py:L132-L158 |
| internal joints | 无（part 内无关节） | — |
| upstream interface | axle rod 跨 ±fork_span，座入 fork tip（element allow_overlap axle↔fork） | S1 / model.py:L190-L199 |
| downstream interface | CONTINUOUS `roller_spin_{i}`，parent=body，origin=(0,0,axle_z)，axis=X | S1 / model.py:L142-L150 |

### Slot A / module faceted_gem
| emits | 描述 | 来源 |
|---|---|---|
| parts | `roller_head_{i}`：`roller_stone_{i}`（MeshGeometry 刻面 barrel）+ `axle_{i}` | S2 / model.py:L201-L220 |
| internal joints | 无 | — |
| upstream interface | axle 座入 fork tip（同 smooth_oval） | S2 / model.py:L255-L265 |
| downstream interface | CONTINUOUS `roller_spin_{i}`，origin=(0,0,axle_z)，axis=X | S2 / model.py:L228-L236 |

### Slot A / module spiky_germanium
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{prefix}_roller`：`{prefix}_ball`（core + nub 场，material germanium）+ `{prefix}_axle` | S3 / model.py:L184-L203 |
| internal joints | 无 | — |
| upstream interface | fork_span 须 ≥ ball_r + nub 突出 + 余量（源用 ball_r+0.009/0.012） | S3 / model.py:L50-L51 |
| downstream interface | CONTINUOUS `{prefix}_roller_spin`，origin=(0,0,axle_z)，axis=X | S3 / model.py:L210-L219 |

### Slot A / module textured_ridged
| emits | 描述 | 来源 |
|---|---|---|
| parts | `{name}_roller`：`{name}_roller_stone`（lathe wavy barrel + marker）+ `{name}_axle` | S4 / model.py:L180-L198 |
| internal joints | 无 | — |
| upstream interface | axle 座入 fork tip（同 smooth_oval） | S4 / model.py:L232-L241 |
| downstream interface | CONTINUOUS `{name}_roller_spin`，origin=(0,0,axle_z)，axis=X | S4 / model.py:L205-L213 |

### Slot B / module straight_stone_bar
| emits | 描述 | 来源 |
|---|---|---|
| parts | body visual `handle`（cylinder+bulge），body inertial | S1 / model.py:L100-L129 |
| internal joints | 无 | — |
| upstream interface | 根 link，无 parent | S1 / model.py:L100 |
| downstream interface | 提供 collar 座 z 与轴线，供 collars/forks/rollers 挂载 | S1 / model.py:L110-L125 |

### Slot B / module contoured_waisted
| emits | 描述 | 来源 |
|---|---|---|
| parts | body visual `handle`（束腰 LatheGeometry），body inertial | S5 / model.py:L100-L140 |
| internal joints | 无 | — |
| upstream interface | 根 link | S5 / model.py:L105-L118 |
| downstream interface | 同长度 + 相同 collar 座 z，接口不变 | S5 / model.py:L120-L127 |

### Slot B / module flat_paddle_bar
| emits | 描述 | 来源 |
|---|---|---|
| parts | body visual `handle`（superellipse extrude paddle），body inertial（盒形） | S6 / model.py:L104-L132 |
| internal joints | 无 | — |
| upstream interface | 根 link | S6 / model.py:L107-L109 |
| downstream interface | 同长度 + 相同 collar 座 z；横截面变扁但 collar/fork 接口不变 | S6 / model.py:L112-L127 |

### Slot C / module u_wire_fork
| emits | 描述 | 来源 |
|---|---|---|
| parts | body visual `{top/bottom}_fork`（连续弯管，两臂 ±X） | S1 / model.py:L118-L125 |
| internal joints | 无（静态） | — |
| upstream interface | z_root 在 collar 端（HANDLE_HALF + COLLAR_H·0.4），嵌入 collar | S1 / model.py:L51-L66 |
| downstream interface | 两臂到 ±span 的 axle tip 座面（z=axle_z），双侧夹 axle | S1 / model.py:L67-L73 |

### Slot C / module flat_blade_yoke
| emits | 描述 | 来源 |
|---|---|---|
| parts | body visual `{top/bottom}_yoke`（Y 形 XZ profile extrude along Y 的扁板） | S7 / model.py:L199-L209 |
| internal joints | 无 | — |
| upstream interface | z_root 在 collar 端（HANDLE_HALF − COLLAR_H·0.25），stem 嵌 collar | S7 / model.py:L174-L197 |
| downstream interface | 两扁臂到 ±span 的轴孔座面（z=axle_z），双侧夹 axle | S7 / model.py:L60-L123 |

### Slot C / module single_cantilever_arm
| emits | 描述 | 来源 |
|---|---|---|
| parts | body visual `arm_{i}`（单侧弯管到 -X tip）；roller 端 axle = cantilever stub | S8 / model.py:L144-L150, L164-L172 |
| internal joints | 无 | — |
| upstream interface | z_embed 深入 collar（z_root − dir·COLLAR_H·0.5）保证连通 | S8 / model.py:L48-L67 |
| downstream interface | 单 -X tip 座面；joint origin=(-reach,0,axle_z)（注意非 0,0）；roller 单侧支撑 | S8 / model.py:L179-L188 |

## 参数范围汇总
| 参数 | 类型 | 取值范围 / 候选值 | 标称默认 | 约束类型 | 约束 / 函数 | 来源 |
|---|---|---|---|---|---|---|
| roller_head_form | enum | smooth_oval / faceted_gem / spiky_germanium / textured_ridged | — | choice | deterministic procedural sampler | Slot A 表 |
| handle_form | enum | straight_stone_bar / contoured_waisted / flat_paddle_bar | — | choice | sampler | Slot B 表 |
| fork_yoke_form | enum | u_wire_fork / flat_blade_yoke / single_cantilever_arm | — | choice | sampler + 兼容门控（cantilever 偏向 N=1） | Slot C 表 |
| roller_count | int | [1, 2]（产品域）；测试 {1,2} | 2 | choice | multiplicity 加权采样（见第 8 节） | source map / S8(N=1) / parent(N=2) |
| palette_style | enum | classic_jade / rose_quartz / amethyst / dark_germanium / obsidian_steel / white_marble_gold | classic_jade | choice | 每 seed 采样，决定 stone+metal rgba（不改拓扑） | 各源 material rgba |
| handle_half_scale | float | [0.90, 1.10] | 1.0 | independent | HANDLE_HALF·s，clamp；不影响 collar/axle 相对接口 | S1 / model.py:L33 |
| roller_size_scale | float | [0.85, 1.15] | 1.0 | independent | 整体滚轮头尺寸（half_x, ry 同比） | S1 / model.py:L42-L45 |
| small_large_ratio | float | derived | ≈0.70 | equation | `small_half_x = ratio · large_half_x`，`small_ry = ratio · large_ry`（保形小头） | parent L42-L45 |
| fork_span | float | derived | — | equation | `fork_span = roller_half_x + clearance`；spiky 时 `= ball_r + nub_protrusion + clearance` | S1 L47-L48 / S3 L50-L51 |
| (—) | constraint | — | — | inequality | `axle_rod_len = 2·fork_span + 0.004 ≥ 2·roller_half_x`（axle 必须跨过滚轮夹住两 tip）；违反按 fork_span 上调 | S1 L136 |
| (—) | constraint | — | — | inequality | spiky_germanium × {flat_blade/cantilever}：`fork_span ≥ ball_r + nub_r·1.0 + 0.003` 防 nub↔臂穿模 | 排除项 / S3 |
| (—) | constraint | — | — | conditional | fork_yoke_form=single_cantilever 时优先 roller_count=1（gate，见第 8/9 节） | 排除项 |
| ridge_count | int | [6, 12] | 8(小)/10(大) | independent | 仅 textured_ridged 用；环向沟数 | S4 / model.py:L122,L133 |
| facet_n_radial | int | [8, 12] | 10 | independent | 仅 faceted_gem；横截面边数（不改拓扑层级） | S2 / model.py:L58 |

连续尺度均在 `resolve_config` 内：先采 independent（handle_half_scale, roller_size_scale, ridge/facet 计数）→ 派生 equation（small_large_ratio, fork_span）→ inequality 投影（axle 跨度、spiky clearance）→ conditional 解析（cantilever×N gate）。

## Multiplicity / Copy Logic

存在 **1 根** multiplicity 轴。

- count_param：`roller_count`
- N_range：产品域 `[1, 2]`；测试覆盖 {1, 2}（已有 S8=N1、parent=N2 两个 5★ 实证）
- sampling domain（权重档）：真实手持滚轮只有 1 或 2 端，域极小且两端等常见 → 近似均匀 `{1: 0.5, 2: 0.5}`（可微偏向 N=2 双端，作为类别标志形态）。无长尾。
- copied object：一个「roller head（Slot A）+ fork/yoke（Slot C）+ 该端 collar + axle/stub + 一根 CONTINUOUS spin joint」单元，用 `for i in range(roller_count)` 循环 emit。
- naming：`roller_{i}` / `roller_head_{i}`（part），`fork_{i}` / `{top|bottom}_yoke` / `arm_{i}`（body visual），`axle_{i}` / `roller_stone_{i}`，joint `roller_spin_{i}`。统一 `_{i}` 编号。
- placement：单元落在 handle 轴 +Z 与 -Z 端的 collar 座（axle_z = ±0.094）。**N=1 时只 emit 较大的 -Z 端单元**，+Z 端退化为 collar + 圆头 `stone_tip`（S8 L101-L112 的静态石帽，无 fork、无活动件）。
- joint policy：每单元一根独立 CONTINUOUS revolute（axis=X），parent=body，child=roller_{i}；各端独立、无链式、无共享，effort 随大小（0.2 小/0.3 大）。
- source/gating：N=1 ← S8 single_ended；N=2 ← parent。Slot C=single_cantilever 在 N=2 时为「可建但机械上少见」，gate 为低权重/优先 N=1（不硬排除）。

## 拓扑多样性审计

总组合数：A(4) × B(3) × C(3) × N(2) = **72** 个名义组合（部分被兼容门控降权，见下）。

理由：4×3×3 = 36 个 slot 组合已远超 10，N=2 进一步翻倍；每个 Slot A 改变 roller part 的 primitive/mesh 构造，Slot C 改变 body 静态 yoke 的 part-visual 拓扑且 cantilever 改变 joint origin（(-reach,0,z) vs (0,0,z)），N 改变 part/joint 计数（1 vs 2 个 roller part + spin joint）。即便门控降权 cantilever×N=2、spiky×{blade/cantilever}，distinct 拓扑仍 ≫10。

seed_domain_policy：procedural_first
Procedural Sampling / Sweep Plan：`config_from_seed` 用 seed 派生 RNG → 加权选 handle_form、roller_head_form、fork_yoke_form、roller_count（近均匀），再采连续 scale；兼容矩阵在选 fork_yoke_form 后据 roller_count 与 roller_head_form 调整（cantilever 优先 N=1、spiky 放大 fork_span）。无小型 curated/modulo 主表。少量 regression overrides 仅用于已知失败回归。random sweep：seeds 0-49 首轮（覆盖各 slot+N），0-999 成熟度审计。
Topology target：1000-seed slot choice tuple distinct 目标 ≥ 50（本类别 slot 候选有限：36 slot 组合 × 2 N = 72 名义拓扑封顶，连续 scale 不计入拓扑 distinct，故 <300 属类别结构上限，非缺陷）。（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）
若使用 regression overrides：仅记录具体失败 seed + 理由；不作为主 seed domain。
Controlled local parameterization：handle_half_scale [0.90,1.10] independent；roller_size_scale [0.85,1.15] independent；small_large_ratio≈0.70 equation（保形小头）；fork_span derived equation（roller_half_x/ball_r + clearance）；axle 跨度 inequality 回缩；ridge_count/facet_n_radial module-local independent。均在 `resolve_config` clamp/派生/投影，不破坏 collar 座 z、axle 座面、spin joint origin、N 复制接口或类别 identity。

| item | policy | validator / viewer focus |
|---|---|---|
| sampler | seed→RNG，加权选 A/B/C 三 slot + roller_count，再采连续 scale | slot_choices_for_seed 与 build choices 一致 |
| compatibility matrix | cantilever 优先 N=1（低权重 N=2）；spiky×{blade/cantilever} 放大 fork_span；N=1 仅 -Z 端 + +Z stone_tip | 无悬空 roller、无 nub↔臂穿模、joint origin 随 cantilever 偏移、N=1 顶端无 fork |
| controlled local variation | handle_half_scale / roller_size_scale / ratio / fork_span / ridge_count / facet_n_radial（clamp+derived） | 比例变化不破坏 axle 跨度、collar 座、spin origin、N 接口 |
| regression overrides | none / 仅记录已知失败 seed | 历史失败或审核指定 |
| random sweep | seeds 0-49 首轮，0-999 成熟度 | 与 contract failures |

| slot | candidate_count | 是否 ≥2 | 是否 ≥3 | 备注 |
|---|---:|---|---|---|
| A roller_head_form | 4 | yes | yes | |
| B handle_form | 3 | yes | yes | |
| C fork_yoke_form | 3 | yes | yes | cantilever gated to N=1-friendly |
| N roller_count | 2 | yes | n/a | multiplicity 轴，域 [1,2] |

## Validator

- slot_choices_for_seed 返回已实现 module 名（A/B/C + roller_count）
- config_from_seed 对所有普通 seed 用 deterministic procedural sampling
- 兼容矩阵阻止非法/高风险组合（cantilever×N=2 降权、spiky×{blade/cantilever} 放大 fork_span）
- regression overrides 稀疏且有理由
- 不靠小型 curated/modulo 表循环作主 seed domain
- 局部 scale 全部 clamp/derived，不破坏 collar 座 z、axle 座面、spin joint origin、roller_count 接口
- 跨件 scale 依赖（small_large_ratio equation、axle-跨度 inequality、cantilever×N conditional）在 `resolve_config` 求解，不留到 builder
- 关键 InterfaceSpec/MatingContract 存在：每个 axle↔fork/yoke element-scoped allow_overlap + expect_contact；handle 介于上下 roller 之间
- 关键 joint：每 roller_spin_i = CONTINUOUS，axis=(1,0,0)，origin=axle 座面（cantilever 为 (-reach,0,z)）
- 复制对象遵循 `_{i}` 命名与 +Z/-Z 端放置；N=1 仅 -Z 端 + +Z stone_tip

## Reject cases

- 任一 roller_spin 不是 CONTINUOUS 或 axis≠X（滚轮必须绕 axle 自由旋转）。
- fork/yoke 被建成独立 part 而非 body 静态 visual（轴承应为静态 parent visual）。
- axle rod 跨度 < 2·roller_half_x，导致滚轮未被两 fork tip 夹住 / 悬空。
- N=2 时缺少大小区分或两端互换（应小头 +Z、大头 -Z；large 沿轴更长且横截面更宽）。
- N=1 时仍 emit 顶端 fork / 第二个 roller part（应只 -Z 端 + +Z stone_tip）。
- single_cantilever joint origin 用 (0,0,z) 而非 (-reach,0,z)，导致旋转轴脱离实际轴位。
- spiky_germanium × flat_blade/cantilever 未放大 fork_span，nub 场穿透 yoke 臂。
- collar/handle 接口随 handle_form 改变而错位（waisted/paddle 必须保持同长度 + 相同 collar 座 z）。

## 与相邻类别的边界

- 不该混入：电动洁面仪 / 美容仪（无电机、无按钮、无电源；本类纯机械被动旋转）。
- 不该混入：油漆滚筒 / lint roller（这些是单一大圆筒滚筒在 U 形把手上，且无双端石质头、无 collar/fork 美容形制）。
- 不该混入：擀面杖 / 按摩棒（无 fork-captured 自由旋转石头头；那些是手柄两端固定把手中间一根滚筒）。
- 不该混入：刮痧板 gua sha（纯静态石板，无任何活动件，不属本可动类别）。

## 审核记录
| 项 | 结论 |
|---|---|
| reviewer status | pending |
| reviewer notes | 待人工审核：确认 roller_count 权重（近均匀 vs 偏 N=2）、cantilever×N=2 是降权还是硬排除、Topology target ≥50 是否接受（类别 slot 上限 72 名义拓扑）。 |（统一口径：富类别建议 ≥300；低于 300 记录真实组合空间或兼容约束原因；report-only，不设门。）

## 模板实现备注（可选）

- 共享 helper：`_u_fork` / `_blade_yoke` / `_cantilever_arm`（Slot C）；`_oval_roller` / `_faceted_roller` / `_spiky_ball` / `_ridged_roller`（Slot A）；handle 三式各自 profile。roller-unit 复制循环 `for i in range(roller_count)` 跨 N 共享。
- InterfaceSpec/MatingContract 重点：每 axle↔对应 fork/yoke 的 element-scoped `allow_overlap` + `expect_contact`（座入轴孔）；u/blade 用 origin=(0,0,axle_z)，cantilever 用 origin=(-reach,0,axle_z) 且 stone 在 local +reach 偏置（见 S8 L155-L157）。
- captured-pin overlap：axle/stub 与 fork tip 必须逐 element allow_overlap，否则碰撞门控报穿模。
- 暂不进入 seed domain 的高风险组合：spiky_germanium × single_cantilever × N=2（nub clearance + 单侧悬臂 + 双端三重叠加），首版可门控为低权重或先排除，成熟后再放开。
